"""Deterministic provenance gate; semantic entailment still belongs to Strict Verifier.

Sources are server-owned Agent observations, never client-supplied dictionaries.
Free-form claims need an applicable document. Without one, only exact, bounded
server-rendered calculation text is permitted; no model-assigned label can bypass it.
"""

import re
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation

from .calculations import UNITS, decimal_result


def bind_unit_evidence(source, sources):
    """Bind an input unit label to actual authorized text, never to model prose.

    This checks literal numeric/unit provenance, not dimensional applicability;
    the latter still requires Strict Verifier. Unbound units cannot be rendered.
    """
    result = source.get("metadata", {}).get("result", {})
    unit = result.get("result_unit")
    if source.get("name") != "calculator" or unit not in UNITS:
        return []
    aliases = {
        "JPY": r"JPY|円|日元|日圓|yen",
        "USD": r"USD|US\$|美元",
        "EUR": r"EUR|€|欧元|ユーロ",
        "CNY": r"CNY|RMB|人民币|人民元",
        "count": r"items?|個|个|件",
        "percent": r"%|percent|パーセント",
        "days": r"days?|日|天",
        "hours": r"hours?|時間|小时",
    }[unit]
    number = r"-?\d[\d,]*(?:\.\d+)?"
    pattern = re.compile(rf"(?:({number})\s*({aliases})|({aliases})\s*({number}))", re.I)
    operands = {Decimal(value) for value in result.get("operands", [])}
    evidence = []
    for candidate in sources:
        if candidate.get("kind") not in ("document", "user"):
            continue
        for match in pattern.finditer(candidate["text"]):
            raw = match[1] or match[4]
            if Decimal(raw.replace(",", "")) in operands:
                # A bounded contiguous excerpt is long enough for quote checking.
                start, end = max(0, match.start() - 12), min(len(candidate["text"]), match.end() + 12)
                evidence.append({"source_id": candidate["number"], "quote": candidate["text"][start:end]})
                break
    return evidence[:4]


def standalone_tool_text(source, language):
    """Render only structured numeric/date outputs, never policy or user prose."""
    if source.get("kind") != "tool" or source.get("provenance") not in ("calculated", "mock", "live"):
        return None
    metadata = source.get("metadata", {})
    result, arguments = metadata.get("result", {}), metadata.get("arguments", {})
    if source.get("name") == "calculator":
        operands, value = result.get("operands", []), result.get("result")
        op = result.get("operation")
        if op not in ("sum", "subtract", "multiply", "divide", "percent_of") or not 2 <= len(operands) <= 10:
            return None
        if not all(isinstance(v, str) and re.fullmatch(r"-?\d+(?:\.\d+)?", v) for v in [*operands, value]):
            return None
        try:
            if op != "sum" and len(operands) != 2:
                return None
            computed, rounded = decimal_result(op, operands)
            if value != computed or result.get("rounded") is not rounded:
                return None
        except (InvalidOperation, ZeroDivisionError):
            return None
        symbol = {"sum": " + ", "subtract": " - ", "multiply": " × ", "divide": " ÷ ", "percent_of": "% × "}[op]
        statement = symbol.join(operands) + " = " + value
        unit = result.get("result_unit")
        if unit:
            if unit not in UNITS or not metadata.get("unit_evidence"):
                return None
            statement += f" {unit}"
        if rounded:
            statement += {
                "en": " (rounded half-up to 6 decimal places)",
                "ja": "（小数点以下6桁、四捨五入）",
                "zh": "（四舍五入至6位小数）",
            }[language]
    elif source.get("name") == "calendar":
        op = arguments.get("operation")
        if op in ("date_offset", "next_weekday"):
            try:
                calculated = date.fromisoformat(result["date"]).isoformat()
            except (ValueError, KeyError, TypeError):
                return None
            statement = {"en": "Calculated date: ", "ja": "計算上の日付：", "zh": "计算日期："}[language] + calculated
            start = result.get("start_date") or arguments.get("start_date") or result.get("reference_date")
            if start:
                statement += (
                    f" ({start}; {op}; "
                    + str(arguments.get("offset_days") if op == "date_offset" else arguments.get("week_offset"))
                    + ")"
                )
        elif op == "date_range":
            calendar_days, working_days = result.get("calendar_days"), result.get("working_days")
            if (
                type(calendar_days) is not int
                or type(working_days) is not int
                or not 0 <= working_days <= calendar_days <= 366
            ):
                return None
            label = "Mock" if source["provenance"] == "mock" else "Configured calendar"
            statement = {
                "en": f"{label}: {calendar_days} calendar days, {working_days} working days",
                "ja": f"{label}：暦日 {calendar_days} 日、勤務日 {working_days} 日",
                "zh": f"{label}：{calendar_days} 个日历日，{working_days} 个工作日",
            }[language]
            start, end = (
                result.get("start_date") or arguments.get("start_date"),
                result.get("end_date") or arguments.get("end_date"),
            )
            if start and end:
                statement += (
                    f" ({start} — {end}; " + {"en": "inclusive", "ja": "両端を含む", "zh": "含首尾"}[language] + ")"
                )
        else:
            return None
    else:
        return None
    return {
        "en": f"Calculation only, not business permission: {statement}.",
        "ja": f"制度上の許可を意味しない計算結果：{statement}。",
        "zh": f"仅为计算结果，不代表业务许可：{statement}。",
    }[language]


