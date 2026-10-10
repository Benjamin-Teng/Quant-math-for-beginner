"""Every number quoted in LM5 (Integration), computed from first principles and from the verified 0050 series.

Run after build_series.py:   python3 data/lm05_numbers.py
Writes data/processed/lm05_numbers.json (used by lm05_charts.py) and prints one labelled line per quoted number.
"""
import json, math
from pathlib import Path

import numpy as np
import polars as pl
from scipy import integrate, special, stats

HERE = Path(__file__).resolve().parent
OUT = {}


def P(label, *vals):
    print(f"{label:<34s}", *vals)


def norm_cdf(z):
    return 0.5 * special.erfc(-z / math.sqrt(2.0))


def norm_pdf(z):
    return math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)


# ----------------------------------------------------------------------------------------------- data
df = pl.read_parquet(HERE / "processed" / "etf_daily_returns.parquet")
dates = df["date"].to_list()
R = df["R_0050"].to_numpy()
n = len(R)
mu, s = R.mean(), R.std()                      # population standard deviation (MLE), as in LM3/LM4
s1 = R.std(ddof=1)
years = (np.datetime64(dates[-1]) - np.datetime64("2014-10-31")).astype(int) / 365.25
D = n / years                                  # observations per year in this sample
P("== DATA", f"n={n} first={dates[0]} last={dates[-1]} years={years:.2f} D={D:.1f}")
P("mean R (mu_hat)", f"{mu:.6%}  ({mu*1e4:.2f} bp)")
P("s population / T-1", f"{s:.6%} / {s1:.6%}")
P("skew / excess kurtosis", f"{((R-mu)**3).mean()/s**3:.3f} / {((R-mu)**4).mean()/s**4-3:.2f}")
OUT.update(n=n, mu=mu, s=s, years=years, D=D)

# 0050-only series (all 2,906 0050 trading days) for the robustness note
m = pl.read_csv(HERE / "processed" / "raw_merged_full.csv").sort("date")
a = m.filter(pl.col("p0050").is_not_null()).select("date", "p0050", "d0050", "s0050")
a = a.with_columns(((pl.col("p0050") + pl.col("d0050")) / (pl.col("p0050").shift(1) / pl.col("s0050")) - 1).alias("R")).drop_nulls("R")
R_only = a["R"].to_numpy()

# ----------------------------------------------------------------------------------------------- case
K = -0.05
z5 = (K - mu) / s
p5 = norm_cdf(z5)
days5 = (R <= K + 1e-12)
P("== CASE", "")
P("z(-5%) pop / T-1", f"{z5:.4f} / {(K-mu)/s1:.4f}")
P("Phi(z)", f"{p5:.4e}")
P("expected days in n", f"{n*p5:.4f}")
P("expected days, T-1 sd", f"{n*norm_cdf((K-mu)/s1):.4f}")
P("return period (years)", f"{1/(p5*D):.1f}   trading days {1/p5:,.0f}")
P("actual count", int(days5.sum()), "  share", f"{days5.mean():.4%}", "  ratio", f"{days5.sum()/(n*p5):.0f}")
P("actual: one every (years)", f"{years/days5.sum():.2f}   trading days {n/days5.sum():.0f}")
case_rows = []
for d, x in zip(np.array(dates)[days5], R[days5]):
    z = (x - mu) / s
    pz = norm_cdf(z)
    case_rows.append(dict(date=d, R=float(x), z=float(z), p=float(pz), years=float(1 / (pz * D))))
    P("  day", d, f"R={x:.3%} z={z:.3f} P={pz:.2e} once in {1/(pz*D):.3g} yr")
OUT["case_rows"] = case_rows
P("mean of the nine", f"{R[days5].mean():.3%}")
# 0050-only robustness
mu_o, s_o = R_only.mean(), R_only.std()
P("0050-only n, exp, count", len(R_only), f"{len(R_only)*norm_cdf((K-mu_o)/s_o):.4f}", int((R_only <= K + 1e-12).sum()))
up5 = (R >= 0.05 - 1e-12).sum()
P("upper tail: R>=+5% actual/exp", int(up5), f"{n*norm_cdf(-(0.05-mu)/s):.4f}")

