# RAG 評価：policy-challenge-v2.1

モード：**api**; 分割：**dev**; クエリ数：54.

実行状態：completed; 要求問題数：54; 索引エラー：none.

合成した種データのみを使用します。この結果は本番の正確性を保証しません。

| 検索指標（回答可能な問題のマクロ平均） | 平均 | n |
|---|---:|---:|
| recall_at_1 | 0.5873 | 42 |
| recall_at_3 | 0.8056 | 42 |
| recall_at_5 | 0.9048 | 42 |
| mrr_at_k | 0.8254 | 42 |
| ndcg_at_k | 0.8104 | 42 |
| precision_at_k | 0.2524 | 42 |

返された Chunk の上限内でページの重複を除去します。precision の分母は未充足枠も含む k です。

| 回答指標 | 平均 | n |
|---|---:|---:|
| all_claims_grounded | 0.8293 | 41 |
| answer_correctness | 0.8095 | 42 |
| citation_groundedness | 1.0000 | 34 |
| claim_groundedness | 0.8293 | 41 |
| correct_refusal | 1.0000 | 12 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | 0.1905 | 42 |
| generator_false_refusal | 0.0238 | 42 |
| grounding_false_refusal | 0.1667 | 42 |
| grounding_rejected_correct_and_grounded | 1.0000 | 7 |
| invalid_model_response | 0.0000 | 54 |
| quote_match_failure | 0.0000 | 54 |
| reference_exact_match | 0.0000 | 42 |
| reference_token_f1_lexical | 0.3434 | 42 |
| refusal_accuracy | 0.8519 | 54 |
| unsupported_answer | 0.1296 | 54 |
| withheld_candidate_correctness | 1.0000 | 7 |

local は回答を生成しないため回答品質は N/A。語彙カバレッジ / token F1 は意味的正確性を証明しません。実行時 claim_groundedness は Verifier 診断値、answer_correctness と citation_groundedness は別設定の評価 Judge の自動判定で、人手ラベルではありません。

