# RAG 評価：policy-challenge-v2.1

モード：**api**; 分割：**test**; クエリ数：54.

実行状態：completed; 要求問題数：54; 索引エラー：none.

合成した種データのみを使用します。この結果は本番の正確性を保証しません。

| 検索指標（回答可能な問題のマクロ平均） | 平均 | n |
|---|---:|---:|
| recall_at_1 | 0.7857 | 42 |
| recall_at_3 | 1.0000 | 42 |
| recall_at_5 | 1.0000 | 42 |
| mrr_at_k | 0.9881 | 42 |
| ndcg_at_k | 0.9874 | 42 |
| precision_at_k | 0.2857 | 42 |

返された Chunk の上限内でページの重複を除去します。precision の分母は未充足枠も含む k です。

| 回答指標 | 平均 | n |
|---|---:|---:|
| all_claims_grounded | 0.9048 | 42 |
| answer_correctness | 0.9048 | 42 |
| citation_groundedness | 1.0000 | 38 |
| claim_groundedness | 0.9286 | 42 |
| correct_refusal | 1.0000 | 12 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | 0.0952 | 42 |
| generator_false_refusal | 0.0000 | 42 |
| grounding_false_refusal | 0.0952 | 42 |
| grounding_rejected_correct_and_grounded | 1.0000 | 4 |
| invalid_model_response | 0.0000 | 54 |
| quote_match_failure | 0.0000 | 54 |
| reference_exact_match | 0.0000 | 42 |
| reference_token_f1_lexical | 0.3779 | 42 |
| refusal_accuracy | 0.9259 | 54 |
| unsupported_answer | 0.0741 | 54 |
| withheld_candidate_correctness | 1.0000 | 4 |

local は回答を生成しないため回答品質は N/A。語彙カバレッジ / token F1 は意味的正確性を証明しません。実行時 claim_groundedness は Verifier 診断値、answer_correctness と citation_groundedness は別設定の評価 Judge の自動判定で、人手ラベルではありません。

