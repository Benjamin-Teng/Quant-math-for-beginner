"""Generate labs/LM07_lab (Polars-first notebook + README) for LM7.

Run:  uv run python build/make_lab07.py
Then execute from inside the lab folder:
      cd labs/LM07_lab && uv run jupyter nbconvert --to notebook --execute --inplace LM07_lab.ipynb

The notebook reads only the files in labs/LM07_lab/data/, which data/make_lab_data.py builds from data/raw/
(FinMind's licence keeps raw data out of the repository). This script writes the notebook and the README only.

Exhibit and example numbers are never typed by hand: cells write [[ex:label]] / [[eg:label]], and the generator
resolves them from the labels in src/lm07.md, numbered in document order as build/build.py does.
"""
import re
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "LM07_lab"
LAB.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- exhibit / example numbers from the module's labels
NUM, _count = {}, {"exhibit": 0, "example": 0}
for m in re.finditer(r"(?m)^(?:>\s?)+\[!(exhibit|example)\][+-]?\s*(.*)$", (ROOT / "src" / "lm07.md").read_text(encoding="utf-8")):
    _count[m.group(1)] += 1
    lab = re.search(r"\{#([\w-]+)\}\s*$", m.group(2))
    if lab:
        NUM[lab.group(1)] = ("Exhibit" if m.group(1) == "exhibit" else "Example", _count[m.group(1)])


def refs(s):
    """Replace [[ex:a]], [[eg:a]] and ranges [[ex:a..b]] by 'Exhibit k', 'Examples k–l', checking the kind."""
    def rep(m):
        kind, a, b = m.group(1), m.group(2), m.group(3)
        word, ka = NUM[a]
        assert word == ("Exhibit" if kind == "ex" else "Example"), (kind, a)
        if b is None:
            return f"{word} {ka}"
        word_b, kb = NUM[b]
        assert word_b == word and kb > ka, (a, b)
        return f"{word}s {ka}–{kb}"
    out = re.sub(r"\[\[(ex|eg):([\w-]+)(?:\.\.([\w-]+))?\]\]", rep, s)
    assert not re.search(r"\[\[(ex|eg):", out), out
    return out


cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(refs(s.strip("\n"))))
code = lambda s: cells.append(nbf.v4.new_code_cell(refs(s.strip("\n"))))

md(r"""
# LM7 Lab — Multivariable Calculus and Lagrange Multipliers

Companion notebook to **From Calculus to Kelly, LM7**. It rebuilds the module's exhibits and computational examples from verified price files, solves the computational practice problems, and ends with an extension exercise.

| Part | Rebuilds |
|:--|:--|
| 1 | Total-return series for 0050 and 00679B: verification, dividends, split, common dates |
| 2 | The case ([[ex:case]]), statistics by year ([[ex:years]]), correlation at three frequencies, rolling correlation ([[ex:rollcorr]]) |
| 3 | Partial derivatives: 00679B in 2022 ([[eg:fx]]), the covariance identities, marginal variance ([[eg:marginal]]), Taylor attribution ([[ex:attrib]]) |
| 4 | The growth function: gradient and Hessian at zero, exact vs quadratic model and where the gap comes from ([[ex:taylor2]]) |
| 5 | Classifying critical points ([[eg:classify]]) |
| 6 | Lagrange multipliers solved symbolically and numerically ([[eg:split]], [[eg:budget]]) |
| 7 | Two-asset portfolios: level curves and the budget line ([[ex:levels]]), minimum variance in and out of sample, tangency and Kelly ([[eg:minvar]], [[eg:kellyeg]], [[ex:volcurve]], [[ex:kelly]]) |
| 8 | KKT: equity floor and leverage cap ([[eg:cap]], [[ex:kkt]]) |
| 9 | Numerical gradients, Newton vs gradient ascent ([[ex:converge]]) |
| 10 | Practice-problem solutions and an extension exercise |

**Environment.** From the repository root, `uv sync` installs the locked Python environment (`uv.lock`). Open this notebook with the `.venv` kernel, or run `uv run --with jupyterlab jupyter lab`.

**Data.** The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

The fetch script reads your token from the `FINMIND_TOKEN` environment variable and checks every file against `data/raw_manifest.json`. `data/` then holds the windows the book retrieved on 2026-10-10: FinMind `TaiwanStockPrice` closes (with FinMind's `spread` column) for 0050 and 00679B, and their cash dividends from `TaiwanStockDividendResult`. Prices are unadjusted; Part 1 handles dividends and the 0050 split explicitly. The notebook reads nothing outside `data/`.

**Conventions (as in the module).** Daily simple total returns between consecutive common trading dates from the base date 2017-01-17; moments with divisor $T$; annualization with $A=T/\text{years}=243.0543$ trading sessions a year (years = calendar days / 365.25), kept unrounded in every computation; an illustrative $r_f=1.5\%$ for tangency and Kelly, $r_f/A$ a day.
""")

code(r"""
from pathlib import Path
from datetime import date
import math
import numpy as np
import polars as pl
import matplotlib.pyplot as plt

DATA = Path("data")
BASE, RF = "2017-01-17", 0.015
pl.Config.set_tbl_rows(40)
pl.Config.set_float_precision(6)
plt.rcParams.update({"figure.figsize": (9, 4.5), "axes.grid": True, "grid.alpha": 0.3,
                     "axes.spines.top": False, "axes.spines.right": False})
""")

md(r"""
## Part 1 — Total-return series

* Every close must satisfy `close[t] − close[t−1] = spread[t]`. FinMind prints `spread = 0` on ex-dividend days and uses the split-adjusted reference on 0050's split day (4-for-1, **2025-06-18**), so those are the only mismatches allowed.
* 00679B has **37** ex-dates in the window. On two of them (2019-03-05 and 2025-08-21) the close did not change, so they produce no mismatch — but their dividends must still be paid. We therefore apply dividends from the dividend file on every ex-date and check that the previous close equals FinMind's `before_price`.
* Each fund's total-return index is built on its own calendar; returns are taken between consecutive **common** dates (0050 was halted 2025-06-11..17 while 00679B traded).
""")

