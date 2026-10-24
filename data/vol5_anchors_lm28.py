"""LM28 anchors (Mean-Variance Optimization): every number the Stage 1 brief quotes (drafted 2026-10-24; revised
the same day to the editor's decisions on the briefs, plans/vol-5.md).

Reads only data/processed/*.parquet, through the shared builders (run them first; this script runs neither):
  * E5 (plans/vol-5.md, "Data"): data/vol5_series.py's frames("E5"), which reads data/processed/vol5_frames.parquet:
    the estimation frame (dates on which every fund has a one-session total return; T = 2,362, A = T / years) and the
    wealth frame (every TR23 session after the base close 2017-01-17; a halted fund earns 0 and books its spanning
    return when it trades again; A_w = sessions / years). The funds, in this order: 0050, 00646, 00679B, 00635U, 00642U.
  * The through case's schedule: data/vol5_rules.py's schedule(), WINDOW (504) and RF (1.5% a year). The first window
    is the 504 estimation rows through the first signal (the first month-end with 504 rows); the test period is every
    wealth-frame session after that signal's trade, to 2026-10-08 (no rule of R1-R8 is recomputed or printed here).
  * U28 (Volume II): data/lm10_series.py's u28(), which reads data/processed/vol2_closes.parquet: 28 TWSE sector price
    indices, T = 4,382 daily price returns 2008-12-02 .. 2026-10-08, A = 245.4794; halves of 2,191 returns (LM11's).

Conventions. Annualized inputs, as the through case's signals use them: mu = A * (window mean), Sigma = A * cov0
(divisor T, ddof=0), with E5's estimation-frame A; e = mu - r_f 1 with r_f = 1.5% a year (simple; r_f / A a day).
These are plug-in estimates treated as known inputs (LM28 is In-sample except the one split). Linear systems are
solved with numpy.linalg.solve, never with an explicit inverse (the Jacobian of (28.9) needs Sigma^-1 itself, and
gets it by solving against the identity). Portfolios held out of sample keep constant weights (rebalanced every
session, no costs) and earn w'R_t on the wealth frame; their annualized volatility and mean use A_w; SE(mean) =
A_w s / sqrt(T) (LM20's (20.2)); SE(volatility) = vol * sqrt((Kurt - 1) / (4 T)) with the raw sample kurtosis (LM20,
the delta method under iid days). Joint statistics of the test period (its covariance matrix, its ex-post frontier,
the split by (28.3)) use the estimation frame's test rows. A single fund's test-period volatility (X1) is computed on
the fund's own one-session dates (traded on t and on the previous wealth-frame date) and annualized by the fund's own
sessions per year over E5: its one-session returns from the base close to 2026-10-08 divided by the same years as A
(shared decision "E5's two frames"; decision C2). Horizons in years are calendar days / 365.25 from the close before
the first return. Weights print in percent; a weight with |w| < 1e-6 would print as 0 (none occurs). "Shorts" count
weights below -1e-6. Gross exposure is the 1-norm of the weights. A residual at machine precision prints as "below
1e-15" (its digits depend on the order of operations); a larger one prints with two significant digits.

Rounding flags. Every number the brief prints passes through f(x, k1, k2, ...), which shows x with max(k) + 3 decimals
and flags it "NEAR" for each printed precision k at which x lies within a tenth of a last-digit unit of a rounding
boundary (|frac(10^k |x|) - 0.5| < 0.1). The brief prints a flagged value as rounded from the unrounded value here.
Numbers printed by earlier modules are echoed with file:line.

Prints one line per anchor, "A28-NN <value>", in ID order, and writes nothing.

Run:  PYTHONUTF8=1 uv run python data/vol5_anchors_lm28.py
"""
import sys
from datetime import date
from importlib.metadata import version
from math import floor, sqrt
from pathlib import Path

import cvxpy as cp
import numpy as np
from numpy.typing import NDArray

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lm10_series import u28
from vol5_rules import CLARABEL_OPTS, OSQP_OPTS, RF, WINDOW, cov0, minvar, schedule
from vol5_series import frames

Vec = NDArray[np.float64]
Mat = NDArray[np.float64]

OUT: list[str] = []
NEAR: list[str] = []


def put(value: str) -> None:
    """One anchor line; values that f() found near a rounding boundary are listed at its end."""
    tail = f" [NEAR a rounding boundary: {'; '.join(NEAR)}]" if NEAR else ""
    OUT.append(f"A28-{len(OUT) + 1:02d} {value}{tail}")
    NEAR.clear()


def f(x: float, *ks: int, plus: bool = False) -> str:
    """x with max(ks) + 3 decimals; flagged for each printed precision k within 0.1 of a last-digit unit of a boundary."""
    x = float(x)
    for k in ks:
        u = abs(x) * 10**k
        if abs(u - floor(u) - 0.5) < 0.1:
            NEAR.append(f"{x:.{k + 3}f} at {k} dp")
    return f"{x:{'+' if plus else ''}.{max(ks) + 3}f}"


