"""Generate labs/LM03_lab/LM03_lab.ipynb (Polars-first) and the lab's README.

Run from the repository root:  uv run python build/make_lab03.py
Then execute inside labs/LM03_lab:  uv run jupyter nbconvert --to notebook --execute --inplace LM03_lab.ipynb

Exhibit and example numbers are never typed by hand: cells write [[ex:label]] / [[eg:label]], and the generator
resolves them from the labels in src/lm03.md, numbered in document order as build/build.py does.
"""

import re
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "LM03_lab"

# ---------------------------------------------------------------- exhibit / example numbers from the module's labels
NUM, _count = {}, {"exhibit": 0, "example": 0}
for m in re.finditer(r"(?m)^(?:>\s?)+\[!(exhibit|example)\][+-]?\s*(.*)$", (ROOT / "src" / "lm03.md").read_text(encoding="utf-8")):
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


def md(s):
    cells.append(nbf.v4.new_markdown_cell(refs(s.strip("\n"))))


def code(s):
    cells.append(nbf.v4.new_code_cell(refs(s.strip("\n"))))


DATA_TEXT = (
    "The notebook reads FinMind files that you download once with your own token. From the repository root, run "
    "`uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not "
    "allow the book to redistribute the data. After that, the notebook runs offline."
)
ENV_TEXT = (
    "**Environment.** From the repository root, `uv sync` installs the locked Python environment (`uv.lock`). "
    "Open this notebook with the `.venv` kernel, or run `uv run --with jupyterlab jupyter lab`."
)

md(rf"""
# LM3 Lab — Taylor Series and Approximation

Companion notebook to **From Calculus to Kelly, LM3**. It rebuilds every exhibit and computational example in the module and the numbers in its knowledge checks, and it solves the computational practice problems; the data-driven parts use FinMind price files.

| Part | Rebuilds |
|:--|:--|
| 1 | The expansions of [[ex:expansions]]; Taylor polynomials and the Lagrange bound ([[ex:remainder]], [[eg:approx]], [[eg:fisher]], [[eg:rule72]]) |
| 2 | Total-return series with dividends and splits, verified; the case ([[ex:paradox]]) |
| 3 | Simple vs log returns ([[ex:simplelog]], Section 5); the two worst days ([[eg:worstdays]]) |
| 4 | Volatility drag across sampling frequencies ([[ex:freq]], [[eg:fiveyears]], [[eg:bet]]) |
| 5 | 00631L decomposition: power, drag, residual ([[ex:wealth]], [[ex:decomp]], [[ex:yearly]]) |
| 6 | TQQQ in 2022 ([[eg:tqqq]]) |
| 7 | Duration and convexity ([[eg:bond]], [[ex:bondcurve]]) |
| 8 | Practice-problem solutions and an extension exercise |

{ENV_TEXT}

**Data.** {DATA_TEXT} `data/` then holds FinMind `TaiwanStockPrice` closes for 0050 and 00631L (2014-10-31 → 2026-10-08), 0050 cash dividends from `TaiwanStockDividendResult`, and QQQ and TQQQ closes for 2022 from `USStockPrice`, retrieved 2026-10-10. Every daily close was checked against FinMind's own `spread` column (close − previous close); the only mismatches are ex-dividend and split days, which Part 2 handles explicitly.

**Conventions (as in the module).** $T$ counts returns; a span in years is calendar days ÷ 365.25, and $A$ is the number of returns per year in the sample in use. The 0050 and 00631L series are aligned on the 2,902 days on which both funds traded.
""")

code(r"""
import math
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import sympy as sp

DATA = Path("data")
BASE = date(2014, 10, 31)                     # last close before the first daily return
pl.Config.set_tbl_rows(30)
pl.Config.set_float_precision(6)
plt.rcParams.update({"figure.figsize": (9, 4.5), "axes.grid": True, "grid.alpha": 0.3,
                     "axes.spines.top": False, "axes.spines.right": False})
""")

md(r"""
## Part 1 — Expansions, Taylor polynomials and the Lagrange bound

[[ex:expansions]] lists four Maclaurin series. SymPy reproduces their first terms.
""")

code(r"""
x, alpha = sp.symbols("x alpha")
for fn in (sp.exp(x), sp.log(1 + x), (1 + x) ** alpha, 1 / (1 - x)):
    print(fn, "=", sp.series(fn, x, 0, 4).removeO())
""")

md(r"""
For $\ln(1+x)$ the order-$n$ Maclaurin polynomial $T_n(x)$ keeps the first $n$ terms of the series (eq. 3.3). The Lagrange remainder (eq. 3.5) bounds its error by $|x|^{n+1}/(n+1)$ for $x\ge0$ and by $|x|^{n+1}/\big((n+1)(1+x)^{n+1}\big)$ for $-1<x<0$.
""")

