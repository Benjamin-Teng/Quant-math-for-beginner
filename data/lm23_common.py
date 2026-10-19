"""Shared computations of LM23 (Linear Regression), imported by data/lm23_numbers.py and data/lm23_charts.py.

Run on its own for a short summary:  uv run python data/lm23_common.py
(after data/vol2_series.py, data/vol3_series.py, data/build_series.py and data/vol4_series.py have built the files below)

Inputs (data/processed/, never data/raw/ directly):
  * U28 (Volume II): data/lm10_series.py's u28(), which reads vol2_closes.parquet (FinMind TaiwanStockPrice, retrieved
    11 October 2026, copied closes repaired by data/vol2_series.py): the 28 leaf TWSE sector price indices and the TAIEX
    price index, closes 2008-12-01 .. 2026-10-08, T = 4,382 simple daily price returns (2008-12-02 .. 2026-10-08),
    years = calendar days / 365.25, A = T / years = 245.4794. Halves: the first and last 2,191 returns (LM11's).
    Electronic (an aggregate outside U28) comes from the same parquet on the same dates; the factor
    R_el - R_mkt is constructed.
  * LM2's 0050/00631L sample: etf_daily_returns.parquet (2,902 common-date total-return pairs, 2014-11-03 ..
    2026-10-08), recomputed under LM23's name.
  * TR23 (Volume III): vol3_taiex.parquet: R - Rp on U28's dates (the TAIEX's dividend yield), and r = ln(1 + R) for
    LM18's model paths (LM18's experiment 3, its own seed default_rng([3, 20261011]), 20 chunks of 500 paths).
  * TX23 (Volume IV): vol4_tx23.parquet (FinMind TaiwanFuturesDaily, retrieved 19 October 2026), one value: the
    settlement price F of the TX contract held from the close of 2026-10-08.

Conventions (as the module states them). OLS with an intercept; d coefficients; s_eps^2 = RSS / (T - d). Classical
SE s_eps^2 (X'X)^-1; White = HC0, (X'X)^-1 (sum e_t^2 x_t x_t') (X'X)^-1 with no degrees-of-freedom factor;
Newey-West with Bartlett weights 1 - k/(L + 1), no small-sample correction, lag L = floor(4 (n/100)^(2/9)) (the book's
rule: statsmodels' default HAC lag, Newey and West's 1994 pilot lag) unless stated. Means, standard deviations,
variances and correlations of data divide by T (ddof=0, passed explicitly). R-squared is (12.4). t-stats and p-values
use the normal reference, two-sided, except the four points of LM12 (t with 2 degrees of freedom). Intercepts in basis
points a day, A times that for a year. One-day regressions on simple returns, 20-day sums on log returns. A sample
autocorrelation is LM19's rho_hat_k (full-sample mean, divisor T in numerator and denominator); a sample quantile is
F_hat^-1(u) (np.quantile method="inverted_cdf"). Counts against a threshold use the guard (|t| > c + 1e-12,
x <= c + 1e-12) and, on two-decimal closes, Fraction. Seeds: LM23's experiment 1 (the correlated null of 28 alpha
t-stats), rng = np.random.default_rng([1, 20261011]) created once, 100,000 draws of standard_normal((B, 28)) @ L.T
with L = np.linalg.cholesky(C), C the residual correlation matrix, and the sectors in U28's column order, Python's
sorted of their FinMind names (ElectricMachinery before ElectricalCable; a case-folded order swaps them). Monte Carlo
SEs: binomial for a probability, SD/sqrt(B) for the mean count, the delta method for the count's SD. LM18's paths keep
LM18's default_rng([3, 20261011]).
"""
import sys
from dataclasses import dataclass
from datetime import date
from fractions import Fraction
from math import floor, sqrt
from pathlib import Path

import numpy as np
import polars as pl
from numpy.typing import NDArray
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lm10_series import FIRST, LAST, u28

