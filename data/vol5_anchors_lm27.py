"""LM27 anchors (Portfolio Return and Risk): every number the Stage 1 brief quotes (drafted 2026-10-24; revised the
same day to the editor's decisions on the briefs, plans/vol-5.md: printed precisions that let each derived figure
follow from its printed inputs, R1's and R2's mu_p, the widget's monthly and window matrices, Problem 6's stem; and
again to the second recomputation and cross-check: the daily-monthly gaps of A27-11, the weekly year count of A27-12
from closes (decision C7), Problem 1's flag, A27-46's comparison and the funds' raw kurtosis, A27-50; and a third time
on 2026-10-25 to the last verification and plans/vol-5.md, "Decisions on the third revision": A27-11's two gap
statements are scoped to the five pairs the brief shows, with the figures over all ten pairs beside them, and its
00679B-00642U gap is marked as computed from the unrounded correlations; A27-46 is withdrawn, since the shared
decision's note that it checked is dropped; its ID is kept so that later IDs do not move).

Reads only data/processed/*.parquet, through the shared builders (run them first; this script runs neither):
  * E5 (plans/vol-5.md, "Data"): vol5_series.frames("E5"), which reads data/processed/vol5_frames.parquet (built and
    checked by data/vol5_series.py from FinMind's TaiwanStockPrice, TaiwanStockDividendResult and
    TaiwanStockSplitPrice): 0050, 00646, 00679B, 00635U and 00642U, daily total returns (P_t + D_t) / P_prev - 1, with
    the previous close restated per current share on a split day (P_prev / 4 for 0050 on 2025-06-18; no split-ratio
    symbol, decision B6), from the base close 2017-01-17 to 2026-10-08. The estimation frame keeps the dates on which
    every fund has a one-session return (T = 2,362); the wealth frame keeps every TR23 session after the base (2,368),
    a halted fund earning 0 and its spanning return booked on the day it trades again. vol5_series.ohlc() gives the
    checked closes.
  * The through case: vol5_rules.schedule() (the 92 month-end signals and their trade dates), vol5_rules.signals()
    and vol5_rules.wealth_path() (R1 and R2, costs, the wealth recursion), vol5_rules.cov0() (divisor T). No rule is
    re-implemented; the trade of 2026-04-01 is replayed from the shared path only to show the recursion's parts.
  * U28 (Volume II): data/lm10_series.py's u28(), which reads data/processed/vol2_closes.parquet (built and repaired
    by data/vol2_series.py): the 28 leaf TWSE sector price indices and the TAIEX price index, T = 4,382 simple daily
    price returns 2008-12-02 .. 2026-10-08, A = 245.4794.

Conventions. Simple returns throughout (portfolio returns aggregate them; plans/vol-5.md, "Return type"). Means,
variances, covariances and correlations divide by T (ddof=0, passed explicitly; cov0). Annualization: A times a mean
or a covariance, sqrt(A) times a standard deviation, with E5's estimation-frame A = 2,362 / years = 242.951422 (years
= calendar days / 365.25 from the base close 2017-01-17, the close before the first return, to the last close, so
A = 2,362 x 365.25 / 3,551 as lm10.md:41 writes it; decision C7), U28's A = 245.4794; weekly statistics use the
periods a year as LM19 counts them (lm19.md:39): the 500 weeks with a session over the years from the close before
the first weekly return to the last weekly close (the same 3,542 days as the 506 calendar weeks they span; six Lunar
New Year weeks have no session); monthly ones A = 12 (plans/vol-5.md, "Sharpe ratio"). Weekly and monthly returns
compound the estimation frame's daily returns inside ISO weeks (Monday to Sunday; keys (ISO year, ISO week)) and
calendar months; the first and last period, in which the sample starts (Wednesday 2017-01-18) and ends (Thursday
2026-10-08), are dropped, complete or not (plans/vol-5.md, "Weeks and months"; the last week, 2026-W41, holds all
four of its sessions). A27-10 prints what keeping the last week would change.
Risk decomposition of weights w under a covariance matrix S: Cov(R_i, R_p) = (S w)_i, beta_{i,p} = (S w)_i / w'S w,
MRC_i = (S w)_i / sqrt(w'S w), RC_i = w_i MRC_i, share_i = RC_i / sqrt(w'S w) = w_i beta_{i,p}; annualized volatility
units multiply MRC_i, RC_i and sqrt(w'S w) by sqrt(A). "Full sample" is the estimation frame, 2,362 dates; a "window"
is the trailing 504 rows of the estimation frame through a signal (vol5_rules.schedule). A correlation's normal-theory
standard error is (1 - rho^2) / sqrt(T) (LM20, Practice Problem 6, lm20.md:558); the plug-in one is sd(L_t) / sqrt(T)
with L_t = x_t y_t - (rho / 2)(x_t^2 + y_t^2) on standardized returns (divisor T), as that problem defines it. Both
assume independent periods; the plug-in one needs finite fourth moments, so A27-50 prints each fund's raw kurtosis
(LM19's (19.3), divisor T).
Costs (plans/vol-5.md, "Cost model"): commission 0.1425% of the value traded on each side (the posted reference on
both markets: TWSE's rules for 0050, 00646, 00635U and 00642U, TPEx's for 00679B; LM34 prints the sources), tax 0.1%
on sales of every E5 fund except 00679B (0); the post-trade wealth solves W_post = W_pre - cost(W_post f - W_pre w_drift). The factor split on U28: OLS
of each sector on the TAIEX price index with an intercept (LM23's (23.1)); the book's market beta is w'beta; the
residual covariance matrix S_res divides by T; sigma_p^2 = (w'beta)^2 var(R_mkt) + w'S_res w holds exactly in sample.
Numbers printed by published modules are echoed with their file:line and recomputed here.

Rounding flags. Every number the brief prints passes through f(x, k1, k2, ...), which shows x with max(k) + 3 decimals
and flags it "NEAR" for each printed precision k at which x lies within a tenth of a last-digit unit of a rounding
boundary (|frac(10^k |x|) - 0.5| < 0.1). The brief prints a flagged value as rounded from the unrounded value here.
Percentages are passed to f() in percent.

Prints one line per anchor, "A27-NN <value>", in ID order, and writes nothing.

Run:  PYTHONUTF8=1 uv run python data/vol5_anchors_lm27.py
"""
import sys
from datetime import date
from fractions import Fraction
from math import floor, sqrt
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lm10_series import u28
from vol5_rules import COMMISSION, R2, TAX, WINDOW, cov0, schedule, signals, wealth_path
from vol5_series import frames, ohlc

Vec = NDArray[np.float64]
Mat = NDArray[np.float64]