def tiny(x: float, bound: float = 1e-15) -> str:
    """A residual: "below 1e-15" at machine precision, else two significant digits."""
    return f"below {bound:.0e}" if abs(x) < bound else f"{abs(x):.1e}"


def pct(v: Vec, *ks: int, plus: bool = False) -> str:
    return "(" + ", ".join(f(100 * float(x), *(ks or (1,)), plus=plus) for x in v) + ")"


def years(a: str, b: str) -> float:
    return (date.fromisoformat(b) - date.fromisoformat(a)).days / 365.25


def kurt(r: Vec) -> float:
    c = r - r.mean()
    return float((c**4).mean() / (c**2).mean() ** 2)


class Opt:
    """The closed forms of LM28 for annualized mu and Sigma (Sigma positive definite)."""

    def __init__(self, mu: Vec, S: Mat, rf: float = RF) -> None:
        n = len(mu)
        self.mu, self.S, self.rf = mu, S, rf
        self.one = np.ones(n)
        x = np.linalg.solve(S, self.one)                       # Sigma^-1 1
        self.s2min = 1 / float(x.sum())                        # (28.2)
        self.wmv = x * self.s2min
        self.mumv = float(mu @ self.wmv)
        d = mu - self.mumv * self.one
        self.dir = np.linalg.solve(S, d)                       # Sigma^-1 (mu - mu_mv 1)
        self.srinf2 = float(d @ self.dir)                      # SR_inf^2, (28.5)
        self.e = mu - rf * self.one
        self.y = np.linalg.solve(S, self.e)                    # Sigma^-1 e
        self.den = float(self.y.sum())                         # 1' Sigma^-1 e
        self.sr2 = float(self.e @ self.y)                      # SR*^2, (28.6)
        self.wtan = self.y / self.den

    def front_var(self, mp: float) -> float:
        return self.s2min + (mp - self.mumv) ** 2 / self.srinf2      # (28.5)

    def front_w(self, mp: float) -> Vec:
        return self.wmv + (mp - self.mumv) / self.srinf2 * self.dir  # (28.4)


def lemma(S: Mat, K: Mat, b: Vec) -> tuple[Vec, float, Vec]:
    """(28.1): min w'Sw subject to Kw = b; returns (w*, value, multipliers lambda, LM7's signs: 2Sw = K'lambda)."""
    Si_Kt = np.linalg.solve(S, K.T)
    G = K @ Si_Kt
    lam = 2 * np.linalg.solve(G, b)
    w = Si_Kt @ lam / 2
    return w, float(b @ np.linalg.solve(G, b)), lam


# ---------------------------------------------------------------- data role
fr = frames("E5")
F = fr.funds
A, Aw = fr.A, fr.A_wealth
put(f"estimation frame T {len(fr.est_dates)} ({fr.est_dates[0]} .. {fr.est_dates[-1]}), A {f(A, 2, 3)}; wealth frame "
    f"{len(fr.wealth_dates)} sessions ({fr.wealth_dates[0]} .. {fr.wealth_dates[-1]}), A_w {f(Aw, 2)}; "
    f"years {f(fr.years, 4)}")                                                                           # 01
sch = schedule(fr)
sig, trade, rows = sch[0]
x = fr.X[rows - WINDOW:rows]
w0, w1 = fr.est_dates[rows - WINDOW], fr.est_dates[rows - 1]
assert w1 == sig
assert fr.wealth_dates.index(w0) > 0
b0w = fr.wealth_dates[fr.wealth_dates.index(w0) - 1]        # the close before the window's first return
put(f"first signal {sig} (estimation rows through it {rows}), trade {trade}; first window {WINDOW} rows {w0} .. {w1}; "
    f"T/A {f(WINDOW / A, 3, 4)}; calendar years from the close before the first return ({b0w}) "
    f"{f(years(b0w, w1), 2, 3)}; signals {len(sch)}, last {sch[-1][0]} (trade {sch[-1][1]})")         # 02
wd = fr.wealth_dates
i0 = wd.index(trade)
Wt = fr.W[i0 + 1:]
ed = fr.est_dates
j0 = next(k for k, d in enumerate(ed) if d > trade)
Xt = fr.X[j0:]
missing = sorted(set(wd[i0 + 1:]) - set(ed[j0:]))
yt = years(trade, wd[-1])
put(f"test period: wealth frame {len(Wt)} returns {wd[i0 + 1]} .. {wd[-1]}; estimation frame {len(Xt)} rows "
    f"{ed[j0]} .. {ed[-1]}; wealth dates not in the estimation frame {missing}; years from the trade close "
    f"{f(yt, 2, 3)}")                                                                                       # 03
