"""Generate labs/LM09_lab (Polars-first notebook + README) for LM9.

Run:  uv run python build/make_lab09.py
Then execute from inside the lab folder:
      cd labs/LM09_lab && uv run jupyter nbconvert --to notebook --execute --inplace LM09_lab.ipynb

The notebook reads only the files in labs/LM09_lab/data/ (sectors_close_raw.csv, sectors_close_repairs.csv), which
data/make_lab_data.py builds from data/raw/ (FinMind's licence keeps raw data out of the repository). This script writes
the notebook and the README only.

Exhibit and example numbers are never typed by hand: cells write [[ex:label]] / [[eg:label]], and the generator
resolves them from the labels in src/lm09.md, numbered in document order as build/build.py does.
"""
import re
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "LM09_lab"
LAB.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- exhibit / example numbers from the module's labels
NUM, _count = {}, {"exhibit": 0, "example": 0}
for m in re.finditer(r"(?m)^(?:>\s?)+\[!(exhibit|example)\][+-]?\s*(.*)$", (ROOT / "src" / "lm09.md").read_text(encoding="utf-8")):
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
    assert not re.search(r"\[\[(ex|eg):", out), out
    return out


cells = []


def md(s: str) -> None:
    cells.append(nbf.v4.new_markdown_cell(refs(s.strip("\n"))))


def code(s: str) -> None:
    cells.append(nbf.v4.new_code_cell(refs(s.strip("\n"))))


md(r"""
# LM9 Lab — Linear Systems, Inverses and Rank

Companion notebook to **From Calculus to Kelly, LM9**. It rebuilds the module's exhibits and computational examples from the sector closes, solves the computational practice problems, and ends with an extension exercise.

| Part | Rebuilds |
|:--|:--|
| 1 | The sector closes with the repair rule; the four days ([[ex:days]]); the common sample |
| 2 | Both pictures of the 8–9 April system ([[eg:two]], [[ex:rowpic]], [[ex:colpic]]) |
| 3 | Determinants: areas and angles ([[eg:sliver]], [[ex:area]]), cofactors with `Fraction` against `np.linalg.det` ([[eg:cof]]) |
| 4 | Cramer's rule ([[eg:cramer]]) timed against `solve` for $n=2,\dots,9$, and its cost ([[ex:cost]]) |
| 5 | Elimination with and without row swaps ([[eg:gauss]], [[ex:elim]]) against `solve` |
| 6 | Gauss–Jordan and the inverse ([[ex:inverse]]); LM7's $\Sigma^{-1}$ ([[eg:sigma]]) |
| 7 | Rank and the number of solutions ([[ex:regimes]], [[eg:line]], [[eg:four]], [[ex:wline]], [[ex:triples]]) |
| 8 | Perfect collinearity: the mix column ([[eg:mix]]), the two 50/50 mixes ([[ex:drift]]), U28 and Electronic |
| 9 | Practice problems 4–11 and an extension exercise |

**Environment.** From the repository root, `uv sync` installs the locked Python environment (`uv.lock`). Open this notebook with the `.venv` kernel, or run `uv run --with jupyterlab jupyter lab`.

**Data.** The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

`data/` then holds two files. `sectors_close_raw.csv` has the daily closes that FinMind's `TaiwanStockPrice` serves for TAIEX and the 30 TWSE sector indices, empty where a series has no close. `sectors_close_repairs.csv` lists the 561 closes that FinMind copied from another date or series, each with its official 13:30:00 value from `TaiwanStockEvery5SecondsIndex` (a paid dataset; the column is empty on FinMind's free plan). The notebook reads nothing outside `data/`.

**Conventions (as in the module).** The hand-sized systems use percent returns $100(P_t/P_{t-1}-1)$ of 7–10 April 2025, rounded to 0.01, solved in exact rational arithmetic (`fractions.Fraction`). Section 7 uses daily simple returns on the common sample from the close of 2008-12-01 to 2026-10-08, between consecutive TAIEX trading dates.
""")

