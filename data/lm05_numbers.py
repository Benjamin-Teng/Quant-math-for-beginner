"""Every number quoted in LM5 (Integration), computed from first principles and from the verified 0050 series.

Run from the repository root, after data/build_series.py:

    uv run python data/lm05_numbers.py

Prints one labelled line per quoted number (with the inputs a printed chain needs) and writes
data/processed/lm05_numbers.json, a record of the main outputs for locating numbers.
"""
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl
from scipy import integrate, special, stats

HERE = Path(__file__).resolve().parent
OUT: dict[str, Any] = {}


def P(label, *vals):
    print(f"{label:<34s}", *vals)


def norm_cdf(z):
    return 0.5 * special.erfc(-z / math.sqrt(2.0))


def norm_pdf(z):
    return math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)


def sig(x, d):
    """x rounded to d significant figures, as a string m.mmm e±k (for chain checks)."""
    e = math.floor(math.log10(abs(x)))
    m_ = round(x / 10**e, d - 1)
    if abs(m_) >= 10:
        m_ /= 10
        e += 1
    return f"{m_:.{d - 1}f}e{e}"


# ----------------------------------------------------------------------------------------------- data
df = pl.read_parquet(HERE / "processed" / "etf_daily_returns.parquet")
dates = [str(d) for d in df["date"].to_list()]
R = df["R_0050"].to_numpy()
n = len(R)
mu, s = R.mean(), R.std()                      # population standard deviation (MLE), as in LM3/LM4
s1 = R.std(ddof=1)
years = (np.datetime64(dates[-1]) - np.datetime64("2014-10-31")).astype(int) / 365.25
A = n / years                                  # returns per year in this sample (book-wide A)
P("== DATA", f"n={n} first={dates[0]} last={dates[-1]} years={years:.2f} A={A:.1f}")
P("mean R (mu_hat)", f"{mu:.6%}  ({mu * 1e4:.2f} bp)  decimal {mu:.9f}")
P("s population / T-1", f"{s:.6%} / {s1:.6%}  decimal s {s:.10f}")
P("skew / excess kurtosis", f"{((R - mu) ** 3).mean() / s**3:.3f} / {((R - mu) ** 4).mean() / s**4 - 3:.2f}")
OUT.update(n=n, mu=mu, s=s, years=years, A=A)

# 0050-only series (all 2,906 0050 trading days) for the robustness note
m = pl.read_csv(HERE / "processed" / "raw_merged_full.csv").sort("date")
a = m.filter(pl.col("p0050").is_not_null()).select("date", "p0050", "d0050", "s0050")
a = a.with_columns(
    ((pl.col("p0050") + pl.col("d0050")) / (pl.col("p0050").shift(1) / pl.col("s0050")) - 1).alias("R")
).drop_nulls("R")
R_only = a["R"].to_numpy()

# ----------------------------------------------------------------------------------------------- case
K = -0.05
z5 = (K - mu) / s
p5 = norm_cdf(z5)
days5 = R <= K + 1e-12
P("== CASE", "")
P("z(-5%) pop / T-1", f"{z5:.7f} / {(K - mu) / s1:.4f}")
P("  chain (-0.05-0.000871205)/0.0123851406", f"{(-0.05 - 0.000871205) / 0.0123851406:.7f}")
P("Phi(z) at z5 / at -4.1074386", f"{p5:.4e} / {norm_cdf(-4.1074386):.6e}")
P("T-1 sd: z, probability ratio - 1", f"{(K - mu) / s1:.4f}  {norm_cdf((K - mu) / s1) / p5 - 1:+.2%}"
  f"  (at printed z -4.1067: {norm_cdf(-4.1067) / norm_cdf(-4.1074386) - 1:+.2%})")
P("  chain T-1 sd 1.23873%: z", f"{(-0.05 - 0.000871205) / 0.0123873:.6f}  s1 to 5 dp {s1:.5%}")
P("expected days in n", f"{n * p5:.4f}  chain 2902*2.0004e-5={2902 * 2.0004e-5:.4f}")
P("return period (years)", f"{1 / (p5 * A):.1f}  chain 1/(243.1*2.0004e-5)={1 / (243.1 * 2.0004e-5):.1f}"
  f"  trading days {1 / p5:,.0f}")
P("actual count", int(days5.sum()), "  share", f"{days5.mean():.4%}", "  ratio",
  f"{days5.sum() / (n * p5):.0f}  chain 9/0.0581={9 / 0.0581:.1f}")
P("actual: one every (years)", f"{years / days5.sum():.2f}   trading days {n / days5.sum():.0f}")
case_rows: list[dict[str, Any]] = []
for d, x in zip(np.array(dates)[days5], R[days5], strict=True):
    z = (x - mu) / s
    pz = norm_cdf(z)
    zr = round(z, 3)
    case_rows.append({"date": str(d), "R": float(x), "z": float(z), "p": float(pz), "years": float(1 / (pz * A))})
    P("  day", d, f"R={x:.3%} z={z:.3f} P={sig(pz, 2)} (from printed z {sig(norm_cdf(zr), 2)}) once in "
      f"{sig(1 / (pz * A), 2)} yr (from printed z {sig(1 / (norm_cdf(zr) * 243.1), 2)})")
