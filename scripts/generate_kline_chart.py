"""Generate a readable candlestick + volume PNG from normalized bars."""
from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch


def generate_chart(bars: list[dict], output: str | Path, title: str = "K线与成交量") -> str:
    if not bars: raise ValueError("no_bars")
    output=Path(output); output.parent.mkdir(parents=True, exist_ok=True)
    up, down, surface, page, grid = "#eb6834", "#2a78d6", "#fcfcfb", "#f9f9f7", "#e1e0d9"
    plt.rcParams.update({"font.sans-serif":["Arial Unicode MS","PingFang SC","DejaVu Sans"],"axes.unicode_minus":False})
    fig,(ax,vol)=plt.subplots(2,1,figsize=(14,8),sharex=True,gridspec_kw={"height_ratios":[3,1]},facecolor=page)
    ax.set_facecolor(surface); vol.set_facecolor(surface); width=.68
    for i,b in enumerate(bars):
        color=up if b["close"] >= b["open"] else down; alpha=1 if b.get("complete",True) else .45
        ax.vlines(i,b["low"],b["high"],color=color,alpha=alpha,lw=1.3)
        body=abs(b["close"]-b["open"]); y=min(b["open"],b["close"])
        if body < .01: ax.hlines(b["close"],i-width/2,i+width/2,color=color,alpha=alpha,lw=2)
        else: ax.add_patch(Rectangle((i-width/2,y),width,body,facecolor=color,edgecolor=color,alpha=alpha))
        vol.bar(i,float(b.get("volume",0))/1e6,width=width,color=color,alpha=alpha)
    ax.grid(axis="y",color=grid); vol.grid(axis="y",color=grid); ax.set_title(title,loc="left")
    ax.set_ylabel("价格"); vol.set_ylabel("成交量（百万）"); ax.tick_params(labelbottom=False)
    ax.legend(handles=[Patch(facecolor=up,label="上涨"),Patch(facecolor=down,label="下跌")],frameon=False,loc="upper left")
    ticks=list(range(0,len(bars),max(1,len(bars)//8))); vol.set_xticks(ticks,[str(bars[i].get("end_datetime",i))[-8:-3] for i in ticks])
    for axis in (ax,vol): axis.spines[["top","right","left","bottom"]].set_visible(False)
    fig.tight_layout(); fig.savefig(output,dpi=160,bbox_inches="tight",facecolor=page); plt.close(fig)
    return str(output)
