"""LM22 anchors (Resampling Methods): every number the Stage 1 brief quotes.

Reads TR23 from data/processed/vol3_taiex.parquet (columns date, tr, price, R, Rp; R is the total-return index's simple
daily return, null on the first row; built and checked by data/vol3_series.py) and U28 through data/lm10_series.py
(u28(), which reads data/processed/vol2_closes.parquet, built and repaired by data/vol2_series.py). Both builders must
have run first. Nothing else is read and nothing is written.

Conventions.
- TR23: T = 5,849 simple returns R_t = tr_t / tr_(t-1) - 1 from 2003-01-03 to 2026-10-08; log returns r = ln(1 + R);
  years = calendar days between the first and last close / 365.25; A = T / years = 246.12. U28: the 28 leaf sector
  price indices, T = 4,382 returns from 2008-12-02, A = 245.4794 (u28().A); the pair is Semiconductor and
  FinancialInsurance; a calendar year's returns are those dated in that year. The 7% regime is TR23's returns dated
  before 2015-06-01, the 10% regime the rest.
- Divisors: s, s^2 and every moment divide by T (ddof=0); s_u divides by T - 1 (ddof=1) and enters only the t-stat
  R bar / (s_u / sqrt(T)) of the bootstrap tests. A correlation divides by the same count in numerator and
  denominator. The autocorrelation is LM19's: full-sample mean, divisor T in numerator and denominator. VR(m) is
  LM19's (19.8): the mean square of the T - m + 1 overlapping m-day log-return sums about m times the sample's mean
  log return, over m s_r^2 (s_r with divisor T).
- Return type: one-day statistics on R (Sharpe ratio, Kelly fraction, volatility, the U28 statistics); sums over days on
  r (VR, the windows, the autocorrelation of |r|). The Sharpe ratio is R bar / s per day with r_f = 0, annualized by
  sqrt(A) with A fixed at the sample's value; the volatility is s sqrt(A); the Kelly fraction f_hat is R bar / s^2
  (LM4's quadratic rule (4.3) estimated) and the exact in-sample optimum f_hat* is the root of (4.5), by Newton's
  method from R bar / s^2.
- Drawing resamples: B = 10,000 resamples of the whole sample unless stated. Draws are made in chunks of 500 resamples
  (rows); a chunk is only how the draws are made. iid: rng.integers(0, n, size=(500, n)) per chunk, the draws
  scipy.stats.bootstrap makes with batch=500; experiments 8 to 15 draw one resample at a time,
  rng.integers(0, n, size=n), which is the same stream. Stationary block bootstrap with mean block length ell: per
  resample rng.integers(n, size=n), then rng.random(n); a block starts at the first position and wherever the uniform
  is at most 1/ell; inside a block the index steps by one, wrapping from the last day to the first. Circular blocks:
  ceil(n/ell) starts rng.integers(n), blocks of ell days with wrap-around, cut to n. Moving blocks: ceil(n/ell) starts
  rng.integers(n - ell + 1), no wrap, cut to n. arch's StationaryBootstrap, CircularBlockBootstrap and
  MovingBlockBootstrap draw exactly these indices from the same generator (A22-42).
- Summaries of B resampled values: the bootstrap SE is their standard deviation, divisor B. Every quantile is
  F_boot^-1(u), the order statistic ceil(u B) (np.quantile, method "inverted_cdf", LM14's quantile function): the 95%
  percentile interval is the order statistics ceil(0.025 B) and ceil(0.975 B), 250 and 9,750 for B = 10,000; the
  basic interval is 2 theta_hat minus the percentile interval's ends, in reverse order. "sd of t" divides by B; the
  "95% point of |t|" is the order statistic ceil(0.95 B) of |t|, the 9,500th. The median of five returns is
  F_hat^-1(1/2), their third smallest.
- Monte Carlo errors (LM18's batch rule): the B values, in resample order, are split into 20 batches of B/20
  consecutive resamples (500 for B = 10,000; 100 for 2,000; 50 for 1,000); the statistic is computed on each batch (a
  standard deviation with divisor B/20; a percentile end as the batch's order statistic ceil(0.025 B/20) or
  ceil(0.975 B/20), the 13th and 488th of 500); the batch SE is the standard deviation of the 20 batch values, divisor
  20, over sqrt(20). A bootstrap p-value's Monte Carlo SE is sqrt(p(1 - p)/B). A ratio of two bootstrap SEs from
  independent experiments has Monte Carlo SE equal to the ratio times the root sum of squares of their relative batch
  SEs.
- Block length, the book's rule: the largest Politis-White stationary-bootstrap estimate (arch's optimal_block_length,
  column "stationary") among the squared demeaned returns of the series the statistic uses, rounded to an integer:
  145 for TR23, 130 for the U28 pair, 7 and 18 for the 28 sectors in 2017 and 2020, 108 in TR23's 7% regime and 36 in
  its 10% regime.
- Crash correlation (E7, LM16's (16.10)): Semiconductor's returns standardized with the full-sample mean and s
  (divisor T); the event days have |z| >= 2 - 1e-12, asserted equal to the strict count with no |z| within 1e-9 of 2;
  the data correlation is the Pearson correlation of the pair's returns on the event days, each return centred at its
  own event-day mean, divisor the number of event days; the model value is rho / sqrt(rho^2 + (1 - rho^2) / V) with
  rho the pair's full-sample correlation (divisor T) and V = Var(Z | |Z| >= 2) = 1 + 2 phi(2) / Phi(-2). A resample
  repeats every step on its own days: re-standardized, reselected, both correlations recomputed.
- Rolling volatility (X5): the standard deviation of each window of 60 returns (centred at the window's mean, divisor
  60) times sqrt(A). A window's session is the 1-based number of its last return; on a resampled path it is a
  position in the path, not a date.
- Counts: the windows under water are recounted exactly with Fraction on the two-decimal closes. Bootstrap counts
  compare continuous values (no ties; asserted).
- Seeds (AUTHORING section 8): each experiment creates its generator once at its start, rng =
  np.random.default_rng([e, 20261011]), with e its stated number: 1 E1; 2 the iid resamples of TR23 (E2-E5, the case,
  X2-X4, X7's iid row; the SciPy check re-creates stream 2 on purpose and draws the same resamples); 3 the stationary
  resamples of TR23 at ell = 145 (the same uses; Problem 10 re-creates it); 4 the block-length grid of X6 (lengths
  other than 1 and 145, B = 2,000 each, in the order listed); 5 moving and 6 circular blocks at ell = 145 (X7); 7 the
  two paths of X5; 8 and 9 the crash correlation (iid, block); 10 to 13 the PC1 shares (2017 iid, 2017 block, 2020
  iid, 2020 block); 14 and 15 LM18's windows (block, iid); 16 to 18 the bootstrap tests (7% regime iid, 7% regime
  block, full sample block); 19 the uncentred resamples of the section 8 knowledge check; 20 the arch index check;
  21 Problem 6 (ell = 2, B = 2,000); 22 and 23 Problem 11 (10% regime iid, block). Experiment 24, the widget's
  precomputed histograms, belongs to data/lm22_charts.py and has no anchor.
- Rounding: every form the brief prints goes through pr(), which rounds the unrounded value at its printed precision
  and flags it when it lies within 0.1 of a unit of its last printed digit from a rounding boundary ("near a rounding
  boundary"). Each line gives the unrounded values, then "-> printed" and the printed forms.

Prints one line per anchor, "A22-NN <value>", in ID order, and writes nothing. Runs in about three minutes.

Run:  PYTHONUTF8=1 uv run python data/vol4_anchors_lm22.py [repository root]
"""
import sys
from collections.abc import Callable, Iterator
from fractions import Fraction
from itertools import product
from math import ceil, floor, sqrt
from pathlib import Path
from typing import cast