OUT: list[str] = []
NEAR: list[str] = []


def put(value: str) -> None:
    """One anchor line; values that f() found near a rounding boundary are listed at its end."""
    tail = f" [NEAR a rounding boundary: {'; '.join(NEAR)}]" if NEAR else ""
    OUT.append(f"A27-{len(OUT) + 1:02d} {value}{tail}")
    NEAR.clear()


def f(x: float, *ks: int, plus: bool = False) -> str:
    """x with max(ks) + 3 decimals; flagged for each printed precision k within 0.1 of a last-digit unit of a boundary."""
    x = float(x)
    for k in ks:
        u = abs(x) * 10**k
        if abs(u - floor(u) - 0.5) < 0.1:
            NEAR.append(f"{x:.{k + 3}f} at {k} dp")
    return f"{x:{'+' if plus else ''}.{max(ks) + 3}f}"


def fl(xs: Vec | list[float], *ks: int) -> str:
    return ", ".join(f(float(x), *ks) for x in xs)


def corr_mat(x: Mat) -> Mat:
    S = cov0(x)
    sd = np.sqrt(np.diag(S))
    return S / np.outer(sd, sd)


def split(S: Mat, w: Vec) -> tuple[float, Vec, Vec, Vec, Vec]:
    """(sigma_p, beta_{i,p}, MRC, RC, shares) of weights w under S, in S's units."""
    Sw = S @ w
    v = float(w @ Sw)
    sp = sqrt(v)
    return sp, Sw / v, Sw / sp, w * Sw / sp, w * Sw / v


def wkey(d: str) -> str:
    """The ISO week of a date, keyed (ISO year, ISO week)."""
    y, wk, _ = date.fromisoformat(d).isocalendar()
    return f"{y}-W{wk:02d}"


def periods(dates: list[str], R: Mat, key: str, drop: bool = True) -> tuple[list[str], Mat]:
    """Compound daily returns within ISO weeks ("week") or calendar months ("month"); drop the first and last period
    (complete or not) unless drop is False."""
    def k(d: str) -> str:
        return d[:7] if key == "month" else wkey(d)
    keys: list[str] = []
    rows: list[Vec] = []
    for d, r in zip(dates, R, strict=True):
        if not keys or k(d) != keys[-1]:
            keys.append(k(d))
            rows.append(np.ones(R.shape[1]))
        rows[-1] = rows[-1] * (1 + r)
    G = np.array(rows) - 1
    return (keys[1:-1], G[1:-1]) if drop else (keys, G)


def se_rho(x: Vec, y: Vec) -> tuple[float, float, float]:
    """(rho, normal-theory SE, plug-in SE) as LM20's Practice Problem 6 defines them (divisor T)."""
    xs = (x - x.mean()) / x.std(ddof=0)
    ys = (y - y.mean()) / y.std(ddof=0)
    r = float(np.mean(xs * ys))
    L = xs * ys - r / 2 * (xs**2 + ys**2)
    n = len(x)
    return r, (1 - r * r) / sqrt(n), float(L.std(ddof=0)) / sqrt(n)


def post_trade(W: float, drift: Vec, f_: Vec, tax: Vec) -> float:
    """Closed form of W_post = W - cost(W_post f - W drift) once every trade's sign is known (taken at W_post = W)."""
    buy = W * f_ - W * drift > 0
    k = COMMISSION
    num = W + k * W * drift[buy].sum() - k * W * drift[~buy].sum() - float(tax[~buy] @ (W * drift[~buy]))
    den = 1 + k * f_[buy].sum() - k * f_[~buy].sum() - float(tax[~buy] @ f_[~buy])
    return float(num / den)


# ---------------------------------------------------------------- E5 and its two frames
fr = frames("E5")
F = fr.funds
N = len(F)
J = {s: i for i, s in enumerate(F)}
T = len(fr.est_dates)
A = fr.A
days = (date.fromisoformat(fr.wealth_dates[-1]) - date.fromisoformat(fr.base)).days
put(f"E5 funds {', '.join(F)}; base close {fr.base}; last close {fr.wealth_dates[-1]}; {days} calendar days; "
    f"years {f(fr.years, 4)}")                                                                               # 01
assert abs(A - T * 365.25 / days) < 1e-12 and abs(fr.A_wealth - len(fr.wealth_dates) * 365.25 / days) < 1e-12
put(f"estimation frame T {T}, {fr.est_dates[0]} .. {fr.est_dates[-1]}; A = T / years = {T} x 365.25 / {days} "
    f"{f(A, 2, 3)}")                                                                                       # 02
est = set(fr.est_dates)
only_w = [d for d in fr.wealth_dates if d not in est]
halted = [(F[j], fr.wealth_dates[i]) for i, j in zip(*np.nonzero(~fr.traded), strict=True)]
put(f"wealth frame {len(fr.wealth_dates)} sessions, {fr.wealth_dates[0]} .. {fr.wealth_dates[-1]}; A_w = "
    f"{len(fr.wealth_dates)} x 365.25 / {days} {f(fr.A_wealth, 2, 3)}; dates in the wealth frame only: "
    f"{', '.join(only_w)} ({len(only_w)}); halted fund-days {len(halted)} ({', '.join(sorted({s for s, _ in halted}))})"
    )                                                                                                      # 03
c50 = {d: Fraction(str(c)) for d, c in ohlc("0050").select("date", "close").iter_rows()}
r_split = 4 * c50["2025-06-18"] / c50["2025-06-10"] - 1
iw = fr.wealth_dates.index("2025-06-18")
assert abs(float(r_split) - fr.W[iw, J["0050"]]) < 1e-15
assert all(fr.W[fr.wealth_dates.index(d), J["0050"]] == 0 for d in only_w[:-1])
put(f"0050: close {float(c50['2025-06-10']):.2f} on 2025-06-10, {float(c50['2025-06-18']):.2f} on 2025-06-18 after "
    f"the 4-for-1 split; total return 4 x {float(c50['2025-06-18']):.2f} / {float(c50['2025-06-10']):.2f} - 1 = "
    f"{f(100 * float(r_split), 2, 3)}% (exact fraction {r_split}); flat on the 5 halted sessions")                                                  # 04
