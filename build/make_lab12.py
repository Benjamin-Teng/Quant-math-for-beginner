"""Generate labs/LM12_lab (Polars-first notebook + README) for LM12, Cholesky, SVD and Least Squares.

Run:  uv run python build/make_lab12.py
Then execute from inside the lab folder:
      cd labs/LM12_lab && uv run jupyter nbconvert --to notebook --execute --inplace LM12_lab.ipynb

The notebook reads only the files in labs/LM12_lab/data/ (sectors_close_raw.csv and sectors_close_repairs.csv), which
data/make_lab_data.py builds from data/raw/ (FinMind's licence keeps raw data out of the repository). This script writes
the notebook and the README only.

Exhibit and example numbers are never typed by hand: cells write [[ex:label]] / [[eg:label]], and the generator
resolves them from the labels in src/lm12.md, numbered in document order as build/build.py does.
"""
import re
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "LM12_lab"
LAB.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- exhibit / example numbers from the module's labels
NUM: dict[str, tuple[str, int]] = {}
_count = {"exhibit": 0, "example": 0}
for m in re.finditer(r"(?m)^(?:>\s?)+\[!(exhibit|example)\][+-]?\s*(.*)$", (ROOT / "src" / "lm12.md").read_text(encoding="utf-8")):
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


cells: list = []


def md(s: str) -> None:
    cells.append(nbf.v4.new_markdown_cell(refs(s.strip("\n"))))


def code(s: str) -> None:
    cells.append(nbf.v4.new_code_cell(refs(s.strip("\n"))))


md(r"""
# LM12 Lab — Cholesky, SVD and Least Squares

Companion notebook to **From Calculus to Kelly, LM12**. It repairs the sector closes, rebuilds the module's exhibits and computational examples, solves the computational practice problems, and ends with an extension exercise.

| Part | Rebuilds |
|:--|:--|
| 0 | Data: the served sector closes, the repair cell (rule and counts), returns and the common sample |
| 1 | Least squares as a projection: [[eg:proj1]], [[eg:line4]], $\Pi^2=\Pi$, orthogonality, R-squared as $\cos^2\theta$ |
| 2 | Rebuilding TAIEX: the case ([[ex:case]]), the last 250 returns ([[eg:taiex250]], [[ex:coef]]), one fit per year ([[eg:peryear]], [[ex:drift]]) and the widget's table |
| 3 | The SVD: [[eg:svd22]] against `np.linalg.svd`, $\lambda_k=s_k^2$, conditioning ([[eg:cond28]], [[ex:cond]]) |
| 4 | December 2008 ([[eg:dec08eg]], [[ex:dec08]]); numerical rank at three tolerances ([[eg:elec9]], [[ex:rank]]) |
| 5 | Cholesky: the recursion (12.8) against `np.linalg.cholesky`, sequential regressions ([[eg:chol2]], [[ex:chol]]), `LinAlgError` |
| 6 | Whitening and colouring: 7 April 2025 ([[eg:apr7eg]], [[ex:apr7]], [[ex:white]]), the asset order |
| 7 | Practice problems 3–12 and an extension exercise |

**Environment.** From the repository root, `uv sync` installs the locked Python environment (`uv.lock`). Open this notebook with the `.venv` kernel, or run `uv run --with jupyterlab jupyter lab`.

**Data.** The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

`data/` then holds `sectors_close_raw.csv` (the closes FinMind's `TaiwanStockPrice` serves for TAIEX and the 30 TWSE sector indices, one column per series, empty where a series has no close) and `sectors_close_repairs.csv` (each of the 561 closes that FinMind copied from another date or series, with its official 13:30:00 value from `TaiwanStockEvery5SecondsIndex`). The notebook reads nothing outside `data/`.

**Conventions (as in the module).** Daily simple returns of price indices between consecutive TAIEX-calendar dates; the common sample of TAIEX and U28 (the 28 sector indices without the aggregates Electronic and ChemicalBiotechnologyMedicalCare) from the close of 2008-12-01 to 2026-10-08, $T=4{,}382$ returns; moments divide by $T$; a fit is least squares of TAIEX's returns on the sector returns with an intercept. Every fit is in-sample, the yearly fits are a stability check, and the SVD, $L$ and $\mathbf z_t$ describe the full sample.
""")

code(r"""
from pathlib import Path
import math
import numpy as np
import polars as pl
import matplotlib.pyplot as plt

DATA = Path("data")
FIRST_CLOSE, LAST_CLOSE = "2008-12-01", "2026-10-08"
AGGREGATES = ["Electronic", "ChemicalBiotechnologyMedicalCare"]
S3 = ["Semiconductor", "FinancialInsurance", "Food"]
S5 = S3 + ["Plastics", "ShippingTransportation"]
ELEC8 = ["Semiconductor", "ComputerPeripheralEquipment", "Optoelectronic", "CommunicationsInternet",
         "ElectronicPartsComponents", "ElectronicProductsDistribution", "InformationService", "OtherElectronic"]
pl.Config.set_tbl_rows(40)
pl.Config.set_float_precision(6)
plt.rcParams.update({"figure.figsize": (9, 4.5), "axes.grid": True, "grid.alpha": 0.3,
                     "axes.spines.top": False, "axes.spines.right": False})
""")

