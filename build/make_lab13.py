"""Generate labs/LM13_lab (Polars-first notebook + README) for LM13, Probability Foundations and Bayes.

Run:  uv run python build/make_lab13.py
Then execute from inside the lab folder:
      cd labs/LM13_lab && uv run jupyter nbconvert --to notebook --execute --inplace LM13_lab.ipynb

The notebook reads only labs/LM13_lab/data/taiex_tr.csv (the TAIEX total-return index as FinMind serves it), which
data/make_lab_data.py builds from data/raw/ (FinMind's licence keeps raw data out of the repository). This script
writes the notebook and the README only.

Exhibit and example numbers are never typed by hand: cells write [[ex:label]] / [[eg:label]], and the generator
resolves them from the labels in src/lm13.md, numbered in document order as build/build.py does. Other modules are
named in plain text (LM14), never as [[LM14]].
"""
import re
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "LM13_lab"
LAB.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- exhibit / example numbers from the module's labels
NUM: dict[str, tuple[str, int]] = {}
_count = {"exhibit": 0, "example": 0}
for m in re.finditer(r"(?m)^(?:>\s?)+\[!(exhibit|example)\][+-]?\s*(.*)$", (ROOT / "src" / "lm13.md").read_text(encoding="utf-8")):
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
    assert not re.search(r"\[\[(ex:|eg:|LM\d)", out), out
    return out


cells: list = []


def md(s: str) -> None:
    cells.append(nbf.v4.new_markdown_cell(refs(s.strip("\n"))))


def code(s: str) -> None:
    cells.append(nbf.v4.new_code_cell(refs(s.strip("\n"))))


md(r"""
# LM13 Lab — Probability Foundations and Bayes

Companion notebook to **From Calculus to Kelly, LM13**. It rebuilds the module's exhibits and computational examples from the TR23 closes, recounts every threshold with exact fractions, solves the computational practice problems, and ends with an extension exercise.

| Part | Rebuilds |
|:--|:--|
| 1 | Data: TR23's returns, the pair space and an exact recount of the threshold days |
| 2 | Events and the axioms: indicators, (13.1), (13.2), [[eg:twofalls]] and the counts of [[ex:venn]] |
| 3 | Conditional probability: the case ([[ex:case]]), [[ex:buckets]], [[eg:fallsinarow]], [[eg:tail]] |
| 4 | Independence: [[ex:signs]], [[eg:pairwise]] by enumeration, [[eg:atleastone]] and other block lengths |
| 5 | Total probability and Bayes' rule: [[ex:regimetab]], [[eg:regimes]], [[eg:casebayes]] three ways, [[eg:manager]] |
| 6 | Random variables: [[eg:rvtrades]] by enumeration, [[ex:ecdf]], [[ex:bins]], the step at a point |
| 7 | Practice problems 4, 5, 6, 7, 10 and 11, and an extension exercise |

**Environment.** From the repository root, `uv sync` installs the locked Python environment (`uv.lock`). Open this notebook with the `.venv` kernel, or run `uv run --with jupyterlab jupyter lab`.

**Data.** The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

`data/` then holds `taiex_tr.csv` (`date`, `price`): the closes of the TAIEX total-return index (FinMind `TaiwanStockTotalReturnIndex`, data_id TAIEX) from 2 January 2003 to 8 October 2026. The notebook reads nothing outside `data/`.

**Conventions (as in the module).** TR23: $T=5{,}849$ simple daily returns from 3 January 2003; the pair space is the 5,848 return dates with a previous return, triples the 5,847 dates with two. Thresholds are inclusive and counted with one guard, `R <= x + 1e-12` and `R >= x - 1e-12`, checked against exact fractions. A fall is $R\le-3\%$ and a big move $\lvert R\rvert\ge2\%$. The limit regimes are the return dates up to 29 May 2015 (7%) and from 1 June 2015 (10%). Every frequency describes the sample; the independent-days figures are a model, and the regime comparison is a stability check. Each `show` line prints a value beside the module's printed value and stops if they differ.
""")