def render_calculation(source, sources, language):
    """Project a source reference into a fixed claim. No model text is accepted."""
    metadata = source.get("metadata", {})
    text = standalone_tool_text(source, language)
    if not text or not metadata.get("observation_id") or text not in source["text"]:
        raise ValueError("Invalid or unquotable server calculation")
    evidence = [{"source_id": source["number"], "quote": text}]
    evidence.extend(metadata.get("unit_evidence", []))
    if any(e["source_id"] not in {s["number"] for s in sources} for e in evidence):
        raise ValueError("Invalid unit provenance")
    details = {
        "observation_id": metadata["observation_id"],
        "source_id": source["number"],
        "tool": source["name"],
        "provenance": source["provenance"],
        "arguments": metadata["arguments"],
        "result": {k: v for k, v in metadata["result"].items() if k != "text"},
        "unit_evidence": metadata.get("unit_evidence", []),
    }
    return {"text": text, "evidence": evidence}, details


def applicable_document(source, as_of, historical=False):
    if source.get("kind") != "document" or source.get("provenance") != "retrieved":
        return False
    if (
        not source.get("document_id")
        or not source.get("chunk_id")
        or type(source.get("page")) is not int
        or source["page"] < 1
    ):
        return False
    metadata = source.get("metadata", {})
    if metadata.get("policy_status") not in ({"current", "archived"} if historical else {"current"}):
        return False
    try:
        start = date.fromisoformat(metadata["effective_from"]) if metadata.get("effective_from") else None
        end = date.fromisoformat(metadata["effective_to"]) if metadata.get("effective_to") else None
    except (TypeError, ValueError):
        return False
    if historical and start is None:
        return False
    return not ((start and start > as_of) or (end and end < as_of) or (start and end and start > end))


def policy_failures(claims, sources, language, *, as_of=None, historical=False):
    as_of = as_of or datetime.now(timezone(timedelta(hours=9))).date()
    source_map = {source["number"]: source for source in sources}
    failures = []
    for index, claim in enumerate(claims, 1):
        cited = [source_map[e.source_id] for e in claim.evidence if e.source_id in source_map]
        if any(applicable_document(s, as_of, historical) for s in cited):
            continue
        # Conservative by construction: not a keyword classifier or model-declared
        # "calculation" type, which could relabel a permission as arithmetic.
        if any(claim.text == standalone_tool_text(s, language) for s in cited):
            continue
        failures.append({"claim_index": index, "code": "applicable_document_required"})
    return failures
