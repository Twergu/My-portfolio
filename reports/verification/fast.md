# RAG 評価：policy-challenge-v2.1

モード：**api**; 分割：**test**; クエリ数：54.

実行状態：completed; 要求問題数：54; 索引エラー：none.

合成した種データのみを使用します。この結果は本番の正確性を保証しません。

| 検索指標（回答可能な問題のマクロ平均） | 平均 | n |
|---|---:|---:|
| recall_at_1 | 0.5833 | 42 |
| recall_at_3 | 0.8452 | 42 |
| recall_at_5 | 0.8810 | 42 |
| mrr_at_k | 0.8254 | 42 |
| ndcg_at_k | 0.8055 | 42 |
| precision_at_k | 0.2476 | 42 |

返された Chunk の上限内でページの重複を除去します。precision の分母は未充足枠も含む k です。

| 回答指標 | 平均 | n |
|---|---:|---:|
| all_claims_grounded | N/A | 0 |
| answer_correctness | 0.9286 | 42 |
| citation_groundedness | 1.0000 | 41 |
| claim_groundedness | N/A | 0 |
| correct_refusal | 1.0000 | 12 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | 0.0238 | 42 |
| generator_false_refusal | 0.0238 | 42 |
| grounding_false_refusal | 0.0000 | 42 |
| invalid_model_response | 0.0000 | 54 |
| quote_match_failure | 0.0000 | 54 |
| reference_exact_match | 0.0000 | 42 |
| reference_token_f1_lexical | 0.4138 | 42 |
| refusal_accuracy | 0.9815 | 54 |
| unsupported_answer | 0.0000 | 54 |

local は回答を生成しないため回答品質は N/A。語彙カバレッジ / token F1 は意味的正確性を証明しません。実行時 claim_groundedness は Verifier 診断値、answer_correctness と citation_groundedness は別設定の評価 Judge の自動判定で、人手ラベルではありません。

