"""Numbers for LM7's illustrative examples, knowledge checks and practice problems.

Run after lm07_stats.py:  uv run python data/lm07_numbers.py
Data-based numbers come from processed/lm07_stats.json; everything else is computed here from the
illustrative inputs stated in the module.
"""
import json
import math
from pathlib import Path

import numpy as np
import polars as pl
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
st = json.loads((HERE / "processed" / "lm07_stats.json").read_text(encoding="utf-8"))
P = print


def two_asset(s1, s2, rho, e1=None, e2=None, rf=None):
    c = rho * s1 * s2
    den = s1**2 + s2**2 - 2 * c
    w = (s2**2 - c) / den
    vmin = (s1**2 * s2**2 - c * c) / den
    out = {"cov": c, "w": w, "vmin": vmin, "smin": math.sqrt(vmin), "lam": 2 * vmin, "den": den}
    if e1 is not None:
        det = s1**2 * s2**2 - c * c
        f1, f2 = (s2**2 * e1 - c * e2) / det, (s1**2 * e2 - c * e1) / det
        sr1, sr2 = e1 / s1, e2 / s2
        sr = math.sqrt((sr1**2 + sr2**2 - 2 * rho * sr1 * sr2) / (1 - rho**2))
        out.update(det=det, f1=f1, f2=f2, lev=f1 + f2, wT1=f1 / (f1 + f2), wT2=f2 / (f1 + f2), sr1=sr1, sr2=sr2, sr=sr,
                   num1=s2**2 * e1 - c * e2, num2=s1**2 * e2 - c * e1)
        if rf is not None:
            out["g"] = rf + 0.5 * sr**2
    return out


# ---------------------------------------------------------------- Example: TWD return of a USD bond (2022)
fx = st["fx2022"]
P(f"EG fx: R_twd={fx['R_twd']:.4%} fx={fx['fx']:.4%} x_usd={fx['x_usd']:.4%} linear={fx['linear']:.4%} cross={fx['cross']:.4%} "
  f"f_x={fx['bond_partial']:.4f} f_y={fx['fx_partial']:.4f} 0050_2022={fx['r0050']:.4%}")

# ---------------------------------------------------------------- Example: order split with quadratic impact (illustrative)
kd, kn, Q = 2.0, 5.0, 100
x = Q * kn / (kd + kn); y = Q - x
lam = 2 * kd * x
C = kd * x**2 + kn * y**2
Cq = lambda q: kd * kn / (kd + kn) * q * q
P(f"EG split: x={x:.4f} y={y:.4f} lam={lam:.4f} (check 2kn*y={2*kn*y:.4f}) C*={C:.4f} lamQ/2={lam*Q/2:.4f} "
  f"C(101)-C(100)={Cq(101)-Cq(100):.4f} second-order={kd*kn/(kd+kn):.4f} C(71,29)={kd*71**2+kn*29**2:.1f} C(72,28)={kd*72**2+kn*28**2:.1f} "
  f"equal split C(50,50)={kd*50**2+kn*50**2:.1f} avg cost/lot={C/Q:.3f} marginal/avg={lam/(C/Q):.3f}")

# ---------------------------------------------------------------- Example: risk budget for two strategies (illustrative)
e1, s1, e2, s2, rho, sT = 0.08, 0.16, 0.03, 0.04, 0.2, 0.10
t = two_asset(s1, s2, rho, e1, e2)
z1, z2 = t["num1"] / t["det"], t["num2"] / t["det"]          # Sigma^{-1} e
k = sT / t["sr"]
f1, f2 = k * z1, k * z2
var = f1**2 * s1**2 + 2 * f1 * f2 * t["cov"] + f2**2 * s2**2
lam_var = t["sr"] / (2 * sT)
P(f"EG budget: SR1={t['sr1']:.4f} SR2={t['sr2']:.4f} SR*={t['sr']:.4f} Sinv_e=({z1:.4f},{z2:.4f}) f=({f1:.4f},{f2:.4f}) "
  f"vol={math.sqrt(var):.4%} excess={f1*e1+f2*e2:.4%} lam_var={lam_var:.4f} lam_sigma={t['sr']:.4f} "
  f"excess at 11%={0.11*t['sr']:.4%} (gain {(0.11-0.10)*t['sr']:.4%}) det={t['det']:.6e} cov={t['cov']:.5f}")
