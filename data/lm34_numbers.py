"""Every number that LM34 (Backtesting Without Fooling Yourself) prints, computed and checked against src/lm34.md.

Run:  PYTHONUTF8=1 uv run python data/lm34_numbers.py
      (after data/vol3_series.py, data/vol5_series.py and data/vol5_rules.py; and after data/lm34_charts.py, whose
      chart and widget files this script checks)

Inputs and conventions: data/lm34_common.py, which keeps the code of data/vol6_anchors_lm34.py (the Stage 1 anchor
script): E5 through vol5_series.frames("E5"), the through case and the grid through vol5_rules (no rule is
re-implemented here), TR23 through data/processed/vol3_taiex.parquet, the survivorship files under data/raw/vol6/.
The module text is src/lm34.md; plans/vol-6-anchors.md, "LM34", holds the Stage 1 anchors A34-01 .. A34-38.

Part 1 compares each anchor line, as data/lm34_common.py recomputes it, with the anchor table's Value column: a
difference is reported, never forced. It also writes data/processed/lm34_grid.parquet (git-ignored): the grid's 60
configurations' net returns on the wealth frame, one column per configuration in the declared grid order (R1_1m,
R1_3m, R1_6m, R2_1m, ..., R3_126_1m, R3_126_3m, ..., R8_504_6m) after a column `date`. Its first row, 2019-03-04,
is the first purchase from the cash of 1 (wealth after it minus 1, so minus the cost share); the 1,851 rows from
2019-03-05 to 2026-10-08 are the daily net returns that CSCV and the reality check use, and the product of one plus
every row is the final wealth. data/make_lab_data.py copies it to labs/LM34_lab/data/lm34_grid.csv.

Part 2 checks the text (each check stops the script on a failure):
  chk(label, value, fmt, printed)  format(value, fmt) equals the printed string, the value is not a rounding tie of
                                   that format, and the printed string is in the module as a whole number. Hand
                                   computations are redone from the printed, rounded inputs (PITFALLS section 7).
  sci(label, value, printed)       a number printed as m\\times10^{e}, compared at the printed mantissa.
  has(label, text)                 a literal string (a date, a phrase, a table row) is in the module.
Part 3 runs the module's printed Python block and compares it with the computations; part 4 checks the structure
(labels, tags, knowledge checks, chart files) and the published lines that the text echoes. At the end the script
lists the numbers of the module that no check covered and prints "all N checks passed".
"""
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lm34_common as C
import numpy as np
import polars as pl
import vol5_rules as V
from scipy import stats

ROOT = HERE.parent
MD = ROOT / "src" / "lm34.md"
JS = ROOT / "src" / "lm34.js"
ANCHORS = ROOT / "plans" / "vol-6-anchors.md"
RAW = MD.read_text(encoding="utf-8")
K = C.KEEP
RULES = V.RULES


# ====================================================================== text helpers
def norm_text(s: str) -> str:
    """The module text with TeX thousands separators, escaped percent and dollar signs, \\text{} and minus signs
    made plain."""
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
    got = format(value, fmt).replace("-", "-")
    print(f"CHECK {label}: {got} (printed {printed})")
    assert got == printed, (label, got, printed)
    assert not tie(value, fmt), ("rounding tie: print more digits", label, value)
    assert not in_md or in_text(printed), f"{label}: {printed!r} not found in src/lm34.md"
    COVERED.add(printed.lstrip("-+"))
    N_CHECKS += 1


def pct(label: str, frac: float, d: int, printed: str, in_md: bool = True) -> None:
    chk(label, 100 * frac, f".{d}f", printed, in_md)


def chks(label: str, values: list[float], fmt: str, printed: list[str]) -> None:
    for k, (v, p) in enumerate(zip(values, printed, strict=True)):
        chk(f"{label} [{k + 1}]", float(v), fmt, p)


def has(label: str, text: str) -> None:
    global N_CHECKS
    assert text in TEXT or text in RAW, f"{label}: {text!r} not found in src/lm34.md"
    print(f"CHECK {label}: '{text[:80]}' in text")
    for num in re.findall(r"\d[\d,]*\.?\d*", text):
        COVERED.add(num.rstrip(".,"))
    N_CHECKS += 1


def sci(label: str, value: float, printed: str) -> None:
    """printed is the TeX in the module, m\\times10^{e}; the value must round to m at m's digits."""
    global N_CHECKS
    m = re.fullmatch(r"([\d.]+)\\times10\^\{(-?\d+)\}", printed)
    assert m, printed
    mant, ex = m.group(1), int(m.group(2))
    digits = len(mant.split(".")[1]) if "." in mant else 0
    got = f"{value / 10**ex:.{digits}f}"
    assert got == mant, (label, got, printed)
    assert printed in RAW, f"{label}: {printed!r} not found in src/lm34.md"
    print(f"CHECK {label}: {value:.3e} (printed {printed})")
    COVERED.add(mant)
    N_CHECKS += 1


# ====================================================================== part 1: the anchors and the grid file
def _anchor_values() -> dict[str, str]:
    rows: dict[str, str] = {}
    sec = ANCHORS.read_text(encoding="utf-8").split("\n## LM34", 1)[1].split("\n## ", 1)[0]
    for line in sec.splitlines():
        if line.startswith("| A34-"):
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
            rows[cells[0]] = cells[3].strip("`").replace("\\|", "|")
    return rows


ANCHOR_ROWS = _anchor_values()
assert len(ANCHOR_ROWS) == 38, len(ANCHOR_ROWS)
assert len(C.OUT) == 38
for line in C.OUT:
    aid, got = line.split(" ", 1)
    ok = got == ANCHOR_ROWS[aid]
    print(f"ANCHOR {aid}: {'ok' if ok else 'DIFFERS'}")
    if not ok:
        ANCHOR_DIFFS.append(f"{aid}:\n      script {got}\n      anchor {ANCHOR_ROWS[aid]}")

G = K["grid"]
case = K["case"]
fr = case.fr
X = np.asarray(G["X"], dtype=np.float64)
cols = [f"{k}_{q}m" if w == 0 else f"{k}_{w}_{q}m" for k, w, q in G["conf"]]
assert len(cols) == 60 == X.shape[1] and len(set(cols)) == 60 and X.shape[0] == 1851
first_w = np.asarray(K["grid_first"], dtype=np.float64)
assert len(first_w) == 60 and case.paths["R1"].dates[0] == "2019-03-04"
XF = np.vstack([first_w - 1, X])
grid_df = pl.DataFrame({"date": [case.paths["R1"].dates[0], *G["dates"]],
                        **{c: XF[:, i] for i, c in enumerate(cols)}})