code(r"""
def taylor_log1p(x, n):
    return sum((-1) ** (k + 1) * x**k / k for k in range(1, n + 1))

def bound_log1p(x, n):
    base = 1.0 if x >= 0 else 1.0 + x
    return abs(x) ** (n + 1) / ((n + 1) * base ** (n + 1))

def taylor_exp(x, n):
    return sum(x**k / math.factorial(k) for k in range(n + 1))

xs = [-0.20, -0.10, -0.05, -0.01, 0.01, 0.05, 0.10, 0.20, 0.50]
xc = pl.col("x")
remainder = pl.DataFrame({"x": xs}).with_columns(
    xc.log1p().alias("ln(1+x)"),
    (xc - xc**2 / 2).alias("T2"),
    (xc.abs() ** 3 / (3 * pl.when(xc >= 0).then(pl.lit(1.0)).otherwise(1 + xc) ** 3)).alias("bound"),
).with_columns((pl.col("ln(1+x)") - pl.col("T2")).alias("error")).select("x", "ln(1+x)", "T2", "error", "bound")
assert (remainder["error"].abs() <= remainder["bound"]).all()
remainder   # [[ex:remainder]]
""")

code(r"""
# [[eg:approx]]: ln(1.05) and e^0.05 with orders 1-3 (errors are exact minus approximation)
for n in (1, 2, 3):
    print(f"n={n}:  ln T={taylor_log1p(0.05, n):.7f} err {math.log1p(0.05) - taylor_log1p(0.05, n):+.7f}"
          f"   exp T={taylor_exp(0.05, n):.7f} err {math.exp(0.05) - taylor_exp(0.05, n):+.7f}")

# [[eg:fisher]]: nominal 1.725% (Bank of Taiwan), expected inflation 1.8% (illustrative)
i, infl = 0.01725, 0.018
print(f"real rate: exact {(1 + i) / (1 + infl) - 1:.5%}  first order {i - infl:.5%}  "
      f"second order {(i - infl) - infl * (i - infl):.5%}")

# [[eg:rule72]]: doubling time and the rule of 72
for R in (0.02, 0.06, 0.08, 0.12):
    print(f"R={R:.0%}: exact {math.log(2) / math.log1p(R):6.3f}  ln2/R+ln2/2 {math.log(2) / R + math.log(2) / 2:6.3f}  "
          f"0.693/R+0.347 {0.693 / R + 0.347:6.3f}  rule of 72 {72 / (100 * R):6.3f}")
print(f"100 ln2 (1 + R/2) = 72 at R = {2 * (72 / (100 * math.log(2)) - 1):.2%}")

# knowledge checks: a monthly rate from 9% a year, and e^-0.3 with T4
print(f"(1+0.09)^(1/12) - 1: second order {0.09 / 12 - 11 / 288 * 0.09**2:.4%}, exact {1.09 ** (1 / 12) - 1:.4%}")
print(f"e^-0.3: bound {0.3**5 / 120:.4e}, actual error {math.exp(-0.3) - taylor_exp(-0.3, 4):.3e}")
""")

code(r"""
xg = np.linspace(-0.95, 1.6, 400)
fig, ax = plt.subplots()
ax.plot(xg, np.log1p(xg), color="black", lw=2, label="ln(1+x)")
for n in (1, 2, 3, 6, 10):
    ax.plot(xg, [taylor_log1p(v, n) for v in xg], lw=1.4, label=f"T{n}")
ax.axvline(1, color="grey", lw=1)
ax.text(1.02, -2.6, "radius of convergence", color="grey")
ax.set_ylim(-3, 1.6)
ax.set_title("ln(1+x) and its Maclaurin polynomials")
ax.legend(ncol=3)
plt.show()
""")

md(r"""
## Part 2 — Total-return series, corporate actions, verification

* **0050** pays cash dividends; on an ex-date $t$ the total return is $R_t=(P_t+D_t)/P_{t-1}-1$. It split 4-for-1 effective **2025-06-18**.
* **00631L** paid no dividends in the sample and split 22-for-1 effective **2026-03-31**.
* On a split day the return is $P_t/(P_{t-1}/k)-1$, where $k$ is the split ratio ($k=4$ for 0050, $k=22$ for 00631L): dividing by $k$ restates the previous close per new share.

The checksum below confirms that every close agrees with FinMind's `spread` except on those corporate-action days.
""")

