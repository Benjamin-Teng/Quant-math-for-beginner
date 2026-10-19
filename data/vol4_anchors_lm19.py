"""LM19 anchors (Descriptive Statistics of Returns): every number the Stage 1 brief quotes.

Reads TR23 from data/processed/vol3_taiex.parquet (columns date, tr, price, R, Rp; R is the total-return index's
simple daily return, null on the first row; built and checked by data/vol3_series.py, which must be run first). It
reads nothing else and writes nothing.

Conventions.
- Samples (one per statistic, named in every line): TR23, the 5,849 returns 2003-01-03 -> 2026-10-08; "2003-2025",
  its 5,664 log returns dated 2003-01-03 -> 2025-12-31 (calendar years 2003-2025, 2003 from its first close,
  2 January 2003); the two limit regimes, returns dated before 2015-06-01 (3,077) and from it (2,772). TR23's 23
  Saturday sessions (2006-2018) stay in every sample and every group.
- Return type: one-day statistics on simple returns R; sums over days, autocorrelations and variance ratios on log
  returns r = ln(1 + R) (|r| and r^2 for the absolute and squared series).
- Divisors: means, s, central moments, autocovariances and every standard deviation of period sums divide by the
  number of terms (s, ddof=0); s_u divides by T - 1 (ddof=1); the adjusted skewness and kurtosis are SciPy's
  bias=False values, checked against their closed forms. Skewness and kurtosis use divisor-T central moments
  (scipy.stats defaults); "excess kurtosis" is Kurt - 3.
- Quantiles: every quantile and every median, of data or of computed values, is the book's quantile function
  F^-1(u) = x_(ceil(un)) (np.quantile method="inverted_cdf"): the median med = F^-1(1/2), the median absolute
  deviation MAD = median of |R - med| (the same rule on |R - med|), a 246-day window's median and quartiles, and the
  median of the 246 grids. IQR = F^-1(0.75) - F^-1(0.25). The 5% trimmed mean drops the j0 = floor(0.05 T) smallest
  and j0 largest returns.
- Normal-equivalent scales use the exact constants: "1.4826 MAD" is MAD / Phi^-1(0.75) and "IQR/1.349" is
  IQR / (2 Phi^-1(0.75)); the labels show the constants rounded.
- Autocorrelation (statsmodels' acf convention): rho_k = gamma_k / gamma_0, gamma_k = (1/T) sum_{t>k} (x_t - xbar)
  (x_{t-k} - xbar), with the full-sample mean xbar and divisor T in numerator and denominator. The iid band is
  +-1.96/sqrt(T). The robust standard error of rho_1 is HC0-type (White), evaluated under rho_1 = 0.
- Variance ratios of m-day log-return sums r_t^(m) = r_{t-m+1} + ... + r_t: VR(m) is the overlapping estimator
  [(1/(T-m+1)) sum over all T-m+1 windows of (r^(m) - m rbar)^2] / (m s_r^2), the book's one variance ratio
  (AUTHORING 6); the non-overlapping VR_n(m) skips the first o returns (0 <= o < m) and uses the floor((T-o)/m)
  consecutive blocks that follow, centred at m rbar of the whole sample, divisor the number of blocks; the identity
  column 1 + 2 sum_{k<m} (1 - k/m) rho_k is (19.7) evaluated with the sample rho_k. Under iid returns the overlapping
  numerator has expectation m sigma^2 (1 - m/T) and s_r^2 has sigma^2 (1 - 1/T), so VR(m)'s iid factor is
  (1 - m/T)/(1 - 1/T). A "one-year standard deviation from blocks" is the standard deviation of the block sums about
  their own mean, divisor the number of blocks (LM15's convention for the 23 calendar years).
- Annualization: TR23's A = T / years = 246.12 (years = calendar days between the first and last close / 365.25); on
  2003-2025 a year is m = 246 sessions (LM17's round(A)), weeks are ISO calendar weeks and a year has 1,185 / 23
  of them, months are calendar months (12 a year). Sharpe ratios use r_f = 0.
- Counting: counts on returns use exact Fraction arithmetic on the two-decimal closes; counts on computed statistics
  use the book's guard (>= x - 1e-12, <= x + 1e-12) and report the smallest margin. Relative changes are
  (new - old) / |old|.
- Seeds: one simulated experiment, e = 1 (the iid check of VR(m)'s expectation): rng =
  np.random.default_rng([1, 20261011]) created once at its start, 10,000 samples of T = 5,849 iid standard normal
  log returns, one standard_normal(T) call per sample; the standard error of a mean of n draws is their standard
  deviation (divisor n) over sqrt(n), as LM18.
- Rounding: every put() passes each value the brief prints from that line, at the precision it prints it; the line
  ends with "[near boundary ...]" listing each one within a tenth of a unit of its last printed digit from a
  rounding boundary, with its distance in units truncated to four decimals.
- Numbers printed by earlier modules are echoed with file:line; LM14's, LM15's and LM17's are recomputed here.

Prints one line per anchor, "A19-NN <value>", in ID order, and writes nothing.

Run:  PYTHONUTF8=1 uv run python data/vol4_anchors_lm19.py [repository root]
"""
import datetime as dt
import sys
from fractions import Fraction
from math import ceil, floor, log, pi, sqrt
from pathlib import Path

import numpy as np
import polars as pl
from numpy.lib.stride_tricks import sliding_window_view
from scipy import stats
from statsmodels.stats.stattools import robust_kurtosis, robust_skewness
from statsmodels.tsa.stattools import acf as sm_acf

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
EPS = 1e-12
LIMIT_SWITCH = "2015-06-01"
Z75 = float(stats.norm.ppf(0.75))
OUT: list[str] = []
Check = tuple[float, int]


def put(value: str, *checks: Check) -> None:
    """Append one anchor line. Each check (v, d) is a value printed at d decimals; it is flagged when it lies within a
    tenth of a unit of the last printed digit from a rounding boundary."""
    flags = []
    for v, d in checks:
        x = abs(v) * 10**d
        units = abs((x - floor(x)) - 0.5)
        if units < 0.1:
            flags.append(f"{v:.{d + 4}f} at {d} dp, {floor(units * 1e4) / 1e4:.4f} unit from a boundary")
    tail = f" [near boundary: {'; '.join(flags)}]" if flags else ""
    OUT.append(f"A19-{len(OUT) + 1:02d} {value}{tail}")


