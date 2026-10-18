"""Every number that LM13 (Probability Foundations and Bayes) prints, computed from TR23 and checked against src/lm13.md.

Run:  uv run python data/lm13_numbers.py      (after data/vol3_series.py has written processed/vol3_taiex.parquet)

Inputs: data/processed/vol3_taiex.parquet through data/lm13_common.py (T = 5,849 simple daily returns of the TAIEX
total-return index, 2003-01-03 .. 2026-10-08; the pair space is the 5,848 return dates with a previous return,
triples the 5,847 dates with two), src/lm13.md (the text the checks compare against), plans/vol-3-anchors.md (the
anchors this script compares with) and labs/LM13_lab/data/taiex_tr.csv (the file the module's printed code reads).
Thresholds are inclusive and counted with the guard; data/lm13_common.py asserts every guarded count equal to an
exact count from the two-decimal closes. LM13 has no simulation, so no random generator.

Checks, all of which stop the script on a mismatch:
  chk(label, value, fmt, printed)  format(value, fmt) must equal the printed string, the string must appear in the
                                   module as a whole number, and the value must not sit on a rounding tie (a reader
                                   rounding by hand could get the other last digit: project/PITFALLS.md section 7).
                                   Hand results are recomputed from the inputs printed beside them.
  has(label, text)                 a literal string (a date, a fraction, a phrase) appears in the module.
  anchor(id, got, expected)        compares a value with plans/vol-3-anchors.md; a difference is reported, not forced
                                   (expected must be part of that anchor's printed value, or the script stops).
It ends by printing "all N checks passed".
"""
import contextlib
import io
import math
import os
import re
from fractions import Fraction
from itertools import product
from math import log
from pathlib import Path

import numpy as np
from lm13_common import BINS, BUCKETS, at_least, at_most, bucket, load, regimes

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MD = ROOT / "src" / "lm13.md"
TEXT = MD.read_text(encoding="utf-8")
NORM = TEXT.replace("{,}", ",").replace("−", "-").replace("\\%", "%").replace("\\,", "")
N_CHECKS = 0
ANCHOR_DIFFS: list[str] = []


def in_text(printed: str) -> bool:
    """The printed number appears in the text as a whole number (not inside a longer one: 6.5 is not in 6.54)."""
    p = printed.replace("−", "-")
    return re.search(r"(?<![\d.])" + re.escape(p) + r"(?!\d)", NORM) is not None


def tie(value: float, fmt: str) -> bool:
    """True when value lies on a rounding boundary of fmt."""
    m = re.search(r"\.(\d+)", fmt)
    d = int(m.group(1)) if m else 0
    scaled = abs(value) * 10 ** d * (100 if "%" in fmt else 1)
    return abs(scaled - math.floor(scaled) - 0.5) < 1e-6


def chk(label: str, value: float, fmt: str, printed: str) -> None:
    global N_CHECKS
    got = format(value, fmt)
    print(f"CHECK {label}: {got} (printed {printed}) {'ok' if got == printed else 'MISMATCH'}")
    assert got == printed, (label, got, printed)
    assert not tie(value, fmt), ("rounding tie: print more digits", label, value)
    assert in_text(printed), f"{label}: {printed!r} not found in src/lm13.md"
    N_CHECKS += 1


def has(label: str, text: str) -> None:
    global N_CHECKS
    t = text.replace("{,}", ",").replace("−", "-").replace("\\%", "%")
    assert t in NORM, f"{label}: {text!r} not found in src/lm13.md"
    print(f"CHECK {label}: '{text}' in text ok")
    N_CHECKS += 1


ANCHORS: dict[str, str] = {}
for line in (ROOT / "plans" / "vol-3-anchors.md").read_text(encoding="utf-8").splitlines():
    if line.startswith("| A13-"):
        cells = line.split(" | ")
        val = cells[-2].strip()
        assert val.startswith("`") and val.endswith("`"), line[:40]
        ANCHORS[cells[0].strip("| ").strip()] = val.strip("`")
assert len(ANCHORS) == 56, len(ANCHORS)
SEEN: set[str] = set()


def anchor(aid: str, got: str, expected: str) -> None:
    """Compare with plans/vol-3-anchors.md; a difference is reported, not forced."""
    assert expected in ANCHORS[aid], f"{aid}: {expected!r} is not in the anchor's value {ANCHORS[aid]!r}"
    SEEN.add(aid)
    tag = "ok" if got == expected else "DIFFERS"
    print(f"ANCHOR {aid}: {got} (anchor {expected}) {tag}")
    if got != expected:
        ANCHOR_DIFFS.append(f"{aid}: script {got}, anchor {expected}")


def g(x: float) -> str:
    return f"{x:.10g}"


def pc(x: float) -> str:
    return f"{100 * x:.10g}%"


# ====================================================================== sample (notation note, case)
tr = load()
T, R = tr.T, tr.R
nP, n3 = T - 1, T - 2
assert (T, tr.dates[0], tr.dates[-1], len(tr.closes)) == (5849, "2003-01-03", "2026-10-08", 5850)
anchor("A13-03", f"closes {len(tr.closes)}; T {T}; returns {tr.dates[0]} .. {tr.dates[-1]}",
       "closes 5850; T 5849; returns 2003-01-03 .. 2026-10-08")
anchor("A13-04", f"{nP} pairs; first pair date {tr.dates[1]}", "5848 pairs; first pair date 2003-01-06")
anchor("A13-05", f"{pc(R[0])} on {tr.dates[0]}", "2.24180759% on 2003-01-03")
chk("T", T, ",", "5,849")
chk("pair space", nP, ",", "5,848")
chk("triples", n3, ",", "5,847")
chk("closes", len(tr.closes), ",", "5,850")
has("first and last return", "3 January 2003 to 8 October 2026")
assert tr.dates[1] == "2003-01-06" and tr.dates[2] == "2003-01-07"
has("pair space start", "5,848 return dates from 6 January 2003")
has("triples start", "5,847 dates from 7 January 2003")
chk("first return", R[0], "+.2%", "+2.24%")
has("first return date", "+2.24% on 3 January 2003")
ties = [sum(1 for r in tr.RF if r == Fraction(c, 100)) for c in (0, -1, 1, -2, 2, -3, 3, -4, 4, -5, 5)]
assert ties == [0] * 11 and len(set(tr.RF)) == T
anchor("A13-06", f"{ties}; distinct returns {len(set(tr.RF))}", "[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]; distinct returns 5849")
has("no exact ties", "no return equal to 0, ±1%, ±2%, ±3%, ±4% or ±5%, and 5,849 distinct returns")
has("no return 0", "no return is 0")

# earlier modules: LM4's bet and the limit
fstar = 0.5 / 0.01 - 0.5 / 0.02
gstar = 0.5 * log(1.5) + 0.5 * log(0.75)
anchor("A13-01", f"f* {g(fstar)}; g* {g(gstar)}", "f* 25; g* 0.05889151783")
lm04 = (ROOT / "src" / "lm04.md").read_text(encoding="utf-8")
assert "f^*=0.5/0.01-0.5/0.02=50-25=25" in lm04 and "5.889\\%" in lm04, "LM4 no longer prints its bet"
assert "raised that limit from 7% to 10% on 1 June 2015" in (ROOT / "src" / "lm05.md").read_text(encoding="utf-8")
anchor("A13-02", "7% to 10% on 2015-06-01", "7% to 10% on 2015-06-01")
has("limit change", "1 June 2015, when the daily price limit was raised from 7% to 10%")

