"""Prints every number quoted in LM4's examples, knowledge checks, practice problems and solutions.

Data-based numbers come from processed/lm04_stats.json (run lm04_stats.py first);
the rest are computed here from the stated assumptions. Exhibits and examples are named by their labels in
src/lm04.md ([[eg:coin]], [[ex:psens]], ...), never by number. Binary bet: gain b and loss a per unit staked.
Where the module prints rounded inputs next to a result, the result is recomputed here from those printed inputs too.
Run after lm04_stats.py:  uv run python data/lm04_numbers.py
"""
import json
from math import exp, log, log1p, log2, sqrt
from pathlib import Path

import numpy as np
import polars as pl
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
st = json.loads((HERE / "processed" / "lm04_stats.json").read_text(encoding="utf-8"))
P = print
A_PRINTED, MU_PRINTED, S_PRINTED = 243.11, 0.0008712, 0.012385      # as printed in the module (A = 2,902 / 11.937)


# ---------------------------------------------------------------- binary-bet helpers (Section 5)
def g_bin(f, p, b, a):
    return p * log1p(f * b) + (1 - p) * log1p(-f * a)


def f_bin(p, b, a):
    return p / a - (1 - p) / b


def g_star(p, b, a):
    q = 1 - p
    return p * log(p * (a + b) / a) + q * log(q * (a + b) / b)


def zero_growth(p, b, a):
    fs = f_bin(p, b, a)
    return brentq(lambda f: g_bin(f, p, b, a), fs, (1 / a) * (1 - 1e-12), xtol=1e-14)


# ---------------------------------------------------------------- Introduction: the case exhibit and its note
P("== Introduction")
mo = st["mom"]
A = st["A"]
k = st["kelly"]
lv = {r["name"]: r for r in st["levels"]}
P(f"[[ex:case]] note: T={st['T']} returns over {st['T'] / A:.4f} years -> A={A:.4f} (printed {A_PRINTED}; 2902/11.937="
  f"{2902 / 11.937:.3f});  mu={mo['mu']:.7%} s={mo['s']:.7%};  printed mu/s^2={MU_PRINTED / S_PRINTED**2:.3f}")
for name in ("1", "2", "half", "full", "zero"):
    r = lv[name]
    P(f"  f={r['f']:.4f}: annual log growth={r['g_ann']:.4%} (x A printed: {r['g_ann'] / A * A_PRINTED:.4%})  growth of 1="
      f"{r['wealth']:.3f}  vol={r['vol_ann']:.4%}  mdd={r['mdd']:.4%}  worst={r['worst']:.4%}")
for f_print in (1, 2, 2.71, 5.42, 9.74, 2.7107, 5.4215, 9.7365):
    P(f"  printed recipe: vol at f={f_print} = f s sqrt(A) = {f_print * S_PRINTED * sqrt(A_PRINTED):.4%}"
      f"  (worst day {-0.1 * f_print:.2%})")

# ---------------------------------------------------------------- Section 2
P("== Section 2")
P(f"[[eg:quadkelly]] 0050: mu={mo['mu']:.5%} s={mo['s']:.4%} m2={mo['m2']:.4e} f_q=mu/m2={mo['mu_over_m2']:.3f} mu/s2={mo['mu_over_s2']:.3f}"
  f" (mu/s)^2={mo['sr_daily']**2:.4f} quad g* per day={mo['mu']**2/(2*mo['m2']):.4%} = {st['quad']['g_ann']:.2%}/yr"
  f"  exact f*={k['f']:.2f} ({k['g_ann']:.2%}/yr): rule {mo['mu_over_m2']/k['f']-1:.1%} too high, growth {st['quad']['g_ann']-k['g_ann']:.2%} too high")
P(f"  printed inputs: m2=s^2+mu^2={S_PRINTED**2 + MU_PRINTED**2:.4e}  f_q={MU_PRINTED / 0.00015415:.3f}  mu/s^2="
  f"{MU_PRINTED / S_PRINTED**2:.3f}  0.2462% x A={0.002462 * A_PRINTED:.4%}")