assert grid_df.height == 1852 and grid_df.width == 61 and grid_df["date"][1] == "2019-03-05"
assert np.abs(np.log1p(XF).sum(axis=0) / case.ev_years - np.asarray(G["growth"])).max() < 1e-12
(ROOT / "data" / "processed").mkdir(exist_ok=True)
grid_df.write_parquet(ROOT / "data" / "processed" / "lm34_grid.parquet")
print(f"wrote data/processed/lm34_grid.parquet ({grid_df.height} rows, {grid_df.width} columns: date and 60 "
      "configurations; the first row is the first purchase)")

# ====================================================================== part 2: the text
summ, gsum, paths = K["summ"], K["gsum"], case.paths
tau = case.ev_years
gr = {k: float(summ[k]["growth"]) for k in RULES}
gg = {k: float(gsum[k]["growth"]) for k in RULES}

# ---------------------------------------------------------------- frames, schedule (notation note, Section 2)
chk("T", len(fr.est_dates), ",d", "2,362")
chk("A", fr.A, ".2f", "242.95")
chk("wealth sessions", len(fr.wealth_dates), ",d", "2,368")
chk("A_w", fr.A_wealth, ".2f", "243.57")
chk("daily returns", K["n_days"], ",d", "1,851")
chk("tau", tau, ".4f", "7.5975")
assert paths["R1"].dates[0] == "2019-03-04" and paths["R1"].dates[1] == "2019-03-05"
assert paths["R1"].dates[-1] == "2026-10-08"
has("year convention", "Years count calendar days ÷ 365.25:")
has("tau's span", "years from the close of 4 March 2019 to 8 October 2026")
sigs = case.sigs
assert (sigs[0].signal, sigs[0].trade, sigs[-1].signal, sigs[-1].trade) == ("2019-02-27", "2019-03-04", "2026-09-30",
                                                                         "2026-10-01")
has("first and last signal", "The first signal, 27 February 2019, traded on 4 March, and the last, 30 September "
    "2026, on 1 October.")
assert len(sigs) == 92 and V.WINDOW == 504
has("window", "the trailing 504 joint dates of the estimation frame")
has("rolling window", "each signal uses only the latest 504 joint dates, where an expanding window keeps all earlier "
    "dates")
has("TPEx session", "(Business Rules, Art. 40; ETF rules, Art. 4 ¶2)")
# Section 2's LM26 paragraph, against the published LM26 (its Section 7)
has("LM26 paragraph", "[[LM26]] scored six forecasts out of sample by QLIKE (26.8), but named the best on the same "
    "4,609 days.")
has("13:30", "known only after 13:30")
has("fixed on", "fixed on 24 October 2026")

# ---------------------------------------------------------------- the case, X1 and the overview
pct("R3 growth", gr["R3"], 2, "8.70")
pct("R2 growth", gr["R2"], 2, "14.49")
pct("R4 growth", gr["R4"], 2, "10.51")
growth = G["growth"]
order = G["order"]
pct("grid best", growth[order[0]], 2, "18.62")
pct("grid second", growth[order[1]], 2, "17.38")
pct("grid median", G["med"], 2, "10.96")
pct("grid worst", growth[order[-1]], 2, "7.60")
name = G["name"]
assert (name[order[0]], name[order[1]], name[order[-1]]) == ("R4 252 6m", "R4 126 6m", "R7 126 1m")
med_i = [i for i in range(60) if growth[i] == G["med"]]
assert name[med_i[0]] == "R3 126 6m"
ranks = {k: order.index(i) + 1 for k, i in zip(RULES, G["tcase"], strict=True)}
assert (ranks["R4"], ranks["R2"]) == (39, 8)
has("X1 R4 row", "| R4 as fixed in advance, growth (rank of 60) | 504 dates, monthly | 10.51% (39) |")
has("X1 R2 row", "| R2 as fixed in advance, growth (rank of 60) | monthly | 14.49% (8) |")
has("X1 best row", "| The grid's best, growth | R4, 252 dates, every 6 month-ends | 18.62% |")
has("X1 second row", "| Second, growth | R4, 126 dates, every 6 month-ends | 17.38% |")
has("X1 median row", "| Median, growth | R3, 126 dates, every 6 month-ends | 10.96% |")
has("X1 worst row", "| Worst, growth | R7, 126 dates, monthly | 7.60% |")
chk("PBO", G["pbo"], ".3f", "0.663")
chk("reality-check p (grid)", G["p_rc"], ".3f", "0.375")
chk("its MC SE", math.sqrt(G["p_rc"] * (1 - G["p_rc"]) / C.B_RC), ".4f", "0.0048")
has("X1 reality-check row", "| 59 differences; studentized, $B=10{,}000$, `default_rng([4, 20261011])` | 0.375 (MC SE "
    "0.0048) |")
all6, sur6 = K["all6"], K["sur6"]
pct("all six", all6 - 1, 1, "-27.7")
pct("survivors", sur6 - 1, 1, "5.4")
has("X1 futures row", "| all six; the four survivors | −27.7%; +5.4% |")
assert len(G["conf"]) == 60 and len(G["oth"]) == 59
has("case: configurations", "That gives 60 configurations.")
has("case: windows", "(126, 252 or 504 joint dates)")
nd = sum(1 for s in C.FUTURES6 if s in K["dld"])
assert nd == 2 and len(C.FUTURES6) == 6
has("case: delisted", "Of the six gold, oil and VIX futures funds trading in January 2017, two were delisted.")
has("overview: t-stat", "with a t-stat of 3.97, is what chance gives: its p-value is 0.283")
has("overview: R4 gap", "(34.1): 0.0422 for R4, or 0.56 points of growth a year")
has("overview: grid reality check", "yet no configuration's mean beats R1's beyond chance: the reality check's p-value "
    "for the largest t-stat is 0.375")
has("case question", "And could the search alone have produced 18.62%?")
has("overview: adjusted", "72.30, reads 13.25 in a series built on 8 October 2026")
has("overview: noise PBO", "it averages 0.50 and ranges from 0.12 to 0.87")
has("overview: 1.17", "over 920 days has a median annualized Sharpe ratio of 1.17 by (21.9)")

