"""Every number that LM20 (Estimation Theory and Maximum Likelihood) quotes, computed and checked against src/lm20.md.

Run:  uv run python data/lm20_numbers.py
      (after data/vol3_series.py has built TR23, data/vol2_series.py the U28 closes and data/build_series.py LM4's
      0050 sample; run data/lm20_charts.py first, because the chart files are checked too)

Inputs and conventions: see data/lm20_common.py (TR23, U28, LM4's 0050 sample; divisors passed explicitly; the
Student-t fit and its observed information; Hill's estimator; the guard 1e-12 with Fraction recounts; seeds
np.random.default_rng([e, 20261011]) with e = 1, 2, 3, 4 for the sampling distributions, the coverage table,
Problem 11 and the spread of experiment 1's Student-t block). Quantiles of simulated values are F-hat^{-1}(u)
(np.quantile(..., method="inverted_cdf")) with LM18's batch standard errors (20 batches, divisor 20).

Checks (each stops the script on a failure):
  chk(label, value, fmt, printed)  format(value, fmt) equals the printed string, the value does not sit on a rounding
                                   tie of that format, and the printed string is in the module as a whole number.
                                   A value within a tenth of a unit of the last printed digit of a rounding boundary
                                   is flagged (listed at the end), as plans/vol-4-anchors.md flags its rows. Hand
                                   computations are redone from the printed, rounded inputs (PITFALLS section 7).
  has(label, text)                 a literal string (a table row, a date, a phrase) is in the module.
  in_chart(label, chart, text)     a string is in the chart file src/data/<chart>.json (labels, alt texts).
  anchor(id, label, value, shown)  compares a value with its row in plans/vol-4-anchors.md (the Value column); a
                                   difference is reported, never forced.
The printed code block of Section 9 is run against the lab's data file (or, before data/make_lab_data.py has run,
the same closes written from TR23's parquet to a temporary file) and its comments are checked. At the end the
script lists the flagged values, the anchor differences, the numbers of the module that no check covered, and prints
"all N checks passed".
"""
import json
import math
import re
import sys
import tempfile
from fractions import Fraction
from math import log, sqrt
from pathlib import Path

import numpy as np
from scipy import optimize, stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lm20_common as c

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MD = ROOT / "src" / "lm20.md"
CHARTS = ROOT / "src" / "data"
ANCHORS = ROOT / "plans" / "vol-4-anchors.md"
LAB_DATA = ROOT / "labs" / "LM20_lab" / "data" / "taiex_tr.csv"
Z = c.Z
EPS = c.EPS


def norm_text(s: str) -> str:
    """The module text with TeX thousands separators, escaped percent signs, \\text{} and minus signs made plain."""
    s = s.replace("{,}", ",").replace("\\%", "%").replace("\u2212", "-").replace("\\,", "")
    return re.sub(r"\\text\{\s*([^}]*)\}", r" \1", s)


RAW = MD.read_text(encoding="utf-8")
TEXT = norm_text(RAW)
N_CHECKS = 0
COVERED: set[str] = set()
FLAGGED: list[str] = []
ANCHOR_DIFFS: list[str] = []


def in_text(printed: str, text: str = TEXT) -> bool:
    """The printed number appears as a whole number (2.323 is not inside 2.3235, 0.32 not inside 10.32)."""
    return re.search(r"(?<![\d.])" + re.escape(printed) + r"(?![\d])", text) is not None


def decimals(fmt: str) -> int:
    m = re.search(r"\.(\d+)", fmt)
    return int(m.group(1)) if m else 0


def tie(value: float, fmt: str) -> bool:
    """True when value lies on a rounding boundary of fmt (a reader rounding by hand could go either way)."""
    if fmt.endswith(("e", "g")):
        return False
    scaled = abs(value) * 10 ** decimals(fmt) * (100 if "%" in fmt else 1)
    return abs(scaled - math.floor(scaled) - 0.5) < 1e-6


def near(value: float, fmt: str) -> bool:
    """Within a tenth of a unit of the last printed digit of a rounding boundary (plans/vol-4-anchors.md's flag)."""
    if fmt.endswith(("e", "g")):
        return False
    scaled = abs(value) * 10 ** decimals(fmt) * (100 if "%" in fmt else 1)
    return abs(scaled - math.floor(scaled) - 0.5) < 0.1


def chk(label: str, value: float, fmt: str, printed: str) -> None:
    global N_CHECKS
    got = format(value, fmt)
    ok = got == printed and in_text(printed) and not tie(value, fmt)
    flag = near(value, fmt)
    print(f"CHECK {label}: {got} (printed {printed}) {'ok' if ok else 'MISMATCH'}{' (!)' if flag else ''}")
    assert got == printed, (label, got, printed)
    assert not tie(value, fmt), ("rounding tie: print more digits", label, value)
    assert in_text(printed), f"{label}: {printed!r} not found in src/lm20.md"
    if flag:
        FLAGGED.append(f"{label}: {value!r} printed {printed}")
    COVERED.add(printed.lstrip("-"))
    N_CHECKS += 1


def has(label: str, text: str) -> None:
    global N_CHECKS
    assert text in TEXT, f"{label}: {text!r} not found in src/lm20.md"
    print(f"CHECK {label}: '{text}' in text ok")
    for num in re.findall(r"\d[\d,]*\.?\d*", text):
        COVERED.add(num.rstrip(".,"))
    N_CHECKS += 1


def chart_text(name: str) -> str:
    return (CHARTS / f"{name}.json").read_text(encoding="utf-8")


def in_chart(label: str, chart: str, text: str) -> None:
    global N_CHECKS
    assert text in chart_text(chart), f"{label}: {text!r} not found in src/data/{chart}.json"
    print(f"CHECK {label}: '{text}' in {chart}.json ok")
    N_CHECKS += 1


def _anchor_rows() -> dict[str, str]:
    rows: dict[str, str] = {}
    sec = ANCHORS.read_text(encoding="utf-8").split("\n## LM20", 1)[1].split("\n## ", 1)[0]
    for line in sec.splitlines():
        if line.startswith("| A20-"):
            cells = [x.strip() for x in line.strip().strip("|").split(" | ")]
            rows[cells[0]] = cells[3].strip("`")
    return rows


ANCHOR_ROWS = _anchor_rows()
assert len(ANCHOR_ROWS) == 51, len(ANCHOR_ROWS)


def anchor(aid: str, label: str, value: float, shown: str) -> None:
    """`shown` is a number as the anchor's Value column prints it; compare value at that number's decimals."""
    row = ANCHOR_ROWS[aid]
    d = len(shown.split(".")[1]) if "." in shown else 0
    got = f"{value:.{d}f}"
    present = in_text(shown, row)
    tag = "ok" if got == shown and present else "DIFFERS"
    print(f"ANCHOR {aid} {label}: {got} (anchor {shown}{'' if present else ', not in the row'}) {tag}")
    if tag != "ok":
        ANCHOR_DIFFS.append(f"{aid} {label}: script {got} | anchor {shown}")


# ====================================================================== data, notation note, hygiene note
T, A, TAU, RB, S, SU = c.T, c.A, c.TAU, c.RB, c.S, c.SU
print(f"TR23: T = {T}, {c.DAYS} days, tau {TAU:.6f}, A {A:.6f}")
chk("T", T, ",", "5,849")
chk("calendar days", c.DAYS, ",", "8,680")
has("tau in the notation note", "8,680/365.25=23.7645")
chk("tau", TAU, ".4f", "23.7645")
chk("tau, two decimals", TAU, ".2f", "23.76")
chk("tau, one decimal", TAU, ".1f", "23.8")
chk("A", A, ".2f", "246.12")
for d in ("3 January 2003", "8 October 2026", "retrieved 18 October 2026", "2003–2025",
          "1 June 2015", "29 May 2015"):
    has("date " + d, d)
anchor("A20-01", "T", T, "5849")
anchor("A20-02", "days", c.DAYS, "8680")
anchor("A20-02", "tau", TAU, "23.764545")
anchor("A20-02", "A", A, "246.122955")

