"""Every number quoted in LM2 that does not come from the TX/TAIEX case (see lm02_case.py).

Run:  python3 data/lm02_numbers.py        (needs data/processed/etf_daily_returns.parquet from build_series.py)
"""
import math
from pathlib import Path

import numpy as np
import polars as pl
import sympy as sp

HERE = Path(__file__).resolve().parent
P = print
EPS = np.finfo(float).eps


def bond_price(y, c=0.02, n=10, face=100.0):
    """Annual-coupon bond, n years, coupon rate c, yield y (annual compounding)."""
    return sum(c * face / (1 + y) ** t for t in range(1, n + 1)) + face / (1 + y) ** n


def bond_dprice(y, c=0.02, n=10, face=100.0):
    """Exact derivative dP/dy by the power and chain rules."""
    return -sum(t * c * face / (1 + y) ** (t + 1) for t in range(1, n + 1)) - n * face / (1 + y) ** (n + 1)


def section(t):
    P("\n" + "=" * 8 + " " + t)


# ------------------------------------------------------------------ Section 2: limits
section("S2 limits")
P("h, (e^h-1)/h, bound 1/(1-h), ln(1+h)/h")
for h in (0.1, 0.01, 0.001, -0.001, -0.01, -0.1):
    P(f"  {h:+.3f}  {math.expm1(h)/h:.6f}  {1/(1-h):.6f}  {math.log1p(h)/h:.6f}")
P("annuity factor at r=2%: n, (1-1.02^-n)/0.02")
for n in (10, 30, 100, 1000):
    P(f"  n={n:5d}  {(1-1.02**-n)/0.02:.4f}")
P("  limit 1/r =", 1 / 0.02)
P("(1+1/n)^n:", [(n, round((1 + 1 / n) ** n, 5)) for n in (1, 12, 365, 1_000_000)], "e =", round(math.e, 5))
# Example: e^r as the limit of monthly/daily compounding of 2%
for n in (1, 12, 365):
    P(f"  (1+0.02/{n})^{n} = {(1+0.02/n)**n:.6f}")
P(f"  e^0.02 = {math.exp(0.02):.6f}")

# ------------------------------------------------------------------ Section 3: the derivative
section("S3 derivative of the 10-year 2% bond at y0 = 2%")
y0 = 0.02
P0 = bond_price(y0); dP = bond_dprice(y0)
P(f"P(2%) = {P0:.6f}   P'(2%) exact = {dP:.4f}")
P("difference quotients [P(y0+h)-P(y0)]/h and central [P(y0+h)-P(y0-h)]/(2h):")
for hbp in (100, 10, 1, 0.1, 0.01):
    h = hbp / 1e4
    fw = (bond_price(y0 + h) - P0) / h
    ce = (bond_price(y0 + h) - bond_price(y0 - h)) / (2 * h)
    P(f"  h={hbp:>6} bp  forward {fw:10.4f}  err {fw-dP:+9.4f}   central {ce:10.4f}  err {ce-dP:+.6f}")
P(f"P'(2%) exact to 8 decimals: {dP:.8f};  P(3%) = {bond_price(0.03):.4f}; MVT average slope 2%->3% = {(bond_price(0.03)-P0)/0.01:.4f}")
# 1-year and T-year zero from the definition
for y in (0.02,):
    P(f"zero 1y: P=100/(1+y), P'(y) = -100/(1+y)^2 = {-100/(1+y)**2:.4f} at y={y:.0%}; DV01 per 100 = {100/(1+y)**2*1e-4:.6f}; "
      f"per NT$100m face = {100/(1+y)**2*1e-4*1e6:,.0f}")
# secant of e^x at 0 (widget initial state)
q = math.expm1(0.5) / 0.5
P(f"widget: (e^0.5-1)/0.5 = {q:.5f}; error {q-1:.5f}; error/h {(q-1)/0.5:.5f}; central (e^0.5-e^-0.5)/1 = {(math.exp(0.5)-math.exp(-0.5))/1:.5f}")
P(f"annuity: 50 - a_100 = {50-(1-1.02**-100)/0.02:.4f}")

