"""Every number that LM35 (Stress Testing) prints, computed and checked against src/lm35.md.

Run:  uv run python data/lm35_numbers.py
      (after data/vol3_series.py, data/vol4_series.py, data/build_series.py, data/vol5_series.py and
      data/vol5_rules.py; and after data/lm35_charts.py, whose chart and widget files this script checks)

Inputs and conventions: data/lm35_common.py, which keeps the code of data/vol6_anchors_lm35.py (the Stage 1 anchor
script): E5 through vol5_series.frames("E5"), the rules' books rebuilt from vol5_rules' files (no rule is
re-implemented here), TR23, TX23, the T5S days, the US proxies and 0050's 2007-2008 files. The module text is
src/lm35.md; plans/vol-6-anchors.md, "LM35", holds the Stage 1 anchors A35-01 .. A35-58.

Part 1 compares each anchor line, as data/lm35_common.py recomputes it, with the anchor table's Value column: a
difference is reported, never forced.

Part 2 checks the text (each check stops the script on a failure):
  chk(label, value, fmt, printed)  format(value, fmt) equals the printed string (minus signs as "-"), the value is not a
                                   rounding tie of that format, and the printed string is in the module as a whole
                                   number. Hand computations are redone from the printed, rounded inputs (PITFALLS
                                   section 7); a proxy value printed at 0 dp is checked against A35's CENT flag.
  has(label, text)                 a literal string (a date, a phrase, a table row) is in the module.
Part 3 runs the module's Python block on R2's book, checks the chart files against the text, and checks the lab
checkpoint's reference answers that build/make_lab35.py prints (its REF block) against data/lm35_common.checkpoint().
At the end the script lists the numbers of the module that no check covered and prints "all N checks passed".
"""
import ast
import math
import re
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import json

import lm35_common as K
import numpy as np
import polars as pl

ROOT = HERE.parent
MD = ROOT / "src" / "lm35.md"
ANCHORS = ROOT / "plans" / "vol-6-anchors.md"
LAB = ROOT / "build" / "make_lab35.py"
RAW = MD.read_text(encoding="utf-8")


# ====================================================================== text helpers
def norm_text(s: str) -> str:
    """The module text with TeX thousands separators, escaped percent and dollar signs, \\text{} and minus signs made
    plain."""
    s = s.replace("{,}", ",").replace("\\%", "%").replace("\\$", "$").replace("\u2212", "-").replace("\\,", "")
    return re.sub(r"\\text\{\s*([^}]*)\}", r" \1", s)


TEXT = norm_text(RAW)
N_CHECKS = 0
COVERED: set[str] = set()
ANCHOR_DIFFS: list[str] = []


def in_text(printed: str) -> bool:
    """The printed number appears as a whole number (0.33 is not inside 0.331, 0.32 not inside 10.32)."""
    return re.search(r"(?<![\d.])" + re.escape(printed) + r"(?![\d])", TEXT) is not None


def tie(value: float, fmt: str) -> bool:
    m = re.search(r"\.(\d+)", fmt)
    d = int(m.group(1)) if m else 0
    scaled = abs(value) * 10**d
    return abs(scaled - math.floor(scaled) - 0.5) < 1e-9


def chk(label: str, value: float, fmt: str, printed: str, in_md: bool = True) -> None:
    global N_CHECKS
    got = format(value, fmt)
    print(f"CHECK {label}: {got} (printed {printed})")
    assert got == printed, (label, got, printed)
    assert not tie(value, fmt), ("rounding tie: print more digits", label, value)
    assert not in_md or in_text(printed), f"{label}: {printed!r} not found in src/lm35.md"
    COVERED.add(printed.lstrip("+-"))
    N_CHECKS += 1


def pc(label: str, frac: float, d: int, printed: str, in_md: bool = True) -> None:
    """A return printed in percent at d decimals (printed with its sign as the module prints it, or unsigned)."""
    sign = printed[0] in "+-"
    chk(label, 100 * frac if sign or frac >= 0 else -100 * frac, f"{'+' if printed[0] == '+' else ''}.{d}f",
        printed, in_md)


def pcs(label: str, fracs: list[float] | np.ndarray, d: int, printed: list[str]) -> None:
    for k, (v, p) in enumerate(zip(fracs, printed, strict=True)):
        pc(f"{label} [{k + 1}]", float(v), d, p)


def has(label: str, text: str) -> None:
    global N_CHECKS
    t = norm_text(text)
    assert t in TEXT, f"{label}: {text!r} not found in src/lm35.md"
    print(f"CHECK {label}: '{text[:80]}' in text")
    for num in re.findall(r"\d[\d,]*\.?\d*", t):
        COVERED.add(num.rstrip(".,"))
    N_CHECKS += 1


def iso(d: str) -> str:
    """2019-02-27 -> '27 February 2019' as the module prints a date."""
    y, mo, dd = d.split("-")
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
              "November", "December"]
    return f"{int(dd)} {months[int(mo) - 1]} {y}"


def short(d: str) -> str:
    """2019-02-27 -> '27 Feb 2019' as the module's tables print a date."""
    y, mo, dd = d.split("-")
    return f"{int(dd)} {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][int(mo) - 1]} {y}"


def row(label: str, cells: list[str]) -> None:
    """A table row of the module, as printed (an empty cell is '| |')."""
    has(label, "|" + "|".join(f" {c} " if c else " " for c in cells) + "|")


def s2(x: float, d: int = 2) -> str:
    """A signed percent as the module's tables print it (U+2212 for the minus, normalized here)."""
    return f"{100 * x:+.{d}f}"


# ====================================================================== part 1: the anchors
def _anchor_values() -> dict[str, str]:
    rows: dict[str, str] = {}
    sec = ANCHORS.read_text(encoding="utf-8").split("\n## LM35", 1)[1].split("\n## ", 1)[0]
    for line in sec.splitlines():
        if line.startswith("| A35-"):
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
            rows[cells[0]] = cells[3].strip("`").replace("\\|", "|")
    return rows


ANCHOR_ROWS = _anchor_values()
assert len(ANCHOR_ROWS) == 58, len(ANCHOR_ROWS)
for line in K.OUT:
    aid, got = line.split(" ", 1)
    ok = got == ANCHOR_ROWS[aid]
    print(f"ANCHOR {aid}: {'ok' if ok else 'DIFFERS'}")
    if not ok:
        ANCHOR_DIFFS.append(f"{aid}:\n      script {got}\n      anchor {ANCHOR_ROWS[aid]}")

# ====================================================================== part 2: the text
fr, WD, WIN, WORST, RT, LV, TPOS, TD = K.fr, K.WD, K.WIN, K.WORST, K.RT, K.LV, K.TPOS, K.TD
FUNDS, RULES = K.FUNDS, K.RULES
i7 = K.i7
W7 = fr.W[i7]
day7 = K.day7
net7 = K.net7

# ---------------------------------------------------------------- the frames (notation note, X1, E6)
chk("T", len(fr.est_dates), ",d", "2,362")
assert (fr.est_dates[0], fr.est_dates[-1], fr.base) == ("2017-01-18", "2026-10-08", "2017-01-17")
has("estimation dates", "joint returns from 18 January 2017 to 8 October 2026")
chk("A", fr.A, ".2f", "242.95")
chk("wealth sessions", len(WD), ",d", "2,368")
chk("years", fr.years, ".2f", "9.72")
has("years from", "over 9.72 years from the close of 17 January 2017")
chk("A_w", fr.A_wealth, ".2f", "243.57")
chk("TR23 returns", int(np.isfinite(RT).sum()), ",d", "5,849")

# ---------------------------------------------------------------- the case and X1
pc("TR23 on 7 April 2025 (lm26.md:32)", RT[TPOS["2025-04-07"]], 2, "9.70")
assert int((RT[np.isfinite(RT)] < RT[TPOS["2025-04-07"]] - K.EPS).sum()) == 0, "7 April 2025 is TR23's worst day"
assert TD[TPOS["2025-04-07"] - 1] == "2025-04-02"
assert (date(2025, 4, 7) - date(2025, 4, 2)).days == 5
has("case: the closure", "After its close on 2 April 2025, Taiwan's market did not trade again until 7 April")
pc("worst 5 sessions 2025", WORST["2025-04-07"][5][0], 2, "15.96")
pc("worst 5 sessions 2020", WORST["2020"][5][0], 2, "16.51")
assert TD[WORST["2025-04-07"][5][1]] == "2025-04-09" and TD[WORST["2025-04-07"][5][1] - 5] == "2025-03-31"
mr = re.search(r"5 sessions \(5845 spans\): 2020's worst [^|]* rank 1; 2025-04-07's worst [^|]* rank 2", K.OUT[57])
assert mr, "A35-58: 2025's worst five sessions rank 2, behind 2020's"
o, h_, lo_, c_, v_ = K.row["2025-04-07"]
assert o == h_ == lo_ == c_ == 158.4 and K.exact == K.Fraction(-1, 10)
has("case: one price", "0050 traded at one price all day, 158.40, exactly 10% below its last close")
chk("0050 volume, millions", v_ / 1e6, ".1f", "29.6")
pcs("X1 returns", W7, 2, ["-10.00", "-12.59", "+1.81", "-3.10", "-14.62"])
pc("case 00646", W7[1], 2, "12.59")
pc("case 00642U", W7[4], 2, "14.62")
pc("case R7", day7["R7"], 2, "5.06")
pc("case R4", day7["R4"], 2, "8.33")
assert min(day7.values()) == day7["R4"] and max(day7.values()) == day7["R7"]
chk("R8 after the 3 March trade", float(K.expo("R8", "2025-03-03").sum()), ".3f", "1.319")
pc("case R8 (named-day replay)", day7["R8"], 2, "7.94")
pc("case R8 (wealth, with interest)", net7["R8"], 2, "7.94", in_md=False)
pred = K.pred
pc("case R1 beta model", float(K.expo("R1", "2025-04-02") @ pred), 2, "3.62")
pc("case R1 actual", day7["R1"], 2, "7.70")
assert float(K.expo("R1", "2025-04-02") @ pred) / day7["R1"] < 0.5, "under half"
beta, r2 = K.beta, K.r2
for j, p_ in enumerate(["1.048", "0.527", "-0.071", "0.161", "0.198"]):
    chk(f"beta {FUNDS[j]}", float(beta[j]), ".3f", p_)
