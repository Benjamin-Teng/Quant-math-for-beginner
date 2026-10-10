"""Prints every number quoted in LM4's examples, knowledge checks, practice problems and solutions.

Data-based numbers come from processed/lm04_stats.json (run lm04_stats.py first);
the rest are computed here from the stated assumptions.
"""
import json
from math import exp, log, log1p, sqrt
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
st = json.loads((HERE / "processed" / "lm04_stats.json").read_text(encoding="utf-8"))
P = print


# ---------------------------------------------------------------- binary-bet helpers (Section 5)
def g_bin(f, p, G, L):
    return p * log1p(f * G) + (1 - p) * log1p(-f * L)


def f_bin(p, G, L):
    return p / L - (1 - p) / G


def g_star(p, G, L):
    q = 1 - p
    return p * log(p * (G + L) / L) + q * log(q * (G + L) / G)


def zero_growth(p, G, L):
    fs = f_bin(p, G, L)
    return brentq(lambda f: g_bin(f, p, G, L), fs, (1 / L) * (1 - 1e-12), xtol=1e-14)


# ---------------------------------------------------------------- Section 2
P("== Section 2")
mo = st["mom"]; A = st["A"]
P(f"Ex1 0050: mu={mo['mu']:.5%} s={mo['s']:.4%} m2={mo['m2']:.4e} f_q=mu/m2={mo['mu_over_m2']:.3f} mu/s2={mo['mu_over_s2']:.3f}"
  f" (mu/sigma)^2={mo['sr_daily']**2:.4f} quad g* per day={mo['mu']**2/(2*mo['m2']):.4%} = {st['quad']['g_ann']:.2%}/yr")
mu, m2 = 0.005, 0.5 * 0.02**2 + 0.5 * 0.01**2
P(f"Ex1 bet: mu={mu:.3%} E[R^2]={m2:.5f} sigma2={m2-mu**2:.6f} f_q={mu/m2:.2f} mu/s2={mu/(m2-mu**2):.2f} quad g*={mu**2/(2*m2):.4%}"
  f" exact f*={f_bin(0.5, 0.02, 0.01):.2f} exact g*={g_star(0.5, 0.02, 0.01):.4%}  fR at 20: +{20*0.02:.0%}/-{20*0.01:.0%}")
# Example 2: linear impact (illustrative)
alpha, c = 600.0, 10.0
xs = alpha / (2 * c)
P(f"Ex2 impact: x*={xs:.0f} lots  profit={alpha*xs - c*xs**2:,.0f}  gross={alpha*xs:,.0f}  cost={c*xs**2:,.0f}  SOC={-2*c:.0f}  premium/share at x*={0.01*xs:.2f}")
k = st["kelly"]
P(f"  Kelly analogue on 0050: arithmetic return at f*={k['arith_ann']:.2%}/yr  growth={k['g_ann']:.2%}/yr  share kept={k['drag_share']:.3f}")
# KC 2: x^3 - 6x^2 + 9x + 1
f = lambda x: x**3 - 6 * x**2 + 9 * x + 1
P(f"KC2 crit x=1: f={f(1):.0f} f''={6*1-12}; x=3: f={f(3):.0f} f''={6*3-12}")

# ---------------------------------------------------------------- Section 3
P("== Section 3")
z = st["zero_growth"]
P(f"Ex3 zero growth: exact f0={z['f']:.2f} = {z['ratio']:.2f} f*  quad zero 2mu/m2={z['quad_zero']:.2f}  worst-day log at f0={z['worst_day_log']:.2f}"
  f"  at f*: {st['worst_day_at_fstar_log']:.2f} of total {st['total_log_at_fstar']:.2f}")
P(f"  g''(f*)={k['g2_day']:.4e} per day  domain=({st['domain']['lo']:.4f},{st['domain']['hi']:.4f})")

# ---------------------------------------------------------------- Section 4
P("== Section 4")
c2 = st["cap2"]
P(f"Ex4a cap 2: g(2)={c2['g_ann']:.2%}/yr wealth x{c2['wealth']:.1f}  g'(2)={c2['g1_ann']:.2%}/yr per unit  to 2.5: first-order {c2['first_order_25']:.2%}"
  f" exact {c2['gain_to_25']:.2%}  00631L actual x{c2['real_00631L']:.1f} ({c2['real_00631L_ann']:.2%}/yr)")
