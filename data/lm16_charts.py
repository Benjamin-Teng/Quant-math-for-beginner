"""Chart specs for LM16 (src/data/lm16-*.json), computed from the repaired sector closes.

Run:  uv run python data/lm16_charts.py      (after data/vol2_series.py; data/lm16_numbers.py checks the text)

Inputs: data/processed/vol2_closes.parquet, loaded by data/lm10_series.py's u28(): the U28 sample, closes 2008-12-01
.. 2026-10-08, T = 4,382 simple price returns, moments with divisor T, the guard 1e-12 at every edge (as
data/lm16_numbers.py). Writes:
  lm16-nextday     the TAIEX price index (U28 dates): mean R_{t+1} and mean |R_{t+1}| by bin of R_t;
  lm16-contours    the pair's centred returns with the normal model's contours d^2 = 1, 4, 9;
  lm16-chisq-pair  days with d_t^2 > k^2, k = 1..5, against the normal model (log scale);
  lm16-chisq-s5    S5's days above the chi-square(5) quantiles at 50%, 90%, 99%, 99.9% (x = -log10(1 - level));
  lm16-exceed      exceedance correlations of the pair, k = 0, 0.25, .., 2, and the normal benchmark (step 0.05);
  lm16-widget      the widget exceed's initial chart (joint falls, rho = 0.5749) and, in its "widget" block, the
                   model grid (joint falls of a standard normal pair, rho = 0, 0.01, .., 0.95 by k = 0, 0.05, .., 2.5,
                   by Gauss-Legendre as in data/lm16_numbers.py), the one-variable conditional variances and the
                   pair's data for the four events.
"""
import json
import math
import sys
from itertools import pairwise
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from scipy import special, stats
from scipy.linalg import solve_triangular

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lm10_series import u28

Vec = NDArray[np.float64]
OUT = Path(__file__).resolve().parents[1] / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)
EPS = 1e-12
S5 = ["Semiconductor", "FinancialInsurance", "Food", "Plastics", "ShippingTransportation"]


def write(name: str, spec: dict) -> None:
    (OUT / f"{name}.json").write_text(json.dumps(spec, ensure_ascii=False, separators=(",", ":"), allow_nan=False),
                                      encoding="utf-8", newline="\n")
    print("wrote", f"src/data/{name}.json")


def r(v: float, n: int) -> float:
    return round(float(v), n)


def corr(u: Vec, v: Vec) -> float:
    uc, vc = u - u.mean(), v - v.mean()
    return float(uc @ vc / math.sqrt(float((uc @ uc) * (vc @ vc))))


def mahal(x: Vec) -> Vec:
    xc = x - x.mean(axis=0)
    lo = np.linalg.cholesky(xc.T @ xc / x.shape[0])
    z = solve_triangular(lo, xc.T, lower=True)
    return (z**2).sum(axis=0)


smp = u28()
X, RT, dates = smp.X, np.asarray(smp.taiex, dtype=np.float64), smp.dates
T = X.shape[0]
assert T == 4382
col = {c: i for i, c in enumerate(smp.names)}
x1, x2 = X[:, col["Semiconductor"]], X[:, col["FinancialInsurance"]]
m1, m2, s1, s2 = float(x1.mean()), float(x2.mean()), float(x1.std()), float(x2.std())
rho = float(((x1 - m1) * (x2 - m2)).mean()) / (s1 * s2)
i7 = dates.index("2025-04-07")

# ------------------------------------------------------------------ nextday: the TAIEX price index today and tomorrow
a_, b_ = RT[:-1], RT[1:]
edges = [-np.inf, -0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03, np.inf]
bx, bm, ba, bn = [], [], [], []
for lo, hi in pairwise(edges):
    m_ = (a_ > lo + EPS) & (a_ <= hi + EPS)
    bn.append(int(m_.sum()))
    bx.append(r(100 * a_[m_].mean(), 4))
    bm.append(r(100 * b_[m_].mean(), 4))
    ba.append(r(100 * np.abs(b_[m_]).mean(), 4))