i0 = fr.wealth_dates.index("2025-06-10")
G_span = np.prod(1 + fr.W[i0 + 1:iw + 1], axis=0)
eq_span = float(G_span.mean() - 1)
log_avg = float(np.exp(np.log(G_span).mean()) - 1)
log_sum = float(np.log(G_span).mean())
log_sigs: list[str] = []
sigs = signals(fr, log_sigs)
p1 = wealth_path(fr, sigs, "R1")
p2 = wealth_path(fr, sigs, "R2")
j0, j1 = p1.dates.index("2025-06-10"), p1.dates.index("2025-06-18")
r1_span = float(p1.wealth[j1] / p1.wealth[j0] - 1)
put("2025-06-10 -> 2025-06-18 (6 sessions of the wealth frame): fund returns "
    + ", ".join(f"{s} {f(100 * (float(g) - 1), 2, 3, plus=True)}%" for s, g in zip(F, G_span, strict=True))
    + f"; 1/N bought at the 06-10 close {f(100 * eq_span, 2, 3)}%; exp(mean log) - 1 {f(100 * log_avg, 2)}% "
    f"(mean log {f(log_sum, 4, 5)}; exp(0.02524) - 1 = {f(100 * (np.exp(0.02524) - 1), 2, 3)}%); R1 (wealth path) "
    f"{f(100 * r1_span, 2, 1)}%")                                                                          # 05
gw, ge = np.prod(1 + fr.W, axis=0), np.prod(1 + fr.X, axis=0)
put("growth factor, wealth frame vs estimation frame: "
    + "; ".join(f"{s} {f(float(a), 3, 4)} vs {f(float(b), 3, 4)}" for s, a, b in zip(F, gw, ge, strict=True))
    + f"; 0050 total return {f(100 * (gw[0] - 1), 1)}% (lm07.md:36 prints +767.3%)")                      # 06
# LM7's pair: returns between consecutive common closes of 0050 and 00679B (both from the previous common date)
pair = [J["0050"], J["00679B"]]
common = fr.traded[:, pair].all(axis=1)
G = np.ones(2)
pr: list[Vec] = []
for i in range(len(fr.wealth_dates)):
    G = G * (1 + fr.W[i, pair])
    if common[i]:
        pr.append(G - 1)
        G = np.ones(2)
P = np.array(pr)
A7 = len(P) / fr.years
rho7 = float(corr_mat(P)[0, 1])
vol7 = np.sqrt(np.diag(cov0(P)) * A7)
rho5 = float(corr_mat(fr.X[:, pair])[0, 1])
put(f"LM7's pair: {len(P)} returns between common closes, A {f(A7, 4)} (lm07.md:45: 2,363; lm08.md:284: A = "
    f"243.0543); corr {f(rho7, 4, 2)} (lm08.md:284: -0.1056; lm07.md:50: -0.11); vols {fl(100 * vol7, 2, 1)}% "
    f"(lm08.md:284: 20.11%, 13.50%); E5 estimation frame corr {f(rho5, 4, 3)} on {T} returns, without "
    f"2025-06-18")                                                                                         # 07

# ---------------------------------------------------------------- full-sample moments (estimation frame)
X = fr.X
S = cov0(X)
SA = A * S
vol = np.sqrt(np.diag(SA))
mu = A * X.mean(axis=0)
put(f"annualized volatilities (divisor T, A {f(A, 2)}) {fl(100 * vol, 2, 1)}%; annualized means A x mean "
    f"{fl(100 * mu, 2)}%")                                                                                 # 08
Cd = corr_mat(X)
put("daily correlations " + "; ".join(f"{F[a]}-{F[b]} {f(Cd[a, b], 2, 3, 4)}" for a in range(N)
                                      for b in range(a + 1, N)))                                         # 09
kw, Xw = periods(fr.est_dates, X, "week")
km, Xm = periods(fr.est_dates, X, "month")
kw_all, Xw_all = periods(fr.est_dates, X, "week", drop=False)
last_wk = [d for d in fr.est_dates if wkey(d) == kw_all[-1]]
Ck = corr_mat(Xw_all[1:])
put(f"weekly: {len(kw)} ISO weeks {kw[0]} .. {kw[-1]}; monthly: {len(km)} calendar months {km[0]} .. {km[-1]} (the "
    f"first and last period, in which the sample starts and ends, dropped); keeping the last week ({kw_all[-1]}: "
    f"{last_wk[0]} .. {last_wk[-1]}, {len(last_wk)} sessions) would give {len(kw) + 1} weeks and weekly correlations "
    f"0050-00646 {f(Ck[0, J['00646']], 3)}, 0050-00679B {f(Ck[0, J['00679B']], 3)}")                  # 10
frq = {"daily": X, "weekly": Xw, "monthly": Xm}
rows = []
pairs = [(0, j) for j in range(1, N)] + [(J["00679B"], J["00642U"])]
se: dict[tuple[int, int, str], tuple[float, float, float]] = {}
for a, b in pairs:
    for nm, x in frq.items():
        se[a, b, nm] = se_rho(x[:, a], x[:, b])
for a, b in pairs[:4]:
    cells = [f"{nm} {f(se[a, b, nm][0], 3, 2)} (SE {f(se[a, b, nm][1], 3)} normal, {f(se[a, b, nm][2], 3)} plug-in)"
             for nm in frq]
    rows.append(f"{F[a]}-{F[b]}: " + ", ".join(cells))
a9, b9 = pairs[4]
c79 = [f(se[a9, b9, nm][0], 3, 2) for nm in frq]
s79 = [f"{f(se[a9, b9, nm][1], 3)}, {f(se[a9, b9, nm][2], 3)}" for nm in frq]
ratio = {(a, b): se[a, b, "daily"][2] / se[a, b, "daily"][1] for a, b in pairs}
lo_p, hi_p = min(ratio, key=ratio.__getitem__), max(ratio, key=ratio.__getitem__)
gap = {(a, b): abs(se[a, b, "daily"][0] - se[a, b, "weekly"][0]) for a, b in pairs}
g_n = {k: gap[k] / se[k[0], k[1], "weekly"][1] for k in pairs}
g_p = {k: gap[k] / se[k[0], k[1], "weekly"][2] for k in pairs}
kg = max(g_n, key=g_n.__getitem__)
assert kg == max(g_p, key=g_p.__getitem__) and g_n[kg] < 2 and g_p[kg] < 2
# daily-monthly gaps, in monthly standard errors of each kind (the round-2 recomputation's Major 1)
gap_m = {k: abs(se[k[0], k[1], "daily"][0] - se[k[0], k[1], "monthly"][0]) for k in pairs}
gap_wm = {k: abs(se[k[0], k[1], "weekly"][0] - se[k[0], k[1], "monthly"][0]) for k in pairs}
m_n = {k: gap_m[k] / se[k[0], k[1], "monthly"][1] for k in pairs}
m_p = {k: gap_m[k] / se[k[0], k[1], "monthly"][2] for k in pairs}
two = [k for k in pairs if m_n[k] >= 2]
km2 = max(m_n, key=m_n.__getitem__)
assert two == [km2] and km2 == max(m_p, key=m_p.__getitem__) and km2 == (a9, b9)
kp = max(pairs, key=lambda k: se[k[0], k[1], "monthly"][2])
dm_list = "; ".join(f"{F[a]}-{F[b]} {m_n[a, b]:.4f}, {m_p[a, b]:.4f}" for a, b in pairs)
# the printed two-decimal correlations of 00679B-00642U do not give the four-decimal gap: the brief says that the gap
# is computed from the unrounded correlations (plans/vol-5.md, "Decisions on the third revision")
gap_2dp = abs(round(se[a9, b9, "daily"][0], 2) - round(se[a9, b9, "monthly"][0], 2))
# the same two statements over all ten pairs, which the brief does not print: it scopes both to the five pairs above
pairs10 = [(a, b) for a in range(N) for b in range(a + 1, N)]
for a, b in pairs10:
    for nm, x in frq.items():
        se.setdefault((a, b, nm), se_rho(x[:, a], x[:, b]))