code(r"""
SPLITS = {"0050": ("2025-06-18", 4), "00631L": ("2026-03-31", 22)}
div = pl.read_csv(DATA / "0050_dividends.csv")

def load_raw(sym):
    df = pl.read_csv(DATA / f"{sym}_daily_raw.csv").sort("date")
    gap = (pl.col("close") - pl.col("close").shift(1) - pl.col("spread")).abs()
    chk = df.with_columns(gap.alias("gap")).filter(pl.col("gap") > 0.005)
    return df, chk

for sym in ("0050", "00631L"):
    df, chk = load_raw(sym)
    expected = (set(div["date"]) | {SPLITS[sym][0]}) if sym == "0050" else {SPLITS[sym][0]}
    unexplained = set(chk["date"]) - expected
    print(f"{sym}: {df.height} rows, checksum mismatches {chk.height}, unexplained {sorted(unexplained)}")
    assert not unexplained
""")

code(r"""
def total_returns(sym):
    df, _ = load_raw(sym)
    split_day, k = SPLITS[sym]                # split ratio k, effective on split_day
    if sym == "0050":
        d = div.select("date", pl.col("cash_dividend").alias("D"))
    else:
        d = pl.DataFrame({"date": [], "D": []}, schema={"date": pl.Utf8, "D": pl.Float64})
    return (df.join(d, on="date", how="left")
              .with_columns(pl.col("D").fill_null(0.0),
                            pl.when(pl.col("date") == pl.lit(split_day)).then(pl.lit(k)).otherwise(pl.lit(1))
                            .cast(pl.Float64).alias("k"))
              .sort("date")
              .select("date", pl.col("close").alias(f"P_{sym}"), pl.col("D").alias(f"D_{sym}"),
                      pl.col("k").alias(f"k_{sym}")))

def returns(sym):
    return (pl.col(f"P_{sym}") + pl.col(f"D_{sym}")) / (pl.col(f"P_{sym}").shift(1) / pl.col(f"k_{sym}")) - 1

# align on common trading dates (each fund had a split-related trading halt), then compute returns
both = total_returns("0050").join(total_returns("00631L"), on="date", how="inner").sort("date")
ret = (both.with_columns(returns("0050").alias("R_0050"), returns("00631L").alias("R_00631L"))
           .drop_nulls("R_0050")
           .with_columns(pl.col("date").str.to_date())
           .select("date", "R_0050", "R_00631L"))
R, RL = ret["R_0050"].to_numpy(), ret["R_00631L"].to_numpy()
days = (ret["date"][-1] - BASE).days
years = days / 365.25
print(f"{ret.height} daily returns from {ret['date'][0]} to {ret['date'][-1]}: {days} days = {years:.3f} years, "
      f"A = {ret.height / years:.1f} returns a year")

# the two halt-spanning returns: sessions of the other fund between the common dates
own = {s: set(load_raw(s)[0]["date"]) for s in ("0050", "00631L")}
for d0, d1, other in (("2025-06-10", "2025-06-18", "00631L"), ("2026-03-24", "2026-03-31", "0050")):
    print(f"return dated {d1} spans {1 + sum(d0 < d < d1 for d in own[other])} sessions")
""")

code(r"""
# [[ex:paradox]]: the case
G0, GL = np.prod(1 + R), np.prod(1 + RL)
print(f"0050 {G0 - 1:+.2%} (x{G0:.2f}), annualized {G0 ** (1 / years) - 1:.1%}")
print(f"00631L {GL - 1:+.1%} (x{GL:.2f}), annualized {GL ** (1 / years) - 1:.1%}")
print(f"twice 0050's return {2 * (G0 - 1):+.1%}; 00631L / twice 0050 = {(GL - 1) / (2 * (G0 - 1)):.1f}")
""")

md(r"""
## Part 3 — Simple vs log returns (Section 5)

Equation (3.6): $r=R-R^2/2+O(R^3)$, so the mean daily gap should be close to $\tfrac12\overline{R^2}=\tfrac12(s^2+\bar R^2)$.
""")

code(r"""
# [[ex:simplelog]]
pl.DataFrame({"R": [-0.5, -0.2, -0.1, -0.01, 0.01, 0.1, 0.2, 0.5, 1.0]}).with_columns(
    pl.col("R").log1p().alias("r"), (pl.col("R") - pl.col("R").log1p()).alias("R - r"),
    (pl.col("R") ** 2 / 2).alias("R^2/2"))
""")

