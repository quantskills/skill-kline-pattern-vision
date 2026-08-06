"""Pure-Python technical indicators over validated bars."""
from __future__ import annotations

from math import sqrt


def moving_average(values: list[float], window: int) -> list[float | None]:
    return [None if i + 1 < window else sum(values[i + 1 - window:i + 1]) / window for i in range(len(values))]


def ema(values: list[float], window: int) -> list[float | None]:
    if not values or window < 1: return [None] * len(values)
    out: list[float | None] = [None] * len(values); alpha = 2 / (window + 1)
    if len(values) < window: return out
    value = sum(values[:window]) / window; out[window - 1] = value
    for i in range(window, len(values)):
        value = alpha * values[i] + (1 - alpha) * value; out[i] = value
    return out


def macd(values: list[float], fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    fast_v, slow_v = ema(values, fast), ema(values, slow)
    line = [None if a is None or b is None else a - b for a, b in zip(fast_v, slow_v)]
    usable = [x for x in line if x is not None]; sig = ema(usable, signal)
    signal_line: list[float | None] = [None] * (len(line) - len(sig)) + sig
    hist = [None if a is None or b is None else a - b for a, b in zip(line, signal_line)]
    return {"dif": line, "dea": signal_line, "histogram": hist}


def rsi(values: list[float], window: int = 14) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    if len(values) <= window: return out
    gains = [max(values[i] - values[i - 1], 0) for i in range(1, len(values))]
    losses = [max(values[i - 1] - values[i], 0) for i in range(1, len(values))]
    avg_gain, avg_loss = sum(gains[:window]) / window, sum(losses[:window]) / window
    def value(): return 100.0 if avg_loss == 0 else 100 - 100 / (1 + avg_gain / avg_loss)
    out[window] = value()
    for i in range(window, len(gains)):
        avg_gain = (avg_gain * (window - 1) + gains[i]) / window
        avg_loss = (avg_loss * (window - 1) + losses[i]) / window
        out[i + 1] = value()
    return out


def bollinger(values: list[float], window: int = 20, deviations: float = 2) -> dict:
    middle = moving_average(values, window); upper=[]; lower=[]
    for i, mean in enumerate(middle):
        if mean is None: upper.append(None); lower.append(None); continue
        sample=values[i+1-window:i+1]; sd=sqrt(sum((x-mean)**2 for x in sample)/window)
        upper.append(mean+deviations*sd); lower.append(mean-deviations*sd)
    return {"middle": middle, "upper": upper, "lower": lower}
