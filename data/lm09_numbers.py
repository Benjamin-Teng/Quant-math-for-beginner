"""Every number that LM9 (Linear Systems, Inverses and Rank) prints, computed and checked.

Run after data/vol2_series.py:  uv run python data/lm09_numbers.py

Inputs: data/processed/vol2_closes.parquet (TAIEX and the 30 TWSE sector price indices, closes repaired by
data/vol2_series.py) and data/processed/vol2_repairs.json. Nothing else is read.

* The hand-sized systems use the percent returns 100 (P_t / P_{t-1} - 1) of TAIEX, Semiconductor, FinancialInsurance
  and Food on 7, 8, 9 and 10 April 2025, between consecutive TAIEX trading dates, rounded to 0.01. The rounded values
  are the inputs: every system built from them is solved in exact rational arithmetic (fractions.Fraction), so each
  printed solution is the exact solution for the printed inputs, rounded only when it is printed.
* Section 7 uses daily simple returns R_t = P_t / P_{t-1} - 1 on the common sample 2008-12-01 .. 2026-10-08 (float64,
  NumPy), as the Volume II briefs define it.

Every printed value is checked twice (AUTHORING section 8, PITFALLS section 7): it must follow from the inputs the
module prints next to it, and it must appear in src/lm09.md exactly as printed. The script stops on any mismatch.
"""
import contextlib
import io
import json
import math
import re
from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal, localcontext
from fractions import Fraction as Fr
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CLOSES = HERE / "processed" / "vol2_closes.parquet"
REPAIRS = HERE / "processed" / "vol2_repairs.json"
TEXT = ROOT / "src" / "lm09.md"
P = print

Mat = list[list[Fr]]
Vec = list[Fr]


# ---------------------------------------------------------------- exact arithmetic
def dec(x: Fr | int, d: int) -> str:
    """The exact rational x rounded to d decimals, as text ('-0.916113'). An exact tie is refused: the module
    would have to say which way it rounds."""
    x = Fr(x)
    twice = x * 10**d * 2
    assert not (twice.denominator == 1 and twice.numerator % 2 == 1), f"exact rounding tie: {x} to {d} decimals"
    with localcontext() as ctx:
        ctx.prec = 80
        q = Decimal(x.numerator) / Decimal(x.denominator)
        r = q.quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_EVEN)
    s = format(r, "f")
    return "0" + s[2:] if s.startswith("-0") and set(s[1:]) <= set("0.") else s   # no "-0.000"


def det(m: Mat) -> Fr:
    """Determinant by cofactor expansion along the first row (exact)."""
    n = len(m)
    if n == 1:
        return m[0][0]
    return sum(((-1) ** j * m[0][j] * det(minor(m, 0, j)) for j in range(n)), Fr(0))


def minor(m: Mat, i: int, j: int) -> Mat:
    """M^(ij): M without row i and column j (0-based indices)."""
    return [row[:j] + row[j + 1:] for k, row in enumerate(m) if k != i]


def rref(m: Mat) -> tuple[Mat, list[int]]:
    """Reduced row echelon form and pivot columns (exact; the first non-zero entry is the pivot)."""
    a = [row[:] for row in m]
    rows, cols, piv, r = len(a), len(a[0]), [], 0
    for c in range(cols):
        k = next((i for i in range(r, rows) if a[i][c] != 0), None)
        if k is None:
            continue
        a[r], a[k] = a[k], a[r]
        p = a[r][c]
        a[r] = [v / p for v in a[r]]
        for i in range(rows):
            if i != r and a[i][c] != 0:
                f = a[i][c]
                a[i] = [v - f * w for v, w in zip(a[i], a[r])]
        piv.append(c)
        r += 1
        if r == rows:
            break
    return a, piv


def rank(m: Mat) -> int:
    return len(rref(m)[1])


def solve(m: Mat, b: Vec) -> Vec:
    a, piv = rref([row + [bi] for row, bi in zip(m, b)])
    assert piv == list(range(len(m))), "not a square system with a unique solution"
    return [row[-1] for row in a]


def inverse(m: Mat) -> Mat:
    n = len(m)
    a, piv = rref([row + [Fr(int(i == j)) for j in range(n)] for i, row in enumerate(m)])
    assert piv == list(range(n)), "singular"
    return [row[n:] for row in a]


def matmul(m: Mat, k: Mat) -> Mat:
    return [[sum((m[i][s] * k[s][j] for s in range(len(k))), Fr(0)) for j in range(len(k[0]))] for i in range(len(m))]


def matvec(m: Mat, x: Vec) -> Vec:
    return [sum((a * b for a, b in zip(row, x)), Fr(0)) for row in m]


def col(m: Mat, j: int) -> Vec:
    return [row[j] for row in m]


def with_col(m: Mat, j: int, v: Vec) -> Mat:
    """M_j(b): M with column j replaced by v."""
    return [row[:j] + [vi] + row[j + 1:] for row, vi in zip(m, v)]


def angle(u: Vec, v: Vec) -> float:
    """Angle between two vectors in degrees."""
    fu, fv = np.array([float(a) for a in u]), np.array([float(a) for a in v])
    return math.degrees(math.acos(float(fu @ fv) / float(np.linalg.norm(fu) * np.linalg.norm(fv))))


def norm(u: Vec) -> float:
    return math.sqrt(float(sum(a * a for a in u)))


# ---------------------------------------------------------------- the four days (exhibit days)
SERIES = ["TAIEX", "Semiconductor", "FinancialInsurance", "Food"]
SECT = SERIES[1:]
DAYS = ["2025-04-07", "2025-04-08", "2025-04-09", "2025-04-10"]
cl = pl.read_parquet(CLOSES).sort("date")
dates = cl["date"].to_list()
i0 = dates.index(DAYS[0])
assert dates[i0 - 1] == "2025-04-02" and dates[i0:i0 + 4] == DAYS, "the four sessions are not consecutive TAIEX dates"
win = dates[i0 - 1:i0 + 4]
closes: dict[str, list[Fr]] = {}
for s in SERIES:
    vals = cl.filter(pl.col("date").is_in(win)).sort("date")[s].to_list()
    exact = []
    for v in vals:
        d2 = Decimal(str(round(v, 2)))
        assert float(d2) == v, (s, v)                      # a two-decimal close, stored as the nearest double
        exact.append(Fr(d2))
    closes[s] = exact
rep = json.loads(REPAIRS.read_text(encoding="utf-8"))
touched = [r for r in rep["repairs"] if r["date"] in win and r["series"] in SERIES]
assert not touched, touched                                 # no close in the window was repaired
ret_exact = {s: [100 * (closes[s][k + 1] / closes[s][k] - 1) for k in range(4)] for s in SERIES}
ret: dict[str, list[Fr]] = {}
tie_gap = []
for s in SERIES:
    rr = []
    for k, v in enumerate(ret_exact[s]):
        with localcontext() as ctx:
            ctx.prec = 60
            q = Decimal(v.numerator) / Decimal(v.denominator)
            up = q.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            even = q.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
        assert up == even
        rr.append(Fr(up))
        h = v * 100 - math.floor(v * 100)                   # fraction of a hundredth; a rounding tie sits at 1/2
        tie_gap.append((abs(h - Fr(1, 2)) / 100, s, DAYS[k], v))
    ret[s] = rr
