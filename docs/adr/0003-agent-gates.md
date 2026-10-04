# ADR 0003: Defer consequential Agents and human review

Status update, 2026-10-04: the user authorized a staged, general-purpose read-only Agent, stopping for review after each stage. [Stage 1](../agent-stage1.md) adds the orchestration core; [stage 2](../agent-stage2.md) connects scoped retrieval, deterministic tools, authenticated task APIs and strict grounding; [stage 3](../agent-stage3.md) adds the bilingual chat interface, clarification lifecycle and typed evidence panels. Real API checks use fictional PDFs and an explicitly mock workweek calendar; the UI check retains one withheld Japanese continuation instead of claiming perfect quality. New remote CI/PostgreSQL acceptance remains pending. This supersedes the original blanket deferral of the Agent, but does not authorize consequential tools or human-review work.

No email, ticket creation, external data mutation or autonomous action tool is installed or exposed. Human review of the proposed evaluation set remains deferred at the user's request; all current synthetic/calibration sets retain an explicit non-human-reviewed label.

Before adding Router, Knowledge Search Tool and Evidence Validator, require a completed real RAG regression report, verifier confusion matrix, zero-skip PostgreSQL/ACL tests, successful Docker/CI and a documented latency/cost preset. The ACL resolver must remain ahead of every retrieval tool; an Agent cannot widen its principal's scope.

Future consequential tools must first create a reviewable proposal containing action, target, arguments, evidence and a content digest. The server must require a fresh authorized human approval tied to that exact proposal, expire stale approvals, invalidate approval after argument changes, recheck permissions, and use an idempotency key at execution. Rejection/cancellation means no tool execution. No timeout or model statement counts as approval. Audit logging and integration tests are prerequisites for exposing these actions.

This document is a future acceptance contract, not a claim that Agent approval flows or an audit log are already implemented.