# ----------------------------------------------------------------------------------------------- thresholds table
P("== THRESHOLD TABLE (lower tail)", "")
nu = 3
sc_t = s * math.sqrt((nu - 2) / nu)
thr = []
for k in [-0.02, -0.03, -0.04, -0.05, -0.06, -0.07, -0.08, -0.09, -0.10]:
    z = (k - mu) / s
    pz = norm_cdf(z)
    act = int((R <= k + 1e-12).sum())
    act_o = int((R_only <= k + 1e-12).sum())
    pt = stats.t.cdf((k - mu) / sc_t, nu)
    thr.append(dict(k=k, z=z, p=pz, exp=n * pz, act=act, t3=n * pt))
    P(f"  k={k:+.0%}", f"z={z:.3f} p={pz:.3e} exp={n*pz:.4g} act={act} (only {act_o}) ratio={act/(n*pz):.3g} t3={n*pt:.2f}")
OUT["thr"] = thr
P("t3 scale (decimal)", f"{sc_t:.6f}")

# sigma that would make the normal model expect 9 days at -5%, and its prediction at -2%
z9 = stats.norm.ppf(9 / n)
sig9 = (K - mu) / z9
P("sigma for 9 days", f"z={z9:.3f} sigma={sig9:.3%} annualized={sig9*math.sqrt(D):.1%}")
P("  that sigma at -2%", f"{n*norm_cdf((-0.02-mu)/sig9):.0f} days (actual {(R <= -0.02 + 1e-12).sum()})")

# ----------------------------------------------------------------------------------------------- Mills ratio
P("== MILLS (a = -z)", "")
aa = -z5
ph = norm_pdf(aa)
P("phi(a)", f"{ph:.4e}   exponent a^2/2={aa*aa/2:.4f}")
P("upper phi/a", f"{ph/aa:.4e}")
P("lower phi/a(1-1/a^2)", f"{ph/aa*(1-1/aa**2):.4e}   1/a^2={1/aa**2:.4f}")
P("Gordon lower phi/(a+1/a)", f"{ph/(aa+1/aa):.4e}")
P("three-term phi/a(1-1/a^2+3/a^4)", f"{ph/aa*(1-1/aa**2+3/aa**4):.4e}")
P("exact Q(a)", f"{p5:.4e}  rel. err upper {(ph/aa-p5)/p5:+.2%} lower {(ph/aa*(1-1/aa**2)-p5)/p5:+.2%}")
OUT.update(z5=z5, p5=p5)

# ----------------------------------------------------------------------------------------------- FTC example: sensitivity to sigma
P("== FTC EXAMPLE: dP/dsigma", "")
el = -z5 * norm_pdf(z5) / p5
P("phi(z)/Phi(z)", f"{norm_pdf(z5)/p5:.4f}")
P("elasticity dlnP/dln sigma", f"{el:.2f}")
P("dP/dsigma (per 1.0 of sigma)", f"{norm_pdf(z5)*(-z5)/s:.5f}  per 0.1pp: {norm_pdf(z5)*(-z5)/s*0.001:.3e}")
s10 = 1.1 * s
z10 = (K - mu) / s10
p10 = norm_cdf(z10)
P("sigma +10%", f"sigma={s10:.4%} z={z10:.4f} P={p10:.3e} ratio={p10/p5:.2f} (+{p10/p5-1:.0%}) exp days={n*p10:.3f}")
P("linear estimate +10%", f"+{el*0.10:.0%}")
P("log-linear exp(el*ln1.1)", f"x{math.exp(el*math.log(1.1)):.2f}")
el10 = -z10 * norm_pdf(z10) / p10
P("el*ln(1.1), elasticity at new z", f"{el*math.log(1.1):.2f}  new elasticity {el10:.2f}  avg-el factor {math.exp(0.5*(el+el10)*math.log(1.1)):.2f}")

