"""LM27 (Portfolio Return and Risk): the computations behind every number, shared by data/lm27_numbers.py and
data/lm27_charts.py. Imported, not run: it prints nothing and writes nothing.

The code is the computational part of data/vol5_anchors_lm27.py (the Stage 1 anchors, plans/vol-5-anchors.md, "LM27"),
with the same names, so that data/lm27_numbers.py rebuilds every anchor line exactly as that script prints it. Inputs,
read only through the shared builders (run them first):
  * E5 (plans/vol-5.md, "Data"): vol5_series.frames("E5") and ohlc(), from data/processed/vol5_frames.parquet and
    vol5_ohlc.parquet (built and checked by data/vol5_series.py from FinMind's TaiwanStockPrice,
    TaiwanStockDividendResult and TaiwanStockSplitPrice, retrieved 2026-10-24): 0050, 00646, 00679B, 00635U and
    00642U, daily total returns (P_t + D_t) / P_prev - 1, the previous close restated per current share on a split day
    (P_prev / 4 for 0050 on 2025-06-18). Estimation frame: T = 2,362 dates on which every fund has a one-session return;
    wealth frame: 2,368 TR23 sessions, a halted fund earning 0 and its spanning return booked when it trades again.
  * The through case: vol5_rules.schedule(), signals() and wealth_path() (R1 and R2, the cost model, the wealth
    recursion) and cov0() (divisor T). No rule is re-implemented; the trade of 2026-04-01 is replayed from the shared
    path only to show the parts of (27.2).
  * U28 (Volume II): data/lm10_series.py's u28() (data/processed/vol2_closes.parquet, repaired closes): 28 sector
    price indices and the TAIEX price index, T = 4,382, A = 245.4794.

Conventions: simple returns; every moment divides by T (ddof=0, passed explicitly; cov0); annualization with E5's
A = 2,362 x 365.25 / 3,551 = 242.951, U28's 245.4794, weeks as LM19 counts them (500 x 365.25 / 3,542) and months 12;
weekly and monthly returns compound the estimation frame inside ISO weeks (keys ISO year, ISO week) and calendar
months, the first and last period dropped, complete or not. A split of weights w under a covariance S:
Cov(R_i, R_p) = (S w)_i, beta_{i,p} = (S w)_i / w'S w, MRC_i = (S w)_i / sqrt(w'S w), RC_i = w_i MRC_i,
share_i = w_i beta_{i,p}. Costs: commission 0.1425% on each side, tax 0.1% on sales of every fund but 00679B.
"""
import sys
from datetime import date
from fractions import Fraction
from math import sqrt
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from lm10_series import u28
from vol5_rules import COMMISSION, R2, TAX, WINDOW, cov0, schedule, signals, wealth_path
from vol5_series import frames, ohlc

Vec = NDArray[np.float64]
Mat = NDArray[np.float64]


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
assert abs(A - T * 365.25 / days) < 1e-12 and abs(fr.A_wealth - len(fr.wealth_dates) * 365.25 / days) < 1e-12
est = set(fr.est_dates)
only_w = [d for d in fr.wealth_dates if d not in est]
halted = [(F[j], fr.wealth_dates[i]) for i, j in zip(*np.nonzero(~fr.traded), strict=True)]
c50 = {d: Fraction(str(c)) for d, c in ohlc("0050").select("date", "close").iter_rows()}
r_split = 4 * c50["2025-06-18"] / c50["2025-06-10"] - 1
iw = fr.wealth_dates.index("2025-06-18")
assert abs(float(r_split) - fr.W[iw, J["0050"]]) < 1e-15
assert all(fr.W[fr.wealth_dates.index(d), J["0050"]] == 0 for d in only_w[:-1])
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
gw, ge = np.prod(1 + fr.W, axis=0), np.prod(1 + fr.X, axis=0)
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