code(r"""
r = np.log1p(R)
print(f"mean R            {R.mean():.6%}")
print(f"mean r            {r.mean():.6%}")
print(f"gap               {(R.mean() - r.mean()) * 1e4:.3f} bp/day, x A = {(R.mean() - r.mean()) * ret.height / years:.2%} a year")
print(f"half mean square  {(R**2).mean() / 2 * 1e4:.3f} bp/day")
print(f"half variance     {R.var() / 2 * 1e4:.3f} bp/day")
cen = R - R.mean()
print(f"skewness {(cen**3).mean() / R.var() ** 1.5:.3f}, excess kurtosis {(cen**4).mean() / R.var() ** 2 - 3:.2f}  (LM19)")

# knowledge check: 60% in an asset up 10%, 40% in one down 10%
print(f"portfolio: R_p {0.6 * 0.1 - 0.4 * 0.1:.2%}, r_p {math.log(1.02):.3%}, "
      f"weighted log {0.6 * math.log(1.1) + 0.4 * math.log(0.9):.3%}")
""")

code(r"""
# [[eg:worstdays]]: exact log return vs T1, T2 and the Lagrange bound
for d in ("2024-08-05", "2025-04-07"):
    x = ret.filter(pl.col("date") == pl.lit(d).str.to_date())["R_0050"][0]
    ex = math.log1p(x)
    print(f"{d}: R={x:.6f} ln={ex:.6f}  T1 err {(x - ex) * 1e4:.1f} bp  T2={taylor_log1p(x, 2):.6f} "
          f"err {(taylor_log1p(x, 2) - ex) * 1e4:.1f} bp  bound {bound_log1p(x, 2) * 1e4:.1f} bp")

# on 0050's own calendar (2,906 returns) the three worst days
own0050 = total_returns("0050").with_columns(returns("0050").alias("R")).drop_nulls("R")
own0050.sort("R").head(3).select("date", "R")
""")

md(r"""
## Part 4 — Volatility drag across sampling frequencies

$R_G\approx\bar R-s^2/2$ (3.9) and $g\approx\bar R-(s^2+\bar R^2)/2$ (3.8), with $s^2$ the population variance. Errors are approximation minus exact, in basis points.
""")

code(r"""
wealth = ret.select("date", (1 + pl.col("R_0050")).cum_prod().alias("W"))

def period_returns(every):
    if every == "1d":
        w = wealth["W"].to_numpy()
    else:
        w = wealth.group_by_dynamic("date", every=every).agg(pl.col("W").last()).sort("date")["W"].to_numpy()
    w = np.concatenate([[1.0], w])
    Rk = w[1:] / w[:-1] - 1
    return Rk[1:-1] if every == "1y" else Rk   # annual: full calendar years 2015-2025 only

rows = []
for label, every in [("Daily", "1d"), ("Weekly", "1w"), ("Monthly", "1mo"), ("Quarterly", "1q"), ("Annual", "1y")]:
    Rk = period_returns(every)
    mu, s2 = Rk.mean(), Rk.var()
    g = np.log1p(Rk).mean()
    RG = np.expm1(g)
    rows.append({"period": label, "T": len(Rk), "mean": mu, "s": math.sqrt(s2), "R_G": RG, "mu - s2/2": mu - s2 / 2,
                 "err_bp": (mu - s2 / 2 - RG) * 1e4, "g": g, "mu - (s2+mu2)/2": mu - (s2 + mu * mu) / 2,
                 "err_g_bp": (mu - (s2 + mu * mu) / 2 - g) * 1e4})
pl.DataFrame(rows)   # [[ex:freq]]
""")

code(r"""
# [[eg:fiveyears]]: calendar-year total returns 2020-2024
annual = (ret.group_by(pl.col("date").dt.year().alias("year"))
             .agg((1 + pl.col("R_0050")).product().sub(1).alias("R_0050"),
                  (1 + pl.col("R_00631L")).product().sub(1).alias("R_00631L"))
             .sort("year"))
sub = annual.filter(pl.col("year").is_between(2020, 2024))["R_0050"].to_numpy()
mu, s2 = sub.mean(), sub.var()
RG = np.prod(1 + sub) ** (1 / len(sub)) - 1
print([f"{v:.2%}" for v in sub])
print(f"mean {mu:.2%}  s^2 {s2:.5f}  s {math.sqrt(s2):.2%}  approx {mu - s2 / 2:.2%}  R_G {RG:.2%}")

# [[eg:bet]]: +2% / -1% on the whole capital
mu, s2 = 0.005, 0.000225
RG, g = math.sqrt(1.02 * 0.99) - 1, (math.log(1.02) + math.log(0.99)) / 2
print(f"bet: R_G {RG:.5%} vs {mu - s2 / 2:.5%} ({(mu - s2 / 2 - RG) * 1e4:.4f} bp);  "
      f"g {g:.5%} vs {mu - (s2 + mu * mu) / 2:.5%} ({(mu - (s2 + mu * mu) / 2 - g) * 1e4:.4f} bp)")

# knowledge check: two funds with mean 10% and volatility 10% or 30%, over 20 years
print(f"(1.095/1.055)^20 = {(1.095 / 1.055) ** 20:.2f};  with (3.8): e^(20 x 0.04) = {math.exp(0.8):.2f}")
annual
""")

