"""LM15 anchors: every number the LM15 brief (plans/vol-3.md, "Distributions in Finance") quotes.

Reads data/processed/vol3_taiex.parquet, built and checked by data/vol3_series.py: TR23, the TAIEX total-return index,
closes 2003-01-02 .. 2026-10-08, and R, its simple daily return (null on the first row). T = 5,849 returns from
2003-01-03; moments divide by T; years = calendar days / 365.25; A = T / years. Counts against a threshold use the
guard of PITFALLS section 5 (R <= -x + 1e-12, R >= x - 1e-12) and are asserted equal to an exact recount with
fractions.Fraction from the two-decimal closes. A printed derived value is recomputed from its printed inputs at their
printed precision and asserted (PITFALLS section 7). LM15 simulates nothing, so no generator is created.
Empirical quantiles are LM14's order statistics R_(ceil(uT)), T the size of the sample or part in use
(np.quantile, method="inverted_cdf").

Prints one line per anchor, "A15-NN <value>", in ID order, and writes nothing. IDs follow the order in which the
Stage 1 brief first quoted them and stay fixed when a revision moves a first quotation.

Run from the repository root:  PYTHONUTF8=1 uv run python data/vol3_anchors_lm15.py [repository root]
"""
import itertools
import math
import sys
from collections.abc import Callable
from datetime import date
from fractions import Fraction
from pathlib import Path

import numpy as np
import polars as pl
from numpy.typing import NDArray
from scipy import integrate, optimize, special, stats

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
HERE = ROOT / "data"
PROC = HERE / "processed"
TR23 = PROC / "vol3_taiex.parquet"
EPS = 1e-12
LIMIT_CHANGE = "2015-06-01"          # the daily price limit was 7% before this date and 10% from it on

Vec = NDArray[np.float64]
VALUES: dict[str, str] = {}


def put(key: str, text: str) -> None:
    assert key not in VALUES, key
    VALUES[key] = text


def same(value: float, fmt: str, printed: str) -> None:
    """Assert that a value recomputed from printed inputs prints as the brief prints it."""
    assert format(value, fmt) == printed, (format(value, fmt), printed)


def same_list(values: list[float], fmt: Callable[[float], str], printed: str) -> None:
    got = ", ".join(fmt(v) for v in values)
    assert got == printed, (got, printed)


def days_fmt(v: float) -> str:
    """Expected days as printed: one decimal from 10 up, three significant figures down to 0.001, two below it."""
    if v >= 10:
        return f"{v:.1f}"
    return f"{v:#.3g}".rstrip(".") if v >= 1e-3 else f"{v:.1e}"


def sig3(v: float) -> str:
    """Three significant figures with trailing zeros kept (79.0, 5.00); whole numbers from 100 up; a x 10^-b below 0.001."""
    if v >= 100:
        return f"{v:.0f}"
    return f"{v:#.3g}".rstrip(".") if v >= 1e-3 else f"{v:.1e}"


def pct(x: float, nd: int = 6) -> str:
    return f"{100 * x:.{nd}f}%"


# ------------------------------------------------------------------ data
df = pl.read_parquet(TR23).sort("date")
dates_c = [d.isoformat() for d in df["date"].to_list()]
closes = np.asarray(df["tr"].to_numpy(), dtype=np.float64)
assert df["R"].null_count() == 1 and df["R"][0] is None
R: Vec = np.asarray(df["R"].to_numpy()[1:], dtype=np.float64)
dates = dates_c[1:]
T = len(R)
assert np.abs(R - (closes[1:] / closes[:-1] - 1)).max() < 1e-15
days = (date.fromisoformat(dates_c[-1]) - date.fromisoformat(dates_c[0])).days
years = days / 365.25
A = T / years

levels = [Fraction(repr(float(v))) for v in closes]          # the two-decimal closes, exactly
assert all((100 * lv).denominator == 1 for lv in levels)
RX = [levels[i] / levels[i - 1] - 1 for i in range(1, len(levels))]


def le(x: Fraction, sample: Vec | None = None) -> int:
    """Days with R <= -x (a loss level x > 0), with the guard."""
    xs = R if sample is None else sample
    return int((xs <= -float(x) + EPS).sum())


def ge(x: Fraction) -> int:
    return int((R >= float(x) - EPS).sum())


def le_exact(x: Fraction) -> int:
    return sum(1 for v in RX if v <= -x)


def ge_exact(x: Fraction) -> int:
    return sum(1 for v in RX if v >= x)


for k in range(1, 11):
    xk = Fraction(k, 100)
    assert le(xk) == le_exact(xk) and ge(xk) == ge_exact(xk), k
assert sum(1 for v in RX if v == 0) == 0

put("T", f"{T} returns {dates[0]} .. {dates[-1]}; {len(closes)} closes from {dates_c[0]}")
put("years", f"{days} calendar days; {years:.6f} years; A = {A:.6f}")

Rbar, s = float(R.mean()), float(R.std())
r: Vec = np.log1p(R)
rbar, s_r = float(r.mean()), float(r.std())
exk = float(stats.kurtosis(R))
assert abs(exk - (((R - Rbar) ** 4).mean() / s**4 - 3)) < 1e-12
skw = float(stats.skew(R))
put("Rbar", pct(Rbar, 8))
put("s", pct(s, 8))
put("exk", f"{exk:.6f}")
put("skew", f"{skw:.6f}")
i_min, i_max = int(R.argmin()), int(R.argmax())
put("extremes", f"min {pct(R[i_min], 4)} ({dates[i_min]}); max {pct(R[i_max], 4)} ({dates[i_max]})")


