# Agent Evaluation: final-quotable-tool-evidence

Real Embedding + Planner + Generator + Strict Verifier + independent Judge API; isolated real SQLite search, deterministic Calculator, explicitly mock workweek Calendar; fictional AI-authored policies, NOT human-reviewed. No external writes.

Dataset: `7e2f341eac8a60c72d1a200d5c623662713a1546d5e320022e8cb88f05700d20`. Completed 3/24.

Planning is scored from actual trace and tool contracts. Task success additionally requires expected final status, correctness and independent groundedness. Answer quality denominators include **all answerable tasks**, including refusals/errors. Judge failures are not successes. No human-review claim.

| Metric | Value |
| --- | --- |
| task_success | 1 |
| planning_success | 1 |
| tool_selection_accuracy | 1 |
| clarification_accuracy | 1 |
| answer_correctness | 1 |
| grounded_answer_rate | 1 |
| grounded_rate_among_delivered | 1 |
| tool_calls_per_task | 1 |
| planner_calls_per_task | 2 |
| cost_per_task_usd | 0.002229126666666667 |

Task latency ms: `{'count': 3, 'mean': 13896.702333333333, 'p50': 14444.272, 'p95': 14475.052}`. Indexing and Judge usage are separate; user thinking time excluded. Prices are configured estimates, not billing reconciliation.

| Phase | P50 ms | P95 ms |
| --- | --- | --- |
| agent_planning | 4962.852 | 5195.3535 |
| agent_tool_knowledge_search | 151.814 | 178.8518 |
| agent_tool_calendar | 0.0 | 0.0 |
| agent_tool_calculator | 0.0 | 0.0 |
| generation | 4994.407 | 5598.5761 |
| verification | 3904.572 | 4081.4355000000005 |

Phase timings are inclusive; HTTP/embedding overlap parent stages and must not be added to them. Absent stages contribute zero per task.

| Scenario | Status | Planning | Task success | Calls | ms | USD |
| --- | --- | --- | --- | --- | --- | --- |
| purchase-limit-zh | answered | True | True | 1 | 14444 | 0.0022691 |
| commuter-contractor-ja | answered | True | True | 1 | 14478 | 0.00241742 |
| hotel-exclusion-en | answered | True | True | 1 | 12767 | 0.00200086 |
