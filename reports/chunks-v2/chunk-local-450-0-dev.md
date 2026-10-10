# RAG 評価：policy-challenge-v2.1

モード：**local**; 分割：**dev**; クエリ数：54.

実行状態：completed; 要求問題数：54; 索引エラー：none.

合成した種データのみを使用します。この結果は本番の正確性を保証しません。

| 検索指標（回答可能な問題のマクロ平均） | 平均 | n |
|---|---:|---:|
| recall_at_1 | 0.5675 | 42 |
| recall_at_3 | 0.7262 | 42 |
| recall_at_5 | 0.8690 | 42 |
| mrr_at_k | 0.8004 | 42 |
| ndcg_at_k | 0.7713 | 42 |
| precision_at_k | 0.2429 | 42 |

返された Chunk の上限内でページの重複を除去します。precision の分母は未充足枠も含む k です。

| 回答指標 | 平均 | n |
|---|---:|---:|
| all_claims_grounded | N/A | 0 |
| answer_correctness | N/A | 0 |
| citation_groundedness | N/A | 0 |
| claim_groundedness | N/A | 0 |
| correct_refusal | N/A | 0 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | N/A | 0 |
| generator_false_refusal | N/A | 0 |
| grounding_false_refusal | N/A | 0 |
| invalid_model_response | N/A | 0 |
| quote_match_failure | N/A | 0 |
| reference_exact_match | N/A | 0 |
| reference_token_f1_lexical | N/A | 0 |
| refusal_accuracy | N/A | 0 |
| unsupported_answer | N/A | 0 |

local は回答を生成しないため回答品質は N/A。語彙カバレッジ / token F1 は意味的正確性を証明しません。実行時 claim_groundedness は Verifier 診断値、answer_correctness と citation_groundedness は別設定の評価 Judge の自動判定で、人手ラベルではありません。