def zx(x: float) -> float:
    return (-x - Rbar) / s


# ------------------------------------------------------------------ Student-t fits
nu_m, loc_m, sc_m = (float(v) for v in stats.t.fit(R))


def nll(p: Vec) -> float:
    return float(-stats.t.logpdf(R, p[0], p[1], math.exp(p[2])).sum()) if p[0] > 0.5 else 1e18


for start in ((3.0, Rbar, math.log(0.6 * s)), (5.0, 0.0, math.log(s)), (2.2, 0.001, math.log(0.007)),
              (10.0, Rbar, math.log(0.8 * s))):
    res = optimize.minimize(nll, np.array(start), method="Nelder-Mead",
                            options={"xatol": 1e-10, "fatol": 1e-10, "maxiter": 20000, "maxfev": 40000})
    assert abs(res.x[0] - nu_m) < 1e-3 and res.fun >= nll(np.array([nu_m, loc_m, math.log(sc_m)])) - 1e-3
put("mlfit", f"nu {nu_m:.6f}; loc {pct(loc_m)}; scale {pct(sc_m)}")
nu_k = 4 + 6 / exk
sc_k = s * math.sqrt((nu_k - 2) / nu_k)
put("kfit", f"nu {nu_k:.6f}; scale {pct(sc_k)}; from the printed 5.27: {4 + 6 / 5.27:.6f}; "
            f"P9's distractors: 6/5.27 = {6 / 5.27:.6f} (the 4 forgotten); 4 + 6/(5.27 - 3) = "
            f"{4 + 6 / (5.27 - 3):.6f} (the excess taken as the kurtosis)")
same(4 + 6 / 5.27, ".2f", "5.14")
same(6 / 5.27, ".2f", "1.14")
same(4 + 6 / (5.27 - 3), ".2f", "6.64")
sd_m = sc_m * math.sqrt(nu_m / (nu_m - 2))
same(0.7761 * math.sqrt(3.065 / 1.065), ".3f", "1.317")
put("mlsd", f"{pct(sd_m)}; / s = {sd_m / s:.6f}")


def e_norm(x: float) -> float:            # expected days with R <= x under the fitted normal
    return T * float(stats.norm.cdf((x - Rbar) / s))


def e_ml(x: float) -> float:
    return T * float(stats.t.cdf(x, nu_m, loc_m, sc_m))


def e_k(x: float) -> float:
    return T * float(stats.t.cdf((x - Rbar) / sc_k, nu_k))


def e_ml_p(x: float) -> float:           # from the printed parameters 3.065, 0.0997%, 0.7761%
    return 5849 * float(stats.t.cdf((100 * x - 0.0997) / 0.7761, 3.065))


def e_norm_p(x: float) -> float:         # from the printed 0.0625% and 1.20836% (X1 and X6 print s to five decimals)
    return 5849 * float(stats.norm.cdf((100 * x - 0.0625) / 1.20836))


def e_k_p(x: float) -> float:            # from the printed nu 5.139 and 0.0625%, 1.20836%
    sc = 1.20836 * math.sqrt(3.139 / 5.139)
    return 5849 * float(stats.t.cdf((100 * x - 0.0625) / sc, 5.139))


# ------------------------------------------------------------------ the case
c5 = le(Fraction(5, 100))
put("norm5", f"{e_norm(-0.05):.6f}; from the printed 0.0625% and 1.20836%: {e_norm_p(-0.05):.6f}; with "
             f"s = 1.2084%: {5849 * float(stats.norm.cdf((-5 - 0.0625) / 1.2084)):.6f}")
same(e_norm_p(-0.05), ".3g", "0.0817")
put("cnt5", f"{c5}")
put("ml5", f"{e_ml(-0.05):.6f}; from the printed 3.065, 0.0997%, 0.7761%: {e_ml_p(-0.05):.6f}; "
           f"with nu 3.07: {5849 * float(stats.t.cdf((-5 - 0.0997) / 0.7761, 3.07)):.6f}")
same(e_ml_p(-0.05), ".1f", "19.6")
assert format(5849 * float(stats.t.cdf((-5 - 0.0997) / 0.7761, 3.07)), ".1f") != "19.6"

months_all = sorted({d[:7] for d in dates})
big = np.abs(R) >= 0.03 - EPS
assert int(big.sum()) == sum(1 for v in RX if abs(v) >= Fraction(3, 100))
mon_idx = np.array([months_all.index(d[:7]) for d in dates])
cnt_m: Vec = np.bincount(mon_idx, weights=big.astype(float), minlength=len(months_all))
sess_m: Vec = np.bincount(mon_idx, minlength=len(months_all)).astype(float)
lam = float(cnt_m.mean())
var_m = float(cnt_m.var())
put("months", f"{len(months_all)} months {months_all[0]} .. {months_all[-1]}; sessions a month: mean "
              f"{sess_m.mean():.6f}, min {int(sess_m.min())}, max {int(sess_m.max())}; {months_all[0]} has "
              f"{int(sess_m[0])}, {months_all[-1]} has {int(sess_m[-1])}")
n_down3, n_up3 = le(Fraction(3, 100)), ge(Fraction(3, 100))
put("big", f"{int(big.sum())} days with |R| >= 3% ({n_down3} with R <= -3%, {n_up3} with R >= +3%); "
           f"p = {int(big.sum())}/{T} = {big.mean():.8f}")
put("lam", f"{int(cnt_m.sum())}/{len(months_all)} = {lam:.8f}")
put("var_m", f"{var_m:.8f} (divisor {len(months_all)}); divisor {len(months_all) - 1}: {cnt_m.var(ddof=1):.6f}")
put("ratio", f"{var_m / lam:.6f}; from the printed 1.846/0.612: {1.846 / 0.612:.6f}; "
             f"0.612/1.846 = {0.612 / 1.846:.6f}")
