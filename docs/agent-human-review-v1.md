# Agent の少数ケース人手レビュー資料

状態：**この対話の依頼者が 8/8 件をレビュー済み**。[署名付きラベル](../evals/agent-human-review-v1.annotations.json)に各問の発言と時刻、[レビュー結果](../reports/agent-followup/human-review-completed.json)に判定を保存しています。候補・参照案は AI 作成で、担当者は参照案を見ています。補助付きレビューであり独立盲検ではありません。

以下の日本語訳は閲覧補助で、新しい人手レビューではありません。評価に使用した質問・候補・制度の原文は保持しています。実ラベルは元データに紐付き、日本語訳を再採点していません。

当時の記入項目は候補の正確性、全主張の根拠、参照案への同意で、それぞれ「はい/いいえ」を指定します。不明点は理由を記し署名を保留し、担当名にはニックネームを使用できます。凍結データのハッシュに紐付け、旧評価は変更しません。返信例：`担当者：名前；H01：いいえ/いいえ/はい；H02：はい/はい/はい；...`。形式例は実ラベルではありません。

## H01

**質問（日本語）：** 事務用品は 1 件あたり最大 5,000 円までしか購入できませんか？

**制度の原文（agent-eval-policies.pdf、物理ページ 1）：**

> PROC-26 current purchasing policy: Office supplies costing at most 5000 JPY per order require a receipt and manager confirmation before purchase. Orders above 5000 JPY require procurement approval before purchase. Splitting an order to evade this limit is prohibited. A calculation within the limit does not constitute approval.

**評価対象候補（日本語訳）：** 現在の事務用品購入制度では、1 注文の上限は5000円です。

**確認点：** 承認経路と絶対的禁止を区別します。原文には 5,000 超の別承認経路があります。

**参照回答案（日本語訳・レビュー対象）：** 絶対購入上限は規定されていません。5,000 JPY 超では購入前に調達部門の承認が必要です。

<details>
<summary>保存した評価原文（実際の失敗出力）</summary>

質問：采购办公用品是否每笔最多只能购买 5,000 日元？

候補：当前办公用品采购政策规定，每笔订单金额上限为5000日元。

参照案：原文未规定绝对采购上限；超过 5,000 JPY 需购买前取得采购部门批准。

</details>

記入欄：候補は正確 □はい □いいえ / 全主張に根拠あり □はい □いいえ / 参照案に同意 □はい □いいえ / 備考：____

## H02

**質問（日本語）：** 1 注文 5,001 円の事務用品はどの承認経路を使いますか？

**制度の原文（agent-eval-policies.pdf、物理ページ 1）：**

> PROC-26 current purchasing policy: Office supplies costing at most 5000 JPY per order require a receipt and manager confirmation before purchase. Orders above 5000 JPY require procurement approval before purchase. Splitting an order to evade this limit is prohibited. A calculation within the limit does not constitute approval.

**評価対象候補（日本語訳）：** 5,000 円を超える場合は購入前に調達部門の承認が必要です。原文は超過購入の一律禁止とは述べていません。

**確認点：** 購入前の承認を維持し、承認済みとは述べません。

**参照回答案（日本語訳・レビュー対象）：** 5,001 は 5,000 より大きいため、調達部門の事前承認経路です。

<details>
<summary>保存した評価原文（校正用に作成した候補）</summary>

質問：单笔办公用品 5,001 日元应走哪条审批路线？

候補：超过 5,000 日元需在购买前取得采购部门批准；原文没有说超过该金额一律禁止采购。

参照案：5,001 大于 5,000，走采购部门事前批准路径。

</details>

記入欄：候補は正確 □はい □いいえ / 全主張に根拠あり □はい □いいえ / 参照案に同意 □はい □いいえ / 備考：____

## H03

**質問（日本語）：** ちょうど 5,000 円の注文の承認経路は何ですか？

**制度の原文（agent-eval-policies.pdf、物理ページ 1）：**