# ------------------------------------------------------------------ Section 4: rules
section("S4 rules")
# forward rate from an illustrative continuously compounded yield curve y(T) = 2.0% - 0.8% e^{-T/3}
yT = lambda T: 0.020 - 0.008 * math.exp(-T / 3)
dyT = lambda T: 0.008 / 3 * math.exp(-T / 3)
for T in (1, 5, 10):
    fwd = yT(T) + T * dyT(T)
    # numerical check: -d ln P / dT with P = exp(-y T)
    h = 1e-5
    num = -(math.log(math.exp(-yT(T + h) * (T + h))) - math.log(math.exp(-yT(T - h) * (T - h)))) / (2 * h)
    P(f"  T={T:2d}: y={yT(T):.5%}  y'={dyT(T):.6%}/yr  f=y+Ty'={fwd:.5%}  numeric {num:.5%}")
# leverage function f(F) = n m F / (E0 + n m (F-F0)) and its derivative -f(f-1)/F
m, F0, E0 = 200, 22116.0, 600_000.0
lev = lambda F: m * F / (E0 + m * (F - F0))
f0 = lev(F0)
d_lev = -f0 * (f0 - 1) / F0
P(f"  leverage A: f0={f0:.4f}; df/dF = {d_lev:.7f} per point; x100 points: {100*d_lev:.4f}; "
  f"exact f(F0+100)-f0 = {lev(F0+100)-f0:.4f}; f(F0+100) = {lev(F0+100):.4f} "
  f"(F={F0+100:,.0f}, notional {m*(F0+100):,.0f}, equity {E0+m*100:,.0f}); wipe-out level F0-E0/m = {F0-E0/m:,.0f}")
# sympy confirmations of the rules used in the text
x, yy, F, E, r, T, R, fK = sp.symbols("x y F E r T R f", real=True)
P("  sympy: d/dx ln x =", sp.diff(sp.log(x), x), "; d/dx e^x =", sp.diff(sp.exp(x), x),
  "; d/dy (1+y)^-T =", sp.simplify(sp.diff((1 + yy) ** (-T), yy)))
levF = 200 * F / (sp.Symbol("E0") + 200 * (F - sp.Symbol("F0")))
P("  sympy: d/dF leverage, simplified ratio to -f(f-1)/F:",
  sp.simplify(sp.diff(levF, F) / (-levF * (levF - 1) / F)))
P("  sympy: d/df ln(1+fR) =", sp.diff(sp.log(1 + fK * R), fK))

# ------------------------------------------------------------------ Section 5: sensitivities
section("S5 futures delta")
pos = {"TX": (2, 200), "MTX": (-3, 50), "TMF": (4, 10)}
delta = sum(n * mm for n, mm in pos.values())
P(f"  delta = {delta} NT$/pt; +150 pts -> {150*delta:+,} ; TX-equivalent {delta/200:.2f}; TMF to neutralise {-delta/10:.0f}")
Fx = 22344.0
P(f"  NT$ per 1% at F={Fx:,.0f}: {delta*Fx/100:,.0f}; points per 1% {Fx/100:.2f}; one TX per 1%: {200*Fx/100:,.0f}")
# fair value sensitivity to the dividend yield (formula from LM6): dF/dq = -T F
P(f"  dF/dq x 0.1% for T=0.25, F=22,000: {-0.25*22000*0.001:.2f} points")
section("S5 bond duration (10y 2% annual coupon at par)")
Dmod = -dP / P0
Dmac = Dmod * (1 + y0)
w = [(t, (0.02 * 100 + (100 if t == 10 else 0)) / 1.02 ** t / P0) for t in range(1, 11)]
P(f"  P={P0:.4f}  P'={dP:.4f}  Dmod={Dmod:.4f}  Dmac={Dmac:.4f}  sum t*w = {sum(t*wt for t, wt in w):.4f}")
P(f"  weights: " + ", ".join(f"{t}:{wt:.4f}" for t, wt in w))
P(f"  annuity factor (1-1.02^-10)/0.02 = {(1-1.02**-10)/0.02:.4f} (= Dmod of a par bond)")
P(f"  DV01 per 100 face = {-dP*1e-4:.5f}; per NT$100 million face = {-dP*1e-4*1e6:,.0f}")
for dbp in (1, 10, 25, 100):
    dy = dbp / 1e4
    ex = bond_price(y0 + dy) / P0 - 1; lin = -Dmod * dy
    P(f"  dy=+{dbp:>3}bp exact {ex:+.4%} linear {lin:+.4%} error {ex-lin:+.4%} ({(ex-lin)*1e4:+.3f} bp of price)")
