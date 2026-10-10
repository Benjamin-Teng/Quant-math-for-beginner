"""Numbers for LM7's illustrative examples, knowledge checks and practice problems.

Run after lm07_stats.py:  python3 data/lm07_numbers.py
Data-based numbers come from processed/lm07_stats.json; everything else is computed here from the
illustrative inputs stated in the module.
"""
import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
st = json.loads((HERE / "processed" / "lm07_stats.json").read_text(encoding="utf-8"))
P = print


def two_asset(s1, s2, rho, e1=None, e2=None, rf=None):
    c = rho * s1 * s2
    den = s1**2 + s2**2 - 2 * c
    w = (s2**2 - c) / den
    vmin = (s1**2 * s2**2 - c * c) / den
    out = dict(cov=c, w=w, vmin=vmin, smin=math.sqrt(vmin), lam=2 * vmin, den=den)
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

# ---------------------------------------------------------------- KC numbers
P("KC2: d/dw1 of V for w=(0.5,0.5) with s1=0.2,s2=0.1,rho=0", 2 * 0.5 * 0.04, 2 * 0.5 * 0.01)
# KC (Taylor): V exact for quadratic; KC for gradient direction
g = np.array([0.2275, -0.0255]); P("KC3 steepest ascent unit vector", g / np.linalg.norm(g))
# KC Lagrange: lambda meaning
P("KC5: split with kd=2,kn=5,Q=100 -> lam", lam, "marginal cost day=", 2 * kd * x, "night=", 2 * kn * y)

# ---------------------------------------------------------------- Practice problems
P("PP1: f=x^2 y+3xy^2 at (1,2): fxy=2x+6y=", 2 * 1 + 6 * 2, "fxx=2y=", 2 * 2, "fyy=6x=", 6 * 1)
xq, yq = -0.05, 0.03
P(f"PP2: exact={(1+xq)*(1+yq)-1:.4%} linear={xq+yq:.4%} cross={xq*yq:.4%} at fx=4%: exact={(1+xq)*1.04-1:.4%} via partial={(1+xq)*(1+yq)-1+(1+xq)*0.01:.4%}")
w = np.array([0.5, 0.5]); S = np.array([[0.04, 0.004], [0.004, 0.01]])
P("PP3: grad=", 2 * S @ w, "half=", S @ w)
xa, ya = 0.20, -0.10
T2 = 0.5 * (xa + ya) - (xa - ya) ** 2 / 8
ex = math.sqrt((1 + xa) * (1 + ya)) - 1
P(f"PP4: T2={T2:.6f} exact={ex:.6f} err={ex-T2:.6f} drag term={(xa-ya)**2/8:.6f} s={abs(xa-ya)/2:.4f} s^2/2={(abs(xa-ya)/2)**2/2:.6f}")
P("PP5: D=2*2-4^2=", 2 * 2 - 16)
for (a, b) in ((1, 2), (-1, -2), (1, -2), (-1, 2)):
    P(f"PP6 ({a},{b}): f={a**3+b**3-3*a-12*b+20} fxx={6*a} fyy={6*b} D={36*a*b}")
t7 = two_asset(0.30, 0.10, 0.0)
P(f"PP7: w1={t7['w']:.4f} vmin={t7['vmin']:.6f} smin={t7['smin']:.4%} lam={t7['lam']:.4f}")
P(f"PP8: lam*db={0.02*0.05:.4f} exact={(1.05**2-1)*0.01:.6f}")
t9 = two_asset(0.25, 0.15, 0.3)
v50 = 0.25 * 0.25**2 + 0.25 * 0.15**2 + 0.5 * t9["cov"]
P(f"PP9: cov={t9['cov']:.5f} den={t9['den']:.4f} w*={t9['w']:.4f} vmin={t9['vmin']:.6f} smin={t9['smin']:.4%} v50={v50:.6f} s50={math.sqrt(v50):.4%}")
P("PP10: threshold rho=", 0.15 / 0.30)
t11 = two_asset(0.20, 0.08, 0.25, 0.06, 0.02, rf=0.02)
P(f"PP11/12: cov={t11['cov']:.4f} num1={t11['num1']:.6f} num2={t11['num2']:.6f} wT=({t11['wT1']:.4f},{t11['wT2']:.4f}) SR1={t11['sr1']:.4f} "
  f"SR2={t11['sr2']:.4f} SR*={t11['sr']:.4f} det={t11['det']:.6f} f=({t11['f1']:.4f},{t11['f2']:.4f}) lev={t11['lev']:.4f} g*={t11['g']:.4%} SR*^2={t11['sr']**2:.5f}")
