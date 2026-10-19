"""LM20 anchors (Estimation Theory and Maximum Likelihood): every number the Stage 1 brief quotes.

Reads TR23 from data/processed/vol3_taiex.parquet (columns date, tr, price, R, Rp; R is the total-return index's
simple daily return, null on the first row; built and checked by data/vol3_series.py), LM4's 0050 sample from
data/processed/etf_daily_returns.parquet (column R_0050: 0050's one-session total returns on the 2,902 common dates
of 0050 and 00631L, built by data/build_series.py) and U28 through data/lm10_series.py (Volume II's sector sample,
repaired by data/vol2_series.py). Run those builders first.

Conventions:
  * TR23: T = 5,849 simple returns R_t from 2003-01-03; log returns r = ln(1 + R); tau = calendar days between the
    first and last close / 365.25 = 23.7645 years; A = T / tau = 246.12. One-day statistics (mean, s, skewness,
    kurtosis, Kelly fraction, Sharpe ratio, the Student-t and Hill fits) use R; sums over days (Merton's m-day sums,
    the calendar years) use r. A year on 2003-2025 is LM17's 246 sessions.
  * Divisors: s, the sample moments m3 and m4, skewness m3/s^3 and kurtosis m4/s^4 divide by T (NumPy ddof=0);
    s_u divides by T - 1 (ddof=1), passed explicitly. A part's, a window's or a simulated sample's statistics divide
    by its own count, and so does a standard deviation across simulated samples or runs.
  * Annualized: mean A*Rbar, volatility sqrt(A)*s, Sharpe ratio sqrt(A)*Rbar/s with r_f = 0 (the last two are LM19's
    point estimates, recomputed); the Kelly fraction f-hat = Rbar/s^2 is daily (LM4's quadratic rule, (4.3) without
    mu^2).
  * Intervals: estimate +- 1.96 standard errors (1.96 as LM4 and LM17 print it); the t interval uses the 97.5%
    quantile of t_{T-1} (scipy.stats.t.ppf) with s_u.
  * Standard errors under iid returns: SE(Rbar) = s/sqrt(T); the delta method with Var(s^2) ~ (m4 - s^4)/T and
    Cov(Rbar, s^2) ~ m3/T ("plug-in"), or with normal moments (m3 = 0, m4 = 3 s^4) where a line says "normal".
  * Student-t maximum likelihood: scipy.stats.t.fit(R) as LM15 ran it, then refined by Nelder-Mead on the returns in
    percent (tolerances 1e-12); standard errors from the inverse of a central-difference Hessian of the negative
    log-likelihood at the refined optimum (steps 1e-4 for nu, 1e-5 for location and scale, in percent), checked
    against steps ten times larger. The profile log-likelihood maximizes over location and scale at each nu.
  * Hill: losses x = -R on the days with R <= -x0 + 1e-12 (the book's guard), k their count, alpha = k / sum
    ln(x / x0), SE alpha / sqrt(k); every count is checked exactly with Fraction on the two-decimal closes.
  * Merton's sums: non-overlapping m-day sums of r from the first return, n_m = T // m of them (the last T mod m
    returns left out).
  * Seeds: each simulated experiment e creates rng = np.random.default_rng([e, 20261011]) once, at its start, and
    never reseeds:
      e = 1 the sampling distributions: 10,000 one-year samples of 246 days, first standard_normal((10000, 246)),
        then standard_t(nu, size=(10000, 246)) with A20-20's refined nu, both scaled to Rbar and s by (15.11);
      e = 2 the coverage table: for T in 5, 10, 30, 100, 246, the normal block (ten chunks standard_normal((10000,
        T))), then the t_3 block (ten chunks zz = standard_normal((10000, T, 4)), each draw zz[..., 0] /
        sqrt(sum(zz[..., 1:]**2, axis=2) / 3) / sqrt(3), a t_3 variable scaled to variance 1, as the widget builds
        it); 100,000 samples per cell;
      e = 3 Problem 11: standard_normal((20000, 5));
      e = 4 twenty further runs of experiment 1's t block (each standard_t(nu, size=(10000, 246)), drawn in turn
        from one generator), whose spread replaces a Monte Carlo standard error for the two standard deviations of
        the t block (their fourth moments are infinite at nu < 4).
    Quantiles of simulated values are F-hat^{-1}(u) (np.quantile(..., method="inverted_cdf"), LM14's quantile
    function); their Monte Carlo standard errors are LM18's batch standard errors (20 equal batches in draw order,
    standard deviation of the 20 batch values with divisor 20, over sqrt(20)). Means and normal-block standard
    deviations use the iid formulas sd/sqrt(n) and sd/sqrt(2n).
  * Rounding flag: v(x, d1, d2, ...) checks x at every precision d the brief prints it with and appends (!) when
    |x 10^d - floor(x 10^d) - 0.5| < 0.1 for any of them (within a tenth of a unit of the last printed digit of a
    rounding boundary). Every printed value goes through v at its printed precision(s); values the brief does not
    print are formatted plainly.

Numbers printed by earlier modules are recomputed here and cited to their owners in the brief (LM4, LM13-LM19).
Prints one line per anchor, "A20-NN <value>", in ID order (a withdrawn anchor keeps its line), and writes nothing.

Run:  PYTHONUTF8=1 uv run python data/vol4_anchors_lm20.py
"""
import sys
from fractions import Fraction
from math import floor, log, sqrt
from pathlib import Path

