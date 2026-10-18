"""Chart specs for LM14 (src/data/lm14-*.json), computed from TR23.

Run:  uv run python data/lm14_charts.py      (after data/vol3_series.py; data/lm14_numbers.py checks the text)

Inputs: data/processed/vol3_taiex.parquet only, through data/lm14_common.py (same sample and conventions as
data/lm14_numbers.py: T = 5,849 daily returns of the TAIEX total-return index, moments with divisor T, calendar years
2003-2025 with 2003 from its first close). Writes:
  lm14-case       the 23 calendar-year returns with the arithmetic mean and the compound rate (bar chart)
  lm14-bounds     days with R <= mean - k s against Cantelli's bound T/(1 + k^2), log scale (line chart)
  lm14-dragyears  each year's daily volatility drag against half its variance, with the 45-degree line (scatter)
  lm14-jensen     the widget's initial state (2008 and 2009 with equal probability) and its presets
"""
import json

import numpy as np
from lm14_common import EPS, HERE, PRESETS, law, load, two_point, year_points

OUT = HERE.parent / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)
NBSP = chr(0xA0)                 # a no-break space, which SVG text does not collapse


def r(v: float, n: int) -> float:
    return round(float(v), n)


def write(name: str, spec: dict) -> None:
    assert spec.get("alt"), name
    (OUT / f"{name}.json").write_text(json.dumps(spec, ensure_ascii=False, separators=(",", ":"), allow_nan=False),
                                      encoding="utf-8", newline="\n")
    print("wrote", f"src/data/{name}.json")


d = load()
T, R = d.T, d.R
assert T == 5849

# ------------------------------------------------------------------ case: calendar-year returns
ann = law(d.year_R, np.full(d.year_R.size, 1 / d.year_R.size))
cagr = float(np.prod(1 + d.year_R) ** (1 / d.year_R.size) - 1)
case = {
    "type": "bar", "height": 300,
    "alt": "TAIEX total-return index, calendar-year returns 2003 to 2025, from −43.07% in 2008 to +83.34% in 2009, "
    "with dashed lines at the arithmetic mean 14.97% and the compound rate 12.35%",
    "categories": [str(y) for y in d.year_ids], "x": {"label": "Calendar year (2003 from its first close)"},
    "y": {"fmt": "pct2", "tfmt": "pct0", "label": "Total return in the year", "ticks": [-0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8]},
    "series": [{"name": "TAIEX total return", "color": "1", "values": [r(v, 8) for v in d.year_R]}],
    # the two lines lie 2.6 points apart, so the upper label is pushed left (no-break spaces) to clear the lower one
    "ann": [{"type": "hline", "y": r(ann["mu"], 8), "label": "arithmetic mean 14.97%" + NBSP * 56},
            {"type": "hline", "y": r(cagr, 8), "label": "compound rate 12.35%"}],
}
write("lm14-case", case)

# ------------------------------------------------------------------ bounds: lower-tail days against Cantelli
Rbar, s = float(R.mean()), float(R.std())
z = (R - Rbar) / s
mags = np.sort(-z[z <= -1 + EPS])                 # k values at which the count drops, ascending, all >= 1
kx = [1.0]
ky = [int((z <= -1 + EPS).sum())]
for m in mags:
    kx.append(r(m, 4))
    ky.append(int((z < -m - EPS).sum()))          # just past k = m the day no longer counts
assert ky[0] == 665 and ky[-1] == 0 and r(mags[-1], 2) == 8.08
grid = [i / 100 for i in range(100, 851, 5)]
bounds = {
    "height": 320,
    "alt": "TAIEX days at or below the mean minus k standard deviations, a step line falling from 665 at k = 1 to 1 at "
    "k = 8.08, far below Cantelli's bound T/(1 + k^2): 2,924.5 days at k = 1, 344.1 at k = 4 and 90.0 at k = 8; "
    "log scale",
    "x": {"type": "num", "fmt": "n2", "tfmt": "n0", "label": "k, standard deviations below the mean", "tipLabel": "k = ",
          "min": 1, "max": 8.5, "ticks": [1, 2, 3, 4, 5, 6, 7, 8]},
    "y": {"type": "log", "fmt": "n1", "tfmt": "n0", "label": "Days", "min": 0.5, "max": 6000,
          "ticks": [1, 10, 100, 1000]},
    "series": [
        {"name": "Cantelli bound, T/(1 + k^2)", "color": "2", "dash": True, "fmt": "n1",
         "x": grid, "y": [r(T / (1 + k * k), 4) for k in grid]},
        {"name": "TAIEX days with R ≤ mean − k s", "color": "1", "step": True, "fmt": "n0", "x": kx, "y": ky},
    ],
    "ann": [{"type": "point", "x": 4, "y": 17, "color": "1", "label": "17 days at k = 4", "dx": 8, "dy": 14},
            {"type": "point", "x": 4, "y": r(T / 17, 4), "color": "2", "label": "bound 344.1", "dx": 8, "dy": -8},
            {"type": "point", "x": r(mags[-1], 4), "y": 1, "color": "1", "label": "7 Apr 2025", "anchor": "end",
             "dx": -8, "dy": 16}],
}
write("lm14-bounds", bounds)