code(r"""
from fractions import Fraction
from itertools import product
from pathlib import Path
import math
import numpy as np
import polars as pl
import matplotlib.pyplot as plt

DATA = Path("data")
EPS = 1e-12
pl.Config.set_tbl_rows(20)
plt.rcParams.update({"figure.figsize": (9, 4.2), "axes.grid": True, "grid.alpha": 0.3,
                     "axes.spines.top": False, "axes.spines.right": False})


def show(label, value, fmt, printed):
    # print a value next to the module's printed value; stop if they differ at the printed precision
    got = format(value, fmt)
    print(f"{label}: {got}   [book: {printed}]")
    assert got == printed, (label, got, printed)
""")

md(r"""
## Part 1 — Data: returns, the pair space and exact ties

The return of a day is the close divided by the previous close, minus 1. `shift(1)` leaves a null in the first row, so `R` has one null and `R_prev`, yesterday's return, has two.
""")

code(r"""
tr = pl.read_csv(DATA / "taiex_tr.csv").sort("date")
df = (tr.with_columns(R=pl.col("price") / pl.col("price").shift(1) - 1)
        .with_columns(R_prev=pl.col("R").shift(1), R_prev2=pl.col("R").shift(2), prev_date=pl.col("date").shift(1)))
days = df.drop_nulls("R")                  # the T returns
pairs = df.drop_nulls("R_prev")            # the pair space
triples = df.drop_nulls("R_prev2")         # three consecutive returns
T = days.height
show("closes", tr.height, ",", "5,850")
show("T", T, ",", "5,849")
show("pair space", pairs.height, ",", "5,848")
show("triples", triples.height, ",", "5,847")
print("returns", days["date"][0], "to", days["date"][-1], "; pairs from", pairs["date"][0], "; triples from", triples["date"][0])
show("first return", days["R"][0], "+.2%", "+2.24%")
""")

code(r"""
# exact returns from the two-decimal closes: the guard must agree with them at every threshold
closes = [Fraction(f"{x:.2f}") for x in tr["price"]]
assert all(float(c) == x for c, x in zip(closes, tr["price"]))
RF = [b / a - 1 for a, b in zip(closes, closes[1:])]
R = days["R"].to_numpy()
ties = {c: sum(r == Fraction(c, 100) for r in RF) for c in range(-5, 6)}
print("returns exactly equal to c% for c = -5..5:", ties)
print("distinct returns:", len(set(RF)))
for c in range(-10, 11):
    assert ((R <= c / 100 + EPS) == np.array([r <= Fraction(c, 100) for r in RF])).all(), c
    assert ((R >= c / 100 - EPS) == np.array([r >= Fraction(c, 100) for r in RF])).all(), c
print("the guarded counts agree with the exact counts at every whole percent from -10% to +10%")
""")

md(r"""
## Part 2 — Events and the axioms

An event on the pair space is a boolean column. Inclusion–exclusion (13.1) and the union bound (13.2) on [[eg:twofalls]]: $A$ is a fall of 2% or more today, $B$ one yesterday.
""")

code(r"""
cnt = pairs.select(
    A=(pl.col("R") <= -0.02 + EPS).sum(),
    B=(pl.col("R_prev") <= -0.02 + EPS).sum(),
    AB=((pl.col("R") <= -0.02 + EPS) & (pl.col("R_prev") <= -0.02 + EPS)).sum(),
    AorB=((pl.col("R") <= -0.02 + EPS) | (pl.col("R_prev") <= -0.02 + EPS)).sum(),
).row(0, named=True)
nP = pairs.height
print(cnt)
assert cnt["AorB"] == cnt["A"] + cnt["B"] - cnt["AB"]            # (13.1) in counts
print("regions of the venn diagram: A only", cnt["A"] - cnt["AB"], "both", cnt["AB"],
      "B only", cnt["B"] - cnt["AB"], "neither", nP - cnt["AorB"])
show("E2 union", cnt["AorB"] / nP, ".2%", "7.97%")
show("E2 union bound", (cnt["A"] + cnt["B"]) / nP, ".2%", "8.62%")
show("E2 Pr(A)", cnt["A"] / nP, ".4f", "0.0431")
show("E2 both if independent (from the printed 0.0431)", nP * 0.0431 ** 2, ".1f", "10.9")
""")

md(r"""
## Part 3 — Conditional probability

The case ([[ex:case]]): $A$ is a fall of 3% or more today, $B$ a move of 2% or more either way yesterday.
""")