code(r"""
SPLITS = {"0050": ("2025-06-18", 4.0)}

def load(sym):
    raw = pl.read_csv(DATA / f"{sym}_daily_raw.csv").sort("date")
    div = pl.read_csv(DATA / f"{sym}_dividends.csv").filter(pl.col("date") > raw["date"][0])
    chk = (raw.with_columns((pl.col("close") - pl.col("close").shift(1) - pl.col("spread")).abs().alias("gap"))
              .filter(pl.col("gap") > 0.005))
    sdate = SPLITS.get(sym, (None, 1.0))[0]
    allowed = set(div["date"]) | ({sdate} if sdate else set())
    unexplained = sorted(set(chk["date"]) - allowed)
    silent = sorted(set(div["date"]) - set(chk["date"]))
    prev = raw.with_columns(pl.col("close").shift(1).alias("prev")).join(div, on="date", how="inner")
    assert prev.height == div.height, "an ex-date is not a trading date"
    assert (prev["prev"] - prev["before_price"]).abs().max() < 1e-9, "previous close != before_price"
    print(f"{sym}: {raw.height} rows {raw['date'][0]} -> {raw['date'][-1]}; ex-dates {div.height}; "
          f"mismatches {chk.height}; unexplained {unexplained}; ex-dates without mismatch {silent}")
    assert not unexplained
    return raw, div

def tr_index(sym):
    raw, div = load(sym)
    sdate, k = SPLITS.get(sym, ("", 1.0))
    return (raw.join(div.select("date", pl.col("cash_dividend").alias("D")), on="date", how="left")
               .sort("date")
               .with_columns(pl.col("D").fill_null(0.0),
                             pl.when(pl.col("date") == pl.lit(sdate)).then(pl.lit(k)).otherwise(pl.lit(1.0)).alias("k"))
               .with_columns(((pl.col("close") + pl.col("D")) / (pl.col("close").shift(1) / pl.col("k"))).fill_null(1.0).alias("G"))
               .select("date", pl.col("G").cum_prod().alias(f"I_{sym}")))

idx = (tr_index("0050").join(tr_index("00679B"), on="date", how="inner")
          .filter(pl.col("date") >= pl.lit(BASE)).sort("date")
          .with_columns(pl.col("I_0050") / pl.col("I_0050").first(), pl.col("I_00679B") / pl.col("I_00679B").first()))
ret = (idx.with_columns((pl.col("I_0050") / pl.col("I_0050").shift(1) - 1).alias("R1"),
                        (pl.col("I_00679B") / pl.col("I_00679B").shift(1) - 1).alias("R2"))
          .drop_nulls("R1").with_columns(pl.col("date").str.to_date()))
R1, R2 = ret["R1"].to_numpy(), ret["R2"].to_numpy()
T = len(R1)
dates = ret["date"].to_list()
years = (dates[-1] - date.fromisoformat(BASE)).days / 365.25
A = T / years
yr = ret["date"].dt.year().to_numpy()
IS, OOS, ALL = yr <= 2021, yr >= 2022, np.ones(T, bool)
print(f"T = {T} returns, {dates[0]} -> {dates[-1]}, years = {years:.6f}, A = {A:.4f} (= 2363 x 365.25 / 3551)")
print(f"growth: 0050 x{np.prod(1 + R1):.4f}, 00679B x{np.prod(1 + R2):.4f}")
assert T == 2363
""")

md(r"""
## Part 2 — The case, statistics by year, and correlation at three frequencies

`est(mask)` returns annualized population moments and every two-asset quantity used in the module: the minimum-variance weight (7.7) and volatility (7.8), the multiplier $\lambda^*=2\sigma_{\min}^2$, the Kelly fractions (7.12), the tangency weights (7.10) and $\mathrm{SR}^*$ (7.11).
""")

code(r"""
def est(m, rf=RF):
    a, b = R1[m], R2[m]
    S = np.cov(np.vstack([a, b]), ddof=0) * A
    s1, s2, c = math.sqrt(S[0, 0]), math.sqrt(S[1, 1]), S[0, 1]
    sd2 = S[0, 0] + S[1, 1] - 2 * c                              # sigma_d^2 = Var(R1 - R2), annualized
    w = (S[1, 1] - c) / sd2
    vmin = (S[0, 0] * S[1, 1] - c * c) / sd2
    e = np.array([A * a.mean() - rf, A * b.mean() - rf])
    f = np.linalg.solve(S, e)                                    # Kelly fractions, eq. (7.12)
    sr = e / np.array([s1, s2]); rho = c / (s1 * s2)
    return dict(n=int(m.sum()), s1=s1, s2=s2, cov=c, rho=rho, w_mv=w, s_mv=math.sqrt(vmin), lam=2 * vmin, sd2=sd2,
                e1=e[0], e2=e[1], f1=f[0], f2=f[1], lev=f.sum(), wT1=f[0] / f.sum(),
                sr_star=math.sqrt((sr[0]**2 + sr[1]**2 - 2 * rho * sr[0] * sr[1]) / (1 - rho**2)),
                ret1=np.prod(1 + a) - 1, ret2=np.prod(1 + b) - 1, S=S)

E = {"full": est(ALL), "2017–2021": est(IS), "2022–2026": est(OOS)}
w_is = E["2017–2021"]["w_mv"]
vol = lambda x: math.sqrt(A * x.var())
mix = lambda w, m: w * R1[m] + (1 - w) * R2[m]
case = pl.DataFrame([{"window": k, "days": v["n"], "0050 return": v["ret1"], "00679B return": v["ret2"], "sigma_0050": v["s1"],
                      "sigma_00679B": v["s2"], "rho": v["rho"], "w_min_var": v["w_mv"], "sigma_min": v["s_mv"],
                      "vol of 42.3/57.7 mix": vol(mix(w_is, m))} for (k, v), m in zip(E.items(), (ALL, IS, OOS))])
case   # [[ex:case]]
""")

code(r"""
label = {2017: "2017 (from 17 Jan)", 2026: "2026 (to 8 Oct)"}
years_tbl = pl.DataFrame([{"year": label.get(y, str(y)), "days": int((yr == y).sum()), "0050": est(yr == y)["ret1"],
                           "00679B": est(yr == y)["ret2"], "sigma_0050": est(yr == y)["s1"], "sigma_00679B": est(yr == y)["s2"],
                           "rho": est(yr == y)["rho"], "w_min_var": est(yr == y)["w_mv"]} for y in range(2017, 2027)])
years_tbl   # [[ex:years]]
""")

