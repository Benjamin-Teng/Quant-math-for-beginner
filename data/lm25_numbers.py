"""Every number that LM25 (Time Series I: ARMA, Unit Roots and Cointegration) quotes, computed and checked.

Run:  uv run python data/lm25_numbers.py      (after data/vol3_series.py and data/vol4_series.py)

Inputs, read through data/lm25_common.py: data/processed/vol4_tx23.parquet (TX23: the TX near-month settlement from
FinMind's TaiwanFuturesDaily and the TAIEX price close on TR23's 5,850 dates, built and checked by
data/vol4_series.py) and data/processed/vol3_taiex.parquet (TR23: the TAIEX total-return and price indices). The
module text is src/lm25.md with its chart files src/data/lm25-*.json (written by data/lm25_charts.py);
plans/vol-4-anchors.md holds the Stage 1 anchors (A25-nn). The script started from data/vol4_anchors_lm25.py: part 1
recomputes every anchor line with the same definitions and compares it with the anchor table, reporting a difference
rather than forcing it; part 2 checks every number the module prints.

Conventions (as the module states them; data/lm25_common.py lists them): the log basis b = ln(F/S) in bp; rolled
changes difference the stored series, roll-free changes are rF - rS; D is the leading block of 5,834 dates whose
contract expires in the sample; TR23's 5,849 log returns for the autocorrelation tests; s divides by the number of
terms, s_eps by T - 2; rho_hat_k by LM19's (19.5); quantiles and medians by numpy's inverted_cdf; LM18's batch
standard error; ARMA at the likelihood maximum with standard errors from -l''. Simulations: experiments 1-4, each
with np.random.default_rng([e, 20261011]) created once (data/lm25_common.py: df_null, spurious).

Checks (each stops the script on a failure):
  chk(label, value, fmt, printed)  format(value, fmt) equals the printed string, the value does not sit on a rounding
                                   tie of that format, and the printed string is in the module (or its charts) as a
                                   whole number. Hand computations are redone from the printed, rounded inputs
                                   (project/PITFALLS.md section 7), as separate checks.
  has(label, text)                 a literal string (a table row, a list, a phrase) is in the module.
At the end the script lists the module's numbers that no check covered and the near-boundary flags, and prints
"all N checks passed".
"""
import datetime as dt
import json
import math
import re
import warnings
from fractions import Fraction

import numpy as np
from lm25_common import (
    BP,
    EPS,
    LIMIT_SWITCH,
    RF,
    ROOT,
    TRI,
    A,
    ArmaFit,
    D,
    F,
    N,
    S,
    T,
    adf,
    arma_acf,
    b,
    batch_se,
    contracts,
    dates,
    days_cal,
    db,
    db_free,
    df_null,
    df_reg,
    fair,
    half_life,
    hc0,
    hl_se,
    iD,
    idx,
    kpss_c,
    last,
    lnF,
    lnS,
    med,
    mon,
    n_year,
    noise_split,
    ols,
    pre,
    q5,
    qt,
    r,
    resid,
    rF,
    rho_hat,
    roll,
    rS,
    se_rob,
    sess,
    spurious,
    tau,
    tr,
    tx,
    vol,
    vr_over,
    years,
    yr,
)
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import acf, adfuller, coint, pacf

MD = ROOT / "src" / "lm25.md"
CHARTS = ROOT / "src" / "data"
ANCHORS = ROOT / "plans" / "vol-4-anchors.md"


# ====================================================================== part 1: the anchors
def near(x: float, d: int) -> bool:
    """True when x, printed to d decimals, lies within a tenth of a unit of the d-th decimal of a rounding boundary."""
    y = abs(x) * 10**d
    return abs(y - math.floor(y) - 0.5) < 0.1


def v(x: float, shown: int, *printed: int) -> str:
    flags = [str(d) for d in printed if near(x, d)]
    return f"{x:.{shown}f}" + (f" NEAR({','.join(flags)})" if flags else "")


def sci(x: float, shown: int, printed: int) -> str:
    mant = abs(x) / 10 ** math.floor(math.log10(abs(x)))
    return f"{x:.{shown}e}" + (" NEAR" if near(mant, printed) else "")


OUT: list[str] = []


def put(nn: int, value: str) -> None:
    assert nn == len(OUT) + 1, f"anchor A25-{nn:02d} out of order"
    OUT.append(f"A25-{nn:02d} {value}")


# ---------------------------------------------------------------- data role (01-05)
put(1, f"{N} dates {dates[0]} .. {dates[-1]}; {int(roll.sum())} rolls; {len(set(contracts))} contracts held")
put(2, f"basis changes {len(db)}; TR23 log returns T {T} ({tr['date'][1]!s} .. {dates[-1]})")
put(3, f"days {days_cal}; years {v(years, 7, 6)}; A {v(A, 6, 2)}; a simulated year round(A) = {n_year} sessions")
put(4, f"D: {int(D.sum())} dates {dates[0]} .. {dates[iD[-1]]} ({N - int(D.sum())} later dates hold a contract "
       f"expiring after {dates[-1]})")
vol_med = float(np.quantile(vol, 0.5, method="inverted_cdf"))
put(5, f"near-month volume min {int(vol.min())}, median (inverted_cdf) {vol_med:.0f}, max {int(vol.max())}; "
       f"the two middle values {int(np.sort(vol)[N // 2 - 1])} and {int(np.sort(vol)[N // 2])} (their mean "
       f"{float(np.median(vol)):.1f} is not used)")

# ---------------------------------------------------------------- case (06-14)
put(6, f"S {S[0]:.2f} on {dates[0]} -> {S[-1]:.2f} on {dates[-1]}; ratio {v(S[-1] / S[0], 4, 1)}")
put(7, f"mean {v(BP * b.mean(), 4, 1)} bp; s (divisor {N}) {v(BP * b.std(), 4, 1)} bp")
i_lo, i_hi = int(b.argmin()), int(b.argmax())
put(8, f"min {v(BP * b[i_lo], 2, 0, 1)} bp on {dates[i_lo]}; max {v(BP * b[i_hi], 2, 0, 1)} bp on {dates[i_hi]}")
Ff = [Fraction(str(x)) for x in F]
Sf = [Fraction(str(x)) for x in S]
neg_x = sum(a < c for a, c in zip(Ff, Sf, strict=True))
zero_x = sum(a == c for a, c in zip(Ff, Sf, strict=True))
neg_g = int((b < -EPS).sum())
assert neg_g == neg_x and int((np.abs(b) <= EPS).sum()) == zero_x
put(9, f"F < S on {neg_x} of {N} dates ({v(100 * neg_x / N, 4, 2)}%); F = S on {zero_x}; guard count {neg_g}")
put(10, f"s of rolled changes {v(BP * db.std(), 4, 1, 2)} bp; roll-free {v(BP * db_free.std(), 4, 1)} bp")
rho1_b = rho_hat(b, 1)
c_b, d_b, se_b, t_b, res_b = df_reg(b)
put(11, f"rho_hat_1(b) {v(rho1_b, 5, 3)}; AR(1) by OLS phi_hat {v(1 + d_b, 5, 4)}; half-life "
        f"{v(half_life(1 + d_b), 4, 1, 2)} sessions")
a_ct = adf(lnS, "ct")
a_c = adf(lnS, "c")
put(12, f"ADF ln S 'ct': {v(a_ct[0], 4, 2)}, p {v(a_ct[1], 4, 2)}, {a_ct[2]} lags; 'c' (check, not printed): "
        f"{a_c[0]:.4f}, p {a_c[1]:.4f}, {a_c[2]} lags")
a_b = adf(b, "c")
assert a_b[1] < 1e-14
put(13, f"ADF b 'c': {v(a_b[0], 4, 2)}, p {a_b[1]:.3e} (below 1e-14), {a_b[2]} lags; DF (no lags) t {v(t_b, 4, 2)}")
put(14, f"ln(S_T/S_0) {math.log(S[-1] / S[0]):.4f} (check row)")

# ---------------------------------------------------------------- stationarity (15-16)
parts = []
for lab, msk in (("before", pre), ("from", ~pre)):
    parts.append(f"{lab} {LIMIT_SWITCH} ({int(msk.sum())} dates): mean S {v(float(S[msk].mean()), 1, 0)}, "
                 f"mean b {v(BP * b[msk].mean(), 3, 1)} bp, s(b) {v(BP * b[msk].std(), 3, 1)} bp")
put(15, "; ".join(parts))
put(16, f"random walk sd 1.2%: 25 sessions {1.2 * math.sqrt(25):.1f}%, 100 sessions {1.2 * math.sqrt(100):.1f}%; "
        f"AR(1) phi 0.9: stationary sd {v(1.2 / math.sqrt(1 - 0.81), 4, 3)}%")

# ---------------------------------------------------------------- autocorrelation tests (17-26)
K = 30
rho = np.array([rho_hat(r, k) for k in range(1, K + 1)])
rob = np.array([se_rob(r, k) for k in range(1, K + 1)])
assert np.allclose(rho, acf(r, nlags=K, fft=False)[1:], atol=1e-12)
se_iid = 1 / math.sqrt(T)
put(17, f"rho_hat_1(r) {v(float(rho[0]), 6, 4, 3)}; k=1..5 (printed to 4 dp): "
        + ", ".join(v(float(x), 6, 4) for x in rho[:5]))
put(18, f"iid SE {v(se_iid, 6, 4)} (band +-{v(1.96 * se_iid, 6, 4)}); robust SE k=1 {v(float(rob[0]), 6, 4)}; "
        f"t-stats iid {v(rho[0] / se_iid, 4, 2)}, robust {v(rho[0] / rob[0], 4, 2)}")
out_iid = [k + 1 for k in range(K) if abs(rho[k]) > 1.96 * se_iid]
out_rob = [k + 1 for k in range(K) if abs(rho[k]) > 1.96 * rob[k]]
gap_iid = np.abs(rho) - 1.96 * se_iid
gap_rob = np.abs(rho) - 1.96 * rob
ki, kr = int(np.argmin(np.abs(gap_iid))), int(np.argmin(np.abs(gap_rob)))
put(19, f"k=1..{K}: outside the iid band {len(out_iid)} {out_iid}; outside the robust band {len(out_rob)} {out_rob}; "
        f"expected under the null 0.05 x {K} = {0.05 * K:.1f}; closest to the iid band lag {ki + 1} "
        f"(|rho| {abs(rho[ki]):.7f} against {1.96 * se_iid:.7f}, {gap_iid[ki]:+.2e}); closest to the robust band lag "
        f"{kr + 1} (|rho| {abs(rho[kr]):.7f} against {1.96 * rob[kr]:.7f}, {gap_rob[kr]:+.2e})")
