"""Chart specs for LM24 (src/data/lm24-*.json), computed from TR23 and U28.

Run:  PYTHONUTF8=1 uv run python data/lm24_charts.py      (data/lm24_numbers.py checks the text)

Inputs and conventions: data/lm24_common.py. Writes
  lm24-case       scatter: the 28 sectors' annual means, first half against second half (price indices, U28's halves)
  lm24-manager    line: the sceptic's prior Beta(82, 82), its posterior Beta(90, 86), the flat prior's posterior Beta(9, 5)
  lm24-normal     line: TR23's annual mean, prior N(0, SE^2), likelihood N(A Rbar, SE^2), posterior at c = 1/2
  lm24-forest     scatter: first-half means with iid 95% intervals and second-half means, sorted by first-half mean
  lm24-oos        line: out-of-sample miss against the weight c, forward and reverse
  lm24-kelly      line, log x: the quadratic Bayes fraction c fhat and the exact root of (4.5) against A sigma0
  lm24-posterior  line: the widget's initial chart (A sigma0 = 10 points), with the widget's inputs in "widget"
No published file carries a daily series: the charts plot statistics of the 28 sectors and model curves, and the widget
embeds four TR23 statistics (plans/vol-4.md, "No full daily series in published files").
"""
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lm24_common as C

OUT = HERE.parent / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)


def rd(v: float, n: int) -> float:
    return round(float(v), n)


