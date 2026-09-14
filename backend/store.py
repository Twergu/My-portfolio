"""SQLite baseline and the storage contract shared by PostgreSQL.

Keep SQLite available for offline development and reproducible comparisons. The
application chooses PostgreSQL through ``create_store`` / RAG_DATABASE_URL.
"""
import heapq
import json
import math
import os
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path


def validate_vector(vector, *, allow_zero=False):
    if not isinstance(vector, (list, tuple)) or not 1 <= len(vector) <= 16000:
        raise ValueError('向量维度必须在 1 到 16000 之间。')
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in vector):
        raise ValueError('向量必须仅包含有限数值。')
    norm = math.hypot(*vector)
    if not math.isfinite(norm) or (not norm and not allow_zero):
        raise ValueError('向量不能为零或溢出。')
    return list(vector)


def chunk_records(chunks, vectors):
    if not chunks or len(chunks) != len(vectors):
        raise ValueError('分块与向量数量不匹配。')
    records = []
    dimensions = len(validate_vector(vectors[0], allow_zero=True))
    for chunk, vector in zip(chunks, vectors, strict=True):
        vector = validate_vector(vector, allow_zero=True)
        if len(vector) != dimensions:
            raise ValueError('同一索引批次的向量维度必须一致。')
        if int(chunk['page']) < 1 or int(chunk['ordinal']) < 0 or not chunk['text'].strip():
            raise ValueError('无效的分块页码、顺序或文本。')
        records.append((chunk.get('id') or uuid.uuid4().hex, int(chunk['page']),
                        int(chunk['ordinal']), chunk['text'], vector))
    return records, dimensions


