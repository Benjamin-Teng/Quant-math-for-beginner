"""LM24 anchors (Bayesian Inference and Shrinkage): every number the Stage 1 brief quotes.

Reads two samples and writes nothing:
  * TR23 from data/processed/vol3_taiex.parquet (columns date, tr, price, R, Rp; R is the total-return index's simple
    daily return, null on the first row; built and checked by data/vol3_series.py, which must run first): 5,850
    closes 2003-01-02 -> 2026-10-08, T = 5,849 returns from 2003-01-03, years = calendar days / 365.25 = 23.76,
    A = T / years = 246.12.
  * U28 from data/lm10_series.py's u28() (it reads data/processed/vol2_closes.parquet, built and repaired by
    data/vol2_series.py): the 28 leaf TWSE sector *price* indices (no dividends), simple returns between consecutive
    closes 2008-12-01 -> 2026-10-08, T = 4,382 returns from 2008-12-02, A = 245.4794 (U28's, used for both halves).
    LM11's halves: the first 2,191 returns (2008-12-02 -> 2017-10-06) and the last 2,191 (2017-10-11 -> 2026-10-08).
    The samples are never mixed in one statistic.

Conventions (plans/vol-4.md, "Shared decisions" and "Editor's decisions on the LM19-LM25 drafts"; AUTHORING section 6):
  * Return type: one-day statistics on simple returns R; LM24 sums no returns over days.
  * Owners: TR23's A Rbar and sqrt(A) s are LM19's; s / sqrt(T), the confidence interval, fhat = Rbar / s^2 and its
    delta-method errors are LM20's; the t-stat (21.1), with s_u, and its p-value (21.2) are LM21's; fhat* = 4.1381 is
    LM17's. They are recomputed here and cited to their owners in the text.
  * Divisors: s and each sector's s_i divide by the number of returns used (T, or 2,191 in a half): NumPy ddof=0,
    passed explicitly; s_u (LM21's t-stat) divides by T - 1 (ddof=1). The cross-sectional SD of the 28 sector means
    divides by 28. The James-Stein sum of squared deviations has no divisor. Anchor "ddof" shows what ddof=1 changes.
  * Annualization: a daily mean times A, a daily SD times sqrt(A); "points" are percentage points a year.
  * Every interval, credible or confidence, uses z = Phi^{-1}(0.975) = 1.959964 (printed 1.96, lm15.md:194).
  * Normal model with known variance: sigma = s (divisor T); SE(Rbar) = s / sqrt(T) (LM20's (20.2)); prior
    mu ~ N(mu0, sigma0^2), centred at zero unless stated; the data's weight c = sigma0^2 / (sigma0^2 + s^2 / T);
    posterior mean mu0 + c (Rbar - mu0), posterior SD sqrt(c) s / sqrt(T). "A sigma0 = 10 points" is a prior SD of
    10 percentage points on the annualized mean A mu. A prior worth n0 = s^2 / sigma0^2 returns (n0 / A years) gives
    c = T / (T + n0).
  * Kelly: r_f = 0. fhat = Rbar / s^2 (LM20's symbol); the Bayes fraction in the stated model (GBM with known sigma,
    normal prior, log utility) is f_B = E[mu | data] / s^2, which is c fhat for a prior centred at zero. "Exact"
    fractions are roots of (4.5): they maximize the mean of ln(1 + f x_t) over x_t = R_t - Rbar + m, TR23's returns
    shifted by one constant so that their mean is the posterior mean m (LM4's band method, lm04.md:543-551), solved
    by brentq; at m = Rbar the root is fhat* (LM17's 4.1381). The posterior-integrated fraction maximizes over f the
    expectation, over mu ~ N(c Rbar, c s^2 / T), of the mean over t of ln(1 + f (R_t - Rbar + mu)), the expectation
    by 60-node Gauss-Hermite quadrature (numpy.polynomial.hermite_e.hermegauss, weights normalized to sum 1).
    Expected growth in the model: A (f E[mu | data] - f^2 s^2 / 2), a year.
  * Beta-binomial: integer Beta parameters, so every probability is exact with Fraction through
    Pr(Beta(a, b) <= x) = Pr(Bin(a + b - 1, x) >= a), and checked against scipy.stats.beta. The sceptic's prior is
    Beta(82, 82), whose share of theta >= 0.55 is closest to LM13's 10% among integer a (anchor "beta_prior").
  * James-Stein (positive part, toward the grand mean): c_hat = max(0, 1 - (N - 3) v / sum_i (m_i - mbar)^2), with
    v the average over the N sectors of s_i^2 / T (one common noise variance, an approximation). "Common removed"
    replaces each day's 28 returns by their deviations from that day's cross-sectional mean; Problem 11 subtracts the
    TAIEX price index's return instead.
  * Out-of-sample error: root mean square over the 28 sectors of (estimate from one half - mean of the other half),
    annualized; "deviations" removes each half's own grand mean first.
  * Counts: LM24 counts no returns against a threshold. Its two counts compare means (the sectors on the same side of
    the grand mean in both halves; the first-half intervals that exclude the grand mean) and use the book's guard
    (>= x - 1e-12, <= -x + 1e-12); the script asserts that no compared quantity lies within 1e-12 of its edge.
  * Simulation (AUTHORING section 8): each experiment creates rng = np.random.default_rng([e, 20261011]) once, at its
    start, e its number in the brief. Experiment 1 (Example E6): one 10,000 x 28 array of true means
    (standard_normal), then one 10,000 x 28 array of noise. Experiment 2 (Problem 10): for each spread 0, 1, 3 in
    that order, from one generator, one 20,000 x 28 array of true means drawn as spread * standard_normal (drawn
    even at spread 0, so the draws are used up), then one 20,000 x 28 array of noise. A Monte Carlo average is printed
    with its standard error: the SD of the per-cross-section values with divisor n, over sqrt(n).
  * Rounding: v() prints a value with three digits more than its most precise printed form and flags it,
    "[near a / b]", at every precision in which the brief prints it, when it lies within a tenth of a printed unit of
    a rounding boundary; sig() does the same in significant figures, mc() for a Monte Carlo mean and its SE.

Prints one line per anchor, "A24-NN <value>", in ID order (ORDER: the brief's order of first appearance for A24-01 to
A24-60, then the anchors added at the revision of 2026-10-19), and writes nothing.

Run:  PYTHONUTF8=1 uv run python data/vol4_anchors_lm24.py [repository root]
"""
import math
import sys
from fractions import Fraction
from math import comb, sqrt
from pathlib import Path