def write(name: str, spec: dict[str, Any]) -> None:
    assert isinstance(spec.get("alt"), str) and spec["alt"].strip()
    text = json.dumps(spec, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    assert len(text.encode("utf-8")) < 300_000, (name, len(text))
    (OUT / f"{name}.json").write_text(text, encoding="utf-8", newline="\n")
    print("wrote", f"src/data/{name}.json", f"({len(text.encode('utf-8')):,} bytes)")


A, RB, S, SE, FHAT, VOL = C.A, C.RB, C.S, C.SE, C.FHAT, C.VOL
names, a1, a2 = C.NAMES, C.A1, C.A2
gm1 = float(a1.mean())

# ------------------------------------------------------------------ case: first-half against second-half annual means
lo, hi = -0.05, 0.35
LAB = {"Automobile": (8, 14), "ShippingTransportation": (8, -8), "Semiconductor": (8, -8),
       "ElectronicPartsComponents": (-8, -8)}
case = {
    "type": "scatter",
    "alt": "Annual mean price returns of the 28 TWSE sector indices in the second half (October 2017 to October 2026) "
           "against the first half (December 2008 to October 2017): the points scatter with correlation -0.05 around "
           "the grand mean line, not along the 45-degree line; Automobile fell from 21.65% to 3.67%, "
           "ShippingTransportation rose from 1.89% to 17.57%",
    "height": 380,
    "x": {"label": "First half: annual mean (price index)", "fmt": "pct2", "tfmt": "pct0", "name": "first half",
          "min": lo, "max": hi, "ticks": [-0.05, 0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35]},
    "y": {"label": "Second half: annual mean (price index)", "fmt": "pct2", "tfmt": "pct0", "name": "second half",
          "min": lo, "max": hi, "ticks": [-0.05, 0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35]},
    "series": [{"name": "Sector", "color": "1", "x": [rd(v, 6) for v in a1], "y": [rd(v, 6) for v in a2]}],
    "lines": [
        {"from": [lo, lo], "to": [hi, hi], "color": "2", "dash": True, "label": "own mean"},
        {"from": [lo, rd(gm1, 6)], "to": [hi, rd(gm1, 6)], "color": "3", "dash": True,
         "label": f"grand mean {100 * gm1:.2f}%"},
    ],
    "points": [{"at": [rd(a1[names.index(n)], 6), rd(a2[names.index(n)], 6)], "label": n, "color": "1",
                "dx": d[0], "dy": d[1], **({"anchor": "end"} if d[0] < 0 else {})} for n, d in LAB.items()],
}
assert f"{100 * gm1:.2f}" == "10.49"
write("lm24-case", case)

# ------------------------------------------------------------------ manager: beta prior and posteriors
th = [rd(0.25 + 0.0025 * k, 4) for k in range(281)]
manager = {
    "alt": "Densities of a manager's monthly chance theta of beating the index: the sceptic's prior Beta(82, 82) and "
           "its posterior Beta(90, 86) after 8 good months of 12, both narrow around 0.5, and the flat prior's "
           "posterior Beta(9, 5), wide and centred near 0.64",
    "height": 300,
    "x": {"type": "num", "fmt": "n3", "tfmt": "n2", "label": "Monthly chance of beating the index, theta",
          "tipLabel": "theta = ", "min": 0.25, "max": 0.95, "ticks": [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
          "values": th},
    "y": {"type": "lin", "fmt": "n2", "tfmt": "n0", "label": "Density", "min": 0, "max": 12, "ticks": [0, 3, 6, 9, 12]},
    "series": [
        {"name": "Sceptic's prior Beta(82, 82)", "color": "3", "dash": True,
         "y": [rd(stats.beta.pdf(x, 82, 82), 4) for x in th]},
        {"name": "Sceptic's posterior Beta(90, 86)", "color": "1", "y": [rd(stats.beta.pdf(x, 90, 86), 4) for x in th]},
        {"name": "Flat prior's posterior Beta(9, 5)", "color": "2", "y": [rd(stats.beta.pdf(x, 9, 5), 4) for x in th]},
    ],
    "ann": [{"type": "vline", "x": 0.5, "dash": True, "label": "0.5", "anchor": "end"},
            {"type": "vline", "x": 0.55, "dash": True, "label": "0.55"}],
}
write("lm24-manager", manager)

# ------------------------------------------------------------------ normal: prior, likelihood, posterior at c = 1/2
se_a = A * SE                         # standard error of the annual mean, as a fraction (3.89 points)
pm_h, psd_h = C.post(0.5)
xs = [rd(-0.15 + 0.0025 * k, 4) for k in range(201)]


def dens(x: float, m: float, sd: float) -> float:
    """Normal density per percentage point at x (fractions)."""
    return rd(0.01 * float(stats.norm.pdf(x, m, sd)), 5)


normal = {
    "alt": "Densities of TAIEX's annual mean return: the prior centred at 0 with standard deviation 3.89 points, the "
           "likelihood centred at the sample's 15.38% with the same spread, and the posterior halfway, at 7.69% with "
           "standard deviation 2.75 points",
    "height": 300,
    "x": {"type": "num", "fmt": "pct2", "tfmt": "pct0", "label": "Annual mean return (TAIEX total-return index)", "tipLabel": "",
          "min": -0.15, "max": 0.35, "ticks": [-0.1, 0, 0.1, 0.2, 0.3], "values": xs},
    "y": {"type": "lin", "fmt": "n4", "tfmt": "n2", "label": "Density per percentage point", "min": 0, "max": 0.16,
          "ticks": [0, 0.04, 0.08, 0.12, 0.16]},
    "series": [
        {"name": "Prior N(0, 3.89²)", "color": "3", "dash": True, "y": [dens(x, 0.0, se_a) for x in xs]},
        {"name": "Likelihood N(15.38%, 3.89²), unit area", "color": "2", "y": [dens(x, A * RB, se_a) for x in xs]},
        {"name": "Posterior N(7.69%, 2.75²)", "color": "1", "y": [dens(x, A * pm_h, A * psd_h) for x in xs]},
    ],
    "ann": [{"type": "vline", "x": 0, "dash": True}],
}
assert (f"{100 * se_a:.2f}", f"{100 * A * RB:.2f}", f"{100 * A * pm_h:.2f}", f"{100 * A * psd_h:.2f}") == (
    "3.89", "15.38", "7.69", "2.75")
write("lm24-normal", normal)

# ------------------------------------------------------------------ forest: first-half intervals, second-half means
hw = C.A28 * C.Z975 * C.X[:C.H].std(axis=0, ddof=0) / math.sqrt(C.H)
order = [int(i) for i in np.argsort(a1)]          # ascending, so the highest first-half mean is the top row
rows = list(range(1, C.N + 1))
forest = {
    "type": "scatter",
    "alt": "The 28 sector price indices sorted by first-half annual mean, each with its iid 95% interval of half-width "
           "9 to 19 points, and each sector's second-half mean; every interval contains the first half's grand mean "
           "of 10.49%, and the second-half means scatter without regard to the first-half order",
    "height": 600, "legend": True,
    "x": {"label": "Annual mean (price index), with 95% intervals", "fmt": "pct2", "tfmt": "pct0", "name": "annual mean",
          "min": -0.20, "max": 0.40, "ticks": [-0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4]},
    "y": {"fmt": "n0", "name": "sector", "min": 0.3, "max": C.N + 1.6, "ticks": rows,
          "tickLabels": [names[i] for i in order]},
    "series": [
        {"name": "First half, with its 95% interval", "color": "1", "x": [rd(a1[i], 6) for i in order], "y": rows},
        {"name": "Second half", "color": "2", "x": [rd(a2[i], 6) for i in order], "y": rows},
    ],
    "lines": [{"from": [rd(a1[i] - hw[i], 6), r], "to": [rd(a1[i] + hw[i], 6), r], "color": "1", "width": 1.5}
              for r, i in zip(rows, order)],
    "segments": [{"from": [rd(gm1, 6), 0.3], "to": [rd(gm1, 6), C.N + 0.7], "color": "3",
                  "label": f"grand mean {100 * gm1:.2f}%"}],
}
assert all(abs(a1[i] - gm1) < hw[i] for i in range(C.N))
assert (f"{100 * hw.min():.0f}", f"{100 * hw.max():.0f}") == ("9", "19")
assert -0.20 < float((a1 - hw).min()) and float((a1 + hw).max()) < 0.40 and -0.20 < float(a2.min())
write("lm24-forest", forest)

# ------------------------------------------------------------------ oos: miss against the weight, both directions
_, _, _, c_rr = C.js(C.X[C.H:])
_, _, _, c_dr = C.js(C.XD[C.H:])
cs = sorted({rd(0.02 * k, 2) for k in range(51)} | {rd(c_rr, 5), rd(c_dr, 5)})
fwd = [rd(100 * C.oos(C.M1, C.M2, c), 4) for c in cs]
rev = [rd(100 * C.oos(C.M2, C.M1, c), 4) for c in cs]
oos = {
    "alt": "Root-mean-square miss of the shrunk sector means against the other half, in points a year, for weights c "
           "from 0 to 1: estimated on the first half the miss rises from 8.5 at c = 0 to 9.8 at c = 1; estimated on "
           "the second half it rises from 4.5 to 9.8, with 5.1 and 6.9 at the James-Stein weights 0.25 and 0.59",
    "height": 300,
    "x": {"type": "num", "fmt": "n3", "tfmt": "n1", "label": "Data's weight c (0 = grand mean, 1 = own means)",
          "tipLabel": "c = ", "min": 0, "max": 1, "ticks": [0, 0.2, 0.4, 0.6, 0.8, 1.0], "values": cs},
    "y": {"type": "lin", "fmt": "n2", "tfmt": "n0", "label": "Root-mean-square miss (points a year)", "min": 0,
          "max": 12, "ticks": [0, 2, 4, 6, 8, 10, 12]},
    "series": [
        {"name": "First half judged on the second (out-of-sample)", "color": "1", "y": fwd},
        {"name": "Second half judged on the first (stability check)", "color": "2", "dash": True, "y": rev},
    ],
    "ann": [
        {"type": "point", "x": 0, "y": fwd[0], "color": "1", "label": "c-hat = 0: 8.5", "dx": 8, "dy": -8},
        {"type": "point", "x": rd(c_rr, 5), "y": rev[cs.index(rd(c_rr, 5))], "color": "2",
         "label": "c-hat 0.25: 5.1", "dx": 8, "dy": 16},
        {"type": "point", "x": rd(c_dr, 5), "y": rev[cs.index(rd(c_dr, 5))], "color": "2",
         "label": "common removed, 0.59: 6.9", "dx": 8, "dy": 16},
    ],
}
assert [f"{v:.1f}" for v in (fwd[0], fwd[-1], rev[0], rev[cs.index(rd(c_rr, 5))], rev[cs.index(rd(c_dr, 5))],
                            rev[-1])] == ["8.5", "9.8", "4.5", "5.1", "6.9", "9.8"]
write("lm24-oos", oos)

# ------------------------------------------------------------------ kelly: Bayes fraction against the prior SD (log x)
sig_q, sig_h = A * SE / math.sqrt(3), A * SE
grid = sorted({rd(10 ** (k * math.log10(50) / 60), 6) for k in range(61)} | {rd(100 * sig_q, 6), rd(100 * sig_h, 6), 10.0})
quad = [rd(C.weight(g / 100) * FHAT, 5) for g in grid]
exact = [rd(C.kelly_exact(C.post(C.weight(g / 100))[0]), 5) for g in grid]
kelly = {
    "alt": "TAIEX's Bayes Kelly fraction against the prior standard deviation of the annual mean, 1 to 50 points on a "
           "log axis: the quadratic rule c times 4.28 and the exact fraction on shifted returns rise toward 4.28 and "
           "4.14; quarter Kelly needs 2.25 points, half Kelly 3.89, and 10 points gives 3.72 (exact 3.62)",
    "height": 320,
    "x": {"type": "log", "fmt": "n2", "tfmt": "n0", "label": "Prior SD of the annual mean, A × sigma0 (points, log scale)",
          "tipLabel": "A × sigma0 = ", "min": 1, "max": 50, "ticks": [1, 2, 5, 10, 20, 50], "values": grid},
    "y": {"type": "lin", "fmt": "n2", "tfmt": "n0", "label": "Kelly fraction (leverage)", "min": 0, "max": 5,
          "ticks": [0, 1, 2, 3, 4, 5]},
    "series": [
        {"name": "Quadratic: c × 4.28, (24.5)", "color": "1", "y": quad},
        {"name": "Exact: root of (4.5) on shifted returns", "color": "2", "dash": True, "y": exact},
    ],
    "ann": [
        {"type": "hline", "y": rd(FHAT, 5), "dash": True, "label": "plug-in 4.28; exact 4.14 below"},
        {"type": "hline", "y": rd(C.kelly_exact(RB), 5), "dash": True},
        {"type": "vline", "x": rd(100 * sig_q, 6), "dash": True, "label": "quarter Kelly", "dy": 230},
        {"type": "vline", "x": rd(100 * sig_h, 6), "dash": True, "label": "half Kelly", "dy": 216},
        {"type": "vline", "x": 10.0, "dash": True, "label": "10 points", "dy": 202},
    ],
}
i_q, i_h, i_10 = grid.index(rd(100 * sig_q, 6)), grid.index(rd(100 * sig_h, 6)), grid.index(10.0)
assert [f"{quad[i]:.2f}" for i in (i_q, i_h, i_10)] == ["1.07", "2.14", "3.72"]
assert [f"{exact[i]:.2f}" for i in (i_h, i_10)] == ["2.11", "3.62"]
assert all(e < q for e, q in zip(exact, quad))
write("lm24-kelly", kelly)

# ------------------------------------------------------------------ posterior: the widget's initial chart and inputs
c10 = C.weight(0.10)
pm10, psd10 = C.post(c10)
xw = [rd(-0.20 + 0.0025 * k, 4) for k in range(241)]
posterior = {
    "alt": "Prior, likelihood and posterior of TAIEX's annual mean return for a prior centred at 0 with standard "
           "deviation 10 points: the posterior sits at 13.4%, between the prior and the sample's 15.38%, closer to "
           "the data",
    "height": 300,
    "x": {"type": "num", "fmt": "pct2", "tfmt": "pct0", "label": "Annual mean return (TAIEX total-return index)", "tipLabel": "",
          "min": -0.20, "max": 0.40, "ticks": [-0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4], "values": xw},
    "y": {"type": "lin", "fmt": "n4", "tfmt": "n2", "label": "Density per percentage point", "min": 0, "max": 0.14,
          "ticks": [0, 0.04, 0.08, 0.12]},
    "series": [
        {"name": "Prior", "color": "3", "dash": True, "y": [dens(x, 0.0, 0.10) for x in xw]},
        {"name": "Likelihood (unit area)", "color": "2", "y": [dens(x, A * RB, se_a) for x in xw]},
        {"name": "Posterior", "color": "1", "y": [dens(x, A * pm10, A * psd10) for x in xw]},
    ],
    "ann": [{"type": "vline", "x": rd(A * pm10, 6), "dash": True, "label": f"posterior mean {100 * A * pm10:.1f}%"}],
    "widget": {"ARbar": rd(A * RB, 8), "vol": rd(VOL, 8), "years": rd(C.YEARS, 6), "fhat": rd(FHAT, 6),
               "z975": rd(C.Z975, 7), "init": {"s0": 10, "years": rd(C.YEARS, 6), "mu0": 0}},
}
assert f"{100 * A * pm10:.1f}" == "13.4"
assert abs(rd(A * RB, 8) / rd(VOL, 8) ** 2 - rd(FHAT, 6)) < 1e-5   # the widget's fhat = A Rbar / (A s^2)
write("lm24-posterior", posterior)