# ---------------------------------------------------------------- E1 netresults and X2
wealth = {k: float(paths[k].wealth[-1]) for k in RULES}
w4 = {k: f"{wealth[k]:.4f}" for k in RULES}
assert list(w4.values()) == ["2.6620", "3.0079", "1.9367", "2.2214", "2.0400", "2.2722", "2.1829", "2.4119"]
NAMES = {"R1": "equal weights", "R2": "reference mix", "R3": "minimum variance", "R4": "maximum Sharpe",
         "R5": "shrunk minimum variance", "R6": "equal risk", "R7": "HRP", "R8": "volatility target"}
for k in RULES:
    row = (f"| {k} {NAMES[k]} | {w4[k]} | {100 * gr[k]:.2f} | {100 * gg[k]:.2f} | {summ[k]['turnover']:.2f} | "
           f"{100 * summ[k]['costs']:.2f} |")
    has(f"E1 row {k}", row)
    chk(f"E1 growth {k} from printed wealth", 100 * math.log(float(w4[k])) / 7.5975, ".2f", f"{100 * gr[k]:.2f}")
    chk(f"E1 growth {k} from printed wealth and tau", 100 * math.log(float(w4[k])) / tau, ".2f", f"{100 * gr[k]:.2f}")
    assert not tie(100 * gg[k], ".2f") and not tie(summ[k]["turnover"], ".2f") and not tie(100 * summ[k]["costs"], ".2f")
assert len(paths["R1"].trades) == 92
rank_net = sorted(RULES, key=lambda k: -gr[k])
assert " > ".join(rank_net) == "R2 > R1 > R8 > R6 > R4 > R7 > R5 > R3"
has("E1 ranking", "The ranking R2 > R1 > R8 > R6 > R4 > R7 > R5 > R3 puts the two rules without estimates first")
has("E1 R1 growth", r"$\ln2.6620/7.5975=12.89\%$")
assert all(p.ruin is None and float(np.min(p.wealth)) > 0 for p in paths.values())
assert all(p.ruin is None for p in K["gross"].values())
has("no ruin", "No path reaches wealth 0.")
has("KC2 R2 growth", r"$\ln3.0079/7.5975=14.49\%$")
has("X2 quiet finals", "ending at 1.937, 2.040, 2.272 and 2.183")
assert [f"{wealth[k]:.3f}" for k in ("R3", "R5", "R6", "R7")] == ["1.937", "2.040", "2.272", "2.183"]
spec2 = json.loads((ROOT / "src" / "data" / "lm34-wealth.json").read_text(encoding="utf-8"))
assert [s.get("endLabel") for s in spec2["series"] if "endLabel" in s] == ["R1 2.662", "R2 3.008", "R4 2.221",
                                                                         "R8 2.412"]
assert all(len(s["y"]) == len(spec2["x"]["values"]) <= 1172 for s in spec2["series"])

# ---------------------------------------------------------------- Section 3: costs
has("commission rate", "| Commission, each side | 0.1425% | 0050, 00646, 00635U, 00642U | TWSE Operating Rules, Art. 94 |")
has("TPEx commission", "| 00679B | TPEx Business Rules, Art. 64, through its ETF rules, Art. 15 ¶1 |")
has("ruling", "台財稅字第09700161260號 (11 August 2008)")
assert V.COMMISSION == 0.001425 and V.TAX == {"0050": 0.001, "00646": 0.001, "00679B": 0.0, "00635U": 0.001,
                                              "00642U": 0.001}
