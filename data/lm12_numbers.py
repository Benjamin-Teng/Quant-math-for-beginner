"""Every number that LM12 (Cholesky, SVD and Least Squares) quotes, computed and checked against src/lm12.md.

Run:  uv run python data/lm12_numbers.py      (after data/vol2_series.py has written processed/vol2_closes.parquet)

Inputs: data/processed/vol2_closes.parquet (TAIEX and the 30 TWSE sector indices, closes repaired from the 13:30:00
values by data/vol2_series.py), the file names in data/raw/sectors_close/ (one per repaired close: they give the
number of repaired closes in the sample and show that no top-five day uses a repaired close), src/lm12.md (the
text the checks compare against) and src/lm07.md (the covariance matrix that Problems 9 and 10 take from LM7).

Sample: closes 2008-12-01 .. 2026-10-08, daily simple returns between consecutive TAIEX-calendar dates, T = 4,382
(first return 2008-12-02); U28 = the 28 leaf indices among the 30 TWSE sector indices that FinMind serves daily,
that is, all but the aggregates Electronic and ChemicalBiotechnologyMedicalCare. Moments divide by T. A fit is least
squares of TAIEX's returns on the sector returns with an intercept (np.linalg.lstsq on (1 X)); R-squared =
1 - |e|^2 / |y - mean(y)|^2.

Each check chk(label, value, fmt, printed) asserts that format(value, fmt) equals the printed string and that the
string appears in src/lm12.md (after replacing the Unicode minus by '-' and '{,}' by ','). Hand examples are
recomputed from the inputs printed next to them (PITFALLS section 7). Floating-point residues are checked against
bounds, never printed as digits, because they differ between machines.
"""
import math
import re
from fractions import Fraction
from pathlib import Path

import numpy as np
import polars as pl
from numpy.typing import NDArray

Vec = NDArray[np.float64]
Mat = NDArray[np.float64]

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CLOSES = HERE / "processed" / "vol2_closes.parquet"
REPAIRED = HERE / "raw" / "sectors_close"          # one raw file per repaired close: <ID>__<date>.csv
TEXT = (ROOT / "src" / "lm12.md").read_text(encoding="utf-8")
NORM = TEXT.replace("{,}", ",").replace("−", "-")


def in_text(printed: str) -> bool:
    """The printed number appears in the text as a whole number (not inside a longer one: 2.323 is not in 2.3235)."""
    return re.search(r"(?<![\d.])" + re.escape(printed) + r"(?!\d)", NORM) is not None

AGGREGATES = ["Electronic", "ChemicalBiotechnologyMedicalCare"]
S3 = ["Semiconductor", "FinancialInsurance", "Food"]
S5 = [*S3, "Plastics", "ShippingTransportation"]
ELEC8 = ["Semiconductor", "ComputerPeripheralEquipment", "Optoelectronic", "CommunicationsInternet",
         "ElectronicPartsComponents", "ElectronicProductsDistribution", "InformationService", "OtherElectronic"]
SIX = ["Semiconductor", "ElectronicPartsComponents", "FinancialInsurance", "ComputerPeripheralEquipment",
       "OtherElectronic", "CommunicationsInternet"]
FIRST_CLOSE, LAST_CLOSE = "2008-12-01", "2026-10-08"
N_CHECKS = 0


def chk(label: str, value: float, fmt: str, printed: str) -> None:
    """Assert that value prints as `printed` and that `printed` appears in the module text."""
    global N_CHECKS
    got = format(value, fmt)
    ok = got == printed and in_text(printed)
    print(f"CHECK {label}: {got} (printed {printed}) {'ok' if ok else 'MISMATCH'}")
    assert got == printed, (label, got, printed)
    assert in_text(printed), f"{label}: {printed!r} not found in src/lm12.md"
    N_CHECKS += 1


def has(label: str, printed: str) -> None:
    """Assert that a printed string (a date, a count, a word) appears in the module text."""
    global N_CHECKS
    assert printed in NORM, f"{label}: {printed!r} not found in src/lm12.md"
    print(f"CHECK {label}: '{printed}' in text ok")
    N_CHECKS += 1


def load() -> tuple[pl.DataFrame, list[str]]:
    """Returns of TAIEX and the 30 sectors on the U28 common sample (all of TAIEX + U28 present on t and t-1)."""
    assert CLOSES.exists(), "run data/vol2_series.py first"
    cdf = pl.read_parquet(CLOSES).sort("date")
    series = [c for c in cdf.columns if c != "date"]
    sectors = [c for c in series if c != "TAIEX"]
    u28 = [c for c in sectors if c not in AGGREGATES]
    assert len(sectors) == 30 and len(u28) == 28
    cdf = cdf.filter(pl.col("date").is_between(pl.lit(FIRST_CLOSE), pl.lit(LAST_CLOSE)))
    ret = cdf.with_columns([(pl.col(c) / pl.col(c).shift(1) - 1).alias(c) for c in series])
    ret = ret.with_columns(pl.col("date").shift(1).alias("prev")).slice(1)
    ret = ret.filter(pl.all_horizontal([pl.col(c).is_not_null() for c in ["TAIEX", *u28]]))
    return ret, u28


def mat(df: pl.DataFrame, cols: list[str]) -> Mat:
    return np.asarray(df.select(cols).to_numpy(), dtype=np.float64)


def fit(y: Vec, x: Mat) -> tuple[Vec, float, Vec]:
    """Least squares with an intercept: coefficients (intercept first), R-squared, residuals."""
    design = np.column_stack([np.ones(len(y)), x])
    b = np.linalg.lstsq(design, y, rcond=None)[0]
    e = y - design @ b
    yc = y - y.mean()
    return b, float(1 - e @ e / (yc @ yc)), e


