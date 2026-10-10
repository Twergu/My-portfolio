# 第 2 回改善：項目別の変更方針と検収

> 過去の作業記録です。ACL、Hybrid、Reranker を追加した段階の状態は[次の 12 項目](retrieval-optimization-report.md)を参照してください。

`policy-challenge-v2.1` を使用。2026-09-15 に依頼者が利用枠を追加した後、実 API 検証を再開し、回答、検証、費用を実呼び出し記録から計算しました。`codex/rag-quality-v2` ブランチに公開し、実 CI とバージョンは [Actions](https://github.com/Twergu/My-portfolio/actions/workflows/ci.yml?query=branch%3Acodex%2Frag-quality-v2) と [README 実験概要](../README.md)を基準とします。未完了実験を通過とは扱いません。

| # | 要求 / 方針 | 実装と効果 | 検収範囲 |
|---|---|---|---|
| 1 | 実 Embedding + LLM | 2 ページ PDF の実 E2E smoke。残高不足を識別し、無条件の再試行を停止 | 枠追加後に解析、Embedding、構造化生成、quote/claim 検証、2 ページ目の引用を通過。[結果](../reports/live-api-smoke.md) |
| 2 | 高難度 Evaluation Dataset | 48 文書、96 ページ、108 問。中国語・日本語・英語、旧・新・草案、類似制度、数値、否定、例外、複数文書、回答なし | 構造・ページ根拠を検証。同言語の競合版を検索範囲に保持。テンプレートに関連性があり、人手の独立評価ではない |
| 3 | 実 RAG 品質評価 | Recall@1/3/5、MRR、nDCG。入力を分離した 2 Judge 呼び出しで Correctness / Citation Groundedness、Refusal Accuracy | [凍結 test](../reports/chunks-api/chunk-api-selected-test.md)に実モデル結果。原文検索を生成品質の代用にしない |
| 4 | 実験による Chunk 選択 | 6 API 設定を完了。dev のみで 900/0 を選び、凍結後に test | [API 比較](../reports/chunks-api/chunk-experiment-api.md)。900/1200 の 4 設定は同じ境界で、差をパラメーター効果と断定しない。ローカル例は 900/0、汎用既定値は維持し長いページでの検証待ち |
| 5 | Verifier 誤拒否分析 | quote_mismatch、unsupported_answer、invalid_model_response、false_refusal を分離し、遮断候補を独立 Judge で再評価 | 各 JSON に実候補。引用 Judge へ gold evidence を渡さず、未引用根拠で支持を過大評価しない。公開 HTTP は遮断候補を返さない |
| 6 | Generator / Verifier 分離 | chat_model、verifier_model を独立化。Luna と gpt-4.1-mini Verifier で各 dev 全件を実測 | [モデル実験](../reports/api-results.md)。Mini は正答が 1 問多いだけで回答も別生成のため、改善の証明には不足。低費用の基準を維持。Embedding profile には影響しない |
| 7 | Verification モード | off：schema/出典番号、fast：原文 quote も確認、strict：モデルで主張も検証 | [3 モード実測](../reports/verification/comparison.md)完了。strict は誤遮断と追加時間・費用があり、off/fast を実行時の意味検証済みと扱わない |
| 8 | PostgreSQL 検収 | GitHub Linux runner の実 pgvector。CI にテスト URL を必須化し、skip は失敗扱い | Actions から実 DB 結果を取得して保存。README 参照。ローカルには PostgreSQL 未導入 |
| 9 | 1k/10k/100k Exact vs HNSW | 同 seed、384 次元、20 クエリ、3 回。独立 float64 NumPy 正解、事前実行を除外。構築時間、サイズ、計画、再現率 | GitHub の実 PostgreSQL で実行。完了のみ measured とし、ANN の優位性を前提にしない |
| 10 | HNSW ライフサイクル | 作成を書き込みトランザクション・保守へ移動。再構築・削除で不要 profile 索引を整理。検索時は DDL なし | 実 PG で旧索引整理、索引欠落エラー、格納前準備、削除後の整理を検証 |
| 11 | Docker 全起動 | 初回に DB のランダムパスワードを作り専用永続ボリュームへ保存。.env なしで docker compose up | CI でビルド、ヘルスチェック、PDF 格納、実 HTTP 引用、再起動時の保持を検証 |
| 12 | GitHub Actions 全通過 | 独立ブランチで通常/PG テスト、両 DB・規模比較、Docker を実行 | 実ワークフローの結論に従い、未完了を成功としない |
| 13 | Latency / Cost | 役割、モデル単価、tokens、平均 cost/query、P50/P95。Judge とアプリ query を分離 | 実時間・usage から DB/local/API データを生成。不明使用量は不明のまま。README と実験 JSON 参照 |
| 14 | README で成果を表示 | 動的 CI badge、高難度・Chunk・Vector 表、リンク付きレポートを JSON から更新 | テスト通過数を手入力せず、範囲と欠測を表示 |
| 15 | 後続 ACL | 次段階で User / Role / Document Permission を設計し、検索前にサーバー側の許可文書集合を解決。PDF、抜粋、一覧も対象 | 依頼の順序に従い次段階へ。この時点では未実装で単一ユーザー |
| 16 | さらに後続の Audit Log | 認証ユーザー、質問、候補・実引用文書、拒否、時刻、リクエスト ID を ACL と連携して記録 | 未実装。性能ログをユーザー監査ログとは呼ばない |
| 17 | 最後に Agent | 実 RAG 評価、pgvector、Docker/CI、アクセス境界が安定してからワークフローとツールを導入 | この段階では LangGraph / Agent を追加せず、RAG の基礎を整備 |

## 指標の解釈

Recall は実 Top-K Chunk を切り出してから物理ページを重複除去します。重複の代わりに上限外の関連ページを補いません。高難度セットでは語彙別名の一致を正解とせず、数値一致を意味的正確性と扱いません。Answer Correctness は参照回答、質問範囲、gold evidence に基づき独立 Judge が完全性と誤りを判定します。Citation Groundedness は実引用のみで判定します。いずれも自動評価で、人手の標本確認が必要です。

`false_refusal` は回答可能な問題に回答を返さなかった割合で、生成時の拒否と検証遮断を含みます。全遮断が不適切という意味ではありません。`grounding_rejected_correct_and_grounded` が、遮断候補のうち独立 Judge が正確かつ根拠ありとした割合です。Judge 未設定やエラー時に完全な品質検収とは報告できません。

独立 Judge も正解の保証ではありません。[3 件の不一致の再確認](../reports/grounding-case-review.md)では、「税抜き」という追加主張に原文の根拠がないのに Judge が正しいとしました。この例で実行時の遮断は妥当です。元の測定を維持し、自動スコア、事後の Codex 分析、将来の独立した人手検収を区別します。

ローカル Chunk 比較ではページが設定値より短く、一部設定の境界が一致しました。長い実資料で再実験が必要です。物理ページ境界は [ADR 0001](adr/0001-physical-page-chunks.md) に従います。

実 API の全概要、同じ境界の設定群、Verifier 実験、重複計上を避けた費用台帳は[実験報告](../reports/api-results.md)を参照してください。test の strict 正確性、引用支持、拒否精度、各失敗を公開し、回答済みの引用高得点で未回答を隠しません。Judge の形式エラー 1 件は元の回答だけ再評価し、失敗と費用を保存しました。形式再試行は最大 1 回で、回復しなければ実験は失敗です。

日本語ブラウザー検収では非同期保存・再構築の通知、動的ナビゲーション見出し、引用パネルの未翻訳ボタンも修正しました。PDF 原文とファイル名は元言語を維持。実モデルの日本語回答と中国語 PDF 引用は独立ブラウザー smoke として記録し、凍結 test に混ぜません。

## テストと認証情報の分離

pytest はアプリ import 前に実 API key を除去し、実 HTTPTransport の通信を禁止します。PostgreSQL ドライバーは明示したテスト DB に接続できます。実 API smoke は別の明示的スクリプトです。.env、ユーザーデータ、キャッシュ、テスト一時ファイルは ZIP と Git に含めず、公開同期時もローカルキーの混入を検査します。