# ====================================================================== the case and its exhibit
fall = at_most(tr, -3)
big_all = at_least(tr, 2) | at_most(tr, -2)
A, Bm = fall[1:], big_all[:-1]                     # on the pair space: a fall today, a big move yesterday
nA, nB, nAB = int(A.sum()), int(Bm.sum()), int((A & Bm).sum())
cells = (nAB, nA - nAB, nB - nAB, nP - nA - nB + nAB)
assert int(fall.sum()) == nA == 108 and not fall[0], "every fall must lie in the pair space"
anchor("A13-08", f"{int(fall.sum())} of {T}: {pc(fall.mean())}", "108 of 5849: 1.846469482%")
anchor("A13-09", f"{nAB}/{nA} = {pc(nAB / nA)}", "32/108 = 29.62962963%")
anchor("A13-10", f"{nB - nAB}/{nP - nA} = {pc((nB - nAB) / (nP - nA))}", "457/5740 = 7.961672474%")
anchor("A13-11", f"{nB} of {nP}", "489 of 5848")
anchor("A13-12", f"{nAB}/{nB} = {pc(nAB / nB)}; days per fall {g(nB / nAB)}", "32/489 = 6.54396728%; days per fall 15.28125")
anchor("A13-15", ", ".join(map(str, (*cells, nP - nA, nP - nB))), "32, 76, 457, 5283, 5740, 5359")
anchor("A13-23", f"Pr(A given Bc) {nA - nAB}/{nP - nB} = {pc((nA - nAB) / (nP - nB))}", "Pr(A given Bc) 76/5359 = 1.418175033%")
for lab, n in (("falls", 108), ("falls after a big move", 32), ("other days after a big move", 457),
               ("days after a big move", 489), ("falls after a smaller move", 76), ("neither", 5283),
               ("days after a smaller move", 5359), ("other days", 5740)):
    chk(f"X1 {lab}", n, ",", f"{n:,}")
assert cells == (32, 76, 457, 5283) and nB == 489 and nP - nB == 5359 and nP - nA == 5740
has("X1 row 1", "| 2% or more either way | 32 | 457 | 489 | 6.54% |")
has("X1 row 2", "| Smaller | 76 | 5,283 | 5,359 | 1.42% |")
has("X1 row 3", "| All | 108 | 5,740 | 5,848 | 1.85% |")
has("X1 row 4", "| Share after a big move | 29.63% | 7.96% | 8.36% | |")
chk("X1 Pr(A|B)", nAB / nB, ".2%", "6.54%")
chk("X1 Pr(A|Bc)", (nA - nAB) / (nP - nB), ".2%", "1.42%")
chk("X1 Pr(A) on pairs", nA / nP, ".2%", "1.85%")
chk("X1 hit rate", nAB / nA, ".2%", "29.63%")
chk("X1 false-alarm rate", (nB - nAB) / (nP - nA), ".2%", "7.96%")
chk("X1 Pr(B)", nB / nP, ".2%", "8.36%")
assert not any(r in (Fraction(2, 100), Fraction(-2, 100), Fraction(-3, 100)) for r in tr.RF)
has("X1 note: ties", "no return equals ±2% or −3%")
chk("case: share of all days", nA / T, ".2%", "1.85%")
chk("case: hit rate, 3 digits", nAB / nA, ".1%", "29.6%")
chk("case: ratio to the base rate (pair space)", (nAB / nB) / (nA / nP), ".1f", "3.5")
chk("case: ratio to the base rate, all days", (nAB / nB) / (nA / T), ".1f", "3.5")
chk("case: ratio from the printed 6.54 and 1.85", 6.54 / 1.85, ".1f", "3.5")
anchor("A13-13", f"(pair space): {g((nAB / nB) / (nA / nP))}", "(pair space): 3.543437098")
assert nB / nAB > 15
has("case: under one day in fifteen", "under one day in fifteen")
anchor("A13-14", g((nAB / nA) / (nAB / nB)), "4.527777778")

# ====================================================================== Section 2
# E1: two trades of LM4's bet at f = 25, outcomes equally likely
om = ["".join(w) for w in product("+-", repeat=2)]
up_m, dn_m = 1 + 25 * 0.02, 1 - 25 * 0.01
assert (up_m, dn_m) == (1.5, 0.75) and 1.5 * 0.75 == 1.125 and 0.75 ** 2 == 0.5625
evA, evB = {w for w in om if w[0] == "+"}, {w for w in om if "-" in w}
assert Fraction(len(evB), 4) == Fraction(3, 4) and evA & evB == {"+-"} and evA | evB == set(om)
below = [w for w in om if (1.5 if w[0] == "+" else 0.75) * (1.5 if w[1] == "+" else 0.75) < 1]
assert below == ["--"]
anchor("A13-35", f"Pr(B) = {Fraction(len(evB), 4)}; Pr(A and B) = {Fraction(len(evA & evB), 4)}", "Pr(B) = 3/4; Pr(A and B) = 1/4")
has("E1", "\\Pr(B)=1-\\Pr(\\{++\\})=3/4$ and $\\Pr(A\\cap B)=1/4")
has("E1 multiples", "$1+25\\times2%=1.5$ and a loss by $1-25\\times1%=0.75$")
has("E1 product", "$1.5\\times0.75=1.125$")
has("E1 two losses", "$0.75^2=0.5625$")

# X2 and E2: falls of 2% or more today (A) and yesterday (B), pair space
f2 = at_most(tr, -2)
t2, y2 = f2[1:], f2[:-1]
nt, ny, nb2, nu2 = int(t2.sum()), int(y2.sum()), int((t2 & y2).sum()), int((t2 | y2).sum())
assert nu2 == nt + ny - nb2
anchor("A13-24", f"today (A) {nt}, yesterday (B) {ny}, both {nb2}, either {nu2}; regions A only {nt - nb2}, both {nb2}, "
       f"B only {ny - nb2}, neither {nP - nu2}",
       "today (A) 252, yesterday (B) 252, both 38, either 466; regions A only 214, both 38, B only 214, neither 5382")
has("X2 note", "$252+252-38=466$")
has("E2 counts", "252 days fell 2% or more ($A$), 252 followed such a fall ($B$), and 38 did both")
has("E2 union", "(252+252-38)/5,848=7.97%")
chk("E2 union share", nu2 / nP, ".2%", "7.97%")
chk("E2 sum share", (nt + ny) / nP, ".2%", "8.62%")
chk("E2 sum", nt + ny, "d", "504")
chk("E2 Pr(A)", nt / nP, ".4f", "0.0431")
chk("E2 model both, from the printed 0.0431", nP * 0.0431 ** 2, ".1f", "10.9")
chk("E2 model both, exact", nP * (nt / nP) * (ny / nP), ".1f", "10.9")
anchor("A13-36", f"union {nu2}/{nP} = {pc(nu2 / nP)}; sum {nt + ny}/{nP} = {pc((nt + ny) / nP)}", "union 466/5848 = 7.968536252%; sum 504/5848 = 8.618331053%")
has("pitfall 2", "$214+38+214=466$")
assert (nt - nb2, nb2, ny - nb2) == (214, 38, 214)
# knowledge check: Pr(A) = Pr(B) = 0.9
assert Fraction(9, 10) + Fraction(9, 10) - 1 == Fraction(4, 5)
anchor("A13-17", g(0.9 + 0.9 - 1), "0.8")
has("KC 2", "$0.9+0.9-1=0.8$")
ten = set(range(10))
assert Fraction(len((ten - {0}) & (ten - {1})), 10) == Fraction(4, 5)   # ten outcomes, A and B each miss one
has("KC 2 example", "with ten equally likely outcomes, let $A$ and $B$ each miss a different one")

