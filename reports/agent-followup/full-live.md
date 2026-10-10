# Agent 評価：calculation-clarification-v2-full

Embedding、Planner、Generator、Strict Verifier、独立 Judge は実 API。隔離した実 SQLite 検索、決定的な Calculator、明示的な Mock 営業日カレンダーを使用します。制度は AI 作成の架空データで、人手レビュー未実施。外部への書き込みはありません。

データセット：`7e2f341eac8a60c72d1a200d5c623662713a1546d5e320022e8cb88f05700d20`. 完了：24/24.

計画は実 trace とツール契約から採点します。Task Success には期待する終状態、正確性、独立した根拠支持も必要です。回答品質の分母は拒否・エラーを含む**回答可能な全タスク**。Judge 失敗は成功扱いせず、人手レビュー済みとは主張しません。

| 指標 | 値 |
| --- | --- |
| task_success | 0.7916666666666666 |
| planning_success | 0.9166666666666666 |
| tool_selection_accuracy | 0.9583333333333334 |
| clarification_accuracy | 0.9583333333333334 |
| answer_correctness | 0.7222222222222222 |
| grounded_answer_rate | 0.8333333333333334 |
| grounded_rate_among_delivered | 1 |
| tool_calls_per_task | 1.2083333333333333 |
| planner_calls_per_task | 2.2083333333333335 |
| cost_per_task_usd | 0.0024599908333333333 |

タスク時間 ms：`{'count': 24, 'mean': 10938.046166666667, 'p50': 10356.811000000002, 'p95': 20126.087850000004}`。索引作成と Judge 使用量は別集計で、ユーザーの思考時間は除きます。費用は設定単価による推定で、請求額との照合ではありません。

| 処理段階 | P50 ms | P95 ms |
| --- | --- | --- |
| agent_planning | 4055.227 | 7018.866650000001 |
| agent_tool_knowledge_search | 174.9645 | 371.44805 |
| agent_tool_calendar | 0.0 | 5.60205 |
| agent_tool_calculator | 0.0 | 5.7201 |
| generation | 4298.309499999999 | 7300.9280499999995 |
| verification | 2382.255 | 7135.0788 |

段階時間は内部処理を含み、HTTP/Embedding は親段階と重なるため加算できません。未実行の段階は、そのタスクではゼロとして集計します。

| シナリオ | 状態 | 計画 | タスク成功 | 呼び出し数 | ms | USD |
| --- | --- | --- | --- | --- | --- | --- |
| purchase-limit-zh | answered | True | True | 1 | 15640 | 0.00295602 |
| commuter-contractor-ja | answered | True | True | 1 | 10562 | 0.00241548 |
| hotel-exclusion-en | answered | True | True | 1 | 9773 | 0.00210026 |
| training-cancelled-zh | answered | True | True | 1 | 11952 | 0.00245432 |
| access-requirements-ja | answered | True | False | 1 | 16332 | 0.0034055 |
| return-materials-en | answered | True | False | 1 | 9286 | 0.00218136 |
| remote-probation-zh | answered | True | True | 1 | 10003 | 0.00227592 |
| leave-materials-ja | answered | True | True | 1 | 8315 | 0.00216368 |
| commuter-clarify-ja | invalid_model_response | False | False | 1 | 10151 | 0.00237344 |
| purchase-clarify-en | answered | True | True | 1 | 13020 | 0.0030542 |
| remote-clarify-zh | needs_input | False | False | 0 | 4266 | 0.0011710000000000002 |
| training-clarify-ja | answered | True | True | 2 | 23238 | 0.00497776 |
| purchase-multiply-en | answered | True | True | 2 | 16839 | 0.00344636 |
| hotel-two-nights-zh | unsupported_answer | True | False | 2 | 16378 | 0.0035319 |
| training-cap-ja | answered | True | True | 2 | 18403 | 0.00390798 |
| return-deadline-en | answered | True | True | 2 | 13654 | 0.00300036 |
| leave-mock-window-zh | answered | True | True | 2 | 14407 | 0.00296424 |
| return-purchase-cross-en | answered | True | True | 3 | 20430 | 0.00475676 |
| unavailable-send-ja | unavailable | True | True | 0 | 1736 | 0.0005278 |
| unavailable-ticket-en | unavailable | True | True | 0 | 1543 | 0.000486 |
| unavailable-grant-zh | unavailable | True | True | 0 | 1664 | 0.000505 |
| unavailable-balance-ja | unavailable | True | True | 0 | 1939 | 0.0005266 |
| unavailable-policy-en | insufficient_evidence | True | True | 2 | 5986 | 0.00163082 |
| unavailable-official-calendar-zh | unavailable | True | True | 2 | 6995 | 0.00222702 |
