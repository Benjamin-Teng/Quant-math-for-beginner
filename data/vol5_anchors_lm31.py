"""LM31 anchors (Risk Parity, HRP and Volatility Targeting): every number the Stage 1 brief quotes (drafted 2026-10-24;
revised the same day to the editor's decisions on the briefs, plans/vol-5.md: owners A2, A4-A6, labels C7, the
recomputation's findings; revised again to the decisions on the second recomputation and cross-check: A31-35 extended
with the EWMA's QLIKE wins and losses, A31-26 worded as the mean of R6's 92 target weights, echoes at their owners'
precision, C12; repaired after the third revision's check: A31-26 names each holding month's own target weights, and
A31-17 prints the squares of A31-07's two-decimal volatilities beside the variances).

Reads only data/processed/*.parquet, through the shared builders (run them first; this script runs neither):
  * E5 (plans/vol-5.md, "Data"): vol5_series.frames("E5"), which reads data/processed/vol5_frames.parquet (built and
    checked by data/vol5_series.py from FinMind's TaiwanStockPrice, TaiwanStockDividendResult and
    TaiwanStockSplitPrice, retrieved 2026-10-24): 0050, 00646, 00679B, 00635U and 00642U, daily total returns from the
    base close 2017-01-17 to 2026-10-08. Estimation frame: the dates on which every fund has a one-session return
    (T = 2,362, A = 242.951422); wealth frame: every TR23 session after the base (2,368, A_w = 243.568572).
  * The through case (plans/vol-5.md, "Through case"): vol5_rules.schedule(), signals(), wealth_path(), summary(),
    erc(), hrp(), minvar(), cov0(), quasi_diag() and the constants WINDOW (504), LAM (0.94), CAP (1.5), RF, SPREAD.
    No rule is re-implemented for a printed through-case number: R6, R7 and R8 come from signals(); the scripts here
    only recompute R8's two volatilities from R6's weights (as signals() does, asserted equal) and replay HRP's steps
    on the first window (asserted equal to hrp()).
  * U28 (Volume II): data/lm10_series.py's u28(), which reads data/processed/vol2_closes.parquet (built and repaired
    by data/vol2_series.py; FinMind TaiwanStockPrice, retrieved 2026-10-11): the 28 leaf TWSE sector price indices,
    T = 4,382 simple daily price returns 2008-12-02 .. 2026-10-08, A = 245.4794; halves of 2,191 returns (LM11's).

Conventions. Simple returns. Covariances divide by T (cov0, ddof=0). Solvers and the ERC iteration get annualized
inputs (A x the window's covariance; the weights do not depend on the scale, A31-15). Risk decomposition of weights w
under S (LM27's): MRC_i = (S w)_i / sqrt(w'S w), RC_i = w_i MRC_i, risk share_i = RC_i / sqrt(w'S w). Risk budgets b
(b_i > 0, sum 1): the risk-budget weights solve w_i (S w)_i = b_i w'S w, w > 0, sum 1, computed as y / sum(y) with y the
minimizer of h(y) = 1/2 y'S y - sum b_i ln y_i (Newton: vol5_rules.erc for equal budgets; cyclical coordinate descent,
CCD, here: y_i <- (-c_i + sqrt(c_i^2 + 4 S_ii b_i)) / (2 S_ii), c_i = (S y)_i - S_ii y_i, sweeps i = 1..N, started at
y_i = 1 / sqrt(S_ii), stopped when max |y_i (S y)_i - b_i| < 1e-12). Jacobi's fixed point (weights proportional to
b_i / beta_{i,p}) is run on the annualized covariance from 1/N for at most 10,000 steps, stopped when no weight moves by
1e-12 or more in a step (max_i |w_{k+1,i} - w_{k,i}| < 1e-12); its step count depends on the scale, the point it
settles at does not. Newton's step count follows vol5_rules.erc exactly (the
same start, Armijo backtracking while max |y_i (S y)_i - b_i| > 1e-6, stop below 1e-13). Inverse-volatility (IV) weights are
proportional to 1 / sqrt(S_ii); HRP's inverse-variance weights inside a cluster to 1 / S_ii. HRP (Lopez de Prado
2016): d_ij = sqrt((1 - rho_ij) / 2); the column distance ||d_i - d_j|| (Euclidean, over the N entries of each column
of the distance matrix); single linkage; the quasi-diagonal order; recursive bisection of the ordered list, the first
half taking floor(n/2) items, each half weighted by the other half's share of the two inverse-variance portfolio
variances. "Linked on d directly": the same steps without the column distance. R8 (vol5_rules.signals): p_t = x_t'w6
on the window's 504 rows with R6's new weights; sigma_bar^2 = mean(p_t^2) (uncentred); the EWMA (26.2) with lambda
0.94 on p_t (simple returns, decimals, uncentred), started at sigma_bar^2; L = min(1.5, sigma_bar / sigma_{t+1|t}).
Annualized volatilities: sqrt(A) x a daily one with the estimation frame's A for window quantities and U28's A for
U28; realized volatility of a rule (summary()'s "vol"): the standard deviation (divisor n, centred) of the wealth
path's daily net returns from the session after the first trade, x sqrt(A_w). A holding month k runs from the session
after trade k to trade k+1 inclusive (the trade's own day earns the old holdings' return) and is named by its first and
last dates; its realized volatility is the uncentred root mean square of the path's daily net returns in it, compared
with that signal's sigma_bar (both daily, per session), as a ratio; where an annual figure is printed beside the
ratio, the month's RMS and its target are both annualized with the target's A (estimation frame), so that the ratio
reads off the printed figures; the last month (5 sessions) is partial and left out. The SD of ln(ratio) divides by
the 91 months (the book's divisor T). QLIKE (26.8): V / F - ln(V / F) - 1 with V the month's mean squared daily
return of R6's net path and F a forecast made at its signal: sigma_bar^2 or the EWMA's sigma_{t+1|t}^2 (both daily).
The EWMA "wins" a holding month when its QLIKE is below the window's; its gain there is the window's QLIKE minus its
own, and its cost in a month it loses is its QLIKE minus the window's (so the costs minus the gains are 91 times the
gap in mean QLIKE). R6's ex-post shares on the out-of-sample covariance use the mean of R6's 92 target weights
(A31-24's means); holding month by holding month, each holding month's own R6 target weights on that holding month's
covariance.
Quantiles: inverted_cdf. Counts against a threshold use a 1e-12 guard. U28's halves: constant weights estimated on
the first half; in-sample volatility sqrt(A w'S1 w), out-of-sample sqrt(A w'S2 w). A gap at machine precision prints
as a bound ("below 1e-15"), since its digits depend on the order of the floating-point operations.
Numbers printed by published modules are echoed with file:line; statistics owned by another module (plans/vol-5.md,
"Owners" and decisions A1-A6) are echoed with that module's name and anchor ID, at most at the owner's precision unless
a computation shown beside them needs more (decision C12), and are not LM31's to print: the first window's fund
volatilities and correlations (LM28's A28-06, A28-07; one and two decimals there), R1's first-window volatility
(A28-15) and R3's first-window weights and volatility (A28-10); R1's first-window risk shares (LM27's A27-21, decision
A4's carve-out); R2's first-window volatility (LM30's A30-24, A4's exception); the realized volatility of R1, R3 and
R5 (LM30's A30-12); 1/N and minimum variance on U28's halves (LM30's A30-19, decision A5). R2's first-window risk
shares are LM31's (decision A4's exception). Annual turnover of every rule is LM34's (A34-06); LM31 prints only R8's
per-trade statistics (decision A2).

Rounding flags. Every number the brief prints passes through f(x, k1, k2, ...), which shows x with max(k) + 3 decimals
and flags it "NEAR" for each printed precision k at which x lies within a tenth of a last-digit unit of a rounding
boundary (|frac(10^k |x|) - 0.5| < 0.1). The brief prints a flagged value as rounded from the unrounded value here.
Percentages are passed to f() in percent.

A31-46 is a source check, not a number for the text: it reproduces Lopez de Prado's (2016) Examples 1-2 (SSRN 2708678).

Prints one line per anchor, "A31-NN <value>", in ID order, and writes nothing.

Run:  PYTHONUTF8=1 uv run python data/vol5_anchors_lm31.py
"""
import sys
import warnings
from math import floor, log, sqrt
from pathlib import Path

