"""Every number that LM16 (Joint Distributions and Dependence) prints, computed and checked against src/lm16.md.

Run:  uv run python data/lm16_numbers.py      (after data/vol2_series.py has written processed/vol2_closes.parquet)

Inputs: data/processed/vol2_closes.parquet and data/processed/vol2_repairs.json (Volume II's U28 sample, closes
repaired from the 13:30:00 values by data/vol2_series.py), loaded as data/lm10_series.py does; src/lm16.md (the text
the checks compare against); src/lm07.md, src/lm10.md, src/lm11.md and src/lm12.md (figures LM16 quotes as those
modules printed them); plans/vol-3-anchors.md (the editor's anchors, compared, not forced). LM16 reads no TR23 data
and draws no random numbers.

Sample: U28, closes 2008-12-01 .. 2026-10-08, simple price returns between consecutive rows, T = 4,382 (first return
2008-12-02). Moments divide by T (a bin's by its days). Counts against an edge use the guard (<= -x + 1e-12,
>= x - 1e-12; "inside" d^2 <= k^2 + 1e-12) and are recounted exactly with Fraction on the two-decimal closes.

Checks:
  * chk(label, value, fmt, printed): format(value, fmt) equals the printed string, the value does not sit on a
    rounding tie of fmt, and the string appears in src/lm16.md as a whole number (after replacing the Unicode minus by
    '-', '{,}' by ',' and '\\%' by '%');
  * same(label, got, printed) and has(label, text): a string computed another way, or a phrase, appears in the text;
  * hand examples are recomputed from the inputs printed beside them (PITFALLS section 7);
  * anchor(id, got): the value is compared with plans/vol-3-anchors.md; a difference prints DIFFERS and is listed at
    the end, without failing the run.
"""
import json
import math
import re
import sys
from fractions import Fraction
from itertools import pairwise
from pathlib import Path

import numpy as np
import polars as pl
from numpy.typing import NDArray
from scipy import integrate, special, stats
from scipy.linalg import solve_triangular

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lm10_series import u28

Vec = NDArray[np.float64]
ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
FIRST, LAST = "2008-12-01", "2026-10-08"
S5 = ["Semiconductor", "FinancialInsurance", "Food", "Plastics", "ShippingTransportation"]
EPS = 1e-12


def norm(s: str) -> str:
    return s.replace("{,}", ",").replace("−", "-").replace("\\%", "%")


NORM = norm((ROOT / "src" / "lm16.md").read_text(encoding="utf-8"))
N_CHECKS = 0
ANCHOR_DIFFS: list[str] = []


def in_text(printed: str) -> bool:
    """The printed number appears as a whole number (not inside a longer one: 2.323 is not in 2.3235)."""
    return re.search(r"(?<![\d.])" + re.escape(printed) + r"(?!\d)", NORM) is not None


def tie(value: float, fmt: str) -> bool:
    """True when value lies on a rounding boundary of fmt (a reader rounding by hand could go either way)."""
    m = re.search(r"\.(\d+)", fmt)
    d = int(m.group(1)) if m else 0
    scaled = abs(value) * 10**d
    return abs(scaled - math.floor(scaled) - 0.5) < 1e-6


def chk(label: str, value: float, fmt: str, printed: str) -> None:
    global N_CHECKS
    got = format(value, fmt)
    print(f"CHECK {label}: {got} (printed {printed}) {'ok' if got == printed else 'MISMATCH'}")
    assert got == printed, (label, got, printed)
    assert not tie(value, fmt), ("rounding tie: print more digits", label, value)
    assert in_text(printed), f"{label}: {printed!r} not found in src/lm16.md"
    N_CHECKS += 1


def same(label: str, got: str, printed: str) -> None:
    global N_CHECKS
    print(f"CHECK {label}: {got} (printed {printed}) {'ok' if got == printed else 'MISMATCH'}")
    assert got == printed, (label, got, printed)
    assert printed in NORM, f"{label}: {printed!r} not found in src/lm16.md"
    N_CHECKS += 1


def has(label: str, text: str) -> None:
    global N_CHECKS
    assert norm(text) in NORM, f"{label}: {text!r} not found in src/lm16.md"
    print(f"CHECK {label}: '{text}' in text ok")
    N_CHECKS += 1


def sci(x: float, d: int) -> str:
    """LaTeX scientific notation as printed: 9.4\\times10^{-18} (d decimals in the mantissa)."""
    m, e = f"{x:.{d}e}".split("e")
    return f"{m}\\times10^{{{int(e)}}}"


def g(x: float, d: int = 10) -> str:
    """As the anchors script prints an unrounded value: d significant digits."""
    return f"{x:.{d}g}"


ANCH: dict[str, str] = {}
_sec = (ROOT / "plans" / "vol-3-anchors.md").read_text(encoding="utf-8").split("## LM16", 1)[1].split("## LM17", 1)[0]
for line in _sec.splitlines():
    if line.startswith("| A16-"):
        cells = line.split("|")
        ANCH[cells[1].strip()] = cells[-3].strip()
assert len(ANCH) == 80, len(ANCH)


def anchor(aid: str, got: str) -> None:
    """Compare with plans/vol-3-anchors.md; a difference is reported, not forced."""
    exp = ANCH[aid]
    tag = "ok" if got == exp else "DIFFERS"
    print(f"ANCHOR {aid}: {got} (anchor {exp}) {tag}")
    if got != exp:
        ANCHOR_DIFFS.append(f"{aid}: script {got}, anchor {exp}")


def corr(u: Vec, v: Vec) -> float:
    uc, vc = u - u.mean(), v - v.mean()
    return float(uc @ vc / math.sqrt(float((uc @ uc) * (vc @ vc))))


def cov0(x: Vec) -> Vec:
    xc = x - x.mean(axis=0)
    return xc.T @ xc / x.shape[0]


def mahal(x: Vec) -> Vec:
    """d_t^2 of every row with the sample's means and divisor-T covariance matrix, by Cholesky ((12.9))."""
    lo = np.linalg.cholesky(cov0(x))
    z = solve_triangular(lo, (x - x.mean(axis=0)).T, lower=True)
    return (z**2).sum(axis=0)


def outside(d: Vec, c: float) -> int:
    return int((~(d <= c + EPS)).sum())


def exact_returns(p: list[float]) -> list[Fraction]:
    q = [Fraction(str(v)) for v in p]
    return [b / a - 1 for a, b in pairwise(q)]


# ============================================================ sample
smp_ = u28()
cl = pl.read_parquet(PROC / "vol2_closes.parquet").sort("date").filter(pl.col("date").is_between(pl.lit(FIRST), pl.lit(LAST)))
names = smp_.names
X = smp_.X
RT = np.asarray(smp_.taiex, dtype=np.float64)
dates = smp_.dates
cd = smp_.close_dates
T = X.shape[0]
assert np.allclose(X, np.asarray(cl.select(names).to_numpy(), dtype=np.float64)[1:] / np.asarray(cl.select(names).to_numpy(), dtype=np.float64)[:-1] - 1, rtol=0, atol=0)
days = round(smp_.years * 365.25)
A = smp_.A
col = {c: i for i, c in enumerate(names)}
x1, x2 = X[:, col["Semiconductor"]], X[:, col["FinancialInsurance"]]
i7 = dates.index("2025-04-07")
assert T == 4382 and dates[0] == "2008-12-02" and dates[-1] == "2026-10-08" and days == 6520
anchor("A16-01", f"{T}; {dates[0]}; {dates[-1]}")
anchor("A16-02", f"{days}; {g(smp_.years, 12)}")
anchor("A16-03", g(A, 12))
chk("T", T, ",", "4,382")
has("first return", "2 December 2008")
has("last return", "8 October 2026")
chk("A", A, ".2f", "245.48")