def qf(x: np.ndarray, u: float) -> float:
    """The book's quantile function, x_(ceil(un))."""
    return float(np.quantile(x, u, method="inverted_cdf"))


def mad(x: np.ndarray) -> float:
    med = qf(x, 0.5)
    return qf(np.abs(x - med), 0.5)


def trim(x: np.ndarray, j0: int) -> float:
    return float(np.sort(x)[j0 : len(x) - j0].mean())


def trim5(x: np.ndarray) -> float:
    return trim(x, floor(0.05 * len(x)))


def qskew(x: np.ndarray) -> float:
    q1, q2, q3 = qf(x, 0.25), qf(x, 0.5), qf(x, 0.75)
    return (q3 + q1 - 2 * q2) / (q3 - q1)


def okurt(x: np.ndarray) -> float:
    e = [qf(x, i / 8) for i in range(1, 8)]
    return ((e[6] - e[4]) + (e[2] - e[0])) / (e[5] - e[1])


def okurt_normal() -> float:
    z = [float(stats.norm.ppf(i / 8)) for i in range(1, 8)]
    return ((z[6] - z[4]) + (z[2] - z[0])) / (z[5] - z[1])


def skew_adj(x: np.ndarray) -> float:
    n = len(x)
    return sqrt(n * (n - 1)) / (n - 2) * float(stats.skew(x))


def exk_adj(x: np.ndarray) -> float:
    n = len(x)
    return (n - 1) / ((n - 2) * (n - 3)) * ((n + 1) * float(stats.kurtosis(x)) + 6)


PCT = ("mean", "median", "trim5", "s", "s_u", "meanAD", "1.4826MAD", "IQR/1.349")
X2_DEC = {"mean": 4, "median": 4, "trim5": 4, "s": 3, "s_u": 3, "meanAD": 3, "1.4826MAD": 3, "IQR/1.349": 3,
          "skew": 4, "skew_adj": 4, "qskew": 3, "exkurt": 3, "exkurt_adj": 3, "okurt": 3}


def summary(x: np.ndarray) -> dict[str, float]:
    return {
        "mean": float(x.mean()), "median": qf(x, 0.5), "trim5": trim5(x), "s": float(x.std(ddof=0)),
        "s_u": float(x.std(ddof=1)), "meanAD": float(np.abs(x - x.mean()).mean()), "1.4826MAD": mad(x) / Z75,
        "IQR/1.349": (qf(x, 0.75) - qf(x, 0.25)) / (2 * Z75), "skew": float(stats.skew(x)), "skew_adj": skew_adj(x),
        "qskew": qskew(x), "exkurt": float(stats.kurtosis(x)), "exkurt_adj": exk_adj(x), "okurt": okurt(x),
    }


def fmt_summary(d: dict[str, float]) -> str:
    return "; ".join(f"{k} {100 * v:.6f}%" if k in PCT else f"{k} {v:.6f}" for k, v in d.items())


def x2_checks(d: dict[str, float]) -> list[Check]:
    """X2 prints location to 4 decimals of a percent, scale to 3, skewness to 4, the quantile measures and kurtosis to 3."""
    return [(100 * v if k in PCT else v, X2_DEC[k]) for k, v in d.items()]


def acf(x: np.ndarray, kmax: int) -> np.ndarray:
    """rho_1 .. rho_kmax: full-sample mean, divisor T in numerator and denominator."""
    xc = x - x.mean()
    g0 = float((xc * xc).sum())
    return np.array([float((xc[k:] * xc[:-k]).sum()) / g0 for k in range(1, kmax + 1)])


def sums(x: np.ndarray, m: int) -> np.ndarray:
    """All len(x) - m + 1 overlapping m-day sums."""
    c = np.concatenate([[0.0], np.cumsum(x)])
    return c[m:] - c[:-m]


def vr_o(x: np.ndarray, m: int) -> float:
    """VR(m), the overlapping estimator (19.8), centred at m xbar."""
    s_m = sums(x, m)
    return float(((s_m - m * x.mean()) ** 2).mean() / (m * x.var(ddof=0)))


def blocks(x: np.ndarray, m: int, off: int) -> np.ndarray:
    """Sums of the floor((len(x) - off)/m) consecutive m-day blocks after skipping the first off returns."""
    y = x[off:]
    nb = len(y) // m
    return y[: nb * m].reshape(nb, m).sum(axis=1)


def vr_n(x: np.ndarray, m: int, off: int = 0) -> float:
    b = blocks(x, m, off)
    return float(((b - m * x.mean()) ** 2).mean() / (m * x.var(ddof=0)))


def vr_plug(rho: np.ndarray, m: int) -> float:
    """(19.7) evaluated with sample autocorrelations: the identity column."""
    k = np.arange(1, m)
    return float(1 + 2 * ((1 - k / m) * rho[: m - 1]).sum())


def iid_factor(n: int, m: int) -> float:
    return (1 - m / n) / (1 - 1 / n)


# ---------------------------------------------------------------- data
df = pl.read_parquet(PROC / "vol3_taiex.parquet").sort("date")
dates_all = [str(d) for d in df["date"].to_list()]
tr = df["tr"].to_numpy()
R = df["R"].to_numpy()[1:]
dates = dates_all[1:]
assert df["R"][0] is None and len(set(dates_all)) == len(dates_all)
T = len(R)
r = np.log1p(R)
days = (df["date"][-1] - df["date"][0]).days
years = days / 365.25
A = T / years
trf = [Fraction(str(x)) for x in tr]
RF = [trf[i] / trf[i - 1] - 1 for i in range(1, len(trf))]
assert all(abs(float(a) - b) < 1e-15 for a, b in zip(RF, R))
dates_np = np.array(dates)
in25 = dates_np <= "2025-12-31"
r25 = r[in25]
T25 = len(r25)
pre = dates_np < LIMIT_SWITCH
year_end: dict[str, int] = {}
for i, d in enumerate(dates_all):
    year_end[d[:4]] = i
ann = np.array([log(tr[year_end[str(y)]] / tr[0 if y == 2003 else year_end[str(y - 1)]]) for y in range(2003, 2026)])
per_year = [year_end[str(y)] - (0 if y == 2003 else year_end[str(y - 1)]) for y in range(2003, 2026)]