ov = st["overshoot"]
P(f"  why: at f_q, f^2 m3={ov['cubic_at_fq']:.3e} vs f^3 m4={ov['quartic_at_fq']:.3e} (normal: {ov['cubic_at_fq_normal']:.3e} vs"
  f" {ov['quartic_at_fq_normal']:.3e});  m4 / normal m4 = {ov['m4_over_normal']:.1f};  excess kurtosis {mo['exkurt']:.2f}")
P(f"  without the limit days {ov['limit_days']}: rule {ov['without_mu_m2']:.2f} vs exact {ov['without_f']:.2f};"
  f" excess kurtosis {ov['without_exkurt']:.2f};  |f*R|>10%: {ov['big_days']} days vs normal {ov['big_days_normal']:.0f}")
P(f"  overshoot without them {ov['without_gap']:.4f} against {ov['gap']:.4f} on the full sample: {ov['without_gap'] / ov['gap']:.3f}"
  f" of it (printed values: {(5.92 - 5.74) / (5.652 - 5.42):.3f})")
mu, m2 = 0.005, 0.5 * 0.02**2 + 0.5 * 0.01**2
P(f"[[eg:quadkelly]] bet: mu={mu:.3%} E[R^2]={m2:.5f} f_q={mu/m2:.2f} quad g*={mu**2/(2*m2):.4%}"
  f" exact f*={f_bin(0.5, 0.02, 0.01):.2f} exact g*={g_star(0.5, 0.02, 0.01):.4%}  fR at 20: +{20*0.02:.0%}/-{20*0.01:.0%}")
P(f"  drag at the optimum: arithmetic return at f*={k['arith_ann']:.2%}/yr  growth={k['g_ann']:.2%}/yr  share kept={k['drag_share']:.3f}")
# KC: x^3 - 6x^2 + 9x + 1
h = lambda x: x**3 - 6 * x**2 + 9 * x + 1
P(f"KC crit x=1: h={h(1):.0f} h''={6*1-12}; x=3: h={h(3):.0f} h''={6*3-12}")

# ---------------------------------------------------------------- Section 3
P("== Section 3")
z = st["zero_growth"]
P(f"[[eg:zerogrowth]]: exact f0={z['f']:.2f} = {z['ratio']:.2f} f*  quad zero 2mu/m2={z['quad_zero']:.2f}  worst day at f0:"
  f" 1-{z['f']*0.1:.4f}={1-z['f']*0.1:.4f}, log {z['worst_day_log']:.2f}  at f*: {st['worst_day_at_fstar_log']:.2f} of total {st['total_log_at_fstar']:.2f}")
P(f"  printed: f={z['f']:.3f} -> 1-{z['f'] * 0.1:.4f}; ln(0.0263)={log(0.0263):.3f};  ln(1-0.54)={log(0.46):.3f} ln(1+0.54)={log(1.54):.3f}")
P(f"  g''(f*)={k['g2_day']:.4e} per day  domain=({st['domain']['lo']:.4f},{st['domain']['hi']:.4f})")

# ---------------------------------------------------------------- Section 4
P("== Section 4")
c2 = st["cap2"]
P(f"[[eg:corners]] (1) cap 2: g(2)={c2['g_ann']:.2%}/yr wealth x{c2['wealth']:.1f}  g'(2)={c2['g1_ann']:.2%}/yr per unit  to 2.5: first-order {c2['first_order_25']:.2%}"
  f" exact {c2['gain_to_25']:.2%}  00631L actual x{c2['real_00631L']:.1f} ({c2['real_00631L_ann']:.2%}/yr)")
y22 = next(y for y in st["years"] if y["year"] == 2022)
P(f"[[eg:corners]] (2) 2022: mu={y22['mu_bp']:.2f} bp/day f*={y22['f']:.2f} long-only f=0, g'(0)=mu={y22['g1_at_0']:.4%}/day  0050 return {y22['ret']:.2%}")
fy = [y["f"] for y in st["years"]]
P(f"[[ex:years]] per-year f* range: {min(fy):.2f} .. {max(fy):.2f}; corners: " + ", ".join(f"{y['year']}:{y['f_cap']:.0f}" for y in st["years"]))
P(f"  years with mu<0: {[y['year'] for y in st['years'] if y['mu_bp'] < 0]};  with f*>2: {sum(y['f'] > 2 for y in st['years'])}")
P("  partial years (not in the rows): " + "; ".join(f"{y['year']} ({y['first']}..{y['last']}, n={y['n']}): {y['ret']:+.2%}, f*={y['f']:.2f}"
                                               for y in st["partial_years"])
  + f";  rows compound to {st['full_years_compound']:+.1%}, whole sample {st['sample_total_return']:+.2%}")