PROC = HERE / "processed"
EPS = 1e-12
SEED = 20261011
Vec = NDArray[np.float64]
Mat = NDArray[np.float64]


def nw_lag(n: int) -> int:
    """The book's lag rule, floor(4 (n/100)^(2/9))."""
    return floor(4 * (n / 100) ** (2 / 9))


@dataclass
class Fit:
    b: Vec        # coefficients (intercept first)
    e: Vec        # residuals
    s2: float     # RSS / (T - d)
    se_c: Vec     # classical
    se_w: Vec     # White (HC0)
    se_n: Vec     # Newey-West
    lag: int
    r2: float
    zi: Mat       # (X'X)^-1
    n: int


def long_run(u: Mat, lag: int) -> Mat:
    """sum_t u_t u_t' + sum_{k=1}^{L} (1 - k/(L+1)) (G_k + G_k'), G_k = sum_t u_t u_{t-k}' (no division by T)."""
    s = u.T @ u
    for k in range(1, lag + 1):
        g = u[k:].T @ u[:-k]
        s = s + (1 - k / (lag + 1)) * (g + g.T)
    return s


def ols(y: Vec, z: Mat, lag: int | None = None) -> Fit:
    n, d = z.shape
    zi = np.linalg.inv(z.T @ z)
    b = zi @ (z.T @ y)
    e = y - z @ b
    s2 = float(e @ e) / (n - d)
    u = z * e[:, None]
    lg = nw_lag(n) if lag is None else lag
    vw = zi @ (u.T @ u) @ zi
    vn = zi @ long_run(u, lg) @ zi
    yc = y - y.mean()
    return Fit(b, e, s2, np.sqrt(s2 * np.diag(zi)), np.sqrt(np.diag(vw)), np.sqrt(np.diag(vn)), lg,
               1 - float(e @ e) / float(yc @ yc), zi, n)


def design(*cols: Vec) -> Mat:
    return np.column_stack([np.ones(len(cols[0])), *cols])


def corr(a: Vec, b: Vec) -> float:
    a, b = a - a.mean(), b - b.mean()
    return float(a @ b / sqrt(float(a @ a) * float(b @ b)))


def rho_hat(x: Vec, k: int) -> float:
    """LM19's sample autocorrelation: full-sample mean, divisor T in numerator and denominator."""
    c = x - x.mean()
    return float(c[k:] @ c[:-k] / (c @ c))


def two_sided(t: float) -> float:
    return float(2 * stats.norm.sf(abs(t)))


def window_sums(x: Vec, k: int) -> Vec:
    c = np.concatenate([[0.0], np.cumsum(x)])
    return c[k:] - c[:-k]


# ---------------------------------------------------------------- U28, Electronic
S = u28()
X, MKT, NAMES, DATES = S.X, S.taiex, S.names, S.dates
T = len(MKT)
A = S.A
YEARS = S.years
J = {nm: i for i, nm in enumerate(NAMES)}
H = T // 2
_cl = pl.read_parquet(PROC / "vol2_closes.parquet").sort("date")
SMP = _cl.filter(pl.col("date").is_between(pl.lit(FIRST), pl.lit(LAST)))
CLOSE_DATES = SMP["date"].to_list()
assert CLOSE_DATES[1:] == DATES and CLOSE_DATES == S.close_dates
assert SMP["Electronic"].null_count() == 0
_pe = SMP["Electronic"].to_numpy().astype(float)
EL = _pe[1:] / _pe[:-1] - 1
FX = EL - MKT                                   # the constructed electronics factor
TAIEX_CLOSE = [Fraction(str(v)) for v in SMP["TAIEX"].to_list()]
YRS = np.array([d[:4] for d in DATES])
ZM = design(MKT)
FITS = {nm: ols(X[:, J[nm]], ZM) for nm in NAMES}
SEMI, FIN = FITS["Semiconductor"], FITS["FinancialInsurance"]
SEMI_CLOSE = SMP["Semiconductor"].to_list()