rep = json.loads((PROC / "vol2_repairs.json").read_text(encoding="utf-8"))["repairs"]
inside_ = [r for r in rep if r["series"] in names and FIRST <= r["date"] <= LAST]
anchor("A16-04", f"{len(inside_)}; {len({r['date'] for r in inside_})}")
chk("repaired closes", len(inside_), "d", "524")
chk("their dates", len({r["date"] for r in inside_}), "d", "38")
key_dates = ["2025-04-07", "2025-04-08", "2025-04-09", "2025-04-10", "2024-08-05", "2009-05-05"]
touched = {r["date"] for r in rep if r["series"] in [*names, "TAIEX"]}
hits = sum(1 for d in key_dates for dd in (d, cd[cd.index(d) - 1]) if dd in touched)
anchor("A16-05", str(hits))
assert hits == 0
has("no repair on the case's dates", "none on these dates or the dates before them")

# ============================================================ the pair: moments and the case
m1, m2 = float(x1.mean()), float(x2.mean())
s1, s2 = float(x1.std()), float(x2.std())
c12 = float(((x1 - m1) * (x2 - m2)).mean())
rho = c12 / (s1 * s2)
anchor("A16-06", g(rho))
anchor("A16-33", f"{g(100 * m1)}; {g(100 * m2)}")
anchor("A16-53", f"{g(100 * s1)}; {g(100 * s2)}")
chk("rho of the pair", rho, ".4f", "0.5749")
chk("Semiconductor mean, %", 100 * m1, ".4f", "0.0947")
chk("FinancialInsurance mean, %", 100 * m2, ".4f", "0.0494")
chk("Semiconductor SD, %", 100 * s1, ".4f", "1.5243")
chk("FinancialInsurance SD, %", 100 * s2, ".4f", "1.2173")
r1p = np.array([-9.95, -3.99, -4.47])                 # LM10's printed returns (lm10.md, example "byhand")
r2p = np.array([-9.89, 0.53, -5.61])
lm10 = norm((ROOT / "src" / "lm10.md").read_text(encoding="utf-8"))
assert all(s in lm10 for s in ("| 7 Apr | -9.95 | -9.89 |", "| 8 Apr | -3.99 | +0.53 |", "| 9 Apr | -4.47 | -5.61 |", "=0.851"))
rho3 = corr(r1p, r2p)
rho3u = corr(x1[i7:i7 + 3], x2[i7:i7 + 3])
anchor("A16-07", g(rho3))
anchor("A16-76", g(rho3u))
chk("three-day correlation from LM10's printed returns", rho3, ".3f", "0.851")
chk("three-day correlation, unrounded returns", rho3u, ".3f", "0.850")
anchor("A16-08", f"{g(100 * x1[i7])}; {g(100 * x2[i7])}")
chk("7 April Semiconductor", 100 * x1[i7], ".2f", "-9.95")
chk("7 April FinancialInsurance", 100 * x2[i7], ".2f", "-9.89")
assert -0.10 < x1[i7] < -0.0985 and -0.10 < x2[i7] < -0.0985        # -9.9529% and -9.8894%: both just short of 10%
has("nearly 10%", "both fell nearly 10%")

XP = np.column_stack([x1, x2])
d2 = mahal(XP)
assert abs(d2.mean() - 2) < 1e-9
rank7 = int((d2 > d2[i7]).sum()) + 1
anchor("A16-09", f"{g(float(d2[i7]))}; {rank7}")
chk("pair d^2 on 7 April", float(d2[i7]), ".2f", "72.05")
assert rank7 == 1
has("rank 1", "72.05 (1st)")
n9 = outside(d2, 9.0)
anchor("A16-10", str(n9))
chk("days with d^2 > 9", n9, "d", "177")
p9 = math.exp(-4.5)
anchor("A16-23", g(p9))
anchor("A16-11", f"{g(T * p9)}; {g(T * p9 * (1 - p9))}; {g(math.sqrt(T * p9 * (1 - p9)))}")
chk("p = e^-4.5", p9, ".6f", "0.011109")
chk("p in %", 100 * p9, ".2f", "1.11")
chk("expected days", T * p9, ".2f", "48.68")
chk("expected days, one decimal", T * p9, ".1f", "48.7")
chk("expected days, about", T * p9, ".0f", "49")
chk("variance of the count", T * p9 * (1 - p9), ".2f", "48.14")
chk("SD of the count", math.sqrt(T * p9 * (1 - p9)), ".2f", "6.94")
chk("mean from printed p", 4382 * 0.011109, ".2f", "48.68")
chk("variance from printed mean and p", 48.68 * (1 - 0.011109), ".2f", "48.14")
chk("SD from printed variance", math.sqrt(48.14), ".2f", "6.94")
assert abs(float(stats.chi2.sf(9, 2)) - p9) < 1e-15

# ============================================================ Section 2: the joint pmf of the bins


def bins(r: Vec) -> NDArray[np.int64]:
    return np.where(r <= -0.01 + EPS, 0, np.where(r >= 0.01 - EPS, 2, 1))


b1, b2 = bins(x1), bins(x2)
tab = np.zeros((3, 3), dtype=int)
np.add.at(tab, (b1, b2), 1)
e1 = exact_returns(cl["Semiconductor"].to_list())
e2 = exact_returns(cl["FinancialInsurance"].to_list())
one = Fraction(1, 100)
tabF = np.zeros((3, 3), dtype=int)
for u_, v_ in zip(e1, e2, strict=True):
    tabF[0 if u_ <= -one else (2 if u_ >= one else 1), 0 if v_ <= -one else (2 if v_ >= one else 1)] += 1
assert (tab == tabF).all()
ties1 = sum(1 for q in [*e1, *e2] if q in (one, -one))
anchor("A16-26", str(ties1))
assert ties1 == 0
has("no exact 1% return", "No return of either sector is exactly ±1%")
anchor("A16-24", " / ".join(", ".join(str(int(c)) for c in row) for row in tab))
rows, cols = tab.sum(axis=1), tab.sum(axis=0)
anchor("A16-25", f"{', '.join(str(int(c)) for c in rows)}; {', '.join(str(int(c)) for c in cols)}")
for lab, r in zip(("$R\\le-1\\%$", "between", "$R\\ge1\\%$"), range(3), strict=True):
    has(f"X2 row {r}", f"| {lab} | {tab[r, 0]:,} | {tab[r, 1]:,} | {tab[r, 2]:,} | {rows[r]:,} |")
has("X2 totals", f"| Total | {cols[0]:,} | {cols[1]:,} | {cols[2]:,} | {T:,} |")
n_ll, n_r0, n_c0 = int(tab[0, 0]), int(rows[0]), int(cols[0])
anchor("A16-47", f"{g(n_ll / T)}; {g(n_r0 / T)}; {g(n_c0 / T)}; {g(n_r0 / T * n_c0 / T)}; "
       f"{g((n_ll / T) / (n_r0 / T * n_c0 / T))}; {g(0.0792 / 0.0241)}")
chk("E1 joint", n_ll / T, ".4f", "0.0792")
chk("E1 margin X", n_r0 / T, ".4f", "0.1960")
chk("E1 margin Y", n_c0 / T, ".4f", "0.1228")
chk("E1 product, unrounded", n_r0 / T * n_c0 / T, ".4f", "0.0241")
chk("E1 product from printed margins", 0.1960 * 0.1228, ".4f", "0.0241")
chk("E1 ratio from printed values", 0.0792 / 0.0241, ".2f", "3.29")
chk("E1 ratio, unrounded", (n_ll / T) / (n_r0 / T * n_c0 / T), ".2f", "3.29")
anchor("A16-48", f"{g(347 / 859)}; {g(20 / 1004)}")
chk("E1 conditional after a fall", n_ll / n_r0, ".3f", "0.404")
chk("E1 conditional after a rise", int(tab[2, 0]) / int(rows[2]), ".4f", "0.0199")
chk("overview: 40.4%", 100 * n_ll / n_r0, ".1f", "40.4")
chk("overview: 12.28%", 100 * n_c0 / T, ".2f", "12.28")
anchor("A16-17", g(20 / 538))
chk("KC section 2", int(tab[2, 0]) / n_c0, ".4f", "0.0372")
anchor("A16-60", f"{g(347 / 538)}; {g(347 / T)}")
chk("P1 C", n_ll / n_c0, ".3f", "0.645")
chk("P1 A", n_ll / T, ".3f", "0.079")

