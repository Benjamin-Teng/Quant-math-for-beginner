"""Every number that LM32 (VaR, Expected Shortfall and Drawdown) prints, computed and checked against src/lm32.md.

Run:  uv run python data/lm32_numbers.py
      (after data/vol3_series.py, data/vol5_series.py and data/vol5_rules.py; and after data/lm32_charts.py, whose
      chart files and widget block this script checks)

Inputs and conventions: data/lm32_common.py, which keeps the code of data/vol6_anchors_lm32.py (the Stage 1 anchor
script): TR23 and LM26's forecasts through data/lm26_common.py, E5 through vol5_series.frames("E5"), the through case
through vol5_rules (no rule is re-implemented here). The module text is src/lm32.md; plans/vol-6-anchors.md, "LM32",
holds the Stage 1 anchors A32-01 .. A32-57.

Part 1 compares each anchor line, as data/lm32_common.py recomputes it, with the anchor table's Value column: a
difference is reported, never forced.

Part 2 checks the text (each check stops the script on a failure):
  chk(label, value, fmt, printed, count)  format(value, fmt) equals the printed string, the value is not a rounding
                                   tie of that format, and the printed string occurs in the body as a whole number:
                                   not preceded by a digit, a point or a minus sign (ASCII or U+2212), not followed
                                   by a digit. count is the number of such occurrences: at least one when omitted,
                                   exactly count when given, and a string that occurs more than once must be given
                                   its count. Hand computations are redone from the printed, rounded inputs
                                   (PITFALLS section 7).
  sci(label, value, printed, count) a number printed as m\\times10^{e}, compared at the printed mantissa; counted the
                                   same way.
  has(label, text, count)          a literal string (a date, a phrase, a table row) occurs in the module file, at
                                   least once or exactly count times; a repeated string must be given its count.
The body is the text between the front matter and "## Glossary". The front matter's overview restates numbers of the
body: has() pins each of its bullets, and its numbers are not part of the body's counts. The glossary and the
references hold no computed number and are not scanned.
Every check that passes pins the places it found (a string found once, or found exactly count times). At the end,
every number of the overview and the body (a decimal, a number with thousands separators or a plain integer; an
integer that ends a name, R1 or LM32, or is a subscript, j_1, is not a number) must lie in a pinned place or be
listed, with its count and a reason, in ALLOW: equation references, levels, numbering, formula constants, inputs and
citation years. Computed integers (dates, ranks, counts, horizons) are pinned by has() phrases. A number added
to the text then fails the script until it is checked or listed.
It also runs experiments 9 and 10, which the anchor script does not have (Stage 2's second pass, the checker's S3):
the permutations and the stationary bootstrap of TR23's days behind [[eg:horizon]]'s overlapping ten-session VaR,
default_rng([9, 20261011]) and default_rng([10, 20261011]), 20 batches of 500 each.
It runs the module's Python code block (Section 9) and compares its results with the text, checks the chart
files and the widget block against the computations, checks the structure (labels, tags, citations) and the glosses of
the 中文導讀 boxes. At the end it asserts that the numbers no check pinned are exactly ALLOW's and prints "all N checks
passed".
"""
import json
import math
import re
import string
import sys
from collections import Counter
from datetime import date
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lm32_common as K
import numpy as np
from scipy import integrate, stats

ROOT = HERE.parent
MD = ROOT / "src" / "lm32.md"
ANCHORS = ROOT / "plans" / "vol-6-anchors.md"
CHARTS = ROOT / "src" / "data"
RAW = MD.read_text(encoding="utf-8")
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


# ====================================================================== text helpers
def norm_text(s: str) -> str:
    """The module text with TeX thousands separators, escaped percent signs, \\text{} and minus signs made plain."""
    s = s.replace("{,}", ",").replace("\\%", "%").replace("\u2212", "-").replace("\\,", "")
    return re.sub(r"\\text\{\s*([^}]*)\}", r" \1", s)


TEXT = norm_text(RAW)
FM_END = TEXT.index("\n---\n", 4) + 5                  # the front matter, from the first '---' to the second
OV0 = TEXT.index("\noverview:\n")                       # its overview, the only part of it with numbers
B0, B1 = FM_END, TEXT.index("\n## Glossary")          # the body
N_CHECKS = 0
PINNED: list[tuple[int, int]] = []                    # spans of TEXT that a passing check pins
UNCOUNTED: list[str] = []                             # repeated strings checked without their count
ANCHOR_DIFFS: list[str] = []
WHOLE = r"(?<![\d.\-−])"                          # not inside a longer number, and not signed


def occ(printed: str) -> list[tuple[int, int]]:
    """The places of the body where the printed number occurs as a whole number: 0.33 is not inside 0.331, 0.32 not
    inside 10.32, and 3.57 not inside -3.57 (the signed form is its own string)."""
    rx = re.compile(WHOLE + re.escape(printed) + r"(?![\d])(?!\.\d)(?!,\d{3}(?!\d))")
    return [m.span() for m in rx.finditer(TEXT, B0, B1)]


def in_text(printed: str) -> bool:
    return bool(occ(printed))


def pin(label: str, what: str, spans: list[tuple[int, int]], count: int | None) -> None:
    """Assert the count of places (at least one, or exactly count) and pin them when that fixes every one of them."""
    if count is None:
        assert spans, f"{label}: {what!r} not found in src/lm32.md"
        if len(spans) > 1:
            UNCOUNTED.append(f"{label}: {what!r} occurs {len(spans)} times")
    else:
        assert len(spans) == count, f"{label}: {what!r} occurs {len(spans)} times, not {count}"
    if count is not None or len(spans) == 1:
        PINNED.extend(spans)


def tie(value: float, fmt: str) -> bool:
    m = re.search(r"\.(\d+)", fmt)
    d = int(m.group(1)) if m else 0
    scaled = abs(value) * 10**d
    return abs(scaled - math.floor(scaled) - 0.5) < 1e-9


def chk(label: str, value: float, fmt: str, printed: str, count: int | None = None, in_md: bool = True) -> None:
    global N_CHECKS
    got = format(value, fmt)
    print(f"CHECK {label}: {got} (printed {printed})")
    assert got == printed, (label, got, printed)
    assert not tie(value, fmt), ("rounding tie: print more digits", label, value)
    if in_md:
        pin(label, printed, occ(printed), count)
    N_CHECKS += 1


def pct(label: str, frac: float, d: int, printed: str, count: int | None = None, in_md: bool = True) -> None:
    chk(label, 100 * frac, f".{d}f", printed, count, in_md)


def chks(label: str, values: list[float] | np.ndarray, fmt: str, printed: list[str],
         counts: list[int | None] | None = None) -> None:
    for k, (v, p) in enumerate(zip(values, printed, strict=True)):
        chk(f"{label} [{k + 1}]", float(v), fmt, p, counts[k] if counts else None)


def cnt(label: str, value: int, printed: str, count: int | None = None) -> None:
    """An integer count, printed with thousands separators."""
    chk(label, float(value), ",.0f", printed, count)


def has(label: str, text: str, count: int | None = None) -> None:
    """text as in src/lm32.md; its places are found in the normalized text (TEXT), the whole file."""
    global N_CHECKS
    t = norm_text(text)
    rx = ("(?<!\\d)" if t[:1].isdigit() else "") + re.escape(t) + ("(?!\\d)" if t[-1:].isdigit() else "")
    spans = [m.span() for m in re.finditer(rx, TEXT)]
    pin(label, text[:80], spans, count)
    print(f"CHECK {label}: '{text[:80]}' in text")
    N_CHECKS += 1


def sci(label: str, value: float, printed: str, count: int | None = None) -> None:
    """printed is the TeX in the module, m\\times10^{e}; the value must round to m at m's digits."""
    global N_CHECKS
    m = re.fullmatch(r"([\d.]+)\\times10\^\{?(-?\d+)\}?", printed)
    assert m, printed
    mant, ex = m.group(1), int(m.group(2))
    digits = len(mant.split(".")[1]) if "." in mant else 0
    got = f"{value / 10**ex:.{digits}f}"
    assert got == mant, (label, got, printed)
    assert not tie(value / 10**ex, f".{digits}f"), ("rounding tie", label, value)
    pin(label, printed, occ(printed), count)
    print(f"CHECK {label}: {value:.3e} (printed {printed})")
    N_CHECKS += 1


def long_date(d: str) -> str:
    """2019-02-27 -> '27 February 2019'."""
    y, mo, dd = d.split("-")
    return f"{int(dd)} {MONTHS[int(mo) - 1]} {y}"


def short_date(d: str) -> str:
    """2019-02-27 -> '27 Feb 2019' (the tables)."""
    y, mo, dd = d.split("-")
    return f"{int(dd)} {MONTHS[int(mo) - 1][:3]} {y}"


# ====================================================================== part 1: the anchors
def _anchor_values() -> dict[str, str]:
    rows: dict[str, str] = {}
    sec = ANCHORS.read_text(encoding="utf-8").split("\n## LM32", 1)[1].split("\n## ", 1)[0]
    for line in sec.splitlines():
        if line.startswith("| A32-"):
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
            rows[cells[0]] = cells[3].strip("`").replace("\\|", "|")
    return rows


ANCHOR_ROWS = _anchor_values()
assert len(ANCHOR_ROWS) == 57, len(ANCHOR_ROWS)
for line in K.OUT:
    aid, got = line.split(" ", 1)
    ok = got == ANCHOR_ROWS[aid]
    print(f"ANCHOR {aid}: {'ok' if ok else 'DIFFERS'}")
    if not ok:
        ANCHOR_DIFFS.append(f"{aid}:\n      script {got}\n      anchor {ANCHOR_ROWS[aid]}")

# ====================================================================== part 2: the text
R, T, U, U2 = K.R, K.T, K.U, K.U2
MODELS, VAR, ES7, k7, i7 = K.MODELS, K.VAR, K.ES7, K.k7, K.i7
ret, nR, SP = K.ret, K.nR, K.SP
var_h, es_h, es_k, var_n, es_n, var_t, es_t = K.var_h, K.es_h, K.es_k, K.var_n, K.es_n, K.var_t, K.es_t

# ---------------------------------------------------------------- data role (notation note)
cnt("T", T, "5,849", 4)
chk("TR23 years", K.C.years, ".4f", "23.7645")
assert K.C.dates_all[0] == "2003-01-02"
has("TR23 years from", "23.7645 years from the close of 2 January 2003")
chk("A", K.A, ".2f", "246.12", 3)
assert float(R.min()) > -1
cnt("rules' returns", nR, "1,851", 2)
assert K.rdates[0] == "2019-03-05" and K.rdates[-1] == "2026-10-08" and K.paths["R1"].dates[0] == "2019-03-04"
has("rules' start", "1,851 sessions from 5 March 2019 (7.60 years from the close of 4 March 2019)")
has("rules' recursion", "net returns on the wealth frame, (27.1)–(27.2),")
has("hygiene fixing date", "**fixed in advance** on 24 October 2026")
has("hygiene labels", "**Constructed** and **hypothetical** inputs are labelled where they appear")
has("hygiene tests", "Section 3 runs one test, Section 7 twelve and Section 8 eight")
for lab_ in ("A hypothetical sample of $T=180$", "A hypothetical daily return is normal", "A hypothetical wealth path",
             "Over 2,000 hypothetical days", "500 hypothetical days", "A hypothetical model gives $-4\\%$",
             "A hypothetical $\\sigma=20\\%$", "a hypothetical 20% limit", "(*constructed*). Compare",
             "(*constructed*). At $u=5\\%$"):
    has("label in place", lab_, 3 if lab_ == "a hypothetical 20% limit" else None)
chk("rules' years", K.yrs_r, ".2f", "7.60")
assert all(p.ruin is None for p in K.paths.values())          # no path reaches wealth <= 0

# ---------------------------------------------------------------- the case and its exhibit
v7 = {m: 100 * float(VAR[m][k7]) for m in MODELS}
e7 = {m: 100 * ES7[m] for m in MODELS}
loss7 = -100 * float(R[i7])
chk("loss 7 April", loss7, ".2f", "9.70", 2)
assert int(np.argmin(R)) == i7
chks("X1 VaR", [v7[m] for m in MODELS], ".2f", ["3.53", "2.66", "3.08", "3.57", "3.83", "4.14"],
     [None, 3, None, 5, None, 2])
chks("X1 ES", [e7[m] for m in MODELS], ".2f", ["4.58", "3.06", "4.38", "4.07", "4.39", "5.26"],
     [None, 2, None, None, None, None])
lv = ["2.75", "3.65", "3.15", "2.72", "2.53", "2.34"]
lv_n: list[int | None] = [4, None, None, None, None, 2]
chks("X1 loss / VaR", [loss7 / v7[m] for m in MODELS], ".2f", lv, lv_n)
chks("X1 loss / VaR from the printed 9.70 and VaR", [9.70 / float(f"{v7[m]:.2f}") for m in MODELS], ".2f", lv,
     lv_n)
x1_name = {"HS": "Historical (HS)", "N": "Normal (N)", "t": "Student t (t)", "EWMA": f"EWMA, $\\lambda={K.C.LAM}$",
           "GARCH-n": "GARCH, normal (GARCH-n)", "GARCH-t": "GARCH, Student t (GARCH-t)"}