OUT["case_rows"] = case_rows
P("summary row: z, P, years", f"z={z5:.4f} P={sig(p5, 2)} years={1 / (p5 * A):.0f} (from printed z -4.1074: "
  f"{1 / (norm_cdf(-4.1074) * 243.1):.1f}, expected days {2902 * norm_cdf(-4.1074):.3f})")
P("mean of the nine", f"{R[days5].mean():.3%}")
mu_o, s_o = R_only.mean(), R_only.std()
P("0050-only n, exp, count", len(R_only), f"{len(R_only) * norm_cdf((K - mu_o) / s_o):.4f}",
  int((R_only <= K + 1e-12).sum()))
P("merged common-day return 2026-03-31", f"{R[dates.index('2026-03-31')]:.4%}  (0050 sessions dropped:"
  f" {sorted(set(a['date'].to_list()) - set(dates) - {'2014-10-31'})})")
up5 = int((R >= 0.05 - 1e-12).sum())
P("upper tail: R>=+5% actual/exp", up5, f"{n * norm_cdf(-(0.05 - mu) / s):.4f}")

# ----------------------------------------------------------------------------------------------- thresholds table
P("== THRESHOLD TABLE (lower tail)", "")
nu = 3
sc_t = s * math.sqrt((nu - 2) / nu)
thr: list[dict[str, Any]] = []
for k in [-0.02, -0.03, -0.04, -0.05, -0.06, -0.07, -0.08, -0.09, -0.10]:
    z = (k - mu) / s
    pz = norm_cdf(z)
    act = int((R <= k + 1e-12).sum())
    act_o = int((R_only <= k + 1e-12).sum())
    pt = stats.t.cdf((k - mu) / sc_t, nu)
    thr.append({"k": k, "z": z, "p": pz, "exp": n * pz, "act": act, "t3": n * pt})
    P(f"  kappa={k:+.0%}", f"z={z:.3f} p={sig(pz, 2)} (from printed z {sig(norm_cdf(round(z, 3)), 2)}) "
      f"exp={n * pz:.4g} act={act} (only {act_o}) ratio={act / (n * pz):.3g} t3={n * pt:.2f}")
OUT["thr"] = thr
P("t3 scale (decimal)", f"{sc_t:.6f}")

# sigma that would make the normal model expect 9 days at -5%, and its prediction at -2%
z9 = stats.norm.ppf(9 / n)
sig9 = (K - mu) / z9
P("sigma for 9 days", f"z={z9:.4f} sigma={sig9:.4%} annualized={sig9 * math.sqrt(A):.1%}"
  f"  chain 0.050871/2.7369={0.050871 / 2.7369:.4%}")
P("  that sigma at -2% / -3%", f"{n * norm_cdf((-0.02 - mu) / sig9):.0f} days (actual {(R <= -0.02 + 1e-12).sum()})"
  f" / {n * norm_cdf((-0.03 - mu) / sig9):.0f} days (actual {(R <= -0.03 + 1e-12).sum()})")

# ----------------------------------------------------------------------------------------------- Mills ratio
P("== MILLS (omega = -z)", "")
aa = -z5
ph = norm_pdf(aa)
P("omega", f"{aa:.7f}")
P("phi(omega)", f"{ph:.4e}   exponent omega^2/2={aa * aa / 2:.6f}")
P("upper phi/omega", f"{ph / aa:.4e}  chain 8.6578e-5/omega={8.6578e-5 / aa:.4e}")
P("1 - 1/omega^2", f"{1 - 1 / aa**2:.5f}  (1/omega^2={1 / aa**2:.4f})")
P("lower phi/omega(1-1/omega^2)", f"{ph / aa * (1 - 1 / aa**2):.4e}  chain 2.1078e-5*0.94073={2.1078e-5 * 0.94073:.4e}")
P("Gordon lower phi/(omega+1/omega)", f"{ph / (aa + 1 / aa):.4e}")
P("three-term (1-1/w^2+3/w^4)", f"{ph / aa * (1 - 1 / aa**2 + 3 / aa**4):.4e}")
P("exact Q(a)", f"{p5:.4e}  rel. err upper {(ph / aa - p5) / p5:+.2%} lower {(ph / aa * (1 - 1 / aa**2) - p5) / p5:+.2%}"
  f"  chain {2.1078 / 2.0004 - 1:+.2%} {1.9829 / 2.0004 - 1:+.2%}")
OUT.update(z5=z5, p5=p5)