# ---------------------------------------------------------------- LM2's pairs, TR23, TX23
_etf = pl.read_parquet(PROC / "etf_daily_returns.parquet").sort("date")
R50 = _etf["R_0050"].to_numpy().astype(float)
R631 = _etf["R_00631L"].to_numpy().astype(float)
ETF_DATES = [str(d) for d in _etf["date"].to_list()]
TR = pl.read_parquet(PROC / "vol3_taiex.parquet").sort("date")
_trd = {str(d): (a, b) for d, a, b in zip(TR["date"].to_list(), TR["R"].to_list(), TR["Rp"].to_list(), strict=True)}
RT = np.array([_trd[d][0] for d in DATES])
RP = np.array([_trd[d][1] for d in DATES])
QM = A * float((RT - RP).mean())
_tx = pl.read_parquet(PROC / "vol4_tx23.parquet").filter(pl.col("date") == date.fromisoformat(LAST))
assert _tx.height == 1 and float(_tx["S"][0]) == float(TAIEX_CLOSE[-1])
F_LAST, CONTRACT = float(_tx["F"][0]), int(_tx["contract"][0])

# ---------------------------------------------------------------- case
TA = {k: float(SEMI.b[0] / se[0]) for k, se in (("c", SEMI.se_c), ("w", SEMI.se_w), ("n", SEMI.se_n))}
SH1 = ols(X[:H, J["Semiconductor"]], ZM[:H])
SH2 = ols(X[H:, J["Semiconductor"]], ZM[H:])
BETAS = {nm: float(FITS[nm].b[1]) for nm in NAMES}
T_C = {nm: float(FITS[nm].b[0] / FITS[nm].se_c[0]) for nm in NAMES}
T_W = {nm: float(FITS[nm].b[0] / FITS[nm].se_w[0]) for nm in NAMES}
T_N = {nm: float(FITS[nm].b[0] / FITS[nm].se_n[0]) for nm in NAMES}


def beyond(tt: dict[str, float], c: float = 1.96) -> list[str]:
    return [k for k in NAMES if abs(tt[k]) > c + EPS]


# ---------------------------------------------------------------- four points (LM12's)
X4 = np.array([0.0, 1, 2, 3])
Y4 = np.array([1.0, 3, 2, 6])
F4 = ols(Y4, design(X4), lag=0)
T2Q = float(stats.t.ppf(0.975, 2))