# ----------------------------------------------------------------------------------------------- Example 1: Riemann sums
P("== EX1 RIEMANN: r(t)=2%-0.5%e^{-2t}", "")
rt = lambda t: 0.02 - 0.005 * np.exp(-2 * t)
I1 = 0.02 - 0.0025 * (1 - math.exp(-2))
P("exact integral", f"{I1:.8f}  factor {math.exp(I1):.6f}  r(0)={rt(0):.4%} r(1)={rt(1):.4%}")
ex1 = []
for nn in [4, 12, 365]:
    h = 1 / nn
    t = np.arange(nn) * h
    L = rt(t).sum() * h
    Rr = rt(t + h).sum() * h
    M = rt(t + h / 2).sum() * h
    ex1.append(dict(n=nn, L=L, R=Rr, M=M))
    P(f"  n={nn}", f"L={L:.8f} ({(L-I1)*1e4:+.4f} bp)  R={Rr:.8f} ({(Rr-I1)*1e4:+.4f} bp)  M={M:.8f} ({(M-I1)*1e4:+.6f} bp)")
P("  lead terms n=4", f"(h/2)(f(b)-f(a))={0.125*(rt(1)-rt(0))*1e4:.4f} bp  (h^2/24)(f'(b)-f'(a))={(0.25**2/24)*(0.01*math.exp(-2)-0.01)*1e4:.5f} bp")
P("  factor L4 / exact", f"{math.exp(ex1[0]['L']):.6f} / {math.exp(I1):.6f}")
P("  NT$ on 1,000,000", f"exact {1e6*math.exp(I1):,.0f}  L4 {1e6*math.exp(ex1[0]['L']):,.0f}  R4 {1e6*math.exp(ex1[0]['R']):,.0f} M4 {1e6*math.exp(ex1[0]['M']):,.0f}")
OUT["ex1"] = dict(I=I1, rows=ex1)

# ----------------------------------------------------------------------------------------------- Example: substitution (standardization)
P("== SUBSTITUTION", "")
P("k-mu", f"{K-mu:.6f}  z={z5:.4f}")
z_up = (0.01 - mu) / s; z_dn = (-0.01 - mu) / s
P("P(-1%<R<=1%) normal", f"z=({z_dn:.4f},{z_up:.4f}) P={norm_cdf(z_up)-norm_cdf(z_dn):.4f}  actual {((R>-0.01)&(R<=0.01)).mean():.4f}")

# ----------------------------------------------------------------------------------------------- Example: parts on LM2's forward curve
P("== PARTS: LM2 curve y(T)=2%-0.8%e^{-T/3}", "")
yT = lambda T: 0.02 - 0.008 * math.exp(-T / 3)
fwd = lambda t: 0.02 - 0.008 * math.exp(-t / 3) * (1 - t / 3)
for T in [1, 5, 10]:
    I_parts = 0.02 * T - 0.008 * 3 * (1 - math.exp(-T / 3)) + (0.008 / 3) * (-3 * T * math.exp(-T / 3) + 9 * (1 - math.exp(-T / 3)))
    I_quad = integrate.quad(fwd, 0, T)[0]
    tint = -3 * T * math.exp(-T / 3) + 9 * (1 - math.exp(-T / 3))
    P(f"  T={T}", f"int t e^-t/3={tint:.6f} int fwd={I_parts:.7f} quad={I_quad:.7f} T*y={T*yT(T):.7f} y={yT(T):.5%} P(T)={math.exp(-I_parts):.6f} fwd(T)={fwd(T):.5%}")

# ----------------------------------------------------------------------------------------------- Example: t e^{-rt} (time-weighted discounting) and continuous annuity
P("== CONTINUOUS ANNUITY", "")
def ann(r, T):
    return (1 - math.exp(-r * T)) / r
def tw(r, T):
    return (1 - math.exp(-r * T) * (1 + r * T)) / r**2
