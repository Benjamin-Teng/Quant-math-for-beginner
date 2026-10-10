"""LM4 statistics: empirical Kelly on 0050 daily total returns, 2014-10-31 -> 2026-10-08.

Computes every data-based number quoted in src/lm04.md and writes processed/lm04_stats.json.
Exhibits and examples are named by their labels in src/lm04.md ([[ex:case]], [[eg:band]], ...), never by number.
Run after build_series.py:  uv run python data/lm04_stats.py
"""
import json
from datetime import date
from decimal import Decimal, getcontext
from math import erf, sqrt
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl
from scipy import integrate
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
df = pl.read_parquet(HERE / "processed" / "etf_daily_returns.parquet").with_columns(pl.col("date").str.to_date())
R = df["R_0050"].to_numpy()
RL = df["R_00631L"].to_numpy()
dates = df["date"].to_list()
T = len(R)
BASE = date(2014, 10, 31)                      # last close before the first return
YEARS = (dates[-1] - BASE).days / 365.25       # 11.937 calendar years
A = T / YEARS                                  # 243.11 trading days a year (2,902 / 11.937): annualization factor


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


res: dict[str, Any] = {"T": T, "years": YEARS, "A": A, "first": str(dates[0]), "last": str(dates[-1])}

# ---------------------------------------------------------------- moments and quadratic approximation
mu, s2 = R.mean(), R.var()                      # population variance, as in (3.7)
m2, m3, m4 = (R**2).mean(), (R**3).mean(), (R**4).mean()
res["mom"] = {"mu": mu, "s": np.sqrt(s2), "s2": s2, "m2": m2, "m3": m3, "m4": m4,
                  "skew": float(((R - mu) ** 3).mean() / s2**1.5), "exkurt": float(((R - mu) ** 4).mean() / s2**2 - 3),
                  "mu_over_s2": mu / s2, "mu_over_m2": mu / m2, "sr_daily": mu / np.sqrt(s2),
                  "sr_annual": mu * A / (np.sqrt(s2) * np.sqrt(A)), "mu_annual": mu * A, "vol_annual": np.sqrt(s2 * A),
                  "min": R.min(), "max": R.max(), "argmin": str(dates[int(R.argmin())]), "argmax": str(dates[int(R.argmax())])}
lo, hi = domain(R)
res["domain"] = {"lo": lo, "hi": hi}

# ---------------------------------------------------------------- exact empirical Kelly
fs = kelly(R)
gs = gbar(fs, R)
res["kelly"] = {"f": fs, "g_day": gs, "g_ann": gs * A, "g2_day": g2(fs, R), "g2_ann": g2(fs, R) * A, "g3_day": g3(fs, R),
                    "newton_C": abs(g3(fs, R) / (2 * g2(fs, R))),
                    "mean_inv": float((1 / (1 + fs * R)).mean()),           # = 1 exactly at the optimum (Section 7)
                    "arith_ann": fs * mu * A, "drag_share": gs / (fs * mu)}
f0 = brentq(lambda f: gbar(f, R), fs, hi * (1 - 1e-12), xtol=1e-14)   # zero-growth leverage
res["zero_growth"] = {"f": f0, "ratio": f0 / fs, "worst_day_log": float(np.log1p(f0 * R.min())),
                          "quad_zero": 2 * mu / m2}
res["levered_moves"] = {f"{th:g}": {"n": int((np.abs(fs * R) > th).sum()), "share": float((np.abs(fs * R) > th).mean())}
                        for th in (0.1, 0.2, 0.3)}
res["one_sd_move_at_fstar"] = fs * np.sqrt(s2)
worst = int(R.argmin())
res["worst_day_at_fstar_log"] = float(np.log1p(fs * R[worst]))
res["total_log_at_fstar"] = gs * T

# quadratic model g_q(f) = f mu - f^2 m2 / 2
fq = mu / m2
res["quad"] = {"f": fq, "g_ann": (fq * mu - fq**2 * m2 / 2) * A, "g_ann_at_fstar": (fs * mu - fs**2 * m2 / 2) * A,
                   "f_mu_s2": mu / s2}