# ---------------------------------------------------------------- section 3
MX, SX = float(MKT.mean()), float(MKT.std(ddof=0))
SEMI_SDT = float(SEMI.e.std(ddof=0))
ADJ_R2 = 1 - (1 - SEMI.r2) * (T - 1) / (T - 2)
F_STAT = float(SEMI.b[1] ** 2 / SEMI.se_c[1] ** 2)
Q_T = {df: float(stats.t.ppf(0.975, df)) for df in (4380, 248, 241, 183)}
Q_N = float(stats.norm.ppf(0.975))
K25 = YRS == "2025"
Y25, X25 = X[K25, J["FinancialInsurance"]], MKT[K25]
F25 = ols(Y25, design(X25))
X0 = -0.05
Z0 = np.array([1.0, X0])
H0 = float(Z0 @ F25.zi @ Z0)
YHAT0 = float(Z0 @ F25.b)
SE_FIT, SE_PRED = sqrt(F25.s2 * H0), sqrt(F25.s2 * (1 + H0))
H0_FULL = float(Z0 @ FIN.zi @ Z0)
HALF_FULL = 1.96 * sqrt(FIN.s2 * H0_FULL)
I7 = DATES.index("2025-04-07")
J7 = int(np.flatnonzero(K25).tolist().index(I7))
D25 = design(X25)
HAT25 = np.einsum("ij,jk,ik->i", D25, F25.zi, D25)
H7 = float(HAT25[J7])
assert abs(H7 - (1 / len(X25) + (X25[J7] - X25.mean()) ** 2 / (len(X25) * X25.var(ddof=0)))) < 1e-12
_u25 = D25 * F25.e[:, None]
SE_FIT_WHITE = sqrt(float(Z0 @ (F25.zi @ (_u25.T @ _u25) @ F25.zi) @ Z0))   # White's SE of the fitted value at -5%
J5 = [int(j) for j in np.flatnonzero(X25 <= -0.05 + EPS)]                      # the 2025 days with TAIEX <= -5%
RES5 = [float(F25.e[j] / sqrt(F25.s2)) for j in J5]                            # their residuals in units of s_eps
OUT5 = [bool(abs(F25.e[j]) > 1.96 * sqrt(F25.s2 * (1 + HAT25[j]))) for j in J5]  # outside the 95% prediction band
_keep = np.ones(len(X25), dtype=bool)
_keep[J7] = False
F25B = ols(Y25[_keep], design(X25[_keep]))
R7 = TAIEX_CLOSE[I7 + 1] / TAIEX_CLOSE[I7] - 1
_r_all = [TAIEX_CLOSE[i + 1] / TAIEX_CLOSE[i] - 1 for i in range(T)]
assert R7 == min(_r_all) and abs(float(R7) - MKT[I7]) < 1e-15
N5 = sum(1 for i in np.flatnonzero(K25) if _r_all[i] <= Fraction(-5, 100))
assert N5 == int((X25 <= -0.05 + EPS).sum())
T_B1 = {"c": float((SEMI.b[1] - 1) / SEMI.se_c[1]), "n": float((SEMI.b[1] - 1) / SEMI.se_n[1]),
        "n0": float(SEMI.b[1] / SEMI.se_n[1])}

# ---------------------------------------------------------------- section 4: LM18's paths (LM18's experiment 3)
RTR = TR["R"].to_numpy()[1:].astype(float)
_rtr = np.log1p(RTR)
_years_tr = (date.fromisoformat(str(TR["date"][-1])) - date.fromisoformat(str(TR["date"][0]))).days / 365.25
M5 = round(5 * len(RTR) / _years_tr)
RBAR_TR, SR_TR = float(_rtr.mean()), float(_rtr.std(ddof=0))
_g3 = np.random.default_rng([3, SEED])
S3 = np.empty(10_000)
for _c in range(0, 10_000, 500):
    S3[_c:_c + 500] = (RBAR_TR + SR_TR * _g3.standard_normal((500, M5))).sum(axis=1)
G3 = np.exp(S3)
F18 = ols(G3, design(S3), lag=0)
_batch = []
for _b in range(20):
    _sl = slice(_b * 500, (_b + 1) * 500)
    _cv = np.cov(G3[_sl], S3[_sl], ddof=0)
    _batch.append(_cv[0, 1] / _cv[1, 1])
BSE = float(np.std(_batch, ddof=0) / sqrt(20))
_mu_s, _v_s = M5 * RBAR_TR, M5 * SR_TR**2
_nodes, _wts = np.polynomial.hermite_e.hermegauss(200)
_wts = _wts / _wts.sum()
_sq = _mu_s + sqrt(_v_s) * _nodes
BETA_MODEL = float(np.exp(_mu_s + _v_s / 2))
_eq = np.exp(_sq) - BETA_MODEL - BETA_MODEL * (_sq - _mu_s)
SE_SAND = sqrt(float((_wts * (_sq - _mu_s) ** 2 * _eq**2).sum()) / (10_000 * _v_s**2))
SE_CLASS_MODEL = sqrt(float((_wts * _eq**2).sum()) / (10_000 * _v_s))
TQ1, TQ2 = (float(v) for v in np.quantile(S3, [1 / 3, 2 / 3], method="inverted_cdf"))
_grp = [S3 <= TQ1, (S3 > TQ1) & (S3 <= TQ2), S3 > TQ2]
TERC = [sqrt(float(np.mean(F18.e[g] ** 2))) for g in _grp]
TERC_N = [int(g.sum()) for g in _grp]
RATIO_W = {nm: float(FITS[nm].se_w[1] / FITS[nm].se_c[1]) for nm in NAMES}
RATIO_N = {nm: float(FITS[nm].se_n[1] / FITS[nm].se_c[1]) for nm in NAMES}
F16 = ols(X[:, J["FinancialInsurance"]], design(X[:, J["Semiconductor"]]))