import cvxpy as cp
import numpy as np
from numpy.typing import NDArray
from scipy.cluster.hierarchy import leaves_list, linkage
from scipy.spatial.distance import squareform

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lm10_series import u28
from vol5_rules import (
    CAP,
    ERC_CHECK_TOL,
    ERC_OPTS,
    LAM,
    RF,
    SPREAD,
    WINDOW,
    cov0,
    erc,
    hrp,
    minvar,
    quasi_diag,
    schedule,
    signals,
    summary,
    wealth_path,
)
from vol5_series import frames

Vec = NDArray[np.float64]
Mat = NDArray[np.float64]
EPS = 1e-12

OUT: list[str] = []
NEAR: list[str] = []


def put(value: str) -> None:
    """One anchor line; values that f() found near a rounding boundary are listed at its end."""
    tail = f" [NEAR a rounding boundary: {'; '.join(NEAR)}]" if NEAR else ""
    OUT.append(f"A31-{len(OUT) + 1:02d} {value}{tail}")
    NEAR.clear()


def f(x: float, *ks: int, plus: bool = False) -> str:
    """x with max(ks) + 3 decimals; flagged for each printed precision k within 0.1 of a last-digit unit of a boundary."""
    x = float(x)
    for k in ks:
        u = abs(x) * 10**k
        if abs(u - floor(u) - 0.5) < 0.1:
            NEAR.append(f"{x:.{k + 3}f} at {k} dp")
    return f"{x:{'+' if plus else ''}.{max(ks) + 3}f}"


def fl(xs: Vec, *ks: int) -> str:
    return "(" + ", ".join(f(float(v), *ks) for v in xs) + ")"


def shares(w: Vec, S: Mat) -> Vec:
    return w * (S @ w) / float(w @ S @ w)


def vol(w: Vec, S: Mat) -> float:
    return sqrt(float(w @ S @ w))


def ccd(S: Mat, b: Vec, tol: float = 1e-12, cap: int = 100000) -> tuple[Vec, int]:
    """Cyclical coordinate descent on h(y) = 1/2 y'S y - sum b_i ln y_i (each step the exact minimizer along y_i)."""
    y = 1 / np.sqrt(np.diag(S))
    for sweep in range(1, cap + 1):
        for i in range(len(b)):
            c = float(S[i] @ y - S[i, i] * y[i])
            y[i] = (-c + sqrt(c * c + 4 * S[i, i] * b[i])) / (2 * S[i, i])
        if float(np.abs(y * (S @ y) - b).max()) < tol:
            return y / y.sum(), sweep
    raise SystemExit("CCD did not converge")


def jacobi(S: Mat, b: Vec, cap: int = 10000, tol: float = 1e-12) -> tuple[Vec, int]:
    """Weights proportional to b_i / beta_{i,p} (Chaves et al. 2012's fixed point); -1 steps when it does not settle."""
    w = np.full(len(b), 1 / len(b))
    for step in range(1, cap + 1):
        beta = (S @ w) / float(w @ S @ w)
        wn = (b / beta) / float((b / beta).sum())
        if float(np.abs(wn - w).max()) < tol:
            return wn, step
        w = wn
    return w, -1


def newton_steps(S: Mat, b: Vec) -> tuple[Vec, int]:
    """Newton's method on h as vol5_rules.erc runs it (same start, Armijo backtracking, same stop), counting steps."""
    n = len(b)
    y = 1 / np.sqrt(np.diag(S))
    y *= np.sqrt(1 / (n * (y @ S @ y)))

    def h(v: Vec) -> float:
        return 0.5 * float(v @ S @ v) - float(b @ np.log(v))

    for step in range(101):
        g = S @ y - b / y
        if float(np.abs(g * y).max()) < 1e-13:
            return y / y.sum(), step
        d = np.linalg.solve(S + np.diag(b / y**2), -g)
        t = 1.0
        far = float(np.abs(g * y).max()) > 1e-6
        while (y + t * d).min() <= 0 or (far and h(y + t * d) > h(y) + 1e-4 * t * float(g @ d)):
            t /= 2
        y = y + t * d
    raise SystemExit("Newton did not converge")


def bound(x: float, b: float = 1e-15) -> str:
    """A gap at machine precision, printed as a bound (its digits depend on the order of operations)."""
    if x >= b:
        raise SystemExit(f"gap {x:.1e} is not below {b:.0e}")
    return f"below {b:.0e}"