r0, T0 = 0.02, 20
c = 360_000
P("annuity factor r=2%,T=20", f"{ann(r0,T0):.4f}  PV={c*ann(r0,T0):,.0f}")
P("int t e^-rt", f"{tw(r0,T0):.4f}  duration={tw(r0,T0)/ann(r0,T0):.3f}  formula 1/r-T/(e^rT-1)={1/r0-T0/(math.exp(r0*T0)-1):.3f}")
h = 1 / 12
k_ = np.arange(1, 241)
end = 30_000 * np.exp(-r0 * k_ * h).sum()
beg = 30_000 * np.exp(-r0 * (k_ - 1) * h).sum()
mid = 30_000 * np.exp(-r0 * (k_ - 0.5) * h).sum()
cont = c * ann(r0, T0)
P("monthly in arrears (right)", f"{end:,.0f}  diff vs cont {end-cont:+,.0f} ({(end-cont)/cont:+.3%})")
P("monthly in advance (left)", f"{beg:,.0f}  diff {beg-cont:+,.0f} ({(beg-cont)/cont:+.3%})")
P("mid-month (midpoint)", f"{mid:,.0f}  diff {mid-cont:+,.0f} ({(mid-cont)/cont:+.5%})")
P("continuous", f"{cont:,.0f}")
P("lead terms", f"rh/2={r0*h/2:.4%}  (rh)^2/24={(r0*h)**2/24:.2e}")
P("perpetuity c/r", f"{c/r0:,.0f}  share of 20y={ann(r0,T0)*r0:.1%}")
P("undiscounted 20y", f"{c*20:,.0f}")
# duration of perpetuity
P("perpetuity duration 1/r at 2.5%", f"{1/0.025:.0f}")

# ----------------------------------------------------------------------------------------------- Example: Pareto moments (illustrative alpha = 3) and data check
P("== PARETO alpha=3", "")
al = 3.0
P("E[X], E[X^2], Var", f"{al/(al-1):.4f}, {al/(al-2):.4f}, {al/(al-2)-(al/(al-1))**2:.4f}")
for b in [10, 100, 1000]:
    P(f"  truncated b={b}", f"int x^3 f = {3*math.log(b):.3f}   int x^4 f = {3*(b-1):.0f}")
for u in [0.03, 0.04, 0.05]:
    sel = R[R <= -u + 1e-12]
    zu = (-u - mu) / s
    P(f"  u={u:.0%}", f"days={len(sel)} data mean={sel.mean():.3%}  Pareto(3) {-1.5*u:.2%}  normal {mu - s*norm_pdf(zu)/norm_cdf(zu):.3%}")

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
# share of the fourth-moment sum from the largest days
dev4 = (R - mu) ** 4
srt = np.sort(dev4)[::-1]
P("  share of sum (R-mu)^4 top1/top5/top10", f"{srt[0]/dev4.sum():.1%} / {srt[:5].sum()/dev4.sum():.1%} / {srt[:10].sum()/dev4.sum():.1%}")
P("  share of sum (R-mu)^2 top10", f"{np.sort((R-mu)**2)[::-1][:10].sum()/((R-mu)**2).sum():.1%}")

# ----------------------------------------------------------------------------------------------- conditional tail mean
P("== CONDITIONAL MEAN beyond -5%", "")
lam = norm_pdf(z5) / p5
P("phi/Phi", f"{lam:.4f}  normal E[R|R<=-5%]={mu - s*lam:.3%}  data={R[days5].mean():.3%}")
P("  approx lam ~ a + 1/a", f"{aa + 1/aa:.4f}")

# ----------------------------------------------------------------------------------------------- lognormal mean
P("== LOGNORMAL", "")
rlog = np.log1p(R)
m_d, s_d = rlog.mean(), rlog.std()
M_, V_ = m_d * D, s_d**2 * D
P("daily log mean, sd", f"{m_d:.6%}  {s_d:.4%}")
P("annual m, sigma, var", f"{M_:.4%}  {math.sqrt(V_):.4%}  {V_:.5f}")
P("E[G] = exp(m+v/2)", f"{math.exp(M_+V_/2):.4f}  ({math.exp(M_+V_/2)-1:.2%})")
P("median exp(m)", f"{math.exp(M_):.4f}  ({math.exp(M_)-1:.2%})  CAGR check {(np.prod(1+R))**(1/years)-1:.2%}")
P("mean - median (pp)", f"{(math.exp(M_+V_/2)-math.exp(M_))*100:.2f}")
P("P(G<1) = Phi(-m/sig)", f"{norm_cdf(-M_/math.sqrt(V_)):.2%}   z={-M_/math.sqrt(V_):.3f}")
# check by quadrature
EG = integrate.quad(lambda x: np.exp(x - 0.5 * (x - M_) ** 2 / V_) / math.sqrt(2 * math.pi * V_), -np.inf, np.inf)[0]
P("quad check E[G]", f"{EG:.6f}")
OUT.update(lognormal=dict(m=M_, v=V_))

