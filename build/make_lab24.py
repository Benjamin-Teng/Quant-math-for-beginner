"""Generate labs/LM24_lab (Polars-first notebook + README) for LM24, Bayesian Inference and Shrinkage.

Run:  uv run python build/make_lab24.py
Then execute from inside the lab folder:
      cd labs/LM24_lab && uv run jupyter nbconvert --to notebook --execute --inplace LM24_lab.ipynb

The notebook reads only the files in labs/LM24_lab/data/ (taiex_tr.csv, sectors_close_raw.csv and
sectors_close_repairs.csv), which data/make_lab_data.py builds from data/raw/ (FinMind's licence keeps raw data out of
the repository). This script writes the notebook and the README only.

Exhibit and example numbers are never typed by hand: cells write [[ex:label]] / [[eg:label]], and the generator
resolves them from the labels in src/lm24.md, numbered in document order as build/build.py does. Other modules are
written LM20, LM21, never as links.
"""
import re
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "LM24_lab"
LAB.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- exhibit / example numbers from the module's labels
NUM: dict[str, tuple[str, int]] = {}
_count = {"exhibit": 0, "example": 0}
for m in re.finditer(r"(?m)^(?:>\s?)+\[!(exhibit|example)\][+-]?\s*(.*)$", (ROOT / "src" / "lm24.md").read_text(encoding="utf-8")):
    _count[m.group(1)] += 1
    lab = re.search(r"\{#([\w-]+)\}\s*$", m.group(2))
    if lab:
        NUM[lab.group(1)] = ("Exhibit" if m.group(1) == "exhibit" else "Example", _count[m.group(1)])


def refs(s: str) -> str:
    """Replace [[ex:a]] and [[eg:a]] by 'Exhibit k' and 'Example k', checking the kind."""
    def rep(m: re.Match[str]) -> str:
        kind, a = m.group(1), m.group(2)
        word, k = NUM[a]
        assert word == ("Exhibit" if kind == "ex" else "Example"), (kind, a)
        return f"{word} {k}"
    out = re.sub(r"\[\[(ex|eg):([\w-]+)\]\]", rep, s)
    assert not re.search(r"\[\[(ex|eg):", out) and "[[LM" not in out, out
    return out


cells: list = []


def md(s: str) -> None:
    cells.append(nbf.v4.new_markdown_cell(refs(s.strip("\n"))))


def code(s: str) -> None:
    cells.append(nbf.v4.new_code_cell(refs(s.strip("\n"))))


md(r"""
# LM24 Lab — Bayesian Inference and Shrinkage

Companion notebook to **From Calculus to Kelly, LM24**. It rebuilds the module's exhibits and computational examples from the closes of the TAIEX total-return index and of the TWSE sector indices, runs Experiments 1 and 2, solves the computational practice problems, and ends with an extension exercise.

| Part | Rebuilds |
|:--|:--|
| 1 | Data: TR23's returns, $T$, years, $A$, $\bar R$, $s$; the sector closes with the repair cell, U28 and its halves |
| 2 | The beta–binomial update with `stats.beta` and exact `Fraction`s: [[eg:sceptic]], [[eg:flat]], [[ex:manager]] |
| 3 | The normal mean: a `posterior` function, [[eg:taiexpost]], [[eg:split]], [[ex:normal]], [[ex:priors]] |
| 4 | Credible intervals and $\Pr(\mu\le0\mid\text{data})$: [[eg:credible]] |
| 5 | A `james_stein` function with `ddof` passed; Experiment 1 ([[eg:exp1]]) |
| 6 | U28's halves: [[ex:case]], [[eg:halves]], [[ex:forest]], [[ex:oos]], [[eg:reverse]] |
| 7 | The Bayes Kelly fraction with `brentq` on shifted returns: [[eg:bayeskelly]], [[eg:sceptics]], [[ex:kelly]] |
| 8 | Practice problems 9–12, and an extension: estimating on one third of U28 and judging on the next |

**Environment.** From the repository root, `uv sync` installs the locked Python environment (`uv.lock`). Open this notebook with the `.venv` kernel, or run `uv run --with jupyterlab jupyter lab`.

**Data.** The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

`data/` then holds `taiex_tr.csv` (`date`, `price`: the daily closes of the TAIEX total-return index, FinMind `TaiwanStockTotalReturnIndex`, data_id TAIEX, 2 January 2003 to 8 October 2026), `sectors_close_raw.csv` (the closes FinMind's `TaiwanStockPrice` serves for TAIEX and the 30 TWSE sector indices, one column per series, empty where a series has no close) and `sectors_close_repairs.csv` (each of the 561 closes that FinMind copied from another date or series, with its official 13:30:00 value from `TaiwanStockEvery5SecondsIndex`). The notebook reads nothing outside `data/`.

**Conventions (as in the module).** TR23: $T=5{,}849$ simple daily returns of the total-return index from 3 January 2003; years are calendar days / 365.25 and $A=T/\text{years}$. U28: the 28 leaf sector *price* indices (no dividends), closes 2008-12-01 to 2026-10-08, $T=4{,}382$ returns, $A=245.4794$ for both of LM11's halves (2,191 returns each: 2 December 2008 to 6 October 2017 and 11 October 2017 to 8 October 2026). Moments divide by the returns used (`ddof=0`); the cross-sectional SD of 28 means divides by 28. Every interval uses $\Phi^{-1}(0.975)$. TR23's posteriors are in-sample; the split-half results are out-of-sample; the reverse direction and the extension are stability checks; the Kelly results and Experiments 1 and 2 are model results; LM13's manager is hypothetical.
""")

