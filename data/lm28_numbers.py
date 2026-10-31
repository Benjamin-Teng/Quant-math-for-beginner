"""Every number that LM28 (Mean-Variance Optimization) prints, computed and checked against src/lm28.md.

Run:  uv run python data/lm28_numbers.py
      (after data/vol5_series.py, data/vol5_rules.py and data/vol2_series.py; and after data/lm28_charts.py, whose
      chart files and widget data this script checks)

Inputs and conventions: data/lm28_common.py (E5's two frames, the first window, the test period, U28 and the closed
forms of LM28). The module text is src/lm28.md; plans/vol-5-anchors.md, "LM28", holds the Stage 1 anchors A28-01 ..
A28-46, which data/vol5_anchors_lm28.py prints and this script started from.

Part 1 recomputes every anchor line exactly as data/vol5_anchors_lm28.py prints it and compares it with the anchor
table's Value column: a difference is reported, never forced.

Part 2 checks the text (each check stops the script on a failure):
  chk(label, value, fmt, printed)  format(value, fmt) equals the printed string, the value is not a rounding tie of
                                   that format, and the printed string is in the module as a whole number. Hand
                                   computations are redone from the printed, rounded inputs (PITFALLS section 7).
  has(label, text)                 a literal string (a date, a phrase, a vector as printed) is in the module.
  vec(label, values, printed)      a vector printed at one decimal, entry by entry, as "(a, b, c)" in the module.
At the end the script lists the numbers of the module that no check covered and prints "all N checks passed".
"""
import json
import math
import re
import sys
from decimal import Decimal
from importlib.metadata import version
from math import floor, sqrt

import cvxpy as cp
import lm28_common as CM
import numpy as np
from lm28_common import (
    CLARABEL_OPTS,
    OSQP_OPTS,
    RF,
    WINDOW,
    A,
    Aw,
    C,
    Ct,
    F,
    Mat,
    Opt,
    S,
    St,
    Vec,
    Wt,
    Xt,
    b0w,
    cov0,
    ed,
    fr,
    i0,
    j0,
    kurt,
    lemma,
    minvar,
    missing,
    mu,
    o,
    ot,
    rows,
    sch,
    sd,
    sdt,
    sig,
    smin,
    trade,
    u28,
    w0,
    w1,
    wd,
    years,
    yt,
)

ROOT = CM.ROOT
MD = ROOT / "src" / "lm28.md"
ANCHORS = ROOT / "plans" / "vol-5-anchors.md"

# ====================================================================== part 1: the anchors
OUT: list[str] = []
NEAR: list[str] = []


def put(value: str) -> None:
    """One anchor line; values that f() found near a rounding boundary are listed at its end."""
    tail = f" [NEAR a rounding boundary: {'; '.join(NEAR)}]" if NEAR else ""
    OUT.append(f"A28-{len(OUT) + 1:02d} {value}{tail}")
    NEAR.clear()


def f(x_: float, *ks: int, plus: bool = False) -> str:
    """x with max(ks) + 3 decimals; flagged for each printed precision k within 0.1 of a last-digit unit of a boundary."""
    x_ = float(x_)
    for k in ks:
        u = abs(x_) * 10**k
        if abs(u - floor(u) - 0.5) < 0.1:
            NEAR.append(f"{x_:.{k + 3}f} at {k} dp")
    return f"{x_:{'+' if plus else ''}.{max(ks) + 3}f}"


def tiny(x_: float, bound: float = 1e-15) -> str:
    """A residual: "below 1e-15" at machine precision, else two significant digits."""
    return f"below {bound:.0e}" if abs(x_) < bound else f"{abs(x_):.1e}"


def pct(v: Vec, *ks: int, plus: bool = False) -> str:
    return "(" + ", ".join(f(100 * float(z), *(ks or (1,)), plus=plus) for z in v) + ")"


def sum1(v: Vec, scale: float = 100.0) -> str:
    """The exact sum of scale * v's entries as printed at one decimal, each rounded separately."""
    return f"{sum((Decimal(f'{scale * float(z):.1f}') for z in v), Decimal(0)):.1f}"


# ---------------------------------------------------------------- data role
put(f"estimation frame T {len(fr.est_dates)} ({fr.est_dates[0]} .. {fr.est_dates[-1]}), A {f(A, 2, 3)}; wealth frame "
    f"{len(fr.wealth_dates)} sessions ({fr.wealth_dates[0]} .. {fr.wealth_dates[-1]}), A_w {f(Aw, 2, 3)}; "
    f"years {f(fr.years, 4)}")                                                                           # 01
put(f"first signal {sig} (estimation rows through it {rows}), trade {trade}; first window {WINDOW} rows {w0} .. {w1}; "
    f"T/A {f(WINDOW / A, 3, 4)}; calendar years from the close before the first return ({b0w}) "
    f"{f(years(b0w, w1), 2, 3)}; signals {len(sch)}, last {sch[-1][0]} (trade {sch[-1][1]})")         # 02
put(f"test period: wealth frame {len(Wt)} returns {wd[i0 + 1]} .. {wd[-1]}; estimation frame {len(Xt)} rows "
    f"{ed[j0]} .. {ed[-1]}; wealth dates not in the estimation frame {missing}; years from the trade close "
    f"{f(yt, 2, 3)}")                                                                                       # 03
put(f"r_f {RF} a year; r_f/A {f(RF / A * 1e4, 3, 4)} bp a day; r_f/A_w {f(RF / Aw * 1e4, 4)} bp a day")     # 04

# ---------------------------------------------------------------- first window: funds
put("window means A*mean " + ", ".join(f"{s} {f(100 * float(m), 1, 2)}%" for s, m in zip(F, mu, strict=True)))   # 05
put("window vols " + ", ".join(f"{s} {f(100 * v, 1, 2)}%" for s, v in zip(F, sd, strict=True)) + "; Sharpe (r_f 1.5%) "
    + ", ".join(f"{s} {f((m - RF) / v, 2, 3)}" for s, m, v in zip(F, mu, sd, strict=True)))            # 06