code(r"""
fall = pl.col("R") <= -0.03 + EPS
big = (pl.col("R_prev") <= -0.02 + EPS) | (pl.col("R_prev") >= 0.02 - EPS)
case = (pairs.with_columns(fall=fall, big=big)
             .group_by("big", "fall").agg(days=pl.len())
             .sort("big", "fall", descending=True))
print(case)
c = pairs.select(AB=(fall & big).sum(), A=fall.sum(), B=big.sum()).row(0, named=True)
show("falls after a big move", c["AB"], "d", "32")
show("falls", c["A"], "d", "108")
show("days after a big move", c["B"], "d", "489")
show("Pr(A | B)", c["AB"] / c["B"], ".2%", "6.54%")
show("Pr(A | not B)", (c["A"] - c["AB"]) / (nP - c["B"]), ".2%", "1.42%")
show("hit rate Pr(B | A)", c["AB"] / c["A"], ".2%", "29.63%")
show("false-alarm rate Pr(B | not A)", (c["B"] - c["AB"]) / (nP - c["A"]), ".2%", "7.96%")
show("Pr(B)", c["B"] / nP, ".2%", "8.36%")
show("falls among all days", c["A"] / T, ".2%", "1.85%")
""")

md(r"""
[[ex:buckets]]: the share of days that fell 3% or more, by yesterday's return. A bucket $(lo, hi]$ is "not at or below $lo$, and at or below $hi$", with the guard at both ends.
""")

code(r"""
edges = [(None, -3), (-3, -2), (-2, -1), (-1, 0), (0, 1), (1, 2), (2, 3), (3, None)]
rows = []
for lo, hi in edges:
    m = pl.lit(True)
    if lo is not None:
        m = m & ~(pl.col("R_prev") <= lo / 100 + EPS)
    if hi is not None:
        m = m & (pl.col("R_prev") <= hi / 100 + EPS)
    d = pairs.select(days=m.sum(), falls=(m & fall).sum()).row(0, named=True)
    rows.append({"bucket": f"({lo}, {hi}]", **d, "share": d["falls"] / d["days"]})
buckets = pl.DataFrame(rows)
print(buckets)
assert buckets["days"].sum() == nP and buckets["falls"].sum() == c["A"]
show("after a fall of 3% or more", rows[0]["share"], ".2%", "12.04%")
show("after a rise of more than 3%", rows[-1]["share"], ".2%", "4.48%")
plt.bar(buckets["bucket"], buckets["share"] * 100)
plt.axhline(100 * c["A"] / nP, ls="--", c="grey")
plt.ylabel("share that fell 3% or more today (%)"); plt.xlabel("yesterday's return (%)")
plt.show()
""")

code(r"""
# two falls in a row, and inside the tail
ff = pairs.select(both=(fall & (pl.col("R_prev") <= -0.03 + EPS)).sum(),
                  yest=(pl.col("R_prev") <= -0.03 + EPS).sum()).row(0, named=True)
show("[[eg:fallsinarow]] Pr(fall today | fall yesterday)", ff["both"] / ff["yest"], ".2%", "12.04%")
show("[[eg:fallsinarow]] both", ff["both"] / nP, ".3%", "0.222%")
show("[[eg:fallsinarow]] ratio to the base rate", (ff["both"] / ff["yest"]) / (c["A"] / nP), ".1f", "6.5")
show("[[eg:fallsinarow]] pairs if independent", ff["yest"] * c["A"] / nP, ".1f", "2.0")
t = days.select(n3=(pl.col("R") <= -0.03 + EPS).sum(), n4=(pl.col("R") <= -0.04 + EPS).sum(),
                n5=(pl.col("R") <= -0.05 + EPS).sum(),
                mean3=pl.col("R").filter(pl.col("R") <= -0.03 + EPS).mean()).row(0, named=True)
show("[[eg:tail]] Pr(R <= -5% | R <= -3%)", t["n5"] / t["n3"], ".1%", "13.9%")
show("[[eg:tail]] Pr(R <= -4% | R <= -3%)", t["n4"] / t["n3"], ".1%", "40.7%")
show("[[eg:tail]] average of the falls", t["mean3"], ".2%", "-4.06%")
""")

md(r"""
## Part 4 — Independence

[[ex:signs]]: signs of consecutive days, and the counts that independence with the same margins would give.
""")

