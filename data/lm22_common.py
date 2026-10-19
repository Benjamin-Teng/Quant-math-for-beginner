"""Shared data, statistics and experiments for LM22's scripts (data/lm22_numbers.py and data/lm22_charts.py import it).

Not a pipeline step of its own. It reads TR23 from data/processed/vol3_taiex.parquet (built and checked by
data/vol3_series.py) and U28 through u28() of data/lm10_series.py (closes in data/processed/vol2_closes.parquet, built
and repaired by data/vol2_series.py). Both builders must have run first. It writes nothing, unless the environment
variable LM22_CACHE names a folder: the experiments then keep their resampled statistics there as .npz files, a
convenience for repeated runs while writing (the pipeline never sets it).

Conventions (plans/vol-4.md, the LM22 brief; plans/vol-4-anchors.md, "LM22", Common definitions):
- TR23: T = 5,849 simple returns R_t = tr_t / tr_(t-1) - 1 from 2003-01-03 to 2026-10-08, log returns r = ln(1 + R),
  years = calendar days / 365.25, A = T / years = 246.12. The 7% regime is the returns dated before 2015-06-01, the 10%
  regime the rest. U28: the 28 leaf sector price indices, T = 4,382 returns from 2008-12-02, A = 245.48; the pair is
  Semiconductor and FinancialInsurance; a calendar year's returns are those dated in it.
- Divisors: s and every moment divide by T (ddof=0); s_u divides by T - 1 and enters only the t-stat. A correlation
  divides by the same count in numerator and denominator. The autocorrelation is LM19's (19.5): full-sample mean,
  divisor T in numerator and denominator. VR(m) is LM19's (19.8): the mean square of the T - m + 1 overlapping m-day
  log-return sums about m r-bar, over m s_r^2, recomputed in each resample from its own r-bar and s_r.
- Estimates: the Sharpe ratio R-bar / s per day with r_f = 0, annualized by sqrt(A) with A fixed at the sample's value;
  the Kelly fraction f_hat = R-bar / s^2; the exact in-sample optimum f_hat* = the root of (4.5), mean of
  R / (1 + f R) = 0, by Newton's method from f_hat inside its bracket; the volatility s sqrt(A).
- Resampling: B = 10,000 unless stated, drawn in chunks of 500 resamples (a chunk is only how the draws are made).
  iid: rng.integers(0, n, size=(500, n)) per chunk, the draws scipy.stats.bootstrap makes with batch=500; one resample
  at a time, rng.integers(0, n, size=n), is the same stream. Stationary (mean block length ell): per resample
  rng.integers(n, size=n), then rng.random(n); a block starts at the first position and wherever the uniform is at
  most 1/ell; inside a block the index steps by one, day T followed by day 1. Circular: ceil(n / ell) starts
  rng.integers(n), blocks of ell days with wrap-around, cut to n. Moving: ceil(n / ell) starts
  rng.integers(n - ell + 1), no wrap, cut to n. arch draws exactly these indices from the same generator.
- Summaries of B values: SE = their standard deviation, divisor B; every quantile is F_boot^-1(u), the order statistic
  ceil(u B) (np.quantile, method "inverted_cdf"); the basic interval is 2 theta_hat minus the percentile ends, reversed.
  Monte Carlo errors follow LM18's batch rule: the statistic on 20 batches of B/20 consecutive resamples, the standard
  deviation of the 20 values (divisor 20) over sqrt(20). A bootstrap p-value's Monte Carlo SE is sqrt(p (1 - p) / B).
- Block lengths, the book's rule: the largest Politis-White stationary estimate (arch's optimal_block_length, column
  "stationary") among the squared demeaned series the statistic uses, rounded.
- Seeds: each experiment creates np.random.default_rng([e, 20261011]) once, at its start (AUTHORING section 8). The
  numbers e are the brief's: 1 E1; 2 iid TR23; 3 stationary TR23 (ell 145); 4 X6's grid; 5 moving, 6 circular; 7 X5's
  paths; 8, 9 the crash correlation; 10-13 the PC1 shares; 14, 15 the windows; 16-18 the tests; 19 the uncentred
  resamples of section 8's knowledge check; 20 the arch check; 21 Problem 6; 22, 23 Problem 11; 24 the widget; 26
  Problem 6's expectation at ell 2 (B = 200,000; the lab's extension uses 25).
"""
import math
import os
import sys
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import polars as pl
from arch.bootstrap import optimal_block_length
from numpy.typing import NDArray
from scipy import stats

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from lm10_series import u28