# ---------------------------------------------------------------- full-sample moments (estimation frame)
X = fr.X
S = cov0(X)
SA = A * S
vol = np.sqrt(np.diag(SA))
mu = A * X.mean(axis=0)
Cd = corr_mat(X)
kw, Xw = periods(fr.est_dates, X, "week")
km, Xm = periods(fr.est_dates, X, "month")
kw_all, Xw_all = periods(fr.est_dates, X, "week", drop=False)
last_wk = [d for d in fr.est_dates if wkey(d) == kw_all[-1]]
Ck = corr_mat(Xw_all[1:])
frq = {"daily": X, "weekly": Xw, "monthly": Xm}
pairs = [(0, j) for j in range(1, N)] + [(J["00679B"], J["00642U"])]
se: dict[tuple[int, int, str], tuple[float, float, float]] = {}
for a, b in pairs:
    for nm, x in frq.items():
        se[a, b, nm] = se_rho(x[:, a], x[:, b])
a9, b9 = pairs[4]
ratio = {(a, b): se[a, b, "daily"][2] / se[a, b, "daily"][1] for a, b in pairs}
lo_p, hi_p = min(ratio, key=ratio.__getitem__), max(ratio, key=ratio.__getitem__)
gap = {(a, b): abs(se[a, b, "daily"][0] - se[a, b, "weekly"][0]) for a, b in pairs}
g_n = {k: gap[k] / se[k[0], k[1], "weekly"][1] for k in pairs}
g_p = {k: gap[k] / se[k[0], k[1], "weekly"][2] for k in pairs}
kg = max(g_n, key=g_n.__getitem__)
assert kg == max(g_p, key=g_p.__getitem__) and g_n[kg] < 2 and g_p[kg] < 2
gap_m = {k: abs(se[k[0], k[1], "daily"][0] - se[k[0], k[1], "monthly"][0]) for k in pairs}
gap_wm = {k: abs(se[k[0], k[1], "weekly"][0] - se[k[0], k[1], "monthly"][0]) for k in pairs}
m_n = {k: gap_m[k] / se[k[0], k[1], "monthly"][1] for k in pairs}
m_p = {k: gap_m[k] / se[k[0], k[1], "monthly"][2] for k in pairs}
two = [k for k in pairs if m_n[k] >= 2]
km2 = max(m_n, key=m_n.__getitem__)
assert two == [km2] and km2 == max(m_p, key=m_p.__getitem__) and km2 == (a9, b9)
kp = max(pairs, key=lambda k: se[k[0], k[1], "monthly"][2])
dm_list = "; ".join(f"{F[a]}-{F[b]} {m_n[a, b]:.4f}, {m_p[a, b]:.4f}" for a, b in pairs)
# the printed two-decimal correlations of 00679B-00642U do not give the four-decimal gap: the text says that the gap is
# computed from the unrounded correlations (plans/vol-5.md, "Decisions on the third revision")
gap_2dp = abs(round(se[a9, b9, "daily"][0], 2) - round(se[a9, b9, "monthly"][0], 2))
# the same two statements over all ten pairs, which the module does not print: it scopes both to the five pairs above
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
w1 = np.full(N, 1 / N)
# periods a year as LM19 counts them (lm19.md:39: periods with data over the years they span); the years run from the
# close before the first weekly return to the last kept week's last close (decision C7)
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

# ---------------------------------------------------------------- R1 and R2 on the full-sample covariance
sp1, b1, m1, rc1, sh1 = split(SA, w1)
sw = float(w1 @ vol)
var_terms = float((w1**2 * np.diag(SA)).sum()) / sp1**2
covp = SA @ w1
stand = w1 * vol / sw
vterm = w1**2 * np.diag(SA) / sp1**2
# the same terms from the printed inputs (two-decimal volatilities, s_p^2 = 132.09 from 11.493%): they do not give
# E7's three-decimal digits, so the text says that those come from unrounded inputs
vol_pr = np.round(100 * vol, 2)
var_pr = round(round(100 * sp1, 3) ** 2, 2)
assert var_pr == 132.09
vterm_pr = 100 * w1**2 * vol_pr**2 / var_pr
w2 = np.array([R2[s] for s in F])
sp2, b2, m2, rc2, sh2 = split(SA, w2)
rp = X @ w1
slopes = np.array([float(np.cov(w1[i] * X[:, i], rp, ddof=0)[0, 1] / rp.var(ddof=0)) for i in range(N)])
dlt = np.zeros(N)
dlt[J["00679B"]], dlt[J["00642U"]] = 0.05, -0.05
lin = float(dlt @ m1)
v_new = float((w1 + dlt) @ SA @ (w1 + dlt))
v_10_9 = sp1**2 + 2 * float(dlt @ SA @ w1) + float(dlt @ SA @ dlt)
assert abs(v_new - v_10_9) < 1e-15