x1_once = {"GARCH-n": f"{1 / (K.p_n * K.A) / 1e6:.1f} million years ", "GARCH-t": f"{1 / (K.p_t * K.A):.1f} years "}
for m in MODELS:                       # every row of X1 from the computed values
    has(f"X1 row {m}", f"| {x1_name[m]} | {v7[m]:.2f} | {e7[m]:.2f} | {loss7 / v7[m]:.2f} | {x1_once.get(m, '')}|")
has("X1 loss row", f"| The loss on 7 April: {loss7:.2f}% | | | | |")
chk("case range low", min(v7.values()), ".2f", "2.66", 3)
chk("case range high", max(v7.values()), ".2f", "4.14", 2)
assert v7["N"] == min(v7.values()) and v7["GARCH-t"] == max(v7.values())
has("case range", "Their answers ran from 2.66% (a normal law on its last 1,231 returns) to 4.14% (GARCH with")
lo, hi = min(loss7 / v for v in v7.values()), max(loss7 / v for v in v7.values())
chk("case loss / VaR low", lo, ".1f", "2.3")
chk("case loss / VaR high", hi, ".1f", "3.6")
chk("case low from printed", 9.70 / 4.14, ".1f", "2.3")
chk("case high from printed", 9.70 / 2.66, ".1f", "3.6")
has("case ratio sentence", "That loss was 2.3 to 3.6 times each model's value at risk, and 1.8 to 3.2 times its expected")
chk("case loss / ES low", min(loss7 / e for e in e7.values()), ".1f", "1.8", 2)
chk("case loss / ES high", max(loss7 / e for e in e7.values()), ".1f", "3.2")
chk("case loss / ES low from printed", 9.70 / 5.26, ".1f", "1.8", 2)
chk("case loss / ES high from printed", 9.70 / 3.06, ".1f", "3.2")
pct("ten sessions", -K.real10, 2, "8.92", 3)
assert K.dates[i7 + 9] == "2025-04-18"
has("X1 ten sessions", "| The loss over 7 to 18 April, ten sessions: 8.92% |")
assert sum(1 for k in K.RULES if K.worst[k] == "2025-04-07") == 7 and K.worst["R7"] == "2020-03-19"
has("case seven of eight", "It was also the worst day for seven of the eight allocation rules")
assert K.dates[i7 - 1] == "2025-04-02" and K.gap_days - 1 == 4
has("case four days", "The next session came after four days without trading")
has("case date", "On Monday 7 April the index fell 9.70%, the worst of its 5,849 daily returns since 2003")
chk("7 April log return", 100 * float(np.log1p(R[i7])), ".2f", "-10.20", 2)
assert K.dates[i7 - K.W_] == "2020-03-12" and K.W_ == 1231
has("X1 note window", "HS and N on the 1,231 returns from 12 March 2020, t on its fit of 1 April")
assert K.dates[K.s7] == "2025-04-01"
has("X1 note limit", "The 10% limit capped many stocks (936 listed stocks closed limit-down; Atkinson, 7 April 2025), so the"
    " index return understates the selling")
for f_ in ("lm13.md", "lm14.md"):           # the source fact, echoed as LM13 and LM14 print it (lm13.md:592, lm14.md:627)
    assert "): 936 listed stocks, and 1,702" in (ROOT / "src" / f_).read_text(encoding="utf-8"), f_
has("X1 sessions per year", '"Once in": years of 246.12 sessions')

# ---------------------------------------------------------------- Section 2
x5 = K.x5
assert list(np.round(100 * x5, 1)) == [1.2, -0.8, 0.3, -2.5, 0.6]
has("E1 returns", "+1.2, −0.8, +0.3, −2.5 and +0.6%")
has("E1 u", f"and a large $u={K.u3}$")
assert K.jrank(0.3, 5) == 2
chk("E1 uT", 0.3 * 5, ".1f", "1.5")
has("E1 uT", "Here $uT=1.5$, so $j=2$")
pct("E1 VaR", var_h(x5, 0.3), 2, "0.80")
pct("E1 ES", es_h(x5, 0.3), 2, "1.93")
chk("E1 ES from the printed formula", -(1 / 0.3) * (-2.5 / 5 + (0.3 - 1 / 5) * (-0.8)), ".2f", "1.93")
has("E1 ES display", "\\operatorname{ES}=-\\frac1{0.3}\\Big[\\frac{-2.5}{5}+\\Big(0.3-\\frac15\\Big)(-0.8)\\Big]\\\\"
    "=1.93\\%")
pct("E1 mean of two worst", es_k(x5, 0.3), 2, "1.65")
pct("E1 floor estimator", -float(np.sort(x5)[0]), 2, "2.50")
has("E1 floor", "the mean of the $\\lfloor uT\\rfloor=1$ worst, gives 2.50%")
# X2 and its note
assert K.j05 == 293 and int(K.HIST.sum()) == 293
pct("X2 smallest loss in the 293", -float(np.sort(R)[292]), 2, "1.86")
has("X2 note", "the 293 worst of TR23's 5,849 returns as losses, in bins of 0.25 points (the first holds losses from 1.86%)")
assert set(np.round(np.diff(K.EDGES), 10)) == {0.25}          # the bin width the note prints
chk("X2 bin width", float(K.EDGES[1] - K.EDGES[0]), ".2f", "0.25")
pct("X2 VaR", var_h(R, U), 2, "3.57", 5)
pct("X2 ES", es_h(R, U), 2, "4.69", 4)
pct("X2 normal VaR", var_n(K.mu, K.s, U), 2, "2.75", 4)
pct("X2 normal ES", es_n(K.mu, K.s, U), 2, "3.16", 5)
assert K.jrank(U, T) == 59
has("X2 59", "ES averages the 59 worst days, the 59th weighted by (32.2)")
# E2
levels = [0.001, 0.01, 0.025, 0.05]
assert [K.jrank(u, T) for u in levels] == [6, 59, 147, 293]
has("E2 ranks", "| Rank $j$ | 6 | 59 | 147 | 293 |")
e2_var = [100 * var_h(R, u) for u in levels]
e2_es = [100 * es_h(R, u) for u in levels]
chks("E2 VaR", e2_var, ".3f", ["6.313", "3.567", "2.648", "1.862"], [None, 4, None, None])
chks("E2 ES", e2_es, ".3f", ["7.360", "4.689", "3.740", "2.969"], [None, 3, None, None])
has("E2 VaR row", "| VaR (%) | " + " | ".join(f"{v_:.3f}" for v_ in e2_var) + " |")
has("E2 ES row", "| ES (%), (32.2) | " + " | ".join(f"{v_:.3f}" for v_ in e2_es) + " |")
pct("X3 / X2 VaR 2.5% at 2 dp", var_h(R, 0.025), 2, "2.65")
pct("X2 note smallest of the 293 at 2 dp", var_h(R, 0.05), 2, "1.86")
has("E2 LM14", "The 0.1% and 1% VaRs are [[LM14]]'s quantiles")
chk("E2 ES/VaR 1%", es_h(R, U) / var_h(R, U), ".2f", "1.31")
chk("E2 ES/VaR 2.5%", es_h(R, U2) / var_h(R, U2), ".2f", "1.41")
chk("E2 ratio 1% from printed", 4.689 / 3.567, ".2f", "1.31")
chk("E2 ratio 2.5% from printed", 3.740 / 2.648, ".2f", "1.41")
# pitfall: the ceil(uT) mean, the floor(uT) mean and (32.2)
pct("pitfall mean of 59", es_k(R, U), 3, "4.679")
pct("pitfall mean of 58", -float(np.sort(R)[:58].mean()), 3, "4.699")
assert math.floor(U * T) == 58
pct("pitfall (32.2)", es_h(R, U), 3, "4.689", 3)
has("pitfall three values", "(4.679%, 4.699% and 4.689% at 1%)")
# KC 2
assert K.jrank(0.01, 50) == 1
chk("KC 2 uT", 0.01 * 50, ".1f", "0.5", 2)
has("KC 2", "Here $uT=0.5$, so $j=1$")

# ---------------------------------------------------------------- Section 3
chk("E3 mean (LM19)", 100 * K.mu, ".4f", "0.0625")
chk("E3 s (LM19)", 100 * K.s, ".4f", "1.2084")
chk("E3 nu (LM20)", K.nu0, ".3f", "3.065", 2)
chk("E3 location", K.loc0, ".4f", "0.0997")
chk("E3 scale", K.sc0, ".4f", "0.7761")
chk("E3 Phi^-1(0.01)", K.z01, ".4f", "-2.3263")
chk("E3 phi/u", float(stats.norm.pdf(K.z01)) / U, ".4f", "2.6652", 2)
chk("E3 normal VaR from printed", -0.0625 + 1.2084 * 2.3263, ".2f", "2.75", 4)
chk("E3 normal ES from printed", -0.0625 + 1.2084 * 2.6652, ".2f", "3.16", 5)
qt = float(stats.t.ppf(U, K.nu0))
chk("E3 q", qt, ".4f", "-4.4644", 2)
chk("E3 q from the printed nu (the text says the unrounded fit's)", float(stats.t.ppf(U, 3.065)), ".4f", "-4.4646",
    in_md=False)
has("E3 unrounded q", "the unrounded fit's $q=-4.4644$ gives 3.37% and 5.19%")
chk("E3 t VaR", var_t(K.nu0, K.loc0, K.sc0, U), ".2f", "3.37", 2)
chk("E3 t ES", es_t(K.nu0, K.loc0, K.sc0, U), ".2f", "5.19", 3)
chk("E3 t VaR from printed", var_t(3.065, 0.0997, 0.7761, U), ".2f", "3.37", 2)
chk("E3 t ES from printed", es_t(3.065, 0.0997, 0.7761, U), ".2f", "5.19", 3)
has("E3 data", "The data give 3.57% and 4.69%")
assert K.d15 < 1e-12
has("Deep Dive 3 quadrature", "agrees to better than $10^{-12}$ (Section 9)")
# X3
x3 = {
    "Historical VaR": [100 * var_h(R, u) for u in (0.001, 0.01, 0.025)],
    "Historical ES, (32.2)": [100 * es_h(R, u) for u in (0.001, 0.01, 0.025)],
    "Mean of the $j$ worst": [100 * es_k(R, u) for u in (0.001, 0.01, 0.025)],
    "Normal VaR, (32.3)": [100 * var_n(K.mu, K.s, u) for u in (0.001, 0.01, 0.025)],
    "Normal ES": [100 * es_n(K.mu, K.s, u) for u in (0.001, 0.01, 0.025)],
    "Student t VaR, (32.4)": [var_t(K.nu0, K.loc0, K.sc0, u) for u in (0.001, 0.01, 0.025)],
    "Student t ES": [es_t(K.nu0, K.loc0, K.sc0, u) for u in (0.001, 0.01, 0.025)],
}
for name, vals in x3.items():
    row = f"| {name} | " + " | ".join(f"{v:.2f}" for v in vals) + " |"
    for v in vals:
        chk(f"X3 {name}", v, ".2f", f"{v:.2f}", in_md=False)
    has(f"X3 row {name}", row)
hill = {}
for u in (0.001, 0.01):
    vq = K.x0 * (K.kh / (T * u)) ** (1 / K.ah)
    hill[u] = (100 * vq, 100 * vq * K.ah / (K.ah - 1))
has("X3 Hill VaR row", f"| Hill VaR | {hill[0.001][0]:.2f} | {hill[0.01][0]:.2f} | |")
has("X3 Hill ES row", f"| Hill ES | {hill[0.001][1]:.2f} | {hill[0.01][1]:.2f} | |")
N_HILL = {"6.69": 2, "9.23": 2, "3.55": 3, "4.90": 3}      # X3, the Hill paragraph (1% only) and Solution 11
chks("Hill", [hill[0.001][0], hill[0.001][1], hill[0.01][0], hill[0.01][1]], ".2f", ["6.69", "9.23", "3.55", "4.90"],
     [2, 2, 3, 3])
assert abs(es_t(3.065, 0.0997, 0.7761, 0.001) - 11.376) < 0.001 and f"{x3['Student t ES'][0]:.2f}" == "11.37"
has("X3 note labels", "Note: historical rows descriptive, fits in-sample.")
has("X3 note unrounded", "The $t$ cells use the unrounded fit (the rounded one changes the 0.1% ES's last digit)")
assert K.kh == 108 and K.kh / T < 0.025
has("X3 note Hill", "Hill uses the 108 losses of 3% or more, $\\hat\\alpha=3.634$ (Problem 11), and holds for $u\\le k/T$")
has("X3 note six days", "The historical 0.1% figures rest on six days")
has("X3 note SE", "Only the 1% historical VaR carries a standard error ([[eg:precision]])")
# moments and Hill paragraph
has("moments", "TR23's $t$, $\\nu=3.065$, has no fourth moment")
chk("Hill alpha (LM20's)", K.ah, ".2f", "3.63")
has("Hill paragraph", "At $x_0=3\\%$, $k=108$ and $\\hat\\alpha=3.63$ the 1% figures are 3.55% and 4.90% (Problem 11)")
v_h1 = 100 * 0.03 * (108 / (0.01 * 5849)) ** (1 / 3.63)
chk("Hill 1% VaR from the printed alpha", v_h1, ".2f", "3.55", 3)
chk("Hill 1% ES from the printed alpha", v_h1 * 3.63 / 2.63, ".2f", "4.90", 3)
# the derivation the display prints: the tail mean of the fitted power tail is alpha/(alpha - 1) times the level
for u in (0.001, 0.01):
    lev = K.x0 * (K.kh / (T * u)) ** (1 / K.ah)
    num_ = integrate.quad(lambda x_: x_ ** (-K.ah), lev, np.inf)[0]
    den_ = integrate.quad(lambda x_: x_ ** (-K.ah - 1), lev, np.inf)[0]
    assert abs(num_ / den_ - K.ah / (K.ah - 1) * lev) < 1e-9 * lev, u