# ====================================================================== the case and its exhibit
chk("Rbar (case)", 100 * RB, ".4f", "0.0625")
chk("s (case)", 100 * S, ".4f", "1.2084")
anchor("A20-03", "Rbar", 100 * RB, "0.0625050622")
anchor("A20-03", "s", 100 * S, "1.2083643417")
anchor("A20-03", "s_u", 100 * SU, "1.2084676516")
y08, y09 = c.ANN_SIMPLE_L[2008 - 2003], c.ANN_SIMPLE_L[2009 - 2003]
assert min(c.ANN_SIMPLE_L) == y08 and max(c.ANN_SIMPLE_L) == y09
chk("2008", 100 * y08, ".2f", "-43.07")
chk("2009", 100 * y09, ".2f", "83.34")
anchor("A20-07", "2008", 100 * y08, "-43.068784")
anchor("A20-07", "2009", 100 * y09, "83.344884")
ann_mean, ann_vol = A * RB, sqrt(A) * S
chk("A Rbar", 100 * ann_mean, ".2f", "15.38")
chk("sqrt(A) s", 100 * ann_vol, ".2f", "18.96")
anchor("A20-08", "A Rbar", 100 * ann_mean, "15.383931")
anchor("A20-08", "sqrt(A) s", 100 * ann_vol, "18.957190")
se_ann = sqrt(A) * S / sqrt(TAU)
chk("SE(A Rbar)", 100 * se_ann, ".2f", "3.89")
lo9, hi9 = ann_mean - Z * se_ann, ann_mean + Z * se_ann
chk("mean interval low", 100 * lo9, ".1f", "7.8")
chk("mean interval high", 100 * hi9, ".1f", "23.0")
chk("mean interval low, printed inputs", 15.38 - 1.96 * 3.89, ".1f", "7.8")
chk("mean interval high, printed inputs", 15.38 + 1.96 * 3.89, ".1f", "23.0")
anchor("A20-09", "SE", 100 * se_ann, "3.888743")
anchor("A20-09", "low", 100 * lo9, "7.76199")
anchor("A20-09", "high", 100 * hi9, "23.00587")
kurt, skew = c.KURT, c.SKEW
se_vol_k = ann_vol * sqrt((kurt - 1) / (4 * T))
se_vol_n = ann_vol / sqrt(2 * T)
chk("SE volatility, plug-in", 100 * se_vol_k, ".2f", "0.33")
chk("SE volatility, plug-in (delta table)", 100 * se_vol_k, ".3f", "0.334")
chk("SE volatility, normal", 100 * se_vol_n, ".3f", "0.175")
chk("volatility interval low", 100 * (ann_vol - Z * se_vol_k), ".1f", "18.3")
chk("volatility interval high", 100 * (ann_vol + Z * se_vol_k), ".1f", "19.6")
chk("volatility interval low, printed", 18.96 - 1.96 * 0.33, ".1f", "18.3")
chk("volatility interval high, printed", 18.96 + 1.96 * 0.33, ".1f", "19.6")
anchor("A20-10", "plug-in", 100 * se_vol_k, "0.334127")
anchor("A20-10", "normal", 100 * se_vol_n, "0.1752743")
kelly = RB / S**2
chk("Kelly f-hat", kelly, ".2f", "4.28")
chk("Kelly from printed 0.0625% and 1.2084%", 0.000625 / 0.012084**2, ".2f", "4.28")
anchor("A20-11", "f-hat", kelly, "4.280745")
se_k = c.se_kelly(RB, S, c.M3, c.M4, T)
se_k_mean = 1 / (S * sqrt(T))
se_k_norm = c.se_kelly(RB, S, 0.0, 3 * S**4, T)
chk("SE Kelly, plug-in (case)", se_k, ".2f", "1.11")
chk("SE Kelly, plug-in (delta table)", se_k, ".3f", "1.111")
chk("SE Kelly, mean only (text)", se_k_mean, ".2f", "1.08")
chk("SE Kelly, mean only (delta table)", se_k_mean, ".3f", "1.082")
chk("SE Kelly, normal (delta table)", se_k_norm, ".3f", "1.085")
chk("Kelly interval low", kelly - Z * se_k, ".2f", "2.10")
chk("Kelly interval high", kelly + Z * se_k, ".2f", "6.46")
chk("Kelly interval low, printed", 4.28 - 1.96 * 1.11, ".2f", "2.10")
chk("Kelly interval high, printed", 4.28 + 1.96 * 1.11, ".2f", "6.46")
anchor("A20-28", "mean only", se_k_mean, "1.0820848")
anchor("A20-28", "normal", se_k_norm, "1.0849762")
anchor("A20-28", "plug-in", se_k, "1.1111595")
anchor("A20-28", "low", kelly - Z * se_k, "2.102873")
anchor("A20-28", "high", kelly + Z * se_k, "6.458618")
sr = RB / S
se_s = c.se_sharpe(RB, S, c.M3, c.M4, T)
se_s_n = sqrt((1 + sr**2 / 2) / T)
chk("daily SR", sr, ".4f", "0.0517")
chk("daily SR, six decimals (E1)", sr, ".6f", "0.051727")
chk("SE daily SR, plug-in", se_s, ".4f", "0.0132")
chk("SE daily SR, normal", se_s_n, ".4f", "0.0131")
chk("daily SR interval low", sr - Z * se_s, ".4f", "0.0258")
chk("daily SR interval high", sr + Z * se_s, ".4f", "0.0776")
chk("daily SR interval low, printed", 0.0517 - 1.96 * 0.0132, ".4f", "0.0258")
chk("daily SR interval high, printed", 0.0517 + 1.96 * 0.0132, ".4f", "0.0776")
chk("annual SR", sqrt(A) * sr, ".2f", "0.81")
chk("SE annual SR, plug-in (case)", sqrt(A) * se_s, ".2f", "0.21")
chk("SE annual SR, plug-in (delta table)", sqrt(A) * se_s, ".3f", "0.207")
chk("SE annual SR, normal (delta table)", sqrt(A) * se_s_n, ".3f", "0.205")
chk("annual SR interval low", sqrt(A) * (sr - Z * se_s), ".2f", "0.40")
chk("annual SR interval high", sqrt(A) * (sr + Z * se_s), ".2f", "1.22")
chk("annual SR interval low, printed", 0.81 - 1.96 * 0.21, ".2f", "0.40")
chk("annual SR interval high, printed", 0.81 + 1.96 * 0.21, ".2f", "1.22")
chk("1/sqrt(tau) (KC 7)", 1 / sqrt(TAU), ".3f", "0.205")
anchor("A20-29", "daily SR", sr, "0.05172700")
anchor("A20-29", "SE plug-in", se_s, "0.01322096")
anchor("A20-29", "SE normal", se_s_n, "0.01308427")
anchor("A20-29", "annual SR", sqrt(A) * sr, "0.811509")
anchor("A20-29", "annual SE plug-in", sqrt(A) * se_s, "0.2074144")
anchor("A20-29", "annual SE normal", sqrt(A) * se_s_n, "0.2052700")
anchor("A20-29", "low", sqrt(A) * (sr - Z * se_s), "0.404977")
anchor("A20-29", "high", sqrt(A) * (sr + Z * se_s), "1.218041")
anchor("A20-29", "1/sqrt(tau)", 1 / sqrt(TAU), "0.2051329")
NU, LOC, SCALE = c.NU, c.LOC, c.SCALE
SE_T = c.SE_T
chk("nu", NU, ".3f", "3.065")
chk("SE nu", SE_T[0], ".3f", "0.144")
chk("Wald low", NU - Z * SE_T[0], ".2f", "2.78")
chk("Wald high", NU + Z * SE_T[0], ".2f", "3.35")
chk("Wald low, printed", 3.065 - 1.96 * 0.144, ".2f", "2.78")
chk("Wald high, printed", 3.065 + 1.96 * 0.144, ".2f", "3.35")
k3, a3, e3 = c.hill("0.03")
chk("k at 3%", k3, "d", "108")
chk("Hill at 3%", a3, ".2f", "3.63")
chk("Hill SE at 3%", e3, ".2f", "0.35")
chk("Hill SE at 3% from printed 3.63", 3.63 / sqrt(108), ".2f", "0.35")
chk("Hill interval low", a3 - Z * e3, ".1f", "2.9")
chk("Hill interval high", a3 + Z * e3, ".1f", "4.3")
chk("Hill interval low, printed", 3.63 - 1.96 * 0.35, ".1f", "2.9")
chk("Hill interval high, printed", 3.63 + 1.96 * 0.35, ".1f", "4.3")
anchor("A20-33", "k", k3, "108")
anchor("A20-33", "alpha", a3, "3.634243")
anchor("A20-33", "SE", e3, "0.349705")
for row in ("| Mean, % a year, $A\\bar R$ | 15.38 | 3.89 | 7.8 to 23.0 | (20.2) |",
            "| Volatility, % a year, $\\sqrt A\\,s$ | 18.96 | 0.33 | 18.3 to 19.6 |",
            "| Kelly fraction $\\hat f=\\bar R/s^2$ | 4.28 | 1.11 | 2.10 to 6.46 |",
            "| Sharpe ratio a year, $r_f=0$ | 0.81 | 0.21 | 0.40 to 1.22 |",
            "| Student-t degrees of freedom | 3.065 | 0.144 | 2.78 to 3.35 |",
            "| Tail index, Hill, 108 losses of 3% or more | 3.63 | 0.35 | 2.9 to 4.3 |"):
    has("case table row", norm_text(row))
has("case: within a third of a point", "within a third of a point")
assert se_vol_k < 1 / 3 + 0.01 and abs(se_vol_k * 100 - 1 / 3) < 0.01

# ====================================================================== Section 2: sampling distributions, E1, consistency
sims = c.experiment1()
assert sims["normal"].shape == (10_000, 246)
chk("simulated samples", c.N_SIM, ",", "10,000")
x2: dict[str, dict[str, float]] = {}
for lab, xs in sims.items():
    am = A * xs.mean(axis=1)
    av = sqrt(A) * xs.std(axis=1, ddof=0)
    x2[lab] = {"sd_am": float(am.std(ddof=0)), "sd_av": float(av.std(ddof=0)),
               "q025": c.qinv(av, 0.025), "q50": c.qinv(av, 0.5), "q975": c.qinv(av, 0.975),
               "b025": c.batch_se(av, 0.025), "b50": c.batch_se(av, 0.5), "b975": c.batch_se(av, 0.975),
               "off40": int((av > 0.40).sum()), "am_out": int(((am < -0.6) | (am >= 0.9)).sum())}