same(1.846 / 0.612, ".2f", "3.02")
eight = [m for m, c in zip(months_all, cnt_m) if c == 8]
assert int(cnt_m.max()) == 8
put("mon8", f"{len(eight)} months with eight: {', '.join(eight)}; 2008-12 has "
            f"{int(cnt_m[months_all.index('2008-12')])}")

# ------------------------------------------------------------------ binomial: up days in 20-session blocks
NB = T // 20
up = (R > 0).astype(float)
blocks = up[: NB * 20].reshape(NB, 20).sum(axis=1)
p_hat = float(up[: NB * 20].mean())
put("blocks", f"{NB} blocks of 20 from {dates[0]}; {T - NB * 20} returns left out, {dates[NB * 20]} .. {dates[-1]}")
put("p_hat", f"{int(up[: NB * 20].sum())}/{NB * 20} = {p_hat:.8f}")
v_bin = 20 * p_hat * (1 - p_hat)
put("blk_mv", f"mean {blocks.mean():.6f}; variance {blocks.var():.6f} (divisor {NB}; divisor {NB - 1}: "
              f"{blocks.var(ddof=1):.6f})")
put("bin_mv", f"np = {20 * p_hat:.6f}; np(1-p) = {v_bin:.6f}; from the printed 0.548: {20 * 0.548 * 0.452:.6f}; "
              f"sd {math.sqrt(v_bin):.6f}; n/4 = 5")
same(20 * 0.548 * 0.452, ".2f", "4.95")
same(math.sqrt(20 * 0.548 * 0.452), ".2f", "2.23")
obs = [int((blocks == j).sum()) for j in range(4, 18)]
exp_b = [NB * float(stats.binom.pmf(j, 20, p_hat)) for j in range(4, 18)]
assert int(blocks.min()) >= 5 and int(blocks.max()) <= 16 and sum(obs) == NB
outside = NB * (float(stats.binom.cdf(3, 20, p_hat)) + float(stats.binom.sf(17, 20, p_hat)))
put("blk_obs", ", ".join(str(v) for v in obs))
put("blk_exp", ", ".join(f"{v:.4f}" for v in exp_b) + f" (p = 3200/5840 unrounded); outside 4..17: {outside:.4f}")
t5, t16 = float(stats.binom.cdf(5, 20, 0.548)), float(stats.binom.sf(15, 20, 0.548))
put("bin_tails", f"Pr(X<=5) {t5:.6f} -> {NB * t5:.4f} blocks (observed {int((blocks <= 5).sum())}); Pr(X>=16) "
                 f"{t16:.6f} -> {NB * t16:.4f} (observed {int((blocks >= 16).sum())}); from the unrounded p: "
                 f"{NB * float(stats.binom.cdf(5, 20, p_hat)):.4f}, {NB * float(stats.binom.sf(15, 20, p_hat)):.4f}; "
                 f"292 x 0.0181 = {292 * 0.0181:.4f}")
same(t5, ".3g", "0.00677")
same(t16, ".4g", "0.01807")
same(NB * t16, ".2f", "5.28")
same(292 * 0.00677, ".2f", "1.98")
same(292 * 0.01807, ".2f", "5.28")
assert format(292 * 0.0181, ".2f") != "5.28"
# X2 plots p = 3,200/5,840 unrounded (its legend says so); from the printed 0.548 ten values would differ
same_list(exp_b, lambda v: f"{v:.2f}", "0.39, 1.50, 4.56, 11.05, 21.77, 35.18, 46.91, 51.69, 46.99, 35.05, 21.24, 10.30, 3.90, 1.11")
assert abs(outside - (NB - sum(exp_b))) < 1e-9
same(outside, ".2f", "0.34")
down = R < 0
put("signs", f"Pr(R<0) {int(down.sum())}/{T} = {down.mean():.6f}; on the {T - 1} day-pairs: Pr(R_t<0) = "
             f"{down[1:].mean():.6f}, Pr(R_t<0 | R_t-1<0) = {(down[:-1] & down[1:]).sum() / down[:-1].sum():.6f}")
# A15-30: LM13's sign dependence as a lag-1 correlation of the down-day (equally, up-day: no return is 0) indicators,
# rho1 = (Pr(D_t | D_t-1) - Pr(D)) / (1 - Pr(D)) for a stationary two-state sequence, from the printed 0.4639 and 0.4521
rho_p = (0.4639 - 0.4521) / (1 - 0.4521)
pc = float((down[:-1] & down[1:]).sum() / down[:-1].sum())
pd_ = float(down[1:].mean())
rho_u = (pc - pd_) / (1 - pd_)
xu = up[: NB * 20]
pairs_in = np.ones(NB * 20 - 1, dtype=bool)
pairs_in[19::20] = False                   # the 291 pairs that straddle two blocks
rho_in = float(np.corrcoef(xu[:-1][pairs_in], xu[1:][pairs_in])[0, 1])
rho_all = float(np.corrcoef(up[:-1], up[1:])[0, 1])
same(rho_p, ".4f", "0.0215")
same(20 * 0.548 * 0.452 * (1 + 2 * (19 / 20) * 0.0215), ".2f", "5.16")
same(v_bin * (1 + 2 * (19 / 20) * rho_u), ".2f", "5.16")
put("dep_var", f"rho1 from the printed 0.4639, 0.4521: {rho_p:.6f} (from the unrounded frequencies {rho_u:.6f}); "
               f"20 x 0.548 x 0.452 x (1 + 2 (19/20) 0.0215) = {20 * 0.548 * 0.452 * (1 + 2 * (19 / 20) * 0.0215):.6f}; "
               f"with the unrounded p and rho1: {v_bin * (1 + 2 * (19 / 20) * rho_u):.6f}; other pair sets (not printed): "
               f"within-block pairs {rho_in:.6f}, all {T - 1} pairs of R {rho_all:.6f}")