# KC: x^3 - 3x on [-2, 3]
h = lambda x: x**3 - 3 * x
P(f"KC values: h(-2)={h(-2)} h(-1)={h(-1)} h(1)={h(1)} h(3)={h(3)}")

# ---------------------------------------------------------------- Section 5
P("== Section 5")
p, b, a = 0.5, 0.02, 0.01
fs = f_bin(p, b, a); gs = g_star(p, b, a)
P(f"[[eg:coin]] +2/-1: f*={fs:.2f} risk={fs*a:.2%} f*a=p-qa/b={p-(1-p)*a/b:.2f} g*={gs:.4%}/trade (check {g_bin(fs,p,b,a):.6f})"
  f"  1+f*b={1+fs*b:.2f} 1-f*a={1-fs*a:.2f}  half: g={g_bin(fs/2,p,b,a):.4%} share={g_bin(fs/2,p,b,a)/gs:.3f}"
  f"  f=0.25: g={g_bin(0.25,p,b,a):.4%} share={g_bin(0.25,p,b,a)/gs:.4f}  zero growth={zero_growth(p,b,a):.4f}"
  f"  domain=(-{1/b:.0f},{1/a:.0f})  arith at f*={fs*0.005:.2%}")
P(f"  break-even pi=a/(a+b)={a/(a+b):.4f}  df*/dp=1/a+1/b={1/a+1/b:.0f}")
p0 = log(1 / (1 - 25 * a)) / log((1 + 25 * b) / (1 - 25 * a))
P(f"  p where g(25)=0: {p0:.5f}  f*(p0)={f_bin(p0,b,a):.4f}  25/f*(p0)={25/f_bin(p0,b,a):.4f}")
P("[[ex:psens]]: p | f* | risk f*a | g* | g(25)")
for pp in [0.60, 0.55, 0.50, 0.45, p0, 0.40, 1 / 3]:
    fp = f_bin(pp, b, a)
    gsp = g_star(pp, b, a) if fp > 1e-12 else 0.0
    P(f"  p={pp:.5f} f*={fp:6.2f} risk={fp*a:6.2%} g*={gsp:.4%} g(25)={g_bin(25,pp,b,a):+.4%}")
P(f"  at p=0.40: expected return per unit {0.40*0.02-0.60*0.01:+.2%}")
# KC: +3% / -1.5% at p = 0.45
P(f"KC: f*={f_bin(0.45,0.03,0.015):.3f} risk={f_bin(0.45,0.03,0.015)*0.015:.2%} p-qa/b={0.45-0.55*0.015/0.03:.3f}")
# deep dive: relative entropy
pi = a / (a + b)
P(f"KL check: p ln(p/pi)+q ln(q/(1-pi))={0.5*log(0.5/pi)+0.5*log(0.5/(1-pi)):.6f} vs g*={g_star(0.5,0.02,0.01):.6f}")

# ---------------------------------------------------------------- Section 6
P("== Section 6")
dg_ = st["degree"]
P(f"Kelly condition as a polynomial: {dg_['zero_days']} zero-return days, {dg_['distinct_nonzero']} distinct non-zero returns -> degree {dg_['degree']}")
cpn, F_, n_, P0 = 1.5, 100.0, 5, 97.80
price = lambda y: sum(cpn / (1 + y) ** t for t in range(1, n_ + 1)) + F_ / (1 + y) ** n_
dprice = lambda y: -sum(t * cpn / (1 + y) ** (t + 1) for t in range(1, n_ + 1)) - n_ * F_ / (1 + y) ** (n_ + 1)
y = 0.015
P("[[eg:ytm]] Newton: n y u(y)=P(y)-97.80 u'(y)")
for it in range(5):
    P(f"  {it} {y:.10%} {price(y)-P0:+.3e} {dprice(y):.2f}")
    y = y - (price(y) - P0) / dprice(y)
