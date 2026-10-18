"""LM16 anchors (Joint Distributions and Dependence): every number the Stage 1 brief quotes.

Reads Volume II's U28 sample as data/lm10_series.py does: data/processed/vol2_closes.parquet (built and repaired by
data/vol2_series.py, which must run first), the 28 TWSE sector indices other than the aggregates Electronic and
ChemicalBiotechnologyMedicalCare, and the TAIEX price index on the same dates, closes 2008-12-01 -> 2026-10-08.
LM16 does not read TR23 (plans/vol-3.md, "Data"). Writes nothing.

Conventions: T = 4,382 simple price returns R_t = P_t / P_{t-1} - 1 between consecutive rows, from 2008-12-02;
moments divide by T; years = calendar days / 365.25; A = T / years. Counts against a threshold use the guard
(<= -x + 1e-12, >= x - 1e-12; "inside" d^2 <= k^2 + 1e-12) and the counts on returns are recounted exactly with
Fraction on the two-decimal closes. LM16 draws no random numbers (no seed). A value computed "from printed inputs"
uses the inputs at the precision the brief prints them.

Revised 2026-10-18 after the fresh check: A16-46 (the widget's four-point interpolation, error over the whole slider
range) and A16-67 (Problem 7 from the printed mean -1.37) changed; A16-79 (eigenvalues of the pair's covariance
matrix by (11.2)) and A16-80 (E10 from unrounded inputs) are new.

Run from the repository root (an optional first argument gives the repository root):
    PYTHONUTF8=1 uv run python data/vol3_anchors_lm16.py
Prints one line per anchor, "A16-NN <value>", in ID order.
"""
import json
import math
import sys
from datetime import date
from fractions import Fraction
from itertools import pairwise
from pathlib import Path

import numpy as np
import polars as pl
from numpy.typing import NDArray
from scipy import integrate, special, stats
from scipy.linalg import solve_triangular

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
HERE = ROOT / "data"
PROC = HERE / "processed"
AGGREGATES = ("Electronic", "ChemicalBiotechnologyMedicalCare")
FIRST, LAST = "2008-12-01", "2026-10-08"
S5 = ["Semiconductor", "FinancialInsurance", "Food", "Plastics", "ShippingTransportation"]
EPS = 1e-12
OUT: dict[str, str] = {}
Vec = NDArray[np.float64]


def put(name: str, *vals: object) -> None:
    assert name not in OUT, name
    OUT[name] = "; ".join(str(v) for v in vals)


def g(x: float, d: int = 10) -> str:
    """A float with d significant digits (the unrounded value the anchors table quotes)."""
    return f"{x:.{d}g}"


def corr(u: Vec, v: Vec) -> float:
    uc, vc = u - u.mean(), v - v.mean()
    return float(uc @ vc / math.sqrt(float((uc @ uc) * (vc @ vc))))


def cov0(x: Vec) -> Vec:
    xc = x - x.mean(axis=0)
    return xc.T @ xc / x.shape[0]


def mahal(x: Vec) -> Vec:
    """d_t^2 of every row of x with the sample's means and divisor-T covariance matrix, by Cholesky ((12.9))."""
    lo = np.linalg.cholesky(cov0(x))
    z = solve_triangular(lo, (x - x.mean(axis=0)).T, lower=True)
    return (z**2).sum(axis=0)


def exact_returns(p: list[float]) -> list[Fraction]:
    q = [Fraction(str(v)) for v in p]
    return [b / a - 1 for a, b in pairwise(q)]


