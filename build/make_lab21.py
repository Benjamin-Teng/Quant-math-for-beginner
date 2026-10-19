"""Generate labs/LM21_lab (Polars-first notebook + README) for LM21, Hypothesis Testing and Multiple Testing.

Run:  uv run python build/make_lab21.py
Then execute from inside the lab folder:
      cd labs/LM21_lab && uv run jupyter nbconvert --to notebook --execute --inplace LM21_lab.ipynb

The notebook reads only labs/LM21_lab/data/taiex_tr.csv (date, price: the TAIEX total-return closes as FinMind's
TaiwanStockTotalReturnIndex serves them), which data/make_lab_data.py builds from data/raw/ (FinMind's licence keeps
raw data out of the repository). This script writes the notebook and the README only.

Exhibit and example numbers are never typed by hand: cells write [[ex:label]] / [[eg:label]], and the generator
resolves them from the labels in src/lm21.md, numbered in document order as build/build.py does.
"""
import re
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "LM21_lab"
LAB.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- exhibit / example numbers from the module's labels
NUM: dict[str, tuple[str, int]] = {}
_count = {"exhibit": 0, "example": 0}
for m in re.finditer(r"(?m)^(?:>\s?)+\[!(exhibit|example)\][+-]?\s*(.*)$", (ROOT / "src" / "lm21.md").read_text(encoding="utf-8")):
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
# LM21 Lab — Hypothesis Testing and Multiple Testing

Companion notebook to **From Calculus to Kelly, LM21**. It rebuilds the module's exhibits and computational examples from the closes of the TAIEX total-return index, runs experiments 8 and 10, solves the computational practice problems, and ends with an extension exercise.

| Part | Rebuilds |
|:--|:--|
| 1 | Data: TR23's returns, the exact check that no day is unchanged, $T$, years, $A$, the guard, weekdays and months, the 23 Saturday sessions, the 29 tests |
| 2 | Testing a frequency and a mean: [[eg:updays]], [[eg:mean]], [[ex:case]] and [[ex:nulldist]] |
| 3 | Two groups and power: (21.3), [[eg:regimes]], [[ex:power]] and [[eg:years]] |
| 4 | Counts: [[eg:manager]] and Problem 6 with `stats.binom`, the sign table and (21.5) by hand, [[eg:signs]] with and without Yates, [[eg:falls]] ([[ex:independence]]) |
| 5 | The calendar family: [[ex:calendar]] and experiment 8 ([[eg:wednesday]]) |
| 6 | Holm and Benjamini–Hochberg by hand and with the packages: [[eg:holmbh]], [[ex:pvalues]] |
| 7 | A search: experiment 10 ([[eg:search]]) and (21.9), [[ex:maxt]] |
| 8 | Practice problems 7, 9, 10 and 11, and an extension: the calendar family in each limit regime |

**Environment.** From the repository root, `uv sync` installs the locked Python environment (`uv.lock`). Open this notebook with the `.venv` kernel, or run `uv run --with jupyterlab jupyter lab`.

**Data.** The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

`data/` then holds `taiex_tr.csv`: `date` and `price`, the daily closes of the TAIEX total-return index (FinMind `TaiwanStockTotalReturnIndex`, data_id TAIEX) from 2 January 2003 to 8 October 2026. The notebook reads nothing outside `data/`.

**Conventions (as in the module).** TR23: $T=5{,}849$ simple daily returns $R_t$ from 3 January 2003; no log returns. $s$ divides by $T$ and $s_{\mathrm u}$ by $T-1$ (`ddof` always passed); every t-stat (21.1) uses $s_{\mathrm u}$, and the two-sample statistic (21.3) uses unpooled $s_{\mathrm u}^2$. p-values are two-sided against the standard normal unless stated. Years are calendar days / 365.25 and $A=T/\text{years}$. The calendar family is the 12 months and the 5 weekdays of each return's date, each against all other returns. An up day is `R > 1e-12`, a fall `R <= -0.03 + 1e-12`, and every count is checked exactly with `Fraction` on the two-decimal closes. Each experiment creates its generator once, `np.random.default_rng([e, 20261011])` with `e` its number. Every test here is in-sample; the null laws, power curves, shuffles and simulated searches are model results.
""")

code(r"""
import datetime as dt
from fractions import Fraction
from math import log, sqrt
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from scipy import stats
from statsmodels.stats.multitest import multipletests

DATA = Path("data")
EPS = 1e-12
SEED = 20261011
pl.Config.set_tbl_rows(30)
plt.rcParams.update({"figure.figsize": (9, 4.5), "axes.grid": True, "grid.alpha": 0.3,
                     "axes.spines.top": False, "axes.spines.right": False})