ytm = brentq(lambda y: price(y) - P0, 0, 0.1, xtol=1e-15)
lo_, hi_, nb = 0.0, 0.10, 0
while hi_ - lo_ >= 1e-10:
    m = (lo_ + hi_) / 2; nb += 1
    lo_, hi_ = (m, hi_) if price(m) - P0 > 0 else (lo_, m)
P(f"  ytm={ytm:.6%}  price at 0%={price(0):.2f} at 10%={price(0.1):.2f}  bisection steps to a bracket width of 1e-10: {nb}"
  f"  (log2(0.1/1e-10)={log2(0.1 / 1e-10):.2f})")
nw = st["newton"]
ex_ = st["exact"]
P("[[ex:iter]] Newton (double precision): " + "; ".join(f"n={r['n']} f={r['f']:.9f} err={r['err']:.1e} g1={r['g1']:.3e} g2={r['g2']:.4e}" for r in nw[:5]))
P("  Newton errors printed (50 digits): " + "; ".join(f"n={r['n']} err={r['err']:.1e}" for r in ex_["newton"]))
en = [r["err"] for r in ex_["newton"]]                  # the unrounded (50-digit) errors behind the printed ones
P(f"  ratios e(n+1)/e(n)^2 from the unrounded errors (printed): {en[2] / en[1]**2:.3f}, {en[3] / en[2]**2:.3f}"
  f"  (from the printed 2.3e-1, 2.4e-3, 2.5e-7 they would be {2.4e-3 / 2.3e-1**2:.3f}, {2.5e-7 / 2.4e-3**2:.3f})"
  f"  C=|g'''/(2g'')|={k['newton_C']:.3f}  f* (50 digits)={ex_['f'][:14]}")
br = st["bracket"]
bs = st["bisection"]
P(f"[[ex:iter]] bisection on [{br['lo']}, {br['hi']}] (g'(lo)={br['g1_lo']:.2e} > 0, g'(hi)={br['g1_hi']:.2e} < 0), double precision: "
  + "; ".join(f"n={r['n']} w={r['width']:.4g} err={r['mid_err']:.1e}" for r in bs if r["n"] in (0, 1, 2, 3, 4, 10, 20, 30, 44))
  + f";  steps to width < 1e-12: {st['bisection_steps_1e-12']}")
P("  printed (50 digits, exact returns): " + "; ".join(f"n={r['n']} w={r['width']:.4g} err={r['mid_err']:.1e}"
                                                        for r in ex_["bisection"] if r["n"] in (0, 1, 2, 3, 4, 10, 20, 30, 44))
  + f";  step 44: {ex_['bisection'][44]['mid_err']:.2e} exact, {bs[44]['mid_err']:.2e} in double precision")
P(f"KC: steps for [0,10%] to 1e-6: {log2(0.10 / 1e-6):.2f} -> {int(np.ceil(log2(0.10 / 1e-6)))}")
# pitfall: two IRRs and a flat tangent
cf2 = [-100, 230, -132]
npv2 = lambda y: sum(x / (1 + y) ** t for t, x in enumerate(cf2))
dnpv2 = lambda y: sum(-t * x / (1 + y) ** (t + 1) for t, x in enumerate(cf2))
for y0 in (0.14, 0.15):
    y = y0; path = [y]
    for it in range(12):
        y = y - npv2(y) / dnpv2(y); path.append(y)
    P(f"Pitfall two IRRs from {y0:.0%}: " + " -> ".join(f"{x:.2%}" for x in path[:4]) + f" ... {path[-1]:.4%}")
