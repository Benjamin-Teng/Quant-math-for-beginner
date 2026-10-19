"""Chart specs for LM20 (src/data/lm20-*.json), computed from TR23 and from LM20's simulations.

Run:  uv run python data/lm20_charts.py      (after data/vol3_series.py; data/lm20_numbers.py checks the text)

Inputs and conventions: data/lm20_common.py (TR23's daily simple returns, log returns for sums, divisor T, A = T /
years, the Student-t fit, Hill's estimator with the guard 1e-12, experiment 1's seed default_rng([1, 20261011])).
No chart carries a daily series in date order: the charts plot simulated histograms, standard errors by sampling
interval, model curves, a profile likelihood and Hill estimates by threshold.

Writes:
  lm20-sampling-mean, lm20-sampling-vol  experiment 1: histograms of A x mean and sqrt(A) x s over 10,000 one-year
                                         samples from the normal and the Student-t model (step series on bin edges)
  lm20-merton                            standard errors of the annual mean and volatility from non-overlapping m-day
                                         sums of log returns, m = 1 ... 246 (log x axis)
  lm20-years                             the 95% interval for an annual mean against 1 to 100 years (log x axis)
  lm20-profile                           the profile log-likelihood of the degrees of freedom and its parabola
  lm20-hill                              Hill estimates and their 95% band for thresholds 1.0% to 6.0%
  lm20-coverage                          the widget's data: 97.5% quantiles of t_{T-1}, T = 2 ... 250, drawn as a line
                                         chart (the page shows it only if the widget does not run)
"""
import json
import math
from pathlib import Path
from typing import Any

import lm20_common as c
import numpy as np
from scipy import optimize, stats

OUT = Path(__file__).resolve().parents[1] / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)
A, T, RB, S, Z = c.A, c.T, c.RB, c.S, c.Z


def rd(v: float, n: int) -> float:
    return round(float(v), n)


