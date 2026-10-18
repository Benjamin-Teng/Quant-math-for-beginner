"""Shared inputs of LM14's scripts (data/lm14_numbers.py, data/lm14_charts.py): TR23 and the small laws.

Not run on its own. data/vol3_series.py builds data/processed/vol3_taiex.parquet (columns date, tr, price, R, Rp),
which this module reads: TR23 is the TAIEX total-return index, R its simple daily return tr_t / tr_{t-1} - 1, null
on the first row (2003-01-02), so T = 5,849 returns from 2003-01-03 to 2026-10-08. Conventions (plans/vol-3.md,
Shared decisions): the empirical law puts mass 1/T on each return, so moments divide by T; years = calendar days from
the first to the last close / 365.25 and A = T / years; calendar years 2003-2025 run from the last close of the
previous year, 2003 from its first close (2003-01-02); 2026 is partial and left out. Counts against a threshold use
the guard EPS (<= c + 1e-12, >= c - 1e-12).
"""
import datetime as dt
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import polars as pl
from numpy.typing import NDArray

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PARQUET = HERE / "processed" / "vol3_taiex.parquet"
EPS = 1e-12
LIMIT_CHANGE = dt.date(2015, 6, 1)      # daily price limit 7% before, 10% from this date

Vec = NDArray[np.float64]


@dataclass(frozen=True)
class TR23:
    dates: list[dt.date]                # the 5,850 close dates
    tr: Vec                             # total-return index closes
    R: Vec                              # the 5,849 simple daily returns
    rdates: list[dt.date]               # their dates (from 2003-01-03)
    years: float                        # calendar days / 365.25
    days: int                           # calendar days from the first to the last close
    year_ids: list[int]                 # 2003 .. 2025
    year_R: Vec                         # calendar-year returns, 2003 from its first close

    @property
    def T(self) -> int:
        return int(self.R.size)

    @property
    def A(self) -> float:
        return self.T / self.years


def load() -> TR23:
    assert PARQUET.exists(), "run data/vol3_series.py first (it builds data/processed/vol3_taiex.parquet)"
    df = pl.read_parquet(PARQUET).sort("date")
    dates = df["date"].to_list()
    tr = df["tr"].to_numpy().astype(np.float64)
    R = df["R"].to_numpy()[1:].astype(np.float64)
    assert df["R"][0] is None and not np.isnan(R).any()
    assert np.allclose(R, tr[1:] / tr[:-1] - 1, rtol=0, atol=1e-15)
    days = (dates[-1] - dates[0]).days
    ys: list[int] = []
    ry: list[float] = []
    prev = float(tr[0])
    last = (pl.DataFrame({"date": dates, "tr": tr}).with_columns(pl.col("date").dt.year().alias("y"))
            .group_by("y", maintain_order=True).agg(pl.col("tr").last()).sort("y"))
    for y, p in last.iter_rows():
        if y == 2026:
            continue
        ys.append(int(y))
        ry.append(float(p) / prev - 1)
        prev = float(p)
    return TR23(dates=dates, tr=tr, R=R, rdates=dates[1:], years=days / 365.25, days=days, year_ids=ys,
                year_R=np.array(ry))


def law(x: Vec, p: Vec) -> dict[str, float]:
    """Moments, drag and Jensen-gap terms of the law with values x (all > -1) and probabilities p.

    jensen = ln(1 + mu) - g; t2, t3, t4 = the terms of (14.13), E[y^j] (-1)^j / j with y = (x - mu) / (1 + mu).
    """
    mu = float((p * x).sum())
    var = float((p * (x - mu) ** 2).sum())
    sd = var**0.5
    g = float((p * np.log1p(x)).sum())
    y = (x - mu) / (1 + mu)
    t2, t3, t4 = (float((p * y**j).sum()) * (-1) ** j / j for j in (2, 3, 4))
    return {"mu": mu, "var": var, "sd": sd, "g": g, "RG": float(np.expm1(g)), "lnmu": float(np.log1p(mu)),
            "jensen": float(np.log1p(mu)) - g, "drag": mu - float(np.expm1(g)), "t2": t2, "t3": t3, "t4": t4,
            "skew": float((p * (x - mu) ** 3).sum()) / sd**3 if sd > 0 else 0.0,
            "kurt": float((p * (x - mu) ** 4).sum()) / sd**4 if sd > 0 else 0.0}


def two_point(b: float, a: float, p: float) -> dict[str, float]:
    """A return of +b with probability p and -a otherwise (the widget's law)."""
    return law(np.array([b, -a]), np.array([p, 1 - p]))


def year_points(d: TR23) -> list[tuple[int, float, float]]:
    """For each calendar year 2003-2025: (year, drag mean - compound rate, half the variance), both in bp."""
    ry = np.array([t.year for t in d.rdates])
    out = []
    for y in d.year_ids:
        x = d.R[ry == y]
        out.append((y, (float(x.mean()) - float(np.expm1(np.log1p(x).mean()))) * 1e4, float(x.var()) / 2 * 1e4))
    return out


# the widget's presets: (key, label, b, a, p)
PRESETS: list[tuple[str, str, float, float, float]] = [
    ("y0809", "TAIEX 2008 and 2009", 0.8334, 0.4307, 0.5),
    ("bet25", "+2%/−1% bet at 25× (LM4)", 0.50, 0.25, 0.5),
    ("hm", "+100%/−50% (LM3)", 1.00, 0.50, 0.5),
]
