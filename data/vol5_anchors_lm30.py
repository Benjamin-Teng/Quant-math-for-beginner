"""LM30 anchors (Estimation Error and Robust Portfolios): every number the Stage 1 brief quotes (drafted 2026-10-24).

Reads only data/processed/*.parquet, through the shared builders (run them first):
  * E5 (batch 4): vol5_series.frames("E5"), which reads data/processed/vol5_frames.parquet (built and checked by
    data/vol5_series.py): the estimation frame (the dates on which all five funds have a one-session total return,
    T = 2,362, 2017-01-18 .. 2026-10-08) and the wealth frame (2,368 sessions).
  * The through case: data/vol5_rules.py's schedule, signals, wealth_path, summary, minvar, maxsharpe, cov0, RF,
    WINDOW and R2 (the rules are computed there, never re-implemented here). Its first window is the 504 estimation
    rows through the first signal, 2019-02-27.
  * U28 (Volume II): data/lm10_series.py's u28(), which reads data/processed/vol2_closes.parquet (built and repaired
    by data/vol2_series.py): 28 TWSE sector price indices and the TAIEX price index, T = 4,382 simple daily returns,
    2008-12-02 .. 2026-10-08, A = T / years = 245.4794; LM11's halves, the first and last 2,191 returns.
  * LM10's constructed pairwise correlation matrix C_pw, from its entries as printed (lm10.md:376-378: 0.982 for
    0050/00631L, 0.199 for 0050/00679B, -0.444 for 00631L/00679B). No other input.

Conventions. Sample covariance matrices divide by T (cov0, AUTHORING section 6); a window's annual inputs are A times
the daily ones with E5's estimation-frame A (as vol5_rules does), U28's own A for U28. Excess returns are over
RF = 1.5% a year, RF / A a day. Shrinkage (30.1): S_c = c S + (1 - c) lam_bar I with lam_bar = tr S / N, so c is the
data's weight and scikit-learn's shrinkage_ is 1 - c; LedoitWolf(assume_centered=False) throughout. The Frobenius norm
is unscaled (LM18); Ledoit and Wolf's 1/N scaling cancels in every ratio printed here. Minimum-variance weights
w = S^-1 1 / 1'S^-1 1 come from np.linalg.solve (unconstrained) or vol5_rules.minvar (long-only, exact NNLS with its
KKT check). "Volatility" is sqrt(A w'S w); "predicted" uses the estimation sample's matrix, "realized" the evaluation
sample's (U28's second half), "true" the model's. A model Sharpe ratio of exposures f is sqrt(A) f'e / sqrt(f'S f)
with the model's daily e and S. The through-case volatilities are vol5_rules.summary()'s ("vol": daily net returns
from the session after the first trade, divisor T, times sqrt(A_w)). Raw kurtosis is (14.5) with divisor-T moments
(scipy.stats.kurtosis, fisher=False, bias=True). A median or other quantile is x_(ceil(uT)) (method="inverted_cdf").
Counts against a threshold use the guard 1e-12; a weight below 1e-6 counts as 0 (shared decision "Solver output").

Seeds (AUTHORING section 8; one generator per experiment, created once): experiment 1, default_rng([1, 20261011]):
10,000 samples of 504 days from N(mean, S) of the first window, one standard_normal((504, 5)) call per sample;
experiment 2, default_rng([2, 20261011]): 2,000 samples at each of seven lengths, in increasing order; experiment 3,
default_rng([3, 20261011]): U28's first-half S as the truth (mean 0), 1,000 samples at each of seven lengths, in
increasing order, one standard_normal((T, 28)) call per sample; experiment 4, default_rng([4, 20261011]): 1,000 iid
bootstrap resamples of the first window's 504 rows (integers(0, 504, 504) per resample). Standard errors: a Monte
Carlo mean's is its SD (divisor n) over sqrt(n), and a paired difference's the same on the per-sample differences; a
proportion's is sqrt(p (1 - p) / n); any other statistic of experiment 1 (a median, an SD, a ratio of SDs) gets a
batch SE: the statistic on 20 consecutive batches of 500 samples, their SD (divisor 20) over sqrt(20).

Revised 2026-10-24 to the editor's decisions on the briefs (plans/vol-5.md): experiment 2 prints each length's gap to
SR(1/N) in SEs (A30-11), every Monte Carlo result carries its SE (A30-07, 08, 10, 21, 27), the excess of Ledoit and
Wolf's noise estimate over (18.4)'s value is split by fund (A30-13, A30-15), A30-41 is withdrawn (decision D settled
the Black-Litterman delta) and A30-42 adds the error of R1's risk shares in experiment 1 (LM27 hands it to LM30).
Revised again 2026-10-24 to the decisions on the second recomputation: A30-03 measures the calendar span from the
close before the first return (A28-02's), echoes print at their owners' precision (A30-04, A30-06, A30-39), every
Monte Carlo result prints at its SE's digit (mc(); A30-07 to A30-11, A30-21, A30-27, A30-42), A30-20 states the
singular window's zero variance without its rounding noise, and A30-43 adds the ratio SR(1/N) / SR* beside DeMiguel,
Garlappi and Uppal's calibration. Repaired 2026-10-25 after the verifier's check: E2 shows (20.2)'s computation with
the volatilities at 2 dp and tau at 4 dp (decision C12's exception), so A30-04 flags the volatilities at 1 and 2 dp
and A30-06 recomputes the SEs from those printed inputs. Revised 2026-10-25 to the decisions on the third
revision: A30-03 also flags tau at 3 dp (three decimals suffice for (20.2)'s computation; the fourth keeps tau
off a rounding boundary). Revised 2026-10-31 to the fresh check of the whole of Stage 1: identities that hold to
rounding error (A30-05's R3 against w_mv, A30-13's c_hat against scikit-learn's shrinkage_ and covariance_, A30-22's
S_nu weights and stationarity gap, A30-26's average) are asserted below BOUND = 1e-15 and printed as that bound, not
as their rounding noise (another implementation gets other noise); A30-12 adds R1's full-sample fixed-weight
volatility (echo of A27-13), which X1's note names beside the out-of-sample 12.48% (decision C7).

Rounding flags. Every number the brief prints passes through f(x, k1, k2, ...), which shows x with max(k) + 3 decimals
and flags it "NEAR" for each printed precision k at which x lies within a tenth of a last-digit unit of a rounding
boundary (|frac(10^k |x|) - 0.5| < 0.1). The brief prints a flagged value as rounded from the unrounded value here.
A Monte Carlo result goes through mc(x, se): the SE is rounded to one significant digit, x and its SE are shown at
that digit's decimal k (plus 3 decimals, flagged at k) and the line says "prints at k dp".

Prints one line per anchor, "A30-NN <value>", in ID order, and writes nothing.

Run:  PYTHONUTF8=1 uv run python data/vol5_anchors_lm30.py
"""
import sys
from collections.abc import Callable
from datetime import date
from decimal import Decimal
from math import floor, log10, sqrt
from pathlib import Path