def cov0(x: Mat) -> Mat:
    xc = x - x.mean(axis=0)
    return xc.T @ xc / x.shape[0]


def sign_rule(v: Vec) -> Vec:
    """Entry largest in absolute value positive; on a tie, the first tied entry (AUTHORING section 6)."""
    a = np.abs(v)
    k = int(np.flatnonzero(a >= a.max() - 1e-12)[0])
    return v if v[k] > 0 else -v


ret, U28 = load()
T = ret.height
dates = ret["date"].to_list()
X = mat(ret, U28)
y = ret["TAIEX"].to_numpy().astype(np.float64)
year = np.array([int(d[:4]) for d in dates])
col = {c: i for i, c in enumerate(U28)}
print(f"sample: T = {T}, first return {dates[0]} (from {ret['prev'][0]}), last {dates[-1]}")
assert T == 4382 and dates[0] == "2008-12-02" and ret["prev"][0] == FIRST_CLOSE and dates[-1] == LAST_CLOSE
assert ret.select(AGGREGATES).null_count().row(0) == (0, 0), "the aggregates have gaps in the sample"
has("T", "4,382")
has("sample start", "2 December 2008")
has("sample end", "8 October 2026")

# ------------------------------------------------------------------ case and Section 3: three fits
FULL = np.ones(T, dtype=bool)
LAST = np.arange(T) >= T - 250
DEC = np.array([d.startswith("2008-12") for d in dates])
print(f"last 250: {dates[T - 250]} .. {dates[-1]}; December 2008: {int(DEC.sum())} returns")
assert dates[T - 250] == "2025-09-25" and int(DEC.sum()) == 22
has("last-250 start", "25 September 2025")
chk("December 2008 returns", float(DEC.sum()), ".0f", "22")

b_full, r2_full, _ = fit(y, X)
b_last, r2_last, _ = fit(y[LAST], X[LAST])
d_dec = np.column_stack([np.ones(22), X[DEC]])
b_dec = np.linalg.pinv(d_dec) @ y[DEC]
e_dec = y[DEC] - d_dec @ b_dec
r2_dec = 1 - float(e_dec @ e_dec) / float(((y[DEC] - y[DEC].mean()) ** 2).sum())
for nm, b, r2 in (("full", b_full, r2_full), ("last 250", b_last, r2_last), ("December 2008", b_dec, r2_dec)):
    print(f"{nm}: R-squared {r2:.10f}, sum of slopes {b[1:].sum():.6f}, intercept {b[0]:.4e}, "
          + ", ".join(f"{c} {b[1 + col[c]]:.6f}" for c in SIX))
chk("R-squared, last 250", r2_last, ".5f", "0.99912")
chk("R-squared, last 250, in %", 100 * r2_last, ".3f", "99.912")
chk("R-squared, full", r2_full, ".5f", "0.98333")
assert 1 - r2_dec < 1e-12, "December 2008 is not exact"
chk("sum, full", b_full[1:].sum(), ".3f", "1.009")
chk("sum, last 250", b_last[1:].sum(), ".3f", "0.990")
chk("sum, December 2008 (minimum norm)", b_dec[1:].sum(), ".3f", "0.968")
for nm, b, printed in (("full", b_full, ("0.337", "0.081", "0.123", "0.067", "0.060", "0.075")),
                       ("last 250", b_last, ("0.542", "0.098", "0.084", "0.054", "0.047", "0.038")),
                       ("December 2008", b_dec, ("0.145", "0.065", "0.165", "0.060", "0.055", "0.081"))):
    for c, p in zip(SIX, printed, strict=True):
        chk(f"{nm} {c}", b[1 + col[c]], ".3f", p)
order = np.argsort(-b_last[1:])
assert [U28[i] for i in order[:6]] == SIX, "the six largest last-250 coefficients changed"
neg = b_last[1:] < 0
chk("last 250: negative coefficients", float(neg.sum()), ".0f", "7")
assert U28[int(np.argmin(b_last[1:]))] == "InformationService"
has("smallest coefficient's sector", "the smallest −0.0081 (InformationService)".replace("−", "-"))
chk("last 250: smallest coefficient", b_last[1:].min(), ".4f", "-0.0081")
chk("last 250: intercept, % a day", 100 * b_last[0], ".3f", "-0.013")
x_wo = np.delete(X, col["Semiconductor"], axis=1)
_, r2_wo, _ = fit(y[LAST], x_wo[LAST])
chk("last 250 without Semiconductor: R-squared", r2_wo, ".3f", "0.856")
for nm, d in (("full", np.column_stack([np.ones(T), X])), ("last 250", np.column_stack([np.ones(250), X[LAST]]))):
    assert np.linalg.matrix_rank(d) == 29, nm

# per calendar year (stability check)
yearly: dict[int, tuple[Vec, float]] = {}
for yr in range(2009, 2027):
    m = year == yr
    b, r2, _ = fit(y[m], X[m])
    yearly[yr] = (b, r2)
    print(f"{yr}: T = {int(m.sum())}, R-squared {r2:.8f}, Semiconductor {b[1 + col['Semiconductor']]:.4f}, "
          f"FinancialInsurance {b[1 + col['FinancialInsurance']]:.4f}")
