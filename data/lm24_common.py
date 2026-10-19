"""Shared inputs and formulas of LM24's scripts (Bayesian Inference and Shrinkage).

Imported by data/lm24_numbers.py and data/lm24_charts.py. Run on its own, it prints a summary of the two samples:
    PYTHONUTF8=1 uv run python data/lm24_common.py

Samples (never mixed in one statistic; plans/vol-4.md, "Data"):
  * TR23: data/processed/vol3_taiex.parquet (built and checked by data/vol3_series.py from FinMind's
    TaiwanStockTotalReturnIndex, data_id TAIEX, retrieved 2026-10-18): 5,850 closes 2003-01-02 -> 2026-10-08, T = 5,849
    simple returns R_t (the parquet's column R), years = calendar days / 365.25, A = T / years = 246.12.
  * U28: data/lm10_series.py's u28() (closes built and repaired by data/vol2_series.py from FinMind's TaiwanStockPrice):
    the 28 leaf TWSE sector price indices (no dividends), 4,382 returns 2008-12-02 -> 2026-10-08, A = 245.4794, used to
    annualize both of LM11's halves (the first and the last 2,191 returns), and the TAIEX price index on the same dates.

Conventions (AUTHORING section 6 and plans/vol-4.md, the LM24 brief):
  * Divisors: s and every sector's s_i divide by the returns used (NumPy ddof=0, passed explicitly); s_u (LM21's
    t-stat only) by T - 1. The cross-sectional SD of 28 means divides by 28.
  * Normal model with known variance: sigma = s, standard error s / sqrt(T) (LM20's (20.2)); prior N(mu0, sigma0^2),
    centred at zero unless stated; the data's weight c = sigma0^2 / (sigma0^2 + s^2 / T); posterior mean
    mu0 + c (Rbar - mu0); posterior SD sqrt(c) s / sqrt(T). "A sigma0 = 10 points" is a prior SD of 0.10 on A mu.
  * Kelly: r_f = 0; fhat = Rbar / s^2 (LM20's); Bayes fraction f_B = E[mu | data] / s^2 = c fhat for a prior centred
    at zero. Exact fractions are roots of (4.5) on TR23's returns shifted by one constant to the posterior mean (LM4's
    band method); with no shift the root is fhat* (LM17's 4.1381). The posterior-integrated fraction maximizes the
    posterior expectation of mean_t ln(1 + f (R_t - Rbar + mu)), mu ~ N(c Rbar, c s^2 / T), the expectation by 60-node
    Gauss-Hermite quadrature (numpy.polynomial.hermite_e.hermegauss, weights normalized to sum 1).
  * James-Stein (24.4), positive part toward the grand mean: 1 - c_hat = (N - 3) v / sum_i (m_i - mbar)^2, with v the
    average over the 28 sectors of s_i^2 / T (one common noise variance, an approximation). "Common removed" replaces
    each day's 28 returns by their deviations from that day's cross-sectional mean; Problem 11 subtracts the TAIEX price
    index's return instead.
  * Out-of-sample miss: root mean square over the 28 sectors of (estimate from one half - mean of the other half),
    annualized by A = 245.4794; "deviations" removes each half's own grand mean first.
  * Beta probabilities: integer parameters, so Pr(Beta(a, b) <= x) = Pr(Bin(a + b - 1, x) >= a) is exact with Fraction,
    checked against scipy.stats.beta.
  * Simulation (AUTHORING section 8): experiment e creates rng = np.random.default_rng([e, 20261011]) once, at its start.
    Experiment 1 (Example "exp1"): one 10,000 x 28 array of true means (standard_normal), then one 10,000 x 28 array of
    noise. Experiment 2 (Problem 10): for each spread 0, 1, 3 in that order, one 20,000 x 28 array of true means drawn as
    spread * standard_normal (drawn even at spread 0), then one 20,000 x 28 array of noise. A Monte Carlo average is
    printed with its standard error, the SD of the per-cross-section values with divisor n over sqrt(n).
"""
import sys
from fractions import Fraction
from math import comb, sqrt
from pathlib import Path

import numpy as np
import polars as pl
from numpy.typing import NDArray
from scipy import optimize, stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lm10_series import u28

Vec = NDArray[np.float64]
SEED = 20261011
EPS = 1e-12
Z975 = float(stats.norm.ppf(0.975))

