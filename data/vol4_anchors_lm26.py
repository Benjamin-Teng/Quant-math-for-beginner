"""LM26 anchors (Time Series II: Volatility Models): every number the Stage 1 brief quotes.

Reads TR23 from data/processed/vol3_taiex.parquet (columns date, tr, price, R, Rp; R the total-return index's simple
daily return, Rp the price index's, null on the first row; built and checked by data/vol3_series.py), the committed
realized variances data/derived/vol4_rv.csv (data/vol4_rv.py; one row per T5S day: regime_s, rv_<h> and n_<h> on the
window 09:30:00-13:30:00 for h = 5s, 10s, 15s, 30s, 1m, 5m, 10m, 15m, 30m, NaN where h is finer than the day's
sampling; o2, the squared log change from the previous TAIEX close to 09:30:00), TX23 from
data/processed/vol4_tx23.parquet (data/vol4_series.py; the held near-month contract per date), the raw 5-second TAIEX
files data/raw/intraday/taiex5s/<year>/<date>.csv and the raw TX 1-minute bars of 2025,
data/raw/intraday/tx1m/2025/<date>.csv (data/fetch_intraday.py), and the TX daily file data/raw/vol4/TX__*.csv. The
raw intraday files serve only anchors marked "raw": no intraday value is printed, only statistics. The script writes
nothing.

Conventions.
- Samples, never mixed in one statistic: TR23's T = 5,849 daily log returns r_t = ln(1 + R_t), 2003-01-03 ->
  2026-10-08, for every daily model; years = calendar days between TR23's first and last close / 365.25; A = T /
  years = 246.12. The daily models use r_t in percent (arch is given 100 r_t), so variances are in %^2 a day. T5S: the
  5,351 sessions 2005-01-03 -> 2026-10-08 of vol4_rv.csv (the same dates as TR23 from 2005-01-03, checked). TX: the
  near-month contract held during day t is TX23's contract on the previous TX23 date (rolled at the close of the day
  before each last trading day), 2025 only.
- Intraday: RV_t(h) = sum of squared log changes of the TAIEX price index on the grid 09:30:00, 09:30:00 + h, ...,
  13:30:00 (14,400 s / h returns); r_o,t^2 = o2 (previous close -> 09:30:00). The daily target V_t(h) = 1e4 (o2 +
  rv_h) in %^2; the main target is V_t := V_t(15 min). Intraday autocorrelations ("raw") pool within-day pairs only:
  rho_1 = sum over days of sum_t r_t r_{t-1} / sum over days of sum_t r_t^2 (uncentred, as the requested per-day
  columns c1_<h> of vol4_rv.csv would give it); the centred version subtracts the group's mean intraday return
  (LM19's (19.5) with divisor = number of returns) and is a check row. A period's signature is the ratio of the
  period's mean RV(h) to its mean RV(5 min).
- TX bars: a bar's label is the minute it starts (the regular session's labels run 08:45-13:44, sometimes with a
  13:45 bar, and the last regular bar's close equals TaiwanFuturesDaily's close), so the price at 09:30:00 is the
  close of the 09:29 bar and the grid 09:30:00..13:30:00 uses the closes of the bars 09:29..13:29; a minute without a
  bar (no trade) keeps the previous close.
- Models. GARCH(1,1): r_t = g + eps_t, eps_t = sigma_t xi_t, sigma_t^2 = omega + alpha eps_{t-1}^2 + beta
  sigma_{t-1}^2, fitted by arch 8.0.0, arch_model(100 r, mean="Constant", vol="GARCH", p=1, q=1, dist="normal" or
  "t").fit(disp="off") (SLSQP, arch's defaults), convergence asserted. The recursion starts from arch's backcast, the
  weighted mean of the first 75 squared residuals from the sample mean with weights 0.94^j (j = 0..74) normalized to
  1: sigma_1^2 = omega + (alpha + beta) * backcast. The log-likelihood is recomputed by hand in NumPy and must equal
  arch's to 1e-6. Standard errors: "classic" = the inverse of -l'' (arch's numerical Hessian; LM20's (20.6)), "robust"
  = arch's default sandwich H^-1 J H^-1 / T with J the sample covariance (divisor T - 1) of the per-day scores.
  EWMA: sigma^2_{t+1|t} = lam sigma^2_{t|t-1} + (1 - lam) r_t^2 with lam = 0.94 (RiskMetrics) and zero mean, started
  at the mean of r^2 over TR23's first 246 returns. Rolling 60-day: the mean of the last 60 r^2. Yesterday's V: V_t
  as the forecast for t + 1. EWMA of V: lam = 0.94 on V_t, started at the first T5S day's V.
- Out of sample: W = round(5A) = 1,231 returns (LM17's five years). At the first session s of each calendar month
  with s >= W, both GARCH models are refitted on r_{s-W}..r_{s-1}; the recursion is restarted at the window's first
  day with that window's backcast and run with the new parameters through the month's last session; the forecast of
  day t made at the close of t - 1 is sigma^2_{t|t-1}. Out-of-sample days: 2008-01-02 -> 2026-10-08. Losses per day:
  MSE (V - f)^2 in %^4, QLIKE V/f - ln(V/f) - 1 (zero for f = V). Loss differences against GARCH-normal: mean, its
  Newey-West standard error (Bartlett weights 1 - k/(l + 1), l = floor(4 (n/100)^(2/9)), divisor n, no small-sample
  correction; checked against statsmodels' HAC), t-stat, two-sided normal p-value. Mincer-Zarnowitz: OLS of V_t on a
  constant and f_t, coefficients a, b, HC0 standard errors (checked against statsmodels), the t-stat of b = 1.
- ARCH test (Engle 1982): OLS of eps^2_t on a constant and eps^2_{t-1}..eps^2_{t-K}, eps_t = r_t - rbar in percent;
  statistic (T - K) R-squared, upper tail of chi2_K (statsmodels' het_arch, checked).
- Simulation: experiment e creates rng = np.random.default_rng([e, 20261011]) once: 1 the GARCH-normal full-sample fit,
  2 the GARCH-t fit; 1,000 paths of T = 5,849 days each, sigma^2 started at the model's unconditional variance; each
  day draws one innovation per path (a vector of 1,000; t draws rng.standard_t(nu) * sqrt((nu - 2)/nu)). Statistics
  per path on TR23's 286 calendar months: the variance (divisor 286) over the mean of monthly counts of |R| >= 3%
  (guard), R = exp(r) - 1; the excess kurtosis (divisor T) of r. Medians and quantiles of the 1,000 values are
  F_hat^{-1}(u) (method="inverted_cdf"); the median's standard error is LM18's batch SE (20 consecutive batches of 50
  paths, standard deviation of the batch medians with divisor 20, over sqrt(20)).
- Counts against a threshold use the guard (R <= -0.03 + 1e-12 for a fall of 3% or more).
- Rounding: v(x, shown, *printed) prints x to `shown` decimals and appends " NEAR(d)" for each printed precision d
  (decimals) at which x lies within a tenth of a unit of the d-th decimal of a rounding boundary; sci() does the same
  for a mantissa. Every printed form of the brief is checked here at the precision it is printed.

Prints one line per anchor, "A26-NN <value>", in ID order.

Run:  PYTHONUTF8=1 .venv/Scripts/python.exe data/vol4_anchors_lm26.py [repository root]
"""
import datetime as dt
import math
import sys
import warnings
from pathlib import Path
from typing import Literal

import numpy as np
import polars as pl
import statsmodels.api as sm
from arch import arch_model
from numpy.typing import NDArray
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
RV_FILE = ROOT / "data" / "derived" / "vol4_rv.csv"
RAW5 = ROOT / "data" / "raw" / "intraday" / "taiex5s"
RAWTX = ROOT / "data" / "raw" / "intraday" / "tx1m" / "2025"
SEED = 20261011
EPS = 1e-12
LAM = 0.94
IV = [("5s", 5), ("10s", 10), ("15s", 15), ("30s", 30), ("1m", 60), ("5m", 300), ("10m", 600), ("15m", 900),
      ("30m", 1800)]
START_S, AUCT_S, CLOSE_S = 9 * 3600 + 30 * 60, 13 * 3600 + 25 * 60, 13 * 3600 + 30 * 60
Vec = NDArray[np.float64]
Mask = NDArray[np.bool_]
Dist = Literal["normal", "t"]
DISTS: tuple[Dist, Dist] = ("normal", "t")