put(f"r_f {RF} a year; r_f/A {f(RF / A * 1e4, 3, 4)} bp a day; r_f/A_w {f(RF / Aw * 1e4, 4)} bp a day")     # 04

# ---------------------------------------------------------------- first window: funds
mu = A * x.mean(axis=0)
S = A * cov0(x)
sd = np.sqrt(np.diag(S))
C = S / np.outer(sd, sd)
put("window means A*mean " + ", ".join(f"{s} {f(100 * float(m), 1, 2)}%" for s, m in zip(F, mu, strict=True)))   # 05
put("window vols " + ", ".join(f"{s} {f(100 * v, 1, 2)}%" for s, v in zip(F, sd, strict=True)) + "; Sharpe (r_f 1.5%) "
    + ", ".join(f"{s} {f((m - RF) / v, 2, 3)}" for s, m, v in zip(F, mu, sd, strict=True)))            # 06
pairs = [(i, j) for i in range(5) for j in range(i + 1, 5)]
put("window correlations " + ", ".join(f"{F[i]}-{F[j]} {f(C[i, j], 2, 3, plus=True)}" for i, j in pairs))   # 07
St = A * cov0(Xt)
sdt = np.sqrt(np.diag(St))
Ct = St / np.outer(sdt, sdt)
one_sess = fr.traded & np.vstack([np.ones((1, 5), dtype=np.bool_), fr.traded[:-1]])   # traded on t and t-1
A_own = one_sess.sum(axis=0) / fr.years          # each fund's own sessions per year over E5 (base close to the end)
own = []
for j in range(5):
    ok = one_sess[i0 + 1:, j]
    s_j = float(Wt[ok, j].std(ddof=0))
    own.append((int(ok.sum()), float(A_own[j]), s_j * sqrt(float(A_own[j])), s_j * sqrt(A)))
gaps = [abs(va - float(sj)) for (_, _, _, va), sj in zip(own, sdt, strict=True)]
jg = int(np.argmax(gaps))
put("test vols, estimation frame (A) " + ", ".join(f"{s} {f(100 * v, 1, 2)}%" for s, v in zip(F, sdt, strict=True))
    + "; each fund's own one-session dates, annualized by its own sessions per year over E5 "
    + ", ".join(f"{s} {f(100 * v, 1, 2)}% (n {n}, A_i {ai:.6f})" for s, (n, ai, v, _) in zip(F, own, strict=True))
    + f"; largest |own - estimation frame| on a common A (both x sqrt(A)) {f(100 * gaps[jg], 2)} points "
    f"({F[jg]})")                                                                                       # 08
put("test correlations (estimation frame) "
    + ", ".join(f"{F[i]}-{F[j]} {f(Ct[i, j], 2, 3, plus=True)}" for i, j in pairs))                   # 09

# ---------------------------------------------------------------- section 2: minimum variance
o = Opt(mu, S)
assert np.linalg.eigvalsh(S).min() > 0
put(f"w_mv {pct(o.wmv)}%; sigma_min {f(100 * sqrt(o.s2min), 2)}%; sigma_min^2 {f(o.s2min, 6)}; mu_mv "
    f"{f(100 * o.mumv, 2)}%; lambda* = 2 sigma_min^2 {f(2 * o.s2min, 5)}; gross {f(np.abs(o.wmv).sum(), 4)}; "
    f"smallest weight {f(100 * o.wmv.min(), 2)}% ({F[int(o.wmv.argmin())]})")                          # 10
cov_mv = S @ o.wmv
rc_share = o.wmv * cov_mv / o.s2min
put(f"Cov(R_i, R_mv) = (Sigma w_mv)_i: {f(cov_mv.min(), 7)} .. {f(cov_mv.max(), 7)} (sigma_min^2 {f(o.s2min, 7)}); "
    f"max |risk share - weight| {tiny(np.abs(rc_share - o.wmv).max())}; |beta_i,mv - 1| "
    f"{tiny(np.abs(cov_mv / o.s2min - 1).max())}")                                                     # 11
smins: list[tuple[float, str]] = []
negw, minw, r3gap = 0, 1.0, 0.0
tanscan: list[tuple[float, str, float, float, float]] = []
for sg, _, rw in sch:
    xx = fr.X[rw - WINDOW:rw]
    oo = Opt(A * xx.mean(axis=0), A * cov0(xx))
    smins.append((sqrt(oo.s2min), sg))
    negw += int((oo.wmv < -1e-6).any())
    minw = min(minw, float(oo.wmv.min()))
    r3gap = max(r3gap, float(np.abs(minvar(A * cov0(xx), f"R3 {sg}") - oo.wmv).max()))   # vol5_rules' long-only R3
    tanscan.append((oo.den, sg, float(np.abs(oo.wtan).sum()), oo.mumv, sqrt(oo.sr2)))