pairs = [(i, j) for i in range(5) for j in range(i + 1, 5)]
put("window correlations " + ", ".join(f"{F[i]}-{F[j]} {f(C[i, j], 2, 3, plus=True)}" for i, j in pairs))   # 07
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
put(f"w_mv {pct(o.wmv)}%; sigma_min {f(100 * sqrt(o.s2min), 2)}%; sigma_min^2 {f(o.s2min, 6, 7)}; mu_mv "
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
win_w: dict[str, Vec] = {}
for sg, _, rw in sch:
    xx = fr.X[rw - WINDOW:rw]
    oo = Opt(A * xx.mean(axis=0), A * cov0(xx))
    win_w[sg] = oo.wmv
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
put(f"U28 T {u.X.shape[0]} ({u.dates[0]} .. {u.dates[-1]}), A {f(u.A, 2, 4)}; w_mv shorts {int((ou.wmv < -1e-6).sum())} of 28; gross "
    f"{f(np.abs(ou.wmv).sum(), 2)}; sigma_min {f(100 * sqrt(ou.s2min), 2)}%; largest {u.names[int(ou.wmv.argmax())]} "
    f"{f(100 * ou.wmv.max(), 1)}%; most negative {u.names[int(ou.wmv.argmin())]} {f(100 * ou.wmv.min(), 1)}%; least "
    f"volatile sector {u.names[int(sdu.argmin())]} {f(100 * sdu.min(), 2)}%; equal weights {f(100 * sqrt(ew @ Su @ ew), 2)}% "
    f"(lm10.md:36 prints 15.75%); kappa(Sigma_hat) {f(evu[-1] / evu[0], 1)}")                            # 13
H = u.X.shape[0] // 2
hv = [Opt(u.A * part.mean(axis=0), u.A * cov0(part)) for part in (u.X[:H], u.X[-H:])]
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
slope = 0.01 * o.dir / o.srinf2
put(f"(28.4): weights move by {pct(slope, 1, 2, plus=True)} points per point of target mean; at mu_p = "
    f"10%: weights {pct(o.front_w(0.10))}%, vol {f(100 * sqrt(o.front_var(0.10)), 2)}%")               # 17

# ---------------------------------------------------------------- section 4: tangency and the CML
sr = sqrt(o.sr2)
st = sqrt(float(o.wtan @ S @ o.wtan))
k_best = int(np.argmax((mu - RF) / sd))
mtan = float(mu @ o.wtan)
gtan = mtan - o.mumv                                            # mu_tan - mu_mv
t_sep = (me - o.mumv) / gtan                                    # two-fund separation: E3's point on the w_mv-w_tan line
sep_gap = float(np.abs(wme - (o.wmv + t_sep * (o.wtan - o.wmv))).max())
put(f"1'Sigma^-1 e {f(o.den, 2, 3)} > 0 (mu_mv {f(100 * o.mumv, 2, 3)}% > r_f 1.5%); w_tan {pct(o.wtan)}%; mean "
    f"{f(100 * mtan, 2, 3)}%, vol {f(100 * st, 2, 3)}%; SR* {f(sr, 2, 3)}; gross {f(np.abs(o.wtan).sum(), 2)}; "
    f"best single fund {F[k_best]} {f((mu[k_best] - RF) / sd[k_best], 2, 3)}; mu_tan - mu_mv {f(100 * gtan, 4)} points; "
    f"E3's efficient weights = w_mv + t (w_tan - w_mv), t = (mu_p - mu_mv) / (mu_tan - mu_mv) {f(t_sep, 2, 3)} "
    f"(max gap {tiny(sep_gap)})")                                                                        # 18
put(f"(28.7): SR*^2 {f(o.sr2, 4)}; SR_inf^2 + ((mu_mv - r_f)/sigma_min)^2 {f(o.srinf2 + (o.mumv - RF) ** 2 / o.s2min, 4)}; "
    f"difference {tiny(o.sr2 - o.srinf2 - (o.mumv - RF) ** 2 / o.s2min)}; ((mu_mv - r_f)/sigma_min) "
    f"{f((o.mumv - RF) / sqrt(o.s2min), 3, 4)}")                                                          # 19
rfs = []
w646 = []
o_rf: list[Opt] = []
for r in (0.0, 0.02):
    orr = Opt(mu, S, r)
    w646.append(float(orr.wtan[1]))
    o_rf.append(orr)
    rfs.append(f"r_f {100 * r:.1f}%: w_tan {pct(orr.wtan)}%, SR* {f(sqrt(orr.sr2), 2, 3)}, 1'Sigma^-1 e {f(orr.den, 2)}")
put("; ".join(rfs) + f"; 00646's weight moves by {f(100 * (w646[1] - w646[0]), 0)} points from r_f 0 to 2%")  # 20
s10 = 0.10
dlt = sr / s10
fx = o.y / dlt
put(f"CML at vol 10%: mean r_f + SR* x 10% = {f(100 * (RF + sr * s10), 2)}%; delta = SR*/0.10 {f(dlt, 2)}; L = "
    f"1'Sigma^-1 e / delta {f(o.den / dlt, 2, 3)}; cash 1 - L {f(1 - o.den / dlt, 2)}; exposures {pct(fx, 1, 3)}%; check "
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
Sinv = np.linalg.solve(S, np.eye(5))                                                  # Sigma^-1 by solving
Jac = (np.eye(5) - np.outer(o.wtan, o.one)) @ Sinv / o.den
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
held: dict[str, dict[str, float]] = {}
for name, w in (("w_mv", o.wmv), ("w_tan", o.wtan)):
    r = Wt @ w
    T = len(r)
    s = float(r.std(ddof=0))
    vol = s * sqrt(Aw)
    kk = kurt(r)
    pv, pm = sqrt(float(w @ S @ w)), float(mu @ w)
    se_v, se_m = vol * sqrt((kk - 1) / (4 * T)), s * Aw / sqrt(T)
    held[name] = {"vol": vol, "mean": float(r.mean() * Aw), "pv": pv, "pm": pm, "se_v": se_v, "se_m": se_m, "kurt": kk,
                  "nse": vol / sqrt(2 * T), "g": float(np.log1p(r).sum()) / yt, "min": float((1 + r).min()), "T": T}
    put(f"{name} held {wd[i0 + 1]} .. {wd[-1]} (wealth frame, T {T}): predicted vol {f(100 * pv, 2)}%, "
        f"realized {f(100 * vol, 2)}% (SE {f(100 * se_v, 2)}, raw kurtosis {f(kk, 1, 2)}; normal "
        f"SE {f(100 * vol / sqrt(2 * T), 2)}); predicted mean {f(100 * pm, 2)}%, realized "
        f"{f(100 * float(r.mean()) * Aw, 2)}% (SE {f(100 * se_m, 1, 2)}); log growth "
        f"{f(100 * float(np.log1p(r).sum()) / yt, 2)}% a year; min 1 + R {f(float((1 + r).min()), 3, 4)}; "
        f"realized vol / predicted {f(vol / pv, 2)}; (realized - predicted) / SE: vol {f((vol - pv) / se_v, 0, 1)}, "
        f"mean {f((float(r.mean()) * Aw - pm) / se_m, 1)}")                                              # 29, 30
cf_tv = smin(np.outer(sdt, sdt) * C)        # the test volatilities with the window's correlations
cf_wv = smin(np.outer(sd, sd) * Ct)         # the window's volatilities with the test correlations
parts = []
split: dict[str, tuple[float, float]] = {}
for name, w in (("w_mv", o.wmv), ("w_tan", o.wtan)):
    dv = float((w - ot.wmv) @ St @ (w - ot.wmv))
    tot = float(w @ St @ w)
    split[name] = (dv, tot)
    vol_a = float((Wt @ w).std(ddof=0)) * sqrt(A)                # wealth frame on the estimation frame's A (not printed)
    parts.append(f"{name}: weight-error term {f(dv, 5, 6)}, total {f(tot, 5, 6)} (check {tiny(ot.s2min + dv - tot)}), vol "
                 f"{f(100 * sqrt(tot), 2)}% (wealth frame {f(100 * held[name]['vol'], 2)}%; on a common A {100 * vol_a:.5f}%), "
                 f"added by the weight error {f(100 * (sqrt(tot) - sqrt(ot.s2min)), 2)} points")
put(f"test period, estimation frame ({len(Xt)} rows): sigma_min^2 {f(ot.s2min, 5, 6)}, sigma_min {f(100 * sqrt(ot.s2min), 2)}% "
    f"(window {f(100 * sqrt(o.s2min), 2)}%; test vols with the window's correlations {f(100 * cf_tv, 2)}%, window vols "
    f"with the test correlations {100 * cf_wv:.5f}%); " + "; ".join(parts))                              # 31
put(f"test period ex post (in-sample on the test rows): w_mv {pct(ot.wmv)}%, mu_mv {f(100 * ot.mumv, 2)}%; w_tan "
    f"{pct(ot.wtan)}%, SR* {f(sqrt(ot.sr2), 2)}; 1'Sigma^-1 e {f(ot.den, 2)}; SR_inf {f(sqrt(ot.srinf2), 3)}")  # 32

# ---------------------------------------------------------------- section 7: Python
KKT = np.block([[2 * S, K.T], [K, np.zeros((2, 2))]])
sol = np.linalg.solve(KKT, np.concatenate([np.zeros(5), [1.0, me]]))
duals = []
cvx: dict[str, dict[str, float | str]] = {}
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
    wbound = 1e-11 if solver == cp.CLARABEL else 1e-15      # an interior-point gap prints as a bound
    sbound = 1e-13 if solver == cp.CLARABEL else 1e-15      # and so does its stationarity residual
    cvx[str(solver)] = {"status": str(prob.status), "wgap": float(np.abs(vv - wl).max()), "stat": float(stat),
                        "prim": float(prim), "d0": d0, "d1": d1}
    duals.append(f"{solver} {opts} status {prob.status}, max weight gap {tiny(np.abs(vv - wl).max(), wbound)}, "
                 f"objective gap "
                 f"{tiny((float(prob.value) - val) / val)}, KKT residuals: stationarity {tiny(stat, sbound)}, feasibility "
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


def pd_edge(inside_: float, outside: float) -> float:
    """Bisection on the sign of the smallest eigenvalue between a PD and a non-PD correlation."""
    assert np.linalg.eigvalsh(with_corr(inside_)).min() > 0 >= np.linalg.eigvalsh(with_corr(outside)).min()
    for _ in range(100):
        mid = 0.5 * (inside_ + outside)
        if np.linalg.eigvalsh(with_corr(mid)).min() > 0:
            inside_ = mid
        else:
            outside = mid
    return inside_


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
put("tangency betas, first window: (Sigma w_tan)_i / sigma_tan^2 (" + ", ".join(f(float(b), 2) for b in beta_tan)
    + f"); mu_tan - r_f {f(100 * (mtan - RF), 2)} points; "
    f"max |beta_i - e_i / (mu_tan - r_f)| {tiny(np.abs(beta_tan - o.e / (mtan - RF)).max())}; "
    f"max |Sigma w_tan - e / 1'Sigma^-1 e| {tiny(np.abs(Sw_tan - o.e / o.den).max())}")                 # 45
dE6 = 0.01 * col / dlt                                          # A28-28's exposure change, a fraction of capital
put("sums of the vectors printed at one decimal, each entry rounded separately, added exactly (exact sums: weights 100, "
    f"weight changes 0): w_mv {sum1(o.wmv)}; w_tan {sum1(o.wtan)}; E3's efficient weights {sum1(wme)}; w_tan at r_f 0 "
    f"{sum1(o_rf[0].wtan)} and at 2% {sum1(o_rf[1].wtan)}; ex-post w_mv {sum1(ot.wmv)} and w_tan {sum1(ot.wtan)}; the "
    f"widget's rounded-state w_tan {sum1(o_s.wtan)}; X3's columns "
    + ", ".join(f"{F[i]} {sum1(dW[:, i])}" for i in range(5))
    + f"; E5's exposures {sum1(fx)} (100 L {f(100 * o.den / dlt, 1)}); E6's exposure change {sum1(dE6)} (its exact "
    f"sum, the change in 100 L, {f(100 * float(dE6.sum()), 1)})")                                         # 46


def _anchor_values() -> dict[str, str]:
    rows_: dict[str, str] = {}
    sec = ANCHORS.read_text(encoding="utf-8").split("\n## LM28", 1)[1].split("\n## ", 1)[0]
    for line in sec.splitlines():
        if line.startswith("| A28-"):
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
            rows_[cells[0]] = cells[3].strip("`").replace("\\|", "|")
    return rows_


ANCHOR_ROWS = _anchor_values()
assert len(ANCHOR_ROWS) == 46 == len(OUT), (len(ANCHOR_ROWS), len(OUT))
ANCHOR_DIFFS: list[str] = []
for line in OUT:
    aid, got = line.split(" ", 1)
    tag = "ok" if got == ANCHOR_ROWS[aid] else "DIFFERS"
    print(f"ANCHOR {aid}: {tag}")
    if got != ANCHOR_ROWS[aid]:
        ANCHOR_DIFFS.append(f"{aid}:\n      script {got}\n      anchor {ANCHOR_ROWS[aid]}")

if "--anchors" in sys.argv:
    print(f"anchor differences ({len(ANCHOR_DIFFS)}):")
    for a_ in ANCHOR_DIFFS:
        print("   ", a_)
    sys.exit(0)

# ====================================================================== part 2: the text
def norm_text(s_: str) -> str:
    """The module text with TeX thousands separators, escaped percent signs, \\text{} and minus signs made plain."""
    s_ = s_.replace("{,}", ",").replace("\\%", "%").replace("\u2212", "-").replace("\\,", "")
    return re.sub(r"\\text\{\s*([^}]*)\}", r" \1", s_)


MD_RAW = MD.read_text(encoding="utf-8")
TEXT = norm_text(MD_RAW)
N_CHECKS = 0
COVERED: set[str] = set()


def in_text(printed: str) -> bool:
    """The printed number appears as a whole number (2.323 is not inside 2.3235, 0.32 not inside 10.32)."""
    return re.search(r"(?<![\d.])" + re.escape(printed) + r"(?![\d])", TEXT) is not None


def tie(value: float, fmt: str) -> bool:
    m_ = re.search(r"\.(\d+)", fmt)
    d_ = int(m_.group(1)) if m_ else 0
    if fmt.endswith(("e", "g")):
        return False
    scaled = abs(value) * 10**d_ * (100 if "%" in fmt else 1)
    return abs(scaled - math.floor(scaled) - 0.5) < 1e-6


def chk(label: str, value: float, fmt: str, printed: str, in_md: bool = True) -> None:
    global N_CHECKS
    got = format(value, fmt)
    print(f"CHECK {label}: {got} (printed {printed})")
    assert got == printed, (label, got, printed)
    assert not tie(value, fmt), ("rounding tie: print more digits", label, value)
    assert not in_md or in_text(printed), f"{label}: {printed!r} not found in src/lm28.md"
    COVERED.add(printed.lstrip("+-"))
    N_CHECKS += 1


def has(label: str, text: str) -> None:
    global N_CHECKS
    assert text in TEXT, f"{label}: {text!r} not found in src/lm28.md"
    print(f"CHECK {label}: '{text[:80]}' in text")
    for num in re.findall(r"\d[\d,]*\.?\d*", text):
        COVERED.add(num.rstrip(".,"))
    N_CHECKS += 1


def vec(label: str, values: Vec | list[float], printed: str, plus: bool = False) -> None:
    """A vector printed at one decimal in percent (or points): each entry from its unrounded value, no ties."""
    got = "(" + ", ".join(f"{100 * float(z):{'+' if plus else ''}.1f}" for z in values) + ")"
    for z in values:
        assert not tie(100 * float(z), ".1f"), (label, z)
    assert got == printed, (label, got, printed)
    has(label, printed)


# ---------------------------------------------------------------- data role, case box, notation, hygiene
assert (w0, w1, b0w, trade) == ("2017-02-13", "2019-02-27", "2017-02-10", "2019-03-04")
assert (wd[i0 + 1], wd[-1], ed[0]) == ("2019-03-05", "2026-10-08", "2017-01-18")
for d_ in ("13 February 2017", "27 February 2019", "4 March 2019", "8 October 2026", "5 March 2019", "18 January 2017"):
    has(f"date {d_}", d_)
chk("window rows", WINDOW, "d", "504")
chk("estimation frame T", len(fr.est_dates), ",d", "2,362")
chk("wealth frame sessions", len(fr.wealth_dates), ",d", "2,368")
chk("A", A, ".2f", "242.95")
chk("A_w", Aw, ".2f", "243.57")
chk("r_f / A in bp", RF / A * 1e4, ".3f", "0.617")
chk("test returns", len(Wt), ",d", "1,851")
chk("test rows", len(Xt), ",d", "1,845")
chk("test years", yt, ".2f", "7.60")
assert missing == ["2025-06-11", "2025-06-12", "2025-06-13", "2025-06-16", "2025-06-17", "2025-06-18"]
has("0050's halt", "There 0050 earns 0 during its halt from 11 to 17 June 2025 and its six-session return on 18 June. "
                   "Joint statistics use the 1,845 estimation rows, which lack those six sessions.")
j_halt = [k for k, d_ in enumerate(wd) if "2025-06-11" <= d_ <= "2025-06-17"]
assert len(j_halt) == 5 and not fr.traded[j_halt, 0].any() and (fr.W[j_halt, 0] == 0).all()
assert fr.traded[wd.index("2025-06-18"), 0] and wd[wd.index("2025-06-18") - 6] == "2025-06-10"
has("short threshold", "a short is a weight below $-10^{-6}$")
has("counts", "$T$ returns (504, 1,845, 1,851, 4,382), $N$ assets (5 or 28)")
chk("case: 1 point in SE units, under a sixth", 0.01 / se_mu[3], ".3f", "0.153", in_md=False)
assert 0.01 / se_mu[3] < 1 / 6
has("case: under a sixth", "under a sixth of its standard error")
chk("case: SR* 2 dp", sr, ".2f", "0.88")
held_mv, held_tan = held["w_mv"], held["w_tan"]
chk("case: twice", held_mv["vol"] / held_mv["pv"], ".2f", "2.00", in_md=False)
has("case: twice its prediction", "The first realizes 10.05%, twice its prediction; the second 14.15%")
chk("case: gold weight before", 100 * o.wtan[3], ".1f", "2.6")
chk("case: gold weight after", 100 * (o.wtan[3] + dW[3, 3]), ".1f", "12.8")
chk("case: bond weight", 100 * o.wmv[2], ".1f", "41.4")
# X1
for i, s_ in enumerate(F):
    row = (f"| {s_} | {100 * mu[i]:.1f} | {100 * sd[i]:.1f} | {100 * own[i][2]:.1f} | {100 * o.wmv[i]:.1f} | "
           f"{100 * o.wtan[i]:.1f} |")
    for z in (mu[i], sd[i], own[i][2], o.wmv[i], o.wtan[i]):
        assert not tie(100 * float(z), ".1f")
    has(f"X1 row {s_}", row)
has("X1 w_mv row", f"| $\\mathbf w^{{\\mathrm{{mv}}}}$ | {100 * held_mv['pv']:.2f} | {100 * held_mv['vol']:.2f} | "
                   f"{100 * held_mv['pm']:.2f} | {100 * held_mv['mean']:.2f} |")
has("X1 w_tan row", f"| $\\mathbf w^{{\\mathrm{{tan}}}}$ | {100 * held_tan['pv']:.2f} | {100 * held_tan['vol']:.2f} | "
                    f"{100 * held_tan['pm']:.2f} | {100 * held_tan['mean']:.2f} |")
chk("X1: largest own-date gap", 100 * gaps[jg], ".2f", "0.07")
assert F[jg] == "00642U"
assert sum1(o.wtan) == "100.1"
has("X1: w_tan sums to 100.1", "the $\\mathbf w^{\\mathrm{tan}}$ column, rounded separately, sums to 100.1")
# typicality
assert rank == 3 and len(srt) == 92
has("typicality", "Its minimum volatility ranks third lowest of the through case's 92 windows, whose minima run from "
                  "4.97% (31 May 2019) to 10.42% (31 March 2022)")
assert (srt[0][1], srt[-1][1]) == ("2019-05-31", "2022-03-31")
chk("92 windows lowest", 100 * srt[0][0], ".2f", "4.97")
chk("92 windows highest", 100 * srt[-1][0], ".2f", "10.42")
chk("signals", len(sch), "d", "92")

# ---------------------------------------------------------------- section 2
vec("E1 w_mv", o.wmv, "(10.7, 22.5, 41.4, 25.0, 0.4)")
chk("E1 sigma_min^2", o.s2min, ".7f", "0.0025152")
chk("E1 sigma_min", 100 * sqrt(o.s2min), ".2f", "5.02")
chk("E1 sqrt(0.002515)", 100 * sqrt(0.002515), ".2f", "5.01")
chk("E1 mu_mv", 100 * o.mumv, ".2f", "4.34")
chk("E1 lambda*", 2 * o.s2min, ".5f", "0.00503")
assert np.abs(cov_mv - o.s2min).max() < 1e-15 and np.abs(rc_share - o.wmv).max() < 1e-15
chk("E1 lowest fund vol", 100 * sd.min(), ".1f", "8.5")
assert F[int(sd.argmin())] == "00679B" and sqrt(o.s2min) < sd.min()
chk("E1 smallest weight", 100 * o.wmv.min(), ".2f", "0.36")
assert F[int(o.wmv.argmin())] == "00642U"
assert negw == 0 and r3gap < 1e-15
chk("E1 smallest weight in 92 windows", 100 * minw, ".2f", "0.13")
chk("E2 U28 T", u.X.shape[0], ",d", "4,382")
assert (u.dates[0], u.dates[-1]) == ("2008-12-02", "2026-10-08")
has("E2 dates", "4,382 returns from 2 December 2008 to 8 October 2026, $A=245.48$")
chk("E2 A", u.A, ".2f", "245.48")
chk("E2 shorts", int((ou.wmv < -1e-6).sum()), "d", "12")
chk("E2 gross", float(np.abs(ou.wmv).sum()), ".2f", "2.24")
chk("E2 sigma_min", 100 * sqrt(ou.s2min), ".2f", "10.98")
chk("E2 equal weights", 100 * sqrt(float(ew @ Su @ ew)), ".2f", "15.75")
chk("E2 least volatile", 100 * float(sdu.min()), ".2f", "13.67")
assert u.names[int(sdu.argmin())] == u.names[int(ou.wmv.argmax())] == "CommunicationsInternet"
chk("E2 largest weight", 100 * float(ou.wmv.max()), ".1f", "53.6")
assert u.names[int(ou.wmv.argmin())] == "Optoelectronic"
chk("E2 most negative", 100 * float(ou.wmv.min()), ".1f", "-10.8")
chk("E2 kappa", float(evu[-1] / evu[0]), ".1f", "108.1")
chk("E2 halves", H, ",d", "2,191")
chk("E2 half 1 shorts", int((hv[0].wmv < -1e-6).sum()), "d", "10")
chk("E2 half 2 shorts", int((hv[1].wmv < -1e-6).sum()), "d", "13")
chk("E2 half 1 gross", float(np.abs(hv[0].wmv).sum()), ".2f", "2.44")
chk("E2 half 2 gross", float(np.abs(hv[1].wmv).sum()), ".2f", "2.06")
chk("E2 cosine", cosh, ".3f", "0.690")
has("X5 note", "Twelve weights are negative, the gross exposure is 2.24 and $\\sigma_{\\min}=10.98%$")
chk("KC2 sqrt(lambda_N/N)", 100 * sqrt(ev5[0] / 5), ".2f", "3.18")
chk("KC2 equal weights", 100 * sN, ".2f", "7.38")
chk("KC2 sqrt(lambda_1/N)", 100 * sqrt(ev5[-1] / 5), ".2f", "10.69")
has("KC2 chain", "$3.18%\\le5.02%\\le7.38%\\le10.69%$")

# ---------------------------------------------------------------- section 3
chk("E3 equal weights mean", 100 * mN, ".3f", "3.913")
chk("E3 gap", 100 * (o.mumv - mN), ".2f", "0.42")
chk("E3 mu_mv", 100 * o.mumv, ".3f", "4.335")
chk("E3 SR_inf^2", o.srinf2, ".4f", "0.4554")
chk("E3 frontier vol at that mean (printed inputs)", 100 * sqrt(0.0025152 + 0.0042**2 / 0.4554), ".2f", "5.05")
chk("E3 frontier vol at that mean", 100 * sf, ".2f", "5.05")
has("E3 display", "\\sqrt{0.0025152+0.0042^2/0.4554}=5.05%")
chk("E3 efficient mean", 100 * me, ".2f", "7.99")
vec("E3 efficient weights", wme, "(11.7, 58.8, 38.1, 4.7, -13.3)")
chk("E3 lambda", lam[0], ".5f", "-0.00193")
chk("E3 mu_p - mu_mv", 100 * (me - o.mumv), ".4f", "3.6565")
chk("E3 lambda_mu (printed inputs)", 2 * 0.036565 / 0.4554, ".3f", "0.161")
chk("E3 lambda_mu", lam[1], ".3f", "0.161")
assert abs(lam[1] - 2 * (me - o.mumv) / o.srinf2) < 1e-13
assert abs(lam[0] - (2 * o.s2min - o.mumv * lam[1])) < 1e-15          # Deep Dive 1's lambda
has("E3 lambda_mu display", "\\frac{2\\times3.6565%}{0.4554}=0.161")
chk("E3 00646 slope", 100 * slope[1], "+.1f", "+9.9")
chk("E3 gold slope", 100 * slope[3], "+.1f", "-5.6")
has("E3 slopes", "moves 00646's weight by +9.9 points and gold's by -5.6")
chk("X2 SR_inf", sqrt(o.srinf2), ".3f", "0.675")

# ---------------------------------------------------------------- section 4
chk("E4 mu_mv - r_f", o.mumv - RF, ".5f", "0.02835")
chk("E4 1'S^-1 e (printed inputs)", 0.02835 / 0.0025152, ".2f", "11.27")
chk("E4 1'S^-1 e", o.den, ".2f", "11.27")
assert abs(o.den - (o.mumv - RF) / o.s2min) < 1e-12
vec("E4 w_tan", o.wtan, "(11.8, 62.6, 37.8, 2.6, -14.7)")
chk("E4 gross", float(np.abs(o.wtan).sum()), ".2f", "1.29")
chk("E4 mean", 100 * mtan, ".3f", "8.376")
chk("E4 vol", 100 * st, ".3f", "7.810")
chk("E4 SR* (printed inputs)", (8.376 - 1.5) / 7.810, ".3f", "0.880")
chk("E4 SR*", sr, ".3f", "0.880")
chk("E4 best single fund", float((mu[1] - RF) / sd[1]), ".2f", "0.72")
assert F[k_best] == "00646"
chk("E4 best single fund (rounded X1)", (10.0 - 1.5) / 11.9, ".2f", "0.71")
chk("E4 SR*^2", o.sr2, ".4f", "0.7750")
chk("E4 (mu_mv - r_f)/sigma_min", (o.mumv - RF) / sqrt(o.s2min), ".4f", "0.5653")
chk("E4 (28.7) from the printed parts", 0.4554 + 0.5653**2, ".4f", "0.7750")
has("E4 (28.7)", "$0.7750=0.4554+0.5653^2$")
chk("E4 t", t_sep, ".3f", "0.905")
chk("E4 mu_tan - mu_mv", 100 * gtan, ".4f", "4.0405")
chk("E4 t (printed inputs)", 3.6565 / 4.0405, ".3f", "0.905")
assert sep_gap < 1e-15
has("E4 separation", "$\\mathbf w^{\\mathrm{mv}}+0.905(\\mathbf w^{\\mathrm{tan}}-\\mathbf w^{\\mathrm{mv}})$, where "
                     "$0.905=3.6565/4.0405$")
assert np.abs(beta_tan - o.e / (mtan - RF)).max() < 1e-15
has("E4 betas", "equals $e_i/(\\mu_{\\tan}-r_f)$, to below $10^{-15}$")
vec("E4 w_tan at 0%", o_rf[0].wtan, "(11.4, 48.7, 39.1, 10.3, -9.5)")
chk("E4 SR* at 0%", sqrt(o_rf[0].sr2), ".2f", "1.10")
vec("E4 w_tan at 2%", o_rf[1].wtan, "(12.0, 71.1, 37.0, -2.2, -18.0)")
chk("E4 SR* at 2%", sqrt(o_rf[1].sr2), ".2f", "0.82")
assert sum1(o_rf[0].wtan) == "100.0" and sum1(o_rf[1].wtan) == "99.9"
has("E4 sums to 99.9", "(rounded separately; they sum to 99.9)")
chk("E4 00646 moves", 100 * (w646[1] - w646[0]), ".0f", "22")
chk("E5 CML mean (printed inputs)", 1.5 + 0.880 * 10, ".2f", "10.30")
chk("E5 CML mean", 100 * (RF + sr * s10), ".2f", "10.30")
chk("E5 delta (printed inputs)", 0.880 / 0.10, ".2f", "8.80")
chk("E5 delta", dlt, ".2f", "8.80")
chk("E5 L (printed inputs)", 11.27 / 8.80, ".2f", "1.28")
chk("E5 L", o.den / dlt, ".2f", "1.28")
chk("E5 borrowing", o.den / dlt - 1, ".2f", "0.28")
vec("E5 exposures", fx, "(15.1, 80.1, 48.4, 3.3, -18.9)")
chk("E5 oil exposure", 100 * fx[4], ".3f", "-18.860")
chk("E5 1.28 x -14.7", 1.28 * -14.7, ".1f", "-18.8")
chk("E5 delta with no cash", o.den, ".2f", "11.27")
assert abs(sqrt(float(fx @ S @ fx)) - 0.10) < 1e-15 and abs(sr / dlt - 0.10) < 1e-15
# pitfall: r_f >= mu_mv
chk("pitfall: windows", len(bad), "d", "22")
assert (b0, b1, inside) == ("2022-06-30", "2024-04-30", ["2024-03-29"])
has("pitfall: span", "every month-end from 30 June 2022 to 30 April 2024 except 29 March 2024")
chk("pitfall: 2024-03-29 denominator", gmax[0], ".3f", "0.614")
assert gmax[1] == "2024-03-29"
chk("pitfall: 2024-03-29 gross", gmax[2], ".1f", "29.1")
assert bw[1] == "2024-04-30"
chk("pitfall: mu_mv 2024-04-30", 100 * ob.mumv, ".2f", "1.34")
chk("pitfall: denominator 2024-04-30", ob.den, ".3f", "-0.185")
chk("pitfall: Sharpe", srn, ".2f", "-1.20")
assert abs(srn + sqrt(ob.sr2)) < 1e-12
chk("pitfall: gross 2024-04-30", bw[2], ".1f", "86.0")
chk("pitfall: SR_inf 2024-04-30", sqrt(ob.srinf2), ".4f", "1.2023")
for v_, p_ in zip(sup, ("0.7864", "1.1928", "1.2020"), strict=True):
    chk(f"pitfall: upper branch {p_}", v_, ".4f", p_)
assert sup[0] < sup[1] < sup[2] < sqrt(ob.srinf2)
has("pitfall: points above", "at 10, 100 and 1,000 points above")

# ---------------------------------------------------------------- section 5
for i, p_ in zip((3, 1, 0, 2, 4), ("+10.3", "+4.7", "+6.6", "+7.6", "+1.9"), strict=True):
    chk(f"X3 diagonal {F[i]}", 100 * dW[i, i], "+.1f", p_)
has("X3 diagonal sentence", "its diagonal runs from +1.9 points (oil) through +4.7 (00646), +6.6 (0050) and +7.6 "
                            "(00679B) to +10.3 (gold)")
chk("X3 linear gold", 100 * 0.01 * Jac[3, 3], ".1f", "11.2")
for i, p_ in enumerate(("9.4", "8.2", "5.9", "6.5", "16.1")):
    chk(f"SE of the mean {F[i]}", 100 * se_mu[i], ".1f", p_)
has("X3 SEs", "is 9.4, 8.2, 5.9, 6.5 and 16.1 points")
assert sum1(dW[:, 0]) == "-0.1" and sum1(dW[:, 1]) == "-0.1"
assert all(sum1(dW[:, i]) == "0.0" for i in (2, 3, 4))
has("X3 sums", "0050's and 00646's columns sum to -0.1, not 0")
chk("E6 gold mean", 100 * mu[3], ".2f", "0.78")
chk("E6 gold mean + 1", 100 * (mu[3] + 0.01), ".2f", "1.78")
chk("E6 SE units", 0.01 / se_mu[3], ".2f", "0.15")
chk("E6 weight before", 100 * o.wtan[3], ".3f", "2.576")
chk("E6 weight after", 100 * (o.wtan[3] + dW[3, 3]), ".3f", "12.845")
chk("E6 00679B's fall", -100 * dW[2, 3], ".1f", "5.7")
chk("E6 00646's fall", -100 * dW[1, 3], ".1f", "2.8")
has("E6 falls", "00679B's falls by 5.7 points and 00646's by 2.8")
vec("E6 exposure change", 0.01 * col / dlt, "(-2.0, +3.2, -3.6, +14.6, -0.9)", plus=True)
assert sum1(dE6) == "11.3"
chk("E6 L change", 100 * 0.01 * col.sum() / dlt, ".1f", "11.3")
assert abs(float(dE6.sum()) - 0.01 * col.sum() / dlt) < 1e-15
assert np.abs(dE6 - 0.01 * Sinv[:, 3] / dlt).max() < 1e-15
# the widget's paragraph and data
WJ = json.loads((ROOT / "src" / "data" / "lm28-frontierLab.json").read_text(encoding="utf-8"))["widget"]
assert WJ["mu"] == [float(z) for z in mu] and WJ["S"] == [[float(z) for z in r_] for r_ in S] and WJ["rf"] == RF
assert WJ["funds"] == list(F)
chk("widget slider 00646", 100 * mu[1], ".1f", "10.0")
chk("widget slider 00635U", 100 * mu[3], ".1f", "0.8")
chk("widget slider rho", C[0, 1], ".2f", "0.54")
assert (WJ["sliders"]["mu646"], WJ["sliders"]["mu635"], WJ["sliders"]["rho"]) == (10.0, 0.8, 0.54)
has("widget sliders", "(10.0%, 0.8% and 0.54)")
vec("widget rounded w_tan", o_s.wtan, "(11.8, 62.4, 37.8, 2.7, -14.7)")
chk("widget rounded SR*", sqrt(o_s.sr2), ".3f", "0.878")
chk("widget rounded mu_mv", 100 * o_s.mumv, ".2f", "4.33")
has("widget comparison", "against 62.6, 2.6, 0.880 and 4.34% for the window")
chk("widget PD low", lo_r, ".3f", "-0.736")
chk("widget PD high", hi_r, ".3f", "0.969")
assert lo_r > -0.74 and hi_r < 0.97                     # so the slider, in steps of 0.01, reaches both failures
has("widget PD sentence", "strictly between -0.736 and 0.969")
JS = (ROOT / "src" / "lm28.js").read_text(encoding="utf-8")
assert 'if (moved["fl-m1"]) mu[1] = v.mu646 / 100;' in JS and "if (!(s > 0)) return null;" in JS
assert "Σ is not positive definite: no frontier" in JS and "no tangency portfolio" in JS
has("summary sentence", "Two years of means cannot fix tangency weights to the nearest 10 points: a change of 0.15 "
                        "standard errors in gold's mean moves its weight by 10.3")

# ---------------------------------------------------------------- section 6
chk("held: min 1 + R, w_mv", held_mv["min"], ".3f", "0.949")
chk("held: min 1 + R, w_tan", held_tan["min"], ".3f", "0.929")
assert held_mv["T"] == held_tan["T"] == 1851
chk("E7 sigma_min^2 test", ot.s2min, ".5f", "0.00927")
chk("E7 sigma_min test", 100 * sqrt(ot.s2min), ".2f", "9.63")
chk("E7 w_mv weight error", split["w_mv"][0], ".5f", "0.00081")
chk("E7 w_mv total", split["w_mv"][1], ".5f", "0.01008")
chk("E7 w_tan weight error", split["w_tan"][0], ".5f", "0.01071")
chk("E7 w_tan total", split["w_tan"][1], ".5f", "0.01998")
chk("E7 w_mv parts (printed)", 0.00927 + 0.00081, ".5f", "0.01008")
chk("E7 w_tan parts (printed)", 0.00927 + 0.01071, ".5f", "0.01998")
has("E7 split", "0.00927+0.00081=0.01008")
has("E7 split tan", "0.00927+0.01071=0.01998")
chk("E7 w_mv vol", 100 * sqrt(split["w_mv"][1]), ".2f", "10.04")
chk("E7 w_tan vol", 100 * sqrt(split["w_tan"][1]), ".2f", "14.14")
chk("E7 w_mv added", 100 * (sqrt(split["w_mv"][1]) - sqrt(ot.s2min)), ".2f", "0.41")
chk("E7 w_tan added", 100 * (sqrt(split["w_tan"][1]) - sqrt(ot.s2min)), ".2f", "4.51")
chk("E7 added (printed)", 10.04 - 9.63, ".2f", "0.41")
chk("E7 added tan (printed)", 14.14 - 9.63, ".2f", "4.51")
for name_, w_ in (("w_mv", o.wmv), ("w_tan", o.wtan)):
    vol_a_ = float((Wt @ w_).std(ddof=0)) * sqrt(A)
    assert vol_a_ < sqrt(split[name_][1]) < held[name_]["vol"]        # "on a common A those sessions lower both"
vec("E7 ex-post w_mv", ot.wmv, "(8.0, 22.4, 46.1, 17.0, 6.5)")
vec("E7 ex-post w_tan", ot.wtan, "(69.7, 8.8, -11.9, 27.6, 5.9)")
assert sum1(ot.wtan) == "100.1" and sum1(ot.wmv) == "100.0"
has("E7 sums", "(rounded separately; it sums to 100.1)")
chk("X4 test minimum mean", 100 * ot.mumv, ".2f", "8.22")
chk("E8 w_mv vol", 100 * held_mv["vol"], ".2f", "10.05")
chk("E8 w_mv SE", 100 * held_mv["se_v"], ".2f", "0.40")
chk("E8 kurtosis", held_mv["kurt"], ".1f", "12.6")
chk("E8 w_mv SE (printed inputs)", 10.05 * sqrt((12.6 - 1) / (4 * 1851)), ".2f", "0.40")
chk("E8 w_mv mean", 100 * held_mv["mean"], ".2f", "9.14")
chk("E8 w_mv mean SE", 100 * held_mv["se_m"], ".1f", "3.6")
chk("E8 w_mv growth", 100 * held_mv["g"], ".2f", "8.63")
chk("E8 w_tan vol", 100 * held_tan["vol"], ".2f", "14.15")
chk("E8 w_tan SE", 100 * held_tan["se_v"], ".2f", "0.53")
chk("E8 w_tan mean", 100 * held_tan["mean"], ".2f", "10.79")
chk("E8 w_tan mean SE", 100 * held_tan["se_m"], ".1f", "5.1")
chk("E8 w_tan growth", 100 * held_tan["g"], ".2f", "9.79")
chk("E8 w_tan predicted mean", 100 * held_tan["pm"], ".2f", "8.38")
chk("E8 w_mv vol gap (printed)", (10.05 - 5.02) / 0.40, ".0f", "13")
chk("E8 w_tan vol gap (printed)", (14.15 - 7.81) / 0.53, ".0f", "12")
chk("E8 w_mv vol gap", (held_mv["vol"] - held_mv["pv"]) / held_mv["se_v"], ".0f", "13")
chk("E8 w_tan vol gap", (held_tan["vol"] - held_tan["pv"]) / held_tan["se_v"], ".0f", "12")
chk("E8 w_mv mean gap", (held_mv["mean"] - held_mv["pm"]) / held_mv["se_m"], ".1f", "1.3")
chk("E8 w_tan mean gap", (held_tan["mean"] - held_tan["pm"]) / held_tan["se_m"], ".1f", "0.5")
chk("E8 w_mv mean gap (printed)", (9.14 - 4.34) / 3.6, ".1f", "1.3")
chk("E8 w_tan mean gap (printed)", (10.79 - 8.38) / 5.1, ".1f", "0.5")
has("E8 gap display", "$(10.05-5.02)/0.40$ and $(14.15-7.81)/0.53$")
assert (sdt > sd).all()                                                # "every fund's volatility rose"
for (i, j), p0, p1 in (((0, 2), "-0.30", "-0.09"), ((1, 2), "-0.26", "-0.06")):
    chk(f"E8 window corr {F[i]}-{F[j]}", C[i, j], ".2f", p0)
    chk(f"E8 test corr {F[i]}-{F[j]}", Ct[i, j], ".2f", p1)
has("E8 correlations", "0050–00679B from -0.30 to -0.09 and 00646–00679B from -0.26 to -0.06")
chk("E8 counterfactual", 100 * cf_tv, ".2f", "8.35")
chk("normal-days SE", 100 * held_mv["nse"], ".2f", "0.17")

# ---------------------------------------------------------------- section 7
assert np.abs(sol[:5] - wl).max() < 1e-15 and np.abs(sol[:5] - wme).max() < 1e-15
osqp, clar = cvx[str(cp.OSQP)], cvx[str(cp.CLARABEL)]
assert osqp["status"] == clar["status"] == "optimal"
assert float(osqp["wgap"]) < 1e-15 and float(clar["wgap"]) < 1e-11
assert max(float(osqp["stat"]), float(osqp["prim"]), float(clar["stat"]), float(clar["prim"])) < 1e-13
for k_, p_ in (("d0", "+0.00193"), ("d1", "-0.161")):
    chk(f"E9 OSQP dual {k_}", float(osqp[k_]), "+.5f" if k_ == "d0" else "+.3f", p_)
    chk(f"E9 CLARABEL dual {k_}", float(clar[k_]), "+.5f" if k_ == "d0" else "+.3f", p_)
assert abs(float(osqp["d0"]) + lam[0]) < 1e-9 and abs(float(osqp["d1"]) + lam[1]) < 1e-9
assert (version("cvxpy"), version("osqp"), version("clarabel")) == ("1.9.3", "1.1.3", "0.11.1")
assert OSQP_OPTS["eps_abs"] == OSQP_OPTS["eps_rel"] == 1e-10 and OSQP_OPTS["polishing"] is True
assert CLARABEL_OPTS == {"tol_gap_abs": 1e-12, "tol_gap_rel": 1e-12, "tol_feas": 1e-12}
has("E9 versions", "cvxpy 1.9.3")
has("E9 OSQP", "OSQP 1.1.3 runs with `eps_abs` and `eps_rel` $10^{-10}$ and polishing")
has("E9 CLARABEL", "CLARABEL 0.11.1 with `tol_gap_abs`, `tol_gap_rel` and `tol_feas` $10^{-12}$")
has("E9 gaps", "below $10^{-15}$ (OSQP) and below $10^{-11}$ (CLARABEL, an interior-point method)")
has("E9 residuals", "are below $10^{-13}$")
has("code: A and r_f", "A = 242.95, rf = 0.015")
has("E1 sqrt", "$\\sqrt{0.002515}$ would give 5.01%")
has("E5 delta display", "$\\delta=0.880/0.10=8.80$")
has("P2 rho", "correlation $\\rho=0.6$")
has("P4 A", "**A.** 0.50")
has("S3 display", "$\\sigma_p^2=0.05^2+0.04^2/0.5^2=0.0089$")

# ---------------------------------------------------------------- problems and solutions
chk("P1 key B", 100 * o3.wmv[0], ".1f", "66.7")
chk("P1 A", 100 * 10 / 20, ".1f", "50.0")
chk("P1 C", 100 / 3, ".1f", "33.3")
chk("S1 sigma_min", 100 * sqrt(o3.s2min), ".2f", "8.16")
chk("S1 sigma_min (printed)", 100 * sqrt(1 / 150), ".2f", "8.16")
has("S1 inverse variances", "$\\Sigma^{-1}\\mathbf 1=(100, 25, 25)$")
chk("P2 key A", 100 * o2.wmv[0], ".1f", "-7.7")
chk("P2 C", 100 * 0.01 / (0.04 + 0.01), ".1f", "20.0")
chk("S2 (7.7) (printed)", 100 * (0.01 - 0.012) / (0.04 + 0.01 - 0.024), ".1f", "-7.7")
has("S2 display", "$(0.01-0.012)/(0.04+0.01-0.024)=-7.7%$")
chk("P3 key C", 100 * p3, ".2f", "9.43")
chk("P3 A", 100 * (0.05 + 0.04 / 0.5), ".1f", "13.0")
chk("P3 B", 100 * 0.04 / 0.5, ".1f", "8.0")
chk("S3 variance", 0.05**2 + 0.04**2 / 0.5**2, ".4f", "0.0089")
chk("P4 key B", p4, ".3f", "0.707")
chk("P4 C", 0.5 + 0.5, ".2f", "1.00")
chk("S4 SR*^2", 0.5**2 + (0.025 / 0.05) ** 2, ".1f", "0.5")
chk("S4 mu_tan", 100 * (0.015 + 0.5 * 0.0025 / 0.025), ".2f", "6.50")
has("S4 mu_tan", "$\\mu_{\\tan}=1.5%+0.5\\times0.0025/0.025=6.50%$")
chk("P5 key A vol", 100 * 0.8 / 4, ".0f", "20")
chk("P5 key A L", 8 / 4, ".1f", "2.0")
chk("P5 B", 4 / 8, ".1f", "0.5")
chk("P5 C", 100 * 0.8 * 4, ".0f", "320")
has("S6 the window", "on 30 April 2024 it was -1.20")
chk("S9 numerator", 0.018353 + 0.004908, ".6f", "0.023261")
chk("S9 denominator", 0.026800 + 0.018353 + 2 * 0.004908, ".6f", "0.054969")
chk("S9 weight", 100 * o7.wmv[0], ".1f", "42.3")
chk("S9 weight (printed)", 100 * 0.023261 / 0.054969, ".1f", "42.3")
chk("S9 sigma_min", 100 * sqrt(o7.s2min), ".2f", "9.22")
chk("S9 lambda*", 2 * o7.s2min, ".4f", "0.0170")
has("S9 inputs", "$\\sigma_1^2=0.026800$, $\\sigma_2^2=0.018353$ and $\\sigma_{12}=-0.004908$")
for i, p_ in enumerate(("+6.6", "-6.4", "+0.8", "-1.6", "+0.5")):
    chk(f"S10 change {F[i]}", 100 * dW[i, 0], "+.1f", p_)
has("S10 changes", "+6.6 points in 0050, -6.4 in 00646, and +0.8, -1.6 and +0.5 in the others")
vec("S10 column 1", 0.01 * col1, "(82.8, -48.1, 25.8, -17.3, -0.7)")
chk("S10 1 point in SE units", 0.01 / se_mu[0], ".2f", "0.11")
chk("S10 1 point in SE units (printed)", 1 / 9.4, ".2f", "0.11")
assert min(abs(dW[0, 0]), abs(dW[1, 0])) > 0.06
has("S10 more than 6", "moves two weights by more than 6 points")
has("S11 duals", "the duals +0.00193 and -0.161 are the negatives of LM7's multipliers")

# ---------------------------------------------------------------- the chart files
FJ = json.loads((ROOT / "src" / "data" / "lm28-frontier.json").read_text(encoding="utf-8"))
pts_ = {p["label"]: p["at"] for p in FJ["points"] if "label" in p}
assert [f"{v:.2f}" for v in pts_["minimum variance"]] == ["5.02", "4.34"]
assert [f"{v:.2f}" for v in pts_["tangency"]] == ["7.81", "8.38"]
assert [f"{v:.2f}" for v in pts_["equal weights"]] == ["7.38", "3.91"]
small = [p["at"] for p in FJ["points"] if "label" not in p]
assert [f"{small[0][0]:.2f}", f"{small[1][1]:.2f}"] == ["5.05", "7.99"]
assert FJ["series"][0]["labels"] == list(F)
HJ = json.loads((ROOT / "src" / "data" / "lm28-heldout.json").read_text(encoding="utf-8"))
assert [[f"{z:.2f}" for z in v_["from"] + v_["to"]] for v_ in HJ["vectors"]] == [
    ["5.02", "4.34", "10.05", "9.14"], ["7.81", "8.38", "14.15", "10.79"]]
assert [f"{z:.2f}" for z in HJ["points"][0]["at"]] == ["9.63", "8.22"]
XJ = json.loads((ROOT / "src" / "data" / "lm28-sensitivity.json").read_text(encoding="utf-8"))
assert np.abs(np.array(XJ["matrix"]) - 100 * dW).max() < 1e-4
UJ = json.loads((ROOT / "src" / "data" / "lm28-u28mv.json").read_text(encoding="utf-8"))
uv_ = UJ["series"][0]["values"]
assert len(uv_) == 28 and sum(v_ < 0 for v_ in uv_) == 12 and f"{100 * max(uv_):.1f}" == "53.6"
assert f"{100 * min(uv_):.1f}" == "-10.8" and UJ["categories"][0] == "CommunicationsInternet"
print("chart files: points, vectors, cells and weights match the text")

# ====================================================================== structure: labels and citations
ex_labels = re.findall(r"\[!exhibit\][^\n]*\{#([\w-]+)\}", MD_RAW)
eg_labels = re.findall(r"\[!example\][^\n]*\{#([\w-]+)\}", MD_RAW)
assert ex_labels == ["case", "u28w", "frontier", "sensitivity", "heldout"], ex_labels
assert eg_labels == ["mv5", "u28mv", "inside", "tan5", "cml10", "bump", "held", "realized", "kkt"], eg_labels
assert len(set(ex_labels) | set(eg_labels)) == len(ex_labels) + len(eg_labels), "a label is used twice"
for lab_ in ex_labels:
    assert f"[[ex:{lab_}]]" in MD_RAW, f"exhibit {lab_} is never cited"
for kind, lab_ in re.findall(r"\[\[(ex|eg):([\w-]+)\]\]", MD_RAW):
    assert lab_ in (ex_labels if kind == "ex" else eg_labels), (kind, lab_)
tags = re.findall(r"\\tag\{(28\.\d+)\}", MD_RAW)
assert tags == [f"28.{k}" for k in range(1, 10)], tags
for name_ in re.findall(r'data-chart="(lm28-[\w-]+)"', MD_RAW):
    assert (ROOT / "src" / "data" / f"{name_}.json").exists(), name_
assert MD_RAW.count("> [!kc]") == 6 and MD_RAW.count("> [!zh]") == 5
for form in ("最小變異數投資組合（minimum-variance portfolio）", "效率前緣（efficient frontier）", "拋物線（parabola）",
             "雙曲線（hyperbola）", "漸近線（asymptote）", "兩基金分離（two-fund separation）", "分離定理（separation theorem）",
             "切點投資組合（tangency portfolio）", "資本市場線（capital market line）", "無風險資產（risk-free asset）",
             "無風險利率（risk-free rate）", "風險規避（risk aversion）", "敏感度（sensitivity）", "估計誤差（estimation error）",
             "拉格朗日乘數（Lagrange multiplier）", "共變異數矩陣（covariance matrix）", "凸函數（convex function）",
             "樣本外（out-of-sample）", "樣本內（in-sample）"):
    assert form in MD_RAW, form
assert "切點組合" not in MD_RAW.replace("切點投資組合", "")
print(f"labels: {len(ex_labels)} exhibits, {len(eg_labels)} examples, tags (28.1)-(28.9), every exhibit cited")

# ====================================================================== report
body = TEXT.split("\n## Glossary", 1)[0]
nums = set(re.findall(r"(?<![\w.])\d+\.\d+|(?<![\w.,])\d{1,3}(?:,\d{3})+", body))
left = sorted(n for n in nums if n not in COVERED)
print(f"\nnumbers with a decimal point or thousands separator not covered by a check ({len(left)}):")
print("   " + " ".join(left))
print(f"\nanchor differences ({len(ANCHOR_DIFFS)}):")
for a_ in ANCHOR_DIFFS:
    print("   ", a_)
print(f"\nall {N_CHECKS} checks passed")
sys.exit(0)
