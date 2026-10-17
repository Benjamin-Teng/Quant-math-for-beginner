"""Every number that LM10 (Quadratic Forms and Covariance Matrices) prints, with its checks.

Run after data/vol2_series.py:  uv run python data/lm10_numbers.py

Inputs: data/processed/vol2_closes.parquet (the repaired sector closes) and data/processed/vol2_repairs.json, both
from data/vol2_series.py, and the raw 0050, 00631L and 00679B closes and dividends in data/raw/ (see
data/lm10_series.py for the U28 sample and the ETFs' one-session total returns).

The script prints each value as src/lm10.md prints it, asserts the first two things below and reports the third:
  * every printed value appears in src/lm10.md exactly as printed (after the normalization in `norm`);
  * every hand calculation follows from the inputs printed next to it (PITFALLS section 7): such values are
    recomputed from the printed strings, often in exact decimal arithmetic;
  * the data values agree with the editor's anchors (plans/vol-2-anchors.md, LM10). Rows 14, 21 and 35 give the
    module's values, from the S3 matrix printed to two decimals (E7: its block in whole %²), and beside them the
    values from the matrix to one decimal; the script compares both. Row 34 gives the module's pivots only. A
    difference prints DIFFERS and is listed at the end.
A floating-point residue is never printed in the module: it is asserted against a bound, and the text says "below
10^-15" (the daily 6×6 matrix of S5 and its equal-weight column) or "larger" (the 50/50 matrix in %²).
"""
import json
import math
import re
import sys
from fractions import Fraction as Fr
from itertools import permutations
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lm10_series import ETFS, REPAIRS, S3, S5, cov0, one_session, u28

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "src" / "lm10.md"


def norm(s: str) -> str:
    """Make prose and math spellings comparable: 4{,}382 -> 4,382; minus sign -> hyphen; \\% -> %."""
    return s.replace("{,}", ",").replace("\u2212", "-").replace("\\%", "%")


MD = norm(MD_PATH.read_text(encoding="utf-8"))
PRINTED: list[tuple[str, str]] = []


def show(label: str, text: str) -> str:
    """A value the module prints; checked against src/lm10.md at the end."""
    print(f"{label}: {text}")
    PRINTED.append((label, text))
    return text


def same(label: str, got: str, printed: str) -> None:
    """A printed figure recomputed from printed inputs must give the printed text."""
    print(f"CHECK {label}: {got} (printed {printed}) {'ok' if got == printed else 'MISMATCH'}")
    assert got == printed, (label, got, printed)


def pct(x: float, d: int = 2) -> str:
    return f"{100 * x:.{d}f}%"


def sci(x: float, d: int) -> str:
    """LaTeX scientific notation as printed: 2.0328\\times10^{-4}."""
    m, e = f"{x:.{d}e}".split("e")
    return f"{m}\\times10^{{{int(e)}}}"


def dec(s: str) -> Fr:
    return Fr(s.replace("\u2212", "-").replace(",", ""))


def fmt(x: float | Fr, d: int) -> str:
    """Round half up in exact arithmetic (a printed hand result must not depend on binary floating point)."""
    q = Fr(x) if not isinstance(x, Fr) else x
    scale = 10**d
    n = abs(q) * scale
    r = int(n) + (1 if n - int(n) >= Fr(1, 2) else 0)
    s = f"{r // scale}" + (f".{r % scale:0{d}d}" if d else "")
    return ("-" if q < 0 and r else "") + s


def thousands(s: str) -> str:
    whole, _, frac = s.partition(".")
    neg = whole.startswith("-")
    whole = f"{int(whole.lstrip('-')):,}"
    return ("-" if neg else "") + whole + (f".{frac}" if frac else "")


def plain(q: Fr, sep: bool = False) -> str:
    """A value with up to six decimals as the anchors spell it: no trailing zeros (416.05, 364.4, 0), commas if sep."""
    assert q * 10**6 == int(q * 10**6), q                                   # exact at six decimals: nothing is cut
    s = fmt(q, 6).rstrip("0").rstrip(".")
    return thousands(s) if sep else s


def det3(m: list[list[Fr]]) -> Fr:
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def pivots(m: np.ndarray) -> np.ndarray:
    """Pivots of Gaussian elimination without row exchanges; stops at the first pivot that is not positive."""
    m = np.array(m, dtype=np.float64)
    out = []
    for k in range(m.shape[0]):
        out.append(m[k, k])
        if m[k, k] <= 0:
            break
        m[k + 1:] -= np.outer(m[k + 1:, k] / m[k, k], m[k])
    return np.array(out)


ANCHOR_DIFFS: list[str] = []


def anchor(label: str, got: str, expected: str) -> None:
    """Compare with plans/vol-2-anchors.md; a difference is reported, not forced."""
    tag = "ok" if got == expected else "DIFFERS"
    print(f"ANCHOR {label}: {got} (anchor {expected}) {tag}")
    if got != expected:
        ANCHOR_DIFFS.append(f"{label}: script {got}, anchor {expected}")


# ====================================================================================== sample (anchors row 1-2)
smp = u28()
X, names, T = smp.X, smp.names, smp.X.shape[0]
A = smp.A
assert T == 4382 and smp.dates[0] == "2008-12-02" and smp.dates[-1] == "2026-10-08"
days = round(smp.years * 365.25)
assert days == 6520
anchor("years", f"{smp.years:.8f}", "17.85078713")
anchor("A", f"{A:.7f}", "245.4793712")
show("T", "4,382")
show("first return", "2 December 2008")
show("last return", "8 October 2026")
show("A formula", f"$A={A:.2f}$ sessions a year: 4,382 returns times 365.25, divided by the sample's {days:,} calendar days")
same("A from printed T and days", f"{4382 * 365.25 / days:.2f}", "245.48")
show("A (overview, notation)", "A=245.48")
rep = json.loads(REPAIRS.read_text(encoding="utf-8"))["repairs"]
r28 = [r for r in rep if r["series"] in names and smp.close_dates[0] <= r["date"] <= smp.close_dates[-1]]
show("repaired closes", f"{len(r28)} closes in this sample (on {len({r['date'] for r in r28})} dates)")
anchor("repairs", f"{len(r28)}; {len({r['date'] for r in r28})}", "524; 38")

# ====================================================================================== case (anchors rows 3-9)
S = cov0(X)
s = np.sqrt(np.diag(S))
vol = s * math.sqrt(A)
order = list(np.argsort(vol))
lo, hi = order[0], order[-1]
show("min vol", f"{pct(vol[lo])} ({names[lo]})")
show("max vol", f"{pct(vol[hi])} ({names[hi]})")
show("mean vol", f"average {pct(vol.mean())}")
w = np.full(28, 1 / 28)
sp2 = float(w @ S @ w)
book = math.sqrt(A * sp2)
assert abs(book - math.sqrt(A) * float((X @ w).std())) < 1e-15            # (10.4) on the data: never printed
show("book vol", f"The book's volatility was {pct(book)}")
below = int((vol < book).sum())
assert below == 1 and names[lo] == "CommunicationsInternet"
show("below the book", "below every sector but one")
tx_vol = math.sqrt(A) * float(smp.taiex.std())
show("TAIEX vol", f"TAIEX's {pct(tx_vol)}")
var_only = math.sqrt(A * float(np.sum(w**2 * s**2)))
show("variances only", f"a volatility of only {pct(var_only)}")
show("distinct entries", "406 distinct entries")
assert 28 * 29 // 2 == 406 and 28 * 27 // 2 == 378
show("X1 note mean", f"({pct(vol.mean())})")
anchor("vols", f"{pct(vol[lo])} {names[lo]}; {pct(vol[hi])} {names[hi]}", "13.67% CommunicationsInternet; 35.31% GlassCeramic")
anchor("mean vol", pct(vol.mean()), "21.94%")
anchor("book", pct(book), "15.75%")
anchor("TAIEX", pct(tx_vol), "17.82%")
anchor("variances only", pct(var_only), "4.22%")
vbar = float(np.mean(np.diag(S)))
off = ~np.eye(28, dtype=bool)
cbar = float(S[off].mean())
share = (sp2 - float(np.sum(w**2 * s**2))) / sp2
anchor("off-diagonal share", f"{100 * share:.1f}%", "92.8%")
# the variance terms' share of the variance (A1): the two printed shares add to 100%
assert f"{100 * share:.1f}" == "92.8" and f"{100 * (1 - share):.1f}" == "7.2"
same("variance-term share from the printed covariance share", f"{100 - 92.8:.1f}%", "7.2%")
show("variance-term share", "the variance terms are the other 7.2%")
show("variance-term share (Summary)", "The variance terms alone, 7.2% of it, would give a volatility of only 4.22%, against the book's 15.75%")
anchor("vbar, cbar", f"{vbar:.4e}; {cbar:.4e}", "2.0328e-04; 9.7254e-05")
C = S / np.outer(s, s)
anchor("mean correlation", f"{C[off].mean():.3f}", "0.502")