assert bn == [60, 95, 389, 1433, 1770, 483, 112, 39], bn
nextday = {
    "alt": "TAIEX price index on U28 dates: by bin of today's return, the mean of tomorrow's return stays near zero "
    "while the mean of tomorrow's absolute return forms a V, high after large moves of either sign",
    "height": 260,
    "x": {"type": "num", "fmt": "n2", "tfmt": "n0", "label": "Today's return, mean of its bin (%)",
          "tipLabel": "Today, bin mean (%): ", "min": -4.5, "max": 4.5, "ticks": [-4, -3, -2, -1, 0, 1, 2, 3, 4]},
    "y": {"type": "lin", "fmt": "n4", "tfmt": "n1", "label": "Tomorrow (%)", "min": -0.5, "max": 2.5,
          "ticks": [-0.5, 0, 0.5, 1, 1.5, 2, 2.5]},
    "series": [{"name": "Mean of tomorrow's return", "color": "1", "x": bx, "y": bm},
               {"name": "Mean of tomorrow's absolute return", "color": "2", "x": bx, "y": ba}],
    "ann": [{"type": "hline", "y": r(100 * np.abs(b_).mean(), 4), "dash": True, "label": "all days: 0.79%"}],
}
write("lm16-nextday", nextday)

# ------------------------------------------------------------------ contours: the pair with the model's ellipses
xp = np.column_stack([x1, x2])
xpc = 100 * (xp - xp.mean(axis=0))
sig = xpc.T @ xpc / T
d2 = mahal(xp)
cov_e = [[r(sig[0, 0], 6), r(sig[0, 1], 6)], [r(sig[1, 0], 6), r(sig[1, 1], 6)]]
L2 = np.linalg.cholesky(np.array(cov_e))
rings = []
for k in (1, 2, 3):   # dots about 5 px apart on screen: 40 per unit of k
    tt = np.linspace(0.0, 2 * math.pi, 40 * k, endpoint=False)
    rings.append((L2 @ (k * np.vstack([np.cos(tt), np.sin(tt)]))).T)
ring = np.vstack(rings)
assert np.allclose(np.einsum("ij,jk,ik->i", ring, np.linalg.inv(np.array(cov_e)), ring),
                   np.concatenate([np.full(40 * k, float(k * k)) for k in (1, 2, 3)]))
contours = {
    "type": "scatter", "equal": True,
    "alt": "Centred daily returns of Semiconductor against FinancialInsurance, 4,382 days, with the normal model's "
    "probability contours at 1, 2 and 3 standard units holding 39.35%, 86.47% and 98.89%; 7 April 2025 lies far "
    "outside",
    "height": 400,
    "x": {"label": "Semiconductor, centred (% a day)", "fmt": "n2", "tfmt": "n0", "name": "Semiconductor",
          "min": -11, "max": 11},
    "y": {"label": "FinancialInsurance, centred (% a day)", "fmt": "n2", "tfmt": "n0", "name": "FinancialInsurance",
          "min": -11, "max": 9},
    # the contours again as a dotted series drawn after the data points: the chart kit draws ellipses under the
    # points, which hide the two inner contours in the dense centre
    "series": [{"name": "Daily returns, centred", "color": "1", "r": 1.3,
                "x": [r(v, 2) for v in xpc[:, 0]], "y": [r(v, 2) for v in xpc[:, 1]]},
               {"name": "Normal model's contours", "color": "2", "r": 1.6,
                "x": [r(v, 3) for v in ring[:, 0]], "y": [r(v, 3) for v in ring[:, 1]]}],
    "ellipses": [{"center": [0, 0], "cov": cov_e, "scale": k, "color": "2",
                  "label": f"{100 * (1 - math.exp(-k * k / 2)):.2f}% inside"} for k in (1, 2, 3)],
    "points": [{"at": [r(xpc[i7, 0], 3), r(xpc[i7, 1], 3)], "label": "7 Apr 2025", "color": "2", "dx": 8, "dy": -6}],
}
assert [e["label"] for e in contours["ellipses"]] == ["39.35% inside", "86.47% inside", "98.89% inside"]
write("lm16-contours", contours)

