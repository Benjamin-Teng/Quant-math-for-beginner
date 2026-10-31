"""LM29 anchors (Convex Optimization in Practice): every number the Stage 1 brief quotes (drafted 2026-10-24; revised
the same day to the editor's decisions on the briefs, and again to the decisions on the first revision and on the
second recomputation and cross-check, plans/vol-5.md). The fresh check of the whole of Stage 1 (2026-10-31) adds A29-35
(R4 and problem 11's 2-point optimum at r_f = 0 and 2%, the shared decision "Risk-free rate"), prints R3's variance
lambda / 2 in A29-12, the 70 tangency windows in A29-07, both Problem.value and Variable.value in A29-18 and SciPy's
version in A29-22, flags the volatility given up (bp) at its shown fourth decimal in A29-21, and names R4's equality
e'y = 1 (not "the budget") in A29-25, A29-26 and A29-34 and sigma_p^2 in A29-28; no earlier value changes.

Reads only data/processed/*.parquet, through the shared builders (run them first; this script runs neither):
  * E5 (plans/vol-5.md, "Data"): data/vol5_series.py's frames("E5"), which reads data/processed/vol5_frames.parquet:
    the estimation frame (dates on which every fund has a one-session total return; T = 2,362, A = T / years) and the
    wealth frame (every TR23 session after the base close 2017-01-17; a halted fund earns 0; A_w = sessions / years);
    years are calendar days / 365.25 from the close before the first return (2017-01-17) to the last close (AUTHORING
    section 8). LM27 owns these counts (A27-02, A27-03); A29-01 reprints them.
    The funds, in this order: 0050, 00646, 00679B, 00635U, 00642U.
  * The through case: data/vol5_rules.py's schedule(), WINDOW (504 estimation rows through each month-end signal), RF
    (1.5% a year), the cost model (COMMISSION 0.1425% on both sides, TAX on sales: 0.1%, 0 for 00679B), and the exact
    long-only solvers minvar() (R3) and maxsharpe() (R4, the homogenized QP), which this script calls; no rule is
    re-implemented. R3's and R4's weights are LM29's numbers (it defines their through-case form); no statistic of a
    rule's wealth path (growth, Sharpe ratio, volatility, drawdown, turnover, costs) is computed here.
  * U28 (Volume II): data/lm10_series.py's u28() (28 TWSE sector price indices, T = 4,382 daily price returns
    2008-12-02 .. 2026-10-08, A = 245.4794; halves of 2,191 returns, LM11's), covariance only.

Conventions. Every optimization uses a window's annualized plug-in inputs, as the through case does: Sigma = A * cov0
(vol5_rules.cov0: Xc' Xc / T from the window's centred daily returns Xc, in that order, LM10's (10.2); np.cov would
change a solver gap's digits beyond the second significant one) and e = A * (window mean) - r_f, with E5's estimation-frame A (U28's own A for U28). They are
in-sample estimates treated as known; every in-sample Sharpe ratio and volatility below is on its window's inputs, not
a realized statistic. A weight with |w| < 1e-6 is 0 and prints as 0; a constraint is active when its slack is below
1e-6. Solvers: cvxpy (fresh Problem every time, no warm start) with the book's tolerances (vol5_rules.OSQP_OPTS: OSQP
eps_abs = eps_rel = 1e-10, polishing; vol5_rules.CLARABEL_OPTS: CLARABEL tol_gap_abs = tol_gap_rel = tol_feas = 1e-12)
unless the line says "default"; every printed solution is checked by a closed form or the exact NNLS solution, or by a
second solver, and the script stops if a check fails. Multipliers follow LM7's signs written for a minimization
(the brief's (29.4)): grad h = lambda (budget) + nu (lower bounds) - nu_cap (caps), nu >= 0; cvxpy's dual of the
budget constraint is printed as cvxpy reports it. Drifted weights at a signal: the previous target set at its trade's
close, grown by each fund's wealth-frame returns through the signal's close, normalized. Planned turnover at a signal
is 1/2 |f - w_drift|_1 and planned cost 0.1425% |f - w_drift|_1 + sum tax_i max(0, w_drift,i - f_i), both as fractions
of pre-trade wealth at the signal close (the through case trades a session later; LM34 owns the executed figures and
every rule's annual turnover, so the cost sweep prints its planned totals relative to theta = 0). The cost-penalized
QP is given to cvxpy as LM27's cost function, COMMISSION * norm1(w - w_drift) + tax' pos(w_drift - w) (its KKT check
splits buys and sells; solver gaps depend on the formulation).

Rounding flags. Every number the brief prints passes through f(x, k1, k2, ...), which shows x with max(k) + 3 decimals
and flags it "NEAR" for each printed precision k at which x lies within a tenth of a last-digit unit of a rounding
boundary (|frac(10^k |x|) - 0.5| < 0.1), or through ef(x, k...), the same for the mantissa of e-notation; f's keyword
also=(k, ...) flags further precisions without showing more digits (A29-21 flags its shown fourth decimal). The brief
prints a flagged value as rounded from the unrounded value here; a cell at rounding level is printed as a bound.
Weights pass through pc() (percent). Numbers printed by earlier modules are echoed with file:line or their anchor ID.

Prints one line per anchor, "A29-NN <value>", in ID order, and writes nothing.

Run:  PYTHONUTF8=1 uv run python data/vol5_anchors_lm29.py
"""
import inspect
import itertools
import re
import sys
import warnings
from importlib import import_module
from importlib.metadata import version
from math import floor, log10, sqrt
from pathlib import Path
from typing import SupportsFloat

import cvxpy as cp
import numpy as np
from numpy.typing import NDArray

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lm10_series import u28
from vol5_rules import (
    CLARABEL_OPTS,
    COMMISSION,
    ERC_OPTS,
    OSQP_OPTS,
    RF,
    SPREAD,
    TAX,
    WINDOW,
    cov0,
    maxsharpe,
    minvar,
    schedule,
)
from vol5_series import frames

Vec = NDArray[np.float64]
Mat = NDArray[np.float64]
ZERO = 1e-6
EPS = 1e-12

OUT: list[str] = []
NEAR: list[str] = []


def put(value: str) -> None:
    """One anchor line; values that f() found near a rounding boundary are listed at its end."""
    tail = f" [NEAR a rounding boundary: {'; '.join(NEAR)}]" if NEAR else ""
    OUT.append(f"A29-{len(OUT) + 1:02d} {value}{tail}")
    NEAR.clear()


def f(x: SupportsFloat, *ks: int, plus: bool = False, also: tuple[int, ...] = ()) -> str:
    """x with max(ks) + 3 decimals; flagged for each printed precision k (and each k in also) within 0.1 of a
    last-digit unit of a boundary."""
    x = float(x)
    for k in (*ks, *also):
        u = abs(x) * 10**k
        if abs(u - floor(u) - 0.5) < 0.1:
            NEAR.append(f"{x:.{k + 3}f} at {k} dp")
    return f"{x:{'+' if plus else ''}.{max(ks) + 3}f}"


def ef(x: SupportsFloat, *ks: int) -> str:
    """x in e-notation with max(ks) + 3 mantissa decimals; flagged as f() does, for k decimals of the mantissa."""
    x = float(x)
    if x == 0:
        return "0"
    m = abs(x) / 10 ** floor(log10(abs(x)))
    for k in ks:
        u = m * 10**k
        if abs(u - floor(u) - 0.5) < 0.1:
            NEAR.append(f"{x:.{k + 3}e} at {k} mantissa dp")
    return f"{x:.{max(ks) + 3}e}"


def stop(msg: str) -> None:
    sys.exit(f"vol5_anchors_lm29: CHECK FAILED: {msg}")


fr = frames("E5")
FUNDS = fr.funds
N = len(FUNDS)
A = fr.A
WD = fr.wealth_dates
SCH = schedule(fr)
TAXV = np.array([TAX[s] for s in FUNDS])
ONE = np.ones(N)