# ------------------------------------------------------------------ dragyears: each year's drag against s^2/2
pts = year_points(d)
lab = {2008: {"dx": -16, "dy": 4, "anchor": "end"}, 2017: {"dy": 22}}   # 2008 sits near the right edge
drag_years = {
    "type": "scatter", "height": 320,
    "alt": "One point per calendar year 2003 to 2025: half the variance of the year's daily returns against its "
    "volatility drag, both in basis points; every point lies close to the 45-degree line, from 0.14 bp in 2017 to "
    "2.25 bp in 2008",
    "x": {"label": "Half the variance of the year's daily returns (bp)", "fmt": "n4", "tfmt": "n1", "min": 0,
          "max": 2.5, "name": "half variance"},
    "y": {"label": "Volatility drag, mean minus compound rate (bp)", "fmt": "n4", "tfmt": "n1", "min": 0, "max": 2.5,
          "name": "drag"},
    "series": [{"name": "Calendar year", "color": "1", "x": [r(h, 6) for _, _, h in pts],
                "y": [r(g, 6) for _, g, _ in pts]}],
    "lines": [{"from": [0, 0], "to": [1, 1], "extend": True, "color": "var(--muted)"}],
    "points": [{"at": [r(h, 6), r(g, 6)], "label": f"{y}: {g:.2f} bp", "color": "1", **lab[y]}
               for y, g, h in pts if y in lab],
}
write("lm14-dragyears", drag_years)

# ------------------------------------------------------------------ jensen: the widget's initial state
key0, label0, b0, a0, p0 = PRESETS[0]
w0 = two_point(b0, a0, p0)
xs = [r(-0.9 + 1.9 * i / 200, 6) for i in range(201)]
cx = [r(-a0 + (a0 + b0) * i / 60, 6) for i in range(61)]          # the chord, as points for the tooltip
cy = [r(np.log1p(-a0) + (np.log1p(b0) - np.log1p(-a0)) * (x + a0) / (a0 + b0), 6) for x in cx]
jensen = {
    "height": 320,
    "alt": "The curve ln(1 + x) with the chord between −43.07% and +83.34%: above the mean 20.1% the chord gives the "
    "average of the logs, 2.141%, and the curve the log of the average, 18.345%",
    "x": {"type": "num", "fmt": "pct2", "tfmt": "pct0", "label": "Return x", "tipLabel": "x = ", "min": -0.9, "max": 1.0},
    "y": {"type": "lin", "fmt": "n4", "tfmt": "n1", "label": "ln(1 + x)", "min": -2.4, "max": 0.8},
    "series": [   # the chord first, so that the crosshair snaps to the curve's finer grid
        {"name": "chord between the two outcomes", "color": "2", "dash": True, "x": cx, "y": cy},
        {"name": "ln(1 + x)", "color": "1", "x": xs, "y": [r(np.log1p(x), 6) for x in xs]},
    ],
    "ann": [{"type": "vline", "x": r(w0["mu"], 6), "dash": True},
            {"type": "point", "x": r(w0["mu"], 6), "y": r(w0["lnmu"], 6), "color": "1", "label": "log of the average",
             "anchor": "end", "dx": -8, "dy": -8},
            {"type": "point", "x": r(w0["mu"], 6), "y": r(w0["g"], 6), "color": "2", "label": "average of the logs",
             "dx": 8, "dy": 16}],
    "widget": {"presets": [{"key": k, "label": lb, "b": b, "a": a, "p": p} for k, lb, b, a, p in PRESETS]},
}
write("lm14-jensen", jensen)