# ------------------------------------------------------------------ chisq: the pair and S5 against the normal model


def outside(d: Vec, c: float) -> int:
    return int((~(d <= c + EPS)).sum())


ks = [1, 2, 3, 4, 5]
pair_model = [T * math.exp(-k * k / 2) for k in ks]
pair_data = [outside(d2, k * k) for k in ks]
assert pair_data == [1921, 528, 177, 61, 25]
log_ticks = [0.01, 0.1, 1, 10, 100, 1000, 10000]
chisq_pair = {
    "alt": "The pair: days outside the normal model's contours at 1 to 5 standard units, data against the model's "
    "expected days, on a log scale; the data exceed the model from 3 units on",
    "height": 220,
    "x": {"type": "num", "fmt": "n0", "label": "Contour d = k, k standard units", "tipLabel": "k = ", "min": 1,
          "max": 5, "ticks": ks},
    "y": {"type": "log", "fmt": "num", "label": "Days with d² above k² (log scale)", "min": 0.01, "max": 10000,
          "ticks": log_ticks},
    "series": [{"name": "U28 days", "color": "1", "fmt": "n0", "x": ks, "y": pair_data},
               {"name": "Normal model, expected days", "color": "2", "dash": True, "fmt": "sig4", "x": ks,
                "y": [r(v, 4) for v in pair_model]}],
}
write("lm16-chisq-pair", chisq_pair)
d25 = mahal(X[:, [col[c] for c in S5]])
levels = [0.5, 0.9, 0.99, 0.999]
lx = [r(-math.log10(1 - q), 6) for q in levels]
qs = [float(stats.chi2.ppf(q, 5)) for q in levels]
s5_data = [outside(d25, c) for c in qs]
assert s5_data == [1411, 613, 291, 184]
chisq_s5 = {
    "alt": "S5: days above the chi-square quantiles with 5 degrees of freedom at levels 50%, 90%, 99% and 99.9%, "
    "data against the normal model on a log scale; above 90% the data hold far more days",
    "height": 220,
    "x": {"type": "num", "fmt": "n2", "label": "Level of the chi-square quantile, 5 degrees of freedom",
          "tipLabel": "-log10(1 - level) = ", "min": 0.2, "max": 3.1, "ticks": lx,
          "tickLabels": ["50%", "90%", "99%", "99.9%"]},
    "y": {"type": "log", "fmt": "num", "label": "Days with d² above the quantile (log scale)", "min": 1,
          "max": 10000, "ticks": [1, 10, 100, 1000, 10000]},
    "series": [{"name": "U28 days", "color": "1", "fmt": "n0", "x": lx, "y": s5_data},
               {"name": "Normal model, expected days", "color": "2", "dash": True, "fmt": "sig4", "x": lx,
                "y": [r(T * (1 - q), 4) for q in levels]}],
}
write("lm16-chisq-s5", chisq_s5)

# ------------------------------------------------------------------ the normal benchmark: joint falls of a standard pair
GL_X, GL_W = np.polynomial.legendre.leggauss(600)


def joint_low(rs: Vec, k: float) -> tuple[Vec, Vec]:
    """Probability and correlation of a standard normal pair (correlations rs), given both <= -k."""
    c, lo = -k, -14.0
    x = 0.5 * (c - lo) * GL_X + 0.5 * (c + lo)
    w = 0.5 * (c - lo) * GL_W * np.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)
    r_ = rs[:, None]
    sd = np.sqrt(1 - r_ * r_)
    a = (c - r_ * x) / sd
    big_phi, small_phi = special.ndtr(a), np.exp(-0.5 * a * a) / math.sqrt(2 * math.pi)
    p1 = r_ * x * big_phi - sd * small_phi
    p2 = (r_ * r_ * x * x + sd * sd) * big_phi - sd * (r_ * x + c) * small_phi
    p, ex, ey = big_phi @ w, (x * big_phi) @ w, p1 @ w
    exx, eyy, exy = (x * x * big_phi) @ w, p2 @ w, (x * p1) @ w
    vx, vy = exx / p - (ex / p) ** 2, eyy / p - (ey / p) ** 2
    return p, (exy / p - ex * ey / p**2) / np.sqrt(vx * vy)