tie_gap.sort()
P("DAYS returns (%), rounded to 0.01 [TAIEX, Semi, Fin, Food]:")
for k, d in enumerate(DAYS):
    P(f"   {d}: " + ", ".join(dec(ret[s][k], 2) for s in SERIES) + "   unrounded: " + ", ".join(dec(ret_exact[s][k], 6) for s in SERIES))
P(f"   TAIEX 7 Apr unrounded {dec(ret_exact['TAIEX'][0], 6)}% (closes {dec(closes['TAIEX'][0], 2)} -> {dec(closes['TAIEX'][1], 2)})")
P(f"   nearest rounding tie: {tie_gap[0][1]} {tie_gap[0][2]} {dec(tie_gap[0][3], 6)} ({dec(tie_gap[0][0], 6)} away); "
  f"next {tie_gap[1][1]} {tie_gap[1][2]} {dec(tie_gap[1][3], 6)} ({dec(tie_gap[1][0], 6)} away)")

MF: Mat = [[ret[s][k] for s in SECT] for k in range(4)]       # rows = days, columns = Semi, Fin, Food
BF: Vec = [ret["TAIEX"][k] for k in range(4)]
ones3 = [Fr(-1)] * 3
row7 = MF[0]
P(f"   7 April row {[dec(v, 2) for v in row7]}: angle with -1 = {angle(row7, ones3):.4f} deg")


def sub(rows: list[int], cols: list[int]) -> tuple[Mat, Vec]:
    return [[MF[r][c] for c in cols] for r in rows], [BF[r] for r in rows]


# ---------------------------------------------------------------- E1, E2: two unknowns
M1, b1 = sub([1, 2], [0, 1])                               # 8, 9 April; Semi, Fin
d1 = det(M1)
x1 = solve(M1, b1)
P(f"E1 (8-9 Apr; Semi, Fin): det {dec(d1, 6)}; numerators {dec(det(with_col(M1, 0, b1)), 6)}, {dec(det(with_col(M1, 1, b1)), 6)}; "
  f"x = ({dec(x1[0], 6)}, {dec(x1[1], 6)}); angle between columns {angle(col(M1, 0), col(M1, 1)):.4f}; "
  f"|m1| {norm(col(M1, 0)):.6f} |m2| {norm(col(M1, 1)):.6f} product {norm(col(M1, 0)) * norm(col(M1, 1)):.4f}")
P(f"   E1 hand steps: 5.61 eq1 + 0.53 eq2 ... -3.99*5.61={dec(Fr('-3.99') * Fr('5.61'), 4)} -4.47*0.53={dec(Fr('-4.47') * Fr('0.53'), 4)} "
  f"-4.02*5.61={dec(Fr('-4.02') * Fr('5.61'), 4)} -5.79*0.53={dec(Fr('-5.79') * Fr('0.53'), 4)}; "
  f"4.47*0.53={dec(Fr('4.47') * Fr('0.53'), 4)} 3.99*5.61={dec(Fr('3.99') * Fr('5.61'), 4)} -4.02*4.47={dec(Fr('-4.02') * Fr('4.47'), 4)} 5.79*3.99={dec(Fr('5.79') * Fr('3.99'), 4)}")
P(f"   E1 check eq1: {dec(matvec(M1, x1)[0], 6)} eq2: {dec(matvec(M1, x1)[1], 6)}; scaled columns x1 m1 = ({dec(x1[0] * M1[0][0], 6)}, {dec(x1[0] * M1[1][0], 6)}), "
  f"x2 m2 = ({dec(x1[1] * M1[0][1], 6)}, {dec(x1[1] * M1[1][1], 6)})")
M2, b2 = sub([0, 2], [0, 2])                               # 7, 9 April; Semi, Food
d2 = det(M2)
x2 = solve(M2, b2)
P(f"E2 (7, 9 Apr; Semi, Food): det {dec(d2, 6)}; x = ({dec(x2[0], 6)}, {dec(x2[1], 6)}); angle {angle(col(M2, 0), col(M2, 1)):.4f}; "
  f"|m1| {norm(col(M2, 0)):.6f} |m2| {norm(col(M2, 1)):.6f} product {norm(col(M2, 0)) * norm(col(M2, 1)):.4f}; "
  f"det/product {float(d2) / (norm(col(M2, 0)) * norm(col(M2, 1))):.6f}; E1 det/product {float(d1) / (norm(col(M1, 0)) * norm(col(M1, 1))):.6f}")
P(f"   E2 products: -9.95*-4.17={dec(Fr('-9.95') * Fr('-4.17'), 4)} -8.66*-4.47={dec(Fr('-8.66') * Fr('-4.47'), 4)}")

# ---------------------------------------------------------------- E3-E5: the 7-9 April system
M3, b3 = sub([0, 1, 2], [0, 1, 2])
D3 = det(M3)
x3 = solve(M3, b3)
mins = [det(minor(M3, 0, j)) for j in range(3)]
P(f"E3 det(7-9) = {dec(D3, 6)} = {D3}; first-row minors {[dec(v, 6) for v in mins]}; terms "
  f"{[dec((-1) ** j * M3[0][j] * mins[j], 6) for j in range(3)]}")
cram = [det(with_col(M3, j, b3)) for j in range(3)]
P(f"E4 Cramer numerators {[dec(v, 6) for v in cram]}; x = {[dec(v, 6) for v in x3]}; sum {dec(sum(x3), 6)}")
mins3 = [det(minor(with_col(M3, 2, b3), 0, j)) for j in range(3)]
P(f"   det M_3(b) first-row minors {[dec(v, 6) for v in mins3]}")


def eliminate(m: Mat, b: Vec, pivoting: bool) -> dict:
    """Gaussian elimination on [M | b] (exact). Returns the multipliers, the rows after each step, the pivots,
    the swaps and the back-substituted solution."""
    a = [row[:] + [bi] for row, bi in zip(m, b)]
    n = len(a)
    steps, mult, swaps = [], {}, []
    for k in range(n - 1):
        if pivoting:
            p = max(range(k, n), key=lambda i: abs(a[i][k]))
            if p != k:
                a[k], a[p] = a[p], a[k]
                swaps.append((k, p))
        assert a[k][k] != 0
        for i in range(k + 1, n):
            ell = a[i][k] / a[k][k]
            mult[(i, k)] = ell
            a[i] = [v - ell * w for v, w in zip(a[i], a[k])]
        steps.append([row[:] for row in a])
    piv = [a[k][k] for k in range(n)]
    x = [Fr(0)] * n
    for i in reversed(range(n)):
        x[i] = (a[i][n] - sum((a[i][j] * x[j] for j in range(i + 1, n)), Fr(0))) / a[i][i]
    return {"mult": mult, "steps": steps, "piv": piv, "swaps": swaps, "x": x}


