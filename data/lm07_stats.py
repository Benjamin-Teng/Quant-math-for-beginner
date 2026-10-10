"""Every data-based number quoted in LM7, from the verified 0050 / 00679B series.

Run after lm07_series.py:  uv run python data/lm07_stats.py
Writes data/processed/lm07_stats.json and prints the numbers used in the text.

Conventions (stated in the module):
  * daily simple total returns between consecutive common trading dates, 2017-01-18 .. 2026-10-08;
  * annualization factor A = (number of returns) / (calendar years from the base date 2017-01-17);
  * means are arithmetic, annualized as A x daily mean; variances and covariances use divisor T
    (population form, as in LM3) and are annualized as A x daily value;
  * the estimation window is 2017-01-18 .. 2021-12-30 (in sample), the test window 2022-01-03 .. 2026-10-08;
  * r_f = 1.5% a year is an illustrative assumption, used only for the tangency and Kelly calculations.
"""
import datetime as dt
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
BASE = "2017-01-17"
RF = 0.015
df = pl.read_parquet(HERE / "processed" / "lm07_returns.parquet").drop_nulls("R_0050").sort("date")
dates = df["date"].to_list()
R1 = df["R_0050"].to_numpy()
R2 = df["R_00679B"].to_numpy()
year = np.array([int(d[:4]) for d in dates])
n = len(R1)
years = (dt.date.fromisoformat(dates[-1]) - dt.date.fromisoformat(BASE)).days / 365.25
A = n / years
IS, OOS = year <= 2021, year >= 2022
res: dict[str, Any] = {"sample": {"n": n, "first": dates[0], "last": dates[-1], "base": BASE, "years": years, "A": A, "rf": RF,
                      "n_is": int(IS.sum()), "n_oos": int(OOS.sum())}}


def growth(x):
    return float(np.prod(1 + x))


def est(m, rf=RF) -> dict[str, Any]:
    """Two-asset estimates on mask m (annualized, population moments)."""
    a, b = R1[m], R2[m]
    mu1, mu2 = A * a.mean(), A * b.mean()
    S = np.cov(np.vstack([a, b]), ddof=0) * A
    s1, s2, c = math.sqrt(S[0, 0]), math.sqrt(S[1, 1]), S[0, 1]
    rho = c / (s1 * s2)
    den = S[0, 0] + S[1, 1] - 2 * c
    w = (S[1, 1] - c) / den
    vmin = (S[0, 0] * S[1, 1] - c * c) / den
    e1, e2 = mu1 - rf, mu2 - rf
    det = S[0, 0] * S[1, 1] - c * c
    f1 = (S[1, 1] * e1 - c * e2) / det
    f2 = (S[0, 0] * e2 - c * e1) / det
    sr1, sr2 = e1 / s1, e2 / s2
    sr2_star = (sr1**2 + sr2**2 - 2 * rho * sr1 * sr2) / (1 - rho**2)
    return {"n": int(m.sum()), "mu1": mu1, "mu2": mu2, "s1": s1, "s2": s2, "cov": c, "rho": rho, "w_mv": w, "s_mv": math.sqrt(vmin),
                "lam": 2 * vmin, "e1": e1, "e2": e2, "f1": f1, "f2": f2, "lev": f1 + f2, "wT1": f1 / (f1 + f2), "wT2": f2 / (f1 + f2),
                "sr1": sr1, "sr2": sr2, "sr_star": math.sqrt(sr2_star), "g_star": rf + 0.5 * sr2_star,
                "g1": growth(a) - 1, "g2": growth(b) - 1}


ALL = np.ones(n, bool)
res["full"] = est(ALL)
res["is"] = est(IS)
res["oos"] = est(OOS)
res["y2022"] = est(year == 2022)
res["y2023p"] = est(year >= 2023)
F = res["full"]
F["cagr1"] = growth(R1) ** (1 / years) - 1
F["cagr2"] = growth(R2) ** (1 / years) - 1
F["min1"], F["max1"] = float(R1.min()), float(R1.max())
F["min2"], F["max2"] = float(R2.min()), float(R2.max())
F["date_min1"], F["date_min2"] = dates[int(R1.argmin())], dates[int(R2.argmin())]

# ---------------------------------------------------------------- by calendar year
rows: list[dict[str, Any]] = []
for y in range(2017, 2027):
    m = year == y
    e = est(m)
    rows.append({"year": y, "n": e["n"], "r1": e["g1"], "r2": e["g2"], "s1": e["s1"], "s2": e["s2"], "rho": e["rho"], "w_mv": e["w_mv"],
                     "s_mv": e["s_mv"]})
res["years"] = rows