srt = sorted(smins)
rank = [s for _, s in srt].index(sig) + 1
put(f"92 windows: sigma_min {f(100 * srt[0][0], 2)}% ({srt[0][1]}) .. {f(100 * srt[-1][0], 2)}% ({srt[-1][1]}); "
    f"first window rank {rank} from the lowest of {len(srt)}; windows with a negative w_mv weight {negw}; smallest "
    f"w_mv weight in any window {f(100 * minw, 2)}%; largest gap to vol5_rules.minvar (long-only R3) {tiny(r3gap)}")  # 12
u = u28()
Su = u.A * cov0(u.X)
ou = Opt(u.A * u.X.mean(axis=0), Su)
evu = np.linalg.eigvalsh(Su)
sdu = np.sqrt(np.diag(Su))
ew = np.full(28, 1 / 28)
put(f"U28 T {u.X.shape[0]}, A {f(u.A, 4)}; w_mv shorts {int((ou.wmv < -1e-6).sum())} of 28; gross "
    f"{f(np.abs(ou.wmv).sum(), 2)}; sigma_min {f(100 * sqrt(ou.s2min), 2)}%; largest {u.names[int(ou.wmv.argmax())]} "
    f"{f(100 * ou.wmv.max(), 1)}%; most negative {u.names[int(ou.wmv.argmin())]} {f(100 * ou.wmv.min(), 1)}%; least "
    f"volatile sector {u.names[int(sdu.argmin())]} {f(100 * sdu.min(), 2)}%; equal weights {f(100 * sqrt(ew @ Su @ ew), 2)}% "
    f"(lm10.md:36 prints 15.75%); kappa(Sigma_hat) {f(evu[-1] / evu[0], 1)}")                            # 13
H = u.X.shape[0] // 2
hv = []
for part in (u.X[:H], u.X[-H:]):
    oh = Opt(u.A * part.mean(axis=0), u.A * cov0(part))
    hv.append(oh)
cosh = float(hv[0].wmv @ hv[1].wmv / (np.linalg.norm(hv[0].wmv) * np.linalg.norm(hv[1].wmv)))
put(f"U28 halves ({H} returns each; their sigma_min and 1/N are LM30's, A30-19): "
    f"shorts {int((hv[0].wmv < -1e-6).sum())} and {int((hv[1].wmv < -1e-6).sum())}; gross "
    f"{f(np.abs(hv[0].wmv).sum(), 2)} and {f(np.abs(hv[1].wmv).sum(), 2)}; cosine of the two w_mv {f(cosh, 3)} "
    f"(lm11.md:467 prints 0.690 for the unscaled solutions)")                                          # 14

# ---------------------------------------------------------------- section 3: the frontier
wN = np.full(5, 0.2)
mN, sN = float(mu @ wN), sqrt(float(wN @ S @ wN))
sf = sqrt(o.front_var(mN))
me = o.mumv + sqrt(o.srinf2 * (sN**2 - o.s2min))
wme = o.front_w(me)
put(f"SR_inf {f(sqrt(o.srinf2), 3)} (SR_inf^2 {f(o.srinf2, 4)}); equal weights: mean {f(100 * mN, 2, 3)}%, vol "
    f"{f(100 * sN, 2)}% (below mu_mv {f(100 * o.mumv, 2, 3)}% by {f(100 * (o.mumv - mN), 2)} points); frontier vol at that mean "
    f"{f(100 * sf, 2)}%; efficient mean at that vol {f(100 * me, 2)}%, weights {pct(wme)}%")           # 15
K = np.vstack([o.one, mu])
wl, val, lam = lemma(S, K, np.array([1.0, me]))
put(f"(28.1) at mu_p {f(100 * me, 2)}%: max |w - (28.4)| {tiny(np.abs(wl - wme).max())}; value {f(val, 6)} = w'Sw "
    f"{f(float(wl @ S @ wl), 6)}; multipliers lambda {f(lam[0], 5, plus=True)}, lambda_mu {f(lam[1], 3, 4, plus=True)}; "
    f"d sigma_p^2 / d mu_p = 2 (mu_p - mu_mv) / SR_inf^2 {f(2 * (me - o.mumv) / o.srinf2, 3, 4)} with mu_p - mu_mv "
    f"{f(100 * (me - o.mumv), 4)} points")                                                               # 16
put(f"(28.4): weights move by {pct(0.01 * o.dir / o.srinf2, 1, 2, plus=True)} points per point of target mean; at mu_p = "
    f"10%: weights {pct(o.front_w(0.10))}%, vol {f(100 * sqrt(o.front_var(0.10)), 2)}%")               # 17