code(r"""
from pathlib import Path
from fractions import Fraction
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN
import math
import time
import numpy as np
import polars as pl
import matplotlib.pyplot as plt

DATA = Path("data")
pl.Config.set_tbl_rows(40)
pl.Config.set_fmt_str_lengths(60)
plt.rcParams.update({"figure.figsize": (9, 4), "axes.grid": True, "grid.alpha": 0.3,
                     "axes.spines.top": False, "axes.spines.right": False})


def dec(x, k):
    # an exact rational rounded to k decimals, as text
    q = (Decimal(x.numerator) / Decimal(x.denominator)).quantize(Decimal(1).scaleb(-k), rounding=ROUND_HALF_EVEN)
    return format(q, "f")


def det_cof(m):
    # determinant by cofactor expansion along the first row (n! terms; exact for Fractions)
    n = len(m)
    if n == 1:
        return m[0][0]
    return sum((-1) ** j * m[0][j] * det_cof([row[:j] + row[j + 1:] for row in m[1:]]) for j in range(n))


def rref(m):
    # reduced row echelon form and pivot columns, exact
    a = [list(r) for r in m]
    rows, cols, piv, r = len(a), len(a[0]), [], 0
    for c in range(cols):
        k = next((i for i in range(r, rows) if a[i][c] != 0), None)
        if k is None:
            continue
        a[r], a[k] = a[k], a[r]
        a[r] = [v / a[r][c] for v in a[r]]
        for i in range(rows):
            if i != r and a[i][c] != 0:
                f = a[i][c]
                a[i] = [v - f * w for v, w in zip(a[i], a[r])]
        piv.append(c)
        r += 1
        if r == rows:
            break
    return a, piv


def rank_exact(m):
    return len(rref(m)[1])


def with_col(m, j, v):
    return [row[:j] + [vi] + row[j + 1:] for row, vi in zip(m, v)]


def cramer(m, b):
    d = det_cof(m)
    return [det_cof(with_col(m, j, b)) / d for j in range(len(m))]
""")

md(r"""
## Part 1 — Data: the repair rule, the four days and the common sample

FinMind serves some sector closes copied from another date or another series. The repair cell replaces each close listed in `sectors_close_repairs.csv` by its 13:30:00 value; a listed close without that value (FinMind's free plan) is dropped, never estimated. With every value present, the result equals the closes the module uses, cell for cell.
""")

code(r"""
raw = pl.read_csv(DATA / "sectors_close_raw.csv", infer_schema_length=None).sort("date")
rep = pl.read_csv(DATA / "sectors_close_repairs.csv", infer_schema_length=None,
                  schema_overrides={"close_1330": pl.Float64})
SERIES = raw.columns[1:]                         # TAIEX and the 30 sector ids
AGG = ["Electronic", "ChemicalBiotechnologyMedicalCare"]
U28 = [c for c in SERIES if c not in ["TAIEX", *AGG]]
ELEC8 = ["Semiconductor", "ComputerPeripheralEquipment", "Optoelectronic", "CommunicationsInternet",
         "ElectronicPartsComponents", "ElectronicProductsDistribution", "InformationService", "OtherElectronic"]
closes = raw
for sid in rep["id"].unique().sort().to_list():
    fix = (rep.filter(pl.col("id") == pl.lit(sid))
              .select("date", pl.col("close_1330").alias("_fix"), pl.lit(True).alias("_listed")))
    closes = (closes.join(fix, on="date", how="left")
                    .with_columns(pl.when(pl.col("_listed")).then(pl.col("_fix")).otherwise(pl.col(sid)).alias(sid))
                    .drop("_fix", "_listed").sort("date"))
n_fixed = rep.filter(pl.col("close_1330").is_not_null()).height
in_u28 = rep.filter(pl.col("id").is_in(U28) & (pl.col("date") >= pl.lit("2008-12-01")))
in_sec7 = rep.filter(pl.col("id").is_in(["Electronic", *ELEC8, "FinancialInsurance"])
                     & (pl.col("date") >= pl.lit("2008-12-01")))
print("rule: each listed close is replaced by its 13:30:00 value; without that value it is dropped")
print(f"listed closes {rep.height}: replaced {n_fixed}, dropped {rep.height - n_fixed}")
print(f"in U28 from 2008-12-01: {in_u28.height} closes on {in_u28['date'].n_unique()} dates; "
      f"in Electronic, its eight sub-industries and Financial: {in_sec7.height}")
print(f"{len(SERIES)} series, {closes.height} dates, {closes['date'][0]} -> {closes['date'][-1]}")
""")