# ----------------------------------------------------------------------------------------------- FTC example: sensitivity to sigma
P("== FTC EXAMPLE: dP/dsigma", "")
el = -z5 * norm_pdf(z5) / p5
P("phi(z)/Phi(z)", f"{norm_pdf(z5) / p5:.4f} (4 s.f. {norm_pdf(z5) / p5:.3f}; chain 8.6578/2.0004={8.6578 / 2.0004:.4f})")
P("elasticity dlnP/dln sigma", f"{el:.2f}  chain 4.1074386*4.328={4.1074386 * 4.328:.3f}")
P("dP/dsigma (per 1.0 of sigma)", f"{norm_pdf(z5) * (-z5) / s:.5f}  per 0.1pp: {norm_pdf(z5) * (-z5) / s * 0.001:.3e}")
s10 = 1.1 * s
z10 = (K - mu) / s10
p10 = norm_cdf(z10)
P("sigma +10%", f"sigma={s10:.4%} z={z10:.5f} P={p10:.3e} ratio={p10 / p5:.2f} (+{p10 / p5 - 1:.0%}) exp days={n * p10:.3f}")
P("  chain z=-4.1074386/1.1, Phi there", f"{-4.1074386 / 1.1:.5f}  {norm_cdf(-3.73404):.3e}  ratio 9.422/2.0004="
  f"{9.422 / 2.0004:.2f}")
P("linear estimate +10%", f"+{el * 0.10:.0%}")
P("log-linear exp(el*ln1.1)", f"x{math.exp(el * math.log(1.1)):.2f}  chain 17.78*ln1.1={17.78 * math.log(1.1):.4f}"
  f" exp(1.6946)={math.exp(1.6946):.2f}")
el10 = -z10 * norm_pdf(z10) / p10
P("el*ln(1.1), elasticity at new z", f"{el * math.log(1.1):.2f}  new elasticity {el10:.2f}"
  f"  avg-el factor {math.exp(0.5 * (el + el10) * math.log(1.1)):.2f}")

# ----------------------------------------------------------------------------------------------- the Riemann-sum example (label riemann)
P("== RIEMANN EXAMPLE: r(t)=2%-0.5%e^{-2t}", "")


def rt(t):
    return 0.02 - 0.005 * np.exp(-2 * t)


I1 = 0.02 - 0.0025 * (1 - math.exp(-2))
P("exact integral", f"{I1:.8f}  factor {math.exp(I1):.6f}  r(0)={rt(0):.4%} r(1)={rt(1):.4%}")
ex1 = []
for nn in [4, 12, 365]:
    h = 1 / nn
    t = np.arange(nn) * h
    L = rt(t).sum() * h
    Rr = rt(t + h).sum() * h
    M = rt(t + h / 2).sum() * h
    ex1.append({"n": nn, "L": L, "R": Rr, "M": M})
    P(f"  N={nn}", f"L={L:.8f} ({(L - I1) * 1e4:+.4f} bp)  R={Rr:.8f} ({(Rr - I1) * 1e4:+.4f} bp)"
      f"  M={M:.8f} ({(M - I1) * 1e4:+.6f} bp)")
P("  lead terms N=4", f"(dt/2)(f(b)-f(a))={0.125 * (rt(1) - rt(0)) * 1e4:.4f} bp"
  f"  (dt^2/24)(f'(b)-f'(a))={(0.25**2 / 24) * (0.01 * math.exp(-2) - 0.01) * 1e4:.5f} bp")
P("  factor L4 / exact", f"{math.exp(ex1[0]['L']):.6f} / {math.exp(I1):.6f}")
P("  NT$ on 1,000,000", f"exact {1e6 * math.exp(I1):,.0f}  L4 {1e6 * math.exp(ex1[0]['L']):,.0f}"
  f"  R4 {1e6 * math.exp(ex1[0]['R']):,.0f} M4 {1e6 * math.exp(ex1[0]['M']):,.0f}"
  f"  short {1e6 * (math.exp(I1) - math.exp(ex1[0]['L'])):,.0f}")
P("  chain 0.25*(sum of four rates)", f"{0.25 * (1.50000 + 1.69673 + 1.81606 + 1.88843):.4f}%"
  f"  right {0.25 * (1.69673 + 1.81606 + 1.88843 + 1.93233):.4f}%")
OUT["ex1"] = {"I": I1, "rows": ex1}

# ----------------------------------------------------------------------------------------------- Example: substitution (standardization)
P("== SUBSTITUTION", "")
P("k-mu", f"{K - mu:.6f}  z={z5:.7f}")
z_up = (0.01 - mu) / s
z_dn = (-0.01 - mu) / s
P("P(-1%<R<=1%) normal", f"z=({z_dn:.4f},{z_up:.4f}) P={norm_cdf(z_up) - norm_cdf(z_dn):.4f}"
  f"  actual {((R > -0.01 + 1e-12) & (R <= 0.01 + 1e-12)).mean():.4f}")
P("  chain 3 decimals", f"zdn {(-0.01 - 0.000871) / 0.012385:.3f} zup {(0.01 - 0.000871) / 0.012385:.3f}"
  f"  Phi(0.737)={norm_cdf(0.737):.3f} Phi(-0.878)={norm_cdf(-0.878):.3f}"
  f"  diff {norm_cdf(0.737) - norm_cdf(-0.878):.3f} (true {norm_cdf(z_up) - norm_cdf(z_dn):.3f})")

# ----------------------------------------------------------------------------------------------- Example: parts on LM2's forward curve
P("== PARTS: LM2 curve y(T)=2%-0.8%e^{-T/3}", "")


def yT(T):
    return 0.02 - 0.008 * math.exp(-T / 3)


def fwd(t):
    return 0.02 - 0.008 * math.exp(-t / 3) * (1 - t / 3)