P(f"  roots: NPV(10%)={npv2(0.10):.1e} NPV(20%)={npv2(0.20):.1e}  flat at y={264/230-1:.2%}")
# Newton on 0050's Kelly condition from other starts (robustness remark)
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
P(f"[[eg:half]]: g={lv['half']['g_ann']:.2%} vs {lv['full']['g_ann']:.2%} share={lv['half']['g_ann']/lv['full']['g_ann']:.3f}"
  f" vol {lv['half']['vol_ann']:.1%} vs {lv['full']['vol_ann']:.1%}  mdd {lv['half']['mdd']:.1%} vs {lv['full']['mdd']:.1%}"
  f" worst {lv['half']['worst']:.1%} vs {lv['full']['worst']:.1%} wealth {lv['half']['wealth']:.0f} vs {lv['full']['wealth']:.0f}")
ft = st["flat_top_half"]
P(f"  flat top: 0.5|g''| per unit^2={ft['per_unit']:.4f}/yr  predicted loss={ft['pred_loss']:.1%} actual={ft['actual_loss']:.1%}")
P("[[ex:share]] fractions c: " + ", ".join(f"{kk}:{v:.1%} (quad {1-(1-float(kk))**2:.2%})" for kk, v in st["fractions"].items()))
cs = np.round(np.arange(0, 1.2501, 0.01), 2)
fB = 25.0; gB = g_star(0.5, 0.02, 0.01)
devB = max(abs(g_bin(c * fB, 0.5, 0.02, 0.01) / gB - (1 - (1 - c) ** 2)) for c in cs)
P(f"  bet share: half {g_bin(12.5,0.5,0.02,0.01)/gB:.3f} 1.5x {g_bin(37.5,0.5,0.02,0.01)/gB:.3f} quarter {g_bin(6.25,0.5,0.02,0.01)/gB:.3f};"
  f" max dev from parabola on [0,1.25]: {devB:.4f};  0050 curve ends at c=10/f*={10/k['f']:.4f} (printed f*: {10/5.42:.4f})")
fi = st["financing"]
P(f"[[eg:financing]]: dV/dr_f={fi['dVdr']:.2f}  r_f={fi['r_ann']:.0%}/yr as {fi['r_day']:.4%} per trading day (= 2%/{A:.2f}): first-order {fi['first_order']:.2%}"
  f"  exact {fi['dV']:.2%}  f*(r_f)={fi['f_r']:.2f}  V(r_f)={fi['Vr']:.2%}  at old f*={fi['g_at_old_f']:.2%}"
  f"  gain from re-optimizing={fi['Vr']-fi['g_at_old_f']:.2%}  mean 1/(1+f*R)={k['mean_inv']:.12f}")
se = st["se"]
P(f"[[eg:band]]: se={se['se_mu']:.4%} t={se['t']:.2f} rel={se['rel']:.1%} CI=[{se['lo_mu']:.3%},{se['hi_mu']:.3%}]"
  f"  exact band f=[{se['f_lo']:.2f},{se['f_hi']:.2f}]  (rule mu/s2: [{se['f_lo_rule']:.2f},{se['f_hi_rule']:.2f}])")
P(f"  printed inputs: se=1.2385%/sqrt(2902)={S_PRINTED / sqrt(2902):.4%}  rel={0.000230 / 0.000871:.3f}  CI=[{0.0871 - 1.96 * 0.0230:.4f}%,"
  f" {0.0871 + 1.96 * 0.0230:.4f}%]  rule at the printed ends: {0.00042 / S_PRINTED**2:.3f}, {0.00132 / S_PRINTED**2:.3f}")
P(f"  lower end: c={se['c_if_lo']:.4f} (5.42/2.7={5.42 / 2.7:.3f}) quad share={se['share_if_lo_quad']:.2%}"
  f" (at c=2.007: {1 - (1 - 5.42 / 2.7) ** 2:.2%}: almost nothing either way)  5.42 on the shifted sample earns {se['g_fstar_if_lo']:.2%}/yr")
P(f"  upper end: c={se['c_if_hi']:.2f} (5.42/7.6={5.42 / 7.6:.3f}) quad share={se['share_if_hi_quad']:.1%}"
  f" (printed c=0.71: {1 - 0.29**2:.1%})  exact share on the shifted sample {se['share_if_hi_exact']:.1%}")
