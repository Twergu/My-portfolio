# Agent latency / cost comparison

Two independent real API passes on the same fictional regression set. No causal/significance claim; model generation and service latency vary. All failed cases retained. Runtime Strict/all and ACL unchanged.

| Metric | Before | After |
| --- | --- | --- |
| task_success | 0.7916666666666666 | 0.75 |
| planning_success | 0.9166666666666666 | 0.9166666666666666 |
| tool_selection_accuracy | 0.9583333333333334 | 0.9166666666666666 |
| clarification_accuracy | 0.9583333333333334 | 1 |
| grounded_answer_rate | 0.8333333333333334 | 0.7222222222222222 |
| planner_calls_per_task | 2.2083333333333335 | 2.2083333333333335 |
| tool_calls_per_task | 1.2083333333333333 | 1.2083333333333333 |
| duplicate_calls | 0 | 0 |
| cost_per_task_usd | 0.0024599908333333333 | 0.0025793891666666667 |
| latency_ms.p50 | 10356.811000000002 | 12189.028 |
| latency_ms.p95 | 20126.087850000004 | 24921.773050000003 |

| Phase | Before P50/P95 ms | After P50/P95 ms |
| --- | --- | --- |
| agent_planning | 4055.2 / 7018.9 | 4272.8 / 9057.8 |
| agent_tool_knowledge_search | 175.0 / 371.4 | 166.5 / 417.2 |
| agent_tool_calendar | 0.0 / 5.6 | 0.0 / 5.6 |
| agent_tool_calculator | 0.0 / 5.7 | 0.0 / 5.7 |
| generation | 4298.3 / 7300.9 | 4137.7 / 11080.1 |
| verification | 2382.3 / 7135.1 | 3158.0 / 8400.1 |

Different refusal/delivery mixes affect whole-set latency. Supplementary same-successful-answer cohort (selected after runs, not a replacement score):

```json
{
  "ids": [
    "commuter-contractor-ja",
    "hotel-exclusion-en",
    "training-cancelled-zh",
    "remote-probation-zh",
    "leave-materials-ja",
    "purchase-clarify-en",
    "purchase-multiply-en",
    "training-cap-ja",
    "return-deadline-en",
    "return-purchase-cross-en"
  ],
  "before_ms": {
    "count": 10,
    "mean": 13295.0609,
    "p50": 12485.724999999999,
    "p95": 19517.795550000003
  },
  "after_ms": {
    "count": 10,
    "mean": 15188.8202,
    "p50": 12808.752,
    "p95": 24364.99915
  }
}
```