# ---------------------------------------------------------------- section 5: overlapping 20-day sums
M20 = 20
LX, LMK = np.log1p(X), np.log1p(MKT)


@dataclass
class Overlap:
    daily: Fit
    ov: Fit
    ov38: Fit
    non: Fit
    offs: list[float]
    nwin: int


def overlap(nm: str) -> Overlap:
    y1 = LX[:, J[nm]]
    fd = ols(y1, design(LMK), lag=0)
    yo, xo = window_sums(y1, M20), window_sums(LMK, M20)
    zo = design(xo)
    fo = ols(yo, zo, lag=M20 - 1)
    fo2 = ols(yo, zo, lag=2 * (M20 - 1))
    nwin = T // M20
    fn = ols(y1[: nwin * M20].reshape(nwin, M20).sum(1), design(LMK[: nwin * M20].reshape(nwin, M20).sum(1)), lag=0)
    offs = []
    for o in range(M20):
        nn = (T - o) // M20
        offs.append(float(ols(y1[o:o + nn * M20].reshape(nn, M20).sum(1),
                              design(LMK[o:o + nn * M20].reshape(nn, M20).sum(1)), lag=0).b[1]))
    return Overlap(fd, fo, fo2, fn, offs, nwin)


OV = {nm: overlap(nm) for nm in ("Semiconductor", "FinancialInsurance", "Food")}
OVS = OV["Semiconductor"]
RHO_OV = {k: rho_hat(OVS.ov.e, k) for k in (1, 10, 19, 20)}


def iid_overlap_factor(m: int, lag: int | None = None) -> float:
    """Model: daily errors and regressor sums of m iid days, independent of each other. The products' autocovariance
    is (m - k)^2 for k < m (times sigma_eps^2 sigma_x^2), so the true variance of the overlapping slope over the
    classical one is sum_k (m - |k|)^2 / m^2 = (2 m^2 + 1) / (3 m); with Bartlett weights at lag L, the Newey-West
    estimate's large-T limit keeps (1 - k/(L+1)) of each term."""
    if lag is None:
        tot = m * m + 2 * sum((m - k) ** 2 for k in range(1, m))
    else:
        tot = m * m + 2 * sum((1 - k / (lag + 1)) * (m - k) ** 2 for k in range(1, min(lag, m - 1) + 1))
    return sqrt(tot / (m * m))


assert abs(iid_overlap_factor(20) ** 2 - (2 * 400 + 1) / 60) < 1e-12

# X4: the lag curve, pooled residuals against residuals of yearly fits, always with the full-sample bread
_ys = X[:, J["Semiconductor"]]
E_YEAR = np.empty(T)
for _yy in sorted(set(YRS)):
    _k = YRS == _yy
    E_YEAR[_k] = ols(_ys[_k], ZM[_k], lag=0).e
N_YEAR_FITS = len(set(YRS))
U_POOL, U_YEAR = ZM * SEMI.e[:, None], ZM * E_YEAR[:, None]
LAG_MAX = 400


def gammas(u: Mat, kmax: int) -> list[Mat]:
    return [u.T @ u] + [u[k:].T @ u[:-k] for k in range(1, kmax + 1)]


_GP, _GY = gammas(U_POOL, LAG_MAX), gammas(U_YEAR, LAG_MAX)


def nw_se_curve(gs: list[Mat], lag: int) -> float:
    s = gs[0].copy()
    for k in range(1, lag + 1):
        s = s + (1 - k / (lag + 1)) * (gs[k] + gs[k].T)
    return float(np.sqrt((SEMI.zi @ s @ SEMI.zi)[1, 1]))