has("Hill derivation", "whose density there is proportional to $x^{-\\alpha-1}$")
has("not in the book: EVT", "Extreme value theory beyond Hill's estimator is not in this book.")
# E4
assert len(K.R10) == 5840
cnt("E4 overlapping sums", len(K.R10), "5,840")
pct("E4 overlapping VaR", var_h(K.R10, U), 2, "10.49", 5)
pct("E4 sqrt rule", math.sqrt(10) * var_h(R, U), 2, "11.28", 2)
chk("E4 sqrt rule from printed", math.sqrt(10) * 3.567, ".2f", "11.28", 2)
pct("E4 iid normal", K.v10n, 2, "8.02", 2)
pct("E4 iid draws", -float(np.quantile(K.R10iid, U, method="inverted_cdf")), 2, "8.75", 2)
chk("E4 iid batch SE", 100 * K.batch_se_q(K.R10iid, U), ".2f", "0.04", 3)
assert len(K.R10iid) == 100_000
has("E4 experiment", "Experiment 7 draws 100,000 sums with `default_rng([7, 20261011])`, batch SE 0.04")
pct("E4 R1 20 sessions", var_h(K.R20["R1"], U), 2, "8.66")
pct("E4 R1 one-day VaR", var_h(ret["R1"], U), 3, "2.102")
chk("E4 R1 sqrt(20) from printed", math.sqrt(20) * 2.102, ".2f", "9.40")
pct("E4 R1 sqrt(20)", math.sqrt(20) * var_h(ret["R1"], U), 2, "9.40")
for row_ in ("| The 5,840 overlapping compound returns | 10.49 |", "| The $\\sqrt{10}$ rule, $\\sqrt{10}\\times3.567\\%$ | 11.28 |",
             "| Iid normal log returns with TR23's $\\bar r$ and $s_r$ | 8.02 |",
             "| Ten days drawn independently from TR23 (experiment 7) | 8.75 |"):
    has("E4 table", row_)
has("E4 shape", "moves the iid figure from 8.02% to 8.75%.")
has("E4 order", "The real order of days moves the figure to 10.49%.")


def v10_rows(X: np.ndarray) -> np.ndarray:
    """The 99% VaR of the overlapping ten-session compound returns of each row of X (5,840 sums of 5,849 days)."""
    cs_ = np.concatenate([np.zeros((X.shape[0], 1)), np.cumsum(np.log1p(X), axis=1)], axis=1)
    return -np.quantile(np.expm1(cs_[:, 10:] - cs_[:, :-10]), U, axis=1, method="inverted_cdf")


v10_real = var_h(K.R10, U)
assert abs(float(v10_rows(R[None, :])[0]) - v10_real) < 1e-15
# experiment 9: permutations of TR23's 5,849 returns (20 batches of 500 `permuted` copies), the order destroyed
rng9 = np.random.default_rng([9, K.SEED])
P9 = np.concatenate([v10_rows(rng9.permuted(np.tile(R, (500, 1)), axis=1)) for _ in range(20)])
chk("E4 permutation median", 100 * float(np.quantile(P9, 0.5, method="inverted_cdf")), ".1f", "8.7")
chk("E4 permutation median batch SE", 100 * K.batch_se_q(P9, 0.5), ".3f", "0.004")
n9 = int(np.sum(P9 >= v10_real - K.EPS))
assert n9 == 2 and len(P9) == 10_000, n9
has("E4 permutations", "Their median is 8.7% (batch SE 0.004), and 2 of 10,000 reach 10.49% (experiment 9, "
    "`default_rng([9, 20261011])`)")
# experiment 10: the stationary bootstrap of TR23's days (l = 145, LM22's draw order), 20 batches of 500 resamples
rng10 = np.random.default_rng([10, K.SEED])
B10 = np.concatenate([v10_rows(R[K.stat_idx(rng10, T, 145, 500)]) for _ in range(20)])
assert len(B10) == 10_000
chk("E4 bootstrap SE of 10.49", 100 * float(B10.std()), ".1f", "1.0")
chk("E4 bootstrap SE batch SE", 100 * K.batch_se_sd(B10), ".3f", "0.006")
has("E4 bootstrap", "A stationary bootstrap (experiment 10, `default_rng([10, 20261011])`, $\\ell=145$, 10,000 resamples) "
    "gives it a standard error of 1.0 point (batch SE 0.006)")
assert 100 * (math.sqrt(10) * var_h(R, U) - v10_real) < 100 * float(B10.std())   # the rule's gap is within one SE
# 導讀 of Section 3: the normal's shortfall, from the printed values too
chk("zh 3 VaR gap", 100 * (var_h(R, U) - var_n(K.mu, K.s, U)), ".2f", "0.82")
chk("zh 3 VaR gap from printed", 3.57 - 2.75, ".2f", "0.82")
chk("zh 3 ES gap", 100 * (es_h(R, U) - es_n(K.mu, K.s, U)), ".2f", "1.53")
chk("zh 3 ES gap from printed", 4.69 - 3.16, ".2f", "1.53")
# KC 3 (b): what the normal and the t miss at 2.5%, from X3's printed cells and unrounded
kc3: dict[str, str] = {}
for lbl_, unr, prd, s_ in (("normal VaR", 100 * (var_h(R, U2) - var_n(K.mu, K.s, U2)), 2.65 - 2.31, "0.34"),
                           ("normal ES", 100 * (es_h(R, U2) - es_n(K.mu, K.s, U2)), 3.74 - 2.76, "0.98"),
                           ("t ES", 100 * es_h(R, U2) - es_t(K.nu0, K.loc0, K.sc0, U2), 3.74 - 3.73, "0.01"),
                           ("t VaR", 100 * var_h(R, U2) - var_t(K.nu0, K.loc0, K.sc0, U2), 2.65 - 2.34, "0.31")):
    chk(f"KC 3 (b) {lbl_}", unr, ".2f", s_, in_md=False)          # the two sentences below are the text checks
    chk(f"KC 3 (b) {lbl_} from printed", prd, ".2f", s_, in_md=False)
    kc3[lbl_] = s_
has("KC 3 (b)", f"The normal's VaR and ES are {kc3['normal VaR']} and {kc3['normal ES']} points low")
has("KC 3 (b) t", f"The $t$'s ES is within {kc3['t ES']} points, but its VaR is {kc3['t VaR']} points low")
lm15 = (ROOT / "src" / "lm15.md").read_text(encoding="utf-8")
assert "79.0, 36.6, 19.6 days against 108, 44, 15" in lm15          # lm15.md:461, the t's days at or below -3, -4, -5%
t_at, d_at = {}, {}
for lv_, t_days, d_days in ((0.03, "79.0", 108), (0.05, "19.6", 15)):
    t_at[lv_] = T * float(stats.t.cdf(-100 * lv_, K.nu0, K.loc0, K.sc0))
    d_at[lv_] = int(np.sum(R <= -lv_ + K.EPS))
    assert f"{t_at[lv_]:.1f}" == t_days and d_at[lv_] == d_days
assert t_at[0.03] - t_at[0.05] < d_at[0.03] - d_at[0.05] and t_at[0.05] > d_at[0.05]   # too few from -3% to -5%, too many beyond
has("KC 3 (a)", "The order of days raised it in [[eg:horizon]]. Under GARCH ([[eg:mc10]]), mean reversion from a high "
    "variance lowers it, and the variance's random feedback raises it")

# ---------------------------------------------------------------- Section 4
xs = K.xs
j1, j2, cov = K.binom_interval(T, U)
assert (j1, j2) == (44, 75)
for row_ in ("| Ranks $j_1$, $j_2$ | 44, 75 | 2,850, 3,000 |", "| Interval (%) | −4.016 to −3.425 | 0.069 to 0.114 |",
             "| Coverage | 0.9587 | 0.9502 |", "| Spacing density (per point) | 0.0090 | 0.5655 |",
             "| SE by (32.6) (points) | 0.145 | 0.0116 |", "| Half the width ÷ 1.96 (points) | 0.151 | |"):
    has("E5 table", row_)
has("E5 large T", "For the 1% quantile the two SEs nearly agree, so at 5,849 days \"large $T$\" holds")
chk("E5 point", 100 * float(xs[58]), ".3f", "-3.567")
has("E5 ranks", f"$R_{{({K.jrank(U, T)})}}=-3.567\\%$, and its median, $R_{{({K.jrank(0.5, T)})}}=0.0879\\%$")
chk("E5 lower", 100 * float(xs[j1 - 1]), ".3f", "-4.016")
chk("E5 upper", 100 * float(xs[j2 - 1]), ".3f", "-3.425")
chk("E5 coverage", cov, ".4f", "0.9587")
fhat = (j2 - j1) / (T * 100 * (float(xs[j2 - 1]) - float(xs[j1 - 1])))
chk("E5 density", fhat, ".4f", "0.0090")
chk("E5 density from printed", 31 / (5849 * (4.016 - 3.425)), ".4f", "0.0090")
se_a = math.sqrt(U * (1 - U) / T) / fhat
chk("E5 SE", se_a, ".3f", "0.145")
chk("E5 SE from the printed density", math.sqrt(0.01 * 0.99 / 5849) / 0.0090, ".3f", "0.145")
half = 100 * (float(xs[j2 - 1]) - float(xs[j1 - 1])) / 2 / 1.96
chk("E5 half-width / 1.96", half, ".3f", "0.151")
chk("E5 half-width from printed", (4.016 - 3.425) / 2 / 1.96, ".3f", "0.151")
chk("E5 iid bootstrap", 100 * float(K.qi_a.std()), ".3f", "0.119")
chk("E5 iid batch SE", 100 * K.batch_se_sd(K.qi_a), ".4f", "0.0014")
chk("E5 block bootstrap", 100 * float(K.qb_a.std()), ".3f", "0.257")
chk("E5 block batch SE", 100 * K.batch_se_sd(K.qb_a), ".4f", "0.0019")
chk("E5 ratio", float(K.qb_a.std() / K.qi_a.std()), ".1f", "2.2", 2)
chk("E5 ratio from printed", 0.257 / 0.119, ".1f", "2.2", 2)
has("E5 block length", "(experiment 6, `default_rng([6, 20261011])`, $\\ell=145$ by [[LM22]]'s rule, in its draw order)")
has("E5 iid", "The iid bootstrap (experiment 5, `default_rng([5, 20261011])`, 10,000 resamples) gives the 1% quantile an "
    "SE of 0.119 points (batch SE 0.0014)")
m1, m2, mcov = K.binom_interval(T, 0.5)
assert (m1, m2) == (2850, 3000) and K.jrank(0.5, T) == 2925
chk("E5 median", 100 * float(xs[2924]), ".4f", "0.0879")
chk("E5 median lower", 100 * float(xs[m1 - 1]), ".3f", "0.069")
chk("E5 median upper", 100 * float(xs[m2 - 1]), ".3f", "0.114")
chk("E5 median coverage", mcov, ".4f", "0.9502")
fm = (m2 - m1) / (T * 100 * (float(xs[m2 - 1]) - float(xs[m1 - 1])))
chk("E5 median spacing density", fm, ".4f", "0.5655")
chk("E5 median SE", math.sqrt(0.25 / T) / fm, ".4f", "0.0116")
chk("E5 median SE from the printed density", math.sqrt(0.25 / 5849) / 0.5655, ".4f", "0.0116")
assert m2 - m1 == 150
has("E5 LM20 location SE", "[[LM20]]'s $t$ location had 0.0124")
assert "| 0.0997 (0.0124) |" in (ROOT / "src" / "lm20.md").read_text(encoding="utf-8")   # lm20.md:269
# 250 returns
b1, b2, bcov = K.binom_interval(250, U)
assert b1 == 0 and b2 == 7
chk("250: 0.99^250", 100 * 0.99**250, ".2f", "8.11", 2)
assert 0.99**250 > 0.025
chk("250 coverage", bcov, ".3f", "0.986")
has("250 upper rank", "Its upper end is $R_{(7)}$, coverage 0.986")
has("250 Pr(X=0)", f"With 250 iid returns, $\\Pr(X=0)={1 - U:.2f}^{{250}}$ exceeds {100 * U2:.1f}\\%, so no rank")
has("KC 4 (a)", f"The chance is ${1 - U:.2f}^{{250}}={100 * (1 - U) ** 250:.2f}\\%$, the first cell of Basel's Table 2 "
    f"(Section 7). It exceeds {100 * U2:.1f}%")