for T in [1, 5, 10]:
    I_parts = (0.02 * T - 0.008 * 3 * (1 - math.exp(-T / 3))
               + (0.008 / 3) * (-3 * T * math.exp(-T / 3) + 9 * (1 - math.exp(-T / 3))))
    I_quad = integrate.quad(fwd, 0, T)[0]
    tint = -3 * T * math.exp(-T / 3) + 9 * (1 - math.exp(-T / 3))
    P(f"  T={T}", f"int t e^-t/3={tint:.6f} int fwd={I_parts:.7f} quad={I_quad:.7f} T*y={T * yT(T):.7f}"
      f" y={yT(T):.5%} P(T)={math.exp(-I_parts):.6f} fwd(T)={fwd(T):.5%}")

# ----------------------------------------------------------------------------------------------- continuous annuity and duration
P("== CONTINUOUS ANNUITY", "")


def ann(r, T):
    return (1 - math.exp(-r * T)) / r


def tw(r, T):
    return (1 - math.exp(-r * T) * (1 + r * T)) / r**2


r0, T0 = 0.02, 20
cf = 360_000
P("annuity factor r=2%,T=20", f"{ann(r0, T0):.6f}  PV={cf * ann(r0, T0):,.0f}  chain 360,000*16.483998="
  f"{360_000 * 16.483998:,.2f}")
P("int t e^-rt", f"{tw(r0, T0):.4f}  duration={tw(r0, T0) / ann(r0, T0):.3f}"
  f"  formula 1/r-T/(e^rT-1)={1 / r0 - T0 / (math.exp(r0 * T0) - 1):.3f}")
h = 1 / 12
k_ = np.arange(1, 241)
end = 30_000 * np.exp(-r0 * k_ * h).sum()
beg = 30_000 * np.exp(-r0 * (k_ - 1) * h).sum()
mid = 30_000 * np.exp(-r0 * (k_ - 0.5) * h).sum()
cont = cf * ann(r0, T0)
P("monthly in arrears (right)", f"{end:,.0f}  diff vs cont {end - cont:+,.0f} ({(end - cont) / cont:+.3%})")
P("monthly in advance (left)", f"{beg:,.0f}  diff {beg - cont:+,.0f} ({(beg - cont) / cont:+.3%})")
P("mid-month (midpoint)", f"{mid:,.2f}  continuous {cont:,.2f}  gap NT${cont - mid:.2f}")
P("continuous", f"{cont:,.0f}")
P("lead terms", f"r dt/2={r0 * h / 2:.4%}  (r dt)^2/24={(r0 * h) ** 2 / 24:.2e}")
P("perpetuity c/r", f"{cf / r0:,.0f}  share of 20y={ann(r0, T0) * r0:.1%}")
P("perpetuity duration 1/r at 2.5%", f"{1 / 0.025:.0f}")

# ----------------------------------------------------------------------------------------------- Pareto moments (illustrative alpha = 3) and data check
P("== PARETO alpha=3", "")
al = 3.0
P("E[X], E[X^2], Var", f"{al / (al - 1):.4f}, {al / (al - 2):.4f}, {al / (al - 2) - (al / (al - 1)) ** 2:.4f}")
for b in [10, 100, 1000]:
    P(f"  truncated b={b}", f"int x^3 f = {3 * math.log(b):.3f}   int x^4 f = {3 * (b - 1):.0f}")
for u in [0.03, 0.04, 0.05]:
    sel = R[R <= -u + 1e-12]
    zu = (-u - mu) / s
    P(f"  kappa=-{u:.0%}", f"days={len(sel)} data mean={sel.mean():.3%}  Pareto(3) {-1.5 * u:.2%}"
      f"  normal {mu - s * norm_pdf(zu) / norm_cdf(zu):.3%}")

# kurtosis instability
P("== KURTOSIS", "")


def exk(X):
    return ((X - X.mean()) ** 4).mean() / X.std() ** 4 - 3


P("full", f"{exk(R):.2f}")
for excl in (["2025-04-07"], ["2025-04-07", "2024-08-05"], ["2025-04-07", "2024-08-05", "2026-07-31", "2025-04-10"]):
    X = df.filter(~pl.col("date").is_in(excl))["R_0050"].to_numpy()
    P(f"  without {len(excl)} day(s)", f"{exk(X):.2f}")
for y in (2017, 2018, 2019, 2020, 2024, 2025):
    msk = np.array([d[:4] <= str(y) for d in dates])
    P(f"  through {y}", f"n={msk.sum()} exkurt={exk(R[msk]):.2f}")
before = np.array([d < "2025-04-07" for d in dates])
P("  through 2025-04-03 / 04-07", f"{exk(R[before]):.2f} / {exk(R[np.array([d <= '2025-04-07' for d in dates])]):.2f}")
dev4 = (R - mu) ** 4
srt = np.sort(dev4)[::-1]
P("  share of sum (R-mu)^4 top1/top5/top10", f"{srt[0] / dev4.sum():.1%} / {srt[:5].sum() / dev4.sum():.1%}"
  f" / {srt[:10].sum() / dev4.sum():.1%}")
