"""LM23 anchors (Linear Regression): every number the Stage 1 brief quotes (revised 2026-10-19).

Reads only data/processed/*.parquet, through the builders named here (run them first):
  * U28 (Volume II): data/lm10_series.py's u28(), which reads data/processed/vol2_closes.parquet (built and repaired
    by data/vol2_series.py): the 28 leaf TWSE sector price indices and the TAIEX price index, closes 2008-12-01 ..
    2026-10-08, simple daily price returns between consecutive rows, T = 4,382 (2008-12-02 .. 2026-10-08), years =
    calendar days / 365.25, A = T / years = 245.4794. Halves (LM11's): the first and last 2,191 returns. The Electronic
    aggregate (outside U28) comes from the same parquet on the same dates; the named factor is its return minus the
    TAIEX's, labelled constructed.
  * LM2's 0050/00631L sample: data/processed/etf_daily_returns.parquet (2,902 common-date total-return pairs,
    2014-11-03 .. 2026-10-08), recomputed under LM23's name.
  * TR23 (Volume III): data/processed/vol3_taiex.parquet (columns date, tr, price, R, Rp), used twice: R - Rp on
    U28's dates (the TAIEX's dividend yield; Rp equals U28's TAIEX return there) and r = ln(1 + R) for LM18's model
    paths (experiment 3 of LM18 recomputed with LM18's own seed, default_rng([3, 20261011]), chunks of 500 paths).
  * TX23 (Volume IV): data/processed/vol4_tx23.parquet (data/vol4_series.py), one value: F, the settlement price of
    the TX contract held from the close of 2026-10-08 (LM8's contract value 200 F NT$, lm08.md:104-112).

Conventions. Regressions: OLS with an intercept unless stated; d = number of coefficients; the residual variance
s_eps^2 = RSS / (T - d). Standard errors: classical s_eps^2 (X'X)^-1; White's HC0 (X'X)^-1 (sum e_t^2 x_t x_t')
(X'X)^-1 without a degrees-of-freedom factor; Newey-West with Bartlett weights 1 - j/(L + 1), j = 1..L, no small-sample
correction (statsmodels' OLS default use_correction=False), lag L = floor(4 (n/100)^(2/9)) (the book's rule; it is
statsmodels' cov_hac_simple default; its attribution is an open point) unless stated: 9 at n = 4,382, 8 at 2,902, 7
at 2,191, 4 for one calendar year or 250 returns. t-stats and p-values use the normal reference (two-sided) except
Example 1's four points (t with T - d = 2). Means, standard deviations, variances and correlations of data divide by T
(ddof=0, passed explicitly); R-squared is (12.4). A sample autocorrelation is LM19's rho_hat_k: the full-sample mean,
divisor T in numerator and denominator. A sample quantile is LM14's F_hat^-1(u) (np.quantile method="inverted_cdf").
An intercept is printed in basis points a day and annualized as A times the daily value (A = U28's 245.4794). Simple
returns for one-day regressions; 20-day sums on log returns r = ln(1 + R). Counts against a threshold use the book's
guard (x <= c + 1e-12, |t| > c + 1e-12) and, where closes have two decimals, are checked exactly with Fraction.
Seeds: one LM23 experiment, e = 1 (the correlated null of 28 alpha t-stats, 100,000 draws), rng =
np.random.default_rng([1, 20261011]) created once at its start; LM18's paths reuse LM18's experiment 3 generator,
default_rng([3, 20261011]), as LM18 printed them. A Monte Carlo proportion's standard error is the binomial
sqrt(p (1 - p) / B); LM18's batch standard error is the SD of 20 batch slopes (divisor 20) over sqrt(20).
Numbers printed by earlier modules are echoed with file:line.

Rounding flags. Every number the brief prints passes through f(x, k1, k2, ...), which shows x with max(k) + 3 decimals
and flags it "NEAR" for each printed precision k at which x lies within a tenth of a last-digit unit of a rounding
boundary (|frac(10^k |x|) - 0.5| < 0.1). The brief prints a flagged value as rounded from the unrounded value here.

Prints one line per anchor, "A23-NN <value>", in ID order, and writes nothing.

Run:  PYTHONUTF8=1 uv run python data/vol4_anchors_lm23.py
"""
import sys
from dataclasses import dataclass
from datetime import date
from fractions import Fraction
from math import floor, sqrt
from pathlib import Path

import numpy as np
import polars as pl
import statsmodels.api as sm
from numpy.typing import NDArray
from scipy import stats
from statsmodels.stats.multitest import multipletests

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lm10_series import FIRST, LAST, u28

PROC = HERE / "processed"
EPS = 1e-12
SEED = 20261011
Vec = NDArray[np.float64]

OUT: list[str] = []
NEAR: list[str] = []


def put(value: str) -> None:
    """One anchor line; values that f() found near a rounding boundary are listed at its end."""
    tail = f" [NEAR a rounding boundary: {'; '.join(NEAR)}]" if NEAR else ""
    OUT.append(f"A23-{len(OUT) + 1:02d} {value}{tail}")
    NEAR.clear()


def f(x: float, *ks: int, plus: bool = False) -> str:
    """x with max(ks) + 3 decimals; flagged for each printed precision k within 0.1 of a last-digit unit of a boundary."""
    x = float(x)
    for k in ks:
        u = abs(x) * 10**k
        if abs(u - floor(u) - 0.5) < 0.1:
            NEAR.append(f"{x:.{k + 3}f} at {k} dp")
    return f"{x:{'+' if plus else ''}.{max(ks) + 3}f}"


def nw_lag(n: int) -> int:
    return floor(4 * (n / 100) ** (2 / 9))


@dataclass
class Fit:
    b: Vec
    e: Vec
    s2: float
    se_c: Vec
    se_w: Vec
    se_n: Vec
    lag: int
    r2: float
    zi: NDArray[np.float64]


def long_run(u: NDArray[np.float64], lag: int) -> NDArray[np.float64]:
    s = u.T @ u
    for j in range(1, lag + 1):
        g = u[j:].T @ u[:-j]
        s = s + (1 - j / (lag + 1)) * (g + g.T)
    return s


