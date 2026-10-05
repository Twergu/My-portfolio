# Agent Evaluation: guarded-handoff

Real Embedding + Planner + Generator + Strict Verifier + independent Judge API; isolated real SQLite search, deterministic Calculator, explicitly mock workweek Calendar; fictional AI-authored policies, NOT human-reviewed. No external writes.

Dataset: `7e2f341eac8a60c72d1a200d5c623662713a1546d5e320022e8cb88f05700d20`. Completed 24/24.

Planning is scored from actual trace and tool contracts. Task success additionally requires expected final status, correctness and independent groundedness. Answer quality denominators include **all answerable tasks**, including refusals/errors. Judge failures are not successes. No human-review claim.

| Metric | Value |
| --- | --- |
| task_success | 0.7083333333333334 |
| planning_success | 0.875 |
| tool_selection_accuracy | 0.875 |
| clarification_accuracy | 1 |
| answer_correctness | 0.6666666666666666 |
| grounded_answer_rate | 0.6666666666666666 |
| grounded_rate_among_delivered | 1 |
| tool_calls_per_task | 1.25 |
| planner_calls_per_task | 2.2916666666666665 |
| cost_per_task_usd | 0.00214715 |

Task latency ms: `{'count': 24, 'mean': 9994.561541666666, 'p50': 10682.009, 'p95': 19904.046050000008}`. Indexing and Judge usage are separate; user thinking time excluded. Prices are configured estimates, not billing reconciliation.

| Phase | P50 ms | P95 ms |
| --- | --- | --- |
| agent_planning | 3153.196 | 6336.08445 |
| agent_tool_knowledge_search | 155.949 | 280.5840000000002 |
| agent_tool_calendar | 0.0 | 4.5668 |
| agent_tool_calculator | 0.0 | 5.508900000000001 |
| generation | 3962.9855000000002 | 7870.6196 |
| verification | 2796.3244999999997 | 6379.817550000002 |

Phase timings are inclusive; HTTP/embedding overlap parent stages and must not be added to them. Absent stages contribute zero per task.

| Scenario | Status | Planning | Task success | Calls | ms | USD |
| --- | --- | --- | --- | --- | --- | --- |
| purchase-limit-zh | unsupported_answer | True | False | 1 | 12629 | 0.00250116 |
| commuter-contractor-ja | unsupported_answer | True | False | 1 | 11188 | 0.00211956 |
| hotel-exclusion-en | answered | True | True | 1 | 6431 | 0.00120732 |
| training-cancelled-zh | answered | True | True | 1 | 12144 | 0.00238078 |
| access-requirements-ja | answered | True | True | 1 | 12199 | 0.00250204 |
| return-materials-en | unsupported_answer | True | False | 1 | 9189 | 0.00195612 |
| remote-probation-zh | answered | True | True | 1 | 9123 | 0.00199758 |
| leave-materials-ja | answered | True | True | 1 | 9784 | 0.00207516 |
| commuter-clarify-ja | needs_input | True | False | 1 | 10176 | 0.00262708 |
| purchase-clarify-en | answered | True | True | 1 | 12800 | 0.0027530600000000003 |
| remote-clarify-zh | answered | True | True | 1 | 14604 | 0.0031792599999999997 |
| training-clarify-ja | needs_input | False | False | 1 | 6589 | 0.0017242400000000001 |
| purchase-multiply-en | answered | True | True | 2 | 13837 | 0.00277244 |
| hotel-two-nights-zh | unsupported_answer | False | False | 3 | 16150 | 0.0035624 |
| training-cap-ja | answered | False | False | 3 | 20567 | 0.00420276 |
| return-deadline-en | answered | True | True | 2 | 12700 | 0.00265044 |
| leave-mock-window-zh | answered | True | True | 2 | 11294 | 0.0024361 |
| return-purchase-cross-en | answered | True | True | 3 | 24009 | 0.00477024 |
| unavailable-send-ja | unavailable | True | True | 0 | 1469 | 0.0004016 |
| unavailable-ticket-en | unavailable | True | True | 0 | 1389 | 0.0003782 |
| unavailable-grant-zh | unavailable | True | True | 0 | 1297 | 0.0003936 |
| unavailable-balance-ja | unavailable | True | True | 0 | 1395 | 0.0003964 |
| unavailable-policy-en | insufficient_evidence | True | True | 1 | 2363 | 0.0006818 |
| unavailable-official-calendar-zh | unavailable | True | True | 2 | 6542 | 0.00186226 |