assert K.dates[-250] == "2025-09-25"
has("250 start", "TR23's last 250 returns, from 25 September 2025, give a VaR of 4.43%")
pct("250 VaR", -float(np.sort(K.last250)[2]), 2, "4.43")
pct("250 upper end", float(np.sort(K.last250)[6]), 2, "-3.61")
pct("250 worst", float(K.last250.min()), 2, "-6.46")
assert K.dates[T - 250 + int(np.argmin(K.last250))] == "2026-07-17"
has("250 worst date", "The worst was −6.46%, on 17 July 2026")
# KC 4 (b): (32.6) at 250 iid returns with E5's density
chk("KC 4 (b) sqrt(5849/250)", math.sqrt(5849 / 250), ".1f", "4.8")
chk("KC 4 (b) SE", math.sqrt(U * (1 - U) / 250) / fhat, ".2f", "0.70", 2)
chk("KC 4 (b) SE from the printed density", math.sqrt(0.01 * 0.99 / 250) / 0.0090, ".2f", "0.70", 2)
chk("KC 4 (b) SE from the printed 0.145 and 4.8", 0.145 * 4.8, ".2f", "0.70", 2)
chk("KC 4 (b) uT", 0.01 * 250, ".1f", "2.5", in_md=False)       # "2.5" recurs as u: the sentence is the text check
has("KC 4 (b) uT", f"With $uT={0.01 * 250:.1f}$, \"large $T$\" fails, so {math.sqrt(U * (1 - U) / 250) / fhat:.2f} is a "
    "rough guide")
has("KC 4 (b)", "About 0.70 points: (32.6) scales with $1/\\sqrt T$, and $\\sqrt{5849/250}=4.8$")
has("250 Basel", "(BCBS 1996b, B.4(d)), about 250 returns")

# ---------------------------------------------------------------- Section 5
assert float(K.var1) == -0.02 and float(K.es1) == 0.476
has("E6 inputs", "Two independent bonds each lose 60% with probability 0.8% and gain 2% otherwise (*constructed*)")
chk("E6 one bond VaR", float(100 * K.var1), ".2f", "-2.00", 5)   # also Problem 7's option A (one bond at 5%)
has("E6 ES display", "$-\\big[0.008\\times(-60\\%)+0.002\\times2\\%\\big]/0.01=47.60\\%$")
chk("E6 one bond ES", float(100 * K.es1), ".2f", "47.60", 5)
chk("E6 ES from the printed formula", -(0.008 * -60 + 0.002 * 2) / 0.01, ".2f", "47.60", 5)
chk("E6 some default", float(100 * K.p_any), ".2f", "1.59")
chk("E6 some default from printed", 100 * (1 - 0.992**2), ".2f", "1.59")
has("E6 some default display", "$1-0.992^2=1.59\\%$")
chk("E6 half VaR", float(-100 * K.half_one), ".2f", "29.00", 4)
chk("E6 half VaR from printed", -(-60 + 2) / 2, ".2f", "29.00", 4)
chk("E6 half ES", float(100 * K.es_half), ".2f", "29.20", 3)
assert float(2 * K.var1 / 2) == -0.02
has("E6 conclusion", "Diversifying raised VaR and lowered ES")
chk("Deep Dive 5 minimum", float(K.Fru[K.kmin]), ".3f", "4.689", 3)
chk("Deep Dive 5 theta", float(K.Ls[K.kmin]), ".3f", "3.567", 4)
assert K.kmin + 1 == 59 and abs(float(K.Fru[K.kmin]) - 100 * es_h(R, U)) < 1e-9
has("Basel 2019", "Basel's 2019 market-risk standard uses ES at 97.5% (BCBS 2019, MAR33.3), where the 1996 rules used a "
    "99% VaR (BCBS 1996b, B.4(b))")
assert K.C.LAM == 0.94
has("EWMA decay", "EWMA (26.2), with RiskMetrics' $\\lambda=0.94$")
chk("Basel normal ES 2.5%", K.k_n, ".3f", "2.338", 2)
chk("Basel normal VaR 1%", -K.z01, ".3f", "2.326", 2)
has("Basel normal display", f"$\\operatorname{{ES}}_{{{U2}}}={K.k_n:.3f}\\sigma$ and "
    f"$\\operatorname{{VaR}}_{{{U}}}={-K.z01:.3f}\\sigma$")
chk("KC 5 ratio", K.k_n / -K.z01, ".3f", "1.005")
chk("KC 5 ratio from printed", 2.338 / 2.326, ".3f", "1.005")
chk("TR23 ES2.5/VaR1 historical", es_h(R, U2) / var_h(R, U), ".2f", "1.05")
chk("TR23 ES2.5/VaR1 t", es_t(K.nu0, K.loc0, K.sc0, U2) / var_t(K.nu0, K.loc0, K.sc0, U), ".2f", "1.11")
chk("historical ratio from X3's printed cells", 3.74 / 3.57, ".2f", "1.05")
chk("t ratio from X3's printed cells", 3.73 / 3.37, ".2f", "1.11")
has("KC 5 ratios", "TR23's heavier tail makes ES at 2.5% over VaR at 1% 1.05 in the data and 1.11 under the $t$ "
    "([[ex:models]])")

# ---------------------------------------------------------------- Section 6
sg = K.sg
chk("E7 EWMA sigma", sg["EWMA"], ".4f", "1.5605")
chk("E7 GARCH-n sigma", sg["GARCH-n"], ".4f", "1.7222", 2)
chk("E7 GARCH-t sigma", sg["GARCH-t"], ".4f", "1.7040", 2)
chk("E7 normal mean", float(K.pn[0]), ".4f", "0.1020")
chk("E7 t mean", float(K.pt[0]), ".4f", "0.1190")
chk("E7 t nu", float(K.pt[4]), ".2f", "6.39")
# the VaRs from the printed inputs (32.8)
z = float(stats.norm.ppf(U))
chk("E7 EWMA VaR from printed", 100 * (1 - math.exp(1.5605 * z / 100)), ".2f", "3.57", 5)
chk("E7 GARCH-n VaR from printed", 100 * (1 - math.exp((0.1020 + 1.7222 * z) / 100)), ".2f", "3.83")
zt_p = float(stats.t.ppf(U, 6.39)) * math.sqrt(4.39 / 6.39)
chk("E7 GARCH-t VaR from printed", 100 * (1 - math.exp((0.1190 + 1.7040 * zt_p) / 100)), ".2f", "4.14", 2)


def es_lognormal(g0: float, s0: float, u: float) -> float:
    return 1 - math.exp(g0 + s0 * s0 / 2) * float(stats.norm.cdf(stats.norm.ppf(u) - s0)) / u


chk("E7 EWMA ES from printed", 100 * es_lognormal(0.0, 0.015605, U), ".2f", "4.07")
chk("E7 GARCH-n ES from printed", 100 * es_lognormal(0.001020, 0.017222, U), ".2f", "4.39")
qy = float(stats.t.ppf(U, 6.39))
es_tp = 1 - integrate.quad(lambda v: math.exp(0.001190 + 0.017040 * math.sqrt(4.39 / 6.39) * v)
                           * float(stats.t.pdf(v, 6.39)), -np.inf, qy)[0] / U
chk("E7 GARCH-t ES from printed", 100 * es_tp, ".2f", "5.26")
chk("E7 z GARCH-n", K.zn, ".2f", "-5.98")
chk("E7 z GARCH-n from printed", (-10.20 - 0.1020) / 1.7222, ".2f", "-5.98")
has("E7 LM26's 5.9", "([[LM26]]'s 5.9 divides the return itself by 1.7222)")
assert f"{-loss7 / 1.7222 * (-1):.1f}" != "" and f"{100 * float(np.log1p(R[i7])) / sg['GARCH-n']:.1f}" == "-5.9"
sci("E7 GARCH-n probability", K.p_n, "1.1\\times10^{-9}")
chk("E7 GARCH-n years (millions)", 1 / (K.p_n * K.A) / 1e6, ".1f", "3.7", 2)
chk("E7 z GARCH-t", K.zt_, ".2f", "-6.06")
chk("E7 z GARCH-t from printed", (-10.20 - 0.1190) / 1.7040, ".2f", "-6.06")
sci("E7 GARCH-t probability", K.p_t, "1.2\\times10^{-4}")
cnt("E7 sessions", round(1 / K.p_t), "8,014")
chk("E7 years", 1 / (K.p_t * K.A), ".1f", "32.6", in_md=False)     # "32.6" is also the tag (32.6): the sentence
has("E7 once in", f"once in {round(1 / K.p_t):,} sessions, {1 / (K.p_t * K.A):.1f} years")
has("E7 unrounded", "Both come from the unrounded fits and probabilities.")
has("E7 points to X1", "By (32.8) the VaRs and ESs are [[ex:case]]'s EWMA and GARCH rows")
# from the printed inputs and the printed probability the count of sessions differs; the text says it uses neither
p_t_pr = float(stats.t.cdf((-10.20 - 0.1190) / 1.7040 / math.sqrt(4.39 / 6.39), 6.39))
assert round(1 / p_t_pr) != 8014 and round(1 / 1.2e-4) != 8014
# E8
v1t = float(VAR["GARCH-t"][k7])
chk("E8 one-day GARCH-t VaR", 100 * v1t, ".3f", "4.142")
pct("E8 MC VaR", K.v_full, 1, "10.5")
chk("E8 MC batch SE", 100 * K.batch_se_q(K.R10mc, U), ".2f", "0.07")
pct("E8 sqrt(10) rule", math.sqrt(10) * v1t, 2, "13.10", 2)
chk("E8 sqrt(10) from printed", math.sqrt(10) * 4.142, ".2f", "13.10", 2)
has("E8 design", "(experiment 1, `default_rng([1, 20261011])`, 100,000 paths; each step draws all paths' $t$ innovations "
    "at once")
has("E8 batches", "Batch SEs use 20 batches of 5,000 paths.")
has("E8 realized", "| Realized loss over the ten sessions | 8.92 | |")
has("E8 rows", "| GARCH-t, simulated | 10.5 | 0.07 |")
has("E8 rows", "| Constant $\\sigma_{t+1\\mid t}=1.7040\\%$ | 10.9 | 0.05 |")
has("E8 rows", "| (26.4)'s path toward the fit's unconditional 1.116% a day | 9.9 | 0.06 |")
has("E8 rows", "| The $\\sqrt{10}$ rule, $\\sqrt{10}\\times4.142\\%$ | 13.10 | |")
assert K.v_d < K.v_c and K.v_full > K.v_d      # KC 3 (a): mean reversion lowers, the random feedback raises
pct("E8 constant sigma", K.v_c, 1, "10.9")
chk("E8 constant batch SE", 100 * K.batch_se_q(K.R10c, U), ".2f", "0.05", 5)
chk("E8 gap 13.10 - 10.9", 13.10 - 10.9, ".1f", "2.2", 2)
chk("E8 gap unrounded", 100 * (math.sqrt(10) * v1t - K.v_c), ".1f", "2.2", 2)
chk("E8 unconditional sd", math.sqrt(K.s2_bar), ".3f", "1.116")
chk("E8 persistence", K.al + K.be, ".3f", "0.922")
pct("E8 deterministic path", K.v_d, 1, "9.9")
chk("E8 deterministic batch SE", 100 * K.batch_se_q(K.R10d, U), ".2f", "0.06")
chk("E8 one point (unrounded)", 100 * (K.v_c - K.v_d), ".0f", "1", in_md=False)
chk("E8 one point from printed", 10.9 - 9.9, ".1f", "1.0", in_md=False)
has("E8 one point", "Mean reversion (persistence 0.922) takes one point more")
has("E8 gap", "gives 2.2 points less than 13.10%")
chk("E8 feedback", 100 * (K.v_full - K.v_d), ".1f", "0.6", 2)
chk("E8 feedback from printed", 10.5 - 9.9, ".1f", "0.6", 2)
chk("E8 feedback SE", 100 * float(np.std(K.bq_full - K.bq_d)) / math.sqrt(20), ".2f", "0.04", 3)
# KC 6
chk("KC 6", 100 * (math.exp(-0.04) - 1), ".2f", "-3.92")
has("KC 6 display", "$e^{-0.04}-1=-3.92\\%$")

# ---------------------------------------------------------------- Section 7
BT = K.BT
chk("HS smallest margin", 100 * float(np.min(np.abs(K.Ro + VAR["HS"]))), ".3f", "0.011")
chk("smallest margin over six models", min(100 * float(np.min(np.abs(K.Ro + VAR[m]))) for m in MODELS), ".4f", "0.0012")
has("margins", "is 0.011 points for HS and 0.0012 over all six models, so no return ties with its forecast")
has("t refits", "the $t$ refits at each month's first session on the 1,231 returns before it")
cnt("window", K.W_, "1,231", 4)                 # the case, X1's note and the backtest's two
assert K.dates[K.s7 - K.W_] == "2020-03-10" and K.dates[K.s7 - 1] == "2025-03-31"   # the t's fit of 1 April
cnt("n", K.n_bt, "4,609", 6)
assert K.dates[K.first] == "2008-01-02"
has("backtest start", "on $n=4{,}609$ days from 2 January 2008")
chk("expected", K.n_bt * U, ".2f", "46.09", 4)
x = {m: int(BT[m]["x"]) for m in MODELS}
assert [x[m] for m in MODELS] == [56, 110, 69, 103, 102, 77]
has("X4 note counts", "the returns of HS's 56 and GARCH-t's 77 exceedance days. N had 110")
# E9
cum = K.cum250
chks("E9 cumulative", cum[:5], ".2f", ["8.11", "28.58", "54.32", "75.81", "89.22"], [2, None, None, None, None])
chk("E9 at 5", cum[5], ".2f", "95.88")
assert (K.yb, K.rb, K.y5, K.r5, K.yN, K.rN) == (5, 10, 9, 15, 57, 73)
has("E9 table", "| $\\Pr(X\\le x)$ (%) | " + " | ".join(f"{c_:.2f}" for c_ in cum[:6]) + " |")
has("E9 zones", "Yellow starts where $\\Pr(X\\le x)$ reaches 95%, at 5, and red where it reaches 99.99%, at 10")
has("E9 other lengths", "The rule gives 9 and 15 for 500 days, and 57 and 73 for 4,609")
has("X5 note thresholds", "Dashed lines: the 46.09 expected, yellow from 57 and red from 73")
chk("E9 HS Pr(X>=56)", BT["HS"]["p_cov"], ".3f", "0.085", 2)
has("E9 zones of the models", "HS's 56 are green, $\\Pr(X\\ge56)=0.085$, the $t$'s 69 yellow and the other four red")
# X6a
zone = {m: ("green" if x[m] < K.yN else ("yellow" if x[m] < K.rN else "red")) for m in MODELS}
pc_txt = {"HS": "0.085", "N": "$6.5\\times10^{-16}$", "t": "$9.1\\times10^{-4}$", "EWMA": "$2.7\\times10^{-13}$",
          "GARCH-n": "$6.2\\times10^{-13}$", "GARCH-t": "$1.8\\times10^{-5}$"}