def write(name: str, spec: dict[str, Any]) -> None:
    assert isinstance(spec.get("alt"), str) and spec["alt"].strip()
    blob = json.dumps(spec, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    assert len(blob.encode("utf-8")) < 300_000, name
    (OUT / f"{name}.json").write_text(blob, encoding="utf-8", newline="\n")
    print(f"wrote src/data/{name}.json ({len(blob.encode('utf-8')):,} bytes)")


# ------------------------------------------------------------------ experiment 1: sampling distributions
sims = c.experiment1()
am = {k: A * v.mean(axis=1) for k, v in sims.items()}
av = {k: math.sqrt(A) * v.std(axis=1, ddof=0) for k, v in sims.items()}


def hist(x: np.ndarray, lo: float, hi: float, width: float) -> tuple[list[float], list[float]]:
    """Shares of all draws in bins [lo + i w, lo + (i + 1) w); draws outside [lo, hi) count in no bin."""
    nb = round((hi - lo) / width)
    edges = [rd(lo + i * width, 6) for i in range(nb + 1)]
    idx = np.floor((x - lo) / width).astype(int)
    ok = (idx >= 0) & (idx < nb)
    counts = np.bincount(idx[ok], minlength=nb)
    return edges, [rd(v / len(x), 5) for v in counts]


e_m, h_mn = hist(am["normal"], -0.60, 0.90, 0.02)
_, h_mt = hist(am["t"], -0.60, 0.90, 0.02)
write("lm20-sampling-mean", {
    "alt": "Histograms of the annual mean from 10,000 simulated one-year samples of 246 days, normal model and "
           "Student-t model with TAIEX's mean and standard deviation: both spread about 19 points around 15%",
    "height": 240,
    "x": {"type": "num", "fmt": "pct0", "label": "Annual mean, A × sample mean (bins of 2 points)",
          "tipLabel": "bin from ", "min": -0.6, "max": 0.9, "ticks": [-0.6, -0.3, 0, 0.3, 0.6, 0.9]},
    "y": {"type": "lin", "fmt": "pct2", "tfmt": "pct0", "label": "Share of samples", "min": 0, "max": 0.05,
          "ticks": [0, 0.01, 0.02, 0.03, 0.04, 0.05]},
    "series": [
        {"name": "Normal model", "color": "1", "step": True, "x": e_m, "y": h_mn},
        {"name": "Student-t model", "color": "2", "step": True, "x": e_m, "y": h_mt},
    ],
})
e_v, h_vn = hist(av["normal"], 0.10, 0.40, 0.0025)
_, h_vt = hist(av["t"], 0.10, 0.40, 0.0025)
assert int((av["t"] >= 0.40).sum()) == 35 and int((av["normal"] >= 0.40).sum()) == 0
assert int((av["t"] < 0.10).sum()) == 0 and int((av["normal"] < 0.10).sum()) == 0
# the alt text's numbers: the normal model's range rounds to 16% and 22%, its 95% range is 17.3% to 20.6%,
# and the Student-t model's lowest value rounds to 12%
assert [f"{100 * v:.0f}" for v in (av["normal"].min(), av["normal"].max(), av["t"].min())] == ["16", "22", "12"]
assert [f"{100 * c.qinv(av['normal'], u):.1f}" for u in (0.025, 0.975)] == ["17.3", "20.6"]
write("lm20-sampling-vol", {
    "alt": "Histograms of the annualized volatility from the same 10,000 samples: the normal model's lie between 16% "
           "and 22%, 95% of them between 17.3% and 20.6%, the Student-t model's spread from about 12% to beyond 40%",
    "height": 240,
    "x": {"type": "num", "fmt": "pct2", "tfmt": "pct0", "label": "Annual volatility, √A × sample s (bins of 0.25 points)",
          "tipLabel": "bin from ", "min": 0.10, "max": 0.40, "ticks": [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]},
    "y": {"type": "lin", "fmt": "pct2", "tfmt": "pct0", "label": "Share of samples", "min": 0, "max": 0.12,
          "ticks": [0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12]},
    "series": [
        {"name": "Normal model", "color": "1", "step": True, "x": e_v, "y": h_vn},
        {"name": "Student-t model", "color": "2", "step": True, "x": e_v, "y": h_vt},
    ],
})
assert max(h_vn) < 0.12 and max(h_mn + h_mt) < 0.05

# ------------------------------------------------------------------ Merton: standard errors by sampling interval
ms = list(c.MERTON_M)
rows = [c.merton(m) for m in ms]
iid_mean = math.sqrt(A) * c.S_R / math.sqrt(c.TAU)
assert f"{100 * iid_mean:.2f}" == "3.90"
write("lm20-merton", {
    "alt": "Standard errors of TAIEX's annual mean and annual volatility estimated from sums over 1 to 246 sessions: "
           "the mean's stays near 3.9 points at every interval, the volatility's grows from 0.34 to 4.43 points",
    "height": 300,
    "x": {"type": "log", "fmt": "n0", "label": "Sessions in each sum (log scale)", "tipLabel": "sessions per sum: ",
          "values": ms, "ticks": [1, 5, 21, 62, 246],
          "tickLabels": ["1 day", "1 week", "1 month", "1 quarter", "1 year"]},
    "y": {"type": "lin", "fmt": "n2", "tfmt": "n0", "label": "Standard error, percentage points a year", "min": 0,
          "max": 5, "ticks": [0, 1, 2, 3, 4, 5]},
    "series": [
        {"name": "Annual mean, data", "color": "1", "y": [rd(100 * r[1], 4) for r in rows]},
        {"name": "Annual mean, iid model (3.90)", "color": "1", "dash": True, "y": [rd(100 * iid_mean, 4)] * len(ms)},
        {"name": "Annual volatility, data", "color": "2", "y": [rd(100 * r[2], 4) for r in rows]},
        {"name": "Annual volatility, normal iid model", "color": "2", "dash": True,
         "y": [rd(100 * r[3], 4) for r in rows]},
    ],
})

# ------------------------------------------------------------------ years: the interval against years of data
yrs = sorted({rd(v, 4) for v in np.geomspace(1, 100, 49)} | {rd(c.TAU, 4)})
am0, vol0 = A * RB, math.sqrt(A) * S
write("lm20-years", {
    "alt": "The 95% interval for an annual mean with TAIEX's mean of 15.38% and volatility of 18.96%, against 1 to 100 "
           "years of data on a log scale: from -21.8% to 52.5% after one year, 7.8% to 23.0% after TAIEX's 23.76 "
           "years and 11.7% to 19.1% after a hundred",
    "height": 300,
    "x": {"type": "log", "fmt": "n2", "tfmt": "n0", "label": "Years of data (log scale)", "tipLabel": "years: ", "values": yrs,
          "ticks": [1, 2, 5, 10, 20, 50, 100]},
    "y": {"type": "lin", "fmt": "pct1", "tfmt": "pct0", "label": "Annual mean, 95% interval", "min": -0.3,
          "max": 0.6, "ticks": [-0.2, 0, 0.2, 0.4, 0.6]},
    "series": [
        {"name": "95% interval", "color": "1", "lo": [rd(am0 - Z * vol0 / math.sqrt(y), 6) for y in yrs],
         "hi": [rd(am0 + Z * vol0 / math.sqrt(y), 6) for y in yrs]},
        {"name": "TR23's annual mean, 15.38%", "color": "1", "y": [rd(am0, 6)] * len(yrs)},
    ],
    "ann": [{"type": "hline", "y": 0},
            {"type": "vline", "x": rd(c.TAU, 4), "dash": True, "label": "TR23, 23.76 years"}],
})

# ------------------------------------------------------------------ profile log-likelihood of nu
nus = [rd(2.5 + 0.02 * i, 2) for i in range(66)]
prof = [c.profile(v) for v in nus]
quad = [-(v - c.NU) ** 2 / (2 * c.SE_T[0] ** 2) for v in nus]
drop = Z**2 / 2
lr = [float(optimize.brentq(lambda q: c.profile(q) + drop, a, b)) for a, b in ((2.5, c.NU), (c.NU, 4.0))]
wald = [c.NU - Z * c.SE_T[0], c.NU + Z * c.SE_T[0]]
assert [f"{v:.2f}" for v in lr + wald] == ["2.80", "3.37", "2.78", "3.35"]


def clip10(v: float) -> float | None:
    return rd(v, 4) if v >= -10 else None


write("lm20-profile", {
    "alt": "Profile log-likelihood of the Student-t's degrees of freedom for TAIEX, against the parabola of the observed "
           "information: both peak at 3.065; the curve falls 1.92 below its top at 2.80 and 3.37, the parabola at "
           "2.78 and 3.35",
    "height": 300,
    "x": {"type": "num", "fmt": "n2", "label": "Degrees of freedom", "tipLabel": "degrees of freedom: ", "min": 2.5,
          "max": 3.8, "ticks": [2.5, 2.75, 3.0, 3.25, 3.5, 3.75]},
    "y": {"type": "lin", "fmt": "n2", "tfmt": "n0", "label": "Log-likelihood minus its maximum", "min": -10,
          "max": 0.5, "ticks": [-10, -8, -6, -4, -2, 0]},
    "series": [
        {"name": "Profile log-likelihood", "color": "1", "x": nus, "y": [clip10(v) for v in prof]},
        {"name": "Parabola from the observed information", "color": "2", "dash": True, "x": nus,
         "y": [clip10(v) for v in quad]},
    ],
    "ann": [{"type": "hline", "y": rd(-drop, 4), "dash": True, "label": "−1.92"},
            {"type": "point", "x": rd(lr[0], 4), "y": rd(-drop, 4), "label": "2.80", "color": "1", "dx": -8, "dy": -8,
             "anchor": "end"},
            {"type": "point", "x": rd(lr[1], 4), "y": rd(-drop, 4), "label": "3.37", "color": "1", "dx": 8, "dy": -8},
            {"type": "point", "x": rd(wald[0], 4), "y": rd(-drop, 4), "label": "2.78", "color": "2", "dx": -8,
             "dy": 16, "anchor": "end"},
            {"type": "point", "x": rd(wald[1], 4), "y": rd(-drop, 4), "label": "3.35", "color": "2", "dx": -8,
             "dy": 16, "anchor": "end"}],
})

# ------------------------------------------------------------------ Hill estimates by threshold
x0s = [rd(0.01 + 0.0005 * i, 4) for i in range(101)]
hl = [c.hill_fast(x0) for x0 in x0s]
for x0s_, x0 in (("0.02", 0.02), ("0.03", 0.03), ("0.04", 0.04), ("0.05", 0.05)):
    assert c.hill(x0s_)[0] == c.hill_fast(x0)[0]
lo_h = [rd(a - Z * e, 4) for _, a, e in hl]
hi_h = [rd(a + Z * e, 4) for _, a, e in hl]
ymax = max(hi_h)
assert 10 < ymax < 12, ymax
marks = []
for x0s_, dx, dy, anc in (("0.02", 8, 18, "start"), ("0.03", -8, -10, "end"), ("0.04", 8, -10, "start"),
                          ("0.05", -8, 22, "end")):
    k, a, _ = c.hill(x0s_)
    marks.append({"type": "point", "x": float(x0s_), "y": rd(a, 4), "label": f"{float(x0s_):.0%} (k = {k}): {a:.2f}",
                  "color": "1", "dx": dx, "dy": dy, "anchor": anc})
assert f"{hl[0][1]:.1f}" == "1.7"                                   # the estimate at 1%
assert [f"{c.hill(x)[1]:.2f}" for x in ("0.02", "0.03", "0.04", "0.05")] == ["2.49", "3.63", "4.93", "4.76"]
write("lm20-hill", {
    "alt": "Hill estimates of TAIEX's tail index for loss thresholds from 1% to 6%, with a 95% band: the estimate "
           "rises from about 1.7 at 1% to 4.93 at 4% (2.49 at 2%, 3.63 at 3%), then wanders (4.76 at 5%) while the "
           "band widens",
    "height": 320,
    "x": {"type": "num", "fmt": "pct2", "tfmt": "pct0", "label": "Loss threshold", "tipLabel": "threshold: ",
          "min": 0.01, "max": 0.06, "ticks": [0.01, 0.02, 0.03, 0.04, 0.05, 0.06]},
    "y": {"type": "lin", "fmt": "n2", "tfmt": "n0", "label": "Tail index", "min": 0, "max": 12,
          "ticks": [0, 2, 4, 6, 8, 10, 12]},
    "series": [
        {"name": "95% interval", "color": "1", "x": x0s, "lo": lo_h, "hi": hi_h},
        {"name": "Hill estimate", "color": "1", "x": x0s, "y": [rd(a, 4) for _, a, _ in hl]},
    ],
    "ann": [{"type": "hline", "y": rd(c.NU, 4), "dash": True, "label": "Student-t fit, 3.065"}] + marks,
})

# ------------------------------------------------------------------ the widget's data: t quantiles
Ts = list(range(2, 251))
tq = [rd(float(stats.t.ppf(0.975, n - 1)), 10) for n in Ts]
write("lm20-coverage", {
    "alt": "The 97.5% quantile of the Student-t with T - 1 degrees of freedom for samples of 2 to 250 days, against "
           "the normal quantile 1.96: 12.71 at two days, 2.26 at ten and 1.97 at 250",
    "height": 280,
    "x": {"type": "log", "fmt": "n0", "label": "Days in the sample, T (log scale)", "tipLabel": "T = ", "values": Ts,
          "ticks": [2, 5, 10, 20, 50, 100, 200]},
    "y": {"type": "log", "fmt": "n4", "tfmt": "n0", "label": "97.5% quantile", "min": 1.5, "max": 15,
          "ticks": [2, 5, 10]},
    "series": [{"name": "t quantile, T − 1 degrees of freedom", "color": "1", "y": tq}],
    "ann": [{"type": "hline", "y": 1.96, "dash": True, "label": "1.96"}],
    "widget": {"tq": tq, "Tmin": 2, "Tmax": 250, "Rbar": rd(RB, 12), "s": rd(S, 12), "n": 1000, "shown": 100,
               "init": {"model": "normal", "T": 10, "interval": "t", "seed": 1}},
})
assert f"{tq[0]:.2f}" == "12.71" and f"{tq[8]:.2f}" == "2.26" and f"{tq[-1]:.2f}" == "1.97"
