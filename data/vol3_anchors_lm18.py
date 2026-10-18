"""LM18 anchors (Monte Carlo Simulation and the Bootstrap): every number the Stage 1 brief quotes.

Reads TR23 from data/processed/vol3_taiex.parquet (built and checked by data/vol3_series.py, which must run first):
the closes `tr`, 2003-01-02 -> 2026-10-08. Writes nothing.

Conventions (plans/vol-3.md, "Shared decisions"): T = 5,849 simple returns R_t = P_t / P_{t-1} - 1 from 2003-01-03,
log returns r_t = ln(1 + R_t); moments divide by T; years = calendar days / 365.25; A = T / years; five years is
m = round(5A) = 1,231 sessions. Counts against a threshold use the guard (<= -x + 1e-12, >= x - 1e-12) and are
recounted exactly with Fraction on the two-decimal closes. Each simulated experiment creates its generator once, at
its start, as np.random.default_rng([20261011, k]), k its stream number in the brief (E1 1, E2 2, E3 3 and E7, E5 5,
E6 6, E8 8, E9 9, E10 10 and Problem 12, common random numbers 11, X3 12, coverage 13, X7 14, the t extension 15);
the reproduction of LM12's lab keeps that lab's default_rng(20261011). LM12's printed S5 Cholesky factor
(lm12.md:441-445, % a day, 4 decimals) is a model parameter: the script loads no U28 data. Values the brief quotes
from LM5's printed text (lm05.md:581-603) are recomputed here.

Run from the repository root (an optional first argument gives the repository root):
    PYTHONUTF8=1 uv run python data/vol3_anchors_lm18.py
Prints one line per anchor, "A18-NN <value>", in ID order.
"""
import bisect
import math
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import polars as pl
from scipy import integrate, stats

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
HERE = ROOT / "data"
PROC = HERE / "processed"
SEED = 20261011
EPS = 1e-12
OUT: dict[str, str] = {}


def rng(k: int) -> np.random.Generator:
    """The generator of experiment k (shared decision "Simulation")."""
    return np.random.default_rng([SEED, k])


def put(name: str, *vals: object) -> None:
    assert name not in OUT, name
    OUT[name] = "; ".join(str(v) for v in vals)


def pct(x: float, d: int = 4) -> str:
    return f"{100 * x:.{d}f}%"


def se(y: np.ndarray) -> float:
    """Standard error of a mean of draws: standard deviation with divisor n, over sqrt(n)."""
    return float(y.std() / math.sqrt(y.size))


def lag1(x: np.ndarray) -> float:
    return float(np.corrcoef(x[1:], x[:-1])[0, 1])


# ------------------------------------------------------------------ TR23
df = pl.read_parquet(PROC / "vol3_taiex.parquet").sort("date")
dd = list(df["date"])
dates = [d.isoformat() for d in dd]
P = df["tr"].to_numpy()
R = P[1:] / P[:-1] - 1
assert np.allclose(R, df["R"].to_numpy()[1:], rtol=0, atol=1e-15)
r = np.log1p(R)
T = R.size
Pq = [Fraction(f"{x:.2f}") for x in P]
assert all(abs(float(q) - x) < 1e-9 for q, x in zip(Pq, P))
Rq = [Pq[i + 1] / Pq[i] - 1 for i in range(T)]
days = (dd[-1] - dd[0]).days
years = days / 365.25
A = T / years
Rbar, s = float(R.mean()), float(R.std())
rbar, sr = float(r.mean()), float(r.std())
put("sample", f"{P.size} closes {dates[0]} -> {dates[-1]}", f"T = {T} returns from {dates[1]}")
put("years_A", f"{days} days", f"{years:.6f} years", f"A = {A:.6f}")
put("Rbar_s", f"Rbar = {pct(Rbar, 7)}", f"s = {pct(s, 6)}")
put("rbar_sr", f"rbar = {pct(rbar, 7)}", f"s_r = {pct(sr, 6)}")

