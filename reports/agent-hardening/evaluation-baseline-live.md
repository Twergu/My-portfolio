# Agent 評価：baseline

Embedding、Planner、Generator、Strict Verifier、独立 Judge は実 API。隔離した実 SQLite 検索、決定的な Calculator、明示的な Mock 営業日カレンダーを使用します。制度は AI 作成の架空データで、人手レビュー未実施。外部への書き込みはありません。

データセット：`7e2f341eac8a60c72d1a200d5c623662713a1546d5e320022e8cb88f05700d20`. 完了：24/24.

計画は実 trace とツール契約から採点します。Task Success には期待する終状態、正確性、独立した根拠支持も必要です。回答品質の分母は拒否・エラーを含む**回答可能な全タスク**。Judge 失敗は成功扱いせず、人手レビュー済みとは主張しません。

| 指標 | 値 |
| --- | --- |
| task_success | 0.5 |
| planning_success | 0.875 |
| tool_selection_accuracy | 0.9166666666666666 |
| clarification_accuracy | 0.9583333333333334 |
| answer_correctness | 0.3888888888888889 |
| grounded_answer_rate | 0.3888888888888889 |
| grounded_rate_among_delivered | 1 |
| tool_calls_per_task | 1.25 |
| planner_calls_per_task | 2.6666666666666665 |
| cost_per_task_usd | 0.0022355158333333333 |

タスク時間 ms：`{'count': 24, 'mean': 10968.710375, 'p50': 12258.825499999999, 'p95': 18122.117350000004}`。索引作成と Judge 使用量は別集計で、ユーザーの思考時間は除きます。費用は設定単価による推定で、請求額との照合ではありません。

| 処理段階 | P50 ms | P95 ms |
| --- | --- | --- |
| agent_planning | 5011.5735 | 8711.540100000004 |
| agent_tool_knowledge_search | 185.26850000000002 | 394.8718 |
| agent_tool_calendar | 0.0 | 4.6252 |
| agent_tool_calculator | 0.0 | 4.6103000000000005 |
| generation | 4214.4439999999995 | 7436.75155 |
| verification | 2626.064 | 6164.762250000001 |

段階時間は内部処理を含み、HTTP/Embedding は親段階と重なるため加算できません。未実行の段階は、そのタスクではゼロとして集計します。

| シナリオ | 状態 | 計画 | タスク成功 | 呼び出し数 | ms | USD |
| --- | --- | --- | --- | --- | --- | --- |
| purchase-limit-zh | answered | True | True | 1 | 13298 | 0.00226302 |
| commuter-contractor-ja | unsupported_answer | True | False | 1 | 13165 | 0.00207924 |
| hotel-exclusion-en | answered | True | True | 1 | 9615 | 0.00184326 |
| training-cancelled-zh | unsupported_answer | True | False | 1 | 11970 | 0.00226348 |
| access-requirements-ja | unsupported_answer | True | False | 1 | 12167 | 0.00242444 |
| return-materials-en | answered | True | True | 1 | 9174 | 0.00180534 |
| remote-probation-zh | unsupported_answer | True | False | 1 | 12625 | 0.00232324 |
| leave-materials-ja | answered | True | True | 1 | 9055 | 0.00186788 |
| commuter-clarify-ja | needs_input | True | False | 2 | 12351 | 0.00305278 |
| purchase-clarify-en | unsupported_answer | True | False | 1 | 18396 | 0.00319866 |
| remote-clarify-zh | answered | True | True | 1 | 15398 | 0.00297486 |
| training-clarify-ja | needs_input | False | False | 0 | 3918 | 0.0008929999999999999 |
| purchase-multiply-en | unsupported_answer | True | False | 2 | 16228 | 0.00331684 |
| hotel-two-nights-zh | unsupported_answer | True | False | 2 | 16572 | 0.003461 |
| training-cap-ja | unsupported_answer | True | False | 2 | 22637 | 0.00447078 |
| return-deadline-en | answered | True | True | 2 | 16427 | 0.00355144 |
| leave-mock-window-zh | answered | True | True | 2 | 15549 | 0.00335664 |
| return-purchase-cross-en | needs_input | False | False | 3 | 14196 | 0.00324402 |
| unavailable-send-ja | unavailable | True | True | 0 | 1731 | 0.0003972 |
| unavailable-ticket-en | unavailable | True | True | 0 | 1666 | 0.000357 |
| unavailable-grant-zh | unavailable | True | True | 0 | 1672 | 0.0003784 |
| unavailable-balance-ja | unavailable | True | True | 0 | 1606 | 0.0003716 |
| unavailable-policy-en | unavailable | False | False | 3 | 7205 | 0.0020801 |
| unavailable-official-calendar-zh | unavailable | True | True | 2 | 6628 | 0.00167816 |
