# RAG 評価データセットと指標の定義

既定は `hard_dataset.json` で、`python -m evals.make_hard` により再構築します。`policy-challenge-v2.1` は架空制度 48 件、物理ページ 96 枚、中国語・日本語・英語の質問 108 問、dev/test 各 54 問です。組織名と金額を dev/test で分けますが、検索範囲には両組織、旧版、現行版、草案、契約社員の制度を残し、妨害文書を事前除外しません。旧 `dataset.json` は回帰用の 36 問の種セットです。

各問は質問、言語、分類、検索範囲、`answerable`、ページ単位の `relevance`、`reference_answer`、`reference_evidence` を持ちます。新旧版、類似制度、数値の罠、否定、例外、複数文書、回答なし、プロンプト注入を含みます。高難度セットは数値別名一致を回答正確性の代用にしません。v2.1 は英語の参照回答が gold ページを超える事実を修正し、承認ルールを分けて、複数文書問題が 1 文書だけで解けないようにしました。ページテキストは PDF 解析後から扱い、アップロードと解析は別 smoke で検証します。

## Retrieval 指標

実際に返った Top-K Chunk を切り出し、`(document_id, page)` の初出順で重複を除きます。Recall@1/3/5 を個別に報告し、MRR@K と nDCG@K は指定 K（既定 5）を使います。重複ページの代わりに上限外のページを補いません。未充足の枠も precision の分母に含めます。

| 指標 | 定義 |
| --- | --- |
| Recall@K | ヒットした異なる関連ページ数 / 全関連ページ数 |
| Precision@K | ヒットした異なる関連ページ数 / K |
| MRR@K | 最初の関連ページの順位の逆数。未ヒットは 0 |
| nDCG@K | 利得 `2^grade - 1`、割引 `log2(rank+1)` による DCG / 理想 DCG |
| 回答なしの誤検索率 | 回答なしの問題で 1 ページ以上返した割合。独立に表示 |

回答なしでは Recall/Precision/MRR/nDCG は適用外で、満点と扱いません。集計は適用可能な問題のマクロ平均と件数です。ページの再現率は各事実の取得を保証せず、回答と抜粋は別途検証します。

## 回答品質

| 指標 | 定義と制約 |
| --- | --- |
| Answer Correctness | 別設定の Evaluation Judge が質問・参照回答・gold evidence から正確性と完全性を評価。回答可能でも未回答は 0 |
| Citation Groundedness | 実引用が各主張を支持するか独立 Judge で確認し、抜粋一致も別検証。実行時 Verifier の通過状態を引き継がない |
| Refusal Accuracy | 回答可能な問題で回答し、回答なしで構造化拒否する割合。拒否の判断のみで、回答内容の評価ではない |
| quote_match_failure / unsupported_answer | 抜粋不一致の割合 / 根拠チェックによる遮断の割合 |
| grounding_rejected_correct_and_grounded | 遮断候補のうち Judge が正確かつ根拠ありとした割合。候補数を併記し、誤遮断の発見に使う |
| Expected facts coverage | 参照事実の別名が回答に現れる割合。語彙の代理指標で、数値一致は意味的正確性を保証しない |
| Reference token F1 | 参照・生成回答の token 重複 F1。中国語・日本語は文字、英語は単語 |
| Reference exact match | 正規化した token 列の一致。すべての言い換えを正しく評価できるわけではない |
| Correct refusal | 回答なしに構造化 `insufficient_evidence` を返したか。形式不正・根拠検証失敗は正しい拒否に含めない |
| False refusal | 回答可能な問題で根拠検証済みの回答を出せなかったか。遮断候補も含む |
| Claim groundedness | 遮断された候補を含む全候補主張のうち、根拠チェックを通過した割合 |
| All claims grounded | その問題の候補主張がすべて支持されたか |

local は原文のみなので回答品質は N/A。実行時 `claim_groundedness` は Verifier 診断値で、off/fast が意味検証しない場合は不明です。独立 `citation_groundedness` は追加 Judge の値で、人手ラベルではありません。遮断候補は明示的な内部評価にのみ使い、公開回答へ返しません。Judge 未設定、呼び出し失敗、不完全な結果を完全な品質検収とは扱いません。Judge も誤るため、公開前に人手で標本確認が必要です。