# ---------------------------------------------------------------- correlation at lower frequencies
I = df.select("date", "I_0050", "I_00679B").with_columns(pl.col("date").str.to_date())
base_row = pl.DataFrame({"date": [dt.date.fromisoformat(BASE)], "I_0050": [1.0], "I_00679B": [1.0]})
freq: dict[str, Any] = {}
for every in ("1w", "1mo"):
    w = I.group_by_dynamic("date", every=every).agg(pl.col("I_0050").last(), pl.col("I_00679B").last()).sort("date")
    a = np.concatenate([[1.0], w["I_0050"].to_numpy()])
    b = np.concatenate([[1.0], w["I_00679B"].to_numpy()])
    r1, r2 = a[1:] / a[:-1] - 1, b[1:] / b[:-1] - 1
    yy = w["date"].dt.year().to_numpy()
    freq[every] = {"n": len(r1), "full": float(np.corrcoef(r1, r2)[0, 1]),
                       "IS": float(np.corrcoef(r1[yy <= 2021], r2[yy <= 2021])[0, 1]),
                       "OOS": float(np.corrcoef(r1[yy >= 2022], r2[yy >= 2022])[0, 1])}
lag: dict[int, float] = {}
for k in (-1, 1):
    lag[k] = float(np.corrcoef(R1[k:], R2[:-k])[0, 1]) if k > 0 else float(np.corrcoef(R1[:k], R2[-k:])[0, 1])
freq["lag"] = {"R1_t_vs_R2_t-1": lag[1], "R1_t-1_vs_R2_t": lag[-1]}
res["freq"] = freq

# ---------------------------------------------------------------- in sample vs out of sample (the case)
wIS = res["is"]["w_mv"]
port = lambda w, m: w * R1[m] + (1 - w) * R2[m]
vol = lambda x: math.sqrt(A * x.var())
cagr = lambda x: growth(x) ** (A / len(x)) - 1
# calendar span of each window (AUTHORING 8: years = calendar days / 365.25), from the close before its first return
last_is = dates[int(np.flatnonzero(IS)[-1])]
yrs_is = (dt.date.fromisoformat(last_is) - dt.date.fromisoformat(BASE)).days / 365.25
yrs_oos = (dt.date.fromisoformat(dates[-1]) - dt.date.fromisoformat(last_is)).days / 365.25
cagr_cal = lambda x, yrs: growth(x) ** (1 / yrs) - 1
oos_rows: dict[str, dict[str, Any]] = {}
for name, w in (("0050", 1.0), ("00679B", 0.0), ("IS min-var", wIS), ("OOS min-var", res["oos"]["w_mv"]),
                ("60/40", 0.6), ("50/50", 0.5)):
    oos_rows[name] = {"w": w, "vol_is": vol(port(w, IS)), "vol_oos": vol(port(w, OOS)), "ret_is": growth(port(w, IS)) - 1,
                          "ret_oos": growth(port(w, OOS)) - 1, "cagr_is": cagr(port(w, IS)), "cagr_oos": cagr(port(w, OOS)),
                          "cagr_is_cal": cagr_cal(port(w, IS), yrs_is), "cagr_oos_cal": cagr_cal(port(w, OOS), yrs_oos),
                          "r2022": growth(port(w, year == 2022)) - 1}
res["oos_table"] = oos_rows
res["windows"] = {"last_is": last_is, "yrs_is": yrs_is, "yrs_oos": yrs_oos, "sessions_oos": float(OOS.sum() / yrs_oos)}
# standard error of an annualized mean over the estimation window: sigma / sqrt(years of data), with the window's
# calendar years (calendar days / 365.25, AUTHORING 8), the convention the module uses for the test window too
yd = yrs_is
res["se_means"] = {"years": yd, "se1": res["is"]["s1"] / math.sqrt(yd), "se2": res["is"]["s2"] / math.sqrt(yd),
                       "mu1": res["is"]["mu1"], "mu2": res["is"]["mu2"]}
res["se_means"].update(ratio1=res["se_means"]["se1"] / res["se_means"]["mu1"], ratio2=res["se_means"]["se2"] / res["se_means"]["mu2"])
res["case"] = {"w_is": wIS, "pred": res["is"]["s_mv"], "realized": oos_rows["IS min-var"]["vol_oos"],
                   "w_oos": res["oos"]["w_mv"], "s_oos": res["oos"]["s_mv"], "vol_full": vol(port(wIS, ALL)),
                   "miss": oos_rows["IS min-var"]["vol_oos"] - res["is"]["s_mv"]}
# flat bottom (exact identity V(w) = Vmin + D (w - w*)^2) on the test window
Doos = res["oos"]["s1"] ** 2 + res["oos"]["s2"] ** 2 - 2 * res["oos"]["cov"]
res["flat"] = {"D": Doos, "dw": wIS - res["oos"]["w_mv"], "vmin": res["oos"]["s_mv"] ** 2, "pen": Doos * (wIS - res["oos"]["w_mv"]) ** 2,
                   "moved": res["oos"]["s_mv"] - res["is"]["s_mv"], "weight_cost": oos_rows["IS min-var"]["vol_oos"] - res["oos"]["s_mv"],
                   "err5": math.sqrt(res["oos"]["s_mv"] ** 2 + Doos * 0.05**2) - res["oos"]["s_mv"],
                   "err10": math.sqrt(res["oos"]["s_mv"] ** 2 + Doos * 0.10**2) - res["oos"]["s_mv"]}