for dbp in (-25, -100):
    dy = dbp / 1e4
    ex = bond_price(y0 + dy) / P0 - 1; lin = -Dmod * dy
    P(f"  dy={dbp:>4}bp exact {ex:+.4%} linear {lin:+.4%} error {ex-lin:+.4%}")
section("S5 PV of a 5-year zero: continuous vs annual compounding")
for rr in (0.02,):
    pv_c = 1e6 * math.exp(-5 * rr); pv_a = 1e6 / (1 + rr) ** 5
    P(f"  r={rr:.0%}: PV cont {pv_c:,.2f}, dPV/dr = {-5*pv_c:,.2f} (= -T PV), per bp {-5*pv_c*1e-4:,.2f}")
    P(f"  r={rr:.0%}: PV annual {pv_a:,.2f}, dPV/dr = {-5/(1+rr)*pv_a:,.2f} (= -T/(1+r) PV), mod dur {5/(1+rr):.4f}, per bp {-5/(1+rr)*pv_a*1e-4:,.2f}")

# ------------------------------------------------------------------ Section 6: elasticity
section("S6 elasticity")
# elasticity of leverage: account A on 11 June, hypothetical +1% move in F
fA = m * F0 / E0
for RF in (0.01, -0.01):
    f1 = fA * (1 + RF) / (1 + fA * RF)
    lin = fA * (1 + (1 - fA) * RF)
    loglin = fA * math.exp((1 - fA) * math.log1p(RF))
    P(f"  A f={fA:.4f}, RF={RF:+.0%}: exact {f1:.4f}  linear {lin:.4f}  log-linear {loglin:.4f}  eps=1-f={1-fA:.4f}")
# KC: f=6, +1%
f6 = 6 * 1.01 / (1 + 0.06)
P(f"  KC f=6, +1%: exact {f6:.4f}; first order 6*(1-0.05) = {6*0.95:.2f}")
# 00631L vs 0050
df = pl.read_parquet(HERE / "processed" / "etf_daily_returns.parquet")
R = df["R_0050"].to_numpy(); RL = df["R_00631L"].to_numpy(); dates = df["date"].to_list()
slope = np.polyfit(R, RL, 1)[0]
P(f"  00631L on 0050: n={len(R)}, OLS slope {slope:.3f}, corr {np.corrcoef(R, RL)[0,1]:.3f}")
yr = np.array([int(d[:4]) for d in dates]); by = {}
for yv in sorted(set(yr)):
    k = yr == yv; by[yv] = np.polyfit(R[k], RL[k], 1)[0]
full_years = {k: v for k, v in by.items() if 2015 <= k <= 2025}
lo = min(full_years, key=full_years.get); hi = max(full_years, key=full_years.get)
P(f"  by full calendar year 2015-2025: min {full_years[lo]:.3f} ({lo}), max {full_years[hi]:.3f} ({hi})")
P("  " + ", ".join(f"{k}:{v:.3f}" for k, v in by.items()))
for d in ("2025-04-07", "2024-08-05"):
    i = dates.index(d)
    P(f"  {d}: 0050 {R[i]:+.3%}  00631L {RL[i]:+.3%}  ratio {RL[i]/R[i]:.3f}")