# ---------------------------------------------------------------- section 4: tangency and the CML
sr = sqrt(o.sr2)
st = sqrt(float(o.wtan @ S @ o.wtan))
k_best = int(np.argmax((mu - RF) / sd))
put(f"1'Sigma^-1 e {f(o.den, 2, 3)} > 0 (mu_mv {f(100 * o.mumv, 2, 3)}% > r_f 1.5%); w_tan {pct(o.wtan)}%; mean "
    f"{f(100 * float(mu @ o.wtan), 2, 3)}%, vol {f(100 * st, 2, 3)}%; SR* {f(sr, 2, 3)}; gross {f(np.abs(o.wtan).sum(), 2)}; "
    f"best single fund {F[k_best]} {f((mu[k_best] - RF) / sd[k_best], 2, 3)}")                          # 18
put(f"(28.7): SR*^2 {f(o.sr2, 4)}; SR_inf^2 + ((mu_mv - r_f)/sigma_min)^2 {f(o.srinf2 + (o.mumv - RF) ** 2 / o.s2min, 4)}; "
    f"difference {tiny(o.sr2 - o.srinf2 - (o.mumv - RF) ** 2 / o.s2min)}; ((mu_mv - r_f)/sigma_min) "
    f"{f((o.mumv - RF) / sqrt(o.s2min), 3, 4)}")                                                          # 18 -> 19
rfs = []
w646 = []
for r in (0.0, 0.02):
    orr = Opt(mu, S, r)
    w646.append(float(orr.wtan[1]))
    rfs.append(f"r_f {100 * r:.1f}%: w_tan {pct(orr.wtan)}%, SR* {f(sqrt(orr.sr2), 2, 3)}, 1'Sigma^-1 e {f(orr.den, 2)}")
put("; ".join(rfs) + f"; 00646's weight moves by {f(100 * (w646[1] - w646[0]), 0)} points from r_f 0 to 2%")  # 20
s10 = 0.10
dlt = sr / s10
fx = o.y / dlt
put(f"CML at vol 10%: mean r_f + SR* x 10% = {f(100 * (RF + sr * s10), 2)}%; delta = SR*/0.10 {f(dlt, 2)}; L = "
    f"1'Sigma^-1 e / delta {f(o.den / dlt, 2, 3)}; cash 1 - L {f(1 - o.den / dlt, 2)}; exposures {pct(fx)}%; check "
    f"vol of f {f(100 * sqrt(float(fx @ S @ fx)), 3)}%; L x sigma_tan {f(100 * o.den / dlt * st, 3)}%")    # 21
put(f"delta that holds w_tan with no cash: 1'Sigma^-1 e {f(o.den, 2)}; at delta = 1 the exposures would be "
    f"{pct(o.y, 2)}%, L {f(o.den, 2)}; lm07.md:484 prints f* = L* w_tan for two assets")              # 22
bad = [t for t in tanscan if t[0] <= 0]
good = [t for t in tanscan if t[0] > 0]
gmax = max(good, key=lambda t: t[2])
b0, b1 = min(t[1] for t in bad), max(t[1] for t in bad)
inside = [t[1] for t in good if b0 < t[1] < b1]
put(f"92 windows: 1'Sigma^-1 e <= 0 (r_f >= mu_mv) in {len(bad)}, first {b0}, last {b1}; valid month-ends between "
    f"them {inside}; mu_mv over the {len(bad)}: {f(100 * min(t[3] for t in bad), 2)}% .. "
    f"{f(100 * max(t[3] for t in bad), 2)}%; among the other {len(good)}: smallest 1'Sigma^-1 e "
    f"{f(min(t[0] for t in good), 3)}, "
    f"largest gross |w_tan| {f(gmax[2], 1, 2)} ({gmax[1]}, 1'Sigma^-1 e {f(gmax[0], 3)}, mu_mv {f(100 * gmax[3], 2)}%); "
    f"gross range of valid tangencies {f(min(t[2] for t in good), 2)} .. {f(gmax[2], 1, 2)}")                # 23
bw = max(bad, key=lambda t: t[2])
rwb = next(rw for sg, _, rw in sch if sg == bw[1])
xb = fr.X[rwb - WINDOW:rwb]
ob = Opt(A * xb.mean(axis=0), A * cov0(xb))
srn = float(ob.e @ ob.wtan) / sqrt(float(ob.wtan @ ob.S @ ob.wtan))
sup = [((mp - RF) / sqrt(ob.front_var(mp))) for mp in (ob.mumv + 0.1, ob.mumv + 1.0, ob.mumv + 10.0)]
put(f"window {bw[1]}: mu_mv {f(100 * ob.mumv, 2)}% < r_f; 1'Sigma^-1 e {f(ob.den, 3)}; normalized Sigma^-1 e: gross "
    f"{f(bw[2], 1)}, Sharpe {f(srn, 2, 3)} = -sqrt(e'Sigma^-1 e) {f(-sqrt(ob.sr2), 2, 3)}; upper-branch Sharpe at mu_mv + 10, "
    f"100, 1000 points {', '.join(f(v, 3, 4) for v in sup)} -> SR_inf {f(sqrt(ob.srinf2), 3, 4)}")              # 24

