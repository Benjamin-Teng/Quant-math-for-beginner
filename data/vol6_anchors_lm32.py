"""LM32 anchors (VaR, Expected Shortfall and Drawdown): every number the Stage 1 brief quotes (drafted 2026-10-24;
revised the same day to the editor's decisions on the briefs, plans/vol-5.md).

Reads only checked, git-ignored outputs and the raw files the plan names (run their builders first):
  * TR23 (Volume III) and LM26's out-of-sample forecasts: data/lm26_common.py, which reads
    data/processed/vol3_taiex.parquet (data/vol3_series.py; FinMind TaiwanStockTotalReturnIndex, TAIEX, retrieved
    2026-10-18) and, at import, the committed per-day file data/derived/vol4_rv.csv. T = 5,849 simple daily returns
    R_t, 2003-01-03 .. 2026-10-08, years = calendar days / 365.25, A = 246.12; y = 100 ln(1 + R) for the EWMA and
    GARCH models. forecasts() gives LM26's six forecasts: window round(5A) = 1,231 returns, GARCH(1,1) normal and t
    refitted at each month's first session (226 refits), EWMA 0.94 with zero mean, forecast days 2008-01-02 ..
    2026-10-08 (n = 4,609).
  * E5 and the through case (Volume V): data/vol5_series.py's frames("E5") (data/processed/vol5_frames.parquet) and
    data/vol5_rules.py's signals() and wealth_path(), recomputed here and asserted equal to the stored
    data/processed/vol5_rules.parquet. A rule's daily return is its net wealth ratio from the session after the first
    trade (2019-03-05 .. 2026-10-08, 1,851 sessions of the wealth frame); its drawdown path starts at the cash of 1
    before the first purchase, as summary() does.
  * T5S (Volume IV): three raw files data/raw/intraday/taiex5s/<year>/<date>.csv (TaiwanVariousIndicators5Seconds,
    TAIEX price index; 09:00:00 is the previous close), for the lab's per-day intraday drawdowns.

Conventions (the brief's "Data role").
  * VaR_u and ES_u are positive for a loss; u is the tail probability ("99% VaR" is u = 0.01). Historical VaR is
    -R_(j), j = ceil(u T), LM14's F_hat^-1(u) (np.quantile method="inverted_cdf"). Historical ES is Acerbi and Tasche's
    tail mean applied to F_hat, (32.2): -(1/u) [ (1/T) sum_{i<j} R_(i) + R_(j) (u - (j - 1)/T) ]; the mean of the j
    worst returns is printed beside it where the brief compares them.
  * Normal: VaR = -(mean + s Phi^-1(u)), ES = -mean + s phi(Phi^-1(u))/u, mean and s (divisor T) of the sample.
    Student t: scipy.stats.t.fit (maximum likelihood, location and scale) on returns in percent; for Y ~ t_nu with
    q = F_Y^-1(u): VaR = -(loc + scale q), ES = -loc + scale (nu + q^2) f_Y(q) / ((nu - 1) u).
  * Filtered VaR (quantile equivariance): r = ln(1 + R) in percent has quantile g + sigma z_u, so VaR = 1 -
    exp((g + sigma z_u)/100); EWMA has g = 0 and z_u = Phi^-1(u); GARCH uses the refit's constant mean, z_u =
    Phi^-1(u) (normal) or sqrt((nu - 2)/nu) F_Y^-1(u) (t, scaled to variance 1 as (15.11)).
  * Backtest: six models on TR23, u = 0.01, forecast for day t from data through day t - 1. HS and N use the
    trailing 1,231 simple returns every day; t refits on them at each month's first session (LM26's schedule);
    EWMA and GARCH as LM26. An exceedance is R_t < -VaR - 1e-12 (the guard; the smallest margin is printed).
    Coverage: one-sided upper exact binomial tail Pr(X >= x), X ~ Bin(n, u). Independence (LM21's exact form):
    of the exceedance days that have a next forecast day, how many are followed by another; null law
    Bin(trials, x/n), one-sided upper tail. Basel zones (BCBS 1996): yellow from the smallest count with
    Pr(X <= count) >= 0.95, red from the smallest with >= 0.9999.
  * Filtered ES (A32-54): ES_u of R = e^r - 1 under the day's model, (32.1): 1 - E[e^r 1{r <= q_u}] / u, in closed
    form for a normal log return (e^(g + s^2/2) Phi(Phi^-1(u) - s), checked by quadrature) and by quadrature for the
    scaled t.
  * Drawdowns: DD_t = 1 - W_t / max(W_0..W_t) with W_0 = 1 (LM1); MDD = max DD_t; DD0_t = max(0, 1 - W_t/W_0); a
    spell under water runs from a peak to the first session with W at or above that peak; durations in sessions.
    Resampled MDDs: medians and 5-95% points by inverted_cdf; a block bootstrap reproduces a short episode that fits
    in one block exactly, so its MDDs have atoms: the largest is printed with its count and the realized
    peak -> trough it equals, and a median that sits on an atom (over 1% of the resamples) gets no batch SE; the
    resamples equal to the realized MDD are counted too.
  * Stationary bootstrap (shared decision "Counting, simulation"): each resample is drawn as LM22's stationary_idx
    (lm22.md:365-383): integers then random, a new block where the uniform is <= 1/ell; it equals arch's
    StationaryBootstrap on twin generators (asserted). Resamples are drawn one after another; batches are
    consecutive.
  * Seeds (one generator per experiment, created once): 1 Monte Carlo 10-day GARCH-t VaR (100,000 paths); 2
    importance sampling (Problem 10, 10,000 draws); 3 permutations of each rule's returns (10,000 per rule, rules in
    order); 4 stationary bootstrap of each rule's returns (10,000 per rule, the book's block rule, LM22); 5 and 6 iid
    and stationary bootstrap of TR23's 1% quantile (10,000 each); 7 ten-session compound returns of iid draws from
    TR23's returns (100,000). Batch standard errors use 20 consecutive batches (divisor 20).
  * T5S: every change is a log change from the 09:00:00 value (the previous close), as the shared decisions write
    them; the intraday fall is the largest log fall from the running peak, the previous close included.
  * Owners (shared decision): the rules' losses on 2025-04-07 are LM35's (A35-13) and the first purchase's cost is
    LM27's (A27-23, echoed); neither is computed here as LM32's number.
  * Counts against a threshold use the guard (<= x + 1e-12); the TR23 minimum is checked with Fraction on the
    two-decimal index values.
Numbers printed by earlier modules are echoed with file:line.

Rounding flags. Every number the brief prints passes through f(x, k1, k2, ...), which shows x with max(k) + 3 decimals
and flags it "NEAR" for each printed precision k at which x lies within a tenth of a last-digit unit of a rounding
boundary (|frac(10^k |x|) - 0.5| < 0.1); g(x, sig) does the same for significant figures in scientific notation.
The brief prints a flagged value as rounded from the unrounded value here.

Prints one line per anchor, "A32-NN <value>", in ID order, and writes nothing.

Run:  PYTHONUTF8=1 uv run python data/vol6_anchors_lm32.py
"""
from dataclasses import dataclass
from datetime import date
from fractions import Fraction
from itertools import pairwise
from math import ceil, exp, floor, log10, pi, sqrt
from pathlib import Path

import cvxpy as cp
import lm26_common as C
import numpy as np
import polars as pl
from arch.bootstrap import StationaryBootstrap, optimal_block_length
from numpy.typing import NDArray
from scipy import integrate, stats
from vol5_rules import RULES, WINDOW, cov0, minvar, schedule, signals, wealth_path
from vol5_series import frames

HERE = Path(__file__).resolve().parent
PROC = HERE / "processed"
RAW5 = HERE / "raw" / "intraday" / "taiex5s"
EPS = 1e-12
SEED = 20261011
Vec = NDArray[np.float64]

OUT: list[str] = []
NEAR: list[str] = []


