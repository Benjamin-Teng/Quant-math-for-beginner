"""Shared helpers of LM21 (Hypothesis Testing and Multiple Testing): TR23, the tests and the three experiments.

Imported by data/lm21_numbers.py and data/lm21_charts.py; it writes nothing. Run either of them, not this file:
    uv run python data/lm21_numbers.py

Input: data/processed/vol3_taiex.parquet (TR23: the TAIEX total-return index from FinMind's
TaiwanStockTotalReturnIndex, closes 2003-01-02 .. 2026-10-08; columns date, tr, price, R, Rp), written and checked by
data/vol3_series.py, which must run first.

Conventions (src/lm21.md and plans/vol-4.md, the LM21 brief): T = 5,849 simple daily returns R_t from 2003-01-03, no
log returns; s divides by T, s_u by T - 1 (ddof passed explicitly); the t-stat of a mean is (21.1), the two-sample
statistic (21.3) uses unpooled divisor-(n - 1) variances; p-values are two-sided against the standard normal. The
calendar family is the 12 months and the 5 weekdays of each return's date, each against all other returns (the 23
Saturday sessions belong to every "rest"). Each simulated experiment creates its generator once, at its start, as
np.random.default_rng([e, 20261011]) with e its number: 8 (shuffled dates), 10 (random rules), 11 (Problem 11).
"""
import datetime as dt
from dataclasses import dataclass
from fractions import Fraction
from math import sqrt
from pathlib import Path

import numpy as np
import polars as pl
from numpy.typing import NDArray
from scipy import stats

Vec = NDArray[np.float64]

HERE = Path(__file__).resolve().parent
PARQUET = HERE / "processed" / "vol3_taiex.parquet"
SEED = 20261011
EPS = 1e-12
LIMIT_SWITCH = dt.date(2015, 6, 1)
WD_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MO_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
C975 = float(stats.norm.isf(0.025))
C80 = float(stats.norm.ppf(0.8))
C95 = float(stats.norm.isf(0.05))


@dataclass
class TR23:
    dates_all: list[dt.date]   # the 5,850 close dates
    dates: list[dt.date]       # the 5,849 return dates
    tr: Vec                    # closes
    R: Vec                     # simple returns
    RF: list[Fraction]         # the same returns, exact, from the two-decimal closes
    T: int
    days: int                  # calendar days from the first to the last close
    years: float               # days / 365.25
    years_f: Fraction
    A: float                   # T / years
    pre: NDArray[np.bool_]     # return dated before 2015-06-01
    wd: NDArray[np.int64]      # weekday, Monday 0
    mo: NDArray[np.int64]      # month 1..12


def load() -> TR23:
    assert PARQUET.exists(), "run data/vol3_series.py first"
    df = pl.read_parquet(PARQUET).sort("date")
    dates_all: list[dt.date] = list(df["date"].to_list())
    assert df["R"][0] is None and len(set(dates_all)) == len(dates_all)
    tr = df["tr"].to_numpy().astype(np.float64)
    R = df["R"].to_numpy()[1:].astype(np.float64)
    assert np.allclose(R, tr[1:] / tr[:-1] - 1, rtol=0, atol=1e-15)
    trf = [Fraction(str(x)) for x in df["tr"].to_list()]
    RF = [trf[i] / trf[i - 1] - 1 for i in range(1, len(trf))]
    dates = dates_all[1:]
    days = (dates_all[-1] - dates_all[0]).days
    T = len(R)
    return TR23(dates_all=dates_all, dates=dates, tr=tr, R=R, RF=RF, T=T, days=days, years=days / 365.25,
                years_f=Fraction(4 * days, 1461), A=T / (days / 365.25),
                pre=np.array([d < LIMIT_SWITCH for d in dates]), wd=np.array([d.weekday() for d in dates]),
                mo=np.array([d.month for d in dates]))


def rng(e: int) -> np.random.Generator:
    """The generator of experiment e: the experiment number first, then the root seed (AUTHORING section 8)."""
    return np.random.default_rng([e, SEED])


def p2(z: float) -> float:
    """Two-sided normal p-value, (21.2)."""
    return float(2 * stats.norm.sf(abs(z)))


def tstat(x: Vec) -> float:
    """(21.1) with mu_null = 0 and s_u (divisor T - 1)."""
    return float(x.mean()) / (float(x.std(ddof=1)) / sqrt(len(x)))