import numpy as np
import polars as pl
from numpy.typing import NDArray
from scipy import optimize, stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lm10_series import u28

Vec = NDArray[np.float64]
ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
EPS = 1e-12
Z = 1.96
LIMIT_SWITCH = "2015-06-01"
OUT: list[str] = []


def put(n: int, value: str) -> None:
    """Anchor A20-n; IDs are fixed and printed in order."""
    assert n == len(OUT) + 1, (n, len(OUT))
    OUT.append(f"A20-{n:02d} {value}")


def near(x: float, d: int) -> bool:
    scaled = abs(x) * 10**d
    return abs(scaled - floor(scaled) - 0.5) < 0.1


def v(x: float, *printed: int, extra: int = 4) -> str:
    """x with `extra` more decimals than its finest printed form, marked (!) if any printed form is near a boundary."""
    assert printed
    return f"{x:.{max(printed) + extra}f}" + (" (!)" if any(near(x, d) for d in printed) else "")


def moments(x: Vec) -> tuple[float, float, float, float]:
    """Mean, s (divisor n), third and fourth central moments (divisor n)."""
    xc = x - x.mean()
    return float(x.mean()), float(x.std()), float((xc**3).mean()), float((xc**4).mean())


def se_kelly(m: float, s: float, m3: float, m4: float, n: int) -> float:
    return sqrt((1 / s**2 - 2 * m * m3 / s**6 + m**2 * (m4 - s**4) / s**8) / n)


def se_sharpe(m: float, s: float, m3: float, m4: float, n: int) -> float:
    sr = m / s
    return sqrt((1 - sr * m3 / s**3 + sr**2 * (m4 / s**4 - 1) / 4) / n)


# ---------------------------------------------------------------- TR23
df = pl.read_parquet(PROC / "vol3_taiex.parquet").sort("date")
dates_all = [str(d) for d in df["date"].to_list()]
tr = np.asarray(df["tr"].to_numpy(), dtype=np.float64)
R = np.asarray(df["R"].to_numpy()[1:], dtype=np.float64)
dates = dates_all[1:]
assert df["R"][0] is None and len(set(dates_all)) == len(dates_all)
T = len(R)
r = np.log1p(R)
days = (df["date"][-1] - df["date"][0]).days
tau = days / 365.25
A = T / tau
Rb, s, m3, m4 = moments(R)
su = float(R.std(ddof=1))
skew, kurt = m3 / s**3, m4 / s**4
trf = [Fraction(str(x)) for x in tr]
RF = [trf[i] / trf[i - 1] - 1 for i in range(1, len(trf))]


def count_le(x0: str) -> int:
    """Days with R <= -x0, guarded, checked exactly against the two-decimal closes."""
    g = int((R <= -float(x0) + EPS).sum())
    assert g == sum(1 for q in RF if q <= -Fraction(x0)), x0
    return g


# calendar years 2003-2025, 2003 from its first close
year_end: dict[str, int] = {}
for i_, d_ in enumerate(dates_all):
    year_end[d_[:4]] = i_
ann_log, ann_simple = [], []
for y in range(2003, 2026):
    b = 0 if y == 2003 else year_end[str(y - 1)]
    ann_log.append(log(tr[year_end[str(y)]] / tr[b]))
    ann_simple.append(float(trf[year_end[str(y)]] / trf[b] - 1))
la = np.array(ann_log)
n_y = len(la)
sa = float(la.std())
in_win = np.array([d <= "2025-12-31" for d in dates])
r_w = r[in_win]
_, srw, _, m4w = moments(r_w)
kw = m4w / srw**4