PROC = HERE / "processed"
SEED = 20261011
EPS = 1e-12                  # the guard for counts against a threshold (PITFALLS section 5)
CHUNK = 500
B = 10_000
B_GRID = 2_000               # X6's other lengths (experiment 4) and Problem 6 (experiment 21)
B_WIDGET = 1_000             # the widget's resamples per replicate (experiment 24)
B_26 = 200_000               # Problem 6's expectation at ell 2 (experiment 26)
GRID = (2, 3, 5, 10, 20, 50, 100, 200, 400)          # experiment 4, in this order
WIDGET_ELLS = (1, 2, 3, 5, 10, 20, 50, 100, 145, 200, 400)
WIDGET_REPS = 3
W60 = 60                     # X5's rolling window
Vec = NDArray[np.float64]
Idx = NDArray[np.int64]
Row = Callable[[np.random.Generator, int, int], Idx]
CACHE = Path(os.environ["LM22_CACHE"]) if os.environ.get("LM22_CACHE") else None


def gen(e: int) -> np.random.Generator:
    """The generator of experiment e: its number first, then the root seed."""
    return np.random.default_rng([e, SEED])


def cached(name: str, make: Callable[[], dict[str, np.ndarray]]) -> dict[str, np.ndarray]:
    if CACHE is None:
        return make()
    f = CACHE / f"{name}.npz"
    if f.exists():
        with np.load(f) as z:
            keys = [str(k) for k in z["arr_0"]]
            return {k: z[f"arr_{i + 1}"] for i, k in enumerate(keys)}
    out = make()
    CACHE.mkdir(parents=True, exist_ok=True)
    np.savez(f, np.array(list(out)), *out.values())
    return out


# ---------------------------------------------------------------- resampling schemes (arch's order of draws)
def sb_row(rng: np.random.Generator, n: int, ell: int) -> Idx:
    """One stationary-bootstrap resample's indices."""
    idx = rng.integers(n, size=n, dtype=np.int64)
    u = rng.random(n)
    new = u <= 1.0 / ell
    new[0] = True
    starts = np.flatnonzero(new)
    bid = np.cumsum(new) - 1
    return (idx[starts][bid] + np.arange(n) - starts[bid]) % n