nx, tx = x2["normal"], x2["t"]
chk("normal: sd of annual mean", 100 * nx["sd_am"], ".1f", "18.9")
chk("normal: its MC SE", 100 * nx["sd_am"] / sqrt(2 * c.N_SIM), ".2f", "0.13")
chk("t: sd of annual mean", 100 * tx["sd_am"], ".1f", "18.7")
theory_am = sqrt(A) * S * sqrt(A / 246)
chk("theory: sd of annual mean", 100 * theory_am, ".2f", "18.96")
chk("normal: sd of volatility", 100 * nx["sd_av"], ".2f", "0.86")
chk("normal: its MC SE", 100 * nx["sd_av"] / sqrt(2 * c.N_SIM), ".3f", "0.006")
chk("theory: sd of volatility", 100 * sqrt(A) * S / sqrt(2 * 246), ".3f", "0.855")
chk("t: sd of volatility, about 4", 100 * tx["sd_av"], ".0f", "4")
chk("normal 2.5%", 100 * nx["q025"], ".1f", "17.3")
chk("normal 97.5%", 100 * nx["q975"], ".1f", "20.6")
chk("t 2.5%", 100 * tx["q025"], ".1f", "14.6")
chk("t 97.5%", 100 * tx["q975"], ".1f", "26.8")
chk("t median", 100 * tx["q50"], ".1f", "17.7")
batch = [nx["b025"], nx["b50"], nx["b975"], tx["b025"], tx["b50"]]
assert 0.005 <= 100 * min(batch) and 100 * max(batch) < 0.035, batch
has("batch SEs", "0.01 to 0.03 points")
chk("t 97.5% batch SE", 100 * tx["b975"], ".1f", "0.3")
chk("t values above 40%", tx["off40"], "d", "35")
assert nx["off40"] == 0
print(f"     annual means outside the top axis: normal {nx['am_out']}, t {tx['am_out']} (the axis is clipped)")
anchor("A20-35", "normal sd of A x mean", 100 * nx["sd_am"], "18.91985")
anchor("A20-35", "normal sd of volatility", 100 * nx["sd_av"], "0.855165")
anchor("A20-35", "normal 2.5%", 100 * nx["q025"], "17.25880")
anchor("A20-35", "normal 97.5%", 100 * nx["q975"], "20.59109")
anchor("A20-35", "t sd of A x mean", 100 * tx["sd_am"], "18.74431")
anchor("A20-35", "t sd of volatility", 100 * tx["sd_av"], "3.74150")
anchor("A20-35", "t 2.5%", 100 * tx["q025"], "14.57362")
anchor("A20-35", "t median", 100 * tx["q50"], "17.74816")
anchor("A20-35", "t 97.5%", 100 * tx["q975"], "26.83947")
anchor("A20-35", "t 97.5% batch SE", 100 * tx["b975"], "0.3030")
run_am, run_av = c.experiment4()
chk("exp 4: sd of annual mean, lowest", 100 * run_am.min(), ".1f", "18.6")
chk("exp 4: sd of annual mean, highest", 100 * run_am.max(), ".1f", "19.2")
chk("exp 4: sd of volatility, lowest", 100 * run_av.min(), ".1f", "3.3")
chk("exp 4: sd of volatility, highest", 100 * run_av.max(), ".1f", "4.6")
assert f"{100 * run_av.mean():.0f}" == "4"           # "about 4" also over the runs
anchor("A20-51", "range low (mean)", 100 * run_am.min(), "18.60043")
anchor("A20-51", "range high (mean)", 100 * run_am.max(), "19.22676")
anchor("A20-51", "range low (vol)", 100 * run_av.min(), "3.32470")
anchor("A20-51", "range high (vol)", 100 * run_av.max(), "4.63413")
has("experiment 1 seed", "`default_rng([1, 20261011])`")
has("bins", "bins of 2 points")
has("bins", "bins of 0.25 points; 35 Student-t values above 40%")
has("about 19 points (zh)", "約 19 個百分點")
# E1
for T_ in (246, 5849):
    tsr = T_ * sr**2
    print(f"     E1 T={T_}: T SR^2 {tsr:.6f}, eta* {tsr / (1 + tsr):.6f}")
chk("E1: 246 SR^2", 246 * sr**2, ".3f", "0.658")
chk("E1: 246 SR^2 from printed 0.051727", 246 * 0.051727**2, ".3f", "0.658")
chk("E1: eta* one year", 246 * sr**2 / (1 + 246 * sr**2), ".3f", "0.397")
chk("E1: eta* one year from printed 0.658", 0.658 / 1.658, ".3f", "0.397")
chk("E1: T SR^2", T * sr**2, ".2f", "15.65")
chk("E1: T SR^2 from printed 0.051727", T * 0.051727**2, ".2f", "15.65")
chk("E1: eta* sample", T * sr**2 / (1 + T * sr**2), ".3f", "0.940")
chk("E1: eta* sample from printed 15.65", 15.65 / 16.65, ".3f", "0.940")
anchor("A20-12", "T=246 T SR^2", 246 * sr**2, "0.6582179")
anchor("A20-12", "eta* 246", 246 * sr**2 / (1 + 246 * sr**2), "0.3969429")
anchor("A20-12", "T SR^2", T * sr**2, "15.650067")
anchor("A20-12", "eta*", T * sr**2 / (1 + T * sr**2), "0.9399402")
# the minimizer and the minimum, numerically
eta = np.linspace(0, 1.5, 300001)
mse = eta**2 * S**2 / 246 + (eta - 1) ** 2 * RB**2
e_star = 246 * sr**2 / (1 + 246 * sr**2)
assert abs(eta[mse.argmin()] - e_star) < 1e-5 and abs(mse.min() - e_star * S**2 / 246) < 1e-15
# KC 2
chk("KC 2: sqrt(3/246)", sqrt(3 / 246), ".3f", "0.110")
anchor("A20-49", "sqrt(3/246)", sqrt(3 / 246), "0.1104315")
assert 0.25 * S**2 / 246 + 0.25 * RB**2 < S**2 / 246      # one half R-bar wins in the model with TR23's values

# ====================================================================== Section 3: standard error, Merton, (20.3)
chk("s/sqrt(T)", 100 * S / sqrt(T), ".5f", "0.01580")
chk("s/sqrt(T) from printed 1.2084%", 1.2084 / sqrt(5849), ".5f", "0.01580")
anchor("A20-13", "s/sqrt(T)", 100 * S / sqrt(T), "0.015800000")
chk("E2: 0.01580 x A", 0.01580 * 246.12, ".2f", "3.89")
chk("E2: 18.96/sqrt(23.7645)", 18.96 / sqrt(23.7645), ".2f", "3.89")
assert 0.24 < se_ann / ann_mean < 0.26                     # "a quarter of the 15.38%"
has("E2: LM7's values", "[[LM7]]'s 7.36 and 6.09 points over 4.95 years")
# Merton's chart
mer = {m: c.merton(m) for m in c.MERTON_M}
model_mean = sqrt(A) * c.S_R / sqrt(TAU)
chk("iid line", 100 * model_mean, ".2f", "3.90")
mean_ses = [100 * v[1] for v in mer.values()]
chk("Merton: lowest mean SE", min(mean_ses), ".2f", "3.87")
chk("Merton: highest mean SE", max(mean_ses), ".2f", "4.53")
chk("Merton: daily volatility SE", 100 * mer[1][2], ".2f", "0.34")
chk("Merton: annual-sum volatility SE", 100 * mer[246][2], ".2f", "4.43")
chk("Merton: normal model daily", 100 * mer[1][3], ".2f", "0.18")
chk("Merton: normal model annual", 100 * mer[246][3], ".2f", "2.80")
assert all(mer[a_][2] < mer[b_][2] for a_, b_ in zip(c.MERTON_M, c.MERTON_M[1:]))   # "grows"
anchor("A20-36", "model mean SE", 100 * model_mean, "3.896346")
for m, (nm, sm_, sv, mv) in mer.items():
    row = ANCHOR_ROWS["A20-36"]
    seg = re.search(rf"m={m} \(n={nm}\): mean SE ([\d.]+), vol SE ([\d.]+)(?: \(!\))?, normal model vol SE ([\d.]+)", row)
    assert seg, m
    anchor("A20-36", f"m={m} mean", 100 * sm_, seg.group(1))
    anchor("A20-36", f"m={m} vol", 100 * sv, seg.group(2))
    anchor("A20-36", f"m={m} model", 100 * mv, seg.group(3))