def ols(y: Vec, z: NDArray[np.float64], lag: int | None = None) -> Fit:
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
               1 - float(e @ e) / float(yc @ yc), zi)


def design(*cols: Vec) -> NDArray[np.float64]:
    return np.column_stack([np.ones(len(cols[0])), *cols])


def corr(a: Vec, b: Vec) -> float:
    return float(np.corrcoef(a, b)[0, 1])


def rho_hat(x: Vec, k: int) -> float:
    """LM19's sample autocorrelation: full-sample mean, divisor T in numerator and denominator."""
    c = x - x.mean()
    return float(c[k:] @ c[:-k] / (c @ c))


def two_sided(t: float) -> float:
    return float(2 * stats.norm.sf(abs(t)))


# ---------------------------------------------------------------- data
s = u28()
X, m, names, dates = s.X, s.taiex, s.names, s.dates
T = len(m)
A = s.A
J = {nm: i for i, nm in enumerate(names)}
H = T // 2
cl = pl.read_parquet(PROC / "vol2_closes.parquet").sort("date")
smp = cl.filter(pl.col("date").is_between(pl.lit(FIRST), pl.lit(LAST)))
close_dates = smp["date"].to_list()
assert close_dates[1:] == dates and close_dates == s.close_dates
pe = smp["Electronic"].to_numpy().astype(float)
assert smp["Electronic"].null_count() == 0
el = pe[1:] / pe[:-1] - 1
fx = el - m                                   # the constructed electronics factor
taiex_close = [Fraction(str(v)) for v in smp["TAIEX"].to_list()]
yrs = np.array([d[:4] for d in dates])
Zm = design(m)
fits = {nm: ols(X[:, J[nm]], Zm) for nm in names}
semi, fin = fits["Semiconductor"], fits["FinancialInsurance"]

# ---------------------------------------------------------------- data role
put(f"T {T}; returns {dates[0]} .. {dates[-1]}; closes {close_dates[0]} .. {close_dates[-1]}")          # 01
put(f"years {f(s.years, 4)}; A {f(A, 4, 2)}")                                                          # 02
put(f"halves {H} + {T - H}: {dates[0]} .. {dates[H - 1]} and {dates[H]} .. {dates[-1]}")               # 03
put(f"L = floor(4 (n/100)^(2/9)): n=4382 -> {nw_lag(4382)}, 2902 -> {nw_lag(2902)}, 2191 -> {nw_lag(2191)}, "
    f"250 -> {nw_lag(250)}, 243 -> {nw_lag(243)}, 185 -> {nw_lag(185)}")                                 # 04
cnt_y = {y: int((yrs == y).sum()) for y in sorted(set(yrs))}
full_years = {y: c for y, c in cnt_y.items() if "2009" <= y <= "2025"}
put(f"2008 {cnt_y['2008']} returns (December); 2009-2025 {min(full_years.values())}..{max(full_years.values())} "
    f"a year; 2025 {cnt_y['2025']}; 2026 {cnt_y['2026']} (to {dates[-1]}); last 250 {dates[T - 250]} .. {dates[-1]}")  # 05
put(f"Electronic: {len(el)} returns, no null close; corr(TAIEX, Electronic) {f(corr(m, el), 3)}")      # 06
etf = pl.read_parquet(PROC / "etf_daily_returns.parquet").sort("date")
R50 = etf["R_0050"].to_numpy()
R631 = etf["R_00631L"].to_numpy()
etf_dates = etf["date"].to_list()
put(f"LM2 sample: {len(R50)} pairs, {etf_dates[0]} .. {etf_dates[-1]}")                               # 07
tr = pl.read_parquet(PROC / "vol3_taiex.parquet").sort("date")
trd = {str(d): (a, b) for d, a, b in zip(tr["date"].to_list(), tr["R"].to_list(), tr["Rp"].to_list(), strict=True)}
Rt = np.array([trd[d][0] for d in dates])
Rp = np.array([trd[d][1] for d in dates])
qm = A * float((Rt - Rp).mean())
put(f"TR23 on U28 dates: max abs(Rp - TAIEX) {np.abs(Rp - m).max():.1e}; q_m = A mean(R - Rp) {f(100 * qm, 2)}%; "
    f"growth TR {f(np.prod(1 + Rt), 2)} vs price {f(np.prod(1 + Rp), 2)}")                             # 08

# ---------------------------------------------------------------- case
semi_close = smp["Semiconductor"].to_list()
put(f"Semiconductor {semi_close[0]} -> {semi_close[-1]}: x{f(semi_close[-1] / semi_close[0], 1)}; TAIEX "
    f"{float(taiex_close[0]):.2f} -> {float(taiex_close[-1]):.2f}: x{f(float(taiex_close[-1] / taiex_close[0]), 1)}")  # 09
put(f"beta {f(semi.b[1], 3, 4)}; alpha {f(1e4 * semi.b[0], 2)} bp/day; A*alpha {f(100 * A * semi.b[0], 2)}%; "
    f"R-squared {f(semi.r2, 4, 5)}")                                                                     # 10
put(f"SE(beta) classical {f(semi.se_c[1], 4)}, White {f(semi.se_w[1], 4)}, HAC(L={semi.lag}) {f(semi.se_n[1], 4)}; "
    f"SE(alpha) bp {f(1e4 * semi.se_c[0], 2)}, {f(1e4 * semi.se_w[0], 2)}, {f(1e4 * semi.se_n[0], 2)}")  # 11
ta = [semi.b[0] / semi.se_c[0], semi.b[0] / semi.se_w[0], semi.b[0] / semi.se_n[0]]
put("t(alpha) classical, White, HAC " + ", ".join(f(t, 2) for t in ta) + "; p "
    + ", ".join(f(two_sided(t), 3) for t in ta))                                                        # 12