def show(label, value, fmt, printed):
    # print a value next to the module's printed value and assert that they agree
    got = format(value, fmt)
    print(f"{label}: {got}   [book: {printed}]")
    assert got == printed, (label, got, printed)


def p2(z):
    # two-sided normal p-value, (21.2)
    return float(2 * stats.norm.sf(abs(z)))


def tstat(x):
    # (21.1) with mu_null = 0 and s_u
    return float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x))))


def two_sample(a, b):
    # (21.3): unpooled divisor-(n - 1) variances; returns the statistic and its standard error
    se = sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return float((a.mean() - b.mean()) / se), se
""")

md(r"""
## Part 1 — Data

Returns between consecutive closes, in Polars; then NumPy arrays for the arithmetic. The closes have two decimals, so an exact `Fraction` recount decides whether any day is unchanged, and the guard `R > 1e-12` must agree with it. Weekdays follow Python's convention, Monday 0, checked on a known date: 8 October 2026 was a Thursday.
""")

code(r"""
raw = pl.read_csv(DATA / "taiex_tr.csv", schema_overrides={"price": pl.String}).sort("date")
df = raw.with_columns(pl.col("date").str.to_date(), pl.col("price").cast(pl.Float64).alias("tr"))
df = df.with_columns((pl.col("tr") / pl.col("tr").shift(1) - 1).alias("R"))
rets = df.slice(1).with_columns((pl.col("date").dt.weekday() - 1).alias("wd"), pl.col("date").dt.month().alias("mo"))
R = rets["R"].to_numpy()
wd, mo = rets["wd"].to_numpy(), rets["mo"].to_numpy()
pre = (rets["date"] < dt.date(2015, 6, 1)).to_numpy()            # the 7% limit regime
T = len(R)
days = (df["date"][-1] - df["date"][0]).days
years = days / 365.25
A = T / years
print(f"{df.height} closes, {df['date'][0]} -> {df['date'][-1]}; T = {T} returns from {rets['date'][0]}")
show("calendar days", days, ",", "8,680")
show("years", years, ".4f", "23.7645")
show("A", A, ".2f", "246.12")
show("returns before 1 June 2015", int(pre.sum()), ",", "3,077")
show("returns from 1 June 2015", int((~pre).sum()), ",", "2,772")

closes = [Fraction(p) for p in raw["price"].to_list()]
RF = [closes[i] / closes[i - 1] - 1 for i in range(1, len(closes))]
up_exact, zero = sum(x > 0 for x in RF), sum(x == 0 for x in RF)
assert up_exact == int((R > EPS).sum()) and zero == 0
show("up days (exact = guard)", up_exact, ",", "3,205")

assert rets.filter(pl.col("date") == pl.date(2026, 10, 8))["wd"][0] == 3   # a Thursday
print(rets.group_by("wd").len().sort("wd"))
print(rets.group_by("mo").len().sort("mo"))
sat = rets.filter(pl.col("wd") == 5)["date"]
print(f"{len(sat)} Saturday sessions, {sat[0]} -> {sat[-1]}")
""")

md(r"""
The 23 Saturday sessions belong to no weekday and to every "rest" of the calendar family. TWSE's history page states that the market stopped trading on Saturday make-up workdays from 2019; that these sessions were such days is an inference.

The module runs **29 tests** on TR23, all in-sample: the mean (E3), the mean before and from 1 June 2015, the regimes' difference (E4), the up-day frequency (E2), down after down (E6), falls after falls (E7), the 17 calendar tests, Wednesday in each regime, the blocks' variance against 4.95 and against 5.16 (Problem 7), and Jarque–Bera (Problem 9). Read every p-value below with that count in mind.
""")

md(r"""
## Part 2 — Testing a frequency and a mean

[[eg:updays]]: the share of up days against a fair coin, by the normal approximation and exactly. [[eg:mean]]: the t-stat (21.1) of TR23's mean, with the normal and the $t_{T-1}$ reference.
""")

code(r"""
up = int((R > EPS).sum())
theta = up / T
z_up = (theta - 0.5) / sqrt(1 / (4 * T))
show("theta hat", theta, ".3f", "0.548")
show("z", z_up, ".1f", "7.3")
show("exact Pr(X >= 3,205)", float(stats.binom.sf(up - 1, T, 0.5)), ".1e", "1.2e-13")

