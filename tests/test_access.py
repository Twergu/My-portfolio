import json
from pathlib import Path

from fastapi.testclient import TestClient

from backend.config import Settings
from backend.main import create_app


def test_required_auth_filters_every_surface_before_provider(store, monkeypatch):
    monkeypatch.setenv("RAG_AUTH_MODE", "required")
    monkeypatch.setattr("backend.main.create_store", lambda *a, **kw: store)
    app = create_app(store.folder, database_url="")
    with TestClient(app) as client:
        service = app.state.knowledge
        settings = Settings(mode="api", retrieval_mode="hybrid", reranker_mode="llm", min_score=0)
        service.settings = settings
        store = service.store
        _, admin_token = store.provision_user("admin", ["admin"])
        reader_id, reader_token = store.provision_user("reader", ["reader"])
        for doc_id in ("visible", "secret"):
            store.register_document(
                {
                    "id": doc_id,
                    "name": doc_id + ".pdf",
                    "sha256": doc_id,
                    "size": 1,
                    "status": "queued",
                    "created_at": "2026-01-01",
                }
            )
            store.commit_chunks(
                doc_id, [{"page": 1, "ordinal": 0, "text": doc_id + " policy text."}], [[1.0, 0.0]], settings.profile
            )
            (Path(store.folder) / "files" / (doc_id + ".pdf")).write_bytes(b"%PDF-test")
        assert client.get("/api/documents").status_code == 401
        assert client.get("/api/health").json() == {"status": "ok", "storage": store.backend}
        assert client.get("/api/documents", headers={"X-User-ID": reader_id}).status_code == 401
        assert client.post("/api/auth/login", json={"token": reader_token}).status_code == 200
        cookie = client.cookies.get("knowbase_session")
        assert cookie == reader_token
        assert client.get("/api/documents").json()["documents"] == []
        calls = []
        service.provider.embed = lambda *a, **kw: calls.append("embedding")
        service.provider.chat = lambda *a, **kw: calls.append("chat")
        empty = client.post("/api/chat", json={"question": "Secret policy?"})
        assert empty.status_code == 200 and empty.json()["retrieved_sources"] == []
        assert calls == []
        store.grant_document("visible", "reader", "read")
        docs = client.get("/api/documents").json()["documents"]
        assert [d["id"] for d in docs] == ["visible"] and not docs[0]["can_write"]
        for suffix in ("file", "chunks"):
            assert client.get("/api/documents/secret/" + suffix).status_code == 404
            assert client.get("/api/documents/visible/" + suffix).status_code == 200
        assert client.post("/api/chat", json={"question": "Secret?", "document_ids": ["secret"]}).status_code == 404
        assert (
            client.post("/api/chat", json={"question": "Policy?", "filters": {"department": "none"}}).json()[
                "retrieved_sources"
            ]
            == []
        )
        assert calls == []
        assert client.delete("/api/documents/visible").status_code == 404
        assert client.put("/api/documents/visible/metadata", json={}).status_code == 404
        assert client.get("/api/metrics").status_code == 403
        assert client.put("/api/settings", json={}).status_code == 403
        assert client.post("/api/documents/sample").status_code == 403

        def embedding(*args, **kwargs):
            return [[1.0, 0.0]]

        def chat(config, key, messages, **kwargs):
            assert "secret" not in json.dumps(messages).lower()
            if kwargs.get("role") == "verifier":
                return json.dumps({"verdicts": [{"claim_index": 1, "supported": True, "reason": "Exact evidence."}]})
            return json.dumps(
                {
                    "status": "answered",
                    "claims": [
                        {
                            "text": "visible policy text.",
                            "evidence": [{"source_id": 1, "quote": "visible policy text."}],
                        }
                    ],
                }
            )

        service.provider.embed = embedding
        service.provider.chat = chat
        result = client.post("/api/chat", json={"question": "Policy?"})
        assert result.status_code == 200 and result.json()["status"] == "answered"
        assert {s["document_id"] for s in result.json()["retrieved_sources"]} == {"visible"}
        store.set_user_active(reader_id, False)
        assert client.get("/api/documents").status_code == 401
        assert client.get("/api/documents", headers={"Authorization": "Bearer " + admin_token}).status_code == 200


def test_authenticated_cookie_is_httponly_and_cross_origin_write_denied(tmp_path, monkeypatch):
    monkeypatch.setenv("RAG_AUTH_MODE", "required")
    app = create_app(tmp_path / "app", database_url="")
    with TestClient(app, base_url="https://testserver") as client:
        _, token = app.state.knowledge.store.provision_user("admin", ["admin"])
        result = client.post("/api/auth/login", json={"token": token})
        header = result.headers["set-cookie"].lower()
        assert "httponly" in header and "secure" in header and "samesite=strict" in header
        assert client.post("/api/auth/logout", headers={"Origin": "https://attacker.example"}).status_code == 403
        assert client.post("/api/auth/logout").status_code == 200
        assert client.get("/api/documents").status_code == 401