# ----------------------------------------------------------------------------------------------- numerical integration of the tail
P("== NUMERICAL: int_{-12}^{z} phi", "")
LO = -12.0
exact = p5 - norm_cdf(LO)
P("truncation Phi(-12)", f"{norm_cdf(LO):.2e}  bound phi(12)/12={norm_pdf(12)/12:.2e}")
phi_v = np.vectorize(norm_pdf)
def trap(f, a, b, nn):
    x = np.linspace(a, b, nn + 1); y = f(x); hh = (b - a) / nn
    return hh * (y.sum() - 0.5 * (y[0] + y[-1]))
def simp(f, a, b, nn):
    x = np.linspace(a, b, nn + 1); y = f(x); hh = (b - a) / nn
    return hh / 3 * (y[0] + y[-1] + 4 * y[1:-1:2].sum() + 2 * y[2:-1:2].sum())
def midp(f, a, b, nn):
    hh = (b - a) / nn; x = a + hh * (np.arange(nn) + 0.5)
    return hh * f(x).sum()
f_ = lambda x: np.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)
rows = []
prevT = prevS = None
for nn in [8, 16, 32, 64, 128, 256, 512, 1024]:
    T_ = trap(f_, LO, z5, nn); S_ = simp(f_, LO, z5, nn); Mid_ = midp(f_, LO, z5, nn)
    eT, eS = T_ - exact, S_ - exact
    rows.append(dict(n=nn, h=(z5 - LO) / nn, T=T_, S=S_, eT=eT, eS=eS, eM=Mid_ - exact))
    P(f"  n={nn:5d}", f"h={(z5-LO)/nn:.4f} T={T_:.6e} eT={eT:+.3e} ratioT={'' if prevT is None else f'{prevT/eT:.2f}'}  "
                     f"S={S_:.6e} eS={eS:+.3e} ratioS={'' if prevS is None else f'{prevS/eS:.2f}'}  eM={Mid_-exact:+.3e}")
    prevT, prevS = eT, eS
OUT["numint"] = dict(exact=exact, rows=rows)
P("exact (target)", f"{exact:.10e}")
# relative errors
for rw in rows:
    if rw["n"] in (16, 64, 256):
        P(f"  rel n={rw['n']}", f"T {rw['eT']/exact:+.2e}  S {rw['eS']/exact:+.2e}")
# Richardson: S_2n = (4 T_2n - T_n)/3
P("Richardson check n=64", f"(4T64-T32)/3={(4*rows[3]['T']-rows[2]['T'])/3:.10e}  S64={rows[3]['S']:.10e}")
# quad
qv, qe = integrate.quad(norm_pdf, -np.inf, z5)
P("quad(-inf,z)", f"{qv:.10e}  est.err {qe:.1e}  scipy norm.cdf {stats.norm.cdf(z5):.10e}")
# trapezoid on the whole line for sqrt(2 pi) (spectral accuracy)
for hh in [2.0, 1.5, 1.0, 0.5]:
    k = np.arange(-int(40 / hh), int(40 / hh) + 1)
    val = hh * np.exp(-0.5 * (k * hh) ** 2).sum()
    P(f"  whole-line trapezoid h={hh}", f"{val:.12f}  err={val-math.sqrt(2*math.pi):+.2e}")
P("sqrt(2 pi)", f"{math.sqrt(2*math.pi):.12f}")

# ----------------------------------------------------------------------------------------------- knowledge checks
P("== KCs", "")
P("KC6 duration 20y annuity", f"{tw(r0,T0)/ann(r0,T0):.3f}")
P("KC7 sigma+10% expected days", f"{n*p10:.2f}")
P("KC8 3.2e-6/256", f"{3.2e-6/256:.2e}")