# ------------------------------------------------------------------ U28 sample
cl = pl.read_parquet(PROC / "vol2_closes.parquet").sort("date")
names = [c for c in cl.columns if c not in ("date", "TAIEX") and c not in AGGREGATES]
assert len(names) == 28
smp = cl.filter(pl.col("date").is_between(pl.lit(FIRST), pl.lit(LAST)))
assert smp.select([*names, "TAIEX"]).null_count().sum_horizontal()[0] == 0
cd: list[str] = smp["date"].to_list()
P = np.asarray(smp.select(names).to_numpy(), dtype=np.float64)
PT = np.asarray(smp["TAIEX"].to_numpy(), dtype=np.float64)
X = P[1:] / P[:-1] - 1
RT = PT[1:] / PT[:-1] - 1
dates = cd[1:]
T = X.shape[0]
days = (date.fromisoformat(cd[-1]) - date.fromisoformat(cd[0])).days
years = days / 365.25
A = T / years
col = {c: i for i, c in enumerate(names)}
x1, x2 = X[:, col["Semiconductor"]], X[:, col["FinancialInsurance"]]
i7 = dates.index("2025-04-07")

put("T", T, dates[0], dates[-1])
put("years", days, g(years, 12))
put("A", g(A, 12))

rep = json.loads((PROC / "vol2_repairs.json").read_text(encoding="utf-8"))["repairs"]
inside = [r_ for r_ in rep if r_["series"] in names and FIRST <= r_["date"] <= LAST]
put("repairs", len(inside), len({r_["date"] for r_ in inside}))
key_dates = ["2025-04-07", "2025-04-08", "2025-04-09", "2025-04-10", "2024-08-05", "2009-05-05"]
touched = {(r_["date"]) for r_ in rep if r_["series"] in [*names, "TAIEX"]}
hits = sum(1 for d_ in key_dates for dd in (d_, cd[cd.index(d_) - 1]) if dd in touched)
put("repairs_key", hits)
put("freeplan", "4,307 (printed in build/make_lab12.py:167)")

# ------------------------------------------------------------------ the pair: moments
m1, m2 = float(x1.mean()), float(x2.mean())
s1, s2 = float(x1.std()), float(x2.std())
c12 = float(((x1 - m1) * (x2 - m2)).mean())
rho = c12 / (s1 * s2)
put("rho", g(rho))
put("means", g(100 * m1), g(100 * m2))
put("sds", g(100 * s1), g(100 * s2))

# LM10's three days, from its printed two-decimal returns (lm10.md:106-108)
r1p = np.array([-9.95, -3.99, -4.47])
r2p = np.array([-9.89, 0.53, -5.61])
put("rho3", g(corr(r1p, r2p)))
put("rho3u", g(corr(x1[i7:i7 + 3], x2[i7:i7 + 3])))
put("apr7", g(100 * x1[i7]), g(100 * x2[i7]))

# ------------------------------------------------------------------ pair d^2 and the circle of radius 3
XP = np.column_stack([x1, x2])
d2 = mahal(XP)
assert abs(d2.mean() - 2) < 1e-9
put("d2apr7", g(float(d2[i7])), int((d2 > d2[i7]).sum()) + 1)


def outside(d: Vec, c: float) -> int:
    return int((~(d <= c + EPS)).sum())


n9 = outside(d2, 9.0)
put("out9", n9)
p9 = math.exp(-4.5)
put("p9", g(p9))
put("exp9", g(T * p9), g(T * p9 * (1 - p9)), g(math.sqrt(T * p9 * (1 - p9))))

# ------------------------------------------------------------------ X2: joint pmf of the two sectors' bins


def bins(r: Vec) -> NDArray[np.int64]:
    return np.where(r <= -0.01 + EPS, 0, np.where(r >= 0.01 - EPS, 2, 1))


b1, b2 = bins(x1), bins(x2)
tab = np.zeros((3, 3), dtype=int)
np.add.at(tab, (b1, b2), 1)
e1 = exact_returns(smp["Semiconductor"].to_list())
e2 = exact_returns(smp["FinancialInsurance"].to_list())
one = Fraction(1, 100)
tabF = np.zeros((3, 3), dtype=int)
for u_, v_ in zip(e1, e2):
    tabF[0 if u_ <= -one else (2 if u_ >= one else 1), 0 if v_ <= -one else (2 if v_ >= one else 1)] += 1