# ---------------------------------------------------------------- R1's shares in the 92 windows
sch = schedule(fr)
SH = np.array([split(cov0(X[n_rows - WINDOW:n_rows]), w1)[4] for _, _, n_rows in sch])
GUARD = 1e-12                                 # counting guard (plans/vol-5.md, "Counting"); margins printed
kneg = [k for k in range(len(sch)) if SH[k, J["00679B"]] < -GUARD]
k_m79 = int(np.abs(SH[:, J["00679B"]]).argmin())
m79 = float(abs(SH[k_m79, J["00679B"]]))
assert m79 > GUARD
neg = [sch[k][0] for k in kneg]
kneg_last = kneg[-1]
span_n = kneg[-1] - kneg[0] + 1
neg_1bp = [sch[k][0] for k in kneg if SH[k, J["00679B"]] < -1e-4]
k6 = J["00642U"]
first_rows = sch[0][2]
kmin = int(SH[:, J["00679B"]].argmin())
xn = X[sch[kmin][2] - WINDOW:sch[kmin][2]]
Sn = A * cov0(xn)
spn, bn, mn, _, shn = split(Sn, w1)
rho_b = float((Sn @ w1)[J["00679B"]] / sqrt(Sn[J["00679B"], J["00679B"]]) / spn)
vn2 = sqrt(float((w1 + dlt) @ Sn @ (w1 + dlt)))
assert all(mn[j] > 0 for j in range(N) if j != J["00679B"]) and mn[J["00679B"]] < 0

# ---------------------------------------------------------------- the wealth recursion: R1's trades
tax = np.array([TAX[s] for s in F])
t0 = p1.trades[0]
W_first = 1 / (1 + COMMISSION)
assert abs(p1.wealth[0] - W_first) < 1e-15 and abs(p2.wealth[0] - W_first) < 1e-15
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
ifirst = fr.wealth_dates.index(t0.trade)
g = np.cumprod(1 + fr.W[ifirst + 1:], axis=0)
wbh = g / g.sum(axis=1, keepdims=True)
dbh = fr.wealth_dates[ifirst + 1:]
g0 = np.prod(1 + fr.W, axis=0)
# X2's thinned points (X37): the last session of each ISO week from the purchase date, the purchase date itself and
# every fund's lowest and highest weight (dbh starts the session after the purchase, so its index i is point i + 1)
d_all = fr.wealth_dates[ifirst:]
wk_of = [wkey(d) for d in d_all]
pts = {i for i in range(len(d_all)) if i == len(d_all) - 1 or wk_of[i + 1] != wk_of[i]} | {0}
n_week = len(pts) - 1
for j in range(N):
    pts |= {int(wbh[:, j].argmin()) + 1, int(wbh[:, j].argmax()) + 1}