md(r"""
## Part 0 — Data and the repair cell

FinMind's `TaiwanStockPrice` serves the sector indices with some rows copied from another date, or from another series on the same date (PITFALLS §3 of the repository). The book replaces each of these 561 closes with the official 13:30:00 value. On FinMind's free plan the 13:30:00 values are not available (`TaiwanStockEvery5SecondsIndex` is a paid dataset), so `close_1330` is empty and the cell **drops** those closes instead: a dropped close removes the returns into and out of its date, and the common sample shrinks from 4,382 to 4,307 returns. Nothing is ever estimated.
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
n_listed = rep.height
n_replaced = int(rep["close_1330"].is_not_null().sum())
U28 = [c for c in series if c not in ("TAIEX", *AGGREGATES)]
in_sample = rep.filter((pl.col("date") >= pl.lit(FIRST_CLOSE)) & pl.col("id").is_in(U28))
elec = rep.filter((pl.col("date") >= pl.lit(FIRST_CLOSE)) & (pl.col("id") == pl.lit("Electronic")))
FULL_DATA = n_replaced == n_listed
print("Rule: every close listed in sectors_close_repairs.csv is replaced by its 13:30:00 value (close_1330);")
print("      a listed close without that value is dropped (set to missing), never estimated.")
print(f"listed closes {n_listed}: replaced {n_replaced}, dropped {n_listed - n_replaced}")
print(f"in this module's sample (U28 from {FIRST_CLOSE}): {in_sample.height} closes on {in_sample['date'].n_unique()} dates; "
      f"Electronic adds {elec.height} on dates among them")
""")

code(r"""
ret = (fixed.filter(pl.col("date").is_between(pl.lit(FIRST_CLOSE), pl.lit(LAST_CLOSE))).sort("date")
            .with_columns([(pl.col(c) / pl.col(c).shift(1) - 1).alias(c) for c in series])
            .with_columns(pl.col("date").shift(1).alias("prev"))
            .slice(1))
smp = ret.filter(pl.all_horizontal([pl.col(c).is_not_null() for c in ["TAIEX", *U28]]))
T = smp.height
dates = smp["date"].to_list()
X = smp.select(U28).to_numpy()
y = smp["TAIEX"].to_numpy()
year = np.array([int(d[:4]) for d in dates])
col = {c: i for i, c in enumerate(U28)}
print(f"common sample: T = {T} returns, {dates[0]} .. {dates[-1]}; X is {X.shape}, y is {y.shape}")
assert smp.select(AGGREGATES).null_count().row(0) == (0, 0)


def show(label, value, fmt, printed, kept=False):
    # print a value next to the module's printed value; assert equality when every close is repaired, or when the
    # number comes from a window without a listed close (December 2008, the last 250 returns, 2014, 2023, 2024, 2026)
    got = format(value, fmt)
    note = "" if got == printed else ("   (differs: closes were dropped)" if not (FULL_DATA or kept) else "   MISMATCH")
    print(f"{label}: {got}   [book: {printed}]{note}")
    if FULL_DATA or kept:
        assert got == printed, (label, got, printed)


show("T", T, ",", "4,382")
""")

md(r"""
**Which numbers change on the free plan.** With the 561 listed closes dropped, the sample keeps $T=4{,}307$ returns. Numbers computed inside a window without a listed close keep their values: December 2008, the last 250 returns, the calendar years 2014, 2023, 2024 and 2026, and the raw returns of 7–10 April 2025. Everything that uses the full sample changes slightly: the full-sample fit and the other yearly fits, the SVD and condition numbers of the full sample and of 2016, the Cholesky factors, the whitened returns and the ranking of days. The mean of $\lVert\mathbf z_t\rVert^2$ stays exactly $N$. `show(...)` prints each value next to the module's and asserts equality only where the value cannot change.
""")

md(r"""
## Part 1 — Least squares as a projection

**[[eg:proj1]].** The multiple of $\mathbf x=(2,1)^{\top}$ closest to $\mathbf y=(1,3)^{\top}$. **[[eg:line4]].** A line through four points, with and without an intercept (the pitfall of Section 2). Then the projection matrix (12.2) on real data: the last 250 returns with an intercept.
""")