pcs("X1 beta x TR23", pred, 2, ["-10.17", "-5.11", "+0.69", "-1.56", "-1.92"])
for j, (b_, p_) in enumerate(zip([1.048, 0.527, -0.071, 0.161, 0.198], ["-10.17", "-5.11", "+0.69", "-1.56", "-1.92"],
                                 strict=True)):
    assert f"{b_ * -9.70:+.2f}" == p_, ("X1 from the printed beta and -9.70", FUNDS[j])
row("X1 0050", ["0050", "TWSE", "10%", "−10.00", "1.048", "−10.17"])
row("X1 00679B", ["00679B", "TPEx", "none", "+1.81", "−0.071", "+0.69"])
row("X1 R1", ["R1's book", "", "", "−7.70", "", "−3.62"])
row("X1 rules", ["Loss, %"] + [f"{-100 * day7[k]:.2f}" for k in RULES])
assert f"{-100 * net7['R8']:.2f}" == f"{-100 * day7['R8']:.2f}", "R8's loss rounds alike with and without interest"
chk("R8's exposure at the 2 April close", float(K.expo("R8", "2025-04-02").sum()), ".3f", "1.331")
chk("R8's interest, points", 100 * (day7["R8"] - net7["R8"]), ".3f", "0.005")
assert max(abs(net7[k] - day7[k]) for k in RULES if k != "R8") < 1e-12, "R1-R7 hold no cash"

# ---------------------------------------------------------------- hygiene note
has("hygiene: fixed", "The through case fixed its rules on 24 October 2026")
has("hygiene: labels", "the windows, limits, intraday statistics and the 2022 illustration")
has("hygiene: in-sample", "Betas, distances, the partial scenario, the (16.10) check and the reverse stress test")
has("hygiene: hypothetical", "So are 2020 on proxies, the other shocks, ruin scalings, the TX position, presets and "
    "problems.")
# the hygiene count: eight rules, five scenarios, one illustration (2022), four built shocks (the factor shock, the
# partial scenario, the correlation break, the worst day of each fund), one reverse stress test per book
assert len(K.RULES) == 8 and len(K.SCEN) == 5
built = {"factor": K.beta * -0.10, "partial": K.full, "break": K.brk, "worst": K.woe}
assert len(built) == 4 and all(np.isfinite(v).all() and v.shape == (5,) for v in built.values())
has("hygiene: count", "eight rules, none chosen by a scenario, five scenarios, one illustration, four built shocks and "
    "one reverse stress test per book")
has("hygiene: 00635U", "GLD also for 00635U, traded from 15 April 2015")
chk("break correlation", K.RHO_BRK, ".2f", "0.30")

# ---------------------------------------------------------------- Section 2: the windows (X2, E1, pitfall, KC)
NAMES = ["2008", "2015", "2020", "2024-08-05", "2025-04-07"]
SHORTN = ["2008", "2015", "2020", "2024", "2025"]
ranks = {}
for n, sn in zip(NAMES, SHORTN, strict=True):
    p, t, nd = WIN[n]
    sess = TPOS[t] - TPOS[p]
    rank = int((RT[np.isfinite(RT)] < RT[TPOS[nd]] - K.EPS).sum()) + 1
    ranks[n] = rank
    row(f"X2 dates {sn}", [sn, short(p), short(t), str(sess), short(nd), str(rank)])
    vals = [RT[TPOS[nd]], WORST[n][5][0], WORST[n][20][0], LV[TPOS[t]] / LV[TPOS[p]] - 1]
    row(f"X2 losses {sn}", [sn] + [f"{100 * x:.2f}".replace("-", "−") for x in vals])
    for k, x in enumerate(vals):
        assert not tie(100 * x, ".2f"), (n, k)
        COVERED.add(f"{-100 * x:.2f}")
assert ranks == {"2008": 4, "2015": 17, "2020": 8, "2024-08-05": 2, "2025-04-07": 1}
has("X2: 2024's 20 sessions", "2024's worst 20 sessions start before its peak, at the close of 4 July")
assert TD[WORST["2024-08-05"][20][1] - 20] == "2024-07-04" and "2024-07-04" < WIN["2024-08-05"][0]
has("X2: the limit history", "TWSE's stock limit was 7% until 1 June 2015")
pc("2008 peak to trough", LV[TPOS[WIN["2008"][1]]] / LV[TPOS[WIN["2008"][0]]] - 1, 2, "56.02")
pc("2024 peak to trough", LV[TPOS[WIN["2024-08-05"][1]]] / LV[TPOS[WIN["2024-08-05"][0]]] - 1, 2, "18.31")
p25, t25, nd25 = WIN["2025-04-07"]
assert (p25, t25, nd25) == ("2025-02-21", "2025-04-09", "2025-04-07") and TPOS[t25] - TPOS[p25] == 30
has("E1 window", "TR23 peaked on 21 February 2025 and bottomed 30 sessions later, on 9 April, 26.54% lower")
pc("E1 peak to trough", LV[TPOS[t25]] / LV[TPOS[p25]] - 1, 2, "26.54")
has("E1 worst day", "Its worst day, 7 April, lost 9.70% ([[LM26]]), five calendar days after 2 April")
assert TD[WORST["2025-04-07"][20][1] - 20] == "2025-03-10"
has("E1 spans", "The worst 5 sessions, from the close of 31 March, lose 15.96%, and the worst 20, from the close of "
    "10 March, 22.38%")
pc("E1 worst 20", WORST["2025-04-07"][20][0], 2, "22.38")
chk("five-session spans", len(LV) - 5, ",d", "5,845")
has("E1 rank", "only one, ending 19 March 2020, lost more")
k24, k25 = TPOS["2024-08-05"], TPOS["2025-04-09"]
pk = int(np.argmax(LV[:k25 + 1]))
assert TD[pk] == "2024-07-11" and k25 - pk == 176
has("E1 running peak", "from the running peak, 11 July 2024: 27.72% on 9 April 2025, 176 sessions later, and 18.31% "
    "on 5 August 2024")
pc("E1 DD 2025", 1 - LV[k25] / LV[:k25 + 1].max(), 2, "27.72")
pc("E1 DD 2024", 1 - LV[k24] / LV[:k24 + 1].max(), 2, "18.31")
gaps = np.array([(date.fromisoformat(TD[i]) - date.fromisoformat(TD[i - 1])).days for i in range(1, len(TD))])
long_ = gaps >= 4
r1_ = RT[1:]
chk("spans >= 4 days", int(long_.sum()), "d", "140")
pc("their share (not printed)", float(long_.mean()), 1, "2.4", in_md=False)
pc("their mean |R|", float(np.abs(r1_[long_]).mean()), 2, "1.39")
pc("the rest", float(np.abs(r1_[~long_]).mean()), 2, "0.83")
has("pitfall spans", "Of TR23's 5,849 returns, 140 span four or more calendar days")
has("KC2 answer", "Compare it with the 140 returns that span four or more days, 1.39% in mean absolute size, not with "
    "the rest (0.83%)")
has("pitfall closure", "the Lunar New Year closure of 21 to 29 January (TWSE's 2020 schedule)")
has("pitfall 7 April", "7 April 2025 followed four days without trading")
pc("KC 2020-01-30", RT[TPOS["2020-01-30"]], 2, "5.75")
assert WIN["2020"][2] == "2020-01-30" and TD[TPOS["2020-01-30"] - 1] == "2020-01-20" and K.TR23_RANK_0130 == 8
assert (date(2020, 1, 30) - date(2020, 1, 20)).days == 10
has("KC rank", "the 8th worst of 5,849 returns, and followed the session of 20 January")
has("KC answer", "The return spans ten calendar days across the Lunar New Year closure")

# ---------------------------------------------------------------- Section 3: replays (X3, X4, E2, E3, KC)
FZ, AC = K.FROZEN, K.ACTUAL
named = {}
for n, sn in zip(["2020", "2024-08-05", "2025-04-07"], ["2020", "2024", "2025"], strict=True):
    nd = WIN[n][2]
    eve = WD[K.WIDX[nd] - 1]
    named[n] = {k: float(K.expo(k, eve) @ fr.W[K.WIDX[nd]]) for k in RULES}
    for lab, src in (("frozen", FZ[n]), ("actual", AC[n]), ("named day", named[n])):
        row(f"X3 {sn} {lab}", [f"{sn}, {lab}"] + [s2(src[k]).replace("-", "−") for k in RULES])
        for k in RULES:
            assert not tie(100 * src[k], ".2f"), (n, lab, k)
            COVERED.add(f"{abs(100 * src[k]):.2f}")
assert all(abs(named["2025-04-07"][k] - day7[k]) < 1e-15 for k in RULES)
# the hypothetical block: 2008 and 2015 at the first weights, R1/R3/R6/R8 (USO), at the digits a cent leaves safe
hyp = {"2008": {"R1": "-24.5", "R3": "-9", "R6": "-15", "R8": "-12"},
       "2015": {"R1": "-7.2", "R3": "+1.8", "R6": "-2.1", "R8": "-1.8"}}
for n, cells in hyp.items():
    for k, p_ in cells.items():
        x = float(K.FIRST[k] @ K.PROXY_RET[n]["USO"])
        u = K.book_u(K.FIRST[k], K.PROXY_U[n]["USO"])
        d0 = 0 if "." not in p_ else 1
        cent1 = math.floor(1000 * (x - u) + 0.5) != math.floor(1000 * (x + u) + 0.5)
        assert (d0 == 0) == cent1, (n, k, "printed at 0 dp exactly when a cent could move the first decimal")
        assert d0 or math.floor(100 * (x - u) + 0.5) == math.floor(100 * (x + u) + 0.5), (n, k, "0 dp is safe")
        chk(f"X3 hypothetical {n} {k}", 100 * x, f"+.{d0}f" if p_[0] == "+" else f".{d0}f", p_, in_md=False)
    has(f"X3 hypothetical {n}", f"{n} " + ", ".join(f"{k} {p_.replace('-', '−')}" for k, p_ in cells.items()))