# ====================================================================== Section 3
dn = R < 0
yD, tD = dn[:-1], dn[1:]
nDD, nDU, nUD, nUU = (int((yD & tD).sum()), int((yD & ~tD).sum()), int((~yD & tD).sum()), int((~yD & ~tD).sum()))
assert (nDD, nDU, nUD, nUU) == (1226, 1417, 1418, 1787)
chk("down today on the pair space", nDD + nUD, ",", "2,644")
chk("share down on the pair space", (nDD + nUD) / nP, ".2%", "45.21%")
chk("down yesterday", nDD + nDU, ",", "2,643")
chk("share down after down", nDD / (nDD + nDU), ".2%", "46.39%")
has("opening", "Of the 2,643 days after a down day, 1,226 were down, 46.39%")

# X3: buckets of yesterday's return
yR = R[:-1]
bk = []
for lo, hi in BUCKETS:
    m = bucket(yR, None if lo is None else lo / 100, None if hi is None else hi / 100)
    ex = np.array([(lo is None or r > Fraction(lo, 100)) and (hi is None or r <= Fraction(hi, 100)) for r in tr.RF[:-1]])
    assert (m == ex).all(), ("bucket guard differs from the exact count", lo, hi)
    bk.append((int(m.sum()), int((m & A).sum())))
assert sum(d for d, _ in bk) == nP and sum(c for _, c in bk) == nA
anchor("A13-25", "; ".join(f"{d}/{c} {pc(c / d)}" for d, c in bk),
       "108/13 12.03703704%; 144/8 5.555555556%; 516/15 2.906976744%; 1875/30 1.6%; 2272/23 1.012323944%; "
       "696/8 1.149425287%; 170/8 4.705882353%; 67/3 4.47761194%")
has("X3 note counts", "108/13, 144/8, 516/15, 1,875/30, 2,272/23, 696/8, 170/8 and 67/3, which sum to 5,848 and 108")
assert tr.dates[-2] == "2026-10-07"
has("X3 note: yesterday's last date", "Yesterday's returns end on 7 October 2026")
bins = [int(bucket(R, None if lo is None else lo / 100, None if hi is None else hi / 100).sum()) for lo, hi in BINS]
assert bins[5] - bk[3][0] == 1, "the bucket from -1% to 0 must hold one day fewer than the bin"
chk("X3 after a fall", bk[0][1] / bk[0][0], ".2%", "12.04%")
chk("X3 after a rise of more than 3%", bk[7][1] / bk[7][0], ".2%", "4.48%")
chk("pitfall 3: one more fall in the left bucket", (bk[0][1] + 1) / bk[0][0], ".2%", "12.96%")
chk("pitfall 3: one more fall in the right bucket", (bk[7][1] + 1) / bk[7][0], ".2%", "5.97%")
has("pitfall 3 counts", "13 falls among 108 days and the 4.48% on 3 among 67")

# E3: a fall after a fall
yA = fall[:-1]
ncc, nyA = int((yA & A).sum()), int(yA.sum())
assert (ncc, nyA) == (13, 108)
has("E3 inputs", "$\\Pr(A_1)=108/5,848$ and $\\Pr(A_2\\mid A_1)=13/108=12.04%$")
chk("E3 conditional", ncc / nyA, ".2%", "12.04%")
chk("E3 both", ncc / nP, ".3%", "0.222%")
has("E3 both, fraction", "13/5,848=0.222%")
chk("E3 base rate on pairs", nA / nP, ".2%", "1.85%")
chk("E3 ratio to the base rate", (ncc / nyA) / (nA / nP), ".1f", "6.5")
chk("E3 ratio from the printed 12.04 and 1.85", 12.04 / 1.85, ".1f", "6.5")
chk("E3 pairs if independent", nyA * nA / nP, ".1f", "2.0")
has("E3 model", "$108^2/5,848=2.0$ days, not 13")
anchor("A13-37", f"pairs if independent {g(nyA * nA / nP)}", "pairs if independent 1.994528044")

# E4: inside the tail
n4, n5 = int(at_most(tr, -4).sum()), int(at_most(tr, -5).sum())
assert (n4, n5) == (44, 15)
chk("E4 Pr(<=-5 | <=-3)", n5 / nA, ".1%", "13.9%")
chk("E4 Pr(<=-4 | <=-3)", n4 / nA, ".1%", "40.7%")
has("E4 fractions", "15/108=13.9%")
has("E4 fractions 2", "44/108=40.7%")
chk("E4 mean of the 108 days", float(R[fall].mean()), ".2%", "-4.06%")
anchor("A13-38", f"mean R of the {nA} days {pc(float(R[fall].mean()))}",
       "mean R of the 108 days -4.062685051%")

# KC 3
chk("KC3 down given down", nDD / (nDD + nDU), ".4f", "0.4639")
chk("KC3 down yesterday given down today", nDD / (nDD + nUD), ".4f", "0.4637")
anchor("A13-18", f"{nDD}/{nDD + nDU} = {g(nDD / (nDD + nDU))}; {nDD}/{nDD + nUD} = {g(nDD / (nDD + nUD))}",
       "1226/2643 = 0.463866818; 1226/2644 = 0.4636913767")
has("KC3 fractions", "1,226/2,643=0.4639")
has("KC3 fractions 2", "1,226/2,644=0.4637")
chk("KC3 inversion factor", nB / nA, ".2f", "4.53")
chk("KC3 inversion factor, one decimal", nB / nA, ".1f", "4.5")
has("KC3 factor", "$489/108=4.53$")

# ====================================================================== Section 4
anchor("A13-26", f"DD {nDD}, DU {nDU}, UD {nUD}, UU {nUU}",
       "DD 1226, DU 1417, UD 1418, UU 1787")
has("X4 row down", "| Down | 1,226 | 1,417 | 2,643 | 0.4639 |")
has("X4 row up", "| Up | 1,418 | 1,787 | 3,205 | 0.4424 |")
has("X4 row all", "| All | 2,644 | 3,204 | 5,848 | 0.4521 |")
chk("X4 share down after up", nUD / (nUD + nUU), ".4f", "0.4424")
chk("X4 share down today", (nDD + nUD) / nP, ".4f", "0.4521")
rows, cols = (nDD + nDU, nUD + nUU), (nDD + nUD, nDU + nUU)
ind = [rows[i] * cols[j] / nP for i in range(2) for j in range(2)]
for v, p in zip(ind, ("1,195.0", "1,448.0", "1,449.0", "1,756.0"), strict=True):
    chk(f"X4 if independent {p}", v, ",.1f", p)