assert abs(nw_se_curve(_GP, 9) - SEMI.se_n[1]) < 1e-15 and abs(nw_se_curve(_GP, 0) - SEMI.se_w[1]) < 1e-15
LAG_GRID = sorted({round(float(v)) for v in np.geomspace(1, LAG_MAX, 60)} | {1, 2, 5, 9, 10, 20, 50, 100, 200, 400})
CURVE_POOL = [nw_se_curve(_GP, lg) for lg in LAG_GRID]
CURVE_YEAR = [nw_se_curve(_GY, lg) for lg in LAG_GRID]
CURVE_AT = {lg: (nw_se_curve(_GP, lg), nw_se_curve(_GY, lg)) for lg in (0, 9, 50, 200)}

# ---------------------------------------------------------------- section 6
CI = FITS["CommunicationsInternet"]
RF = 0.02
ADJ_CI = (1 - CI.b[1]) * RF / A
ADJ_SEMI = (1 - SEMI.b[1]) * RF / A
GAP_SEMI = (QM - SEMI.b[1] * QM) / A
ALPHA_J_SEMI = float(SEMI.b[0] - ADJ_SEMI + GAP_SEMI)
HALVES = []
for _nm in NAMES:
    _a1 = ols(X[:H, J[_nm]], ZM[:H])
    _a2 = ols(X[H:, J[_nm]], ZM[H:])
    HALVES.append((_nm, float(_a1.b[1]), float(_a2.b[1]),
                   float((_a2.b[1] - _a1.b[1]) / sqrt(_a1.se_n[1] ** 2 + _a2.se_n[1] ** 2)), _a1, _a2))
N_HALF_SIG = sum(1 for h in HALVES if abs(h[3]) > 1.96 + EPS)
B1V = np.array([h[1] for h in HALVES])
B2V = np.array([h[2] for h in HALVES])
HALF_SORTED = sorted(HALVES, key=lambda h: h[2] - h[1])


def rolling(y: Vec, x: Vec, w: int = 250) -> tuple[Vec, Vec]:
    """Slope (Cov/Var, ddof=0) and its classical SE, s_eps/(sqrt(w) s_x) with s_eps^2 = RSS/(w - 2), per window."""
    cy, cx = np.concatenate([[0.0], np.cumsum(y)]), np.concatenate([[0.0], np.cumsum(x)])
    cyy, cxx = np.concatenate([[0.0], np.cumsum(y * y)]), np.concatenate([[0.0], np.cumsum(x * x)])
    cxy = np.concatenate([[0.0], np.cumsum(x * y)])
    sy, sx_, syy, sxx, sxy = (c[w:] - c[:-w] for c in (cy, cx, cyy, cxx, cxy))
    vx = sxx / w - (sx_ / w) ** 2
    vy = syy / w - (sy / w) ** 2
    cv = sxy / w - (sx_ / w) * (sy / w)
    b = cv / vx
    rss = w * (vy - b * cv)
    se = np.sqrt(rss / (w - 2) / (w * vx))
    return b, se


ROLL = {nm: rolling(X[:, J[nm]], MKT) for nm in ("FinancialInsurance", "Semiconductor")}
for _nm, (_rb, _rse) in ROLL.items():     # the cumulative-sum slopes against np.cov at the extremes and the end
    for _t in (int(_rb.argmax()), int(_rb.argmin()), len(_rb) - 1):
        _yw, _xw = X[_t:_t + 250, J[_nm]], MKT[_t:_t + 250]
        _f = ols(_yw, design(_xw), lag=0)
        assert abs(_f.b[1] - _rb[_t]) < 1e-9 and abs(_f.se_c[1] - _rse[_t]) < 1e-9
ROLL_DATES = DATES[249:]
YF = X[:, J["FinancialInsurance"]]


