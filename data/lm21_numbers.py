"""Every number that LM21 (Hypothesis Testing and Multiple Testing) prints, computed and checked against src/lm21.md.

Run:  uv run python data/lm21_numbers.py
      (after data/vol3_series.py has built TR23, data/vol2_series.py the U28 sample, and data/lm21_charts.py the charts)

Input: data/processed/vol3_taiex.parquet (TR23, through data/lm21_common.py) and, only to recount LM16's printed counts
(A21-61), U28 through data/lm10_series.py. Reads src/lm21.md, src/data/lm21-*.json and plans/vol-4-anchors.md.
Writes nothing.

Conventions (src/lm21.md; plans/vol-4.md, the LM21 brief and the shared decisions): T = 5,849 simple daily returns
R_t from 2003-01-03; s divides by T, s_u by T - 1; the t-stat of a mean is (21.1) with s_u, the two-sample statistic
(21.3) uses unpooled divisor-(n - 1) variances; p-values are two-sided against the standard normal unless the text
says otherwise; years = calendar days / 365.25 (exactly 4 days / 1461), A = T / years. The calendar family is the 12
months and the 5 weekdays, each against all other returns (the 23 Saturday sessions belong to every "rest"). Counts
against a threshold use the guard (R > 1e-12, R <= -0.03 + 1e-12, statistics >= x - 1e-12) and are recounted exactly
with Fraction on the two-decimal closes; constructed p-values are compared as Fractions. Experiments 8, 10 and 11
create np.random.default_rng([e, 20261011]) once at their start. Monte Carlo errors: a share by (18.2) on indicators,
a mean by s / sqrt(B), E10's standard deviation by LM18's batch standard error (20 batches of 500, divisor 20).

Checks (each failure is collected; the script exits 1 after printing them all):
  chk(aid, label, value, printed)   the unrounded value rounds to the printed string at the string's own precision (an
                                    exact rational is rounded exactly; an exact tie fails), the printed string occurs in
                                    the module as a whole number, and a value within a tenth of a last-digit unit of a
                                    rounding boundary is reported as NEAR (plans/vol-4.md, "Rounding").
  sci(aid, label, value, mant, ex)  a number printed as mant\\times10^{ex}.
  has(label, text)                  a literal string (a date, a phrase, a table row) is in the module.
  anchor(aid, line)                 compares the anchors script's line with plans/vol-4-anchors.md and reports a
                                    difference (never forced).
At the end the script lists the module's numbers that no check covered, the NEAR flags and the anchor differences,
and prints "all N checks passed".
"""
import inspect
import json
import re
import sys
from fractions import Fraction
from math import comb, floor, log, log10, sqrt
from pathlib import Path

