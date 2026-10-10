# Agent のレイテンシ・費用比較

同じ架空回帰セットで独立に実 API を実行した比較です。生成とサービス時間は変動するため、因果関係や統計的有意差は主張しません。全失敗を保持し、実行時 Strict/all と ACL は不変です。

| 指標 | 変更前 | 変更後 |
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

| 処理段階 | 変更前 P50/P95 ms | 変更後 P50/P95 ms |
| --- | --- | --- |
| agent_planning | 4055.2 / 7018.9 | 4272.8 / 9057.8 |
| agent_tool_knowledge_search | 175.0 / 371.4 | 166.5 / 417.2 |
| agent_tool_calendar | 0.0 / 5.6 | 0.0 / 5.6 |
| agent_tool_calculator | 0.0 / 5.7 | 0.0 / 5.7 |
| generation | 4298.3 / 7300.9 | 4137.7 / 11080.1 |
| verification | 2382.3 / 7135.1 | 3158.0 / 8400.1 |

拒否・回答の割合の違いも全体時間に影響します。以下は両実行で回答に成功した共通集合です。実行後に選んだ補足であり、全体スコアの代わりにはなりません。

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
