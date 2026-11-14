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

Part 2 checks the text (each check stops the script on a failure). The text is the module's body: everything after the
front matter and before the Glossary (the References follow it). The front matter's overview bullets are checked
whole, against the front matter only (has_fm); its other fields hold no computed number.
  chk(label, value, fmt, printed, n)  format(value, fmt) equals the printed string (minus signs as "-"), the value is
                                   not a rounding tie of that format, and the printed string occurs in the body as a
                                   whole number: exactly n times, or at least once when n is None. Hand computations
                                   are redone from the printed, rounded inputs (PITFALLS section 7); a proxy value
                                   printed at 0 dp is checked against A35's CENT flag.
  pc(label, frac, d, printed, loss=, n=)  a return in percent: printed with its sign, or unsigned with loss=True (the
                                   return is negative: the text says lost, fell or a drawdown) or loss=False (positive).
  has(label, text, n)              a literal string (a phrase, a table row) occurs in the body (n times, or at least
                                   once); every number in it counts as covered.
  pin(token, n, why)               a number covered by has() literals occurs exactly n times (dates, small integers).
The numbers of the body are tokens (tokens() below): a minus sign belongs to its number, so an unsigned printed value
never matches a signed occurrence; a plus sign belongs to its number where it is a sign (after a space, "(", "=" or
"|"), not where it is an operator; dates ("7 April 2025", "29 Oct 2007", "March 2020") and times ("09:01:00") are one
token each. At the end the script asserts that every covered token printed more than once carries its exact count
(from chk/pc's n or pin), and that the tokens no check covers equal ALLOW, an explicit list with counts and reasons;
so a one-digit change at any occurrence fails. Then it prints "all N checks passed".
Part 3 runs the module's Python block on R2's book, checks the chart files against the text, and checks the lab
checkpoint's reference answers that build/make_lab35.py prints (its REF block) against data/lm35_common.checkpoint().
"""
import ast
import math
import re
import sys
from collections import Counter
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
    plain, and a space after a TeX command that runs into a number (\\times10.10)."""
    s = s.replace("{,}", ",").replace("\\%", "%").replace("\\$", "$").replace("\u2212", "-").replace("\\,", "")
    s = re.sub(r"\\text\{\s*([^}]*)\}", r" \1", s)
    return re.sub(r"(\\[A-Za-z]+)(?=[\d.\-])", r"\1 ", s)


_FM_END = RAW.index("\n---\n", 4) + 5
FM = norm_text(RAW[:_FM_END])                                   # the front matter
BODY = norm_text(RAW[_FM_END:].split("\n## Glossary", 1)[0])    # the text every check searches
_MONTHS = ("January|February|March|April|May|June|July|August|September|October|November|December|"
           "Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec")
TOKEN = re.compile(
    rf"(?<![\w.])\d{{1,2}} (?:{_MONTHS})(?: \d{{4}})?(?![\w])"   # a date: 7 April 2025, 29 Oct 2007, 7 April
    rf"|(?<![\w.])(?:{_MONTHS}) \d{{4}}(?![\w])"                 # a month: March 2020
    r"|(?<![\w.:])\d\d:\d\d(?::\d\d)?(?![\w:])"                  # a time: 09:01:00
    # a number: its minus always, its plus where it is a sign; fund codes (0050, 00646) are not numbers
    r"|(?:(?<![^\s(=|])\+|(?<![.])-|(?<![\w.\-−]))(?!0\d)(?:\d{1,3}(?:,\d{3})+(?!\d)|\d+(?:\.\d+)?)(?![\w])"
)


def tokens(s: str) -> list[str]:
    return TOKEN.findall(s)


TOK = Counter(tokens(BODY))
N_CHECKS = 0
COVERED: set[str] = set()          # tokens of the body that a check verifies
PINNED: dict[str, int] = {}        # tokens with their exact count in the body
ANCHOR_DIFFS: list[str] = []


def occ(printed: str) -> int:
    """How often the printed number occurs in the body as a whole token: 0.33 is not inside 0.331, and, by TOKEN's
    lookbehind (?<![\\w.\\-−]), an unsigned 0.33 is not inside -0.33 (U+2212 is normalized to '-')."""
    assert tokens(printed) == [printed], ("not one token", printed)
    return TOK[printed]


def count(label: str, printed: str, n: int | None) -> None:
    """The printed number occurs n times in the body (at least once when n is None); it counts as covered."""
    k = occ(printed)
    if n is None:
        assert k >= 1, f"{label}: {printed!r} not found in src/lm35.md"
    else:
        assert k == n, f"{label}: {printed!r} occurs {k} times in src/lm35.md, not {n}"
        assert PINNED.get(printed, n) == n, (label, printed, "two counts")
        PINNED[printed] = n
    COVERED.add(printed)


def pin(printed: str, n: int, why: str) -> None:
    """A number that has() literals cover, printed n times (why: what the occurrences are)."""
    assert why and printed in COVERED, (printed, "pin a covered number")
    count(f"pin ({why})", printed, n)


def tie(value: float, fmt: str) -> bool:
    m = re.search(r"\.(\d+)", fmt)
    d = int(m.group(1)) if m else 0
    scaled = abs(value) * 10**d
    return abs(scaled - math.floor(scaled) - 0.5) < 1e-9


def chk(label: str, value: float, fmt: str, printed: str, in_md: bool = True, n: int | None = None) -> None:
    global N_CHECKS
    got = format(value, fmt)
    print(f"CHECK {label}: {got} (printed {printed})")
    assert got == printed, (label, got, printed)
    assert not tie(value, fmt), ("rounding tie: print more digits", label, value)
    if in_md:
        count(label, printed, n)
    else:
        assert n is None, (label, "a value not printed has no count")
    N_CHECKS += 1


def pc(label: str, frac: float, d: int, printed: str, *, loss: bool | None = None, in_md: bool = True,
       n: int | None = None) -> None:
    """A return printed in percent at d decimals: with its sign as the module prints it, or unsigned, with loss=True
    for a negative return printed as a loss (lost, fell, a drawdown) or loss=False for a positive one."""
    if printed[0] in "+-":
        assert loss is None, (label, "a signed printed value carries its own sign")
        chk(label, 100 * frac, f"{'+' if printed[0] == '+' else ''}.{d}f", printed, in_md, n)
    else:
        assert loss is not None, (label, "an unsigned printed value needs loss=True or loss=False")
        assert (frac < 0 if loss else frac > 0), (label, frac, "the wrong sign for the text")
        chk(label, -100 * frac if loss else 100 * frac, f".{d}f", printed, in_md, n)


def pcs(label: str, fracs: list[float] | np.ndarray, d: int, printed: list[str],
        n: list[int | None] | None = None) -> None:
    """Signed returns in percent; n gives each one's count."""
    for k, (v, p) in enumerate(zip(fracs, printed, strict=True)):
        pc(f"{label} [{k + 1}]", float(v), d, p, n=None if n is None else n[k])


def has(label: str, text: str, n: int | None = None, where: str = "body") -> None:
    global N_CHECKS
    t = norm_text(text)
    src = BODY if where == "body" else FM
    k = src.count(t)
    assert k >= 1, f"{label}: {text!r} not found in the {where} of src/lm35.md"
    assert n is None or k == n, f"{label}: {text!r} occurs {k} times in the {where}, not {n}"
    print(f"CHECK {label}: '{text[:80]}' in the {where}")
    if where == "body":
        COVERED.update(tokens(t))
    N_CHECKS += 1


def has_fm(label: str, text: str) -> None:
    """A whole overview bullet of the front matter."""
    has(label, f'  - "{text}"\n', 1, where="front matter")


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


def row(label: str, cells: list[str], n: int | None = None) -> None:
    """A table row of the module, as printed (an empty cell is '| |')."""
    has(label, "|" + "|".join(f" {c} " if c else " " for c in cells) + "|", n)


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
chk("T", len(fr.est_dates), ",d", "2,362", n=6)
assert (fr.est_dates[0], fr.est_dates[-1], fr.base) == ("2017-01-18", "2026-10-08", "2017-01-17")
has("estimation dates", "joint returns from 18 January 2017 to 8 October 2026")
chk("A", fr.A, ".2f", "242.95")
chk("wealth sessions", len(WD), ",d", "2,368")
chk("years", fr.years, ".2f", "9.72")
has("years from", "over 9.72 years from the close of 17 January 2017")
chk("A_w", fr.A_wealth, ".2f", "243.57")
chk("TR23 returns", int(np.isfinite(RT).sum()), ",d", "5,849", n=4)

# ---------------------------------------------------------------- the case and X1
pc("TR23 on 7 April 2025 (lm26.md:32)", RT[TPOS["2025-04-07"]], 2, "9.70", loss=True, n=2)
assert int((RT[np.isfinite(RT)] < RT[TPOS["2025-04-07"]] - K.EPS).sum()) == 0, "7 April 2025 is TR23's worst day"
assert TD[TPOS["2025-04-07"] - 1] == "2025-04-02"
assert (date(2025, 4, 7) - date(2025, 4, 2)).days == 5
has("case: the closure", "After its close on 2 April 2025, Taiwan's market did not trade again until 7 April")
pc("worst 5 sessions 2025", WORST["2025-04-07"][5][0], 2, "15.96", loss=True, n=2)
pc("worst 5 sessions 2020", WORST["2020"][5][0], 2, "16.51", loss=True)
assert TD[WORST["2025-04-07"][5][1]] == "2025-04-09" and TD[WORST["2025-04-07"][5][1] - 5] == "2025-03-31"
mr = re.search(r"5 sessions \(5845 spans\): 2020's worst [^|]* rank 1; 2025-04-07's worst [^|]* rank 2", K.OUT[57])
assert mr, "A35-58: 2025's worst five sessions rank 2, behind 2020's"
o, h_, lo_, c_, v_ = K.row["2025-04-07"]
assert o == h_ == lo_ == c_ == 158.4 and K.exact == K.Fraction(-1, 10)
has("case: one price", "0050 traded at one price all day, 158.40, exactly 10% below its last close")
chk("0050 volume, millions", v_ / 1e6, ".1f", "29.6")
pcs("X1 returns", W7, 2, ["-10.00", "-12.59", "+1.81", "-3.10", "-14.62"], n=[5, 3, 2, 1, 2])
pc("case 00646", W7[1], 2, "12.59", loss=True, n=2)
pc("case 00642U", W7[4], 2, "14.62", loss=True)
pc("case R7", day7["R7"], 2, "5.06", loss=True, n=2)
pc("case R4", day7["R4"], 2, "8.33", loss=True, n=2)
assert min(day7.values()) == day7["R4"] and max(day7.values()) == day7["R7"] and max(day7.values()) < 0
chk("R8 after the 3 March trade", float(K.expo("R8", "2025-03-03").sum()), ".3f", "1.319", n=4)
pc("case R8 (named-day replay)", day7["R8"], 2, "7.94", loss=True, n=2)
pc("case R8 (wealth, with interest)", net7["R8"], 2, "7.94", loss=True, in_md=False)
pred = K.pred
pc("case R1 beta model", float(K.expo("R1", "2025-04-02") @ pred), 2, "3.62", loss=True, n=2)
pc("case R1 actual", day7["R1"], 2, "7.70", loss=True, n=4)
assert float(K.expo("R1", "2025-04-02") @ pred) / day7["R1"] < 0.5, "under half"
has("case box: the five sessions", "Its five sessions to 9 April lost 15.96%, second only to March 2020's 16.51%.")
has("case box: the rules", "The through case's eight rules lost from 5.06% (R7) to 8.33% (R4). R8 had raised its "
    "exposure to 1.319 at its trade of 3 March, and it lost 7.94%. A beta model fitted on 2,362 days, that day "
    "included, gives R1 3.62%, under half the actual 7.70%.", 1)
has("case box: no limit", "00646 and 00642U have no daily limit, and they fell 12.59% and 14.62% ([[ex:case]]).", 1)
beta, r2 = K.beta, K.r2
for j, (p_, n_) in enumerate(zip(["1.048", "0.527", "-0.071", "0.161", "0.198"], [2, 2, 1, 1, 1], strict=True)):
    chk(f"beta {FUNDS[j]}", float(beta[j]), ".3f", p_, n=n_)
pcs("X1 beta x TR23", pred, 2, ["-10.17", "-5.11", "+0.69", "-1.56", "-1.92"], n=[2, 1, 2, 1, 4])
for j, (b_, p_) in enumerate(zip([1.048, 0.527, -0.071, 0.161, 0.198], ["-10.17", "-5.11", "+0.69", "-1.56", "-1.92"],
                                 strict=True)):
    assert f"{b_ * -9.70:+.2f}" == p_, ("X1 from the printed beta and -9.70", FUNDS[j])
X1_MARKET = {"0050": ("TWSE", "10%"), "00646": ("TWSE", "none"), "00679B": ("TPEx", "none"),
             "00635U": ("TWSE", "none"), "00642U": ("TWSE", "none")}
for j, s in enumerate(FUNDS):           # every fund's row of [[ex:case]], from the computed values
    row(f"X1 {s}", [s, *X1_MARKET[s], s2(W7[j]).replace("-", "−"), f"{beta[j]:.3f}".replace("-", "−"),
                    s2(pred[j]).replace("-", "−")], 1)
row("X1 R1", ["R1's book", "", "", s2(day7["R1"]).replace("-", "−"), "",
              s2(float(K.expo("R1", "2025-04-02") @ pred)).replace("-", "−")], 1)
row("X1 rules", ["Loss, %"] + [f"{-100 * day7[k]:.2f}" for k in RULES], 1)
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
chk("break correlation", K.RHO_BRK, ".2f", "0.30", n=3)

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
    row(f"X2 losses {sn}", [sn] + [f"{100 * x:.2f}".replace("-", "−") for x in vals], 1)
    for k, x in enumerate(vals):
        assert not tie(100 * x, ".2f") and x < 0, (n, k)
assert ranks == {"2008": 4, "2015": 17, "2020": 8, "2024-08-05": 2, "2025-04-07": 1}
has("X2: 2024's 20 sessions", "2024's worst 20 sessions start before its peak, at the close of 4 July")
assert TD[WORST["2024-08-05"][20][1] - 20] == "2024-07-04" and "2024-07-04" < WIN["2024-08-05"][0]
has("X2: the limit history", "TWSE's stock limit was 7% until 1 June 2015")
pc("2008 peak to trough", LV[TPOS[WIN["2008"][1]]] / LV[TPOS[WIN["2008"][0]]] - 1, 2, "56.02", loss=True)
pc("2024 peak to trough", LV[TPOS[WIN["2024-08-05"][1]]] / LV[TPOS[WIN["2024-08-05"][0]]] - 1, 2, "18.31", loss=True)
p25, t25, nd25 = WIN["2025-04-07"]
assert (p25, t25, nd25) == ("2025-02-21", "2025-04-09", "2025-04-07") and TPOS[t25] - TPOS[p25] == 30
has("E1 window", "TR23 peaked on 21 February 2025 and bottomed 30 sessions later, on 9 April, 26.54% lower")
pc("E1 peak to trough", LV[TPOS[t25]] / LV[TPOS[p25]] - 1, 2, "26.54", loss=True)
has("E1 worst day", "Its worst day, 7 April, lost 9.70% ([[LM26]]), five calendar days after 2 April")
assert TD[WORST["2025-04-07"][20][1] - 20] == "2025-03-10"
has("E1 spans", "The worst 5 sessions, from the close of 31 March, lose 15.96%, and the worst 20, from the close of "
    "10 March, 22.38%")
pc("E1 worst 20", WORST["2025-04-07"][20][0], 2, "22.38", loss=True)
chk("five-session spans", len(LV) - 5, ",d", "5,845")
has("E1 rank", "only one, ending 19 March 2020, lost more")
k24, k25 = TPOS["2024-08-05"], TPOS["2025-04-09"]
pk = int(np.argmax(LV[:k25 + 1]))
assert TD[pk] == "2024-07-11" and k25 - pk == 176
has("E1 running peak", "from the running peak, 11 July 2024: 27.72% on 9 April 2025, 176 sessions later, and 18.31% "
    "on 5 August 2024")
pc("E1 DD 2025", LV[k25] / LV[:k25 + 1].max() - 1, 2, "27.72", loss=True)
pc("E1 DD 2024", LV[k24] / LV[:k24 + 1].max() - 1, 2, "18.31", loss=True)
gaps = np.array([(date.fromisoformat(TD[i]) - date.fromisoformat(TD[i - 1])).days for i in range(1, len(TD))])
long_ = gaps >= 4
r1_ = RT[1:]
chk("spans >= 4 days", int(long_.sum()), "d", "140", n=2)
pc("their share (not printed)", float(long_.mean()), 1, "2.4", loss=False, in_md=False)
pc("their mean |R|", float(np.abs(r1_[long_]).mean()), 2, "1.39", loss=False)
pc("the rest", float(np.abs(r1_[~long_]).mean()), 2, "0.83", loss=False)
has("pitfall spans", "Of TR23's 5,849 returns, 140 span four or more calendar days")
has("KC2 answer", "Compare it with the 140 returns that span four or more days, 1.39% in mean absolute size, not with "
    "the rest (0.83%)")
has("pitfall closure", "and 30 January 2020 the Lunar New Year closure of 21 to 29 January (TWSE's 2020 schedule)")
has("KC question", "TR23's worst day in the 2020 window, 30 January 2020, lost 5.75%")
has("pitfall 7 April", "7 April 2025 followed four days without trading")
pc("KC 2020-01-30", RT[TPOS["2020-01-30"]], 2, "5.75", loss=True)
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
        row(f"X3 {sn} {lab}", [f"{sn}, {lab}"] + [s2(src[k]).replace("-", "−") for k in RULES], 1)
        for k in RULES:
            assert not tie(100 * src[k], ".2f"), (n, lab, k)
# the named-day replay of 7 April 2025 against the stored wealth paths (vol5_rules' output, not the rebuilt books): no
# rule trades that day, so each wealth ratio is the replay plus one session's interest on the cash (R8 borrows)
for k in RULES:
    pth_ = K.RULEW.filter(pl.col("rule") == k)
    wr = dict(zip(pth_["date"].to_list(), pth_["wealth"].to_list(), strict=True))
    e_ = K.expo(k, "2025-04-02")
    cash = 1 - float(e_.sum())
    rate = (K.RF if cash >= 0 else K.RF + K.SPREAD) / fr.A_wealth
    assert abs(named["2025-04-07"][k] + cash * rate - (wr["2025-04-07"] / wr["2025-04-02"] - 1)) < 1e-12, k
    assert (abs(cash) < 1e-12) == (k != "R8"), (k, "R1-R7 hold no cash")
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
chk("X4 R6 two-decimal sum", sum(float(g) for g in r6_2), ".2f", "-5.95", n=2)
pc("X4 R6 total", day7["R6"], 2, "-5.96", n=2)
pcs("X4 R6 three decimals", P14["R6"], 3, ["-1.351", "-2.733", "+0.556", "-0.684", "-1.752"])
chk("X4 R6 three-decimal sum", sum(float(f"{100 * x:.3f}") for x in P14["R6"]), ".3f", "-5.964")
pc("X4 R6 total, 3 dp", day7["R6"], 3, "-5.964")
assert K.R1_LAST_TRADE_0402 == "2025-04-01" and np.abs(K.E_R1_0402 - 0.2).max() < 0.002
has("E2 trade", "After its trade of 1 April, R1's exposures on 2 April are near 0.2")
pcs("E2 parts", P14["R1"], 2, ["-2.00", "-2.53", "+0.36", "-0.62", "-2.91"], n=[2, 2, 2, 2, 2])
pc("E2 R3", day7["R3"], 2, "5.40", loss=True, n=2)
pc("E2 R3 from 00646", P14["R3"][1], 2, "4.07", loss=True)
pc("E3 R8 frozen 2020", FZ["2020"]["R8"], 2, "17.04", loss=True, n=2)
pc("E3 R8 path 2020", AC["2020"]["R8"], 2, "12.58", loss=True, n=2)
assert WIN["2020"][0] == "2020-01-14" and [d for d, *_ in K.TRADE_EFFECT_2020["R8"]] == ["2020-02-03", "2020-03-02"]
has("E3 frozen at", "Frozen at 14 January 2020, R8 loses 17.04%, but its path lost 12.58%. Its trades of 3 February "
    "and 2 March cut its exposure from 1.307 to 0.991", 1)
r8 = {d: (float(K.PRE["R8"][d].sum()), float(K.expo("R8", d).sum())) for d in K.PRE["R8"]}
chk("E3 R8 entry", float(K.expo("R8", WIN["2020"][0]).sum()), ".3f", "1.307", n=2)
chk("E3 R8 3 February", r8["2020-02-03"][1], ".3f", "0.991", n=2)
chk("E3 R8 2 March (A31-33)", r8["2020-03-02"][1], ".3f", "0.884", n=2)
g20 = K.growth(*WIN["2020"][:2])
pc("E3 book of 3 February", float(K.expo("R8", "2020-02-03") @ g20), 2, "13.20", loss=True)
pc("E3 book of 2 March", float(K.expo("R8", "2020-03-02") @ g20), 2, "11.68", loss=True)
has("E3 LM31's 0.884", "cut its exposure from 1.307 to 0.991, then to [[LM31]]'s 0.884. Frozen over the whole window, "
    "those books lose 13.20% and 11.68%.")
assert "0.991" not in (ROOT / "src" / "lm31.md").read_text(encoding="utf-8") and \
    "0.884" in (ROOT / "src" / "lm31.md").read_text(encoding="utf-8"), "0.991 is LM35's, 0.884 LM31's"
pc("E3 R8 frozen 2025", FZ["2025-04-07"]["R8"], 2, "10.15", loss=True, n=2)
chk("E3 R8 exposure 21 Feb", float(K.expo("R8", WIN["2025-04-07"][0]).sum()), ".3f", "1.005", n=3)
pc("E3 R8 path 2025", AC["2025-04-07"]["R8"], 2, "13.84", loss=True, n=2)
g25 = K.growth(*WIN["2025-04-07"][:2])
assert f"{r8['2025-03-03'][0]:.3f}" == "1.005"
pc("E3 book of 3 March", float(K.expo("R8", "2025-03-03") @ g25), 2, "13.35", loss=True)
chk("E3 1 April (A31-32)", r8["2025-04-01"][1], ".2f", "1.33")
pc("E3 book of 1 April", float(K.expo("R8", "2025-04-01") @ g25), 2, "13.42", loss=True)
assert max(r8["2025-03-03"][1], r8["2025-04-01"][1], r8["2020-02-03"][1], r8["2020-03-02"][1]) < 1.5 - 1e-6
has("E3 cap", "and the cap of 1.5 bound at neither")
for n in ("2020", "2024-08-05", "2025-04-07"):
    s_, dev = K.SCALE[n]
    assert dev < 1e-12, (n, "R8's book is R6's scaled")
    assert abs(FZ[n]["R8"] - s_ * FZ[n]["R6"]) < 1e-12
pc("KC3 R6 frozen 2025", FZ["2025-04-07"]["R6"], 2, "10.10", loss=True, n=3)
chk("KC3 from printed", 1.005 * 10.10, ".2f", "10.15", n=2)
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
pc("E4 0050 2008", R08["USO"][0], 2, "55.66", loss=True, n=2)
pc("E4 TR23 2008", LV[TPOS[b8]] / LV[TPOS[a8]] - 1, 2, "56.02", loss=True)


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
        assert x < 0, (label, x, "an unsigned proxy return is a loss")
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
has("E4 window", "From 29 October 2007 to 20 November 2008, 0050 itself lost 55.66% (TR23 56.02%), and USD/TWD rose "
    "from 32.390 to 33.390 (+3.09%).", 1)
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
pc("E4 R2 on 22 January", 0.4 * K.R50["2008-01-22"], 1, "2.8", loss=True)
pc("E4 0050 on 22 January", K.R50["2008-01-22"], 2, "6.93", loss=True)
pd25 = re.search(r"00646~SPY daily ([\d.]+) weekly ([\d.]+).*00679B~TLT daily ([\d.]+) weekly ([\d.]+).*00635U~GLD "
                 r"daily ([\d.]+) weekly ([\d.]+).*00642U~USO daily ([\d.]+) weekly ([\d.]+).*00642U~DBO daily ([\d.]+) "
                 r"weekly ([\d.]+)", K.OUT[24])
assert pd25 and "498 ISO weeks" in K.OUT[24]
corr = [float(x) for x in pd25.groups()]
for v, p_, n_ in zip(corr[0::2], ["0.705", "0.783", "0.745", "0.655", "0.696"], [1, 2, 1, 2, 1], strict=True):
    chk("E5 daily correlation", v, ".3f", p_, n=n_)                # 0.655 and 0.783 also in the zh box
for v, p_ in zip(corr[1::2], ["0.944", "0.952", "0.926", "0.845", "0.894"], strict=True):
    chk("E5 weekly correlation", v, ".3f", p_)
has("E5 weeks", "over 498 ISO weeks of the wealth frame (first, last and two across 0050's halt dropped)")
row("E5 daily", ["Daily", "0.705", "0.783", "0.745", "0.655", "0.696"])
row("E5 weekly", ["Weekly", "0.944", "0.952", "0.926", "0.845", "0.894"])
has("E5 roll", "Invesco states no roll rule for DBO, unlike USCF for USO, so the two are compared by their data only.")
a20, b20, _ = WIN["2020"]
pc("E5 00642U 2020", g20[4], 2, "46.42", loss=True)
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
pc("E5 R1 on proxies, USO", float(e20 @ uso), 1, "21.5", loss=True)
chk("E5 R1 on proxies, DBO", -100 * float(e20 @ dbo), ".0f", "19")
pc("E5 R1 on the funds", FZ["2020"]["R1"], 2, "19.84", loss=True)
gap08 = float(K.FIRST["R1"] @ (R08["DBO"] - R08["USO"]))
gap20 = float(e20 @ (dbo - uso))
assert round(100 * gap08) == 2 and round(100 * gap20) == 3, (gap08, gap20)
has("pitfall: oil proxy", "from the unrounded losses, the oil proxy alone moves R1's loss by about two points in 2008 "
    "and three in 2020")
has("zh: correlations", "只有 0.655 到 0.783")
z_ = K.z
chk("KC4 dates without a US session", int(z_.sum()), "d", "80")
pc("KC4 00646 none", float(np.abs(K.X[z_, 1]).mean()), 2, "0.43", loss=False)
pc("KC4 00646 one", float(np.abs(K.X[K.one, 1]).mean()), 2, "0.67", loss=False)
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
pcs("E6 partial scenario", full[1:], 2, ["-4.79", "+0.71", "-1.46", "-1.69"], n=[1, 3, 1, 1])
CUR = K.CUR
pc("E6 factor R1", float(CUR["R1"] @ (beta * -0.10)), 2, "3.77", loss=True)
pc("E6 factor R4", float(CUR["R4"] @ (beta * -0.10)), 2, "7.28", loss=True, n=2)
# the printed 3-dp betas give R1 3.76 (A35-31), so the text says the losses come from the unrounded betas and books
pc("E6 factor R1 from 3-dp betas (not printed)", float(CUR["R1"] @ (np.round(beta, 3) * -0.10)), 2, "3.76",
   loss=True, in_md=False)
has("E6 unrounded", "costs R1 3.77% and R4 7.28%, from the unrounded betas and books.")
has("E6 last column", "Times −9.70%, the betas give [[ex:case]]'s last column: 00642U −1.92% against −14.62% actual, "
    "and R1 −3.62% against −7.70%.")
sd = np.sqrt(np.diag(K.S))
chk("E7 full correlation (A27-11)", float(K.S[0, 2] / sd[0] / sd[2]), ".3f", "-0.105", n=3)
chk("E7 lambda_N", K.lam_min, ".3f", "0.298")
pc("E7 00679B full", full[2], 2, "+0.71", n=3)
pc("E7 00679B break", brk[2], 2, "-2.04", n=2)
pc("E7 R3 full", float(CUR["R3"] @ full), 2, "1.41", loss=True, n=3)      # 1.41 also E10's times equity
pc("E7 R3 break", float(CUR["R3"] @ brk), 2, "2.95", loss=True)
pc("E7 R7 full", float(CUR["R7"] @ full), 2, "1.40", loss=True)
pc("E7 R7 break", float(CUR["R7"] @ brk), 2, "3.00", loss=True)
a22, b22 = TD[K.p22], TD[K.k22]           # the 2022 illustration's peak and trough
assert (a22, b22) == ("2022-01-17", "2022-10-25")
has("E7 2022 dates", "an illustration outside the five scenarios, from 17 January to 25 October 2022:")
row("E7 2022 table", ["Return"] + [s2(x).replace("-", "−") for x in (
    LV[TPOS[b22]] / LV[TPOS[a22]] - 1, K.g22[0], K.g22[2], float(K.expo("R2", a22) @ K.g22),
    float(K.expo("R4", a22) @ K.g22))], 1)
pcs("E7 2022 table", [LV[TPOS[b22]] / LV[TPOS[a22]] - 1, K.g22[0], K.g22[2], float(K.expo("R2", a22) @ K.g22),
                      float(K.expo("R4", a22) @ K.g22)], 2, ["-28.47", "-33.93", "-22.15", "-22.37", "-29.86"])
chk("E7 2022 daily", float(np.corrcoef(K.X[K.ep, 0], K.X[K.ep, 2])[0, 1]), ".3f", "-0.138")
chk("E7 2022 weekly", float(np.corrcoef(K.we[:, 0], K.we[:, 2])[0, 1]), "+.3f", "+0.019")
chk("E7 2022 weeks", K.nwe, "d", "38")
chk("E7 full weekly (A27-11)", float(np.corrcoef(K.wf[:, 0], K.wf[:, 2])[0, 1]), ".3f", "-0.022")
assert K.nwf == 498
chk("E7 tail days", K.nev, "d", "48", n=2)
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
pc("KC5 R4 break", float(CUR["R4"] @ brk), 2, "6.89", loss=True)
assert abs(float(CUR["R4"] @ full) - float(CUR["R4"] @ brk)) < 1e-15 and CUR["R4"][2] == 0
chk("KC5 R4 00679B", float(CUR["R4"][2]), ".3f", "0.000")

# ---------------------------------------------------------------- Section 6: reverse stress (E8, X6, Deep Dive, KC)
S, MU = K.S, K.MU
kmax, k7 = K.kmax, K.k7
E8_N = {"0.7434": 2, "1.0174": 2, "13.52": 3, "9.91": 2, "12.27": 2}    # the rest printed once (KC6, X6, formulas)
for k, (pm, ps, pd) in {"R1": ("0.048", "0.7434", "13.52"), "R2": ("0.055", "0.7216", "13.93"),
                        "R4": ("0.078", "1.0174", "9.91"), "R5": ("0.030", "0.5717", "17.54"),
                        "R8": ("0.051", "0.8191", "12.27")}.items():
    e = CUR[k]
    sp, mp = math.sqrt(float(e @ S @ e)), float(e @ MU)
    pc(f"E8 {k} mean", mp, 3, pm, loss=False)
    chk(f"E8 {k} s_p", 100 * sp, ".4f", ps, n=E8_N.get(ps))
    chk(f"E8 {k} d*", (K.LOSS + mp) / sp, ".2f", pd, n=E8_N.get(pd))
    chk(f"E8 {k} d* from printed", (10 + float(pm)) / float(ps), ".2f", pd, n=E8_N.get(pd))
pcs("E8 R1 shock", K.XSTAR["R1"], 2, ["-10.47", "-8.79", "-1.21", "-6.12", "-23.00"], n=[2, 1, 1, 1, 1])
E8 = {"R1": ("0.048", "0.7434", "13.52"), "R2": ("0.055", "0.7216", "13.93"), "R4": ("0.078", "1.0174", "9.91"),
      "R5": ("0.030", "0.5717", "17.54"), "R8": ("0.051", "0.8191", "12.27")}
row("E8 means", ["Mean, %"] + [E8[k][0] for k in E8], 1)
row("E8 s_p", ["$s_p$, %"] + [E8[k][1] for k in E8], 1)
row("E8 d*", ["$d^*$"] + [E8[k][2] for k in E8], 1)
# X6's table: the four shocks and their distances
xb2_, db2_, _ = K.bounded(CUR["R2"])
x6 = [("R1, (35.4)", K.XSTAR["R1"], (K.LOSS + float(CUR["R1"] @ MU)) / math.sqrt(float(CUR["R1"] @ S @ CUR["R1"]))),
      ("R8, (35.4)", K.XSTAR["R8"], (K.LOSS + float(CUR["R8"] @ MU)) / math.sqrt(float(CUR["R8"] @ S @ CUR["R8"]))),
      ("R2, $x_{0050}\\ge-10\\%$", xb2_, db2_), ("Worst day of each fund", K.woe, K.maha(K.woe))]
for lab, xv, dv in x6:
    for v in xv:
        assert not tie(100 * float(v), ".2f"), (lab, v)
    assert not tie(float(dv), ".2f")
    row(f"X6 {lab}", [lab] + [f"{100 * float(v):.2f}".replace("-", "−") for v in xv] + [f"{float(dv):.2f}"], 1)
assert abs(K.maha(K.XSTAR["R8"]) - x6[1][2]) < 1e-9 and abs(float(CUR["R8"] @ K.XSTAR["R8"]) + K.LOSS) < 1e-12
assert [f"{100 * v:.2f}" for v in K.XSTAR["R8"]] == ["-8.90", "-7.65", "-4.57", "-6.75", "-14.14"]
assert [f"{100 * v:.2f}" for v in xb2_] == ["-10.00", "-10.81", "-9.89", "-8.67", "-0.34"]
assert [f"{100 * v:.2f}" for v in K.woe] == ["-10.00", "-12.59", "-7.15", "-11.09", "-22.20"]
has("E8 points to X6", "and R1's shock is the first row of [[ex:reverse]].")
od = np.argsort(-K.dt)
chk("largest distance", float(K.dt[od[0]]), ".3f", "15.017", n=3)
assert K.fr.est_dates[od[0]] == "2026-03-09" and K.fr.est_dates[od[1]] == "2020-03-09"
assert K.fr.est_dates[od[2]] == "2025-04-07"
has("E8 dates", "The sample's largest distance, 15.017, came on 9 March 2026, when 00642U rose 33.10%")
pc("E8 00642U on 9 March 2026", float(K.X[od[0], 4]), 2, "33.10", loss=False)
chk("second distance", float(K.dt[od[1]]), ".3f", "12.971")
chk("2025-04-07 distance", float(K.dt[od[2]]), ".3f", "12.937", n=5)
chk("median distance", float(np.quantile(K.dt, 0.5, method="inverted_cdf")), ".2f", "1.60")
e1 = CUR["R1"]
sp1, mp1 = math.sqrt(float(e1 @ S @ e1)), float(e1 @ MU)
pc("E8 worst loss within d <= k_max", mp1 - kmax * sp1, 2, "11.12", loss=True)
chk("E8 worst loss from printed", 15.017 * 0.7434 - 0.048, ".2f", "11.12")
has("E8 next distances", "Next come 12.971 (9 March 2020) and 12.937 (7 April 2025), and the median is 1.60.", 1)
has("E8 worst loss", "Within $d\\le15.017$ R1 can lose $15.017\\times0.7434\\%-0.048\\%=11.12\\%$.", 1)
xb1, db1, nb1 = K.bounded(CUR["R1"])
xb2, db2, nb2 = K.bounded(CUR["R2"])
xb8, db8, nb8 = K.bounded(CUR["R8"])
chk("bounded R1 d", db1, ".2f", "13.52", n=3)
chk("bounded R2 d", db2, ".2f", "17.01", n=3)
pc("bounded R2 00679B", xb2[2], 2, "-9.89", n=3)
pc("00679B worst day", float(K.woe[2]), 2, "-7.15", n=3)
assert "inactive" in nb8 and "active" in nb1 and "active" in nb2
chk("worst-of-each distance", K.maha(K.woe), ".2f", "19.07", n=2)
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
pc("widget loss", r49, 2, "7.78", loss=True)
chk("widget ruin", -1 / r49, ".2f", "12.85")
chk("widget ruin from printed", 1 / 0.0778, ".2f", "12.85", in_md=False)
chk("widget d", K.maha(W7), ".2f", "12.94")
chk("widget farther", K.FARTHER_0407, "d", "2")
has("widget text", "a loss of 7.78%, ruin from leverage 12.85 (Section 8), distance 12.94 and 2 of 2,362 days "
    "farther")
pc("pitfall R1's 0050", K.XSTAR["R1"][0], 2, "-10.47", n=2)
chk("KC6 R4 d*", (K.LOSS + float(CUR["R4"] @ MU)) / math.sqrt(float(CUR["R4"] @ S @ CUR["R4"])), ".2f", "9.91", n=2)
e4 = CUR["R4"]
pc("KC6 worst loss within d <= k_0407", float(e4 @ MU) - k7 * math.sqrt(float(e4 @ S @ e4)), 2, "13.08", loss=True)
chk("KC6 from printed", 12.937 * 1.0174 - 0.078, ".2f", "13.08")
has("KC6 answer", "Within $d\\le12.937$ its worst loss is $12.937\\times1.0174\\%-0.078\\%=13.08\\%$.", 1)

# ---------------------------------------------------------------- Section 7: limits, locks, gaps (X8, X5, E9, KC)
X8_RULE = {"0050": ("TWSE, Art. 8 ¶1", "10%"), "00646": ("TWSE, Art. 8 ¶1 item 1", "none"),
           "00679B": ("TPEx, Art. 7 ¶1 item 一", "none"), "00635U": ("TWSE, Art. 8 ¶1 item 2", "none"),
           "00642U": ("TWSE, Art. 8 ¶1 item 2", "none")}
for j, s in enumerate(FUNDS):
    w = fr.W[:, j]
    n10 = int((np.abs(w) > 0.10 + K.EPS).sum())
    assert not tie(100 * w.min(), ".2f") and not tie(100 * w.max(), ".2f")
    row(f"X8 {s}", [s, *X8_RULE[s], s2(w.min()).replace("-", "−"), s2(w.max()), str(n10)], 1)
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
                     f"{cl_:.2f}".replace("-", "−"), f"{float(ratio):.2f}"], 1)
    for v in (gp_, low_, cl_, float(ratio)):
        assert not tie(v, ".2f")
