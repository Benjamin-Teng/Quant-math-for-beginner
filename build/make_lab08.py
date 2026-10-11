"""Generate labs/LM08_lab (Polars-first notebook + README) for LM8.

Run:  uv run python build/make_lab08.py
Then execute from inside the lab folder:
      cd labs/LM08_lab && uv run jupyter nbconvert --to notebook --execute --inplace LM08_lab.ipynb

The notebook reads only the files in labs/LM08_lab/data/, which data/make_lab_data.py builds from data/raw/
(FinMind's licence keeps raw data out of the repository). This script writes the notebook and the README only.

Exhibit and example numbers are never typed by hand: cells write [[ex:label]] / [[eg:label]], and the generator
resolves them from the labels in src/lm08.md, numbered in document order as build/build.py does.
"""
import re
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "LM08_lab"
LAB.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- exhibit / example numbers from the module's labels
NUM, _count = {}, {"exhibit": 0, "example": 0}
for m in re.finditer(r"(?m)^(?:>\s?)+\[!(exhibit|example)\][+-]?\s*(.*)$", (ROOT / "src" / "lm08.md").read_text(encoding="utf-8")):
    _count[m.group(1)] += 1
    lab = re.search(r"\{#([\w-]+)\}\s*$", m.group(2))
    if lab:
        NUM[lab.group(1)] = ("Exhibit" if m.group(1) == "exhibit" else "Example", _count[m.group(1)])


def refs(s):
    """Replace [[ex:a]] and [[eg:a]] by 'Exhibit k' and 'Example k', checking the kind."""
    def rep(m):
        kind, a = m.group(1), m.group(2)
        word, ka = NUM[a]
        assert word == ("Exhibit" if kind == "ex" else "Example"), (kind, a)
        return f"{word} {ka}"
    out = re.sub(r"\[\[(ex|eg):([\w-]+)\]\]", rep, s)
    assert not re.search(r"\[\[(ex|eg):", out), out
    return out


cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(refs(s.strip("\n"))))
code = lambda s: cells.append(nbf.v4.new_code_cell(refs(s.strip("\n"))))

md(r"""
# LM8 Lab — Vectors and Matrices

Companion notebook to **From Calculus to Kelly, LM8**. It rebuilds the module's exhibits and computational examples from verified price files, solves the computational practice problems, and ends with an extension exercise.

| Part | Rebuilds |
|:--|:--|
| 1 | The case week: TX, 0050 and 00679B joined on their dates; shapes and units ([[ex:case]], [[eg:shapes]]) |
| 2 | P&L as a dot product, in exact decimals and in floating point; simple against log returns across assets ([[eg:lines]], [[eg:expo]], [[ex:pnl-lines]]) |
| 3 | Net and gross exposure, norms and distances ([[eg:netgross]], [[ex:balls]]) |
| 4 | Cauchy–Schwarz, projections and angles on data columns ([[eg:angle]], [[ex:cs-proof]]) |
| 5 | Correlation as a cosine: the week by hand, the ETF frames, the sector sample with its repair, the six pairs ([[eg:weekcorr]], [[eg:bound]], [[ex:plane]], [[ex:angles]]) |
| 6 | The data matrix: $X$, $Y$, $X\mathbf w$, $Y\mathbf h$ and the drift of a fixed book's exposures ([[ex:week]], [[eg:xw]]) |
| 7 | Matrix products: $XK$, associativity, $(MK)^{\top}=K^{\top}M^{\top}$, $I$, $MK\ne KM$ ([[ex:xk]], [[eg:yh]]) |
| 8 | Practice-problem solutions and an extension exercise |

**Environment.** From the repository root, `uv sync` installs the locked Python environment (`uv.lock`). Open this notebook with the `.venv` kernel, or run `uv run --with jupyterlab jupyter lab`.

**Data.** The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

`data/` then holds FinMind `TaiwanFuturesDaily` rows for TX (April to October 2025, regular session, every contract month), `TaiwanStockPrice` closes with FinMind's `spread` column for 0050, 00631L and 00679B, their cash dividends from `TaiwanStockDividendResult`, and the closes of TAIEX and of the 30 TWSE sector indices that FinMind serves daily, with the list of closes that the book repairs (Part 5). Prices are unadjusted; dividends and splits are handled explicitly. The notebook reads nothing outside `data/`.

**Conventions (as in the module).** Vectors list (TX, 0050, 00679B) in that order; TX is worth NT\$200 a point per contract. Returns are simple returns; standard deviations and covariances divide by $T$; a correlation is the same with any divisor.
""")

code(r"""
from pathlib import Path
from datetime import date
from decimal import Decimal
import math
import numpy as np
import polars as pl
import matplotlib.pyplot as plt

DATA = Path("data")
pl.Config.set_tbl_rows(40)
pl.Config.set_float_precision(6)
plt.rcParams.update({"figure.figsize": (9, 4.5), "axes.grid": True, "grid.alpha": 0.3,
                     "axes.spines.top": False, "axes.spines.right": False})
NAMES = ["TX", "0050", "00679B"]
""")