code(r"""
x1, y1 = np.array([2.0, 1.0]), np.array([1.0, 3.0])
b1 = x1 @ y1 / (x1 @ x1)
print(f"[[eg:proj1]]: beta = {b1}, fitted {b1 * x1}, residual {y1 - b1 * x1}, x'e = {x1 @ (y1 - b1 * x1)}, "
      f"distance {np.linalg.norm(y1 - b1 * x1):.3f}; 1.5x is at {np.linalg.norm(y1 - 1.5 * x1):.1f}")

x4, y4 = np.array([0.0, 1, 2, 3]), np.array([1.0, 3, 2, 6])
D4 = np.column_stack([np.ones(4), x4])
a4, b4 = np.linalg.lstsq(D4, y4, rcond=None)[0]
e4 = y4 - D4 @ np.array([a4, b4])
yc = y4 - y4.mean()
print(f"[[eg:line4]]: alpha = {a4:.1f}, beta = {b4:.1f}, residuals {e4.round(1)}, sum {e4.sum():.1e}, x'e {x4 @ e4:.1e}")
print(f"   R-squared = 1 - {e4 @ e4:.1f}/{yc @ yc:.0f} = {1 - e4 @ e4 / (yc @ yc):.1f}; squared cosine "
      f"{(np.corrcoef(x4, y4)[0, 1]) ** 2:.1f}")
b0 = x4 @ y4 / (x4 @ x4)
e0 = y4 - b0 * x4
print(f"   through the origin: beta = {b0:.3f}, |e|^2 = {e0 @ e0:.3f}, uncentred share {1 - e0 @ e0 / (y4 @ y4):.3f}, "
      f"centred formula {1 - e0 @ e0 / (yc @ yc):.3f}")
""")

code(r"""
LAST = np.arange(T) >= T - 250
D = np.column_stack([np.ones(250), X[LAST]])
Pi = D @ np.linalg.solve(D.T @ D, D.T)            # projection matrix (12.2), 250 x 250; solve, never inv
yl = y[LAST]
e = yl - Pi @ yl
print(f"last 250 design {D.shape}: |Pi Pi - Pi| = {np.abs(Pi @ Pi - Pi).max():.1e}, |Pi - Pi'| = {np.abs(Pi - Pi.T).max():.1e}, "
      f"trace = {np.trace(Pi):.6f}, max |D'e| = {np.abs(D.T @ e).max():.1e}")
fit_c = Pi @ yl - yl.mean()
cos = (yl - yl.mean()) @ fit_c / (np.linalg.norm(yl - yl.mean()) * np.linalg.norm(fit_c))
show("R-squared, last 250, as 1 - |e|^2/|y~|^2", 1 - e @ e / ((yl - yl.mean()) @ (yl - yl.mean())), ".5f", "0.99912", kept=True)
show("R-squared, last 250, as cos^2 theta", cos**2, ".5f", "0.99912", kept=True)
""")

md(r"""
## Part 2 — Rebuilding TAIEX from its sectors

`fit(mask)` regresses TAIEX on the 28 sector returns with an intercept on the dates in `mask` (`np.linalg.lstsq` on $(\mathbf 1\ X)$, which returns the minimum-norm solution when the design is rank deficient).
""")

code(r"""
def fit(mask):
    D = np.column_stack([np.ones(int(mask.sum())), X[mask]])
    b = np.linalg.lstsq(D, y[mask], rcond=None)[0]
    e = y[mask] - D @ b
    yc = y[mask] - y[mask].mean()
    return b, 1 - e @ e / (yc @ yc), np.linalg.matrix_rank(D)


FULL = np.ones(T, dtype=bool)
DEC = np.array([d.startswith("2008-12") for d in dates])
SIX = ["Semiconductor", "ElectronicPartsComponents", "FinancialInsurance", "ComputerPeripheralEquipment",
       "OtherElectronic", "CommunicationsInternet"]
fits = {"full sample": fit(FULL), "last 250": fit(LAST), "December 2008": fit(DEC)}
case = pl.DataFrame([{"sample": k, "T": int(m.sum()), "rank": int(f[2]), "R-squared": f[1], "sum of slopes": f[0][1:].sum(),
                      **{c: f[0][1 + col[c]] for c in SIX}} for (k, f), m in zip(fits.items(), (FULL, LAST, DEC))])
case   # [[ex:case]]
""")