assert (tab == tabF).all()
put("ties1", sum(1 for q_ in [*e1, *e2] if q_ in (one, -one)))
put("X2", " / ".join(", ".join(str(int(c)) for c in row) for row in tab))
rows, cols = tab.sum(axis=1), tab.sum(axis=0)
put("X2m", ", ".join(str(int(c)) for c in rows), ", ".join(str(int(c)) for c in cols))
put("E1joint", g(347 / T), g(rows[0] / T), g(cols[0] / T), g(rows[0] / T * cols[0] / T),
    g((347 / T) / (rows[0] / T * cols[0] / T)), g(0.0792 / 0.0241))
put("E1cond", g(347 / 859), g(20 / 1004))
put("KC2", g(20 / 538))
put("P1", g(347 / 538), g(347 / T))

# ------------------------------------------------------------------ E2: f(x, y) = x + y on the unit square (exact)


def sq(a: int, b: int, top: Fraction = Fraction(1)) -> Fraction:
    """Integral of x^a y^b over [0, top]^2."""
    return top ** (a + 1) / (a + 1) * top ** (b + 1) / (b + 1)


EX = sq(2, 0) + sq(1, 1)
EX2 = sq(3, 0) + sq(2, 1)
EXY = sq(2, 1) + sq(1, 2)
VX = EX2 - EX**2
CXY = EXY - EX * EX
half = Fraction(1, 2)
put("E2", sq(1, 0) + sq(0, 1), EX, EX2, VX, EXY, CXY, g(float(CXY)), CXY / VX, g(float(CXY / VX)),
    sq(1, 0, half) + sq(0, 1, half), Fraction(2, 3), Fraction(5, 9))
# E[Y | X = x] = (x/2 + 1/3) / (x + 1/2) = (3x + 2) / (6x + 3): checked at x = 0 and x = 1
assert (Fraction(0) / 2 + Fraction(1, 3)) / (0 + half) == Fraction(2, 3)
assert (Fraction(1) / 2 + Fraction(1, 3)) / (1 + half) == Fraction(5, 9)

# E3: X uniform on {-1, 0, 1}, Y = X^2
xs = [Fraction(-1), Fraction(0), Fraction(1)]
put("E3", sum(x**3 for x in xs) / 3 - sum(xs, Fraction(0)) / 3 * sum(x**2 for x in xs) / 3, Fraction(1, 3))

# ------------------------------------------------------------------ E4, X3: TAIEX price index today and tomorrow
a_, b_ = RT[:-1], RT[1:]
put("E4corr", T - 1, g(corr(a_, b_)), g(corr(np.abs(a_), np.abs(b_))))
big = np.abs(a_) >= 0.02 - EPS
eT = exact_returns(smp["TAIEX"].to_list())
assert int(big.sum()) == sum(1 for q_ in eT[:-1] if abs(q_) >= Fraction(2, 100))
put("E4big", int(big.sum()), g(100 * float(np.abs(b_[big]).mean())), g(100 * float(np.abs(b_[~big]).mean())),
    g(100 * float(np.abs(b_).mean())))
edges = [-np.inf, -0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03, np.inf]
cnt, mx, my, mabs = [], [], [], []
for lo, hi in pairwise(edges):
    m_ = (a_ > lo + EPS) & (a_ <= hi + EPS)
    lo_f = None if lo == -np.inf else Fraction(str(lo))
    hi_f = None if hi == np.inf else Fraction(str(hi))
    ex = sum(1 for q_ in eT[:-1] if (lo_f is None or q_ > lo_f) and (hi_f is None or q_ <= hi_f))
    assert ex == int(m_.sum())
    cnt.append(str(int(m_.sum())))
    mx.append(f"{100 * a_[m_].mean():.4f}")
    my.append(f"{100 * b_[m_].mean():.4f}")
    mabs.append(f"{100 * np.abs(b_[m_]).mean():.4f}")
put("X3", ", ".join(cnt), ", ".join(mx), ", ".join(my), ", ".join(mabs))