down3 = R <= -0.03 + EPS
down5 = R <= -0.05 + EPS
big = (R >= 0.03 - EPS) | down3
assert int(down3.sum()) == sum(1 for x in Rq if x <= Fraction(-3, 100))
assert int(down5.sum()) == sum(1 for x in Rq if x <= Fraction(-5, 100))
assert int(big.sum()) == sum(1 for x in Rq if abs(x) >= Fraction(3, 100))
ties = sum(1 for x in Rq if abs(x) in (Fraction(3, 100), Fraction(5, 100)))
put("counts", f"R <= -3%: {int(down3.sum())}", f"R <= -5%: {int(down5.sum())}", f"abs(R) >= 3%: {int(big.sum())}",
    "guard = Fraction recount", f"returns exactly at +-3% or +-5%: {ties}")
lam = int(big.sum()) / T
put("lambda", f"175/5849 = {lam:.6f}")
iw = int(R.argmin())
put("worst_day", f"{dates[1 + iw]}", f"R = {pct(float(R[iw]), 4)}")
before = sum(1 for d in dates[1:] if d < "2015-06-01")
put("regimes", f"before 2015-06-01: {before}", f"from 2015-06-01: {T - before}")

# ------------------------------------------------------------------ five-year windows (the case)
m5 = 5 * A
m = round(m5)
put("m", f"5A = {m5:.4f}", f"m = {m}")
nwin = P.size - m
Gw = P[m:] / P[:-m]
uw = np.flatnonzero(Gw < 1)
assert uw.size == sum(1 for i in range(nwin) if Pq[i + m] < Pq[i])
put("windows", f"{nwin} windows", f"{uw.size} under water", pct(uw.size / nwin, 4),
    f"last start {dates[nwin - 1]} -> {dates[nwin - 1 + m]}")
episodes = np.split(uw, np.flatnonzero(np.diff(uw) > 250) + 1)   # gaps inside an episode are under 30 sessions
assert len(episodes) == 2
put("episodes", *(f"starts {dates[e[0]]} -> {dates[e[-1]]} ({e.size} windows), ends {dates[e[0] + m]} -> "
                  f"{dates[e[-1] + m]}" for e in episodes))
i0, i1 = int(Gw.argmin()), int(Gw.argmax())
put("window_extremes", f"worst {Gw[i0]:.4f} ({dates[i0]} -> {dates[i0 + m]})",
    f"best {Gw[i1]:.4f} ({dates[i1]} -> {dates[i1 + m]})")
put("window_quantiles", " / ".join(f"{x:.4f}" for x in np.quantile(Gw, [0.05, 0.5, 0.95])))
lw = np.log(Gw)
put("window_spread", f"sd ln G (divisor {nwin}) {lw.std():.4f}", f"mean ln G {lw.mean():.4f}",
    f"m rbar {m * rbar:.4f}")
put("disjoint", f"years / 5 = {years / 5:.3f}")
cal_n = cal_under = 0
lens = []
for i, d0 in enumerate(dd):
    d1 = d0.replace(year=d0.year + 5, day=28) if (d0.month, d0.day) == (2, 29) else d0.replace(year=d0.year + 5)
    if d1 > dd[-1]:
        break
    j = bisect.bisect_right(dd, d1) - 1
    cal_n += 1
    cal_under += Pq[j] < Pq[i]
    lens.append(j - i)
put("calendar_windows", f"{cal_under} of {cal_n}", pct(cal_under / cal_n, 4), f"{min(lens)}-{max(lens)} sessions")

# ------------------------------------------------------------------ the model: iid normal daily log returns
z0 = -math.sqrt(m) * rbar / sr
p_ln = float(stats.norm.cdf(z0))
v = m * sr**2
EG = math.exp(m * (rbar + sr**2 / 2))
put("lognormal", f"z = {z0:.6f}", f"Pr(G<1) = {p_ln:.6f}")
gp, sp = 0.0005517, 0.012107
zp = -math.sqrt(m) * gp / sp
put("lognormal_printed", f"from g = 0.05517%, sigma_r = 1.2107%: z = {zp:.6f}", f"Phi(z) = {stats.norm.cdf(zp):.6f}",
    f"E G = {math.exp(m * (gp + sp**2 / 2)):.6f}", f"m sigma_r^2 = {m * sp**2:.6f}", f"m g = {m * gp:.6f}")
