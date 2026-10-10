# 日本語資料の範囲と評価原本

2026-10-10 に、詳細評価、変更報告、共有・デプロイ手順を日本語化しました。README、ソース一覧、セキュリティ説明、docs 内の設計・Agent 各段階・人手レビュー資料、evals の評価方式、reports 内の全 Markdown が対象です。歴史的報告の未完了・失敗・通過は当時の状態として維持しています。

数値、分母、失敗ケース、モデル名、ケース ID、実行日時、Git コミット、コマンド、リンクを維持します。表の識別子（answered、unsupported_answer、task_success など）は JSON と照合できるよう元のままです。意味は[Agent 評価](agent-evaluation.md)と[RAG 指標](../evals/README.md)を参照してください。

評価 JSON、データセット、人手 annotations、モデル出力、画像、画面取得テキスト、アプリ・テスト・実験スクリプトは変更していません。中国語・英語の元質問や引用は、検証の証跡として残ります。人手資料の日本語訳は閲覧補助であり、日本語訳に対して新たな人手レビューを行ったという意味ではありません。

翻訳前の全文は [Git コミット aac72b1](https://github.com/Twergu/My-portfolio/tree/aac72b18a278f6207ad897eacea8122df3cfa382) に残っています。[元の凍結検収文](https://github.com/Twergu/My-portfolio/blob/aac72b18a278f6207ad897eacea8122df3cfa382/reports/agent-freeze-20261005/acceptance.md)も参照できます。freeze-manifest、integrity-check、CI provenance に記録された Markdown のハッシュは、その実行時の原文に対するものです。翻訳版のバイト列に一致させるために過去の証跡を書き換えていません。元 JSON のハッシュは不変です。

これは文書のみの更新で、新しい API 評価、Prompt 調整、再採点、性能測定は実施していません。最終モデル評価は引き続き [24 問の凍結結果](../reports/agent-freeze-20261005/acceptance.md)です。アプリの CI 成績は、そのレポートが示すコード版の結果として扱います。

既存の生成スクリプトの言語は変更していません。実験・集計・ソース一覧を再生成すると、そのスクリプトの中国語または英語の文面に戻る場合があります。再実験は新しい出力先へ保存し、凍結結果を上書きしないでください。この日本語版は、保存済み測定の表示用スナップショットです。

公開前に相対リンク、実行可能なコードブロック、表中の数値、非 Markdown のハッシュを照合しました。検査範囲と結果は[日本語化の検査記録](../reports/localization-ja/validation.json)に保存します。ソース ZIP も日本語版の文書で更新します。
