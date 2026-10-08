"""The same contract against SQLite and a real, explicitly configured pgvector DB."""

import hashlib
import json
import sqlite3

import psycopg
import pytest

from backend.config import Settings
from backend.store import Store, create_store
from scripts.benchmark_stores import run_benchmark
from scripts.migrate_sqlite import migrate


def register(store, doc_id="one"):
    return store.register_document(
        {
            "id": doc_id,
            "name": doc_id + ".pdf",
            "sha256": doc_id,
            "size": 1,
            "status": "queued",
            "created_at": "2026-01-01T00:00:00Z",
        }
    )


def chunks(prefix="a"):
    return [
        {"id": prefix + "-1", "page": 1, "ordinal": 0, "text": "Annual leave policy."},
        {"id": prefix + "-2", "page": 2, "ordinal": 1, "text": "Travel expenses policy."},
    ]


def test_storage_scopes_dimensions_cosine_and_delete(store):
    register(store)
    store.commit_chunks("one", chunks(), [[3.0, 0.0], [0.0, 9.0]], "model-a")
    register(store, "two")
    store.commit_chunks("two", chunks("b"), [[0.0, 9.0], [3.0, 0.0]], "model-b")
    assert not store.has_searchable("unknown")
    assert store.has_searchable("model-a", ["one"])
    assert not store.has_searchable("model-a", ["two"])
    rows = store.search([1.0, 0.0], "model-a", top_k=2, min_score=0.5)
    assert [row["id"] for row in rows] == ["a-1"]
    assert rows[0]["score"] == pytest.approx(1.0)
    assert store.search([1.0, 0.0, 0.0], "model-a") == []
    assert store.search([0.0, 0.0], "model-a") == []
    assert store.get_chunks("one")[1]["page"] == 2
    store.delete_document("one")
    assert not store.has_searchable("model-a") and store.get_chunks("one") == []


def test_atomic_chunk_replace_rolls_back_on_duplicate_id(store):
    register(store)
    store.commit_chunks("one", chunks(), [[1.0, 0.0], [0.0, 1.0]], "original")
    replacement = chunks("new")
    replacement[1]["id"] = replacement[0]["id"]
    with pytest.raises((sqlite3.IntegrityError, psycopg.IntegrityError)):
        store.commit_chunks("one", replacement, [[1.0, 0.0], [0.0, 1.0]], "broken")
    assert [row["id"] for row in store.get_chunks("one")] == ["a-1", "a-2"]
    assert store.document("one")["profile"] == "original"
    assert store.document("one")["status"] == "ready"
    assert store.lexical_search("Annual", "original")[0]["id"] == "a-1"


def test_lexical_multilingual_scope_and_lifecycle(store):
    register(store)
    register(store, "secret")
    page = [{"id": "policy", "page": 1, "ordinal": 0, "text": "旅費規程 TR-2026.2 は 2026-04-01 発効。申請期限 3 日。"}]
    store.commit_chunks("one", page, [[1.0, 0.0]], "p")
    store.commit_chunks("secret", [dict(page[0], id="private")], [[1.0, 0.0]], "p")
    for question in ("TR-2026.2", "2026-04-01", "旅費", "3", "ＴＲ－２０２６．２"):
        assert [r["id"] for r in store.lexical_search(question, "p", ["one"])] == ["policy"]
    assert store.lexical_search("旅費", "other") == []
    assert store.lexical_search("旅費", "p", []) == []
    assert store.search([1.0, 0.0], "p", []) == []
    assert not store.has_searchable("p", [])
    replacement = [dict(page[0], text="Replacement benefits only.")]
    store.commit_chunks("one", replacement, [[1.0, 0.0]], "p")
    assert store.lexical_search("旅費", "p", ["one"]) == []
    assert store.lexical_search("Replacement", "p", ["one"])
    store.delete_document("one")
    assert store.lexical_search("Replacement", "p") == []


def test_metadata_filters_before_both_searches(store):
    from backend.governance import RetrievalFilters

    for name in ("current", "archived", "draft", "unknown"):
        register(store, name)
        store.commit_chunks(name, chunks(name), [[1.0, 0.0], [0.0, 1.0]], "p")
    store.set_metadata(
        "current",
        {
            "policy_status": "current",
            "effective_from": "2026-04-01",
            "effective_to": "2026-12-31",
            "department": "HR",
            "document_version": "2",
        },
    )
    store.set_metadata(
        "archived",
        {"policy_status": "archived", "effective_from": "2025-01-01", "effective_to": "2026-03-31", "department": "HR"},
    )
    store.set_metadata("draft", {"policy_status": "draft", "effective_from": "2026-07-01", "department": "HR"})
    for day in ("2026-04-01", "2026-12-31"):
        scope = store.allowed_document_ids(
            filters=RetrievalFilters(policy_status=["current"], as_of=day, department="HR")
        )
        assert scope == ["current"]
        assert {r["document_id"] for r in store.search([1.0, 0.0], "p", scope)} == {"current"}
        assert {r["document_id"] for r in store.lexical_search("policy", "p", scope)} == {"current"}
    assert store.allowed_document_ids(filters=RetrievalFilters(as_of="2025-06-01")) == ["archived"]
    assert store.allowed_document_ids(filters=RetrievalFilters(department="HR' OR 1=1 --")) == []
    with pytest.raises(ValueError):
        store.set_metadata("current", {"effective_from": "2026-12-31", "effective_to": "2026-01-01"})