chk("X4 if independent: total", sum(ind), ",.1f", "5,848.0")
has("X4 independent row down", "| Down | 1,195.0 | 1,448.0 | 2,643 |")
has("X4 independent row up", "| Up | 1,449.0 | 1,756.0 | 3,205 |")
anchor("A13-27", ", ".join(g(x) for x in ind), "1194.954172, 1448.045828, 1449.045828, 1755.954172")
chk("X4 gap", nDD - ind[0], ".0f", "31")
has("X4 gap text", "the gap is 31 days in 5,848")

# E5: pairwise is not mutual
ev = {"A1": {w for w in om if w[0] == "+"}, "A2": {w for w in om if w[1] == "+"}, "A3": {w for w in om if w[0] == w[1]}}
assert ev["A1"] == {"++", "+-"} and ev["A2"] == {"++", "-+"} and ev["A3"] == {"++", "--"}
for a, b in (("A1", "A2"), ("A1", "A3"), ("A2", "A3")):
    assert Fraction(len(ev[a] & ev[b]), 4) == Fraction(1, 4) == Fraction(len(ev[a]), 4) * Fraction(len(ev[b]), 4)
assert Fraction(len(ev["A1"] & ev["A2"] & ev["A3"]), 4) == Fraction(1, 4) != Fraction(1, 8)
anchor("A13-39", f"all three {Fraction(len(ev['A1'] & ev['A2'] & ev['A3']), 4)} against {Fraction(1, 8)}", "all three 1/4 against 1/8")
has("E5 result", "$\\Pr(A_1\\cap A_2\\cap A_3)=1/4$, not $1/8$")
# Deep Dive 2: 2^m - m - 1 conditions
assert 2 ** 3 - 3 - 1 == 4
anchor("A13-16", f"2^3 - 3 - 1 = {2 ** 3 - 3 - 1}", "2^3 - 3 - 1 = 4")
has("DD2", "$2^m-m-1$ conditions remain: 4 for three events")

# E6: at least one fall in 20 sessions
p1 = nA / T
chk("E6 Pr(A), five digits", p1, ".4%", "1.8465%")
has("E6 fraction", "$108/5,849=1.8465%$")
chk("E6 model from the printed 1.8465%", 1 - (1 - 0.018465) ** 20, ".1%", "31.1%")
chk("E6 model exact", 1 - (1 - p1) ** 20, ".1%", "31.1%")


def blocks(n: int) -> tuple[int, int, int]:
    nb = T // n
    return nb, T - nb * n, int(fall[: nb * n].reshape(nb, n).any(axis=1).sum())


nb20, left20, hit20 = blocks(20)
assert (nb20, left20, hit20) == (292, 9, 61)
has("E6 blocks", "TR23 has 292 complete blocks, with the last 9 returns left out")
chk("E6 model blocks from the printed 31.1%", nb20 * 0.311, ".0f", "91")
chk("E6 model blocks exact", nb20 * (1 - (1 - p1) ** 20), ".0f", "91")
has("E6 model blocks text", "$292\\times0.311=91$")
chk("E6 data share", hit20 / nb20, ".1%", "20.9%")
has("E6 data", "The data have 61 such blocks, 20.9%")
anchor("A13-40", f"blocks {nb20}, left out {left20}, with a fall {hit20} ({pc(hit20 / nb20)})",
       "blocks 292, left out 9, with a fall 61 (20.89041096%)")

# KC 4: up and down today
n_up, n_dn = int((R > 0).sum()), int((R < 0).sum())
assert (n_up, n_dn) == (3205, 2644)
chk("KC4 Pr(up)", n_up / T, ".4f", "0.5480")
chk("KC4 Pr(down)", n_dn / T, ".4f", "0.4520")
chk("KC4 product of the printed", 0.5480 * 0.4520, ".4f", "0.2477")
has("KC4 fractions", "$\\Pr(\\text{up})=3,205/5,849=0.5480$ and $\\Pr(\\text{down})=2,644/5,849=0.4520$")
anchor("A13-19", f"Pr(up) {n_up}/{T} = {g(n_up / T)}, Pr(down) {n_dn}/{T} = {g(n_dn / T)}; product of the printed 0.5480 x 0.4520 = {g(0.5480 * 0.4520)}",
       "Pr(up) 3205/5849 = 0.5479569157, Pr(down) 2644/5849 = 0.4520430843; product of the printed 0.5480 x 0.4520 = 0.247696")

# ====================================================================== Section 5
r7, r10 = regimes(tr)
n7, n10 = int(r7.sum()), int(r10.sum())
assert (n7, n10) == (3077, 2772)
d7, d10 = np.array(tr.dates)[r7], np.array(tr.dates)[r10]
assert (d7[0], d7[-1], d10[0], d10[-1]) == ("2003-01-03", "2015-05-29", "2015-06-01", "2026-10-08")
anchor("A13-07", f"7%: {n7} returns {d7[0]} .. {d7[-1]}; 10%: {n10} returns {d10[0]} .. {d10[-1]}",
       "7%: 3077 returns 2003-01-03 .. 2015-05-29; 10%: 2772 returns 2015-06-01 .. 2026-10-08")
has("X5 note dates", "returns dated 3 January 2003 → 29 May 2015 and 1 June 2015 → 8 October 2026")
c7, c10 = int((fall & r7).sum()), int((fall & r10).sum())
x5 = {}
for name, m in (("7", r7), ("10", r10)):
    mp = m[1:] & m[:-1]
    x5[name] = (int(mp.sum()), int((A & Bm & mp).sum()), int((Bm & mp).sum()), int((A & mp).sum()))
assert x5 == {"7": (3076, 17, 303, 72), "10": (2771, 15, 186, 36)}
i_s = tr.dates.index("2015-05-29")
assert not fall[i_s + 1] and not big_all[i_s]
chk("X5 straddling first day", R[i_s], ".2%", "-0.12%")
chk("X5 straddling second day", R[i_s + 1], ".2%", "-0.77%")
has("X5 straddling pair", "(−0.12%, then −0.77%) lies in neither and changes no count")
has("X5 pairs inside", "the 3,076 and 2,771 day pairs inside one regime")
has("X5 days", "| Days | 3,077 | 2,772 | 5,849 |")
has("X5 falls", "| Falls of 3% or more | 72 | 36 | 108 |")
has("X5 after a big move", "| After a big move: falls / days | 17 / 303 | 15 / 186 | 32 / 489 |")
chk("X5 share of days 7", n7 / T, ".2%", "52.61%")
chk("X5 share of days 10", n10 / T, ".2%", "47.39%")
chk("X5 fall share 7", c7 / n7, ".2%", "2.34%")
chk("X5 fall share 10", c10 / n10, ".2%", "1.30%")
chk("X5 after a big move 7", 17 / 303, ".2%", "5.61%")
chk("X5 after a big move 10", 15 / 186, ".2%", "8.06%")
chk("X5 hit 7", 17 / 72, ".2%", "23.61%")
chk("X5 hit 10", 15 / 36, ".2%", "41.67%")
has("X5 shares row", "| Share of days that fell | 2.34% | 1.30% | 1.85% |")
has("X5 after row", "| Share that fell after a big move | 5.61% | 8.06% | 6.54% |")
has("X5 hit row", "| Hit rate: share of falls after a big move | 23.61% | 41.67% | 29.63% |")
anchor("A13-28", f"7%: days {n7} ({pc(n7 / T)}), falls {c7} ({pc(c7 / n7)})", "7%: days 3077 (52.6072833%), falls 72 (2.339941501%)")

