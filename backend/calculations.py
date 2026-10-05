"""Bounded arithmetic shared by tools and server rendering; no policy semantics."""

from decimal import ROUND_HALF_UP, Decimal, localcontext

UNITS = ("JPY", "USD", "EUR", "CNY", "count", "percent", "days", "hours")


def decimal_result(operation, operands):
    with localcontext() as ctx:
        ctx.prec = 40
        values = [Decimal(value) for value in operands]
        match operation:
            case "sum":
                result = sum(values)
            case "subtract":
                result = values[0] - values[1]
            case "multiply":
                result = values[0] * values[1]
            case "divide":
                result = values[0] / values[1]
            case "percent_of":
                result = values[0] * values[1] / 100
            case _:
                raise ValueError("Unsupported arithmetic operation")
        rounded = result.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
        return format(rounded, "f").rstrip("0").rstrip(".") or "0", rounded != result
