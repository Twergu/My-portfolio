# RAG 評価：policy-challenge-v2.1

モード：**api**; 分割：**test**; クエリ数：54.

実行状態：completed; 要求問題数：54; 索引エラー：none.

合成した種データのみを使用します。この結果は本番の正確性を保証しません。

| 検索指標（回答可能な問題のマクロ平均） | 平均 | n |
|---|---:|---:|
| recall_at_1 | 0.7619 | 42 |
| recall_at_3 | 1.0000 | 42 |
| recall_at_5 | 1.0000 | 42 |
| mrr_at_k | 0.9762 | 42 |
| ndcg_at_k | 0.9805 | 42 |
| precision_at_k | 0.2857 | 42 |

返された Chunk の上限内でページの重複を除去します。precision の分母は未充足枠も含む k です。

| 回答指標 | 平均 | n |
|---|---:|---:|
| all_claims_grounded | N/A | 0 |
| answer_correctness | 0.9286 | 42 |
| citation_groundedness | 1.0000 | 40 |
| claim_groundedness | N/A | 0 |
| correct_refusal | 1.0000 | 12 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | 0.0476 | 42 |
| generator_false_refusal | 0.0476 | 42 |
| grounding_false_refusal | 0.0000 | 42 |
| invalid_model_response | 0.0000 | 54 |
| quote_match_failure | 0.0000 | 54 |
| reference_exact_match | 0.0000 | 42 |
| reference_token_f1_lexical | 0.3701 | 42 |
| refusal_accuracy | 0.9630 | 54 |
| unsupported_answer | 0.0000 | 54 |

local は回答を生成しないため回答品質は N/A。語彙カバレッジ / token F1 は意味的正確性を証明しません。実行時 claim_groundedness は Verifier 診断値、answer_correctness と citation_groundedness は別設定の評価 Judge の自動判定で、人手ラベルではありません。