qln = np.exp(m * rbar + math.sqrt(m) * sr * stats.norm.ppf([0.05, 0.5, 0.95]))
put("lognormal_G", f"E G = {EG:.6f}", "quantiles " + " / ".join(f"{x:.4f}" for x in qln),
    f"sqrt(m) s_r = {math.sqrt(v):.4f}", f"m s_r^2 = {v:.6f}", f"m rbar = {m * rbar:.6f}")

# ------------------------------------------------------------------ E1 (stream 1): same seed, same answer
hits1 = [int((np.random.default_rng([s_, 1]).standard_normal(10_000) <= -2).sum()) for s_ in (SEED, SEED, SEED + 1)]
put("E1", f"[20261011, 1]: {hits1[0]}, rerun {hits1[1]}", f"[20261012, 1]: {hits1[2]}",
    f"Phi(-2) = {stats.norm.cdf(-2):.6f}", f"expected {10_000 * stats.norm.cdf(-2):.2f}")

# ------------------------------------------------------------------ E2 (stream 2): inverse transform
u3 = rng(2).random(3)
Rs = np.sort(R)
ranks = [math.ceil(T * u) for u in u3]
assert ranks == [math.ceil(T * round(float(u), 6)) for u in u3]
emp = []
for j in ranks:
    x = Rs[j - 1]
    assert int((R == x).sum()) == 1
    emp.append(f"{j} -> {pct(float(x), 4)} ({dates[1 + int(np.flatnonzero(R == x)[0])]})")
put("E2_u", ", ".join(f"{u:.8f}" for u in u3))
put("E2_exp", "waits " + ", ".join(f"{-math.log(1 - u) / lam:.4f}" for u in u3),
    "from u to 6 dp and 0.02992: " + ", ".join(f"{-math.log(1 - round(float(u), 6)) / 0.02992:.4f}" for u in u3),
    f"1/lambda = {1 / lam:.4f} ({1 / 0.02992:.4f})", f"ln2/lambda = {math.log(2) / lam:.4f} ({math.log(2) / 0.02992:.4f})")
put("E2_emp", *emp)

# ------------------------------------------------------------------ E3 (stream 3): the case by simulation
g3 = rng(3)
S3 = np.empty(10_000)
for c in range(0, 10_000, 1000):
    S3[c:c + 1000] = (rbar + sr * g3.standard_normal((1000, m))).sum(axis=1)
Y3 = (S3 < 0).astype(float)
p3, se3 = float(Y3.mean()), se(Y3)
G3 = np.exp(S3)
put("E3", f"{int(Y3.sum())} of 10000", f"{p3:.6f} +- {se3:.6f}", f"interval {p3 - 1.96 * se3:.6f} - {p3 + 1.96 * se3:.6f}",
    f"covers {abs(p3 - p_ln) <= 1.96 * se3}")
put("E3_G", f"mean G {G3.mean():.6f} +- {se(G3):.6f}")

# ------------------------------------------------------------------ E4: LM12's lab gap with the printed L
L = np.array([[1.5243, 0, 0, 0, 0], [0.6998, 0.9960, 0, 0, 0], [0.4336, 0.4779, 0.8594, 0, 0],
              [0.7238, 0.5162, 0.1831, 1.3034, 0], [0.6415, 0.5995, 0.2050, 0.1109, 1.4358]]) / 100