std = K["first_std"]
pct("first purchase", std, 4, "0.1423")
pct("first purchase from printed", 0.001425 / 1.001425, 4, "0.1423")
has("first purchase formula", r"$0.001425/1.001425=0.1423\%$")
l8, to8, c8 = K["first_r8"]
assert l8 < 1 and c8 < std
has("switch", "Switching NT$1,000,000 from 0050 into 00679B costs about NT$3,850, and back about NT$2,850")
assert round(1e6 * (2 * V.COMMISSION + V.TAX["0050"])) == 3850 and round(1e6 * 2 * V.COMMISSION) == 2850
to1, co1 = K["r1_to"], K["r1_cost"]
assert len(to1) == 91
pct("R1 mean TO", float(np.mean(to1)), 2, "1.96")
pct("R1 largest TO", float(np.max(to1)), 2, "8.06")
pct("R1 mean cost", float(np.mean(co1)), 4, "0.0073")
pct("R1 costs", summ["R1"]["costs"], 2, "0.81")
pct("R4 costs", summ["R4"]["costs"], 2, "4.22")
pct("R2 costs", summ["R2"]["costs"], 2, "0.64")
tax_share = {k: 1 - K["comm"][k] / summ[k]["costs"] for k in RULES}
pct("tax share low", min(tax_share.values()), 0, "17")
pct("tax share high", max(tax_share.values()), 0, "22")
has("tax share", "The tax is 17% to 22% of each rule's costs.")
lg1 = math.log(K["gross"]["R1"].wealth[-1] / paths["R1"].wealth[-1])
lg4 = math.log(K["gross"]["R4"].wealth[-1] / paths["R4"].wealth[-1])
chk("R1 log gap", lg1, ".7f", "0.0080768")
chk("R1 cost sum", summ["R1"]["costs"], ".7f", "0.0080755")
chk("R4 log gap", lg4, ".7f", "0.0422296")
chk("R4 cost sum", summ["R4"]["costs"], ".7f", "0.0422153")
chk("R4 log gap (overview, four decimals)", lg4, ".4f", "0.0422")
# Problem 2's options: the gap (A), the cost sum (B) and C's slip, the sum of x - x^2/2 (the x^2/2 term's sign flipped)
x1 = np.array([t.cost for t in paths["R1"].trades])
assert len(x1) == 92 and abs(x1.sum() - summ["R1"]["costs"]) < 1e-15
assert abs(-np.log1p(-x1).sum() - lg1) < 1e-14
chk("P2 C: sum of x - x^2/2", float((x1 - x1**2 / 2).sum()), ".7f", "0.0080741")
has("P2 options", "It is larger, 0.0080768, as $-\\ln(1-x)>x$.")
has("P2 option B", "It equals the sum, 0.0080755, as the costs are scale-free.")
has("P2 option C", "It is smaller, 0.0080741, as $-\\ln(1-x)\\approx x-x^2/2$.")
has("S2", "B mistakes the bound for an equality, and C has the wrong sign on $x^2/2$.")
assert K["ident"] < 2e-14
has("identity bound", r"to below $2\times10^{-14}$")
chk("R4 gap a year (KC 3)", 100 * (gg["R4"] - gr["R4"]), ".2f", "0.56")
chk("R4 cost sum over tau, printed", 100 * 0.0422 / 7.5975, ".2f", "0.56")
chk("R4 log gap over tau, printed", 100 * 0.0422296 / 7.5975, ".2f", "0.56")
pct("R4 gross (KC 3)", gg["R4"], 2, "11.06")
chk("R4 gap from printed parts", 11.06 - 10.51, ".2f", "0.55", in_md=False)   # why the KC says "separately"
has("KC3 note", "[[ex:grossnet]]'s 11.06% and 10.51% are rounded separately")
twice = {k: float(K["twice"][k]["growth"]) for k in RULES}
pct("R4 twice", twice["R4"], 2, "9.95")
chk("R4 twice change", 100 * (gr["R4"] - twice["R4"]), ".2f", "0.56")
chk("R4 twice change from printed", 10.51 - 9.95, ".2f", "0.56")
assert twice["R4"] < twice["R7"] and gr["R4"] > gr["R7"]
pct("R1 twice", twice["R1"], 2, "12.78")
chk("R1 twice change", 100 * (gr["R1"] - twice["R1"]), ".2f", "0.11")
chk("R1 twice change from printed", 12.89 - 12.78, ".2f", "0.11")
assert " > ".join(sorted(RULES, key=lambda k: -twice[k])) == "R2 > R1 > R8 > R6 > R7 > R4 > R5 > R3"
has("twice ranking", "The order becomes R2 > R1 > R8 > R6 > R7 > R4 > R5 > R3.")
ex8 = K["r8_exposure"]
assert sum(v > 1 + C.EPS for v in ex8) == 62 and len(ex8) == 92
has("R8 borrows", "R8 borrows at 62 of its 92 trades ([[LM31]])")
assert abs(V.RF + V.SPREAD - 0.035) < 1e-15
s0, s2, s5 = K["r8_spreads"]
pct("R8 spread 0", s0, 2, "11.99")
pct("R8 spread 2", s2, 2, "11.59")
pct("R8 spread 5", s5, 2, "10.99")
pct("R8 gross", gg["R8"], 2, "11.99")
assert s0 != gg["R8"]
has("spreads", "At spreads of 0, 2 and 5 points it grows 11.99%, 11.59% and 10.99%.")
rf0, rf2 = K["rf_0"], K["rf_0.02"]
pct("R4 rf 0", rf0["R4"], 2, "10.88")
pct("R4 rf 2", rf2["R4"], 2, "10.31")
pct("R8 rf 0", rf0["R8"], 2, "11.79")
pct("R8 rf 2", rf2["R8"], 2, "11.52")
assert rf0["R4"] > gr["R6"] and rf0["R4"] < gr["R1"]
has("rf sentence", "At 0% or 2% R4 grows 10.88% or 10.31% and R8 11.79% or 11.52%.")
gn_parts = [100 * (gg[k] - gr[k]) for k in RULES]
chk("gross minus net low (R2)", min(gn_parts), ".2f", "0.08")
chk("gross minus net high (R4)", max(gn_parts), ".2f", "0.56")
has("Section 8 costs cell", "0.08 to 0.56 points a year")

# ---------------------------------------------------------------- Section 4: adjusted prices and the same close
c50, d50, adj = K["c50"], K["d50"], K["adj50"]
i17 = K["i17"]
chk("0050 close 2017-01-17", float(c50[i17]), ".2f", "72.30")
chk("adjusted 2020", adj("2017-01-17", "2020-01-02"), ".2f", "65.12")
chk("adjusted 2024", adj("2017-01-17", "2024-12-31"), ".2f", "55.20")
chk("adjusted 2026", adj("2017-01-17", "2026-10-08"), ".2f", "13.25")
has("X4 close row", "| Close of 17 January 2017 | 72.30 | 65.12 | 55.20 | 13.25 |")
assert sum(1 for d in K["div50"] if "2017-01-17" < d <= "2026-10-08") == 20
has("20 distributions", "after 20 distributions and the 4-for-1 split of 18 June 2025")
assert K["ex17"] == ["2017-02-08", "2017-07-31"] and K["end17"] == "2017-12-29"
assert (K["div50"]["2017-02-08"], K["div50"]["2017-07-31"]) == (1.70, 0.70)
ya, yj = K["y_act"], K["y_adj"]
pct("Feb yield actual", ya[0], 2, "2.32")
pct("Jul yield actual", ya[1], 2, "0.85")
pct("Feb yield adjusted", yj[0], 2, "12.65")
pct("Jul yield adjusted", yj[1], 2, "4.54")
pct("2017 yield actual", K["ttm_act"], 2, "2.92")
pct("2017 yield adjusted", K["ttm_adj"], 2, "15.44")
has("X4 Feb row", "| NT$1.70 of 8 February over the previous close | 2.32% | — | — | 12.65% |")
has("X4 Jul row", "| NT$0.70 of 31 July over the previous close | 0.85% | — | — | 4.54% |")
has("X4 year row", "| Both over the close of 29 December 2017 | 2.92% | — | — | 15.44% |")
# returns from every adjusted series equal the total returns (34.2): check on three build dates
cum = K["cum50"]
for built in ("2020-01-02", "2024-12-31", "2026-10-08"):
    j = d50.index(built)
    adj_s = c50[j] / (cum[j] / cum[: j + 1])
    tr = cum[1: j + 1] / cum[:j]
    assert np.abs(adj_s[1:] / adj_s[:-1] - tr).max() < 1e-12, built
sc = K["same_close"]
pct("same close R1", sc["g"]["R1"], 2, "13.14")
pct("same close R2", sc["g"]["R2"], 2, "14.59")
pct("same close R4", sc["g"]["R4"], 2, "10.09")
pct("same close R8", sc["g"]["R8"], 2, "12.48")
chg = {k: 100 * (sc["g"][k] - gr[k]) for k in RULES}
chk("same close low (R4)", min(chg.values()), ".2f", "-0.41")
chk("same close high (R8)", max(chg.values()), ".2f", "0.89")
assert min(chg, key=lambda k: chg[k]) == "R4" and max(chg, key=lambda k: chg[k]) == "R8" and sc["gain"] == 7
chk("same close R4 change from printed (why 'from unrounded')", 10.09 - 10.51, ".2f", "-0.42", in_md=False)
has("same close wording", "From unrounded values, the changes run from −0.41 points (R4) to +0.89 (R8), and seven "
    "of the eight rules gain.")