code(r"""
# the four days: exact percent returns from the two-decimal closes, rounded to 0.01
DAYS = ["2025-04-07", "2025-04-08", "2025-04-09", "2025-04-10"]
COLS = ["TAIEX", "Semiconductor", "FinancialInsurance", "Food"]
win = closes.filter(pl.col("date").is_between(pl.lit("2025-04-02"), pl.lit("2025-04-10"))).select("date", *COLS)
assert win["date"].to_list() == ["2025-04-02", *DAYS]          # 3-4 April were holidays
assert rep.filter(pl.col("date").is_between(pl.lit("2025-04-02"), pl.lit("2025-04-10"))).height == 0
P = {c: [Fraction(str(round(v, 2))) for v in win[c].to_list()] for c in COLS}
R_exact = {c: [100 * (P[c][k + 1] / P[c][k] - 1) for k in range(4)] for c in COLS}


def round2(x):
    up = (Decimal(x.numerator) / Decimal(x.denominator)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    assert up == (Decimal(x.numerator) / Decimal(x.denominator)).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
    return Fraction(up)


R = {c: [round2(v) for v in R_exact[c]] for c in COLS}
MF = [[R["Semiconductor"][k], R["FinancialInsurance"][k], R["Food"][k]] for k in range(4)]   # rows: days
BF = R["TAIEX"]
days = pl.DataFrame({"session": DAYS, "TAIEX b_i": [float(v) for v in BF],
                     "Semiconductor": [float(r[0]) for r in MF], "Financial": [float(r[1]) for r in MF],
                     "Food": [float(r[2]) for r in MF]})
ties = sorted((abs(100 * v - math.floor(100 * v) - Fraction(1, 2)) / 100, c, d, v)
              for c in COLS for d, v in zip(DAYS, R_exact[c]))
print(f"TAIEX 7 April before rounding: {dec(R_exact['TAIEX'][0], 6)}%")
print(f"closest to a rounding tie: {ties[0][1]} {ties[0][2]} at {dec(ties[0][3], 6)}, {dec(ties[0][0], 6)} away")
days   # [[ex:days]]
""")

code(r"""
# the common sample: closes from 2008-12-01, returns between consecutive TAIEX trading dates
cs = closes.filter(pl.col("date") >= pl.lit("2008-12-01")).sort("date")
rets = cs.with_columns([(pl.col(c) / pl.col(c).shift(1) - 1).alias(c) for c in SERIES]).slice(1)
sample = rets.drop_nulls(subset=[*U28, "Electronic", "TAIEX"])
T = sample.height
print(f"common sample: {cs.height} closes {cs['date'][0]} -> {cs['date'][-1]}; T = {T:,} returns, first {sample['date'][0]}")
""")

md(r"""
## Part 2 — Two pictures of the 8–9 April system

Rows: each day is a line in the plane of the multiples $(x_1,x_2)$. Columns: $x_1\mathbf m_1+x_2\mathbf m_2$ must reach $\mathbf b$, equation (9.1).
""")

code(r"""
M1 = [MF[1][:2], MF[2][:2]]          # 8 and 9 April; Semiconductor, Financial
b1 = BF[1:3]
x1 = cramer(M1, b1)
print("E1: det =", dec(det_cof(M1), 3), " x =", [dec(v, 6) for v in x1])
print("    check: M x =", [dec(sum(a * v for a, v in zip(row, x1)), 6) for row in M1], " b =", [float(v) for v in b1])

fig, (ax_r, ax_c) = plt.subplots(1, 2, figsize=(10, 4.2))
u = np.linspace(0, 2, 50)
for row, rhs, lab in zip(M1, b1, ("8 April", "9 April")):
    a, c, r = float(row[0]), float(row[1]), float(rhs)
    if abs(c) > abs(a):
        ax_r.plot(u, (r - a * u) / c, label=lab)
    else:
        v_ = np.linspace(-1, 1.5, 50)
        ax_r.plot((r - c * v_) / a, v_, label=lab)
ax_r.plot(float(x1[0]), float(x1[1]), "ko")
ax_r.set(xlim=(0, 2), ylim=(-1, 1.5), xlabel="x1 (Semiconductor)", ylabel="x2 (Financial)", title="[[ex:rowpic]]: rows")
ax_r.legend()
m1, m2 = np.array([float(M1[0][0]), float(M1[1][0])]), np.array([float(M1[0][1]), float(M1[1][1])])
p = float(x1[0]) * m1
for start, vec, col, lab in ((np.zeros(2), p, "C0", "1.035 m1"), (p, float(x1[1]) * m2, "C1", "0.207 m2"),
                             (np.zeros(2), np.array([float(v) for v in b1]), "k", "b (TAIEX)")):
    ax_c.annotate("", xy=start + vec, xytext=start, arrowprops=dict(arrowstyle="->", color=col, lw=2))
    ax_c.text(*(start + vec), " " + lab, color=col)
ax_c.set(xlim=(-6, 1.5), ylim=(-7, 0.5), aspect="equal", xlabel="8 April return (%)", ylabel="9 April return (%)",
         title="[[ex:colpic]]: columns")
plt.tight_layout()
plt.show()
""")

md(r"""
## Part 3 — Determinants: area, angle and the cofactor expansion

The $2\times2$ determinant is the signed area spanned by the columns, (9.2): $\lvert\det M\rvert=\lVert\mathbf m_1\rVert\,\lVert\mathbf m_2\rVert\sin\theta$.
""")

