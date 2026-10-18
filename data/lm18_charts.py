"""Chart specs for LM18 (src/data/lm18-*.json), computed from TR23 and from the module's simulations.

Run:  PYTHONUTF8=1 uv run python data/lm18_charts.py      (after data/vol3_series.py; data/lm18_numbers.py checks the text)

Inputs (data/lm18_common.py): data/processed/vol3_taiex.parquet (TR23), LM12's printed S5 Cholesky factor and LM5's
printed Simpson errors. Same conventions and seeds as data/lm18_numbers.py: experiment 12 for the rate chart and
experiment 14 for the resampled months, each generator created once as np.random.default_rng([e, 20261011]).
Writes lm18-windows (the case), lm18-invtr (the inverse transform on TR23), lm18-rate (the 1/sqrt(n) rate of
(18.9)), lm18-quad (Monte Carlo against Simpson's rule) and lm18-destroy (monthly counts, data against resamples).
"""
import json
import math

import numpy as np
from lm18_common import (
    KK,
    L_PRINTED,
    P_LM5,
    ROOT,
    SIMPSON_LM5,
    X3_SIZES,
    bse,
    load,
    rng,
    x3_runs,
    x7_resamples,
)
from scipy import stats

OUT = ROOT / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)


def write(name: str, spec: dict) -> None:
    assert spec.get("alt"), name
    (OUT / f"{name}.json").write_text(json.dumps(spec, ensure_ascii=False, separators=(",", ":"), allow_nan=False),
                                      encoding="utf-8", newline="\n")
    print("wrote", f"src/data/{name}.json")


def rd(v: float, n: int) -> float:
    return round(float(v), n)


d = load()
R, T, P, dates, m = d.R, d.T, d.P, d.dates, d.m
assert (T, m) == (5849, 1231)

# ------------------------------------------------------------------ windows: the case
nwin = P.size - m
Gw = P[m:] / P[:-m]
uw = np.flatnonzero(Gw < 1)
eps = np.split(uw, np.flatnonzero(np.diff(uw) > 250) + 1)
assert len(eps) == 2 and int(Gw.argmin()) in uw
windows = {
    "alt": "Growth factor of TR23 over 1,231 sessions for each of the 4,619 windows that start on a close from "
    "2 January 2003 to 10 September 2021, log scale: 191 end below 1, all of them starting in late 2003 to early 2004 "
    "or in the second half of 2007",
    "height": 320,
    "x": {"type": "date", "label": "First close of the five-year window"},
    "y": {"type": "log", "fmt": "x2", "tfmt": "x1", "label": "Growth factor over 1,231 sessions (log scale)",
          "min": 0.7, "max": 3.7, "ticks": [0.75, 1, 1.5, 2, 3]},
    "series": [{"name": "Five-year growth factor", "color": "1", "x": dates[:nwin], "y": [rd(v, 4) for v in Gw]}],
    "ann": [{"type": "band", "x0": dates[int(e[0])], "x1": dates[int(e[-1])]} for e in eps]
    + [{"type": "hline", "y": 1, "label": "1: under water below"}],
}
write("lm18-windows", windows)

# ------------------------------------------------------------------ invtr: F-hat as a step, E2's three draws
Rs = np.sort(R)
u3 = rng(2).random(3)
ranks = [math.ceil(T * float(u)) for u in u3]
assert ranks == [818, 2712, 1019] and Rs.min() > -0.1 and Rs.max() < 0.1
xs = [-0.1] + [rd(v, 7) for v in Rs] + [0.1]
ys = [0.0] + [rd((j + 1) / T, 6) for j in range(T)] + [1.0]
invtr = {
    "alt": "Empirical distribution function of TR23's 5,849 daily returns, a staircase from 0 to 1, with the three "
    "uniform draws of the example placed at the returns they draw: -0.9468%, +0.0247% and -0.7785%",
    "height": 320,
    "x": {"type": "num", "fmt": "pct2", "tfmt": "pct0", "label": "Daily return R", "min": -0.1, "max": 0.1,
          "ticks": [-0.1, -0.05, 0, 0.05, 0.1]},
    "y": {"type": "lin", "fmt": "n4", "tfmt": "n1", "label": "Empirical distribution function, share of days with return at or below R",
          "min": 0, "max": 1, "ticks": [0, 0.2, 0.4, 0.6, 0.8, 1]},
    "series": [{"name": "Empirical distribution function", "color": "1", "step": True, "x": xs, "y": ys}],
    "ann": [{"type": "point", "x": rd(Rs[j - 1], 7), "y": rd(float(u), 7), "color": "2", "label": f"u = {u:.3f}",
             "dx": dx, "dy": dy}
            for j, u, dx, dy in zip(ranks, u3, (-74, 10, -74), (14, 4, -6), strict=True)],
}
write("lm18-invtr", invtr)

# ------------------------------------------------------------------ rate: (18.9) against 200 runs (experiment 12)
L = L_PRINTED
Sig = L @ L.T
F2, tr = float(np.linalg.norm(Sig) ** 2), float(np.trace(Sig))
cst = math.sqrt(1 + tr**2 / F2)
runs = x3_runs(L)
rms = [math.sqrt(float((runs[n] ** 2).mean())) for n in X3_SIZES]
rms_b = [bse(lambda a: math.sqrt(float((a**2).mean())), runs[n]) for n in X3_SIZES]
gap4 = float(np.linalg.norm(np.cov(np.random.default_rng(20261011).standard_normal((4382, 5)) @ L.T, rowvar=False,
                                   ddof=0) - Sig) / np.linalg.norm(Sig))