# envelope theorem: d(sigma_min^2)/d rho = 2 w1* w2* s1 s2 (IS inputs), checked against a +0.10 bump
def vmin_of(s1, s2, r):
    c = r * s1 * s2
    return (s1 * s1 * s2 * s2 - c * c) / (s1 * s1 + s2 * s2 - 2 * c)
e_ = res["is"]
env = 2 * e_["w_mv"] * (1 - e_["w_mv"]) * e_["s1"] * e_["s2"]
res["envelope"] = {"dvdrho": env, "pred_01": 0.1 * env, "exact_01": vmin_of(e_["s1"], e_["s2"], e_["rho"] + 0.1) - e_["s_mv"] ** 2,
                       "smin_bumped": math.sqrt(vmin_of(e_["s1"], e_["s2"], e_["rho"] + 0.1))}
# partial derivatives of V(s1, s2, rho) at the IS point for the fixed IS mix
res["attrib_partials"] = None   # filled below after the attribution block

# Taylor attribution of the variance of the fixed IS mix: V(s1, s2, rho) = a s1^2 + b s2^2 + c rho s1 s2
a_, b_, c_ = wIS**2, (1 - wIS) ** 2, 2 * wIS * (1 - wIS)
p0 = (res["is"]["s1"], res["is"]["s2"], res["is"]["rho"])
p1 = (res["oos"]["s1"], res["oos"]["s2"], res["oos"]["rho"])
V = lambda s1, s2, r: a_ * s1**2 + b_ * s2**2 + c_ * r * s1 * s2
d1, d2, dr = (p1[i] - p0[i] for i in range(3))
s1, s2, r = p0
first = {"s1": (2 * a_ * s1 + c_ * r * s2) * d1, "s2": (2 * b_ * s2 + c_ * r * s1) * d2, "rho": c_ * s1 * s2 * dr}
second = {"s1s1": a_ * d1**2, "s2s2": b_ * d2**2, "s1s2": c_ * r * d1 * d2, "s1rho": c_ * s2 * d1 * dr, "s2rho": c_ * s1 * d2 * dr}
third = c_ * d1 * d2 * dr
res["attrib"] = {"V0": V(*p0), "V1": V(*p1), "dV": V(*p1) - V(*p0), "first": first, "first_total": sum(first.values()),
                     "second": second, "second_total": sum(second.values()), "third": third,
                     "check": sum(first.values()) + sum(second.values()) + third - (V(*p1) - V(*p0)),
                     "vol0": math.sqrt(V(*p0)), "vol1": math.sqrt(V(*p1)), "d": {"s1": d1, "s2": d2, "rho": dr},
                     "dvol_first": {k: v / (2 * math.sqrt(V(*p0))) for k, v in first.items()}}
res["attrib_partials"] = {"dV_ds1": 2 * a_ * s1 + c_ * r * s2, "dV_ds2": 2 * b_ * s2 + c_ * r * s1, "dV_drho": c_ * s1 * s2,
                              "d2V_ds1": 2 * a_, "d2V_ds1drho": c_ * s2, "a": a_, "b": b_, "c": c_}
# first-order differential of sigma_p itself
sp0 = math.sqrt(V(*p0))
res["attrib"]["dsig_partials"] = {"ds1": (a_ * s1 + 0.5 * c_ * r * s2) / sp0, "ds2": (b_ * s2 + 0.5 * c_ * r * s1) / sp0,
                                      "drho": 0.5 * c_ * s1 * s2 / sp0}

# ---------------------------------------------------------------- 2022 and the currency effect
FX0, FX1 = 27.690, 30.708            # USD/TWD Taipei close, end-2021 and end-2022 (CBC / Taipei FX via CNA)
r2022 = res["y2022"]["g2"]
y_fx = FX1 / FX0 - 1
x_usd = (1 + r2022) / (1 + y_fx) - 1
res["fx2022"] = {"R_twd": r2022, "fx": y_fx, "x_usd": x_usd, "linear": x_usd + y_fx, "cross": x_usd * y_fx,
                     "fx_partial": 1 + x_usd, "bond_partial": 1 + y_fx, "r0050": res["y2022"]["g1"]}

# ---------------------------------------------------------------- marginal variance at 60/40 (full sample)
S11, S22, S12 = F["s1"] ** 2, F["s2"] ** 2, F["cov"]
w1, w2 = 0.6, 0.4
V64 = w1**2 * S11 + w2**2 * S22 + 2 * w1 * w2 * S12
dV1, dV2 = 2 * (w1 * S11 + w2 * S12), 2 * (w1 * S12 + w2 * S22)
res["marginal"] = {"V": V64, "vol": math.sqrt(V64), "dV1": dV1, "dV2": dV2, "dir": dV1 - dV2,
                       "dvol1": dV1 / (2 * math.sqrt(V64)), "dvol2": dV2 / (2 * math.sqrt(V64)),
                       "dvol_dir": (dV1 - dV2) / (2 * math.sqrt(V64)),
                       "exact_cash": math.sqrt((w1 + .01) ** 2 * S11 + w2**2 * S22 + 2 * (w1 + .01) * w2 * S12) - math.sqrt(V64),
                       "exact_switch": math.sqrt((w1 + .01) ** 2 * S11 + (w2 - .01) ** 2 * S22 + 2 * (w1 + .01) * (w2 - .01) * S12) - math.sqrt(V64)}

