# Agent Evaluation: structured-calculation-and-clarification

Real Embedding + Planner + Generator + Strict Verifier + independent Judge API; isolated real SQLite search, deterministic Calculator, explicitly mock workweek Calendar; fictional AI-authored policies, NOT human-reviewed. No external writes.

Dataset: `7e2f341eac8a60c72d1a200d5c623662713a1546d5e320022e8cb88f05700d20`. Completed 5/5.

Planning is scored from actual trace and tool contracts. Task success additionally requires expected final status, correctness and independent groundedness. Answer quality denominators include **all answerable tasks**, including refusals/errors. Judge failures are not successes. No human-review claim.

| Metric | Value |
| --- | --- |
| task_success | 0.6 |
| planning_success | 1 |
| tool_selection_accuracy | 1 |
| clarification_accuracy | 1 |
| answer_correctness | 0.6 |
| grounded_answer_rate | 0.6 |
| grounded_rate_among_delivered | 1 |
| tool_calls_per_task | 2 |
| planner_calls_per_task | 2.6 |
| cost_per_task_usd | 0.003961676 |

Task latency ms: `{'count': 5, 'mean': 19590.586, 'p50': 20660.61, 'p95': 27424.336399999997}`. Indexing and Judge usage are separate; user thinking time excluded. Prices are configured estimates, not billing reconciliation.

| Phase | P50 ms | P95 ms |
| --- | --- | --- |
| agent_planning | 6576.523 | 7807.9446 |
| agent_tool_knowledge_search | 172.867 | 955.6077999999998 |
| agent_tool_calendar | 0.0 | 5.6162 |
| agent_tool_calculator | 5.494 | 5.5962000000000005 |
| generation | 6286.6939999999995 | 12883.7784 |
| verification | 4723.929 | 10101.055 |

Phase timings are inclusive; HTTP/embedding overlap parent stages and must not be added to them. Absent stages contribute zero per task.

| Scenario | Status | Planning | Task success | Calls | ms | USD |
| --- | --- | --- | --- | --- | --- | --- |
| commuter-clarify-ja | needs_input | True | False | 1 | 14364 | 0.0032094 |
| training-clarify-ja | answered | True | True | 2 | 28681 | 0.0052063000000000005 |
| purchase-multiply-en | unsupported_answer | True | False | 2 | 20661 | 0.00391342 |
| leave-mock-window-zh | answered | True | True | 2 | 11851 | 0.00278304 |
| return-purchase-cross-en | answered | True | True | 3 | 22396 | 0.00469622 |