# FX example (illustrative)
Ru, Rx = 0.06, -0.06
P(f"  FX: exact TWD return {(1+Ru)*(1+Rx)-1:+.4%}; first order {Ru+Rx:+.2%}; cross term {Ru*Rx:+.4%}; "
  f"log: {math.log1p(Ru):+.5f} + {math.log1p(Rx):+.5f} = {math.log1p(Ru)+math.log1p(Rx):+.5f}; exp-1 = {math.expm1(math.log1p(Ru)+math.log1p(Rx)):+.4%}")
# margin-financed 0050 purchase (illustrative)
shares, px, own = 1000, 60.0, 24_000.0
lev_m = shares * px / own
P(f"  margin purchase: assets {shares*px:,.0f}, equity {own:,.0f}, loan {shares*px-own:,.0f}, f={lev_m:.2f}; 0050 -4% -> equity {-0.04*lev_m:+.0%}")
# elasticity of a sum = value-weighted average (portfolio of 60% 0050-like with eps 1 and 40% cash with eps 0)
P(f"  portfolio elasticity 0.6*1 + 0.4*0 = {0.6*1+0.4*0:.1f}")

# ------------------------------------------------------------------ Section 7: differentials
section("S7 differentials")
# square-root / ln examples for KC
P(f"  ln(1.03) = {math.log1p(0.03):.6f} vs differential 0.03; error {math.log1p(0.03)-0.03:.6f}")
P(f"  ln(0.90) = {math.log(0.9):.6f} vs differential -0.10; error {math.log(0.9)+0.1:.6f}")
# bond: dP for +5bp per 100 face
P(f"  bond dP for +5bp: P'(y0)*0.0005 = {dP*0.0005:.4f}; exact {bond_price(0.0205)-P0:.4f}")
# MVT error bound demo: halving dx quarters error for e^x linearisation at 0
errs_lin = [math.expm1(dxv) - dxv for dxv in (0.2, 0.1, 0.05)]
for dxv, ev in zip((0.2, 0.1, 0.05), errs_lin):
    P(f"  e^x at 0, dx={dxv}: error e^dx-(1+dx) = {ev:.6f}")
P(f"  ratios {errs_lin[0]/errs_lin[1]:.2f}, {errs_lin[1]/errs_lin[2]:.2f};  ln error ratio 10% vs 3%: "
  f"{(math.log(0.9)+0.1)/(math.log1p(0.03)-0.03):.1f}  ((10/3)^2 = {(10/3)**2:.1f})")

# ------------------------------------------------------------------ Section 8: numerical derivatives
section("S8 numerical derivatives")
P(f"  machine epsilon {EPS:.6e}  sqrt {math.sqrt(EPS):.3e}  cbrt {EPS**(1/3):.3e}")
# error table for the bond derivative at y0 (relative to |P'|)
P("  h, forward D, rel err, central D, rel err")
tab = []
for k in range(1, 13):
    h = 10.0 ** (-k)
    fw = (bond_price(y0 + h) - P0) / h
    ce = (bond_price(y0 + h) - bond_price(y0 - h)) / (2 * h)
    tab.append((k, fw, (fw - dP) / abs(dP), ce, (ce - dP) / abs(dP)))
    P(f"  1e-{k:02d}  {fw:14.8f}  {(fw-dP)/abs(dP):+.2e}  {ce:14.8f}  {(ce-dP)/abs(dP):+.2e}")
