# RAG 評価：policy-challenge-v2.1

モード：**local**; 分割：**dev**; クエリ数：54.

実行状態：completed; 要求問題数：54; 索引エラー：none.

合成した種データのみを使用します。この結果は本番の正確性を保証しません。

| 検索指標（回答可能な問題のマクロ平均） | 平均 | n |
|---|---:|---:|
| recall_at_1 | 0.5794 | 42 |
| recall_at_3 | 0.7262 | 42 |
| recall_at_5 | 0.8611 | 42 |
| mrr_at_k | 0.8123 | 42 |
| ndcg_at_k | 0.7717 | 42 |
| precision_at_k | 0.2381 | 42 |

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
| query_embedding | 0.3880 | 0.7285 | 54 |
| retrieval | 14.2315 | 20.6398 | 54 |
| question_total | 23.6963 | 30.7494 | 54 |

索引作成：100 chunks, 1247.71 ms.
実行全体の API 費用 (USD)：0.0000。使用量不明や単価未設定は null/N/A を保持します。

アプリ平均 USD/query：0.0000; 報告された tokens：{'embedding_tokens': 0, 'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0, 'complete': True}.
独立評価：{'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'not_applicable', 'judge_cost_usd': 0.0, 'judge_errors': 0}。Judge の時間・費用はアプリ query の指標から除外します。
逐次で 1 回実行し、事前実行や同時実行はありません。時間は推定ではなく実測です。

## 問題ごとの結果

| ID | 分類 | 状態 | Recall@k | 参照事実の語彙カバレッジ | 合計 ms |
|---|---|---|---:|---:|---:|
| aster-en-01 | current_version | retrieval_only | 0.0000 | N/A | 21.79 |
| aster-en-02 | old_version | retrieval_only | 1.0000 | N/A | 19.97 |
| aster-en-03 | similar_document | retrieval_only | 1.0000 | N/A | 20.23 |
| aster-en-04 | numeric_trap | retrieval_only | 1.0000 | N/A | 23.66 |
| aster-en-05 | negation | retrieval_only | 1.0000 | N/A | 27.33 |
| aster-en-06 | exception | retrieval_only | 1.0000 | N/A | 25.47 |
| aster-en-07 | exception_denied | retrieval_only | 0.5000 | N/A | 30.20 |
| aster-en-08 | negation | retrieval_only | 1.0000 | N/A | 30.11 |
| aster-en-09 | cross_document | retrieval_only | 0.3333 | N/A | 25.12 |
| aster-en-10 | cross_document | retrieval_only | 1.0000 | N/A | 24.31 |
| aster-en-11 | similar_document | retrieval_only | 1.0000 | N/A | 23.23 |
| aster-en-12 | draft_trap | retrieval_only | 1.0000 | N/A | 20.60 |
| aster-en-13 | negative | retrieval_only | N/A | N/A | 21.56 |
| aster-en-14 | negative | retrieval_only | N/A | N/A | 19.74 |
| aster-en-15 | negative | retrieval_only | N/A | N/A | 18.55 |
| aster-en-16 | adversarial | retrieval_only | N/A | N/A | 17.52 |
| aster-en-17 | negation | retrieval_only | 1.0000 | N/A | 22.95 |
| aster-en-18 | cross_document | retrieval_only | 1.0000 | N/A | 22.52 |
| aster-zh-01 | current_version | retrieval_only | 1.0000 | N/A | 21.86 |
| aster-zh-02 | old_version | retrieval_only | 1.0000 | N/A | 22.51 |
| aster-zh-03 | similar_document | retrieval_only | 1.0000 | N/A | 23.39 |
| aster-zh-04 | numeric_trap | retrieval_only | 0.0000 | N/A | 23.10 |
| aster-zh-05 | negation | retrieval_only | 1.0000 | N/A | 27.97 |
| aster-zh-06 | exception | retrieval_only | 1.0000 | N/A | 26.18 |
| aster-zh-07 | exception_denied | retrieval_only | 1.0000 | N/A | 30.61 |
| aster-zh-08 | negation | retrieval_only | 1.0000 | N/A | 26.32 |
| aster-zh-09 | cross_document | retrieval_only | 0.6667 | N/A | 22.82 |
| aster-zh-10 | cross_document | retrieval_only | 1.0000 | N/A | 23.99 |
| aster-zh-11 | similar_document | retrieval_only | 1.0000 | N/A | 22.12 |
| aster-zh-12 | draft_trap | retrieval_only | 0.5000 | N/A | 24.99 |
| aster-zh-13 | negative | retrieval_only | N/A | N/A | 24.46 |
| aster-zh-14 | negative | retrieval_only | N/A | N/A | 25.26 |
| aster-zh-15 | negative | retrieval_only | N/A | N/A | 19.60 |
| aster-zh-16 | adversarial | retrieval_only | N/A | N/A | 19.82 |
| aster-zh-17 | negation | retrieval_only | 1.0000 | N/A | 21.99 |
| aster-zh-18 | cross_document | retrieval_only | 1.0000 | N/A | 25.39 |
| aster-ja-01 | current_version | retrieval_only | 1.0000 | N/A | 23.73 |
| aster-ja-02 | old_version | retrieval_only | 1.0000 | N/A | 26.52 |
| aster-ja-03 | similar_document | retrieval_only | 1.0000 | N/A | 28.62 |
| aster-ja-04 | numeric_trap | retrieval_only | 0.0000 | N/A | 28.70 |
| aster-ja-05 | negation | retrieval_only | 1.0000 | N/A | 35.47 |
| aster-ja-06 | exception | retrieval_only | 1.0000 | N/A | 33.16 |
| aster-ja-07 | exception_denied | retrieval_only | 0.5000 | N/A | 31.00 |
| aster-ja-08 | negation | retrieval_only | 1.0000 | N/A | 24.59 |
| aster-ja-09 | cross_document | retrieval_only | 0.6667 | N/A | 22.39 |
| aster-ja-10 | cross_document | retrieval_only | 1.0000 | N/A | 23.66 |
| aster-ja-11 | similar_document | retrieval_only | 1.0000 | N/A | 26.41 |
| aster-ja-12 | draft_trap | retrieval_only | 1.0000 | N/A | 28.67 |
| aster-ja-13 | negative | retrieval_only | N/A | N/A | 25.25 |
| aster-ja-14 | negative | retrieval_only | N/A | N/A | 23.94 |
| aster-ja-15 | negative | retrieval_only | N/A | N/A | 21.58 |
| aster-ja-16 | adversarial | retrieval_only | N/A | N/A | 19.08 |
| aster-ja-17 | negation | retrieval_only | 1.0000 | N/A | 21.98 |
| aster-ja-18 | cross_document | retrieval_only | 1.0000 | N/A | 20.54 |

## 制約

- テンプレートを共有する多言語ケースには関連性があり、統計的に独立した標本ではありません。
- dev/test は組織名と数値を分けていますが、ルールのテンプレートは共有します。
- 参照根拠はページ単位で、検索の再現率は全事実の網羅性を保証しません。
- 代表的な実文書による人手レビューが引き続き必要です。
- ページテキストは PDF 解析後から扱います。PDF の一連の処理は live_smoke で検証します。
