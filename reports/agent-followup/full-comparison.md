# Agent latency / cost comparison

Two independent real API passes on the same fictional regression set. No causal/significance claim; model generation and service latency vary. All failed cases retained. Runtime Strict/all and ACL unchanged.

| Metric | Before | After |
| --- | --- | --- |
| task_success | 0.7916666666666666 | 0.7916666666666666 |
| planning_success | 0.9583333333333334 | 0.9166666666666666 |
| tool_selection_accuracy | 0.9583333333333334 | 0.9583333333333334 |
| clarification_accuracy | 1 | 0.9583333333333334 |
| grounded_answer_rate | 0.7222222222222222 | 0.8333333333333334 |
| planner_calls_per_task | 2.5416666666666665 | 2.2083333333333335 |
| tool_calls_per_task | 1.3333333333333333 | 1.2083333333333333 |
| duplicate_calls | 0 | 0 |
| cost_per_task_usd | 0.002206185833333333 | 0.0024599908333333333 |
| latency_ms.p50 | 13231.716 | 10356.811000000002 |
| latency_ms.p95 | 20327.500000000004 | 20126.087850000004 |

| Phase | Before P50/P95 ms | After P50/P95 ms |
| --- | --- | --- |
| agent_planning | 4909.4 / 11101.7 | 4055.2 / 7018.9 |
| agent_tool_knowledge_search | 152.9 / 386.5 | 175.0 / 371.4 |
| agent_tool_calendar | 0.0 / 5.6 | 0.0 / 5.6 |
| agent_tool_calculator | 0.0 / 5.6 | 0.0 / 5.7 |
| generation | 5035.0 / 10090.9 | 4298.3 / 7300.9 |
| verification | 1834.6 / 4544.3 | 2382.3 / 7135.1 |

Different refusal/delivery mixes affect whole-set latency. Supplementary same-successful-answer cohort (selected after runs, not a replacement score):

```json
{
  "ids": [
    "purchase-limit-zh",
    "commuter-contractor-ja",
    "hotel-exclusion-en",
    "training-cancelled-zh",
    "remote-probation-zh",
    "leave-materials-ja",
    "purchase-clarify-en",
    "training-cap-ja",
    "return-deadline-en"
  ],
  "before_ms": {
    "count": 9,
    "mean": 15045.623777777777,
    "p50": 14478.472,
    "p95": 18197.5482
  },
  "after_ms": {
    "count": 9,
    "mean": 12369.075777777778,
    "p50": 11951.679,
    "p95": 17297.648999999998
  }
}
```