# ====================================================================================== Section 2: the S3 matrix
i3 = [names.index(n) for n in S3]
S3m = S[np.ix_(i3, i3)]
AS3 = 1e4 * A * S3m
P3 = [[fmt(AS3[i, j], 2) for j in range(3)] for i in range(3)]       # printed to two decimals
print("A Sigma_3 (%^2), printed:", P3)
for v in (P3[0][0], P3[0][1], P3[0][2], P3[1][1], P3[1][2], P3[2][2]):
    show("A Sigma_3 entry", v)
anchor("A Sigma_3 to two decimals (row 14, as printed)",
       ", ".join(P3[i][j] for i, j in ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))),
       "570.34, 261.83, 162.26, 363.73, 191.35, 283.54")
anchor("A Sigma_3 to one decimal (row 14)", ", ".join(fmt(AS3[i, j], 1) for i, j in ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))),
       "570.3, 261.8, 162.3, 363.7, 191.3, 283.5")
M3 = [[dec(v) for v in row] for row in P3]                             # the printed matrix, exact
same("sqrt(570.34)", f"{math.sqrt(float(M3[0][0])):.2f}", "23.88")
long_short = M3[0][0] + M3[1][1] - 2 * M3[0][1]
same("e1 - e2 form", fmt(long_short, 2), "410.41")
same("its volatility", f"{math.sqrt(float(long_short)):.2f}", "20.26")
show("long-short", "570.34+363.73-2(261.83)=410.41")
show("long-short vol", "or 20.26%")
wm = [Fr(1, 2), Fr(3, 10), Fr(1, 5)]
mix_printed = sum(wm[i] * wm[j] * M3[i][j] for i in range(3) for j in range(3))
same("mix form from printed matrix", fmt(mix_printed, 1), "320.6")
same("mix form, two decimals", fmt(mix_printed, 2), "320.63")
same("mix vol from printed matrix", f"{math.sqrt(float(mix_printed)):.2f}", "17.91")
show("mix form", "it gives 320.6, or 17.91%")

# ====================================================================================== Section 3: E2 by hand
cl_dates = smp.close_dates
idx = {d: k for k, d in enumerate(smp.dates)}
e2 = {}
for nm in ("Semiconductor", "FinancialInsurance"):
    j = names.index(nm)
    e2[nm] = [100 * X[idx[d], j] for d in ("2025-04-07", "2025-04-08", "2025-04-09")]
assert smp.dates[idx["2025-04-07"] - 1] == "2025-04-02"                 # 7 April runs from the close of 2 April
r_s = [fmt(v, 2) for v in e2["Semiconductor"]]
r_f = [fmt(v, 2) for v in e2["FinancialInsurance"]]
assert r_s == ["-9.95", "-3.99", "-4.47"] and r_f == ["-9.89", "0.53", "-5.61"], (r_s, r_f)
for v in r_s + ["-9.89", "+0.53", "-5.61"]:
    show("E2 return", f"| {v.replace('-', chr(0x2212))} |" if v != "+0.53" else "| +0.53 |")
# hand values from the printed (rounded) returns
RS = [dec(v) for v in r_s]
RF = [dec(v) for v in r_f]
ms_, mf_ = sum(RS) / 3, sum(RF) / 3
same("mean Semiconductor", fmt(ms_, 4), "-6.1367")
same("mean FinancialInsurance", fmt(mf_, 2), "-4.99")
dS = [fmt(v - ms_, 4) for v in RS]
dF = [fmt(v - mf_, 2) for v in RF]
assert dS == ["-3.8133", "2.1467", "1.6667"] and dF == ["-4.90", "5.52", "-0.62"], (dS, dF)
for v in dS + dF:
    show("E2 deviation", v)
dSp = [dec(v) for v in dS]                                              # the printed deviations
dFp = [dec(v) for v in dF]
s11 = sum(v * v for v in dSp) / 3
s12 = sum(a * b for a, b in zip(dSp, dFp)) / 3
s22 = sum(v * v for v in dFp) / 3
same("sigma_11 from printed deviations", fmt(s11, 4), "7.3092")
same("sigma_12 from printed deviations", fmt(s12, 4), "9.8339")
same("sigma_22 from printed deviations", fmt(s22, 4), "18.2883")
# and the same values from the exact means (the deviations' rounding does not move the fourth decimal)
assert fmt(sum((v - ms_) ** 2 for v in RS) / 3, 4) == "7.3092"
assert fmt(sum((a - ms_) * (b - mf_) for a, b in zip(RS, RF)) / 3, 4) == "9.8339"
rho_e2 = 9.8339 / math.sqrt(7.3092 * 18.2883)
same("rho from printed entries", f"{rho_e2:.3f}", "0.851")
# the products table of the solution: each product from the printed deviations, the means from the printed products
prods = [[fmt(a * a, 4), fmt(a * b, 4), fmt(b * b, 4)] for a, b in zip(dSp, dFp)]
assert prods == [["14.5413", "18.6852", "24.0100"], ["4.6083", "11.8498", "30.4704"], ["2.7779", "-1.0334", "0.3844"]], prods
means = [fmt(sum(dec(row[k]) for row in prods) / 3, 4) for k in range(3)]
same("means of the printed products", ", ".join(means), "7.3092, 9.8339, 18.2883")
for row in prods:
    show("E2 products", "| " + " | ".join(v.replace("-", "−") for v in row) + " |")
show("E2 means", "| 7.3092 | 9.8339 | 18.2883 |")
for v in ("=0.851", "give 0.851"):
    show("E2 result", v)
anchor("E2", f"{fmt(ms_, 4)}%, {fmt(mf_, 2)}%; {fmt(s11, 4)}, {fmt(s12, 4)}, {fmt(s22, 4)}; {rho_e2:.3f}",
       "-6.1367%, -4.99%; 7.3092, 9.8339, 18.2883; 0.851")

# ====================================================================================== Section 3: E3 and C_3
vols3 = [math.sqrt(float(M3[i][i])) for i in range(3)]
same("vols from printed matrix", ", ".join(f"{v:.2f}" for v in vols3), "23.88, 19.07, 16.84")
c3 = {}
for (i, j) in ((0, 1), (0, 2), (1, 2)):
    from_matrix = float(M3[i][j]) / math.sqrt(float(M3[i][i] * M3[j][j]))
    from_vols = float(M3[i][j]) / (round(vols3[i], 2) * round(vols3[j], 2))
    from_data = float(C[i3[i], i3[j]])
    c3[(i, j)] = f"{from_data:.3f}"
    same(f"c_{i + 1}{j + 1} from printed matrix", f"{from_matrix:.3f}", c3[(i, j)])
    same(f"c_{i + 1}{j + 1} from printed vols", f"{from_vols:.3f}", c3[(i, j)])
assert list(c3.values()) == ["0.575", "0.403", "0.596"]
anchor("C_3", ", ".join(c3.values()), "0.575, 0.403, 0.596")
anchor("S3 vols", ", ".join(f"{100 * math.sqrt(A * S3m[i, i]):.2f}" for i in range(3)), "23.88, 19.07, 16.84")
show("E3 vols", "\\sqrt{570.34}=23.88%")
show("E3 vols", "\\sqrt{363.73}=19.07%")
show("E3 vols", "\\sqrt{283.54}=16.84%")
show("E3 example", "261.83/(23.88\\times19.07)=0.575")
same("way back", f"{23.88 * 19.07 * 0.575:.2f}", "261.85")
show("E3 way back", "23.88\\times19.07\\times0.575=261.85")
show("C_3 display", "1&0.575&0.403\\\\0.575&1&0.596\\\\0.403&0.596&1")
show("full-sample correlation in E2", "give 0.575")
cmin, cmax = float(C[off].min()), float(C[off].max())
show("correlation range", f"from {cmin:.3f} to {cmax:.3f}, with mean {C[off].mean():.3f}")
anchor("correlation range (LM8, LM11)", f"{cmin:.4f}, {cmax:.4f}; {cmin:.3f}, {cmax:.3f}", "0.2175, 0.7547; 0.217, 0.755")
ordered = [names[k] for k in order]
show("heatmap order", "The first fourteen are " + ", ".join(ordered[:13]) + " and " + ordered[13] + ".")
show("heatmap order", "The last fourteen are " + ", ".join(ordered[14:27]) + " and " + ordered[27] + ".")
same("divisor factor", f"{math.sqrt(T / (T - 1)):.6f}", "1.000114")
show("divisor factor", "\\sqrt{T/(T-1)}=1.000114")
show("divisor relative change", "a relative change of 0.0114%")
anchor("divisor", f"{math.sqrt(T / (T - 1)):.6f}", "1.000114")

