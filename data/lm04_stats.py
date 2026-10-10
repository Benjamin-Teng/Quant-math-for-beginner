"""LM4 statistics: empirical Kelly on 0050 daily total returns, 2014-10-31 -> 2026-10-08.

Computes every data-based number quoted in src/lm04.md and writes processed/lm04_stats.json.
Run after build_series.py:  python3 data/lm04_stats.py
"""
import json
from datetime import date
from pathlib import Path

import numpy as np
import polars as pl
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
df = pl.read_parquet(HERE / "processed" / "etf_daily_returns.parquet").with_columns(pl.col("date").str.to_date())
R = df["R_0050"].to_numpy()
RL = df["R_00631L"].to_numpy()
dates = df["date"].to_list()
T = len(R)
BASE = date(2014, 10, 31)                      # last close before the first return
YEARS = (dates[-1] - BASE).days / 365.25       # 11.937 calendar years
A = T / YEARS                                  # 243.1 trading days a year: annualization factor


# ---------------------------------------------------------------- empirical Kelly helpers
def domain(r):
    """Open interval of leverages with 1 + f R_t > 0 for every t."""
    return -1.0 / r.max(), 1.0 / (-r.min())


def gbar(f, r):
    """Average log growth per period, eq. (4.4)."""
    return float(np.log1p(f * r).mean())


def g1(f, r):
    """First derivative of gbar: the empirical Kelly condition, eq. (4.5)."""
    return float((r / (1 + f * r)).mean())


def g2(f, r):
    """Second derivative of gbar, eq. (4.6)."""
    return float(-((r / (1 + f * r)) ** 2).mean())


def g3(f, r):
    return float(2 * ((r / (1 + f * r)) ** 3).mean())


def kelly(r, xtol=1e-15):
    lo, hi = domain(r)
    eps = 1e-12
    return brentq(lambda f: g1(f, r), lo * (1 - eps), hi * (1 - eps), xtol=xtol, rtol=4 * np.finfo(float).eps)


def max_drawdown(f, r):
    w = np.concatenate([[1.0], np.cumprod(1 + f * r)])
    return float((w / np.maximum.accumulate(w) - 1).min())


res = {"T": T, "years": YEARS, "A": A, "first": str(dates[0]), "last": str(dates[-1])}

# ---------------------------------------------------------------- moments and quadratic approximation
mu, s2 = R.mean(), R.var()                      # population variance, as in (3.7)
m2, m3, m4 = (R**2).mean(), (R**3).mean(), (R**4).mean()
res["mom"] = dict(mu=mu, s=np.sqrt(s2), s2=s2, m2=m2, m3=m3, m4=m4,
                  skew=float(((R - mu) ** 3).mean() / s2**1.5), exkurt=float(((R - mu) ** 4).mean() / s2**2 - 3),
                  mu_over_s2=mu / s2, mu_over_m2=mu / m2, sr_daily=mu / np.sqrt(s2),
                  sr_annual=mu * A / (np.sqrt(s2) * np.sqrt(A)), mu_annual=mu * A, vol_annual=np.sqrt(s2 * A),
                  min=R.min(), max=R.max(), argmin=str(dates[int(R.argmin())]), argmax=str(dates[int(R.argmax())]))
lo, hi = domain(R)
res["domain"] = dict(lo=lo, hi=hi)

# ---------------------------------------------------------------- exact empirical Kelly
fs = kelly(R)
gs = gbar(fs, R)
res["kelly"] = dict(f=fs, g_day=gs, g_ann=gs * A, g2_day=g2(fs, R), g2_ann=g2(fs, R) * A, g3_day=g3(fs, R),
                    newton_C=abs(g3(fs, R) / (2 * g2(fs, R))),
                    mean_inv=float((1 / (1 + fs * R)).mean()),           # = 1 exactly at the optimum (Section 7)
                    arith_ann=fs * mu * A, drag_share=gs / (fs * mu))