# E2: f(x, y) = x + y on the unit square, exact


def sq(a: int, b: int, top: Fraction = Fraction(1)) -> Fraction:
    """Integral of x^a y^b over [0, top]^2."""
    return top ** (a + 1) / (a + 1) * top ** (b + 1) / (b + 1)


F = Fraction
half = F(1, 2)
EX, EX2, EXY = sq(2, 0) + sq(1, 1), sq(3, 0) + sq(2, 1), sq(2, 1) + sq(1, 2)
VX, CXY = EX2 - EX**2, EXY - EX * EX
anchor("A16-49", "; ".join([str(sq(1, 0) + sq(0, 1)), str(EX), str(EX2), str(VX), str(EXY), str(CXY), g(float(CXY)),
                            str(CXY / VX), g(float(CXY / VX)), str(sq(1, 0, half) + sq(0, 1, half)), "2/3", "5/9"]))
assert sq(1, 0) + sq(0, 1) == 1 and EX == F(7, 12) and EXY == F(1, 3) and VX == F(11, 144) and CXY == F(-1, 144)
assert CXY / VX == F(-1, 11) and EX**2 == F(49, 144)
assert sq(1, 0, half) + sq(0, 1, half) == F(1, 8) and F(1, 2) * F(1, 2) ** 2 / 2 + F(1, 8) * F(1, 2) == F(1, 8)
assert F(1, 16) + F(1, 16) == F(1, 8)
for frag in ("\\tfrac7{12}", "\\tfrac13", "\\tfrac{49}{144}", "\\tfrac1{144}", "\\tfrac{11}{144}", "\\tfrac1{11}",
             "\\tfrac1{16}+\\tfrac1{16}=\\tfrac18", "\\tfrac23(1+y)", "\\frac{3x+2}{6x+3}"):
    has(f"E2 {frag}", frag)
chk("P2 covariance", float(CXY), ".4f", "-0.0069")
chk("P2 correlation", float(CXY / VX), ".4f", "-0.0909")
chk("P2 distractor B", float(EXY), ".4f", "0.3333")


def cond_mean(x: Fraction) -> Fraction:
    """E[Y | X = x] = (x/2 + 1/3) / (x + 1/2)."""
    return (x / 2 + F(1, 3)) / (x + half)


assert all(cond_mean(F(k, 7)) == (3 * F(k, 7) + 2) / (6 * F(k, 7) + 3) for k in range(8))
assert cond_mean(F(0)) == F(2, 3) and cond_mean(F(1)) == F(5, 9)
has("E2 conditional mean values", "The conditional mean falls from 2/3 at $x=0$ to 5/9 at $x=1$.")

# E3
xs = [F(-1), F(0), F(1)]
cov3 = sum(x**3 for x in xs) / 3 - sum(xs, F(0)) / 3 * sum(x**2 for x in xs) / 3
anchor("A16-50", f"{cov3}; {F(1, 3)}")
assert cov3 == 0 and sum(x**2 for x in xs) / 3 == F(2, 3)

# ============================================================ Section 3: E4, X3 (TAIEX price index, U28 dates)
a_, b_ = RT[:-1], RT[1:]
anchor("A16-27", f"{T - 1}; {g(corr(a_, b_))}; {g(corr(np.abs(a_), np.abs(b_)))}")
chk("pairs", T - 1, ",", "4,381")
chk("E4 corr of returns", corr(a_, b_), ".3f", "0.040")
chk("E4 corr of sizes", corr(np.abs(a_), np.abs(b_)), ".3f", "0.183")
big = np.abs(a_) >= 0.02 - EPS
eT = exact_returns(cl["TAIEX"].to_list())
assert int(big.sum()) == sum(1 for q in eT[:-1] if abs(q) >= F(2, 100))
anchor("A16-28", f"{int(big.sum())}; {g(100 * float(np.abs(b_[big]).mean()))}; "
       f"{g(100 * float(np.abs(b_[~big]).mean()))}; {g(100 * float(np.abs(b_).mean()))}")
chk("big days", int(big.sum()), "d", "306")
chk("size after big days", 100 * float(np.abs(b_[big]).mean()), ".2f", "1.28")
chk("size after the others", 100 * float(np.abs(b_[~big]).mean()), ".2f", "0.75")
chk("size overall", 100 * float(np.abs(b_).mean()), ".2f", "0.79")
edges = [-np.inf, -0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03, np.inf]
cnt, mx, my, mabs = [], [], [], []
for lo, hi in pairwise(edges):
    m_ = (a_ > lo + EPS) & (a_ <= hi + EPS)
    lo_f = None if lo == -np.inf else F(str(lo))
    hi_f = None if hi == np.inf else F(str(hi))
    assert int(m_.sum()) == sum(1 for q in eT[:-1] if (lo_f is None or q > lo_f) and (hi_f is None or q <= hi_f))
    cnt.append(str(int(m_.sum())))
    mx.append(f"{100 * a_[m_].mean():.4f}")
    my.append(f"{100 * b_[m_].mean():.4f}")
    mabs.append(f"{100 * np.abs(b_[m_]).mean():.4f}")
anchor("A16-29", f"{', '.join(cnt)}; {', '.join(mx)}; {', '.join(my)}; {', '.join(mabs)}")
chk("X3 lowest bin days", int(cnt[0]), "d", "60")
chk("X3 highest bin days", int(cnt[-1]), "d", "39")

lm07 = norm((ROOT / "src" / "lm07.md").read_text(encoding="utf-8"))
assert "fell by about 21–22% while their daily correlation was -0.06" in lm07
anchor("A16-77", "21-22%; -0.06 (printed in lm07.md:418)")
has("2022 joint loss", "both fell about 21–22% while their daily correlation was −0.06")

# ============================================================ Section 4
a11, a12, a22 = 570.34, 261.83, 363.73
assert "570.34&261.83&162.26" in lm10 and "363.73" in lm10 and "=410.41$, or 20.26%" in lm10
anchor("A16-51", "570.34; 261.83; 363.73 (printed in lm10.md:61)")
vp = 0.25 * a11 + 0.5 * a12 + 0.25 * a22
anchor("A16-52", f"{g(vp)}; {g(math.sqrt(vp))}; {g(0.5 * a11 + 0.5 * a12)}; {g(a11 + a22 - 2 * a12)}; "
       f"{g(math.sqrt(a11 + a22 - 2 * a12))}")
chk("E5 sigma_p^2", vp, ".2f", "364.43")
chk("E5 sigma_p", math.sqrt(vp), ".2f", "19.09")
chk("E5 sigma_p from printed variance", math.sqrt(364.43), ".2f", "19.09")
assert F("0.5") * F("570.34") + F("0.5") * F("261.83") == F("416.085")
chk("E5 Cov(R1, Rp), exact", 0.5 * a11 + 0.5 * a12, ".3f", "416.085")
chk("E5 Var(R1 - R2)", a11 + a22 - 2 * a12, ".2f", "410.41")
chk("E5 its volatility", math.sqrt(a11 + a22 - 2 * a12), ".2f", "20.26")
chk("pitfall: sqrt(570.34)", math.sqrt(a11), ".2f", "23.88")
chk("pitfall: sqrt(363.73)", math.sqrt(a22), ".2f", "19.07")
chk("pitfall: difference of printed volatilities", 23.88 - 19.07, ".2f", "4.81")
chk("pitfall: root of the summed variances", math.sqrt(a11 + a22), ".2f", "30.56")
has("pitfall formulas", "23.88 − 19.07 = 4.81 points nor √(570.34 + 363.73) = 30.56%")
r_log = np.log1p(RT)
anchor("A16-12", f"{g(100 * float(r_log.mean()))}; {g(100 * float(r_log.std()))}")
chk("rbar, %", 100 * float(r_log.mean()), ".5f", "0.05454")
chk("s_r, %", 100 * float(r_log.std()), ".4f", "1.1392")
m_days = round(A)
anchor("A16-13", str(m_days))
chk("m", m_days, "d", "245")
anchor("A16-14", f"{g(m_days * 100 * float(r_log.mean()))}; {g(math.sqrt(m_days) * 100 * float(r_log.std()))}; "
       f"{g(m_days * 0.05454)}; {g(math.sqrt(m_days) * 1.1392)}")
