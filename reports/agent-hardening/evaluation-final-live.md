# Agent 評価：final-policy-state-hardening

Embedding、Planner、Generator、Strict Verifier、独立 Judge は実 API。隔離した実 SQLite 検索、決定的な Calculator、明示的な Mock 営業日カレンダーを使用します。制度は AI 作成の架空データで、人手レビュー未実施。外部への書き込みはありません。

データセット：`7e2f341eac8a60c72d1a200d5c623662713a1546d5e320022e8cb88f05700d20`. 完了：15/24.

計画は実 trace とツール契約から採点します。Task Success には期待する終状態、正確性、独立した根拠支持も必要です。回答品質の分母は拒否・エラーを含む**回答可能な全タスク**。Judge 失敗は成功扱いせず、人手レビュー済みとは主張しません。

| 指標 | 値 |
| --- | --- |
| task_success | 0.6 |
| planning_success | 0.9333333333333333 |
| tool_selection_accuracy | 0.9333333333333333 |
| clarification_accuracy | 1 |
| answer_correctness | 0.6666666666666666 |
| grounded_answer_rate | 0.6 |
| grounded_rate_among_delivered | 0.9 |
| tool_calls_per_task | 1.1333333333333333 |
| planner_calls_per_task | 2.1333333333333333 |
| cost_per_task_usd | 0.0021602053333333333 |

タスク時間 ms：`{'count': 15, 'mean': 10375.1902, 'p50': 11090.758, 'p95': 14051.295399999999}`。索引作成と Judge 使用量は別集計で、ユーザーの思考時間は除きます。費用は設定単価による推定で、請求額との照合ではありません。

| 処理段階 | P50 ms | P95 ms |
| --- | --- | --- |
| agent_planning | 3412.669 | 5360.9711 |
| agent_tool_knowledge_search | 153.158 | 394.9596000000005 |
| agent_tool_calendar | 0.0 | 0.0 |
| agent_tool_calculator | 0.0 | 5.7203 |
| generation | 4482.176 | 7589.8363 |
| verification | 2044.735 | 4240.467000000001 |

段階時間は内部処理を含み、HTTP/Embedding は親段階と重なるため加算できません。未実行の段階は、そのタスクではゼロとして集計します。

| シナリオ | 状態 | 計画 | タスク成功 | 呼び出し数 | ms | USD |
| --- | --- | --- | --- | --- | --- | --- |
| purchase-limit-zh | answered | True | False | 1 | 13295 | 0.00235314 |
| commuter-contractor-ja | answered | True | True | 1 | 12645 | 0.00240774 |
| hotel-exclusion-en | answered | True | True | 1 | 6884 | 0.00129206 |
| training-cancelled-zh | answered | True | True | 1 | 12986 | 0.00240026 |
| access-requirements-ja | answered | True | True | 1 | 14082 | 0.00270634 |
| return-materials-en | answered | True | True | 1 | 7825 | 0.00164152 |
| remote-probation-zh | answered | True | True | 1 | 8315 | 0.00172824 |
| leave-materials-ja | answered | True | True | 1 | 8564 | 0.00185972 |
| commuter-clarify-ja | needs_input | True | False | 1 | 9711 | 0.00257018 |
| purchase-clarify-en | answered | True | True | 1 | 11918 | 0.002686 |
| remote-clarify-zh | answered | True | True | 1 | 14038 | 0.00307038 |
| training-clarify-ja | needs_input | False | False | 0 | 4632 | 0.0010276 |
| purchase-multiply-en | unsupported_answer | True | False | 2 | 8398 | 0.0019603 |
| hotel-two-nights-zh | unsupported_answer | True | False | 2 | 11091 | 0.00228044 |
| training-cap-ja | unsupported_answer | True | False | 2 | 11245 | 0.00241916 |
