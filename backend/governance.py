"""Server-owned identity, role grants and metadata predicates shared by stores."""

import hashlib
import secrets
import uuid
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DocumentMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")
    policy_status: Literal["unclassified", "current", "archived", "draft"] = "unclassified"
    effective_from: date | None = None
    effective_to: date | None = None
    department: str = Field(default="", max_length=120)
    document_version: str = Field(default="", max_length=80)

    @model_validator(mode="after")
    def valid_interval(self):
        if self.effective_from and self.effective_to and self.effective_from > self.effective_to:
            raise ValueError("effective_from must not follow effective_to")
        return self


class RetrievalFilters(BaseModel):
    model_config = ConfigDict(extra="forbid")
    policy_status: list[Literal["unclassified", "current", "archived", "draft"]] = Field(
        default_factory=list, max_length=4
    )
    as_of: date | None = None
    department: str | None = Field(default=None, max_length=120)


class Principal(BaseModel):
    id: str
    username: str
    roles: list[str]

    @property
    def admin(self):
        return "admin" in self.roles

    @property
    def can_upload(self):
        return self.admin or "editor" in self.roles


LOCAL_ADMIN = Principal(id="local", username="Local single user", roles=["admin"])


def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


class GovernanceMixin:
    def _execute(self, db, statement, params=()):
        return db.execute(statement.replace("?", "%s") if self.backend == "pgvector" else statement, params)

    def init_governance(self):
        with self.connect() as db:
            columns = (
                {} if self.backend == "pgvector" else {r["name"] for r in db.execute("PRAGMA table_info(documents)")}
            )
            for name, definition in [
                ("policy_status", "TEXT NOT NULL DEFAULT 'unclassified'"),
                ("effective_from", "TEXT"),
                ("effective_to", "TEXT"),
                ("department", "TEXT NOT NULL DEFAULT ''"),
                ("document_version", "TEXT NOT NULL DEFAULT ''"),
                ("owner_id", "TEXT"),
            ]:
                if self.backend == "pgvector":
                    db.execute(f"ALTER TABLE documents ADD COLUMN IF NOT EXISTS {name} {definition}")
                elif name not in columns:
                    db.execute(f"ALTER TABLE documents ADD COLUMN {name} {definition}")
            for statement in [
                "CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, username TEXT UNIQUE NOT NULL, token_digest TEXT UNIQUE NOT NULL, active INTEGER NOT NULL DEFAULT 1)",
                "CREATE TABLE IF NOT EXISTS roles (name TEXT PRIMARY KEY)",
                "CREATE TABLE IF NOT EXISTS user_roles (user_id TEXT REFERENCES users(id) ON DELETE CASCADE, role_name TEXT REFERENCES roles(name) ON DELETE CASCADE, PRIMARY KEY(user_id,role_name))",
                "CREATE TABLE IF NOT EXISTS document_permissions (document_id TEXT REFERENCES documents(id) ON DELETE CASCADE, role_name TEXT REFERENCES roles(name) ON DELETE CASCADE, permission TEXT NOT NULL CHECK(permission IN ('read','write')), PRIMARY KEY(document_id,role_name))",
                "CREATE INDEX IF NOT EXISTS documents_metadata ON documents(policy_status,department,effective_from,effective_to)",
            ]:
                db.execute(statement)
            for role in ("admin", "editor", "reader"):
                self._execute(db, "INSERT INTO roles(name) VALUES(?) ON CONFLICT(name) DO NOTHING", (role,))

    def set_metadata(self, doc_id, metadata):
        fields = DocumentMetadata.model_validate(metadata).model_dump(mode="json")
        with self.connect() as db:
            self._execute(
                db,
                "UPDATE documents SET " + ",".join(key + "=?" for key in fields) + " WHERE id=?",
                (*fields.values(), doc_id),
            )
        return fields

    def set_owner(self, doc_id, user_id):
        with self.connect() as db:
            if not self._execute(db, "SELECT id FROM users WHERE id=?", (user_id,)).fetchone():
                raise ValueError("Unknown owner")
            self._execute(db, "UPDATE documents SET owner_id=? WHERE id=?", (user_id, doc_id))

    def allowed_document_ids(self, principal=None, requested=None, filters=None, *, write=False):
        # None is an explicit internal unrestricted caller. HTTP always supplies
        # a server-authenticated Principal (or the documented local-mode admin).
        where, params = ["1=1"], []
        if principal is not None and not principal.admin:
            where.append(
                "(d.owner_id=? OR EXISTS (SELECT 1 FROM document_permissions dp "
                "JOIN user_roles ur ON ur.role_name=dp.role_name WHERE dp.document_id=d.id AND ur.user_id=?"
                + (" AND dp.permission='write'" if write else "")
                + "))"
            )
            params.extend([principal.id, principal.id])
        if requested is not None:
            if not requested:
                return []
            where.append("d.id IN (" + ",".join("?" for _ in requested) + ")")
            params.extend(requested)
        filters = filters or RetrievalFilters()
        if filters.policy_status:
            where.append("d.policy_status IN (" + ",".join("?" for _ in filters.policy_status) + ")")
            params.extend(filters.policy_status)
        if filters.department is not None:
            where.append("d.department=?")
            params.append(filters.department)
        if filters.as_of:
            # Undated/unclassified policy is excluded from date-scoped answers.
            where.extend(
                ["d.effective_from IS NOT NULL", "d.effective_from<=?", "(d.effective_to IS NULL OR d.effective_to>=?)"]
            )
            params.extend([filters.as_of.isoformat()] * 2)
        with self.connect() as db:
            return [
                r["id"]
                for r in self._execute(
                    db, "SELECT d.id FROM documents d WHERE " + " AND ".join(where) + " ORDER BY d.id", params
                )
            ]

    def provision_user(self, username, roles):
        if not username.strip() or len(username) > 120 or not roles:
            raise ValueError("Username and at least one role are required")
        token = secrets.token_urlsafe(32)
        with self.connect() as db:
            for role in roles:
                if not self._execute(db, "SELECT name FROM roles WHERE name=?", (role,)).fetchone():
                    raise ValueError("Unknown role")
            self._execute(
                db,
                "INSERT INTO users(id,username,token_digest) VALUES(?,?,?)",
                (user_id := uuid.uuid4().hex, username.strip(), token_hash(token)),
            )
            for role in set(roles):
                self._execute(db, "INSERT INTO user_roles(user_id,role_name) VALUES(?,?)", (user_id, role))
        return user_id, token

    def authenticate(self, token):
        if not token or len(token) > 200:
            return None
        with self.connect() as db:
            row = self._execute(
                db, "SELECT id,username FROM users WHERE token_digest=? AND active=1", (token_hash(token),)
            ).fetchone()
            if row is None:
                return None
            roles = [
                r["role_name"]
                for r in self._execute(db, "SELECT role_name FROM user_roles WHERE user_id=?", (row["id"],))
            ]
            return Principal(id=row["id"], username=row["username"], roles=roles)

    def set_user_active(self, user_id, active):
        with self.connect() as db:
            self._execute(db, "UPDATE users SET active=? WHERE id=?", (int(active), user_id))

    def set_user_roles(self, user_id, roles):
        with self.connect() as db:
            self._execute(db, "DELETE FROM user_roles WHERE user_id=?", (user_id,))
            for role in set(roles):
                self._execute(db, "INSERT INTO user_roles(user_id,role_name) VALUES(?,?)", (user_id, role))

    def rotate_token(self, user_id):
        token = secrets.token_urlsafe(32)
        with self.connect() as db:
            if not self._execute(db, "SELECT id FROM users WHERE id=?", (user_id,)).fetchone():
                raise ValueError("Unknown user")
            self._execute(db, "UPDATE users SET token_digest=? WHERE id=?", (token_hash(token), user_id))
        return token

    def create_role(self, name):
        if not name.strip() or len(name) > 80:
            raise ValueError("Role name is required (max 80 characters)")
        with self.connect() as db:
            self._execute(db, "INSERT INTO roles(name) VALUES(?) ON CONFLICT(name) DO NOTHING", (name,))

    def grant_document(self, doc_id, role, permission):
        if permission not in ("read", "write", None):
            raise ValueError("Invalid permission")
        with self.connect() as db:
            self._execute(db, "DELETE FROM document_permissions WHERE document_id=? AND role_name=?", (doc_id, role))
            if permission:
                self._execute(
                    db,
                    "INSERT INTO document_permissions(document_id,role_name,permission) VALUES(?,?,?)",
                    (doc_id, role, permission),
                )

    def list_users(self):
        with self.connect() as db:
            users = [dict(r) for r in self._execute(db, "SELECT id,username,active FROM users ORDER BY username")]
            for user in users:
                user["roles"] = [
                    r["role_name"]
                    for r in self._execute(db, "SELECT role_name FROM user_roles WHERE user_id=?", (user["id"],))
                ]
            return users

    def list_permissions(self, doc_id):
        with self.connect() as db:
            return [
                dict(r)
                for r in self._execute(
                    db, "SELECT role_name,permission FROM document_permissions WHERE document_id=?", (doc_id,)
                )
            ]