assert max(abs(v) for v in chg.values()) < 1.0          # "less than a point a year"
has("same close size", "For monthly rules the shift moves growth by less than a point a year.")
has("KC4 numbers", "yield 15.44% of the year-end close, against 2.92% on the actual close")

# ---------------------------------------------------------------- Section 5: survivorship
chk("ETFs 2017", K["n2017"], "d", "69")
chk("gone by 2026", len(K["gone"]), "d", "10")
assert all(g in K["dld"] for g in K["gone"])
chk("all six mean", all6, ".4f", "0.7234")
chk("survivors mean", sur6, ".4f", "1.0539")
y17 = K["years17"]
chk("years 2017", y17, ".4f", "9.7221")
pct("all six log growth", math.log(all6) / y17, 2, "-3.33")
pct("survivors log growth", math.log(sur6) / y17, 2, "0.54")
chk("gap", 100 * (math.log(sur6) - math.log(all6)) / y17, ".2f", "3.87")
chk("all six log growth from printed", 100 * math.log(0.7234) / 9.7221, ".2f", "-3.33")
chk("survivors log growth from printed", 100 * math.log(1.0539) / 9.7221, ".2f", "0.54")
chk("gap from printed", 100 * math.log(1.0539 / 0.7234) / 9.7221, ".2f", "3.87")
has("E6 means", "grew to 0.7234, or −27.7% (log growth −3.33% a year), and in the four survivors to 1.0539, or "
    "+5.4% (+0.54% a year)")
g6 = K["g6"]
f3 = {s: f"{g6[s][0]:.3f}" for s in C.FUTURES6}
assert list(f3.values()) == ["2.198", "1.593", "0.038", "0.140", "0.285", "0.086"]
p6, p4 = sum(float(v) for v in f3.values()) / 6, sum(float(f3[s]) for s in C.FUTURES6 if s not in K["dld"]) / 4
chk("printed factors' mean, all six", p6, ".4f", "0.7233")
chk("printed factors' mean, survivors", p4, ".4f", "1.0540")
chk("problem 10 gap", 100 * math.log(p4 / p6) / 9.7221, ".2f", "3.87")
chk("problem 10 gap from printed means", 100 * math.log(1.0540 / 0.7233) / 9.7221, ".2f", "3.87")
has("S10 all six", "$(2.198+1.593+0.038+0.140+0.285+0.086)/6=0.7233$")
has("S10 survivors", "$(2.198+1.593+0.140+0.285)/4=1.0540$")
assert (g6["00672L"][1], K["dld"]["00672L"], K["dld"]["00677U"]) == ("2020-11-12", "2020-11-13", "2021-06-03")
has("X5 delisting dates", "00672L was delisted on 13 November 2020 and 00677U on 3 June 2021")
has("KC5 answer", "It last traded on 12 November 2020 and was delisted the next day, with growth factor $G=0.038$.")
assert set(K["dld"]) & set(C.FUTURES6) == {"00672L", "00677U"}
has("multiples", "00672L +2× crude oil, 00673R −1× crude oil and 00674R −1× gold")
has("multiples (box)", "單日正向兩倍或反向一倍")
has("KC5 stem", "E5 holds 00642U, an oil futures ETF. Which oil futures fund with a row on 17 January 2017 did not "
    "survive?")
assert "00642U" not in K["dld"] and "00642U" in C.FUTURES6       # 00642U survived

# ---------------------------------------------------------------- Section 6: the reality check
rc = K["rc10"]
tt, best = rc["tt"], rc["best"]
chk("best t-stat", float(tt[best]), ".4f", "3.9738")
chk("best t-stat (LM21)", float(tt[best]), ".2f", "3.97")
sci("one-sided p", rc["p1"], r"3.54\times10^{-5}")
chk("Bonferroni", 10_000 * rc["p1"], ".3f", "0.354")
chk("Bonferroni from printed", 10_000 * 3.54e-5, ".3f", "0.354")
chk("(21.9)", 1 - stats.norm.cdf(float(tt[best])) ** 10_000, ".3f", "0.298")
chk("(21.9) from printed", 1 - (1 - 3.54e-5) ** 10_000, ".3f", "0.298")
has("E7 Bonferroni", r"$10{,}000\times3.54\times10^{-5}=0.354$")
has("E7 Bonferroni's tag", "Bonferroni's bound (21.6) is")
has("Section 6 recap", "by (21.9) for independent rules.")
assert "Bonferroni" not in RAW.split("[[LM21]]'s Experiment 10 judged", 1)[1].split("\n", 1)[0]   # LM21 uses (21.9)
has("White's moment", "a finite moment of order $6+\\varepsilon$")
has("White's mixing rate", "exceeds $3(6+\\varepsilon)/\\varepsilon$")
has("Sullivan et al.", "on 100 years of daily Dow Jones data (their abstract)")
has("scope: other tests", "Other data-snooping tests are not covered, and Harvey, Liu and Zhu's hurdle of 3 is "
    "[[LM21]]'s.")
has("E7 (21.9)", r"$1-(1-3.54\times10^{-5})^{10{,}000}=0.298$")
assert round(float(rc["pw"].max())) == 145 == C.ELL_TR23
chk("largest block estimate", float(rc["pw"].max()), ".2f", "145.44")
chk("White p", rc["p_white"], ".3f", "0.283")
chk("studentized p", rc["p_stud"], ".3f", "0.281")
for p_ in (rc["p_white"], rc["p_stud"], rc["p_spa"]):
    chk("its MC SE", math.sqrt(p_ * (1 - p_) / C.B_RC), ".4f", "0.0045")
