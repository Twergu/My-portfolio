# 計算の主張・追加確認・人手レビューの変更報告

この作業は 3 つの優先事項に対応します。前回の[変更報告](agent-hardening-report.md)、24 問の JSON、計算の誤拒否 3 件、追加確認の失敗 2 件を維持し、ラベル変更や標本削除は行いません。

**最終全件検収の追記：** 依頼に従い最終コード `9af3637` で 24 問を 1 回すべて再実行しました。**Task Success 18/24、Correctness 13/18、Grounded 13/18**、P50/P95 **12.189/24.922 秒**、推定 USD **0.002579/task**。6 件の失敗と全出力を保持し、実行前後のハッシュでコード、Prompt、データ、旧レポートが不変と確認しました。結果を見た調整、失敗の再実行、採点変更はしていません。[凍結検収](../reports/agent-freeze-20261005/acceptance.md)と[元 JSON](../reports/agent-freeze-20261005/evaluation-live.json)を参照してください。以下はそれ以前の実装・段階別結果であり、最終全件スコアを代替しません。

## 1. 計算 Claim をサーバーが描画

Generator は `claims` に `{"calculation_source_id": 4}` を返せます。現在のサーバーツール出典への参照のみで、text、evidence、結果、単位の上書き、自己申告の Claim 種別を付加できません。バックエンドは存在、Calculator/Calendar 由来、observation_id、構造化結果を確認し、中国語・日本語・英語の固定文と引用を生成します。文書やユーザー出典 ID でツールを装えません。

Calculator は元の十進文字列、演算、結果、丸め、任意の単位を保持し、表示前に同じ十進実装で再計算します。単位は列挙値のみを認め、許可文書またはユーザー入力に該当する被演算数と単位の原文が必要で、サーバーが出典を固定引用します。単位未指定は空のままで、推測・自動換算しません。文字列としての単位の結び付けは次元や業務適用性の証明ではなく、引き続き Strict で検証します。

Calendar は開始・終了日、基準日、タイムゾーン、端点を含む規則、営業週・休日、Mock/live の出所を保持します。API の計算 Claim に `rendering=server_calculation` と `calculation` を付け、ツール、observation_id、出典番号、元引数、結果、単位の出所を保存します。自由文による許可・資格・承認の結論には適用可能な Document Evidence が必要です。全計算・制度 Claim に Strict/all を実行します。引用の厳密一致は緩めず、モデルの「非 Policy」という自己申告も認めません。

対象は `backend/calculations.py`、`agent_tools.py`、`agent_grounding.py`、`agent_service.py`、`rag.py`、`verification.py`。`tests/test_agent_calculations.py` は 3 言語、2 ツール、単位置換、ID/結果/種別偽造、承認の混入、Verifier 否定時の非表示、元の失敗 3 件の制御済み契約回帰を対象とします。元候補の計算部分だけ構造化参照へ置換し、歴史的レポートや他の主張は変えません。制御済みテストは新たな実 API スコアではありません。

関連回帰は 98 passed、24 PostgreSQL skipped。DB は実 CI で別途検収し、ローカル skip を成功扱いしません。

後続の実行で意味的誤拒否が発生しました。サーバーは「2026-10-09 に 7 暦日を加えると 2026-10-16」とだけ述べたのに、Verifier が会社の返却期限と解釈して制度条文を要求しました。バックエンドは構造化結果の検証済み `rendering=server_calculation` を Verifier に渡すよう修正し、モデルからは指定できません。Verifier は演算、日付、単位、制約を検証しますが、純粋な計算に制度の意味を勝手に加えてはいけません。自由文の制度推論には文書が必要で、マーカーは矛盾を免除せず、否定 verdict では非表示にします。偽造マーカーと正負の回帰例を追加しました。

## 2. 追加確認の完全性

`backend/clarification.py` が元の目的、各ターンの自己申告、対応する先行質問を逐語的にまとめます。Planner と Generator は同じ内容を使い、最新返信を新規タスクとせず、返信済みだけで全項目が解決したとも扱いません。Generator にはサーバーが確定した制度の適用日も渡し、有効日を追加の個人条件として尋ねないようにしました。

共通ルールは現在の質問と将来の手続きを区別します。条件・書類の説明に、雇用主の確認完了を先に証明する必要はありません。単一講座の見積もりに全講座数は不要ですが、合計を求める際に数量がなければ質問します。フルタイムであることは非 contractor の証明ではありません。明示的な除外条件付きで申請規則を説明でき、本人属性や承認が確認済みとは述べません。矛盾や決定に不可欠な条件の不足には、引き続き質問できます。

凍結した日本語 2 ケースの回帰で、複数ターンの原文と目的が Planner/Generator に完全に入ることを確認しました。合計には数量が必要な例と、矛盾を自動解決しない例も含めます。質問の意味的な必要性はモデルに依存し、これは文脈とプロンプトの契約であって、決定的な自然言語理解の保証ではありません。