sh1 = ols(X[:H, J["Semiconductor"]], Zm[:H])
sh2 = ols(X[H:, J["Semiconductor"]], Zm[H:])
put(f"halves beta {f(sh1.b[1], 3)} (HAC L={sh1.lag} {f(sh1.se_n[1], 3)}), {f(sh2.b[1], 3)} (HAC {f(sh2.se_n[1], 3)}); "
    f"alpha bp {f(1e4 * sh1.b[0], 2)}, {f(1e4 * sh2.b[0], 2)}")                                       # 13
betas = {nm: float(fits[nm].b[1]) for nm in names}
lo_b, hi_b = min(betas, key=lambda k: betas[k]), max(betas, key=lambda k: betas[k])
put(f"betas {lo_b} {f(betas[lo_b], 3)} .. {hi_b} {f(betas[hi_b], 3)}")                                # 14
t_c = {nm: float(fits[nm].b[0] / fits[nm].se_c[0]) for nm in names}
t_w = {nm: float(fits[nm].b[0] / fits[nm].se_w[0]) for nm in names}
t_n = {nm: float(fits[nm].b[0] / fits[nm].se_n[0]) for nm in names}


def beyond(tt: dict[str, float], c: float = 1.96) -> list[str]:
    return [f"{k} {f(tt[k], 2, 3, 4, plus=True)}" for k in names if abs(tt[k]) > c + EPS]


put(f"abs(t(alpha)) > 1.96: classical {beyond(t_c)}; White {beyond(t_w)}; HAC {beyond(t_n)}; expected 28 x 0.05 = "
    f"{28 * 0.05:.1f}")                                                                                  # 15

# ---------------------------------------------------------------- section 2: four points (LM12's example)
x4 = np.array([0.0, 1, 2, 3])
y4 = np.array([1.0, 3, 2, 6])
f4 = ols(y4, design(x4), lag=0)
t2 = float(stats.t.ppf(0.975, 2))
put(f"beta {f(f4.b[1], 1)}, alpha {f(f4.b[0], 1)}, RSS {f(f4.s2 * 2, 1)}, s_eps^2 {f(f4.s2, 1)}; SE(beta) "
    f"{f(f4.se_c[1], 3)}, SE(alpha) {f(f4.se_c[0], 3)}; t(beta) {f(f4.b[1] / f4.se_c[1], 2)}; t_2 quantile {f(t2, 3)}; "
    f"t interval {f(f4.b[1] - t2 * f4.se_c[1], 2)}..{f(f4.b[1] + t2 * f4.se_c[1], 2)}; 1.96 interval "
    f"{f(f4.b[1] - 1.96 * f4.se_c[1], 2)}..{f(f4.b[1] + 1.96 * f4.se_c[1], 2)}")                       # 16

# ---------------------------------------------------------------- section 3
mx, sx = float(m.mean()), float(m.std(ddof=0))
put(f"s_eps (T-2) {f(100 * sqrt(semi.s2), 5)}%; divisor T {f(100 * float(semi.e.std(ddof=0)), 5)}%; TAIEX mean "
    f"{f(100 * mx, 4)}%, s_x {f(100 * sx, 3)}%; s_eps/(sqrt(T) s_x) {f(sqrt(semi.s2) / (sqrt(T) * sx), 4)}")  # 17
put(f"95% interval for beta: classical {f(semi.b[1] - 1.96 * semi.se_c[1], 3)}..{f(semi.b[1] + 1.96 * semi.se_c[1], 3)}"
    f"; HAC {f(semi.b[1] - 1.96 * semi.se_n[1], 3)}..{f(semi.b[1] + 1.96 * semi.se_n[1], 3)}")         # 18
q4380, q248 = float(stats.t.ppf(0.975, 4380)), float(stats.t.ppf(0.975, 248))
q241, q183, qn = float(stats.t.ppf(0.975, 241)), float(stats.t.ppf(0.975, 183)), float(stats.norm.ppf(0.975))
put(f"t quantiles 0.975: df 4380 {f(q4380, 4)}, df 248 {f(q248, 3)}, df 241 {f(q241, 3, 4)}, df 183 {f(q183, 3)}, "
    f"normal {f(qn, 3, 4)}; t_183 / normal - 1 {f(100 * (q183 / qn - 1), 1)}%")                         # 19
adj = 1 - (1 - semi.r2) * (T - 1) / (T - 2)
put(f"adjusted R-squared {f(adj, 5)}; F = t(beta)^2 {f(semi.b[1] ** 2 / semi.se_c[1] ** 2, 0)} "
    f"(t {f(semi.b[1] / semi.se_c[1], 2)})")                                                            # 20
k25 = yrs == "2025"
y25, x25 = X[k25, J["FinancialInsurance"]], m[k25]
f25 = ols(y25, design(x25))
put(f"FinancialInsurance 2025: T {int(k25.sum())}; beta {f(f25.b[1], 3)} (classical {f(f25.se_c[1], 3, 4)}, White "
    f"{f(f25.se_w[1], 3)}, HAC L={f25.lag} {f(f25.se_n[1], 3)}; White/classical {f(f25.se_w[1] / f25.se_c[1], 2)}); "
    f"alpha {f(1e4 * f25.b[0], 2)} bp; s_eps {f(100 * sqrt(f25.s2), 3)}%; R-squared {f(f25.r2, 4)}; TAIEX mean "
    f"{f(100 * float(x25.mean()), 4)}%, s_x {f(100 * float(x25.std(ddof=0)), 4)}%, min "
    f"{f(100 * float(x25.min()), 2, 4)}%, max {f(100 * float(x25.max()), 2)}%")                         # 21