# ------------------------------------------------------------------ E5: LM10's printed annualized matrix (%^2)
a11, a12, a22 = 570.34, 261.83, 363.73
vp = 0.25 * a11 + 0.5 * a12 + 0.25 * a22
put("lm10S", "570.34; 261.83; 363.73 (printed in lm10.md:61)")
put("E5", g(vp), g(math.sqrt(vp)), g(0.5 * a11 + 0.5 * a12), g(a11 + a22 - 2 * a12), g(math.sqrt(a11 + a22 - 2 * a12)))

# ------------------------------------------------------------------ the sum of m independent days (log returns)
r = np.log1p(RT)
put("logmom", g(100 * float(r.mean())), g(100 * float(r.std())))
m = round(A)
put("m", m)
put("annual", g(m * 100 * float(r.mean())), g(math.sqrt(m) * 100 * float(r.std())),
    g(m * 0.05454), g(math.sqrt(m) * 1.1392))
fac = 1 + 2 * 0.04 * (m - 1) / m
put("P5", g(fac), g(math.sqrt(m) * 1.1392 * math.sqrt(fac)))
put("P5w", g(m * 1.1392), g(17.83 * fac), g(math.sqrt(m) * 1.1392 * fac))

# ------------------------------------------------------------------ X4, E6: law of total variance (divisor: the bin's days)
gm, gs = [], []
within = between = 0.0
for k_ in range(3):
    sel = b1 == k_
    w_ = float(sel.mean())
    gm.append(float(x2[sel].mean()))
    gs.append(float(x2[sel].std()))
    within += w_ * float(x2[sel].var())
    between += w_ * (float(x2[sel].mean()) - m2) ** 2
assert abs(within + between - float(x2.var())) < 1e-15
put("X4", ", ".join(g(100 * v, 8) for v in gm), ", ".join(g(100 * v, 8) for v in gs))
put("X4tot", g(1e4 * within), g(1e4 * between), g(1e4 * float(x2.var())), g(100 * between / float(x2.var())))
ng = np.array([859, 2519, 1004])
mgp = np.array([round(100 * v, 4) for v in gm])
sgp = np.array([round(100 * v, 4) for v in gs])
wg = ng / T
mean_p = float(wg @ mgp)
within_p = float(wg @ sgp**2)
between_p = float(wg @ (mgp - mean_p) ** 2)
put("X4printed", g(within_p), g(between_p), g(within_p + between_p), g(100 * between_p / (within_p + between_p)),
    g(mean_p))
put("rho2", g(rho**2))
put("eqw", g(float(mgp.mean())))

# P6: TAIEX price index tomorrow, grouped by today's |R_t| >= 2%
pg = float(big.mean())
gb, gn = b_[big], b_[~big]
put("P6", int(big.sum()), int((~big).sum()), g(100 * float(gb.mean())), g(100 * float(gn.mean())),
    g(100 * float(gb.std())), g(100 * float(gn.std())))
mb, mn = round(100 * float(gb.mean()), 4), round(100 * float(gn.mean()), 4)
sb, sn = round(100 * float(gb.std()), 4), round(100 * float(gn.std()), 4)
wb, wn = int(big.sum()) / (T - 1), int((~big).sum()) / (T - 1)
mp6 = wb * mb + wn * mn
w6 = wb * sb**2 + wn * sn**2
bt6 = wb * (mb - mp6) ** 2 + wn * (mn - mp6) ** 2
put("P6b", g(sb / sn), str(Fraction(str(mb)) / 2 + Fraction(str(mn)) / 2), g((mb + mn) / 2))
put("P6res", g(mp6), g(w6), g(bt6), g(w6 + bt6), g(100 * bt6 / (w6 + bt6)), g(100 * float(b_.mean())),
    g(1e4 * float(b_.var())))