code(r"""
from fractions import Fraction
from math import comb, sqrt
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from scipy import optimize, stats

DATA = Path("data")
EPS = 1e-12
SEED = 20261011
Z975 = stats.norm.ppf(0.975)
pl.Config.set_tbl_rows(40)
plt.rcParams.update({"figure.figsize": (9, 4.5), "axes.grid": True, "grid.alpha": 0.3,
                     "axes.spines.top": False, "axes.spines.right": False})
""")

md(r"""
## Part 1 — Data

TR23 first: returns between consecutive closes of the total-return index.
""")

code(r"""
tr_df = pl.read_csv(DATA / "taiex_tr.csv", schema_overrides={"price": pl.Float64}).sort("date")
tr = tr_df["price"].to_numpy()
R = tr[1:] / tr[:-1] - 1
T = len(R)
d0, d1 = pl.Series([tr_df["date"][0], tr_df["date"][-1]]).str.to_date().to_list()
years = (d1 - d0).days / 365.25
A = T / years
Rbar, s, s_u = R.mean(), R.std(ddof=0), R.std(ddof=1)
se = s / sqrt(T)                         # LM20's (20.2), daily
fhat = Rbar / s**2                       # LM20's plug-in Kelly fraction


def show(label, value, fmt, printed):
    # print a value next to the module's printed value and assert that they agree
    got = format(value, fmt)
    print(f"{label}: {got}   [book: {printed}]")
    assert got == printed, (label, got, printed)


show("T", T, ",", "5,849")
show("years", years, ".2f", "23.76")
show("A", A, ".2f", "246.12")
show("A Rbar (%, LM19's)", 100 * A * Rbar, ".2f", "15.38")
show("sqrt(A) s (%, LM19's)", 100 * sqrt(A) * s, ".2f", "18.96")
show("SE of the annual mean (points, LM20's)", 100 * A * se, ".2f", "3.89")
show("fhat (LM20's)", fhat, ".2f", "4.28")
""")

md(r"""
### The sector closes and the repair cell

FinMind's `TaiwanStockPrice` serves the sector indices with some rows copied from another date, or from another series on the same date (PITFALLS §3 of the repository). The book replaces each of these 561 closes with the official 13:30:00 value, as in LM16's lab. On FinMind's free plan the 13:30:00 values are not available (`TaiwanStockEvery5SecondsIndex` is a paid dataset), so `close_1330` is empty and the cell **drops** those closes instead: a dropped close removes the returns into and out of its date, the sample shrinks from 4,382 returns, and the halves are then taken by date. Nothing is ever estimated.
""")

code(r"""
raw = pl.read_csv(DATA / "sectors_close_raw.csv", infer_schema_length=None).sort("date")
rep = pl.read_csv(DATA / "sectors_close_repairs.csv", infer_schema_length=None,
                  schema_overrides={"close_1330": pl.Float64})
series = [c for c in raw.columns if c != "date"]
fixed = raw
for sid in rep["id"].unique(maintain_order=True).to_list():
    g = rep.filter(pl.col("id") == pl.lit(sid)).select("date", pl.col("close_1330").alias("_new"),
                                                        pl.lit(True).alias("_listed"))
    fixed = (fixed.join(g, on="date", how="left").sort("date")
                  .with_columns(pl.when(pl.col("_listed")).then(pl.col("_new")).otherwise(pl.col(sid)).alias(sid))
                  .drop("_new", "_listed"))
FULL_DATA = int(rep["close_1330"].is_not_null().sum()) == rep.height
AGGREGATES = ["Electronic", "ChemicalBiotechnologyMedicalCare"]
U28 = [c for c in series if c not in ("TAIEX", *AGGREGATES)]
FIRST_CLOSE, LAST_CLOSE = "2008-12-01", "2026-10-08"
closes = fixed.filter(pl.col("date").is_between(pl.lit(FIRST_CLOSE), pl.lit(LAST_CLOSE))).sort("date")
ret = closes.with_columns([(pl.col(c) / pl.col(c).shift(1) - 1).alias(c) for c in series]).slice(1)
smp = ret.filter(pl.all_horizontal([pl.col(c).is_not_null() for c in ["TAIEX", *U28]]))
T28, N = smp.height, len(U28)
years28 = (np.datetime64(LAST_CLOSE) - np.datetime64(FIRST_CLOSE)).astype(int) / 365.25
A28 = T28 / years28
first = smp.filter(pl.col("date") <= pl.lit("2017-10-06"))
second = smp.filter(pl.col("date") >= pl.lit("2017-10-11"))
X1, X2 = first.select(U28).to_numpy(), second.select(U28).to_numpy()
TX1, TX2 = first["TAIEX"].to_numpy(), second["TAIEX"].to_numpy()   # the TAIEX price index (no dividends)
print(f"every listed close repaired: {FULL_DATA}; U28: T = {T28}, N = {N}, A = {A28:.4f}; "
      f"halves {len(X1)} + {len(X2)}")


def show28(label, value, fmt, printed):
    # U28 numbers: assert only when every close is repaired (on the free plan the sample is smaller)
    got = format(value, fmt)
    note = "" if got == printed else ("   (differs: closes were dropped)" if not FULL_DATA else "   MISMATCH")
    print(f"{label}: {got}   [book: {printed}]{note}")
    if FULL_DATA:
        assert got == printed, (label, got, printed)


show28("T (U28)", T28, ",", "4,382")
show28("A (U28)", A28, ".4f", "245.4794")
show28("first half", len(X1), ",", "2,191")
""")

