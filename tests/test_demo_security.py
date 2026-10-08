"""Local security/transport contracts; no paid API calls or claimed model quality."""

import json
from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest
from fastapi.testclient import TestClient

from backend.config import Settings
from backend.demo_security import DemoGuard, DemoLimit, DemoProvider, allowed_hosts
from backend.main import create_app
from backend.providers import ModelError
from scripts.prepare_demo import seed


def test_demo_rejects_auth_bypass_and_weakened_verification(tmp_path, monkeypatch):
    monkeypatch.setenv("RAG_DEMO_MODE", "1")
    with pytest.raises(ValueError, match="AUTH_MODE"):
        create_app(tmp_path, database_url="")
    monkeypatch.setenv("RAG_AUTH_MODE", "required")
    monkeypatch.setenv("RAG_VERIFICATION_MODE", "fast")
    with pytest.raises(ValueError, match="strict"):
        create_app(tmp_path, database_url="")


def test_fictional_seed_is_idempotent_and_grants_only_demo_role(store, monkeypatch):
    monkeypatch.setattr("backend.main.create_store", lambda *a, **kw: store)
    app = create_app(store.folder, database_url="")
    service = app.state.knowledge
    try:
        first = seed(service)
        assert seed(service)["document_id"] == first["document_id"]
        assert len(store.all_documents()) == 1
        _, token = store.provision_user("demo", ["demo-reviewer"])
        _, outsider = store.provision_user("outsider", ["reader"])
        assert store.allowed_document_ids(store.authenticate(token)) == [first["document_id"]]
        assert store.allowed_document_ids(store.authenticate(outsider)) == []
        assert service.documents()[0]["policy_status"] == "current"
        assert service.documents()[0]["pages"] == 8
    finally:
        service.close()


@pytest.mark.parametrize("hosts", ["*", "*.example.org", "", "https://demo.example.org", "demo.example.org:443"])
def test_hosts_are_explicit(monkeypatch, hosts):
    monkeypatch.setenv("RAG_ALLOWED_HOSTS", hosts)
    with pytest.raises(ValueError):
        allowed_hosts()


def test_demo_acl_readonly_https_and_request_limits(store, monkeypatch):
    monkeypatch.setenv("RAG_DEMO_MODE", "1")
    monkeypatch.setenv("RAG_AUTH_MODE", "required")
    monkeypatch.setenv("RAG_ALLOWED_HOSTS", "demo.example.org,localhost")
    monkeypatch.setenv("RAG_DEMO_USER_DAILY", "2")
    monkeypatch.setattr("backend.main.create_store", lambda *a, **kw: store)
    app = create_app(store.folder, database_url="")
    with TestClient(app, base_url="https://demo.example.org") as client:
        _, token = store.provision_user("reviewer", ["reader"])
        _, admin_token = store.provision_user("owner", ["admin"])
        assert client.get("/api/documents").status_code == 401
        assert client.get("https://untrusted.example.org/api/health").status_code == 400
        assert client.get("http://demo.example.org/api/health").status_code == 200
        assert client.get("http://demo.example.org/", headers={"X-Forwarded-Proto": "https"}).status_code == 400
        response = client.post("/api/auth/login", json={"token": token})
        assert response.status_code == 200
        assert all(word in response.headers["set-cookie"].lower() for word in ("secure", "httponly", "samesite=strict"))
        assert client.get("/api/auth/status").json()["demo"] is True
        assert client.get("/api/documents").json()["documents"] == []
        assert client.get("/api/documents/secret/file").status_code == 404
        assert client.post("/api/chat", json={"question": "secret", "document_ids": ["secret"]}).status_code == 404
        # Reply shares the same per-user allowance; nonexistent task is still a request.
        assert client.post("/api/agent/missing/reply", json={"reply": "test"}).status_code != 429
        assert client.post("/api/chat", json={"question": "test"}).status_code == 429
        assert client.post("/api/auth/logout", headers={"Origin": "https://evil.example.org"}).status_code == 403
        client.headers["Authorization"] = "Bearer " + admin_token
        for method, path in [
            ("POST", "/api/documents/sample"),
            ("PUT", "/api/settings"),
            ("DELETE", "/api/documents/a"),
            ("GET", "/api/admin/users"),
            ("POST", "/api/settings/test"),
        ]:
            assert client.request(method, path, json={}).status_code == 403
        assert client.post("/api/chat", content=b"x" * 65537).status_code == 413