Rbar, s, su = R.mean(), R.std(ddof=0), R.std(ddof=1)
se = su / sqrt(T)
t_all = Rbar / se
show("mean (% a day)", 100 * Rbar, ".4f", "0.0625")
show("s_u (% a day)", 100 * su, ".4f", "1.2085")
show("SE (% a day)", 100 * se, ".4f", "0.0158")
show("t-stat", t_all, ".2f", "3.96")
show("t-stat with s", Rbar / (s / sqrt(T)), ".3f", "3.956")
show("two-sided p, normal", p2(t_all), ".1e", "7.6e-05")
show("two-sided p, t_(T-1)", 2 * float(stats.t.sf(t_all, T - 1)), ".1e", "7.7e-05")
show("one-sided p", float(stats.norm.sf(t_all)), ".1e", "3.8e-05")
print(stats.ttest_1samp(R, 0.0))   # SciPy's one-sample test: the same t-stat, t reference
""")

md(r"""
[[ex:case]]: the mean of all days, of each limit regime, and Wednesdays against the other days.
""")

code(r"""
wed, oth = R[wd == 2], R[wd != 2]
z_wed, se_wed = two_sample(wed, oth)
rows = []
for name, x in (("All days", R), ("Before 1 June 2015", R[pre]), ("From 1 June 2015", R[~pre])):
    rows.append({"returns": name, "days": str(len(x)), "mean %": 100 * x.mean(), "s_u %": 100 * x.std(ddof=1),
                 "SE %": 100 * x.std(ddof=1) / sqrt(len(x)), "t-stat": tstat(x), "p": p2(tstat(x))})
rows.append({"returns": "Wednesdays minus other days", "days": f"{len(wed)}; {len(oth)}",
             "mean %": 100 * (wed.mean() - oth.mean()), "s_u %": None, "SE %": 100 * se_wed, "t-stat": z_wed,
             "p": p2(z_wed)})
case = pl.DataFrame(rows)
print(case)
for (t, p_), (tp, pp) in zip(case.select("t-stat", "p").rows(), (("3.956", None), ("2.046", "0.041"),
                                                                 ("3.675", "0.00024"), ("2.363", "0.018"))):
    show("t-stat", t, ".3f", tp)
    if pp:
        show("p-value", p_, f".{len(pp) - 2}f", pp)
show("Wednesdays (% a day)", 100 * wed.mean(), ".4f", "0.1332")
show("other days (% a day)", 100 * oth.mean(), ".4f", "0.0446")
""")

md(r"""
[[ex:nulldist]]: the standard normal density, the two-sided 5% rejection region and TR23's three t-stats. The $t_{5848}$ density is not drawn, because it differs from $\varphi$ by at most $2.3\times10^{-5}$.
""")

code(r"""
x = np.linspace(-5, 5, 2001)
gap = np.abs(stats.t.pdf(x, T - 1) - stats.norm.pdf(x)).max()
show("largest density gap", gap, ".1e", "2.3e-05")
show("t_5848 97.5% point", float(stats.t.isf(0.025, T - 1)), ".4f", "1.9604")
c = stats.norm.isf(0.025)
fig, ax = plt.subplots()
ax.plot(x, stats.norm.pdf(x), label="null law of the t-stat")
for side in (x <= -c, x >= c):
    ax.fill_between(x[side], 0, stats.norm.pdf(x[side]), color="C1", alpha=0.4)
for t, style, ha, y_ in ((t_all, "-", "left", 0.40), (tstat(R[pre]), "--", "left", 0.37),
                         (tstat(R[~pre]), "--", "right", 0.40)):
    ax.axvline(t, color="k", ls=style, lw=1)
    ax.text(t, y_, f" {t:.2f} ", ha=ha)
ax.set(xlabel="t-stat", ylabel="density", ylim=(0, 0.42))
ax.legend();
""")

md(r"""
## Part 3 — Two groups and power

[[eg:regimes]]: the two-sample statistic (21.3) of the 10% regime against the 7% regime, by hand and with SciPy's `ttest_ind(..., equal_var=False)` (whose default, `equal_var=True`, pools the variances).
""")

code(r"""
z_reg, se_reg = two_sample(R[~pre], R[pre])
show("SE of the difference (% a day)", 100 * se_reg, ".4f", "0.0315")
show("statistic (21.3)", z_reg, ".2f", "1.08")
show("p, normal", p2(z_reg), ".2f", "0.28")
show("p, SciPy (t reference)", float(stats.ttest_ind(R[~pre], R[pre], equal_var=False).pvalue), ".3f", "0.280")
show("from the printed inputs", (0.0804 - 0.0464) / sqrt(0.0227**2 + 0.0219**2), ".2f", "1.08")
""")

md(r"""
[[ex:power]] and [[eg:years]]: (21.4) for four annual Sharpe ratios, and the years for 80% power. TR23's annual ratio is $\sqrt A\,\bar R/s$ with $r_f=0$ (LM19's statistic).
""")

code(r"""
c975, c80 = stats.norm.isf(0.025), stats.norm.ppf(0.8)


