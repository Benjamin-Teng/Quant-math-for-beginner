"""Shared inputs and estimators for LM20 (Estimation Theory and Maximum Likelihood).

Imported by data/lm20_numbers.py and data/lm20_charts.py; it prints nothing and writes nothing.

Inputs (run their builders first):
  * TR23: data/processed/vol3_taiex.parquet (columns date, tr, price, R, Rp; R is the TAIEX total-return index's
    simple daily return, null on the first row), built and checked by data/vol3_series.py from FinMind's
    TaiwanStockTotalReturnIndex (data_id TAIEX, retrieved 2026-10-18): 5,850 closes 2003-01-02 .. 2026-10-08.
  * U28 (Problem 6 only): data/lm10_series.py (Volume II's 28 leaf sector price indices, repaired by
    data/vol2_series.py), T = 4,382 returns 2008-12-02 .. 2026-10-08.
  * LM4's 0050 sample (the delta table's 0050 row and the Example on the normal MLE): column R_0050 of
    data/processed/etf_daily_returns.parquet, 0050's total returns on the 2,902 common dates of 0050 and
    00631L (data/build_series.py).

Conventions (the module's, and plans/vol-4-anchors.md's for A20-nn):
  * T = 5,849 simple returns R_t from 2003-01-03; log returns r = ln(1 + R); tau = calendar days from the first to the
    last close / 365.25 = 23.7645 years; A = T / tau = 246.12. One-day statistics on R; sums (Merton's m-day sums,
    the 23 calendar years 2003-2025, 2003 from its first close) on r.
  * Divisors passed explicitly: s, the central moments m3, m4, skewness m3/s^3 and kurtosis m4/s^4 divide by the
    number of terms (ddof=0); s_u divides by T - 1 (ddof=1). A standard deviation across simulated samples or runs
    divides by their number.
  * Student-t maximum likelihood on the returns in percent: scipy's t.fit as LM15 ran it (on R), refined by
    Nelder-Mead (tolerances 1e-12); standard errors from the inverse of a central-difference Hessian of the negative
    log-likelihood (steps 1e-4 for nu, 1e-5 for location and scale), checked against steps ten times larger.
  * Counts use the guard (R <= -x0 + 1e-12, R >= x0 - 1e-12, R > 1e-12) and are checked exactly with Fraction on the
    two-decimal closes.
  * Seeds: experiment e creates rng = np.random.default_rng([e, 20261011]) once at its start and never reseeds;
    e = 1 the sampling distributions, 2 the coverage table, 3 Problem 11, 4 the spread of experiment 1's t block.
"""
from __future__ import annotations

import sys
from collections.abc import Callable
from fractions import Fraction
from math import log, sqrt
from pathlib import Path

import numpy as np
import polars as pl
from numpy.typing import NDArray
from scipy import optimize, stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lm10_series import u28

Vec = NDArray[np.float64]
PROC = HERE / "processed"
EPS = 1e-12
Z = 1.96
LIMIT_SWITCH = "2015-06-01"
SEED_ROOT = 20261011

# ---------------------------------------------------------------- TR23
_df = pl.read_parquet(PROC / "vol3_taiex.parquet").sort("date")
DATES_ALL: list[str] = [str(d) for d in _df["date"].to_list()]
TR: Vec = np.asarray(_df["tr"].to_numpy(), dtype=np.float64)
R: Vec = np.asarray(_df["R"].to_numpy()[1:], dtype=np.float64)
DATES: list[str] = DATES_ALL[1:]
assert _df["R"][0] is None and len(set(DATES_ALL)) == len(DATES_ALL)
assert np.allclose(R, TR[1:] / TR[:-1] - 1, rtol=0, atol=1e-15)
T = len(R)
r: Vec = np.log1p(R)
DAYS = (_df["date"][-1] - _df["date"][0]).days
TAU = DAYS / 365.25
A = T / TAU
assert (len(TR), T, DATES_ALL[0], DATES[0], DATES_ALL[-1]) == (5850, 5849, "2003-01-02", "2003-01-03", "2026-10-08")


def moments(x: Vec) -> tuple[float, float, float, float]:
    """Mean, s (divisor n), third and fourth central moments (divisor n)."""
    xc = x - x.mean()
    return float(x.mean()), float(x.std(ddof=0)), float((xc**3).mean()), float((xc**4).mean())


RB, S, M3, M4 = moments(R)
SU = float(R.std(ddof=1))
SKEW, KURT = M3 / S**3, M4 / S**4
RBAR_LOG, S_R, _, _ = moments(r)
TRF = [Fraction(str(x)) for x in TR]
RF = [TRF[i] / TRF[i - 1] - 1 for i in range(1, len(TRF))]
PRE = np.array([d < LIMIT_SWITCH for d in DATES])   # the 7% limit regime, returns to 2015-05-29