chk("year mean from printed inputs", 245 * 0.05454, ".2f", "13.36")
chk("year mean, unrounded", m_days * 100 * float(r_log.mean()), ".2f", "13.36")
chk("year SD from printed inputs", math.sqrt(245) * 1.1392, ".2f", "17.83")
chk("year SD, unrounded", math.sqrt(m_days) * 100 * float(r_log.std()), ".2f", "17.83")
has("year formulas", "mean 245 × 0.05454% = 13.36% and standard deviation √245 × 1.1392% = 17.83%")
anchor("A16-18", f"{4 + 9}; {g(4 / math.sqrt(4 * 13))}")
chk("KC section 4", 2 / math.sqrt(13), ".3f", "0.555")

# ============================================================ Section 5: X4, E6, the tower property
gm, gs, gn = [], [], []
within = between = 0.0
for k_ in range(3):
    sel = b1 == k_
    w_ = float(sel.mean())
    gn.append(int(sel.sum()))
    gm.append(float(x2[sel].mean()))
    gs.append(float(x2[sel].std()))
    within += w_ * float(x2[sel].var())
    between += w_ * (float(x2[sel].mean()) - m2) ** 2
assert abs(within + between - float(x2.var())) < 1e-15 and gn == [859, 2519, 1004]
anchor("A16-30", f"{', '.join(g(100 * v, 8) for v in gm)}; {', '.join(g(100 * v, 8) for v in gs)}")
anchor("A16-31", f"{g(1e4 * within)}; {g(1e4 * between)}; {g(1e4 * float(x2.var()))}; "
       f"{g(100 * between / float(x2.var()))}")
for lab, k_, pm, ps in (("$R\\le-1\\%$", 0, "-0.9505", "1.4122"), ("between", 1, "0.0730", "0.8426"),
                        ("$R\\ge1\\%$", 2, "0.8458", "1.2201")):
    chk(f"X4 mean, bin {k_}", 100 * gm[k_], ".4f", pm)
    chk(f"X4 SD, bin {k_}", 100 * gs[k_], ".4f", ps)
    has(f"X4 row {k_}", f"| {lab} | {gn[k_]:,} | {pm} | {ps} |")
has("X4 all days", "| All days | 4,382 | 0.0494 | 1.2173 |")
chk("within", 1e4 * within, ".3f", "1.140")
chk("between", 1e4 * between, ".3f", "0.342")
chk("total", 1e4 * float(x2.var()), ".3f", "1.482")
chk("share", 100 * between / float(x2.var()), ".1f", "23.1")
ng = np.array([859, 2519, 1004])
mgp, sgp = np.array([-0.9505, 0.0730, 0.8458]), np.array([1.4122, 0.8426, 1.2201])
wg = ng / T
mean_p = float(wg @ mgp)
within_p = float(wg @ sgp**2)
between_p = float(wg @ (mgp - mean_p) ** 2)
anchor("A16-32", f"{g(within_p)}; {g(between_p)}; {g(within_p + between_p)}; "
       f"{g(100 * between_p / (within_p + between_p))}; {g(mean_p)}")
chk("tower from printed bins", mean_p, ".4f", "0.0494")
chk("within from printed bins", within_p, ".3f", "1.140")
chk("between from printed bins", between_p, ".3f", "0.342")
chk("total from printed bins", within_p + between_p, ".3f", "1.482")
chk("share from printed parts", 100 * 0.342 / 1.482, ".1f", "23.1")
chk("total = 1.2173^2", 1.2173**2, ".3f", "1.482")
anchor("A16-34", g(rho**2))
chk("rho^2", rho**2, ".4f", "0.3305")
anchor("A16-15", g(float(mgp.mean())))
chk("equal-weight mean of bin means", float(mgp.mean()), ".4f", "-0.0106")
chk("middle bin share, %", 100 * 2519 / T, ".0f", "57")
ell2 = float(stats.norm.pdf(2.0)) / float(stats.norm.cdf(-2.0))
anchor("A16-16", g(ell2))
chk("ell at 2 = -E[Z | Z <= -2]", ell2, ".4f", "2.3732")
assert "-2.3732" in norm((ROOT / "src" / "lm05.md").read_text(encoding="utf-8"))
chk("Phi(-2)", float(stats.norm.cdf(-2.0)), ".5f", "0.02275")
chk("KC ratio from the printed Phi(-2)", float(stats.norm.pdf(2.0)) / 0.02275, ".4f", "2.3732")

# P6: the TAIEX price index tomorrow, grouped by today's |R_t| >= 2%
gb, gnb = b_[big], b_[~big]
anchor("A16-64", f"{int(big.sum())}; {int((~big).sum())}; {g(100 * float(gb.mean()))}; {g(100 * float(gnb.mean()))}; "
       f"{g(100 * float(gb.std()))}; {g(100 * float(gnb.std()))}")
chk("P6 other days", int((~big).sum()), ",", "4,075")
chk("P6 mean after big", 100 * float(gb.mean()), ".4f", "0.2251")
chk("P6 mean after others", 100 * float(gnb.mean()), ".4f", "0.0496")
chk("P6 SD after big", 100 * float(gb.std()), ".4f", "1.8889")
chk("P6 SD after others", 100 * float(gnb.std()), ".4f", "1.0570")
wb, wn = 306 / 4381, 4075 / 4381
mp6 = wb * 0.2251 + wn * 0.0496
w6 = wb * 1.8889**2 + wn * 1.0570**2
bt6 = wb * (0.2251 - mp6) ** 2 + wn * (0.0496 - mp6) ** 2
anchor("A16-65", f"{g(mp6)}; {g(w6)}; {g(bt6)}; {g(w6 + bt6)}; {g(100 * bt6 / (w6 + bt6))}; "
       f"{g(100 * float(b_.mean()))}; {g(1e4 * float(b_.var()))}")
chk("P6 mean", mp6, ".4f", "0.0619")
chk("P6 within", w6, ".3f", "1.288")
chk("P6 between", bt6, ".3f", "0.002")
chk("P6 between from the printed mean", wb * (0.2251 - 0.0619) ** 2 + wn * (0.0496 - 0.0619) ** 2, ".3f", "0.002")
chk("P6 total", w6 + bt6, ".3f", "1.290")
chk("P6 total from printed parts", 1.288 + 0.002, ".3f", "1.290")
chk("P6 share, one decimal", 100 * bt6 / (w6 + bt6), ".1f", "0.2")
chk("P6 share, three decimals", 100 * bt6 / (w6 + bt6), ".3f", "0.155")
chk("P6 share from the printed parts", 100 * 0.002 / 1.290, ".3f", "0.155")
chk("P6 share from the printed parts, one decimal", 100 * 0.002 / 1.290, ".1f", "0.2")
bt6u = wb * (float(gb.mean()) - float(b_.mean())) ** 2 + wn * (float(gnb.mean()) - float(b_.mean())) ** 2
chk("P6 share, unrounded data", 100 * bt6u / float(b_.var()), ".3f", "0.155")
has("P6 share as printed", "a share between of 0.2% (0.155%)")
has("P6 between part", "The between part is tiny (0.002 of 1.290)")
chk("P6 unrounded mean", 100 * float(b_.mean()), ".4f", "0.0619")
chk("P6 unrounded variance", 1e4 * float(b_.var()), ".3f", "1.290")
anchor("A16-66", f"{g(1.8889 / 1.0570)}; {F('0.2251') / 2 + F('0.0496') / 2}; {g((0.2251 + 0.0496) / 2)}")
chk("P6 SD ratio", 1.8889 / 1.0570, ".2f", "1.79")
assert F("0.2251") / 2 + F("0.0496") / 2 == F("0.13735")
chk("P6 equal-weight mean, exact", (0.2251 + 0.0496) / 2, ".5f", "0.13735")

