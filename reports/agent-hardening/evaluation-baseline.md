# Agent Evaluation: baseline

Real Embedding + Planner + Generator + Strict Verifier + independent Judge API; isolated real SQLite search, deterministic Calculator, explicitly mock workweek Calendar; fictional AI-authored policies, NOT human-reviewed. No external writes.

Dataset: `7e2f341eac8a60c72d1a200d5c623662713a1546d5e320022e8cb88f05700d20`. Completed 0/24.

Planning is scored from actual trace and tool contracts. Task success additionally requires expected final status, correctness and independent groundedness. Answer quality denominators include **all answerable tasks**, including refusals/errors. Judge failures are not successes. No human-review claim.

| Metric | Value |
| --- | --- |
| task_success | None |
| planning_success | None |
| tool_selection_accuracy | None |
| clarification_accuracy | None |
| answer_correctness | None |
| grounded_answer_rate | None |
| grounded_rate_among_delivered | None |
| tool_calls_per_task | None |
| planner_calls_per_task | None |
| cost_per_task_usd | None |

Task latency ms: `{'count': 0, 'mean': None, 'p50': None, 'p95': None}`. Indexing and Judge usage are separate; user thinking time excluded. Prices are configured estimates, not billing reconciliation.

| Phase | P50 ms | P95 ms |
| --- | --- | --- |
| agent_planning | None | None |
| agent_tool_knowledge_search | None | None |
| agent_tool_calendar | None | None |
| agent_tool_calculator | None | None |
| generation | None | None |
| verification | None | None |

Phase timings are inclusive; HTTP/embedding overlap parent stages and must not be added to them. Absent stages contribute zero per task.

| Scenario | Status | Planning | Task success | Calls | ms | USD |
| --- | --- | --- | --- | --- | --- | --- |