# ---------------------------------------------------------------- data role
put(f"{len(dates_all)} closes, {dates_all[0]} -> {dates_all[-1]}")                                   # 01
put(f"{T} returns, {dates[0]} -> {dates[-1]}")                                                       # 02
put(f"{days} days; {years:.7f} years", (years, 4))                                                   # 03
put(f"{A:.6f}", (A, 2))                                                                              # 04
n_distinct = len(set(RF))
n_zero = sum(x == 0 for x in RF)
put(f"distinct returns {n_distinct} of {T}; exact zeros {n_zero} (Fraction on the closes)")         # 05
put(f"{T25} log returns {dates[0]} -> {dates_np[in25][-1]}; sessions per calendar year {min(per_year)}-{max(per_year)},"
    f" mean {T25 / 23:.5f}; returns dated 2026: {T - T25}", (T25 / 23, 2))                           # 06
put(f"before {LIMIT_SWITCH}: {int(pre.sum())}; from it: {int((~pre).sum())}")                        # 07
d25 = [dt.date.fromisoformat(d) for d in dates_np[in25]]
wk_key = [x.isocalendar()[:2] for x in d25]
mo_key = [(x.year, x.month) for x in d25]


def period_sums(keys: list[tuple[int, int]], x: np.ndarray) -> tuple[np.ndarray, list[int]]:
    order: dict[tuple[int, int], list[int]] = {}
    for i, k in enumerate(keys):
        order.setdefault(k, []).append(i)
    vals = np.array([x[v].sum() for v in order.values()])
    return vals, [len(v) for v in order.values()]


wk, wk_n = period_sums(wk_key, r25)
mo, mo_n = period_sums(mo_key, r25)
wpy = len(wk) / 23
put(f"weeks {len(wk)} ({min(wk_n)}-{max(wk_n)} sessions), {wpy:.5f} a year; months {len(mo)} ({min(mo_n)}-{max(mo_n)}"
    f" sessions); years 23 ({min(per_year)}-{max(per_year)} sessions)", (wpy, 2))                    # 08

# ---------------------------------------------------------------- case (2003-2025 log returns)
sr25 = float(r25.std(ddof=0))
v_day = sqrt(246) * sr25
put(f"s_r (divisor {T25}) {100 * sr25:.7f}%; sqrt(246) s_r {100 * v_day:.5f}%",
    (100 * sr25, 5), (100 * v_day, 3), (100 * v_day, 2))                                             # 09
sd_wk, sd_mo = float(wk.std(ddof=0)), float(mo.std(ddof=0))
v_wk = sd_wk * sqrt(wpy)
put(f"weekly s {100 * sd_wk:.6f}% x sqrt({wpy:.5f}) = {100 * v_wk:.5f}%", (100 * sd_wk, 4), (100 * v_wk, 2))  # 10
v_mo = sd_mo * sqrt(12)
put(f"monthly s {100 * sd_mo:.6f}% x sqrt(12) = {100 * v_mo:.5f}%", (100 * sd_mo, 4), (100 * v_mo, 2))  # 11
v_yr = float(ann.std(ddof=0))
m246 = 246 * float(r25.mean())
put(f"calendar years: mean {ann.mean():.7f}, s (divisor 23) {v_yr:.7f}; 246 rbar' {m246:.7f}",
    (100 * float(ann.mean()), 3), (100 * v_yr, 3), (100 * v_yr, 2), (100 * m246, 3))                # 12
vr_need = (v_yr / v_day) ** 2
put(f"(s_year / (sqrt(246) s_r))^2 = {vr_need:.6f}", (vr_need, 2))                                   # 13

# ---------------------------------------------------------------- section 2: location
wdates = ["2025-04-07", "2025-04-08", "2025-04-09", "2025-04-10", "2025-04-11"]
iw = [dates.index(d) for d in wdates]
wF = [RF[i] for i in iw]
wR = np.array([float(x) for x in wF])
all_wk: dict[tuple[int, int], list[int]] = {}
for i, d in enumerate(dates):
    all_wk.setdefault(dt.date.fromisoformat(d).isocalendar()[:2], []).append(i)
wk_sd = sorted(((float(R[v].std(ddof=0)), k) for k, v in all_wk.items()), reverse=True)
rank = [k for _, k in wk_sd].index(dt.date(2025, 4, 7).isocalendar()[:2]) + 1
w_s = float(wR.std(ddof=0))
put("returns " + ", ".join(f"{100 * float(x):.6f}%" for x in wF)
    + f" (Fraction); week's s {100 * w_s:.5f}%, rank {rank} of {len(all_wk)} ISO weeks by s",
    *[(100 * float(x), 4) for x in wF], (100 * float(wF[0]), 2), (100 * w_s, 2))                     # 14
w_mean, w_med, w_trim = float(wR.mean()), qf(wR, 0.5), trim(wR, 1)
put(f"mean {100 * w_mean:.6f}%; median {100 * w_med:.6f}%; 20% trimmed {100 * w_trim:.6f}%",
    (100 * w_mean, 3), (100 * w_med, 3), (100 * w_trim, 3))                                          # 15
wG = float(np.prod(1 + wR))
w_RG, w_rbar = wG ** 0.2 - 1, float(np.log1p(wR).mean())
put(f"G {wG:.7f} ({100 * (wG - 1):.5f}%); R_G {100 * w_RG:.6f}%; rbar {100 * w_rbar:.6f}%",
    (wG, 4), (100 * (wG - 1), 2), (100 * w_RG, 3), (100 * w_rbar, 3))                                # 16
wR2 = wR.copy()
wR2[0] = wR[0] - 0.10
k_mean, k_med, k_trim = float(wR2.mean()), qf(wR2, 0.5), trim(wR2, 1)
put(f"with {100 * wR2[0]:.4f}% for {100 * wR[0]:.4f}%: mean {100 * k_mean:.6f}%; median {100 * k_med:.6f}%;"
    f" 20% trimmed {100 * k_trim:.6f}%",
    (100 * float(wR2[0]), 2), (100 * k_mean, 3), (100 * k_med, 3), (100 * k_trim, 3))                # 17