# ---------------------------------------------------------------- the covariance identities of Section 2 (checked on the data)
# Var(w1 R1 + w2 R2) = w1^2 s1^2 + 2 w1 w2 s12 + w2^2 s2^2;  Cov(R1, Rp) = w1 s1^2 + w2 s12;  Var(R1 - R2) = s1^2 + s2^2 - 2 s12
Rp64 = w1 * R1 + w2 * R2
res["cov_identities"] = {"var_p": A * Rp64.var(), "var_p_formula": V64,
                             "cov_1p": A * ((R1 - R1.mean()) * (Rp64 - Rp64.mean())).mean(), "cov_1p_formula": w1 * S11 + w2 * S12,
                             "var_diff": A * (R1 - R2).var(), "var_diff_formula": S11 + S22 - 2 * S12}
ci = res["cov_identities"]
assert abs(ci["var_p"] - ci["var_p_formula"]) < 1e-15 and abs(ci["cov_1p"] - ci["cov_1p_formula"]) < 1e-15
assert abs(ci["var_diff"] - ci["var_diff_formula"]) < 1e-15


# ---------------------------------------------------------------- log-growth function g(f1, f2) and its quadratic model
def g_exact(f, m=ALL, rf=RF):
    rd = rf / A
    u = rd + f[0] * (R1[m] - rd) + f[1] * (R2[m] - rd)
    return A * np.log1p(u).mean()


def grad_hess(f, m=ALL, rf=RF):
    rd = rf / A
    X = np.vstack([R1[m] - rd, R2[m] - rd])
    u = rd + f[0] * X[0] + f[1] * X[1]
    gr = A * (X / (1 + u)).mean(axis=1)
    He = -A * (X[:, None, :] * X[None, :, :] / (1 + u) ** 2).mean(axis=2)
    return gr, He


def g_quad(f, e):
    return RF + f[0] * e["e1"] + f[1] * e["e2"] - 0.5 * (f[0] ** 2 * e["s1"] ** 2 + 2 * f[0] * f[1] * e["cov"] + f[1] ** 2 * e["s2"] ** 2)


def g_quad2(f, e):
    """Second-order Taylor of ln(1+u) without dropping the squared daily mean."""
    m1 = RF + f[0] * e["e1"] + f[1] * e["e2"]
    return g_quad(f, e) - m1**2 / (2 * A)


def newton(f0, m=ALL, tol=1e-12, maxit=50):
    f = np.array(f0, float); path = [f.copy()]
    for k in range(maxit):
        gr, He = grad_hess(f, m)
        step = np.linalg.solve(He, gr)
        f = f - step; path.append(f.copy())
        if np.abs(step).max() < tol: break
    return f, path


emp: dict[str, dict[str, Any]] = {}
for key, m in (("full", ALL), ("is", IS), ("oos", OOS)):
    e = res[key]
    fstar = np.array([e["f1"], e["f2"]])
    fe, _ = newton(fstar, m)
    emp[key] = {"f1": fe[0], "f2": fe[1], "g": g_exact(fe, m), "g_at_quad": g_exact(fstar, m), "g_quad_at_quad": g_quad(fstar, e),
                    "g_half": g_exact(0.5 * fstar, m), "g_quad_half": g_quad(0.5 * fstar, e), "g_0050": g_exact((1, 0), m),
                    "worst_day_fstar": float((fstar[0] * (R1[m] - RF / A) + fstar[1] * (R2[m] - RF / A) + RF / A).min())}
res["kelly_emp"] = emp

# Taylor accuracy table (full sample)
fstar = np.array([F["f1"], F["f2"]])
pts = [("0050 alone", (1.0, 0.0)), ("00679B alone", (0.0, 1.0)), ("min-variance mix (full sample)", (F["w_mv"], 1 - F["w_mv"])),
       ("2 x 0050", (2.0, 0.0)), ("half Kelly", tuple(0.5 * fstar)), ("full Kelly (quadratic)", tuple(fstar))]
def taylor_terms(f) -> dict[str, Any]:
    """Split model (7.3) minus exact growth into the dropped squared daily mean and the higher-order terms of ln(1+R_p).

    exact = A mean ln(1+R_p);  A mean(R_p - R_p^2/2) = (7.3) - A mean(R_p)^2 / 2  (population variance, as in (7.3));
    exact - A mean(R_p - R_p^2/2) = third + fourth + rest, with third = A mean(R_p^3)/3 and fourth = -A mean(R_p^4)/4.
    """
    rd = RF / A
    Rp = rd + f[0] * (R1 - rd) + f[1] * (R2 - rd)
    ex = A * np.log1p(Rp).mean()
    sq = A * Rp.mean() ** 2 / 2
    q2 = A * (Rp - Rp**2 / 2).mean()
    third, fourth = A * (Rp**3).mean() / 3, -A * (Rp**4).mean() / 4
    rest = ex - q2 - third - fourth
    assert abs((g_quad(f, F) - sq) - q2) < 1e-12
    return {"sqmean": sq, "third": third, "fourth": fourth, "rest": rest, "higher": third + fourth + rest}