put(20, f"robust SE k=1..{K}: {v(float(rob.min()), 6, 4)} (k={int(rob.argmin()) + 1}) .. "
        f"{v(float(rob.max()), 6, 4)} (k={int(rob.argmax()) + 1})")
lb = acorr_ljungbox(r, lags=[5, 10]).to_numpy()
q10 = T * (T + 2) * sum(rho[k] ** 2 / (T - k - 1) for k in range(10))
q5_ = T * (T + 2) * sum(rho[k] ** 2 / (T - k - 1) for k in range(5))
assert abs(q10 - lb[1, 0]) < 1e-8 and abs(q5_ - lb[0, 0]) < 1e-8
put(21, f"Q_LB(10) {v(q10, 4, 1)}, p {sci(float(lb[1, 1]), 3, 1)} (upper tail of chi2_10); chi2_10 5% point "
        f"{v(float(stats.chi2.isf(0.05, 10)), 4, 2)}")
lb_abs = acorr_ljungbox(np.abs(r), lags=[10]).to_numpy()
rho_abs1 = rho_hat(np.abs(r), 1)
se_abs1 = se_rob(np.abs(r), 1)
put(22, f"|r|: Q_LB(10) {v(float(lb_abs[0, 0]), 2, 0)}; rho_hat_1(|r|) {v(rho_abs1, 5, 3)} (LM17 printed 0.161, "
        f"lm17.md:392), robust SE {v(se_abs1, 6, 4)}, robust t {v(rho_abs1 / se_abs1, 3, 1)}")


def vr_test(m: int) -> tuple[float, float, float]:
    w = 2 * (1 - np.arange(1, m) / m)
    vr = vr_over(r, m)
    v_iid = 2 * (2 * m - 1) * (m - 1) / (3 * m * T)
    assert abs(v_iid - float(w @ w) / T) < 1e-15
    v_rob = float((w**2) @ (rob[: m - 1] ** 2))
    return vr, (vr - 1) / math.sqrt(v_iid), (vr - 1) / math.sqrt(v_rob)


VR = {m: vr_test(m) for m in (2, 5, 10, 20)}
put(23, "; ".join(f"m={m}: VR {v(VR[m][0], 5, 4)}, t iid {v(VR[m][1], 3, 2)}, t robust {v(VR[m][2], 3, 2)}"
                  for m in (2, 5, 10, 20)))
ov = []
gaps = []
for m in (2, 5, 10, 20, 246):
    w = 2 * (1 - np.arange(1, m) / m)
    rho_m = np.array([rho_hat(r, k) for k in range(1, m)])
    vw = 1 + float(w @ rho_m)
    if m <= 20:
        gaps.append(abs(vw - vr_over(r, m)))
    ov.append(f"m={m}: overlapping {vr_over(r, m):.5f}, rho-weighted {vw:.5f}")
put(24, "check row (LM19's identity column; not printed): " + "; ".join(ov)
        + f"; largest gap for m <= 20 {max(gaps):.4f}")
n_tests = K + 1 + 4
put(25, f"tests on TR23 log returns: {K} lags + Ljung-Box + 4 variance ratios = {n_tests}; expected false "
        f"rejections at 5% {0.05 * n_tests:.2f}")
rho4 = [round(float(x), 4) for x in rho[:5]]
rob4 = [round(float(x), 4) for x in rob[:5]]
q5_4 = T * (T + 2) * sum(rho4[k] ** 2 / (T - k - 1) for k in range(5))
put(26, f"Q_LB(5) unrounded {v(q5_, 4, 2)}; rho 1..5 to 4 dp {', '.join(f'{x:.4f}' for x in rho4)}; robust SE "
        f"1..5 to 4 dp {', '.join(f'{x:.4f}' for x in rob4)}; from these 4-dp inputs: Q_LB(5) {v(q5_4, 4, 2, 0)}, "
        f"robust t-stats {', '.join(v(a / c, 4, 2) for a, c in zip(rho4, rob4, strict=True))}; chi2_5 5% point "
        f"{v(float(stats.chi2.isf(0.05, 5)), 4, 2)}")

# ---------------------------------------------------------------- AR and MA models (27-34)
put(27, f"MA(1) theta1 -0.36: rho1 {v(-0.36 / (1 + 0.36**2), 5, 3)}; AR(1) phi1 0.5: half-life "
        f"{half_life(0.5):.0f} session")
s_eps_b = math.sqrt(float(res_b @ res_b) / (len(db) - 2))
put(28, f"AR(1) on b (rolled, {len(db)} changes): c {v(BP * c_b, 4, 2)} bp, phi_hat {v(1 + d_b, 5, 4)}, SE "
        f"{v(se_b, 7, 5)}, s_eps {v(BP * s_eps_b, 3, 1)} bp, half-life "
        f"{v(half_life(1 + d_b), 4, 2)}, mean c/(1-phi) {v(-BP * c_b / d_b, 4, 2)} bp")
acf_b = acf(b, nlags=20, fft=False)[1:]
pacf_b = np.asarray(pacf(b, nlags=20, method="ols"), dtype=float)[1:]
put(29, "acf(b) k=1..10: " + ", ".join(v(float(x), 5, 3) for x in acf_b[:10]) + f"; k=20 {v(float(acf_b[19]), 5, 3)}")
assert float(np.abs(pacf_b[5:]).max()) < 0.07
put(30, "pacf(b) k=1..5: " + ", ".join(v(float(x), 5, 3) for x in pacf_b[:5])
        + f"; max |pacf| k=6..20 {float(np.abs(pacf_b[5:]).max()):.5f} (printed: below 0.07)")
fit_b = ArmaFit(BP * b)
fit_ar1 = ArmaFit(BP * b, (1, 0, 0))
p_b, se_p = fit_b.params, fit_b.bse
put(31, f"ARMA(1,1) on b (bp), maximum likelihood: mean {v(p_b[0], 4, 1)} (SE {v(se_p[0], 4, 1)}), phi1 "
        f"{v(p_b[1], 9, 5)} (SE {v(se_p[1], 7, 4, 6)}), theta1 {v(p_b[2], 6, 3)} (SE {v(se_p[2], 6, 3)}), sigma2 "
        f"{v(p_b[3], 3, 1)} bp^2 (SE {se_p[3]:.2f}); SEs from -l''; llf {fit_b.llf:.4f} (default fit "
        f"{fit_b.llf_default:.4f}); AIC {fit_b.aic:.1f} vs AR(1) {fit_ar1.aic:.1f}")
put(32, "model ACF k=1,2,5,10,20: ARMA "
        + ", ".join(v(arma_acf(p_b[1], p_b[2], k), 5, 4 if k == 1 else 3) for k in (1, 2, 5, 10, 20))
        + "; AR(1) " + ", ".join(v((1 + d_b) ** k, 5, 3) for k in (1, 2, 5, 10, 20))
        + "; sample " + ", ".join(f"{float(acf_b[k - 1]):.5f}" for k in (1, 2, 5, 10, 20)))
put(33, f"half-life at phi1 {p_b[1]:.6f}: {v(half_life(p_b[1]), 4, 1)}; at 0.91: {v(half_life(0.91), 4, 2)}")
put(34, f"AR(1) on r by OLS: phi_hat {v(df_reg(r)[1] + 1, 5, 3)}")

# ---------------------------------------------------------------- unit roots (35-42)
t1, crit1 = df_null(1, N, 10_000)
qs1 = np.quantile(t1, [0.01, 0.05, 0.10], method="inverted_cdf")
bse1 = batch_se(t1, q5)
put(35, f"exp 1, {N} levels, 10,000 walks: quantiles 1% {v(qs1[0], 4, 2)}, 5% {v(qs1[1], 4, 2)} (batch SE "
        f"{v(bse1, 4, 3)}), 10% {v(qs1[2], 4, 2)}; mean {v(float(t1.mean()), 4, 2)}")
n1a, n1b = int((t1 < -1.645).sum()), int((t1 < -1.96).sum())
sh1, sh2 = n1a / 1e4, n1b / 1e4
put(36, f"below -1.645 {n1a} of 10000 = {v(100 * sh1, 2, 1)}% (SE {v(100 * math.sqrt(sh1 * (1 - sh1) / 1e4), 3, 1)}%); "
        f"below -1.96 {n1b} = {v(100 * sh2, 2, 1)}% (SE {100 * math.sqrt(sh2 * (1 - sh2) / 1e4):.2f}%)")
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    a0 = adfuller(b, maxlag=0, autolag=None, regression="c", result_object=True)
cv = a0.critical_values
assert abs(float(a0.statistic) - t_b) < 1e-9
put(37, f"MacKinnon (statsmodels) for {int(a0.nobs)} observations: 1% {v(cv['1%'], 5, 4, 2)}, 5% "
        f"{v(cv['5%'], 5, 4, 2)}, 10% {v(cv['10%'], 5, 4, 2)}; standard normal 5% point "
        f"{v(float(stats.norm.ppf(0.05)), 7, 3)}")
t3, crit3 = df_null(3, n_year, 100_000)
n3 = int((t3 < -1.645).sum())
sh3 = n3 / 1e5
bse3 = batch_se(t3, q5)
put(38, f"exp 3, {n_year} levels, 100,000 walks: 5% {v(q5(t3), 4, 2)} (batch SE {v(bse3, 4, 3)}); "
        f"below -1.645 {n3} of 100000 = {v(100 * sh3, 3, 1)}% (SE {v(100 * math.sqrt(sh3 * (1 - sh3) / 1e5), 3, 2)}%); "
        f"MacKinnon 5% for {n_year - 1} observations {v(crit3, 5, 4, 2)}")
_, d_s, _, t_s, _ = df_reg(lnS)
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    p_s = float(adfuller(lnS, maxlag=0, autolag=None, regression="c", result_object=True).pvalue)
    a_ct0 = adfuller(lnS, maxlag=0, autolag=None, regression="ct", result_object=True)
put(39, f"DF ln S by hand ('c', no lags): t {v(t_s, 4, 2)}, phi_hat {v(1 + d_s, 7, 6)}, p {v(p_s, 4, 3)}; 'ct' no "
        f"lags (check, not printed) t {float(a_ct0.statistic):.4f}, p {float(a_ct0.pvalue):.4f}")
