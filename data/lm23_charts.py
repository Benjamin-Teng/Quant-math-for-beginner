"""Chart specs for LM23 (src/data/lm23-*.json), computed by data/lm23_common.py.

Run:  uv run python data/lm23_charts.py      (after data/vol2_series.py, data/vol3_series.py, data/build_series.py and
                                              data/vol4_series.py; data/lm23_numbers.py checks the text)

Writes lm23-fin2025 (scatter: FinancialInsurance on the TAIEX in 2025, 243 points stored in the order of the TAIEX
return, without dates, with the fitted line, the fit without 7 April 2025 and the 95% confidence and prediction bands),
lm23-betas (forest plot of the 28 betas: full sample with classical and Newey-West intervals, and the halves),
lm23-haclag (line chart, log x: the Newey-West standard error of Semiconductor's beta against the lag),
lm23-alphas (bar chart: the 28 intercept t-stats, classical and Newey-West),
lm23-rolling (line chart: rolling 250-return betas of FinancialInsurance and Semiconductor with classical 95% bands,
weekly windows plus the cited extremes), and lm23-regWindows (the widget's initial forest plot and, in its "widget"
block, per-window statistics of the 28 market models; no series in date order).
No published file carries a daily series in date order (plans/vol-4.md, "No full daily series in published files").
"""
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lm23_common as c

OUT = HERE.parent / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)


def rd(v: float, n: int) -> float:
    return round(float(v), n)