P14 = {k: K.expo(k, "2025-04-02") * W7 for k in ("R1", "R3", "R6", "R8")}
for k, prt in (("R1", ["-2.00", "-2.53", "+0.36", "-0.62", "-2.91"]), ("R3", ["-0.22", "-4.07", "+0.65", "-0.68",
                                                                              "-1.08"]),
               ("R8", ["-1.80", "-3.64", "+0.74", "-0.91", "-2.33"])):
    got = [f"{100 * x:+.2f}" for x in P14[k]]
    assert got == prt, (k, got)
    assert f"{sum(float(g) for g in got):.2f}" == f"{100 * day7[k]:.2f}", (k, "two-decimal parts add to the total")
r6_2 = [f"{100 * x:+.2f}" for x in P14["R6"]]
chk("X4 R6 two-decimal sum", sum(float(g) for g in r6_2), ".2f", "-5.95")
pc("X4 R6 total", day7["R6"], 2, "-5.96")
pcs("X4 R6 three decimals", P14["R6"], 3, ["-1.351", "-2.733", "+0.556", "-0.684", "-1.752"])
chk("X4 R6 three-decimal sum", sum(float(f"{100 * x:.3f}") for x in P14["R6"]), ".3f", "-5.964")
pc("X4 R6 total, 3 dp", day7["R6"], 3, "-5.964")
assert K.R1_LAST_TRADE_0402 == "2025-04-01" and np.abs(K.E_R1_0402 - 0.2).max() < 0.002
has("E2 trade", "After its trade of 1 April, R1's exposures on 2 April are near 0.2")
pcs("E2 parts", P14["R1"], 2, ["-2.00", "-2.53", "+0.36", "-0.62", "-2.91"])
pc("E2 R3", day7["R3"], 2, "5.40")
pc("E2 R3 from 00646", P14["R3"][1], 2, "4.07")
pc("E3 R8 frozen 2020", FZ["2020"]["R8"], 2, "17.04")
pc("E3 R8 path 2020", AC["2020"]["R8"], 2, "12.58")
r8 = {d: (float(K.PRE["R8"][d].sum()), float(K.expo("R8", d).sum())) for d in K.PRE["R8"]}
chk("E3 R8 entry", float(K.expo("R8", WIN["2020"][0]).sum()), ".3f", "1.307")
chk("E3 R8 3 February", r8["2020-02-03"][1], ".3f", "0.991")
chk("E3 R8 2 March (A31-33)", r8["2020-03-02"][1], ".3f", "0.884")
g20 = K.growth(*WIN["2020"][:2])
pc("E3 book of 3 February", float(K.expo("R8", "2020-02-03") @ g20), 2, "13.20")
pc("E3 book of 2 March", float(K.expo("R8", "2020-03-02") @ g20), 2, "11.68")
has("E3 LM31's 0.884", "cut its exposure from 1.307 to 0.991, then to [[LM31]]'s 0.884. Frozen over the whole window, "
    "those books lose 13.20% and 11.68%.")
assert "0.991" not in (ROOT / "src" / "lm31.md").read_text(encoding="utf-8") and \
    "0.884" in (ROOT / "src" / "lm31.md").read_text(encoding="utf-8"), "0.991 is LM35's, 0.884 LM31's"
pc("E3 R8 frozen 2025", FZ["2025-04-07"]["R8"], 2, "10.15")
chk("E3 R8 exposure 21 Feb", float(K.expo("R8", WIN["2025-04-07"][0]).sum()), ".3f", "1.005")
pc("E3 R8 path 2025", AC["2025-04-07"]["R8"], 2, "13.84")
g25 = K.growth(*WIN["2025-04-07"][:2])
assert f"{r8['2025-03-03'][0]:.3f}" == "1.005"
pc("E3 book of 3 March", float(K.expo("R8", "2025-03-03") @ g25), 2, "13.35")
chk("E3 1 April (A31-32)", r8["2025-04-01"][1], ".2f", "1.33")
pc("E3 book of 1 April", float(K.expo("R8", "2025-04-01") @ g25), 2, "13.42")
assert max(r8["2025-03-03"][1], r8["2025-04-01"][1], r8["2020-02-03"][1], r8["2020-03-02"][1]) < 1.5 - 1e-6
has("E3 cap", "and the cap of 1.5 bound at neither")
for n in ("2020", "2024-08-05", "2025-04-07"):
    s_, dev = K.SCALE[n]
    assert dev < 1e-12, (n, "R8's book is R6's scaled")
    assert abs(FZ[n]["R8"] - s_ * FZ[n]["R6"]) < 1e-12
pc("KC3 R6 frozen 2025", FZ["2025-04-07"]["R6"], 2, "10.10")
chk("KC3 from printed", 1.005 * 10.10, ".2f", "10.15")
has("KC3 product", "$1.005\\times10.10\\%=10.15\\%$")

# ---------------------------------------------------------------- Section 4: proxies (35.5), E4, E5, KC
# A35-24's counts of US sessions per TR23 date (no longer printed: the second pass cut them for words)
ns = [int(K.LASTD[i] - K.LASTD[i - 1]) for i in range(K.first_tw, len(TD))]
chk("TR23 dates from 3 July 2007", len(ns), ",d", "4,736", in_md=False)
assert TD[K.first_tw] == "2007-07-03"
chk("no new US session", ns.count(0), "d", "170", in_md=False)
chk("one", ns.count(1), ",d", "4,421", in_md=False)
chk("two", ns.count(2), "d", "94", in_md=False)
chk("three or more", sum(1 for x in ns if x >= 3), "d", "51", in_md=False)
has("pairing compounds", "A Taiwan date's return thus compounds every US session since the previous Taiwan date.")
has("LM27's timing (lm27.md:196)", "00646's and 00679B's 13:30 closes follow the previous New York session, and "
    "futures-trust ETFs are valued on European and US futures ([[LM27]])")
l27 = (ROOT / "src" / "lm27.md").read_text(encoding="utf-8")
assert "the 13:30 closes of 00646 and 00679B follow the previous New York session" in l27
assert "valued on European and US futures" in l27
# in 2008 none of E5's foreign funds existed; in the 2015 window only 00635U (listed 2015-04-15; 00642U listed
# 2015-09-07, after the window's trough of 2015-08-24; listing dates from project/SOURCES.md)
assert WIN["2015"][1] == "2015-08-24" and "2015-04-15" < WIN["2015"][1] < "2015-09-07"
has("2015 window", "In 2008 none of E5's foreign funds existed, and in the 2015 window only 00635U.")
a8, b8, nd8 = WIN["2008"]
assert (a8, b8, nd8) == ("2007-10-29", "2008-11-20", "2008-01-22")
R08 = K.PROXY_RET["2008"]
pc("E4 0050 2008", R08["USO"][0], 2, "55.66")
pc("E4 TR23 2008", LV[TPOS[b8]] / LV[TPOS[a8]] - 1, 2, "56.02")


def proxy(label: str, s: str, a: str, b: str, printed: str) -> None:
    """A proxy return printed to 0 dp exactly when A35's CENT rule says a cent could move its first decimal (signed as
    printed, or unsigned for a loss)."""
    x, u = K.prox(s, a, b), K.cent(s, a, b)
    cent1 = math.floor(1000 * (x - u) + 0.5) != math.floor(1000 * (x + u) + 0.5)
    d0 = 0 if "." not in printed else 1
    assert (d0 == 0) == cent1, (label, x, u)
    if printed[0] in "+-":
        chk(label, 100 * x, f"+.{d0}f", printed)
    else:
        chk(label, -100 * x, f".{d0}f", printed)


proxy("E4 SPY", "SPY", a8, b8, "-44")
proxy("E4 TLT", "TLT", a8, b8, "+19")
proxy("E4 GLD", "GLD", a8, b8, "-4.1")
proxy("E4 USO", "USO", a8, b8, "-37.3")
proxy("E4 DBO", "DBO", a8, b8, "-27")
fxa, fxb = float(K.USRATE[K.LASTD[TPOS[a8]]]), float(K.USRATE[K.LASTD[TPOS[b8]]])
chk("E4 FX start", fxa, ".3f", "32.390")
chk("E4 FX end", fxb, ".3f", "33.390")
pc("E4 FX change", fxb / fxa - 1, 2, "+3.09")
for k, oil, p_ in (("R1", "USO", "24.5"), ("R1", "DBO", "22"), ("R2", "USO", "25.9"), ("R3", "USO", "9")):
    x = float(K.FIRST[k] @ R08[oil])
    u = K.book_u(K.FIRST[k], K.PROXY_U["2008"][oil])
    d0 = 0 if "." not in p_ else 1
    assert (d0 == 0) == (math.floor(1000 * (x - u) + 0.5) != math.floor(1000 * (x + u) + 0.5)), (k, oil)
    chk(f"E4 {k} {oil}", -100 * x, f".{d0}f", p_)