code(r"""
b_last, r2_last, _ = fits["last 250"]
show("[[eg:taiex250]] R-squared", r2_last, ".5f", "0.99912", kept=True)
for c, p in zip(SIX, ("0.542", "0.098", "0.084", "0.054", "0.047", "0.038")):
    show(f"   {c}", b_last[1 + col[c]], ".3f", p, kept=True)
show("   sum of the 28 slopes", b_last[1:].sum(), ".3f", "0.990", kept=True)
show("   intercept, % a day", 100 * b_last[0], ".3f", "-0.013", kept=True)
show("   negative coefficients", int((b_last[1:] < 0).sum()), "d", "7", kept=True)
show(f"   smallest ({U28[int(np.argmin(b_last[1:]))]})", b_last[1:].min(), ".4f", "-0.0081", kept=True)
Xw = np.delete(X, col["Semiconductor"], axis=1)
Dw = np.column_stack([np.ones(250), Xw[LAST]])
ew = y[LAST] - Dw @ np.linalg.lstsq(Dw, y[LAST], rcond=None)[0]
show("   R-squared without Semiconductor", 1 - ew @ ew / ((y[LAST] - y[LAST].mean()) ** 2).sum(), ".3f", "0.856", kept=True)
show("full sample R-squared", fits["full sample"][1], ".5f", "0.98333")

order = np.argsort(-b_last[1:], kind="stable")
fig, ax = plt.subplots(figsize=(10, 4.5))
ax.bar(range(28), b_last[1:][order], color="tab:blue")
ax.set_xticks(range(28), [U28[i] for i in order], rotation=60, ha="right", fontsize=8)
ax.axhline(0, color="black", lw=0.8); ax.set_ylabel("coefficient")
ax.set_title("[[ex:coef]]: coefficients of the 28 sectors, last 250 returns"); plt.tight_layout(); plt.show()
""")

code(r"""
KEPT_YEARS = (2014, 2023, 2024, 2026)          # no listed close inside these years
rows = []
for yr in range(2009, 2027):
    b, r2, _ = fit(year == yr)
    rows.append({"year": yr, "T": int((year == yr).sum()), "R-squared": r2, "sum": b[1:].sum(),
                 **{c: b[1 + col[c]] for c in SIX[:4]}, "negatives": int((b[1:] < 0).sum())})
yearly = pl.DataFrame(rows)
print("the widget's table: one fit per calendar year (2026 to 8 October)")
yearly
""")

code(r"""
yr_ = {r["year"]: r for r in rows}
show("[[eg:peryear]] Semiconductor 2009", yr_[2009]["Semiconductor"], ".3f", "0.189")
show("   Semiconductor 2026", yr_[2026]["Semiconductor"], ".3f", "0.554", kept=True)
show("   FinancialInsurance 2009", yr_[2009]["FinancialInsurance"], ".3f", "0.133")
show("   FinancialInsurance 2026", yr_[2026]["FinancialInsurance"], ".3f", "0.080", kept=True)
low = min(rows, key=lambda r: r["R-squared"])
show(f"   smallest yearly R-squared ({low['year']})", low["R-squared"], ".5f", "0.99800")
print("   every year above the full sample:", all(r["R-squared"] > fits["full sample"][1] for r in rows))
fig, ax = plt.subplots()
for c in SIX[:4]:
    ax.plot(yearly["year"], yearly[c], marker="o", ms=3, label=c)
ax.set_xlabel("calendar year (2026 to 8 October)"); ax.set_ylabel("coefficient")
ax.set_title("[[ex:drift]]: four coefficients by calendar year"); ax.legend(fontsize=8); plt.show()
""")

md(r"""
## Part 3 — The singular value decomposition

**[[eg:svd22]].** `np.linalg.svd` returns $U$, the singular values in **descending** order and $V^{\top}$ (as `Vh`, whose rows are the $\mathbf v_k$); `np.linalg.eigh` returns eigenvalues in **ascending** order. The book signs each $\mathbf v_k$ so that its entry largest in absolute value is positive (the first of tied entries) and then sets $\mathbf u_k=M\mathbf v_k/s_k$.
""")

code(r"""
def sign_rule(v):
    a = np.abs(v)
    k = int(np.flatnonzero(a >= a.max() - 1e-12)[0])
    return v if v[k] > 0 else -v


M = np.array([[4.0, 4.0], [-2.0, 4.0]])
U, s, Vh = np.linalg.svd(M)
v = [sign_rule(r) for r in Vh]
u = [M @ v[k] / s[k] for k in range(2)]
print("M'M =", (M.T @ M).tolist(), " eigenvalues (eigh, ascending):", np.linalg.eigh(M.T @ M)[0])
print("singular values:", s, " v_1, v_2 * sqrt(5):", (np.array(v) * math.sqrt(5)).round(6).tolist(),
      " u_1, u_2 * sqrt(5):", (np.array(u) * math.sqrt(5)).round(6).tolist())
print(f"|det M| = {abs(np.linalg.det(M)):.6f} = s_1 s_2 = {s[0] * s[1]:.6f}; kappa = {np.linalg.cond(M):.2f}")
""")