| 所要時間 (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| generation | 4018.8405 | 8008.4387 | 54 |
| provider_http | 5599.9410 | 10055.2535 | 54 |
| query_embedding | 291.0710 | 411.0546 | 54 |
| retrieval | 15.4090 | 33.6894 | 54 |
| verification | 1399.9820 | 2743.5810 | 41 |
| question_total | 5641.5755 | 10082.1213 | 54 |

索引作成：100 chunks, 21026.40 ms.
実行全体の API 費用 (USD)：0.2019。使用量不明や単価未設定は null/N/A を保持します。

アプリ平均 USD/query：0.0009; 報告された tokens：{'embedding_tokens': 1582, 'input_tokens': 72786, 'output_tokens': 22915, 'total_tokens': 97283, 'complete': True}.
独立評価：{'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'completed', 'judge_cost_usd': 0.153448, 'judge_errors': 0}。Judge の時間・費用はアプリ query の指標から除外します。
query worker 2 個で 1 回実行し、事前実行はありません。アプリ時間は評価処理と待ち行列を除き、Judge 費用は別集計です。

## 問題ごとの結果

| ID | 分類 | 状態 | Recall@k | 参照事実の語彙カバレッジ | 合計 ms |
|---|---|---|---:|---:|---:|
| aster-en-01 | current_version | answered | 1.0000 | N/A | 5381.50 |
| aster-en-02 | old_version | unsupported_answer | 1.0000 | N/A | 5664.16 |
| aster-en-03 | similar_document | answered | 1.0000 | N/A | 4789.11 |
| aster-en-04 | numeric_trap | answered | 1.0000 | N/A | 6633.11 |
| aster-en-05 | negation | answered | 1.0000 | N/A | 7991.53 |
| aster-en-06 | exception | unsupported_answer | 1.0000 | N/A | 5747.95 |
| aster-en-07 | exception_denied | answered | 1.0000 | N/A | 4569.11 |
| aster-en-08 | negation | answered | 1.0000 | N/A | 8507.71 |
| aster-en-09 | cross_document | answered | 0.6667 | N/A | 7561.60 |
| aster-en-10 | cross_document | unsupported_answer | 1.0000 | N/A | 5316.19 |
| aster-en-11 | similar_document | answered | 1.0000 | N/A | 4315.75 |
| aster-en-12 | draft_trap | answered | 1.0000 | N/A | 5243.86 |
| aster-en-13 | negative | insufficient_evidence | N/A | N/A | 1562.99 |
| aster-en-14 | negative | insufficient_evidence | N/A | N/A | 1470.63 |
| aster-en-15 | negative | insufficient_evidence | N/A | N/A | 1480.77 |
| aster-en-16 | adversarial | insufficient_evidence | N/A | N/A | 1672.45 |
| aster-en-17 | negation | answered | 1.0000 | N/A | 7128.43 |
| aster-en-18 | cross_document | answered | 1.0000 | N/A | 8910.43 |
| aster-zh-01 | current_version | answered | 1.0000 | N/A | 6345.25 |
| aster-zh-02 | old_version | answered | 1.0000 | N/A | 4082.84 |
| aster-zh-03 | similar_document | answered | 1.0000 | N/A | 4811.55 |
| aster-zh-04 | numeric_trap | answered | 0.0000 | N/A | 9998.79 |
| aster-zh-05 | negation | answered | 1.0000 | N/A | 7573.74 |
| aster-zh-06 | exception | unsupported_answer | 1.0000 | N/A | 7198.46 |
| aster-zh-07 | exception_denied | answered | 1.0000 | N/A | 9196.56 |
| aster-zh-08 | negation | answered | 1.0000 | N/A | 7357.04 |
| aster-zh-09 | cross_document | answered | 0.6667 | N/A | 9019.69 |
| aster-zh-10 | cross_document | answered | 1.0000 | N/A | 7838.67 |
| aster-zh-11 | similar_document | answered | 1.0000 | N/A | 4597.09 |
| aster-zh-12 | draft_trap | insufficient_evidence | 0.5000 | N/A | 2247.80 |
| aster-zh-13 | negative | insufficient_evidence | N/A | N/A | 2782.57 |
| aster-zh-14 | negative | insufficient_evidence | N/A | N/A | 2064.78 |
| aster-zh-15 | negative | insufficient_evidence | N/A | N/A | 1688.38 |
| aster-zh-16 | adversarial | insufficient_evidence | N/A | N/A | 2125.05 |
| aster-zh-17 | negation | answered | 1.0000 | N/A | 4968.79 |
| aster-zh-18 | cross_document | answered | 1.0000 | N/A | 7139.68 |
| aster-ja-01 | current_version | answered | 1.0000 | N/A | 5618.99 |
| aster-ja-02 | old_version | answered | 1.0000 | N/A | 5842.61 |
| aster-ja-03 | similar_document | unsupported_answer | 1.0000 | N/A | 4630.73 |
| aster-ja-04 | numeric_trap | answered | 0.0000 | N/A | 12427.99 |
| aster-ja-05 | negation | answered | 1.0000 | N/A | 5691.60 |
| aster-ja-06 | exception | answered | 1.0000 | N/A | 5964.82 |
| aster-ja-07 | exception_denied | unsupported_answer | 1.0000 | N/A | 10247.73 |
| aster-ja-08 | negation | answered | 1.0000 | N/A | 9777.32 |
| aster-ja-09 | cross_document | answered | 0.6667 | N/A | 9532.85 |
| aster-ja-10 | cross_document | answered | 1.0000 | N/A | 6016.61 |
| aster-ja-11 | similar_document | answered | 1.0000 | N/A | 5528.03 |
| aster-ja-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 7506.05 |
| aster-ja-13 | negative | insufficient_evidence | N/A | N/A | 1914.39 |
| aster-ja-14 | negative | insufficient_evidence | N/A | N/A | 1370.68 |
| aster-ja-15 | negative | insufficient_evidence | N/A | N/A | 2073.84 |
| aster-ja-16 | adversarial | insufficient_evidence | N/A | N/A | 1550.12 |
| aster-ja-17 | negation | answered | 1.0000 | N/A | 5265.18 |
| aster-ja-18 | cross_document | answered | 0.5000 | N/A | 10236.88 |

## 制約

- テンプレートを共有する多言語ケースには関連性があり、統計的に独立した標本ではありません。
- dev/test は組織名と数値を分けていますが、ルールのテンプレートは共有します。
- 参照根拠はページ単位で、検索の再現率は全事実の網羅性を保証しません。
- 代表的な実文書による人手レビューが引き続き必要です。
- ページテキストは PDF 解析後から扱います。PDF の一連の処理は live_smoke で検証します。