dw10 = {k: abs(se[k[0], k[1], "daily"][0] - se[k[0], k[1], "weekly"][0]) / se[k[0], k[1], "weekly"][1]
        for k in pairs10}
kw10 = max(dw10, key=dw10.__getitem__)
dm10 = {k: abs(se[k[0], k[1], "daily"][0] - se[k[0], k[1], "monthly"][0]) for k in pairs10}
two10 = [k for k in pairs10 if dm10[k] / se[k[0], k[1], "monthly"][1] >= 2]
assert kw10 not in pairs and set(two10) - set(pairs)          # both statements need the five-pair scope
ten = (f"over all ten pairs (not printed; the brief scopes both statements to the five pairs): largest daily-weekly "
       f"gap {F[kw10[0]]}-{F[kw10[1]]} {abs(se[kw10[0], kw10[1], 'daily'][0] - se[kw10[0], kw10[1], 'weekly'][0]):.6f}"
       f" = {dw10[kw10]:.4f} weekly normal-theory SEs; daily-monthly gaps at 2 or more monthly normal-theory SEs: "
       + "; ".join(f"{F[a]}-{F[b]} {dm10[a, b]:.6f} = {dm10[a, b] / se[a, b, 'monthly'][1]:.4f} normal-theory, "
                   f"{dm10[a, b] / se[a, b, 'monthly'][2]:.4f} plug-in SEs" for a, b in two10)
       + "; largest monthly plug-in SE {:.6f} ({}-{})".format(
           *max((se[a, b, "monthly"][2], F[a], F[b]) for a, b in pairs10)))
put("; ".join(rows) + f"; 00679B-00642U daily, weekly, monthly {', '.join(c79)} (SE normal, plug-in: "
    f"{'; '.join(s79)}); daily plug-in over normal-theory SE, five pairs: {f(ratio[lo_p], 1, 2)} "
    f"({F[lo_p[0]]}-{F[lo_p[1]]}) to {f(ratio[hi_p], 1, 2)} ({F[hi_p[0]]}-{F[hi_p[1]]}); of the five pairs, largest "
    f"daily-weekly gap {F[kg[0]]}-{F[kg[1]]} {f(gap[kg], 3)} = {f(g_n[kg], 1)} weekly normal-theory SEs, "
    f"{f(g_p[kg], 1)} plug-in SEs (of the five pairs, no daily-weekly gap reaches 2 weekly SEs of either kind); "
    f"daily-monthly gaps in monthly normal-theory and plug-in SEs: {dm_list}; of the five pairs, at 2 or more "
    f"normal-theory SEs only {F[a9]}-{F[b9]}: gap {f(gap_m[a9, b9], 4)} from the unrounded correlations (the "
    f"two-decimal ones give {gap_2dp:.2f}) = {f(m_n[a9, b9], 1)} normal-theory SEs ({f(se[a9, b9, 'monthly'][1], 4)}),"
    f" {f(m_p[a9, b9], 1)} plug-in SEs ({f(se[a9, b9, 'monthly'][2], 4)}); its weekly-monthly gap "
    f"{gap_wm[a9, b9]:.6f} = {gap_wm[a9, b9] / se[a9, b9, 'monthly'][1]:.4f} and "
    f"{gap_wm[a9, b9] / se[a9, b9, 'monthly'][2]:.4f}; largest monthly plug-in SE "
    f"{f(se[kp[0], kp[1], 'monthly'][2], 2)} ({F[kp[0]]}-{F[kp[1]]}); " + ten)                           # 11
w1 = np.full(N, 1 / N)
# periods a year as LM19 counts them (lm19.md:39: periods with data over the years they span); the years run from the
# close before the first weekly return (the last session of the dropped first week) to the last kept week's last close
# (decision C7), which here equals the span of the calendar weeks, Monday of kw[0] to Sunday of kw[-1]; weeks without
# a session (Lunar New Year) are not periods
wk_first = date.fromisocalendar(int(kw[0][:4]), int(kw[0][6:]), 1)
wk_last = date.fromisocalendar(int(kw[-1][:4]), int(kw[-1][6:]), 7)
n_cal_weeks = ((wk_last - wk_first).days + 1) // 7
c_before = max(d for d in fr.est_dates if wkey(d) == kw_all[0])
c_last = max(d for d in fr.est_dates if wkey(d) == kw[-1])
days_wk = (date.fromisoformat(c_last) - date.fromisoformat(c_before)).days
assert days_wk == (wk_last - wk_first).days + 1
years_wk = days_wk / 365.25
A_week = len(kw) / years_wk
assert len(km) == 116 and km[0] == "2017-02" and km[-1] == "2026-09"     # 116 months over 116 / 12 years: A = 12
Afreq = {"daily": A, "weekly": A_week, "monthly": 12.0}
cells = []
for nm, x in frq.items():
    sp, _, _, _, sh = split(cov0(x), w1)
    cells.append(f"{nm} vol {f(100 * sp * sqrt(Afreq[nm]), 2)}%, 00642U share {f(100 * sh[J['00642U']], 1)}%, "
                 f"0050 share {f(100 * sh[0], 1)}%")
    if nm == "weekly":
        cells[-1] += f" (vol {f(100 * sp * sqrt(365.25 / 7), 2)}% with A = 365.25 / 7)"
put(f"R1's weights by frequency (A = {f(A, 2)}, {f(A_week, 2)}, 12; weekly A = {len(kw)} weeks with a session over "
    f"{f(years_wk, 4)} years from the close of {c_before}, before the first weekly return, to that of {c_last} "
    f"({days_wk} days, the span of the {n_cal_weeks} calendar weeks {wk_first} .. {wk_last}) = {len(kw)} x 365.25 / "
    f"{days_wk}): " + "; ".join(cells))                                                                    # 12