# ---------------------------------------------------------------- TR23
PARQUET = HERE / "processed" / "vol3_taiex.parquet"
assert PARQUET.exists(), "run data/vol3_series.py first"
_df = pl.read_parquet(PARQUET).sort("date")
DATES_ALL: list[str] = [str(d) for d in _df["date"].to_list()]
assert _df["R"][0] is None and len(set(DATES_ALL)) == len(DATES_ALL)
R: Vec = np.asarray(_df["R"].to_numpy()[1:], dtype=np.float64)
_tr = np.asarray(_df["tr"].to_numpy(), dtype=np.float64)
assert np.allclose(R, _tr[1:] / _tr[:-1] - 1, rtol=0, atol=1e-15)
T = len(R)
DAYS = (_df["date"][-1] - _df["date"][0]).days
YEARS = DAYS / 365.25
A = T / YEARS
RB = float(R.mean())
S = float(R.std(ddof=0))
S_U = float(R.std(ddof=1))
SE = S / sqrt(T)
FHAT = RB / S**2
VOL = S * sqrt(A)
assert (len(DATES_ALL), T, DATES_ALL[0], DATES_ALL[-1]) == (5850, 5849, "2003-01-02", "2026-10-08")


def weight(a_sigma0: float) -> float:
    """The data's weight c for a prior SD a_sigma0 on the annual mean A mu (a fraction: 0.10 is 10 points)."""
    s0 = a_sigma0 / A
    return s0**2 / (s0**2 + SE**2)


def post(c: float, a_mu0: float = 0.0) -> tuple[float, float]:
    """Posterior mean and SD of the daily mu for the data's weight c and a prior centred at a_mu0 (annual)."""
    mu0 = a_mu0 / A
    return mu0 + c * (RB - mu0), sqrt(c) * SE


def kelly_exact(mean_target: float) -> float:
    """Root of (4.5) on TR23's returns shifted so that their mean is mean_target (LM4's band method)."""
    x = R - RB + mean_target

    def d(f: float) -> float:
        return float((x / (1 + f * x)).mean())

    return float(optimize.brentq(d, 1e-6, 1 / abs(float(x.min())) - 1e-6, xtol=1e-14))


_XG, _WG = np.polynomial.hermite_e.hermegauss(60)
_WG = _WG / _WG.sum()


def kelly_bayes_quad(c: float) -> float:
    """The f maximizing the posterior expectation of mean_t ln(1 + f (R_t - Rbar + mu)), by 60-node quadrature."""
    m, sd = post(c)
    shifts = m + sd * _XG - RB

    def d(f: float) -> float:
        tot = 0.0
        for w, sh in zip(_WG, shifts):
            x = R + sh
            tot += float(w) * float((x / (1 + f * x)).mean())
        return tot

    return float(optimize.brentq(d, 1e-6, 8.0, xtol=1e-14))


def growth(f: float, m: float) -> float:
    """Posterior-expected annual log growth of the fixed fraction f in the model (GBM), posterior mean m per day."""
    return A * (f * m - f**2 * S**2 / 2)


# ---------------------------------------------------------------- U28 and LM11's halves
SMP = u28()
X: NDArray[np.float64] = np.asarray(SMP.X, dtype=np.float64)
NAMES: list[str] = list(SMP.names)
A28 = float(SMP.A)
T28, N = X.shape
H = T28 // 2
assert (T28, N, H) == (4382, 28, 2191)
assert (SMP.dates[0], SMP.dates[H - 1], SMP.dates[H], SMP.dates[-1]) == (
    "2008-12-02", "2017-10-06", "2017-10-11", "2026-10-08")
TX: Vec = np.asarray(SMP.taiex, dtype=np.float64)
XD = X - X.mean(axis=1, keepdims=True)      # common component (each day's cross-sectional mean) removed
XE = X - TX[:, None]                        # TAIEX price index removed (Problem 11)
M1, M2 = X[:H].mean(axis=0), X[H:].mean(axis=0)
A1, A2 = A28 * M1, A28 * M2


def rank(a: Vec, i: int) -> int:
    """Rank of entry i, 1 = highest."""
    return int((a > a[i]).sum()) + 1