tay: list[dict[str, Any]] = []
for name, f in pts:
    ge, gq, gq2 = g_exact(f), g_quad(f, F), g_quad2(f, F)
    tt = taylor_terms(f)
    assert abs((gq - ge) - (tt["sqmean"] - tt["higher"])) < 1e-12
    tay.append(dict(name=name, f1=f[0], f2=f[1], exact=ge, quad=gq, quad2=gq2, err=gq - ge, err2=gq2 - ge, **tt))
res["taylor"] = tay

# gradient and Hessian of g at f = 0 (exact) vs the quadratic model
gr0, He0 = grad_hess((0.0, 0.0))
res["grad0"] = {"g1": gr0[0], "g2": gr0[1], "H11": He0[0, 0], "H12": He0[0, 1], "H22": He0[1, 1]}

# ---------------------------------------------------------------- KKT examples (full-sample and IS estimates)
KKT_SETS = [(), ("cap",), ("f2",), ("f1",), ("cap", "f2"), ("cap", "f1"), ("f1", "f2"), ("cap", "f1", "f2")]


def kkt_cap(e, cap) -> list[dict[str, Any]]:
    """max g_quad s.t. f1 + f2 <= cap (nu_c), -f1 <= 0 (nu_1), -f2 <= 0 (nu_2): every one of the 2^3 active sets.

    For a guessed active set, stationarity ev - S f = sum_i nu_i a_i and a_i . f = b_i (i active) form one linear system.
    A set whose constraint normals are linearly dependent cannot all hold as equalities here (f1 = f2 = 0 breaks
    f1 + f2 = cap): it is reported as inconsistent.
    """
    S = np.array([[e["s1"] ** 2, e["cov"]], [e["cov"], e["s2"] ** 2]]); ev = np.array([e["e1"], e["e2"]])
    cons = {"cap": (np.array([1.0, 1.0]), cap), "f1": (np.array([-1.0, 0.0]), 0.0), "f2": (np.array([0.0, -1.0]), 0.0)}
    name = {"cap": "nu_c", "f1": "nu_1", "f2": "nu_2"}
    out: list[dict[str, Any]] = []
    for act in KKT_SETS:
        k = len(act)
        Aa = np.array([cons[c][0] for c in act]).reshape(k, 2)
        if np.linalg.matrix_rank(Aa) < k:
            out.append({"case": "+".join(act), "consistent": False}); continue
        M = np.block([[S, Aa.T], [Aa, np.zeros((k, k))]])
        sol = np.linalg.solve(M, np.concatenate([ev, [cons[c][1] for c in act]]))
        f, nu = sol[:2], sol[2:]
        assert np.allclose(ev - S @ f, Aa.T @ nu, atol=1e-14)            # stationarity holds by construction
        feas = bool(all(a @ f <= b + 1e-12 for a, b in cons.values()))
        dual = bool((nu >= -1e-12).all())
        out.append({"case": "+".join(act) or "none", "consistent": True, "f1": f[0], "f2": f[1],
                        "mult": {name[c]: float(v) for c, v in zip(act, nu)}, "feasible": feas, "dual": dual, "ok": feas and dual,
                        "g": g_quad(f, e), "gross": float(abs(f).sum()), "net": float(f.sum())})
    assert sum(c.get("ok", False) for c in out) == 1, "exactly one KKT point expected (concave objective, convex set)"
    return out


res["kkt_cap"] = {"full_cap2": kkt_cap(F, 2.0), "is_cap2": kkt_cap(res["is"], 2.0), "full_cap1": kkt_cap(F, 1.0)}

# Net versus gross exposure cap (full sample, model (7.3)).  The cap f1 + f2 <= 2 limits NET exposure.
#  * nu_2 prices f2 >= 0: relaxed to f2 >= -0.01 under the net cap, the optimum moves to (2.01, -0.01) (checked by KKT);
#  * under a GROSS cap |f1| + |f2| <= 2 the same short uses up cap, so it displaces 0050: (1.99, -0.01).
gq = lambda f: g_quad(np.asarray(f, float), F)
Sf = np.array([[F["s1"] ** 2, F["cov"]], [F["cov"], F["s2"] ** 2]]); evf = np.array([F["e1"], F["e2"]])
f_rel = np.array([2.01, -0.01]); gr_rel = evf - Sf @ f_rel                # binding: cap and f2 >= -0.01
nu_c_rel, nu_2_rel = gr_rel[0], gr_rel[0] - gr_rel[1]
assert nu_c_rel > 0 and nu_2_rel > 0
# brute-force maximum of the model on the boundary of the gross-cap diamond |f1| + |f2| = 2 (the unconstrained optimum lies outside)
tt_ = np.linspace(0, 1, 200001)
edges = [np.column_stack([2 * tt_, 2 * (1 - tt_)]), np.column_stack([2 * tt_, -2 * (1 - tt_)]),
         np.column_stack([-2 * tt_, 2 * (1 - tt_)]), np.column_stack([-2 * tt_, -2 * (1 - tt_)])]