x0 = -0.05
z0 = np.array([1.0, x0])
h0 = float(z0 @ f25.zi @ z0)
yhat0 = float(z0 @ f25.b)
se_fit, se_pred = sqrt(f25.s2 * h0), sqrt(f25.s2 * (1 + h0))
h0_full = float(z0 @ fin.zi @ z0)
put(f"x0 -5%: fitted {f(100 * yhat0, 2)}%; SE(fit) {f(100 * se_fit, 3)}%; confidence {f(100 * (yhat0 - 1.96 * se_fit), 2)}"
    f"..{f(100 * (yhat0 + 1.96 * se_fit), 2)}%; prediction {f(100 * (yhat0 - 1.96 * se_pred), 2)}.."
    f"{f(100 * (yhat0 + 1.96 * se_pred), 2)}%; half-widths {f(100 * 1.96 * se_fit, 2)} and {f(100 * 1.96 * se_pred, 2)}"
    f" points; full-sample confidence half-width at -5% {f(100 * 1.96 * sqrt(fin.s2 * h0_full), 3)} points")  # 22
i7 = dates.index("2025-04-07")
j7 = int(np.flatnonzero(k25).tolist().index(i7))
h7 = float(design(x25)[j7] @ f25.zi @ design(x25)[j7])
h7b = 1 / len(x25) + (x25[j7] - x25.mean()) ** 2 / (len(x25) * x25.var(ddof=0))
assert abs(h7 - h7b) < 1e-12
keep = np.ones(len(x25), dtype=bool)
keep[j7] = False
f25b = ols(y25[keep], design(x25[keep]))
r7 = taiex_close[i7 + 1] / taiex_close[i7] - 1
r_all = [taiex_close[i + 1] / taiex_close[i] - 1 for i in range(T)]
assert r7 == min(r_all) and abs(float(r7) - m[i7]) < 1e-15
n5 = sum(1 for i in np.flatnonzero(k25) if r_all[i] <= Fraction(-5, 100))
n5g = int((x25 <= -0.05 + EPS).sum())
assert n5 == n5g
put(f"2025-04-07: TAIEX {f(100 * float(r7), 2)}% (exact sample minimum by Fraction), FinancialInsurance "
    f"{f(100 * y25[j7], 2)}%; leverage {f(h7, 3, 4)} (equals the formula 1/T + (x_t - xbar)^2/(T s_x^2)); average d/T "
    f"{f(2 / len(x25), 4)}; ratio {f(h7 / (2 / len(x25)), 0)}; beta without it {f(f25b.b[1], 3)} (SE classical "
    f"{f(f25b.se_c[1], 3)}, White {f(f25b.se_w[1], 3)}); shift of beta in classical SEs "
    f"{f((f25.b[1] - f25b.b[1]) / f25.se_c[1], 1)}; 2025 days with TAIEX <= -5%: {n5} (guard {n5g})")   # 23
put(f"beta = 1, Semiconductor: classical t {f((semi.b[1] - 1) / semi.se_c[1], 1)}, HAC t "
    f"{f((semi.b[1] - 1) / semi.se_n[1], 1)}; against 0 with HAC {f(semi.b[1] / semi.se_n[1], 1)}")     # 24

# ---------------------------------------------------------------- section 4: LM18's paths (experiment 3 of LM18)
Rtr = tr["R"].to_numpy()[1:].astype(float)
rtr = np.log1p(Rtr)
years_tr = (date.fromisoformat(str(tr["date"][-1])) - date.fromisoformat(str(tr["date"][0]))).days / 365.25
m5 = round(5 * len(Rtr) / years_tr)
rbar, sr = float(rtr.mean()), float(rtr.std(ddof=0))
g3 = np.random.default_rng([3, SEED])
S3 = np.empty(10_000)
for c in range(0, 10_000, 500):
    S3[c:c + 500] = (rbar + sr * g3.standard_normal((500, m5))).sum(axis=1)
G3 = np.exp(S3)
f18 = ols(G3, design(S3), lag=0)
batch = []
for bb in range(20):
    sl = slice(bb * 500, (bb + 1) * 500)
    cv = np.cov(G3[sl], S3[sl], ddof=0)
    batch.append(cv[0, 1] / cv[1, 1])
bse = float(np.std(batch, ddof=0) / sqrt(20))
mu_s, v_s = m5 * rbar, m5 * sr**2
nodes, wts = np.polynomial.hermite_e.hermegauss(200)
wts = wts / wts.sum()
Sq = mu_s + sqrt(v_s) * nodes
beta_exact = float(np.exp(mu_s + v_s / 2))
eq = np.exp(Sq) - beta_exact - beta_exact * (Sq - mu_s)
se_sand = sqrt(float((wts * (Sq - mu_s) ** 2 * eq**2).sum()) / (10_000 * v_s**2))
se_class_model = sqrt(float((wts * eq**2).sum()) / (10_000 * v_s))
q1, q2 = (float(v) for v in np.quantile(S3, [1 / 3, 2 / 3], method="inverted_cdf"))
grp = [S3 <= q1, (S3 > q1) & (S3 <= q2), S3 > q2]
terc = [sqrt(float(np.mean(f18.e[g] ** 2))) for g in grp]
put(f"m {m5}; rbar {100 * rbar:.7f}%, s_r {100 * sr:.6f}%; beta hat {f(f18.b[1], 4)}; classical {f(f18.se_c[1], 4)}; "
    f"White {f(f18.se_w[1], 4)}; batch (LM18) {f(bse, 4)}; model: beta {f(beta_exact, 4)}, sandwich SE "
    f"{f(se_sand, 4)}, classical-formula SE {f(se_class_model, 4)}; residual RMS by tercile of ln G (cuts F^-1(1/3), "
    f"F^-1(2/3); {', '.join(str(int(g.sum())) for g in grp)} paths) "
    + ", ".join(f(v, 3) for v in terc))                                                                 # 25
ratio = {nm: float(fits[nm].se_w[1] / fits[nm].se_c[1]) for nm in names}
ratio_n = {nm: float(fits[nm].se_n[1] / fits[nm].se_c[1]) for nm in names}
rl, rh = min(ratio, key=lambda k: ratio[k]), max(ratio, key=lambda k: ratio[k])
nl, nh = min(ratio_n, key=lambda k: ratio_n[k]), max(ratio_n, key=lambda k: ratio_n[k])
put(f"SE(beta) White/classical {rl} {f(ratio[rl], 2)} .. {rh} {f(ratio[rh], 2)}; HAC/classical {nl} "
    f"{f(ratio_n[nl], 2)} .. {nh} {f(ratio_n[nh], 2)}")                                                 # 26