md(r"""
## Part 1 — The case week: three instruments joined on their dates

The TX file has one row per listed contract month; keep the April 2025 contract (`contract_date` 202504), which expires on 16 April (its `settlement_price` prints 0.0 that day). An **inner join** on `date` keeps the sessions all three instruments share, so every row of the result describes one date. Taiwan's markets were closed on 3 and 4 April 2025, so the session before 7 April is 2 April.
""")

code(r"""
txall = pl.read_csv(DATA / "TX__2025-04-01__2025-10-31.csv")
tx = (txall.filter(pl.col("contract_date") == 202504)
           .select("date", pl.col("settlement_price").alias("TX"), pl.col("volume").alias("TX_volume")))
print("202504 expires on", tx.filter(pl.col("TX") == 0)["date"].to_list())
e50 = pl.read_csv(DATA / "0050_daily_raw.csv").select("date", pl.col("close").alias("0050"))
e679 = pl.read_csv(DATA / "00679B_daily_raw.csv").select("date", pl.col("close").alias("00679B"))
apr = (tx.join(e50, on="date", how="inner").join(e679, on="date", how="inner")
         .filter(pl.col("date").is_between(pl.lit("2025-04-02"), pl.lit("2025-04-11")))
         .sort("date"))                                   # never rely on row order after a join
for f in ("0050_dividends.csv", "00679B_dividends.csv"):    # no ex-date in the window: price changes are total changes
    d = pl.read_csv(DATA / f).filter(pl.col("date").is_between(pl.lit("2025-04-03"), pl.lit("2025-04-11")))
    assert d.height == 0, f
print("shape:", apr.shape)
apr   # [[ex:case]]: settlement prices in points, closes in NT$ per share; TX_volume is the April contract's regular-session volume
""")

code(r"""
# [[eg:shapes]]: every vector has three entries in the order (TX, 0050, 00679B)
H = np.array([-1, 24_000, 100_000])            # holdings: contracts, shares, shares
MULT = np.array([200, 1, 1])                   # NT$ per unit of quoted price: TX pays NT$200 a point
P = apr.select(NAMES).to_numpy() * MULT        # 6 x 3 prices, NT$ per contract or per share
W0 = 10_000_000                                # equity, NT$
print("h:", H.shape, " P_t (one row of P):", P[0].shape, " P (all dates):", P.shape)
print("P on 2 April, NT$ per unit:", P[0])
H_B = np.array([-1, 20_000, 100_000])          # the second trader's book
print("combined book:", H + H_B, "  difference:", H - H_B)
""")

md(r"""
## Part 2 — P&L as a dot product; simple against log returns

$\Delta W=\mathbf h^{\top}\Delta\mathbf P$ (8.2) and $\Delta W=W_0\mathbf f^{\top}\mathbf R$ (8.4). Prices have two decimals, so 176.00 → 158.40 is **exactly** −10%. Floating point does not see that: `158.4/176.0 - 1` and `(158.4 - 176.0)/176.0` both miss −0.1 in the last digit, so a count against a limit needs a guard or exact arithmetic (`Decimal`).
""")

code(r"""
dP = np.diff(P, axis=0)                        # 5 x 3 price changes (rows: 7, 8, 9, 10, 11 April)
lines7 = H * dP[0]
print("7 April, line by line (NT$):", lines7.round(2), "  book:", round(float(H @ dP[0]), 2))   # [[eg:lines]]

# the same in exact decimals, from the prices as printed
Pd = [[Decimal(repr(float(v))) for v in row] for row in apr.select(NAMES).rows()]
dPd = [(Pd[1][i] - Pd[0][i]) * (200 if i == 0 else 1) for i in range(3)]
print("exact:", [str(int(h) * d) for h, d in zip(H, dPd)], "sum", str(sum(int(h) * d for h, d in zip(H, dPd))))
print("floats:", 158.4 / 176.0 - 1, (158.4 - 176.0) / 176.0, "  Decimal:", Decimal("158.4") / Decimal("176.0") - 1)
R = P[1:] / P[:-1] - 1                         # 5 x 3 simple returns (the 200 multiplier cancels for TX)
print("R <= -0.10 on 7 April:", R[0, 1] <= -0.10, "  with a guard:", R[0, 1] <= -0.10 + 1e-12)

f = H * P[0] / W0                              # exposures at the close of 2 April
print("f =", f, "  f_i R_i =", (f * R[0]).round(6), "  W0 f'R =", round(W0 * f @ R[0], 2))     # [[eg:expo]]
""")

code(r"""
# simple returns combine with weights, log returns do not: a 60/40 mix of 0050 and 00679B on 7 April
w = np.array([0.0, 0.6, 0.4])
Rp = w @ R[0]
print(f"w'R = {Rp:.4%};  its log return ln(1 + w'R) = {math.log1p(Rp):.4%};  but w'r = {w @ np.log1p(R[0]):.4%}")

# [[ex:pnl-lines]]: each line's daily P&L for the fixed book
LINES = H * dP
days = ["7 Apr", "8 Apr", "9 Apr", "10 Apr", "11 Apr"]
fig, ax = plt.subplots()
for k, (nm, lab) in enumerate(zip(NAMES, ("TX, 1 contract short", "0050, 24,000 shares", "00679B, 100,000 shares"))):
    ax.bar(np.arange(5) + (k - 1) * 0.27, LINES[:, k], width=0.27, label=lab)
ax.axhline(0, color="black", lw=0.8); ax.set_xticks(range(5), days); ax.set_ylabel("NT$")
ax.set_title("[[ex:pnl-lines]]: daily P&L of each line"); ax.legend(); plt.show()
print("daily book P&L, Y h:", (dP @ H).round(2))
""")