chk("2026 returns", float((year == 2026).sum()), ".0f", "185")
chk("Semiconductor 2009", yearly[2009][0][1 + col["Semiconductor"]], ".3f", "0.189")
chk("Semiconductor 2026", yearly[2026][0][1 + col["Semiconductor"]], ".3f", "0.554")
chk("FinancialInsurance 2009", yearly[2009][0][1 + col["FinancialInsurance"]], ".3f", "0.133")
chk("FinancialInsurance 2026", yearly[2026][0][1 + col["FinancialInsurance"]], ".3f", "0.080")
r2_min_year = min(yearly, key=lambda k: yearly[k][1])
assert r2_min_year == 2021 and all(v[1] > r2_full for v in yearly.values())
chk("smallest yearly R-squared (2021)", yearly[2021][1], ".5f", "0.99800")
has("calendar years", "18 years")

# ------------------------------------------------------------------ Section 2: hand examples (exact arithmetic)
xe, ye = np.array([2.0, 1.0]), np.array([1.0, 3.0])
be = float(xe @ ye / (xe @ xe))
assert be == 1.0 and np.allclose(ye - be * xe, [-1, 2]) and float(xe @ (ye - be * xe)) == 0.0
chk("E1 distance sqrt(5)", math.sqrt(5), ".3f", "2.236")
chk("E1 distance of 1.5x", float(np.linalg.norm(ye - 1.5 * xe)), ".1f", "2.5")
chk("KC section 2: |y| = sqrt(10)", math.sqrt(10), ".3f", "3.162")
F = Fraction
x4, y4 = [F(0), F(1), F(2), F(3)], [F(1), F(3), F(2), F(6)]
xm, ym = sum(x4) / 4, sum(y4) / 4
sxy = sum((a - xm) * (b - ym) for a, b in zip(x4, y4, strict=True))
sxx = sum((a - xm) ** 2 for a in x4)
beta4 = sxy / sxx
alpha4 = ym - beta4 * xm
res4 = [b - alpha4 - beta4 * a for a, b in zip(x4, y4, strict=True)]
rss4 = sum(r * r for r in res4)
tss4 = sum((b - ym) ** 2 for b in y4)
assert (xm, ym, sxy, sxx) == (F(3, 2), F(3), F(7), F(5)) and beta4 == F(7, 5) and alpha4 == F(9, 10)
assert res4 == [F(1, 10), F(7, 10), F(-17, 10), F(9, 10)] and sum(res4) == 0
assert sum(a * r for a, r in zip(x4, res4, strict=True)) == 0
assert rss4 == F(21, 5) and tss4 == 14 and 1 - rss4 / tss4 == F(7, 10) and sxy ** 2 / (sxx * tss4) == F(7, 10)
# pitfall: the same data through the origin
b0 = sum(a * b for a, b in zip(x4, y4, strict=True)) / sum(a * a for a in x4)
rss0 = sum((b - b0 * a) ** 2 for a, b in zip(x4, y4, strict=True))
assert b0 == F(25, 14) and sum(b * b for b in y4) == 50
chk("pitfall: slope through the origin", float(b0), ".3f", "1.786")
chk("pitfall: residual sum of squares", float(rss0), ".3f", "5.357")
chk("pitfall: uncentred share from printed 5.357", 1 - 5.357 / 50, ".3f", "0.893")
chk("pitfall: centred formula", float(1 - rss0 / tss4), ".3f", "0.617")
chk("pitfall: centred formula from printed 5.357", 1 - 5.357 / 14, ".3f", "0.617")

# ------------------------------------------------------------------ Section 4: SVD
M5 = np.array([[4.0, 4.0], [-2.0, 4.0]])
G5 = M5.T @ M5
assert G5.tolist() == [[20.0, 8.0], [8.0, 32.0]] and np.trace(G5) == 52 and round(np.linalg.det(G5)) == 576
U5, s5_, Vt5 = np.linalg.svd(M5)
assert np.allclose(s5_, [6, 4])
v1, v2 = sign_rule(Vt5[0]), sign_rule(Vt5[1])
assert np.allclose(v1, np.array([1, 2]) / math.sqrt(5)) and np.allclose(v2, np.array([2, -1]) / math.sqrt(5))
assert np.allclose(M5 @ v1 / 6, np.array([2, 1]) / math.sqrt(5)) and np.allclose(M5 @ v2 / 4, np.array([1, -2]) / math.sqrt(5))
assert round(abs(np.linalg.det(M5))) == 24
# KC section 4: singular values 5 and 0.5
assert 5 / 0.5 == 10 and 5 * 0.5 == 2.5 and 25 / 0.25 == 100 and 25 * 0.25 == 6.25

xc_full = X - X.mean(axis=0)
s_u28 = np.linalg.svd(xc_full / math.sqrt(T), compute_uv=False)
sig = xc_full.T @ xc_full / T
lam = np.linalg.eigvalsh(sig)[::-1]
assert np.allclose(lam, s_u28**2, rtol=1e-10), "lambda_k = s_k^2 fails"
chk("U28 s_1", s_u28[0], ".6f", "0.054245")
chk("U28 s_28", s_u28[-1], ".6f", "0.005218")
chk("U28 kappa(X~)", s_u28[0] / s_u28[-1], ".2f", "10.40")
chk("U28 kappa(X~) from printed s_1, s_28", 0.054245 / 0.005218, ".2f", "10.40")
chk("U28 kappa(Sigma)", (s_u28[0] / s_u28[-1]) ** 2, ".2f", "108.09")
assert abs(np.linalg.cond(sig) - (s_u28[0] / s_u28[-1]) ** 2) < 1e-8


