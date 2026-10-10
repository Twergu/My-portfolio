# 診断用ベースライン：置き換え済みの評価方式

最初の実 dev 54 問では、gold evidence と実引用を同じ Judge プロンプトへ渡しました。確認の結果、引用支持を採点する際に未引用の gold を借用する説明が見つかりました。この citation-groundedness と誤遮断の推定を最終品質結果として扱ってはいけません。

元の測定を追跡性と発生費用の記録のために保持します。評価器修正に test 問題は使っていません。新方式 `isolated-correctness-and-citations-v2` では正確性 Judge は参照を見ますが、別の引用 Judge は質問と候補の実引用だけを見ます。Generator にも連続した抜粋と、複数文書の主張に必要な全前提を要求します。

正式結果は `reports/chunks-api/` と `reports/verification/`。この基準は新方式の設定選択には再利用しません。日本語版は説明文の翻訳であり、元 JSON と過去の原文は維持しています。