code(r"""
signs = (pairs.with_columns(yd=pl.col("R_prev") < 0, td=pl.col("R") < 0)
              .group_by("yd", "td").agg(n=pl.len()).sort("yd", "td", descending=True))
print(signs)
s = {(r["yd"], r["td"]): r["n"] for r in signs.iter_rows(named=True)}
row = {y: s[(y, True)] + s[(y, False)] for y in (True, False)}
col = {d: s[(True, d)] + s[(False, d)] for d in (True, False)}
show("down after down", s[(True, True)], ",", "1,226")
show("share down after down", s[(True, True)] / row[True], ".4f", "0.4639")
show("share down after up", s[(False, True)] / row[False], ".4f", "0.4424")
for y in (True, False):
    for d in (True, False):
        print("if independent", "down" if y else "up", "->", "down" if d else "up", f"{row[y] * col[d] / nP:,.1f}")
show("if independent, down after down", row[True] * col[True] / nP, ",.1f", "1,195.0")
""")

code(r"""
# [[eg:pairwise]] by enumeration: two fair trades, four equally likely outcomes
omega = ["".join(w) for w in product("+-", repeat=2)]
pr = lambda ev: Fraction(sum(1 for w in omega if ev(w)), len(omega))
A1, A2, A3 = (lambda w: w[0] == "+"), (lambda w: w[1] == "+"), (lambda w: w[0] == w[1])
for a, b, name in ((A1, A2, "A1 A2"), (A1, A3, "A1 A3"), (A2, A3, "A2 A3")):
    print(name, pr(lambda w: a(w) and b(w)), "=", pr(a) * pr(b))
print("all three:", pr(lambda w: A1(w) and A2(w) and A3(w)), "against", pr(A1) * pr(A2) * pr(A3))
""")

code(r"""
# [[eg:atleastone]]: at least one fall of 3% or more in blocks of n sessions, model against data
p1 = c["A"] / T
fall_np = R <= -0.03 + EPS


def blocks(n):
    nb = T // n
    return nb, T - nb * n, int(fall_np[: nb * n].reshape(nb, n).any(axis=1).sum())


show("Pr(A), five digits", p1, ".4%", "1.8465%")
show("model, 20 sessions", 1 - (1 - 0.018465) ** 20, ".1%", "31.1%")
nb, left, hit = blocks(20)
print("blocks of 20:", nb, "left out:", left, "with a fall:", hit)
show("model blocks", nb * 0.311, ".0f", "91")
show("data, 20 sessions", hit / nb, ".1%", "20.9%")
for n in (5, 10, 60):       # not in the module: the same comparison for other block lengths
    nb, left, hit = blocks(n)
    print(f"{n:>2} sessions: model {1 - (1 - p1) ** n:.1%}, data {hit}/{nb} = {hit / nb:.1%} ({left} returns left out)")
""")

md(r"""
## Part 5 — Total probability and Bayes' rule

[[ex:regimetab]] and [[eg:regimes]]: the 7% and 10% limit regimes (a stability check). Pairs count only when both days lie in one regime.
""")

code(r"""
reg = pl.when(pl.col("date") <= pl.lit("2015-05-29")).then(pl.lit("7%")).otherwise(pl.lit("10%"))
by_day = (days.with_columns(regime=reg)
              .group_by("regime").agg(days=pl.len(), falls=(pl.col("R") <= -0.03 + EPS).sum())
              .sort("regime", descending=True))
print(by_day)
prev_reg = pl.when(pl.col("prev_date") <= pl.lit("2015-05-29")).then(pl.lit("7%")).otherwise(pl.lit("10%"))
inside = (pairs.with_columns(regime=reg, prev_regime=prev_reg)
               .filter(pl.col("regime") == pl.col("prev_regime"))
               .group_by("regime").agg(pairs=pl.len(), falls=fall.sum(), big=big.sum(), both=(fall & big).sum())
               .sort("regime", descending=True))
print(inside)
d7, d10 = (by_day.filter(pl.col("regime") == pl.lit(r)).row(0, named=True) for r in ("7%", "10%"))
show("share of days, 7%", d7["days"] / T, ".2%", "52.61%")
show("fall share, 7%", d7["falls"] / d7["days"], ".2%", "2.34%")
show("fall share, 10%", d10["falls"] / d10["days"], ".2%", "1.30%")
total = Fraction(d7["falls"], d7["days"]) * Fraction(d7["days"], T) + Fraction(d10["falls"], d10["days"]) * Fraction(d10["days"], T)
print("(13.8) in counts:", total, "=", Fraction(c["A"], T))
show("[[eg:regimes]] Pr(10% regime | fall)", d10["falls"] / (d7["falls"] + d10["falls"]), ".1%", "33.3%")
show("[[eg:regimes]] from the rounded 2.34%, 1.30%, 52.6%, 47.4%", 0.0130 * 0.474 / (0.0234 * 0.526 + 0.0130 * 0.474), ".1%", "33.4%")
i10 = inside.filter(pl.col("regime") == pl.lit("10%")).row(0, named=True)
show("10% regime: share that fell after a big move", i10["both"] / i10["big"], ".2%", "8.06%")
show("10% regime: hit rate", i10["both"] / i10["falls"], ".2%", "41.67%")
""")