| 所要時間 (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| generation | 3784.6145 | 7452.1552 | 54 |
| provider_http | 10470.6820 | 15261.4588 | 54 |
| query_embedding | 341.3315 | 630.1935 | 54 |
| reranking | 6494.5820 | 9922.3820 | 54 |
| retrieval | 15.1610 | 23.1396 | 54 |
| question_total | 10497.5124 | 15314.5513 | 54 |

索引作成：96 chunks, 23241.44 ms.
実行全体の API 費用 (USD)：0.2510。使用量不明や単価未設定は null/N/A を保持します。

アプリ平均 USD/query：0.0017; 報告された tokens：{'embedding_tokens': 1600, 'input_tokens': 174332, 'output_tokens': 47126, 'total_tokens': 223058, 'complete': True}.
独立評価：{'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'completed', 'judge_cost_usd': 0.159398, 'judge_errors': 0}。Judge の時間・費用はアプリ query の指標から除外します。
query worker 2 個で 1 回実行し、事前実行はありません。アプリ時間は評価処理と待ち行列を除き、Judge 費用は別集計です。

## 問題ごとの結果

| ID | 分類 | 状態 | Recall@k | 参照事実の語彙カバレッジ | 合計 ms |
|---|---|---|---:|---:|---:|
| boreal-en-01 | current_version | answered | 1.0000 | N/A | 8632.73 |
| boreal-en-02 | old_version | answered | 1.0000 | N/A | 10239.25 |
| boreal-en-03 | similar_document | answered | 1.0000 | N/A | 9014.48 |
| boreal-en-04 | numeric_trap | answered | 1.0000 | N/A | 10720.41 |
| boreal-en-05 | negation | answered | 1.0000 | N/A | 10305.47 |
| boreal-en-06 | exception | answered | 1.0000 | N/A | 10352.31 |
| boreal-en-07 | exception_denied | answered | 1.0000 | N/A | 10886.22 |
| boreal-en-08 | negation | answered | 1.0000 | N/A | 7308.61 |
| boreal-en-09 | cross_document | answered | 1.0000 | N/A | 12869.08 |
| boreal-en-10 | cross_document | answered | 1.0000 | N/A | 12008.22 |
| boreal-en-11 | similar_document | answered | 1.0000 | N/A | 10250.88 |
| boreal-en-12 | draft_trap | answered | 1.0000 | N/A | 9910.11 |
| boreal-en-13 | negative | insufficient_evidence | N/A | N/A | 8361.76 |
| boreal-en-14 | negative | insufficient_evidence | N/A | N/A | 8124.00 |
| boreal-en-15 | negative | insufficient_evidence | N/A | N/A | 7304.34 |
| boreal-en-16 | adversarial | insufficient_evidence | N/A | N/A | 7518.93 |
| boreal-en-17 | negation | answered | 1.0000 | N/A | 14366.98 |
| boreal-en-18 | cross_document | answered | 1.0000 | N/A | 12941.35 |
| boreal-zh-01 | current_version | answered | 1.0000 | N/A | 8087.88 |
| boreal-zh-02 | old_version | answered | 1.0000 | N/A | 11767.11 |
| boreal-zh-03 | similar_document | answered | 1.0000 | N/A | 10320.58 |
| boreal-zh-04 | numeric_trap | answered | 1.0000 | N/A | 16443.35 |
| boreal-zh-05 | negation | insufficient_evidence | 1.0000 | N/A | 11961.26 |
| boreal-zh-06 | exception | answered | 1.0000 | N/A | 8606.47 |
| boreal-zh-07 | exception_denied | answered | 1.0000 | N/A | 11679.91 |
| boreal-zh-08 | negation | answered | 1.0000 | N/A | 11859.16 |
| boreal-zh-09 | cross_document | answered | 1.0000 | N/A | 11287.88 |
| boreal-zh-10 | cross_document | answered | 1.0000 | N/A | 10582.99 |
| boreal-zh-11 | similar_document | answered | 1.0000 | N/A | 10696.45 |
| boreal-zh-12 | draft_trap | answered | 1.0000 | N/A | 11170.20 |
| boreal-zh-13 | negative | insufficient_evidence | N/A | N/A | 8468.11 |
| boreal-zh-14 | negative | insufficient_evidence | N/A | N/A | 8120.10 |
| boreal-zh-15 | negative | insufficient_evidence | N/A | N/A | 11268.58 |
| boreal-zh-16 | adversarial | insufficient_evidence | N/A | N/A | 6074.02 |
| boreal-zh-17 | negation | answered | 1.0000 | N/A | 10207.33 |
| boreal-zh-18 | cross_document | answered | 1.0000 | N/A | 11093.19 |
| boreal-ja-01 | current_version | answered | 1.0000 | N/A | 13149.68 |
| boreal-ja-02 | old_version | answered | 1.0000 | N/A | 9019.37 |
| boreal-ja-03 | similar_document | answered | 1.0000 | N/A | 8286.75 |
| boreal-ja-04 | numeric_trap | insufficient_evidence | 1.0000 | N/A | 11582.89 |
| boreal-ja-05 | negation | answered | 1.0000 | N/A | 12063.43 |
| boreal-ja-06 | exception | answered | 1.0000 | N/A | 8104.05 |
| boreal-ja-07 | exception_denied | answered | 1.0000 | N/A | 10412.04 |
| boreal-ja-08 | negation | answered | 1.0000 | N/A | 16955.56 |
| boreal-ja-09 | cross_document | answered | 1.0000 | N/A | 14445.87 |
| boreal-ja-10 | cross_document | answered | 1.0000 | N/A | 15806.01 |
| boreal-ja-11 | similar_document | answered | 1.0000 | N/A | 10797.21 |
| boreal-ja-12 | draft_trap | answered | 1.0000 | N/A | 15049.92 |
| boreal-ja-13 | negative | insufficient_evidence | N/A | N/A | 8873.96 |
| boreal-ja-14 | negative | insufficient_evidence | N/A | N/A | 12126.44 |
| boreal-ja-15 | negative | insufficient_evidence | N/A | N/A | 7961.51 |
| boreal-ja-16 | adversarial | insufficient_evidence | N/A | N/A | 9104.75 |
| boreal-ja-17 | negation | answered | 1.0000 | N/A | 9106.82 |
| boreal-ja-18 | cross_document | answered | 1.0000 | N/A | 11670.40 |

## 制約

- テンプレートを共有する多言語ケースには関連性があり、統計的に独立した標本ではありません。
- dev/test は組織名と数値を分けていますが、ルールのテンプレートは共有します。
- 参照根拠はページ単位で、検索の再現率は全事実の網羅性を保証しません。
- 代表的な実文書による人手レビューが引き続き必要です。
- ページテキストは PDF 解析後から扱います。PDF の一連の処理は live_smoke で検証します。