md(r"""
## Part 5 — Leveraged ETF decomposition

From (3.10)–(3.11): $\ln G_{\text{fund}} = L\ln G + \sum_t\big[\ln(1+LR_t)-L\ln(1+R_t)\big] + \text{residual}$, and the middle term is $\approx-\tfrac{L(L-1)}{2}\sum_t R_t^2$. The function is the one printed in Section 9 of the module.
""")

code(r'''
def leverage_decomposition(R, RF, L):
    """Split a daily-reset fund's log growth into power, drag and residual
    (eqs. 3.10-3.11). R, RF: aligned daily simple returns of the index and
    the fund, as NumPy arrays."""
    power = L * np.log1p(R).sum()                           # ln G^L
    exact_drag = (np.log1p(L * R) - L * np.log1p(R)).sum()  # exact effect
    taylor2 = -L * (L - 1) / 2 * (R**2).sum()               # to 2nd order
    taylor3 = taylor2 + (L**3 - L) / 3 * (R**3).sum()       # to 3rd order
    taylor4 = taylor3 - (L**4 - L) / 4 * (R**4).sum()       # to 4th order
    actual = np.log1p(RF).sum()
    return {"power": power, "exact_drag": exact_drag,
            "taylor2": taylor2, "taylor3": taylor3, "taylor4": taylor4,
            "residual": actual - power - exact_drag, "actual": actual}

full = leverage_decomposition(R, RL, 2)
print({name: round(float(v), 5) for name, v in full.items()})   # [[ex:decomp]]
print(f"third-order term {full['taylor3'] - full['taylor2']:+.4f}, fourth-order term {full['taylor4'] - full['taylor3']:+.4f}")
print(f"growth factors: 0050^2 x{G0**2:.2f}, drag x{math.exp(full['exact_drag']):.3f}, residual x{math.exp(full['residual']):.3f}, "
      f"00631L x{GL:.2f}")
print(f"drag per year {-full['taylor2'] / years:.4f} log points; s^2 A {R.var() * ret.height / years:.4f}; "
      f"mean^2 A {R.mean() ** 2 * ret.height / years:.4f}; residual per year {full['residual'] / years:.3f}")
path = np.cumsum(np.log1p(2 * R) - 2 * np.log1p(R)) + np.cumsum(R**2)
imax = int(np.argmax(np.abs(path)))
print(f"running gap between the exact effect and -RV: largest {path[imax]:+.4f} on {ret['date'][imax]}")
''')

code(r"""
yearly = []
for y in range(2014, 2027):   # 2014 is the stub from the base close of 31 Oct; 2026 runs to 8 Oct
    m = (ret["date"].dt.year() == y).to_numpy()
    d = leverage_decomposition(R[m], RL[m], 2)
    yearly.append({"year": y, "0050": np.prod(1 + R[m]) - 1, "00631L": np.prod(1 + RL[m]) - 1,
                   "2x0050": 2 * (np.prod(1 + R[m]) - 1), "taylor2": d["taylor2"], "exact_drag": d["exact_drag"],
                   "residual": d["residual"], "exact - taylor2": d["exact_drag"] - d["taylor2"],
                   "exact_daily_2x": math.exp(d["power"] + d["exact_drag"]) - 1})
yearly = pl.DataFrame(yearly)
print(f"columns sum to: taylor2 {yearly['taylor2'].sum():.5f}, exact {yearly['exact_drag'].sum():.5f}, "
      f"residual {yearly['residual'].sum():.4f}; mean residual 2015-2025 "
      f"{yearly.filter(pl.col('year').is_between(2015, 2025))['residual'].mean():.3f}")
yearly   # [[ex:yearly]] (+ exact daily 2x)
""")

