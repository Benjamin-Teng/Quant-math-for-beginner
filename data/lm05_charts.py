"""Chart data for LM5 (src/data/lm05-*.json), computed from the verified 0050 return series.

Run from the repository root, after data/build_series.py:

    uv run python data/lm05_charts.py

lm05-riemann.json  Section 2: a rising deposit rate and its left/right Riemann sums with four panels
lm05-tail.json     Section 7: days with R <= x, normal model vs Student-t (illustrative) vs 0050 data (log scale).
                   Its extra key "widget" carries the data of the tail-probability explorer in src/lm05.js:
                   the sample moments, a histogram of all daily returns and the sorted returns below -0.9%.
"""
import json
import math
from pathlib import Path

import numpy as np
import polars as pl
from scipy import special, stats

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "src" / "data"
df = pl.read_parquet(HERE / "processed" / "etf_daily_returns.parquet")
R = df["R_0050"].to_numpy()
dates = df["date"].to_list()
n = len(R)
mu, s = R.mean(), R.std()                                   # population sd, as in the text
years = (np.datetime64(dates[-1]) - np.datetime64("2014-10-31")).astype(int) / 365.25
Phi = lambda z: 0.5 * special.erfc(-z / math.sqrt(2.0))

# ------------------------------------------------------------------ Section 2: Riemann sums of r(t) = 2% - 0.5% e^{-2t}
rt = lambda t: 0.02 - 0.005 * math.exp(-2 * t)
ts = [round(k / 100, 2) for k in range(101)]
left_x, left_y, right_x, right_y = [], [], [], []
for k in range(4):
    a, b = k / 4, (k + 1) / 4
    left_x += [a, b]; left_y += [round(rt(a), 6)] * 2
    right_x += [a, b]; right_y += [round(rt(b), 6)] * 2
L4 = sum(rt(k / 4) for k in range(4)) / 4
R4 = sum(rt((k + 1) / 4) for k in range(4)) / 4
riemann = {
    "alt": "A rising deposit rate r(t) over one year with left and right Riemann sums of four panels", "height": 280,
    "x": {"type": "num", "fmt": "n2", "label": "Time t (years)", "tipLabel": "t = ", "min": 0, "max": 1},
    "y": {"type": "lin", "fmt": "pct3", "tfmt": "pct1", "label": "Continuously compounded rate r(t), % a year", "min": 0, "max": 0.022},
    "series": [
        {"name": "Rate path r(t) = 2.0% − 0.5% e^(−2t)", "color": "1", "x": ts, "y": [round(rt(t), 6) for t in ts]},
        {"name": f"Left sum, 4 panels (area {L4:.4%})", "color": "2", "area": True, "x": left_x, "y": left_y},
        {"name": f"Right sum, 4 panels (area {R4:.4%})", "color": "3", "dash": True, "x": right_x, "y": right_y}],
}

# ------------------------------------------------------------------ Section 7: tail counts, normal vs t(3) vs data
nu = 3
sc = s * math.sqrt((nu - 2) / nu)
xs = [round(-0.105 + k * 0.0005, 4) for k in range(round((0.105 - 0.010) / 0.0005) + 1)]
floor = 1e-3
norm_y = []
for x in xs:
    v = n * Phi((x - mu) / s)
    norm_y.append(round(v, 6) if v >= floor else None)
# add the exact floor crossing so the normal curve ends on the axis instead of in mid-air
z_floor = stats.norm.ppf(floor / n)
x_floor = round(mu + s * z_floor, 5)
t_y = [round(float(n * stats.t.cdf((x - mu) / sc, nu)), 5) for x in xs]
srt = np.sort(R)
emp_x, emp_y = [], []
# Returns keep 10 decimals: enough to separate every pair of distinct returns (the closest differ by 2e-7), while
# exact ties, such as the two -1.000% days that float division puts on either side of -0.01, become equal again.
for k, v in enumerate(srt[srt <= -0.010 + 1e-12], start=1):  # step function of #(R <= x)
    emp_x += [round(float(v), 10), round(float(v), 10)]
    emp_y += [k - 1 if k > 1 else None, k]
emp_x.append(-0.010); emp_y.append(int((R <= -0.010 + 1e-12).sum()))
nx = sorted(set(xs + [x_floor]))
ny = []
for x in nx:
    if x == x_floor:
        ny.append(floor)
    else:
        ny.append(norm_y[xs.index(x)])

# histogram for the widget: bins of 0.5 pp centred on multiples of 0.5%, so the +-10% limit days sit in bin centres
edges = np.round(np.arange(-0.1075, 0.1076, 0.005), 4)
counts, _ = np.histogram(R, bins=edges)
# the widget counts R <= kappa + 1e-12 from this list: at 6 decimals 2021-05-17's -1.8999612% became -1.9%
lower = [round(float(v), 10) for v in srt[srt <= -0.009 + 1e-12]]

tail = {
    "alt": "Number of days with a return at or below x: normal model, Student-t with 3 degrees of freedom, and 0050 data, log scale",
    "height": 330,
    "x": {"type": "num", "fmt": "pct1", "tfmt": "pct0", "label": "Threshold x (daily total return)", "tipLabel": "x = ", "min": -0.105, "max": -0.010},
    "y": {"type": "log", "fmt": "num", "label": "Days with R ≤ x out of 2,902 (log scale)", "min": 0.001, "max": 1000,
          "ticks": [0.001, 0.01, 0.1, 1, 10, 100, 1000]},
    "series": [
        {"name": "0050 data (actual count)", "color": "2", "x": emp_x, "y": emp_y},
        {"name": "Normal model (expected)", "color": "1", "x": nx, "y": ny},
        {"name": "Student-t, ν = 3, same σ (illustrative)", "color": "3", "dash": True, "x": xs, "y": t_y}],
    "ann": [{"type": "vline", "x": -0.05, "label": "x = −5%", "anchor": "start"},
            {"type": "hline", "y": 1, "label": "1 day"}],
    "widget": {
        "n": n, "mu": round(float(mu), 9), "s": round(float(s), 9), "years": round(float(years), 4),
        "first": dates[0], "last": dates[-1],
        "bin": 0.005, "edges0": float(edges[0]), "counts": [int(c) for c in counts],
        "lower": lower,
    },
}
assert int(np.sum(counts)) == n, "histogram must contain every return"

for name, spec in (("lm05-riemann", riemann), ("lm05-tail", tail)):
    (OUT / f"{name}.json").write_text(json.dumps(spec, ensure_ascii=True, separators=(",", ":")), encoding="utf-8")
    print("wrote", f"src/data/{name}.json", f"({(OUT / f'{name}.json').stat().st_size:,} bytes)")
print(f"normal curve floor crossing at x = {x_floor:.4%}; lower-tail list {len(lower)} values; bins {len(counts)}")