def pc(w: Vec, *ks: int) -> str:
    """Weights in percent, fund by fund; |w| < 1e-6 prints as 0."""
    return ", ".join(f"{s} {'0' if abs(v) < ZERO else f(100 * v, *ks)}" for s, v in zip(FUNDS, w, strict=True))


def window(k: int) -> tuple[str, str, Mat, list[str]]:
    sg, tr, rows = SCH[k]
    return sg, tr, fr.X[rows - WINDOW:rows], fr.est_dates[rows - WINDOW:rows]


def inputs(x: Mat) -> tuple[Mat, Vec, Vec]:
    S = A * cov0(x)
    mu = A * x.mean(axis=0)
    return S, mu, mu - RF


def sr(w: Vec, S: Mat, e: Vec) -> float:
    return float(w @ e / np.sqrt(w @ S @ w))


def vol(w: Vec, S: Mat) -> float:
    return float(np.sqrt(w @ S @ w))


def tangency(S: Mat, e: Vec) -> tuple[Vec, float]:
    """LM28's unconstrained tangency weights S^-1 e / 1'S^-1 e, and 1'S^-1 e."""
    z = np.linalg.solve(S, e)
    return z / z.sum(), float(z.sum())


def solve(obj: cp.Expression, cons: list, solver: str, opts: dict | None = None,
          sense: str = "min") -> tuple[cp.Problem, Vec | None]:
    """A fresh Problem; returns it and the first variable's value (None unless optimal)."""
    p = cp.Problem(cp.Minimize(obj) if sense == "min" else cp.Maximize(obj), cons)
    p.solve(solver=solver, **({} if opts is None else opts))
    var = p.variables()[0]
    v = var.value
    if p.status != "optimal" or v is None:
        return p, None
    return p, np.asarray(v, dtype=np.float64)


def must(v: Vec | None, label: str) -> Vec:
    if v is None:
        stop(f"{label}: solver did not return an optimal solution")
    assert v is not None
    return v


BOOK = {"OSQP": (cp.OSQP, OSQP_OPTS), "CLARABEL": (cp.CLARABEL, CLARABEL_OPTS)}
SCS_OPTS = {"eps": 1e-9, "max_iters": 200000}      # problem 11's second solver; cvxpy's own SCS default is eps 1e-5


def homog(S: Mat, e: Vec, extra: str = "", solver: str = "CLARABEL", lb: Vec | None = None,
          cap: float | None = None, gross: float | None = None) -> Vec:
    """Maximum Sharpe ratio by the homogenized QP: min y'Sy, e'y = 1, plus limits; returns w = y / 1'y."""
    x = cp.Variable(N)
    cons = [e @ x == 1]
    if lb is not None:
        cons.append(x >= lb)
    if cap is not None:
        cons += [x >= 0, x <= cap * cp.sum(x)]
    if gross is not None:
        cons.append(cp.norm1(x) <= gross * cp.sum(x))
    sv, op = BOOK[solver]
    _, v = solve(cp.quad_form(x, cp.psd_wrap(S)), cons, sv, op)
    v = must(v, f"homogenized {extra} {solver}")
    if v.sum() <= 0:
        stop(f"homogenized {extra}: 1'y <= 0")
    return v / v.sum()


# ---------------------------------------------------------------------------------------------------- data and windows
put(f"echo of A27-02 and A27-03 (LM27's): E5 estimation frame T = {len(fr.est_dates)} ({fr.est_dates[0]} -> "
    f"{fr.est_dates[-1]}), A = {f(A, 2, 3)}; wealth frame {len(WD)} sessions, A_w = {f(fr.A_wealth, 2)}")
sg0, tr0, x0, d0 = window(0)
sgL, trL, xL, dL = window(len(SCH) - 1)
put(f"{len(SCH)} signals; first {sg0} (trade {tr0}), window {d0[0]} -> {d0[-1]} ({len(d0)} rows) (the count and the "
    f"first window echo A28-02, LM28's); last {sgL} (trade {trL}), window {dL[0]} -> {dL[-1]} ({len(dL)} rows)")

lo_eig, kap = [], []
for k in range(len(SCH)):
    S_k = inputs(window(k)[2])[0]
    ev = np.linalg.eigvalsh(S_k)
    lo_eig.append(float(ev[0]))
    kap.append((float(ev[-1] / ev[0]), SCH[k][0]))
kmin, kmax = min(kap), max(kap)
put(f"A Sigma_hat positive definite at all {len(SCH)} windows: smallest eigenvalue {f(min(lo_eig), 4)} (annual); "
    f"condition number {f(kmin[0], 1, 2)} ({kmin[1]}) to {f(kmax[0], 1, 2)} ({kmax[1]})")

SL, muL, eL = inputs(xL)
volL = np.sqrt(np.diag(SL))
CL = SL / np.outer(volL, volL)
put("last window, annualized: mean " + ", ".join(f"{s} {f(100 * v, 1, 2, 3)}%" for s, v in zip(FUNDS, muL, strict=True))
    + "; excess e " + ", ".join(f"{s} {f(100 * v, 1, 2, 3)}%" for s, v in zip(FUNDS, eL, strict=True))
    + "; volatility " + ", ".join(f"{s} {f(100 * v, 1, 2)}%" for s, v in zip(FUNDS, volL, strict=True))
    + "; Sharpe ratio " + ", ".join(f"{s} {f(v, 2)}" for s, v in zip(FUNDS, eL / volL, strict=True))
    + f"; correlation 0050-00646 {f(CL[0, 1], 3)}")

# ---------------------------------------------------------------------------------------------------- the case
wtL, zsumL = tangency(SL, eL)
put(f"last window, unconstrained tangency (LM28's formula): {pc(wtL, 1, 2)}; gross {f(100 * np.abs(wtL).sum(), 0, 1)}%; "
    f"in-sample Sharpe ratio {f(sr(wtL, SL, eL), 2, 3)}, volatility {f(100 * vol(wtL, SL), 1, 2)}%; "
    f"1'Sigma^-1 e = {f(zsumL, 2)} > 0")
w4L = maxsharpe(SL, eL, "R4 last")
assert w4L is not None
w3L = minvar(SL, "R3 last")
put(f"last signal R4 (long-only maximum Sharpe): {pc(w4L, 1, 2)}; in-sample Sharpe ratio {f(sr(w4L, SL, eL), 2, 3)}, "
    f"volatility {f(100 * vol(w4L, SL), 1, 2)}%, mu_p - r_f {f(100 * float(w4L @ eL), 1, 2)}%; R3 (long-only minimum "
    f"variance): {pc(w3L, 1)}; volatility {f(100 * vol(w3L, SL), 2)}%, in-sample Sharpe ratio {f(sr(w3L, SL, eL), 2)}")

shorts, wrong, gross_u, held = 0, [], [], []
tan_n, tan_short = 0, 0                               # the windows with 1'Sigma^-1 e > 0, where the formula is a tangency
r4z = np.zeros(N, dtype=int)
pos_out, neg_in = 0, 0
hedges: list[tuple[str, str, float, float]] = []      # formatted after A29-07, so that f()'s flags stay on A29-08
mv_gap = 0.0
r3min = (1.0, "", "")
r3zero = 0
beta_dev = 0.0
for k in range(len(SCH)):
    sg, _, x, _ = window(k)
    S, mu, e = inputs(x)
    wt, zs = tangency(S, e)
    shorts += int(wt.min() < -ZERO)
    if zs <= 0:
        wrong.append(sg)
    else:
        tan_n += 1
        tan_short += int(wt.min() < -ZERO)
    gross_u.append(float(np.abs(wt).sum()))
    w4 = maxsharpe(S, e, f"R4 {sg}")
    assert w4 is not None
    held.append(int((w4 > ZERO).sum()))
    r4z += (w4 < ZERO).astype(int)
    pos_out += int(((e > 0) & (w4 < ZERO)).sum())
    neg_in += int(((e <= 0) & (w4 > ZERO)).sum())
    hedges += [(FUNDS[i], sg, float(w4[i]), float(e[i])) for i in range(N) if e[i] <= 0 and w4[i] > ZERO]
    mv_gap = max(mv_gap, float(np.abs(minvar(S, "x") - np.linalg.solve(S, ONE) / np.linalg.solve(S, ONE).sum()).max()))
    w3 = minvar(S, f"R3 {sg}")
    r3zero += int((w3 < ZERO).sum())
    i = int(np.argmin(w3))
    if w3[i] < r3min[0]:
        r3min = (float(w3[i]), FUNDS[i], sg)
    beta_dev = max(beta_dev, float(np.abs(S @ w3 / (w3 @ S @ w3) - 1).max()))