lo1, lo2 = (x1 - m1) / s1, (x2 - m2) / s2


def data_corr(sel: NDArray[np.bool_]) -> tuple[int, float | None]:
    n = int(sel.sum())
    return n, (r(corr(x1[sel], x2[sel]), 6) if n >= 30 else None)


# ------------------------------------------------------------------ exceed: exceedance correlations (X8)
kq = [0.25 * j for j in range(9)]
xs_d = [-k for k in reversed(kq)] + kq[1:]
falls = {k: data_corr((lo1 <= -k + EPS) & (lo2 <= -k + EPS)) for k in kq}
rises = {k: data_corr((lo1 >= k - EPS) & (lo2 >= k - EPS)) for k in kq}
assert all(v[1] is not None for v in [*falls.values(), *rises.values()]), "a point has fewer than 30 days"
y_falls = [falls[k][1] for k in reversed(kq)] + [None] * 8
y_rises = [None] * 8 + [rises[k][1] for k in kq]
kf = [0.05 * j for j in range(41)]
bench = [float(joint_low(np.array([rho]), k)[1][0]) for k in kf]
xs_m = [r(-k, 2) for k in reversed(kf)] + [r(k, 2) for k in kf[1:]]
ys_m = [r(v, 6) for v in reversed(bench)] + [r(v, 6) for v in bench[1:]]
exceed = {
    "alt": "Exceedance correlations of Semiconductor and FinancialInsurance: on joint falls of k standard deviations "
    "(left) and joint rises (right), against the normal benchmark, which falls from 0.332 at k = 0 to 0.156 at k = 2; "
    "the data stay near or above 0.43",
    "height": 280,
    "x": {"type": "num", "fmt": "n2", "tfmt": "n1", "label": "k standard deviations: joint falls at −k, joint rises at +k",
          "tipLabel": "", "min": -2, "max": 2, "ticks": [-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2]},
    "y": {"type": "lin", "fmt": "n3", "tfmt": "n1", "label": "Correlation on the days of the event", "min": 0,
          "max": 0.8, "ticks": [0, 0.2, 0.4, 0.6, 0.8]},
    "series": [{"name": "U28 pair, joint falls", "color": "1", "x": xs_d, "y": y_falls},
               {"name": "U28 pair, joint rises", "color": "3", "x": xs_d, "y": y_rises},
               {"name": "Normal model, same correlation", "color": "2", "dash": True, "x": xs_m, "y": ys_m}],
    "ann": [{"type": "hline", "y": r(rho, 6), "dash": True, "label": "full sample: 0.5749"}],
}
assert f"{bench[0]:.3f}" == "0.332" and f"{bench[20]:.3f}" == "0.229" and f"{bench[40]:.3f}" == "0.156"
write("lm16-exceed", exceed)

# ------------------------------------------------------------------ widget: the model grid and the pair's data
KG = [0.05 * j for j in range(51)]
RG = np.asarray(np.arange(96) * 0.01, dtype=np.float64)
grid_c, grid_p = [], []
for k in KG:
    p_, c_ = joint_low(RG, k)
    grid_c.append([r(v, 7) for v in c_])
    grid_p.append([r(v, 9) for v in p_])


def v_two(k: float) -> float:
    return 1 + k * float(stats.norm.pdf(k)) / float(stats.norm.sf(k))


def v_low(k: float) -> float:
    ell = float(stats.norm.pdf(k)) / float(stats.norm.cdf(-k))
    return 1 + k * ell - ell * ell