md(r"""
## Part 3 — Net and gross exposure, norms and distances ([[eg:netgross]], [[ex:balls]])
""")

code(r"""
print(f"net exposure 1'f = {f.sum():.5f}   gross exposure ||f||_1 = {np.abs(f).sum():.5f}")
print(f"in NT$: net {W0 * f.sum():,.0f}, gross {W0 * np.abs(f).sum():,.0f}")
feq = f[:2]                                    # the equity lines (TX, 0050)
print(f"(f_TX, f_0050) = {feq.round(3)}: Euclidean norm {np.linalg.norm(feq):.3f}, 1-norm {np.abs(feq).sum():.3f}, net {feq.sum():.3f}")
print("distance between (0.6, 0.4) and (0.5, 0.5):", round(float(np.linalg.norm(np.array([0.6, 0.4]) - np.array([0.5, 0.5]))), 4))

th = np.linspace(0, 2 * np.pi, 361)
fig, ax = plt.subplots(figsize=(5.5, 5.5))
ax.plot(np.cos(th), np.sin(th), label="Euclidean norm 1")
ax.plot([1, 0, -1, 0, 1], [0, 1, 0, -1, 0], label="1-norm 1")
ax.plot([-1.25, 1.25], [1.25, -1.25], "--", color="grey", label="net exposure 0")
ax.plot(*feq, "ko"); ax.annotate("case", feq, textcoords="offset points", xytext=(6, 6))
ax.set_aspect("equal"); ax.set_xlabel("f_TX"); ax.set_ylabel("f_0050"); ax.set_title("[[ex:balls]]"); ax.legend(loc="lower left"); plt.show()
""")

md(r"""
## Part 4 — Cauchy–Schwarz, projections and angles on data columns

The inequality $\lvert\mathbf x^{\top}\mathbf y\rvert\le\lVert\mathbf x\rVert\lVert\mathbf y\rVert$ (8.6) is checked on real columns, not on random numbers: the week's return columns of the three instruments. The proof's $a^*=\mathbf x^{\top}\mathbf y/\lVert\mathbf y\rVert^2$ leaves a remainder $\mathbf x-a^*\mathbf y$ orthogonal to $\mathbf y$ ([[ex:cs-proof]]).
""")

code(r"""
def cos(x, y):
    return float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y)))

for i, j in ((0, 1), (1, 2), (0, 2)):
    x, y = R[:, i], R[:, j]
    a = x @ y / (y @ y)
    print(f"{NAMES[i]:>6} / {NAMES[j]:<6} |x'y| = {abs(x @ y):.6f} <= {np.linalg.norm(x) * np.linalg.norm(y):.6f};"
          f"  a* = {a:+.4f}, x - a*y orthogonal to y: {abs((x - a * y) @ y) < 1e-12};"
          f"  uncentred angle {math.degrees(math.acos(cos(x, y))):.2f} deg")
# [[eg:angle]] and the picture of [[ex:cs-proof]]
for x, y in ((np.array([0.6, 0.4]), np.array([0.5, 0.5])), (feq, np.ones(2)), (np.array([1.5, 2.5]), np.array([3.0, 1.0]))):
    print(f"x = {x}, y = {y}: cos = {cos(x, y):.5f}, angle = {math.degrees(math.acos(cos(x, y))):.2f} deg, a* = {x @ y / (y @ y):.4f}")
""")

md(r"""
## Part 5 — Correlation as a cosine

**The week by hand ([[eg:weekcorr]]).** Centre each column, then take the cosine (8.9). The divisor cancels: `np.corrcoef`, `np.cov` with `ddof=0` or `ddof=1`, and the cosine of the centred vectors all give the same number.
""")

