# Agent 評価：structured-calculation-and-clarification

Embedding、Planner、Generator、Strict Verifier、独立 Judge は実 API。隔離した実 SQLite 検索、決定的な Calculator、明示的な Mock 営業日カレンダーを使用します。制度は AI 作成の架空データで、人手レビュー未実施。外部への書き込みはありません。

データセット：`7e2f341eac8a60c72d1a200d5c623662713a1546d5e320022e8cb88f05700d20`. 完了：5/5.

計画は実 trace とツール契約から採点します。Task Success には期待する終状態、正確性、独立した根拠支持も必要です。回答品質の分母は拒否・エラーを含む**回答可能な全タスク**。Judge 失敗は成功扱いせず、人手レビュー済みとは主張しません。

| 指標 | 値 |
| --- | --- |
| task_success | 0.6 |
| planning_success | 1 |
| tool_selection_accuracy | 1 |
| clarification_accuracy | 1 |
| answer_correctness | 0.6 |
| grounded_answer_rate | 0.6 |
| grounded_rate_among_delivered | 1 |
| tool_calls_per_task | 2 |
| planner_calls_per_task | 2.6 |
| cost_per_task_usd | 0.003961676 |

タスク時間 ms：`{'count': 5, 'mean': 19590.586, 'p50': 20660.61, 'p95': 27424.336399999997}`。索引作成と Judge 使用量は別集計で、ユーザーの思考時間は除きます。費用は設定単価による推定で、請求額との照合ではありません。

| 処理段階 | P50 ms | P95 ms |
| --- | --- | --- |
| agent_planning | 6576.523 | 7807.9446 |
| agent_tool_knowledge_search | 172.867 | 955.6077999999998 |
| agent_tool_calendar | 0.0 | 5.6162 |
| agent_tool_calculator | 5.494 | 5.5962000000000005 |
| generation | 6286.6939999999995 | 12883.7784 |
| verification | 4723.929 | 10101.055 |

段階時間は内部処理を含み、HTTP/Embedding は親段階と重なるため加算できません。未実行の段階は、そのタスクではゼロとして集計します。

| シナリオ | 状態 | 計画 | タスク成功 | 呼び出し数 | ms | USD |
| --- | --- | --- | --- | --- | --- | --- |
| commuter-clarify-ja | needs_input | True | False | 1 | 14364 | 0.0032094 |
| training-clarify-ja | answered | True | True | 2 | 28681 | 0.0052063000000000005 |
| purchase-multiply-en | unsupported_answer | True | False | 2 | 20661 | 0.00391342 |
| leave-mock-window-zh | answered | True | True | 2 | 11851 | 0.00278304 |
| return-purchase-cross-en | answered | True | True | 3 | 22396 | 0.00469622 |