def power(sr, yrs):
    d = sr * np.sqrt(yrs)
    return stats.norm.cdf(d - c975) + stats.norm.cdf(-d - c975)


sr_tr = sqrt(A) * Rbar / s
show("TR23's annual Sharpe ratio", sr_tr, ".4f", "0.8115")
show("the identity SR sqrt(years)", sr_tr * sqrt(years), ".3f", "3.956")
for sr, book in ((1, "7.85"), (sr_tr, "11.9"), (0.5, "31.4"), (0.25, "125.6")):
    show(f"years for 80% power at SR {sr:.4g}", ((c975 + c80) / sr) ** 2, f".{len(book.split('.')[1])}f", book)
for sr, book in ((1, "0.998"), (sr_tr, "0.977"), (0.5, "0.68"), (0.25, "0.23")):
    show(f"power over {years:.2f} years at SR {sr:.4g}", power(sr, years), f".{len(book.split('.')[1])}f", book)
yrs = np.logspace(0, np.log10(200), 300)
fig, ax = plt.subplots()
for sr, lab in ((1, "SR 1"), (sr_tr, "SR 0.81 (TR23)"), (0.5, "SR 0.5"), (0.25, "SR 0.25")):
    ax.plot(yrs, power(sr, yrs), label=lab)
ax.axhline(0.8, color="k", ls="--", lw=0.8)
ax.axvline(years, color="k", ls=":", lw=0.8)
ax.set(xscale="log", xlabel="years of daily data", ylabel="power")
ax.legend();
""")

md(r"""
## Part 4 — Counts and independence

[[eg:manager]] and Problem 6: LM13's hypothetical manager with `stats.binom`, then the months needed for 80% power and an exact check.
""")

code(r"""
show("Pr(X >= 8)", stats.binom.sf(7, 12, 0.5), ".3f", "0.194")
show("Pr(X >= 9)", stats.binom.sf(8, 12, 0.5), ".3f", "0.073")
show("size of X >= 10", stats.binom.sf(9, 12, 0.5), ".4f", "0.0193")
show("power at 0.55", stats.binom.sf(9, 12, 0.55), ".3f", "0.042")
n_months = ((stats.norm.isf(0.05) * 0.5 + c80 * sqrt(0.55 * 0.45)) / 0.05) ** 2
show("months, normal approximation", n_months, ".2f", "616.16")
n = int(np.ceil(n_months))
cut = int(stats.binom.isf(0.05, n, 0.5)) + 1          # the smallest count whose upper tail is at most 5%
while stats.binom.sf(cut - 1, n, 0.5) > 0.05:
    cut += 1