code(r"""
x, y = 100 * R[:, 1], 100 * R[:, 2]            # 0050 and 00679B, in percent
# by hand, as the module prints it: inputs to 4 decimals, means to 5, centred values and products to 4
xh, yh = x.round(4), y.round(4)
xb, yb = round(xh.mean(), 5), round(yh.mean(), 5)
xch, ych = (xh - xb).round(4), (yh - yb).round(4)
prh = (xch * ych).round(4)
print("means:", xb, yb)
print(pl.DataFrame({"date": days, "x": xh, "y": yh, "x~": xch, "y~": ych, "x~ y~": prh}))
rho_h = 25.989 / math.sqrt(230.775 * 45.851)     # from the printed sums, as [[eg:weekcorr]] does
print(f"sum x~y~ = {prh.sum():.4f}; |x~|^2 = {xch @ xch:.3f}; |y~|^2 = {ych @ ych:.3f}; "
      f"rho = {rho_h:.4f}, angle {math.degrees(math.acos(round(rho_h, 4))):.1f} deg; "
      f"uncentred {xh @ yh:.3f} / sqrt({xh @ xh:.3f} x {yh @ yh:.3f})")
# the same from the unrounded returns
xc, yc = x - x.mean(), y - y.mean()
rho_w = cos(xc, yc)
print(f"unrounded: cosine of the centred vectors {rho_w:.4f} (angle {math.degrees(math.acos(rho_w)):.2f} deg); uncentred {cos(x, y):.4f}")
for ddof in (0, 1):
    S = np.cov(x, y, ddof=ddof)
    print(f"ddof={ddof}: cov / (s_x s_y) = {S[0, 1] / math.sqrt(S[0, 0] * S[1, 1]):.4f}")
print("np.corrcoef:", round(float(np.corrcoef(x, y)[0, 1]), 4))
""")

md(r"""
**The ETF frames.** The pairs of 0050 with 00631L and with 00679B use total returns, rebuilt as the LM1 and LM7 labs do. Each fund's total-return index runs on its own dates, $G_t=(P_t+D_t)/(P_{t-1}/s_t)$, with the cash dividend $D_t$ of every row of the dividend file and the split ratio $s_t$ (4 for 0050 on 2025-06-18, 22 for 00631L on 2026-03-31, 1 otherwise). The two indices are joined on their common dates, and returns run between consecutive common dates: 0050 was halted 11–17 June 2025 and 00631L 25–30 March 2026, so a return across a halt spans several sessions. Every close is first checked against FinMind's `spread`; the only mismatches allowed are ex-dividend and split days.
""")

code(r"""
SPLITS = {"0050": ("2025-06-18", 4.0), "00631L": ("2026-03-31", 22.0)}

def tr_index(sym):
    raw = pl.read_csv(DATA / f"{sym}_daily_raw.csv").sort("date")
    dfile = DATA / f"{sym}_dividends.csv"
    div = (pl.read_csv(dfile).select("date", pl.col("cash_dividend").alias("D")) if dfile.exists()
           else pl.DataFrame({"date": [], "D": []}, schema={"date": pl.Utf8, "D": pl.Float64}))
    sdate, k = SPLITS.get(sym, ("", 1.0))
    gap = (pl.col("close") - pl.col("close").shift(1) - pl.col("spread")).abs()
    bad = set(raw.with_columns(gap.alias("gap")).filter(pl.col("gap") > 0.005)["date"])
    assert bad <= set(div["date"]) | {sdate}, sorted(bad - set(div["date"]))
    return (raw.join(div, on="date", how="left").sort("date")
               .with_columns(pl.col("D").fill_null(0.0),
                             pl.when(pl.col("date") == pl.lit(sdate)).then(pl.lit(k)).otherwise(pl.lit(1.0)).alias("s"))
               .with_columns(((pl.col("close") + pl.col("D")) / (pl.col("close").shift(1) / pl.col("s"))).fill_null(1.0).alias("G"))
               .select("date", pl.col("G").cum_prod().alias(f"I_{sym}")))

def pair(a, b, base=None):
    j = tr_index(a).join(tr_index(b), on="date", how="inner").sort("date")
    if base:
        j = j.filter(pl.col("date") >= pl.lit(base))
    return (j.with_columns((pl.col(f"I_{a}") / pl.col(f"I_{a}").shift(1) - 1).alias(f"R_{a}"),
                           (pl.col(f"I_{b}") / pl.col(f"I_{b}").shift(1) - 1).alias(f"R_{b}"))
             .drop_nulls(f"R_{a}"))

lm1 = pair("0050", "00631L")                    # LM1's frame
lm7 = pair("0050", "00679B", base="2017-01-17")  # LM7's frame
for name, fr, b in (("LM1", lm1, "00631L"), ("LM7", lm7, "00679B")):
    r = np.corrcoef(fr["R_0050"].to_numpy(), fr[f"R_{b}"].to_numpy())[0, 1]
    print(f"{name}: T = {fr.height}, {fr['date'][0]} .. {fr['date'][-1]}, rho(0050, {b}) = {r:.6f}, angle {math.degrees(math.acos(r)):.3f} deg")
assert lm1.height == 2902 and lm7.height == 2363
""")