def solver_gap(cols: list[str], mask: NDArray[np.bool_]) -> tuple[float, float, float]:
    """kappa(X~), kappa(X~'X~) and the largest gap between lstsq on X~ and solve on the normal equations."""
    xs = mat(ret.filter(pl.Series(mask)), cols)
    ys = y[mask]
    xc = xs - xs.mean(axis=0)
    yc = ys - ys.mean()
    s = np.linalg.svd(xc, compute_uv=False)
    b1 = np.linalg.lstsq(xc, yc, rcond=None)[0]
    b2 = np.linalg.solve(xc.T @ xc, xc.T @ yc)
    return float(s[0] / s[-1]), float(np.linalg.cond(xc.T @ xc)), float(np.abs(b1 - b2).max())


Y2016 = year == 2016
rows_cond = [("S3", S3, FULL, "2.654", "7.045", ".3f", ".3f"), ("S5", S5, FULL, "3.481", "12.12", ".3f", ".2f"),
             ("U28 full", U28, FULL, "10.40", "108.09", ".2f", ".2f"), ("U28 last 250", U28, LAST, "17.04", "290.2", ".2f", ".1f"),
             ("U28 + Electronic full", ["Electronic", *U28], FULL, "48.33", "2,336", ".2f", ",.0f"),
             ("U28 + Electronic 2016", ["Electronic", *U28], Y2016, "642.0", "412,167", ".1f", ",.0f")]
gaps: dict[str, float] = {}
for nm, cols, mask, p1, p2, f1, f2 in rows_cond:
    k1, k2, gap = solver_gap(cols, mask)
    gaps[nm] = gap
    print(f"cond table {nm}: kappa(X~) {k1:.4f}, kappa(X~'X~) {k2:.2f}, gap {gap:.1e}")
    chk(f"cond {nm} kappa(X~)", k1, f1, p1)
    chk(f"cond {nm} kappa(X~'X~)", k2, f2, p2)
for nm in ("S3", "S5", "U28 full", "U28 last 250"):
    assert gaps[nm] < 1e-14, (nm, gaps[nm])
assert gaps["U28 + Electronic full"] < 1e-12
assert 1e-12 <= gaps["U28 + Electronic 2016"] < 1e-11, gaps["U28 + Electronic 2016"]
has("gap order", "$10^{-12}$ to $10^{-11}$")
chk("digits lost, U28", math.log10(solver_gap(U28, FULL)[1]), ".1f", "2.0")
chk("digits lost, U28 + Electronic 2016", math.log10(solver_gap(["Electronic", *U28], Y2016)[1]), ".1f", "5.6")

# ------------------------------------------------------------------ Section 5: December 2008 and numerical rank
assert np.linalg.matrix_rank(d_dec) == 22 and d_dec.shape == (22, 29)
assert np.abs(np.linalg.lstsq(d_dec, y[DEC], rcond=None)[0] - b_dec).max() < 1e-12, "lstsq is not the minimum-norm fit"
assert np.abs(e_dec).max() < 1e-13
chk("December 2008 null space", 29 - 22, ".0f", "7")
chk("December 2008 minimum-norm: norm of 29 coefficients", float(np.linalg.norm(b_dec)), ".3f", "0.285")
d_wo = np.delete(d_dec, 1 + col["Semiconductor"], axis=1)
names_wo = ["intercept", *[c for c in U28 if c != "Semiconductor"]]
b_wo = np.linalg.pinv(d_wo) @ y[DEC]
e_wo = y[DEC] - d_wo @ b_wo
assert np.linalg.matrix_rank(d_wo) == 22 and np.abs(e_wo).max() < 1e-13
for c, p in (("FinancialInsurance", "0.218"), ("ElectronicPartsComponents", "0.172"), ("CommunicationsInternet", "0.068")):
    chk(f"December 2008 without Semiconductor: {c}", b_wo[names_wo.index(c)], ".3f", p)
chk("December 2008 without Semiconductor: sum", b_wo[1:].sum(), ".3f", "0.914")
chk("December 2008 without Semiconductor: norm", float(np.linalg.norm(b_wo)), ".3f", "0.401")
has("null space without Semiconductor", "| Dimension of the null space | 7 | 6 |")
common = [c for c in U28 if c != "Semiconductor"]
diffs = [abs(b_dec[1 + col[c]] - b_wo[names_wo.index(c)]) for c in common] + [abs(b_dec[0] - b_wo[0])]
assert min(diffs) > 1e-4, "an exact-fit coefficient agrees in both fits"
print(f"December 2008: the two exact fits differ on every coefficient (smallest gap {min(diffs):.5f})")
sig_dec = cov0(X[DEC])
assert np.linalg.matrix_rank(sig_dec) == 21
try:
    np.linalg.cholesky(sig_dec)
    raise AssertionError("cholesky succeeded on December 2008's Sigma")
except np.linalg.LinAlgError:
    print("December 2008: Sigma has rank 21; np.linalg.cholesky raises LinAlgError")
chk("machine precision", float(np.finfo(np.float64).eps) * 1e16, ".1f", "2.2")

e9 = mat(ret, ["Electronic", *ELEC8])


def std_sv(m: NDArray[np.bool_], standardize: bool = True) -> Vec:
    z = e9[m] - e9[m].mean(axis=0)
    if standardize:
        z = z / z.std(axis=0)
    return np.linalg.svd(z / math.sqrt(int(m.sum())), compute_uv=False)


