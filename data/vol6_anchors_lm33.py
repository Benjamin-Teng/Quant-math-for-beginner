"""LM33 anchors (The Statistics of the Sharpe Ratio): every number the Stage 1 brief quotes (drafted 2026-10-24).

Reads only data/processed/*.parquet, through the shared builders (run them first; this script runs neither):
  * E5, the through case (plans/vol-5.md): data/vol5_series.py's frames("E5") reads vol5_frames.parquet; the eight
    rules come from data/vol5_rules.py (signals, wealth_path, summary; no rule is re-implemented here). The rules'
    daily net returns are the wealth path's ratios W_t / W_{t-1} - 1 from the session after the first trade
    (2019-03-05) to 2026-10-08, T = 1,851 sessions of the wealth frame; their excess returns subtract RF / A_w per
    session (RF = 1.5% a year, A_w = the wealth frame's sessions a year). The wealth paths are checked equal to
    data/processed/vol5_rules.parquet. Monthly returns: the 90 full calendar months 2019-04 .. 2026-09 (the partial
    months March 2019 and October 2026 are left out), each the log change of net wealth between month-end sessions
    minus the month's accrued log interest (sessions x ln(1 + RF / A_w)).
  * TR23 (Volume III): data/processed/vol3_taiex.parquet (columns date, tr, price, R, Rp), the simple returns R,
    T = 5,849, A = T / years = 246.12, r_f = 0 (Volume IV's convention).

Conventions. Sharpe ratios are per observation in every formula and annualized by sqrt(A) only for printing (A_w for
E5's days, 12 for months, A for TR23). Means and moments divide by T (ddof=0): s, the sample skewness and the raw
kurtosis of (19.3) (normal = 3). Delta method: the iid standard error of a Sharpe ratio is (20.9) with the sample
moments, sqrt((1 - SR Skew + (Kurt - 1) SR^2 / 4) / T); "normal" uses Skew 0, Kurt 3. The HAC standard error
(the brief's (33.1)) is sqrt(g' Psi g / T) with g = (1/s, -mean/(2 s^3)) and Psi = (23.7)'s Bartlett estimate of the
long-run covariance of y_t = (x_t - mean, (x_t - mean)^2 - s^2), lag L by the book's rule floor(4 (T/100)^(2/9)),
no small-sample factor; at L = 0 it equals the plug-in (20.9). The two-Sharpe statistics follow Ledoit and Wolf
(2008, IEW WP 320): v = (mu_j, mu_1, gamma_j, gamma_1) with uncentred second moments, f = a/sqrt(c - a^2) -
b/sqrt(d - b^2), s(Delta) = sqrt(grad' Psi grad / T); Psi by (23.7) with the book's lag (their prewhitened QS kernel
and T/(T-4) factor are not used); the studentized circular block bootstrap with block size b, the bootstrap
standard error from the floor(T/b) complete blocks (Goetze-Kuensch, as their section 3.2.2), the centred statistic
|Delta* - Delta| / s(Delta*), the p-value (#{d* >= d} + 1) / (B + 1) and the symmetric interval
Delta +- z*_{0.95} s(Delta). Holm's adjusted p-values are (21.7)'s. PSR and MinTRL as Bailey and Lopez de Prado
(2012, appendix code): sqrt(T - 1) and the "1 +" term. The expected maximum E Z_(n) of n iid standard normals is the
exact integral from (21.9), int_0^inf (1 - Phi^n) - int_-inf^0 Phi^n; the approximation is Bailey and Lopez de
Prado's (2014), (1 - g) Phi^-1(1 - 1/n) + g Phi^-1(1 - 1/(n e)), g = 0.5772156649 (Euler's constant). The deflated
benchmark is SR_0 = E Z_(n) / sqrt(T - 1) per observation (the null standard deviation of (20.9) at SR = 0, on PSR's
T - 1). Haircuts as Harvey and Liu (2015): the two-sided normal p-value of t = SR sqrt(T), adjusted for n tests
(Bonferroni (21.6), Holm (21.7), or independent tests 1 - (1 - p)^n), back to SR via Phi^-1(1 - p_adj / 2) / sqrt(T);
their own example uses t with T - 1 degrees of freedom, as they print it.

Experiments (one generator each, created once at the start, np.random.default_rng([e, 20261011])):
  e = 1: the seven Ledoit-Wolf tests R2..R8 against R1, B = 9,999 circular-block resamples of the 1,851 dates
         (block size b by the book's rule, below), one set of block starts per resample shared by the seven pairs;
  e = 2: the maximum of eight correlated standard normals, N_8(0, C) with C the correlation matrix of the rules'
         daily excess returns, 1,000,000 draws (Cholesky), for the effective number of trials;
  e = 3: R2 against R1 at block sizes 1, 5, 10, 26, 50 and 100, B = 9,999 each, drawn in that order.
Block size: the book's rule of LM22 (lm22.md:254) on the circular scheme: the largest circular estimate of arch's
optimal_block_length among the eight rules' squared demeaned excess returns, rounded.

Rounding flags. Every number the brief prints passes through f(x, k1, k2, ...), which shows x with max(k) + 3
decimals and flags it "NEAR" for each printed precision k at which x lies within a tenth of a last-digit unit of a
rounding boundary (|frac(10^k |x|) - 0.5| < 0.1). The brief prints a flagged value as rounded from the unrounded value.

Prints one line per anchor, "A33-NN <value>", in ID order, and writes nothing.

Run:  PYTHONUTF8=1 uv run python data/vol6_anchors_lm33.py     (after data/vol5_series.py and data/vol3_series.py)
"""
import sys
from datetime import date
from math import ceil, e, floor, sqrt
from pathlib import Path

import numpy as np
import polars as pl
from arch.bootstrap import optimal_block_length
from numpy.typing import NDArray
from scipy import integrate, optimize, stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from vol5_rules import RF, RULES, signals, summary, wealth_path
from vol5_series import frames

PROC = HERE / "processed"
SEED = 20261011
EULER = 0.5772156649015329
Vec = NDArray[np.float64]
Mat = NDArray[np.float64]

