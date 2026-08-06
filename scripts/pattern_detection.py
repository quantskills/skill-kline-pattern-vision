"""Conservative, evidence-carrying K-line structure candidates."""
from __future__ import annotations


def _pivots(bars: list[dict], wing: int = 2) -> tuple[list[tuple[int, float]], list[tuple[int, float]]]:
    highs=[]; lows=[]
    for i in range(wing, len(bars)-wing):
        h=bars[i]["high"]; l=bars[i]["low"]
        if h >= max(b["high"] for b in bars[i-wing:i+wing+1]): highs.append((i,h))
        if l <= min(b["low"] for b in bars[i-wing:i+wing+1]): lows.append((i,l))
    return highs,lows


def detect_structure(bars: list[dict], wing: int = 2) -> dict:
    if len(bars) < max(5, wing * 2 + 1): return {"status":"insufficient_bars","pivots":{},"labels":[]}
    highs,lows=_pivots(bars,wing); labels=[]
    for seq, kind in ((highs,"high"),(lows,"low")):
        for (i0,v0),(i1,v1) in zip(seq,seq[1:]):
            if kind == "high": label="HH" if v1>v0 else "LH" if v1<v0 else "EQH"
            else: label="HL" if v1>v0 else "LL" if v1<v0 else "EQL"
            labels.append({"kind":kind,"from_index":i0,"to_index":i1,"from_value":v0,"to_value":v1,"label":label})
    last_labels=[x["label"] for x in labels[-6:]]
    trend="mixed"
    if sum(x in ("HH","HL") for x in last_labels)>=2 and not any(x=="LL" for x in last_labels[-3:]): trend="rising"
    elif sum(x in ("LH","LL") for x in last_labels)>=2 and not any(x=="HH" for x in last_labels[-3:]): trend="falling"
    return {"status":"ok","pivots":{"highs":[{"index":i,"value":v} for i,v in highs],"lows":[{"index":i,"value":v} for i,v in lows]},"labels":labels,"trend":trend}


def detect_candles(bars: list[dict]) -> list[dict]:
    out=[]
    for i,b in enumerate(bars):
        body=abs(b["close"]-b["open"]); span=b["high"]-b["low"]
        if span <= 0: continue
        upper=b["high"]-max(b["open"],b["close"]); lower=min(b["open"],b["close"])-b["low"]
        if body/span <= .1: out.append({"index":i,"candidate":"doji","evidence":"实体占全幅不超过10%"})
        if lower >= max(body*2, span*.45) and upper <= max(body*.5, .01): out.append({"index":i,"candidate":"hammer_or_long_lower_rejection","evidence":"下影显著长于实体"})
        if upper >= max(body*2, span*.45) and lower <= max(body*.5, .01): out.append({"index":i,"candidate":"shooting_star_or_long_upper_rejection","evidence":"上影显著长于实体"})
    return out


def detect_patterns(bars: list[dict]) -> dict:
    structure=detect_structure(bars)
    highs=structure.get("pivots",{}).get("highs",[]); lows=structure.get("pivots",{}).get("lows",[])
    patterns=[]
    if len(highs)>=2:
        a,b=highs[-2:]
        if abs(a["value"]-b["value"])/max(a["value"],1) <= .02:
            patterns.append({"candidate":"possible_double_top","evidence":[a,b],"confirmation":"跌破两高点间的回撤低点","invalidation":"有效突破两高点","confidence":"low"})
    if len(lows)>=2:
        a,b=lows[-2:]
        if abs(a["value"]-b["value"])/max(a["value"],1) <= .02:
            patterns.append({"candidate":"possible_double_bottom","evidence":[a,b],"confirmation":"突破两低点间的反弹高点","invalidation":"跌破两低点","confidence":"low"})
    return {"structure":structure,"candlestick_candidates":detect_candles(bars),"chart_candidates":patterns}