code(r"""
# [[eg:casebayes]] three ways
base, hit, alarm = c["A"] / nP, c["AB"] / c["A"], (c["B"] - c["AB"]) / (nP - c["A"])
show("(a) counts", c["AB"] / c["B"], ".2%", "6.54%")
show("(b) (13.9), four digits", 0.01847 * 0.2963 / (0.01847 * 0.2963 + 0.98153 * 0.07962), ".2%", "6.54%")
show("(b) the case's rounded inputs", 0.0185 * 0.296 / (0.0185 * 0.296 + 0.9815 * 0.0796), ".2%", "6.55%")
show("(c) prior odds", c["A"] / (nP - c["A"]), ".6f", "0.018815")
show("(c) likelihood ratio", hit / alarm, ".4f", "3.7215")
show("(c) posterior odds", 0.018815 * 3.7215, ".5f", "0.07002")
show("(c) probability", 0.07002 / 1.07002, ".2%", "6.54%")
# [[eg:manager]]
lr = 0.55 ** 8 * 0.45 ** 4 / 0.5 ** 12
show("manager: likelihood ratio", lr, ".4f", "1.4064")
odds = (0.1 / 0.9) * 1.4064
show("manager: posterior odds", odds, ".5f", "0.15627")
show("manager: posterior", odds / (1 + odds), ".1%", "13.5%")
""")

md(r"""
## Part 6 — Random variables

[[eg:rvtrades]] by enumeration: $X=W_2/W_0$ on two trades of LM4's bet at 25 times equity, outcomes equally likely.
""")

code(r"""
mult = {"+": 1 + 25 * 0.02, "-": 1 - 25 * 0.01}
X = {w: mult[w[0]] * mult[w[1]] for w in omega}
pmf = {}
for w, v in X.items():
    pmf[v] = pmf.get(v, Fraction(0)) + Fraction(1, 4)
print("X:", X)
print("pmf:", pmf)
print("F_X(1.125) =", sum(p for v, p in pmf.items() if v <= 1.125), "; Pr(X < 1.125) =", sum(p for v, p in pmf.items() if v < 1.125))
g_star = 0.5 * math.log(1.5) + 0.5 * math.log(0.75)
show("half log 1.125 = g*", 0.5 * math.log(1.125), ".3%", "5.889%")
print("probability-weighted average of the half-logs minus g*:", sum(p * 0.5 * math.log(v) for v, p in pmf.items()) - g_star)
""")

code(r"""
# [[ex:ecdf]]: the empirical distribution function (13.12), and the step at a point
x = np.sort(R)
F = np.arange(1, T + 1) / T
for c_ in (-3, 0, 3):
    n = int((R <= c_ / 100 + EPS).sum())
    print(f"Fhat({c_:+d}%) = {n}/{T} = {n / T:.4f}")
show("Fhat(-3%)", (R <= -0.03 + EPS).mean(), ".4f", "0.0185")
show("Fhat(0)", (R <= 0 + EPS).mean(), ".4f", "0.4520")
show("Fhat(+3%)", (R <= 0.03 + EPS).mean(), ".4f", "0.9885")
show("Pr(-1% < R <= 1%)", ((R <= 0.01 + EPS) & ~(R <= -0.01 + EPS)).mean(), ".4f", "0.7092")
i_min, i_max = int(R.argmin()), int(R.argmax())
print("smallest", days["date"][i_min], f"{R[i_min]:.2%}", "; largest", days["date"][i_max], f"{R[i_max]:+.2%}")
# at a return r, Fhat jumps by 1/T: Fhat(r) counts r, the share strictly below does not
r0 = x[100]
print("at r =", r0, ": Fhat(r) =", (R <= r0).sum(), "/ T, Pr(R < r) =", (R < r0).sum(), "/ T")
plt.step(np.concatenate([[-0.10], x, [0.10]]), np.concatenate([[0], F, [1]]), where="post")
plt.xlim(-0.10, 0.10); plt.xlabel("daily return x"); plt.ylabel("share of days at or below x")
plt.show()
""")