P("  share of sum (R-mu)^2 top10", f"{np.sort((R - mu) ** 2)[::-1][:10].sum() / ((R - mu) ** 2).sum():.1%}")

# ----------------------------------------------------------------------------------------------- conditional tail mean
P("== CONDITIONAL MEAN beyond -5%", "")
lam = norm_pdf(z5) / p5
P("phi/Phi", f"{lam:.4f}  normal E[R|R<=-5%]={mu - s * lam:.3%}  data={R[days5].mean():.3%}"
  f"  chain 0.0871-1.2385*4.328={0.0871 - 1.2385 * 4.328:.4f}%")
P("  approx lam ~ omega + 1/omega", f"{aa + 1 / aa:.4f}")

# ----------------------------------------------------------------------------------------------- lognormal mean
P("== LOGNORMAL", "")
rlog = np.log1p(R)
m_d, s_d = rlog.mean(), rlog.std()
A1 = 243.1                                     # the printed A: the text annualizes with 243.1, not n/years
M_, V_ = m_d * A1, s_d**2 * A1
P("daily log mean, sd", f"{m_d:.6%}  {s_d:.4%}")
P("annual mu_X, sigma_X, var (A=243.1)", f"{M_:.5f} = {M_:.4%}  {math.sqrt(V_):.4%}  {V_:.7f}  var/2 {V_ / 2:.7f}"
  f"  (unrounded A: {m_d * A:.5f}, {s_d**2 * A:.6f})")
P("E[G] = exp(mu_X+var/2)", f"{math.exp(M_ + V_ / 2):.4f}  ({math.exp(M_ + V_ / 2) - 1:.2%})"
  f"  chain exp(0.19308+0.018632)={math.exp(0.19308 + 0.018632):.6f}")
P("median exp(mu_X)", f"{math.exp(M_):.4f}  ({math.exp(M_) - 1:.2%})  CAGR check {(np.prod(1 + R)) ** (1 / years) - 1:.4%}"
  f"  chain exp(0.19308)={math.exp(0.19308):.4f}")
P("mean - median (pp)", f"{(math.exp(M_ + V_ / 2) - math.exp(M_)) * 100:.2f}")
P("P(G<1) = Phi(-mu_X/sig)", f"{norm_cdf(-M_ / math.sqrt(V_)):.2%}   z={-M_ / math.sqrt(V_):.3f}")
EG = integrate.quad(lambda x: np.exp(x - 0.5 * (x - M_) ** 2 / V_) / math.sqrt(2 * math.pi * V_), -np.inf, np.inf)[0]
P("quad check E[G]", f"{EG:.6f}")
OUT.update(lognormal={"mu_X": M_, "var_X": V_})

# ----------------------------------------------------------------------------------------------- numerical integration of the tail
P("== NUMERICAL: int_{-12}^{z} phi", "")
LO = -12.0
exact = p5 - norm_cdf(LO)
P("truncation Phi(-12)", f"{norm_cdf(LO):.2e}  bound phi(12)/12={norm_pdf(12) / 12:.2e}")


def trap(f, a_, b_, nn):
    x = np.linspace(a_, b_, nn + 1)
    y_ = f(x)
    hh = (b_ - a_) / nn
    return hh * (y_.sum() - 0.5 * (y_[0] + y_[-1]))


def simp(f, a_, b_, nn):
    x = np.linspace(a_, b_, nn + 1)
    y_ = f(x)
    hh = (b_ - a_) / nn
    return hh / 3 * (y_[0] + y_[-1] + 4 * y_[1:-1:2].sum() + 2 * y_[2:-1:2].sum())


def midp(f, a_, b_, nn):
    hh = (b_ - a_) / nn
    x = a_ + hh * (np.arange(nn) + 0.5)
    return hh * f(x).sum()


def f_(x):
    return np.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


rows: list[dict[str, float]] = []
prevT = prevS = None
for nn in [8, 16, 32, 64, 128, 256, 512, 1024]:
    T_, S_, Mid_ = trap(f_, LO, z5, nn), simp(f_, LO, z5, nn), midp(f_, LO, z5, nn)
    eT, eS = T_ - exact, S_ - exact
    rows.append({"n": nn, "h": (z5 - LO) / nn, "T": T_, "S": S_, "eT": eT, "eS": eS, "eM": Mid_ - exact})
    rT = "" if prevT is None else f"{prevT / eT:.2f}"
    rS = "" if prevS is None else f"{prevS / eS:.2f}"
    P(f"  N={nn:5d}", f"dx={(z5 - LO) / nn:.4f} T={T_:.6e} eT={eT:+.3e} ratioT={rT}  "
      f"S={S_:.6e} eS={eS:+.3e} ratioS={rS}  eM={Mid_ - exact:+.3e}")
    prevT, prevS = eT, eS
OUT["numint"] = {"exact": exact, "rows": rows}
P("exact (target)", f"{exact:.10e}  at printed z -4.1074386: {norm_cdf(-4.1074386) - norm_cdf(LO):.6e}")
for rw in rows:
    if rw["n"] in (16, 64, 256):
        P(f"  rel N={rw['n']:.0f}", f"T {rw['eT'] / exact:+.2e}  S {rw['eS'] / exact:+.2e}")
