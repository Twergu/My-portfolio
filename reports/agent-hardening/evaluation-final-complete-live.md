# Agent Evaluation: final-complete

Real Embedding + Planner + Generator + Strict Verifier + independent Judge API; isolated real SQLite search, deterministic Calculator, explicitly mock workweek Calendar; fictional AI-authored policies, NOT human-reviewed. No external writes.

Dataset: `7e2f341eac8a60c72d1a200d5c623662713a1546d5e320022e8cb88f05700d20`. Completed 24/24.

Planning is scored from actual trace and tool contracts. Task success additionally requires expected final status, correctness and independent groundedness. Answer quality denominators include **all answerable tasks**, including refusals/errors. Judge failures are not successes. No human-review claim.

| Metric | Value |
| --- | --- |
| task_success | 0.6666666666666666 |
| planning_success | 1 |
| tool_selection_accuracy | 1 |
| clarification_accuracy | 1 |
| answer_correctness | 0.5555555555555556 |
| grounded_answer_rate | 0.6111111111111112 |
| grounded_rate_among_delivered | 1 |
| tool_calls_per_task | 1.3333333333333333 |
| planner_calls_per_task | 2.25 |
| cost_per_task_usd | 0.0020397325 |

Task latency ms: `{'count': 24, 'mean': 11863.565666666667, 'p50': 12988.771499999999, 'p95': 21734.54240000001}`. Indexing and Judge usage are separate; user thinking time excluded. Prices are configured estimates, not billing reconciliation.

| Phase | P50 ms | P95 ms |
| --- | --- | --- |
| agent_planning | 4565.4125 | 10083.188400000003 |
| agent_tool_knowledge_search | 151.872 | 602.6214500000004 |
| agent_tool_calendar | 0.0 | 5.55975 |
| agent_tool_calculator | 0.0 | 5.62975 |
| generation | 5280.6645 | 8807.1412 |
| verification | 0.0 | 3762.41125 |

Phase timings are inclusive; HTTP/embedding overlap parent stages and must not be added to them. Absent stages contribute zero per task.

| Scenario | Status | Planning | Task success | Calls | ms | USD |
| --- | --- | --- | --- | --- | --- | --- |
| purchase-limit-zh | answered | True | True | 1 | 16784 | 0.0024617 |
| commuter-contractor-ja | answered | True | True | 1 | 14676 | 0.00244514 |
| hotel-exclusion-en | answered | True | True | 1 | 9011 | 0.00132846 |
| training-cancelled-zh | answered | True | True | 1 | 13097 | 0.00217426 |
| access-requirements-ja | answered | True | True | 1 | 16234 | 0.0021803 |
| return-materials-en | answered | True | True | 1 | 7611 | 0.00131934 |
| remote-probation-zh | answered | True | True | 1 | 12490 | 0.00209504 |
| leave-materials-ja | answered | True | True | 1 | 8974 | 0.00143888 |
| commuter-clarify-ja | needs_input | True | False | 2 | 16730 | 0.0037487799999999997 |
| purchase-clarify-en | answered | True | True | 1 | 15227 | 0.00266524 |
| remote-clarify-zh | answered | True | True | 2 | 22608 | 0.0037806 |
| training-clarify-ja | unsupported_answer | True | False | 2 | 15738 | 0.0030045799999999998 |
| purchase-multiply-en | unsupported_answer | True | False | 2 | 11770 | 0.0020962 |
| hotel-two-nights-zh | unsupported_answer | True | False | 2 | 13390 | 0.00220704 |
| training-cap-ja | unsupported_answer | True | False | 2 | 14113 | 0.00241176 |
| return-deadline-en | answered | True | False | 2 | 16398 | 0.0027963 |
| leave-mock-window-zh | unsupported_answer | True | False | 2 | 12881 | 0.00205744 |
| return-purchase-cross-en | unsupported_answer | True | False | 3 | 25732 | 0.00411334 |
| unavailable-send-ja | unavailable | True | True | 0 | 1830 | 0.0003968 |
| unavailable-ticket-en | unavailable | True | True | 0 | 2049 | 0.0003866 |
| unavailable-grant-zh | unavailable | True | True | 0 | 1909 | 0.0003936 |
| unavailable-balance-ja | unavailable | True | True | 0 | 1923 | 0.0003976 |
| unavailable-policy-en | insufficient_evidence | True | True | 2 | 6327 | 0.00128164 |
| unavailable-official-calendar-zh | unavailable | True | True | 2 | 7223 | 0.00177294 |
