"""Real store/tool/HTTP contracts; model outputs are controlled, with no network."""

import json
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import date

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.agent import AgentContext, AgentRunner
from backend.agent_service import AgentReply, AgentService
from backend.agent_tools import (
    CalculatorArguments,
    CalendarArguments,
    CalendarConfig,
    calculator_result,
    calendar_result,
)
from backend.config import Settings
from backend.main import create_app

POLICY = "Office supplies require a budget and manager confirmation. The purchasing limit is 5000 JPY."


def action(kind, **values):
    return {"intent": "business_task", "goal": "Check applicable rules", "action": {"type": kind, **values}}


def search():
    return action("call_tool", tool="knowledge_search", arguments={"query": "office supplies policy"})


def ready(*ids):
    return action("prepare_answer", observation_ids=list(ids))


def clarify():
    return action("clarify", questions=["What is the total amount?"])


class Models:
    def __init__(self, decisions=()):
        self.decisions = list(decisions)
        self.calls = []
        self.supported = True
        self.bad_quote = False
        self.hook = None
        self.generation_override = None

    def close(self):
        pass

    def embed(self, texts, settings, key, metrics=None):
        self.calls.append(("embedding", texts))
        return [[1.0, 0.0] for text in texts]

    def chat_json(self, settings, key, messages, metrics=None, **options):
        self.calls.append(("planner", messages))
        if self.hook:
            self.hook()
        return self.decisions.pop(0)

    def chat(self, settings, key, messages, metrics=None, **options):
        payload = json.loads(messages[-1]["content"])
        role = options.get("role", "generator")
        self.calls.append((role, messages))
        if role == "verifier":
            assert settings.verification_mode == "strict" and settings.verification_strategy == "all"
            return json.dumps(
                {
                    "verdicts": [
                        {
                            "claim_index": claim["claim_index"],
                            "supported": self.supported,
                            "reason": "Controlled test verdict",
                        }
                        for claim in payload["claims"]
                    ]
                }
            )
        if self.generation_override:
            return json.dumps(self.generation_override)
        sources = [source for source in payload["sources"] if source.get("kind") != "user"]
        return json.dumps(
            {
                "status": "answered",
                "claims": [
                    {
                        "text": source.get("metadata", {}).get("standalone_text") or source["text"],
                        "evidence": [
                            {
                                "source_id": source["id"],
                                "quote": "Not an original quote" if self.bad_quote else source["text"],
                            }
                        ],
                    }
                    for source in sources
                ],
            }
        )


def seed(store, config, doc_id="visible"):
    store.register_document(
        {
            "id": doc_id,
            "name": doc_id + ".pdf",
            "sha256": doc_id,
            "size": 1,
            "status": "queued",
            "created_at": "2026-10-04",
        }
    )
    store.commit_chunks(
        doc_id,
        [{"page": 2, "ordinal": 0, "text": POLICY if doc_id == "visible" else "CONFIDENTIAL_OTHER_ROLE"}],
        [[1.0, 0.0]],
        config.profile,
    )
    store.set_metadata(doc_id, {"policy_status": "current", "effective_from": "2026-01-01"})


@pytest.fixture
def api(store, monkeypatch):
    monkeypatch.setenv("RAG_AUTH_MODE", "required")
    monkeypatch.setattr("backend.main.create_store", lambda *args, **kwargs: store)
    models = Models()
    app = create_app(store.folder, database_url="", provider=models)
    config = Settings(mode="api", retrieval_mode="hybrid", min_score=0, verification_mode="fast")
    app.state.knowledge.settings = config
    store = app.state.knowledge.store
    seed(store, config)
    seed(store, config, "secret")
    store.grant_document("visible", "reader", "read")
    _, token = store.provision_user("alice", ["reader"])
    _, bob = store.provision_user("bob", ["reader"])
    with TestClient(app) as client:
        client.headers["Authorization"] = "Bearer " + token
        yield client, app, models, bob