# ------------------------------------------------------------------ E7: the normal pair given Semiconductor = -5%
M1, M2, S1, S2, RH = 0.0947, 0.0494, 1.5243, 1.2173, 0.5749     # printed inputs (% a day)
beta = RH * S2 / S1
csd = S2 * math.sqrt(1 - RH**2)
cm5 = M2 + beta * (-5 - M1)
put("E7", g(beta), g(cm5), g(csd), g((-3 - cm5) / csd), g(float(stats.norm.cdf((-3 - cm5) / csd))))
beta_u = c12 / s1**2
put("E7u", g(beta_u), g(100 * (m2 + beta_u * (-0.05 - m1))), g(100 * s2 * math.sqrt(1 - rho**2)))
sel5 = (x1 >= -0.055 - EPS) & (x1 <= -0.045 + EPS)
put("E7data", int(sel5.sum()), g(100 * float(x2[sel5].mean())), g(100 * float(x2[sel5].std())),
    int((x2[sel5] <= -0.03 + EPS).sum()))

# P7: Semiconductor = -3%. The mean is printed -1.37; z and both probabilities follow from that printed mean and the
# printed standard deviations 0.996 and 1.2173 (PITFALLS section 7).
cm3 = M2 + beta * (-3 - M1)
assert f"{cm3:.2f}" == "-1.37" and f"{csd:.3f}" == "0.996"
z7 = (-2 + 1.37) / 0.996
put("P7", g(cm3), g(z7), g(float(stats.norm.cdf(z7))), g(float(stats.norm.cdf((-2 + 1.37) / S2))),
    g(M2 + RH * (-3 - M1)))

# ------------------------------------------------------------------ contours and X6
put("X5", *(g(100 * (1 - math.exp(-k * k / 2))) for k in (1, 2, 3)),
    *(g(100 * float((d2 <= k * k + EPS).mean())) for k in (1, 2, 3)))
put("X5S", g(1e4 * s1**2, 7), g(1e4 * c12, 7), g(1e4 * s2**2, 7))
# Contour axes: (11.2) on X5's printed entries (%^2); semi-axes sqrt(lambda) at k = 1 (% a day), along q_1, q_2
tr2, det2 = 2.323354 + 1.481729, 2.323354 * 1.481729 - 1.066603**2
lam1 = tr2 / 2 + math.sqrt(tr2**2 / 4 - det2)
lam2 = tr2 / 2 - math.sqrt(tr2**2 / 4 - det2)
ev2 = np.linalg.eigvalsh(1e4 * cov0(np.column_stack([x1, x2])))
assert abs(ev2[1] - lam1) < 1e-5 and abs(ev2[0] - lam2) < 1e-5
put("axes", g(lam1), g(lam2), g(math.sqrt(lam1)), g(math.sqrt(lam2)))
put("X6pair", ", ".join(g(100 * math.exp(-k * k / 2), 6) for k in range(1, 6)),
    ", ".join(g(T * math.exp(-k * k / 2), 6) for k in range(1, 6)),
    ", ".join(str(outside(d2, k * k)) for k in range(1, 6)))
X5m = X[:, [col[c] for c in S5]]
d25 = mahal(X5m)
assert abs(d25.mean() - 5) < 1e-9
qs = (0.5, 0.9, 0.99, 0.999)
cs = [float(stats.chi2.ppf(q, 5)) for q in qs]
put("X6S5", ", ".join(g(c, 6) for c in cs), ", ".join(g(T * (1 - q), 6) for q in qs),
    ", ".join(str(outside(d25, c)) for c in cs))
put("E9", g(float(d25[i7])), int((d25 > d25[i7]).sum()) + 1, "89.30 (printed in lm12.md:483)")
sf89 = float(stats.chi2.sf(89.30, 5))
put("E9p", g(sf89, 6), g(1 / (sf89 * 245.48), 6))
d228 = mahal(X)
assert abs(d228.mean() - 28) < 1e-8
imax = int(np.argmax(d228))
put("KC6", g(float(d228[i7])), int((d228 > d228[i7]).sum()) + 1, g(float(d228[imax])), dates[imax])
_, q_ = np.linalg.eigh(cov0(X))
dev7 = X[i7] - X.mean(axis=0)
put("KC6b", g(float((q_[:, -1] @ dev7) ** 2 / (dev7 @ dev7))), g(100 * float(X[imax].min())),
    g(100 * float(X[imax].max())), g(100 * float(RT[imax])))