import numpy as np
import polars as pl
from numpy.typing import NDArray
from scipy import optimize, stats

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "data"))
from lm10_series import u28

PROC = ROOT / "data" / "processed"
SEED = 20261011
EPS = 1e-12
Z975 = float(stats.norm.ppf(0.975))
Vec = NDArray[np.float64]
VAL: dict[str, str] = {}

ORDER = [
    "closes", "t_count", "years_a", "rbar_s", "u28", "halves", "auto", "ship", "corr", "grand", "rmse", "tr_annual",
    "fhat", "sig_c", "beta_prior", "post_half", "js_common", "kc_beta", "years09", "table_flat", "kc_js", "agree",
    "mu0_8", "ddof", "semis", "beta_post", "beta_flat", "table_a", "table_b", "table_c", "z975", "forest_hw",
    "forest_excl", "reverse", "gaps", "kelly10", "widget", "months", "post10", "worth", "tv_check", "exp1", "theory",
    "js_raw", "fwd_opt", "spread2", "kelly_sd", "growth10", "growth_sc", "p1", "p2", "p3", "p4", "p5", "p6", "p9",
    "exp2", "p11", "p12", "thirds",
    "eta",  # A24-61, added at the revision of 2026-10-19
]


def put(key: str, value: str) -> None:
    assert key not in VAL, key
    VAL[key] = value


def rng(e: int) -> np.random.Generator:
    """The generator of experiment e (AUTHORING section 8: the experiment number first, then the root seed)."""
    return np.random.default_rng([e, SEED])


def flag(y: float, d: int) -> str:
    """' [near lo / hi]' when y, printed with d decimals, lies within a tenth of a printed unit of a boundary."""
    scaled = y * 10**d
    frac = scaled - math.floor(scaled)
    if abs(frac - 0.5) >= 0.1:
        return ""
    lo, hi = math.floor(scaled) / 10**d, (math.floor(scaled) + 1) / 10**d
    return f" [near {lo:.{max(d, 0)}f} / {hi:.{max(d, 0)}f}]"


def v(x: float, *ds: int, pct: bool = False, extra: int = 3) -> str:
    """x with max(ds) + extra decimals, flagged at each precision in ds (every form in which the brief prints it)."""
    y = 100 * x if pct else x
    out = f"{y:.{max(ds) + extra}f}" + ("%" if pct else "")
    return out + "".join(flag(y, d) for d in sorted(set(ds), reverse=True))


def sig(x: float, *ns: int) -> str:
    """x in scientific notation with max(ns) + 2 significant figures, flagged at each n significant figures in ns."""
    e = math.floor(math.log10(abs(x)))
    m = x / 10**e
    return f"{m:.{max(ns) + 1}f}e{e:+d}" + "".join(flag(m, n - 1) for n in sorted(set(ns), reverse=True))


def mc(e: Vec, d: int = 1, dse: int = 2) -> str:
    """Monte Carlo mean (printed with d decimals) and its SE (dse decimals): SD with divisor n over sqrt(n)."""
    m, se_ = float(e.mean()), float(e.std(ddof=0)) / sqrt(len(e))
    return f"{v(m, d, extra=2)} (SE {v(se_, dse, extra=2)})"