md(r"""
## Part 2 — The beta–binomial update

A $\operatorname{Beta}(\alpha_0,\beta_0)$ prior and $j$ good months in $n$ give $\operatorname{Beta}(\alpha_0+j,\beta_0+n-j)$, (24.2). For integer parameters, $\Pr(\theta\le x)$ is the chance of at least $\alpha_0$ successes in $\alpha_0+\beta_0-1$ trials with probability $x$, so `Fraction` gives exact probabilities; `stats.beta` checks them.
""")

code(r"""
def beta_sf_exact(a, b, x):
    # Pr(Beta(a, b) > x) for integer a, b: fewer than a successes in a + b - 1 trials
    n = a + b - 1
    return sum(Fraction(comb(n, k)) * x**k * (1 - x) ** (n - k) for k in range(a))


P55 = Fraction(11, 20)
a_root = optimize.brentq(lambda a: stats.beta.sf(0.55, a, a) - 0.10, 1, 1000)
show("a with 10% of managers at theta >= 0.55", a_root, ".2f", "81.96")
show("Beta(82, 82): share at theta >= 0.55 (%)", 100 * float(beta_sf_exact(82, 82, P55)), ".1f", "10.0")
show("Beta(82, 82): SD", stats.beta.std(82, 82), ".3f", "0.039")

# [[eg:sceptic]]: 8 good months of 12 under the sceptic's prior
p_sc = beta_sf_exact(90, 86, P55)
assert abs(float(p_sc) - stats.beta.sf(0.55, 90, 86)) < 1e-12
show("[[eg:sceptic]] posterior mean", 90 / 176, ".4f", "0.5114")
show("   data's weight c = 12/176", 12 / 176, ".3f", "0.068")
show("   Pr(theta >= 0.55 | record) (%)", 100 * float(p_sc), ".1f", "15.3")

# [[eg:flat]]: the flat prior Beta(1, 1)
p_half, p_55 = beta_sf_exact(9, 5, Fraction(1, 2)), beta_sf_exact(9, 5, P55)
print("Pr(theta > 0.5) =", p_half)
show("[[eg:flat]] Pr(theta > 0.5) (%)", 100 * float(p_half), ".1f", "86.7")
show("   Pr(theta >= 0.55) (%)", 100 * float(p_55), ".1f", "77.2")
show("   2.5% quantile", stats.beta.ppf(0.025, 9, 5), ".2f", "0.39")
show("   97.5% quantile", stats.beta.ppf(0.975, 9, 5), ".2f", "0.86")
n_need = next(n for n in range(3, 600, 3) if beta_sf_exact(82 + 2 * n // 3, 82 + n // 3, P55) > Fraction(1, 2))
show("   months of two good in three", n_need, "d", "72")
show("   Pr at 72 months (%)", 100 * float(beta_sf_exact(82 + 48, 82 + 24, P55)), ".1f", "51.2")
show("   Pr at 69 months (%)", 100 * float(beta_sf_exact(82 + 46, 82 + 23, P55)), ".1f", "49.4")
""")

code(r"""
th = np.linspace(0.25, 0.95, 281)
fig, ax = plt.subplots()
ax.plot(th, stats.beta.pdf(th, 82, 82), "--", label="Sceptic's prior Beta(82, 82)")
ax.plot(th, stats.beta.pdf(th, 90, 86), label="Sceptic's posterior Beta(90, 86)")
ax.plot(th, stats.beta.pdf(th, 9, 5), label="Flat prior's posterior Beta(9, 5)")
for x in (0.5, 0.55):
    ax.axvline(x, color="grey", ls=":")
ax.set(xlabel="monthly chance theta", ylabel="density", title="[[ex:manager]]")
ax.legend(); plt.show()
""")

md(r"""
## Part 3 — The normal mean with known variance

(24.3) on the annual scale: a prior SD of $A\sigma_0$ points on the annual mean against the standard error $As/\sqrt T$ = 3.89 points.
""")