def count_le(x0: str) -> int:
    """Days with R <= -x0, guarded, checked exactly against the two-decimal closes."""
    g = int((R <= -float(x0) + EPS).sum())
    assert g == sum(1 for q in RF if q <= -Fraction(x0)), x0
    return g


# calendar years 2003-2025, 2003 from its first close
_year_end: dict[str, int] = {}
for _i, _d in enumerate(DATES_ALL):
    _year_end[_d[:4]] = _i
ANN_LOG_L, ANN_SIMPLE_L = [], []
for _y in range(2003, 2026):
    _b = 0 if _y == 2003 else _year_end[str(_y - 1)]
    ANN_LOG_L.append(log(TR[_year_end[str(_y)]] / TR[_b]))
    ANN_SIMPLE_L.append(float(TRF[_year_end[str(_y)]] / TRF[_b] - 1))
ANN_LOG: Vec = np.array(ANN_LOG_L)
N_YEARS = len(ANN_LOG)
S_ANN = float(ANN_LOG.std(ddof=0))
SU_ANN = float(ANN_LOG.std(ddof=1))
IN_2025 = np.array([d <= "2025-12-31" for d in DATES])
R_W = r[IN_2025]                       # the 5,664 daily log returns of 2003-2025 (LM17's refit)
_, S_RW, _, M4_RW = moments(R_W)
KURT_RW = M4_RW / S_RW**4

# ---------------------------------------------------------------- U28 pair and LM4's 0050 sample
_smp = u28()
U28_T = _smp.X.shape[0]
U28_A = _smp.A
U28_DATES = (_smp.dates[0], _smp.dates[-1])
X1: Vec = _smp.X[:, _smp.names.index("Semiconductor")]
X2: Vec = _smp.X[:, _smp.names.index("FinancialInsurance")]
_etf = pl.read_parquet(PROC / "etf_daily_returns.parquet").sort("date")
R50: Vec = np.asarray(_etf["R_0050"].to_numpy(), dtype=np.float64)
assert int(_etf["R_0050"].null_count()) == 0
T50 = len(R50)
DATES50_ALL: list[str] = [str(d) for d in _etf["date"].to_list()]
DATES50 = (DATES50_ALL[0], DATES50_ALL[-1])
MU50, S50, M3_50, M4_50 = moments(R50)


# ---------------------------------------------------------------- delta-method standard errors (iid returns)
def se_kelly(m: float, s: float, m3: float, m4: float, n: int) -> float:
    """(20.9): SE of mean/s^2 from Var R-bar ~ s^2/n, Var s^2 ~ (m4 - s^4)/n, Cov ~ m3/n."""
    return sqrt((1 / s**2 - 2 * m * m3 / s**6 + m**2 * (m4 - s**4) / s**8) / n)


def se_sharpe(m: float, s: float, m3: float, m4: float, n: int) -> float:
    """(20.9): SE of mean/s."""
    sr = m / s
    return sqrt((1 - sr * m3 / s**3 + sr**2 * (m4 / s**4 - 1) / 4) / n)


# ---------------------------------------------------------------- Student-t maximum likelihood (percent)
X100: Vec = 100 * R


def nll(p: Vec, x: Vec = X100) -> float:
    """Negative Student-t log-likelihood of x (percent) at (nu, location, scale)."""
    if p[0] <= 0.5 or p[2] <= 0:
        return 1e18
    return float(-stats.t.logpdf(x, p[0], p[1], p[2]).sum())


def hessian(fun: Callable[[Vec], float], p: Vec, h: Vec) -> Vec:
    """Central-difference Hessian of fun at p with steps h."""
    k = len(p)
    H = np.zeros((k, k))
    for i in range(k):
        for j in range(k):
            ei, ej = np.zeros(k), np.zeros(k)
            ei[i], ej[j] = h[i], h[j]
            H[i, j] = (fun(p + ei + ej) - fun(p + ei - ej) - fun(p - ei + ej) + fun(p - ei - ej)) / (4 * h[i] * h[j])
    return H


STEPS = np.array([1e-4, 1e-5, 1e-5])