hist = {n: held.count(n) for n in range(1, N + 1)}
put(f"92-signal backing: LM28's formula Sigma^-1 e / 1'Sigma^-1 e has a negative weight at {shorts} of {len(SCH)} "
    f"signals (at {tan_short} of the {tan_n} where 1'Sigma^-1 e > 0 and it is the tangency; the other {len(wrong)} have "
    f"no tangency, A28-23), smallest gross exposure {f(min(gross_u), 2)}; R4 holds 1/2/3/4/5 funds at "
    f"{hist[1]}/{hist[2]}/{hist[3]}/{hist[4]}/{hist[5]} signals; echo of A28-23 and A28-24 (LM28's): 1'Sigma^-1 e <= 0 "
    f"at {len(wrong)} ({wrong[0]} .. {wrong[-1]}), largest gross {f(max(gross_u), 1)}")
put("R4 zero weights across the 92 signals: " + ", ".join(f"{s} {int(c)}" for s, c in zip(FUNDS, r4z, strict=True))
    + f"; fund-signals with e_i > 0 but w_i = 0: {pos_out}; with e_i <= 0 but w_i > 0: {neg_in} (of {N * len(SCH)}): "
    + "; ".join(f"{s} {sg} ({f(100 * wi, 1)}%, e {f(100 * ei, 2)}%)" for s, sg, wi, ei in hedges))
put(f"R3's bounds never bind on E5 (LM29 owns this, decision A5; LM28's A28-12 and LM30's A30-16 echo it): R3 zero "
    f"weights across the 92 signals: {r3zero}; smallest R3 weight {f(100 * r3min[0], 2)}% ({r3min[1]}, {r3min[2]}); "
    f"largest |beta_ip - 1| over all signals and funds {ef(beta_dev, 1)} (rounding level: the exact NNLS reference's "
    f"own rounding); largest gap between R3 and LM28's unconstrained minimum-variance weights (28.2) {ef(mv_gap, 1)}")

# ---------------------------------------------------------------------------------------------------- KKT at the last signal
xr = w4L / float(eL @ w4L)
lam4 = float(2 * xr @ SL @ xr)
nu4 = 2 * SL @ xr - lam4 * eL
b4 = SL @ w4L / float(w4L @ SL @ w4L)
ep = float(w4L @ eL)
short = b4 * ep - eL
if np.abs(nu4 / lam4 - short).max() > 1e-12 or nu4.min() < -1e-10 * lam4:
    stop("R4 KKT identity nu / lambda = beta (mu_p - r_f) - e")
put(f"R4 KKT, last signal (homogenized y = w / e'w): lambda {f(lam4, 4, 5)}; nu " + ", ".join(
    f"{s} {'0' if w > ZERO else f(v, 4, 5)}" for s, v, w in zip(FUNDS, nu4, w4L, strict=True))
    + "; beta_ip " + ", ".join(f"{s} {f(v, 3, 5)}" for s, v in zip(FUNDS, b4, strict=True))
    + f"; mu_p - r_f {f(100 * ep, 2, 3)}%; beta_ip (mu_p - r_f) " + ", ".join(
    f"{s} {f(100 * v, 2, 3)}%" for s, v in zip(FUNDS, b4 * ep, strict=True))
    + "; nu_i / lambda = beta_ip (mu_p - r_f) - e_i " + ", ".join(
    f"{s} {'0 (held)' if w > ZERO else f(100 * v, 2) + ' points'}" for s, v, w in zip(FUNDS, short, w4L, strict=True)))
srL = sr(w4L, SL, eL)
bumps = []
for name in ("00646", "00679B"):
    i = FUNDS.index(name)
    lb = np.zeros(N)
    lb[i] = -0.01
    wb = homog(SL, eL, f"bump {name}", lb=lb)
    wo = homog(SL, eL, f"bump {name}", solver="OSQP", lb=lb)
    if np.abs(wb - wo).max() > 1e-6:
        stop(f"bump {name}: CLARABEL and OSQP differ")
    pred = srL + srL**3 * nu4[i] * 0.01 / 2
    bumps.append(f"{name} >= -0.01: {pc(wb, 2)}; Sharpe ratio {f(sr(wb, SL, eL), 6)} against the first-order "
                 f"prediction {f(pred, 6)} (from {f(srL, 4, 6)}); gain {f(sr(wb, SL, eL) - srL, 6)} against the "
                 f"first-order gain SR^3 nu_i 0.01 / 2 = {f(pred - srL, 6)}")
put("R4 bumps, last signal (y_i >= -0.01 in the homogenized QP): " + "; ".join(bumps))
lam3 = float(2 * w3L @ SL @ w3L)
nu3 = 2 * SL @ w3L - lam3
put(f"R3 KKT, last signal: lambda = 2 A s_p^2 = {f(lam3, 4, 6)}; largest |nu_i| {ef(np.abs(nu3).max(), 1)} (no bound "
    f"active); s_p^2 = lambda / 2 = {f(lam3 / 2, 4)}; s_p = sqrt(lambda / 2) = {f(100 * sqrt(lam3 / 2), 2)}%")

# ---------------------------------------------------------------------------------------------------- U28
u = u28()
SU = u.A * cov0(u.X)
wU = minvar(SU, "U28")
heldU = [u.names[i] for i in range(len(u.names)) if wU[i] > ZERO]
zU = np.linalg.solve(SU, np.ones(len(u.names)))
wuU = zU / zU.sum()
lamU = float(2 * wU @ SU @ wU)
bU = SU @ wU / float(wU @ SU @ wU)
outU = [i for i in range(len(u.names)) if wU[i] <= ZERO]
imin, imax = min(outU, key=lambda i: bU[i]), max(outU, key=lambda i: bU[i])
w1 = minvar(u.A * cov0(u.X[:2191]), "U28 first half")          # LM30 owns the halves (decision A5): an echo
held1 = [u.names[i] for i in range(len(u.names)) if w1[i] > ZERO]
put(f"U28 (T = {u.X.shape[0]}, A = {f(u.A, 4)}): long-only minimum variance holds {len(heldU)} of {len(u.names)}: "
    f"{', '.join(heldU)}; volatility {f(100 * vol(wU, SU), 2)}% (in-sample); lambda {f(lamU, 4)}; excluded sectors' "
    f"beta_ip from {f(bU[imin], 3, 6)} ({u.names[imin]}) to {f(bU[imax], 3)} ({u.names[imax]}), all {len(outU)} >= 1; "
    f"echo of A28-13 (LM28's unconstrained solution): {int((wuU < -ZERO).sum())} shorts, gross "
    f"{f(np.abs(wuU).sum(), 2)}, volatility {f(100 * vol(wuU, SU), 2)}%; echo of A30-22 (LM30's first half, 2,191 "
    f"returns): {len(held1)} held ({', '.join(held1)}), {len(set(held1) & set(heldU))} of them among the full "
    f"sample's {len(heldU)}; candidate active sets 2^28 = {2**28:,}")
if min(bU[i] for i in outU) < 1 - 1e-12:
    stop("U28: an excluded sector has beta_ip < 1")

# ---------------------------------------------------------------------------------------------------- the cap on R3
icap = FUNDS.index("00679B")


def r3_capped(S: Mat, c: float) -> Vec:
    """R3 with w_00679B fixed at the cap c (the active set the KKT check confirms): closed form of the reduced QP."""
    free = [i for i in range(N) if i != icap]
    Sf = S[np.ix_(free, free)]
    rhs = np.linalg.solve(Sf, np.ones(N - 1))
    lin = np.linalg.solve(Sf, S[free, icap])
    # minimize w_f'Sf w_f + 2 c w_f'S_fc subject to 1'w_f = 1 - c: w_f = mu Sf^-1 1 - c Sf^-1 S_fc
    m = (1 - c + c * lin.sum()) / rhs.sum()
    w = np.zeros(N)
    w[free] = m * rhs - c * lin
    w[icap] = c
    return w


