# Agent 第 2 段階：実ツールと根拠付き回答

当時はバックエンドツール、Agent API、複数ターン、結果検証を接続し、実モデルの 4 フローを通過して停止しました。その後の続行指示で[第 3 段階の画面](agent-stage3.md)も完了しています。以下は当時の範囲と結果です。

## 変更と効果

| 変更 | 動作 |
| --- | --- |
| Knowledge Search | 既存 Dense/Hybrid/Reranker で実 Chunk、物理ページ、PDF リンク、制度 metadata を取得。モデルは検索語のみ指定し、範囲・ACL・版はサーバーが決定 |
| Calendar | 日付加減算、指定週の曜日、両端を含む区間。既定は明示的な Mock 月～金で、法定・会社休日は未設定。残高、空き時間、承認は確認できない |
| Calculator | Decimal で加減乗除・百分率。式やコードは実行しない。小数は最大 6 桁で丸めを明記。値・単位の業務適用性は文書・ユーザー根拠で別確認 |
| 根拠の出所 | document/tool/user を区別。PDF はページリンクを保持し、ツール・自己申告は PDF を装わず、計算・Mock・自己申告の表示を付ける |
| 回答生成 | 取得済み根拠を共有 answer_from_sources に渡し、Embedding/検索を繰り返さない。制度・計算・本人条件から結論、書類、手順を生成 |
| 厳密検証 | Agent は strict + all を強制し、出典番号、原文抜粋、全主張を検証。通常 RAG の設定は維持。1 主張でも根拠不足なら候補を隠す |
| 2 段階の質問機会 | Planner が質問でき、早期引き継ぎ後でも生成側が必要条件不足なら needs_input を返す。追加後は同タスクを継続し、制度根拠不足は拒否 |
| 複数ターンと権限 | サーバーメモリのみ。ランダム task ID をユーザーに紐付け、各モデル操作前に再認証・範囲確認。返信時は権限、文書、設定、旧根拠を再確認し、変化なら新規タスク |
| ライフサイクル | 全体 100、ユーザー別 4 タスク。作成から 15 分、同一タスクの並行返信禁止。追加情報待ちのみ保持、完了・失敗は解放し、待機は明示取消可能 |
| 可観測性 | Planner、Embedding、Generator、Verifier、ツールの時間と token/cost。入力ごとに計測し、利用者の思考時間を含めない |

[実ツール](../backend/agent_tools.py)、[タスク・HTTP](../backend/agent_service.py)、[共有回答処理](../backend/rag.py)、[検証規則](../backend/verification.py)、[結合テスト](../tests/test_agent_integration.py)。

## API

既存ログイン Cookie または Bearer Token で認証。local は単一ユーザー開発モードです。以下のリクエスト例は元の中国語を保持しています。

```http
POST /api/agent
Content-Type: application/json

{
  "question": "购买3本办公笔记本，每本1200日元，按采购规定需要提交什么？",
  "language": "zh",
  "document_ids": [],
  "filters": {"policy_status": ["current"]}
}
```

needs_input は task_id と questions を返します。再開は `POST /api/agent/{task_id}/reply`、本文は `{"question":"ユーザーの追加情報"}` のみ。状態、範囲変更、偽ツール結果は送信できません。待機取消は `DELETE /api/agent/{task_id}`。

answered は検証済み claims、sources、support、trace、metrics を含みます。evidence_notices に Mock、自己申告、外部業務操作未実行を明示。その他の状態は needs_input、insufficient_evidence、unsupported_answer、unavailable、error、limit_reached。

タイムゾーンは Asia/Tokyo、基準日は開始時にサーバーで固定し応答へ返します。権限があり有効に索引済みの文書がなければ、モデル前に no_accessible_evidence を返します。企業知識タスク向けで、空の知識庫で単独計算するモードは未公開です。

## 実 API 検証

[全 JSON](../reports/agent-stage2/live-smoke.json)に要求、使用量、応答、検証、費用を記録。gpt-5.6-luna と text-embedding-3-small を使い、一時アプリへ架空 PDF をアップロードして実索引を作成。検索は隔離 SQLite + Hybrid、日付と計算も実処理です。

| シナリオ | 実結果 |
| --- | --- |
| 中国語の購入 | 検索 + Calculator：3 × 1200 = 3600 円。必要書類と原文引用 |
| 日本語の研修申請 | 検索 + Calendar：開始 2026-10-12 の 3 暦日前は 2026-10-09。必要書類を列挙 |
| 英語の通勤補助 | 雇用区分と週の出社日数を質問。返信後は自己申告による条件付き判断と、雇用主確認の必要性を明示 |
| Mock 営業日 | 2026-10-02～10-06 の両端を含め、Mock 月～金では 3 営業日。会社休日は未確認と明示 |

4 フローで状態、期待ツール、厳密検証を通過しました。機能 smoke であって大規模品質評価ではなく、独立 Judge・人手レビューもありません。元制度と質問は[架空テストセット](../evals/agent-workflows.json)。

成功実行はモデル/Embedding 24 要求、報告 token 合計 32,927、索引・追加確認を含む推定 **USD 0.01040254**。最終回答ターンは約 7.94–16.82 秒で、通勤には前段の確認時間もあります。安定した P50/P95 benchmark ではなく、費用も請求額ではありません。

初回は「Planner が早すぎる引き継ぎを行い、生成側が条件不足で拒否」を確認。[修正前](../reports/agent-stage2/live-smoke-before-clarification.json)を削除せず、生成段階の構造化質問を追加して再実行しました。使用量のある 2 実行の合計は **USD 0.01908548**。[最初の一時ディレクトリ権限エラー](../reports/agent-stage2/live-smoke-first.json)も保存し、その実行に API 操作の記録はありません。

## 自動テストと当時の制約

- 件数・カバレッジは[動的テスト結果](../reports/tests.md)。Ruff lint/format 通過。権限取消、別ユーザー、metadata/モデル/索引変更、文脈偽造、期限・並行・容量、計算・日付境界、生成側質問からの再開を検証。
- ローカル PostgreSQL は未設定で skip。新 Agent の両 DB 共通検索権限契約も PG 側は skip で、成功としません。旧遠隔 CI/Docker は旧版で、この段階では未再実行。
- 状態は単一プロセスのメモリで再起動時に消失。複数プロセス・レプリカ共有なし。同期要求は Provider timeout・回数制限のみで、取消 API は送信中 HTTP を中断できません。
- 実業務日暦、HR 残高、承認状態、申請提出は未接続。Mock/自己申告の限定は実システム検証の代わりでなく、モデル検証も形式的証明ではありません。
- この時点では画面、LangGraph、外部書き込み、人手承認を追加していません。

再現：

```powershell
.\.venv\Scripts\python.exe -m scripts.check
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
# 有料呼び出しを明示的に許可。架空 PDF と質問のみ使用
.\.venv\Scripts\python.exe -m scripts.agent_live_smoke --live
```

次の第 3 段階は Agent モード、追加確認、分類出典カード、実ツール記録、実シナリオの画面接続です。当時はこの段階完了後に依頼者の確認を待ちました。
