# RAG 評価：policy-challenge-v2.1

モード：**api**; 分割：**dev**; クエリ数：54.

実行状態：completed; 要求問題数：54; 索引エラー：none.

合成した種データのみを使用します。この結果は本番の正確性を保証しません。

| 検索指標（回答可能な問題のマクロ平均） | 平均 | n |
|---|---:|---:|
| recall_at_1 | 0.5992 | 42 |
| recall_at_3 | 0.8135 | 42 |
| recall_at_5 | 0.8810 | 42 |
| mrr_at_k | 0.8353 | 42 |
| ndcg_at_k | 0.8128 | 42 |
| precision_at_k | 0.2476 | 42 |

返された Chunk の上限内でページの重複を除去します。precision の分母は未充足枠も含む k です。

| 回答指標 | 平均 | n |
|---|---:|---:|
| all_claims_grounded | 0.9000 | 40 |
| answer_correctness | 0.8333 | 42 |
| citation_groundedness | 1.0000 | 36 |
| claim_groundedness | 0.9250 | 40 |
| correct_refusal | 1.0000 | 12 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | 0.1429 | 42 |
| generator_false_refusal | 0.0476 | 42 |
| grounding_false_refusal | 0.0952 | 42 |
| grounding_rejected_correct_and_grounded | 1.0000 | 4 |
| invalid_model_response | 0.0000 | 54 |
| quote_match_failure | 0.0000 | 54 |
| reference_exact_match | 0.0000 | 42 |
| reference_token_f1_lexical | 0.3771 | 42 |
| refusal_accuracy | 0.8889 | 54 |
| unsupported_answer | 0.0741 | 54 |
| withheld_candidate_correctness | 1.0000 | 4 |

local は回答を生成しないため回答品質は N/A。語彙カバレッジ / token F1 は意味的正確性を証明しません。実行時 claim_groundedness は Verifier 診断値、answer_correctness と citation_groundedness は別設定の評価 Judge の自動判定で、人手ラベルではありません。