# ---------------------------------------------------------------- why the quadratic rule overshoots ([[eg:quadkelly]])
# Two more terms of ln(1+x) add f^2 m3 - f^3 m4 to the first-order condition. For normal returns with the same mean and
# standard deviation, m3 = mu^3 + 3 mu s^2 and m4 = mu^4 + 6 mu^2 s^2 + 3 s^4, and at f = mu/s^2 the two terms cancel to
# leading order. 0050's fourth moment is far larger (excess kurtosis), so the quartic term pulls the optimum down.
m3N = mu**3 + 3 * mu * s2
m4N = mu**4 + 6 * mu**2 * s2 + 3 * s2**2
sd = np.sqrt(s2)
Phi = lambda z: 0.5 * (1 + erf(z / sqrt(2)))
th = 0.10 / fs                                     # |f* R| > 10%  <=>  |R| > 0.10 / f*
p_big_normal = (1 - Phi((th - mu) / sd)) + Phi((-th - mu) / sd)


def g1_normal(f):
    """Kelly condition for normal returns with 0050's mu and s, integrated over mu +- 12 s (the rest has mass < 1e-32)."""
    dens = lambda x: x / (1 + f * x) * np.exp(-0.5 * ((x - mu) / sd) ** 2) / (sd * sqrt(2 * np.pi))
    return integrate.quad(dens, mu - 12 * sd, mu + 12 * sd, epsabs=1e-14, epsrel=1e-12, limit=200)[0]


ext = np.abs(R) >= 0.0999                          # the two limit days, -10% on 2025-04-07 and +10% on 2026-07-31
Rx = R[~ext]
overshoot: dict[str, Any] = {
    "cubic_at_fq": fq**2 * m3, "quartic_at_fq": fq**3 * m4, "cubic_at_fq_normal": fq**2 * m3N, "quartic_at_fq_normal": fq**3 * m4N,
    "m4_over_normal": m4 / m4N, "m3_central_share": float(((R - mu) ** 3).mean() / m3), "m3_3mus2_share": 3 * mu * s2 / m3,
    "big_days": int((np.abs(fs * R) > 0.10).sum()), "big_days_normal": p_big_normal * T, "big_share_normal": p_big_normal,
    "f_normal_exact": brentq(g1_normal, 5.0, 6.2, xtol=1e-10),
    "limit_days": [str(d) for d, e in zip(dates, ext) if e], "limit_days_m4_share": float((R[ext] ** 4).sum() / (R**4).sum()),
    "without_f": kelly(Rx), "without_mu_m2": Rx.mean() / (Rx**2).mean(), "without_mu_s2": Rx.mean() / Rx.var(),
    "without_exkurt": float(((Rx - Rx.mean()) ** 4).mean() / Rx.var() ** 2 - 3),
    "gap": fq - fs, "without_gap": Rx.mean() / (Rx**2).mean() - kelly(Rx)}
res["overshoot"] = overshoot

# ---------------------------------------------------------------- leverage table ([[ex:case]])
rows = []
for name, f in [("1", 1.0), ("2", 2.0), ("half", fs / 2), ("full", fs), ("zero", f0)]:
    rows.append({"name": name, "f": f, "g_ann": gbar(f, R) * A, "wealth": float(np.exp(gbar(f, R) * T)),
                     "vol_ann": f * np.sqrt(s2 * A), "mdd": max_drawdown(f, R), "worst": f * R.min(), "arith_ann": f * mu * A})
res["levels"] = rows

# growth curve values used in the text
res["curve"] = {f"{f:g}": {"g_ann": gbar(f, R) * A, "quad_ann": (f * mu - f**2 * m2 / 2) * A}
                for f in [0.5, 1, 2, 2.5, 3, 4, 5, 6, 7, 8, 9, 9.5, 9.9]}
res["fractions"] = {f"{lam:g}": gbar(lam * fs, R) / gs for lam in [0.25, 0.5, 0.75, 0.9, 1.1, 1.25, 1.5, 1.75, 2.0 if 2 * fs < hi else 1.8]}
res["flat_top_half"] = {"pred_loss": 0.5 * abs(g2(fs, R)) * A * (fs / 2) ** 2, "actual_loss": (gs - gbar(fs / 2, R)) * A,
                            "per_unit": 0.5 * abs(g2(fs, R)) * A}

# ---------------------------------------------------------------- degree of the cleared Kelly condition (Section 6)
# sum_t R_t/(1+fR_t) = sum over distinct non-zero values v of n_v v/(1+fv); clearing the denominators gives a polynomial
# of degree K-1 (K distinct non-zero values), with leading coefficient (prod v) * (number of non-zero days) != 0.
# Floating-point noise splits equal returns (np.unique on raw floats finds 2,731), so values are rounded to 12 decimals
# first: distinct rational returns built from 2-decimal prices differ by more than 1e-9. An exact count with
# fractions.Fraction from the raw closes and dividends gives the same 2,710 distinct non-zero returns.
nonzero = np.round(R[R != 0], 12)
res["degree"] = {"zero_days": int((R == 0).sum()), "distinct_nonzero": len(np.unique(nonzero)),
                     "degree": int(len(np.unique(nonzero)) - 1)}

