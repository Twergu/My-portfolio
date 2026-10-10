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
| ndcg_at_k | 0.8109 | 42 |
| precision_at_k | 0.2476 | 42 |

返された Chunk の上限内でページの重複を除去します。precision の分母は未充足枠も含む k です。

| 回答指標 | 平均 | n |
|---|---:|---:|
| all_claims_grounded | 0.7143 | 42 |
| answer_correctness | 0.6905 | 42 |
| citation_groundedness | 1.0000 | 30 |
| claim_groundedness | 0.7619 | 42 |
| correct_refusal | 0.9167 | 12 |
| expected_facts_coverage_lexical | N/A | 0 |
| false_refusal | 0.3095 | 42 |
| generator_false_refusal | 0.0238 | 42 |
| grounding_false_refusal | 0.2857 | 42 |
| grounding_rejected_correct_and_grounded | 0.7500 | 12 |
| invalid_model_response | 0.0000 | 54 |
| quote_match_failure | 0.0556 | 54 |
| reference_exact_match | 0.0000 | 42 |
| reference_token_f1_lexical | 0.3290 | 42 |
| refusal_accuracy | 0.7407 | 54 |
| unsupported_answer | 0.2222 | 54 |
| withheld_candidate_correctness | 1.0000 | 12 |

local は回答を生成しないため回答品質は N/A。語彙カバレッジ / token F1 は意味的正確性を証明しません。実行時 claim_groundedness は Verifier 診断値、answer_correctness と citation_groundedness は別設定の評価 Judge の自動判定で、人手ラベルではありません。

| 所要時間 (ms) | p50 | p95 | n |
|---|---:|---:|---:|
| generation | 2573.8520 | 5026.3482 | 54 |
| provider_http | 5194.5355 | 8639.3372 | 54 |
| query_embedding | 321.7530 | 437.6913 | 54 |
| retrieval | 31.0060 | 122.8900 | 54 |
| verification | 2563.1220 | 5112.4336 | 39 |
| question_total | 5250.1360 | 8729.7730 | 54 |

索引作成：96 chunks, 25298.37 ms.
実行全体の API 費用 (USD)：0.1626。使用量不明や単価未設定は null/N/A を保持します。

アプリ平均 USD/query：0.0007; 報告された tokens：{'embedding_tokens': 1582, 'input_tokens': 64570, 'output_tokens': 18850, 'total_tokens': 85002, 'complete': True}.
独立評価：{'judge_model': 'gpt-4.1', 'independent_model': True, 'status': 'completed', 'judge_cost_usd': 0.126822, 'judge_errors': 0}。Judge の時間・費用はアプリ query の指標から除外します。
query worker 2 個で 1 回実行し、事前実行はありません。アプリ時間は評価処理と待ち行列を除き、Judge 費用は別集計です。

## 問題ごとの結果