import cvxpy as cp
import numpy as np
import polars as pl
from numpy.typing import NDArray
from scipy.stats import kurtosis
from sklearn.covariance import LedoitWolf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lm10_series import u28
from vol5_rules import (
    CLARABEL_OPTS,
    ERC_OPTS,
    R2,
    RF,
    WINDOW,
    cov0,
    maxsharpe,
    minvar,
    schedule,
    signals,
    summary,
    wealth_path,
)
from vol5_series import frames

SEED = 20261011
EPS = 1e-12
ZERO = 1e-6
BOUND = 1e-15               # an identity that holds to rounding error is asserted below this and printed as the bound
NB = 20                     # batches for the batch SE of experiment 1's non-mean statistics
CONE_OPTS = ERC_OPTS        # CLARABEL at 1e-10, the shared tolerance for cone programs
Vec = NDArray[np.float64]
Mat = NDArray[np.float64]

OUT: list[str] = []
NEAR: list[str] = []
LATE: dict[int, str] = {}   # anchors computed early but printed in ID order at the end


def put(value: str, num: int | None = None) -> None:
    """One anchor line; values that f() found near a rounding boundary are listed at its end."""
    tail = f" [NEAR a rounding boundary: {'; '.join(NEAR)}]" if NEAR else ""
    NEAR.clear()
    if num is None:
        OUT.append(f"A30-{len(OUT) + 1:02d} {value}{tail}")
    else:
        LATE[num] = f"A30-{num:02d} {value}{tail}"


def f(x: float, *ks: int, plus: bool = False) -> str:
    """x with max(ks) + 3 decimals; flagged for each printed precision k within 0.1 of a last-digit unit of a boundary."""
    x = float(x)
    for k in ks:
        u = abs(x) * 10**k
        if abs(u - floor(u) - 0.5) < 0.1:
            NEAR.append(f"{x:.{k + 3}f} at {k} dp")
    return f"{x:{'+' if plus else ''}.{max(ks) + 3}f}"


def k_of(se: float) -> int:
    """Decimals at which a Monte Carlo result prints: the SE is rounded to one significant digit, and the result's last
    printed digit sits at that digit (decision of the second recomputation, 2026-10-24)."""
    k = -floor(log10(float(f"{se:.0e}")))
    assert k >= 0, se
    return k


def mc(x: float, se: float, plus: bool = False, label: str = "SE") -> str:
    """A Monte Carlo result with its SE, both at the result's printed precision (shown with 3 more decimals)."""
    k = k_of(se)
    return f"{f(x, k, plus=plus)} ({label} {f(se, k)}, prints at {k} dp)"


def pct(v: Vec, *ks: int) -> str:
    return "(" + ", ".join(f(100 * float(x), *ks) for x in v) + ")"


def vec(v: Vec, k: int) -> str:
    return "(" + ", ".join(f(float(x), k) for x in v) + ")"


def gmv(S: Mat) -> Vec:
    w = np.linalg.solve(S, np.ones(S.shape[0]))
    return w / w.sum()


def vol(w: Vec, S: Mat, a: float) -> float:
    return sqrt(a * float(w @ S @ w))


def fro2(M: Mat) -> float:
    return float(np.sum(M * M))


def lw_by_hand(x: Mat) -> tuple[float, float, float, float]:
    """(lam_bar, |S - lam_bar I|^2, noise estimate, c_hat) by Ledoit and Wolf's (2004) formulas, divisor T, centred."""
    T, n = x.shape
    xc = x - x.mean(axis=0)
    S = xc.T @ xc / T
    lam = float(np.trace(S)) / n
    d2 = fro2(S - lam * np.eye(n))
    b2 = sum(fro2(np.outer(v, v) - S) for v in xc) / T**2
    return lam, d2, b2, 1 - min(b2, d2) / d2


def c_lw(x: Mat) -> float:
    return 1 - float(LedoitWolf(assume_centered=False).fit(x).shrinkage_)


def shrunk(x: Mat) -> Mat:
    return np.asarray(LedoitWolf(assume_centered=False).fit(x).covariance_, dtype=np.float64)


def normal_noise(S: Mat, T: int) -> float:
    """E|S_hat - S|_F^2 for T iid normal vectors with known mean, (18.4)."""
    return (fro2(S) + float(np.trace(S)) ** 2) / T


def oracle_c(S: Mat, T: int) -> float:
    n = S.shape[0]
    d = fro2(S - float(np.trace(S)) / n * np.eye(n))
    return d / (d + normal_noise(S, T))


def kappa(S: Mat) -> float:
    ev = np.linalg.eigvalsh(S)
    return float(ev[-1] / ev[0])


def q50(v: Vec) -> float:
    return float(np.quantile(v, 0.5, method="inverted_cdf"))


def mean_se(v: Vec) -> tuple[float, float]:
    return float(v.mean()), float(v.std() / sqrt(len(v)))


def batch_se(stat: Callable[[Mat], NDArray[np.float64] | float], data: Mat) -> Vec:
    """SE of stat(data) from NB consecutive batches of the samples (rows): SD (divisor NB) over sqrt(NB)."""
    vals = np.array([np.asarray(stat(chunk), dtype=np.float64) for chunk in np.array_split(data, NB)])
    return np.atleast_1d(vals.std(axis=0) / sqrt(NB))


def noise_split(x: Mat) -> tuple[Vec, float]:
    """Each fund's share of the excess of Ledoit and Wolf's noise estimate over (18.4)'s value, entry by entry, by row;
    and c_hat with (18.4)'s value in place of the noise estimate (the window's S as the truth)."""
    T, n = x.shape
    xc = x - x.mean(axis=0)
    S = xc.T @ xc / T
    noise = np.zeros((n, n))
    for v in xc:
        noise += (np.outer(v, v) - S) ** 2
    noise /= T**2
    normal = (S**2 + np.outer(np.diag(S), np.diag(S))) / T
    ex = noise - normal
    d2 = fro2(S - float(np.trace(S)) / n * np.eye(n))
    return ex.sum(axis=1) / ex.sum(), 1 - min(float(normal.sum()), d2) / d2


