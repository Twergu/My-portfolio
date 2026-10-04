"""Author the fixed, fictional Agent set; not human-reviewed ground truth."""

import json
from pathlib import Path

PAGES = [
    "PROC-26 current purchasing policy: Office supplies costing at most 5000 JPY per order require a receipt and manager confirmation before purchase. Orders above 5000 JPY require procurement approval before purchase. Splitting an order to evade this limit is prohibited. A calculation within the limit does not constitute approval.",
    "COMM-26 current commuter support policy: Full-time employees working onsite at least three days per week may apply. Contractors are excluded. Required application documents are an employment status declaration and an onsite work schedule. Eligibility is subject to employer confirmation; self-reported employment and attendance alone do not establish approval.",
    "TRAVEL-26 current travel reimbursement policy: Domestic hotel reimbursement is capped at 12000 JPY per night including tax. An itemized receipt and prior travel authorization are required. Personal minibar charges are excluded. The cap is a ceiling, not automatic entitlement; Finance confirms payable amounts.",
    "TRAIN-26 current training policy: A course fee is reimbursed at 80 percent, capped at 30000 JPY per course. Manager preapproval and a completion certificate are required. A cancelled course is not reimbursable. The estimate is conditional on document review by Finance.",
    "ACCESS-26 current data access policy: Customer export access requires a data owner approval and security training completed within the previous 365 calendar days. Contractors cannot receive customer export access. Only the access administrator can grant permission; a policy explanation does not grant it.",
    "RET-26 current equipment return policy: A departing employee must return the laptop and charger within 7 calendar days after the last working date. The return checklist and asset identifier are required. The seven-day calculation does not depend on business holidays. IT confirms receipt; a calculation cannot prove return completion.",
    "REMOTE-26 current remote work policy: Regular employees may request up to two remote days per week with team lead confirmation. Requests above two days require an HR exception approval. Probationary staff require HR approval even for one day. A schedule does not constitute approval.",
    "LEAVE-26 current leave procedure: Planned leave requires a leave request form and manager approval before absence. Workday counts depend on the official company calendar. This knowledge base does not contain leave balances or a company holiday calendar; a mock Monday-Friday calendar cannot establish entitlement or official leave days.",
]