OUT: list[str] = []
NEAR: list[str] = []


def put(value: str) -> None:
    """One anchor line; values that f() found near a rounding boundary are listed at its end."""
    tail = f" [NEAR a rounding boundary: {'; '.join(NEAR)}]" if NEAR else ""
    OUT.append(f"A33-{len(OUT) + 1:02d} {value}{tail}")
    NEAR.clear()


def f(x: float, *ks: int, plus: bool = False) -> str:
    """x with max(ks) + 3 decimals; flagged for each printed precision k within 0.1 of a last-digit unit of a boundary."""
    x = float(x)
    for k in ks:
        u = abs(x) * 10**k
        if abs(u - floor(u) - 0.5) < 0.1:
            NEAR.append(f"{x:.{k + 3}f} at {k} dp")
    return f"{x:{'+' if plus else ''}.{max(ks) + 3}f}"


def pc(x: float, *ks: int) -> str:
    """A fraction printed as a percentage (ks are the decimals of the percentage)."""
    return f(100 * x, *ks) + "%"


def lag_rule(n: int) -> int:
    return floor(4 * (n / 100) ** (2 / 9))


def lrv(Y: Mat, lag: int) -> Mat:
    """(23.7)'s Bartlett estimate of the long-run covariance of the rows of Y (already centred), divisor T."""
    T = Y.shape[0]
    S = Y.T @ Y / T
    for k in range(1, lag + 1):
        G = Y[k:].T @ Y[:-k] / T
        S = S + (1 - k / (lag + 1)) * (G + G.T)
    return S


def moments(x: Vec) -> tuple[float, float, float, float]:
    """mean, s (divisor T), sample skewness and raw kurtosis ((19.3), divisor T)."""
    m, s = float(x.mean()), float(x.std())
    c = x - m
    return m, s, float((c**3).mean() / s**3), float((c**4).mean() / s**4)


def v209(sr: float, sk: float, ku: float) -> float:
    """(20.9): T Var(SR hat) for iid returns."""
    return 1 - sr * sk + (ku - 1) / 4 * sr**2


def se_sr_hac(x: Vec, lag: int) -> float:
    """(33.1): the delta method (20.8) with (23.7)'s long-run covariance of (x - mean, (x - mean)^2 - s^2)."""
    T = len(x)
    m, s, _, _ = moments(x)
    c = x - m
    g = np.array([1 / s, -m / (2 * s**3)])
    return float(np.sqrt(g @ lrv(np.column_stack([c, c**2 - s**2]), lag) @ g / T))


def se_mean_hac(x: Vec, lag: int) -> float:
    c = (x - x.mean())[:, None]
    return float(np.sqrt(lrv(c, lag)[0, 0] / len(x)))


def se_vol_hac(x: Vec, lag: int) -> float:
    """SE of s: (x - mean)^2 has long-run variance Psi; d s / d s^2 = 1 / (2 s)."""
    m, s, _, _ = moments(x)
    c = ((x - m) ** 2 - s**2)[:, None]
    return float(np.sqrt(lrv(c, lag)[0, 0] / len(x)) / (2 * s))


def psr(sr: float, sr0: float, T: float, sk: float, ku: float) -> float:
    """Bailey and Lopez de Prado (2012): Phi((SR - SR_0) sqrt(T - 1) / sqrt(1 - Skew SR + (Kurt - 1) SR^2 / 4))."""
    return float(stats.norm.cdf((sr - sr0) * sqrt(T - 1) / sqrt(v209(sr, sk, ku))))


def mintrl(sr: float, sr0: float, sk: float, ku: float, conf: float = 0.95) -> float:
    """Bailey and Lopez de Prado (2012): 1 + (1 - Skew SR + (Kurt - 1) SR^2 / 4) (Phi^-1(conf) / (SR - SR_0))^2."""
    return 1 + v209(sr, sk, ku) * (stats.norm.ppf(conf) / (sr - sr0)) ** 2


def emax(n: float) -> float:
    """E Z_(n), the expected largest of n iid standard normals, from (21.9): int_0^inf (1 - Phi^n) - int_-inf^0 Phi^n."""
    if n == 1:
        return 0.0
    up = integrate.quad(lambda z: 1 - stats.norm.cdf(z) ** n, 0, 12, limit=200, epsabs=1e-13, epsrel=1e-13)[0]
    lo = integrate.quad(lambda z: stats.norm.cdf(z) ** n, -12, 0, limit=200, epsabs=1e-13, epsrel=1e-13)[0]
    return up - lo


def emax_bldp(n: float) -> float:
    """Bailey and Lopez de Prado's (2014) approximation of E Z_(n)."""
    return float((1 - EULER) * stats.norm.ppf(1 - 1 / n) + EULER * stats.norm.ppf(1 - 1 / (n * e)))


def holm(p: list[float]) -> list[float]:
    """(21.7)'s adjusted p-values, in the input order."""
    m = len(p)
    order = sorted(range(m), key=lambda i: p[i])
    adj = [0.0] * m
    run = 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (m - r) * p[i]))
        adj[i] = run
    return adj


def two_sided(t: float) -> float:
    return float(2 * stats.norm.sf(abs(t)))


# ---------------------------------------------------------------- data
fr = frames("E5")
sigs = signals(fr, [])
Aw = fr.A_wealth
paths = {k: wealth_path(fr, sigs, k) for k in RULES}
pq = pl.read_parquet(PROC / "vol5_rules.parquet")
for k in RULES:
    q = pq.filter(pl.col("rule") == k).sort("date")
    assert q["date"].to_list() == paths[k].dates and np.array_equal(q["wealth"].to_numpy(), paths[k].wealth), k
    assert paths[k].ruin is None, k