# ---------------------------------------------------------------- R1 and R2 on the full-sample covariance
sp1, b1, m1, rc1, sh1 = split(SA, w1)
sw = float(w1 @ vol)
var_terms = float((w1**2 * np.diag(SA)).sum()) / sp1**2
put(f"R1 weights 1/5: s_p {f(100 * sp1, 1, 2, 3)}%; w's {f(100 * sw, 2)}%; ratio w's / s_p {f(sw / sp1, 3, 2)}; "
    f"variance terms {f(100 * var_terms, 1)}% of the variance, covariance terms {f(100 * (1 - var_terms), 1)}%")  # 13
covp = SA @ w1
put(f"R1 Cov(R_i, R_p) x A {fl(1e4 * covp, 2)} (%^2); beta_(i,p) {fl(b1, 3)}; sum w_i beta_(i,p) "
    f"{float(w1 @ b1):.15f}")                                                                              # 14
put(f"R1 MRC {fl(100 * m1, 2)}% ; RC {fl(100 * rc1, 2)}% (sum {f(100 * rc1.sum(), 2)}%); shares {fl(100 * sh1, 1)}%"
    f" (sum {f(100 * sh1.sum(), 1)}%)")                                                                   # 15
stand = w1 * vol / sw
vterm = w1**2 * np.diag(SA) / sp1**2
put(f"R1 other splits: stand-alone w_i s_i / w's {fl(100 * stand, 1)}%; variance terms w_i^2 s_i^2 / s_p^2 "
    f"{fl(100 * vterm, 1, 3)}% (sum {f(100 * vterm.sum(), 1, 3)}%; the three-decimal parts sum to "
    f"{sum(round(100 * float(v), 3) for v in vterm):.3f})")                                                # 16
w2 = np.array([R2[s] for s in F])
sp2, b2, m2, rc2, sh2 = split(SA, w2)
put(f"R2 weights {fl(100 * w2, 0)}%: s_p {f(100 * sp2, 2)}%; w's {f(100 * float(w2 @ vol), 2)}%; ratio "
    f"{f(float(w2 @ vol) / sp2, 3, 2)}; beta_(i,p) {fl(b2, 3)}; RC {fl(100 * rc2, 2)}%; shares {fl(100 * sh2, 1)}%")  # 17
rp = X @ w1
slopes = np.array([float(np.cov(w1[i] * X[:, i], rp, ddof=0)[0, 1] / rp.var(ddof=0)) for i in range(N)])
put(f"OLS slope of w_i R_i on R_p (R1, full sample) minus w_i beta_(i,p): max |diff| "
    f"{np.abs(slopes - sh1).max():.1e}; sum of slopes {slopes.sum():.15f}")                                # 18
dlt = np.zeros(N)
dlt[J["00679B"]], dlt[J["00642U"]] = 0.05, -0.05
lin = float(dlt @ m1)
v_new = float((w1 + dlt) @ SA @ (w1 + dlt))
v_10_9 = sp1**2 + 2 * float(dlt @ SA @ w1) + float(dlt @ SA @ dlt)
assert abs(v_new - v_10_9) < 1e-15
put(f"R1, 5 points from 00642U to 00679B: linear change (MRC difference x 0.05) {f(100 * lin, 2, 3)} points; exact "
    f"by (10.9) {f(100 * (sqrt(v_new) - sp1), 2, 3)} points; s_p {f(100 * sp1, 2)}% -> {f(100 * sqrt(v_new), 2)}%; "
    f"variance {f(1e4 * sp1**2, 2)} -> {f(1e4 * v_new, 2)} (%^2), linear term {f(1e4 * 2 * float(dlt @ SA @ w1), 2)}, "
    f"quadratic {f(1e4 * float(dlt @ SA @ dlt), 2)}")                                                     # 19

# ---------------------------------------------------------------- R1's shares in the 92 windows
sch = schedule(fr)
shw = []
for _, _, n_rows in sch:
    x = X[n_rows - WINDOW:n_rows]
    shw.append(split(cov0(x), w1)[4])
SH = np.array(shw)
kneg = [k for k in range(len(sch)) if SH[k, J["00679B"]] < 0]
neg = [sch[k][0] for k in kneg]
kneg_last = kneg[-1]
span_n = kneg[-1] - kneg[0] + 1
neg_1bp = [sch[k][0] for k in kneg if SH[k, J["00679B"]] < -1e-4]
k6 = J["00642U"]
put(f"{len(sch)} windows of {WINDOW} rows (signals {sch[0][0]} .. {sch[-1][0]}); R1's 00642U share "
    f"{f(100 * SH[:, k6].min(), 1)}% ({sch[int(SH[:, k6].argmin())][0]}) to {f(100 * SH[:, k6].max(), 1)}% "
    f"({sch[int(SH[:, k6].argmax())][0]}); 0050 {f(100 * SH[:, 0].min(), 1)}% to {f(100 * SH[:, 0].max(), 1)}%; "
    f"00679B negative in {len(neg)} windows ({neg[0]} .. {neg[-1]}), lowest {f(100 * SH[:, J['00679B']].min(), 2)}% "
    f"({sch[int(SH[:, J['00679B']].argmin())][0]}), highest {f(100 * SH[:, J['00679B']].max(), 1)}%; "
    f"{span_n} windows from {neg[0]} to {neg[-1]}, the last negative share {f(100 * SH[kneg_last, J['00679B']], 4)}%; "
    f"below -0.01% in {len(neg_1bp)} windows, the last {neg_1bp[-1]}")                                    # 20
first_rows = sch[0][2]
put(f"first window {fr.est_dates[first_rows - WINDOW]} .. {fr.est_dates[first_rows - 1]}: R1 shares "
    f"{fl(100 * SH[0], 1)}%")                                                                              # 21
kmin = int(SH[:, J["00679B"]].argmin())
xn = X[sch[kmin][2] - WINDOW:sch[kmin][2]]
Sn = A * cov0(xn)
spn, bn, mn, _, shn = split(Sn, w1)
rho_b = float((Sn @ w1)[J["00679B"]] / sqrt(Sn[J["00679B"], J["00679B"]]) / spn)
vn2 = sqrt(float((w1 + dlt) @ Sn @ (w1 + dlt)))
put(f"window through {sch[kmin][0]} ({fr.est_dates[sch[kmin][2] - WINDOW]} .. {fr.est_dates[sch[kmin][2] - 1]}): "
    f"R1 s_p {f(100 * spn, 2)}%; 00679B corr with the book {f(rho_b, 3)}, beta_(i,p) {f(bn[J['00679B']], 3, 4)}, MRC "
    f"{f(100 * mn[J['00679B']], 2)}%, share {f(100 * shn[J['00679B']], 2)}%; 00642U share "
    f"{f(100 * shn[k6], 1)}%; 5 points from 00642U to 00679B: s_p -> {f(100 * vn2, 2)}%")               # 22