`false_refusal` は回答可能でも未回答となった割合で、Verifier 自体の誤判定率ではありません。生成器が根拠のない限定表現を追加し、正しく遮断された場合も含みます。v3 では Judge による税の限定表現の見逃しと、不完全な gold ページにより正しい補足を誤判定する例がありました。元スコアを維持し、[不一致診断](../reports/v3/grounding-diagnostics.md)に記録しています。

## Latency と Cost

indexing、query embedding、retrieval、generation、verification、provider HTTP、バックオフ、問題全体を実測し、p50/p95/平均/件数を集計します。段階は入れ子で、すべてを加算できません。token usage は実サービス応答から取得し、`.env` の 100 万 token あたり単価で費用を推定します。生成と根拠検証の両 LLM 呼び出しを含めます。

query と追加 Judge の費用は分離し、run cost は索引・質問応答・Judge を含みます。API 未使用なら 0、usage 欠落・失敗費用不明・単価不足なら合計は null/N/A とし、既知部分を保持します。キャッシュ割引、税、サービス階層の差は含まず、請求書の代わりにはなりません。

## 実行

```powershell
.\.venv\Scripts\python.exe -m scripts.evaluate --mode local --split test --output reports/evaluation-local-test
.\.venv\Scripts\python.exe -m scripts.chunk_experiment --mode local --output-dir reports/chunks-v2
```

実評価はキー、サービス、Generator/Verifier、`RAG_EVAL_JUDGE_MODEL`、単価を設定し、明示的に `--mode api` を使います。3 モード比較は `python -m scripts.verification_experiment --run-api`。有料 API を呼び出すコマンドで、2026-09-15 の利用枠追加後に再開しました。既定 local は API を呼びません。隔離一時 SQLite を使いアプリのナレッジベースは変更せず、保存性能は別の pgvector 比較で評価します。

正式プロトコル `isolated-correctness-and-citations-v2` は 2 Judge リクエストを分離します。正確性は参照回答・gold evidence、引用支持は質問・実引用だけを見ます。未引用の根拠を流用せず、実行時 Verifier 状態も入力しません。旧単一 Judge は診断と発生費用の記録のみで、正式な設定選択に使いません。

`--concurrency 2` は独立指標を持つ問題 worker を 2 個使い、並列数を記録します。アプリ時間は待ち行列と追加 Judge を除外。Chunk/Verification の `--resume` は、データハッシュ、設定、Embedding profile、採点方式、Judge、並列数が一致する完了済み結果だけを再利用します。変更時は別の出力先が必要です。

Judge の JSON/schema や主張番号が不完全なら、最大 1 回の形式再試行を行います。欠落 verdict を通過としません。全試行の token/cost を残し、`validation_failures` に段階と回数を記録しますが、元の不正応答は保存しません。正確性と引用の入力分離は維持し、再試行に期待スコアは渡しません。合成データの `evaluation_trace` を保存して再確認可能にします。実企業資料では、原文を含む実験ファイルも資料のアクセス要件に従って管理してください。

`900/0 dev` の Judge 形式エラー 1 件は元の回答だけ再評価し、回答生成と検索は再実行しませんでした。失敗スナップショットは `reports/judge-recovery/`、正式結果の `judge_replays` に追加評価を記録しています。正式費用は元の失敗分を含むため、スナップショット分を重複加算しません。

6 設定は `(450,0)`、`(450,60)`、`(900,0)`、`(900,120)`、`(1200,120)`、`(1200,180)`。文字数単位で物理ページをまたぎません。API は dev Answer Correctness、Recall、nDCG、Chunk 数の少なさの順、local は検索指標のみで選択し、凍結後に test を実行します。test に合わせて調整しません。一部ページは設定より短く 900/1200 の境界が同じなので、長い実ページで検証が必要です。ルール・翻訳には関連性があり、独立した人手検収は未実施。本番の正確性の主張や自動の設定変更はしません。

[高難度 Chunk 実験](../reports/chunks-v2/chunk-experiment-local.md)、[凍結設定の test](../reports/chunks-v2/chunk-local-selected-test.md)、[実 API の状態](../reports/live-api-smoke.md)を参照してください。