# ---------------------------------------------------------------- E5 and the through case
fr = frames("E5")
F5 = fr.funds
N5 = len(F5)
A = fr.A
put(f"E5 estimation frame T {len(fr.est_dates)} ({fr.est_dates[0]} .. {fr.est_dates[-1]}), A {f(A, 2, 6)}; "
    f"wealth frame {len(fr.wealth_dates)} sessions ({fr.wealth_dates[0]} .. {fr.wealth_dates[-1]}), "
    f"A_w {f(fr.A_wealth, 2, 6)}")                                                                       # 01
sch = schedule(fr)
put(f"{len(sch)} signals, first {sch[0][0]} (trade {sch[0][1]}), last {sch[-1][0]} (trade {sch[-1][1]}); window "
    f"{WINDOW} estimation rows")                                                                         # 02
rows0 = sch[0][2]
x0 = fr.X[rows0 - WINDOW:rows0]
tau = WINDOW / A
d_first, d_last = fr.est_dates[rows0 - WINDOW], fr.est_dates[rows0 - 1]
b0w = fr.wealth_dates[fr.wealth_dates.index(d_first) - 1]      # the close before the window's first return
cal0 = (date.fromisoformat(d_last) - date.fromisoformat(b0w)).days / 365.25
put(f"first window: {WINDOW} returns {d_first} .. {d_last}; tau = T/A {f(tau, 2, 3, 4)} years (sessions over A, as "
    f"A28-02 computes it); calendar years from the close before the first return ({b0w}) to {d_last} "
    f"{f(cal0, 2)} (A28-02's)")                                                                           # 03
mu_d = x0.mean(axis=0)
S_d = cov0(x0)
mu_a, S_a = A * mu_d, A * S_d
sd_a = np.sqrt(np.diag(S_a))
C0 = S_a / np.outer(sd_a, sd_a)
iu = np.triu_indices(N5, 1)
put(f"first window, annual means A R_bar {pct(mu_a, 1)}%; SDs sqrt(A) s {pct(sd_a, 1, 2)}%; correlations "
    + ", ".join(f"{F5[i]}/{F5[j]} {f(C0[i, j], 2)}" for i, j in zip(*iu, strict=True)))                # 04
e_d = mu_d - RF / A
Si = np.linalg.inv(S_d)
delta_m = float(np.ones(N5) @ Si @ e_d)
w_tan = Si @ e_d / delta_m
sr_star = sqrt(A * float(e_d @ Si @ e_d))
w1 = np.full(N5, 1 / N5)


def sr_true(fx: Vec) -> float:
    return sqrt(A) * float(fx @ e_d) / sqrt(float(fx @ S_d @ fx))


sr_1n = sr_true(w1)
w_mv = gmv(S_d)
r3_first = minvar(S_a, "R3 first window")
assert np.abs(r3_first - w_mv).max() < BOUND      # a rounding-level agreement prints as the bound, not its noise
put(f"model = first window: w_tan {pct(w_tan, 1)}%; delta = 1'S^-1 e {f(delta_m, 2)}; SR* {f(sr_star, 2, 3)}; "
    f"SR(1/N) {f(sr_1n, 2, 3)} (equal weights' mean {f(100 * A * float(w1 @ mu_d), 2)}% and volatility "
    f"{f(100 * vol(w1, S_d, A), 2)}%, as A28-15); w_mv {pct(w_mv, 1)}%, sigma_min {f(100 * vol(w_mv, S_d, A), 2, 3)}%; "
    f"long-only R3 equals w_mv below {BOUND:.0e}")                                                      # 05
put(f"SR(1/N) / SR* in the model {f(sr_1n / sr_star, 2)} ({f(sr_1n, 3)} / {f(sr_star, 3)}); DeMiguel, Garlappi and "
    f"Uppal's panel E calibration (monthly Sharpe ratios 0.12 for 1/N and 0.15 for the tangency, their p. 1939) "
    f"{f(0.12 / 0.15, 1)}", num=43)                                                                       # 43
se_mean = sd_a / sqrt(tau)
nbelow = int((np.abs(mu_a) < se_mean - EPS).sum())
rms_rel = sqrt((1 + float(np.trace(S_a)) ** 2 / fro2(S_a)) / WINDOW)
se_printed = np.round(100 * sd_a, 2) / sqrt(round(tau, 4))     # E2's computation from its printed inputs
put(f"SE of annual means sqrt(A) s / sqrt(tau) {pct(se_mean, 1)} points; from E2's printed inputs (volatilities at "
    f"2 dp, tau {round(tau, 4)}) {vec(se_printed, 1)} points, the same at 1 dp: "
    f"{bool((np.round(se_printed, 1) == np.round(100 * se_mean, 1)).all())}; funds with |mean| below its SE {nbelow} "
    f"of {N5}; RMS relative error of S_hat by (18.4) at T {WINDOW}: {f(100 * rms_rel, 1)}%")          # 06

# experiment 1: plug-in errors at T = 504
Lc = np.linalg.cholesky(S_d)
rng1 = np.random.default_rng([1, SEED])
n1 = 10_000
sr_b, sr_m, sr_s = np.empty(n1), np.empty(n1), np.empty(n1)
fb_all, fs_all = np.empty((n1, N5)), np.empty((n1, N5))
mv_true, mv_pred = np.empty(n1), np.empty(n1)
rs_all = np.empty((n1, N5))
for i in range(n1):
    r = mu_d + rng1.standard_normal((WINDOW, N5)) @ Lc.T
    Sh = cov0(r)
    eh = r.mean(axis=0) - RF / A
    fb = np.linalg.solve(Sh, eh) / delta_m
    fm = Si @ eh / delta_m
    fs = np.linalg.solve(Sh, e_d) / delta_m
    sr_b[i], sr_m[i], sr_s[i] = sr_true(fb), sr_true(fm), sr_true(fs)
    fb_all[i], fs_all[i] = fb, fs
    wm = gmv(Sh)
    mv_true[i], mv_pred[i] = vol(wm, S_d, A), vol(wm, Sh, A)
    g1 = Sh @ w1
    rs_all[i] = w1 * g1 / float(w1 @ g1)          # R1's risk shares w_i (S_hat w)_i / w'S_hat w, LM27's statistic
mb, sb = mean_se(sr_b)
mm, sm = mean_se(sr_m)
ms, ss = mean_se(sr_s)
p_lose = float((sr_b < sr_1n - EPS).mean())
med_se = float(batch_se(lambda c: q50(c[:, 0]), sr_b[:, None])[0])
p_se = sqrt(p_lose * (1 - p_lose) / n1)
put(f"experiment 1 ({n1} samples of {WINDOW} days): mean true SR, means and covariances estimated {mc(mb, sb)}, "
    f"means only {mc(mm, sm)}, covariances only {mc(ms, ss)}; P(SR < SR(1/N)) in percent {mc(100 * p_lose, 100 * p_se)}; "
    f"median SR (both) {mc(q50(sr_b), med_se, label='batch SE')}")                                       # 07