for m in MODELS:
    rate = 100 * x[m] / K.n_bt
    mv = 100 * BT[m]["mean"]
    chk(f"X6a rate {m}", rate, ".2f", f"{rate:.2f}", in_md=False)
    chk(f"X6a mean VaR {m}", mv, ".2f", f"{mv:.2f}", in_md=False)
    if m == "HS":
        chk("X6a p HS", BT[m]["p_cov"], ".3f", "0.085", 2)
    else:
        sci(f"X6a p {m}", BT[m]["p_cov"], pc_txt[m].strip("$"))
    has(f"X6a row {m}", f"| {m} | {x[m]} | {rate:.2f} | {pc_txt[m]} | {zone[m]} | {mv:.2f} |")
# X6b and the independence counts
p_ind_txt = {"HS": "$2.6\\times10^{-8}$", "N": "$6.4\\times10^{-8}$", "t": "$5.1\\times10^{-10}$", "EWMA": "0.028",
             "GARCH-n": "0.026", "GARCH-t": "0.0095"}
mx = {"HS": 12, "N": 27, "t": 16, "EWMA": 10, "GARCH-n": 11, "GARCH-t": 10}
first_end = {"HS": "2009-01-08", "N": "2009-01-08", "t": "2009-01-08", "EWMA": "2010-10-18", "GARCH-n": "2022-04-25",
             "GARCH-t": "2025-04-07"}
n_tie: dict[str, int] = {}
tie_months: dict[str, set[str]] = {}
for m in MODELS:
    hit = K.HIT[m]
    n11, tr = int(BT[m]["n11"]), int(BT[m]["trials"])
    exp_ = tr * x[m] / K.n_bt
    csum = np.concatenate([[0], np.cumsum(hit)])
    r250 = csum[250:] - csum[:-250]
    yel = 100 * float(np.mean((r250 >= 5) & (r250 <= 9)))
    red = 100 * float(np.mean(r250 >= 10))
    assert int(r250.max()) == mx[m] and len(r250) == 4360
    at_max = np.flatnonzero(r250 == r250.max())
    ends = [K.dates[int(K.oos[k_ + 249])] for k_ in at_max]          # each tied window's last day
    assert ends[0] == first_end[m], (m, ends[0])
    n_tie[m] = len(ends)
    # runs of consecutive windows; a run that starts more than 31 days after the first window recurs "months later"
    starts_ = [ends[i_] for i_ in range(len(at_max)) if i_ == 0 or at_max[i_] != at_max[i_ - 1] + 1]
    d0 = date.fromisoformat(ends[0])
    tie_months[m] = {s_[:7] for s_ in starts_ if (date.fromisoformat(s_) - d0).days > 31}
    ptxt = p_ind_txt[m]
    if ptxt.startswith("$"):
        sci(f"X6b p {m}", BT[m]["p_ind"], ptxt.strip("$"), 2 if m == "HS" else None)   # HS: also in the prose
    else:
        d = len(ptxt.split(".")[1])
        chk(f"X6b p {m}", BT[m]["p_ind"], f".{d}f", ptxt)
    has(f"X6b row {m}", f"| {m} | {n11} of {tr} | {exp_:.2f} | {ptxt} | {yel:.1f}, {red:.1f} | {mx[m]} | "
        f"{short_date(first_end[m])} |")
    for v_, f_ in ((exp_, ".2f"), (yel, ".1f"), (red, ".1f")):
        chk(f"X6b {m}", v_, f_, format(v_, f_), in_md=False)
chk("X6b HS expected", int(BT["HS"]["trials"]) * x["HS"] / K.n_bt, ".2f", "0.68", 3)   # X6b, the prose, KC 7
cnt("X6b windows", 4360, "4,360")
assert (min(n_tie.values()), max(n_tie.values())) == (7, 19), n_tie       # "From 7 to 19 windows tie at each maximum"
assert {m for m in MODELS if tie_months[m]} == {"N", "EWMA"}
assert tie_months["N"] == {"2009-06"} and tie_months["EWMA"] == {"2020-03", "2022-03"}, tie_months
has("X6b recurrences", "The most recurs months later only for N, in June 2009, and for EWMA, in March 2020 and March "
    "2022. From 7 to 19 windows tie at each maximum")
has("independence HS", "HS's 9 of 56, against 0.68 expected, give $2.6\\times10^{-8}$")
has("independence p-value", "and its upper tail gives the p-value")
has("not in the book: ES backtests", "Backtests of ES and multivariate GARCH are not in this book.")
has("LM26 scored", "scored the variance forecasts behind EWMA and the two GARCH laws")
chk("Bonferroni", 0.05 / 12, ".4f", "0.0042", 3)
rej_cov = [m for m in MODELS if BT[m]["p_cov"] <= 0.05 / 12]
rej_ind = [m for m in MODELS if BT[m]["p_ind"] <= 0.05 / 12]
assert rej_cov == ["N", "t", "EWMA", "GARCH-n", "GARCH-t"] and rej_ind == ["HS", "N", "t"]
has("Bonferroni verdicts", "It rejects coverage ([[ex:coverage]]) for N, t, EWMA, GARCH-n and GARCH-t, and independence "
    "for HS, N and t")
assert all(bool(K.Ro[k7] < -VAR[m][k7] - K.EPS) for m in MODELS)
ten = {m: int((K.Ro[k7:k7 + 10] < -VAR[m][k7:k7 + 10] - K.EPS).sum()) for m in MODELS}
assert ten == {"HS": 3, "N": 3, "t": 3, "EWMA": 1, "GARCH-n": 1, "GARCH-t": 1}
has("7 April exceedances", "In the ten sessions from 7 April HS, N and t had three each, and EWMA and the two GARCH models one each")
has("Kupiec", "Kupiec (1995; §IV of its Federal Reserve working paper) tests the same count")
has("Christoffersen", "Christoffersen (1998; §3 of the author's manuscript) adds a ratio for independence")
sd_c = math.sqrt(K.n_bt * U * (1 - U))
chk("KC 7 SD", sd_c, ".2f", "6.75", 2)
chk("KC 7 z", (56 - K.n_bt * U) / sd_c, ".2f", "1.47", 2)
chk("KC 7 z from printed", (56 - 46.09) / 6.75, ".2f", "1.47", 2)
has("KC 7 displays", "The SD is $\\sqrt{4609\\times0.01\\times0.99}=6.75$, so $z=(56-46.09)/6.75=1.47$")
has("KC 7 question", f"HS had {x['HS']} exceedances against {K.n_bt * U:.2f} expected")
has("KC 7 answer", f"{int(BT['HS']['n11'])} of HS's {x['HS']} exceedances were followed by another")
has("中文導讀 backtest", f"的次數 {x['HS']} 與模型應有的 {K.n_bt * U:.2f} 次")

# ---------------------------------------------------------------- Section 8
rt_rows = []
for k in K.RULES:
    vals = [100 * var_h(ret[k], U), 100 * es_h(ret[k], U), 100 * es_h(ret[k], U2),
            100 * var_n(float(ret[k].mean()), float(ret[k].std(ddof=0)), U)]
    for v_ in vals:
        chk(f"X8a {k}", v_, ".2f", f"{v_:.2f}", in_md=False)
    has(f"X8a row {k}", f"| {k} | " + " | ".join(f"{v_:.2f}" for v_ in vals) + " |")
assert K.jrank(U, nR) == 19
has("X8a note 19 days", "The 1% figures rest on 19 days, and no standard error is printed")
has("widget labels", "by the three methods (the normal and $t$ fits in-sample)")
assert "(divisor 1,851; in-sample)" in (ROOT / "src" / "lm32.js").read_text(encoding="utf-8")
has("worst days", "Each rule's worst day was 7 April 2025, except R7's, 19 March 2020")
for k in K.RULES:
    sp = SP[k]
    row = (f"| {k} | {100 * sp.mdd:.2f} | {short_date(sp.peak)} | {short_date(sp.trough)} | "
           f"{short_date(sp.rec or '')} | {sp.long} | {100 * sp.dd0:.2f} | {short_date(sp.dd0_date)} | "
           f"{100 * sp.end_dd:.2f} |")
    has(f"X8b row {k}", row)
    for v_ in (100 * sp.mdd, 100 * sp.dd0, 100 * sp.end_dd):
        chk(f"X8b {k}", v_, ".2f", f"{v_:.2f}", in_md=False)
    if k != "R1":
        assert (sp.long_peak, sp.long_end) == (sp.peak, sp.rec), k
assert {k for k in K.RULES if SP[k].dd0_date == "2019-03-05"} == {"R3", "R5", "R7", "R8"}
for k in ("R3", "R5", "R7", "R8"):          # chiefly the purchase cost
    assert (1 - float(K.paths[k].wealth[0])) / SP[k].dd0 > 0.5, k
has("X8b note", "A max $\\mathrm{DD}^0$ on 5 March 2019 is chiefly the purchase cost")
assert K.paths["R1"].dates[-1] == "2026-10-08"
has("X8b end", "the end is 8 October 2026")
# E10
s1 = SP["R1"]
assert (s1.peak, s1.trough, s1.rec, s1.n_pt, s1.n_tr) == ("2020-01-06", "2020-03-19", "2021-01-13", 45, 205)
has("E10 episode", "R1's MDD of 23.19% took 45 sessions from peak to trough and 205 more to recover ([[ex:rulesdd]])")
assert (s1.long, s1.long_peak, s1.long_end) == (484, "2022-03-07", "2024-03-05")
has("E10 longest", "484 sessions below the peak of 7 March 2022, back on 5 March 2024")
assert s1.dd0_date == s1.trough == "2020-03-19"
pct("E10 DD0", s1.dd0, 2, "10.24", 2)
has("E10 DD0", "Its largest loss from the start, 10.24%, came at the same trough.")
has("E10 (31.7)", "R8 scales R6 by a volatility forecast, [[LM31]]'s (31.7).")
pct("E10 recovery", s1.mdd / (1 - s1.mdd), 2, "30.19")
chk("E10 recovery from printed", 100 * 0.2319 / 0.7681, ".2f", "30.19")
has("E10 recovery printed", "$0.2319/0.7681=30.19\\%$")
s2 = SP["R2"]
assert s2.dd0_date == "2019-03-08"
has("E10 R2", "R2's MDD is 22.97%, yet its loss from the start never exceeded 0.39%, on 8 March 2019")
# the MDDs and R2's largest loss from the start wherever they are printed (X8b, the prose, KC 8, the 中文導讀)
chk("R1 MDD", 100 * SP["R1"].mdd, ".2f", "23.19", 4)
chk("R2 MDD", 100 * SP["R2"].mdd, ".2f", "22.97", 6)
chk("R2 max DD0", 100 * SP["R2"].dd0, ".2f", "0.39", 5)
chk("R6 MDD", 100 * SP["R6"].mdd, ".2f", "18.90", 2)
pct("E10 purchase cost (LM27's A27-23)", 1 - float(K.paths["R2"].wealth[0]), 3, "0.142")
pct("E10 R8 ES", es_h(ret["R8"], U), 2, "3.16", 5)
pct("E10 R6 ES", es_h(ret["R6"], U), 2, "2.86", 2)
has("E10 R6 R8", "Its 1% ES is higher (3.16% against 2.86%), yet its MDD is lower (18.42% against 18.90%)")
breach = [k for k in K.RULES if SP[k].mdd > 0.20]
assert breach == ["R1", "R2", "R4"]
has("limit", "R1, R2 and R4 (23.19%, 22.97%, 33.56%) breach a hypothetical 20% limit on the MDD")
# resampled MDDs (X9)
q_ = K.batch_se_q


def qv(v: np.ndarray, u: float) -> float:
    return float(np.quantile(v, u, method="inverted_cdf"))


pm = [100 * qv(K.MP[k], 0.5) for k in K.RULES]
bm = [100 * qv(K.MB[k], 0.5) for k in K.RULES]
pge = [int(np.sum(K.MP[k] >= SP[k].mdd - K.EPS)) for k in K.RULES]
bge = [int(np.sum(K.MB[k] >= SP[k].mdd - K.EPS)) for k in K.RULES]
has("X9 permutation medians", "| Permutation median (%) | " + " | ".join(f"{v_:.1f}" for v_ in pm) + " |")
has("X9 permutation counts", "| Permutations at or above the MDD | " + " | ".join(f"{c:,}" for c in pge) + " |")
has("X9 bootstrap medians", "| Bootstrap median (%) | " + " | ".join(f"{v_:.1f}" for v_ in bm) + " |")
has("X9 bootstrap counts", "| Bootstrap at or above the MDD | " + " | ".join(f"{c:,}" for c in bge) + " |")
has("X9 block lengths", "| Block length (sessions) | " + " | ".join(str(K.ELL[k]) for k in K.RULES) + " |")
for v_ in pm + bm:
    chk("X9 median", v_, ".1f", f"{v_:.1f}", in_md=False)   # the rows