f16 = ols(X[:, J["FinancialInsurance"]], design(X[:, J["Semiconductor"]]))
put(f"LM16 pair: beta {f(f16.b[1], 4)} (lm16.md:354 prints 0.4591); SE classical {f(f16.se_c[1], 4)}, White "
    f"{f(f16.se_w[1], 4)}, HAC(9) {f(f16.se_n[1], 4)}; HAC interval {f(f16.b[1] - 1.96 * f16.se_n[1], 3)}.."
    f"{f(f16.b[1] + 1.96 * f16.se_n[1], 3)}; s_eps (T-2) {f(100 * sqrt(f16.s2), 5)}%, divisor T "
    f"{f(100 * float(f16.e.std(ddof=0)), 5)}% (lm12.md:436 prints 0.996%)")                             # 27

# ---------------------------------------------------------------- section 5: overlapping 20-day sums
lx, lm = np.log1p(X), np.log1p(m)
M20 = 20


def ov(x: Vec, k: int) -> Vec:
    c = np.concatenate([[0.0], np.cumsum(x)])
    return c[k:] - c[:-k]


def overlap_row(nm: str) -> tuple[str, Vec, float, float]:
    y1 = lx[:, J[nm]]
    fd = ols(y1, design(lm), lag=0)
    yo, xo = ov(y1, M20), ov(lm, M20)
    zo = design(xo)
    fo = ols(yo, zo, lag=M20 - 1)
    fo2 = ols(yo, zo, lag=2 * (M20 - 1))
    nwin = T // M20
    fn = ols(y1[: nwin * M20].reshape(nwin, M20).sum(1), design(lm[: nwin * M20].reshape(nwin, M20).sum(1)), lag=0)
    offs = []
    for o in range(M20):
        nn = (T - o) // M20
        offs.append(ols(y1[o:o + nn * M20].reshape(nn, M20).sum(1),
                        design(lm[o:o + nn * M20].reshape(nn, M20).sum(1)), lag=0).b[1])
    txt = (f"{nm}: daily log beta {f(fd.b[1], 3)} (classical {f(fd.se_c[1], 4)}); overlapping ({len(yo)} windows) beta "
           f"{f(fo.b[1], 3)}, classical {f(fo.se_c[1], 4)}, White {f(fo.se_w[1], 4)}, NW(19) {f(fo.se_n[1], 4)}, "
           f"NW(38) {f(fo2.se_n[1], 4)}; non-overlapping ({nwin} windows from the first return) beta {f(fn.b[1], 3)}, "
           f"classical {f(fn.se_c[1], 4)}; 20 starting days {f(min(offs), 3)}..{f(max(offs), 3)}")
    return txt, fo.e, float(fo.se_c[1]), float(fo.se_n[1])


txt_s, eo, ov_c, ov_n = overlap_row("Semiconductor")
put(txt_s)                                                                                               # 28
put("overlap residual rho_hat_k (LM19) " + ", ".join(f"lag {k} {f(rho_hat(eo, k), 3)}" for k in (1, 10, 19, 20))
    + f"; iid model (m - k)/m: lag 1 {19 / 20:.2f}, lag 10 {10 / 20:.2f}, lag 19 {1 / 20:.2f}, lag 20 0")  # 29
put(overlap_row("FinancialInsurance")[0] + " // " + overlap_row("Food")[0])                               # 30
ys = X[:, J["Semiconductor"]]
e_year = np.empty(T)
for yy in sorted(set(yrs)):                    # one fit per calendar year; 2008's 22 returns form their own fit
    k = yrs == yy
    e_year[k] = ols(ys[k], Zm[k], lag=0).e
u_pool, u_year = Zm * semi.e[:, None], Zm * e_year[:, None]


def nw_se(u: NDArray[np.float64], lag: int) -> float:
    return float(np.sqrt((semi.zi @ long_run(u, lag) @ semi.zi)[1, 1]))


put("NW SE of Semiconductor's beta by L (0 = White): pooled residuals "
    + ", ".join(f"L{lg} {f(nw_se(u_pool, lg), 4)}" for lg in (0, 9, 50, 200))
    + f"; residuals of yearly fits ({len(set(yrs))} fits, 2008 its own) "
    + ", ".join(f"L{lg} {f(nw_se(u_year, lg), 4)}" for lg in (0, 9, 50, 200)))                         # 31

# ---------------------------------------------------------------- section 6: alpha, r_f, dividends, stability, hedge
ci = fits["CommunicationsInternet"]
adj_ci = (1 - ci.b[1]) * 0.02 / A
adj_se = (1 - semi.b[1]) * 0.02 / A
put(f"(1 - beta) r_f / A at r_f = 2%: CommunicationsInternet beta {f(ci.b[1], 3)}: {f(1e4 * adj_ci, 2)} bp/day "
    f"({f(100 * (1 - ci.b[1]) * 0.02, 2)}% a year), raw alpha {f(1e4 * ci.b[0], 2)} bp (SE classical "
    f"{f(1e4 * ci.se_c[0], 2)}), Jensen-type {f(1e4 * (ci.b[0] - adj_ci), 2)} bp; Semiconductor {f(1e4 * adj_se, 2)} "
    f"bp/day ({f(100 * (1 - semi.b[1]) * 0.02, 2)}% a year)")                                           # 32
gap_semi = (qm - semi.b[1] * qm) / A
put(f"dividend gap (q_i - beta q_m)/A: one point of yield = {f(1e4 * 0.01 / A, 2)} bp/day; Semiconductor with q_i = q_m: "
    f"{f(1e4 * gap_semi, 2)} bp/day ({f(100 * (1 - semi.b[1]) * qm, 2)}% a year); alpha then "
    f"{f(1e4 * (semi.b[0] + gap_semi - adj_se), 2)} bp/day with r_f = 2%")                              # 33