code(r"""
Xc = X - X.mean(axis=0)
sv = np.linalg.svd(Xc / math.sqrt(T), compute_uv=False)
Sig = Xc.T @ Xc / T
lam = np.linalg.eigh(Sig)[0][::-1]
print(f"lambda_k = s_k^2 for U28: largest gap {np.abs(lam - sv ** 2).max():.1e}")
show("[[eg:cond28]] s_1", sv[0], ".6f", "0.054245")
show("   s_28", sv[-1], ".6f", "0.005218")
show("   kappa(X~)", sv[0] / sv[-1], ".2f", "10.40")
show("   kappa(Sigma) = kappa(X~)^2", (sv[0] / sv[-1]) ** 2, ".2f", "108.09")
print(f"   np.linalg.cond(Sigma) = {np.linalg.cond(Sig):.2f}")


def solvers(cols, mask):
    Z = smp.filter(pl.Series(mask)).select(cols).to_numpy()
    Zc, yc = Z - Z.mean(axis=0), y[mask] - y[mask].mean()
    s_ = np.linalg.svd(Zc, compute_uv=False)
    gap = np.abs(np.linalg.lstsq(Zc, yc, rcond=None)[0] - np.linalg.solve(Zc.T @ Zc, Zc.T @ yc)).max()
    return s_[0] / s_[-1], np.linalg.cond(Zc.T @ Zc), gap


cond_rows = [("S3, full sample", S3, FULL), ("S5, full sample", S5, FULL), ("U28, full sample", U28, FULL),
             ("U28, last 250 returns", U28, LAST), ("U28 + Electronic, full sample", ["Electronic", *U28], FULL),
             ("U28 + Electronic, 2016", ["Electronic", *U28], year == 2016)]
tbl = []
for name, cols, mask in cond_rows:
    k1, k2, gap = solvers(cols, mask)
    tbl.append({"design": name, "columns": len(cols), "kappa(X~)": k1, "kappa(X~'X~)": k2,
                "gap order": f"1e{math.floor(math.log10(gap))}" if gap > 0 else "0",
                "digits lost (rule of thumb)": math.log10(k2)})
pl.DataFrame(tbl)   # [[ex:cond]]; the gap depends on the machine, only its order matters
""")

md(r"""
## Part 4 — Rank deficiency, the pseudoinverse and numerical rank

**[[eg:dec08eg]].** December 2008: 22 returns, 29 coefficients. `lstsq` and `pinv` return the minimum-norm solution (12.7). Note that `lstsq` returns an empty array of residual sums when the design is rank deficient. **[[eg:elec9]].** The numerical rank of Electronic and its eight sub-industries at three tolerances.
""")

code(r"""
D8 = np.column_stack([np.ones(int(DEC.sum())), X[DEC]])
sol = np.linalg.lstsq(D8, y[DEC], rcond=None)
b_pinv = np.linalg.pinv(D8) @ y[DEC]
print(f"design {D8.shape}, matrix_rank {np.linalg.matrix_rank(D8)}, null space dimension {D8.shape[1] - np.linalg.matrix_rank(D8)}; "
      f"lstsq residual sums: {sol[1]} (empty when rank deficient); |lstsq - pinv| = {np.abs(sol[0] - b_pinv).max():.1e}")
print(f"largest |residual| {np.abs(y[DEC] - D8 @ b_pinv).max():.1e} (below 1e-13)")
show("minimum-norm: Semiconductor", b_pinv[1 + col["Semiconductor"]], ".3f", "0.145", kept=True)
show("   FinancialInsurance", b_pinv[1 + col["FinancialInsurance"]], ".3f", "0.165", kept=True)
show("   norm of the 29 coefficients", np.linalg.norm(b_pinv), ".3f", "0.285", kept=True)
D8w = np.delete(D8, 1 + col["Semiconductor"], axis=1)
names_w = ["intercept"] + [c for c in U28 if c != "Semiconductor"]
b_w = np.linalg.pinv(D8w) @ y[DEC]
print(f"without Semiconductor: rank {np.linalg.matrix_rank(D8w)}, largest |residual| {np.abs(y[DEC] - D8w @ b_w).max():.1e}")
show("   FinancialInsurance", b_w[names_w.index("FinancialInsurance")], ".3f", "0.218", kept=True)
show("   norm", np.linalg.norm(b_w), ".3f", "0.401", kept=True)
pl.DataFrame({"coefficient": ["intercept", *U28],
              "all 28 sectors": b_pinv,
              "without Semiconductor": np.insert(b_w, 1 + col["Semiconductor"], np.nan)})   # [[ex:dec08]]
""")

code(r"""
E9 = smp.select(["Electronic", *ELEC8]).to_numpy()


def ratios(mask, standardize=True):
    Z = E9[mask] - E9[mask].mean(axis=0)
    if standardize:
        Z = Z / Z.std(axis=0)
    s_ = np.linalg.svd(Z / math.sqrt(int(mask.sum())), compute_uv=False)
    return s_ / s_[0]


r_full, r_2016 = ratios(FULL), ratios(year == 2016)
show("s_9/s_1 standardized, full sample", r_full[-1], ".4f", "0.0346")
show("s_9/s_1 standardized, 2016", r_2016[-1], ".5f", "0.00277")
show("s_9/s_1 covariance scale, full sample", ratios(FULL, False)[-1], ".4f", "0.0329")
for delta in (0.1, 0.01, 0.001):
    print(f"delta = {delta}: numerical rank {int((r_full > delta).sum())} (full sample), {int((r_2016 > delta).sum())} (2016)")
fig, ax = plt.subplots()
ax.semilogy(range(1, 10), r_full, marker="o", label="full sample")
ax.semilogy(range(1, 10), r_2016, marker="o", label="2016")
ax.axhline(0.01, color="black", ls="--", lw=0.8, label="tolerance 0.01")
ax.set_xlabel("k"); ax.set_ylabel("s_k / s_1"); ax.set_title("[[ex:rank]]: Electronic and its eight sub-industries")
ax.legend(); plt.show()
""")