code(r"""
# [[ex:plane]] and [[eg:bound]]: 0050 and 00679B in their own plane, LM7's sample
a7, b7 = lm7["R_0050"].to_numpy(), lm7["R_00679B"].to_numpy()
T7 = len(a7)
A7 = T7 / ((date(2026, 10, 8) - date(2017, 1, 17)).days / 365.25)
s1, s2, r7 = a7.std() * math.sqrt(A7), b7.std() * math.sqrt(A7), np.corrcoef(a7, b7)[0, 1]
mix = 0.423 * a7 + 0.577 * b7
print(f"A = {A7:.4f}; vols {s1:.3%} and {s2:.3%}; rho {r7:.4f}, angle {math.degrees(math.acos(r7)):.2f} deg")
print(f"42.3/57.7 mix, rebalanced daily: {mix.std() * math.sqrt(A7):.3%} against the bound {0.423 * s1 + 0.577 * s2:.3%}")
print("check from the printed inputs:", round(math.sqrt(0.423**2 * 20.106**2 + 0.577**2 * 13.496**2
      + 2 * 0.423 * 0.577 * -0.1056 * 20.106 * 13.496), 3), "%")
th7 = math.acos(r7)
v1, v2 = np.array([100 * s1, 0.0]), 100 * s2 * np.array([math.cos(th7), math.sin(th7)])
vm = 0.423 * v1 + 0.577 * v2
fig, ax = plt.subplots(figsize=(6.5, 4.5))
for v, lab in ((v1, "0050"), (v2, "00679B"), (vm, "42.3/57.7 mix")):
    ax.annotate("", v, (0, 0), arrowprops={"arrowstyle": "->", "lw": 2}); ax.text(*v, f" {lab}: {np.linalg.norm(v):.2f}%")
ax.plot([0.423 * v1[0], vm[0], 0.577 * v2[0]], [0.423 * v1[1], vm[1], 0.577 * v2[1]], "--", color="grey")
ax.set_xlim(-3, 25); ax.set_ylim(-1, 15); ax.set_aspect("equal"); ax.set_title("[[ex:plane]] (% a year)"); plt.show()
""")

md(r"""
**The sector sample, with its repair.** FinMind serves some sector closes copied from another date or from another series on the same date (Getting Started, "Check, do not trust"). `sectors_close_repairs.csv` lists every close the book repairs, with the official 13:30:00 value in `close_1330`. **Rule:** replace each listed close with `close_1330`; if `close_1330` is empty, drop that close. On FinMind's free plan `close_1330` is empty, because the 13:30:00 values come from a paid dataset, so every listed close is dropped. Returns stay between consecutive TAIEX-calendar dates, so a dropped close removes the returns into and out of its date.

**U28** is the 28 leaf indices among the 30 TWSE sector indices that FinMind serves daily: all except the aggregates `Electronic` and `ChemicalBiotechnologyMedicalCare`, on one common sample of daily price returns from 2008-12-01. TWSE compiles them as price indices (IndexS03), so their returns leave out cash dividends.
""")

code(r"""
raw = pl.read_csv(DATA / "sectors_close_raw.csv", infer_schema_length=None)
rep = pl.read_csv(DATA / "sectors_close_repairs.csv", infer_schema_length=None,
                  schema_overrides={"close_1330": pl.Float64})
ids = [c for c in raw.columns if c != "date"]
long = raw.unpivot(index="date", on=ids, variable_name="id", value_name="close")
fixed = (long.join(rep.with_columns(pl.lit(True).alias("listed")), on=["id", "date"], how="left")
             .with_columns(pl.when(pl.col("listed").fill_null(False)).then(pl.col("close_1330"))
                           .otherwise(pl.col("close")).alias("close")))
closes = fixed.pivot(on="id", index="date", values="close").sort("date").select("date", *ids)
replaced = rep.filter(pl.col("close_1330").is_not_null()).height
dropped = rep.height - replaced
AGG = ["Electronic", "ChemicalBiotechnologyMedicalCare"]
U28 = [c for c in ids if c not in ("TAIEX", *AGG)]
in_smp = rep.filter(pl.col("id").is_in(U28) & (pl.col("date") >= pl.lit("2008-12-01")))
print(f"rule: replace each listed close with its 13:30:00 value, drop it if that value is missing")
print(f"listed closes: {rep.height}; replaced {replaced}, dropped {dropped}; in the U28 sample: {in_smp.height} closes on {in_smp['date'].n_unique()} dates")

smp = closes.filter(pl.col("date") >= pl.lit("2008-12-01")).sort("date")
ret28 = (smp.select("date", *[(pl.col(c) / pl.col(c).shift(1) - 1).alias(c) for c in U28])
            .slice(1).drop_nulls())
X28 = ret28.select(U28).to_numpy()
T28 = X28.shape[0]
print(f"U28: {len(U28)} indices, T = {T28} returns, {ret28['date'][0]} .. {ret28['date'][-1]}")
assert T28 == (4382 if dropped == 0 else 4307), T28
""")

md(r"""
On a paid plan every listed close is replaced and $T=4{,}382$; on the free plan the 561 listed closes are dropped and $T=4{,}307$. **What changes on the free plan:** every number computed from U28 below, that is the four sector pairs of [[ex:angles]], the largest and smallest of the 378 correlations, the identity check (8.10) and the S3 bound (8.11). The ETF pairs and everything about the case week do not change.
""")