k_s = kpss_c(lnS)
k_b = kpss_c(b)
assert k_s[1] <= 0.01
put(40, f"KPSS ln S {v(k_s[0], 4, 3)} (p {k_s[1]:.3f}, the table's bound, {k_s[2]} lags); KPSS b {v(k_b[0], 4, 3)} "
        f"(p {v(k_b[1], 4, 3)}, {k_b[2]} lags); the table's 5% point 0.463, 1% point 0.739")
max_lag = math.ceil(12 * (len(b) / 100) ** 0.25)
put(41, f"ADF b 'c' {a_b[0]:.3f} with {a_b[2]} lags; statsmodels' default maximum "
        f"{max_lag} (12 x (T/100)^(1/4) rounded up, T = {len(b)})")
put(42, f"DF on b: {t_b:.4f} against the 5% point {cv['5%']:.4f} (check row)")

# ---------------------------------------------------------------- spurious regression, cointegration (43-50)
tt2, r22, first2, paths2 = spurious(2, N, 1000)
n2 = int((np.abs(tt2) > 1.96).sum())
sh = n2 / 1000
put(43, f"exp 2, {N} sessions, 1,000 pairs: |t| > 1.96 in {n2} = {100 * sh:.1f}% (SE "
        f"{v(100 * math.sqrt(sh * (1 - sh) / 1000), 3, 1)}%); median |t| {v(med(np.abs(tt2)), 4, 0)} (batch SE "
        f"{v(batch_se(np.abs(tt2), med), 4, 1)}); median R-squared {v(med(r22), 4, 2)} (batch SE "
        f"{v(batch_se(r22, med), 4, 3)})")
put(44, f"plotted pair: slope {v(first2[0], 4, 2)}, t {v(first2[1], 3, 1)}, R-squared {v(first2[2], 4, 3)}; "
        f"differences: t {v(first2[3], 4, 2)}; ends x {v(float(paths2[0, -1]), 3, 1)}, y {v(float(paths2[1, -1]), 3, 1)}")
tt4, r24, _, _ = spurious(4, n_year, 1000)
n4 = int((np.abs(tt4) > 1.96).sum())
sh4 = n4 / 1000
put(45, f"exp 4, {n_year} sessions, 1,000 pairs: |t| > 1.96 in {n4} = {100 * sh4:.1f}% (SE "
        f"{v(100 * math.sqrt(sh4 * (1 - sh4) / 1000), 3, 1)}%); median |t| {v(med(np.abs(tt4)), 4, 1)} (batch SE "
        f"{v(batch_se(np.abs(tt4), med), 4, 1)}); median R-squared {v(med(r24), 4, 2)} (batch SE "
        f"{v(batch_se(r24, med), 4, 3)})")
beta_eg, se_eg, res_eg = ols(np.column_stack([np.ones(N), lnS]), lnF)
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    cg = coint(lnF, lnS, trend="c", return_results=True)
assert float(cg.pvalue) < 1e-14
put(46, f"EG: ln F = {v(float(beta_eg[0]), 6, 4)} + {v(float(beta_eg[1]), 6, 4)} ln S (classical SE "
        f"{v(float(se_eg[1]), 8, 6)}); coint t {v(float(cg.coint_t), 4, 2)}, p {float(cg.pvalue):.2e} (below 1e-14), "
        f"5% point {v(float(cg.critical_values[1]), 4, 2)}")
Xl = np.column_stack([np.ones(N - 1), b[:-1]])
bFe, seFe, resF = ols(Xl, rF[1:])
bSe, seSe, resS = ols(Xl, rS[1:])
wF, wS = float(hc0(Xl, resF)[1]), float(hc0(Xl, resS)[1])
put(47, f"ECM: alpha_F {v(float(bFe[1]), 5, 3)} (classical {seFe[1]:.4f}, White {v(wF, 5, 3)}); "
        f"alpha_S {v(float(bSe[1]), 6, 4)} (classical {seSe[1]:.4f}, White {v(wS, 5, 3)}); "
        f"alpha_F - alpha_S {bFe[1] - bSe[1]:.5f}")
c_f, d_f, se_f, t_f, _ = df_reg(b, db_free)
assert abs((bFe[1] - bSe[1]) - d_f) < 1e-12
put(48, f"roll-free DF: delta {d_f:.5f}, t {v(t_f, 4, 2)}, phi {v(1 + d_f, 5, 4)}, half-life "
        f"{v(half_life(1 + d_f), 4, 2)}")
jump = (db - db_free)[roll[1:]]
rm = mon[1:][roll[1:]]
put(49, f"roll jumps ({int(roll[1:].sum())}), by the calendar month of the roll date (June: from the June into the "
        f"July contract): mean {v(BP * float(jump.mean()), 3, 1)} bp, s {v(BP * float(jump.std()), 3, 1)}; June "
        f"{v(BP * float(jump[rm == 6].mean()), 4, 1)} (n {int((rm == 6).sum())}), July "
        f"{v(BP * float(jump[rm == 7].mean()), 4, 2)} (n {int((rm == 7).sum())}), other months "
        f"{v(BP * float(jump[(rm != 6) & (rm != 7)].mean()), 4, 1)}")
put(50, f"(beta - 1) / classical SE {v(float((beta_eg[1] - 1) / se_eg[1]), 2, 0)}; residual rho_hat_1 "
        f"{v(rho_hat(res_eg, 1), 5, 3)}")

# ---------------------------------------------------------------- the basis as a time series (51-60)
ex_rows = []
for s_ in (2, 10, 20):
    msk = D & (sess == s_)
    ex_rows.append(f"{s_} sessions (n {int(msk.sum())}): mean b {v(BP * float(b[msk].mean()), 4, 2)}, "
                   f"s {v(BP * float(b[msk].std()), 4, 2, 0)}, mean fair {v(BP * float(fair[msk].mean()), 4, 2)} bp")
put(51, "; ".join(ex_rows) + f"; sessions range {int(sess[D].min())} .. {int(sess[D].max())}; "
        f"at least 200 dates for 2 .. {max(s for s in range(2, 30) if int((D & (sess == s)).sum()) >= 200)}; "
        f"dates per point for 2 .. 20: {min(int((D & (sess == s)).sum()) for s in range(2, 21))} .. "
        f"{max(int((D & (sess == s)).sum()) for s in range(2, 21))}")
put(52, f"on D: mean carry r_f tau {v(BP * float((RF * tau[D]).mean()), 3, 2)} bp, mean q_real tau "
        f"{v(BP * float(qt[D].mean()), 3, 2)} bp, mean fair {v(BP * float(fair[D].mean()), 3, 2)}, mean residual "
        f"{v(BP * float(resid[D].mean()), 3, 2)}, mean b {v(BP * float(b[D].mean()), 3, 2)}")
season = []
SEAS: dict[int, tuple[float, float, float, int]] = {}
for mm in range(1, 13):
    msk = D & (mon == mm)
    SEAS[mm] = (BP * float(b[msk].mean()), BP * float(fair[msk].mean()), BP * float(resid[msk].mean()), int(msk.sum()))
    season.append(f"{mm}: b {v(SEAS[mm][0], 3, 2)} = fair {v(SEAS[mm][1], 3, 2)} + "
                  f"resid {v(SEAS[mm][2], 3, 2)} (n {SEAS[mm][3]})")
put(53, "; ".join(season))
mm_mean = {mm: float(b[D & (mon == mm)].mean()) for mm in range(1, 13)}
bseas = b - np.array([mm_mean[mm] for mm in mon])
versions = (("b", b[D]), ("b - carry", (b - RF * tau)[D]), ("residual", resid[D]), ("b - month mean", bseas[D]))
vt = []
VERS: list[dict[str, float]] = []
for name, x in versions:
    _, dd, _, tdf, _ = df_reg(x)
    aa = adf(x)
    kk = kpss_c(x)
    fv = ArmaFit(BP * x)
    pp = fv.params
    VERS.append({"mean": BP * float(x.mean()), "s": BP * float(x.std()), "df": tdf, "adf": aa[0], "lags": aa[2],
                 "adf_p": aa[1], "kpss": kk[0], "kpss_p": kk[1], "ar": 1 + dd, "arma_phi": float(pp[1]),
                 "arma_theta": float(pp[2])})
    kp = f"p {v(kk[1], 4, 3)}" if kk[1] > 0.01 else f"p {kk[1]:.3f}, the table's bound"
    vt.append(f"{name}: mean {v(BP * float(x.mean()), 3, 1)}, s {v(BP * float(x.std()), 3, 2)}, DF t {v(tdf, 3, 1)}, "
              f"ADF {v(aa[0], 3, 2)} ({aa[2]} lags, p {aa[1]:.1e}), KPSS {v(kk[0], 4, 2)} ({kp}), "
              f"AR phi {v(1 + dd, 5, 4)} (half-life {v(half_life(1 + dd), 4, 2)}), ARMA phi {v(pp[1], 9, 5)} "
              f"theta {v(pp[2], 5, 3)} (half-life {v(half_life(pp[1]), 4, 2)})")
put(54, " | ".join(vt))
su2, sz2, sx2, vdb = noise_split(p_b[1], p_b[2], p_b[3])
put(55, f"sigma_u {v(math.sqrt(su2), 4, 1)} bp; sigma_zeta {v(math.sqrt(sz2), 4, 1)} bp; persistent sd "
        f"{v(math.sqrt(sx2), 4, 1)} bp; model s(change) {v(math.sqrt(vdb), 4, 2)} bp against the sample "
        f"{v(BP * db.std(), 4, 2)}; noise share of Var(change) {v(100 * 2 * su2 / vdb, 3, 0)}%; of Var(level) "
        f"{v(100 * su2 / (sx2 + su2), 3, 1)}%")
stab = []
reg_fits: dict[str, ArmaFit] = {}
REG: dict[str, dict[str, float]] = {}
for lab, msk in (("before", pre), ("from", ~pre)):
    x = b[msk]
    _, dd, _, tdf, _ = df_reg(x)
    reg_fits[lab] = fv = ArmaFit(BP * x)
    pp = fv.params
    u2, _, _, _ = noise_split(pp[1], pp[2], pp[3])
    REG[lab] = {"df": tdf, "phi": float(pp[1]), "su": math.sqrt(u2)}
    stab.append(f"{lab} {LIMIT_SWITCH} ({len(x)}): s(b) {BP * float(x.std()):.2f}, s(change within) "
                f"{BP * float(np.diff(x).std()):.2f}, DF t {tdf:.2f}, AR phi {1 + dd:.4f}, ARMA phi {v(pp[1], 6, 4, 2)} "
                f"theta {v(pp[2], 6, 4)} sigma2 {v(pp[3], 3, 1)}, sigma_u {v(math.sqrt(u2), 4, 2)} bp")