print(f"n = {n} months ({n / 12:.1f} years): reject at X >= {cut}")
show("exact size", stats.binom.sf(cut - 1, n, 0.5), ".4f", "0.0454")
show("exact power at 0.55", stats.binom.sf(cut - 1, n, 0.55), ".4f", "0.7874")
""")

md(r"""
[[eg:signs]] and [[ex:independence]]: LM13's table of yesterday's and today's signs, counted exactly; the expected counts as fractions; (21.5) by hand, as $n\hat\rho^2$, and with SciPy, whose default applies Yates' correction.
""")

code(r"""
down = [x < 0 for x in RF]
n11 = sum(a and b for a, b in zip(down[:-1], down[1:]))
n12 = sum(a and not b for a, b in zip(down[:-1], down[1:]))
n21 = sum(b and not a for a, b in zip(down[:-1], down[1:]))
n22 = sum(not a and not b for a, b in zip(down[:-1], down[1:]))
npair = n11 + n12 + n21 + n22
tab = np.array([[n11, n12], [n21, n22]])
rows_, cols_ = tab.sum(axis=1), tab.sum(axis=0)
expected = [[Fraction(int(r) * int(c_), npair) for c_ in cols_] for r in rows_]
print(tab, rows_, cols_)
print([[f"{float(e):,.2f}" for e in row] for row in expected])
chi2 = sum(float((tab[i, j] - expected[i][j]) ** 2 / expected[i][j]) for i in (0, 1) for j in (0, 1))
rho = (n11 * n22 - n12 * n21) / sqrt(rows_.prod() * cols_.prod())
show("chi2 by hand", chi2, ".2f", "2.69")
show("n rho^2", npair * rho**2, ".2f", "2.69")
show("rho", rho, ".4f", "0.0214")
show("p-value", float(stats.chi2.sf(chi2, 1)), ".2f", "0.10")
yates = stats.chi2_contingency(tab)                     # correction=True by default
show("SciPy default (Yates)", float(yates.statistic), ".2f", "2.60")
show("its p-value", float(yates.pvalue), ".3f", "0.107")
show("SciPy without the correction", float(stats.chi2_contingency(tab, correction=False).statistic), ".2f", "2.69")
""")

md(r"""
[[eg:falls]]: falls of 3% or more after such a fall, counted exactly, against $\operatorname{Bin}(108,108/5{,}848)$. LM13's lab asked whether shares of falls after big moves exceed chance: this is one answer, and the clustering it reveals is why LM22 resamples blocks of days and LM26 models volatility.
""")

code(r"""
fall = [x <= Fraction(-3, 100) for x in RF]
f1 = sum(fall[:-1])
f12 = sum(a and b for a, b in zip(fall[:-1], fall[1:]))
assert f12 == int(((R[:-1] <= -0.03 + EPS) & (R[1:] <= -0.03 + EPS)).sum())
print(f"{f1} days after a fall of 3% or more; {f12} of them fell 3% or more")
show("expected", Fraction(f1 * sum(fall[1:]), npair), ".1f", "2.0")
show("exact Pr(X >= 13)", float(stats.binom.sf(f12 - 1, f1, sum(fall[1:]) / npair)), ".1e", "1.2e-07")
""")

md(r"""
## Part 5 — The calendar family

[[ex:calendar]]: each month and weekday against all other returns with (21.3). Then experiment 8 ([[eg:wednesday]]): the returns shuffled over TR23's fixed dates, `R[perm]`, 10,000 times, recomputing the 17 statistics each time. Model.
""")

code(r"""
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
groups = [(MONTHS[k - 1], mo == k) for k in range(1, 13)] + [(DAYS[k], wd == k) for k in range(5)]
fam = pl.DataFrame([{"group": g, "days": int(sel.sum()), "mean %": 100 * R[sel].mean(),
                     "z": two_sample(R[sel], R[~sel])[0]} for g, sel in groups])
pv = 2 * stats.norm.sf(np.abs(fam["z"].to_numpy()))           # two-sided normal p-values, (21.2)
fam = fam.with_columns(pl.Series("p", pv))
print(fam)
m = len(pv)
show("rejections at 5%", int((pv <= 0.05).sum()), "d", "1")
show("Wednesday's p", float(pv[14]), ".3f", "0.018")
show("expected false rejections", m * 0.05, ".2f", "0.85")
show("FWER if independent", 1 - 0.95**m, ".3f", "0.582")
show("Bonferroni-adjusted", m * pv.min(), ".2f", "0.31")
show("Sidak for independent tests", 1 - (1 - pv.min()) ** m, ".3f", "0.267")
fig, ax = plt.subplots()
ax.bar(fam["group"], fam["z"])
for y_ in (1.96, -1.96, stats.norm.isf(0.025 / m), -stats.norm.isf(0.025 / m)):
    ax.axhline(y_, color="k", ls="--", lw=0.8)
ax.set(ylabel="statistic (21.3)", ylim=(-3.2, 3.2));
""")

code(r"""
g8 = np.random.default_rng([8, SEED])
grp_m, grp_w = mo - 1, wd
n_m = np.bincount(grp_m, minlength=12).astype(float)
n_w = np.bincount(grp_w, minlength=7)[:5].astype(float)
S_all, Q_all = R.sum(), (R * R).sum()
zmax = np.empty(10_000)
for b in range(10_000):
    x = R[g8.permutation(T)]
    zs = []
    for grp, cnt, K in ((grp_m, n_m, 12), (grp_w, n_w, 5)):   # (21.3) for every group at once, from sums
        s1 = np.bincount(grp, weights=x, minlength=12)[:K]
        q1 = np.bincount(grp, weights=x * x, minlength=12)[:K]
        c2 = T - cnt
        m1, m2 = s1 / cnt, (S_all - s1) / c2
        v1 = (q1 - cnt * m1**2) / (cnt - 1)
        v2 = (Q_all - q1 - c2 * m2**2) / (c2 - 1)
        zs.append((m1 - m2) / np.sqrt(v1 / cnt + v2 / c2))
    zmax[b] = np.abs(np.concatenate(zs)).max()