# ---------------------------------------------------------------- the wealth recursion: R1's trades
tax = np.array([TAX[s] for s in F])
t0 = p1.trades[0]
W_first = 1 / (1 + COMMISSION)
assert abs(p1.wealth[0] - W_first) < 1e-15 and abs(p2.wealth[0] - W_first) < 1e-15
put(f"first purchase {t0.trade} (signal {t0.signal}): from cash 1, TO {f(t0.turnover, 2)}, W_post = 1 / (1 + 0.001425) "
    f"{f(W_first, 6)}, cost {f(100 * t0.cost, 4, 2)}% of W; the same for R2")                             # 23
reb = p1.trades[1:]
to = np.array([t.turnover for t in reb])
kbig = int(to.argmax())
tb = reb[kbig]
prev = p1.trades[kbig]
ia, ib = p1.dates.index(prev.trade), p1.dates.index(tb.trade)
h = p1.wealth[ia] * prev.target
cash = p1.wealth[ia] * (1 - float(prev.target.sum()))
wd0 = fr.wealth_dates.index(prev.trade)
for i in range(wd0 + 1, wd0 + 1 + ib - ia):
    h = h * (1 + fr.W[i])
assert abs(cash) < 1e-15
W_pre = float(h.sum())
drift = h / W_pre
W_post = post_trade(W_pre, drift, tb.target, tax)
assert abs(W_post - p1.wealth[ib]) < 1e-12 and abs(0.5 * float(np.abs(tb.target - drift).sum()) - tb.turnover) < 1e-15
approx = 2 * COMMISSION * tb.turnover + float(tax @ np.clip(drift - tb.target, 0, None))
put(f"R1's trade on {tb.trade} (signal {tb.signal}; the largest one-way turnover of {len(reb)} rebalances): "
    f"W_pre {f(W_pre, 6)}, drift weights {fl(100 * drift, 2, 3)}%, TO {f(100 * tb.turnover, 2, 3)}%, W_post "
    f"{f(W_post, 6)}, "
    f"cost {f(100 * tb.cost, 4, 5)}% of W_pre ({f(1e6 * tb.cost, 0)} NT$ per NT$1 million); approximation "
    f"2 x 0.1425% x TO + tax on sales {f(100 * approx, 4, 5)}%")                                          # 24
put(f"cost per unit of turnover, a rebalance of weights summing to 1 (approximation): 2 x 0.1425% = "
    f"{f(200 * COMMISSION, 3)}% with no taxed sale, up to {f(200 * COMMISSION + 0.1, 3)}% when every sale is taxed")  # 25
ifirst = fr.wealth_dates.index(t0.trade)
g = np.cumprod(1 + fr.W[ifirst + 1:], axis=0)
wbh = g / g.sum(axis=1, keepdims=True)
dbh = fr.wealth_dates[ifirst + 1:]
ext = "; ".join(f"{s} {f(100 * wbh[:, j].min(), 1)}% ({dbh[int(wbh[:, j].argmin())]}) to "
                f"{f(100 * wbh[:, j].max(), 1)}% ({dbh[int(wbh[:, j].argmax())]})" for j, s in enumerate(F))
g0 = np.prod(1 + fr.W, axis=0)
# X2's thinned points (X37): the last session of each ISO week from the purchase date, the purchase date itself and
# every fund's lowest and highest weight (dbh starts the session after the purchase, so its index i is point i + 1)
d_all = fr.wealth_dates[ifirst:]
wk_of = [wkey(d) for d in d_all]
pts = {i for i in range(len(d_all)) if i == len(d_all) - 1 or wk_of[i + 1] != wk_of[i]} | {0}
n_week = len(pts) - 1
for j in range(N):
    pts |= {int(wbh[:, j].argmin()) + 1, int(wbh[:, j].argmax()) + 1}
put(f"buy-and-hold from 1/N at the close of {t0.trade}: weights on {dbh[-1]} {fl(100 * wbh[-1], 1, 3)}% (the "
    f"three-decimal weights sum to {sum(round(100 * float(x), 3) for x in wbh[-1]):.3f}); range {ext}; "
    f"{len(dbh) + 1} dates with the purchase date; thinned for X2 to {len(pts)} points ({n_week} last sessions of ISO "
    f"weeks, the purchase date and the extremes); from 1/N at the base close {fr.base}: {fl(100 * g0 / g0.sum(), 1)}%")  # 26

# ---------------------------------------------------------------- U28: drift echo and the factor split
s = u28()
U, mkt, names = s.X, s.taiex, s.names
k_s, k_f = names.index("Semiconductor"), names.index("FinancialInsurance")
gs, gf = np.cumprod(1 + U[:, k_s]), np.cumprod(1 + U[:, k_f])
wsf = gs / (gs + gf)
put(f"U28 T {len(mkt)} ({s.dates[0]} .. {s.dates[-1]}), A {f(s.A, 4)}; Semiconductor's weight in a 50/50 "
    f"buy-and-hold mix with FinancialInsurance: {f(wsf[-1], 3)} on {s.dates[-1]}, low {f(wsf.min(), 3)} "
    f"({s.dates[int(wsf.argmin())]}), high {f(wsf.max(), 3)} ({s.dates[int(wsf.argmax())]}) (lm09.md:437)")  # 27
Tm = len(mkt)
mc = mkt - mkt.mean()
vm = float(mc @ mc) / Tm
beta = (U - U.mean(axis=0)).T @ mc / Tm / vm
alpha = U.mean(axis=0) - beta * mkt.mean()
E = U - alpha - np.outer(mkt, beta)
assert float(np.abs(E.T @ mc).max()) / Tm < 1e-18
wu = np.full(28, 1 / 28)
Su, Sres = cov0(U), cov0(E)
vp = float(wu @ Su @ wu)
bp = float(wu @ beta)
v_sys, v_res = bp**2 * vm, float(wu @ Sres @ wu)
v_diag = float((wu**2 * np.diag(Sres)).sum())
assert abs(v_sys + v_res - vp) < 1e-15
rp_u = U @ wu
r2_book = float(np.corrcoef(rp_u, mkt)[0, 1] ** 2)
Au = s.A
put(f"U28 equal-weight book: s_p {f(100 * sqrt(Au * vp), 2)}% (lm10.md:36: 15.75%); TAIEX {f(100 * sqrt(Au * vm), 2)}% "
    f"(lm10.md:41: 17.82%); market betas {f(beta.min(), 3)} ({names[int(beta.argmin())]}) to {f(beta.max(), 3)} "
    f"({names[int(beta.argmax())]}); book beta w'beta {f(bp, 4, 3)}; systematic {f(100 * v_sys / vp, 1, 3)}% of the "
    f"variance (R-squared of the book on TAIEX {f(100 * r2_book, 1, 3)}%), residual {f(100 * v_res / vp, 1, 3)}%: "
    f"diagonal {f(100 * v_diag / vp, 1, 3)}%, off-diagonal {f(100 * (v_res - v_diag) / vp, 1, 3)}%")       # 28