assert np.allclose(K.FIRST["R1"], 0.2) and K.FIRST["R2"][4] == 0
has("E4 first weights", "on the rules' first weights of 4 March 2019")
# from the printed returns (SPY and TLT at whole percents) R1 and R2 give 24.4 and 25.8, not 24.5 and 25.9: the text
# says the book losses come from the unrounded returns
assert f"{-0.2 * (-55.66 - 44 + 19 - 4.1 - 37.3):.1f}" == "24.4"
assert f"{-(0.4 * -55.66 + 0.2 * -44 + 0.3 * 19 + 0.1 * -4.1):.1f}" == "25.8"
assert np.allclose(K.FIRST["R2"], [0.4, 0.2, 0.3, 0.1, 0.0])
assert f"{-0.2 * (-55.66 - 44 + 19 - 4.1 - 27):.0f}" == "22", "R1 with DBO follows from the printed returns"
has("E4 unrounded", "From the unrounded returns, R1, 20% in each, loses 24.5% with USO and 22% with DBO")
row("E4 proxies", ["Return", "−44", "+19", "−4.1", "−37.3", "−27"])
# KC section 4 (b): half 0050 and half SPY over the 2008 window, a whole percent (a cent could move SPY's first decimal)
half = 0.5 * R08["USO"][0] + 0.5 * K.prox("SPY", a8, b8)
u_half = 0.5 * K.cent("SPY", a8, b8)
assert round(-100 * half) == 50 and math.floor(100 * (-half - u_half) + 0.5) == math.floor(100 * (-half + u_half) + 0.5)
chk("KC4b half 0050, half SPY (unrounded)", -100 * half, ".0f", "50", in_md=False)
chk("KC4b from printed", 0.5 * 55.66 + 0.5 * 44, ".0f", "50", in_md=False)
has("KC4b", "About 50%, half of 55.66% plus half of 44%, in whole percents like SPY's return.")
has("KC4b question", "what does a hypothetical book of half 0050 and half SPY lose over the 2008 window?")
assert K.TRADES.filter(pl.col("rule") == "R1").sort("trade")["trade"][0] == "2019-03-04"
assert K.LASTD[TPOS["2008-01-22"]] == K.LASTD[TPOS["2008-01-21"]] and "2008-01-21" not in K.usd
has("E4 named day", "On 22 January 2008 every proxy returned exactly 0, since no US session is dated 21 January")
pc("E4 R2 on 22 January", 0.4 * K.R50["2008-01-22"], 1, "2.8")
pc("E4 0050 on 22 January", K.R50["2008-01-22"], 2, "6.93")
pd25 = re.search(r"00646~SPY daily ([\d.]+) weekly ([\d.]+).*00679B~TLT daily ([\d.]+) weekly ([\d.]+).*00635U~GLD "
                 r"daily ([\d.]+) weekly ([\d.]+).*00642U~USO daily ([\d.]+) weekly ([\d.]+).*00642U~DBO daily ([\d.]+) "
                 r"weekly ([\d.]+)", K.OUT[24])
assert pd25 and "498 ISO weeks" in K.OUT[24]
corr = [float(x) for x in pd25.groups()]
for v, p_ in zip(corr[0::2], ["0.705", "0.783", "0.745", "0.655", "0.696"], strict=True):
    chk("E5 daily correlation", v, ".3f", p_)
for v, p_ in zip(corr[1::2], ["0.944", "0.952", "0.926", "0.845", "0.894"], strict=True):
    chk("E5 weekly correlation", v, ".3f", p_)
has("E5 weeks", "over 498 ISO weeks of the wealth frame (first, last and two across 0050's halt dropped)")
row("E5 daily", ["Daily", "0.705", "0.783", "0.745", "0.655", "0.696"])
row("E5 weekly", ["Weekly", "0.944", "0.952", "0.926", "0.845", "0.894"])
has("E5 roll", "Invesco states no roll rule for DBO, unlike USCF for USO, so the two are compared by their data only.")
a20, b20, _ = WIN["2020"]
pc("E5 00642U 2020", g20[4], 2, "46.42")
proxy("E5 USO 2020", "USO", a20, b20, "60.7")
x_dbo, u_dbo = K.prox("DBO", a20, b20), K.cent("DBO", a20, b20)
assert math.floor(100 * (x_dbo - u_dbo) + 0.5) != math.floor(100 * (x_dbo + u_dbo) + 0.5) and round(-100 * x_dbo) == 46
has("E5 DBO about", "USO 60.7% and DBO about 46%")
gfund = g20
uso = np.array([gfund[0], K.prox("SPY", a20, b20), K.prox("TLT", a20, b20), K.prox("GLD", a20, b20),
                K.prox("USO", a20, b20)])
dbo = uso.copy()
dbo[4] = K.prox("DBO", a20, b20)
e20 = K.expo("R1", a20)
pc("E5 R1 on proxies, USO", float(e20 @ uso), 1, "21.5")
chk("E5 R1 on proxies, DBO", -100 * float(e20 @ dbo), ".0f", "19")
pc("E5 R1 on the funds", FZ["2020"]["R1"], 2, "19.84")
gap08 = float(K.FIRST["R1"] @ (R08["DBO"] - R08["USO"]))
gap20 = float(e20 @ (dbo - uso))
assert round(100 * gap08) == 2 and round(100 * gap20) == 3, (gap08, gap20)
has("pitfall: oil proxy", "from the unrounded losses, the oil proxy alone moves R1's loss by about two points in 2008 "
    "and three in 2020")
has("zh: correlations", "只有 0.655 到 0.783")
z_ = K.z
chk("KC4 dates without a US session", int(z_.sum()), "d", "80")
pc("KC4 00646 none", float(np.abs(K.X[z_, 1]).mean()), 2, "0.43")
pc("KC4 00646 one", float(np.abs(K.X[K.one, 1]).mean()), 2, "0.67")
has("KC4 mean absolute", "00646 still moved 0.43% on average in absolute size, against 0.67% on dates with one US "
    "session")

# ---------------------------------------------------------------- Section 5: shocks (E6, E7, KC)
chk("R-squared 0050", float(r2[0]), ".3f", "0.924")
chk("R-squared 00646", float(r2[1]), ".3f", "0.363")
assert r2[4] < 0.01
has("E6 under 1%", "00642U's variance is residual (R-squared under 1%)")
pc("E6 00646 model", pred[1], 2, "-5.11")
pc("E6 00642U model", pred[4], 2, "-1.92")
full, brk = K.full, K.brk
pcs("E6 partial scenario", full[1:], 2, ["-4.79", "+0.71", "-1.46", "-1.69"])
CUR = K.CUR
pc("E6 factor R1", float(CUR["R1"] @ (beta * -0.10)), 2, "3.77")
pc("E6 factor R4", float(CUR["R4"] @ (beta * -0.10)), 2, "7.28")
# the printed 3-dp betas give R1 3.76 (A35-31), so the text says the losses come from the unrounded betas and books
pc("E6 factor R1 from 3-dp betas (not printed)", float(CUR["R1"] @ (np.round(beta, 3) * -0.10)), 2, "3.76",
   in_md=False)
has("E6 unrounded", "costs R1 3.77% and R4 7.28%, from the unrounded betas and books.")
has("E6 last column", "Times −9.70%, the betas give [[ex:case]]'s last column: 00642U −1.92% against −14.62% actual, "
    "and R1 −3.62% against −7.70%.")
sd = np.sqrt(np.diag(K.S))
chk("E7 full correlation (A27-11)", float(K.S[0, 2] / sd[0] / sd[2]), ".3f", "-0.105")
chk("E7 lambda_N", K.lam_min, ".3f", "0.298")
pc("E7 00679B full", full[2], 2, "+0.71")
pc("E7 00679B break", brk[2], 2, "-2.04")
pc("E7 R3 full", float(CUR["R3"] @ full), 2, "1.41")
pc("E7 R3 break", float(CUR["R3"] @ brk), 2, "2.95")
pc("E7 R7 full", float(CUR["R7"] @ full), 2, "1.40")
pc("E7 R7 break", float(CUR["R7"] @ brk), 2, "3.00")
a22, b22 = TD[K.p22], TD[K.k22]           # the 2022 illustration's peak and trough
assert (a22, b22) == ("2022-01-17", "2022-10-25")
has("E7 2022 dates", "an illustration outside the five scenarios, from 17 January to 25 October 2022:")
row("E7 2022 table", ["Return"] + [s2(x).replace("-", "−") for x in (
    LV[TPOS[b22]] / LV[TPOS[a22]] - 1, K.g22[0], K.g22[2], float(K.expo("R2", a22) @ K.g22),
    float(K.expo("R4", a22) @ K.g22))])
pc("E7 2022 TR23", LV[TPOS[b22]] / LV[TPOS[a22]] - 1, 2, "28.47")
pc("E7 2022 0050", K.g22[0], 2, "33.93")
pc("E7 2022 00679B", K.g22[2], 2, "22.15")
pc("E7 2022 R2", float(K.expo("R2", a22) @ K.g22), 2, "22.37")
pc("E7 2022 R4", float(K.expo("R4", a22) @ K.g22), 2, "29.86")
chk("E7 2022 daily", float(np.corrcoef(K.X[K.ep, 0], K.X[K.ep, 2])[0, 1]), ".3f", "-0.138")
chk("E7 2022 weekly", float(np.corrcoef(K.we[:, 0], K.we[:, 2])[0, 1]), "+.3f", "+0.019")
chk("E7 2022 weeks", K.nwe, "d", "38")
chk("E7 full weekly (A27-11)", float(np.corrcoef(K.wf[:, 0], K.wf[:, 2])[0, 1]), ".3f", "-0.022")
assert K.nwf == 498
chk("E7 tail days", K.nev, "d", "48")
tail = re.search(r"00646: data ([\d.]+), \(16.10\) ([\d.]+), full ([\d.]+)", K.OUT[34])
assert tail
chk("E7 tail correlation", float(tail.group(1)), ".3f", "0.540")
chk("E7 (16.10)", float(tail.group(2)), ".3f", "0.669")
chk("E7 full", float(tail.group(3)), ".3f", "0.599")
chk("E7 variance ratio", K.vs / K.s0**2, ".3f", "1.449")
chk("E7 SE", K.se646, ".2f", "0.10")
chk("E7 gap in SEs", (K.model646 - K.r646) / K.se646, ".1f", "1.3")
chk("E7 gap in SEs from printed", 0.13 / 0.10, ".1f", "1.3", in_md=False)
assert round(K.model646 - K.r646, 2) == 0.13
has("zh5", "它預測 R1 虧 3.62%，實際卻虧 7.70%")
pc("KC5 R4 break", float(CUR["R4"] @ brk), 2, "6.89")
assert abs(float(CUR["R4"] @ full) - float(CUR["R4"] @ brk)) < 1e-15 and CUR["R4"][2] == 0
chk("KC5 R4 00679B", float(CUR["R4"][2]), ".3f", "0.000")

