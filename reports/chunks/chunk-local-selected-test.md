# RAG 評価：aster-synthetic-v1

モード：**local**; 分割：**test**; クエリ数：12.

合成した種データのみを使用します。この結果は本番の正確性を保証しません。

| 検索指標（回答可能な問題のマクロ平均） | 平均 | n |
|---|---:|---:|
| recall_at_k | 1.0000 | 9 |
| precision_at_k | 0.2667 | 9 |
| mrr_at_k | 0.8056 | 9 |
| ndcg_at_k | 0.8547 | 9 |

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
| query_embedding | 0.2365 | 0.2779 | 12 |
| retrieval | 3.0605 | 3.3813 | 12 |
| question_total | 9.3126 | 9.9711 | 12 |

索引作成：17 chunks, 65.09 ms.
実行全体の API 費用 (USD)：0.0000。使用量不明や単価未設定は null/N/A を保持します。

逐次で 1 回実行し、事前実行や同時実行はありません。時間は推定ではなく実測です。

## 問題ごとの結果

| ID | 分類 | 状態 | Recall@k | 参照事実の語彙カバレッジ | 合計 ms |
|---|---|---|---:|---:|---:|
| en-09 | direct | retrieval_only | 1.0000 | N/A | 10.21 |
| en-10 | cross_page | retrieval_only | 1.0000 | N/A | 9.21 |
| en-11 | negative | retrieval_only | N/A | N/A | 9.37 |
| en-12 | adversarial | retrieval_only | 1.0000 | N/A | 9.09 |
| zh-09 | direct | retrieval_only | 1.0000 | N/A | 9.54 |
| zh-10 | cross_page | retrieval_only | 1.0000 | N/A | 9.19 |
| zh-11 | negative | retrieval_only | N/A | N/A | 9.18 |
| zh-12 | adversarial | retrieval_only | 1.0000 | N/A | 9.25 |
| ja-09 | direct | retrieval_only | 1.0000 | N/A | 9.69 |
| ja-10 | cross_page | retrieval_only | 1.0000 | N/A | 9.78 |
| ja-11 | negative | retrieval_only | N/A | N/A | 8.96 |
| ja-12 | adversarial | retrieval_only | 1.0000 | N/A | 9.38 |

## 制約

- 人手レビューと、代表的な未使用 PDF による拡充が必要です。
- パーサー出力を入口とし、OCR/PDF 抽出はこのデータで測定しません。
- test は Chunk 選択に使いませんが、dev と制度の主題を共有します。
- 翻訳した主題は統計的に独立した標本ではありません。
