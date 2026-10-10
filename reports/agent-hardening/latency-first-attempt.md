# Agent のレイテンシ・費用比較

同じ架空回帰セットで独立に実 API を実行した比較です。生成とサービス時間は変動するため、因果関係や統計的有意差は主張しません。全失敗を保持し、実行時 Strict/all と ACL は不変です。

| 指標 | 変更前 | 変更後 |
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

| 処理段階 | 変更前 P50/P95 ms | 変更後 P50/P95 ms |
| --- | --- | --- |
| agent_planning | 5011.6 / 8711.5 | 3356.6 / 6359.8 |
| agent_tool_knowledge_search | 185.3 / 394.9 | 149.8 / 291.7 |
| agent_tool_calendar | 0.0 / 4.6 | 0.0 / 4.6 |
| agent_tool_calculator | 0.0 / 4.6 | 0.0 / 4.6 |
| generation | 4214.4 / 7436.8 | 4986.0 / 8207.0 |
| verification | 2626.1 / 6164.8 | 3042.8 / 9304.1 |

拒否・回答の割合の違いも全体時間に影響します。以下は両実行で回答に成功した共通集合です。実行後に選んだ補足であり、全体スコアの代わりにはなりません。

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