Sig = L @ L.T
n4 = 4382
sim = np.random.default_rng(SEED).standard_normal((n4, 5)) @ L.T
Ssim = np.cov(sim, rowvar=False, ddof=0)
put("E4_gap", f"{float(np.linalg.norm(Ssim - Sig) / np.linalg.norm(Sig)):.6f}")
put("E4_entry", f"Semiconductor simulated / model variance - 1 = {pct(float(Ssim[0, 0] / Sig[0, 0] - 1), 3)}",
    f"sqrt(2/4382) = {pct(math.sqrt(2 / n4), 3)}")
F2, tr = float(np.linalg.norm(Sig) ** 2), float(np.trace(Sig))
cst = math.sqrt(1 + tr**2 / F2)


def rms_centred(n: int) -> float:
    """Exact RMS relative gap of np.cov(ddof=0) for n iid N(0, Sig) draws (Wishart moments)."""
    return math.sqrt(((n - 1) / n**2) * (F2 + tr**2) + F2 / n**2) / math.sqrt(F2)


put("E4_formula", f"centring changes the RMS gap at n = 100 by {pct(1 - rms_centred(100) / (cst / 10), 3)}",
    f"tr(Sigma)^2 / Frobenius(Sigma)^2 = {tr**2 / F2:.4f}", f"sqrt(1 + .) = {cst:.4f}",
    f"n = 4382: {cst / math.sqrt(n4):.5f} (centred {rms_centred(n4):.5f})",
    f"n = 50000: {cst / math.sqrt(50_000):.5f} (centred {rms_centred(50_000):.5f})")

# ------------------------------------------------------------------ X3 (stream 12): the 1/sqrt(n) rate
g12 = rng(12)
sizes = (100, 500, 1000, 4382, 10_000, 50_000)
rms_run = []
q_4382 = np.zeros(2)
for n_ in sizes:
    gs = np.empty(200)
    for i in range(200):
        x = g12.standard_normal((n_, 5)) @ L.T
        gs[i] = np.linalg.norm(np.cov(x, rowvar=False, ddof=0) - Sig) / np.linalg.norm(Sig)
    rms_run.append(math.sqrt(float((gs**2).mean())))
    if n_ == 4382:
        q_4382 = np.quantile(gs, [0.05, 0.95])
put("X3", "RMS of 200 runs " + ", ".join(f"{x:.4f}" for x in rms_run),
    "(18.9) " + ", ".join(f"{cst / math.sqrt(n_):.4f}" for n_ in sizes),
    f"5-95% of runs at 4382: {q_4382[0]:.4f}-{q_4382[1]:.4f}")

# ------------------------------------------------------------------ LM5's tail, quadrature, Monte Carlo (E5, stream 5)
kk = 4.1074386
pk = float(stats.norm.cdf(-kk))
put("tail_exact", f"Phi(-4.1074386) = {pk:.7e}",
    f"quad relative difference {abs(integrate.quad(stats.norm.pdf, -np.inf, -kk)[0] / pk - 1):.1e}")
z5 = rng(5).standard_normal(1_000_000)
h5 = int((z5 <= -kk).sum())
p5 = h5 / 1e6
se5 = math.sqrt(p5 * (1 - p5) / 1e6)
put("E5", f"{h5} hits", f"{p5:.3e} +- {se5:.3e}", f"expected {1e6 * pk:.2f}",
    f"relative SE exact {math.sqrt((1 - pk) / (1e6 * pk)):.4f}, run {se5 / p5:.4f}",
    f"n for 1.96 SE = 1%: {(1.96 / 0.01) ** 2 * (1 - pk) / pk:.4e}",
    f"n for relative SE 1.2e-6: {(1 / 1.2e-6) ** 2 * (1 - pk) / pk:.4e}")
put("zero_hits", f"(1-p)^100000 = {(1 - pk) ** 100_000:.4f}", f"(1-p)^10000 = {(1 - pk) ** 10_000:.4f}")
simpson = {8: 9.69e-6, 16: 1.23e-6, 32: 9.47e-8, 64: 6.23e-9, 128: 3.94e-10, 256: 2.47e-11, 512: 1.55e-12,
           1024: 9.67e-14}