md(r"""
## Part 5 — Cholesky: the recursion, sequential regressions and failure

The recursion (12.8) column by column, checked against `np.linalg.cholesky` (lower factor). `scipy.linalg.cholesky` returns the **upper** factor by default.
""")

code(r"""
def cholesky(S):
    n = len(S)
    L = np.zeros_like(S)
    for j in range(n):
        d = S[j, j] - L[j, :j] @ L[j, :j]
        if d <= 0:
            raise np.linalg.LinAlgError(f"not positive definite at column {j + 1}")
        L[j, j] = math.sqrt(d)
        for i in range(j + 1, n):
            L[i, j] = (S[i, j] - L[i, :j] @ L[j, :j]) / L[j, j]
    return L


i5 = [col[c] for c in S5]
S5m = Sig[np.ix_(i5, i5)]
L5 = cholesky(S5m)
print(f"own recursion vs np.linalg.cholesky: largest difference {np.abs(L5 - np.linalg.cholesky(S5m)).max():.1e}")
show("[[eg:chol2]] sigma_11 (x 1e4)", 1e4 * S5m[0, 0], ".6f", "2.323354")
show("   l_11", L5[0, 0], ".7f", "0.0152426")
show("   l_21", L5[1, 0], ".6f", "0.006998")
show("   l_22", L5[1, 1], ".6f", "0.009960")
show("   slope of FinancialInsurance on Semiconductor", np.polyfit(Xc[:, i5[0]], Xc[:, i5[1]], 1)[0], ".4f", "0.4591")
for j in range(1, 5):
    Zj, zt = Xc[:, i5[:j]], Xc[:, i5[j]]
    res = zt - Zj @ np.linalg.lstsq(Zj, zt, rcond=None)[0]
    print(f"   {S5[j]} on the sectors before it: residual s.d. {math.sqrt(res @ res / T):.7f}, l_jj {L5[j, j]:.7f}")
pl.DataFrame(100 * L5, schema=S5, orient="row").insert_column(0, pl.Series("sector", S5))   # [[ex:chol]], % a day
""")

code(r"""
S_dec = np.cov(X[DEC], rowvar=False, ddof=0)
print(f"December 2008: Sigma is {S_dec.shape} with rank {np.linalg.matrix_rank(S_dec)}")
try:
    np.linalg.cholesky(S_dec)
except np.linalg.LinAlgError as err:
    print("np.linalg.cholesky raised LinAlgError:", err)
""")

md(r"""
## Part 6 — Whitening and colouring

$\mathbf z_t=L^{-1}(\mathbf R_t-\bar{\mathbf R})$ by a triangular solve (here `np.linalg.solve`; `scipy.linalg.solve_triangular` exploits the triangle). The mean of $\lVert\mathbf z_t\rVert^2$ is exactly $N$, and the squared length does not depend on the asset order.
""")

code(r"""
Z5 = np.linalg.solve(L5, Xc[:, i5].T).T
q5 = (Z5 ** 2).sum(axis=1)
print(f"sample covariance of z: largest |entry - identity| {np.abs(Z5.T @ Z5 / T - np.eye(5)).max():.1e}; mean |z|^2 = {q5.mean():.12f}")
i7 = dates.index("2025-04-07")
for c, p in zip(S5, ("-9.95", "-9.89", "-8.66", "-9.90", "-9.73")):
    show(f"7 April 2025 return, {c}", 100 * X[i7, col[c]], ".2f", p, kept=True)
rev = i5[::-1]
z_rev = np.linalg.solve(np.linalg.cholesky(Sig[np.ix_(rev, rev)]), Xc[i7, rev])
tbl = pl.DataFrame({"sector": S5, "return %": 100 * X[i7, i5], "centred %": 100 * Xc[i7, i5],
                    "z, given order": Z5[i7], "z, reversed order": z_rev[::-1]})
show("[[eg:apr7eg]] |z|^2", q5[i7], ".2f", "89.30")
show("   |z|^2, reversed order", z_rev @ z_rev, ".2f", "89.30")
print("   rank among the days:", int((q5 > q5[i7]).sum()) + 1)
tbl   # [[ex:apr7]], first table
""")