wc = r3_capped(SL, 0.40)
gc = 2 * SL @ wc
free = [i for i in range(N) if i != icap]
lamc = float(gc[free].mean())
nuc = lamc - float(gc[icap])
if np.abs(gc[free] - lamc).max() > 1e-12 or nuc < 0 or wc.min() < 0:
    stop("cap 40%: KKT fails")
wv = cp.Variable(N)
_, vco = solve(cp.quad_form(wv, cp.psd_wrap(SL)), [cp.sum(wv) == 1, wv >= 0, wv <= 0.40], cp.OSQP, OSQP_OPTS)
if np.abs(must(vco, "cap OSQP") - wc).max() > 1e-9:
    stop("cap 40%: OSQP differs from the closed form")
for c_ in (0.39, 0.41, 0.42):                     # the same active set: feasible, equal free gradients, nu_cap >= 0
    w_ = r3_capped(SL, c_)
    g_ = 2 * SL @ w_
    if w_.min() < 0 or float(g_[free].mean()) - float(g_[icap]) < 0 or np.abs(g_[free] - g_[free].mean()).max() > 1e-12:
        stop(f"cap {c_}: the active set changes")
v39, v41, v42 = (float(r3_capped(SL, c) @ SL @ r3_capped(SL, c)) for c in (0.39, 0.41, 0.42))
vc = float(wc @ SL @ wc)
b_free, b_cap = lamc / (2 * vc), (lamc - nuc) / (2 * vc)          # beta_ip = (Sigma w)_i / V; 2 Sigma w = lambda - nu_cap
if abs(0.60 * b_free + 0.40 * b_cap - 1) > 1e-12 or abs(lamc - (2 * vc + 0.40 * nuc)) > 1e-12:
    stop("cap 40%: beta or multiplier identity fails")
nbind = sum(1 for k in range(len(SCH)) if minvar(inputs(window(k)[2])[0], "x").max() > 0.40 + EPS)
put(f"R3 with a 40% cap, last window: {pc(wc, 1, 2)}; volatility {f(100 * sqrt(vc), 2)}% against R3's "
    f"{f(100 * vol(w3L, SL), 2)}%; variance V {f(vc, 6, 7)}; lambda {f(lamc, 5, 6)} = 2 V + 0.40 nu_cap; nu_cap "
    f"{f(nuc, 5, 6)}; beta_ip: the four free funds {f(b_free, 3, 4)}, 00679B {f(b_cap, 3, 4)}; (V(41%) - V(39%)) / 0.02 = "
    f"{f((v41 - v39) / 0.02, 6)}; V(41%) {f(v41, 6)} (volatility {f(100 * sqrt(v41), 2)}%), first-order "
    f"{f(vc - nuc * 0.01, 6)}, change {f(v41 - vc, 6)} against -nu_cap x 0.01 = {f(-nuc * 0.01, 6)}; V(42%) "
    f"{f(v42, 6)}, first-order {f(vc - nuc * 0.02, 6)}, change {f(v42 - vc, 6)}; R3's largest weight exceeds 40% "
    f"(the cap binds) at {nbind} of {len(SCH)} signals")

lims = {"unconstrained": wtL, "gross <= 150%": homog(SL, eL, "gross", gross=1.5),
        "long-only (R4)": w4L, "long-only, cap 40%": homog(SL, eL, "cap", cap=0.40)}
if np.abs(lims["gross <= 150%"] - homog(SL, eL, "gross", solver="OSQP", gross=1.5)).max() > 1e-6:
    stop("gross limit: solvers differ")
if np.abs(lims["long-only, cap 40%"] - homog(SL, eL, "cap", solver="OSQP", cap=0.40)).max() > 1e-6:
    stop("cap limit: solvers differ")
put("maximum Sharpe ratio under limits, last window: " + "; ".join(
    f"{k}: {pc(w, 1, 2)}, Sharpe ratio {f(sr(w, SL, eL), 2, 3)}, gross {f(100 * np.abs(w).sum(), 1)}%, volatility "
    f"{f(100 * vol(w, SL), 1, 2)}%" for k, w in lims.items()))

# frontier: the unconstrained frontier's weights are linear in the target mean m; long-only by CLARABEL
Kf = np.vstack([np.ones(N), muL])
Bf = np.linalg.solve(SL, Kf.T)                       # Sigma^-1 [1 mu]
Gf = Kf @ Bf                                         # 2 x 2


def w_front(m: float) -> Vec:
    return Bf @ np.linalg.solve(Gf, np.array([1.0, m]))


a0, a1 = w_front(0.0), w_front(1.0) - w_front(0.0)  # w(m) = a0 + m a1
lo_m, hi_m = -np.inf, np.inf
for i in range(N):
    if a1[i] > 0:
        lo_m = max(lo_m, -a0[i] / a1[i])
    elif a1[i] < 0:
        hi_m = min(hi_m, -a0[i] / a1[i])
mgmv = float(w3L @ muL)


def lo_front(m: float) -> Vec:
    w = cp.Variable(N)
    _, v = solve(cp.quad_form(w, cp.psd_wrap(SL)), [cp.sum(w) == 1, muL @ w == m, w >= 0], cp.CLARABEL, CLARABEL_OPTS)
    return must(v, f"long-only frontier at {m}")


w30u, w30l = w_front(0.40), lo_front(0.40)
put(f"frontier, last window: the global minimum-variance point (= R3, interior) has mean {f(100 * mgmv, 2)}% and "
    f"volatility {f(100 * vol(w3L, SL), 2)}%; the long-only frontier equals the unconstrained one for target means "
    f"{f(100 * lo_m, 2)}% to {f(100 * hi_m, 2)}% (all weights >= 0); at a target mean of 40%: unconstrained volatility "
    f"{f(100 * vol(w30u, SL), 2)}% ({pc(w30u, 1)}), long-only {f(100 * vol(w30l, SL), 2)}% ({pc(w30l, 1)}); the "
    f"long-only frontier ends at 0050 (mean {f(100 * muL[0], 1)}%, volatility {f(100 * volL[0], 1)}%); the "
    f"unconstrained tangency's mean {f(100 * float(wtL @ muL), 1, 2)}%, R4's {f(100 * float(w4L @ muL), 1, 2)}%; CML slopes "
    f"(in-sample) {f(sr(wtL, SL, eL), 3)} and {f(sr(w4L, SL, eL), 3)}")

# LP and statuses
wv = cp.Variable(N)
plp, vlp = solve(muL @ wv, [cp.sum(wv) == 1, wv >= 0, wv <= 0.40], "CLARABEL", None, sense="max")
vlp = must(vlp, "LP")
order = np.argsort(-muL)
greedy = np.zeros(N)
greedy[order[0]], greedy[order[1]], greedy[order[2]] = 0.4, 0.4, 0.2
if np.abs(vlp - greedy).max() > 1e-6:
    stop("LP: not the greedy vertex")
wv = cp.Variable(N)
pdef = cp.Problem(cp.Maximize(muL @ wv), [cp.sum(wv) == 1, wv >= 0, wv <= 0.40])
pdef.solve()
put(f"LP, last window: maximize the window mean subject to 1'w = 1, 0 <= w <= 40%: {pc(vlp, 1)} (a vertex: the two "
    f"highest means at the cap, the third takes the rest); mean {f(100 * float(muL @ vlp), 2)}%; cvxpy's default "
    f"solver {pdef.solver_stats.solver_name}")