def test_agent_reuses_retrieval_and_validates_document_and_calculation_sources(api):
    client, app, models, _ = api
    models.decisions = [
        search(),
        action("call_tool", tool="calculator", arguments={"operation": "multiply", "operands": ["1200", "3"]}),
        ready("tool_1", "tool_2"),
    ]
    result = client.post(
        "/api/agent", json={"question": "Check purchasing 3 notebooks at 1200 JPY each", "language": "en"}
    )
    assert result.status_code == 200
    data = result.json()
    assert data["status"] == "answered" and data["support"]["all_supported"] is True
    assert data["support"]["verification_mode"] == "strict"
    assert [role for role, _ in models.calls] == ["planner", "embedding", "planner", "planner", "generator", "verifier"]
    assert {s["kind"] for s in data["sources"]} == {"document", "tool"}
    document = next(s for s in data["sources"] if s["kind"] == "document")
    assert document["url"] == "/api/documents/visible/file#page=2"
    tool = next(s for s in data["sources"] if s["kind"] == "tool")
    assert tool["url"] is None and tool["metadata"]["result"]["result"] == "3600"
    assert "CONFIDENTIAL_OTHER_ROLE" not in json.dumps(models.calls)
    assert not app.state.agent.tasks and data["evidence_notices"]["actions_executed"] is False
    assert app.state.knowledge.measurements[-1]["operation"] == "agent"


@pytest.mark.parametrize("bad_quote,supported", [(True, True), (False, False)])
def test_agent_withholds_ungrounded_answers(api, bad_quote, supported):
    client, _, models, _ = api
    models.decisions = [search(), ready("tool_1")]
    models.bad_quote, models.supported = bad_quote, supported
    data = client.post("/api/agent", json={"question": "Check supplies policy"}).json()
    assert data["status"] == "unsupported_answer" and data["sources"] == [] and data["claims"] == []
    assert ("verifier" in [role for role, _ in models.calls]) == (not bad_quote)


def test_generator_can_clarify_when_planner_hands_off_too_early(api):
    client, app, models, _ = api
    models.decisions = [search(), ready("tool_1"), ready("tool_1")]
    models.generation_override = {"status": "needs_input", "claims": [], "questions": ["What is the total amount?"]}
    first = client.post("/api/agent", json={"question": "Does my purchase comply?"}).json()
    assert first["status"] == "needs_input" and first["task_id"]
    assert first["sources"] == [] and first["claims"] == []
    assert "verifier" not in [role for role, _ in models.calls]
    assert first["trace"][-1]["event"] == "answer_clarification"
    models.generation_override = None
    final = client.post(f"/api/agent/{first['task_id']}/reply", json={"question": "The total is 1000 JPY"}).json()
    assert final["status"] == "answered" and not app.state.agent.tasks


def test_clarification_cannot_smuggle_unverified_answer_claims(api):
    client, _, models, _ = api
    models.decisions = [search(), ready("tool_1")]
    models.generation_override = {
        "status": "needs_input",
        "claims": [{"text": "Approved", "evidence": [{"source_id": 1, "quote": POLICY}]}],
        "questions": ["Your name?"],
    }
    data = client.post("/api/agent", json={"question": "Check"}).json()
    assert data["status"] == "invalid_model_response" and not data["claims"]


def test_no_acl_scope_or_filtered_evidence_means_no_model_call(api):
    client, app, models, _ = api
    assert client.post("/api/agent", json={"question": "Policy", "document_ids": ["secret"]}).status_code == 404
    assert (
        client.post("/api/agent", json={"question": "Policy", "filters": {"department": "none"}}).json()["failure_code"]
        == "no_accessible_evidence"
    )
    app.state.knowledge.store.grant_document("visible", "reader", None)
    assert client.post("/api/agent", json={"question": "Policy"}).json()["failure_code"] == "no_accessible_evidence"
    assert not models.calls


def test_server_state_resume_and_cross_user_isolation(api):
    client, app, models, bob = api
    models.decisions = [search(), clarify(), ready("tool_1")]
    first = client.post("/api/agent", json={"question": "Can I buy these supplies?"}).json()
    task_id = first["task_id"]
    assert first["status"] == "needs_input"
    other = client.post(
        f"/api/agent/{task_id}/reply", json={"question": "1000 JPY"}, headers={"Authorization": "Bearer " + bob}
    )
    assert other.status_code == 404
    reply = client.post(f"/api/agent/{task_id}/reply", json={"question": "1000 JPY"})
    assert reply.status_code == 200 and reply.json()["status"] == "answered"
    assert "1000 JPY" in json.dumps(models.calls[-2])
    assert not app.state.agent.tasks
    assert client.post(f"/api/agent/{task_id}/reply", json={"question": "Again"}).status_code == 404


