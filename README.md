# Knowbase · 企業向けナレッジ AI アシスタント

PDF アップロード → ページ単位の解析 → Embedding → 権限・バージョンによる絞り込み → Hybrid Retrieval → 任意の Reranker → 構造化回答 → 主張の根拠検証 → PDF の物理ページへの引用。中国語・日本語 UI、接続を再利用する OpenAI 互換 Provider、PostgreSQL + pgvector、実 API による評価、Docker Compose に対応しています。

**クイックガイド：** [2 分間のデモ手順とスクリーンショット](docs/demo-walkthrough.md) · [安全な共有 / Docker + HTTPS デプロイ](docs/portfolio-sharing.md) · [凍結した 24 問の評価結果と 6 件の失敗](reports/agent-freeze-20261005/acceptance.md) · [デプロイ対応の変更報告](docs/portfolio-sharing-report.md)。現在はデプロイ可能なコードを提供しており、一般公開のオンラインデモはありません。デフォルトブランチに未マージの場合は `codex/rag-quality-v2` を参照してください。

![Knowbase Agent — 日本語の初期画面](docs/images/agent-home-ja.jpg)

日本語 UI の実ブラウザー画面（2026-10-10 撮影）。空の資料庫で撮影しており、API 回答や評価結果の画面ではありません。

```mermaid
flowchart LR
  U[ログイン済みユーザー] --> H[HTTPS / 利用制限]
  H --> A[認証と ACL]
  A --> R[RAG / 読み取り専用 Agent]
  R --> K[権限・バージョンの絞り込み → Hybrid Retrieval]
  K --> P[(PostgreSQL + pgvector)]
  R --> T[Calculator / Mock Calendar]
  K --> G[構造化 Generator]
  T --> G
  G --> V[サーバー側の根拠制約 + Strict Verifier]
  V --> O[回答 / 追加質問 / 回答拒否 + 引用]
```

公開用 Demo 設定では、読み取り専用アカウント、ユーザー別・IP 別・サイト全体のリクエスト制限、単一プロセス内の同時実行制限、永続化された API 費用の事前予約、HTTPS を有効にします。通常のローカル実行の動作は変わりません。凍結した API 評価の対象は `9af3637` です。追加したデプロイ保護機能の検証範囲は別途記録し、凍結後のプロンプト調整や成績の書き換えは行っていません。