| 所要時間 (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| generation | 3044.0215 | 6667.4983 | 54 |
| provider_http | 3366.4920 | 6963.9756 | 54 |
| query_embedding | 303.8110 | 509.0630 | 54 |
| retrieval | 12.4795 | 12.8029 | 54 |
| question_total | 3389.1299 | 6984.6610 | 54 |

索引作成：96 chunks, 18384.76 ms.
実行全体の API 費用 (USD)：0.1823。使用量不明や単価未設定は null/N/A を保持します。

アプリ平均 USD/query：0.0006; 報告された tokens：{'embedding_tokens': 1600, 'input_tokens': 51133, 'output_tokens': 17070, 'total_tokens': 69803, 'complete': True}.
独立評価：{'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'completed', 'judge_cost_usd': 0.151348, 'judge_errors': 0}。Judge の時間・費用はアプリ query の指標から除外します。
query worker 2 個で 1 回実行し、事前実行はありません。アプリ時間は評価処理と待ち行列を除き、Judge 費用は別集計です。

## 問題ごとの結果

| ID | 分類 | 状態 | Recall@k | 参照事実の語彙カバレッジ | 合計 ms |
|---|---|---|---:|---:|---:|
| boreal-en-01 | current_version | answered | 1.0000 | N/A | 3137.03 |
| boreal-en-02 | old_version | answered | 1.0000 | N/A | 1890.65 |
| boreal-en-03 | similar_document | answered | 1.0000 | N/A | 2514.89 |
| boreal-en-04 | numeric_trap | answered | 0.0000 | N/A | 5759.36 |
| boreal-en-05 | negation | answered | 1.0000 | N/A | 3694.25 |
| boreal-en-06 | exception | answered | 1.0000 | N/A | 2815.89 |
| boreal-en-07 | exception_denied | answered | 1.0000 | N/A | 3697.25 |
| boreal-en-08 | negation | answered | 1.0000 | N/A | 3321.41 |
| boreal-en-09 | cross_document | answered | 0.6667 | N/A | 4428.41 |
| boreal-en-10 | cross_document | answered | 1.0000 | N/A | 3456.85 |
| boreal-en-11 | similar_document | answered | 1.0000 | N/A | 3287.91 |
| boreal-en-12 | draft_trap | answered | 1.0000 | N/A | 3523.63 |
| boreal-en-13 | negative | insufficient_evidence | N/A | N/A | 1613.48 |
| boreal-en-14 | negative | insufficient_evidence | N/A | N/A | 2090.05 |
| boreal-en-15 | negative | insufficient_evidence | N/A | N/A | 1584.48 |
| boreal-en-16 | adversarial | insufficient_evidence | N/A | N/A | 1158.29 |
| boreal-en-17 | negation | answered | 1.0000 | N/A | 2511.86 |
| boreal-en-18 | cross_document | answered | 1.0000 | N/A | 5349.39 |
| boreal-zh-01 | current_version | answered | 1.0000 | N/A | 3575.37 |
| boreal-zh-02 | old_version | answered | 1.0000 | N/A | 3240.85 |
| boreal-zh-03 | similar_document | answered | 1.0000 | N/A | 3547.59 |
| boreal-zh-04 | numeric_trap | answered | 0.0000 | N/A | 5302.28 |
| boreal-zh-05 | negation | answered | 1.0000 | N/A | 2726.95 |
| boreal-zh-06 | exception | answered | 1.0000 | N/A | 7324.14 |
| boreal-zh-07 | exception_denied | answered | 1.0000 | N/A | 4159.76 |
| boreal-zh-08 | negation | answered | 1.0000 | N/A | 9490.28 |
| boreal-zh-09 | cross_document | answered | 0.6667 | N/A | 5324.64 |
| boreal-zh-10 | cross_document | answered | 1.0000 | N/A | 6711.37 |
| boreal-zh-11 | similar_document | answered | 1.0000 | N/A | 4125.50 |
| boreal-zh-12 | draft_trap | insufficient_evidence | 0.5000 | N/A | 1751.49 |
| boreal-zh-13 | negative | insufficient_evidence | N/A | N/A | 1680.03 |
| boreal-zh-14 | negative | insufficient_evidence | N/A | N/A | 1552.42 |
| boreal-zh-15 | negative | insufficient_evidence | N/A | N/A | 1836.39 |
| boreal-zh-16 | adversarial | insufficient_evidence | N/A | N/A | 1659.34 |
| boreal-zh-17 | negation | answered | 1.0000 | N/A | 4471.92 |
| boreal-zh-18 | cross_document | answered | 1.0000 | N/A | 4291.84 |
| boreal-ja-01 | current_version | answered | 1.0000 | N/A | 3074.04 |
| boreal-ja-02 | old_version | answered | 1.0000 | N/A | 2549.23 |
| boreal-ja-03 | similar_document | answered | 1.0000 | N/A | 3494.72 |
| boreal-ja-04 | numeric_trap | answered | 0.0000 | N/A | 6801.87 |
| boreal-ja-05 | negation | answered | 1.0000 | N/A | 3297.62 |
| boreal-ja-06 | exception | answered | 1.0000 | N/A | 4307.12 |
| boreal-ja-07 | exception_denied | answered | 1.0000 | N/A | 4424.40 |
| boreal-ja-08 | negation | answered | 1.0000 | N/A | 3230.03 |
| boreal-ja-09 | cross_document | answered | 0.6667 | N/A | 5162.39 |
| boreal-ja-10 | cross_document | answered | 1.0000 | N/A | 8109.97 |
| boreal-ja-11 | similar_document | answered | 1.0000 | N/A | 4646.10 |
| boreal-ja-12 | draft_trap | answered | 1.0000 | N/A | 6665.32 |
| boreal-ja-13 | negative | insufficient_evidence | N/A | N/A | 1555.98 |
| boreal-ja-14 | negative | insufficient_evidence | N/A | N/A | 2163.00 |
| boreal-ja-15 | negative | insufficient_evidence | N/A | N/A | 1688.39 |
| boreal-ja-16 | adversarial | insufficient_evidence | N/A | N/A | 1465.04 |
| boreal-ja-17 | negation | answered | 1.0000 | N/A | 3205.61 |
| boreal-ja-18 | cross_document | answered | 0.5000 | N/A | 6100.13 |

## 制約

- テンプレートを共有する多言語ケースには関連性があり、統計的に独立した標本ではありません。
- dev/test は組織名と数値を分けていますが、ルールのテンプレートは共有します。
- 参照根拠はページ単位で、検索の再現率は全事実の網羅性を保証しません。
- 代表的な実文書による人手レビューが引き続き必要です。
- ページテキストは PDF 解析後から扱います。PDF の一連の処理は live_smoke で検証します。