# alternative: each strategy alone scaled to 10% vol
P(f"   alone at 10% vol: strategy1 excess={0.10*t['sr1']:.2%}, strategy2 excess={0.10*t['sr2']:.2%}")
# the variance budget is an ellipse: the Lagrange conditions give +f (lambda > 0, the maximum) and -f (lambda < 0, the minimum)
for sgn in (1, -1):
    fs = (sgn * f1, sgn * f2)
    lam_s = (fs[0] * e1 + fs[1] * e2) / (2 * sT**2)          # f'e = 2 lambda f' Sigma f = 2 lambda sT^2
    chk = [e1 - 2 * lam_s * (s1**2 * fs[0] + t["cov"] * fs[1]), e2 - 2 * lam_s * (t["cov"] * fs[0] + s2**2 * fs[1])]
    P(f"   candidate {sgn:+d}: f=({fs[0]:.4f},{fs[1]:.4f}) excess={fs[0]*e1+fs[1]*e2:+.4%} lambda={lam_s:+.4f} stationarity residual={max(map(abs, chk)):.1e}")

# ---------------------------------------------------------------- Example: classify critical points of x^3 - 3xy + y^3
for (a, b) in ((0, 0), (1, 1)):
    fxx, fyy, fxy = 6 * a, 6 * b, -3
    P(f"EG classify ({a},{b}): f={a**3-3*a*b+b**3} fxx={fxx} fyy={fyy} fxy={fxy} D={fxx*fyy-fxy**2}")

# ---------------------------------------------------------------- data examples echoed for convenience
F, IS, OOS = st["full"], st["is"], st["oos"]
P(f"EG minvar IS: s1={IS['s1']:.4%} s2={IS['s2']:.4%} rho={IS['rho']:.4f} cov={IS['cov']:.6f} w*={IS['w_mv']:.4%} "
  f"smin={IS['s_mv']:.4%} lam={IS['lam']:.5f} num={IS['s2']**2-IS['cov']:.6f} den={IS['s1']**2+IS['s2']**2-2*IS['cov']:.6f}")
P(f"   variance check: s1^2={IS['s1']**2:.6f} s2^2={IS['s2']**2:.6f} vmin={IS['s_mv']**2:.6f}")
den_oos = OOS["s1"] ** 2 + OOS["s2"] ** 2 - 2 * OOS["cov"]
gap = st["case"]["w_is"] - OOS["w_mv"]
P(f"FLAT BOTTOM: den_oos={den_oos:.6f} dw={gap:.4f} penalty={den_oos*gap**2*1e4:.2f}%^2 vmin_oos={OOS['s_mv']**2*1e4:.2f}%^2 "
  f"realized={st['case']['realized']**2*1e4:.2f}%^2 sum={(OOS['s_mv']**2+den_oos*gap**2)*1e4:.2f} vol={math.sqrt(OOS['s_mv']**2+den_oos*gap**2):.4%}")
for dw in (0.05, 0.10, 0.17):
    P(f"   weight error {dw:.2f}: vol {math.sqrt(OOS['s_mv']**2+den_oos*dw**2):.4%} (+{(math.sqrt(OOS['s_mv']**2+den_oos*dw**2)-OOS['s_mv'])*100:.2f} pp)")
at = st["attrib"]
P("ATTRIB precise (%^2):", {k: round(v * 1e4, 4) for k, v in at["first"].items()}, round(at["first_total"] * 1e4, 4),
  {k: round(v * 1e4, 4) for k, v in at["second"].items()}, round(at["second_total"] * 1e4, 4), round(at["third"] * 1e4, 4),
  "V0", round(at["V0"] * 1e4, 4), "V1", round(at["V1"] * 1e4, 4), "dV", round(at["dV"] * 1e4, 4))