sd_b, sd_s = fb_all.std(axis=0), fs_all.std(axis=0)
both = np.hstack([fb_all, fs_all])
se_sd = batch_se(lambda c: c.std(axis=0), both)
ratio = sd_b / sd_s
se_ratio = batch_se(lambda c: c[:, :N5].std(axis=0) / c[:, N5:].std(axis=0), both)
jlo, jhi = int(np.argmin(ratio)), int(np.argmax(ratio))
put("SD of plug-in exposures across samples, in points, with batch SEs: both estimated "
    + ", ".join(f"{F5[j]} {mc(100 * float(sd_b[j]), 100 * float(se_sd[j]))}" for j in range(N5))
    + "; covariances only "
    + ", ".join(f"{F5[j]} {mc(100 * float(sd_s[j]), 100 * float(se_sd[N5 + j]))}" for j in range(N5))
    + f"; ratio, fund by fund, smallest {F5[jlo]} {mc(float(ratio[jlo]), float(se_ratio[jlo]))}, largest {F5[jhi]} "
    f"{mc(float(ratio[jhi]), float(se_ratio[jhi]))}")                                                     # 08
nneg = int((fb_all.sum(axis=1) <= EPS).sum())
p9 = nneg / n1
put(f"samples with 1'f_hat <= 0 (normalized weights would flip sign): {nneg} of {n1}; share "
    f"{Decimal(100 * nneg) / Decimal(n1)}% exactly, {mc(100 * p9, 100 * sqrt(p9 * (1 - p9) / n1))}")   # 09
put(f"plug-in minimum variance in the model: mean true vol {mc(100 * mv_true.mean(), 100 * mv_true.std() / sqrt(n1))}%,"
    f" mean predicted {mc(100 * mv_pred.mean(), 100 * mv_pred.std() / sqrt(n1))}%, true minimum "
    f"{f(100 * vol(w_mv, S_d, A), 2, 3)}% (A28-10's sigma_min)")                                         # 10
rs_true = w1 * (S_d @ w1) / float(w1 @ S_d @ w1)
rs_sd = rs_all.std(axis=0)
rs_se = batch_se(lambda c: c.std(axis=0), rs_all)
put(f"experiment 1, R1's risk shares w_i (S w)_i / w'S w: true (the model's) {pct(rs_true, 1)}% (as A27-21); SD of "
    f"the estimated shares across the {n1} samples, in points, with batch SEs: "
    + ", ".join(f"{F5[j]} {mc(100 * float(rs_sd[j]), 100 * float(rs_se[j]))}" for j in range(N5))
    + f"; mean estimated {pct(rs_all.mean(axis=0), 1)}%", num=42)                                       # 42

# experiment 2: how long a sample the plug-in needs
rng2 = np.random.default_rng([2, SEED])
n2 = 2_000
grid2 = [126, 252, 504, 1008, 2016, 4032, 8064]
rows2 = []
for T in grid2:
    vb, vs = np.empty(n2), np.empty(n2)
    for i in range(n2):
        r = mu_d + rng2.standard_normal((T, N5)) @ Lc.T
        Sh = cov0(r)
        vb[i] = sr_true(np.linalg.solve(Sh, r.mean(axis=0) - RF / A))
        vs[i] = sr_true(np.linalg.solve(Sh, e_d))
    (b_, bse), (s_, sse) = mean_se(vb), mean_se(vs)
    rows2.append(f"T {T} ({f(T / A, 1, 2)} y): {mc(b_, bse)}, minus SR(1/N) "
                 f"{f((b_ - sr_1n) / bse, 1, plus=True)} SE; covariances only {mc(s_, sse)}")
put(f"experiment 2 ({n2} samples per length; years T/A with E5's A), mean true SR, both estimated and covariances "
    f"only: " + "; ".join(rows2) + f"; SR(1/N) {f(sr_1n, 3)}")                                           # 11

log: list[str] = []
sigs = signals(fr, log)
paths = {k: wealth_path(fr, sigs, k) for k in ("R1", "R3", "R5")}
vols = {k: float(summary(fr, p)["vol"]) for k, p in paths.items()}
pd1 = paths["R1"].dates
stored = pl.read_parquet(HERE / "processed" / "vol5_rules.parquet")
for k, v in vols.items():
    wv = stored.filter(pl.col("rule") == k).sort("date")["wealth"].to_numpy()
    rr = wv[1:] / wv[:-1] - 1
    assert abs(float(rr.std()) * sqrt(fr.A_wealth) - v) < 1e-12, k
pred3 = np.array([vol(sg.targets["R3"], cov0(fr.X[r_ - WINDOW:r_]), A) for sg, (_, _, r_) in zip(sigs, sch, strict=True)])
put(f"through case, realized volatility net of costs, daily returns {pd1[1]} .. {pd1[-1]} ({len(pd1) - 1} returns, "
    f"the session after the first trade to the end): R1 {f(100 * vols['R1'], 2, 4)}%, R3 {f(100 * vols['R3'], 2, 4)}%, "
    f"R5 {f(100 * vols['R5'], 2, 4)}% (R5 - R3 {f(100 * (vols['R5'] - vols['R3']), 2, 3, 4)} points; equal to "
    f"vol5_rules.parquet); R3 predicted in its windows: mean {f(100 * pred3.mean(), 2)}%, "
    f"{f(100 * pred3.min(), 2)}% to {f(100 * pred3.max(), 2)}%; R1 with fixed weights 1/5 over the whole "
    f"estimation frame ({fr.X.shape[0]} returns) {f(100 * vol(w1, cov0(fr.X), A), 2)}% (echo of A27-13's s_p)")  # 12

lam0, d20, b20, ch0 = lw_by_hand(x0)
ck0 = c_lw(x0)
cov_ok = float(np.abs(shrunk(x0) - (ch0 * S_d + (1 - ch0) * lam0 * np.eye(N5))).max())
gaps = []
for xs in (x0, sqrt(A) * x0):                     # daily units and annual units (returns times sqrt(A))
    sk = float(LedoitWolf(assume_centered=False).fit(xs).shrinkage_)
    ch_x = lw_by_hand(xs)[3]
    gaps += [abs(ch_x - (1 - sk)), abs(sk - (1 - ch_x))]