code(r"""
top = np.argsort(-q5)[:5]
pl.DataFrame({"rank": list(range(1, 6)), "date": [dates[k] for k in top], "|z|^2": q5[top], "TAIEX %": 100 * y[top]})   # [[ex:apr7]]
""")

code(r"""
L2 = np.linalg.cholesky(Sig[np.ix_(i5[:2], i5[:2])])
Z2 = np.linalg.solve(L2, Xc[:, i5[:2]].T).T
print("the pair's z equals the first two entries of S5's z:", np.allclose(Z2, Z5[:, :2]))
fig, axes = plt.subplots(1, 2, figsize=(10, 5))
t = np.linspace(0, 2 * np.pi, 400)
ring = np.vstack([np.cos(t), np.sin(t)]) * 3
for ax, P, curve, title in ((axes[0], 100 * Xc[:, i5[:2]], 100 * L2 @ ring, "centred returns (% a day)"),
                            (axes[1], Z2, ring, "whitened returns")):
    ax.scatter(P[:, 0], P[:, 1], s=2, alpha=0.4)
    ax.plot(curve[0], curve[1], color="tab:orange", label="|z|^2 = 9")
    ax.scatter([P[i7, 0]], [P[i7, 1]], color="tab:red", s=30, label="7 Apr 2025")
    ax.set_aspect("equal"); ax.set_title(title); ax.legend(fontsize=8)
fig.suptitle("[[ex:white]]: Semiconductor (x) and FinancialInsurance (y)"); plt.show()
""")

code(r"""
# colouring: L maps vectors with identity sample covariance to vectors with sample covariance Sigma
W = Z5 @ L5.T                       # rows L z_t, back to the centred returns
print(f"colouring the whitened returns gives back the centred returns: largest difference {np.abs(W - Xc[:, i5]).max():.1e}")
""")

md(r"""
## Part 7 — Practice problems

Problems 1 and 2 are conceptual; the numerical parts of Problems 3–12 follow.
""")

code(r"""
for name, Mx in (("A", [[4, 2], [2, 5]]), ("B", [[4, 6], [6, 9]]), ("C", [[1, 3], [3, 4]])):
    Mx = np.array(Mx, dtype=float)
    try:
        print(f"P3 matrix {name}: det {np.linalg.det(Mx):.0f}, L = {np.linalg.cholesky(Mx).tolist()}")
    except np.linalg.LinAlgError:
        print(f"P3 matrix {name}: det {np.linalg.det(Mx):.0f}, no Cholesky factor")

xp, yp = np.array([-1.0, 0, 1, 2]), np.array([0.0, 1, 1, 4])
Dp = np.column_stack([np.ones(4), xp]); bp = np.linalg.lstsq(Dp, yp, rcond=None)[0]; ep = yp - Dp @ bp
print(f"P4: alpha {bp[0]:.1f}, beta {bp[1]:.1f}, residuals {ep.round(1)}, sum {ep.sum():.1e}, x'e {xp @ ep:.1e}, "
      f"R-squared {1 - ep @ ep / ((yp - yp.mean()) ** 2).sum():.1f}")

x5 = np.array([[1.0], [1.0], [0.0]]); P5 = x5 @ x5.T / 2
print(f"P5: Pi = {P5.tolist()}, |Pi Pi - Pi| = {np.abs(P5 @ P5 - P5).max()}, trace {np.trace(P5)}, Pi y = {P5 @ [3, 1, 2]}")

M6 = np.array([[2.0, 0.0], [3.0, 2.0]]); _, s6, V6 = np.linalg.svd(M6)
v6 = [sign_rule(r) for r in V6]
print(f"P6: s = {s6}, v_k * sqrt(5) = {(np.array(v6) * math.sqrt(5)).round(6).tolist()}, "
      f"u_k * sqrt(5) = {(np.array([M6 @ v6[k] / s6[k] for k in range(2)]) * math.sqrt(5)).round(6).tolist()}, kappa {s6[0] / s6[1]:.0f}")

M7 = np.array([[1.0, 2.0], [2.0, 4.0]])
print(f"P7: pinv * 25 = {(np.linalg.pinv(M7) * 25).round(9).tolist()}, minimum-norm solution {np.linalg.pinv(M7) @ [5, 10]}")
""")