chk("R1 permutation median", pm[0], ".1f", "17.2", 2)
chk("R1 bootstrap median", bm[0], ".1f", "20.7", 2)
assert (pge[0], bge[0], pge[1]) == (1069, 3305, 557)
has("permutation paragraph", "For R1, 10,000 permutations give a median MDD of 17.2% and 1,069 reach the realized 23.19%. "
    "The bootstrap gives 20.7% and 3,305")
# X9's note: the medians' batch SEs (none on an atom) and the counts' SEs as shares of 10,000
bse_m = [100 * q_(K.MP[k], 0.5) for k in K.RULES] + [100 * q_(K.MB[k], 0.5) for k in K.RULES if k not in ("R5", "R6")]
chk("X9 median batch SE low", min(bse_m), ".2f", "0.03", 5)
chk("X9 median batch SE high", max(bse_m), ".2f", "0.13")
sh_se = [100 * math.sqrt(c / 1e4 * (1 - c / 1e4) / 1e4) for c in pge + bge]
chk("X9 share SE low", min(sh_se), ".1f", "0.2")
chk("X9 share SE high", max(sh_se), ".1f", "0.5", 2)
has("X9 SEs", "The medians' batch SEs are 0.03 to 0.13 points, and each count, as a share of 10,000, has an SE of 0.2 to "
    "0.5 points")
has("X9 seeds", "(experiment 3, `default_rng([3, 20261011])`)")
has("X9 seeds", "(experiment 4, `default_rng([4, 20261011])`, [[LM22]]'s draw order)")
atoms = {k: K.atom(k, K.MB[k]) for k in K.RULES}
na = [round(atoms[k][1] * 10_000) for k in K.RULES]
assert (min(na), max(na)) == (399, 1737)
starts = {atoms[k][2].split(" -> ")[0] for k in K.RULES}
assert starts == {"2020-02-21", "2020-02-24", "2020-03-09"}
assert all(atoms[k][2].endswith("2020-03-19") for k in K.RULES)
has("X9 atoms", "In 399 to 1,737 bootstrap resamples, by rule, the MDD equals a realized fall into 19 March 2020 (from "
    "21 February, 24 February or 9 March)")
on_atom = [k for k in K.RULES if float(np.mean(np.abs(K.MB[k] - qv(K.MB[k], 0.5)) < 1e-10)) > 0.01]
assert on_atom == ["R5", "R6"]
has("X9 atom medians", "R5's and R6's bootstrap medians lie on them and have no batch SE")
has("X9 atoms gloss", "so these values are atoms, values that many resamples take exactly")
assert int(np.sum(np.abs(K.MB["R1"] - SP["R1"].mdd) < 1e-10)) == 223
has("X9 223", "And 223 of R1's 3,305 equal its MDD exactly")
p_share = [c / 10_000 for c in pge]
assert min(p_share) == p_share[1] == 0.0557 and all(p > 0.05 for p in p_share)
has("eight tests", "One permutation test per rule makes eight tests, and none is significant at the 5% level: the smallest "
    "share at or above the realized MDD is R2's, 557 of 10,000")
chk("KC 8 share", 100 * pge[1] / 10_000, ".2f", "5.57")
chk("KC 8 share SE", 100 * math.sqrt(0.0557 * 0.9443 / 10_000), ".2f", "0.23")
has("KC 8 SE", "No: 5.57% (SE 0.23 points) is above 5%")
has("KC 8 question", f"(c) {pge[1]} of 10,000 permutations of R2's returns reach its MDD")
has("not in the book: conditional drawdown", "Conditional drawdown measures are not in this book.")
# (32.10)
chk("(32.10)", math.sqrt(math.pi / 2) * 0.20 * math.sqrt(10), ".3f", "0.793", 2)
chk("(32.10) four decimals, the exponent", -math.sqrt(math.pi / 2) * 0.20 * math.sqrt(10), ".4f", "-0.7927")
chk("(32.10) fall", 100 * (1 - math.exp(-0.7927)), ".1f", "54.7")
assert abs(2 * math.sqrt(math.pi / 8) - math.sqrt(math.pi / 2)) < 1e-15
has("(32.10) hypothetical", "A hypothetical $\\sigma=20\\%$ over ten years gives 0.793")

# ---------------------------------------------------------------- Section 9: run the module's code block
code = re.search(r"```python\n(.*?)```", RAW, flags=re.DOTALL)
assert code
ns: dict = {}
exec(compile(code.group(1), "lm32.md section 9", "exec"), ns)  # noqa: S102 - the module's own code block
v9, e9 = ns["var_es"](R, 0.01)
chk("code var_es VaR", 100 * v9, ".3f", "3.567", 4)
chk("code var_es ES", 100 * e9, ".3f", "4.689", 3)
chk("code es_t", ns["es_t"](R, 0.01), ".2f", "5.19", 3)
w_code, obj_code = ns["min_es"](100 * K.xw, 0.025)
assert float(np.max(np.abs(np.asarray(w_code) - K.w_c))) < 1e-9 and abs(float(obj_code) - float(K.lp.value)) < 1e-9
assert max(len(ln) for ln in code.group(1).splitlines()) <= 80
chk("KC 9 default", 100 * float(np.quantile(R, U)), ".4f", "-3.5668")
chk("KC 9 inverted_cdf", 100 * float(np.quantile(R, U, method="inverted_cdf")), ".4f", "-3.5671", 2)
chk("KC 9 position", (T - 1) * U, ".2f", "58.48")
j_ = K.jrank(U, T)
has("KC 9 rank", f"Which one is $R_{{({j_})}}$")
has("KC 9 ranks", f"returns $R_{{({j_})}}=-3.5671\\%$")
has("KC 9 neighbours", f"between $R_{{({j_})}}$ and $R_{{({j_ + 1})}}$, so it lies a little above")
has("section 9 LM26", "The lab refits the forecasts with [[LM26]]'s `arch` code.")

# ---------------------------------------------------------------- practice problems and solutions
assert K.jrank(U, 250) == 3 and math.floor(0.01 * 250) == 2
has("S1", "**C** is correct: $j=\\lceil2.5\\rceil=3$. A takes $\\lfloor uT\\rfloor=2$")
# B is the midpoint of R_(2) and R_(3), interpolation at rank uT = 2.5 (NumPy's interpolated_inverted_cdf);
# NumPy's default interpolates at position (T - 1)u = 2.49 from 0, between R_(3) and R_(4) (rank 3.49)
assert float(np.quantile(np.arange(1.0, 251.0), U, method="interpolated_inverted_cdf")) == 2.5
assert abs(float(np.quantile(np.arange(1.0, 251.0), U)) - 3.49) < 1e-12
chk("S1 position", 249 * U, ".2f", "2.49")
has("S1 NumPy", "B interpolates at rank $uT=2.5$. NumPy's default interpolates at position $(T-1)u=2.49$ from 0, "
    "between $R_{(3)}$ and $R_{(4)}$ (Section 9)")
xp2 = K.xp2
chk("P2 uT", 180 * U2, ".1f", "4.5")
chk("P2 four worst", 100 * float(xp2[:4].sum()), ".1f", "-18.8")
p2_ = [f"{100 * v_:.1f}" for v_ in xp2]
has("P2 inputs", "has the five worst " + ", ".join(p2_[:-1]) + f" and {p2_[-1]}%")
es2 = -100 * (float(xp2[:4].sum()) / 180 + float(xp2[4]) * (U2 - 4 / 180)) / U2
chk("P2 ES", es2, ".3f", "4.544", 2)
chk("P2 ES from printed", -(1 / 0.025) * (-18.8 / 180 + (0.025 - 4 / 180) * (-3.3)), ".3f", "4.544", 2)
has("S2 display", "$-\\frac1{0.025}\\big[\\frac{-18.8}{180}+\\big(0.025-\\frac4{180}\\big)(-3.3)\\big]=4.544\\%$")
chk("P2 B", -100 * float(xp2.mean()), ".3f", "4.420")
chk("P2 C", -100 * float(xp2[:4].mean()), ".3f", "4.700")
has("P2 options", "   - **A.** 4.544%\n   - **B.** 4.420%\n   - **C.** 4.700%")
assert K.jrank(U2, 180) == 5
chk("P3 ES", es_n(0.05, 1.2, U), ".3f", "3.148", 2)
chk("P3 VaR", var_n(0.05, 1.2, U), ".3f", "2.742", 2)
chk("P3 C", 0.05 + 1.2 * float(stats.norm.pdf(K.z01)) / U, ".3f", "3.248", 2)
chk("P3 ES from printed", -0.05 + 1.2 * 2.6652, ".3f", "3.148", 2)
chk("P3 VaR from printed", -0.05 + 1.2 * 2.3263, ".3f", "2.742", 2)
has("P3 inputs", "normal with $\\mu=0.05\\%$ and $\\sigma=1.2\\%$")
has("S3 ES display", "$-0.05+1.2\\times2.6652=3.148\\%$")
has("S3 VaR display", "$-0.05+1.2\\times2.3263=2.742\\%$")
ddp = K.ddp
has("S4 drawdowns", "the drawdowns are 0, 0, 5.56, 16.67, 12.04, 0, 5.45 and 0%")
chks("P4 DD", [100 * v_ for v_ in ddp if v_ > 0], ".2f", ["5.56", "16.67", "12.04", "5.45"], [None, 3, None, None])
chk("P4 MDD", 100 * float(ddp.max()), ".2f", "16.67", 3)
chk("P4 MDD from printed", 100 * (1 - 0.90 / 1.08), ".2f", "16.67", 3)
has("P4 path", "wealth path is " + ", ".join(f"{w_:.2f}" for w_ in K.wp[:-1]) + f" and {K.wp[-1]:.2f}, with $W_0=1$")
has("S4 MDD display", "$1-0.90/1.08=16.67\\%$")
chk("P4 B", 100 * (1 - float(K.wp.min())), ".2f", "10.00")
has("P4 options", "   - **A.** 16.67%\n   - **B.** 10.00%\n   - **C.** 20.00%")
chk("P4 C", 100 * float(ddp.max()) / (1 - float(ddp.max())), ".2f", "20.00")
assert (K.j1k, K.j2k) == (4, 18) and K.jrank(U, 1000) == 10
chk("P6 coverage", K.covk, ".4f", "0.9761")
has("P6 inputs", "For $T=1{,}000$ and $u=1\\%$")                   # binom_interval(1000, U) in lm32_common
has("S6", "the ranks are 4 and 18, around the point $R_{(10)}$, with coverage 0.9761")
chk("P7 some default", float(100 * K.pa7), ".2f", "7.84")
chk("P7 some default from printed", 100 * (1 - 0.96**2), ".2f", "7.84")
chk("P7 both", float(100 * K.pb7), ".2f", "0.16", 2)
chk("P7 VaR", float(-100 * K.half_one), ".2f", "29.00", 4)
chk("P7 one bond ES", float(100 * K.es7_1), ".2f", "47.60", 5)
chk("P7 one bond ES from printed", -(0.04 * -60 + 0.01 * 2) / 0.05, ".2f", "47.60", 5)
chk("P7 mixture ES", float(100 * K.es7_h), ".2f", "29.99")
chk("S7 quantile", float(100 * K.half_one), ".2f", "-29.00")
has("S7 some default display", "$1-0.96^2=7.84\\%$")
has("S7 ES display", "$-[0.04\\times(-60\\%)+0.01\\times2\\%]/0.05$")
assert K.pb7 < Fraction(5, 100) <= K.pb7 + K.pone7
chk("P8 Pr(X<=9)", float(stats.binom.cdf(9, 500, U)), ".4f", "0.9689")
chk("P8 Pr(X>=9)", float(stats.binom.sf(8, 500, U)), ".4f", "0.0671")
N8, X8 = 500, 9                                              # Problem 8's inputs, as the two checks above use them
assert float(stats.binom.sf(9, 500, U)) < 0.05 < float(stats.binom.sf(8, 500, U))   # a 5% test rejects from 10
has("S8 red", "here at 9 with 0.9689, and red at 15")
chk("P9 rate", 60 / 2000, ".2f", "0.03", 5)
chk("P9 expected", 59 * 60 / 2000, ".2f", "1.77")
chk("P9 p", float(stats.binom.sf(5, 59, 0.03)), ".4f", "0.0084")
assert float(stats.binom.sf(5, 59, 0.03)) < 0.05 and float(stats.binom.sf(5, 59, 0.03)) > 0.05 / 12
has("P9 inputs", "Over 2,000 hypothetical days a VaR has 60 exceedances. Of them, 59 have a next day, and 6 of those are "
    "followed by another")
has("S9 displays", "The rate is $60/2000=0.03$, so the expected count is $59\\times0.03=1.77$, and "
    "$\\Pr(\\operatorname{Bin}(59,0.03)\\ge6)=0.0084$")