@pytest.mark.parametrize("change", ["permission", "metadata", "settings", "reindex"])
def test_task_invalidates_when_scope_or_evidence_changes(api, change):
    client, app, models, _ = api
    models.decisions = [search(), clarify()]
    task_id = client.post("/api/agent", json={"question": "Check policy"}).json()["task_id"]
    store = app.state.knowledge.store
    count = len(models.calls)
    if change == "permission":
        store.grant_document("visible", "reader", None)
    elif change == "metadata":
        store.set_metadata("visible", {"policy_status": "archived"})
    elif change == "settings":
        app.state.knowledge.settings.chat_model = "other-model"
    else:
        store.commit_chunks(
            "visible", [{"page": 2, "ordinal": 0, "text": POLICY}], [[1.0, 0.0]], app.state.knowledge.settings.profile
        )
    response = client.post(f"/api/agent/{task_id}/reply", json={"question": "1000 JPY"})
    assert response.status_code == 409 and len(models.calls) == count
    assert not app.state.agent.tasks


@pytest.mark.parametrize("handoff", [False, True])
def test_midflight_revocation_stops_before_embedding_and_hides_all_results(api, handoff):
    client, app, models, _ = api
    decision = search()
    decision["action"]["answer_after"] = handoff
    models.decisions = [decision]
    models.hook = lambda: app.state.knowledge.store.grant_document("visible", "reader", None)
    response = client.post("/api/agent", json={"question": "Policy"})
    assert response.status_code == 409 and [role for role, _ in models.calls] == ["planner"]
    assert "sources" not in response.json()


def test_first_turn_reindex_is_detected_before_next_planner_receives_old_evidence(api, monkeypatch):
    client, app, models, _ = api
    models.decisions = [search(), ready("tool_1")]
    original = AgentRunner._messages

    def reindex_between_steps(runner, state):
        if state.observations:
            app.state.knowledge.store.commit_chunks(
                "visible",
                [{"page": 2, "ordinal": 0, "text": POLICY}],
                [[1.0, 0.0]],
                app.state.knowledge.settings.profile,
            )
        return original(runner, state)

    monkeypatch.setattr(AgentRunner, "_messages", reindex_between_steps)
    response = client.post("/api/agent", json={"question": "Check policy"})
    assert response.status_code == 409
    assert [role for role, _ in models.calls] == ["planner", "embedding"]
    assert not app.state.agent.tasks


@pytest.mark.parametrize("supported", [True, False])
def test_direct_tool_handoff_still_runs_strict_verifier_and_acl(api, supported):
    client, app, models, _ = api
    final = search()
    final["action"]["answer_after"] = True
    final["intent"] = "knowledge_question"
    models.decisions, models.supported = [final], supported
    data = client.post("/api/agent", json={"question": "Purchasing policy"}).json()
    assert [role for role, _ in models.calls] == ["planner", "embedding", "generator", "verifier"]
    assert data["status"] == ("answered" if supported else "unsupported_answer")
    assert "CONFIDENTIAL_OTHER_ROLE" not in json.dumps(models.calls)
    assert not app.state.agent.tasks
    if not supported:
        assert not data["claims"] and not data["sources"]


def test_client_cannot_forge_state_or_expand_tool_scope(api):
    client, _, models, _ = api
    assert client.post("/api/agent", json={"question": "Policy", "state": {"role": "admin"}}).status_code == 422
    models.decisions = [
        action("call_tool", tool="knowledge_search", arguments={"query": "Policy", "document_ids": ["secret"]}),
        action("unavailable", reason="no_evidence"),
    ]
    data = client.post("/api/agent", json={"question": "Policy"}).json()
    assert data["status"] == "unavailable"
    assert any(step.get("code") == "invalid_arguments" for step in data["trace"])
    assert all(role != "embedding" for role, _ in models.calls)