# ---------------------------------------------------------------- Newton and bisection traces ([[ex:iter]])
newton = []
f = 0.0
for k in range(6):
    newton.append({"n": k, "f": f, "err": abs(f - fs), "g1": g1(f, R), "g2": g2(f, R)})
    f = f - g1(f, R) / g2(f, R)
res["newton"] = newton
bis = []
x_lo, x_hi = 0.0, 9.9                             # g1(0) = mu > 0; g1(9.9) < 0 (g1 -> -inf as f -> 10, the -10% day)
res["bracket"] = {"lo": x_lo, "hi": x_hi, "g1_lo": g1(x_lo, R), "g1_hi": g1(x_hi, R)}
bis.append({"n": 0, "a": x_lo, "b": x_hi, "width": x_hi - x_lo, "mid_err": abs((x_lo + x_hi) / 2 - fs)})
n = 0
while x_hi - x_lo >= 1e-12:
    n += 1
    m = (x_lo + x_hi) / 2
    if g1(m, R) > 0:
        x_lo = m
    else:
        x_hi = m
    bis.append({"n": n, "a": x_lo, "b": x_hi, "width": x_hi - x_lo, "mid_err": abs((x_lo + x_hi) / 2 - fs)})
res["bisection"] = bis
res["bisection_steps_1e-12"] = n

# [[ex:iter]] prints its errors from 50-digit arithmetic. Newton's fourth error is about three units in the last place
# of a double (ulp(5.42) = 8.9e-16), and a double-precision f* is itself off by a few units, which moves the second
# digit of bisection's step-44 midpoint error (4.5e-14 in doubles, 4.76e-14 exact: the module prints 4.8e-14). The
# returns are rebuilt exactly from the 2-decimal closes and dividends, (P_t + D_t) s_t / P_{t-1} - 1 on the common
# days, then f* is solved by Newton to full precision and both traces are rerun with the same start and bracket.
getcontext().prec = 50
_base = pl.read_csv(HERE / "processed" / "raw_merged_full.csv", n_rows=1, schema_overrides={"p0050": pl.Utf8})
assert _base["date"][0] == str(BASE)
RD, _prev = [], Decimal(_base["p0050"][0])
for _p, _d, _s in zip(df["p0050"].to_list(), df["d0050"].to_list(), df["s0050"].to_list(), strict=True):
    _P = Decimal(repr(_p))                        # repr of a 2-decimal close is its exact decimal string
    RD.append((_P + Decimal(repr(_d))) * Decimal(repr(_s)) / _prev - 1)
    _prev = _P
assert max(abs(float(x) - y) for x, y in zip(RD, R.tolist(), strict=True)) < 1e-15


def g1_hp(f):
    return sum(r / (1 + f * r) for r in RD) / len(RD)


def g2_hp(f):
    return -sum((r / (1 + f * r)) ** 2 for r in RD) / len(RD)


f_hp = Decimal(0)
for _ in range(10):                               # quadratic convergence: ten steps from 0 exhaust 50 digits
    f_hp -= g1_hp(f_hp) / g2_hp(f_hp)
assert abs(g1_hp(f_hp)) < Decimal("1e-45")
newton_hp, f_it = [], Decimal(0)
for k in range(5):
    newton_hp.append({"n": k, "f": float(f_it), "err": float(abs(f_it - f_hp))})
    f_it -= g1_hp(f_it) / g2_hp(f_it)
bis_hp, d_lo, d_hi = [], Decimal(0), Decimal("9.9")
for k in range(45):
    d_mid = (d_lo + d_hi) / 2
    bis_hp.append({"n": k, "width": float(d_hi - d_lo), "mid_err": float(abs(d_mid - f_hp))})
    assert abs(float(d_lo) - bis[k]["a"]) < 1e-12 and abs(float(d_hi) - bis[k]["b"]) < 1e-12   # same sign decisions
    if g1_hp(d_mid) > 0:
        d_lo = d_mid
    else:
        d_hi = d_mid
