# Agent latency / cost comparison

Two independent real API passes on the same fictional regression set. No causal/significance claim; model generation and service latency vary. All failed cases retained. Runtime Strict/all and ACL unchanged.

| Metric | Before | After |
| --- | --- | --- |
| task_success | 0.5 | 0.4583333333333333 |
| planning_success | 0.875 | 0.875 |
| tool_selection_accuracy | 0.9166666666666666 | 0.875 |
| clarification_accuracy | 0.9583333333333334 | 1 |
| grounded_answer_rate | 0.3888888888888889 | 0.2777777777777778 |
| planner_calls_per_task | 2.6666666666666665 | 2 |
| tool_calls_per_task | 1.25 | 1.125 |
| duplicate_calls | 1 | 0 |
| cost_per_task_usd | 0.0022355158333333333 | 0.0022178808333333335 |
| latency_ms.p50 | 12258.825499999999 | 10996.5625 |
| latency_ms.p95 | 18122.117350000004 | 20131.89965 |

| Phase | Before P50/P95 ms | After P50/P95 ms |
| --- | --- | --- |
| agent_planning | 5011.6 / 8711.5 | 3356.6 / 6359.8 |
| agent_tool_knowledge_search | 185.3 / 394.9 | 149.8 / 291.7 |
| agent_tool_calendar | 0.0 / 4.6 | 0.0 / 4.6 |
| agent_tool_calculator | 0.0 / 4.6 | 0.0 / 4.6 |
| generation | 4214.4 / 7436.8 | 4986.0 / 8207.0 |
| verification | 2626.1 / 6164.8 | 3042.8 / 9304.1 |

Different refusal/delivery mixes affect whole-set latency. Supplementary same-successful-answer cohort (selected after runs, not a replacement score):

```json
{
  "ids": [
    "purchase-limit-zh",
    "hotel-exclusion-en",
    "return-materials-en",
    "leave-materials-ja",
    "leave-mock-window-zh"
  ],
  "before_ms": {
    "count": 5,
    "mean": 11338.3004,
    "p50": 9614.97,
    "p95": 15098.938
  },
  "after_ms": {
    "count": 5,
    "mean": 10810.1712,
    "p50": 9165.119,
    "p95": 16459.42
  }
}
```