# ---------------------------------------------------------------- Section 6: reverse stress (E8, X6, Deep Dive, KC)
S, MU = K.S, K.MU
kmax, k7 = K.kmax, K.k7
for k, (pm, ps, pd) in {"R1": ("0.048", "0.7434", "13.52"), "R2": ("0.055", "0.7216", "13.93"),
                        "R4": ("0.078", "1.0174", "9.91"), "R5": ("0.030", "0.5717", "17.54"),
                        "R8": ("0.051", "0.8191", "12.27")}.items():
    e = CUR[k]
    sp, mp = math.sqrt(float(e @ S @ e)), float(e @ MU)
    pc(f"E8 {k} mean", mp, 3, pm)
    pc(f"E8 {k} s_p", sp, 4, ps)
    chk(f"E8 {k} d*", (K.LOSS + mp) / sp, ".2f", pd)
    chk(f"E8 {k} d* from printed", (10 + float(pm)) / float(ps), ".2f", pd)
pcs("E8 R1 shock", K.XSTAR["R1"], 2, ["-10.47", "-8.79", "-1.21", "-6.12", "-23.00"])
E8 = {"R1": ("0.048", "0.7434", "13.52"), "R2": ("0.055", "0.7216", "13.93"), "R4": ("0.078", "1.0174", "9.91"),
      "R5": ("0.030", "0.5717", "17.54"), "R8": ("0.051", "0.8191", "12.27")}
row("E8 means", ["Mean, %"] + [E8[k][0] for k in E8])
row("E8 s_p", ["$s_p$, %"] + [E8[k][1] for k in E8])
row("E8 d*", ["$d^*$"] + [E8[k][2] for k in E8])
# X6's table: the four shocks and their distances
xb2_, db2_, _ = K.bounded(CUR["R2"])
x6 = [("R1, (35.4)", K.XSTAR["R1"], (K.LOSS + float(CUR["R1"] @ MU)) / math.sqrt(float(CUR["R1"] @ S @ CUR["R1"]))),
      ("R8, (35.4)", K.XSTAR["R8"], (K.LOSS + float(CUR["R8"] @ MU)) / math.sqrt(float(CUR["R8"] @ S @ CUR["R8"]))),
      ("R2, $x_{0050}\\ge-10\\%$", xb2_, db2_), ("Worst day of each fund", K.woe, K.maha(K.woe))]
for lab, xv, dv in x6:
    for v in xv:
        assert not tie(100 * float(v), ".2f"), (lab, v)
        COVERED.add(f"{abs(100 * float(v)):.2f}")
    assert not tie(float(dv), ".2f")
    row(f"X6 {lab}", [lab] + [f"{100 * float(v):.2f}".replace("-", "−") for v in xv] + [f"{float(dv):.2f}"])
assert abs(K.maha(K.XSTAR["R8"]) - x6[1][2]) < 1e-9 and abs(float(CUR["R8"] @ K.XSTAR["R8"]) + K.LOSS) < 1e-12
assert [f"{100 * v:.2f}" for v in K.XSTAR["R8"]] == ["-8.90", "-7.65", "-4.57", "-6.75", "-14.14"]
assert [f"{100 * v:.2f}" for v in xb2_] == ["-10.00", "-10.81", "-9.89", "-8.67", "-0.34"]
assert [f"{100 * v:.2f}" for v in K.woe] == ["-10.00", "-12.59", "-7.15", "-11.09", "-22.20"]
has("E8 points to X6", "and R1's shock is the first row of [[ex:reverse]].")
od = np.argsort(-K.dt)
chk("largest distance", float(K.dt[od[0]]), ".3f", "15.017")
assert K.fr.est_dates[od[0]] == "2026-03-09" and K.fr.est_dates[od[1]] == "2020-03-09"
assert K.fr.est_dates[od[2]] == "2025-04-07"
has("E8 dates", "The sample's largest distance, 15.017, came on 9 March 2026, when 00642U rose 33.10%")
pc("E8 00642U on 9 March 2026", float(K.X[od[0], 4]), 2, "33.10")
chk("second distance", float(K.dt[od[1]]), ".3f", "12.971")
chk("2025-04-07 distance", float(K.dt[od[2]]), ".3f", "12.937")
chk("median distance", float(np.quantile(K.dt, 0.5, method="inverted_cdf")), ".2f", "1.60")
e1 = CUR["R1"]
sp1, mp1 = math.sqrt(float(e1 @ S @ e1)), float(e1 @ MU)
pc("E8 worst loss within d <= k_max", kmax * sp1 - mp1, 2, "11.12")
chk("E8 worst loss from printed", 15.017 * 0.7434 - 0.048, ".2f", "11.12")
xb1, db1, nb1 = K.bounded(CUR["R1"])
xb2, db2, nb2 = K.bounded(CUR["R2"])
xb8, db8, nb8 = K.bounded(CUR["R8"])
chk("bounded R1 d", db1, ".2f", "13.52")
chk("bounded R2 d", db2, ".2f", "17.01")
pc("bounded R2 00679B", xb2[2], 2, "-9.89")
pc("00679B worst day", float(K.woe[2]), 2, "-7.15")
assert "inactive" in nb8 and "active" in nb1 and "active" in nb2
chk("worst-of-each distance", K.maha(K.woe), ".2f", "19.07")
m40 = re.search(r"R1: d [\d.]+, .*?multipliers ([\d.]+) and ([\d.]+)", K.OUT[39])
assert m40
chk("Deep Dive R1 multiplier 1", float(m40.group(1)), ".1f", "37.3")
chk("Deep Dive R1 multiplier 2", float(m40.group(2)), ".4f", "0.8877")
m40b = re.search(r"R2: d [\d.]+, .*?multipliers ([\d.]+) and ([\d.]+)", K.OUT[39])
assert m40b and float(m40b.group(1)) > 0 and float(m40b.group(2)) > 0
chk("S11 R2 multiplier 1", float(m40b.group(1)), ".1f", "90.3")
chk("S11 R2 multiplier 2", float(m40b.group(2)), ".1f", "32.7")
has("Deep Dive bounds", "CLARABEL and OSQP agree with the closed form to $10^{-9}$, with stationarity residuals below "
    "$10^{-13}$ and complementary slackness below $10^{-9}$")
r49 = float(CUR["R1"] @ W7)
pc("widget loss", r49, 2, "7.78")
chk("widget ruin", -1 / r49, ".2f", "12.85")
chk("widget ruin from printed", 1 / 0.0778, ".2f", "12.85", in_md=False)
chk("widget d", K.maha(W7), ".2f", "12.94")
chk("widget farther", K.FARTHER_0407, "d", "2")
has("widget text", "a loss of 7.78%, ruin from leverage 12.85 (Section 8), distance 12.94 and 2 of 2,362 days "
    "farther")
pc("pitfall R1's 0050", K.XSTAR["R1"][0], 2, "-10.47")
chk("KC6 R4 d*", (K.LOSS + float(CUR["R4"] @ MU)) / math.sqrt(float(CUR["R4"] @ S @ CUR["R4"])), ".2f", "9.91")
e4 = CUR["R4"]
pc("KC6 worst loss within d <= k_0407", k7 * math.sqrt(float(e4 @ S @ e4)) - float(e4 @ MU), 2, "13.08")
chk("KC6 from printed", 12.937 * 1.0174 - 0.078, ".2f", "13.08")

# ---------------------------------------------------------------- Section 7: limits, locks, gaps (X8, X5, E9, KC)
for j, s in enumerate(FUNDS):
    w = fr.W[:, j]
    n10 = int((np.abs(w) > 0.10 + K.EPS).sum())
    lo, hi = f"{100 * w.min():+.2f}".replace("-", "−"), f"{100 * w.max():+.2f}"
    m = re.search(r"\| " + re.escape(s) + r" \| [^|]+ \| [^|]+ \| " + re.escape(lo) + r" \| " + re.escape(hi) +
                  r" \| " + str(n10) + r" \|", RAW)
    assert m, (s, lo, hi, n10)
    COVERED.update({lo.lstrip("−+"), hi.lstrip("+")})
    N_CHECKS += 1
assert K.locked == ["2025-04-07", "2025-04-10"]
has("X8 locks", "0050 traded only at its limit on 7 April 2025 (down) and 10 April 2025 (up)")
assert fr.W[K.WIDX["2025-04-10"], 0] > 0.099
o56 = K.o56
assert o56[1] == o56[2] == o56[3] == o56[4] == 31.66
has("X8 0056", "The checkpoint's 0056 locked at 31.66 on 7 April 2025")
assert K.x720 == K.Fraction(-9, 80) and K.c720["2020-03-19"] == 35.5 and K.c720[K.p720] == 40.0
has("X8 00720B", "fell 11.25% on 19 March 2020, from 40.00 to 35.50")
has("limits history", "items standing since 3 June 2016")
has("TPEx listing notice", "and TPEx's listing notice gave 00679B no limit from its first day ([[ex:limits]])")
has("X8 source", "with the checkpoint funds' `TaiwanStockPrice` files, retrieved 24 October 2026")
has("proxies' rules", "For 2008 and 2015 the proxies are read under the current rules of their funds' markets")
t5 = re.findall(r"(\d{4}-\d\d-\d\d): gap (-[\d.]+)%, low (-[\d.]+)% at ([\d:]+).*?, close (-[\d.]+)%, gap / close "
                r"([\d.]+)", K.OUT[44])
assert len(t5) == 5
gl_unr = {}
for nd, gp, low, tm, cl, ratio in t5:
    gp_, low_, cl_ = float(gp), float(low), float(cl)
    gl_unr[nd] = (gp_, cl_)
    row(f"X5 {nd}", [short(nd), f"{gp_:.2f}".replace("-", "−"), f"{low_:.2f}".replace("-", "−"), tm,
                     f"{cl_:.2f}".replace("-", "−"), f"{float(ratio):.2f}"])
    for v in (gp_, low_, cl_, float(ratio)):
        assert not tie(v, ".2f")
        COVERED.add(f"{abs(v):.2f}")
