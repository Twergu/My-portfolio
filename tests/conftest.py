"""Unit/contract tests never inherit a user's paid API credentials."""

import os
import uuid

import httpx
import pytest

from backend.store import Store

# Set these before test-module imports cause config.py to load .env. dotenv
# does not override an existing variable, including the intentionally empty key.
os.environ["RAG_API_KEY"] = ""
os.environ["RAG_MODE"] = "local"
os.environ["RAG_BASE_URL"] = "https://api.openai.com/v1"
os.environ["RAG_CHAT_MODEL"] = "gpt-4o-mini"
os.environ["RAG_VERIFIER_MODEL"] = ""
os.environ["RAG_VERIFICATION_MODE"] = "strict"
os.environ["RAG_DATABASE_URL"] = ""
os.environ["RAG_DATABASE_PASSWORD_FILE"] = ""
os.environ["RAG_AUTH_MODE"] = "local"
os.environ["RAG_RETRIEVAL_MODE"] = "dense"
os.environ["RAG_RERANKER_MODE"] = "off"
os.environ["RAG_VERIFICATION_STRATEGY"] = "all"
os.environ["RAG_VERIFIER_PROMPT"] = "baseline"


@pytest.fixture(autouse=True)
def prevent_paid_http_calls(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError("Tests must inject MockTransport; real HTTP calls are forbidden.")

    monkeypatch.setattr(httpx.HTTPTransport, "handle_request", deny)


@pytest.fixture(params=["sqlite", "pgvector"])
def store(request, tmp_path):
    if request.param == "sqlite":
        result = Store(tmp_path / "sqlite")
        yield result
        result.close()
        return
    url = os.getenv("RAG_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set RAG_TEST_DATABASE_URL for real PostgreSQL + pgvector integration tests.")
    import psycopg
    from psycopg import sql

    from backend.postgres_store import PostgresStore

    schema = "kb_test_" + uuid.uuid4().hex
    result = None
    try:
        result = PostgresStore(tmp_path / "pgvector", url, schema=schema, recover=False)
        yield result
    finally:
        if result:
            result.close()
        # This invocation owns only this unique schema, never public app tables.
        with psycopg.connect(url, autocommit=True) as db:
            db.execute(sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(schema)))