# ====================================================================================== Section 4: E4, X5, E5
wv = np.array([0.5, 0.3, 0.2])
cells = 1e4 * A * np.outer(wv, wv) * S3m
cell_txt = [[f"{cells[i, j]:.2f}" for j in range(3)] for i in range(3)]
for i, j in ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)):
    show("X5 cell", f"| {cell_txt[i][j]} |")
total = float(cells.sum())
same("X5 total", f"{total:.2f}", "320.62")
same("X5 printed cells sum", f"{sum(dec(cell_txt[i][j]) for i in range(3) for j in range(3)):.2f}", "320.62")
anchor("X5 cells", "; ".join(cell_txt[i][j] for i, j in ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))),
       "142.58; 39.27; 16.23; 32.74; 11.48; 11.34")
same("mix vol from printed total", f"{math.sqrt(320.62):.2f}", "17.91")
show("E4", "sum to 320.62 (%²)")
show("E4", "\\sqrt{320.62}=17.91%")
wavg = 0.5 * 23.88 + 0.3 * 19.07 + 0.2 * 16.84
same("weighted average of printed vols", f"{wavg:.2f}", "21.03")
show("E4 average", "0.5(23.88)+0.3(19.07)+0.2(16.84)=21.03%")
same("gap", f"{21.03 - 17.91:.2f}", "3.12")
show("E4 gap", "3.12 percentage points")
show("X5 note", "the nine sum to 320.62. The rounded matrix of Section 2 gives 320.63")
anchor("mix", f"{pct(math.sqrt(A * wv @ S3m @ wv))}; {pct(wv @ np.sqrt(A * np.diag(S3m)))}; {total:.2f}", "17.91%; 21.03%; 320.62")
# E5 from the printed averages
show("vbar", "\\overline{\\operatorname{var}}=2.0328\\times10^{-4}")
show("cbar", "\\overline{\\operatorname{cov}}=9.7254\\times10^{-5}")
show("off-diagonal count", "the 756 off-diagonal")
assert 28 * 27 == 756
assert sci(vbar, 4) == "2.0328\\times10^{-4}" and sci(cbar, 4) == "9.7254\\times10^{-5}"
VB, CB = Fr("2.0328e-4"), Fr("9.7254e-5")
t1, t2 = VB / 28, CB * 27 / 28
same("variance term", f"{float(t1):.3e}", "7.260e-06")
same("covariance term", f"{float(t2):.3e}", "9.378e-05")
same("daily variance from printed terms", f"{float(dec('7.260e-6') + dec('9.378e-5')):.4e}", "1.0104e-04")
show("E5 terms", "=7.260\\times10^{-6}+9.378\\times10^{-5}")
show("E5 terms", "=1.0104\\times10^{-4}")
for a_ in (A, 245.48):
    same("annualized", f"{a_ * 1.0104e-4:.6f}", "0.024803")
show("E5 annual", "As_p^2=0.024803")
same("E5 vol", pct(math.sqrt(0.024803)), "15.75%")
show("E5 vol", "\\sqrt{0.024803}=15.75%")
same("covariance share", f"{100 * 9.378 / 10.104:.1f}%", "92.8%")
show("E5 share", "9.378/10.104=92.8%")
for a_ in (A, 245.48):
    same("variance terms alone", pct(math.sqrt(a_ * 7.260e-6)), "4.22%")
    same("limit", pct(math.sqrt(a_ * 9.7254e-5)), "15.45%")
show("E5 variance terms", "\\sqrt{A\\times7.260\\times10^{-6}}=4.22%")
show("E5 limit", "\\sqrt{A\\,\\overline{\\operatorname{cov}}}=15.45%")
anchor("limit", pct(math.sqrt(A * cbar)), "15.45%")

# ====================================================================================== Section 5: E6, X6, E7
c12, c13, c23 = dec("0.575"), dec("0.403"), dec("0.596")
# the opening of Section 5: the form of the printed C_3 at (1,-1,0) and (0,1,-1); X6's first row quotes both
C3p = [[Fr(1), c12, c13], [c12, Fr(1), c23], [c13, c23, Fr(1)]]
for xv_, txt in (([1, -1, 0], "2-2(0.575)=0.85"), ([0, 1, -1], "2-2(0.596)=0.808")):
    val = sum(xv_[i] * C3p[i][j] * xv_[j] for i in range(3) for j in range(3))
    same(f"x'C_3x at {xv_}", fmt(val, 3 if "808" in txt else 2), txt.split("=")[1])
    show("Section 5 opening", txt)
show("X6 first row", "0.85 and 0.808 at the two vectors tried")
m2 = 1 - c12**2
m3 = 1 + 2 * c12 * c13 * c23 - c12**2 - c13**2 - c23**2
same("C_3 minor 2", fmt(m2, 6), "0.669375")
same("C_3 det", fmt(m3, 6), "0.427966")
same("C_3 pivot 2", fmt(m2, 4), "0.6694")
same("C_3 pivot 3", fmt(m3 / m2, 4), "0.6394")
same("C_3 pivot 3 from printed minors", fmt(dec("0.427966") / dec("0.669375"), 4), "0.6394")
assert all(v > 0 for v in (1 - c12**2, 1 - c13**2, 1 - c23**2, m3))     # all seven principal minors positive
show("E6 minor", "1-0.575^2=0.669375")
show("E6 det", "=0.427966")
show("E6 pivots", "0.669375/1=0.6694")
show("E6 pivots", "0.427966/0.669375=0.6394")
show("X6 minors", "1, 0.669375, 0.427966: PD")
show("X6 pivots", "1, 0.6694, 0.6394: PD")
anchor("C_3 minors and pivots", f"1, {fmt(m2, 6)}, {fmt(m3, 6)}; 1, {fmt(m2, 4)}, {fmt(m3 / m2, 4)}",
       "1, 0.669375, 0.427966; 1, 0.6694, 0.6394")
# E7 (b): the Semiconductor / FinancialInsurance block rounded to whole %^2, plus the 50/50 mix
a11, a12, a22 = round(float(M3[0][0])), round(float(M3[0][1])), round(float(M3[1][1]))
assert (a11, a12, a22) == (570, 262, 364)
E7 = [[Fr(a11), Fr(a12), Fr(a11 + a12, 2)], [Fr(a12), Fr(a22), Fr(a12 + a22, 2)],
      [Fr(a11 + a12, 2), Fr(a12 + a22, 2), Fr(a11, 4) + Fr(a12, 2) + Fr(a22, 4)]]
same("E7 third row", ", ".join(fmt(v, 1) for v in E7[2]), "416.0, 313.0, 364.5")
mins2 = [E7[0][0] * E7[1][1] - E7[0][1] ** 2, E7[0][0] * E7[2][2] - E7[0][2] ** 2, E7[1][1] * E7[2][2] - E7[1][2] ** 2]
same("E7 2x2 minors", ", ".join(thousands(fmt(v, 0)) for v in mins2), "138,836, 34,709, 34,709")
assert mins2[1] == mins2[2] == mins2[0] / 4 and det3(E7) == 0
xnull = [Fr(1, 2), Fr(1, 2), Fr(-1)]
assert sum(xnull[i] * E7[i][j] * xnull[j] for i in range(3) for j in range(3)) == 0
show("E7 minors", "570(364)-262^2=138,836")
show("E7 minors", "570(364.5)-416^2=34,709")
show("E7 minors", "364(364.5)-313^2=34,709")
show("E7 matrix", "570&262&416\\\\262&364&313\\\\416&313&364.5")
show("E7 variance rule", "\\tfrac14(570)+\\tfrac12(262)+\\tfrac14(364)")
anchor("E7 from the block in whole %² (row 21, the module's construction)",
       f"{', '.join(plain(v) for v in E7[2])}; {', '.join(plain(v, True) for v in mins2)}; det {plain(det3(E7))}",
       "416, 313, 364.5; 138,836, 34,709, 34,709; det 0")