# ============================================================ Section 6: the normal pair
M1, M2, S1, S2, RH = 0.0947, 0.0494, 1.5243, 1.2173, 0.5749     # printed inputs (% a day)
beta = RH * S2 / S1
csd = S2 * math.sqrt(1 - RH**2)
cm5 = M2 + beta * (-5 - M1)
anchor("A16-54", f"{g(beta)}; {g(cm5)}; {g(csd)}; {g((-3 - cm5) / csd)}; {g(float(stats.norm.cdf((-3 - cm5) / csd)))}")
chk("E7 beta", beta, ".4f", "0.4591")
chk("E7 conditional mean", cm5, ".2f", "-2.29")
chk("E7 conditional mean from printed beta", M2 + 0.4591 * (-5 - M1), ".2f", "-2.29")
chk("E7 conditional SD", csd, ".3f", "0.996")
chk("E7 z from printed mean and SD", (-3 + 2.29) / 0.996, ".3f", "-0.713")
chk("E7 probability from printed z", float(stats.norm.cdf(-0.713)), ".3f", "0.238")
chk("E7 probability from printed mean and SD", float(stats.norm.cdf((-3 + 2.29) / 0.996)), ".3f", "0.238")
beta_u = c12 / s1**2
cm5u = 100 * (m2 + beta_u * (-0.05 - m1))
csdu = 100 * s2 * math.sqrt(1 - rho**2)
anchor("A16-55", f"{g(beta_u)}; {g(cm5u)}; {g(csdu)}")
chk("E7 beta, unrounded", beta_u, ".4f", "0.4591")
chk("E7 mean, unrounded", cm5u, ".2f", "-2.29")
chk("E7 SD, unrounded", csdu, ".3f", "0.996")
chk("E7 z, unrounded", (-3 - cm5u) / csdu, ".3f", "-0.713")
chk("E7 probability, unrounded", float(stats.norm.cdf((-3 - cm5u) / csdu)), ".3f", "0.238")
has("unrounded inputs agree", "Unrounded inputs agree.")
assert "0.4591" in norm((ROOT / "src" / "lm12.md").read_text(encoding="utf-8"))
sel5 = (x1 >= -0.055 - EPS) & (x1 <= -0.045 + EPS)
anchor("A16-56", f"{int(sel5.sum())}; {g(100 * float(x2[sel5].mean()))}; {g(100 * float(x2[sel5].std()))}; "
       f"{int((x2[sel5] <= -0.03 + EPS).sum())}")
chk("E7 days", int(sel5.sum()), "d", "17")
chk("E7 data mean", 100 * float(x2[sel5].mean()), ".2f", "-2.86")
chk("E7 data SD", 100 * float(x2[sel5].std()), ".2f", "2.00")
assert int((x2[sel5] <= -0.03 + EPS).sum()) == 6
has("E7 six days", "Six fell 3% or more")

# P7: Semiconductor = -3%, from the printed mean -1.37
cm3 = M2 + beta * (-3 - M1)
z7 = (-2 + 1.37) / 0.996
anchor("A16-67", f"{g(cm3)}; {g(z7)}; {g(float(stats.norm.cdf(z7)))}; {g(float(stats.norm.cdf((-2 + 1.37) / S2)))}; "
       f"{g(M2 + RH * (-3 - M1))}")
chk("P7 mean", cm3, ".2f", "-1.37")
chk("P7 mean from printed beta", M2 + 0.4591 * (-3 - M1), ".2f", "-1.37")
chk("P7 z", z7, ".4f", "-0.6325")
chk("P7 probability from printed z", float(stats.norm.cdf(-0.6325)), ".3f", "0.264")
chk("P7 probability", float(stats.norm.cdf(z7)), ".3f", "0.264")
chk("P7 unconditional SD route", float(stats.norm.cdf(-0.63 / 1.2173)), ".3f", "0.302")
chk("P7 slope rho route", M2 + RH * (-3 - M1), ".2f", "-1.73")

# the pair's covariance matrix, eigenvalues, contours
anchor("A16-35", f"{g(1e4 * s1**2, 7)}; {g(1e4 * c12, 7)}; {g(1e4 * s2**2, 7)}")
chk("sigma_11 (%^2)", 1e4 * s1**2, ".6f", "2.323354")
chk("sigma_21 (%^2)", 1e4 * c12, ".6f", "1.066603")
chk("sigma_22 (%^2)", 1e4 * s2**2, ".6f", "1.481729")
tr2, det2 = 2.323354 + 1.481729, 2.323354 * 1.481729 - 1.066603**2
lam1 = tr2 / 2 + math.sqrt(tr2**2 / 4 - det2)
lam2 = tr2 / 2 - math.sqrt(tr2**2 / 4 - det2)
ev2 = np.linalg.eigvalsh(1e4 * cov0(XP))
assert abs(ev2[1] - lam1) < 1e-5 and abs(ev2[0] - lam2) < 1e-5
anchor("A16-79", f"{g(lam1)}; {g(lam2)}; {g(math.sqrt(lam1))}; {g(math.sqrt(lam2))}")
chk("lambda_1", lam1, ".3f", "3.049")
chk("lambda_2", lam2, ".3f", "0.756")
chk("sqrt lambda_1", math.sqrt(lam1), ".3f", "1.746")
chk("sqrt lambda_2", math.sqrt(lam2), ".3f", "0.869")
anchor("A16-36", ", ".join([*(g(100 * (1 - math.exp(-k * k / 2))) for k in (1, 2, 3)),
                            *(g(100 * float((d2 <= k * k + EPS).mean())) for k in (1, 2, 3))]).replace(", ", "; "))
for k, pm, pd in ((1, "39.35", "56.16"), (2, "86.47", "87.95"), (3, "98.89", "95.96")):
    chk(f"X5 model inside k={k}", 100 * (1 - math.exp(-k * k / 2)), ".2f", pm)
    chk(f"X5 data inside k={k}", 100 * float((d2 <= k * k + EPS).mean()), ".2f", pd)

# X6: the pair and S5
anchor("A16-37", "; ".join([", ".join(g(100 * math.exp(-k * k / 2), 6) for k in range(1, 6)),
                            ", ".join(g(T * math.exp(-k * k / 2), 6) for k in range(1, 6)),
                            ", ".join(str(outside(d2, k * k)) for k in range(1, 6))]))
share_fmt = (".2f", ".2f", ".2f", ".4f", ".5f")
exp_fmt = (",.1f", ".1f", ".1f", ".2f", ".3f")
share_p = ("60.65", "13.53", "1.11", "0.0335", "0.00037")
exp_p = ("2,657.8", "593.0", "48.7", "1.47", "0.016")
act_p = ("1,921", "528", "177", "61", "25")
for k in range(1, 6):
    chk(f"X6 pair share k={k}", 100 * math.exp(-k * k / 2), share_fmt[k - 1], share_p[k - 1])
    chk(f"X6 pair expected k={k}", T * math.exp(-k * k / 2), exp_fmt[k - 1], exp_p[k - 1])
    chk(f"X6 pair actual k={k}", outside(d2, k * k), ",", act_p[k - 1])