def js(x_est: NDArray[np.float64], ddof: int = 0) -> tuple[float, float, float, float]:
    """Annual noise SD of a mean; annual cross-sectional SD (divisor N) of the means; 1 - c_hat; c_hat."""
    n = x_est.shape[0]
    m = x_est.mean(axis=0)
    noise = float((x_est.var(axis=0, ddof=ddof) / n).mean())
    ss = float(((m - m.mean()) ** 2).sum())
    b = (N - 3) * noise / ss
    return A28 * sqrt(noise), A28 * float(m.std(ddof=0)), b, max(0.0, 1 - b)


def oos(m_est: Vec, m_judge: Vec, c: float, deviations: bool = False) -> float:
    """Annualized root mean square error of the shrunk estimate against the other half's means."""
    est = m_est.mean() + c * (m_est - m_est.mean())
    if deviations:
        return A28 * sqrt(float((((est - m_est.mean()) - (m_judge - m_judge.mean())) ** 2).mean()))
    return A28 * sqrt(float(((est - m_judge) ** 2).mean()))


def c_opt(m_est: Vec, m_judge: Vec) -> float:
    """Slope of the judging half's deviations on the estimating half's: the best weight in hindsight."""
    d1, d2 = m_est - m_est.mean(), m_judge - m_judge.mean()
    return float(d1 @ d2 / (d1 @ d1))


# ---------------------------------------------------------------- beta laws, exact
P55 = Fraction(11, 20)


def beta_cdf(a: int, b: int, x: Fraction) -> Fraction:
    """Pr(Beta(a, b) <= x) for integer a, b: the probability of at least a successes in a + b - 1 trials."""
    n = a + b - 1
    return sum((comb(n, k) * x**k * (1 - x) ** (n - k) for k in range(a, n + 1)), Fraction(0))


def beta_sf(a: int, b: int, x: Fraction) -> Fraction:
    """Pr(Beta(a, b) > x), exact, checked against SciPy."""
    p = 1 - beta_cdf(a, b, x)
    assert abs(float(p) - float(stats.beta.sf(float(x), a, b))) < 1e-12
    return p


# ---------------------------------------------------------------- the two simulated experiments
def _errors(mu: NDArray[np.float64], x: NDArray[np.float64]) -> dict[str, Vec]:
    gm = x.mean(axis=1, keepdims=True)
    ch = 1 - (N - 3) / ((x - gm) ** 2).sum(axis=1, keepdims=True)
    return {
        "raw": ((x - mu) ** 2).sum(axis=1),
        "js": ((gm + ch * (x - gm) - mu) ** 2).sum(axis=1),
        "pp": ((gm + np.maximum(ch, 0) * (x - gm) - mu) ** 2).sum(axis=1),
        "bayes": ((0.5 * x - mu) ** 2).sum(axis=1),
        "c_pp": np.maximum(ch, 0)[:, 0],
        "c_js": ch[:, 0],
    }


def experiment1() -> dict[str, Vec]:
    """Experiment 1: 10,000 cross-sections of 28 means, prior spread 1, noise 1."""
    rng = np.random.default_rng([1, SEED])
    mu = rng.standard_normal((10_000, N))      # one 10,000 x 28 array of true means first,
    x = mu + rng.standard_normal((10_000, N))  # then one 10,000 x 28 array of noise
    return _errors(mu, x)


def experiment2() -> dict[float, dict[str, Vec]]:
    """Experiment 2: 20,000 cross-sections at each spread 0, 1, 3, in that order, from one generator."""
    rng = np.random.default_rng([2, SEED])
    out: dict[float, dict[str, Vec]] = {}
    for spread in (0.0, 1.0, 3.0):
        mu = spread * rng.standard_normal((20_000, N))  # drawn even at spread 0, so the draws are used up
        x = mu + rng.standard_normal((20_000, N))
        out[spread] = _errors(mu, x)
    return out


def mc_mean_se(e: Vec) -> tuple[float, float]:
    """Monte Carlo mean and its standard error (SD with divisor n over sqrt(n))."""
    return float(e.mean()), float(e.std(ddof=0)) / sqrt(len(e))


if __name__ == "__main__":
    print(f"TR23: T = {T}, {DATES_ALL[0]} -> {DATES_ALL[-1]}, years {YEARS:.6f}, A {A:.6f}, Rbar {RB:.8f}, s {S:.8f}")
    print(f"U28: T = {T28}, N = {N}, halves {H} + {T28 - H}, A {A28:.7f}")