def put(value: str) -> None:
    """One anchor line; values that f() found near a rounding boundary are listed at its end."""
    tail = f" [NEAR a rounding boundary: {'; '.join(NEAR)}]" if NEAR else ""
    OUT.append(f"A32-{len(OUT) + 1:02d} {value}{tail}")
    NEAR.clear()


def f(x: float, *ks: int, plus: bool = False) -> str:
    """x with max(ks) + 3 decimals; flagged for each printed precision k within 0.1 of a last-digit unit of a boundary."""
    x = float(x)
    for k in ks:
        v = abs(x) * 10**k
        if abs(v - floor(v) - 0.5) < 0.1:
            NEAR.append(f"{x:.{k + 3}f} at {k} dp")
    return f"{x:{'+' if plus else ''}.{max(ks) + 3}f}"


def g(x: float, sig: int) -> str:
    """x in scientific notation with sig significant digits (p-values, tiny probabilities); flagged as f() does when
    its mantissa lies within a tenth of a last-digit unit of a rounding boundary."""
    x = float(x)
    if x != 0:
        v = abs(x) / 10 ** floor(log10(abs(x))) * 10 ** (sig - 1)
        if abs(v - floor(v) - 0.5) < 0.1:
            NEAR.append(f"{x:.{sig + 2}e} at {sig} sf")
    return f"{x:.{sig - 1}e}"


def jrank(u: float, n: int) -> int:
    return ceil(u * n - EPS)


def var_h(x: Vec, u: float) -> float:
    """Historical VaR: -F_hat^-1(u) (LM14's quantile function)."""
    q = float(np.quantile(x, u, method="inverted_cdf"))
    xs = np.sort(x)
    assert q == float(xs[jrank(u, len(x)) - 1])
    return -q


def es_h(x: Vec, u: float) -> float:
    """Historical ES, (32.2): Acerbi and Tasche's tail mean applied to F_hat."""
    xs = np.sort(x)
    n = len(xs)
    j = jrank(u, n)
    return -(float(xs[: j - 1].sum()) / n + float(xs[j - 1]) * (u - (j - 1) / n)) / u


def es_k(x: Vec, u: float) -> float:
    """The mean of the ceil(uT) worst returns (the other candidate of the shared decision)."""
    xs = np.sort(x)
    return -float(xs[: jrank(u, len(xs))].mean())


def var_n(mu: float, s: float, u: float) -> float:
    return -(mu + s * float(stats.norm.ppf(u)))


def es_n(mu: float, s: float, u: float) -> float:
    return -mu + s * float(stats.norm.pdf(stats.norm.ppf(u))) / u


def var_t(nu: float, loc: float, sc: float, u: float) -> float:
    return -(loc + sc * float(stats.t.ppf(u, nu)))


def es_t(nu: float, loc: float, sc: float, u: float) -> float:
    q = float(stats.t.ppf(u, nu))
    return -loc + sc * (nu + q * q) * float(stats.t.pdf(q, nu)) / ((nu - 1) * u)


def path_of(w: Vec) -> Vec:
    return np.concatenate([[1.0], w])


def dd_of(path: Vec) -> Vec:
    return 1 - path / np.maximum.accumulate(path)


def mdd_rows(G: NDArray[np.float64], w0: float) -> Vec:
    """MDD of each row's path 1, w0, w0 (1 + G_1), ... (the first purchase's cost as in the realized path)."""
    Wp = w0 * np.cumprod(1 + G, axis=1)
    Wp = np.concatenate([np.ones((G.shape[0], 1)), np.full((G.shape[0], 1), w0), Wp], axis=1)
    return (1 - Wp / np.maximum.accumulate(Wp, axis=1)).max(axis=1)


def stationary_idx(rng: np.random.Generator, n: int, ell: int) -> NDArray[np.int64]:
    """Day indices of one stationary resample (22.3), drawn as LM22's stationary_idx (lm22.md:365-383) and
    data/lm22_common.py's sb_row do, in arch's order: n candidate start days, then n uniforms; a block starts where the
    uniform is <= 1/ell (and at the first position); day n is followed by day 1."""
    start = rng.integers(n, size=n, dtype=np.int64)
    new = rng.random(n) <= 1.0 / ell
    new[0] = True
    first_ = np.flatnonzero(new)
    blk = np.cumsum(new) - 1
    return (start[first_][blk] + np.arange(n) - first_[blk]) % n


def stat_idx(rng: np.random.Generator, n: int, ell: int, B: int) -> NDArray[np.int64]:
    """B consecutive stationary resamples, one row each, in LM22's draw order (one resample after another)."""
    return np.stack([stationary_idx(rng, n, ell) for _ in range(B)])


def book_ell(x: Vec) -> int:
    """LM22's book's rule: the stationary Politis-White estimate on the squared demeaned series, rounded."""
    ob = optimal_block_length((x - x.mean()) ** 2)
    assert list(ob.columns) == ["stationary", "circular"]
    return round(float(ob.to_numpy()[0][0]))


def batch_se(v: Vec) -> float:
    b = np.array([float(np.mean(c)) for c in np.split(v, 20)])
    return float(b.std() / sqrt(20))


def batch_se_q(v: Vec, u: float) -> float:
    b = np.array([float(np.quantile(c, u, method="inverted_cdf")) for c in np.split(v, 20)])
    return float(b.std() / sqrt(20))


def batch_se_sd(v: Vec) -> float:
    """Batch standard error of a standard deviation (20 batches, divisor 20), as batch_se_q."""
    b = np.array([float(c.std()) for c in np.split(v, 20)])
    return float(b.std() / sqrt(20))


def binom_interval(n: int, u: float, level: float = 0.95) -> tuple[int, int, float]:
    """(j1, j2, coverage): Pr(R_(j1) <= F^-1(u) < R_(j2)) = Pr(j1 <= X <= j2 - 1), X ~ Bin(n, u), (32.5);
    j1 the largest rank with Pr(X <= j1 - 1) <= (1 - level)/2, j2 the smallest with Pr(X <= j2 - 1) >= (1 + level)/2.
    j1 = 0 means no lower order statistic (the interval is unbounded below)."""
    a = (1 - level) / 2
    j1 = 0
    while stats.binom.cdf(j1, n, u) <= a:     # Pr(X <= j1) <= a, so rank j1 + 1 still qualifies
        j1 += 1
    j2 = 1
    while stats.binom.cdf(j2 - 1, n, u) < 1 - a:
        j2 += 1
    lo = float(stats.binom.cdf(j1 - 1, n, u)) if j1 >= 1 else 0.0
    return j1, j2, float(stats.binom.cdf(j2 - 1, n, u)) - lo


# ================================================================ data
R, T, A, dates = C.R, C.T, C.A, C.dates
y = C.y
pos = C.pos
assert T == 5849
put(f"TR23: {T} simple daily returns {dates[0]} -> {dates[-1]}; years {f(C.years, 4)}; A {f(A, 2)} "
    f"(echo lm19.md:46)")                                                                 # 01
tr = pl.read_parquet(PROC / "vol3_taiex.parquet").sort("date")["tr"].to_list()
fr_ret = [Fraction(f"{b:.2f}") / Fraction(f"{a:.2f}") - 1 for a, b in pairwise(tr)]
i7 = pos["2025-04-07"]
assert min(range(T), key=lambda i: fr_ret[i]) == i7 == int(np.argmin(R))
d_prev = dates[i7 - 1]
gap_days = (date.fromisoformat(dates[i7]) - date.fromisoformat(d_prev)).days
put(f"2025-04-07: R {f(100 * R[i7], 2, 4)}%, the exact minimum of {T} (Fraction on the closes); log return "
    f"{f(100 * float(np.log1p(R[i7])), 2, 4)}%; previous session {d_prev}, {gap_days} calendar days, so "
    f"{gap_days - 1} days without a session (3-6 April)")                                               # 02