put(56, "; ".join(stab))
m25 = yr == 2025
fit25 = ArmaFit(BP * b[m25])
p25 = fit25.params
u25, _, _, _ = noise_split(p25[1], p25[2], p25[3])
s25 = float(S[m25].mean())
sch25 = BP * float(np.diff(b[m25]).std())
put(57, f"2025 ({int(m25.sum())} dates): ARMA phi {p25[1]:.4f}, theta {p25[2]:.4f}, sigma2 {p25[3]:.1f}; "
        f"sigma_u {v(math.sqrt(u25), 4, 1)} bp; s(change within 2025, {int(m25.sum()) - 1} changes) "
        f"{sch25:.3f} bp; mean S {s25:.2f}")
ym = {y: float(b[yr == y].mean()) for y in range(2003, 2027)}
ylo, yhi = min(ym, key=lambda y: ym[y]), max(ym, key=lambda y: ym[y])
put(58, f"yearly mean b: lowest {ylo} {v(BP * ym[ylo], 3, 0)} bp, highest {yhi} {v(BP * ym[yhi], 3, 0)} bp "
        f"(2026 to {dates[-1]})")
put(59, f"2025 at the mean S {s25:.2f}: s(change) {v(float(np.diff(b[m25]).std()) * s25, 3, 1)} points, sigma_u "
        f"{v(math.sqrt(u25) / BP * s25, 3, 0)} points; LM6 printed 83.4 points (lm06.md:624)")
put(60, f"widget: phi1 0.91, sigma_zeta {v(math.sqrt(sz2), 3, 1)} bp, sigma_u {v(math.sqrt(su2), 3, 0)} bp, mean "
        f"{v(p_b[0], 3, 1)} bp, {n_year} sessions, 5% point {v(crit3, 4, 2)}")

# ---------------------------------------------------------------- problems (61-66)
put(61, f"P1 phi 0.8: rho3 {0.8**3:.3f}, rho1 0.8, pacf3 0; P2 phi 0.9: half-life {v(half_life(0.9), 5, 2)}, "
        f"0.5/(1-phi) {0.5 / 0.1:.1f}, 1/(1-phi) {1 / 0.1:.1f}; P3 theta 0.5: rho1 {0.5 / 1.25:.2f}, theta^2 0.25")
put(62, f"P4 t -2.50 against {cv['5%']:.2f}: rejects at -1.645 and at |t| > 1.96, not at the DF point")
pr = []
P8: dict[str, tuple[float, float, float]] = {}
for lab in ("before", "from"):
    pp = reg_fits[lab].params
    p4 = (round(float(pp[1]), 4), round(float(pp[2]), 4), round(float(pp[3]), 1))
    u2, _, x2, var_ch = noise_split(*p4)
    P8[lab] = (math.sqrt(u2), math.sqrt(x2), 100 * 2 * u2 / var_ch)
    pr.append(f"{lab}: printed ({p4[0]:.4f}, {p4[1]:.4f}, {p4[2]:.1f}) -> sigma_u {v(math.sqrt(u2), 4, 2)} bp, "
              f"persistent sd {v(math.sqrt(x2), 4, 2)}, noise share of Var(change) {v(100 * 2 * u2 / var_ch, 3, 1)}%")
put(63, "P8 " + "; ".join(pr))
put(64, f"P9 DF by hand t {v(t_b, 4, 2)} = adfuller(maxlag=0) {float(a0.statistic):.4f}; roll-free {v(t_f, 4, 2)}; "
        f"half-lives {v(half_life(1 + d_b), 4, 2)}, {v(half_life(1 + d_f), 4, 2)}")
put(65, f"P10 exp 3: 5% {q5(t3):.4f}, MacKinnon {crit3:.4f}; P11 exp 4: share {sh4:.3f}, median R-squared "
        f"{med(r24):.4f} (check row)")
vr5, t5i, t5r = VR[5]
put(66, f"P12 m=5: VR {v(vr5, 5, 4)}, iid t {v(t5i, 3, 2)}, robust t {v(t5r, 3, 2)}")
put(67, "tests on TX23: ln S 3 (ADF 'ct', DF 'c', KPSS) + b 3 (DF, ADF, KPSS) + the roll-free DF 1 + Engle-Granger 1 "
        f"+ error-correction slopes 2 + four versions on D x 3 = 12 + the two regimes' DF 2 = {3 + 3 + 1 + 1 + 2 + 12 + 2}")
hl = half_life(p_b[1])
hse = hl_se(p_b[1], se_p[1])
put(68, f"ARMA half-life {v(hl, 4, 1, 2)} sessions, delta-method SE {v(hse, 4, 2, 3)} (from phi1's SE {se_p[1]:.7f}, "
        f"-l''; from the inputs as printed, phi1 {round(p_b[1], 5):.5f} and SE {round(se_p[1], 6):.6f}: "
        f"{v(hl_se(round(p_b[1], 5), round(se_p[1], 6)), 5, 3)}); 95% interval {v(hl - 1.96 * hse, 4, 2)} .. "
        f"{v(hl + 1.96 * hse, 4, 2)}")
put(69, "withdrawn (cross-check section 8, LM25 Q9: the 10,000-walk run of experiment 3 is not printed)")

# ---------------------------------------------------------------- additions of the revision (70-72)
iso = [dt.date.fromisoformat(d).isocalendar() for d in dates]
week_last: dict[tuple[int, int], int] = {}
for i, c in enumerate(iso):
    week_last[(c[0], c[1])] = i
keep = sorted(set(week_last.values()) | {0, i_lo, i_hi, N - 1})
payload = json.dumps({"x": [dates[i] for i in keep], "S": [round(float(S[i]), 2) for i in keep],
                      "b": [round(float(BP * b[i]), 1) for i in keep]}, separators=(",", ":"))
put(70, f"X1 thinned: {len(week_last)} ISO weeks (last session of each) + first date and the two extremes "
        f"= {len(keep)} dates of {N}; JSON of dates, S (2 dp) and b (1 dp) {len(payload.encode())} bytes")


def shifted(p: np.ndarray, steps: np.ndarray, moves: dict[int, float]) -> np.ndarray:
    q = p.copy()
    for i_, s_ in moves.items():
        q[i_] += s_ * steps[i_]
    return q


def hand_hessian_and_scores(fit: ArmaFit) -> tuple[np.ndarray, np.ndarray]:
    """Central-difference Hessian of the log-likelihood and per-observation scores at the fitted parameters."""
    p = fit.params
    h = 1e-5 * np.maximum(1.0, np.abs(p))
    k = len(p)

    def ll(q: np.ndarray) -> float:
        return float(fit.model.loglike(q))

    H = np.empty((k, k))
    for i_ in range(k):
        for j_ in range(k):
            H[i_, j_] = (ll(shifted(p, h, {i_: 1, j_: 1} if i_ != j_ else {i_: 2}))
                         - ll(shifted(p, h, {i_: 1, j_: -1} if i_ != j_ else {i_: 0}))
                         - ll(shifted(p, h, {i_: -1, j_: 1} if i_ != j_ else {i_: 0}))
                         + ll(shifted(p, h, {i_: -1, j_: -1} if i_ != j_ else {i_: -2}))) / (4 * h[i_] * h[j_])
    Sc = np.column_stack([(np.asarray(fit.model.loglikeobs(shifted(p, h, {i_: 1})))
                           - np.asarray(fit.model.loglikeobs(shifted(p, h, {i_: -1})))) / (2 * h[i_])
                          for i_ in range(k)])
    return H, Sc


Hh, Sc = hand_hessian_and_scores(fit_b)
Hinv = np.linalg.inv(-Hh)
se_hand = np.sqrt(np.diag(Hinv))
assert np.allclose(se_hand, se_p, rtol=1e-3), "-l'' by hand differs from statsmodels' approx"
se_sand_hand = np.sqrt(np.diag(Hinv @ (Sc.T @ Sc) @ Hinv))
se_oim, se_opg, se_sand = fit_b.bse_of("oim"), fit_b.bse_of("opg"), fit_b.bse_of("robust_approx")
assert np.allclose(se_sand_hand, se_sand, rtol=1e-2), "the sandwich by hand differs from statsmodels'"
hse_s = hl_se(p_b[1], se_sand[1])
put(71, f"ARMA(1,1) SEs (mean, phi1, theta1, sigma2): -l'' {', '.join(f'{x:.6g}' for x in se_p)} (hand "
        f"{', '.join(f'{x:.6g}' for x in se_hand)}); Harvey 'oim' {', '.join(f'{x:.6g}' for x in se_oim)} (phi1 "
        f"{v(se_oim[1], 7, 4)}); 'opg' {', '.join(f'{x:.6g}' for x in se_opg)} (phi1 {v(se_opg[1], 7, 5)}); "
        f"sandwich {v(se_sand[1], 6, 4)} for phi1, all "
        f"{', '.join(f'{x:.6g}' for x in se_sand)} (hand {', '.join(f'{x:.6g}' for x in se_sand_hand)}); half-life "
        f"SE with the sandwich {v(hse_s, 4, 2)}, 95% interval {v(hl - 1.96 * hse_s, 4, 2)} .. "
        f"{v(hl + 1.96 * hse_s, 4, 2)}")
cr = r - r.mean()
den = float(cr @ cr) ** 2
xl_rows = []
ratios = []
XL: dict[int, float] = {}
for m in (2, 5, 10, 20):
    w = 2 * (1 - np.arange(1, m) / m)
    M = np.empty((m - 1, m - 1))
    for j in range(1, m):
        for k in range(1, m):
            lag = max(j, k)
            M[j - 1, k - 1] = float((cr[lag:] ** 2 * cr[lag - j:T - j] * cr[lag - k:T - k]).sum()) / den
    assert np.allclose(np.diag(M), rob[: m - 1] ** 2)
    se_full, se_diag = math.sqrt(float(w @ M @ w)), math.sqrt(float((w**2) @ np.diag(M)))
    ratios.append(se_full / se_diag)
    XL[m] = (VR[m][0] - 1) / se_full
    xl_rows.append(f"m={m}: SE {se_diag:.5f} -> {se_full:.5f}, t robust {v(XL[m], 4, 2)}")
put(72, "robust VR SE with the cross-lag terms sum_t c_t^2 c_{t-j} c_{t-k} (j != k) kept: " + "; ".join(xl_rows)
        + f"; largest increase {v(100 * (max(ratios) - 1), 2, 0)}%")