# ------------------------------------------------------------------ Poisson
p3 = float(big.mean())
same(175 / 5849, ".5f", "0.02992")
pb = 0.02992
put("rare", "; ".join(f"j={j}: Bin(20, 0.02992) {float(stats.binom.pmf(j, 20, pb)):.6f} against "
                      f"Poisson(0.5984) {float(stats.poisson.pmf(j, 20 * pb)):.6f}" for j in range(3)))
same_list([(1 - 0.612 / n) ** n for n in (20, 250, 10_000)] + [math.exp(-0.612)], lambda v: f"{v:.5f}",
          "0.53711, 0.54186, 0.54226, 0.54227")
same_list([float(stats.binom.pmf(j, 20, pb)) for j in range(3)], lambda v: f"{v:.4g}", "0.5447, 0.336, 0.09845")
same_list([float(stats.poisson.pmf(j, 20 * pb)) for j in range(3)], lambda v: f"{v:.4g}", "0.5497, 0.3289, 0.09842")
put("limit", "; ".join(f"n={n}: {(1 - 0.612 / n) ** n:.6f}" for n in (20, 250, 10_000))
        + f"; e^-0.612 = {math.exp(-0.612):.6f}")
obs_m = [int((cnt_m == j).sum()) for j in range(9)]
exp_m = [len(months_all) * float(stats.poisson.pmf(j, lam)) for j in range(9)]
put("mon_obs", ", ".join(str(v) for v in obs_m))
same_list(exp_m, days_fmt, "155.1, 94.9, 29.0, 5.92, 0.906, 0.111, 0.0113, 9.9e-04, 7.6e-05")
same(len(months_all) * float(stats.poisson.sf(4, lam)), ".3f", "0.123")
same(len(months_all) * float(stats.poisson.sf(7, lam)), ".1e", "8.1e-05")
put("mon_exp", ", ".join(f"{v:.4f}" for v in exp_m[:5]) + ", " + ", ".join(f"{v:.3g}" for v in exp_m[5:])
        + f"; five or more {len(months_all) * float(stats.poisson.sf(4, lam)):.6f} (observed "
          f"{int((cnt_m >= 5).sum())}); eight or more {len(months_all) * float(stats.poisson.sf(7, lam)):.4e}")
p0, p5 = math.exp(-0.612), float(stats.poisson.sf(4, 0.612))
put("pois612", f"Pr(X=0) {p0:.6f}; Pr(X>=5) {p5:.8f}; x286: {286 * p0:.4f}, {286 * p5:.6f}")
same(286 * p0, ".1f", "155.1")
same(286 * p5, ".3f", "0.123")
same(286 * 0.612 * p0, ".1f", "94.9")
nbar, nvar = float(sess_m.mean()), float(sess_m.var())
put("unequal", f"{nbar * p3 * (1 - p3) + p3**2 * nvar:.6f} (mean sessions {nbar:.4f}, variance {nvar:.4f}, p = 175/5849)")
pre_m = np.array([m < LIMIT_CHANGE[:7] for m in months_all])
rr = [float(cnt_m[k].var() / cnt_m[k].mean()) for k in (pre_m, ~pre_m)]
put("reg_ratio", f"months {int(pre_m.sum())} / {int((~pre_m).sum())}: variance / mean {rr[0]:.6f} / {rr[1]:.6f}")

# ------------------------------------------------------------------ normal quantiles
U = ("0.001", "0.01", "0.025", "0.05", "0.5", "0.95", "0.99")      # levels of the empirical quantiles reported
put("phiinv", "; ".join(f"{u}: {float(stats.norm.ppf(float(u))):.6f}" for u in ("0.95", "0.975", "0.99", "0.999")))
srt = np.sort(R)
order = np.argsort(R, kind="stable")


def emp(u: str, xs: Vec | None = None) -> tuple[int, float]:
    """LM14's empirical quantile: the order statistic R_(ceil(uT))."""
    v = np.sort(R if xs is None else xs)
    j = math.ceil(Fraction(u) * len(v))
    assert float(np.quantile(v, float(u), method="inverted_cdf")) == float(v[j - 1])
    return j, float(v[j - 1])


put("normq", "; ".join(f"{u}: {pct(Rbar + s * float(stats.norm.ppf(float(u))), 4)}"
                       for u in ("0.001", "0.01", "0.025", "0.05", "0.99")))
for u, ph, printed in (("0.001", -3.0902, "-3.672"), ("0.01", -2.3263, "-2.749"), ("0.025", -1.9600, "-2.306"),
                       ("0.05", -1.6449, "-1.925"), ("0.99", 2.3263, "2.874")):
    same(0.0625 + 1.2084 * ph, ".3f", printed)
put("empq", "; ".join(f"{u}: #{emp(u)[0]} {pct(emp(u)[1], 4)}" for u in U)
        + f"; #6 is {dates[int(order[5])]}; linear default at 0.01: {pct(float(np.quantile(R, 0.01)), 4)}")
