"""LM25 anchors (Time Series I: ARMA, Unit Roots and Cointegration): every number the Stage 1 brief quotes.

Revised 2026-10-19 after the cross-check (X9, X13, X16, X24, X37) and the independent recomputation.

Reads TX23 from data/processed/vol4_tx23.parquet (built and checked by data/vol4_series.py: one row per TR23 date,
2003-01-02 -> 2026-10-08; S the TAIEX price close, F the settlement of the TX near-month contract held from that
close, rolled at the close of the day before each contract's last trading day; basis = ln(F/S); rF and rS the
roll-free daily log changes of the position and of the index; days = calendar days to the held contract's last
trading day) and TR23 from data/processed/vol3_taiex.parquet (columns date, tr, price, R, Rp; R the total-return
index's simple daily return, null on the first row; built and checked by data/vol3_series.py). Run both builders
first. The script writes nothing.

Conventions.
- Samples, never mixed in one statistic: TX23, 5,850 dates (5,849 daily changes) for the log basis
  b_t = ln F_t - ln S_t and for ln S_t; D, the 5,834 TX23 dates whose held contract's last trading day lies in the
  sample (2003-01-02 -> 2026-09-14), wherever the realized dividends to expiry enter (the four versions of the basis,
  the season and expiry exhibits); TR23's T = 5,849 log returns r_t = ln(1 + R_t), 2003-01-03 -> 2026-10-08, for
  the autocorrelation tests. TX23's S is TR23's price column (the price index); TR23's R is the total-return index.
  The two limit regimes split TX23 at 2015-06-01 (a stability check); the year 2025 is LM6's year. A statistic of a
  window (a regime, a year) uses only that window's dates: its changes are differences within the window, so the
  change into its first date is left out.
- Units: the log basis in basis points (1 bp = 1e-4 in log units). Years = calendar days between TR23's first and
  last close / 365.25; A = T / years = 246.12; a simulated year has round(A) = 246 sessions. LM6's conventions for
  the fair basis: r_f = 2% (continuously compounded proxy), tau = calendar days to the last trading day / 365
  (actual/365), realized dividends q_real*tau = ln(TR_L/TR_t) - ln(S_L/S_t), L the held contract's last trading day;
  fair log basis r_f*tau - q_real*tau; the residual of (6.25) in log form, ln(F/F_fair) = b - fair.
- Divisors: a sample mean, variance or standard deviation divides by the number of terms (s, divisor T); a
  regression's residual variance divides by T - d (s_eps); sample autocorrelations use the full-sample mean and
  divisor T in numerator and denominator (LM19's (19.5); statsmodels' acf with adjusted=False). The partial
  autocorrelation at lag k is the last coefficient of an OLS regression of x_t on a constant and x_{t-1}, ...,
  x_{t-k} (statsmodels' pacf with method="ols"; its default is "ywadjusted").
- Quantiles and medians, of data and of simulated values, are F_hat^{-1}(u) (numpy method="inverted_cdf"); a median
  is F_hat^{-1}(1/2), the lower middle value of an even sample.
- Robust (HC0-type) standard error of rho_hat_k: sqrt(sum_{t>k} c_t^2 c_{t-k}^2) / sum_t c_t^2, c_t = r_t - r_bar.
  Variance ratio: LM19's (19.8), the mean square of the overlapping m-day sums of r centred at m*r_bar (divisor
  T - m + 1, the number of sums) over m times the daily variance (divisor T). Its test (25.6) divides VR(m) - 1 by
  SE_iid = sqrt(2(2m - 1)(m - 1)/(3mT)) or by SE_rob = sqrt(sum_{k<m} [2(1 - k/m)]^2 SE_rob(rho_hat_k)^2), the
  large-sample variances of 2 sum_{k<m} (1 - k/m) rho_hat_k (LM19's identity column, a check row here); two-sided,
  normal reference.
- Tests: a normal reference and two-sided unless named otherwise; Dickey-Fuller, ADF and Engle-Granger are one-sided
  (reject for small values), KPSS one-sided (reject for large values), Ljung-Box the upper tail of chi2_K.
- Dickey-Fuller: OLS of the change on a constant (and, where named, a trend) and the lagged level, classical standard
  error with divisor T - d. "Rolled" changes difference the near-month series as stored (a roll day's change links
  two contracts); "roll-free" changes are rF - rS (one contract). ADF, KPSS, Engle-Granger and Ljung-Box come from
  statsmodels 0.15.0 (adfuller and kpss with result_object=True, autolag="AIC", nlags="auto"; coint with
  return_results=True; acorr_ljungbox). Error-correction slopes carry classical and White (HC0, no small-sample
  factor) standard errors.
- ARMA: statsmodels' ARIMA(order=(p, 0, q)) on the basis in bp ("const" is the process mean), fitted at the maximum
  of the Gaussian likelihood: method="innovations_mle", then a restart of the state-space optimizer from those
  estimates, asserting that the log-likelihood rises by less than 1e-6 (the default fit stops short of the maximum).
  Standard errors from the observed information -l'' (cov_type="approx", a numerical Hessian), checked against a
  central-difference Hessian of the log-likelihood; A25-71 compares statsmodels' "oim" (Harvey's information
  formula), "opg" and the sandwich "robust_approx", checked against a hand sandwich.
- Guard: counts against a threshold use the book's guard (b < -1e-12 for a negative basis) and are checked exactly
  with Fraction on the settlement (whole points) and the two-decimal TAIEX close.
- Simulation: each experiment creates its generator once, at its start, as np.random.default_rng([e, 20261011]),
  e the experiment number in the brief: 1 the Dickey-Fuller null at 5,850 levels (10,000 random walks); 2 spurious
  regressions at 5,850 sessions (1,000 independent pairs; the first pair drawn is the plotted one); 3 the
  Dickey-Fuller null at 246 levels (100,000 walks); 4 spurious regressions at 246 sessions (1,000 pairs). A walk of
  n levels is x_t = z_1 + ... + z_t, t = 1..n, z iid standard normal: walks are drawn in chunks of 500 rows of n
  draws (rng.standard_normal((500, n)), cumulated along each row); a pair is rng.standard_normal((2, n)) cumulated
  along each row, x first, then y, one pair at a time. Standard errors: of a share p of n draws, sqrt(p(1 - p)/n);
  of a quantile or a median (LM18), the standard deviation with divisor 20 of its values on 20 equal consecutive
  batches of the draws, over sqrt(20).
- Rounding: v(x, shown, *printed) prints x to `shown` decimals and appends " NEAR(d)" for each printed precision d
  (decimals) at which x lies within a tenth of a unit of the d-th decimal of a rounding boundary; sci() does the same
  for a mantissa. Every printed form of the brief is checked here at the precision it is printed.

Prints one line per anchor, "A25-NN <value>", in ID order; a withdrawn anchor keeps its line.

Run:  PYTHONUTF8=1 uv run python data/vol4_anchors_lm25.py [repository root]
"""
import datetime as dt
import json
import math
import sys
import warnings
from collections.abc import Callable
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl
from numpy.typing import NDArray
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import KPSSResult, acf, adfuller, coint, kpss, pacf

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
SEED = 20261011
EPS = 1e-12
RF = 0.02                      # LM6's financing-rate proxy, continuously compounded
LIMIT_SWITCH = "2015-06-01"    # the 10% daily limit from this date (7% before)
BP = 1e4
Vec = NDArray[np.float64]