full = summary(R)
RG = float((tr[-1] / tr[0]) ** (1 / T) - 1)
rbar = float(r.mean())
i_med = int(np.argsort(R)[ceil(0.5 * T) - 1])
put(f"Rbar {100 * full['mean']:.7f}%; median R_({ceil(0.5 * T)}) {100 * full['median']:.7f}% ({dates[i_med]});"
    f" 5% trimmed (j0 = {floor(0.05 * T)}) {100 * full['trim5']:.7f}%; R_G {100 * RG:.7f}%; rbar {100 * rbar:.7f}%",
    (100 * full["mean"], 4), (100 * full["median"], 4), (100 * full["trim5"], 4), (100 * RG, 5), (100 * RG, 6),
    (100 * rbar, 5))                                                                                 # 18

# ---------------------------------------------------------------- section 3: dispersion
w_su = float(wR.std(ddof=1))
w_mad = mad(wR)
w_mad_mean = float(np.abs(wR - w_mean).mean())
put(f"week: s {100 * w_s:.6f}%; s_u {100 * w_su:.6f}%; ratio {w_su / w_s:.6f}; mean abs dev "
    f"{100 * w_mad_mean:.6f}%; MAD {100 * w_mad:.6f}%",
    (100 * w_s, 3), (100 * w_su, 3), (w_su / w_s, 3), (100 * w_mad_mean, 3), (100 * w_mad, 3))       # 19
put(f"s {100 * full['s']:.7f}%; s_u {100 * full['s_u']:.7f}%; ratio {full['s_u'] / full['s']:.9f}",
    (100 * full["s"], 4), (100 * full["s_u"], 4), (full["s_u"] / full["s"], 7),
    (100 * full["s"], 3), (100 * full["s_u"], 3))                                                    # 20
put(f"mean abs dev {100 * full['meanAD']:.7f}%; / s {full['meanAD'] / full['s']:.6f}; sqrt(2/pi) {sqrt(2 / pi):.7f}",
    (100 * full["meanAD"], 3), (full["meanAD"] / full["s"], 3), (sqrt(2 / pi), 3))                   # 21
put(f"Phi^-1(0.75) {Z75:.7f}; 1/Phi^-1(0.75) {1 / Z75:.7f}; 2 Phi^-1(0.75) {2 * Z75:.7f}",
    (Z75, 4), (1 / Z75, 4), (2 * Z75, 3))                                                            # 22
q1, q3, mad_full = qf(R, 0.25), qf(R, 0.75), mad(R)
put(f"R_({ceil(0.25 * T)}) {100 * q1:.6f}%; R_({ceil(0.75 * T)}) {100 * q3:.6f}%; IQR {100 * (q3 - q1):.6f}%;"
    f" IQR/(2 Phi^-1(0.75)) {100 * full['IQR/1.349']:.7f}%; MAD {100 * mad_full:.7f}%; MAD/Phi^-1(0.75) "
    f"{100 * full['1.4826MAD']:.7f}%",
    (100 * q1, 3), (100 * q3, 3), (100 * (q3 - q1), 3), (100 * full["IQR/1.349"], 3), (100 * mad_full, 3),
    (100 * mad_full, 4), (100 * full["1.4826MAD"], 3))                                               # 23
an_s, an_m, an_i = sqrt(A) * full["s"], sqrt(A) * full["1.4826MAD"], sqrt(A) * full["IQR/1.349"]
put(f"sqrt(A) s {100 * an_s:.5f}%; sqrt(A) 1.4826 MAD {100 * an_m:.5f}%; sqrt(A) IQR/1.349 {100 * an_i:.5f}%;"
    f" s over each {an_s / an_m:.5f}, {an_s / an_i:.5f}",
    (100 * an_s, 2), (100 * an_m, 1), (100 * an_i, 1), (an_s / an_m, 2), (an_s / an_i, 2))           # 24
W = sliding_window_view(R, 246)
srt = np.sort(W, axis=1)
med_w = srt[:, 122]
madw = np.sort(np.abs(W - med_w[:, None]), axis=1)[:, 122]
roll = {"s": sqrt(A) * W.std(axis=1, ddof=0), "MAD": sqrt(A) * madw / Z75,
        "IQR": sqrt(A) * (srt[:, 184] - srt[:, 61]) / (2 * Z75)}
ends = dates_np[245:]
txt = []
roll_checks: list[Check] = []
for k, v in roll.items():
    txt.append(f"{k} max {100 * v.max():.4f}% ({ends[v.argmax()]}) min {100 * v.min():.4f}% ({ends[v.argmin()]})"
               f" end {100 * v[-1]:.4f}%")
    roll_checks += [(100 * float(v.max()), 1), (100 * float(v.min()), 1), (100 * float(v[-1]), 1)]
ratio = roll["s"] / roll["MAD"]
put(f"{len(W)} windows ending {ends[0]} -> {ends[-1]}: " + "; ".join(txt)
    + f"; s / (1.4826 MAD) max {ratio.max():.5f} ({ends[ratio.argmax()]}) min {ratio.min():.5f} ({ends[ratio.argmin()]})",
    *roll_checks, (float(ratio.max()), 2), (float(ratio.min()), 2))                                  # 25
medF = sorted(RF)[ceil(0.5 * T) - 1]
devF = sorted(abs(x - medF) for x in RF)
madF = devF[ceil(0.5 * T) - 1]
n_in = sum(abs(x - medF) <= madF for x in RF)
put(f"days with |R - median| <= MAD: {n_in} (Fraction); ties among |R - median|: {len(devF) - len(set(devF))};"
    f" exact and float MAD agree within 1e-15: {abs(float(madF) - mad_full) < 1e-15}")              # 26

# ---------------------------------------------------------------- section 4: shape
sk_b, ek_b = float(stats.skew(R, bias=False)), float(stats.kurtosis(R, bias=False))
put(f"skew {full['skew']:.7f}, adjusted {full['skew_adj']:.7f}; excess kurtosis {full['exkurt']:.7f}, adjusted "
    f"{full['exkurt_adj']:.7f}; closed forms agree with SciPy bias=False within 1e-13: "
    f"{abs(full['skew_adj'] - sk_b) < 1e-13}, {abs(full['exkurt_adj'] - ek_b) < 1e-13}",
    (full["skew"], 3), (full["skew"], 4), (full["skew_adj"], 4), (full["exkurt"], 2), (full["exkurt"], 3),
    (full["exkurt_adj"], 3))                                                                         # 27
