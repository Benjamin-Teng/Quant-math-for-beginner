"""Shared inputs of LM10's scripts: the U28 sample and the ETFs' one-session total returns.

Imported by data/lm10_numbers.py and data/lm10_charts.py; it computes nothing when run on its own except a summary:
    uv run python data/lm10_series.py

U28 is every TWSE sector index of data/processed/vol2_closes.parquet (built and repaired by data/vol2_series.py) except
the aggregates Electronic and ChemicalBiotechnologyMedicalCare. The sample is the closes from 2008-12-01 to 2026-10-08,
simple price returns between consecutive rows (the TAIEX calendar), T = 4,382, divisor T.

An ETF's one-session total return on date t (plans/vol-2.md, "Labs") is (P_t + D_t) / (P_{t-1} / s_t) - 1, taken only
when the fund has a close on t and on the previous TAIEX-calendar date, so a return that spans a halt drops out. D_t is
the cash dividend of every row of the fund's dividends file and s_t the split ratio (4 for 0050 on 2025-06-18, 22 for
00631L on 2026-03-31, 1 otherwise; both split days follow a halt, so both returns drop out).
"""
from dataclasses import dataclass
from datetime import date
from itertools import pairwise
from pathlib import Path

import numpy as np
import polars as pl
from numpy.typing import NDArray

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
CLOSES = HERE / "processed" / "vol2_closes.parquet"
REPAIRS = HERE / "processed" / "vol2_repairs.json"
AGGREGATES = ("Electronic", "ChemicalBiotechnologyMedicalCare")
FIRST, LAST = "2008-12-01", "2026-10-08"
S3 = ["Semiconductor", "FinancialInsurance", "Food"]
S5 = [*S3, "Plastics", "ShippingTransportation"]
ETFS = ["0050", "00631L", "00679B"]
SPLITS = {"0050": ("2025-06-18", 4.0), "00631L": ("2026-03-31", 22.0)}

Mat = NDArray[np.float64]


@dataclass
class Sample:
    names: list[str]          # the 28 U28 sector ids, in the parquet's (alphabetical) order
    close_dates: list[str]    # 4,383 dates, 2008-12-01 .. 2026-10-08
    dates: list[str]          # 4,382 return dates, 2008-12-02 .. 2026-10-08
    X: Mat                    # T x 28 simple returns
    taiex: NDArray[np.float64]  # T returns of TAIEX on the same dates
    calendar: list[str]       # every TAIEX date of the parquet (for the ETFs' previous-date rule)
    years: float
    A: float


def u28() -> Sample:
    assert CLOSES.exists(), "run data/vol2_series.py first (it builds data/processed/vol2_closes.parquet)"
    cl = pl.read_parquet(CLOSES).sort("date")
    names = [c for c in cl.columns if c not in ("date", "TAIEX") and c not in AGGREGATES]
    assert len(names) == 28, len(names)
    smp = cl.filter(pl.col("date").is_between(pl.lit(FIRST), pl.lit(LAST)))
    assert smp.select(names + ["TAIEX"]).null_count().sum_horizontal()[0] == 0, "a U28 close is missing"
    p = np.asarray(smp.select(names).to_numpy(), dtype=np.float64)
    tx = np.asarray(smp["TAIEX"].to_numpy(), dtype=np.float64)
    cd = smp["date"].to_list()
    years = (date.fromisoformat(cd[-1]) - date.fromisoformat(cd[0])).days / 365.25
    x = p[1:] / p[:-1] - 1
    return Sample(names, cd, cd[1:], x, tx[1:] / tx[:-1] - 1, cl["date"].to_list(), years, x.shape[0] / years)


def cov0(x: Mat) -> Mat:
    """Sample covariance matrix with divisor T, columns = variables: (10.2)."""
    xc = x - x.mean(axis=0)
    return xc.T @ xc / x.shape[0]


def raw_closes(sym: str) -> dict[str, float]:
    files = sorted(RAW.glob(f"{sym}__*.csv"))
    assert files, f"no raw files for {sym}"
    df = pl.concat([pl.read_csv(f, schema_overrides={"close": pl.Float64, "spread": pl.Float64}) for f in files])
    df = df.unique(subset="date", keep="first").sort("date")
    assert df["date"].n_unique() == df.height
    return dict(zip(df["date"].to_list(), df["close"].to_list()))


def dividends(sym: str) -> dict[str, float]:
    f = RAW / f"{sym}_dividends.csv"
    if not f.exists():
        return {}
    dv = pl.read_csv(f)
    return dict(zip(dv["date"].to_list(), dv["cash_dividend"].to_list()))


def one_session(sym: str, calendar: list[str]) -> dict[str, float]:
    """The fund's one-session total returns, keyed by date, on the TAIEX calendar."""
    px, div = raw_closes(sym), dividends(sym)
    assert set(px) <= set(calendar), f"{sym} has closes off the TAIEX calendar"
    out: dict[str, float] = {}
    for d0, d1 in pairwise(calendar):
        if d1 in px and d0 in px:
            s = SPLITS[sym][1] if sym in SPLITS and d1 == SPLITS[sym][0] else 1.0
            out[d1] = (px[d1] + div.get(d1, 0.0)) / (px[d0] / s) - 1
    first = min(px)
    missed = [d for d in div if d > first and d not in out]
    assert not missed, f"{sym}: dividends on dates without a one-session return {missed}"
    return out


if __name__ == "__main__":
    s = u28()
    print(f"U28: T = {s.X.shape[0]}, first return {s.dates[0]}, last {s.dates[-1]}, years {s.years:.8f}, A {s.A:.7f}")
    for e in ETFS:
        r = one_session(e, s.calendar)
        print(f"{e}: {len(r)} one-session returns, {min(r)} .. {max(r)}")