code(r"""
dates = np.concatenate([[np.datetime64("2014-10-31")], ret["date"].to_numpy()])
W0 = np.concatenate([[1], np.cumprod(1 + R)])
W2 = np.concatenate([[1], np.cumprod(1 + 2 * R)])
WT = np.concatenate([[1], np.cumprod(1 + R) ** 2 * np.exp(-np.cumsum(R**2))])
WL = np.concatenate([[1], np.cumprod(1 + RL)])
print(f"end values: 00631L {WL[-1]:.2f}, exact daily 2x {W2[-1]:.3f}, Taylor {WT[-1]:.3f}, 0050 {W0[-1]:.2f}")
fig, ax = plt.subplots()
ax.plot(dates, WL, label="00631L (market price)")
ax.plot(dates, W2, label="exact daily 2x of 0050")
ax.plot(dates, WT, "--", label="Taylor: G^2 exp(-sum R^2)")
ax.plot(dates, W0, label="0050 total return")
ax.set_yscale("log")
ax.set_title("Growth of 1 unit ([[ex:wealth]])")
ax.legend()
plt.show()

fig, ax = plt.subplots()
ax.plot(dates, np.concatenate([[0], np.cumsum(np.log1p(RL) - 2 * np.log1p(R))]), label="00631L actual gap")
ax.plot(dates, np.concatenate([[0], np.cumsum(np.log1p(2 * R) - 2 * np.log1p(R))]), label="exact rebalancing effect")
ax.plot(dates, np.concatenate([[0], -np.cumsum(R**2)]), "--", label="Taylor: -sum R^2")
ax.set_title("Cumulative log gap vs 2 x log growth of 0050")
ax.legend()
plt.show()

# knowledge check: a flat index (G = 1) with RV = 0.04
print(f"flat index: 2x {math.exp(-0.04) - 1:.1%}, 3x {math.exp(-0.12) - 1:.1%}")
""")

md(r"""
## Part 6 — TQQQ in 2022

Calendar-2022 returns use the adjusted close from 2021-12-31 to 2022-12-30; $L=3$, so the second-order drag coefficient is $L(L-1)/2=3$ and the third-order coefficient $(L^3-L)/3=8$.

TQQQ targets three times the daily return of the Nasdaq-100 Index (NDX), a price index that leaves dividends out. QQQ's adjusted close includes its dividends and its unadjusted close does not. The last lines therefore also measure the residual, and the benchmark $G^3e^{-3\,\mathrm{RV}}$, against the unadjusted close.
""")

code(r"""
qt = (pl.read_csv(DATA / "QQQ_TQQQ_2022.csv")
        .filter(pl.col("date").is_between(pl.lit("2021-12-31"), pl.lit("2022-12-30"))).sort("date"))
qa, ta, qc = qt["qqq_adj"].to_numpy(), qt["tqqq_adj"].to_numpy(), qt["qqq_close"].to_numpy()
rq, rt = qa[1:] / qa[:-1] - 1, ta[1:] / ta[:-1] - 1
d3 = leverage_decomposition(rq, rt, 3)
G = qa[-1] / qa[0]
RVq = float(np.sum(rq**2))
print(f"QQQ {qa[0]} -> {qa[-1]}: {G - 1:.2%}   TQQQ {ta[0]} -> {ta[-1]}: {ta[-1] / ta[0] - 1:.2%}   "
      f"3 x QQQ {3 * (G - 1):.1%}")
print(f"RV {RVq:.4f}, sqrt(RV) {math.sqrt(RVq):.1%};  3 ln G {3 * math.log(G):.5f}, G^3 {G**3:.4f}")
print({name: round(float(v), 5) for name, v in d3.items()})   # [[eg:tqqq]]
print(f"residual vs the exact effect {d3['residual']:.4f} ({math.expm1(d3['residual']):.1%} of value); "
      f"vs the second-order drag {d3['actual'] - d3['power'] - d3['taylor2']:.4f}")
print(f"before costs: Taylor {G**3 * math.exp(d3['taylor2']):.3f}, exact {G**3 * math.exp(d3['exact_drag']):.3f}")

# what the residual contains: fees and financing, then the dividends in QQQ's adjusted close
cost = 0.0086 + 2 * 0.0168   # expense ratio after waivers + two units at 2022's average fed funds rate
div_qqq = math.log(G) - math.log(qc[-1] / qc[0])
du = leverage_decomposition(qc[1:] / qc[:-1] - 1, rt, 3)
print(f"fees and financing {cost:.3f} ({cost / -d3['residual']:.0%} of the residual); "
      f"QQQ dividends {div_qqq:.4f} log points, x 3 = {3 * div_qqq:.3f}")
print(f"QQQ unadjusted {qc[0]} -> {qc[-1]}: residual {du['residual']:.3f}, "
      f"beyond fees and financing {-du['residual'] - cost:.3f}")
Gu3 = (qc[-1] / qc[0]) ** 3
bench_u = Gu3 * math.exp(du["taylor2"])
print(f"benchmark on the unadjusted closes: {Gu3:.4f} x {math.exp(du['taylor2']):.3f} = {bench_u:.3f}, "
      f"a {1 - bench_u:.1%} loss ({1 - Gu3 * math.exp(du['exact_drag']):.1%} with the exact effect)")
""")