sk23, ek23 = float(stats.skew(ann)), float(stats.kurtosis(ann))
put(f"23 calendar-year log returns: skew {sk23:.6f}, adjusted {skew_adj(ann):.6f}; excess kurtosis "
    f"{ek23:.6f}, adjusted {exk_adj(ann):.6f}",
    (sk23, 2), (skew_adj(ann), 2), (ek23, 2), (exk_adj(ann), 2))                                     # 28
n50 = 2902
k50 = (n50 - 1) / ((n50 - 2) * (n50 - 3)) * ((n50 + 1) * 8.12 + 6)
put(f"LM4's 0050 8.12 (lm04.md:132) adjusted at T = {n50}: {k50:.5f}", (k50, 2))                     # 29
okn = okurt_normal()
sk_sm = robust_skewness(R)[1]
kr_sm = robust_kurtosis(R)[1]
put(f"quartile skewness {full['qskew']:.7f}; octile kurtosis {full['okurt']:.7f}, normal {okn:.7f}, excess "
    f"{full['okurt'] - okn:.7f}; statsmodels sk2 {float(sk_sm):.7f}, kr2 (excess) {float(kr_sm):.7f}",
    (full["qskew"], 3), (full["qskew"], 4), (full["okurt"], 3), (okn, 3), (full["okurt"] - okn, 3))  # 30
plus = summary(np.append(R, -0.10))
rel = {k: (plus[k] - full[k]) / abs(full[k]) for k in full}
REL_DEC = {"mean": 1, "median": 1, "trim5": 1, "s": 1, "1.4826MAD": 2, "IQR/1.349": 2, "skew": 0, "exkurt": 0,
           "qskew": 1, "okurt": 2}
put("one more -10% day (T+1): " + fmt_summary(plus) + "; relative changes "
    + ", ".join(f"{k} {100 * v:+.5f}%" for k, v in rel.items()),
    *x2_checks(plus), (plus["skew"], 3), (plus["exkurt"], 2),
    *[(100 * rel[k], d) for k, d in REL_DEC.items()])                                                # 31
reg7, reg10 = summary(R[pre]), summary(R[~pre])
put("7% regime: " + fmt_summary(reg7), *x2_checks(reg7), (reg7["exkurt"], 2))                         # 32
put("10% regime: " + fmt_summary(reg10), *x2_checks(reg10), (reg10["exkurt"], 2))                     # 33
put(f"normal with TR23's mean and s: mean = median = trimmed {100 * full['mean']:.6f}%; mean abs dev "
    f"{100 * sqrt(2 / pi) * full['s']:.6f}%; robust scales = s {100 * full['s']:.6f}%; skewness 0; quartile "
    f"skewness 0; excess kurtosis 0; octile kurtosis {okn:.7f}",
    (100 * full["mean"], 4), (100 * sqrt(2 / pi) * full["s"], 3), (100 * full["s"], 3), (okn, 3))    # 34

# ---------------------------------------------------------------- section 5: autocorrelation
alt = np.array([1.0, -1.0, 1.0, -1.0, 1.0, -1.0])
a1 = float(acf(alt, 1)[0])
put(f"alternating six: rho_1 {a1:.7f} = {Fraction(-5, 6)}", (a1, 3))                                  # 35
w_rho, w_pair = float(acf(wR, 1)[0]), float(np.corrcoef(wR[:-1], wR[1:])[0, 1])
put(f"tariff week R: rho_1 {w_rho:.6f}; correlation of the 4 pairs (R_t, R_t+1) {w_pair:.6f}",
    (w_rho, 3), (w_pair, 3))                                                                          # 36
band, band25 = 1.96 / sqrt(T), 1.96 / sqrt(T25)
put(f"1.96/sqrt(T) {band:.7f}; on 2003-2025 {band25:.7f}", (band, 4), (band, 5), (band25, 4))         # 37
rho_r, rho_a, rho_q = acf(r, 1230), acf(np.abs(r), 30), acf(r**2, 30)


def corr_pairs(a: np.ndarray, b: np.ndarray) -> float:
    a, b = a - a.mean(), b - b.mean()
    return float((a * b).mean() / sqrt(float((a * a).mean() * (b * b).mean())))


out_r = [(k + 1, rho_r[k]) for k in range(30) if abs(rho_r[k]) >= band - EPS]
marg = np.abs(np.abs(rho_r[:30]) - band)
k_close = int(marg.argmin())
pr1 = corr_pairs(r[:-1], r[1:])
put(f"r: rho_1 {rho_r[0]:.7f} (pairs {pr1:.8f}); outside the band {len(out_r)} of 30: "
    + ", ".join(f"{k} {v:.6f}" for k, v in out_r)
    + f"; closest to the band: lag {k_close + 1} {rho_r[k_close]:.7f} (margin {marg[k_close]:.1e}); X4 tooltips: all"
    " 30 lags checked at 5 dp",
    (float(rho_r[0]), 4), (pr1, 4), (float(rho_r[0]), 3), (pr1, 3), *[(float(v), 5) for v in rho_r[:30]])  # 38
ar = np.abs(r)
pa20 = corr_pairs(ar[:-20], ar[20:])
put(f"|r|: rho_1 {rho_a[0]:.7f}; rho_20 {rho_a[19]:.7f} (pairs {pa20:.7f}); min over 1-30 "
    f"{rho_a.min():.6f} (lag {int(rho_a.argmin()) + 1}); max {rho_a.max():.6f} (lag {int(rho_a.argmax()) + 1}); "
    f"outside the band {int((np.abs(rho_a) >= band - EPS).sum())} of 30; X4 tooltips: all 30 lags checked at 5 dp",
    (float(rho_a[0]), 3), (float(rho_a[19]), 4), (pa20, 4), (pa20, 3), (float(rho_a.min()), 3),
    (float(rho_a.max()), 3), *[(float(v), 5) for v in rho_a])                                        # 39