# ---------------------------------------------------------------- section 5: sensitivity
dW = np.zeros((5, 5))
for i in range(5):
    m2 = mu.copy()
    m2[i] += 0.01
    dW[:, i] = Opt(m2, S).wtan - o.wtan
put("exact change of w_tan (points) for +1 point in one mean, columns = the fund whose mean rises: "
    + "; ".join(f"{F[i]}: {pct(dW[:, i], 1, 2, plus=True)}" for i in range(5)))                           # 25
Jac = (np.eye(5) - np.outer(o.wtan, o.one)) @ np.linalg.solve(S, np.eye(5)) / o.den   # Sigma^-1 by solving
gap = np.abs(0.01 * Jac - dW)
put(f"(28.9) linear prediction for +1 point: 00635U's own weight {f(100 * 0.01 * Jac[3, 3], 1, 2)} against exact "
    f"{f(100 * dW[3, 3], 1, 2)} points; largest gap {f(100 * gap.max(), 1, 2)} points; 00642U column linear "
    f"{pct(0.01 * Jac[:, 4], 1, 2, plus=True)}")                                                            # 26
se_mu = sd / sqrt(WINDOW / A)
put("SE of each window mean, A s / sqrt(T) (annual points): " + ", ".join(f"{s} {f(100 * v, 1)}" for s, v in
                                                                          zip(F, se_mu, strict=True))
    + f"; 00635U: mean {f(100 * mu[3], 2)}% -> {f(100 * (mu[3] + 0.01), 2)}%, 1 point = {f(0.01 / se_mu[3], 2, 3)} SE; "
    f"w_tan(00635U) {f(100 * o.wtan[3], 1, 2, 3)}% -> {f(100 * (o.wtan[3] + dW[3, 3]), 1, 2, 3)}%")        # 27
col = np.linalg.solve(S, np.eye(5)[:, 3])
put(f"exposure form at delta {f(dlt, 2)}: +1 point in 00635U's mean changes f* by 0.01 x column 4 of Sigma^-1 / delta "
    f"= {pct(0.01 * col / dlt, 1, 2, plus=True)} points exactly; L changes by {f(100 * 0.01 * col.sum() / dlt, 1, 2, plus=True)} "
    f"points")                                                                                            # 28

# ---------------------------------------------------------------- section 6: held to the end
held = {}
for name, w in (("w_mv", o.wmv), ("w_tan", o.wtan)):
    r = Wt @ w
    T = len(r)
    s = float(r.std(ddof=0))
    vol = s * sqrt(Aw)
    kk = kurt(r)
    held[name] = (vol, float(r.mean() * Aw))
    pv, pm = sqrt(float(w @ S @ w)), float(mu @ w)
    se_v, se_m = vol * sqrt((kk - 1) / (4 * T)), s * Aw / sqrt(T)
    put(f"{name} held {wd[i0 + 1]} .. {wd[-1]} (wealth frame, T {T}): predicted vol {f(100 * pv, 2)}%, "
        f"realized {f(100 * vol, 2)}% (SE {f(100 * se_v, 2)}, raw kurtosis {f(kk, 1, 2)}; normal "
        f"SE {f(100 * vol / sqrt(2 * T), 2)}); predicted mean {f(100 * pm, 2)}%, realized "
        f"{f(100 * float(r.mean()) * Aw, 2)}% (SE {f(100 * se_m, 1, 2)}); log growth "
        f"{f(100 * float(np.log1p(r).sum()) / yt, 2)}% a year; min 1 + R {f(float((1 + r).min()), 3, 4)}; "
        f"realized vol / predicted {f(vol / pv, 2)}; (realized - predicted) / SE: vol {f((vol - pv) / se_v, 0, 1)}, "
        f"mean {f((float(r.mean()) * Aw - pm) / se_m, 1)}")                                              # 29, 30
ot = Opt(A * Xt.mean(axis=0), St)
parts = []
for name, w in (("w_mv", o.wmv), ("w_tan", o.wtan)):
    dv = float((w - ot.wmv) @ St @ (w - ot.wmv))
    tot = float(w @ St @ w)
    parts.append(f"{name}: weight-error term {f(dv, 5, 6)}, total {f(tot, 5, 6)} (check {tiny(ot.s2min + dv - tot)}), vol "
                 f"{f(100 * sqrt(tot), 2)}% (wealth frame {f(100 * held[name][0], 2)}%), added by the weight error "
                 f"{f(100 * (sqrt(tot) - sqrt(ot.s2min)), 2)} points")
put(f"test period, estimation frame ({len(Xt)} rows): sigma_min^2 {f(ot.s2min, 5, 6)}, sigma_min {f(100 * sqrt(ot.s2min), 2)}% "
    f"(window {f(100 * sqrt(o.s2min), 2)}%); " + "; ".join(parts))                                       # 31
