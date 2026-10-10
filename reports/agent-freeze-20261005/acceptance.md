# 最終コード：24 問の Agent 凍結検収

2026-10-05、最終コード `9af3637b0853d638f972580786ed1decc9383e49` で 24 問の実 API 評価を 1 回すべて実行しました。**24/24 完了、Task Success 18/24（75%）**。実行後は結果の記録のみで、Prompt、アプリ、ツール契約、データ、参照回答、採点規則は変更せず、失敗問題も再実行していません。

## 実行と凍結の証跡

- [実行前のファイル一覧と SHA-256](freeze-manifest.json)：最終 Git コミット、全ケース、コード・Prompt・評価スクリプト・旧レポートのハッシュ。
- [実行後の整合性検査](integrity-check.json)：コード・Prompt・旧レポートの不変性、データとバックエンドのハッシュ一致、元の順序で 24 ID が各 1 回出現すること。
- [元 JSON](evaluation-live.json)：Generator Output、Evidence、Verifier Verdict、Planner/ツール trace、Judge、使用量、全失敗。
- [問題・段階別時間](evaluation-live.md)、[集計と費用詳細](acceptance-summary.json)、[前回の全件開発評価との比較](comparison.md)。

Embedding は `text-embedding-3-small`、Planner/Generator/Verifier は `gpt-5.6-luna`、独立 Judge は `gpt-4.1`。実 PDF 解析、Embedding、Hybrid Retrieval、モデル生成・検証・採点を実行し、検索は隔離 SQLite です。Calendar の営業週は明示的な Mock、Calculator は決定的計算。Strict/all と ACL を有効にしています。以前の実 PostgreSQL/pgvector と Docker CI は別の検証経路で、今回は再実行せず、live API + PostgreSQL 検収とは呼びません。

全件を 1 回実行したコマンド（既存出力への上書きは禁止）：

```powershell
python -m scripts.agent_evaluate --live --label final-code-freeze-9af3637 --output reports/agent-freeze-20261005/evaluation-live.json
```

既存の HTTP 再試行と最大 1 回の形式修正は変更していません。今回は HTTP 再試行なし。日本語通勤の初回で既存の Generator 形式修正を 1 回実行しました。凍結した実行時動作であり、失敗を見て追加実行したものではありません。

## 全件結果

| 指標 | 凍結結果 |
| --- | ---: |
| 完了問題数 | 24/24 |
| Task Success | 18/24（75.00%） |
| Planning Success | 22/24（91.67%） |
| Tool Selection Accuracy | 22/24（91.67%） |
| Clarification Accuracy | 24/24（100.00%） |
| Answer Correctness | 13/18（72.22%） |
| Grounded Answer Rate | 13/18（72.22%） |
| 回答済み出力の自動 Groundedness | 13/13（100.00%） |
| ツール呼び出し | 29 回、平均 1.2083 回/task |
| アプリ P50 / P95 | 12.189 / 24.922 秒 |
| 平均アプリ費用 | USD 0.00257939/task |
| アプリ token usage | 205,692：input 184,020、output 20,905、embedding 767 |
| ケース例外 / 元 chat 呼び出し例外 | 0 / 0 |
| HTTP 再試行 / 重複ツール呼び出し | 0 / 0 |

終状態は 13 answered、4 unsupported_answer、1 needs_input、5 unavailable、1 insufficient_evidence。6 件の失敗を分母に含めます。Correctness/Grounded は回答可能な全 18 件が分母で、13/13 は回答済み集合のみを表し全体品質を代替しません。Clarification Accuracy は指定された追加質問が発生したかのみで、質問内容やタスク完了を測りません。

**呼び出し数の定義：** 凍結採点器の `planner_calls_per_task=2.2083` は計画 trace 53 イベントから算出します。元モデル記録は実際には Planner 48 回（2.0 回/task）。`unavailable` が同名 trace を 2 回生成するため、イベント数が実呼び出し数を超えます。両方を記録し、採点器と元値は変えません。Generator 20 回、Verifier 16 回、Judge 26 回で、検索 Embedding は別途アプリ使用量に含めます。

## 6 件の失敗と元判定