halves = []
for nm in names:
    a1 = ols(X[:H, J[nm]], Zm[:H])
    a2 = ols(X[H:, J[nm]], Zm[H:])
    z = (a2.b[1] - a1.b[1]) / sqrt(a1.se_n[1] ** 2 + a2.se_n[1] ** 2)
    halves.append((nm, float(a1.b[1]), float(a2.b[1]), float(z)))
n_sig = sum(1 for h in halves if abs(h[3]) > 1.96 + EPS)
b1v = np.array([h[1] for h in halves])
b2v = np.array([h[2] for h in halves])
big = sorted(halves, key=lambda h: h[2] - h[1])          # ordered by the change in beta, second half minus first
low_z = min(halves, key=lambda h: abs(h[3]))
put(f"halves (HAC L=7 each): {n_sig} of 28 differ by more than 1.96 SE; corr of halves' betas {f(corr(b1v, b2v), 3)}; "
    f"largest falls of beta {big[0][0]} {f(big[0][1], 3)} -> {f(big[0][2], 3)} (z {f(big[0][3], 1)}), {big[1][0]} "
    f"{f(big[1][1], 3)} -> {f(big[1][2], 3)}, {big[2][0]} {f(big[2][1], 3)} -> {f(big[2][2], 3)}; largest rise "
    f"{big[-1][0]} {f(big[-1][1], 3)} -> {f(big[-1][2], 3)} (z {f(big[-1][3], 1)}); smallest abs(z) {low_z[0]} "
    f"{f(abs(low_z[3]), 2)}")                                                                            # 34
roll_txt = []
for nm in ("FinancialInsurance", "Semiconductor"):
    yv = X[:, J[nm]]
    rb = np.array([np.cov(yv[t - 250:t], m[t - 250:t], ddof=0)[0, 1] / m[t - 250:t].var(ddof=0)
                   for t in range(250, T + 1)])
    roll_txt.append(f"{nm} max {f(rb.max(), 3)} ({dates[249 + int(rb.argmax())]}), min {f(rb.min(), 3)} "
                    f"({dates[249 + int(rb.argmin())]}), last {f(rb[-1], 3)}")
put(f"rolling 250-return betas ({T - 249} windows, first ends {dates[249]}): " + "; ".join(roll_txt))    # 35
yf = X[:, J["FinancialInsurance"]]


def slope_r2(y: Vec, x: Vec) -> tuple[float, float]:
    c = np.cov(y, x, ddof=0)
    return float(c[0, 1] / c[1, 1]), float(c[0, 1] ** 2 / (c[0, 0] * c[1, 1]))


hb = {lab: slope_r2(yf[k], m[k]) for lab, k in
      (("full", slice(None)), ("first", slice(0, H)), ("second", slice(H, None)), ("last250", slice(T - 250, None)))}
tx = pl.read_parquet(PROC / "vol4_tx23.parquet").filter(pl.col("date") == date.fromisoformat(LAST))
assert tx.height == 1 and float(tx["S"][0]) == float(taiex_close[-1])
F_last, contract = float(tx["F"][0]), int(tx["contract"][0])
notional = 100e6 / (200 * F_last)
put("FinancialInsurance hedge ratios (beta, R-squared): "
    + "; ".join(f"{k} {f(v[0], 4)}, {f(v[1], 4)}" for k, v in hb.items())
    + f"; TX23 on {LAST}: F {F_last:.0f} (contract {contract}; TAIEX {float(taiex_close[-1]):.2f}); NT$100m / (200 F): "
    f"notional {f(notional, 2)} contracts, full beta {f(hb['full'][0] * notional, 2)}, last-250 beta "
    f"{f(hb['last250'][0] * notional, 2)}")                                                             # 36
y2, m2 = yf[H:], m[H:]
red = []
for lab, hh in (("none", 0.0), ("notional 1", 1.0), ("first-half beta", hb["first"][0]),
                ("second-half beta (in-sample)", hb["second"][0]), ("full beta", hb["full"][0])):
    vv = float(np.var(y2 - hh * m2, ddof=0))
    red.append(f"{lab} SD {f(100 * sqrt(vv), 4)}%, reduction {f(100 * (1 - vv / float(y2.var(ddof=0))), 2)}%")
put("second half hedged: " + "; ".join(red))                                                            # 37
f2 = ols(R631, design(R50))
yr2 = np.array([d[:4] for d in etf_dates])
by = {}
for yy in sorted(set(yr2)):
    k = yr2 == yy
    by[yy] = ols(R631[k], design(R50[k]))
full2 = {k: v for k, v in by.items() if "2015" <= k <= "2025"}
ylo = min(full2, key=lambda k: full2[k].b[1])
yhi = max(full2, key=lambda k: full2[k].b[1])
zdiff = (full2[yhi].b[1] - full2[ylo].b[1]) / sqrt(full2[yhi].se_n[1] ** 2 + full2[ylo].se_n[1] ** 2)
put(f"LM2: slope {f(f2.b[1], 3, 4)} (lm02.md:496 prints 1.887), corr {f(corr(R50, R631), 3)}; SE classical "
    f"{f(f2.se_c[1], 4)}, White {f(f2.se_w[1], 4)}, HAC(L={f2.lag}) {f(f2.se_n[1], 4)}; (2 - slope)/HAC SE "
    f"{f((2 - f2.b[1]) / f2.se_n[1], 2)}; HAC interval {f(f2.b[1] - 1.96 * f2.se_n[1], 3)}.."
    f"{f(f2.b[1] + 1.96 * f2.se_n[1], 3)}; years 2015-2025: {ylo} {f(full2[ylo].b[1], 3)} (HAC L={full2[ylo].lag} "
    f"{f(full2[ylo].se_n[1], 4)}), {yhi} {f(full2[yhi].b[1], 3)} ({f(full2[yhi].se_n[1], 4)}); difference z "
    f"{f(zdiff, 2)}")                                                                                    # 38