code(r"""
def weight(a_sigma0):
    # the data's weight c for a prior SD a_sigma0 on the annual mean (0.10 = 10 points)
    s0 = a_sigma0 / A
    return s0**2 / (s0**2 + se**2)


def posterior(c, a_mu0=0.0):
    # posterior mean and SD of the annual mean, (24.3), for the data's weight c and prior mean a_mu0 (annual)
    mu0 = a_mu0 / A
    return A * (mu0 + c * (Rbar - mu0)), A * sqrt(c) * se


c10 = weight(0.10)
m10, sd10 = posterior(c10)
show("[[eg:taiexpost]] c at 10 points", c10, ".3f", "0.869")
show("   posterior mean (%)", 100 * m10, ".1f", "13.4")
show("   posterior SD (points)", 100 * sd10, ".1f", "3.6")
show("   prior worth (years)", (sqrt(A) * s / 0.10) ** 2, ".2f", "3.59")
show("knowledge check: the unrounded worth (years)", (sqrt(A) * s / 0.10) ** 2, ".3f", "3.594")
show("   years of data for c = 0.9, nine times that", 9 * (sqrt(A) * s / 0.10) ** 2, ".1f", "32.3")
show("[[eg:split]] variance of the posterior mean (points^2)", c10 * 100, ".1f", "86.9")
show("   expected posterior variance (points^2)", 1e4 * sd10**2, ".1f", "13.1")
mh, sdh = posterior(0.5)
show("[[ex:normal]] posterior mean at c = 1/2 (%)", 100 * mh, ".2f", "7.69")
show("   posterior SD (points)", 100 * sdh, ".2f", "2.75")
show("LM20's eta* = c at a prior SD equal to the mean", weight(A * Rbar), ".3f", "0.940")
""")

code(r"""
x = np.linspace(-0.15, 0.35, 201)
fig, ax = plt.subplots()
ax.plot(100 * x, 0.01 * stats.norm.pdf(x, 0, A * se), "--", label="prior N(0, 3.89²)")
ax.plot(100 * x, 0.01 * stats.norm.pdf(x, A * Rbar, A * se), label="likelihood, unit area")
ax.plot(100 * x, 0.01 * stats.norm.pdf(x, mh, sdh), label="posterior at c = 1/2")
ax.set(xlabel="annual mean (%)", ylabel="density per point", title="[[ex:normal]]")
ax.legend(); plt.show()

rows = []
for name, s0 in (("quarter-Kelly sceptic", A * se / sqrt(3)), ("half-Kelly sceptic", A * se), ("10 points", 0.10),
                 ("flat", np.inf)):
    c = 1.0 if np.isinf(s0) else weight(s0)
    m, sd = posterior(c)
    rows.append({"prior": name, "A sigma0 (points)": 100 * s0,
                 "worth (years)": 0.0 if np.isinf(s0) else (sqrt(A) * s / s0) ** 2, "c": c,
                 "posterior mean (%)": 100 * m, "lower (%)": 100 * (m - Z975 * sd), "upper (%)": 100 * (m + Z975 * sd),
                 "Pr(mu<=0)": stats.norm.cdf(-m / sd), "Bayes fraction": c * fhat})
priors = pl.DataFrame(rows)
priors   # [[ex:priors]]
""")

code(r"""
show("[[ex:priors]] quarter-Kelly A sigma0", priors["A sigma0 (points)"][0], ".2f", "2.25")
show("   its worth (years)", priors["worth (years)"][0], ".2f", "71.29")
show("   the sample's span (years), four decimals", years, ".4f", "23.7645")
show("   three times the span", 3 * years, ".2f", "71.29")
show("   its interval", f"{priors['lower (%)'][0]:.1f} to {priors['upper (%)'][0]:.1f}", "", "0.0 to 7.7")
show("   its Pr(mu<=0)", priors["Pr(mu<=0)"][0], ".2g", "0.024")
show("   half-Kelly interval", f"{priors['lower (%)'][1]:.1f} to {priors['upper (%)'][1]:.1f}", "", "2.3 to 13.1")
show("   10 points: interval", f"{priors['lower (%)'][2]:.1f} to {priors['upper (%)'][2]:.1f}", "", "6.3 to 20.5")
show("   Bayes fractions", ", ".join(f"{v:.2f}" for v in priors["Bayes fraction"]), "", "1.07, 2.14, 3.72, 4.28")
""")

md(r"""
## Part 4 — Credible intervals and the chance of a negative mean

**[[eg:credible]].** Under the flat prior the credible interval is numerically LM20's confidence interval, and $\Pr(\mu\le0\mid\text{data})=\Phi(-\bar R/(s/\sqrt T))$. LM21's one-sided p-value divides by $s_{\mathrm u}$ instead.
""")

code(r"""
mf, sdf = posterior(1.0)
show("[[eg:credible]] lower (%)", 100 * (mf - Z975 * sdf), ".1f", "7.8")
show("   upper (%)", 100 * (mf + Z975 * sdf), ".1f", "23.0")
print(f"Pr(mu <= 0 | data), flat prior: {stats.norm.cdf(-Rbar / se):.2e}   [book: 3.8e-05]")
t_u = Rbar / (s_u / sqrt(T))
print(f"LM21's t-stat {t_u:.6f} (with s: {Rbar / se:.6f}); one-sided p-value {stats.norm.cdf(-t_u):.2e}")
assert f"{stats.norm.cdf(-Rbar / se):.1e}" == f"{stats.norm.cdf(-t_u):.1e}" == "3.8e-05"
print(f"at 10 points: Pr(mu <= 0 | data) = {stats.norm.cdf(-m10 / sd10):.1e}   [book: 1.1e-04]")
q_m, q_sd = posterior(0.25)
h_m, h_sd = posterior(0.5)
# each sceptic's prior is centred at zero and puts 50% on mu > 0; the posterior puts much more there
show("Pr(mu > 0 | data) under the quarter-Kelly prior (%)", 100 * stats.norm.sf(-q_m / q_sd), ".1f", "97.6")
show("Pr(mu > 0 | data) under the half-Kelly prior (%)", 100 * stats.norm.sf(-h_m / h_sd), ".1f", "99.7")
""")

