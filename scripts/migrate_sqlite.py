"""Explicit, validated SQLite -> PostgreSQL migration; source is read-only.

Stop the app, set RAG_DATABASE_URL, then run:
  python -m scripts.migrate_sqlite --source data --target-data-dir pgdata
  python -m scripts.migrate_sqlite --source data --target-data-dir pgdata --apply
The first command only validates. Never point two running apps at these folders.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import tempfile
from pathlib import Path

from backend.lexical import indexed_text
from backend.store import validate_vector


def validate_source(source, db):
    if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok" or db.execute("PRAGMA foreign_key_check").fetchone():
        raise ValueError("SQLite 数据完整性检查失败。")
    docs = [dict(row) for row in db.execute("SELECT * FROM documents ORDER BY id")]
    total = 0
    for doc in docs:
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", doc["id"]):
            raise ValueError("文档 id 不是安全的文件标识。")
        if doc["status"] in ("queued", "parsing", "embedding"):
            raise ValueError("源数据库存在未完成索引任务；请先处理完毕并停止应用。")
        path = source / "files" / (doc["id"] + ".pdf")
        if not path.is_file():
            raise ValueError(f"PDF 文件缺失：{doc['id']}")
        content = path.read_bytes()
        if len(content) != doc["size"] or hashlib.sha256(content).hexdigest() != doc["sha256"]:
            raise ValueError(f"PDF 大小或 SHA-256 不匹配：{doc['id']}")
        if not content.startswith(b"%PDF-"):
            raise ValueError(f"文件不是 PDF：{doc['id']}")
        count = 0
        for chunk in db.execute("SELECT * FROM chunks WHERE document_id=? ORDER BY ordinal", (doc["id"],)):
            vector = validate_vector(json.loads(chunk["vector"]), allow_zero=True)
            if len(vector) != doc["dimensions"] or not doc["profile"]:
                raise ValueError(f"向量 profile 或维度不匹配：{chunk['id']}")
            if not 1 <= chunk["page"] <= doc["pages"] or chunk["ordinal"] < 0 or not chunk["text"].strip():
                raise ValueError(f"分块元数据无效：{chunk['id']}")
            count += 1
        if count != doc["chunk_count"] or (doc["status"] == "ready" and count == 0):
            raise ValueError(f"分块计数或就绪状态不一致：{doc['id']}")
        total += count
    return docs, total


def migrate(source, target_data_dir, database_url=None, *, apply=False, schema="public"):
    source = Path(source).resolve()
    target_data_dir = Path(target_data_dir).resolve()
    if source == target_data_dir or source in target_data_dir.parents or target_data_dir in source.parents:
        raise ValueError("源目录与目标目录必须分离，且不能互为子目录。")
    path = source / "knowledge.db"
    if not path.is_file():
        raise ValueError("源目录中不存在 knowledge.db。")
    with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        db.execute("BEGIN")  # Stable snapshot, including WAL data; never mutate source.
        docs, chunk_count = validate_source(source, db)
        report = {
            "status": "validated",
            "documents": len(docs),
            "chunks": chunk_count,
            "pdf_sha256_verified": len(docs),
            "source_preserved": True,
        }
        if not apply:
            return report | {"next_step": "Set RAG_DATABASE_URL and rerun with --apply."}
        if not database_url:
            raise ValueError("请设置 RAG_DATABASE_URL 后再执行迁移。")
        if (target_data_dir / "files").exists() and any((target_data_dir / "files").iterdir()):
            raise ValueError("目标 files 目录必须为空；不会覆盖已有文件。")
        from backend.postgres_store import PostgresStore

        target = PostgresStore(target_data_dir, database_url, schema=schema, recover=False)
        moved = []
        try:
            with target.connect() as pg:
                pg.execute(
                    "LOCK TABLE documents,chunks,settings,index_profiles,users,roles,user_roles,document_permissions IN ACCESS EXCLUSIVE MODE"
                )
                if any(
                    pg.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()["count"]
                    for table in (
                        "documents",
                        "chunks",
                        "settings",
                        "index_profiles",
                        "users",
                        "user_roles",
                        "document_permissions",
                    )
                ):
                    raise ValueError("目标数据库必须为空；不会覆盖已有数据。")
                # Stage and recheck the exact bytes that will be served by the app.
                with tempfile.TemporaryDirectory(prefix="migration-", dir=target_data_dir) as stage:
                    stage = Path(stage)
                    for doc in docs:
                        filename = doc["id"] + ".pdf"
                        staged = stage / filename
                        shutil.copyfile(source / "files" / filename, staged)
                        if hashlib.sha256(staged.read_bytes()).hexdigest() != doc["sha256"]:
                            raise ValueError("迁移期间源 PDF 发生变化；已取消。")
                    for row in db.execute("SELECT * FROM settings"):
                        pg.execute("INSERT INTO settings(id,value) VALUES(%s,%s)", (row["id"], row["value"]))
                    for row in db.execute("SELECT * FROM index_profiles"):
                        pg.execute(
                            "INSERT INTO index_profiles(profile,dimensions) VALUES(%s,%s)",
                            (row["profile"], row["dimensions"]),
                        )
                    tables = {row["name"] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                    for table, columns in [
                        ("roles", ("name",)),
                        ("users", ("id", "username", "token_digest", "active")),
                        ("user_roles", ("user_id", "role_name")),
                    ]:
                        if table in tables:
                            for row in db.execute("SELECT * FROM " + table):
                                pg.execute(
                                    "INSERT INTO "
                                    + table
                                    + "("
                                    + ",".join(columns)
                                    + ") VALUES("
                                    + ",".join("%s" for _ in columns)
                                    + ")"
                                    + (" ON CONFLICT(name) DO NOTHING" if table == "roles" else ""),
                                    tuple(row[column] for column in columns),
                                )
                    fields = (
                        "id",
                        "name",
                        "sha256",
                        "size",
                        "status",
                        "pages",
                        "chunk_count",
                        "profile",
                        "dimensions",
                        "error",
                        "warning",
                        "created_at",
                    )
                    for doc in docs:
                        metadata_fields = tuple(
                            key
                            for key in (
                                "policy_status",
                                "effective_from",
                                "effective_to",
                                "department",
                                "document_version",
                                "owner_id",
                            )
                            if key in doc
                        )
                        doc_fields = fields + metadata_fields
                        pg.execute(
                            "INSERT INTO documents("
                            + ",".join(doc_fields)
                            + ") VALUES("
                            + ",".join("%s" for _ in doc_fields)
                            + ")",
                            tuple(doc[key] for key in doc_fields),
                        )
                        for row in db.execute(
                            "SELECT * FROM chunks WHERE document_id=? ORDER BY ordinal", (doc["id"],)
                        ):
                            pg.execute(
                                "INSERT INTO chunks(id,document_id,page,ordinal,text,vector,profile,dimensions,lexical) VALUES(%s,%s,%s,%s,%s,%s::vector,%s,%s,to_tsvector('simple',%s))",
                                (
                                    row["id"],
                                    doc["id"],
                                    row["page"],
                                    row["ordinal"],
                                    row["text"],
                                    row["vector"],
                                    doc["profile"],
                                    doc["dimensions"],
                                    indexed_text(row["text"]),
                                ),
                            )
                    if "document_permissions" in tables:
                        for row in db.execute("SELECT * FROM document_permissions"):
                            pg.execute(
                                "INSERT INTO document_permissions(document_id,role_name,permission) VALUES(%s,%s,%s)",
                                (row["document_id"], row["role_name"], row["permission"]),
                            )
                    if pg.execute("SELECT COUNT(*) AS count FROM chunks").fetchone()["count"] != chunk_count:
                        raise ValueError("目标分块计数校验失败。")
                    for doc in docs:
                        final = target_data_dir / "files" / (doc["id"] + ".pdf")
                        if final.exists():
                            raise ValueError("目标 PDF 已存在；不会覆盖。")
                        # Exclusive creation protects against an accidental parallel migration.
                        with final.open("xb") as output:
                            moved.append(final)
                            output.write((stage / final.name).read_bytes())
            return report | {"status": "migrated", "database_backend": "pgvector"}
        except Exception:
            # PostgreSQL rolls back before file cleanup. Restrict cleanup to files
            # created by this invocation inside the already resolved target root.
            for path in moved:
                if path.resolve().parent == target_data_dir / "files":
                    path.unlink(missing_ok=True)
            raise
        finally:
            target.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--target-data-dir", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps(
            migrate(args.source, args.target_data_dir, os.getenv("RAG_DATABASE_URL"), apply=args.apply),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
