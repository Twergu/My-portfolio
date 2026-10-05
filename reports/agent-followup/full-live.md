# Agent Evaluation: calculation-clarification-v2-full

Real Embedding + Planner + Generator + Strict Verifier + independent Judge API; isolated real SQLite search, deterministic Calculator, explicitly mock workweek Calendar; fictional AI-authored policies, NOT human-reviewed. No external writes.

Dataset: `7e2f341eac8a60c72d1a200d5c623662713a1546d5e320022e8cb88f05700d20`. Completed 24/24.

Planning is scored from actual trace and tool contracts. Task success additionally requires expected final status, correctness and independent groundedness. Answer quality denominators include **all answerable tasks**, including refusals/errors. Judge failures are not successes. No human-review claim.

| Metric | Value |
| --- | --- |
| task_success | 0.7916666666666666 |
| planning_success | 0.9166666666666666 |
| tool_selection_accuracy | 0.9583333333333334 |
| clarification_accuracy | 0.9583333333333334 |
| answer_correctness | 0.7222222222222222 |
| grounded_answer_rate | 0.8333333333333334 |
| grounded_rate_among_delivered | 1 |
| tool_calls_per_task | 1.2083333333333333 |
| planner_calls_per_task | 2.2083333333333335 |
| cost_per_task_usd | 0.0024599908333333333 |

Task latency ms: `{'count': 24, 'mean': 10938.046166666667, 'p50': 10356.811000000002, 'p95': 20126.087850000004}`. Indexing and Judge usage are separate; user thinking time excluded. Prices are configured estimates, not billing reconciliation.

| Phase | P50 ms | P95 ms |
| --- | --- | --- |
| agent_planning | 4055.227 | 7018.866650000001 |
| agent_tool_knowledge_search | 174.9645 | 371.44805 |
| agent_tool_calendar | 0.0 | 5.60205 |
| agent_tool_calculator | 0.0 | 5.7201 |
| generation | 4298.309499999999 | 7300.9280499999995 |
| verification | 2382.255 | 7135.0788 |

Phase timings are inclusive; HTTP/embedding overlap parent stages and must not be added to them. Absent stages contribute zero per task.

| Scenario | Status | Planning | Task success | Calls | ms | USD |
| --- | --- | --- | --- | --- | --- | --- |
| purchase-limit-zh | answered | True | True | 1 | 15640 | 0.00295602 |
| commuter-contractor-ja | answered | True | True | 1 | 10562 | 0.00241548 |
| hotel-exclusion-en | answered | True | True | 1 | 9773 | 0.00210026 |
| training-cancelled-zh | answered | True | True | 1 | 11952 | 0.00245432 |
| access-requirements-ja | answered | True | False | 1 | 16332 | 0.0034055 |
| return-materials-en | answered | True | False | 1 | 9286 | 0.00218136 |
| remote-probation-zh | answered | True | True | 1 | 10003 | 0.00227592 |
| leave-materials-ja | answered | True | True | 1 | 8315 | 0.00216368 |
| commuter-clarify-ja | invalid_model_response | False | False | 1 | 10151 | 0.00237344 |
| purchase-clarify-en | answered | True | True | 1 | 13020 | 0.0030542 |
| remote-clarify-zh | needs_input | False | False | 0 | 4266 | 0.0011710000000000002 |
| training-clarify-ja | answered | True | True | 2 | 23238 | 0.00497776 |
| purchase-multiply-en | answered | True | True | 2 | 16839 | 0.00344636 |
| hotel-two-nights-zh | unsupported_answer | True | False | 2 | 16378 | 0.0035319 |
| training-cap-ja | answered | True | True | 2 | 18403 | 0.00390798 |
| return-deadline-en | answered | True | True | 2 | 13654 | 0.00300036 |
| leave-mock-window-zh | answered | True | True | 2 | 14407 | 0.00296424 |
| return-purchase-cross-en | answered | True | True | 3 | 20430 | 0.00475676 |
| unavailable-send-ja | unavailable | True | True | 0 | 1736 | 0.0005278 |
| unavailable-ticket-en | unavailable | True | True | 0 | 1543 | 0.000486 |
| unavailable-grant-zh | unavailable | True | True | 0 | 1664 | 0.000505 |
| unavailable-balance-ja | unavailable | True | True | 0 | 1939 | 0.0005266 |
| unavailable-policy-en | insufficient_evidence | True | True | 2 | 5986 | 0.00163082 |
| unavailable-official-calendar-zh | unavailable | True | True | 2 | 6995 | 0.00222702 |