def test_acl_roles_owner_revocation_and_token_rotation(store):
    register(store)
    register(store, "private")
    user_id, token = store.provision_user("reader", ["reader"])
    user = store.authenticate(token)
    assert store.allowed_document_ids(user) == []
    store.grant_document("one", "reader", "read")
    assert store.allowed_document_ids(user) == ["one"]
    assert store.allowed_document_ids(user, write=True) == []
    store.grant_document("one", "reader", "write")
    assert store.allowed_document_ids(user, write=True) == ["one"]
    store.grant_document("one", "reader", None)
    assert store.allowed_document_ids(user) == []
    store.set_owner("private", user_id)
    assert store.allowed_document_ids(user) == ["private"]
    new_token = store.rotate_token(user_id)
    assert store.authenticate(token) is None
    assert store.authenticate(new_token).id == user_id
    store.set_user_active(user_id, False)
    assert store.authenticate(new_token) is None
    assert "token_digest" not in store.list_users()[0]


def test_settings_dedup_and_dimension_drift(store):
    saved = Settings().model_dump_json()
    store.save_settings(saved)
    assert store.get_settings() == saved
    assert not register(store)["duplicate"]
    assert register(store)["duplicate"]
    store.commit_chunks("one", chunks(), [[1.0, 0.0], [0.0, 1.0]], "profile")
    store.accept_dimensions("profile", 3)
    assert store.document("one")["status"] == "stale"
    assert not store.has_searchable("profile")


def test_hnsw_has_explicit_backend_and_dimension_contract(store):
    register(store)
    store.commit_chunks("one", chunks(), [[1.0, 0.0], [0.0, 1.0]], "profile")
    if store.backend == "sqlite":
        with pytest.raises(ValueError, match="HNSW"):
            store.search([1.0, 0.0], "profile", mode="hnsw")
    else:
        with pytest.raises(ValueError, match="not ready"):
            store.search([1.0, 0.0], "profile", mode="hnsw", top_k=1)
        store.prepare_index("profile", 2)
        plan = store.explain_search([1.0, 0.0], "profile", document_ids=["one"], mode="hnsw", top_k=1)
        assert store.index_name("profile", 2) in json.dumps(plan)
        exact_plan = store.explain_search([1.0, 0.0], "profile", mode="exact", top_k=1)
        assert store.index_name("profile", 2) not in json.dumps(exact_plan)
        rows = store.search([1.0, 0.0], "profile", mode="hnsw", top_k=1)
        assert rows[0]["id"] == "a-1"
        with pytest.raises(ValueError, match="2000"):
            store.prepare_index("profile", 2048)


def test_factory_keeps_explicit_offline_store_isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("RAG_DATABASE_URL", "postgresql://invalid.example/prod")
    result = create_store(tmp_path, database_url="")
    assert result.backend == "sqlite"
    result.close()


def test_hnsw_index_lifecycle_is_outside_query_path(store):
    if store.backend != "pgvector":
        return
    register(store)
    store.commit_chunks("one", chunks(), [[1.0, 0.0], [0.0, 1.0]], "old", search_mode="hnsw")
    old_name = store.index_name("old", 2)
    with store.connect() as db:
        assert db.execute("SELECT to_regclass(%s) AS name", (old_name,)).fetchone()["name"]
    # Replacing the final document of a profile cleans the now-abandoned index.
    store.commit_chunks("one", chunks("new"), [[1.0, 0.0], [0.0, 1.0]], "new", search_mode="hnsw")
    with store.connect() as db:
        assert db.execute("SELECT to_regclass(%s) AS name", (old_name,)).fetchone()["name"] is None
    store.prepare_index = lambda *args: pytest.fail("Query must not create indexes")
    assert store.search([1.0, 0.0], "new", mode="hnsw")[0]["id"] == "new-1"
    new_name = store.index_name("new", 2)
    store.delete_document("one")
    with store.connect() as db:
        assert db.execute("SELECT to_regclass(%s) AS name", (new_name,)).fetchone()["name"] is None


def test_migration_dry_run_checks_actual_pdf_bytes_and_preserves_source(tmp_path):
    source = tmp_path / "source"
    store = Store(source)
    content = b"%PDF-1.7\nfixture bytes for migration integrity verification"
    store.register_document(
        {
            "id": "doc",
            "name": "sample.pdf",
            "sha256": hashlib.sha256(content).hexdigest(),
            "size": len(content),
            "status": "queued",
            "created_at": "2026-01-01",
        }
    )
    (source / "files" / "doc.pdf").write_bytes(content)
    store.commit_chunks("doc", chunks(), [[1.0, 0.0], [0.0, 1.0]], "profile")
    store.update("doc", pages=2)
    snapshot = (source / "knowledge.db").read_bytes()
    result = migrate(source, tmp_path / "destination")
    assert result["status"] == "validated" and result["pdf_sha256_verified"] == 1
    assert (source / "knowledge.db").read_bytes() == snapshot
    assert not (tmp_path / "destination").exists()
    (source / "files" / "doc.pdf").write_bytes(b"%PDF-corrupted")
    with pytest.raises(ValueError, match="SHA-256"):
        migrate(source, tmp_path / "destination")
    store.close()


def test_benchmark_measurements_do_not_fabricate_absent_postgres(tmp_path):
    report = run_benchmark(count=10, dimensions=4, query_count=2, repeats=1, top_k=2, work_dir=tmp_path)
    assert not report["comparison_complete"]
    assert report["backends"]["sqlite_exact"]["status"] == "measured"
    assert report["backends"]["sqlite_exact"]["recall_at_k_against_independent_exact"] == 1
    assert report["backends"]["pgvector_exact"]["status"] == "blocked"
    assert "query_latency_ms" not in report["backends"]["pgvector_exact"]