P_ = np.vstack(edges)
gv = RF + P_ @ evf - 0.5 * np.einsum("ij,jk,ik->i", P_, Sf, P_)
f_gross = P_[int(np.argmax(gv))]
assert np.allclose(f_gross, [2.0, 0.0], atol=1e-4)
cap_only = next(c for c in res["kkt_cap"]["full_cap2"] if c["case"] == "cap")
# a shadow price is a first-order value: the exact model gain of a larger cap, re-solved by KKT enumeration
cap21, cap3 = (next(c for c in kkt_cap(F, cap_) if c["ok"]) for cap_ in (2.1, 3.0))
res["netgross"] = {"f_rel": f_rel.tolist(), "gain_net": gq(f_rel) - gq((2.0, 0.0)), "nu2_pred": 0.01 * nu_2_rel, "nu_c_rel": nu_c_rel,
                       "nu_2_rel": nu_2_rel, "loss_gross": gq((1.99, -0.01)) - gq((2.0, 0.0)), "f_gross_opt": f_gross.tolist(),
                       "cap_only_gross": cap_only["gross"], "cap_only_f": [cap_only["f1"], cap_only["f2"]],
                       "g_f2_at_20": float((evf - Sf @ np.array([2.0, 0.0]))[1]),
                       # the relaxed optimum's gain split into its two moves from (2, 0): extra 0050, and the short alone
                       "gain_0050_only": gq((2.01, 0.0)) - gq((2.0, 0.0)), "gain_short_only": gq((2.0, -0.01)) - gq((2.0, 0.0)),
                       "loss_0050_cut": gq((1.99, 0.0)) - gq((2.0, 0.0)),
                       "cap21_f": [cap21["f1"], cap21["f2"]], "cap21_gain": cap21["g"] - gq((2.0, 0.0)),
                       "cap3_f": [cap3["f1"], cap3["f2"]], "cap3_gain": cap3["g"] - gq((2.0, 0.0))}


def floor(e, wmin) -> dict[str, Any]:
    S11, S22, S12 = e["s1"] ** 2, e["s2"] ** 2, e["cov"]
    Vw = lambda w: w * w * S11 + (1 - w) ** 2 * S22 + 2 * w * (1 - w) * S12
    dV = lambda w: 2 * w * S11 - 2 * (1 - w) * S22 + 2 * (1 - 2 * w) * S12
    w = max(e["w_mv"], wmin)
    mu = dV(w) if w == wmin else 0.0
    lam = 2 * ((1 - w) * S22 + w * S12)    # dV/dw2 at the solution = lambda (budget multiplier)
    return {"wmin": wmin, "w": w, "mu": mu, "lam": lam, "vol": math.sqrt(Vw(w)), "vol_unc": e["s_mv"],
                "vol_relaxed": math.sqrt(Vw(wmin - 0.01)), "dvar_pred": -0.01 * mu, "dvar_exact": Vw(wmin - 0.01) - Vw(wmin)}


res["floor"] = {"full_60": floor(F, 0.6), "is_60": floor(res["is"], 0.6)}

# ---------------------------------------------------------------- numerical optimization: gradient ascent vs Newton
fN, pathN = newton((0.0, 0.0))
gstar = g_exact(fN)


def shortfall(f, fs=fN):
    """g(fs) - g(f), computed as A mean ln((1+u_s)/(1+u)) with u_s - u = X (fs - f): no cancellation of two ~64% rates."""
    rd = RF / A
    u = rd + f[0] * (R1 - rd) + f[1] * (R2 - rd)
    du = (fs[0] - f[0]) * (R1 - rd) + (fs[1] - f[1]) * (R2 - rd)
    return A * np.log1p(du / (1 + u)).mean()


newton_rows = [{"k": k, "f1": p[0], "f2": p[1], "gap": shortfall(p), "gnorm": float(np.linalg.norm(grad_hess(p)[0]))}
               for k, p in enumerate(pathN)]
S = np.array([[F["s1"] ** 2, F["cov"]], [F["cov"], F["s2"] ** 2]])
eig = np.linalg.eigvalsh(S)
# the same two curvatures from the 2x2 closed form: roots of x^2 - (s1^2 + s2^2) x + det S = 0
tr_, det_ = S[0, 0] + S[1, 1], S[0, 0] * S[1, 1] - S[0, 1] ** 2
roots = [(tr_ - math.sqrt(tr_**2 - 4 * det_)) / 2, (tr_ + math.sqrt(tr_**2 - 4 * det_)) / 2]
assert np.allclose(roots, eig, rtol=1e-12)
alpha = 2 / (eig[0] + eig[1])          # best fixed step for the quadratic model
f = np.zeros(2); ga_rows = [{"k": 0, "f1": 0.0, "f2": 0.0, "gap": shortfall(f)}]
for k in range(1, 201):
    f = f + alpha * grad_hess(f)[0]
    ga_rows.append({"k": k, "f1": f[0], "f2": f[1], "gap": shortfall(f)})