def two_sample(a: Vec, b: Vec) -> tuple[float, float]:
    """The two-sample statistic (21.3) with unpooled divisor-(n - 1) variances, and its standard error."""
    se = sqrt(float(a.var(ddof=1)) / len(a) + float(b.var(ddof=1)) / len(b))
    return (float(a.mean()) - float(b.mean())) / se, se


def holm_count(p: list[Fraction] | list[float], a: float | Fraction) -> int:
    """(21.7): the number of leading ranks with p_(i) <= a / (m - i + 1)."""
    ps, m, k = sorted(p), len(p), 0
    for i, pi in enumerate(ps):
        if pi <= a / (m - i):
            k += 1
        else:
            break
    return k


def bh_count(p: list[Fraction] | list[float], q: float | Fraction) -> int:
    """(21.8): the largest rank i with p_(i) <= i q / m, or 0."""
    ps, m = sorted(p), len(p)
    ok = [i + 1 for i, pi in enumerate(ps) if pi <= (i + 1) * q / m]
    return max(ok) if ok else 0


def bonf_count(p: list[Fraction] | list[float], a: float | Fraction) -> int:
    """(21.6): every test at level a / m."""
    return sum(1 for pi in p if pi <= a / len(p))


def calendar(d: TR23) -> list[tuple[str, int, float, float, float]]:
    """The 17 tests: (name, days, mean in %, (21.3) against all other returns, two-sided normal p)."""
    fam = []
    for name, sel in ([(MO_NAMES[k - 1], d.mo == k) for k in range(1, 13)]
                      + [(WD_NAMES[k], d.wd == k) for k in range(5)]):
        a, b = d.R[sel], d.R[~sel]
        z, _ = two_sample(a, b)
        fam.append((name, len(a), 100 * float(a.mean()), z, p2(z)))
    return fam


def experiment8(d: TR23, B: int = 10_000) -> Vec:
    """Shuffled dates: B series R[perm] on TR23's dates in their order; the largest |(21.3)| of the 17 tests of each."""
    g8 = rng(8)
    T, R = d.T, d.R
    grp_m, grp_w = d.mo - 1, d.wd
    n_m = np.bincount(grp_m, minlength=12).astype(float)
    n_w = np.bincount(grp_w, minlength=7)[:5].astype(float)
    S_all, Q_all = float(R.sum()), float((R * R).sum())
    zmax = np.empty(B)
    for b_ in range(B):
        x = R[g8.permutation(T)]
        zs = []
        for grp, cnt, K in ((grp_m, n_m, 12), (grp_w, n_w, 5)):
            s1 = np.bincount(grp, weights=x, minlength=12)[:K]
            q1 = np.bincount(grp, weights=x * x, minlength=12)[:K]
            c2 = T - cnt
            m1, m2 = s1 / cnt, (S_all - s1) / c2
            v1 = (q1 - cnt * m1**2) / (cnt - 1)
            v2 = (Q_all - q1 - c2 * m2**2) / (c2 - 1)
            zs.append((m1 - m2) / np.sqrt(v1 / cnt + v2 / c2))
        zmax[b_] = float(np.abs(np.concatenate(zs)).max())
    return zmax


def experiment10(d: TR23, M: int = 10_000) -> Vec:
    """M random long-short rules: positions 2x - 1 from one call integers(0, 2, (M, T), int8); the t-stat (21.1) of
    each rule's daily returns f_{i,t} R_t, processed in chunks of 500 rules."""
    g10 = rng(10)
    pos = g10.integers(0, 2, size=(M, d.T), dtype=np.int8)
    tt = np.empty(M)
    for c in range(0, M, 500):
        xr = (2.0 * pos[c:c + 500].astype(np.float64) - 1.0) * d.R
        tt[c:c + 500] = xr.mean(axis=1) / (xr.std(axis=1, ddof=1) / sqrt(d.T))
    return tt


def maxq(u: float, m: int) -> float:
    """The u quantile of the largest of m independent standard normals, (21.9): Phi^-1(u^(1/m))."""
    return float(stats.norm.ppf(u ** (1 / m)))


def power(sr: float, yrs: float, c: float = C975) -> float:
    """(21.4): power of the two-sided test of a zero mean at annual Sharpe ratio sr over yrs years."""
    dd = sr * sqrt(yrs)
    return float(stats.norm.cdf(dd - c) + stats.norm.cdf(-dd - c))


def years80(sr: float) -> float:
    """(21.4): years of data for 80% power at the two-sided 5% level."""
    return ((C975 + C80) / sr) ** 2