fr = frames("E5")
log_: list[str] = []
sigs = signals(fr, log_)
paths = {k: wealth_path(fr, sigs, k) for k in RULES}
stored = pl.read_parquet(PROC / "vol5_rules.parquet")
for k, p in paths.items():
    s_w = stored.filter(pl.col("rule") == k).sort("date")
    assert s_w["date"].to_list() == p.dates and np.allclose(s_w["wealth"].to_numpy(), p.wealth, rtol=0, atol=1e-12)
    assert p.ruin is None
ret = {k: p.wealth[1:] / p.wealth[:-1] - 1 for k, p in paths.items()}
rdates = paths["R1"].dates[1:]
nR = len(rdates)
yrs_r = (date.fromisoformat(rdates[-1]) - date.fromisoformat(paths["R1"].dates[0])).days / 365.25
put(f"E5 wealth frame {len(fr.wealth_dates)} sessions, A_w {f(fr.A_wealth, 2)}; {len(sigs)} signals, first trade "
    f"{sigs[0].trade}, last {sigs[-1].trade}; rules' returns: {nR} sessions {rdates[0]} -> {rdates[-1]} "
    f"({f(yrs_r, 2)} years from the first trade); stored vol5_rules.parquet reproduced to 1e-12")       # 03

F = C.forecasts()
first, oos, FC, refits, W_ = F["first"], F["oos"], F["FC"], F["refits"], F["W"]
n_bt = len(oos)
U = 0.01
put(f"backtest: window {W_} returns (round(5A)); forecast days {dates[first]} -> {dates[-1]}, n {n_bt}; "
    f"{len(refits['t'])} monthly GARCH refits per law (LM26); u {U}, expected exceedances {f(n_bt * U, 2)}")  # 04

# ================================================================ forecasts of the six models
mu_n, mu_t, nu_t = (np.full(T, np.nan) for _ in range(3))
for dist, lst in refits.items():
    for k, (d, p) in enumerate(lst):
        s0 = pos[d]
        e0 = pos[lst[k + 1][0]] if k + 1 < len(lst) else T
        if dist == "normal":
            mu_n[s0:e0] = p[0]
        else:
            mu_t[s0:e0] = p[0]
            nu_t[s0:e0] = p[4]
tday = np.full((T, 3), np.nan)
mstarts = [s for s in C.starts if s >= first]
for k, s0 in enumerate(mstarts):
    e0 = mstarts[k + 1] if k + 1 < len(mstarts) else T
    nu_, loc_, sc_ = stats.t.fit(100 * R[s0 - W_:s0])
    tday[s0:e0] = (nu_, loc_, sc_)
MODELS = ["HS", "N", "t", "EWMA", "GARCH-n", "GARCH-t"]
z01 = float(stats.norm.ppf(U))


def var_day(model: str, tt: int, u: float) -> float:
    win = R[tt - W_:tt]
    if model == "HS":
        return var_h(win, u)
    if model == "N":
        return var_n(float(win.mean()), float(win.std(ddof=0)), u)
    if model == "t":
        a, b, c = tday[tt]
        return var_t(float(a), float(b), float(c), u) / 100
    if model == "EWMA":
        return 1 - exp(sqrt(float(FC["ewma"][tt])) * float(stats.norm.ppf(u)) / 100)
    if model == "GARCH-n":
        return 1 - exp((float(mu_n[tt]) + sqrt(float(FC["garch_n"][tt])) * float(stats.norm.ppf(u))) / 100)
    nv = float(nu_t[tt])
    zt = float(stats.t.ppf(u, nv)) * sqrt((nv - 2) / nv)
    return 1 - exp((float(mu_t[tt]) + sqrt(float(FC["garch_t"][tt])) * zt) / 100)


VAR = {m: np.array([var_day(m, int(tt), U) for tt in oos]) for m in MODELS}
Ro = R[oos]
k7 = list(oos).index(i7)

# ================================================================ case
s7 = max(s for s in mstarts if s <= i7)            # the t model's refit for 7 April: the month's first session
assert dates[s7] == "2025-04-01" and dates[i7 - W_] > dates[s7 - W_]
put("2 April 2025 -> 7 April 99% VaR forecasts (%): " + "; ".join(f"{m} {f(100 * VAR[m][k7], 2, 3)}" for m in MODELS)
    + f"; loss {f(-100 * R[i7], 2)}%; loss / VaR " + "; ".join(f"{m} {f(-R[i7] / VAR[m][k7], 1, 2)}" for m in MODELS)
    + f"; range {f(100 * min(VAR[m][k7] for m in MODELS), 2)} to {f(100 * max(VAR[m][k7] for m in MODELS), 2)}"
    + f" (HS and N: the {W_} returns {dates[i7 - W_]} -> {dates[i7 - 1]}; t: the fit of {dates[s7]} on the {W_} "
      f"returns {dates[s7 - W_]} -> {dates[s7 - 1]})")                                                     # 05
worst = {k: rdates[int(np.argmin(ret[k]))] for k in RULES}
put("each rule's worst day over its " + str(nR) + " returns: " + "; ".join(f"{k} {worst[k]}" for k in RULES)
    + " (the rules' losses on 2025-04-07 are LM35's, A35-13)")                                          # 06
U2 = 0.025
put("rules' historical VaR / ES at 1% and ES at 2.5% (%; j = "
    f"{jrank(U, nR)}, {jrank(U2, nR)} of {nR}): "
    + "; ".join(f"{k} {f(100 * var_h(ret[k], U), 2, 3)} / {f(100 * es_h(ret[k], U), 2)} / "
                f"{f(100 * es_h(ret[k], U2), 2)}" for k in RULES))                                       # 07


@dataclass
class Spell:
    mdd: float
    peak: str
    trough: str
    rec: str | None
    n_pt: int
    n_tr: int | None
    long: int
    long_peak: str
    long_end: str
    dd0: float
    dd0_date: str
    end_dd: float
    end_peak: str


def spells(path: Vec, dts: list[str]) -> Spell:
    """MDD episode (peak, trough, recovery) and the longest spell under water; dts labels path[1:]."""
    lab = ["start", *dts]
    dd = dd_of(path)
    it = int(np.argmax(dd))
    ip = int(np.argmax(path[: it + 1]))
    rec = next((j for j in range(it, len(path)) if path[j] >= path[ip] - EPS), None)
    pk = np.maximum.accumulate(path)
    under = path < pk - EPS
    best, cur, best_end = 0, 0, 0
    for j, uw in enumerate(under):
        cur = cur + 1 if uw else 0
        if cur > best:
            best, best_end = cur, j
    b0 = best_end - best + 1            # first session under water; its peak is the session before
    rec_long = best_end + 1 if best_end + 1 < len(path) else None
    j0 = int(np.argmax(1 - path))
    return Spell(float(dd[it]), lab[ip], lab[it], lab[rec] if rec is not None else None, it - ip,
                 (rec - it) if rec is not None else None, best, lab[b0 - 1],
                 lab[rec_long] if rec_long is not None else "open", max(0.0, float(1 - path.min())), lab[j0],
                 float(dd[-1]), lab[int(np.argmax(path))])


SP = {k: spells(path_of(p.wealth), p.dates) for k, p in paths.items()}
sp1 = SP["R1"]
put(f"R1: MDD {f(100 * sp1.mdd, 2)}% (peak {sp1.peak}, trough {sp1.trough}, back at the peak "
    f"{sp1.rec}; {sp1.n_pt} sessions down, {sp1.n_tr} back up); longest spell under water {sp1.long} "
    f"sessions (peak {sp1.long_peak}, back {sp1.long_end}); max DD0 {f(100 * sp1.dd0, 2)}% on "
    f"{sp1.dd0_date}; at 2026-10-08 {f(100 * sp1.end_dd, 2)}% under the peak of {sp1.end_peak}")  # 08
c20 = {k: np.concatenate([[0.0], np.cumsum(np.log1p(ret[k]))]) for k in RULES}
R20 = {k: np.expm1(c20[k][20:] - c20[k][:-20]) for k in RULES}
put(f"R1 20-session compound returns: {len(R20['R1'])} overlapping windows; 99% VaR {f(100 * var_h(R20['R1'], U), 2)}% "
    f"(j = {jrank(U, len(R20['R1']))}); sqrt(20) x one-day VaR {f(100 * sqrt(20) * var_h(ret['R1'], U), 2)}%")  # 09

