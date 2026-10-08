# Agent Evaluation: final-code-freeze-9af3637

Real Embedding + Planner + Generator + Strict Verifier + independent Judge API; isolated real SQLite search, deterministic Calculator, explicitly mock workweek Calendar; fictional AI-authored policies, NOT human-reviewed. No external writes.

Dataset: `7e2f341eac8a60c72d1a200d5c623662713a1546d5e320022e8cb88f05700d20`. Completed 24/24.

Planning is scored from actual trace and tool contracts. Task success additionally requires expected final status, correctness and independent groundedness. Answer quality denominators include **all answerable tasks**, including refusals/errors. Judge failures are not successes. No human-review claim.

| Metric | Value |
| --- | --- |
| task_success | 0.75 |
| planning_success | 0.9166666666666666 |
| tool_selection_accuracy | 0.9166666666666666 |
| clarification_accuracy | 1 |
| answer_correctness | 0.7222222222222222 |
| grounded_answer_rate | 0.7222222222222222 |
| grounded_rate_among_delivered | 1 |
| tool_calls_per_task | 1.2083333333333333 |
| planner_calls_per_task | 2.2083333333333335 |
| cost_per_task_usd | 0.0025793891666666667 |

Task latency ms: `{'count': 24, 'mean': 13139.78475, 'p50': 12189.028, 'p95': 24921.773050000003}`. Indexing and Judge usage are separate; user thinking time excluded. Prices are configured estimates, not billing reconciliation.

| Phase | P50 ms | P95 ms |
| --- | --- | --- |
| agent_planning | 4272.778 | 9057.810200000004 |
| agent_tool_knowledge_search | 166.537 | 417.2006500000001 |
| agent_tool_calendar | 0.0 | 5.6356 |
| agent_tool_calculator | 0.0 | 5.6834999999999996 |
| generation | 4137.675 | 11080.066150000002 |
| verification | 3158.0195 | 8400.061900000002 |

Phase timings are inclusive; HTTP/embedding overlap parent stages and must not be added to them. Absent stages contribute zero per task.

| Scenario | Status | Planning | Task success | Calls | ms | USD |
| --- | --- | --- | --- | --- | --- | --- |
| purchase-limit-zh | unsupported_answer | True | False | 1 | 20396 | 0.00300632 |
| commuter-contractor-ja | answered | True | True | 1 | 17972 | 0.00335644 |
| hotel-exclusion-en | answered | True | True | 1 | 10808 | 0.00216006 |
| training-cancelled-zh | answered | True | True | 1 | 12286 | 0.00248752 |
| access-requirements-ja | answered | True | True | 1 | 16556 | 0.00257524 |
| return-materials-en | answered | True | True | 1 | 11950 | 0.00237934 |
| remote-probation-zh | answered | True | True | 1 | 10800 | 0.00228036 |
| leave-materials-ja | answered | True | True | 1 | 10777 | 0.00237784 |
| commuter-clarify-ja | unsupported_answer | True | False | 1 | 37333 | 0.00671768 |
| purchase-clarify-en | answered | True | True | 1 | 13332 | 0.0029961600000000003 |
| remote-clarify-zh | needs_input | False | False | 0 | 4355 | 0.0010942 |
| training-clarify-ja | unsupported_answer | True | False | 2 | 15366 | 0.00337154 |
| purchase-multiply-en | answered | True | True | 2 | 15276 | 0.00327418 |
| hotel-two-nights-zh | answered | True | True | 2 | 14898 | 0.00289452 |
| training-cap-ja | answered | True | True | 2 | 25200 | 0.00455568 |
| return-deadline-en | answered | True | True | 2 | 12092 | 0.0026563 |
| leave-mock-window-zh | unsupported_answer | True | False | 2 | 15693 | 0.00307144 |
| return-purchase-cross-en | answered | True | True | 3 | 23344 | 0.00486334 |
| unavailable-send-ja | unavailable | True | True | 0 | 1706 | 0.000505 |
| unavailable-ticket-en | unavailable | True | True | 0 | 1477 | 0.0004872 |
| unavailable-grant-zh | unavailable | False | False | 1 | 11092 | 0.00115866 |
| unavailable-balance-ja | unavailable | True | True | 0 | 1837 | 0.0005146 |
| unavailable-policy-en | insufficient_evidence | True | True | 1 | 3779 | 0.00097416 |
| unavailable-official-calendar-zh | unavailable | True | True | 2 | 7028 | 0.00214756 |
