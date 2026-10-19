"""Shared data and statistics for LM19's scripts (data/lm19_numbers.py and data/lm19_charts.py import it).

Not a pipeline step of its own. It reads only data/processed/vol3_taiex.parquet (TR23, the TAIEX total-return index
from FinMind's TaiwanStockTotalReturnIndex, built and checked by data/vol3_series.py, which must run first).

Conventions (plans/vol-4.md, the LM19 brief, and plans/vol-4-anchors.md, "Common definitions"):
- Samples: TR23, the 5,849 returns 2003-01-03 -> 2026-10-08; "2003-2025", its 5,664 log returns dated up to
  2025-12-31 (the calendar years of LM15 and LM17, 2003 from its first close); the limit regimes, returns dated
  before 2015-06-01 (3,077) and from it (2,772). The 23 Saturday sessions stay in every sample.
- Return type: one-day statistics on simple returns R; sums, autocorrelations and variance ratios on log returns
  r = ln(1 + R) (and |r|, r^2).
- Divisors: means, s, central moments, autocovariances and the standard deviation of period sums divide by the number
  of terms (ddof=0, passed explicitly); s_u by T - 1 (ddof=1); the adjusted skewness and excess kurtosis are SciPy's
  bias=False values, written here in closed form.
- Quantiles: every quantile and median is F^-1(u) = x_(ceil(un)) (np.quantile, method="inverted_cdf").
- rho_k: full-sample mean, divisor T in numerator and denominator (statsmodels' acf). VR(m), (19.8): every window sum
  of m log returns centred at m rbar, divided by the T - m + 1 windows, over m s_r^2; VR_n(m): the floor((T - o)/m)
  consecutive blocks after o skipped returns, centred at m rbar of the whole sample, divisor the number of blocks.
"""
import datetime as dt
from fractions import Fraction
from math import floor, log, sqrt
from pathlib import Path

import numpy as np
import polars as pl
from numpy.typing import NDArray
from scipy import stats

Vec = NDArray[np.float64]

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PARQUET = HERE / "processed" / "vol3_taiex.parquet"
EPS = 1e-12                    # the guard for counts against a threshold (PITFALLS section 5)
SEED = 20261011
LIMIT_SWITCH = "2015-06-01"    # TWSE's daily limit widened from 7% to 10% on this date
Z75 = float(stats.norm.ppf(0.75))
YEAR = 246                     # a year of 2003-2025 in sessions (LM17's m)
M_MAX = 1231                   # five years, LM18's m = round(5A)


def qf(x: Vec, u: float) -> float:
    """The book's quantile function F^-1(u) = x_(ceil(un)) (LM14)."""
    return float(np.quantile(x, u, method="inverted_cdf"))


def mad(x: Vec) -> float:
    """Median absolute deviation: the median of |x - med|, both medians by F^-1(1/2)."""
    return qf(np.abs(x - qf(x, 0.5)), 0.5)


def trim(x: Vec, j0: int) -> float:
    """Mean after dropping the j0 smallest and the j0 largest values."""
    return float(np.sort(x)[j0 : len(x) - j0].mean())


def trim5(x: Vec) -> float:
    return trim(x, floor(0.05 * len(x)))


def qskew(x: Vec) -> float:
    """Quartile skewness, (19.4)."""
    q1, q2, q3 = qf(x, 0.25), qf(x, 0.5), qf(x, 0.75)
    return (q3 + q1 - 2 * q2) / (q3 - q1)


def okurt(x: Vec) -> float:
    """Octile kurtosis, (19.4), from E_j = F^-1(j/8)."""
    e = [qf(x, i / 8) for i in range(1, 8)]
    return ((e[6] - e[4]) + (e[2] - e[0])) / (e[5] - e[1])


def okurt_normal() -> float:
    z = [float(stats.norm.ppf(i / 8)) for i in range(1, 8)]
    return ((z[6] - z[4]) + (z[2] - z[0])) / (z[5] - z[1])


def skew(x: Vec) -> float:
    """Sample skewness, (19.3): divisor-T central moments (scipy.stats.skew with bias=True, its default)."""
    return float(stats.skew(x, bias=True))


def exkurt(x: Vec) -> float:
    """Sample excess kurtosis, (19.3) minus 3: divisor-T moments (scipy.stats.kurtosis, fisher=True, bias=True)."""
    return float(stats.kurtosis(x, fisher=True, bias=True))


def skew_closed(x: Vec) -> float:
    """(19.3) written out, to check SciPy's value."""
    xc = x - x.mean()
    return float((xc**3).mean() / (xc**2).mean() ** 1.5)


def exkurt_closed(x: Vec) -> float:
    xc = x - x.mean()
    return float((xc**4).mean() / (xc**2).mean() ** 2 - 3)


def skew_adj(x: Vec) -> float:
    """Adjusted skewness, sqrt(T(T-1))/(T-2) times the sample skewness (SciPy's bias=False)."""
    n = len(x)
    return sqrt(n * (n - 1)) / (n - 2) * skew(x)


def exk_adj(x: Vec) -> float:
    """Adjusted excess kurtosis, (T-1)/((T-2)(T-3)) ((T+1) g2 + 6) (SciPy's bias=False)."""
    n = len(x)
    return (n - 1) / ((n - 2) * (n - 3)) * ((n + 1) * exkurt(x) + 6)


PCT = ("mean", "median", "trim5", "s", "s_u", "meanAD", "1.4826MAD", "IQR/1.349")


