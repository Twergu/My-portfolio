# 最初の v3 CI スナップショット

[CI 35039880066](https://github.com/Twergu/My-portfolio/actions/runs/35039880066) の成果物を保存した記録です。検証対象アプリは `07ae4e8419daf9e32b19146895fe113d8f332264`。当該段階の最終実行は `reports/ci-status.json`、その実測ベクトルは `reports/vector-scale.json` から確認できます。日本語化した Markdown は表示用の翻訳で、元 JSON と過去の原文は変更していません。

両実行とも skip ゼロのテスト条件を通過しました。HNSW 構築と共有 CI ハードウェアは変動し、10k、ef=400 の Recall は 0.95→0.91、100k、ef=1000 は 0.57→0.67。安定した本番閾値の証明ではありません。Exact を既定とし、各環境でフィルター適用後の実資料を評価する必要があります。
