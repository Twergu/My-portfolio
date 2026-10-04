# Agent Evaluation: guarded-handoff

Real Embedding + Planner + Generator + Strict Verifier + independent Judge API; isolated real SQLite search, deterministic Calculator, explicitly mock workweek Calendar; fictional AI-authored policies, NOT human-reviewed. No external writes.

Dataset: `7e2f341eac8a60c72d1a200d5c623662713a1546d5e320022e8cb88f05700d20`. Completed 12/24.

Planning is scored from actual trace and tool contracts. Task success additionally requires expected final status, correctness and independent groundedness. Answer quality denominators include **all answerable tasks**, including refusals/errors. Judge failures are not successes. No human-review claim.

| Metric | Value |
| --- | --- |
| task_success | 0.5833333333333334 |
| planning_success | 0.9166666666666666 |
| tool_selection_accuracy | 0.9166666666666666 |
| clarification_accuracy | 1 |
| answer_correctness | 0.5833333333333334 |
| grounded_answer_rate | 0.5833333333333334 |
| grounded_rate_among_delivered | 1 |
| tool_calls_per_task | 1 |
| planner_calls_per_task | 2.25 |
| cost_per_task_usd | 0.0022519466666666666 |

Task latency ms: `{'count': 12, 'mean': 10571.529666666667, 'p50': 10682.009, 'p95': 13611.87885}`. Indexing and Judge usage are separate; user thinking time excluded. Prices are configured estimates, not billing reconciliation.

| Phase | P50 ms | P95 ms |
| --- | --- | --- |
| agent_planning | 3152.0685 | 6110.381799999999 |
| agent_tool_knowledge_search | 162.05349999999999 | 259.12334999999985 |
| agent_tool_calendar | 0.0 | 0.0 |
| agent_tool_calculator | 0.0 | 0.0 |
| generation | 4268.3405 | 7283.83285 |
| verification | 2796.3244999999997 | 4235.0512499999995 |

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