# derivatives needed for the step-size rule
ysym = sp.Symbol("y")
Psym = sum(sp.Rational(2) / (1 + ysym) ** t for t in range(1, 11)) + 100 / (1 + ysym) ** 10
d2 = float(sp.diff(Psym, ysym, 2).subs(ysym, sp.Rational(1, 50)))
d3 = float(sp.diff(Psym, ysym, 3).subs(ysym, sp.Rational(1, 50)))
d1 = float(sp.diff(Psym, ysym, 1).subs(ysym, sp.Rational(1, 50)))
P(f"  sympy P'={d1:.4f} P''={d2:.4f} P'''={d3:.4f}  (P''/P = {d2/100:.4f} = convexity)")
hf = 2 * math.sqrt(EPS * P0 / abs(d2)); hc = (3 * EPS * P0 / abs(d3)) ** (1 / 3)
Ef = 2 * math.sqrt(EPS * P0 * abs(d2)); Ec = (abs(d3) / 6) * hc ** 2 + EPS * P0 / hc
P(f"  optimal h forward ~ {hf:.2e} (min err ~ {Ef:.2e}, rel {Ef/abs(dP):.1e}); central ~ {hc:.2e} (min err ~ {Ec:.2e}, rel {Ec/abs(dP):.1e})")
# best observed on a fine grid
ks = np.arange(-16, 0.001, 0.25); best = {}
for name in ("forward", "central"):
    errs = []
    for kk in ks:
        h = 10.0 ** kk
        D = (bond_price(y0 + h) - P0) / h if name == "forward" else (bond_price(y0 + h) - bond_price(y0 - h)) / (2 * h)
        errs.append(abs(D - dP))
    errs = np.array(errs); j = int(np.argmin(np.where(errs > 0, errs, np.inf)))
    best[name] = (ks[j], errs[j])
    P(f"  grid best {name}: h=1e{ks[j]:.2f}  abs err {errs[j]:.2e}  rel {errs[j]/abs(dP):.1e}")
# 1bp bump estimates of Dmod
h = 1e-4
Dm_fw = -((bond_price(y0 + h) - P0) / h) / P0
Dm_ce = -((bond_price(y0 + h) - bond_price(y0 - h)) / (2 * h)) / P0
P(f"  1bp bump: Dmod forward {Dm_fw:.6f} (err {Dm_fw-Dmod:+.6f}), central {Dm_ce:.6f} (err {Dm_ce-Dmod:+.2e}); exact {Dmod:.6f}; "
  f"accuracy ratio {abs(Dm_fw-Dmod)/abs(Dm_ce-Dmod):,.0f}")
dec = [(t[0], abs(t[2]), abs(t[4])) for t in tab]          # (k, |rel err forward|, |rel err central|) for h = 1e-k
P(f"  decade grid: forward min |rel| at 1e-{min(dec, key=lambda z: z[1])[0]} ({min(z[1] for z in dec):.2e}); "
  f"central min at 1e-{min(dec, key=lambda z: z[2])[0]} ({min(z[2] for z in dec):.2e}); "
  f"forward |rel| at 1e-8..1e-10: {[f'{z[1]:.2e}' for z in dec if 8 <= z[0] <= 10]}")
# kink: call payoff max(x-1,0) at x=1
call = lambda v: max(v - 1.0, 0.0)
for h in (0.1, 0.001):
    P(f"  call kink h={h}: forward {(call(1+h)-call(1))/h:.3f} backward {(call(1)-call(1-h))/h:.3f} central {(call(1+h)-call(1-h))/(2*h):.3f}")
# ln x at 2 with h = 0.01 (practice problem) and order check by halving
lnerr = []
for h in (0.01, 0.005):
    fw = (math.log(2 + h) - math.log(2)) / h; ce = (math.log(2 + h) - math.log(2 - h)) / (2 * h)
    lnerr.append((fw - 0.5, ce - 0.5))
    P(f"  ln at 2, h={h}: forward {fw:.6f} err {fw-0.5:+.7f}; central {ce:.7f} err {ce-0.5:+.3e}")
P(f"  ln ratios when halving: forward {lnerr[0][0]/lnerr[1][0]:.2f}, central {lnerr[0][1]/lnerr[1][1]:.2f}; "
  f"central vs forward accuracy at h=0.01: {abs(lnerr[0][0])/abs(lnerr[0][1]):.0f}x")
# TAIFEX margin table effective 2026-08-12 (official figures quoted in Section 6): check the proportionality
IM = {"TX": 701_000, "MTX": 175_250, "TMF": 35_050}; MM = {"TX": 538_000, "MTX": 134_500, "TMF": 26_900}
P(f"  TAIFEX margins effective 2026-08-12 (quoted): initial {IM}, maintenance {MM}")
P(f"  margins: MTX/TX = {IM['MTX']/IM['TX']:.4f} (50/200 = {50/200}), TMF/TX = {IM['TMF']/IM['TX']:.4f} (10/200 = {10/200}); "
  f"maintenance/initial TX = {MM['TX']/IM['TX']:.3f}")