code(r"""
# correlation at weekly and monthly frequency, and lead-lag at daily frequency
lev = idx.with_columns(pl.col("date").str.to_date())
for every in ("1w", "1mo"):
    w = lev.group_by_dynamic("date", every=every).agg(pl.col("I_0050").last(), pl.col("I_00679B").last()).sort("date")
    a = np.concatenate([[1.0], w["I_0050"].to_numpy()]); b = np.concatenate([[1.0], w["I_00679B"].to_numpy()])
    r1, r2 = a[1:] / a[:-1] - 1, b[1:] / b[:-1] - 1
    yy = w["date"].dt.year().to_numpy()
    print(f"{every:>3}: n={len(r1)}  2017-2021 {np.corrcoef(r1[yy <= 2021], r2[yy <= 2021])[0, 1]:+.2f}   2022-2026 {np.corrcoef(r1[yy >= 2022], r2[yy >= 2022])[0, 1]:+.2f}")
print(f"lead-lag: corr(R1_t, R2_t-1) = {np.corrcoef(R1[1:], R2[:-1])[0, 1]:+.3f}, corr(R1_t-1, R2_t) = {np.corrcoef(R1[:-1], R2[1:])[0, 1]:+.3f}")

roll = ret.select("date", pl.rolling_corr(pl.col("R1"), pl.col("R2"), window_size=243).alias("rho_243")).drop_nulls()
late = roll.filter(pl.col("date") >= pl.lit(date(2023, 1, 1)))
lo, hi = late.sort("rho_243").row(0), late.sort("rho_243").row(-1)
print(f"trailing 243-day correlation, windows ending from 2023: min {lo[1]:+.2f} on {lo[0]}, max {hi[1]:+.2f} on {hi[0]}")
fig, ax = plt.subplots()
ax.plot(roll["date"], roll["rho_243"], label="trailing 243-day correlation")
ax.axvspan(date(2022, 1, 1), date(2022, 12, 31), color="grey", alpha=0.15)
ax.hlines([E["2017–2021"]["rho"], E["2022–2026"]["rho"]], [date(2018, 1, 1), date(2022, 1, 3)], [date(2021, 12, 30), date(2026, 10, 8)],
          colors="tab:orange", linestyles="dashed", label="correlation over each full window")
ax.axhline(0, color="black", lw=0.8); ax.set_title("[[ex:rollcorr]]: trailing one-year correlation of daily returns"); ax.legend(); plt.show()
""")

md(r"""
## Part 3 — Partial derivatives, the covariance identities and a Taylor attribution

**[[eg:fx]].** $h(x,y)=(1+x)(1+y)-1$ with USD/TWD from 27.690 to 30.708 in 2022 (central-bank close via CNA).
**Section 2's identities.** For $R_p=w_1R_1+w_2R_2$: $\operatorname{Var}(R_p)=w_1^2\sigma_1^2+2w_1w_2\sigma_{12}+w_2^2\sigma_2^2$, $\operatorname{Cov}(R_1,R_p)=w_1\sigma_1^2+w_2\sigma_{12}$, $\operatorname{Var}(R_1-R_2)=\sigma_1^2+\sigma_2^2-2\sigma_{12}$; they hold exactly for sample moments.
**[[eg:marginal]].** Partial derivatives of $V(w_1,w_2)$ at 60/40 with full-sample moments.
**[[ex:attrib]].** First- and second-order Taylor terms of $V(\sigma_1,\sigma_2,\rho)=w_1^2\sigma_1^2+w_2^2\sigma_2^2+2w_1w_2\rho\sigma_1\sigma_2$ at fixed weights.
""")

code(r"""
r22 = est(yr == 2022)["ret2"]; y = 30.708 / 27.690 - 1; x = (1 + r22) / (1 + y) - 1
print(f"[[eg:fx]]: R_TWD {r22:.2%}, FX {y:.2%}, implied USD return {x:.2%}; h_x = {1 + y:.4f}, h_y = {1 + x:.4f}; "
      f"x + y = {x + y:.2%}, cross term {x * y:.2%}")

F = E["full"]; S = F["S"]; w = np.array([0.6, 0.4])
Rp = mix(0.6, ALL)
print("identities:", f"Var(Rp) {A * Rp.var():.6f} vs formula {w @ S @ w:.6f};",
      f"Cov(R1, Rp) {A * np.mean((R1 - R1.mean()) * (Rp - Rp.mean())):.6f} vs {(S @ w)[0]:.6f};",
      f"Var(R1 - R2) {A * (R1 - R2).var():.6f} vs {S[0, 0] + S[1, 1] - 2 * S[0, 1]:.6f}")
V = w @ S @ w; grad = 2 * S @ w
print(f"[[eg:marginal]]: V = {V:.6f}, sigma = {math.sqrt(V):.2%}, dV/dw = {grad.round(4)}, dsigma/dw = {(grad / (2 * math.sqrt(V))).round(3)}")
for step in (np.array([0.01, 0.0]), np.array([0.01, -0.01])):
    print(f"   step {step}: linear {grad @ step / (2 * math.sqrt(V)) * 100:.3f} pp, exact {(math.sqrt((w + step) @ S @ (w + step)) - math.sqrt(V)) * 100:.3f} pp")
""")

code(r"""
e0, e1 = E["2017–2021"], E["2022–2026"]
a, b, c = w_is**2, (1 - w_is)**2, 2 * w_is * (1 - w_is)
Vf = lambda s1, s2, r: a * s1**2 + b * s2**2 + c * r * s1 * s2
p0 = np.array([e0["s1"], e0["s2"], e0["rho"]]); d = np.array([e1["s1"], e1["s2"], e1["rho"]]) - p0
s1, s2, r = p0
grad = np.array([2 * a * s1 + c * r * s2, 2 * b * s2 + c * r * s1, c * s1 * s2])
H = np.array([[2 * a, c * r, c * s2], [c * r, 2 * b, c * s1], [c * s2, c * s1, 0.0]])
first = grad * d
exact = Vf(*(p0 + d)) - Vf(*p0)
print(f"weights {w_is:.3%} / {1 - w_is:.3%}; changes (decimal):", d.round(6), " partial derivatives at the start:", grad.round(6))
print("first-order terms (%^2):", (first * 1e4).round(2), " total", round(first.sum() * 1e4, 2))
print("second-order approximation (%^2):", round((first.sum() + 0.5 * d @ H @ d) * 1e4, 2), " exact:", round(exact * 1e4, 2))
print("third-order term (%^2):", round(c * d[0] * d[1] * d[2] * 1e4, 3), "  volatility", f"{math.sqrt(Vf(*p0)):.2%} -> {math.sqrt(Vf(*(p0 + d))):.2%}")
""")