chk("X5 2015 ratio from printed", -1.66 / -4.96, ".2f", "0.33")
assert f"{gl_unr['2015-08-24'][0] / gl_unr['2015-08-24'][1]:.2f}" == "0.34"
has("X5 tie", "2020's holds through the closing call auction to 13:29:55")
assert "the last 13:29:55" in K.OUT[44]
stale = re.search(r"09:00:05 \(the daily open\) (-[\d.]+)%", K.OUT[44])
assert stale
chk("KC7c stale open", float(stale.group(1)), ".2f", "-5.52")
chk("KC7c 09:01:00", gl_unr["2025-04-07"][0], ".2f", "-10.28", n=2)
has("KC7c", "(c) The open is the stale 09:00:05 value: −5.52%, against −10.28% by 09:01:00 ([[ex:gaps]]).")
assert gl_unr["2025-04-07"][0] < 0 and float(stale.group(1)) < 0
chk("zh7 to 09:01:00", -gl_unr["2025-04-07"][0], ".2f", "10.28")
chk("zh7 stale open", -float(stale.group(1)), ".2f", "5.52")
has("zh7 gap", "當天到 09:01:00 加權指數已跌 10.28%，每日資料的開盤價卻是 09:00:05 的舊值，只顯示 5.52%", 1)
# data/lm35_common.py stops unless each day's 09:00:00 value is the previous close
has("X5 note 09:00:00", "log changes from the previous close, which the series prints at 09:00:00", 1)
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
pc("E9 below the lock", o8 / 158.4 - 1, 2, "4.55", loss=True, n=2)
pc("E9 below 2 April", o8 / c0 - 1, 2, "14.09", loss=True, n=3)
assert K.WD[K.WIDX["2025-04-07"] + 1] == "2025-04-08"
has("E9 next open", "An unfilled sale waited for 8 April's open, 151.20: 4.55% below the lock and 14.09% below "
    "2 April.", 1)