# E7: total probability and the regime of a fall
tot = Fraction(c7, n7) * Fraction(n7, T) + Fraction(c10, n10) * Fraction(n10, T)
assert tot == Fraction(108, T)
has("E7 display", "\\frac{72}{3,077}\\cdot\\frac{3,077}{5,849}+\\frac{36}{2,772}\\cdot\\frac{2,772}{5,849}")
has("E7 total", "\\frac{108}{5,849}=1.85%")
chk("E7 total", float(tot), ".2%", "1.85%")
chk("E7 weight 7", n7 / T, ".1%", "52.6%")
chk("E7 weight 10", n10 / T, ".1%", "47.4%")
chk("E7 Pr(10% | A)", c10 / (c7 + c10), ".1%", "33.3%")
has("E7 fraction", "36/108=33.3%")
trap = 0.0130 * 0.474 / (0.0234 * 0.526 + 0.0130 * 0.474)
chk("E7 from the printed 2.34%, 1.30%, 52.6%, 47.4%", trap, ".1%", "33.4%")
chk("E7 from the printed 0.5261, 0.4739", 0.0130 * 0.4739 / (0.0234 * 0.5261 + 0.0130 * 0.4739), ".1%", "33.4%")
anchor("A13-41", f"Pr(10% given A) {c10}/{c7 + c10} = {pc(c10 / (c7 + c10))}", "Pr(10% given A) 36/108 = 33.33333333%")

# E8: the case by Bayes' rule
base, hit, fa = nA / nP, nAB / nA, (nB - nAB) / (nP - nA)
chk("E8 base rate, 4 digits", base, ".3%", "1.847%")
chk("E8 hit rate, 4 digits", hit, ".2%", "29.63%")
chk("E8 false-alarm rate, 4 digits", fa, ".3%", "7.962%")
chk("E8 (a)", nAB / nB, ".2%", "6.54%")
has("E8 (a) text", "$32+457=489$ days after a big move, 32 fell: $32/489=6.54%$")
t1, t2b = 0.01847 * 0.2963, 0.98153 * 0.07962
assert abs(0.98153 - (1 - 0.01847)) < 1e-15
chk("E8 (b) first term", t1, ".6f", "0.005473")
chk("E8 (b) second term", t2b, ".5f", "0.07815")
chk("E8 (b) ratio from the printed terms", 0.005473 / (0.005473 + 0.07815), ".2%", "6.54%")
chk("E8 (b) from the four-digit inputs", t1 / (t1 + t2b), ".2%", "6.54%")
chk("E8 (b) from the case's rounded inputs", 0.0185 * 0.296 / (0.0185 * 0.296 + 0.9815 * 0.0796), ".2%", "6.55%")
has("E8 (b) rounded inputs", "The case's rounded inputs, 1.85%, 29.6% and 7.96%, would give 6.55%")
chk("E8 (c) prior odds", nA / (nP - nA), ".6f", "0.018815")
lr = hit / fa
chk("E8 (c) likelihood ratio", lr, ".4f", "3.7215")
chk("E8 (c) posterior odds from the printed", 0.018815 * 3.7215, ".5f", "0.07002")
chk("E8 (c) posterior odds exact", nAB / (nB - nAB), ".5f", "0.07002")
chk("E8 (c) probability from the printed odds", 0.07002 / 1.07002, ".2%", "6.54%")
has("E8 (c) text", "$0.018815\\times3.7215=0.07002$, which is $32/457$")
has("E8 (c) odds", "$108/5,740=0.018815$")
has("E8 (c) ratio", "$(32/108)/(457/5,740)=3.7215$")
has("E8 last paragraph", "outnumber the hits, 457 to 32")
anchor("A13-20", f"LR = Pr(B given A)/Pr(B given Ac) = {g(lr)}; base rate with Pr(A given B) = 1/2: 1/(1 + LR) = {pc(1 / (1 + lr))}",
       "LR = Pr(B given A)/Pr(B given Ac) = 3.72153335; base rate with Pr(A given B) = 1/2: 1/(1 + LR) = 21.17956024%")
anchor("A13-33", f"prior odds {nA}/{nP - nA} = {g(nA / (nP - nA))}; LR = {g(lr)}; posterior odds {nAB}/{nB - nAB} = "
       f"{g(nAB / (nB - nAB))}", "prior odds 108/5740 = 0.01881533101; LR = 3.72153335; posterior odds 32/457 = 0.07002188184")
anchor("A13-42", f"(13.9) with 0.01847, 0.2963, 0.07962: {pc(t1 / (t1 + t2b))}", "(13.9) with 0.01847, 0.2963, 0.07962: 6.544516743%")
# frequency formats (quoted, Gigerenzer and Hoffrage 1995, Study 1)
has("frequency formats", "It rose from 16% to 46% with their standard menu and from 28% to 50% with the short one")
anchor("A13-22", "probability formats 16% (standard menu), 28% (short menu); frequency formats 46% (standard menu), 50% (short menu)",
       "probability formats 16% (standard menu), 28% (short menu); frequency formats 46% (standard menu), 50% (short menu)")

# widget: initial state (the PDF) and the 1,000-day picture
chk("widget Pr(B)", nB / nP, ".2%", "8.36%")
anchor("A13-32", f"Pr(B) {pc(nB / nP)}; Pr(A given B) {pc(nAB / nB)}; Pr(A given Bc) {pc((nA - nAB) / (nP - nB))}; "
       f"ratio {g((nAB / nB) / base)}", "Pr(B) 8.361833105%; Pr(A given B) 6.54396728%; Pr(A given Bc) 1.418175033%; ratio 3.543437098")
per = [1000 * c / nP for c in cells]
sq = [int(x) for x in per]
for i in sorted(range(4), key=lambda i: per[i] - sq[i], reverse=True)[: 1000 - sum(sq)]:
    sq[i] += 1
anchor("A13-34", f"squares {sq}; picture share {sq[0]}/{sq[0] + sq[2]} = {pc(sq[0] / (sq[0] + sq[2]))}",
       "squares [6, 13, 78, 903]; picture share 6/84 = 7.142857143%")

# E9: the manager
lr8 = 0.55 ** 8 * 0.45 ** 4 / 0.5 ** 12
chk("E9 likelihood ratio", lr8, ".4f", "1.4064")
chk("E9 posterior odds from the printed ratio", (0.1 / 0.9) * 1.4064, ".5f", "0.15627")
chk("E9 posterior from the printed odds", 0.15627 / 1.15627, ".1%", "13.5%")
po = (0.1 / 0.9) * lr8
chk("E9 posterior exact", po / (1 + po), ".1%", "13.5%")
has("E9 posterior text", "$\\Pr(\\text{skilled}\\mid\\text{record})=0.15627/1.15627=13.5%$")
anchor("A13-43", f"LR {g(lr8)}; posterior odds {g(po)}; posterior {pc(po / (1 + po))}",
       "LR 1.406408618; posterior odds 0.1562676242; posterior 13.51483177%")