code(r"""
def area_angle(m):
    c1 = np.array([float(m[0][0]), float(m[1][0])])
    c2 = np.array([float(m[0][1]), float(m[1][1])])
    n1, n2 = np.linalg.norm(c1), np.linalg.norm(c2)
    return n1, n2, math.degrees(math.acos(c1 @ c2 / (n1 * n2)))


M2 = [[MF[0][0], MF[0][2]], [MF[2][0], MF[2][2]]]   # 7 and 9 April; Semiconductor, Food
b2 = [BF[0], BF[2]]
for name, m, b in (("8, 9 April: Semi, Fin", M1, b1), ("7, 9 April: Semi, Food", M2, b2)):
    n1, n2, th = area_angle(m)
    d = det_cof(m)
    print(f"{name}: det {dec(d, 4)}; |m1| {n1:.6f}, |m2| {n2:.6f}, product {n1 * n2:.4f}; "
          f"sin(theta) {float(d) / (n1 * n2):.4f}; theta {th:.2f} deg; x = {[dec(v, 5) for v in cramer(m, b)]}")
print("ratio of the areas:", round(float(det_cof(M1) / det_cof(M2)), 2), "(about nine)")
""")

code(r"""
# [[eg:cof]]: the 7-9 April system, cofactors with exact fractions against floating point
M3, b3 = MF[:3], BF[:3]
minors = [det_cof([row[:j] + row[j + 1:] for row in M3[1:]]) for j in range(3)]
terms = [(-1) ** j * M3[0][j] * minors[j] for j in range(3)]
D3 = det_cof(M3)
print("minors:", [dec(v, 4) for v in minors], " terms:", [dec(t, 6) for t in terms])
print("det M exact:", dec(D3, 6), "=", D3)
print("np.linalg.det:", repr(np.linalg.det(np.array(M3, dtype=float))))
""")

md(r"""
## Part 4 — Cramer's rule and its cost

Cramer's rule (9.4) with cofactor expansions takes $(n+1)!$ terms; elimination takes about $\tfrac23n^3$ operations. The timing uses real returns: the first $n$ sectors of U28 on the last $n$ days of the sample. Times depend on the machine; the counts do not.
""")

code(r"""
x3 = cramer(M3, b3)
print("[[eg:cramer]]: numerators", [dec(det_cof(with_col(M3, j, b3)), 6) for j in range(3)])
print("               x =", [dec(v, 6) for v in x3], " sum", dec(sum(x3), 3))

rows = []
X_pct = sample.select(U28).to_numpy() * 100
for n in range(2, 10):
    m = X_pct[-n:, :n].tolist()
    b = sample["TAIEX"].to_numpy()[-n:] * 100
    t0 = time.perf_counter()
    xc = cramer(m, b.tolist())
    t1 = time.perf_counter()
    xs = np.linalg.solve(np.array(m), b)
    t2 = time.perf_counter()
    rows.append({"n": n, "(n+1)! terms": math.factorial(n + 1), "2n^3/3 operations": round(2 * n**3 / 3, 1),
                 "Cramer seconds": t1 - t0, "solve seconds": t2 - t1, "max |difference|": float(np.abs(np.array(xc) - xs).max())})
pl.DataFrame(rows)   # [[ex:cost]]: the counts; the times are this machine's
""")

code(r"""
ns = np.arange(2, 21)
plt.semilogy(ns, [math.factorial(n + 1) for n in ns], label="Cramer: (n+1)! terms")
plt.semilogy(ns, 2 * ns**3 / 3, label="Elimination: 2n^3/3 operations")
plt.xlabel("number of unknowns n"); plt.title("[[ex:cost]]"); plt.legend(); plt.show()
print(f"n = 20: 21! = {math.factorial(21):,} terms against {2 * 20**3 / 3:,.0f} operations")
""")

md(r"""
## Part 5 — Gaussian elimination, with and without row swaps

Each step subtracts $\ell_{ik}$ times the pivot row; partial pivoting first swaps up the row whose entry in the pivot column is largest in absolute value.
""")