has("P3 data", "is held from the close of 2 April 2025, 176.00. On 7 April a sell order does not fill at the lock, "
    "158.40, and 8 April opens at 151.20.", 1)
pc("E9 00631L", K.r631[K.EPOS["2025-04-07"]], 3, "19.995", loss=True)
pc("E9 00631L next", K.r631[K.EPOS["2025-04-08"]], 2, "11.20", loss=True)
tx = K.lim.filter(pl.col("date") == "2025-04-07").row(0, named=True)
pc("E9 TX", tx["RF"], 2, "10.00", loss=True)
pc("E9 TAIEX price", tx["RS"], 2, "-9.70", n=5)     # the price index here, TR23 at the other four
chk("E9 TX volume", tx["volume"], ",d", "2,736", n=2)
tx24 = K.lim.filter(pl.col("date") == "2024-08-05").row(0, named=True)
chk("KC7 volume 2024", tx24["volume"], ",d", "211,207")
chk("KC7 volume 8 April", K.vol8, ",d", "152,423")
has("KC7 question", "traded 2,736 contracts on 7 April 2025, against 211,207 on 5 August 2024 and 152,423 on 8 April "
    "2025", 1)
has("zh7", "0050 開在 151.20，比鎖住的價格再低 4.55%")

# ---------------------------------------------------------------- Section 8: leverage, ruin, margin (X7, E10, KC)
m41 = re.findall(r"2024-08-05 (R[35]) (-[\d.]+) \((\d{4}-\d\d-\d\d); last close ([+-][\d.]+)\)", K.OUT[40])
assert [x[0] for x in m41] == ["R3", "R5"] and all(x[2] == "2024-07-26" for x in m41)
chk("R3 low 2024", float(m41[0][1]), ".2f", "-1.40")
chk("R5 low 2024", float(m41[1][1]), ".2f", "-1.47")
chk("R3 end 2024", float(m41[0][3]), "+.2f", "+0.11", n=3)    # and X3's R3 2024 frozen and actual
chk("R5 end 2024", float(m41[1][3]), ".2f", "-0.07", n=4)     # and X3's R5 2024 frozen; problem 6's beta
has("ruin over a window", "R3's and R5's 2024 books reach it on 26 July")
lw20, lw25 = FZ["2020"]["R6"], FZ["2025-04-07"]["R6"]
ld25 = float(K.expo("R6", "2025-04-02") @ W7)
chk("X7 R6 2020", -1 / lw20, ".2f", "7.67", n=3)
chk("X7 R6 2025", -1 / lw25, ".2f", "9.90")
chk("X7 R6 7 April", -1 / ld25, ".2f", "16.77")
chk("X7 0050 next open", -1 / K.xo, ".2f", "7.10", n=2)
has("X7 crossings", "The lines cross zero at 7.67, 9.90, 16.77 and 7.10")
has("X7 text", "draws (35.2) for R6's book in three replays and for 0050 to the open of 8 April 2025.", 1)
pc("L = 5 at the lock", 5 * -0.10, 2, "50.00", loss=True)
pc("L = 5 at the next open", 5 * K.xo, 2, "70.45", loss=True)
chk("R8's cap", 1.5, ".1f", "1.5", n=2)
chk("R8's largest uncapped ratio (A31-29)", float(K.ratio.max()), ".2f", "2.14")
pc("X7 note R6 2020", lw20, 2, "13.04", loss=True, n=2)
pc("X7 note R6 2025", lw25, 2, "10.10", loss=True, n=3)
pc("X7 note R6 7 April", ld25, 3, "5.964", loss=True)
pc("X7 note 0050", K.xo, 2, "14.09", loss=True, n=3)
F26, notional = K.F26, K.notional
chk("E10 F", F26, ",.0f", "49,357", n=2)
chk("E10 notional", notional, ",.0f", "9,871,400", n=5)
assert notional == 200 * F26, "NT$200 a point (lm23.md:327)"
has("E10 multiplier", "NT\\$200 a point")
has("E10 margins", "sets the initial margin at NT\\$701,000 and the maintenance margin at NT\\$538,000")
chk("E10 f", notional / 701_000, ".2f", "14.08", n=2)
chk("E10 margin gap", 701_000 - 538_000, ",d", "163,000")
pc("E10 call fall", -163_000 / notional, 2, "1.65", loss=True, n=2)
chk("E10 limit-day loss", 0.10 * notional, ",.0f", "987,140")
chk("E10 times equity", 0.10 * notional / 701_000, ".2f", "1.41", n=3)
chk("E10 equity", 701_000 - 0.10 * notional, ",.0f", "-286,140")
has("E10 from printed", "$f=9,871,400/701,000=14.08$, and a fall of $163,000/9,871,400=1.65%$")
has("zh8", "一口台指期是 14.08 倍，下跌 1.65% 就碰到維持保證金")
chk("KC8 R6's 2020 loss a unit", -lw20, ".5f", "0.13036")
chk("KC8 smallest ruin leverage", 1 / 0.13036, ".3f", "7.671")
chk("KC8 from the unrounded loss", -1 / lw20, ".3f", "7.671")
pc("KC8 R6 under the worst of each", float(CUR["R6"] @ K.woe), 2, "11.11", loss=True)
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
                                                                      for k in ("R1", "R6", "R8")], 1)
