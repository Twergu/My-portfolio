import hashlib
import json
import os
from pathlib import Path
from typing import Literal
from urllib.parse import quote, urlsplit

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator, model_validator

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
DATA_DIR = Path(os.getenv("RAG_DATA_DIR", str(ROOT / "data"))).resolve()
CHUNK_VERSION = "physical-page-v2"


class Settings(BaseModel):
    mode: Literal["local", "api"] = "local"
    base_url: str = Field(default="https://api.openai.com/v1", max_length=500)
    chat_model: str = Field(default="gpt-4o-mini", min_length=1, max_length=160)
    verifier_model: str = Field(default="", max_length=160)
    verification_mode: Literal["off", "fast", "strict"] = "strict"
    verification_strategy: Literal["all", "selective"] = "all"
    verifier_prompt: Literal["baseline", "calibrated"] = "baseline"
    embedding_model: str = Field(default="text-embedding-3-small", min_length=1, max_length=160)
    top_k: int = Field(default=5, ge=1, le=50)
    min_score: float = Field(default=0.25, ge=0, le=1)
    chunk_size: int = Field(default=900, ge=64, le=8000)
    chunk_overlap: int = Field(default=120, ge=0, le=2000)
    search_mode: Literal["exact", "hnsw"] = "exact"
    retrieval_mode: Literal["dense", "hybrid"] = "dense"
    candidate_k: int = Field(default=20, ge=5, le=100)
    rrf_k: int = Field(default=60, ge=1, le=200)
    reranker_mode: Literal["off", "llm"] = "off"
    reranker_model: str = Field(default="", max_length=160)

    @model_validator(mode="after")
    def valid_chunks(self):
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("Chunk overlap must be smaller than chunk size.")
        return self

    @field_validator("base_url")
    @classmethod
    def valid_url(cls, value):
        value = value.strip().rstrip("/")
        url = urlsplit(value)
        if not url.hostname or url.username or url.password or url.query or url.fragment:
            raise ValueError("请输入不含账号、密码、查询参数的 API 服务地址。")
        if url.scheme != "https" and not (url.scheme == "http" and url.hostname in ("localhost", "127.0.0.1", "::1")):
            raise ValueError("远程 API 必须使用 HTTPS；本机服务可使用 HTTP。")
        return value

    @field_validator("chat_model", "embedding_model")
    @classmethod
    def valid_model(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("模型名称不能为空。")
        return value

    @property
    def profile(self):
        identity = (
            ["local-hash-2048-v1"]
            if self.mode == "local"
            else ["openai-compatible", self.base_url, self.embedding_model]
        )
        return hashlib.sha256(
            json.dumps([identity, CHUNK_VERSION, self.chunk_size, self.chunk_overlap]).encode()
        ).hexdigest()[:24]

    @property
    def effective_verifier_model(self):
        return self.verifier_model.strip() or self.chat_model

    @property
    def effective_reranker_model(self):
        return self.reranker_model.strip() or self.chat_model


def environment_settings():
    return Settings(
        mode=os.getenv("RAG_MODE", "local"),
        base_url=os.getenv("RAG_BASE_URL", "https://api.openai.com/v1"),
        chat_model=os.getenv("RAG_CHAT_MODEL", "gpt-4o-mini"),
        verifier_model=os.getenv("RAG_VERIFIER_MODEL", ""),
        verification_mode=os.getenv("RAG_VERIFICATION_MODE", "strict"),
        verification_strategy=os.getenv("RAG_VERIFICATION_STRATEGY", "all"),
        verifier_prompt=os.getenv("RAG_VERIFIER_PROMPT", "baseline"),
        embedding_model=os.getenv("RAG_EMBEDDING_MODEL", "text-embedding-3-small"),
        chunk_size=int(os.getenv("RAG_CHUNK_SIZE", "900")),
        chunk_overlap=int(os.getenv("RAG_CHUNK_OVERLAP", "120")),
        search_mode=os.getenv("RAG_SEARCH_MODE", "exact"),
        retrieval_mode=os.getenv("RAG_RETRIEVAL_MODE", "dense"),
        candidate_k=int(os.getenv("RAG_CANDIDATE_K", "20")),
        reranker_mode=os.getenv("RAG_RERANKER_MODE", "off"),
        reranker_model=os.getenv("RAG_RERANKER_MODEL", ""),
    )


def environment_database_url():
    direct = os.getenv("RAG_DATABASE_URL", "")
    if direct:
        return direct
    password_file = os.getenv("RAG_DATABASE_PASSWORD_FILE", "")
    if not password_file:
        return ""
    password = Path(password_file).read_text(encoding="utf-8").strip()
    if not password:
        raise ValueError("Database password file is empty.")
    return "postgresql://{}:{}@{}:{}/{}".format(
        quote(os.getenv("RAG_DATABASE_USER", "knowbase"), safe=""),
        quote(password, safe=""),
        os.getenv("RAG_DATABASE_HOST", "db"),
        os.getenv("RAG_DATABASE_PORT", "5432"),
        quote(os.getenv("RAG_DATABASE_NAME", "knowbase"), safe=""),
    )