same(-2.749 - -3.567, ".2f", "0.82")
same(3.125 - 2.874, ".2f", "0.25")
put("p5gap", f"from the printed quantiles: 1% {-2.749 - -3.567:.3f}; 99% {3.125 - 2.874:.3f} percentage points")
q_ml = float(stats.t.ppf(0.01, nu_m, loc_m, sc_m))
q_ml_p = 0.0997 + 0.7761 * float(stats.t.ppf(0.01, 3.065))
put("mlq", f"1%: {pct(q_ml, 4)} (from the printed parameters {q_ml_p:.4f}%); 5%: "
           f"{pct(float(stats.t.ppf(0.05, nu_m, loc_m, sc_m)), 4)}")
same(q_ml_p, ".3f", "-3.365")
pp = (np.arange(1, T + 1) - 0.5) / T
qq: Vec = np.asarray(stats.norm.ppf(pp), dtype=np.float64)
zs = (srt - Rbar) / s
sel = (np.abs(qq) > 2) | (np.arange(T) % 10 == 0)
sel[0] = sel[-1] = True
put("qq", f"rank 1 ({qq[0]:.6f}, {zs[0]:.6f}); rank {T} ({qq[-1]:.6f}, {zs[-1]:.6f}); rank 59 ({qq[58]:.6f}, "
          f"{zs[58]:.6f}); {int(sel.sum())} points plotted, {int((np.abs(qq) > 2).sum())} with |normal quantile| > 2")
same((-9.6997 - 0.0625) / 1.2084, ".3f", "-8.079")
same((9.2512 - 0.0625) / 1.2084, ".3f", "7.604")
same((-3.5671 - 0.0625) / 1.2084, ".3f", "-3.004")
phi15 = float(stats.norm.ppf(15 / T))
sig15 = (-0.05 - Rbar) / phi15
put("sig15", f"Phi^-1(15/T) {phi15:.6f}; sigma {pct(sig15)}; then days <= -2%: "
             f"{T * float(stats.norm.cdf((-0.02 - Rbar) / sig15)):.4f}; from the printed 1.809%: "
             f"{5849 * float(stats.norm.cdf((-2 - 0.0625) / 1.809)):.4f}")
same((-5 - 0.0625) / -2.7988, ".3f", "1.809")
same(5849 * float(stats.norm.cdf((-2 - 0.0625) / 1.809)), ".0f", "743")

# ------------------------------------------------------------------ lognormal: calendar-year growth factors
last: dict[int, float] = {}
for d, c in zip(dates_c, closes):
    last[int(d[:4])] = float(c)
yrs = list(range(2003, 2026))
G = np.array([last[y] / (float(closes[0]) if y == 2003 else last[y - 1]) for y in yrs])
put("annual", ", ".join(f"{y} {pct(g - 1, 4)}" for y, g in zip(yrs, G)))
put("annual_means", f"arithmetic {pct(float(G.mean()) - 1, 4)}; compound {pct(math.exp(float(np.log(G).mean())) - 1, 4)}")
muX, sX = float(np.log(G).mean()), float(np.log(G).std())
put("muX", f"mu_X {muX:.8f}; sigma_X {sX:.8f} (divisor 23; divisor 22: {float(np.log(G).std(ddof=1)):.6f})")
med, mean_g = math.exp(muX), math.exp(muX + sX**2 / 2)
sd_g = math.sqrt((math.exp(sX**2) - 1) * math.exp(2 * muX + sX**2))
put("logn_mom", f"median {med:.6f}; mean {mean_g:.6f}; sd {sd_g:.6f}; from 0.1165: median {math.exp(0.1165):.6f}")
same(math.exp(0.11646), ".4f", "1.1235")
same(math.exp(0.11646 + 0.22207**2 / 2), ".4f", "1.1516")
same(math.sqrt((math.exp(0.22207**2) - 1) * math.exp(2 * 0.11646 + 0.22207**2)), ".4f", "0.2589")
assert format(math.exp(0.1165), ".4f") != "1.1235"
ploss = float(stats.norm.cdf(-muX / sX))
put("ploss", f"Phi({-muX / sX:.6f}) = {ploss:.6f}; Phi(+{muX / sX:.6f}) = {1 - ploss:.6f}; x 23 = {23 * ploss:.4f}; "
             f"losing years "
             f"{int((G < 1).sum())} ({', '.join(str(y) for y, g in zip(yrs, G) if g < 1)}) = {(G < 1).mean():.6f}")