row("X9 MDD", ["Drawdown", "MDD, % ([[LM32]])"] + [f"{100 * fail_vals[k][1]:.2f}" for k in ("R1", "R6", "R8")], 1)
row("X9 DD0", ["", "largest $\\mathrm{DD}^0_t$, % ([[LM32]])"] + [f"{100 * fail_vals[k][2]:.2f}"
                                                                 for k in ("R1", "R6", "R8")], 1)
for k in ("R1", "R6", "R8"):
    for v in fail_vals[k]:
        assert not tie(100 * v, ".2f") and v > 0
ruin_row = [-1 / FZ["2020"]["R1"], -1 / FZ["2020"]["R6"], -1 / (FZ["2020"]["R8"] / K.SCALE["2020"][0])]
row("X9 ruin", ["Ruin", "$L_{\\mathrm{ruin}}$ over 2020's window"] + [f"{x:.2f}" for x in ruin_row], 1)
chk("X9 R8 scale", K.SCALE["2020"][0], ".3f", "1.307", n=2)
# funding: R8's borrowing per unit of equity is its held exposure minus 1; the held exposure drifts between trades,
# to at most 1.53 on 22 August 2023 (lm31.md:335), above the cap of 1.5 that a trade sets
held = {k: K.BOOKS[k][1].sum(axis=1) for k in ("R1", "R6", "R8")}
assert held["R1"].max() <= 1 + 1e-12 and held["R6"].max() <= 1 + 1e-12, "R1 and R6 never borrow"
j8 = int(np.argmax(held["R8"]))
assert K.BOOKS["R8"][0][j8] == "2023-08-22" and f"{held['R8'][j8]:.2f}" == "1.53"
chk("X9 R8's largest borrowing", held["R8"][j8] - 1, ".2f", "0.53", n=2)
assert "to at most 1.53 on 22 August 2023" in (ROOT / "src" / "lm31.md").read_text(encoding="utf-8")
assert abs(K.vr.RF + K.vr.SPREAD - 0.035) < 1e-15, "the through case's borrowing rate, 3.5% (illustrative)"
row("X9 funding", ["Funding", "borrowing at an illustrative 3.5% a year", "none", "none", "up to 0.53"], 1)
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
chk("KC9 worst-of-each distance", K.maha(K.woe), ".2f", "19.07", n=2)
chk("KC9 largest distance", float(K.dt.max()), ".2f", "15.02")

