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
| all_claims_grounded | 0.9231 | 39 |
| answer_correctness | 0.8333 | 42 |
| citation_groundedness | 1.0000 | 36 |
| claim_groundedness | 0.9359 | 39 |
| correct_refusal | 0.9167 | 12 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | 0.1667 | 42 |
| generator_false_refusal | 0.0952 | 42 |
| grounding_false_refusal | 0.0714 | 42 |
| grounding_rejected_correct_and_grounded | 1.0000 | 3 |
| invalid_model_response | 0.0000 | 54 |
| quote_match_failure | 0.0000 | 54 |
| reference_exact_match | 0.0000 | 42 |
| reference_token_f1_lexical | 0.3615 | 42 |
| refusal_accuracy | 0.8519 | 54 |
| unsupported_answer | 0.0556 | 54 |
| withheld_candidate_correctness | 1.0000 | 3 |

local は回答を生成しないため回答品質は N/A。語彙カバレッジ / token F1 は意味的正確性を証明しません。実行時 claim_groundedness は Verifier 診断値、answer_correctness と citation_groundedness は別設定の評価 Judge の自動判定で、人手ラベルではありません。

| 所要時間 (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| generation | 3191.3650 | 6278.5334 | 54 |
| provider_http | 5405.0205 | 9730.8082 | 54 |
| query_embedding | 328.2060 | 441.1453 | 54 |
| retrieval | 13.1920 | 13.8969 | 54 |
| verification | 2260.5410 | 4266.9601 | 39 |
| question_total | 5426.1470 | 9751.6545 | 54 |

索引作成：96 chunks, 19251.29 ms.
実行全体の API 費用 (USD)：0.1889。使用量不明や単価未設定は null/N/A を保持します。

アプリ平均 USD/query：0.0008; 報告された tokens：{'embedding_tokens': 1600, 'input_tokens': 72417, 'output_tokens': 24360, 'total_tokens': 98377, 'complete': True}.
独立評価：{'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'completed', 'judge_cost_usd': 0.144998, 'judge_errors': 0}。Judge の時間・費用はアプリ query の指標から除外します。
query worker 2 個で 1 回実行し、事前実行はありません。アプリ時間は評価処理と待ち行列を除き、Judge 費用は別集計です。

## 問題ごとの結果

| ID | 分類 | 状態 | Recall@k | 参照事実の語彙カバレッジ | 合計 ms |
|---|---|---|---:|---:|---:|
| boreal-en-01 | current_version | answered | 1.0000 | N/A | 4623.69 |
| boreal-en-02 | old_version | answered | 1.0000 | N/A | 4947.86 |
| boreal-en-03 | similar_document | answered | 1.0000 | N/A | 5047.95 |
| boreal-en-04 | numeric_trap | insufficient_evidence | 0.0000 | N/A | 2427.19 |
| boreal-en-05 | negation | answered | 1.0000 | N/A | 6395.03 |
| boreal-en-06 | exception | answered | 1.0000 | N/A | 5061.95 |
| boreal-en-07 | exception_denied | answered | 1.0000 | N/A | 7650.35 |
| boreal-en-08 | negation | answered | 1.0000 | N/A | 8258.64 |
| boreal-en-09 | cross_document | answered | 0.6667 | N/A | 7305.20 |
| boreal-en-10 | cross_document | answered | 1.0000 | N/A | 8601.47 |
| boreal-en-11 | similar_document | answered | 1.0000 | N/A | 5427.84 |
| boreal-en-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 8059.93 |
| boreal-en-13 | negative | insufficient_evidence | N/A | N/A | 1456.22 |
| boreal-en-14 | negative | insufficient_evidence | N/A | N/A | 1470.44 |
| boreal-en-15 | negative | answered | N/A | N/A | 4601.99 |
| boreal-en-16 | adversarial | insufficient_evidence | N/A | N/A | 1367.49 |
| boreal-en-17 | negation | answered | 1.0000 | N/A | 6226.40 |
| boreal-en-18 | cross_document | answered | 1.0000 | N/A | 8319.39 |
| boreal-zh-01 | current_version | answered | 1.0000 | N/A | 7666.20 |
| boreal-zh-02 | old_version | answered | 1.0000 | N/A | 5294.05 |
| boreal-zh-03 | similar_document | answered | 1.0000 | N/A | 5118.10 |
| boreal-zh-04 | numeric_trap | insufficient_evidence | 0.0000 | N/A | 6384.96 |
| boreal-zh-05 | negation | answered | 1.0000 | N/A | 4774.89 |
| boreal-zh-06 | exception | answered | 1.0000 | N/A | 4720.97 |
| boreal-zh-07 | exception_denied | answered | 1.0000 | N/A | 6979.88 |
| boreal-zh-08 | negation | answered | 1.0000 | N/A | 8915.96 |
| boreal-zh-09 | cross_document | unsupported_answer | 0.6667 | N/A | 9582.02 |
| boreal-zh-10 | cross_document | answered | 1.0000 | N/A | 7411.92 |
| boreal-zh-11 | similar_document | answered | 1.0000 | N/A | 6786.55 |
| boreal-zh-12 | draft_trap | insufficient_evidence | 0.5000 | N/A | 1790.70 |
| boreal-zh-13 | negative | insufficient_evidence | N/A | N/A | 2032.72 |
| boreal-zh-14 | negative | insufficient_evidence | N/A | N/A | 1631.98 |
| boreal-zh-15 | negative | insufficient_evidence | N/A | N/A | 2149.34 |
| boreal-zh-16 | adversarial | insufficient_evidence | N/A | N/A | 1374.88 |
| boreal-zh-17 | negation | answered | 1.0000 | N/A | 5403.11 |
| boreal-zh-18 | cross_document | answered | 1.0000 | N/A | 6782.75 |
| boreal-ja-01 | current_version | answered | 1.0000 | N/A | 5693.13 |
| boreal-ja-02 | old_version | unsupported_answer | 1.0000 | N/A | 4423.46 |
| boreal-ja-03 | similar_document | answered | 1.0000 | N/A | 6466.35 |
| boreal-ja-04 | numeric_trap | insufficient_evidence | 0.0000 | N/A | 4052.72 |
| boreal-ja-05 | negation | answered | 1.0000 | N/A | 8245.51 |
| boreal-ja-06 | exception | answered | 1.0000 | N/A | 5069.15 |
| boreal-ja-07 | exception_denied | answered | 1.0000 | N/A | 7085.88 |
| boreal-ja-08 | negation | answered | 1.0000 | N/A | 6166.66 |
| boreal-ja-09 | cross_document | answered | 0.6667 | N/A | 11646.47 |
| boreal-ja-10 | cross_document | answered | 1.0000 | N/A | 10066.69 |
| boreal-ja-11 | similar_document | answered | 1.0000 | N/A | 6950.18 |
| boreal-ja-12 | draft_trap | answered | 1.0000 | N/A | 9423.76 |
| boreal-ja-13 | negative | insufficient_evidence | N/A | N/A | 1805.12 |
| boreal-ja-14 | negative | insufficient_evidence | N/A | N/A | 1477.63 |
| boreal-ja-15 | negative | insufficient_evidence | N/A | N/A | 1352.95 |
| boreal-ja-16 | adversarial | insufficient_evidence | N/A | N/A | 1430.73 |
| boreal-ja-17 | negation | answered | 1.0000 | N/A | 5424.46 |
| boreal-ja-18 | cross_document | answered | 0.5000 | N/A | 11338.13 |

## 制約

- テンプレートを共有する多言語ケースには関連性があり、統計的に独立した標本ではありません。
- dev/test は組織名と数値を分けていますが、ルールのテンプレートは共有します。
- 参照根拠はページ単位で、検索の再現率は全事実の網羅性を保証しません。
- 代表的な実文書による人手レビューが引き続き必要です。
- ページテキストは PDF 解析後から扱います。PDF の一連の処理は live_smoke で検証します。