def beta_cdf(a: int, b: int, x: Fraction) -> Fraction:
    """Pr(Beta(a, b) <= x) for integer a, b: the probability of at least a successes in a + b - 1 trials."""
    n = a + b - 1
    return sum((comb(n, k) * x**k * (1 - x) ** (n - k) for k in range(a, n + 1)), Fraction(0))


def beta_sf(a: int, b: int, x: Fraction) -> Fraction:
    p = 1 - beta_cdf(a, b, x)
    assert abs(float(p) - float(stats.beta.sf(float(x), a, b))) < 1e-12
    return p


# ---------------------------------------------------------------- TR23
df = pl.read_parquet(PROC / "vol3_taiex.parquet").sort("date")
dates_all = [str(d) for d in df["date"].to_list()]
assert df["R"][0] is None and len(set(dates_all)) == len(dates_all)
R = np.asarray(df["R"].to_numpy()[1:], dtype=np.float64)
T = len(R)
days = (df["date"][-1] - df["date"][0]).days
years = days / 365.25
A = T / years
Rb = float(R.mean())
s = float(R.std(ddof=0))
s_u = float(R.std(ddof=1))
se = s / sqrt(T)
fhat = Rb / s**2
vol = s * sqrt(A)


def weight(a_sigma0: float) -> float:
    """The data's weight c for a prior SD a_sigma0 (annual, as a fraction) on A mu."""
    s0 = a_sigma0 / A
    return s0**2 / (s0**2 + se**2)


def post(c: float, a_mu0: float = 0.0) -> tuple[float, float]:
    """Posterior mean and SD of the daily mu for the data's weight c and a prior centred at a_mu0 (annual)."""
    mu0 = a_mu0 / A
    return mu0 + c * (Rb - mu0), sqrt(c) * se


def kelly_exact(mean_target: float) -> float:
    """Root of (4.5) on TR23's returns shifted so that their mean is mean_target (LM4's band method)."""
    x = R - Rb + mean_target

    def d(f: float) -> float:
        return float((x / (1 + f * x)).mean())

    return float(optimize.brentq(d, 1e-6, 1 / abs(float(x.min())) - 1e-6))


XG, WG = np.polynomial.hermite_e.hermegauss(60)
WG = WG / WG.sum()


def kelly_bayes_quad(c: float) -> float:
    """Maximizer of the posterior expectation of the empirical growth, mu ~ N(c Rbar, c se^2), by quadrature."""
    m, sd = post(c)
    shifts = m + sd * XG - Rb

    def d(f: float) -> float:
        tot = 0.0
        for w, sh in zip(WG, shifts):
            x = R + sh
            tot += float(w) * float((x / (1 + f * x)).mean())
        return tot

    return float(optimize.brentq(d, 1e-6, 8.0))


def growth(f: float, m: float) -> float:
    """Posterior-expected annual log growth of the fixed fraction f in the model (GBM), posterior mean m per day."""
    return A * (f * m - f**2 * s**2 / 2)


f_star = kelly_exact(Rb)
c10 = weight(0.10)
pm10, psd10 = post(c10)
sig_q, sig_h = A * se / sqrt(3), A * se

# ---------------------------------------------------------------- U28 and LM11's halves
smp = u28()
X = np.asarray(smp.X, dtype=np.float64)
names = smp.names
A28 = float(smp.A)
T28, N = X.shape
h = T28 // 2
assert (T28, N, h) == (4382, 28, 2191)
assert (smp.dates[0], smp.dates[h - 1], smp.dates[h], smp.dates[-1]) == (
    "2008-12-02", "2017-10-06", "2017-10-11", "2026-10-08")
Xd = X - X.mean(axis=1, keepdims=True)                     # common component (cross-sectional mean) removed
Xe = X - np.asarray(smp.taiex, dtype=np.float64)[:, None]  # TAIEX removed (Problem 11)


def js(x_est: Vec, ddof: int = 0) -> tuple[float, float, float, float]:
    """Annual noise SD of a mean; annual cross-sectional SD (divisor N) of the means; 1 - c_hat; c_hat."""
    n = x_est.shape[0]
    m = x_est.mean(axis=0)
    noise = float((x_est.var(axis=0, ddof=ddof) / n).mean())
    ss = float(((m - m.mean()) ** 2).sum())
    b = (N - 3) * noise / ss
    return A28 * sqrt(noise), A28 * float(m.std(ddof=0)), b, max(0.0, 1 - b)