import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lm10_series import S5, u28
from lm21_common import (
    C80,
    C95,
    C975,
    EPS,
    MO_NAMES,
    WD_NAMES,
    bh_count,
    bonf_count,
    calendar,
    experiment8,
    experiment10,
    holm_count,
    load,
    maxq,
    p2,
    power,
    rng,
    two_sample,
    years80,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MD = ROOT / "src" / "lm21.md"
CHARTS = ROOT / "src" / "data"
ANCHORS = ROOT / "plans" / "vol-4-anchors.md"


def norm_text(s: str) -> str:
    """The module with TeX thousands separators, escaped percent signs, \\text{} and minus signs made plain."""
    s = s.replace("{,}", ",").replace("\\%", "%").replace("\u2212", "-").replace("\\,", "")
    return re.sub(r"\\text\{\s*([^}]*)\}", r" \1", s)


RAW = MD.read_text(encoding="utf-8")
TEXT = norm_text(RAW)
N_CHECKS = 0
COVERED: set[str] = set()
FAILS: list[str] = []
NEARS: list[str] = []
ANCHOR_DIFFS: list[str] = []


def in_text(printed: str) -> bool:
    """The printed number appears as a whole number (2.36 is not inside 2.363, 0.10 not inside 10.10)."""
    return re.search(r"(?<![\d.])" + re.escape(printed) + r"(?![\d])", TEXT) is not None


def rounds_to(value: float | np.integer | Fraction, shown: str) -> tuple[str, bool, bool]:
    """(the value rounded at the precision of shown, NEAR, exact tie) for a printed form such as 1,194.95 or -0.01."""
    want = shown.replace(",", "")
    d = len(want.split(".")[1]) if "." in want else 0
    if isinstance(value, (int, np.integer)):
        value = Fraction(int(value))
    if isinstance(value, Fraction):
        u = abs(value) * Fraction(10) ** d
        n = floor(u)
        frac = u - n
        tie, near = frac == Fraction(1, 2), abs(frac - Fraction(1, 2)) < Fraction(1, 10)
        if frac > Fraction(1, 2):
            n += 1
        digits = str(n).rjust(d + 1, "0")
        got = digits[:-d] + "." + digits[-d:] if d else digits
        if value < 0 and n:
            got = "-" + got
        return got, near, tie
    x = float(value)
    uf = abs(x) * 10.0**d
    r = uf - floor(uf)
    got = f"{x:.{d}f}"
    if got.startswith("-") and float(got) == 0:
        got = got[1:]
    return got, abs(r - 0.5) < 0.1, r == 0.5


def chk(aid: str, label: str, value: float | np.integer | Fraction, shown: str, in_md: bool = True) -> None:
    """A printed number against its unrounded value, at the printed precision; it must occur in the module."""
    global N_CHECKS
    got, near, tie = rounds_to(value, shown)
    want = shown.replace(",", "")
    ok = got == want and not tie and (not in_md or in_text(shown))
    print(f"CHECK {aid} {label}: {float(value)!r} -> {got} (printed {shown}) {'ok' if ok else 'MISMATCH'}")
    if tie:
        FAILS.append(f"{aid} {label}: {value} is an exact tie at {shown}; print more digits")
    elif got != want:
        FAILS.append(f"{aid} {label}: {value} rounds to {got}, printed {shown}")
    if in_md and not in_text(shown):
        FAILS.append(f"{aid} {label}: {shown!r} not found in src/lm21.md")
    if near:
        NEARS.append(f"NEAR {aid} {label}: {float(value)!r} printed {shown}")
    COVERED.add(shown.lstrip("-"))
    N_CHECKS += 1


def sci(aid: str, label: str, value: float, mant: str, ex: int) -> None:
    """A number printed as mant\\times10^{ex}; mant carries the printed significant figures."""
    global N_CHECKS
    d = len(mant.split(".")[1]) if "." in mant else 0
    got = f"{value:.{d}e}"
    want = f"{mant}e{ex:+03d}"
    tex = f"{mant}\\times10^{{{ex}}}"
    ok = got == want and tex in TEXT
    print(f"CHECK {aid} {label}: {value!r} -> {got} (printed {tex}) {'ok' if ok else 'MISMATCH'}")
    if got != want:
        FAILS.append(f"{aid} {label}: {value} is {got}, printed {want}")
    if tex not in TEXT:
        FAILS.append(f"{aid} {label}: {tex!r} not found in src/lm21.md")
    m = abs(value) / 10.0**ex
    r = m * 10**d - floor(m * 10**d)
    if abs(r - 0.5) < 0.1:
        NEARS.append(f"NEAR {aid} {label}: {value!r} printed {tex}")
    COVERED.add(mant)
    N_CHECKS += 1


def has(label: str, text: str) -> None:
    global N_CHECKS
    text = norm_text(text)
    ok = text in TEXT
    print(f"CHECK {label}: {text!r} in text {'ok' if ok else 'MISSING'}")
    if not ok:
        FAILS.append(f"{label}: {text!r} not found in src/lm21.md")
    for num in re.findall(r"\d[\d,]*\.?\d*", text):
        COVERED.add(num.rstrip(".,"))
    N_CHECKS += 1


def _anchor_values() -> dict[str, str]:
    rows: dict[str, str] = {}
    sec = ANCHORS.read_text(encoding="utf-8").split("\n## LM21", 1)[1].split("\n## ", 1)[0]
    for line in sec.splitlines():
        if line.startswith("| A21-"):
            cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
            rows[cells[0]] = cells[3].strip("`")
    return rows


ANCHOR_ROWS = _anchor_values()
assert len(ANCHOR_ROWS) == 61, len(ANCHOR_ROWS)


def anchor(aid: str, got: str) -> None:
    """Compare the anchors script's line with plans/vol-4-anchors.md; a difference is reported, not forced."""
    expected = ANCHOR_ROWS[aid]
    tag = "ok" if got == expected else "DIFFERS"
    print(f"ANCHOR {aid}: {tag}")
    if got != expected:
        ANCHOR_DIFFS.append(f"{aid}: script {got} | anchor {expected}")


# ====================================================================== data: TR23 (notation note, case)
d = load()
R, T, RF, dates, dates_all = d.R, d.T, d.RF, d.dates, d.dates_all
assert (len(dates_all), T, str(dates_all[0]), str(dates[0]), str(dates[-1])) == (
    5850, 5849, "2003-01-02", "2003-01-03", "2026-10-08")
Rb, s, su = float(R.mean()), float(R.std(ddof=0)), float(R.std(ddof=1))
se = su / sqrt(T)
tstat = Rb / se
anchor("A21-01", f"{len(dates_all)} closes, {dates_all[0]} -> {dates_all[-1]}")
anchor("A21-02", f"{T} returns, {dates[0]} -> {dates[-1]}")
anchor("A21-03", f"{d.days} days; {d.years:.6f} years")
anchor("A21-04", f"{d.A:.6f}")
chk("A21-02", "T", T, "5,849")
chk("A21-03", "calendar days", d.days, "8,680")
chk("A21-03", "years", d.years_f, "23.7645")
chk("A21-03", "years, two decimals", d.years_f, "23.76")
chk("A21-03", "years, one decimal (zh boxes)", d.years_f, "23.8")
chk("A21-04", "A", Fraction(T) / d.years_f, "246.12")
for text in ("3 January 2003", "8 October 2026", "retrieved 18 October 2026", "1 June 2015"):
    has("dates", text)
i_pre = int(d.pre.sum())
anchor("A21-05", f"before 2015-06-01: {i_pre} returns ({dates[0]} -> {dates[i_pre - 1]}); from 2015-06-01: {T - i_pre} "
       f"({dates[i_pre]} -> {dates[-1]})")
chk("A21-05", "returns before 1 June 2015", i_pre, "3,077")
chk("A21-05", "returns from 1 June 2015", T - i_pre, "2,772")
anchor("A21-06", f"pairs {T - 1} ({dates[1]} -> {dates[-1]}); blocks {T // 20} of 20 ({T // 20 * 20} returns, last "
       f"{T % 20} excluded, {dates[T // 20 * 20]} -> {dates[-1]})")
chk("A21-06", "pairs", T - 1, "5,848")
chk("A21-06", "blocks", T // 20, "292")
chk("A21-06", "block returns", T // 20 * 20, "5,840")
cnt_wd = np.bincount(d.wd, minlength=7)
sats = [str(x) for x, w in zip(dates, d.wd) if w == 5]
anchor("A21-07", ", ".join(f"{WD_NAMES[k]} {cnt_wd[k]}" for k in range(7)) + f"; Saturdays: {', '.join(sats)}")
for k, shown in enumerate(("1,151", "1,181", "1,183", "1,168", "1,143", "23")):
    chk("A21-07", f"{WD_NAMES[k]} returns", cnt_wd[k], shown)
assert (sats[0][:4], sats[-1][:4], cnt_wd[6]) == ("2006", "2018", 0)
has("Saturday sessions", "23 Saturday sessions (2006–2018)")
has("TWSE's 2019 rule", "stopped trading on Saturday make-up workdays from 2019")
cnt_mo = np.bincount(d.mo, minlength=13)[1:]
anchor("A21-08", ", ".join(f"{MO_NAMES[k]} {cnt_mo[k]}" for k in range(12)))
has("month sizes", "450, 369, 532, 477, 503, 498, 524, 522, 491, 482, 492 and 509 days")
assert ", ".join(str(c) for c in cnt_mo[:11]) + f" and {cnt_mo[11]}" == "450, 369, 532, 477, 503, 498, 524, 522, 491, 482, 492 and 509"
has("weekday sizes", "1,151, 1,181, 1,183, 1,168 and 1,143 (Monday to Friday)")
up_x, dn_x, zero_x = sum(x > 0 for x in RF), sum(x < 0 for x in RF), sum(x == 0 for x in RF)
up_g = int((R > EPS).sum())
assert up_g == up_x and int((R < -EPS).sum()) == dn_x and zero_x == 0
anchor("A21-09", f"up {up_x}; down {dn_x}; zero {zero_x} (Fraction); guard count up {up_g}")
chk("A21-09", "up days", up_x, "3,205")
has("no zero return", "no return is exactly zero")

# ---------------------------------------------------------------- the case and Exhibit case
anchor("A21-10", f"{100 * Rb:.10f}% (printed {100 * Rb:.4f}%)")
chk("A21-10", "mean % a day", 100 * Rb, "0.0625")
anchor("A21-11", f"s_u {100 * su:.6f}%; s {100 * s:.6f}% (printed s_u {100 * su:.4f}%)")
chk("A21-11", "s_u %", 100 * su, "1.2085")
chk("A21-11", "s % (E5)", 100 * s, "1.2084")
chk("A21-11", "s % (case box)", 100 * s, "1.21")
near12 = " NEAR" if abs(tstat * 100 - floor(tstat * 100) - 0.5) < 0.1 else ""
anchor("A21-12", f"SE {100 * se:.7f}%; t-stat {tstat:.6f} (printed {tstat:.2f}{near12}); with s: {Rb / (s / sqrt(T)):.6f}")
chk("A21-12", "SE %", 100 * se, "0.0158")
chk("A21-12", "SE % from the printed s_u", 1.2085 / sqrt(5849), "0.0158")
chk("A21-12", "t-stat", tstat, "3.96")
chk("A21-12", "t-stat, X1", tstat, "3.956")
chk("A21-12", "t-stat with s", Rb / (s / sqrt(T)), "3.956")
reg_lines = []
reg = {}
for lab, x, shown in (("before", R[d.pre], ("0.0464", "1.2572", "0.0227", "2.05", "2.046", "0.041")),
                      ("from", R[~d.pre], ("0.0804", "1.1519", "0.0219", "3.68", "3.675", "0.00024"))):
    n = len(x)
    m_, su_ = float(x.mean()), float(x.std(ddof=1))
    t_ = m_ / (su_ / sqrt(n))
    reg[lab] = (m_, su_, t_)
    nr = " NEAR" if abs(t_ * 100 - floor(t_ * 100) - 0.5) < 0.1 else ""
    reg_lines.append(f"{lab} 2015-06-01: T {n}, mean {100 * m_:.6f}%, s_u {100 * su_:.5f}%, SE "
                     f"{100 * su_ / sqrt(n):.6f}%, t {t_:.5f} (printed {t_:.2f}{nr}), p {p2(t_):.6f}")
    for v, sh in zip((100 * m_, 100 * su_, 100 * su_ / sqrt(n), t_, t_, p2(t_)), shown):
        chk("A21-13", f"{lab} regime", v, sh)
anchor("A21-13", "; ".join(reg_lines))
wed, oth = R[d.wd == 2], R[d.wd != 2]
z_wed, se_wed = two_sample(wed, oth)
pw_wed = float(stats.ttest_ind(wed, oth, equal_var=False).pvalue)
anchor("A21-14", f"Wednesdays {len(wed)}: mean {100 * wed.mean():.5f}%; other days {len(oth)}: mean "
       f"{100 * oth.mean():.5f}%; difference {100 * (wed.mean() - oth.mean()):.5f}%; SE {100 * se_wed:.5f}%; z "
       f"{z_wed:.5f} (printed {z_wed:.2f}); p normal {p2(z_wed):.6f}; p SciPy ttest_ind(equal_var=False) {pw_wed:.6f}")
for v, sh in ((len(wed), "1,183"), (len(oth), "4,666"), (100 * float(wed.mean()), "0.1332"),
              (100 * float(oth.mean()), "0.0446"), (100 * float(wed.mean() - oth.mean()), "0.0886"),
              (100 * se_wed, "0.0375"), (z_wed, "2.36"), (z_wed, "2.363"), (p2(z_wed), "0.018")):
    chk("A21-14", "Wednesday", v, sh)
has("X1 row 4", "| Wednesdays minus other days | 1,183; 4,666 | 0.0886 | | 0.0375 | 2.363 | 0.018 |")
has("X1 row 1", "| All days | 5,849 | 0.0625 | 1.2085 | 0.0158 | 3.956 | $7.6\\times10^{-5}$ |")
has("X1 row 2", "| Before 1 June 2015 | 3,077 | 0.0464 | 1.2572 | 0.0227 | 2.046 | 0.041 |")
has("X1 row 3", "| From 1 June 2015 | 2,772 | 0.0804 | 1.1519 | 0.0219 | 3.675 | 0.00024 |")
hi = []
for k, shown in ((2, ("0.1405", "1.33")), (12, ("0.1270", "1.53"))):
    a, b = R[d.mo == k], R[d.mo != k]
    hi.append(f"{MO_NAMES[k - 1]} {len(a)} days, mean {100 * a.mean():.5f}%, z {two_sample(a, b)[0]:.4f}")
    chk("A21-15", f"{MO_NAMES[k - 1]} mean %", 100 * float(a.mean()), shown[0])
    chk("A21-15", f"{MO_NAMES[k - 1]} z", two_sample(a, b)[0], shown[1])
order = np.argsort([-R[d.mo == k].mean() for k in range(1, 13)])
anchor("A21-15", "; ".join(hi) + f"; months by mean: {', '.join(MO_NAMES[i] for i in order)}")
assert [MO_NAMES[i] for i in order[:2]] == ["Feb", "Dec"]
has("top months", "February (0.1405% a day, 1.33) and December (0.1270%, 1.53) have the highest monthly means")

# ---------------------------------------------------------------- the mean (E3), X2, the interval, the regimes (E4)
p_n, p_t, p_1 = p2(tstat), 2 * float(stats.t.sf(tstat, T - 1)), float(stats.norm.sf(tstat))
anchor("A21-16", f"two-sided: normal {p_n:.4e}, t_(T-1) {p_t:.4e}; one-sided normal {p_1:.4e}")
sci("A21-16", "two-sided normal p", p_n, "7.6", -5)
sci("A21-16", "two-sided t_(T-1) p", p_t, "7.7", -5)
sci("A21-16", "one-sided p", p_1, "3.8", -5)
chk("A21-16", "t against normal, in % (about 1%)", 100 * (p_t / p_n - 1), "1")
has("about 1%", "differ by only about 1%")
has("code comments", "# 7.6e-05, normal")
has("code comments", "# 7.7e-05, t with T - 1")
has("code comments", "# (21.1): 3.96")
se_s = s / sqrt(T)
A = d.A
anchor("A21-17", f"LM20's interval (A20-09), A Rbar +- 1.96 A s / sqrt(T): {100 * A * (Rb - 1.96 * se_s):.6f}% to "
       f"{100 * A * (Rb + 1.96 * se_s):.6f}%; daily, Rbar +- 1.96 s / sqrt(T): {100 * (Rb - 1.96 * se_s):.6f}% to "
       f"{100 * (Rb + 1.96 * se_s):.6f}%")
chk("A21-17", "LM20's interval, low (% a year)", 100 * A * (Rb - 1.96 * se_s), "7.8")
chk("A21-17", "LM20's interval, high (% a year)", 100 * A * (Rb + 1.96 * se_s), "23.0")
has("LM20's interval", "7.8% to 23.0% a year")
z_reg, se_reg = two_sample(R[~d.pre], R[d.pre])
wr = stats.ttest_ind(R[~d.pre], R[d.pre], equal_var=False)
anchor("A21-18", f"z {z_reg:.5f} (printed {z_reg:.2f}); SE {100 * se_reg:.6f}%; p normal {p2(z_reg):.5f}; SciPy "
       f"ttest_ind(equal_var=False) df {float(wr.df):.1f}, p {float(wr.pvalue):.5f}")
chk("A21-18", "regimes' statistic", z_reg, "1.08")
chk("A21-18", "its SE %", 100 * se_reg, "0.0315")
chk("A21-18", "its SE from the printed SEs", sqrt(0.0227**2 + 0.0219**2), "0.0315")
chk("A21-18", "statistic from the printed inputs", (0.0804 - 0.0464) / 0.0315, "1.08")
chk("A21-18", "p", p2(z_reg), "0.28")
chk("A21-18", "SciPy p (t reference)", float(wr.pvalue), "0.280")
has("E4", "$(0.0804-0.0464)/0.0315=1.08$")
has("E4", "$\\sqrt{0.0227^2+0.0219^2}=0.0315%$")
assert reg["from"][2] > stats.norm.isf(0.005) and stats.norm.isf(0.025) < reg["before"][2] < stats.norm.isf(0.005)
has("E4", "One period passes 1% and the other 5%")
grid = np.linspace(-5, 5, 2001)
gap = float(np.abs(stats.t.pdf(grid, T - 1) - stats.norm.pdf(grid)).max())
t975 = float(stats.t.isf(0.025, T - 1))
anchor("A21-59", f"t_(T-1) 97.5% point {t975:.5f} against {C975:.5f}; largest density gap on [-5, 5] {gap:.2e}")
chk("A21-59", "t_5848 97.5% point", t975, "1.9604")
chk("A21-59", "normal 97.5% point", C975, "1.9600")
sci("A21-59", "density gap", gap, "2.3", -5)
t60 = [mm / (ss / sqrt(n)) for mm, ss, n in ((0.0625, 1.2085, T), (0.0464, 1.2572, i_pre), (0.0804, 1.1519, T - i_pre))]
anchor("A21-60", "from the four-decimal means and s_u: " + "; ".join(
    f"{lab} {v:.4f}" for lab, v in zip(("all", "before", "from"), t60)))
for v, sh in zip(t60, ("3.955", "2.047", "3.675")):
    chk("A21-60", "X1 note, t-stat from the printed inputs", v, sh)
has("X1 note", "give 3.955, 2.047 and 3.675")
# X1 (reviews/vol4_cross.md): LM19 owns TR23's autocorrelations; (19.5) on log returns, full-sample mean, divisor T
rlog = np.log1p(R)
rlc = rlog - rlog.mean()
rho1_log = float((rlc[1:] * rlc[:-1]).sum() / (rlc * rlc).sum())
print(f"LM19's rho_1 of TR23's log returns: {rho1_log:.6f}")
chk("new", "LM19's lag-1 autocorrelation of log returns", rho1_log, "0.0393")
has("LM19's lag-1 autocorrelation", "TR23's log returns have a lag-1 autocorrelation of 0.0393 ([[LM19]])")
# KC section 3
chk("A21-39", "KC 3 t-stat", 0.04 / (1 / sqrt(900)), "1.20")
chk("A21-39", "KC 3 days", Fraction(2 * 100, 4) ** 2, "2,500")
chk("A21-39", "KC 3 sqrt(T)", Fraction(2 * 100, 4), "50")
chk("new", "KC 3: 2,500 days in years at A, about ten", 2500 / A, "10", in_md=False)
has("KC 3", "2,500 days, about ten years")
anchor("A21-39", f"t {0.04 / (1 / sqrt(900)):.4f}; T for t = 2: {(2 * 1 / 0.04) ** 2:.0f}")

# ---------------------------------------------------------------- power (X3, E5, KC 4)
sr_d = Rb / s
sr_a = sr_d * sqrt(A)
anchor("A21-19", f"SR per day {sr_d:.6f}; annual {sr_a:.5f} (printed {sr_a:.2f}); SR_annual * sqrt(years) "
       f"{sr_a * sqrt(d.years):.6f} = Rbar / s * sqrt(T) {sr_d * sqrt(T):.6f}")
chk("A21-19", "SR annual", sr_a, "0.81")
chk("A21-19", "SR annual, four decimals", sr_a, "0.8115")
chk("A21-19", "SR from the printed inputs", sqrt(246.12) * 0.0625 / 1.2084, "0.81")
chk("A21-19", "identity", sr_a * sqrt(d.years), "3.956")
chk("A21-19", "identity from the printed inputs", 0.8115 * sqrt(23.7645), "3.956")
has("E5", "$0.8115\\times\\sqrt{23.7645}=3.956$")
has("E5", "$\\sqrt{246.12}\\times0.0625%/1.2084%=0.81$")
anchor("A21-20", f"c {C975:.6f}; Phi^-1(0.8) {C80:.6f}; years for 80% power: " +
       ", ".join(f"SR {v:g}: {years80(v):.3f}" for v in (0.25, 0.5, 1.0)) +
       f", TR23's {sr_a:.6f}: {years80(sr_a):.3f}; power at those years (both tails): " +
       ", ".join(f"{power(v, years80(v)):.4f}" for v in (0.25, 0.5, 1.0, sr_a)))
chk("A21-20", "Phi^-1(0.975)", C975, "1.959964")
chk("A21-20", "Phi^-1(0.8)", C80, "0.841621")
chk("A21-20", "their sum", C975 + C80, "2.801585")
chk("A21-20", "their sum from the printed values", 1.959964 + 0.841621, "2.801585")
for v, sh in ((0.25, "125.6"), (0.5, "31.4"), (1.0, "7.85"), (sr_a, "11.9")):
    chk("A21-20", f"years SR {v:.4g}", years80(v), sh)
    chk("A21-20", f"years SR {v:.4g} from 2.801585", (2.801585 / v) ** 2, sh)
chk("A21-20", "years at the printed 0.8115", (2.801585 / 0.8115) ** 2, "11.9")
has("X3 note", "Power reaches 80% at 7.85, 11.9, 31.4 and 125.6 years")
anchor("A21-21", f"at {d.years:.4f} years: " + ", ".join(f"SR {v:.4g}: {power(v, d.years):.5f}"
                                                        for v in (0.25, 0.5, 1.0, sr_a)))
for v, sh in ((0.25, "0.23"), (0.5, "0.68"), (1.0, "0.998"), (sr_a, "0.977"), (sr_a, "0.98")):
    chk("A21-21", f"power over TR23's span, SR {v:.4g}", power(v, d.years), sh)
chk("A21-21", "power at the printed 0.81", power(0.81, d.years), "0.98")
has("X3 note", "it is 0.998, 0.977, 0.68 and 0.23")
anchor("A21-40", f"power at SR 0.5, 10 years {power(0.5, 10):.4f}; years for t = 3: SR 1 {(3 / 1) ** 2:.0f}, SR 0.5 "
       f"{(3 / 0.5) ** 2:.0f}")
chk("A21-40", "KC 4 power", power(0.5, 10), "0.35")
chk("A21-40", "KC 4 power with 1.96", power(0.5, 10, 1.96), "0.35")
chk("A21-40", "KC 4 years at SR 1", Fraction(3) ** 2, "9")
chk("A21-40", "KC 4 years at SR 0.5", Fraction(6) ** 2, "36")

# ---------------------------------------------------------------- tests of frequencies (E1, E2, E6, E7, X4)
th = up_x / T
z_up = (th - 0.5) / sqrt(0.25 / T)
p_up = float(stats.binom.sf(up_x - 1, T, 0.5))
anchor("A21-22", f"theta_hat {th:.6f}; z {z_up:.5f}; exact Pr(X >= {up_x}) {p_up:.4e}; "
       f"normal Pr(Z >= z) {float(stats.norm.sf(z_up)):.4e}")
chk("A21-22", "theta hat", Fraction(up_x, T), "0.548")
chk("A21-22", "z", z_up, "7.3")
sci("A21-22", "exact binomial p", p_up, "1.2", -13)
has("code comments", "# 1.2e-13, up days")
prev_dn, now_dn = [x < 0 for x in RF[:-1]], [x < 0 for x in RF[1:]]
n11 = sum(a and b for a, b in zip(prev_dn, now_dn))
n12 = sum(a and not b for a, b in zip(prev_dn, now_dn))
n21 = sum((not a) and b for a, b in zip(prev_dn, now_dn))
n22 = sum((not a) and (not b) for a, b in zip(prev_dn, now_dn))
npair = n11 + n12 + n21 + n22
assert npair == T - 1 and n11 == int(((R[:-1] < -EPS) & (R[1:] < -EPS)).sum())
tab = np.array([[n11, n12], [n21, n22]], dtype=float)
ex = tab.sum(1)[:, None] * tab.sum(0)[None, :] / npair
chi = float(((tab - ex) ** 2 / ex).sum())
rho = (n11 * n22 - n12 * n21) / sqrt((n11 + n12) * (n21 + n22) * (n11 + n21) * (n12 + n22))
c_y = stats.chi2_contingency(tab, correction=True)
c_n = stats.chi2_contingency(tab, correction=False)
assert abs(float(c_n.statistic) - chi) < 1e-9 and abs(npair * rho**2 - chi) < 1e-9
anchor("A21-23", f"counts dd {n11}, du {n12}, ud {n21}, uu {n22}; expected {ex[0, 0]:.4f}, {ex[0, 1]:.4f}, "
       f"{ex[1, 0]:.4f}, {ex[1, 1]:.4f}; chi2 {chi:.5f} (= n rho^2), p {float(stats.chi2.sf(chi, 1)):.5f}; rho "
       f"{rho:.6f}; z = sqrt(n) rho {sqrt(npair) * rho:.5f}; Yates (SciPy default) {float(c_y.statistic):.5f}, "
       f"p {float(c_y.pvalue):.5f}")
chk("A21-23", "down after down", n11, "1,226")
rows_, cols_ = (n11 + n12, n21 + n22), (n11 + n21, n12 + n22)
for v, sh in ((rows_[0], "2,643"), (rows_[1], "3,205"), (cols_[0], "2,644"), (cols_[1], "3,204")):
    chk("A21-23", "margin", v, sh)
for (i, j), sh in zip(((0, 0), (0, 1), (1, 0), (1, 1)), ("1,194.95", "1,448.05", "1,449.05", "1,755.95")):
    chk("A21-23", f"expected {i + 1}{j + 1}", Fraction(rows_[i] * cols_[j], npair), sh)
chk("A21-23", "expected dd as LM13 printed it", Fraction(rows_[0] * cols_[0], npair), "1,195.0")
dev = Fraction(n11 * n22 - n12 * n21, npair)
assert all(abs(Fraction(int(tab[i, j])) - Fraction(rows_[i] * cols_[j], npair)) == dev for i in (0, 1) for j in (0, 1))
chk("new", "observed minus expected, D / n (E6)", dev, "31.05")
chk("new", "LM13's gap in days", dev, "31")
for v, sh in ((chi, "2.69"), (float(stats.chi2.sf(chi, 1)), "0.10"), (rho, "0.0214"), (rho, "0.02143"),
              (float(c_y.statistic), "2.60"), (float(c_y.pvalue), "0.107"), (5848 * 0.02143**2, "2.69")):
    chk("A21-23", "sign table", v, sh)
has("E6", "$5,848\\times0.02143^2$")
chk("A21-23", "code: chi2 tail of the printed 2.69", float(stats.chi2.sf(2.69, 1)), "0.10")
has("code comments", "# 0.10, signs, (21.5)")
has("X4 row 1", "| Down after down | 5,848 pairs | 1,226 | 1,194.95 | $\\chi^2=2.69$ | 0.10 |")
f_dd, f_d = Fraction(n11, n11 + n12), Fraction(n11 + n21, npair)
rho15 = (f_dd - f_d) / (1 - f_d)
anchor("A21-24", f"LM15's rho_1 = (Pr(down given down) - Pr(down)) / (1 - Pr(down)): unrounded {float(rho15):.6f}; "
       f"from printed 0.4639, 0.4521: {(0.4639 - 0.4521) / (1 - 0.4521):.6f} (printed 0.0215 and 0.0214, lm15.md:100)")
chk("A21-24", "LM15's rho_1 unrounded, as E6's 0.0214", rho15, "0.0214")
fl_prev = [x <= Fraction(-3, 100) for x in RF[:-1]]
fl_now = [x <= Fraction(-3, 100) for x in RF[1:]]
f1, f2 = sum(fl_prev), sum(fl_now)
f12 = sum(a and b for a, b in zip(fl_prev, fl_now))
assert f12 == int(((R[:-1] <= -0.03 + EPS) & (R[1:] <= -0.03 + EPS)).sum())
p_ff = float(stats.binom.sf(f12 - 1, f1, f2 / npair))
anchor("A21-25", f"falls on day t-1 {f1}, on day t {f2}, both {f12}; expected {f1 * f2 / npair:.5f}; exact "
       f"Pr(X >= {f12}) for Bin({f1}, {f2}/{npair}) {p_ff:.4e}; Poisson({f1 * f2 / npair:.4f}) "
       f"{float(stats.poisson.sf(f12 - 1, f1 * f2 / npair)):.4e}")
assert f1 == f2 == 108
chk("A21-25", "falls", f1, "108")
chk("A21-25", "falls after falls", f12, "13")
chk("A21-25", "expected", Fraction(f1 * f2, npair), "2.0")
sci("A21-25", "exact binomial p", p_ff, "1.2", -7)
has("E7", "$\\theta_0=108/5,848$")
has("X4 row 2", "| Fall of 3% or more after one | 108 days | 13 | 2.0 | exact binomial | $1.2\\times10^{-7}$ |")
# LM16's printed U28 counts (A21-61 recounts them below)
z16 = (177 - 48.68) / 6.94
anchor("A21-26", f"printed 177, 48.68, 6.94 (lm16.md:382, 384): z {z16:.4f}; the SD that makes z = 3: "
       f"{(177 - 48.68) / 3:.3f} = {(177 - 48.68) / 3 / 6.94:.3f} x 6.94")
chk("A21-26", "z from LM16's printed counts", z16, "18.5")
chk("A21-26", "SD for z = 3", (177 - 48.68) / 3, "42.8")
chk("A21-26", "its ratio to 6.94", (177 - 48.68) / 3 / 6.94, "6.2")
has("LM16", "$z=(177-48.68)/6.94=18.5$")
anchor("A21-27", "printed 43.8 expected and 291 U28 days beyond the chi2_5 99% quantile 15.09 (lm16.md:398-400)")
has("LM16's S5", "43.8 rejections expected, 291 found")
has("LM16's crash correlation", "0.788 against the model's 0.860")
chi95 = float(stats.chi2.isf(0.05, 1))
anchor("A21-41", f"chi2_1 5% point {chi95:.5f} = 1.959964^2; abs(rho) > {sqrt(chi95 / 10000):.6f}")
chk("A21-41", "chi2_1 5% point", chi95, "3.84")
chk("A21-41", "abs(rho)", sqrt(chi95 / 10000), "0.0196")
# E1 (and Problem 6)
pge8 = Fraction(sum(comb(12, j) for j in range(8, 13)), 4096)
pge9 = Fraction(sum(comb(12, j) for j in range(9, 13)), 4096)
pge10 = Fraction(sum(comb(12, j) for j in range(10, 13)), 4096)
th1 = Fraction(55, 100)
pow55 = sum(comb(12, j) * th1**j * (1 - th1) ** (12 - j) for j in range(10, 13))
anchor("A21-46", f"Pr(X >= 8) {pge8} = {float(pge8):.5f}; Pr(X >= 9) {pge9} = {float(pge9):.5f}; Pr(X >= 10) "
       f"{pge10} = {float(pge10):.5f}; power at 0.55 {float(pow55):.5f}; type II {1 - float(pow55):.5f}")
assert pge8 == Fraction(794, 4096) and pge10 == Fraction(79, 4096) and pge9 > Fraction(1, 20) >= pge10
for v, sh in ((pge8, "0.194"), (pge9, "0.073"), (pge10, "0.0193"), (pow55, "0.042"), (1 - pow55, "0.958"),
              (100 * pow55, "4")):
    chk("A21-46", "E1", v, sh)
has("E1", "$\\Pr(X\\ge8)=794/4,096=0.194$")
has("E1", "$\\Pr(X\\ge10)=79/4,096=0.0193$")
has("LM13's posterior", "posterior of 13.5%")
has("power 4%", "power 4%")
# KC section 2
z_kc = (0.60 - 0.5) / sqrt(0.25 / 100)
anchor("A21-38", f"z {z_kc:.4f}; p two-sided {p2(z_kc):.5f}")
chk("A21-38", "KC 2 z", z_kc, "2.00")
chk("A21-38", "KC 2 p", p2(z_kc), "0.0455")
assert 0.01 < p2(z_kc) <= 0.05

# ---------------------------------------------------------------- the calendar family (X5, E8)
fam = calendar(d)
M = len(fam)
pv = [f[4] for f in fam]
fam_sc = []
for name, sel in ([(MO_NAMES[k - 1], d.mo == k) for k in range(1, 13)] + [(WD_NAMES[k], d.wd == k) for k in range(5)]):
    fam_sc.append(float(stats.ttest_ind(R[sel], R[~sel], equal_var=False).pvalue))
anchor("A21-28", "; ".join(f"{f[0]} {f[1]} {f[2]:.4f}% z {f[3]:.4f} p {f[4]:.5f} (SciPy t {sc:.5f})"
                           for f, sc in zip(fam, fam_sc)))
X5 = ("-0.32", "1.33", "-1.04", "0.59", "0.51", "-0.15", "1.00", "-0.50", "-1.13", "-1.10", "-0.34", "1.53",
      "-1.05", "-0.10", "2.36", "-0.63", "-0.42")
cal = json.loads((CHARTS / "lm21-calendar.json").read_text(encoding="utf-8"))
assert cal["categories"] == MO_NAMES + WD_NAMES[:5], cal["categories"]
for f, sh, v in zip(fam, X5, cal["series"][0]["values"]):
    chk("A21-28", f"X5 {f[0]} (chart file)", f[3], sh, in_md=False)
    assert abs(v - f[3]) < 5e-7, (f[0], v, f[3])
chk("A21-28", "Wednesday p", fam[14][4], "0.018")
chk("A21-28", "December p (X6's point label)", fam[11][4], "0.127", in_md=False)
n_sig = sum(1 for p in pv if p <= 0.05)
fwer17 = 1 - Fraction(19, 20) ** M
c_bonf = float(stats.norm.isf(0.025 / M))
anchor("A21-29", f"m = {M}; unadjusted p <= 0.05: {n_sig}; expected false rejections {M * 0.05:.2f}; FWER if "
       f"independent {1 - 0.95**M:.5f}; Bonferroni level {0.05 / M:.7f}, abs(z) >= {c_bonf:.5f}")
for v, sh in ((M, "17"), (Fraction(M, 20), "0.85"), (fwer17, "0.58"), (fwer17, "0.582"),
              (Fraction(1, 20 * M), "0.00294"), (c_bonf, "2.97"), (c_bonf, "2.974")):
    chk("A21-29", "family", v, sh)
assert n_sig == 1 and fam[14][0] == "Wed" and pv[14] == min(pv)
has("one rejection", "One test rejects: Wednesday's, at 2.36")
has("X5 lines", "±1.96, the 5% level of one test, and ±2.97, Bonferroni's level for 17 tests")
pmin = min(pv)
anchor("A21-30", f"smallest p {pmin:.6f}; Bonferroni-adjusted {M * pmin:.5f}; Sidak 1 - (1 - p)^17 "
       f"{1 - (1 - pmin) ** M:.5f}")
chk("A21-30", "Bonferroni-adjusted", M * pmin, "0.31")
chk("A21-30", "Sidak", 1 - (1 - pmin) ** M, "0.267")
assert abs(float(multipletests(pv, method="sidak")[1].min()) - (1 - (1 - pmin) ** M)) < 1e-12
has("E8", "$17p_{(1)}=0.31$")
zmax = experiment8(d)
B8 = len(zmax)
n8a = int((zmax >= C975 - EPS).sum())
n8b = int((zmax >= abs(fam[14][3]) - EPS).sum())
fw8, pw8 = n8a / B8, n8b / B8
anchor("A21-31", f"B {B8}: share with a test at abs(z) >= 1.959964: {fw8:.4f} (SE {sqrt(fw8 * (1 - fw8) / B8):.4f}); "
       f"share with max abs(z) >= {abs(fam[14][3]):.4f}: {pw8:.4f} (SE {sqrt(pw8 * (1 - pw8) / B8):.4f})")
chk("A21-31", "shuffles with a rejection", Fraction(n8a, B8), "0.580")
chk("A21-31", "its SE", sqrt(fw8 * (1 - fw8) / B8), "0.005")
chk("A21-31", "shuffles at least as extreme as Wednesday", Fraction(n8b, B8), "0.266")
chk("A21-31", "its SE", sqrt(pw8 * (1 - pw8) / B8), "0.004")
has("E8", "$0.580\\pm0.005$")
has("E8", "$0.266\\pm0.004$")
has("E8 seed", "`rng = default_rng([8, 20261011])`")
has("E8 shuffles (U2)", "Each shuffle is `R[perm]`, with `perm = rng.permutation(T)` drawn 10,000 times from one")
has("E8 shares", "Across the shuffles, $0.580\\pm0.005$ of the families")
assert B8 == 10_000 and "x = R[g8.permutation(T)]" in inspect.getsource(experiment8), "E8's printed call"
has("pitfall 7", "(0.580 against 0.582)")
stab = []
for lab, sel, shown in (("before", d.pre, ("2.06", "0.040")), ("from", ~d.pre, ("1.25", "0.21"))):
    x, w = R[sel], d.wd[sel]
    z, _ = two_sample(x[w == 2], x[w != 2])
    stab.append(f"{lab} 2015-06-01: {int((w == 2).sum())} Wednesdays, mean {100 * x[w == 2].mean():.4f}% against "
                f"{100 * x[w != 2].mean():.4f}%, z {z:.4f}, p {p2(z):.4f}")
    chk("A21-33", f"Wednesday {lab} June 2015", z, shown[0])
    chk("A21-33", "its p", p2(z), shown[1])
anchor("A21-33", "; ".join(stab))
has("E8 stability", "2.06 before June 2015 (p-value 0.040) and 1.25 after (0.21)")
anchor("A21-42", f"expected {100 * 0.05:.0f}; Pr(at least one) {1 - 0.95**100:.5f}")
chk("A21-42", "KC 6 expected", Fraction(100, 20), "5")
chk("A21-42", "KC 6 Pr", 1 - Fraction(19, 20) ** 100, "0.994")

# ---------------------------------------------------------------- Holm, Benjamini-Hochberg (E9, X6, KC 7)
ps_sorted = sorted(pv)
rej = {meth: int(multipletests(pv, alpha=0.05, method=meth)[0].sum()) for meth in ("bonferroni", "holm", "fdr_bh", "hs")}
rej_bh10 = int(multipletests(pv, alpha=0.10, method="fdr_bh")[0].sum())
assert rej["bonferroni"] == bonf_count(pv, 0.05) and rej["holm"] == holm_count(pv, 0.05)
assert rej["fdr_bh"] == bh_count(pv, 0.05) and rej_bh10 == bh_count(pv, 0.10)
anchor("A21-32", f"p_(1) {ps_sorted[0]:.5f} against Holm/Bonferroni/BH(0.05) {0.05 / M:.6f} and BH(0.10) "
       f"{0.10 / M:.6f}; p_(2) {ps_sorted[1]:.5f} against Holm {0.05 / (M - 1):.6f}, BH(0.05) {2 * 0.05 / M:.6f}, "
       f"BH(0.10) {2 * 0.10 / M:.6f}; rejections: Bonferroni {rej['bonferroni']}, Holm {rej['holm']}, BH q=0.05 "
       f"{rej['fdr_bh']}, BH q=0.10 {rej_bh10}, multipletests default (Holm-Sidak) {rej['hs']}")
chk("A21-32", "BH(0.10) first level (no longer printed, C1)", Fraction(1, 10 * M), "0.00588", in_md=False)
# C1: each p_(i) exceeds its BH level i q / m at least threefold even at q = 10% (so also at 5%)
bh_ratio = {q_: min(p_ / ((i + 1) * q_ / M) for i, p_ in enumerate(ps_sorted)) for q_ in (0.05, 0.10)}
print(f"C1: smallest p_(i) / (i q / m): q = 5% {bh_ratio[0.05]:.4f}, q = 10% {bh_ratio[0.10]:.4f}")
assert 3 <= bh_ratio[0.10] < bh_ratio[0.05], bh_ratio
has("E9 calendar (C1)", "the first level of Bonferroni and Holm at 5%, so neither rejects anything")
has("E9 calendar (C1)", "each $p_{(i)}$ exceeds its level $iq/m$, at least threefold even at $q=10\\%$")
has("E9 calendar (C1)", "Its adjusted p-values, $\\min_{j\\ge i}mp_{(j)}/j$ (at most 1), start at 0.308")
# the printed definition of BH's adjusted p-values reproduces SciPy's and statsmodels'
bh_adj = [min(1.0, min(M * ps_sorted[j] / (j + 1) for j in range(i, M))) for i in range(M)]
assert np.allclose(bh_adj, np.sort(stats.false_discovery_control(pv, method="bh")), rtol=0, atol=1e-15)
assert np.allclose(bh_adj, np.sort(multipletests(pv, method="fdr_bh")[1]), rtol=0, atol=1e-15)
# Solution 10: Holm-Sidak's first level 1 - (1 - alpha)^(1/m)
hs1 = 1 - 0.95 ** (1 / M)
chk("new", "Holm-Sidak first level (Solution 10)", hs1, "0.00301")
assert ps_sorted[0] > hs1 and abs(float(multipletests(pv, method="hs")[1].min()) - (1 - (1 - ps_sorted[0]) ** M)) < 1e-12
has("S10", "$p_{(1)}=0.018$ exceeds their first levels, 0.00294 and 0.00301")
has("S10", "rejects nothing either, because every $p_{(i)}$ exceeds $iq/m$")
has("P10 stem", "Give the rejections at 5% and Benjamini–Hochberg's two smallest adjusted p-values")
chk("A21-32", "Holm's second level (exact: printed in full)", Fraction(1, 20 * (M - 1)), "0.003125")
assert Fraction(1, 20 * (M - 1)) == Fraction(3125, 10**6)
assert all(v == 0 for v in (rej["bonferroni"], rej["holm"], rej["fdr_bh"], rej_bh10, rej["hs"]))
has("E9 calendar", "$p_{(1)}=0.018$ exceeds 0.00294")
c17 = sum(Fraction(1, i) for i in range(1, M + 1))
chk("new", "BY's divisor, sum of 1/i for m = 17", c17, "3.44")
has("BY", "(3.44 for $m=17$)")
a5 = Fraction(5, 100)
e9 = [Fraction(x) for x in ("0.002", "0.0054", "0.0061", "0.011", "0.024", "0.031", "0.09", "0.22", "0.47", "0.86")]
m9 = len(e9)
anchor("A21-47", f"Bonferroni {bonf_count(e9, a5)} (level {float(a5 / m9):.4f}); Holm {holm_count(e9, a5)} (levels " +
       ", ".join(f"{float(a5 / (m9 - i)):.5f}" for i in range(4)) + f"); BH {bh_count(e9, a5)} (levels " +
       ", ".join(f"{float((i + 1) * a5 / m9):.3f}" for i in range(7)) + ")")
for v, sh in ((bonf_count(e9, a5), "1"), (holm_count(e9, a5), "3"), (bh_count(e9, a5), "5")):
    chk("A21-47", "E9 rejections", v, sh)
chk("A21-47", "Bonferroni's level", a5 / m9, "0.005")
for i, sh in enumerate(("0.005", "0.00556", "0.00625", "0.00714")):
    chk("A21-47", f"Holm level {i + 1}", a5 / (m9 - i), sh)
for i, sh in ((0, "0.005"), (1, "0.010"), (4, "0.025"), (5, "0.030"), (6, "0.035"), (9, "0.050")):
    chk("A21-47", f"BH level {i + 1}", (i + 1) * a5 / m9, sh)
assert e9[2] <= a5 / 8 and e9[3] > a5 / 7 and e9[4] <= 5 * a5 / m9
assert all(e9[i] > (i + 1) * a5 / m9 for i in range(5, m9))
has("E9", "The p-values 0.002, 0.0054 and 0.0061 pass, and 0.011 misses: 3 rejections")
has("E9", "$0.024\\le0.025$")
has("E9", "$0.031>0.030$ and $0.09>0.035$")
has("E9 stem", "0.002, 0.0054, 0.0061, 0.011, 0.024, 0.031, 0.09, 0.22, 0.47 and 0.86")
e9f = np.array([float(x) for x in e9])
assert [int(multipletests(e9f, alpha=0.05, method=meth)[0].sum()) for meth in ("bonferroni", "holm", "fdr_bh")] == [1, 3, 5]
chk("A21-47", "code: BH-adjusted p-values at or below 0.05", int((stats.false_discovery_control(e9f) <= 0.05).sum()), "5")
has("code comments", "# 1, 3, 5")
has("code comments", "# 5, BH")
kc6 = [Fraction(4, 1000), Fraction(12, 1000), Fraction(30, 1000)]
anchor("A21-43", f"Bonferroni {bonf_count(kc6, a5)}, Holm {holm_count(kc6, a5)}, BH {bh_count(kc6, a5)}")
for v, sh in ((bonf_count(kc6, a5), "2"), (holm_count(kc6, a5), "3"), (bh_count(kc6, a5), "3")):
    chk("A21-43", "KC 7 rejections", v, sh)
for v, sh in ((a5 / 3, "0.0167"), (a5 / 2, "0.025"), (a5, "0.05"), (2 * a5 / 3, "0.0333")):
    chk("A21-43", "KC 7 levels", v, sh)
has("KC 7", "with 0.0167, 0.025 and 0.05: all pass, 3 rejections")
has("KC 7", "levels are 0.0167, 0.0333 and 0.05")
adj = sorted(float(v) for v in stats.false_discovery_control(pv, method="bh"))
anchor("A21-56", f"multipletests rejections: default 'hs' {rej['hs']}, 'holm' {rej['holm']}, 'fdr_bh' "
       f"{rej['fdr_bh']}, 'bonferroni' {rej['bonferroni']}; BH-adjusted p (false_discovery_control), two smallest: " +
       ", ".join(f"{v:.5f}" for v in adj[:2]))
chk("A21-56", "BH adjusted, smallest", adj[0], "0.308")
chk("A21-56", "BH adjusted, second", adj[1], "0.669")
assert abs(adj[0] - float(multipletests(pv, method="fdr_bh")[1].min())) < 1e-12

# ---------------------------------------------------------------- the largest of m (X7, E10, KC 8) and t = 3
p3 = p2(3.0)
anchor("A21-34", f"two-sided p at abs(t) = 3: {p3:.7f}; 0.05 / p = {0.05 / p3:.3f} tests; one-sided "
       f"{float(stats.norm.sf(3)):.7f}")
chk("A21-34", "p at 3", p3, "0.0027")
chk("A21-34", "tests", 0.05 / p3, "18.5")
has("t = 3", "a search of about 18.5 tests")
anchor("A21-35", "; ".join(f"m={m}: median {maxq(0.5, m):.4f}, 5% {maxq(0.05, m):.4f}, 95% {maxq(0.95, m):.4f}, "
                           f"Pr(max > 3) {1 - float(stats.norm.cdf(3)) ** m:.4f}" for m in (17, 100, 1000, 10000)))
for m, sh in ((17, "1.75"), (100, "2.46"), (1000, "3.20"), (10000, "3.81")):
    chk("A21-35", f"median of the best of {m}", maxq(0.5, m), sh)
chk("A21-35", "5% at m = 1,000", maxq(0.05, 1000), "2.75")
chk("A21-35", "95% at m = 1,000", maxq(0.95, 1000), "3.88")
chk("A21-35", "Pr(max > 3) at m = 1,000", 1 - float(stats.norm.cdf(3)) ** 1000, "0.74")
has("medians", "1.75 at $m=17$, 2.46 at 100, 3.20 at 1,000 and 3.81 at 10,000")
has("range", "from 2.75 to 3.88")
tt = experiment10(d)
run = np.maximum.accumulate(tt)
records = [(i + 1, float(tt[i])) for i in range(len(tt)) if i == 0 or tt[i] > run[i - 1]]
anchor("A21-36", "; ".join(f"m={m}: {run[m - 1]:.4f}" for m in (1, 10, 17, 100, 1000, 10000)) + "; records (m, t): " +
       ", ".join(f"({i}, {v:.4f})" for i, v in records))
for v, sh in ((run[99], "2.95"), (run[999], "2.95"), (tt[1021], "3.28"), (run[-1], "3.97")):
    chk("A21-36", "search", float(v), sh)
for v, sh in ((int(np.argmax(tt[:100])) + 1, "90"), (int(np.argmax(tt[:1100])) + 1, "1,022"),
              (int(np.argmax(tt)) + 1, "7,840"), (len(records), "11")):
    chk("A21-36", "record rule", v, sh)
has("E10", "The best after 100 rules is 2.95 (rule 90), and it is still 2.95 after 1,000")
has("E10", "Rule 1,022 reaches 3.28, and the best of all 10,000 is 3.97 (rule 7,840)")
has("E10 seed", "`default_rng([10, 20261011])`")
has("E10 call (U1)", "`integers(0, 2, size=(10000, T), dtype=np.int8)`, with 1 for long and 0 for short")
assert len(tt) == 10_000 and "integers(0, 2, size=(M, d.T), dtype=np.int8)" in inspect.getsource(experiment10)
assert "2.0 * pos[c:c + 500].astype(np.float64) - 1.0" in inspect.getsource(experiment10), "1 long, 0 short"
mx = json.loads((CHARTS / "lm21-maxt.json").read_text(encoding="utf-8"))
step = next(sr for sr in mx["series"] if sr.get("step"))
assert step["x"][:-1] == [i for i, _ in records] and step["x"][-1] == 10000
assert all(abs(a - b) < 5e-5 for a, (_, b) in zip(step["y"], records)), "X7's record points"
n3 = int((tt >= 3 - EPS).sum())
n196 = int((np.abs(tt) >= 1.96 - EPS).sum())
sd_t = float(tt.std(ddof=0))
sd_batches = np.array([tt[c:c + 500].std(ddof=0) for c in range(0, len(tt), 500)])
se_sd = float(sd_batches.std(ddof=0)) / sqrt(20)
anchor("A21-37", f"t >= 3: {n3} (expected {len(tt) * float(stats.norm.sf(3)):.2f}); abs(t) >= 1.96: {n196} (expected "
       f"{len(tt) * p2(1.96):.1f}); mean {tt.mean():.4f} (SE s/sqrt(B) {sd_t / sqrt(len(tt)):.4f}); s (divisor "
       f"10,000) {sd_t:.4f} (batch SE {se_sd:.4f}, 20 batches of 500)")
for v, sh in ((n3, "13"), (len(tt) * float(stats.norm.sf(3)), "13.5"), (float(tt.mean()), "-0.01"),
              (sd_t / sqrt(len(tt)), "0.01"), (sd_t, "0.995"), (se_sd, "0.007")):
    chk("A21-37", "search counts and moments", v, sh)
has("E10", "average −0.01 (standard error 0.01), with a standard deviation of 0.995 (batch standard error 0.007")
has("E10", "$10,000\\Phi(-3)=13.5$")
m50 = log(0.5) / log(float(stats.norm.cdf(3)))
m_up = int(np.ceil(m50))
anchor("A21-44", f"m = ln 0.5 / ln Phi(3) = {m50:.2f}; at m = {m_up}: {1 - float(stats.norm.cdf(3)) ** m_up:.5f}; "
       f"at m = {m_up - 1}: {1 - float(stats.norm.cdf(3)) ** (m_up - 1):.5f}")
chk("A21-44", "KC 8 m", m50, "513.1")
chk("A21-44", "KC 8 m rounded up", m_up, "514")
p29 = 2 * float(stats.t.sf(2, 29))
anchor("A21-45", f"t_29 {p29:.5f}; normal {p2(2.0):.5f}")
chk("A21-45", "KC 9 t_29", p29, "0.055")
chk("A21-45", "KC 9 normal", p2(2.0), "0.0455")
has("widget initial state", "It starts with 100 tests at the 5% level, 10% of them with a mean t-stat of 3")

# ---------------------------------------------------------------- problems
anchor("A21-48", f"{1 - 0.95**20:.5f}; 20 x 0.05 = {20 * 0.05:.2f}; one test {0.05:.2f}")
chk("A21-48", "P2 C", 1 - Fraction(19, 20) ** 20, "0.64")
chk("A21-48", "P2 B", Fraction(20, 20), "1.00")
chk("A21-48", "P2 A", Fraction(1, 20), "0.05")
anchor("A21-49", f"{years80(0.5):.3f}; (1.959964/0.5)^2 {(C975 / 0.5) ** 2:.3f}; (1.959964 + 0.841621)/0.5 "
       f"{(C975 + C80) / 0.5:.3f}")
chk("A21-49", "P3 A", years80(0.5), "31.4")
chk("A21-49", "P3 B", (1.959964 / 0.5) ** 2, "15.4")
chk("A21-49", "P3 C", 2.801585 / 0.5, "5.60")
chk("new", "P3 B's power, in %", 100 * power(0.5, (C975 / 0.5) ** 2), "50")
has("P3", "which gives power of about 50%")
chi_p4 = 4000 * 0.03**2
anchor("A21-50", f"chi2 {chi_p4:.3f}, p {float(stats.chi2.sf(chi_p4, 1)):.5f}; 4000 x 0.03 = {4000 * 0.03:.0f}; "
       f"sqrt(4000) x 0.03 = {sqrt(4000) * 0.03:.4f}")
chk("A21-50", "P4 B", Fraction(4000 * 9, 10000), "3.60")
chk("A21-50", "P4 p", float(stats.chi2.sf(3.6, 1)), "0.058")
chk("A21-50", "P4 A", Fraction(4000 * 3, 100), "120")
chk("A21-50", "P4 C", sqrt(4000) * 0.03, "1.90")
p5 = [Fraction(x) for x in ("0.003", "0.012", "0.020", "0.030", "0.40")]
anchor("A21-51", f"Bonferroni {bonf_count(p5, a5)}, Holm {holm_count(p5, a5)}, BH {bh_count(p5, a5)}")
for v, sh in ((bonf_count(p5, a5), "1"), (holm_count(p5, a5), "2"), (bh_count(p5, a5), "4")):
    chk("A21-51", "P5", v, sh)
for v, sh in ((a5 / 5, "0.01"), (a5 / 4, "0.0125"), (a5 / 3, "0.0167"), (4 * a5 / 5, "0.04")):
    chk("A21-51", "P5 levels", v, sh)
has("S5", "0.003 and 0.012 pass 0.01 and 0.0125, and 0.020 misses 0.0167")
has("S5", "0.01, 0.02, 0.03, 0.04 and 0.05")
n_months = ((C95 * 0.5 + C80 * sqrt(0.55 * 0.45)) / 0.05) ** 2
n_up = int(np.ceil(n_months))
cmin = int(stats.binom.isf(0.05, n_up, 0.5)) + 1
while float(stats.binom.sf(cmin - 1, n_up, 0.5)) > 0.05:
    cmin += 1
half, th55 = Fraction(1, 2), Fraction(11, 20)
size_x = sum(comb(n_up, j) for j in range(cmin, n_up + 1)) * half**n_up
pow_x = sum(comb(n_up, j) * th55**j * (1 - th55) ** (n_up - j) for j in range(cmin, n_up + 1))
size_prev = sum(comb(n_up, j) for j in range(cmin - 1, n_up + 1)) * half**n_up
assert size_x <= Fraction(1, 20) < size_prev
anchor("A21-52", f"one-sided p {float(pge8):.4f}; Phi^-1(0.95) {C95:.6f}; months for 80% power at 0.55 (normal) "
       f"{n_months:.2f} -> {n_up} = {n_up / 12:.2f} years; exact at n = {n_up}: reject X >= {cmin}, size "
       f"{float(size_x):.5f}, power {float(pow_x):.5f}")
chk("new", "P6 sqrt(n) x 0.05 from the printed constants", 1.644854 * 0.5 + 0.841621 * sqrt(0.55 * 0.45), "1.241128")
chk("new", "P6 n from the printed 1.241128", (1.241128 / 0.05) ** 2, "616.16")
for v, sh in ((C95, "1.644854"), (n_months, "616.16"),
              (((1.644854 * 0.5 + 0.841621 * sqrt(0.55 * 0.45)) / 0.05) ** 2, "616.16"), (n_up, "617"),
              (Fraction(n_up, 12), "51.4"), (cmin, "330"), (size_x, "0.0454"), (pow_x, "0.7874")):
    chk("A21-52", "P6", v, sh)
# m8: Problem 6 (a)-(c) on 9 of 12 months at 10%, so that they no longer repeat E1
pow55_9 = sum(comb(12, j) * th1**j * (1 - th1) ** (12 - j) for j in range(9, 13))
print(f"P6: Pr(X >= 9) {pge9} = {float(pge9):.6f}; Pr(X >= 8) {float(pge8):.5f}; power of X >= 9 at 0.55 "
      f"{float(pow55_9):.5f}")
assert pge9 == Fraction(299, 4096) and pge8 > Fraction(1, 10) >= pge9   # the 10% region is X >= 9
chk("new", "P6 p-value Pr(X >= 9)", pge9, "0.0730")
chk("new", "P6 power of X >= 9 at 0.55", pow55_9, "0.134")
has("P6 stem", "A hypothetical manager beat the index in 9 of 12 months. Test $\\theta=\\tfrac12$ against "
    "$\\theta>\\tfrac12$ at 10%.")
has("S6 (a)", "$\\Pr(X\\ge9)=299/4,096=0.0730$, significant at 10%")
has("S6 (b)", "$\\Pr(X\\ge8)=0.194$ exceeds 0.10, so the region is $X\\ge9$, with size 0.0730")
has("S6 (c)", "$\\Pr(X\\ge9)=0.134$")
has("P6 (d) stem (K2)", "using $\\hat\\theta$'s standard deviation under each hypothesis")


# K2: the exact one-sided 5% test of theta = 1/2 for n months; power at 0.55 is not monotone in n
def exact_test(n: int) -> tuple[int, Fraction, Fraction]:
    """(smallest c with Pr(X >= c | 1/2) <= 5%, its size, its power at 0.55), exactly."""
    tail, c = Fraction(0), n + 1
    while tail + comb(n, c - 1) * half**n <= Fraction(1, 20):
        c -= 1
        tail += comb(n, c) * half**n
    pw_ = sum((comb(n, j) * th55**j * (1 - th55) ** (n - j) for j in range(c, n + 1)), Fraction(0))
    return c, tail, pw_


pw_float = [float(stats.binom.sf(int(stats.binom.isf(0.05, n, 0.5)), n, 0.55)) for n in range(1, 700)]
n80 = next(n for n in range(1, 700) if pw_float[n - 1] >= 0.8)
c80, size80, pow80 = exact_test(n80)
assert c80 == int(stats.binom.isf(0.05, n80, 0.5)) + 1 and pow80 >= Fraction(4, 5)
assert max(pw_float[:499]) < 0.75 and all(exact_test(n)[2] < Fraction(4, 5) for n in range(500, n80))
assert exact_test(n_up)[0] == cmin and exact_test(n_up - 1)[2] > pow_x   # 616 beats 617: not monotone
print(f"P6 (d): exact power first reaches 80% at n = {n80}: reject X >= {c80}, size {float(size80):.5f}, "
      f"power {float(pow80):.5f}; at {n_up - 1}: power {float(exact_test(n_up - 1)[2]):.5f}")
for v, sh in ((n80, "620"), (c80, "331"), (size80, "0.0498"), (pow80, "0.8018")):
    chk("new", "P6 (d) exact months for 80% power", v, sh)
has("S6 (d)", "Exact power is not monotone in $n$: it first reaches 80% at 620 months (reject at $X\\ge331$, "
    "size 0.0498, power 0.8018)")
nb = T // 20
blk = (R[: nb * 20] > EPS).reshape(nb, 20).sum(axis=1)
assert list(blk) == [sum(1 for x in RF[20 * j: 20 * j + 20] if x > 0) for j in range(nb)]
bv = float(blk.var(ddof=0))
ph = float(blk.sum()) / (nb * 20)
bin_v = 20 * ph * (1 - ph)
v516 = bin_v * (1 + 2 * 19 / 20 * float(rho15))
v516_p = 20 * 0.548 * 0.452 * (1 + 2 * 19 / 20 * 0.0215)
se_b, se_b2 = bin_v * sqrt(2 / nb), v516 * sqrt(2 / nb)
n_blk = 2 * (C975 * 4.95 / (5.16 - 4.95)) ** 2
n_blk_up = int(np.ceil(n_blk))
anchor("A21-53", f"blocks {nb}: mean {float(blk.mean()):.4f}, variance (divisor {nb}) {bv:.4f}; p_hat {ph:.5f}; 20 p q "
       f"{bin_v:.4f}; LM15's 5.16 unrounded {v516:.4f}, from printed {v516_p:.4f}; SE sigma^2 sqrt(2/292): "
       f"{se_b:.4f} and {se_b2:.4f}; z {(bv - bin_v) / se_b:.4f} and {(bv - v516) / se_b2:.4f}; from printed 4.72, "
       f"4.95, 5.16: {(4.72 - 4.95) / (4.95 * sqrt(2 / 292)):.4f}, {(4.72 - 5.16) / (5.16 * sqrt(2 / 292)):.4f}; "
       f"blocks n for which a gap of 0.21 is 1.959964 SE, SE = 4.95 sqrt(2/n) (the binomial null, printed inputs): "
       f"{n_blk:.2f}, rounded up {n_blk_up} = {20 * n_blk_up} sessions = {20 * n_blk_up / A:.1f} years at A")
for v, sh in ((bv, "4.72"), (bin_v, "4.95"), (v516, "5.16"), (5.16 - 4.95, "0.21"),
              ((4.72 - 4.95) / (4.95 * sqrt(2 / 292)), "-0.56"), ((4.72 - 5.16) / (5.16 * sqrt(2 / 292)), "-1.03"),
              ((bv - bin_v) / se_b, "-0.58"), ((bv - v516) / se_b2, "-1.03"), (n_blk, "4,268.7"),
              (n_blk_up, "4,269"), (20 * n_blk_up, "85,380"), (20 * n_blk_up / A, "347")):
    chk("A21-53", "P7", v, sh)
c11, c1r, c1c, cn = 347, 859, 538, 4382
c12, c21 = c1r - c11, c1c - c11
c22 = cn - c11 - c12 - c21
rho16 = (c11 * c22 - c12 * c21) / sqrt(c1r * (cn - c1r) * c1c * (cn - c1c))
anchor("A21-54", f"from printed counts 347, 859, 538, 4,382 (lm16.md:71-74): table {c11}, {c12}, {c21}, {c22}; rho "
       f"{rho16:.5f}; chi2 {cn * rho16**2:.2f}; ratio {c11 * cn / (c1r * c1c):.4f} (printed 3.29, lm16.md:88)")
for v, sh in ((c12, "512"), (c21, "191"), (c22, "3,332"), (rho16, "0.423"), (cn * rho16**2, "784"),
              (Fraction(c11 * cn, c1r * c1c), "3.29"), (Fraction(c11 * cn, c1r * c1c), "3.2902"),
              (cn * rho16**2 / chi95, "204")):
    chk("A21-54", "P8", v, sh)
assert abs(cn * rho16**2 - float(stats.chi2_contingency(np.array([[c11, c12], [c21, c22]]), correction=False).statistic)) < 1e-6
# m13: the widening of sqrt(n) rho_hat's spread that would bring 784 down to the 5% point
print(f"P8: chi2 {cn * rho16**2:.4f}; variance factor {cn * rho16**2 / chi95:.4f}; spread factor "
      f"{sqrt(cn * rho16**2 / chi95):.4f}")
chk("new", "P8 spread factor", sqrt(cn * rho16**2 / chi95), "14.3")
has("S8 (m13)", "widen the spread of $\\sqrt n\\,\\hat\\rho$ 14.3-fold, its variance 204-fold, to bring 784 down to the 5% point 3.84")
xc = R - Rb
m2_, m3_, m4_ = float((xc**2).mean()), float((xc**3).mean()), float((xc**4).mean())
sk, ku = m3_ / m2_**1.5, m4_ / m2_**2 - 3
jb = T / 6 * (sk**2 + ku**2 / 4)
jb_p = T / 6 * (0.34**2 + 5.27**2 / 4)
assert abs(jb - float(stats.jarque_bera(R).statistic)) < 1e-6
anchor("A21-55", f"skew {sk:.5f}; excess kurtosis {ku:.5f}; JB {jb:.2f}; from printed -0.34, 5.27: {jb_p:.2f}; "
       f"log10 p = -JB / (2 ln 10): {-jb / (2 * log(10)):.1f}, from printed {-jb_p / (2 * log(10)):.1f}")
chk("A21-55", "P9 skewness (LM14's print)", sk, "-0.34", in_md=False)
chk("A21-55", "P9 excess kurtosis (LM14's print)", ku, "5.27")
for v, sh in ((jb_p, "6,881"), (jb, "6,875")):
    chk("A21-55", "P9 JB", v, sh)
for v, sh in ((-jb_p / (2 * log(10)), "-1494"), (-jb / (2 * log(10)), "-1493")):
    chk("A21-55", "P9 log10 of the p-value", v, sh, in_md=False)
    has("P9 p-value", f"10^{{{sh}}}")
has("P9 stem", "skewness −0.34 and excess kurtosis 5.27")
g11 = rng(11)
Z11 = g11.standard_normal((10_000, 17))
cb = float(stats.norm.isf(0.025 / 17))
n11u = int((np.abs(Z11) >= C975 - EPS).any(axis=1).sum())
n11b = int((np.abs(Z11) >= cb - EPS).any(axis=1).sum())
fw_u, fw_b = n11u / 10_000, n11b / 10_000
fwer17b = 1 - (1 - Fraction(1, 340)) ** 17
anchor("A21-57", f"unadjusted {fw_u:.4f} (SE {sqrt(fw_u * (1 - fw_u) / 10_000):.4f}), exact {1 - 0.95**17:.5f}; "
       f"Bonferroni {fw_b:.4f} (SE {sqrt(fw_b * (1 - fw_b) / 10_000):.4f}), exact {float(fwer17b):.5f}")
for v, sh in ((Fraction(n11u, 10_000), "0.590"), (sqrt(fw_u * (1 - fw_u) / 10_000), "0.005"),
              (Fraction(n11b, 10_000), "0.051"), (sqrt(fw_b * (1 - fw_b) / 10_000), "0.002"), (fwer17b, "0.04884")):
    chk("A21-57", "P11", v, sh)
assert abs(fw_u - 0.58188) < 2 * sqrt(fw_u * (1 - fw_u) / 10_000) and abs(fw_b - float(fwer17b)) < 2 * sqrt(fw_b * (1 - fw_b) / 10_000)
has("S11", "$0.590\\pm0.005$")
has("S11", "$0.051\\pm0.002$")
has("P11 seed", "`default_rng([11, 20261011]).standard_normal((10000, 17))`")
has("S11", "Both lie within two standard errors of the exact values")

# ---------------------------------------------------------------- hygiene: tests on TR23
tests = (["mean (E3)", "mean before 2015-06-01", "mean from 2015-06-01", "regimes' difference (E4)",
          "up-day frequency (E2)", "down after down (E6)", "falls after falls (E7)"]
         + [f"calendar: {f[0]}" for f in fam]
         + ["Wednesday before 2015-06-01", "Wednesday from 2015-06-01",
            "blocks' variance against 4.95 (Problem 7)", "against 5.16 (Problem 7)", "Jarque-Bera (Problem 9)"])
anchor("A21-58", f"{len(tests)} tests: " + ", ".join(tests))
chk("A21-58", "tests on TR23", len(tests), "29")
has("29 tests", "seven in Sections 2 to 5, the 17 of the calendar, Wednesday in each regime and three in Problems 7 and 9")
# X1's four rows are four of the 29: the mean, the two regimes' means and Wednesday's calendar test
assert {"mean (E3)", "mean before 2015-06-01", "mean from 2015-06-01", "calendar: Wed"} <= set(tests)
has("X1 note", "In-sample, 4 of 29 tests on TR23")
has("X1 note (U6)", "Row 4's other days include the 23 Saturday sessions (Section 6)")
assert (d.wd[d.wd != 2] == 5).sum() == 23   # the Saturdays are among Wednesday's "other days"
# m14 (ii): the mean's t-stat against the hurdle of 3 and against Bonferroni for the module's 29 tests
c29 = float(stats.norm.isf(0.025 / len(tests)))
print(f"Bonferroni's two-sided 5% level for {len(tests)} tests: {c29:.5f}; TR23's t-stat {tstat:.4f}")
chk("new", "Bonferroni level for 29 tests", c29, "3.134")
assert tstat > c29 > 3
has("m14", "TR23's mean clears both bars: its t-stat, 3.96, exceeds 3 and Bonferroni's 3.134 for this module's 29 tests")
# m5: the hygiene note names U28 and counts its two tests (Section 5's z = 18.5 and Problem 8's chi2)
has("hygiene (m5)", "[[LM16]]'s counts are U28's (28 TWSE sector price indices, 2008–2026), as printed; Section 5 and "
    "Problem 8 run two tests on them")
has("notation (m6)", "So $A=246.12$ sessions a year")
has("notation (m9, X10)", "$V$ a $\\chi^2$ variable")
has("t law (m9, X10)", "$V:=(T-1)s_{\\mathrm u}^2/\\sigma^2\\sim\\chi^2_{T-1}$")

# ====================================================================== A21-61: LM16's printed counts recounted on U28
u = u28()
col = {c: i for i, c in enumerate(u.names)}
xs, xf = u.X[:, col["Semiconductor"]], u.X[:, col["FinancialInsurance"]]
nU = len(xs)
fs, ff = xs <= -0.01 + EPS, xf <= -0.01 + EPS


def mahal(x: np.ndarray) -> np.ndarray:
    """d_t^2 of every row with the sample's means and divisor-T covariance matrix ((12.9), LM16's convention)."""
    xc_ = x - x.mean(axis=0)
    lo = np.linalg.cholesky(xc_.T @ xc_ / x.shape[0])
    return (np.linalg.solve(lo, xc_.T) ** 2).sum(axis=0)


d2 = mahal(np.column_stack([xs, xf]))
d5 = mahal(u.X[:, [col[c] for c in S5]])
q99 = float(stats.chi2.ppf(0.99, 5))
n177 = int((~(d2 <= 9 + EPS)).sum())
n291 = int((~(d5 <= q99 + EPS)).sum())
p9 = float(np.exp(-4.5))
anchor("A21-61", f"U28 {nU} days ({u.dates[0]} -> {u.dates[-1]}): Semiconductor <= -1% {int(fs.sum())}, "
       f"FinancialInsurance <= -1% {int(ff.sum())}, both {int((fs & ff).sum())}; pair d^2 > 9: {n177} against mean "
       f"{nU * p9:.4f}, SD {sqrt(nU * p9 * (1 - p9)):.4f} (z {(n177 - nU * p9) / sqrt(nU * p9 * (1 - p9)):.4f}); S5 d^2 "
       f"above the chi2_5 99% quantile {q99:.4f}: {n291} against {nU * 0.01:.2f}")
for v, sh in ((nU, "4,382"), (int(fs.sum()), "859"), (int(ff.sum()), "538"), (int((fs & ff).sum()), "347"),
              (n177, "177"), (nU * p9, "48.68"), (sqrt(nU * p9 * (1 - p9)), "6.94"), (n291, "291"),
              (Fraction(nU, 100), "43.8")):
    chk("A21-61", "LM16's counts on U28", v, sh)
assert (str(u.dates[0]), str(u.dates[-1])) == ("2008-12-02", "2026-10-08")
assert len(u.names) == u.X.shape[1] == 28   # "28 TWSE sector price indices, 2008–2026" (the hygiene note)

# ====================================================================== the charts carry the cited values
pw = json.loads((CHARTS / "lm21-power.json").read_text(encoding="utf-8"))
xv = pw["x"]["values"]
for sr_, years_ in ((1.0, 7.85), (0.5, 31.4), (0.25, 125.6)):
    assert any(abs(x - years80(sr_)) < 1e-3 for x in xv), years_
assert any(abs(x - years80(sr_a)) < 1e-3 for x in xv) and any(abs(x - d.years) < 1e-3 for x in xv)
nd = json.loads((CHARTS / "lm21-nulldist.json").read_text(encoding="utf-8"))
vl = sorted(round(a["x"], 6) for a in nd["ann"] if a["type"] == "vline")
assert vl == sorted(round(v, 6) for v in (tstat, reg["before"][2], reg["from"][2])), vl
pvj = json.loads((CHARTS / "lm21-pvalues.json").read_text(encoding="utf-8"))
assert [round(v, 9) for v in pvj["series"][0]["y"]] == [round(log10(p), 9) for p in ps_sorted]
assert [p_["label"] for p_ in pvj["points"]] == ["Wed 0.018", "Dec 0.127"]

# ====================================================================== structure: labels and citations
ex_labels = re.findall(r"\[!exhibit\][^\n]*\{#([\w-]+)\}", RAW)
eg_labels = re.findall(r"\[!example\][^\n]*\{#([\w-]+)\}", RAW)
assert len(ex_labels) == 7 and len(eg_labels) == 10, (ex_labels, eg_labels)
for lab in ex_labels:
    if f"[[ex:{lab}]]" not in RAW:
        FAILS.append(f"exhibit {lab} is never cited")
for kind, lab in re.findall(r"\[\[(ex|eg):([\w-]+)\]\]", RAW):
    if lab not in (ex_labels if kind == "ex" else eg_labels):
        FAILS.append(f"[[{kind}:{lab}]] has no target")
for lab in ex_labels:
    if lab not in ("case", "independence") and not (CHARTS / f"lm21-{lab}.json").exists():
        FAILS.append(f"src/data/lm21-{lab}.json is missing")
print(f"labels: {len(ex_labels)} exhibits, {len(eg_labels)} examples")

# ====================================================================== report
body = TEXT.split("\n## Glossary", 1)[0]
nums = set(re.findall(r"(?<![\w.])\d+\.\d+|(?<![\w.,])\d{1,3}(?:,\d{3})+", body))
left = sorted(n for n in nums if n not in COVERED)
print(f"\nnumbers with a decimal point or thousands separator not covered by a check ({len(left)}):")
print("   " + " ".join(left))
print(f"\nvalues within a tenth of a last-digit unit of a rounding boundary ({len(NEARS)}):")
for line in NEARS:
    print("   ", line)
print(f"\nanchor differences ({len(ANCHOR_DIFFS)}):")
for a in ANCHOR_DIFFS:
    print("   ", a)
if FAILS:
    print(f"\nFAILED ({len(FAILS)}):")
    for f in FAILS:
        print("   ", f)
    sys.exit(1)
print(f"\nall {N_CHECKS} checks passed")