code(r"""
C28 = np.corrcoef(X28, rowvar=False)
iu = np.triu_indices(len(U28), 1)
vals = C28[iu]
kmax, kmin = int(np.argmax(vals)), int(np.argmin(vals))
print(f"{len(vals)} pairs; largest {U28[iu[0][kmax]]} / {U28[iu[1][kmax]]} {vals[kmax]:.4f}; "
      f"smallest {U28[iu[0][kmin]]} / {U28[iu[1][kmin]]} {vals[kmin]:.4f}; median {np.median(vals):.4f}")
ix = {n: i for i, n in enumerate(U28)}
PAIRS = [("0050/00631L", lm1["R_0050"].to_numpy(), lm1["R_00631L"].to_numpy()),
         ("Parts/Computer", X28[:, ix["ElectronicPartsComponents"]], X28[:, ix["ComputerPeripheralEquipment"]]),
         ("Semi/Financial", X28[:, ix["Semiconductor"]], X28[:, ix["FinancialInsurance"]]),
         ("Semi/Food", X28[:, ix["Semiconductor"]], X28[:, ix["Food"]]),
         ("Biotech/OilGas", X28[:, ix["BiotechnologyMedicalCare"]], X28[:, ix["OilGasElectricity"]]),
         ("0050/00679B", a7, b7)]
rows = []
for lab, x, y in PAIRS:
    c = cos(x - x.mean(), y - y.mean())
    rows.append({"pair": lab, "T": len(x), "cosine of centred": c, "np.corrcoef": float(np.corrcoef(x, y)[0, 1]),
                 "angle (deg)": math.degrees(math.acos(c)), "uncentred cosine": cos(x, y)})
ang = pl.DataFrame(rows)
ang   # [[ex:angles]]
""")

code(r"""
fig, ax = plt.subplots()
ax.bar(ang["pair"].to_list(), ang["angle (deg)"].to_numpy())
ax.axhline(90, ls="--", color="grey"); ax.set_ylabel("degrees"); ax.set_title("[[ex:angles]]: angle = arccos(rho)")
plt.xticks(rotation=20); plt.show()

# (8.10): standardized vectors have length sqrt(T); their squared distance is 2T(1 - rho)
x, y = X28[:, ix["Semiconductor"]], X28[:, ix["FinancialInsurance"]]
zx, zy = (x - x.mean()) / x.std(), (y - y.mean()) / y.std()
rho_sf = np.corrcoef(x, y)[0, 1]
print(f"|zx|^2 = {zx @ zx:.2f} = T; squared distance {np.sum((zx - zy)**2):.2f} = 2T(1 - rho) {2 * T28 * (1 - rho_sf):.2f}")
# (8.11): the equal-weight mix of S3, rebalanced daily
S3 = X28[:, [ix[n] for n in ("Semiconductor", "FinancialInsurance", "Food")]]
print(f"S3 equal weights: s_p = {S3.mean(axis=1).std():.4%} a day <= sum w_i s_i = {S3.std(axis=0).mean():.4%}")
""")

code(r"""
# price returns against total returns: 0050 / 00679B on their own common dates, 0050's split day excluded
cal = raw["date"].to_list()                      # the TAIEX calendar

def price_returns(sym, skip=None):
    c = dict(pl.read_csv(DATA / f"{sym}_daily_raw.csv").select("date", "close").iter_rows())
    return {cal[i]: c[cal[i]] / c[cal[i - 1]] - 1 for i in range(1, len(cal))
            if cal[i] in c and cal[i - 1] in c and cal[i] != skip}

pr50, pr679 = price_returns("0050", skip="2025-06-18"), price_returns("00679B")
com = sorted(set(pr50) & set(pr679))
print(f"price returns: T = {len(com)}, rho = {np.corrcoef([pr50[d] for d in com], [pr679[d] for d in com])[0, 1]:.4f}; "
      f"total returns (LM7): rho = {r7:.4f}")
""")

md(r"""
## Part 6 — The data matrix: $X$, $Y$, $X\mathbf w$, $Y\mathbf h$ ([[ex:week]], [[eg:xw]])

Row $t$ of $X$ is $\mathbf R_t^{\top}$ (date first, asset second); row $t$ of $Y$ is $\Delta\mathbf P_t^{\top}$. $X\mathbf w$ is the return series of a portfolio rebalanced to $\mathbf w$ at every close; $Y\mathbf h$ is the P&L of a book that never trades. A fixed book's exposures drift as prices move.
""")

code(r"""
X, Y = R, dP                                   # 5 x 3 each
print("X:", X.shape, " Y:", Y.shape, " X^T:", X.T.shape)
fig, ax = plt.subplots(figsize=(4.5, 4.5))
im = ax.imshow(X, cmap="RdBu", vmin=-0.1, vmax=0.1)
ax.set_xticks(range(3), NAMES); ax.set_yticks(range(5), days)
for (i, j), v in np.ndenumerate(X):
    ax.text(j, i, f"{v:.1%}", ha="center", va="center", color="white" if abs(v) > 0.06 else "black")
ax.grid(False); ax.set_title("[[ex:week]]"); plt.show()

w = np.array([0.0, 0.6, 0.4])
Xw = X @ w
print("[[eg:xw]] X w (%):", (100 * Xw).round(3), f" sum {Xw.sum():.2%}, compounded {np.prod(1 + Xw) - 1:.2%}")
print("by columns:", np.allclose(Xw, 0.6 * X[:, 1] + 0.4 * X[:, 2]))
print("Y h (NT$):", (Y @ H).round(2), " 1'Y h =", round(float(np.ones(5) @ Y @ H), 2),
      " = h'(P_11 - P_2) =", round(float(H @ (P[-1] - P[0])), 2))

# the drift: exposures of the fixed book after 7 April, and the 8 April return
W7 = W0 + H @ dP[0]                            # equity at the close of 7 April: W0 plus that day's P&L
f7 = H * P[1] / W7
print(f"equity at the close of 7 April: {W7:,.0f}")
print("exposures at the close of 2 April:", f.round(3), "  at the close of 7 April:", f7.round(3))
print(f"8 April: the fixed book returned {(H @ dP[1]) / W7:.3%}; the 2 April exposures give {f @ R[1]:.3%}; "
      f"today's exposures give {f7 @ R[1]:.3%}")
""")