el = eliminate(M3, b3, pivoting=False)
elp = eliminate(M3, b3, pivoting=True)
assert not elp["swaps"] and elp["x"] == el["x"] == x3       # partial pivoting picks the same rows
P("E5 elimination 7-9 Apr: multipliers " + ", ".join(f"l{i + 1}{k + 1}={dec(v, 6)}" for (i, k), v in el["mult"].items()))
for s_, rows in enumerate(el["steps"], 1):
    P(f"   after step {s_}: " + " | ".join("(" + ", ".join(dec(v, 6) for v in r) + ")" for r in rows))
P(f"   pivots {[dec(v, 6) for v in el['piv']]}; product {dec(el['piv'][0] * el['piv'][1] * el['piv'][2], 6)}; x {[dec(v, 6) for v in el['x']]}")

Minv = inverse(M3)
assert matmul(M3, Minv) == [[Fr(int(i == j)) for j in range(3)] for i in range(3)]
P("INVERSE 7-9 Apr rows: " + " | ".join("(" + ", ".join(dec(v, 6) for v in r) + ")" for r in Minv))
P(f"   M^-1 b = {[dec(v, 6) for v in matvec(Minv, b3)]}")
Mf = np.array([[float(v) for v in r] for r in M3])
bf = np.array([float(v) for v in b3])
res_inv = np.abs(Mf @ np.linalg.inv(Mf) - np.eye(3)).max()
gap_solve_inv = np.abs(np.linalg.solve(Mf, bf) - np.linalg.inv(Mf) @ bf).max()
P(f"   float max|M inv(M) - I| = {res_inv:.1e}; max|solve - inv@b| = {gap_solve_inv:.1e} (machine-dependent, not printed)")
assert res_inv < 1e-12 and gap_solve_inv < 1e-12

# ---------------------------------------------------------------- the other triples, the 10 April check
TRIPLES = {"7-8-9": [0, 1, 2], "7-8-10": [0, 1, 3], "7-9-10": [0, 2, 3], "8-9-10": [1, 2, 3]}
tri = {}
for name, rows_ in TRIPLES.items():
    m_, b_ = sub(rows_, [0, 1, 2])
    tri[name] = (det(m_), solve(m_, b_))
    P(f"TRIPLE {name}: det {dec(tri[name][0], 6)}; x {[dec(v, 6) for v in tri[name][1]]}; sum {dec(sum(tri[name][1]), 6)}")
fin = [t[1][1] for t in tri.values()]
P(f"   Financial's multiple from {dec(min(fin), 5)} to {dec(max(fin), 5)}")
pred10 = sum((a * b for a, b in zip(MF[3], x3)), Fr(0))
P(f"   7-9 multiples on 10 Apr: {dec(pred10, 5)} vs TAIEX {dec(BF[3], 2)}; gap {dec(pred10 - BF[3], 5)}")

# ---------------------------------------------------------------- E7, E8: two days and four days
a78, piv78 = rref([r + [bi] for r, bi in zip(*sub([0, 1], [0, 1, 2]))])
assert piv78 == [0, 1]
xp78 = [a78[0][3], a78[1][3], Fr(0)]
xh78 = [-a78[0][2], -a78[1][2], Fr(1)]
P(f"E7 7-8 Apr: x1 = {dec(a78[0][3], 6)} + {dec(-a78[0][2], 6)} x3, x2 = {dec(a78[1][3], 6)} + {dec(-a78[1][2], 6)} x3; "
  f"x_h = {[dec(v, 6) for v in xh78]}")
for name in ("7-8-9", "7-8-10"):
    x_ = tri[name][1]
    assert x_[0] == xp78[0] + x_[2] * xh78[0] and x_[1] == xp78[1] + x_[2] * xh78[1]   # both lie on the 7-8 line
M4b = [r + [bi] for r, bi in zip(MF, BF)]
P(f"E8 four days: rank M {rank(MF)}, rank [M|b] {rank(M4b)}, det [M|b] = {dec(det(M4b), 8)}")

# ---------------------------------------------------------------- E9: the 50/50 mix column on 7-9 April
Mmix = [[r[0], r[1], (r[0] + r[1]) / 2] for r in M3]
P(f"E9 mix column {[dec(r[2], 2) for r in Mmix]}; rank M {rank(Mmix)}, rank [M|b] {rank([r + [bi] for r, bi in zip(Mmix, b3)])}; "
  f"det {det(Mmix)}")
assert matvec(Mmix, [Fr(-1, 2), Fr(-1, 2), Fr(1)]) == [0, 0, 0]
Mmf = np.array([[float(v) for v in r] for r in Mmix])
fdet = float(np.linalg.det(Mmf))
try:
    xs = np.linalg.solve(Mmf, bf)
    big = float(np.abs(xs).max())
    P(f"   float: det {fdet:.2e}, solve returned max |x_j| {big:.2e} (no exception; machine-dependent, not printed)")
    assert big > 1e10
except np.linalg.LinAlgError:
    P(f"   float: det {fdet:.2e}, solve raised LinAlgError (machine-dependent)")
assert abs(fdet) < 1e-10
assert np.linalg.matrix_rank(Mmf) == 2
try:
    np.linalg.solve(np.array([[float(v) for v in r] for r in MF]), np.array([float(v) for v in BF]))
    raise AssertionError("solve accepted a 4 x 3 matrix")
except np.linalg.LinAlgError as e:
    P(f"   solve on four days: LinAlgError: {e}")
    assert str(e) == "Last 2 dimensions of the array must be square"

# ---------------------------------------------------------------- E6: LM7's Sigma (printed values of LM7)
S11, S22, S12 = Fr("0.040425"), Fr("0.018214"), Fr("-0.002866")
E1_, E2_ = Fr("0.22751"), Fr("-0.02547")
Sig = [[S11, S12], [S12, S22]]
dS = det(Sig)
Sinv = inverse(Sig)
fstar = matvec(Sinv, [E1_, E2_])
P(f"E6 LM7 Sigma: det {dec(dS * 10**4, 5)}e-4; inverse ({dec(Sinv[0][0], 4)}, {dec(Sinv[0][1], 4)}; {dec(Sinv[1][0], 4)}, {dec(Sinv[1][1], 4)}); "
  f"f* = ({dec(fstar[0], 4)}, {dec(fstar[1], 4)})")
P(f"   products: s11*s22 = {dec(S11 * S22, 11)}, s12^2 = {dec(S12 * S12, 12)}, det = {dec(dS, 12)}")
Sinv4 = [[Fr(dec(v, 4)) for v in r] for r in Sinv]
f4 = matvec(Sinv4, [E1_, E2_])
P(f"   f* from the printed 4-decimal inverse: ({dec(f4[0], 6)}, {dec(f4[1], 6)}); Sigma times printed inverse: "
  f"{[[dec(v, 6) for v in r] for r in matmul(Sig, Sinv4)]}")