OUT: list[str] = []


def put(nn: int, value: str) -> None:
    assert nn == len(OUT) + 1, f"anchor A25-{nn:02d} out of order"
    OUT.append(f"A25-{nn:02d} {value}")


def near(x: float, d: int) -> bool:
    """True when x, printed to d decimals, lies within a tenth of a unit of the d-th decimal of a rounding boundary."""
    y = abs(x) * 10**d
    return abs(y - math.floor(y) - 0.5) < 0.1


def v(x: float, shown: int, *printed: int) -> str:
    flags = [str(d) for d in printed if near(x, d)]
    return f"{x:.{shown}f}" + (f" NEAR({','.join(flags)})" if flags else "")


def sci(x: float, shown: int, printed: int) -> str:
    """x in scientific notation; NEAR when its mantissa, printed to `printed` decimals, is near a boundary."""
    mant = abs(x) / 10 ** math.floor(math.log10(abs(x)))
    return f"{x:.{shown}e}" + (" NEAR" if near(mant, printed) else "")


def ols(X: Vec, y: Vec) -> tuple[Vec, Vec, Vec]:
    """OLS coefficients, classical standard errors (divisor T - d) and residuals."""
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ beta
    n, d = X.shape
    s2 = float(res @ res) / (n - d)
    se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
    return beta, se, res


