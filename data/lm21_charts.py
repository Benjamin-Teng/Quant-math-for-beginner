"""Chart specs for LM21 (src/data/lm21-*.json), computed from TR23 and from the module's model formulas.

Run:  uv run python data/lm21_charts.py      (after data/vol3_series.py; data/lm21_numbers.py then checks the text)

Input: data/processed/vol3_taiex.parquet only (TR23, the TAIEX total-return index from FinMind's
TaiwanStockTotalReturnIndex), through data/lm21_common.py, whose conventions these charts share. Writes lm21-nulldist
(the null law and TR23's t-stats), lm21-power ((21.4) for four Sharpe ratios), lm21-calendar (the 17 statistics of
the calendar family), lm21-pvalues (their p-values against Bonferroni, Holm and Benjamini-Hochberg) and lm21-maxt
((21.9) and experiment 10's record points). No file carries a daily series: the charts hold statistics, model curves
and 11 record points of a simulated search. The widget "multitest" (src/lm21.js) embeds no data.
"""
import json
from math import log10
from pathlib import Path
from typing import Any

import numpy as np
from lm21_common import (
    C975,
    MO_NAMES,
    WD_NAMES,
    calendar,
    experiment10,
    load,
    maxq,
    power,
    tstat,
    years80,
)
from scipy import stats

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)


def rd(v: float, n: int = 6) -> float:
    return round(float(v), n)