assert max(gaps) < BOUND, gaps                    # the gaps are rounding noise: assert the bound, print the bound
assert cov_ok < BOUND * lam0, cov_ok
assert abs(ck0 - c_lw(sqrt(A) * x0)) < BOUND
share0, _ = noise_split(x0)
put(f"Ledoit-Wolf on the first window, annual units: lam_bar {f(A * lam0, 4, 5)} (a volatility of "
    f"{f(100 * sqrt(A * lam0), 1)}%); |S - lam_bar I|_F^2 {A**2 * d20:.4e}; noise estimate {A**2 * b20:.4e}; "
    f"c_hat {f(ch0, 3, 4)}; scikit-learn shrinkage_ {f(1 - ck0, 3, 4)} (c_hat equals 1 - shrinkage_ to rounding "
    f"error: the largest gap of c_hat to 1 - shrinkage_ and of shrinkage_ to 1 - c_hat, daily and annual units, is "
    f"below {BOUND:.0e}; covariance_ equals c_hat S + (1 - c_hat) lam_bar I below {BOUND:.0e} of lam_bar; c_hat "
    f"daily against annual below {BOUND:.0e}); normal-model oracle c* "
    f"{f(oracle_c(S_d, WINDOW), 3, 4)}; noise estimate / normal value {f(b20 / normal_noise(S_d, WINDOW), 2)}; "
    f"each fund's share of the excess over the normal value (entry by entry, by row) {pct(share0, 0)}%")  # 13
cs = np.array([c_lw(fr.X[r_ - WINDOW:r_]) for _, _, r_ in sch])
imin = int(np.argmin(cs))
n_low = int((cs < 0.9 - EPS).sum())
put(f"c_hat over the {len(sch)} signals: min {f(float(cs.min()), 3, 4)} ({sch[imin][0]}), median "
    f"{f(q50(cs), 3, 4)}, max {f(float(cs.max()), 3, 4)} ({sch[int(np.argmax(cs))][0]}); below 0.9 at {n_low} "
    f"signals (first {sch[int(np.argmax(cs < 0.9))][0]}; nearest to 0.9 by {float(np.abs(cs - 0.9).min()):.1e}); "
    f"first {f(float(cs[0]), 3, 4)}")                                                                   # 14
xm = fr.X[sch[imin][2] - WINDOW:sch[imin][2]]
k0 = kurtosis(x0, axis=0, fisher=False, bias=True)
km = kurtosis(xm, axis=0, fisher=False, bias=True)
_, _, bm, _ = lw_by_hand(xm)
share_m, c_norm_m = noise_split(xm)
put(f"raw kurtosis, first window {vec(k0, 1)}; window to {sch[imin][0]} ({fr.est_dates[sch[imin][2] - WINDOW]} "
    f".. {fr.est_dates[sch[imin][2] - 1]}) {vec(km, 1)}; there the noise estimate is "
    f"{f(bm / normal_noise(cov0(xm), WINDOW), 1)} times the normal value, each fund's share of the excess "
    f"{pct(share_m, 0)}%, and c_hat with the normal value in place of the noise estimate would be "
    f"{f(c_norm_m, 3)} (against {f(float(cs[imin]), 3)})")                                               # 15
d35 = np.array([float(np.abs(sg.targets["R3"] - sg.targets["R5"]).max()) for sg in sigs])
jm = int(np.argmax(d35))
sdm = np.sqrt(np.diag(A * cov0(xm)))
z3 = sum(int((sg.targets["R3"] < ZERO).any()) for sg in sigs)
z5 = sum(int((sg.targets["R5"] < ZERO).any()) for sg in sigs)
put(f"R3 against R5: largest weight gap {f(100 * float(d35.max()), 1)} points at {sigs[jm].signal} (R3 "
    f"{pct(sigs[jm].targets['R3'], 1)}%, R5 {pct(sigs[jm].targets['R5'], 1)}%; window SDs {pct(sdm, 1)}%); median "
    f"gap {f(100 * q50(d35), 1)} points; signals with a zero weight: R3 {z3} (as A29-09), R5 {z5}")      # 16

# ---------------------------------------------------------------- U28
s = u28()
AU = s.A
NU = len(s.names)
H = s.X.shape[0] // 2
X1, X2 = s.X[:H], s.X[H:]
S1, S2 = cov0(X1), cov0(X2)
put(f"U28: T {s.X.shape[0]} ({s.dates[0]} .. {s.dates[-1]}), A {f(AU, 2, 4)}; halves {H}: {s.dates[0]} .. "
    f"{s.dates[H - 1]} and {s.dates[H]} .. {s.dates[-1]}")                                               # 17
ev1 = np.linalg.eigvalsh(S1)
c1 = c_lw(X1)
lam1 = float(np.trace(S1)) / NU
evc = c1 * ev1 + (1 - c1) * lam1
put(f"first half: annual eigenvalues lambda_1 {f(AU * ev1[-1], 4)}, lambda_28 {f(AU * ev1[0], 4, 5)}, mean "
    f"{f(AU * lam1, 4)}; kappa {f(kappa(S1), 2)} (lm11.md: 126.05); c_hat {f(c1, 3, 4)}; kappa after shrinkage "
    f"{f(float(evc[-1] / evc[0]), 2)}; normal-model oracle c* {f(oracle_c(S1, H), 3, 4)}")                # 18
w_s = gmv(S1)
Sc1 = shrunk(X1)
w_c = gmv(Sc1)
w_lo = minvar(AU * S1, "U28 long-only")
m1 = s.taiex[:H]
xmk = m1 - m1.mean()
beta = (X1 - X1.mean(axis=0)).T @ xmk / float(xmk @ xmk)
res = (X1 - X1.mean(axis=0)) - np.outer(xmk, beta)
SF = np.outer(beta, beta) * float(xmk @ xmk) / H + np.diag((res**2).mean(axis=0))
w_f = gmv(SF)
wN = np.full(NU, 1 / NU)
grid_c = np.round(np.linspace(0, 1, 101), 2)
rv = np.array([vol(gmv(c * S1 + (1 - c) * lam1 * np.eye(NU)), S2, AU) for c in grid_c])
put(f"U28 halves, predicted / realized volatility: sample {f(100 * vol(w_s, S1, AU), 2, 3)} / "
    f"{f(100 * vol(w_s, S2, AU), 2, 3)}%; shrunk {f(100 * vol(w_c, Sc1, AU), 2, 3)} / {f(100 * vol(w_c, S2, AU), 2, 3)}%; "
    f"long-only {f(100 * vol(w_lo, S1, AU), 2, 3)} / {f(100 * vol(w_lo, S2, AU), 2, 3)}%; single index "
    f"{f(100 * vol(w_f, SF, AU), 2, 3)} / {f(100 * vol(w_f, S2, AU), 2, 3)}%; 1/N {f(100 * vol(wN, S1, AU), 2, 3)} / "
    f"{f(100 * vol(wN, S2, AU), 2, 3)}%; best c in hindsight {grid_c[int(np.argmin(rv))]:.2f} "
    f"({f(100 * float(rv.min()), 2, 3)}%); gross exposure sample {f(float(np.abs(w_s).sum()), 2)}")       # 19