x2 = r**2 - (r**2).mean()
p3 = x2[3:] * x2[:-3]
i10 = dates.index("2025-04-10")
xa = ar - ar.mean()
pa3 = xa[3:] * xa[:-3]
sh_q, sh_a = float(p3[i10 - 3] / p3.sum()), float(pa3[i10 - 3] / pa3.sum())
put(f"r^2: rho_1..3 {rho_q[0]:.6f}, {rho_q[1]:.6f}, {rho_q[2]:.6f}; min over 1-30 {rho_q.min():.6f} (lag "
    f"{int(rho_q.argmin()) + 1}); outside the band {int((np.abs(rho_q) >= band - EPS).sum())} of 30; share of the lag-3 "
    f"sum from 2025-04-10 x 2025-04-07 {100 * sh_q:.5f}%; |r| rho_3 {rho_a[2]:.6f}, that pair's share "
    f"{100 * sh_a:.5f}%",
    (float(rho_q[0]), 3), (float(rho_q[1]), 3), (float(rho_q[2]), 3), (float(rho_q.min()), 3), (100 * sh_q, 1),
    (float(rho_a[2]), 3), (100 * sh_a, 1))                                                           # 40
xr = r - r.mean()
se_rob = sqrt(float(((xr[1:] * xr[:-1]) ** 2).sum())) / float((xr * xr).sum())
put(f"rho_1(r) standard errors: iid 1/sqrt(T) {1 / sqrt(T):.6f}; HC0-type robust {se_rob:.6f} (LM25's; not printed"
    " in LM19)", (1 / sqrt(T), 4))                                                                   # 41
reg = []
reg_checks: list[Check] = []
for lab, msk in (("7%", pre), ("10%", ~pre)):
    a_r, a_a = float(acf(r[msk], 1)[0]), float(acf(np.abs(r[msk]), 1)[0])
    reg.append(f"{lab}: rho_1(r) {a_r:.6f}, rho_1(|r|) {a_a:.6f}")
    reg_checks += [(a_r, 3), (a_a, 3)]
put("; ".join(reg), *reg_checks)                                                                      # 42
dmax = max(float(np.abs(sm_acf(x, nlags=30, fft=False)[1:] - acf(x, 30)).max()) for x in (r, ar, r**2))
put(f"statsmodels acf(x, nlags=30, fft=False) and the book's rho_k agree within 1e-15 for r, |r|, r^2: {dmax < 1e-15}")  # 43

# ---------------------------------------------------------------- section 6: variance ratios
put(f"VR(2): 1 + rho_1 {1 + rho_r[0]:.7f}; overlapping {vr_o(r, 2):.7f}", (1 + float(rho_r[0]), 4), (vr_o(r, 2), 4))  # 44
f16, f1 = 1 + 2 * 0.04 * 244 / 245, 1 + 2 * float(rho_r[0]) * 245 / 246
put(f"LM16's factor (lm16.md:623) 1 + 2(0.04)(244/245) = {f16:.7f}; TR23 lag 1 only at m = 246: "
    f"1 + 2 rho_1 (245/246) = {f1:.7f}", (f16, 4), (f1, 4))                                          # 45
offs246 = [vr_n(r, 246, o) for o in range(246)]
vo246, vp246 = vr_o(r, 246), vr_plug(rho_r, 246)
put(f"m = 246, TR23: identity column {vp246:.7f}; overlapping {vo246:.7f}; non-overlapping from the first "
    f"return {vr_n(r, 246):.7f} ({T // 246} blocks), over the 246 first returns {min(offs246):.6f} to {max(offs246):.6f}",
    (vp246, 3), (vo246, 3))                                                                          # 46
put(f"iid factor (1 - m/T)/(1 - 1/T): m = 246, T = {T}: {iid_factor(T, 246):.7f}; m = 1231: {iid_factor(T, 1231):.7f};"
    f" m = 246, T = {T25}: {iid_factor(T25, 246):.7f}",
    (iid_factor(T, 246), 3), (iid_factor(T, 1231), 3), (iid_factor(T25, 246), 3))                    # 47
# experiment 1: the iid expectation of the overlapping estimator
rng = np.random.default_rng([1, 20261011])
n_sim = 10_000
sim = np.empty((n_sim, 2))
for j in range(n_sim):
    z = rng.standard_normal(T)
    sim[j] = vr_o(z, 246), vr_o(z, 1231)
mc = sim.mean(axis=0)
mcse = sim.std(axis=0, ddof=0) / sqrt(n_sim)
put(f"e = 1, {n_sim} iid normal samples of T = {T}: mean VR(246) {mc[0]:.6f} +- {mcse[0]:.6f}, formula "
    f"{iid_factor(T, 246):.6f}; mean VR(1231) {mc[1]:.6f} +- {mcse[1]:.6f}, formula {iid_factor(T, 1231):.6f}",
    (float(mc[0]), 3), (float(mcse[0]), 3), (float(mc[1]), 3), (float(mcse[1]), 3))                  # 48
rows = []
x6_checks: list[Check] = []
for m in (2, 5, 20, 60, 246, 1231):
    o = [vr_n(r, m, k) for k in range(m)]
    vals = (vr_o(r, m), vr_plug(rho_r, m), vr_n(r, m), min(o), max(o), iid_factor(T, m))
    rows.append(f"m={m}: windows {T - m + 1}, blocks {T // m}, T/m {T / m:.4f}, overlapping {vals[0]:.6f}, identity "
                f"column {vals[1]:.6f}, non-overlapping first {vals[2]:.6f}, range {vals[3]:.6f}-{vals[4]:.6f}, "
                f"iid factor {vals[5]:.6f}")
    x6_checks += [(T / m, 2)] + [(v, 3) for v in vals]
put("; ".join(rows), *x6_checks)                                                                      # 49
s1231 = sums(r, 1231)
own = float(s1231.var(ddof=0)) / (1231 * float(r.var(ddof=0)))
cen = vr_o(r, 1231)
wts = np.convolve(np.ones(T - 1231 + 1), np.ones(1231)) / (T - 1231 + 1)
own_factor = (1231 - float((wts**2).sum())) / (1231 * (1 - 1 / T))
sd_own, sqm = float(s1231.std(ddof=0)), sqrt(1231) * float(r.std(ddof=0))
put(f"LM18's windows: sd of ln G about its own mean {sd_own:.6f}; sqrt(m) s_r {sqm:.6f}; own-mean ratio {own:.6f}"
    f" (iid factor {own_factor:.6f}; neither printed); VR(1231) {cen:.6f} (iid factor {iid_factor(T, 1231):.6f},"
    f" ratio {cen / iid_factor(T, 1231):.6f}); mean ln G {float(s1231.mean()):.6f} vs m rbar {1231 * rbar:.6f}",
    (sd_own, 3), (sqm, 3), (cen, 3), (cen / iid_factor(T, 1231), 2), (float(s1231.mean()), 3), (1231 * rbar, 3))  # 50