has("X6 pair row", "| U28 days | 1,921 | 528 | 177 | 61 | 25 |")
X5m = X[:, [col[c] for c in S5]]
d25 = mahal(X5m)
assert abs(d25.mean() - 5) < 1e-9
qs = (0.5, 0.9, 0.99, 0.999)
cs = [float(stats.chi2.ppf(q, 5)) for q in qs]
anchor("A16-38", "; ".join([", ".join(g(c, 6) for c in cs), ", ".join(g(T * (1 - q), 6) for q in qs),
                            ", ".join(str(outside(d25, c)) for c in cs)]))
for c, q, pc, pe, pa, fe in zip(cs, qs, ("4.35", "9.24", "15.09", "20.52"), ("2,191", "438.2", "43.8", "4.4"),
                                ("1,411", "613", "291", "184"), (",.0f", ".1f", ".1f", ".1f"), strict=True):
    chk(f"X6 S5 quantile {q}", c, ".2f", pc)
    chk(f"X6 S5 expected {q}", T * (1 - q), fe, pe)
    chk(f"X6 S5 actual {q}", outside(d25, c), ",", pa)
has("X6 S5 row", "| U28 days | 1,411 | 613 | 291 | 184 |")

# E9
lm12 = norm((ROOT / "src" / "lm12.md").read_text(encoding="utf-8"))
assert "| 1 | 2025-04-07 | 89.30 |" in lm12 and "| 1 | 1.5243 |" not in lm12
anchor("A16-57", f"{g(float(d25[i7]))}; {int((d25 > d25[i7]).sum()) + 1}; 89.30 (printed in lm12.md:483)")
chk("S5 d^2 on 7 April", float(d25[i7]), ".2f", "89.30")
sf89 = float(stats.chi2.sf(89.30, 5))
anchor("A16-58", f"{g(sf89, 6)}; {g(1 / (sf89 * 245.48), 6)}")
same("E9 probability", sci(sf89, 1), "9.4\\times10^{-18}")
same("E9 years", sci(1 / (sf89 * 245.48), 0), "4\\times10^{14}")
has("E9 tail days", "184 days lie beyond the 99.9% quantile 20.52, where the model expects 4.4")

# KC section 6: U28's 28-dimensional d^2
d228 = mahal(X)
assert abs(d228.mean() - 28) < 1e-8
imax = int(np.argmax(d228))
anchor("A16-19", f"{g(float(d228[i7]))}; {int((d228 > d228[i7]).sum()) + 1}; {g(float(d228[imax]))}; {dates[imax]}")
chk("KC6 7 April d^2", float(d228[i7]), ".2f", "132.29")
assert int((d228 > d228[i7]).sum()) + 1 == 15 and dates[imax] == "2009-05-05"
has("KC6 rank", "ranks only 15th")
has("KC6 date", "falls on 5 May 2009")
chk("KC6 largest", float(d228[imax]), ".2f", "209.55")
_, q_ = np.linalg.eigh(cov0(X))
dev7 = X[i7] - X.mean(axis=0)
anchor("A16-20", f"{g(float((q_[:, -1] @ dev7) ** 2 / (dev7 @ dev7)))}; {g(100 * float(X[imax].min()))}; "
       f"{g(100 * float(X[imax].max()))}; {g(100 * float(RT[imax]))}")
chk("KC6 share along q_1", 100 * float((q_[:, -1] @ dev7) ** 2 / (dev7 @ dev7)), ".1f", "97.1")
chk("KC6 lowest sector", 100 * float(X[imax].min()), ".2f", "-3.71")
chk("KC6 highest sector", 100 * float(X[imax].max()), "+.2f", "+6.06")
chk("KC6 TAIEX", 100 * float(RT[imax]), ".2f", "0.78")
all_down, all_up = int((X < 0).all(axis=1).sum()), int((X > 0).all(axis=1).sum())
anchor("A16-78", f"{all_down}; {all_up}; (printed in lm11.md:48)")
assert "| Days on which all 28 rose; all 28 fell | 144; 156 |" in norm((ROOT / "src" / "lm11.md").read_text(encoding="utf-8"))
chk("all 28 fell", all_down, "d", "156")

# ============================================================ Section 7: crash correlation


def trunc(mu: float, sd: float, c: float) -> tuple[float, float, float]:
    """E[1{W<=c}], E[W 1{W<=c}], E[W^2 1{W<=c}] for W ~ N(mu, sd^2)."""
    a = (c - mu) / sd
    big_phi, small_phi = float(stats.norm.cdf(a)), float(stats.norm.pdf(a))
    return big_phi, mu * big_phi - sd * small_phi, (mu * mu + sd * sd) * big_phi - sd * (mu + c) * small_phi


def bvn_lower(r_: float, k: float) -> tuple[float, float]:
    """Probability and correlation of a standard normal pair with correlation r_, given both <= -k (quad)."""
    c, sd = -k, math.sqrt(1 - r_ * r_)

    def mom(which: int) -> float:
        def f(x: float) -> float:
            p0, p1, p2 = trunc(r_ * x, sd, c)
            return float(stats.norm.pdf(x)) * (p0, x * p0, p1, x * x * p0, p2, x * p1)[which]

        return integrate.quad(f, -np.inf, c, epsabs=1e-13, epsrel=1e-11, limit=200)[0]

    p, ex, ey, exx, eyy, exy = (mom(w) for w in range(6))
    vx, vy = exx / p - (ex / p) ** 2, eyy / p - (ey / p) ** 2
    return p, (exy / p - ex * ey / p**2) / math.sqrt(vx * vy)


def v_two(k: float) -> float:
    return 1 + k * float(stats.norm.pdf(k)) / float(stats.norm.sf(k))


def v_low(k: float) -> float:
    ell = float(stats.norm.pdf(k)) / float(stats.norm.cdf(-k))
    return 1 + k * ell - ell * ell


def bgl(r_: float, v: float) -> float:
    """(16.10) with Var(X) = 1."""
    return r_ / math.sqrt(r_ * r_ + (1 - r_ * r_) / v)


assert abs(bvn_lower(rho, 0.0)[0] - (0.25 + math.asin(rho) / (2 * math.pi))) < 1e-10
assert abs(bvn_lower(RH, 0.0)[0] - (0.25 + math.asin(RH) / (2 * math.pi))) < 1e-10
# the model rows of the exceedance exhibit use the printed rho = 0.5749, as the note, condcorr and the widget do
mod = {k: bvn_lower(RH, k) for k in (0.0, 1.0, 2.0)}
mod_u = {k: bvn_lower(rho, k) for k in (0.0, 1.0, 2.0)}
for k in mod:            # the unrounded rho changes only k = 0's expected days (1,522.6), nothing else printed
    assert f"{mod[k][1]:.3f}" == f"{mod_u[k][1]:.3f}" and f"{mod[k][0]:.4f}" == f"{mod_u[k][0]:.4f}"
has("X8 note: rho", "Benchmark and model rows at $\\rho=0.5749$")
anchor("A16-39", "; ".join(g(mod[k][1]) for k in mod))
anchor("A16-42", "; ".join(f"{g(mod[k][0])} ({g(T * mod[k][0])})" for k in mod))
for k, pc, pp, pd in ((0.0, "0.332", "0.3475", "1,522.7"), (1.0, "0.229", "0.0699", "306.3"), (2.0, "0.156", "0.0051", "22.4")):
    chk(f"X8 benchmark k={k}", mod[k][1], ".3f", pc)
    chk(f"X8 model probability k={k}", mod[k][0], ".4f", pp)
    chk(f"X8 model days k={k}", T * mod[k][0], ",.1f", pd)
lo1, lo2 = (x1 - m1) / s1, (x2 - m2) / s2