chk("bootstrap 95% point", rc["q95"], ".2f", "4.77")
assert int((tt > rc["q95"] + C.EPS).sum()) == 0
chk("(21.9) 95% point", rc["q95_219"], ".2f", "4.41")
chk("SPA recentred", rc["keep"], ",d", "9,814")
chk("SPA threshold", -rc["thr"], ".3f", "-2.079")
chk("SPA p", rc["p_spa"], ".3f", "0.277")
has("SPA sentence", "On Experiment 10 that threshold is −2.079, so it recentres 9,814 rules")
assert rc["p_spa"] == rc["p_spa_strict"]
chk("Experiment 10 days", rc["T"], ",d", "5,849")
assert C.B_RC == 10_000
jb = G["jb"]
chk("grid best t", float(G["tg"][jb]), ".3f", "1.296")
assert name[G["oth"][jb]] == "R4 126 6m"
chk("grid one-sided p", G["p1"], ".4f", "0.0975")
chk("grid one-sided p from printed", float(stats.norm.sf(1.296)), ".4f", "0.0975")
assert 59 * 0.0975 > 1 and 59 * G["p1"] > 1
has("E8 Bonferroni", "so Bonferroni's bound is 1")
chk("grid block estimate", max(G["pwd"]), ".2f", "74.63")
assert G["ell"] == 75.0 and name[G["oth"][int(np.argmax(G["pwd"]))]] == "R4 126 1m"
chk("R1's own estimate (rounded)", G["pw_r1"], ".0f", "17")
chk("p at 17", G["p_rc17"], ".3f", "0.421")
chk("its MC SE at 17", math.sqrt(G["p_rc17"] * (1 - G["p_rc17"]) / C.B_RC), ".4f", "0.0049")
has("E8 seeds", "the studentized reality check ($B=10{,}000$, `default_rng([4, 20261011])`) 0.375 (MC SE 0.0048)")
has("E8 seed at 17", "`default_rng([5, 20261011])` gives 0.421 (MC SE 0.0049)")
has("P11 seeds", "at $\\ell=75$ (`default_rng([4, 20261011])`) and 17 (`default_rng([5, 20261011])`)")
has("Section 9 seed", "`ell=75`, `B=10000` and `default_rng([4, 20261011])` give [[eg:rcgrid]]'s 0.375")
chk("grid 95% point", G["q95"], ".2f", "2.42")
chk("Bonferroni's 95% point", G["bonf"], ".2f", "3.14")
chk("median correlation", float(np.quantile(G["corr"], 0.5, method="inverted_cdf")), ".2f", "0.78")

# ---------------------------------------------------------------- Section 7: PBO
# the declaration as printed: trades per frequency, the grid order, the degradation statistics
for q, printed in ((1, "92"), (3, "31"), (6, "16")):
    chk(f"trades every {q} month-end signals", len(sigs[::q]), "d", printed)
has("declared trades", "signals 1, $1+q$, $1+2q$, … (92, 31 and 16 trades)")
conf_order = [(k, 0, q) for k in ("R1", "R2") for q in (1, 3, 6)]
conf_order += [(k, w, q) for k in RULES[2:] for w in (126, 252, 504) for q in (1, 3, 6)]
assert G["conf"] == conf_order
has("declared grid order", "| Grid order | R1 1m, 3m, 6m; R2 1m, 3m, 6m; then R3 … R8, each by window 126, 252, 504 and "
    "frequency 1, 3, 6 |")
has("declared degradation", "| Degradation | the OLS slope of $k^*$'s out-of-sample Sharpe ratio on its in-sample one; "
    "the share of splits with an out-of-sample ratio below 0 |")
has("declared window", "| Window | 126, 252 or 504 joint dates through the signal; none for R1 and R2 |")
has("scope: overlapping returns", "Daily returns do not overlap, so cross-validation that removes overlaps is not "
    "needed.")
assert G["m"] == 115 and G["drop"] == 11 and len(G["lg"]) == math.comb(16, 8) == 12_870
has("E9 blocks", "The 1,851 days give 16 blocks of 115, the 11 earliest days dropped, and 12,870 splits.")
chk("splits at or below 0", int((G["lg"] <= C.EPS).sum()), ",d", "8,530")
chk("logit median", float(np.quantile(G["lg"], 0.5, method="inverted_cdf")), ".2f", "-0.72")
cnt = G["cnt"]
top = G["top"]
assert [name[i] for i in top] == ["R2 - 1m", "R4 252 6m", "R4 126 6m"]
pct("top 1", cnt[top[0]] / 12_870, 1, "19.1")
pct("top 2", cnt[top[1]] / 12_870, 1, "18.8")
pct("top 3", cnt[top[2]] / 12_870, 1, "13.8")
chk("distinct bests", int((cnt > 0).sum()), "d", "31")
chk("logit min", float(G["lg"].min()), ".2f", "-4.09")
chk("logit max", float(G["lg"].max()), ".2f", "3.38")
aw = fr.A_wealth
chk("IS mean", float(np.mean(G["is"])) * math.sqrt(aw), ".2f", "1.31")
chk("OOS mean", float(np.mean(G["oos"])) * math.sqrt(aw), ".2f", "0.80")
chk("slope", G["slope"], ".2f", "-0.86")
chk("intercept", G["icept"], ".2f", "1.93")
pct("OOS below 0", G["neg"] / 12_870, 2, "0.99")
chk("C(15, 7)", math.comb(15, 7), ",d", "6,435")
has("Pascal", r"$$\begin{aligned}\binom{16}{8}&=\binom{15}{7}+\binom{15}{8}\\&=6{,}435+6{,}435=12{,}870,"
    r"\end{aligned}$$")