t13 = two_asset(0.20, 0.40, 0.95)
dV1 = 2 * 1 * 0.04 - 0 + 2 * (1 - 2) * t13["cov"]
P(f"PP13: cov={t13['cov']:.4f} den={t13['den']:.4f} w*={t13['w']:.4f} vmin={t13['vmin']:.6f} smin={t13['smin']:.4%} V'(1)={dV1:.4f} mu={-dV1:.4f}")
V13 = lambda w: w * w * 0.04 + (1 - w) ** 2 * 0.16 + 2 * w * (1 - w) * t13["cov"]
P(f"   V(1)={V13(1):.6f} V(1.01)={V13(1.01):.6f} diff={V13(1.01)-V13(1):.6f} pred={dV1*0.01:.6f}")
# PP14: Kelly with cap
e1_, e2_, s1_, s2_ = 0.10, 0.04, 0.20, 0.10
fu = (e1_ / s1_**2, e2_ / s2_**2)
f1c = (e1_ - e2_ + s2_**2 * 2) / (s1_**2 + s2_**2); f2c = 2 - f1c
lamc = e1_ - s1_**2 * f1c
gq = lambda a, b: a * e1_ + b * e2_ - 0.5 * (a * a * s1_**2 + b * b * s2_**2)
P(f"PP14: unconstrained f=({fu[0]:.4f},{fu[1]:.4f}) lev={sum(fu):.4f} g_excess={gq(*fu):.4%}; capped f=({f1c:.4f},{f2c:.4f}) "
  f"lam={lamc:.4f} check={e2_-s2_**2*f2c:.4f} g_excess={gq(f1c,f2c):.4%}; at cap 2.1 g_excess={gq((e1_-e2_+s2_**2*2.1)/(s1_**2+s2_**2), 2.1-(e1_-e2_+s2_**2*2.1)/(s1_**2+s2_**2)):.4%}")
# PP16 walk-forward is computed in lm07_stats-like fashion below (needs data)
import polars as pl
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
    P(f"PP16 {r[0]}: w_prev={r[1]:.4f} vol={r[2]:.4%} vol50={r[3]:.4%} best={r[4]:.4%} beats50={r[5]}")
P("PP16 count beats 50/50:", sum(r[5] for r in rows), "of", len(rows), "| mean vol prev-w", f"{np.mean([r[2] for r in rows]):.4%}",
  "mean vol 50/50", f"{np.mean([r[3] for r in rows]):.4%}", "mean best", f"{np.mean([r[4] for r in rows]):.4%}")

# ---------------------------------------------------------------- KKT examples (full sample): floor and cap, plus exact-growth checks
fl = st["floor"]["full_60"]
P(f"EG floor: w=0.6 nu={fl['mu']:.4f} (V1={st['marginal']['dV1']:.4f} V2={st['marginal']['dV2']:.4f}) vol={fl['vol']:.4%} "
  f"unconstrained={fl['vol_unc']:.4%} cost={(fl['vol']-fl['vol_unc'])*100:.2f}pp relaxed59={fl['vol_relaxed']:.4%} "
  f"dvar_pred={fl['dvar_pred']:.6f} dvar_exact={fl['dvar_exact']:.6f}")
cap = {c["case"]: c for c in st["kkt_cap"]["full_cap2"]}
c = cap["cap+f2=0"]
e1f, e2f, S11, S22, S12 = F["e1"], F["e2"], F["s1"] ** 2, F["s2"] ** 2, F["cov"]
g1 = e1f - S11 * 2; g2 = e2f - S12 * 2
gq = lambda a, b: 0.015 + a * e1f + b * e2f - 0.5 * (a * a * S11 + 2 * a * b * S12 + b * b * S22)
P(f"EG cap: nu_cap={c['mult']['lam']:.4f} nu2={c['mult']['mu2']:.4f} g1={g1:.4f} g2={g2:.4f} 2*S11={2*S11:.5f} 2*S12={2*S12:.6f} "
  f"model g(2,0)={gq(2,0):.4%} g(2.1,0)-g(2,0)={(gq(2.1,0)-gq(2,0))*100:.3f}pp linear={0.1*c['mult']['lam']*100:.3f}pp")
from scipy.optimize import minimize
from datetime import date
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
P("NEWTON path:", [(r_["k"], round(r_["f1"], 4), round(r_["f2"], 4), f"{r_['gap']:.1e}") for r_ in st["numopt"]["newton"][:5]])

# ---------------------------------------------------------------- intermediate values quoted in examples, knowledge checks and solutions
n1 = S22 * e1f - S12 * e2f; n2 = S11 * e2f - S12 * e1f; det_f = S11 * S22 - S12**2
P(f"EG kelly numerators: {n1:.6f} {n2:.6f} det={det_f:.4e} -> f=({n1/det_f:.4f},{n2/det_f:.4f})")
P(f"EG budget ratio f2/f1 = {t['num2']/t['num1']:.4f}")
P(f"KC3 rate along (1,-1)/sqrt2 = {(0.2275+0.0255)/math.sqrt(2):.4f}; |grad| = {math.hypot(0.2275, 0.0255):.4f}")
P(f"KC5 (k_n=3): x={100*3/5:.0f} y={100*2/5:.0f} lam={2*2*60:.0f} C(101)-C(100)={1.2*(101**2-100**2):.1f}")
P(f"KC7: cov={0.6*0.30*0.15:.4f} nu=V'(0)={2*(0.6*0.30*0.15-0.15**2):.4f} 1%-short variance cut={0.01*2*(0.6*0.30*0.15-0.15**2):.5f}")
P(f"PP11 intermediates: s2^2 e1={0.08**2*0.06:.6f} s12 e2={0.004*0.02:.6f} s1^2 e2={0.04*0.02:.6f} s12 e1={0.004*0.06:.6f} "
  f"sum of numerators={t11['num1']+t11['num2']:.6f}; SR formula pieces 0.09+0.0625-2*0.25*0.3*0.25={0.09+0.0625-2*0.25*0.3*0.25:.4f} / {1-0.25**2:.4f}")
P(f"PP15: SE mean ten years = {0.16/math.sqrt(10):.4f}; Kelly error = {0.16/math.sqrt(10)/0.16**2:.2f}; five years SE = {0.16/math.sqrt(5):.4f}")
P(f"Split: equal split premium = {17500/C-1:.4%}")