f0 = brentq(lambda f: gbar(f, R), fs, hi * (1 - 1e-12), xtol=1e-14)   # zero-growth leverage
res["zero_growth"] = dict(f=f0, ratio=f0 / fs, worst_day_log=float(np.log1p(f0 * R.min())),
                          quad_zero=2 * mu / m2)
res["levered_moves"] = {f"{th:g}": dict(n=int((np.abs(fs * R) > th).sum()), share=float((np.abs(fs * R) > th).mean()))
                        for th in (0.1, 0.2, 0.3)}
res["one_sd_move_at_fstar"] = fs * np.sqrt(s2)
worst = int(R.argmin())
res["worst_day_at_fstar_log"] = float(np.log1p(fs * R[worst]))
res["total_log_at_fstar"] = gs * T

# quadratic model g_q(f) = f mu - f^2 m2 / 2
fq = mu / m2
res["quad"] = dict(f=fq, g_ann=(fq * mu - fq**2 * m2 / 2) * A, g_ann_at_fstar=(fs * mu - fs**2 * m2 / 2) * A,
                   f_mu_s2=mu / s2)

# ---------------------------------------------------------------- leverage table (Exhibit 1)
rows = []
for name, f in [("1", 1.0), ("2", 2.0), ("half", fs / 2), ("full", fs), ("zero", f0)]:
    rows.append(dict(name=name, f=f, g_ann=gbar(f, R) * A, wealth=float(np.exp(gbar(f, R) * T)),
                     vol_ann=f * np.sqrt(s2 * A), mdd=max_drawdown(f, R), worst=f * R.min(), arith_ann=f * mu * A))
res["levels"] = rows

# growth curve values used in the text
res["curve"] = {f"{f:g}": dict(g_ann=gbar(f, R) * A, quad_ann=(f * mu - f**2 * m2 / 2) * A)
                for f in [0.5, 1, 2, 2.5, 3, 4, 5, 6, 7, 8, 9, 9.5, 9.9]}
res["fractions"] = {f"{lam:g}": gbar(lam * fs, R) / gs for lam in [0.25, 0.5, 0.75, 0.9, 1.1, 1.25, 1.5, 1.75, 2.0 if 2 * fs < hi else 1.8]}
res["flat_top_half"] = dict(pred_loss=0.5 * abs(g2(fs, R)) * A * (fs / 2) ** 2, actual_loss=(gs - gbar(fs / 2, R)) * A,
                            per_unit=0.5 * abs(g2(fs, R)) * A)

# ---------------------------------------------------------------- moment truncations of the Kelly condition
r3 = np.roots([m3, -m2, mu]); r4 = np.roots([-m4, m3, -m2, mu])
inside = lambda rr: float(min((x.real for x in rr if abs(x.imag) < 1e-9 and lo < x.real < hi), key=lambda v: abs(v - fs)))
res["trunc"] = dict(order2=fq, order3=inside(r3), order4=inside(r4), exact=fs, maxabs_fR=fs * max(abs(R.min()), R.max()))

# ---------------------------------------------------------------- Newton and bisection traces (Exhibit 6)
newton = []
f = 0.0
for k in range(6):
    newton.append(dict(n=k, f=f, err=abs(f - fs), g1=g1(f, R), g2=g2(f, R)))
    f = f - g1(f, R) / g2(f, R)
res["newton"] = newton
bis = []
a, b = 0.0, 10.0                                  # g1(0) = mu > 0; g1 -> -inf as f -> 10 (worst day -10%)
bis.append(dict(n=0, a=a, b=b, width=b - a, mid_err=abs((a + b) / 2 - fs)))
n = 0
while b - a >= 1e-12:
    n += 1
    m = (a + b) / 2
    if g1(m, R) > 0:
        a = m
    else:
        b = m
    bis.append(dict(n=n, a=a, b=b, width=b - a, mid_err=abs((a + b) / 2 - fs)))
res["bisection"] = bis
res["bisection_steps_1e-12"] = n