md(r"""
## Part 5 — James–Stein, and Experiment 1

(24.4) toward the grand mean with one common noise variance, the average of the $s_i^2/T$, treated as known. The divisor is passed explicitly.
""")

code(r"""
def james_stein(X, ddof=0):
    # (24.4) on a T x N array of daily returns: c_hat, its unclipped 1 - c_hat, the estimates, the noise variance
    T_, N_ = X.shape
    m = X.mean(axis=0)
    noise = (X.var(axis=0, ddof=ddof) / T_).mean()
    one_minus = (N_ - 3) * noise / ((m - m.mean()) ** 2).sum()
    c_hat = max(0.0, 1 - one_minus)
    return c_hat, one_minus, m.mean() + c_hat * (m - m.mean()), noise


# the knowledge check of Section 5: four means 1, 2, 3, 6 with noise variance 1
km = np.array([1.0, 2.0, 3.0, 6.0])
kc = 1 - (4 - 3) * 1 / ((km - km.mean()) ** 2).sum()
print("c_hat =", Fraction(kc).limit_denominator(100), "| estimates", np.round(km.mean() + kc * (km - km.mean()), 2))

rng = np.random.default_rng([1, SEED])          # Experiment 1, created once
mu = rng.standard_normal((10_000, 28))          # one 10,000 x 28 array of true means,
xs = mu + rng.standard_normal((10_000, 28))     # then one of noise
gm = xs.mean(axis=1, keepdims=True)
ch = 1 - 25 / ((xs - gm) ** 2).sum(axis=1, keepdims=True)
err = {"raw": ((xs - mu) ** 2).sum(axis=1), "JS": ((gm + ch * (xs - gm) - mu) ** 2).sum(axis=1),
       "positive part": ((gm + np.maximum(ch, 0) * (xs - gm) - mu) ** 2).sum(axis=1),
       "Bayes 0.5x": ((0.5 * xs - mu) ** 2).sum(axis=1)}
for k, e in err.items():
    print(f"{k}: {e.mean():.3f} (SE {e.std(ddof=0) / sqrt(len(e)):.4f})")
show("[[eg:exp1]] raw", err["raw"].mean(), ".1f", "28.1")
show("   James-Stein", err["JS"].mean(), ".1f", "15.5")
show("   positive part", err["positive part"].mean(), ".1f", "15.5")
show("   Bayes rule", err["Bayes 0.5x"].mean(), ".1f", "14.0")
show("   mean c_hat", np.maximum(ch, 0).mean(), ".2f", "0.50")
""")

md(r"""
## Part 6 — The sector halves

**[[ex:case]], [[eg:halves]], [[ex:forest]], [[ex:oos]], [[eg:reverse]].** Annual means are $A$ (U28's) times the daily means; the miss is the root mean square over the 28 sectors.
""")

code(r"""
m1, m2 = X1.mean(axis=0), X2.mean(axis=0)
a1, a2 = A28 * m1, A28 * m2
case = pl.DataFrame({"sector": U28, "first half (%)": 100 * a1, "second half (%)": 100 * a2})
print(case.sort("first half (%)", descending=True).head(5))
show28("correlation of the halves", np.corrcoef(a1, a2)[0, 1], ".2f", "-0.05")
show28("first-half grand mean (%)", 100 * a1.mean(), ".2f", "10.49")


def miss(m_est, m_judge, c):
    # annualized RMS miss of the shrunk estimate against the other half's means
    est = m_est.mean() + c * (m_est - m_est.mean())
    return A28 * sqrt(((est - m_judge) ** 2).mean())


show28("[[ex:case]] miss of the own means (points)", 100 * miss(m1, m2, 1), ".1f", "9.8")
show28("   miss of the grand mean (points)", 100 * miss(m1, m2, 0), ".1f", "8.5")
c_r, b_r, _, v_r = james_stein(X1)
show28("[[eg:halves]] noise (points)", 100 * A28 * sqrt(v_r), ".2f", "7.18")
show28("   spread (divisor 28, points)", 100 * a1.std(ddof=0), ".2f", "4.50")
show28("   1 - c_hat", b_r, ".2f", "2.27")
noise_i = 100 * A28 * np.sqrt(X1.var(axis=0, ddof=0) / len(X1))   # each sector's own noise (points)
show28("   smallest and largest sector noise (points)", f"{noise_i.min():.1f} to {noise_i.max():.1f}", "", "4.8 to 9.7")
show28("   ratio of the noise variances", (noise_i.max() / noise_i.min()) ** 2, ".0f", "4")
print("   spread below every sector's noise:", bool((noise_i > 100 * a1.std(ddof=0)).all()))
d1, d2 = m1 - m1.mean(), m2 - m2.mean()
show28("   best weight in hindsight", d1 @ d2 / (d1 @ d1), ".2f", "-0.09")
XD1 = X1 - X1.mean(axis=1, keepdims=True)                 # each day's cross-sectional mean removed
c_d, b_d, _, v_d = james_stein(XD1)
show28("   noise, common removed (points)", 100 * A28 * sqrt(v_d), ".2f", "4.79")
show28("   1 - c_hat, common removed", b_d, ".2f", "1.01")
show28("   second-half spread (points)", 100 * a2.std(ddof=0), ".2f", "8.49")
c_rr, _, _, _ = james_stein(X2)
c_dr, _, _, _ = james_stein(X2 - X2.mean(axis=1, keepdims=True))
show28("[[eg:reverse]] c_hat", c_rr, ".2f", "0.25")
show28("   c_hat, common removed", c_dr, ".2f", "0.59")
show28("   misses at 0, c_hat, c_hat (common removed), 1",
       ", ".join(f"{100 * miss(m2, m1, c):.1f}" for c in (0, c_rr, c_dr, 1)), "", "4.5, 5.1, 6.9, 9.8")
same_side = int(((d1 >= EPS) & (d2 >= EPS)).sum() + ((d1 <= -EPS) & (d2 <= -EPS)).sum())
show28("knowledge check: same side in both halves", same_side, "d", "13")
""")