関連回帰は 63 passed、3 PostgreSQL skipped。その後、Generator が answered/claims と questions を同時に返し、排他的な状態契約に違反しました。最大 1 回の形式修正を追加し、質問・主張を黙って消したり、quote/provenance/Verifier で拒否済みの回答を再試行したりはしません。修正後も全 Strict を実行し、再び不正なら非表示にします。回数上限と Verifier 拒否の維持を確認する 3 つの正負テストを追加しました。

最終ローカル回帰は 313 passed、37 PostgreSQL skipped。skip は成功に含めません。Ruff と format は通過。実 API と最終 CI は以下に記載します。

## 3. 人手レビューセット

[8 件のレビュー資料](agent-human-review-v1.md)、`evals/agent-human-review-v1.json`、空の annotations を作成しました。実際の「1 件あたり最大 5000 円」という誤候補、5,001 とちょうど 5,000 の境界、計算と許可の区別、領収書時点の曖昧さ、日本語の条件付き説明と講座見積もり、Mock カレンダーで承認を証明できない例を含めます。

各例に質問、制度全文、候補、必要根拠・許容解釈、確認対象の参照回答を提示しました。**この対話の依頼者が 8/8 件を実際にレビュー済みです。** 最初の「はい」は曖昧だったため確認し、その後各問の制度解釈を明記してもらいました。元発言、ラベル対応、時刻を [annotations](../evals/agent-human-review-v1.annotations.json) に保存。H01/H03/H04/H08 は誤り・根拠なし、H02/H05/H06/H07 は正確・根拠ありで、参照回答案は承認されました。[レビュー結果](../reports/agent-followup/human-review-completed.json)と確認待ち時点のスナップショットは別保存です。参照回答を見た補助付きレビューであり、独立した盲検評価ではありません。

`scripts.human_review_report` は凍結データのハッシュ、担当者宣言、タイムゾーン付き時刻、ID の一意性・完全性を検証します。署名・項目が欠ければ人手の正確性を出さず、参照回答に不同意なら「裁定待ち」として、確定正解に数えません。レビュー後の H01 と旧 Verifier の supported=true を比較できます。担当者の宣言を記録するだけで、本人確認を技術的に保証しません。意図的な誤候補を含む 8 件の正確性は候補校正の結果で、新しい Agent タスク成功率ではありません。

`tests/test_agent_human_review.py` は未レビュー・未署名、文字列 boolean、部分レビュー、ハッシュ変更、重複 ID、時刻形式、参照回答への不同意、過去の自動判定との不一致を対象とします。自動テストは明示的なテスト署名者を使い、実ラベルは依頼者の今回の各問への返信だけに由来します。

確定した意味に基づき、Generator/Verifier に「より高額な場合の別承認経路があるなら、分岐額を絶対上限と呼ばない」という汎用規則を追加しました。実際の精算上限は原文どおり維持し、5,000 という業務値はハードコードせず、検証も緩めません。`scripts.agent_human_calibration` による実 Verifier 校正は **7/8 一致、Precision 1.00、Recall 0.75、API エラー 0**。[結果](../reports/agent-followup/human-verifier-live.json)では H01 の絶対上限誤述を拒否しましたが、H05 の領収書時点の曖昧さの説明は根拠なしとされ、人手判定と異なります。プロンプト開発に使ったデータであり、未見データの正確性ではありません。

## 実測と残る制約

[最初の旧失敗 5 シナリオ](../reports/agent-followup/five-cases-live.md)では実 Embedding、Planner、Generator、Strict Verifier、独立 Judge を呼び、3/5 成功。講座見積もり、Mock カレンダー、複数制度の計算を完了しました。購入では計算 Claim は通過したものの別の制度適用推論が拒否され、通勤では制度日付・雇用区分を追加質問しました。全失敗を維持し、日付文脈と条件付き適用説明を補いました。

[24 問の全件実測](../reports/agent-followup/full-live.json)は、最後の形式修正・承認閾値のプロンプト追加**前**です。自動 Task Success 19/24、Correctness 13/18、Grounded Answer Rate 15/18、回答済み 15 件。元の計算失敗 3 件はすべて完了。P50/P95 10.357/20.126 秒、索引・Judge を除く推定 USD 0.002460/task。[同じセットの比較](../reports/agent-followup/full-comparison.md)に全失敗を保存しています。自動で「正解」とされた購入問題は再び分岐額を上限と述べ、人手解釈に反します。元の自動スコアは変更せず、人手の正確性とは呼びません。出力状態の混在、必要引用の欠落、再質問、完全性に関する Judge との不一致もありました。

