# Agent 評価：final-quotable-tool-evidence

Embedding、Planner、Generator、Strict Verifier、独立 Judge は実 API。隔離した実 SQLite 検索、決定的な Calculator、明示的な Mock 営業日カレンダーを使用します。制度は AI 作成の架空データで、人手レビュー未実施。外部への書き込みはありません。

データセット：`7e2f341eac8a60c72d1a200d5c623662713a1546d5e320022e8cb88f05700d20`. 完了：24/24.

計画は実 trace とツール契約から採点します。Task Success には期待する終状態、正確性、独立した根拠支持も必要です。回答品質の分母は拒否・エラーを含む**回答可能な全タスク**。Judge 失敗は成功扱いせず、人手レビュー済みとは主張しません。

| 指標 | 値 |
| --- | --- |
| task_success | 0.7916666666666666 |
| planning_success | 0.9583333333333334 |
| tool_selection_accuracy | 0.9583333333333334 |
| clarification_accuracy | 1 |
| answer_correctness | 0.7222222222222222 |
| grounded_answer_rate | 0.7222222222222222 |
| grounded_rate_among_delivered | 1 |
| tool_calls_per_task | 1.3333333333333333 |
| planner_calls_per_task | 2.5416666666666665 |
| cost_per_task_usd | 0.002206185833333333 |

タスク時間 ms：`{'count': 24, 'mean': 12528.264333333333, 'p50': 13231.716, 'p95': 20327.500000000004}`。索引作成と Judge 使用量は別集計で、ユーザーの思考時間は除きます。費用は設定単価による推定で、請求額との照合ではありません。

| 処理段階 | P50 ms | P95 ms |
| --- | --- | --- |
| agent_planning | 4909.4465 | 11101.692350000001 |
| agent_tool_knowledge_search | 152.93349999999998 | 386.5317000000001 |
| agent_tool_calendar | 0.0 | 5.550199999999999 |
| agent_tool_calculator | 0.0 | 5.629 |
| generation | 5035.043 | 10090.882950000003 |
| verification | 1834.603 | 4544.29165 |

段階時間は内部処理を含み、HTTP/Embedding は親段階と重なるため加算できません。未実行の段階は、そのタスクではゼロとして集計します。

| シナリオ | 状態 | 計画 | タスク成功 | 呼び出し数 | ms | USD |
| --- | --- | --- | --- | --- | --- | --- |
| purchase-limit-zh | answered | True | True | 1 | 14444 | 0.0022691 |
| commuter-contractor-ja | answered | True | True | 1 | 14478 | 0.00241742 |
| hotel-exclusion-en | answered | True | True | 1 | 12767 | 0.00200086 |
| training-cancelled-zh | answered | True | True | 1 | 15292 | 0.0022499 |
| access-requirements-ja | answered | True | True | 1 | 10911 | 0.00197546 |
| return-materials-en | answered | True | True | 1 | 10504 | 0.00187152 |
| remote-probation-zh | answered | True | True | 1 | 11594 | 0.00191304 |
| leave-materials-ja | answered | True | True | 1 | 13696 | 0.00223472 |
| commuter-clarify-ja | needs_input | True | False | 1 | 13907 | 0.00253264 |
| purchase-clarify-en | answered | True | True | 1 | 16842 | 0.00273002 |
| remote-clarify-zh | answered | True | True | 1 | 20669 | 0.0030070599999999998 |
| training-clarify-ja | needs_input | False | False | 1 | 7872 | 0.00170636 |
| purchase-multiply-en | unsupported_answer | True | False | 2 | 12388 | 0.0020858 |
| hotel-two-nights-zh | answered | True | True | 2 | 16711 | 0.00280384 |
| training-cap-ja | answered | True | True | 2 | 18394 | 0.0032944 |
| return-deadline-en | answered | True | True | 2 | 17903 | 0.00301844 |
| leave-mock-window-zh | unsupported_answer | True | False | 2 | 12382 | 0.00209076 |
| return-purchase-cross-en | unsupported_answer | True | False | 3 | 28324 | 0.00478574 |
| unavailable-send-ja | unavailable | True | True | 0 | 1782 | 0.0003872 |
| unavailable-ticket-en | unavailable | True | True | 0 | 1985 | 0.0003758 |
| unavailable-grant-zh | unavailable | True | True | 0 | 1613 | 0.0003912 |
| unavailable-balance-ja | unavailable | True | True | 0 | 1835 | 0.0003832 |
| unavailable-policy-en | unavailable | True | True | 5 | 16204 | 0.00464014 |
| unavailable-official-calendar-zh | unavailable | True | True | 2 | 8180 | 0.00178384 |