put("all28", int((X < 0).all(axis=1).sum()), int((X > 0).all(axis=1).sum()), "(printed in lm11.md:48)")
put("lm7", "21-22%; -0.06 (printed in lm07.md:418)")

# ------------------------------------------------------------------ crash correlation: model


def trunc(mu: float, sd: float, c: float) -> tuple[float, float, float]:
    """E[1{W<=c}], E[W 1{W<=c}], E[W^2 1{W<=c}] for W ~ N(mu, sd^2)."""
    a = (c - mu) / sd
    big_phi, small_phi = float(stats.norm.cdf(a)), float(stats.norm.pdf(a))
    return big_phi, mu * big_phi - sd * small_phi, (mu * mu + sd * sd) * big_phi - sd * (mu + c) * small_phi


def bvn_lower(r_: float, k: float) -> tuple[float, float]:
    """Probability and correlation of a standard normal pair with correlation r_, given both <= -k (numerical)."""
    c, sd = -k, math.sqrt(1 - r_ * r_)

    def mom(which: int) -> float:
        def f(x: float) -> float:
            p0, p1, p2 = trunc(r_ * x, sd, c)
            return float(stats.norm.pdf(x)) * (p0, x * p0, p1, x * x * p0, p2, x * p1)[which]

        return integrate.quad(f, -np.inf, c, epsabs=1e-13, epsrel=1e-11, limit=200)[0]

    p, ex, ey, exx, eyy, exy = (mom(w) for w in range(6))
    vx, vy = exx / p - (ex / p) ** 2, eyy / p - (ey / p) ** 2
    return p, (exy / p - ex * ey / p**2) / math.sqrt(vx * vy)


def v_two(k: float) -> float:
    """Var(Z | |Z| >= k)."""
    return 1 + k * float(stats.norm.pdf(k)) / float(stats.norm.sf(k))


def v_low(k: float) -> float:
    """Var(Z | Z <= -k) = 1 + k l - l^2, l = phi(k) / Phi(-k)."""
    ell = float(stats.norm.pdf(k)) / float(stats.norm.cdf(-k))
    return 1 + k * ell - ell * ell


def bgl(r_: float, v: float) -> float:
    """(16.10) with Var(X) = 1."""
    return r_ / math.sqrt(r_ * r_ + (1 - r_ * r_) / v)


assert abs(bvn_lower(rho, 0.0)[0] - (0.25 + math.asin(rho) / (2 * math.pi))) < 1e-10
mod = {k: bvn_lower(rho, k) for k in (0.0, 1.0, 2.0)}
put("X8model", *(g(mod[k][1]) for k in mod))
put("X8prob", *(f"{g(mod[k][0])} ({g(T * mod[k][0])})" for k in mod))

# ------------------------------------------------------------------ crash correlation: data (full-sample moments)
lo1, lo2 = (x1 - m1) / s1, (x2 - m2) / s2


def exceed(k: float, side: int) -> tuple[int, float]:
    sel = ((lo1 <= -k + EPS) & (lo2 <= -k + EPS)) if side < 0 else ((lo1 >= k - EPS) & (lo2 >= k - EPS))
    return int(sel.sum()), corr(x1[sel], x2[sel])


low = {k: exceed(k, -1) for k in (0.0, 1.0, 2.0)}
upp = {k: exceed(k, +1) for k in (0.0, 1.0, 2.0)}
put("X8low", *(f"{low[k][0]} {g(low[k][1])}" for k in low))
put("X8up", *(f"{upp[k][0]} {g(upp[k][1])}" for k in upp))
grid_k = [0.25 * j for j in range(9)]
assert min(min(exceed(k, -1)[0], exceed(k, +1)[0]) for k in grid_k) >= 30   # every plotted point has 30 days