# row 21's value: the same construction from the block to one decimal (570.3, 261.8, 363.7)
b11, b12, b22 = (dec(fmt(AS3[i, j], 1)) for i, j in ((0, 0), (0, 1), (1, 1)))
E7a = [[b11, b12, (b11 + b12) / 2], [b12, b22, (b12 + b22) / 2],
       [(b11 + b12) / 2, (b12 + b22) / 2, b11 / 4 + b12 / 2 + b22 / 4]]
mins2a = [E7a[0][0] * E7a[1][1] - E7a[0][1] ** 2, E7a[0][0] * E7a[2][2] - E7a[0][2] ** 2,
          E7a[1][1] * E7a[2][2] - E7a[1][2] ** 2]
anchor("E7 from the block to one decimal (row 21's value)",
       f"{', '.join(plain(v) for v in E7a[2])}; {', '.join(plain(v, True) for v in mins2a)}; det {plain(det3(E7a))}",
       "416.05, 312.75, 364.4; 138,878.87, 34,719.7175, 34,719.7175; det 0")
# the computed 50/50 matrix, rounded to one decimal (pitfall of Section 6)
mix50 = 0.5 * X[:, i3[0]] + 0.5 * X[:, i3[1]]
S_mix = 1e4 * A * cov0(np.column_stack([X[:, i3[0]], X[:, i3[1]], mix50]))
R1 = [[Fr(fmt(S_mix[i, j], 1)) for j in range(3)] for i in range(3)]
upper = [fmt(S_mix[i, j], 1) for i, j in ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))]
assert upper == ["570.3", "261.8", "416.1", "363.7", "312.8", "364.4"], upper
show("rounding pitfall entries", "upper triangle reads 570.3, 261.8, 416.1; 363.7, 312.8; 364.4")
d_r1 = det3(R1)
d_printed = det3([[dec("570.3"), dec("261.8"), dec("416.1")], [dec("261.8"), dec("363.7"), dec("312.8")],
                  [dec("416.1"), dec("312.8"), dec("364.4")]])
same("det of the computed 50/50 matrix rounded to 0.1", thousands(fmt(d_r1, 2)), "-13,888.91")
same("det from the printed upper triangle", thousands(fmt(d_printed, 2)), "-13,888.91")
show("rounding pitfall", "Its determinant is then $-13,888.91$")
anchor("E7 rounded", thousands(fmt(d_r1, 2)), "-13,888.91")
# in daily %^2 the same rounding keeps the matrix exactly singular (A2's evidence; the text names its units instead)
daily = 1e4 * cov0(np.column_stack([X[:, i3[0]], X[:, i3[1]], mix50]))
assert det3([[Fr(fmt(daily[i, j], 1)) for j in range(3)] for i in range(3)]) == 0

# ====================================================================================== Section 6: rank, collinearity
ranks = {}
for TT in range(20, 36):
    ranks[TT] = int(np.linalg.matrix_rank(cov0(X[-TT:])))
    assert ranks[TT] == min(TT - 1, 28), (TT, ranks[TT])                # (10.7), and the bound is reached
assert smp.dates[-28] == "2026-08-28" and smp.dates[-29] == "2026-08-27"
show("E8", "On the latest 28 returns, from 28 August to 8 October 2026, the rank is 27")
show("E8", "On the latest 29, from 27 August, it is 28")
anchor("rank windows", f"T=28: {ranks[28]} from {smp.dates[-28]}; T=29: {ranks[29]} from {smp.dates[-29]}",
       "T=28: 27 from 2026-08-28; T=29: 28 from 2026-08-27")
i5 = [names.index(n) for n in S5]
X6 = np.column_stack([X[:, i5], X[:, i5].mean(axis=1)])
S6 = cov0(X6)
xv = np.array([0.2] * 5 + [-1.0])
assert int(np.linalg.matrix_rank(S6)) == 5 and abs(float(xv @ S6 @ xv)) < 1e-15
show("collinear", "The $6\\times6$ matrix has rank 5")
show("residue", "below $10^{-15}$")
# the exact zeros of the pitfall's 50/50 matrix in %² (x'Mx at (0.5, 0.5, -1), and det) come out far above 10^-15:
# its entries sit on a floating-point grid with spacing above 10^-14. The residues differ between machines and are
# never printed in the module.
x50 = np.array([0.5, 0.5, -1.0])
res50 = (abs(float(x50 @ S_mix @ x50)), abs(float(np.linalg.det(S_mix))))
print(f"residues of the 50/50 matrix in %^2: x'Mx {res50[0]:.1e}, det {res50[1]:.1e}")
assert max(res50) > 1e-15 and float(np.spacing(np.abs(S_mix)).min()) > 1e-14
show("residue, two matrices", r"below $10^{-15}$ for the daily $6\times6$ matrix above, larger for the 50/50 matrix in %²")

# ====================================================================================== Section 6: pairwise deletion, real case
etf = {e: one_session(e, smp.calendar) for e in ETFS}
cols = names + ETFS
n = len(cols)
Z = np.full((T, n), np.nan)
Z[:, :28] = X
for j, e in enumerate(ETFS):
    Z[:, 28 + j] = [etf[e].get(d, np.nan) for d in smp.dates]
ok = ~np.isnan(Z)
cnt = np.zeros((n, n), dtype=int)
Cp, Sp = np.eye(n), np.zeros((n, n))
for i in range(n):
    Sp[i, i] = float(Z[ok[:, i], i].var())
    cnt[i, i] = int(ok[:, i].sum())
    for j in range(i + 1, n):
        m = ok[:, i] & ok[:, j]
        u_, v_ = Z[m, i], Z[m, j]
        cnt[i, j] = cnt[j, i] = int(m.sum())
        Cp[i, j] = Cp[j, i] = float(np.corrcoef(u_, v_)[0, 1])
        Sp[i, j] = Sp[j, i] = float(np.mean((u_ - u_.mean()) * (v_ - v_.mean())))
allm = ok.all(axis=1)
Zc = Z[allm]
Sc, Cc = cov0(Zc), np.corrcoef(Zc.T)
common_dates = [d for d, f in zip(smp.dates, allm) if f]
assert int(allm.sum()) == 2357 and common_dates[0] == "2017-01-18"
assert min(etf["00679B"]) == "2017-01-18"
offc = cnt[np.triu_indices(n, 1)]
show("common sample", "2,357 returns from 18 January 2017")
show("pairwise counts", f"from {offc.min():,} to {offc.max():,}")
show("X8a counts", f"| {offc.min():,} to {offc.max():,} |")
piv = {k: pivots(M_) for k, M_ in (("Cp", Cp), ("Sp", Sp), ("Cc", Cc), ("Sc", Sc))}
assert len(piv["Cp"]) == n and piv["Cp"].min() > 0                       # pairwise C: PD by the pivot test
assert len(piv["Cc"]) == n and piv["Cc"].min() > 0 and len(piv["Sc"]) == n and piv["Sc"].min() > 0
k_neg = len(piv["Sp"])
assert k_neg == 29 and piv["Sp"][-1] < 0 and cols[k_neg - 1] == "0050"
show("negative pivot", f"d_{{29}}={sci(float(piv['Sp'][-1]), 2)}")
show("negative pivot step", "a negative pivot at step 29, the 0050 column")
show("X8a", "not PSD: pivot 29 is negative")
show("X8a", "PD: 31 positive pivots")
# the most negative unit direction (LM11's eigenvector, sign rule): printed as a book, not as an eigenpair
ev, evec = np.linalg.eigh(Sp)
q = evec[:, 0] * np.sign(evec[int(np.argmax(np.abs(evec[:, 0]))), 0])
assert int((ev < 0).sum()) == 1
top = sorted(range(n), key=lambda k: -abs(q[k]))[:3]
assert [cols[k] for k in top] == ["Semiconductor", "00631L", "0050"]
show("witness entries", f"{q[top[0]]:.3f} in Semiconductor, {q[top[1]]:.3f} in 00631L, {q[top[2]]:.3f} in 0050".replace("-", "\u2212"))
show("witness form", f"\\mathbf x^{{\\top}}\\hat\\Sigma_{{\\text{{pw}}}}\\mathbf x={sci(float(q @ Sp @ q), 2)}")
assert abs(float(q @ Sp @ q) - float(ev[0])) < 1e-18
anchor("pairwise eigen", f"C {np.linalg.eigvalsh(Cp)[0]:.5f}; Sigma {ev[0]:.2e}; common C {np.linalg.eigvalsh(Cc)[0]:.5f}, Sigma {np.linalg.eigvalsh(Sc)[0]:.2e}",
       "C 0.01380; Sigma -6.56e-06; common C 0.01337, Sigma 3.55e-06")