def slope_r2(y: Vec, x: Vec) -> tuple[float, float]:
    c = np.cov(y, x, ddof=0)
    return float(c[0, 1] / c[1, 1]), float(c[0, 1] ** 2 / (c[0, 0] * c[1, 1]))


HB = {lab: slope_r2(YF[k], MKT[k]) for lab, k in
      (("full", slice(None)), ("first", slice(0, H)), ("second", slice(H, None)), ("last250", slice(T - 250, None)))}
NOTIONAL = 100e6 / (200 * F_LAST)
_y2, _m2 = YF[H:], MKT[H:]
HEDGE_OOS = {}
for _lab, _hh in (("none", 0.0), ("notional", 1.0), ("first", HB["first"][0]), ("second", HB["second"][0]),
                  ("full", HB["full"][0])):
    _vv = float(np.var(_y2 - _hh * _m2, ddof=0))
    HEDGE_OOS[_lab] = (sqrt(_vv), 1 - _vv / float(_y2.var(ddof=0)))
HEDGE28 = {}                    # every sector: (the first-half ratio's cut of the second half's variance, that half's own)
for _nm in NAMES:
    _ys = X[H:, J[_nm]]
    _b1 = slope_r2(X[:H, J[_nm]], MKT[:H])[0]
    HEDGE28[_nm] = (1 - float(np.var(_ys - _b1 * _m2, ddof=0)) / float(_ys.var(ddof=0)), slope_r2(_ys, _m2)[1])
HEDGE28_KEPT = float(np.median([o / i for o, i in HEDGE28.values()]))   # median share of the in-sample cut kept
HEDGE28_FAIL = sorted(nm for nm, (o, _) in HEDGE28.items() if o < 0.01 - EPS)  # cut under 1% or raise the variance
F2 = ols(R631, design(R50))
_yr2 = np.array([d[:4] for d in ETF_DATES])
BY_YEAR_ETF = {yy: ols(R631[_yr2 == yy], design(R50[_yr2 == yy])) for yy in sorted(set(_yr2))}
FULL2 = {k: v for k, v in BY_YEAR_ETF.items() if "2015" <= k <= "2025"}
YLO = min(FULL2, key=lambda k: FULL2[k].b[1])
YHI = max(FULL2, key=lambda k: FULL2[k].b[1])
ZDIFF = float((FULL2[YHI].b[1] - FULL2[YLO].b[1]) / sqrt(FULL2[YHI].se_n[1] ** 2 + FULL2[YLO].se_n[1] ** 2))
Z_YEARS = {k: float((v.b[1] - F2.b[1]) / v.se_n[1]) for k, v in FULL2.items()}   # each year against the full slope
YEARS_BEYOND = [k for k, z in Z_YEARS.items() if abs(z) > 1.96 + EPS]

# ---------------------------------------------------------------- section 7: 28 alphas
ORDER_T = sorted(NAMES, key=lambda k: T_C[k])
P_C = np.array([two_sided(T_C[k]) for k in NAMES])
P_N = np.array([two_sided(T_N[k]) for k in NAMES])
Z_BONF = float(stats.norm.isf(0.025 / 28))
ECOL = np.column_stack([FITS[nm].e for nm in NAMES])
CRES = np.corrcoef(ECOL.T)
IU = np.triu_indices(28, 1)
P_ANY_IND = 1 - 0.95**28
SD_IND = sqrt(28 * 0.05 * 0.95)
P3_IND = float(stats.binom.sf(2, 28, 0.05))
B1 = 100_000
_rng1 = np.random.default_rng([1, SEED])                       # experiment 1, created once
ZS = _rng1.standard_normal((B1, 28)) @ np.linalg.cholesky(CRES).T
CNT = (np.abs(ZS) > 1.96 + EPS).sum(axis=1)
N_ANY, N_GE3 = int((CNT >= 1).sum()), int((CNT >= 3).sum())
P_ANY, P_GE3 = N_ANY / B1, N_GE3 / B1
SE_ANY = sqrt(P_ANY * (1 - P_ANY) / B1)
CNT_MEAN, CNT_SD = float(CNT.mean()), float(CNT.std(ddof=0))
CNT_MEAN_SE = CNT_SD / sqrt(B1)
_m4 = float(((CNT - CNT_MEAN) ** 4).mean())
CNT_SD_SE = sqrt((_m4 - CNT_SD**4) / (4 * CNT_SD**2 * B1))     # delta method: SE of a standard deviation
SE_GE3 = sqrt(P_GE3 * (1 - P_GE3) / B1)