put("X4_simpson", ", ".join(f"{N + 1}: {e / 2.000355e-5:.4e}" for N, e in simpson.items()))
var_is = math.exp(kk**2) * float(stats.norm.cdf(-2 * kk)) - pk**2
put("X4_mc", f"plain sqrt((1-p)/p) = {math.sqrt((1 - pk) / pk):.2f}", f"IS {math.sqrt(var_is) / pk:.4f}")

# ------------------------------------------------------------------ E6 (stream 6): antithetic paths
Z6 = rng(6).standard_normal((5000, m))
Sa = (rbar + sr * Z6).sum(axis=1)
Sb = (rbar - sr * Z6).sum(axis=1)
Ga, Gb = np.exp(Sa), np.exp(Sb)
pairG = (Ga + Gb) / 2
rho_m = -math.exp(-v)
put("E6_G", f"{pairG.mean():.6f} +- {se(pairG):.6f}", f"run corr {np.corrcoef(Ga, Gb)[0, 1]:.4f}",
    f"exact rho {rho_m:.4f}", f"exact ratio {1 / (1 + rho_m):.4f}")
Ia, Ib = (Sa < 0).astype(float), (Sb < 0).astype(float)
pairI = (Ia + Ib) / 2
rho_i = -p_ln / (1 - p_ln)
put("E6_Pr", f"{pairI.mean():.6f} +- {se(pairI):.6f}", f"run corr {np.corrcoef(Ia, Ib)[0, 1]:.4f}",
    f"exact rho {rho_i:.4f}", f"exact ratio {1 / (1 + rho_i):.4f}")

# ------------------------------------------------------------------ E7: control variate on E3's paths
C = np.cov(G3, S3, ddof=0)
rho_x = math.sqrt(v / (math.exp(v) - 1))
Gc = G3 - C[0, 1] / C[1, 1] * (S3 - m * rbar)
put("E7_G", f"beta_hat {C[0, 1] / C[1, 1]:.4f}", f"rho_hat {C[0, 1] / math.sqrt(C[0, 0] * C[1, 1]):.4f}",
    f"controlled {Gc.mean():.6f} +- {se(Gc):.6f}", f"exact rho {rho_x:.4f}", f"exact ratio {1 / (1 - rho_x**2):.4f}",
    f"from rho 0.955: {1 / (1 - 0.955**2):.4f}")
Ci = np.cov(Y3, S3, ddof=0)
Yc = Y3 - Ci[0, 1] / Ci[1, 1] * (S3 - m * rbar)
rho_xi = -float(stats.norm.pdf(z0)) / math.sqrt(p_ln * (1 - p_ln))
put("E7_Pr", f"exact rho {rho_xi:.4f}", f"run rho {Ci[0, 1] / math.sqrt(Ci[0, 0] * Ci[1, 1]):.4f}",
    f"exact ratio {1 / (1 - rho_xi**2):.4f}", f"controlled {Yc.mean():.6f} +- {se(Yc):.6f}")

# ------------------------------------------------------------------ E8 (stream 8): importance sampling
x8 = -kk + rng(8).standard_normal(10_000)
y8 = (x8 <= -kk) * np.exp(kk * x8 + kk**2 / 2)
p8, se8 = float(y8.mean()), se(y8)
put("E8", f"{int((x8 <= -kk).sum())} draws in the tail", f"{p8:.5e} +- {se8:.4e}", f"relative SE {se8 / p8:.4f}",
    f"covers {abs(p8 - pk) <= 1.96 * se8}")
put("E8_var", f"per-draw variance IS {var_is:.5e}", f"plain {pk * (1 - pk):.5e}", f"ratio {pk * (1 - pk) / var_is:.1f}",
    f"from 3 significant digits {2.00e-5 / 1.85e-9:.1f}", f"plain draws for 10,000 {1e4 * pk * (1 - pk) / var_is:.4e}")
