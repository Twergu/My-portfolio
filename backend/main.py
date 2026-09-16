import hashlib
import json
import logging
import os
import re
import subprocess
import sys
import threading
import uuid
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Annotated

import anyio
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, SecretStr, field_validator
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .config import DATA_DIR, ROOT, Settings, environment_settings
from .governance import LOCAL_ADMIN, DocumentMetadata, RetrievalFilters
from .providers import ModelError, OpenAICompatibleProvider
from .rag import answer, chunks_from_pages, embed
from .store import create_store
from .telemetry import Metrics

ACTIVE = ("queued", "parsing", "embedding")
MAX_BYTES = 20 * 1024 * 1024
log = logging.getLogger("knowbase")


class BodyLimitMiddleware:
    """Bound actual streamed input before the multipart parser creates temporary files."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] not in ("POST", "PUT", "PATCH"):
            return await self.app(scope, receive, send)
        limit = MAX_BYTES + 1024 * 1024 if scope["path"] == "/api/documents" else 65536
        buffered = deque()
        total = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            total += len(message.get("body", b""))
            if total > limit:
                response = JSONResponse({"detail": "请求内容过大；单个 PDF 不能超过 20 MB。"}, status_code=413)
                return await response(scope, receive, send)
            buffered.append(message)
            if not message.get("more_body", False):
                break

        async def replay():
            return buffered.popleft() if buffered else await receive()

        await self.app(scope, replay, send)


class SettingsInput(Settings):
    api_key: SecretStr = Field(default=SecretStr(""), max_length=2000)
    clear_key: bool = False


class Question(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    document_ids: list[str] = Field(default_factory=list, max_length=100)
    language: str | None = Field(default=None, pattern="^(zh|ja|en)$")
    filters: RetrievalFilters = Field(default_factory=RetrievalFilters)

    @field_validator("question")
    @classmethod
    def nonempty(cls, value):
        if not value.strip():
            raise ValueError("请输入问题。")
        return value.strip()


class LoginInput(BaseModel):
    token: SecretStr = Field(min_length=20, max_length=200)


class PermissionInput(BaseModel):
    role: str = Field(min_length=1, max_length=80)
    permission: str | None = Field(default=None, pattern="^(read|write)$")


class KnowledgeService:
    def __init__(self, folder, database_url=None, provider=None):
        self.store = create_store(folder, database_url=database_url)
        self.provider = provider if provider is not None else OpenAICompatibleProvider()
        self.lock = threading.RLock()
        self.index_lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="knowbase-index")
        self.measurements = deque(maxlen=100)
        log_folder = folder / "logs"
        log_folder.mkdir(exist_ok=True)
        self.log = logging.getLogger(f"knowbase.service.{uuid.uuid4().hex}")
        self.log.setLevel(logging.INFO)
        self.log_handler = RotatingFileHandler(
            log_folder / "service.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
        self.log_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        self.log.addHandler(self.log_handler)
        env = environment_settings()
        saved = self.store.get_settings()
        self.settings = Settings.model_validate_json(saved) if saved else env
        self.api_key = os.getenv("RAG_API_KEY", "") if self.settings.base_url == env.base_url else ""
        if self.store.backend == "pgvector":
            self.store.maintain_indexes(self.settings.profile, self.settings.search_mode)

    def close(self):
        self.executor.shutdown(wait=True, cancel_futures=True)
        self.provider.close()
        self.store.close()
        self.log.removeHandler(self.log_handler)
        self.log_handler.close()

    def record_metrics(self, operation, status, metrics, document_id=None):
        record = {
            "operation": operation,
            "status": status,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "document_id": document_id,
            "metrics": metrics,
        }
        with self.lock:
            self.measurements.append(record)
        self.log.info("operation_metrics %s", json.dumps(record, ensure_ascii=False))

    def snapshot(self):
        with self.lock:
            return self.settings.model_copy(), self.api_key

    def enqueue(self, doc_id):
        future = self.executor.submit(self.process, doc_id)

        def report_unhandled(completed):
            if not completed.cancelled() and (exc := completed.exception()) is not None:
                self.log.error(
                    "Unhandled indexing exception document_id=%s", doc_id, exc_info=(type(exc), exc, exc.__traceback__)
                )

        future.add_done_callback(report_unhandled)
        return future

    def wait_for_jobs(self):
        # Also used by deterministic integration tests, without blocking HTTP workers.
        self.executor.submit(lambda: None).result(timeout=120)

    def public_settings(self):
        config, key = self.snapshot()
        return {**config.model_dump(), "has_key": bool(key), "profile": config.profile}

    def documents(self):
        profile = self.settings.profile
        documents = self.store.all_documents()
        for doc in documents:
            doc["needs_reindex"] = doc["status"] == "stale" or (doc["status"] == "ready" and doc["profile"] != profile)
            doc.pop("sha256")
        return documents

    def save_settings(self, candidate):
        with self.lock:
            if any(doc["status"] in ACTIVE for doc in self.store.all_documents()):
                raise HTTPException(409, "请等待文档处理完成后再修改模型配置。")
            config = Settings(**candidate.model_dump(exclude={"api_key", "clear_key"}))
            if config.search_mode == "hnsw" and (config.mode != "api" or self.store.backend != "pgvector"):
                raise HTTPException(400, "HNSW 需要 PostgreSQL + pgvector 和 AI 问答模式；当前请使用 exact。")
            key = candidate.api_key.get_secret_value()
            if config.base_url != self.settings.base_url or candidate.clear_key:
                self.api_key = ""
            if key:
                self.api_key = key
            if self.store.backend == "pgvector":
                self.store.maintain_indexes(config.profile, config.search_mode)
            self.store.save_settings(config.model_dump_json())
            self.settings = config
        return self.public_settings()

    def register(self, name, content):
        if not name.lower().endswith(".pdf") or not content.startswith(b"%PDF-"):
            raise HTTPException(400, "仅支持有效的 PDF 文件。")
        if len(content) > MAX_BYTES:
            raise HTTPException(413, "单个 PDF 不能超过 20 MB。")
        safe_name = re.sub(r"[\x00-\x1f\x7f]", "", name.replace("\\", "/").split("/")[-1])[:180]
        digest = hashlib.sha256(content).hexdigest()
        with self.lock:
            existing = self.store.find_by_digest(digest)
            if existing:
                return {"id": existing["id"], "duplicate": True}
            if self.store.count_documents() >= 100:
                raise HTTPException(400, "当前版本最多存储 100 份文档，请删除不需要的文档。")
            doc_id = uuid.uuid4().hex
            path = self.store.folder / "files" / (doc_id + ".pdf")
            path.write_bytes(content)
            try:
                registered = self.store.register_document(
                    {
                        "id": doc_id,
                        "name": safe_name,
                        "sha256": digest,
                        "size": len(content),
                        "status": "queued",
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    }
                )
                if registered["duplicate"]:
                    path.unlink(missing_ok=True)
                    return registered
            except Exception:
                path.unlink(missing_ok=True)
                raise
        return {"id": doc_id, "duplicate": False}

    def process(self, doc_id):
        with self.index_lock:
            doc = self.store.document(doc_id)
            if not doc:
                return
            config, key = self.snapshot()
            metrics = Metrics()
            stage, outcome = "parsing", "error"
            try:
                self.store.update(doc_id, status="parsing", error="", warning="")
                path = self.store.folder / "files" / (doc_id + ".pdf")
                with metrics.measure("parsing"):
                    result = subprocess.run(
                        [sys.executable, "-m", "backend.parse_pdf", str(path)],
                        cwd=ROOT,
                        capture_output=True,
                        timeout=45,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                    )
                if result.returncode and result.stderr:
                    self.log.error(
                        "PDF parser traceback document_id=%s stage=parsing\n%s",
                        doc_id,
                        result.stderr.decode("utf-8", errors="replace")[-16000:],
                    )
                try:
                    parsed = json.loads(result.stdout)
                except (ValueError, UnicodeError):
                    raise ValueError("PDF 解析进程异常，请检查文件并重试。") from None
                if result.returncode or "error" in parsed:
                    raise ValueError(parsed.get("error", "PDF 解析失败。"))
                stage = "chunking"
                with metrics.measure("chunking"):
                    chunks = chunks_from_pages(parsed["pages"], config.chunk_size, config.chunk_overlap)
                if not chunks:
                    raise ValueError("PDF 没有可供检索的文字。")
                self.store.update(doc_id, status="embedding", pages=len(parsed["pages"]))
                stage = "embedding"
                with metrics.measure("embedding"):
                    vectors = embed(
                        [chunk["text"] for chunk in chunks], config, key, provider=self.provider, metrics=metrics
                    )
                self.store.accept_dimensions(config.profile, len(vectors[0]))
                blank = parsed["empty_pages"]
                warning = (
                    f"第 {', '.join(map(str, blank[:20]))} 页未提取到文字，未纳入检索；如含扫描内容，请先进行 OCR。"
                    if blank
                    else ""
                )
                stage = "storage"
                with metrics.measure("storage"):
                    options = {"search_mode": config.search_mode} if self.store.backend == "pgvector" else {}
                    self.store.commit_chunks(doc_id, chunks, vectors, config.profile, warning, **options)
                outcome = "ready"
            except subprocess.TimeoutExpired:
                self.log.exception(
                    "Document indexing timed out document_id=%s profile=%s stage=%s", doc_id, config.profile, stage
                )
                self.store.update(doc_id, status="error", error="PDF 解析超过 45 秒，请拆分或简化文档后重试。")
            except (ValueError, ModelError) as exc:
                self.log.exception(
                    "Document indexing failed document_id=%s profile=%s stage=%s", doc_id, config.profile, stage
                )
                self.store.update(doc_id, status="error", error=str(exc))
            except Exception:
                self.log.exception(
                    "Document indexing failed document_id=%s profile=%s stage=%s", doc_id, config.profile, stage
                )
                self.store.update(doc_id, status="error", error="处理失败，请重试；若持续失败，请检查服务日志。")
            finally:
                self.record_metrics("indexing", outcome, metrics.as_dict(), doc_id)


def create_app(data_dir=DATA_DIR, database_url=None, provider=None):
    service = KnowledgeService(Path(data_dir), database_url=database_url, provider=provider)

    @asynccontextmanager
    async def lifespan(app):
        try:
            yield
        finally:
            await anyio.to_thread.run_sync(service.close)

    app = FastAPI(
        title="Knowbase API",
        version="0.2.0",
        description="PDF retrieval and evidence-checked RAG answers",
        lifespan=lifespan,
    )
    app.state.knowledge = service
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "[::1]", "testserver"])
    app.add_middleware(BodyLimitMiddleware)

    auth_mode = os.getenv("RAG_AUTH_MODE", "local")
    if auth_mode not in ("local", "required"):
        raise ValueError("RAG_AUTH_MODE must be local or required")

    def identify(request):
        if auth_mode == "local":
            return LOCAL_ADMIN
        header = request.headers.get("authorization", "")
        token = header[7:] if header.startswith("Bearer ") else request.cookies.get("knowbase_session", "")
        return service.store.authenticate(token)

    @app.middleware("http")
    async def access_control(request: Request, call_next):
        path = request.url.path
        if not path.startswith("/api/"):
            return await call_next(request)
        principal = await anyio.to_thread.run_sync(identify, request)
        request.state.principal = principal
        if path in ("/api/health", "/api/auth/status", "/api/auth/login", "/api/auth/logout"):
            return await call_next(request)
        if principal is None:
            return JSONResponse({"detail": "Authentication required"}, status_code=401)
        admin_only = (
            path.startswith("/api/admin/")
            or path == "/api/metrics"
            or (path.startswith("/api/settings") and request.method != "GET")
            or path == "/api/documents/reindex"
        )
        if admin_only and not principal.admin:
            return JSONResponse({"detail": "Administrator role required"}, status_code=403)
        if (
            request.method == "POST"
            and path in ("/api/documents", "/api/documents/sample")
            and not principal.can_upload
        ):
            return JSONResponse({"detail": "Editor role required"}, status_code=403)
        match = re.fullmatch(r"/api/documents/([^/]+)(?:/(file|chunks|retry|metadata|permissions))?", path)
        if match and match[1] not in ("sample", "reindex"):
            if match[2] == "permissions" and not principal.admin:
                return JSONResponse({"detail": "Administrator role required"}, status_code=403)
            allowed = await anyio.to_thread.run_sync(
                lambda: service.store.allowed_document_ids(
                    principal, [match[1]], write=request.method not in ("GET", "HEAD")
                )
            )
            if not allowed:
                return JSONResponse({"detail": "Document not found"}, status_code=404)
        return await call_next(request)

    @app.get("/api/auth/status")
    def auth_status(request: Request):
        principal = request.state.principal
        return {"mode": auth_mode, "user": principal.model_dump() if principal else None}

    @app.post("/api/auth/login")
    def login(candidate: LoginInput, request: Request):
        principal = service.store.authenticate(candidate.token.get_secret_value())
        if principal is None:
            raise HTTPException(401, "Invalid or revoked access token")
        response = JSONResponse({"user": principal.model_dump()})
        response.set_cookie(
            "knowbase_session",
            candidate.token.get_secret_value(),
            httponly=True,
            secure=request.url.scheme == "https",
            samesite="strict",
            max_age=28800,
            path="/",
        )
        return response

    @app.post("/api/auth/logout")
    def logout():
        response = JSONResponse({"ok": True})
        response.delete_cookie("knowbase_session", path="/")
        return response

    @app.get("/api/admin/users")
    def users():
        return {"users": service.store.list_users()}

    @app.get("/api/documents/{doc_id}/permissions")
    def permissions(doc_id: str):
        return {"permissions": service.store.list_permissions(doc_id)}

    @app.put("/api/documents/{doc_id}/permissions")
    def grant(doc_id: str, candidate: PermissionInput):
        try:
            service.store.grant_document(doc_id, candidate.role, candidate.permission)
        except Exception:
            raise HTTPException(422, "Invalid role or document permission") from None
        return {"permissions": service.store.list_permissions(doc_id)}

    @app.put("/api/documents/{doc_id}/metadata")
    def update_metadata(doc_id: str, candidate: DocumentMetadata):
        return service.store.set_metadata(doc_id, candidate.model_dump(mode="json"))

    @app.middleware("http")
    async def local_origin(request: Request, call_next):
        origin = request.headers.get("origin")
        if request.method not in ("GET", "HEAD", "OPTIONS"):
            expected = f"{request.url.scheme}://{request.headers.get('host', '')}"
            if (origin and origin != expected) or request.headers.get("sec-fetch-site") == "cross-site":
                return JSONResponse({"detail": "仅允许从本机应用页面发起操作。"}, status_code=403)
        length = request.headers.get("content-length", "")
        if length.isdigit() and int(length) > MAX_BYTES + 1024 * 1024:
            return JSONResponse({"detail": "上传文件不能超过 20 MB。"}, status_code=413)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        return JSONResponse(
            {"detail": "输入无效：" + "；".join(error["msg"].replace("Value error, ", "") for error in exc.errors())},
            status_code=422,
        )

    @app.exception_handler(ModelError)
    async def model_error(request, exc):
        return JSONResponse({"detail": str(exc)}, status_code=502)

    @app.get("/api/health")
    def health():
        if auth_mode == "required":
            return {"status": "ok", "storage": service.store.backend}
        docs = service.documents()
        return {
            "status": "ok",
            "mode": service.settings.mode,
            "storage": service.store.backend,
            "documents": len(docs),
            "ready": sum(doc["status"] == "ready" and not doc["needs_reindex"] for doc in docs),
            "chunks": sum(doc["chunk_count"] for doc in docs if doc["status"] == "ready" and not doc["needs_reindex"]),
        }

    @app.get("/api/metrics")
    def metrics():
        with service.lock:
            return {"scope": "last_100_operations_since_start", "operations": list(service.measurements)}

    @app.get("/api/settings")
    def settings():
        return service.public_settings()

    @app.put("/api/settings")
    def update_settings(candidate: SettingsInput):
        return service.save_settings(candidate)

    @app.post("/api/settings/test")
    def test_settings(candidate: SettingsInput):
        config = Settings(**candidate.model_dump(exclude={"api_key", "clear_key"}))
        saved_config, saved_key = service.snapshot()
        key = candidate.api_key.get_secret_value() or (
            saved_key if config.base_url == saved_config.base_url and not candidate.clear_key else ""
        )
        if config.mode == "local":
            return {"ok": True, "message": "文档检索模式可用，无需模型服务。"}
        measurements = Metrics()
        outcome = "error"
        try:
            with measurements.measure("embedding"):
                vector = embed(["连接测试"], config, key, provider=service.provider, metrics=measurements)[0]
            with measurements.measure("generation"):
                service.provider.chat(config, key, [{"role": "user", "content": "请只回复 OK。"}], metrics=measurements)
            outcome = "ok"
            return {
                "ok": True,
                "message": f"连接成功：Embedding 返回 {len(vector)} 维向量，回答模型可用。",
                "metrics": measurements.as_dict(),
            }
        finally:
            service.record_metrics("connection_test", outcome, measurements.as_dict())

    @app.get("/api/documents")
    def documents(request: Request):
        allowed = set(service.store.allowed_document_ids(request.state.principal))
        writable = set(service.store.allowed_document_ids(request.state.principal, write=True))
        return {
            "documents": [d | {"can_write": d["id"] in writable} for d in service.documents() if d["id"] in allowed]
        }

    @app.post("/api/documents", status_code=202)
    async def upload(request: Request, file: Annotated[UploadFile, File()]):
        content = bytearray()
        try:
            while block := await file.read(1024 * 1024):
                content.extend(block)
                if len(content) > MAX_BYTES:
                    raise HTTPException(413, "单个 PDF 不能超过 20 MB。")
            doc = service.register(file.filename or "", bytes(content))
        finally:
            await file.close()
        if doc["duplicate"] and not service.store.allowed_document_ids(request.state.principal, [doc["id"]]):
            raise HTTPException(409, "This file cannot be registered in the current scope")
        if not doc["duplicate"]:
            if auth_mode == "required":
                service.store.set_owner(doc["id"], request.state.principal.id)
            service.enqueue(doc["id"])
        return doc

    @app.post("/api/documents/sample", status_code=202)
    def sample(request: Request):
        path = ROOT / "samples" / "employee-handbook.pdf"
        if not path.exists():
            raise HTTPException(404, "演示文档不存在。")
        doc = service.register("员工手册（演示）.pdf", path.read_bytes())
        if doc["duplicate"] and not service.store.allowed_document_ids(request.state.principal, [doc["id"]]):
            raise HTTPException(409, "This file cannot be registered in the current scope")
        if not doc["duplicate"]:
            if auth_mode == "required":
                service.store.set_owner(doc["id"], request.state.principal.id)
            service.enqueue(doc["id"])
        return doc

    @app.post("/api/documents/reindex", status_code=202)
    def reindex():
        with service.lock:
            docs = [doc for doc in service.documents() if doc["status"] not in ACTIVE]
            for doc in docs:
                service.store.update(doc["id"], status="queued", error="")
                service.enqueue(doc["id"])
        return {"queued": len(docs)}

    @app.post("/api/documents/{doc_id}/retry", status_code=202)
    def retry(doc_id: str):
        with service.lock:
            doc = service.store.document(doc_id)
            if not doc:
                raise HTTPException(404, "文档不存在或已删除。")
            if doc["status"] in ACTIVE:
                raise HTTPException(409, "该文档正在处理中。")
            service.store.update(doc_id, status="queued", error="")
            service.enqueue(doc_id)
        return {"id": doc_id}

    @app.get("/api/documents/{doc_id}/file")
    def pdf(doc_id: str):
        doc = service.store.document(doc_id)
        if not doc:
            raise HTTPException(404, "文档不存在或已删除。")
        return FileResponse(
            service.store.folder / "files" / (doc["id"] + ".pdf"),
            media_type="application/pdf",
            filename=doc["name"],
            content_disposition_type="inline",
        )

    @app.get("/api/documents/{doc_id}/chunks")
    def document_chunks(doc_id: str):
        doc = service.store.document(doc_id)
        if not doc:
            raise HTTPException(404, "文档不存在或已删除。")
        return {"document": doc, "chunks": service.store.get_chunks(doc_id)}

    @app.delete("/api/documents/{doc_id}")
    def delete(doc_id: str):
        with service.lock:
            doc = service.store.document(doc_id)
            if not doc:
                raise HTTPException(404, "文档不存在或已删除。")
            if doc["status"] in ACTIVE:
                raise HTTPException(409, "请等待处理完成后再删除。")
            service.store.delete_document(doc_id)
            (service.store.folder / "files" / (doc["id"] + ".pdf")).unlink(missing_ok=True)
        return {"deleted": True}

    @app.post("/api/chat")
    def chat(question: Question, request: Request):
        config, key = service.snapshot()
        allowed = service.store.allowed_document_ids(
            request.state.principal, question.document_ids or None, question.filters
        )
        if question.document_ids:
            permitted = set(service.store.allowed_document_ids(request.state.principal, question.document_ids))
            if any(doc_id not in permitted for doc_id in question.document_ids):
                raise HTTPException(404, "Document not found")
            docs = {doc["id"]: doc for doc in service.documents()}
            if any(
                docs[doc_id]["status"] != "ready" or docs[doc_id]["needs_reindex"] for doc_id in question.document_ids
            ):
                raise HTTPException(409, "所选文档尚未就绪或需要重建索引，请重新选择。")
        measurements, outcome = Metrics(), "error"
        try:
            result = answer(
                service.store,
                question.question,
                config,
                key,
                allowed,
                question.language,
                provider=service.provider,
                metrics=measurements,
            )
            outcome = result["status"]
            return result
        finally:
            service.record_metrics("question", outcome, measurements.as_dict())

    app.mount("/", StaticFiles(directory=ROOT / "dist", html=True), name="ui")
    return app