exact: dict[str, Any] = {"f": str(f_hp)[:20], "f_float_minus_exact": float(Decimal(fs) - f_hp), "newton": newton_hp,
                          "bisection": bis_hp}
res["exact"] = exact

# ---------------------------------------------------------------- the 2x cap (Section 4)
res["cap2"] = {"g_ann": gbar(2, R) * A, "g1_ann": g1(2, R) * A, "wealth": float(np.exp(gbar(2, R) * T)),
                   "g25_ann": gbar(2.5, R) * A, "gain_to_25": (gbar(2.5, R) - gbar(2, R)) * A, "first_order_25": 0.5 * g1(2, R) * A,
                   "real_00631L": float(np.prod(1 + RL)), "real_00631L_ann": float(np.log1p(RL).sum() / YEARS)}

# ---------------------------------------------------------------- per calendar year ([[ex:years]]): full years 2015-2025
yr = np.array([d.year for d in dates])


def year_row(y):
    r = R[yr == y]
    fy = kelly(r)
    return {"year": y, "n": len(r), "ret": float(np.prod(1 + r) - 1), "mu_bp": r.mean() * 1e4, "s_pct": r.std() * 100,
                "f": fy, "f_quad": r.mean() / r.var(), "f_cap": float(min(max(fy, 0.0), 2.0)), "g1_at_0": r.mean(),
                "dom_lo": domain(r)[0], "dom_hi": domain(r)[1], "first": str(dates[int(np.argmax(yr == y))]),
                "last": str(dates[len(yr) - 1 - int(np.argmax(yr[::-1] == y))])}


years = [year_row(y) for y in range(2015, 2026)]
res["years"] = years
res["partial_years"] = [year_row(y) for y in (2014, 2026)]          # left out of the rows, kept in the full-sample row
res["full_years_compound"] = float(np.prod([1 + y["ret"] for y in years]) - 1)
res["sample_total_return"] = float(np.prod(1 + R) - 1)
# sub-periods
halves = {}
h = T // 2
for name, r, d0 in [("first_half", R[:h], dates[0]), ("second_half", R[h:], dates[h])]:
    halves[name] = {"start": str(d0), "n": len(r), "f": kelly(r), "f_quad": r.mean() / r.var()}
halves["split_last_first"] = str(dates[h - 1])
m2020 = yr >= 2020
halves["2020_2026"] = {"n": int(m2020.sum()), "f": kelly(R[m2020]), "f_quad": R[m2020].mean() / R[m2020].var()}
res["halves"] = halves

# ---------------------------------------------------------------- rolling three-year windows ([[ex:rolling]])
W = 729                                           # 3 x 243 trading days
roll = []
for e in range(W, T + 1):
    r = R[e - W:e]
    roll.append((str(dates[e - 1]), kelly(r, xtol=1e-10), r.mean() / r.var()))
fr = np.array([x[1] for x in roll])
res["rolling"] = {"window": W, "n": len(roll), "first_end": roll[0][0], "min": float(fr.min()), "min_end": roll[int(fr.argmin())][0],
                      "max": float(fr.max()), "max_end": roll[int(fr.argmax())][0], "last": float(fr[-1]), "median": float(np.median(fr))}

# ---------------------------------------------------------------- sampling error preview ([[eg:band]])
# 95% interval for the mean, mu +- 1.96 SE. Every daily return is shifted by the same amount so that the sample mean sits
# at either end, and the EXACT Kelly condition is solved on the shifted sample (the quadratic rule mu/s^2, which is
# proportional to the mean, overshoots at the upper end: it is kept here only for comparison).
se = np.sqrt(s2) / np.sqrt(T)
res["se"] = {"se_mu": se, "t": mu / se, "rel": se / mu, "lo_mu": mu - 1.96 * se, "hi_mu": mu + 1.96 * se,
                 "f_lo_rule": (mu - 1.96 * se) / s2, "f_hi_rule": (mu + 1.96 * se) / s2}
q = lambda c: 1 - (1 - c) ** 2                    # share of g* kept at c = f / f*, quadratic model (4.15)
for side, k in (("lo", -1.96), ("hi", 1.96)):
    Rs = R + k * se
    f_side = kelly(Rs)
    c_side = fs / f_side
    res["se"].update({f"f_{side}": f_side, f"c_if_{side}": c_side, f"share_if_{side}_quad": q(c_side),
                      f"g_fstar_if_{side}": gbar(fs, Rs) * A, f"g_max_if_{side}": gbar(f_side, Rs) * A,
                      f"share_if_{side}_exact": gbar(fs, Rs) / gbar(f_side, Rs)})