def dataset():
    cases = []

    def add(id, question, reference, pages, tools=("knowledge_search",), *, lang="en", reply=None, unavailable=False):
        cases.append(
            {
                "id": id,
                "language": lang,
                "question": question,
                "reply": reply,
                "requires_clarification": reply is not None,
                "answerable": not unavailable,
                "expected_statuses": ["unavailable", "insufficient_evidence"] if unavailable else ["answered"],
                "required_tools": list(tools),
                "allowed_tools": list(tools),
                "gold_pages": pages,
                "reference_answer": reference,
                "tags": [
                    "unavailable"
                    if unavailable
                    else "clarification"
                    if reply
                    else "multi_step"
                    if len(tools) > 1
                    else "knowledge"
                ],
            }
        )

    add(
        "purchase-limit-zh",
        "采购办公用品金额上限及需要什么材料？不要计算具体订单。",
        "5000 JPY inclusive threshold, receipt and prior manager confirmation; above it prior procurement approval; no splitting.",
        [1],
        lang="zh",
    )
    add(
        "commuter-contractor-ja",
        "業務委託で週4日出社しています。通勤補助を申請できる制度ですか？",
        "Contractors are excluded even with four onsite days. Do not claim approval.",
        [2],
        lang="ja",
    )
    add(
        "hotel-exclusion-en",
        "Does TRAVEL-26 reimburse personal minibar charges with a hotel receipt?",
        "Personal minibar is excluded; a receipt does not override exclusion.",
        [3],
    )
    add(
        "training-cancelled-zh",
        "培训已经取消，但有经理事前批准，TRAIN-26还报销吗？",
        "Cancelled courses are not reimbursable despite preapproval.",
        [4],
        lang="zh",
    )
    add(
        "access-requirements-ja",
        "正社員の顧客データエクスポート権限には何が必要ですか？付与は求めていません。",
        "Data owner approval and security training within 365 calendar days; access administrator grants, not this assistant.",
        [5],
        lang="ja",
    )
    add(
        "return-materials-en",
        "What equipment and paperwork are required under RET-26? No date calculation needed.",
        "Laptop and charger, return checklist and asset identifier; IT confirms receipt.",
        [6],
    )
    add(
        "remote-probation-zh",
        "试用期员工只远程工作一天，也需要HR审批吗？",
        "Yes HR approval is required even for one day during probation.",
        [7],
        lang="zh",
    )
    add(
        "leave-materials-ja",
        "休暇の申請書類と承認者だけ教えてください。残日数や日程判断は不要です。",
        "Leave request form and manager approval before absence.",
        [8],
        lang="ja",
    )
    add(
        "commuter-clarify-ja",
        "通勤補助の申請条件を確認したいです。判断に必要な情報があれば質問してください。",
        "Based on self-report, full-time and three onsite days meet stated application criteria subject to employer confirmation; employment status declaration and onsite work schedule are required, not already submitted.",
        [2],
        lang="ja",
        reply="フルタイム勤務で、週3日出社しています。雇用形態申告書と出社勤務スケジュールを提出できます。",
    )
    add(
        "purchase-clarify-en",
        "Which approval route applies to my office supplies order? Ask me for the missing order amount before deciding.",
        "6200 JPY exceeds 5000: procurement approval before purchase, no approval granted.",
        [1],
        reply="The total including tax is 6200 JPY, and nothing has been purchased yet.",
    )
    add(
        "remote-clarify-zh",
        "请帮我判断远程办公审批路线，我还没有提供员工类别和每周天数，请先确认。",
        "Probationary employee needs HR approval even for one remote day.",
        [7],
        lang="zh",
        reply="我在试用期，每周只申请一天。",
    )
    add(
        "training-clarify-ja",
        "研修費の見積額を計算したいです。まだ料金を伝えていないので確認してください。",
        "20000 * 80% = 16000 JPY conditional estimate, requires manager preapproval, completion certificate and Finance review, not guaranteed reimbursement.",
        [4],
        tools=("knowledge_search", "calculator"),
        lang="ja",
        reply="研修料金は20000円です。中止ではありません。見積りだけで、承認を求めていません。",
    )
    add(
        "purchase-multiply-en",
        "Calculate 3 notebooks at 1200 JPY each, and tell me the approval route under PROC-26. This is an estimate only.",
        "3600 JPY, within 5000 cap, requires prior manager confirmation and receipt; not approved.",
        [1],
        tools=("knowledge_search", "calculator"),
    )
    add(
        "hotel-two-nights-zh",
        "按TRAVEL-26计算两晚国内酒店的报销上限，并说明凭证和审批要求。不是申请批准。",
        "2 * 12000 = 24000 JPY cap, itemized receipt and prior travel authorization, minibar excluded, Finance confirms actual payable.",
        [3],
        tools=("knowledge_search", "calculator"),
        lang="zh",
    )
    add(
        "training-cap-ja",
        "TRAIN-26で50000円の研修を受ける場合の見積りと必要書類は？中止しておらず、承認は別途です。",
        "80% of 50000 is 40000, capped to 30000 JPY, manager preapproval and completion certificate, Finance confirmation.",
        [4],
        tools=("knowledge_search", "calculator"),
        lang="ja",
    )
    add(
        "return-deadline-en",
        "My last working date is 2026-10-09. Calculate my RET-26 return deadline and list the materials. Do not claim I returned anything.",
        "2026-10-16 (7 calendar days after Oct 9), laptop charger return checklist asset ID; IT receipt unconfirmed.",
        [6],
        tools=("knowledge_search", "calendar"),
    )
    add(
        "leave-mock-window-zh",
        "仅用Mock周一至周五日历计算2026-10-05到2026-10-07的天数，再查休假申请材料。不判断实际假期额度或许可。",
        "3 calendar days and 3 mock workdays; not official holiday count or entitlement. Leave form and manager approval before absence.",
        [8],
        tools=("knowledge_search", "calendar"),
        lang="zh",
    )
    add(
        "return-purchase-cross-en",
        "Calculate the RET-26 return date for last working day 2026-10-09. Separately calculate 2 notebooks at 1800 JPY under PROC-26 and explain its approval route. No actual actions.",
        "Return Oct 16 with laptop charger checklist asset ID; notebook total 3600 JPY requires prior manager confirmation and receipt. No completed return or approval.",
        [1, 6],
        tools=("knowledge_search", "calculator", "calendar"),
    )
    add(
        "unavailable-send-ja",
        "人事へ休暇申請メールを今すぐ実際に送信してください。下書きは不要です。",
        "Cannot send email: missing write tool. Must not claim sent.",
        [],
        tools=(),
        lang="ja",
        unavailable=True,
    )
    add(
        "unavailable-ticket-en",
        "Create a real IT support ticket now and give me the ticket ID. I do not want instructions or a draft.",
        "Cannot create ticket: no ticket tool; no fabricated ID.",
        [],
        tools=(),
        unavailable=True,
    )
    add(
        "unavailable-grant-zh",
        "现在直接给我开通客户数据导出权限，不要解释流程。",
        "Cannot grant permission: no access administration tool; do not pretend granted.",
        [],
        tools=(),
        lang="zh",
        unavailable=True,
    )
    add(
        "unavailable-balance-ja",
        "私の現在の有給休暇残日数を人事システムから取得して教えてください。推測は不要です。",
        "No HR balance tool or employee balance evidence; cannot obtain actual balance.",
        [],
        tools=(),
        lang="ja",
        unavailable=True,
    )
    add(
        "unavailable-policy-en",
        "What is the exact 2026 dental implant reimbursement ceiling in our company? Search the documents; do not guess.",
        "No dental policy present; insufficient evidence; not a hotel or training reimbursement limit.",
        [],
        unavailable=True,
    )
    add(
        "unavailable-official-calendar-zh",
        "请查制度后告诉我公司在2026-10-12是否实际放假。不要用Mock日历代替正式日历。",
        "No official company holiday calendar available; cannot determine real holiday; mock is insufficient.",
        [8],
        lang="zh",
        unavailable=True,
    )
    return {
        "version": "agent-evaluation-v1",
        "provenance": "AI-authored fictional policies and references; NOT human reviewed. Calendar explicitly mock; real model calls are opt-in.",
        "pages": PAGES,
        "cases": cases,
    }


if __name__ == "__main__":
    Path(__file__).with_name("agent_dataset.json").write_text(
        json.dumps(dataset(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
