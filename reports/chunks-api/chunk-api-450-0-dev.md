# RAG 評価：policy-challenge-v2.1

モード：**api**; 分割：**dev**; クエリ数：54.

実行状態：completed; 要求問題数：54; 索引エラー：none.

合成した種データのみを使用します。この結果は本番の正確性を保証しません。

| 検索指標（回答可能な問題のマクロ平均） | 平均 | n |
|---|---:|---:|
| recall_at_1 | 0.5992 | 42 |
| recall_at_3 | 0.8056 | 42 |
| recall_at_5 | 0.9048 | 42 |
| mrr_at_k | 0.8373 | 42 |
| ndcg_at_k | 0.8177 | 42 |
| precision_at_k | 0.2524 | 42 |

返された Chunk の上限内でページの重複を除去します。precision の分母は未充足枠も含む k です。

| 回答指標 | 平均 | n |
|---|---:|---:|
| all_claims_grounded | 0.7857 | 42 |
| answer_correctness | 0.7857 | 42 |
| citation_groundedness | 1.0000 | 33 |
| claim_groundedness | 0.8333 | 42 |
| correct_refusal | 1.0000 | 12 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | 0.2143 | 42 |
| generator_false_refusal | 0.0000 | 42 |
| grounding_false_refusal | 0.2143 | 42 |
| grounding_rejected_correct_and_grounded | 1.0000 | 9 |
| invalid_model_response | 0.0000 | 54 |
| quote_match_failure | 0.0000 | 54 |
| reference_exact_match | 0.0000 | 42 |
| reference_token_f1_lexical | 0.3361 | 42 |
| refusal_accuracy | 0.8333 | 54 |
| unsupported_answer | 0.1667 | 54 |
| withheld_candidate_correctness | 1.0000 | 9 |

local は回答を生成しないため回答品質は N/A。語彙カバレッジ / token F1 は意味的正確性を証明しません。実行時 claim_groundedness は Verifier 診断値、answer_correctness と citation_groundedness は別設定の評価 Judge の自動判定で、人手ラベルではありません。