P(f"   shares of dV: first-order {at['first_total']/at['dV']:.1%}, second {at['second_total']/at['dV']:.1%}; "
  f"s1 first {at['first']['s1']/at['dV']:.1%}, rho first {at['first']['rho']/at['dV']:.1%}")
oth = at["second"]["s2s2"] + at["second"]["s1s2"] + at["second"]["s2rho"]
P(f"   second-order grouped: s1s1={at['second']['s1s1']*1e4:.2f} s1rho={at['second']['s1rho']*1e4:.2f} other={oth*1e4:.2f}; "
  f"first+second={(at['first_total']+at['second_total'])*1e4:.2f}")

# Kelly example (full sample, r_f 1.5%)
P(f"EG kelly full: e1={F['e1']:.4%} e2={F['e2']:.4%} s1^2={F['s1']**2:.6f} s2^2={F['s2']**2:.6f} cov={F['cov']:.6f} "
  f"det={F['s1']**2*F['s2']**2-F['cov']**2:.4e} f=({F['f1']:.4f},{F['f2']:.4f}) lev={F['lev']:.4f} wT=({F['wT1']:.4f},{F['wT2']:.4f}) "
  f"SR1={F['sr1']:.4f} SR2={F['sr2']:.4f} SR*={F['sr_star']:.4f} g*={F['g_star']:.4%}")
ke = st["kelly_emp"]["full"]
P(f"   exact empirical optimum f=({ke['f1']:.4f},{ke['f2']:.4f}) g={ke['g']:.4%}; exact g at quadratic f*={ke['g_at_quad']:.4%}; worst day at f* {ke['worst_day_fstar']:.2%}")

# ---------------------------------------------------------------- knowledge checks (by section)
g = np.array([0.2275, -0.0255]); P("KC Section 3: steepest ascent unit vector", g / np.linalg.norm(g))
P("KC Section 5 (k_n=5 example): lam", lam, "marginal cost day=", 2 * kd * x, "night=", 2 * kn * y)

# ---------------------------------------------------------------- practice problems, numbered as in the module
P("PP1: h=x^2 y+3xy^2 at (1,2): hxy=2x+6y=", 2 * 1 + 6 * 2, "hxx=2y=", 2 * 2, "hx=2xy+3y^2=", 2 * 1 * 2 + 3 * 2**2)
xq, yq = -0.05, 0.03
P(f"PP2: exact={(1+xq)*(1+yq)-1:.4%} linear={xq+yq:.4%} cross={xq*yq:.4%} at fx=4%: exact={(1+xq)*1.04-1:.4%} via partial={(1+xq)*(1+yq)-1+(1+xq)*0.01:.4%}")
xa, ya = 0.20, -0.10
T2 = 0.5 * (xa + ya) - (xa - ya) ** 2 / 8
ex = math.sqrt((1 + xa) * (1 + ya)) - 1
P(f"PP3: T2={T2:.6f} exact={ex:.6f} err={ex-T2:.6f} drag term={(xa-ya)**2/8:.6f} s={abs(xa-ya)/2:.4f} s^2/2={(abs(xa-ya)/2)**2/2:.6f}")
for (a, b) in ((1, 2), (-1, -2), (1, -2), (-1, 2)):
    P(f"PP4 ({a},{b}): h={a**3+b**3-3*a-12*b+20} hxx={6*a} hyy={6*b} detH={36*a*b}")
# PP5: A is lambda* db; B reads lambda* as sigma_min^2 (2 sigma_min^2 db); C drops the 2 in lambda* = 2 sigma_min^2 (sigma_min^2 db)
P(f"PP5: A lam*db={0.02*0.05:.4f} exact={(1.05**2-1)*0.01:.6f}; distractors B={2*0.02*0.05:.4f} C={0.01*0.05:.4f}")
P("PP6: threshold rho=", 0.15 / 0.30)
t11 = two_asset(0.20, 0.08, 0.25, 0.06, 0.02, rf=0.02)
P(f"PP7/8: cov={t11['cov']:.4f} num1={t11['num1']:.6f} num2={t11['num2']:.6f} wT=({t11['wT1']:.4f},{t11['wT2']:.4f}) SR1={t11['sr1']:.4f} "
  f"SR2={t11['sr2']:.4f} SR*={t11['sr']:.4f} det={t11['det']:.6f} f=({t11['f1']:.4f},{t11['f2']:.4f}) lev={t11['lev']:.4f} g*={t11['g']:.4%} SR*^2={t11['sr']**2:.5f}")