def tfit(x: Vec) -> tuple[Vec, Vec, float, Vec]:
    """(refined parameters, covariance from the observed information, maximal log-likelihood, t.fit's answer)."""
    raw = np.array([float(q) for q in stats.t.fit(x / 100)]) * np.array([1.0, 100.0, 100.0])
    res = optimize.minimize(lambda p: nll(p, x), raw, method="Nelder-Mead",
                            options={"xatol": 1e-12, "fatol": 1e-12, "maxiter": 40000, "maxfev": 80000})
    p = np.asarray(res.x, dtype=np.float64)
    assert res.fun <= nll(raw, x) + 1e-9
    covs = []
    for scale in (1.0, 10.0):
        H = hessian(lambda q: nll(q, x), p, scale * STEPS)
        covs.append(np.linalg.inv(H))
    se0, se1 = np.sqrt(np.diag(covs[0])), np.sqrt(np.diag(covs[1]))
    assert np.all(np.abs(se0 / se1 - 1) < 1e-4), (se0, se1)
    return p, covs[0], -float(res.fun), raw


P_T, COV_T, LL_T, RAW_T = tfit(X100)
SE_T: Vec = np.sqrt(np.diag(COV_T))
NU, LOC, SCALE = (float(q) for q in P_T)
LL_N = float(stats.norm.logpdf(X100, X100.mean(), X100.std(ddof=0)).sum())


def profile(nu: float) -> float:
    """Profile log-likelihood of nu (location and scale re-maximized) minus the maximum."""
    res = optimize.minimize(lambda q: nll(np.array([nu, q[0], q[1]])), np.array([LOC, SCALE]),
                            method="Nelder-Mead", options={"xatol": 1e-11, "fatol": 1e-11, "maxiter": 20000})
    return -float(res.fun) - LL_T


# ---------------------------------------------------------------- Hill
def hill(x0: str) -> tuple[int, float, float]:
    """(k, alpha-hat, SE) at the loss level x0 (a decimal string, e.g. "0.03"): (20.10)."""
    k = count_le(x0)
    xs = -R[R <= -float(x0) + EPS]
    a = k / float(np.log(xs / float(x0)).sum())
    return k, a, a / sqrt(k)


def hill_fast(x0: float) -> tuple[int, float, float]:
    """(20.10) at a float threshold, guarded, for the chart's grid (no Fraction check)."""
    xs = -R[R <= -x0 + EPS]
    k = len(xs)
    a = k / float(np.log(xs / x0).sum())
    return k, a, a / sqrt(k)


# ---------------------------------------------------------------- experiments 1 and 4: one-year samples
N_SIM, T1, N_BATCH = 10_000, 246, 20
T_SCALE = sqrt((NU - 2) / NU)


def experiment1() -> dict[str, Vec]:
    """10,000 one-year samples of 246 days: the normal block, then the Student-t block with the fitted nu,
    both with TR23's mean and s by (15.11)."""
    rng = np.random.default_rng([1, SEED_ROOT])
    sims = {"normal": RB + S * rng.standard_normal((N_SIM, T1))}
    sims["t"] = RB + S * T_SCALE * rng.standard_t(NU, size=(N_SIM, T1))
    return sims


def experiment4(n_runs: int = 20) -> tuple[Vec, Vec]:
    """20 further runs of experiment 1's t block: per run the sd (divisor 10,000) of A x mean and of sqrt(A) x s."""
    rng = np.random.default_rng([4, SEED_ROOT])
    am, av = [], []
    for _ in range(n_runs):
        xs = RB + S * T_SCALE * rng.standard_t(NU, size=(N_SIM, T1))
        am.append(float((A * xs.mean(axis=1)).std(ddof=0)))
        av.append(float((sqrt(A) * xs.std(axis=1, ddof=0)).std(ddof=0)))
    return np.array(am), np.array(av)


def qinv(x: Vec, u: float) -> float:
    """F-hat^{-1}(u), LM14's quantile function."""
    return float(np.quantile(x, u, method="inverted_cdf"))


def batch_se(x: Vec, u: float) -> float:
    """LM18's batch standard error of a quantile: 20 equal batches in draw order, sd (divisor 20) / sqrt(20)."""
    qb = np.array([qinv(b, u) for b in x.reshape(N_BATCH, -1)])
    return float(qb.std(ddof=0)) / sqrt(N_BATCH)


# ---------------------------------------------------------------- Merton's sums
MERTON_M = (1, 2, 5, 10, 21, 62, 123, 246)


def merton(m: int) -> tuple[int, float, float, float]:
    """Non-overlapping m-day sums of r from the first return: (count, SE of the annual mean, SE of the annual
    volatility by the delta method with the sums' kurtosis, the normal iid model's volatility SE), in decimals."""
    nm = T // m
    sums = r[: nm * m].reshape(nm, m).sum(axis=1)
    _, s_m, _, m4_m = moments(sums)
    se_mean = A / m * s_m / sqrt(nm)
    se_vol = sqrt(A / m) * s_m * sqrt((m4_m / s_m**4 - 1) / (4 * nm))
    model_vol = sqrt(A) * S_R / sqrt(2 * nm)
    return nm, se_mean, se_vol, model_vol
