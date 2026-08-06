"""One-shot read-only K-line analysis CLI for SDK or MCP JSON input."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from .ohlcv_validate import validate_rows
    from .resample_kline import FREQUENCIES, resample_rows
    from .indicators import moving_average, macd, rsi, bollinger
    from .pattern_detection import detect_patterns
    from .generate_kline_chart import generate_chart
except ImportError:
    from ohlcv_validate import validate_rows
    from resample_kline import FREQUENCIES, resample_rows
    from indicators import moving_average, macd, rsi, bollinger
    from pattern_detection import detect_patterns
    from generate_kline_chart import generate_chart


def load_rows(path: str) -> list[dict[str, Any]]:
    payload=json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, dict) and "result" in payload: payload=payload["result"]
    if isinstance(payload, dict) and "rows" in payload:
        cols=payload.get("columns",[]); return [dict(zip(cols,row)) for row in payload["rows"]]
    if isinstance(payload, list): return payload
    raise ValueError("input_must_be_rows_or_dataframe_json")


def analyze(rows: list[dict[str, Any]], frequency: str, min_bars: int = 20) -> dict[str, Any]:
    valid, status=validate_rows(rows, min_bars=1)
    bars=resample_rows(valid, frequency)
    closes=[float(b["close"]) for b in bars]
    result={"status":status,"frequency":frequency,"raw_rows":len(valid),"bars":len(bars),"complete_bars":sum(bool(b.get("complete")) for b in bars),"partial_bars":sum(not bool(b.get("complete")) for b in bars),"data_gate":"ok" if len(bars)>=min_bars else "error:insufficient_valid_bars","indicators":{"ma5":moving_average(closes,5),"ma10":moving_average(closes,10),"ma20":moving_average(closes,20),"macd":macd(closes),"rsi14":rsi(closes),"bollinger20":bollinger(closes)},"patterns":detect_patterns(bars)}
    return result


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("--input",required=True); parser.add_argument("--frequency",choices=sorted(FREQUENCIES),default="10m"); parser.add_argument("--out",default="/tmp/kline-analysis"); args=parser.parse_args()
    raw=load_rows(args.input); result=analyze(raw,args.frequency); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    bars = resample_rows(validate_rows(raw,min_bars=1)[0], args.frequency)
    (out/"analysis.json").write_text(json.dumps({k:v for k,v in result.items() if k!="bars"},ensure_ascii=False,indent=2,default=str),encoding="utf-8")
    (out/"bars.json").write_text(json.dumps(bars,ensure_ascii=False,indent=2,default=str),encoding="utf-8")
    chart = generate_chart(bars, out / f"kline_{args.frequency}.png", title=f"K线与成交量（{args.frequency}）")
    print(json.dumps({"status":result["data_gate"],"frequency":args.frequency,"raw_rows":result["raw_rows"],"bars":result["bars"],"chart":chart,"out":str(out)},ensure_ascii=False))

if __name__ == "__main__": main()
