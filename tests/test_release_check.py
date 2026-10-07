from scripts.release_check import private_path, sensitive


def test_release_rejects_private_files_and_known_or_generic_secrets():
    for name in (".env", ".env.demo", "data/file.pdf", ".secrets/reviewer.txt", "backup.sqlite3", "private.key"):
        assert private_path(name)
    for name in (".env.example", ".env.demo.example", "docs/deployment.md", "samples/example.pdf"):
        assert not private_path(name)
    assert sensitive(b"some customer credential", [b"customer credential"])
    assert sensitive(b"sk-" + b"a" * 40)
    assert sensitive(b"-----BEGIN " + b"PRIVATE KEY-----")
    assert not sensitive(b"RAG_API_KEY=\nRAG_DEMO_DAILY_USD=1\n")