形式修正後の[5 問再実測](../reports/agent-followup/five-cases-final-live.json)では 4/5 が回答し、その 4 件は独立の正確性・根拠検証を通過しましたが、凍結 Task Success は 3/5 のままです。通勤は不要な質問をせず条件を正しく説明したものの、旧「追加確認必須」ラベルでは失敗となり、変更しません。複数制度の純粋な日付計算は Verifier に制度期限と誤解されて拒否されました。本文は計算であって業務許可ではないと限定しており、Verifier の誤拒否です。RET-26 の 7 日ルールを十分説明したかは別の回答完全性評価で扱います。元判定は保持します。

最後の[実 Verifier 再検証](../reports/agent-followup/calculation-verifier-replay.json)は候補全文と根拠を維持し、バックエンドで再検証した計算参照にのみサーバーマーカーを追加しました。4 主張はすべて通過し、別途作った「計算が会社の期限で、利用者は適合済み」という反例は拒否しました。`python -m scripts.agent_calculation_replay --live --output <new-path.json>` で再現でき、入力・出力・使用量を保存します。2 リクエストは 8.800 / 2.744 秒、推定合計 USD 0.001640。Verifier のみであり、Agent 全体の時間ではありません。これは最終プロンプト修正を含みますが、24 問・5 問・人手校正は別の開発段階で、最新版の 1 回の全件成功に合成できません。

営業日カレンダーは Mock のままで、ACL、Citation、Strict を維持します。意味的推論、追加質問の必要性、単位・分類の適用性はモデル依存です。引用不足では拒否し、人手セットも 8 件の非盲検です。24 問は凍結合成回帰セットで、「条件説明に質問は必須か」の境界は新しい版で別途レビューし、旧スコアを書き換えません。

## 最終エンジニアリング検収

アプリ `467d4471d9654c3398dfb408530401631e5d0ff5` の [GitHub Actions](https://github.com/Twergu/My-portfolio/actions/runs/37310074658) は全通過。JUnit と JSON を照合し、**350 passed、0 failed、0 errors、0 skipped**、うち**実 PostgreSQL/pgvector 37 件**。フロントエンド 15/15、Ruff、format も通過。[全テスト](../reports/agent-followup/ci-final/tests.md)、[DB 一覧と JUnit ハッシュ](../reports/agent-followup/ci-final/postgres-tests.json)、[版と実行手順](../reports/agent-followup/ci-final/provenance.json)を参照してください。README は生成結果を参照し、件数を固定しません。

Docker Compose で App + pgvector 起動、ヘルスチェック、PDF 索引・物理ページ引用、再起動後の保持を[確認](../reports/agent-followup/ci-final/container-persistence.json)しました。Docker の Agent 部分は local mode の API gate で、全 Agent 契約は制御済みモデルと実 pgvector で検証。実モデル評価は別の SQLite 実行であり、live API + PostgreSQL の単一テストとは呼びません。

CI では [SQLite/pgvector 比較](../reports/agent-followup/ci-final/store-benchmark.md)と [1k/10k/100k Exact/HNSW](../reports/agent-followup/ci-final/vector-scale.md) も完了。合成ベクトルによる動作検証で、この作業では索引戦略を変えず Exact を既定にします。後続の保存コミットは文書・レポートのみで、検証済みアプリコードは変更しません。

## 変更ファイルと再現入口

| ファイル | 変更内容 |
| --- | --- |
| `backend/calculations.py`、`agent_tools.py` | 共通の十進演算と、構造化した数値・単位・日付・出所 |
| `backend/agent_grounding.py`、`agent_service.py` | 単位の原文対応、固定表示・引用、サーバーによる出所確認 |
| `backend/rag.py`、`verification.py` | 計算参照契約、サーバーマーカー、Strict、承認分岐の意味、最大 1 回の形式修正 |
| `backend/clarification.py`、`agent.py` | 元目的と各ターンを共有し、実不足条件と条件付き説明を規定 |
| `tests/test_agent_calculations.py`、`test_agent_clarification.py`、`test_agent_human_review.py` | 元失敗、偽造・越権、部分回答、形式修正、人手ラベルの回帰 |
| `scripts/agent_evaluate.py`、`agent_calculation_replay.py` | 追跡可能な部分集合選択と、元失敗の実 Verifier 再検証 |
| `scripts/prepare_agent_review.py`、`human_review_report.py`、`agent_human_calibration.py` | 凍結レビュー資料、人手発言の検証、実 Verifier 比較 |
| `evals/agent-human-review-v1*.json`、`docs/agent-human-review-v1.md` | 8 件の原文、候補、参照回答、実レビュー |
| `README.md`、`SOURCE_INDEX.md`、`docs/agent-evaluation.md`、`agent-runtime.md` | 実験範囲、動的テストリンク、相対ソース一覧、再現方法、制約 |

全データは `reports/agent-followup/`。コマンドと API/単体テストの範囲は[評価プロトコル](agent-evaluation.md)を参照してください。旧 `reports/agent-hardening/`、24 問、日本語回帰の元データは維持します。