# ================================================================ section 2: definitions and historical estimators
x5 = np.array([0.012, -0.008, 0.003, -0.025, 0.006])     # LM18's five returns (lm22.md:75)
u3 = 0.3
put(f"five returns (LM18's, lm22.md:75), u 0.3: j {jrank(u3, 5)}; VaR {f(100 * var_h(x5, u3), 2)}%; ES (32.2) "
    f"{f(100 * es_h(x5, u3), 4)}%; mean of the 2 worst {f(100 * es_k(x5, u3), 2)}%; Acerbi-Tasche's floor "
    f"[uT] = {floor(u3 * 5)} worst {f(-100 * float(np.sort(x5)[0]), 2)}%")                                 # 10
rows = []
for u in (0.001, 0.01, 0.025, 0.05):
    rows.append(f"u {u}: j {jrank(u, T)}, VaR {f(100 * var_h(R, u), 2, 3)}, ES {f(100 * es_h(R, u), 2, 3)}, mean of j "
                f"worst {f(100 * es_k(R, u), 2, 3)}")
put("TR23 historical (%): " + "; ".join(rows) + " (VaR at 1% and 0.1% echo lm14.md:105)")                # 11
put(f"TR23 ES / VaR at 1%: {f(es_h(R, U) / var_h(R, U), 2)}; at 2.5%: {f(es_h(R, U2) / var_h(R, U2), 2)}; "
    f"KC: 50 returns at u 0.01 give j = {jrank(0.01, 50)}, so VaR = ES = the worst return")             # 12

# ================================================================ section 3: normal, t, horizon
mu, s = float(R.mean()), float(R.std(ddof=0))
rows = []
for u in (0.001, 0.01, 0.025):
    z = float(stats.norm.ppf(u))
    rows.append(f"u {u}: Phi^-1 {f(z, 4)}, phi/u {f(float(stats.norm.pdf(z)) / u, 3, 4)}, VaR "
                f"{f(100 * var_n(mu, s, u), 2, 3)}, ES {f(100 * es_n(mu, s, u), 2, 3)}")
put(f"normal on TR23 (mean {f(100 * mu, 4)}%, s {f(100 * s, 4)}%, lm19.md:19): " + "; ".join(rows))     # 13
nu0, loc0, sc0 = (float(v) for v in stats.t.fit(100 * R))
rows = []
for u in (0.001, 0.01, 0.025):
    rows.append(f"u {u}: q {f(float(stats.t.ppf(u, nu0)), 4)}, VaR {f(var_t(nu0, loc0, sc0, u), 2, 3)}, ES "
                f"{f(es_t(nu0, loc0, sc0, u), 2, 3)}")
put(f"Student t on TR23 (ML refit: nu {f(nu0, 3)}, loc {f(loc0, 4)}%, scale {f(sc0, 4)}%; lm20.md:269 prints "
    f"3.065, 0.0997, 0.7761; sd {f(sc0 * sqrt(nu0 / (nu0 - 2)), 3)}): " + "; ".join(rows)
    + " (1% VaR echoes lm15.md:461's -3.365%)")                                                         # 14
num = integrate.quad(lambda v: v * stats.t.pdf(v, nu0), -np.inf, float(stats.t.ppf(U, nu0)))[0] / U
d15 = abs(-loc0 - sc0 * num - es_t(nu0, loc0, sc0, U))
assert d15 < 1e-12                       # quad's default tolerances; the digits of d15 itself are rounding noise
put(f"check of (32.4): -loc - scale x (numerical tail mean of Y at 1%, quad's default tolerances) "
    f"{f(-loc0 - sc0 * num, 6)} against the closed form {f(es_t(nu0, loc0, sc0, U), 6)}; difference below 1e-12")  # 15
cs = np.concatenate([[0.0], np.cumsum(np.log1p(R))])
R10 = np.expm1(cs[10:] - cs[:-10])
rbar, sr = float(np.log1p(R).mean()), float(np.log1p(R).std(ddof=0))
v10n = 1 - exp(10 * rbar + sqrt(10) * sr * z01)
put(f"10-session TR23: {len(R10)} overlapping compound returns, 99% VaR {f(100 * var_h(R10, U), 2)}% (j "
    f"{jrank(U, len(R10))}); sqrt(10) x one-day {f(100 * sqrt(10) * var_h(R, U), 2)}%; iid normal log returns "
    f"(10 rbar + sqrt(10) s_r z) {f(100 * v10n, 2)}%; ratio empirical / sqrt rule "
    f"{f(var_h(R10, U) / (sqrt(10) * var_h(R, U)), 3)}")                                                # 16
loss = -R
x0 = 0.03
tail = loss[loss >= x0 - EPS]
kh = len(tail)
ah = kh / float(np.sum(np.log(tail / x0)))
rows = []
for u in (0.01, 0.001):
    vq = x0 * (kh / (T * u)) ** (1 / ah)
    rows.append(f"u {u}: VaR {f(100 * vq, 2)}% (historical {f(100 * var_h(R, u), 2)}), ES {f(100 * vq * ah / (ah - 1), 2)}%"
                f" (historical {f(100 * es_h(R, u), 2)})")
put(f"Hill tail (Problem 11): x0 3%, k {kh}, alpha_hat {f(ah, 2)} (lm20.md:441: 3.63, k = 108); "
    + "; ".join(rows))                                                                                   # 17

# ================================================================ section 4: precision of a quantile
xs = np.sort(R)
rows = []
for u in (0.01, 0.5):
    j1, j2, cov = binom_interval(T, u)
    half = (float(xs[j2 - 1]) - float(xs[j1 - 1])) / 2
    rows.append(f"u {u}: point R_({jrank(u, T)}) {f(100 * float(xs[jrank(u, T) - 1]), 4)}%; ranks {j1}, {j2}; "
                f"interval {f(100 * float(xs[j1 - 1]), 3)}% to {f(100 * float(xs[j2 - 1]), 3)}%; coverage {f(cov, 4)}; "
                f"half-width / 1.96 {f(100 * half / 1.96, 3, 4)} points")
put("TR23 distribution-free 95% intervals (32.5): " + "; ".join(rows) + " (median 0.0879% echoes lm14.md:103)")  # 18
rows = []
for u in (0.01, 0.5):
    j1, j2, _ = binom_interval(T, u)
    fhat = (j2 - j1) / (T * 100 * (float(xs[j2 - 1]) - float(xs[j1 - 1])))     # density per percentage point
    rows.append(f"u {u}: spacing density (j2 - j1)/(T (R_(j2) - R_(j1))) {f(fhat, 3, 4)} per point, SE "
                f"sqrt(u(1-u)/T)/f {f(sqrt(u * (1 - u) / T) / fhat, 3, 4)} points")
put("asymptotic SE (delta method on (32.5); Glasserman's (9.7) stated) with the density read off the interval's "
    "ranks: " + "; ".join(rows) + " (LM20's Student-t location SE 0.0124, lm20.md:269)")                  # 19
tw1, tw2 = np.random.default_rng([99, SEED]), np.random.default_rng([99, SEED])   # twins, as LM22's experiment 20
sbt = StationaryBootstrap(145, R, seed=tw1)
assert all(np.array_equal(np.asarray(sbt.index), stationary_idx(tw2, T, 145)) for _ in sbt.bootstrap(3))
rng5 = np.random.default_rng([5, SEED])
rng6 = np.random.default_rng([6, SEED])
qi, qb = [], []
for _ in range(20):
    qi.append(np.quantile(R[rng5.integers(0, T, size=(500, T))], U, axis=1, method="inverted_cdf"))
    qb.append(np.quantile(R[stat_idx(rng6, T, 145, 500)], U, axis=1, method="inverted_cdf"))
