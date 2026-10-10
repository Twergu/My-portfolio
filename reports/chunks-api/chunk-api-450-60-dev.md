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
| ndcg_at_k | 0.8123 | 42 |
| precision_at_k | 0.2524 | 42 |

返された Chunk の上限内でページの重複を除去します。precision の分母は未充足枠も含む k です。

| 回答指標 | 平均 | n |
|---|---:|---:|
| all_claims_grounded | 0.8250 | 40 |
| answer_correctness | 0.7619 | 42 |
| citation_groundedness | 1.0000 | 33 |
| claim_groundedness | 0.8500 | 40 |
| correct_refusal | 0.9167 | 12 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | 0.2381 | 42 |
| generator_false_refusal | 0.0714 | 42 |
| grounding_false_refusal | 0.1667 | 42 |
| grounding_rejected_correct_and_grounded | 0.8571 | 7 |
| invalid_model_response | 0.0000 | 54 |
| quote_match_failure | 0.0000 | 54 |
| reference_exact_match | 0.0000 | 42 |
| reference_token_f1_lexical | 0.3293 | 42 |
| refusal_accuracy | 0.7963 | 54 |
| unsupported_answer | 0.1296 | 54 |
| withheld_candidate_correctness | 1.0000 | 7 |

local は回答を生成しないため回答品質は N/A。語彙カバレッジ / token F1 は意味的正確性を証明しません。実行時 claim_groundedness は Verifier 診断値、answer_correctness と citation_groundedness は別設定の評価 Judge の自動判定で、人手ラベルではありません。