put(f"test period ex post (in-sample on the test rows): w_mv {pct(ot.wmv)}%, mu_mv {f(100 * ot.mumv, 2)}%; w_tan "
    f"{pct(ot.wtan)}%, SR* {f(sqrt(ot.sr2), 2)}; 1'Sigma^-1 e {f(ot.den, 2)}; SR_inf {f(sqrt(ot.srinf2), 3)}")  # 32

# ---------------------------------------------------------------- section 7: Python
KKT = np.block([[2 * S, K.T], [K, np.zeros((2, 2))]])
sol = np.linalg.solve(KKT, np.concatenate([np.zeros(5), [1.0, me]]))
duals = []
for solver, opts in ((cp.OSQP, OSQP_OPTS), (cp.CLARABEL, CLARABEL_OPTS)):
    wv = cp.Variable(5)
    cons = [o.one @ wv == 1, mu @ wv == me]
    prob = cp.Problem(cp.Minimize(cp.quad_form(wv, cp.psd_wrap(S))), cons)
    prob.solve(solver=solver, **opts)
    v = wv.value
    assert v is not None
    vv = np.asarray(v, dtype=np.float64)
    d0, d1 = float(np.asarray(cons[0].dual_value)), float(np.asarray(cons[1].dual_value))
    stat = np.abs(2 * S @ vv + K.T @ np.array([d0, d1])).max()     # KKT stationarity with cvxpy's duals: 2 S w + K' nu
    prim = np.abs(K @ vv - np.array([1.0, me])).max()              # primal feasibility
    duals.append(f"{solver} {opts} status {prob.status}, max weight gap {tiny(np.abs(vv - wl).max())}, objective gap "
                 f"{tiny((float(prob.value) - val) / val)}, KKT residuals: stationarity {tiny(stat)}, feasibility "
                 f"{tiny(prim)}; dual values {f(d0, 5, plus=True)} and {f(d1, 3, 4, plus=True)}")
put(f"KKT system [2 Sigma, K'; K, 0][w; -lambda] = [0; b]: max |w - (28.1)| {tiny(np.abs(sol[:5] - wl).max())}, "
    f"max |w - (28.4)| {tiny(np.abs(sol[:5] - wme).max())}, -lambda {f(sol[5], 5, plus=True)}, "
    f"{f(sol[6], 3, 4, plus=True)}; cvxpy {version('cvxpy')} (OSQP {version('osqp')}, CLARABEL {version('clarabel')}), "
    f"a fresh Problem per solver: " + "; ".join(duals))                                                  # 33

# ---------------------------------------------------------------- problems (hypothetical inputs unless stated)
S3 = np.diag([0.01, 0.04, 0.04])
o3 = Opt(np.zeros(3), S3)
put(f"P1 vols 10%, 20%, 20%, uncorrelated: w_mv {pct(o3.wmv)}%, sigma_min {f(100 * sqrt(o3.s2min), 2)}%; inverse "
    f"volatility {f(100 * 10 / 20, 1)}%; equal {f(100 / 3, 1)}%")                                       # 34
S2 = np.array([[0.04, 0.6 * 0.2 * 0.1], [0.6 * 0.2 * 0.1, 0.01]])
o2 = Opt(np.zeros(2), S2)
put(f"P2 vols 20%, 10%, rho 0.6: w_mv in asset 1 {f(100 * o2.wmv[0], 1)}%, sigma_min {f(100 * sqrt(o2.s2min), 2)}%; "
    f"inverse variance ignoring rho {f(100 * 25 / 125, 1)}%; rho > sigma_2/sigma_1 = 0.5")                # 35
p3 = sqrt(0.05**2 + (0.08 - 0.04) ** 2 / 0.5**2)
put(f"P3 sigma_min 5%, mu_mv 4%, SR_inf 0.5, mu_p 8%: vol {f(100 * p3, 2)}%; distractors {f(100 * (0.05 + 0.04 / 0.5), 1)}%"
    f", {f(100 * 0.04 / 0.5, 1)}%")                                                                      # 36
p4 = sqrt(0.5**2 + ((0.04 - 0.015) / 0.05) ** 2)
put(f"P4 same, r_f 1.5%: SR* {f(p4, 3)}; distractors 0.50 (SR_inf), {f(0.5 + 0.5, 2)}; w_tan mean "
    f"{f(100 * (0.015 + p4**2 * 0.05**2 / (0.04 - 0.015)), 2)}%")                                       # 37
put(f"P5 SR* 0.8, 1'Sigma^-1 e 8, delta 4: vol SR*/delta {f(100 * 0.8 / 4, 1)}%, L 8/4 {f(8 / 4, 1)}, borrowing "
    f"{f(8 / 4 - 1, 1)}; distractors L {f(4 / 8, 1)}, vol {f(100 * 0.8 * 4, 0)}%")                       # 38