P("Richardson check N=64", f"(4T64-T32)/3={(4 * rows[3]['T'] - rows[2]['T']) / 3:.10e}  S64={rows[3]['S']:.10e}")
qv, qe = integrate.quad(norm_pdf, -np.inf, z5)
P("quad(-inf,z)", f"{qv:.10e}  est.err {qe:.1e}  scipy norm.cdf {stats.norm.cdf(z5):.10e}")
for hh in [2.0, 1.5, 1.0, 0.5]:
    kk = np.arange(-int(40 / hh), int(40 / hh) + 1)
    val = hh * np.exp(-0.5 * (kk * hh) ** 2).sum()
    P(f"  whole-line trapezoid dx={hh}", f"{val:.12f}  err={val - math.sqrt(2 * math.pi):+.2e}")
P("sqrt(2 pi)", f"{math.sqrt(2 * math.pi):.12f}")


def fp(x):
    return -x * norm_pdf(x)


r256 = rows[5]
d1 = fp(z5) - fp(LO)
P("(5.13) predicted N=256", f"T-exact={r256['h'] ** 2 / 12 * d1:.3e} (obs {r256['eT']:.3e})"
  f"  M-exact={-r256['h'] ** 2 / 24 * d1:.3e} (obs {r256['eM']:.3e})  f'(b)-f'(a)={d1:.4e}")
P("  chain dx=7.8925614/256, -z phi(z)", f"z+12={z5 + 12:.7f} dx={7.8925614 / 256:.5f}  -z*phi(z)={-z5 * norm_pdf(z5):.4e}"
  f"  0.03083^2/12*3.5561e-4={0.03083**2 / 12 * 3.5561e-4:.3e}")
P("  phi'(-12) = 12 phi(12)", f"{fp(LO):.2e}")

# ----------------------------------------------------------------------------------------------- knowledge checks
P("== KCs", "")
P("KC duration of the rent stream", f"{tw(r0, T0) / ann(r0, T0):.3f}  20/(e^0.4-1)={20 / (math.exp(0.4) - 1):.3f}")
P("KC sigma+10% expected days", f"{n * p10:.2f}  chain 2902*9.422e-5={2902 * 9.422e-5:.4f}"
  f"  shortfall {9 / (n * p10):.0f}  gain {p10 / p5:.1f}")
P("KC Simpson panels 3.2e-6/256", f"{3.2e-6 / 256:.2e}  n=32*125^0.25={32 * 125**0.25:.1f}")
w5 = (0.05 - mu) / s
P("KC upper tail P(R>+5%)", f"z={w5:.4f} P={norm_cdf(-w5):.3e} expected={n * norm_cdf(-w5):.3f}"
  f"  chain z=(0.05-0.000871)/0.012385={(0.05 - 0.000871) / 0.012385:.4f} Phi(-3.9668)={sig(norm_cdf(-3.9668), 3)}"
  f" 2902*3.64e-5={2902 * 3.64e-5:.3f}")

# ----------------------------------------------------------------------------------------------- practice problems
P("== PROBLEMS", "")
P("PP1 annuity 10y 3%", f"cont={ann(0.03, 10):.4f}  annual discrete={(1 - 1.03**-10) / 0.03:.4f}"
  f"  annual cont-disc={sum(math.exp(-0.03 * k) for k in range(1, 11)):.4f}")
hh = 0.25
xx = np.arange(4) * hh
Lx = np.exp(xx).sum() * hh
Rx = np.exp(xx + hh).sum() * hh
Ix = math.e - 1
P("PP2 left/right e^x N=4", f"L={Lx:.6f} ({Lx - Ix:+.6f}) R={Rx:.6f} ({Rx - Ix:+.6f}) exact={Ix:.6f}"
  f"  avg(L,R)={(Lx + Rx) / 2:.6f} err {(Lx + Rx) / 2 - Ix:+.6f}"
  f"  (5.13): exact - T4 = -(dx^2/12)(e-1)={-hh**2 / 12 * (math.e - 1):.6f}"
  f" chain -0.0625/12*1.718282={-0.0625 / 12 * 1.718282:.6f}"
  f"  bound dx(e-1)={hh * (math.e - 1):.6f}")
P("PP4 int_0^1 x e^{-x^2/2}", f"{1 - math.exp(-0.5):.4f}")
P("PP5 perpetuity duration 2.5%", f"{1 / 0.025:.0f}")
al2 = 2.5
P("PP7 Pareto 2.5", f"E[X]={al2 / (al2 - 1):.4f} E[X^2]={al2 / (al2 - 2):.4f} Var={al2 / (al2 - 2) - (al2 / (al2 - 1)) ** 2:.4f}"
  f"  5-25/9={5 - 25 / 9:.4f}")
mu8, s8, k8 = 0.0005, 0.015, -0.06
z8 = (k8 - mu8) / s8
for a8 in (-z8, 4.03333):
    ph8 = norm_pdf(a8)
    P(f"PP8 at omega={a8:.7f}", f"phi={ph8:.4e} upper={ph8 / a8:.4e} lower={ph8 / a8 * (1 - 1 / a8**2):.4e}"
      f" exact={norm_cdf(-a8):.4e}  upper {ph8 / a8 / norm_cdf(-a8) - 1:+.2%}"
      f" lower {ph8 / a8 * (1 - 1 / a8**2) / norm_cdf(-a8) - 1:+.2%}")