dates = paths["R1"].dates
R = {k: paths[k].wealth[1:] / paths[k].wealth[:-1] - 1 for k in RULES}
X = {k: R[k] - RF / Aw for k in RULES}
XM = np.column_stack([X[k] for k in RULES])
T = len(dates) - 1
L = lag_rule(T)
crit = {k: summary(fr, paths[k]) for k in RULES}
cal_years = (date.fromisoformat(dates[-1]) - date.fromisoformat(dates[0])).days / 365.25
tau = T / Aw
sqA = sqrt(Aw)
mom = {k: moments(X[k]) for k in RULES}
SR = {k: mom[k][0] / mom[k][1] for k in RULES}
for k in RULES:
    assert abs(SR[k] * sqA - float(crit[k]["sharpe"])) < 1e-12, k

tr = pl.read_parquet(PROC / "vol3_taiex.parquet").sort("date").drop_nulls("R")
Rt = tr["R"].to_numpy().astype(float)
Tt = len(Rt)
tr_years = (tr["date"][-1] - date(2003, 1, 2)).days / 365.25
At = Tt / tr_years
Lt = lag_rule(Tt)

# ---------------------------------------------------------------- data role
put(f"T {T} daily returns {dates[1]} .. {dates[-1]} (first trade {dates[0]}); tau = T/A_w {f(tau, 2, 4)} years; "
    f"calendar years from the first trade {f(cal_years, 4)}")
put(f"A_w {f(Aw, 2, 4)} (wealth frame {len(fr.wealth_dates)} sessions); RF {RF}; RF/A_w per session "
    f"{f(RF / Aw * 1e4, 4)} bp; sqrt(A_w) {f(sqA, 4)}")
ym = [d[:7] for d in dates]
ends = [i for i in range(len(dates)) if i == len(dates) - 1 or ym[i] != ym[i + 1]]
full = [i for i in ends if "2019-03" <= ym[i] <= "2026-09"]
nsess = np.diff(full)
mar19 = sum(1 for d in dates[1:] if d[:7] == "2019-03")
oct26 = sum(1 for d in dates[1:] if d[:7] == "2026-10")
TM = len(full) - 1
put(f"months: {TM} full months {ym[full[1]]} .. {ym[full[-1]]}, {int(nsess.min())}-{int(nsess.max())} sessions "
    f"each; left out: 2019-03 ({mar19} returns from {dates[1]}), 2026-10 ({oct26} returns)")
put(f"HAC lag rule floor(4 (T/100)^(2/9)): T={T} -> {L}; TR23 T={Tt} -> {Lt}; months T={TM} -> {lag_rule(TM)}")
put(f"TR23: T {Tt} returns {tr['date'][0]} .. {tr['date'][-1]}; years {f(tr_years, 4)}; A {f(At, 2)}; r_f = 0")

# ---------------------------------------------------------------- checkpoint table, one line per rule
SE9, SEH, SEN = {}, {}, {}
for k in RULES:
    m, s, sk, ku = mom[k]
    sr = SR[k]
    SE9[k] = sqrt(v209(sr, sk, ku) / T)
    SEN[k] = sqrt((1 + sr**2 / 2) / T)
    SEH[k] = se_sr_hac(X[k], L)
    assert abs(se_sr_hac(X[k], 0) - SE9[k]) < 1e-15, k               # (33.1) at lag 0 is the plug-in (20.9)
    se_m = s / sqrt(T)
    se_v = s * sqrt((ku - 1) / (4 * T))
    lo9, hi9 = (sr - 1.959964 * SE9[k]) * sqA, (sr + 1.959964 * SE9[k]) * sqA
    loh, hih = (sr - 1.959964 * SEH[k]) * sqA, (sr + 1.959964 * SEH[k]) * sqA
    put(f"{k}: SR a year {f(sr * sqA, 2, 3, 4)} (daily {f(sr, 4)}); mean excess a year {pc(m * Aw, 2)} "
        f"(SE iid {pc(se_m * Aw, 2)}, HAC {pc(se_mean_hac(X[k], L) * Aw, 2)}); vol {pc(s * sqA, 2)} "
        f"(SE iid {pc(se_v * sqA, 2)}, HAC {pc(se_vol_hac(X[k], L) * sqA, 2)}); skew {f(sk, 2)}, raw kurt "
        f"{f(ku, 1)}; SE(SR) a year normal {f(SEN[k] * sqA, 3)}, (20.9) {f(SE9[k] * sqA, 2, 3)}, HAC(L={L}) "
        f"{f(SEH[k] * sqA, 2, 3)}; 95% (20.9) {f(lo9, 2)} to {f(hi9, 2)}, HAC {f(loh, 2)} to {f(hih, 2)}")
best = max(RULES, key=lambda k: SR[k])
worst = min(RULES, key=lambda k: SR[k])

# ---------------------------------------------------------------- case and E1
m2, s2, sk2, ku2 = mom["R2"]
put(f"best {best} {f(SR[best] * sqA, 2)}, R1 {f(SR['R1'] * sqA, 2)}, worst {worst} {f(SR[worst] * sqA, 2)}; "
    f"R2 - R1 {f((SR['R2'] - SR['R1']) * sqA, 2, 3)} a year; rules inside R2's (20.9) interval: "
    f"{sum(1 for k in RULES if k != 'R2' and abs(SR[k] - SR['R2']) < 1.959964 * SE9['R2'])} of 7")
put(f"E1 R2: daily mean excess {f(m2 * 100, 4)}%, s {f(s2 * 100, 4)}%, SR {f(m2 / s2, 5)}; (20.9) factor "
    f"1 - SR Skew + (Kurt-1) SR^2/4 = 1 + {f(-SR['R2'] * sk2, 5)} + {f((ku2 - 1) / 4 * SR['R2'] ** 2, 5)} = "
    f"{f(v209(SR['R2'], sk2, ku2), 4)}; SE daily {f(SE9['R2'], 5)}, a year {f(SE9['R2'] * sqA, 3)}; "
    f"SR sqrt(T) = t-stat {f(SR['R2'] * sqrt(T), 2)}")
put("PSR(0) by rule (one-sided p = 1 - PSR): " + ", ".join(
    f"{k} {f(psr(SR[k], 0, T, mom[k][2], mom[k][3]), 3, 4)}" for k in RULES)
    + "; Holm (21.7) on the 8 one-sided p: rejections at 5% "
    + str(sum(1 for a in holm([1 - psr(SR[k], 0, T, mom[k][2], mom[k][3]) for k in RULES]) if a <= 0.05 + 1e-12))
    + "; largest Holm-adjusted p " + f(max(holm([1 - psr(SR[k], 0, T, mom[k][2], mom[k][3]) for k in RULES])), 3))