code(r"""
hw = A28 * Z975 * X1.std(axis=0, ddof=0) / sqrt(len(X1))
order = np.argsort(a1)
fig, axs = plt.subplots(1, 3, figsize=(15, 6))
axs[0].scatter(100 * a1, 100 * a2)
lim = [-5, 35]
axs[0].plot(lim, lim, "--", label="own mean")
axs[0].axhline(100 * a1.mean(), ls="--", color="green", label="grand mean")
axs[0].set(xlabel="first half (%)", ylabel="second half (%)", title="[[ex:case]]"); axs[0].legend()
axs[1].errorbar(100 * a1[order], range(28), xerr=100 * hw[order], fmt="o", label="first half, 95% interval")
axs[1].scatter(100 * a2[order], range(28), color="C1", label="second half")
axs[1].axvline(100 * a1.mean(), ls="--", color="green")
axs[1].set_yticks(range(28), [U28[i] for i in order], fontsize=7); axs[1].set(title="[[ex:forest]]")
axs[1].legend(fontsize=7)
cs = np.linspace(0, 1, 51)
axs[2].plot(cs, [100 * miss(m1, m2, c) for c in cs], label="first half judged on the second")
axs[2].plot(cs, [100 * miss(m2, m1, c) for c in cs], "--", label="second half judged on the first")
axs[2].set(xlabel="data's weight c", ylabel="RMS miss (points)", title="[[ex:oos]]"); axs[2].legend()
plt.tight_layout(); plt.show()
print(f"half-widths {100 * hw.min():.0f} to {100 * hw.max():.0f} points; intervals excluding the grand mean: "
      f"{int((np.abs(a1 - a1.mean()) >= hw + EPS).sum())}")
""")

md(r"""
## Part 7 — The Bayes Kelly fraction

(24.5): $f_{\mathrm B}=c\hat f$ for a prior centred at zero. The exact fraction solves (4.5) on TR23's returns shifted by one constant to the posterior mean, LM4's band method. To see what the quadratic rule's overshoot at $c=1$ is made of, the cell keeps (4.2)'s $\mu^2$ term, then mirrors the days about their mean: the mirrored days keep the fat tails and lose the skewness.
""")