ro = st["rolling"]
P(f"[[ex:rolling]] first window end {ro['first_end']}; ratio max/min={ro['max']/ro['min']:.1f}")
P(f"  3y: min {ro['min']:.2f} ({ro['min_end']}) max {ro['max']:.2f} ({ro['max_end']}) last {ro['last']:.2f} median {ro['median']:.2f}")
sh = st["sharpe"]
P(f"Sharpe view: SR={sh['sr_ann']:.2f} SR/sigma={sh['f_sr_over_sigma']:.2f} SR^2/2={sh['g_sr2_half']:.1%}")
# pitfall: Sharpe 3 backtest
SRb, sig = 3.0, 0.15
fb = SRb / sig
for SRt in (1.5, 1.0):
    c = SRb / SRt; gt = SRt**2 / 2
    P(f"Pitfall SR3: f={fb:.0f}  true SR={SRt}: f*_true={SRt/sig:.2f} c={c:.1f} share={2*c-c**2:.0f} g={(2*c-c**2)*gt:+.2f}/yr wealth factor/yr={exp((2*c-c**2)*gt):.3f}")
P(f"  backtest g*=SR^2/2={SRb**2/2:.2f}/yr -> x{exp(SRb**2/2):.0f} a year")
# KC
P(f"KC: quad share at 1.5 = {1-0.5**2:.2f}; 0050 exact = {st['fractions']['1.5']:.3f}; vol ratio 1.5/0.5 = 3")

# ---------------------------------------------------------------- Practice problems (numbered as in the module)
P("== Practice problems")
P(f"PP1 x e^-x: max at 1, value {exp(-1):.4f}")
P(f"PP3 g=0.12f-0.08f^2: f*={0.12/0.16:.2f} g*={0.12**2/(4*0.08):.4f} half={0.12*0.375-0.08*0.375**2:.5f} share={(0.12*0.375-0.08*0.375**2)/(0.12**2/0.32):.2f} zero={0.12/0.08:.2f}")
P(f"PP4 +5/-5 p=.55: f*={f_bin(0.55,0.05,0.05):.2f} risk={f_bin(0.55,0.05,0.05)*0.05:.0%} p-qa/b={0.55-0.45:.2f}")
f6 = f_bin(0.30, 0.08, 0.02); f6b = f_bin(0.25, 0.08, 0.02)
P(f"PP6 p=.30 b=8% a=2%: f*={f6:.3f} risk={f6*0.02:.2%} p-qa/b={0.30-0.70*0.02/0.08:.4f} g*={g_star(0.30,0.08,0.02):.4%}  pi={0.02/0.10:.2f}"
  f"  p=.25: f*={f6b:.4f} ratio={f6/f6b:.3f} g(f6;.25)={g_bin(f6,0.25,0.08,0.02):.4%} g*(.25)={g_star(0.25,0.08,0.02):.4%}"
  f"  1+f*b={1+f6*0.08:.3f} 1-f*a={1-f6*0.02:.4f}")
z6 = zero_growth(0.25, 0.08, 0.02)
P(f"  (b) share kept={g_bin(f6, 0.25, 0.08, 0.02) / g_star(0.25, 0.08, 0.02):.4f} (printed 0.122/0.738={0.122 / 0.738:.4f})"
  f"  exact zero growth at {z6:.4f} = {z6 / f6b:.4f} x Kelly (printed 6.56/3.125={6.56 / 3.125:.3f})")
# Why the zero lies beyond 2f*: with x := (f - f*) ab/(a+b), g(f) - g* = p ln(1 + x/p) + q ln(1 - x/q), whose odd part is
# positive for x > 0 exactly when p < q. A rare large gain (p < 1/2) makes growth fall more slowly beyond f* than it rises
# below it, so g(2f*) > g(0) = 0; at p = 1/2 the curve is symmetric about f*, whatever the sign of pb^3 - qa^3.
ds = np.linspace(0.01, 1.0, 100)                                 # distances d * f* from the optimum, up to f* itself
asym = [g_bin(f6b * (1 + d), 0.25, 0.08, 0.02) - g_bin(f6b * (1 - d), 0.25, 0.08, 0.02) for d in ds]
asym_half = [g_bin(25 * (1 + d), 0.5, 0.02, 0.01) - g_bin(25 * (1 - d), 0.5, 0.02, 0.01) for d in ds]
assert min(asym) > 0 and max(map(abs, asym_half)) < 1e-15
P(f"  why: g(f*+d)-g(f*-d) for 0<d<=f* at p=0.25: min {min(asym):.2e} > 0, and g(2f*)={g_bin(2 * f6b, 0.25, 0.08, 0.02):.4%};"
  f"  payoff skewness (q-p)/sqrt(pq)={(0.75 - 0.25) / sqrt(0.25 * 0.75):.3f}")