qi_a, qb_a = np.concatenate(qi), np.concatenate(qb)
put(f"bootstrap SE of TR23's 1% quantile (B 10,000 each, 20 consecutive batches of 500; experiments 5 iid and 6 "
    f"stationary, l = 145, LM22's rule lm22.md:254, LM22's draw order, equal to arch's StationaryBootstrap): iid "
    f"{f(100 * float(qi_a.std()), 3)} points (batch SE {f(100 * batch_se_sd(qi_a), 3, 4)}), blocks "
    f"{f(100 * float(qb_a.std()), 3)} points (batch SE {f(100 * batch_se_sd(qb_a), 3, 4)}); ratio "
    f"{f(float(qb_a.std() / qi_a.std()), 1, 2)}")                                                          # 20
last250 = R[-250:]
j1, j2, cov = binom_interval(250, U)
p0 = 0.99**250
put(f"250 returns: Pr(no return below the 1% quantile) = 0.99^250 = {f(p0, 4)} (BCBS 1996 Table 2: 8.11%); "
    f"ranks j1 {j1} (no lower end), j2 {j2}, coverage {f(cov, 4)}; TR23's last 250 returns ({dates[-250]} -> "
    f"{dates[-1]}): VaR -R_(3) {f(-100 * float(np.sort(last250)[2]), 2)}%, interval upper end R_({j2}) "
    f"{f(100 * float(np.sort(last250)[j2 - 1]), 2)}%, worst {f(100 * float(last250.min()), 2)}% on "
    f"{dates[len(R) - 250 + int(np.argmin(last250))]}")                                                    # 21

# ================================================================ section 5: coherence
pd_, lgd, gain = Fraction(8, 1000), Fraction(-60, 100), Fraction(2, 100)
p_any = 1 - (1 - pd_) ** 2
var1 = -gain                                      # Pr(default) 0.8% < 1%, so the 1% quantile is the gain
es1 = -(pd_ * lgd + (Fraction(1, 100) - pd_) * gain) / Fraction(1, 100)
half_one = (lgd + gain) / 2
p_both = pd_**2
assert p_any >= Fraction(1, 100) > p_both
es_half = -(p_both * lgd + (Fraction(1, 100) - p_both) * half_one) / Fraction(1, 100)
put(f"constructed bonds (default 0.8%, loss 60%, else +2%; independent): one bond VaR {float(100 * var1):.2f}%, ES "
    f"{float(100 * es1):.2f}%; half in each: Pr(at least one default) {float(100 * p_any):.4f}%, VaR "
    f"{float(-100 * half_one):.2f}%, ES {float(100 * es_half):.4f}%; halves' VaRs sum to {float(100 * var1):.2f}%")  # 22
k_n = float(stats.norm.pdf(stats.norm.ppf(U2))) / U2
put(f"normal: ES_0.025 / sigma {f(k_n, 4)} against VaR_0.01 / sigma {f(-z01, 4)} (ratio {f(k_n / -z01, 4)}); TR23 "
    f"ES 2.5% / VaR 1%: historical {f(100 * es_h(R, U2), 3)} / {f(100 * var_h(R, U), 3)} = "
    f"{f(es_h(R, U2) / var_h(R, U), 2, 3)}; normal {f(es_n(mu, s, U2) / var_n(mu, s, U), 3)}; t "
    f"{f(es_t(nu0, loc0, sc0, U2) / var_t(nu0, loc0, sc0, U), 2, 3)}")                                  # 23
sig0, trade0, rows0 = schedule(fr)[0]
xw = fr.X[rows0 - WINDOW:rows0]
nw_ = xw.shape[0]
wv, th = cp.Variable(5), cp.Variable()
lp = cp.Problem(cp.Minimize(th + cp.sum(cp.pos(-100 * xw @ wv - th)) / (U2 * nw_)), [cp.sum(wv) == 1, wv >= 0])
lp.solve(solver=cp.CLARABEL, tol_gap_abs=1e-12, tol_gap_rel=1e-12, tol_feas=1e-12)
assert lp.status == "optimal" and wv.value is not None and th.value is not None
w_es = np.where(np.abs(np.asarray(wv.value)) < 1e-6, 0.0, np.asarray(wv.value))
lp2 = cp.Problem(cp.Minimize(th + cp.sum(cp.pos(-100 * xw @ wv - th)) / (U2 * nw_)), [cp.sum(wv) == 1, wv >= 0])
lp2.solve(solver=cp.HIGHS)
assert lp2.status == "optimal" and lp.value is not None and lp2.value is not None
es_lp = float(lp.value) / 100
w3 = minvar(fr.A * cov0(xw), "R3 first window")
put(f"ES minimization (Problem 12; Rockafellar-Uryasev LP): first window {fr.est_dates[rows0 - WINDOW]} -> "
    f"{fr.est_dates[rows0 - 1]} ({nw_} rows; signal {sig0}, trade {trade0}), u 2.5% (uT {f(U2 * nw_, 1)}); weights "
    + ", ".join(f"{s_} {f(v, 3)}" for s_, v in zip(fr.funds, w_es, strict=True))
    + f"; ES {f(100 * es_lp, 3, 4)}%, theta* {f(float(th.value), 3, 4)}% = VaR {f(100 * var_h(xw @ w_es, U2), 3, 4)}%; "
    f"(32.2) at "
    f"the solution {f(100 * es_h(xw @ w_es, U2), 3, 4)}%; HiGHS objective gap {abs(float(lp2.value) - float(lp.value)):.1e}; "
    f"R3's ES {f(100 * es_h(xw @ w3, U2), 3, 4)}%, R1's {f(100 * es_h(xw @ np.full(5, 0.2), U2), 3, 4)}%")       # 24
Ls = np.sort(-100 * R)[::-1]                           # losses in %, largest first
csl = np.concatenate([[0.0], np.cumsum(Ls)])
kk_ = np.arange(1, T + 1)
Fru = Ls + (csl[kk_ - 1] - (kk_ - 1) * Ls) / (U * T)  # theta at the k-th largest loss: theta + sum_{i<k}(L_i - theta)/(uT)
kmin = int(np.argmin(Fru))
put(f"Rockafellar-Uryasev identity on TR23 at 1%: theta + sum (L - theta)+ / (uT) is piecewise linear and convex in "
    f"theta, so its minimum is at a loss; minimum {f(float(Fru[kmin]), 6)}% at theta = the {kmin + 1}th largest loss "
    f"{f(float(Ls[kmin]), 6)}% (= VaR {f(100 * var_h(R, U), 6)}%), against (32.2) {f(100 * es_h(R, U), 6)}%")  # 25

# ================================================================ section 6: filtered VaR, Monte Carlo
lst_t = [(d, p) for d, p in refits["t"] if d <= "2025-04-07"][-1]
lst_n = [(d, p) for d, p in refits["normal"] if d <= "2025-04-07"][-1]
pt, pn = lst_t[1], lst_n[1]
sg = {"EWMA": sqrt(float(FC["ewma"][i7])), "GARCH-n": sqrt(float(FC["garch_n"][i7])),
      "GARCH-t": sqrt(float(FC["garch_t"][i7]))}
put(f"forecasts for 7 April made on 2 April (% a day of y): EWMA sigma {f(sg['EWMA'], 4)} (lm26.md:39: 1.5605), "
    f"GARCH-n {f(sg['GARCH-n'], 4)} (lm26.md:39: 1.7222), GARCH-t {f(sg['GARCH-t'], 4)}; refits of {lst_t[0]}: "
    f"normal mean {f(float(pn[0]), 4)}%, t mean {f(float(pt[0]), 4)}%, t nu {f(float(pt[4]), 2)}, t persistence "
    f"{f(float(pt[2] + pt[3]), 4)}, t unconditional sd {f(sqrt(float(pt[1]) / (1 - float(pt[2] + pt[3]))), 3)}%")  # 26