def cb_row(rng: np.random.Generator, n: int, ell: int) -> Idx:
    nb = -(-n // ell)
    st = rng.integers(n, size=nb, dtype=np.int64)
    return ((st[:, None] + np.arange(ell)).ravel() % n)[:n]


def mb_row(rng: np.random.Generator, n: int, ell: int) -> Idx:
    nb = -(-n // ell)
    st = rng.integers(n - ell + 1, size=nb, dtype=np.int64)
    return (st[:, None] + np.arange(ell)).ravel()[:n]


ROWS: dict[str, Row] = {"sb": sb_row, "cb": cb_row, "mb": mb_row}


def chunks(rng: np.random.Generator, n: int, kind: str, ell: int, b: int = B) -> Iterator[Idx]:
    """b resamples of n indices in chunks of 500 rows: iid when kind is "iid", else the named block scheme."""
    for _ in range(b // CHUNK):
        if kind == "iid":
            yield rng.integers(0, n, size=(CHUNK, n))
        else:
            yield np.stack([ROWS[kind](rng, n, ell) for _ in range(CHUNK)])


def draws(rng: np.random.Generator, n: int, ell: int) -> Idx:
    """One resample: iid when ell is 1, else stationary."""
    return rng.integers(0, n, size=n) if ell == 1 else sb_row(rng, n, ell)


# ---------------------------------------------------------------- summaries of B values
def pct(v: Vec) -> tuple[float, float]:
    q = np.quantile(v, [0.025, 0.975], method="inverted_cdf")
    return float(q[0]), float(q[1])


def sd(c: Vec) -> float:
    return float(c.std())


def lo_end(c: Vec) -> float:
    return pct(c)[0]


def hi_end(c: Vec) -> float:
    return pct(c)[1]


def bse(v: Vec, fn: Callable[[Vec], float]) -> float:
    """LM18's batch SE: fn on 20 batches of consecutive resamples; their SD (divisor 20) over sqrt(20)."""
    vals = np.array([fn(c) for c in np.split(v, 20)])
    return float(vals.std() / math.sqrt(20))


@dataclass
class Summary:
    est: float
    se: float
    lo: float
    hi: float
    mean: float
    se_b: float          # batch SEs of the SE and of the two ends
    lo_b: float
    hi_b: float

    @property
    def blo(self) -> float:
        return 2 * self.est - self.hi

    @property
    def bhi(self) -> float:
        return 2 * self.est - self.lo

    @property
    def bias(self) -> float:
        return self.mean - self.est


def summ(v: Vec, est: float) -> Summary:
    lo, hi = pct(v)
    return Summary(est, float(v.std()), lo, hi, float(v.mean()), bse(v, sd), bse(v, lo_end), bse(v, hi_end))


# ---------------------------------------------------------------- statistics
def acf1(x: Vec) -> Vec:
    """LM19's lag-1 autocorrelation of each row: full-row mean, divisor n in numerator and denominator."""
    c = x - x.mean(axis=-1, keepdims=True)
    return (c[..., 1:] * c[..., :-1]).sum(axis=-1) / (c * c).sum(axis=-1)


def acfk(x: Vec, k: int) -> float:
    c = x - x.mean()
    return float((c[k:] * c[:-k]).sum() / (c * c).sum())


def vr(x: Vec, m: int) -> Vec:
    """LM19's VR(m) of each row of log returns."""
    n = x.shape[-1]
    mu = x.mean(axis=-1, keepdims=True)
    c = np.concatenate([np.zeros(x.shape[:-1] + (1,)), np.cumsum(x, axis=-1)], axis=-1)
    sums = c[..., m:] - c[..., :-m]
    return ((sums - m * mu) ** 2).sum(axis=-1) / (n - m + 1) / (m * x.var(axis=-1))


def exact_kelly(Rx: Vec) -> Vec:
    """Root of (4.5), the mean of R / (1 + f R) = 0, per row, by Newton's method from mean / var inside the bracket."""
    m = Rx.mean(axis=-1)
    pos = m > 0
    f_hi = -1 / Rx.min(axis=-1) * (1 - 1e-12)         # 1 + f R > 0 needs f below 1/|worst day| ...
    f_lo = -1 / Rx.max(axis=-1) * (1 - 1e-12)         # ... and above -1/best day
    a = np.where(pos, 0.0, f_lo)                      # bracket: (4.5) is positive at a, negative at b
    b = np.where(pos, f_hi, 0.0)
    f = m / Rx.var(axis=-1)
    f = np.where((f > a) & (f < b), f, (a + b) / 2)
    for _ in range(200):
        q = Rx / (1 + f[..., None] * Rx)
        h = q.mean(axis=-1)
        a = np.where(h > 0, f, a)
        b = np.where(h > 0, b, f)
        newton = f + h / (q * q).mean(axis=-1)
        new = np.where((newton > a) & (newton < b), newton, (a + b) / 2)
        step = new - f
        f = new
        if np.abs(step).max() < 1e-12:
            break
    assert (1 + f[..., None] * Rx).min() > 0
    assert np.abs((Rx / (1 + f[..., None] * Rx)).mean(axis=-1)).max() < 1e-14
    return f


def tstat(x: Vec) -> Vec:
    """R-bar / (s_u / sqrt(T)) of each row, (21.1) with mu_null = 0."""
    return x.mean(axis=-1) / (x.std(axis=-1, ddof=1) / np.sqrt(x.shape[-1]))


def pw(x: Vec) -> tuple[float, float]:
    """Politis and White's stationary and circular estimates (arch; columns asserted)."""
    ob = optimal_block_length(x)
    assert list(ob.columns) == ["stationary", "circular"]
    a = ob.to_numpy()[0]
    return float(a[0]), float(a[1])


# ---------------------------------------------------------------- TR23
@dataclass
class TR23:
    dates_all: list[str]
    dates: list[str]
    tr: Vec
    R: Vec
    r: Vec
    T: int
    days: int
    years: float
    A: float
    SQA: float
    Rb: float
    s: float
    rb: float
    sr: float
    skew: float
    kurt: float
    pre: NDArray[np.bool_]


def load() -> TR23:
    df = pl.read_parquet(PROC / "vol3_taiex.parquet").sort("date")
    dates_all = [str(d) for d in df["date"].to_list()]
    tr = df["tr"].to_numpy()
    R = df["R"].to_numpy()[1:]
    assert df["R"][0] is None and len(set(dates_all)) == len(dates_all)
    dates = dates_all[1:]
    T = R.size
    r = np.log1p(R)
    days = (df["date"][-1] - df["date"][0]).days
    years = days / 365.25
    A = T / years
    Rb, s = float(R.mean()), float(R.std())
    xc = R - Rb
    return TR23(dates_all, dates, tr, R, r, T, days, years, A, math.sqrt(A), Rb, s, float(r.mean()), float(r.std()),
                float((xc**3).mean() / s**3), float((xc**4).mean() / s**4),
                np.array([d < "2015-06-01" for d in dates]))


D = load()
KEYS5 = ("SR", "Kelly", "vol", "acf", "VR20")


def tr_stats(Rx: Vec, fx: bool = True) -> dict[str, Vec]:
    """The TR23 statistics of each row: annual Sharpe ratio, f_hat, annual volatility, LM19's lag-1 autocorrelation of
    |r|, VR(20) and (with fx) the exact optimum f_hat*."""
    m = Rx.mean(axis=-1)
    sdx = Rx.std(axis=-1)
    rx = np.log1p(Rx)
    out = {"SR": D.SQA * m / sdx, "Kelly": m / sdx**2, "vol": D.SQA * sdx, "acf": acf1(np.abs(rx)), "VR20": vr(rx, 20)}
    if fx:
        out["fx"] = exact_kelly(Rx)
    return out


OBS = {k: float(v[0]) for k, v in tr_stats(D.R[None, :]).items()}


def boot_tr(it: Iterator[Idx], fx: bool = True) -> dict[str, np.ndarray]:
    acc: dict[str, list[Vec]] = {}
    for idx in it:
        for k, v in tr_stats(D.R[idx], fx).items():
            acc.setdefault(k, []).append(v)
    return {k: np.concatenate(v) for k, v in acc.items()}


ELL = round(pw((D.R - D.Rb) ** 2)[0])             # 145, the book's rule on TR23


def exp_tr(e: int, kind: str, ell: int, b: int = B, fx: bool = True) -> dict[str, np.ndarray]:
    """Experiments 2, 3, 5, 6 (and 21): b resamples of TR23 under one scheme, all statistics."""
    return cached(f"e{e}", lambda: boot_tr(chunks(gen(e), D.T, kind, ell, b), fx))


def exp4() -> dict[int, dict[str, np.ndarray]]:
    """X6's grid: one generator, lengths in GRID's order, B_GRID stationary resamples each."""
    def make() -> dict[str, np.ndarray]:
        rng = gen(4)
        out: dict[str, np.ndarray] = {}
        for ell in GRID:
            for k, v in boot_tr(chunks(rng, D.T, "sb", ell, B_GRID), fx=False).items():
                out[f"{ell}_{k}"] = v
        return out
    z = cached("e4", make)
    return {ell: {k: z[f"{ell}_{k}"] for k in KEYS5} for ell in GRID}


def exp7() -> tuple[Idx, Idx]:
    """X5's two paths: one iid resample, then one stationary resample (ell 145), from one generator."""
    rng = gen(7)
    a = rng.integers(0, D.T, size=D.T)
    return a, sb_row(rng, D.T, ELL)


def roll_vol(x: Vec) -> Vec:
    """Standard deviation of each window of 60 returns (its own mean, divisor 60), times sqrt(A)."""
    c1 = np.concatenate([[0.0], np.cumsum(x)])
    c2 = np.concatenate([[0.0], np.cumsum(x * x)])
    m1 = (c1[W60:] - c1[:-W60]) / W60
    m2 = (c2[W60:] - c2[:-W60]) / W60
    return np.sqrt(np.maximum(m2 - m1 * m1, 0.0)) * D.SQA


# ---------------------------------------------------------------- U28
U = u28()
TU = U.X.shape[0]
I_SEMI, I_FIN = U.names.index("Semiconductor"), U.names.index("FinancialInsurance")
PAIR = U.X[:, [I_SEMI, I_FIN]]
V2 = 1 + 2 * float(stats.norm.pdf(2.0) / stats.norm.sf(2.0))       # Var(Z | |Z| >= 2), LM16's Deep Dive
YEARS_U = np.array([d[:4] for d in U.dates])


def corr0(a: Vec, b: Vec) -> float:
    ac, bc = a - a.mean(), b - b.mean()
    return float((ac * bc).mean() / math.sqrt(float((ac * ac).mean() * (bc * bc).mean())))


def crash(P: Vec) -> tuple[float, float, int]:
    """Correlation on the days Semiconductor moves 2 standard deviations either way; (16.10) at the sample's rho."""
    a, b = P[:, 0], P[:, 1]
    z = (a - a.mean()) / a.std()
    sel = np.abs(z) >= 2 - EPS
    rho = corr0(a, b)
    return corr0(a[sel], b[sel]), rho / math.sqrt(rho**2 + (1 - rho**2) / V2), int(sel.sum())


def pc1_share(Xy: Vec) -> float:
    return float(np.linalg.eigvalsh(np.corrcoef(Xy, rowvar=False))[-1] / Xy.shape[1])


def exp_crash(e: int, ell: int) -> dict[str, np.ndarray]:
    def make() -> dict[str, np.ndarray]:
        rng = gen(e)
        v = np.array([crash(PAIR[draws(rng, TU, ell)]) for _ in range(B)])
        return {"corr": v[:, 0], "model": v[:, 1], "days": v[:, 2]}
    return cached(f"e{e}", make)


def year_rows(y: str) -> Vec:
    return U.X[np.flatnonzero(YEARS_U == y)]


def exp_pc1(e: int, y: str, ell: int) -> Vec:
    Xy = year_rows(y)

    def make() -> dict[str, np.ndarray]:
        rng = gen(e)
        return {"v": np.array([pc1_share(Xy[draws(rng, Xy.shape[0], ell)]) for _ in range(B)])}
    return cached(f"e{e}", make)["v"]


# ---------------------------------------------------------------- LM18's windows
M5 = round(5 * D.A)


def windows(x: Vec) -> tuple[float, float]:
    """Share of the T - m + 1 windows of m log returns with a negative sum; standard deviation of the sums."""
    c = np.concatenate([[0.0], np.cumsum(x)])
    lg = c[M5:] - c[:-M5]
    return float((lg < 0).mean()), float(lg.std())


def exp_windows(e: int, ell: int) -> dict[str, np.ndarray]:
    def make() -> dict[str, np.ndarray]:
        rng = gen(e)
        v = np.array([windows(D.r[draws(rng, D.T, ell)]) for _ in range(B)])
        return {"share": v[:, 0], "sd": v[:, 1]}
    return cached(f"e{e}", make)


# ---------------------------------------------------------------- tests
def exp_test(e: int, x: Vec, ell: int) -> Vec:
    """Resampled t-stats of x - x-bar (the null imposed): iid when ell is 1, else stationary."""
    x0 = x - x.mean()

    def make() -> dict[str, np.ndarray]:
        rng = gen(e)
        it = chunks(rng, x.size, "iid" if ell == 1 else "sb", ell)
        return {"t": np.concatenate([tstat(x0[idx]) for idx in it])}
    return cached(f"e{e}", make)["t"]


def exp19() -> Vec:
    def make() -> dict[str, np.ndarray]:
        return {"t": np.concatenate([tstat(D.R[idx]) for idx in chunks(gen(19), D.T, "iid", 1)])}
    return cached("e19", make)["t"]


def exp_kelly_only(e: int, x: Vec, kind: str, ell: int) -> Vec:
    """Problem 11: f_hat in b = B resamples of a sub-sample."""
    def make() -> dict[str, np.ndarray]:
        return {"v": np.concatenate([x[idx].mean(axis=-1) / x[idx].var(axis=-1)
                                     for idx in chunks(gen(e), x.size, kind, ell)])}
    return cached(f"e{e}", make)["v"]


# ---------------------------------------------------------------- the widget (experiment 24)
def exp24() -> dict[str, np.ndarray]:
    """For each length of WIDGET_ELLS in order, three replicates of B_WIDGET resamples of TR23 (ell 1 is iid), one
    generator; the five statistics of tr_stats (no f_hat*)."""
    def make() -> dict[str, np.ndarray]:
        rng = gen(24)
        out: dict[str, np.ndarray] = {}
        for ell in WIDGET_ELLS:
            for rep in range(WIDGET_REPS):
                kind = "iid" if ell == 1 else "sb"
                for k, v in boot_tr(chunks(rng, D.T, kind, ell, B_WIDGET), fx=False).items():
                    out[f"{ell}_{rep}_{k}"] = v
        return out
    return cached("e24", make)
