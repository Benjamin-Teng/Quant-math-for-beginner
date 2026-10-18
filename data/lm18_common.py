"""Shared data and experiments for LM18's scripts (data/lm18_numbers.py and data/lm18_charts.py import it).

Not a pipeline step of its own. It reads only data/processed/vol3_taiex.parquet (TR23, the TAIEX total-return index,
built and checked by data/vol3_series.py, which must run first).

Conventions (plans/vol-3.md, "Shared decisions"): closes `tr` 2003-01-02 .. 2026-10-08, T = 5,849 simple returns
R_t = P_t / P_(t-1) - 1 from 2003-01-03, log returns r_t = ln(1 + R_t); moments divide by T; years = calendar days /
365.25, A = T / years; five years is m = round(5A) = 1,231 sessions. Quantiles are order statistics x_(ceil(un))
(np.quantile(..., method="inverted_cdf")).

Simulation (AUTHORING section 8): each simulated experiment creates its generator once, at its start, as
np.random.default_rng([e, 20261011]) with e the experiment's number in the module. Paths and resamples are drawn in
chunks of 500 rows (rows = paths); the chunks are also the batches of a batch standard error. Standard errors: of a
mean of n draws, their standard deviation (divisor n) over sqrt(n); of a standard deviation of n near-normal values,
s / sqrt(2n); of a quantile, a slope or a root-mean-square, the standard deviation (divisor 20) of its values on 20
equal batches, over sqrt(20).

LM12's printed S5 Cholesky factor (src/lm12.md, the exhibit "Cholesky factor of S5's covariance matrix", % a day) is
a model parameter here: no U28 data are loaded.
"""
import math
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from fractions import Fraction
from pathlib import Path

import numpy as np
import polars as pl
from numpy.typing import NDArray

Vec = NDArray[np.float64]

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PROC = HERE / "processed"
SEED = 20261011
EPS = 1e-12                   # the guard for counts against a threshold (PITFALLS section 5)
CH = 500                      # rows per chunk (paths or resamples); also the batch size
KK = 4.1074386                # LM5's -5% day for 0050 in standard deviations (lm05.md)
# LM12's printed S5 Cholesky factor, % a day (Semiconductor, FinancialInsurance, Food, Plastics, ShippingTransportation)
L_PRINTED = np.array([[1.5243, 0, 0, 0, 0], [0.6998, 0.9960, 0, 0, 0], [0.4336, 0.4779, 0.8594, 0, 0],
                      [0.7238, 0.5162, 0.1831, 1.3034, 0], [0.6415, 0.5995, 0.2050, 0.1109, 1.4358]]) / 100
X3_SIZES = (100, 500, 1000, 4382, 10_000, 50_000)
X3_RUNS = 200
X7_RESAMPLES = 1000


def rng(e: int) -> np.random.Generator:
    """The generator of experiment e: the experiment number first, then the root seed (AUTHORING section 8)."""
    return np.random.default_rng([e, SEED])


def se(y: Vec) -> float:
    """Standard error of a mean of draws: standard deviation with divisor n, over sqrt(n)."""
    return float(y.std() / math.sqrt(y.size))


def sd_se(y: Vec) -> float:
    """Standard error of a standard deviation of n near-normal values, s / sqrt(2n)."""
    return float(y.std() / math.sqrt(2 * y.size))


def bse(stat: Callable[..., float], *arrays: np.ndarray, batches: int = 20) -> float:
    """Batch standard error: the statistic on `batches` equal consecutive batches of the rows, standard deviation
    (divisor `batches`) over sqrt(batches)."""
    n = arrays[0].shape[0]
    assert n % batches == 0
    k = n // batches
    vals = np.array([stat(*(a[b * k:(b + 1) * k] for a in arrays)) for b in range(batches)])
    return float(vals.std() / math.sqrt(batches))


def q_inv(x: np.ndarray, u: list[float]) -> np.ndarray:
    """Order-statistic quantiles x_(ceil(un)) (LM14's rule)."""
    return np.quantile(x, u, method="inverted_cdf")


def lag1(x: np.ndarray) -> float:
    return float(np.corrcoef(x[1:], x[:-1])[0, 1])