# ---------------------------------------------------------------- envelope theorem: financing rate ([[eg:financing]])
def gbar_r(f, r_d):
    return float(np.log1p(r_d + f * (R - r_d)).mean())


def kelly_r(r_d):
    return brentq(lambda f: float(((R - r_d) / (1 + r_d + f * (R - r_d))).mean()), 0, 9.99, xtol=1e-14)


r_ann = 0.02
r_d = r_ann / A                                   # charged as 2%/A per trading day: a simple rate per session
f_r = kelly_r(r_d)
V0, Vr = gs * A, gbar_r(f_r, r_d) * A
res["financing"] = {"r_ann": r_ann, "r_day": r_d, "dVdr": 1 - fs, "f_r": f_r, "V0": V0, "Vr": Vr, "dV": Vr - V0, "first_order": (1 - fs) * r_ann,
                        "g_at_old_f": gbar_r(fs, r_d) * A, "df_dr_ann": (f_r - fs) / r_ann}

# ---------------------------------------------------------------- Sharpe-based view of the in-sample optimum
res["sharpe"] = {"sr_ann": mu * A / np.sqrt(s2 * A), "f_sr_over_sigma": (mu * A / np.sqrt(s2 * A)) / np.sqrt(s2 * A),
                     "g_sr2_half": (mu * A / np.sqrt(s2 * A)) ** 2 / 2}


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
ov = res["overshoot"]
P(f"OVERSHOOT at f_q: 0050 f^2 m3={ov['cubic_at_fq']:.3e} f^3 m4={ov['quartic_at_fq']:.3e}  normal f^2 m3={ov['cubic_at_fq_normal']:.3e}"
  f" f^3 m4={ov['quartic_at_fq_normal']:.3e}  m4/m4(normal)={ov['m4_over_normal']:.3f}  m3 shares: central {ov['m3_central_share']:.1%}"
  f" 3mu s^2 {ov['m3_3mus2_share']:.1%}")
P(f"  |f*R|>10%: 0050 {ov['big_days']} days; normal {ov['big_days_normal']:.1f} ({ov['big_share_normal']:.1%})  normal exact optimum"
  f" {ov['f_normal_exact']:.4f} vs rule {res['quad']['f']:.4f}")
P(f"  without {ov['limit_days']} (share of m4 {ov['limit_days_m4_share']:.1%}): exact {ov['without_f']:.4f} mu/m2 {ov['without_mu_m2']:.4f}"
  f" mu/s2 {ov['without_mu_s2']:.4f} exkurt {ov['without_exkurt']:.2f}  gap {ov['without_gap']:.4f} of {ov['gap']:.4f}"
  f" ({ov['without_gap'] / ov['gap']:.0%})")
P("LEVELS  name f g_ann wealth vol_ann mdd worst arith_ann")
for rw in rows:
    P(f"  {rw['name']:5s} {rw['f']:.4f} {rw['g_ann']:.4%} {rw['wealth']:.3f} {rw['vol_ann']:.4%} {rw['mdd']:.4%} {rw['worst']:.4%} {rw['arith_ann']:.4%}")
P("CURVE " + "  ".join(f"f={kk}: {v['g_ann']:.4%}/{v['quad_ann']:.4%}" for kk, v in res["curve"].items()))
P("FRACTIONS " + "  ".join(f"lam={kk}: {v:.4f}" for kk, v in res["fractions"].items()))
ft = res["flat_top_half"]
P(f"FLAT TOP half: predicted loss={ft['pred_loss']:.4%}  actual loss={ft['actual_loss']:.4%}  per unit^2={ft['per_unit']:.5f}")
dg_ = res["degree"]
P(f"DEGREE zero-return days={dg_['zero_days']}  distinct non-zero returns={dg_['distinct_nonzero']}  polynomial degree={dg_['degree']}")
P("NEWTON n f err g1 g2")
for rw in newton:
    P(f"  {rw['n']} {rw['f']:.12f} {rw['err']:.3e} {rw['g1']:.4e} {rw['g2']:.6e}")