y7 = float(y[i7])
zn = (y7 - float(pn[0])) / sg["GARCH-n"]
zt_ = (y7 - float(pt[0])) / sg["GARCH-t"]
sct = sqrt((float(pt[4]) - 2) / float(pt[4]))
p_n = float(stats.norm.cdf(zn))
p_t = float(stats.t.cdf(zt_ / sct, float(pt[4])))
put(f"7 April under the 2 April forecasts (Model): GARCH-n z {f(zn, 2)}, Pr {g(p_n, 2)} (once in {g(1 / p_n, 2)} "
    f"sessions, {g(1 / (p_n * A), 2)} years at A); GARCH-t standardized {f(zt_, 2)}, Pr {g(p_t, 2)} (once in "
    f"{f(1 / p_t, 0)} sessions, {f(1 / (p_t * A), 1)} years)")                                          # 27
mu_, om, al, be, nu7 = (float(v) for v in pt)
s2_0 = float(FC["garch_t"][i7])
rng1 = np.random.default_rng([1, SEED])
B1, m10 = 100_000, 10
tot = np.zeros(B1)
s2v = np.full(B1, s2_0)
for _ in range(m10):
    e = np.sqrt(s2v) * rng1.standard_t(nu7, size=B1) * sct
    tot += mu_ + e
    s2v = om + al * e**2 + be * s2v
R10mc = np.expm1(tot / 100)
v1t = VAR["GARCH-t"][k7]
real10 = float(np.prod(1 + R[i7:i7 + 10]) - 1)
put(f"Monte Carlo 10-session VaR, GARCH-t from 2 April (experiment 1, default_rng([1, {SEED}]), {B1:,} paths; "
    f"each of the {m10} steps draws standard_t(nu, size={B1:,}) for all paths at once; batch SE over 20 consecutive "
    f"batches of 5,000 paths): "
    f"{f(-100 * float(np.quantile(R10mc, U, method='inverted_cdf')), 2)}% (batch SE "
    f"{f(100 * batch_se_q(R10mc, U), 2)} points); sqrt(10) x one-day {f(100 * sqrt(10) * v1t, 2)}%; realized "
    f"{dates[i7]} -> {dates[i7 + 9]} {f(100 * real10, 2)}%")                                            # 28
put(f"KC section 6: a 1% log-return quantile of -4% gives R's 1% quantile e^-0.04 - 1 = {f(100 * (exp(-0.04) - 1), 3)}%")  # 29

# ================================================================ section 7: backtests
cum250 = [100 * float(stats.binom.cdf(x, 250, U)) for x in range(11)]


def zones(n: int) -> tuple[int, int]:
    yel = next(x for x in range(n + 1) if stats.binom.cdf(x, n, U) >= 0.95)
    red = next(x for x in range(n + 1) if stats.binom.cdf(x, n, U) >= 0.9999)
    return yel, red


yb, rb = zones(250)
assert (yb, rb) == (5, 10)                 # BCBS 1996 Table 2; the 250-day window shares below use 5-9 and 10+
y5, r5 = zones(500)
yN, rN = zones(n_bt)
put("Basel 1996, 250 days at 99%: Pr(X <= x) for x = 0..10 (%): " + ", ".join(f(v, 2) for v in cum250)
    + f"; yellow from {yb}, red from {rb}; 500 days: yellow from {y5}, red from {r5}; {n_bt} days: yellow from "
    f"{yN}, red from {rN}")                                                                              # 30
BT: dict[str, dict[str, float]] = {}
lines = []
for m in MODELS:
    v = VAR[m]
    hit = Ro < -v - EPS
    margin = 100 * float(np.min(np.abs(Ro + v)))      # in percentage points
    x = int(hit.sum())
    p_cov = float(stats.binom.sf(x - 1, n_bt, U))
    trials = int(hit[:-1].sum())
    n11 = int((hit[:-1] & hit[1:]).sum())
    p_ind = float(stats.binom.sf(n11 - 1, trials, x / n_bt))
    csum = np.concatenate([[0], np.cumsum(hit)])
    r250 = csum[250:] - csum[:-250]
    zone = "green" if x < yN else ("yellow" if x < rN else "red")
    BT[m] = {"x": x, "p_cov": p_cov, "n11": n11, "trials": trials, "p_ind": p_ind, "mean": float(v.mean())}
    imax = int(np.argmax(r250))
    lines.append(f"{m}: x {x} ({f(100 * x / n_bt, 2)}%), Pr(X >= x) {g(p_cov, 2)}, zone {zone}; after an exceedance "
                 f"{n11} of {trials} (expected {f(trials * x / n_bt, 2)}), p {g(p_ind, 2)}; 250-day windows "
                 f"{len(r250)}: yellow {f(100 * float(np.mean((r250 >= 5) & (r250 <= 9))), 1)}%, red "
                 f"{f(100 * float(np.mean(r250 >= 10)), 1)}%, max {int(r250.max())} (window ending "
                 f"{dates[int(oos[imax + 249])]}); mean VaR {f(100 * float(v.mean()), 2)}%; smallest margin "
                 f"|R + VaR| {f(margin, 3)} points")
put("six models, u 1%, n " + str(n_bt) + ": " + " | ".join(lines))                                       # 31
put(f"tests on TR23's forecasts: {2 * len(MODELS)} (coverage and independence for six models); Bonferroni level "
    f"0.05/{2 * len(MODELS)} = {f(0.05 / (2 * len(MODELS)), 4)}; coverage rejected at it: "
    + ", ".join(m for m in MODELS if BT[m]["p_cov"] <= 0.05 / 12) + "; independence rejected at it: "
    + ", ".join(m for m in MODELS if BT[m]["p_ind"] <= 0.05 / 12))                                       # 32
x_hs = int(BT["HS"]["x"])
put(f"KC section 7 (Problem 9 style): HS's {x_hs} exceedances against {f(n_bt * U, 2)} expected; SD of the count under "
    f"the binomial {f(sqrt(n_bt * U * (1 - U)), 2)}; z {f((x_hs - n_bt * U) / sqrt(n_bt * U * (1 - U)), 2)}")  # 33
hit7 = {m: bool(Ro[k7] < -VAR[m][k7] - EPS) for m in MODELS}
put("7 April 2025 an exceedance for: " + ", ".join(m for m in MODELS if hit7[m])
    + "; exceedances in the 10 sessions from 7 April: "
    + ", ".join(f"{m} {int((Ro[k7:k7 + 10] < -VAR[m][k7:k7 + 10] - EPS).sum())}" for m in MODELS))      # 34

# ================================================================ section 8: drawdowns of the rules
rows = []
for k in RULES:
    sp = SP[k]
    rows.append(f"{k} MDD {f(100 * sp.mdd, 2)} ({sp.peak} -> {sp.trough} -> {sp.rec}); longest "
                f"{sp.long} ({sp.long_peak} -> {sp.long_end}); DD0 {f(100 * sp.dd0, 2)} ({sp.dd0_date}); end "
                f"{f(100 * sp.end_dd, 2)}")
put("rules' drawdowns (%; sessions): " + " | ".join(rows))                                              # 35
B3 = 10_000
rng3 = np.random.default_rng([3, SEED])
rng4 = np.random.default_rng([4, SEED])
MP: dict[str, Vec] = {}
MB: dict[str, Vec] = {}
ELL: dict[str, int] = {}
for k in RULES:                                       # experiment 3 first for every rule, then experiment 4
    MP[k] = np.concatenate([mdd_rows(rng3.permuted(np.tile(ret[k], (500, 1)), axis=1), float(paths[k].wealth[0]))
                            for _ in range(20)])
for k in RULES:
    ELL[k] = book_ell(ret[k])
    MB[k] = np.concatenate([mdd_rows(ret[k][stat_idx(rng4, nR, ELL[k], 500)], float(paths[k].wealth[0]))
                            for _ in range(20)])