# ---------------------------------------------------------------- Section 7: the common sample (float64)
AGG = ["Electronic", "ChemicalBiotechnologyMedicalCare"]
U28 = [c for c in cl.columns[1:] if c not in ["TAIEX", *AGG]]
ELEC8 = ["Semiconductor", "ComputerPeripheralEquipment", "Optoelectronic", "CommunicationsInternet",
         "ElectronicPartsComponents", "ElectronicProductsDistribution", "InformationService", "OtherElectronic"]
assert len(U28) == 28 and all(e in U28 for e in ELEC8)
cs = cl.filter(pl.col("date") >= pl.lit("2008-12-01")).sort("date")
assert cs.select(pl.all().is_null().any()).row(0) == tuple([False] * cs.width), "a gap in the common sample"
cdates = cs["date"].to_list()
Rt = {c: cs[c].to_numpy()[1:] / cs[c].to_numpy()[:-1] - 1 for c in U28 + ["Electronic", "TAIEX"]}
T = len(Rt["Semiconductor"])
P(f"COMMON SAMPLE: {len(cdates)} dates {cdates[0]}..{cdates[-1]}; T = {T}; first return {cdates[1]}")
RS, RF = Rt["Semiconductor"], Rt["FinancialInsurance"]
reb = 0.5 * RS + 0.5 * RF
PS, PF = cs["Semiconductor"].to_numpy(), cs["FinancialInsurance"].to_numpy()
V = 0.5 * PS / PS[0] + 0.5 * PF / PF[0]
bh = V[1:] / V[:-1] - 1
wS = 0.5 * (PS / PS[0]) / V
r_reb = int(np.linalg.matrix_rank(np.column_stack([RS, RF, reb])))
r_bh = int(np.linalg.matrix_rank(np.column_stack([RS, RF, bh])))
sv_reb = np.linalg.svd(np.column_stack([RS, RF, reb]), compute_uv=False)
sv_bh = np.linalg.svd(np.column_stack([RS, RF, bh]), compute_uv=False)
gap = np.abs(reb - bh)
imax, imin = int(np.argmax(wS)), int(np.argmin(wS))
P(f"   50/50 mixes: matrix_rank rebalanced {r_reb}, buy-and-hold {r_bh}; singular values reb {sv_reb}, bh {sv_bh}")
P(f"   buy-and-hold weight in Semi: start {wS[0]:.4f}, end {wS[-1]:.4f} ({cdates[-1]}); max {wS[imax]:.4f} ({cdates[imax]}); "
  f"min {wS[imin]:.4f} ({cdates[imin]}); largest daily gap {gap.max() * 100:.4f} pp on {cdates[1 + int(np.argmax(gap))]}")
# the buy-and-hold return is the previous day's weights times today's returns: an identity, checked
assert np.allclose(bh, wS[:-1] * RS + (1 - wS[:-1]) * RF, rtol=0, atol=1e-15)
XU = np.column_stack([Rt[c] for c in U28])
XE = np.column_stack([Rt["Electronic"]] + [Rt[c] for c in ELEC8])
r_u28, r_e9 = int(np.linalg.matrix_rank(XU)), int(np.linalg.matrix_rank(XE))
corr_se = float(np.corrcoef(Rt["Semiconductor"], Rt["Electronic"])[0, 1])
P(f"   U28 matrix_rank {r_u28} of {XU.shape}; Electronic + eight: matrix_rank {r_e9} of {XE.shape}; corr(Semi, Electronic) {corr_se:.6f}")
P(f"   max |X x_h| for the rebalanced mix: {np.abs(np.column_stack([RS, RF, reb]) @ np.array([-0.5, -0.5, 1.0])).max():.1e}")

# ---------------------------------------------------------------- Section 3: the cost of Cramer's rule
cost = [(n, math.factorial(n), math.factorial(n + 1), Fr(2, 3) * n**3) for n in range(2, 21)]
P("COST n, n!, (n+1)!, 2n^3/3: " + "; ".join(f"{n}: {a}, {b}, {dec(c, 1)}" for n, a, b, c in cost if n in (2, 3, 4, 5, 10, 20)))

# ---------------------------------------------------------------- knowledge checks and practice problems
# KC Section 4: one elimination step on E1's system
l21_e1 = M1[1][0] / M1[0][0]
row2_e1 = [M1[1][1] - l21_e1 * M1[0][1], b1[1] - l21_e1 * b1[0]]
P(f"KC4 E1 step: l21 = {dec(l21_e1, 6)}; new row 2 (0, {dec(row2_e1[0], 6)} | {dec(row2_e1[1], 6)}); x2 = {dec(row2_e1[1] / row2_e1[0], 6)}; "
  f"det = {dec(M1[0][0] * row2_e1[0], 6)}")
# Problem 4: 7 and 10 April, Semiconductor and Food
M4, b4 = sub([0, 3], [0, 2])
d4 = det(M4)
x4 = solve(M4, b4)
P(f"PP4 (7, 10 Apr; Semi, Food): det {dec(d4, 6)}; numerators {dec(det(with_col(M4, 0, b4)), 6)}, {dec(det(with_col(M4, 1, b4)), 6)}; "
  f"x = ({dec(x4[0], 6)}, {dec(x4[1], 6)}); sum {dec(sum(x4), 6)}")
P(f"   products: -9.95*5.72={dec(Fr('-9.95') * Fr('5.72'), 4)} -8.66*9.91={dec(Fr('-8.66') * Fr('9.91'), 4)} "
  f"-9.70*5.72={dec(Fr('-9.70') * Fr('5.72'), 4)} -8.66*9.25={dec(Fr('-8.66') * Fr('9.25'), 4)} "
  f"-9.95*9.25={dec(Fr('-9.95') * Fr('9.25'), 4)} -9.70*9.91={dec(Fr('-9.70') * Fr('9.91'), 4)}")
# Problem 5: 8-10 April by elimination with partial pivoting
M5, b5 = sub([1, 2, 3], [0, 1, 2])
el5 = eliminate(M5, b5, pivoting=True)
el5n = eliminate(M5, b5, pivoting=False)
P(f"PP5 8-10 Apr, partial pivoting: swaps {el5['swaps']}; multipliers " + ", ".join(f"l{i + 1}{k + 1}={dec(v, 6)}" for (i, k), v in el5["mult"].items()))
for s_, rows in enumerate(el5["steps"], 1):
    P(f"   after step {s_}: " + " | ".join("(" + ", ".join(dec(v, 6) for v in r) + ")" for r in rows))
P(f"   pivots {[dec(v, 6) for v in el5['piv']]}; x {[dec(v, 6) for v in el5['x']]}; det {dec(det(M5), 6)}; "
  f"no-swap pivots {[dec(v, 6) for v in el5n['piv']]}")
