"""Authenticated Agent API, short-lived server-owned tasks and grounded answers."""

import hashlib
import json
import secrets
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from .agent import AgentContext, AgentLimits, AgentRunner, AgentState, ProviderPlanner, Text, TraceEvent
from .agent_grounding import standalone_tool_text
from .agent_tools import CalendarConfig, build_tools
from .governance import RetrievalFilters
from .rag import answer_from_sources, answer_language
from .telemetry import Metrics


class AgentQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: Text
    document_ids: list[str] = Field(default_factory=list, max_length=100)
    filters: RetrievalFilters = Field(default_factory=RetrievalFilters)
    language: Literal["zh", "ja", "en"] | None = None


class AgentReply(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: Text


class GuardedProvider:
    """Check fresh identity/scope before each model operation; reuse shared transport."""

    def __init__(self, provider, guard):
        self.provider, self.guard = provider, guard

    def chat(self, *args, **kwargs):
        self.guard()
        return self.provider.chat(*args, **kwargs)

    def chat_json(self, *args, **kwargs):
        self.guard()
        return self.provider.chat_json(*args, **kwargs)

    def embed(self, *args, **kwargs):
        self.guard()
        return self.provider.embed(*args, **kwargs)


@dataclass
class PendingTask:
    owner: str
    request: AgentQuestion
    expires: float
    state: AgentState | None = None
    busy: bool = True


def evidence_sources(state):
    """Keep PDF citations distinct from computed facts and self-reported inputs."""
    sources, seen = [], set()
    for observation in state.observations:
        if observation.id not in state.selected_observation_ids or observation.status != "ok":
            continue
        output = observation.output
        if observation.tool == "knowledge_search":
            for source in output.data["sources"]:
                if source["chunk_id"] not in seen:
                    seen.add(source["chunk_id"])
                    sources.append(dict(source))
        elif output.data.get("text"):
            sources.append(
                {
                    "kind": "tool",
                    "provenance": output.provenance,
                    "name": observation.tool,
                    "page": None,
                    "url": None,
                    "text": output.data["text"],
                    "metadata": {
                        "observation_id": observation.id,
                        "arguments": observation.arguments,
                        "result": output.data,
                    },
                }
            )
    # User statements alone cannot make a task answerable.
    if not sources:
        return []
    for index, turn in enumerate(state.turns, 1):
        sources.append(
            {
                "kind": "user",
                "provenance": "self_report",
                "name": f"User input {index}",
                "page": None,
                "url": None,
                "text": turn.text,
                "metadata": {
                    "responding_to": turn.responding_to,
                    "reference_date": state.context.reference_date.isoformat(),
                    "timezone": state.context.timezone,
                },
            }
        )
    for source in sources:
        if source.get("kind") == "tool":
            source["metadata"]["standalone_text"] = standalone_tool_text(source, state.context.language)
    return [source | {"number": index} for index, source in enumerate(sources, 1)]


class AgentService:
    def __init__(self, knowledge, *, clock=time.monotonic, calendar=None):
        self.knowledge = knowledge
        self.clock = clock
        self.calendar = calendar or CalendarConfig()
        self.tasks = {}
        self.lock = threading.Lock()
        self.ttl_seconds = 900
        self.max_tasks = 100
        self.max_user_tasks = 4

    def _acquire(self, principal, question, task_id):
        with self.lock:
            self.tasks = {key: task for key, task in self.tasks.items() if task.busy or task.expires > self.clock()}
            if task_id:
                task = self.tasks.get(task_id)
                if task is None or task.owner != principal.id:
                    raise HTTPException(404, "Task not found or expired")
                if task.busy:
                    raise HTTPException(409, "Task is already running")
                task.busy = True
                return task_id, task
            if (
                len(self.tasks) >= self.max_tasks
                or sum(t.owner == principal.id for t in self.tasks.values()) >= self.max_user_tasks
            ):
                raise HTTPException(429, "Too many active tasks; finish or cancel an existing task")
            task_id = secrets.token_urlsafe(24)
            task = PendingTask(principal.id, question, self.clock() + self.ttl_seconds)
            self.tasks[task_id] = task
            return task_id, task

    def cancel(self, task_id, principal):
        with self.lock:
            task = self.tasks.get(task_id)
            if task is None or task.owner != principal.id:
                raise HTTPException(404, "Task not found")
            if not task.busy and task.expires <= self.clock():
                del self.tasks[task_id]
                raise HTTPException(404, "Task not found or expired")
            if task.busy:
                raise HTTPException(409, "Wait for the current operation before cancelling")
            del self.tasks[task_id]
        return {"cancelled": True}

    def _scope(self, principal, question, config, key):
        store = self.knowledge.store
        requested = question.document_ids or None
        allowed = store.allowed_document_ids(principal, requested, question.filters)
        if requested and not set(requested) <= set(store.allowed_document_ids(principal, requested)):
            raise HTTPException(404, "Document not found")
        documents = [store.document(doc_id) for doc_id in allowed]
        if any(doc is None for doc in documents):
            raise HTTPException(409, "Documents changed; start a new task")
        if requested and any(doc["status"] != "ready" or doc["profile"] != config.profile for doc in documents):
            raise HTTPException(409, "Selected documents need indexing")
        identity = {
            "principal": principal.model_dump(),
            "request": question.model_dump(mode="json", exclude={"question"}),
            "settings": config.model_dump(),
            "credential_revision": hashlib.sha256(key.encode()).hexdigest(),
            "documents": documents,
            "calendar": repr(self.calendar),
        }
        revision = hashlib.sha256(json.dumps(identity, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        return allowed, revision

    def run(self, question, principal_loader, *, task_id=None):
        principal = principal_loader()
        if principal is None:
            raise HTTPException(401, "Authentication required")
        task_id, task = self._acquire(principal, question, task_id)
        metrics, outcome, keep = Metrics(), "error", False
        try:
            config, key = self.knowledge.snapshot()
            allowed, revision = self._scope(principal, task.request, config, key)
            if task.state is not None and revision != task.state.context.scope_revision:
                raise HTTPException(409, "Permissions, documents or configuration changed; start a new task")

            def guard():
                current = principal_loader()
                if current is None or current.id != task.owner:
                    raise HTTPException(401, "Authentication changed")
                fresh_config, fresh_key = self.knowledge.snapshot()
                if self._scope(current, task.request, fresh_config, fresh_key)[1] != revision:
                    raise HTTPException(409, "Permissions, documents or configuration changed; start a new task")
                # Reindexing the same file can replace chunk IDs without changing its digest.
                if task.state is not None:
                    by_document = {}
                    for obs in task.state.observations:
                        if obs.status == "ok" and obs.tool == "knowledge_search":
                            for source in obs.output.data["sources"]:
                                doc_id = source["document_id"]
                                if doc_id not in by_document:
                                    by_document[doc_id] = {
                                        c["id"]: c["text"] for c in self.knowledge.store.get_chunks(doc_id)
                                    }
                                if by_document[doc_id].get(source["chunk_id"]) != source["text"]:
                                    raise HTTPException(409, "Evidence changed; start a new task")

            if not self.knowledge.store.has_searchable(config.profile, allowed):
                outcome = "unavailable"
                return {
                    "status": outcome,
                    "failure_code": "no_accessible_evidence",
                    "task_id": None,
                    "questions": [],
                    "sources": [],
                    "trace": [],
                    "metrics": metrics.as_dict(),
                }
            now = datetime.now(timezone(timedelta(hours=9)))
            context = (
                task.state.context
                if task.state
                else AgentContext(
                    principal.id,
                    revision,
                    now.date(),
                    "Asia/Tokyo",
                    answer_language(question.question, task.request.language),
                )
            )
            provider = GuardedProvider(self.knowledge.provider, guard)
            runner = AgentRunner(
                ProviderPlanner(provider, config, key),
                build_tools(self.knowledge.store, config, key, provider, allowed, guard, calendar=self.calendar),
                limits=AgentLimits(max_context_chars=80000, max_tool_output_chars=20000),
            )
            state = (
                runner.resume(task.state, question.question, context, metrics)
                if task.state
                else runner.start(
                    question.question, context, metrics, on_state=lambda state: setattr(task, "state", state)
                )
            )
            task.state = state
            guard()
            response = {
                "status": state.status,
                "task_id": task_id if state.status == "needs_input" else None,
                "intent": state.intent,
                "goal": state.goal,
                "questions": state.questions,
                "failure_code": state.failure_code,
                "trace": [event.model_dump() for event in state.trace],
                "sources": [],
                "reference_date": context.reference_date.isoformat(),
                "timezone": context.timezone,
            }
            if state.status == "ready":
                sources = evidence_sources(state)
                user_task = json.dumps([turn.model_dump() for turn in state.turns], ensure_ascii=False)
                if len(json.dumps(sources, ensure_ascii=False)) + len(user_task) > 80000:
                    response.update(status="limit_reached", failure_code="evidence_context_limit")
                else:
                    result = answer_from_sources(
                        user_task,
                        config,
                        key,
                        sources,
                        context.language,
                        provider,
                        metrics,
                        agent_mode=True,
                        policy_as_of=task.request.filters.as_of or context.reference_date,
                        historical_policy=task.request.filters.as_of is not None,
                    )
                    response.update(result)
                    if result["status"] == "needs_input":
                        state.status, state.questions = "needs_input", result["questions"]
                        state.trace.append(TraceEvent(step=state.steps, event="answer_clarification"))
                        response.update(task_id=task_id, trace=[event.model_dump() for event in state.trace])
                    # Every statement in the rendered answer has passed quote and semantic checks.
                    response["evidence_notices"] = {
                        "uses_mock_data": any(s.get("provenance") == "mock" for s in result["sources"]),
                        "uses_self_report": any(s.get("provenance") == "self_report" for s in result["sources"]),
                        "actions_executed": False,
                    }
            guard()
            if response["status"] == "needs_input" and task.expires <= self.clock():
                # A slow request must not advertise a handle that cannot resume.
                state.status, state.questions, state.failure_code = "limit_reached", [], "task_expired"
                state.trace.append(TraceEvent(step=state.steps, event="limit_reached", code="task_expired"))
                response.update(
                    status="limit_reached",
                    failure_code="task_expired",
                    task_id=None,
                    questions=[],
                    trace=[event.model_dump() for event in state.trace],
                    answer={
                        "zh": "任务已过期，请重新开始。",
                        "ja": "タスクの有効期限が切れました。新しく開始してください。",
                        "en": "This task expired. Start a new task.",
                    }[context.language],
                )
            outcome = response["status"]
            keep = outcome == "needs_input"
            response["metrics"] = metrics.as_dict()
            response["elapsed_ms"] = response["metrics"]["elapsed_ms"]
            return response
        finally:
            with self.lock:
                if keep:
                    task.busy = False
                else:
                    self.tasks.pop(task_id, None)
            self.knowledge.record_metrics("agent", outcome, metrics.as_dict())


def install_agent_routes(app, knowledge, identify):
    service = AgentService(knowledge)
    app.state.agent = service

    @app.post("/api/agent")
    def start_agent(question: AgentQuestion, request: Request):
        return service.run(question, lambda: identify(request))

    @app.post("/api/agent/{task_id}/reply")
    def reply_agent(task_id: str, question: AgentReply, request: Request):
        return service.run(question, lambda: identify(request), task_id=task_id)

    @app.delete("/api/agent/{task_id}")
    def cancel_agent(task_id: str, request: Request):
        return service.cancel(task_id, request.state.principal)