import numpy as np
import polars as pl
from arch.bootstrap import (
    CircularBlockBootstrap,
    MovingBlockBootstrap,
    StationaryBootstrap,
    optimal_block_length,
)
from numpy.typing import NDArray
from scipy import stats

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "data"))
from lm10_series import u28

PROC = ROOT / "data" / "processed"
EPS = 1e-12
ROOT_SEED = 20261011
CHUNK = 500
B = 10_000
Z975 = float(stats.norm.ppf(0.975))
Vec = NDArray[np.float64]
Idx = NDArray[np.int64]
Row = Callable[[np.random.Generator, int, int], Idx]

OUT: list[str] = []
FLAGS: list[str] = []


def put(value: str) -> None:
    line = f"A22-{len(OUT) + 1:02d} {value}"
    if FLAGS:
        line += " [near a rounding boundary: " + "; ".join(dict.fromkeys(FLAGS)) + "]"
        FLAGS.clear()
    OUT.append(line)


def pr(x: float, nd: int, scale: float = 1.0, suffix: str = "") -> str:
    """Printed form of x * scale with nd decimals; flags a value within 0.1 of a unit of a rounding boundary."""
    y = float(x) * scale
    u = abs(y) * 10**nd
    if abs(u - floor(u) - 0.5) < 0.1:
        FLAGS.append(f"{y:.{nd + 3}f} printed {y:.{nd}f}")
    out = f"{y:.{nd}f}"
    if out.startswith("-") and float(out) == 0:
        out = out[1:]
    return out + suffix


def gen(e: int) -> np.random.Generator:
    return np.random.default_rng([e, ROOT_SEED])


# ---------------------------------------------------------------- resampling schemes
def sb_row(rng: np.random.Generator, n: int, ell: int) -> Idx:
    """One stationary-bootstrap resample's indices, in arch's order of draws."""
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


