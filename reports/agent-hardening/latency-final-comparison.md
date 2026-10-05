# Agent latency / cost comparison

Two independent real API passes on the same fictional regression set. No causal/significance claim; model generation and service latency vary. All failed cases retained. Runtime Strict/all and ACL unchanged.

| Metric | Before | After |
| --- | --- | --- |
| task_success | 0.5 | 0.7916666666666666 |
| planning_success | 0.875 | 0.9583333333333334 |
| tool_selection_accuracy | 0.9166666666666666 | 0.9583333333333334 |
| clarification_accuracy | 0.9583333333333334 | 1 |
| grounded_answer_rate | 0.3888888888888889 | 0.7222222222222222 |
| planner_calls_per_task | 2.6666666666666665 | 2.5416666666666665 |
| tool_calls_per_task | 1.25 | 1.3333333333333333 |
| duplicate_calls | 1 | 0 |
| cost_per_task_usd | 0.0022355158333333333 | 0.002206185833333333 |
| latency_ms.p50 | 12258.825499999999 | 13231.716 |
| latency_ms.p95 | 18122.117350000004 | 20327.500000000004 |

| Phase | Before P50/P95 ms | After P50/P95 ms |
| --- | --- | --- |
| agent_planning | 5011.6 / 8711.5 | 4909.4 / 11101.7 |
| agent_tool_knowledge_search | 185.3 / 394.9 | 152.9 / 386.5 |
| agent_tool_calendar | 0.0 / 4.6 | 0.0 / 5.6 |
| agent_tool_calculator | 0.0 / 4.6 | 0.0 / 5.6 |
| generation | 4214.4 / 7436.8 | 5035.0 / 10090.9 |
| verification | 2626.1 / 6164.8 | 1834.6 / 4544.3 |

Different refusal/delivery mixes affect whole-set latency. Supplementary same-successful-answer cohort (selected after runs, not a replacement score):

```json
{
  "ids": [
    "purchase-limit-zh",
    "hotel-exclusion-en",
    "return-materials-en",
    "leave-materials-ja",
    "remote-clarify-zh",
    "return-deadline-en"
  ],
  "before_ms": {
    "count": 6,
    "mean": 12161.1615,
    "p50": 11456.688,
    "p95": 16169.485
  },
  "after_ms": {
    "count": 6,
    "mean": 14997.231666666667,
    "p50": 14070.1705,
    "p95": 19977.261749999998
  }
}
```