lines = []
for T in (20, 30, 60, 120, 250, 504, 2191):
    x = X1[-T:]
    S = cov0(x)
    rk = int(np.linalg.matrix_rank(S))
    c = c_lw(x)
    lam = float(np.trace(S)) / NU
    wl = gmv(shrunk(x))
    ev = np.linalg.eigvalsh(S)
    kc = (c * ev[-1] + (1 - c) * lam) / (c * ev[0] + (1 - c) * lam)
    cg = grid_c[:-1] if rk < NU else grid_c
    rvT = np.array([vol(gmv(cc * S + (1 - cc) * lam * np.eye(NU)), S2, AU) for cc in cg])
    head = f"T {T} ({s.dates[H - T]} .. {s.dates[H - 1]}, rank {rk}): c_hat {f(c, 3)}"
    k_case = (1, 2) if T == 30 else (2,)          # the case box prints T = 30's realized volatilities at 1 dp
    if rk == NU:
        ws = gmv(S)
        body = (f"kappa {f(ev[-1] / ev[0], 0)} -> {f(kc, 1)}; sample predicted {f(100 * vol(ws, S, AU), 2)}%, "
                f"realized {f(100 * vol(ws, S2, AU), *k_case)}%, gross {f(float(np.abs(ws).sum()), 2)}")
    else:
        wp = np.linalg.pinv(S) @ np.ones(NU)
        wp /= wp.sum()
        qn = np.linalg.eigh(S)[1][:, :NU - rk]       # an orthonormal basis of S's null space
        p1 = qn @ (qn.T @ np.ones(NU))
        w0 = p1 / p1.sum()
        v0 = float(w0 @ S @ w0)                       # zero up to rounding; its printed digits would be noise
        assert abs(v0) < 1e-12 * lam, v0
        body = (f"kappa (shrunk) {f(kc, 1)}; sample singular: the part of 1 outside S's column space has "
                f"{f(float(np.linalg.norm(p1)) / sqrt(NU), 2)} of 1's length, so w = P1 / 1'P1 is fully invested "
                f"with predicted variance 0 to rounding (below 1e-12 of the mean eigenvalue; the minimum is 0, not "
                f"unique); pseudoinverse (the minimum within the column space) predicted "
                f"{f(100 * vol(wp, S, AU), 2)}%, realized {f(100 * vol(wp, S2, AU), 2)}%, gross "
                f"{f(float(np.abs(wp).sum()), 2)}")
    lines.append(f"{head}; {body}; shrunk realized {f(100 * vol(wl, S2, AU), *k_case)}%, gross "
                 f"{f(float(np.abs(wl).sum()), 2)}; best c in hindsight {cg[int(np.argmin(rvT))]:.2f} "
                 f"({f(100 * float(rvT.min()), 2)}%)")
put(" | ".join(lines))                                                                                    # 20

# experiment 3: U28's first-half matrix as the truth
L1 = np.linalg.cholesky(S1)
rng3 = np.random.default_rng([3, SEED])
n3 = 1_000
w_true = gmv(S1)
rows3 = []
for T in (20, 30, 60, 120, 250, 504, 2191):
    vs, vl, vo, cc = [], [], [], []
    for _ in range(n3):
        x = rng3.standard_normal((T, NU)) @ L1.T
        S = cov0(x)
        lw = LedoitWolf(assume_centered=False).fit(x)
        cc.append(1 - float(lw.shrinkage_))
        vl.append(vol(gmv(np.asarray(lw.covariance_, dtype=np.float64)), S1, AU))
        if T > NU:
            vs.append(vol(gmv(S), S1, AU))
            vo.append(vol(minvar(AU * S, "experiment 3"), S1, AU))
    part = [f"shrunk {mc(100 * float(np.mean(vl)), 100 * float(np.std(vl)) / sqrt(n3))}%"]
    if vs:
        dlo = 100 * (np.array(vo) - np.array(vl))
        part.insert(0, f"sample {mc(100 * float(np.mean(vs)), 100 * float(np.std(vs)) / sqrt(n3))}%")
        part.append(f"long-only {mc(100 * float(np.mean(vo)), 100 * float(np.std(vo)) / sqrt(n3))}%; long-only "
                    f"minus shrunk, paired, {mc(float(dlo.mean()), float(dlo.std()) / sqrt(n3), plus=True)} points")
    ccm, ccs = mean_se(np.array(cc))
    part.append(f"mean c_hat {mc(ccm, ccs)}")
    rows3.append(f"T {T}: " + ", ".join(part))
put(f"experiment 3 ({n3} samples per length), mean true volatility: " + "; ".join(rows3)
    + f"; true minimum {f(100 * vol(w_true, S1, AU), 2, 3)}%, 1/N {f(100 * vol(wN, S1, AU), 2, 3)}%")       # 21

# Jagannathan and Ma on U28's first half
act = w_lo > ZERO
g = S1 @ w_lo
nu0 = float(g[act].mean())
nu = g - nu0
gap_act = float(np.abs(nu[act]).max())
nu[act] = 0.0
assert nu.min() > -1e-12 * abs(nu0), "a multiplier is negative"
S_nu = S1 - (np.outer(nu, np.ones(NU)) + np.outer(np.ones(NU), nu))
w_nu = gmv(S_nu)
assert np.abs(w_nu - w_lo).max() < BOUND          # rounding noise: assert the bound, print the bound
assert gap_act < BOUND * abs(nu0), gap_act
red = 2 * nu / np.diag(S1)
put(f"long-only minimum variance on the first half: {int(act.sum())} sectors held ("
    + ", ".join(nm for nm, a_ in zip(s.names, act, strict=True) if a_) + f"), {int((~act).sum())} constraints bind; "
    f"S_nu's minimum-variance weights equal them below {BOUND:.0e} (stationarity gap below {BOUND:.0e} of nu_0); "
    f"smallest eigenvalue of A S_nu {f(AU * float(np.linalg.eigvalsh(S_nu)[0]), 4, 5)}; largest variance reduction "
    f"2 nu_i / s_i^2 {f(100 * float(red.max()), 1)}% ({s.names[int(np.argmax(red))]})")                # 22