events = {
    "fall2": lambda k: (lo1 <= -k + EPS) & (lo2 <= -k + EPS),
    "rise2": lambda k: (lo1 >= k - EPS) & (lo2 >= k - EPS),
    "two": lambda k: np.abs(lo1) >= k - EPS,
    "fall1": lambda k: lo1 <= -k + EPS,
}
data = {}
for ev, fn in events.items():
    dc = [data_corr(fn(k)) for k in KG]
    data[ev] = {"days": [d[0] for d in dc], "corr": [d[1] for d in dc]}


def lag4(yg: Vec, x: float, h: float = 0.01) -> float:
    """The widget's interpolation: four-point Lagrange through the four nearest nodes, clamped at the ends."""
    i0 = min(max(math.floor(x / h + 1e-9) - 1, 0), len(yg) - 4)
    t = x / h - i0
    out = 0.0
    for a in range(4):
        la = 1.0
        for b in range(4):
            if b != a:
                la *= (t - b) / (a - b)
        out += la * yg[i0 + a]
    return out


# the stored (rounded) grid reproduces the widget's initial state and the error bound of the text
kI = 40
c_init = lag4(np.array(grid_c[kI]), 0.5749)
p_init = lag4(np.array(grid_p[kI]), 0.5749)
assert f"{c_init:.3f}" == "0.156" and f"{p_init:.4f}" == "0.0051" and f"{T * p_init:.1f}" == "22.4"
assert data["fall2"]["days"][kI] == 44 and f"{data['fall2']['corr'][kI]:.3f}" == "0.669"
rfine = np.asarray(np.arange(9501) * 1e-4, dtype=np.float64)
err_c = err_p = 0.0
for j in (0, 10, 20, 30, 40, 50):
    pf, cf = joint_low(rfine, KG[j])
    gc, gp = np.array(grid_c[j]), np.array(grid_p[j])
    err_c = max(err_c, max(abs(lag4(gc, float(x)) - float(v)) for x, v in zip(rfine[::7], cf[::7], strict=True)))
    err_p = max(err_p, max(abs(lag4(gp, float(x)) - float(v)) for x, v in zip(rfine[::7], pf[::7], strict=True)))
assert err_c < 1e-5 and T * err_p < 0.01, (err_c, err_p)
model_init = [r(lag4(np.array(grid_c[j]), 0.5749), 6) for j in range(51)]
widget = {
    "alt": "The normal model's correlation on joint falls of k standard deviations at correlation 0.5749, falling "
    "from 0.33 at k = 0 to 0.156 at k = 2, against the pair's 0.669 on 44 days at k = 2",
    "height": 280,
    "x": {"type": "num", "fmt": "n2", "tfmt": "n1", "label": "k standard deviations", "tipLabel": "k = ",
          "min": 0, "max": 2.5, "ticks": [0, 0.5, 1, 1.5, 2, 2.5]},
    "y": {"type": "lin", "fmt": "n3", "tfmt": "n1", "label": "Correlation given the event", "min": 0, "max": 1,
          "ticks": [0, 0.2, 0.4, 0.6, 0.8, 1]},
    "series": [{"name": "Normal model", "color": "2", "dash": True, "x": [r(k, 2) for k in KG], "y": model_init},
               {"name": "U28 pair (at least 30 days)", "color": "1", "x": [r(k, 2) for k in KG],
                "y": data["fall2"]["corr"]}],
    "ann": [{"type": "vline", "x": 2, "label": "k = 2"},
            {"type": "hline", "y": r(rho, 6), "dash": True, "label": "full sample: 0.5749"}],
    "widget": {"T": T, "rhoHat": r(rho, 10), "rhoStep": 0.01, "kStep": 0.05, "corr": grid_c, "prob": grid_p,
               "vtwo": [r(v_two(k), 8) for k in KG], "vlow": [r(v_low(k), 8) for k in KG], "data": data},
}
write("lm16-widget", widget)
print(f"exceed benchmark at k = 0, 1, 2: {bench[0]:.4f}, {bench[20]:.4f}, {bench[40]:.4f}; widget grid errors "
      f"{err_c:.2e} (correlation), {err_p:.2e} (probability); initial state {c_init:.3f}, {p_init:.4f}, {T * p_init:.1f}")
