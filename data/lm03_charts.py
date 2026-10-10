"""Chart data for LM3 (src/data/lm03-*.json), computed from the verified return series.
Run after build_series.py:  python3 data/lm03_charts.py"""
import json
from pathlib import Path
import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "src" / "data"
df = pl.read_parquet(HERE / "processed" / "etf_daily_returns.parquet")
R = df["R_0050"].to_numpy(); RL = df["R_00631L"].to_numpy(); d = df["date"].to_list()
dates = ["2014-10-31"] + d                                   # base date: last close before the first return
W0 = np.concatenate([[1.0], np.cumprod(1 + R)])               # 0050 total return
WL = np.concatenate([[1.0], np.cumprod(1 + RL)])              # 00631L
W2 = np.concatenate([[1.0], np.cumprod(1 + 2 * R)])           # exact daily 2x of 0050
WT = np.concatenate([[1.0], (np.cumprod(1 + R) ** 2) * np.exp(-np.cumsum(R ** 2))])   # Taylor (3.11)
gap_act = np.concatenate([[0.0], np.cumsum(np.log1p(RL) - 2 * np.log1p(R))])
gap_ex = np.concatenate([[0.0], np.cumsum(np.log1p(2 * R) - 2 * np.log1p(R))])
gap_t2 = np.concatenate([[0.0], -np.cumsum(R ** 2)])
idx = list(range(0, len(dates), 5))                          # weekly thinning keeps the page light
if idx[-1] != len(dates) - 1: idx.append(len(dates) - 1)
pick = lambda a, k=4: [round(float(a[i]), k) for i in idx]
xs = [dates[i] for i in idx]

wealth = {"alt": "Growth of 1 unit, log scale, Nov 2014 to Oct 2026", "height": 340, "endLabels": True, "endValue": True,
  "x": {"type": "date"}, "y": {"type": "log", "fmt": "x1", "label": "Growth of 1 unit (log scale)"},
  "series": [
    {"name": "00631L (market price)", "endLabel": "00631L", "color": "2", "x": xs, "y": pick(WL, 3)},
    {"name": "Exact daily 2× of 0050", "endLabel": "Daily 2×", "color": "1", "x": xs, "y": pick(W2, 3)},
    {"name": "Taylor: G² · e^(−ΣR²)", "endLabel": "Taylor", "color": "4", "dash": True, "x": xs, "y": pick(WT, 3)},
    {"name": "0050 total return", "endLabel": "0050", "color": "3", "x": xs, "y": pick(W0, 3)}],
  "endMargin": 150}
gap = {"alt": "Cumulative log-point gap versus twice 0050, Nov 2014 to Oct 2026", "height": 320, "endLabels": True,
  "x": {"type": "date"}, "y": {"type": "lin", "fmt": "n2", "label": "Cumulative gap vs 2 × log growth of 0050 (log points)"},
  "series": [
    {"name": "00631L actual gap", "endLabel": "00631L", "color": "2", "x": xs, "y": pick(gap_act)},
    {"name": "Exact daily-rebalancing effect", "endLabel": "Exact", "color": "1", "x": xs, "y": pick(gap_ex)},
    {"name": "Taylor: −ΣR²", "endLabel": "−ΣR²", "color": "4", "dash": True, "x": xs, "y": pick(gap_t2)}],
  "ann": [{"type": "hline", "y": 0}], "endMargin": 120}

def price(y, c=0.02, n=10, F=100.0):
    return sum(c * F / (1 + y) ** t for t in range(1, n + 1)) + F / (1 + y) ** n
y0, P0, Dm, C = 0.02, price(0.02), 8.98258, 93.9955          # Dm, C from central differences (lab Part 7)
ys = [round(0.0 + k * 0.0025, 4) for k in range(0, 25)]
bond = {"alt": "Bond price versus yield with first- and second-order approximations", "height": 300, "endLabels": True,
  "x": {"type": "num", "fmt": "pct1", "label": "Yield to maturity", "tipLabel": "yield "},
  "y": {"type": "lin", "fmt": "n1", "label": "Price per 100 face (10-year, 2% annual coupon)"},
  "series": [
    {"name": "Exact price", "endLabel": "Exact", "color": "1", "x": ys, "y": [round(price(y), 3) for y in ys]},
    {"name": "Duration only (1st order)", "endLabel": "1st order", "color": "2", "x": ys, "y": [round(P0 * (1 - Dm * (y - y0)), 3) for y in ys]},
    {"name": "Duration + convexity (2nd order)", "endLabel": "2nd order", "color": "3", "dash": True, "x": ys,
     "y": [round(P0 * (1 - Dm * (y - y0) + 0.5 * C * (y - y0) ** 2), 3) for y in ys]}],
  "ann": [{"type": "point", "x": 0.02, "y": 100.0, "label": "expansion point y₀ = 2%", "color": "1", "dx": 8, "dy": -10}],
  "endMargin": 80}

for name, spec in (("lm03-wealth", wealth), ("lm03-gap", gap), ("lm03-bond", bond)):
    (OUT / f"{name}.json").write_text(json.dumps(spec, ensure_ascii=True), encoding="utf-8")
    print("wrote", f"src/data/{name}.json")