has("misprint", "(the manuscript prints 12,780)")
nz = K["noise"]
chk("noise panels", len(nz["pb"]), "d", "200")
chk("noise PBO", nz["mean"], ".2f", "0.50")
chk("noise PBO SE", nz["se"], ".3f", "0.012")
chk("noise min", min(nz["pb"]), ".2f", "0.12")
chk("noise max", max(nz["pb"]), ".2f", "0.87")
chk("noise IS", nz["is"], ".2f", "1.20")
chk("noise IS SE", nz["se_is"], ".3f", "0.007")
chk("noise OOS", nz["oos"], ".2f", "-0.00", in_md=False)
assert abs(nz["oos"]) < 0.005
has("noise OOS printed", "0.00 (SE 0.016)")
chk("noise OOS SE", nz["se_oos"], ".3f", "0.016")
assert nz["half"] == 920
chk("(21.9) median", nz["median_219"], ".2f", "1.17")
chk("(21.9) median from printed A_w", stats.norm.ppf(0.5 ** (1 / 60)) * math.sqrt(243.57 / 920), ".2f", "1.17")
chk("z of the median", nz["z_med"], ".3f", "2.274")
chk("1.17 from printed z", 2.274 * math.sqrt(243.57 / 920), ".2f", "1.17")
chk("(21.9) mean", nz["mean_219"], ".2f", "1.19")
has("derivation display", r"$$\Phi^{-1}(0.5^{1/60})\sqrt{A_{\mathrm w}/920}=1.17,$$")
wg = K["widget"]
chk("widget n=60, ratio 0", wg[(60, 0.0)][0], ".2f", "0.51")
chk("widget n=60, ratio 2", wg[(60, 2.0)][0], ".2f", "0.05")
chk("widget SE, n=60, ratio 0", wg[(60, 0.0)][1], ".3f", "0.026")
chk("widget SE, n=60, ratio 2", wg[(60, 2.0)][1], ".3f", "0.010")
has("widget readout", "is 0.51 (SE 0.026) at $n=60$ without skill and 0.05 (SE 0.010) at a ratio of 2")
assert C.N_STATE == 40
js = JS.read_text(encoding="utf-8")
assert "so with no skill the expected PBO is (n + 1)/(2n): 0.6 at n = 5." in js and (5 + 1) / (2 * 5) == 0.6
assert f"{wg[(5, 0.0)][0]:.2f}" == "0.65"
chk("logit j=30", math.log(30 / 31), ".4f", "-0.0328")
chk("logit j=31", math.log(31 / 30), ".4f", "0.0328")
chk("logit j=60", math.log(60), ".3f", "4.094")
chk("logit j=1", math.log(1 / 60), ".3f", "-4.094")
chk("n + 1 (KC 7)", 60 + 1, "d", "61")
has("KC7 logits", "The logits are $\\ln(j/(61-j))$ for $j=1,\\dots,60$")
# Problem 4: rank 45 of 60 out of sample (1 = worst); B counts from the best, C takes the in-sample rank 60
chk("P4 key", math.log(45 / 16), ".3f", "1.034")
chk("P4 B", math.log(16 / 45), ".3f", "-1.034")
chk("P4 rank from the best", 61 - 45, "d", "16")
has("P4 stem", "the in-sample best ranks 45th of 60 out of sample (1 = worst)")
has("S4", "$\\omega=45/61$, so the logit is $\\ln(45/16)=1.034$. B counts the rank from the best, $j=16$, and C uses "
    "the in-sample rank, 60.")
chk("2^16", 2**16, ",d", "65,536")
chk("extension: the eight rules every 12 signals", len(RULES), "d", "8")
chk("extension: n", 60 + len(RULES), "d", "68")
assert len(sigs[::12]) == 8                          # its 8 trades (A34-26); the lab builds it
has("extension", "The lab's extension adds 8, declared after the grid's results were seen, so it counts $n=68$.")

r1g = [g for c, g in zip(G["conf"], growth, strict=True) if c[0] == "R1"]
r4g = [g for c, g in zip(G["conf"], growth, strict=True) if c[0] == "R4"]
pct("R1's configurations, low", min(r1g), 2, "12.85")
pct("R1's configurations, high", max(r1g), 2, "12.96")
pct("R4's configurations, low", min(r4g), 2, "10.51")
pct("R4's configurations, high", max(r4g), 2, "18.62")
has("R1 range", "R4's configurations start at 10.51%, while R1's three span 12.85% to 12.96%.")
has("KC3 fraction", "$0.0422/7.5975$")
pct("tax rate", V.TAX["0050"], 1, "0.1")
pct("cash rate", V.RF, 1, "1.5")
pct("borrowing rate", V.RF + V.SPREAD, 1, "3.5")
chk("resamples", C.B_RC, ",d", "10,000")
has("rounding note", "two printed parts can miss their total by 0.01")
assert any(abs(100 * (round(gg[k], 4) - round(gr[k], 4)) - round(100 * (gg[k] - gr[k]), 2)) > 0.005 for k in RULES)

# ---------------------------------------------------------------- problems 8 and 9 (TR23)
scl = K["scale"]
chk("P8 days", scl["days"], ",d", "5,344")
assert (scl["first"], scl["before"]) == ("2005-01-12", "2005-01-11")
chk("P8 years", scl["years"], ".2f", "21.74")
chk("P8 A", scl["A"], ".2f", "245.83")
gh, vh, mh = scl["honest"]
gp, vp, mp = scl["peek"]
pct("P8 honest growth", gh, 2, "15.08")
pct("P8 honest vol", vh, 2, "18.27")
pct("P8 honest worst", mh, 2, "-7.50")
pct("P8 peek growth", gp, 2, "16.70")
pct("P8 peek vol", vp, 2, "17.04")
pct("P8 peek worst", mp, 2, "-4.93")
pct("P8 7 April (a fall)", -scl["r7"], 2, "9.70")
chk("P8 scale honest", scl["s7"][0], ".3f", "0.703")
chk("P8 scale peek", scl["s7"][1], ".3f", "0.428")
pct("P8 scaled honest", scl["x7"][0], 2, "-6.81")
pct("P8 scaled peek", scl["x7"][1], 2, "-4.15")
# from the printed inputs 9.70% and 0.703 the honest product rounds to 6.82, hence "from unrounded values"
chk("P8 scaled honest from printed (why 'from unrounded values')", 9.70 * 0.703, ".2f", "6.82", in_md=False)
chk("P8 scaled peek from printed", 9.70 * 0.428, ".2f", "4.15")
has("P8 unrounded", "giving −6.81% and −4.15% from unrounded values")
pct("S8 index growth", scl["index"][0], 2, "13.32")
pct("S8 index vol", scl["index"][1], 2, "18.62")
pct("S8 slip", scl["slip"], 2, "14.90")
has("P8 window", "from the 504 daily simple returns through it, with borrowing at 0")
has("problems preamble", "Rules on TR23, the TAIEX total-return index, rebalance daily with $r_f=0$ and no trading "
    "costs.")
kw = K["kelly"]
chk("P9 days", kw["days"], ",d", "5,103")
assert kw["before"] == "2006-01-02" and (kw["first_end"], kw["last_end"]) == ("2005-12-30", "2026-09-30")
chk("P9 years", kw["years"], ".2f", "20.76")
chk("P9 root (LM22's precision)", kw["full"], ".2f", "4.14")
pct("P9 held at 4.14", kw["p414"], 2, "31.70")
pct("P9 held at the unrounded root", kw["full_held"], 2, "31.70", in_md=False)
pct("P9 walk-forward", kw["walk"], 2, "22.27")
pct("P9 f = 1", kw["f1"], 2, "13.38")
pct("P9 4.14 with borrowing", kw["p414_fin"], 2, "20.71")
pct("P9 walk-forward with borrowing", kw["walk_fin"], 2, "16.63")
chk("P9 month-ends", kw["ends"], "d", "250")
chk("P9 at the cap", kw["at_cap"], "d", "178")
assert C.BORROW == 0.035
has("P9 window", "The trailing 729-return root, capped to [0, 3], set at each calendar month-end close and traded at "
    "the next, grows 22.27%")
