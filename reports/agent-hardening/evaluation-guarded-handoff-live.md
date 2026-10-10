# Agent 評価：guarded-handoff

Embedding、Planner、Generator、Strict Verifier、独立 Judge は実 API。隔離した実 SQLite 検索、決定的な Calculator、明示的な Mock 営業日カレンダーを使用します。制度は AI 作成の架空データで、人手レビュー未実施。外部への書き込みはありません。

データセット：`7e2f341eac8a60c72d1a200d5c623662713a1546d5e320022e8cb88f05700d20`. 完了：24/24.

計画は実 trace とツール契約から採点します。Task Success には期待する終状態、正確性、独立した根拠支持も必要です。回答品質の分母は拒否・エラーを含む**回答可能な全タスク**。Judge 失敗は成功扱いせず、人手レビュー済みとは主張しません。

| 指標 | 値 |
| --- | --- |
| task_success | 0.7083333333333334 |
| planning_success | 0.875 |
| tool_selection_accuracy | 0.875 |
| clarification_accuracy | 1 |
| answer_correctness | 0.6666666666666666 |
| grounded_answer_rate | 0.6666666666666666 |
| grounded_rate_among_delivered | 1 |
| tool_calls_per_task | 1.25 |
| planner_calls_per_task | 2.2916666666666665 |
| cost_per_task_usd | 0.00214715 |

タスク時間 ms：`{'count': 24, 'mean': 9994.561541666666, 'p50': 10682.009, 'p95': 19904.046050000008}`。索引作成と Judge 使用量は別集計で、ユーザーの思考時間は除きます。費用は設定単価による推定で、請求額との照合ではありません。

| 処理段階 | P50 ms | P95 ms |
| --- | --- | --- |
| agent_planning | 3153.196 | 6336.08445 |
| agent_tool_knowledge_search | 155.949 | 280.5840000000002 |
| agent_tool_calendar | 0.0 | 4.5668 |
| agent_tool_calculator | 0.0 | 5.508900000000001 |
| generation | 3962.9855000000002 | 7870.6196 |
| verification | 2796.3244999999997 | 6379.817550000002 |

段階時間は内部処理を含み、HTTP/Embedding は親段階と重なるため加算できません。未実行の段階は、そのタスクではゼロとして集計します。

| シナリオ | 状態 | 計画 | タスク成功 | 呼び出し数 | ms | USD |
| --- | --- | --- | --- | --- | --- | --- |
| purchase-limit-zh | unsupported_answer | True | False | 1 | 12629 | 0.00250116 |
| commuter-contractor-ja | unsupported_answer | True | False | 1 | 11188 | 0.00211956 |
| hotel-exclusion-en | answered | True | True | 1 | 6431 | 0.00120732 |
| training-cancelled-zh | answered | True | True | 1 | 12144 | 0.00238078 |
| access-requirements-ja | answered | True | True | 1 | 12199 | 0.00250204 |
| return-materials-en | unsupported_answer | True | False | 1 | 9189 | 0.00195612 |
| remote-probation-zh | answered | True | True | 1 | 9123 | 0.00199758 |
| leave-materials-ja | answered | True | True | 1 | 9784 | 0.00207516 |
| commuter-clarify-ja | needs_input | True | False | 1 | 10176 | 0.00262708 |
| purchase-clarify-en | answered | True | True | 1 | 12800 | 0.0027530600000000003 |
| remote-clarify-zh | answered | True | True | 1 | 14604 | 0.0031792599999999997 |
| training-clarify-ja | needs_input | False | False | 1 | 6589 | 0.0017242400000000001 |
| purchase-multiply-en | answered | True | True | 2 | 13837 | 0.00277244 |
| hotel-two-nights-zh | unsupported_answer | False | False | 3 | 16150 | 0.0035624 |
| training-cap-ja | answered | False | False | 3 | 20567 | 0.00420276 |
| return-deadline-en | answered | True | True | 2 | 12700 | 0.00265044 |
| leave-mock-window-zh | answered | True | True | 2 | 11294 | 0.0024361 |
| return-purchase-cross-en | answered | True | True | 3 | 24009 | 0.00477024 |
| unavailable-send-ja | unavailable | True | True | 0 | 1469 | 0.0004016 |
| unavailable-ticket-en | unavailable | True | True | 0 | 1389 | 0.0003782 |
| unavailable-grant-zh | unavailable | True | True | 0 | 1297 | 0.0003936 |
| unavailable-balance-ja | unavailable | True | True | 0 | 1395 | 0.0003964 |
| unavailable-policy-en | insufficient_evidence | True | True | 1 | 2363 | 0.0006818 |
| unavailable-official-calendar-zh | unavailable | True | True | 2 | 6542 | 0.00186226 |
