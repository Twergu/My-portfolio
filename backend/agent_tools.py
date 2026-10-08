"""Server-bound retrieval and deterministic date/decimal tools; no external writes."""

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field, StringConstraints, field_validator, model_validator

from .agent import AgentModel, ReadOnlyTool, Text, ToolOutput
from .calculations import decimal_result
from .rag import retrieve


class SearchArguments(AgentModel):
    query: Text


class CalendarArguments(AgentModel):
    operation: Literal["date_offset", "next_weekday", "date_range"]
    start_date: str | None = None
    end_date: str | None = None
    offset_days: int = Field(default=0, ge=-3660, le=3660)
    weekday: int = Field(default=0, ge=0, le=6, description="Monday=0, Sunday=6")
    week_offset: int = Field(default=1, ge=0, le=52, description="1 means next calendar week")

    @field_validator("start_date", "end_date")
    @classmethod
    def iso_date(cls, value):
        if value is not None:
            parsed = date.fromisoformat(value)
            if parsed.isoformat() != value:
                raise ValueError("Use YYYY-MM-DD dates.")
        return value

    @model_validator(mode="after")
    def relevant_fields(self):
        if self.operation != "date_range" and self.end_date is not None:
            raise ValueError("end_date is only valid for date_range.")
        if self.operation == "date_range" and self.end_date is None:
            raise ValueError("date_range requires end_date.")
        if self.operation != "date_offset" and self.offset_days != 0:
            raise ValueError("offset_days is only valid for date_offset.")
        if self.operation != "next_weekday" and (self.weekday != 0 or self.week_offset != 1):
            raise ValueError("weekday/week_offset apply only to next_weekday.")
        return self


@dataclass(frozen=True)
class CalendarConfig:
    name: str = "Mock Monday-Friday calendar; statutory/company holidays are not configured"
    workweek: tuple[int, ...] = (0, 1, 2, 3, 4)
    holidays: tuple[date, ...] = ()
    provenance: Literal["mock", "live"] = "mock"

    def __post_init__(self):
        if (
            not self.name.strip()
            or not self.workweek
            or any(type(day) is not int or not 0 <= day <= 6 for day in self.workweek)
        ):
            raise ValueError("A named calendar with a valid workweek is required.")
        if any(type(day) is not date for day in self.holidays) or self.provenance not in ("mock", "live"):
            raise ValueError("Invalid calendar data provenance.")


Operand = Annotated[str, StringConstraints(pattern=r"^-?\d{1,12}(\.\d{1,6})?$")]


class CalculatorArguments(AgentModel):
    operation: Literal["sum", "subtract", "multiply", "divide", "percent_of"]
    operands: list[Operand] = Field(min_length=2, max_length=10, description="Decimal strings, not expressions")
    result_unit: Literal["JPY", "USD", "EUR", "CNY", "count", "percent", "days", "hours"] | None = Field(
        default=None,
        description="Optional result unit explicitly grounded in user/policy inputs; no automatic unit conversion",
    )

    @model_validator(mode="after")
    def arity(self):
        if self.operation != "sum" and len(self.operands) != 2:
            raise ValueError("This operation requires two operands.")
        if self.operation == "divide" and Decimal(self.operands[1]) == 0:
            raise ValueError("Division by zero.")
        return self