yv = cp.Variable(NU)
cons = [np.ones(NU) @ yv == 1, yv >= 0]
prob = cp.Problem(cp.Minimize(cp.quad_form(yv, cp.psd_wrap(AU * S1))), cons)
prob.solve(solver=cp.CLARABEL, **CLARABEL_OPTS)
assert prob.status == "optimal", prob.status
wcv = yv.value
dual = cons[1].dual_value
assert wcv is not None and dual is not None
nu_cv = np.asarray(dual, dtype=np.float64) / (2 * AU)       # cvxpy's multipliers of y >= 0 for min y'(A S)y
put(f"cvxpy check (CLARABEL, status {prob.status}): largest weight gap to the NNLS weights "
    f"{np.abs(np.asarray(wcv, dtype=np.float64) - w_lo).max():.1e}; multipliers / (2A) against nu: largest gap "
    f"{np.abs(nu_cv - nu).max() / nu.max():.1e} of the largest nu")                                      # 23

# ---------------------------------------------------------------- Black-Litterman on the first window
wref = np.array([R2[k] for k in F5])
e_a = mu_a - RF
mex = float(wref @ e_a)
vref = float(wref @ S_a @ wref)
dl = mex / vref
e_eq = dl * S_a @ wref
put(f"R2 on the first window: mean excess {f(100 * mex, 2, 3)}%, volatility {f(100 * sqrt(vref), 2, 3)}%, Sharpe "
    f"{f(mex / sqrt(vref), 2, 3)}; delta = mean excess / variance {f(dl, 2)}; e_eq = delta S w_ref "
    f"{pct(e_eq, 2)}%")                                                                                  # 24
K = np.array([-1.0, 1.0, 0.0, 0.0, 0.0])
b = float(K @ e_a)
KSK = float(K @ S_a @ K)
kq = float(K @ e_eq)
bl = []
for c in (0.0, 0.25, 0.5, 0.75, 1.0):
    ebl = e_eq + S_a @ K * c * (b - kq) / KSK
    fbl = np.linalg.solve(S_a, ebl) / dl
    assert np.abs(fbl - (wref + K * c * (b - kq) / (dl * KSK))).max() < 1e-12
    bl.append(f"c {c:.2f}: {pct(fbl, 1)}% (sum {f(100 * float(fbl.sum()), 1)}%)")
fp = np.linalg.solve(S_a, e_a) / dl
put(f"view K = (-1, 1, 0, 0, 0): b = K e_hat {f(100 * b, 2, 3)} points, K e_eq {f(100 * kq, 2, 3)} points, "
    f"sqrt(K S K') {f(100 * sqrt(KSK), 2, 3)}%; c = T/(T + n0), n0 = {WINDOW} gives c 0.5; f_BL " + "; ".join(bl)
    + f"; plug-in S^-1 e_hat / delta {pct(fp, 1)}% (sum {f(100 * float(fp.sum()), 1)}%)")                 # 25
f_all = np.linalg.solve(S_a, 0.5 * e_a + 0.5 * e_eq) / dl
assert np.abs(f_all - (0.5 * fp + 0.5 * wref)).max() < BOUND
put(f"all five window means as views, c 0.5: f {pct(f_all, 1)}% (sum {f(100 * float(f_all.sum()), 1)}%), the average "
    f"of the plug-in and w_ref below {BOUND:.0e}")                                                      # 26

# experiment 4: resampled long-only maximum-Sharpe weights
rng4 = np.random.default_rng([4, SEED])
B4 = 1_000
Wb = np.empty((B4, N5))
fallback = 0
for i in range(B4):
    xb = x0[rng4.integers(0, WINDOW, WINDOW)]
    Sb = A * cov0(xb)
    wb = maxsharpe(Sb, A * xb.mean(axis=0) - RF, "experiment 4")
    if wb is None:
        fallback += 1
        wb = minvar(Sb, "experiment 4 fallback")
    Wb[i] = wb
pz = (Wb < ZERO).mean(axis=0)
mw, sw = Wb.mean(axis=0), Wb.std(axis=0) / sqrt(B4)
sz = np.sqrt(pz * (1 - pz) / B4)
put(f"experiment 4 ({B4} iid bootstrap resamples of the first window): mean weights, in percent, "
    + ", ".join(f"{F5[j]} {mc(100 * float(mw[j]), 100 * float(sw[j]))}" for j in range(N5))
    + f"; SDs {pct(Wb.std(axis=0), 1)} points; share of resamples with a zero weight, in percent, "
    + ", ".join(f"{F5[j]} {mc(100 * float(pz[j]), 100 * float(sz[j]))}" for j in range(N5))
    + f"; no fund above r_f in {fallback} (long-only minimum variance held)")                            # 27

# ---------------------------------------------------------------- repairing LM10's C_pw
Cp = np.array([[1.0, 0.982, 0.199], [0.982, 1.0, -0.444], [0.199, -0.444, 1.0]])
evp, Qp = np.linalg.eigh(Cp)
cmax = 1 / (1 - evp[0])
Csh = cmax * Cp + (1 - cmax) * np.eye(3)
Ccl = Qp @ np.diag(np.clip(evp, 0, None)) @ Qp.T
dg = np.sqrt(np.diag(Ccl))
Ccl = Ccl / np.outer(dg, dg)
Y = Cp.copy()
dS = np.zeros_like(Cp)
for it in range(100_000):                       # Higham's (2002b) alternating projections with Dykstra's correction
    Rm = Y - dS
    wv, Vv = np.linalg.eigh(Rm)
    Xp = Vv @ np.diag(np.clip(wv, 0, None)) @ Vv.T
    dS = Xp - Rm
    Yn = Xp.copy()
    np.fill_diagonal(Yn, 1.0)
    done = float(np.abs(Yn - Y).max()) < 1e-15   # the stopping rule tests the unit-diagonal iterate Y
    Y = Yn
    if done:
        break
Xc = cp.Variable((3, 3), symmetric=True)        # second solver: min |X - C_pw|_F^2, X PSD, unit diagonal
pc = cp.Problem(cp.Minimize(cp.sum_squares(Xc - Cp)), [Xc >> 0, cp.diag(Xc) == 1])
pc.solve(solver=cp.CLARABEL, **CONE_OPTS)
assert pc.status == "optimal", pc.status
assert Xc.value is not None
gap_ncm = float(np.abs(np.asarray(Xc.value, dtype=np.float64) - Y).max())
off = [(0, 1), (0, 2), (1, 2)]


def offd(M: Mat) -> str:
    return "(" + ", ".join(f(M[i, j], 3) for i, j in off) + ")"