put(f"U28 book volatilities: systematic part {f(100 * sqrt(Au * v_sys), 1, 2)}%, residual part "
    f"{f(100 * sqrt(Au * v_res), 1, 2)}%; with the residual covariances set to 0 "
    f"{f(100 * sqrt(Au * (v_sys + v_diag)), 2)}% against {f(100 * sqrt(Au * vp), 2)}%")                   # 29
spu = sqrt(vp)
rc_u = wu * (Su @ wu) / spu
rc_sys = wu * beta * bp * vm / spu
rc_res = wu * (Sres @ wu) / spu
assert float(np.abs(rc_sys + rc_res - rc_u).max()) < 1e-17
ku_hi, ku_lo = int(rc_u.argmax()), int(rc_u.argmin())
put(f"U28 shares (RC / s_p): Semiconductor {f(100 * rc_u[k_s] / spu, 2)}% = systematic "
    f"{f(100 * rc_sys[k_s] / spu, 2)}% + residual {f(100 * rc_res[k_s] / spu, 2)}%; largest {names[ku_hi]} "
    f"{f(100 * rc_u[ku_hi] / spu, 2)}%, smallest {names[ku_lo]} {f(100 * rc_u[ku_lo] / spu, 2)}% "
    f"(1/28 = {f(100 / 28, 2)}%); negative residual parts: {int((rc_res < 0).sum())} of 28")              # 30
volu = np.sqrt(np.diag(Su) * Au)
vt_u = float((wu**2 * np.diag(Su)).sum())
put(f"U28 mean of the 28 volatilities {f(100 * volu.mean(), 2)}% (lm10.md:41: 21.94%); ratio w's / s_p "
    f"{f(volu.mean() / sqrt(Au * vp), 3)}; E5's R1 {f(sw / sp1, 3)}; U28 variance terms {f(100 * vt_u / vp, 1)}% of "
    f"the variance, covariance terms {f(100 * (1 - vt_u / vp), 1)}%, variance terms alone a volatility of "
    f"{f(100 * sqrt(Au * vt_u), 2)}% (lm10.md:220: 92.8%, 7.2%, 4.22%)")                                   # 31
lam = np.linalg.eigvalsh(SA)
put(f"(11.4) for R1 on E5 (annualized S): eigenvalues {fl(1e4 * lam[::-1], 2)} (%^2); |w|^2 = 1/5, so "
    f"{f(1e4 * lam[0] / N, 2)} <= s_p^2 = {f(1e4 * sp1**2, 2)} <= {f(1e4 * lam[-1] / N, 2)} (%^2)")       # 32
put("widget matrix A S (daily, full sample, decimals): "
    + "; ".join(" ".join(f"{SA[a, b]:.10f}" for b in range(N)) for a in range(N))
    + f"; initial state R1: s_p {f(100 * sp1, 2)}%, shares {fl(100 * sh1, 1)}%")                          # 33
Tu = T
put(f"np.cov's default divisor T - 1: volatility ratio sqrt(T/(T-1)) = {f(sqrt(Tu / (Tu - 1)), 6)} at T = {Tu}; "
    f"R1's s_p {f(100 * sp1, 3, 4)}% -> {f(100 * sp1 * sqrt(Tu / (Tu - 1)), 3, 4)}%")                      # 34

# ---------------------------------------------------------------- problems (hypothetical inputs unless stated)
put(f"P1: 50/50, returns +10% and -5%: R_p {f(2.5, 2)}%; drifted weight 0.55 / 1.025 = {f(0.55 / 1.025, 3, 4)}")  # 35
pre = np.array([0.30, 0.20, 0.15, 0.15, 0.20])
tgt = np.full(5, 0.2)
Wq = 1.0
for _ in range(100):
    d = Wq * tgt - pre
    new = 1 - (COMMISSION * float(np.abs(d).sum()) + float(tax @ np.clip(-d, 0, None)))
    if abs(new - Wq) < 1e-16:
        break
    Wq = new
to_q = 0.5 * float(np.abs(tgt - pre).sum())
tax_q = float(tax @ np.clip(pre - tgt, 0, None))
ap_q = 2 * COMMISSION * to_q + tax_q
put(f"P2: E5's taxes, pre-trade weights {fl(pre, 2)}, target 1/N: TO {f(to_q, 2)}; approximation "
    f"{f(100 * ap_q, 4)}% of W; exact {f(100 * (1 - Wq), 4)}%; distractors {f(100 * 2 * COMMISSION * to_q, 4)}% "
    f"(no tax), {f(100 * (4 * COMMISSION * to_q + tax_q), 4)}% (commission on twice the trades)")           # 36
g_hi, g_lo = 1.40, 0.80
put(f"P3: 50/50 bought and held, growth factors {g_hi} and {g_lo}: R_p {f(100 * (0.5 * g_hi + 0.5 * g_lo - 1), 2)}%; "
    f"exp(mean log) - 1 {f(100 * (sqrt(g_hi * g_lo) - 1), 2)}%; mean log {f(100 * 0.5 * np.log(g_hi * g_lo), 2)}%")  # 37
sd3 = np.array([0.20, 0.10, 0.30])
C3 = np.array([[1.0, 0.2, 0.6], [0.2, 1.0, -0.2], [0.6, -0.2, 1.0]])
S3 = C3 * np.outer(sd3, sd3)
w3 = np.array([0.4, 0.4, 0.2])
sp3, b3, m3, rc3, sh3 = split(S3, w3)
put(f"P4: sigma (20%, 10%, 30%), rho12 0.2, rho13 0.6, rho23 -0.2, w (0.4, 0.4, 0.2): sigma_p {f(100 * sp3, 2)}%; "
    f"MRC {fl(100 * m3, 2)}%; RC {fl(100 * rc3, 2)}%; shares {fl(100 * sh3, 1)}%; stand-alone shares "
    f"{fl(100 * w3 * sd3 / float(w3 @ sd3), 1)}%; variance-term shares {fl(100 * w3**2 * sd3**2 / sp3**2, 1)}%")                                                         # 38