def oos(m_est: Vec, m_judge: Vec, c: float, deviations: bool = False) -> float:
    """Annualized root mean square error of the shrunk estimate against the other half's means."""
    est = m_est.mean() + c * (m_est - m_est.mean())
    if deviations:
        return A28 * sqrt(float((((est - m_est.mean()) - (m_judge - m_judge.mean())) ** 2).mean()))
    return A28 * sqrt(float(((est - m_judge) ** 2).mean()))


def c_opt(m_est: Vec, m_judge: Vec) -> float:
    d1, d2 = m_est - m_est.mean(), m_judge - m_judge.mean()
    return float(d1 @ d2 / (d1 @ d1))


m1, m2 = X[:h].mean(axis=0), X[h:].mean(axis=0)
a1, a2 = A28 * m1, A28 * m2
rank1 = {names[i]: int((a1 > a1[i]).sum()) + 1 for i in range(N)}
rank2 = {names[i]: int((a2 > a2[i]).sum()) + 1 for i in range(N)}


def sector(name: str) -> str:
    i = names.index(name)
    return f"{name} {v(float(a1[i]), 2, pct=True)} (rank {rank1[name]}) -> {v(float(a2[i]), 2, pct=True)} (rank {rank2[name]})"


# ================================================================ data role
put("closes", f"{len(dates_all)} closes {dates_all[0]} -> {dates_all[-1]}")
put("t_count", f"{T} returns {dates_all[1]} -> {dates_all[-1]}")
put("years_a", f"days {days}; years {v(years, 2, 1)}; A {v(A, 2)}")
put("rbar_s", f"Rbar {v(Rb, 4, pct=True)}; s {v(s, 4, pct=True)} (divisor T; lm14.md:240-241 prints 0.0625%, 1.2084%)")
put("u28", f"T {T28}; N {N}; {smp.dates[0]} -> {smp.dates[-1]}; years {smp.years:.6f}; A {v(A28, 4)}")
put("halves", f"{h} + {T28 - h}: {smp.dates[0]} -> {smp.dates[h - 1]}; {smp.dates[h]} -> {smp.dates[-1]}")

# ================================================================ case (U28 halves, price indices)
put("auto", sector("Automobile"))
put("ship", sector("ShippingTransportation"))
corr = float(np.corrcoef(a1, a2)[0, 1])
put("corr", f"Pearson {v(corr, 2)} (Spearman {float(stats.spearmanr(a1, a2).statistic):.5f}, not printed)")
put("grand", f"grand means {v(float(a1.mean()), 2, pct=True)}; {v(float(a2.mean()), 2, pct=True)}")
put("rmse", f"c=1 (own means) {v(oos(m1, m2, 1.0), 1, pct=True)}; c=0 (grand mean) {v(oos(m1, m2, 0.0), 1, pct=True)}")
put("tr_annual", f"A Rbar {v(A * Rb, 2, 1, pct=True)} (LM19's); sqrt(A) s {v(vol, 2, pct=True)} (LM19's); SE A s/sqrt(T) "
    f"{v(A * se, 2, pct=True)} (LM20's); t-stat with s_u {v(Rb / (s_u / sqrt(T)), 2, extra=4)} (LM21's (21.1)); "
    f"with s {v(Rb / se, 2, extra=4)}; years {v(years, 1)}")
put("fhat", f"plug-in Rbar/s^2 {v(fhat, 2)} (LM20's)")
put("sig_c", f"A sigma0 = SE/sqrt(3) for c = 1/4: {v(sig_q, 2, pct=True)} (from printed 3.89: {v(3.89 / sqrt(3), 2, extra=3)}; "
    f"from 3.9: {v(3.9 / sqrt(3), 2, extra=3)}); = SE for c = 1/2: {v(sig_h, 2, pct=True)}")

# ================================================================ sections, knowledge checks
a_exact = float(optimize.brentq(lambda a: float(stats.beta.sf(0.55, a, a)) - 0.10, 1.0, 1000.0))
P55 = Fraction(11, 20)
pr_prior = beta_sf(82, 82, P55)
near_int = min(range(70, 95), key=lambda a: abs(float(stats.beta.sf(0.55, a, a)) - 0.10))
assert near_int == 82
put("beta_prior", f"a solving Pr(theta>=0.55)=0.10 for Beta(a,a): {v(a_exact, 2, extra=2)}; Beta(82,82): Pr "
    f"{v(float(pr_prior), 1, pct=True)}, SD {v(float(stats.beta.std(82, 82)), 3)}; n0 = 164 months")
pm_h, psd_h = post(0.5)
put("post_half", f"c = 1/2: prior SD = SE {v(A * se, 2, pct=True)}; posterior mean {v(A * pm_h, 2, pct=True)}; "
    f"SD {v(A * psd_h, 2, pct=True)} (from printed 3.89/sqrt(2) = {3.89 / sqrt(2):.4f}, 15.38/2 = 7.69)")