md(r"""
## Part 7 — Duration and convexity

A 10-year bond with a 2% annual coupon, priced at a 2% yield. Duration and convexity come from the exact derivatives of $P(y)$.
""")

code(r"""
def price(y, coupon=0.02, periods=10, face=100.0):
    return sum(coupon * face / (1 + y) ** t for t in range(1, periods + 1)) + face / (1 + y) ** periods

y0 = 0.02
P0 = price(y0)
dP = -sum(t * 2 / (1 + y0) ** (t + 1) for t in range(1, 11)) - 10 * 100 / (1 + y0) ** 11
d2P = sum(t * (t + 1) * 2 / (1 + y0) ** (t + 2) for t in range(1, 11)) + 110 * 100 / (1 + y0) ** 12
Dmod, C = -dP / P0, d2P / P0
print(f"P0={P0:.4f}  Dmod={Dmod:.6f}  C={C:.6f}")
pl.DataFrame([{"dy_bp": dy * 1e4, "exact": price(y0 + dy) / P0 - 1, "duration": -Dmod * dy,
               "duration+convexity": -Dmod * dy + 0.5 * C * dy * dy} for dy in (0.01, -0.01, 0.03)])   # [[eg:bond]]
""")

code(r"""
yg = np.linspace(0.0, 0.06, 121)
fig, ax = plt.subplots()
ax.plot(yg, [price(v) for v in yg], lw=2, label="exact price")
ax.plot(yg, P0 * (1 - Dmod * (yg - y0)), label="duration only (1st order)")
ax.plot(yg, P0 * (1 - Dmod * (yg - y0) + 0.5 * C * (yg - y0) ** 2), "--", label="duration + convexity (2nd order)")
ax.plot([y0], [P0], "o", color="black")
ax.set_xlabel("yield")
ax.set_ylabel("price per 100 face")
ax.set_title("[[ex:bondcurve]]")
ax.legend()
plt.show()
""")

md(r"""
## Part 8 — Practice-problem solutions (computational) and an extension
""")

code(r"""
print("PP2 ", f"T2={0.08 - 0.08**2 / 2:.4f}  exact={math.log(1.08):.5f}  third-order term={0.08**3 / 3:.5f}")
print("PP3 ", f"ln(0.92)={math.log1p(-0.08):.7f}  T2={taylor_log1p(-0.08, 2):.7f}  bound={bound_log1p(-0.08, 2):.7f}")
pp4 = np.array([0.30, -0.20, 0.10])
print("PP4 ", f"geo={np.prod(1 + pp4) ** (1 / 3) - 1:.4%}  approx={pp4.mean() - pp4.var() / 2:.4%}  "
      f"with the sample variance {pp4.mean() - pp4.var(ddof=1) / 2:.4%}")
print("PP6 ", f"geo={math.sqrt(1.6 * 0.6) - 1:.3%}  approx={0.10 - 0.5**2 / 2:.3%}")
print("PP7 ", f"index={1.1 * 0.9 - 1:.2%}  fund={1.2 * 0.8 - 1:.2%}  taylor={(1.1 * 0.9) ** 2 * math.exp(-0.02) - 1:.2%}  "
      f"drag={math.log(0.96) - 2 * math.log(0.99):.4f}")
print("PP8 ", f"{1.2**3 * math.exp(-3 * 0.09) - 1:.2%}")
for y, Gp, RVp in ((2017, 1.1813, 0.0088), (2015, 0.9369, 0.0266)):   # the inputs printed in the problem
    Gy = 1 + annual.filter(pl.col("year") == y)["R_0050"][0]
    RVy = float(np.sum(R[(ret["date"].dt.year() == y).to_numpy()] ** 2))
    assert (round(Gy, 4), round(RVy, 4)) == (Gp, RVp)
    print(f"PP9  {y}: G={Gp} RV={RVp}  |1-1/G|={abs(1 - 1 / Gp):.3f}  sqrt(RV)={math.sqrt(RVp):.3f}")
print("PP10", f"{-7.5 * 0.015 + 0.5 * 70 * 0.015**2:.3%}")
print("PP12", f"exact={math.log(2) / math.log1p(0.06):.3f}  ln2/R+ln2/2={math.log(2) / 0.06 + math.log(2) / 2:.3f}  "
      f"0.693/R+0.347={0.693 / 0.06 + 0.347:.3f}")
print("PP13", f"exact={1.03 / 1.025 - 1:.4%}  first={0.005:.4%}  second={0.005 - 0.025 * 0.005:.4%}")
m = ret["date"].dt.year().is_between(2020, 2023).to_numpy()
pp14 = leverage_decomposition(R[m], RL[m], 2)
print("PP14", {name: round(float(v), 5) for name, v in pp14.items()}, f"00631L {math.expm1(pp14['actual']):+.1%}")
""")

