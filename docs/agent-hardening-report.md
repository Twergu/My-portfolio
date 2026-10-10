# Agent の信頼性・評価の変更報告

依頼の優先順で実装し、各項目をテストしてから次へ進みました。実モデルの結果と制御済み回帰テストを分け、過去の失敗データを保存します。

後続の計算表示、追加確認、人手レビューは[次の変更報告](agent-followup-report.md)を参照してください。以下はこの段階の凍結検収で、後の再実行で上書きしません。

## P0-1 日本語の複数ターン回答

完了。第 3 段階の元失敗は画面と使用量のみで、非表示候補を取得していなかったため、当時の 4 主張を復元したとは主張できません。同じ日本語質問、追加情報、架空制度で実再実行し、初回 2/4 通過、2 回目 3/3 通過を観測しました。[修正前のリクエスト、Generator、根拠、Verdict](../reports/agent-hardening/p0-before-live.json)と第 3 段階の 1/4 記録を保持しています。

確認した原因：

1. Generator の「条件を満たす」という主張がユーザー入力だけを引用し、同じ主張に制度も最終資格の確認待ちという限定もありませんでした。この遮断は妥当で、他の主張から未引用制度を借用させるべきではありません。
2. 「申請には…を提出します」という手続き説明を、Verifier が実際・確実に提出するという事実と読み、「提出できる」と「提出済み」の違いを理由に制度要件を否定しました。日本語の規範的表現の誤判定です。

`backend/rag.py` と `backend/verification.py` を修正。資格推論ごとに制度と本人条件を共同引用し、同じ文に自己申告・確認待ちを残します。必要書類は「提出が必要です」などで表します。Verifier は手続き上の要件、本人の能力、実行済み事実を区別し、制度引用なしの資格結論、未確認の提出・承認・約束は引き続き拒否します。

検証：

- [修正後の実複数ターン](../reports/agent-hardening/p0-after-live.json)：2 回とも needs_input → answered、3/3 主張通過。
- [実 Verifier 再検証](../reports/agent-hardening/p0-verifier-replay.json)：正負 6 例すべて期待どおり。実記録の文と構成した対照例を区別し、完全な Agent 実行とは扱いません。
- `tests/test_agent_japanese_regression.py` は[凍結した実失敗](../evals/agent-ja-regression.json)を使い、プロンプト契約、引用根拠のみの送信、厳密検証、未検証結果の非表示を確認。制御済み応答で、実 API の代わりではありません。
- 関連 Grounding/Agent：62 passed、1 PostgreSQL skipped（次項で実環境実行）。Strict/all を維持し、検証停止や根拠不足の受け入れはしません。

コマンド：`python -m scripts.agent_diagnose --live --repeats 2 --output <new-report.json>`、`python -m scripts.agent_verifier_replay --live --output <new-report.json>`。原文診断は架空制度の明示的オフライン実行のみで、本番 HTTP ログに非公開質問やキーを記録しません。最初のサンドボックス一時ディレクトリエラー `p0-before.json` も保持します。

少数例の通過は安定した正確性の保証ではありません。プロンプト修正は形式的な意味保証を与えず、後続評価も失敗を集計します。

## P0-2 全 CI / PostgreSQL / Docker