wv = cp.Variable(N)
pinf = cp.Problem(cp.Minimize(cp.quad_form(wv, cp.psd_wrap(SL))), [cp.sum(wv) == 1, wv >= 0, wv <= 0.15])
pinf.solve(solver=cp.CLARABEL)
wv2 = cp.Variable(N)
punb = cp.Problem(cp.Maximize(muL @ wv2), [cp.sum(wv2) == 1])
punb.solve(solver=cp.CLARABEL)
wv3 = cp.Variable(N)
try:
    cp.Problem(cp.Minimize(cp.sum(wv3)), [cp.quad_form(wv3, cp.psd_wrap(SL)) >= 0.01]).solve()
    dcp = "solved (unexpected)"
except cp.error.DCPError as exc:
    dcp = type(exc).__name__
put(f"statuses: a 15% cap on five funds -> '{pinf.status}', prob.value {pinf.value}, w.value {wv.value}; maximize the "
    f"mean with the budget only -> '{punb.status}', prob.value {punb.value}, w.value {wv2.value}; a volatility floor "
    f"w'Sw >= 0.01 alone (no budget) -> {dcp}")

# ---------------------------------------------------------------------------------------------------- costs in the objective


def drift(w: Vec, i0: int, i1: int) -> Vec:
    """Weights w set at the close of wealth date i0, grown through the close of wealth date i1."""
    h = w * np.prod(1 + fr.W[i0 + 1:i1 + 1], axis=0)
    return h / h.sum()


def cost(d: Vec) -> float:
    return COMMISSION * float(np.abs(d).sum()) + float(TAXV @ np.clip(-d, 0, None))


def penalized(S: Mat, wd: Vec, theta: float, solver: str = "OSQP") -> Vec:
    w = cp.Variable(N)
    obj = cp.quad_form(w, cp.psd_wrap(S)) + theta * (COMMISSION * cp.norm1(w - wd) + TAXV @ cp.pos(wd - w))
    sv, op = BOOK[solver]
    _, v = solve(obj, [cp.sum(w) == 1, w >= 0], sv, op)
    return must(v, f"penalized theta {theta}")


def band_kkt(S: Mat, w: Vec, wd: Vec, theta: float, tol: float = 1e-9) -> bool:
    """KKT of the cost-penalized QP (buys and sells split, so every term is differentiable): with g = 2 S w, a bought
    fund has g_i + theta c = lambda, a sold fund still held g_i - theta (c + tax_i) = lambda, a fund sold out
    g_i - theta (c + tax_i) = lambda + nu_i with nu_i >= 0, and an untouched fund lies in the band between."""
    g = 2 * S @ w
    d = w - wd
    lo, hi = g + theta * COMMISSION, g - theta * (COMMISSION + TAXV)
    buy, sell, out = d > tol, d < -tol, w < tol
    keep = ~buy & ~sell
    lam_c = np.concatenate([lo[buy], hi[sell & ~out]])
    if lam_c.size == 0:
        return bool(hi[keep].max() <= lo[keep].min() + 1e-10)
    lam = float(lam_c.mean())
    return bool(np.abs(lam_c - lam).max() < 1e-8 and np.all(lo[keep] >= lam - 1e-10)
                and np.all(hi[keep] <= lam + 1e-10) and np.all(hi[sell & out] >= lam - 1e-10))


kc = [s[0] for s in SCH].index("2025-04-30")
sgp, trp, xp, _ = window(kc - 1)
sgc, trc, xc, _ = window(kc)
Sp = inputs(xp)[0]
Sc = inputs(xc)[0]
w3p = minvar(Sp, "R3 prev")
wdc = drift(w3p, WD.index(trp), WD.index(sgc))
w3c = minvar(Sc, "R3 2025-04")
Gd = 2 * Sc @ wdc
bar = max((Gd[i] - Gd[j]) / (2 * COMMISSION + TAXV[i]) for i in range(N) for j in range(N) if i != j)
pair = max(((i, j) for i in range(N) for j in range(N) if i != j),
           key=lambda ij: (Gd[ij[0]] - Gd[ij[1]]) / (2 * COMMISSION + TAXV[ij[0]]))
for th, trade in ((bar * 0.999, True), (bar * 1.001, False)):
    tr_ = bool(0.5 * np.abs(penalized(Sc, wdc, th) - wdc).sum() > 1e-7)
    if tr_ != trade:
        stop(f"no-trade threshold: theta {th} trades = {tr_}")
put(f"2025-04-30 signal (R3): previous target ({sgp}, traded {trp}) {pc(w3p, 1, 2)}; drifted to the signal close "
    f"{pc(wdc, 1, 2)}; new R3 {pc(w3c, 1, 2)}; planned turnover {f(100 * 0.5 * np.abs(w3c - wdc).sum(), 2)}%, cost "
    f"{f(100 * cost(w3c - wdc), 3, 4)}% of wealth; variance gradient 2 A Sigma_hat w_drift " + ", ".join(
    f"{s} {f(v, 5)}" for s, v in zip(FUNDS, Gd, strict=True)) + f"; R3's lambda {f(float(2 * w3c @ Sc @ w3c), 5)}; "
    f"no trade for theta >= {f(bar, 2, 4)} (set by selling {FUNDS[pair[0]]} against buying {FUNDS[pair[1]]})")

th1 = 1.0
wp1 = penalized(Sc, wdc, th1)
wp1c = penalized(Sc, wdc, th1, "CLARABEL")
dp1 = wp1 - wdc
gp1 = 2 * Sc @ wp1
buy, sell = dp1 > ZERO, dp1 < -ZERO
lam_b = float((gp1[buy] + th1 * COMMISSION).mean())
lam_s = float((gp1[sell] - th1 * (COMMISSION + TAXV[sell])).mean())
if abs(lam_b - lam_s) > 1e-9 or np.abs(gp1[buy] + th1 * COMMISSION - lam_b).max() > 1e-9:
    stop("theta = 1: the band conditions fail")
keep = ~buy & ~sell
if not np.all((gp1[keep] >= lam_b - th1 * COMMISSION - 1e-9) & (gp1[keep] <= lam_b + th1 * (COMMISSION + TAXV[keep])
                                                                 + 1e-9)):
    stop("theta = 1: an untouched fund lies outside its band")
put(f"theta = 1, 2025-04-30: {pc(wp1, 1, 2)}; trades " + ", ".join(
    f"{s} {'0' if abs(v) < ZERO else f(100 * v, 1, 2, plus=True)}" for s, v in zip(FUNDS, dp1, strict=True))
    + f"; planned turnover {f(100 * 0.5 * np.abs(dp1).sum(), 2)}%, cost {f(100 * cost(dp1), 3, 4)}%; volatility "
    f"{f(100 * vol(wp1, Sc), 2, 3)}% against R3's {f(100 * vol(w3c, Sc), 2, 3)}% and no trade's "
    f"{f(100 * vol(wdc, Sc), 2, 3)}%;"
    f" lambda {f(lam_b, 6)}; gradient " + ", ".join(f"{s} {f(v, 6)}" for s, v in zip(FUNDS, gp1, strict=True))
    + f"; band: buy at {f(lam_b - th1 * COMMISSION, 6)}, sell at {f(lam_b + th1 * (COMMISSION + 0.001), 6)} (taxed) "
    f"and {f(lam_b + th1 * COMMISSION, 6)} (00679B); OSQP against CLARABEL (cost as norm1 and pos) "
    f"{ef(np.abs(wp1 - wp1c).max(), 1)}")