# ---------------------------------------------------------------- U28 pair and LM4's 0050
smp = u28()
x1 = smp.X[:, smp.names.index("Semiconductor")]
x2 = smp.X[:, smp.names.index("FinancialInsurance")]
TU = len(x1)
z1 = (x1 - x1.mean()) / x1.std()
z2 = (x2 - x2.mean()) / x2.std()
rho = float((z1 * z2).mean())
etf = pl.read_parquet(PROC / "etf_daily_returns.parquet").sort("date")
R5 = np.asarray(etf["R_0050"].to_numpy(), dtype=np.float64)
assert int(etf["R_0050"].null_count()) == 0
T5 = len(R5)
mu5, s5, m35, m45 = moments(R5)

# ---------------------------------------------------------------- Student-t maximum likelihood (returns in percent)
X100 = 100 * R


def nll(p: Vec, x: Vec = X100) -> float:
    if p[0] <= 0.5 or p[2] <= 0:
        return 1e18
    return float(-stats.t.logpdf(x, p[0], p[1], p[2]).sum())


def hessian(fun, p: Vec, h: Vec) -> Vec:
    k = len(p)
    H = np.zeros((k, k))
    for i in range(k):
        for j in range(k):
            ei, ej = np.zeros(k), np.zeros(k)
            ei[i], ej[j] = h[i], h[j]
            H[i, j] = (fun(p + ei + ej) - fun(p + ei - ej) - fun(p - ei + ej) + fun(p - ei - ej)) / (4 * h[i] * h[j])
    return H


def tfit(x: Vec) -> tuple[Vec, Vec, float, Vec]:
    """(refined parameters, covariance from the observed information, maximal log-likelihood, t.fit's answer)."""
    raw = np.array([float(q) for q in stats.t.fit(x / 100)]) * np.array([1.0, 100.0, 100.0])
    res = optimize.minimize(lambda p: nll(p, x), raw, method="Nelder-Mead",
                            options={"xatol": 1e-12, "fatol": 1e-12, "maxiter": 40000, "maxfev": 80000})
    p = np.asarray(res.x, dtype=np.float64)
    assert res.fun <= nll(raw, x) + 1e-9
    covs = []
    for scale in (1.0, 10.0):
        H = hessian(lambda q: nll(q, x), p, scale * np.array([1e-4, 1e-5, 1e-5]))
        covs.append(np.linalg.inv(H))
    se0, se1 = np.sqrt(np.diag(covs[0])), np.sqrt(np.diag(covs[1]))
    assert np.all(np.abs(se0 / se1 - 1) < 1e-4), (se0, se1)
    return p, covs[0], -float(res.fun), raw


p_t, cov_t, ll_t, raw_t = tfit(X100)
se_t = np.sqrt(np.diag(cov_t))
nu_t, loc_t, sc_t = (float(q) for q in p_t)
ll_n = float(stats.norm.logpdf(X100, X100.mean(), X100.std()).sum())


def profile(nu: float) -> float:
    res = optimize.minimize(lambda q: nll(np.array([nu, q[0], q[1]])), np.array([loc_t, sc_t]),
                            method="Nelder-Mead", options={"xatol": 1e-11, "fatol": 1e-11, "maxiter": 20000})
    return -float(res.fun) - ll_t


drop = Z**2 / 2
lr_lo = float(optimize.brentq(lambda q: profile(q) + drop, 2.5, nu_t))
lr_hi = float(optimize.brentq(lambda q: profile(q) + drop, nu_t, 4.0))

# ---------------------------------------------------------------- data role
put(1, f"closes {len(dates_all)}; T {T}; returns {dates[0]} .. {dates[-1]}")
put(2, f"days {days}; tau {v(tau, 4, 2, 1, extra=2)} years; A {v(A, 2)}")
put(3, f"Rbar {v(100 * Rb, 6, 4)}%; s {v(100 * s, 6, 4)}%; s_u {v(100 * su, 6, 4)}%; s_u/s {v(su / s, 7)}")  # LM14's
put(4, f"T {TU}; returns {smp.dates[0]} .. {smp.dates[-1]}; A {v(smp.A, 2)}; rho Semiconductor-FinancialInsurance "
    f"{v(rho, 4, extra=6)}")                                                                        # LM16's
put(5, f"T {T5}; {etf['date'][0]} .. {etf['date'][-1]}; mean {v(100 * mu5, 4, extra=6)}%; "
    f"s {v(100 * s5, 4, extra=6)}%")                                                                # LM4's
put(6, f"n {n_y}; mean {v(float(la.mean()), 5)}; sd (divisor 23) {v(100 * sa, 3, 2)}%; daily model on 2003-2025 "
    f"({len(r_w)} returns): sqrt(246) s_r {v(100 * sqrt(246) * srw, 3, 2)}%")                     # LM15's, LM17's