def calendar_result(args, context, calendar):
    start = date.fromisoformat(args.start_date) if args.start_date else context.reference_date
    common = {
        "reference_date": context.reference_date.isoformat(),
        "timezone": context.timezone,
        "operation": args.operation,
        "start_date": start.isoformat(),
        "unit": "calendar_days",
    }
    if args.operation == "date_offset":
        result = start + timedelta(days=args.offset_days)
        data = common | {
            "text": f"Date calculation: {start.isoformat()} plus {args.offset_days} calendar days = {result.isoformat()}.",
            "date": result.isoformat(),
            "offset_days": args.offset_days,
        }
        return ToolOutput(provenance="calculated", data=data)
    if args.operation == "next_weekday":
        result = start - timedelta(days=start.weekday()) + timedelta(weeks=args.week_offset, days=args.weekday)
        data = common | {
            "text": f"Relative to {start.isoformat()}, weekday {args.weekday} (Monday=0) in calendar week offset {args.week_offset} is {result.isoformat()}.",
            "date": result.isoformat(),
            "weekday": args.weekday,
            "week_offset": args.week_offset,
        }
        return ToolOutput(provenance="calculated", data=data)
    end = date.fromisoformat(args.end_date)
    span = (end - start).days + 1
    if not 1 <= span <= 366:
        raise ValueError("Date ranges must be ordered and at most 366 days inclusive.")
    working_days = [
        day.isoformat()
        for offset in range(span)
        if (day := start + timedelta(days=offset)).weekday() in calendar.workweek and day not in calendar.holidays
    ]
    return ToolOutput(
        provenance=calendar.provenance,
        data=common
        | {
            "text": f"From {start.isoformat()} to {end.isoformat()} inclusive: {span} calendar days and {len(working_days)} working days under calendar '{calendar.name}'. Calendar provenance: {calendar.provenance}. This does not establish employee availability, entitlement or approval.",
            "calendar": calendar.name,
            "end_date": end.isoformat(),
            "inclusive": True,
            "workweek": list(calendar.workweek),
            "holidays": [day.isoformat() for day in calendar.holidays],
            "calendar_days": span,
            "working_days": len(working_days),
            "working_dates": working_days,
        },
    )


def calculator_result(args):
    value, rounded = decimal_result(args.operation, args.operands)
    return ToolOutput(
        provenance="calculated",
        data={
            "operation": args.operation,
            "operands": args.operands,
            "result": value,
            "rounded": rounded,
            "result_unit": args.result_unit,
            "unit_provenance": "planner_input" if args.result_unit else "unspecified",
            "text": f"Calculation {args.operation} on operands {', '.join(args.operands)} gives {value} (at most 6 decimal places, half-up rounding). Input result-unit label: {args.result_unit or 'unspecified'}; no unit conversion performed. The operands and unit label were supplied by the planner; their applicability requires user or document evidence.",
        },
    )


def build_tools(store, settings, api_key, provider, allowed_ids, guard, *, calendar=None):
    """Only the server can set the scope. Empty IDs remain deny-all."""
    if allowed_ids is None:
        raise ValueError("Agent retrieval requires an explicit authorized document scope.")
    allowed_ids = tuple(allowed_ids)
    calendar = calendar or CalendarConfig()

    def search(args, context, metrics):
        guard()
        sources = retrieve(store, args.query, settings, api_key, list(allowed_ids), provider, metrics)
        for source in sources:
            doc = store.document(source["document_id"])
            source.update(
                kind="document",
                provenance="retrieved",
                metadata={
                    name: doc.get(name)
                    for name in ("policy_status", "effective_from", "effective_to", "department", "document_version")
                },
            )
        guard()
        return ToolOutput(provenance="retrieved", data={"sources": sources})

    def dates(args, context, metrics):
        guard()
        return calendar_result(args, context, calendar)

    def calculate(args, context, metrics):
        guard()
        return calculator_result(args)

    return [
        ReadOnlyTool(
            "knowledge_search",
            "Search authorized enterprise policies. Use query only; access and version filters are server-controlled. Empty sources mean no evidence.",
            SearchArguments,
            search,
        ),
        ReadOnlyTool(
            "calendar",
            "Calculate ISO dates or inclusive date ranges. Omitted start_date uses the server reference date. Working-day counts use the explicitly labeled calendar, which may be mock. No availability or leave balances.",
            CalendarArguments,
            dates,
        ),
        ReadOnlyTool(
            "calculator",
            "Perform decimal arithmetic. For percent_of, first operand is the percent and second is the base. Use operands from the user or policy; never invent business figures.",
            CalculatorArguments,
            calculate,
        ),
    ]