# ---------------------------------------------------------------- practice problems and solutions
chk("P1", 0.6 * -10 + 0.4 * 1.81, ".2f", "-5.28", n=2)
chk("P1 A", -10 + 1.81, ".2f", "-8.19")
chk("P1 C", 0.6 * -10, ".2f", "-6.00")
assert f"{100 * W7[2]:+.2f}" == "+1.81", "problem 1 uses 00679B's return of 7 April 2025"
has("S1", "$0.6\\times(-10\\%)+0.4\\times1.81\\%=-5.28\\%$", 1)
chk("P2", 1 / 0.08, ".1f", "12.5", n=5)            # problems 2 and 5
chk("P2 B", 8.0, ".1f", "8.0")
chk("P2 C", (1 - 0.08) / 0.08, ".1f", "11.5")
pc("P3", K.P3["open"], 2, "-56.36", n=2)
pc("P3 A", K.P3["close"], 2, "-40.00")
pc("P3 B", K.P3["lock"], 2, "-18.18")
chk("P4", 100 * (1.01 * 0.96 * 32.48 / 32.00 - 1), ".2f", "-1.59", n=2)
chk("P4 A", 100 * (1.01 * 0.96 - 1), ".2f", "-3.04")
chk("P4 C", 100 * (1.01 * 0.96 * 32.00 / 32.48 - 1), ".2f", "-4.47")
chk("P5", 10 / 0.8, ".1f", "12.5", n=5)
chk("P5 A", (10 / 0.8) ** 2, ".2f", "156.25")
chk("P5 B", math.sqrt(10 / 0.8), ".2f", "3.54")
keys = re.findall(r"^(\d+)\. \*\*([A-C])\*\* is correct", RAW, flags=re.MULTILINE)
assert keys == [("1", "B"), ("2", "A"), ("3", "C"), ("4", "B"), ("5", "C")], keys
chk("S6 bond normal", -0.07 * -10, "+.2f", "+0.70")
chk("S6 book normal", 0.4 * -10 + 0.6 * 0.70, ".2f", "-3.58")
chk("S6 0050 part", 0.4 * -10, ".2f", "-4.00", n=2)
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
chk("S7 sigma_p", math.sqrt(0.472), ".4f", "0.6870", n=2)
chk("S7 d*", 5 / math.sqrt(0.472), ".2f", "7.28", n=2)            # and E6's R4
chk("S7 d* from printed", 5 / 0.6870, ".2f", "7.28", n=2)
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
pc("P8 mean 0050", float(MU[0]), 4, "0.0995", loss=False)
pc("P8 mean 00679B", float(MU[2]), 4, "-0.0040", n=2)
chk("P8 SD 0050", 100 * float(sd[0]), ".4f", "1.2898", n=2)
chk("P8 SD 00679B", 100 * float(sd[2]), ".4f", "0.8657", n=2)
chk("S8 move", -0.0040 + 0.105 * (0.8657 / 1.2898) * 10.0995, "+.2f", "+0.71", n=3)
chk("S8 move at 0.30", -0.0040 - 0.30 * (0.8657 / 1.2898) * 10.0995, ".2f", "-2.04", n=2)
chk("S8 10 + mean", 10 + 0.0995, ".4f", "10.0995")
has("S8 move", "00679B moves $-0.0040\\%+0.105\\times(0.8657/1.2898)\\times10.0995\\%=+0.71\\%$, and −2.04% at "
    "0.30.", 1)