def atom(k: str, v: Vec) -> tuple[float, float, str]:
    """The most frequent MDD of the resamples (values equal to 1e-10), its share, and the realized peak -> trough
    whose fall equals it (a block that holds that whole episode reproduces it exactly)."""
    vals, cnt = np.unique(np.round(v, 10), return_counts=True)
    i = int(np.argmax(cnt))
    a, share = float(vals[i]), float(cnt[i]) / len(v)
    W = path_of(paths[k].wealth)
    lab = ["start", *paths[k].dates]
    fall = 1 - W[None, :] / W[:, None]
    ii, jj = np.nonzero(np.triu(np.abs(fall - a) < 1e-9, 1))
    return a, share, (f"{lab[int(ii[0])]} -> {lab[int(jj[0])]}" if len(ii) else "no realized peak-to-trough")


def dist_row(k: str, v: Vec, with_atom: bool = False) -> str:
    real = SP[k].mdd
    n_ge = int(np.sum(v >= real - EPS))        # a count of 10,000: printed exactly (as a share it can sit on a tie)
    sh = n_ge / len(v)
    med = float(np.quantile(v, 0.5, method="inverted_cdf"))
    on_atom = float(np.mean(np.abs(v - med) < 1e-10)) > 0.01
    se = "on the atom, no batch SE" if on_atom else f"batch SE {f(100 * batch_se_q(v, 0.5), 2)}"
    n_eq = int(np.sum(np.abs(v - real) < 1e-10))       # resamples that rebuild the realized MDD episode exactly
    ties = f", {n_eq} of them equal to it" if with_atom else ""
    row = (f"{k} median {f(100 * med, 1)} ({se}), 5-95% "
           f"{f(100 * float(np.quantile(v, 0.05, method='inverted_cdf')), 1)}-"
           f"{f(100 * float(np.quantile(v, 0.95, method='inverted_cdf')), 1)}, at or above the realized {n_ge} of "
           f"{len(v):,}{ties} (SE {f(100 * sqrt(sh * (1 - sh) / B3), 2)} points)")
    if with_atom:
        a, s_a, where = atom(k, v)
        row += (f", largest atom {f(100 * a, 2)} in {round(s_a * len(v))} of {len(v):,} resamples (the realized fall "
                f"{where})")
    return row


put(f"permutations of each rule's {nR} returns (experiment 3, default_rng([3, {SEED}]), {B3:,} each, rules in order; "
    f"MDD in %): " + " | ".join(dist_row(k, MP[k]) for k in RULES))                                     # 36
put(f"stationary bootstrap (experiment 4, default_rng([4, {SEED}]), {B3:,} each in LM22's draw order, one resample "
    f"after another, rules in order; the book's block rule on each rule's squared demeaned returns, block lengths "
    + ", ".join(f"{k} {ELL[k]}" for k in RULES)
    + "; MDD in %): " + " | ".join(dist_row(k, MB[k], with_atom=True) for k in RULES))                   # 37
gam = sqrt(pi / 8)
lg = sqrt(pi / 2) * 0.20 * sqrt(10)
put(f"Brownian motion, zero drift (Magdon-Ismail et al. 2004, eq. (16) of the authors' preprint of 2003-09-01): E[max log "
    f"drawdown] = 2 gamma sigma sqrt(T), gamma = sqrt(pi/8) = {f(gam, 4)}; hypothetical sigma 20% a year, 10 years: "
    f"{f(lg, 3)}, a loss of {f(100 * (1 - exp(-lg)), 1)}%")                                             # 38
put(f"R6 against R8: ES 1% {f(100 * es_h(ret['R6'], U), 2)} / {f(100 * es_h(ret['R8'], U), 2)}%; MDD "
    f"{f(100 * SP['R6'].mdd, 2)} / {f(100 * SP['R8'].mdd, 2)}% (their losses on 2025-04-07 are LM35's, A35-13)")  # 39
sp2 = SP["R2"]
put(f"KC section 8: R2 MDD {f(100 * sp2.mdd, 2)}% but max DD0 {f(100 * sp2.dd0, 2)}% ({sp2.dd0_date}; the first "
    f"purchase cost {f(100 * (1 - float(paths['R2'].wealth[0])), 3)}%, echo of LM27's A27-23); recovery "
    f"gain (1.17) {f(100 * sp2.mdd / (1 - sp2.mdd), 1)}%; R1's {f(100 * sp1.mdd / (1 - sp1.mdd), 2)}%")  # 40
mu1, s1 = float(ret["R1"].mean()), float(ret["R1"].std(ddof=0))
put("rules' normal 1% VaR (In-sample, own mean and s; %): " + "; ".join(
    f"{k} {f(100 * var_n(float(ret[k].mean()), float(ret[k].std(ddof=0)), U), 2)}" for k in RULES)
    + f"; R1 historical / normal {f(var_h(ret['R1'], U) / var_n(mu1, s1, U), 2)}")                      # 41

# ================================================================ widget and Python
ugrid = np.round(np.arange(1, 101) / 1000, 3)
ntail = jrank(0.10, nR)
rows = []
for k in RULES:
    a_, b_, c_ = (float(v) for v in stats.t.fit(100 * ret[k]))
    m_, s_ = 100 * float(ret[k].mean()), 100 * float(ret[k].std(ddof=0))
    rows.append(f"{k} nu {f(a_, 3)} loc {f(b_, 4)} scale {f(c_, 4)}" + (
        f" [R1 at 1%: historical {f(100 * var_h(ret[k], U), 2)} / {f(100 * es_h(ret[k], U), 2)}, normal "
        f"{f(var_n(m_, s_, U), 2)} / {f(es_n(m_, s_, U), 2)}, t {f(var_t(a_, b_, c_, U), 2)} / {f(es_t(a_, b_, c_, U), 2)}]"
        if k == "R1" else ""))
put(f"widget varLevel: u grid 0.001..0.100 ({len(ugrid)} values); per rule the {ntail} worst returns (u <= 10% "
    f"needs ranks up to ceil(0.1 x {nR}) = {ntail}); ML t fits (in-sample, %): " + "; ".join(rows))      # 42
put(f"Python: np.quantile(R, 0.01) default 'linear' {f(100 * float(np.quantile(R, U)), 4)}% against inverted_cdf "
    f"{f(100 * float(np.quantile(R, U, method='inverted_cdf')), 4)}%; for R1 {f(100 * float(np.quantile(ret['R1'], U)), 4)}"
    f" against {f(100 * float(np.quantile(ret['R1'], U, method='inverted_cdf')), 4)}%")                   # 43

# ================================================================ lab: intraday drawdowns from T5S (per-day statistics)
rows = []
for d in ("2025-04-07", "2024-08-05", "2020-03-19"):
    fpath = RAW5 / d[:4] / f"{d}.csv"
    if not fpath.exists():
        rows.append(f"{d}: raw T5S file missing")
        continue
    xx = pl.read_csv(fpath, schema_overrides={"date": pl.String, "TAIEX": pl.Float64})
    P = xx["TAIEX"].to_numpy().astype(np.float64)
    tt = xx["date"].str.slice(11, 8).to_list()
    assert tt[0] == "09:00:00" and tt[-1] == "13:30:00"
    lfall = np.log(np.maximum.accumulate(P) / P)          # log fall from the running peak (previous close included)
    jl = int(np.argmin(P))
    jm = int(np.argmax(lfall))
    rows.append(f"{d}: close {f(100 * float(np.log(P[-1] / P[0])), 2)}%, low {f(100 * float(np.log(P[jl] / P[0])), 2)}% "
                f"at {tt[jl]}, largest log fall from the running peak {f(100 * float(lfall[jm]), 2)}% (peak "
                f"{tt[int(np.argmax(P[: jm + 1]))]}, trough {tt[jm]})")
put("T5S per day (TAIEX price index; log changes from 09:00:00, the previous close): " + "; ".join(rows))  # 44