@dataclass
class TR23:
    dd: list[date]            # the 5,850 close dates
    dates: list[str]          # the same, ISO strings
    P: Vec                    # closes
    Pq: list[Fraction]        # closes, exact (two decimals)
    R: Vec                    # T simple returns, dated dates[1:]
    r: Vec                    # T log returns
    T: int
    days: int
    years: float
    A: float
    m: int


def load() -> TR23:
    path = PROC / "vol3_taiex.parquet"
    assert path.exists(), "run data/vol3_series.py first"
    df = pl.read_parquet(path).sort("date")
    dd = list(df["date"])
    P = df["tr"].to_numpy().astype(np.float64)
    R = P[1:] / P[:-1] - 1
    assert np.allclose(R, df["R"].to_numpy()[1:], rtol=0, atol=1e-15)
    Pq = [Fraction(f"{x:.2f}") for x in P]
    assert all(abs(float(q) - x) < 1e-9 for q, x in zip(Pq, P, strict=True))
    days = (dd[-1] - dd[0]).days
    years = days / 365.25
    T = int(R.size)
    A = T / years
    return TR23(dd, [d.isoformat() for d in dd], P, Pq, R, np.log1p(R), T, days, years, A, round(5 * A))


def x3_runs(L: Vec) -> dict[int, Vec]:
    """Experiment 12: at each n of X3_SIZES, 200 runs of standard_normal((n, 5)) @ L.T; the relative Frobenius gap of
    np.cov(..., ddof=0) from Sigma = L L'. One generator for the whole experiment, sizes in this order."""
    sig = L @ L.T
    g = rng(12)
    out: dict[int, Vec] = {}
    for n in X3_SIZES:
        gs = np.empty(X3_RUNS)
        for i in range(X3_RUNS):
            x = g.standard_normal((n, 5)) @ L.T
            gs[i] = np.linalg.norm(np.cov(x, rowvar=False, ddof=0) - sig) / np.linalg.norm(sig)
        out[n] = gs
    return out


@dataclass
class X7:
    months: list[str]         # the 286 calendar months of the return dates
    counts: NDArray[np.int64]  # days with |R| >= 3% in each month (data)
    nmon: NDArray[np.int64]   # returns in each month
    pmf: Vec                  # (1000, 9): months by count 0..7 and 8 or more, per resample
    variances: Vec            # monthly variance (divisor 286) per resample
    lag1s: Vec                # lag-1 correlation of |r| per resample


def x7_resamples(d: TR23) -> X7:
    """Experiment 14: 1,000 resamples integers(0, T, size=T) placed on TR23's return dates."""
    big = (d.R >= 0.03 - EPS) | (d.R <= -0.03 + EPS)
    ym = [s[:7] for s in d.dates[1:]]
    months = sorted(set(ym))
    mi = np.searchsorted(months, ym)
    cnt = np.bincount(mi, weights=big.astype(float), minlength=len(months)).astype(np.int64)
    nmon = np.bincount(mi).astype(np.int64)
    g = rng(14)
    variances, lag1s, pmf = np.empty(X7_RESAMPLES), np.empty(X7_RESAMPLES), np.zeros((X7_RESAMPLES, 9))
    absr = np.abs(d.r)
    for b in range(X7_RESAMPLES):
        idx = g.integers(0, d.T, size=d.T)
        c = np.bincount(mi, weights=big[idx].astype(float), minlength=len(months)).astype(int)
        variances[b] = c.var()
        pmf[b] = np.bincount(np.minimum(c, 8), minlength=9)[:9]
        lag1s[b] = lag1(absr[idx])
    return X7(months, cnt, nmon, pmf, variances, lag1s)


SIMPSON_LM5 = {8: 9.69e-6, 16: 1.23e-6, 32: 9.47e-8, 64: 6.23e-9, 128: 3.94e-10, 256: 2.47e-11, 512: 1.55e-12,
               1024: 9.67e-14}   # LM5's printed Simpson errors by panels N (src/lm05.md, exhibit numinttable)
P_LM5 = 2.000355e-5              # LM5's printed exact value of Phi(-4.1074386)