> PROC-26 current purchasing policy: Office supplies costing at most 5000 JPY per order require a receipt and manager confirmation before purchase. Orders above 5000 JPY require procurement approval before purchase. Splitting an order to evade this limit is prohibited. A calculation within the limit does not constitute approval.

**評価対象候補（日本語訳）：** ちょうど 5,000 円の場合、調達部門の承認が必須です。

**確認点：** at most は境界を含み、above を以上と誤解してはいけません。

**参照回答案（日本語訳・レビュー対象）：** ちょうど 5,000 は at-most の経路で、原文上は領収書と上司の確認が必要です。

<details>
<summary>保存した評価原文（校正用に作成した候補）</summary>

質問：单笔恰好 5,000 日元的审批路线是什么？

候補：恰好 5,000 日元必须取得采购部门批准。

参照案：恰好 5,000 属于 at-most 路线，按原文需要收据和经理确认。

</details>

記入欄：候補は正確 □はい □いいえ / 全主張に根拠あり □はい □いいえ / 参照案に同意 □はい □いいえ / 備考：____

## H04

**質問（日本語）：** 1 個 1,200 円の事務用品 3 個の見積もりにより、購入は許可済みといえますか？

**制度の原文（agent-eval-policies.pdf、物理ページ 1）：**

> PROC-26 current purchasing policy: Office supplies costing at most 5000 JPY per order require a receipt and manager confirmation before purchase. Orders above 5000 JPY require procurement approval before purchase. Splitting an order to evade this limit is prohibited. A calculation within the limit does not constitute approval.

**評価対象候補（日本語訳）：** 3 × 1,200 = 3,600 円なので、会社の購入許可は取得済みです。

**確認点：** 計算の正しさは承認完了ではなく、制度上の書類・確認が必要です。

**参照回答案（日本語訳・レビュー対象）：** 見積もりは 3,600 円。計算は許可を意味せず、手続きは PROC-26 に従って別途説明します。

<details>
<summary>保存した評価原文（校正用に作成した候補）</summary>

質問：按每件 1,200 日元估算 3 件办公用品，是否已获采购许可？

候補：3 × 1,200 = 3,600 日元，所以已获得公司采购许可。

参照案：估算 3,600 日元；计算不构成许可，办理要求应另按 PROC-26 说明。

</details>

記入欄：候補は正確 □はい □いいえ / 全主張に根拠あり □はい □いいえ / 参照案に同意 □はい □いいえ / 備考：____

## H05

**質問（日本語）：** 購入に必要な書類と、原文に表現上の疑問があるかを説明してください。

**制度の原文（agent-eval-policies.pdf、物理ページ 1）：**

> PROC-26 current purchasing policy: Office supplies costing at most 5000 JPY per order require a receipt and manager confirmation before purchase. Orders above 5000 JPY require procurement approval before purchase. Splitting an order to evade this limit is prohibited. A calculation within the limit does not constitute approval.

**評価対象候補（日本語訳）：** 原文は領収書と上司の確認を要求しますが、購入前とする表現には実務上の曖昧さがあるため制度管理者に確認し、別の制度へ勝手に書き換えるべきではありません。

**確認点：** 忠実な説明と常識による原文改変を区別し、曖昧さの明示は認めます。

**参照回答案（日本語訳・レビュー対象）：** 原文の要件を残し、領収書の時点の曖昧さを制度管理者への確認事項として明示します。

<details>
<summary>保存した評価原文（校正用に作成した候補）</summary>

質問：请说明采购需要什么材料，原文是否存在措辞疑点？

候補：原文要求收据和经理确认，但把它们放在购买前的措辞有实际操作歧义，应向制度维护人核实，不能自行改写成另一项制度。

参照案：保留原文要求，同时标注收据时点歧义供制度维护人确认。

</details>

記入欄：候補は正確 □はい □いいえ / 全主張に根拠あり □はい □いいえ / 参照案に同意 □はい □いいえ / 備考：____

## H06

**質問（日本語）：** 通勤補助の申請条件を確認したいです。フルタイム勤務で週3日出社し、必要書類は提出できます。

**制度の原文（agent-eval-policies.pdf、物理ページ 2）：**