def _anchor_values() -> dict[str, str]:
    rows_: dict[str, str] = {}
    sec = ANCHORS.read_text(encoding="utf-8").split("\n## LM25", 1)[1].split("\n## ", 1)[0]
    for line in sec.splitlines():
        if line.startswith("| A25-"):
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
            rows_[cells[0]] = cells[3].strip("`").replace("\\|", "|")
    return rows_


ANCHOR_ROWS = _anchor_values()
assert len(ANCHOR_ROWS) == 72 == len(OUT), (len(ANCHOR_ROWS), len(OUT))
ANCHOR_DIFFS: list[str] = []
for line in OUT:
    aid, got = line.split(" ", 1)
    if got != ANCHOR_ROWS[aid]:
        ANCHOR_DIFFS.append(f"{aid}: script {got} | anchor {ANCHOR_ROWS[aid]}")
print(f"part 1: {len(OUT)} anchor lines recomputed, {len(OUT) - len(ANCHOR_DIFFS)} identical to the anchor table")


# ====================================================================== part 2: the module's text
def norm_text(s: str) -> str:
    """Module text with TeX thousands separators, escaped percent signs, \\text{} and minus signs made plain."""
    s = s.replace("{,}", ",").replace("\\%", "%").replace("\u2212", "-").replace("\\,", "")
    return re.sub(r"\\text\{\s*([^}]*)\}", r" \1", s)


MD_RAW = MD.read_text(encoding="utf-8")
CHART_TEXT = ""
for p_ in sorted(CHARTS.glob("lm25-*.json")):
    CHART_TEXT += "\n" + json.dumps(json.loads(p_.read_text(encoding="utf-8")), ensure_ascii=False)
TEXT = norm_text(MD_RAW) + "\n" + CHART_TEXT
N_CHECKS = 0
COVERED: set[str] = set()
NEARS: list[str] = []


def in_text(printed: str) -> bool:
    """The printed number appears as a whole number (2.323 is not inside 2.3235, 0.32 not inside 10.32)."""
    return re.search(r"(?<![\d.])" + re.escape(printed) + r"(?![\d])", TEXT) is not None


def tie(value: float, fmt: str) -> bool:
    """True when value lies on a rounding boundary of fmt (a reader rounding by hand could go either way)."""
    m_ = re.search(r"\.(\d+)", fmt)
    d_ = int(m_.group(1)) if m_ else 0
    if fmt.endswith(("e", "g")):
        return False
    scaled = abs(value) * 10**d_ * (100 if "%" in fmt else 1)
    return abs(scaled - math.floor(scaled) - 0.5) < 1e-6


def chk(label: str, value: float, fmt: str, printed: str) -> None:
    global N_CHECKS
    got = format(value, fmt)
    ok = got == printed and in_text(printed) and not tie(value, fmt)
    print(f"CHECK {label}: {got} (printed {printed}) {'ok' if ok else 'MISMATCH'}")
    assert got == printed, (label, got, printed)
    assert not tie(value, fmt), ("rounding tie: print more digits", label, value)
    assert in_text(printed), f"{label}: {printed!r} not found in src/lm25.md or its charts"
    m_ = re.search(r"\.(\d+)f", fmt)
    if m_ and near(value * (100 if "%" in fmt else 1), int(m_.group(1))):
        NEARS.append(f"{label}: {value!r} printed {printed}")
    COVERED.add(printed.lstrip("-+"))
    N_CHECKS += 1


def has(label: str, text: str) -> None:
    global N_CHECKS
    assert text in TEXT, f"{label}: {text!r} not found in src/lm25.md or its charts"
    print(f"CHECK {label}: '{text}' in text ok")
    for num in re.findall(r"\d[\d,]*\.?\d*", text):
        COVERED.add(num.rstrip(".,"))
    N_CHECKS += 1


def hl_of(phi: float) -> float:
    return half_life(phi)


# ---------------------------------------------------------------- front matter, case, notes
chk("S first", S[0], ",.2f", "4,524.87")
chk("S last", S[-1], ",.2f", "49,313.44")
chk("S growth", S[-1] / S[0], ".1f", "10.9")
has("dates", "From 2 January 2003 to 8 October 2026")
chk("mean b", BP * b.mean(), ".1f", "-25.4")
chk("s b", BP * b.std(), ".1f", "58.2")
chk("min b (case)", BP * b[i_lo], ".0f", "-793")
chk("min b (X1)", BP * b[i_lo], ".1f", "-792.9")
chk("max b (case)", BP * b[i_hi], "+.0f", "+248")
chk("max b (X1)", BP * b[i_hi], "+.1f", "+247.8")
assert (dates[i_lo], dates[i_hi]) == ("2008-10-27", "2009-05-05")
has("min date", "27 October 2008")
has("max date", "5 May 2009")
chk("TX fall on 2008-10-27 (%)", 100 * (1 - F[i_lo] / F[i_lo - 1]), ".1f", "7.0")
chk("TAIEX fall on 2008-10-27 (%)", 100 * (1 - S[i_lo] / S[i_lo - 1]), ".1f", "4.6")
chk("F < S count", neg_x, ",", "4,051")
chk("TX23 dates", N, ",", "5,850")
chk("s rolled changes", BP * db.std(), ".1f", "38.9")
chk("rho1 b", rho1_b, ".3f", "0.776")
chk("AR(1) half-life (case)", half_life(1 + d_b), ".1f", "2.7")
chk("X1 dates", len(keep), ",", "1,227")
chk("D dates", int(D.sum()), ",", "5,834")
# D: every date whose held contract's last trading day is a TX23 date; the last, 14 September 2026, holds 202609,
# which expires on 16 September (only 5,814 dates hold a contract that expires by 14 September)
assert dates[iD[-1]] == "2026-09-14" and contracts[iD[-1]] == 202609 and last[iD[-1]] == "2026-09-16"
assert sum(1 for x in last if x <= "2026-09-14") == 5814
has("D end", "to 14 September 2026, whose contract expires within the sample (the last, 202609, on 16 September)")
chk("TR23 T", T, ",", "5,849")
n_tests36 = n_tests + 1                  # Problem 6's Q_LB(5) is a 36th test on TR23's log returns
chk("tests on TR23", n_tests36, "d", "36")
chk("expected false rejections", 0.05 * n_tests36, ".1f", "1.8")
has("Problem 6's test counted", "one of them Problem 6's $Q_{ LB}(5)$")
has("X2 note's count", "36 tests on these returns, one in Problem 6")
has("tests on |r|", "Two are on $\\lvert r_t\\rvert$")
chk("tests on TX23", 3 + 3 + 1 + 1 + 2 + 12 + 2, "d", "24")
chk("neighbouring days (hygiene, TX23)", rho1_b, ".2f", "0.78")
chk("neighbouring days (hygiene, D)", rho_hat(b[D], 1), ".2f", "0.78")

# ---------------------------------------------------------------- section 2
chk("|r| lag 1 (LM19's)", rho_abs1, ".3f", "0.161")
chk("regime dates before", int(pre.sum()), ",", "3,078")
chk("regime dates from", int((~pre).sum()), ",", "2,772")
chk("mean S before", float(S[pre].mean()), ",.0f", "7,302")
chk("mean S from", float(S[~pre].mean()), ",.0f", "16,042")
chk("mean b before", BP * float(b[pre].mean()), ".1f", "-28.6")
chk("mean b from", BP * float(b[~pre].mean()), ".1f", "-21.8")
chk("s b before", BP * float(b[pre].std()), ".1f", "65.7")
chk("s b from", BP * float(b[~pre].std()), ".1f", "48.2")
chk("KC2 25 sessions", 1.2 * math.sqrt(25), ".1f", "6.0")
chk("KC2 100 sessions", 1.2 * math.sqrt(100), ".1f", "12.0")
chk("KC2 1 - 0.81", 1 - 0.9**2, ".2f", "0.19")
chk("KC2 stationary sd", 1.2 / math.sqrt(0.19), ".3f", "2.753")

# ---------------------------------------------------------------- section 3: AR and MA
chk("E4 c", BP * c_b, ".2f", "-5.66")
chk("E4 phi", 1 + d_b, ".4f", "0.7758")
chk("E4 SE", se_b, ".5f", "0.00824")
chk("E4 s_eps", BP * s_eps_b, ".1f", "36.7")
chk("E4 half-life", half_life(1 + d_b), ".2f", "2.73")
chk("E4 half-life from printed 0.7758", half_life(0.7758), ".2f", "2.73")
chk("E4 mean", -BP * c_b / d_b, ".2f", "-25.25")
chk("E4 mean from printed", -5.66 / (1 - 0.7758), ".2f", "-25.25")
chk("pacf 2", float(pacf_b[1]), ".3f", "0.230")
chk("pacf 3", float(pacf_b[2]), ".3f", "0.109")
chk("roll-free phi", 1 + d_f, ".4f", "0.7748")
chk("roll-free half-life", half_life(1 + d_f), ".2f", "2.72")
chk("roll-free half-life from printed", half_life(0.7748), ".2f", "2.72")
for k_, pr_ in ((1, "0.776"), (2, "0.693"), (3, "0.633"), (10, "0.441"), (20, "0.360")):
    chk(f"acf b lag {k_}", float(acf_b[k_ - 1]), ".3f", pr_)
for k_, pr_ in ((1, "0.776"), (2, "0.230"), (3, "0.109"), (4, "0.021"), (5, "0.072")):
    chk(f"pacf b lag {k_}", float(pacf_b[k_ - 1]), ".3f", pr_)
assert float(np.abs(pacf_b[5:]).max()) < 0.07
has("pacf below", "then below 0.07")
for k_, pr_ in ((2, "0.602"), (5, "0.281"), (10, "0.079")):
    chk(f"AR(1) model lag {k_}", (1 + d_b) ** k_, ".3f", pr_)
    chk(f"AR(1) model lag {k_} from printed 0.7758", 0.7758**k_, ".3f", pr_)
for k_, fm, pr_ in ((1, ".4f", "0.7745"), (2, ".3f", "0.702"), (5, ".3f", "0.522"), (10, ".3f", "0.319"),
                    (20, ".3f", "0.119")):
    chk(f"ARMA model lag {k_}", arma_acf(p_b[1], p_b[2], k_), fm, pr_)