def test_quota_restart_utc_rollover_and_release(tmp_path, monkeypatch):
    monkeypatch.setenv("RAG_DEMO_USER_DAILY", "1")
    now = [86400.0]
    guard = DemoGuard(tmp_path, clock=lambda: now[0])
    with pytest.raises(RuntimeError), guard.slot("user", "ip"):
        raise RuntimeError("handler failed")
    assert not guard.active
    restarted = DemoGuard(tmp_path, clock=lambda: now[0])
    with pytest.raises(DemoLimit), restarted.slot("user", "ip"):
        pass
    now[0] += 86400
    with restarted.slot("user", "ip"):
        with pytest.raises(DemoLimit, match="busy"), restarted.slot("user", "other ip"):
            pass
        with restarted.slot("another user", "ip"):
            with pytest.raises(DemoLimit, match="busy"), restarted.slot("third", "ip"):
                pass
    assert not restarted.active


def test_shared_ip_global_and_login_limits(tmp_path, monkeypatch):
    monkeypatch.setenv("RAG_DEMO_IP_MINUTE", "1")
    guard = DemoGuard(tmp_path)
    with guard.slot("a", "same"):
        pass
    with pytest.raises(DemoLimit), guard.slot("b", "same"):
        pass
    for _ in range(10):
        guard.login_attempt("same")
    with pytest.raises(DemoLimit):
        guard.login_attempt("same")
    guard.global_daily = 1
    with pytest.raises(DemoLimit), guard.slot("c", "different"):
        pass


def test_budget_atomic_restart_unknown_usage_and_excess(tmp_path, monkeypatch):
    monkeypatch.setenv("RAG_DEMO_DAILY_USD", "0.1")
    guard = DemoGuard(tmp_path)

    def reserve(_):
        try:
            return guard.reserve(0.06)
        except ModelError:
            return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        attempts = list(pool.map(reserve, range(2)))
    assert sum(a is not None for a in attempts) == 1
    day = next(a for a in attempts if a)
    guard.settle(day, 0.06, None)
    restarted = DemoGuard(tmp_path)
    with pytest.raises(ModelError, match="budget"):
        restarted.reserve(0.06)
    restarted.settle(day, 0.06, 0.001)
    restarted.reserve(0.06)
    restarted.settle(day, 0.06, 0.07)
    with pytest.raises(ModelError, match="budget"):
        restarted.reserve(0.001)


@pytest.fixture
def priced_guard(tmp_path, monkeypatch):
    for name in ("CHAT_INPUT", "CHAT_OUTPUT", "VERIFIER_INPUT", "VERIFIER_OUTPUT", "EMBEDDING"):
        monkeypatch.setenv("RAG_" + name + "_USD_PER_MILLION_TOKENS", "1")
    return DemoGuard(tmp_path)


def test_provider_caps_and_charges_all_roles(priced_guard):
    calls = []

    def respond(request):
        calls.append(json.loads(request.content))
        return httpx.Response(200, json={"usage": {"prompt_tokens": 12, "completion_tokens": 5}})

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        provider = DemoProvider(priced_guard, client)
        for role, group in [("planner", "chat"), ("generator", "chat"), ("verifier", "verifier")]:
            provider.request(
                Settings(),
                "test",
                "/chat/completions",
                {"model": "test", "max_tokens": 99999},
                role=role,
                price_group=group,
            )
    assert len(calls) == 3 and all(c["max_completion_tokens"] == 4096 and "max_tokens" not in c for c in calls)
    with priced_guard.connect() as db:
        assert db.execute("SELECT reserved FROM spend").fetchone()[0] == pytest.approx(51 / 1_000_000)


@pytest.mark.parametrize("failure", ["missing_price", "oversized", "budget"])
def test_reject_before_http(priced_guard, monkeypatch, failure):
    payload = {"model": "test", "messages": []}
    if failure == "missing_price":
        monkeypatch.delenv("RAG_CHAT_INPUT_USD_PER_MILLION_TOKENS")
    elif failure == "oversized":
        payload["messages"] = ["x" * 60001]
    else:
        priced_guard.reserve(priced_guard.budget)

    def forbidden(request):
        raise AssertionError("Must not call API")

    with httpx.Client(transport=httpx.MockTransport(forbidden)) as client:
        with pytest.raises(ModelError):
            DemoProvider(priced_guard, client).request(Settings(), "test", "/chat/completions", payload)


@pytest.mark.parametrize("result", [None, "invalid", "timeout"])
def test_unknown_usage_retains_reservation_without_retry(priced_guard, result):
    calls = []

    def respond(request):
        calls.append(1)
        if result == "timeout":
            raise httpx.ReadTimeout("unknown billing", request=request)
        return httpx.Response(200, json={"usage": result})

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        provider = DemoProvider(priced_guard, client)
        if result == "timeout":
            with pytest.raises(ModelError):
                provider.request(Settings(), "test", "/embeddings", {"input": ["sample"]})
        else:
            provider.request(Settings(), "test", "/embeddings", {"input": ["sample"]})
    assert len(calls) == 1
    with priced_guard.connect() as db:
        assert db.execute("SELECT reserved FROM spend").fetchone()[0] > 0