md(r"""
## Part 4 — The growth function and its quadratic model ([[ex:taylor2]])

$g(f_1,f_2)=A\cdot\frac1T\sum_t\ln(1+r_f/A+f_1X_{1t}+f_2X_{2t})$ with $X_i=R_i-r_f/A$; the model (7.3) is $r_f+f_1e_1+f_2e_2-\tfrac12(f_1^2\sigma_1^2+2f_1f_2\sigma_{12}+f_2^2\sigma_2^2)$.

Where does the gap come from? Exactly, $A\cdot\overline{R_p-R_p^2/2}$ equals (7.3) minus the dropped squared daily mean $\tfrac12A\bar R_p^{\,2}$, so model − exact = squared mean − (third + fourth + higher-order terms of $\ln(1+R_p)$), with third $=A\,\overline{R_p^3}/3$ and fourth $=-A\,\overline{R_p^4}/4$.
""")

code(r"""
rd = RF / A                                                     # daily financing rate r_f/A
X = np.column_stack([R1, R2]) - rd

def g(f, m=ALL):
    return A * np.log1p(rd + X[m] @ np.asarray(f, float)).mean()

def g_model(f, e=F):
    f = np.asarray(f, float)
    return RF + f @ np.array([e["e1"], e["e2"]]) - 0.5 * f @ e["S"] @ f

def grad_hess(f, m=ALL):
    Xm = X[m]; wgt = 1 / (1 + rd + Xm @ np.asarray(f, float))
    return A * (Xm * wgt[:, None]).mean(0), -A * (Xm.T * wgt**2) @ Xm / len(Xm)

g0, H0 = grad_hess(np.zeros(2))
print("gradient at 0:", g0.round(4), " e =", np.round([F["e1"], F["e2"]], 4))
print("Hessian at 0:", H0.round(4).tolist(), " -Sigma =", (-F["S"]).round(4).tolist())

def terms(f):
    Rp = rd + X @ np.asarray(f, float)
    sq = A * Rp.mean()**2 / 2
    third, fourth = A * (Rp**3).mean() / 3, -A * (Rp**4).mean() / 4
    rest = g(f) - (g_model(f) - sq) - third - fourth
    return sq, third, fourth, rest

fstar = np.array([F["f1"], F["f2"]])
pts = {"0050 alone": (1, 0), "00679B alone": (0, 1), "min-var mix": (F["w_mv"], 1 - F["w_mv"]), "2 x 0050": (2, 0),
       "half Kelly": tuple(0.5 * fstar), "full Kelly (model)": tuple(fstar)}
rows = []
for k, v in pts.items():
    sq, t3, t4, t5 = terms(v)
    rows.append({"portfolio": k, "f1": v[0], "f2": v[1], "exact g": g(v), "model g": g_model(v),
                 "model - exact (bp)": (g_model(v) - g(v)) * 1e4, "squared mean (bp)": sq * 1e4,
                 "higher order (bp)": -(t3 + t4 + t5) * 1e4, "3rd (bp)": t3 * 1e4, "4th (bp)": t4 * 1e4, "5th+ (bp)": t5 * 1e4})
pl.DataFrame(rows)   # [[ex:taylor2]], with the gap split into the squared daily mean and higher-order terms
""")

code(r"""
cs = np.linspace(0, 1.6, 33)                                     # c = fraction of full Kelly (book-wide symbol)
fig, ax = plt.subplots()
ax.plot(cs, [g(c * fstar) for c in cs], label="exact sample growth")
ax.plot(cs, [g_model(c * fstar) for c in cs], "--", label="quadratic model (7.3)")
ax.axvline(0.5, color="grey", lw=0.8); ax.axvline(1.0, color="grey", lw=0.8)
ax.set_xlabel("fraction c of the model Kelly portfolio f* = (5.59, -0.52)"); ax.set_ylabel("annual log growth")
ax.set_title("Growth along the Kelly direction"); ax.legend(); plt.show()
worst = (rd + X @ fstar).min()
print(f"worst day at f*: {worst:.2%} on {dates[int(np.argmin(rd + X @ fstar))]}")
""")

md(r"""
## Part 5 — Classifying critical points ([[eg:classify]])
""")

code(r"""
import sympy as sp
xs, ys = sp.symbols("x y", real=True)
h = xs**3 - 3 * xs * ys + ys**3
crit = sp.solve([sp.diff(h, xs), sp.diff(h, ys)], [xs, ys], dict=True)
Hh = sp.hessian(h, (xs, ys))
for cp in crit:
    if all(v.is_real for v in cp.values()):
        Hc = Hh.subs(cp); D = Hc.det()
        kind = "saddle" if D < 0 else ("local min" if Hc[0, 0] > 0 else "local max") if D > 0 else "inconclusive"
        print(cp, " h =", h.subs(cp), " det H =", D, " ->", kind)
""")

md(r"""
## Part 6 — Lagrange multipliers, symbolically and numerically

**[[eg:split]]** (order split, illustrative $k_d=2$, $k_n=5$) and **[[eg:budget]]** (risk budget across two strategies, illustrative figures). Each multiplier is checked against the shadow-price identity (7.6) by re-solving with the constraint relaxed. The variance budget is an ellipse, so the Lagrange conditions have two solutions: $\pm\mathbf f$ with $\pm\lambda$.
""")

code(r"""
from scipy.optimize import minimize
xq, yq, lam, Q = sp.symbols("x y lambda Q", positive=True)
Lg = 2 * xq**2 + 5 * yq**2 - lam * (xq + yq - Q)
sol = sp.solve([sp.diff(Lg, v) for v in (xq, yq, lam)], [xq, yq, lam], dict=True)[0]
print("split:", {k: sp.simplify(v) for k, v in sol.items()}, " at Q=100:", {k: float(v.subs(Q, 100)) for k, v in sol.items()})
Cstar = sp.simplify((2 * xq**2 + 5 * yq**2).subs(sol))
print("C*(Q) =", Cstar, "  dC*/dQ at 100 =", float(sp.diff(Cstar, Q).subs(Q, 100)), "  C*(101)-C*(100) =", float(Cstar.subs(Q, 101) - Cstar.subs(Q, 100)))
print("integer split 71/29 cost:", 2 * 71**2 + 5 * 29**2, "   equal split:", 2 * 50**2 + 5 * 50**2)
""")