P("PP8 chain upper/exact, lower/exact", f"{2.9023 / 2.7496 - 1:+.2%} {2.7239 / 2.7496 - 1:+.2%}")
P("PP8 per year", f"{norm_cdf(z8) * 243.1:.5f}  return period={1 / (norm_cdf(z8) * 243.1):.0f}y"
  f"  chain 243.1*2.7496e-5={243.1 * 2.7496e-5:.5f} 1/0.00668={1 / 0.00668:.0f}")
P("PP9 Phi(-4)", f"{norm_cdf(-4):.4e} two-sided {2 * norm_cdf(-4):.4e} Cantelli 1/17={1 / 17:.4f}"
  f"  return period {1 / (norm_cdf(-4) * A):.0f} years")
g10, r10, T10 = 0.03, 0.05, 30
P("PP10 growing annuity", f"PV={(1 - math.exp(-(r10 - g10) * T10)) / (r10 - g10):.4f} perp={1 / (r10 - g10):.1f}"
  f" share={1 - math.exp(-(r10 - g10) * T10):.1%}  LM6 discrete level at 2%: {1 - 1.02**-30:.1%}")


def g11(x):
    return np.exp(-0.5 * x * x)


I11 = math.sqrt(2 * math.pi) * (norm_cdf(1) - 0.5)
T2, T4, S4 = trap(g11, 0, 1, 2), trap(g11, 0, 1, 4), simp(g11, 0, 1, 4)
P("PP11 values (7dp)", " ".join(f"{g11(x):.7f}" for x in (0, 0.25, 0.5, 0.75, 1)))
P("PP11 7dp", f"T2={T2:.7f} ({T2 - I11:+.7f}) T4={T4:.7f} ({T4 - I11:+.7f}) S4={S4:.7f} ({S4 - I11:+.7f})"
  f" (4T4-T2)/3={(4 * T4 - T2) / 3:.7f} exact={I11:.7f} ratioT={(T2 - I11) / (T4 - I11):.2f}")
P("PP12", "16")
m13, s13 = 0.08, 0.20
P("PP13 lognormal", f"mean={math.exp(m13 + s13**2 / 2):.4f} median={math.exp(m13):.4f} P(G<1)={norm_cdf(-m13 / s13):.4f}")
P("PP14 E[Z|Z<=-2]", f"phi(2)={norm_pdf(2):.5f} Phi(-2)={norm_cdf(-2):.5f} cond={-norm_pdf(2) / norm_cdf(-2):.4f}"
  f"  2.5/2.3732={2.5 / 2.3732:.3f}")
P("PP15 upper tail", f"actual={up5} expected={n * norm_cdf(-(0.05 - mu) / s):.4f} ratio={up5 / (n * norm_cdf(-(0.05 - mu) / s)):.0f}")
up_mask = R >= 0.05 - 1e-12
P("PP15 dates", ", ".join(f"{d} ({x:+.2%})" for d, x in zip(np.array(dates)[up_mask], R[up_mask], strict=True)))
P("PP16", f"z9={z9:.4f} sigma9={sig9:.4%}; at -2%: {n * norm_cdf((-0.02 - mu) / sig9):.0f} vs "
  f"{(R <= -0.02 + 1e-12).sum()}; at -3%: {n * norm_cdf((-0.03 - mu) / sig9):.0f} vs {(R <= -0.03 + 1e-12).sum()}")

# ----------------------------------------------------------------------------------------------- other quoted values
P("== EXTRA", "")
P("Phi(-25) (25-sigma)", f"{norm_cdf(-25):.4e}")
P("quad rel. error vs erfc", f"{abs(qv - p5) / p5:.1e}")
recent = [r_["date"] for r_ in case_rows if r_["date"] >= "2024-04-01"]
P("-5% days since April 2024", len(recent), recent)
P("first/last of the nine", case_rows[0]["date"], case_rows[-1]["date"])
P("days -10% exactly (limit)", int((np.abs(R + 0.10) < 1e-9).sum()), " +10%:", int((np.abs(R - 0.10) < 1e-9).sum()))
P("largest drop, largest gain", f"{R.min():.3%} {R.max():.3%}")
P("share within +-1% actual", f"{((R > -0.01 + 1e-12) & (R <= 0.01 + 1e-12)).sum()} days")
P("Riemann table: L12 M12 L365 in %", f"{ex1[1]['L']:.6%} {ex1[1]['M']:.6%} {ex1[2]['L']:.6%} R12 {ex1[1]['R']:.6%}"
  f" M365 {ex1[2]['M']:.6%} R365 {ex1[2]['R']:.6%}")