def hc0(X: Vec, res: Vec) -> Vec:
    """White's heteroskedasticity-consistent standard errors, no small-sample factor."""
    xtxi = np.linalg.inv(X.T @ X)
    meat = (X * res[:, None] ** 2).T @ X
    return np.sqrt(np.diag(xtxi @ meat @ xtxi))


def df_reg(level: Vec, change: Vec | None = None) -> tuple[float, float, float, float, Vec]:
    """Dickey-Fuller regression change_t = c + delta*level_{t-1}: c, delta, se(delta), t-stat, residuals."""
    dy = np.diff(level) if change is None else change
    X = np.column_stack([np.ones(len(dy)), level[:-1]])
    beta, se, res = ols(X, dy)
    return float(beta[0]), float(beta[1]), float(se[1]), float(beta[1] / se[1]), res


def half_life(phi: float) -> float:
    return math.log(0.5) / math.log(phi)


def rho_hat(x: Vec, k: int) -> float:
    c = x - x.mean()
    return float(c[k:] @ c[:-k] / (c @ c))


def se_rob(x: Vec, k: int) -> float:
    c = x - x.mean()
    return math.sqrt(float((c[k:] ** 2 * c[:-k] ** 2).sum())) / float(c @ c)


def vr_over(x: Vec, m: int) -> float:
    """LM19's (19.8): overlapping m-day sums centred at m*mean, mean square over m times the daily variance."""
    cs = np.concatenate([[0.0], np.cumsum(x)])
    sums = cs[m:] - cs[:-m]
    return float(((sums - m * x.mean()) ** 2).mean()) / (m * float(((x - x.mean()) ** 2).mean()))


class ArmaFit:
    """ARMA(p, q) at the likelihood maximum (see the module docstring)."""

    def __init__(self, x: Vec, order: tuple[int, int, int] = (1, 0, 1)) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.model: Any = ARIMA(x, order=order)
            f_in = self.model.fit(method="innovations_mle")
            self.res: Any = self.model.fit(start_params=np.asarray(f_in.params), cov_type="approx")
            self.llf_default = float(self.model.fit().llf)
        self.llf = float(self.res.llf)
        assert self.llf - float(f_in.llf) < 1e-6, "a restart raised the log-likelihood"
        assert self.llf >= self.llf_default - 1e-9, "the default fit beats the maximum"
        self.params = np.asarray(self.res.params, dtype=float)
        self.bse = np.asarray(self.res.bse, dtype=float)
        self.aic = float(self.res.aic)

    def bse_of(self, cov_type: str) -> Vec:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return np.asarray(self.model.smooth(self.params, cov_type=cov_type).bse, dtype=float)


def shifted(p: Vec, steps: Vec, moves: dict[int, float]) -> Vec:
    q = p.copy()
    for i, s in moves.items():
        q[i] += s * steps[i]
    return q


def hand_hessian_and_scores(fit: ArmaFit) -> tuple[Vec, Vec]:
    """Central-difference Hessian of the log-likelihood and per-observation scores at the fitted parameters."""
    p = fit.params
    h = 1e-5 * np.maximum(1.0, np.abs(p))
    k = len(p)

    def ll(q: Vec) -> float:
        return float(fit.model.loglike(q))

    H = np.empty((k, k))
    for i in range(k):
        for j in range(k):
            H[i, j] = (ll(shifted(p, h, {i: 1, j: 1} if i != j else {i: 2}))
                       - ll(shifted(p, h, {i: 1, j: -1} if i != j else {i: 0}))
                       - ll(shifted(p, h, {i: -1, j: 1} if i != j else {i: 0}))
                       + ll(shifted(p, h, {i: -1, j: -1} if i != j else {i: -2}))) / (4 * h[i] * h[j])
    S = np.column_stack([(np.asarray(fit.model.loglikeobs(shifted(p, h, {i: 1})))
                          - np.asarray(fit.model.loglikeobs(shifted(p, h, {i: -1})))) / (2 * h[i]) for i in range(k)])
    return H, S