signs = {}
for j, e in enumerate(ETFS):
    idx_ = list(range(28)) + [28 + j]
    p_ = pivots(Sp[np.ix_(idx_, idx_)])
    signs[e] = bool(len(p_) == 29 and p_.min() > 0)
    assert signs[e] == (np.linalg.eigvalsh(Sp[np.ix_(idx_, idx_)])[0] > 0)
assert signs == {"0050": False, "00631L": False, "00679B": True}
show("one ETF at a time", "Adding 0050 alone or 00631L alone to U28 already breaks the matrix; adding 00679B alone does not")
iS = names.index("Semiconductor")
m631 = ok[:, 28 + ETFS.index("00631L")]
show("Semiconductor variance", sci(float(Sp[iS, iS]), 4))
show("Semiconductor variance on 00631L dates", sci(float(Z[m631, iS].var()), 4))
show("00631L dates", f"on 00631L's {int(m631.sum()):,} dates")
show("Semiconductor variance, common sample", f"{sci(float(Zc[:, iS].var()), 4)}$, on the 2,357 common dates")
show("Semiconductor variance, all returns", f"{sci(float(Sp[iS, iS]), 4)}$, on all 4,382 returns")
assert abs(float(Sc[iS, iS]) - float(Zc[:, iS].var())) < 1e-18
anchor("Semiconductor variance", f"{Sp[iS, iS]:.4e} vs {Z[m631, iS].var():.4e} ({int(m631.sum())})", "2.3234e-04 vs 2.5076e-04 (2906)")
# the correlation that the pairwise Sigma-hat implies between Semiconductor and 00631L, against the pairwise one
i631 = 28 + ETFS.index("00631L")
assert cnt[iS, i631] == cnt[i631, i631] == int(m631.sum())                # the pair's dates are all of 00631L's dates
implied = Sp[iS, i631] / math.sqrt(Sp[iS, iS] * Sp[i631, i631])
ratio = implied / Cp[iS, i631]
assert abs(ratio - math.sqrt(Z[m631, iS].var() / Sp[iS, iS])) < 1e-12
same("implied / pairwise correlation", f"{ratio:.3f}", "1.039")
same("ratio from printed variances", f"{math.sqrt(2.5076 / 2.3234):.3f}", "1.039")
show("implied correlation factor", "\\sqrt{2.5076/2.3234}=1.039")
print(f"Semiconductor/00631L: pairwise correlation {Cp[iS, i631]:.4f}, implied by the pairwise Sigma-hat {implied:.4f}")
dC = np.abs(Cp - Cc)
kk = np.unravel_index(int(np.argmax(dC)), dC.shape)
pair = sorted([cols[kk[0]], cols[kk[1]]])
assert pair == ["ElectronicProductsDistribution", "TradingConsumersGoods"]
show("largest change", f"by as much as {dC[kk]:.3f}")
show("largest change pair", f"correlate at {Cp[kk]:.3f} on all dates but at {Cc[kk]:.3f} from 2017")
# what the common sample drops: every return before 18 January 2017, and the dates around two ETF halts
before = [d for d in smp.dates if d < common_dates[0]]
assert before[0] == "2008-12-02" and before[-1] == "2017-01-17"
halt = [d for d in smp.dates if d >= common_dates[0] and d not in set(common_dates)]
assert len(halt) == 11 and len(before) + len(halt) + 2357 == T
assert [d for d in halt if d not in etf["0050"]] == [d for d in halt if d.startswith("2025-06")]      # 6 dates
assert [d for d in halt if d not in etf["00631L"]] == [d for d in halt if d.startswith("2026-03")]    # 5 dates
assert all(d in etf["00679B"] for d in halt)
show("common sample drops", "It drops the returns from 2 December 2008 to 17 January 2017, and 11 dates around the "
     "trading halts of 0050 (June 2025) and 00631L (March 2026)")

# ====================================================================================== Section 6: E9 (constructed)
pairs = [("0050", "00631L"), ("0050", "00679B"), ("00631L", "00679B")]
tab: dict[tuple[tuple[str, str], int], tuple[float, int]] = {}
for p_ in pairs:
    ds = sorted(set(etf[p_[0]]) & set(etf[p_[1]]))
    a_ = np.array([etf[p_[0]][d] for d in ds])
    b_ = np.array([etf[p_[1]][d] for d in ds])
    yr = np.array([int(d[:4]) for d in ds])
    for Y in range(2017, 2027):
        mk = yr == Y
        tab[(p_, Y)] = (float(np.corrcoef(a_[mk], b_[mk])[0, 1]), int(mk.sum()))
choice = {pairs[0]: 2018, pairs[1]: 2023, pairs[2]: 2019}
rv = {p_: f"{tab[(p_, y)][0]:.3f}" for p_, y in choice.items()}
tv = {p_: tab[(p_, y)][1] for p_, y in choice.items()}
assert list(rv.values()) == ["0.982", "0.199", "-0.444"] and list(tv.values()) == [247, 239, 242]
print("per-year pair correlations (one-session total returns):")
for p_ in pairs:
    print("   ", "/".join(p_), " ".join(f"{Y}:{tab[(p_, Y)][0]:+.3f}({tab[(p_, Y)][1]})" for Y in range(2017, 2027)))
show("E9 rho", "\\rho_{12}=0.982")
show("E9 rho", "\\rho_{13}=0.199")
show("E9 rho", "\\rho_{23}=-0.444")
for p_ in pairs:
    show("X8 row", f"| {choice[p_]} | {tv[p_]} | {rv[p_].replace('-', chr(0x2212))} |")
r12, r13, r23 = dec("0.982"), dec("0.199"), dec("-0.444")
detC = 1 + 2 * r12 * r13 * r23 - r12**2 - r13**2 - r23**2
same("E9 det from printed", fmt(detC, 6), "-0.374592")
show("E9 det", "=-0.374592<0")
form = 3 + 2 * (-r12 - r13 + r23)
assert form == Fr(-1, 4)
show("E9 form", "3+2(-0.982-0.199-0.444)")
show("E9 form", "=-0.25")
adj = [1 - r23**2, 1 - r13**2, 1 - r12**2]
same("adjugate diagonal", ", ".join(fmt(v, 6) for v in adj), "0.802864, 0.960399, 0.035676")
same("witnesses", ", ".join(fmt(detC * v, 4) for v in adj), "-0.3007, -0.3598, -0.0134")
same("witnesses from printed det", ", ".join(fmt(dec("-0.374592") * v, 4) for v in adj), "-0.3007, -0.3598, -0.0134")
show("P7 minors", "1-0.444^2=0.802864")
show("P7 minors", "1-0.199^2=0.960399")
show("P7 minors", "1-0.982^2=0.035676")
show("P7 values", "-0.3007, -0.3598 and -0.0134")
anchor("witnesses", ", ".join(fmt(detC * v, 4) for v in adj), "-0.3007, -0.3598, -0.0134")
# 2018 on the dates all three traded
d18 = [d for d in sorted(set(etf["0050"]) & set(etf["00631L"]) & set(etf["00679B"])) if d.startswith("2018")]
M18 = np.array([[etf[e][d] for e in ETFS] for d in d18])
C18 = np.corrcoef(M18.T)
c18 = [f"{C18[0, 1]:.3f}", f"{C18[0, 2]:.3f}", f"{C18[1, 2]:.3f}"]
assert len(d18) == 247 and c18 == ["0.982", "-0.394", "-0.395"]
det18 = det3([[Fr(1), dec(c18[0]), dec(c18[1])], [dec(c18[0]), Fr(1), dec(c18[2])], [dec(c18[1]), dec(c18[2]), Fr(1)]])
same("2018 det from printed", fmt(det18, 4), "0.0301")
show("E9 2018", "give 0.982, -0.394 and -0.395, and then $\\det C=0.0301>0")
fails = 0
for y1, y2, y3 in permutations(range(2017, 2027), 3):
    p, q_, r = tab[(pairs[0], y1)][0], tab[(pairs[1], y2)][0], tab[(pairs[2], y3)][0]
    d_full = 1 + 2 * p * q_ * r - p * p - q_ * q_ - r * r
    p3, q3, r3_ = round(p, 3), round(q_, 3), round(r, 3)
    d_3 = 1 + 2 * p3 * q3 * r3_ - p3 * p3 - q3 * q3 - r3_ * r3_
    assert (d_full < 0) == (d_3 < 0)
    fails += d_full < 0