P(f"   PP7 intermediates: s2^2 e1={0.08**2*0.06:.6f} s12 e2={0.004*0.02:.6f} s1^2 e2={0.04*0.02:.6f} s12 e1={0.004*0.06:.6f} "
  f"sum of numerators={t11['num1']+t11['num2']:.6f}; SR formula pieces 0.09+0.0625-2*0.25*0.3*0.25={0.09+0.0625-2*0.25*0.3*0.25:.4f} / {1-0.25**2:.4f}")
t9 = two_asset(0.20, 0.40, 0.95)
dV1 = 2 * 1 * 0.04 - 0 + 2 * (1 - 2) * t9["cov"]          # V'(1) = 2 s1^2 - 2 s12
P(f"PP9: cov={t9['cov']:.4f} den={t9['den']:.4f} w*={t9['w']:.4f} vmin={t9['vmin']:.6f} smin={t9['smin']:.4%} V'(1)={dV1:.4f} nu={-dV1:.4f}")
V9 = lambda w: w * w * 0.04 + (1 - w) ** 2 * 0.16 + 2 * w * (1 - w) * t9["cov"]
P(f"   V(1)={V9(1):.6f} V(1.01)={V9(1.01):.6f} diff={V9(1.01)-V9(1):.6f} pred={dV1*0.01:.6f}")
# PP10: Kelly with a net cap; the multiplier is a first-order value, so also re-solve at a cap of 3
e1_, e2_, s1_, s2_ = 0.10, 0.04, 0.20, 0.10
fu = (e1_ / s1_**2, e2_ / s2_**2)
gq10 = lambda a, b: a * e1_ + b * e2_ - 0.5 * (a * a * s1_**2 + b * b * s2_**2)


def capped10(capv):
    f1 = (e1_ - e2_ + s2_**2 * capv) / (s1_**2 + s2_**2)
    return f1, capv - f1


f1c, f2c = capped10(2.0)
f13, f23 = capped10(3.0)
assert min(f13, f23) > 0 and e1_ - s1_**2 * f13 > 0                     # cap still binds, sign constraints slack
P(f"PP10: unconstrained f=({fu[0]:.4f},{fu[1]:.4f}) lev={sum(fu):.4f} g_excess={gq10(*fu):.4%}; capped f=({f1c:.4f},{f2c:.4f}) "
  f"nu_c={e1_ - s1_**2 * f1c:.4f} check={e2_-s2_**2*f2c:.4f} g_excess={gq10(f1c,f2c):.4%}; cap 3: f=({f13:.4f},{f23:.4f}) "
  f"g_excess={gq10(f13,f23):.4%} gain={(gq10(f13,f23)-gq10(f1c,f2c))*100:.4f}pp")
P(f"PP11: SE mean ten years = {0.16/math.sqrt(10):.4f}; Kelly error = {0.16/math.sqrt(10)/0.16**2:.2f}")
# PP12 walk-forward: each year's minimum-variance weight held, rebalanced daily, through the following year
df = pl.read_parquet(HERE / "processed" / "lm07_returns.parquet").drop_nulls("R_0050")
R1, R2 = df["R_0050"].to_numpy(), df["R_00679B"].to_numpy()
yr = np.array([int(d[:4]) for d in df["date"].to_list()])
A = st["sample"]["A"]
rows = []
for y in range(2018, 2027):
    prev = yr == y - 1; cur = yr == y
    Sp = np.cov(np.vstack([R1[prev], R2[prev]]), ddof=0)
    w = (Sp[1, 1] - Sp[0, 1]) / (Sp[0, 0] + Sp[1, 1] - 2 * Sp[0, 1])
    vw = math.sqrt(A * (w * R1[cur] + (1 - w) * R2[cur]).var())
    v50_ = math.sqrt(A * (0.5 * R1[cur] + 0.5 * R2[cur]).var())
    Sc = np.cov(np.vstack([R1[cur], R2[cur]]), ddof=0)
    wc = (Sc[1, 1] - Sc[0, 1]) / (Sc[0, 0] + Sc[1, 1] - 2 * Sc[0, 1])
    vbest = math.sqrt(A * (wc * R1[cur] + (1 - wc) * R2[cur]).var())
    rows.append((y, w, vw, v50_, vbest, vw < v50_))