y22 = [y for y in st["years"] if y["year"] == 2022][0]
P(f"Ex4b 2022: mu={y22['mu_bp']:.2f} bp/day f*={y22['f']:.2f} long-only f=0, g'(0)=mu={y22['g1_at_0']:.4%}/day  0050 return {y22['ret']:.2%}")
fy = [y["f"] for y in st["years"]]
P(f"  per-year f* range: {min(fy):.2f} .. {max(fy):.2f}; corners: " + ", ".join(f"{y['year']}:{y['f_cap']:.0f}" for y in st["years"]))
# KC 4: x^3 - 3x on [-2, 3]
h = lambda x: x**3 - 3 * x
P(f"KC4 values: h(-2)={h(-2)} h(-1)={h(-1)} h(1)={h(1)} h(3)={h(3)}")

# ---------------------------------------------------------------- Section 5
P("== Section 5")
p, G, L = 0.5, 0.02, 0.01
fs = f_bin(p, G, L); gs = g_star(p, G, L)
P(f"Ex5 +2/-1: f*={fs:.2f} risk={fs*L:.2%} g*={gs:.4%}/trade (check {g_bin(fs,p,G,L):.6f})  1+f*G={1+fs*G:.2f} 1-f*L={1-fs*L:.2f}"
  f"  half: g={g_bin(fs/2,p,G,L):.4%} share={g_bin(fs/2,p,G,L)/gs:.3f}  f=0.25: g={g_bin(0.25,p,G,L):.4%} share={g_bin(0.25,p,G,L)/gs:.4f}"
  f"  zero growth={zero_growth(p,G,L):.4f}  domain=(-{1/G:.0f},{1/L:.0f})  arith at f*={fs*0.005:.2%}  e^(100 g*)={exp(100*gs):.0f}")
P(f"  break-even pi=L/(G+L)={L/(G+L):.4f}  df*/dp=1/L+1/G={1/L+1/G:.0f}")
p0 = log(1 / (1 - 25 * L)) / log((1 + 25 * G) / (1 - 25 * L))
P(f"  p where g(25)=0: {p0:.5f}  f*(p0)={f_bin(p0,G,L):.4f}  25/f*(p0)={25/f_bin(p0,G,L):.4f}")
P("Exhibit 5: p | f* | risk | g* | g(25)")
for pp in [0.60, 0.55, 0.50, 0.45, p0, 0.40, 1 / 3]:
    fp = f_bin(pp, G, L)
    gsp = g_star(pp, G, L) if fp > 1e-12 else 0.0
    P(f"  p={pp:.4f} f*={fp:6.2f} risk={fp*L:6.2%} g*={gsp:.4%} g(25)={g_bin(25,pp,G,L):+.4%}")
# Example 6: breakout system
p, G, L = 0.40, 0.06, 0.02
fs6 = f_bin(p, G, L); gs6 = g_star(p, G, L)
P(f"Ex6 breakout: f*={fs6:.2f} risk={fs6*L:.0%} b={G/L:.0f} p-q/b={p-(1-p)/(G/L):.2f} g*={gs6:.3%}  half: g={g_bin(fs6/2,p,G,L):.3%} share={g_bin(fs6/2,p,G,L)/gs6:.3f}"
  f"  df/dp={1/L+1/G:.2f}  5 losses: full {1-(1-fs6*L)**5:.1%}, half {1-(1-fs6*L/2)**5:.1%}, prob {0.6**5:.2%}")
f35 = f_bin(0.35, G, L)
P(f"  if p=0.35: f*={f35:.3f} lambda={fs6/f35:.3f} g(10)={g_bin(10,0.35,G,L):.3%} g*={g_star(0.35,G,L):.3%} share={g_bin(10,0.35,G,L)/g_star(0.35,G,L):.3f}")
# KC 5
P(f"KC5: f*={f_bin(0.45,0.03,0.015):.3f} risk={f_bin(0.45,0.03,0.015)*0.015:.2%} p-q/b={0.45-0.55/2:.3f}")
# envelope for the binary bet (Section 7 text)
P(f"Envelope binary: dg*/dp=ln((1+f*G)/(1-f*L))={log((1+25*0.02)/(1-25*0.01)):.4f}  exact g*(0.51)-g*(0.50)={g_star(0.51,0.02,0.01)-g_star(0.50,0.02,0.01):.5f}"
  f"  first-order={0.01*log(2):.5f}")
