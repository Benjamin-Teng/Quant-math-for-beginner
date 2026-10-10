"""Chart data for LM1 (src/data/lm01-*.json), computed from the verified 0050 total-return series.
Run after build_series.py:  python3 data/lm01_charts.py"""
import json
import datetime as dt
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)
BASE = dt.date(2014, 10, 31)

df = pl.read_parquet(HERE / "processed" / "etf_daily_returns.parquet").with_columns(pl.col("date").str.to_date())
R = df["R_0050"].to_numpy()
dates = [BASE] + df["date"].to_list()
W = np.concatenate([[1.0], np.cumprod(1 + R)])               # growth of 1 unit, total return
T = (dates[-1] - BASE).days / 365.25
G = W[-1]
t_years = np.array([(d - BASE).days / 365.25 for d in dates])
PATH = G ** (t_years / T)                                     # constant-rate path at the annualized return
RG = G ** (1 / T) - 1
peak = np.maximum.accumulate(W)
DD = W / peak - 1

idx = list(range(0, len(dates), 5))                           # weekly thinning keeps the page light
# keep the trough of every drawdown episode (and the last day) so the thinned curve reaches each true depth
troughs, start = [], None
for k in range(1, len(W)):
    if DD[k] < 0 and start is None:
        start = k
    if start is not None and (DD[k] >= 0 or k == len(W) - 1):
        troughs.append(start + int(np.argmin(DD[start:k + 1])))
        start = None
for k in sorted(set(troughs) | {len(dates) - 1}):
    if k not in idx:
        idx.append(k)
idx.sort()
xs = [str(dates[i]) for i in idx]
pick = lambda a, k=4: [round(float(a[i]), k) for i in idx]


def first_cross(level):
    k = int(np.argmax(W >= level))
    return str(dates[k]), float(W[k])


# annotations on a date axis need epoch milliseconds: book.js converts series dates, not annotation x values
def ts(d):
    return int(dt.datetime(*map(int, d.split("-")), tzinfo=dt.timezone.utc).timestamp() * 1000)


marks = []
# label offsets keep the text clear of both the index and the dashed constant-rate path
for lev, lab, anchor, dx, dy in ((2, "×2 · Nov 2020", "start", 8, 16), (4, "×4 · Jul 2024", "end", -8, -8), (8, "×8 · Apr 2026", "end", -6, -20)):
    d, _ = first_cross(lev)
    marks.append({"type": "point", "x": ts(d), "y": lev, "label": lab, "color": "1", "anchor": anchor, "dx": dx, "dy": dy})


def growth_chart(kind):
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


lin, log = growth_chart("lin"), growth_chart("log")

trough24, trough25 = dates.index(dt.date(2024, 8, 5)), dates.index(dt.date(2025, 4, 9))
drawdown = {
    "alt": "Drawdown of the 0050 total-return index from its running peak, Nov 2014 to Oct 2026",
    "height": 280,
    "x": {"type": "date"},
    "y": {"type": "lin", "fmt": "pct1", "tfmt": "pct0", "label": "Drawdown from running peak", "min": -0.36, "max": 0.0},
    "series": [{"name": "0050 drawdown", "color": "2", "area": True, "x": xs, "y": pick(DD)}],
    "ann": [
        {"type": "point", "x": ts("2024-08-05"), "y": round(float(DD[trough24]), 4), "label": f"{DD[trough24]:.1%}".replace("-", "−"),
         "color": "2", "anchor": "end", "dx": -9, "dy": 4},
        {"type": "point", "x": ts("2025-04-09"), "y": round(float(DD[trough25]), 4), "label": f"{DD[trough25]:.1%}".replace("-", "−"),
         "color": "2", "anchor": "end", "dx": -9, "dy": 4},
    ],
}

for name, spec in (("lm01-linear", lin), ("lm01-log", log), ("lm01-drawdown", drawdown)):
    (OUT / f"{name}.json").write_text(json.dumps(spec, ensure_ascii=True), encoding="utf-8")
    print("wrote", f"src/data/{name}.json", f"points={len(spec['series'][0]['x'])}")
print(f"min W {W.min():.4f} on {dates[int(np.argmin(W))]}, end {G:.4f}, R_G {RG:.4%}")
print("first crossings:", [first_cross(l) for l in (2, 4, 8)])
print("troughs:", dates[trough24], f"{DD[trough24]:.4%}", dates[trough25], f"{DD[trough25]:.4%}")