assert fails == 362
show("failing assignments", "Of the 720 ways")
show("failing assignments", "362 produce a negative determinant")
# the calendar years are partial at both ends: 00679B's first return and the sample's last date
assert min(etf["00679B"]) == "2017-01-18" and min(etf["0050"]) < "2017-01-03" and min(etf["00631L"]) < "2017-01-03"
assert max(max(etf[e]) for e in ETFS) == "2026-10-08"
show("partial years", "Here 00679B's 2017 starts on 18 January, and 2026 runs to 8 October.")
show("X8 ellipse", "\\rho_{13}^2-2(0.982)\\rho_{13}\\rho_{23}+\\rho_{23}^2\\le1-0.982^2")
# the constructed point lies outside the ellipse, the 2018 point inside
assert float(r13**2 - 2 * r12 * r13 * r23 + r23**2) > 1 - 0.982**2
assert float(dec(c18[1]) ** 2 - 2 * r12 * dec(c18[1]) * dec(c18[2]) + dec(c18[2]) ** 2) < 1 - 0.982**2

# ====================================================================================== Section 7: E10
g = 2 * A * S @ w
iG, iC = names.index("GlassCeramic"), names.index("CommunicationsInternet")
assert int(np.argmax(g)) == iG and int(np.argmin(g)) == iC
show("E10 gradient", f"The GlassCeramic entry of the gradient is {g[iG]:.6f}")
show("E10 gradient", f"the CommunicationsInternet entry is {g[iC]:.6f}")
Dl = np.zeros(28)
Dl[iC], Dl[iG] = 1 / 28, -1 / 28
lin, quad = float(Dl @ g), float(A * Dl @ S @ Dl)
v0, v1 = A * sp2, float(A * (w + Dl) @ S @ (w + Dl))
assert abs(v0 + lin + quad - v1) < 1e-15                               # (10.9) is exact
P_ = {k: f"{val:.7f}" for k, val in (("v0", v0), ("lin", lin), ("quad", quad), ("v1", v1))}
same("linear term from printed gradient", fmt((dec(f"{g[iC]:.6f}") - dec(f"{g[iG]:.6f}")) / 28, 7), P_["lin"])
same("printed parts add up", fmt(dec(P_["v0"]) + dec(P_["lin"]) + dec(P_["quad"]), 7), P_["v1"])
show("E10 linear", f"$$\\begin{{aligned}}2A\\boldsymbol\\Delta^{{\\top}}\\hat\\Sigma\\mathbf w&=\\frac{{{g[iC]:.6f}-{g[iG]:.6f}}}{{28}}"
                  f"\\\\&={P_['lin']}.\\end{{aligned}}$$")
show("E10 quadratic", f"=+{P_['quad']}")
show("E10 sum", f"variance of {P_['v0']} becomes")
show("E10 sum", f"&{P_['v0']}{P_['lin']}+{P_['quad']}")
show("E10 sum", f"&={P_['v1']}")
same("E10 vol before", pct(math.sqrt(float(P_["v0"]))), "15.75%")
same("E10 vol after", pct(math.sqrt(float(P_["v1"]))), "15.28%")
same("E10 linear only", pct(math.sqrt(float(dec(P_["v0"]) + dec(P_["lin"])))), "15.23%")
show("E10 vols", "the sample volatility would have fallen from 15.75% to 15.28%")
show("E10 linear only", "would give 15.23%")
show("overview", "would have cut its 2008–2026 sample volatility from 15.75% to 15.28%")
anchor("E10", f"{g[iG]:.5f}, {g[iC]:.5f}; {lin:.6f}; {quad:+.6f}; {v0:.6f} -> {v1:.6f}; {pct(math.sqrt(v0))} -> {pct(math.sqrt(v1))}",
       "0.07230, 0.02764; -0.001595; +0.000136; 0.024803 -> 0.023345; 15.75% -> 15.28%")

# ====================================================================================== Practice problems
# P3
show("P3", "\\min(28,\\,20-1)=19")
# P4: rebuild from printed C_3 and printed volatilities
vp = [dec("23.88"), dec("19.07"), dec("16.84")]
cp = {(0, 1): dec("0.575"), (0, 2): dec("0.403"), (1, 2): dec("0.596")}
R4 = [[vp[i] * vp[j] * (Fr(1) if i == j else cp[(min(i, j), max(i, j))]) for j in range(3)] for i in range(3)]
p4 = [fmt(R4[i][j], 2) for i, j in ((0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2))]
assert p4 == ["570.25", "363.66", "283.59", "261.85", "162.06", "191.40"], p4
w4 = [Fr(1, 5), Fr(3, 10), Fr(1, 2)]
v4 = sum(w4[i] * w4[j] * R4[i][j] for i in range(3) for j in range(3))
same("P4 variance", fmt(v4, 2), "247.69")
same("P4 vol", f"{math.sqrt(float(v4)):.2f}", "15.74")
same("P4 vol from printed variance", f"{math.sqrt(247.69):.2f}", "15.74")
R4p = {(i, j): dec(p4[k]) for k, (i, j) in enumerate(((0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2)))}
v4p = sum(w4[i] * w4[j] * R4p[(min(i, j), max(i, j))] for i in range(3) for j in range(3))
same("P4 variance from the printed (rounded) entries", fmt(v4p, 2), "247.69")
v4_data = math.sqrt(1e4 * A * np.array([0.2, 0.3, 0.5]) @ S3m @ np.array([0.2, 0.3, 0.5]))
print(f"P4 on the unrounded matrix: {v4_data:.4f}% (printed answer 15.74%)")
for t in ("23.88^2=570.25", "19.07^2=363.66", "16.84^2=283.59", "23.88\\times19.07\\times0.575=261.85",
          "23.88\\times16.84\\times0.403=162.06", "19.07\\times16.84\\times0.596=191.40", "=247.69", "\\sqrt{247.69}=15.74%"):
    show("P4", t)
anchor("P4", "15.74%", "15.74%")
# P5: S5 averages, printed
S5m = cov0(X[:, i5])
vb5, cb5 = float(np.mean(np.diag(S5m))), float(S5m[~np.eye(5, dtype=bool)].mean())
assert sci(vb5, 4) == "2.0740\\times10^{-4}" and sci(cb5, 4) == "9.0696\\times10^{-5}"
show("P5 vbar", "\\overline{\\operatorname{var}}=2.0740\\times10^{-4}")
show("P5 cbar", "\\overline{\\operatorname{cov}}=9.0696\\times10^{-5}")
sp5 = Fr("2.0740e-4") / 5 + Fr(4, 5) * Fr("9.0696e-5")
same("P5 variance term", f"{float(Fr('2.0740e-4') / 5):.4e}", "4.1480e-05")
same("P5 covariance term", f"{float(Fr(4, 5) * Fr('9.0696e-5')):.4e}", "7.2557e-05")
same("P5 daily variance", f"{float(sp5):.5e}", "1.14037e-04")
same("P5 daily variance from printed terms", f"{float(Fr('4.1480e-5') + Fr('7.2557e-5')):.5e}", "1.14037e-04")
same("P5 annual from printed", f"{245.48 * 1.14037e-4:.6f}", "0.027994")
same("P5 annual, full A", f"{A * float(sp5):.6f}", "0.027994")
same("P5 vol", pct(math.sqrt(0.027994)), "16.73%")
same("P5 limit", pct(math.sqrt(245.48 * 9.0696e-5)), "14.92%")
same("P5 limit, full A", pct(math.sqrt(A * 9.0696e-5)), "14.92%")
same("P5 gaps", f"{16.73 - 14.92:.2f}, {15.75 - 15.45:.2f}", "1.81, 0.30")
for t in ("=4.1480\\times10^{-5}+7.2557\\times10^{-5}", "=1.14037\\times10^{-4}", "245.48\\times1.14037\\times10^{-4}=0.027994",
          "a volatility of 16.73%", "\\sqrt{245.48\\times9.0696\\times10^{-5}}=14.92%", "1.81 points above",
          "0.30 points above"):
    show("P5", t)