sv_full, sv_2016 = std_sv(FULL), std_sv(Y2016)
chk("Electronic + eight: s_9/s_1 full", sv_full[-1] / sv_full[0], ".4f", "0.0346")
chk("Electronic + eight: s_9/s_1 2016", sv_2016[-1] / sv_2016[0], ".5f", "0.00277")
chk("Electronic + eight: s_9/s_1 2016 in %", 100 * sv_2016[-1] / sv_2016[0], ".1f", "0.3")
chk("Electronic + eight: covariance scale, full", std_sv(FULL, False)[-1] / std_sv(FULL, False)[0], ".4f", "0.0329")


def nrank(s: Vec, delta: float) -> int:
    return int((s > delta * s[0]).sum())


assert (nrank(sv_full, 0.01), nrank(sv_2016, 0.01), nrank(sv_full, 0.1), nrank(sv_2016, 0.1)) == (9, 8, 8, 8)
ranks_year = {}
for yr in range(2009, 2027):
    m = year == yr
    zs = (e9[m] - e9[m].mean(axis=0)) / e9[m].std(axis=0)
    ranks_year[yr] = (nrank(std_sv(m), 0.01), int(np.linalg.matrix_rank(zs)))
print("Electronic + eight, rank at delta = 0.01 and matrix_rank by year:", ranks_year)
assert all(v[1] == 9 for v in ranks_year.values())
assert [yr for yr, v in ranks_year.items() if v[0] == 9] == [2009, 2010, 2018]
assert sum(v[0] == 8 for v in ranks_year.values()) == 15
has("years with rank 9", "9 in 2009, 2010 and 2018 and 8 in the other 15 years")
has("Problem 12 standardizes within each year", "within that year (divisor $T$)")
sv_2010 = std_sv(year == 2010)
chk("Electronic + eight: s_9/s_1 in 2010, standardized within the year", sv_2010[-1] / sv_2010[0], ".5f", "0.01004")
assert nrank(sv_2010, 0.01) == 9 and nrank(sv_2010, 0.0101) == 8, "2010 is no longer just above the tolerance"

# ------------------------------------------------------------------ Section 6: Cholesky, whitening
i5 = [col[c] for c in S5]
sig5 = sig[np.ix_(i5, i5)]
L5 = np.linalg.cholesky(sig5)
assert np.allclose(L5 @ L5.T, sig5, rtol=0, atol=1e-18)
chk("E9 sigma_11 (x 1e4)", sig5[0, 0] * 1e4, ".6f", "2.323354")
chk("E9 sigma_21 (x 1e4)", sig5[1, 0] * 1e4, ".6f", "1.066603")
chk("E9 sigma_22 (x 1e4)", sig5[1, 1] * 1e4, ".6f", "1.481729")
chk("E9 l_11", L5[0, 0], ".7f", "0.0152426")
chk("E9 l_21", L5[1, 0], ".6f", "0.006998")
chk("E9 l_22", L5[1, 1], ".6f", "0.009960")
chk("E9 l_11 from printed sigma_11", math.sqrt(2.323354e-4), ".7f", "0.0152426")
chk("E9 l_21 from printed inputs", 1.066603e-4 / 0.0152426, ".6f", "0.006998")
chk("E9 l_22 from printed inputs", math.sqrt(1.481729e-4 - 0.006998**2), ".6f", "0.009960")
chk("E9 slope sigma_21/sigma_11", sig5[1, 0] / sig5[0, 0], ".4f", "0.4591")
chk("E9 slope from printed l_21/l_11", 0.006998 / 0.0152426, ".4f", "0.4591")
chk("E9 slope from printed sigma", 1.066603 / 2.323354, ".4f", "0.4591")
xs1 = xc_full[:, i5[:1]]
slope_fin = np.linalg.lstsq(xs1, xc_full[:, i5[1]], rcond=None)[0][0]
assert abs(slope_fin - sig5[1, 0] / sig5[0, 0]) < 1e-12
chk("E9 l_22 in % a day", 100 * L5[1, 1], ".3f", "0.996")
chk("E9 FinancialInsurance s.d. in % a day", 100 * math.sqrt(sig5[1, 1]), ".3f", "1.217")
chk("E9 S3 l_33", L5[2, 2], ".6f", "0.008594")
res_food = xc_full[:, i5[2]] - xc_full[:, i5[:2]] @ np.linalg.lstsq(xc_full[:, i5[:2]], xc_full[:, i5[2]], rcond=None)[0]
assert abs(math.sqrt(float(res_food @ res_food) / T) - L5[2, 2]) < 1e-12
res_ship = xc_full[:, i5[4]] - xc_full[:, i5[:4]] @ np.linalg.lstsq(xc_full[:, i5[:4]], xc_full[:, i5[4]], rcond=None)[0]
assert abs(math.sqrt(float(res_ship @ res_ship) / T) - L5[4, 4]) < 1e-12
printed_L = [["1.5243"], ["0.6998", "0.9960"], ["0.4336", "0.4779", "0.8594"],
             ["0.7238", "0.5162", "0.1831", "1.3034"], ["0.6415", "0.5995", "0.2050", "0.1109", "1.4358"]]
for i, row in enumerate(printed_L):
    for j, p in enumerate(row):
        chk(f"chol L[{i + 1},{j + 1}] in %", 100 * L5[i, j], ".4f", p)
    assert abs(sum(float(p) ** 2 for p in row) - 1e4 * sig5[i, i]) < 2e-3, "a printed row does not square to its variance"