chk("P10 a", K.kk, ".4f", "5.9836")
# the resamples and draws of 10,000: experiments 9, 10, 5, 6, 3, 4 and Problem 10's draws
assert {len(P9), len(B10), len(K.qi_a), len(K.qb_a), len(K.Z), *(len(v_) for v_ in K.MP.values()),
        *(len(v_) for v_ in K.MB.values())} == {10_000}
cnt("10,000", 10_000, "10,000", 9)
has("P10 estimate", "$(1.15\\pm0.03)\\times10^{-9}$")
chk("P10 estimate mantissa", K.p_is / 1e-9, ".2f", "1.15")
chk("P10 SE", K.se_is / 1e-9, ".2f", "0.03", 5)
sci("P10 exact", K.p_n, "1.091\\times10^{-9}")
chk("P10 plain expected", 10_000 * K.p_n, ".6f", "0.000011")
cnt("P10 shifted in the tail", int((K.Z <= 0).sum()), "4,927")
sci("P10 variance ratio", K.p_n * (1 - K.p_n) / K.var_one, "1.34\\times10^8")
chk("P11 alpha", K.ah, ".3f", "3.634", 2)
for u, (vq, eq) in ((0.001, ("6.69", "9.23")), (0.01, ("3.55", "4.90"))):
    chk(f"P11 VaR {u}", hill[u][0], ".2f", vq, N_HILL[vq])
    chk(f"P11 ES {u}", hill[u][1], ".2f", eq, N_HILL[eq])
for u, (vq, eq) in ((0.001, ("6.69", "9.23")), (0.01, ("3.55", "4.90"))):     # from the printed 3.634
    vv = 3 * (108 / (u * 5849)) ** (1 / 3.634)
    chk(f"P11 VaR {u} from printed", vv, ".2f", vq, N_HILL[vq])
    chk(f"P11 ES {u} from printed", vv * 3.634 / 2.634, ".2f", eq, N_HILL[eq])
has("S11 k", f"With $k={K.kh}$, $\\hat\\alpha={K.ah:.3f}$.")
has("S11 historical", f"against the historical {100 * var_h(R, U):.2f}%, {100 * es_h(R, U):.2f}%, "
    f"{100 * var_h(R, 0.001):.2f}% and {100 * es_h(R, 0.001):.2f}%")
assert K.WINDOW == 504 and K.fr.est_dates[K.rows0 - 504] == "2017-02-13" and K.fr.est_dates[K.rows0 - 1] == "2019-02-27"
has("P12 window", "the 504 joint dates from 13 February 2017 to 27 February 2019")
w_p = [f"{v_:.3f}" for v_ in K.w_es]
assert w_p == ["0.078", "0.203", "0.398", "0.290", "0.030"], w_p
assert list(K.fr.funds) == ["0050", "00646", "00679B", "00635U", "00642U"]
has("S12 weights", "The weights of 0050, 00646, 00679B, 00635U and 00642U are 0.078, 0.203, 0.398, 0.290 and 0.030 "
    "(rounded separately; 0.999 as printed)")
has("S12 ES", "The ES is 0.857%, and $\\theta^*=0.693\\%$ is the VaR at the solution")
has("P12 tags", "12. Minimum ES (*in-sample*; [[LM29]]'s (29.1) and (29.3)).")
assert f"{sum(float(p) for p in w_p):.3f}" == "0.999"
pct("S12 ES", K.es_lp, 3, "0.857")
chk("S12 theta", K.th_c, ".3f", "0.693")
pct("S12 VaR at the solution", var_h(K.xw @ K.w_es, U2), 3, "0.693")
pct("S12 R3", es_h(K.xw @ K.w3, U2), 3, "0.880")
pct("S12 R1", es_h(K.xw @ np.full(5, 0.2), U2), 3, "1.303")
assert K.kkt < 1e-12 and max(K.gaps) < 1e-12 and K.width < 1e-7
has("S12 checks", "HiGHS agrees to $10^{-12}$, and the KKT residuals are below $10^{-12}$")
has("S12 uniqueness", "Within $10^{-9}$ of the minimum no weight moves by more than $10^{-7}$")

# ---------------------------------------------------------------- the integers of the text: dates, ranks, counts, inputs
# the dates of the case: 7 April (the day), 2 April (the forecasts), 1 April (the t's refit), with and without the year
# (counts over the whole file: the overview and the references' "7 April 2025" included)
d7_, dfc_, dfit_, dr_ = (long_date(d_) for d_ in (K.dates[i7], K.dates[i7 - 1], K.dates[K.s7], K.rdates[0]))
has("date, the day", d7_, 8)
has("date, the day, day and month", d7_.rsplit(" ", 1)[0], 17)
has("date, the forecasts", dfc_, 1)
has("date, the forecasts, day and month", dfc_.rsplit(" ", 1)[0], 7)
has("date, the t's refit, day and month", dfit_.rsplit(" ", 1)[0], 2)
has("date, the rules' first return", dr_, 3)
has("month, the rules' start (and R2's max DD0 of 8 March 2019)", dr_.split(" ", 1)[1], 6)
# ranks and counts computed by the script
has("E1 VaR rank", f"$\\operatorname{{VaR}}=-R_{{({K.jrank(0.3, 5)})}}=0.80\\%$")
has("KC 2 question", "A sample has 50 daily returns")
j_kc2 = K.jrank(0.01, 50)
has("KC 2 answer", f"the VaR is $-R_{{({j_kc2})}}$, and (32.2) gives $-\\frac1{{0.01}}(0.01)R_{{({j_kc2})}}$")
has("E4 R1 horizon", "R1 over 20 sessions: 8.66% against $\\sqrt{20}\\times2.102\\%=9.40\\%$")   # K.R20: 20 sessions
assert "too heavy from −5%" in lm15                          # lm15.md:461
has("E3 LM15 quote", '"too heavy from −5%" ([[LM15]])')
has("KC 3 (b) days", f"Its shortage of days from −{100 * 0.03:.0f}% to −{100 * 0.05:.0f}% and its surplus beyond")
has("E6 half display", f"$({100 * float(K.lgd):.0f}\\%+{100 * float(K.gain):.0f}\\%)/2$")
has("X6a note binomial", f"$X\\sim\\operatorname{{Bin}}({K.n_bt},{U})$")
has("E9 x row", "| $x$ | " + " | ".join(str(i_) for i_ in range(6)) + " |")      # cum[:6] above
n_tests = 2 * len(MODELS)                                     # coverage and independence for six models
assert n_tests == 12
has("Bonferroni display", f"$0.05/{n_tests}=0.0042$", 2)       # Section 7 and Solution 9
has("中文導讀 tests", f"做了 {n_tests} 個檢定")
has("widget range", f"at any $u$ up to {100 * float(K.ugrid[-1]):.0f}%")
has("KC 8 (b)", "(b) (32.10) gives 0.793 for $\\sigma=20\\%$ over ten years")      # (32.10)'s check above: 0.20
g_ = f"$10^{{{round(math.log10(K.EPS))}}}$"                   # the guard K.EPS
has("backtest guard", f"with a guard of {g_}")
has("P11 inputs", f"losses of {100 * K.x0:.0f}% or more (guard {g_})")
j_a, j_c = math.floor(U * 250), K.jrank(U, 250)
has("P1 options", f"   - **A.** $R_{{({j_a})}}$\n   - **B.** the midpoint of $R_{{({j_a})}}$ and $R_{{({j_c})}}$\n"
    f"   - **C.** $R_{{({j_c})}}$")
has("S2 rank", f"$uT={180 * U2:.1f}$ and $j={K.jrank(U2, 180)}$")
has("S2 options", f"B is the mean of the $\\lceil uT\\rceil={K.jrank(U2, 180)}$ worst, C of the "
    f"$\\lfloor uT\\rfloor={math.floor(180 * U2)}$ worst")
has("S6 binomial", f"$X\\sim\\operatorname{{Bin}}(1000,{U})$ the ranks are {K.j1k} and {K.j2k}")
has("P7 inputs", f"lose {-100 * float(K.lgd):.0f}% with probability {100 * float(K.pd7):.0f}% and gain "
    f"{100 * float(K.gain):.0f}%")
has("P8 inputs", f"applied to {N8} hypothetical days of 99% VaR forecasts with {X8} exceedances")
has("S8 A", f"A reads $\\Pr(X\\ge{X8})=0.0671$ as a pass")
has("P10 seed", f"`np.random.default_rng([2, {K.SEED}])` and 10,000 `standard_normal` draws")

# ---------------------------------------------------------------- the overview's and summary's restatements
# the overview (front matter): each bullet whole, from the computed values; its numbers are outside the body's counts
ov = [(f"On 7 April 2025 the TAIEX total-return index fell {loss7:.2f}%: {lo:.1f} to {hi:.1f} times the one-day 99% "
       f"value at risk that six models had forecast on 2 April."),
      (f"Historical VaR is minus an order statistic, and historical ES, (32.2), is the tail mean of the empirical "
       f"distribution. On TR23's {T:,} returns they are {100 * var_h(R, U):.2f}% and {100 * es_h(R, U):.2f}%, against a "
       f"normal model's {100 * var_n(K.mu, K.s, U):.2f}% and {100 * es_n(K.mu, K.s, U):.2f}%."),
      (f"From {T:,} iid days the 1% quantile has a standard error of {se_a:.3f} points. A block bootstrap, which keeps "
       f"the order of days, gives {100 * float(K.qb_a.std()):.3f}. From 250 iid returns no order statistic is a 95% "
       f"lower bound."),
      (f"Two independent bonds held half and half raise VaR from {float(100 * K.var1):.2f}% to "
       f"{float(-100 * K.half_one):.2f}%, while ES falls from {float(100 * K.es1):.2f}% to {float(100 * K.es_half):.2f}%: "
       f"ES is coherent, and it is the minimum of a convex function, (32.7)."),
      (f"Under GARCH with normal innovations 7 April was a once-in-{1 / (K.p_n * K.A) / 1e6:.1f}-million-years day. With "
       f"Student-t innovations it was once in {1 / (K.p_t * K.A):.1f} years. The law's tail decides."),
      (f"Over {K.n_bt:,} days historical simulation had {int(BT['HS']['x'])} exceedances against {K.n_bt * U:.2f} "
       f"expected, but they clustered. The filtered models clustered far less and exceeded too often."),
      (f"The eight rules' maximum drawdowns run from {100 * min(SP[k].mdd for k in K.RULES):.2f}% to "
       f"{100 * max(SP[k].mdd for k in K.RULES):.2f}%, and three of them breach a hypothetical 20% limit. Permuting the "
       f"returns finds no rule's order of days unusual at the 5% level.")]
assert len(re.findall(r"^  - ", TEXT[OV0:FM_END], flags=re.MULTILINE)) == len(ov)
for k_, b_ in enumerate(ov):
    has(f"overview {k_ + 1}", f'  - "{b_}"')
has("summary sqrt rule", "On TR23 it overstates against ten iid days and under GARCH-t.")
assert math.sqrt(10) * var_h(R, U) > -float(np.quantile(K.R10iid, U, method="inverted_cdf")) and \
    math.sqrt(10) * float(VAR["GARCH-t"][k7]) > K.v_full
has("summary interval", "needs iid returns but no model for $F_R$. From 250 returns a 99% VaR has no distribution-free 95% "
    "lower bound")
chk("overview MDD low", 100 * min(SP[k].mdd for k in K.RULES), ".2f", "18.42", 3)
chk("overview MDD high", 100 * max(SP[k].mdd for k in K.RULES), ".2f", "33.56", 3)
has("summary MDD", "The rules' MDDs run from 18.42% to 33.56%")

# ====================================================================== charts and the widget block
tail_spec = json.loads((CHARTS / "lm32-tail.json").read_text(encoding="utf-8"))
assert sum(tail_spec["series"][0]["y"]) == 293
uw = json.loads((CHARTS / "lm32-underwater.json").read_text(encoding="utf-8"))
assert [s_["name"] for s_ in uw["series"]] == ["R1", "R3", "R6", "R8"]
for s_ in uw["series"]:
    assert abs(min(s_["y"]) + SP[s_["name"]].mdd) < 1e-6, s_["name"]           # every trough is plotted
zs = json.loads((CHARTS / "lm32-zones.json").read_text(encoding="utf-8"))
assert zs["series"][0]["values"] == [x[m] for m in MODELS]
vl = json.loads((CHARTS / "lm32-varlevel.json").read_text(encoding="utf-8"))
w = vl["widget"]
assert w["T"] == nR and all(len(w["worst"][k]) == 186 for k in K.RULES)
init = [v_ * 100 for v_ in vl["series"][0]["values"] + vl["series"][1]["values"]]
assert [f"{v_:.2f}" for v_ in init] == ["2.10", "1.80", "2.05", "3.38", "2.08", "3.07"]
for name in re.findall(r'data-chart="(lm32-[\w-]+)"', RAW):
    assert (CHARTS / f"{name}.json").exists(), name
print("charts: every plotted trough, count and the widget's first draw agree with the computations")

# ====================================================================== structure: labels, tags and citations
ex_labels = re.findall(r"\[!exhibit\][^\n]*\{#([\w-]+)\}", RAW)
eg_labels = re.findall(r"\[!example\][^\n]*\{#([\w-]+)\}", RAW)
assert len(ex_labels) == 11 and len(eg_labels) == 10, (ex_labels, eg_labels)
assert len(set(ex_labels) | set(eg_labels)) == 21, "a label is used twice"
for lab in ex_labels:
    assert f"[[ex:{lab}]]" in RAW, f"exhibit {lab} is never cited"
