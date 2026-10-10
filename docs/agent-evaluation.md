# Agent 評価プロトコル

`evals/agent_dataset.json` は中国語・日本語・英語の架空企業タスク 24 件を凍結したもので、`python -m evals.make_agent` で再構築できます。制度 Q&A、個人条件不足による複数ターンの確認、複数制度の計算・日付、書き込みツールの不在、制度なし、実カレンダーの不在を含みます。架空制度 8 件を単一の複数ページ PDF にまとめています。複数制度の質問では物理ページをまたいで検索しますが、この評価で複数 PDF を網羅したとは主張しません。データと参照回答は AI 作成で、**人手レビュー未実施**です。本番の正確性を示しません。

実行前に `.env` へ既存 API 設定と独立した `RAG_EVAL_JUDGE_MODEL` を設定します。

```powershell
python -m scripts.agent_evaluate --live --label baseline --output reports/agent-hardening/evaluation-baseline-live.json
```

新しい出力名を指定してください。既存実験への上書きは拒否します。隔離した一時 DB で、実 PDF 解析、実 Embedding、SQLite Hybrid Retrieval、実 Planner/Generator/Strict Verifier を使います。Calculator は決定的な十進計算、Calendar は明示的な Mock 営業週です。権限は検索前に適用し、モデルは範囲を拡大できません。メール送信や申請提出などの書き込みはありません。本番 PostgreSQL/pgvector は別 CI で検収し、この SQLite 実行を PostgreSQL 性能テストとは呼びません。

各シナリオは独立した状態を持ち、事前に書いた利用者の返信を最大 1 回だけ追加します。評価器がその場で不足条件を補うことはしません。24 件すべてを残し、エラー、遮断、追加質問の継続による未完了も失敗に含めます。各問題後に JSON/Markdown を保存し、中断時は completed/expected を明記します。中断結果は全件結果ではありません。元の日本語失敗は `agent-ja-regression.json` と初期診断に保存し、このセットにも同じ複数ターン問題を含めます。

## 指標

- **Tool Selection Accuracy**：試みたツール集合が required を含み、allowed を超えず、ツールエラーがないこと。重複・不正呼び出しを正解と扱いません。
- **Clarification Accuracy**：追加質問の有無が「必須」のラベルと一致する割合。参照返信は実際に質問された場合のみ与えます。
- **Planning Success**：ツールと追加確認が正しく、回答可能な問題は ready、回答なしは許可された unavailable/insufficient_evidence に到達したこと。最終 Generator の成否には依存しません。
- **Task Success**：Planning Success と正しい終状態。回答可能な問題は独立 Judge の Correctness、各引用の Groundedness、実行時 Strict のすべてが通過する必要があります。
- **Answer Correctness / Grounded Answer Rate**：分母は誤拒否・例外を含む回答可能な全タスク。grounded_rate_among_delivered は回答済みのみの補助指標で、全体の成功率を代替しません。
- **Tool Calls / Planner Calls**：最終的な累積 trace から数え、追加確認前後を重複加算しません。
- **Latency**：各 API 入力に対するアプリ処理時間を合計し、利用者の思考、索引、オフライン Judge を除外します。Planner、Knowledge Search、Calendar、Calculator、Generator、Verifier の各時間も保持。検索は Embedding を含み、段階時間と HTTP 時間の重複加算はできません。
- **Cost**：応答 token usage と設定単価からタスクあたりのアプリ費用を推定。索引と Judge は別集計。不明費用は null とし、ゼロにはしません。

独立 Judge は正確性と引用を別々の 2 呼び出しで評価します。正確性には参照回答と必要文書を渡し、引用 Judge には候補と実引用のみを渡します。欠けた根拠を gold から補うことはできません。どちらも実行時 Verifier verdict は見ません。自動 Judge も誤るため、失敗は原文と照合する必要があります。

オフラインスクリプトは Generator Output、Evidence、Verifier Verdict、全モデルリクエスト本文を保存します。架空データの診断専用であり、非公開の本番データをこの平文診断に使わないでください。テストの制御済み応答は採点と実装契約を検証するもので、実 API の結果とは区別します。

## 計算と人手による校正

`--case` は複数指定でき、例は `--case commuter-clarify-ja --case training-clarify-ja` です。選択 ID と全データセットのハッシュを記録します。部分集合は全件結果を代替せず、未完了・拒否・エラーも削除しません。旧「追加質問が必須」ラベルを維持するため、正しい条件付き説明を直接返しても旧契約上は失敗になる場合があります。

[agent-human-review-v1](agent-human-review-v1.md) は独立した 8 候補の校正セットで、意図的な誤りと元の失敗を含みます。依頼者が各問をレビュー済みで、発言は annotations に保存しました。上の 24 タスクすべての人手レビューを意味しません。作成時の `awaiting_human_review` は内容ハッシュを維持するため変更せず、現在の状態は記名 annotations とレビュー報告で確定します。

次のコマンドには新しい出力名が必要です。`--live` は実 API を呼び出します。

```powershell
python -m scripts.human_review_report --annotations evals/agent-human-review-v1.annotations.json --output reports/review-new.json
python -m scripts.agent_human_calibration --live --output reports/verifier-calibration-new.json
python -m scripts.agent_calculation_replay --live --output reports/calculation-replay-new.json
```

2 番目は人手ラベル 8 件と Verifier の一致を測ります。プロンプト開発に使用したため未見テストではありません。3 番目は保存した計算の誤拒否候補と別途用意した制度推論の反例のみを再検証します。Planner/Generator は再実行せず、新しい E2E 成功率とは扱いません。両方でモデル原文・使用量を保存します。版、失敗、性能、制約は[変更報告](agent-followup-report.md)を参照してください。