shift_se = [math.sqrt(math.exp(sh**2) * float(stats.norm.cdf(-kk - sh)) - pk**2) / pk for sh in (kk / 2, 2 * kk)]
put("IS_shifts", f"per-draw relative SE at shift k/2 {shift_se[0]:.4f}", f"at 2k {shift_se[1]:.2f}")
put("anti_tail", f"corr -p/(1-p) = {-pk / (1 - pk):.4e}", f"variance ratio {1 / (1 - pk / (1 - pk)):.6f}")

# ------------------------------------------------------------------ E9 (stream 9): bootstrap of the mean day
g9 = rng(9)
means = np.empty(10_000)
for c in range(0, 10_000, 500):
    means[c:c + 500] = R[g9.integers(0, T, size=(500, T))].mean(axis=1)
put("E9", f"mean of resample means {pct(float(means.mean()), 7)}", f"sd {pct(float(means.std()), 7)}",
    f"s/sqrt(T) {pct(s / math.sqrt(T), 7)}, from 1.2084%: {1.2084 / math.sqrt(T):.7f}%",
    f"means <= 0: {int((means <= 0).sum())}")

# ------------------------------------------------------------------ E10 (stream 10): the case by bootstrap
g10 = rng(10)
S10, G10 = np.empty(10_000), np.empty(10_000)
for c in range(0, 10_000, 500):
    idx = g10.integers(0, T, size=(500, m))
    S10[c:c + 500] = r[idx].sum(axis=1)
    G10[c:c + 500] = np.prod(1 + R[idx], axis=1)
Y10 = (S10 < 0).astype(float)
p10, se10 = float(Y10.mean()), se(Y10)
put("E10", f"{int(Y10.sum())} of 10000", f"{p10:.6f} +- {se10:.6f}",
    "quantiles " + " / ".join(f"{x:.4f}" for x in np.quantile(G10, [0.05, 0.5, 0.95])), f"sd ln G {S10.std():.4f}")
C10 = np.cov(G10, S10, ddof=0)
Gc10 = G10 - C10[0, 1] / C10[1, 1] * (S10 - m * rbar)
put("E10_mean", f"(1+Rbar)^m = {(1 + Rbar) ** m:.6f}", f"from 0.062505%: {1.00062505**m:.6f}",
    f"from 0.0625%: {1.000625**m:.6f}", f"estimate {G10.mean():.6f} +- {se(G10):.6f}",
    f"controlled {Gc10.mean():.6f} +- {se(Gc10):.6f}")
put("median_path", f"exp(m rbar) = {math.exp(m * rbar):.6f}", f"from 0.055170%: {math.exp(m * 0.00055170):.6f}")
g10b = rng(10)
chunked = np.concatenate([g10b.integers(0, T, size=(500, m)) for _ in range(20)])
put("chunking", f"memory of 10000 x {m} float64: {10_000 * m * 8 / 1e6:.2f} MB",
    f"20 chunks of 500 == one call of 10000: {bool((chunked == rng(10).integers(0, T, size=(10_000, m))).all())}")
del chunked

# ------------------------------------------------------------------ X7 (stream 14): what resampling destroys
ym = [d[:7] for d in dates[1:]]
months = sorted(set(ym))
mi = np.searchsorted(months, ym)
cnt = np.bincount(mi, weights=big.astype(float), minlength=len(months))
top = [months[i] for i in np.flatnonzero(cnt == cnt.max())]
put("months_data", "months by count 0..8: " + ", ".join(str(int(x)) for x in np.bincount(cnt.astype(int))),
    f"{len(months)} months {months[0]} -> {months[-1]}", f"mean {cnt.mean():.4f}", f"variance {cnt.var():.4f}",
    f"max {int(cnt.max())} in {', '.join(top)}")
g14 = rng(14)
vars_, maxs = np.empty(1000), np.empty(1000)
acs = np.empty(1000)
pmf = np.zeros(40)
absr = np.abs(r)
for b in range(1000):
    idx = g14.integers(0, T, size=T)
    c_ = np.bincount(mi, weights=big[idx].astype(float), minlength=len(months))
    vars_[b], maxs[b] = c_.var(), c_.max()
    pmf[:int(c_.max()) + 1] += np.bincount(c_.astype(int))
    acs[b] = lag1(absr[idx])