# ---------------------------------------------------------------- motivating case
i08, i09 = 2008 - 2003, 2009 - 2003
put(7, f"2008 {v(100 * ann_simple[i08], 2)}%; 2009 {v(100 * ann_simple[i09], 2)}%; lowest and highest of the 23 "
    f"years {100 * min(ann_simple):.4f}%, {100 * max(ann_simple):.4f}%")                          # LM14's
put(8, f"A Rbar {v(100 * A * Rb, 2)}%; sqrt(A) s {v(100 * sqrt(A) * s, 2)}%")                     # LM19's 18.96%
se_ann = sqrt(A) * s / sqrt(tau)
put(9, f"SE(A Rbar) = sqrt(A) s / sqrt(tau) = A s / sqrt(T) = {v(100 * se_ann, 2)} points; interval "
    f"{v(100 * (A * Rb - Z * se_ann), 1)}% to {v(100 * (A * Rb + Z * se_ann), 1)}%")
se_vol_k = sqrt(A) * s * sqrt((kurt - 1) / (4 * T))
se_vol_n = sqrt(A) * s / sqrt(2 * T)
put(10, f"SE(sqrt(A) s): plug-in kurtosis {v(100 * se_vol_k, 2)} points; normal {v(100 * se_vol_n, 3, 2)} points; "
    f"interval (plug-in) {v(100 * (sqrt(A) * s - Z * se_vol_k), 1)}% to {v(100 * (sqrt(A) * s + Z * se_vol_k), 1)}%")
kelly = Rb / s**2
put(11, f"f-hat = Rbar/s^2 {v(kelly, 2)}; (4.3) with mu^2, Rbar/(s^2 + Rbar^2) {kelly * s**2 / (s**2 + Rb**2):.6f}")
# ---------------------------------------------------------------- sections
sr = Rb / s
put(12, "eta* = T SR^2 / (1 + T SR^2), SR = Rbar/s: T=246: T SR^2 "
    f"{v(246 * sr**2, 3)}, eta* {v(246 * sr**2 / (1 + 246 * sr**2), 3)}; T={T}: T SR^2 {v(T * sr**2, 2)}, "
    f"eta* {v(T * sr**2 / (1 + T * sr**2), 3)}")
put(13, f"s/sqrt(T) {v(100 * s / sqrt(T), 5)}% a day")                                            # LM18's 0.01580%
put(14, f"(1.96 sqrt(A) s / 1 point)^2 = {v((Z * 100 * sqrt(A) * s) ** 2, 0)} years")
put(15, f"23 values: E[s^2]/sigma^2 = 22/23 = {v(22 / 23, 4)}; s_u/s = sqrt(23/22) = {v(sqrt(23 / 22), 4)}; "
    f"s_u of the annual log returns {v(100 * float(la.std(ddof=1)), 3)}%")
put(16, f"t_{{{T - 1}}} 97.5% quantile {v(float(stats.t.ppf(0.975, T - 1)), 5)}; Phi^-1(0.975) "
    f"{v(float(stats.norm.ppf(0.975)), 5)}")