# ---------------------------------------------------------------- U28: drift echo and the factor split
s = u28()
U, mkt, names = s.X, s.taiex, s.names
k_s, k_f = names.index("Semiconductor"), names.index("FinancialInsurance")
gs, gf = np.cumprod(1 + U[:, k_s]), np.cumprod(1 + U[:, k_f])
wsf = gs / (gs + gf)
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
spu = sqrt(vp)
rc_u = wu * (Su @ wu) / spu
rc_sys = wu * beta * bp * vm / spu
rc_res = wu * (Sres @ wu) / spu
assert float(np.abs(rc_sys + rc_res - rc_u).max()) < 1e-17
ku_hi, ku_lo = int(rc_u.argmax()), int(rc_u.argmin())
volu = np.sqrt(np.diag(Su) * Au)
vt_u = float((wu**2 * np.diag(Su)).sum())
# residual correlations across the 378 pairs (echo of lm23.md:359: mean 0.112)
Cres = corr_mat(E)
res_pairs = Cres[np.triu_indices(28, 1)]
lam = np.linalg.eigvalsh(SA)
Tu = T

# ---------------------------------------------------------------- problems (hypothetical inputs unless stated)
pre = np.array([0.30, 0.20, 0.15, 0.15, 0.20])
tgt = np.full(5, 0.2)
Wq = 1.0
for _ in range(100):
    dq = Wq * tgt - pre
    new = 1 - (COMMISSION * float(np.abs(dq).sum()) + float(tax @ np.clip(-dq, 0, None)))
    if abs(new - Wq) < 1e-16:
        break
    Wq = new
to_q = 0.5 * float(np.abs(tgt - pre).sum())
tax_q = float(tax @ np.clip(pre - tgt, 0, None))
ap_q = 2 * COMMISSION * to_q + tax_q
g_hi, g_lo = 1.40, 0.80
sd3 = np.array([0.20, 0.10, 0.30])
C3 = np.array([[1.0, 0.2, 0.6], [0.2, 1.0, -0.2], [0.6, -0.2, 1.0]])
S3 = C3 * np.outer(sd3, sd3)
w3 = np.array([0.4, 0.4, 0.2])
sp3, b3, m3, rc3, sh3 = split(S3, w3)
d3 = np.array([0.0, 0.05, -0.05])
lin3 = float(d3 @ m3)
ex3 = sqrt(float((w3 + d3) @ S3 @ (w3 + d3))) - sp3
mu3 = np.array([0.08, 0.04, 0.10])           # Problem 10's hypothetical annual means
sw3 = float(w3 @ sd3)
assert round(100 * sw3, 2) == 18.0 and round(100 * sp3, 2) == 13.30      # the printed inputs of the ratio
r_m, se_m, _ = se_rho(Xm[:, 0], Xm[:, J["00646"]])
r_st = round(r_m, 4)                          # the stem gives the correlation to four decimals

# ---------------------------------------------------------------- details for the exhibits and checks
x_tr = (W_post * tb.target - W_pre * drift) / W_pre
com_i = COMMISSION * np.abs(x_tr)
tax_i = tax * np.clip(-x_tr, 0, None)
w_span = 0.2 * G_span / float((0.2 * G_span).sum())
B = 1e7                                       # a book of NT$10 million before the trade (scale-free recursion)
SH2 = np.array([split(cov0(X[n_rows - WINDOW:n_rows]), w2)[4] for _, _, n_rows in sch])
over = [sch[k][0] for k in range(len(sch)) if SH2[k, 0] > 0.70 + GUARD]
k_m70 = int(np.abs(SH2[:, 0] - 0.70).argmin())
m70 = float(abs(SH2[k_m70, 0] - 0.70))
assert m70 > GUARD
SM = 12 * cov0(Xm)
spm, _, _, _, shm = split(SM, w1)
# raw kurtosis (LM19's (19.3), divisor T) of each fund at each frequency: the plug-in SE needs finite fourth moments
kurt = {nm: ((x - x.mean(axis=0)) ** 4).mean(axis=0) / x.var(axis=0, ddof=0) ** 2 for nm, x in frq.items()}
k_hi = {nm: F[int(np.argmax(kurt[nm]))] for nm in frq}
assert k_hi["daily"] == k_hi["monthly"] == "00642U"
ko = [j for j in range(N) if F[j] != "00642U"]
k_d, k_m = kurt["daily"], kurt["monthly"]