| 所要時間 (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| generation | 3210.5865 | 6424.1342 | 54 |
| provider_http | 5807.7680 | 10369.8617 | 54 |
| query_embedding | 284.5365 | 434.6642 | 54 |
| retrieval | 27.6065 | 210.9366 | 54 |
| verification | 2705.1145 | 4469.9575 | 40 |
| question_total | 5991.3406 | 10409.0792 | 54 |

索引作成：100 chunks, 16635.57 ms.
実行全体の API 費用 (USD)：0.1879。使用量不明や単価未設定は null/N/A を保持します。

アプリ平均 USD/query：0.0008; 報告された tokens：{'embedding_tokens': 1582, 'input_tokens': 72118, 'output_tokens': 24077, 'total_tokens': 97777, 'complete': True}.
独立評価：{'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'completed', 'judge_cost_usd': 0.144386, 'judge_errors': 0}。Judge の時間・費用はアプリ query の指標から除外します。
query worker 2 個で 1 回実行し、事前実行はありません。アプリ時間は評価処理と待ち行列を除き、Judge 費用は別集計です。

## 問題ごとの結果

| ID | 分類 | 状態 | Recall@k | 参照事実の語彙カバレッジ | 合計 ms |
|---|---|---|---:|---:|---:|
| aster-en-01 | current_version | answered | 1.0000 | N/A | 4630.56 |
| aster-en-02 | old_version | answered | 1.0000 | N/A | 3996.05 |
| aster-en-03 | similar_document | answered | 1.0000 | N/A | 5738.06 |
| aster-en-04 | numeric_trap | answered | 1.0000 | N/A | 5940.10 |
| aster-en-05 | negation | answered | 1.0000 | N/A | 7655.40 |
| aster-en-06 | exception | answered | 1.0000 | N/A | 4900.28 |
| aster-en-07 | exception_denied | answered | 1.0000 | N/A | 5457.16 |
| aster-en-08 | negation | answered | 1.0000 | N/A | 9313.25 |
| aster-en-09 | cross_document | insufficient_evidence | 0.6667 | N/A | 2075.65 |
| aster-en-10 | cross_document | answered | 1.0000 | N/A | 7668.07 |
| aster-en-11 | similar_document | answered | 1.0000 | N/A | 5270.85 |
| aster-en-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 7654.67 |
| aster-en-13 | negative | insufficient_evidence | N/A | N/A | 1765.64 |
| aster-en-14 | negative | insufficient_evidence | N/A | N/A | 1571.02 |
| aster-en-15 | negative | answered | N/A | N/A | 5278.07 |
| aster-en-16 | adversarial | insufficient_evidence | N/A | N/A | 1335.45 |
| aster-en-17 | negation | answered | 1.0000 | N/A | 6894.12 |
| aster-en-18 | cross_document | answered | 1.0000 | N/A | 10639.97 |
| aster-zh-01 | current_version | answered | 1.0000 | N/A | 11633.97 |
| aster-zh-02 | old_version | answered | 1.0000 | N/A | 4997.86 |
| aster-zh-03 | similar_document | answered | 1.0000 | N/A | 4877.72 |
| aster-zh-04 | numeric_trap | unsupported_answer | 0.0000 | N/A | 10078.07 |
| aster-zh-05 | negation | answered | 1.0000 | N/A | 7475.88 |
| aster-zh-06 | exception | answered | 1.0000 | N/A | 8125.52 |
| aster-zh-07 | exception_denied | answered | 1.0000 | N/A | 7470.04 |
| aster-zh-08 | negation | answered | 1.0000 | N/A | 9056.03 |
| aster-zh-09 | cross_document | unsupported_answer | 0.6667 | N/A | 7628.07 |
| aster-zh-10 | cross_document | answered | 1.0000 | N/A | 8687.31 |
| aster-zh-11 | similar_document | unsupported_answer | 1.0000 | N/A | 7927.58 |
| aster-zh-12 | draft_trap | insufficient_evidence | 0.5000 | N/A | 2132.01 |
| aster-zh-13 | negative | insufficient_evidence | N/A | N/A | 1642.15 |
| aster-zh-14 | negative | insufficient_evidence | N/A | N/A | 1955.75 |
| aster-zh-15 | negative | insufficient_evidence | N/A | N/A | 1413.29 |
| aster-zh-16 | adversarial | insufficient_evidence | N/A | N/A | 1703.14 |
| aster-zh-17 | negation | answered | 1.0000 | N/A | 5635.36 |
| aster-zh-18 | cross_document | answered | 1.0000 | N/A | 6921.36 |
| aster-ja-01 | current_version | answered | 1.0000 | N/A | 7696.13 |
| aster-ja-02 | old_version | answered | 1.0000 | N/A | 5378.37 |
| aster-ja-03 | similar_document | answered | 1.0000 | N/A | 5528.03 |
| aster-ja-04 | numeric_trap | insufficient_evidence | 0.0000 | N/A | 6042.58 |
| aster-ja-05 | negation | answered | 1.0000 | N/A | 9250.62 |
| aster-ja-06 | exception | unsupported_answer | 1.0000 | N/A | 7238.65 |
| aster-ja-07 | exception_denied | answered | 1.0000 | N/A | 7418.71 |
| aster-ja-08 | negation | answered | 1.0000 | N/A | 9964.34 |
| aster-ja-09 | cross_document | answered | 0.6667 | N/A | 11425.82 |
| aster-ja-10 | cross_document | answered | 1.0000 | N/A | 9144.55 |
| aster-ja-11 | similar_document | unsupported_answer | 1.0000 | N/A | 8261.89 |
| aster-ja-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 8467.69 |
| aster-ja-13 | negative | insufficient_evidence | N/A | N/A | 1933.22 |
| aster-ja-14 | negative | insufficient_evidence | N/A | N/A | 1534.00 |
| aster-ja-15 | negative | insufficient_evidence | N/A | N/A | 1448.97 |
| aster-ja-16 | adversarial | insufficient_evidence | N/A | N/A | 1980.83 |
| aster-ja-17 | negation | answered | 1.0000 | N/A | 5646.91 |
| aster-ja-18 | cross_document | answered | 0.5000 | N/A | 10284.75 |

## 制約

- テンプレートを共有する多言語ケースには関連性があり、統計的に独立した標本ではありません。
- dev/test は組織名と数値を分けていますが、ルールのテンプレートは共有します。
- 参照根拠はページ単位で、検索の再現率は全事実の網羅性を保証しません。
- 代表的な実文書による人手レビューが引き続き必要です。
- ページテキストは PDF 解析後から扱います。PDF の一連の処理は live_smoke で検証します。
