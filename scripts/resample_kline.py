"""Aggregate intraday OHLCV without crossing A-share lunch breaks."""
from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime

FREQUENCIES = {"1m": 1, "5m": 5, "10m": 10, "15m": 15, "30m": 30, "60m": 60}


def _session_key(dt: datetime) -> str:
    t = dt.strftime("%H:%M")
    if "09:30" <= t <= "11:30":
        return "morning"
    if "13:00" <= t <= "15:00":
        return "afternoon"
    return "outside"


def resample_rows(rows: Iterable[dict], frequency: str) -> list[dict]:
    if frequency not in FREQUENCIES:
        raise ValueError(f"unsupported_frequency:{frequency}")
    width = FREQUENCIES[frequency]
    ordered = sorted((dict(r) for r in rows), key=lambda r: r["_dt"])
    if width == 1:
        return [{k: v for k, v in r.items() if k != "_dt"} | {"bar_count": 1, "complete": True} for r in ordered if _session_key(r["_dt"]) != "outside"]
    result: list[dict] = []
    group: list[dict] = []
    previous_session = None
    for row in ordered:
        session = _session_key(row["_dt"])
        if session == "outside":
            continue
        if group and (session != previous_session or len(group) >= width):
            result.append(_aggregate(group, width))
            group = []
        group.append(row)
        previous_session = session
    if group:
        result.append(_aggregate(group, width))
    return result


def _aggregate(group: list[dict], width: int) -> dict:
    first, last = group[0], group[-1]
    result = {
        "datetime": last["_dt"].isoformat(),
        "start_datetime": first["_dt"].isoformat(),
        "end_datetime": last["_dt"].isoformat(),
        "symbol": first.get("symbol"),
        "open": first["open"], "high": max(r["high"] for r in group),
        "low": min(r["low"] for r in group), "close": last["close"],
        "bar_count": len(group), "complete": len(group) == width,
    }
    for field in ("volume", "amount", "num_trades"):
        if any(field in r for r in group):
            result[field] = sum(float(r.get(field, 0) or 0) for r in group)
    return result