rows_sweep = []
sweep_gap = 0.0          # OSQP (polished, checked by band_kkt) against CLARABEL on every penalized solve of the sweep
to0, cs0 = 0.0, 0.0      # theta = 0's planned totals: the denominators (R3's own figures are LM34's; not printed)
for th in (0.0, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0):
    prev, iprev = None, -1
    to, cs, gap, quiet = 0.0, 0.0, [], 0
    for sg, tr, rows in SCH:
        S = A * cov0(fr.X[rows - WINDOW:rows])
        w3 = minvar(S, "x")
        if prev is None:
            fk = w3
        else:
            wd_ = drift(prev, iprev, WD.index(sg))
            fk = penalized(S, wd_, th) if th > 0 else w3
            if th > 0:
                if not band_kkt(S, fk, wd_, th):
                    stop(f"cost sweep: KKT fails at theta {th}, {sg}")
                sweep_gap = max(sweep_gap, float(np.abs(fk - penalized(S, wd_, th, "CLARABEL")).max()))
            fk = np.clip(fk, 0, None)
            fk = fk / fk.sum()
            d = fk - wd_
            to += 0.5 * float(np.abs(d).sum())
            cs += cost(d)
            gap.append(0.0 if th == 0 else vol(fk, S) - vol(w3, S))
            quiet += int(0.5 * float(np.abs(d).sum()) < ZERO)
        prev, iprev = fk, WD.index(tr)
    if th == 0:
        to0, cs0 = to, cs
    rows_sweep.append(f"theta {th:g}: planned turnover {f(100 * to / to0, 1, also=(4,))}% of theta 0's, planned cost "
                      f"{f(100 * cs / cs0, 1, also=(4,))}% of theta 0's, no trade at {quiet} of {len(SCH) - 1}, in-sample "
                      f"volatility given up mean {f(1e4 * float(np.mean(gap)), 1, also=(4,))} bp, largest "
                      f"{f(1e4 * float(np.max(gap)), 1, also=(4,))} bp")
if sweep_gap > 1e-5:
    stop(f"cost sweep: OSQP and CLARABEL differ by {sweep_gap:.1e}")
put("cost-penalized R3 on its own path (planned at each signal close; 91 rebalancing signals; totals over the 91 "
    "relative to theta = 0, i.e. R3 itself): " + "; ".join(rows_sweep)
    + "; every OSQP solution passes the KKT band check; with the cost given to cvxpy as norm1 and pos atoms, CLARABEL "
    f"differs from OSQP by at most {ef(sweep_gap, 1)} in a weight (an interior point leaves trades of that size where "
    f"the exact solution has none); theta = 2 / (delta tau) for risk aversion delta and holding period tau years: "
    f"delta 4 and tau 1/12 give theta {2 / (4 * (1 / 12)):g}, theta 1 is delta tau = 2")

# ---------------------------------------------------------------------------------------------------- solvers and checks
names = {}
w = cp.Variable(N)
p = cp.Problem(cp.Minimize(cp.quad_form(w, cp.psd_wrap(SL))), [cp.sum(w) == 1, w >= 0])
p.solve()
names["R3 QP"] = p.solver_stats.solver_name
w = cp.Variable(N)
p = cp.Problem(cp.Maximize(eL @ w), [cp.quad_form(w, cp.psd_wrap(SL)) <= 0.04, w >= 0, cp.sum(w) <= 1.5])
p.solve()
names["volatility limit (SOCP)"] = p.solver_stats.solver_name
w = cp.Variable(N)
p = cp.Problem(cp.Minimize(cp.quad_form(w, cp.psd_wrap(SL)) + COMMISSION * cp.norm1(w - wdc)), [cp.sum(w) == 1, w >= 0])
p.solve()
names["cost-penalized QP"] = p.solver_stats.solver_name
dflt = vars(import_module("clarabel"))["DefaultSettings"]()    # a compiled module without type information
# cvxpy overrides OSQP's own defaults in its interface; read them from the installed source, not from memory
osqp_src = inspect.getsource(import_module("cvxpy.reductions.solvers.qp_solvers.osqp_qpif"))
osqp_def = {k: re.search(rf"solver_opts\.get\('{k}', ([^)]+)\)", osqp_src) for k in ("eps_abs", "eps_rel", "max_iter")}
if any(m is None for m in osqp_def.values()) or "solver_opts.get(polish_param, True)" not in osqp_src:
    stop("cvxpy's OSQP defaults: source pattern not found")
put("cvxpy's default solver: " + ", ".join(f"{k} {v}" for k, v in names.items()) + f" (LP: {pdef.solver_stats.solver_name})"
    f"; versions cvxpy {version('cvxpy')}, OSQP {version('osqp')}, CLARABEL {version('clarabel')}, SCS {version('scs')} "
    f"(problem 11's second solver), SciPy {version('scipy')} (nnls); CLARABEL defaults "
    f"tol_gap_abs {dflt.tol_gap_abs:g}, tol_gap_rel {dflt.tol_gap_rel:g}, tol_feas {dflt.tol_feas:g}, max_iter "
    f"{dflt.max_iter}; cvxpy's OSQP defaults (osqp_qpif.py) " + ", ".join(
    f"{k} {m.group(1)}" for k, m in osqp_def.items() if m is not None) + ", polishing True on a fresh solve")


def gap_run(x: Mat, rule: str, unit: str, solver: str, opts: dict | None) -> float:
    S_ann = A * cov0(x)
    e_ann = A * x.mean(axis=0) - RF
    exact = minvar(S_ann, "x") if rule == "R3" else maxsharpe(S_ann, e_ann, "x")
    assert exact is not None
    k = 1.0 if unit == "daily" else A
    S = k * cov0(x)
    a = ONE if rule == "R3" else (k / A) * e_ann
    y = cp.Variable(N)
    _, v = solve(cp.quad_form(y, cp.psd_wrap(S)), [a @ y == 1, y >= 0], solver, opts)
    if v is None:
        return float("inf")
    return float(np.abs(v / v.sum() - exact).max())


cases = [("OSQP", None, "default"), ("CLARABEL", None, "default"), ("OSQP", OSQP_OPTS, "book"),
         ("CLARABEL", CLARABEL_OPTS, "book")]
first = []
for unit in ("daily", "annual"):
    for sv, op, lab in cases:
        first.append(f"{unit} {sv} {lab} {ef(gap_run(x0, 'R3', unit, sv, op), 1)}")
w30d = minvar(cov0(x0), "R3 first daily")
put("R3 at the first signal, largest weight gap to the exact solution: " + "; ".join(first)
    + f"; the optimal variance in daily units {ef(float(w30d @ cov0(x0) @ w30d), 3)}, in annual units (A times it; "
    f"echo of LM28's first-window sigma_min^2, A28-10) {ef(float(w30d @ (A * cov0(x0)) @ w30d), 3)}")
worst = {}
for k in range(len(SCH)):
    x = window(k)[2]
    for rule in ("R3", "R4"):
        for unit in ("daily", "annual"):
            for sv, op, lab in cases:
                key = f"{rule} {unit} {sv} {lab}"
                worst[key] = max(worst.get(key, 0.0), gap_run(x, rule, unit, sv, op))
put("largest weight gap over the 92 signals: " + "; ".join(f"{k} {ef(v, 1)}" for k, v in worst.items()))

xe = xr                                                    # the exact homogenized R4 (NNLS)
checks = []
for sv in ("OSQP", "CLARABEL"):
    y = cp.Variable(N)
    s_, o_ = BOOK[sv]
    pr, v = solve(cp.quad_form(y, cp.psd_wrap(SL)), [eL @ y == 1, y >= 0], s_, o_)
    v = must(v, f"R4 check {sv}")
    lam_h = float(2 * v @ SL @ v)
    nu_h = 2 * SL @ v - lam_h * eL
    on = v > ZERO
    checks.append(f"{sv} status {pr.status}, weight gap {ef(np.abs(v / v.sum() - w4L).max(), 1)}, objective gap "
                  f"{ef(abs(float(v @ SL @ v) - float(xe @ SL @ xe)) / float(xe @ SL @ xe), 1)}, |e'y - 1| "
                  f"{ef(abs(float(eL @ v) - 1), 1)}, min y {ef(v.min(), 1)}, stationarity on held funds "
                  f"{ef(np.abs(nu_h[on]).max(), 1)}, smallest nu {ef(nu_h.min(), 1)}, complementarity "
                  f"{ef(np.abs(nu_h * v).max(), 1)}")
act = [i for i in range(N) if w4L[i] > ZERO]
zS = np.linalg.solve(SL[np.ix_(act, act)], eL[act])
wcf = np.zeros(N)
wcf[act] = zS / zS.sum()
put("R4 checks, last signal (each solver's y; nu = 2 Sigma y - lambda e with lambda = 2 y'Sigma y, the value that "
    "e'y = 1 gives; cvxpy's dual of e'y = 1 is not used): " + "; ".join(checks)
    + f"; closed form on the active set {{{', '.join(FUNDS[i] for i in act)}}} (LM28's tangency of the held funds) "
    f"against the exact solution {ef(np.abs(wcf - w4L).max(), 1)}")