put(f"P6 r_f above mu_mv: Sigma^-1 e / 1'Sigma^-1 e has Sharpe -sqrt(e'Sigma^-1 e), the lowest of any fully invested "
    f"portfolio (window {bw[1]}: {f(srn, 2, 3)})")                                                          # 39
s1, s2, s12 = 0.026800, 0.018353, -0.004908
o7 = Opt(np.zeros(2), np.array([[s1, s12], [s12, s2]]))
put(f"P9 LM7's 2017-2021 inputs (lm07.md:409): w_mv {pct(o7.wmv)}%, sigma_min {f(100 * sqrt(o7.s2min), 2)}%, lambda* "
    f"{f(2 * o7.s2min, 4)} (lm07.md:412-414 print 42.3%, 9.22%, 0.0170)")                              # 40
col1 = np.linalg.solve(S, np.eye(5)[:, 0])
put(f"P10 +1 point in 0050's mean: {pct(dW[:, 0], 1, 2, plus=True)} points; column 1 of Sigma^-1 (annual units) ("
    + ", ".join(f(float(v), 1, 2) for v in col1) + f"); window correlation 0050-00646 {f(C[0, 1], 2, 3)}")  # 41


def with_corr(r_: float) -> Mat:
    """The window's Sigma with corr(0050, 00646) replaced by r_ (the widget's third slider)."""
    S_ = S.copy()
    S_[0, 1] = S_[1, 0] = r_ * sd[0] * sd[1]
    return S_


def pd_edge(inside: float, outside: float) -> float:
    """Bisection on the sign of the smallest eigenvalue between a PD and a non-PD correlation."""
    assert np.linalg.eigvalsh(with_corr(inside)).min() > 0 >= np.linalg.eigvalsh(with_corr(outside)).min()
    for _ in range(100):
        mid = 0.5 * (inside + outside)
        if np.linalg.eigvalsh(with_corr(mid)).min() > 0:
            inside = mid
        else:
            outside = mid
    return inside


lo_r, hi_r = pd_edge(float(C[0, 1]), -0.999), pd_edge(float(C[0, 1]), 0.999)
mu_s = mu.copy()
mu_s[1], mu_s[3] = 0.100, 0.008                                  # the sliders' rounded starting values
o_s = Opt(mu_s, with_corr(0.54))
put(f"widget: Sigma stays positive definite for corr(0050, 00646) between {f(lo_r, 3, 4)} and {f(hi_r, 3, 4)} with the "
    f"other window entries fixed (bisection on the smallest eigenvalue); at the sliders' rounded starting values "
    f"(00646's mean 10.0%, 00635U's 0.8%, corr 0.54): w_mv {pct(o_s.wmv)}%, sigma_min {f(100 * sqrt(o_s.s2min), 2)}%, "
    f"mu_mv {f(100 * o_s.mumv, 2)}%, w_tan {pct(o_s.wtan)}%, SR* {f(sqrt(o_s.sr2), 3)}, gross "
    f"{f(np.abs(o_s.wtan).sum(), 2)}")                                                                   # 42

ev5 = np.linalg.eigvalsh(S)
put(f"E5 first window: kappa(Sigma) {f(ev5[-1] / ev5[0], 3)} against 1'Sigma^-1 e {f(o.den, 3)} (a numerical "
    f"coincidence: 1'Sigma^-1 e depends on the annualization, kappa does not); eigenvalues "
    + ", ".join(f(float(v), 5) for v in ev5[::-1]))                                                   # 43

put(f"(11.4) bounds, first window: sqrt(lambda_N / N) {f(100 * sqrt(ev5[0] / 5), 2)}% <= sigma_min "
    f"{f(100 * sqrt(o.s2min), 2)}% <= equal weights {f(100 * sN, 2)}% <= sqrt(lambda_1 / N) {f(100 * sqrt(ev5[-1] / 5), 2)}%")  # 44

Sw_tan = S @ o.wtan
beta_tan = Sw_tan / float(o.wtan @ Sw_tan)                      # (27.5) with p = the tangency portfolio
mu_tan = float(mu @ o.wtan)
put("tangency betas, first window: (Sigma w_tan)_i / sigma_tan^2 (" + ", ".join(f(float(b), 2) for b in beta_tan)
    + f"); mu_tan - r_f {f(100 * (mu_tan - RF), 2)} points; "
    f"max |beta_i - e_i / (mu_tan - r_f)| {tiny(np.abs(beta_tan - o.e / (mu_tan - RF)).max())}; "
    f"max |Sigma w_tan - e / 1'Sigma^-1 e| {tiny(np.abs(Sw_tan - o.e / o.den).max())}")                 # 45

print("\n".join(OUT))