for r in rows:
    P(f"PP12 {r[0]}: w_prev={r[1]:.4f} vol={r[2]:.4%} vol50={r[3]:.4%} best={r[4]:.4%} beats50={r[5]}")
P("PP12 count beats 50/50:", sum(r[5] for r in rows), "of", len(rows), "| simple means: prev-w", f"{np.mean([r[2] for r in rows]):.4%}",
  "50/50", f"{np.mean([r[3] for r in rows]):.4%}", "ex-post", f"{np.mean([r[4] for r in rows]):.4%}")
r20 = next(r for r in rows if r[0] == 2020)
P(f"   2020: {r20[2]:.3%} against {r20[3]:.3%}, lost by {(r20[2]-r20[3])*100:.4f} points")

# ---------------------------------------------------------------- KKT examples (full sample): floor and cap, plus exact-growth checks
fl = st["floor"]["full_60"]
P(f"EG floor: w=0.6 nu={fl['mu']:.4f} (V1={st['marginal']['dV1']:.4f} V2={st['marginal']['dV2']:.4f}) vol={fl['vol']:.4%} "
  f"unconstrained={fl['vol_unc']:.4%} cost={(fl['vol']-fl['vol_unc'])*100:.2f}pp relaxed59={fl['vol_relaxed']:.4%} "
  f"dvar_pred={fl['dvar_pred']:.6f} dvar_exact={fl['dvar_exact']:.6f}")
cap = {c["case"]: c for c in st["kkt_cap"]["full_cap2"]}
c = cap["cap+f2"]
e1f, e2f, S11, S22, S12 = F["e1"], F["e2"], F["s1"] ** 2, F["s2"] ** 2, F["cov"]
g1 = e1f - S11 * 2; g2 = e2f - S12 * 2
gq = lambda a, b: 0.015 + a * e1f + b * e2f - 0.5 * (a * a * S11 + 2 * a * b * S12 + b * b * S22)
P(f"EG cap: nu_cap={c['mult']['nu_c']:.4f} nu2={c['mult']['nu_2']:.4f} g1={g1:.4f} g2={g2:.4f} 2*S11={2*S11:.5f} 2*S12={2*S12:.6f} "
  f"model g(2,0)={gq(2,0):.4%} g(2.1,0)-g(2,0)={(gq(2.1,0)-gq(2,0))*100:.3f}pp linear={0.1*c['mult']['nu_c']*100:.3f}pp")
ng = st["netgross"]
P(f"   shadow price vs exact: cap 2.1 -> optimum {np.round(ng['cap21_f'], 4).tolist()} gain {ng['cap21_gain']*100:.4f}pp; "
  f"cap 3 -> optimum {np.round(ng['cap3_f'], 4).tolist()} gain {ng['cap3_gain']*100:.4f}pp (first order: {c['mult']['nu_c']*100:.2f}pp a unit)")
P(f"   net cap, f2 >= -0.01: optimum {ng['f_rel']} gain {ng['gain_net']*100:.4f}pp (0.01 nu2 = {0.01*c['mult']['nu_2']*100:.4f}pp); "
  f"split: extra 0050 alone {ng['gain_0050_only']*100:+.4f}pp, short alone {ng['gain_short_only']*100:+.4f}pp "
  f"(sum {(ng['gain_0050_only']+ng['gain_short_only'])*100:.4f}); g_f2 at (2,0) = {ng['g_f2_at_20']:.4f}")