# Problem 6: det of the 7-8-10 matrix by cofactors and by pivots (no swaps)
M6, b6 = sub([0, 1, 3], [0, 1, 2])
mins6 = [det(minor(M6, 0, j)) for j in range(3)]
el6 = eliminate(M6, b6, pivoting=False)
P(f"PP6 7-8-10: minors {[dec(v, 6) for v in mins6]}; terms {[dec((-1) ** j * M6[0][j] * mins6[j], 6)  for j in range(3)]}; det {dec(det(M6), 6)}; "
  f"multipliers " + ", ".join(f"l{i + 1}{k + 1}={dec(v, 6)}" for (i, k), v in el6["mult"].items()) +
  f"; pivots {[dec(v, 6) for v in el6['piv']]}; product {dec(el6['piv'][0] * el6['piv'][1] * el6['piv'][2], 6)}")
for s_, rows in enumerate(el6["steps"], 1):
    P(f"   after step {s_}: " + " | ".join("(" + ", ".join(dec(v, 6) for v in r) + ")" for r in rows))
# Problem 7: an integer augmented matrix with a parameter a
for a_ in (Fr(2), Fr(3)):
    aug7 = [[Fr(1), Fr(2), Fr(3), Fr(1)], [Fr(2), Fr(4), Fr(7), Fr(3)], [Fr(1), Fr(2), Fr(4), a_]]
    r7, p7 = rref(aug7)
    P(f"PP7 a={a_}: rank M {rank([r[:3] for r in aug7])}, rank [M|b] {len(p7)}, pivots {p7}, rref {[[str(v) for v in r] for r in r7]}")
assert matvec([[Fr(1), Fr(2), Fr(3)], [Fr(2), Fr(4), Fr(7)], [Fr(1), Fr(2), Fr(4)]], [Fr(-2), Fr(1), Fr(0)]) == [0, 0, 0]
assert matvec([[Fr(1), Fr(2), Fr(3)], [Fr(2), Fr(4), Fr(7)], [Fr(1), Fr(2), Fr(4)]], [Fr(-2), Fr(0), Fr(1)]) == [1, 3, 2]
# Problem 8: discount factors from three illustrative annual-coupon bonds (face 100), by forward substitution
cpn, price = [Fr(2), Fr(3), Fr(4)], [Fr("100.50"), Fr("102.55"), Fr("106.25")]
Mb = [[cpn[i] + (100 if j == i else 0) if j <= i else Fr(0) for j in range(3)] for i in range(3)]
v = []
for i in range(3):
    v.append((price[i] - sum((Mb[i][j] * v[j] for j in range(i)), Fr(0))) / Mb[i][i])
P(f"PP8 bonds: matrix {[[str(x) for x in r] for r in Mb]}; v = {[dec(x, 6) for x in v]}; "
  f"spot rates {[f'{(float(x) ** (-1 / (i + 1)) - 1) * 100:.4f}%' for i, x in enumerate(v)]}")
P(f"   forward substitution from printed v: v2 = (102.55 - 3*{dec(v[0], 6)})/103 = {dec((Fr('102.55') - 3 * Fr(dec(v[0], 6))) / 103, 6)}; "
  f"v3 = (106.25 - 4*{dec(v[0], 6)} - 4*{dec(v[1], 6)})/104 = {dec((Fr('106.25') - 4 * Fr(dec(v[0], 6)) - 4 * Fr(dec(v[1], 6))) / 104, 6)}")
# Problem 9: TX and MTX on two illustrative days (index moves in points), NT$ per contract
moves = [Fr(-300), Fr(150)]
M9 = [[200 * d_, 50 * d_] for d_ in moves]
P(f"PP9 TX/MTX: M = {[[str(x) for x in r] for r in M9]}; det {det(M9)}; rank {rank(M9)}; x_h = (-1/4, 1): {matvec(M9, [Fr(-1, 4), Fr(1)])}")
assert det(M9) == 0 and rank(M9) == 1 and matvec(M9, [Fr(-1, 4), Fr(1)]) == [0, 0]

# TAIEX's 7 April 2025 move is the largest absolute daily move of the whole TAIEX series (2007-07-02 onward)
tx_all = cl["TAIEX"].to_numpy()
r_all = tx_all[1:] / tx_all[:-1] - 1
k_max = int(np.argmax(np.abs(r_all)))
P(f"TAIEX largest |daily return| {dates[0]}..{dates[-1]}: {r_all[k_max]:.6%} on {dates[k_max + 1]}")
assert dates[k_max + 1] == "2025-04-07" and dates[0] == "2007-07-02"


# ==================================================================================================== CHECKS
# Every value below is (1) recomputed from the inputs that src/lm09.md prints next to it, and (2) looked up in the
# text exactly as printed (minus signs and the thousands separator {,} of the formulas normalized).
TXT = TEXT.read_text(encoding="utf-8")
NORM = TXT.replace("−", "-").replace("{,}", ",")
n_checks = 0


def present(printed: str) -> None:
    """The printed string appears in the module, not as part of a longer number."""
    pat = r"(?<![\d.])" + re.escape(printed.replace("−", "-")) + r"(?![\d])"
    assert re.search(pat, NORM), f"not in src/lm09.md: {printed!r}"


def chk(label: str, got: str, printed: str, in_text: bool = True) -> None:
    global n_checks
    n_checks += 1
    ok = got == printed
    if not ok:
        P(f"CHECK {label}: computed {got}, printed {printed} MISMATCH")
    assert ok, (label, got, printed)
    if in_text:
        present(printed)


def d(x: Fr | int, k: int) -> str:
    return dec(x, k)


def F(s: str) -> Fr:
    return Fr(s.replace("−", "-"))


# ---- exhibit days and the case: inputs, rounding, the 7 April context
for s, col_ in zip(SERIES, ("TAIEX", "Semi", "Fin", "Food")):
    for k in range(4):
        chk(f"days {col_} {DAYS[k]}", d(ret[s][k], 2), d(ret[s][k], 2))
chk("TAIEX 7 Apr (case, %)", d(-ret["TAIEX"][0], 2) + "%", "9.70%")
chk("closest tie value", d(tie_gap[0][3], 6), "3.774862")
chk("closest tie distance", d(tie_gap[0][0], 6), "0.000138")
assert tie_gap[0][1:3] == ("Food", "2025-04-08")
chk("case x (3 dec)", ", ".join(d(v, 3) for v in x3), "0.334, 1.447, -0.916", in_text=False)
for v_, s_ in zip(x3, ("0.334", "1.447", "-0.916")):
    present(s_)
