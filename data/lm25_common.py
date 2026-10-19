"""Shared data and helpers for LM25 (Time Series I): data/lm25_numbers.py and data/lm25_charts.py import this file.

Not a script: `uv run python data/lm25_numbers.py` and `uv run python data/lm25_charts.py` run it (after
data/vol3_series.py and data/vol4_series.py). It writes nothing.

Inputs (git-ignored, built and checked by the series scripts):
  data/processed/vol4_tx23.parquet  TX23 (data/vol4_series.py): one row per TR23 date, 2003-01-02 .. 2026-10-08;
                                    S the TAIEX price close, F the settlement of the TX near-month contract held from
                                    that close (rolled at the close of the day before each contract's last trading
                                    day), basis = ln(F/S), rF and rS the roll-free daily log changes, days to the held
                                    contract's last trading day, roll, volume.
  data/processed/vol3_taiex.parquet TR23 (data/vol3_series.py): the TAIEX total-return index (tr), the price index
                                    (price) and the simple total return R.

Conventions (the module states each one where it is used; plans/vol-4.md, "LM25", and plans/vol-4-anchors.md):
  * samples, never mixed in one statistic: TX23 (5,850 dates, 5,849 changes) for the log basis b and ln S; D (the
    5,834 TX23 dates whose held contract expires inside the sample) wherever realized dividends enter; TR23's 5,849 log
    returns r = ln(1 + R) for the autocorrelation tests; a window (a limit regime, a year) uses its own dates only;
  * the basis in basis points (1 bp = 1e-4 log units); s divides by the number of terms, a regression's s_eps by
    T - d; rho_hat_k uses the full-sample mean and divisor T (LM19's (19.5)); PACF by OLS;
  * quantiles and medians are F_hat^{-1}(u) (numpy method="inverted_cdf"); LM18's batch standard error;
  * simulations: np.random.default_rng([e, 20261011]), created once per experiment; walks x_t = z_1 + ... + z_t;
  * ARMA at the likelihood maximum (method="innovations_mle", a restart that must not raise the log-likelihood),
    standard errors from -l'' (cov_type="approx").
"""
import math
import warnings
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl
from numpy.typing import NDArray
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import KPSSResult, adfuller, kpss

Vec = NDArray[np.float64]

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PROC = HERE / "processed"
SEED = 20261011
EPS = 1e-12
RF = 0.02                      # LM6's financing-rate proxy, continuously compounded
LIMIT_SWITCH = "2015-06-01"    # TWSE's daily limit widened from 7% to 10% on this date
BP = 1e4


# ---------------------------------------------------------------- helpers
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
    """(25.2): ln(1/2) / ln(phi), 0 < phi < 1."""
    return math.log(0.5) / math.log(phi)


def rho_hat(x: Vec, k: int) -> float:
    """LM19's (19.5): full-sample mean, divisor T in numerator and denominator."""
    c = x - x.mean()
    return float(c[k:] @ c[:-k] / (c @ c))


def se_rob(x: Vec, k: int) -> float:
    """(25.4): sqrt(sum_{t>k} c_t^2 c_{t-k}^2) / sum_t c_t^2, c the centred series."""
    c = x - x.mean()
    return math.sqrt(float((c[k:] ** 2 * c[:-k] ** 2).sum())) / float(c @ c)


def vr_over(x: Vec, m: int) -> float:
    """LM19's (19.8): overlapping m-day sums centred at m*mean, mean square over m times the daily variance."""
    cs = np.concatenate([[0.0], np.cumsum(x)])
    sums = cs[m:] - cs[:-m]
    return float(((sums - m * x.mean()) ** 2).mean()) / (m * float(((x - x.mean()) ** 2).mean()))


class ArmaFit:
    """ARMA(p, q) on x at the likelihood maximum: innovations MLE, then a restart that must not raise l."""

    def __init__(self, x: Vec, order: tuple[int, int, int] = (1, 0, 1)) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.model: Any = ARIMA(x, order=order)
            f_in = self.model.fit(method="innovations_mle")
            self.res: Any = self.model.fit(start_params=np.asarray(f_in.params), cov_type="approx")
            self.llf_default = float(self.model.fit().llf)
        self.llf = float(self.res.llf)
        self.llf_innov = float(f_in.llf)
        assert self.llf - self.llf_innov < 1e-6, "a restart raised the log-likelihood"
        assert self.llf >= self.llf_default - 1e-9, "the default fit beats the maximum"
        self.params = np.asarray(self.res.params, dtype=float)
        self.bse = np.asarray(self.res.bse, dtype=float)
        self.aic = float(self.res.aic)

    def bse_of(self, cov_type: str) -> Vec:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return np.asarray(self.model.smooth(self.params, cov_type=cov_type).bse, dtype=float)


def noise_split(phi: float, theta: float, sig2: float) -> tuple[float, float, float, float]:
    """(25.9): a persistent AR(1) plus white noise read from ARMA(1,1): sigma_u^2, sigma_zeta^2, sigma_x^2 and the
    variance of a daily change."""
    su2 = -theta * sig2 / phi
    sz2 = (1 + theta**2) * sig2 - (1 + phi**2) * su2
    sx2 = sz2 / (1 - phi**2)
    return su2, sz2, sx2, 2 * sx2 * (1 - phi) + 2 * su2


def arma_acf(phi: float, theta: float, k: int) -> float:
    """ARMA(1,1) autocorrelation at lag k >= 1."""
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
    levels, drawn in chunks of 500 rows, and statsmodels' MacKinnon 5% point for length - 1 observations."""
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
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        crit = adfuller(x[0], maxlag=0, autolag=None, regression="c", result_object=True).critical_values
    return out, float(crit["5%"])


def batch_se(x: Vec, fn: Callable[[Vec], float]) -> float:
    """LM18's batch standard error: 20 equal consecutive batches, standard deviation with divisor 20, over sqrt(20)."""
    vals = np.array([fn(part) for part in np.split(x, 20)])
    return float(vals.std(ddof=0) / math.sqrt(20))


def quant(x: Vec, u: float) -> float:
    return float(np.quantile(x, u, method="inverted_cdf"))


def q5(x: Vec) -> float:
    return quant(x, 0.05)


def med(x: Vec) -> float:
    return quant(x, 0.5)


def spurious(e: int, length: int, n: int) -> tuple[Vec, Vec, tuple[float, float, float, float], Vec]:
    """Slope t-stats and R-squared of y on x for n pairs of independent random walks (one pair at a time, x then y);
    the first pair's slope, t, R-squared and the t of its differenced regression; the first pair's two paths."""
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
_tx = PROC / "vol4_tx23.parquet"
_tr = PROC / "vol3_taiex.parquet"
assert _tx.exists() and _tr.exists(), "run data/vol3_series.py and data/vol4_series.py first"
tx = pl.read_parquet(_tx).sort("date")
tr = pl.read_parquet(_tr).sort("date")
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
lnF = np.log(F)
db = np.diff(b)                          # rolled changes
db_free = (rF - rS)[1:]                  # roll-free changes (one contract)
tau = days / 365.0
qt = np.full(N, np.nan)
sess = np.full(N, -1)
for _i in range(N):
    if last[_i] in idx:
        _j = idx[last[_i]]
        qt[_i] = math.log(TRI[_j] / TRI[_i]) - math.log(S[_j] / S[_i])
        sess[_i] = _j - _i
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