two, fall, rise = [], [], []
for k in (1.0, 2.0, 2.5):
    s_two = np.abs(lo1) >= k - EPS
    s_fall, s_rise = lo1 <= -k + EPS, lo1 >= k - EPS
    two.append((int(s_two.sum()), corr(x1[s_two], x2[s_two]), bgl(rho, v_two(k))))
    fall.append((int(s_fall.sum()), corr(x1[s_fall], x2[s_fall]), bgl(rho, v_low(k))))
    rise.append((int(s_rise.sum()), corr(x1[s_rise], x2[s_rise])))
put("X9two", ", ".join(str(t[0]) for t in two), ", ".join(g(t[1]) for t in two), ", ".join(g(t[2]) for t in two))
put("X9fall", ", ".join(str(t[0]) for t in fall), ", ".join(g(t[1]) for t in fall), ", ".join(g(t[2]) for t in fall))
put("X9rise", ", ".join(str(t[0]) for t in rise), ", ".join(g(t[1]) for t in rise))
put("vtrunc", ", ".join(g(v_two(k)) for k in (1.0, 2.0, 2.5)), ", ".join(g(v_low(k)) for k in (1.0, 2.0, 2.5)))
put("ell2", g(float(stats.norm.pdf(2.0)) / float(stats.norm.cdf(-2.0))))

# E10: Semiconductor on 7-9 April 2025 in standard deviations, from printed inputs; then from unrounded returns and
# moments (9 April moves from -2.99 to -3.00, so the text keeps "from printed inputs")
put("E10", *(g((r_ - M1) / S1) for r_ in r1p))
put("E10u", *(g(float((x1[i7 + j] - m1) / s1)) for j in range(3)))
# P10 and KC7: (16.10) from printed inputs
put("P10", g(bgl(RH, 5.7464)), g(bgl(RH, 0.1143)))
put("KC7", g(bgl(RH, 2.5251)))

# ------------------------------------------------------------------ problems with constructed inputs
put("P4", g(math.sqrt(0.04 + 0.0225 - 2 * 0.5 * 0.2 * 0.15)), g(0.6 * 0.04 + 0.4 * 0.5 * 0.2 * 0.15),
    g(math.sqrt(0.36 * 0.04 + 2 * 0.24 * 0.015 + 0.16 * 0.0225)),
    g((0.6 * 0.04 + 0.4 * 0.015) / (0.2 * math.sqrt(0.36 * 0.04 + 2 * 0.24 * 0.015 + 0.16 * 0.0225))),
    g(math.sqrt((0.2 - 0.15) ** 2)), g(math.sqrt(0.04 + 0.0225)))
put("KC4", 4 + 9, g(4 / math.sqrt(4 * 13)))

# P8: 5 August 2024, from printed inputs (returns to two decimals; LM12's printed L, % a day)
i5 = dates.index("2024-08-05")
put("P8ret", g(100 * x1[i5]), g(100 * x2[i5]))
z1 = (-9.48 - M1) / 1.5243
z2 = (-6.93 - M2 - 0.6998 * z1) / 0.9960
put("P8", g(z1), g(z2), g(z1 * z1 + z2 * z2), g(float(d2[i5])))
put("P8p", g((z1 * z1 + z2 * z2) / 2), g(math.exp(-(z1 * z1 + z2 * z2) / 2), 6),
    g(T * math.exp(-(z1 * z1 + z2 * z2) / 2), 6))
put("Lp", "1.5243; 0.6998; 0.9960 (printed in lm12.md:441-442)")

# Python pitfall and Problem 12
put("py", repr(1 - float(stats.chi2.cdf(89.30, 5))), repr(sf89), g(float(stats.chi2.sf(9, 2))),
    g(T * float(stats.chi2.sf(9, 2))))

# ------------------------------------------------------------------ lab extension: the two price-limit regimes
reg = np.array([d_ <= "2015-05-29" for d_ in dates])
put("regimes", int(reg.sum()), int((~reg).sum()), g(corr(x1[reg], x2[reg])), g(corr(x1[~reg], x2[~reg])),
    int((~(d2[reg] <= 9 + EPS)).sum()), int((~(d2[~reg] <= 9 + EPS)).sum()))