chk("ARMA acf lag 1 from printed (0.90620, -0.3553)", arma_acf(0.90620, -0.3553, 1), ".4f", "0.7745")
chk("half-life (pitfall)", half_life(p_b[1]), ".1f", "7.0")
# partial autocorrelation at lag 2 from the normal equations of the two-lag regression (population autocorrelations):
# AR(1) gives (phi1, 0); MA(1), with rho_2 = 0, gives a lag-2 coefficient of -rho_1^2 / (1 - rho_1^2)
for ph_ in (0.8, 0.5, -0.4, 0.7758):
    a_ar = np.linalg.solve(np.array([[1, ph_], [ph_, 1]]), np.array([ph_, ph_**2]))
    assert np.allclose(a_ar, [ph_, 0.0], atol=1e-14)
for th_ in (0.5, -0.36, -0.3553, 0.9):
    r1_ = th_ / (1 + th_**2)
    a_ma = np.linalg.solve(np.array([[1, r1_], [r1_, 1]]), np.array([r1_, 0.0]))
    assert abs(a_ma[1] - (-(r1_**2) / (1 - r1_**2))) < 1e-14 and a_ma[1] != 0
has("MA(1) PACF at lag 2", "a lag-2 coefficient of $-\\rho_1^2/(1-\\rho_1^2)\\ne0$")
chk("KC3 1 + 0.36^2", 1 + 0.36**2, ".4f", "1.1296")
chk("KC3 rho1", -0.36 / 1.1296, ".3f", "-0.319")

# ---------------------------------------------------------------- section 4: tests for autocorrelation
chk("rho1 r", float(rho[0]), ".4f", "0.0393")
chk("SE iid", se_iid, ".6f", "0.013076")
chk("SE iid, four decimals (the 導讀 box)", se_iid, ".4f", "0.0131")
chk("SE rob lag 1", float(rob[0]), ".4f", "0.0205")
chk("t iid", float(rho[0]) / se_iid, ".2f", "3.01")
chk("t iid from printed", 0.0393 / 0.013076, ".2f", "3.01")
chk("t rob", float(rho[0] / rob[0]), ".2f", "1.92")
chk("t rob from printed", 0.0393 / 0.0205, ".2f", "1.92")
assert len(out_iid) == 9 and len(out_rob) == 2
has("E2 exits", "9 values leave the iid band and 2 leave the robust one")
chk("expected exits", 0.05 * K, ".1f", "1.5")
chk("iid band", 1.96 * se_iid, ".4f", "0.0256")
chk("rob SE min", float(rob.min()), ".4f", "0.0151")
chk("rob SE max", float(rob.max()), ".4f", "0.0227")
has("iid exits", "lags " + ", ".join(str(k) for k in out_iid[:-1]) + f" and {out_iid[-1]}")
assert out_rob == [8, 14]
has("robust exits", "Outside the robust band: lags 8 and 14")
assert ki + 1 == 29 and f"{abs(gap_iid[ki]):.0e}" == "2e-05"
has("lag 29 margin", "lag 29 lies inside by $2\\times10^{-5}$")
chk("Q_LB(10)", q10, ".1f", "37.1")
chk("chi2_10 5%", float(stats.chi2.isf(0.05, 10)), ".2f", "18.31")
assert f"{float(lb[1, 1]):.1e}" == "5.4e-05"
has("LB p-value", "$5.4\\times10^{-5}$")
for m_, (pv, pi, prb) in ((2, ("1.0392", "3.00", "1.91")), (5, ("1.0465", "1.62", "1.02")),
                          (10, ("1.0065", "0.15", "0.09")), (20, ("1.0359", "0.55", "0.37"))):
    chk(f"VR({m_})", VR[m_][0], ".4f", pv)
    chk(f"VR({m_}) t iid", VR[m_][1], ".2f", pi)
    chk(f"VR({m_}) t rob", VR[m_][2], ".2f", prb)
chk("cross-lag widening %", 100 * (max(ratios) - 1), ".0f", "25")
for m_, pr_ in ((5, "0.90"), (10, "0.08"), (20, "0.30")):
    chk(f"cross-lag t m={m_}", XL[m_], ".2f", pr_)
chk("|r| Q_LB(10)", float(lb_abs[0, 0]), ",.0f", "1,820")
chk("KC4 |r| robust SE", se_abs1, ".4f", "0.0240")
chk("KC4 |r| robust t", rho_abs1 / se_abs1, ".1f", "6.7")
chk("KC4 |r| robust t from printed", 0.161 / 0.0240, ".1f", "6.7")

# ---------------------------------------------------------------- section 5: unit roots
chk("exp1 1%", qs1[0], ".2f", "-3.44")
chk("exp1 5%", qs1[1], ".2f", "-2.86")
chk("exp1 batch SE", bse1, ".3f", "0.014")
chk("exp1 10%", qs1[2], ".2f", "-2.58")
chk("exp1 mean", float(t1.mean()), ".2f", "-1.54")
chk("MacKinnon 1%", cv["1%"], ".2f", "-3.43")
chk("MacKinnon 5%", cv["5%"], ".2f", "-2.86")
chk("MacKinnon 10%", cv["10%"], ".2f", "-2.57")
assert int(a0.nobs) == 5849
chk("normal 5% point", float(stats.norm.ppf(0.05)), ".3f", "-1.645")
chk("share below -1.645", 100 * sh1, ".1f", "46.7")
chk("its SE", 100 * math.sqrt(sh1 * (1 - sh1) / 1e4), ".1f", "0.5")
chk("share below -1.96", 100 * sh2, ".1f", "30.7")
assert float(t1.min()) > -5.5 and float(t1.max()) < 2.5
chk("ADF max lag", max_lag, "d", "34")
chk("ln S DF t", t_s, ".2f", "1.19")
chk("ln S phi", 1 + d_s, ".6f", "1.000392")
chk("ln S DF p", p_s, ".3f", "0.996")
chk("ln S ADF ct", a_ct[0], ".2f", "-0.77")
chk("ln S ADF ct p", a_ct[1], ".2f", "0.97")
assert a_ct[2] == 32 and a_b[2] == 28
has("ADF ct lags", "32 lags by AIC")
chk("ln S KPSS", k_s[0], ".3f", "10.356")
chk("b DF t", t_b, ".2f", "-27.20")
chk("b ADF", a_b[0], ".2f", "-9.00")
has("ADF b lags", "(28 lags)")
chk("b KPSS", k_b[0], ".3f", "0.664")
chk("b KPSS p", k_b[1], ".3f", "0.017")
assert 0.574 < k_b[0] < 0.739
chk("lowest yearly mean", BP * ym[ylo], ".0f", "-80")
chk("highest yearly mean", BP * ym[yhi], "+.0f", "+34")
assert (ylo, yhi) == (2008, 2026)
has("KPSS table", "(0.347, 0.463, 0.574 and 0.739 at 10%, 5%, 2.5% and 1%)")

# ---------------------------------------------------------------- section 6: spurious regression, cointegration
chk("X5 slope", first2[0], ".2f", "0.61")
chk("X5 t", first2[1], ".1f", "23.5")
chk("X5 R-squared", first2[2], ".3f", "0.086")
chk("X5 differences t", first2[3], ".2f", "-0.98")
chk("X5 end x", float(paths2[0, -1]), ".1f", "62.0")
chk("X5 end y", float(paths2[1, -1]), ".1f", "98.3")
chk("exp2 share", 100 * sh, ".1f", "96.6")
chk("exp2 SE", 100 * math.sqrt(sh * (1 - sh) / 1000), ".1f", "0.6")
chk("exp2 median |t|", med(np.abs(tt2)), ".0f", "36")
chk("exp2 median |t| batch SE", batch_se(np.abs(tt2), med), ".1f", "0.9")
chk("exp2 median R2", med(r22), ".2f", "0.18")
chk("exp2 median R2 batch SE", batch_se(r22, med), ".3f", "0.007")
chk("exp4 share", 100 * sh4, ".1f", "81.7")
chk("exp4 SE", 100 * math.sqrt(sh4 * (1 - sh4) / 1000), ".1f", "1.2")
chk("exp4 median R2", med(r24), ".2f", "0.17")
chk("exp4 median R2 batch SE", batch_se(r24, med), ".3f", "0.011")
chk("EG intercept", float(beta_eg[0]), ".4f", "-0.0283")
chk("EG slope", float(beta_eg[1]), ".4f", "1.0028")
chk("EG slope classical SE", float(se_eg[1]), ".6f", "0.000154")
chk("EG t for beta = 1", float((beta_eg[1] - 1) / se_eg[1]), ".0f", "18")
chk("EG t for beta = 1 from printed", (1.0028 - 1) / 0.000154, ".0f", "18")
chk("coint t", float(cg.coint_t), ".2f", "-9.42")
chk("coint 5% point", float(cg.critical_values[1]), ".2f", "-3.34")
chk("EG residual rho1", rho_hat(res_eg, 1), ".3f", "0.764")
chk("alpha_F", float(bFe[1]), ".4f", "-0.1597")
chk("alpha_F White SE", wF, ".3f", "0.055")
chk("alpha_S", float(bSe[1]), "+.4f", "+0.0655")
chk("alpha_S White SE", wS, ".3f", "0.040")
chk("alpha_F - alpha_S", float(bFe[1] - bSe[1]), ".4f", "-0.2252")
chk("alpha_F - alpha_S from printed", -0.1597 - 0.0655, ".4f", "-0.2252")
chk("roll-free delta", d_f, ".4f", "-0.2252")

# ---------------------------------------------------------------- section 7: the basis
ex_ = {s_: (BP * float(b[D & (sess == s_)].mean()), BP * float(b[D & (sess == s_)].std()),
            BP * float(fair[D & (sess == s_)].mean())) for s_ in range(2, 21)}