chk("X5 2015 ratio from printed", -1.66 / -4.96, ".2f", "0.33")
assert f"{gl_unr['2015-08-24'][0] / gl_unr['2015-08-24'][1]:.2f}" == "0.34"
has("X5 tie", "2020's holds through the closing call auction to 13:29:55")
assert "the last 13:29:55" in K.OUT[44]
stale = re.search(r"09:00:05 \(the daily open\) (-[\d.]+)%", K.OUT[44])
assert stale
chk("KC7c stale open", float(stale.group(1)), ".2f", "-5.52")
chk("KC7c 09:01:00", gl_unr["2025-04-07"][0], ".2f", "-10.28")
has("KC7c", "(c) The open is the stale 09:00:05 value: −5.52%, against −10.28% by 09:01:00 ([[ex:gaps]]).")
has("pitfall stale open", "FinMind's daily TAIEX open is the value at 09:00:05, before most stocks have traded.")
# X5's note: 2008's day is a minute series (the other days every 5 seconds)
t08 = pl.read_csv(K.T5S / "2008" / "2008-01-22.csv")
tt08 = [s[-8:] for s in t08["date"].to_list()]
secs = [int(h) * 3600 + int(m) * 60 + int(s) for h, m, s in (x.split(":") for x in tt08)]
assert set(np.diff(secs).tolist()) == {60} and tt08[0] == "09:00:00", "2008 every minute"
t25 = pl.read_csv(K.T5S / "2025" / "2025-04-07.csv")["date"].to_list()
assert t25[1][-8:] == "09:00:05", "the other days every 5 seconds"
has("X5 minute", "(2008 every minute)")
# 00631L, limited at 20%: TWSE's 10% times its multiple of 2 (lm02.md:498), and its fall stopped inside the limit
assert -0.20 - K.EPS < K.r631[K.EPOS["2025-04-07"]] < -0.1999
has("E9 00631L limit", "00631L, limited at 20%, fell 19.995%")
o8, c0 = K.o8, K.c0
assert (o8, c0) == (151.2, 176.0)
has("E9 lock", "0050 opened, peaked, bottomed and closed at 158.40, exactly 1/10 below 176.00, on 29,578,872 units")
assert v_ == 29_578_872
pc("E9 below the lock", o8 / 158.4 - 1, 2, "4.55")
pc("E9 below 2 April", o8 / c0 - 1, 2, "14.09")
pc("E9 00631L", K.r631[K.EPOS["2025-04-07"]], 3, "19.995")
pc("E9 00631L next", K.r631[K.EPOS["2025-04-08"]], 2, "11.20")
tx = K.lim.filter(pl.col("date") == "2025-04-07").row(0, named=True)
pc("E9 TX", tx["RF"], 2, "10.00")
pc("E9 TAIEX price", tx["RS"], 2, "-9.70")
chk("E9 TX volume", tx["volume"], ",d", "2,736")
tx24 = K.lim.filter(pl.col("date") == "2024-08-05").row(0, named=True)
chk("KC7 volume 2024", tx24["volume"], ",d", "211,207")
chk("KC7 volume 8 April", K.vol8, ",d", "152,423")
has("zh7", "0050 開在 151.20，比鎖住的價格再低 4.55%")

# ---------------------------------------------------------------- Section 8: leverage, ruin, margin (X7, E10, KC)
m41 = re.findall(r"2024-08-05 (R[35]) (-[\d.]+) \((\d{4}-\d\d-\d\d); last close ([+-][\d.]+)\)", K.OUT[40])
assert [x[0] for x in m41] == ["R3", "R5"] and all(x[2] == "2024-07-26" for x in m41)
chk("R3 low 2024", float(m41[0][1]), ".2f", "-1.40")
chk("R5 low 2024", float(m41[1][1]), ".2f", "-1.47")
chk("R3 end 2024", float(m41[0][3]), "+.2f", "+0.11")
chk("R5 end 2024", float(m41[1][3]), ".2f", "-0.07")
has("ruin over a window", "R3's and R5's 2024 books reach it on 26 July")
lw20, lw25 = FZ["2020"]["R6"], FZ["2025-04-07"]["R6"]
ld25 = float(K.expo("R6", "2025-04-02") @ W7)
chk("X7 R6 2020", -1 / lw20, ".2f", "7.67")
chk("X7 R6 2025", -1 / lw25, ".2f", "9.90")
chk("X7 R6 7 April", -1 / ld25, ".2f", "16.77")
chk("X7 0050 next open", -1 / K.xo, ".2f", "7.10")
has("X7 crossings", "The lines cross zero at 7.67, 9.90, 16.77 and 7.10")
pc("L = 5 at the lock", 5 * -0.10, 2, "50.00")
pc("L = 5 at the next open", 5 * K.xo, 2, "70.45")
chk("R8's cap", 1.5, ".1f", "1.5")
chk("R8's largest uncapped ratio (A31-29)", float(K.ratio.max()), ".2f", "2.14")
pc("X7 note R6 2020", lw20, 2, "13.04")
pc("X7 note R6 2025", lw25, 2, "10.10")
pc("X7 note R6 7 April", ld25, 3, "5.964")
pc("X7 note 0050", K.xo, 2, "14.09")
F26, notional = K.F26, K.notional
chk("E10 F", F26, ",.0f", "49,357")
chk("E10 notional", notional, ",.0f", "9,871,400")
assert notional == 200 * F26, "NT$200 a point (lm23.md:327)"
has("E10 multiplier", "NT\\$200 a point")
has("E10 margins", "sets the initial margin at NT\\$701,000 and the maintenance margin at NT\\$538,000")
chk("E10 f", notional / 701_000, ".2f", "14.08")
chk("E10 margin gap", 701_000 - 538_000, ",d", "163,000")
pc("E10 call fall", 163_000 / notional, 2, "1.65")
chk("E10 limit-day loss", 0.10 * notional, ",.0f", "987,140")
chk("E10 times equity", 0.10 * notional / 701_000, ".2f", "1.41")
chk("E10 equity", 701_000 - 0.10 * notional, ",.0f", "-286,140")
has("E10 from printed", "$f=9,871,400/701,000=14.08$, and a fall of $163,000/9,871,400=1.65%$")
has("zh8", "一口台指期是 14.08 倍，下跌 1.65% 就碰到維持保證金")
chk("KC8 R6's 2020 loss a unit", -lw20, ".5f", "0.13036")
chk("KC8 smallest ruin leverage", 1 / 0.13036, ".3f", "7.671")
chk("KC8 from the unrounded loss", -1 / lw20, ".3f", "7.671")
pc("KC8 R6 under the worst of each", float(CUR["R6"] @ K.woe), 2, "11.11")
assert 5 * float(CUR["R6"] @ K.woe) < -0.5, "more than half its wealth at L = 5"
assert -1 / lw20 < min(-1 / lw25, -1 / ld25), "2020's window is R6's smallest ruin leverage of 2020-2025"

# ---------------------------------------------------------------- Section 9: the four failures (X9), KC
RULEW = K.RULEW
fail_vals = {}
for k in ("R1", "R6", "R8"):
    pth = RULEW.filter(pl.col("rule") == k).sort("date")
    w = np.asarray(pth["wealth"].to_numpy(), dtype=np.float64)
    d0, d1 = pth["date"][0], pth["date"][-1]
    yrs = (date.fromisoformat(d1) - date.fromisoformat(d0)).days / 365.25
    path = np.concatenate([[1.0], w])
    fail_vals[k] = (math.log(w[-1]) / yrs, float((1 - path / np.maximum.accumulate(path)).max()),
                    float(np.maximum(0, 1 - w).max()))
row("X9 growth", ["Weak growth", "net log growth, % a year ([[LM34]])"] + [f"{100 * fail_vals[k][0]:.2f}"
                                                                      for k in ("R1", "R6", "R8")])
row("X9 MDD", ["Drawdown", "MDD, % ([[LM32]])"] + [f"{100 * fail_vals[k][1]:.2f}" for k in ("R1", "R6", "R8")])
row("X9 DD0", ["", "largest $\\mathrm{DD}^0_t$, % ([[LM32]])"] + [f"{100 * fail_vals[k][2]:.2f}"
                                                                 for k in ("R1", "R6", "R8")])
for k in ("R1", "R6", "R8"):
    for v in fail_vals[k]:
        assert not tie(100 * v, ".2f")
        COVERED.add(f"{100 * v:.2f}")
ruin_row = [-1 / FZ["2020"]["R1"], -1 / FZ["2020"]["R6"], -1 / (FZ["2020"]["R8"] / K.SCALE["2020"][0])]
row("X9 ruin", ["Ruin", "$L_{\\mathrm{ruin}}$ over 2020's window"] + [f"{x:.2f}" for x in ruin_row])
COVERED.update(f"{x:.2f}" for x in ruin_row)
chk("X9 R8 scale", K.SCALE["2020"][0], ".3f", "1.307")
# funding: R8's borrowing per unit of equity is its held exposure minus 1; the held exposure drifts between trades,
# to at most 1.53 on 22 August 2023 (lm31.md:335), above the cap of 1.5 that a trade sets
held = {k: K.BOOKS[k][1].sum(axis=1) for k in ("R1", "R6", "R8")}
assert held["R1"].max() <= 1 + 1e-12 and held["R6"].max() <= 1 + 1e-12, "R1 and R6 never borrow"
j8 = int(np.argmax(held["R8"]))
assert K.BOOKS["R8"][0][j8] == "2023-08-22" and f"{held['R8'][j8]:.2f}" == "1.53"
chk("X9 R8's largest borrowing", held["R8"][j8] - 1, ".2f", "0.53")
assert "to at most 1.53 on 22 August 2023" in (ROOT / "src" / "lm31.md").read_text(encoding="utf-8")
assert abs(K.vr.RF + K.vr.SPREAD - 0.035) < 1e-15, "the through case's borrowing rate, 3.5% (illustrative)"
row("X9 funding", ["Funding", "borrowing at an illustrative 3.5% a year", "none", "none", "up to 0.53"])
has("X9 note borrowing", "Borrowing is per unit of equity, at most 0.53 as R8's held exposure drifted above its cap to "
    "1.53 ([[LM31]]).")