yrs = (1.96 * 100 * ann_vol) ** 2
chk("years for +-1 point", yrs, ",.0f", "1,381")
chk("years for +-1 point, printed 1.96 x 18.96", (1.96 * 18.96) ** 2, ",.0f", "1,381")
anchor("A20-14", "years", yrs, "1380.5752")
# (20.3) and E3
chk("s_u/s TR23", SU / S, ".7f", "1.0000855")
anchor("A20-03", "s_u/s", SU / S, "1.00008549566")
chk("sqrt(23/22)", sqrt(23 / 22), ".4f", "1.0225")
chk("22/23", 22 / 23, ".4f", "0.9565")
chk("23 annual: s", 100 * c.S_ANN, ".3f", "22.207")
chk("23 annual: s_u", 100 * c.SU_ANN, ".3f", "22.706")
assert f"{22.207 * sqrt(23 / 22):.3f}" == "22.706"       # the printed s times the exact factor
chk("LM10's sqrt(4382/4381)", sqrt(4382 / 4381), ".6f", "1.000114")
chk("U28 T", c.U28_T, ",", "4,382")
anchor("A20-15", "22/23", 22 / 23, "0.95652174")
anchor("A20-15", "sqrt(23/22)", sqrt(23 / 22), "1.02247472")
anchor("A20-15", "s_u annual", 100 * c.SU_ANN, "22.7061634")
anchor("A20-06", "annual sd", 100 * c.S_ANN, "22.2070659")
# the pitfall
chk("pitfall: 0.0158% x sqrt(A)", 0.0158 * sqrt(A), ".2f", "0.25")
chk("pitfall: unrounded", 100 * S / sqrt(T) * sqrt(A), ".2f", "0.25")
anchor("A20-42", "without the 2", 100 * sqrt(A) * S / sqrt(T), "0.247875")
chk("pitfall: sqrt(A)", sqrt(A), ".2f", "15.69")
# KC 3
chk("KC 3: three years", 18.96 / sqrt(3), ".1f", "10.9")
chk("KC 3: ten years", 18.96 / sqrt(10), ".1f", "6.0")
anchor("A20-50", "three years", 100 * ann_vol / sqrt(3), "10.94494")
anchor("A20-50", "ten years", 100 * ann_vol / sqrt(10), "5.99479")
has("zh 3: 2.2%", "標準差則差 2.2%")