code(r"""
s5 = np.linalg.svd(Xc[:, i5] / math.sqrt(T), compute_uv=False)
print("P8: singular values", s5.round(6), " eigenvalues x 1e4", (1e4 * s5 ** 2).round(3),
      f" kappa(X~) {s5[0] / s5[-1]:.3f}, kappa(Sigma) {(s5[0] / s5[-1]) ** 2:.2f}")

s1, s2, rho = 0.201, 0.135, -0.11
S7 = np.array([[s1 ** 2, rho * s1 * s2], [rho * s1 * s2, s2 ** 2]])
L7 = np.linalg.cholesky(S7)
print(f"P9: L = {L7.round(5).tolist()}, slope l21/l11 = {L7[1, 0] / L7[0, 0]:.4f}, l22 = {L7[1, 1]:.4%}")
d = np.array([-0.30, 0.10])
z = np.linalg.solve(L7, d)
zr = np.linalg.solve(np.linalg.cholesky(S7[::-1, ::-1]), d[::-1])
print(f"P10: z = {z.round(4)}, |z|^2 = {z @ z:.3f}; reversed order z = {zr.round(4)}, |z|^2 = {zr @ zr:.3f}; "
      f"d' Sigma^-1 d = {d @ np.linalg.solve(S7, d):.3f}")
""")

code(r"""
# P11: the last-250 fit three ways
XL = X[LAST] - X[LAST].mean(axis=0); yL = y[LAST] - y[LAST].mean()
b_a = np.linalg.lstsq(np.column_stack([np.ones(250), X[LAST]]), y[LAST], rcond=None)[0][1:]
b_b = np.linalg.solve(XL.T @ XL, XL.T @ yL)
b_c = (np.linalg.pinv(np.column_stack([np.ones(250), X[LAST]])) @ y[LAST])[1:]
sL = np.linalg.svd(XL, compute_uv=False)
print(f"P11: R-squared {r2_last:.5f}; largest gaps {np.abs(b_a - b_b).max():.1e} and {np.abs(b_a - b_c).max():.1e}; "
      f"kappa(X~) {sL[0] / sL[-1]:.2f}, kappa(X~'X~) {(sL[0] / sL[-1]) ** 2:.1f}")
# P12: yearly fits and the numerical rank of Electronic + eight at delta = 0.01
ranks = {yr: (int((ratios(year == yr) > 0.01).sum()),
              int(np.linalg.matrix_rank((E9[year == yr] - E9[year == yr].mean(0)) / E9[year == yr].std(0))))
         for yr in range(2009, 2027)}
print(f"P12: smallest yearly R-squared {low['R-squared']:.5f} ({low['year']}); rank at 0.01 and matrix_rank by year:", ranks)
""")

md(r"""
### Extension: how close is a coloured simulation?

Colour $T$ independent standard normal draws with S5's $L$ and compare the sample covariance of the simulated returns with $\hat\Sigma$. The relative gap below uses the Frobenius norm, the square root of the sum of squared entries. Then repeat with other seeds and with $T$ = 500, 4,382 and 50,000: how does the gap shrink as $T$ grows? [[LM18]] explains the rate.
""")

code(r"""
rng = np.random.default_rng(20261011)
draws = rng.standard_normal((T, 5))
sim = draws @ L5.T                      # row t is L z_t
S_sim = np.cov(sim, rowvar=False, ddof=0)
gap = np.linalg.norm(S_sim - S5m) / np.linalg.norm(S5m)
print(f"relative Frobenius gap: {gap:.4f}")
show("relative Frobenius gap (4 decimals)", gap, ".4f", "0.0250")
# your code: other seeds, other T
""")

nb = nbf.v4.new_notebook()
nb["cells"] = cells
nb["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                  "language_info": {"name": "python"}}
nbf.write(nb, LAB / "LM12_lab.ipynb")

(LAB / "README.md").write_text("""# LM12 Lab — Cholesky, SVD and Least Squares

Companion to *From Calculus to Kelly*, Learning Module 12. The notebook repairs the sector closes, rebuilds the module's exhibits and computational examples (TAIEX rebuilt from its sector indices, the SVD and conditioning, December 2008's rank-deficient fit, Cholesky factors and whitened returns), and works the computational practice problems.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM12_lab/LM12_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM12_lab.ipynb
```

`build/make_lab12.py` generates the notebook and this README: edit the generator, not the generated files.

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
| `data/sectors_close_raw.csv` | the daily closes FinMind's `TaiwanStockPrice` serves for TAIEX and the 30 TWSE sector indices, 2007-07-02 → 2026-10-08, one column per series, empty where a series has no close |
| `data/sectors_close_repairs.csv` | `id`, `date`, `close_1330`: the 561 closes that FinMind copied from another date or series, each with its official 13:30:00 value from `TaiwanStockEvery5SecondsIndex` |

The first part of the notebook replaces each listed close with its 13:30:00 value. `TaiwanStockEvery5SecondsIndex` is a paid FinMind dataset: on the free plan `close_1330` is empty, the notebook drops those closes instead (never estimating one), and the common sample keeps 4,307 of its 4,382 returns. The notebook then says which of its numbers differ from the module's; December 2008, the last 250 returns and the calendar years 2014, 2023, 2024 and 2026 do not change.
""", encoding="utf-8", newline="\n")
print("wrote", LAB / "LM12_lab.ipynb", "and README.md | labels:", {k: ("X" if w == "Exhibit" else "E") + str(n) for k, (w, n) in NUM.items()})