code(r"""
def kelly_exact(target):
    # root of (4.5) on TR23's returns shifted so that their mean is `target` (daily)
    x = R - Rbar + target
    return optimize.brentq(lambda f: (x / (1 + f * x)).mean(), 1e-6, 1 / abs(x.min()) - 1e-6)


f_star = kelly_exact(Rbar)
show("LM17's exact in-sample root", f_star, ".4f", "4.1381")
show("[[eg:bayeskelly]] c fhat at 10 points", c10 * fhat, ".2f", "3.72")
show("   exact on shifted returns", kelly_exact(c10 * Rbar), ".2f", "3.62")
xg, wg = np.polynomial.hermite_e.hermegauss(60)
wg = wg / wg.sum()
pm_d, psd_d = c10 * Rbar, sqrt(c10) * se


def dgrowth(f):
    # derivative of the empirical growth averaged over the posterior of mu (60-node Gauss-Hermite quadrature)
    return sum(w * ((R - Rbar + pm_d + psd_d * z) / (1 + f * (R - Rbar + pm_d + psd_d * z))).mean()
               for w, z in zip(wg, xg))


show("   posterior-integrated", optimize.brentq(dgrowth, 1e-6, 8), ".2f", "3.62")
show("   posterior SD of mu / sigma^2", psd_d / s**2, ".2f", "1.01")
show("   quadratic minus exact at c = 1/2", 0.5 * fhat - kelly_exact(0.5 * Rbar), ".2f", "0.03")

# what the gap at c = 1 is made of: (4.2) keeps a mu^2 term that (24.5) drops; the rest comes from non-normal days
quad_mu2 = Rbar / (s**2 + Rbar**2)
show("   (4.2) with its mu^2 term, c = 1", quad_mu2, ".2f", "4.27")
show("   mu^2 part of the gap", fhat - quad_mu2, ".2f", "0.01")
show("   the rest (non-normal days)", quad_mu2 - f_star, ".2f", "0.13")
sym = np.concatenate([R, 2 * Rbar - R])         # the days mirrored about their mean: same tails, no skewness
f_sym = optimize.brentq(lambda f: (sym / (1 + f * sym)).mean(), 1e-6, 1 / abs(sym.min()) - 1e-6)
print(f"   mirrored days' root {f_sym:.4f}: fat tails {quad_mu2 - f_sym:.4f}, skewness {f_sym - f_star:.4f}")
print(f"   skewness of TR23's daily returns (LM19's): {(((R - Rbar) / s) ** 3).mean():.4f}")


def growth(f, m):
    # posterior-expected annual log growth in the model, posterior mean m per day
    return A * (f * m - f**2 * s**2 / 2)


show("   expected growth at f_B (%)", 100 * growth(c10 * fhat, pm_d), ".0f", "25")
show("   plug-in's share (%)", 100 * growth(fhat, pm_d) / growth(c10 * fhat, pm_d), ".1f", "97.7")
show("[[eg:sceptics]] Bayes growth, half Kelly (%)", 100 * growth(0.5 * fhat, 0.5 * Rbar), ".1f", "8.2")
show("   plug-in growth, quarter Kelly (%)", 100 * growth(fhat, 0.25 * Rbar), ".1f", "-16.5")
show("   Bayes growth, quarter Kelly (%)", 100 * growth(0.25 * fhat, 0.25 * Rbar), ".2f", "2.06")
""")

code(r"""
grid = np.geomspace(1, 50, 61)
quad = [weight(g / 100) * fhat for g in grid]
exact = [kelly_exact(weight(g / 100) * Rbar) for g in grid]
fig, ax = plt.subplots()
ax.semilogx(grid, quad, label="quadratic c × fhat")
ax.semilogx(grid, exact, "--", label="exact on shifted returns")
for g in (100 * A * se / sqrt(3), 100 * A * se, 10):
    ax.axvline(g, color="grey", ls=":")
ax.axhline(fhat, color="grey", ls="--"); ax.axhline(f_star, color="grey", ls="-.")
ax.set(xlabel="prior SD of the annual mean (points)", ylabel="Kelly fraction", title="[[ex:kelly]]")
ax.legend(); plt.show()
""")

md(r"""
## Part 8 — Practice problems 9–12

**Problem 9.** A prior centred at zero with $A\sigma_0=5$ points.
""")

code(r"""
c5 = weight(0.05)
m5, sd5 = posterior(c5)
show("P9 c", c5, ".3f", "0.623")
show("   posterior mean (%)", 100 * m5, ".1f", "9.6")
show("   posterior SD (points)", 100 * sd5, ".1f", "3.1")
show("   from the printed 0.623: mean, two decimals", 0.623 * 15.38, ".2f", "9.58")
show("   SD, two decimals", sqrt(0.623) * 3.89, ".2f", "3.07")
show("   interval from 9.58 and 3.07", f"{9.58 - 1.96 * 3.07:.1f} to {9.58 + 1.96 * 3.07:.1f}", "", "3.6 to 15.6")
show("   interval (%)", f"{100 * (m5 - Z975 * sd5):.1f} to {100 * (m5 + Z975 * sd5):.1f}", "", "3.6 to 15.6")
show("   Pr(mu <= 0 | data)", stats.norm.cdf(-m5 / sd5), ".4f", "0.0009")
show("   Bayes fraction", c5 * fhat, ".2f", "2.67")
show("   prior worth (years)", (sqrt(A) * s / 0.05) ** 2, ".1f", "14.4")
""")

md(r"""
**Problem 10.** Experiment 2: one generator, the spreads 0, 1 and 3 in that order, true means drawn even at spread 0.
""")

code(r"""
rng = np.random.default_rng([2, SEED])          # Experiment 2, created once
for spread, book in ((0.0, ("28.0", "3.0", "2.1")), (1.0, ("28.0", "15.5", "15.5")), (3.0, ("28.0", "25.5", "25.5"))):
    mu = spread * rng.standard_normal((20_000, 28))
    xs = mu + rng.standard_normal((20_000, 28))
    gm = xs.mean(axis=1, keepdims=True)
    ch = 1 - 25 / ((xs - gm) ** 2).sum(axis=1, keepdims=True)
    e = [((xs - mu) ** 2).sum(axis=1), ((gm + ch * (xs - gm) - mu) ** 2).sum(axis=1),
         ((gm + np.maximum(ch, 0) * (xs - gm) - mu) ** 2).sum(axis=1)]
    out = ", ".join(f"{v.mean():.1f}" for v in e)
    ses = ", ".join(f"{v.std(ddof=0) / sqrt(len(v)):.3f}" for v in e)
    show(f"P10 spread {spread:g}: raw, JS, positive part", out, "", ", ".join(book))
    print(f"   standard errors {ses}; theory for JS {28 - 25 / (1 + spread**2):g}")
""")