code(r"""
def eliminate(m, b, pivoting):
    a = [list(r) + [bi] for r, bi in zip(m, b)]
    n = len(a)
    steps, swaps = [], []
    for k in range(n - 1):
        if pivoting:
            p = max(range(k, n), key=lambda i: abs(a[i][k]))
            if p != k:
                a[k], a[p] = a[p], a[k]
                swaps.append((k + 1, p + 1))
        for i in range(k + 1, n):
            ell = a[i][k] / a[k][k]
            a[i] = [v - ell * w for v, w in zip(a[i], a[k])]
            steps.append({"step": k + 1, "row": i + 1, "multiplier": dec(ell, 6),
                          "new row": " ".join(dec(v, 6) for v in a[i])})
    piv = [a[k][k] for k in range(n)]
    x = [Fraction(0)] * n
    for i in reversed(range(n)):
        x[i] = (a[i][n] - sum(a[i][j] * x[j] for j in range(i + 1, n))) / a[i][i]
    return steps, swaps, piv, x


steps, swaps, piv, xg = eliminate(M3, b3, pivoting=False)
print("[[eg:gauss]]: swaps", swaps, " pivots", [dec(v, 6) for v in piv], " x", [dec(v, 6) for v in xg])
print("product of the pivots:", dec(piv[0] * piv[1] * piv[2], 6))
print("np.linalg.solve:", np.linalg.solve(np.array(M3, dtype=float), np.array(b3, dtype=float)).round(6))
pl.DataFrame(steps)   # [[ex:elim]]
""")

md(r"""
## Part 6 — Gauss–Jordan elimination and the inverse

Row-reducing $[M\mid I_3]$ to $[I_3\mid M^{-1}]$ solves the three systems $M\mathbf k_j=\mathbf e_j$ at once. Column $j$ of $M^{-1}$ is the change in the mix per point of TAIEX's return on day $j$.
""")

code(r"""
aug = [list(r) + [Fraction(int(i == j)) for j in range(3)] for i, r in enumerate(M3)]
red, pivcols = rref(aug)
Minv = [r[3:] for r in red]
print("pivot columns:", pivcols)
for r in Minv:
    print("  ", [dec(v, 6) for v in r])
fig, ax = plt.subplots(figsize=(5, 3.6))
im = ax.imshow(np.array(Minv, dtype=float), cmap="RdBu", vmin=-1.1, vmax=1.1)
for i in range(3):
    for j in range(3):
        ax.text(j, i, f"{float(Minv[i][j]):.3f}", ha="center", va="center")
ax.set_xticks(range(3), ["7 April", "8 April", "9 April"]); ax.set_yticks(range(3), ["x1 Semi", "x2 Fin", "x3 Food"])
ax.grid(False); ax.set_title("[[ex:inverse]]"); plt.colorbar(im); plt.show()
print("x = M^-1 b:", [dec(sum(a * v for a, v in zip(r, b3)), 6) for r in Minv])
""")

code(r"""
# [[eg:sigma]]: LM7's covariance matrix and excess returns, as LM7 prints them
S = [[Fraction("0.040425"), Fraction("-0.002866")], [Fraction("-0.002866"), Fraction("0.018214")]]
e = [Fraction("0.22751"), Fraction("-0.02547")]
dS = det_cof(S)
Sinv = [[S[1][1] / dS, -S[0][1] / dS], [-S[1][0] / dS, S[0][0] / dS]]     # formula (9.5)
f_star = [sum(a * v for a, v in zip(r, e)) for r in Sinv]
print("det Sigma =", float(dS), " Sigma^-1 =", [[dec(v, 4) for v in r] for r in Sinv])
print("Kelly fractions =", [dec(v, 4) for v in f_star])
print("np.linalg.inv:", np.linalg.inv(np.array(S, dtype=float)).round(4).tolist())
""")

md(r"""
## Part 7 — Rank and the number of solutions

Two days give a line of mixes, three days one mix, four days none ((9.7), (9.8)).
""")

code(r"""
regimes = []
for name, rows_ in (("7-8 April", [0, 1]), ("7-9 April", [0, 1, 2]), ("7-10 April", [0, 1, 2, 3])):
    m = [MF[r] for r in rows_]
    mb = [MF[r] + [BF[r]] for r in rows_]
    regimes.append({"days": name, "equations x unknowns": f"{len(rows_)} x 3", "rank M": rank_exact(m),
                    "rank [M|b]": rank_exact(mb)})
red2, piv2 = rref([MF[r] + [BF[r]] for r in (0, 1)])
print(f"[[eg:line]]: x1 = {dec(red2[0][3], 6)} + {dec(-red2[0][2], 6)} x3,  x2 = {dec(red2[1][3], 6)} - {dec(red2[1][2], 6)} x3;"
      f"  x_h = ({dec(-red2[0][2], 6)}, {dec(-red2[1][2], 6)}, 1)")
print("[[eg:four]]: det [M|b] =", dec(det_cof([MF[r] + [BF[r]] for r in range(4)]), 6))
pl.DataFrame(regimes)   # [[ex:regimes]]
""")