md(r"""
### Extension: the inverse fund

For an inverse fund $L=-1$, the drag coefficient $L(L-1)/2$ equals $1$: a daily −1× fund suffers the **same** variance drag as a daily 2× fund. Fetch Yuanta Taiwan 50 Bear −1X (00632R) and test (3.11) with $L=-1$. The helper below downloads data from the FinMind API with your own token (`FINMIND_TOKEN` environment variable) and the standard library's `urllib`; it queries one year at a time.
""")

code(r"""
import json
import os
import urllib.parse
import urllib.request


def finmind(dataset, data_id, start, end):
    token = os.environ["FINMIND_TOKEN"]
    out = []
    for y in range(int(start[:4]), int(end[:4]) + 1):
        params = {"dataset": dataset, "data_id": data_id, "start_date": max(start, f"{y}-01-01"),
                  "end_date": min(end, f"{y}-12-31"), "token": token}
        req = urllib.request.Request("https://api.finmindtrade.com/api/v4/data?" + urllib.parse.urlencode(params),
                                     headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            out.extend(json.load(resp).get("data", []))
    return pl.DataFrame(out)

# inv = finmind("TaiwanStockPrice", "00632R", "2015-01-01", "2026-10-08")   # uncomment to run
""")

nb = nbf.v4.new_notebook()
nb["cells"] = cells
nb["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                  "language_info": {"name": "python"}}
LAB.mkdir(parents=True, exist_ok=True)
nbf.write(nb, LAB / "LM03_lab.ipynb")
print("wrote", LAB / "LM03_lab.ipynb")

README = f"""# LM3 Lab — Taylor Series and Approximation

Companion to *From Calculus to Kelly*, Learning Module 3. The notebook rebuilds every exhibit and computational
example of the module and the numbers in its knowledge checks: Taylor polynomials and Lagrange bounds, the 0050 and
00631L total-return series with their corporate actions, simple versus log returns, volatility drag at five sampling
frequencies, the decomposition of 00631L into power, drag and residual, TQQQ in 2022 and the bond example. It also
solves the computational practice problems.

## Run

From the repository root:

```bash
uv sync                  # install the locked Python environment (uv.lock)
uv run --with jupyterlab jupyter lab labs/LM03_lab/LM03_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. It is generated by
`build/make_lab03.py`; to re-execute it, run this inside `labs/LM03_lab`:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM03_lab.ipynb
```

## Data (FinMind, retrieved 2026-10-10; not in the repository)

{DATA_TEXT} The first command needs your token in `FINMIND_TOKEN`:

```bash
export FINMIND_TOKEN=...              # your FinMind API token
uv run python data/fetch_finmind.py   # rebuild data/raw/, checked against
                                      # data/raw_manifest.json
uv run python data/make_lab_data.py   # write this lab's data/ and every
                                      # other lab's
```

The folder then holds:

| File | Content |
|:--|:--|
| `data/0050_daily_raw.csv` | 0050 daily close and FinMind `spread`, 2014-10-31 → 2026-10-08 (unadjusted) |
| `data/00631L_daily_raw.csv` | 00631L daily close and `spread`, same period (unadjusted) |
| `data/0050_dividends.csv` | 0050 ex-dividend dates and cash dividends (`TaiwanStockDividendResult`) |
| `data/QQQ_TQQQ_2022.csv` | QQQ and TQQQ adjusted and raw closes, 2021-12-30 → 2023-01-03 (`USStockPrice`) |

Every close was verified against FinMind's own `spread` column (close − previous close). The only mismatches are
0050's ex-dividend days in the window and the two split days: 0050 4-for-1 on 2025-06-18 and 00631L 22-for-1 on
2026-03-31. Part 2 of the notebook re-runs this check. The two funds are aligned on the 2,902 days on which both
traded.

The optional `finmind()` helper at the end downloads further data with your own token, using the standard library's
`urllib`. Exhibit and example numbers in the notebook are generated from the labels in `src/lm03.md`, so they always
match the module.
"""
(LAB / "README.md").write_text(README, encoding="utf-8", newline="\n")
print("wrote", LAB / "README.md")