nz_d, _, b_d, c_d = js(Xd[:h])
put("js_common", f"common removed, first half: noise {v(nz_d, 1, pct=True)}; 1 - c_hat {v(b_d, 2)}; c_hat {c_d:g}")
put("kc_beta", f"Beta(2,2), 3 of 4 -> Beta(5,3): mean {Fraction(5, 8)} = {v(5 / 8, 3)}; c {Fraction(4, 8)}")
n0_10 = s**2 / (0.10 / A) ** 2
put("years09", f"A sigma0 = 10 worth {v(n0_10 / A, 2)} years; c = 0.9 needs 9 x that = {v(9 * n0_10 / A, 1)} years "
    f"(from printed 3.59: {9 * 3.59:.2f})")
km = np.array([1.0, 2.0, 3.0, 6.0])
kss = float(((km - km.mean()) ** 2).sum())
kc = 1 - (4 - 3) * 1.0 / kss
assert Fraction(kc).limit_denominator(100) == Fraction(13, 14)
put("kc_js", f"means 1,2,3,6, noise 1: grand {km.mean():g}; sum {kss:g}; c_hat 13/14 = {kc:.6f}; estimates "
    f"8/7, 29/14, 3, 81/14 = {', '.join(v(float(km.mean() + kc * (x - km.mean())), 2) for x in km)}")
dev1, dev2 = m1 - m1.mean(), m2 - m2.mean()
assert np.all(np.abs(dev1) > EPS) and np.all(np.abs(dev2) > EPS)
agree = int(((dev1 >= EPS) & (dev2 >= EPS)).sum() + ((dev1 <= -EPS) & (dev2 <= -EPS)).sum())
put("agree", f"same side of the grand mean in both halves: {agree} of {N} (independent halves: {N / 2:g} expected)")
c_h = 0.5
pm8, _ = post(c_h, 0.08)
fb8 = pm8 / s**2
put("mu0_8", f"prior centred at 8% a year, A sigma0 = SE (c = 1/2): posterior mean {v(A * pm8, 2, pct=True)}; "
    f"Bayes fraction {v(fb8, 2)}; ratio to fhat {v(fb8 / fhat, 2)}; c fhat {v(0.5 * fhat, 2)}")
_, _, b_d1, _ = js(Xd[:h], ddof=1)
put("ddof", f"common removed, 1 - c_hat with ddof=1 {v(b_d1, 3)} against ddof=0 {v(b_d, 3)} (factor 2191/2190)")

# ================================================================ exhibits
put("semis", f"{sector('Semiconductor')}; {sector('ElectronicPartsComponents')}")
pr_post = beta_sf(90, 86, P55)
put("beta_post", f"Beta(90,86): mean {Fraction(90, 176)} = {v(90 / 176, 4)} (shift {v(90 / 176 - 0.5, 4)}); c "
    f"{Fraction(12, 176)} = {v(12 / 176, 3)} = {v(12 / 176, 1, pct=True)}; Pr(theta>=0.55) "
    f"{v(float(pr_post), 1, pct=True)} exact; LM13 13.5% (lm13.md:334)")
pr_flat_half = beta_sf(9, 5, Fraction(1, 2))
pr_flat_55 = beta_sf(9, 5, P55)
assert pr_flat_half == Fraction(7099, 8192)
put("beta_flat", f"Beta(9,5): mean {Fraction(9, 14)} = {v(9 / 14, 3)}; c {Fraction(12, 14)} = {12 / 14:.5f}; "
    f"Pr(theta>0.5) {pr_flat_half} = {v(float(pr_flat_half), 1, pct=True)}; Pr(theta>=0.55) "
    f"{v(float(pr_flat_55), 1, pct=True)}; 95% {v(float(stats.beta.ppf(0.025, 9, 5)), 2)} to "
    f"{v(float(stats.beta.ppf(0.975, 9, 5)), 2)}")


def row(c: float, s0: float, dw: int) -> str:
    """One row of X4; dw is the number of decimals the row prints for the prior's worth in years."""
    m, sd = post(c)
    lo, hi = A * (m - Z975 * sd), A * (m + Z975 * sd)
    worth = (vol / s0) ** 2 if math.isfinite(s0) else 0.0
    s0_txt = v(s0, 2, pct=True) if math.isfinite(s0) else "inf"
    return (f"A sigma0 {s0_txt}; worth {v(worth, dw)} years; c {v(c, 3, 2)}; mean {v(A * m, 1, pct=True)}; 95% "
            f"{v(lo, 1, pct=True)} to {v(hi, 1, pct=True)}; Pr(mu<=0) {sig(float(stats.norm.cdf(-m / sd)), 2)}; "
            f"Bayes fraction {v(c * fhat, 2)}")