first_below = lambda rows, tol: next((r["k"] for r in rows if r["gap"] < tol), None)
FLOOR = 1e-10      # the convergence chart and the text stop here: far above rounding error in g (about 1e-16)
res["numopt"] = {"f_newton": fN.tolist(), "g_star": gstar, "newton": newton_rows[:8], "eig": eig.tolist(), "kappa": eig[1] / eig[0],
                     "alpha": alpha, "rate": (eig[1] - eig[0]) / (eig[1] + eig[0]), "ga": [ga_rows[k] for k in (0, 1, 2, 5, 10, 20, 30, 40)],
                     "ga_k_1e6": first_below(ga_rows, 1e-6), "ga_k_1e10": first_below(ga_rows, 1e-10),
                     "nt_k_1e6": first_below(newton_rows, 1e-6), "nt_k_1e10": first_below(newton_rows, 1e-10), "floor": FLOOR,
                     "ga_path": [[r["k"], r["gap"]] for r in ga_rows[:61]], "nt_path": [[r["k"], r["gap"]] for r in newton_rows]}


def conv(o):
    if isinstance(o, dict): return {str(k): conv(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [conv(v) for v in o]
    if isinstance(o, np.ndarray): return conv(o.tolist())
    if isinstance(o, (np.floating,)): return float(o)
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.bool_,)): return bool(o)
    return o


(HERE / "processed" / "lm07_stats.json").write_text(json.dumps(conv(res), indent=1), encoding="utf-8")

# ---------------------------------------------------------------- print
P = print
s = res["sample"]
P(f"SAMPLE n={s['n']} {s['first']}..{s['last']} years={s['years']:.6f} A={s['A']:.6f} (printed 243.0543) n_is={s['n_is']} n_oos={s['n_oos']}")
for key in ("full", "is", "oos", "y2022", "y2023p"):
    e = res[key]
    P(f"{key:7s} n={e['n']:4d} mu1={e['mu1']:.4%} mu2={e['mu2']:.4%} s1={e['s1']:.4%} s2={e['s2']:.4%} rho={e['rho']:+.4f} "
      f"cov={e['cov']:+.6f} w_mv={e['w_mv']:.4%} s_mv={e['s_mv']:.4%} lam={e['lam']:.5f} | ret1={e['g1']:+.4%} ret2={e['g2']:+.4%}")
    P(f"        e1={e['e1']:.4%} e2={e['e2']:+.4%} SR1={e['sr1']:.4f} SR2={e['sr2']:+.4f} SR*={e['sr_star']:.4f} "
      f"Kelly f1={e['f1']:.4f} f2={e['f2']:+.4f} lev={e['lev']:.4f} wT=({e['wT1']:.4f},{e['wT2']:+.4f}) g*quad={e['g_star']:.4%}")
P(f"FULL extra: cagr1={F['cagr1']:.4%} cagr2={F['cagr2']:+.4%} min1={F['min1']:.4%} on {F['date_min1']} min2={F['min2']:.4%} on {F['date_min2']}")
P("YEARS: year n r0050 r00679B s1 s2 rho w_mv s_mv")
for r_ in rows:
    P(f"  {r_['year']} {r_['n']:3d} {r_['r1']:+8.2%} {r_['r2']:+8.2%} {r_['s1']:7.2%} {r_['s2']:7.2%} {r_['rho']:+.3f} {r_['w_mv']:7.2%} {r_['s_mv']:6.2%}")
P("FREQ corr:", {k: ({kk: round(vv, 4) for kk, vv in v.items()} if isinstance(v, dict) else v) for k, v in freq.items()})
P("OOS TABLE:")
for k, v in oos_rows.items():
    P(f"  {k:12s} w={v['w']:.4f} vol_is={v['vol_is']:.4%} vol_oos={v['vol_oos']:.4%} ret_is={v['ret_is']:+.2%} "
      f"ret_oos={v['ret_oos']:+.2%} cagr_is={v['cagr_is']:+.2%} cagr_oos={v['cagr_oos']:+.2%} "
      f"cagr_oos_calendar={v['cagr_oos_cal']:+.2%} r2022={v['r2022']:+.2%}")
P("WINDOWS:", {k: (round(v, 4) if isinstance(v, float) else v) for k, v in res["windows"].items()})
P("SE OF MEANS (2017-2021, calendar years):", {k: round(float(v), 5) for k, v in res["se_means"].items()})
P("COV IDENTITIES (60/40, full sample):", {k: round(v, 8) for k, v in res["cov_identities"].items()})
at: dict[str, Any] = res["attrib"]
P(f"ATTRIB V0={at['V0']*1e4:.2f}%^2 V1={at['V1']*1e4:.2f}%^2 dV={at['dV']*1e4:.2f} first={ {k: round(v*1e4, 2) for k, v in at['first'].items()} } "
  f"total1={at['first_total']*1e4:.2f} second={ {k: round(v*1e4, 2) for k, v in at['second'].items()} } total2={at['second_total']*1e4:.2f} "
  f"third={at['third']*1e4:.3f} check={at['check']:.1e} vol0={at['vol0']:.4%} vol1={at['vol1']:.4%} d={ {k: round(float(v), 6) for k, v in at['d'].items()} }")