P(f"   gross cap: optimum {ng['f_gross_opt']}; (1.99,-0.01) changes growth by {ng['loss_gross']*100:+.4f}pp "
  f"(0050 cut alone {ng['loss_0050_cut']*100:+.4f}pp); cap-only candidate {np.round(ng['cap_only_f'], 4).tolist()} gross exposure {ng['cap_only_gross']:.4f}")
P("KKT table rows (binding set, f, multipliers, feasible, dual, growth):")
for row in st["kkt_cap"]["full_cap2"]:
    if row["consistent"]:
        P(f"   {row['case']:8s} ({row['f1']:.2f}, {row['f2']:.2f}) {', '.join(f'{k}={v:.3f}' for k, v in row['mult'].items())} "
          f"feasible={row['feasible']} dual={row['dual']} g={row['g']:.2%}")
    else:
        P(f"   {row['case']:8s} inconsistent")
X = np.vstack([R1, R2]).T - 0.015 / A
gex = lambda f: A * np.log1p(0.015 / A + X @ f).mean()


def kc(capv):
    res = minimize(lambda f: -gex(f), x0=[0.5, 0.5], method="SLSQP", bounds=[(0, None), (0, None)],
                   constraints=[{"type": "ineq", "fun": lambda f: capv - f.sum()}])
    return res.x, -res.fun


xx, gg = kc(2.0)
nu_ex = (kc(2.01)[1] - kc(1.99)[1]) / 0.02
P(f"   exact SLSQP cap 2: f={xx.round(4)} g={gg:.4%} nu_cap exact={nu_ex:.4f}; exact g(2.1,0)-g(2,0)={(gex(np.array([2.1,0]))-gex(np.array([2.0,0])))*100:.3f}pp")
# Newton path from 0 (exact growth) for the text
FL = st["numopt"]["floor"]       # shortfalls below the floor are rounding-level and never quoted
P("NEWTON path:", [(r_["k"], round(r_["f1"], 4), round(r_["f2"], 4), f"{r_['gap']:.1e}" if r_["gap"] >= FL else f"below {FL:.0e}")
                   for r_ in st["numopt"]["newton"][:5]])

# ---------------------------------------------------------------- intermediate values quoted in examples, knowledge checks and solutions
n1 = S22 * e1f - S12 * e2f; n2 = S11 * e2f - S12 * e1f; det_f = S11 * S22 - S12**2
P(f"EG kelly numerators (unrounded inputs): {n1:.7f} {n2:.7f} det={det_f:.4e} -> f=({n1/det_f:.4f},{n2/det_f:.4f})")
P(f"EG budget ratio f2/f1 = {t['num2']/t['num1']:.4f}")
P(f"KC Section 3: rate along (1,-1)/sqrt2 = {(0.2275+0.0255)/math.sqrt(2):.4f}; |grad| = {math.hypot(0.2275, 0.0255):.4f}")
P(f"KC Section 5 (k_n=3): x={100*3/5:.0f} y={100*2/5:.0f} lam={2*2*60:.0f} C(101)-C(100)={1.2*(101**2-100**2):.1f}")
P(f"Split: equal split premium = {17500/C-1:.4%}")


# ---------------------------------------------------------------- printed inputs reproduce printed outputs (round-2 checks)
# Each check recomputes a printed figure from the inputs printed next to it in src/lm07.md and asserts the printed text.
def chk(label, value, fmt, printed):
    got = format(value, fmt)
    P(f"CHECK {label}: {got} (printed {printed}) {'ok' if got == printed else 'MISMATCH'}")
    assert got == printed, (label, got, printed)