# e^x at 0: forward/central error ratios when halving h (order check)
for h in (0.1, 0.05, 0.025):
    fw = (math.exp(h) - 1) / h - 1; ce = (math.exp(h) - math.exp(-h)) / (2 * h) - 1
    P(f"  e^x at 0, h={h}: forward err {fw:.6f}  err/h {fw/h:.4f}   central err {ce:.3e}  err/h^2 {ce/h**2:.5f}")

# ------------------------------------------------------------------ Practice problems
section("Practice problems")
P(f"  PP1 lim (e^(2h)-1)/h = 2")
P(f"  PP2 d/dx ln(1+3x) at 0 = 3")
P(f"  PP3 sqrt at 4 = {1/(2*math.sqrt(4)):.4f}")
# PP5 position delta
d5 = 1 * 200 - 3 * 50 + 7 * 10
P(f"  PP5 delta {d5} NT$/pt; -250 pts -> {d5*-250:+,}")
# PP6 elasticity of 2 MTX account
notional = 2 * 50 * 25_000; f6p = notional / 500_000
P(f"  PP6 notional {notional:,}; f {f6p:.1f}; +1.2% -> {f6p*1.2:.1f}%; distractors: 2 x 1.2% = {2*1.2:.1f}%, f = {f6p:.1f}")
# PP7 leverage drift f=8, +2%
f8 = 8 * 1.02 / (1 + 8 * 0.02)
P(f"  PP7 f=8, +2%: exact {f8:.4f}; linear {8*(1+(1-8)*0.02):.4f}; log-linear {8*math.exp((1-8)*math.log(1.02)):.4f}")
P(f"  PP7 f=8, -2%: exact {8*0.98/(1-0.16):.4f}; linear {8*(1+(1-8)*-0.02):.4f}")
# PP8 zero coupon 5y at 2%
P(f"  PP8 5y zero at 2%: annual Dmod {5/1.02:.4f}; continuous {5:.4f}; price annual {100/1.02**5:.4f}")
# PP10 FX
Ru, Rx = 0.08, -0.05
P(f"  PP10 FX: exact {(1+Ru)*(1+Rx)-1:+.4%}; first order {Ru+Rx:+.2%}; cross {Ru*Rx:+.4%}")
# PP11 numerical ln at 2, h=0.01 (printed above)
# PP13 Kelly-style derivative of g(f) = 0.5 ln(1+0.02f) + 0.5 ln(1-0.01f)
g1 = lambda f: 0.5 * 0.02 / (1 + 0.02 * f) - 0.5 * 0.01 / (1 - 0.01 * f)
P(f"  PP13 g'(0) = {g1(0):.5f}; g'(10) = {g1(10):.6f}; g'(25) = {g1(25):.2e}; g'(40) = {g1(40):.6f}")
# PP15 bond bump in Python: grid best h (printed above)
# PP14 current yield CY = C/P: dCY/dy = CY * Dmod
CY = 2 / P0
P(f"  PP14 CY={CY:.4%}; dCY/dy = CY*Dmod = {CY*Dmod:.5f}; x10bp = {CY*Dmod*0.001*1e4:.2f} bp; exact CY(2.1%) = {2/bond_price(0.021):.5%} "
  f"(+{(2/bond_price(0.021)-CY)*1e4:.2f} bp); P(2.1%) = {bond_price(0.021):.4f}")
# PP15 fair value F = S e^{(r-q)T} with illustrative inputs
S, rr, qq, TT = 22470.10, 0.016, 0.030, 0.25
Ffv = S * math.exp((rr - qq) * TT)
P(f"  PP15 F={Ffv:.1f}; dF/dS = {math.exp((rr-qq)*TT):.6f}; elasticity 1; dF/dq = {-TT*Ffv:,.1f} per unit; per +0.1% q: {-TT*Ffv*0.001:.2f} pts")
