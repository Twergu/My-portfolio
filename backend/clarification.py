"""Shared clarification scope and verbatim answer ledger; no inferred HR facts."""

CLARIFICATION_RULES = (
    "Before asking anything, reconcile the original requested outcome with ALL user turns and their responding_to "
    "questions in clarification_context. A reply is additional information, not a replacement task. Treat it as "
    "self-report, never independently verified employment or approval. Inventory all material missing inputs and "
    "ask for them together in at most three focused questions. Reuse already supplied facts; do not ask users to "
    "repeat facts merely because their phrasing differs. If an answer was partial, ask ONLY the unresolved part. "
    "An application procedure, conditional eligibility explanation or estimate does not require evidence that "
    "later employer/manager/Finance confirmation has already happened. State that remaining condition with a "
    "document citation instead of insisting on confirmation before explaining the process. Never assert approval. "
    "For a policy expressed per course/item/night, a supplied amount supports a per-unit estimate. Do not demand "
    "the number of units unless the user asks for an aggregate total. If an aggregate is requested, do ask for an "
    "unknown count. Never silently assume a total count. Full-time work does not prove non-contractor status; "
    "for a criteria/application explanation, give the exclusion as an explicit document-backed condition, not "
    "as an established personal fact. If the user asks for a definitive personal eligibility decision and that "
    "category is unknown, ask only for that category. If user facts conflict, ask which applies instead of "
    "silently choosing one. Do not ask the user to supply missing company rules or unavailable business records. "
    "Do not transform a request for application criteria into a request for a definitive personal approval. "
    "After receiving relevant self-reported facts for a criteria explanation, explain the policy conditionally "
    "and explicitly identify unresolved exclusions rather than repeatedly demanding a complete personal adjudication. "
    "Use the server policy_scope date for current-policy questions. A document's effective-from date is a filter "
    "on policy applicability, not an extra personal question. Ask for a different target date only when the user's "
    "request actually refers to an unspecified past/future period. "
)


def clarification_context(turns):
    """Keep exact question/reply association; do not mark every asked field solved."""
    return {
        "requested_outcome": turns[0].text if turns else "",
        "statements": [
            {"turn": index, "text": turn.text, "responding_to": list(turn.responding_to), "provenance": "self_report"}
            for index, turn in enumerate(turns, 1)
        ],
        "scope": "Verbatim inputs only. A reply may answer only part of the preceding questions; no eligibility or permission is established by this ledger.",
    }
