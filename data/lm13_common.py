"""TR23 for LM13 (Probability Foundations and Bayes): loading, exact returns and guarded threshold counts.

Imported by data/lm13_numbers.py and data/lm13_charts.py; not run on its own.

Sample: TR23, the TAIEX total-return index, from data/processed/vol3_taiex.parquet (built and checked by
data/vol3_series.py): 5,850 closes 2003-01-02 .. 2026-10-08 and T = 5,849 simple daily returns R from 2003-01-03.
Every count against a threshold uses one guard (R <= c + 1e-12, R >= c - 1e-12; project/PITFALLS.md section 5) and is
asserted equal to an exact count with fractions.Fraction from the two-decimal closes.
"""
from dataclasses import dataclass
from fractions import Fraction
from itertools import pairwise
from pathlib import Path

import numpy as np
import polars as pl
from numpy.typing import NDArray

Bools = NDArray[np.bool_]
Floats = NDArray[np.float64]
EPS = 1e-12
HERE = Path(__file__).resolve().parent
PARQUET = HERE / "processed" / "vol3_taiex.parquet"
REG_END_7, REG_START_10 = "2015-05-29", "2015-06-01"   # the daily price limit: 7% to 29 May 2015, 10% from 1 June


@dataclass(frozen=True)
class TR23:
    dates: list[str]            # return dates, 2003-01-03 .. 2026-10-08
    R: Floats                   # simple returns of the total-return index
    Rp: Floats                  # simple returns of the price index (dividends not reinvested)
    closes: list[Fraction]      # the 5,850 two-decimal closes, exact
    RF: list[Fraction]          # the returns, exact

    @property
    def T(self) -> int:
        return len(self.R)


def load() -> TR23:
    assert PARQUET.exists(), "run data/vol3_series.py first"
    df = pl.read_parquet(PARQUET).sort("date")
    assert df["R"][0] is None and df["R"].null_count() == 1
    closes = [Fraction(f"{x:.2f}") for x in df["tr"].to_list()]
    assert all(float(c) == x for c, x in zip(closes, df["tr"].to_list(), strict=True)), "a close has more than two decimals"
    RF = [b / a - 1 for a, b in pairwise(closes)]
    R = np.asarray(df["R"].to_numpy()[1:], dtype=np.float64)
    assert np.allclose(R, [float(r) for r in RF], rtol=0, atol=1e-15)
    dates = [d.isoformat() for d in df["date"].to_list()][1:]
    return TR23(dates, R, np.asarray(df["Rp"].to_numpy()[1:], dtype=np.float64), closes, RF)


def le(x: Floats, c: float) -> Bools:
    """x <= c with the guard."""
    return x <= c + EPS


def ge(x: Floats, c: float) -> Bools:
    """x >= c with the guard."""
    return x >= c - EPS


def at_most(tr: TR23, pc: Fraction | int) -> Bools:
    """R <= pc % (guarded), asserted equal to the exact count."""
    c = Fraction(pc) / 100
    m = le(tr.R, float(c))
    assert (m == np.array([r <= c for r in tr.RF])).all(), ("guard and exact count differ at", pc)
    return m


def at_least(tr: TR23, pc: Fraction | int) -> Bools:
    """R >= pc % (guarded), asserted equal to the exact count."""
    c = Fraction(pc) / 100
    m = ge(tr.R, float(c))
    assert (m == np.array([r >= c for r in tr.RF])).all(), ("guard and exact count differ at", pc)
    return m


def bucket(x: Floats, lo: float | None, hi: float | None) -> Bools:
    """x in (lo, hi] with the guard at both ends; None is an open end."""
    m = np.ones(len(x), dtype=bool)
    if lo is not None:
        m &= ~le(x, lo)
    if hi is not None:
        m &= le(x, hi)
    return m


BUCKETS: list[tuple[int | None, int | None]] = [(None, -3), (-3, -2), (-2, -1), (-1, 0), (0, 1), (1, 2), (2, 3),
                                                  (3, None)]
BUCKET_NAMES = ["−3 or below", "−3 to −2", "−2 to −1", "−1 to 0", "0 to 1", "1 to 2", "2 to 3", "above 3"]
BINS: list[tuple[int | None, int | None]] = [(None, -5)] + [(k, k + 1) for k in range(-5, 5)] + [(5, None)]
BIN_NAMES = ["−5 or below"] + [f"{'−' if k < 0 else ''}{abs(k)} to {'−' if k + 1 < 0 else ''}{abs(k + 1)}"
                               for k in range(-5, 5)] + ["above 5"]


def regimes(tr: TR23) -> tuple[Bools, Bools]:
    d = np.array(tr.dates)
    r7, r10 = d <= REG_END_7, d >= REG_START_10
    assert (r7 ^ r10).all()
    return r7, r10