chk("case sum of printed 3-dec multiples", d(Fr("0.334") + Fr("1.447") - Fr("0.916"), 3), "0.865")
chk("case sum exact", d(sum(x3), 3), "0.865")
x8910 = tri["8-9-10"][1]
chk("case 8-10 mix", f"({d(x8910[0], 3)},\\,{d(x8910[1], 3)},\\,{d(x8910[2], 3)})", "(-0.018,\\,2.069,\\,-1.376)")
chk("case 10 Apr from the 7-9 mix", "+" + d(pred10, 2) + "%", "+10.17%")
present("+9.25%")
present("-4.02%")
present("-5.79%")
# ---- Example two (E1)
chk("E1 coefficient", d(F("-3.99") * F("5.61") - F("4.47") * F("0.53"), 3), "-24.753")
chk("E1 right side", d(F("-4.02") * F("5.61") - F("5.79") * F("0.53"), 4), "-25.6209")
chk("E1 x1 from printed", d(F("-25.6209") / F("-24.753"), 6), "1.035062")
chk("E1 x2 coefficient", d(F("4.47") * F("0.53") + F("-3.99") * F("-5.61"), 3), "24.753")
chk("E1 x2 right side", d(F("4.47") * F("-4.02") + F("-3.99") * F("-5.79"), 4), "5.1327")
chk("E1 x2 from printed", d(F("5.1327") / F("24.753"), 6), "0.207357")
chk("E1 x exact", f"{d(x1[0], 6)}, {d(x1[1], 6)}", "1.035062, 0.207357", in_text=False)
chk("E1 det", d(d1, 3), "24.753")
chk("E1 x (3 dec)", f"{d(x1[0], 3)} {d(x1[1], 3)}", "1.035 0.207", in_text=False)
present("1.035")
present("0.207")
# ---- Example sliver (E2) and the pitfall
chk("E2 products", f"{d(F('-3.99') * F('-5.61'), 4)} {d(-F('0.53') * F('-4.47'), 4)}", "22.3839 2.3691", in_text=False)
present("22.3839")
present("2.3691")
chk("E2 lengths", f"{norm(col(M1, 0)):.6f} {norm(col(M1, 1)):.6f}", "5.991744 5.634980", in_text=False)
present("5.991744")
present("5.634980")
chk("E2 product of printed lengths", f"{5.991744 * 5.634980:.4f}", "33.7634")
chk("E2 sin from printed", f"{24.753 / 33.7634:.4f}", "0.7331")
chk("E2 angle from printed sin", f"{math.degrees(math.asin(0.7331)):.2f}", "47.15")
chk("E2 angle exact", f"{angle(col(M1, 0), col(M1, 1)):.2f}", "47.15")
chk("E2 sliver products", f"{d(F('-9.95') * F('-4.17'), 4)} {d(F('-8.66') * F('-4.47'), 4)}", "41.4915 38.7102", in_text=False)
present("41.4915")
present("38.7102")
chk("E2 sliver det", d(F("41.4915") - F("38.7102"), 4), "2.7813")
chk("E2 sliver lengths", f"{norm(col(M2, 0)):.6f} {norm(col(M2, 1)):.6f}", "10.907951 9.611686", in_text=False)
present("10.907951")
present("9.611686")
chk("E2 sliver product of printed lengths", f"{10.907951 * 9.611686:.4f}", "104.8438")
chk("E2 sliver sin", f"{2.7813 / 104.8438:.4f}", "0.0265")
chk("E2 sliver angle from printed sin", f"{math.degrees(math.asin(0.0265)):.2f}", "1.52")
chk("E2 sliver angle exact", f"{angle(col(M2, 0), col(M2, 1)):.2f}", "1.52")
num1 = det(with_col(M2, 0, b2))
num2 = det(with_col(M2, 1, b2))
chk("E2 sliver numerators", f"{d(num1, 4)} {d(num2, 4)}", "-9.6924 14.2515", in_text=False)
present("-9.6924")
present("14.2515")
chk("E2 sliver x1", d(F("-9.6924") / F("2.7813"), 2), "-3.48")
chk("E2 sliver x2", d(F("14.2515") / F("2.7813"), 2), "5.12")
chk("E2 sliver x exact", f"{d(x2[0], 2)} {d(x2[1], 2)}", "-3.48 5.12", in_text=False)
chk("area ratio about a ninth", f"{float(d1 / d2):.2f}", "8.90", in_text=False)
chk("pitfall: product of lengths E1", f"{5.991744 * 5.634980:.2f}", "33.76")
chk("pitfall: product of lengths sliver", f"{10.907951 * 9.611686:.2f}", "104.84")
# ---- Example cof (E3)
chk("E3 minor 11", d(F("0.53") * F("-4.17") - F("3.77") * F("-5.61"), 4), "18.9396")
chk("E3 minor 12", d(F("3.99") * F("4.17") + F("3.77") * F("4.47"), 4), "33.4902")
assert [d(v, 4) for v in mins] == ["18.9396", "33.4902", "24.7530"]
terms = [F("-9.95") * F("18.9396"), F("9.89") * F("33.4902"), F("-8.66") * F("24.753")]
chk("E3 terms", " ".join(d(t, 6) for t in terms), "-188.449020 331.218078 -214.360980", in_text=False)
present("-188.44902")
present("331.218078")
present("-214.36098")
chk("E3 det from printed terms", d(sum(terms), 6), "-71.591922")
chk("E3 det exact", d(D3, 6), "-71.591922")
chk("KC swap", "+" + d(-D3, 6), "+71.591922")
# ---- Example cramer (E4) and the cost of Cramer's rule
for j, pr in enumerate(("-23.919201", "-103.581657", "65.586258")):
    chk(f"E4 numerator {j + 1}", d(cram[j], 6), pr)
    chk(f"E4 x{j + 1} from printed", d(F(pr) / F("-71.591922"), 6), d(x3[j], 6))
chk("E4 x", ", ".join(d(v, 6) for v in x3), "0.334105, 1.446834, -0.916113", in_text=False)
present("0.334105,\\ 1.446834,\\ -0.916113")
chk("cost n=3", f"{math.factorial(4)} {Fr(2, 3) * 27}", "24 18", in_text=False)
chk("cost n=20 terms", f"{math.factorial(21):,}", "51,090,942,171,709,440,000")
chk("cost n=20 terms (about)", f"{math.factorial(21):.1e}", "5.1e+19", in_text=False)
present("5.1\\times10^{19}")
chk("cost n=20 operations", f"{2 * 20**3 / 3:,.0f}", "5,333")
chk("KC n=4 products", f"{5 * math.factorial(4)}", "120")
chk("KC n=4 multiplications", f"{5 * math.factorial(4) * 3}", "360")
# ---- Example gauss (E5), exhibit elim, KC of Section 4
L = el["mult"]
chk("E5 l21 from printed", d(F("-3.99") / F("-9.95"), 6), "0.401005")
chk("E5 l31 from printed", d(F("-4.47") / F("-9.95"), 6), "0.449246")
chk("E5 l21 l31 l32 exact", " ".join(d(L[key], 6) for key in ((1, 0), (2, 0), (2, 1))), "0.401005 0.449246 -0.259557", in_text=False)
# l32 from the rounded entries is -0.2595575..., so the text gives the exact value and names the entries in words
assert abs(F("-1.166955") / F("4.495940") - L[(2, 1)]) < Fr(1, 10**6)
present("-0.259557")
step1 = el["steps"][0]
chk("elim row 8 Apr after step 1", " ".join(d(v, 6) for v in step1[1][1:]), "4.495940 7.242704 -0.130251", in_text=False)
chk("elim row 9 Apr after step 1", " ".join(d(v, 6) for v in step1[2][1:]), "-1.166955 -0.279528 -1.432312", in_text=False)
chk("elim row 9 Apr after step 2", " ".join(d(v, 6) for v in el["steps"][1][2][2:]), "1.600370 -1.466119", in_text=False)
for s_ in ("4.495940", "7.242704", "-0.130251", "-1.166955", "-0.279528", "-1.432312", "1.600370", "-1.466119"):
    present(s_)
