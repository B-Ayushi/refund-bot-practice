from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from typing import Any


def to_jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if is_dataclass(value):
        return {key: to_jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def money(amount: float | int | None, currency: str = "INR") -> str:
    if amount is None:
        return "Not specified"
    symbol = "₹" if currency == "INR" else currency + " "
    return f"{symbol}{amount:,.0f}"


def status_label(status: str) -> str:
    return status.replace("_", " ").title()
