import hashlib
import os

from backend.store import Store
from scripts.migrate_sqlite import migrate


def test_migration_preserves_policy_grants_identity_and_fulltext(store, tmp_path):
    if store.backend != "pgvector":
        return
    source = Store(tmp_path / "source")
    content = b"%PDF-1.7\nMigration access fixture"
    source.register_document(
        {
            "id": "policy",
            "name": "policy.pdf",
            "sha256": hashlib.sha256(content).hexdigest(),
            "size": len(content),
            "status": "queued",
            "created_at": "2026-01-01",
        }
    )
    (source.folder / "files" / "policy.pdf").write_bytes(content)
    source.commit_chunks("policy", [{"page": 1, "ordinal": 0, "text": "POL-2026 Leave policy."}], [[1.0, 0.0]], "p")
    source.update("policy", pages=1)
    source.set_metadata("policy", {"policy_status": "current", "effective_from": "2026-01-01", "department": "HR"})
    user_id, token = source.provision_user("reader", ["reader"])
    source.grant_document("policy", "reader", "read")
    result = migrate(source.folder, store.folder, os.environ["RAG_TEST_DATABASE_URL"], apply=True, schema=store.schema)
    assert result["status"] == "migrated"
    principal = store.authenticate(token)
    assert principal.id == user_id
    assert store.allowed_document_ids(principal) == ["policy"]
    assert store.allowed_document_ids(principal, write=True) == []
    assert store.document("policy")["department"] == "HR"
    assert store.lexical_search("POL-2026", "p", ["policy"])[0]["document_id"] == "policy"
    assert (store.folder / "files" / "policy.pdf").read_bytes() == content