デプロイ版 `e603ef2` は [CI の全チェックを通過](https://github.com/Twergu/My-portfolio/actions/runs/37615440769)しています。Python / 実 pgvector の全テストで失敗・エラー・スキップはなく、フロントエンド、Ruff、既存 Docker 回帰、新しい HTTPS Demo のログイン・利用制限・再起動検証、規模別ベンチマークも通過しました。テスト件数は[自動生成レポート](reports/portfolio-sharing/ci-final/tests.md)、[PostgreSQL の実行一覧](reports/portfolio-sharing/ci-final/postgres-tests.json)、[フロントエンドレポート](reports/portfolio-sharing/ci-final/frontend-tests.json)を参照してください。HTTPS 検証は CI 内部 CA とローカル検索を使用しており、一般公開や実 API による品質評価の再実施を意味するものではありません。

[全ソースファイル](SOURCE_INDEX.md) · [検索・権限に関する 12 項目の改善](docs/retrieval-optimization-report.md) · [前段階の 17 項目の改善](docs/optimization-report.md) · [初回変更記録](docs/change-report.md) · [アーキテクチャと設計判断](docs/architecture.md)。詳細評価、変更報告、共有・デプロイ手順は日本語で閲覧できます。評価の原文、モデル出力、JSON の識別子は元言語を保持します。[日本語化の範囲と原本](docs/localization-ja.md)を参照してください。

業務 Agent は、タスク計画、権限内のナレッジ検索、日付・計算ツール、複数ターンの追加確認、厳密な根拠検証に対応しています。チャット画面で「ナレッジ Q&A / 業務 Agent」を切り替えられます。日本語の失敗事例の回帰テスト、24 シナリオの実 API 評価、処理段階別の時間計測、制度に関する主張（Policy Claim）の決定的な制約、単一プロセスの状態管理検証を追加しました。詳細は [Modification Report](docs/agent-hardening-report.md) を参照してください。営業日カレンダーは明示的に Mock と表示されます。過去の失敗、[第 3 段階のブラウザー結合検証](docs/agent-stage3.md)、[第 2 段階のツール検証](docs/agent-stage2.md)、[第 1 段階の処理フロー](docs/agent-stage1.md)も保存しています。

フロントエンドテストは Node.js 24 の組み込みテストランナーを使用し、npm 依存はありません：`python -m scripts.check_frontend`。件数は実行結果から生成されます。[フロントエンドテストレポート](reports/agent-stage3/frontend-tests.json)、Python テストとカバレッジの[生成レポート](reports/tests.md)を参照してください。Agent は実 PostgreSQL + pgvector、Docker、GitHub Actions で検証済みです。対象バージョンと各レポートは以下に記載しています。

[![CI](https://github.com/Twergu/My-portfolio/actions/workflows/ci.yml/badge.svg?branch=codex%2Frag-quality-v2)](https://github.com/Twergu/My-portfolio/actions/workflows/ci.yml?query=branch%3Acodex%2Frag-quality-v2)

計算に関する主張はツール ID を引用し、構造化された数値・日付と固定引用をサーバー側で表示します。追加確認では、各ターンの質問・回答と制度の基準日を共有します。8 件の回答候補はプロジェクト依頼者が 1 件ずつ確認しており、[実際のアノテーション](evals/agent-human-review-v1.annotations.json)を保存しています。これは参考回答を提示したうえでの補助付きレビューです。[変更内容と検証](docs/agent-followup-report.md)、[人手レビュー資料](docs/agent-human-review-v1.md)を参照してください。

| 実 API による検証範囲 | 結果と制約 |
| --- | --- |
| [最終コードによる 24 問の凍結評価](reports/agent-freeze-20261005/acceptance.md)、バージョン `9af3637` | 24/24 問を完了。Task Success **18/24**、Correctness/Grounded **13/18**、回答を返したタスクは 13 件。P50/P95 **12.189/24.922 秒**、推定 **USD 0.002579/task**。6 件の失敗をすべて保存し、実行後のプロンプト調整・採点変更は実施していません |
| [修正前の 24 問の開発評価](reports/agent-followup/full-live.md) | 自動採点の Task Success 19/24、Correctness 13/18、Grounded 15/18。以前失敗した計算シナリオ 3 件を完了。P50/P95 10.357/20.126 秒、推定 USD 0.002460/task |
| [出力形式の修正後に 5 問を再検証](reports/agent-followup/five-cases-final-live.md) | 4/5 件で回答を返し、その 4 件は自動の正確性・根拠チェックを通過。ただし凍結した Task Success は 3/5 のまま。正しい直接回答と、旧ラベルの「追加確認が必須」との不一致を含みます |
| [最終 Strict Verifier の再検証](reports/agent-followup/calculation-verifier-replay.json) | 以前失敗した複数制度にまたがる回答候補の 4 主張がすべて通過。計算結果を制度上の期限や適合証明にすり替える反例は引き続き拒否。Verifier のみの再検証であり、新しいエンドツーエンド評価ではありません |
| [8 件の人手ラベルによる校正](reports/agent-followup/human-verifier-live.md) | 実 Verifier と人手判定の一致は 7/8、Precision 1.00、Recall 0.75。H05 の曖昧さに関する説明は依然として誤って拒否。プロンプト開発に使用したデータであり、ブラインド評価や未見テストではありません |

これらは異なる開発段階の実行結果であり、成績をまとめて扱うことはできません。モデル品質の最終評価は表の先頭にある凍結結果を参照してください。自動採点は以前、「承認経路の分岐額を絶対的な上限と解釈する」という誤りを受け入れていました。最終実行でも Generator は同じ誤りを生成しましたが、Strict が遮断し、タスクは失敗のまま計上しています。[最終比較](reports/agent-freeze-20261005/comparison.md)では成功率、P50/P95、費用は前回の全件開発評価を上回っていません。元の採点と失敗をすべて保存しています。費用は設定単価に基づく推定で、インデックス作成とオフライン Judge を除きます。独立したモデル実行 1 回ずつの比較から因果関係は断定できません。以下の Agent 表は前段階の凍結ベースラインです。

前段階の最終アプリケーション版 `467d447` も [CI の全チェックを通過](https://github.com/Twergu/My-portfolio/actions/runs/37310074658)しています。Python / 実 pgvector テストに失敗・エラー・スキップはなく、フロントエンドと Ruff、Docker ビルド・引用・再起動後の永続性、規模別ベンチマークを完了しました。件数は[テストレポート](reports/agent-followup/ci-final/tests.md)と[データベース実行一覧](reports/agent-followup/ci-final/postgres-tests.json)から確認できます。[Docker 検証](reports/agent-followup/ci-final/container-persistence.json)には対象範囲を記録しています。

<!-- AGENT_RESULTS_START -->
## 過去の Agent 実 API 評価と実行上の制約

中国語・日本語・英語の独立した架空タスク 24 件を使用。Embedding、Planner、Generator、Strict/all Verifier、独立 Judge は実 API です。Calculator は決定的な計算を行い、営業日カレンダーは明示的に Mock です。データセットは人手レビュー未実施で、以下は回帰評価の実測値であり、本番環境の正確性を保証しません。

| 指標 | ベースライン | 処理引き継ぎの最適化 | 根拠・状態管理の強化後 |
| --- | ---: | ---: | ---: |
| Task Success | 50.0% | 70.8% | 79.2% |
| Planning Success | 87.5% | 87.5% | 95.8% |
| Tool Selection Accuracy | 91.7% | 87.5% | 95.8% |
| Clarification Accuracy | 95.8% | 100.0% | 100.0% |
| Answer Correctness | 38.9% | 66.7% | 72.2% |
| Grounded Answer Rate | 38.9% | 66.7% | 72.2% |
| P50 / P95 秒 | 12.26 / 18.12 | 10.68 / 19.90 | 13.23 / 20.33 |
| Planner calls/task | 2.67 | 2.29 | 2.54 |
| Tool calls/task | 1.25 | 1.25 | 1.33 |
| USD/task | 0.002236 | 0.002147 | 0.002206 |

Answer Correctness と Grounded Answer Rate の分母は、回答可能な全タスクです。回答拒否や例外も含みます。Task Success ではツール選択と追加確認の正しさも要求します。Planner の処理引き継ぎを最適化しても ACL と Strict/all は維持しています。中間の最適化段階では P50 と費用が低下しましたが、根拠・状態管理の強化後の P50/P95 はベースラインを上回る改善にはなりませんでした。各評価で独立して回答を生成しており、確率的な変動があるため、差分をすべて処理引き継ぎの改善に帰属させることはできません。

[ベースライン](reports/agent-hardening/evaluation-baseline-live.md) · [失敗した最初の最適化](reports/agent-hardening/latency-first-attempt.md) · [処理引き継ぎの比較](reports/agent-hardening/latency-comparison.md) · [強化後の性能比較](reports/agent-hardening/latency-final-comparison.md) · [各問題の結果](reports/agent-hardening/evaluation-final-quoted-live.md) · [評価プロトコル](docs/agent-evaluation.md)。費用は設定単価による推定で、インデックス作成とオフライン Judge を除きます。中断した実行も保存し、取得できなかった使用量をゼロとは扱いません。

この段階では、追加質問を続けたタスクが 2 件、ツールの計算結果を自由に言い換えたことで保守的な根拠チェックに遮断されたタスクが 3 件残りました。Clarification Accuracy は追加確認の必要性と発生の有無だけを確認し、質問内容の質は測定しません。自動の根拠スコアも人手による正確性の保証ではありません。失敗時の原文、モデル出力、判定結果はすべて保存しています。

当該段階の CI：[success](https://github.com/Twergu/My-portfolio/actions/runs/37249750795)、バージョン `fcfb60f`。テスト件数は README に固定せず、[当該段階の全テストレポート](reports/agent-hardening/ci-final/tests.md)と [Docker 検証](reports/agent-hardening/ci-final/container-persistence.json)を参照します。

実行は 1 worker です。Agent セッションはメモリ上にのみ保持し、作成から 15 分で失効します。アクティブなタスクはユーザーごとに最大 4 件、プロセス全体で最大 100 件で、再起動後はやり直しが必要です。現在のツールは読み取り専用です。制度に関する結論には、状態・日付が適用条件を満たす文書の引用が必要です。未分類の文書は制度上の状態を先に確認する必要があります。詳細とキャンセルの挙動は[実行上の制約](docs/agent-runtime.md)、変更・失敗・テストは [Modification Report](docs/agent-hardening-report.md) に記載しています。
<!-- AGENT_RESULTS_END -->

<!-- V3_RESULTS_START -->
## v3 の実 API 検索・回答品質

保存した JSON に基づく結果です。test は 54 問（回答可能 42 問、回答なし 12 問）。Luna / text-embedding-3-small を使用し、独立評価の Judge は gpt-4.1 です。

| 検索方式 | Recall@1 | Recall@3 | Recall@5 | MRR | nDCG | 検索 P50/P95 秒 | エラー |
|---|---:|---:|---:|---:|---:|---:|---:|
| dense | 0.583 | 0.845 | 0.881 | 0.825 | 0.806 | 0.458/0.553 | 0 |
| hybrid | 0.631 | 0.810 | 0.881 | 0.861 | 0.818 | 0.420/0.591 | 0 |
| hybrid_reranked | 0.738 | 1.000 | 1.000 | 0.964 | 0.974 | 6.164/9.052 | 0 |

3 方式の検索レポートでは dev に出力形式エラーが 1 件あり、元の記録を保存しています。その後、上限 1 回の形式修正処理を追加しました。test の 3 方式ではエラーはありませんでした。

| エンドツーエンド RAG | 正確性 / n | 引用の根拠支持 / n | 回答拒否の正確性 | 誤拒否率 | P50/P95 秒 | USD/query |
|---|---:|---:|---:|---:|---:|---:|
| strict | 0.905 / 42 | 1.000 / 38 | 0.926 | 0.095 | 13.905/19.923 | 0.002028 |
| fast | 0.929 / 42 | 1.000 / 40 | 0.963 | 0.048 | 10.498/15.315 | 0.001694 |

エンドツーエンド RAG と検索のみの実験は別々に実行しており、順位が異なる場合があります。費用は設定単価による推定で、USD/query はインデックス作成とオフライン Judge を除きます。fast では意味的な根拠を検証する Verifier を実行しないため、自動 Judge の高得点は実行時の保護を代替できません。

選択的検証の再評価では、生成された 59 主張のうちスキップ可能なものは 0 件、Verifier の呼び出しを丸ごと省略できる回数も 0 回でした。固定した回答候補に対するオフラインの方針検証であり、新たな API レイテンシ実験ではありません。

この段階で追跡できる実験費用の小計は USD 0.662463 です。それ以前に中断した実行の使用量は不明のため、この小計を請求総額とは扱えません。

データセットは人手レビュー未実施です。結果はこの合成回帰セットに限られます。問題ごとの原文、tokens、段階別所要時間、失敗、単価は [v3 JSON](reports/v3/summary.json) に保存しています。
<!-- V3_RESULTS_END -->

ここでの「誤拒否率」は、回答可能な問題に回答を返せなかった割合を表し、誤った候補を正しく遮断したケースも含みます。Verifier の誤判定率と同義ではありません。Judge が税額に関する限定条件を見落とした例や、追加の正しい説明を誤判定した例もあります。[事例別の診断](reports/v3/grounding-diagnostics.md)を参照してください。

モデル設定で `retrieval_mode=hybrid`、`candidate_k=20`、`reranker_mode=llm` を選ぶと再ランキングが有効になります。独立した `reranker_model` も指定できます。通常設定の既定値は費用を抑える Dense / 再ランキングなしで、データベース検索は引き続き Exact が既定です。`strict + all` はすべての主張を検証し、`selective` でスキップした主張は常に未検証と表示します。

文書情報パネルでは制度の状態、バージョン、部門、有効期間を編集できます。質問入力欄の上部には検索フィルターがあります。複数ユーザーで利用する場合は、[ACL の設定手順](docs/access-control.md)に従って `RAG_AUTH_MODE=required` を有効にしてください。local 開発モードは認証の代わりにはなりません。

## エンジニアリング検証と過去のベースライン

テスト、CI、Docker、Vector Benchmark の表は、対象バージョンを明記した実行スナップショットです。以下の Dense RAG、Chunk、off/fast/strict は過去のベースラインを保持しており、最新の Agent データは冒頭に掲載しています。Hybrid / Reranker の比較は v3 の結果、各変更の詳細は[変更報告](docs/retrieval-optimization-report.md)を参照してください。8 件の Agent 回答候補は人手レビュー済みですが、RAG / Agent の全評価セットは人手レビュー未実施です。業務操作の Human-in-the-loop は引き続き保留し、Agent は読み取り専用ツールのみを使用します。

<!-- EXPERIMENT_RESULTS_START -->
| 項目 | 実測結果と範囲 |
|---|---|
| ローカルテスト | passed。件数と実行時刻は[生成レポート](reports/tests.md)を参照 |
| CI / PostgreSQL テスト | success。[検証実行](https://github.com/Twergu/My-portfolio/actions/runs/35040708976)、バージョン `4ce795f`。[データベーステストレポート](reports/ci/tests.md) |
| 高難度セット / ローカル検索 | policy-challenge-v2.1。test Recall@1/3/5 = 0.5873 / 0.7500 / 0.8611、MRR=0.8302、nDCG=0.7819 |
| Chunk 実験 | 6 設定を比較。dev で選択した 450/0 はローカルベースラインにのみ適用。[全結果](reports/chunks-v2/chunk-experiment-local.md) |
| 1,000 chunks / exact | measured：P50/P95 = 2.3311/2.3804 ms、Recall@5=1.0000 |
| 1,000 chunks / hnsw | measured：P50/P95 = 2.7179/3.3895 ms、Recall@5=1.0000 |
| 10,000 chunks / exact | measured：P50/P95 = 8.3276/9.7683 ms、Recall@5=1.0000 |
| 10,000 chunks / hnsw | measured：P50/P95 = 3.4084/3.5676 ms、Recall@5=0.6000 |
| 100,000 chunks / exact | measured：P50/P95 = 91.4987/105.9707 ms、Recall@5=1.0000 |
| 100,000 chunks / hnsw | measured：P50/P95 = 7.2535/8.1185 ms、Recall@5=0.1500 |
| Vector Benchmark | [ハードウェア、手法、構築時間、インデックスサイズ](reports/vector-scale.md)。合成ベクトル、単一クライアント、ウォームキャッシュでの測定であり、意味検索の品質を表すものではありません |
| SQLite vs pgvector / 1k | P50 ms：sqlite_exact 132.0714 / pgvector_exact 2.3453 / pgvector_hnsw 2.7563。[比較レポート](reports/store-benchmark.md) |
| Docker | passed：App + pgvector、PDF インデックスと引用、アプリ再起動後の永続性。[検証データ](reports/ci/container-persistence.json) |
| 実 API フロー | passed：PDF → Embedding → 構造化回答 → 原文・主張の検証 → 物理ページ引用。[実 API スモークテスト](reports/live-api-smoke.md) |

上記データは JSON の実行スナップショットから集計したものです。既存の集計コマンドは `python -m scripts.results_summary` です（再生成部分は中国語出力）。テスト件数は常に自動生成レポートを参照します。ローカルのハッシュ検索スコアは、実モデルの正確性と同じではありません。

| 実 API による RAG テストセット | 実測結果 |
|---|---|
| バージョン / 範囲 | policy-challenge-v2.1、54 問、gpt-5.6-luna / verifier gpt-5.6-luna。[問題別の全結果](reports/chunks-api/chunk-api-selected-test.md) |
| Recall@1/3/5 | 0.5833 / 0.8452 / 0.8810 |
| MRR / nDCG | 0.8254 / 0.8055 |
| Correctness / Citation Groundedness / Refusal Accuracy | 0.8333 / 1.0000 / 0.8519 |
| Quote mismatch / Unsupported / False refusal | 0.0000 / 0.0556 / 0.1667 |
| Query P50 / P95 | 5426.1470 / 9751.6545 ms、2 workers、追加 Judge を除く |
| 平均アプリケーション cost/query | USD 0.00081014 |
| 実験・追加評価の費用 | [分割設定の比較](reports/chunks-api/chunk-experiment-api.md)、[検証モード](reports/verification/comparison.md)。Judge はユーザーの query 費用に含めません |

回答の正確性と引用による支持度は、別々の独立 Judge 呼び出しで採点します。引用評価には gold evidence を見せません。各指標の分母と制約は評価プロトコルを参照してください。合成セットでの 1 回の結果だけでは不十分で、実資料と人手による確認が必要です。
実 API の開発セットでは **900/0** を凍結設定として選択しました。900/1200 系の 4 設定は同一のテキスト境界になっており、単発のスコア差だけで分割の効果は証明できません。[境界分析と費用台帳](reports/api-results.md)を参照してください。ローカルデモでは凍結設定を使用していますが、コードの汎用的な既定値は対象文書での検証が必要です。

| 検証モード（同じ test セット） | Correctness | False refusal | P50 / P95 ms | 平均 USD/query |
|---|---:|---:|---:|---:|
| off | 0.9762 | 0.0238 | 3527.5054 / 6822.6271 | 0.00057060 |
| fast | 0.9286 | 0.0238 | 3389.1299 / 6984.6610 | 0.00056931 |
| strict | 0.8333 | 0.1667 | 5426.1470 / 9751.6545 | 0.00081014 |

各モードで独立して 1 回ずつ生成しているため確率的な変動があり、同じ回答に対する因果比較とは扱えません。off/fast は実行時に意味的な根拠を保証しません。この段階の strict には誤った遮断があり、test の成績を見てプロンプトを再調整するのではなく、その制約を記録しています。
この実験段階で記録された実 API 呼び出しの推定総費用は **USD 2.084806** です。インデックス作成、追加 Judge、診断用ベースライン、追加評価を含みます。税金は含まず、請求書の代替にはなりません。
HNSW の表は ef_search=100 を使用しています。全レポートには 400/1000 の Recall とレイテンシも記載しています。既定は Exact のままとし、対象データで Recall とレイテンシの両方が要件を満たした場合にのみ HNSW へ切り替えます。CI の Docker 検証は新規 Linux runner で実施し、開発用のローカル PC には Docker をインストールしていません。
<!-- EXPERIMENT_RESULTS_END -->

## 実行・テスト状況の確認

独立 Judge も誤判定することがあります。事後の原文確認で、資料に記載のない「税抜き」を根拠ありと判定した例が見つかりました。その回答は実行時 Verifier が遮断していました。[根拠検証の判定差と反例](reports/grounding-case-review.md)を参照してください。自動の Citation Groundedness や誤拒否の診断は、人手による検収と同等ではありません。

**テスト件数は README に固定値として記載しません。** 次のコマンドを実行すると、その実行の pytest JUnit XML から[テストレポート](reports/tests.md)と [JSON データ](reports/tests.json)を生成し、成功・失敗・エラー・スキップ件数、時刻、ソースのハッシュを記録します。レポートは時刻付きの実行スナップショットであり、スキップは成功に含めません。

~~~powershell
.\.venv\Scripts\python.exe -m scripts.check
~~~

[CI](.github/workflows/ci.yml) は実 pgvector サービスでストレージの契約テストを実行し、評価・データベースのベンチマークレポートを生成し、Compose をビルド・起動してヘルスチェックを検証します。ワークフローが存在するだけで、未実行の検証が通過したとは扱いません。

各実測結果は[分割実験](reports/chunks-v2/chunk-experiment-local.md)、[データベースベンチマーク](reports/store-benchmark.md)、[実 API の状況](reports/live-api-smoke.md)を参照してください。認証情報やデータベース環境が不足する場合は blocked と明記し、模擬結果を実測値の代わりにはしません。

## ローカル起動

Python 3.11 以降が必要です。フロントエンドは標準の HTML / JavaScript / CSS で、ビルドは不要です。

~~~powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe run.py
~~~

環境を作成済みの場合は `start.ps1` を実行できます。同じ PC で[アプリ](http://127.0.0.1:8000/)を開き、ターミナルを起動したままにしてください。ポート使用中の場合は `run.py --port 8001` を使えます。`127.0.0.1` はアクセスする PC 自身のアドレスです。macOS / Linux では対応するコマンドを `.venv/bin/python` で実行してください。ロックファイルには実行・テスト用の依存関係が含まれます。

既定は SQLite + ローカル原文検索で、API は不要です。語彙のハッシュベクトルを用いて原文を直接返し、AI 回答は生成しません。`RAG_DATABASE_URL` を設定すると PostgreSQL を使用します。AI 質問応答モードでは実 Embedding と LLM を呼び出します。

## 使い方と日本語対応

1. 「ドキュメント」で PDF をアップロードするか、サンプルの社員ハンドブックを取り込みます。複数選択、ドラッグ＆ドロップ、重複排除、再処理、削除に対応しています。
2. 資料の準備完了後、「ナレッジ Q&A」で検索範囲を選択して質問します。引用をクリックすると抜粋と PDF の実際のページを確認できます。
3. 上部バーまたはモデル設定から「日本語」に切り替えられます。選択は現在のブラウザーに保存します。日本語 UI は `language: "ja"` を送信するため、漢字だけの質問でも日本語での回答を指定します。API は `zh`、`ja`、`en` を受け付けます。

テキスト層のある日本語 PDF と、漢字・ひらがな・カタカナの検索に対応しています。AI の日本語品質は設定したモデルに依存します。スキャン資料には別途 OCR が必要で、複数段組みや表の抽出品質は元の文書に左右されます。通常のナレッジ Q&A は毎回独立して検索します。Agent は追加情報を待っている間、元のタスクを継続できます。ページ再読み込みで会話やタスク ID は保持されず、サーバー側のタスクの保持期限は作成から最大 15 分です。

## モデル API の設定と実 API 検証

[.env.example](.env.example) を `.env` にコピーするか、Web 画面のモデル設定でサービスを指定します。

~~~dotenv
RAG_MODE=api
RAG_BASE_URL=https://api.openai.com/v1
RAG_API_KEY=利用するサービスのAPIキーを入力
RAG_CHAT_MODEL=サービスが対応する回答モデル名を入力
RAG_VERIFIER_MODEL=検証モデル名を入力（空欄なら回答モデルを再利用）
RAG_VERIFICATION_MODE=strict
RAG_EVAL_JUDGE_MODEL=独立した評価モデル名を入力
RAG_EMBEDDING_MODEL=サービスが対応するEmbeddingモデル名を入力
~~~

回答と Embedding は同じサービス URL・キーを使用します。Base URL は API のルートで、末尾に `/embeddings` や `/chat/completions` は付けません。リモートサービスは HTTPS、ローカルサービスは HTTP を使用できます。画面で入力したキーはサーバーのメモリ内にのみ保持し、ブラウザーへ返したりデータベースに保存したりしません。`.env` のキーは利用者がローカルで管理します。サービス URL を変更しても、以前のキーを新しいサービスへ引き継ぎません。画面で保存したキー以外の設定は、環境変数の既定値より優先されます。

通常の「接続テスト」は Embedding と回答 API をそれぞれ 1 回検証します。エンドツーエンドの実 API 検証は次のコマンドで実行します。

~~~powershell
.\.venv\Scripts\python.exe -m scripts.live_smoke --output reports/live-api-smoke
~~~

架空の 2 ページ PDF を生成し、独立した一時データベースでアップロード、解析、実 Embedding、検索、JSON 形式の主張生成、LLM による再検証を行い、金額と 2 ページ目の引用を確認します。キーがない場合はサービスにリクエストを送らず、blocked レポートを出力します。通過はその 1 回のエンドツーエンド検証の成功を意味し、モデル全体の品質合格を意味しません。

互換サービスは JSON object 形式の回答に対応している必要があります。通常の RAG 質問応答では、質問の Embedding、回答生成、根拠検証がサービスの規定に従って課金されます。資料のテキストは利用者が設定したサービスに送信されます。実 API による全件評価と分割実験は、明示的な `--mode api` 指定時に API を呼び出します。

## 構造化された回答拒否と根拠検証

Generator と Verifier は個別に設定できます。同じモデルを 2 回呼び出しても、似た誤りを繰り返す可能性は残ります。`off` は JSON 構造と出典番号のみを確認し、`fast` は原文抜粋の一致確認を追加します。既定の `strict` はさらに、モデルを用いて各主張の根拠を検証します。off/fast のレスポンスには意味的な根拠が未検証であることを明示し、構造化された回答拒否を正しい回答として表示しません。

モデルは `status` と `claims` を返します。各 claim は `text` と `evidence[{source_id, quote}]` を持ち、それ以外の自由記述による回答は許可しません。strict モードでは、サーバーがまず指定した出典内に抜粋が存在することを確認し、その後 1 回の検証呼び出しで各主張が原文に支持されているかを確認します。数値、条件、適用範囲、有効日、否定表現も対象です。

引用の欠落、偽の抜粋、矛盾した主張、検証結果の欠落、出力形式エラーがある回答は、そのまま表示できません。処理は `answered`、`retrieval_only`、`insufficient_evidence`、`unsupported_answer`、`invalid_model_response` で分岐し、特別な拒否文字列には依存しません。レスポンスには互換性のための `refused` フィールドと、`claims`、`support`、完全な `retrieved_sources`、`metrics` を含みます。ファイル名、物理ページ番号、原文はサーバー側で対応付けます。

自動の根拠検証にも誤判定があり、「ハルシネーションゼロ」や形式的な証明を保証するものではありません。品質の検収には、独立したデータと人手による確認が必要です。

## 評価・レイテンシ・費用

[評価プロトコル](evals/README.md)と[データセット](evals/dataset.json)には、中国語・日本語・英語の質問、ページ単位の ground truth、参照事実・回答、回答なし・プロンプトインジェクションのケースを含め、dev/test の分割と制約を明記しています。

既定の実験では[高難度セット policy-challenge-v2.1](evals/hard_dataset.json)を使用します。文書 48 件、96 ページ、108 問で、dev/test は各 54 問です。旧制度・新制度、草案、類似文書、数値の取り違え、否定、例外、複数文書にまたがる質問、回答なしを扱います。dev/test 間で会社と金額を分離し、検索範囲には競合するバージョンも同時に含めます。ただしテンプレート間の関連性は残るため、人手と実資料による拡充が必要です。

~~~powershell
.\.venv\Scripts\python.exe -m scripts.evaluate --mode local --split test --output reports/evaluation-local-test
.\.venv\Scripts\python.exe -m scripts.chunk_experiment --mode local --output-dir reports/chunks-v2
# モデルサービスの設定後、実 API 評価を実行：
.\.venv\Scripts\python.exe -m scripts.evaluate --mode api --split test --output reports/evaluation-api-test
~~~

- Retrieval：Recall@1/3/5、MRR@K、nDCG@K、Precision@K、回答なしの問題での誤検索率を測定します。実際の Chunk 件数制限を適用してから、物理ページ単位で重複を除きます。
- 回答品質：独立 Judge が reference answer / gold evidence に基づいて Answer Correctness と Citation Groundedness を採点します。Refusal Accuracy、quote の一致失敗、unsupported answer、false refusal も別途集計します。拒否された回答候補も Judge が個別に評価し、正しく根拠のある回答を Verifier が遮断したケースを検出します。これらの候補はユーザーへの回答には表示しません。
- 実行時 Verifier の通過率と独立 Judge のスコアは分けて扱います。語彙 F1 やカバレッジは代理指標にすぎません。ローカル検索は回答を生成しないため、意味的な品質は N/A です。Judge にも誤りがあるため、人手での確認が必要です。
- Latency：解析、分割、インデックス用 Embedding、データベース書き込み、質問の Embedding、検索、生成、検証、全体の所要時間を記録し、平均・p50/p95・サンプル数を集計します。入れ子の処理段階を単純に合計することはできません。
- Cost：実レスポンスの token usage、リクエスト・再試行回数を記録し、設定単価から推定します。使用量または単価が不足する場合は不明とします。失敗したリクエストと検証リクエストも含めます。

`.env` で 100 万 token あたりの米ドル単価を設定します。空欄は不明を意味します。サービスやモデルを変更した場合は単価も更新してください。

~~~dotenv
RAG_EMBEDDING_USD_PER_MILLION_TOKENS=
RAG_CHAT_INPUT_USD_PER_MILLION_TOKENS=
RAG_CHAT_OUTPUT_USD_PER_MILLION_TOKENS=
RAG_VERIFIER_INPUT_USD_PER_MILLION_TOKENS=
RAG_VERIFIER_OUTPUT_USD_PER_MILLION_TOKENS=
RAG_JUDGE_INPUT_USD_PER_MILLION_TOKENS=
RAG_JUDGE_OUTPUT_USD_PER_MILLION_TOKENS=
~~~

回答の下で性能・使用量の詳細を表示できます。`GET /api/metrics` は現在のプロセスの直近の操作を返します。計測値はローテーションログ `data/logs/service.log` にも保存します。ログには実際の例外スタック、文書 ID、処理段階、インデックス識別子を記録し、PDF 解析サブプロセスの失敗スタックも残します。

実験レポートでは通常の query cost と追加 Judge の費用を分け、token usage、平均 cost/query、P50/P95 を出力します。モデルごとに対応する単価を使用しますが、標準単価による推定であり、キャッシュ割引はまだ反映しません。3 種類の検証モードを比較する有料実験は `python -m scripts.verification_experiment --run-api` で実行します。評価プロトコルでは、正確性 Judge と引用 Judge の入力を分離し、引用されていない参照根拠で引用の支持度を補わないようにしています。

## Chunk 分割実験と物理ページ境界

サイズの単位は文字数です。既定値は size=900、overlap=120 で、Web 画面から変更できます。overlap は size 未満である必要があります。これらの値はインデックス識別子に含まれるため、変更後は再構築が必要です。古いインデックスが新しい設定の検索に混入することはありません。

比較する設定は (450,0)、(450,60)、(900,0)、(900,120)、(1200,120)、(1200,180) です。API モードでは dev の Answer Correctness を優先し、その後に Recall / nDCG / Chunk 数を比較します。local モードは検索成績のみで選択します。評価用 Chunk ID を固定し、同点時の順位がランダム ID に左右されるのを防ぎます。選択した設定を凍結して最後に test を実行し、test の結果で調整しません。[ローカル高難度セットの結果](reports/chunks-v2/chunk-experiment-local.md)はローカルベースラインにのみ適用します。実 API の選択結果は上記の評価表を参照してください。

**各 Chunk は物理ページをまたがない設計を維持しています。** 理由、トレードオフ、拡張方針は [ADR 0001](docs/adr/0001-physical-page-chunks.md) を参照してください。複数ページにまたがる質問では、複数ページを検索し、同じ主張に複数の出典を付けられます。

## PostgreSQL + pgvector と移行

`RAG_DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE` を設定すると、設定・文書・Chunk・ネイティブ vector の保存先に PostgreSQL を使用し、データベース接続プールを再利用します。PDF 原本は `RAG_DATA_DIR/files/` に保存します。SQLite はオフライン開発と比較用ベースラインとして残しています。

既定は exact cosine 検索です。`RAG_SEARCH_MODE=hnsw` または Web 画面で HNSW を選ぶと近似検索を使用できます。現在の HNSW は vector 型を使い、最大 2,000 次元に対応します。PostgreSQL と API モードが必要です。ローカルの 2,048 次元ベクトルは exact を使用し、暗黙の切り詰めや精度低下は行いません。モデル・profile・次元を分離しています。

HNSW インデックスは、インデックス書き込みトランザクション、起動、設定のメンテナンス時に作成します。ユーザーの検索時に CREATE INDEX は実行しません。最後の文書が新しい profile に再構築された場合や削除された場合、不要なインデックスを削除します。メンテナンスの対象は本アプリ専用の名前空間に限定し、データベースの advisory lock で操作を直列化します。

既存の SQLite は自動移行しません。先にアプリを停止し、データベースと PDF をバックアップしたうえで、移行先データベースとファイルディレクトリが空の状態で実行してください。

~~~powershell
.\.venv\Scripts\python.exe -m scripts.migrate_sqlite --source data --target-data-dir pgdata
# 上のコマンドは検証のみ。RAG_DATABASE_URL の設定後、明示的に移行を実行：
.\.venv\Scripts\python.exe -m scripts.migrate_sqlite --source data --target-data-dir pgdata --apply
~~~

SQLite の整合性、PDF のサイズ・SHA-256、Chunk の件数・次元・ページ番号を検証します。移行元は読み取り専用で、移行先のトランザクションに失敗した場合はロールバックします。成功後は `RAG_DATA_DIR` を移行先ディレクトリに設定してください。Docker への移行では対応するファイルディレクトリをアプリのデータボリュームにマウントし、データベースと PDF は必ず同じ移行で得たものを使用します。

データベースベンチマークは同じ seed・ベクトル・クエリを使い、モデル呼び出し時間を除外します。ウォームアップ後の p50/p95、インデックス構築時間、独立した exact 参照に対する Recall を記録します。

~~~powershell
# RAG_BENCHMARK_DATABASE_URL に、隔離 schema を作成できる pgvector データベースを指定
.\.venv\Scripts\python.exe -m scripts.benchmark_stores --count 1000 --dimensions 384 --queries 20 --repeats 3
.\.venv\Scripts\python.exe -m scripts.benchmark_scale --sizes 1000 10000 100000 --dimensions 384 --queries 20 --repeats 3
~~~

作成・削除するのは、その実行で作成したランダムな schema のみです。データベース未設定でも SQLite は測定し、PostgreSQL は blocked と明示します。両方を測定せずに性能向上を主張しません。実際のモデル次元、より大きな規模、同時アクセスは別途測定が必要です。

## Docker

利用可能な Docker Engine / Compose が必要です。新しくクローンした環境では `.env` や API キーなしで `docker compose up` を実行すると、ローカル検索用 App + PostgreSQL + pgvector が起動します。初回起動時にランダムなデータベースパスワードを生成して専用の永続ボリュームに保存し、再起動時には再利用します。AI モードを使用する場合は [.env.example](.env.example) に従って追加設定してください。

~~~powershell
docker compose up --build -d --wait
docker compose logs -f app
~~~

[アプリ](http://127.0.0.1:8000/)を開いてください。Compose は app と pgvector データベース、ヘルスチェック、独立した永続ボリューム、非 root のアプリユーザー、単一のインデックス処理プロセスを提供します。ホスト上のアプリポートはループバックアドレスにのみ公開し、データベースはホストへ直接公開しません。

起動中の Compose でデータベースベンチマークを実行し、レポートを取得するには、次のコマンドを使います。

~~~powershell
docker compose exec app python -m scripts.benchmark_scale --database-url-env RAG_DATABASE_URL
docker compose cp app:/app/reports/vector-scale.json reports/vector-scale.json
docker compose cp app:/app/reports/vector-scale.md reports/vector-scale.md
~~~

`docker compose down` で停止しても、名前付きデータボリュームは保持されます。既定の `RAG_AUTH_MODE=local` は単一ユーザーの開発モードです。`required` を設定し、ユーザートークンを発行すると ACL が有効になります。[ユーザーと権限の設定](docs/access-control.md)を参照してください。公開用 HTTPS は別の `compose.demo.yaml` で対応しており、[デプロイ手順](docs/portfolio-sharing.md)に従って設定します。SSO、ユーザー監査、分散タスクは未実装です。

## 現在の制約

PDF 1 件あたりの上限は 20 MB、200 ページ、100 万文字、2,000 Chunk です。ライブラリ全体では最大 100 文書です。インデックス作成は単一 worker で行い、PDF はサブプロセスで解析し、45 秒でタイムアウトします。OCR、永続的な会話メモリ、SSO、本番環境の品質保証は含みません。OneDrive などの同期ディレクトリ内に保存したファイルは、その同期ソフトウェアによって同期される場合があります。

API ドキュメント：[OpenAPI](http://127.0.0.1:8000/docs)。実装の詳細と公式 API 資料への参照は [Architecture](docs/architecture.md) に記載しています。
