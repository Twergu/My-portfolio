# Agent Evaluation: direct-tool-handoff

Real Embedding + Planner + Generator + Strict Verifier + independent Judge API; isolated real SQLite search, deterministic Calculator, explicitly mock workweek Calendar; fictional AI-authored policies, NOT human-reviewed. No external writes.

Dataset: `7e2f341eac8a60c72d1a200d5c623662713a1546d5e320022e8cb88f05700d20`. Completed 24/24.

Planning is scored from actual trace and tool contracts. Task success additionally requires expected final status, correctness and independent groundedness. Answer quality denominators include **all answerable tasks**, including refusals/errors. Judge failures are not successes. No human-review claim.

| Metric | Value |
| --- | --- |
| task_success | 0.4583333333333333 |
| planning_success | 0.875 |
| tool_selection_accuracy | 0.875 |
| clarification_accuracy | 1 |
| answer_correctness | 0.2777777777777778 |
| grounded_answer_rate | 0.2777777777777778 |
| grounded_rate_among_delivered | 1 |
| tool_calls_per_task | 1.125 |
| planner_calls_per_task | 2 |
| cost_per_task_usd | 0.0022178808333333335 |

Task latency ms: `{'count': 24, 'mean': 11248.561708333333, 'p50': 10996.5625, 'p95': 20131.89965}`. Indexing and Judge usage are separate; user thinking time excluded. Prices are configured estimates, not billing reconciliation.

| Phase | P50 ms | P95 ms |
| --- | --- | --- |
| agent_planning | 3356.631 | 6359.83885 |
| agent_tool_knowledge_search | 149.838 | 291.74440000000016 |
| agent_tool_calendar | 0.0 | 4.5847 |
| agent_tool_calculator | 0.0 | 4.6081 |
| generation | 4986.022999999999 | 8206.99445 |
| verification | 3042.7709999999997 | 9304.053600000001 |

Phase timings are inclusive; HTTP/embedding overlap parent stages and must not be added to them. Absent stages contribute zero per task.

| Scenario | Status | Planning | Task success | Calls | ms | USD |
| --- | --- | --- | --- | --- | --- | --- |
| purchase-limit-zh | answered | True | True | 1 | 12483 | 0.00239528 |
| commuter-contractor-ja | unsupported_answer | True | False | 1 | 9504 | 0.00159044 |
| hotel-exclusion-en | answered | True | True | 1 | 9165 | 0.00163606 |
| training-cancelled-zh | unsupported_answer | True | False | 1 | 13533 | 0.00258168 |
| access-requirements-ja | unsupported_answer | True | False | 1 | 14761 | 0.00281954 |
| return-materials-en | answered | True | True | 1 | 7334 | 0.00134234 |
| remote-probation-zh | unsupported_answer | True | False | 1 | 12694 | 0.00248224 |
| leave-materials-ja | answered | True | True | 1 | 7615 | 0.00143648 |
| commuter-clarify-ja | unsupported_answer | True | False | 1 | 20004 | 0.0042922 |
| purchase-clarify-en | unsupported_answer | True | False | 1 | 15962 | 0.00284564 |
| remote-clarify-zh | unsupported_answer | True | False | 1 | 9510 | 0.0019709799999999998 |
| training-clarify-ja | needs_input | False | False | 0 | 3988 | 0.000985 |
| purchase-multiply-en | unsupported_answer | False | False | 3 | 18789 | 0.00387724 |
| hotel-two-nights-zh | unsupported_answer | True | False | 2 | 16455 | 0.003312 |
| training-cap-ja | unsupported_answer | False | False | 1 | 20154 | 0.00378614 |
| return-deadline-en | unsupported_answer | True | False | 2 | 16301 | 0.00317544 |
| leave-mock-window-zh | answered | True | True | 2 | 17454 | 0.0036633 |
| return-purchase-cross-en | unsupported_answer | True | False | 3 | 30110 | 0.00540562 |
| unavailable-send-ja | unavailable | True | True | 0 | 1446 | 0.0004044 |
| unavailable-ticket-en | unavailable | True | True | 0 | 1186 | 0.0003678 |
| unavailable-grant-zh | unavailable | True | True | 0 | 1097 | 0.00037 |
| unavailable-balance-ja | unavailable | True | True | 0 | 1572 | 0.0003932 |
| unavailable-policy-en | insufficient_evidence | True | True | 1 | 2777 | 0.00069542 |
| unavailable-official-calendar-zh | insufficient_evidence | True | True | 2 | 6070 | 0.0014007 |
