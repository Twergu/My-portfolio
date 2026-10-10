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
| all_claims_grounded | 0.9231 | 39 |
| answer_correctness | 0.8571 | 42 |
| citation_groundedness | 1.0000 | 36 |
| claim_groundedness | 0.9359 | 39 |
| correct_refusal | 1.0000 | 12 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | 0.1429 | 42 |
| generator_false_refusal | 0.0714 | 42 |
| grounding_false_refusal | 0.0714 | 42 |
| grounding_rejected_correct_and_grounded | 1.0000 | 3 |
| invalid_model_response | 0.0000 | 54 |
| quote_match_failure | 0.0000 | 54 |
| reference_exact_match | 0.0000 | 42 |
| reference_token_f1_lexical | 0.3781 | 42 |
| refusal_accuracy | 0.8889 | 54 |
| unsupported_answer | 0.0556 | 54 |
| withheld_candidate_correctness | 1.0000 | 3 |

local は回答を生成しないため回答品質は N/A。語彙カバレッジ / token F1 は意味的正確性を証明しません。実行時 claim_groundedness は Verifier 診断値、answer_correctness と citation_groundedness は別設定の評価 Judge の自動判定で、人手ラベルではありません。

| 所要時間 (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| generation | 3547.1170 | 6950.0146 | 54 |
| provider_http | 5848.9910 | 11424.6376 | 54 |
| query_embedding | 295.8660 | 403.5239 | 54 |
| retrieval | 25.3895 | 120.4880 | 54 |
| verification | 2483.3840 | 3999.5946 | 39 |
| question_total | 5988.0166 | 11451.9354 | 54 |

索引作成：96 chunks, 24288.33 ms.
実行全体の API 費用 (USD)：0.1943。使用量不明や単価未設定は null/N/A を保持します。

アプリ平均 USD/query：0.0008; 報告された tokens：{'embedding_tokens': 1582, 'input_tokens': 72342, 'output_tokens': 24514, 'total_tokens': 98438, 'complete': True}.
独立評価：{'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'completed', 'judge_cost_usd': 0.150168, 'judge_errors': 0, 'recovered_errors': 1}。Judge の時間・費用はアプリ query の指標から除外します。
query worker 2 個で 1 回実行し、事前実行はありません。アプリ時間は評価処理と待ち行列を除き、Judge 費用は別集計です。

## 問題ごとの結果

| ID | 分類 | 状態 | Recall@k | 参照事実の語彙カバレッジ | 合計 ms |
|---|---|---|---:|---:|---:|
| aster-en-01 | current_version | answered | 1.0000 | N/A | 6397.12 |
| aster-en-02 | old_version | answered | 1.0000 | N/A | 5212.72 |
| aster-en-03 | similar_document | answered | 1.0000 | N/A | 4988.62 |
| aster-en-04 | numeric_trap | insufficient_evidence | 0.0000 | N/A | 4306.80 |
| aster-en-05 | negation | answered | 1.0000 | N/A | 7638.38 |
| aster-en-06 | exception | insufficient_evidence | 1.0000 | N/A | 3715.44 |
| aster-en-07 | exception_denied | answered | 1.0000 | N/A | 7272.22 |
| aster-en-08 | negation | answered | 1.0000 | N/A | 5894.69 |
| aster-en-09 | cross_document | unsupported_answer | 0.6667 | N/A | 13871.92 |
| aster-en-10 | cross_document | answered | 1.0000 | N/A | 9206.04 |
| aster-en-11 | similar_document | answered | 1.0000 | N/A | 5979.80 |
| aster-en-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 6717.25 |
| aster-en-13 | negative | insufficient_evidence | N/A | N/A | 1703.61 |
| aster-en-14 | negative | insufficient_evidence | N/A | N/A | 1469.93 |
| aster-en-15 | negative | insufficient_evidence | N/A | N/A | 1647.44 |
| aster-en-16 | adversarial | insufficient_evidence | N/A | N/A | 1496.48 |
| aster-en-17 | negation | answered | 1.0000 | N/A | 5126.39 |
| aster-en-18 | cross_document | answered | 1.0000 | N/A | 9077.73 |
| aster-zh-01 | current_version | answered | 1.0000 | N/A | 5626.17 |
| aster-zh-02 | old_version | answered | 1.0000 | N/A | 4403.07 |
| aster-zh-03 | similar_document | answered | 1.0000 | N/A | 4686.85 |
| aster-zh-04 | numeric_trap | answered | 0.0000 | N/A | 9248.74 |
| aster-zh-05 | negation | answered | 1.0000 | N/A | 5407.26 |
| aster-zh-06 | exception | answered | 1.0000 | N/A | 5996.23 |
| aster-zh-07 | exception_denied | answered | 1.0000 | N/A | 7594.27 |
| aster-zh-08 | negation | answered | 1.0000 | N/A | 8241.47 |
| aster-zh-09 | cross_document | answered | 0.6667 | N/A | 11395.73 |
| aster-zh-10 | cross_document | answered | 1.0000 | N/A | 7475.77 |
| aster-zh-11 | similar_document | answered | 1.0000 | N/A | 6757.36 |
| aster-zh-12 | draft_trap | insufficient_evidence | 0.5000 | N/A | 2250.97 |
| aster-zh-13 | negative | insufficient_evidence | N/A | N/A | 1905.94 |
| aster-zh-14 | negative | insufficient_evidence | N/A | N/A | 1791.01 |
| aster-zh-15 | negative | insufficient_evidence | N/A | N/A | 1890.20 |
| aster-zh-16 | adversarial | insufficient_evidence | N/A | N/A | 1831.39 |
| aster-zh-17 | negation | answered | 1.0000 | N/A | 5876.71 |
| aster-zh-18 | cross_document | answered | 1.0000 | N/A | 7847.47 |
| aster-ja-01 | current_version | answered | 1.0000 | N/A | 8282.77 |
| aster-ja-02 | old_version | unsupported_answer | 1.0000 | N/A | 5066.97 |
| aster-ja-03 | similar_document | answered | 1.0000 | N/A | 5410.38 |
| aster-ja-04 | numeric_trap | answered | 0.0000 | N/A | 10374.07 |
| aster-ja-05 | negation | answered | 1.0000 | N/A | 7368.45 |
| aster-ja-06 | exception | answered | 1.0000 | N/A | 6326.93 |
| aster-ja-07 | exception_denied | answered | 1.0000 | N/A | 6869.61 |
| aster-ja-08 | negation | answered | 1.0000 | N/A | 7168.36 |
| aster-ja-09 | cross_document | answered | 0.6667 | N/A | 9138.36 |
| aster-ja-10 | cross_document | answered | 1.0000 | N/A | 9434.68 |
| aster-ja-11 | similar_document | answered | 1.0000 | N/A | 6558.71 |
| aster-ja-12 | draft_trap | answered | 1.0000 | N/A | 11942.05 |
| aster-ja-13 | negative | insufficient_evidence | N/A | N/A | 2792.37 |
| aster-ja-14 | negative | insufficient_evidence | N/A | N/A | 1514.78 |
| aster-ja-15 | negative | insufficient_evidence | N/A | N/A | 1149.75 |
| aster-ja-16 | adversarial | insufficient_evidence | N/A | N/A | 1378.51 |
| aster-ja-17 | negation | answered | 1.0000 | N/A | 6449.38 |
| aster-ja-18 | cross_document | answered | 0.5000 | N/A | 11556.31 |

## 制約

- テンプレートを共有する多言語ケースには関連性があり、統計的に独立した標本ではありません。
- dev/test は組織名と数値を分けていますが、ルールのテンプレートは共有します。
- 参照根拠はページ単位で、検索の再現率は全事実の網羅性を保証しません。
- 代表的な実文書による人手レビューが引き続き必要です。
- ページテキストは PDF 解析後から扱います。PDF の一連の処理は live_smoke で検証します。