# ---------------------------------------------------------------- section 7: 28 alphas
order = sorted(names, key=lambda k: t_c[k])
put("t(alpha) classical / HAC, ascending by classical: "
    + "; ".join(f"{k} {f(t_c[k], 2, 3, plus=True)}/{f(t_n[k], 2, 3, plus=True)}" for k in order))      # 39
p_c = np.array([two_sided(t_c[k]) for k in names])
p_n = np.array([two_sided(t_n[k]) for k in names])
zb = float(stats.norm.isf(0.025 / 28))
rej = {meth: (int(multipletests(p_c, alpha=0.05, method=meth)[0].sum()),
              int(multipletests(p_n, alpha=0.05, method=meth)[0].sum())) for meth in ("bonferroni", "holm", "fdr_bh")}
ps = np.sort(p_c)
bh_hand = sum(1 for i, p in enumerate(ps, start=1) if p <= 0.05 * i / 28)
put(f"Bonferroni p < {f(0.05 / 28, 5)}, abs(t) > {f(zb, 2)}; rejections (classical, HAC): {rej}; BH by hand: largest i "
    f"with p_(i) <= 0.05 i/28: {bh_hand}; smallest p {f(ps[0], 3)} vs 0.05/28; adjusted min: Holm "
    f"{f(multipletests(p_c, method='holm')[1].min(), 3)}, BH {f(multipletests(p_c, method='fdr_bh')[1].min(), 3)} "
    f"(HAC {f(multipletests(p_n, method='fdr_bh')[1].min(), 3)})")                                    # 40
Ecol = np.column_stack([fits[nm].e for nm in names])
C = np.corrcoef(Ecol.T)
iu = np.triu_indices(28, 1)
put(f"residual correlations across sectors ({len(iu[0])} pairs): mean {f(C[iu].mean(), 3)}, min {f(C[iu].min(), 3)}, "
    f"max {f(C[iu].max(), 3)}")                                                                           # 41
p_any = 1 - 0.95**28
put(f"independent tests: count mean 1.4, SD {f(sqrt(28 * 0.05 * 0.95), 3)}; Pr(>=1) {f(p_any, 4)}; Pr(>=3) "
    f"{f(float(stats.binom.sf(2, 28, 0.05)), 3)}")                                                      # 42
rng1 = np.random.default_rng([1, SEED])                       # experiment 1
B1 = 100_000
Zs = rng1.standard_normal((B1, 28)) @ np.linalg.cholesky(C).T
cnt = (np.abs(Zs) > 1.96 + EPS).sum(axis=1)
n1, n3 = int((cnt >= 1).sum()), int((cnt >= 3).sum())
pa, p3 = n1 / B1, n3 / B1
put(f"experiment 1 (default_rng([1, 20261011]), {B1} draws): count mean {f(cnt.mean(), 3)} (SE "
    f"{f(cnt.std(ddof=0) / sqrt(B1), 3)}), SD {f(cnt.std(ddof=0), 3)}; Pr(>=1) {n1}/{B1} = {f(pa, 3)} (binomial SE "
    f"{f(sqrt(pa * (1 - pa) / B1), 4)}); Pr(>=3) {n3}/{B1} = {f(p3, 3)} (SE {f(sqrt(p3 * (1 - p3) / B1), 4)})")  # 43

# ---------------------------------------------------------------- section 8: the named factor
rho_me, rho_mf = corr(m, el), corr(m, fx)
put(f"corr(TAIEX, Electronic) {f(rho_me, 3)}, VIF {f(1 / (1 - rho_me**2), 1)}, condition number of the correlation "
    f"matrix {f((1 + rho_me) / (1 - rho_me), 0)}; corr(TAIEX, Electronic - TAIEX) {f(rho_mf, 3)}, VIF "
    f"{f(1 / (1 - rho_mf**2), 2)}, condition number {f((1 + rho_mf) / (1 - rho_mf), 2)}; SD daily: TAIEX "
    f"{f(100 * float(m.std(ddof=0)), 3)}%, factor {f(100 * float(fx.std(ddof=0)), 3)}%")                 # 44
Z2 = design(m, fx)
Zraw = design(m, el)
two = {nm: ols(X[:, J[nm]], Z2) for nm in names}


def frow(nm: str) -> str:
    t2f = two[nm]
    return (f"{nm}: one-factor {f(fits[nm].b[1], 3)} (R2 {f(fits[nm].r2, 4)}); market {f(t2f.b[1], 3)} "
            f"({f(t2f.se_c[1], 3)}; HAC {f(t2f.se_n[1], 3)}), electronics {f(t2f.b[2], 3, plus=True)} "
            f"({f(t2f.se_c[2], 3)}; HAC {f(t2f.se_n[2], 3)}); R2 {f(t2f.r2, 4)}")


fraw = ols(X[:, J["Semiconductor"]], Zraw)
same_fit = float(np.abs(fraw.e - two["Semiconductor"].e).max())
ident = float(two["Semiconductor"].b[1] - fraw.b[1] - fraw.b[2])
assert same_fit < 1e-12 and abs(ident) < 1e-12
put(frow("Semiconductor") + f" // raw design (TAIEX, Electronic): {f(fraw.b[1], 3, plus=True)} ({f(fraw.se_c[1], 3)}), "
    f"{f(fraw.b[2], 3, plus=True)} ({f(fraw.se_c[2], 3)}); market(excess) = market(raw) + Electronic(raw) and the "
    f"residuals agree within 1e-12")                                                                     # 45