| ID | 分類 | 状態 | Recall@k | 参照事実の語彙カバレッジ | 合計 ms |
|---|---|---|---:|---:|---:|
| aster-en-01 | current_version | answered | 1.0000 | N/A | 5357.81 |
| aster-en-02 | old_version | answered | 1.0000 | N/A | 5202.55 |
| aster-en-03 | similar_document | answered | 1.0000 | N/A | 5116.44 |
| aster-en-04 | numeric_trap | unsupported_answer | 0.0000 | N/A | 8243.10 |
| aster-en-05 | negation | unsupported_answer | 1.0000 | N/A | 5746.73 |
| aster-en-06 | exception | answered | 1.0000 | N/A | 4776.62 |
| aster-en-07 | exception_denied | answered | 1.0000 | N/A | 6658.61 |
| aster-en-08 | negation | answered | 1.0000 | N/A | 6829.91 |
| aster-en-09 | cross_document | unsupported_answer | 0.6667 | N/A | 7566.69 |
| aster-en-10 | cross_document | answered | 1.0000 | N/A | 8430.65 |
| aster-en-11 | similar_document | answered | 1.0000 | N/A | 4901.49 |
| aster-en-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 9153.70 |
| aster-en-13 | negative | insufficient_evidence | N/A | N/A | 2591.19 |
| aster-en-14 | negative | insufficient_evidence | N/A | N/A | 1598.50 |
| aster-en-15 | negative | insufficient_evidence | N/A | N/A | 1689.34 |
| aster-en-16 | adversarial | answered | N/A | N/A | 5102.66 |
| aster-en-17 | negation | answered | 1.0000 | N/A | 5297.72 |
| aster-en-18 | cross_document | answered | 1.0000 | N/A | 7488.31 |
| aster-zh-01 | current_version | answered | 1.0000 | N/A | 5385.25 |
| aster-zh-02 | old_version | answered | 1.0000 | N/A | 4312.02 |
| aster-zh-03 | similar_document | answered | 1.0000 | N/A | 4656.05 |
| aster-zh-04 | numeric_trap | answered | 0.0000 | N/A | 8501.51 |
| aster-zh-05 | negation | answered | 1.0000 | N/A | 4166.44 |
| aster-zh-06 | exception | answered | 1.0000 | N/A | 4895.06 |
| aster-zh-07 | exception_denied | answered | 1.0000 | N/A | 6495.98 |
| aster-zh-08 | negation | unsupported_answer | 1.0000 | N/A | 4397.05 |
| aster-zh-09 | cross_document | unsupported_answer | 0.6667 | N/A | 5889.13 |
| aster-zh-10 | cross_document | answered | 1.0000 | N/A | 7396.95 |
| aster-zh-11 | similar_document | unsupported_answer | 1.0000 | N/A | 7457.33 |
| aster-zh-12 | draft_trap | insufficient_evidence | 0.5000 | N/A | 2194.96 |
| aster-zh-13 | negative | insufficient_evidence | N/A | N/A | 1708.90 |
| aster-zh-14 | negative | insufficient_evidence | N/A | N/A | 1746.39 |
| aster-zh-15 | negative | insufficient_evidence | N/A | N/A | 1581.75 |
| aster-zh-16 | adversarial | insufficient_evidence | N/A | N/A | 1845.77 |
| aster-zh-17 | negation | answered | 1.0000 | N/A | 4184.89 |
| aster-zh-18 | cross_document | answered | 1.0000 | N/A | 6275.61 |
| aster-ja-01 | current_version | answered | 1.0000 | N/A | 6444.29 |
| aster-ja-02 | old_version | unsupported_answer | 1.0000 | N/A | 5359.54 |
| aster-ja-03 | similar_document | answered | 1.0000 | N/A | 4849.55 |
| aster-ja-04 | numeric_trap | unsupported_answer | 0.0000 | N/A | 3850.20 |
| aster-ja-05 | negation | answered | 1.0000 | N/A | 5148.06 |
| aster-ja-06 | exception | answered | 1.0000 | N/A | 5357.90 |
| aster-ja-07 | exception_denied | answered | 1.0000 | N/A | 6564.93 |
| aster-ja-08 | negation | answered | 1.0000 | N/A | 6478.28 |
| aster-ja-09 | cross_document | answered | 0.6667 | N/A | 11425.19 |
| aster-ja-10 | cross_document | answered | 1.0000 | N/A | 8416.88 |
| aster-ja-11 | similar_document | unsupported_answer | 1.0000 | N/A | 7138.53 |
| aster-ja-12 | draft_trap | unsupported_answer | 1.0000 | N/A | 12590.14 |
| aster-ja-13 | negative | insufficient_evidence | N/A | N/A | 1897.75 |
| aster-ja-14 | negative | insufficient_evidence | N/A | N/A | 1649.54 |
| aster-ja-15 | negative | insufficient_evidence | N/A | N/A | 1471.66 |
| aster-ja-16 | adversarial | insufficient_evidence | N/A | N/A | 1420.71 |
| aster-ja-17 | negation | answered | 1.0000 | N/A | 4788.32 |
| aster-ja-18 | cross_document | unsupported_answer | 0.5000 | N/A | 7657.00 |

## 制約

- テンプレートを共有する多言語ケースには関連性があり、統計的に独立した標本ではありません。
- dev/test は組織名と数値を分けていますが、ルールのテンプレートは共有します。
- 参照根拠はページ単位で、検索の再現率は全事実の網羅性を保証しません。
- 代表的な実文書による人手レビューが引き続き必要です。
- ページテキストは PDF 解析後から扱います。PDF の一連の処理は live_smoke で検証します。