# ================================================================ problems
put(f"P1: T 250, u 1%: j = ceil(2.5) = {jrank(U, 250)} (floor gives 2)")                              # 45
xp2 = np.array([-0.061, -0.048, -0.042, -0.037, -0.033])
put(f"P2 (T 180, u 2.5%, worst five -6.1, -4.8, -4.2, -3.7, -3.3%): uT {f(180 * U2, 1)}, j {jrank(U2, 180)}; ES (32.2) "
    f"{f(-100 * (float(xp2[:4].sum()) / 180 + float(xp2[4]) * (U2 - 4 / 180)) / U2, 3)}%; mean of 5 worst "
    f"{f(-100 * float(xp2.mean()), 2)}%; mean of 4 worst {f(-100 * float(xp2[:4].mean()), 3)}%; VaR {f(100 * 0.033, 1)}%")  # 46
put(f"P3 (normal, mean 0.05%, sigma 1.2%, u 1%): VaR {f(var_n(0.05, 1.2, U), 3)}%, ES {f(es_n(0.05, 1.2, U), 3)}%; "
    f"distractors: VaR with the mean added {f(-z01 * 1.2 + 0.05, 3)}%; ES with the mean added "
    f"{f(0.05 + 1.2 * float(stats.norm.pdf(z01)) / U, 3)}%")                                           # 47
wp = np.array([1.00, 1.08, 1.02, 0.90, 0.95, 1.10, 1.04, 1.12])
ddp = dd_of(wp)
put("P4 (hypothetical wealth 1.00, 1.08, 1.02, 0.90, 0.95, 1.10, 1.04, 1.12): DD_t "
    + ", ".join(f(100 * v, 2) for v in ddp) + f"; MDD {f(100 * float(ddp.max()), 2)}%; max DD0 "
    f"{f(100 * max(0.0, 1 - float(wp.min())), 1)}%; recovery gain (1.17) {f(100 * float(ddp.max()) / (1 - float(ddp.max())), 2)}%")  # 48
j1k, j2k, covk = binom_interval(1000, U)
put(f"P6 (T 1,000, u 1%): ranks j1 {j1k}, j2 {j2k}, coverage {f(covk, 4)}; point R_({jrank(U, 1000)})")  # 49
pd7 = Fraction(4, 100)
pa7 = 1 - (1 - pd7) ** 2
es7_1 = -(pd7 * lgd + (Fraction(5, 100) - pd7) * gain) / Fraction(5, 100)
pb7 = pd7**2
pone7 = 2 * pd7 * (1 - pd7)
assert pb7 < Fraction(5, 100) <= pb7 + pone7
es7_h = -(pb7 * lgd + (Fraction(5, 100) - pb7) * half_one) / Fraction(5, 100)
put(f"P7 (default 4%, loss 60%, else +2%, u 5%): one bond VaR {float(100 * var1):.2f}%, ES {float(100 * es7_1):.2f}%; "
    f"half each: Pr(at least one) {float(100 * pa7):.2f}%, VaR {float(-100 * half_one):.2f}%, ES {float(100 * es7_h):.2f}%")  # 50
put(f"P8 (500 days, 99%): yellow from {y5}, red from {r5}; 9 exceedances: Pr(X >= 9) {f(float(stats.binom.sf(8, 500, U)), 4)}, "
    f"Pr(X <= 9) {f(float(stats.binom.cdf(9, 500, U)), 4)}")                                             # 51
put(f"P9 (2,000 days, 60 exceedances of which 59 have a next day, 6 followed by another): expected "
    f"{f(59 * 60 / 2000, 3)}; Pr(Bin(59, 0.03) >= 6) {f(float(stats.binom.sf(5, 59, 60 / 2000)), 4)}")   # 52
rng2 = np.random.default_rng([2, SEED])
kk = -zn
Z = rng2.standard_normal(10_000)
wis = (Z <= 0) * np.exp(kk * Z - kk * kk / 2)
p_is = float(wis.mean())
se_is = float(wis.std() / sqrt(len(wis)))
var_one = exp(kk * kk) * float(stats.norm.cdf(-2 * kk)) - p_n**2
put(f"P10 importance sampling (18.7), shift a = {f(kk, 4)} (7 April under GARCH-n), experiment 2, default_rng([2, "
    f"{SEED}]), 10,000 draws: {g(p_is, 4)} +- {g(se_is, 2)} (relative SE {f(100 * se_is / p_is, 1)}%); exact Phi(-a) "
    f"{g(p_n, 4)}; plain draws in the tail expected {f(10_000 * p_n, 6)}; variance ratio p(1-p) / (e^a^2 Phi(-2a) - p^2) "
    f"{g(p_n * (1 - p_n) / var_one, 3)}; shifted draws in the tail {int((Z <= 0).sum())}")              # 53


def es_day(model: str, tt: int, u: float) -> float:
    """ES_u of the next day's simple return R = e^r - 1 under each model's forecast for day tt, (32.1): HS, N and t
    on the window's simple returns; for the log-return models r (decimal) = g + s xi, ES = 1 - E[e^r 1{r <= q}] / u,
    in closed form for normal xi, e^(g + s^2/2) Phi(Phi^-1(u) - s), and by quadrature for the scaled t."""
    win = R[tt - W_:tt]
    if model == "HS":
        return es_h(win, u)
    if model == "N":
        return es_n(float(win.mean()), float(win.std(ddof=0)), u)
    if model == "t":
        a, b, c = tday[tt]
        return es_t(float(a), float(b), float(c), u) / 100
    if model in ("EWMA", "GARCH-n"):
        g0 = 0.0 if model == "EWMA" else float(mu_n[tt]) / 100
        s0 = sqrt(float(FC["ewma" if model == "EWMA" else "garch_n"][tt])) / 100
        closed = 1 - exp(g0 + s0 * s0 / 2) * float(stats.norm.cdf(stats.norm.ppf(u) - s0)) / u
        qn = g0 + s0 * float(stats.norm.ppf(u))
        num_ = 1 - integrate.quad(lambda v: exp(v) * float(stats.norm.pdf(v, g0, s0)), -np.inf, qn)[0] / u
        assert abs(closed - num_) < 1e-10
        return closed
    nv = float(nu_t[tt])
    g0, s0, c0 = float(mu_t[tt]) / 100, sqrt(float(FC["garch_t"][tt])) / 100, sqrt((nv - 2) / nv)
    qy = float(stats.t.ppf(u, nv))
    return 1 - integrate.quad(lambda v: exp(g0 + s0 * c0 * v) * float(stats.t.pdf(v, nv)), -np.inf, qy)[0] / u


ES7 = {m: es_day(m, i7, U) for m in MODELS}
put("2 April 2025 -> 7 April 99% ES forecasts (%; u = 1%, (32.1) under each model): "
    + "; ".join(f"{m} {f(100 * ES7[m], 2)}" for m in MODELS) + "; ES / VaR "
    + "; ".join(f"{m} {f(ES7[m] / VAR[m][k7], 2)}" for m in MODELS) + "; loss / ES "
    + "; ".join(f"{m} {f(-R[i7] / ES7[m], 1)}" for m in MODELS)
    + f"; range {f(100 * min(ES7.values()), 2)} to {f(100 * max(ES7.values()), 2)}")                    # 54
rng7 = np.random.default_rng([7, SEED])
B7 = 100_000
R10iid = np.concatenate([np.prod(1 + R[rng7.integers(0, T, size=(5_000, 10))], axis=1) - 1 for _ in range(20)])
put(f"10 sessions drawn iid from TR23's 5,849 returns (experiment 7, default_rng([7, {SEED}]), {B7:,} sums in 20 "
    f"consecutive batches, each one integers(0, T, size=(5000, 10)), a row per sum): 99% VaR {f(-100 * float(np.quantile(R10iid, U, method='inverted_cdf')), 2)}% (batch SE "
    f"{f(100 * batch_se_q(R10iid, U), 2)} points), against the overlapping {f(100 * var_h(R10, U), 2)}% (A32-16) and "
    f"sqrt(10) x one-day {f(100 * sqrt(10) * var_h(R, U), 2)}%")                                         # 55
print("\n".join(OUT))