put(frow("FinancialInsurance"))                                                                          # 46
n_el_c = sum(1 for nm in names if abs(two[nm].b[2] / two[nm].se_c[2]) > 1.96 + EPS)
n_el_n = sum(1 for nm in names if abs(two[nm].b[2] / two[nm].se_n[2]) > 1.96 + EPS)
L1 = np.array([ols(X[:H, J[nm]], Z2[:H]).b[2] for nm in names])
L2 = np.array([ols(X[H:, J[nm]], Z2[H:]).b[2] for nm in names])
weak = min(names, key=lambda k: abs(two[k].b[2] / two[k].se_c[2]))
weak_n = min(names, key=lambda k: abs(two[k].b[2] / two[k].se_n[2]))
assert weak == weak_n
put(f"electronics loadings abs(t) > 1.96: classical {n_el_c}, HAC {n_el_n} of 28 (smallest abs(t), both methods: {weak} "
    f"classical {f(two[weak].b[2] / two[weak].se_c[2], 2, plus=True)}, HAC "
    f"{f(two[weak].b[2] / two[weak].se_n[2], 2, plus=True)}); halves' loadings corr {f(corr(L1, L2), 3)}, cosine "
    f"{f(float(L1 @ L2 / np.linalg.norm(L1) / np.linalg.norm(L2)), 3)}; halves' betas corr {f(corr(b1v, b2v), 3)}, "
    f"cosine {f(float(b1v @ b2v / np.linalg.norm(b1v) / np.linalg.norm(b2v)), 3)}")                    # 47
put(" // ".join(frow(nm) for nm in ("ElectronicPartsComponents", "ComputerPeripheralEquipment", "CommunicationsInternet",
                                   "Plastics")))                                                         # 48

# ---------------------------------------------------------------- section 9 and problems
r_sm = sm.OLS(X[:, J["FinancialInsurance"]], Zm).fit()
r_hc = sm.OLS(X[:, J["FinancialInsurance"]], Zm).fit(cov_type="HC0")
r_hac = sm.OLS(X[:, J["FinancialInsurance"]], Zm).fit(cov_type="HAC", cov_kwds={"maxlags": 9})
r_hacc = sm.OLS(X[:, J["FinancialInsurance"]], Zm).fit(cov_type="HAC", cov_kwds={"maxlags": 9, "use_correction": True})
dif = max(float(np.abs(np.asarray(r_sm.bse) / fin.se_c - 1).max()), float(np.abs(np.asarray(r_hc.bse) / fin.se_w - 1).max()),
          float(np.abs(np.asarray(r_hac.bse) / fin.se_n - 1).max()))
assert dif < 1e-12
put(f"FinancialInsurance: beta {f(fin.b[1], 4)}; SE classical {f(fin.se_c[1], 4)}, HC0 {f(fin.se_w[1], 4)}, HAC(9) "
    f"{f(fin.se_n[1], 4)}; HAC use_correction=True {f(float(np.asarray(r_hacc.bse)[1]), 5)} (x sqrt(T/(T-2)) "
    f"{f(sqrt(T / (T - 2)), 6)}); statsmodels agrees with NumPy (largest relative difference below 1e-12); HAC "
    f"p-values normal: use_t {r_hac.use_t}")                                                             # 49
put(f"P1 (T 12, d 2, RSS 0.0240): T-d {f(100 * sqrt(0.0240 / 10), 2)}%, T {f(100 * sqrt(0.0240 / 12), 2)}%, T-1 "
    f"{f(100 * sqrt(0.0240 / 11), 2)}%")                                                                 # 50
put(f"P2 (s_eps 1%, s_x 1.2%, T 1000): {f(0.01 / (0.012 * sqrt(1000)), 4)}; {f(0.01 / 0.012, 3)}; "
    f"{f(0.01 / (0.012 * 1000), 6)}")                                                                    # 51
put(f"P3 (beta 1.2073, SEs 0.0088 and 0.0185): {f((1.2073 - 1) / 0.0185, 1)}; {f((1.2073 - 1) / 0.0088, 1)}; "
    f"{f(1.2073 / 0.0185, 1)}")                                                                           # 52
put(f"P4: sqrt(20) {f(sqrt(20), 1, 2)}; Semiconductor NW(19)/classical on the overlap {f(ov_n / ov_c, 2)}")  # 53
put(f"P5 (beta 0.6, alpha 1.0 bp, r_f 2%, A 245.48): (1-beta) r_f/A {f(1e4 * 0.4 * 0.02 / 245.48, 3)} bp; Jensen "
    f"{f(1.0 - 1e4 * 0.4 * 0.02 / 245.48, 3)}; sign error {f(1.0 + 1e4 * 0.4 * 0.02 / 245.48, 3)}; beta ignored "
    f"{f(1.0 - 1e4 * 0.02 / 245.48, 3)}")                                                                # 54
pp = [0.004, 0.011, 0.019, 0.030, 0.20]
put(f"P6 rejections at 5%: Bonferroni {int(multipletests(pp, 0.05, 'bonferroni')[0].sum())}, Holm "
    f"{int(multipletests(pp, 0.05, 'holm')[0].sum())}, BH {int(multipletests(pp, 0.05, 'fdr_bh')[0].sum())}, default "
    f"'hs' {int(multipletests(pp, 0.05)[0].sum())}")                                                     # 55
xb, sxp = round(100 * float(x25.mean()), 4), round(100 * float(x25.std(ddof=0)), 4)
xt = round(100 * float(x25[j7]), 4)
put(f"P8 from printed inputs (mean {xb}%, s_x {sxp}%, x_t {xt}%, T 243): h "
    f"{f(1 / 243 + (xt - xb) ** 2 / (243 * sxp**2), 4)}; sum of leverages "
    f"{float(np.trace(design(x25) @ f25.zi @ design(x25).T)):.6f}")                                     # 56
put(f"P9 (NT$50m, beta 0.75, R2 0.5, TX 20,000, NT$200 a point): contracts {0.75 * 50e6 / (200 * 20000):.3f}; notional "
    f"{50e6 / (200 * 20000):.2f}; residual SD factor {f(sqrt(0.5), 4)}")                               # 57
put(f"batch SE from 20 batches: relative error about 1/sqrt(2 x 20) = {f(100 / sqrt(40), 0)}%; LM18's batch / model "
    f"sandwich {f(bse / se_sand, 2)}; White / model sandwich {f(f18.se_w[1] / se_sand, 2)}; classical / model sandwich "
    f"{f(f18.se_c[1] / se_sand, 2)} ({f(100 * f18.se_c[1] / se_sand, 0)}%)")                            # 58

print("\n".join(OUT))