put(f"iid correlation of consecutive overlapping 246-day sums (m-1)/m {245 / 246:.6f}; T/m at 246 {T / 246:.4f},"
    f" at 1231 {T / 1231:.4f}", (245 / 246, 3), (T / 246, 1), (T / 1231, 2))                          # 51
vr_all = np.array([vr_o(r, m) for m in range(2, 1232)])
vr25_all = np.array([vr_o(r25, m) for m in range(2, 1232)])
mm = np.arange(2, 1232)
v492, v25_492, v25_1231 = vr_o(r, 492), vr_o(r25, 492), vr_o(r25, 1231)
put(f"TR23 VR(m), m = 2..1231: max {vr_all.max():.6f} at m = {int(mm[vr_all.argmax()])}; at 492 {v492:.6f};"
    f" min {vr_all.min():.6f} at m = {int(mm[vr_all.argmin()])}; first m below 1: {int(mm[np.argmax(vr_all < 1)])};"
    f" 2003-2025 VR at 492 {v25_492:.6f}, at 1231 {v25_1231:.6f}, max {vr25_all.max():.6f} at m ="
    f" {int(mm[vr25_all.argmax()])} (not printed)",
    (float(vr_all.max()), 3), (v492, 3), (float(vr_all.min()), 3), (v25_492, 3), (v25_1231, 3))      # 52
rho25 = acf(r25, 245)
v25 = vr_o(r25, 246)
vp25 = vr_plug(rho25, 246)
put(f"2003-2025, m = 246: VR {v25:.7f}; identity column {vp25:.7f}; divided by the iid factor "
    f"{v25 / iid_factor(T25, 246):.6f}; TR23 VR {vo246:.7f}",
    (v25, 4), (v25, 3), (vp25, 3), (v25 / iid_factor(T25, 246), 3), (vo246, 3))                      # 53

# ---------------------------------------------------------------- section 7: annualization
sr_R, sr_r = full["mean"] / full["s"], rbar / float(r.std(ddof=0))
s_r = float(r.std(ddof=0))
put(f"TR23: A Rbar {100 * A * full['mean']:.5f}%; A rbar {100 * A * rbar:.5f}%; A s^2 {A * full['s'] ** 2:.7f};"
    f" A s_r^2 {A * s_r**2:.7f}; s_r {100 * s_r:.6f}%; sqrt(A) s {100 * an_s:.5f}%; sqrt(A) s_r {100 * sqrt(A) * s_r:.5f}%;"
    f" SR(R) per day {sr_R:.7f}, x sqrt(A) {sqrt(A) * sr_R:.6f}; SR(r) per day {sr_r:.7f}, x sqrt(A) "
    f"{sqrt(A) * sr_r:.6f}, / sqrt(VR(246)) {sqrt(A) * sr_r / sqrt(vo246):.6f}",
    (100 * A * full["mean"], 2), (100 * A * rbar, 2), (A * full["s"] ** 2, 4), (A * s_r**2, 4), (100 * s_r, 4),
    (100 * an_s, 2), (100 * sqrt(A) * s_r, 2), (sr_R, 4), (sqrt(A) * sr_R, 2), (sr_r, 4), (sqrt(A) * sr_r, 3),
    (sqrt(A) * sr_r / sqrt(vo246), 3))                                                               # 54
v_ovl, v_bias = sqrt(v25) * v_day, sqrt(v25 / iid_factor(T25, 246)) * v_day
put(f"2003-2025 annual volatility: iid {100 * v_day:.5f}%; overlapping sqrt(VR) {100 * v_ovl:.5f}%;"
    f" bias-corrected {100 * v_bias:.5f}%; calendar years {100 * v_yr:.5f}%",
    (100 * v_day, 3), (100 * v_day, 2), (100 * v_ovl, 2), (100 * v_bias, 2), (100 * v_yr, 3), (100 * v_yr, 2))  # 55
grid = [(float(blocks(r25, 246, o).std(ddof=0)), len(blocks(r25, 246, o)), o) for o in range(246)]
gv = np.array([g[0] for g in grid])
lo, hi = grid[int(gv.argmin())], grid[int(gv.argmax())]
g_med = qf(gv, 0.5)
n_hi = int((gv >= v_yr - EPS).sum())
n_lo = int((gv <= v_day + EPS).sum())
mrg = min(float(np.abs(gv - v_yr).min()), float(np.abs(gv - v_day).min()))
put(f"246 grids of 246-day blocks on 2003-2025: min {100 * lo[0]:.5f}% (first return {lo[2]}, {lo[1]} blocks); max "
    f"{100 * hi[0]:.5f}% (first return {hi[2]}, {hi[1]} blocks); first return 0: {100 * grid[0][0]:.5f}% ({grid[0][1]}"
    f" blocks); median F^-1(1/2) = grid {ceil(0.5 * 246)} of 246 sorted, {100 * g_med:.5f}%; at or above the calendar"
    f" years' value {n_hi} ({100 * n_hi / 246:.4f}%); at or below the iid value {n_lo} ({100 * n_lo / 246:.4f}%);"
    f" smallest margin {mrg:.1e}; grids with 23 blocks: first returns "
    f"{min(g[2] for g in grid if g[1] == 23)}-{max(g[2] for g in grid if g[1] == 23)}",
    (100 * lo[0], 2), (100 * hi[0], 2), (100 * grid[0][0], 2), (100 * g_med, 2), (100 * n_hi / 246, 1),
    (100 * n_lo / 246, 1))                                                                           # 56
sh25 = float(r25.mean()) / sr25
cal_sr = float(ann.mean()) / v_yr
put(f"2003-2025 log returns: SR per day {sh25:.7f}; x sqrt(246) {sqrt(246) * sh25:.6f}; / sqrt(VR(246)) "
    f"{sqrt(246) * sh25 / sqrt(v25):.6f}; calendar years mean / s {cal_sr:.6f}",
    (sh25, 4), (sqrt(246) * sh25, 3), (sqrt(246) * sh25 / sqrt(v25), 3), (cal_sr, 3))                # 57