P("Riemann table: L4 R4 M4 in %", f"{ex1[0]['L']:.6%} {ex1[0]['R']:.6%} {ex1[0]['M']:.6%}  exact {I1:.6%}")
P("Riemann r at quarter points", " ".join(f"{rt(q):.5%}" for q in (0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0)))
# bands lo < R <= hi, with the 1e-12 guard of the threshold counts: prices have two decimals, so returns of
# exactly -1% or +1% are ties that float division can push to either side of the edge
for lo_, hi_ in ((-0.03, -0.01), (0.01, 0.03), (-0.01, 0.01)):
    pn = norm_cdf((hi_ - mu) / s) - norm_cdf((lo_ - mu) / s)
    cnt = int(((R > lo_ + 1e-12) & (R <= hi_ + 1e-12)).sum())
    cnt_o = int(((R_only > lo_ + 1e-12) & (R_only <= hi_ + 1e-12)).sum())
    P(f"  band ({lo_:+.0%},{hi_:+.0%}]", f"normal {pn:.4f} ({n * pn:.2f} days) actual {cnt / n:.4f} ({cnt} days)"
      f"  0050-only {cnt_o} of {len(R_only)} ({cnt_o / len(R_only):.2%}), move {cnt_o - cnt:+d}")
P("  partition check", f"{int((R <= -0.03 + 1e-12).sum())} + bands + {int((R > 0.03 + 1e-12).sum())}")
P("advance vs arrears", f"{(beg - end) / end:.3%}  NT$ {beg - end:,.0f}")
r_eff = math.log1p(0.02)
P("pitfall r=ln(1.02)", f"r={r_eff:.4%} PV={cf * ann(r_eff, T0):,.0f} vs {cf * ann(0.02, T0):,.0f}"
  f" diff {cf * ann(r_eff, T0) - cf * ann(0.02, T0):,.0f}")
P("Laplace/t5 kurtosis", "Laplace 6, t5 3+6/(5-4)=9")
P("Riemann bound dt[r(1)-r(0)] (bp)", f"{0.25 * (rt(1) - rt(0)) * 1e4:.1f}")
P("pitfall 2% for 30 days", f"{0.02 * 30 / 365:.3%}")
P("KC falling rate bound 0.25 x 0.5% (bp)", f"{0.25 * 0.005 * 1e4:.1f}")
P("pitfall Phi(-0.05)", f"{norm_cdf(-0.05):.2f}")
P("PP1 option B", f"{ann(0.03, 10):.2f}")
P("PP9 option A (%)", f"{norm_cdf(-4) * 100:.4f}")
P("normal floor crossing on chart (%)", f"{(mu + s * stats.norm.ppf(1e-3 / n)) * 100:.2f}")

# ----------------------------------------------------------------------------------------------- exhibit rows (Markdown, as printed in src/lm05.md)


def sci_md(x, d=2):
    """x as $m\\times10^{e}$ with d significant digits."""
    if x == 0:
        return "0"
    e = math.floor(math.log10(abs(x)))
    m_ = round(x / 10**e, d - 1)
    if abs(m_) >= 10:
        m_ /= 10
        e += 1
    return f"${m_:.{d - 1}f}\\times10^{{{e}}}$"


def years_md(v):
    """A return period at two significant figures, as the exhibit prints it."""
    if v >= 1e5:
        return sci_md(v, 2)
    e = math.floor(math.log10(v))
    return f"{round(v, 1 - e):,.0f}"


print("== EXHIBIT ROWS")
print("-- Exhibit case")
for rw in case_rows:
    print(f"> | {rw['date']} | −{abs(rw['R']) * 100:.3f}% | −{abs(rw['z']):.3f} | {sci_md(rw['p'])} | {years_md(rw['years'])} |")
print("-- Exhibit thresholds")
for rw in thr:
    e_ = rw["exp"]
    if e_ >= 10:
        e_s = f"{e_:.1f}"
    elif e_ >= 1:
        e_s = f"{e_:.2f}"
    elif e_ >= 0.01:
        e_s = f"{e_:.3f}"
    elif e_ >= 0.001:
        e_s = f"{e_:.4f}"
    else:
        e_s = sci_md(e_)
    ratio = rw["act"] / e_
    if ratio < 10:
        r_s = f"{ratio:.2f}"
    elif ratio < 100:
        r_s = f"{ratio:.1f}"
    elif ratio < 1e4:
        r_s = f"{ratio:,.0f}"
    else:
        r_s = sci_md(ratio)
    print(f"> | −{abs(rw['k']) * 100:.0f}% | −{abs(rw['z']):.3f} | {sci_md(rw['p'], 2)} | {e_s} | {rw['act']} | {r_s} | {rw['t3']:.1f} |")
print("-- Exhibit numint")
prev = None
for rw in rows:
    rt_ = "—" if prev is None else f"{prev[0] / rw['eT']:.2f}"
    rs_ = "—" if prev is None else f"{prev[1] / rw['eS']:.2f}"
    print(f"> | {rw['n']:,} | {rw['h']:.4f} | +{sci_md(rw['eT'], 3)} | {rt_} | +{sci_md(rw['eS'], 3)} | {rs_} |")
    prev = (rw["eT"], rw["eS"])

(HERE / "processed").mkdir(exist_ok=True)
(HERE / "processed" / "lm05_numbers.json").write_text(json.dumps(OUT, indent=1, default=float), encoding="utf-8")
print("wrote data/processed/lm05_numbers.json")