def iid_chunks(rng: np.random.Generator, n: int, b: int = B) -> Iterator[Idx]:
    for _ in range(b // CHUNK):
        yield rng.integers(0, n, size=(CHUNK, n))


def row_chunks(rng: np.random.Generator, n: int, row: Row, ell: int, b: int = B) -> Iterator[Idx]:
    for _ in range(b // CHUNK):
        yield np.stack([row(rng, n, ell) for _ in range(CHUNK)])


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
    """LM18's batch SE: fn on 20 batches of consecutive resamples; their SD (divisor 20) / sqrt(20)."""
    vals = np.array([fn(c) for c in np.split(v, 20)])
    return float(vals.std() / sqrt(20))


def summ(v: Vec, est: float) -> str:
    """Unrounded summary of B bootstrap values, with batch SEs."""
    lo, hi = pct(v)
    return (f"SE {v.std():.6g} (batch {bse(v, sd):.2g}); percentile {lo:.6g} to {hi:.6g} (batch {bse(v, lo_end):.2g}, "
            f"{bse(v, hi_end):.2g}); basic {2 * est - hi:.6g} to {2 * est - lo:.6g}; mean {v.mean():.6g}")


def fq(v: Vec, est: float) -> dict[str, float]:
    lo, hi = pct(v)
    return {"se": float(v.std()), "lo": lo, "hi": hi, "blo": 2 * est - hi, "bhi": 2 * est - lo, "mean": float(v.mean())}


def ivp(d: dict[str, float], nd: int, scale: float = 1.0, suf: str = "", se: int | None = None,
        basic: bool = False, mean: int | None = None) -> str:
    """Printed forms of a summary: SE (in points when scaled), percentile ends, optionally basic ends and mean."""
    out = [] if se is None else [f"SE {pr(d['se'], se, scale)}"]
    out.append(f"{pr(d['lo'], nd, scale, suf)} to {pr(d['hi'], nd, scale, suf)}")
    if basic:
        out.append(f"basic {pr(d['blo'], nd, scale, suf)} to {pr(d['bhi'], nd, scale, suf)}")
    if mean is not None:
        out.append(f"mean {pr(d['mean'], mean, scale, suf)}")
    return ", ".join(out)


# ---------------------------------------------------------------- TR23
df = pl.read_parquet(PROC / "vol3_taiex.parquet").sort("date")
dates_all = [str(d) for d in df["date"].to_list()]
tr = df["tr"].to_numpy()
R = df["R"].to_numpy()[1:]
dates = dates_all[1:]
assert df["R"][0] is None and len(set(dates_all)) == len(dates_all)
T = R.size
r = np.log1p(R)
days = (df["date"][-1] - df["date"][0]).days
years = days / 365.25
A = T / years
SQA = sqrt(A)
Rb, s = float(R.mean()), float(R.std())
rb, sr_ = float(r.mean()), float(r.std())
xc = R - Rb
skew = float((xc**3).mean() / s**3)
kurt = float((xc**4).mean() / s**4)
SR = Rb / s


def acf1(x: Vec) -> Vec:
    """LM19's lag-1 autocorrelation of each row: full-row mean, divisor n in numerator and denominator."""
    c = x - x.mean(axis=-1, keepdims=True)
    return (c[..., 1:] * c[..., :-1]).sum(axis=-1) / (c * c).sum(axis=-1)


def vr(x: Vec, m: int) -> Vec:
    """VR(m) of each row of log returns (module docstring)."""
    n = x.shape[-1]
    mu = x.mean(axis=-1, keepdims=True)
    c = np.concatenate([np.zeros(x.shape[:-1] + (1,)), np.cumsum(x, axis=-1)], axis=-1)
    sums = c[..., m:] - c[..., :-m]
    return ((sums - m * mu) ** 2).sum(axis=-1) / (n - m + 1) / (m * x.var(axis=-1))


def exact_kelly(Rx: Vec) -> Vec:
    """Root of (4.5), the mean of R / (1 + f R) = 0, per row, by Newton's method from mean / var."""
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


def tr_stats(Rx: Vec) -> dict[str, Vec]:
    m = Rx.mean(axis=-1)
    sdx = Rx.std(axis=-1)
    rx = np.log1p(Rx)
    return {"SR": SQA * m / sdx, "Kelly": m / sdx**2, "vol": SQA * sdx, "acf": acf1(np.abs(rx)), "VR20": vr(rx, 20),
            "fx": exact_kelly(Rx)}


OBS = {k: float(v[0]) for k, v in tr_stats(R[None, :]).items()}
KEL, VOL, FX = OBS["Kelly"], OBS["vol"], OBS["fx"]


def boot_tr(chunks: Iterator[Idx]) -> dict[str, Vec]:
    acc: dict[str, list[Vec]] = {k: [] for k in OBS}
    for idx in chunks:
        st = tr_stats(R[idx])
        for k, lst in acc.items():
            lst.append(st[k])
    return {k: np.concatenate(v) for k, v in acc.items()}


def pw(x: Vec) -> tuple[float, float]:
    ob = optimal_block_length(x)
    assert list(ob.columns) == ["stationary", "circular"]
    a = ob.to_numpy()[0]
    return float(a[0]), float(a[1])


def tstat(x: Vec) -> Vec:
    return x.mean(axis=-1) / (x.std(axis=-1, ddof=1) / np.sqrt(x.shape[-1]))


# ---------------------------------------------------------------- U28
U = u28()
X = U.X
TU = X.shape[0]
i1, i2 = U.names.index("Semiconductor"), U.names.index("FinancialInsurance")
PAIR = X[:, [i1, i2]]
V2 = 1 + 2 * float(stats.norm.pdf(2.0) / stats.norm.sf(2.0))       # Var(Z | |Z| >= 2), LM16's Deep Dive


def corr0(a: Vec, b: Vec) -> float:
    """Pearson correlation, each series centred at its own mean, the same divisor in numerator and denominator."""
    ac, bc = a - a.mean(), b - b.mean()
    return float((ac * bc).mean() / sqrt(float((ac * ac).mean() * (bc * bc).mean())))


def crash(P: Vec) -> tuple[float, float, int]:
    """Correlation on the days Semiconductor moves 2 standard deviations either way; (16.10) at the sample's rho."""
    a, b = P[:, 0], P[:, 1]
    z = (a - a.mean()) / a.std()
    sel = np.abs(z) >= 2 - EPS
    rho = corr0(a, b)
    return corr0(a[sel], b[sel]), rho / sqrt(rho**2 + (1 - rho**2) / V2), int(sel.sum())


def pc1_share(Xy: Vec) -> float:
    return float(np.linalg.eigvalsh(np.corrcoef(Xy, rowvar=False))[-1] / Xy.shape[1])


ydates = np.array([d[:4] for d in U.dates])
pre = np.array([d < "2015-06-01" for d in dates])
KEEP: dict[str, float] = {}                                           # values that later stems quote

# ================================================================ data role
put(f"closes {len(dates_all)} {dates_all[0]} to {dates_all[-1]}; T {T} returns {dates[0]} to {dates[-1]}; "
    f"7% regime {int(pre.sum())} returns to {dates[int(np.flatnonzero(pre)[-1])]}, 10% regime {int((~pre).sum())} "
    f"from {dates[int(np.flatnonzero(~pre)[0])]}")                                                                  # 01
put(f"days {days}; years {years:.7f}; A {A:.6f}; sqrt(A) {SQA:.6f} -> printed {days}, {pr(years, 4)}, {pr(A, 2)}, "
    f"{pr(SQA, 2)}")                                                                                                # 02
put(f"Rbar {Rb:.10%}; s {s:.8%}; rbar {rb:.8%}; s_r {sr_:.8%}; Skew {skew:.8f}; Kurt {kurt:.8f} (excess "
    f"{kurt - 3:.6f}) -> printed {pr(Rb, 6, 100, '%')}, {pr(s, 4, 100, '%')}, Skew {pr(skew, 2)} and {pr(skew, 4)}, "
    f"Kurt {pr(kurt, 2)} and {pr(kurt, 4)}")                                                                        # 03
put(f"U28 T {TU} returns {U.dates[0]} to {U.dates[-1]}; years {U.years:.6f}; A {U.A:.6f}; pair {U.names[i1]}, "
    f"{U.names[i2]} -> printed {TU}, {pr(U.A, 2)}")                                                                # 04

# ================================================================ the case's estimates (LM19's and LM20's)
put(f"SR per day {SR:.8f}; annualized {SR * SQA:.6f} -> printed {pr(SR, 4)}, {pr(SR * SQA, 2)}")                   # 05
put(f"f_hat = Rbar/s^2 {KEL:.6f}; exact optimum f_hat* {FX:.6f} (LM17 printed 4.14 and 4.1381, lm17.md:36, 239, "
    "248) -> printed "
    f"{pr(KEL, 2)}, {pr(FX, 2)} ({pr(FX, 4)})")                                                                    # 06
put(f"volatility s sqrt(A) {VOL:.6%} -> printed {pr(VOL, 2, 100, '%')}")                                          # 07
pw_R, pw_R2, pw_r2 = pw(R), pw(xc**2), pw((r - rb) ** 2)
ELL = round(pw_R2[0])
CAP = ceil(min(3 * sqrt(T), T / 3))
put(f"optimal_block_length returns columns 'stationary', 'circular'; R: {pw_R[0]:.6f}, {pw_R[1]:.6f}; (R - Rbar)^2: "
    f"{pw_R2[0]:.6f}, {pw_R2[1]:.6f}; (r - rbar)^2: {pw_r2[0]:.6f}, {pw_r2[1]:.6f}; ell = {ELL}; b_max {CAP} -> "
    f"printed {pr(pw_R[0], 1)} ({pr(pw_R[0], 2)}, circular {pr(pw_R[1], 2)}); {pr(pw_R2[0], 1)} ({pr(pw_R2[0], 2)}, "
    f"circular {pr(pw_R2[1], 2)}); {pr(pw_r2[0], 2)}; ell {ELL}; cap {CAP}")                                      # 08

IID = boot_tr(iid_chunks(gen(2), T))                                  # experiment 2
SB = boot_tr(row_chunks(gen(3), T, sb_row, ELL))                      # experiment 3
put("SR iid (e 2): " + summ(IID["SR"], OBS["SR"]) + " -> printed "
    + ivp(fq(IID["SR"], OBS["SR"]), 2, se=3, basic=True))                                                           # 09
put("Kelly iid (e 2): " + summ(IID["Kelly"], KEL) + " -> printed " + ivp(fq(IID["Kelly"], KEL), 1, se=2, basic=True))  # 10
put("vol iid (e 2): " + summ(IID["vol"], VOL) + " -> printed " + ivp(fq(IID["vol"], VOL), 1, 100, "%", se=2))   # 11
put(f"SR block ell {ELL} (e 3): " + summ(SB["SR"], OBS["SR"]) + " -> printed " + ivp(fq(SB["SR"], OBS["SR"]), 2, se=3))  # 12
put(f"Kelly block ell {ELL} (e 3): " + summ(SB["Kelly"], KEL) + " -> printed "
    + ivp(fq(SB["Kelly"], KEL), 1, se=2, basic=True))                                                              # 13
put(f"vol block ell {ELL} (e 3): " + summ(SB["vol"], VOL) + " -> printed " + ivp(fq(SB["vol"], VOL), 1, 100, "%", se=2))  # 14
rat, shown, mxs = [], [], []
for key in ("SR", "Kelly", "vol"):
    wi = pct(IID[key])[1] - pct(IID[key])[0]
    wb = pct(SB[key])[1] - pct(SB[key])[0]
    mx = max(bse(d[key], fn) for d in (IID, SB) for fn in (lo_end, hi_end))
    rat.append(f"{key} width iid {wi:.6g} block {wb:.6g} ratio {wb / wi:.6f}; SE ratio "
               f"{SB[key].std() / IID[key].std():.6f}; largest batch SE of the four ends {mx:.6g}")
    shown.append(pr(wb / wi, 1))
    mxs.append(mx)
put("; ".join(rat) + f" -> printed width ratios {', '.join(shown)}; ends' Monte Carlo SEs at most {pr(mxs[0], 3)} "
    f"(Sharpe), {pr(mxs[1], 2)} (Kelly), {pr(mxs[2], 2, 100)} points (volatility)")                                # 15
HW4 = (7.6 - 2.7) / 2 / 5.42
HWT = (pct(IID["Kelly"])[1] - pct(IID["Kelly"])[0]) / 2 / KEL
put("LM4 printed (lm04.md:543-549, 0050, 2,902 returns): SE 0.0230% a day against 0.0871%, 26%; interval 0.042% to "
    f"0.132%; exact Kelly band 2.7 to 7.6, quadratic 2.7 to 8.6; full-sample 5.42; half-width / estimate: LM4's band "
    f"{HW4:.6f}, TR23's iid percentile interval {HWT:.6f} -> printed {pr(HW4, 0, 100, '%')}, {pr(HWT, 0, 100, '%')}")  # 16

# ================================================================ E1: five returns, the ideal bootstrap
five = np.array([0.012, -0.008, 0.003, -0.025, 0.006])
n5 = five.size
allres = np.array(list(product(range(n5), repeat=n5)))
mean_all = five[allres].mean(axis=1)
med_all = np.quantile(five[allres], 0.5, axis=1, method="inverted_cdf")
assert np.array_equal(med_all, np.median(five[allres], axis=1))
b1 = gen(1).integers(0, n5, size=(1000, n5))                          # experiment 1
m1 = five[b1].mean(axis=1)
md1 = np.quantile(five[b1], 0.5, axis=1, method="inverted_cdf")
s5 = float(five.std())
put(f"five returns (LM18 Problem 4): mean {five.mean():.4%}; s {s5:.6%}; s/sqrt(5) {s5 / sqrt(5):.6%}; all "
    f"{allres.shape[0]} resamples: SE of mean {mean_all.std():.6%}, SE of median {med_all.std():.6%}; Pr(median = each "
    "return) " + ", ".join(f"{x:+.1%}: {Fraction(int((med_all == x).sum()), allres.shape[0])}" for x in np.sort(five))
    + f"; e 1, B = 1,000: SE of mean {m1.std():.6%} (batch {bse(m1, sd):.4%}), SE of median {md1.std():.6%} (batch "
    f"{bse(md1, sd):.4%}) -> printed {pr(five.mean(), 2, 100, '%')}, {pr(s5, 4, 100, '%')}, "
    f"{pr(s5 / sqrt(5), 3, 100, '%')}, {pr(float(med_all.std()), 3, 100, '%')}; B = 1,000: "
    f"{pr(float(m1.std()), 2, 100, '%')} ± {pr(bse(m1, sd), 2, 100)}, {pr(float(md1.std()), 2, 100, '%')} ± "
    f"{pr(bse(md1, sd), 2, 100)}")                                                                                 # 17

# ================================================================ E2: the Sharpe ratio
se_sr = sqrt((1 - SR * skew + SR**2 * (kurt - 1) / 4) / T)
se_sr_n = sqrt((1 + SR**2 / 2) / T)
dlo, dhi = SR * SQA - Z975 * se_sr * SQA, SR * SQA + Z975 * se_sr * SQA
put(f"delta (LM20's, iid, plug-in Skew and Kurt) SE daily {se_sr:.6f}, annual {se_sr * SQA:.6f}; normal-model SE daily "
    f"{se_sr_n:.6f}, annual {se_sr_n * SQA:.6f}; 1/sqrt(T) {1 / sqrt(T):.8f}; bootstrap SE daily "
    f"{IID['SR'].std() / SQA:.6f}; delta interval annual {dlo:.6f} to {dhi:.6f} -> printed {pr(se_sr * SQA, 3)}, "
    f"{pr(se_sr_n * SQA, 3)}, {pr(dlo, 2)} to {pr(dhi, 2)} (LM20's); 1/sqrt(T) {pr(1 / sqrt(T), 4)}")             # 18


def sr_vec(x: Vec, axis: int = -1) -> Vec:
    return SQA * x.mean(axis=axis) / x.std(axis=axis)


def kel_vec(x: Vec, axis: int = -1) -> Vec:
    return x.mean(axis=axis) / x.var(axis=axis)


sp = {}
for meth in ("percentile", "basic", "BCa"):
    for nm, fn in (("SR", sr_vec), ("Kelly", kel_vec)):              # stream 2 re-created on purpose
        sp[(meth, nm)] = stats.bootstrap((R,), fn, n_resamples=B, batch=CHUNK, vectorized=True, method=meth,
                                         rng=gen(2))
assert np.array_equal(sp[("percentile", "SR")].bootstrap_distribution, IID["SR"])
assert np.allclose(sp[("percentile", "Kelly")].bootstrap_distribution, IID["Kelly"], rtol=0, atol=1e-12)


def ci(meth: str, nm: str) -> tuple[float, float]:
    c = sp[(meth, nm)].confidence_interval
    return float(c.low), float(c.high)


sp_lo, sp_hi = ci("percentile", "SR")
sb_lo, sb_hi = ci("BCa", "SR")
se_sp = float(sp[("percentile", "SR")].standard_error)
put("SciPy bootstrap(batch=500, rng=default_rng([2, 20261011])): same resamples as e 2 (asserted); SR percentile "
    f"(linear interpolation) {sp_lo:.6f} to {sp_hi:.6f} against inverted_cdf {pct(IID['SR'])[0]:.6f} to "
    f"{pct(IID['SR'])[1]:.6f}; basic {ci('basic', 'SR')[0]:.6f} to {ci('basic', 'SR')[1]:.6f}; BCa {sb_lo:.6f} to "
    f"{sb_hi:.6f}; standard_error (divisor B - 1) {se_sp:.8f} against divisor B {IID['SR'].std():.8f} -> printed "
    f"{pr(sp_lo, 4)} against {pr(pct(IID['SR'])[0], 4)}; BCa {pr(sb_lo, 2)} to {pr(sb_hi, 2)}; {pr(se_sp, 5)} against "
    f"{pr(float(IID['SR'].std()), 5)}")                                                                            # 19

# ================================================================ E3: the Kelly fraction
se_k = sqrt((1 - 2 * SR * skew + SR**2 * (kurt - 1)) / (s**2 * T))
se_k_n = sqrt((1 + 2 * SR**2) / (s**2 * T))
se_k_m = 1 / (s * sqrt(T))
klo, khi = KEL - Z975 * se_k, KEL + Z975 * se_k
kb_lo, kb_hi = ci("BCa", "Kelly")
put(f"delta SE of f_hat (LM20's (20.9)): plug-in {se_k:.6f}, normal model {se_k_n:.6f}, mean only 1/(s sqrt T) "
    f"{se_k_m:.6f}; plug-in interval {klo:.6f} to {khi:.6f}; SciPy on e 2's resamples: percentile "
    f"{ci('percentile', 'Kelly')[0]:.6f} to {ci('percentile', 'Kelly')[1]:.6f}, basic {ci('basic', 'Kelly')[0]:.6f} to "
    f"{ci('basic', 'Kelly')[1]:.6f}, BCa {kb_lo:.6f} to {kb_hi:.6f} -> printed {pr(se_k, 3)}, {pr(se_k_n, 3)}, "
    f"{pr(se_k_m, 3)}, {pr(klo, 2)} to {pr(khi, 2)} (LM20's); BCa {pr(kb_lo, 1)} to {pr(kb_hi, 1)}")              # 20
put(f"exact optimum {FX:.6f}: iid (e 2) " + summ(IID["fx"], FX) + f" // block ell {ELL} (e 3) " + summ(SB["fx"], FX)
    + " -> printed iid " + ivp(fq(IID["fx"], FX), 1, se=2) + "; blocks " + ivp(fq(SB["fx"], FX), 1, se=2))       # 21

# ================================================================ E4: what resampling days cannot see
a_ = np.abs(r)
ac_ = a_ - a_.mean()
lag20 = float((ac_[20:] * ac_[:-20]).sum() / (ac_ * ac_).sum())
pc1 = float(np.corrcoef(a_[:-1], a_[1:])[0, 1])
pc20 = float(np.corrcoef(a_[:-20], a_[20:])[0, 1])
n_ge = int((IID["acf"] >= OBS["acf"]).sum())
d_i, d_b = fq(IID["acf"], OBS["acf"]), fq(SB["acf"], OBS["acf"])
put(f"acf abs(r) (LM19's convention) lag 1 {OBS['acf']:.6f}, lag 20 {lag20:.6f}; LM17's pair correlations lag 1 "
    f"{pc1:.6f}, lag 20 {pc20:.6f}; iid (e 2): " + summ(IID["acf"], OBS["acf"]) + f"; bias "
    f"{d_i['mean'] - OBS['acf']:.6f}; iid resamples at or above the estimate {n_ge} of {B} // block ell {ELL} (e 3): "
    + summ(SB["acf"], OBS["acf"]) + f" -> printed {pr(OBS['acf'], 3)}; LM17's {pr(pc1, 3)} and {pr(pc20, 3)}; iid "
    f"{pr(d_i['lo'], 3)} to {pr(d_i['hi'], 3)}, mean {pr(d_i['mean'], 4)}, basic {pr(d_i['blo'], 3)} to "
    f"{pr(d_i['bhi'], 3)}, bias {pr(d_i['mean'] - OBS['acf'], 3)}, {n_ge} of {B}; blocks {pr(d_b['lo'], 2)} to "
    f"{pr(d_b['hi'], 2)}, mean {pr(d_b['mean'], 3)}")                                                              # 22
d_i, d_b = fq(IID["VR20"], OBS["VR20"]), fq(SB["VR20"], OBS["VR20"])
put(f"VR(20) {OBS['VR20']:.6f}; iid (e 2): " + summ(IID["VR20"], OBS["VR20"]) + f" // block ell {ELL} (e 3): "
    + summ(SB["VR20"], OBS["VR20"]) + f" -> printed {pr(OBS['VR20'], 3)}; iid mean {pr(d_i['mean'], 3)}, "
    f"{pr(d_i['lo'], 2)} to {pr(d_i['hi'], 2)}, SE {pr(d_i['se'], 3)}; blocks mean {pr(d_b['mean'], 3)}, "
    f"{pr(d_b['lo'], 2)} to {pr(d_b['hi'], 2)}, SE {pr(d_b['se'], 3)}")                                           # 23

# ================================================================ E5: the volatility
se_s = s * sqrt((kurt - 1) / (4 * T))
v_i, v_b = float(IID["vol"].std()), float(SB["vol"].std())
put(f"SE(s) = s sqrt((Kurt - 1)/(4T)) (LM20's) {se_s:.6%} a day, annual {se_s * SQA:.6%}; iid bootstrap SE annual "
    f"{v_i:.6%} (batch {bse(IID['vol'], sd):.4%}); block {v_b:.6%} (batch {bse(SB['vol'], sd):.4%}); ratio "
    f"{v_b / v_i:.6f}; relative SE iid {v_i / VOL:.6%}, block {v_b / VOL:.6%} -> printed {pr(se_s * SQA, 2, 100)} "
    f"(LM20's), {pr(v_i, 2, 100)}, {pr(v_b, 2, 100)}; {pr(v_b / v_i, 1)}; {pr(v_i / VOL, 2, 100, '%')}, "
    f"{pr(v_b / VOL, 2, 100, '%')}")                                                                               # 24

# ================================================================ X7: three block schemes at ell = 145
MB = boot_tr(row_chunks(gen(5), T, mb_row, ELL))                      # experiment 5
CB = boot_tr(row_chunks(gen(6), T, cb_row, ELL))                      # experiment 6
segs, forms = [], []
for nm, d in (("iid e 2", IID), ("moving e 5", MB), ("circular e 6", CB), ("stationary e 3", SB)):
    fv, fk = fq(d["vol"], VOL), fq(d["Kelly"], KEL)
    segs.append(f"{nm}: vol SE {fv['se']:.6%}, percentile {fv['lo']:.6%} to {fv['hi']:.6%}; Kelly SE {fk['se']:.6f}, "
                f"percentile {fk['lo']:.6f} to {fk['hi']:.6f}; SR SE {d['SR'].std():.6f}")
    forms.append(f"{nm.split()[0]} {pr(fv['se'], 2, 100)}, {pr(fv['lo'], 1, 100)}-{pr(fv['hi'], 1, 100)}, "
                 f"{pr(fk['se'], 2)}, {pr(fk['lo'], 1)}-{pr(fk['hi'], 1)}, {pr(float(d['SR'].std()), 3)}")
put(" // ".join(segs) + " -> printed " + "; ".join(forms))                                                        # 25

# ================================================================ X6: block-length grid (experiment 4)
GRID = (2, 3, 5, 10, 20, 50, 100, 200, 400)
B4 = 2000
rng4 = gen(4)
grid = {1: IID, ELL: SB}
for ell in GRID:
    grid[ell] = boot_tr(row_chunks(rng4, T, sb_row, ell, B4))
KEYS = ("SR", "Kelly", "vol", "VR20")
ratio = {ell: {k: float(grid[ell][k].std() / IID[k].std()) for k in KEYS} for ell in sorted(grid)}
relb = {ell: {k: bse(grid[ell][k], sd) / float(grid[ell][k].std()) for k in KEYS} for ell in sorted(grid)}
rmc = {ell: {k: sqrt(relb[ell][k] ** 2 + relb[1][k] ** 2) for k in KEYS} for ell in sorted(grid) if ell != 1}
mc2 = [rmc[ell][k] for ell in GRID for k in KEYS]
mc145 = [rmc[ELL][k] for k in KEYS]
chg = {k: ratio[ELL][k] / ratio[3][k] - 1 for k in ("SR", "Kelly")}
mxk = {k: max(GRID + (ELL,), key=lambda e, k=k: ratio[e][k]) for k in ("SR", "Kelly")}
put("SE / iid SE: " + "; ".join(f"ell {ell}: " + ", ".join(f"{k} {ratio[ell][k]:.6f}" for k in KEYS)
                                for ell in sorted(grid))
    + "; iid SEs " + ", ".join(f"{k} {IID[k].std():.6g}" for k in KEYS)
    + f"; relative Monte Carlo SE of a ratio: B 2,000 lengths {min(mc2):.4%} to {max(mc2):.4%}, ell {ELL} "
    f"{min(mc145):.4%} to {max(mc145):.4%}; SE(ell {ELL}) / SE(ell 3) - 1: SR {chg['SR']:.4%}, Kelly "
    f"{chg['Kelly']:.4%}; largest ratio: SR at ell {mxk['SR']}, Kelly at ell {mxk['Kelly']} -> printed (X6, two "
    "decimals) " + "; ".join(f"ell {ell}: " + ", ".join(pr(ratio[ell][k], 2) for k in KEYS) for ell in sorted(grid))
    + f"; Monte Carlo SE of a ratio at most {pr(max(mc2), 0, 100, '%')} (B 2,000), about {pr(max(mc145), 0, 100, '%')} "
    f"(ell {ELL}); changes between 3 and {ELL}: SR {pr(chg['SR'], 0, 100, '%')}, Kelly {pr(chg['Kelly'], 0, 100, '%')}; "
    f"at most SR {pr(ratio[mxk['SR']]['SR'], 2)}, Kelly {pr(ratio[mxk['Kelly']]['Kelly'], 2)}")                 # 26

# ================================================================ X5: two resampled paths (experiment 7)
W60 = 60


def roll_vol(x: Vec) -> Vec:
    c1 = np.concatenate([[0.0], np.cumsum(x)])
    c2 = np.concatenate([[0.0], np.cumsum(x * x)])
    m1_ = (c1[W60:] - c1[:-W60]) / W60
    m2_ = (c2[W60:] - c2[:-W60]) / W60
    return np.sqrt(np.maximum(m2_ - m1_ * m1_, 0.0)) * SQA


rng7 = gen(7)
p_iid = R[rng7.integers(0, T, size=T)]
p_sb = R[sb_row(rng7, T, ELL)]
segs, forms = [], []
for nm, x in (("TR23", R), ("iid", p_iid), ("block", p_sb)):
    v = roll_vol(x)
    segs.append(f"{nm} max {v.max():.6%} (session {int(v.argmax()) + W60}), min {v.min():.6%} (session "
                f"{int(v.argmin()) + W60})")
    forms.append(f"{nm} {pr(float(v.max()), 1, 100, '%')} and {pr(float(v.min()), 1, 100, '%')}")
rv = roll_vol(R)
put("60-day volatility (divisor 60, annualized by sqrt(A)): " + "; ".join(segs) + f"; TR23 max window ends "
    f"{dates[int(rv.argmax()) + W60 - 1]}, min ends {dates[int(rv.argmin()) + W60 - 1]} -> printed "
    + "; ".join(forms))                                                                                             # 27

# ================================================================ E7: LM16's crash correlation (experiments 8, 9)
cc0, mod0, n0 = crash(PAIR)
rho0 = corr0(PAIR[:, 0], PAIR[:, 1])
pw_p = [pw((PAIR[:, j] - PAIR[:, j].mean()) ** 2) for j in (0, 1)]
ELL_P = round(max(p[0] for p in pw_p))
z0 = (PAIR[:, 0] - PAIR[:, 0].mean()) / PAIR[:, 0].std()
assert int((np.abs(z0) > 2).sum()) == n0 and not np.any(np.abs(np.abs(z0) - 2) < 1e-9)
put(f"{n0} days with abs(z) >= 2; data {cc0:.6f}; full-sample rho {rho0:.8f}; model (16.10) {mod0:.6f}; gap "
    f"{cc0 - mod0:.6f}; Var(Z given abs(Z) >= 2) {V2:.6f}; Politis-White on squares {pw_p[0][0]:.8f} (Semiconductor), "
    f"{pw_p[1][0]:.8f} (FinancialInsurance); ell {ELL_P} -> printed {n0}; {pr(cc0, 3)}; {pr(mod0, 3)}; "
    f"{pr(cc0 - mod0, 3)}; rho {pr(rho0, 4)}; {pr(V2, 4)}; {pr(pw_p[0][0], 1)} and {pr(pw_p[1][0], 1)}; ell "
    f"{ELL_P}")                                                                                                     # 28
for e, ell in ((8, 1), (9, ELL_P)):
    rng = gen(e)
    v = np.array([crash(PAIR[draws(rng, TU, ell)]) for _ in range(B)])
    gap = v[:, 0] - v[:, 1]
    assert not np.any(gap == 0)
    dc, dg = fq(v[:, 0], cc0), fq(gap, cc0 - mod0)
    n_pos = int((gap >= 0).sum())
    shown_e = (f"gap {pr(dg['lo'], 3)} to {pr(dg['hi'], 3)}" if ell == 1 else
               f"correlation SE {pr(dc['se'], 3)}, {pr(dc['lo'], 2)} to {pr(dc['hi'], 2)}; gap SE {pr(dg['se'], 3)}, "
               f"{pr(dg['lo'], 3)} to {pr(dg['hi'], 3)}")
    put(f"ell {ell} (e {e}): data corr " + summ(v[:, 0], cc0) + " // gap " + summ(gap, cc0 - mod0)
        + f"; resamples with gap >= 0: {n_pos}; event days {int(v[:, 2].min())} to {int(v[:, 2].max())} -> printed "
        + shown_e + f"; {n_pos} at or above 0; {int(v[:, 2].min())} to {int(v[:, 2].max())} days")                 # 29-30

# ================================================================ E8: LM11's PC1 share (experiments 10-13)
for y, e_iid, e_blk in (("2017", 10, 11), ("2020", 12, 13)):
    rows = np.flatnonzero(ydates == y)
    Xy = X[rows]
    ny = Xy.shape[0]
    est = pc1_share(Xy)
    pws = [pw((Xy[:, j] - Xy[:, j].mean()) ** 2)[0] for j in range(Xy.shape[1])]
    ell_y = round(max(pws))
    out, vals = [], {}
    for e, ell in ((e_iid, 1), (e_blk, ell_y)):
        rng = gen(e)
        v = np.array([pc1_share(Xy[draws(rng, ny, ell)]) for _ in range(B)])
        vals[ell] = v
        out.append(f"ell {ell} (e {e}): " + summ(v, est) + f"; bias {v.mean() - est:+.6f}")
    di, db = fq(vals[1], est), fq(vals[ell_y], est)
    if y == "2020":
        KEEP.update(est20=est, lo20=db["lo"], hi20=db["hi"], se20=db["se"])
    shown_y = (f"{ny}; {pr(est, 1, 100, '%')}" + (f" ({pr(est, 2, 100, '%')})" if y == "2020" else "")
               + f"; Politis-White max {pr(max(pws), 2)}, ell {ell_y}; iid {pr(di['lo'], 1, 100, '%')} to "
               f"{pr(di['hi'], 1, 100, '%')}; blocks SE {pr(db['se'], 1, 100)}, {pr(db['lo'], 1, 100, '%')} to "
               f"{pr(db['hi'], 1, 100, '%')}")
    if y == "2020":
        shown_y += (f", basic {pr(db['blo'], 1, 100, '%')} to {pr(db['bhi'], 1, 100, '%')}, mean "
                    f"{pr(db['mean'], 1, 100, '%')}, bias {pr(db['mean'] - est, 1, 100)}")
    put(f"{y}: {ny} returns {U.dates[int(rows[0])]} to {U.dates[int(rows[-1])]}; share {est:.6f}; Politis-White max "
        f"over the 28 sectors {max(pws):.6f}; ell {ell_y}; " + " // ".join(out) + " -> printed " + shown_y)     # 31-32

# ================================================================ E9: LM18's windows (experiments 14, 15)
M5 = round(5 * A)


def windows(x: Vec) -> tuple[float, float]:
    c = np.concatenate([[0.0], np.cumsum(x)])
    lg = c[M5:] - c[:-M5]
    return float((lg < 0).mean()), float(lg.std())


trf = [Fraction(str(x)) for x in tr]
under_exact = sum(trf[i + M5] < trf[i] for i in range(len(trf) - M5))
sh0, sd0 = windows(r)
assert under_exact == round(sh0 * (T - M5 + 1))
put(f"m {M5}; windows {T - M5 + 1}; under water {under_exact} (Fraction) = {sh0:.6%}; sd ln G (divisor = windows) "
    f"{sd0:.6f}; sqrt(m) s_r {sqrt(M5) * sr_:.6f} -> printed {under_exact} of {T - M5 + 1}; {pr(sh0, 1, 100, '%')}; "
    f"{pr(sd0, 3)}; {pr(sqrt(M5) * sr_, 3)}")                                                                      # 33
for e, ell in ((14, ELL), (15, 1)):
    rng = gen(e)
    v = np.array([windows(r[draws(rng, T, ell)]) for _ in range(B)])
    ds, dd = fq(v[:, 0], sh0), fq(v[:, 1], sd0)
    nz = int((v[:, 0] == 0).sum())
    shown_w = (f"share SE {pr(ds['se'], 1, 100)}, {pr(ds['lo'], 1, 100, '%')} to {pr(ds['hi'], 1, 100, '%')}, basic "
               f"{pr(ds['blo'], 1, 100, '%')} to {pr(ds['bhi'], 1, 100, '%')}, {nz} with none; sd SE {pr(dd['se'], 3)}, "
               f"{pr(dd['lo'], 2)} to {pr(dd['hi'], 2)}, mean {pr(dd['mean'], 3)}" if ell > 1 else
               f"share SE {pr(ds['se'], 1, 100)}; sd {pr(dd['lo'], 2)} to {pr(dd['hi'], 2)}")
    put(f"ell {ell} (e {e}): share " + summ(v[:, 0], sh0) + f"; resamples with no window under water {nz} of {B} // "
        "sd ln G " + summ(v[:, 1], sd0) + " -> printed " + shown_w)                                               # 34-35

# ================================================================ E10: bootstrap tests of the mean (experiments 16-18)
for lab, x, plan in (("7% regime", R[pre], ((16, 1), (17, None))), ("full sample", R, ((18, None),))):
    n = x.size
    t0 = float(tstat(x[None, :])[0])
    x0 = x - x.mean()
    ell_t = round(pw(x0**2)[0])
    p_n = 2 * float(stats.norm.sf(abs(t0)))
    seg = (f"{lab}: n {n}; Rbar {x.mean():.6%}; s_u {x.std(ddof=1):.6%}; t-stat {t0:.6f}; two-sided normal p "
           f"{p_n:.8f} (LM21's reference); Politis-White ell {ell_t}")
    shown_t = [f"t-stat {pr(t0, 2)}", f"normal p {pr(p_n, 3)}" if p_n > 0.001 else
               f"normal p {pr(p_n * 1e5, 1)}e-5"]
    for e, ell0 in plan:
        ell = ell_t if ell0 is None else ell0
        rng = gen(e)
        tb = np.concatenate([tstat(x0[idx]) for idx in (iid_chunks(rng, n) if ell == 1
                                                         else row_chunks(rng, n, sb_row, ell))])
        assert not np.any(np.abs(tb) == abs(t0))
        k = int((np.abs(tb) >= abs(t0)).sum())
        p = k / B
        mcse = sqrt(p * (1 - p) / B)
        if e == 17:
            KEEP["k17"] = k
        seg += (f"; ell {ell} (e {e}): {k} of {B} with abs(t) >= abs(t-stat), p {p:.4f} (MC SE {mcse:.6f}); sd of t "
                f"(divisor B) {tb.std():.6f}; 95% point of abs(t) "
                f"{float(np.quantile(np.abs(tb), 0.95, method='inverted_cdf')):.4f}")
        shown_t.append(f"ell {ell}: {k}, {pr(p, 3)} ± {pr(mcse, 3)}, sd {pr(float(tb.std()), 2)}" if k > 0 else
                       f"ell {ell}: {k} of {B}, below 1/B = {1 / B:.4f}")
    put(seg + " -> printed " + "; ".join(shown_t))                                                                 # 36-37

# ================================================================ knowledge checks
rel_se = 1 / (SR * sqrt(T))
put(f"1/(SR sqrt T) {rel_se:.6f}; SE(Rbar)/Rbar {(s / sqrt(T)) / Rb:.6f}; LM4's 0.0230/0.0871 = {0.0230 / 0.0871:.5f} "
    f"(printed 26%, lm04.md:547) -> printed {pr(rel_se, 1, 100, '%')} and {pr(rel_se, 0, 100, '%')}; LM4 "
    f"{pr(0.0230 / 0.0871, 0, 100, '%')}")                                                                         # 38
nb = ceil(T / ELL)
put(f"moving blocks: ceil({T}/{ELL}) = {nb}; {nb} x {ELL} = {nb * ELL}; cut {nb * ELL - T}")                        # 39
yrs = sorted({y for y in ydates if y >= "2009"})
put(f"LM11's calendar years {yrs[0]}-{yrs[-1]}: {len(yrs)}; December 2008 returns {int((ydates == '2008').sum())}")  # 40
rng19 = gen(19)
tb_u = np.concatenate([tstat(R[idx]) for idx in iid_chunks(rng19, T)])
t_full = float(tstat(R[None, :])[0])
sh_u = float((tb_u >= t_full).mean())
put(f"uncentred iid resamples (e 19): mean t {tb_u.mean():.6f}, sd (divisor B) {tb_u.std():.6f}; share with t >= "
    f"t-stat {sh_u:.4f} -> printed mean {pr(float(tb_u.mean()), 2)}, share {pr(sh_u, 1)}")                       # 41
same = []
for cls, fn in ((StationaryBootstrap, sb_row), (CircularBlockBootstrap, cb_row), (MovingBlockBootstrap, mb_row)):
    g1, g2 = gen(20), gen(20)                                         # experiment 20: two copies of one stream
    bs = cls(ELL, R, seed=g1)
    ok = True
    for _ in bs.bootstrap(3):
        ok &= bool(np.array_equal(cast(Idx, bs.index), fn(g2, T, ELL)))
    same.append(f"{cls.__name__} {ok}")
put("e 20: arch draws the same indices as the NumPy functions, three resamples each: " + ", ".join(same))          # 42

# ================================================================ problems
three = np.array([0.01, -0.02, 0.04])
res3 = three[np.array(list(product(range(3), repeat=3)))].mean(axis=1)
s3, su3 = float(three.std()), float(three.std(ddof=1))
put(f"P1: three returns s {s3:.6%}; s/sqrt(3) {s3 / sqrt(3):.6%}; ideal SE (27 resamples) {res3.std():.6%}; "
    f"s_u/sqrt(3) {su3 / sqrt(3):.6%}; s/3 {s3 / 3:.6%} -> printed {pr(s3 / sqrt(3), 3, 100, '%')}, "
    f"{pr(su3 / sqrt(3), 3, 100, '%')}, {pr(s3 / 3, 3, 100, '%')}")                                                # 43
put(f"P2: B {B}: ranks ceil(0.025 B) {ceil(0.025 * B)}, ceil(0.975 B) {ceil(0.975 * B)}; a 90% interval "
    f"{ceil(0.05 * B)}, {ceil(0.95 * B)}")                                                                          # 44
E20, L20, H20, S20 = (100 * KEEP[k] for k in ("est20", "lo20", "hi20", "se20"))
st_e, st_l, st_h, st_s = (float(f"{x:.2f}") for x in (E20, L20, H20, S20))   # the stem's two-decimal inputs
put(f"P3: unrounded (A22-32) {E20:.6f}%, {L20:.6f}% to {H20:.6f}%, SE {S20:.6f} points; from the stem's inputs: basic "
    f"{2 * st_e - st_h:.4f}% to {2 * st_e - st_l:.4f}%, normal {st_e - 1.96 * st_s:.4f}% to {st_e + 1.96 * st_s:.4f}%; "
    f"from the unrounded values: basic {2 * E20 - H20:.4f}% to {2 * E20 - L20:.4f}%, normal {E20 - 1.96 * S20:.4f}% to "
    f"{E20 + 1.96 * S20:.4f}% -> printed stem {pr(E20, 2, 1, '%')}, {pr(L20, 2, 1, '%')} to {pr(H20, 2, 1, '%')}, "
    f"SE {pr(S20, 2)}; basic {pr(2 * st_e - st_h, 1, 1, '%')} to {pr(2 * st_e - st_l, 1, 1, '%')}; normal "
    f"{pr(st_e - 1.96 * st_s, 1, 1, '%')} to {pr(st_e + 1.96 * st_s, 1, 1, '%')}")                                 # 45
assert (f"{2 * st_e - st_h:.1f}", f"{st_e + 1.96 * st_s:.1f}") == (f"{2 * E20 - H20:.1f}", f"{E20 + 1.96 * S20:.1f}")
put(f"P5: 1/{ELL} {1 / ELL:.6f}; 1 - 1/{ELL} {1 - 1 / ELL:.6f}; {ELL}/{T} {ELL / T:.6f} -> printed {pr(1 / ELL, 4)}, "
    f"{pr(1 - 1 / ELL, 4)}, {pr(ELL / T, 4)}")                                                                      # 46
keep145 = (1 - 1 / ELL) + (1 / ELL) / T
keep2 = 0.5 + 0.5 / T
b21 = boot_tr(row_chunks(gen(21), T, sb_row, 2, 2000))
m21 = float(b21["acf"].mean())
bs21 = bse(b21["acf"], lambda c: float(c.mean()))
m3 = float(SB["acf"].mean())
put(f"P6: blocks expected 1 + {T - 1}/{ELL} = {1 + (T - 1) / ELL:.6f}; Pr(block of 60 days or more) (1 - 1/{ELL})^59 = "
    f"{(1 - 1 / ELL) ** 59:.6f}; adjacent pairs kept ell {ELL} {keep145:.6f}, ell 2 {keep2:.6f}; predicted mean acf "
    f"abs(r) {keep145 * OBS['acf']:.6f}, {keep2 * OBS['acf']:.6f}; e 21 (ell 2, B 2,000) mean {m21:.6f} (batch "
    f"{bs21:.6f}); e 3 (ell {ELL}) mean {m3:.6f} -> printed {pr(1 + (T - 1) / ELL, 1)}; {pr((1 - 1 / ELL) ** 59, 3)}; "
    f"about {pr(keep145 * OBS['acf'], 2)} and {pr(keep2 * OBS['acf'], 3)}; {pr(m21, 3)}, batch SE {pr(bs21, 4)}; "
    f"{pr(m3, 3)}")                                                                                                 # 47
p7 = KEEP["k17"] / B
se7 = sqrt(p7 * (1 - p7) / B)
put(f"P7: {int(KEEP['k17'])} of {B} (A22-36, e 17): p {p7:.4f}; MC SE {se7:.6f}; p + 2 SE {p7 + 2 * se7:.6f}; B for "
    f"MC SE 0.001: {p7 * (1 - p7) / 1e-6:.1f} -> printed {pr(p7, 4)} ± {pr(se7, 4)}; {pr(p7 + 2 * se7, 3)}; about "
    f"{pr(p7 * (1 - p7) / 1e-6 / 1000, 0)},000")                                                                   # 48
cnt = np.array([min(t, ELL, T - ELL + 1, T - t + 1) for t in range(1, T + 1)])
emb = float((cnt * R).sum() / cnt.sum())
put(f"P9: moving blocks of {ELL}: day 1 in {cnt[0]} of the {T - ELL + 1} blocks, day {ELL} in {cnt[ELL - 1]}; "
    f"E[mean] {emb:.8%} against Rbar {Rb:.8%}: {1e4 * (emb - Rb):.6f} bp ({emb / Rb - 1:+.6%}) -> printed "
    f"{cnt[0]} and {cnt[ELL - 1]}; {pr(emb, 6, 100, '%')} against {pr(Rb, 6, 100, '%')}; {pr(1e4 * (emb - Rb), 2)} bp; "
    f"{pr(emb / Rb - 1, 1, 100, '%')}")                                                                            # 49
R10 = R[~pre]
k10 = float(R10.mean() / R10.var())
ell10 = round(pw((R10 - R10.mean()) ** 2)[0])
v22 = np.concatenate([kel_vec(R10[idx]) for idx in iid_chunks(gen(22), R10.size)])
v23 = np.concatenate([kel_vec(R10[idx]) for idx in row_chunks(gen(23), R10.size, sb_row, ell10)])
put(f"P11: 10% regime {R10.size} returns; f_hat {k10:.6f}; Politis-White ell {ell10}; iid (e 22) " + summ(v22, k10)
    + " // block (e 23) " + summ(v23, k10) + f" -> printed {pr(k10, 2)}; ell {ell10}; iid "
    + ivp(fq(v22, k10), 1) + "; blocks " + ivp(fq(v23, k10), 1))                                                   # 50

print("\n".join(OUT))