code(r"""
# [[ex:bins]]: the pmf of the 1% bin of R
bins = [(None, -5)] + [(k, k + 1) for k in range(-5, 5)] + [(5, None)]
counts = []
for lo, hi in bins:
    m = np.ones(T, dtype=bool)
    if lo is not None:
        m &= ~(R <= lo / 100 + EPS)
    if hi is not None:
        m &= R <= hi / 100 + EPS
    counts.append(int(m.sum()))
print("counts:", counts, "sum", sum(counts))
print("shares (%):", [round(100 * n / T, 2) for n in counts], "sum of the rounded shares", round(sum(round(100 * n / T, 2) for n in counts), 2))
assert sum(counts[:3]) == c["A"]
plt.bar([f"{lo}..{hi}" for lo, hi in bins], np.array(counts) / T * 100)
plt.xticks(rotation=40); plt.ylabel("probability (%)")
plt.show()
""")

md(r"""
## Part 7 — Practice problems

Problems 4, 5, 6, 7, 10 and 11 of the module.
""")

code(r"""
# Problem 4: falls of 2% or more on the days of the 5,847 triples
f2 = R <= -0.02 + EPS
e0, e1, e2 = f2[:-2], f2[1:-1], f2[2:]
n3 = len(e0)
print("singles", int(e0.sum()), int(e1.sum()), int(e2.sum()), "| pairs", int((e0 & e1).sum()), int((e0 & e2).sum()),
      int((e1 & e2).sum()), "| all three", int((e0 & e1 & e2).sum()))
show("P4 union", (e0 | e1 | e2).mean(), ".2%", "11.19%")
show("P4 union bound", (e0.sum() + e1.sum() + e2.sum()) / n3, ".2%", "12.93%")
# Problem 5: three down days in a row
d = R < 0
d0, d1, d2 = d[:-2], d[1:-1], d[2:]
f1, f2_, f3 = d0.sum() / n3, (d0 & d1).sum() / d0.sum(), (d0 & d1 & d2).sum() / (d0 & d1).sum()
print(f"chain factors {f1:.4f} x {f2_:.4f} x {f3:.4f}")
show("P5 chain", 0.4519 * 0.4637 * 0.4424, ".2%", "9.27%")
show("P5 count", (d0 & d1 & d2).mean(), ".2%", "9.27%")
show("P5 independent days", d0.mean() * d1.mean() * d2.mean(), ".2%", "9.24%")
""")

code(r"""
# Problem 6: the fifty-fifty horizon
n_half = math.log(0.5) / math.log(1 - p1)
show("P6 n", n_half, ".2f", "37.19")
nb, left, hit = blocks(38)
print("blocks of 38:", nb, "left out:", left, "with a fall:", hit)
show("P6 data", hit / nb, ".2%", "32.68%")
# Problem 7: falls of 5% or more by regime
f5 = days.with_columns(regime=reg).group_by("regime").agg(n=(pl.col("R") <= -0.05 + EPS).sum(), days=pl.len())
print(f5.sort("regime", descending=True))
r = {row["regime"]: row for row in f5.iter_rows(named=True)}
show("P7 share, 7%", r["7%"]["n"] / r["7%"]["days"], ".4%", "0.2600%")
show("P7 share, 10%", r["10%"]["n"] / r["10%"]["days"], ".4%", "0.2525%")
show("P7 likelihood ratio", (r["10%"]["n"] / r["10%"]["days"]) / (r["7%"]["n"] / r["7%"]["days"]), ".3f", "0.971")
show("P7 Pr(10% regime | R <= -5%)", r["10%"]["n"] / (r["7%"]["n"] + r["10%"]["n"]), ".1%", "46.7%")
""")