OUT: list[str] = []


def put(nn: int, value: str) -> None:
    assert nn == len(OUT) + 1, f"anchor A26-{nn:02d} out of order"
    OUT.append(f"A26-{nn:02d} {value}")


def near(x: float, d: int) -> bool:
    """True when x, printed to d decimals, lies within a tenth of a unit of the d-th decimal of a boundary."""
    y = abs(x) * 10**d
    return abs(y - math.floor(y) - 0.5) < 0.1


def v(x: float, shown: int, *printed: int) -> str:
    flags = [str(d) for d in printed if near(x, d)]
    return f"{x:.{shown}f}" + (f" NEAR({','.join(flags)})" if flags else "")


def sci(x: float, shown: int, printed: int) -> str:
    mant = abs(x) / 10 ** math.floor(math.log10(abs(x)))
    return f"{x:.{shown}e}" + (" NEAR" if near(mant, printed) else "")


def qinv(x: Vec, u: float) -> float:
    return float(np.quantile(x, u, method="inverted_cdf"))


def batch_se_median(x: Vec) -> float:
    meds = np.array([qinv(b, 0.5) for b in np.split(x, 20)])
    return float(meds.std() / math.sqrt(20))


def ann(var_pct2: float) -> float:
    """Annualized volatility in percent from a daily variance in %^2."""
    return math.sqrt(A * var_pct2)


def nw_se(d: Vec, lags: int) -> float:
    """Newey-West standard error of a mean: Bartlett weights, divisor n, no small-sample correction."""
    c = d - d.mean()
    n = len(c)
    s = float(c @ c) / n
    for k in range(1, lags + 1):
        s += 2 * (1 - k / (lags + 1)) * float(c[k:] @ c[:-k]) / n
    return math.sqrt(s / n)


def ols_hc0(X: Vec, yv: Vec) -> tuple[Vec, Vec, float]:
    """OLS coefficients, HC0 standard errors, R-squared."""
    b, *_ = np.linalg.lstsq(X, yv, rcond=None)
    e = yv - X @ b
    xtxi = np.linalg.inv(X.T @ X)
    meat = (X * e[:, None] ** 2).T @ X
    se = np.sqrt(np.diag(xtxi @ meat @ xtxi))
    yc = yv - yv.mean()
    return b, se, 1 - float(e @ e) / float(yc @ yc)


def backcast(e: Vec) -> float:
    w = 0.94 ** np.arange(min(75, len(e)))
    return float(np.sum(e[: len(w)] ** 2 * w / w.sum()))


def garch_filter(om: float, al: float, be: float, e: Vec, bc: float) -> Vec:
    """sigma^2_t for t = 0..len(e) (the last is the forecast after e ends), started from the backcast."""
    s2 = np.empty(len(e) + 1)
    s2[0] = om + (al + be) * bc
    for t in range(len(e)):
        s2[t + 1] = om + al * e[t] ** 2 + be * s2[t]
    return s2


def fit(x: Vec, dist: Dist, cov: Literal["robust", "classic"] = "robust"):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        res = arch_model(x, mean="Constant", vol="GARCH", p=1, q=1, dist=dist).fit(disp="off", cov_type=cov)
    assert res.convergence_flag == 0, "arch did not converge"
    return res


def qlike(h: Vec, f: Vec) -> Vec:
    return h / f - np.log(h / f) - 1


# ---------------------------------------------------------------- data
tr = pl.read_parquet(PROC / "vol3_taiex.parquet").sort("date")
dates_all = [str(d) for d in tr["date"].to_list()]
dates = dates_all[1:]
R = tr["R"].to_numpy()[1:]
Rp = tr["Rp"].to_numpy()[1:]
r = np.log1p(R)
rp = np.log1p(Rp)
y = 100 * r
T = len(y)
days_span = (dt.date.fromisoformat(dates_all[-1]) - dt.date.fromisoformat(dates_all[0])).days
years = days_span / 365.25
A = T / years
pos = {d: i for i, d in enumerate(dates)}
rvf = pl.read_csv(RV_FILE, comment_prefix="#").sort("date")
rv_dates = rvf["date"].to_list()
reg = rvf["regime_s"].to_numpy()
RV = {name: rvf[f"rv_{name}"].to_numpy() for name, _ in IV}
NN = {name: rvf[f"n_{name}"].to_numpy() for name, _ in IV}
O2 = rvf["o2"].to_numpy()
ryear = np.array([d[:4] for d in rv_dates])
Vt = {name: 1e4 * (O2 + RV[name]) for name in ("5m", "15m", "30m")}
Vmap = {name: dict(zip(rv_dates, Vt[name].tolist())) for name in Vt}

# ---------------------------------------------------------------- data role
put(1, f"T {T} returns {dates[0]} .. {dates[-1]}; days {days_span}; years {years:.6f}; A {A:.6f}")
regimes = []
for s in (60, 15, 10, 5):
    idx = np.flatnonzero(reg == s)
    regimes.append(f"{s}s: {len(idx)} days {rv_dates[idx[0]]} .. {rv_dates[idx[-1]]}")