def test_expiration_cancel_capacity_and_busy_task(api):
    client, app, models, bob = api
    agent = app.state.agent
    now = [0.0]
    agent.clock = lambda: now[0]
    agent.max_user_tasks = 1
    models.decisions = [clarify(), clarify(), clarify()]
    task_id = client.post("/api/agent", json={"question": "Check"}).json()["task_id"]
    assert client.post("/api/agent", json={"question": "Another"}).status_code == 429
    agent.tasks[task_id].busy = True
    assert client.post(f"/api/agent/{task_id}/reply", json={"question": "Reply"}).status_code == 409
    agent.tasks[task_id].busy = False
    assert client.delete(f"/api/agent/{task_id}", headers={"Authorization": "Bearer " + bob}).status_code == 404
    assert client.delete(f"/api/agent/{task_id}").json()["cancelled"]
    task_id = client.post("/api/agent", json={"question": "Check"}).json()["task_id"]
    now[0] = 901.0
    assert client.post(f"/api/agent/{task_id}/reply", json={"question": "Reply"}).status_code == 404
    assert not agent.tasks


def test_real_concurrent_resume_and_cancel_do_not_execute_twice(api):
    client, app, models, bob = api
    models.decisions = [search(), clarify(), ready("tool_1")]
    task_id = client.post("/api/agent", json={"question": "Check purchase"}).json()["task_id"]
    started, release = threading.Event(), threading.Event()

    def block_planner():
        started.set()
        assert release.wait(10), "Test did not release the worker"

    models.hook = block_planner
    app.state.agent.max_user_tasks = 1
    before = len(models.calls)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(client.post, f"/api/agent/{task_id}/reply", json={"question": "1000 JPY"})
        try:
            assert started.wait(10)
            assert client.post(f"/api/agent/{task_id}/reply", json={"question": "duplicate"}).status_code == 409
            assert client.delete(f"/api/agent/{task_id}").status_code == 409
            assert client.post("/api/agent", json={"question": "another"}).status_code == 429
            assert client.delete(f"/api/agent/{task_id}", headers={"Authorization": "Bearer " + bob}).status_code == 404
            assert len(models.calls) == before + 1  # Only the worker's planner.
        finally:
            release.set()
        assert future.result(timeout=10).json()["status"] == "answered"
    assert not app.state.agent.tasks


def test_expiry_is_absolute_not_extended_by_reply_and_cancel_matches_resume(api):
    client, app, models, _ = api
    now = [0.0]
    app.state.agent.clock = lambda: now[0]
    models.decisions = [clarify(), clarify(), clarify()]
    task_id = client.post("/api/agent", json={"question": "Check"}).json()["task_id"]
    now[0] = 800
    assert (
        client.post(f"/api/agent/{task_id}/reply", json={"question": "Still missing amount"}).json()["status"]
        == "needs_input"
    )
    assert app.state.agent.tasks[task_id].expires == 900
    now[0] = 900
    assert client.delete(f"/api/agent/{task_id}").status_code == 404
    assert client.post(f"/api/agent/{task_id}/reply", json={"question": "1000"}).status_code == 404
    assert not app.state.agent.tasks


def test_slow_clarification_cannot_return_an_already_expired_task_handle(api):
    client, app, models, _ = api
    now = [0.0]
    app.state.agent.clock = lambda: now[0]
    models.decisions = [clarify()]
    models.hook = lambda: now.__setitem__(0, 901)
    result = client.post("/api/agent", json={"question": "Check", "language": "ja"}).json()
    assert result["status"] == "limit_reached" and result["failure_code"] == "task_expired"
    assert result["task_id"] is None and not result["questions"] and not app.state.agent.tasks
    assert app.state.knowledge.measurements[-1]["status"] == "limit_reached"


def test_process_restart_loses_only_ephemeral_task_not_document(api):
    client, app, models, _ = api
    models.decisions = [clarify()]
    task_id = client.post("/api/agent", json={"question": "Check"}).json()["task_id"]
    old = app.state.agent
    principal = app.state.knowledge.store.authenticate(client.headers["Authorization"].removeprefix("Bearer "))
    restarted = AgentService(app.state.knowledge)
    with pytest.raises(HTTPException) as error:
        restarted.run(AgentReply(question="1000"), lambda: principal, task_id=task_id)
    assert error.value.status_code == 404 and not restarted.tasks
    assert old.tasks[task_id].owner == principal.id
    assert app.state.knowledge.store.document("visible")["status"] == "ready"