same(float(stats.norm.cdf(-0.11646 / 0.22207)), ".3f", "0.300")
same(-0.11646 / 0.22207, ".4f", "-0.5244")
q05, q95 = math.exp(muX + sX * float(stats.norm.ppf(0.05))), math.exp(muX + sX * float(stats.norm.ppf(0.95)))
put("logn_q", f"5% {q05:.6f}; 95% {q95:.6f}; outside: 2008 {G[5]:.6f}, 2009 {G[6]:.6f}; 10% of 23 = 2.3")
same(math.exp(0.11646 - 1.644854 * 0.22207), ".4f", "0.7797")
same(math.exp(0.11646 + 1.644854 * 0.22207), ".4f", "1.6189")
lg = stats.lognorm(s=sX, scale=math.exp(muX))
assert abs(float(lg.mean()) - mean_g) < 1e-12 and abs(float(lg.ppf(0.05)) - q05) < 1e-12
gs = np.sort(G)
put("emp_med_g", f"{gs[11]:.6f} ({yrs[int(np.argsort(G)[11])]})")
put("norm_annual", f"Pr(G<0) = Phi(-{G.mean():.6f}/{G.std():.6f}) = {float(stats.norm.cdf(-G.mean() / G.std())):.4e}")
same(float(stats.norm.cdf(-1.1497 / 0.2370)), ".1e", "6.1e-07")
# LM17's iid daily model over one year, fitted to the same window as the 23 calendar years (C2; editor 2026-10-18):
# the log returns dated 2003-01-03 .. 2025-12-31, whose sum is the sum of the 23 ln G_y
m1 = round(A)
win = np.array([d <= "2025-12-31" for d in dates])
r_w: Vec = r[win]
assert abs(float(r_w.sum()) - float(np.log(G).sum())) < 1e-12
rb_w, sr_w = float(r_w.mean()), float(r_w.std())
mu_w, sd_w = m1 * rb_w, sr_w * math.sqrt(m1)
p_w = float(stats.norm.cdf(-mu_w / sd_w))
put("lm17", f"{len(r_w)} log returns {dates[0]} .. {dates[int(np.flatnonzero(win)[-1])]}: rbar {pct(rb_w, 6)}, s_r "
            f"{pct(sr_w, 6)}; m = round(A) = {m1}: mean m rbar = {mu_w:.6f}, sd s_r sqrt(m) = {sd_w:.6f}; "
            f"Pr(loss year) = Phi(-mean/sd) = {p_w:.6f}; x 23 = {23 * p_w:.4f}; against mu_X {muX:.6f}, sigma_X {sX:.6f}; "
            f"from the printed 0.1163, 0.1856: {float(stats.norm.cdf(-0.1163 / 0.1856)):.6f}; with 0.186: "
            f"{float(stats.norm.cdf(-0.1163 / 0.186)):.6f}")
same(float(stats.norm.cdf(-0.1163 / 0.1856)), ".3f", "0.265")
same(p_w, ".3f", "0.265")
same(mu_w, ".4f", "0.1163")
same(sd_w, ".4f", "0.1856")
same(float(stats.norm.cdf(-0.1163 / 0.186)), ".3f", "0.266")      # so the brief prints 0.1856, not 0.186
put("rbar", f"rbar {pct(rbar, 8)}; s_r {pct(s_r, 8)}")
d_ln = T * float(stats.norm.cdf((math.log(0.95) - rbar) / s_r))
put("dlogn5", f"{d_ln:.6f}; from the printed 0.05517%, 1.2107%: "
              f"{5849 * float(stats.norm.cdf((math.log(0.95) - 0.0005517) / 0.012107)):.6f}")
same(5849 * float(stats.norm.cdf((math.log(0.95) - 0.0005517) / 0.012107)), ".4f", "0.0541")

# ------------------------------------------------------------------ gamma function and Student-t constants
put("gamma", f"Gamma(1/2) {special.gamma(0.5):.6f} (sqrt(pi) {math.sqrt(math.pi):.6f}); Gamma(3/2) "
             f"{special.gamma(1.5):.6f}; Gamma(2) {special.gamma(2.0):.6f}; Gamma(5/2) {special.gamma(2.5):.6f}")


def c_nu(nu: float) -> float:
    return math.exp(float(special.gammaln((nu + 1) / 2) - special.gammaln(nu / 2))) / math.sqrt(nu * math.pi)


put("c_nu", "; ".join(f"nu={v}: {c_nu(v):.6f}" for v in (1, 3, 4, 30, 1000))
        + f"; 1/sqrt(2 pi) {1 / math.sqrt(2 * math.pi):.6f}; 2/(pi sqrt 3) {2 / (math.pi * math.sqrt(3)):.6f}")
same(2 / (math.pi * math.sqrt(3)), ".4f", "0.3676")
for v in (nu_m, nu_k, 3.0, 5.0):
    area = integrate.quad(lambda y, v=v: c_nu(v) * (1 + y * y / v) ** (-(v + 1) / 2), -np.inf, np.inf)[0]
    assert abs(area - 1) < 1e-8, (v, area)
for v, m2, m4 in ((5.0, 5 / 3, None), (6.0, 1.5, 13.5)):
    e2 = integrate.quad(lambda y, v=v: y**2 * float(stats.t.pdf(y, v)), -np.inf, np.inf)[0]
    assert abs(e2 - m2) < 1e-7
    if m4 is not None:
        e4 = integrate.quad(lambda y, v=v: y**4 * float(stats.t.pdf(y, v)), -np.inf, np.inf)[0]
        assert abs(e4 - m4) < 1e-6


def t_var(nu: float) -> float:       # (15.10), nu > 2
    return nu / (nu - 2)


def t_kurt(nu: float) -> float:      # (15.10), nu > 4
    return 3 + 6 / (nu - 4)


put("t_mom", f"nu=3: variance {t_var(3):.6f}, kurtosis infinite; nu=4: variance {t_var(4):.6f}, kurtosis infinite; "
             f"nu=5: variance {t_var(5):.6f}, kurtosis {t_kurt(5):.6f}; nu=6: variance {t_var(6):.6f}, kurtosis "
             f"{t_kurt(6):.6f}; SciPy t(5).stats(moments='k') {float(stats.t(5).stats(moments='k')):.1f}; "
             f"LM5 prints 9 for t_5 (lm05.md:342)")

# ------------------------------------------------------------------ tail table, both tails
LV = [Fraction(k, 100) for k in range(2, 11)]
put("z_tab", ", ".join(f"{zx(float(x)):.6f}" for x in LV))
for x in LV:
    same((-100 * float(x) - 0.0625) / 1.20836, ".3f", format(zx(float(x)), ".3f"))