z90 = stats.norm.ppf(0.95)
put(f"R4: two-sided 95% (20.9) {f((SR['R4'] - 1.959964 * SE9['R4']) * sqA, 2, plus=True)} to "
    f"{f((SR['R4'] + 1.959964 * SE9['R4']) * sqA, 2)} contains 0; one-sided PSR(0) "
    f"{f(psr(SR['R4'], 0, T, mom['R4'][2], mom['R4'][3]), 3)}; two-sided 90% {f((SR['R4'] - z90 * SE9['R4']) * sqA, 2)} "
    f"to {f((SR['R4'] + z90 * SE9['R4']) * sqA, 2)}")

# ---------------------------------------------------------------- dependence
put("SE(SR) a year by HAC lag (0 = (20.9) plug-in): " + "; ".join(
    f"{k} " + ", ".join(f"L={lg} {f(se_sr_hac(X[k], lg) * sqA, 3)}" for lg in (0, L, 20, 60)) for k in ("R1", "R2", "R4"))
    + "; HAC / iid at L=" + str(L) + ": " + ", ".join(f"{k} {f(SEH[k] / SE9[k], 2)}" for k in RULES))
put("rho_1 of daily excess returns (19.5): " + ", ".join(
    f"{k} {f(float((X[k][1:] - X[k].mean()) @ (X[k][:-1] - X[k].mean()) / ((X[k] - X[k].mean()) @ (X[k] - X[k].mean()))), 3)}"
    for k in RULES) + "; rho_1 of squared demeaned R1 " + f(float(np.corrcoef(
        (X['R1'] - X['R1'].mean())[1:] ** 2, (X['R1'] - X['R1'].mean())[:-1] ** 2)[0, 1]), 3))
vr = {k: se_vol_hac(X[k], L) / (mom[k][1] * sqrt((mom[k][3] - 1) / (4 * T))) for k in RULES}
put("vol SE HAC/iid at L=" + str(L) + ": " + ", ".join(f"{k} {f(vr[k], 2)}" for k in RULES)
    + "; R1 vol SE a year iid " + pc(mom['R1'][1] * sqrt((mom['R1'][3] - 1) / (4 * T)) * sqA, 2)
    + ", HAC " + pc(se_vol_hac(X['R1'], L) * sqA, 2) + ", HAC L=20 " + pc(se_vol_hac(X['R1'], 20) * sqA, 2)
    + ", HAC L=60 " + pc(se_vol_hac(X['R1'], 60) * sqA, 2))
mt, st, skt, kut = moments(Rt)
srt = mt / st
put(f"TR23: SR daily {f(srt, 4)}, a year {f(srt * sqrt(At), 2, 4)}; skew {f(skt, 2)}, raw kurt {f(kut, 2)}; SE a "
    f"year (20.9) {f(sqrt(v209(srt, skt, kut) / Tt) * sqrt(At), 3)} (lm20.md:401, 0.207), HAC L={Lt} "
    f"{f(se_sr_hac(Rt, Lt) * sqrt(At), 3)}, HAC L=145 {f(se_sr_hac(Rt, 145) * sqrt(At), 3)}; LM22 blocks of 145: "
    f"stationary 0.233, circular 0.244, moving 0.247 (lm22.md:216-219)")

# ---------------------------------------------------------------- annualization
line = []
eta: dict[str, float] = {}
den: dict[str, float] = {}
for k in RULES:
    w = paths[k].wealth[full]
    xm = np.log(w[1:] / w[:-1]) - nsess * np.log(1 + RF / Aw)
    c = xm - xm.mean()
    rho = [float(c[j:] @ c[:-j] / (c @ c)) for j in range(1, 12)]
    den[k] = 1 + 2 * sum((1 - j / 12) * rho[j - 1] for j in range(1, 12))
    eta[k] = sqrt(12) / sqrt(den[k])
    srm = float(xm.mean() / xm.std())
    se_rob2 = sum((2 * (1 - j / 12)) ** 2 * float(np.sum(c[j:] ** 2 * c[:-j] ** 2)) / float(c @ c) ** 2
                  for j in range(1, 12))
    line.append(f"{k} SR_month {f(srm, 4)}, x sqrt12 {f(srm * sqrt(12), 2)}, Lo {f(srm * eta[k], 2)} "
                f"(eta {f(eta[k], 2)}; 1 + 2 sum (1-k/12) rho_k = {f(den[k], 2)}, robust SE (25.6) {f(sqrt(se_rob2), 2)}; "
                f"rho_1 {f(rho[0], 3)})")
put("monthly log excess returns, 90 months: " + "; ".join(line))
se_iid12 = sqrt(2 * (2 * 12 - 1) * (12 - 1) / (3 * 12 * TM))
put(f"(25.6) iid SE of VR(12) - 1 at T={TM}: {f(se_iid12, 3)}; R1's {f(den['R1'] - 1, 2)} is "
    f"{f((den['R1'] - 1) / se_iid12, 1)} SEs; eta range over rules {f(min(eta.values()), 2)}..{f(max(eta.values()), 2)} "
    f"against sqrt12 {f(sqrt(12), 4)}")
ar = 12 / sqrt(12 + 2 * sum((12 - j) * 0.2**j for j in range(1, 12)))
put(f"Lo (2002) checks: eta(12) iid {f(sqrt(12), 2)}; AR(1) rho=0.2 {f(ar, 2, 3)} (Lo's Table 2: 2.88); "
    f"eta(12) at rho=0.2 / sqrt12 {f(ar / sqrt(12), 3)}; sqrt12 / eta {f(sqrt(12) / ar, 3)}")
xd = {k: np.log(paths[k].wealth[1:] / paths[k].wealth[:-1]) - np.log(1 + RF / Aw) for k in RULES}
put("daily log excess SR x sqrt(A_w): " + ", ".join(f"{k} {f(xd[k].mean() / xd[k].std() * sqA, 2)}" for k in RULES))

