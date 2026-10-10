# Agent 評価：baseline

Embedding、Planner、Generator、Strict Verifier、独立 Judge は実 API。隔離した実 SQLite 検索、決定的な Calculator、明示的な Mock 営業日カレンダーを使用します。制度は AI 作成の架空データで、人手レビュー未実施。外部への書き込みはありません。

データセット：`7e2f341eac8a60c72d1a200d5c623662713a1546d5e320022e8cb88f05700d20`. 完了：0/24.

計画は実 trace とツール契約から採点します。Task Success には期待する終状態、正確性、独立した根拠支持も必要です。回答品質の分母は拒否・エラーを含む**回答可能な全タスク**。Judge 失敗は成功扱いせず、人手レビュー済みとは主張しません。

| 指標 | 値 |
| --- | --- |
| task_success | None |
| planning_success | None |
| tool_selection_accuracy | None |
| clarification_accuracy | None |
| answer_correctness | None |
| grounded_answer_rate | None |
| grounded_rate_among_delivered | None |
| tool_calls_per_task | None |
| planner_calls_per_task | None |
| cost_per_task_usd | None |

タスク時間 ms：`{'count': 0, 'mean': None, 'p50': None, 'p95': None}`。索引作成と Judge 使用量は別集計で、ユーザーの思考時間は除きます。費用は設定単価による推定で、請求額との照合ではありません。

| 処理段階 | P50 ms | P95 ms |
| --- | --- | --- |
| agent_planning | None | None |
| agent_tool_knowledge_search | None | None |
| agent_tool_calendar | None | None |
| agent_tool_calculator | None | None |
| generation | None | None |
| verification | None | None |

段階時間は内部処理を含み、HTTP/Embedding は親段階と重なるため加算できません。未実行の段階は、そのタスクではゼロとして集計します。

| シナリオ | 状態 | 計画 | タスク成功 | 呼び出し数 | ms | USD |
| --- | --- | --- | --- | --- | --- | --- |