P("  dsig partials", {k: round(v, 4) for k, v in at["dsig_partials"].items()}, "dvol from first-order dV:", {k: round(v * 100, 3) for k, v in at["dvol_first"].items()})
P("FX2022", {k: round(v, 6) for k, v in res["fx2022"].items()})
P("MARGINAL 60/40", {k: round(v, 6) for k, v in res["marginal"].items()})
P("GRAD0", {k: round(v, 6) for k, v in res["grad0"].items()})
P("TAYLOR (full sample):")
for t in tay:
    P(f"  {t['name']:32s} f=({t['f1']:.4f},{t['f2']:+.4f}) exact={t['exact']:.4%} quad={t['quad']:.4%} err={t['err']*1e4:+.1f}bp quad2={t['quad2']:.4%} err2={t['err2']*1e4:+.1f}bp"
      f" | sq.mean {t['sqmean']*1e4:+.2f}bp higher {-t['higher']*1e4:+.2f}bp (3rd {t['third']*1e4:+.2f} 4th {t['fourth']*1e4:+.2f} 5th+ {t['rest']*1e4:+.2f})")
P("KELLY EMPIRICAL:")
for k, v in emp.items():
    P(f"  {k:4s}", {kk: round(vv, 5) for kk, vv in v.items()})
P("KKT CAP:")
for k, v in res["kkt_cap"].items():
    P(" ", k)
    for c in v:
        if not c["consistent"]:
            P(f"    {c['case']:10s} inconsistent (constraint normals dependent)"); continue
        P(f"    {c['case']:10s} f=({c['f1']:.4f},{c['f2']:+.4f}) feasible={c['feasible']} dual={c['dual']} ok={c['ok']} g={c['g']:.4%} "
          f"gross={c['gross']:.4f}", {kk: round(vv, 5) for kk, vv in c["mult"].items()})
P("NET vs GROSS CAP:", {k: (np.round(v, 6).tolist() if isinstance(v, list) else round(v, 6)) for k, v in res["netgross"].items()})
P("FLOOR:", {k: {kk: round(vv, 6) for kk, vv in v.items()} for k, v in res["floor"].items()})
no: dict[str, Any] = res["numopt"]
P(f"NUMOPT f*={no['f_newton']} g*={no['g_star']:.6%} eig={no['eig']} kappa={no['kappa']:.3f} alpha={no['alpha']:.3f} rate={no['rate']:.4f}")
P("  newton:", [(r_["k"], round(r_["f1"], 6), round(r_["f2"], 6), f"{r_['gap']:.2e}") for r_ in no["newton"]])
P("  grad ascent:", [(r_["k"], round(r_["f1"], 4), round(r_["f2"], 4), f"{r_['gap']:.2e}") for r_ in no["ga"]])
P(f"  first k below 1e-6: GA {no['ga_k_1e6']} Newton {no['nt_k_1e6']}; below 1e-10: GA {no['ga_k_1e10']} Newton {no['nt_k_1e10']}")
P("CASE extra:", {k: round(v, 6) for k, v in res["case"].items()})
P("FLAT:", {k: round(v, 6) for k, v in res["flat"].items()})
P("ENVELOPE:", {k: round(v, 6) for k, v in res["envelope"].items()})
P("ATTRIB PARTIALS:", {k: round(v, 6) for k, v in res["attrib_partials"].items()})

# ---------------------------------------------------------------- extra: exact Hessian at the optimum (gradient-ascent rate) and worst days
fopt = np.array(res["numopt"]["f_newton"])
_, Hopt = grad_hess(fopt)
cv = np.linalg.eigvalsh(-Hopt)
alpha_ = res["numopt"]["alpha"]
rate_dist = max(abs(1 - alpha_ * cv[0]), abs(1 - alpha_ * cv[1]))
ga = res["numopt"]["ga_path"]
gap20, gap30 = ga[20][1], ga[30][1]
rd_ = RF / A
worst_opt = float((rd_ + fopt[0] * (R1 - rd_) + fopt[1] * (R2 - rd_)).min())
res["numopt_extra"] = {"curv_opt": cv.tolist(), "rate_dist": rate_dist, "rate_gap": rate_dist**2,
                           "empirical_gap_rate": (gap30 / gap20) ** 0.1, "worst_day_opt": worst_opt}
(HERE / "processed" / "lm07_stats.json").write_text(json.dumps(conv(res), indent=1), encoding="utf-8")
P("NUMOPT EXTRA:", {k: (np.round(v, 5).tolist() if isinstance(v, list) else round(v, 5)) for k, v in res["numopt_extra"].items()})