pmf /= 1000
put("months_boot", "expected months by count 0..8: " + ", ".join(f"{x:.3f}" for x in pmf[:9]),
    f"variance: mean {vars_.mean():.4f}, highest {vars_.max():.4f}", f"resamples with a month of 8 or more: {int((maxs >= 8).sum())}")
put("lag1_data", f"corr(abs(r_t), abs(r_t+1)) = {lag1(absr):.4f}")
put("lag1_boot", f"mean {acs.mean():.5f}", f"sd {acs.std():.5f}")

# ------------------------------------------------------------------ problems, knowledge checks
put("KC3", f"u = 0.5 -> rank {math.ceil(T * 0.5)} -> {pct(float(Rs[math.ceil(T * 0.5) - 1]), 4)}",
    f"np.median {pct(float(np.median(R)), 4)}")
put("KC4", f"p(1-p)/0.001^2 = {p_ln * (1 - p_ln) / 1e-6:.0f}", f"from 5.49%: {0.0549 * 0.9451 / 1e-6:.0f}")
put("KC7", f"(1-1/T)^T = {(1 - 1 / T) ** T:.6f}", f"complement {1 - (1 - 1 / T) ** T:.6f}")
p3_ = float(stats.norm.cdf(-3))
put("P2", f"Phi(-3) = {p3_:.6e}", f"SE {math.sqrt(p3_ * (1 - p3_) / 1e6):.4e}", f"variance {p3_ * (1 - p3_) / 1e6:.4e}",
    f"without n {math.sqrt(p3_ * (1 - p3_)):.4f}")
put("P3", "-lambda ln(1-U) has mean lambda = 0.02992 sessions", f"1 - exp(-0.02992) = {1 - math.exp(-0.02992):.4f}")
put("P4", "sorted -2.5, -0.8, +0.3, +0.6, +1.2", "ceil(5u) for u = 0.37, 0.95, 0.18: "
    + ", ".join(str(math.ceil(5 * u)) for u in (0.37, 0.95, 0.18)))
put("P5", f"0.0096 sqrt(1 - 0.835) = {0.0096 * math.sqrt(1 - 0.835):.5f}",
    f"0.0096 sqrt(1 - 0.058) = {0.0096 * math.sqrt(1 - 0.058):.5f}")
put("P6", f"1/(1-0.95^2) = {1 / (1 - 0.95**2):.4f}", f"1/(1-0.95) = {1 / (1 - 0.95):.4f}", f"1/0.95^2 = {1 / 0.95**2:.4f}")
v3 = math.exp(9) * float(stats.norm.cdf(-6))
put("P7", f"Phi(-3) = {p3_:.5e}", f"e^9 Phi(-6) = {v3:.5e}", f"IS variance {v3 - p3_**2:.5e}",
    f"plain {p3_ * (1 - p3_):.5e}", f"ratio {p3_ * (1 - p3_) / (v3 - p3_**2):.2f}")
put("P10", f"n^(-4/m) falls faster than n^(-1/2) iff m < 8; Monte Carlo's order is better iff m > {4 / 0.5:.0f}")
pa, pb = float(stats.norm.cdf(-2.01)), float(stats.norm.cdf(-1.99))
pa7, pb7 = round(pa, 7), round(pb, 7)
put("CRN_formula", f"Phi(-2.01) = {pa:.9f}", f"Phi(-1.99) = {pb:.9f}", f"difference {pb - pa:.9f}",
    f"from 7 decimals {pb7 - pa7:.7f}", f"from 6 decimals {round(pb, 6) - round(pa, 6):.6f}",
    f"SE independent {math.sqrt(pa * (1 - pa) / 1e5 + pb * (1 - pb) / 1e5) / 0.02:.5f}",
    f"SE common {math.sqrt((pb - pa) * (1 - (pb - pa)) / 1e5) / 0.02:.5f}", f"-phi(2) = {-stats.norm.pdf(2):.6f}")