chk("X7 20: mean", ex_[20][0], ".2f", "-37.95")
chk("X7 20: s", ex_[20][1], ".2f", "69.17")
chk("X7 20: fair", ex_[20][2], ".2f", "-14.78")
chk("X7 2: mean", ex_[2][0], ".2f", "-6.56")
chk("X7 2: s", ex_[2][1], ".2f", "35.13")
chk("X7 2: s, about", ex_[2][1], ".0f", "35")
chk("X7 2: fair", ex_[2][2], ".2f", "-1.84")
npt = [int((D & (sess == s_)).sum()) for s_ in range(2, 21)]
assert (min(npt), max(npt)) == (235, 285)
has("X7 dates per point", "235 to 285 dates per point")
chk("roll jumps", int(roll[1:].sum()), "d", "285")
chk("roll jump mean", BP * float(jump.mean()), ".1f", "-37.5")
chk("roll jump s", BP * float(jump.std()), ".1f", "58.7")
chk("June roll", -BP * float(jump[rm == 6].mean()), ".1f", "144.7")
chk("July roll", -BP * float(jump[rm == 7].mean()), ".2f", "104.95")
chk("other rolls", -BP * float(jump[(rm != 6) & (rm != 7)].mean()), ".1f", "19.8")
chk("June roll (overview)", BP * float(jump[rm == 6].mean()), ".1f", "-144.7")
# KC of Section 7: the share of a calendar year's dividends (the TR - price log gap from the previous year's last close,
# 2003 from its first date) that went ex in the life of the contract entered at the June and the July roll, 2003-2025
share: dict[int, list[float]] = {6: [], 7: []}
for y_ in range(2003, 2026):
    yi = np.flatnonzero(yr == y_)
    j0 = max(int(yi[0]) - 1, 0)
    gap = math.log(TRI[yi[-1]] / TRI[j0]) - math.log(S[yi[-1]] / S[j0])
    for mm_ in (6, 7):
        (i_r,) = [int(i) for i in yi if roll[i] and mon[i] == mm_]
        j_ = idx[last[i_r]]
        share[mm_].append((math.log(TRI[j_] / TRI[i_r]) - math.log(S[j_] / S[i_r])) / gap)
chk("June roll's share of the year's dividends (%)", 100 * float(np.mean(share[6])), ".0f", "45")
chk("July roll's share of the year's dividends (%)", 100 * float(np.mean(share[7])), ".0f", "39")
# the roll jump split into the change of the fair log basis (carry and dividends: new contract minus the expiring one,
# whose last trading day is the next session) and the residual; rolls whose two contracts expire in the sample
dec = []
for i_r in np.flatnonzero(roll):
    j_new, j_old = idx.get(last[int(i_r)]), int(i_r) + 1
    if j_new is None:
        continue
    tau_old = (dt.date.fromisoformat(dates[j_old]) - dt.date.fromisoformat(dates[i_r])).days / 365.0
    q_old = math.log(TRI[j_old] / TRI[i_r]) - math.log(S[j_old] / S[i_r])
    q_new = math.log(TRI[j_new] / TRI[i_r]) - math.log(S[j_new] / S[i_r])
    jmp = BP * float((db - db_free)[i_r - 1])
    fair_old = BP * (RF * tau_old - q_old)
    dec.append((mon[i_r], jmp, BP * RF * (tau[i_r] - tau_old), -BP * (q_new - q_old), fair_old))
dec_ = np.array(dec)
d_jun, d_oth = dec_[dec_[:, 0] == 6], dec_[(dec_[:, 0] != 6) & (dec_[:, 0] != 7)]
assert abs(d_jun[:, 4].mean()) < 3 and d_jun[:, 4].mean() + d_jun[:, 2:4].sum(axis=1).mean() < -100  # -2.5, -143
resid_oth = d_oth[:, 1] - d_oth[:, 2] - d_oth[:, 3]
assert len(d_oth) == 236 and 15 < d_oth[:, 2].mean() < 18 and resid_oth.mean() < -d_oth[:, 2].mean()
assert abs(d_oth[:, 3].mean()) < d_oth[:, 2].mean()       # dividends matter less than the carry outside June and July
has("KC answer", "on average 45% of a year's dividends went ex in its life, and 39% in the July roll's contract")
for mm, (pb, pf, prs) in ((6, ("-74.80", "-67.43", "-7.37")), (7, ("-70.17", "-65.88", "-4.29"))):
    chk(f"season {mm} b", SEAS[mm][0], ".2f", pb)
    chk(f"season {mm} fair", SEAS[mm][1], ".2f", pf)
    chk(f"season {mm} resid", SEAS[mm][2], ".2f", prs)
    chk(f"season {mm} sum of printed parts", float(pf) + float(prs), ".2f", pb)
chk("D mean b", BP * float(b[D].mean()), ".2f", "-25.57")
chk("D carry", BP * float((RF * tau[D]).mean()), "+.2f", "+9.73")
chk("D dividends", -BP * float(qt[D].mean()), ".2f", "-17.54")
chk("D residual", BP * float(resid[D].mean()), ".2f", "-17.76")
chk("D sum of printed parts", 9.73 - 17.54 - 17.76, ".2f", "-25.57")
ns = [SEAS[mm][3] for mm in range(1, 13)]
assert (min(ns), max(ns)) == (369, 532)
has("X6 per month", "369 to 532 a month")
# X8 table, row by row
X8_ROWS = (
    "| $b_t$ | -25.6 | 58.11 | -27.2 | -9.03 (28) | 0.62 (0.021) | 0.7751 (2.72) | 0.90584, -0.355 (7.01) |",
    "| $b_t-r_f\\tau$ | -35.3 | 59.11 | -27.4 | -9.15 (28) | 0.62 (0.021) | 0.7723 (2.68) | 0.89557, -0.327 (6.28) |",
    "| Residual | -17.8 | 47.67 | -32.3 | -7.75 (33) | 0.77 (<0.01) | 0.6974 (1.92) | 0.89075, -0.414 (5.99) |",
    "| $b_t$ - month mean | 0.0 | 53.24 | -30.3 | -8.51 (28) | 0.96 (<0.01) | 0.7284 (2.19) | 0.87168, -0.323 (5.05) |",
)
for row, vv in zip(X8_ROWS, VERS, strict=True):
    cells = [c.strip() for c in row.strip("|").split(" | ")]
    mean_s = f"{vv['mean']:.1f}".replace("-0.0", "0.0")
    kp = f"{vv['kpss']:.2f} ({vv['kpss_p']:.3f})" if vv["kpss_p"] > 0.01 else f"{vv['kpss']:.2f} (<0.01)"
    got = [mean_s, f"{vv['s']:.2f}", f"{vv['df']:.1f}", f"{vv['adf']:.2f} ({int(vv['lags'])})", kp,
           f"{vv['ar']:.4f} ({half_life(round(vv['ar'], 4)):.2f})",
           f"{vv['arma_phi']:.5f}, {vv['arma_theta']:.3f} ({half_life(round(vv['arma_phi'], 5)):.2f})"]
    assert cells[1:] == got, (cells, got)
    # the half-lives follow from the unrounded coefficients too
    assert f"{half_life(vv['ar']):.2f}" == got[5][-5:-1] and f"{half_life(vv['arma_phi']):.2f}" == got[6][-5:-1]
    has(f"X8 row {cells[0]}", row)
