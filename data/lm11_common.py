"""Shared data and helpers for LM11's scripts (data/lm11_numbers.py and data/lm11_charts.py import it).

Not a pipeline step of its own. It reads only data/processed/ (vol2_closes.parquet, the repaired sector closes of
data/vol2_series.py; lm07_returns.parquet and etf_daily_returns.parquet, Volume I's ETF frames).

Conventions (plans/vol-2.md, "Universe and sample"): U28 = the 28 leaf TWSE sector indices (every sector series
except the aggregates Electronic and ChemicalBiotechnologyMedicalCare); closes 2008-12-01 .. 2026-10-08; daily simple
returns R_t = P_t / P_(t-1) - 1 between consecutive dates of the TAIEX calendar; sample covariance with divisor T;
A = T / years, years = calendar days / 365.25. Eigenvalues are sorted in descending order and every eigenvector is
signed so that its entry largest in absolute value is positive (on a tie, the first tied entry).
"""
from datetime import date
from pathlib import Path

import numpy as np
import polars as pl
from numpy.typing import NDArray

Vec = NDArray[np.float64]
Mat = NDArray[np.float64]

HERE = Path(__file__).resolve().parent
PROC = HERE / "processed"
START, END = "2008-12-01", "2026-10-08"
AGGREGATES = ("Electronic", "ChemicalBiotechnologyMedicalCare")
S3 = ["Semiconductor", "FinancialInsurance", "Food"]
S5 = [*S3, "Plastics", "ShippingTransportation"]
ELEC8 = ["Semiconductor", "ComputerPeripheralEquipment", "Optoelectronic", "CommunicationsInternet",
         "ElectronicPartsComponents", "ElectronicProductsDistribution", "InformationService", "OtherElectronic"]
TIE = 1e-12           # relative tolerance for a tie in absolute value (exact ties, e.g. (1, -1)/sqrt(2))


def closes() -> pl.DataFrame:
    """Repaired closes of TAIEX and the 30 sector indices on the sample dates (data/vol2_series.py)."""
    path = PROC / "vol2_closes.parquet"
    assert path.exists(), "run data/vol2_series.py first (it writes data/processed/vol2_closes.parquet)"
    df = pl.read_parquet(path).sort("date")
    return df.filter(pl.col("date").is_between(pl.lit(START), pl.lit(END)))


def sector_names(df: pl.DataFrame) -> tuple[list[str], list[str]]:
    """(all 30 sector ids, the 28 leaves of U28), in the column order of vol2_closes.parquet (alphabetical)."""
    all30 = [c for c in df.columns if c not in ("date", "TAIEX")]
    u28 = [c for c in all30 if c not in AGGREGATES]
    assert len(all30) == 30 and len(u28) == 28, (len(all30), len(u28))
    return all30, u28


def returns(df: pl.DataFrame, cols: list[str]) -> tuple[list[str], Mat]:
    """Dates of the returns and the T x N matrix of daily simple returns (no gaps allowed in the sample)."""
    p = np.asarray(df.select(cols).to_numpy(), dtype=np.float64)
    assert not np.isnan(p).any(), "a close is missing in the sample"
    return df["date"].to_list()[1:], p[1:] / p[:-1] - 1


def a_factor(n_returns: int, first: str, last: str) -> float:
    """Returns per year: T / (calendar days between the first and last close / 365.25)."""
    return n_returns / ((date.fromisoformat(last) - date.fromisoformat(first)).days / 365.25)


def cov0(x: Mat) -> Mat:
    """Sample covariance matrix with divisor T (rows are dates): Xc' Xc / T."""
    xc = x - x.mean(axis=0)
    return xc.T @ xc / x.shape[0]


def corr(s: Mat) -> Mat:
    """Correlation matrix diag(s)^-1 S diag(s)^-1."""
    d = np.sqrt(np.diag(s))
    return s / np.outer(d, d)


def sign_fix(v: Vec) -> Vec:
    """The book's sign rule: the entry largest in absolute value is positive; on a tie, the first tied entry."""
    a = np.abs(v)
    i = int(np.flatnonzero(a >= a.max() * (1 - TIE))[0])
    return v if v[i] > 0 else -v


def eig_desc(m: Mat) -> tuple[Vec, Mat]:
    """Eigenvalues of a symmetric matrix in descending order, eigenvectors (columns) signed by the sign rule."""
    w, v = np.linalg.eigh(m)
    w, v = w[::-1], v[:, ::-1]
    return w.copy(), np.column_stack([sign_fix(v[:, k]) for k in range(v.shape[1])])


def spec_norm(m: Mat) -> float:
    """Spectral norm of a symmetric matrix: its largest absolute eigenvalue."""
    return float(np.abs(np.linalg.eigvalsh(m)).max())


def lm07_pair() -> tuple[Vec, Vec, float]:
    """LM7's daily total returns of 0050 and 00679B (T = 2,363) and its A = 2,363 / (3,551 / 365.25)."""
    df = pl.read_parquet(PROC / "lm07_returns.parquet").sort("date").drop_nulls("R_0050")
    d = pl.read_parquet(PROC / "lm07_returns.parquet").sort("date")["date"].to_list()
    return (df["R_0050"].to_numpy().astype(np.float64), df["R_00679B"].to_numpy().astype(np.float64),
            a_factor(df.height, d[0], d[-1]))


def etf_pair() -> tuple[Vec, Vec]:
    """LM1's daily total returns of 0050 and 00631L on their 2,902 common dates (LM8's sample)."""
    df = pl.read_parquet(PROC / "etf_daily_returns.parquet").sort("date")
    return df["R_0050"].to_numpy().astype(np.float64), df["R_00631L"].to_numpy().astype(np.float64)