anchor("P5", f"{vb5:.4e}, {cb5:.4e}; {pct(math.sqrt(A * np.full(5, 0.2) @ S5m @ np.full(5, 0.2)))}; {pct(math.sqrt(A * cb5))}",
       "2.0740e-04, 9.0696e-05; 16.73%; 14.92%")
# P6: pivots of the printed matrix (two decimals) by elimination without row exchanges, as the editor decided
k22 = M3[1][1] - M3[0][1] ** 2 / M3[0][0]                                 # exact rationals from the printed entries
k23 = M3[1][2] - M3[0][1] * M3[0][2] / M3[0][0]
k33 = M3[2][2] - M3[0][2] ** 2 / M3[0][0]
P6 = {"k22": fmt(k22, 4), "k23": fmt(k23, 4), "k33": fmt(k33, 4), "d3x": fmt(k33 - k23**2 / k22, 4)}
assert P6 == {"k22": "243.5299", "k23": "116.8602", "k33": "237.3775", "d3x": "181.3010"}, P6
# from the printed four-decimal block the third pivot is the same; so are two-decimal intermediates
same("P6 d3 from the printed block", fmt(dec(P6["k33"]) - dec(P6["k23"]) ** 2 / dec(P6["k22"]), 4), P6["d3x"])
same("P6 d3 from two-decimal intermediates", fmt(dec("237.38") - dec("116.86") ** 2 / dec("243.53"), 2), "181.30")
piv3 = pivots(np.array([[float(v) for v in row] for row in M3]))
same("P6 pivots by float elimination", f"{piv3[0]:.2f}, {piv3[1]:.2f}, {piv3[2]:.2f}", "570.34, 243.53, 181.30")
same("P6 pivots from the printed values", f"{fmt(dec(P6['k22']), 2)}, {fmt(dec(P6['d3x']), 2)}", "243.53, 181.30")
assert k22 > 0 and k33 - k23**2 / k22 > 0                                # all pivots positive: PD (test 3)
assert fmt(M3[0][0] * k22 * (k33 - k23**2 / k22), 2) == fmt(det3(M3), 2)  # their product is det, never printed
print("P6 (printed matrix):", P6)
show("P6 d1", "The first pivot is $d_1=570.34$")
show("P6 elimination", "Subtract $261.83/570.34$ times row 1 from row 2, and $162.26/570.34$ times row 1 from row 3")
show("P6 rule", "k_{ij}=m_{ij}-m_{i1}m_{1j}/570.34")
show("P6 K", f"K=\\begin{{pmatrix}}{P6['k22']}&{P6['k23']}\\\\{P6['k23']}&{P6['k33']}\\end{{pmatrix}}")
show("P6 k22 example", "k_{22}=363.73-261.83^2/570.34")
show("P6 d2", f"So $d_2={P6['k22']}$")
show("P6 d3", f"$$d_3={P6['k33']}-\\frac{{{P6['k23']}^2}}{{{P6['k22']}}}={P6['d3x']}.$$")
show("P6 pivots", "The pivots 570.34, 243.53 and 181.30 are all positive")
anchor("P6 pivots (row 34, the printed two-decimal matrix)",
       f"{fmt(M3[0][0], 2)}, {fmt(k22, 2)}, {fmt(k33 - k23**2 / k22, 2)} "
       f"(after step 1: {P6['k22']}, {P6['k23']}, {P6['k33']})",
       "570.34, 243.53, 181.30 (after step 1: 243.5299, 116.8602, 237.3775)")
# P9: five points from Semiconductor to Food, printed matrix in decimal units
Md = [[v / 10**4 for v in row] for row in M3]
w9 = [Fr(1, 2), Fr(3, 10), Fr(1, 5)]
d9 = [Fr(-1, 20), Fr(0), Fr(1, 20)]
g9 = [2 * sum(Md[i][j] * w9[j] for j in range(3)) for i in range(3)]
g9p = [fmt(v, 5) for v in g9]
lin9 = sum(d9[i] * g9[i] for i in range(3))
quad9 = sum(d9[i] * Md[i][j] * d9[j] for i in range(3) for j in range(3))
var9 = sum(w9[i] * Md[i][j] * w9[j] for i in range(3) for j in range(3))
new9 = var9 + lin9 + quad9
assert new9 == sum((w9[i] + d9[i]) * Md[i][j] * (w9[j] + d9[j]) for i in range(3) for j in range(3))
P9 = {"lin": fmt(lin9, 6), "quad": fmt(quad9, 6), "v0": fmt(var9, 6), "v1": fmt(new9, 6)}
print("P9:", g9p, P9)
same("P9 linear from printed gradient", fmt(sum(d9[i] * dec(g9p[i]) for i in range(3)), 6), P9["lin"])
same("P9 parts add up", fmt(dec(P9["v0"]) + dec(P9["lin"]) + dec(P9["quad"]), 6), P9["v1"])
same("P9 vols", f"{pct(math.sqrt(float(dec(P9['v0']))))} -> {pct(math.sqrt(float(dec(P9['v1']))))}", "17.91% -> 17.37%")
same("P9 quadratic from printed entries", fmt(Fr(1, 400) * (dec("0.057034") + dec("0.028354") - 2 * dec("0.016226")), 6), P9["quad"])
show("P9 gradient", f"2A\\hat\\Sigma_3\\mathbf w=({g9p[0]},\\,{g9p[1]},\\,{g9p[2]})")
show("P9 linear", f"$$0.05\\,({g9p[2]}-{g9p[0]})={P9['lin']},$$")
show("P9 quadratic", f"&0.05^2\\,(0.057034+0.028354\\\\&\\quad-2\\times0.016226)=+{P9['quad']}")
show("P9 variance", f"So the variance moves from {P9['v0']} to")
show("P9 variance", f"$$\\begin{{aligned}}&{P9['v0']}{P9['lin']}+{P9['quad']}\\\\&={P9['v1']},\\end{{aligned}}$$")
show("P9 vols", "the volatility falls from 17.91% to 17.37%")
assert (dec("0.057034"), dec("0.028354"), dec("0.016226")) == (M3[0][0] / 10**4, M3[2][2] / 10**4, M3[0][2] / 10**4)
anchor("P9 (row 35, the printed two-decimal matrix)",
       f"{', '.join(g9p)}; {P9['lin']}; +{P9['quad']}; {P9['v0']} -> {P9['v1']}; "
       f"{pct(math.sqrt(float(dec(P9['v0']))))} -> {pct(math.sqrt(float(dec(P9['v1']))))}",
       "0.07923, 0.05566, 0.03905; -0.002009; +0.000132; 0.032063 -> 0.030186; 17.91% -> 17.37%")
# row 35's notes: the matrix to one decimal (row 14) gives 0.032060 -> 0.030184, and the mix's 320.60 %² beside the
# two-decimal matrix's 320.63 and the computed matrix's 320.62 (row 17, the total of the nine terms)
M1d = [[dec(fmt(AS3[i, j], 1)) / 10**4 for j in range(3)] for i in range(3)]
var9a = sum(w9[i] * M1d[i][j] * w9[j] for i in range(3) for j in range(3))
new9a = sum((w9[i] + d9[i]) * M1d[i][j] * (w9[j] + d9[j]) for i in range(3) for j in range(3))
anchor("P9 on the one-decimal matrix (row 35's note)", f"{fmt(var9a, 6)} -> {fmt(new9a, 6)}", "0.032060 -> 0.030184")
anchor("mix in %² from the two-decimal, one-decimal and computed matrices (row 35's note)",
       f"{fmt(var9 * 10**4, 2)}, {fmt(var9a * 10**4, 2)}, {total:.2f}", "320.63, 320.60, 320.62")