chk("chol: 1.5243^2 from the printed entry", 1.5243**2, ".3f", "2.323")
# LM10's pivots are l_jj^2: leading minors are products of l_jj^2
for j in range(1, 6):
    minor, prod = float(np.linalg.det(sig5[:j, :j])), float(np.prod(np.diag(L5)[:j] ** 2))
    assert abs(minor - prod) < 1e-10 * prod, (j, minor, prod)

# whitening: z_t = L^{-1}(R_t - mean), the mean of |z_t|^2 is exactly N
xc5 = xc_full[:, i5]
z5 = np.linalg.solve(L5, xc5.T).T
assert np.allclose(z5.T @ z5 / T, np.eye(5), atol=1e-12)
q5 = (z5**2).sum(axis=1)
assert abs(q5.mean() - 5) < 1e-9
chk("mean |z|^2, S5", float(q5.mean()), ".0f", "5")
L28 = np.linalg.cholesky(sig)
z28 = np.linalg.solve(L28, xc_full.T).T
assert abs((z28**2).sum(axis=1).mean() - 28) < 1e-9
chk("mean |z|^2, U28 (knowledge check)", float((z28**2).sum(axis=1).mean()), ".0f", "28")
i7 = dates.index("2025-04-07")
for c, p in zip(S5, ("-9.95", "-9.89", "-8.66", "-9.90", "-9.73"), strict=True):
    chk(f"7 April 2025 return {c}", 100 * X[i7, col[c]], ".2f", p)
assert int((100 * X[i7, i5] <= -9.7).sum()) == 4
centred_p = ("-10.048", "-9.939", "-8.693", "-9.947", "-9.772")
for c, k, p in zip(S5, range(5), centred_p, strict=True):
    chk(f"7 April 2025 centred {c}", 100 * xc5[i7, k], ".3f", p)
z_given = z5[i7]
rev = i5[::-1]
L_rev = np.linalg.cholesky(sig[np.ix_(rev, rev)])
z_rev = np.linalg.solve(L_rev, xc_full[i7, rev])
z_rev_by_sector = z_rev[::-1]                       # back to the order Semiconductor .. ShippingTransportation
for c, k, pg, pr in zip(S5, range(5), ("-6.592", "-5.347", "-3.815", "-1.317", "-0.981"),
                        ("-1.541", "-2.709", "-5.109", "-4.518", "-5.751"), strict=True):
    chk(f"z given order {c}", z_given[k], ".3f", pg)
    chk(f"z reversed order {c}", z_rev_by_sector[k], ".3f", pr)
chk("|z|^2 on 7 April 2025", float(z_given @ z_given), ".2f", "89.30")
assert abs(float(z_rev @ z_rev) - float(z_given @ z_given)) < 1e-9
chk("|z|^2 from the printed given-order entries", sum(float(p) ** 2 for p in ("-6.592", "-5.347", "-3.815", "-1.317", "-0.981")), ".2f", "89.30")
chk("|z|^2 from the printed reversed-order entries", sum(float(p) ** 2 for p in ("-1.541", "-2.709", "-5.109", "-4.518", "-5.751")), ".2f", "89.30")
chk("E10 z_1 from printed inputs", -10.048 / 1.5243, ".3f", "-6.592")
chk("E10 z_2 from printed inputs", (-9.939 - 0.6998 * (-10.048 / 1.5243)) / 0.9960, ".3f", "-5.347")
chk("E10 z_2 from printed z_1", (-9.939 - 0.6998 * -6.592) / 0.9960, ".3f", "-5.347")
assert int((q5 > q5[i7]).sum()) == 0, "7 April 2025 is not the largest"
top = np.argsort(-q5)[:5]
for rank, (k, pd, pq, pt) in enumerate(zip(top, ("2025-04-07", "2026-07-31", "2025-04-10", "2020-07-27", "2026-07-17"),
                                           ("89.30", "74.13", "65.98", "61.28", "55.58"),
                                           ("-9.70", "+7.98", "+9.25", "+2.31", "-6.47"), strict=True), 1):
    assert dates[k] == pd, (rank, dates[k], pd)
    has(f"top-5 date {rank}", f"| {rank} | {pd} |")
    chk(f"top-5 |z|^2 {pd}", float(q5[k]), ".2f", pq)
    chk(f"top-5 TAIEX return {pd}", float(100 * y[int(k)]), "+.2f", pt)
assert REPAIRED.is_dir(), "data/raw/sectors_close/ is missing: run data/fetch_finmind.py"
repairs = [f.stem.split("__") for f in REPAIRED.glob("*__*.csv")]
assert len(repairs) == 561, "the manifest lists 561 repaired closes"
in_window = [(sid, d) for sid, d in repairs if FIRST_CLOSE <= d <= LAST_CLOSE]
rep_u28 = [(sid, d) for sid, d in in_window if sid in U28]
rep_elec = [(sid, d) for sid, d in in_window if sid == "Electronic"]
assert not [d for sid, d in in_window if sid == "TAIEX"], "a TAIEX close was repaired"
assert {d for _, d in rep_elec} <= {d for _, d in rep_u28}, "an Electronic repair falls on a date without a U28 repair"
print(f"repaired closes in the sample: U28 {len(rep_u28)} on {len({d for _, d in rep_u28})} dates, "
      f"Electronic {len(rep_elec)}, others {len(in_window) - len(rep_u28) - len(rep_elec)} (not used)")