# pitfall and KC 5
chk("prosecutor's factor", nB / nA, ".2f", "4.53")
chk("KC5 base rate for a posterior of 1/2, from the printed 3.7215", 1 / (1 + 3.7215), ".2%", "21.18%")
chk("KC5 exact", 1 / (1 + lr), ".2%", "21.18%")
assert 11 < (1 / (1 + 3.7215)) / 0.0185 < 12 and 11 < (1 / (1 + lr)) / (nA / nP) < 12
has("KC5 eleven times", "more than eleven times TR23's base rate of 1.85%")

# ====================================================================== Section 6
# E10: X = W2/W0 on two trades at f = 25
vals = {w: (1.5 if w[0] == "+" else 0.75) * (1.5 if w[1] == "+" else 0.75) for w in om}
assert vals == {"++": 2.25, "+-": 1.125, "-+": 1.125, "--": 0.5625}
pmf = {v: Fraction(sum(1 for w in om if vals[w] == v), 4) for v in set(vals.values())}
assert pmf == {2.25: Fraction(1, 4), 1.125: Fraction(1, 2), 0.5625: Fraction(1, 4)}
assert sum(p for v, p in pmf.items() if v <= 1.125) == Fraction(3, 4) and sum(p for v, p in pmf.items() if v < 1.125) == Fraction(1, 4)
chk("E10 ln 1.5", log(1.5), ".2%", "40.55%")
chk("E10 half ln 1.125 = g*", 0.5 * log(1.125), ".3%", "5.889%")
chk("E10 ln 0.75", log(0.75), ".2%", "-28.77%")
assert abs(0.5 * log(1.125) - gstar) < 1e-15 and abs(0.5 * (log(1.5) + log(0.75)) - gstar) < 1e-15
assert abs(log(1.5) / 4 + gstar / 2 + log(0.75) / 4 - gstar) < 1e-15
anchor("A13-44", f"X = 2.25, 1.125, 0.5625; pmf 1/4, 1/2, 1/4; F_X(1) = {sum(p for v, p in pmf.items() if v <= 1)}",
       "X = 2.25, 1.125, 0.5625; pmf 1/4, 1/2, 1/4; F_X(1) = 1/4")
has("E10 values", "$X(++)=1.5^2=2.25$, $X(+-)=X(-+)=1.5\\times0.75=1.125$ and $X(--)=0.75^2=0.5625$")
has("pitfall 6", "$F_X(1.125)=3/4$, while $\\Pr(X<1.125)=1/4$; the difference is the jump $p_X(1.125)=1/2$")
has("indicator pmf", "so its pmf is 3/4 at 0 and 1/4 at 1")

# X6: the empirical distribution function
fx = {c: int(at_most(tr, c).sum()) for c in (-3, 0, 3)}
chk("X6 Fhat(-3%)", fx[-3] / T, ".4f", "0.0185")
chk("X6 Fhat(0)", fx[0] / T, ".4f", "0.4520")
chk("X6 Fhat(+3%)", fx[3] / T, ".4f", "0.9885")
anchor("A13-29", "; ".join(f"Fhat({c:+d}%) = {fx[c]}/{T} = {g(fx[c] / T)}" for c in (-3, 0, 3)),
       "Fhat(-3%) = 108/5849 = 0.01846469482; Fhat(+0%) = 2644/5849 = 0.4520430843; Fhat(+3%) = 5782/5849 = 0.9885450504")
has("X6 text", "It is 0.0185 at −3%, the 108 falls; 0.4520 at 0; and 0.9885 at +3%")
i_min, i_max = int(R.argmin()), int(R.argmax())
chk("X6 minimum", R[i_min], ".2%", "-9.70%")
chk("X6 maximum", R[i_max], "+.2%", "+9.25%")
assert (tr.dates[i_min], tr.dates[i_max]) == ("2025-04-07", "2025-04-10")
has("X6 note extremes", "The smallest return, −9.70% on 7 April 2025, and the largest, +9.25% on 10 April 2025")
anchor("A13-30", f"min {pc(R[i_min])} on {tr.dates[i_min]}; max {pc(R[i_max])} on {tr.dates[i_max]}",
       "min -9.69969699% on 2025-04-07; max 9.251191375% on 2025-04-10")

# X7: the 1% bins
for (lo, hi), c in zip(BINS, bins, strict=True):
    ex = sum(1 for r in tr.RF if (lo is None or r > Fraction(lo, 100)) and (hi is None or r <= Fraction(hi, 100)))
    assert ex == c, ("bin guard differs from the exact count", lo, hi)
assert bins == [15, 29, 64, 144, 516, 1876, 2272, 696, 170, 37, 17, 13] and sum(bins[:3]) == nA
has("X7 counts", "15, 29, 64, 144, 516, 1,876, 2,272, 696, 170, 37, 17 and 13")
shares = [round(100 * c / T, 2) for c in bins]
assert not any(tie(c / T, ".2%") for c in bins)
chk("X7 printed shares sum", sum(shares), ".2f", "99.99")
anchor("A13-31", "counts " + ", ".join(map(str, bins)),
       "counts 15, 29, 64, 144, 516, 1876, 2272, 696, 170, 37, 17, 13")

# KC 6
n_le1, n_lem1 = int(at_most(tr, 1).sum()), int(at_most(tr, -1).sum())
assert (n_le1, n_lem1, fx[0]) == (4916, 768, n_dn)
chk("KC6 Fhat(0)", fx[0] / T, ".4f", "0.4520")
chk("KC6 interval", (n_le1 - n_lem1) / T, ".4f", "0.7092")
has("KC6 counts", "(4,916-768)/5,849=4,148/5,849=0.7092")
anchor("A13-21", f"Fhat(0) = {fx[0]}/{T} = {g(fx[0] / T)}; Pr(-1% < R <= 1%) = ({n_le1} - {n_lem1})/{T}",
       "Fhat(0) = 2644/5849 = 0.4520430843; Pr(-1% < R <= 1%) = (4916 - 768)/5849")

# ====================================================================== Section 7: the printed code, run on the lab's file
code = re.search(r"```python\n(.*?)```", TEXT, re.DOTALL)
assert code is not None
src = code.group(1)
assert max(len(ln) for ln in src.splitlines()) <= 80, "a code line is longer than 80 characters"
buf = io.StringIO()
cwd = os.getcwd()
try:
    os.chdir(ROOT / "labs" / "LM13_lab")
    with contextlib.redirect_stdout(buf):
        exec(compile(src, "src/lm13.md", "exec"), {})  # noqa: S102 - the module's own code block
finally:
    os.chdir(cwd)
out = buf.getvalue().splitlines()
expect = ["{'AB': 32, 'A': 108, 'B': 489, 'N': 5848}", "0.065440 0.065440", "0"]
print("printed code output:", out)
assert out == expect, out
for e in expect:
    assert e in TEXT.replace("−", "-"), e