# coverage, experiment 2: 100,000 samples per cell, drawn in chunks of 10,000 (the same stream as one block)
rng2 = np.random.default_rng([2, 20261011])
n_cov, chunk = 100_000, 10_000
cov_rows = []
for Tc in (5, 10, 30, 100, 246):
    q = float(stats.t.ppf(0.975, Tc - 1))
    exact_z = 2 * float(stats.t.cdf(Z * sqrt((Tc - 1) / Tc), Tc - 1)) - 1
    for model in ("normal", "t3"):
        hit_z = hit_t = 0
        for _ in range(n_cov // chunk):
            if model == "normal":
                xs = rng2.standard_normal((chunk, Tc))
            else:
                zz = rng2.standard_normal((chunk, Tc, 4))
                xs = zz[..., 0] / np.sqrt((zz[..., 1:] ** 2).sum(axis=2) / 3) / sqrt(3)
            mean_ = xs.mean(axis=1)
            hit_z += int((np.abs(mean_) <= Z * xs.std(axis=1) / sqrt(Tc)).sum())
            hit_t += int((np.abs(mean_) <= q * xs.std(axis=1, ddof=1) / sqrt(Tc)).sum())
        cz, ct = hit_z / n_cov, hit_t / n_cov
        ex = f" (exact {v(100 * exact_z, 1, extra=4)}%, 95%)" if model == "normal" else ""
        cov_rows.append(f"T={Tc} {model}: z(s) {v(100 * cz, 1, extra=2)}%, t(s_u) {v(100 * ct, 1, extra=2)}%{ex}")
put(17, f"n {n_cov} per cell, MC SE at 95% {v(100 * sqrt(0.95 * 0.05 / n_cov), 2)} points; " + "; ".join(cov_rows))
half_1y = Z * sqrt(A) * s * sqrt(A / 246)
put(18, f"T=246: SE of A x mean {v(100 * sqrt(A) * s * sqrt(A / 246), 2)} points; half-width "
    f"{v(100 * half_1y, 1)} points")
put(19, f"loglik t minus normal (returns in percent) {v(ll_t - ll_n, 1)}")
put(20, f"t.fit nu {v(float(raw_t[0]), 5, extra=1)}; refined nu {v(nu_t, 5, 3, extra=2)} (SE {v(se_t[0], 3)}), "
    f"location {v(loc_t, 4)}% (SE {v(se_t[1], 4)}), scale {v(sc_t, 4)}% (SE {v(se_t[2], 4)})")     # LM15's fit
gsd = np.array([sc_t * 0.5 * sqrt((nu_t - 2) / nu_t) * (-2 / (nu_t - 2) ** 2), 0.0, sqrt(nu_t / (nu_t - 2))])
sd_t = sc_t * sqrt(nu_t / (nu_t - 2))
put(21, f"fit's standard deviation {v(sd_t, 3)}% (SE {v(sqrt(float(gsd @ cov_t @ gsd)), 3)}); s {v(100 * s, 4)}%")
cor_t = cov_t / np.outer(se_t, se_t)
put(22, f"correlation of the estimates: nu-scale {v(float(cor_t[0, 2]), 2)}; nu-location {cor_t[0, 1]:.6f}; "
    f"location-scale {cor_t[1, 2]:.6f}")
put(23, f"profile drop 1.96^2/2 = {drop:.4f}: nu {v(lr_lo, 2)} to {v(lr_hi, 2)}; Wald nu +- 1.96 SE "
    f"{v(nu_t - Z * se_t[0], 2)} to {v(nu_t + Z * se_t[0], 2)}")
put(24, f"normal model: SE(Rbar) = s/sqrt(T) {v(100 * s / sqrt(T), 4)}%; SE(sigma hat) = s/sqrt(2T) "
    f"{v(100 * s / sqrt(2 * T), 4)}%")
put(25, f"t location SE {v(se_t[1], 4)}% against s/sqrt(T) {v(100 * s / sqrt(T), 4)}%; ratio "
    f"{v(se_t[1] / (100 * s / sqrt(T)), 2)}")
pre = np.array([d < LIMIT_SWITCH for d in dates])
reg = []
reg_fit = {}
for lab, x in (("before", X100[pre]), ("from", X100[~pre])):
    pp, cc, _, _ = tfit(x)
    ss = np.sqrt(np.diag(cc))
    reg_fit[lab] = (float(pp[0]), float(ss[0]))
    reg.append(f"{lab} {LIMIT_SWITCH} ({len(x)}): nu {v(float(pp[0]), 3)} (SE {v(float(ss[0]), 3)}), "
               f"location {pp[1]:.4f}%, scale {pp[2]:.4f}%")
put(26, "; ".join(reg))                                                                             # LM15's nu
put(27, f"skewness {v(skew, 2)}; kurtosis {v(kurt, 2)} (excess {v(kurt - 3, 2)})")                # LM14's
se_k = se_kelly(Rb, s, m3, m4, T)
se_k_mean = 1 / (s * sqrt(T))
se_k_norm = se_kelly(Rb, s, 0.0, 3 * s**4, T)
put(28, f"SE(f-hat): mean only 1/(s sqrt T) {v(se_k_mean, 3, 2)}; normal {v(se_k_norm, 3)}; plug-in {v(se_k, 3, 2)}; "
    f"interval {v(kelly - Z * se_k, 2)} to {v(kelly + Z * se_k, 2)}")
se_s = se_sharpe(Rb, s, m3, m4, T)
se_s_norm = sqrt((1 + sr**2 / 2) / T)
put(29, f"daily SR {v(sr, 4)}; SE plug-in {v(se_s, 4)}, normal {v(se_s_norm, 4)}; annual SR {v(sqrt(A) * sr, 2)}, "
    f"SE plug-in {v(sqrt(A) * se_s, 3, 2)}, normal {v(sqrt(A) * se_s_norm, 3)}, interval "
    f"{v(sqrt(A) * (sr - Z * se_s), 2)} to {v(sqrt(A) * (sr + Z * se_s), 2)}; 1/sqrt(tau) {v(1 / sqrt(tau), 3)}")
k5 = mu5 / s5**2
se5 = se_kelly(mu5, s5, m35, m45, T5)
se5m = 1 / (s5 * sqrt(T5))
put(30, f"0050 mean/s^2 {v(k5, 2)}; mean only SE {v(se5m, 2)}, band {v(k5 - Z * se5m, 2)} to {v(k5 + Z * se5m, 2)}; "
    f"plug-in SE {v(se5, 2)}, interval {v(k5 - Z * se5, 2)} to {v(k5 + Z * se5, 2)}; skewness "
    f"{v(m35 / s5**3, 2)}, kurtosis {v(m45 / s5**4, 2)}; SE(mean) {v(100 * s5 / sqrt(T5), 4)}%")     # LM4's band
se_a = sa / sqrt(2 * n_y)
se_daily = sqrt(246) * srw * sqrt((kw - 1) / (4 * len(r_w)))
put(31, f"annual sd {v(100 * sa, 3)}%, SE s/sqrt(2n) {v(100 * se_a, 2)} points, interval {v(100 * (sa - Z * se_a), 1)}% "
    f"to {v(100 * (sa + Z * se_a), 1)}%; daily-based {v(100 * sqrt(246) * srw, 3)}% (SE plug-in "
    f"{v(100 * se_daily, 2)}); gap {v(100 * (sa - sqrt(246) * srw), 1)} points = "
    f"{v((sa - sqrt(246) * srw) / se_a, 1)} SE")
c_lo, c_hi = stats.chi2.ppf(0.025, n_y - 1), stats.chi2.ppf(0.975, n_y - 1)
put(32, f"withdrawn (X32: the chi-square interval stays out until its source is read; not printed); recomputed for "
    f"reference: chi2_22 quantiles {c_lo:.4f}, {c_hi:.4f}; interval for sigma {100 * sa * sqrt(n_y / c_hi):.5f}% to "
    f"{100 * sa * sqrt(n_y / c_lo):.5f}%")


def hill(x0: str) -> tuple[int, float, float]:
    k = count_le(x0)
    xs_ = -R[R <= -float(x0) + EPS]
    a = k / float(np.log(xs_ / float(x0)).sum())
    return k, a, a / sqrt(k)


k3, a3, e3 = hill("0.03")
put(33, f"x0 3%: k {k3}; alpha {v(a3, 2)}; SE {v(e3, 2)}; interval {v(a3 - Z * e3, 1)} to {v(a3 + Z * e3, 1)}")
hl = []
for x0 in ("0.02", "0.04", "0.05"):
    kk, aa, ee = hill(x0)
    iv = f"interval {v(aa - Z * ee, 1)} to {v(aa + Z * ee, 1)}" if x0 != "0.05" else \
        f"interval width {v(2 * Z * ee, 1)}"
    hl.append(f"x0 {float(x0):.0%}: k {kk}, alpha {v(aa, 2)}, SE {v(ee, 2)}, {iv}")
put(34, "; ".join(hl))
# ---------------------------------------------------------------- exhibits: X2 (experiment 1)
rng1 = np.random.default_rng([1, 20261011])
n_sim, T1, n_b = 10_000, 246, 20
t_scale = sqrt((nu_t - 2) / nu_t)
sims = {"normal": Rb + s * rng1.standard_normal((n_sim, T1))}
sims["t"] = Rb + s * t_scale * rng1.standard_t(nu_t, size=(n_sim, T1))
U3 = (0.025, 0.5, 0.975)


def qinv(x: Vec, u: float) -> float:
    """F-hat^{-1}(u), LM14's quantile function."""
    return float(np.quantile(x, u, method="inverted_cdf"))


def batch_se(x: Vec, u: float) -> float:
    """LM18's batch standard error of a quantile: 20 equal batches in draw order, sd (divisor 20) / sqrt(20)."""
    qb = np.array([qinv(b_, u) for b_ in x.reshape(n_b, -1)])
    return float(qb.std()) / sqrt(n_b)


x2l = []
for lab, xs in sims.items():
    am = A * xs.mean(axis=1)
    av = sqrt(A) * xs.std(axis=1)
    sd_am, sd_av = float(am.std()), float(av.std())
    qs = ", ".join(v(100 * qinv(av, u), 1) for u in U3)
    qse = ", ".join(v(100 * batch_se(av, u), 2, 1, extra=2) for u in U3)
    if lab == "normal":
        sd_txt = (f"sd {v(100 * sd_am, 1)} (MC SE {v(100 * sd_am / sqrt(2 * n_sim), 2, extra=2)})",
                  f"sd {v(100 * sd_av, 2)} (MC SE {v(100 * sd_av / sqrt(2 * n_sim), 3, extra=2)})")
    else:
        sd_txt = (f"sd {v(100 * sd_am, 1)} (no MC SE: spread over runs, A20-51)",
                  f"sd {v(100 * sd_av, 0, extra=5)} (no MC SE: spread over runs, A20-51)")
    x2l.append(f"{lab}: A x mean: mean {100 * am.mean():.3f}% (MC SE {100 * sd_am / sqrt(n_sim):.3f}), {sd_txt[0]}; "
               f"volatility: mean {100 * av.mean():.3f}%, {sd_txt[1]}, 2.5/50/97.5% (inverted_cdf) {qs} "
               f"(batch SE {qse})")
put(35, f"n {n_sim} samples of {T1} days; nu {nu_t:.6f}; " + "; ".join(x2l) + "; theory (normal): sd of A x mean "
    f"{v(100 * sqrt(A) * s * sqrt(A / T1), 2)}, sd of volatility {v(100 * sqrt(A) * s / sqrt(2 * T1), 3)}")
# X3 (Merton)
_, s_r, _, _ = moments(r)
mer = []
for m in (1, 2, 5, 10, 21, 62, 123, 246):
    nm = T // m
    sums = r[: nm * m].reshape(nm, m).sum(axis=1)
    _, s_m, _, m4_m = moments(sums)
    se_mean_m = A / m * s_m / sqrt(nm)
    se_vol_m = sqrt(A / m) * s_m * sqrt((m4_m / s_m**4 - 1) / (4 * nm))
    model_vol = sqrt(A) * s_r / sqrt(2 * nm)
    mer.append(f"m={m} (n={nm}): mean SE {v(100 * se_mean_m, 2, extra=2)}, vol SE {v(100 * se_vol_m, 2, extra=2)}, "
               f"normal model vol SE {v(100 * model_vol, 2, extra=2)}")
put(36, f"model mean SE sqrt(A) s_r / sqrt(tau) {v(100 * sqrt(A) * s_r / sqrt(tau), 2)}; " + "; ".join(mer))
put(37, "A Rbar +- 1.96 sqrt(A) s / sqrt(years): " + "; ".join(
    f"{y} years: {v(100 * (A * Rb - Z * sqrt(A) * s / sqrt(y)), 1)}% to {v(100 * (A * Rb + Z * sqrt(A) * s / sqrt(y)), 1)}%"
    for y in (1, 10, 100)))
# ---------------------------------------------------------------- widget
put(38, "t_{T-1} 97.5% quantiles: " + ", ".join(
    f"T={n}: {v(float(stats.t.ppf(0.975, n - 1)), 4, extra=2)}" for n in (5, 10, 20, 30, 100, 250)))
# ---------------------------------------------------------------- examples and problems
reg_s = []
for lab, x in (("before", R[pre]), ("from", R[~pre])):
    _, sx, _, m4x = moments(x)
    reg_s.append(f"{lab} {LIMIT_SWITCH} ({len(x)}): s {v(100 * sx, 3)}%, SE plug-in "
                 f"{v(100 * sx * sqrt((m4x / sx**4 - 1) / (4 * len(x))), 3)}, normal {100 * sx / sqrt(2 * len(x)):.4f}")
put(39, "; ".join(reg_s))
put(40, f"P1: 20/sqrt(10) {v(20 / sqrt(10), 2)}; /sqrt(54) {v(20 / sqrt(10) / sqrt(54), 2)}; 20/sqrt(2461) "
    f"{v(20 / sqrt(2461), 2)}")
put(41, f"P2: 23/22 - 1 {v(100 * (23 / 22 - 1), 1)}%; sqrt(23/22) - 1 {v(100 * (sqrt(23 / 22) - 1), 1)}%")
put(42, f"P5: normal {v(100 * se_vol_n, 2)}; plug-in {v(100 * se_vol_k, 2)}; without the 2 {v(100 * sqrt(A) * s / sqrt(T), 2)}")
L_t = z1 * z2 - rho / 2 * (z1**2 + z2**2)
se_rn = (1 - rho**2) / sqrt(TU)
se_rm = float(L_t.std()) / sqrt(TU)
put(43, f"P6: rho {v(rho, 4)}; normal SE {v(se_rn, 4)}, interval {v(rho - Z * se_rn, 3)} to {v(rho + Z * se_rn, 3)}; "
    f"plug-in SE {v(se_rm, 4)}, interval {v(rho - Z * se_rm, 3)} to {v(rho + Z * se_rm, 3)}; ratio {v(se_rm / se_rn, 2)}")
dnu = reg_fit["from"][0] - reg_fit["before"][0]
sed = sqrt(reg_fit["from"][1] ** 2 + reg_fit["before"][1] ** 2)
put(44, f"P7: difference {v(dnu, 3)}; SE of the difference {v(sed, 3)}; ratio {v(dnu / sed, 1)}")
months = sorted({d[:7] for d in dates})
cnt = np.array([sum(1 for d, q in zip(dates, RF) if d[:7] == mo and (q <= Fraction("-0.03") or q >= Fraction("0.03")))
                for mo in months], dtype=np.float64)
cnt_g = np.array([int(((np.array([d[:7] == mo for d in dates])) & ((R <= -0.03 + EPS) | (R >= 0.03 - EPS))).sum())
                  for mo in months], dtype=np.float64)
assert np.array_equal(cnt, cnt_g)
lam = float(cnt.mean())
put(45, f"P8: months {len(months)} (zero counts included: {int((cnt == 0).sum())}); total {int(cnt.sum())}; lambda "
    f"{v(lam, 5)}; Poisson SE sqrt(lambda/n) {v(sqrt(lam / len(months)), 5)}; variance/mean (divisor n) "
    f"{v(float(cnt.var()) / lam, 4, 2)}; SE sd/sqrt(n) {v(float(cnt.std()) / sqrt(len(months)), 4)}; ratio "
    f"{v(float(cnt.std()) / sqrt(lam), 3)}")
up = int((R > EPS).sum())
assert up == sum(1 for q in RF if q > 0)
ph = up / T
se_p = sqrt(ph * (1 - ph) / T)
put(46, f"P9: up {up}; theta-hat {v(ph, 4)}; SE {v(se_p, 4)}; interval {v(ph - Z * se_p, 3)} to {v(ph + Z * se_p, 3)}")
rng3 = np.random.default_rng([3, 20261011])
n3 = 20_000
xs3 = rng3.standard_normal((n3, 5))
c3z = float((np.abs(xs3.mean(axis=1)) <= Z * xs3.std(axis=1) / sqrt(5)).mean())
c3t = float((np.abs(xs3.mean(axis=1)) <= stats.t.ppf(0.975, 4) * xs3.std(axis=1, ddof=1) / sqrt(5)).mean())
ez5 = 2 * float(stats.t.cdf(Z * sqrt(4 / 5), 4)) - 1
put(47, f"P11: n {n3}, T 5, normal: z(s) {v(100 * c3z, 1, extra=2)}%, t(s_u) {v(100 * c3t, 1, extra=2)}%; MC SE "
    f"{v(100 * sqrt(c3z * (1 - c3z) / n3), 2)} and {v(100 * sqrt(c3t * (1 - c3t) / n3), 2)} points; exact z(s) "
    f"2 F_t4(1.96 sqrt(4/5)) - 1 = {v(100 * ez5, 1, extra=4)}% (1.96 sqrt(4/5) = {Z * sqrt(4 / 5):.6f})")
sr_d = 0.5 / sqrt(A)
put(48, f"P12: daily SR {sr_d:.6f}; years for SE 0.1: {v((1 + sr_d**2 / 2) / 0.1**2, 0, extra=2)}; 1/0.1 = 10; "
    f"1.96^2/0.1^2 = {v(Z**2 / 0.1**2, 0, extra=2)}")
put(49, f"KC 2: sqrt(3/246) {v(sqrt(3 / 246), 3)} against daily SR {v(sr, 4)}")
put(50, f"KC 3: sqrt(A) s / sqrt(3) {v(100 * sqrt(A) * s / sqrt(3), 1)} points; / sqrt(10) "
    f"{v(100 * sqrt(A) * s / sqrt(10), 1)} points")
# ---------------------------------------------------------------- experiment 4: spread of experiment 1's t block
rng4 = np.random.default_rng([4, 20261011])
n_runs = 20
run_am, run_av = [], []
for _ in range(n_runs):
    xs = Rb + s * t_scale * rng4.standard_t(nu_t, size=(n_sim, T1))
    run_am.append(float((A * xs.mean(axis=1)).std()))
    run_av.append(float((sqrt(A) * xs.std(axis=1)).std()))
ra, rv = 100 * np.array(run_am), 100 * np.array(run_av)
put(51, f"{n_runs} runs of {n_sim} t samples of {T1} days: sd of A x mean: mean over runs {v(float(ra.mean()), 1)}, "
    f"spread (sd across runs, divisor {n_runs}) {v(float(ra.std()), 2)}, range {v(float(ra.min()), 1)} to "
    f"{v(float(ra.max()), 1)}; sd of volatility: mean over runs {v(float(rv.mean()), 1)}, spread {v(float(rv.std()), 2)}, "
    f"range {v(float(rv.min()), 1)} to {v(float(rv.max()), 1)}")

print("\n".join(OUT))