# deep dive: KL
pi = 0.01 / 0.03
P(f"KL check: p ln(p/pi)+q ln(q/(1-pi))={0.5*log(0.5/pi)+0.5*log(0.5/(1-pi)):.6f} vs g*={g_star(0.5,0.02,0.01):.6f}")

# ---------------------------------------------------------------- Section 6
P("== Section 6")
c_, F_, n_, P0 = 1.5, 100.0, 5, 97.80
price = lambda y: sum(c_ / (1 + y) ** t for t in range(1, n_ + 1)) + F_ / (1 + y) ** n_
dprice = lambda y: -sum(t * c_ / (1 + y) ** (t + 1) for t in range(1, n_ + 1)) - n_ * F_ / (1 + y) ** (n_ + 1)
y = 0.015
P("Ex7 YTM Newton: n y P(y)-P P'(y)")
for it in range(5):
    P(f"  {it} {y:.10%} {price(y)-P0:+.3e} {dprice(y):.2f}")
    y = y - (price(y) - P0) / dprice(y)
ytm = brentq(lambda y: price(y) - P0, 0, 0.1, xtol=1e-15)
a, b, nb = 0.0, 0.10, 0
while b - a >= 1e-10:
    m = (a + b) / 2; nb += 1
    a, b = (m, b) if price(m) - P0 > 0 else (a, m)
P(f"  ytm={ytm:.6%}  price at 0%={price(0):.2f} at 10%={price(0.1):.2f}  bisection steps to 1e-10: {nb}  (log2(0.1/1e-10)={log(0.1/1e-10,2):.2f})")
tr = st["trunc"]
P(f"Ex8 truncations: 2nd {tr['order2']:.3f} 3rd {tr['order3']:.3f} 4th {tr['order4']:.3f} exact {tr['exact']:.3f} max|fR|={tr['maxabs_fR']:.3f}"
  f" skew={mo['skew']:.3f} exkurt={mo['exkurt']:.2f}")
nw = st["newton"]
P("Exhibit 6 Newton: " + "; ".join(f"n={r['n']} f={r['f']:.9f} err={r['err']:.1e} g1={r['g1']:.3e} g2={r['g2']:.4e}" for r in nw[:5]))
P(f"  C=|g'''/(2g'')|={k['newton_C']:.3f}")
bs = st["bisection"]
P("Exhibit 6 bisection widths: " + "; ".join(f"n={r['n']} w={r['width']:.3e} err={r['mid_err']:.1e}" for r in bs if r["n"] in (0, 1, 2, 3, 4, 5, 10, 20, 30, 44)))
P(f"KC6: steps for [0,10%] to 1e-6: {log(0.10/1e-6, 2):.2f} -> {int(np.ceil(log(0.10/1e-6, 2)))}")
# pitfall: two IRRs and a flat tangent
cf2 = [-100, 230, -132]
npv2 = lambda r: sum(x / (1 + r) ** t for t, x in enumerate(cf2))
dnpv2 = lambda r: sum(-t * x / (1 + r) ** (t + 1) for t, x in enumerate(cf2))
for r0 in (0.14, 0.15):
    r = r0; path = [r]
    for it in range(12):
        r = r - npv2(r) / dnpv2(r); path.append(r)
    P(f"Pitfall two IRRs from {r0:.0%}: " + " -> ".join(f"{x:.2%}" for x in path[:4]) + f" ... {path[-1]:.4%}")
P(f"  roots: NPV(10%)={npv2(0.10):.1e} NPV(20%)={npv2(0.20):.1e}  flat at r={264/230-1:.2%}")
# Newton on 0050's Kelly condition from other starts (robustness remark)
import polars as pl
R = pl.read_parquet(HERE / "processed" / "etf_daily_returns.parquet")["R_0050"].to_numpy()
starts, worst = np.round(np.arange(-9.9, 9.95, 0.1), 1), 0
for f0 in starts:
    f = f0
    for it in range(60):
        f = f - (R / (1 + f * R)).mean() / (-((R / (1 + f * R)) ** 2).mean())
        if not (-10 < f < 10): raise SystemExit(f"left domain from {f0}")
        if abs(f - k["f"]) < 1e-12: worst = max(worst, it + 1); break