def dist(x: Mat) -> tuple[Mat, Mat]:
    """(d, column distance) as vol5_rules.hrp builds them."""
    C = np.corrcoef(x, rowvar=False)
    C = (C + C.T) / 2
    np.fill_diagonal(C, 1.0)
    d = np.sqrt(np.clip((1 - C) / 2, 0.0, None))
    np.fill_diagonal(d, 0.0)
    d2 = np.sqrt(((d[:, :, None] - d[:, None, :]) ** 2).sum(axis=0))
    d2 = (d2 + d2.T) / 2
    np.fill_diagonal(d2, 0.0)
    return d, d2


def link(m: Mat) -> NDArray[np.float64]:
    return np.asarray(linkage(squareform(m, checks=False), method="single"), dtype=np.float64)


def bisect(order: list[int], S: Mat) -> tuple[Vec, list[tuple[list[int], list[int], float, float]]]:
    """HRP's recursive bisection, recording each split (left, right, var_left, var_right)."""
    w = np.ones(S.shape[0])
    steps = []
    clusters = [order]
    while clusters:
        clusters = [c[a:b] for c in clusters for a, b in ((0, len(c) // 2), (len(c) // 2, len(c))) if len(c) > 1]
        for left, right in zip(clusters[::2], clusters[1::2], strict=True):
            v = []
            for c in (left, right):
                sub = S[np.ix_(c, c)]
                ivp = 1 / np.diag(sub)
                ivp /= ivp.sum()
                v.append(float(ivp @ sub @ ivp))
            w[left] *= v[1] / (v[0] + v[1])
            w[right] *= v[0] / (v[0] + v[1])
            steps.append((left, right, v[0], v[1]))
    return w, steps


def hrp_on_d(x: Mat, S: Mat) -> Vec:
    d, _ = dist(x)
    return bisect(quasi_diag(link(d), S.shape[0]), S)[0]


def ewma(p: Vec, start: float) -> float:
    s2 = start
    for r in p:
        s2 = LAM * s2 + (1 - LAM) * r * r
    return s2


# ---------------------------------------------------------------- data role
fr = frames("E5")
funds = fr.funds
N = len(funds)
J = {s: i for i, s in enumerate(funds)}
A, Aw = fr.A, fr.A_wealth
est = fr.est_dates
put(f"estimation frame T {len(est)}, {est[0]} -> {est[-1]}, A {f(A, 2)} (vol5_series)")                     # 01
put(f"wealth frame {len(fr.wealth_dates)} sessions {fr.wealth_dates[0]} -> {fr.wealth_dates[-1]}, A_w {f(Aw, 2)}, "
    f"years {fr.years:.8f}")                                                                                 # 02
sch = schedule(fr)
log_: list[str] = []
sigs = signals(fr, log_)
s0, t0, r0 = sch[0]
put(f"{len(sch)} signals: first {s0} (trade {t0}; window rows {r0 - WINDOW + 1}..{r0}, 1-based = {est[r0 - WINDOW]} -> "
    f"{est[r0 - 1]}), last {sch[-1][0]} (trade {sch[-1][1]}); window {WINDOW} rows")                         # 03
paths = {k: wealth_path(fr, sigs, k) for k in ("R1", "R3", "R5", "R6", "R7", "R8")}
p8 = paths["R8"]
trades = [s.trade for s in sigs]
idx = [p8.dates.index(t) for t in trades]
mlen = [idx[k + 1] - idx[k] for k in range(len(idx) - 1)]
put(f"out-of-sample returns {p8.dates[1]} -> {p8.dates[-1]}: {len(p8.dates) - 1} sessions; complete holding months "
    f"{len(mlen)} ({min(mlen)}-{max(mlen)} sessions); last month {p8.dates[idx[-1] + 1]} -> {p8.dates[-1]} "
    f"({len(p8.dates) - 1 - idx[-1]} sessions, left out)")                                                  # 04
u = u28()
H = len(u.X) // 2
put(f"U28 T {len(u.X)}, {u.dates[0]} -> {u.dates[-1]}, A {f(u.A, 4, 2)}; halves {H} + {len(u.X) - H}: "
    f"{u.dates[0]} -> {u.dates[H - 1]} and {u.dates[H]} -> {u.dates[-1]} (lm11.md:387, 400)")                # 05

# ---------------------------------------------------------------- the first window (Descriptive)
x0 = fr.X[r0 - WINDOW:r0]
S0 = A * cov0(x0)
v0 = np.sqrt(np.diag(S0))
C0 = S0 / np.outer(v0, v0)
rbar = float((C0.sum() - N) / (N * (N - 1)))
put(f"first window (echo of LM28's A28-06, A28-07) vols {fl(100 * v0, 1, 2)}%; corr 0050-00646 {f(C0[0, 1], 2)}, "
    f"0050-00679B {f(C0[0, 2], 2)}, 00646-00679B {f(C0[1, 2], 2)}, 00679B-00635U {f(C0[2, 3], 2)}, 0050-00642U "
    f"{f(C0[0, 4], 2)}, 00646-00642U {f(C0[1, 4], 2)}, 00679B-00642U {f(C0[2, 4], 2)}; mean off-diagonal (LM31's) "
    f"{f(rbar, 4)}")                                                                                        # 06
pair = [J["0050"], J["00679B"]]
S2 = S0[np.ix_(pair, pair)]
w_two = erc(S2)
iv_two = (1 / np.sqrt(np.diag(S2))) / float((1 / np.sqrt(np.diag(S2))).sum())
mv_two = minvar(S2, "two funds")
put(f"0050/00679B: vols {f(100 * sqrt(S2[0, 0]), 2)}% and {f(100 * sqrt(S2[1, 1]), 2)}%, rho {f(C0[0, 2], 2)}; ERC "
    f"{fl(w_two, 4)} = IV {fl(iv_two, 4)} (max diff {bound(float(np.abs(w_two - iv_two).max()))}); shares "
    f"{fl(shares(w_two, S2), 4)}; minimum variance (LM7's formula) {fl(mv_two, 3)}; ERC vol "
    f"{f(100 * vol(w_two, S2), 1)}%, MV vol {f(100 * vol(mv_two, S2), 1)}%")                               # 07
Ceq = (1 - rbar) * np.eye(N) + rbar * np.ones((N, N))
iv0 = (1 / v0) / float((1 / v0).sum())
w_eq = erc(np.outer(v0, v0) * Ceq)
put(f"equal correlations {f(rbar, 4)} with the window's vols: ERC - IV max |diff| "
    f"{bound(float(np.abs(w_eq - iv0).max()))}")                                                           # 08
put(f"IV first window {fl(iv0, 3, 4)}; shares {fl(100 * shares(iv0, S0), 1)}%; vol {f(100 * vol(iv0, S0), 2)}%")  # 09
w6 = sigs[0].targets["R6"]
w7 = sigs[0].targets["R7"]
w3 = sigs[0].targets["R3"]
w1 = np.full(N, 1 / N)
put(f"R6 first {fl(w6, 4)}; shares - 1/5 max |diff| {bound(float(np.abs(shares(w6, S0) - 0.2).max()))}; vol "
    f"{f(100 * vol(w6, S0), 2)}%")                                                                            # 10
put(f"R7 first {fl(w7, 4)}; shares {fl(100 * shares(w7, S0), 1)}%; vol {f(100 * vol(w7, S0), 2)}%")          # 11
wmv = np.linalg.solve(S0, np.ones(N))
wmv /= wmv.sum()
put(f"echo: R1's first-window shares (LM27's A27-21) {fl(100 * shares(w1, S0), 1)}%, R1's vol (LM28's A28-15) "
    f"{f(100 * vol(w1, S0), 2)}%; R3 (LM28's A28-10) {fl(w3, 4)}, vol {f(100 * vol(w3, S0), 2)}%, equal to (28.2)'s "
    f"unconstrained w_mv on this window (max diff {bound(float(np.abs(wmv - w3).max()), 1e-12)}); order R3 <= R6 <= R1: "
    f"{vol(w3, S0) <= vol(w6, S0) <= vol(w1, S0)}")                                                        # 12
held3 = w3 > 1e-6
put(f"R3 (minimum variance; weights LM28's A28-10): max |share - weight| {bound(float(np.abs(shares(w3, S0) - w3).max()))}; "
    f"(S w)_i / w'S w on held funds {fl(((S0 @ w3) / float(w3 @ S0 @ w3))[held3], 6)}; 00679B weight = share "
    f"{f(100 * w3[J['00679B']], 1)}%; R6's 00679B weight {f(100 * w6[J['00679B']], 1)}%, share 20%")       # 13
b5 = np.full(N, 1 / N)
w_n, it_n = newton_steps(S0, b5)
w_c, it_c = ccd(S0, b5)
w_j, it_j = jacobi(S0, b5)
fails = 0
for _, _, rw in sch:
    fails += jacobi(A * cov0(fr.X[rw - WINDOW:rw]), b5)[1] < 0
gap6 = next(line for line in log_ if line.startswith("largest gap")).split("R6 ")[-1]
put(f"R6 first window (annualized S): Newton {it_n} steps (diff to R6 {bound(float(np.abs(w_n - w6).max()))}); CCD "
    f"{it_c} sweeps (diff {np.abs(w_c - w6).max():.1e}); Jacobi from 1/N (stopped when max |w_(k+1) - w_k| < 1e-12) "
    f"stops after {it_j} steps at {fl(w_j, 3)} "
    f"(shares {fl(shares(w_j, S0), 3)}); Jacobi does not settle in 10,000 steps at {fails} of {len(sch)} signals; "
    f"cvxpy's log form (CLARABEL, tol_gap_abs = tol_gap_rel = tol_feas = {ERC_OPTS['tol_feas']:.0e}) against Newton, "
    f"largest weight gap over the signals {gap6} (vol5_rules), inside the conic cross-check's tolerance "
    f"{ERC_CHECK_TOL:.0e}")                                                                                  # 14
put(f"scale: ERC on daily S minus ERC on annualized S, max |diff| {bound(float(np.abs(erc(S0 / A) - w6).max()))}")  # 15
four = [J["0050"], J["00646"], J["00679B"], J["00635U"]]
S4 = S0[np.ix_(four, four)]
b4 = np.array([0.4, 0.2, 0.3, 0.1])
w_rb, it_rb = ccd(S4, b4)
w_mv4 = minvar(S4, "four funds")
yv = cp.Variable(4)
prob = cp.Problem(cp.Minimize(0.5 * cp.quad_form(yv, cp.psd_wrap(S4)) - b4 @ cp.log(yv)))
prob.solve(solver=cp.CLARABEL, **ERC_OPTS)
assert prob.status == "optimal" and yv.value is not None
w_cvx = np.asarray(yv.value, dtype=float)
w_cvx = w_cvx / w_cvx.sum()
assert np.abs(w_cvx - w_rb).max() < ERC_CHECK_TOL
put(f"budgets (0.4, 0.2, 0.3, 0.1) on 0050, 00646, 00679B, 00635U: weights {fl(w_rb, 4)} ({it_rb} CCD sweeps; cvxpy "
    f"CLARABEL, the ERC options, diff {np.abs(w_cvx - w_rb).max():.1e}); shares {fl(shares(w_rb, S4), 4)}; vols: "
    f"minimum variance of the four funds {f(100 * vol(w_mv4, S4), 3)}% (not R3, which holds five), budgets "
    f"{f(100 * vol(w_rb, S4), 3)}%, R2 (weights = budgets; echo of LM30's A30-24) {f(100 * vol(b4, S4), 3)}%; "
    f"R2's first-window risk shares (LM31's, decision A4) {fl(100 * shares(b4, S4), 1)}%")                 # 16

# ---------------------------------------------------------------- HRP by hand
three = [J["0050"], J["00646"], J["00679B"]]
x3 = x0[:, three]
S3 = S0[np.ix_(three, three)]
d3, dd3 = dist(x3)
Z3 = link(dd3)
o3 = quasi_diag(Z3, 3)
w3h, st3 = bisect(o3, S3)
assert np.abs(w3h - hrp(x3, S3)).max() < 1e-15
put(f"HRP 0050, 00646, 00679B: rho {f(C0[0, 1], 2)}, {f(C0[0, 2], 2)}, {f(C0[1, 2], 2)}; d12 {f(d3[0, 1], 3)} d13 "
    f"{f(d3[0, 2], 3)} d23 {f(d3[1, 2], 3)}; column distances {f(dd3[0, 1], 3)}, {f(dd3[0, 2], 3)}, {f(dd3[1, 2], 3)}; "
    f"merges {f(Z3[0, 2], 3)} then {f(Z3[1, 2], 3)}; order {[funds[three[i]] for i in o3]}; splits "
    + "; ".join(f"{[funds[three[i]] for i in a]} | {[funds[three[i]] for i in b]}: variances {f(1e4 * va, 2)}, "
                f"{f(1e4 * vb, 2)} (%^2 a year), left share {f(vb / (va + vb), 4)}, right share "
                f"{f(va / (va + vb), 4)}" for a, b, va, vb in st3)
    + f"; weights {fl(w3h, 4)}; squares of A31-07's two-decimal volatilities (0050, 00679B), not the variances: "
    + ", ".join(f(float(f"{100 * sqrt(S2[i, i]):.2f}") ** 2, 2) for i in range(2)))                         # 17
d5, dd5 = dist(x0)
Z5 = link(dd5)
o5 = quasi_diag(Z5, N)
w5h, st5 = bisect(o5, S0)
assert np.abs(w5h - w7).max() < 1e-15
put(f"R7 first window: d(0050, 00646) {f(d5[0, 1], 4)}, LM8's sqrt(2(1 - rho)) {f(sqrt(2 * (1 - C0[0, 1])), 4)} "
    f"(ratio {sqrt(2 * (1 - C0[0, 1])) / d5[0, 1]:.12f}); merges "
    + ", ".join(f"{int(a)}+{int(b)} at {f(h, 4)}" for a, b, h, _ in Z5)
    + f" (items 0-4 = {funds}, 5+ = clusters); order {[funds[i] for i in o5]}; splits "
    + "; ".join(f"{[funds[i] for i in a]} | {[funds[i] for i in b]}: left share {f(vb / (va + vb), 4)}"
                for a, b, va, vb in st5)
    + f"; weights {fl(w5h, 4)} = R7")                                                                      # 18
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    same_obs = all(np.allclose(np.asarray(linkage(dist(fr.X[rw - WINDOW:rw])[0], method="single")),
                               link(dist(fr.X[rw - WINDOW:rw])[1]), rtol=0, atol=1e-12) for _, _, rw in sch)
    du, ddu = dist(u.X)
    same_u = np.allclose(np.asarray(linkage(du, method="single")), link(ddu), rtol=0, atol=1e-12)
put(f"the author's code (SciPy linkage on the square matrix d, read as observations) gives the column-distance tree: "
    f"all {len(sch)} E5 windows {same_obs}; U28 {same_u}")                                                  # 19
diff_order = 0
wdiff, wdiff_at = 0.0, ""
for k, (sg, _, rw) in enumerate(sch):
    xx = fr.X[rw - WINDOW:rw]
    dd, dd2 = dist(xx)
    if leaves_list(link(dd)).tolist() != leaves_list(link(dd2)).tolist():
        diff_order += 1
    gap = float(np.abs(hrp_on_d(xx, A * cov0(xx)) - sigs[k].targets["R7"]).max())
    if gap > wdiff:
        wdiff, wdiff_at = gap, sg
Zu, Zud = link(ddu), link(du)
put(f"linked on d directly: leaf order differs at {diff_order} of {len(sch)} E5 signals; largest weight difference "
    f"{f(wdiff, 3)} ({wdiff_at}); U28 order differs {leaves_list(Zu).tolist() != leaves_list(Zud).tolist()}")  # 20
Zu8 = link(2 * du)
ok8 = all(np.allclose(link(2 * dist(fr.X[rw - WINDOW:rw])[0])[:, :2], link(dist(fr.X[rw - WINDOW:rw])[0])[:, :2])
          for _, _, rw in sch)
put(f"LM8's distance 2 d: same single-linkage merges as d, heights x2: U28 "
    f"{np.array_equal(Zu8[:, :2], Zud[:, :2]) and np.allclose(Zu8[:, 2], 2 * Zud[:, 2])}; E5 windows {ok8}")  # 21
Su = cov0(u.X)
wu_h = hrp(u.X, Su)
ou = quasi_diag(Zu, 28)
wu_e = erc(u.A * Su)
vu = np.sqrt(np.diag(Su))
wu_iv = (1 / vu) / float((1 / vu).sum())
wu_1 = np.full(28, 1 / 28)
nm = u.names
first = (nm[int(Zu[0, 0])], nm[int(Zu[0, 1])])
Cu = np.corrcoef(u.X, rowvar=False)
off = Cu[~np.eye(28, dtype=bool)]
put(f"U28 full sample: {len(off) // 2} correlations {f(off.min(), 3)} to {f(off.max(), 3)} (all positive "
    f"{bool(off.min() > 0)}); "
    f"first merge {first} at {f(Zu[0, 2], 3, 4)}, root at {f(Zu[-1, 2], 3, 4)}; HRP order "
    f"{[nm[i] for i in ou]}; HRP weights {f(100 * wu_h.max(), 2)}% ({nm[int(wu_h.argmax())]}) to "
    f"{f(100 * wu_h.min(), 2)}% ({nm[int(wu_h.argmin())]}); ERC {f(100 * wu_e.max(), 2)}% "
    f"({nm[int(wu_e.argmax())]}) to {f(100 * wu_e.min(), 2)}% ({nm[int(wu_e.argmin())]}); vols (A {f(u.A, 2)}): 1/N "
    f"{f(100 * sqrt(u.A) * vol(wu_1, Su), 2)}% (lm10.md:36), IV {f(100 * sqrt(u.A) * vol(wu_iv, Su), 2)}%, ERC "
    f"{f(100 * sqrt(u.A) * vol(wu_e, Su), 2)}%, HRP {f(100 * sqrt(u.A) * vol(wu_h, Su), 2)}%")                # 22
S1u, S2u = cov0(u.X[:H]), cov0(u.X[H:])
v1u = np.sqrt(np.diag(S1u))
halves = {"IV": (1 / v1u) / float((1 / v1u).sum()), "ERC": erc(u.A * S1u), "HRP": hrp(u.X[:H], S1u)}
mv_s = np.linalg.solve(S1u, np.ones(28))
echo30 = {"1/N": wu_1, "long-only minimum variance": minvar(u.A * S1u, "U28 first half"),
          "sample minimum variance": mv_s / mv_s.sum()}


def inout(w: Vec) -> str:
    return f"in {f(100 * sqrt(u.A) * vol(w, S1u), 2)}% out {f(100 * sqrt(u.A) * vol(w, S2u), 2)}%"


put("U28 halves, first-half weights held constant (LM31's): " + "; ".join(f"{k} {inout(w)}" for k, w in halves.items())
    + "; echo of LM30's A30-19: " + "; ".join(f"{k} {inout(w)}" for k, w in echo30.items()))                # 23

# ---------------------------------------------------------------- R6 and R7 in the through case
W6 = np.array([s.targets["R6"] for s in sigs])
W7 = np.array([s.targets["R7"] for s in sigs])
put(f"R6 over {len(sigs)} signals: mean {fl(W6.mean(0), 3)}, min {fl(W6.min(0), 3)}, max {fl(W6.max(0), 3)}")  # 24
sh7 = np.array([shares(W7[k], A * cov0(fr.X[rw - WINDOW:rw])) for k, (_, _, rw) in enumerate(sch)])
put(f"R7: mean {fl(W7.mean(0), 3)}, min {fl(W7.min(0), 3)}, max {fl(W7.max(0), 3)}; ex-ante shares mean "
    f"{fl(sh7.mean(0), 3)}, min {fl(sh7.min(0), 3)}, max {fl(sh7.max(0), 3)}")                              # 25
i_oos = next(i for i, d in enumerate(est) if d > sigs[0].trade)
So = A * cov0(fr.X[i_oos:])
sh_post = shares(W6.mean(0), So)
monthly = []
for k in range(len(sigs) - 1):
    a = next(i for i, d in enumerate(est) if d > sigs[k].trade)
    b = next(i for i, d in enumerate(est) if d > sigs[k + 1].trade)
    monthly.append(shares(sigs[k].targets["R6"], cov0(fr.X[a:b])))
mon = np.array(monthly)
q10, q90 = (np.quantile(mon, q, axis=0, method="inverted_cdf") for q in (0.1, 0.9))
put(f"R6 ex post: the mean of R6's {len(W6)} target weights (A31-24's means) on the covariance of {len(est) - i_oos} "
    f"estimation rows {est[i_oos]} -> {est[-1]}: "
    f"shares {fl(100 * sh_post, 1)}%; holding month by holding month ({len(mon)} holding months, each holding month's "
    f"own R6 target weights on that holding month's covariance) 10% quantile "
    f"{fl(100 * q10, 1)}%, 90% {fl(100 * q90, 1)}%; holding months with a negative share "
    f"{int((mon.min(1) < -EPS).sum())}")                                                                   # 26
summ = {k: summary(fr, p) for k, p in paths.items()}
put(f"realized volatility out of sample (summary, net, sqrt A_w, {p8.dates[1]} -> {p8.dates[-1]}): " + ", ".join(
    f"{k} {f(100 * float(summ[k]['vol']), 2)}%" for k in ("R6", "R7", "R8"))
    + "; echo of LM30's A30-12: " + ", ".join(f"{k} {f(100 * float(summ[k]['vol']), 2)}%"
                                               for k in ("R1", "R3", "R5")))                                # 27

# ---------------------------------------------------------------- R8
sbar, sfc, Ls = [], [], []
for (_, _, rw), s in zip(sch, sigs, strict=True):
    p = fr.X[rw - WINDOW:rw] @ s.targets["R6"]
    sb2 = float(np.mean(p**2))
    s2 = ewma(p, sb2)
    sbar.append(sqrt(sb2))
    sfc.append(sqrt(s2))
    Ls.append(min(CAP, sqrt(sb2 / s2)))
sb, sf, L = np.array(sbar), np.array(sfc), np.array(Ls)
assert np.abs(L - np.array([s.targets["R8"].sum() for s in sigs])).max() < 1e-15
put(f"R8 first signal: sigma_bar {f(sb[0], 7)}/day = {f(100 * sqrt(A) * sb[0], 2)}%, EWMA {f(sf[0], 7)}/day = "
    f"{f(100 * sqrt(A) * sf[0], 2)}%; L {f(L[0], 2, 3, 4)}; R8 exposures {fl(sigs[0].targets['R8'], 4)}, cash "
    f"{f(1 - L[0], 3)}")                                                                                        # 28
capped = [s.signal for s, v in zip(sigs, L, strict=True) if v >= CAP - EPS]
put(f"exposure path: min {f(L.min(), 3)} ({sigs[int(L.argmin())].signal}), mean {f(L.mean(), 3)}, at the cap "
    f"{len(capped)} (first {capped[0]}, last {capped[-1]}), above 1 {int((L > 1 + EPS).sum())}, below 1 "
    f"{int((L < 1 - EPS).sum())}; uncapped ratio max {f((sb / sf).max(), 2)}")                              # 29
put(f"sigma_bar (annualized) {f(100 * sqrt(A) * sb.min(), 2)}% to {f(100 * sqrt(A) * sb.max(), 2)}%, mean "
    f"{f(100 * sqrt(A) * sb.mean(), 2)}%; EWMA {f(100 * sqrt(A) * sf.min(), 2)}% "
    f"({sigs[int(sf.argmin())].signal}) to {f(100 * sqrt(A) * sf.max(), 2)}% ({sigs[int(sf.argmax())].signal})")  # 30
err = 0.0
for (_, _, rw), s in zip(sch, sigs, strict=True):
    xx = fr.X[rw - WINDOW:rw]
    w = s.targets["R6"]
    M = xx.T @ xx / len(xx)
    Sig = M.copy()
    for r in xx:
        Sig = LAM * Sig + (1 - LAM) * np.outer(r, r)
    pp = xx @ w
    err = max(err, abs(float(w @ Sig @ w) - ewma(pp, float(np.mean(pp**2)))) / float(np.mean(pp**2)))
put(f"EWMA matrix started at the window's uncentred second moments: w'Sigma_(t+1|t) w equals the portfolio EWMA, "
    f"largest difference over the signals divided by sigma_bar^2 {bound(err, 1e-14)} (to rounding)")        # 31
k25 = [s.signal for s in sigs].index("2025-03-31")
_, _, rw25 = sch[k25]
w25 = sigs[k25].targets["R6"]
p25 = fr.X[rw25 - WINDOW:rw25] @ w25
sb25 = float(np.mean(p25**2))
s225 = ewma(p25, sb25)
track = []
j = rw25
while est[j] <= "2025-04-09":
    s225 = LAM * s225 + (1 - LAM) * float(fr.X[j] @ w25) ** 2
    track.append(f"{est[j]} EWMA {f(100 * sqrt(A * s225), 2)}%, implied L {f(min(CAP, sqrt(sb25 / s225)), 2)}")
    j += 1
put(f"2025-03-31 (trade {sigs[k25].trade}): R6 {fl(w25, 3)}; sigma_bar {f(100 * sqrt(A) * sb[k25], 2)}%, EWMA "
    f"{f(100 * sqrt(A) * sf[k25], 2)}%, L {f(L[k25], 3, 2)} (borrowed {f(L[k25] - 1, 3, 2)}); continued daily on "
    f"R6's constant-weight returns: "
    + "; ".join(track) + f"; next trade {sigs[k25 + 1].trade} at L {f(L[k25 + 1], 3, 2)}")                 # 32
k20 = [s.signal for s in sigs].index("2020-02-27")
put("2020: " + "; ".join(f"{sigs[k].signal} (trade {sigs[k].trade}) L {f(L[k], 3)}, EWMA "
                         f"{f(100 * sqrt(A) * sf[k], 2)}%, sigma_bar {f(100 * sqrt(A) * sb[k], 2)}%"
                         for k in (k20, k20 + 1, k20 + 2)))                                                  # 33
ratio = {}
vmon = {}
for k in ("R6", "R8"):
    p = paths[k]
    r = p.wealth[1:] / p.wealth[:-1] - 1
    ii = [p.dates.index(t) for t in trades]
    rms = np.array([sqrt(float(np.mean(r[ii[m]:ii[m + 1]] ** 2))) for m in range(len(ii) - 1)])
    vmon[k] = rms**2
    ratio[k] = rms / sb[:-1]


def month(m: int) -> str:
    """Holding month m: the session after trade m through trade m + 1."""
    return f"holding month {p8.dates[idx[m] + 1]} -> {p8.dates[idx[m + 1]]}"


cells = []
for k in ("R6", "R8"):
    q = ratio[k]
    lq = np.log(q)
    top = int(q.argmax())
    cells.append(f"{k}: median {f(float(np.quantile(q, 0.5, method='inverted_cdf')), 2, 3)}, mean {f(q.mean(), 2)}, "
                 f"SD of ln (divisor {len(q)}) {f(lq.std(), 3)}, above 1.5 {int((q > 1.5 + EPS).sum())}, below 2/3 "
                 f"{int((q < 2 / 3 - EPS).sum())}, min {f(q.min(), 2)}, max {f(q.max(), 2)} ({month(top)})")
crash = [trades.index(t) for t in ("2020-03-02", "2025-04-01")]
cells += [f"{month(m)} (trade {trades[m]}): target {sb[m]:.9f}/day = {f(100 * sqrt(A) * sb[m], 2)}%; " + ", ".join(
    f"{k} ratio {f(ratio[k][m], 2)}, RMS {sqrt(vmon[k][m]):.8f}/day = {f(100 * sqrt(A * vmon[k][m]), 1)}% "
    f"annualized with the target's A (with A_w {100 * sqrt(Aw * vmon[k][m]):.4f}%)" for k in ("R6", "R8"))
    for m in crash]
put(f"{len(ratio['R6'])} complete holding months, realized RMS / sigma_bar (daily units): " + "; ".join(cells))  # 34
V6 = vmon["R6"]
loss = {nmq: V6 / F - np.log(V6 / F) - 1 for nmq, F in (("window", sb[:-1] ** 2), ("EWMA", sf[:-1] ** 2))}
wins = int((loss["window"] < loss["EWMA"]).sum())
wins_e = int((loss["EWMA"] < loss["window"]).sum())
big = np.argsort(loss["EWMA"])[::-1][:2]
gq = loss["EWMA"] - loss["window"]  # above 0: the EWMA loses the holding month; below 0: it wins it
won, lost = gq < 0, gq > 0
assert int(won.sum()) == wins_e and int(lost.sum()) == wins
worst, best = int(gq.argmax()), int(gq.argmin())
put(f"QLIKE of R6's holding month ({len(V6)} months): mean window {f(loss['window'].mean(), 3)}, EWMA "
    f"{f(loss['EWMA'].mean(), 3)}; median window {f(float(np.quantile(loss['window'], 0.5, method='inverted_cdf')), 3)}, "
    f"EWMA {f(float(np.quantile(loss['EWMA'], 0.5, method='inverted_cdf')), 3)}; the window's QLIKE is lower in {wins} "
    f"months, the EWMA's in {wins_e}; the EWMA's {wins_e} wins gain {f(float(-gq[won].sum()), 2)} in all (mean "
    f"{f(float(-gq[won].mean()), 3)}), its {wins} losses cost {f(float(gq[lost].sum()), 2)} (mean "
    f"{f(float(gq[lost].mean()), 3)}); costs minus gains {f(float(gq.sum()), 2)} = {len(gq)} x the gap in means "
    f"{f(float(gq.mean()), 3)}; largest loss {f(float(gq[worst]), 1)} ({month(worst)}), largest win "
    f"{f(float(-gq[best]), 2)} ({month(best)}); the EWMA's two largest QLIKE values " + ", ".join(
        f"{f(loss['EWMA'][m], 2)} ({month(int(m))}; window {f(loss['window'][m], 2)})" for m in big)
    + f"; without the largest loss's month only, means window {f(float(np.delete(loss['window'], worst).mean()), 3)}, "
    f"EWMA {f(float(np.delete(loss['EWMA'], worst).mean()), 3)}; without the months of the two largest QLIKE values, "
    f"means window {f(float(np.delete(loss['window'], big).mean()), 3)}, EWMA "
    f"{f(float(np.delete(loss['EWMA'], big).mean()), 3)}; corr(ln EWMA/sigma_bar, ln realized/sigma_bar) "
    f"{f(float(np.corrcoef(np.log(sf[:-1] / sb[:-1]), np.log(ratio['R6']))[0, 1]), 2)}")                     # 35
to8 = np.array([t.turnover for t in p8.trades[1:]])
put(f"R8's trades (decision A2; annual turnover of every rule is LM34's, A34-06): one-way turnover per trade over the "
    f"{len(to8)} trades after the first purchase, mean {f(100 * to8.mean(), 1)}%, largest {f(100 * to8.max(), 1)}% "
    f"({p8.trades[1 + int(to8.argmax())].trade})")                                                          # 36
r8 = p8.wealth[1:] / p8.wealth[:-1]
put(f"R8 domain check: 1 + R_t > 0 on all {len(r8)} sessions: {bool((r8 > 0).all())}; ruin {p8.ruin} (the worst day "
    f"is LM35's); rates: cash {RF}, borrowing {RF + SPREAD} a year, accrued per session at /A_w")             # 37
put(f"half-lives: lambda {LAM} -> {f(log(0.5) / log(LAM), 1)} days (lm26.md:113); a 20-day half-life -> lambda "
    f"{f(0.5 ** (1 / 20), 4)}; the start value's weight after the {WINDOW} window days lambda^{WINDOW} "
    f"{LAM ** WINDOW:.2e}")                                                                                    # 38
wid = [J["0050"], J["00679B"], J["00642U"]]
Sw = S0[np.ix_(wid, wid)]
vw = np.sqrt(np.diag(Sw))
Cw = Sw / np.outer(vw, vw)
ew, itw = ccd(Sw, np.full(3, 1 / 3))
assert np.abs(ew - erc(Sw)).max() < 1e-10
jw, jit = jacobi(Sw, np.full(3, 1 / 3))
ivw = (1 / vw) / float((1 / vw).sum())
put(f"widget start (first window, 0050, 00679B, 00642U): vols {fl(100 * vw, 1)}%, corr {f(Cw[0, 1], 2)}, "
    f"{f(Cw[0, 2], 2)}, {f(Cw[1, 2], 2)}; ERC {fl(ew, 4)} ({itw} CCD sweeps), vol {f(100 * vol(ew, Sw), 2)}%; IV "
    f"{fl(ivw, 4)}, shares {fl(100 * shares(ivw, Sw), 1)}%; 1/3 each: shares "
    f"{fl(100 * shares(np.full(3, 1 / 3), Sw), 1)}%; Jacobi from 1/3 (annualized S; stopped when max |w_(k+1) - w_k| "
    f"< 1e-12): "
    + (f"settles after {jit} steps at {fl(jw, 1)} (shares {fl(shares(jw, Sw), 3)}), not ERC" if jit > 0
       else "does not settle in 10,000 steps"))                                                              # 39

# ---------------------------------------------------------------- problems
Sp = np.array([[0.04, 0.5 * 0.2 * 0.1], [0.5 * 0.2 * 0.1, 0.01]])
put(f"P1 (20%, 10%, rho 0.5): ERC {fl(erc(Sp), 4)}; inverse variance {f(0.25 / 1.25, 4)}; equal 0.5")        # 40
wp = np.array([0.5, 0.5])
put(f"P2 (20%, 10%, rho 0.5): the budget b1 for which 50/50 solves (31.1) = fund 1's share at 50/50 "
    f"{f(shares(wp, Sp)[0], 3)}; CCD with that budget {fl(ccd(Sp, shares(wp, Sp))[0], 4)}; distractors: "
    f"w s / sum w s {f(0.1 / 0.15, 3)}, variance terms {f(0.25 * 0.04 / (0.25 * 0.04 + 0.25 * 0.01), 3)}")   # 41
v3 = np.array([0.1, 0.2, 0.4])
C3 = 0.7 * np.eye(3) + 0.3 * np.ones((3, 3))
e3 = erc(np.outer(v3, v3) * C3)
put(f"P3 (vols 10, 20, 40%, rho 0.3): ERC {fl(e3, 4)} (4/7, 2/7, 1/7 = {f(4 / 7, 4)}, {f(2 / 7, 4)}, {f(1 / 7, 4)}); "
    f"inverse variance on the 40% asset {f((1 / 16) / (1 + 1 / 4 + 1 / 16), 4)}; equal {f(1 / 3, 4)}")        # 42
S5p = np.diag([0.04, 0.01])
w5p, _ = ccd(S5p, np.array([0.7, 0.3]))
w5c = (sqrt(0.7) / 0.2) / (sqrt(0.7) / 0.2 + sqrt(0.3) / 0.1)
put(f"P5 (rho 0, vols 20%, 10%, budgets 0.7, 0.3): w1 = (sqrt(.7)/.2) / (sqrt(.7)/.2 + sqrt(.3)/.1) {f(w5c, 4)}; CCD "
    f"{fl(w5p, 4)}; shares {fl(shares(w5p, S5p), 4)}; IV {f(0.1 / 0.3, 4)}")                                  # 43
Cp = np.array([[1.0, 0.8, 0.1], [0.8, 1.0, 0.2], [0.1, 0.2, 1.0]])
vp = np.array([0.20, 0.25, 0.10])
dp = np.sqrt((1 - Cp) / 2)
np.fill_diagonal(dp, 0.0)
ddp = np.sqrt(((dp[:, :, None] - dp[:, None, :]) ** 2).sum(axis=0))
Zp = link((ddp + ddp.T) / 2)
op = quasi_diag(Zp, 3)
Spp = np.outer(vp, vp) * Cp
wpp, stp = bisect(op, Spp)
put(f"P6 (rho12 0.8, rho13 0.1, rho23 0.2; vols 20, 25, 10%): d {f(dp[0, 1], 4)}, {f(dp[0, 2], 4)}, {f(dp[1, 2], 4)}; "
    f"column distances {f(ddp[0, 1], 4)}, {f(ddp[0, 2], 4)}, {f(ddp[1, 2], 4)}; merges {f(Zp[0, 2], 4)}, "
    f"{f(Zp[1, 2], 4)}; order {[int(i) + 1 for i in op]}; splits "
    + "; ".join(f"{[int(i) + 1 for i in a]}|{[int(i) + 1 for i in b]} left share {f(vb / (va + vb), 4)}"
                for a, b, va, vb in stp) + f"; weights {fl(wpp, 4)}")                                       # 44
Awp = 243.57
lp = [min(1.5, 0.08 / 0.05), min(1.5, 0.08 / 0.16)]
book = [lp[0] * -0.03 - (lp[0] - 1) * (RF + SPREAD) / Awp, lp[1] * -0.03 + (1 - lp[1]) * RF / Awp]
put(f"P8 (sigma_bar 8%, forecasts 5% and 16%, A_w 243.57, fund book -3%): L {f(lp[0], 2)} (uncapped "
    f"{f(0.08 / 0.05, 2)}), {f(lp[1], 2)}; book returns {f(100 * book[0], 4)}%, {f(100 * book[1], 4)}%")       # 45

# ---------------------------------------------------------------- source check (not for the text)
Cx = np.array([[1.0, 0.7, 0.2], [0.7, 1.0, -0.2], [0.2, -0.2, 1.0]])
dx = np.sqrt((1 - Cx) / 2)
np.fill_diagonal(dx, 0.0)
ddx = np.sqrt(((dx[:, :, None] - dx[:, None, :]) ** 2).sum(axis=0))
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    Zx = np.asarray(linkage(dx, method="single"), dtype=np.float64)
put(f"Lopez de Prado (2016), Examples 1-2 (rho12 0.7, rho13 0.2, rho23 -0.2): d {f(dx[0, 1], 4)}, {f(dx[0, 2], 4)}, "
    f"{f(dx[1, 2], 4)}; column distances {f(ddx[0, 1], 4)}, {f(ddx[0, 2], 4)}, {f(ddx[1, 2], 4)}; SciPy on the square "
    f"matrix (rows read as observations): first merge {int(Zx[0, 0]) + 1}+{int(Zx[0, 1]) + 1} at {f(Zx[0, 2], 4)}")  # 46

print("\n".join(OUT))