chk("repaired U28 closes in the sample", float(len(rep_u28)), ".0f", "524")
chk("dates of the repaired U28 closes", float(len({d for _, d in rep_u28})), ".0f", "38")
chk("repaired U28 and Electronic closes", float(len(rep_u28) + len(rep_elec)), ".0f", "542")
has("U28 repairs in the case source", "524 copied closes on 38 dates in this sample")
has("repairs in the References", "524 closes on 38 dates of the U28 sample, 542 with Electronic")
chk("sector indices served", 30.0, ".0f", "30")
has("U28's description", "the 28 leaf indices among the 30 TWSE sector indices that FinMind serves daily")
has("the four sector indices of 30 June 2023", "base date 30 June 2023")
chk("pitfall: smallest fall of the four", -100 * X[i7, col["ShippingTransportation"]], ".2f", "9.73")
chk("pitfall: largest fall", -100 * X[i7, col["Semiconductor"]], ".2f", "9.95")
chk("December 2008 Sigma rank", float(np.linalg.matrix_rank(sig_dec)), ".0f", "21")
for k in top:
    for d in (dates[k], ret["prev"][int(k)]):
        hits = [c for c in S5 if (REPAIRED / f"{c}__{d}.csv").exists()]
        assert not hits, f"a top-5 return uses a repaired close: {hits} on {d}"
has("no repaired close in the top five", "No close on these dates or the dates before them was repaired")
z3 = np.linalg.solve(np.linalg.cholesky(sig[np.ix_(i5[:3], i5[:3])]), xc_full[:, i5[:3]].T).T
q3 = (z3**2).sum(axis=1)
print(f"S3 on 7 April 2025: |z|^2 = {q3[i7]:.2f}, rank {int((q3 > q3[i7]).sum()) + 1} (not printed in the text)")

# ------------------------------------------------------------------ practice problems
# 3: Cholesky of three 2x2 matrices
A3, B3, C3 = np.array([[4.0, 2.0], [2.0, 5.0]]), np.array([[4.0, 6.0], [6.0, 9.0]]), np.array([[1.0, 3.0], [3.0, 4.0]])
assert np.allclose(np.linalg.cholesky(A3), [[2, 0], [1, 2]])
assert (round(np.linalg.det(A3)), round(np.linalg.det(B3)), round(np.linalg.det(C3))) == (16, 0, -5)
for bad in (B3, C3):
    try:
        np.linalg.cholesky(bad)
        raise AssertionError("cholesky of a matrix that is not positive definite succeeded")
    except np.linalg.LinAlgError:
        pass
# 4: four-point line
x4b, y4b = [F(-1), F(0), F(1), F(2)], [F(0), F(1), F(1), F(4)]
xm4, ym4 = sum(x4b) / 4, sum(y4b) / 4
sxy4 = sum((a - xm4) * (b - ym4) for a, b in zip(x4b, y4b, strict=True))
sxx4 = sum((a - xm4) ** 2 for a in x4b)
bb = sxy4 / sxx4
aa = ym4 - bb * xm4
rr = [b - aa - bb * a for a, b in zip(x4b, y4b, strict=True)]
tss = sum((b - ym4) ** 2 for b in y4b)
assert (xm4, ym4, sxy4, sxx4, bb, aa) == (F(1, 2), F(3, 2), F(6), F(5), F(6, 5), F(9, 10))
assert rr == [F(3, 10), F(1, 10), F(-11, 10), F(7, 10)] and sum(rr) == 0 and sum(a * r for a, r in zip(x4b, rr, strict=True)) == 0
assert sum(r * r for r in rr) == F(9, 5) and tss == 9 and 1 - F(9, 5) / 9 == F(4, 5) and sxy4**2 / (sxx4 * tss) == F(4, 5)
# 5: projection on (1, 1, 0)
x5 = np.array([[1.0], [1.0], [0.0]])
P5 = x5 @ x5.T / 2
assert np.allclose(P5 @ P5, P5) and np.trace(P5) == 1 and np.allclose(P5 @ [3, 1, 2], [2, 2, 0])
assert float(x5[:, 0] @ (np.array([3, 1, 2]) - P5 @ [3, 1, 2])) == 0
# 6: SVD of [[2, 0], [3, 2]]
M6 = np.array([[2.0, 0.0], [3.0, 2.0]])
G6 = M6.T @ M6
assert G6.tolist() == [[13.0, 6.0], [6.0, 4.0]] and np.trace(G6) == 17 and round(np.linalg.det(G6)) == 16
_, s6, Vt6 = np.linalg.svd(M6)
assert np.allclose(s6, [4, 1])
w1, w2 = sign_rule(Vt6[0]), sign_rule(Vt6[1])
assert np.allclose(w1, np.array([2, 1]) / math.sqrt(5)) and np.allclose(w2, np.array([-1, 2]) / math.sqrt(5))
assert np.allclose(M6 @ w1 / 4, np.array([1, 2]) / math.sqrt(5)) and np.allclose(M6 @ w2, np.array([-2, 1]) / math.sqrt(5))
assert round(abs(np.linalg.det(M6))) == 4
# 7: rank-one system
M7, y7 = np.array([[1.0, 2.0], [2.0, 4.0]]), np.array([5.0, 10.0])
assert np.linalg.matrix_rank(M7) == 1 and np.allclose(np.linalg.pinv(M7), np.array([[1, 2], [2, 4]]) / 25)
assert np.allclose(np.linalg.pinv(M7) @ y7, [1, 2]) and np.allclose(np.linalg.lstsq(M7, y7, rcond=None)[0], [1, 2])
# 8: S5's printed singular values
s5p = [0.024240, 0.013487, 0.011470, 0.009351, 0.006964]
s5_true = np.linalg.svd(xc5 / math.sqrt(T), compute_uv=False)
for v, p in zip(s5_true, ("0.024240", "0.013487", "0.011470", "0.009351", "0.006964"), strict=True):
    chk(f"S5 singular value {p}", float(v), ".6f", p)
