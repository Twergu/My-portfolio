# Agent latency / cost comparison

Two independent real API passes on the same fictional regression set. No causal/significance claim; model generation and service latency vary. All failed cases retained. Runtime Strict/all and ACL unchanged.

| Metric | Before | After |
| --- | --- | --- |
| task_success | 0.5 | 0.7083333333333334 |
| planning_success | 0.875 | 0.875 |
| tool_selection_accuracy | 0.9166666666666666 | 0.875 |
| clarification_accuracy | 0.9583333333333334 | 1 |
| grounded_answer_rate | 0.3888888888888889 | 0.6666666666666666 |
| planner_calls_per_task | 2.6666666666666665 | 2.2916666666666665 |
| tool_calls_per_task | 1.25 | 1.25 |
| duplicate_calls | 1 | 0 |
| cost_per_task_usd | 0.0022355158333333333 | 0.00214715 |
| latency_ms.p50 | 12258.825499999999 | 10682.009 |
| latency_ms.p95 | 18122.117350000004 | 19904.046050000008 |

| Phase | Before P50/P95 ms | After P50/P95 ms |
| --- | --- | --- |
| agent_planning | 5011.6 / 8711.5 | 3153.2 / 6336.1 |
| agent_tool_knowledge_search | 185.3 / 394.9 | 155.9 / 280.6 |
| agent_tool_calendar | 0.0 / 4.6 | 0.0 / 4.6 |
| agent_tool_calculator | 0.0 / 4.6 | 0.0 / 5.5 |
| generation | 4214.4 / 7436.8 | 3963.0 / 7870.6 |
| verification | 2626.1 / 6164.8 | 2796.3 / 6379.8 |

Different refusal/delivery mixes affect whole-set latency. Supplementary same-successful-answer cohort (selected after runs, not a replacement score):

```json
{
  "ids": [
    "hotel-exclusion-en",
    "leave-materials-ja",
    "remote-clarify-zh",
    "return-deadline-en",
    "leave-mock-window-zh"
  ],
  "before_ms": {
    "count": 5,
    "mean": 13208.6892,
    "p50": 15397.837000000001,
    "p95": 16251.175000000001
  },
  "after_ms": {
    "count": 5,
    "mean": 10962.6326,
    "p50": 11294.448,
    "p95": 14223.146
  }
}
```