# ---------------------------------------------------------------- the 2x cap (Section 4)
res["cap2"] = dict(g_ann=gbar(2, R) * A, g1_ann=g1(2, R) * A, wealth=float(np.exp(gbar(2, R) * T)),
                   g25_ann=gbar(2.5, R) * A, gain_to_25=(gbar(2.5, R) - gbar(2, R)) * A, first_order_25=0.5 * g1(2, R) * A,
                   real_00631L=float(np.prod(1 + RL)), real_00631L_ann=float(np.log1p(RL).sum() / YEARS))

# ---------------------------------------------------------------- per calendar year (Exhibit 4)
yr = np.array([d.year for d in dates])
years = []
for y in range(2015, 2026):
    r = R[yr == y]
    fy = kelly(r)
    years.append(dict(year=y, n=int(len(r)), ret=float(np.prod(1 + r) - 1), mu_bp=r.mean() * 1e4, s_pct=r.std() * 100,
                      f=fy, f_quad=r.mean() / r.var(), f_cap=float(min(max(fy, 0.0), 2.0)), g1_at_0=r.mean(),
                      dom_lo=domain(r)[0], dom_hi=domain(r)[1]))
res["years"] = years
# sub-periods
halves = {}
h = T // 2
for name, r, d0 in [("first_half", R[:h], dates[0]), ("second_half", R[h:], dates[h])]:
    halves[name] = dict(start=str(d0), n=int(len(r)), f=kelly(r), f_quad=r.mean() / r.var())
halves["split_last_first"] = str(dates[h - 1])
m2020 = yr >= 2020
halves["2020_2026"] = dict(n=int(m2020.sum()), f=kelly(R[m2020]), f_quad=R[m2020].mean() / R[m2020].var())
res["halves"] = halves

# ---------------------------------------------------------------- rolling three-year windows (Exhibit 8)
W = 729                                           # 3 x 243 trading days
roll = []
for e in range(W, T + 1):
    r = R[e - W:e]
    roll.append((str(dates[e - 1]), kelly(r, xtol=1e-10), r.mean() / r.var()))
fr = np.array([x[1] for x in roll])
res["rolling"] = dict(window=W, n=len(roll), first_end=roll[0][0], min=float(fr.min()), min_end=roll[int(fr.argmin())][0],
                      max=float(fr.max()), max_end=roll[int(fr.argmax())][0], last=float(fr[-1]), median=float(np.median(fr)))

# ---------------------------------------------------------------- sampling error preview (Section 7)
se = np.sqrt(s2) / np.sqrt(T)
res["se"] = dict(se_mu=se, t=mu / se, rel=se / mu, lo_mu=mu - 1.96 * se, hi_mu=mu + 1.96 * se,
                 f_lo=(mu - 1.96 * se) / s2, f_hi=(mu + 1.96 * se) / s2,
                 lam_if_lo=fs / ((mu - 1.96 * se) / s2), lam_if_hi=fs / ((mu + 1.96 * se) / s2))
q = lambda lam: 1 - (1 - lam) ** 2
res["se"]["share_if_lo_quad"] = q(res["se"]["lam_if_lo"])
res["se"]["share_if_hi_quad"] = q(res["se"]["lam_if_hi"])

# ---------------------------------------------------------------- envelope theorem: financing rate (Example 11)
def gbar_r(f, r_d):
    return float(np.log1p(r_d + f * (R - r_d)).mean())


def kelly_r(r_d):
    return brentq(lambda f: float(((R - r_d) / (1 + r_d + f * (R - r_d))).mean()), 0, 9.99, xtol=1e-14)


r_ann = 0.02
r_d = r_ann / A
f_r = kelly_r(r_d)
V0, Vr = gs * A, gbar_r(f_r, r_d) * A
res["financing"] = dict(r_ann=r_ann, r_day=r_d, dVdr=1 - fs, f_r=f_r, V0=V0, Vr=Vr, dV=Vr - V0, first_order=(1 - fs) * r_ann,
                        g_at_old_f=gbar_r(fs, r_d) * A, df_dr_ann=(f_r - fs) / r_ann)