code(r"""
TRI = {"7, 8, 9": [0, 1, 2], "7, 8, 10": [0, 1, 3], "7, 9, 10": [0, 2, 3], "8, 9, 10": [1, 2, 3]}
tri = []
for name, rows_ in TRI.items():
    m, b = [MF[r] for r in rows_], [BF[r] for r in rows_]
    x = cramer(m, b)
    tri.append({"days (April)": name, "det": dec(det_cof(m), 6), "Semiconductor": float(x[0]), "Financial": float(x[1]),
                "Food": float(x[2])})
tri = pl.DataFrame(tri)
pred = sum(a * v for a, v in zip(MF[3], x3))
print(f"Financial's multiple from {tri['Financial'].min():.3f} to {tri['Financial'].max():.3f}")
print(f"7-9 April mix on 10 April: {dec(pred, 2)}% against TAIEX's {float(BF[3])}%")
tri   # [[ex:triples]]
""")

code(r"""
xp = np.array([float(red2[0][3]), float(red2[1][3])]); xh = np.array([float(-red2[0][2]), float(-red2[1][2])])
s_ = np.linspace(-2, 2, 50)
plt.plot(xp[0] + s_ * xh[0], xp[1] + s_ * xh[1], "k-", label="7-8 April line, x3 from -2 to 2")
for name, col in (("7, 8, 9", "C0"), ("7, 8, 10", "C1")):
    row = tri.filter(pl.col("days (April)") == pl.lit(name))
    plt.plot(row["Semiconductor"][0], row["Financial"][0], "o", color=col, label=f"with {name.split(', ')[-1]} April")
plt.xlabel("x1 (Semiconductor)"); plt.ylabel("x2 (Financial)"); plt.title("[[ex:wline]]"); plt.legend(); plt.show()
""")

md(r"""
## Part 8 — Perfect collinearity

A return matrix has rank below its number of columns exactly when a fixed mix of its columns returns 0 on every date (9.9).
""")

code(r"""
# [[eg:mix]]: replace Food by the daily rebalanced 50/50 mix of Semiconductor and Financial
Mmix = [[r[0], r[1], (r[0] + r[1]) / 2] for r in M3]
print("mix column:", [float(r[2]) for r in Mmix], " exact ranks:", rank_exact(Mmix),
      rank_exact([r + [bi] for r, bi in zip(Mmix, b3)]))
Xm = np.array(Mmix, dtype=float)
print("np.linalg.det:", np.linalg.det(Xm), "(exactly 0 in exact arithmetic)")
try:
    xs = np.linalg.solve(Xm, np.array(b3, dtype=float))
    print("np.linalg.solve returned, largest |x_j| of order 10^%d, along x_h:" % round(math.log10(np.abs(xs).max())),
          (xs / xs[2]).round(6))
except np.linalg.LinAlgError as err:
    print("np.linalg.solve raised LinAlgError:", err)
print("np.linalg.matrix_rank:", np.linalg.matrix_rank(Xm))
""")

code(r"""
# the two 50/50 mixes on the common sample
RS, RF = sample["Semiconductor"].to_numpy(), sample["FinancialInsurance"].to_numpy()
reb = 0.5 * RS + 0.5 * RF
PS, PF = cs["Semiconductor"].to_numpy(), cs["FinancialInsurance"].to_numpy()
V = 0.5 * PS / PS[0] + 0.5 * PF / PF[0]                      # buy-and-hold value from the 2008-12-01 close
w = 0.5 * (PS / PS[0]) / V                                  # its weight in Semiconductor
bh_all = cs.select("date").with_columns(pl.Series("V", V)).with_columns((pl.col("V") / pl.col("V").shift(1) - 1).alias("R_bh"))
bh = sample.select("date").join(bh_all.select("date", "R_bh"), on="date", how="left").sort("date")["R_bh"].to_numpy()
print("matrix_rank, daily rebalanced:", np.linalg.matrix_rank(np.column_stack([RS, RF, reb])),
      " buy-and-hold:", np.linalg.matrix_rank(np.column_stack([RS, RF, bh])))
dts = cs["date"].to_list()
iw_max, iw_min = int(np.nanargmax(w)), int(np.nanargmin(w))
print(f"buy-and-hold weight in Semiconductor: {w[0]:.2f} -> {w[-1]:.3f} on {dts[-1]}; "
      f"min {w[iw_min]:.3f} on {dts[iw_min]}, max {w[iw_max]:.3f} on {dts[iw_max]}")
print(f"largest daily gap between the two mixes: {np.nanmax(np.abs(reb - bh)) * 100:.2f} percentage points")
plt.plot(pl.Series(dts).str.to_date().to_list(), w, label="bought on 1 December 2008 and held")
plt.axhline(0.5, color="C1", ls="--", label="rebalanced to 50/50 every day")
plt.ylabel("weight of Semiconductor"); plt.title("[[ex:drift]]"); plt.legend(); plt.show()
""")