put("table_a", "c = 1/4: " + row(0.25, sig_q, 1))
put("table_b", "c = 1/2: " + row(0.5, sig_h, 1))
put("table_c", "A sigma0 = 10: " + row(c10, 0.10, 2))
t_u = Rb / (s_u / sqrt(T))
put("table_flat", "flat: " + row(1.0, math.inf, 0) + f"; LM21's one-sided p-value Phi(-{t_u:.6f}) "
    f"{sig(float(stats.norm.cdf(-t_u)), 2)}")
put("z975", f"{v(Z975, 2, extra=4)} (lm15.md:194 prints 1.9600)")
hw = A28 * Z975 * X[:h].std(axis=0, ddof=0) / sqrt(h)
put("forest_hw", f"half-widths Phi^-1(0.975) A s_i/sqrt(2191): {v(float(hw.min()), 0, pct=True)} "
    f"({names[int(hw.argmin())]}) to {v(float(hw.max()), 0, pct=True)} ({names[int(hw.argmax())]})")
gap = np.abs(a1 - float(a1.mean())) - hw
assert np.all(np.abs(gap) > EPS)
excl = int((gap >= EPS).sum())
put("forest_excl", f"first-half intervals excluding the first-half grand mean: {excl} of {N}; smallest margin "
    f"(half-width - abs(mean - grand mean)) {v(float(-gap.max()), 1, pct=True)} ({names[int(gap.argmax())]})")
_, _, b_rr, c_rr = js(X[h:])
_, _, b_dr, c_dr = js(Xd[h:])
put("reverse", f"estimated on the second half: c_hat {v(c_rr, 2)}; common removed {v(c_dr, 2)}; judged on the first: "
    f"RMSE c=0 {v(oos(m2, m1, 0), 1, pct=True)}, c=c_hat {v(oos(m2, m1, c_rr), 1, pct=True)}, c=c_hat(common) "
    f"{v(oos(m2, m1, c_dr), 1, pct=True)}, c=1 {v(oos(m2, m1, 1), 1, pct=True)}; optimal c {v(c_opt(m2, m1), 2)}")
put("widget", f"inputs A Rbar {A * Rb:.8f}; sqrt(A) s {vol:.8f}; years {years:.6f}; fhat {fhat:.6f}; initial readouts "
    f"at A sigma0 0.10: years {v(years, 2)}; SE {v(A * se, 2, pct=True)}; c {v(c10, 3)}; mean "
    f"{v(A * pm10, 1, pct=True)}; SD {v(A * psd10, 1, pct=True)}; 95% {v(A * (pm10 - Z975 * psd10), 1, pct=True)} to "
    f"{v(A * (pm10 + Z975 * psd10), 1, pct=True)}; fraction {v(c10 * fhat, 2)}")