完了。[Actions 37181289264](https://github.com/Twergu/My-portfolio/actions/runs/37181289264)、コミット `4e1902bdf49541275cedeaf74c38258f856d9604` は 248 passed、0 failed、0 errors、0 skipped。実 PostgreSQL 17 + pgvector で DB テストを実行し、Agent HTTP/ACL/複数ターンは SQLite と PostgreSQL の両方を対象にしました。

`tests/test_agent_integration.py` に両 DB fixture を再利用し、`scripts/container_smoke.py` に Agent API とフロントエンドの確認を追加。Compose ビルド、ヘルス、PDF アップロード・索引・取得、再起動後の永続性が通過しました。Docker smoke は local 検索で API 設定 gate を確認し、実モデル呼び出しとは称しません。実モデルは P0-1 を参照。CI は skip が 1 件でも失敗とし、後続変更後に最終全 CI を再実行します。

## P1-3 Agent Evaluation

完了。`evals/make_agent.py`、`evals/agent_dataset.json`、`evals/agent_metrics.py`、`scripts/agent_evaluate.py`、`docs/agent-evaluation.md` を追加し、`evals/judge.py` に Agent 根拠の意味を拡張。中国語・日本語・英語の独立シナリオ 24 件で計画と最終回答を分けて採点し、全モデル出力・失敗を各問後に JSON/Markdown へ保存。上書きを禁止します。

`tests/test_agent_evaluation.py` と既存評価テストは 21 passed。拒否・例外の分母、回答済みと全体の groundedness、再開時の累積 trace の重複防止、不明費用 null、データ再構築を検証しました。一時ディレクトリの初回失敗 `evaluation-baseline.json` は残し、モデル品質実験に数えません。

[実ベースライン](../reports/agent-hardening/evaluation-baseline-live.md)：24/24 完了、Task Success 50.0%、Planning Success 87.5%、Tool Selection 91.7%、Clarification 95.8%。回答可能な 18 タスク中 7 件を回答し、独立 Correctness/Groundedness は通過、残りは失敗。P50/P95 12.259/18.122 秒、Judge・索引を除く USD 0.002236/task。非連続 quote、文書にない追加条件、誤った自己申告への帰属、不要な質問が失敗原因です。曖昧な問題を含む未レビュー回帰セットで、汎化精度や本番安定性は主張しません。

## P1-4 レイテンシ

実装と実測は完了し、P95 は未改善です。基準の平均は Planner 4.726 秒、Generator 3.608 秒、Verifier 2.394 秒、Knowledge Search 0.221 秒/タスク。`backend/agent.py` に任意の `answer_after` を追加し、最後の読み取り専用ツールが成功し、非空の本文・出典を返せば Generator に直接引き継ぎます。`prepare_answer` だけのモデル往復を省きます。空結果・失敗・重複は対象外で、全成功条件、AgentService の再 ACL、Strict/all を維持します。

編成と両 DB の HTTP 安全回帰を追加し、ローカル関連テストは通過（DB は最終 CI）。[初回比較](../reports/agent-hardening/latency-first-attempt.md)では Planner 2.67→2.00、P50 12.259→10.997 秒でしたが、P95 18.122→20.132 秒、Task Success 50.0%→45.8%。未達の実行を最終成功とは扱いません。

business_task が検索から直接引き継ぎ Calculator を省いた例を確認。業務検索では再計画を必須とし、直接の知識質問、または制度の前提を取得済みの最終 Calculator/Calendar のみ早期引き継ぎを許可しました。早すぎる引き継ぎと途中の権限取り消しをテスト。83 passed、18 PostgreSQL skipped（最終 CI で実行）。

[同一セットの実比較](../reports/agent-hardening/latency-comparison.md)：Planner 2.67→2.29 回/タスク、P50 12.259→10.682 秒（約 -12.9%）、平均 USD 0.002236→0.002147（約 -4.0%）、Task Success 50.0%→70.8%。P95 は 18.122→19.904 秒で改善せず、全体が速くなったとは言えません。生成・サービスの変動があり、同一回答の因果比較ではありません。両実行で成功した共通集合も補足しますが、主表は全失敗を含みます。

## P2-5 Policy Claim の制約

完了。`backend/agent_grounding.py` を追加し、`backend/rag.py` と `backend/agent_service.py` に接続。引用文書はサーバー取得の document/retrieved で、文書・Chunk・物理ページの ID と適用可能な状態・日付が必要です。既定は現行制度、明示的 as_of では有効な過去制度を許可。草案、未分類、将来・失効済み文書では現在の許可を証明できず、未引用文書は借用できません。

モデルの Claim 自己分類に頼らず、全自由文 claim に有効文書を要求する保守的な決定ルールです。文書なしで認めるのは、サーバーが構造化数値・日付から作る中国語・日本語・英語の固定計算文のみで、「したがって精算可・承認済み」を追加できません。User Input は自己申告のままで、単独で制度を証明しません。全候補に Strict/all を実行し、Verifier は除去しません。文書の存在だけでは意味的正確性は保証できず、Verifier が必要です。

Generator の確認済み欠陥も修正し、全制度に一律に「雇用主確認」を加えず、引用制度が要求する場合だけ残します。一般的な仮定を実際のユーザー申告と偽らせません。Verifier の受け入れ基準は変えていません。

`tests/test_agent_policy_grounding.py` は意図的に通過を返す制御済み Verifier、計算・自己申告の制度偽装、未引用、失効・草案、固定計算への末尾追加、表示文の偽造、物理ページ ID を検証。92 passed、18 PostgreSQL skipped（最終 CI）。旧日本語 fixture の原文は不変で、新回帰にサーバー文書 ID を追加し、元の誤りをモデル検証前に拒否できることを確認します。

## P3-6 状態管理の境界

完了。単一プロセスのメモリ、ユーザー別・全体容量、絶対 TTL、busy 排他、例外時解放を確認・維持しました。最小修正として、失効した取消・再開は両方 404、遅いリクエストは失効した再開ハンドルを返さず、初回 state 作成時に PendingTask を結び付けます。初回検索後の再インデックスを runner 終了待ちではなく、次 Planner 呼び出し前に検出します。

`tests/test_agent_integration.py` は実スレッドで返信・取消・他人アクセスの競合を検証し、モデル経路が 1 回だけであることを確認（busy フラグを書き換えるだけではない）。期限延長なし、TTL 境界、遅い追加確認、例外解放、全体容量、再起動でハンドルは失うが文書は保持することを検証。79 passed、24 PostgreSQL skipped（最終 CI）。[実行境界](agent-runtime.md)に worker 1 個、900 秒、100/4 の容量、強制中断なし、切断後も課金され得ること、再起動後は新タスクが必要なことを記載。Redis/キューは追加しません。

## 最終検収

実 API 評価は 24/24 完了。アプリ `fcfb60f05030055b7c4a05386c4aa3af53762e5f` の[全 Actions](https://github.com/Twergu/My-portfolio/actions/runs/37249750795) は通過しました。JUnit と成果物を照合し、**314 passed、0 failed、0 errors、0 skipped**、うち [pgvector 34 ケース](../reports/agent-hardening/ci-final/postgres-tests.json)をすべて実行。フロントエンド 15/15、Ruff、Docker ビルド・ヘルス・PDF 引用・再起動保持、1k/10k/100k Vector Benchmark も通過。[版と手順](../reports/agent-hardening/ci-final/provenance.json)、[自動テスト](../reports/agent-hardening/ci-final/tests.md)、[Docker](../reports/agent-hardening/ci-final/container-persistence.json)を保存。最後の保存作業は文書、レポート、README 表生成の文言のみで、アプリ動作は検収版と同一です。

全件 `evaluation-final-complete-live.json` は 24/24、Task Success 66.7%、Planning/Tool Selection/Clarification はすべて 100% でしたが、ツール 6 ケースを quote mismatch で遮断しました。原因は**新しい固定計算文が metadata のみにあり source.text に未登録**だったこと。モデルが正しいサーバー計算文をコピーしても引用一致しない統合欠陥で、quote を緩めるべきではありません。

同じサーバー計算文を tool source.text に追加し、元計算文も保持する最小修正を実施。中国語・日本語・英語 × Calculator/Calendar の 6 回帰を追加し、104 passed、24 PostgreSQL skipped（最終 CI）。失敗実行はそのまま残し、修正後全実測を `evaluation-final-quoted-live.json` に保存しました。

この段階の `return-deadline-en` では Correctness Judge が `answer_correct=false` を返しつつ reason で正しいと説明しました。都合のよい説明で手動変更せず false のまま採点します。自動 Judge の限界であり、決定的なバックエンド保証ではありません。

P1 コミット `e41b980` の [CI](https://github.com/Twergu/My-portfolio/actions/runs/37198130074) は 269 passed、0 failed、0 errors、0 skipped。[元記録](../reports/agent-hardening/ci-p1/tests.json)を維持。引用修正後のローカル全件は 280 passed、34 PostgreSQL skipped で、上記最終 CI が全 DB ケースを実行しました。

`evaluation-final-live.json` はプロセス中断により 15/24 のみで、最終全件結果として扱ったり、再実行と合成してスコアを上げたりしません。全失敗を保持し、中断時に送信済みだった可能性のあるリクエストと未保存の索引使用量は不明で、ゼロ扱いしません。次の完全実行は `evaluation-final-complete-live.json` です。

中断結果では `purchase-limit-zh` が 5000 JPY の承認経路の分岐額を購入の絶対上限と述べたのに、実行時 Verifier と Correctness Judge が見逃しました。Grounding Judge は「購入前の領収書」に異議を示し、架空原文の領収書時点自体も不明瞭でした。原文、候補、全 verdict、過去スコアを維持します。固定出典・有効期間の検査は意味判断の代替ではなく、自動 groundedness は人手の保証ではありません。

### 最終実 API 結果と未達項目

[問題別 JSON](../reports/agent-hardening/evaluation-final-quoted-live.json) / [Markdown](../reports/agent-hardening/evaluation-final-quoted-live.md)は同じ凍結データ、モデル、検索設定で 24 ケースをすべて実行し、失敗を除いていません。実 API は隔離 SQLite、PostgreSQL 全回帰は別 CI で、組み合わせて実 API + PostgreSQL の E2E 実測とは呼びません。

| 指標 | ベースライン | この段階の最終版 |
| --- | ---: | ---: |
| Task Success Rate | 12/24、50.0% | 19/24、79.2% |
| Planning Success | 21/24、87.5% | 23/24、95.8% |
| Tool Selection Accuracy | 22/24、91.7% | 23/24、95.8% |
| Clarification Accuracy | 23/24、95.8% | 24/24、100% |
| Answer Correctness / 回答可能な全タスク | 7/18、38.9% | 13/18、72.2% |
| Grounded Answer Rate / 回答可能な全タスク | 7/18、38.9% | 13/18、72.2% |
| 回答済みのうち独立 Grounding Judge 通過 | 7/7 | 13/13 |
| Planner calls/task | 2.67 | 2.54 |
| Tool calls/task | 1.25 | 1.33 |
| 重複ツール要求（遮断） | 1 | 0 |
| P50 / P95 | 12.259 / 18.122 秒 | 13.232 / 20.328 秒 |
| 平均アプリ費用 | USD 0.002236/task | USD 0.002206/task |

実行不能タスク 6 件は正しく unavailable を返しました。失敗した 5 件：

- `commuter-clarify-ja`：Generator が雇用属性・雇用主確認を再質問し、Verifier は未実行。固定返信はフルタイムとのみ述べ contractor を明示的に除外していません。追加確認の十分性とデータの意味境界の問題で、Verifier 誤拒否ではありません。返信は 1 回のみの契約なので失敗です。
- `training-clarify-ja`：Planner が講座数を尋ねましたが固定返信に答えがなく Calculator 未実行。ツール・計画・タスクが失敗。
- `purchase-multiply-en`、`leave-mock-window-zh`、`return-purchase-cross-en`：モデルがツール・ユーザー入力のみを引用した計算を自由に言い換え、決定的な `applicable_document_required` で遮断。計算自体が許可を与えたわけではなく、保守的制約による正当な計算表現の誤遮断コストです。Strict Verifier はまだ未実行なので責任を帰しません。元候補を維持し、スコア向上目的で制約を緩めません。

この実行に quote mismatch はありません。6 件の出典本文欠落は修正しましたが、上の 3 件はモデルが固定文契約に従わない可能性を示します。次は検証可能な構造化計算 Claim のサーバー描画と安全回帰を設計し、モデル自己申告の「非制度」を単純受理しない方針です。

最終版の平均は Planner / Generator / Verifier が 5.577 / 4.853 / 1.885 秒、Knowledge Search が 0.193 秒/タスクで、モデルが主な時間要因です。引き継ぎ単独実験では P50 と費用が低下しましたが、最終強化版は基準より **P50・P95 とも改善せず**、費用は約 1.3% 低下のみ。[最終性能比較](../reports/agent-hardening/latency-final-comparison.md)に全問と共通成功集合を保存し、良い中間結果で最終性能を代替しません。

費用は設定単価推定で索引・独立 Judge を除き、請求書照合ではありません。AI 作成・未レビューの制度 8 件を 1 PDF の 8 ページにし、複数制度・ページを扱いますが複数 PDF の集約は未評価。Clarification Accuracy は質問の発生のみで十分性・冗長性・表現を測らず、100% でも完全な確認品質ではありません。Judge の見逃しと自己矛盾もあり、高スコアは人手検収ではありません。失敗・中断をすべて保持します。

## 変更ファイル一覧

| ファイル | 変更内容 |
| --- | --- |
| `backend/verification.py` | 日本語の規範と実行事実の区別、同一 claim の全前提、根拠のない雇用主確認の排除 |
| `backend/rag.py` | Agent 生成規則、Strict 前の決定的 Policy Evidence 制約 |
| `backend/agent.py` | 最終ツールの制限付き引き継ぎ、初回からのサーバー状態参照 |
| `backend/agent_service.py` | 固定計算文、過去日付、失効取消・不正ハンドル、初回の根拠変更検出 |
| `backend/agent_grounding.py` | 文書 ID・状態・日付、サーバーの 3 言語計算文。モデル分類に依存しない |
| `evals/agent-ja-regression.json` | 実失敗の Generator/Evidence/Verdict 凍結データ |
| `evals/make_agent.py`, `evals/agent_dataset.json` | 再構築可能な 24 シナリオと参照契約 |
| `evals/agent_metrics.py`, `evals/judge.py` | 計画と回答の独立採点、分母、呼び出し・時間・費用、独立 Judge |
| `scripts/agent_diagnose.py`, `scripts/agent_verifier_replay.py` | 架空制度での実複数ターン診断と正負 Verifier 再検証 |
| `scripts/agent_evaluate.py`, `scripts/agent_compare.py` | 実全件評価、問題別保存、失敗保持、同セット性能比較 |
| `scripts/agent_results_summary.py` | 実測全件 JSON から README Agent 表を自動更新 |
| `tests/test_agent_japanese_regression.py` | 元の日本語失敗、条件・規範・提出済みの回帰 |
| `tests/test_agent_policy_grounding.py` | 自己申告・ツールによる制度偽装、無効文書、固定計算の迂回防止 |
| `tests/test_agent.py`, `tests/test_agent_integration.py` | 引き継ぎ安全性、両 DB Agent/ACL、並行・期限・再起動・再索引 |
| `tests/test_agent_evaluation.py` | データ・指標契約、失敗保持、不完全・異なるデータの比較禁止 |
| `scripts/container_smoke.py` | Docker Agent API/UI gate と既存 PDF・再起動検証 |
| `README.md`, `SOURCE_INDEX.md` | 成果・制約の入口、相対パスの全ソース一覧 |
| `docs/agent-evaluation.md`, `docs/agent-runtime.md`, 本書 | 評価方式、実行境界、項目別変更報告 |
| `reports/agent-hardening/*` | 元失敗、実全呼び出し、性能、CI。モデル実測と制御済みテストを区別 |