# ====================================================================== Section 4: intervals, coverage, years
q_t = float(stats.t.ppf(0.975, T - 1))
z975 = float(stats.norm.ppf(0.975))
chk("t quantile at T-1", q_t, ".5f", "1.96037")
chk("normal quantile", z975, ".5f", "1.95996")
chk("T-1", T - 1, ",", "5,848")
anchor("A20-16", "t", q_t, "1.960369722")
anchor("A20-16", "norm", z975, "1.959963985")
t_half = q_t * A * SU / sqrt(T)
z_half = Z * A * S / sqrt(T)
chk("t interval moves the ends by", 100 * (t_half - z_half), ".3f", "0.002")
assert f"{100 * (ann_mean - t_half):.1f}" == "7.8" and f"{100 * (ann_mean + t_half):.1f}" == "23.0"
one_year_se = sqrt(A) * S * sqrt(A / 246)
chk("one year: SE", 100 * one_year_se, ".2f", "18.96")
chk("one year: half-width", 100 * Z * one_year_se, ".1f", "37.2")
chk("one year: half-width, printed", 1.96 * 18.96, ".1f", "37.2")
anchor("A20-18", "SE", 100 * one_year_se, "18.961927")
anchor("A20-18", "half-width", 100 * Z * one_year_se, "37.16538")
# coverage, experiment 2
rng2 = np.random.default_rng([2, c.SEED_ROOT])
n_cov, chunk = 100_000, 10_000
cov: dict[tuple[int, str], tuple[float, float]] = {}
exact: dict[int, float] = {}
for Tc in (5, 10, 30, 100, 246):
    q = float(stats.t.ppf(0.975, Tc - 1))
    exact[Tc] = 2 * float(stats.t.cdf(Z * sqrt((Tc - 1) / Tc), Tc - 1)) - 1
    for model in ("normal", "t3"):
        hz = ht = 0
        for _ in range(n_cov // chunk):
            if model == "normal":
                xs = rng2.standard_normal((chunk, Tc))
            else:
                zz = rng2.standard_normal((chunk, Tc, 4))
                xs = zz[..., 0] / np.sqrt((zz[..., 1:] ** 2).sum(axis=2) / 3) / sqrt(3)
            mn = xs.mean(axis=1)
            hz += int((np.abs(mn) <= Z * xs.std(axis=1, ddof=0) / sqrt(Tc)).sum())
            ht += int((np.abs(mn) <= q * xs.std(axis=1, ddof=1) / sqrt(Tc)).sum())
        cov[(Tc, model)] = (hz / n_cov, ht / n_cov)
chk("coverage MC SE", 100 * sqrt(0.95 * 0.05 / n_cov), ".2f", "0.07")
chk("simulated samples per cell", n_cov, ",", "100,000")
for Tc in (5, 10, 30, 100, 246):
    vals = [cov[(Tc, "normal")][0], exact[Tc], cov[(Tc, "normal")][1], cov[(Tc, "t3")][0], cov[(Tc, "t3")][1]]
    printed = [f"{100 * v:.1f}" for v in vals]
    for v in vals:
        assert not tie(100 * v, ".1f")
        if near(100 * v, ".1f"):
            FLAGGED.append(f"coverage T={Tc}: {100 * v:.4f} printed {100 * v:.1f}")
    has(f"coverage row T={Tc}", f"| {Tc} | " + " | ".join(printed) + " |")
    print(f"     coverage T={Tc}: " + ", ".join(f"{100 * v:.3f}" for v in vals))
    row = ANCHOR_ROWS["A20-17"]
    for model in ("normal", "t3"):
        seg = re.search(rf"T={Tc} {model}: z\(s\) ([\d.]+) ?(?:\(!\))?%, t\(s_u\) ([\d.]+)", row)
        assert seg, (Tc, model)
        anchor("A20-17", f"T={Tc} {model} z", 100 * cov[(Tc, model)][0], seg.group(1))
        anchor("A20-17", f"T={Tc} {model} t", 100 * cov[(Tc, model)][1], seg.group(2))
chk("coverage at T=5, normal, 1.96 with s", 100 * cov[(5, "normal")][0], ".1f", "84.5")
lo246 = min(min(cov[(246, m)]) for m in ("normal", "t3"))
hi246 = max(max(cov[(246, m)]) for m in ("normal", "t3"))
chk("T=246: lowest coverage", 100 * min(lo246, exact[246]), ".1f", "94.8")
chk("T=246: highest coverage", 100 * hi246, ".1f", "95.2")
has("T=246 range", "every column is between 94.8% and 95.2%")
assert cov[(5, "t3")][1] > 0.95 and cov[(10, "t3")][1] > 0.95   # the t interval covers too often for t3 days
has("experiment 2 seed", "`default_rng([2, 20261011])`")
# years chart
for yrs_, lo_p, hi_p in ((1, "-21.8", "52.5"), (10, "3.6", "27.1"), (100, "11.7", "19.1")):
    h = Z * ann_vol / sqrt(yrs_)
    chk(f"{yrs_} years low", 100 * (ann_mean - h), ".1f", lo_p)
    chk(f"{yrs_} years high", 100 * (ann_mean + h), ".1f", hi_p)
    chk(f"{yrs_} years low, printed", 15.38 - 1.96 * 18.96 / sqrt(yrs_), ".1f", lo_p)
    chk(f"{yrs_} years high, printed", 15.38 + 1.96 * 18.96 / sqrt(yrs_), ".1f", hi_p)
    seg = re.search(rf"(?<![\d.]){yrs_} years: ([-\d.]+)% to ([\d.]+)", ANCHOR_ROWS["A20-37"])
    assert seg
    anchor("A20-37", f"{yrs_} years low", 100 * (ann_mean - h), seg.group(1))
    anchor("A20-37", f"{yrs_} years high", 100 * (ann_mean + h), seg.group(2))
has("widget: draws", "1,000 samples per click and draws the first 100 intervals")
# the widget's t table
tq = {n: float(stats.t.ppf(0.975, n - 1)) for n in (5, 10, 20, 30, 100, 250)}
for n, shown in zip(tq, ("2.776445", "2.262157", "2.093024", "2.045230", "1.984217", "1.969537")):
    anchor("A20-38", f"t quantile T={n}", tq[n], shown)

# ====================================================================== Section 5: maximum likelihood
chk("0050 T", c.T50, ",", "2,902")
chk("0050 mean", 100 * c.MU50, ".4f", "0.0871")
chk("0050 s", 100 * c.S50, ".4f", "1.2385")
chk("0050 SE of the mean (LM4's)", 100 * c.S50 / sqrt(c.T50), ".4f", "0.0230")
anchor("A20-05", "mean", 100 * c.MU50, "0.0871204726")
anchor("A20-05", "s", 100 * c.S50, "1.2385140606")
anchor("A20-30", "SE(mean)", 100 * c.S50 / sqrt(c.T50), "0.02299070")
chk("TR23 s_u, four decimals", 100 * SU, ".4f", "1.2085")
assert abs(float(np.mean(c.X100)) - 100 * RB) < 1e-12 and abs(float(np.std(c.X100, ddof=0)) - 100 * S) < 1e-12
# the normal MLE, numerically: no other point of a grid around (Rbar, s) has a higher log-likelihood
grid_mu = RB + np.linspace(-3, 3, 61) * S / sqrt(T)
grid_s = S * (1 + np.linspace(-3, 3, 61) / sqrt(2 * T))
ll = np.array([[float(stats.norm.logpdf(c.R, mu, sg).sum()) for sg in grid_s] for mu in grid_mu])
assert ll.argmax() == 30 * 61 + 30
# the multivariate MLE (Deep Dive 1): at the 28 U28 sectors, Sigma-hat beats perturbed matrices
smp = c.u28()
Xu = smp.X
mu_u = Xu.mean(axis=0)
Sig = np.cov(Xu, rowvar=False, ddof=0)


def ll_mvn(mu: np.ndarray, sig: np.ndarray) -> float:
    d = Xu - mu
    sign, logdet = np.linalg.slogdet(sig)
    assert sign > 0
    return float(-0.5 * len(Xu) * (Xu.shape[1] * log(2 * math.pi) + logdet)
                 - 0.5 * np.einsum("ij,jk,ik->", d, np.linalg.inv(sig), d))


best = ll_mvn(mu_u, Sig)
rng_dd = np.random.default_rng(12345)       # a check, not an experiment of the module: nothing is printed
for _ in range(20):
    E = rng_dd.standard_normal(Sig.shape) * 1e-6
    assert ll_mvn(mu_u, Sig + E @ E.T + 1e-7 * np.eye(28)) < best
    assert ll_mvn(mu_u + rng_dd.standard_normal(28) * 1e-5, Sig) < best
lam = np.linalg.eigvalsh(np.linalg.cholesky(Sig).T @ np.linalg.inv(Sig) @ np.linalg.cholesky(Sig))
assert np.allclose(lam, 1.0)
# the Student-t fit
chk("t.fit nu", float(c.RAW_T[0]), ".5f", "3.06522")
chk("refined nu", NU, ".5f", "3.06526")
chk("location", LOC, ".4f", "0.0997")
chk("scale", SCALE, ".4f", "0.7761")
chk("SE location", SE_T[1], ".4f", "0.0124")
chk("SE scale", SE_T[2], ".4f", "0.0138")
ll_gain = c.LL_T - c.LL_N
chk("log-likelihood gain", ll_gain, ".1f", "561.8")
gsd = np.array([SCALE * 0.5 * sqrt((NU - 2) / NU) * (-2 / (NU - 2) ** 2), 0.0, sqrt(NU / (NU - 2))])
sd_t = SCALE * sqrt(NU / (NU - 2))
se_sd_t = sqrt(float(gsd @ c.COV_T @ gsd))
chk("fit's standard deviation", sd_t, ".3f", "1.317")
chk("fit's sd from printed 0.7761 and 3.065", 0.7761 * sqrt(3.065 / 1.065), ".3f", "1.317")
chk("SE of the fit's sd", se_sd_t, ".3f", "0.045")
anchor("A20-19", "gain", ll_gain, "561.77325")
anchor("A20-20", "t.fit nu", float(c.RAW_T[0]), "3.065223")
anchor("A20-20", "refined nu", NU, "3.0652570")
anchor("A20-20", "SE nu", SE_T[0], "0.1435028")
anchor("A20-20", "location", LOC, "0.09972601")
anchor("A20-20", "SE location", SE_T[1], "0.01235669")
anchor("A20-20", "scale", SCALE, "0.77611599")
anchor("A20-20", "SE scale", SE_T[2], "0.01383101")
anchor("A20-21", "sd", sd_t, "1.3165364")
anchor("A20-21", "SE sd", se_sd_t, "0.0453758")
reg = {}
for lab, x in (("before", c.X100[c.PRE]), ("from", c.X100[~c.PRE])):
    pp, cc, _, _ = c.tfit(x)
    reg[lab] = (len(x), float(pp[0]), float(np.sqrt(np.diag(cc))[0]))
chk("regime 1 size", reg["before"][0], ",", "3,077")
chk("regime 2 size", reg["from"][0], ",", "2,772")
chk("regime 1 nu", reg["before"][1], ".3f", "2.990")
chk("regime 1 SE", reg["before"][2], ".3f", "0.195")
chk("regime 2 nu", reg["from"][1], ".3f", "3.237")
chk("regime 2 SE", reg["from"][2], ".3f", "0.223")
anchor("A20-26", "nu before", reg["before"][1], "2.9897318")
anchor("A20-26", "SE before", reg["before"][2], "0.1946773")
anchor("A20-26", "nu from", reg["from"][1], "3.2370259")
anchor("A20-26", "SE from", reg["from"][2], "0.2225593")
has("fits row normal", "| Normal, TR23 | 5,849 | — | 0.0625 (0.0158) | — | 1.2084 (0.0112) |")
has("fits row t", "| Student-t, TR23 | 5,849 | 3.065 (0.144) | 0.0997 (0.0124) | 0.7761 (0.0138) | 1.317 (0.045) |")
has("fits row regime 1", "| Student-t, 7% limit, to 29 May 2015 | 3,077 | 2.990 (0.195) |")
has("fits row regime 2", "| Student-t, 10% limit, from 1 June 2015 | 2,772 | 3.237 (0.223) |")
# the location against the median and the mean
srt = np.sort(c.R)
med = float(srt[(T + 1) // 2 - 1])            # F-hat^{-1}(1/2): T is odd, the 2,925th order statistic
assert med == c.qinv(c.R, 0.5)
chk("median (LM14's)", 100 * med, ".4f", "0.0879")
chk("skewness", skew, ".2f", "-0.34")
assert (LOC / 100 - RB) / RB > 0.5                          # "more than half above the mean"
anchor("A20-27", "skewness", skew, "-0.338444")
anchor("A20-27", "kurtosis", kurt, "8.268030")

# ====================================================================== Section 6: information, profile, Cramer-Rao
chk("SE(mu-hat), four decimals", 100 * S / sqrt(T), ".4f", "0.0158")
chk("SE(sigma-hat)", 100 * S / sqrt(2 * T), ".4f", "0.0112")
anchor("A20-24", "SE mu", 100 * S / sqrt(T), "0.01580000")
anchor("A20-24", "SE sigma", 100 * S / sqrt(2 * T), "0.01117229")
# the observed information of the normal model equals T/s^2 and 2T/s^2 at the MLE
Hn = c.hessian(lambda p: float(-stats.norm.logpdf(c.X100, p[0], p[1]).sum()),
               np.array([100 * RB, 100 * S]), np.array([1e-5, 1e-5]))
assert np.allclose(np.diag(Hn), [T / (100 * S) ** 2, 2 * T / (100 * S) ** 2], rtol=1e-5) and abs(Hn[0, 1]) < 1e-3
drop = Z**2 / 2
chk("profile drop", drop, ".2f", "1.92")
lr_lo = float(optimize.brentq(lambda q: c.profile(q) + drop, 2.5, NU))
lr_hi = float(optimize.brentq(lambda q: c.profile(q) + drop, NU, 4.0))
chk("profile low", lr_lo, ".2f", "2.80")
chk("profile high", lr_hi, ".2f", "3.37")
anchor("A20-23", "profile low", lr_lo, "2.801835")
anchor("A20-23", "profile high", lr_hi, "3.366757")
anchor("A20-23", "Wald low", NU - Z * SE_T[0], "2.783991")
anchor("A20-23", "Wald high", NU + Z * SE_T[0], "3.346523")
assert c.profile(2.6) < -(2.6 - NU) ** 2 / (2 * SE_T[0] ** 2)   # the curve falls faster towards small nu
cor = c.COV_T / np.outer(SE_T, SE_T)
chk("corr nu-scale", float(cor[0, 2]), ".2f", "0.68")
anchor("A20-22", "nu-scale", float(cor[0, 2]), "0.677422")
ratio = SE_T[1] / (100 * S / sqrt(T))
chk("location SE / mean SE", ratio, ".2f", "0.78")
chk("ratio from printed", 0.0124 / 0.0158, ".2f", "0.78")
anchor("A20-25", "ratio", ratio, "0.782069")
chk("KC 6: one-year bound", 100 * A * S / sqrt(246), ".2f", "18.96")

# ====================================================================== Section 7: delta method
chk("kurtosis", kurt, ".2f", "8.27")
chk("kurtosis minus 1", 8.27 - 1, ".2f", "7.27")
chk("E8 from printed", 18.96 * sqrt(7.27 / (4 * 5849)), ".2f", "0.33")
chk("E8 normal from printed", 18.96 / sqrt(2 * 5849), ".3f", "0.175")
# the delta method for s against simulation (normal days, 246 per sample): theory 0.855 above, simulation 0.86
se_a = c.S_ANN / sqrt(2 * c.N_YEARS)
chk("23 years: SE", 100 * se_a, ".2f", "3.27")
chk("23 years: SE from printed", 22.207 / sqrt(46), ".2f", "3.27")
chk("23 years: low", 100 * (c.S_ANN - Z * se_a), ".1f", "15.8")
chk("23 years: high", 100 * (c.S_ANN + Z * se_a), ".1f", "28.6")
chk("23 years: low, printed", 22.207 - 1.96 * 3.27, ".1f", "15.8")
chk("23 years: high, printed", 22.207 + 1.96 * 3.27, ".1f", "28.6")
daily_based = sqrt(246) * c.S_RW
se_daily = daily_based * sqrt((c.KURT_RW - 1) / (4 * len(c.R_W)))
chk("LM17's 18.563%", 100 * daily_based, ".3f", "18.563")
chk("its SE", 100 * se_daily, ".2f", "0.34")
gap = c.S_ANN - daily_based
chk("gap", 100 * gap, ".1f", "3.6")
chk("gap in SEs", gap / se_a, ".1f", "1.1")
chk("gap in SEs, printed", (22.207 - 18.563) / 3.27, ".1f", "1.1")
anchor("A20-31", "SE", 100 * se_a, "3.274253")
anchor("A20-31", "low", 100 * (c.S_ANN - Z * se_a), "15.78953")
anchor("A20-31", "high", 100 * (c.S_ANN + Z * se_a), "28.62460")
anchor("A20-31", "daily-based", 100 * daily_based, "18.5628494")
anchor("A20-31", "its SE", 100 * se_daily, "0.338834")
anchor("A20-31", "gap", 100 * gap, "3.64422")
anchor("A20-31", "gap in SEs", gap / se_a, "1.11299")
c_lo, c_hi = float(stats.chi2.ppf(0.025, 22)), float(stats.chi2.ppf(0.975, 22))
chk("chi2 2.5%", c_lo, ".2f", "10.98")
chk("chi2 97.5%", c_hi, ".2f", "36.78")
chk("chi2 interval low", 100 * c.S_ANN * sqrt(23 / c_hi), ".1f", "17.6")
chk("chi2 interval high", 100 * c.S_ANN * sqrt(23 / c_lo), ".1f", "32.1")
chk("chi2 interval low, printed", 22.207 * sqrt(23 / 36.78), ".1f", "17.6")
chk("chi2 interval high, printed", 22.207 * sqrt(23 / 10.98), ".1f", "32.1")
anchor("A20-32", "chi2 low", c_lo, "10.9823")
anchor("A20-32", "chi2 high", c_hi, "36.7807")
anchor("A20-32", "interval low", 100 * c.S_ANN * sqrt(23 / c_hi), "17.56083")
anchor("A20-32", "interval high", 100 * c.S_ANN * sqrt(23 / c_lo), "32.13720")
regs = {}
for lab, x in (("before", c.R[c.PRE]), ("from", c.R[~c.PRE])):
    _, sx, _, m4x = c.moments(x)
    regs[lab] = (sx, sx * sqrt((m4x / sx**4 - 1) / (4 * len(x))))
chk("regime 1 s", 100 * regs["before"][0], ".3f", "1.257")
chk("regime 1 s SE", 100 * regs["before"][1], ".3f", "0.026")
chk("regime 2 s", 100 * regs["from"][0], ".3f", "1.152")
chk("regime 2 s SE", 100 * regs["from"][1], ".3f", "0.035")
anchor("A20-39", "s before", 100 * regs["before"][0], "1.2570342")
anchor("A20-39", "SE before", 100 * regs["before"][1], "0.0263120")
anchor("A20-39", "s from", 100 * regs["from"][0], "1.1516693")
anchor("A20-39", "SE from", 100 * regs["from"][1], "0.0347108")
# (20.9) against a brute-force delta method with numerical gradients
cov2 = np.array([[S**2, c.M3], [c.M3, c.M4 - S**4]]) / T
for h_, se_ in ((lambda m, v: m / v, se_k), (lambda m, v: m / sqrt(v), se_s)):
    g = np.array([(h_(RB + 1e-9, S**2) - h_(RB - 1e-9, S**2)) / 2e-9,
                  (h_(RB, S**2 + 1e-11) - h_(RB, S**2 - 1e-11)) / 2e-11])
    assert abs(sqrt(float(g @ cov2 @ g)) / se_ - 1) < 1e-5
# 0050
k5 = c.MU50 / c.S50**2
se5 = c.se_kelly(c.MU50, c.S50, c.M3_50, c.M4_50, c.T50)
se5m = 1 / (c.S50 * sqrt(c.T50))
se5n = c.se_kelly(c.MU50, c.S50, 0.0, 3 * c.S50**4, c.T50)
chk("0050 f", k5, ".2f", "5.68")
chk("0050 mean-only SE (text)", se5m, ".2f", "1.50")
chk("0050 mean-only SE (table)", se5m, ".3f", "1.499")
chk("0050 normal SE (table)", se5n, ".3f", "1.506")
chk("0050 plug-in SE (text)", se5, ".2f", "1.53")
chk("0050 plug-in SE (table)", se5, ".3f", "1.532")
chk("0050 band low", k5 - Z * se5m, ".2f", "2.74")
chk("0050 band high", k5 + Z * se5m, ".2f", "8.62")
chk("0050 interval low", k5 - Z * se5, ".2f", "2.68")
chk("0050 interval high", k5 + Z * se5, ".2f", "8.68")
chk("0050 band low, printed", 5.68 - 1.96 * 1.50, ".2f", "2.74")
chk("0050 band high, printed", 5.68 + 1.96 * 1.50, ".2f", "8.62")
chk("0050 interval low, printed", 5.68 - 1.96 * 1.53, ".2f", "2.68")
chk("0050 interval high, printed", 5.68 + 1.96 * 1.53, ".2f", "8.68")
assert f"{k5 - Z * se5m:.1f}" == "2.7" and f"{k5 + Z * se5m:.1f}" == "8.6"      # LM4's 2.7 to 8.6
lm4 = (c.MU50 - Z * c.S50 / sqrt(c.T50)) / c.S50**2, (c.MU50 + Z * c.S50 / sqrt(c.T50)) / c.S50**2
assert abs(lm4[0] - (k5 - Z * se5m)) < 1e-12 and abs(lm4[1] - (k5 + Z * se5m)) < 1e-12
has("LM4's bands", "[[LM4]]'s quadratic 2.7 to 8.6")
has("LM4's exact band", "[[LM4]]'s exact band, 2.7 to 7.6")
chk("0050 skewness", c.M3_50 / c.S50**3, ".2f", "0.04")
chk("0050 kurtosis", c.M4_50 / c.S50**4, ".2f", "11.12")
anchor("A20-30", "f", k5, "5.679608")
anchor("A20-30", "mean-only SE", se5m, "1.498823")
anchor("A20-30", "band low", k5 - Z * se5m, "2.741915")
anchor("A20-30", "band high", k5 + Z * se5m, "8.617301")
anchor("A20-30", "plug-in SE", se5, "1.532115")
anchor("A20-30", "interval low", k5 - Z * se5, "2.676662")
anchor("A20-30", "interval high", k5 + Z * se5, "8.682553")
anchor("A20-30", "skewness", c.M3_50 / c.S50**3, "0.036675")
anchor("A20-30", "kurtosis", c.M4_50 / c.S50**4, "11.120502")
has("0050 dates", "3 November 2014 to 8 October 2026")
assert c.DATES50 == ("2014-11-03", "2026-10-08")
for row in ("| Annual volatility, %, TR23 | 18.96 | — | 0.175 | 0.334 | 18.3 to 19.6 |",
            "| Kelly fraction $\\hat f$, TR23 | 4.28 | 1.082 | 1.085 | 1.111 | 2.10 to 6.46 |",
            "| Kelly fraction $\\hat f$, 0050 | 5.68 | 1.499 | 1.506 | 1.532 | 2.68 to 8.68 |",
            "| Sharpe ratio a day, TR23 | 0.0517 | — | 0.0131 | 0.0132 | 0.0258 to 0.0776 |",
            "| Sharpe ratio a year, TR23 | 0.81 | — | 0.205 | 0.207 | 0.40 to 1.22 |"):
    has("delta table row", norm_text(row))
has("23.7645 in KC 7", "0.205 for TR23's 23.7645 years")

# ====================================================================== Section 8: Hill
counts = {x0: c.count_le(x0) for x0 in ("0.02", "0.03", "0.04", "0.05", "0.06")}
cnt = list(counts.values())
chords = [log(cnt[i] / cnt[j]) / log((j + 2) / (i + 2)) for i in range(5) for j in range(i + 1, 5)]
chk("LM15's lowest chord", min(chords), ".2f", "2.09")
chk("LM15's highest chord", max(chords), ".2f", "5.03")
hl = {}
for x0, a_p, e_p, k_p in (("0.02", "2.49", "0.16", "252"), ("0.04", "4.93", "0.74", "44"),
                          ("0.05", "4.76", "1.23", "15")):
    kk, aa, ee = c.hill(x0)
    hl[x0] = (kk, aa, ee)
    chk(f"Hill k at {x0}", kk, "d", k_p)
    chk(f"Hill at {x0}", aa, ".2f", a_p)
    chk(f"Hill SE at {x0}", ee, ".2f", e_p)
    chk(f"Hill SE at {x0}, from printed", float(a_p) / sqrt(kk), ".2f", e_p)
has("E10 k list", "from $k$ = 252, 44 and 15")
has("hill note k list", "with $k$ = 252, 108, 44 and 15")
for x0, lo_p, hi_p in (("0.02", "2.2", "2.8"), ("0.04", "3.5", "6.4")):
    kk, aa, ee = hl[x0]
    chk(f"P10 low {x0}", aa - Z * ee, ".1f", lo_p)
    chk(f"P10 high {x0}", aa + Z * ee, ".1f", hi_p)
    a_p, e_p = float(f"{aa:.2f}"), float(f"{ee:.2f}")
    chk(f"P10 low {x0}, printed", a_p - 1.96 * e_p, ".1f", lo_p)
    chk(f"P10 high {x0}, printed", a_p + 1.96 * e_p, ".1f", hi_p)
assert hl["0.02"][1] + Z * hl["0.02"][2] < hl["0.04"][1] - Z * hl["0.04"][2]      # the intervals do not overlap
width5 = 2 * Z * hl["0.05"][2]
chk("KC 8: width at 5%", width5, ".1f", "4.8")
chk("KC 8: width, printed", 2 * 1.96 * 1.23, ".1f", "4.8")
for x0, shown_k, shown_a, shown_e in (("0.02", "252", "2.489927", "0.156851"), ("0.04", "44", "4.932313", "0.743574"),
                                      ("0.05", "15", "4.763056", "1.229816")):
    kk, aa, ee = hl[x0]
    anchor("A20-34", f"k {x0}", kk, shown_k)
    anchor("A20-34", f"alpha {x0}", aa, shown_a)
    anchor("A20-34", f"SE {x0}", ee, shown_e)
anchor("A20-34", "width at 5%", width5, "4.82088")
# the Hill estimator is the Pareto MLE: the log-likelihood's root
xs3 = -c.R[c.R <= -0.03 + EPS]
llp = lambda a: len(xs3) * log(a) + len(xs3) * a * log(0.03) - (a + 1) * float(np.log(xs3).sum())
assert llp(a3) > llp(a3 * 1.001) and llp(a3) > llp(a3 * 0.999)
has("Hill note range", "from 1.0% to 6.0% in steps of 0.05 points")

# ====================================================================== Section 9: the printed code, run against the lab's data
code = re.search(r"## Estimation in Python.*?```python\n(.*?)```", RAW, re.DOTALL)
assert code
src_code = code.group(1)
assert max(len(line) for line in src_code.splitlines()) <= 80
printed_out: list[str] = []
env: dict = {"print": lambda *a: printed_out.append(" ".join(str(x) for x in a))}
with tempfile.TemporaryDirectory() as tmp:
    # the lab's file when data/make_lab_data.py has built it; otherwise the same closes from TR23's parquet
    csv = LAB_DATA
    if not csv.exists():
        csv = Path(tmp) / "taiex_tr.csv"
        csv.write_text("date,price\n" + "".join(f"{d},{p:.2f}\n" for d, p in zip(c.DATES_ALL, c.TR, strict=True)),
                       encoding="utf-8", newline="\n")
    exec(compile(src_code.replace('"data/taiex_tr.csv"', repr(str(csv))), "lm20.md code", "exec"), env)  # noqa: S102 - the module's own code block
assert env["T"] == T
chk("code: s", 100 * float(env["s"]), ".6f", "1.208364")
chk("code: s_u", 100 * float(env["s_u"]), ".6f", "1.208468")
chk("code: se_mean", 100 * float(env["se_mean"]), ".5f", "0.01580")
chk("code: q", float(env["q"]), ".5f", "1.96037")
assert np.allclose(env["fit"].x, c.P_T, rtol=0, atol=1e-6), env["fit"].x
assert len(printed_out) == 3, printed_out
for h_ in ([1e-4, 1e-5, 1e-5], [1e-3, 1e-4, 1e-4]):
    se_code = np.sqrt(np.diag(np.linalg.inv(c.hessian(env["nll"], env["fit"].x, np.array(h_)))))
    assert [f"{se_code[0]:.3f}", f"{se_code[1]:.4f}", f"{se_code[2]:.4f}"] == ["0.144", "0.0124", "0.0138"], se_code
qs = env["np"].quantile(env["vol"], [0.025, 0.975], method="inverted_cdf")
assert [f"{100 * v:.1f}" for v in qs] == ["17.3", "20.6"], qs
has("code comment: SEs", "# 0.144, 0.0124, 0.0138 both times")
has("code comment: s", "# 1.208364%, 1.208468%")
has("code comment: T", "# T = 5,849 simple returns")
has("Nelder-Mead default tolerance", "a tolerance of $10^{-4}$")
chk("KC 9: Polars std", 100 * SU, ".6f", "1.208468")
chk("KC 9: NumPy std", 100 * S, ".6f", "1.208364")
anchor("A20-03", "s, six decimals", 100 * S, "1.2083643417")

# ====================================================================== practice problems and solutions
chk("P1: 20/sqrt(10)", 20 / sqrt(10), ".2f", "6.32")
chk("P1: /sqrt(54)", 20 / sqrt(10) / sqrt(54), ".2f", "0.86")
chk("P1: 10 years of sessions", round(10 * 246.12), ",", "2,461")
chk("P1: 20/sqrt(2461)", 20 / sqrt(2461), ".2f", "0.40")
anchor("A20-40", "6.32", 20 / sqrt(10), "6.324555")
anchor("A20-40", "0.86", 20 / sqrt(10) / sqrt(54), "0.860663")
anchor("A20-40", "0.40", 20 / sqrt(2461), "0.403157")
chk("P2: 23/22 - 1", 100 * (23 / 22 - 1), ".1f", "4.5")
chk("P2: sqrt(23/22) - 1", 100 * (sqrt(23 / 22) - 1), ".1f", "2.2")
anchor("A20-41", "4.5", 100 * (23 / 22 - 1), "4.54545")
anchor("A20-41", "2.2", 100 * (sqrt(23 / 22) - 1), "2.24747")
has("P3: about 22 points", "spread about 22 points")
assert f"{100 * c.S_ANN:.0f}" == "22"
chk("P4: s", 100 * c.S_ANN, ".2f", "22.21")
chk("P4: s_u", 100 * c.SU_ANN, ".2f", "22.71")
chk("P4: LM17's", 100 * daily_based, ".2f", "18.56")
chk("P5: normal", 100 * se_vol_n, ".2f", "0.18")
chk("P5: normal, printed", 18.96 / sqrt(2 * 5849), ".2f", "0.18")
chk("P5: without the 2, printed", 18.96 / sqrt(5849), ".2f", "0.25")
anchor("A20-42", "normal", 100 * se_vol_n, "0.175274")
anchor("A20-42", "plug-in", 100 * se_vol_k, "0.334127")
# Problem 6
z1 = (c.X1 - c.X1.mean()) / c.X1.std(ddof=0)
z2 = (c.X2 - c.X2.mean()) / c.X2.std(ddof=0)
rho = float((z1 * z2).mean())
TU = c.U28_T
L_t = z1 * z2 - rho / 2 * (z1**2 + z2**2)
se_rn = (1 - rho**2) / sqrt(TU)
se_rm = float(L_t.std(ddof=0)) / sqrt(TU)
chk("P6: rho", rho, ".4f", "0.5749")
chk("P6: normal SE", se_rn, ".4f", "0.0101")
chk("P6: normal SE from printed", (1 - 0.5749**2) / sqrt(4382), ".4f", "0.0101")
chk("P6: normal low", rho - Z * se_rn, ".3f", "0.555")
chk("P6: normal high", rho + Z * se_rn, ".3f", "0.595")
chk("P6: normal low, printed", 0.5749 - 1.96 * 0.0101, ".3f", "0.555")
chk("P6: normal high, printed", 0.5749 + 1.96 * 0.0101, ".3f", "0.595")
chk("P6: plug-in SE", se_rm, ".4f", "0.0153")
chk("P6: plug-in low", rho - Z * se_rm, ".3f", "0.545")
chk("P6: plug-in high", rho + Z * se_rm, ".3f", "0.605")
chk("P6: plug-in low, printed", 0.5749 - 1.96 * 0.0153, ".3f", "0.545")
chk("P6: plug-in high, printed", 0.5749 + 1.96 * 0.0153, ".3f", "0.605")
chk("P6: ratio", se_rm / se_rn, ".2f", "1.51")
chk("P6: ratio, printed", 0.0153 / 0.0101, ".2f", "1.51")
anchor("A20-04", "rho", rho, "0.5748584673")
anchor("A20-43", "normal SE", se_rn, "0.01011437")
anchor("A20-43", "plug-in SE", se_rm, "0.01529192")
anchor("A20-43", "ratio", se_rm / se_rn, "1.511900")
# (a) and (b) by simulation of a normal pair at rho = 0.5749 (a check; nothing printed)
rng_p6 = np.random.default_rng(6)
xa = rng_p6.standard_normal(2_000_000)
ya = rho * xa + sqrt(1 - rho**2) * rng_p6.standard_normal(2_000_000)
assert abs(float((xa**3 * ya).mean()) - 3 * rho) < 0.02 and abs(float((xa**2 * ya**2).mean()) - (1 + 2 * rho**2)) < 0.02
La = xa * ya - rho / 2 * (xa**2 + ya**2)
assert abs(float(La.var()) - (1 - rho**2) ** 2) < 0.01
assert abs(float(((xa**2 + ya**2) ** 2).mean()) - (8 + 4 * rho**2)) < 0.05
# Problem 7
dnu = reg["from"][1] - reg["before"][1]
sed = sqrt(reg["from"][2] ** 2 + reg["before"][2] ** 2)
chk("P7: difference", dnu, ".3f", "0.247")
chk("P7: SE", sed, ".3f", "0.296")
chk("P7: SE from printed", sqrt(0.195**2 + 0.223**2), ".3f", "0.296")
chk("P7: ratio", dnu / sed, ".1f", "0.8")
anchor("A20-44", "difference", dnu, "0.2472941")
anchor("A20-44", "SE", sed, "0.2956888")
# Problem 8
months = sorted({d[:7] for d in c.DATES})
mcount = np.array([sum(1 for d, q in zip(c.DATES, c.RF) if d[:7] == mo and (q <= Fraction("-0.03") or q >= Fraction("0.03")))
                   for mo in months], dtype=np.float64)
mcount_g = np.array([int((np.array([d[:7] == mo for d in c.DATES]) & ((c.R <= -0.03 + EPS) | (c.R >= 0.03 - EPS))).sum())
                     for mo in months], dtype=np.float64)
assert np.array_equal(mcount, mcount_g)
lam = float(mcount.mean())
chk("P8: months", len(months), "d", "286")
chk("P8: total", int(mcount.sum()), "d", "175")
chk("P8: lambda", lam, ".5f", "0.61189")
chk("P8: lambda as 175/286", 175 / 286, ".5f", "0.61189")
chk("P8: Poisson SE", sqrt(lam / len(months)), ".5f", "0.04625")
chk("P8: Poisson SE from printed", sqrt(0.61189 / 286), ".5f", "0.04625")
chk("P8: counts' SE", float(mcount.std(ddof=0)) / sqrt(len(months)), ".4f", "0.0803")
chk("P8: variance/mean", float(mcount.var(ddof=0)) / lam, ".4f", "3.0167")
chk("P8: variance/mean (LM15's)", float(mcount.var(ddof=0)) / lam, ".2f", "3.02")
chk("P8: ratio", float(mcount.std(ddof=0)) / sqrt(lam), ".3f", "1.737")
chk("P8: sqrt(3.0167)", sqrt(3.0167), ".3f", "1.737")
anchor("A20-45", "lambda", lam, "0.611888112")
anchor("A20-45", "Poisson SE", sqrt(lam / len(months)), "0.046254394")
anchor("A20-45", "variance/mean", float(mcount.var(ddof=0)) / lam, "3.01668332")
anchor("A20-45", "counts' SE", float(mcount.std(ddof=0)) / sqrt(len(months)), "0.08033741")
anchor("A20-45", "ratio", float(mcount.std(ddof=0)) / sqrt(lam), "1.7368602")
# Problem 9
up = int((c.R > EPS).sum())
assert up == sum(1 for q in c.RF if q > 0)
th = up / T
se_th = sqrt(th * (1 - th) / T)
chk("P9: up days", up, ",", "3,205")
chk("P9: theta-hat", th, ".4f", "0.5480")
chk("P9: SE", se_th, ".4f", "0.0065")
chk("P9: SE from printed", sqrt(0.5480 * 0.4520 / 5849), ".4f", "0.0065")
chk("P9: low", th - Z * se_th, ".3f", "0.535")
chk("P9: high", th + Z * se_th, ".3f", "0.561")
chk("P9: low, printed", 0.5480 - 1.96 * 0.0065, ".3f", "0.535")
chk("P9: high, printed", 0.5480 + 1.96 * 0.0065, ".3f", "0.561")
anchor("A20-46", "theta-hat", th, "0.54795692")
anchor("A20-46", "SE", se_th, "0.00650762")
anchor("A20-46", "low", th - Z * se_th, "0.5352020")
anchor("A20-46", "high", th + Z * se_th, "0.5607119")
has("P9: LM17's 9,604", "[[LM17]]'s 9,604")
# Problem 11 (experiment 3)
rng3 = np.random.default_rng([3, c.SEED_ROOT])
xs3_ = rng3.standard_normal((20_000, 5))
c3z = float((np.abs(xs3_.mean(axis=1)) <= Z * xs3_.std(axis=1, ddof=0) / sqrt(5)).mean())
c3t = float((np.abs(xs3_.mean(axis=1)) <= stats.t.ppf(0.975, 4) * xs3_.std(axis=1, ddof=1) / sqrt(5)).mean())
ez5 = 2 * float(stats.t.cdf(Z * sqrt(4 / 5), 4)) - 1
chk("P11: z coverage", 100 * c3z, ".1f", "84.3")
chk("P11: t coverage", 100 * c3t, ".1f", "94.8")
chk("P11: z MC SE", 100 * sqrt(c3z * (1 - c3z) / 20_000), ".2f", "0.26")
chk("P11: t MC SE", 100 * sqrt(c3t * (1 - c3t) / 20_000), ".2f", "0.16")
chk("P11: exact", 100 * ez5, ".1f", "84.6")
chk("P11: gap", 100 * (ez5 - c3z), ".1f", "0.2")
assert 0.7 < (ez5 - c3z) / sqrt(c3z * (1 - c3z) / 20_000) < 1.3          # "about one Monte Carlo standard error"
chk("exact T=5 (coverage table)", 100 * exact[5], ".1f", "84.6")
anchor("A20-47", "z", 100 * c3z, "84.320")
anchor("A20-47", "t", 100 * c3t, "94.770")
anchor("A20-47", "exact", 100 * ez5, "84.55399")
has("P11 seed", "`default_rng([3, 20261011])`, draw `standard_normal((20000, 5))`")
# Problem 12
srd = 0.5 / sqrt(246.12)
yrs12 = (1 + srd**2 / 2) / 0.1**2
chk("P12: years", yrs12, ".2f", "100.05")
chk("P12: B", 1 / 0.1, ".0f", "10")
chk("P12: C", 1.96**2 / 0.1**2, ".0f", "384")
anchor("A20-48", "years", yrs12, "100.05")

# ====================================================================== the chart files (written by data/lm20_charts.py)
for name in ("lm20-sampling-mean", "lm20-sampling-vol", "lm20-merton", "lm20-years", "lm20-profile", "lm20-hill",
             "lm20-coverage"):
    spec = json.loads(chart_text(name))
    assert spec["alt"].strip()
    n_bytes = len(json.dumps(spec, separators=(",", ":")).encode("utf-8"))
    assert n_bytes < 300_000, (name, n_bytes)
    print(f"     {name}.json: {n_bytes:,} bytes")
in_chart("years: TR23's line", "lm20-years", "TR23's annual mean, 15.38%")
in_chart("years: vline", "lm20-years", "TR23, 23.76 years")
in_chart("profile: points", "lm20-profile", "2.80")
in_chart("profile: points", "lm20-profile", "3.37")
in_chart("profile: points", "lm20-profile", "2.78")
in_chart("profile: points", "lm20-profile", "3.35")
in_chart("hill: t line", "lm20-hill", "Student-t fit, 3.065")
in_chart("hill: point labels", "lm20-hill", "3% (k = 108): 3.63")
in_chart("merton: iid line value", "lm20-merton", "3.90")
widget = json.loads(chart_text("lm20-coverage"))["widget"]
for n, shown in ((5, "2.7764"), (10, "2.2622"), (20, "2.0930"), (30, "2.0452"), (100, "1.9842"), (250, "1.9695")):
    assert f"{widget['tq'][n - 2]:.4f}" == shown, (n, widget["tq"][n - 2])
    assert f"{tq[n]:.4f}" == shown
assert widget["Rbar"] == round(RB, 12) and widget["s"] == round(S, 12)

# ====================================================================== structure: labels, citations, tags
ex_labels = re.findall(r"\[!exhibit\][^\n]*\{#([\w-]+)\}", RAW)
eg_labels = re.findall(r"\[!example\][^\n]*\{#([\w-]+)\}", RAW)
print(f"labels: {len(ex_labels)} exhibits {ex_labels}, {len(eg_labels)} examples {eg_labels}")
assert len(set(ex_labels)) == len(ex_labels) and len(set(eg_labels)) == len(eg_labels)
assert not set(ex_labels) & set(eg_labels)
for lab in ex_labels:
    assert f"[[ex:{lab}]]" in RAW, f"exhibit {lab} is never cited"
for kind, lab in re.findall(r"\[\[(ex|eg):([\w-]+)\]\]", RAW):
    assert lab in (ex_labels if kind == "ex" else eg_labels), (kind, lab)
tags = re.findall(r"\\tag\{(20\.\d+)\}", RAW)
assert tags == [f"20.{i}" for i in range(1, 11)], tags
assert "\t" not in RAW

# ====================================================================== report
body = TEXT.split("\n## Glossary", 1)[0]
nums = set(re.findall(r"(?<![\w.])\d+\.\d+|(?<![\w.,])\d{1,3}(?:,\d{3})+", body))
left = sorted(n for n in nums if n not in COVERED)
print(f"\nnumbers with a decimal point or thousands separator not covered by a check ({len(left)}):")
print("   " + " ".join(left))
print(f"\nvalues within a tenth of a unit of a rounding boundary at their printed precision ({len(FLAGGED)}):")
for f_ in FLAGGED:
    print("   ", f_)
print(f"\nanchor differences ({len(ANCHOR_DIFFS)}):")
for a_ in ANCHOR_DIFFS:
    print("   ", a_)
print(f"\nall {N_CHECKS} checks passed")