P(f"  Newton on 0050 Kelly condition: converged from all {len(starts)} starts in [-9.9, 9.9]; max iterations {worst}")

# ---------------------------------------------------------------- Section 7
P("== Section 7")
lv = {r["name"]: r for r in st["levels"]}
P(f"Ex9 half Kelly: g={lv['half']['g_ann']:.2%} vs {lv['full']['g_ann']:.2%} share={lv['half']['g_ann']/lv['full']['g_ann']:.3f}"
  f" vol {lv['half']['vol_ann']:.1%} vs {lv['full']['vol_ann']:.1%}  mdd {lv['half']['mdd']:.1%} vs {lv['full']['mdd']:.1%}"
  f" worst {lv['half']['worst']:.1%} vs {lv['full']['worst']:.1%} wealth {lv['half']['wealth']:.0f} vs {lv['full']['wealth']:.0f}")
ft = st["flat_top_half"]
P(f"  flat top: 0.5|g''| per unit^2={ft['per_unit']:.4f}/yr  predicted loss={ft['pred_loss']:.1%} actual={ft['actual_loss']:.1%}")
P("  fractions: " + ", ".join(f"{kk}:{v:.1%} (quad {1-(1-float(kk))**2:.2%})" for kk, v in st["fractions"].items()))
lam = np.round(np.arange(0, 1.2501, 0.01), 2)
fB = 25.0; gB = g_star(0.5, 0.02, 0.01)
devB = max(abs(g_bin(l * fB, 0.5, 0.02, 0.01) / gB - (1 - (1 - l) ** 2)) for l in lam)
P(f"  bet share: half {g_bin(12.5,0.5,0.02,0.01)/gB:.3f} 1.5x {g_bin(37.5,0.5,0.02,0.01)/gB:.3f} quarter {g_bin(6.25,0.5,0.02,0.01)/gB:.3f}; max dev from parabola on [0,1.25]: {devB:.4f}")
fi = st["financing"]
P(f"Ex10 financing: dV/dr={fi['dVdr']:.2f}  r={fi['r_ann']:.0%}/yr: first-order {fi['first_order']:.2%}  exact {fi['dV']:.2%}  f*(r)={fi['f_r']:.2f}"
  f"  V(r)={fi['Vr']:.2%}  at old f*={fi['g_at_old_f']:.2%}  gain from re-optimizing={fi['Vr']-fi['g_at_old_f']:.2%}  mean 1/(1+f*R)={k['mean_inv']:.12f}")
se = st["se"]
P(f"SE: se={se['se_mu']:.4%} t={se['t']:.2f} rel={se['rel']:.1%} CI=[{se['lo_mu']:.3%},{se['hi_mu']:.3%}] f=[{se['f_lo']:.1f},{se['f_hi']:.1f}]"
  f" lambda lo={se['lam_if_lo']:.2f} share={se['share_if_lo_quad']:.1%} lambda hi={se['lam_if_hi']:.2f} share={se['share_if_hi_quad']:.1%}")
ro = st["rolling"]
P(f"Rolling first window end {ro['first_end']}; ratio max/min={ro['max']/ro['min']:.1f}")
P(f"Rolling 3y: min {ro['min']:.2f} ({ro['min_end']}) max {ro['max']:.2f} ({ro['max_end']}) last {ro['last']:.2f} median {ro['median']:.2f}")
sh = st["sharpe"]
P(f"Sharpe view: SR={sh['sr_ann']:.2f} SR/sigma={sh['f_sr_over_sigma']:.2f} SR^2/2={sh['g_sr2_half']:.1%}")
# pitfall: Sharpe 3 backtest
SRb, sig = 3.0, 0.15
fb = SRb / sig
for SRt in (1.5, 1.0):
    lam = SRb / SRt; gt = SRt**2 / 2
    P(f"Pitfall SR3: f={fb:.0f}  true SR={SRt}: f*_true={SRt/sig:.2f} lambda={lam:.1f} share={2*lam-lam**2:.0f} g={(2*lam-lam**2)*gt:+.2f}/yr wealth factor/yr={exp((2*lam-lam**2)*gt):.3f}")