def noise_split(phi: float, theta: float, sig2: float) -> tuple[float, float, float, float]:
    """A persistent AR(1) plus white noise read from ARMA(1,1): sigma_u^2, sigma_zeta^2, sigma_x^2, Var(change)."""
    su2 = -theta * sig2 / phi
    sz2 = (1 + theta**2) * sig2 - (1 + phi**2) * su2
    sx2 = sz2 / (1 - phi**2)
    return su2, sz2, sx2, 2 * sx2 * (1 - phi) + 2 * su2


def arma_acf(phi: float, theta: float, k: int) -> float:
    r1 = (1 + phi * theta) * (phi + theta) / (1 + 2 * phi * theta + theta**2)
    return r1 * phi ** (k - 1)


def hl_se(phi: float, se_phi: float) -> float:
    """Delta method (LM20's (20.8)) for the half-life ln(1/2)/ln(phi)."""
    return abs(math.log(0.5) / (phi * math.log(phi) ** 2)) * se_phi


def adf(x: Vec, reg: str = "c") -> tuple[float, float, int]:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        a = adfuller(x, regression=reg, autolag="AIC", result_object=True)
    return float(a.statistic), float(a.pvalue), int(a.lags)


def kpss_c(x: Vec) -> tuple[float, float, int]:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        k = kpss(x, regression="c", nlags="auto", result_object=True)
    assert isinstance(k, KPSSResult)
    return float(k.statistic), float(k.pvalue), int(k.lags)


def df_null(e: int, length: int, n: int) -> tuple[Vec, float]:
    """n Dickey-Fuller t-stats (constant, no lags) of standard normal random walks x_t = z_1 + ... + z_t of `length`
    levels, and statsmodels' MacKinnon 5% point for length - 1 observations."""
    rng = np.random.default_rng([e, SEED])
    out = np.empty(n)
    x = np.zeros((500, length))
    for c0 in range(0, n, 500):
        x = np.cumsum(rng.standard_normal((500, length)), axis=1)
        dy = np.diff(x, axis=1)
        xl = x[:, :-1]
        xm = xl - xl.mean(axis=1, keepdims=True)
        ym = dy - dy.mean(axis=1, keepdims=True)
        sxx = (xm * xm).sum(axis=1)
        d = (xm * ym).sum(axis=1) / sxx
        res = ym - d[:, None] * xm
        s2 = (res * res).sum(axis=1) / (length - 1 - 2)
        out[c0:c0 + 500] = d / np.sqrt(s2 / sxx)
    crit = adfuller(x[0], maxlag=0, autolag=None, regression="c", result_object=True).critical_values
    return out, float(crit["5%"])


def batch_se(x: Vec, fn: Callable[[Vec], float]) -> float:
    """LM18's batch standard error: 20 equal consecutive batches, standard deviation with divisor 20, over sqrt(20)."""
    vals = np.array([fn(part) for part in np.split(x, 20)])
    return float(vals.std(ddof=0) / math.sqrt(20))


def q5(x: Vec) -> float:
    return float(np.quantile(x, 0.05, method="inverted_cdf"))


def med(x: Vec) -> float:
    return float(np.quantile(x, 0.5, method="inverted_cdf"))


def spurious(e: int, length: int, n: int) -> tuple[Vec, Vec, tuple[float, float, float, float], Vec]:
    """Slope t-stats and R-squared of y on x for n pairs of independent random walks; the first pair's slope, t,
    R-squared and the t of its differenced regression; the first pair's two paths."""
    rng = np.random.default_rng([e, SEED])
    tt, r2 = np.empty(n), np.empty(n)
    first = (0.0, 0.0, 0.0, 0.0)
    paths = np.zeros((2, length))
    for i in range(n):
        xy = np.cumsum(rng.standard_normal((2, length)), axis=1)
        X = np.column_stack([np.ones(length), xy[0]])
        beta, se, res = ols(X, xy[1])
        yc = xy[1] - xy[1].mean()
        tt[i] = beta[1] / se[1]
        r2[i] = 1 - float(res @ res) / float(yc @ yc)
        if i == 0:
            bd, sd, _ = ols(np.column_stack([np.ones(length - 1), np.diff(xy[0])]), np.diff(xy[1]))
            first = (float(beta[1]), float(tt[0]), float(r2[0]), float(bd[1] / sd[1]))
            paths = xy
    return tt, r2, first, paths