# ----------------------------------------------------------------------------------------------- practice problems
P("== PROBLEMS", "")
P("PP1 annuity 10y 3%", f"cont={ann(0.03,10):.4f}  annual discrete={(1-1.03**-10)/0.03:.4f}  annual cont-disc={sum(math.exp(-0.03*k) for k in range(1,11)):.4f}")
# PP2 Riemann e^x on [0,1] n=4
hh = 0.25; xx = np.arange(4) * hh
Lx = np.exp(xx).sum() * hh; Rx = np.exp(xx + hh).sum() * hh; Ix = math.e - 1
P("PP2 left/right e^x n=4", f"L={Lx:.6f} ({Lx-Ix:+.6f}) R={Rx:.6f} ({Rx-Ix:+.6f}) exact={Ix:.6f}  lead (h/2)(e-1)={hh/2*(math.e-1):.6f} avg(L,R)={(Lx+Rx)/2:.6f}")
P("PP4 int_0^1 x e^{-x^2/2}", f"{1-math.exp(-0.5):.4f}")
P("PP5 perpetuity duration 2.5%", f"{1/0.025:.0f}")
al2 = 2.5
P("PP7 Pareto 2.5", f"E[X]={al2/(al2-1):.4f} E[X^2]={al2/(al2-2):.4f} Var={al2/(al2-2)-(al2/(al2-1))**2:.4f}")
mu8, s8, k8 = 0.0005, 0.015, -0.06
z8 = (k8 - mu8) / s8; a8 = -z8; ph8 = norm_pdf(a8)
P("PP8", f"z={z8:.4f} phi(a)={ph8:.4e} upper={ph8/a8:.4e} lower={ph8/a8*(1-1/a8**2):.4e} exact={norm_cdf(z8):.4e} per year={norm_cdf(z8)*243.1:.4f} return period={1/(norm_cdf(z8)*243.1):.0f}y")
P("PP9 Phi(-4)", f"{norm_cdf(-4):.4e} two-sided {2*norm_cdf(-4):.4e} Cantelli 1/17={1/17:.4f}")
g10, r10, T10 = 0.03, 0.05, 30
P("PP10 growing annuity", f"PV={(1-math.exp(-(r10-g10)*T10))/(r10-g10):.4f} perp={1/(r10-g10):.1f} share={1-math.exp(-(r10-g10)*T10):.1%}")
# PP11 trapezoid/simpson on int_0^1 e^{-x^2/2}
g11 = lambda x: np.exp(-0.5 * x * x)
I11 = math.sqrt(2 * math.pi) * (norm_cdf(1) - 0.5)
T2, T4, S4 = trap(g11, 0, 1, 2), trap(g11, 0, 1, 4), simp(g11, 0, 1, 4)
P("PP11", f"T2={T2:.6f} ({T2-I11:+.6f}) T4={T4:.6f} ({T4-I11:+.6f}) S4={S4:.6f} ({S4-I11:+.2e}) (4T4-T2)/3={(4*T4-T2)/3:.6f} exact={I11:.6f} ratioT={(T2-I11)/(T4-I11):.2f}")
P("PP11 values", f"g(0)=1 g(.25)={g11(0.25):.6f} g(.5)={g11(0.5):.6f} g(.75)={g11(0.75):.6f} g(1)={g11(1):.6f}")
P("PP12", "16")
m13, s13 = 0.08, 0.20
P("PP13 lognormal", f"mean={math.exp(m13+s13**2/2):.4f} median={math.exp(m13):.4f} P(G<1)={norm_cdf(-m13/s13):.4f}")
P("PP14 E[Z|Z<=-2]", f"phi(2)={norm_pdf(2):.5f} Phi(-2)={norm_cdf(-2):.5f} cond={-norm_pdf(2)/norm_cdf(-2):.4f}")
P("PP15 upper tail", f"actual={int(up5)} expected={n*norm_cdf(-(0.05-mu)/s):.4f} ratio={up5/(n*norm_cdf(-(0.05-mu)/s)):.0f}")
up_days = np.array(dates)[R >= 0.05 - 1e-12]
P("PP15 dates", ", ".join(f"{d} ({x:+.2%})" for d, x in zip(up_days, R[R >= 0.05 - 1e-12])))
P("PP16", f"sigma9={sig9:.4%} at -2%: {n*norm_cdf((-0.02-mu)/sig9):.0f} vs {(R <= -0.02 + 1e-12).sum()}; at -3%: {n*norm_cdf((-0.03-mu)/sig9):.0f} vs {(R <= -0.03 + 1e-12).sum()}")