# ================================================================ examples
need_n = next(n for n in range(3, 3000, 3) if beta_sf(82 + 2 * n // 3, 82 + n // 3, P55) > Fraction(1, 2))
pr_need = beta_sf(82 + 2 * need_n // 3, 82 + need_n // 3, P55)
pr_before = beta_sf(82 + 2 * (need_n - 3) // 3, 82 + (need_n - 3) // 3, P55)
put("months", f"record 2/3: smallest n (multiple of 3) with Pr(theta>=0.55) > 1/2: {need_n} months; Pr "
    f"{v(float(pr_need), 1, pct=True)}; at {need_n - 3}: {v(float(pr_before), 1, pct=True)}; c "
    f"{v(need_n / (need_n + 164), 3)}")
put("post10", f"A sigma0 = 10: c {v(c10, 3)}; posterior mean {v(A * pm10, 1, pct=True)}; SD {v(A * psd10, 1, pct=True)}; "
    f"from printed 0.869, 15.38, 3.89: {0.869 * 15.38:.4f}, {sqrt(0.869) * 3.89:.4f}")
put("worth", f"A sigma0 = 10: {n0_10:.1f} returns = {v(n0_10 / A, 2)} years (from printed (18.96/10)^2 = "
    f"{(18.96 / 10) ** 2:.4f}); c = 1/2: {T} returns = {v(years, 1)} years; c = 1/4: {3 * T} returns = "
    f"{v(3 * years, 1)} years")
epv, vpm = (A * psd10) ** 2, c10 * 0.10**2
put("tv_check", f"(16.6) at A sigma0 = 10, points^2: 100 = {v(vpm * 1e4, 1)} (variance of the posterior mean) + "
    f"{v(epv * 1e4, 1)} (expected posterior variance); sum {(vpm + epv) * 1e4:.10f}")
g1 = rng(1)
n1 = 10_000
mu1 = g1.standard_normal((n1, N))       # one 10,000 x 28 array of true means first,
x1 = mu1 + g1.standard_normal((n1, N))  # then one 10,000 x 28 array of noise
gm1 = x1.mean(axis=1, keepdims=True)
ch1 = 1 - (N - 3) / ((x1 - gm1) ** 2).sum(axis=1, keepdims=True)
e_raw = ((x1 - mu1) ** 2).sum(axis=1)
e_js = ((gm1 + ch1 * (x1 - gm1) - mu1) ** 2).sum(axis=1)
e_pp = ((gm1 + np.maximum(ch1, 0) * (x1 - gm1) - mu1) ** 2).sum(axis=1)
e_by = ((0.5 * x1 - mu1) ** 2).sum(axis=1)
put("exp1", f"Experiment 1, 10,000 cross-sections: raw {mc(e_raw)}; JS {mc(e_js)}; positive part {mc(e_pp)}; "
    f"Bayes 0.5x {mc(e_by)}; mean c_hat (positive part) {v(float(np.maximum(ch1, 0).mean()), 2, extra=2)}; "
    f"mean unclipped 1 - 25/S {v(float(ch1.mean()), 2, extra=2)}")
put("theory", f"N - (N-3)/(1 + spread^2) at spread 0, 1, 3: {N - (N - 3)}, {N - (N - 3) / 2:g}, {N - (N - 3) / 10:g}; "
    f"Bayes N/2 = {N / 2:g} at spread 1")
nz_r, sp1, b_r, c_r = js(X[:h])
put("js_raw", f"first half: noise {v(nz_r, 1, pct=True)}; spread SD (divisor 28) {v(sp1, 1, pct=True)}; 1 - c_hat "
    f"{v(b_r, 2)}; c_hat {c_r:g}")
put("fwd_opt", f"optimal c (forward) {v(c_opt(m1, m2), 2)}; deviations RMSE c=0 {v(oos(m1, m2, 0, True), 1, pct=True)}, "
    f"c=1 {v(oos(m1, m2, 1, True), 1, pct=True)}")
_, sp2, _, _ = js(X[h:])
put("spread2", f"second half spread SD (divisor 28) {v(sp2, 1, pct=True)}")
kx10 = kelly_exact(pm10)
put("kelly10", f"A sigma0 = 10: c fhat {v(c10 * fhat, 2)}; exact (shifted) {v(kx10, 2)}; posterior-integrated "
    f"{v(kelly_bayes_quad(c10), 2)}; fhat* {v(f_star, 2, extra=4)} (lm17.md:239 prints 4.1381)")
ksd = psd10 / s**2
put("kelly_sd", f"posterior SD of mu/sigma^2 {v(ksd, 2)}; 95% {v(c10 * fhat - Z975 * ksd, 1)} to "
    f"{v(c10 * fhat + Z975 * ksd, 1)}; at c = 1, 1/(s sqrt(T)) {v(1 / (s * sqrt(T)), 2)} (LM20's mean-only SE of fhat)")
kxh, kxq = kelly_exact(0.5 * Rb), kelly_exact(0.25 * Rb)
put("gaps", f"quadratic minus exact: c=1 {fhat:.5f} - {f_star:.5f} = {v(fhat - f_star, 2)}; c(10) {c10 * fhat:.5f} - "
    f"{kx10:.5f} = {v(c10 * fhat - kx10, 2)}; c=1/2 {0.5 * fhat:.5f} - {v(kxh, 2)} = {v(0.5 * fhat - kxh, 2)}; c=1/4 "
    f"{0.25 * fhat:.5f} - {kxq:.5f} = {v(0.25 * fhat - kxq, 2)}; 1 - c(10) {v(1 - c10, 2)}")
gb, gp = growth(c10 * fhat, pm10), growth(fhat, pm10)
put("growth10", f"A sigma0 = 10: Bayes {v(gb, 0, pct=True)}, plug-in {v(gp, 0, pct=True)}, share {v(gp / gb, 3)} "
    f"(1-(1-1/c)^2 = {1 - (1 - 1 / c10) ** 2:.6f})")
gbh, gph = growth(0.5 * fhat, 0.5 * Rb), growth(fhat, 0.5 * Rb)
gbq, gpq = growth(0.25 * fhat, 0.25 * Rb), growth(fhat, 0.25 * Rb)
assert abs(gph) < 1e-12
put("growth_sc", f"c = 1/2: Bayes {v(gbh, 1, pct=True)}, plug-in {gph:.1e}; c = 1/4: Bayes {v(gbq, 2, pct=True)}, "
    f"plug-in {v(gpq, 1, pct=True)} (ratio {gpq / gbq:.6f}); Pr(mu>0) {v(1 - float(stats.norm.cdf(-0.25 * Rb / (0.5 * se))), 1, pct=True)}"
    f" and {v(1 - float(stats.norm.cdf(-0.5 * Rb / (sqrt(0.5) * se))), 1, pct=True)}")

# ================================================================ problems
put("p1", f"Beta(3,7), 4 of 6: {Fraction(7, 16)} = {v(7 / 16, 4)}; data alone {v(4 / 6, 3)}; 7/10 {v(0.7, 3)}")
put("p2", f"prior SD 6, SE 4: c 36/52 = {v(36 / 52, 2)}; 6/10 {v(0.6, 2)}; 16/52 {v(16 / 52, 2)}")
put("p3", f"posterior SD {v(1 / sqrt(1 / 36 + 1 / 16), 2)}; sqrt(52) {v(sqrt(52), 2)}; 6 x 4/10 {v(2.4, 2)}")
put("p4", f"N=10, sum 18: c_hat 1-7/18 {v(1 - 7 / 18, 3)}; N-2: {v(1 - 8 / 18, 3)}; 7/18 {v(7 / 18, 3)}")
put("p5", f"fhat 3.0, c 0.4: {v(0.4 * 3, 2)}; sqrt(c) {v(sqrt(0.4) * 3, 2)}; c^2 {v(0.16 * 3, 2)}")
put("p6", "c = 1/2: plug-in = 2 x Bayes, 1-(1-2)^2 = 0; distractors 1-(1-1/2)^2 = 0.75, 0.5")
c5 = weight(0.05)
pm5, psd5 = post(c5)
put("p9", f"A sigma0 = 5: c {v(c5, 3)} (from printed 3.89: {25 / (25 + 3.89**2):.5f}); mean {v(A * pm5, 1, pct=True)}; "
    f"SD {v(A * psd5, 1, pct=True)}; 95% {v(A * (pm5 - Z975 * psd5), 1, pct=True)} to "
    f"{v(A * (pm5 + Z975 * psd5), 1, pct=True)}; Pr(mu<=0) {sig(float(stats.norm.cdf(-pm5 / psd5)), 1)}; "
    f"fraction {v(c5 * fhat, 2)}; worth {v((vol / 0.05) ** 2, 1)} years (from printed (18.96/5)^2 = {(18.96 / 5) ** 2:.3f})")
g2 = rng(2)
n2 = 20_000
res = []
for spread in (0.0, 1.0, 3.0):
    mu2 = spread * g2.standard_normal((n2, N))  # drawn even at spread 0, so the draws are used up
    x2 = mu2 + g2.standard_normal((n2, N))
    gm2 = x2.mean(axis=1, keepdims=True)
    ch2 = 1 - (N - 3) / ((x2 - gm2) ** 2).sum(axis=1, keepdims=True)
    ej = ((gm2 + ch2 * (x2 - gm2) - mu2) ** 2).sum(axis=1)
    ep = ((gm2 + np.maximum(ch2, 0) * (x2 - gm2) - mu2) ** 2).sum(axis=1)
    er = ((x2 - mu2) ** 2).sum(axis=1)
    res.append(f"spread {spread:g}: raw {mc(er)}, JS {mc(ej)}, positive part {mc(ep)}")
put("exp2", "Experiment 2, 20,000 each: " + "; ".join(res))
nz_e, _, b_e, c_e = js(Xe[:h])
me1, me2 = Xe[:h].mean(axis=0), Xe[h:].mean(axis=0)
tx = np.asarray(smp.taiex, dtype=np.float64)
put("p11", f"TAIEX removed: noise {v(nz_e, 1, pct=True)}; 1 - c_hat {v(b_e, 1)}; c_hat {c_e:g}; RMSE c=0 "
    f"{v(oos(me1, me2, 0), 1, pct=True)} (deviations {v(oos(me1, me2, 0, True), 1, pct=True)}); average excess "
    f"{v(A28 * float(me1.mean()), 1, pct=True)} -> {v(A28 * float(me2.mean()), 1, 0, pct=True)}; TAIEX "
    f"{v(A28 * float(tx[:h].mean()), 1, pct=True)} -> {v(A28 * float(tx[h:].mean()), 1, pct=True)}")
pr1624 = beta_sf(98, 90, P55)
put("p12", f"16 of 24, Beta(98,90): mean {98 / 188:.5f}; Pr(theta>=0.55) {v(float(pr1624), 1, pct=True)} exact; "
    f"LM13 18.02% (lm13.md:530)")
thirds = [len(a) for a in np.array_split(np.arange(T28), 3)]
put("thirds", f"thirds of {T28}: {thirds} -> sorted {sorted(thirds)}")

# ================================================================ added at the revision (2026-10-19)
eta = T * Rb**2 / (T * Rb**2 + s**2)
put("eta", f"LM20's eta* = T Rbar^2/(T Rbar^2 + s^2) {v(eta, 3)} (LM20's E1 prints 0.940); c at A sigma0 = A Rbar "
    f"{v(weight(A * Rb), 3)}")

assert sorted(VAL) == sorted(ORDER), sorted(set(VAL) ^ set(ORDER))
print("\n".join(f"A24-{i:02d} {VAL[k]}" for i, k in enumerate(ORDER, start=1)))
