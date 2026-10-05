# Agent Evaluation: schema-repair-five-case-regression

Real Embedding + Planner + Generator + Strict Verifier + independent Judge API; isolated real SQLite search, deterministic Calculator, explicitly mock workweek Calendar; fictional AI-authored policies, NOT human-reviewed. No external writes.

Dataset: `7e2f341eac8a60c72d1a200d5c623662713a1546d5e320022e8cb88f05700d20`. Completed 5/5.

Planning is scored from actual trace and tool contracts. Task success additionally requires expected final status, correctness and independent groundedness. Answer quality denominators include **all answerable tasks**, including refusals/errors. Judge failures are not successes. No human-review claim.

| Metric | Value |
| --- | --- |
| task_success | 0.6 |
| planning_success | 0.8 |
| tool_selection_accuracy | 1 |
| clarification_accuracy | 0.8 |
| answer_correctness | 0.8 |
| grounded_answer_rate | 0.8 |
| grounded_rate_among_delivered | 1 |
| tool_calls_per_task | 2 |
| planner_calls_per_task | 2.4 |
| cost_per_task_usd | 0.004066732 |

Task latency ms: `{'count': 5, 'mean': 20622.6214, 'p50': 20133.09, 'p95': 30304.862199999996}`. Indexing and Judge usage are separate; user thinking time excluded. Prices are configured estimates, not billing reconciliation.

| Phase | P50 ms | P95 ms |
| --- | --- | --- |
| agent_planning | 5472.842 | 8546.7488 |
| agent_tool_knowledge_search | 170.946 | 770.6581999999999 |
| agent_tool_calendar | 0.0 | 5.6941999999999995 |
| agent_tool_calculator | 5.53 | 5.586 |
| generation | 7216.84 | 12052.964 |
| verification | 4646.292 | 11289.600199999997 |

Phase timings are inclusive; HTTP/embedding overlap parent stages and must not be added to them. Absent stages contribute zero per task.

| Scenario | Status | Planning | Task success | Calls | ms | USD |
| --- | --- | --- | --- | --- | --- | --- |
| commuter-clarify-ja | answered | False | False | 1 | 20133 | 0.00416386 |
| training-clarify-ja | answered | True | True | 2 | 20771 | 0.00445342 |
| purchase-multiply-en | answered | True | True | 2 | 16225 | 0.00300138 |
| leave-mock-window-zh | answered | True | True | 2 | 13296 | 0.00283642 |
| return-purchase-cross-en | unsupported_answer | True | False | 3 | 32688 | 0.00587858 |