share_a = (zmax >= 1.959964 - EPS).mean()
share_b = (zmax >= abs(fam["z"][14]) - EPS).mean()
show("shuffles with a rejection", share_a, ".3f", "0.580")
show("its SE (18.2)", sqrt(share_a * (1 - share_a) / 10_000), ".3f", "0.005")
show("shuffles at least as extreme as Wednesday", share_b, ".3f", "0.266")
show("its SE (18.2)", sqrt(share_b * (1 - share_b) / 10_000), ".3f", "0.004")
for name, sel, book in (("before", pre, "2.06"), ("from", ~pre, "1.25")):
    x, w = R[sel], wd[sel]
    show(f"Wednesday {name} 1 June 2015", two_sample(x[w == 2], x[w != 2])[0], ".2f", book)
""")

md(r"""
## Part 6 — Holm and Benjamini–Hochberg

The three rules by hand on [[eg:holmbh]]'s constructed p-values, compared exactly as fractions; then the packages on the calendar family. `multipletests` defaults to Holm–Šidák (`method="hs"`), not Holm: always pass `method`.
""")

code(r"""
def bonferroni(p, a):
    return sum(pi <= a / len(p) for pi in p)


def holm(p, a):                       # (21.7): leading ranks with p_(i) <= a / (m - i + 1)
    k = 0
    for i, pi in enumerate(sorted(p)):
        if pi > a / (len(p) - i):
            break
        k += 1
    return k


def bh(p, q):                         # (21.8): the largest rank with p_(i) <= i q / m
    ok = [i + 1 for i, pi in enumerate(sorted(p)) if pi <= (i + 1) * q / len(p)]
    return max(ok, default=0)


e9 = [Fraction(v) for v in ("0.002", "0.0054", "0.0061", "0.011", "0.024", "0.031", "0.09", "0.22", "0.47", "0.86")]
a5 = Fraction(5, 100)
show("Bonferroni", bonferroni(e9, a5), "d", "1")
show("Holm", holm(e9, a5), "d", "3")
show("Benjamini-Hochberg", bh(e9, a5), "d", "5")
p10 = np.array([float(v) for v in e9])
for method, book in (("bonferroni", "1"), ("holm", "3"), ("fdr_bh", "5")):
    show(f"multipletests {method}", int(multipletests(p10, alpha=0.05, method=method)[0].sum()), "d", book)
print("calendar:", {meth: int(multipletests(pv, alpha=0.05, method=meth)[0].sum())
                    for meth in ("bonferroni", "holm", "fdr_bh", "hs")})
adj = np.sort(stats.false_discovery_control(pv, method="bh"))
show("smallest BH-adjusted p", adj[0], ".3f", "0.308")
""")

md(r"""
[[ex:pvalues]]: the calendar's sorted p-values against each rule's levels, on a log scale. No point lies on or below any line.
""")

code(r"""
ps = np.sort(pv)
i = np.arange(1, m + 1)
fig, ax = plt.subplots()
ax.plot(i, ps, "o", label="calendar family")
ax.plot(i, np.full(m, 0.05 / m), label="Bonferroni")
ax.plot(i, 0.05 / (m - i + 1), label="Holm")
ax.plot(i, i * 0.05 / m, label="BH, q = 5%")
ax.plot(i, i * 0.10 / m, "--", label="BH, q = 10%")
ax.set(yscale="log", xlabel="rank i", ylabel="p-value", ylim=(1e-3, 1.2))
ax.legend();
""")

md(r"""
## Part 7 — A search over random rules

Experiment 10 ([[eg:search]]): 10,000 rules, each long or short one unit by a fair coin each day, every position drawn in one call; the t-stat (21.1) of each rule's daily returns, in 20 chunks of 500 rules. The standard deviation of the 10,000 t-stats gets LM18's batch standard error over the 20 chunks. Then (21.9) for the best of $m$ independent null statistics ([[ex:maxt]]).
""")

code(r"""
g10 = np.random.default_rng([10, SEED])
pos = g10.integers(0, 2, size=(10_000, T), dtype=np.int8)
tt = np.empty(10_000)
for c0 in range(0, 10_000, 500):
    xr = (2.0 * pos[c0:c0 + 500].astype(np.float64) - 1.0) * R
    tt[c0:c0 + 500] = xr.mean(axis=1) / (xr.std(axis=1, ddof=1) / np.sqrt(T))