code(r"""
e = np.array([0.08, 0.03]); sd = np.array([0.16, 0.04]); rho_ = 0.2
Sg = np.array([[sd[0]**2, rho_ * sd[0] * sd[1]], [rho_ * sd[0] * sd[1], sd[1]**2]])
z = np.linalg.solve(Sg, e)                                       # direction Sigma^-1 e
for sgn in (1, -1):                                              # the two Lagrange candidates on the ellipse
    fc = sgn * 0.10 * z / math.sqrt(z @ Sg @ z)
    print(f"candidate {sgn:+d}: f = {fc.round(4)}, excess return {fc @ e:+.4%}, lambda = {(fc @ e) / (2 * 0.10**2):+.4f}")
def best(sigma_b):
    res = minimize(lambda f: -(f @ e), x0=[0.1, 1.0], method="SLSQP",
                   constraints=[{"type": "eq", "fun": lambda f: f @ Sg @ f - sigma_b**2}])
    return res.x, -res.fun
f10, E10 = best(0.10)
sr_star = math.sqrt(e @ z)
print(f"SLSQP maximum: exposures {f10.round(4)}, excess return {E10:.4%}, SR* = {sr_star:.4f}")
print(f"multiplier on the variance budget SR*/(2 sigma_b) = {sr_star / 0.2:.4f};  numerical dE*/d(sigma_b^2) = {(best(0.1001)[1] - best(0.0999)[1]) / (0.1001**2 - 0.0999**2):.4f}")
print(f"dE*/d sigma_b = {(best(0.11)[1] - E10) / 0.01:.4f}  (= SR*)")
""")

md(r"""
## Part 7 — Two-asset portfolios: minimum variance in and out of sample, tangency and Kelly
""")

code(r"""
e0, e1 = E["2017–2021"], E["2022–2026"]
realized = vol(mix(w_is, OOS))
print(f"[[eg:minvar]]: w* = {e0['w_mv']:.2%}, sigma_min = {e0['s_mv']:.2%}, lambda* = {e0['lam']:.4f}; realized in sample {vol(mix(w_is, IS)):.2%}")
print(f"out of sample: realized {realized:.2%}; ex-post w* = {e1['w_mv']:.2%} with {e1['s_mv']:.2%}; "
      f"sigma_d^2 = {e1['sd2']:.5f}, half the curvature V'' = 2 sigma_d^2 = {2 * e1['sd2']:.4f}")
pen = e1["sd2"] * (w_is - e1["w_mv"])**2
print(f"identity (7.9): {e1['s_mv']**2 * 1e4:.2f} + {pen * 1e4:.2f} = {(e1['s_mv']**2 + pen) * 1e4:.2f} %^2 vs realized^2 {realized**2 * 1e4:.2f}")
for dw in (0.05, 0.10):
    print(f"   weight error {dw:.2f}: +{(math.sqrt(e1['s_mv']**2 + e1['sd2'] * dw**2) - e1['s_mv']) * 100:.2f} pp")
env = 2 * e0["w_mv"] * (1 - e0["w_mv"]) * e0["s1"] * e0["s2"]
s1, s2, rr = e0["s1"], e0["s2"], e0["rho"] + 0.1
vb = (s1**2 * s2**2 - (rr * s1 * s2)**2) / (s1**2 + s2**2 - 2 * rr * s1 * s2)
print(f"envelope: d sigma_min^2/d rho = {env:.4f}; +0.1 -> predicted {0.1 * env:.5f}, exact {vb - e0['s_mv']**2:.5f}, sigma_min {math.sqrt(vb):.2%}")
""")

code(r"""
# [[ex:levels]]: level curves of portfolio volatility in the (w1, w2) plane, 2017-2021 estimates, and the budget line
S0 = e0["S"]
grid = np.linspace(-1.25, 1.25, 251)
w1_, w2_ = np.meshgrid(grid, grid)
sig_ = np.sqrt(S0[0, 0] * w1_**2 + 2 * S0[0, 1] * w1_ * w2_ + S0[1, 1] * w2_**2)
fig, ax = plt.subplots(figsize=(6, 6))
cl = ax.contour(w1_, w2_, sig_, levels=[e0["s_mv"], 0.12, 0.15], colors=["tab:blue", "tab:green", "tab:red"])
ax.clabel(cl, fmt=lambda v: f"{v:.2%}")
ax.plot([-0.25, 1.25], [1.25, -0.25], "--", color="grey", label="budget line w1 + w2 = 1")
ax.plot([e0["w_mv"]], [1 - e0["w_mv"]], "o", color="tab:blue", label="minimum variance")
ax.set_aspect("equal"); ax.set_xlabel("weight w1 in 0050"); ax.set_ylabel("weight w2 in 00679B")
ax.set_title("[[ex:levels]]: level curves of portfolio volatility"); ax.legend(loc="lower right"); plt.show()
# where the smallest ellipse touches the line, grad V is parallel to grad psi = (1, 1): both entries equal lambda*
gV = 2 * S0 @ np.array([e0["w_mv"], 1 - e0["w_mv"]])
print(f"minimum variance at w = ({e0['w_mv']:.1%}, {1 - e0['w_mv']:.1%}), volatility {e0['s_mv']:.2%}; "
      f"grad V there: {gV.round(6)}; lambda* = 2 sigma_min^2 = {e0['lam']:.6f}")
""")

code(r"""
ws = np.linspace(0, 1, 101)
vc = lambda e: np.sqrt(ws**2 * e["s1"]**2 + (1 - ws)**2 * e["s2"]**2 + 2 * ws * (1 - ws) * e["cov"])
fig, ax = plt.subplots()
ax.plot(ws, vc(e0), label="estimated on 2017-2021"); ax.plot(ws, vc(e1), label="realized in 2022-2026")
ax.plot([e0["w_mv"]], [e0["s_mv"]], "o", color="tab:blue"); ax.plot([e1["w_mv"]], [e1["s_mv"]], "o", color="tab:orange")
ax.plot([w_is], [realized], "o", color="tab:orange")
ax.set_xlabel("weight in 0050"); ax.set_ylabel("annualized volatility"); ax.set_title("[[ex:volcurve]]"); ax.legend(); plt.show()

W = lambda w: np.concatenate([[1.0], np.cumprod(1 + w * R1 + (1 - w) * R2)])
dts = [date.fromisoformat(BASE)] + dates
fig, ax = plt.subplots()
for w_, lab in ((1.0, "0050"), (w_is, "42/58 mix"), (0.0, "00679B")):
    ax.plot(dts, W(w_), label=f"{lab} (x{W(w_)[-1]:.2f})")
ax.set_yscale("log"); ax.axvline(date(2022, 1, 3), color="grey", lw=0.8); ax.set_title("Growth of one unit (log scale)"); ax.legend(); plt.show()
last_is = dates[int(np.flatnonzero(IS)[-1])]
yrs_oos = (dates[-1] - last_is).days / 365.25                   # calendar years, as AUTHORING 8 requires
cg = lambda x: np.prod(1 + x) ** (1 / yrs_oos) - 1
print(f"test window {last_is} -> {dates[-1]} = {yrs_oos:.2f} calendar years; compound growth a year: "
      f"mix {cg(mix(w_is, OOS)):.2%}, 0050 {cg(mix(1, OOS)):.2%}, 00679B {cg(mix(0, OOS)):.2%}")
""")

