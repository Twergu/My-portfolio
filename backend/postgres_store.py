"""PostgreSQL storage with pooled connections and native pgvector search.

Exact cosine search supports 1..16000 dimensions. HNSW is an explicit opt-in for
1..2000 dimensions; no implicit truncation, precision reduction or fallback.
See https://github.com/pgvector/pgvector#can-i-store-vectors-with-different-dimensions
"""

import hashlib
import json
import math
import re
from contextlib import contextmanager
from pathlib import Path

import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from .governance import GovernanceMixin
from .lexical import indexed_text, query_terms
from .store import chunk_records, validate_vector


class PostgresStore(GovernanceMixin):
    backend = "pgvector"

    def __init__(self, folder, database_url, *, schema="public", recover=True):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        (self.folder / "files").mkdir(exist_ok=True)
        self.schema = schema
        # vector lives in public; isolated benchmark schemas only contain app data.
        with psycopg.connect(database_url, autocommit=True, connect_timeout=10) as db:
            db.execute("CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public")
            db.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(schema)))

        def configure(db):
            db.execute(sql.SQL("SET search_path TO {}, public").format(sql.Identifier(schema)))
            db.commit()

        self.pool = ConnectionPool(
            database_url,
            min_size=1,
            max_size=4,
            timeout=15,
            kwargs={"row_factory": dict_row, "connect_timeout": 10, "prepare_threshold": None},
            configure=configure,
            open=False,
        )
        try:
            self.pool.open(wait=True, timeout=15)
            with self.connect() as db:
                db.execute("""
                    CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY CHECK(id=1), value TEXT NOT NULL);
                    CREATE TABLE IF NOT EXISTS index_profiles (profile TEXT PRIMARY KEY, dimensions INTEGER NOT NULL);
                    CREATE TABLE IF NOT EXISTS documents (
                        id TEXT PRIMARY KEY, name TEXT NOT NULL, sha256 TEXT UNIQUE NOT NULL,
                        size BIGINT NOT NULL, status TEXT NOT NULL, pages INTEGER DEFAULT 0,
                        chunk_count INTEGER DEFAULT 0, profile TEXT DEFAULT '', dimensions INTEGER DEFAULT 0,
                        error TEXT DEFAULT '', warning TEXT DEFAULT '', created_at TEXT NOT NULL
                    );
                    CREATE TABLE IF NOT EXISTS chunks (
                        id TEXT PRIMARY KEY, document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                        page INTEGER NOT NULL CHECK(page>0), ordinal INTEGER NOT NULL CHECK(ordinal>=0),
                        text TEXT NOT NULL, vector vector NOT NULL, profile TEXT NOT NULL,
                        dimensions INTEGER NOT NULL CHECK(dimensions BETWEEN 1 AND 16000),
                        CHECK(vector_dims(vector)=dimensions)
                    );
                    CREATE INDEX IF NOT EXISTS chunks_document ON chunks(document_id);
                    CREATE INDEX IF NOT EXISTS chunks_profile_dimensions ON chunks(profile,dimensions);
                """)
                db.execute("ALTER TABLE chunks ADD COLUMN IF NOT EXISTS lexical tsvector")
                with db.cursor() as cursor:
                    cursor.executemany(
                        "UPDATE chunks SET lexical=to_tsvector('simple',%s) WHERE id=%s",
                        [
                            (indexed_text(row["text"]), row["id"])
                            for row in db.execute("SELECT id,text FROM chunks WHERE lexical IS NULL")
                        ],
                    )
                db.execute("CREATE INDEX IF NOT EXISTS chunks_lexical ON chunks USING gin(lexical)")
                if recover:
                    db.execute(
                        "UPDATE documents SET status='error',error='上次处理被中断，请点击重试。' WHERE status IN ('queued','parsing','embedding')"
                    )
            self.init_governance()
        except Exception:
            self.pool.close()
            raise

    @contextmanager
    def connect(self):
        # Pool context commits on success, rolls back on errors, then returns the
        # same physical connection to the pool. A failed transaction cannot leak.
        with self.pool.connection() as db:
            yield db

    def close(self):
        self.pool.close()

    def all_documents(self):
        with self.connect() as db:
            return db.execute("SELECT * FROM documents ORDER BY created_at DESC").fetchall()

    def document(self, doc_id):
        with self.connect() as db:
            return db.execute("SELECT * FROM documents WHERE id=%s", (doc_id,)).fetchone()

    def update(self, doc_id, **fields):
        allowed = {"status", "pages", "chunk_count", "profile", "dimensions", "error", "warning"}
        if not fields or not set(fields).issubset(allowed):
            raise ValueError("Invalid document update")
        assignments = sql.SQL(",").join(sql.SQL("{}=%s").format(sql.Identifier(key)) for key in fields)
        with self.connect() as db:
            db.execute(sql.SQL("UPDATE documents SET {} WHERE id=%s").format(assignments), (*fields.values(), doc_id))

    def accept_dimensions(self, profile, dimensions):
        if not 1 <= dimensions <= 16000:
            raise ValueError("pgvector 向量维度必须在 1 到 16000 之间。")
        with self.connect() as db:
            db.execute(
                "INSERT INTO index_profiles(profile,dimensions) VALUES(%s,%s) ON CONFLICT(profile) DO UPDATE SET dimensions=excluded.dimensions",
                (profile, dimensions),
            )
            db.execute(
                "UPDATE documents SET status='stale',error='模型返回的向量维度已变化，请重新建立索引。' WHERE status='ready' AND profile=%s AND dimensions!=%s",
                (profile, dimensions),
            )

    def get_settings(self):
        with self.connect() as db:
            row = db.execute("SELECT value FROM settings WHERE id=1").fetchone()
            return row["value"] if row else None

    def save_settings(self, value):
        with self.connect() as db:
            db.execute(
                "INSERT INTO settings(id,value) VALUES(1,%s) ON CONFLICT(id) DO UPDATE SET value=excluded.value",
                (value,),
            )

    def find_by_digest(self, digest):
        with self.connect() as db:
            return db.execute("SELECT id FROM documents WHERE sha256=%s", (digest,)).fetchone()

    def count_documents(self):
        with self.connect() as db:
            return db.execute("SELECT COUNT(*) AS count FROM documents").fetchone()["count"]

    def register_document(self, document, max_documents=100):
        with self.connect() as db:
            # Serializes the check+insert capacity constraint across processes.
            db.execute("LOCK TABLE documents IN SHARE ROW EXCLUSIVE MODE")
            existing = db.execute("SELECT id FROM documents WHERE sha256=%s", (document["sha256"],)).fetchone()
            if existing:
                return {"id": existing["id"], "duplicate": True}
            if db.execute("SELECT COUNT(*) AS count FROM documents").fetchone()["count"] >= max_documents:
                raise ValueError(f"当前版本最多存储 {max_documents} 份文档，请删除不需要的文档。")
            keys = ("id", "name", "sha256", "size", "status", "created_at")
            db.execute(
                "INSERT INTO documents(id,name,sha256,size,status,created_at) VALUES(%s,%s,%s,%s,%s,%s)",
                tuple(document[key] for key in keys),
            )
        return {"id": document["id"], "duplicate": False}

    def commit_chunks(self, doc_id, chunks, vectors, profile, warning="", search_mode="exact"):
        records, dimensions = chunk_records(chunks, vectors)
        with self.connect() as db:
            self._lifecycle_lock(db)
            db.execute("DELETE FROM chunks WHERE document_id=%s", (doc_id,))
            with db.cursor() as cursor:
                cursor.executemany(
                    "INSERT INTO chunks(id,document_id,page,ordinal,text,vector,profile,dimensions,lexical) VALUES(%s,%s,%s,%s,%s,%s::vector,%s,%s,to_tsvector('simple',%s))",
                    [
                        (cid, doc_id, page, ordinal, text, json.dumps(vector), profile, dimensions, indexed_text(text))
                        for cid, page, ordinal, text, vector in records
                    ],
                )
            if search_mode == "hnsw":
                self._prepare_index_db(db, profile, dimensions)
            db.execute(
                "UPDATE documents SET status='ready',chunk_count=%s,profile=%s,dimensions=%s,warning=%s,error='' WHERE id=%s",
                (len(records), profile, dimensions, warning, doc_id),
            )
            self._cleanup_indexes_db(db)

    def get_chunks(self, doc_id, limit=2000):
        with self.connect() as db:
            return db.execute(
                "SELECT id,page,ordinal,text FROM chunks WHERE document_id=%s ORDER BY ordinal LIMIT %s",
                (doc_id, limit),
            ).fetchall()

    def delete_document(self, doc_id):
        with self.connect() as db:
            self._lifecycle_lock(db)
            db.execute("DELETE FROM documents WHERE id=%s", (doc_id,))
            self._cleanup_indexes_db(db)

    def has_searchable(self, profile, document_ids=None):
        where = "d.status='ready' AND d.profile=%s"
        params = [profile]
        if document_ids is not None:
            where += " AND d.id=ANY(%s)"
            params.append(list(document_ids))
        with self.connect() as db:
            return (
                db.execute(
                    "SELECT 1 FROM chunks c JOIN documents d ON c.document_id=d.id WHERE " + where + " LIMIT 1", params
                ).fetchone()
                is not None
            )

    @staticmethod
    def index_name(profile, dimensions):
        return "chunks_hnsw_" + hashlib.sha256(f"{profile}:{dimensions}".encode()).hexdigest()[:24]

    def _lifecycle_lock(self, db):
        db.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (self.schema + ":hnsw-lifecycle",))

    def _prepare_index_db(self, db, profile, dimensions):
        if not 1 <= dimensions <= 2000:
            raise ValueError(
                "HNSW vector 索引仅支持最多 2000 维；请使用 exact，或选择最多 2000 维的 Embedding 模型并重建索引。"
            )
        name = self.index_name(profile, dimensions)
        statement = sql.SQL(
            "CREATE INDEX IF NOT EXISTS {} ON chunks USING hnsw ((vector::vector({})) vector_cosine_ops) WHERE profile={} AND dimensions={}"
        ).format(sql.Identifier(name), sql.Literal(dimensions), sql.Literal(profile), sql.Literal(dimensions))
        db.execute(statement)

    def prepare_index(self, profile, dimensions):
        """Explicit indexing/maintenance operation. Never called by search."""
        with self.connect() as db:
            self._lifecycle_lock(db)
            self._prepare_index_db(db, profile, dimensions)

    def _cleanup_indexes_db(self, db, active_profile=None):
        pairs = db.execute("SELECT DISTINCT profile,dimensions FROM documents WHERE status='ready'").fetchall()
        keep = {
            self.index_name(row["profile"], row["dimensions"])
            for row in pairs
            if active_profile is None or row["profile"] == active_profile
        }
        indexes = db.execute(
            "SELECT indexname FROM pg_indexes WHERE schemaname=%s AND tablename='chunks'", (self.schema,)
        ).fetchall()
        removed = []
        for row in indexes:
            name = row["indexname"]
            # Only indexes in this application's reserved namespace are managed.
            if re.fullmatch(r"chunks_hnsw_[0-9a-f]{24}", name) and name not in keep:
                db.execute(sql.SQL("DROP INDEX {}.{}").format(sql.Identifier(self.schema), sql.Identifier(name)))
                removed.append(name)
        return removed

    def maintain_indexes(self, profile, mode):
        """Run at startup/settings changes, away from the user query path."""
        with self.connect() as db:
            self._lifecycle_lock(db)
            removed = self._cleanup_indexes_db(db, active_profile=profile)
            if mode == "hnsw":
                rows = db.execute(
                    "SELECT DISTINCT dimensions FROM documents WHERE profile=%s AND status='ready'", (profile,)
                ).fetchall()
                for row in rows:
                    self._prepare_index_db(db, profile, row["dimensions"])
        return removed

    @staticmethod
    def _search_statement(query, profile, document_ids, top_k, text_filter):
        dimensions = len(query)
        vector = json.dumps(query)
        # Literals are escaped by psycopg, not interpolated strings. Constants
        # let the planner prove eligibility of each model/dimension partial index.
        where = sql.SQL(
            "c.profile={} AND c.dimensions={} AND d.profile={} AND d.dimensions={} AND d.status='ready' AND vector_norm(c.vector)>0"
        ).format(sql.Literal(profile), sql.Literal(dimensions), sql.Literal(profile), sql.Literal(dimensions))
        if document_ids is not None:
            where += sql.SQL(" AND d.id=ANY(%s)")
        distance = sql.SQL("c.vector::vector({}) <=> %s::vector").format(sql.Literal(dimensions))
        statement = sql.SQL(
            "SELECT c.id,c.document_id,c.page,c.text,d.name,1-({}) AS score FROM chunks c JOIN documents d ON c.document_id=d.id WHERE {} ORDER BY {} ASC"
        ).format(distance, where, distance)
        # Parameter order: SELECT vector, optional scope, ORDER vector.
        params = [vector] + ([list(document_ids)] if document_ids is not None else []) + [vector]
        if not text_filter:
            statement += sql.SQL(" LIMIT %s")
            params.append(top_k)
        return statement, params

    def _configure_search(self, db, profile, dimensions, mode, ef_search):
        if mode == "exact":
            # Explicit exact baseline even if this table already has HNSW indexes.
            db.execute("SET LOCAL enable_indexscan=off")
            db.execute("SET LOCAL enable_bitmapscan=off")
        elif mode == "hnsw":
            if not 1 <= dimensions <= 2000:
                raise ValueError("HNSW only supports dimensions up to 2000.")
            if not 1 <= ef_search <= 1000:
                raise ValueError("HNSW ef_search must be between 1 and 1000.")
            name = self.index_name(profile, dimensions)
            exists = db.execute("SELECT to_regclass(%s) AS name", (f"{self.schema}.{name}",)).fetchone()["name"]
            if exists is None:
                raise ValueError(
                    "HNSW index is not ready; rebuild the document index or run index maintenance before querying."
                )
            # HNSW is explicitly requested. A bitmap/B-tree scan followed by a
            # sort is exact search, and must not masquerade as an ANN measurement.
            db.execute("SET LOCAL enable_seqscan=off")
            db.execute("SET LOCAL enable_bitmapscan=off")
            db.execute("SET LOCAL enable_sort=off")
            db.execute("SELECT set_config('hnsw.ef_search', %s, true)", (str(ef_search),))
            db.execute("SET LOCAL hnsw.iterative_scan='strict_order'")
        else:
            raise ValueError("检索模式必须是 exact 或 hnsw。")

    def lexical_search(self, question, profile, document_ids=None, top_k=20):
        terms = query_terms(question)
        if not terms or top_k < 1:
            return []
        where = "d.status='ready' AND d.profile=%s AND c.profile=%s"
        params = [" | ".join(terms), profile, profile]
        if document_ids is not None:
            where += " AND d.id=ANY(%s)"
            params.append(list(document_ids))
        with self.connect() as db:
            return db.execute(
                "SELECT c.id,c.document_id,c.page,c.text,d.name,ts_rank_cd(c.lexical,q) AS score "
                "FROM chunks c JOIN documents d ON d.id=c.document_id, to_tsquery('simple',%s) q "
                "WHERE c.lexical @@ q AND " + where + " ORDER BY score DESC,c.id LIMIT %s",
                [*params, top_k],
            ).fetchall()

    def explain_search(self, query_vector, profile, document_ids=None, top_k=5, mode="exact", ef_search=100):
        """Inspect the production SQL, including document scope and planner settings."""
        query = validate_vector(query_vector, allow_zero=True)
        statement, params = self._search_statement(query, profile, document_ids, top_k, None)
        with self.connect() as db:
            self._configure_search(db, profile, len(query), mode, ef_search)
            # Search uses a server-side cursor. Explain DECLARE so its planner
            # context is the same as the timed path, rather than a simpler probe.
            return db.execute(
                sql.SQL("EXPLAIN (FORMAT JSON) DECLARE knowledge_plan CURSOR FOR ") + statement, params
            ).fetchone()["QUERY PLAN"]

    def search(
        self,
        query_vector,
        profile,
        document_ids=None,
        top_k=5,
        min_score=-1,
        mode="exact",
        text_filter=None,
        ef_search=100,
    ):
        if mode not in ("exact", "hnsw"):
            raise ValueError("检索模式必须是 exact 或 hnsw。")
        query = validate_vector(query_vector, allow_zero=True)
        if mode == "hnsw" and text_filter:
            raise ValueError("本地词法过滤使用 exact 检索；HNSW 用于 API Embedding。")
        if not math.hypot(*query) or top_k < 1:
            return []
        statement, params = self._search_statement(query, profile, document_ids, top_k, text_filter)
        with self.connect() as db:
            self._configure_search(db, profile, len(query), mode, ef_search)
            # A named cursor streams results for lexical filtering; never loads
            # the whole corpus into Python when the local baseline is selected.
            with db.cursor(name="knowledge_search") as cursor:
                cursor.execute(statement, params)
                found = []
                for row in cursor:
                    if not math.isfinite(row["score"]) or row["score"] < min_score:
                        continue
                    if text_filter and not text_filter(row["text"]):
                        continue
                    row["score"] = max(-1.0, min(1.0, row["score"]))
                    found.append(row)
                    if len(found) >= top_k:
                        break
                return found