code(r"""
# Problem 10: indicators of down yesterday and down today on the pair space
ind = pairs.select(X=(pl.col("R_prev") < 0).cast(pl.Int64), Y=(pl.col("R") < 0).cast(pl.Int64))
joint = (ind["X"] * ind["Y"]).mean()
show("P10 Pr(X=1, Y=1)", joint, ".4f", "0.2096")
show("P10 product of the margins", ind["X"].mean() * ind["Y"].mean(), ".4f", "0.2043")
# Problem 11: the case inside the 10% regime, and the exact check of the thresholds
p10 = pairs.filter(pl.col("prev_date") >= pl.lit("2015-06-01"))
c10 = p10.select(AB=(fall & big).sum(), A=fall.sum(), B=big.sum(), N=pl.len()).row(0, named=True)
print(c10)
show("P11 share after a big move", c10["AB"] / c10["B"], ".2%", "8.06%")
show("P11 hit rate", c10["AB"] / c10["A"], ".2%", "41.67%")
print("returns exactly equal to +2%, -2% or -3%:", sum(r_ in (Fraction(2, 100), Fraction(-2, 100), Fraction(-3, 100)) for r_ in RF))
""")

md(r"""
### Extension: how far back does a big move reach?

Two descriptive questions, with counts beside every share. First, in each limit regime, what share of the days after a move of at least 1%, 1.5%, 2% or 3% either way fell 3% or more? Second, on all days from the sixth return on, how many of the falls had a move of 2% or more anywhere in the previous five sessions? The module prints neither answer; the code below starts both, and the conclusions are yours (LM21 asks whether such gaps exceed chance, and LM26 models the clustering).
""")

code(r"""
for thr in (0.01, 0.015, 0.02, 0.03):
    mv = pl.col("R_prev").abs() >= thr - EPS
    out = (pairs.with_columns(regime=reg, prev_regime=prev_reg)
                .filter(pl.col("regime") == pl.col("prev_regime"))
                .group_by("regime").agg(after=mv.sum(), falls=(mv & fall).sum())
                .with_columns(share=pl.col("falls") / pl.col("after"))
                .sort("regime", descending=True))
    print(f"move of {thr:.1%} or more yesterday:", out.rows())
absR = np.abs(R)
idx = np.arange(5, T)
prev5 = np.array([bool((absR[i - 5:i] >= 0.02 - EPS).any()) for i in idx])
fw = fall_np[idx]
print(f"days {len(idx)}; falls after a big move in the previous five sessions: {int((prev5 & fw).sum())} of "
      f"{int(fw.sum())}, {(prev5 & fw).sum() / fw.sum():.1%} (a lab result; the module does not print it)")
# your code: other windows, other thresholds, each regime
""")

nb = nbf.v4.new_notebook()
nb["cells"] = cells
nb["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                  "language_info": {"name": "python"}}
nbf.write(nb, LAB / "LM13_lab.ipynb")

(LAB / "README.md").write_text("""# LM13 Lab — Probability Foundations and Bayes

Companion to *From Calculus to Kelly*, Learning Module 13. The notebook rebuilds the module's exhibits and computational examples from the TAIEX total-return index (events and the axioms, conditional probability after a big move, independence of consecutive days, total probability and Bayes' rule across the two limit regimes, the empirical distribution function), recounts every threshold with exact fractions, and works the computational practice problems.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM13_lab/LM13_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM13_lab.ipynb
```

`build/make_lab13.py` generates the notebook and this README: edit the generator, not the generated files. Each `show` line prints a value beside the number the module prints and stops if they differ.

## Data (FinMind; not in the repository)

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
| `data/taiex_tr.csv` | `date`, `price`: the daily closes of the TAIEX total-return index (FinMind `TaiwanStockTotalReturnIndex`, data_id TAIEX, cash dividends reinvested), 2003-01-02 → 2026-10-08, 5,850 rows |
""", encoding="utf-8", newline="\n")
print("wrote", LAB / "LM13_lab.ipynb", "and README.md | labels:", {k: ("X" if w == "Exhibit" else "E") + str(n) for k, (w, n) in NUM.items()})