P("  ratios e(n+1)/e(n)^2: " + ", ".join(f"{newton[i+1]['err']/newton[i]['err']**2:.4f}" for i in range(1, 4)))
br = res["bracket"]
P(f"BISECTION bracket [{br['lo']}, {br['hi']}]: g'(lo)={br['g1_lo']:.4e} g'(hi)={br['g1_hi']:.4e};  n width mid_err (selected)")
for rw in bis:
    if rw["n"] in (0, 1, 2, 3, 4, 5, 10, 20, 30, 40, 43, 44):
        P(f"  {rw['n']:2d} [{rw['a']:.12f}, {rw['b']:.12f}] width={rw['width']:.3e} mid_err={rw['mid_err']:.3e}")
P(f"  steps to width < 1e-12: {res['bisection_steps_1e-12']}")
ex_ = res["exact"]
P(f"50 DIGITS f*={ex_['f']}  (double-precision f* minus exact: {ex_['f_float_minus_exact']:.2e})")
P("  Newton errors: " + "  ".join(f"n={r_['n']}: {r_['err']:.4e}" for r_ in ex_["newton"]))
P("  bisection width / midpoint error: " + "  ".join(f"n={r_['n']}: {r_['width']:.4g} / {r_['mid_err']:.4e}"
                                                    for r_ in ex_["bisection"] if r_["n"] in (0, 1, 2, 3, 4, 10, 20, 30, 44)))
c = res["cap2"]
P(f"CAP2 g(2)={c['g_ann']:.4%}/yr  g'(2)={c['g1_ann']:.4%}/yr per unit  wealth={c['wealth']:.3f}  g(2.5)={c['g25_ann']:.4%}"
  f"  gain 2->2.5 exact={c['gain_to_25']:.4%} first-order={c['first_order_25']:.4%}  00631L actual x{c['real_00631L']:.2f} ({c['real_00631L_ann']:.4%}/yr)")
P("YEARS year n ret mu_bp s_pct f* f_quad f_cap domain")
for y in years + res["partial_years"]:
    P(f"  {y['year']} {y['n']} {y['ret']:+.4%} {y['mu_bp']:+.2f} {y['s_pct']:.3f} {y['f']:+.3f} {y['f_quad']:+.3f} {y['f_cap']:.0f} ({y['dom_lo']:.1f},{y['dom_hi']:.1f})"
      f" {y['first']}..{y['last']}")
P(f"  full years 2015-2025 compound {res['full_years_compound']:+.4%};  whole sample {res['sample_total_return']:+.4%}")
P("HALVES", {kk: ({k2: (round(v2, 4) if isinstance(v2, float) else v2) for k2, v2 in vv.items()} if isinstance(vv, dict) else vv) for kk, vv in halves.items()})
ro = res["rolling"]
P(f"ROLLING W={ro['window']} n={ro['n']} first_end={ro['first_end']} min={ro['min']:.3f} (end {ro['min_end']}) max={ro['max']:.3f} (end {ro['max_end']}) last={ro['last']:.3f} median={ro['median']:.3f}")
se_ = res["se"]
P(f"SE se(mu)={se_['se_mu']:.6%}  t={se_['t']:.3f}  rel={se_['rel']:.4f}  mu CI=[{se_['lo_mu']:.4%}, {se_['hi_mu']:.4%}]"
  f"  exact f band=[{se_['f_lo']:.4f}, {se_['f_hi']:.4f}]  (rule mu/s2 would give [{se_['f_lo_rule']:.3f}, {se_['f_hi_rule']:.3f}])")
for side in ("lo", "hi"):
    P(f"  if true f*={se_[f'f_{side}']:.4f}: c={se_[f'c_if_{side}']:.4f} quad share={se_[f'share_if_{side}_quad']:.4f}"
      f"  exact on shifted sample: g(5.42)={se_[f'g_fstar_if_{side}']:.4%}/yr vs max {se_[f'g_max_if_{side}']:.4%}/yr"
      f" (share {se_[f'share_if_{side}_exact']:.4f})")
fi = res["financing"]
P(f"FINANCING r={fi['r_ann']:.2%}/yr ({fi['r_day']:.3e}/day)  dV/dr=1-f*={fi['dVdr']:.4f}  f*(r)={fi['f_r']:.4f}  V0={fi['V0']:.4%}  V(r)={fi['Vr']:.4%}"
  f"  dV={fi['dV']:.4%}  first-order={fi['first_order']:.4%}  g at old f*={fi['g_at_old_f']:.4%}  df*/dr={fi['df_dr_ann']:.3f}")
sh = res["sharpe"]
P(f"SHARPE SR ann={sh['sr_ann']:.4f}  SR/sigma={sh['f_sr_over_sigma']:.4f}  SR^2/2={sh['g_sr2_half']:.4%}")