# a step recomputed from the printed entries: equal, or one unit off in the sixth decimal (the note says so)
r8 = [F("0.53") - F("0.401005") * F("-9.89"), F("3.77") - F("0.401005") * F("-8.66"), F("-4.02") - F("0.401005") * F("-9.70")]
r9 = [F("-5.61") - F("0.449246") * F("-9.89"), F("-4.17") - F("0.449246") * F("-8.66"), F("-5.79") - F("0.449246") * F("-9.70")]
fin3 = [F("-0.279528") - F("-0.259557") * F("7.242704"), F("-1.432312") - F("-0.259557") * F("-0.130251")]
dev_steps = [abs(got_ - F(pr_)) for got_, pr_ in zip(r8 + r9 + fin3, ("4.495940", "7.242704", "-0.130251", "-1.166955", "-0.279528",
                                                                     "-1.432312", "1.600370", "-1.466119"))]
P(f"   elim steps recomputed from the printed entries: largest difference {float(max(dev_steps)):.1e} (sixth decimal)")
assert max(dev_steps) < Fr(5, 10**6)
chk("E5 x3 from printed", d(F("-1.466119") / F("1.600370"), 6), "-0.916113")
bs2 = (F("-0.130251") - F("7.242704") * F("-0.916113")) / F("4.495940")
bs1 = (F("-9.70") + F("9.89") * F("1.446834") + F("8.66") * F("-0.916113")) / F("-9.95")
P(f"   E5 back substitution from the printed entries: x2 {d(bs2, 7)}, x1 {d(bs1, 7)} (exact: {d(x3[1], 7)}, {d(x3[0], 7)})")
assert abs(bs2 - x3[1]) < Fr(2, 10**6) and abs(bs1 - x3[0]) < Fr(2, 10**6)   # the text says the substitution is exact
chk("E5 exact pivots product", d(el["piv"][0] * el["piv"][1] * el["piv"][2], 6), "-71.591922")
chk("KC4 l21", d(F("-4.47") / F("-3.99"), 6), "1.120301")
chk("KC4 row", f"{d(row2_e1[0], 6)} {d(row2_e1[1], 6)}", "-6.203759 -1.286391", in_text=False)
present("-6.203759")
present("-1.286391")
chk("KC4 x2 from printed", d(F("-1.286391") / F("-6.203759"), 6), "0.207357")
chk("KC4 det from printed", d(F("-3.99") * F("-6.203759"), 3), "24.753")
# ---- Section 5: inverse, sensitivity, Example sigma (E6)
chk("inverse column 1 (3 dec)", f"{d(Minv[0][0], 3)} {d(Minv[1][0], 3)}", "-0.265 0.468", in_text=False)
present("0.265")
present("0.468")
chk("8.70% scenario", d(-(BF[0] + 1), 2) + "%", "8.70%")
chk("E6 det", d(F("0.040425") * F("0.018214") - F("-0.002866") ** 2, 12), "0.000728086994", in_text=False)
present("7.28087\\times10^{-4}")
chk("E6 det (5 sig)", f"{float(dS) * 1e4:.5f}", "7.28087", in_text=False)
for (i_, j_), pr in zip(((0, 0), (0, 1), (1, 1)), ("25.0162", "3.9363", "55.5222")):
    chk(f"E6 inverse {i_}{j_}", d(Sinv[i_][j_], 4), pr)
    chk(f"E6 inverse {i_}{j_} from printed det", d([F("0.018214"), F("0.002866"), F("0.040425")][(i_ + j_)] / F("0.000728087"), 4), pr,
        in_text=False)
chk("E6 f1 from printed", d(F("25.0162") * F("0.22751") - F("3.9363") * F("0.02547"), 4), "5.5912")
chk("E6 f2 from printed", d(F("3.9363") * F("0.22751") - F("55.5222") * F("0.02547"), 4), "-0.5186")
chk("E6 f exact", f"{d(fstar[0], 4)} {d(fstar[1], 4)}", "5.5912 -0.5186", in_text=False)
chk("E6 f (2 dec)", f"({d(fstar[0], 2)},\\,{d(fstar[1], 2)})", "(5.59,\\,-0.52)")
dev = max(abs(v - (1 if i == j else 0)) for i, r in enumerate(matmul(Sig, Sinv4)) for j, v in enumerate(r))
P(f"   E6 max |Sigma x printed inverse - I| = {float(dev):.3e}")
assert dev <= Fr(2, 10**6)
present("0.000002")
# ---- Python block of Section 5 and of Section 7: run the code as printed and compare with its comments
blocks = re.findall(r"(?ms)^```python\n(.*?)^```", TXT)
assert len(blocks) == 2, len(blocks)
ns: dict = {}
outs = []
for blk in blocks:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(blk, "src/lm09.md", "exec"), ns)  # noqa: S102 - the module's own code blocks
    outs.append(buf.getvalue().splitlines())
P(f"   code block outputs: {outs[0][:2]} | {outs[1]}")
chk("code 1 line 1", outs[0][0], "[ 0.334105  1.446834 -0.916113]")
chk("code 1 line 2", outs[0][1], "-71.591922")
chk("code 2", " | ".join(outs[1]), "2 | True | 3 4", in_text=False)
for blk in blocks:
    assert all(len(line) <= 80 for line in blk.splitlines()), "a code line is longer than 80 characters"
# ---- Section 6: E7, wline, E8, the triples
chk("E7 line", f"{d(a78[0][3], 6)} {d(-a78[0][2], 6)} {d(a78[1][3], 6)} {d(-a78[1][2], 6)}", "1.003671 0.730877 -0.028971 -1.610943",
    in_text=False)
for s_ in ("1.003671", "0.730877", "-0.028971", "-1.610943"):
    present(s_)
chk("E7/wline x3 with 9 Apr", d(x3[2], 6), "-0.916113")
chk("wline x3 with 10 Apr", d(tri["7-8-10"][1][2], 6), "0.900269")
chk("E8 det [M|b]", d(det(M4b), 6), "65.603260")
assert rank(MF) == 3 and rank(M4b) == 4
fin_rng = [t[1][1] for t in tri.values()]
chk("triples Financial min", d(min(fin_rng), 3), "-1.479")
chk("triples Financial max", d(max(fin_rng), 3), "2.069")
assert tri["7-8-10"][1][1] == min(fin_rng) and tri["8-9-10"][1][1] == max(fin_rng)
chk("10 Apr from printed mix", d(F("9.91") * F("0.334105") + F("8.36") * F("1.446834") + F("5.72") * F("-0.916113"), 2), "10.17")
for name, pr in (("7-8-9", "-71.591922"), ("7-8-10", "22.568247"), ("7-9-10", "-29.587887"), ("8-9-10", "49.300524")):
    chk(f"triple det {name}", d(tri[name][0], 6), pr)