chk("E9 DF max", max(vv["df"] for vv in VERS), ".1f", "-27.2")
chk("E9 DF min", min(vv["df"] for vv in VERS), ".1f", "-32.3")
chk("E9 ADF max", max(vv["adf"] for vv in VERS), ".2f", "-7.75")
chk("E9 ADF min", min(vv["adf"] for vv in VERS), ".2f", "-9.15")
assert all(vv["kpss"] > 0.463 for vv in VERS)
chk("E9 AR half-life min", min(half_life(vv["ar"]) for vv in VERS), ".2f", "1.92")
chk("E9 AR half-life max", max(half_life(vv["ar"]) for vv in VERS), ".2f", "2.72")
chk("E9 ARMA half-life min", min(half_life(vv["arma_phi"]) for vv in VERS), ".2f", "5.05")
chk("E9 ARMA half-life max", max(half_life(vv["arma_phi"]) for vv in VERS), ".2f", "7.01")
# E9: removing slow parts shortens the half-lives by up to 29% (AR(1) 2.72 -> 1.92, the residual; ARMA 7.01 -> 5.05)
short_ar = [1 - half_life(vv["ar"]) / half_life(VERS[0]["ar"]) for vv in VERS[1:]]
short_arma = [1 - half_life(vv["arma_phi"]) / half_life(VERS[0]["arma_phi"]) for vv in VERS[1:]]
assert min(short_ar + short_arma) > 0          # every version reverts faster than b_t itself
chk("E9 largest shortening (%)", 100 * max(short_ar + short_arma), ".0f", "29")
chk("E9 largest shortening from printed (%)", 100 * (1 - 1.92 / 2.72), ".0f", "29")
assert 100 * (1 - 5.05 / 7.01) < 29.5 and max(half_life(vv["arma_phi"]) for vv in VERS) < 7.5
has("E9 shortening", "shortens the half-lives by up to 29%, but every version still reverts within days")
# hygiene note: KPSS's rejections for b_t (TX23 0.017; D 0.021 for b_t and b_t - r_f tau) and alpha_F's t-stat fail
# Bonferroni's correction for the 24 tests on TX23; every DF and ADF verdict lies far from its critical value
bonf = 0.05 / 24
kp_b = [k_b[1], VERS[0]["kpss_p"], VERS[1]["kpss_p"]]
chk("KPSS p-values for b_t, lowest", min(kp_b), ".3f", "0.017")
chk("KPSS p-values for b_t, highest", max(kp_b), ".3f", "0.021")
assert all(0.01 < p_ < 0.05 and p_ > bonf for p_ in kp_b)
t_aF = float(bFe[1]) / wF
chk("alpha_F t-stat (HC0)", t_aF, ".1f", "-2.9")
assert bonf < 2 * stats.norm.sf(abs(t_aF)) < 0.05
df_like = [t_b, a_b[0], t_f] + [vv["df"] for vv in VERS] + [vv["adf"] for vv in VERS] + [REG[k]["df"] for k in REG]
assert max(df_like) < cv["1%"] - 3 and min(t_s, a_ct[0]) > -1 and min(p_s, a_ct[1]) > 0.9
has("hygiene DF verdicts", "Every DF and ADF verdict lies far from its critical value")
has("hygiene KPSS", "KPSS's rejections for $b_t$ (p-values 0.017 to 0.021) and $\\hat\\alpha_F$'s t-stat, -2.9")
chk("X6 neighbouring days on D", rho_hat(b[D], 1), ".3f", "0.775")
chk("KPSS 5% point", 0.463, ".3f", "0.463")
# E10
chk("llf default gap", fit_b.llf - fit_b.llf_default, ".3f", "0.006")
chk("ARMA mean", p_b[0], ".1f", "-25.5")
chk("ARMA mean SE", se_p[0], ".1f", "3.2")
chk("ARMA phi", p_b[1], ".5f", "0.90620")
chk("ARMA phi SE", se_p[1], ".4f", "0.0071")
chk("ARMA phi SE (6 dp)", se_p[1], ".6f", "0.007055")
chk("ARMA theta", p_b[2], ".4f", "-0.3553")
chk("ARMA theta SE", se_p[2], ".3f", "0.017")
chk("ARMA sigma2", p_b[3], ",.1f", "1,257.0")
chk("sigma_u", math.sqrt(su2), ".1f", "22.2")
chk("sigma_zeta", math.sqrt(sz2), ".1f", "22.8")
chk("persistent sd", math.sqrt(sx2), ".1f", "53.8")
chk("noise share of change", 100 * 2 * su2 / vdb, ".0f", "64")
chk("noise share of level", 100 * su2 / (sx2 + su2), ".1f", "14.5")
chk("model s(change)", math.sqrt(vdb), ".2f", "39.11")
chk("sample s(change)", BP * db.std(), ".2f", "38.91")
pu2, pz2, px2, pvd = noise_split(0.90620, -0.3553, 1257.0)          # from the printed estimates
chk("sigma_u from printed", math.sqrt(pu2), ".1f", "22.2")
chk("sigma_zeta from printed", math.sqrt(pz2), ".1f", "22.8")
chk("persistent sd from printed", math.sqrt(px2), ".1f", "53.8")
chk("noise share from printed", 100 * 2 * pu2 / pvd, ".0f", "64")
chk("level share from printed", 100 * pu2 / (px2 + pu2), ".1f", "14.5")
chk("model s(change) from printed", math.sqrt(pvd), ".2f", "39.11")
chk("half-life", hl, ".2f", "7.04")
chk("half-life from printed phi", half_life(0.90620), ".2f", "7.04")
chk("half-life SE", hse, ".3f", "0.556")
chk("half-life SE from printed", hl_se(0.90620, 0.007055), ".3f", "0.556")
chk("interval low", hl - 1.96 * hse, ".2f", "5.95")
chk("interval high", hl + 1.96 * hse, ".2f", "8.13")
chk("interval low from printed", 7.04 - 1.96 * 0.556, ".2f", "5.95")
chk("interval high from printed", 7.04 + 1.96 * 0.556, ".2f", "8.13")
chk("sandwich SE", se_sand[1], ".5f", "0.01462")
hs_p = hl_se(0.90620, 0.01462)
chk("sandwich low", hl - 1.96 * hse_s, ".2f", "4.78")
chk("sandwich high", hl + 1.96 * hse_s, ".2f", "9.30")
chk("sandwich low from printed", 7.04 - 1.96 * hs_p, ".2f", "4.78")
chk("sandwich high from printed", 7.04 + 1.96 * hs_p, ".2f", "9.30")
chk("regime phi before", REG["before"]["phi"], ".2f", "0.90")
chk("regime phi from", REG["from"]["phi"], ".2f", "0.91")
chk("regime sigma_u before", REG["before"]["su"], ".2f", "25.74")
chk("regime sigma_u from", REG["from"]["su"], ".2f", "17.45")
chk("regime DF before", REG["before"]["df"], ".2f", "-20.20")
chk("regime DF from", REG["from"]["df"], ".2f", "-17.88")
chk("2025 sigma_u", math.sqrt(u25), ".1f", "23.4")
chk("2025 mean S", s25, ",.0f", "23,919")
chk("2025 sigma_u points", math.sqrt(u25) / BP * s25, ".0f", "56")
chk("2025 sigma_u points from printed", 23.4 / BP * 23919, ".0f", "56")
chk("2025 changes", int(m25.sum()) - 1, "d", "242")
# measured in index points (not a conversion at the mean close): the changes of F - S within 2025, rolled (the stored
# series) and roll-free (the contract held over the day, F_held), divisor 242
F_held = tx["F_held"].to_numpy()
i25 = np.flatnonzero(m25)
assert np.all(np.diff(i25) == 1) and len(i25) == 243
i25c = i25[1:]
pts_rolled = (F[i25c] - S[i25c]) - (F[i25c - 1] - S[i25c - 1])
pts_free = (F_held[i25c] - F[i25c - 1]) - (S[i25c] - S[i25c - 1])
assert np.allclose(np.log(F_held[i25c] / F[i25c - 1]), rF[i25c])   # F_held is the contract held over the day
assert int(roll[i25c].sum()) == 12
chk("2025 rolled s(change) points", float(pts_rolled.std()), ".1f", "81.4")
chk("2025 roll-free s(change) points", float(pts_free.std()), ".1f", "76.7")
has("2025 measured", "Measured in points, the 242 rolled daily changes within 2025 had a standard deviation of 81.4")
has("LM6's 83.4", "[[LM6]]'s 83.4 used same-contract pairs from April to October only")
# widget
chk("widget sigma_zeta", math.sqrt(sz2), ".1f", "22.8")
chk("widget mean", p_b[0], ".1f", "-25.5")
chk("widget sessions", n_year, "d", "246")
chk("widget MacKinnon 5% (245)", crit3, ".2f", "-2.87")
chk("widget half-life at 0.91", half_life(0.91), ".2f", "7.35")
# Python section
chk("opg SE phi", se_opg[1], ".5f", "0.00385")
chk("oim SE phi", se_oim[1], ".4f", "0.0068")
chk("approx SE phi", se_p[1], ".4f", "0.0071")

# ---------------------------------------------------------------- problems and solutions
chk("P1", 0.8**3, ".3f", "0.512")
chk("P2 B", half_life(0.9), ".2f", "6.58")
chk("P2 A", 0.5 / (1 - 0.9), ".1f", "5.0")
chk("P2 C", 1 / (1 - 0.9), ".0f", "10")
chk("P3 C", 0.5 / 1.25, ".2f", "0.40")
assert -2.86 < -2.50 < -1.645 and abs(-2.50) > 1.96
for i_, pr_ in enumerate(("0.0393", "0.0000", "-0.0031", "-0.0323", "-0.0173")):
    chk(f"P6 rho {i_ + 1}", rho4[i_], ".4f", pr_)
for i_, pr_ in enumerate(("0.0205", "0.0210", "0.0227", "0.0178", "0.0196")):
    chk(f"P6 SE {i_ + 1}", rob4[i_], ".4f", pr_)
chk("P6 Q from printed", q5_4, ".2f", "16.96")
chk("P6 Q unrounded", q5_, ".2f", "16.98")
chk("P6 chi2_5", float(stats.chi2.isf(0.05, 5)), ".2f", "11.07")
for i_, pr_ in enumerate(("1.92", "0.00", "-0.14", "-1.81", "-0.88")):
    chk(f"P6 robust t {i_ + 1}", rho4[i_] / rob4[i_], ".2f", pr_)
chk("P6 SE range low", min(rob4), ".4f", "0.0178")
chk("P6 SE range high", max(rob4), ".4f", "0.0227")
chk("P6 expected false rejections", 0.05 * 5, ".2f", "0.25")
p8b, p8f = P8["before"], P8["from"]
has("P8 inputs before", "$\\hat\\phi_1=0.9035$, $\\hat\\theta_1=-0.3606$, $\\hat\\sigma_\\eta^2=1,659.9$")
has("P8 inputs from", "0.9101, −0.3427, 808.6".replace("\u2212", "-"))
chk("P8 sigma_u before", p8b[0], ".2f", "25.74")
chk("P8 sd before", p8b[1], ".2f", "60.50")
chk("P8 share before", p8b[2], ".1f", "65.2")
chk("P8 sigma_u from", p8f[0], ".2f", "17.45")
chk("P8 sd from", p8f[1], ".2f", "44.95")
chk("P8 share from", p8f[2], ".1f", "62.6")
assert 0.30 < 1 - p8f[0] / p8b[0] < 0.36 and 0.22 < 1 - p8f[1] / p8b[1] < 0.28
has("P8 reading", "The noise fell by about a third and the persistent spread by about a quarter")
chk("P9 roll-free t", t_f, ".2f", "-29.66")
chk("P10 5% point", q5(t3), ".2f", "-2.87")
chk("P10 batch SE", bse3, ".3f", "0.006")
chk("P10 share", 100 * sh3, ".1f", "45.7")
chk("P10 SE", 100 * math.sqrt(sh3 * (1 - sh3) / 1e5), ".2f", "0.16")
chk("P12 VR(5)", vr5, ".4f", "1.0465")
se_i5 = math.sqrt(72 / (15 * 5849))
assert abs(se_i5**2 - 2 * 9 * 4 / (3 * 5 * T)) < 1e-15
chk("P12 SE iid", se_i5, ".5f", "0.02865")
chk("P12 t iid", t5i, ".2f", "1.62")
chk("P12 t iid from printed", 0.0465 / 0.02865, ".2f", "1.62")
w5 = 2 * (1 - np.arange(1, 5) / 5)
se_r5 = math.sqrt(float((w5**2) @ (np.array(rob4[:4]) ** 2)))
chk("P12 SE rob from P6's SEs", se_r5, ".5f", "0.04573")
chk("P12 t rob", t5r, ".2f", "1.02")
chk("P12 t rob from printed", 0.0465 / 0.04573, ".2f", "1.02")

# ---------------------------------------------------------------- structure: labels and citations
md_raw = MD_RAW
ex_labels = re.findall(r"\[!exhibit\][^\n]*\{#([\w-]+)\}", md_raw)
eg_labels = re.findall(r"\[!example\][^\n]*\{#([\w-]+)\}", md_raw)
assert len(ex_labels) == 8 and len(eg_labels) == 10, (ex_labels, eg_labels)
for lab in ex_labels:
    assert f"[[ex:{lab}]]" in md_raw, f"exhibit {lab} is never cited"
for kind, lab in re.findall(r"\[\[(ex|eg):([\w-]+)\]\]", md_raw):
    assert lab in (ex_labels if kind == "ex" else eg_labels), (kind, lab)
tags = re.findall(r"\\tag\{(25\.\d+)\}", md_raw)
assert tags == [f"25.{i}" for i in range(1, 10)], tags
print(f"labels: {len(ex_labels)} exhibits, {len(eg_labels)} examples, every exhibit cited; tags {tags[0]}..{tags[-1]}")

# ====================================================================== report
body = TEXT.split("\n## Glossary", 1)[0]
nums = set(re.findall(r"(?<![\w.])\d+\.\d+|(?<![\w.,])\d{1,3}(?:,\d{3})+", body))
left = sorted(n for n in nums if n not in COVERED)
print(f"\nnumbers with a decimal point or thousands separator not covered by a check ({len(left)}):")
print("   " + " ".join(left))
print(f"\nnear a rounding boundary at the printed precision ({len(NEARS)}):")
for n_ in NEARS:
    print("   ", n_)
print(f"\nanchor differences ({len(ANCHOR_DIFFS)}):")
for a_ in ANCHOR_DIFFS:
    print("   ", a_)
print(f"\nall {N_CHECKS} checks passed")
