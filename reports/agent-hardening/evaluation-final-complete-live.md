# Agent Evaluation: final-complete

Real Embedding + Planner + Generator + Strict Verifier + independent Judge API; isolated real SQLite search, deterministic Calculator, explicitly mock workweek Calendar; fictional AI-authored policies, NOT human-reviewed. No external writes.

Dataset: `7e2f341eac8a60c72d1a200d5c623662713a1546d5e320022e8cb88f05700d20`. Completed 8/24.

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
| planner_calls_per_task | 1.625 |
| cost_per_task_usd | 0.00193039 |

Task latency ms: `{'count': 8, 'mean': 12359.638125, 'p50': 12793.443, 'p95': 16591.62775}`. Indexing and Judge usage are separate; user thinking time excluded. Prices are configured estimates, not billing reconciliation.

| Phase | P50 ms | P95 ms |
| --- | --- | --- |
| agent_planning | 4177.7735 | 5699.28495 |
| agent_tool_knowledge_search | 155.5165 | 732.8401500000002 |
| agent_tool_calendar | 0.0 | 0.0 |
| agent_tool_calculator | 0.0 | 0.0 |
| generation | 5232.1955 | 6735.68615 |
| verification | 3045.9945 | 4629.65465 |

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
