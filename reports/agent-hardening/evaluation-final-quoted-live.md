# Agent Evaluation: final-quotable-tool-evidence

Real Embedding + Planner + Generator + Strict Verifier + independent Judge API; isolated real SQLite search, deterministic Calculator, explicitly mock workweek Calendar; fictional AI-authored policies, NOT human-reviewed. No external writes.

Dataset: `7e2f341eac8a60c72d1a200d5c623662713a1546d5e320022e8cb88f05700d20`. Completed 24/24.

Planning is scored from actual trace and tool contracts. Task success additionally requires expected final status, correctness and independent groundedness. Answer quality denominators include **all answerable tasks**, including refusals/errors. Judge failures are not successes. No human-review claim.

| Metric | Value |
| --- | --- |
| task_success | 0.7916666666666666 |
| planning_success | 0.9583333333333334 |
| tool_selection_accuracy | 0.9583333333333334 |
| clarification_accuracy | 1 |
| answer_correctness | 0.7222222222222222 |
| grounded_answer_rate | 0.7222222222222222 |
| grounded_rate_among_delivered | 1 |
| tool_calls_per_task | 1.3333333333333333 |
| planner_calls_per_task | 2.5416666666666665 |
| cost_per_task_usd | 0.002206185833333333 |

Task latency ms: `{'count': 24, 'mean': 12528.264333333333, 'p50': 13231.716, 'p95': 20327.500000000004}`. Indexing and Judge usage are separate; user thinking time excluded. Prices are configured estimates, not billing reconciliation.

| Phase | P50 ms | P95 ms |
| --- | --- | --- |
| agent_planning | 4909.4465 | 11101.692350000001 |
| agent_tool_knowledge_search | 152.93349999999998 | 386.5317000000001 |
| agent_tool_calendar | 0.0 | 5.550199999999999 |
| agent_tool_calculator | 0.0 | 5.629 |
| generation | 5035.043 | 10090.882950000003 |
| verification | 1834.603 | 4544.29165 |

Phase timings are inclusive; HTTP/embedding overlap parent stages and must not be added to them. Absent stages contribute zero per task.

| Scenario | Status | Planning | Task success | Calls | ms | USD |
| --- | --- | --- | --- | --- | --- | --- |
| purchase-limit-zh | answered | True | True | 1 | 14444 | 0.0022691 |
| commuter-contractor-ja | answered | True | True | 1 | 14478 | 0.00241742 |
| hotel-exclusion-en | answered | True | True | 1 | 12767 | 0.00200086 |
| training-cancelled-zh | answered | True | True | 1 | 15292 | 0.0022499 |
| access-requirements-ja | answered | True | True | 1 | 10911 | 0.00197546 |
| return-materials-en | answered | True | True | 1 | 10504 | 0.00187152 |
| remote-probation-zh | answered | True | True | 1 | 11594 | 0.00191304 |
| leave-materials-ja | answered | True | True | 1 | 13696 | 0.00223472 |
| commuter-clarify-ja | needs_input | True | False | 1 | 13907 | 0.00253264 |
| purchase-clarify-en | answered | True | True | 1 | 16842 | 0.00273002 |
| remote-clarify-zh | answered | True | True | 1 | 20669 | 0.0030070599999999998 |
| training-clarify-ja | needs_input | False | False | 1 | 7872 | 0.00170636 |
| purchase-multiply-en | unsupported_answer | True | False | 2 | 12388 | 0.0020858 |
| hotel-two-nights-zh | answered | True | True | 2 | 16711 | 0.00280384 |
| training-cap-ja | answered | True | True | 2 | 18394 | 0.0032944 |
| return-deadline-en | answered | True | True | 2 | 17903 | 0.00301844 |
| leave-mock-window-zh | unsupported_answer | True | False | 2 | 12382 | 0.00209076 |
| return-purchase-cross-en | unsupported_answer | True | False | 3 | 28324 | 0.00478574 |
| unavailable-send-ja | unavailable | True | True | 0 | 1782 | 0.0003872 |
| unavailable-ticket-en | unavailable | True | True | 0 | 1985 | 0.0003758 |
| unavailable-grant-zh | unavailable | True | True | 0 | 1613 | 0.0003912 |
| unavailable-balance-ja | unavailable | True | True | 0 | 1835 | 0.0003832 |
| unavailable-policy-en | unavailable | True | True | 5 | 16204 | 0.00464014 |
| unavailable-official-calendar-zh | unavailable | True | True | 2 | 8180 | 0.00178384 |
