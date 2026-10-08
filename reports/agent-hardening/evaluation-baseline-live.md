# Agent Evaluation: baseline

Real Embedding + Planner + Generator + Strict Verifier + independent Judge API; isolated real SQLite search, deterministic Calculator, explicitly mock workweek Calendar; fictional AI-authored policies, NOT human-reviewed. No external writes.

Dataset: `7e2f341eac8a60c72d1a200d5c623662713a1546d5e320022e8cb88f05700d20`. Completed 24/24.

Planning is scored from actual trace and tool contracts. Task success additionally requires expected final status, correctness and independent groundedness. Answer quality denominators include **all answerable tasks**, including refusals/errors. Judge failures are not successes. No human-review claim.

| Metric | Value |
| --- | --- |
| task_success | 0.5 |
| planning_success | 0.875 |
| tool_selection_accuracy | 0.9166666666666666 |
| clarification_accuracy | 0.9583333333333334 |
| answer_correctness | 0.3888888888888889 |
| grounded_answer_rate | 0.3888888888888889 |
| grounded_rate_among_delivered | 1 |
| tool_calls_per_task | 1.25 |
| planner_calls_per_task | 2.6666666666666665 |
| cost_per_task_usd | 0.0022355158333333333 |

Task latency ms: `{'count': 24, 'mean': 10968.710375, 'p50': 12258.825499999999, 'p95': 18122.117350000004}`. Indexing and Judge usage are separate; user thinking time excluded. Prices are configured estimates, not billing reconciliation.

| Phase | P50 ms | P95 ms |
| --- | --- | --- |
| agent_planning | 5011.5735 | 8711.540100000004 |
| agent_tool_knowledge_search | 185.26850000000002 | 394.8718 |
| agent_tool_calendar | 0.0 | 4.6252 |
| agent_tool_calculator | 0.0 | 4.6103000000000005 |
| generation | 4214.4439999999995 | 7436.75155 |
| verification | 2626.064 | 6164.762250000001 |

Phase timings are inclusive; HTTP/embedding overlap parent stages and must not be added to them. Absent stages contribute zero per task.

| Scenario | Status | Planning | Task success | Calls | ms | USD |
| --- | --- | --- | --- | --- | --- | --- |
| purchase-limit-zh | answered | True | True | 1 | 13298 | 0.00226302 |
| commuter-contractor-ja | unsupported_answer | True | False | 1 | 13165 | 0.00207924 |
| hotel-exclusion-en | answered | True | True | 1 | 9615 | 0.00184326 |
| training-cancelled-zh | unsupported_answer | True | False | 1 | 11970 | 0.00226348 |
| access-requirements-ja | unsupported_answer | True | False | 1 | 12167 | 0.00242444 |
| return-materials-en | answered | True | True | 1 | 9174 | 0.00180534 |
| remote-probation-zh | unsupported_answer | True | False | 1 | 12625 | 0.00232324 |
| leave-materials-ja | answered | True | True | 1 | 9055 | 0.00186788 |
| commuter-clarify-ja | needs_input | True | False | 2 | 12351 | 0.00305278 |
| purchase-clarify-en | unsupported_answer | True | False | 1 | 18396 | 0.00319866 |
| remote-clarify-zh | answered | True | True | 1 | 15398 | 0.00297486 |
| training-clarify-ja | needs_input | False | False | 0 | 3918 | 0.0008929999999999999 |
| purchase-multiply-en | unsupported_answer | True | False | 2 | 16228 | 0.00331684 |
| hotel-two-nights-zh | unsupported_answer | True | False | 2 | 16572 | 0.003461 |
| training-cap-ja | unsupported_answer | True | False | 2 | 22637 | 0.00447078 |
| return-deadline-en | answered | True | True | 2 | 16427 | 0.00355144 |
| leave-mock-window-zh | answered | True | True | 2 | 15549 | 0.00335664 |
| return-purchase-cross-en | needs_input | False | False | 3 | 14196 | 0.00324402 |
| unavailable-send-ja | unavailable | True | True | 0 | 1731 | 0.0003972 |
| unavailable-ticket-en | unavailable | True | True | 0 | 1666 | 0.000357 |
| unavailable-grant-zh | unavailable | True | True | 0 | 1672 | 0.0003784 |
| unavailable-balance-ja | unavailable | True | True | 0 | 1606 | 0.0003716 |
| unavailable-policy-en | unavailable | False | False | 3 | 7205 | 0.0020801 |
| unavailable-official-calendar-zh | unavailable | True | True | 2 | 6628 | 0.00167816 |