# ------------------------------------------------------------------ lab: common random numbers (stream 11)
g11 = rng(11)
ind, com = [], []
for _ in range(200):
    a, b2 = g11.standard_normal(100_000), g11.standard_normal(100_000)
    ind.append(((a <= -2.01).mean() - (b2 <= -1.99).mean()) / 0.02)
    com.append(((a <= -2.01).mean() - (a <= -1.99).mean()) / 0.02)
put("CRN_runs", f"sd over 200 repetitions: independent {np.std(ind):.5f}", f"common {np.std(com):.5f}")

# ------------------------------------------------------------------ lab: method dependence (stream 2)
put("methods", "norm.ppf(u) " + ", ".join(f"{x:.4f}" for x in stats.norm.ppf(u3)),
    "standard_normal(3) " + ", ".join(f"{x:.4f}" for x in rng(2).standard_normal(3)))

# ------------------------------------------------------------------ lab: coverage (stream 13)
g13 = rng(13)
cover = 0
for _ in range(1000):
    y = (m * rbar + math.sqrt(m) * sr * g13.standard_normal(1000) < 0).astype(float)
    cover += abs(y.mean() - p_ln) <= 1.96 * se(y)
put("coverage", f"{cover} of 1000", f"expected hits a run {1000 * p_ln:.1f}")

# ------------------------------------------------------------------ lab extension (stream 15): Student t model
nu, loc, scale = (float(x) for x in stats.t.fit(R))
put("t_fit", f"nu {nu:.4f}", f"loc {pct(loc, 5)}", f"scale {pct(scale, 5)}")
g15 = rng(15)
St = np.empty(10_000)
ruined = 0
for c in range(0, 10_000, 1000):
    Rt = loc + scale * g15.standard_t(nu, size=(1000, m))
    bad = (Rt <= -1).any(axis=1)
    ruined += int(bad.sum())
    St[c:c + 1000] = np.where(bad, -np.inf, np.log1p(np.where(Rt <= -1, 0.0, Rt)).sum(axis=1))
Yt = (St < 0).astype(float)
put("t_model", f"Pr(G<1) {Yt.mean():.5f} +- {se(Yt):.5f}", f"paths with a day <= -100%: {ruined}")

# ------------------------------------------------------------------ pitfall: multivariate_normal (stream 2)
mvn = rng(2).multivariate_normal(np.zeros(5), Sig, size=3)
col = rng(2).standard_normal((3, 5)) @ L.T
put("mvn", f"multivariate_normal and z @ L.T differ: {bool(np.abs(mvn - col).max() > 1e-12)}")

# ------------------------------------------------------------------ print in the brief's order
ORDER = ["tail_exact", "E4_gap", "sample", "years_A", "counts", "m", "windows", "episodes", "disjoint", "lognormal",
         "E3", "E10", "E4_formula", "KC3", "KC4", "zero_hits", "anti_tail", "KC7", "chunking", "window_extremes", "X3",
         "X4_simpson", "X4_mc", "E5", "E8", "E8_var", "lognormal_G", "E3_G", "E6_G", "E7_G", "E6_Pr", "E7_Pr",
         "window_quantiles", "window_spread", "months_data", "months_boot", "lag1_data", "lag1_boot", "E1", "E2_u",
         "lambda", "E2_exp", "E2_emp", "rbar_sr", "lognormal_printed", "E4_entry", "Rbar_s", "E9", "E10_mean", "P2",
         "P3", "P4", "P5", "P6", "P7", "median_path", "P10", "CRN_formula", "CRN_runs", "methods", "coverage", "t_fit",
         "t_model", "IS_shifts", "calendar_windows", "regimes", "worst_day", "mvn"]
assert sorted(ORDER) == sorted(OUT), set(ORDER) ^ set(OUT)
for i, name in enumerate(ORDER, 1):
    print(f"A18-{i:02d} {OUT[name]}")