| 所要時間 (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| generation | 3861.0230 | 6821.2513 | 54 |
| provider_http | 6821.0560 | 10955.8051 | 54 |
| query_embedding | 293.7140 | 416.4612 | 54 |
| retrieval | 26.0785 | 164.8868 | 54 |
| verification | 2633.4170 | 4237.0738 | 42 |
| question_total | 6866.2266 | 11097.6768 | 54 |

索引作成：100 chunks, 19682.69 ms.
実行全体の API 費用 (USD)：0.2031。使用量不明や単価未設定は null/N/A を保持します。

アプリ平均 USD/query：0.0009; 報告された tokens：{'embedding_tokens': 1582, 'input_tokens': 73014, 'output_tokens': 26838, 'total_tokens': 101434, 'complete': True}.
独立評価：{'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'completed', 'judge_cost_usd': 0.15609800000000001, 'judge_errors': 0}。Judge の時間・費用はアプリ query の指標から除外します。
query worker 2 個で 1 回実行し、事前実行はありません。アプリ時間は評価処理と待ち行列を除き、Judge 費用は別集計です。

## 問題ごとの結果

| ID | 分類 | 状態 | Recall@k | 参照事実の語彙カバレッジ | 合計 ms |
|---|---|---|---:|---:|---:|
| aster-en-01 | current_version | answered | 1.0000 | N/A | 6750.37 |
| aster-en-02 | old_version | answered | 1.0000 | N/A | 7860.30 |
| aster-en-03 | similar_document | answered | 1.0000 | N/A | 5072.13 |
| aster-en-04 | numeric_trap | answered | 1.0000 | N/A | 5260.14 |
| aster-en-05 | negation | answered | 1.0000 | N/A | 7329.48 |
| aster-en-06 | exception | answered | 1.0000 | N/A | 6086.71 |
| aster-en-07 | exception_denied | answered | 1.0000 | N/A | 5279.37 |
| aster-en-08 | negation | answered | 1.0000 | N/A | 7694.87 |
| aster-en-09 | cross_document | unsupported_answer | 0.6667 | N/A | 10216.07 |
| aster-en-10 | cross_document | answered | 1.0000 | N/A | 6942.02 |
| aster-en-11 | similar_document | answered | 1.0000 | N/A | 5525.73 |
| aster-en-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 6790.43 |
| aster-en-13 | negative | insufficient_evidence | N/A | N/A | 2095.58 |
| aster-en-14 | negative | insufficient_evidence | N/A | N/A | 1337.70 |
| aster-en-15 | negative | insufficient_evidence | N/A | N/A | 1352.87 |
| aster-en-16 | adversarial | insufficient_evidence | N/A | N/A | 1264.69 |
| aster-en-17 | negation | answered | 1.0000 | N/A | 6950.62 |
| aster-en-18 | cross_document | unsupported_answer | 1.0000 | N/A | 11405.47 |
| aster-zh-01 | current_version | answered | 1.0000 | N/A | 8039.66 |
| aster-zh-02 | old_version | answered | 1.0000 | N/A | 5054.06 |
| aster-zh-03 | similar_document | answered | 1.0000 | N/A | 8366.21 |
| aster-zh-04 | numeric_trap | answered | 0.0000 | N/A | 9522.50 |
| aster-zh-05 | negation | answered | 1.0000 | N/A | 8843.56 |
| aster-zh-06 | exception | answered | 1.0000 | N/A | 9895.55 |
| aster-zh-07 | exception_denied | answered | 1.0000 | N/A | 7911.39 |
| aster-zh-08 | negation | answered | 1.0000 | N/A | 8025.50 |
| aster-zh-09 | cross_document | unsupported_answer | 0.6667 | N/A | 7598.06 |
| aster-zh-10 | cross_document | answered | 1.0000 | N/A | 7389.09 |
| aster-zh-11 | similar_document | unsupported_answer | 1.0000 | N/A | 5667.68 |
| aster-zh-12 | draft_trap | answered | 0.5000 | N/A | 8235.02 |
| aster-zh-13 | negative | insufficient_evidence | N/A | N/A | 2277.20 |
| aster-zh-14 | negative | insufficient_evidence | N/A | N/A | 1496.58 |
| aster-zh-15 | negative | insufficient_evidence | N/A | N/A | 1151.09 |
| aster-zh-16 | adversarial | insufficient_evidence | N/A | N/A | 1981.48 |
| aster-zh-17 | negation | answered | 1.0000 | N/A | 5422.32 |
| aster-zh-18 | cross_document | answered | 1.0000 | N/A | 9688.80 |
| aster-ja-01 | current_version | answered | 1.0000 | N/A | 8599.18 |
| aster-ja-02 | old_version | answered | 1.0000 | N/A | 5425.53 |
| aster-ja-03 | similar_document | answered | 1.0000 | N/A | 5864.10 |
| aster-ja-04 | numeric_trap | unsupported_answer | 0.0000 | N/A | 11059.49 |
| aster-ja-05 | negation | answered | 1.0000 | N/A | 6786.27 |
| aster-ja-06 | exception | answered | 1.0000 | N/A | 6737.13 |
| aster-ja-07 | exception_denied | answered | 1.0000 | N/A | 10234.55 |
| aster-ja-08 | negation | answered | 1.0000 | N/A | 7028.64 |
| aster-ja-09 | cross_document | unsupported_answer | 0.6667 | N/A | 11168.59 |
| aster-ja-10 | cross_document | answered | 1.0000 | N/A | 9972.59 |
| aster-ja-11 | similar_document | unsupported_answer | 1.0000 | N/A | 7240.83 |
| aster-ja-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 9493.13 |
| aster-ja-13 | negative | insufficient_evidence | N/A | N/A | 2003.63 |
| aster-ja-14 | negative | insufficient_evidence | N/A | N/A | 1493.52 |
| aster-ja-15 | negative | insufficient_evidence | N/A | N/A | 1172.52 |
| aster-ja-16 | adversarial | insufficient_evidence | N/A | N/A | 1629.59 |
| aster-ja-17 | negation | answered | 1.0000 | N/A | 6003.82 |
| aster-ja-18 | cross_document | answered | 0.5000 | N/A | 12365.92 |

## 制約

- テンプレートを共有する多言語ケースには関連性があり、統計的に独立した標本ではありません。
- dev/test は組織名と数値を分けていますが、ルールのテンプレートは共有します。
- 参照根拠はページ単位で、検索の再現率は全事実の網羅性を保証しません。
- 代表的な実文書による人手レビューが引き続き必要です。
- ページテキストは PDF 解析後から扱います。PDF の一連の処理は live_smoke で検証します。