duals = []
for sv in ("OSQP", "CLARABEL"):
    w = cp.Variable(N)
    c0, c1 = cp.sum(w) == 1, w >= 0
    s_, o_ = BOOK[sv]
    solve(cp.quad_form(w, cp.psd_wrap(SL)), [c0, c1], s_, o_)
    duals.append(f"R3 {sv}: budget dual {f(float(np.asarray(c0.dual_value)), 6)} (the book's lambda {f(lam3, 6)}), "
                 f"largest bound dual {ef(float(np.abs(np.asarray(c1.dual_value)).max()), 1)}")
w = cp.Variable(N)
c0, c1, c2 = cp.sum(w) == 1, w >= 0, w <= 0.40
solve(cp.quad_form(w, cp.psd_wrap(SL)), [c0, c1, c2], cp.CLARABEL, CLARABEL_OPTS)
duals.append(f"R3 with the 40% cap (CLARABEL): budget dual {f(float(np.asarray(c0.dual_value)), 5)}, cap dual of "
             f"00679B {f(float(np.asarray(c2.dual_value)[icap]), 5)} (nu_cap {f(nuc, 5)})")
x = cp.Variable(N)
c0, c1 = eL @ x == 1, x >= 0
solve(cp.quad_form(x, cp.psd_wrap(SL)), [c0, c1], cp.CLARABEL, CLARABEL_OPTS)
duals.append(f"R4 (CLARABEL): dual of e'y = 1 {f(float(np.asarray(c0.dual_value)), 4)} (lambda {f(lam4, 4)}), bound duals "
             + ", ".join(f"{s} {f(float(v), 4)}" for s, v in zip(FUNDS, np.asarray(c1.dual_value), strict=True)))
put("cvxpy's dual values (printed as cvxpy reports them): " + "; ".join(duals))

# ---------------------------------------------------------------------------------------------------- the widget


def pair_kkt(S2: Mat, e2: Vec, delta: float, cap: float) -> list[tuple[str, Vec | None, Vec, bool, bool, float]]:
    """Maximize f'e - delta/2 f'Sf subject to f1 + f2 <= cap, f1 >= 0, f2 >= 0: every binding set (LM7's method)."""
    G = np.array([[1.0, 1.0], [-1.0, 0.0], [0.0, -1.0]])
    b = np.array([cap, 0.0, 0.0])
    names3 = ["cap", "f1>=0", "f2>=0"]
    out = []
    for act3 in itertools.product([0, 1], repeat=3):
        idx = [k for k in range(3) if act3[k]]
        Kk = np.zeros((2 + len(idx), 2 + len(idx)))
        Kk[:2, :2] = delta * S2
        Kk[:2, 2:] = G[idx].T
        Kk[2:, :2] = G[idx]
        label = "+".join(names3[k] for k in idx) or "none"
        if np.linalg.matrix_rank(Kk) < Kk.shape[0]:
            out.append((label, None, np.zeros(0), False, False, float("nan")))
            continue
        sol = np.linalg.solve(Kk, np.concatenate([e2, b[idx]]))
        fv, nu = sol[:2], sol[2:]
        out.append((label, fv, nu, bool(np.all(G @ fv <= b + 1e-12)), bool(np.all(nu >= -1e-12)),
                    float(fv @ e2 - delta / 2 * fv @ S2 @ fv)))
    return out


S0, mu0, e0 = inputs(x0)
pairS, pairE = S0[:2, :2], e0[:2]
init = pair_kkt(pairS, pairE, 4.0, 1.0)
best = [r for r in init if r[1] is not None and r[3] and r[4]]
if len(best) != 1:
    stop(f"widget: {len(best)} candidates pass every condition")
lab, fbest, nubest, _, _, ubest = best[0]
assert fbest is not None
solv = [r for r in init if r[1] is not None]
signs_only = ["the unconstrained point (no binding set)" if r[0] == "none" else f"{r[0]} binding"
              for r in solv if r[4] and not r[3]]
put(f"widget initial state (first window, 0050 and 00646, delta 4, net-exposure cap 1; inputs echo A28-05 to A28-07): "
    f"e {f(100 * pairE[0], 2)}% and "
    f"{f(100 * pairE[1], 2)}%, volatility {f(100 * sqrt(pairS[0, 0]), 2)}% and {f(100 * sqrt(pairS[1, 1]), 2)}%, "
    f"correlation {f(pairS[0, 1] / sqrt(pairS[0, 0] * pairS[1, 1]), 3)}; unconstrained f "
    f"{', '.join(f(v, 2, 3) for v in np.linalg.solve(pairS, pairE) / 4.0)}; optimum binds {lab}: f "
    f"{', '.join(f(v, 3) for v in fbest)}, multipliers {', '.join(f(v, 4) for v in nubest)}, utility {f(ubest, 4)}; "
    f"of {len(solv)} solvable binding sets {sum(r[3] for r in solv)} pass feasibility, {sum(r[4] for r in solv)} the "
    f"signs, {len(best)} both; passing the signs but infeasible: {', '.join(signs_only)}")

# ---------------------------------------------------------------------------------------------------- problems
s2, cv = 0.0102, 0.0150
put(f"problem 2 (hypothetical): sigma_p^2 = {s2}, Cov(R_i, R_p) = {cv}: nu_i = 2 (Cov - sigma_p^2) = "
    f"{f(2 * (cv - s2), 4)}; beta_ip = {f(cv / s2, 3)}; distractors {f(cv - s2, 4)} (factor 2 dropped) and {f(-2 * (cv - s2), 4)} (sign)")
w30, w31 = minvar(S0, "R3 first"), maxsharpe(S0, e0, "R4 first")
assert w31 is not None
act0 = [i for i in range(N) if w31[i] > ZERO]
z0 = np.linalg.solve(S0[np.ix_(act0, act0)], e0[act0])
x31 = w31 / float(w31 @ e0)
nu31 = 2 * S0 @ x31 - float(2 * x31 @ S0 @ x31) * e0
put(f"problem 9 (first window): R3 (= LM28's w_mv, A28-10) {pc(w30, 1)}, volatility {f(100 * vol(w30, S0), 2)}%; R4 {pc(w31, 1, 2)}, in-sample "
    f"Sharpe ratio {f(sr(w31, S0, e0), 3)}; R4 excludes {', '.join(FUNDS[i] for i in range(N) if i not in act0)} "
    f"with nu / lambda " + ", ".join(f"{FUNDS[i]} {f(100 * nu31[i] / float(2 * x31 @ S0 @ x31), 2)} points"
                                     for i in range(N) if i not in act0)
    + f"; closed form on the held funds against the exact {ef(np.abs(z0 / z0.sum() - w31[act0]).max(), 1)}")
w = cp.Variable(N)
cto = 0.5 * cp.norm1(w - wdc) <= 0.05
_, vto = solve(cp.quad_form(w, cp.psd_wrap(Sc)), [cp.sum(w) == 1, w >= 0, cto], cp.CLARABEL, CLARABEL_OPTS)
vto = must(vto, "turnover limit")
nuto = float(np.asarray(cto.dual_value))
w = cp.Variable(N)
_, vpen = solve(cp.quad_form(w, cp.psd_wrap(Sc)) + nuto * 0.5 * cp.norm1(w - wdc), [cp.sum(w) == 1, w >= 0],
                cp.CLARABEL, CLARABEL_OPTS)
vpen = must(vpen, "turnover penalty")
put(f"problem 10 (2025-04-30, R3 with planned turnover <= 5%): {pc(vto, 1, 2)}; volatility {f(100 * vol(vto, Sc), 3)}%; "
    f"multiplier of the limit {f(nuto, 5)}; the turnover penalty with theta = that multiplier gives "
    f"{pc(vpen, 2)} (largest gap {ef(np.abs(vpen - vto).max(), 1)})")