# ---------------------------------------------------------------- data
tx = pl.read_parquet(PROC / "vol4_tx23.parquet").sort("date")
tr = pl.read_parquet(PROC / "vol3_taiex.parquet").sort("date")
assert tx["date"].to_list() == tr["date"].to_list(), "TX23 and TR23 dates differ"
assert (tx["S"] == tr["price"]).all(), "TX23's S is not TR23's price column"
dates = [str(d) for d in tx["date"].to_list()]
N = len(dates)
idx = {d: i for i, d in enumerate(dates)}
S = tx["S"].to_numpy()
F = tx["F"].to_numpy()
TRI = tr["tr"].to_numpy()
b = tx["basis"].to_numpy()
rF = tx["rF"].to_numpy()
rS = tx["rS"].to_numpy()
roll = tx["roll"].to_numpy()
days = tx["days"].to_numpy()
vol = tx["volume"].to_numpy()
last = [str(d) for d in tx["last_day"].to_list()]
contracts = tx["contract"].to_list()
assert N == 5850 and np.allclose(b, np.log(F / S))
lnS = np.log(S)
db = np.diff(b)                          # rolled changes
db_free = (rF - rS)[1:]                  # roll-free changes (one contract)
tau = days / 365.0
qt = np.full(N, np.nan)
sess = np.full(N, -1)
for i in range(N):
    if last[i] in idx:
        j = idx[last[i]]
        qt[i] = math.log(TRI[j] / TRI[i]) - math.log(S[j] / S[i])
        sess[i] = j - i
D = ~np.isnan(qt)
iD = np.flatnonzero(D)
assert D[: iD[-1] + 1].all(), "the dividend sample D is not a leading block"
fair = RF * tau - qt                     # LM6's fair log basis: carry minus realized dividends
resid = b - fair                         # the residual of (6.25) in log form, ln(F / F_fair)
mon = np.array([int(d[5:7]) for d in dates])
yr = np.array([int(d[:4]) for d in dates])
pre = np.array([d < LIMIT_SWITCH for d in dates])

R = tr["R"].to_numpy()[1:]
assert tr["R"][0] is None
r = np.log1p(R)
T = len(r)
days_cal = (tr["date"][-1] - tr["date"][0]).days
years = days_cal / 365.25
A = T / years
n_year = round(A)

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

# ---------------------------------------------------------------- section 2: stationarity (15-16)
parts = []
for lab, msk in (("before", pre), ("from", ~pre)):
    parts.append(f"{lab} {LIMIT_SWITCH} ({int(msk.sum())} dates): mean S {v(float(S[msk].mean()), 1, 0)}, "
                 f"mean b {v(BP * b[msk].mean(), 3, 1)} bp, s(b) {v(BP * b[msk].std(), 3, 1)} bp")
put(15, "; ".join(parts))
put(16, f"random walk sd 1.2%: 25 sessions {1.2 * math.sqrt(25):.1f}%, 100 sessions {1.2 * math.sqrt(100):.1f}%; "
        f"AR(1) phi 0.9: stationary sd {v(1.2 / math.sqrt(1 - 0.81), 4, 3)}%")

# ---------------------------------------------------------------- section 3: autocorrelation tests (17-26)
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
put(22, f"|r|: Q_LB(10) {v(float(lb_abs[0, 0]), 2, 0)}; rho_hat_1(|r|) {v(rho_abs1, 5, 3)} (LM17 printed 0.161, "
        f"lm17.md:392), robust SE {v(se_rob(np.abs(r), 1), 6, 4)}, robust t {v(rho_abs1 / se_rob(np.abs(r), 1), 3, 1)}")