pc("S10 R6 frozen", FZ["2020"]["R6"], 2, "13.04", loss=True, n=2)
pc("S10 R6 path", AC["2020"]["R6"], 2, "14.43", loss=True)
ef6 = K.TRADE_EFFECT_2020["R6"]
assert [d for d, *_ in ef6] == ["2020-02-03", "2020-03-02"]
for d, dl, gt, eff in ef6:
    bought = [FUNDS[j] for j in range(5) if dl[j] > 0]
    assert bought == ["0050", "00646", "00642U"], (d, bought)
    assert all(-0.405 < gt[j] < -0.215 for j in (0, 1, 4)), (d, gt)
assert round(-100 * min(min(gt[j] for j in (0, 1, 4)) for _, _, gt, _ in ef6)) == 40
assert round(-100 * max(max(gt[j] for j in (0, 1, 4)) for _, _, gt, _ in ef6)) == 22
has("S10 trades", "Its trades of 3 February and 2 March moved weight into 0050, 00646 and 00642U, which fell a further "
    "22% to 40%.", 1)
pc("S10 R6 effect 3 Feb", ef6[0][3], 2, "0.90", loss=True)
pc("S10 R6 effect 2 Mar", ef6[1][3], 2, "0.47", loss=True)
gap6 = AC["2020"]["R6"] - FZ["2020"]["R6"]
assert abs(ef6[0][3] + ef6[1][3] - gap6) < 0.0005, "nearly the gap"
assert abs(AC["2020"]["R6"] - K.R6_GROSS_2020) < 0.0003, "costs take about 0.02 points"
ef8 = K.TRADE_EFFECT_2020["R8"]
pc("S10 R8 effect 3 Feb", ef8[0][3], 2, "3.41", loss=False)
pc("S10 R8 effect 2 Mar", ef8[1][3], 2, "1.10", loss=False)
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
# the recipe, recomputed here without K's PRE and growth(): the drifted book before each trade from the previous
# session's exposures, that session's returns and (R8) one session's interest on the cash; each fund's return from the
# trade's close to the trough as a sum of log returns; then (exposure after - drifted book) times that return
for k, eff in (("R6", ef6), ("R8", ef8)):
    dts, exs, _ = K.BOOKS[k]
    for d, dl, gt, e_ in eff:
        i = dts.index(d)
        e0, r_ = exs[i - 1], fr.W[K.WIDX[d]]
        cash = 1 - float(e0.sum())
        rate = (K.RF if cash >= 0 else K.RF + K.SPREAD) / fr.A_wealth
        drifted = e0 * (1 + r_) / (float(e0 @ (1 + r_)) + cash * (1 + rate))
        dl_ = exs[i] - drifted
        gt_ = np.expm1(np.log1p(fr.W[K.WIDX[d] + 1:K.WIDX[t20] + 1]).sum(axis=0))
        assert np.abs(dl_ - dl).max() < 1e-12 and np.abs(gt_ - gt).max() < 1e-12, (k, d)
        assert abs(float(dl_ @ gt_) - e_) < 1e-12, (k, d)
