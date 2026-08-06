"""Normalize and validate OHLCV rows without filling or repairing market data."""
from __future__ import annotations

from datetime import datetime
import math
from typing import Any, Iterable

REQUIRED = ("open", "high", "low", "close")


def _date_value(row: dict[str, Any]) -> str:
    value = row.get("datetime") or row.get("date")
    if value is None:
        raise ValueError("missing_date")
    return str(value)


def validate_rows(rows: Iterable[dict[str, Any]], *, min_bars: int = 1) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for raw in rows:
        row = dict(raw)
        stamp = _date_value(row)
        try:
            dt = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"unparseable_date:{stamp}") from exc
        key = (str(row.get("symbol", "")), dt.isoformat())
        if key in seen:
            raise ValueError(f"duplicate_key:{key[0]}:{key[1]}")
        seen.add(key)
        values: dict[str, float] = {}
        for field in REQUIRED:
            try:
                values[field] = float(row[field])
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"missing_or_invalid_{field}") from exc
            if not math.isfinite(values[field]):
                raise ValueError(f"non_finite_{field}")
        if values["high"] < max(values["open"], values["low"], values["close"]):
            raise ValueError("invalid_ohlc_high")
        if values["low"] > min(values["open"], values["high"], values["close"]):
            raise ValueError("invalid_ohlc_low")
        for field in ("volume", "amount", "num_trades"):
            if field in row and row[field] is not None:
                try:
                    values[field] = float(row[field])
                except (TypeError, ValueError) as exc:
                    raise ValueError(f"invalid_{field}") from exc
                if not math.isfinite(values[field]) or values[field] < 0:
                    raise ValueError(f"invalid_{field}")
        normalized.append({**row, **values, "_dt": dt})
    normalized.sort(key=lambda r: (str(r.get("symbol", "")), r["_dt"]))
    status = "ok" if len(normalized) >= min_bars else "error"
    return normalized, {"status": status, "returned_rows": len(normalized), "valid_rows": len(normalized), "reason": None if status == "ok" else "insufficient_valid_bars"}