# ---------------------------------------------------------------- PSR and MinTRL
psr_lines = []
for k in ("R2", "R1", worst):
    _, _, sk, ku = mom[k]
    n0 = mintrl(SR[k], 0, sk, ku)
    psr_lines.append(f"{k} PSR(0) {f(psr(SR[k], 0, T, sk, ku), 3, 4)}, MinTRL(0) {f(n0, 0)} sessions = "
                     f"{f(n0 / Aw, 2)} years; normal MinTRL {f(mintrl(SR[k], 0, 0, 3) / Aw, 2)} years")
put("; ".join(psr_lines))
zt = (SR["R2"]) * sqrt(T - 1) / sqrt(v209(SR["R2"], sk2, ku2))
put(f"R2 PSR z with sqrt(T-1) {f(zt, 3)}, with sqrt(T) {f(zt * sqrt(T / (T - 1)), 3)}; factor sqrt(T/(T-1)) - 1 "
    f"= {pc(sqrt(T / (T - 1)) - 1, 3)}")
n_tr = mintrl(srt, 0, skt, kut)
put(f"TR23 PSR(0) {f(psr(srt, 0, Tt, skt, kut), 5)}; MinTRL(0) {f(n_tr, 0)} sessions = {f(n_tr / At, 2)} years; "
    f"(21.4) one-sided at power 1/2, (1.645/SR)^2 = {f((stats.norm.ppf(0.95) / (srt * sqrt(At))) ** 2, 2)} "
    f"years; (21.4) two-sided 80% power 11.9 years (lm21.md:177, 183)")
put("X4 normal returns, A_w: MinTRL(0) years at annual SR " + ", ".join(
    f"{a} {f(mintrl(a / sqA, 0, 0, 3) / Aw, 2)}" for a in (0.5, 1.0, 1.5))
    + "; PSR(0) at tau = " + f(tau, 2) + " years: " + ", ".join(
        f"{a} {f(psr(a / sqA, 0, T, 0, 3), 3)}" for a in (0.5, 1.0, 1.5)))
bl12 = [2.0, 12**0.5, -0.72, 5.78]
srm12 = bl12[0] / bl12[1]
n12 = mintrl(srm12, 1 / 12**0.5, bl12[2], bl12[3])
put(f"Bailey-LdP (2012) appendix example: monthly SR {f(srm12, 4)}, SR_0 {f(1 / 12**0.5, 4)}, skew -0.72, kurt 5.78: "
    f"MinTRL {f(n12, 3)} months = {f(n12 / 12, 2)} years; PSR at 59.895 obs {f(psr(srm12, 1 / 12**0.5, 59.895, -0.72, 5.78), 4)}")
put(f"R2 MinTRL against SR_0 = R1's estimate (the misuse): {f(mintrl(SR['R2'], SR['R1'], sk2, ku2) / Aw, 1)} years; "
    f"PSR(SR_R1) {f(psr(SR['R2'], SR['R1'], T, sk2, ku2), 3)}")

# ---------------------------------------------------------------- two Sharpe ratios
obl = [optimal_block_length((X[k] - X[k].mean()) ** 2) for k in RULES]
circ = [float(o["circular"].iloc[0]) for o in obl]
stat_ = [float(o["stationary"].iloc[0]) for o in obl]
b_rule = round(max(circ))
put("optimal_block_length on squared demeaned excess returns, circular: " + ", ".join(
    f"{k} {f(c, 2)}" for k, c in zip(RULES, circ, strict=True)) + f"; largest {f(max(circ), 2)} -> b = {b_rule}; "
    f"stationary largest {f(max(stat_), 2)}")


def lw_parts(xj: Vec, x1: Vec, lag: int) -> tuple[float, float]:
    """(Delta hat, s(Delta hat)) per observation, Ledoit and Wolf's (5) with (23.7)'s Psi."""
    a, b_, c, d = xj.mean(), x1.mean(), (xj**2).mean(), (x1**2).mean()
    Y = np.column_stack([xj - a, x1 - b_, xj**2 - c, x1**2 - d])
    grad = np.array([c / (c - a**2) ** 1.5, -d / (d - b_**2) ** 1.5,
                     -0.5 * a / (c - a**2) ** 1.5, 0.5 * b_ / (d - b_**2) ** 1.5])
    delta = a / sqrt(c - a**2) - b_ / sqrt(d - b_**2)
    return float(delta), float(np.sqrt(grad @ lrv(Y, lag) @ grad / len(xj)))


def lw_boot(XA: Mat, pairs: list[tuple[int, int]], b: int, B: int, rng: np.random.Generator) -> NDArray[np.float64]:
    """Centred studentized statistics |Delta* - Delta| / s(Delta*) for every pair, B circular-block resamples."""
    Tn = XA.shape[0]
    nb, lb = ceil(Tn / b), Tn // b
    base = {p: lw_parts(XA[:, p[0]], XA[:, p[1]], 0)[0] for p in pairs}
    out = np.empty((B, len(pairs)))
    ar_ = np.arange(b)
    for i in range(B):
        idx = ((rng.integers(0, Tn, size=nb)[:, None] + ar_) % Tn).ravel()[:Tn]
        Xs = XA[idx]
        mu, ga = Xs.mean(axis=0), (Xs**2).mean(axis=0)
        Ys = np.concatenate([Xs - mu, Xs**2 - ga], axis=1)[: lb * b]
        Z = Ys.reshape(lb, b, -1).sum(axis=1) / sqrt(b)
        P = Z.T @ Z / lb
        nr = XA.shape[1]
        for jj, (j, o) in enumerate(pairs):
            a, b_, c, d = mu[j], mu[o], ga[j], ga[o]
            grad = np.array([c / (c - a**2) ** 1.5, -d / (d - b_**2) ** 1.5,
                             -0.5 * a / (c - a**2) ** 1.5, 0.5 * b_ / (d - b_**2) ** 1.5])
            ix = [j, o, nr + j, nr + o]
            se = sqrt(float(grad @ P[np.ix_(ix, ix)] @ grad) / Tn)
            ds = a / sqrt(c - a**2) - b_ / sqrt(d - b_**2)
            out[i, jj] = abs(ds - base[(j, o)]) / se
    return out