# ---------------------------------------------------------------- section 8: the named factor
RHO_ME, RHO_MF = corr(MKT, EL), corr(MKT, FX)
Z2 = design(MKT, FX)
ZRAW = design(MKT, EL)
TWO = {nm: ols(X[:, J[nm]], Z2) for nm in NAMES}
FRAW = ols(X[:, J["Semiconductor"]], ZRAW)
assert float(np.abs(FRAW.e - TWO["Semiconductor"].e).max()) < 1e-12
assert abs(float(TWO["Semiconductor"].b[1] - FRAW.b[1] - FRAW.b[2])) < 1e-12
T_EL_C = {nm: float(TWO[nm].b[2] / TWO[nm].se_c[2]) for nm in NAMES}
T_EL_N = {nm: float(TWO[nm].b[2] / TWO[nm].se_n[2]) for nm in NAMES}
L1 = np.array([ols(X[:H, J[nm]], Z2[:H]).b[2] for nm in NAMES])
L2 = np.array([ols(X[H:, J[nm]], Z2[H:]).b[2] for nm in NAMES])


def cosine(a: Vec, b: Vec) -> float:
    return float(a @ b / np.linalg.norm(a) / np.linalg.norm(b))


# ---------------------------------------------------------------- widget: 22 windows x 28 sectors
def windows() -> list[tuple[str, str, slice]]:
    w = [("full", "Full sample", slice(0, T)), ("h1", "First half", slice(0, H)), ("h2", "Second half", slice(H, T))]
    idx = np.arange(T)
    for yy in range(2009, 2027):
        k = idx[YRS == str(yy)]
        w.append((str(yy), str(yy) if yy < 2026 else "2026 to 8 October", slice(int(k[0]), int(k[-1]) + 1)))
    w.append(("last250", "Last 250 returns", slice(T - 250, T)))
    return w


WINDOWS = windows()
assert len(WINDOWS) == 22


def window_table() -> dict[str, dict]:
    out = {}
    for key, label, sl in WINDOWS:
        z = ZM[sl]
        rows = []
        for nm in NAMES:
            f = ols(X[sl, J[nm]], z)
            rows.append([float(f.b[1]), float(f.se_c[1]), float(f.se_w[1]), float(f.se_n[1]),
                         float(f.b[0]), float(f.se_c[0]), float(f.se_w[0]), float(f.se_n[0]),
                         float(f.r2), sqrt(f.s2)])
        out[key] = {"label": label, "T": sl.stop - sl.start, "lag": nw_lag(sl.stop - sl.start),
                    "first": DATES[sl.start], "last": DATES[sl.stop - 1], "rows": rows}
    return out


if __name__ == "__main__":
    print(f"T {T}, A {A:.4f}, halves {H}; Semiconductor beta {SEMI.b[1]:.6f}, alpha {1e4 * SEMI.b[0]:.5f} bp")
    print(f"iid overlap factor m=20: true {iid_overlap_factor(20):.4f}, NW(19) {iid_overlap_factor(20, 19):.4f}, "
          f"NW(38) {iid_overlap_factor(20, 38):.4f}; data NW19/classical {OVS.ov.se_n[1] / OVS.ov.se_c[1]:.4f}")
    print(f"lag grid {len(LAG_GRID)} values; experiment 1: Pr(>=1) {P_ANY:.5f}")