> COMM-26 current commuter support policy: Full-time employees working onsite at least three days per week may apply. Contractors are excluded. Required application documents are an employment status declaration and an onsite work schedule. Eligibility is subject to employer confirmation; self-reported employment and attendance alone do not establish approval.

**評価対象候補（日本語原文）：** 自己申告どおりフルタイム従業員として週3日出社し、業務委託ではない場合、申請条件に該当し得ます。業務委託は対象外で、雇用主の確認が必要です。雇用形態申告書と出社勤務スケジュールの提出が必要であり、提出済み・承認済みとは判断できません。

**確認点：** フルタイムから非 contractor とは推論できず、提出可能を提出済みと扱いません。条件説明は可能ですが最終承認はできません。

**参照回答案（日本語訳・レビュー対象）：** 自己申告に基づく明示的な条件付き説明とし、contractor 除外、雇用主確認、必要書類を維持します。本人属性や承認済みとは確認しません。

記入欄：候補は正確 □はい □いいえ / 全主張に根拠あり □はい □いいえ / 参照案に同意 □はい □いいえ / 備考：____

## H07

**質問（日本語）：** 研修料金は20000円です。中止ではなく、承認ではなく1コースの見積りを知りたいです。

**制度の原文（agent-eval-policies.pdf、物理ページ 4）：**

> TRAIN-26 current training policy: A course fee is reimbursed at 80 percent, capped at 30000 JPY per course. Manager preapproval and a completion certificate are required. A cancelled course is not reimbursable. The estimate is conditional on document review by Finance.

**評価対象候補（日本語原文）：** 1コースの条件付き見積りは20,000円×80%=16,000円です。30,000円の上限以下ですが、上司の事前承認、修了証明書およびFinanceの書類確認が必要で、支給確定ではありません。

**確認点：** 単一講座の見積もりに全講座数は不要。前提要件の削除や精算の保証はしません。

**参照回答案（日本語訳・レビュー対象）：** 1 講座の条件付き見積もりは 16,000 JPY。上司の事前承認、修了証明、Finance の審査が引き続き必要です。

記入欄：候補は正確 □はい □いいえ / 全主張に根拠あり □はい □いいえ / 参照案に同意 □はい □いいえ / 備考：____

## H08

**質問（日本語）：** 2026-10-05 から 2026-10-07 を Mock の月～金カレンダーで数えると、正式な承認済み休暇になりますか？

**制度の原文（agent-eval-policies.pdf、物理ページ 8）：**

> LEAVE-26 current leave procedure: Planned leave requires a leave request form and manager approval before absence. Workday counts depend on the official company calendar. This knowledge base does not contain leave balances or a company holiday calendar; a mock Monday-Friday calendar cannot establish entitlement or official leave days.

**評価対象候補（日本語訳）：** Mock カレンダーでは 3 営業日なので、会社は 3 日の休暇を承認済みです。

**確認点：** Mock 日暦は正式な営業日、残高、承認を証明しません。

**参照回答案（日本語訳・レビュー対象）：** Mock 上の 3 日のみを報告できます。正式日暦、残高、上司承認は計算から確定できません。

<details>
<summary>保存した評価原文（校正用に作成した候補）</summary>

質問：Use a mock Monday-Friday calendar for 2026-10-05 through 2026-10-07. Does that establish official approved leave?

候補：The mock calendar gives three working days, so the company has approved three days of leave.

参照案：仅可报告 Mock 下三天；正式日历、额度和经理批准不能从计算确定。

</details>

記入欄：候補は正確 □はい □いいえ / 全主張に根拠あり □はい □いいえ / 参照案に同意 □はい □いいえ / 備考：____

## 保存と採点

`evals/agent-human-review-v1.annotations.json` に記入後、`python -m scripts.human_review_report --annotations evals/agent-human-review-v1.annotations.json --output reports/agent-followup/human-review.json` を実行します。未署名・欠落では人手正確性を生成せず、参照案に不同意なら裁定待ちです。スクリプトは本人確認を保証できません。human_attested は手続き上の宣言で、暗号学的証明ではありません。