# ---- Section 7: the common sample, the mixes, Electronic; Example mix (E9)
chk("T", f"{T:,}", "4,382")
assert cdates[0] == "2008-12-01" and cdates[1] == "2008-12-02" and cdates[-1] == "2026-10-08"
chk("ranks of the two mixes", f"{r_reb} {r_bh}", "2 3", in_text=False)
chk("bh weight end", f"{wS[-1]:.3f}", "0.858")
chk("bh weight min", f"{wS[imin]:.3f} {cdates[imin]}", "0.457 2011-08-04", in_text=False)
chk("bh weight max", f"{wS[imax]:.3f} {cdates[imax]}", "0.883 2026-05-25", in_text=False)
present("0.457")
present("0.883")
chk("largest daily gap", f"{gap.max() * 100:.2f}", "2.57")
chk("Electronic + eight rank", f"{r_e9} {XE.shape}", "9 (4382, 9)", in_text=False)
chk("corr Semi Electronic", f"{corr_se:.6f}", "0.952591")
chk("U28 rank", f"{r_u28}", "28")
chk("E9 mix column", " ".join(d(r[2], 2) for r in Mmix), "-9.92 -1.73 -5.04", in_text=False)
present("-9.92,\\,-1.73,\\,-5.04")
chk("E9 E1 mix on 7 Apr (from printed)", d(F("-9.95") * F("1.035062") + F("-9.89") * F("0.207357"), 2), "-12.35")
chk("E9 E1 mix on 7 Apr (exact)", d(MF[0][0] * x1[0] + MF[0][1] * x1[1], 2), "-12.35", in_text=False)
# ---- Solutions
chk("S1", d(-2 * D3, 6), "143.183844")
chk("S4 det products", f"{d(F('-9.95') * F('5.72'), 3)} {d(-F('-8.66') * F('9.91'), 4)}", "-56.914 85.8206", in_text=False)
present("-56.914")
present("85.8206")
chk("S4 det", d(d4, 4), "28.9066")
chk("S4 numerator 1", d(F("-9.70") * F("5.72") - F("-8.66") * F("9.25"), 3), "24.621")
chk("S4 numerator 2", d(F("-9.95") * F("9.25") - F("-9.70") * F("9.91"), 4), "4.0895")
chk("S4 x1", d(F("24.621") / F("28.9066"), 5), "0.85174")
chk("S4 x2", d(F("4.0895") / F("28.9066"), 5), "0.14147")
chk("S4 x exact", f"{d(x4[0], 5)} {d(x4[1], 5)}", "0.85174 0.14147", in_text=False)
chk("S4 sum (printed parts and exact agree at 3 decimals)", f"{d(F('0.85174') + F('0.14147'), 3)} {d(sum(x4), 3)}", "0.993 0.993", in_text=False)
present("0.993")
L5 = el5["mult"]
chk("S5 l21 l31", f"{d(F('-4.47') / F('9.91'), 6)} {d(F('-3.99') / F('9.91'), 6)}", "-0.451060 -0.402624", in_text=False)
present("-0.451060")
present("-0.402624")
assert [d(L5[(1, 0)], 6), d(L5[(2, 0)], 6), d(L5[(2, 1)], 6)] == ["-0.451060", "-0.402624", "-0.472067"]
chk("S5 column-2 entries", f"{d(el5['steps'][0][2][1], 6)} {d(el5['steps'][0][1][1], 6)}", "3.895933 -1.839142", in_text=False)
present("3.895933")
present("-1.839142")
chk("S5 l32 from printed", d(F("-1.839142") / F("3.895933"), 6), "-0.472067")
chk("S5 pivots", " ".join(d(v, 6) for v in el5["piv"]), "9.910000 3.895933 1.276928", in_text=False)
present("1.276928")
chk("S5 x", ", ".join(d(v, 6) for v in el5["x"]), "-0.017926, 2.069318, -1.376197", in_text=False)
present("-0.017926,\\,2.069318,\\,-1.376197")
assert len(el5["swaps"]) == 2
chk("S5 det", d(det(M5), 6), "49.300524")
chk("S6 minors", " ".join(d(v, 4) for v in mins6), "-28.4856 -60.1835 -38.6087", in_text=False)
for s_ in ("-28.4856", "-60.1835", "-38.6087"):
    present(s_)
t6 = [F("-9.95") * F("-28.4856"), F("9.89") * F("-60.1835"), F("-8.66") * F("-38.6087")]
chk("S6 terms", " ".join(d(t, 6) for t in t6), "283.431720 -595.214815 334.351342", in_text=False)
present("283.43172")
present("-595.214815")
present("334.351342")
chk("S6 det from printed terms", d(sum(t6), 6), "22.568247")
row10 = el6["steps"][0][2]
chk("S6 10 Apr row after step 1", f"{d(row10[1], 6)} {d(row10[2], 6)}", "-1.490241 -2.905186", in_text=False)
present("-1.490241")
present("-2.905186")
chk("S6 l32", d(el6["mult"][(2, 1)], 6), "-0.331464")
chk("S6 l32 from printed", d(F("-1.490241") / F("4.495940"), 6), "-0.331464", in_text=False)
chk("S6 d3", d(el6["piv"][2], 6), "-0.504492")
chk("S6 exact pivots product", d(el6["piv"][0] * el6["piv"][1] * el6["piv"][2], 6), "22.568247")
chk("S8 v1", d(F("100.50") / 102, 6), "0.985294")
chk("S8 v2 from printed v1", d((F("102.55") - 3 * F("0.985294")) / 103, 6), "0.966933")
chk("S8 v3 from printed v1, v2", d((F("106.25") - 4 * F("0.985294") - 4 * F("0.966933")) / 104, 6), "0.946549")
chk("S8 exact v", " ".join(d(x, 6) for x in v), "0.985294 0.966933 0.946549", in_text=False)
spot = [(0.985294 ** (-1 / (i + 1)) - 1) for i in range(1)] + [0.966933 ** (-1 / 2) - 1, 0.946549 ** (-1 / 3) - 1]
chk("S8 spot rates from printed v", " ".join(f"{z:.4%}" for z in spot), "1.4925% 1.6955% 1.8480%", in_text=False)
spot_ex = [float(x) ** (-1 / (i + 1)) - 1 for i, x in enumerate(v)]
chk("S8 spot rates exact", " ".join(f"{z:.4%}" for z in spot_ex), "1.4925% 1.6955% 1.8480%", in_text=False)
for s_ in ("1.4925%", "1.6955%", "1.8480%"):
    present(s_)
chk("S9 matrix", " ".join(f"{int(x):,}" for r in M9 for x in r), "-60,000 -15,000 30,000 7,500", in_text=False)
present("-60,000")
present("7,500")
chk("S9 determinant terms", f"{int(M9[0][0] * M9[1][1]):,} +{int(-M9[0][1] * M9[1][0]):,}", "-450,000,000 +450,000,000", in_text=False)
present("-450,000,000+450,000,000=0")
P(f"\nall {n_checks} checks passed: every printed value follows from its printed inputs and appears in src/lm09.md")
