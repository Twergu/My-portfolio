# Agent 評価：schema-repair-five-case-regression

Embedding、Planner、Generator、Strict Verifier、独立 Judge は実 API。隔離した実 SQLite 検索、決定的な Calculator、明示的な Mock 営業日カレンダーを使用します。制度は AI 作成の架空データで、人手レビュー未実施。外部への書き込みはありません。

データセット：`7e2f341eac8a60c72d1a200d5c623662713a1546d5e320022e8cb88f05700d20`. 完了：5/5.

計画は実 trace とツール契約から採点します。Task Success には期待する終状態、正確性、独立した根拠支持も必要です。回答品質の分母は拒否・エラーを含む**回答可能な全タスク**。Judge 失敗は成功扱いせず、人手レビュー済みとは主張しません。

| 指標 | 値 |
| --- | --- |
| task_success | 0.6 |
| planning_success | 0.8 |
| tool_selection_accuracy | 1 |
| clarification_accuracy | 0.8 |
| answer_correctness | 0.8 |
| grounded_answer_rate | 0.8 |
| grounded_rate_among_delivered | 1 |
| tool_calls_per_task | 2 |
| planner_calls_per_task | 2.4 |
| cost_per_task_usd | 0.004066732 |

タスク時間 ms：`{'count': 5, 'mean': 20622.6214, 'p50': 20133.09, 'p95': 30304.862199999996}`。索引作成と Judge 使用量は別集計で、ユーザーの思考時間は除きます。費用は設定単価による推定で、請求額との照合ではありません。

| 処理段階 | P50 ms | P95 ms |
| --- | --- | --- |
| agent_planning | 5472.842 | 8546.7488 |
| agent_tool_knowledge_search | 170.946 | 770.6581999999999 |
| agent_tool_calendar | 0.0 | 5.6941999999999995 |
| agent_tool_calculator | 5.53 | 5.586 |
| generation | 7216.84 | 12052.964 |
| verification | 4646.292 | 11289.600199999997 |

段階時間は内部処理を含み、HTTP/Embedding は親段階と重なるため加算できません。未実行の段階は、そのタスクではゼロとして集計します。

| シナリオ | 状態 | 計画 | タスク成功 | 呼び出し数 | ms | USD |
| --- | --- | --- | --- | --- | --- | --- |
| commuter-clarify-ja | answered | False | False | 1 | 20133 | 0.00416386 |
| training-clarify-ja | answered | True | True | 2 | 20771 | 0.00445342 |
| purchase-multiply-en | answered | True | True | 2 | 16225 | 0.00300138 |
| leave-mock-window-zh | answered | True | True | 2 | 13296 | 0.00283642 |
| return-purchase-cross-en | unsupported_answer | True | False | 3 | 32688 | 0.00587858 |