def summary(x: Vec) -> dict[str, float]:
    """Every statistic of the summary exhibit (X2), in its row order."""
    return {
        "mean": float(x.mean()), "median": qf(x, 0.5), "trim5": trim5(x), "s": float(x.std(ddof=0)),
        "s_u": float(x.std(ddof=1)), "meanAD": float(np.abs(x - x.mean()).mean()), "1.4826MAD": mad(x) / Z75,
        "IQR/1.349": (qf(x, 0.75) - qf(x, 0.25)) / (2 * Z75), "skew": skew(x), "skew_adj": skew_adj(x),
        "qskew": qskew(x), "exkurt": exkurt(x), "exkurt_adj": exk_adj(x), "okurt": okurt(x),
    }


def acf(x: Vec, kmax: int) -> Vec:
    """rho_1 .. rho_kmax, (19.5): full-sample mean, divisor T in numerator and denominator."""
    xc = x - x.mean()
    g0 = float((xc * xc).sum())
    return np.array([float((xc[k:] * xc[:-k]).sum()) / g0 for k in range(1, kmax + 1)])


def sums(x: Vec, m: int) -> Vec:
    """All len(x) - m + 1 overlapping m-day sums."""
    c = np.concatenate([[0.0], np.cumsum(x)])
    return c[m:] - c[:-m]


def vr_o(x: Vec, m: int) -> float:
    """VR(m), the overlapping estimator (19.8), centred at m xbar."""
    s_m = sums(x, m)
    return float(((s_m - m * x.mean()) ** 2).mean() / (m * x.var(ddof=0)))


def vr_all(x: Vec, m_max: int) -> Vec:
    """VR(m) for m = 1 .. m_max in one pass over the cumulative sums."""
    c = np.concatenate([[0.0], np.cumsum(x)])
    mu, v = float(x.mean()), float(x.var(ddof=0))
    return np.array([float(((c[m:] - c[:-m] - m * mu) ** 2).mean() / (m * v)) for m in range(1, m_max + 1)])


def blocks(x: Vec, m: int, off: int) -> Vec:
    """Sums of the floor((len(x) - off)/m) consecutive m-day blocks after skipping the first off returns."""
    y = x[off:]
    nb = len(y) // m
    return y[: nb * m].reshape(nb, m).sum(axis=1)


def vr_n(x: Vec, m: int, off: int = 0) -> float:
    """VR_n(m), the non-overlapping estimator (19.8), centred at m xbar of the whole sample."""
    b = blocks(x, m, off)
    return float(((b - m * x.mean()) ** 2).mean() / (m * x.var(ddof=0)))


def vr_plug(rho: Vec, m: int) -> float:
    """(19.7) evaluated with sample autocorrelations: the identity column."""
    k = np.arange(1, m)
    return float(1 + 2 * ((1 - k / m) * rho[: m - 1]).sum())


def iid_factor(n: int, m: int) -> float:
    """(1 - m/T)/(1 - 1/T), the iid factor of (19.8)."""
    return (1 - m / n) / (1 - 1 / n)


class TR23:
    """TR23 and its named sub-samples."""

    def __init__(self) -> None:
        assert PARQUET.exists(), "run data/vol3_series.py first"
        df = pl.read_parquet(PARQUET).sort("date")
        self.dates_all = [str(d) for d in df["date"].to_list()]
        assert df["R"][0] is None and len(set(self.dates_all)) == len(self.dates_all)
        self.tr = df["tr"].to_numpy().astype(np.float64)
        self.R = df["R"].to_numpy()[1:].astype(np.float64)
        assert np.allclose(self.R, self.tr[1:] / self.tr[:-1] - 1, rtol=0, atol=1e-15)
        self.dates = self.dates_all[1:]
        self.T = len(self.R)
        self.r = np.log1p(self.R)
        self.days = (df["date"][-1] - df["date"][0]).days
        self.years = self.days / 365.25
        self.A = self.T / self.years
        trf = [Fraction(str(x)) for x in df["tr"].to_list()]
        self.RF = [trf[i] / trf[i - 1] - 1 for i in range(1, len(trf))]
        assert all(abs(float(a) - b) < 1e-15 for a, b in zip(self.RF, self.R))
        self.dates_np = np.array(self.dates)
        self.in25 = self.dates_np <= "2025-12-31"
        self.r25 = self.r[self.in25]
        self.T25 = len(self.r25)
        self.pre = self.dates_np < LIMIT_SWITCH
        year_end: dict[str, int] = {}
        for i, d in enumerate(self.dates_all):
            year_end[d[:4]] = i
        start = {y: 0 if y == 2003 else year_end[str(y - 1)] for y in range(2003, 2026)}
        self.ann = np.array([log(self.tr[year_end[str(y)]] / self.tr[start[y]]) for y in range(2003, 2026)])
        self.per_year = [year_end[str(y)] - start[y] for y in range(2003, 2026)]
        d25 = [dt.date.fromisoformat(d) for d in self.dates_np[self.in25]]
        self.d25 = d25
        self.wk_key = [x.isocalendar()[:2] for x in d25]
        self.mo_key = [(x.year, x.month) for x in d25]


def period_sums(keys: list[tuple[int, int]], x: Vec) -> tuple[Vec, list[int]]:
    """Sums of x over consecutive runs of equal keys (ISO weeks or calendar months), in date order."""
    order: dict[tuple[int, int], list[int]] = {}
    for i, k in enumerate(keys):
        order.setdefault(k, []).append(i)
    vals = np.array([x[v].sum() for v in order.values()])
    return vals, [len(v) for v in order.values()]