# ----------------------------------------------------------------------------------------------- extra quoted values
P("== EXTRA", "")
P("Phi(z_up), Phi(z_dn)", f"{norm_cdf(z_up):.4f}  {norm_cdf(z_dn):.4f}")
P("Phi(-25) (25-sigma)", f"{norm_cdf(-25):.4e}")
P("quad rel. error vs erfc", f"{abs(qv - p5)/p5:.1e}")
recent = [r_["date"] for r_ in case_rows if r_["date"] >= "2024-04-01"]
P("-5% days since April 2024", len(recent), recent)
P("first/last of the nine", case_rows[0]["date"], case_rows[-1]["date"])
P("days -10% exactly (limit)", int((np.abs(R + 0.10) < 1e-9).sum()), " +10%:", int((np.abs(R - 0.10) < 1e-9).sum()))
P("largest drop, largest gain", f"{R.min():.3%} {R.max():.3%}")
P("share within +-1% actual", f"{((R > -0.01) & (R <= 0.01)).sum()} days")
P("Phi(-1) (losing year)", f"{norm_cdf(-1):.4f}")
P("ex1 table: L12 M12 L365 in %", f"{ex1[1]['L']:.6%} {ex1[1]['M']:.6%} {ex1[2]['L']:.6%} R12 {ex1[1]['R']:.6%} M365 {ex1[2]['M']:.6%} R365 {ex1[2]['R']:.6%}")
P("ex1 table: L4 R4 M4 in %", f"{ex1[0]['L']:.6%} {ex1[0]['R']:.6%} {ex1[0]['M']:.6%}  exact {I1:.6%}")
P("ex1 r at quarter points", " ".join(f"{rt(q):.5%}" for q in (0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0)))

# ----------------------------------------------------------------------------------------------- more checks quoted in the text
P("== MORE", "")
for lo_, hi_ in ((-0.03, -0.01), (0.01, 0.03), (-0.01, 0.01)):
    pn = norm_cdf((hi_ - mu) / s) - norm_cdf((lo_ - mu) / s)
    pa = ((R > lo_) & (R <= hi_)).mean()
    P(f"  band ({lo_:+.0%},{hi_:+.0%}]", f"normal {pn:.4f} ({n*pn:.0f} days) actual {pa:.4f} ({int(round(pa*n))} days)")
P("centre band 5 decimals", f"Phi(up)={norm_cdf(z_up):.5f} Phi(dn)={norm_cdf(z_dn):.5f} diff={norm_cdf(z_up)-norm_cdf(z_dn):.5f}")
w5 = (0.05 - mu) / s
P("KC4 P(R>+5%)", f"w={w5:.4f} P={norm_cdf(-w5):.3e} expected={n*norm_cdf(-w5):.3f}")
P("KC7 shortfall factor", f"{9/(n*p10):.0f}")
P("Phi(-4) return period", f"{1/(norm_cdf(-4)*D):.0f} years")
P("advance vs arrears", f"{(beg-end)/end:.3%}")
i_eff = 0.02; r_eff = math.log1p(i_eff)
P("pitfall r=ln(1.02)", f"r={r_eff:.4%} PV={c*ann(r_eff,T0):,.0f} vs {c*ann(0.02,T0):,.0f} diff {c*ann(r_eff,T0)-c*ann(0.02,T0):,.0f}")
fp = lambda x: -x * norm_pdf(x)
for rw in OUT["numint"]["rows"]:
    if rw["n"] == 256:
        hh = rw["h"]; d1 = fp(z5) - fp(LO)
        P("(5.13) predicted n=256", f"T-exact={hh**2/12*d1:.3e} (obs {rw['eT']:.3e})  M-exact={-hh**2/24*d1:.3e} (obs {rw['eM']:.3e})  f'(b)-f'(a)={d1:.4e}")