P(f"  p=0.5 (+2/-1 bet): max |g(f*+d)-g(f*-d)|={max(map(abs, asym_half)):.1e} (symmetric), g(50)={g_bin(50, 0.5, 0.02, 0.01):.1e},"
  f" although pb^3-qa^3={0.5 * 0.02**3 - 0.5 * 0.01**3:.2e} > 0")
P(f"PP7 bisection [0,1] to 1e-8: log2={log2(1e8):.2f} -> {int(np.ceil(log2(1e8)))};  distractors: decimal digits 8, natural log {log(1e8):.1f} -> {int(np.ceil(log(1e8)))}")
g10 = lambda f: 0.10 * f - 0.05 * f**2
P(f"PP8 g=0.10f-0.05f^2 cap 0.8: f*={0.10/0.10:.1f} g(0.8)={g10(0.8):.3f} g*={g10(1.0):.3f} g'(0.8)={0.10-0.10*0.8:.3f}"
  f"  cap 0.9: exact gain {g10(0.9)-g10(0.8):.4f} vs first-order {0.02*0.1:.4f};  whole gain to the optimum {g10(1.0)-g10(0.8):.4f}")
P(f"PP10 half Kelly quad: share {1-0.25:.2f}, vol 0.50")
SRb, sig = 2.4, 0.12
for SRt in (1.2, 0.8):
    c = SRb / SRt; gt = SRt**2 / 2
    P(f"PP11 SR {SRb} sigma {sig}: f={SRb/sig:.0f} true SR {SRt}: f*_true={SRt/sig:.2f} c={c:.0f} share={2*c-c**2:.0f} g={(2*c-c**2)*gt:+.2f}/yr factor={exp((2*c-c**2)*gt):.3f}")
h20 = st["halves"]["2020_2026"]
P(f"PP12 2020-2026: n={h20['n']} f*={h20['f']:.2f} mu/s2={h20['f_quad']:.2f}  rule too high by {h20['f_quad'] / h20['f'] - 1:.1%}"
  f" (full sample: {mo['mu_over_s2'] / k['f'] - 1:.1%}; printed 5.66/5.38={5.66 / 5.38 - 1:.1%}, 5.68/5.42={5.68 / 5.42 - 1:.1%})")
p, b, a = 0.5, 0.02, 0.01
mub = p * b - (1 - p) * a
s2b = p * b * b + (1 - p) * a * a - mub**2
P(f"PP13 quadratic expansion of binary g: (pb-qa)/(pb^2+qa^2)={(p*b-(1-p)*a)/(p*b**2+(1-p)*a**2):.1f}"
  f"  pb^3-qa^3={p*b**3-(1-p)*a**3:.2e} = mu^3+3 mu sigma^2={mub**3+3*mub*s2b:.2e} (mu={mub:.2%}, sigma={s2b**0.5:.2%};"
  f" central third moment {p*(b-mub)**3+(1-p)*(-a-mub)**3:.1e})")
p, b, a = 0.9, 0.01, 0.05                         # a positive mean with a negative cubic term: +1% at 0.9 against -5%
P(f"  counterexample +1%/-5% at p=0.9: pb-qa={p * b - (1 - p) * a:+.2%}  pb^3-qa^3={p * b**3 - (1 - p) * a**3:.3e}"
  f"  rule (pb-qa)/(pb^2+qa^2)={(p * b - (1 - p) * a) / (p * b**2 + (1 - p) * a**2):.2f}  exact f*={f_bin(p, b, a):.2f}")