def write(name: str, spec: dict[str, Any]) -> None:
    assert isinstance(spec.get("alt"), str) and spec["alt"].strip()
    blob = json.dumps(spec, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    assert len(blob.encode("utf-8")) < 300_000, (name, len(blob))
    (OUT / f"{name}.json").write_text(blob, encoding="utf-8", newline="\n")
    print(f"wrote src/data/{name}.json ({len(blob.encode('utf-8')):,} bytes)")


# ---------------------------------------------------------------- fin2025: the 2025 scatter with bands
order = np.argsort(c.X25, kind="stable")
xs, ys = 100 * c.X25[order], 100 * c.Y25[order]
assert c.J7 == int(order[0])                       # 7 April 2025 is the year's smallest TAIEX return
xmin, xmax = float(xs[0]), float(xs[-1])
grid = sorted(set(np.round(np.linspace(xmin, xmax, 59), 6).tolist()) | {-5.0})
assert len(grid) == 60
band_x, conf_lo, conf_hi, pred_lo, pred_hi = [], [], [], [], []
for xv in grid:
    z0 = np.array([1.0, xv / 100])
    h0 = float(z0 @ c.F25.zi @ z0)
    yh = float(z0 @ c.F25.b)
    sf, sp = np.sqrt(c.F25.s2 * h0), np.sqrt(c.F25.s2 * (1 + h0))
    band_x.append(rd(xv, 4))
    conf_lo.append(rd(100 * (yh - 1.96 * sf), 4))
    conf_hi.append(rd(100 * (yh + 1.96 * sf), 4))
    pred_lo.append(rd(100 * (yh - 1.96 * sp), 4))
    pred_hi.append(rd(100 * (yh + 1.96 * sp), 4))
i5 = band_x.index(-5.0)
assert (f"{conf_lo[i5]:.2f}", f"{conf_hi[i5]:.2f}", f"{pred_lo[i5]:.2f}", f"{pred_hi[i5]:.2f}") == \
    ("-3.01", "-2.28", "-4.33", "-0.96")


def fit_y(b: np.ndarray, xv: float) -> float:
    return rd(100 * (b[0] + b[1] * xv / 100), 4)


write("lm23-fin2025", {
    "type": "scatter", "equal": False, "height": 380,
    "alt": "FinancialInsurance against TAIEX daily price returns in 2025, 243 days, with the fitted line of slope "
           "0.529, the fit without 7 April 2025 of slope 0.432, and the 95% confidence and prediction bands; at a "
           "TAIEX return of minus 5% the fitted value is minus 2.64%, the confidence band runs from minus 3.01% to "
           "minus 2.28% and the prediction band from minus 4.33% to minus 0.96%",
    "x": {"label": "TAIEX daily return, 2025 (%)", "fmt": "n2", "tfmt": "n0", "name": "TAIEX", "min": -10.5,
          "max": 10, "ticks": [-10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10]},
    "y": {"label": "FinancialInsurance daily return (%)", "fmt": "n2", "tfmt": "n0", "name": "FinancialInsurance",
          "min": -10.5, "max": 9, "ticks": [-10, -8, -6, -4, -2, 0, 2, 4, 6, 8]},
    "series": [{"name": "2025 days", "color": "1", "r": 2.6,
                "x": [rd(v, 4) for v in xs], "y": [rd(v, 4) for v in ys]}],
    "bands": [
        {"name": "95% prediction band", "x": band_x, "lo": pred_lo, "hi": pred_hi, "color": "3", "opacity": 0.14},
        {"name": "95% confidence band", "x": band_x, "lo": conf_lo, "hi": conf_hi, "color": "2", "opacity": 0.35},
    ],
    "lines": [
        {"from": [xmin, fit_y(c.F25.b, xmin)], "to": [xmax, fit_y(c.F25.b, xmax)], "color": "2", "width": 2,
         "label": "fit, beta 0.529"},
    ],
    "segments": [
        {"from": [xmin, fit_y(c.F25B.b, xmin)], "to": [xmax, fit_y(c.F25B.b, xmax)], "color": "4", "width": 1.6,
         "label": "dashed: without 7 Apr, beta 0.432", "dy": 155},
    ],
    "points": [
        {"at": [rd(xs[0], 4), rd(ys[0], 4)], "label": "7 Apr 2025", "color": "4", "r": 4.5},
        {"at": [-5.0, fit_y(c.F25.b, -5.0)], "label": "fit at −5%", "color": "2", "r": 3.5, "dx": -64, "dy": -10},
    ],
})

# ---------------------------------------------------------------- betas: forest plot of the 28 betas
SORTED = sorted(c.NAMES, key=lambda k: c.BETAS[k])              # row 1 = smallest beta (bottom)
ROW = {nm: i + 1 for i, nm in enumerate(SORTED)}
half = {h[0]: (h[1], h[2]) for h in c.HALVES}
lines_hac, lines_cls = [], []
for nm in SORTED:
    f = c.FITS[nm]
    b, y = float(f.b[1]), ROW[nm]
    lines_hac.append({"from": [rd(b - 1.96 * f.se_n[1], 6), y], "to": [rd(b + 1.96 * f.se_n[1], 6), y],
                      "color": "var(--ink-2)", "width": 1.5})
    lines_cls.append({"from": [rd(b - 1.96 * f.se_c[1], 6), y], "to": [rd(b + 1.96 * f.se_c[1], 6), y],
                      "color": "1", "width": 5})
write("lm23-betas", {
    "type": "scatter", "equal": False, "height": 620,
    "alt": "Forest plot of the 28 U28 sector betas on the TAIEX, sorted from CommunicationsInternet 0.507 to "
           "Semiconductor 1.207, with classical and Newey-West 95% intervals of the full-sample beta and the betas of "
           "the two halves; FinancialInsurance falls from 1.156 to 0.578 and Semiconductor rises from 1.089 to 1.294",
    "x": {"label": "Beta on the TAIEX (daily price returns)", "fmt": "n3", "tfmt": "n1", "name": "beta",
          "min": 0.2, "max": 1.5, "ticks": [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4]},
    "y": {"fmt": "n0", "name": "sector", "min": 0.4, "max": 28.6, "ticks": list(range(1, 29)),
          "tickLabels": SORTED},
    "series": [
        {"name": "full sample", "color": "1", "r": 4, "x": [rd(c.BETAS[nm], 6) for nm in SORTED],
         "y": [ROW[nm] for nm in SORTED]},
        {"name": "first half", "color": "2", "r": 3.4, "x": [rd(half[nm][0], 6) for nm in SORTED],
         "y": [ROW[nm] for nm in SORTED]},
        {"name": "second half", "color": "3", "r": 3.4, "x": [rd(half[nm][1], 6) for nm in SORTED],
         "y": [ROW[nm] for nm in SORTED]},
    ],
    "lines": lines_hac + lines_cls,
})

# ---------------------------------------------------------------- haclag: Newey-West SE against the lag (log x)
_iy = int(np.argmax(c.CURVE_YEAR))               # the yearly-fit series rises to its maximum, then falls
assert all(b >= a for a, b in zip(c.CURVE_POOL, c.CURVE_POOL[1:]))
assert all(b >= a for a, b in zip(c.CURVE_YEAR[:_iy], c.CURVE_YEAR[1:_iy + 1]))
assert all(b <= a for a, b in zip(c.CURVE_YEAR[_iy:], c.CURVE_YEAR[_iy + 1:]))
assert (c.LAG_GRID[0], c.LAG_GRID[_iy], c.LAG_GRID[-1]) == (1, 39, 400)
assert (f"{c.CURVE_POOL[0]:.4f}", f"{c.CURVE_YEAR[0]:.4f}", f"{c.CURVE_YEAR[_iy]:.4f}", f"{c.CURVE_YEAR[-1]:.4f}") == \
    ("0.0138", "0.0127", "0.0161", "0.0083")
assert (f"{c.SEMI.se_w[1]:.4f}", f"{c.CURVE_AT[9][0]:.4f}", f"{c.CURVE_AT[50][0]:.4f}", f"{c.CURVE_AT[200][0]:.4f}") == \
    ("0.0129", "0.0185", "0.0275", "0.0390")
write("lm23-haclag", {
    "type": "line", "height": 320,
    "alt": "Newey-West standard error of Semiconductor's daily beta against the lag from 1 to 400 on a log axis: with "
           "the full-sample residuals it rises from 0.0138 at lag 1 (White's 0.0129 is dashed) through 0.0185 at 9, "
           "0.0275 at 50 and 0.0390 at 200; with the residuals of yearly fits it rises from 0.0127 to 0.0161 at lag 39 "
           "and falls to 0.0083 at 400",
    "x": {"type": "log", "fmt": "n0", "label": "Newey–West lag (log scale)", "tipLabel": "lag ",
          "min": 1, "max": 400, "ticks": [1, 2, 5, 10, 20, 50, 100, 200, 400], "values": c.LAG_GRID},
    "y": {"fmt": "n4", "tfmt": "n3", "label": "Standard error of beta", "min": 0.006, "max": 0.05,
          "ticks": [0.01, 0.02, 0.03, 0.04, 0.05]},
    "series": [
        {"name": "full-sample residuals", "endLabel": "full sample", "color": "1",
         "y": [rd(v, 6) for v in c.CURVE_POOL]},
        {"name": "residuals of yearly fits", "endLabel": "yearly fits", "color": "2",
         "y": [rd(v, 6) for v in c.CURVE_YEAR]},
    ],
    "ann": [
        {"type": "hline", "y": rd(c.SEMI.se_c[1], 6), "dash": True, "label": "classical 0.0088"},
        {"type": "hline", "y": rd(c.SEMI.se_w[1], 6), "dash": True, "label": "White 0.0129"},
        {"type": "vline", "x": 9, "dash": True, "label": "lag 9"},
    ],
    "endLabels": True, "endMargin": 86,
})

# ---------------------------------------------------------------- alphas: the 28 intercept t-stats
write("lm23-alphas", {
    "type": "bar", "height": 340,
    "alt": "Intercept t-stats of the 28 U28 market models, classical and Newey-West, sorted from Optoelectronic "
           "(-1.94 classical, -1.96 Newey-West) to Semiconductor (2.10 and 2.09); lines at plus and minus 1.96 and at "
           "Bonferroni's plus and minus 3.12",
    "categories": c.ORDER_T,
    "x": {"label": "Sector index (U28), sorted by the classical t-stat"},
    "y": {"fmt": "n2", "tfmt": "n0", "label": "t-stat of the intercept", "min": -3.5, "max": 3.5,
          "ticks": [-3, -2, -1, 0, 1, 2, 3]},
    "series": [
        {"name": "classical", "color": "1", "values": [rd(c.T_C[k], 4) for k in c.ORDER_T]},
        {"name": "Newey–West", "color": "2", "values": [rd(c.T_N[k], 4) for k in c.ORDER_T]},
    ],
    "ann": [
        {"type": "hline", "y": 1.96, "label": "1.96"}, {"type": "hline", "y": -1.96, "label": "−1.96"},
        {"type": "hline", "y": rd(c.Z_BONF, 4), "label": "Bonferroni"},
        {"type": "hline", "y": -rd(c.Z_BONF, 4), "label": "Bonferroni"},
    ],
})

# ---------------------------------------------------------------- rolling: 250-return betas, weekly plus extremes
nwin = len(c.ROLL_DATES)
keep = set(range(0, nwin, 5)) | {nwin - 1}
for b, _ in c.ROLL.values():
    keep |= {int(b.argmax()), int(b.argmin())}
keep_l = sorted(keep)
fi_b, fi_se = c.ROLL["FinancialInsurance"]
se_b, se_se = c.ROLL["Semiconductor"]
write("lm23-rolling", {
    "type": "line", "height": 330,
    "alt": "Rolling 250-return betas of FinancialInsurance and Semiconductor on the TAIEX, windows ending from "
           "November 2009 to October 2026, with classical 95% bands: FinancialInsurance falls from 1.377 in February "
           "2010 to 0.251 in May 2026 and ends at 0.308; Semiconductor ranges from 0.914 in May 2011 to 1.658 in "
           "January 2020 and ends at 1.168",
    "x": {"type": "date", "values": [c.ROLL_DATES[i] for i in keep_l]},
    "y": {"fmt": "n3", "tfmt": "n1", "label": "Beta, last 250 returns", "min": 0, "max": 1.9,
          "ticks": [0, 0.5, 1.0, 1.5]},
    "series": [
        {"name": "FinancialInsurance 95% band", "color": "1",
         "lo": [rd(fi_b[i] - 1.96 * fi_se[i], 4) for i in keep_l],
         "hi": [rd(fi_b[i] + 1.96 * fi_se[i], 4) for i in keep_l]},
        {"name": "Semiconductor 95% band", "color": "2",
         "lo": [rd(se_b[i] - 1.96 * se_se[i], 4) for i in keep_l],
         "hi": [rd(se_b[i] + 1.96 * se_se[i], 4) for i in keep_l]},
        {"name": "FinancialInsurance", "endLabel": "FinancialInsurance", "color": "1",
         "y": [rd(fi_b[i], 4) for i in keep_l]},
        {"name": "Semiconductor", "endLabel": "Semiconductor", "color": "2",
         "y": [rd(se_b[i], 4) for i in keep_l]},
    ],
    "ann": [
        {"type": "hline", "y": rd(c.BETAS["FinancialInsurance"], 4), "dash": True},
        {"type": "hline", "y": rd(c.BETAS["Semiconductor"], 4), "dash": True},
    ],
    "endLabels": True, "endMargin": 118,
})

# ---------------------------------------------------------------- regWindows: the widget's data and initial chart
WT = c.window_table()
XLO, XHI = -0.5, 2.0
for v in WT.values():          # every interval of every window and method fits the fixed x range
    for r in v["rows"]:
        for se in r[1:4]:
            assert XLO < r[0] - 1.96 * se and r[0] + 1.96 * se < XHI
init_key, init_method, init_sector = "full", "n", "Semiconductor"
rows_sorted = {k: [[float(f"{x:.6g}") for x in v["rows"][c.J[nm]]] for nm in SORTED] for k, v in WT.items()}
full_rows = rows_sorted[init_key]
ri = SORTED.index(init_sector)
init_lines = []
for j, r in enumerate(full_rows):
    b, se = r[0], r[3]
    init_lines.append({"from": [rd(b - 1.96 * se, 6), j + 1], "to": [rd(b + 1.96 * se, 6), j + 1],
                       "color": "2" if j == ri else "var(--ink-2)", "width": 4 if j == ri else 1.6})
others = [j for j in range(28) if j != ri]
write("lm23-regWindows", {
    "type": "scatter", "equal": False, "height": 600,
    "alt": "Betas of the 28 U28 market models with Newey-West 95% intervals for the full sample, Semiconductor "
           "highlighted at 1.207 (1.171 to 1.244)",
    "x": {"label": "Beta on the TAIEX", "fmt": "n3", "tfmt": "n1", "name": "beta", "min": XLO, "max": XHI,
          "ticks": [-0.5, 0, 0.5, 1.0, 1.5, 2.0]},
    "y": {"fmt": "n0", "name": "sector", "min": 0.4, "max": 28.6, "ticks": list(range(1, 29)),
          "tickLabels": SORTED},
    "series": [
        {"name": "28 sectors", "color": "1", "r": 3.6, "x": [full_rows[j][0] for j in others],
         "y": [j + 1 for j in others]},
        {"name": init_sector, "color": "2", "r": 5, "x": [full_rows[ri][0]], "y": [ri + 1]},
    ],
    "lines": init_lines,
    "widget": {
        "A": rd(c.A, 6),
        "names": SORTED,
        "cols": ["beta", "se_beta_classical", "se_beta_white", "se_beta_nw", "alpha", "se_alpha_classical",
                 "se_alpha_white", "se_alpha_nw", "r2", "s_eps"],
        "windows": [{"key": k, "label": v["label"], "T": v["T"], "lag": v["lag"], "first": v["first"],
                     "last": v["last"]} for k, v in WT.items()],
        "rows": rows_sorted,
        "xmin": XLO, "xmax": XHI,
        "init": {"window": init_key, "method": init_method, "sector": init_sector},
    },
})