B = 9999
pairs = [(j, 0) for j in range(1, 8)]
rng1 = np.random.default_rng([1, SEED])
dstar = lw_boot(XM, pairs, b_rule, B, rng1)
rows = []
p_boot, p_hac = [], []
for jj, (j, o) in enumerate(pairs):
    k = RULES[j]
    dl, sd = lw_parts(XM[:, j], XM[:, o], L)
    t = dl / sd
    pb = (int(np.sum(dstar[:, jj] >= abs(t) - 1e-12)) + 1) / (B + 1)
    p_boot.append(pb)
    p_hac.append(two_sided(t))
    zq = float(np.quantile(dstar[:, jj], 0.95, method="inverted_cdf"))
    rows.append((k, dl, sd, t, pb, zq, float(np.corrcoef(XM[:, j], XM[:, o])[0, 1])))
hb = holm(p_boot)
hh = holm(p_hac)
for (k, dl, sd, t, pb, zq, rr), a1, a2, ph in zip(rows, hb, hh, p_hac, strict=True):
    put(f"{k} - R1: Delta a year {f(dl * sqA, 2, 3, plus=True)}; corr {f(rr, 3, 2)}; s(Delta) HAC(L={L}) a year "
        f"{f(sd * sqA, 3)}; t-stat {f(t, 2, plus=True)}; HAC p {f(ph, 3, 2)} (Holm {f(a2, 2)}); boot p {f(pb, 3, 2)} "
        f"(Holm {f(a1, 2)}; MC SE {f(sqrt(pb * (1 - pb) / B), 3)}); z*(0.95) {f(zq, 2)}; 95% interval "
        f"{f((dl - zq * sd) * sqA, 2, plus=True)} to {f((dl + zq * sd) * sqA, 2, plus=True)}")

# ---------------------------------------------------------------- R2 vs R1 detail
dl21, sd21 = lw_parts(X["R2"], X["R1"], L)
r21 = float(np.corrcoef(X["R2"], X["R1"])[0, 1])
naive = sqrt(SE9["R2"] ** 2 + SE9["R1"] ** 2)
put(f"R2 vs R1: independent-samples SE a year (as (21.3)) {f(naive * sqA, 3)} against LW HAC {f(sd21 * sqA, 3)}; "
    f"ratio {f(sd21 / naive, 2)} (sqrt(1 - rho) {f(sqrt(1 - r21), 2)}); s(Delta) a year by lag: "
    + ", ".join(f"L={lg} {f(lw_parts(X['R2'], X['R1'], lg)[1] * sqA, 3)}" for lg in (0, L, 26, 60))
    + f"; one-sided Phi(t-stat) {f(float(stats.norm.cdf(dl21 / sd21)), 2, 3)}")
c21 = sd21 * sqrt(tau)                        # s(Delta) per sqrt(year), annual units: SE = c / sqrt(years)
z80 = stats.norm.ppf(0.975) + stats.norm.ppf(0.8)
put(f"years to tell R2 from R1 if the gap {f(dl21 * sqA, 3)} were true: (21.4) 80% two-sided "
    f"{f((z80 * c21 * sqA / (dl21 * sqA)) ** 2, 0)} years; one-sided 95% at power 1/2 "
    f"{f((stats.norm.ppf(0.95) * c21 * sqA / (dl21 * sqA)) ** 2, 0)} years (observed {f(tau, 2)})")
rng3 = np.random.default_rng([3, SEED])
sens = []
for bb in (1, 5, 10, 26, 50, 100):
    ds_ = lw_boot(XM[:, [1, 0]], [(0, 1)], bb, B, rng3)[:, 0]
    sens.append(f"b={bb} {f((int(np.sum(ds_ >= abs(dl21 / sd21) - 1e-12)) + 1) / (B + 1), 2)}")
put("R2 - R1 boot p by block size (experiment 3): " + ", ".join(sens))
put(f"Holm on seven boot p: smallest adjusted {f(min(hb), 2)}; rejections at 5% {sum(1 for a in hb if a <= 0.05 + 1e-12)}; "
    f"on seven HAC p: smallest adjusted {f(min(hh), 2)}")

# ---------------------------------------------------------------- deflation
put("E Z_(n) exact / Bailey-LdP approx / (21.9) median: " + "; ".join(
    f"n={n} {f(emax(n), 3, 4)} / {f(emax_bldp(n), 3)} / {f(stats.norm.ppf(0.5 ** (1 / n)), 2)}"
    for n in (2, 8, 10, 100, 1000, 10000)))
s0 = 1 / sqrt(T - 1)
SR0_8 = emax(8) * s0
put(f"null SD of SR hat 1/sqrt(T-1): daily {f(s0, 5)}, a year {f(s0 * sqA, 3)}; deflated SR_0 at n=8 a year: exact "
    f"{f(SR0_8 * sqA, 2, 3)}, approx {f(emax_bldp(8) * s0 * sqA, 3)}")


def dsr_at(n: float, se_daily: float | None = None) -> float:
    sr0 = emax(n) * s0
    if se_daily is None:
        return psr(SR["R2"], sr0, T, sk2, ku2)
    return float(stats.norm.cdf((SR["R2"] - sr0) / se_daily))


nstar = optimize.brentq(lambda n: dsr_at(n) - 0.95, 2, 100, xtol=1e-10)
put(f"DSR of R2: n=8 exact {f(dsr_at(8), 3, 4)}, n=8 approx {f(psr(SR['R2'], emax_bldp(8) * s0, T, sk2, ku2), 3, 4)}; "
    f"with R2's HAC SE {f(dsr_at(8, SEH['R2']), 3, 4)}; DSR = 0.95 at n = {f(nstar, 1, 2)}")