chk("A = 2,363 x 365.25 / 3,551", 2363 * 365.25 / 3551, ".4f", "243.0543")
assert abs(st["sample"]["A"] - 2363 * 365.25 / 3551) < 1e-9 and st["sample"]["n"] == 2363
# Example minvar (K6): printed sigma1^2 = 0.026800, sigma2^2 = 0.018353, sigma12 = -0.004908, sigma_d^2 = 0.054969
chk("minvar numerator", 0.018353 + 0.004908, ".6f", "0.023261")
chk("minvar w*", (0.018353 + 0.004908) / 0.054969, ".1%", "42.3%")
chk("minvar sigma_d^2", 0.026800 + 0.018353 + 2 * 0.004908, ".6f", "0.054969")
# Taylor attribution (A2): printed partials x printed changes; second-order terms from w1 = 42.317%
ap, at2 = st["attrib_partials"], st["attrib"]
chk("partial s1", ap["dV_ds1"], ".6f", "0.043994")
chk("partial s2", ap["dV_ds2"], ".6f", "0.072465")
chk("partial rho", ap["dV_drho"], ".6f", "0.010827")
chk("change s1", at2["d"]["s1"], "+.6f", "+0.070325")
chk("change s2", at2["d"]["s2"], "+.6f", "-0.001140")
chk("change rho", at2["d"]["rho"], "+.6f", "+0.199414")
c1, c2, c3 = 0.043994 * 0.070325 * 1e4, 0.072465 * -0.001140 * 1e4, 0.010827 * 0.199414 * 1e4
chk("first-order s1", c1, "+.2f", "+30.94")
chk("first-order s2", c2, "+.2f", "-0.83")
chk("first-order rho", c3, "+.2f", "+21.59")
chk("first-order total of printed parts", round(c1, 2) + round(c2, 2) + round(c3, 2), "+.2f", "+51.70")
w1p, w2p = 0.42317, 0.57683
chk("1/2 V_s1s1 ds1^2", w1p**2 * 0.070325**2 * 1e4, ".2f", "8.86")
chk("V_s1rho ds1 drho", 2 * w1p * w2p * 0.1355 * 0.070325 * 0.199414 * 1e4, ".2f", "9.28")
chk("third-order term", 2 * w1p * w2p * 0.070325 * -0.001140 * 0.199414 * 1e4, ".2f", "-0.08")
chk("w1 of the case (unrounded)", st["case"]["w_is"], ".3%", "42.317%")
# Flat bottom (A1): sigma_d^2 on the test window, curvature V'' = 2 sigma_d^2, penalty from printed inputs
fl_ = st["flat"]
chk("sigma_d^2 test window", fl_["D"], ".5f", "0.07419")
chk("curvature 2 sigma_d^2", 2 * fl_["D"], ".4f", "0.1484")
chk("penalty", 0.07419 * 0.17067**2 * 1e4, ".2f", "21.61")
# Example kellyeg (K3, A7): printed Sigma and e = (22.751%, -2.547%)
Sp11, Sp22, Sp12, ep1, ep2 = 0.040425, 0.018214, -0.002866, 0.22751, -0.02547
chk("mu1", F["mu1"], ".3%", "24.251%")
chk("mu2", F["mu2"], ".3%", "-1.047%")
chk("e1", F["e1"], ".3%", "22.751%")
chk("e2", F["e2"], ".3%", "-2.547%")
detp = Sp11 * Sp22 - Sp12**2
np1 = Sp22 * ep1 - Sp12 * ep2
np2 = Sp11 * ep2 - Sp12 * ep1
chk("det", detp * 1e4, ".3f", "7.281")
chk("numerator 1", np1, ".7f", "0.0040709")
chk("numerator 2", np2, ".7f", "-0.0003776")
chk("numerator sum", 0.0040709 - 0.0003776, ".7f", "0.0036933")
chk("f1*", 0.0040709 / 7.281e-4, ".2f", "5.59")
chk("f2*", -0.0003776 / 7.281e-4, ".2f", "-0.52")
chk("L*", 0.0036933 / 7.281e-4, ".2f", "5.07")
chk("w_tan 1", 0.0040709 / 0.0036933, ".1%", "110.2%")
chk("w_tan 2", -0.0003776 / 0.0036933, ".1%", "-10.2%")
sr1p, sr2p = ep1 / math.sqrt(Sp11), ep2 / math.sqrt(Sp22)
rhop = Sp12 / math.sqrt(Sp11 * Sp22)
srsp = math.sqrt((sr1p**2 + sr2p**2 - 2 * rhop * sr1p * sr2p) / (1 - rhop**2))
chk("SR1", sr1p, ".3f", "1.132")
chk("SR2", sr2p, ".3f", "-0.189")
chk("rho", rhop, ".3f", "-0.106")
chk("SR*", srsp, ".3f", "1.134")
chk("g* from printed SR*", 0.015 + 0.5 * 1.134**2, ".1%", "65.8%")
# Kelly exhibit (A7): tangency weights in whole percents follow from the printed f1* and L*
for lab_, f1_, L_, pr in (("2017-2021", 7.00, 10.14, "69%"), ("2022-2026", 5.17, 1.11, "466%"), ("2017-2026", 5.59, 5.07, "110%")):
    chk(f"w_tan {lab_} from printed f1*/L*", f1_ / L_, ".0%", pr)