def write(name: str, spec: dict[str, Any]) -> None:
    assert isinstance(spec.get("alt"), str) and spec["alt"].strip()
    blob = json.dumps(spec, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    assert len(blob.encode("utf-8")) < 300_000, name
    (OUT / f"{name}.json").write_text(blob, encoding="utf-8", newline="\n")
    print("wrote", f"src/data/{name}.json", f"({len(blob.encode('utf-8')):,} bytes)")


d = load()
R, T = d.R, d.T
t_all, t_pre, t_post = tstat(R), tstat(R[d.pre]), tstat(R[~d.pre])
assert (f"{t_all:.2f}", f"{t_pre:.2f}", f"{t_post:.2f}") == ("3.96", "2.05", "3.68")

# ------------------------------------------------------------------ nulldist: the null law and TR23's statistics
xs = sorted(set(np.round(np.linspace(-5, 5, 401), 6).tolist()) | {rd(-C975), rd(C975)})
phi = [rd(stats.norm.pdf(x), 6) for x in xs]
in_tail = [abs(x) >= rd(C975) - 1e-9 for x in xs]
nulldist = {
    "alt": "The standard normal density, the null law of the t-stat, with the two-sided 5% rejection region beyond "
           "plus or minus 1.96 shaded, and vertical lines at TAIEX's t-stats 3.96 for all days, 2.05 before and 3.68 "
           "from June 2015",
    "height": 280,
    "x": {"type": "num", "fmt": "n2", "tfmt": "n0", "label": "t-stat", "tipLabel": "t-stat ", "min": -5, "max": 5,
          "ticks": [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5], "values": xs},
    "y": {"type": "lin", "fmt": "n3", "tfmt": "n1", "label": "Density", "min": 0, "max": 0.42,
          "ticks": [0, 0.1, 0.2, 0.3, 0.4]},
    "series": [
        {"name": "rejection region, two-sided 5%", "color": "2", "opacity": 0.35,
         "lo": [0.0 if t else None for t in in_tail], "hi": [p if t else None for p, t in zip(phi, in_tail)]},
        {"name": "null law of the t-stat", "color": "1", "y": phi},
    ],
    "ann": [{"type": "vline", "x": rd(t_all), "label": "3.96"},
            {"type": "vline", "x": rd(t_pre), "dash": True, "label": "2.05", "dy": 16},
            {"type": "vline", "x": rd(t_post), "dash": True, "label": "3.68", "anchor": "end"}],
}
write("lm21-nulldist", nulldist)

# ------------------------------------------------------------------ power: (21.4) for four annual Sharpe ratios
sr_a = float(R.mean() / R.std(ddof=0)) * np.sqrt(d.A)
srs = [(1.0, "SR 1"), (sr_a, "SR 0.81 (TR23)"), (0.5, "SR 0.5"), (0.25, "SR 0.25")]
grid = set(np.round(np.logspace(0, np.log10(200), 230), 4).tolist())
grid |= {rd(years80(v), 4) for v, _ in srs} | {rd(d.years, 4)}
xp = sorted(grid)
pw = {
    "alt": "Power of the two-sided 5% test of a zero mean against years of daily data on a log axis, for annual "
           "Sharpe ratios of 1, 0.81 (TAIEX's), 0.5 and 0.25; 80% power comes at 7.85, 11.9, 31.4 and 125.6 years",
    "height": 300,
    "x": {"type": "log", "fmt": "n2", "tfmt": "n0", "label": "Years of daily data (log scale)", "tipLabel": "years ",
          "min": 1, "max": 200, "ticks": [1, 2, 5, 10, 20, 50, 100, 200], "values": xp},
    "y": {"type": "lin", "fmt": "n3", "tfmt": "n1", "label": "Power", "min": 0, "max": 1,
          "ticks": [0, 0.2, 0.4, 0.6, 0.8, 1]},
    "series": [{"name": name, "color": str(k + 1), "y": [rd(power(v, x), 5) for x in xp]}
               for k, (v, name) in enumerate(srs)],
    # labels placed off the curves: "80% power" to the left of SR 1's point, "TR23's span" low on the right of its line,
    # where every curve is above 0.2 (book.js draws a vline label at m.t + 11 + dy, m.t = 12, plot height 244)
    "ann": [{"type": "hline", "y": 0.8, "dash": True},
            {"type": "vline", "x": rd(d.years, 4), "dash": True, "label": "TR23's span", "dy": 200}]
           + [{"type": "point", "x": rd(years80(v), 4), "y": 0.8, "color": str(k + 1)}
              | ({"label": "80% power", "dx": -8, "dy": -8, "anchor": "end"} if k == 0 else {})
              for k, (v, _) in enumerate(srs)],
}
assert [f"{years80(v):.2f}" for v, _ in srs] == ["7.85", "11.92", "31.40", "125.58"]
write("lm21-power", pw)

# ------------------------------------------------------------------ calendar: the 17 statistics (21.3)
fam = calendar(d)
c_bonf = float(stats.norm.isf(0.025 / len(fam)))
cal = {
    "type": "bar",
    "alt": "Two-sample statistics of the 12 calendar months and the 5 weekdays of TAIEX against all other days; only "
           "Wednesday, at 2.36, passes 1.96, and none passes Bonferroni's 2.97 for 17 tests",
    "height": 300,
    "valueLabels": True,
    "categories": [f[0] for f in fam],
    "x": {"label": "Month or weekday, each against all other TR23 days"},
    "y": {"fmt": "n2", "tfmt": "n0", "label": "Statistic (21.3)", "min": -3.2, "max": 3.2,
          "ticks": [-3, -2, -1, 0, 1, 2, 3]},
    "series": [{"name": "two-sample statistic", "color": "1", "values": [rd(f[3]) for f in fam]}],
    "ann": [{"type": "hline", "y": rd(C975)}, {"type": "hline", "y": rd(-C975), "label": "±1.96: 5% level, one test"},
            {"type": "hline", "y": rd(c_bonf)}, {"type": "hline", "y": rd(-c_bonf), "label": "±2.97: Bonferroni, 17 tests"}],
}
assert cal["categories"] == MO_NAMES + WD_NAMES[:5]
write("lm21-calendar", cal)

# ------------------------------------------------------------------ pvalues: the sorted p-values against three rules
order = sorted(range(len(fam)), key=lambda k: fam[k][4])
m = len(fam)
ranks = list(range(1, m + 1))
ys = [log10(fam[k][4]) for k in order]
named = [(j + 1, f"{fam[k][0]} {fam[k][4]:.3f}") for j, k in enumerate(order) if fam[k][0] in ("Wed", "Dec")]
assert named == [(1, "Wed 0.018"), (2, "Dec 0.127")]


def path(f, color: str, label: str, dash: bool = False, at: int = m) -> list[dict[str, Any]]:
    """Segments between consecutive ranks of the level f(i), labelled at rank at (Holm's and Benjamini-Hochberg's
    5% levels both end at 0.05, so Holm's label sits at an earlier rank)."""
    segs = []
    for i in range(1, m):
        s = {"from": [i, rd(log10(f(i)))], "to": [i + 1, rd(log10(f(i + 1)))], "color": color}
        if dash:
            s["dash"] = True
        if i + 1 == at:
            s["label"] = label
        segs.append(s)
    return segs


pv_spec = {
    "type": "scatter",
    "alt": "The 17 calendar p-values of TAIEX in increasing order on a log scale, against the levels of Bonferroni, "
           "Holm and Benjamini-Hochberg; every point lies above every line, so no rule rejects",
    "height": 320,
    "x": {"label": "Rank i of the p-value", "name": "rank", "fmt": "n0", "min": 0.5, "max": 17.5,
          "ticks": [1, 3, 5, 7, 9, 11, 13, 15, 17]},
    "y": {"label": "p-value (log scale)", "name": "log10 p", "fmt": "n2", "min": -3, "max": 0,
          "ticks": [-3, -2, -1, 0], "tickLabels": ["0.001", "0.01", "0.1", "1"]},
    "series": [{"name": "calendar family", "color": "1", "x": ranks, "y": [rd(v, 9) for v in ys]}],
    "points": [{"at": [1, rd(ys[0], 9)], "label": named[0][1], "color": "1"},
               {"at": [2, rd(ys[1], 9)], "label": named[1][1], "color": "1", "dx": 8, "dy": 16}],
    "lines": [{"from": [1, rd(log10(0.05 / m))], "to": [m, rd(log10(0.05 / m))], "color": "2", "label": "Bonferroni"}]
             + path(lambda i: 0.05 / (m - i + 1), "3", "Holm", at=13)
             + path(lambda i: i * 0.05 / m, "4", "BH, q = 5%")
             + path(lambda i: i * 0.10 / m, "4", "BH, q = 10%", dash=True),
}
assert all(log10(fam[k][4]) > log10(0.10 * (j + 1) / m) for j, k in enumerate(order))
write("lm21-pvalues", pv_spec)

# ------------------------------------------------------------------ maxt: (21.9) and experiment 10's records
tt = experiment10(d)
run = np.maximum.accumulate(tt)
rec = [i for i in range(len(tt)) if i == 0 or tt[i] > run[i - 1]]
assert len(rec) == 11 and rec[-1] + 1 == 7840
mg = sorted(set(np.unique(np.round(np.logspace(0, 4, 160)).astype(int)).tolist()) | {17, 100, 1000, 10000})
maxt = {
    "alt": "The largest t-stat of a search against the number of rules m on a log axis: the model's median and 90% "
           "range for independent null statistics, and the best of the first m random long-short rules on TAIEX, "
           "which reaches 2.95 by rule 90, 3.28 at rule 1,022 and 3.97 by rule 7,840",
    "height": 320,
    "x": {"type": "log", "fmt": "n0", "label": "Number of rules m (log scale)", "tipLabel": "m = ", "min": 1,
          "max": 10000, "ticks": [1, 10, 100, 1000, 10000], "tickLabels": ["1", "10", "100", "1,000", "10,000"],
          "values": mg},
    "y": {"type": "lin", "fmt": "n2", "tfmt": "n0", "label": "Largest t-stat", "min": -2, "max": 4.6,
          "ticks": [-2, -1, 0, 1, 2, 3, 4]},
    "series": [
        {"name": "model, 90% range", "color": "1", "lo": [rd(maxq(0.05, k), 4) for k in mg],
         "hi": [rd(maxq(0.95, k), 4) for k in mg]},
        {"name": "model median", "color": "1", "dash": True, "y": [rd(maxq(0.5, k), 4) for k in mg]},
        {"name": "best of m random rules on TR23", "color": "2", "step": True, "x": [i + 1 for i in rec] + [10000],
         "y": [rd(tt[i], 4) for i in rec]},
    ],
    "ann": [{"type": "hline", "y": 3, "dash": True, "label": "t = 3"}],
}
assert [f"{maxq(0.5, k):.2f}" for k in (17, 100, 1000, 10000)] == ["1.75", "2.46", "3.20", "3.81"]
write("lm21-maxt", maxt)
