"""Chart data for LM1 (src/data/lm01-*.json), computed from the verified 0050 total-return series.
Run after build_series.py:  uv run python data/lm01_charts.py"""
import datetime as dt
import json
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)
BASE = dt.date(2014, 10, 31)
YEAR = 365.25                                                 # a span in years is calendar days / 365.25

df = pl.read_parquet(HERE / "processed" / "etf_daily_returns.parquet").with_columns(pl.col("date").str.to_date())
R = df["R_0050"].to_numpy()
dates = [BASE] + df["date"].to_list()
W = np.concatenate([[1.0], np.cumprod(1 + R)])               # growth of 1 unit, total return
tau = (dates[-1] - BASE).days / YEAR
G = W[-1]
t_years = np.array([(d - BASE).days / YEAR for d in dates])
PATH = G ** (t_years / tau)                                   # constant-rate path at the annualized return
RG = G ** (1 / tau) - 1
PEAK = np.maximum.accumulate(W)                               # running peak, including W_0 = 1
DD = 1 - W / PEAK                                             # drawdown, a positive number


def first_cross(level):
    return int(np.argmax(W >= level))


# every drawdown episode: start (peak), trough and recovery index
episodes, start = [], None
for k in range(1, len(W)):
    if DD[k] > 0 and start is None:
        start = k - 1
    if start is not None and (DD[k] <= 0 or k == len(W) - 1):
        trough = start + int(np.argmax(DD[start:k + 1]))
        episodes.append((start, trough, k if DD[k] <= 0 else None))
        start = None

# weekly thinning keeps the page light, but every value the text cites stays in the series (AUTHORING 7):
# all peaks, troughs and recovery days of drawdown episodes, the doubling crossings and the last day
keep = {len(dates) - 1} | {first_cross(v) for v in (2, 4, 8)}
for s, t, r in episodes:
    keep |= {s, t} | ({r} if r is not None else set())
idx = sorted(set(range(0, len(dates), 5)) | keep)
xs = [str(dates[i]) for i in idx]
pick = lambda a, k=4: [round(float(a[i]), k) for i in idx]

marks = []
# label offsets keep the text clear of both the index and the dashed constant-rate path
for lev, lab, anchor, dx, dy in ((2, "×2 · Nov 2020", "start", 8, 16), (4, "×4 · Jul 2024", "end", -8, -8), (8, "×8 · Apr 2026", "end", -6, -20)):
    marks.append({"type": "point", "x": str(dates[first_cross(lev)]), "y": lev, "label": lab, "color": "1", "anchor": anchor, "dx": dx, "dy": dy})


def growth_chart(kind: str) -> dict[str, Any]:
    return {
        "alt": f"0050 total-return index on a {'logarithmic' if kind == 'log' else 'linear'} axis, Nov 2014 to Oct 2026, with the constant-rate path",
        "height": 300,
        "x": {"type": "date"},
        "y": {"type": kind, "fmt": "x2", "tfmt": "x0", "label": "Growth of 1 unit" + (" (log scale)" if kind == "log" else " (linear scale)"),
              "ticks": [1, 2, 4, 8], **({"min": 0.0, "max": 11.5} if kind == "lin" else {"min": 0.8, "max": 11.5})},
        "series": [
            {"name": "0050 total return", "color": "1", "x": xs, "y": pick(W)},
            {"name": f"Constant {RG:.1%} a year", "color": "var(--muted)", "dash": True, "x": xs, "y": pick(PATH)}],
        "ann": marks,
    }


t24, t25 = dates.index(dt.date(2024, 8, 5)), dates.index(dt.date(2025, 4, 9))
drawdown: dict[str, Any] = {
    "alt": "Drawdown of the 0050 total-return index from its running peak, plotted as W over the peak minus one, Nov 2014 to Oct 2026",
    "height": 280,
    "x": {"type": "date"},
    "y": {"type": "lin", "fmt": "pct1", "tfmt": "pct0", "label": "W ÷ running peak − 1, which equals −DD", "min": -0.36, "max": 0.0},
    "series": [{"name": "0050: W ÷ running peak − 1", "color": "2", "area": True, "x": xs, "y": pick(-DD)}],
    "ann": [
        {"type": "point", "x": "2024-08-05", "y": round(float(-DD[t24]), 4), "label": f"{-DD[t24]:.1%}".replace("-", "−"),
         "color": "2", "anchor": "end", "dx": -9, "dy": 4},
        {"type": "point", "x": "2025-04-09", "y": round(float(-DD[t25]), 4), "label": f"{-DD[t25]:.1%}".replace("-", "−"),
         "color": "2", "anchor": "end", "dx": -9, "dy": 4},
    ],
}

for name, spec in (("lm01-linear", growth_chart("lin")), ("lm01-log", growth_chart("log")), ("lm01-drawdown", drawdown)):
    (OUT / f"{name}.json").write_text(json.dumps(spec, ensure_ascii=True), encoding="utf-8")
    print("wrote", f"src/data/{name}.json", f"points={len(spec['series'][0]['x'])}")
print(f"min W {W.min():.4f} on {dates[int(np.argmin(W))]}, end {G:.4f}, R_G {RG:.4%}")
print("first crossings:", [(str(dates[first_cross(v)]), round(float(W[first_cross(v)]), 3)) for v in (2, 4, 8)])
print("troughs:", dates[t24], f"DD {DD[t24]:.4%}", dates[t25], f"DD {DD[t25]:.4%}", "| deepest", f"{DD.max():.4%}", dates[int(np.argmax(DD))])
cited = ["2015-04-27", "2015-08-24", "2025-01-07", "2025-04-09", "2024-07-11", "2024-08-05", "2020-11-11", "2024-07-04", "2026-04-27", "2022-10-25"]
print("cited dates present in thinned series:", all(c in xs for c in cited))
