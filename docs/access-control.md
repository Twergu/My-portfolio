# Access control and policy metadata

`RAG_AUTH_MODE=local` is an explicit single-user development bypass, bound to loopback by the supplied launcher/Compose. It is not organization authentication. `required` enables server-authenticated access and denies anonymous document/question requests. The mode is server configuration, never a client-editable setting.

## Local setup

Provision against the same `RAG_DATA_DIR` and `RAG_DATABASE_URL` as the app:

```powershell
python -m scripts.manage_access create-user admin --roles admin --token-file .secrets/admin.token
python -m scripts.manage_access create-role finance
python -m scripts.manage_access create-user alice --roles reader finance --token-file .secrets/alice.token
```

Set `RAG_AUTH_MODE=required` in `.env`, restart, then enter the token from the private file in the login screen. Tokens are random 256-bit bearer credentials; the database stores SHA-256 digests. The UI retains only an HttpOnly, SameSite=Strict cookie (Secure on HTTPS), with an eight-hour browser lifetime. API bearer tokens persist until rotation/revocation: cookie expiry is not token expiry. Keep token files private; `.secrets/` is ignored and excluded from source exports. Windows uses inherited directory ACLs; Unix files are created mode 0600. This is a portfolio authentication implementation, not SSO/MFA.

```powershell
python -m scripts.manage_access list-users
python -m scripts.manage_access grant DOCUMENT_ID finance read
python -m scripts.manage_access grant DOCUMENT_ID finance write
python -m scripts.manage_access grant DOCUMENT_ID finance revoke
python -m scripts.manage_access set-roles USER_ID reader finance
python -m scripts.manage_access disable-user USER_ID
python -m scripts.manage_access rotate-token USER_ID --token-file .secrets/alice-new.token
```

Admin can manage all documents/settings/grants; editor can upload; reader cannot upload. A role's document write grant includes read. Owners have read/write. New and migrated documents have **no automatic shared grants**; administrators can assign grants in the document information panel. Existing unowned documents are initially admin-only in required mode. Role membership/grant changes are read on each request, so revocation applies to subsequent requests. An already-running request uses its resolved authorization scope.

In Compose, use `docker compose exec app python -m scripts.manage_access ... --token-file /app/data/admin.token` to provision in the application container. Copy that private file with `docker compose cp app:/app/data/admin.token .secrets/admin.token`, then enable `RAG_AUTH_MODE=required` and recreate the app container. Database, files and identity/grant tables persist in existing volumes. Real external deployment needs HTTPS and an organization identity provider; no public-port exposure is enabled by this change.

## Retrieval and file boundaries

The server resolves authenticated principal → role/owner grants → requested document IDs → metadata predicates → explicit allowed IDs **before** query Embedding, dense search, full-text search, reranking, generation or verification. Each search SQL applies the IDs before ranking/limiting. `None` means unrestricted internal scope; `[]` means deny all, never unrestricted. An empty UI selection means all *authorized* documents and is resolved on the server.

Document listing, raw PDFs, chunks, retry, delete, metadata changes, reindexing, model settings, cost metrics and permissions have corresponding authorization checks. Client-supplied user IDs are ignored. A forbidden guessed document returns 404. Duplicate uploads cannot disclose inaccessible document IDs. `/api/health` exposes only health and storage backend in required mode. Cross-origin writes are rejected.

The HTTP authorization tests run against SQLite and real PostgreSQL in CI, including spies asserting that forbidden or empty scopes never reach external models. Search storage contracts separately test read/write grants, owners, token rotation, disabled users and policy filters on both backends.

## Metadata API

`status` already tracks indexing (`queued`, `ready`, etc.), so document policy status uses the separate field `policy_status`:

```json
{"policy_status":"current","effective_from":"2026-04-01","effective_to":"2027-03-31","department":"Finance","document_version":"TR-2026.2"}
```

Update via `PUT /api/documents/{id}/metadata` or the document information form. Dates are validated ISO dates, inclusive at both ends. `effective_to=null` means open-ended. Metadata is operator-authored; the app does not guess an effective date or classify uploaded PDFs as current.

```json
{"question":"What is the travel allowance?","document_ids":[],"filters":{"policy_status":["current"],"as_of":"2026-09-15","department":"Finance"}}
```

`POST /api/chat` applies these filters before search. Date-scoped searches exclude unknown start dates; department is exact-match. Leave a filter empty to include all authorized statuses/departments, which is necessary for historical or cross-version questions. A status labeled current is not itself proof of an effective interval. The document pipeline preserves metadata when reindexing.