code(r"""
kelly = pl.DataFrame([{"window": k, "e1": v["e1"], "e2": v["e2"], "s1": v["s1"], "s2": v["s2"], "rho": v["rho"], "f1": v["f1"], "f2": v["f2"],
                       "L": v["lev"], "wtan_0050": v["wT1"], "SR*": v["sr_star"]} for k, v in E.items()])
print(f"[[eg:kellyeg]]: det = {np.linalg.det(F['S']):.4e}; g* (model) = {RF + 0.5 * F['sr_star']**2:.2%}; exact g at f* = {g(fstar):.2%}")
yd = (last_is - date.fromisoformat(BASE)).days / 365.25          # calendar years of the estimation window (4.95)
print(f"standard error of the 2017-2021 mean over {yd:.2f} years: 0050 {e0['s1'] / math.sqrt(yd):.2%} against a mean of "
      f"{A * R1[IS].mean():.1%}; 00679B {e0['s2'] / math.sqrt(yd):.2%} against {A * R2[IS].mean():.1%}")
kelly   # [[ex:kelly]] (in-sample; not recommendations)
""")

md(r"""
## Part 8 — KKT: equity floor and leverage cap ([[eg:cap]], [[ex:kkt]])

The cap $f_1+f_2\le2$ limits **net** exposure; it equals gross exposure $\lvert f_1\rvert+\lvert f_2\rvert$ only when both positions are long. With three constraints there are eight possible binding sets; all three cannot bind at once ($f_1=f_2=0$ breaks $f_1+f_2=2$), which leaves seven.
""")

code(r"""
# knowledge check of Section 7: minimum variance with w1 >= 0.6 (full sample)
Vw = lambda w: w * w * S[0, 0] + (1 - w)**2 * S[1, 1] + 2 * w * (1 - w) * S[0, 1]
dV = 2 * S @ np.array([0.6, 0.4]); nu = dV[0] - dV[1]
print(f"floor binds (w* = {F['w_mv']:.1%}); nu = {nu:.4f}; vol {math.sqrt(Vw(0.6)):.2%} vs unconstrained {F['s_mv']:.2%}; "
      f"floor at 59%: dV predicted {-0.01 * nu:.6f}, exact {Vw(0.59) - Vw(0.6):.6f}")

# [[eg:cap]]: enumerate every binding set for max g_model s.t. f1 + f2 <= 2 (nu_c), -f1 <= 0 (nu_1), -f2 <= 0 (nu_2)
ev = np.array([F["e1"], F["e2"]]); cap = 2.0
cons = {"cap": (np.array([1.0, 1.0]), cap), "f1>=0": (np.array([-1.0, 0.0]), 0.0), "f2>=0": (np.array([0.0, -1.0]), 0.0)}
name = {"cap": "nu_c", "f1>=0": "nu_1", "f2>=0": "nu_2"}
rows = []
for act in [(), ("cap",), ("f2>=0",), ("f1>=0",), ("cap", "f2>=0"), ("cap", "f1>=0"), ("f1>=0", "f2>=0"), ("cap", "f1>=0", "f2>=0")]:
    Aa = np.array([cons[c][0] for c in act]).reshape(len(act), 2)
    if np.linalg.matrix_rank(Aa) < len(act):
        print("binding set", act, "is inconsistent"); continue
    M = np.block([[S, Aa.T], [Aa, np.zeros((len(act), len(act)))]])
    sol = np.linalg.solve(M, np.concatenate([ev, [cons[c][1] for c in act]]))   # stationarity + binding constraints
    f, nus = sol[:2], sol[2:]
    rows.append({"binding": " and ".join(act) or "none", "f1": f[0], "f2": f[1],
                 "multipliers": ", ".join(f"{name[c]} = {v:.3f}" for c, v in zip(act, nus)) or "—",
                 "feasible": bool(f.sum() <= cap + 1e-9 and (f >= -1e-9).all()),
                 "multipliers >= 0": bool((nus >= -1e-12).all()), "gross exposure": float(abs(f).sum()), "model growth": g_model(f)})
kkt = pl.DataFrame(rows)
kkt   # [[ex:kkt]]
""")

code(r"""
gm = lambda f: g_model(np.asarray(f, float))
gr20 = ev - S @ np.array([2.0, 0.0])
nu_c, nu_2 = gr20[0], gr20[0] - gr20[1]
print(f"at (2, 0): nu_c = {nu_c:.4f}, nu_2 = {nu_2:.4f}, g_f2 = {gr20[1]:.4f}")
# the shadow price is a first-order value: exact model gains of a larger cap (the optimum stays at (cap, 0) up to 3)
for c_ in (2.1, 3.0):
    gc = ev - S @ np.array([c_, 0.0])
    assert gc[0] > 0 and gc[0] - gc[1] > 0                          # (c_, 0) still satisfies KKT
    print(f"   cap {c_}: optimum ({c_}, 0), exact model gain {(gm((c_, 0)) - gm((2, 0))) * 100:.2f} pp vs {nu_c * (c_ - 2) * 100:.2f} at first order")
print(f"net cap, f2 >= -0.01: (2.01, -0.01) gains {(gm((2.01, -0.01)) - gm((2, 0))) * 100:.4f} pp (0.01 x nu_2 = {0.01 * nu_2 * 100:.4f}); "
      f"the extra 0050 alone adds {(gm((2.01, 0)) - gm((2, 0))) * 100:.4f}, the short alone {(gm((2, -0.01)) - gm((2, 0))) * 100:.4f}")
print(f"gross cap |f1| + |f2| <= 2: (1.99, -0.01) changes growth by {(gm((1.99, -0.01)) - gm((2, 0))) * 100:+.3f} pp")
t = np.linspace(0, 1, 20001)                                     # the model's maximum on the gross-cap diamond
P = np.vstack([np.column_stack([2 * t, 2 * (1 - t)]), np.column_stack([2 * t, -2 * (1 - t)]),
               np.column_stack([-2 * t, 2 * (1 - t)]), np.column_stack([-2 * t, -2 * (1 - t)])])
gv = RF + P @ ev - 0.5 * np.einsum("ij,jk,ik->i", P, S, P)
print("gross-cap optimum:", P[int(np.argmax(gv))].round(4))

def kelly_capped(cap, fun=g):
    res = minimize(lambda f: -fun(f), x0=[0.5, 0.5], method="SLSQP", bounds=[(0, None), (0, None)],
                   constraints=[{"type": "ineq", "fun": lambda f: cap - f.sum()}])
    return res.x, -res.fun
for nm, fun in (("model", g_model), ("exact", g)):
    x2, g2 = kelly_capped(2.0, fun)
    nu_cap = (kelly_capped(2.01, fun)[1] - kelly_capped(1.99, fun)[1]) / 0.02
    print(f"{nm:5s}: f = {x2.round(4)}, growth {g2:.4%}, shadow price of the cap {nu_cap:.4f}")
""")