P(f"  backtest g*=SR^2/2={SRb**2/2:.2f}/yr -> x{exp(SRb**2/2):.0f} a year")
# KC 7
P(f"KC7: quad share at 1.5 = {1-0.5**2:.2f}; 0050 exact = {st['fractions']['1.5']:.3f}; vol ratio 1.5/0.5 = 3")

# ---------------------------------------------------------------- Practice problems
P("== Practice problems")
P(f"PP1 x e^-x: max at 1, value {exp(-1):.4f}")
P(f"PP3 g=0.12f-0.08f^2: f*={0.12/0.16:.2f} g*={0.12**2/(4*0.08):.4f} half={0.12*0.375-0.08*0.375**2:.5f} share={(0.12*0.375-0.08*0.375**2)/(0.12**2/0.32):.2f} zero={0.12/0.08:.2f}")
P(f"PP4 +5/-5 p=.55: f*={f_bin(0.55,0.05,0.05):.2f} risk={f_bin(0.55,0.05,0.05)*0.05:.0%} p-q={0.55-0.45:.2f}")
f6 = f_bin(0.30, 0.08, 0.02); f6b = f_bin(0.25, 0.08, 0.02)
P(f"PP6 p=.30 G=8% L=2%: f*={f6:.3f} risk={f6*0.02:.2%} b={0.08/0.02:.0f} p-q/b={0.30-0.70/4:.4f} g*={g_star(0.30,0.08,0.02):.4%}  pi={0.02/0.10:.2f}"
  f"  p=.25: f*={f6b:.4f} lambda={f6/f6b:.3f} g(f6;.25)={g_bin(f6,0.25,0.08,0.02):.4%} g*(.25)={g_star(0.25,0.08,0.02):.4%}"
  f"  1+f*G={1+f6*0.08:.3f} 1-f*L={1-f6*0.02:.4f}")
cf = [-100, 30, 40, 50]
npv = lambda r: sum(x / (1 + r) ** t for t, x in enumerate(cf))
dnpv = lambda r: sum(-t * x / (1 + r) ** (t + 1) for t, x in enumerate(cf))
r = 0.0; out = []
for it in range(5):
    out.append(f"r{it}={r:.6%} NPV={npv(r):+.4e}")
    r = r - npv(r) / dnpv(r)
P("PP7 IRR Newton: " + "; ".join(out))
irr = brentq(npv, 0, 0.5, xtol=1e-15); P(f"  IRR={irr:.4%}  NPV'(0)={dnpv(0):.0f}")
P(f"PP8 bisection [0,1] to 1e-8: {log(1e8, 2):.2f} -> {int(np.ceil(log(1e8, 2)))}")
x = 1.0; out = []
for it in range(5):
    out.append(f"x{it}={x:.9f} e={abs(x-sqrt(2)):.3e}")
    x = x - (x * x - 2) / (2 * x)
P("PP9 sqrt2: " + "; ".join(out) + f"  C=1/(2sqrt2)={1/(2*sqrt(2)):.3f}  ratios e2/e1^2={0.0024531/0.0857864**2:.3f} e3/e2^2={2.1239e-6/0.0024531**2:.3f}")
P(f"PP10 g=0.10f-0.05f^2 cap 0.8: f*={0.10/0.10:.1f} g(0.8)={0.10*0.8-0.05*0.64:.3f} g*={0.10**2/(4*0.05):.3f} g'(0.8)={0.10-0.10*0.8:.3f}")
SRb, sig = 2.4, 0.12
for SRt in (1.2, 0.8):
    lam = SRb / SRt; gt = SRt**2 / 2
    P(f"PP13 SR {SRb} sigma {sig}: f={SRb/sig:.0f} true SR {SRt}: f*_true={SRt/sig:.2f} lambda={lam:.0f} share={2*lam-lam**2:.0f} g={(2*lam-lam**2)*gt:+.2f}/yr factor={exp((2*lam-lam**2)*gt):.3f}")
h20 = st["halves"]["2020_2026"]
P(f"PP14 2020-2026: n={h20['n']} f*={h20['f']:.2f} mu/s2={h20['f_quad']:.2f}")
P(f"PP15 quadratic expansion of binary g: (pG-qL)/(pG^2+qL^2)={(0.5*0.02-0.5*0.01)/(0.5*0.02**2+0.5*0.01**2):.1f}")
P(f"PP12 half Kelly quad: share {1-0.25:.2f}, vol 0.50")