for v, p in zip(s5p, ("5.876", "1.819", "1.316", "0.874", "0.485"), strict=True):
    chk(f"S5 eigenvalue x 1e4 from printed s_k {p}", v * v * 1e4, ".3f", p)
chk("S5 kappa(X~) from printed s", s5p[0] / s5p[-1], ".3f", "3.481")
chk("S5 kappa(Sigma) from printed kappa", 3.481**2, ".2f", "12.12")
chk("S5 log10 kappa(Sigma)", math.log10(12.12), ".2f", "1.08")
# 9 and 10: LM7's printed annualized covariance matrix of 0050 and 00679B (src/lm07.md, example "marginal"),
# the matrix LM9 and LM11 use too
var1_7, var2_7, cov_7 = 0.040425, 0.018214, -0.002866
lm07 = (ROOT / "src" / "lm07.md").read_text(encoding="utf-8").replace("−", "-")
assert all(s in lm07 for s in ("\\sigma_1^2=0.040425", "\\sigma_2^2=0.018214", "\\sigma_{12}=-0.002866")), \
    "LM7 no longer prints this covariance matrix"
has("P9 inputs", "$\\sigma_1^2=0.040425$, $\\sigma_2^2=0.018214$ and $\\sigma_{12}=-0.002866$")
L7 = np.linalg.cholesky(np.array([[var1_7, cov_7], [cov_7, var2_7]]))
chk("P9 l_11", L7[0, 0], ".5f", "0.20106")
chk("P9 l_21", L7[1, 0], ".6f", "-0.014254")
chk("P9 l_21 from printed l_11", cov_7 / 0.20106, ".6f", "-0.014254")
chk("P9 l_22", L7[1, 1], ".6f", "0.134204")
chk("P9 l_22 from printed inputs", math.sqrt(var2_7 - 0.014254**2), ".6f", "0.134204")
chk("P9 slope l_21/l_11", L7[1, 0] / L7[0, 0], ".4f", "-0.0709")
chk("P9 slope sigma_12/sigma_1^2", cov_7 / var1_7, ".4f", "-0.0709")
chk("P9 slope from printed l_21/l_11", -0.014254 / 0.20106, ".4f", "-0.0709")
chk("P9 l_22 in %", 100 * L7[1, 1], ".2f", "13.42")
chk("P9 l_22 in % from printed", 100 * 0.134204, ".2f", "13.42")
chk("P9 00679B volatility in %", 100 * math.sqrt(var2_7), ".2f", "13.50")
d10 = np.array([-0.30, 0.10])
z10 = np.linalg.solve(L7, d10)
chk("P10 z_1", z10[0], ".3f", "-1.492")
chk("P10 z_1 from printed l_11", -0.30 / 0.20106, ".3f", "-1.492")
chk("P10 z_2", z10[1], ".3f", "0.587")
chk("P10 z_2 from printed inputs", (0.10 - 0.014254 * 1.492) / 0.134204, ".3f", "0.587")
chk("P10 |z|^2", float(z10 @ z10), ".2f", "2.57")
chk("P10 |z|^2 = d' Sigma^-1 d", float(d10 @ np.linalg.solve(np.array([[var1_7, cov_7], [cov_7, var2_7]]), d10)),
    ".2f", "2.57")
L7r = np.linalg.cholesky(np.array([[var2_7, cov_7], [cov_7, var1_7]]))
chk("P10 reversed l_11", L7r[0, 0], ".6f", "0.134959")
chk("P10 reversed l_21", L7r[1, 0], ".6f", "-0.021236")
chk("P10 reversed l_21 from printed l_11", cov_7 / 0.134959, ".6f", "-0.021236")
chk("P10 reversed l_22", L7r[1, 1], ".6f", "0.199935")
chk("P10 reversed l_22 from printed inputs", math.sqrt(var1_7 - 0.021236**2), ".6f", "0.199935")
z10r = np.linalg.solve(L7r, d10[::-1])
chk("P10 reversed z_1", z10r[0], ".3f", "0.741")
chk("P10 reversed z_1 from printed l_11", 0.10 / 0.134959, ".3f", "0.741")
chk("P10 reversed z_2", z10r[1], ".3f", "-1.422")
chk("P10 reversed z_2 from printed inputs", (-0.30 + 0.021236 * 0.741) / 0.199935, ".3f", "-1.422")
chk("P10 reversed |z|^2", float(z10r @ z10r), ".2f", "2.57")
chk("P10 |z|^2 from printed entries", 1.492**2 + 0.587**2, ".2f", "2.57")
chk("P10 reversed |z|^2 from printed entries", 0.741**2 + 1.422**2, ".2f", "2.57")
# 11: last-250 fit three ways
xl = X[LAST] - X[LAST].mean(axis=0)
yl = y[LAST] - y[LAST].mean()
b_ne = np.linalg.solve(xl.T @ xl, xl.T @ yl)
b_pi = np.linalg.pinv(np.column_stack([np.ones(250), X[LAST]])) @ y[LAST]
assert np.abs(b_ne - b_last[1:]).max() < 1e-14 and np.abs(b_pi[1:] - b_last[1:]).max() < 1e-14
s_l = np.linalg.svd(xl, compute_uv=False)
chk("P11 kappa(X~) last 250", s_l[0] / s_l[-1], ".2f", "17.04")

print(f"\nall {N_CHECKS} checks passed")