# ---------------------------------------------------------------- widget
put(f"initial state (2003-2025, m = 246): VR {v25:.6f}; annual {100 * v_ovl:.5f}%; iid {100 * v_day:.5f}%;"
    f" windows {T25 - 246 + 1}; T/m {T25 / 246:.4f}; iid factor {iid_factor(T25, 246):.6f}",
    (v25, 4), (100 * v_ovl, 2), (100 * v_day, 2), (T25 / 246, 1), (iid_factor(T25, 246), 3))         # 58

# ---------------------------------------------------------------- knowledge checks not given above
kc6 = 1 + 2 * (2 / 3) * 0.04
put(f"KC section 6: m = 3, rho_1 = 0.04, rho_2 = 0: 1 + 2(2/3)(0.04) = {kc6:.7f}", (kc6, 4))           # 59

# ---------------------------------------------------------------- problems
p1d = ["2020-03-16", "2020-03-17", "2020-03-18", "2020-03-19", "2020-03-20"]
p1 = np.array([float(RF[dates.index(d)]) for d in p1d])
p1_mean, p1_med, p1_trim = float(p1.mean()), qf(p1, 0.5), trim(p1, 1)
put("Problem 1 (2020-03-16..20): " + ", ".join(f"{100 * x:.6f}%" for x in p1) + f"; mean {100 * p1_mean:.6f}%;"
    f" median {100 * p1_med:.6f}%; 20% trimmed {100 * p1_trim:.6f}%",
    *[(100 * float(x), 4) for x in p1], (100 * p1_mean, 3), (100 * p1_med, 3), (100 * p1_trim, 3))  # 60
su23 = 100 * float(ann.std(ddof=1))
p2 = (22.207 * sqrt(23 / 22), 22.207 * 23 / 22, 22.207 * sqrt(22 / 23))
put(f"Problem 2: 22.207% x sqrt(23/22) = {p2[0]:.5f}%; x 23/22 = {p2[1]:.5f}%; x sqrt(22/23) = {p2[2]:.5f}%;"
    f" unrounded s_u {su23:.5f}%", *[(v, 2) for v in p2], (su23, 3))                                  # 61
p3v = (0.5889 * 1.4826 * sqrt(246.12), 0.5889 * sqrt(246.12), 0.5889 / 1.4826 * sqrt(246.12))
put(f"Problem 3: 0.5889% x 1.4826 x sqrt(246.12) = {p3v[0]:.5f}%; 0.5889% x sqrt(246.12) = {p3v[1]:.5f}%;"
    f" 0.5889% / 1.4826 x sqrt(246.12) = {p3v[2]:.5f}%", *[(v, 2) for v in p3v])                     # 62
p4 = (0.681 - 0.490 - 2 * 0.088) / (0.681 + 0.490)
p4c = (0.681 - 0.490) / (0.681 + 0.490)
put(f"Problem 4 (printed quartiles -0.490, 0.088, 0.681): {p4:.6f}; sign reversed {-p4:.6f}; without the median "
    f"{p4c:.6f}", (p4, 3), (p4c, 3))                                                                  # 63
p5 = sqrt(1.0393)
put(f"Problem 5: 1 + 0.0393 = 1.0393; 1 + 2(0.0393) = {1 + 2 * 0.0393:.4f}; sqrt(1.0393) = {p5:.6f}", (p5, 4))  # 64
put(f"Problem 6: iid factor {iid_factor(5849, 1231):.6f}; m/T {1231 / 5849:.6f}",
    (iid_factor(5849, 1231), 2), (1231 / 5849, 2))                                                  # 65
vr7 = 1 + 2 * 0.04 * 245 / 246
p7a = sqrt(246) * 1.2107
put(f"Problem 7: model ratio 1 + 2(0.04)(245/246) = {vr7:.7f}; sqrt(246) x 1.2107% = {p7a:.5f}%; x sqrt(ratio) = "
    f"{p7a * sqrt(vr7):.5f}%", (vr7, 4), (p7a, 2), (p7a * sqrt(vr7), 2))                             # 66
t_rows = []
t_checks: list[Check] = []
for nu in (5.0, 3.065):
    tq = float(stats.t.ppf(0.75, nu))
    ratio_t = tq * sqrt((nu - 2) / nu) / Z75
    t_rows.append(f"nu = {nu}: t quantile {tq:.6f}, 1.4826 MAD / sigma {ratio_t:.6f}")
    t_checks += [(tq, 4), (ratio_t, 3)]
tr_ratio = full["1.4826MAD"] / full["s"]
put("Problem 10: " + "; ".join(t_rows) + f"; TR23 {tr_ratio:.6f}", *t_checks, (tr_ratio, 3))          # 67

# ---------------------------------------------------------------- lab extension (stability check)
ext = []
ext_checks: list[Check] = []
for lab, msk in (("7%", pre), ("10%", ~pre)):
    x = r[msk]
    v3 = [vr_o(x, m) for m in (5, 20, 60)]
    ext.append(f"{lab}: " + ", ".join(f"VR({m}) {v:.6f}" for m, v in zip((5, 20, 60), v3)))
    ext_checks += [(v, 3) for v in v3]
put("; ".join(ext), *ext_checks)                                                                     # 68

# ---------------------------------------------------------------- calendar note (X1)
dd = [dt.date.fromisoformat(d) for d in dates]
sat = [d for d in dd if d.weekday() == 5]
wk25: dict[tuple[int, int], list[dt.date]] = {}
for d in d25:
    wk25.setdefault(d.isocalendar()[:2], []).append(d)
sat_wk = [v for v in wk25.values() if any(x.weekday() == 5 for x in v)]
six = [v for v in wk25.values() if len(v) == 6]
put(f"Saturday sessions in TR23: {len(sat)} ({sat[0]} -> {sat[-1]}), {sum(d.year <= 2025 for d in sat)} of them in"
    f" 2003-2025; ISO weeks of 2003-2025 holding one: {len(sat_wk)} ({min(map(len, sat_wk))}-{max(map(len, sat_wk))}"
    f" sessions); weeks of 6 sessions: {len(six)}, each holding a Saturday: {all(any(x.weekday() == 5 for x in v) for v in six)};"
    f" Sunday sessions: {sum(d.weekday() == 6 for d in dd)}")                                          # 69

print("\n".join(OUT))