# the Kelly versions the hygiene note counts: walk-forward, f = 1, the root 4.14 and half of it (the lab), two of them
# also with borrowing
assert {"walk", "f1", "p414", "p207", "walk_fin", "p414_fin"} <= set(kw)
has("hygiene: TR23 versions", "TR23 adds three scales and four Kelly versions, two of them also with borrowing.")
has("S9 protocol", "At each of 250 calendar month-ends from 30 December 2005")

# ---------------------------------------------------------------- Section 8 and the summary
has("Section 8 slip cell", "the slip moves growth by −0.41 to +0.89 points")
has("Section 8 survivorship cell", "survivors alone overstate growth by 3.87 points a year")
has("Section 8 reality-check cell", "| not shown: p-value 0.375 |")
has("Section 8 reading", "No configuration beats R1 beyond chance, so the search alone could have produced the winner")
has("summary: grid", "On E5 no configuration beats R1 beyond chance.")
has("summary: independent", "the in-sample best of $n$ independent strategies has median")
has("S7 derivation", "Both paths hold the same exposures after each trade, so their ratio changes only at trades.")
has("summary survivors", "3.87 points a year among the futures funds of 2017")
has("summary PBO", "0.663 here, about one half without skill")

# ====================================================================== part 3: the printed Python block
block = re.search(r"```python\n(.*?)```", RAW, flags=re.DOTALL)
assert block
code = block.group(1)
assert all(len(line) <= 80 for line in code.splitlines()), "a code line is longer than 80 characters"
ns: dict[str, Any] = {"stationary_idx": C.stationary_idx}
exec(compile(code, "lm34.md", "exec"), ns)   # noqa: S102 - the module's own printed code
rc_fn, cscv_fn = ns["reality_check"], ns["cscv"]
assert callable(rc_fn) and callable(cscv_fn)
p_code = float(rc_fn(np.asarray(G["D"]), 75.0, C.B_RC, np.random.default_rng([4, C.SEED])))
assert p_code == G["p_rc"], (p_code, G["p_rc"])
chk("printed code's reality check", p_code, ".3f", "0.375")
lg_code = np.asarray(cscv_fn(X - V.RF / aw))
assert np.array_equal(lg_code, G["lg"]), float(np.abs(lg_code - G["lg"]).max())
print("printed code: reality_check reproduces 0.3754 and cscv every one of the 12,870 logits exactly")

# ====================================================================== part 4: structure and echoes
ex_labels = re.findall(r"\[!exhibit\][^\n]*\{#([\w-]+)\}", RAW)
eg_labels = re.findall(r"\[!example\][^\n]*\{#([\w-]+)\}", RAW)
assert ex_labels == ["case", "wealth", "grossnet", "adjusted", "survivors", "rc", "bumps", "logits", "degrade"]
assert eg_labels == ["netresults", "costs", "twice", "builddate", "sameclose", "survgap", "rc10", "rcgrid", "pbo",
                     "noise"]
assert len(set(ex_labels) | set(eg_labels)) == 19, "a label is used twice"
for lab in ex_labels:
    assert f"[[ex:{lab}]]" in RAW, f"exhibit {lab} is never cited"
for kind, lab in re.findall(r"\[\[(ex|eg):([\w-]+)\]\]", RAW):
    assert lab in (ex_labels if kind == "ex" else eg_labels), (kind, lab)
tags = re.findall(r"\\tag\{(34\.\d+)\}", RAW)
assert tags == ["34.1", "34.2", "34.3", "34.4"], tags
for nm in re.findall(r'data-chart="(lm34-[\w-]+)"', RAW):
    assert (ROOT / "src" / "data" / f"{nm}.json").exists(), nm
assert len(re.findall(r"^> \[!kc\]", RAW, flags=re.MULTILINE)) == 8
assert len(re.findall(r"^> \[!zh\]", RAW, flags=re.MULTILINE)) == 5
keys = re.findall(r"^\d+\. \*\*([ABC])\*\* is correct", RAW, flags=re.MULTILINE)
assert keys == ["B", "A", "C", "A", "C", "B"], keys
print(f"labels: {len(ex_labels)} exhibits, {len(eg_labels)} examples, tags (34.1)-(34.4), every exhibit cited; "
      f"keys {', '.join(keys)}")
# echoes of published lines (decision C12): each value as the published module prints it
ECHO = [("lm27.md", "0.1423% of the pre-trade wealth"), ("lm27.md", "traded 8.06% of the book"),
        ("lm27.md", "costs about NT\\$2,850"), ("lm27.md", "about NT\\$3,850"),
        ("lm21.md", "the best of all 10,000 is 3.97 (rule 7,840)"), ("lm22.md", "$\\hat f^*=4.14$"),
        ("lm22.md", "145 for TR23"), ("lm26.md", "fell 9.70%"), ("lm31.md", "above 1 at 62"),
        ("lm26.md", "Six forecasts are fixed in advance"), ("lm26.md", "4,609 days"),
        ("lm26.md", "GARCH normal has the lowest QLIKE"), ("lm22.md", "draws the stationary bootstrap in arch's order"),
        ("lm21.md", "Under (21.9) the best of 1,000 has median")]
for f, s in ECHO:
    assert s in (ROOT / "src" / f).read_text(encoding="utf-8"), (f, s)
print(f"echoes: {len(ECHO)} published strings found as printed")

# ====================================================================== report
body = TEXT.split("\n## Glossary", 1)[0]
nums = set(re.findall(r"(?<![\w.])\d+\.\d+|(?<![\w.,])\d{1,3}(?:,\d{3})+", body))
left = sorted(n for n in nums if n not in COVERED)
print(f"\nnumbers with a decimal point or thousands separator not covered by a check ({len(left)}):")
print("   " + " ".join(left))
print(f"anchor differences ({len(ANCHOR_DIFFS)}):")
for a in ANCHOR_DIFFS:
    print("   ", a)
print(f"\nall {N_CHECKS} checks passed")
sys.exit(0)