put(f"C_pw from lm10.md's printed entries: eigenvalues ({', '.join(f(v, 3, 4) for v in evp)}), det {f(np.linalg.det(Cp), 3)}; "
    f"largest c keeping c C + (1-c) I PSD 1/(1 - lambda_3) {f(cmax, 3, 4)}, giving {offd(Csh)}; clipped and rescaled "
    f"{offd(Ccl)}; nearest correlation matrix {offd(Y)} (smallest eigenvalue {np.linalg.eigvalsh(Y)[0]:.1e}, PSD "
    f"to rounding; {it + 1} iterations until no entry of the unit-diagonal iterate moves by 1e-15; cvxpy CLARABEL "
    f"{pc.status} at 1e-10 agrees to {gap_ncm:.1e}); Frobenius distances to C_pw: shrunk "
    f"{f(np.sqrt(fro2(Csh - Cp)), 3)}, clipped "
    f"{f(np.sqrt(fro2(Ccl - Cp)), 3)}, nearest {f(np.sqrt(fro2(Y - Cp)), 3)}")                         # 28
put(f"single-index matrix: {2 * NU + 1} parameters against {NU * (NU + 1) // 2}; kappa {f(kappa(SF), 1)}; residual "
    f"correlations of the first half: mean {f(float(np.corrcoef(res, rowvar=False)[np.triu_indices(NU, 1)].mean()), 3)}")  # 29

# ---------------------------------------------------------------- problems and knowledge checks
put(f"P1 (sigma 20% a year, 4 years, A 243): sigma/sqrt(years) {f(20 / sqrt(4), 1)} points; sigma/years "
    f"{f(20 / 4, 1)}; sigma/sqrt(T days) {f(20 / sqrt(4 * 243), 2)}")                                     # 30
p2 = [(0.8 * lv + 0.2 * 2.5) for lv in (4.0, 1.0)]
put(f"P2 (eigenvalues 4 and 1, c 0.8): shrunk eigenvalues {f(p2[0], 2)}, {f(p2[1], 2)}; kappa {f(p2[0] / p2[1], 2)}; "
    f"unchanged 4; c x kappa {f(0.8 * 4, 2)}")                                                              # 31
put(f"P3 (Sigma = sigma^2 I, N 10, T 250): c* 0; T/(T + N) {f(250 / 260, 3)}")                           # 32
put(f"P4 (T 504, n0 1512): c {f(504 / (504 + 1512), 2)}; view 4%, implied 0%: posterior "
    f"{f(100 * (0.25 * 0.04 + 0.75 * 0.0), 1)}%; weights swapped {f(100 * (0.75 * 0.04), 1)}%; equal "
    f"{f(100 * 0.5 * 0.04, 1)}%")                                                                         # 33
put(f"P5 (sigma_1 20%, rho 0.9): (S^-1)_11 = VIF / sigma_1^2 {f(1 / (0.04 * (1 - 0.81)), 1)}; 1/sigma_1^2 "
    f"{f(1 / 0.04, 1)}; 1/(sigma_1^2 (1 - rho)) {f(1 / (0.04 * 0.1), 1)}; VIF {f(1 / (1 - 0.81), 3)}")   # 34
put("P6 (nu_3 0.0002 daily): variance reduced by 2 nu_3 = 0.0004; each covariance with asset 3 by nu_3 + nu_j")  # 35
Sp = np.diag([4.0, 1.0])
d7 = fro2(Sp - 2.5 * np.eye(2))
n7 = normal_noise(Sp, 100)
put(f"P7 (Sigma diag(4, 1), T 100, normal, mean known): |Sigma - lam_bar I|^2 {f(d7, 2)}; noise (18.4) {f(n7, 2)}; "
    f"c* {f(d7 / (d7 + n7), 4)}")                                                                            # 36
S8 = np.array([[1.0, 1.6], [1.6, 4.0]])
w8 = (S8[1, 1] - S8[0, 1]) / (S8[0, 0] + S8[1, 1] - 2 * S8[0, 1])
g8 = S8 @ np.array([1.0, 0.0])
nu8 = np.array([0.0, g8[1] - g8[0]])
S8n = S8 - (np.outer(nu8, np.ones(2)) + np.outer(np.ones(2), nu8))
put(f"P8 (sigma 1 and 2, rho 0.8, daily %): unconstrained weights ({f(w8, 3)}, {f(1 - w8, 3)}); long-only (1, 0); "
    f"nu_0 {f(g8[0], 2)}, nu_2 {f(nu8[1], 2)}; S_nu = [[{f(S8n[0, 0], 2)}, {f(S8n[0, 1], 2)}], [{f(S8n[1, 0], 2)}, "
    f"{f(S8n[1, 1], 2)}]]; its minimum-variance weights {pct(gmv(S8n), 1)}%")                               # 37
S9 = np.diag([0.04, 0.01])
w9 = np.array([0.5, 0.5])
eq9 = 4 * S9 @ w9
K9 = np.array([-1.0, 1.0])
th9 = 0.5 * (0.0 - float(K9 @ eq9)) / float(K9 @ S9 @ K9)
e9 = eq9 + S9 @ K9 * th9
f9 = np.linalg.solve(S9, e9) / 4
put(f"P9 (sigma 20% and 10%, rho 0, w_ref 50/50, delta 4, view 0 on fund 2 minus fund 1, c 0.5): e_eq {pct(eq9, 1)}%; "
    f"K e_eq {f(100 * float(K9 @ eq9), 1)}; e_BL {pct(e9, 1)}%; f_BL {pct(f9, 1)}%")                      # 38
se646 = f(100 * se_mean[1], 1)
put(f"KC 2: doubling the years divides the SE of an annual mean by sqrt 2: 00646 {se646} -> "
    f"{f(100 * se_mean[1] / sqrt(2), 1)} points (A28-27's SE at its printed 1 dp); doubling the days in the same "
    f"years leaves it at {se646}")                                                                         # 39
put(f"KC 4 (rho 0.9, c 0.5 toward I): eigenvalues 1.9 and 0.1 -> {f(0.5 * 1.9 + 0.5, 2)} and {f(0.5 * 0.1 + 0.5, 2)}; "
    f"kappa {f(1.9 / 0.1, 1)} -> {f((0.5 * 1.9 + 0.5) / (0.5 * 0.1 + 0.5), 2)}")                        # 40
put("withdrawn (it served Open question 3; decision D fixed delta = 9.74, and the brief prints no other delta)")  # 41
assert len(OUT) == 41 and sorted(LATE) == [42, 43]
print("\n".join(OUT + [LATE[k] for k in sorted(LATE)]))