md(r"""
## Part 9 — Numerical derivatives, Newton's method and gradient ascent ([[ex:converge]])

The shortfall $g^*-g(\mathbf f_k)$ is computed as $A\cdot\overline{\ln\big((1+u^*)/(1+u_k)\big)}$, which does not subtract two nearly equal growth rates. Shortfalls below $10^{-10}$ are not shown: far smaller values approach the rounding error of the computed growth rate.
""")

code(r"""
def num_grad(fun, x, d=1e-5):
    E_ = np.eye(len(x)); return np.array([(fun(x + d * E_[i]) - fun(x - d * E_[i])) / (2 * d) for i in range(len(x))])

def num_hess(fun, x, d=1e-4):
    E_, n = np.eye(len(x)), len(x)
    return np.array([[(fun(x + d*E_[i] + d*E_[j]) - fun(x + d*E_[i] - d*E_[j])
                       - fun(x - d*E_[i] + d*E_[j]) + fun(x - d*E_[i] - d*E_[j])) / (4 * d * d) for j in range(n)] for i in range(n)])

print("numerical gradient at 0:", num_grad(g, np.zeros(2)).round(4), "  numerical Hessian at 0:", num_hess(g, np.zeros(2)).round(4).tolist())
f = np.zeros(2); nt = [f.copy()]
for k in range(5):
    gr, Hh = grad_hess(f); f = f + np.linalg.solve(Hh, -gr); nt.append(f.copy())
fopt = nt[-1]; gopt = g(fopt)

def shortfall(f):
    du = X @ (fopt - np.asarray(f, float)); u = rd + X @ np.asarray(f, float)
    return A * np.log1p(du / (1 + u)).mean()

print("Newton path:", [tuple(float(v) for v in p.round(4)) for p in nt[:5]], f" g* = {gopt:.4%}")
print("numerical gradient at the optimum:", num_grad(g, fopt).round(8))
S_eig = np.linalg.eigvalsh(F["S"])
tr, det = F["S"][0, 0] + F["S"][1, 1], np.linalg.det(F["S"])
print("smallest and largest curvature m, M:", S_eig.round(5), "= roots of x^2 - (s1^2 + s2^2) x + det:",
      np.round([(tr - math.sqrt(tr**2 - 4 * det)) / 2, (tr + math.sqrt(tr**2 - 4 * det)) / 2], 5))
alpha_ = 2 / S_eig.sum()                                         # alpha = 2 / (m + M), about 34.1
f = np.zeros(2); ga = [shortfall(f)]
for k in range(60):
    f = f + alpha_ * grad_hess(f)[0]; ga.append(shortfall(f))
nt_gap = [shortfall(p) for p in nt]
first_below = lambda seq, tol: next(i for i, v in enumerate(seq) if v < tol)
print(f"kappa {S_eig[1] / S_eig[0]:.3f}, alpha {alpha_:.4f}, model factor {(S_eig[1] - S_eig[0]) / S_eig.sum():.2f}; "
      f"curvatures at the optimum {np.linalg.eigvalsh(-grad_hess(fopt)[1]).round(4)}")
print(f"iterations to 1e-6: GA {first_below(ga, 1e-6)}, Newton {first_below(nt_gap, 1e-6)};  to 1e-10: GA {first_below(ga, 1e-10)}, Newton {first_below(nt_gap, 1e-10)}")
print("Newton shortfalls above the floor:", [f"{v:.1e}" for v in nt_gap if v >= 1e-10])
print(f"worst day at the exact optimum: {(rd + X @ fopt).min():.2%}")
FLOOR = 1e-10
def to_floor(seq):
    out = []
    for v in seq:
        out.append(max(v, FLOOR))
        if v < FLOOR: break
    return out
fig, ax = plt.subplots()
ga_p, nt_p = to_floor(ga), to_floor(nt_gap)
ax.semilogy(range(len(ga_p)), ga_p, label="gradient ascent, fixed step")
ax.semilogy(range(len(nt_p)), nt_p, "o-", label="Newton")
ax.set_ylim(FLOOR, 1); ax.set_xlabel("iteration"); ax.set_title("[[ex:converge]]: growth shortfall (series end below 1e-10)"); ax.legend(); plt.show()
""")

md(r"""
## Part 10 — Practice-problem solutions (computational)
""")