sd = tt.std(ddof=0)
batch = np.array([tt[c0:c0 + 500].std(ddof=0) for c0 in range(0, 10_000, 500)])
show("mean t-stat", tt.mean(), ".2f", "-0.01")
show("its SE", sd / 100, ".2f", "0.01")
show("standard deviation", sd, ".3f", "0.995")
show("its batch SE", batch.std(ddof=0) / sqrt(20), ".3f", "0.007")
show("rules at t >= 3", int((tt >= 3 - EPS).sum()), "d", "13")
show("expected", 10_000 * stats.norm.sf(3), ".1f", "13.5")
best = np.maximum.accumulate(tt)
show("best of 100", best[99], ".2f", "2.95")
show("best of 1,000", best[999], ".2f", "2.95")
show("rule 1,022", tt[1021], ".2f", "3.28")
show("best of 10,000", best[-1], ".2f", "3.97")
records = [k for k in range(10_000) if k == 0 or tt[k] > best[k - 1]]
print("records (rule, t-stat):", [(k + 1, round(float(tt[k]), 2)) for k in records])
""")

code(r"""
def max_quantile(u, m_):     # (21.9): Pr(max <= x) = Phi(x)^m, so the u quantile is Phi^-1(u^(1/m))
    return stats.norm.ppf(u ** (1 / m_))


for m_, book in ((17, "1.75"), (100, "2.46"), (1000, "3.20"), (10000, "3.81")):
    show(f"median of the best of {m_}", max_quantile(0.5, m_), ".2f", book)
show("Pr(best of 1,000 > 3)", 1 - stats.norm.cdf(3) ** 1000, ".2f", "0.74")
show("Bonferroni tests for t = 3", 0.05 / (2 * stats.norm.sf(3)), ".1f", "18.5")
mm = np.unique(np.round(np.logspace(0, 4, 200)).astype(int))
fig, ax = plt.subplots()
ax.fill_between(mm, max_quantile(0.05, mm), max_quantile(0.95, mm), alpha=0.25, label="model, 90% range")
ax.plot(mm, max_quantile(0.5, mm), "--", label="model median")
ax.step(np.arange(1, 10_001), best, where="post", label="best of m random rules on TR23")
ax.axhline(3, color="k", ls=":", lw=0.8)
ax.set(xscale="log", xlabel="number of rules m", ylabel="largest t-stat")
ax.legend();
""")

md(r"""
## Part 8 — Practice problems

**Problem 7.** LM15's 292 blocks of 20 sessions: the variance of their up-day counts against the binomial and the dependence-adjusted model, with LM20's standard error of a variance, $\sigma_X^2\sqrt{2/n}$; then the blocks needed to see the gap.
""")

code(r"""
nb = T // 20
blk = (R[: nb * 20] > EPS).reshape(nb, 20).sum(axis=1)
v = blk.var(ddof=0)
p_hat = blk.sum() / (nb * 20)
show("blocks' variance", v, ".2f", "4.72")
show("binomial 20 p q", 20 * p_hat * (1 - p_hat), ".2f", "4.95")
show("z against 4.95 (printed inputs)", (4.72 - 4.95) / (4.95 * sqrt(2 / 292)), ".2f", "-0.56")
show("z against 5.16 (printed inputs)", (4.72 - 5.16) / (5.16 * sqrt(2 / 292)), ".2f", "-1.03")
n_blk = 2 * (c975 * 4.95 / 0.21) ** 2
show("blocks", n_blk, ",.1f", "4,268.7")
print(f"{int(np.ceil(n_blk)):,} blocks = {20 * int(np.ceil(n_blk)):,} sessions = {20 * int(np.ceil(n_blk)) / A:.0f} years")
""")

md(r"""
**Problem 9.** Jarque–Bera as SciPy computes it (divisor-$T$ moments), from LM14's printed moments and from the data; the $\chi^2_2$ tail $e^{-\mathrm{JB}/2}$ underflows, so compare its base-10 logarithm.
""")

code(r"""
jb_printed = T / 6 * (0.34**2 + 5.27**2 / 4)
jb = stats.jarque_bera(R)
show("JB from -0.34 and 5.27", jb_printed, ",.0f", "6,881")
show("JB from the data", float(jb.statistic), ",.0f", "6,875")
print("SciPy's p-value:", jb.pvalue, "(underflows to 0)")
show("log10 of the p-value, printed inputs", -jb_printed / (2 * log(10)), ".0f", "-1494")
show("log10 of the p-value, data", -float(jb.statistic) / (2 * log(10)), ".0f", "-1493")
""")

md(r"""
**Problem 10.** The calendar family through the packages: `multipletests` with `method="holm"`, `"fdr_bh"` and without a method (Holm–Šidák), and `stats.false_discovery_control`.
""")

code(r"""
for method in ("holm", "fdr_bh"):
    rej, adj_p, _, _ = multipletests(pv, alpha=0.05, method=method)
    print(f"{method}: {int(rej.sum())} rejected; smallest adjusted p {adj_p.min():.3f}")