chk("S11 d", db2, ".2f", "17.01", n=3)
pc("S11 00679B", xb2[2], 2, "-9.89", n=3)
chk("S12 f", notional / K.EQ12, ".2f", "7.04")
chk("S12 margin gap", K.EQ12 - 538_000, ",d", "864,000")
pc("S12 call", -K.P12["call"], 2, "8.75", loss=True)
chk("S12 after a limit day", K.P12["after"], ",.0f", "414,860")
assert 0 < K.P12["after"] < 538_000
pc("S12 ruin fall", -K.P12["ruin"], 2, "14.20", loss=True)
has("P12 equity", "equity of NT\\$1,402,000, twice the initial margin")
assert K.EQ12 == 1_402_000

# ---------------------------------------------------------------- the overview (front matter), bullet by bullet
# Each bullet is checked whole, so a changed digit fails; its numbers are the body's, checked above.
OVERVIEW = [
    ("On 7 April 2025, after five calendar days without trading, TR23 fell 9.70%, its worst day since 2003. The "
     "through case's eight rules lost from 5.06% (R7) to 8.33% (R4)."),
    ("Peak to trough, the five scenario windows cost TR23 from 18.31% (2024) to 56.02% (2008). The 2008 and 2015 "
     "windows are replayed hypothetically, on 0050 itself and US proxies."),
    ("A frozen book ignores the rule's trades. In 2020 R8 lost 17.04% frozen and 12.58% on its own path. In 2025 it "
     "lost 10.15% frozen and 13.84% on its path, after a trade raised its exposure to 1.319."),
    ("A beta model fitted on the full sample, that day included, gives R1 a loss of 3.62% on 7 April 2025, under half "
     "the actual 7.70%."),
    ("The reverse stress test finds the shock of least Mahalanobis distance that costs a book 10%. R8's current book "
     "needs only 12.27, below the 12.94 of 7 April 2025. A distance ranks shocks and is not a probability."),
    ("0050 locked at its 10% limit on 7 April 2025 and opened 4.55% lower the next day. A book of 0050 levered five "
     "times lost 50.00% at the lock and 70.45% by the next open."),
    ("One TX contract held on its initial margin is levered 14.08 times. A fall of 1.65% reaches the maintenance "
     "margin, and a 10% limit day leaves equity of NT$−286,140."),
    ("Weak growth, a drawdown, funding and ruin are four different failures of the same rules, and surviving the "
     "replayed scenarios does not cover the losses that no scenario shows."),
]
assert FM.count('\n  - "') - FM.split("\noverview:", 1)[0].count('\n  - "') == len(OVERVIEW), "eight bullets"
for k, b_ in enumerate(OVERVIEW):
    has_fm(f"overview {k + 1}", b_)
    assert all(TOK[t] > 0 for t in tokens(norm_text(b_))), (k, "the bullet's numbers are the body's")
assert TD[0].startswith("2003"), "TR23 starts in 2003, so its worst day is the worst since 2003"
has("case: since 2003", "its worst day since 2003 ([[LM26]])", 1)

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


REFV_SEEN: set[str] = set()


def refv(key: str, value: float, fmt: str) -> None:
    global N_CHECKS
    got = format(value, fmt)
    assert REF[key] == got, (key, REF[key], got)
    assert not tie(value, fmt), ("rounding tie in the lab's reference", key, value)
    REFV_SEEN.add(key)
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
e8 = cpt["R8 exposure"]                 # the exposures R8 trades, after the turnover limit (task (e))
assert isinstance(e8, dict)
refv("R8 traded min", e8["min"], ".3f")
refv("R8 traded mean", e8["mean"], ".3f")
refv("R8 traded at cap", e8["at cap"], "d")
refv("R8 uncapped max", e8["uncapped max"], ".3f")
REF_OTHER = {"first", "R3 last trade", "R3 caps", "R3 floors"} | {f"{k} active" for k in K.CP_RULES}   # asserted
assert set(REF) == REFV_SEEN | REF_OTHER, ("REF entries without a check", set(REF) - REFV_SEEN - REF_OTHER)
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