# P11: S5 three ways, the ddof effect
X5 = X[:, i5]
Xc5 = X5 - X5.mean(axis=0)
Sa, Sb = Xc5.T @ Xc5 / T, np.cov(X5, rowvar=False, ddof=0)
Sc5 = sum(np.outer(r, r) for r in Xc5) / T
assert max(np.abs(Sa - Sb).max(), np.abs(Sa - Sc5).max()) < 1e-15
w5 = np.full(5, 0.2)
assert abs(float(np.var(X5 @ w5)) - float(w5 @ Sa @ w5)) < 1e-15
v5, v5d = math.sqrt(A * float(np.var(X5 @ w5))), math.sqrt(A * float(np.var(X5 @ w5, ddof=1)))
same("P11 ratio", f"{v5d / v5:.6f}", "1.000114")
P11 = {"v0": f"{100 * v5:.4f}%", "v1": f"{100 * v5d:.4f}%", "gap": f"{100 * (v5d - v5):.4f}"}
print("P11:", P11)
show("P11", f"from {P11['v0']} to {P11['v1']}")

# ====================================================================================== hand examples (exact arithmetic)
def form2(m: list[list[Fr]], x: list[Fr]) -> Fr:
    """The quadratic form x'Mx in exact arithmetic."""
    return sum((x[i] * m[i][j] * x[j] for i in range(len(x)) for j in range(len(x))), Fr(0))


# E1 and the Section 2 knowledge check
M1 = [[Fr(1), Fr(4)], [Fr(0), Fr(1)]]
assert form2(M1, [Fr(1), Fr(-1)]) == -2 and Fr(1) * 1 - Fr(2) ** 2 == -3
show("E1", "h(1,-1)=1-4+1=-2<0")
show("E1", "\\det M_{\\text{sym}}=1-4=-3<0")
assert form2([[Fr(3), Fr(-2)], [Fr(-2), Fr(1)]], [Fr(1), Fr(2)]) == -1 and 3 * 1 - 4 == -1
show("KC 2", "h(1,2)=3-8+4=-1")
# Section 4 knowledge check: two assets, variances 4 and 1, covariance -1 (%^2)
Mk = [[Fr(4), Fr(-1)], [Fr(-1), Fr(1)]]
for wk, v_, sp_, bound in (([Fr(1, 5), Fr(4, 5)], "0.48", "0.69", "1.2"), ([Fr(1, 2), Fr(1, 2)], "0.75", "0.87", "1.5")):
    vk = form2(Mk, wk)
    same(f"KC 4 variance {wk}", fmt(vk, 2), v_)
    same(f"KC 4 volatility {wk}", f"{math.sqrt(float(vk)):.2f}", sp_)
    same(f"KC 4 bound {wk}", fmt(2 * wk[0] + wk[1], 1), bound)
show("KC 4", "0.04(4)+0.64(1)+2(0.16)(-1)=0.48")
show("KC 4", "0.25(4)+0.25(1)+2(0.25)(-1)=0.75")
show("KC 4", "s_p=0.69%")
show("KC 4", "s_p=0.87%")
# Section 5 knowledge check: m11 = 2, m22 = 4, m12 = 3
assert 2 * 4 - 9 == -1 and form2([[Fr(2), Fr(3)], [Fr(3), Fr(4)]], [Fr(3), Fr(-2)]) == -2
show("KC 5", "h(\\mathbf x)=2(9)+2(3)(3)(-2)+4(4)=-2<0")
# Section 7 knowledge check: gradient of the unsymmetric M of E1 at (1, 1)
assert [sum((M1[i][j] + M1[j][i]) for j in range(2)) for i in range(2)] == [6, 6]
show("KC 7", "\\nabla h(1,1)=(6,6)^{\\top}")
# Problem 1: leading minors; M_C's seven principal minors and its null vector
MA = [[Fr(2), Fr(1), Fr(0)], [Fr(1), Fr(2), Fr(3)], [Fr(0), Fr(3), Fr(2)]]
MB = [[Fr(2), Fr(1), Fr(0)], [Fr(1), Fr(2), Fr(1)], [Fr(0), Fr(1), Fr(2)]]
MC = [[Fr(1), Fr(1), Fr(0)], [Fr(1), Fr(1), Fr(0)], [Fr(0), Fr(0), Fr(1)]]
assert (MB[0][0] * MB[1][1] - MB[0][1] ** 2, det3(MB)) == (3, 4) and (MA[0][0] * MA[1][1] - 1, det3(MA)) == (3, -12)
pm = [MC[0][0], MC[1][1], MC[2][2], MC[0][0] * MC[1][1] - MC[0][1] ** 2, MC[0][0] * MC[2][2] - MC[0][2] ** 2,
      MC[1][1] * MC[2][2] - MC[1][2] ** 2, det3(MC)]
assert pm == [1, 1, 1, 0, 1, 1, 0] and [sum(MC[i][j] * [1, -1, 0][j] for j in range(3)) for i in range(3)] == [0, 0, 0]
show("S1", "Its seven principal minors are 1, 1 and 1, then 0, 1 and 1, then 0")
show("S1", "2(4-9)-1(2)=-12<0")
# Problem 2: the symmetric part of (2 6; 0 3)
assert 2 * 3 - 3**2 == -3 and form2([[Fr(2), Fr(6)], [Fr(0), Fr(3)]], [Fr(1), Fr(-1)]) == -1
show("S2", "h(1,-1)=2-6+3=-1")
# Problem 8: exposures f = (1, 0.5), Delta = (0.1, -0.1)
a8, M8 = [dec("0.10"), dec("0.04")], [[dec("0.04"), dec("0.01")], [dec("0.01"), dec("0.02")]]
f8, D8 = [Fr(1), dec("0.5")], [dec("0.1"), dec("-0.1")]


def u8(f: list[Fr]) -> Fr:
    """u(f) = a'f - f'Mf/2, the quadratic growth model of Problem 8."""
    return sum((a8[i] * f[i] for i in range(2)), Fr(0)) - form2(M8, f) / 2


grad8 = [a8[i] - sum(M8[i][j] * f8[j] for j in range(2)) for i in range(2)]
assert grad8 == [dec("0.055"), dec("0.020")]
lin8, quad8 = sum(D8[i] * grad8[i] for i in range(2)), form2(M8, D8)
assert (lin8, quad8, lin8 - quad8 / 2) == (dec("0.0035"), dec("0.0004"), dec("0.0033"))
assert (u8(f8), u8([f8[0] + D8[0], f8[1] + D8[1]])) == (dec("0.0925"), dec("0.0958"))
assert u8([f8[0] + D8[0], f8[1] + D8[1]]) - u8(f8) == lin8 - quad8 / 2                    # (10.9) is exact
show("S8", "&=(0.10-0.045,\\;0.04-0.02)^{\\top}")
show("S8", "&=(0.055,\\;0.020)^{\\top}")
show("S8", "&=0.0035-\\tfrac12(0.0004)")
show("S8", "&=0.0033")
show("S8", "moves from 0.0925 to 0.0958")
# Problem 10: x = e1, y = e2, omega = 1/2 for the M of E1
xm = [Fr(1, 2), Fr(1, 2)]
assert (form2(M1, xm), (form2(M1, [Fr(1), Fr(0)]) + form2(M1, [Fr(0), Fr(1)])) / 2, -form2(M1, [Fr(1), Fr(-1)])) \
    == (Fr(3, 2), 1, 2)
assert form2(M1, xm) - 1 == Fr(1, 4) * 2                                             # the excess is omega(1-omega)*2
show("S10", "h(\\tfrac12,\\tfrac12)=1.5")
show("S10", "The excess $0.5$")

# ====================================================================================== chart-only numbers cited
show("X7 note", "\\min(T-1,\\,28)")
show("X9 scale", "at four times its length")

# ====================================================================================== the printed values are in the text
missing = [(lab, t) for lab, t in PRINTED if norm(t) not in MD]
print()
print(f"{len(PRINTED)} printed values checked against src/lm10.md; {len(missing)} missing")
for lab, t in missing:
    print(f"   MISSING {lab}: {t}")
print(f"anchor differences ({len(ANCHOR_DIFFS)}):")
for a_ in ANCHOR_DIFFS:
    print("   ", a_)
assert not missing, "a printed value is not in src/lm10.md as printed"
assert not re.search(r"(CORR_ORDER|GRAD_SCALE|P\d+_TEXT)", MD), "a placeholder is left in src/lm10.md"
