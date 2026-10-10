# RAG 評価：aster-synthetic-v1

モード：**local**; 分割：**dev**; クエリ数：24.

合成した種データのみを使用します。この結果は本番の正確性を保証しません。

| 検索指標（回答可能な問題のマクロ平均） | 平均 | n |
|---|---:|---:|
| recall_at_k | 1.0000 | 18 |
| precision_at_k | 0.2000 | 18 |
| mrr_at_k | 1.0000 | 18 |
| ndcg_at_k | 1.0000 | 18 |

返された Chunk の上限内でページの重複を除去します。precision の分母は未充足枠も含む k です。

| 回答指標 | 平均 | n |
|---|---:|---:|
| all_claims_grounded | N/A | 0 |
| claim_groundedness | N/A | 0 |
| correct_refusal | N/A | 0 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | N/A | 0 |
| reference_exact_match | N/A | 0 |
| reference_token_f1_lexical | N/A | 0 |

local は回答を生成しないため回答品質は N/A。語彙カバレッジ / token F1 は意味的正確性を証明しません。Groundedness は構造化 Verifier の判定で、独立した人手ラベルではありません。

| 所要時間 (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| query_embedding | 0.2290 | 0.2471 | 24 |
| retrieval | 3.2985 | 3.7413 | 24 |
| question_total | 9.1470 | 9.6847 | 24 |

索引作成：29 chunks, 70.94 ms.
実行全体の API 費用 (USD)：0.0000。使用量不明や単価未設定は null/N/A を保持します。

逐次で 1 回実行し、事前実行や同時実行はありません。時間は推定ではなく実測です。

## 問題ごとの結果

| ID | 分類 | 状態 | Recall@k | 参照事実の語彙カバレッジ | 合計 ms |
|---|---|---|---:|---:|---:|
| en-01 | direct | retrieval_only | 1.0000 | N/A | 10.47 |
| en-02 | direct | retrieval_only | 1.0000 | N/A | 9.36 |
| en-03 | direct | retrieval_only | 1.0000 | N/A | 9.31 |
| en-04 | direct | retrieval_only | 1.0000 | N/A | 9.53 |
| en-05 | direct | retrieval_only | 1.0000 | N/A | 9.45 |
| en-06 | direct | retrieval_only | 1.0000 | N/A | 8.39 |
| en-07 | negative | retrieval_only | N/A | N/A | 8.99 |
| en-08 | adversarial | retrieval_only | N/A | N/A | 8.67 |
| zh-01 | direct | retrieval_only | 1.0000 | N/A | 8.67 |
| zh-02 | direct | retrieval_only | 1.0000 | N/A | 9.13 |
| zh-03 | direct | retrieval_only | 1.0000 | N/A | 9.01 |
| zh-04 | direct | retrieval_only | 1.0000 | N/A | 8.79 |
| zh-05 | direct | retrieval_only | 1.0000 | N/A | 8.73 |
| zh-06 | direct | retrieval_only | 1.0000 | N/A | 8.35 |
| zh-07 | negative | insufficient_evidence | N/A | N/A | 8.22 |
| zh-08 | adversarial | retrieval_only | N/A | N/A | 8.44 |
| ja-01 | direct | retrieval_only | 1.0000 | N/A | 9.16 |
| ja-02 | direct | retrieval_only | 1.0000 | N/A | 9.22 |
| ja-03 | direct | retrieval_only | 1.0000 | N/A | 9.46 |
| ja-04 | direct | retrieval_only | 1.0000 | N/A | 8.92 |
| ja-05 | direct | retrieval_only | 1.0000 | N/A | 9.33 |
| ja-06 | direct | retrieval_only | 1.0000 | N/A | 9.71 |
| ja-07 | negative | retrieval_only | N/A | N/A | 9.30 |
| ja-08 | adversarial | retrieval_only | N/A | N/A | 9.54 |

## 制約

- 人手レビューと、代表的な未使用 PDF による拡充が必要です。
- パーサー出力を入口とし、OCR/PDF 抽出はこのデータで測定しません。
- test は Chunk 選択に使いませんが、dev と制度の主題を共有します。
- 翻訳した主題は統計的に独立した標本ではありません。