# ====================================================================== every number of the body
# Numbers that has() literals cover and the body prints more than once, with their exact counts (each occurrence read
# against its computed value or its source).
EQ = "an equation reference"
PINS: dict[str, tuple[int, str]] = {
    # signed and decimal values that only table rows and phrases check
    "-3.62": (2, "R1 under the beta model: X1 and E6"),
    "-7.70": (4, "R1 on 7 April 2025: X1, X3, E6 and solution 9"),
    "-8.33": (2, "TR23's worst day of 2024 (X2) and R4 on 7 April 2025 (X3)"),
    "-11.09": (2, "00635U's worst day, in X6 and X8"),
    "-22.20": (2, "00642U's worst day, in X6 and X8"),
    "0.4": (2, "problem 1's exposure, statement and solution"),
    "0.6": (2, "problem 1's exposure, statement and solution"),
    "1.01": (2, "X5's 2025 gap ratio; solution 4's factor"),
    "10.24": (2, "R1's largest DD0: X9 and KC9"),
    "5.04": (2, "R1's ruin leverage over 2020: X9 and KC9"),
    "151.20": (5, "0050's open of 8 April 2025: E9, zh box, problem 3 and solution 3"),
    "158.40": (3, "0050's locked price: case box, E9, problem 3"),
    "176.00": (3, "0050's close of 2 April 2025: E9, problem 3, solution 3"),
    "1,402,000": (2, "problem 12's equity, statement and solution"),
    "701,000": (2, "TX's initial margin in E10"),
    "538,000": (2, "TX's maintenance margin, E10 and problem 12"),
    "200": (2, "NT$200 a point, E10 and problem 12"),
    "498": (2, "the full sample's ISO weeks (E5, E7)"),
    "22": (2, "R1's 22% with DBO (E4); the further fall of 22% (solution 10)"),
    "40": (2, "problem 6's 40%; the further fall to 40% (solution 10)"),
    "30": (3, "2025's 30 sessions (X2, E1); the checkpoint's 30% cap"),
    "20": (8, "20 sessions (the window rule, X2, E1, zh box); R1's 20% in each fund; 00631L's 20% limit"),
    "-10": (14, "-10%: 0050's limit as a shock or a bound (E6, E7, the bounded test, problems 1, 6, 8, 11); 10^{-10}"),
    "-12": (5, "2008's hypothetical R8 (X3's note); the 1e-12 and 10^{-12} solver tolerances"),
    "-9": (3, "2008's hypothetical R3 (X3's note); the Deep Dive's 10^{-9} bounds"),
    "09:00:05": (3, "the stale daily open: pitfall, zh box, KC"),
    "09:01:00": (5, "the gap's time: text, X5's header, pitfall, zh box, KC"),
    "16.10": (3, EQ), "27.5": (2, EQ), "35.2": (5, EQ), "35.4": (12, EQ),
    # dates and years
    "7 April 2025": (16, "the case day"), "7 April": (4, "the case day"), "7 Apr 2025": (2, "the case day: X2, X5"),
    "2 April 2025": (3, "the close before the case day"), "2 April": (6, "the close before the case day"),
    "8 April 2025": (2, "the next open (KC7, X7's text)"), "8 April": (2, "the next open (E9, problem 3)"),
    "9 April": (2, "2025's trough (case box, E1)"), "21 February 2025": (2, "2025's peak (E1, KC3)"),
    "3 March": (4, "R8's trade of 3 March 2025"), "1 April": (2, "R1's and R8's trades of 1 April 2025"),
    "3 February": (2, "the trades of 3 February 2020 (E3, solution 10)"),
    "2 March": (2, "the trades of 2 March 2020 (E3, solution 10)"),
    "30 January 2020": (2, "2020's worst day: pitfall, KC"), "30 Jan 2020": (2, "2020's worst day: X2, X5"),
    "19 March 2020": (2, "the worst five-session span's end (E1); 00720B's fall (X8's note)"),
    "March 2020": (2, "2020's worst five sessions (case box); R1's DD0 at 10% (KC9)"),
    "22 Jan 2008": (2, "2008's worst day: X2, X5"), "24 Aug 2015": (3, "2015's trough and worst day (X2), X5"),
    "5 Aug 2024": (3, "2024's trough and worst day (X2), X5"), "5 August 2024": (2, "the 2024 named day (E1, KC7)"),
    "4 March 2019": (2, "the rules' first trade"), "18 January 2017": (2, "E5's first joint date"),
    "8 October 2026": (6, "the last date, the current books' date"),
    "24 October 2026": (5, "the rules' fixing date and a retrieval date"),
    "2008": (16, "the year"), "2015": (8, "the year"), "2020": (22, "the year"), "2022": (3, "the year"),
    "2024": (9, "the year"), "2025": (18, "the year (with 年 in the zh boxes)"),
    # small integers
    "0": (33, "zero: exact-zero returns, inequalities, (1,0,0,0,0), means 0, X8's day counts, the code's indices"),
    "1": (38, "one: constants in formulas, rank 1, Art. 8 ¶1 and item 1, L=1, 1/10, lo=1, problem 1, Proposition 1"),
    "2": (31, "two: squares, Section 2, lo=2, item 2, X2's rank, X8's days, 2 days farther, problem 2"),
    "4": (14, "four: Section 4, X2's rank, lo=4,7, Principle 4, L=4, problem 4, the zh boxes' 4 月"),
    "5": (13, "five: worst 5 sessions, Sections 5-6, lo=5, L=5, ell=5%, problem 5"),
    "7": (11, "seven: Sections 7-8, the 7% limit before 2015, Art. 7, lo=4,7 and 7,8, problem 7, a zh date"),
    "8": (17, "eight: X2's rank, Section 8, Art. 8, lo=5,8 and 7,8, problem 2's 8%, problem 8, zh dates"),
    "9": (4, "Section 9, E4's R3 9%, problem and solution 9"),
    "10": (31, "10%: the limit, the reverse test's loss, the limit day, 10^{-k} tolerances, problem 10"),
}
# The numbers no check covers, with their counts: equation and section references, problem inputs, citation years and
# pages, retrieval dates, structure, and constants of formulas.
ALLOW: dict[str, tuple[int, str]] = {
    "+0.30": (2, "the constructed break: E7's correlation, problem 6's beta"),
    "-1": (14, "minus one in formulas (-1, Sigma^{-1}, -1/R)"),
    "-10.0": (1, "the Python block's limit (part 3 runs the block)"),
    "0.08": (2, "problem 2's loss, in solution 2"), "-0.08": (1, "problem 2's loss, in solution 2"),
    "-8": (1, "solution 2's -8%"),
    "1.0": (1, "problem 4's input"), "4.0": (1, "problem 4's input"), "0.96": (1, "solution 4's factor"),
    "32.00": (3, "problem 4's rate"), "32.48": (3, "problem 4's rate"),
    "0.8": (3, "problem 5's s_p; problem 7's SD"), "60": (1, "problem 6's 60%"),
    "1.2": (1, "problem 7's SD"), "-0.1": (1, "problem 7's correlation"), "0.5": (2, "problem 7's book"),
    "0.25": (1, "solution 7's arithmetic"), "1.44": (1, "solution 7's arithmetic"),
    "0.64": (1, "solution 7's arithmetic"), "-0.5": (1, "solution 7's arithmetic"),
    "3": (3, "lo=3; problem and solution 3"),
    "6": (6, "Sections 5-6, lo=1,6 and 5,6, BCBS p. 6, problem and solution 6"),
    "11": (2, "problem and solution 11"), "12": (2, "problem and solution 12"),
    "8.4": (1, EQ), "8.13": (1, EQ), "16.4": (1, EQ), "16.8": (3, EQ), "16.9": (2, EQ), "23.1": (1, EQ),
    "27.8": (1, EQ), "28.1": (2, EQ), "29.4": (3, EQ), "30.4": (1, EQ), "31.7": (1, EQ), "32.9": (1, EQ),
    "33.1": (1, EQ), "35.1": (2, EQ), "35.3": (8, EQ), "35.5": (5, EQ),
    "1998": (1, "citation year (Kupiec)"), "2009": (2, "citation year (Breuer et al.)"),
    "2018": (1, "citation year (BCBS)"), "2.1": (1, "Breuer et al.'s section"), "2.2": (1, "Breuer et al.'s section"),
    "2.3": (1, "Breuer et al.'s section"), "209": (1, "Breuer et al.'s page"), "210": (1, "Breuer et al.'s page"),
    "211": (1, "Breuer et al.'s page"), "2007": (1, "0050's 2007-2008 files, in a source note"),
    "10 October 2026": (1, "a retrieval date"), "18 October 2026": (2, "a retrieval date"),
    "19 October 2026": (1, "a retrieval date"), "12 August 2026": (1, "TAIFEX's margin table date (SOURCES.md)"),
}
for t_, (n_, why) in PINS.items():
    pin(t_, n_, why)


def _where(t: str) -> list[str]:
    out = []
    for m in TOKEN.finditer(BODY):
        if m.group(0) == t:
            out.append(BODY[max(0, m.start() - 30):m.end() + 15].replace("\n", " "))
    return out


unpinned = sorted(t for t in COVERED if TOK[t] > 1 and t not in PINNED)
uncovered = {t: k for t, k in TOK.items() if t not in COVERED}
if unpinned or uncovered != {t: k for t, (k, _) in ALLOW.items()}:
    for t in unpinned:
        print(f"UNPINNED {t!r} x{TOK[t]}: " + " || ".join(_where(t)))
    for t in sorted(set(uncovered) | set(ALLOW)):
        if uncovered.get(t) != ALLOW.get(t, (None,))[0]:
            print(f"ALLOW {t!r}: body x{uncovered.get(t, 0)}, listed {ALLOW.get(t, (None,))[0]}: "
                  + " || ".join(_where(t)))
assert not unpinned, f"covered numbers printed more than once without a count: {unpinned}"
assert uncovered == {t: k for t, (k, _) in ALLOW.items()}, "the uncovered numbers differ from ALLOW (listed above)"
print(f"\nnumbers of the body: {len(TOK)} distinct, {sum(TOK.values())} in all; {len(COVERED & set(TOK))} covered, "
      f"{sum(1 for v in PINNED.values() if v > 1)} of them with a count above 1 ({len(PINS)} through PINS); "
      f"{len(ALLOW)} listed in ALLOW")
print(f"anchor differences ({len(ANCHOR_DIFFS)}):")
for a_ in ANCHOR_DIFFS:
    print("   ", a_)
print(f"\nall {N_CHECKS} checks passed")
sys.exit(0)