md(r"""
## Part 7 — Matrix products ([[ex:xk]], [[eg:yh]])

The columns of $K$ are the weights of three portfolios: 100% 0050, 60/40 and 50/50 in 0050 and 00679B. Each column of $XK$ is one portfolio's return series.
""")

code(r"""
K = np.array([[0, 0, 0], [1, 0.6, 0.5], [0, 0.4, 0.5]])
XK = X @ K
xk = pl.DataFrame({"session": days, "100% 0050": 100 * XK[:, 0], "60/40": 100 * XK[:, 1], "50/50": 100 * XK[:, 2]})
print(xk)
print("sum of daily returns (%):", (100 * XK.sum(axis=0)).round(3))
print("compounded week (%):    ", (100 * (np.prod(1 + XK, axis=0) - 1)).round(3))   # [[ex:xk]]

prop = np.array([0.2, 0.3, 0.5])               # holding the three portfolios in these proportions
print("associative:", np.allclose((X @ K) @ prop, X @ (K @ prop)), " combined weights K prop =", K @ prop)
print("(XK)^T = K^T X^T:", np.allclose((X @ K).T, K.T @ X.T), "  X I = X:", np.allclose(X @ np.eye(3), X))
M1, M2 = np.array([[1, 1], [0, 1]]), np.array([[1, 0], [1, 1]])
print("M1 M2 =", (M1 @ M2).tolist(), " M2 M1 =", (M2 @ M1).tolist())
print("1-D arrays have no orientation:", w.shape, w.T.shape, "  an explicit column:", w.reshape(-1, 1).shape)
""")

code(r"""
# [[eg:yh]]: the week line by line, and the second trader's book
print("week, line by line (NT$):", (H * (P[-1] - P[0])).round(2), " total", round(float(H @ (P[-1] - P[0])), 2))
print("TX fell", f"{-(P[-1, 0] - P[0, 0]) / P[0, 0]:.1%}", "and 0050", f"{-(P[-1, 1] - P[0, 1]) / P[0, 1]:.1%}", "over the week")
print("second trader: 7 April", round(float(H_B @ dP[0]), 2), "; week", round(float(H_B @ (P[-1] - P[0])), 2))
""")

md(r"""
## Part 8 — Practice-problem solutions (computational)
""")

code(r"""
H2 = np.array([2, 0, 200_000])
print("PP2: 8 April P&L of (2, 0, 200,000):", round(float(H2 @ dP[1]), 2))
f2 = H2 * P[0] / W0
print(f"PP3: f = {f2}, net = gross = {f2.sum():.5f}; W0 f'R(7 Apr) = {W0 * f2 @ R[0]:,.2f} = h'dP {H2 @ dP[0]:,.2f}")
wa, wb = np.array([0.5, 0.3, 0.2]), np.array([0.4, 0.3, 0.3])
print(f"PP4: norms {np.linalg.norm(wa):.4f}, {np.linalg.norm(wb):.4f}; distance {np.linalg.norm(wb - wa):.4f}; "
      f"relative {np.linalg.norm(wb - wa) / np.linalg.norm(wa):.4f}; 1-norm {np.abs(wb - wa).sum():.1f} "
      f"(two-way turnover {np.abs(wb - wa).sum():.0%}, one way {np.abs(wb - wa).sum() / 2:.0%})")
x6, y6 = np.array([1.0, 2, 2]), np.array([2.0, 1, 2])
a6 = x6 @ y6 / (y6 @ y6)
print(f"PP6: angle {math.degrees(math.acos(cos(x6, y6))):.2f} deg; a = {a6:.4f} = 8/9; "
      f"x - a y orthogonal to y: {abs((x6 - a6 * y6) @ y6) < 1e-12}")
x7, y7 = np.array([2.0, 4, 0, 2]), np.array([1.0, 3, 1, 3])
for d in (0, 1):
    S7 = np.cov(x7, y7, ddof=d)
    print(f"PP7: divisor {4 - d}: covariance {S7[0, 1]:.4f}, rho {S7[0, 1] / math.sqrt(S7[0, 0] * S7[1, 1]):.4f}")
print(f"PP7: cosine of the centred vectors {cos(x7 - x7.mean(), y7 - y7.mean()):.4f}")
for r in (0.7547, 0.2175):
    print(f"PP9: rho {r}: angle {math.degrees(math.acos(r)):.2f} deg, sqrt(2(1 - rho)) = {math.sqrt(2 * (1 - r)):.4f}")
# PP10, option C: the daily P&Ls W0 X f with the exposures of 2 April against the fixed book's Y h
print("PP10: W0 X f (NT$):", (W0 * (X @ f)).round(2))
print("      Y h (NT$):    ", (Y @ H).round(2))
print("      miss, W0 X f - Y h:", (W0 * (X @ f) - Y @ H).round(2) + 0.0, "(exact on 7 April only)")   # + 0.0: no -0.
# PP11: Part 1 joined the files; the five returns as a Polars frame
wk = pl.DataFrame({"date": apr["date"][1:], "R_0050": R[:, 1], "R_00679B": R[:, 2]})
xa, ya = wk["R_0050"].to_numpy(), wk["R_00679B"].to_numpy()
print("PP11:", round(cos(xa - xa.mean(), ya - ya.mean()), 4), round(float(np.corrcoef(xa, ya)[0, 1]), 4))
""")