def test_exception_releases_slot_and_global_capacity_applies_to_all_users(api):
    client, app, models, bob = api
    app.state.agent.max_tasks = 1
    models.decisions = [clarify(), clarify()]
    task_id = client.post("/api/agent", json={"question": "Check"}).json()["task_id"]
    assert (
        client.post("/api/agent", json={"question": "Bob task"}, headers={"Authorization": "Bearer " + bob}).status_code
        == 429
    )
    assert client.delete(f"/api/agent/{task_id}").status_code == 200

    def broken():
        raise RuntimeError("controlled unexpected failure")

    models.hook = broken
    with pytest.raises(RuntimeError, match="controlled unexpected"):
        client.post("/api/agent", json={"question": "Check"})
    assert not app.state.agent.tasks and app.state.knowledge.measurements[-1]["status"] == "error"
    models.hook = None
    assert client.post("/api/agent", json={"question": "After failure"}).json()["status"] == "needs_input"


@pytest.mark.parametrize(
    "operation,operands,expected",
    [
        ("sum", ["0.1", "0.2"], "0.3"),
        ("multiply", ["14500", "3"], "43500"),
        ("divide", ["1", "3"], "0.333333"),
        ("subtract", ["5", "7"], "-2"),
        ("percent_of", ["15", "200"], "30"),
    ],
)
def test_decimal_math_is_deterministic(operation, operands, expected):
    result = calculator_result(CalculatorArguments(operation=operation, operands=operands))
    assert result.data["result"] == expected and result.provenance == "calculated"
    assert result.data["rounded"] == (operation == "divide")


@pytest.mark.parametrize("operands", [["1", "0"], ["1+2", "2"], [1, 2], ["NaN", "2"], ["1e30", "2"]])
def test_calculator_rejects_expressions_coercion_and_divide_by_zero(operands):
    with pytest.raises(ValidationError):
        CalculatorArguments(operation="divide", operands=operands)


def test_calendar_relative_dates_leap_year_and_explicit_mock_holidays():
    ctx = AgentContext("alice", "scope", date(2026, 10, 4), "Asia/Tokyo", "ja")
    next_monday = calendar_result(CalendarArguments(operation="next_weekday"), ctx, CalendarConfig())
    assert next_monday.data["date"] == "2026-10-05"
    leap = calendar_result(
        CalendarArguments(operation="date_offset", start_date="2024-02-28", offset_days=1), ctx, CalendarConfig()
    )
    assert leap.data["date"] == "2024-02-29"
    result = calendar_result(
        CalendarArguments(operation="date_range", start_date="2026-10-02", end_date="2026-10-06"),
        ctx,
        CalendarConfig(name="Test fixture", holidays=(date(2026, 10, 5),)),
    )
    assert result.data["calendar_days"] == 5 and result.data["working_days"] == 2
    assert result.provenance == "mock" and "mock" in result.data["text"]


@pytest.mark.parametrize(
    "args",
    [
        {"operation": "date_range"},
        {"operation": "date_offset", "start_date": "2026-02-30"},
        {"operation": "next_weekday", "weekday": True},
        {"operation": "date_range", "end_date": "2026-10-10", "offset_days": 5},
    ],
)
def test_calendar_rejects_invalid_dates_and_ignored_arguments(args):
    with pytest.raises(ValidationError):
        CalendarArguments(**args)


def test_agent_store_acl_contract(store, monkeypatch):
    monkeypatch.setattr("backend.main.create_store", lambda *args, **kwargs: store)
    monkeypatch.setenv("RAG_AUTH_MODE", "required")
    models = Models([search(), ready("tool_1")])
    app = create_app(store.folder, database_url="", provider=models)
    config = Settings(mode="api", retrieval_mode="hybrid", min_score=0)
    app.state.knowledge.settings = config
    seed(store, config)
    seed(store, config, "secret")
    _, token = store.provision_user("reader", ["reader"])
    store.grant_document("visible", "reader", "read")
    with TestClient(app) as client:
        assert client.post("/api/agent", json={"question": "Policy"}).status_code == 401
        client.headers["Authorization"] = "Bearer " + token
        data = client.post("/api/agent", json={"question": "Policy"}).json()
    assert data["status"] == "answered"
    assert {s["document_id"] for s in data["sources"]} == {"visible"}
    assert "CONFIDENTIAL_OTHER_ROLE" not in json.dumps(models.calls)