class Store:
    backend = 'sqlite'

    def __init__(self, folder, *, recover=True):
        self.folder = folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        (folder / 'files').mkdir(exist_ok=True)
        self.path = folder / 'knowledge.db'
        with self.connect() as db:
            db.executescript('''
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY CHECK(id=1), value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS index_profiles (profile TEXT PRIMARY KEY, dimensions INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL, sha256 TEXT UNIQUE NOT NULL,
                    size INTEGER NOT NULL, status TEXT NOT NULL, pages INTEGER DEFAULT 0,
                    chunk_count INTEGER DEFAULT 0, profile TEXT DEFAULT '', dimensions INTEGER DEFAULT 0,
                    error TEXT DEFAULT '', warning TEXT DEFAULT '', created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS chunks (
                    id TEXT PRIMARY KEY, document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                    page INTEGER NOT NULL, ordinal INTEGER NOT NULL, text TEXT NOT NULL, vector TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS chunks_document ON chunks(document_id);
            ''')
            if recover:
                db.execute("UPDATE documents SET status='error', error='上次处理被中断，请点击重试。' WHERE status IN ('queued','parsing','embedding')")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=20)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def all_documents(self):
        with self.connect() as db:
            return [dict(row) for row in db.execute('SELECT * FROM documents ORDER BY created_at DESC')]

    def document(self, doc_id):
        with self.connect() as db:
            row = db.execute('SELECT * FROM documents WHERE id=?', (doc_id,)).fetchone()
            return dict(row) if row else None

    def update(self, doc_id, **fields):
        allowed = {'status', 'pages', 'chunk_count', 'profile', 'dimensions', 'error', 'warning'}
        if not fields or not set(fields).issubset(allowed):
            raise ValueError('Invalid document update')
        with self.connect() as db:
            db.execute('UPDATE documents SET ' + ','.join(f'{key}=?' for key in fields) + ' WHERE id=?', (*fields.values(), doc_id))

    def accept_dimensions(self, profile, dimensions):
        """An endpoint/model alias can change its vector space without changing its name."""
        with self.connect() as db:
            db.execute('INSERT OR REPLACE INTO index_profiles(profile,dimensions) VALUES(?,?)', (profile, dimensions))
            db.execute("UPDATE documents SET status='stale', error='模型返回的向量维度已变化，请重新建立索引。' WHERE status='ready' AND profile=? AND dimensions!=?",
                       (profile, dimensions))

    def get_settings(self):
        with self.connect() as db:
            row = db.execute('SELECT value FROM settings WHERE id=1').fetchone()
            return row['value'] if row else None

    def save_settings(self, value):
        with self.connect() as db:
            db.execute('INSERT OR REPLACE INTO settings(id,value) VALUES(1,?)', (value,))

    def find_by_digest(self, digest):
        with self.connect() as db:
            row = db.execute('SELECT id FROM documents WHERE sha256=?', (digest,)).fetchone()
            return dict(row) if row else None

    def count_documents(self):
        with self.connect() as db:
            return db.execute('SELECT COUNT(*) FROM documents').fetchone()[0]

    def register_document(self, document, max_documents=100):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT id FROM documents WHERE sha256=?', (document['sha256'],)).fetchone()
            if row:
                return {'id': row['id'], 'duplicate': True}
            if db.execute('SELECT COUNT(*) FROM documents').fetchone()[0] >= max_documents:
                raise ValueError(f'当前版本最多存储 {max_documents} 份文档，请删除不需要的文档。')
            keys = ('id', 'name', 'sha256', 'size', 'status', 'created_at')
            db.execute('INSERT INTO documents(id,name,sha256,size,status,created_at) VALUES(?,?,?,?,?,?)',
                       tuple(document[key] for key in keys))
        return {'id': document['id'], 'duplicate': False}

    def commit_chunks(self, doc_id, chunks, vectors, profile, warning=''):
        records, dimensions = chunk_records(chunks, vectors)
        with self.connect() as db:
            db.execute('DELETE FROM chunks WHERE document_id=?', (doc_id,))
            db.executemany('INSERT INTO chunks(id,document_id,page,ordinal,text,vector) VALUES(?,?,?,?,?,?)',
                           [(cid, doc_id, page, ordinal, text, json.dumps(vector))
                            for cid, page, ordinal, text, vector in records])
            db.execute("UPDATE documents SET status='ready',chunk_count=?,profile=?,dimensions=?,warning=?,error='' WHERE id=?",
                       (len(records), profile, dimensions, warning, doc_id))

    def get_chunks(self, doc_id, limit=2000):
        with self.connect() as db:
            return [dict(row) for row in db.execute(
                'SELECT id,page,ordinal,text FROM chunks WHERE document_id=? ORDER BY ordinal LIMIT ?', (doc_id, limit))]

    def delete_document(self, doc_id):
        with self.connect() as db:
            db.execute('DELETE FROM documents WHERE id=?', (doc_id,))

    @staticmethod
    def _scope(profile, document_ids):
        where = "d.status='ready' AND d.profile=?"
        params = [profile]
        if document_ids:
            where += ' AND d.id IN (' + ','.join('?' for _ in document_ids) + ')'
            params.extend(document_ids)
        return where, params

    def has_searchable(self, profile, document_ids=None):
        where, params = self._scope(profile, document_ids)
        with self.connect() as db:
            return db.execute('SELECT 1 FROM chunks c JOIN documents d ON c.document_id=d.id WHERE ' + where + ' LIMIT 1', params).fetchone() is not None

    def search(self, query_vector, profile, document_ids=None, top_k=5, min_score=-1, mode='exact', text_filter=None):
        if mode != 'exact':
            raise ValueError('SQLite 仅支持 exact 检索；HNSW 需要 PostgreSQL + pgvector。')
        query = validate_vector(query_vector, allow_zero=True)
        query_norm = math.hypot(*query)
        if not query_norm or top_k < 1:
            return []
        where, params = self._scope(profile, document_ids)
        where += ' AND d.dimensions=?'
        params.append(len(query))
        ranked = []
        with self.connect() as db:
            for raw in db.execute('SELECT c.id,c.document_id,c.page,c.text,c.vector,d.name FROM chunks c JOIN documents d ON c.document_id=d.id WHERE ' + where, params):
                row = dict(raw)
                if text_filter and not text_filter(row['text']):
                    continue
                vector = json.loads(row.pop('vector'))
                if len(vector) != len(query):
                    continue
                norm = math.hypot(*vector)
                if not norm:
                    continue
                score = sum(a * b for a, b in zip(query, vector)) / (query_norm * norm)
                if score < min_score:
                    continue
                row['score'] = max(-1., min(1., score))
                entry = (score, row['id'], row)
                if len(ranked) < top_k:
                    heapq.heappush(ranked, entry)
                elif entry[:2] > ranked[0][:2]:
                    heapq.heapreplace(ranked, entry)
        return [entry[2] for entry in sorted(ranked, reverse=True)]

    def close(self):
        pass


def create_store(folder, database_url=None):
    from .config import environment_database_url
    database_url = environment_database_url() if database_url is None else database_url
    if not database_url:
        return Store(folder)
    if not database_url.startswith(('postgresql://', 'postgres://')):
        raise ValueError('RAG_DATABASE_URL 必须为 postgresql:// 或 postgres:// 地址。')
    from .postgres_store import PostgresStore
    return PostgresStore(folder, database_url)