has("code comment 1", "# {'AB': 32, 'A': 108, 'B': 489, 'N': 5848}")
has("code comment 2", "# 0.065440 0.065440")
x10 = 158.40 / 176.00 - 1
assert repr(x10) == "-0.09999999999999998" and not x10 <= -0.10 and x10 <= -0.10 + 1e-12
assert Fraction("158.40") / Fraction("176.00") - 1 == Fraction(-1, 10)
has("pitfall 7", "176.00 → 158.40 is −10% exactly. Floating-point division gives −0.09999999999999998")
has("KC7", "$5,850-2=5,848$")

# ====================================================================== problems and solutions
# P1
n_dn2, n_up2 = int(at_most(tr, -2).sum()), int(at_least(tr, 2).sum())
assert (n_dn2, n_up2) == (252, 237)
chk("P1 Pr(R<=-2%)", n_dn2 / T, ".2%", "4.31%")
chk("P1 Pr(R>=2%)", n_up2 / T, ".2%", "4.05%")
chk("P1 C (exact)", (n_dn2 + n_up2) / T, ".2%", "8.36%")
chk("P1 C (printed sum)", 0.0431 + 0.0405, ".2%", "8.36%")
chk("P1 A (product)", 0.0431 * 0.0405, ".2%", "0.17%")
chk("P1 B", 1 - (1 - 0.0431) * (1 - 0.0405), ".2%", "8.19%")
has("P1 exact", "exactly $489/5,849$")
anchor("A13-45", f"Pr(abs(R)>=2%) {n_dn2 + n_up2}/{T} = {pc((n_dn2 + n_up2) / T)}", "Pr(abs(R)>=2%) 489/5849 = 8.360403488%")
# P2
mp10 = r10[1:] & r10[:-1]
n2, a2, b2, ab2 = int(mp10.sum()), int((A & mp10).sum()), int((Bm & mp10).sum()), int((A & Bm & mp10).sum())
assert (n2, a2, b2, ab2) == (2771, 36, 186, 15)
chk("P2 base", a2 / n2, ".3%", "1.299%")
chk("P2 hit", ab2 / a2, ".2%", "41.67%")
chk("P2 false alarms", (b2 - ab2) / (n2 - a2), ".3%", "6.252%")
chk("P2 option A", ab2 / a2, ".1%", "41.7%")
chk("P2 option C", a2 / n2, ".2%", "1.30%")
p2t1, p2t2 = 0.01299 * 0.4167, 0.98701 * 0.06252
assert abs(0.98701 - (1 - 0.01299)) < 1e-15
chk("S2 first term", p2t1, ".6f", "0.005413")
chk("S2 second term", p2t2, ".5f", "0.06171")
chk("S2 ratio from the printed terms", 0.005413 / (0.005413 + 0.06171), ".2%", "8.06%")
chk("S2 from the printed inputs", p2t1 / (p2t1 + p2t2), ".2%", "8.06%")
chk("S2 exact", ab2 / b2, ".2%", "8.06%")
anchor("A13-46", f"pairs {n2}; base {a2}/{n2} = {pc(a2 / n2)}; hit {ab2}/{a2} = {pc(ab2 / a2)}; false alarms "
       f"{b2 - ab2}/{n2 - a2} = {pc((b2 - ab2) / (n2 - a2))}",
       "pairs 2771; base 36/2771 = 1.299169975%; hit 15/36 = 41.66666667%; false alarms 171/2735 = 6.252285192%")
# P4: three events on the triples
e0, e1, e2 = f2[:-2], f2[1:-1], f2[2:]
singles = (int(e0.sum()), int(e1.sum()), int(e2.sum()))
pairs3 = (int((e0 & e1).sum()), int((e0 & e2).sum()), int((e1 & e2).sum()))
all3, un3 = int((e0 & e1 & e2).sum()), int((e0 | e1 | e2).sum())
assert len(e0) == n3 and singles == (252, 252, 252) and pairs3 == (38, 34, 38) and all3 == 8
assert un3 == sum(singles) - sum(pairs3) + all3 == 654
has("P4 counts", "Each day has 252 falls; days 1 and 2 share 38, days 1 and 3 share 34, days 2 and 3 share 38, and all three share 8")
has("S4 union", "$3\\times252-38-34-38+8=654$ triples, 11.19%")
chk("S4 union share", un3 / n3, ".2%", "11.19%")
chk("S4 bound share", sum(singles) / n3, ".2%", "12.93%")
has("S4 bound", "$756/5,847=12.93%$")
anchor("A13-47", f"triples {n3}; singles {singles[0]}, {singles[1]}, {singles[2]}; pairs 1-2 {pairs3[0]}, 1-3 {pairs3[1]}, "
       f"2-3 {pairs3[2]}; all three {all3}; union {un3} ({pc(un3 / n3)}); bound {sum(singles)} ({pc(sum(singles) / n3)})",
       "triples 5847; singles 252, 252, 252; pairs 1-2 38, 1-3 34, 2-3 38; all three 8; union 654 (11.18522319%); bound 756 (12.92970754%)")
# P5: three down days
d0, d1, d2 = dn[:-2], dn[1:-1], dn[2:]
c0, c01, c012 = int(d0.sum()), int((d0 & d1).sum()), int((d0 & d1 & d2).sum())
m1, m2 = int(d1.sum()), int(d2.sum())
assert (c0, c01, c012, m1, m2) == (2642, 1225, 542, 2643, 2644)
has("P5 counts", "2,642 have a down first day ($R<0$), 1,225 a down first and second day, and 542 three down days")
has("P5 margins", "Days 1, 2 and 3 are down in 2,642, 2,643 and 2,644 triples")
chk("S5 factor 1", c0 / n3, ".4f", "0.4519")
chk("S5 factor 2", c01 / c0, ".4f", "0.4637")
chk("S5 factor 3", c012 / c01, ".4f", "0.4424")
chk("S5 chain from the printed factors", 0.4519 * 0.4637 * 0.4424, ".2%", "9.27%")
chk("S5 exact", c012 / n3, ".2%", "9.27%")
chk("S5 margin 2", m1 / n3, ".4f", "0.4520")
chk("S5 margin 3", m2 / n3, ".4f", "0.4522")
chk("S5 independence from the printed margins", 0.4519 * 0.4520 * 0.4522, ".2%", "9.24%")
chk("S5 independence exact", (c0 / n3) * (m1 / n3) * (m2 / n3), ".2%", "9.24%")
assert c01 / c0 > m1 / n3 > c012 / c01
anchor("A13-48", f"{c0}/{n3} = {g(c0 / n3)}, {c01}/{c0} = {g(c01 / c0)}, {c012}/{c01} = {g(c012 / c01)}",
       "2642/5847 = 0.4518556525, 1225/2642 = 0.463663891, 542/1225 = 0.4424489796")
# P6: the fifty-fifty horizon
n_half = log(0.5) / log(1 - p1)
chk("S6 n", n_half, ".2f", "37.19")
assert math.ceil(n_half) == 38
chk("S6 at 38", 1 - (1 - p1) ** 38, ".2%", "50.75%")
chk("S6 at 37", 1 - (1 - p1) ** 37, ".2%", "49.82%")
nb38, left38, hit38 = blocks(38)
assert (nb38, left38, hit38) == (153, 35, 50)
has("P6 blocks", "TR23 has 153 consecutive blocks of $n$ sessions from 3 January 2003, with the last 35 returns left out, and 50 of them hold a fall")
chk("S6 data share", hit38 / nb38, ".2%", "32.68%")
anchor("A13-49", f"at 37 {pc(1 - (1 - p1) ** 37)}, at 38 {pc(1 - (1 - p1) ** 38)}; blocks of 38: {nb38}, "
       f"left out {left38}, with a fall {hit38} ({pc(hit38 / nb38)})",
       "at 37 49.82131872%, at 38 50.74785276%; blocks of 38: 153, left out 35, with a fall 50 (32.67973856%)")
