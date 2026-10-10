# 人手ラベルによる Verifier 校正

人手レビュー済みの候補・根拠ペア 8 件を実 Verifier API で評価しました。オフライン校正で、Agent 全体の品質評価ではありません。候補には意図的な誤りが 4 件あります。担当者は参照回答案を見ており、盲検や独立裁定ではありません。閾値ルールの開発に使ったため未見テストではありません。

```json
{
  "completed": 8,
  "expected": 8,
  "complete": true,
  "errors": 0,
  "agreement": 0.875,
  "tp": 3,
  "fp": 0,
  "fn": 1,
  "tn": 4,
  "precision": 1.0,
  "recall": 0.75
}
```