lx = [rd(math.log10(n), 4) for n in X3_SIZES]
fx = [rd(v, 3) for v in np.linspace(2, 5, 31)]
rate = {
    "alt": "Root-mean-square relative gap between simulated and model covariance matrices of S5 against the number of "
    "draws on log scales: 200 runs at each of six sizes follow the dashed formula 1.911 over the square root of n, a "
    "slope of minus one half; LM12's single run of 4,382 draws, 0.0250, lies below the 0.0289 of the formula",
    "height": 320,
    "x": {"type": "num", "fmt": "n2", "tipLabel": "log10 n = ", "label": "Number of draws n (log scale)",
          "min": 1.9, "max": 5.15, "ticks": [2, 3, 4, 5], "tickLabels": ["100", "1,000", "10,000", "100,000"]},
    "y": {"type": "log", "fmt": "n4", "tfmt": "n3", "label": "Relative gap, root mean square (log scale)",
          "min": 0.004, "max": 0.25, "ticks": [0.005, 0.01, 0.02, 0.05, 0.1, 0.2]},
    "series": [{"name": "200 runs (experiment 12)", "color": "1", "x": lx, "y": [rd(v, 5) for v in rms]},
               {"name": "Formula (18.9)", "color": "2", "dash": True, "x": fx,
                "y": [rd(cst / math.sqrt(10**v), 5) for v in fx]}],
    "ann": [{"type": "point", "x": rd(math.log10(4382), 4), "y": rd(gap4, 5), "color": "3",
             "label": "LM12's run, 0.0250", "dx": -128, "dy": 18}],
}
write("lm18-rate", rate)
print("rate: RMS " + ", ".join(f"{v:.4f}" for v in rms) + "; batch SE " + ", ".join(f"{v:.4f}" for v in rms_b))

# ------------------------------------------------------------------ quad: Simpson against Monte Carlo
pk = float(stats.norm.cdf(-KK))
rel_plain = math.sqrt((1 - pk) / pk)
rel_is = math.sqrt(math.exp(KK**2) * float(stats.norm.cdf(-2 * KK)) - pk**2) / pk
ev = [n + 1 for n in SIMPSON_LM5]
simp = [SIMPSON_LM5[n] / P_LM5 for n in SIMPSON_LM5]
mx = [0, 10]
quad = {
    "alt": "Relative error against the number of evaluations on log scales for LM5's normal tail probability: "
    "Simpson's rule falls from 0.484 at 9 evaluations to 4.83e-9 at 1,025, while the relative standard errors of plain "
    "Monte Carlo, 223.6 over root n, and of importance sampling, 2.153 over root n, fall with slope minus one half",
    "height": 320,
    "x": {"type": "num", "fmt": "n2", "tipLabel": "log10 n = ", "label": "Evaluations or draws n (log scale)",
          "min": 0, "max": 10, "ticks": [0, 2, 4, 6, 8, 10], "tickLabels": ["1", "100", "1e4", "1e6", "1e8", "1e10"]},
    "y": {"type": "log", "fmt": "sci2", "tfmt": "sci0", "label": "Relative error (log scale)", "min": 1e-9,
          "max": 1000, "ticks": [1e-9, 1e-6, 1e-3, 1, 1000]},
    "series": [{"name": "Simpson's rule (LM5)", "color": "1", "x": [rd(math.log10(e), 4) for e in ev],
                "y": [float(f"{v:.4e}") for v in simp]},
               {"name": "Plain Monte Carlo", "color": "2", "dash": True, "x": mx,
                "y": [rd(rel_plain, 2), float(f"{rel_plain / 1e5:.4e}")]},
               {"name": "Importance sampling", "color": "3", "dash": True, "x": mx,
                "y": [rd(rel_is, 4), float(f"{rel_is / 1e5:.4e}")]}],
}
write("lm18-quad", quad)

# ------------------------------------------------------------------ destroy: monthly counts, data against resamples
x7 = x7_resamples(d)
data_pmf = np.bincount(np.minimum(x7.counts, 8), minlength=9)
avg = x7.pmf.mean(axis=0)
assert [int(v) for v in data_pmf] == [210, 38, 9, 16, 4, 5, 1, 0, 3]
destroy = {
    "type": "bar",
    "alt": "Calendar months by the number of days with an absolute return of 3% or more: TR23's 286 months, 210 with "
    "none and three with eight, against the average of 1,000 resamples of the days, 154.3 with none and almost none "
    "above four",
    "height": 300, "valueLabels": True,
    "categories": ["0", "1", "2", "3", "4", "5", "6", "7", "8+"],
    "x": {"label": "Days with |R| ≥ 3% in a calendar month"},
    "y": {"fmt": "n1", "tfmt": "n0", "label": "Months"},
    "series": [{"name": "TR23, 286 months", "color": "1", "values": [int(v) for v in data_pmf], "fmt": "n0"},
               {"name": "Average of 1,000 resamples", "color": "2", "values": [rd(v, 1) for v in avg], "fmt": "n1"}],
}
write("lm18-destroy", destroy)
print("destroy: resamples " + ", ".join(f"{v:.1f}" for v in avg))