has("X9 note ruin", "The ruin row is a hypothetical scaling of the 2020 replay.")
# KC section 9 (b): a hypothetical mandate stops a book whose DD0 reaches 10%; R1 meets it first in March 2020, while
# it grows fastest of the three, never borrows, and needs L >= 5.04 for ruin over 2020's window
p1 = RULEW.filter(pl.col("rule") == "R1").sort("date")
w1 = np.asarray(p1["wealth"].to_numpy(), dtype=np.float64)
first10 = p1["date"][int(np.argmax(1 - w1 >= 0.10))]
assert (1 - w1 >= 0.10).any() and first10.startswith("2020-03"), first10
assert fail_vals["R6"][2] < 0.10 and fail_vals["R8"][2] < 0.10, "only R1 meets the mandate"
assert fail_vals["R1"][0] > max(fail_vals["R6"][0], fail_vals["R8"][0]), "R1 grew fastest of the three"
has("KC9b question", "A hypothetical mandate stops a book whose $\\mathrm{DD}^0_t$ reaches 10%.")
has("KC9b answer", "That drawdown limit, in March 2020 (10.24%). R1 grew fastest of the three and borrowed nothing, "
    "and ruin over 2020's window needs $L\\ge5.04$.")
chk("KC9 worst-of-each distance", K.maha(K.woe), ".2f", "19.07")
chk("KC9 largest distance", float(K.dt.max()), ".2f", "15.02")

# ---------------------------------------------------------------- practice problems and solutions
chk("P1", 0.6 * -10 + 0.4 * 1.81, ".2f", "-5.28")
chk("P1 A", -10 + 1.81, ".2f", "-8.19")
chk("P1 C", 0.6 * -10, ".2f", "-6.00")
chk("P2", 1 / 0.08, ".1f", "12.5")
chk("P2 B", 8.0, ".1f", "8.0")
chk("P2 C", (1 - 0.08) / 0.08, ".1f", "11.5")
pc("P3", K.P3["open"], 2, "-56.36")
pc("P3 A", K.P3["close"], 2, "-40.00")
pc("P3 B", K.P3["lock"], 2, "-18.18")
chk("P4", 100 * (1.01 * 0.96 * 32.48 / 32.00 - 1), ".2f", "-1.59")
chk("P4 A", 100 * (1.01 * 0.96 - 1), ".2f", "-3.04")
chk("P4 C", 100 * (1.01 * 0.96 * 32.00 / 32.48 - 1), ".2f", "-4.47")
chk("P5", 10 / 0.8, ".1f", "12.5")
chk("P5 A", (10 / 0.8) ** 2, ".2f", "156.25")
chk("P5 B", math.sqrt(10 / 0.8), ".2f", "3.54")
keys = re.findall(r"^(\d+)\. \*\*([A-C])\*\* is correct", RAW, flags=re.MULTILINE)
assert keys == [("1", "B"), ("2", "A"), ("3", "C"), ("4", "B"), ("5", "C")], keys
chk("S6 bond normal", -0.07 * -10, "+.2f", "+0.70")
chk("S6 book normal", 0.4 * -10 + 0.6 * 0.70, ".2f", "-3.58")
chk("S6 0050 part", 0.4 * -10, ".2f", "-4.00")
chk("S6 bond part normal", 0.6 * 0.70, ".2f", "0.42")
chk("S6 bond break", 0.30 * -10, ".2f", "-3.00")
chk("S6 bond part break", 0.6 * -3.00, ".2f", "-1.80")
chk("S6 book break", 0.4 * -10 + 0.6 * -3.00, ".2f", "-5.80")
chk("S6 gap", -3.58 - -5.80, ".2f", "2.22")
S2 = np.array([[1.44, -0.1 * 1.2 * 0.8], [-0.1 * 1.2 * 0.8, 0.64]])
f2 = np.array([0.5, 0.5])
chk("S7 variance", float(f2 @ S2 @ f2), ".3f", "0.472")
chk("S7 covariance term", 0.1 * 1.2 * 0.8, ".3f", "0.096")
chk("S7 variance from printed", 0.25 * (1.44 + 0.64) - 0.5 * 0.096, ".3f", "0.472")
chk("S7 sigma_p", math.sqrt(0.472), ".4f", "0.6870")
chk("S7 d*", 5 / math.sqrt(0.472), ".2f", "7.28")
chk("S7 d* from printed", 5 / 0.6870, ".2f", "7.28")
sf = S2 @ f2
chks_sf = [f"{x:.3f}" for x in sf]
assert chks_sf == ["0.672", "0.272"]
has("S7 Sigma f", "$\\Sigma\\mathbf f=(0.672,0.272)^{\\top}$")
chk("S7 beta 1", float(sf[0] / 0.472), ".3f", "1.424")
chk("S7 beta 2", float(sf[1] / 0.472), ".3f", "0.576")
chk("S7 shock 1", -5 * float(sf[0] / 0.472), ".2f", "-7.12")
chk("S7 shock 2", -5 * float(sf[1] / 0.472), ".2f", "-2.88")
has("S7 (27.5)", "so by (27.5) the betas $\\beta_{i,p}=(\\Sigma\\mathbf f)_i/\\sigma_p^2$ are 1.424 and 0.576. With mean "
    "0, (35.4) gives the shock $-\\ell\\beta_{i,p}$: −7.12% and −2.88%.")
has("P8 pairs", "The correlations are −0.105 (0050–00679B), 0.092 (0050–00642U) and −0.18 (00679B–00642U)")
assert re.search(r"A35-56 .*x\* -7\.11864 / -2\.88136", K.OUT[55])
chk("P8 0050-00642U (A27-11)", float(K.S[0, 4] / sd[0] / sd[4]), ".3f", "0.092")
chk("P8 00679B-00642U (A27-11)", float(K.S[2, 4] / sd[2] / sd[4]), ".2f", "-0.18")
chk("S8 eigenvalue", K.lam3, ".3f", "0.819")
chk("S8 eigenvalue at 0.30", K.lam3b, ".3f", "0.605")
pc("P8 mean 0050", float(MU[0]), 4, "0.0995")
pc("P8 mean 00679B", float(MU[2]), 4, "-0.0040")
pc("P8 SD 0050", float(sd[0]), 4, "1.2898")
pc("P8 SD 00679B", float(sd[2]), 4, "0.8657")
chk("S8 move", -0.0040 + 0.105 * (0.8657 / 1.2898) * 10.0995, "+.2f", "+0.71")
chk("S8 move at 0.30", -0.0040 - 0.30 * (0.8657 / 1.2898) * 10.0995, ".2f", "-2.04")
chk("S8 10 + mean", 10 + 0.0995, ".4f", "10.0995")
pc("S10 R6 frozen", FZ["2020"]["R6"], 2, "13.04")
pc("S10 R6 path", AC["2020"]["R6"], 2, "14.43")
ef6 = K.TRADE_EFFECT_2020["R6"]
assert [d for d, *_ in ef6] == ["2020-02-03", "2020-03-02"]
for d, dl, gt, eff in ef6:
    bought = [FUNDS[j] for j in range(5) if dl[j] > 0]
    assert bought == ["0050", "00646", "00642U"], (d, bought)
    assert all(-0.405 < gt[j] < -0.215 for j in (0, 1, 4)), (d, gt)
assert round(-100 * min(min(gt[j] for j in (0, 1, 4)) for _, _, gt, _ in ef6)) == 40
assert round(-100 * max(max(gt[j] for j in (0, 1, 4)) for _, _, gt, _ in ef6)) == 22
pc("S10 R6 effect 3 Feb", ef6[0][3], 2, "0.90")
pc("S10 R6 effect 2 Mar", ef6[1][3], 2, "0.47")
gap6 = AC["2020"]["R6"] - FZ["2020"]["R6"]
assert abs(ef6[0][3] + ef6[1][3] - gap6) < 0.0005, "nearly the gap"
assert abs(AC["2020"]["R6"] - K.R6_GROSS_2020) < 0.0003, "costs take about 0.02 points"
ef8 = K.TRADE_EFFECT_2020["R8"]
pc("S10 R8 effect 3 Feb", ef8[0][3], 2, "3.41")
pc("S10 R8 effect 2 Mar", ef8[1][3], 2, "1.10")
has("S10 R8", "R8's trades cut its exposure to 0.991 and 0.884 and saved 3.41 and 1.10 points, nearly the gap between "
    "17.04% frozen and 12.58% on its path")
gap8 = AC["2020"]["R8"] - FZ["2020"]["R8"]
assert abs(ef8[0][3] + ef8[1][3] - gap8) < 0.001, "nearly the gap (interest, costs and the approximation)"
assert f"{3.41 + 1.10:.2f}" == "4.51" and f"{17.04 - 12.58:.2f}" == "4.46", "printed parts: nearly, not exactly"
p20, t20, _ = WIN["2020"]
assert (p20, t20) == ("2020-01-14", "2020-03-19")
has("S10 window", "The 2020 window runs from TR23's peak of 14 January to its trough of 19 March ([[ex:windows]]).")
has("S10 recipe", "Each trade's change of exposures, times each fund's return from the trade to the trough, lost 0.90 "
    "and 0.47 points, nearly the gap.")
# the recipe, recomputed here: sum over funds of (exposure after - drifted exposure before) times the fund's return
# from the trade's close to the trough
for k, eff in (("R6", ef6), ("R8", ef8)):
    for d, dl, gt, e_ in eff:
        assert abs(float(np.asarray(dl) @ np.asarray(gt)) - e_) < 1e-12, (k, d)
chk("S11 d", db2, ".2f", "17.01")
pc("S11 00679B", xb2[2], 2, "-9.89")
chk("S12 f", notional / K.EQ12, ".2f", "7.04")
chk("S12 margin gap", K.EQ12 - 538_000, ",d", "864,000")
pc("S12 call", K.P12["call"], 2, "8.75")
chk("S12 after a limit day", K.P12["after"], ",.0f", "414,860")
assert 0 < K.P12["after"] < 538_000
pc("S12 ruin fall", K.P12["ruin"], 2, "14.20")
has("P12 equity", "equity of NT\\$1,402,000, twice the initial margin")
assert K.EQ12 == 1_402_000

# ---------------------------------------------------------------- the overview
has("overview: case", "TR23 fell 9.70%, its worst day since 2003. The through case's eight rules lost from 5.06% (R7) "
    "to 8.33% (R4).")