code(r"""
def two(s1, s2, rho, e1=None, e2=None):
    c = rho * s1 * s2; sd2 = s1**2 + s2**2 - 2 * c
    out = {"w*": (s2**2 - c) / sd2, "sigma_min": math.sqrt((s1**2 * s2**2 - c * c) / sd2)}
    if e1 is not None:
        det = s1**2 * s2**2 - c * c; f1, f2 = (s2**2 * e1 - c * e2) / det, (s1**2 * e2 - c * e1) / det
        sr1, sr2 = e1 / s1, e2 / s2
        out.update(f1=f1, f2=f2, L=f1 + f2, wtan1=f1 / (f1 + f2), SR=math.sqrt((sr1**2 + sr2**2 - 2 * rho * sr1 * sr2) / (1 - rho**2)))
    return out

print("PP2 ", f"exact {0.95 * 1.03 - 1:.2%}, linear {-0.02:.2%}, cross {-0.05 * 0.03:.2%}, at 4%: {0.95 * 1.04 - 1:.2%}")
print("PP3 ", f"second-order {0.05 - 0.3**2 / 8:.4%}, exact {math.sqrt(1.2 * 0.9) - 1:.4%}")
print("PP4 ", [(p, p[0]**3 + p[1]**3 - 3 * p[0] - 12 * p[1] + 20, 36 * p[0] * p[1]) for p in ((1, 2), (-1, -2), (1, -2), (-1, 2))])
print("PP5 ", f"lambda* x db = {0.02 * 0.05:.4f}, exact {(1.05**2 - 1) * 0.01:.6f}; "
      f"distractors: B = 2 x 0.02 x 0.05 = {2 * 0.02 * 0.05:.4f} (lambda* read as sigma_min^2), C = 0.01 x 0.05 = {0.01 * 0.05:.4f}")
print("PP7/8", {k: round(v, 4) for k, v in two(0.20, 0.08, 0.25, 0.06, 0.02).items()}, f"g* = {0.02 + 0.5 * two(0.20, 0.08, 0.25, 0.06, 0.02)['SR']**2:.2%}")
p9 = two(0.20, 0.40, 0.95); c9 = 0.95 * 0.2 * 0.4
print("PP9 ", {k: round(v, 4) for k, v in p9.items()}, f"nu at w=1: {2 * (c9 - 0.04):.4f}")
g10 = lambda a, b: 0.10 * a + 0.04 * b - 0.5 * (0.04 * a * a + 0.01 * b * b)   # excess growth, rho = 0
for cap10 in (2.0, 3.0):
    f1c = (0.10 - 0.04 + 0.01 * cap10) / (0.04 + 0.01)
    print("PP10", f"cap {cap10}: ({f1c:.2f}, {cap10 - f1c:.2f}), nu_c = {0.10 - 0.04 * f1c:.3f}, excess growth {g10(f1c, cap10 - f1c):.2%}")
print("PP10", f"unconstrained (2.5, 4): {g10(2.5, 4):.2%}; raising the cap from 2 to 3 adds {(g10(1.8, 1.2) - g10(1.6, 0.4)) * 100:.2f} points")
""")

code(r"""
# PP12: walk-forward, each year's minimum-variance weight held, rebalanced daily, through the following year,
# against a 50/50 mix also rebalanced daily and each year's own (ex-post) minimum-variance weight
rows = []
for y in range(2018, 2027):
    w_prev = est(yr == y - 1)["w_mv"]; cur = yr == y
    rows.append({"year": y, "w_prev": w_prev, "vol_prev_w": vol(mix(w_prev, cur)), "vol_50_50": vol(mix(0.5, cur)),
                 "vol_best": est(cur)["s_mv"]})
wf = pl.DataFrame(rows).with_columns((pl.col("vol_prev_w") < pl.col("vol_50_50")).alias("beats_50_50"))
print("years beating 50/50:", wf["beats_50_50"].sum(), "of", wf.height,
      "| simple averages of the nine annual volatilities:", {c: f"{wf[c].mean():.2%}" for c in ("vol_prev_w", "vol_50_50", "vol_best")})
r20 = wf.filter(pl.col("year") == 2020).row(0, named=True)
print(f"2020: {r20['vol_prev_w']:.3%} against {r20['vol_50_50']:.3%} for 50/50")
wf
""")

md(r"""
### Extension: how long should the estimation window be?

Practice Problem 12 re-estimated the weight once a year from the previous calendar year. Generalize it. For estimation windows of 6, 12, 24 and 36 months, re-estimate the minimum-variance weight at the end of every month and hold it for the next month, computing returns daily. Compare the out-of-sample volatility of each rule with the 50/50 mix and with the full-sample weight (which uses future data). Then repeat with weekly instead of daily returns for estimation. Which window and which frequency would you have chosen, and how much of the gap to perfect foresight does each close? LM35 returns to this question with shrinkage estimators.
""")

code(r"""
# starter: month-end rebalancing dates and a helper for one estimation window
month_ends = ret.group_by_dynamic("date", every="1mo").agg(pl.col("date").last().alias("d"))["d"].to_list()
def min_var_weight(mask):
    return est(mask)["w_mv"]
# for i, d in enumerate(month_ends[12:-1], start=12): ...  (your code)
""")

nb = nbf.v4.new_notebook(); nb["cells"] = cells
nb["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                  "language_info": {"name": "python"}}
nbf.write(nb, LAB / "LM07_lab.ipynb")

(LAB / "README.md").write_text("""# LM7 Lab — Multivariable Calculus and Lagrange Multipliers

Companion to *From Calculus to Kelly*, Learning Module 7. The notebook builds the total-return series of 0050 and 00679B (all 37 00679B ex-dates, the 0050 split), reproduces the module's exhibits and computational examples, and works the computational practice problems.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM07_lab/LM07_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM07_lab.ipynb
```

`build/make_lab07.py` generates the notebook and this README: edit the generator, not the generated files.

## Data (FinMind, as retrieved 2026-10-10; not in the repository)

The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

The same steps in a shell (`data/raw/` and this folder's `data/` are git-ignored):

```bash
export FINMIND_TOKEN=...               # your FinMind API token
uv run python data/fetch_finmind.py    # rebuilds and verifies data/raw/
uv run python data/make_lab_data.py    # writes every lab's data/ folder
```

`fetch_finmind.py` checks every file against `data/raw_manifest.json`. The notebook reads only the files in its own `data/` folder, which then holds:

| File | Content |
|:--|:--|
| `data/0050_daily_raw.csv` | 0050 daily close and FinMind `spread`, 2014-10-31 → 2026-10-08 (unadjusted) |
| `data/00679B_daily_raw.csv` | 00679B daily close and `spread`, 2017-01-17 → 2026-10-08 (unadjusted) |
| `data/0050_dividends.csv` | 0050 ex-dividend dates, before/after prices and cash dividends (`TaiwanStockDividendResult`) |
| `data/00679B_dividends.csv` | 00679B ex-dividend dates (37 quarterly distributions in the window) |

Every close was verified against FinMind's own `spread` column (close − previous close). The only mismatches are ex-dividend days (spread printed as 0) and 0050's 4-for-1 split on 2025-06-18. Two 00679B ex-dates (2019-03-05 and 2025-08-21) had an unchanged close and therefore show no mismatch; their dividends are still applied, and Part 1 checks that the previous close equals FinMind's `before_price` on every ex-date. 0050 was halted 2025-06-11..17 for its split while 00679B traded, so returns are taken between consecutive common trading dates.

00679B tracks the ICE US Treasury 20+ Year Bond Index and is quoted in New Taiwan dollars without a currency hedge, so its returns include USD/TWD moves.
""", encoding="utf-8", newline="\n")
print("wrote", LAB / "LM07_lab.ipynb", "and README.md | labels:", {k: ("X" if w == "Exhibit" else "E") + str(n) for k, (w, n) in NUM.items()})