for kind, lab in re.findall(r"\[\[(ex|eg):([\w-]+)\]\]", RAW):
    assert lab in (ex_labels if kind == "ex" else eg_labels), (kind, lab)
tags = re.findall(r"\\tag\{(32\.\d+)\}", RAW)
assert tags == [f"32.{k}" for k in range(1, 11)], tags
assert len(re.findall(r"^> \[!kc\]", RAW, flags=re.MULTILINE)) == 8
links = set(re.findall(r"\[\[LM(\d+)", RAW))
fm = RAW.split("\n---\n", 1)[0]
m_pre, m_leads = re.search(r"prereq: \[([^\]]*)\]", fm), re.search(r"leads: \[([^\]]*)\]", fm)
assert m_pre and m_leads
prereq = set(m_pre.group(1).replace(" ", "").split(","))
leads = set(m_leads.group(1).replace(" ", "").split(","))
assert links <= prereq | leads, links - prereq - leads
assert prereq - links <= {"16"}, prereq - links      # LM16 is cited by its tags (16.4) and (16.7)
for t_ in ("(16.4)", "(16.7)", "(21.6)"):
    assert t_ in RAW, t_
# every equation reference (NN.M) of the body names a tag of that module (Glasserman's (9.7) is his book's)
n_refs = 0
for m_ in re.finditer(r"\(([1-9]\d?)\.(\d{1,2})[);]", TEXT[B0:B1]):
    if TEXT[B0:B1][max(0, m_.start() - 17):m_.start()] == "Glasserman 2003, ":
        continue
    src_ = RAW if m_.group(1) == "32" else (ROOT / "src" / f"lm{int(m_.group(1)):02d}.md").read_text(encoding="utf-8")
    assert "\\tag{" + f"{m_.group(1)}.{m_.group(2)}" + "}" in src_, m_.group(0)
    n_refs += 1
print(f"labels: {len(ex_labels)} exhibits, {len(eg_labels)} examples, tags (32.1)-(32.10), every exhibit cited; "
      f"links {sorted(int(v_) for v_ in links)} within prereq and leads; {n_refs} equation references resolved")

# ====================================================================== 中文導讀: every term glossed at its first use in each box
GLOSS = {
    "風險值": "value at risk", "預期短缺": "expected shortfall", "分位數": "quantile", "歷史模擬法": "historical simulation",
    "順序統計量": "order statistic", "常態分布": "normal distribution", "尾部風險": "tail risk", "厚尾": "fat tails",
    "動差": "moment", "一致性風險量數": "coherent risk measure", "劣可加性": "subadditivity",
    "條件風險值": "conditional value at risk", "凸函數": "convex function", "線性規劃": "linear programming",
    "回測": "backtest", "二項分布": "binomial distribution", "獨立性檢定": "independence test", "回撤": "drawdown",
    "最大回撤": "maximum drawdown", "排列檢定": "permutation test", "區塊自助重抽法": "block bootstrap",
    "經驗分布": "empirical distribution", "對數報酬": "log return", "公理": "axiom", "投資組合": "portfolio",
    "期望值": "expected value",
}
boxes = re.findall(r"^> \[!zh\][^\n]*\n((?:>[^\n]*\n?)+)", RAW, flags=re.MULTILINE)
assert len(boxes) == 5, len(boxes)
for b in boxes:
    for zh, en in GLOSS.items():
        if zh in b and not (zh == "回撤" and "最大回撤" in b and b.find("回撤") == b.find("最大回撤") + 2):
            first = b.find(zh)
            assert b[first + len(zh):first + len(zh) + 2 + len(en)].startswith("（" + en), (zh, en)
print(f"中文導讀: {len(boxes)} boxes, every listed term glossed at its first use in each box")

# ====================================================================== the lab's [book: ...] tags are numbers this module prints
NB = ROOT / "labs" / "LM32_lab" / "LM32_lab.ipynb"
if NB.exists():
    nb_src = "".join("".join(c["source"]) for c in json.loads(NB.read_text(encoding="utf-8"))["cells"])
    tags_ = re.findall(r'show\([^\n]*?,\s*"(-?[\d,.]+)"\)', nb_src)
    assert tags_, "no show() calls found in the lab"
    missing = sorted({t_ for t_ in tags_ if not in_text(t_)})
    assert not missing, f"lab [book: ...] values not printed in src/lm32.md: {missing}"
    print(f"lab: all {len(tags_)} [book: ...] values appear in src/lm32.md")

# ====================================================================== every number pinned by a check or listed
ALLOW: dict[str, tuple[int, str]] = {
    # equation references outside the checked strings: this module's tags and references, and other modules'
    # (each resolved under "structure")
    "1.17": (2, "(1.17), LM1's recovery gain"),
    "5.11": (2, "(5.11), LM5's tail mean"),
    "9.7": (1, "(9.7) of Glasserman (2003)"),
    "10.4": (1, "(10.4)"),
    "12.8": (1, "(12.8), LM12's Cholesky factor"),
    "14.10": (2, "(14.10), Jensen's inequality"),
    "15.6": (1, "(15.6)"),
    "15.9": (1, "(15.9)"),
    "15.11": (2, "(15.11), LM15's scaled t"),
    "16.4": (1, "(16.4)"),
    "16.7": (2, "(16.7)"),
    "18.1": (1, "(18.1)"),
    "18.5": (1, "(18.5)"),
    "18.6": (1, "(18.6)"),
    "18.7": (3, "(18.7), importance sampling"),
    "19.7": (1, "(19.7)"),
    "20.10": (1, "(20.10), Hill's estimate"),
    "21.6": (1, "(21.6), Bonferroni's rule"),
    "22.3": (1, "(22.3), the stationary bootstrap"),
    "26.3": (2, "(26.3), GARCH"),
    "26.4": (1, "(26.4)"),
    "26.8": (1, "(26.8), QLIKE"),
    "26.9": (1, "(26.9)"),
    "27.4": (1, "(27.4)"),
    "29.1": (1, "(29.1)"),
    "29.3": (1, "(29.3)"),
    "32.1": (6, "the tag (32.1) and its references"),
    "32.2": (14, "the tag (32.2) and its references, three in the Python block's comments"),
    "32.3": (6, "the tag (32.3) and its references"),
    "32.4": (6, "the tag (32.4) and its references"),
    "32.5": (5, "the tag (32.5) and its references"),
    "32.6": (3, "the tag (32.6) and two references (X5's row and KC 4 (b)'s answer are in checked strings)"),
    "32.7": (7, "the tag (32.7) and its references (the overview's is in its bullet's check)"),
    "32.8": (2, "the tag (32.8) and its reference"),
    "32.9": (2, "the tag (32.9) and its reference"),
    "32.10": (2, "the tag (32.10) and its reference in the notation"),
    # tail probabilities and levels that the text states rather than computes
    "0.01": (7, "u = 0.01: the notation, (32.1)'s note, E3's Phi^{-1}(0.01), Bin(250, 0.01), KC 9 three times"),
    "0.1": (5, "u = 0.1%: E2's question and table, X3's head, Problem and Solution 11"),
    "2.5": (8, "u = 2.5%: E2, X3's head, KC 3, X8a's head, Problems 2 and 12"),
    "0.025": (1, "the equal-tail 95% interval's lower tail, Pr(X <= j1 - 1) <= 0.025"),
    "0.975": (1, "the equal-tail 95% interval's upper tail"),
    "99.99": (1, "Basel's red-zone probability (BCBS 1996a), restated in the pitfall"),
    # plain integers that are not computed: constants of formulas, levels, numbering, inputs and citation years
    "0": (18, ("formula constants (0<u<1, Unif(0,1), probability 0, eta>=0, mean 0, g=0, max(0, .), DD^0, W_t<=0, "
               "KC 9's 'from 0') and the Python block's [0] and >= 0")),
    "1": (140, ("formula constants (F^{-1}, 1-u, 1/T, j-1, t+1, nu-1, frac1u, mathbf 1, e^r-1, ln(1+R_t), variance 1, "
                "W_0 = 1, summing to 1); the level 1% (u = 1%, '1% quantile', X8a's heads); axiom 1, Theorem 1, "
                "lo = 1, Problem and Solution 1; the Python block's 1e-12, 1e-13, 1e-14 and j - 1")),
    "2": (30, ("formula constants (nu-2, nu>2, x^2, y^2, q^2, sigma^2/2, (nu-1)/2, pi/2, chi^2); Sections 2 to 7, "
               "Section 2's, Basel's Table 2, axiom 2, lo = 2, Problem and Solution 2")),
    "3": (6, "Section 3, axiom 3 (twice), lo = 3, Problem and Solution 3"),
    "4": (7, "axiom 4 (twice), Section 4's (twice), lo = 4, Problem and Solution 4"),
    "5": (15, ("the level 5% (the worst 5%, u = 5%, the 5-95% ranges, significance at 5%, Problem 7's 5% quantile), "
               "lo = 5, Section 5, Problem and Solution 5")),
    "6": (3, "lo = 6, Problem and Solution 6"),
    "7": (4, "Sections 2 to 7, lo = 7, Problem and Solution 7"),
    "8": (6, "Section 8, lo = 8 (three headings), Problem and Solution 8"),
    "9": (3, "Section 9, Problem and Solution 9"),
    "10": (6, "the ten-session horizon of sqrt(10) (three times), Problem 10 (twice), Solution 10"),
    "11": (2, "Problem and Solution 11"),
    "12": (9, "Problem 12 (twice) and Solution 12, tfrac12, the Python block's guards and tolerances 1e-12 (five)"),
    "13": (1, "the Python block's quad tolerance 1e-13"),
    "14": (1, "the Python block's quad tolerance 1e-14"),
    "95": (8, "the 95% level of the intervals and of Basel's yellow zone"),
    "99": (20, "the 99% level of VaR and ES"),
    "100": (1, "the Python block's 100 * R (percent)"),
    "250": (9, ("Basel's 250-day year and the 250-return examples (inputs of Section 4, KC 4, E9, X6b's windows, the "
                "pitfalls, Problem 1 and the lab)")),
    "500": (1, "E9's other length, 500 days (an input)"),
    "18": (1, "18 October 2026, TR23's retrieval date (the source line)"),
    "24": (1, "24 October 2026, E5's retrieval date (the source line)"),
    "2026": (2, "the year of the two retrieval dates"),
    "1975": (1, "Hill (1975)"),
    "1994": (1, "Politis and Romano (1994)"),
    "1996": (2, "Basel's 1996 rules, BCBS (1996a)"),
    "1999": (2, "Artzner et al. (1999), Rockafellar and Uryasev's 1999 working paper"),
    "2000": (1, "Rockafellar and Uryasev (2000)"),
    "2002": (3, "Acerbi and Tasche (2002a, 2002b)"),
    "2003": (1, "Glasserman (2003)"),
    "2004": (1, "Magdon-Ismail et al. (2004)"),
}
assert not UNCOUNTED, "give these repeated strings their count:\n  " + "\n  ".join(UNCOUNTED)
# a number of the text: a decimal, a number with thousands separators, or a plain integer. A TeX command before it
# does not hide it (\times3.567, \ge6); an integer is not a number when it ends a name (R1, LM32, lm32_numbers) or
# is a subscript (j_1, W_0).
TOKEN = re.compile(r"(?<![\d.])\d+\.\d+|(?<![\d.,])\d{1,3}(?:,\d{3})+(?!\d)|(?<![\d.])\d+(?!\d)(?!\.\d)")


def is_number(m: re.Match[str]) -> bool:
    a = m.start()
    if "." in m.group(0) or "," in m.group(0):
        return True
    if TEXT[a - 1] == "_":
        return False
    if TEXT[a - 1] in string.ascii_letters:
        k = a - 1
        while TEXT[k - 1] in string.ascii_letters:
            k -= 1
        return TEXT[k - 1] == "\\"
    return True


toks = [m for a_, b_ in ((OV0, FM_END), (B0, B1)) for m in TOKEN.finditer(TEXT, a_, b_) if is_number(m)]
left_m = [m for m in toks if not any(x_ <= m.start() and m.end() <= y_ for x_, y_ in PINNED)]
left = Counter(m.group(0) for m in left_m)
want = Counter({k_: v_[0] for k_, v_ in ALLOW.items()})
if left != want:
    for m in left_m:
        if left[m.group(0)] != want[m.group(0)]:
            ln = TEXT.count("\n", 0, m.start()) + 1
            print(f"  NOT PINNED line {ln}: {m.group(0)!r} (x{left[m.group(0)]}, ALLOW x{want[m.group(0)]})   "
                  f"...{TEXT[max(0, m.start() - 60):m.end() + 25]!r}")
    for k_ in want:
        if want[k_] != left[k_]:
            print(f"  ALLOW {k_!r} x{want[k_]}, found unpinned x{left[k_]}")
assert left == want, "numbers that no check pins differ from ALLOW (listed above)"
print(f"\nnumbers: {len(toks)} in the overview and the body (decimals, thousands, integers); "
      f"{len(toks) - len(left_m)} pinned by checks, {len(left_m)} listed in ALLOW ({len(ALLOW)} strings)")
print(f"anchor differences ({len(ANCHOR_DIFFS)}):")
for a in ANCHOR_DIFFS:
    print("   ", a)
print(f"\nall {N_CHECKS} checks passed")
sys.exit(0)