| 所要時間 (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| generation | 3386.4710 | 6650.6381 | 54 |
| provider_http | 5779.7885 | 11245.7059 | 54 |
| query_embedding | 307.5865 | 434.6291 | 54 |
| retrieval | 12.6585 | 13.2741 | 54 |
| verification | 2332.1785 | 4967.5869 | 40 |
| question_total | 5800.8790 | 11267.2034 | 54 |

索引作成：96 chunks, 22949.62 ms.
実行全体の API 費用 (USD)：0.1902。使用量不明や単価未設定は null/N/A を保持します。

アプリ平均 USD/query：0.0008; 報告された tokens：{'embedding_tokens': 1582, 'input_tokens': 72389, 'output_tokens': 25022, 'total_tokens': 98993, 'complete': True}.
独立評価：{'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'completed', 'judge_cost_usd': 0.145464, 'judge_errors': 0}。Judge の時間・費用はアプリ query の指標から除外します。
query worker 2 個で 1 回実行し、事前実行はありません。アプリ時間は評価処理と待ち行列を除き、Judge 費用は別集計です。

## 問題ごとの結果

| ID | 分類 | 状態 | Recall@k | 参照事実の語彙カバレッジ | 合計 ms |
|---|---|---|---:|---:|---:|
| aster-en-01 | current_version | answered | 1.0000 | N/A | 6159.72 |
| aster-en-02 | old_version | answered | 1.0000 | N/A | 5175.36 |
| aster-en-03 | similar_document | answered | 1.0000 | N/A | 5386.09 |
| aster-en-04 | numeric_trap | insufficient_evidence | 0.0000 | N/A | 2407.38 |
| aster-en-05 | negation | answered | 1.0000 | N/A | 6503.22 |
| aster-en-06 | exception | answered | 1.0000 | N/A | 6137.59 |
| aster-en-07 | exception_denied | answered | 1.0000 | N/A | 8954.63 |
| aster-en-08 | negation | answered | 1.0000 | N/A | 5698.60 |
| aster-en-09 | cross_document | unsupported_answer | 0.6667 | N/A | 9237.59 |
| aster-en-10 | cross_document | answered | 1.0000 | N/A | 10404.24 |
| aster-en-11 | similar_document | answered | 1.0000 | N/A | 8962.97 |
| aster-en-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 7608.45 |
| aster-en-13 | negative | insufficient_evidence | N/A | N/A | 1790.76 |
| aster-en-14 | negative | insufficient_evidence | N/A | N/A | 1252.37 |
| aster-en-15 | negative | insufficient_evidence | N/A | N/A | 1225.54 |
| aster-en-16 | adversarial | insufficient_evidence | N/A | N/A | 1573.25 |
| aster-en-17 | negation | answered | 1.0000 | N/A | 5244.49 |
| aster-en-18 | cross_document | answered | 1.0000 | N/A | 6900.28 |
| aster-zh-01 | current_version | answered | 1.0000 | N/A | 5620.82 |
| aster-zh-02 | old_version | answered | 1.0000 | N/A | 6084.42 |
| aster-zh-03 | similar_document | answered | 1.0000 | N/A | 5903.16 |
| aster-zh-04 | numeric_trap | answered | 0.0000 | N/A | 12186.42 |
| aster-zh-05 | negation | answered | 1.0000 | N/A | 3907.83 |
| aster-zh-06 | exception | answered | 1.0000 | N/A | 7522.82 |
| aster-zh-07 | exception_denied | answered | 1.0000 | N/A | 8764.50 |
| aster-zh-08 | negation | answered | 1.0000 | N/A | 10684.15 |
| aster-zh-09 | cross_document | unsupported_answer | 0.6667 | N/A | 10645.99 |
| aster-zh-10 | cross_document | answered | 1.0000 | N/A | 8263.11 |
| aster-zh-11 | similar_document | answered | 1.0000 | N/A | 6081.78 |
| aster-zh-12 | draft_trap | insufficient_evidence | 0.5000 | N/A | 1844.12 |
| aster-zh-13 | negative | insufficient_evidence | N/A | N/A | 1928.89 |
| aster-zh-14 | negative | insufficient_evidence | N/A | N/A | 1887.58 |
| aster-zh-15 | negative | insufficient_evidence | N/A | N/A | 1680.48 |
| aster-zh-16 | adversarial | insufficient_evidence | N/A | N/A | 1851.40 |
| aster-zh-17 | negation | answered | 1.0000 | N/A | 5512.18 |
| aster-zh-18 | cross_document | answered | 1.0000 | N/A | 8235.37 |
| aster-ja-01 | current_version | answered | 1.0000 | N/A | 6739.02 |
| aster-ja-02 | old_version | answered | 1.0000 | N/A | 5608.37 |
| aster-ja-03 | similar_document | answered | 1.0000 | N/A | 4719.14 |
| aster-ja-04 | numeric_trap | answered | 0.0000 | N/A | 9178.30 |
| aster-ja-05 | negation | answered | 1.0000 | N/A | 4447.92 |
| aster-ja-06 | exception | answered | 1.0000 | N/A | 5690.55 |
| aster-ja-07 | exception_denied | answered | 1.0000 | N/A | 8285.41 |
| aster-ja-08 | negation | answered | 1.0000 | N/A | 7986.16 |
| aster-ja-09 | cross_document | answered | 0.6667 | N/A | 11996.19 |
| aster-ja-10 | cross_document | answered | 1.0000 | N/A | 11520.93 |
| aster-ja-11 | similar_document | answered | 1.0000 | N/A | 5620.92 |
| aster-ja-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 7759.44 |
| aster-ja-13 | negative | insufficient_evidence | N/A | N/A | 1827.29 |
| aster-ja-14 | negative | insufficient_evidence | N/A | N/A | 1540.42 |
| aster-ja-15 | negative | insufficient_evidence | N/A | N/A | 1200.45 |
| aster-ja-16 | adversarial | insufficient_evidence | N/A | N/A | 1381.83 |
| aster-ja-17 | negation | answered | 1.0000 | N/A | 5033.74 |
| aster-ja-18 | cross_document | answered | 0.5000 | N/A | 11130.58 |

## 制約

- テンプレートを共有する多言語ケースには関連性があり、統計的に独立した標本ではありません。
- dev/test は組織名と数値を分けていますが、ルールのテンプレートは共有します。
- 参照根拠はページ単位で、検索の再現率は全事実の網羅性を保証しません。
- 代表的な実文書による人手レビューが引き続き必要です。
- ページテキストは PDF 解析後から扱います。PDF の一連の処理は live_smoke で検証します。