md(r"""
**Problem 11.** Each day's return of the TAIEX price index subtracted instead of the cross-sectional mean (*stability check*).
""")

code(r"""
XE1, XE2 = X1 - TX1[:, None], X2 - TX2[:, None]
c_e, b_e, _, v_e = james_stein(XE1)
me1, me2 = XE1.mean(axis=0), XE2.mean(axis=0)
show28("P11 noise (points)", 100 * A28 * sqrt(v_e), ".1f", "5.0")
show28("   1 - c_hat", b_e, ".2f", "1.10")
show28("   miss of the grand mean (points)", 100 * miss(me1, me2, 0), ".1f", "12.1")
dev_miss = miss(me1 - me1.mean(), me2 - me2.mean(), 0)  # the grand mean's miss of the deviations
show28("   miss of the deviations from each half's grand mean (points)", 100 * dev_miss, ".2f", "8.49")
show28("   average excess, first half (points)", 100 * A28 * me1.mean(), ".1f", "-0.3")
show28("   average excess, second half (points)", 100 * A28 * me2.mean(), ".1f", "-9.0")
show28("   TAIEX price index, halves (%)", f"{100 * A28 * TX1.mean():.1f} -> {100 * A28 * TX2.mean():.1f}", "",
       "10.8 -> 19.1")
""")

md(r"""
**Problem 12.** LM13's Practice Problem 8, 16 good months in 24, under the sceptic's prior.
""")

code(r"""
p12 = beta_sf_exact(98, 90, P55)
show("P12 posterior mean", 98 / 188, ".3f", "0.521")
show("   Pr(theta >= 0.55 | record) (%)", 100 * float(p12), ".1f", "21.6")
""")

md(r"""
### Extension: thirds of U28 (*stability check*)

Split U28 into thirds with `np.array_split` (1,461, 1,461 and 1,460 returns). Estimate $\hat c$ on each third and judge the shrunk means on the next third, as in [[eg:halves]]. Does any third give partial shrinkage, and does it predict the next third better than the grand mean? Then explain why a second split of the same data is a stability check and not a new test: the thirds were chosen after the halves were seen, and they reuse the same 4,382 days (LM21 counts such looks).
""")

code(r"""
Xall = smp.select(U28).to_numpy()
parts = np.array_split(Xall, 3)
print("third lengths:", [len(p) for p in parts])
for k in range(2):
    c_k, _, _, _ = james_stein(parts[k])
    mk, mn = parts[k].mean(axis=0), parts[k + 1].mean(axis=0)
    print(f"third {k + 1} -> {k + 2}: c_hat {c_k:.2f}; miss at 0 {100 * miss(mk, mn, 0):.1f}, "
          f"at c_hat {100 * miss(mk, mn, c_k):.1f}, at 1 {100 * miss(mk, mn, 1):.1f} points")
# your code: repeat with each day's cross-sectional mean removed
""")

nb = nbf.v4.new_notebook()
nb["cells"] = cells
nb["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                  "language_info": {"name": "python"}}
nbf.write(nb, LAB / "LM24_lab.ipynb")

(LAB / "README.md").write_text("""# LM24 Lab — Bayesian Inference and Shrinkage

Companion to *From Calculus to Kelly*, Learning Module 24. The notebook rebuilds the module's exhibits and computational examples (the beta–binomial update of a manager's record, the posterior of TAIEX's mean under four priors, credible intervals, James–Stein shrinkage and Experiment 1, the sector means out of sample, and the Bayes Kelly fraction) and works the computational practice problems.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM24_lab/LM24_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM24_lab.ipynb
```

`build/make_lab24.py` generates the notebook and this README: edit the generator, not the generated files.

## Data (FinMind; not in the repository)

The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

The same steps in a shell (`data/raw/` and this folder's `data/` are git-ignored):

```bash
export FINMIND_TOKEN=...               # your FinMind API token
uv run python data/fetch_finmind.py    # rebuilds and verifies data/raw/
uv run python data/make_lab_data.py    # writes every lab's data/ folder
```

`fetch_finmind.py` checks every file against `data/raw_manifest.json`. The notebook reads only the files in its own `data/` folder:

| File | Content |
|:--|:--|
| `data/taiex_tr.csv` | `date`, `price`: the daily closes of the TAIEX total-return index (FinMind `TaiwanStockTotalReturnIndex`, data_id TAIEX), 2003-01-02 → 2026-10-08 |
| `data/sectors_close_raw.csv` | the closes FinMind's `TaiwanStockPrice` serves for TAIEX and the 30 TWSE sector indices, one column per series |
| `data/sectors_close_repairs.csv` | each of the 561 closes FinMind copied from another date or series, with its official 13:30:00 value (`TaiwanStockEvery5SecondsIndex`, a paid dataset; empty on the free plan, and the notebook then drops those closes) |
""", encoding="utf-8", newline="\n")
print("wrote", LAB / "LM24_lab.ipynb", "and README.md | labels:", {k: ("X" if w == "Exhibit" else "E") + str(n) for k, (w, n) in NUM.items()})