Cm = np.corrcoef(XM, rowvar=False)
off = Cm[~np.eye(8, dtype=bool)]
iu = np.triu_indices(8, 1)
pmin = int(np.argmin(Cm[iu]))
pmax = int(np.argmax(Cm[iu]))
put(f"correlations of daily excess returns: mean off-diagonal {f(float(off.mean()), 3)}; min "
    f"{RULES[iu[0][pmin]]}-{RULES[iu[1][pmin]]} {f(float(Cm[iu][pmin]), 3)}; max {RULES[iu[0][pmax]]}-"
    f"{RULES[iu[1][pmax]]} {f(float(Cm[iu][pmax]), 3)}; R6-R8 {f(float(Cm[5, 7]), 3)}; R2-R1 {f(float(Cm[1, 0]), 3)}")
rng2 = np.random.default_rng([2, SEED])
Zc = rng2.standard_normal((1_000_000, 8)) @ np.linalg.cholesky(Cm).T
mx = Zc.max(axis=1)
emc, emc_se = float(mx.mean()), float(mx.std() / sqrt(len(mx)))
neff = optimize.brentq(lambda n: emax(n) - emc, 1.000001, 8, xtol=1e-12)
d_lo = optimize.brentq(lambda n: emax(n) - (emc - 2 * emc_se), 1.000001, 8, xtol=1e-12)
d_hi = optimize.brentq(lambda n: emax(n) - (emc + 2 * emc_se), 1.000001, 8, xtol=1e-12)
put(f"experiment 2: E max of N_8(0, C) {f(emc, 3)} (MC SE {f(emc_se, 4)}, 10^6 draws); n_eff {f(neff, 2)} "
    f"(+-2 MC SE: {f(d_lo, 3)} to {f(d_hi, 3)}); rho_bar + (1 - rho_bar) 8 = {f(float(off.mean()) + (1 - float(off.mean())) * 8, 2)}; "
    f"DSR of R2 at n_eff {f(psr(SR['R2'], emc * s0, T, sk2, ku2), 3)}; deflated SR_0 a year {f(emc * s0 * sqA, 2)}")
sv2 = sqrt(v209(SR["R2"], sk2, ku2))


def mintrl_n(ez: float) -> float:
    """Sessions T with DSR = 0.95 after trials whose E Z_(n) is ez: 1 + ((Phi^-1(0.95) sqrt(V) + ez) / SR)^2."""
    return 1 + ((z90 * sv2 + ez) / SR["R2"]) ** 2


put(f"R2 MinTRL after n trials, 1 + ((1.645 sqrt(V) + E Z_(n)) / SR)^2: n=1 {f(mintrl_n(0) / Aw, 2)} years; n=8 "
    f"{f(mintrl_n(emax(8)), 0)} sessions = {f(mintrl_n(emax(8)) / Aw, 2)} years; n_eff {f(mintrl_n(emc) / Aw, 2)} years; "
    f"n=100 {f(mintrl_n(emax(100)) / Aw, 1)} years; sqrt(V) {f(sv2, 5)} (observed {T} sessions)")
srs = np.array([SR[k] for k in RULES])
cs_sd = float(srs.std())
exp_sd = sqrt((1 - float(Cm.sum()) / 64) / T)
put(f"cross-section of the 8 daily SRs: SD (divisor 8) {f(cs_sd, 5)} = {f(cs_sd * sqA, 3)} a year; expected under "
    f"equal true SRs sqrt((1 - 1'C1/64)/T) {f(exp_sd, 5)} = {f(exp_sd * sqA, 3)} a year; Bailey-LdP SR_0 = SD x approx(8) "
    f"{f(cs_sd * emax_bldp(8) * sqA, 2)} a year, DSR {f(psr(SR['R2'], cs_sd * emax_bldp(8), T, sk2, ku2), 3)}")
v14 = 0.5 / 250
sr14 = 2.5 / sqrt(250)


def dsr14(n: float, sk: float, ku: float) -> float:
    return psr(sr14, sqrt(v14) * emax_bldp(n), 1250, sk, ku)


put(f"Bailey-LdP (2014) example (SR 2.5 a year, T 1250, V 1/2, skew -3, kurt 10, 250 a year): SR_0 daily "
    f"{f(sqrt(v14) * emax_bldp(100), 4)} at N=100, DSR {f(dsr14(100, -3, 10), 4)}; N=46 {f(dsr14(46, -3, 10), 4)}; "
    f"normal N=88 {f(dsr14(88, 0, 3), 4)}")
put("X6 deflated SR_0 a year (exact) at n = " + ", ".join(
    f"{n} {f(emax(n) * s0 * sqA, 2)}" for n in (1, 2, 8, 10, 100, 1000, 10000))
    + f"; pass line SR_R2 - 1.645 SE(20.9) a year {f((SR['R2'] - stats.norm.ppf(0.95) * sqrt(v209(SR['R2'], sk2, ku2) / (T - 1))) * sqA, 2)}")

# ---------------------------------------------------------------- haircuts
pS = {k: two_sided(SR[k] * sqrt(T)) for k in RULES}
hol = dict(zip(RULES, holm([pS[k] for k in RULES]), strict=True))


def hsr(p_adj: float) -> float:
    return 0.0 if p_adj >= 1 else float(stats.norm.isf(p_adj / 2) / sqrt(T) * sqA)


hc_lines = []
for k in RULES:
    pb_, ph_, pi_ = min(1.0, 8 * pS[k]), hol[k], 1 - (1 - pS[k]) ** 8
    hc_lines.append(f"{k} t {f(SR[k] * sqrt(T), 2)} p {f(pS[k], 4)}: HSR Bonf {f(hsr(pb_), 2)} ({pc(1 - hsr(pb_) / (SR[k] * sqA), 0)}), "
                    f"Holm {f(hsr(ph_), 2)} ({pc(1 - hsr(ph_) / (SR[k] * sqA), 0)}), indep {f(hsr(pi_), 2)} "
                    f"({pc(1 - hsr(pi_) / (SR[k] * sqA), 0)})")