put(2, f"T5S {len(rv_dates)} days {rv_dates[0]} .. {rv_dates[-1]}; " + "; ".join(regimes))
tr_from05 = [d for d in dates if d >= "2005-01-03"]
assert tr_from05 == rv_dates
put(3, f"T5S dates equal TR23's dates from 2005-01-03: {len(tr_from05)} = {len(rv_dates)}")
counts = []
for name, h in IV:
    ok = ~np.isnan(NN[name])
    assert np.all(NN[name][ok] == 14400 // h)
    counts.append(f"{name} {14400 // h} ({int(ok.sum())} days)")
put(4, "returns a day on 09:30:00-13:30:00: " + ", ".join(counts))
i05 = pos["2005-01-03"]
div_share = float(np.sum(y[i05:] ** 2 - (100 * rp[i05:]) ** 2) / np.sum(y[i05:] ** 2))
put(5, f"mean r^2 (TR23, total return) {np.mean(y[i05:] ** 2):.6f} %^2, mean r_p^2 (price index) "
       f"{np.mean((100 * rp[i05:]) ** 2):.6f} %^2 on the 5,351 T5S days; (sum r^2 - sum r_p^2)/sum r^2 {div_share:.5%}")

# ---------------------------------------------------------------- full-sample fits (needed by the case and section 4)
gn = fit(y, "normal")
gn_c = fit(y, "normal", "classic")
gt = fit(y, "t")
gt_c = fit(y, "t", "classic")
pn = gn.params.to_numpy()
pt = gt.params.to_numpy()
cvn = np.asarray(gn.conditional_volatility)
cvt = np.asarray(gt.conditional_volatility)
bc_full = backcast(y - y.mean())
s2_hand = garch_filter(pn[1], pn[2], pn[3], y - pn[0], bc_full)
ll_hand = -0.5 * float(np.sum(np.log(2 * np.pi) + np.log(s2_hand[:T]) + (y - pn[0]) ** 2 / s2_hand[:T]))
assert abs(ll_hand - gn.loglikelihood) < 1e-6, (ll_hand, gn.loglikelihood)
assert np.max(np.abs(s2_hand[:T] - cvn**2)) < 1e-9

# ---------------------------------------------------------------- forecasts (out of sample), used from the case on
W = round(5 * A)
assert W == 1231
month = [d[:7] for d in dates]
starts = [i for i in range(T) if i == 0 or month[i] != month[i - 1]]
first = next(i for i in starts if i >= W)
FC: dict[str, Vec] = {k: np.full(T, np.nan) for k in ("roll60", "ewma", "garch_n", "garch_t", "v_prev", "ewma_v")}
refits: dict[str, list[tuple[str, Vec]]] = {"normal": [], "t": []}


def rolling_garch(window: int, store: bool) -> dict[str, Vec]:
    out = {"normal": np.full(T, np.nan), "t": np.full(T, np.nan)}
    f0 = next(i for i in starts if i >= window)
    for k, s in enumerate(starts):
        if s < f0:
            continue
        e_end = starts[k + 1] if k + 1 < len(starts) else T
        win = y[s - window : s]
        bc = backcast(win - win.mean())
        for dist in DISTS:
            res = fit(win, dist)
            p = res.params.to_numpy()
            if store:
                refits[dist].append((dates[s], p))
            s2 = garch_filter(p[1], p[2], p[3], y[s - window : e_end] - p[0], bc)
            if store and k == starts.index(f0):
                assert np.max(np.abs(s2[:window] - np.asarray(res.conditional_volatility) ** 2)) < 1e-9
            out[dist][s:e_end] = s2[window : window + (e_end - s)]
    return out


rg = rolling_garch(W, True)
FC["garch_n"], FC["garch_t"] = rg["normal"], rg["t"]
ew = np.empty(T + 1)
ew[0] = float(np.mean(y[:246] ** 2))
for t in range(T):
    ew[t + 1] = LAM * ew[t] + (1 - LAM) * y[t] ** 2
FC["ewma"][first:] = ew[first:T]
c2 = np.concatenate([[0.0], np.cumsum(y**2)])
V15 = np.array([Vmap["15m"].get(d, np.nan) for d in dates])
ewv = np.full(T + 1, np.nan)
ewv[i05] = V15[i05]
for t in range(i05, T):
    ewv[t + 1] = LAM * ewv[t] + (1 - LAM) * V15[t]
for t in range(first, T):
    FC["roll60"][t] = (c2[t] - c2[t - 60]) / 60
    FC["v_prev"][t] = V15[t - 1]
    FC["ewma_v"][t] = ewv[t]
oos = np.arange(first, T)
assert not any(np.isnan(FC[k][oos]).any() for k in FC)
NAMES = {"roll60": "rolling 60-day", "ewma": "EWMA 0.94", "garch_n": "GARCH normal", "garch_t": "GARCH t",
         "v_prev": "yesterday's V", "ewma_v": "EWMA of V"}

# ---------------------------------------------------------------- case
i7, i2, i8 = pos["2025-04-07"], pos["2025-04-02"], pos["2025-04-08"]
assert i7 == i2 + 1
rank = int(np.argsort(R)[0])
put(6, f"2025-04-07: R {R[i7]:.4%} (rank 1 of {T}: {rank == i7}); r {y[i7]:.4f}%; 2025-04-02 r {y[i2]:.4f}%")
case = []
for k in ("garch_n", "ewma", "roll60", "v_prev"):
    f = FC[k][i7]
    case.append(f"{NAMES[k]} {math.sqrt(f):.4f}% a day ({v(ann(f), 2, 1)}% a year), r/sigma {y[i7] / math.sqrt(f):.3f}")
put(7, "forecasts for 2025-04-07 made on 2025-04-02: " + "; ".join(case))
put(8, f"2025-04-07: V {V15[i7]:.4f} %^2 (sqrt {math.sqrt(V15[i7]):.4f}%), o2 share {1e4 * O2[rv_dates.index('2025-04-07')] / V15[i7]:.4%}, "
       f"r^2 {y[i7] ** 2:.4f} %^2; V/r^2 {V15[i7] / y[i7] ** 2:.4f}")
case8 = [f"{NAMES[k]} {math.sqrt(FC[k][i8]):.4f}% ({ann(FC[k][i8]):.2f}% a year)" for k in ("garch_n", "ewma", "roll60", "v_prev")]
put(9, "forecasts for 2025-04-08 made on 2025-04-07: " + "; ".join(case8) + f"; V on 2025-04-08 {V15[i8]:.4f} %^2 "
       f"(sqrt {math.sqrt(V15[i8]):.4f}%); r {y[i8]:.4f}%")
pre = np.arange(i7 - 20, i7)
post = np.arange(i7, i7 + 20)
put(10, f"20 sessions to 2025-04-02 ({dates[pre[0]]}..): realized sqrt(A mean V) {ann(float(V15[pre].mean())):.2f}%; "
        f"20 from 2025-04-07 (..{dates[post[-1]]}): {ann(float(V15[post].mean())):.2f}%; GARCH normal forecasts over those 20: "
        f"{ann(float(FC['garch_n'][post].mean())):.2f}%; EWMA {ann(float(FC['ewma'][post].mean())):.2f}%")

# ---------------------------------------------------------------- section 2: ARCH test
yc = y - y.mean()


def arch_test(x: Vec, K: int) -> tuple[Vec, float, float, float]:
    z = x[K:] ** 2
    X = np.column_stack([np.ones(len(x) - K)] + [x[K - j - 1 : len(x) - j - 1] ** 2 for j in range(K)])
    b, *_ = np.linalg.lstsq(X, z, rcond=None)
    e = z - X @ b
    r2 = 1 - float(e @ e) / float((z - z.mean()) @ (z - z.mean()))
    lm = (len(x) - K) * r2
    h = het_arch(x, nlags=K, result_object=True)
    assert abs(h.lm - lm) < 1e-6 * lm
    return b, r2, lm, float(stats.chi2.sf(lm, K))


b1, r21, lm1, p1 = arch_test(yc, 1)
put(11, f"K=1 on r - rbar (%): a {b1[0]:.4f}, b_1 {v(b1[1], 4, 3)}, R-squared {r21:.5f}, LM (T-1)R2 {lm1:.2f}, "
        f"p {sci(p1, 3, 1)} (LM19's rho_hat_1(r^2) 0.194, A19-40)")
b5, r25, lm5, p5 = arch_test(yc, 5)
put(12, f"K=5: a {b5[0]:.4f}, b_1..b_5 {', '.join(f'{x:.4f}' for x in b5[1:])}, sum b {b5[1:].sum():.4f}, "
        f"R-squared {r25:.5f}, LM {v(lm5, 2, 0, 1)}, p {sci(p5, 3, 1)}; chi2_5 5% point {stats.chi2.ppf(0.95, 5):.4f}")
xin = (y - pn[0]) / cvn
_, r2x, lmx, px = arch_test(xin - xin.mean(), 5)
put(13, f"K=5 on GARCH-normal standardized residuals: R-squared {r2x:.5f}, LM {v(lmx, 2, 1)}, p {v(px, 4, 2, 3)}")

# ---------------------------------------------------------------- section 3: EWMA
wts = (1 - LAM) * LAM ** np.arange(10000)
put(14, f"weights sum {wts.sum():.10f}; effective window 1/(1-lam) {1 / (1 - LAM):.4f}; mean lag lam/(1-lam) "
        f"{LAM / (1 - LAM):.4f}; weight half-life ln(1/2)/ln(lam) {math.log(0.5) / math.log(LAM):.4f} days; weight on the "
        f"last 75 days {1 - LAM**75:.4%}; lam^75 {LAM**75:.5f}")
put(15, f"start sigma^2 = mean r^2 of the first 246 returns {ew[0]:.4f} %^2; lam^1231 {LAM**1231:.3e} (first OOS day)")
s_a = math.sqrt(ew[i7])
s_b = math.sqrt(ew[i8])
hand = LAM * ew[i7] + (1 - LAM) * y[i7] ** 2
assert abs(hand - ew[i8]) < 1e-12
put(16, f"sigma for 2025-04-07 {v(s_a, 4, 2, 3)}% ({ew[i7]:.4f} %^2); for 2025-04-08 {v(s_b, 4, 2, 3)}% = sqrt(0.94 x "
        f"{ew[i7]:.4f} + 0.06 x {y[i7] ** 2:.4f}) = sqrt({0.94 * ew[i7]:.4f} + {0.06 * y[i7] ** 2:.4f}); from the printed "
        f"1.560 and -10.203: {math.sqrt(0.94 * 1.560**2 + 0.06 * 10.203**2):.4f}")
lams = np.round(np.arange(0.800, 0.9951, 0.005), 3)
qv = []
hV = V15[oos]
for lam in lams:
    e2 = np.empty(T + 1)
    e2[0] = ew[0]
    for t in range(T):
        e2[t + 1] = lam * e2[t] + (1 - lam) * y[t] ** 2
    qv.append(float(qlike(hV, e2[oos]).mean()))
qv_arr = np.array(qv)
ib = int(qv_arr.argmin())
put(17, f"QLIKE of EWMA r^2 on the OOS days against V, lam = 0.800..0.995 (step 0.005): best lam {lams[ib]:.3f} QLIKE "
        f"{qv_arr[ib]:.4f}; lam 0.94 {qv_arr[list(lams).index(0.94)]:.4f}; lam 0.97 {qv_arr[list(lams).index(0.97)]:.4f}; "
        f"lam 0.80 {qv_arr[0]:.4f}; GARCH normal {float(qlike(hV, FC['garch_n'][oos]).mean()):.4f}")

# ---------------------------------------------------------------- section 4: GARCH
sen, ser = gn_c.std_err.to_numpy(), gn.std_err.to_numpy()
put(18, "GARCH normal, full TR23: " + ", ".join(f"{nm} {pv:.6f} (classic {sc:.6f}, robust {sr:.6f})" for nm, pv, sc, sr in
        zip(("g", "omega", "alpha", "beta"), pn, sen, ser)) + f"; loglik {gn.loglikelihood:.4f}")
put(19, f"backcast {bc_full:.6f} %^2; hand loglik {ll_hand:.6f}, minus arch {ll_hand - gn.loglikelihood:.2e}; "
        f"max |sigma^2 hand - arch| {np.max(np.abs(s2_hand[:T] - cvn**2)):.1e}")
pers = pn[2] + pn[3]
uvar = pn[1] / (1 - pers)
put(20, f"alpha+beta {v(pers, 6, 4)}; unconditional variance omega/(1-alpha-beta) {v(uvar, 6, 3)} %^2 (sigma "
        f"{v(math.sqrt(uvar), 6, 3)}% a day); annualized "
        f"{v(ann(uvar), 4, 2)}%; TR23's sqrt(A) s_r 18.99% (LM19, A19-54)")


def half_life(p: Vec, cov: Vec) -> tuple[float, float]:
    ps = p[2] + p[3]
    hl = math.log(0.5) / math.log(ps)
    grad = -math.log(0.5) / (ps * math.log(ps) ** 2)
    var = grad**2 * (cov[2, 2] + cov[3, 3] + 2 * cov[2, 3])
    return hl, math.sqrt(var)


def hl_of(ps: float) -> float:
    return math.log(0.5) / math.log(ps)


hl_n, se_hl_c = half_life(pn, gn_c.param_cov.to_numpy())
_, se_hl_r = half_life(pn, gn.param_cov.to_numpy())
covr = gn.param_cov.to_numpy()
covc = gn_c.param_cov.to_numpy()
se_pers_r = math.sqrt(covr[2, 2] + covr[3, 3] + 2 * covr[2, 3])
se_pers_c = math.sqrt(covc[2, 2] + covc[3, 3] + 2 * covc[2, 3])
z975 = float(stats.norm.ppf(0.975))
lo_p, hi_p = pers - z975 * se_pers_r, pers + z975 * se_pers_r
put(21, f"half-life ln(1/2)/ln(alpha+beta) {v(hl_n, 4, 1)} sessions; delta-method SE classic {v(se_hl_c, 4, 1)}, robust "
        f"{v(se_hl_r, 4, 1)}; robust delta interval {hl_n - z975 * se_hl_r:.2f} to {hl_n + z975 * se_hl_r:.2f}; SE(alpha+beta) "
        f"classic {se_pers_c:.5f}, robust {se_pers_r:.5f}; robust interval for alpha+beta {lo_p:.5f} to {hi_p:.5f}, mapped to "
        f"half-lives {hl_of(lo_p):.2f} to {hl_of(hi_p):.2f}")
stc, strr = gt_c.std_err.to_numpy(), gt.std_err.to_numpy()
pers_t = pt[2] + pt[3]
hl_t, se_hlt = half_life(pt, gt.param_cov.to_numpy())
put(22, "GARCH t, full TR23: " + ", ".join(f"{nm} {pv:.6f} (classic {sc:.6f}, robust {sr:.6f})" for nm, pv, sc, sr in
        zip(("g", "omega", "alpha", "beta", "nu"), pt, stc, strr)) + f"; loglik {gt.loglikelihood:.4f}; ell gain "
        f"{gt.loglikelihood - gn.loglikelihood:.2f}; alpha+beta {pers_t:.6f}; half-life {v(hl_t, 4, 1)} (robust SE "
        f"{se_hlt:.2f}); unconditional variance {v(pt[1] / (1 - pers_t), 6, 3)} %^2, annualized {ann(pt[1] / (1 - pers_t)):.2f}%")
xit = (y - pt[0]) / cvt
moments = []
for nm, x in (("xi normal", xin), ("xi t", xit), ("r", y)):
    xc = x - x.mean()
    sk = float((xc**3).mean() / (xc**2).mean() ** 1.5)
    ku = float((xc**4).mean() / (xc**2).mean() ** 2 - 3)
    moments.append(f"{nm}: mean {x.mean():.4f}, s {x.std():.4f}, skew {v(sk, 4, 2)}, excess kurtosis {v(ku, 4, 2)}")
put(23, "; ".join(moments) + " (divisor T, LM19's (19.3))")
lbn = acorr_ljungbox(np.abs(xin), lags=[10]).to_numpy()
lbt = acorr_ljungbox(np.abs(xit), lags=[10]).to_numpy()
lbr = acorr_ljungbox(np.abs(y), lags=[10]).to_numpy()
lbn2 = acorr_ljungbox(xin**2, lags=[10]).to_numpy()
put(24, f"Q_LB(10) |xi| normal {v(lbn[0, 0], 2, 1)} p {lbn[0, 1]:.4f}; |xi| t {lbt[0, 0]:.2f} p {lbt[0, 1]:.4f}; xi^2 normal "
        f"{lbn2[0, 0]:.2f} p {lbn2[0, 1]:.4f}; |r| {lbr[0, 0]:.2f} (LM25's 1,820, A25-22); chi2_10 5% point "
        f"{stats.chi2.ppf(0.95, 10):.4f}")
den4 = 1 - pers**2 - 2 * pn[2] ** 2
kurt_n = 3 * (1 - pers**2) / den4
kxi = 3 * (pt[4] - 2) / (pt[4] - 4)
cond_t = pers_t**2 + (kxi - 1) * pt[2] ** 2
put(25, f"normal GARCH: 1-(a+b)^2-2a^2 {den4:.6f}; Kurt 3(1-(a+b)^2)/(...) {v(kurt_n, 4, 2)}, excess {v(kurt_n - 3, 4, 2)}; "
        f"t GARCH: Kurt(xi) 3(nu-2)/(nu-4) {kxi:.4f}; (a+b)^2+(Kurt(xi)-1)a^2 {cond_t:.6f} (>= 1: no finite fourth moment)")
s2_7 = s2_hand[i7 + 1]
assert abs(s2_7 - (pn[1] + pn[2] * (y[i7] - pn[0]) ** 2 + pn[3] * cvn[i7] ** 2)) < 1e-12
fcarch = gn.forecast(horizon=250, start=i7, reindex=False).variance.to_numpy()[0]


def path(s2next: float, m_max: int = 250) -> Vec:
    mm = np.arange(1, m_max + 1)
    return uvar + pers ** (mm - 1) * (s2next - uvar)


p7 = path(s2_7)
assert np.max(np.abs(p7 - fcarch)) < 1e-9
put(26, f"from 2025-04-07 (full-sample normal fit): sigma_t {cvn[i7]:.4f}%, sigma_t+1|t {math.sqrt(s2_7):.4f}% ({s2_7:.4f} %^2); "
        + ", ".join(f"m={m}: {math.sqrt(p7[m - 1]):.4f}%" for m in (1, 5, 20, 44, 60, 250))
        + "; annualized average over m days: " + ", ".join(f"m={m} {ann(float(p7[:m].mean())):.2f}%" for m in (1, 20, 250))
        + f"; arch forecast equal (max diff {np.max(np.abs(p7 - fcarch)):.0e})")
s2_T = s2_hand[T]
pT = path(s2_T)
put(27, f"from 2026-10-08: sigma_T+1|T {math.sqrt(s2_T):.4f}% ({s2_T:.4f} %^2, {ann(s2_T):.2f}% a year); m=250: "
        f"{math.sqrt(pT[-1]):.4f}%; annualized average over 20 days {ann(float(pT[:20].mean())):.2f}%, 250 days "
        f"{ann(float(pT.mean())):.2f}%; unconditional {ann(uvar):.2f}%")
put(28, f"widget initial state: alpha {pn[2]:.4f}, beta {pn[3]:.4f}, unconditional variance {uvar:.4f} %^2 "
        f"({ann(uvar):.2f}% a year), start {math.sqrt(s2_7):.3f}% (after 2025-04-07) or {math.sqrt(s2_T):.3f}% (2026-10-08); "
        f"half-life {hl_n:.1f}")
fall = R <= -0.03 + EPS
rise = R > 0.03 + EPS
idf = np.flatnonzero(fall[:-1])
idr = np.flatnonzero(rise[:-1])
e_n = y - pn[0]
snext = np.sqrt(s2_hand[1 : T + 1])
zthr = (100 * math.log(0.97) - pn[0]) / snext
Femp = np.searchsorted(np.sort(xin), zthr, side="right") / T
Fnor = stats.norm.cdf(zthr)
put(29, f"observed: {len(idf)} falls of 3% or more, {int(fall[idf + 1].sum())} followed by a fall; {len(idr)} rises above 3%, "
        f"{int(fall[idr + 1].sum())} followed by a fall; {int(fall[1:].sum())} falls on days 2..T. GARCH normal, xi's own "
        f"distribution: expected {v(float(Femp[idf].sum()), 2, 1)} after falls ({Femp[idf].mean():.4f}), {Femp[idr].sum():.2f} after "
        f"rises ({Femp[idr].mean():.4f}), {Femp[:-1].sum():.1f} on all days ({Femp[:-1].mean():.4f}); normal xi: "
        f"{Fnor[idf].sum():.2f}, {Fnor[idr].sum():.2f}, {Fnor[:-1].sum():.1f}")
_, mi = np.unique(np.array(month), return_inverse=True)
nm_ = int(mi.max()) + 1
big = np.abs(R) >= 0.03 - EPS
cnt = np.bincount(mi, weights=big.astype(float), minlength=nm_)
obs_disp = float(cnt.var() / cnt.mean())


def simulate(e: int, p: Vec, dist: str) -> str:
    rng = np.random.default_rng([e, SEED])
    npath = 1000
    g, om, al, be = p[:4]
    s2 = np.full(npath, om / (1 - al - be))
    ys = np.empty((npath, T))
    for t in range(T):
        if dist == "normal":
            xi = rng.standard_normal(npath)
        else:
            xi = rng.standard_t(p[4], npath) * math.sqrt((p[4] - 2) / p[4])
        eps = np.sqrt(s2) * xi
        ys[:, t] = g + eps
        s2 = om + al * eps**2 + be * s2
    Rs = np.expm1(ys / 100)
    disp = np.empty(npath)
    for k in range(npath):
        c = np.bincount(mi, weights=(np.abs(Rs[k]) >= 0.03 - EPS).astype(float), minlength=nm_)
        disp[k] = c.var() / c.mean()
    yc_ = ys - ys.mean(axis=1, keepdims=True)
    kurt = (yc_**4).mean(axis=1) / (yc_**2).mean(axis=1) ** 2 - 3
    return (f"dispersion median {v(qinv(disp, 0.5), 4, 2)} (batch SE {batch_se_median(disp):.4f}), 5% {v(qinv(disp, 0.05), 6, 2)}, "
            f"95% {v(qinv(disp, 0.95), 6, 2)}, share >= observed {np.mean(disp >= obs_disp - 1e-12):.3f}; excess kurtosis median "
            f"{qinv(kurt, 0.5):.3f} (batch SE {batch_se_median(kurt):.3f}), 5% {qinv(kurt, 0.05):.3f}, 95% {qinv(kurt, 0.95):.3f}, "
            f"share >= 5.428 {np.mean(kurt >= 5.428):.3f}")


put(30, f"observed months {nm_}, monthly count variance/mean {obs_disp:.4f} (LM15's 3.02); experiment 1 (GARCH normal, "
        f"1,000 paths): " + simulate(1, pn, "normal"))
put(31, "experiment 2 (GARCH t, 1,000 paths): " + simulate(2, pt, "t"))

# ---------------------------------------------------------------- section 5: realized variance (file)
d_arr = np.array(rv_dates)
periods = {
    "2005-2010": (d_arr >= "2005-01-01") & (d_arr <= "2010-12-31"),
    "2011-01-17..2012": (d_arr >= "2011-01-17") & (d_arr <= "2012-12-31"),
    "2015-2026": (d_arr >= "2015-01-01"),
    "2025": ryear == "2025",
}
sig = {}
lines = []
for pname, m in periods.items():
    m5 = float(np.mean(RV["5m"][m]))
    ratios = {}
    for name, _ in IV:
        x = RV[name][m]
        if not np.isnan(x).any():
            ratios[name] = float(np.mean(x)) / m5
    sig[pname] = ratios
    lines.append(f"{pname} ({int(m.sum())} days): " + ", ".join(f"{k} {v(val, 6, 2, 3)}" for k, val in ratios.items()))
put(32, "mean RV(h)/mean RV(5m): " + "; ".join(lines))
lines = []
for s in (60, 15, 10, 5):
    m = reg == s
    m5 = float(np.mean(RV["5m"][m]))
    lines.append(f"{s}s: " + ", ".join(f"{name} {float(np.mean(RV[name][m])) / m5:.3f}" for name, _ in IV
                                       if not np.isnan(RV[name][m]).any()))
put(33, "by sampling regime (check rows): " + "; ".join(lines))

# ---------------------------------------------------------------- raw 5-second pass
files = {f.stem: f for f in RAW5.glob("*/*.csv")}
assert sorted(files) == rv_dates
P: dict[str, list[float]] = {k: [] for k in ("f_ss", "f_p1", "f_s", "f_n", "m1_ss", "m1_p1", "m1_s", "m5_ss", "m5_p1",
                                              "m5_s", "auct2", "frozen_all", "rho1_day", "f_g1", "f_s_head", "f_s_tail",
                                              "m1_head", "m1_tail", "m5_head", "m5_tail")}
for d in rv_dates:
    x = pl.read_csv(files[d], schema_overrides={"date": pl.String, "TAIEX": pl.Float64})
    tt = x["date"].str.slice(11, 8).to_list()
    secs = np.array([int(a[:2]) * 3600 + int(a[3:5]) * 60 + int(a[6:8]) for a in tt])
    lv = np.log(x["TAIEX"].to_numpy())
    rg_s = int(np.bincount(np.diff(secs)).argmax())
    at = {int(s): j for j, s in enumerate(secs)}
    for key, h in (("f", rg_s), ("m1", 60), ("m5", 300)):
        rr = np.diff(lv[[at[s] for s in range(START_S, CLOSE_S + 1, h)]])
        P[f"{key}_ss"].append(float(rr @ rr))
        P[f"{key}_p1"].append(float(rr[1:] @ rr[:-1]))
        P[f"{key}_s"].append(float(rr.sum()))
        hk = "f_s" if key == "f" else key
        P[f"{hk}_head"].append(float(rr[0]))
        P[f"{hk}_tail"].append(float(rr[-1]))
        if key == "f":
            P["f_n"].append(len(rr))
            rc = rr - rr.mean()
            P["rho1_day"].append(float(rc[1:] @ rc[:-1]) / float(rc @ rc))
    inside = [at[s] for s in range(AUCT_S + rg_s, CLOSE_S, rg_s)]   # 13:25:00 + one step .. 13:30:00 - one step
    P["frozen_all"].append(float(np.all(lv[inside] == lv[inside[0]])))
    P["auct2"].append(float((lv[at[CLOSE_S]] - lv[at[AUCT_S]]) ** 2))
PA = {k: np.array(val) for k, val in P.items()}


def pooled(mask: Mask, key: str, centred: bool) -> float:
    ss, p1, s = PA[f"{key}_ss"][mask], PA[f"{key}_p1"][mask], PA[f"{key}_s"][mask]
    if not centred:
        return float(p1.sum() / ss.sum())
    hk = "f_s" if key == "f" else key
    n = PA["f_n"][mask] if key == "f" else np.full(int(mask.sum()), 240.0 if key == "m1" else 48.0)
    mu = float(s.sum() / n.sum())
    a = s - PA[f"{hk}_head"][mask]     # sum over t >= 2
    b = s - PA[f"{hk}_tail"][mask]     # sum over t <= n - 1
    num = p1 - mu * (a + b) + (n - 1) * mu * mu
    den = ss - 2 * mu * s + n * mu * mu
    return float(num.sum() / den.sum())


m5s = reg == 5
m15 = reg == 15
r5 = pooled(m5s, "f", False)
r15 = pooled(m15, "f", False)
vr5 = float(np.mean(RV["10s"][m5s]) / np.mean(RV["5s"][m5s]) - 1)
vr15 = float(np.mean(RV["30s"][m15]) / np.mean(RV["15s"][m15]) - 1)
r5m = pooled(np.ones(len(rv_dates), bool), "m5", False)
vr5m = float(np.mean(RV["10m"]) / np.mean(RV["5m"]) - 1)
put(34, f"pooled rho_1 (raw) against RV(2h)/RV(h) - 1 (file): 5 s, 5-second days {r5:.4f} vs {vr5:.4f}; 15 s, 15-second days "
        f"{r15:.4f} vs {vr15:.4f}; 5 min, all days {r5m:.4f} vs {vr5m:.4f}")
yr_lines = []
maxdiff = 0.0
rows_1m = {}
for yy in sorted(set(ryear)):
    m = ryear == yy
    a1 = pooled(m, "m1", False)
    a5 = pooled(m, "m5", False)
    maxdiff = max(maxdiff, abs(a1 - pooled(m, "m1", True)), abs(a5 - pooled(m, "m5", True)))
    rows_1m[yy] = (a1, a5)
    ratio = float(np.mean(RV["1m"][m]) / np.mean(RV["5m"][m]))
    yr_lines.append(f"{yy} {v(a1, 4, 2, 3)} / {v(a5, 4, 2, 3)} / {ratio:.3f}")
put(35, "by year, rho_1 of 1-minute / 5-minute returns (raw, uncentred, pooled) / RV(1m)/RV(5m) (file): " + "; ".join(yr_lines)
        + f"; max |uncentred - centred| {maxdiff:.1e}; iid SE of a year's 1-minute rho_1 1/sqrt(240 x 246) "
        f"{1 / math.sqrt(240 * 246):.4f}")
m25 = ryear == "2025"
rd = PA["rho1_day"][m25]
ratio_day = RV["5s"][m25] / RV["5m"][m25]
put(36, f"2025, each day's rho_1 of 5-second returns (own mean, divisor n): min {rd.min():.4f}, 25% {qinv(rd, 0.25):.4f}, "
        f"median {qinv(rd, 0.5):.4f}, 75% {qinv(rd, 0.75):.4f}, max {rd.max():.4f} ({int(m25.sum())} days); RV(5s)/RV(5m) per "
        f"day: median {qinv(ratio_day, 0.5):.2f}, max {ratio_day.max():.2f} ({rv_dates[int(np.flatnonzero(m25)[ratio_day.argmax()])]}); "
        f"pooled 2025 rho_1 {pooled(m25, 'f', False):.4f}")
p25 = pooled(m25, "f", False)
put(37, f"MA(1) noise reading, -rho_1 = sigma_u^2/(var e + 2 sigma_u^2) <= 1/2: noise share 2|rho_1| of a 5-second return's "
        f"variance: 2025 {v(2 * abs(p25), 4, 2)}, 5-second days {2 * abs(r5):.4f}")
noise = []
for yy in [str(x) for x in range(2015, 2027)]:
    m = ryear == yy
    g1 = PA["f_p1"][m].sum() / PA["f_n"][m].sum()
    noise.append(f"{yy} {1e4 * math.sqrt(-g1):.3f}")
put(38, "sqrt(-gamma_1) of 5-second log returns, bp (pooled, uncentred; check rows): " + ", ".join(noise))

# ---------------------------------------------------------------- TX 1-minute bars, 2025
tx23 = pl.read_parquet(PROC / "vol4_tx23.parquet").sort("date")
txd = [str(d) for d in tx23["date"].to_list()]
held = dict(zip(txd, tx23["contract"].to_list()))
daily = pl.read_csv(min((ROOT / "data" / "raw" / "vol4").glob("TX__*.csv")), infer_schema_length=0)
daily25 = daily.filter(pl.col("date").str.starts_with("2025"))
dclose = {(a, b): float(c) for a, b, c in zip(daily25["date"].to_list(), daily25["contract_date"].to_list(),
                                                daily25["close"].to_list())}
tx_days = [d for d in txd if d.startswith("2025")]
first_lab, last_lab, nbar, eq, miss_days = set(), {}, {}, 0, {}
TXRV: dict[int, list[float]] = {h: [] for h in (1, 5, 10, 15, 30)}
tx_p1, tx_ss = [], []
for d in tx_days:
    c = str(held[txd[txd.index(d) - 1]])
    x = pl.read_csv(RAWTX / f"{d}.csv", infer_schema_length=0)
    x = x.filter((pl.col("contract_date") == c) & (pl.col("minute") >= "08:45:00") & (pl.col("minute") <= "13:45:00"))
    x = x.sort("minute")
    mins = x["minute"].to_list()
    first_lab.add(mins[0])
    last_lab[mins[-1]] = last_lab.get(mins[-1], 0) + 1
    nbar[len(mins)] = nbar.get(len(mins), 0) + 1
    cl = dict(zip(mins, [float(z) for z in x["close"].to_list()]))
    eq += int(dclose[(d, c)] == cl[mins[-1]])
    before = [m_ for m_ in mins if m_ <= "09:29:00"]
    last = cl[before[-1]]
    grid = []
    for t in range(9 * 60 + 29, 13 * 60 + 30):
        lab = f"{t // 60:02d}:{t % 60:02d}:00"
        if lab in cl:
            last = cl[lab]
        else:
            miss_days[d] = miss_days.get(d, 0) + 1
        grid.append(last)
    lp = np.log(np.array(grid))
    for h, acc in TXRV.items():
        rr = np.diff(lp[::h])
        acc.append(float(rr @ rr))
    r1 = np.diff(lp)
    tx_p1.append(float(r1[1:] @ r1[:-1]))
    tx_ss.append(float(r1 @ r1))
put(39, f"TX near month 2025: {len(tx_days)} days; first label {sorted(first_lab)}; last label counts {dict(sorted(last_lab.items()))}; "
        f"bars a day {dict(sorted(nbar.items()))}; last bar's close = daily close on {eq} of {len(tx_days)}; minutes without a "
        f"bar in 09:29-13:29: {dict(miss_days)}")
TXA = {h: np.array(val) for h, val in TXRV.items()}
keep = np.array([d not in miss_days for d in tx_days])
txr = ", ".join(f"{h}m {float(TXA[h].mean() / TXA[5].mean()):.4f}" for h in (1, 10, 15, 30))
txr_k = ", ".join(f"{h}m {float(TXA[h][keep].mean() / TXA[5][keep].mean()):.4f}" for h in (1, 10, 15, 30))
put(40, f"TX 2025 mean RV(h)/RV(5m): {txr}; without the {len(miss_days)} locked days: {txr_k}; pooled rho_1 of 1-minute "
        f"returns {sum(tx_p1) / sum(tx_ss):.4f}; annualized sqrt(A mean RV): " +
        ", ".join(f"{h}m {v(100 * math.sqrt(A * float(TXA[h].mean())), 4, 1, 2)}%" for h in (1, 5, 10, 15, 30)))
idx25 = np.flatnonzero(m25)
assert [rv_dates[i] for i in idx25] == tx_days
ixv = ", ".join(f"{name} {v(100 * math.sqrt(A * float(np.mean(RV[name][m25]))), 4, 1, 2)}%" for name, _ in IV)
rat = ", ".join(f"{name} {float(np.mean(RV[name][m25])) / float(TXA[h].mean()):.3f}" for name, h in
                (("1m", 1), ("5m", 5), ("10m", 10), ("15m", 15), ("30m", 30)))
put(41, f"TAIEX 2025 annualized sqrt(A mean RV(h)): {ixv}; index/TX mean RV: {rat}; TAIEX 2025 pooled rho_1 of 1-minute "
        f"returns {rows_1m['2025'][0]:.4f}")
aus = []
for s in (60, 15, 10, 5):
    m = reg == s
    aus.append(f"{s}s: frozen on {int(PA['frozen_all'][m].sum())} of {int(m.sum())} days, share of RV(5m) "
               f"{float(PA['auct2'][m].mean() / np.mean(RV['5m'][m])):.4f}")
put(42, "closing auction (values from 13:25:00 + one step to 13:30:00 - one step all equal; (ln P_13:30 - ln P_13:25)^2 "
        "over mean RV(5m), against 1/48 = 0.0208): " + "; ".join(aus))
mo = np.isin(np.array(rv_dates), [dates[i] for i in oos])
put(43, f"o2 share of V: mean 1e4 o2 / mean V, all {len(rv_dates)} days {float(np.mean(1e4 * O2) / np.mean(Vt['15m'])):.4f}, "
        f"OOS days {float(np.mean(1e4 * O2[mo]) / np.mean(Vt['15m'][mo])):.4f}; " +
        ", ".join(f"{s}s {float(np.mean(O2[reg == s]) / np.mean(O2[reg == s] + RV['15m'][reg == s])):.4f}" for s in (60, 15, 10, 5)))
y2 = y[i05:] ** 2
dV = Vt["15m"] - y2
nl_all = math.floor(4 * (len(dV) / 100) ** (2 / 9))
y2o = y[oos] ** 2
dVo = V15[oos] - y2o
put(44, f"mean V {np.mean(Vt['15m']):.4f} vs mean r^2 {np.mean(y2):.4f} %^2 over the 5,351 days: ratio {np.mean(Vt['15m']) / np.mean(y2):.4f}, "
        f"difference t-stat (Newey-West, {nl_all} lags) {dV.mean() / nw_se(dV, nl_all):.2f}; OOS days ratio "
        f"{V15[oos].mean() / y2o.mean():.4f}, t {dVo.mean() / nw_se(dVo, 9):.2f}; V(5m) ratio {np.mean(Vt['5m']) / np.mean(y2):.4f}, "
        f"V(30m) {np.mean(Vt['30m']) / np.mean(y2):.4f}; by year V/r^2: " +
        ", ".join(f"{yy} {np.mean(Vt['15m'][ryear == yy]) / np.mean(y2[ryear == yy]):.3f}" for yy in ("2008", "2020", "2024", "2025")))

# ---------------------------------------------------------------- section 6: forecast evaluation
nl = math.floor(4 * (len(oos) / 100) ** (2 / 9))
put(45, f"W {W} = round(5A); first OOS day {dates[first]} (window {dates[first - W]} .. {dates[first - 1]}); OOS days {len(oos)} "
        f"({dates[oos[0]]} .. {dates[oos[-1]]}); refits per model {len(refits['normal'])}; Newey-West lags {nl}")
pr = np.array([p for _, p in refits["normal"]])
apr = next(p for d_, p in refits["normal"] if d_ == "2025-04-01")
put(46, f"rolling GARCH normal: alpha {pr[:, 2].min():.4f}..{pr[:, 2].max():.4f}, beta {pr[:, 3].min():.4f}..{pr[:, 3].max():.4f}, "
        f"alpha+beta {(pr[:, 2] + pr[:, 3]).min():.4f}..{(pr[:, 2] + pr[:, 3]).max():.4f}; refit of 2025-04-01: g {apr[0]:.4f}, "
        f"omega {apr[1]:.4f}, alpha {apr[2]:.4f}, beta {apr[3]:.4f}, alpha+beta {apr[2] + apr[3]:.4f}")
LOSS: dict[str, dict[str, tuple[Vec, Vec]]] = {}
targets = {"V15": V15[oos], "V5": np.array([Vmap["5m"][dates[i]] for i in oos]),
           "V30": np.array([Vmap["30m"][dates[i]] for i in oos]), "r2": y[oos] ** 2}
tab = []
for k in FC:
    f = FC[k][oos]
    h = targets["V15"]
    se_ = (h - f) ** 2
    ql = qlike(h, f)
    X = np.column_stack([np.ones(len(f)), f])
    bmz, semz, r2mz = ols_hc0(X, h)
    chk = sm.OLS(h, X).fit(cov_type="HC0")
    assert np.allclose(chk.bse, semz, rtol=1e-9)
    tab.append(f"{NAMES[k]}: mean f {v(float(f.mean()), 6, 3)}, MSE {v(float(se_.mean()), 3, 2)}, QLIKE {v(float(ql.mean()), 4, 3)}, a "
               f"{bmz[0]:.3f} ({semz[0]:.3f}), b {bmz[1]:.3f} ({semz[1]:.3f}), t(b=1) {(bmz[1] - 1) / semz[1]:.2f}, "
               f"R-squared {v(r2mz, 4, 3)}")
put(47, f"target V (mean {targets['V15'].mean():.4f} %^2): " + "; ".join(tab))
dl = []
for k in ("garch_t", "ewma", "roll60", "v_prev", "ewma_v"):
    for lname, fn in (("MSE", lambda h, f: (h - f) ** 2), ("QLIKE", qlike)):
        d = fn(targets["V15"], FC[k][oos]) - fn(targets["V15"], FC["garch_n"][oos])
        se_nw = nw_se(d, nl)
        if k == "ewma" and lname == "QLIKE":
            hac = sm.OLS(d, np.ones(len(d))).fit(cov_type="HAC", cov_kwds={"maxlags": nl})
            assert abs(float(hac.bse[0]) - se_nw) < 1e-10 * se_nw
        tt = d.mean() / se_nw
        dl.append(f"{NAMES[k]} {lname} {d.mean():+.4f} (SE {se_nw:.4f}, t {v(tt, 2, 1)}, p {2 * stats.norm.sf(abs(tt)):.4f})")
put(48, "loss minus GARCH normal's, V target: " + "; ".join(dl))
rob = []
for tg in ("V5", "V30", "r2"):
    h = targets[tg]
    ql_ = {k: float(qlike(h, FC[k][oos]).mean()) for k in FC}
    ms_ = {k: float(((h - FC[k][oos]) ** 2).mean()) for k in FC}
    order_q = sorted(FC, key=lambda k: ql_[k])
    order_m = sorted(FC, key=lambda k: ms_[k])
    rob.append(f"{tg}: QLIKE order {', '.join(NAMES[k] for k in order_q)} ({ql_[order_q[0]]:.4f} .. {ql_[order_q[-1]]:.4f}); "
               f"MSE order {', '.join(NAMES[k] for k in order_m)}")
order_v = sorted(FC, key=lambda k: float(qlike(targets["V15"], FC[k][oos]).mean()))
put(49, f"V target QLIKE order {', '.join(NAMES[k] for k in order_v)}; " + "; ".join(rob))
mzr = []
for tg in ("V15", "r2"):
    X = np.column_stack([np.ones(len(oos)), FC["garch_n"][oos]])
    bmz, semz, r2mz = ols_hc0(X, targets[tg])
    mzr.append(f"{tg}: a {bmz[0]:.4f} ({semz[0]:.4f}), b {bmz[1]:.4f} ({semz[1]:.4f}), t(b=1) {(bmz[1] - 1) / semz[1]:.2f}, "
               f"R-squared {r2mz:.4f}")
put(50, "Mincer-Zarnowitz, GARCH normal (HC0): " + "; ".join(mzr) + "; Andersen-Bollerslev's 0.047 and 0.026 against squared "
        "returns (SOURCES)")
oy = np.array([dates[i][:4] for i in oos])
by = []
win_e = 0
for yy in sorted(set(oy)):
    m = oy == yy
    qn = float(qlike(targets["V15"][m], FC["garch_n"][oos][m]).mean())
    qe = float(qlike(targets["V15"][m], FC["ewma"][oos][m]).mean())
    qp = float(qlike(targets["V15"][m], FC["v_prev"][oos][m]).mean())
    win_e += int(qn < qe)
    by.append(f"{yy} ({int(m.sum())}) {qn:.4f} / {qe:.4f} / {qp:.4f}")
put(51, "QLIKE by year, GARCH normal / EWMA / yesterday's V: " + "; ".join(by) + f"; GARCH normal below EWMA in {win_e} of "
        f"{len(set(oy))} years")
iso = [dt.date.fromisoformat(d).isocalendar()[:2] for d in dates]
w25 = sorted({iso[i] for i in oos if dates[i].startswith("2025")})
wk = []
for w_ in w25:
    ids = [i for i in oos if iso[i] == w_ and dates[i].startswith("2025")]
    wk.append((dates[ids[-1]], ids))
i_w = next(j for j, (_, ids) in enumerate(wk) if i7 in ids)
_, ids7 = wk[i_w]
put(52, f"2025 weekly points: {len(wk)} weeks; week of 2025-04-07 ({dates[ids7[0]]}..{dates[ids7[-1]]}, {len(ids7)} sessions): "
        f"realized sqrt(A mean V) {ann(float(V15[ids7].mean())):.2f}%, GARCH normal {ann(float(FC['garch_n'][ids7].mean())):.2f}%, "
        f"EWMA {ann(float(FC['ewma'][ids7].mean())):.2f}%, yesterday's V {ann(float(FC['v_prev'][ids7].mean())):.2f}%; "
        f"2025 means: realized {ann(float(V15[[i for _, ids in wk for i in ids]].mean())):.2f}%")
sens = []
for wv in (1000, 2461):
    rg2 = rolling_garch(wv, False)
    f0 = next(i for i in starts if i >= wv)
    o2_ = np.arange(f0, T)
    qn = float(qlike(V15[o2_], rg2["normal"][o2_]).mean())
    qt = float(qlike(V15[o2_], rg2["t"][o2_]).mean())
    qe = float(qlike(V15[o2_], ew[o2_]).mean())
    sens.append(f"W={wv}: first OOS {dates[f0]}, {len(o2_)} days, QLIKE normal {qn:.4f}, t {qt:.4f}, EWMA {qe:.4f}")
put(53, "; ".join(sens))
wkall: dict[tuple[int, int], list[int]] = {}
for i, w_ in enumerate(iso):
    wkall.setdefault(w_, []).append(i)
wends = [ids[-1] for ids in wkall.values()]
ig, ie = int(np.argmax(cvn)), int(np.argmax(ew[:T]))
extra = sorted({ig, ie} - set(wends))
real_w = [(ids[-1], ann(float(np.mean(V15[ids])))) for ids in wkall.values() if dates[ids[0]] >= "2005-01-03"]
jr = int(np.argmax([x for _, x in real_w]))
put(54, f"weekly chart: {len(wends)} ISO weeks (last session of each), plus {len(extra)} extreme dates; GARCH normal sigma_t max "
        f"{ann(float(cvn[ig] ** 2)):.2f}% a year on {dates[ig]}; EWMA sigma_t|t-1 max {ann(float(ew[ie])):.2f}% on {dates[ie]}; "
        f"weekly realized max {real_w[jr][1]:.2f}% (week ending {dates[real_w[jr][0]]}); realized weeks {len(real_w)}")

# ---------------------------------------------------------------- knowledge checks and problems
k1 = [b1[0] + b1[1] * x**2 for x in (3.0, 0.5)]
k1p = [1.1779 + 0.1960 * x**2 for x in (3.0, 0.5)]
put(55, f"KC 2: ARCH(1) fit after |r - rbar| = 3% and 0.5%: {k1[0]:.4f} and {k1[1]:.4f} %^2 (sd {math.sqrt(k1[0]):.4f}%, "
        f"{math.sqrt(k1[1]):.4f}%); from the printed 1.1779 and 0.1960: {k1p[0]:.4f}, {k1p[1]:.4f} (sd {v(math.sqrt(k1p[0]), 4, 2)}%, "
        f"{v(math.sqrt(k1p[1]), 4, 2)}%)")
put(56, f"lam 0.97: 1/(1-lam) {v(1 / 0.03, 4, 1)}; mean lag lam/(1-lam) {v(0.97 / 0.03, 4, 1)}; weight half-life "
        f"{v(math.log(0.5) / math.log(0.97), 4, 1)} days")
put(57, f"alpha+beta 0.98: half-life {v(hl_of(0.98), 4, 1)}; 0.5/(1-0.98) {0.5 / 0.02:.1f}; 1/(1-0.98) {1 / 0.02:.1f}; "
        f"alpha+beta 0.990978 (t fit): {hl_of(0.990978):.2f}")
put(58, f"QLIKE at f = V/2: {2 - math.log(2) - 1:.4f}; at f = 2V: {0.5 + math.log(2) - 1:.4f}; MSE with V = 1: "
        f"{(1 - 0.5) ** 2:.2f} and {(1 - 2) ** 2:.2f}")
u2 = 0.025 / (1 - 0.09 - 0.89)
u2b = 0.025 / (1 - 0.89)
put(59, f"Problem 2: omega/(1-alpha-beta) {u2:.4f} %^2, annualized sqrt(246.12 x) {math.sqrt(246.12 * u2):.4f}%; omega/(1-beta) "
        f"{u2b:.4f} %^2 -> {v(math.sqrt(246.12 * u2b), 4, 1)}%; sqrt(1.25) {math.sqrt(u2):.4f}% (a day)")
put(60, f"Problem 5: 1 + rho_1 with rho_1 = -0.40: {1 - 0.40:.2f}; 1 + 2 rho_1 {1 - 0.80:.2f}; 1 - rho_1 {1 + 0.40:.2f}")
put(61, f"KC 6: 15-second days, RV(30s)/RV(15s) = {np.mean(RV['30s'][m15]) / np.mean(RV['15s'][m15]):.4f} (file); 1 + pooled "
        f"rho_1 (raw) {1 + r15:.4f}")
put(62, f"KC 5: robust/classic SE ratio: alpha {ser[2] / sen[2]:.3f}, beta {ser[3] / sen[3]:.3f}, omega {ser[1] / sen[1]:.3f}, "
        f"g {ser[0] / sen[0]:.3f}")
z5 = -4.107   # LM5's threshold in standard deviations (make_lab05.py:529)
xo = (y[oos] - np.array([next(p for d_, p in refits["normal"] if d_[:7] == dates[i][:7])[0] for i in oos])) / np.sqrt(FC["garch_n"][oos])
put(63, f"standardized residuals at or below -4.107: in-sample GARCH normal {int((xin <= z5 + EPS).sum())} of {T} (normal model expects "
        f"{T * stats.norm.cdf(z5):.3f}); raw returns standardized by TR23's s: {int(((y - y.mean()) / y.std() <= z5 + EPS).sum())}; "
        f"out of sample (rolling GARCH normal) {int((xo <= z5 + EPS).sum())} of {len(oos)} (expects {len(oos) * stats.norm.cdf(z5):.3f}); "
        f"smallest in-sample xi {xin.min():.3f} on {dates[int(xin.argmin())]}")
big2 = np.abs(R[:-1]) >= 0.02 - EPS
nxt = np.abs(R[1:])
exi = float(np.mean(np.abs(xin)))
pred = exi * snext[:-1] / 100
put(64, f"after |R| >= 2% ({int(big2.sum())} days): next-day mean |R| {nxt[big2].mean():.4%}, after the others {nxt[~big2].mean():.4%}, "
        f"all {nxt.mean():.4%}; GARCH normal mean |xi| {exi:.4f} x sigma_t+1|t: {pred[big2].mean():.4%} and {pred[~big2].mean():.4%}; "
        f"rho_hat_1 of |r| 0.161 (LM17, lm17.md:392)")
ns = [14400 // h for _, h in IV[:6]]
mv = [float(np.mean(RV[name][m5s]) / np.mean(RV["5m"][m5s])) for name, _ in IV[:6]]
slopes = [(mv[j] - mv[j + 1]) / (ns[j] - ns[j + 1]) for j in range(5)]
put(65, "5-second days, rise of mean RV(h)/RV(5m) per extra return a day between neighbouring intervals (constant under iid "
        "noise): " + ", ".join(f"{IV[j][0]}-{IV[j + 1][0]} {s_ * 1e3:.3f}e-3" for j, s_ in enumerate(slopes)))
put(66, "by year, RV(10m)/RV(5m) - 1 (file; approximates the 5-minute rho_1 by A26-34): " +
        ", ".join(f"{yy} {float(np.mean(RV['10m'][ryear == yy]) / np.mean(RV['5m'][ryear == yy]) - 1):.3f}" for yy in sorted(set(ryear))))

print("\n".join(OUT))