for key_, pr in (("is", "69%"), ("oos", "466%"), ("full", "110%")):
    chk(f"w_tan {key_} unrounded", st[key_]["wT1"], ".0%", pr)
# KKT exhibit note (A9) and Section 8 (A11, A12)
chk("cap-only gross 4.585 + 2.585", 4.585 + 2.585, ".2f", "7.17")
chk("cap-only f1", ng["cap_only_f"][0], ".3f", "4.585")
chk("cap-only f2", ng["cap_only_f"][1], ".3f", "-2.585")
no = st["numopt"]
chk("m", no["eig"][0], ".5f", "0.01785")
chk("M", no["eig"][1], ".5f", "0.04079")
chk("kappa from printed m, M", 0.04079 / 0.01785, ".2f", "2.29")
chk("alpha from printed m, M", 2 / (0.01785 + 0.04079), ".1f", "34.1")
chk("factor from printed m, M", (0.04079 - 0.01785) / (0.04079 + 0.01785), ".2f", "0.39")
# Pitfall (A13): standard errors over the estimation window's calendar years
se = st["se_means"]
chk("years 2017-2021", se["years"], ".2f", "4.95")
chk("SE 0050", se["se1"] * 100, ".2f", "7.36")
chk("SE 00679B", se["se2"] * 100, ".2f", "6.09")
chk("SE 0050 from printed inputs", 16.37 / math.sqrt(4.95), ".2f", "7.36")
chk("ratio 7.36 / 18.7", 7.36 / 18.7, ".0%", "39%")
chk("mean 0050 2017-2021", se["mu1"], ".1%", "18.7%")
chk("mean 00679B 2017-2021", se["mu2"], ".1%", "3.8%")
# Example cap (K1, A14)
chk("gain net (2.01,-0.01)", ng["gain_net"] * 100, ".3f", "0.166")
chk("extra 0050 alone", ng["gain_0050_only"] * 100, ".4f", "0.1465")
chk("short alone", ng["gain_short_only"] * 100, ".4f", "0.0196")
chk("printed split sums to 0.166", 0.1465 + 0.0196, ".3f", "0.166")
chk("g_f2 at (2,0)", ng["g_f2_at_20"], ".4f", "-0.0197")
chk("g_f1 at (2,0) from printed inputs", 0.22751 - 2 * 0.040425, ".4f", "0.1467")
chk("2 sigma12 from printed sigma12", 2 * 0.002866, ".6f", "0.005732")
chk("g_f2 at (2,0) from printed inputs", -0.02547 + 0.005732, ".4f", "-0.0197")
chk("nu_2 from printed parts", 0.1467 + 0.0197, ".4f", "0.1664")
chk("gross (1.99,-0.01)", ng["loss_gross"] * 100, ".3f", "-0.127")
chk("cap 2.1 gain", ng["cap21_gain"] * 100, ".2f", "1.45")
chk("cap 3 gain", ng["cap3_gain"] * 100, ".2f", "12.64")
assert np.allclose(ng["cap3_f"], [3.0, 0.0])
chk("PP10 cap 3 gain", (gq10(f13, f23) - gq10(f1c, f2c)) * 100, ".2f", "3.20")
chk("PP12 2020 held weight", r20[2], ".3%", "14.253%")
chk("PP12 2020 50/50", r20[3], ".3%", "14.251%")
chk("PP12 2020 printed gap", 14.253 - 14.251, ".3f", "0.002")