# P7: falls of 5% or more by regime
f5 = at_most(tr, -5)
c57, c510 = int((f5 & r7).sum()), int((f5 & r10).sum())
assert (c57, c510) == (8, 7)
has("P7 counts", "8 of the 3,077 days of the 7% regime and 7 of the 2,772 days of the 10% regime")
chk("S7 share 7", c57 / n7, ".4%", "0.2600%")
chk("S7 share 10", c510 / n10, ".4%", "0.2525%")
chk("S7 likelihood ratio from the printed shares", 0.2525 / 0.2600, ".3f", "0.971")
chk("S7 likelihood ratio exact", (c510 / n10) / (c57 / n7), ".3f", "0.971")
po7 = (n10 / n7) * 0.971
chk("S7 posterior via the printed 0.971", po7 / (1 + po7), ".1%", "46.7%")
chk("S7 posterior exact", c510 / (c57 + c510), ".1%", "46.7%")
chk("S7 prior", n10 / T, ".1%", "47.4%")
has("S7 fraction", "$7/15=46.7%$")
anchor("A13-50", f"{c57}/{n7} = {pc(c57 / n7)}; {c510}/{n10} = {pc(c510 / n10)}", "8/3077 = 0.2599935002%; 7/2772 = 0.2525252525%")
# P8
lr16 = 0.55 ** 16 * 0.45 ** 8 / 0.5 ** 24
chk("S8 likelihood ratio", lr16, ".4f", "1.9780")
chk("S8 square of the printed 1.4064", 1.4064 ** 2, ".4f", "1.9780")
chk("S8 posterior odds from the printed ratio", (0.1 / 0.9) * 1.9780, ".5f", "0.21978")
chk("S8 posterior from the printed odds", 0.21978 / 1.21978, ".2%", "18.02%")
po16 = (0.1 / 0.9) * lr16
chk("S8 posterior exact", po16 / (1 + po16), ".2%", "18.02%")
chk("S8 prior for 1/2, from the printed 1.4064", 1 / (1 + 1.4064), ".2%", "41.56%")
chk("S8 prior for 1/2, exact", 1 / (1 + lr8), ".2%", "41.56%")
anchor("A13-51", f"LR {g(lr16)}", "LR 1.977985201")
# P9
v3: dict[float, int] = {}
for seq in product((1.5, 0.75), repeat=3):
    v = round(seq[0] * seq[1] * seq[2], 9)
    v3[v] = v3.get(v, 0) + 1
assert v3 == {3.375: 1, 1.6875: 3, 0.84375: 3, 0.421875: 1}
assert Fraction(sum(c for v, c in v3.items() if v < 1), 8) == Fraction(1, 2)
has("S9 values", "$1.5^3=3.375$ (1/8), $1.5^2\\times0.75=1.6875$ (3/8), $1.5\\times0.75^2=0.84375$ (3/8) and $0.75^3=0.421875$ (1/8)")
has("S9 probability", "So $\\Pr(W_3<W_0)=1/2$")
anchor("A13-52", "; ".join(f"{g(v)}: {c}/8" for v, c in sorted(v3.items(), reverse=True)),
       "3.375: 1/8; 1.6875: 3/8; 0.84375: 3/8; 0.421875: 1/8")
# P10
chk("S10 joint", nDD / nP, ".4f", "0.2096")
chk("S10 Pr(X=1)", (nDD + nDU) / nP, ".4f", "0.4519")
chk("S10 Pr(Y=1)", (nDD + nUD) / nP, ".4f", "0.4521")
chk("S10 product of the printed", 0.4519 * 0.4521, ".4f", "0.2043")
chk("S10 product exact", (nDD + nDU) * (nDD + nUD) / nP ** 2, ".4f", "0.2043")
has("S10 fraction", "$\\Pr(X=1,Y=1)=1,226/5,848=0.2096$")
anchor("A13-53", f"Pr(X=1,Y=1) {nDD}/{nP} = {g(nDD / nP)}", "Pr(X=1,Y=1) 1226/5848 = 0.2096443228")
# P11
has("S11", "32, 76, 457 and 5,283 days")
has("S11 regime", "15 of the 186 days after a big move fell 3% or more, 8.06%")
has("S11 hit", "The 15 are 41.67% of the regime's 36 falls")
# P12
p_, q_ = 0.55, 0.45
chk("S12 1 - q^2", 1 - q_ ** 2, ".4f", "0.7975")
chk("S12 2pq", 2 * p_ * q_, ".4f", "0.4950")
chk("S12 1 - p^2", 1 - p_ ** 2, ".4f", "0.6975")
anchor("A13-54", f"1 - q^2 = {g(1 - q_ ** 2)}; 2pq = {g(2 * p_ * q_)}; 1 - p^2 = {g(1 - p_ ** 2)}",
       "1 - q^2 = 0.7975; 2pq = 0.495; 1 - p^2 = 0.6975")
# MC keys vary: C, B, A, C
keys = re.findall(r"(?m)^\d+\. \*\*([ABC])\*\* is correct", TEXT)
assert keys == ["C", "B", "A", "C"], keys

# ====================================================================== anchors the text does not print
# A13-55: the lab extension's 70.4% (a lab result); A13-56: the dividend gap (a data fact behind "never mix")
absR = np.abs(R)
idx = np.arange(5, T)
prev = np.array([bool((absR[i - 5:i] >= 0.02 - 1e-12).any()) for i in idx])
cw = fall[idx]
anchor("A13-55", f"days {len(idx)}; falls with abs(R) >= 2% in the previous five sessions {int((prev & cw).sum())}/{int(cw.sum())} "
       f"= {pc((prev & cw).sum() / cw.sum())}", "days 5844; falls with abs(R) >= 2% in the previous five sessions 76/108 = 70.37037037%")
gap = R - tr.Rp
j = int(gap.argmax())
anchor("A13-56", f"max R - Rp = {g(gap[j] * 1e4)} bp on {tr.dates[j]}", "max R - Rp = 83.93463079 bp on 2016-06-27")

# ====================================================================== overview and summary figures
has("overview odds", "$0.018815\\times3.7215=0.07002$")
has("overview pairs", "1,226 times in 5,848 day pairs, against 1,195.0")
has("overview two falls", "13 times, against 2.0")
has("overview blocks", "31.1% of blocks of 20 sessions")
has("overview blocks data", "20.9% of its 292 blocks")
has("summary Bayes", "turn 1.847%, 29.63% and 7.962% into 6.54%")

assert SEEN == set(ANCHORS), sorted(set(ANCHORS) - SEEN)
print()
print(f"anchor differences ({len(ANCHOR_DIFFS)}):")
for d in ANCHOR_DIFFS:
    print("   ", d)
print(f"\nall {N_CHECKS} checks passed")