| 所要時間 (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| query_embedding | 0.3760 | 0.5725 | 54 |
| retrieval | 12.7490 | 15.9325 | 54 |
| question_total | 23.8827 | 27.0414 | 54 |

索引作成：100 chunks, 1520.85 ms.
実行全体の API 費用 (USD)：0.0000。使用量不明や単価未設定は null/N/A を保持します。

アプリ平均 USD/query：0.0000; 報告された tokens：{'embedding_tokens': 0, 'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0, 'complete': True}.
独立評価：{'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'not_applicable', 'judge_cost_usd': 0.0, 'judge_errors': 0}。Judge の時間・費用はアプリ query の指標から除外します。
逐次で 1 回実行し、事前実行や同時実行はありません。時間は推定ではなく実測です。

## 問題ごとの結果

| ID | 分類 | 状態 | Recall@k | 参照事実の語彙カバレッジ | 合計 ms |
|---|---|---|---:|---:|---:|
| aster-en-01 | current_version | retrieval_only | 0.0000 | N/A | 25.42 |
| aster-en-02 | old_version | retrieval_only | 1.0000 | N/A | 24.50 |
| aster-en-03 | similar_document | retrieval_only | 1.0000 | N/A | 24.08 |
| aster-en-04 | numeric_trap | retrieval_only | 1.0000 | N/A | 26.11 |
| aster-en-05 | negation | retrieval_only | 1.0000 | N/A | 22.66 |
| aster-en-06 | exception | retrieval_only | 1.0000 | N/A | 22.18 |
| aster-en-07 | exception_denied | retrieval_only | 0.5000 | N/A | 22.16 |
| aster-en-08 | negation | retrieval_only | 1.0000 | N/A | 21.82 |
| aster-en-09 | cross_document | retrieval_only | 0.6667 | N/A | 23.06 |
| aster-en-10 | cross_document | retrieval_only | 1.0000 | N/A | 22.14 |
| aster-en-11 | similar_document | retrieval_only | 1.0000 | N/A | 21.40 |
| aster-en-12 | draft_trap | retrieval_only | 1.0000 | N/A | 23.31 |
| aster-en-13 | negative | retrieval_only | N/A | N/A | 22.62 |
| aster-en-14 | negative | retrieval_only | N/A | N/A | 21.65 |
| aster-en-15 | negative | retrieval_only | N/A | N/A | 21.04 |
| aster-en-16 | adversarial | retrieval_only | N/A | N/A | 17.88 |
| aster-en-17 | negation | retrieval_only | 1.0000 | N/A | 23.67 |
| aster-en-18 | cross_document | retrieval_only | 1.0000 | N/A | 22.27 |
| aster-zh-01 | current_version | retrieval_only | 1.0000 | N/A | 24.29 |
| aster-zh-02 | old_version | retrieval_only | 1.0000 | N/A | 22.91 |
| aster-zh-03 | similar_document | retrieval_only | 1.0000 | N/A | 24.26 |
| aster-zh-04 | numeric_trap | retrieval_only | 0.0000 | N/A | 22.13 |
| aster-zh-05 | negation | retrieval_only | 1.0000 | N/A | 24.10 |
| aster-zh-06 | exception | retrieval_only | 1.0000 | N/A | 24.63 |
| aster-zh-07 | exception_denied | retrieval_only | 1.0000 | N/A | 26.11 |
| aster-zh-08 | negation | retrieval_only | 1.0000 | N/A | 24.71 |
| aster-zh-09 | cross_document | retrieval_only | 0.6667 | N/A | 28.15 |
| aster-zh-10 | cross_document | retrieval_only | 1.0000 | N/A | 24.20 |
| aster-zh-11 | similar_document | retrieval_only | 1.0000 | N/A | 25.33 |
| aster-zh-12 | draft_trap | retrieval_only | 0.5000 | N/A | 23.29 |
| aster-zh-13 | negative | retrieval_only | N/A | N/A | 22.66 |
| aster-zh-14 | negative | retrieval_only | N/A | N/A | 24.91 |
| aster-zh-15 | negative | retrieval_only | N/A | N/A | 17.93 |
| aster-zh-16 | adversarial | retrieval_only | N/A | N/A | 19.21 |
| aster-zh-17 | negation | retrieval_only | 1.0000 | N/A | 24.53 |
| aster-zh-18 | cross_document | retrieval_only | 1.0000 | N/A | 23.69 |
| aster-ja-01 | current_version | retrieval_only | 1.0000 | N/A | 25.06 |
| aster-ja-02 | old_version | retrieval_only | 1.0000 | N/A | 24.44 |
| aster-ja-03 | similar_document | retrieval_only | 1.0000 | N/A | 24.91 |
| aster-ja-04 | numeric_trap | retrieval_only | 0.0000 | N/A | 23.57 |
| aster-ja-05 | negation | retrieval_only | 1.0000 | N/A | 25.18 |
| aster-ja-06 | exception | retrieval_only | 1.0000 | N/A | 21.12 |
| aster-ja-07 | exception_denied | retrieval_only | 0.5000 | N/A | 24.08 |
| aster-ja-08 | negation | retrieval_only | 1.0000 | N/A | 24.63 |
| aster-ja-09 | cross_document | retrieval_only | 0.6667 | N/A | 21.98 |
| aster-ja-10 | cross_document | retrieval_only | 1.0000 | N/A | 25.21 |
| aster-ja-11 | similar_document | retrieval_only | 1.0000 | N/A | 21.76 |
| aster-ja-12 | draft_trap | retrieval_only | 1.0000 | N/A | 22.05 |
| aster-ja-13 | negative | retrieval_only | N/A | N/A | 27.34 |
| aster-ja-14 | negative | retrieval_only | N/A | N/A | 26.09 |
| aster-ja-15 | negative | retrieval_only | N/A | N/A | 28.00 |
| aster-ja-16 | adversarial | retrieval_only | N/A | N/A | 18.32 |
| aster-ja-17 | negation | retrieval_only | 1.0000 | N/A | 26.88 |
| aster-ja-18 | cross_document | retrieval_only | 1.0000 | N/A | 24.25 |

## 制約

- テンプレートを共有する多言語ケースには関連性があり、統計的に独立した標本ではありません。
- dev/test は組織名と数値を分けていますが、ルールのテンプレートは共有します。
- 参照根拠はページ単位で、検索の再現率は全事実の網羅性を保証しません。
- 代表的な実文書による人手レビューが引き続き必要です。
- ページテキストは PDF 解析後から扱います。PDF の一連の処理は live_smoke で検証します。