d3 = np.array([0.0, 0.05, -0.05])
lin3 = float(d3 @ m3)
ex3 = sqrt(float((w3 + d3) @ S3 @ (w3 + d3))) - sp3
put(f"P10: same inputs, 5 points from asset 3 to asset 2: linear {f(100 * lin3, 2, 3)} points, exact "
    f"{f(100 * ex3, 2, 3)} points; sigma_p -> {f(100 * (sp3 + ex3), 2)}%")                                 # 39
r_m, se_m, _ = se_rho(Xm[:, 0], Xm[:, J["00646"]])
r_st = round(r_m, 4)                          # the stem gives the correlation to four decimals
put(f"P6: 0050-00646 monthly rho {f(r_m, 3, 4)} on T = {len(km)}; the stem's rho {r_st:.4f}: normal-theory SE "
    f"(1 - rho^2) / sqrt(T) {f((1 - r_st**2) / sqrt(len(km)), 4)} (from the unrounded rho {f(se_m, 4)}); distractors "
    f"1 / sqrt(T) {f(1 / sqrt(len(km)), 4)}, (1 - rho^2) / T {f((1 - r_st**2) / len(km), 4)}")             # 40

# ---------------------------------------------------------------- details added for the exhibits and checks
x_tr = (W_post * tb.target - W_pre * drift) / W_pre
com_i = COMMISSION * np.abs(x_tr)
tax_i = tax * np.clip(-x_tr, 0, None)
put(f"detail of A27-24, per fund ({', '.join(F)}), % of W_pre: target {fl(100 * tb.target, 2)}; trade "
    f"{fl(100 * x_tr, 4)}; commission {fl(100 * com_i, 5)}; tax {fl(100 * tax_i, 5)}; totals commission "
    f"{f(100 * com_i.sum(), 5)}, tax {f(100 * tax_i.sum(), 5)}, cost {f(100 * (com_i.sum() + tax_i.sum()), 4)}")  # 41
w_span = 0.2 * G_span / float((0.2 * G_span).sum())
put(f"1/N at the close of 2025-06-10, weights at the close of 2025-06-18 without a trade: {fl(100 * w_span, 2)}%")  # 42
put(f"switching NT$1,000,000 (approximation, no cost on the cost): 00679B -> 0050 "
    f"{f(2 * COMMISSION * 1e6, 0)} NT$; 0050 -> 00679B {f(2 * COMMISSION * 1e6 + TAX['0050'] * 1e6, 0)} NT$")  # 43

B = 1e7                                       # a book of NT$10 million before the trade (scale-free recursion)
put(f"A27-24's trade on a book of NT$10,000,000 before the trade: holdings {fl(B * drift, 0)}; trades "
    f"{fl(B * x_tr, 0)}; commission by fund {fl(B * com_i, 0)}, tax by fund {fl(B * tax_i, 0)}; commission "
    f"{f(B * com_i.sum(), 0)}, tax {f(B * tax_i.sum(), 0)}, cost "
    f"{f(B * tb.cost, 0)} NT$; after the trade {f(B * W_post / W_pre, 0)} NT$, {f(B * W_post / W_pre / 5, 0)} in "
    f"each fund (whole NT$ in X3)")                                                                        # 44
sh2w = []
for _, _, n_rows in sch:
    sh2w.append(split(cov0(X[n_rows - WINDOW:n_rows]), w2)[4])
SH2 = np.array(sh2w)
over = [sch[k][0] for k in range(len(sch)) if SH2[k, 0] > 0.70]
put("R2's shares in the 92 windows: "
    + "; ".join(f"{s} {f(100 * SH2[:, j].min(), 1)}% ({sch[int(SH2[:, j].argmin())][0]}) to "
                f"{f(100 * SH2[:, j].max(), 1)}% ({sch[int(SH2[:, j].argmax())][0]})" for j, s in enumerate(F[:4]))
    + f"; 00642U 0 (weight 0); 0050 above 70% in {len(over)} windows ({over[0]} .. {over[-1]})")             # 45
# A27-46 checked a parenthesis of the shared decision "Timing of E5" (its first figures, log returns with partial end
# periods); the decisions on the third revision dropped that note, so the check has no object
put("withdrawn (it checked the shared decision's note on its first figures, which the decisions on the third "
    "revision dropped; the ID is kept so that later IDs do not move)")                                    # 46
put(f"mu_p = w'mu (A x mean, estimation frame): R1 {f(100 * float(w1 @ mu), 2)}%, R2 {f(100 * float(w2 @ mu), 2)}%")  # 47
SM = 12 * cov0(Xm)
spm, _, _, _, shm = split(SM, w1)
put(f"widget matrix 12 S (monthly, {len(km)} calendar months, decimals): "
    + "; ".join(" ".join(f"{SM[a, b]:.10f}" for b in range(N)) for a in range(N))
    + f"; R1: s_p {f(100 * spm, 2)}%, shares {fl(100 * shm, 1)}%")                                        # 48
put(f"widget matrix A S (daily, window {fr.est_dates[sch[kmin][2] - WINDOW]} .. {fr.est_dates[sch[kmin][2] - 1]}, "
    f"A = {f(A, 2)}, decimals): " + "; ".join(" ".join(f"{Sn[a, b]:.10f}" for b in range(N)) for a in range(N))
    + f"; R1: s_p {f(100 * spn, 2)}%, shares {fl(100 * shn, 1)}%")                                        # 49
# raw kurtosis (LM19's (19.3), divisor T) of each fund at each frequency: the plug-in SE of A27-11 needs finite
# fourth moments (the round-2 recomputation's Minor 6)
kurt = {nm: ((x - x.mean(axis=0)) ** 4).mean(axis=0) / x.var(axis=0, ddof=0) ** 2 for nm, x in frq.items()}
k_hi = {nm: F[int(np.argmax(kurt[nm]))] for nm in frq}
assert k_hi["daily"] == k_hi["monthly"] == "00642U"
ko = [j for j in range(N) if F[j] != "00642U"]
k_d, k_m = kurt["daily"], kurt["monthly"]
put("raw kurtosis (19.3), divisor T, estimation frame: "
    + "; ".join(f"{nm} " + ", ".join(f"{F[j]} {kurt[nm][j]:.4f}" for j in range(N)) for nm in frq)
    + f"; largest daily and monthly 00642U ({f(float(k_d[J['00642U']]), 1)}, {f(float(k_m[J['00642U']]), 1)}), "
    f"largest weekly {k_hi['weekly']}; the other four daily {f(float(k_d[ko].min()), 1)} to "
    f"{f(float(k_d[ko].max()), 1)}, monthly {f(float(k_m[ko].min()), 1)} to {f(float(k_m[ko].max()), 1)}")  # 50

print("\n".join(OUT))