put("norm_tab", ", ".join(f"{e_norm(-float(x)):.6g}" for x in LV))
put("k_tab", ", ".join(f"{e_k(-float(x)):.6g}" for x in LV))
put("ml_tab", ", ".join(f"{e_ml(-float(x)):.6g}" for x in LV))
put("act_tab", ", ".join(str(le(x)) for x in LV))
same_list([e_norm(-float(x)) for x in LV], sig3, "257, 32.9, 2.26, 0.0817, 0.00153, 1.5e-05, 7.4e-08, 1.9e-10, 2.4e-13")
same_list([e_norm_p(-float(x)) for x in LV], sig3, "257, 32.9, 2.26, 0.0817, 0.00153, 1.5e-05, 7.4e-08, 1.9e-10, 2.4e-13")
same_list([e_k(-float(x)) for x in LV], sig3, "232, 64.3, 21.2, 8.17, 3.59, 1.75, 0.926, 0.524, 0.313")
same_list([e_k_p(-float(x)) for x in LV], sig3, "232, 64.3, 21.2, 8.17, 3.59, 1.75, 0.926, 0.524, 0.313")
same_list([e_ml(-float(x)) for x in LV], sig3, "210, 79.0, 36.6, 19.6, 11.6, 7.41, 5.00, 3.52, 2.57")
same_list([e_ml_p(-float(x)) for x in LV], sig3, "210, 79.0, 36.6, 19.6, 11.6, 7.41, 5.00, 3.52, 2.57")
same(1.2084 * math.sqrt(3.14 / 5.14), ".3f", "0.944")
put("upper", f"+3%: {ge(Fraction(3, 100))}, normal {T * float(stats.norm.sf((0.03 - Rbar) / s)):.4f}, ML "
             f"{T * float(stats.t.sf(0.03, nu_m, loc_m, sc_m)):.4f}; +5%: {ge(Fraction(5, 100))}, normal "
             f"{T * float(stats.norm.sf((0.05 - Rbar) / s)):.6f}, ML {T * float(stats.t.sf(0.05, nu_m, loc_m, sc_m)):.4f}")
same(5849 * float(stats.norm.sf((3 - 0.0625) / 1.2084)), ".1f", "44.0")
same(5849 * float(stats.norm.sf((5 - 0.0625) / 1.2084)), ".3f", "0.128")
same(5849 * float(stats.t.sf((3 - 0.0997) / 0.7761, 3.065)), ".1f", "94.2")
same(5849 * float(stats.t.sf((5 - 0.0997) / 0.7761, 3.065)), ".1f", "22.0")

# ------------------------------------------------------------------ tail means, chords, limit regimes
tail = R[R <= -0.05 + EPS]
z5 = zx(0.05)
num = integrate.quad(lambda x: x * float(stats.t.pdf(x, nu_m, loc_m, sc_m)), -np.inf, -0.05)[0]
put("tailmean", f"data {pct(float(tail.mean()), 4)}; normal (5.11) "
                f"{pct(Rbar - s * float(stats.norm.pdf(z5) / stats.norm.cdf(z5)), 4)}; ML t "
                f"{pct(num / float(stats.t.cdf(-0.05, nu_m, loc_m, sc_m)), 4)}")


def chord(n1: float, n2: float, x1: float, x2: float) -> float:
    return math.log(n1 / n2) / math.log(x2 / x1)


cnt = {k: le(Fraction(k, 100)) for k in range(2, 7)}
adj = [chord(cnt[k], cnt[k + 1], k, k + 1) for k in range(2, 6)]          # adjacent levels, one point apart
allc = {(i, j): chord(cnt[i], cnt[j], i, j) for i in range(2, 7) for j in range(i + 1, 7)}
lo_p, hi_p = min(allc, key=lambda k: allc[k]), max(allc, key=lambda k: allc[k])
assert all(a < b for a, b in itertools.pairwise(adj))                      # the chord rises with the level
put("chords", f"counts at 2%..6%: {', '.join(str(cnt[k]) for k in range(2, 7))}; adjacent: "
              + ", ".join(f"{k}%->{k + 1}% {v:.6f}" for k, v in zip(range(2, 6), adj))
              + f"; all ten pairs from {allc[lo_p]:.6f} ({lo_p[0]}%->{lo_p[1]}%) to {allc[hi_p]:.6f} "
              f"({hi_p[0]}%->{hi_p[1]}%); 2%->4% {allc[2, 4]:.6f}; 3%->6% {allc[3, 6]:.6f}; 4%->6% {allc[4, 6]:.6f}; "
              f"2%->6% {allc[2, 6]:.6f}")
same_list(adj, lambda v: f"{v:.2f}", "2.09, 3.12, 4.82, 5.03")
same_list([allc[2, 4], allc[3, 6], allc[4, 6], allc[2, 6]], lambda v: f"{v:.2f}", "2.52, 4.17, 4.91, 3.40")
# P10: the 2%->6% chord is the log-length-weighted mean of 2%->4% and 4%->6%
assert abs(allc[2, 6] - (allc[2, 4] * math.log(2) + allc[4, 6] * math.log(1.5)) / math.log(3)) < 1e-12
put("mchords", f"3%->6%: normal {chord(e_norm(-0.03), e_norm(-0.06), 3, 6):.6f}; ML t "
               f"{chord(e_ml(-0.03), e_ml(-0.06), 3, 6):.6f}; kurtosis-fit t {chord(e_k(-0.03), e_k(-0.06), 3, 6):.6f}")
pre = np.array([d < LIMIT_CHANGE for d in dates])
put("lim7", f"before {LIMIT_CHANGE}: min {pct(float(R[pre].min()), 4)} ({dates[int(np.argmin(np.where(pre, R, 1)))]}), "
            f"max {pct(float(R[pre].max()), 4)} ({dates[int(np.argmax(np.where(pre, R, -1)))]})")