def exceed(k: float, side: int) -> tuple[int, float]:
    sel = ((lo1 <= -k + EPS) & (lo2 <= -k + EPS)) if side < 0 else ((lo1 >= k - EPS) & (lo2 >= k - EPS))
    return int(sel.sum()), corr(x1[sel], x2[sel])


low = {k: exceed(k, -1) for k in (0.0, 1.0, 2.0)}
upp = {k: exceed(k, +1) for k in (0.0, 1.0, 2.0)}
anchor("A16-40", "; ".join(f"{low[k][0]} {g(low[k][1])}" for k in low))
anchor("A16-41", "; ".join(f"{upp[k][0]} {g(upp[k][1])}" for k in upp))
for k, dl, rl, du, ru in ((0.0, "1,509", "0.575", "1,523", "0.430"), (1.0, "228", "0.465", "170", "0.452"),
                          (2.0, "44", "0.669", "32", "0.541")):
    chk(f"X8 falls days k={k}", low[k][0], ",", dl)
    chk(f"X8 falls corr k={k}", low[k][1], ".3f", rl)
    chk(f"X8 rises days k={k}", upp[k][0], ",", du)
    chk(f"X8 rises corr k={k}", upp[k][1], ".3f", ru)
has("X8 table falls", "| Joint falls: $\\hat\\rho$ | 0.575 | 0.465 | 0.669 |")
has("X8 table rises", "| Joint rises: $\\hat\\rho$ | 0.430 | 0.452 | 0.541 |")
assert min(min(exceed(0.25 * j, -1)[0], exceed(0.25 * j, +1)[0]) for j in range(9)) >= 30
has("X8 at least 30 days", "at least 30 days at each point")

two, fall, rise = [], [], []
for k in (1.0, 2.0, 2.5):
    s_two = np.abs(lo1) >= k - EPS
    s_fall, s_rise = lo1 <= -k + EPS, lo1 >= k - EPS
    two.append((int(s_two.sum()), corr(x1[s_two], x2[s_two]), bgl(rho, v_two(k))))
    fall.append((int(s_fall.sum()), corr(x1[s_fall], x2[s_fall]), bgl(rho, v_low(k))))
    rise.append((int(s_rise.sum()), corr(x1[s_rise], x2[s_rise])))
anchor("A16-43", "; ".join([", ".join(str(t[0]) for t in two), ", ".join(g(t[1]) for t in two), ", ".join(g(t[2]) for t in two)]))
anchor("A16-44", "; ".join([", ".join(str(t[0]) for t in fall), ", ".join(g(t[1]) for t in fall), ", ".join(g(t[2]) for t in fall)]))
anchor("A16-45", "; ".join([", ".join(str(t[0]) for t in rise), ", ".join(g(t[1]) for t in rise)]))
anchor("A16-21", "; ".join([", ".join(g(v_two(k)) for k in (1.0, 2.0, 2.5)), ", ".join(g(v_low(k)) for k in (1.0, 2.0, 2.5))]))
X9_rows = (("moves $k$ or more either way", two, ("1,088", "223", "111"), ("0.692", "0.788", "0.811"), ("0.745", "0.860", "0.894")),
           ("falls $k$ or more", fall, ("550", "105", "47"), ("0.474", "0.488", "0.485"), ("0.299", "0.231", "0.205")),
           ("rises $k$ or more", rise, ("538", "118", "64"), ("0.367", "0.429", "0.382"), ("0.299", "0.231", "0.205")))
for name, vals, pd, pr, pm in X9_rows:
    for j, kk in enumerate(("1", "2", "2.5")):
        chk(f"X9 {name} days k={kk}", vals[j][0], ",", pd[j])
        chk(f"X9 {name} data k={kk}", vals[j][1], ".3f", pr[j])
        model = fall[j][2] if name.startswith("rises") else vals[j][2]
        chk(f"X9 {name} model k={kk}", model, ".3f", pm[j])
        first = f"| {name} " if j == 0 else "| "
        has(f"X9 row {name} k={kk}", f"{first}| {kk} | {pd[j]} | {pr[j]} | {pm[j]} |")
for k in (1.0, 2.0, 2.5):    # the note's printed rho = 0.5749 gives the same model column
    assert f"{bgl(RH, v_two(k)):.3f}" == f"{bgl(rho, v_two(k)):.3f}" and f"{bgl(RH, v_low(k)):.3f}" == f"{bgl(rho, v_low(k)):.3f}"
has("X9 note: rho", "The model uses $\\rho=0.5749$")
for k, pt, pl_ in ((1.0, "2.5251", "0.1991"), (2.0, "5.7464", "0.1143"), (2.5, "8.0569", "0.0890")):
    chk(f"Var(Z | |Z| >= {k})", v_two(k), ".4f", pt)
    chk(f"Var(Z | Z <= -{k})", v_low(k), ".4f", pl_)
chk("model from printed variance 5.7464", bgl(RH, 5.7464), ".3f", "0.860")
chk("model from printed variance 0.1143", bgl(RH, 0.1143), ".3f", "0.231")
anchor("A16-72", f"{g(bgl(RH, 5.7464))}; {g(bgl(RH, 0.1143))}")
chk("DD3 1 + 2 ell from printed ell", 1 + 2 * 2.3732, ".4f", "5.7464")
chk("DD3 1 + 2 ell - ell^2 from printed ell", 1 + 2 * 2.3732 - 2.3732**2, ".4f", "0.1143")
anchor("A16-22", g(bgl(RH, 2.5251)))
chk("KC7 from printed inputs", bgl(RH, 2.5251), ".3f", "0.745")

# E10: Semiconductor on 7-9 April in standard deviations, from printed inputs; unrounded for 9 April
anchor("A16-59", "; ".join(g((r - M1) / S1) for r in r1p))
anchor("A16-80", "; ".join(g(float((x1[i7 + j] - m1) / s1)) for j in range(3)))
for r, p in zip(r1p, ("-6.59", "-2.68", "-2.99"), strict=True):
    chk(f"E10 move {r}", (r - M1) / S1, ".2f", p)
chk("E10 9 April, unrounded", float((x1[i7 + 2] - m1) / s1), ".2f", "-3.00")

# ============================================================ the widget's grid (as data/lm16_charts.py writes it)
GL_X, GL_W = np.polynomial.legendre.leggauss(600)


def joint_low(rs: Vec, k: float) -> tuple[Vec, Vec]:
    """bvn_lower vectorized over rs: Gauss-Legendre on [-14, -k] (checked against quad below)."""
    c, lo = -k, -14.0
    x = 0.5 * (c - lo) * GL_X + 0.5 * (c + lo)
    w = 0.5 * (c - lo) * GL_W * np.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)
    r_ = rs[:, None]
    sd = np.sqrt(1 - r_ * r_)
    a = (c - r_ * x) / sd
    big_phi, small_phi = special.ndtr(a), np.exp(-0.5 * a * a) / math.sqrt(2 * math.pi)
    p1 = r_ * x * big_phi - sd * small_phi
    p2 = (r_ * r_ * x * x + sd * sd) * big_phi - sd * (r_ * x + c) * small_phi
    p, ex, ey = big_phi @ w, (x * big_phi) @ w, p1 @ w
    exx, eyy, exy = (x * x * big_phi) @ w, p2 @ w, (x * p1) @ w
    vx, vy = exx / p - (ex / p) ** 2, eyy / p - (ey / p) ** 2
    return p, (exy / p - ex * ey / p**2) / np.sqrt(vx * vy)


for r_chk, k_chk in ((0.57, 2.0), (rho, 1.0), (0.95, 2.5), (0.0, 0.0)):
    pv, cv = joint_low(np.array([r_chk]), k_chk)
    pq, cq = bvn_lower(r_chk, k_chk)
    assert abs(pv[0] - pq) < 1e-12 and abs(cv[0] - cq) < 1e-12