has("overview: windows", "cost TR23 from 18.31% (2024) to 56.02% (2008)")
has("overview: R8", "In 2020 R8 lost 17.04% frozen and 12.58% on its own path. In 2025 it lost 10.15% frozen and "
    "13.84% on its path, after a trade raised its exposure to 1.319.")
has("overview: beta", "gives R1 a loss of 3.62% on 7 April 2025, under half the actual 7.70%")
has("overview: reverse", "R8's current book needs only 12.27, below the 12.94 of 7 April 2025")
has("overview: lock", "opened 4.55% lower the next day. A book of 0050 levered five times lost 50.00% at the lock and "
    "70.45% by the next open.")
has("overview: TX", "levered 14.08 times. A fall of 1.65% reaches the maintenance margin, and a 10% limit day leaves "
    "equity of NT$−286,140.")

# ====================================================================== part 3: code, charts and the lab's reference
# The module's Python block, run on R2's book (percent units, the full estimation frame's moments)
block = re.search(r"```python\n(.*?)```", RAW, flags=re.DOTALL)
assert block
code = block.group(1)
assert max(len(line) for line in code.splitlines()) <= 80, "code lines at most 80 characters"
ns_: dict[str, object] = {"f": CUR["R2"], "S": 1e4 * S, "Rbar": 100 * MU, "loss": 10.0}
printed: list[tuple[float, float]] = []
ns_["print"] = lambda d_, r_: printed.append((float(d_), float(r_)))
exec(compile(code, "lm35.md python block", "exec"), ns_)  # noqa: S102 (the module's own printed code block)
d_code, res_code = printed[0]
assert abs(d_code - db2) < 1e-6 and res_code < 1e-9, (d_code, res_code)
assert abs(float(np.asarray(ns_["d_closed"])) - (10 + 100 * float(CUR["R2"] @ MU)) / (100 * math.sqrt(
    float(CUR["R2"] @ S @ CUR["R2"])))) < 1e-12
print(f"CHECK python block: d {d_code:.5f} (bounded, R2), KKT residual {res_code:.1e}")
N_CHECKS += 1

# the chart files against the text
CH = ROOT / "src" / "data"
spec = json.loads((CH / "lm35-windows.json").read_text(encoding="utf-8"))
assert f"{100 * spec['series'][3]['values'][0]:.2f}" == "-56.02"
spec = json.loads((CH / "lm35-replay.json").read_text(encoding="utf-8"))
assert [f"{100 * v:.2f}" for v in spec["series"][0]["values"]] == ["-19.84", "-5.84", "-12.97"]
spec = json.loads((CH / "lm35-attrib.json").read_text(encoding="utf-8"))
tot = [sum(s["values"][c] for s in spec["series"]) for c in range(4)]
assert [f"{-100 * t:.2f}" for t in tot] == ["7.70", "5.40", "5.96", "7.94"]
spec = json.loads((CH / "lm35-ruin.json").read_text(encoding="utf-8"))
assert [p["label"] for p in spec["ann"] if p["type"] == "point"] == ["7.67", "9.90", "16.77", "7.10"]
assert [a.get("label") for a in spec["ann"] if a["type"] == "vline"] == [None, "R8: cap 1.5, ratio 2.14"]
wid = json.loads((CH / "lm35-builder.json").read_text(encoding="utf-8"))["widget"]
assert len(wid["dist"]) == 2362 and wid["init"] == {"rule": "R1", "preset": "day0407", "L": 1.0}
assert np.allclose(wid["presets"]["day0407"]["x"], W7, atol=0, rtol=0)
assert f"{sum(wid['books']['R8']):.2f}" == "1.36"
for wk, wn in (("win2020", "2020"), ("win2024", "2024-08-05"), ("win2025", "2025-04-07")):
    assert set(wid["presets"][wk]["low"]) == set(RULES), wk
    a_, b_, _ = WIN[wn]
    pth = np.cumprod(1 + fr.W[K.WIDX[a_] + 1:K.WIDX[b_] + 1], axis=0) - 1
    for k in RULES:                                # (35.2) over a window: the lowest value on the window's dates
        assert abs(wid["presets"][wk]["low"][k] - float((pth @ (CUR[k] / CUR[k].sum())).min())) < 1e-15, (wk, k)
print("CHECK chart files: windows, replay, attrib totals, ruin crossings, widget block")
N_CHECKS += 1

# the lab checkpoint's reference answers (build/make_lab35.py's REF block) against the computation here
cpt = K.checkpoint()
src_lab = LAB.read_text(encoding="utf-8")
mref = re.search(r"^REF = (\{.*?^\})$", src_lab, flags=re.DOTALL | re.MULTILINE)
assert mref, "build/make_lab35.py has no REF block"
REF = ast.literal_eval(mref.group(1))


def refv(key: str, value: float, fmt: str) -> None:
    global N_CHECKS
    got = format(value, fmt)
    assert REF[key] == got, (key, REF[key], got)
    assert not tie(value, fmt), ("rounding tie in the lab's reference", key, value)
    N_CHECKS += 1


nsig = cpt["signals"]
assert isinstance(nsig, int)
refv("signals", nsig, "d")
assert REF["first"] == cpt["first"]
for k in K.CP_RULES:
    rk = cpt[k]
    assert isinstance(rk, dict)
    refv(f"{k} cut", rk["cut"], "d")
    refv(f"{k} growth", 100 * rk["growth"], ".2f")
    refv(f"{k} sr", rk["sr"], ".2f")
    refv(f"{k} se", rk["se"], ".2f")
    refv(f"{k} lo", rk["sr"] - 1.96 * rk["se"], ".2f")
    refv(f"{k} hi", rk["sr"] + 1.96 * rk["se"], ".2f")
    refv(f"{k} mdd", 100 * rk["mdd"], ".2f")
    refv(f"{k} turnover", rk["turnover"], ".3f")
    refv(f"{k} costs", 100 * rk["costs"], ".3f")
    refv(f"{k} low", 100 * (rk["low"] - 1), ".2f")
    for n in ("2024-08-05", "2025-04-07"):
        for kind in ("frozen", "actual", "named"):
            refv(f"{k} {kind} {n}", 100 * rk[f"{kind} {n}"], ".2f")
    refv(f"{k} first 2020", 100 * rk["first 2020"], ".2f")
    refv(f"{k} d", rk["d"], ".2f")
    assert REF[f"{k} active"] == rk["active"], (k, rk["active"])
r1c = cpt["R1"]
assert isinstance(r1c, dict)
refv("lag", r1c["lag"], "d")
refv("T", r1c["T"], ",d")
r3 = cpt["R3 last"]
assert isinstance(r3, dict)
assert REF["R3 last trade"] == r3["trade"]
for j, s in enumerate(K.fc.funds):
    refv(f"R3 w {s}", float(r3["w"][j]), ".4f")
    refv(f"R3 uncapped {s}", float(r3["uncapped"][j]), ".4f")
assert REF["R3 caps"] == [s for j, s in enumerate(K.fc.funds) if r3["caps"][j] > 0]
assert REF["R3 floors"] == [s for j, s in enumerate(K.fc.funds) if r3["floors"][j] > 0]
binds = cpt["R3 cap binds"]
assert isinstance(binds, int)
refv("R3 cap binds", binds, "d")
e8 = cpt["R8 exposure"]
assert isinstance(e8, dict)
for key in ("min", "mean", "uncapped max"):
    refv(f"R8 {key}", e8[key], ".3f")
refv("R8 at cap", e8["at cap"], "d")
print(f"CHECK lab checkpoint: REF block of build/make_lab35.py equals the computation ({len(REF)} entries); "
      f"recursion against vol5_rules.wealth_path {cpt['check']:.0e}, E5 targets {cpt['targets']:.0e}")

# ====================================================================== structure: labels, tags and citations
ex_labels = re.findall(r"\[!exhibit\][^\n]*\{#([\w-]+)\}", RAW)
eg_labels = re.findall(r"\[!example\][^\n]*\{#([\w-]+)\}", RAW)
assert len(ex_labels) == 9 and len(eg_labels) == 10, (ex_labels, eg_labels)
assert len(set(ex_labels) | set(eg_labels)) == 19, "a label is used twice"
for lab in ex_labels:
    assert f"[[ex:{lab}]]" in RAW, f"exhibit {lab} is never cited"
for kind, lab in re.findall(r"\[\[(ex|eg):([\w-]+)\]\]", RAW):
    assert lab in (ex_labels if kind == "ex" else eg_labels), (kind, lab)
tags = re.findall(r"\\tag\{(35\.\d+)\}", RAW)
assert sorted(tags) == [f"35.{k}" for k in range(1, 6)], tags
for name in re.findall(r'data-chart="(lm35-[\w-]+)"', RAW):
    assert (CH / f"{name}.json").exists(), name
assert len(re.findall(r"^> \[!kc\]", RAW, flags=re.MULTILINE)) == 8
fm = RAW.split("\n---", 1)[0]
mpre = re.search(r"prereq: \[([^\]]*)\]", fm)
assert mpre
prereq = [int(x) for x in mpre.group(1).split(",")]
for m_ in prereq:
    assert f"[[LM{m_}]]" in RAW or f"[[LM{m_}|" in RAW, f"prerequisite LM{m_} is never cited"
print(f"labels: {len(ex_labels)} exhibits, {len(eg_labels)} examples, tags (35.1)-(35.5), every exhibit cited, every "
      "prerequisite cited")

# ====================================================================== report
body = TEXT.split("\n## Glossary", 1)[0]
nums = set(re.findall(r"(?<![\w.])\d+\.\d+|(?<![\w.,])\d{1,3}(?:,\d{3})+", body))
left = sorted(n for n in nums if n not in COVERED)
print(f"\nnumbers with a decimal point or thousands separator not covered by a check ({len(left)}):")
print("   " + " ".join(left))
print(f"anchor differences ({len(ANCHOR_DIFFS)}):")
for a_ in ANCHOR_DIFFS:
    print("   ", a_)
print(f"\nall {N_CHECKS} checks passed")
sys.exit(0)