# ---------------------------------------------------------------- Sharpe-based view of the in-sample optimum
res["sharpe"] = dict(sr_ann=mu * A / np.sqrt(s2 * A), f_sr_over_sigma=(mu * A / np.sqrt(s2 * A)) / np.sqrt(s2 * A),
                     g_sr2_half=(mu * A / np.sqrt(s2 * A)) ** 2 / 2)


def conv(o):
    if isinstance(o, dict): return {k: conv(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [conv(v) for v in o]
    if isinstance(o, np.floating): return float(o)
    if isinstance(o, np.integer): return int(o)
    return o


(HERE / "processed" / "lm04_stats.json").write_text(json.dumps(conv(res), indent=1), encoding="utf-8")

# ---------------------------------------------------------------- report
P = print
mo = res["mom"]
P(f"SAMPLE {res['first']} -> {res['last']}  T={T}  years={YEARS:.3f}  A={A:.2f} trading days/yr")
P(f"  mu={mo['mu']:.6%}/day  s={mo['s']:.4%}  s2={mo['s2']:.6e}  m2={mo['m2']:.6e}  m3={mo['m3']:.4e}  m4={mo['m4']:.4e}")
P(f"  skew={mo['skew']:.3f}  exkurt={mo['exkurt']:.2f}  min={mo['min']:.4%} ({mo['argmin']})  max={mo['max']:.4%} ({mo['argmax']})")
P(f"  mu/s2={mo['mu_over_s2']:.4f}  mu/m2={mo['mu_over_m2']:.4f}  SR daily={mo['sr_daily']:.4f}  SR annual={mo['sr_annual']:.4f}"
  f"  mu ann={mo['mu_annual']:.4%}  vol ann={mo['vol_annual']:.4%}")
P(f"  domain=({lo:.6f}, {hi:.6f})")
k = res["kelly"]
P(f"KELLY f*={k['f']:.6f}  g*={k['g_day']:.6%}/day = {k['g_ann']:.4%}/yr  g''(f*)={k['g2_day']:.6e}/day = {k['g2_ann']:.5f}/yr"
  f"  C={k['newton_C']:.4f}  mean 1/(1+f*R)={k['mean_inv']:.15f}  arith ann={k['arith_ann']:.4%}  g*/arith={k['drag_share']:.4f}")
z = res["zero_growth"]
P(f"ZERO GROWTH f0={z['f']:.5f}  f0/f*={z['ratio']:.4f}  worst-day log at f0={z['worst_day_log']:.4f}  quad zero=2mu/m2={z['quad_zero']:.4f}")
P(f"  worst day at f*: log={res['worst_day_at_fstar_log']:.4f}  total log at f*={res['total_log_at_fstar']:.4f}")
P("LEVERED MOVES at f*: " + "  ".join(f">{kk}: {v['n']} days ({v['share']:.1%})" for kk, v in res["levered_moves"].items())
  + f"  one-sd move={res['one_sd_move_at_fstar']:.2%}")
P(f"QUAD f={res['quad']['f']:.4f}  g_ann(max)={res['quad']['g_ann']:.4%}  quad at f*={res['quad']['g_ann_at_fstar']:.4%}")
P("LEVELS  name f g_ann wealth vol_ann mdd worst arith_ann")
for rw in rows:
    P(f"  {rw['name']:5s} {rw['f']:.4f} {rw['g_ann']:.4%} {rw['wealth']:.3f} {rw['vol_ann']:.4%} {rw['mdd']:.4%} {rw['worst']:.4%} {rw['arith_ann']:.4%}")
P("CURVE " + "  ".join(f"f={kk}: {v['g_ann']:.4%}/{v['quad_ann']:.4%}" for kk, v in res["curve"].items()))
P("FRACTIONS " + "  ".join(f"lam={kk}: {v:.4f}" for kk, v in res["fractions"].items()))
ft = res["flat_top_half"]
P(f"FLAT TOP half: predicted loss={ft['pred_loss']:.4%}  actual loss={ft['actual_loss']:.4%}  per unit^2={ft['per_unit']:.5f}")
tr = res["trunc"]
P(f"TRUNC order2={tr['order2']:.4f} order3={tr['order3']:.4f} order4={tr['order4']:.4f} exact={tr['exact']:.4f}  max|fR| at f*={tr['maxabs_fR']:.4f}")
P("NEWTON n f err g1 g2")
for rw in newton:
    P(f"  {rw['n']} {rw['f']:.12f} {rw['err']:.3e} {rw['g1']:.4e} {rw['g2']:.6e}")
P(f"  ratios e(n+1)/e(n)^2: " + ", ".join(f"{newton[i+1]['err']/newton[i]['err']**2:.4f}" for i in range(1, 4)))
P("BISECTION n width mid_err (selected)")
for rw in bis:
    if rw["n"] in (0, 1, 2, 3, 4, 5, 10, 20, 30, 40, 43, 44):
        P(f"  {rw['n']:2d} [{rw['a']:.12f}, {rw['b']:.12f}] width={rw['width']:.3e} mid_err={rw['mid_err']:.3e}")
P(f"  steps to width < 1e-12: {res['bisection_steps_1e-12']}")
c = res["cap2"]
P(f"CAP2 g(2)={c['g_ann']:.4%}/yr  g'(2)={c['g1_ann']:.4%}/yr per unit  wealth={c['wealth']:.3f}  g(2.5)={c['g25_ann']:.4%}"
  f"  gain 2->2.5 exact={c['gain_to_25']:.4%} first-order={c['first_order_25']:.4%}  00631L actual x{c['real_00631L']:.2f} ({c['real_00631L_ann']:.4%}/yr)")
P("YEARS year n ret mu_bp s_pct f* f_quad f_cap domain")
for y in years:
    P(f"  {y['year']} {y['n']} {y['ret']:+.4%} {y['mu_bp']:+.2f} {y['s_pct']:.3f} {y['f']:+.3f} {y['f_quad']:+.3f} {y['f_cap']:.0f} ({y['dom_lo']:.1f},{y['dom_hi']:.1f})")
P("HALVES", {kk: ({k2: (round(v2, 4) if isinstance(v2, float) else v2) for k2, v2 in vv.items()} if isinstance(vv, dict) else vv) for kk, vv in halves.items()})
ro = res["rolling"]
P(f"ROLLING W={ro['window']} n={ro['n']} first_end={ro['first_end']} min={ro['min']:.3f} (end {ro['min_end']}) max={ro['max']:.3f} (end {ro['max_end']}) last={ro['last']:.3f} median={ro['median']:.3f}")
se_ = res["se"]
P(f"SE se(mu)={se_['se_mu']:.6%}  t={se_['t']:.3f}  rel={se_['rel']:.4f}  mu CI=[{se_['lo_mu']:.4%}, {se_['hi_mu']:.4%}]  f range=[{se_['f_lo']:.3f}, {se_['f_hi']:.3f}]"
  f"  lambda if lo={se_['lam_if_lo']:.3f} (share {se_['share_if_lo_quad']:.3f})  lambda if hi={se_['lam_if_hi']:.3f} (share {se_['share_if_hi_quad']:.3f})")
fi = res["financing"]
P(f"FINANCING r={fi['r_ann']:.2%}/yr ({fi['r_day']:.3e}/day)  dV/dr=1-f*={fi['dVdr']:.4f}  f*(r)={fi['f_r']:.4f}  V0={fi['V0']:.4%}  V(r)={fi['Vr']:.4%}"
  f"  dV={fi['dV']:.4%}  first-order={fi['first_order']:.4%}  g at old f*={fi['g_at_old_f']:.4%}  df*/dr={fi['df_dr_ann']:.3f}")
sh = res["sharpe"]
P(f"SHARPE SR ann={sh['sr_ann']:.4f}  SR/sigma={sh['f_sr_over_sigma']:.4f}  SR^2/2={sh['g_sr2_half']:.4%}")