| 所要時間 (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| generation | 4135.8460 | 7058.1643 | 54 |
| provider_http | 13869.5435 | 19889.7725 | 54 |
| query_embedding | 335.2250 | 504.4816 | 54 |
| reranking | 6776.2435 | 11459.0501 | 54 |
| retrieval | 15.7385 | 18.0750 | 54 |
| verification | 2501.0875 | 5175.1133 | 42 |
| question_total | 13904.6206 | 19922.9541 | 54 |

索引作成：96 chunks, 22738.28 ms.
実行全体の API 費用 (USD)：0.2790。使用量不明や単価未設定は null/N/A を保持します。

アプリ平均 USD/query：0.0020; 報告された tokens：{'embedding_tokens': 1600, 'input_tokens': 199565, 'output_tokens': 57980, 'total_tokens': 259145, 'complete': True}.
独立評価：{'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'completed', 'judge_cost_usd': 0.169298, 'judge_errors': 0}。Judge の時間・費用はアプリ query の指標から除外します。
query worker 2 個で 1 回実行し、事前実行はありません。アプリ時間は評価処理と待ち行列を除き、Judge 費用は別集計です。

## 問題ごとの結果

| ID | 分類 | 状態 | Recall@k | 参照事実の語彙カバレッジ | 合計 ms |
|---|---|---|---:|---:|---:|
| boreal-en-01 | current_version | answered | 1.0000 | N/A | 15208.30 |
| boreal-en-02 | old_version | answered | 1.0000 | N/A | 13618.40 |
| boreal-en-03 | similar_document | answered | 1.0000 | N/A | 12761.81 |
| boreal-en-04 | numeric_trap | answered | 1.0000 | N/A | 14547.39 |
| boreal-en-05 | negation | unsupported_answer | 1.0000 | N/A | 15999.99 |
| boreal-en-06 | exception | answered | 1.0000 | N/A | 14708.26 |
| boreal-en-07 | exception_denied | answered | 1.0000 | N/A | 15452.45 |
| boreal-en-08 | negation | answered | 1.0000 | N/A | 14306.15 |
| boreal-en-09 | cross_document | answered | 1.0000 | N/A | 16037.09 |
| boreal-en-10 | cross_document | answered | 1.0000 | N/A | 13681.70 |
| boreal-en-11 | similar_document | answered | 1.0000 | N/A | 14594.45 |
| boreal-en-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 14649.63 |
| boreal-en-13 | negative | insufficient_evidence | N/A | N/A | 8645.68 |
| boreal-en-14 | negative | insufficient_evidence | N/A | N/A | 6983.66 |
| boreal-en-15 | negative | insufficient_evidence | N/A | N/A | 9243.52 |
| boreal-en-16 | adversarial | insufficient_evidence | N/A | N/A | 5122.32 |
| boreal-en-17 | negation | answered | 1.0000 | N/A | 15074.36 |
| boreal-en-18 | cross_document | answered | 1.0000 | N/A | 14267.91 |
| boreal-zh-01 | current_version | answered | 1.0000 | N/A | 12592.26 |
| boreal-zh-02 | old_version | answered | 1.0000 | N/A | 17008.90 |
| boreal-zh-03 | similar_document | answered | 1.0000 | N/A | 12351.50 |
| boreal-zh-04 | numeric_trap | answered | 1.0000 | N/A | 20842.58 |
| boreal-zh-05 | negation | answered | 1.0000 | N/A | 13967.56 |
| boreal-zh-06 | exception | answered | 1.0000 | N/A | 12613.54 |
| boreal-zh-07 | exception_denied | answered | 1.0000 | N/A | 13810.93 |
| boreal-zh-08 | negation | answered | 1.0000 | N/A | 41174.90 |
| boreal-zh-09 | cross_document | answered | 1.0000 | N/A | 14933.37 |
| boreal-zh-10 | cross_document | answered | 1.0000 | N/A | 17767.34 |
| boreal-zh-11 | similar_document | answered | 1.0000 | N/A | 16099.31 |
| boreal-zh-12 | draft_trap | answered | 1.0000 | N/A | 22663.86 |
| boreal-zh-13 | negative | insufficient_evidence | N/A | N/A | 9258.36 |
| boreal-zh-14 | negative | insufficient_evidence | N/A | N/A | 8855.60 |
| boreal-zh-15 | negative | insufficient_evidence | N/A | N/A | 8313.67 |
| boreal-zh-16 | adversarial | insufficient_evidence | N/A | N/A | 10370.43 |
| boreal-zh-17 | negation | answered | 1.0000 | N/A | 13608.94 |
| boreal-zh-18 | cross_document | answered | 1.0000 | N/A | 12752.22 |
| boreal-ja-01 | current_version | answered | 1.0000 | N/A | 12871.65 |
| boreal-ja-02 | old_version | answered | 1.0000 | N/A | 14792.78 |
| boreal-ja-03 | similar_document | answered | 1.0000 | N/A | 13364.95 |
| boreal-ja-04 | numeric_trap | unsupported_answer | 1.0000 | N/A | 14954.94 |
| boreal-ja-05 | negation | answered | 1.0000 | N/A | 17798.87 |
| boreal-ja-06 | exception | answered | 1.0000 | N/A | 15550.50 |
| boreal-ja-07 | exception_denied | answered | 1.0000 | N/A | 15056.54 |
| boreal-ja-08 | negation | answered | 1.0000 | N/A | 15012.97 |
| boreal-ja-09 | cross_document | unsupported_answer | 1.0000 | N/A | 13841.68 |
| boreal-ja-10 | cross_document | answered | 1.0000 | N/A | 13737.84 |
| boreal-ja-11 | similar_document | answered | 1.0000 | N/A | 12725.84 |
| boreal-ja-12 | draft_trap | answered | 1.0000 | N/A | 19427.77 |
| boreal-ja-13 | negative | insufficient_evidence | N/A | N/A | 13609.64 |
| boreal-ja-14 | negative | insufficient_evidence | N/A | N/A | 10409.54 |
| boreal-ja-15 | negative | insufficient_evidence | N/A | N/A | 6823.29 |
| boreal-ja-16 | adversarial | insufficient_evidence | N/A | N/A | 5711.42 |
| boreal-ja-17 | negation | answered | 1.0000 | N/A | 17752.84 |
| boreal-ja-18 | cross_document | answered | 1.0000 | N/A | 12534.42 |

## 制約

- テンプレートを共有する多言語ケースには関連性があり、統計的に独立した標本ではありません。
- dev/test は組織名と数値を分けていますが、ルールのテンプレートは共有します。
- 参照根拠はページ単位で、検索の再現率は全事実の網羅性を保証しません。
- 代表的な実文書による人手レビューが引き続き必要です。
- ページテキストは PDF 解析後から扱います。PDF の一連の処理は live_smoke で検証します。