| ケース | 結果と記録 |
| --- | --- |
| `purchase-limit-zh` | Generator は再び「办公用品每单金额不超过5000日元」と生成。Verifier が承認分岐額と絶対上限の違いを識別し、第 1 主張を拒否、3/4 支持。誤りは遮断されたがタスクは失敗 |
| `commuter-clarify-ja` | 確認後に再開。Verifier は「自己申告から勤務日数条件を満たす」という主張の支持が不十分とし、第 1 主張を拒否、2/3 支持。新候補は独立した人手裁定をしておらず、元判定を保持 |
| `remote-clarify-zh` | 固定返信で試用期間と週一日を示したが、Agent は従業員区分を再質問。検索未実行・未完了。利用者の代わりに情報を追加しない |
| `training-clarify-ja` | 構造化計算参照は存在。第 4 主張が User Input のみで自己申告を言い直し、バックエンドの `applicable_document_required` で遮断。全回答は意味的 Verifier に未到達で、計算誤りや Verifier 誤判定には分類しない |
| `leave-mock-window-zh` | サーバー描画のカレンダー計算は支持。Verifier は第 3 主張「Mock 日暦では許可を確定できない」を、引用が permission を直接述べていないとして拒否。2/3 支持 |
| `unavailable-grant-zh` | 最後は正しく `unavailable` を返し、権限付与もしなかったが、先に Knowledge Search を呼び、凍結 `allowed_tools=[]` に違反。ツール選択・計画・タスクは失敗 |

元出力と遮断位置の記録であり、新しい人手採点ではありません。失敗を成功に変更せず、この結果で Prompt や安全上の制約を調整していません。

## 前回全件実行との時間・費用比較

| 指標 | 前回の全件開発評価（最終修正前） | 最終コードの凍結評価 |
| --- | ---: | ---: |
| Task Success | 19/24 | 18/24 |
| Planning Success | 22/24 | 22/24 |
| Answer Correctness | 13/18 | 13/18 |
| Grounded Answer Rate | 15/18 | 13/18 |
| アプリ P50 / P95 秒 | 10.357 / 20.126 | 12.189 / 24.922 |
| USD/task | 0.002460 | 0.002579 |

今回の成功率、P50/P95、費用は前回より改善していません。最終コードの記録として維持します。生成は独立で確率的変動があり、全差分をコード変更に帰属させたり、過去の高スコアを最終結果としたりはできません。

| 段階 | P50 秒 | P95 秒 |
| --- | ---: | ---: |
| Planner | 4.273 | 9.058 |
| Knowledge Search | 0.167 | 0.417 |
| Calendar | 0.000 | 0.006 |
| Calculator | 0.000 | 0.006 |
| Generator | 4.138 | 11.080 |
| Verifier | 3.158 | 8.400 |

段階の分布は全タスクを分母とし、未実行段階はゼロです。親段階と HTTP/Embedding は重なり、重複加算できません。各段階の P50/P95 を足して全体の分位数にすることもできません。

| 費用の範囲 | 設定単価による推定 USD | Tokens |
| --- | ---: | ---: |
| アプリタスク合計 | 0.06190534 | 205,692 |
| 独立したオフライン Judge | 0.06787600 | 24,545 |
| 初期 PDF 索引 | 0.00001148 | 574 |
| 今回の全件評価合計 | 0.12979282 | 230,811 |

使用量は完全で、費用不明のタスクは 0。金額は応答 usage と設定価格による推定で、請求書の照合ではありません。タスク費用は初期索引・オフライン Judge を、アプリ時間は利用者の思考・索引・Judge を除きます。

## 凍結の範囲

既存 24 問で最終コードの動作を検収した記録です。開発に使った合成回帰セットで、未見テストでも、全問の人手レビュー済みセットでもありません。自動 Judge は業務上の正確性を保証しません。H01～H08 の人手校正は独立した候補セットで、この採点の置換には使いません。

アプリ、Prompt、Strict Verification、ACL、評価契約は不変です。当時の後続納品は本レポートと結果入口の追加のみでした。日本語化では説明文のみを翻訳し、凍結 JSON と元の判定を保持しています。元の Markdown とそのハッシュは翻訳前の Git 履歴で確認できます。