# ------------------------------------------------------------------ widget: the rho grid (step 0.01) and its error
# The widget interpolates the joint-event grid in rho by four-point Lagrange (cubic) interpolation; k moves on the
# grid's own 0.05 steps. The error is measured over the whole slider range, rho = 0, 0.0001, ..., 0.95, at every k.
GL_X, GL_W = np.polynomial.legendre.leggauss(600)


def joint_low(rs: Vec, k: float) -> tuple[Vec, Vec]:
    """bvn_lower vectorized over rs: Gauss-Legendre on [-14, -k] (checked against quad below)."""
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


for r_chk, k_chk in ((0.57, 2.0), (rho, 1.0), (0.95, 2.5), (0.0, 0.0)):
    pv, cv = joint_low(np.array([r_chk]), k_chk)
    pq, cq = bvn_lower(r_chk, k_chk)
    assert abs(pv[0] - pq) < 1e-12 and abs(cv[0] - cq) < 1e-12


def lag4(yg: Vec, x: Vec, h: float = 0.01) -> Vec:
    """Four-point Lagrange interpolation on the nodes 0, h, 2h, ... (the four nearest nodes, clamped at the ends)."""
    i0 = np.clip(np.floor(x / h + 1e-9).astype(np.int64) - 1, 0, len(yg) - 4)
    t = x / h - i0
    out = np.zeros_like(x)
    for a in range(4):
        la = np.ones_like(x)
        for b in range(4):
            if b != a:
                la = la * (t - b) / (a - b)
        out = out + la * yg[i0 + a]
    return out


rgrid = np.asarray(np.arange(96) * 0.01, dtype=np.float64)
rfine = np.asarray(np.arange(9501) * 1e-4, dtype=np.float64)
err_c = err_p = 0.0
for j in range(51):
    pg, cg = joint_low(rgrid, 0.05 * j)
    pf, cf = joint_low(rfine, 0.05 * j)
    err_c = max(err_c, float(np.abs(lag4(cg, rfine) - cf).max()))
    err_p = max(err_p, float(np.abs(lag4(pg, rfine) - pf).max()))
put("grid", g(err_c, 4), g(err_p, 4), g(T * err_p, 4))
pg2, cg2 = joint_low(rgrid, 2.0)
c_init = float(lag4(cg2, np.array([RH]))[0])
p_init = float(lag4(pg2, np.array([RH]))[0])
assert f"{c_init:.3f}" == "0.156" and f"{p_init:.4f}" == "0.0051" and f"{T * p_init:.1f}" == "22.4"  # initial state

ORDER = [
    "T", "years", "A", "repairs", "repairs_key", "rho", "rho3", "apr7", "d2apr7", "out9", "exp9", "logmom", "m",
    "annual", "eqw", "ell2", "KC2", "KC4", "KC6", "KC6b", "vtrunc", "KC7", "p9", "X2", "X2m", "ties1", "E4corr",
    "E4big", "X3", "X4", "X4tot", "X4printed", "means", "rho2", "X5S", "X5", "X6pair", "X6S5", "X8model", "X8low",
    "X8up", "X8prob", "X9two", "X9fall", "X9rise", "grid", "E1joint", "E1cond", "E2", "E3", "lm10S", "E5", "sds",
    "E7", "E7u", "E7data", "E9", "E9p", "E10", "P1", "P4", "P5", "P5w", "P6", "P6res", "P6b", "P7", "P8ret", "Lp",
    "P8", "P8p", "P10", "py", "freeplan", "regimes", "rho3u", "lm7", "all28", "axes", "E10u",
]
assert sorted(ORDER) == sorted(OUT), set(OUT) ^ set(ORDER)
for i, key in enumerate(ORDER, 1):
    print(f"A16-{i:02d} {OUT[key]}")