fl = cp.Variable(N)
res11 = []
p11 = cp.Problem(cp.Maximize(eL @ fl), [cp.quad_form(fl, cp.psd_wrap(SL)) <= 0.25**2, fl >= 0, cp.norm1(fl) <= 1.5])
with warnings.catch_warnings():                                   # cvxpy warns on an inaccurate solution
    warnings.simplefilter("ignore")
    p11.solve(solver=cp.CLARABEL, **CLARABEL_OPTS)
st12 = p11.status                                                  # the book's 1e-12 on this cone problem
for spread in (0.0, SPREAD):
    # The exact optimum: the long-only tangency at the borrowing rate r_f + spread (excess e - spread), scaled to 25%
    # volatility. Valid when its net exposure L is above 1 (so the spread is paid on L - 1, linearly) and its gross
    # exposure is at most 1.5: then f'e - spread max(0, 1'f - 1) <= (e - spread 1)'f + spread for every f, with
    # equality at this point, which maximizes the right side over the volatility limit and f >= 0.
    wb = maxsharpe(SL, eL - spread, f"problem 11 spread {spread}")
    assert wb is not None
    kb = 0.25 / vol(wb, SL)
    fx = kb * wb
    if not (fx.sum() > 1 and np.abs(fx).sum() <= 1.5):
        stop("problem 11: the scaled tangency is not the optimum")
    obj = eL @ fl - spread * cp.pos(cp.sum(fl) - 1)
    cons11 = [cp.quad_form(fl, cp.psd_wrap(SL)) <= 0.25**2, fl >= 0, cp.norm1(fl) <= 1.5]
    _, v11 = solve(obj, cons11, "CLARABEL", ERC_OPTS, sense="max")     # 1e-12 stops at "optimal_inaccurate"
    v11 = must(v11, "problem 11")
    _, s11 = solve(obj, cons11, "SCS", SCS_OPTS, sense="max")
    s11 = must(s11, "problem 11 SCS")
    if np.abs(v11 - fx).max() > 1e-5 or np.abs(s11 - fx).max() > 1e-5:
        stop("problem 11: CLARABEL or SCS differs from the exact solution")
    gross_ret = float(eL @ fx)
    res11.append(f"spread {spread:.2f}: the long-only tangency at r_f + spread {pc(wb, 2)}, scaled by 25% / "
                 f"{f(100 * vol(wb, SL), 2)}% = {f(kb, 3)}: f {pc(fx, 2)}, net exposure L {f(100 * fx.sum(), 1)}%, "
                 f"volatility {f(100 * vol(fx, SL), 2)}%, excess return before financing {f(100 * gross_ret, 2)}%, "
                 f"financing spread x (L - 1) {f(100 * spread * (fx.sum() - 1), 2)}%, excess return after financing "
                 f"{f(100 * (gross_ret - spread * max(0.0, fx.sum() - 1)), 2)}%; CLARABEL against it "
                 f"{ef(np.abs(v11 - fx).max(), 1)}, SCS {ef(np.abs(s11 - fx).max(), 1)}")
    if spread == 0.0 and np.abs(wb - w4L).max() > 1e-12:
        stop("problem 11: spread 0 is not R4")
put("problem 11 (last window; maximize f'e - spread max(0, 1'f - 1), f'Sf <= 25%^2, f >= 0, |f|_1 <= 1.5; exact "
    f"solution by vol5_rules.maxsharpe, checked to 1e-5 by CLARABEL at 1e-10 and by SCS (eps "
    f"{str(SCS_OPTS['eps']).replace('e-0', 'e-')}, "
    f"max_iters {SCS_OPTS['max_iters']:,}); at the book's 1e-12 CLARABEL returns '{st12}'; spread 0 gives R4 "
    f"itself): " + "; ".join(res11))

g5 = np.round(Gd, 5)
bar5 = max((g5[i] - g5[j]) / (2 * COMMISSION + TAXV[i]) for i in range(N) for j in range(N) if i != j)
put("problem 7 (2025-04-30, the variance gradient at the drifted weights printed to 5 decimals): " + ", ".join(
    f"{s} {v:.5f}" for s, v in zip(FUNDS, g5, strict=True)) + f"; threshold from the printed inputs {f(bar5, 2, 4)}, "
    f"from the unrounded ones {f(bar, 2, 4)}")
put(f"problem 6: from cvxpy's budget dual -0.020396, s_p = sqrt(0.020396 / 2) = {f(100 * sqrt(0.020396 / 2), 2)}%; "
    f"distractor sqrt(0.020396) = {f(100 * sqrt(0.020396), 2)}%")

lam_p = 0.4506
put(f"problem 5: from the dual -0.4506 of e'y = 1 (R4's homogenized QP, last window), SR = sqrt(2 / 0.4506) = "
    f"{f(sqrt(2 / lam_p), 2, 3)}; distractors sqrt(1 / 0.4506) = {f(sqrt(1 / lam_p), 2, 3)} (factor 2 dropped) and "
    f"0.4506 (the dual read as the ratio); exact {f(sr(w4L, SL, eL), 3)}")

# ---------------------------------------------------------------------------------------------------- r_f sensitivity
# The shared decision "Risk-free rate": 1.5% is illustrative, so R4 and problem 11's 2-point optimum are recomputed at
# r_f = 0 and 2% on the last window (e = mu - r_f; problem 11's borrowing rate r_f + SPREAD), by A29-31's method.
heldL = [s for s, v in zip(FUNDS, w4L, strict=True) if v > ZERO]
r4rf, chg, p11rf = [], (0.0, "", ""), []
for rf_, lab_ in ((0.0, "0"), (0.02, "2%")):
    e_ = muL - rf_
    wr = maxsharpe(SL, e_, f"R4 r_f {lab_}")
    assert wr is not None
    held_r = [s for s, v in zip(FUNDS, wr, strict=True) if v > ZERO]
    if held_r != heldL:
        stop(f"r_f {lab_}: R4 holds other funds than at 1.5%")
    i = int(np.argmax(np.abs(wr - w4L)))
    if abs(wr[i] - w4L[i]) > chg[0]:
        chg = (float(abs(wr[i] - w4L[i])), FUNDS[i], lab_)
    r4rf.append(f"R4 at r_f {lab_}: {pc(wr, 2)}, in-sample Sharpe ratio {f(sr(wr, SL, e_), 2)}")
    wb = maxsharpe(SL, e_ - SPREAD, f"problem 11 r_f {lab_}")
    assert wb is not None
    fx = 0.25 / vol(wb, SL) * wb
    L_ = float(fx.sum())
    if not (L_ > 1 and np.abs(fx).sum() <= 1.5):
        stop(f"r_f {lab_}: the scaled tangency is not problem 11's optimum")
    obj = e_ @ fl - SPREAD * cp.pos(cp.sum(fl) - 1)
    cons11 = [cp.quad_form(fl, cp.psd_wrap(SL)) <= 0.25**2, fl >= 0, cp.norm1(fl) <= 1.5]
    _, v11 = solve(obj, cons11, "CLARABEL", ERC_OPTS, sense="max")
    if np.abs(must(v11, f"problem 11 r_f {lab_}") - fx).max() > 1e-6:
        stop(f"r_f {lab_}: CLARABEL differs from the exact solution of problem 11 by more than 1e-6")
    p11rf.append(f"r_f {lab_}: L {f(100 * L_, 1)}%, excess return after financing "
                 f"{f(100 * (float(e_ @ fx) - SPREAD * (L_ - 1)), 2)}%")
put("r_f sensitivity (shared decision \"Risk-free rate\"), last window: " + "; ".join(r4rf)
    + f"; the same {len(heldL)} funds as at 1.5% ({', '.join(heldL)}); largest weight change against r_f 1.5% {f(100 * chg[0], 2)} points "
    f"({chg[1]}, r_f {chg[2]}); problem 11 at a 2-point spread: " + "; ".join(p11rf)
    + "; CLARABEL at 1e-10 within 1e-6 of each")

print("\n".join(OUT))