rows, x9 = [], []
for name, msk in (("full", np.ones(T, dtype=bool)), ("7% limit", pre), ("10% limit", ~pre)):
    x = R[msk]
    sd_r, ek_, nu_r, q1 = float(x.std()), float(stats.kurtosis(x)), float(stats.t.fit(x)[0]), emp("0.01", x)[1]
    c3 = le(Fraction(3, 100), x)
    rows.append(f"{name}: T {len(x)} ({dates[int(np.argmax(msk))]} .. {dates[len(msk) - 1 - int(np.argmax(msk[::-1]))]}), "
                f"s {pct(sd_r, 4)}, excess kurtosis {ek_:.4f}, nu by kurtosis {4 + 6 / ek_:.4f}, ML nu "
                f"{nu_r:.4f}, 1% quantile {pct(q1, 4)}, <= -3% {c3} ({1000 * c3 / len(x):.4f} per 1,000)")
    x9.append(f"{len(x):,}, {100 * sd_r:.3f}, {ek_:.2f}, {4 + 6 / ek_:.2f}, {nu_r:.3f}, {100 * q1:.3f}, "
              f"{1000 * c3 / len(x):.1f}")
put("regimes", "; ".join(rows))
assert " / ".join(x9) == ("5,849, 1.208, 5.27, 5.14, 3.065, -3.567, 18.5 / 3,077, 1.257, 3.39, 5.77, 2.990, -3.621, "
                          "23.4 / 2,772, 1.152, 8.07, 4.74, 3.237, -3.467, 13.0"), x9
same_list([var_m / lam, *rr], lambda v: f"{v:.2f}", "3.02, 2.95, 3.01")

i7 = dates.index("2025-04-07")
eve, aft = R[:i7], R[: i7 + 1]
put("oneday", f"returns to {dates[i7 - 1]} ({len(eve)}) then to 2025-04-07 ({len(aft)}): excess kurtosis "
              f"{float(stats.kurtosis(eve)):.4f} -> {float(stats.kurtosis(aft)):.4f}; 1% quantile "
              f"{pct(emp('0.01', eve)[1], 4)} -> {pct(emp('0.01', aft)[1], 4)}; <= -3% {le(Fraction(3, 100), eve)} -> "
              f"{le(Fraction(3, 100), aft)}; whole sample without 2025-04-07: {float(stats.kurtosis(np.delete(R, i7))):.4f}")
dev = R - Rbar
top4 = np.argsort(-np.abs(dev), kind="stable")[:4]
put("four", f"without the four largest |R - Rbar| ({', '.join(dates[int(i)] for i in top4)}): "
            f"{float(stats.kurtosis(np.delete(R, top4))):.4f}")
top10 = np.argsort(-(dev**4), kind="stable")[:10]
put("ten", f"{pct(float((dev[top10] ** 4).sum() / (dev**4).sum()), 4)} of sum (R - Rbar)^4; "
           f"{pct(float((dev[top10] ** 2).sum() / (dev**2).sum()), 4)} of sum (R - Rbar)^2")

# ------------------------------------------------------------------ Python facts
loc_n, sc_n = (float(v) for v in stats.norm.fit(R))
put("normfit", f"norm.fit - (Rbar, s): {loc_n - Rbar:.3e}, {sc_n - s:.3e}")
put("median", f"#{(T + 1) // 2} {pct(float(srt[(T - 1) // 2]), 4)}")

# ------------------------------------------------------------------ earlier modules' printed values
put("lm4_196", "printed in lm04.md:541: 1.96, the value a standard normal variable exceeds with probability 2.5%")
put("lm5_case", "printed in lm05.md:35 (0.058 days expected) and lm05.md:53 (9 days actual)")
put("lm5_kurt", "printed in lm05.md:367: 8.12; 7.05 without 7 April 2025; 3.85 without the four largest moves; "
                "5.84 -> 7.63")
put("lm5_ten", "printed in lm05.md:369: 62.8% of sum (R - mu)^4, 14.1% of sum (R - mu)^2")
put("lm5_lit", "printed in lm05.md:350: tail index of most return series between 2 and 5 (Cont 2001); "
               "alpha about 3 for index returns (Gopikrishnan et al. 1999)")

# the anchors in the order of their IDs, A15-01, A15-02, ... (the order in which the brief first quotes them)
ORDER = ["big", "skew", "T", "years", "blocks", "months", "regimes", "extremes", "Rbar", "s", "norm5", "cnt5",
         "mlfit", "ml5", "lam", "var_m", "ratio", "mon8", "lm5_case", "lm4_196", "bin_mv", "p_hat", "sig15",
         "act_tab", "norm_annual", "kfit", "ml_tab", "t_mom", "signs", "dep_var", "blk_mv", "mon_exp", "rbar",
         "dlogn5", "norm_tab", "blk_obs", "blk_exp", "mon_obs", "qq", "muX", "logn_mom", "logn_q", "emp_med_g",
         "z_tab", "k_tab", "lm5_lit", "chords", "reg_ratio", "exk", "empq", "normq", "mlq", "annual_means",
         "normfit", "mlsd", "bin_tails", "rare", "limit", "pois612", "unequal", "phiinv", "annual", "ploss",
         "lm17", "gamma", "c_nu", "median", "mchords", "oneday", "four", "ten", "lm5_kurt", "lm5_ten", "tailmean",
         "p5gap", "upper", "lim7"]

if __name__ == "__main__":
    assert sorted(ORDER) == sorted(VALUES), set(ORDER) ^ set(VALUES)
    for n, key in enumerate(ORDER, 1):
        print(f"A15-{n:02d} {VALUES[key]}")