def lag4(yg: Vec, x: Vec, h: float = 0.01) -> Vec:
    """Four-point Lagrange interpolation on the nodes 0, h, 2h, ... (the four nearest nodes, clamped at the ends)."""
    i0 = np.clip(np.floor(x / h + 1e-9).astype(np.int64) - 1, 0, len(yg) - 4)
    t = x / h - i0
    out = np.zeros_like(x)
    for a in range(4):
        la = np.ones_like(x)
        for b in range(4):
            if b != a:
                la = la * (t - b) / (a - b)
        out = out + la * yg[i0 + a]
    return out


rgrid = np.asarray(np.arange(96) * 0.01, dtype=np.float64)
rfine = np.asarray(np.arange(9501) * 1e-4, dtype=np.float64)
err_c = err_p = 0.0
for j in range(51):
    pg_, cg_ = joint_low(rgrid, 0.05 * j)
    pf_, cf_ = joint_low(rfine, 0.05 * j)
    err_c = max(err_c, float(np.abs(lag4(cg_, rfine) - cf_).max()))
    err_p = max(err_p, float(np.abs(lag4(pg_, rfine) - pf_).max()))
anchor("A16-46", f"{g(err_c, 4)}; {g(err_p, 4)}; {g(T * err_p, 4)}")
assert err_c < 1e-5 and T * err_p < 0.01
has("widget errors", "with errors below $10^{-5}$ in the correlation and 0.01 days in the count")
pg2, cg2 = joint_low(rgrid, 2.0)
chk("widget initial correlation", float(lag4(cg2, np.array([RH]))[0]), ".3f", "0.156")
chk("widget initial probability", float(lag4(pg2, np.array([RH]))[0]), ".4f", "0.0051")
chk("widget initial days", T * float(lag4(pg2, np.array([RH]))[0]), ".1f", "22.4")

# ============================================================ Section 8 and the problems
chk("Python: 1 - cdf", 1 - float(stats.chi2.cdf(89.30, 5)), ".1f", "0.0")
assert 1 - float(stats.chi2.cdf(89.30, 5)) == 0.0 and sf89 < 1e-17
anchor("A16-73", f"{1 - float(stats.chi2.cdf(89.30, 5))!r}; {sf89!r}; {g(float(stats.chi2.sf(9, 2)))}; "
       f"{g(T * float(stats.chi2.sf(9, 2)))}")
same("Python: sf", f"{sf89:.1e}", "9.4e-18")
same("pitfall: spacing below 1", sci(2.0**-53, 1), "1.1\\times10^{-16}")
assert np.nextafter(1.0, 0.0) == 1 - 2.0**-53
has("code: corner count", "# 347 days, the corner cell")

# P4 (constructed)
anchor("A16-61", "; ".join([g(math.sqrt(0.04 + 0.0225 - 2 * 0.5 * 0.2 * 0.15)), g(0.6 * 0.04 + 0.4 * 0.5 * 0.2 * 0.15),
                            g(math.sqrt(0.36 * 0.04 + 2 * 0.24 * 0.015 + 0.16 * 0.0225)),
                            g((0.6 * 0.04 + 0.4 * 0.015) / (0.2 * math.sqrt(0.36 * 0.04 + 2 * 0.24 * 0.015 + 0.16 * 0.0225))),
                            g(math.sqrt((0.2 - 0.15) ** 2)), g(math.sqrt(0.04 + 0.0225))]))
assert F("0.04") + F("0.0225") - 2 * F("0.5") * F("0.20") * F("0.15") == F("0.0325")
assert F("0.6") * F("0.04") + F("0.4") * F("0.015") == F("0.03") and F("0.5") * F("0.2") * F("0.15") == F("0.015")
assert F("0.36") * F("0.04") + 2 * F("0.24") * F("0.015") + F("0.16") * F("0.0225") == F("0.0252")
chk("P4 volatility of R1 - R2", 100 * math.sqrt(0.0325), ".2f", "18.03")
chk("P4 Cov(R1, Rp)", 0.03, ".4f", "0.0300")
chk("P4 sigma_p", 100 * math.sqrt(0.0252), ".2f", "15.87")
chk("P4 correlation from printed sigma_p", 0.03 / (0.2 * 0.1587), ".3f", "0.945")
chk("P4 correlation, unrounded", 0.03 / (0.2 * math.sqrt(0.0252)), ".3f", "0.945")

# P5
fac = 1 + 2 * 0.04 * (245 - 1) / 245
anchor("A16-62", f"{g(fac)}; {g(math.sqrt(245) * 1.1392 * math.sqrt(fac))}")
anchor("A16-63", f"{g(245 * 1.1392)}; {g(17.83 * fac)}; {g(math.sqrt(245) * 1.1392 * fac)}")
chk("P5 factor", fac, ".4f", "1.0797")
chk("P5 SD from printed 17.83 and factor", 17.83 * math.sqrt(1.0797), ".2f", "18.53")
chk("P5 SD, unrounded", math.sqrt(245) * 1.1392 * math.sqrt(fac), ".2f", "18.53")
chk("P5 wrong route: 245 x 1.1392", 245 * 1.1392, ".1f", "279.1")
chk("P5 wrong route: 17.83 x factor", 17.83 * 1.0797, ".2f", "19.25")

# P8: 5 August 2024 from printed inputs
i5 = dates.index("2024-08-05")
anchor("A16-68", f"{g(100 * x1[i5])}; {g(100 * x2[i5])}")
chk("P8 Semiconductor return", 100 * x1[i5], ".2f", "-9.48")
chk("P8 FinancialInsurance return", 100 * x2[i5], ".2f", "-6.93")
assert "| 2 FinancialInsurance | 0.6998 | 0.9960 |" in lm12 and "| 1 Semiconductor | 1.5243 |" in lm12
anchor("A16-69", "1.5243; 0.6998; 0.9960 (printed in lm12.md:441-442)")
z1 = (-9.48 - M1) / 1.5243
z2 = (-6.93 - M2 - 0.6998 * z1) / 0.9960
anchor("A16-70", f"{g(z1)}; {g(z2)}; {g(z1 * z1 + z2 * z2)}; {g(float(d2[i5]))}")
chk("P8 z1", z1, ".3f", "-6.281")
chk("P8 z2", z2, ".3f", "-2.594")
chk("P8 z2 from printed z1", (-6.93 - M2 - 0.6998 * -6.281) / 0.9960, ".3f", "-2.594")
chk("P8 d^2", z1 * z1 + z2 * z2, ".2f", "46.18")
chk("P8 d^2 from printed z", 6.281**2 + 2.594**2, ".2f", "46.18")
chk("P8 d^2 unrounded", float(d2[i5]), ".2f", "46.22")
anchor("A16-71", f"{g((z1 * z1 + z2 * z2) / 2)}; {g(math.exp(-(z1 * z1 + z2 * z2) / 2), 6)}; "
       f"{g(T * math.exp(-(z1 * z1 + z2 * z2) / 2), 6)}")
chk("P8 half of d^2", 46.18 / 2, ".2f", "23.09")
same("P8 probability", sci(math.exp(-23.09), 1), "9.4\\times10^{-11}")
same("P8 expected days", sci(T * math.exp(-23.09), 0), "4\\times10^{-7}")

# figures the anchors list for other parts (lab), compared here
anchor("A16-74", "4,307 (printed in build/make_lab12.py:167)")
reg = np.array([d <= "2015-05-29" for d in dates])
anchor("A16-75", f"{int(reg.sum())}; {int((~reg).sum())}; {g(corr(x1[reg], x2[reg]))}; {g(corr(x1[~reg], x2[~reg]))}; "
       f"{int((~(d2[reg] <= 9 + EPS)).sum())}; {int((~(d2[~reg] <= 9 + EPS)).sum())}")

print(f"\n{len(ANCHOR_DIFFS)} anchor differences" + ("".join(f"\n  {d}" for d in ANCHOR_DIFFS) if ANCHOR_DIFFS else ""))
print(f"all {N_CHECKS} checks passed")