md(r"""
### Extension: how far is 00631L from twice 0050?

00631L is the daily 2× fund on 0050's index. If it delivered exactly twice 0050's daily return, the vector $\mathbf x_{00631L}-2\mathbf x_{0050}$ would be zero and the ratio of the lengths would be 2. The cell below measures both on LM1's frame. Then explore: compute the same per calendar year; compare centred and uncentred versions; and find the dates that contribute most to the gap. Which of them are halts or splits, where one return spans several sessions? What else, from Volume I, could make a 2× fund's daily return differ from twice its index's?
""")

code(r"""
x50, x631 = lm1["R_0050"].to_numpy(), lm1["R_00631L"].to_numpy()
gap = x631 - 2 * x50
print(f"root-mean-square gap per day {math.sqrt(np.mean(gap**2)):.4%} (uncentred); "
      f"length ratio |x_00631L| / |x_0050| = {np.linalg.norm(x631) / np.linalg.norm(x50):.4f}")
print(f"centred: {math.sqrt(np.mean((gap - gap.mean())**2)):.4%}, "
      f"{np.linalg.norm(x631 - x631.mean()) / np.linalg.norm(x50 - x50.mean()):.4f}")
# your code: per-year gaps, the largest contributions to |gap|^2, and the dates of the two halts
""")

nb = nbf.v4.new_notebook(); nb["cells"] = cells
nb["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                  "language_info": {"name": "python"}}
nbf.write(nb, LAB / "LM08_lab.ipynb")

(LAB / "README.md").write_text("""# LM8 Lab — Vectors and Matrices

Companion to *From Calculus to Kelly*, Learning Module 8. The notebook joins TX, 0050 and 00679B on their dates for the week of 7–11 April 2025, rebuilds the total-return frames of the ETF pairs and the repaired sample of U28 (the 28 leaf indices among the 30 TWSE sector indices that FinMind serves daily), reproduces the module's exhibits and computational examples, and works the computational practice problems.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM08_lab/LM08_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM08_lab.ipynb
```

`build/make_lab08.py` generates the notebook and this README: edit the generator, not the generated files.

## Data (FinMind; not in the repository)

The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

The same steps in a shell (`data/raw/` and this folder's `data/` are git-ignored):

```bash
export FINMIND_TOKEN=...               # your FinMind API token
uv run python data/fetch_finmind.py    # rebuilds and verifies data/raw/
uv run python data/make_lab_data.py    # writes every lab's data/ folder
```

On FinMind's free plan, fetch with `uv run python data/fetch_finmind.py --exclude sectors_close/`; the sector repair then drops the closes it cannot repair, and Part 5 says which printed numbers change.

`fetch_finmind.py` checks every file against `data/raw_manifest.json`. The notebook reads only the files in its own `data/` folder, which then holds:

| File | Content |
|:--|:--|
| `data/TX__2025-04-01__2025-10-31.csv` | TX daily rows from `TaiwanFuturesDaily`, regular session, every listed contract month: settlement price, close, volume, open interest |
| `data/0050_daily_raw.csv`, `data/00631L_daily_raw.csv`, `data/00679B_daily_raw.csv` | daily closes and FinMind `spread` (unadjusted) from `TaiwanStockPrice` |
| `data/0050_dividends.csv`, `data/00679B_dividends.csv` | ex-dividend dates, before and after prices and cash dividends from `TaiwanStockDividendResult` |
| `data/sectors_close_raw.csv` | the closes FinMind serves for TAIEX and the 30 TWSE sector indices it has daily, one column per series |
| `data/sectors_close_repairs.csv` | every sector close the book repairs, with its 13:30:00 value from `TaiwanStockEvery5SecondsIndex` (empty on the free plan) |

Every ETF close is checked against FinMind's own `spread` column; the only mismatches allowed are ex-dividend days and the splits of 0050 (4-for-1, 2025-06-18) and 00631L (22-for-1, 2026-03-31).
""", encoding="utf-8", newline="\n")
print("wrote", LAB / "LM08_lab.ipynb", "and README.md | labels:", {k: ("X" if w == "Exhibit" else "E") + str(n) for k, (w, n) in NUM.items()})
