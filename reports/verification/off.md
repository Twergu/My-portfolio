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
| answer_correctness | 0.9762 | 42 |
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
| reference_token_f1_lexical | 0.4097 | 42 |
| refusal_accuracy | 0.9815 | 54 |
| unsupported_answer | 0.0000 | 54 |

local は回答を生成しないため回答品質は N/A。語彙カバレッジ / token F1 は意味的正確性を証明しません。実行時 claim_groundedness は Verifier 診断値、answer_correctness と citation_groundedness は別設定の評価 Judge の自動判定で、人手ラベルではありません。

| 所要時間 (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| generation | 3160.4220 | 6520.8744 | 54 |
| provider_http | 3506.8535 | 6802.2297 | 54 |
| query_embedding | 309.2435 | 422.3744 | 54 |
| retrieval | 12.6505 | 13.8556 | 54 |
| question_total | 3527.5054 | 6822.6271 | 54 |

索引作成：96 chunks, 18573.85 ms.
実行全体の API 費用 (USD)：0.1873。使用量不明や単価未設定は null/N/A を保持します。

アプリ平均 USD/query：0.0006; 報告された tokens：{'embedding_tokens': 1600, 'input_tokens': 51133, 'output_tokens': 17128, 'total_tokens': 69861, 'complete': True}.
独立評価：{'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'completed', 'judge_cost_usd': 0.156276, 'judge_errors': 0}。Judge の時間・費用はアプリ query の指標から除外します。
query worker 2 個で 1 回実行し、事前実行はありません。アプリ時間は評価処理と待ち行列を除き、Judge 費用は別集計です。

## 問題ごとの結果

| ID | 分類 | 状態 | Recall@k | 参照事実の語彙カバレッジ | 合計 ms |
|---|---|---|---:|---:|---:|
| boreal-en-01 | current_version | answered | 1.0000 | N/A | 4682.73 |
| boreal-en-02 | old_version | answered | 1.0000 | N/A | 2451.05 |
| boreal-en-03 | similar_document | answered | 1.0000 | N/A | 3576.47 |
| boreal-en-04 | numeric_trap | insufficient_evidence | 0.0000 | N/A | 6387.92 |
| boreal-en-05 | negation | answered | 1.0000 | N/A | 6580.75 |
| boreal-en-06 | exception | answered | 1.0000 | N/A | 2987.20 |
| boreal-en-07 | exception_denied | answered | 1.0000 | N/A | 3364.26 |
| boreal-en-08 | negation | answered | 1.0000 | N/A | 3591.09 |
| boreal-en-09 | cross_document | answered | 0.6667 | N/A | 3991.16 |
| boreal-en-10 | cross_document | answered | 1.0000 | N/A | 5818.42 |
| boreal-en-11 | similar_document | answered | 1.0000 | N/A | 2660.73 |
| boreal-en-12 | draft_trap | answered | 1.0000 | N/A | 3812.10 |
| boreal-en-13 | negative | insufficient_evidence | N/A | N/A | 1770.33 |
| boreal-en-14 | negative | insufficient_evidence | N/A | N/A | 1398.21 |
| boreal-en-15 | negative | insufficient_evidence | N/A | N/A | 1739.26 |
| boreal-en-16 | adversarial | insufficient_evidence | N/A | N/A | 1342.41 |
| boreal-en-17 | negation | answered | 1.0000 | N/A | 3296.45 |
| boreal-en-18 | cross_document | answered | 1.0000 | N/A | 4866.27 |
| boreal-zh-01 | current_version | answered | 1.0000 | N/A | 3439.58 |
| boreal-zh-02 | old_version | answered | 1.0000 | N/A | 2840.57 |
| boreal-zh-03 | similar_document | answered | 1.0000 | N/A | 3419.26 |
| boreal-zh-04 | numeric_trap | answered | 0.0000 | N/A | 6654.49 |
| boreal-zh-05 | negation | answered | 1.0000 | N/A | 3090.74 |
| boreal-zh-06 | exception | answered | 1.0000 | N/A | 3261.49 |
| boreal-zh-07 | exception_denied | answered | 1.0000 | N/A | 4973.70 |
| boreal-zh-08 | negation | answered | 1.0000 | N/A | 5135.40 |
| boreal-zh-09 | cross_document | answered | 0.6667 | N/A | 2996.01 |
| boreal-zh-10 | cross_document | answered | 1.0000 | N/A | 5401.79 |
| boreal-zh-11 | similar_document | answered | 1.0000 | N/A | 3916.84 |
| boreal-zh-12 | draft_trap | answered | 0.5000 | N/A | 4890.84 |
| boreal-zh-13 | negative | insufficient_evidence | N/A | N/A | 2041.90 |
| boreal-zh-14 | negative | insufficient_evidence | N/A | N/A | 1622.09 |
| boreal-zh-15 | negative | insufficient_evidence | N/A | N/A | 1470.39 |
| boreal-zh-16 | adversarial | insufficient_evidence | N/A | N/A | 1856.16 |
| boreal-zh-17 | negation | answered | 1.0000 | N/A | 2420.54 |
| boreal-zh-18 | cross_document | answered | 1.0000 | N/A | 4582.45 |
| boreal-ja-01 | current_version | answered | 1.0000 | N/A | 3805.51 |
| boreal-ja-02 | old_version | answered | 1.0000 | N/A | 3424.46 |
| boreal-ja-03 | similar_document | answered | 1.0000 | N/A | 2917.03 |
| boreal-ja-04 | numeric_trap | answered | 0.0000 | N/A | 7134.87 |
| boreal-ja-05 | negation | answered | 1.0000 | N/A | 5450.55 |
| boreal-ja-06 | exception | answered | 1.0000 | N/A | 5271.49 |
| boreal-ja-07 | exception_denied | answered | 1.0000 | N/A | 3708.91 |
| boreal-ja-08 | negation | answered | 1.0000 | N/A | 3478.54 |
| boreal-ja-09 | cross_document | answered | 0.6667 | N/A | 4589.99 |
| boreal-ja-10 | cross_document | answered | 1.0000 | N/A | 4349.82 |
| boreal-ja-11 | similar_document | answered | 1.0000 | N/A | 4180.82 |
| boreal-ja-12 | draft_trap | answered | 1.0000 | N/A | 4950.11 |
| boreal-ja-13 | negative | insufficient_evidence | N/A | N/A | 1820.34 |
| boreal-ja-14 | negative | insufficient_evidence | N/A | N/A | 1400.30 |
| boreal-ja-15 | negative | insufficient_evidence | N/A | N/A | 1217.22 |
| boreal-ja-16 | adversarial | insufficient_evidence | N/A | N/A | 1288.59 |
| boreal-ja-17 | negation | answered | 1.0000 | N/A | 7270.58 |
| boreal-ja-18 | cross_document | answered | 0.5000 | N/A | 7244.55 |

## 制約

- テンプレートを共有する多言語ケースには関連性があり、統計的に独立した標本ではありません。
- dev/test は組織名と数値を分けていますが、ルールのテンプレートは共有します。
- 参照根拠はページ単位で、検索の再現率は全事実の網羅性を保証しません。
- 代表的な実文書による人手レビューが引き続き必要です。
- ページテキストは PDF 解析後から扱います。PDF の一連の処理は live_smoke で検証します。