def vr_test(m: int) -> tuple[float, float, float]:
    w = 2 * (1 - np.arange(1, m) / m)
    vr = vr_over(r, m)
    v_iid = 2 * (2 * m - 1) * (m - 1) / (3 * m * T)
    assert abs(v_iid - float(w @ w) / T) < 1e-15
    v_rob = float((w**2) @ (rob[: m - 1] ** 2))
    return vr, (vr - 1) / math.sqrt(v_iid), (vr - 1) / math.sqrt(v_rob)


vr_rows = []
for m in (2, 5, 10, 20):
    vr, t_i, t_r = vr_test(m)
    vr_rows.append(f"m={m}: VR {v(vr, 5, 4)}, t iid {v(t_i, 3, 2)}, t robust {v(t_r, 3, 2)}")
put(23, "; ".join(vr_rows))
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

# ---------------------------------------------------------------- section 4: AR and MA models (27-34)
put(27, f"MA(1) theta1 -0.36: rho1 {v(-0.36 / (1 + 0.36**2), 5, 3)}; AR(1) phi1 0.5: half-life "
        f"{half_life(0.5):.0f} session")
put(28, f"AR(1) on b (rolled, {len(db)} changes): c {v(BP * c_b, 4, 2)} bp, phi_hat {v(1 + d_b, 5, 4)}, SE "
        f"{v(se_b, 7, 5)}, s_eps {v(BP * math.sqrt(float(res_b @ res_b) / (len(db) - 2)), 3, 1)} bp, half-life "
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
# E10 prints phi1 to five decimals, its SE to four, and the SE to six where the half-life SE is derived from it
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

# ---------------------------------------------------------------- section 5: unit roots (35-42)
t1, crit1 = df_null(1, N, 10_000)
qs1 = np.quantile(t1, [0.01, 0.05, 0.10], method="inverted_cdf")
put(35, f"exp 1, {N} levels, 10,000 walks: quantiles 1% {v(qs1[0], 4, 2)}, 5% {v(qs1[1], 4, 2)} (batch SE "
        f"{v(batch_se(t1, q5), 4, 3)}), 10% {v(qs1[2], 4, 2)}; mean {v(float(t1.mean()), 4, 2)}")
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
put(38, f"exp 3, {n_year} levels, 100,000 walks: 5% {v(q5(t3), 4, 2)} (batch SE {v(batch_se(t3, q5), 4, 3)}); "
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
put(41, f"ADF b 'c' {a_b[0]:.3f} with {a_b[2]} lags; statsmodels' default maximum "
        f"{math.ceil(12 * (len(b) / 100) ** 0.25)} (12 x (T/100)^(1/4) rounded up, T = {len(b)})")
put(42, f"DF on b: {t_b:.4f} against the 5% point {cv['5%']:.4f} (check row)")

# ---------------------------------------------------------------- section 6: spurious regression, cointegration (43-50)
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
lnF = np.log(F)
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
put(47, f"ECM: alpha_F {v(float(bFe[1]), 5, 3)} (classical {seFe[1]:.4f}, White {v(float(hc0(Xl, resF)[1]), 5, 3)}); "
        f"alpha_S {v(float(bSe[1]), 6, 4)} (classical {seSe[1]:.4f}, White {v(float(hc0(Xl, resS)[1]), 5, 3)}); "
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

# ---------------------------------------------------------------- section 7: the basis as a time series (51-60)
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
for mm in range(1, 13):
    msk = D & (mon == mm)
    season.append(f"{mm}: b {v(BP * float(b[msk].mean()), 3, 2)} = fair {v(BP * float(fair[msk].mean()), 3, 2)} + "
                  f"resid {v(BP * float(resid[msk].mean()), 3, 2)} (n {int(msk.sum())})")
put(53, "; ".join(season))
mm_mean = {mm: float(b[D & (mon == mm)].mean()) for mm in range(1, 13)}
bseas = b - np.array([mm_mean[mm] for mm in mon])
versions = (("b", b[D]), ("b - carry", (b - RF * tau)[D]), ("residual", resid[D]), ("b - month mean", bseas[D]))
vt = []
for name, x in versions:
    _, dd, _, tdf, _ = df_reg(x)
    aa = adf(x)
    kk = kpss_c(x)
    fv = ArmaFit(BP * x)
    pp = fv.params
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
for lab, msk in (("before", pre), ("from", ~pre)):
    x = b[msk]
    _, dd, _, tdf, _ = df_reg(x)
    reg_fits[lab] = fv = ArmaFit(BP * x)
    pp = fv.params
    u2, _, _, _ = noise_split(pp[1], pp[2], pp[3])
    stab.append(f"{lab} {LIMIT_SWITCH} ({len(x)}): s(b) {BP * float(x.std()):.2f}, s(change within) "
                f"{BP * float(np.diff(x).std()):.2f}, DF t {tdf:.2f}, AR phi {1 + dd:.4f}, ARMA phi {v(pp[1], 6, 4, 2)} "
                f"theta {v(pp[2], 6, 4)} sigma2 {v(pp[3], 3, 1)}, sigma_u {v(math.sqrt(u2), 4, 2)} bp")
put(56, "; ".join(stab))
m25 = yr == 2025
fit25 = ArmaFit(BP * b[m25])
p25 = fit25.params
u25, _, _, _ = noise_split(p25[1], p25[2], p25[3])
s25 = float(S[m25].mean())
put(57, f"2025 ({int(m25.sum())} dates): ARMA phi {p25[1]:.4f}, theta {p25[2]:.4f}, sigma2 {p25[3]:.1f}; "
        f"sigma_u {v(math.sqrt(u25), 4, 1)} bp; s(change within 2025, {int(m25.sum()) - 1} changes) "
        f"{BP * float(np.diff(b[m25]).std()):.3f} bp; mean S {s25:.2f}")
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
for lab in ("before", "from"):
    pp = reg_fits[lab].params
    p4 = (round(float(pp[1]), 4), round(float(pp[2]), 4), round(float(pp[3]), 1))
    u2, _, x2, var_ch = noise_split(*p4)
    pr.append(f"{lab}: printed ({p4[0]:.4f}, {p4[1]:.4f}, {p4[2]:.1f}) -> sigma_u {v(math.sqrt(u2), 4, 2)} bp, "
              f"persistent sd {v(math.sqrt(x2), 4, 2)}, noise share of Var(change) {v(100 * 2 * u2 / var_ch, 3, 1)}%")
put(63, "P8 " + "; ".join(pr))
put(64, f"P9 DF by hand t {v(t_b, 4, 2)} = adfuller(maxlag=0) {float(a0.statistic):.4f}; roll-free {v(t_f, 4, 2)}; "
        f"half-lives {v(half_life(1 + d_b), 4, 2)}, {v(half_life(1 + d_f), 4, 2)}")
put(65, f"P10 exp 3: 5% {q5(t3):.4f}, MacKinnon {crit3:.4f}; P11 exp 4: share {sh4:.3f}, median R-squared "
        f"{med(r24):.4f} (check row)")
vr5, t5i, t5r = vr_test(5)
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

# ---------------------------------------------------------------- additions of the revision (70-71)
iso = [dt.date.fromisoformat(d).isocalendar() for d in dates]
week_last: dict[tuple[int, int], int] = {}
for i, c in enumerate(iso):
    week_last[(c[0], c[1])] = i
keep = sorted(set(week_last.values()) | {0, i_lo, i_hi, N - 1})
payload = json.dumps({"x": [dates[i] for i in keep], "S": [round(float(S[i]), 2) for i in keep],
                      "b": [round(float(BP * b[i]), 1) for i in keep]}, separators=(",", ":"))
put(70, f"X1 thinned: {len(week_last)} ISO weeks (last session of each) + first date and the two extremes "
        f"= {len(keep)} dates of {N}; JSON of dates, S (2 dp) and b (1 dp) {len(payload.encode())} bytes")
H, Sc = hand_hessian_and_scores(fit_b)
Hinv = np.linalg.inv(-H)
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
    xl_rows.append(f"m={m}: SE {se_diag:.5f} -> {se_full:.5f}, t robust {v((vr_test(m)[0] - 1) / se_full, 4, 2)}")
put(72, "robust VR SE with the cross-lag terms sum_t c_t^2 c_{t-j} c_{t-k} (j != k) kept: " + "; ".join(xl_rows)
        + f"; largest increase {v(100 * (max(ratios) - 1), 2, 0)}%")

print("\n".join(OUT))