P("KC8 n for 1e-10", f"n=32*125^0.25={32*125**0.25:.1f}")
Tx = (Lx + Rx) / 2
P("PP2 trapezoid check", f"T4={Tx:.6f} err={Tx-Ix:+.6f} predicted (h^2/12)(e-1)={hh*0 + 0.25**2/12*(math.e-1):.6f} bound h(e-1)={0.25*(math.e-1):.6f}")
P("PP11 7dp", f"T2={T2:.7f} T4={T4:.7f} S4={S4:.7f} (4T4-T2)/3={(4*T4-T2)/3:.7f} exact={I11:.7f}")
P("PP11 errors", f"T2 {T2-I11:+.6f} T4 {T4-I11:+.6f} S4 {S4-I11:+.7f}")
P("Laplace/t5 kurtosis", "Laplace 6, t5 3+6/(5-4)=9")

# ----------------------------------------------------------------------------------------------- small arithmetic quoted in the text
P("== ARITHMETIC", "")
P("Ex1 bound h[r(1)-r(0)] (bp)", f"{0.25*(rt(1)-rt(0))*1e4:.1f}")
P("pitfall 2% for 30 days", f"{0.02*30/365:.3%}")
P("KC1 bound 0.25 x 0.5% (bp)", f"{0.25*0.005*1e4:.1f}")
P("pitfall Phi(-0.05)", f"{norm_cdf(-0.05):.2f}")
P("advance - arrears (NT$)", f"{beg-end:,.0f}")
P("20/(e^0.4-1)", f"{20/(math.exp(0.4)-1):.3f}")
P("PP1 option B", f"{ann(0.03,10):.2f}")
P("PP9 option A (%)", f"{norm_cdf(-4)*100:.4f}")
P("normal floor crossing on chart (%)", f"{(mu + s*stats.norm.ppf(1e-3/n))*100:.2f}")
P("lognormal v/2", f"{V_/2:.5f}")

# ----------------------------------------------------------------------------------------------- exhibit rows (Markdown, as printed in src/lm05.md)
def sci_md(x, d=2):
    """x as $m\times10^{e}$ with d significant digits."""
    if x == 0:
        return "0"
    e = int(math.floor(math.log10(abs(x))))
    m_ = round(x / 10**e, d - 1)
    if abs(m_) >= 10:
        m_ /= 10; e += 1
    return f"${m_:.{d-1}f}\\times10^{{{e}}}$"

def years_md(v):
    return f"{v:,.0f}" if v < 1e5 else sci_md(v, 2)

print("== EXHIBIT ROWS")
print("-- Exhibit case")
for rw in case_rows:
    print(f"> | {rw['date']} | −{abs(rw['R'])*100:.3f}% | −{abs(rw['z']):.3f} | {sci_md(rw['p'])} | {years_md(rw['years'])} |")
print("-- Exhibit thresholds")
for rw in thr:
    e_ = rw["exp"]
    e_s = f"{e_:.1f}" if e_ >= 10 else f"{e_:.2f}" if e_ >= 1 else f"{e_:.3f}" if e_ >= 0.01 else f"{e_:.4f}" if e_ >= 0.001 else sci_md(e_)
    ratio = rw["act"] / e_
    r_s = f"{ratio:.2f}" if ratio < 10 else f"{ratio:.1f}" if ratio < 100 else f"{ratio:,.0f}" if ratio < 1e4 else sci_md(ratio)
    print(f"> | −{abs(rw['k'])*100:.0f}% | −{abs(rw['z']):.3f} | {sci_md(rw['p'], 3)} | {e_s} | {rw['act']} | {r_s} | {rw['t3']:.1f} |")
print("-- Exhibit numint")
prev = None
for rw in OUT["numint"]["rows"]:
    rt_ = "—" if prev is None else f"{prev[0]/rw['eT']:.2f}"
    rs_ = "—" if prev is None else f"{prev[1]/rw['eS']:.2f}"
    print(f"> | {rw['n']:,} | {rw['h']:.4f} | +{sci_md(rw['eT'], 3)} | {rt_} | +{sci_md(rw['eS'], 3)} | {rs_} |")
    prev = (rw["eT"], rw["eS"])

(HERE / "processed").mkdir(exist_ok=True)
(HERE / "processed" / "lm05_numbers.json").write_text(json.dumps(OUT, indent=1, default=float), encoding="utf-8")
print("wrote data/processed/lm05_numbers.json")