put("haircuts, n = 8 (two-sided normal p of SR sqrt(T)): " + "; ".join(hc_lines))
k2 = "R2"
put(f"E9 R2: t {f(SR[k2] * sqrt(T), 3)}, single p {f(pS[k2], 5)}; 1-(1-p)^8 {f(1 - (1 - pS[k2]) ** 8, 4)}; 8p "
    f"{f(8 * pS[k2], 4)}; t* {f(float(stats.norm.isf((1 - (1 - pS[k2]) ** 8) / 2)), 2)}; HSR (indep) "
    f"{f(hsr(1 - (1 - pS[k2]) ** 8), 3)} a year, haircut {pc(1 - hsr(1 - (1 - pS[k2]) ** 8) / (SR[k2] * sqA), 1)}")
t240 = 0.75 / sqrt(12) * sqrt(240)
ps240 = float(2 * stats.t.sf(t240, 239))
pm240 = 1 - (1 - ps240) ** 200
h240 = float(stats.t.isf(pm240 / 2, 239)) / sqrt(240) * sqrt(12)
hn240 = float(stats.norm.isf((1 - (1 - two_sided(t240)) ** 200) / 2)) / sqrt(240) * sqrt(12)
put(f"Harvey-Liu (2015) example (T 240 months, SR 0.75 a year, N 200, t with 239 df): t {f(t240, 3)}, single p "
    f"{f(ps240, 4)}; p_M {f(pm240, 3)}; HSR {f(h240, 2)}; haircut {pc(1 - h240 / 0.75, 0)}; normal reference: single p "
    f"{f(two_sided(t240), 4)}, p_M {f(1 - (1 - two_sided(t240)) ** 200, 3)}, HSR {f(hn240, 2)}, haircut "
    f"{pc(1 - hn240 / 0.75, 0)} (they print 0.0008, 0.15, 0.32 and about 60%)")
put(f"sizing pointer: the quadratic Kelly fraction mean/var (lm04.md:561) scales with SR / sigma, so the independent-"
    f"test haircut of R2 cuts it by the same {pc(1 - hsr(1 - (1 - pS[k2]) ** 8) / (SR[k2] * sqA), 0)} at a fixed sigma")

# ---------------------------------------------------------------- problems
put(f"P1 normal SE(SR) daily SR 0.06, T 1,851: {f(sqrt((1 + 0.06**2 / 2) / 1851), 4)} daily, x sqrt(243.57) "
    f"{f(sqrt((1 + 0.06**2 / 2) / 1851) * sqrt(243.57), 3)}; distractors: no sqrt(A) {f(sqrt((1 + 0.06**2 / 2) / 1851), 4)}, "
    f"x A {f(sqrt((1 + 0.06**2 / 2) / 1851) * 243.57, 2)}")
put(f"P2 SE of a monthly SR 0.30, skew -1.0, raw kurt 8.0, T 90 by (20.9): factor {f(v209(0.3, -1, 8), 4)}, SE "
    f"{f(sqrt(v209(0.3, -1, 8) / 90), 3)}; excess kurtosis 5 typed as Kurt: {f(sqrt(v209(0.3, -1, 5) / 90), 3)}; normal "
    f"{f(sqrt(v209(0.3, 0, 3) / 90), 3)}")
n3, n3b, n3c = mintrl(0.05, 0, 0, 3), mintrl(0.05, 0, 0, 3, conf=0.975), mintrl(0.05 * sqrt(243.57), 0, 0, 3)
put(f"P3 MinTRL(0) daily SR 0.05, normal, 95%: {f(n3, 1)} obs = {f(n3 / 243.57, 2)} years at 243.57; Phi^-1(0.975) "
    f"in place of Phi^-1(0.95): {f(n3b, 0)} obs = {f(n3b / 243.57, 2)} years; the annual SR in the daily formula: "
    f"{f(n3c, 2)} obs = {f(n3c / 243.57, 3)} years")
put(f"P4 E Z_(n) n=3 {f(emax(3), 4)}; n=5 {f(emax(5), 3, 4)}; approximation n=5 {f(emax_bldp(5), 3, 4)}; "
    f"(21.9) median n=5 {f(stats.norm.ppf(0.5 ** 0.2), 3, 4)}")
put(f"P5 (19.9) scale factor for months, rho_1 = 0.1 and no other: {f(12 / sqrt(12 + 2 * 11 * 0.1), 3)}; with "
    f"rho_1 = -0.1: {f(12 / sqrt(12 - 2 * 11 * 0.1), 3)}; sqrt12 {f(sqrt(12), 3)}")
put(f"P6 two SRs 1.0 and 0.8 a year, each SE 0.36, correlation 0.9: SE(diff) {f(0.36 * sqrt(2 * 0.1), 3)}, t "
    f"{f(0.2 / (0.36 * sqrt(2 * 0.1)), 2)}; as if independent {f(0.36 * sqrt(2), 3)}, t {f(0.2 / (0.36 * sqrt(2)), 2)}; "
    f"0.36 (1 - 0.9) {f(0.36 * 0.1, 3)}")
put(f"P7 haircut: t 2.5, n 10 independent: p {f(two_sided(2.5), 4)}, p_M {f(1 - (1 - two_sided(2.5)) ** 10, 4)}, "
    f"t* {f(float(stats.norm.isf((1 - (1 - two_sided(2.5)) ** 10) / 2)), 3)}, haircut "
    f"{pc(1 - float(stats.norm.isf((1 - (1 - two_sided(2.5)) ** 10) / 2)) / 2.5, 1)}; Bonferroni t* "
    f"{f(float(stats.norm.isf(10 * two_sided(2.5) / 2)), 3)}, haircut {pc(1 - float(stats.norm.isf(10 * two_sided(2.5) / 2)) / 2.5, 1)}")

put(f"KC 9: scipy.stats.kurtosis(R2's excess returns) with its defaults (fisher=True, bias=True) "
    f"{f(float(stats.kurtosis(X['R2'])), 2)} (excess); fisher=False {f(float(stats.kurtosis(X['R2'], fisher=False)), 2)}; "
    f"skew {f(float(stats.skew(X['R2'])), 3)}")
print("\n".join(OUT))