code(r"""
XU = sample.select(U28).to_numpy()
XE = sample.select("Electronic", *ELEC8).to_numpy()
print("U28:", XU.shape, "matrix_rank", np.linalg.matrix_rank(XU))
print("Electronic + eight:", XE.shape, "matrix_rank", np.linalg.matrix_rank(XE))
print(f"correlation of Semiconductor with Electronic: {np.corrcoef(sample['Semiconductor'], sample['Electronic'])[0, 1]:.6f}")
""")

md(r"""
## Part 9 — Practice problems

**Problem 4.** Semiconductor and Food on 7 and 10 April, by Cramer's rule (9.4) and by the inverse formula (9.5).
""")

code(r"""
M4 = [[MF[0][0], MF[0][2]], [MF[3][0], MF[3][2]]]
b4 = [BF[0], BF[3]]
d4 = det_cof(M4)
inv4 = [[M4[1][1] / d4, -M4[0][1] / d4], [-M4[1][0] / d4, M4[0][0] / d4]]
print("det", dec(d4, 4), " Cramer", [dec(v, 5) for v in cramer(M4, b4)],
      " (9.5)", [dec(sum(a * v for a, v in zip(r, b4)), 5) for r in inv4], " sum", dec(sum(cramer(M4, b4)), 3))
""")

md(r"""
**Problems 5 and 6.** Elimination with partial pivoting on 8–10 April; the determinant of 7, 8 and 10 April by cofactors and by pivots.
""")

code(r"""
M5, b5 = MF[1:4], BF[1:4]
steps5, swaps5, piv5, x5 = eliminate(M5, b5, pivoting=True)
print("Problem 5: swaps", swaps5, " pivots", [dec(v, 6) for v in piv5], " x", [dec(v, 6) for v in x5],
      " det", dec(det_cof(M5), 6))
print(pl.DataFrame(steps5))
M6 = [MF[0], MF[1], MF[3]]
minors6 = [det_cof([row[:j] + row[j + 1:] for row in M6[1:]]) for j in range(3)]
steps6, _, piv6, _ = eliminate(M6, [BF[0], BF[1], BF[3]], pivoting=False)
print("Problem 6: minors", [dec(v, 4) for v in minors6], " det", dec(det_cof(M6), 6),
      " pivots", [dec(v, 6) for v in piv6], " product", dec(piv6[0] * piv6[1] * piv6[2], 6))
""")

md(r"""
**Problem 7.** The augmented matrix with the constant $a$: solvable only for $a=2$.
""")

code(r"""
for a in (Fraction(2), Fraction(3)):
    aug7 = [[1, 2, 3, 1], [2, 4, 7, 3], [1, 2, 4, a]]
    red7, piv7 = rref([[Fraction(v) for v in r] for r in aug7])
    print(f"a = {a}: rank M = {rank_exact([[Fraction(v) for v in r[:3]] for r in aug7])}, rank [M|b] = {len(piv7)}, "
          f"reduced rows {[[str(v) for v in r] for r in red7]}")
""")

md(r"""
**Problem 8.** Three discount factors from three illustrative coupon bonds, by forward substitution.
""")

code(r"""
coupons, prices = [2, 3, 4], [Fraction("100.50"), Fraction("102.55"), Fraction("106.25")]
Mb = [[Fraction(coupons[i] + (100 if j == i else 0)) if j <= i else Fraction(0) for j in range(3)] for i in range(3)]
v = []
for i in range(3):
    v.append((prices[i] - sum(Mb[i][j] * v[j] for j in range(i))) / Mb[i][i])
print("discount factors:", [dec(x, 6) for x in v])
print("spot rates:", [f"{float(x) ** (-1 / (i + 1)) - 1:.4%}" for i, x in enumerate(v)])
""")

md(r"""
**Problem 9.** TX and MTX on two illustrative days with TAIEX moves of −300 and +150 points.
""")

code(r"""
moves = [Fraction(-300), Fraction(150)]
M9 = [[200 * dm, 50 * dm] for dm in moves]
print("M =", [[int(v) for v in r] for r in M9], " det =", det_cof(M9), " rank =", rank_exact(M9))
print("M x_h with x_h = (-1/4, 1):", [str(sum(a * v for a, v in zip(r, [Fraction(-1, 4), Fraction(1)]))) for r in M9])
""")

md(r"""
**Problem 10.** `solve` against `inv @ b`; `solve` on four days; `matrix_rank`.
""")