rej, adj_p, _, _ = multipletests(pv, alpha=0.05)
print(f"default (Holm-Sidak): {int(rej.sum())} rejected")
adj = np.sort(stats.false_discovery_control(pv))
show("BH-adjusted, smallest", adj[0], ".3f", "0.308")
show("BH-adjusted, second", adj[1], ".3f", "0.669")
""")

md(r"""
**Problem 11.** Ten thousand families of 17 independent standard normal statistics, from `default_rng([11, 20261011])`. Model.
""")

code(r"""
Z = np.random.default_rng([11, SEED]).standard_normal((10_000, 17))
c_b = stats.norm.isf(0.025 / 17)
f_u = (np.abs(Z) >= c975 - EPS).any(axis=1).mean()
f_b = (np.abs(Z) >= c_b - EPS).any(axis=1).mean()
show("Bonferroni level", c_b, ".3f", "2.974")
show("share with a rejection, unadjusted", f_u, ".3f", "0.590")
show("its SE", sqrt(f_u * (1 - f_u) / 10_000), ".3f", "0.005")
show("exact", 1 - 0.95**17, ".3f", "0.582")
show("share with a rejection, Bonferroni", f_b, ".3f", "0.051")
show("its SE", sqrt(f_b * (1 - f_b) / 10_000), ".3f", "0.002")
show("exact", 1 - (1 - 0.05 / 17) ** 17, ".5f", "0.04884")
""")

md(r"""
### Extension: the calendar family in each limit regime

Split TR23 at 1 June 2015 and run the 17 calendar tests within each regime: 34 tests, each group against the other days of its own regime. Apply Holm and Benjamini–Hochberg at 5% to all 34 together. Does Wednesday survive in either regime? Does any month? Remember that this adds 34 tests to the module's 29 on the same data: a stability check, not a new discovery.
""")

code(r"""
regime_p = []
for name, sel in (("to 29 May 2015", pre), ("from 1 June 2015", ~pre)):
    x, w, mth = R[sel], wd[sel], mo[sel]
    for g, gsel in [(MONTHS[k - 1], mth == k) for k in range(1, 13)] + [(DAYS[k], w == k) for k in range(5)]:
        regime_p.append((name, g, p2(two_sample(x[gsel], x[~gsel])[0])))
print(f"{len(regime_p)} tests; smallest p-values:", sorted(regime_p, key=lambda r: r[2])[:3])
# your code: apply holm() and bh() (or multipletests) to the 34 p-values
""")

nb = nbf.v4.new_notebook()
nb["cells"] = cells
nb["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                  "language_info": {"name": "python"}}
nbf.write(nb, LAB / "LM21_lab.ipynb")

(LAB / "README.md").write_text("""# LM21 Lab — Hypothesis Testing and Multiple Testing

Companion to *From Calculus to Kelly*, Learning Module 21. The notebook rebuilds the module's exhibits and computational examples (tests of TAIEX's mean, of its up days and of its signs, the two limit regimes, power and the years a Sharpe ratio needs, the calendar family with shuffled dates, Holm and Benjamini–Hochberg, and a search over 10,000 random rules) and works the computational practice problems.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM21_lab/LM21_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM21_lab.ipynb
```

`build/make_lab21.py` generates the notebook and this README: edit the generator, not the generated files.

## Data (FinMind; not in the repository)

The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

The same steps in a shell (`data/raw/` and this folder's `data/` are git-ignored):

```bash
export FINMIND_TOKEN=...               # your FinMind API token
uv run python data/fetch_finmind.py    # rebuilds and verifies data/raw/
uv run python data/make_lab_data.py    # writes every lab's data/ folder
```

`fetch_finmind.py` checks every file against `data/raw_manifest.json`. The notebook reads only the file in its own `data/` folder:

| File | Content |
|:--|:--|
| `data/taiex_tr.csv` | `date`, `price`: the daily closes of the TAIEX total-return index (FinMind `TaiwanStockTotalReturnIndex`, data_id TAIEX), 2003-01-02 → 2026-10-08 |
""", encoding="utf-8", newline="\n")
print("wrote", LAB / "LM21_lab.ipynb", "and README.md | labels:", {k: ("X" if w == "Exhibit" else "E") + str(n) for k, (w, n) in NUM.items()})
