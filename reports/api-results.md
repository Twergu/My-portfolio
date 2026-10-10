# 実 API の実験結果と費用

モデル：text-embedding-3-small → gpt-5.6-luna → gpt-5.6-luna。独立 Judge：gpt-4.1。

データ：policy-challenge-v2.1。6 dev 設定後に 900/0 を凍結し、選択した設定のみ test を実行。

| test 指標 | スコア | 件数 |
|---|---:|---:|
| answer_correctness | 83.33% | 42 |
| citation_groundedness | 100.00% | 36 |
| refusal_accuracy | 85.19% | 54 |
| quote_match_failure | 0.00% | 54 |
| unsupported_answer | 5.56% | 54 |
| false_refusal | 16.67% | 42 |
| grounding_rejected_correct_and_grounded | 100.00% | 3 |

Citation Groundedness は回答済みの主張支持率を問題ごとに平均し、拒否には採点対象の回答がありません。False Refusal は生成拒否と検証遮断を含み、すべて Verifier の誤りとは解釈できません。

## 分割の効果と選択範囲

| 同じテキスト境界を生む設定 | Chunk 数 |
|---|---:|
| 450/0 | 100 |
| 450/60 | 100 |
| 900/0, 900/120, 1200/120, 1200/180 | 96 |

dev の最高スコアで test 設定を凍結しましたが、1 回で普遍的最適性は示せません。同じ境界の設定間の差を Size/Overlap に帰属させず、長い実ページでの拡充が必要です。ページ再現率は全事実の再現率ではありません。

## 独立した Verifier モデルの実験

450/0 dev、strict、Luna 生成で比較。各設定で別に 1 回生成し、回答の確率的な差を残しています。

| Verifier | 正確性 | 誤拒否率 | P50 / P95 ms | 平均 USD/query |
|---|---:|---:|---:|---:|
| gpt-5.6-luna | 78.57% | 21.43% | 6866.2 / 11097.7 | 0.00086741 |
| gpt-4.1-mini | 80.95% | 19.05% | 5641.6 / 10082.1 | 0.00089413 |

別 Verifier を実際に呼べることは確認しましたが、変更が必ず改善する証明には不足します。依頼者が選んだ低費用の Luna/Luna 基準を維持します。

[off / fast / strict 比較](verification/comparison.md)を参照してください。off/fast は実行時の意味的支持を保証せず、この test 結果でプロンプトやモデルを再選択しません。

## 費用台帳

| 実行レポート | USD |
|---|---:|
| [chunks-api/chunk-api-1200-120-dev.json](chunks-api/chunk-api-1200-120-dev.json) | 0.18900416 |
| [chunks-api/chunk-api-1200-180-dev.json](chunks-api/chunk-api-1200-180-dev.json) | 0.19583936 |
| [chunks-api/chunk-api-450-0-dev.json](chunks-api/chunk-api-450-0-dev.json) | 0.20311336 |
| [chunks-api/chunk-api-450-60-dev.json](chunks-api/chunk-api-450-60-dev.json) | 0.18791012 |
| [chunks-api/chunk-api-900-0-dev.json](chunks-api/chunk-api-900-0-dev.json) | 0.19426016 |
| [chunks-api/chunk-api-900-120-dev.json](chunks-api/chunk-api-900-120-dev.json) | 0.19017516 |
| [chunks-api/chunk-api-selected-test.json](chunks-api/chunk-api-selected-test.json) | 0.18892072 |
| [api-baseline-v1/chunk-api-900-120-dev.json](api-baseline-v1/chunk-api-900-120-dev.json) | 0.16256296 |
| [verifier-models/mini-450-0-dev.json](verifier-models/mini-450-0-dev.json) | 0.20190656 |
| [verification/off.json](verification/off.json) | 0.18726352 |
| [verification/fast.json](verification/fast.json) | 0.18226592 |
| [live-api-smoke.json](live-api-smoke.json) | 0.00026316 |
| [live-ui-smoke.json](live-ui-smoke.json) | 0.00132072 |

記録された既知の推定費用合計：USD **2.08480588**。費用情報の完全性：True。

独立 Judge、索引、診断基準、失敗後の追加採点を含みます。アプリ cost/query は各問の結果を参照し、評価費用を利用者の質問 1 回の費用と混同しません。再利用した strict と修正前スナップショットは二重計上しません。

## 制約

- テンプレートに関連性のある合成多言語制度で、人手ラベル付き本番データではありません。
- 設定ごとに 1 回。同じ境界では分割サイズ効果を立証できず、API の順位・生成・Judge の変動が残ります。
- Verifier の試験とモード比較は回答を再生成し、対応のある因果実験ではありません。
- Judge は自動判定で、引用スコアは回答済み出力にのみ適用します。
- 一律の設定価格と報告使用量による推定で、請求書ではありません。元 Judge の失敗費用は修正版に含み、回復スナップショットと再利用 strict を重複加算しません。