code(r"""
Mf, bf = np.array(M3, dtype=float), np.array(b3, dtype=float)
print("largest |solve - inv @ b| =", np.abs(np.linalg.solve(Mf, bf) - np.linalg.inv(Mf) @ bf).max(), "(machine-dependent)")
four, b4d = np.array(MF, dtype=float), np.array(BF, dtype=float)
try:
    np.linalg.solve(four, b4d)
except np.linalg.LinAlgError as err:
    print("solve on four days: LinAlgError:", err)
print("matrix_rank of M and [M|b]:", np.linalg.matrix_rank(four), np.linalg.matrix_rank(np.column_stack([four, b4d])))
""")

md(r"""
**Problem 11.** The two 50/50 mixes: Part 8 printed the ranks (2 and 3), the final buy-and-hold weight and the largest daily gap.

**Without the repair files.** On FinMind's free plan the repair cell drops the 561 listed closes. No listed close falls on 2–10 April 2025, so Parts 2–7 and Problems 4–10 do not change. The common sample loses the returns into and out of each dropped date: $T$ falls from 4,382 to 4,307, and the correlation of Semiconductor with Electronic moves from 0.952591 to 0.953091. The four ranks, the buy-and-hold weights and the largest daily gap stay as printed. The timings of Part 4 differ from machine to machine in any case.

### Extension: an exact fit for any $N$

Take $N$ sectors of U28 and exactly $N$ consecutive days, for $N=3,\dots,10$. Solve each square system and confirm that it fits TAIEX exactly: this is an in-sample fit, so it always succeeds when the determinant is not 0. How do the multiples change when you shift the window by one day or swap one sector? Then apply each mix to the following day and compare with TAIEX's return. Which choice of sectors and days would you have to defend before such a mix meant anything? LM12 fits many more days than sectors.
""")

code(r"""
# starter: the first N sectors of U28 on the N days before the last day of the sample, percent returns
y_pct = sample["TAIEX"].to_numpy() * 100
for N in range(3, 11):
    m, b = X_pct[-N - 1:-1, :N], y_pct[-N - 1:-1]
    x = np.linalg.solve(m, b)
    print(N, "largest |multiple|", round(float(np.abs(x).max()), 2),
          " largest residual", f"{float(np.abs(m @ x - b).max()):.1e}")
# your code: apply each mix to the last day, X_pct[-1, :N] @ x against y_pct[-1]; vary the sectors and the days
""")

nb = nbf.v4.new_notebook()
nb["cells"] = cells
nb["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                  "language_info": {"name": "python"}}
nbf.write(nb, LAB / "LM09_lab.ipynb")

(LAB / "README.md").write_text("""# LM9 Lab — Linear Systems, Inverses and Rank

Companion to *From Calculus to Kelly*, Learning Module 9. The notebook repairs the sector closes, rebuilds the four-day case of 7–10 April 2025 in exact arithmetic, draws both pictures of a linear system, computes determinants, Cramer's rule, elimination and inverses, counts solutions with the rank, builds the two 50/50 mixes of Semiconductor and Financial, and works the computational practice problems.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM09_lab/LM09_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM09_lab.ipynb
```

`build/make_lab09.py` generates the notebook and this README: edit the generator, not the generated files.

## Data (FinMind, retrieved 2026-10-11; not in the repository)

The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

The same steps in a shell (`data/raw/` and this folder's `data/` are git-ignored):

```bash
export FINMIND_TOKEN=...               # your FinMind API token
uv run python data/fetch_finmind.py    # rebuilds and verifies data/raw/
uv run python data/make_lab_data.py    # writes every lab's data/ folder
```

On FinMind's free plan, run `uv run python data/fetch_finmind.py --exclude sectors_close/` instead: the repair values come from a paid dataset. The notebook then drops the listed closes and says which of its numbers change.

The notebook reads only the files in its own `data/` folder:

| File | Content |
|:--|:--|
| `data/sectors_close_raw.csv` | `date`, then TAIEX and the 30 TWSE sector indices: the daily closes FinMind's `TaiwanStockPrice` serves, 2007-07-02 → 2026-10-08, empty where a series has no close |
| `data/sectors_close_repairs.csv` | `id`, `date`, `close_1330`: the 561 closes FinMind copied from another date or series, with the official 13:30:00 value of `TaiwanStockEvery5SecondsIndex` (empty on the free plan) |

Part 1 replaces each listed close by its 13:30:00 value, or drops it when the value is missing. The sector indices are market-value-weighted price indices; `Electronic` and `ChemicalBiotechnologyMedicalCare` aggregate other sector indices and stay out of the 28-sector set U28.
""", encoding="utf-8", newline="\n")
print("wrote", LAB / "LM09_lab.ipynb", "and README.md | labels:", {k: ("X" if w == "Exhibit" else "E") + str(n) for k, (w, n) in NUM.items()})
