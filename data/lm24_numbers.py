"""Every number that LM24 (Bayesian Inference and Shrinkage) prints, computed and checked against src/lm24.md.

Run:  uv run python data/lm24_numbers.py
      (after data/vol3_series.py, which builds TR23, and data/vol2_series.py, which builds U28's closes)

Inputs and conventions: data/lm24_common.py (TR23 from data/processed/vol3_taiex.parquet; U28 from data/lm10_series.py's
u28(); divisors, the normal model, Kelly, James-Stein, the out-of-sample miss, exact beta probabilities and the two
simulated experiments with their seeds). The module text is src/lm24.md; plans/vol-4-anchors.md holds the Stage 1
anchors A24-01 .. A24-61, which data/vol4_anchors_lm24.py prints.

Checks (each stops the script on a failure):
  chk(label, value, fmt, printed)  format(value, fmt) equals the printed string, the value does not sit on a rounding
                                   tie of that format, and the printed string is in the module as a whole number.
                                   A value within a tenth of a printed unit of a rounding boundary is listed at the end
                                   ("near a boundary"). Hand computations are redone from the printed, rounded inputs
                                   (project/PITFALLS.md section 7) as well as from unrounded values.
  has(label, text)                 a literal string (a phrase, a fraction, a table row) is in the module.
  sci(label, value, digits, printed)  a number printed as m\\times10^{e}.
  anchor(id, got)                  compares a value string with plans/vol-4-anchors.md and reports a difference (never
                                   forced). The strings are built here with the anchor script's formats from this
                                   script's own computations.
At the end the script lists the numbers of the module that no check covered, the values near a rounding boundary and
the anchor differences, and prints "all N checks passed".
"""
import math
import re
import sys
from fractions import Fraction
from math import sqrt
from pathlib import Path

import numpy as np
from scipy import optimize, stats

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import lm24_common as C

MD = ROOT / "src" / "lm24.md"
ANCHORS = ROOT / "plans" / "vol-4-anchors.md"


def norm_text(s: str) -> str:
    """The module text with TeX thousands separators, escaped percent signs, \\text{} and minus signs made plain."""
    s = s.replace("{,}", ",").replace("\\%", "%").replace("\u2212", "-").replace("\\,", "")
    return re.sub(r"\\text\{\s*([^}]*)\}", r" \1", s)


RAW_MD = MD.read_text(encoding="utf-8")
TEXT = norm_text(RAW_MD)
N_CHECKS = 0
COVERED: set[str] = set()
NEAR: list[str] = []
ANCHOR_DIFFS: list[str] = []


def in_text(printed: str) -> bool:
    """The printed number appears as a whole number (2.323 is not inside 2.3235, 0.32 not inside 10.32)."""
    return re.search(r"(?<![\d.])" + re.escape(printed) + r"(?![\d])", TEXT) is not None


def _decimals(fmt: str) -> int:
    m = re.search(r"\.(\d+)", fmt)
    return int(m.group(1)) if m else 0


def tie(value: float, fmt: str) -> bool:
    """True when value lies on a rounding boundary of fmt (a reader rounding by hand could go either way)."""
    if fmt.endswith(("e", "g")):
        return False
    scaled = abs(value) * 10 ** _decimals(fmt) * (100 if "%" in fmt else 1)
    return abs(scaled - math.floor(scaled) - 0.5) < 1e-6


def near(value: float, fmt: str) -> bool:
    """Within a tenth of a printed unit of a rounding boundary (the brief's flag)."""
    if fmt.endswith(("e", "g", ",", "d")):
        return False
    scaled = abs(value) * 10 ** _decimals(fmt) * (100 if "%" in fmt else 1)
    return abs(scaled - math.floor(scaled) - 0.5) < 0.1


def chk(label: str, value: float, fmt: str, printed: str) -> None:
    global N_CHECKS
    got = format(value, fmt)
    ok = got == printed and in_text(printed) and not tie(value, fmt)
    print(f"CHECK {label}: {got} (printed {printed}) {'ok' if ok else 'MISMATCH'}")
    assert got == printed, (label, got, printed)
    assert not tie(value, fmt), ("rounding tie: print more digits", label, value)
    assert in_text(printed), f"{label}: {printed!r} not found in src/lm24.md"
    if near(value, fmt):
        NEAR.append(f"{label}: {value!r} printed {printed}")
    COVERED.add(printed.lstrip("-"))
    N_CHECKS += 1


def has(label: str, text: str) -> None:
    global N_CHECKS
    assert text in TEXT, f"{label}: {text!r} not found in src/lm24.md"
    print(f"CHECK {label}: '{text}' in text ok")
    for num in re.findall(r"\d[\d,]*\.?\d*", text):
        COVERED.add(num.rstrip(".,"))
    N_CHECKS += 1


def same(label: str, got: str, printed: str) -> None:
    """A value produced as a string (a fraction, a rank) equals the printed one, which is in the text."""
    global N_CHECKS
    assert got == printed, (label, got, printed)
    assert printed in TEXT, f"{label}: {printed!r} not found in src/lm24.md"
    print(f"CHECK {label}: {got} ok")
    for num in re.findall(r"\d[\d,]*\.?\d*", printed):
        COVERED.add(num.rstrip(".,"))
    N_CHECKS += 1


def sci(label: str, value: float, digits: int, printed: str) -> None:
    """A number printed as m\\times10^{e} in the text: printed is 'm e', e.g. '3.8 -5'."""
    global N_CHECKS
    mant, ex = printed.split()
    got = f"{value:.{digits}e}"
    assert float(got) == float(f"{mant}e{ex}") and len(mant.replace(".", "").lstrip("-")) == digits + 1, (label, got, printed)
    tex = f"{mant}\\times10^{{{ex}}}"
    assert tex in TEXT, f"{label}: {tex!r} not found in src/lm24.md"
    m = value / 10 ** math.floor(math.log10(abs(value)))
    if near(m, f".{digits}f"):
        NEAR.append(f"{label}: {value!r} printed {tex}")
    print(f"CHECK {label}: {got} (printed {tex}) ok")
    COVERED.add(mant)
    N_CHECKS += 1


# ---------------------------------------------------------------- anchors (formats of data/vol4_anchors_lm24.py)
def _anchor_values() -> dict[str, str]:
    rows: dict[str, str] = {}
    sec = ANCHORS.read_text(encoding="utf-8").split("## LM24", 1)[1].split("\n## ", 1)[0]
    for line in sec.splitlines():
        if line.startswith("| A24-"):
            cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
            rows[cells[0]] = cells[3].strip("`")
    return rows


ANCHOR_ROWS = _anchor_values()
assert len(ANCHOR_ROWS) == 61, len(ANCHOR_ROWS)


def anchor(aid: str, got: str) -> None:
    """Compare with plans/vol-4-anchors.md; a difference is reported, not forced."""
    expected = ANCHOR_ROWS[aid]
    tag = "ok" if got == expected else "DIFFERS"
    print(f"ANCHOR {aid}: {tag}" + ("" if got == expected else f"\n    script {got}\n    anchor {expected}"))
    if got != expected:
        ANCHOR_DIFFS.append(f"{aid}: script {got} | anchor {expected}")


def flag(y: float, d: int) -> str:
    scaled = y * 10**d
    frac = scaled - math.floor(scaled)
    if abs(frac - 0.5) >= 0.1:
        return ""
    lo, hi = math.floor(scaled) / 10**d, (math.floor(scaled) + 1) / 10**d
    return f" [near {lo:.{max(d, 0)}f} / {hi:.{max(d, 0)}f}]"


def v(x: float, *ds: int, pct: bool = False, extra: int = 3) -> str:
    y = 100 * x if pct else x
    out = f"{y:.{max(ds) + extra}f}" + ("%" if pct else "")
    return out + "".join(flag(y, d) for d in sorted(set(ds), reverse=True))


def sig(x: float, *ns: int) -> str:
    e = math.floor(math.log10(abs(x)))
    m = x / 10**e
    return f"{m:.{max(ns) + 1}f}e{e:+d}" + "".join(flag(m, n - 1) for n in sorted(set(ns), reverse=True))


def mcs(e: np.ndarray, d: int = 1, dse: int = 2) -> str:
    m, se_ = C.mc_mean_se(e)
    return f"{v(m, d, extra=2)} (SE {v(se_, dse, extra=2)})"


# ====================================================================== data (notation note, hygiene note)
T, A, Rb, s, s_u, se, fhat, vol, years = C.T, C.A, C.RB, C.S, C.S_U, C.SE, C.FHAT, C.VOL, C.YEARS
print(f"TR23: T = {T}, {C.DATES_ALL[1]} .. {C.DATES_ALL[-1]}, {C.DAYS} days, {years:.6f} years, A = {A:.6f}")
chk("T (TR23)", T, ",", "5,849")
chk("years, two decimals", years, ".2f", "23.76")
chk("years, one decimal", years, ".1f", "23.8")
chk("A (TR23)", A, ".2f", "246.12")
has("first return", "3 January 2003")
has("last date", "8 October 2026")
chk("s (%), divisor T", 100 * s, ".4f", "1.2084")
chk("T (U28)", C.T28, ",", "4,382")
chk("A (U28)", C.A28, ".4f", "245.4794")
chk("half", C.H, ",", "2,191")
has("U28 first return", "2 December 2008")
has("halves' dates", "2 December 2008 → 6 October 2017 and 11 October 2017 → 8 October 2026")
has("retrieval TR23", "retrieved 18 October 2026")
has("retrieval U28", "retrieved 11 October 2026")
anchor("A24-01", f"{len(C.DATES_ALL)} closes {C.DATES_ALL[0]} -> {C.DATES_ALL[-1]}")
anchor("A24-02", f"{T} returns {C.DATES_ALL[1]} -> {C.DATES_ALL[-1]}")
anchor("A24-03", f"days {C.DAYS}; years {v(years, 2, 1)}; A {v(A, 2)}")
anchor("A24-04", f"Rbar {v(Rb, 4, pct=True)}; s {v(s, 4, pct=True)} (divisor T; lm14.md:240-241 prints 0.0625%, 1.2084%)")
anchor("A24-05", f"T {C.T28}; N {C.N}; {C.SMP.dates[0]} -> {C.SMP.dates[-1]}; years {C.SMP.years:.6f}; A {v(C.A28, 4)}")
anchor("A24-06", f"{C.H} + {C.T28 - C.H}: {C.SMP.dates[0]} -> {C.SMP.dates[C.H - 1]}; {C.SMP.dates[C.H]} -> {C.SMP.dates[-1]}")

# ====================================================================== case (U28 halves, price indices)
names, a1, a2 = C.NAMES, C.A1, C.A2
ORD = {1: "first", 2: "second", 5: "fifth", 9: "ninth", 20: "20th", 28: "last"}


def sector(name: str) -> str:
    i = names.index(name)
    return (f"{name} {v(float(a1[i]), 2, pct=True)} (rank {C.rank(a1, i)}) -> {v(float(a2[i]), 2, pct=True)} "
            f"(rank {C.rank(a2, i)})")


i_auto, i_ship = names.index("Automobile"), names.index("ShippingTransportation")
i_semi, i_epc = names.index("Semiconductor"), names.index("ElectronicPartsComponents")
chk("Automobile first half", 100 * a1[i_auto], ".2f", "21.65")
chk("Automobile second half", 100 * a2[i_auto], ".2f", "3.67")
assert (C.rank(a1, i_auto), C.rank(a2, i_auto)) == (1, 20), "Automobile ranks"
has("Automobile led", "Automobile led")
has("Automobile 20th", "it ranked 20th, at 3.67%")
chk("Shipping first half", 100 * a1[i_ship], ".2f", "1.89")
chk("Shipping second half", 100 * a2[i_ship], ".2f", "17.57")
assert (C.rank(a1, i_ship), C.rank(a2, i_ship)) == (28, 5), "Shipping ranks"
has("Shipping last to fifth", "ShippingTransportation went from last, 1.89%, to fifth, 17.57%")
chk("Semiconductor first", 100 * a1[i_semi], ".2f", "16.86")
chk("Semiconductor second", 100 * a2[i_semi], ".2f", "29.64")
assert (C.rank(a1, i_semi), C.rank(a2, i_semi)) == (2, 2), "Semiconductor ranks"
has("Semiconductor second in both", "Semiconductor was second in both (16.86% → 29.64%)")
chk("EPC first", 100 * a1[i_epc], ".2f", "12.19")
chk("EPC second", 100 * a2[i_epc], ".2f", "31.08")
assert (C.rank(a1, i_epc), C.rank(a2, i_epc)) == (9, 1), "EPC ranks"
has("EPC ninth to first", "ElectronicPartsComponents went from ninth (12.19%) to first (31.08%)")
corr = float(np.corrcoef(a1, a2)[0, 1])
chk("halves' correlation", corr, ".2f", "-0.05")
gm1, gm2 = float(a1.mean()), float(a2.mean())
chk("first-half grand mean", 100 * gm1, ".2f", "10.49")
miss_own, miss_grand = C.oos(C.M1, C.M2, 1.0), C.oos(C.M1, C.M2, 0.0)
chk("miss, own means", 100 * miss_own, ".1f", "9.8")
chk("miss, grand mean", 100 * miss_grand, ".1f", "8.5")
anchor("A24-07", sector("Automobile"))
anchor("A24-08", sector("ShippingTransportation"))
anchor("A24-09", f"Pearson {v(corr, 2)} (Spearman {float(stats.spearmanr(a1, a2).statistic):.5f}, not printed)")
anchor("A24-10", f"grand means {v(gm1, 2, pct=True)}; {v(gm2, 2, pct=True)}")
anchor("A24-11", f"c=1 (own means) {v(miss_own, 1, pct=True)}; c=0 (grand mean) {v(miss_grand, 1, pct=True)}")
anchor("A24-25", f"{sector('Semiconductor')}; {sector('ElectronicPartsComponents')}")

# TR23's annual figures (LM19's, LM20's, LM21's), the plug-in fraction (LM20's)
chk("A Rbar (LM19's)", 100 * A * Rb, ".2f", "15.38")
chk("A Rbar, one decimal (X4)", 100 * A * Rb, ".1f", "15.4")
chk("sqrt(A) s (LM19's)", 100 * vol, ".2f", "18.96")
chk("SE A s/sqrt(T) (LM20's)", 100 * A * se, ".2f", "3.89")
t_u, t_s = Rb / (s_u / sqrt(T)), Rb / se
chk("t-stat with s_u (LM21's)", t_u, ".2f", "3.96")
chk("t-stat with s_u, six decimals", t_u, ".6f", "3.955678")
chk("t-stat with s, six decimals", t_s, ".6f", "3.956017")
chk("s_u / s", s_u / s, ".7f", "1.0000855")
chk("fhat (LM20's)", fhat, ".2f", "4.28")
anchor("A24-12", f"A Rbar {v(A * Rb, 2, 1, pct=True)} (LM19's); sqrt(A) s {v(vol, 2, pct=True)} (LM19's); SE A s/sqrt(T) "
       f"{v(A * se, 2, pct=True)} (LM20's); t-stat with s_u {v(t_u, 2, extra=4)} (LM21's (21.1)); "
       f"with s {v(t_s, 2, extra=4)}; years {v(years, 1)}")
anchor("A24-13", f"plug-in Rbar/s^2 {v(fhat, 2)} (LM20's)")

# ====================================================================== section 2: the manager
a_exact = float(optimize.brentq(lambda a: float(stats.beta.sf(0.55, a, a)) - 0.10, 1.0, 1000.0))
near_int = min(range(70, 95), key=lambda a: abs(float(stats.beta.sf(0.55, a, a)) - 0.10))
assert near_int == 82
pr_prior = C.beta_sf(82, 82, C.P55)
sd_prior = float(stats.beta.std(82, 82))
assert abs(sd_prior - sqrt(82 * 82 / (164**2 * 165))) < 1e-15        # the variance formula of the text
chk("a solving the 10% share", a_exact, ".2f", "81.96")
chk("prior share at 82", 100 * float(pr_prior), ".1f", "10.0")
chk("prior SD", sd_prior, ".3f", "0.039")
has("n0 = 164", "worth $n_0=164$ months")
anchor("A24-15", f"a solving Pr(theta>=0.55)=0.10 for Beta(a,a): {v(a_exact, 2, extra=2)}; Beta(82,82): Pr "
       f"{v(float(pr_prior), 1, pct=True)}, SD {v(sd_prior, 3)}; n0 = 164 months")
# E1 (sceptic)
pr_post = C.beta_sf(90, 86, C.P55)
same("E1 mean as fractions", f"{Fraction(90, 176).numerator * 2}/176={Fraction(90, 176)}", "90/176=45/88")
chk("E1 mean", 90 / 176, ".4f", "0.5114")
same("E1 c", f"12/176={Fraction(12, 176)}", "12/176=3/44")
chk("E1 c", 12 / 176, ".3f", "0.068")
chk("E1 c in %", 100 * 12 / 176, ".1f", "6.8")
shift = Fraction(3, 44) * (Fraction(8, 12) - Fraction(1, 2))
assert shift == Fraction(1, 88) and Fraction(90, 176) - Fraction(1, 2) == shift
has("E1 shift", r"\tfrac3{44}\times(\tfrac8{12}-\tfrac12)=\tfrac1{88}=0.0114")
chk("E1 shift", float(shift), ".4f", "0.0114")
chk("E1 Pr(theta>=0.55)", 100 * float(pr_post), ".1f", "15.3")
chk("LM13's two-type posterior (lm13.md:334)", 100 * 0.1 * 1.4064 / 0.9 / (1 + 0.1 * 1.4064 / 0.9), ".1f", "13.5")
anchor("A24-26", f"Beta(90,86): mean {Fraction(90, 176)} = {v(90 / 176, 4)} (shift {v(90 / 176 - 0.5, 4)}); c "
       f"{Fraction(12, 176)} = {v(12 / 176, 3)} = {v(12 / 176, 1, pct=True)}; Pr(theta>=0.55) "
       f"{v(float(pr_post), 1, pct=True)} exact; LM13 13.5% (lm13.md:334)")
# E2 (flat)
pr_flat_half, pr_flat_55 = C.beta_sf(9, 5, Fraction(1, 2)), C.beta_sf(9, 5, C.P55)
assert pr_flat_half == Fraction(7099, 8192)
has("E2 fractions", "$9/14=0.643$ and $c=12/14=6/7$")
chk("E2 mean", 9 / 14, ".3f", "0.643")
has("E2 Pr > 0.5 exact", "7,099/8,192=86.7%")
chk("E2 Pr > 0.5", 100 * float(pr_flat_half), ".1f", "86.7")
chk("E2 Pr >= 0.55", 100 * float(pr_flat_55), ".1f", "77.2")
q_lo, q_hi = (float(q) for q in stats.beta.ppf([0.025, 0.975], 9, 5))
chk("E2 2.5% quantile", q_lo, ".2f", "0.39")
chk("E2 97.5% quantile", q_hi, ".2f", "0.86")
anchor("A24-27", f"Beta(9,5): mean {Fraction(9, 14)} = {v(9 / 14, 3)}; c {Fraction(12, 14)} = {12 / 14:.5f}; "
       f"Pr(theta>0.5) {pr_flat_half} = {v(float(pr_flat_half), 1, pct=True)}; Pr(theta>=0.55) "
       f"{v(float(pr_flat_55), 1, pct=True)}; 95% {v(q_lo, 2)} to {v(q_hi, 2)}")
need_n = next(n for n in range(3, 3000, 3) if C.beta_sf(82 + 2 * n // 3, 82 + n // 3, C.P55) > Fraction(1, 2))
pr_need = C.beta_sf(82 + 2 * need_n // 3, 82 + need_n // 3, C.P55)
pr_before = C.beta_sf(82 + 2 * (need_n - 3) // 3, 82 + (need_n - 3) // 3, C.P55)
chk("E2 months", need_n, "d", "72")
chk("E2 Pr at 72", 100 * float(pr_need), ".1f", "51.2")
chk("E2 Pr at 69", 100 * float(pr_before), ".1f", "49.4")
has("E2 at 69", "49.4% at 69")
has("E2 c", "c=72/236=0.305")
chk("E2 c", need_n / (need_n + 164), ".3f", "0.305")
has("E2 six years", "six years barely convince the sceptic")
assert need_n == 6 * 12
anchor("A24-38", f"record 2/3: smallest n (multiple of 3) with Pr(theta>=0.55) > 1/2: {need_n} months; Pr "
       f"{v(float(pr_need), 1, pct=True)}; at {need_n - 3}: {v(float(pr_before), 1, pct=True)}; c "
       f"{v(need_n / (need_n + 164), 3)}")
# X2 note, pitfall
has("X2 probabilities", "15.3% and 77.2%")
flat55 = 1 - 0.55
chk("flat prior's share at 0.55 (%)", 100 * flat55, ".0f", "45")
assert abs(flat55 / 0.10 - 4.5) < 1e-12
has("four and a half times", "four and a half times [[LM13]]'s share")
# KC section 2
has("KC2", "the posterior is Beta(5, 3), with mean $5/8=0.625$")
chk("KC2 mean", 5 / 8, ".3f", "0.625")
has("KC2 c", r"$c=4/(4+4)=\tfrac12$")
anchor("A24-18", f"Beta(2,2), 3 of 4 -> Beta(5,3): mean {Fraction(5, 8)} = {v(5 / 8, 3)}; c {Fraction(4, 8)}")

# ====================================================================== section 3: the normal mean
c10 = C.weight(0.10)
pm10, psd10 = C.post(c10)
pm_h, psd_h = C.post(0.5)
chk("c = 1/2: posterior mean", 100 * A * pm_h, ".2f", "7.69")
chk("c = 1/2: posterior mean from printed 15.38/2", 15.38 / 2, ".2f", "7.69")
chk("c = 1/2: posterior SD", 100 * A * psd_h, ".2f", "2.75")
chk("c = 1/2: posterior SD from printed 3.89/sqrt(2)", 3.89 / sqrt(2), ".2f", "2.75")
anchor("A24-16", f"c = 1/2: prior SD = SE {v(A * se, 2, pct=True)}; posterior mean {v(A * pm_h, 2, pct=True)}; "
       f"SD {v(A * psd_h, 2, pct=True)} (from printed 3.89/sqrt(2) = {3.89 / sqrt(2):.4f}, 15.38/2 = 7.69)")
eta = T * Rb**2 / (T * Rb**2 + s**2)
chk("LM20's eta* = c at a prior SD equal to the mean", eta, ".3f", "0.940")
assert abs(C.weight(A * Rb) - eta) < 1e-12
anchor("A24-61", f"LM20's eta* = T Rbar^2/(T Rbar^2 + s^2) {v(eta, 3)} (LM20's E1 prints 0.940); c at A sigma0 = A Rbar "
       f"{v(C.weight(A * Rb), 3)}")
# minimizing the prior-averaged MSE of eta Rbar gives eta = c (checked numerically at 10 points)
s0d = 0.10 / A
eta_min = float(optimize.minimize_scalar(lambda e: e**2 * se**2 + (1 - e) ** 2 * s0d**2, bounds=(0, 1),
                                         method="bounded", options={"xatol": 1e-12}).x)
assert abs(eta_min - c10) < 1e-8
# E3
chk("E3 c", c10, ".3f", "0.869")
chk("E3 c from printed 3.89", 100 / (100 + 3.89**2), ".3f", "0.869")
chk("E3 posterior mean", 100 * A * pm10, ".1f", "13.4")
chk("E3 posterior mean from printed", 0.869 * 15.38, ".1f", "13.4")
chk("E3 posterior SD", 100 * A * psd10, ".1f", "3.6")
chk("E3 posterior SD from printed", sqrt(0.869) * 3.89, ".1f", "3.6")
n0_10 = s**2 / (0.10 / A) ** 2
chk("E3 prior worth (years)", n0_10 / A, ".2f", "3.59")
chk("E3 prior worth from printed (18.96/10)^2", (18.96 / 10) ** 2, ".2f", "3.59")
chk("E3 c = 1/4 worth (years)", 3 * years, ".1f", "71.3")
anchor("A24-39", f"A sigma0 = 10: c {v(c10, 3)}; posterior mean {v(A * pm10, 1, pct=True)}; SD {v(A * psd10, 1, pct=True)}; "
       f"from printed 0.869, 15.38, 3.89: {0.869 * 15.38:.4f}, {sqrt(0.869) * 3.89:.4f}")
anchor("A24-40", f"A sigma0 = 10: {n0_10:.1f} returns = {v(n0_10 / A, 2)} years (from printed (18.96/10)^2 = "
       f"{(18.96 / 10) ** 2:.4f}); c = 1/2: {T} returns = {v(years, 1)} years; c = 1/4: {3 * T} returns = "
       f"{v(3 * years, 1)} years")
# E4
vpm, epv = c10 * 0.10**2, (A * psd10) ** 2
assert abs(vpm + epv - 0.01) < 1e-15
chk("E4 variance of the posterior mean", vpm * 1e4, ".1f", "86.9")
chk("E4 expected posterior variance", epv * 1e4, ".1f", "13.1")
has("E4 sum", "$100=86.9+13.1$")
anchor("A24-41", f"(16.6) at A sigma0 = 10, points^2: 100 = {v(vpm * 1e4, 1)} (variance of the posterior mean) + "
       f"{v(epv * 1e4, 1)} (expected posterior variance); sum {(vpm + epv) * 1e4:.10f}")
# pitfall: a prior SD annualized by sqrt(A)
s0_wrong, s0_right = 0.10 / sqrt(A), 0.10 / A
c_wrong = s0_wrong**2 / (s0_wrong**2 + se**2)
chk("pitfall: daily sigma0 by sqrt(A) (%)", 100 * s0_wrong, ".3f", "0.637")
chk("pitfall: daily sigma0 by A (%)", 100 * s0_right, ".4f", "0.0406")
chk("pitfall: c with sqrt(A)", c_wrong, ".4f", "0.9994")
# KC section 3
chk("KC3 nine times 3.59", 9 * n0_10 / A, ".1f", "32.3")
chk("KC3 unrounded worth, three decimals (K1)", n0_10 / A, ".3f", "3.594")
assert abs(n0_10 / A - (vol / 0.10) ** 2) < 1e-12                       # the worth in years is (sqrt(A) s / A sigma0)^2
chk("KC3 sqrt(A) s, three decimals (N-2)", 100 * vol, ".3f", "18.957")
chk("KC3 worth from printed 18.957 (N-2)", (18.957 / 10) ** 2, ".3f", "3.594")
chk("KC3 from printed 3.594", 9 * 3.594, ".1f", "32.3")
chk("KC3 from printed 18.957, nine times", 9 * (18.957 / 10) ** 2, ".1f", "32.3")
chk("KC3 from printed 3.59", 9 * 3.59, ".1f", "32.3")
has("KC3 answer (N-2)", "nine times the unrounded worth, $(18.957/10)^2=3.594$: 32.3 years")
anchor("A24-19", f"A sigma0 = 10 worth {v(n0_10 / A, 2)} years; c = 0.9 needs 9 x that = {v(9 * n0_10 / A, 1)} years "
       f"(from printed 3.59: {9 * 3.59:.2f})")
anchor("A24-31", f"{v(C.Z975, 2, extra=4)} (lm15.md:194 prints 1.9600)")
chk("Phi^-1(0.975)", C.Z975, ".2f", "1.96")

# ====================================================================== section 4: X4 and the credible intervals
sig_q, sig_h = A * se / sqrt(3), A * se
TABLE: dict[str, tuple[float, float, int]] = {"q": (0.25, sig_q, 1), "h": (0.5, sig_h, 1), "10": (c10, 0.10, 2),
                                              "flat": (1.0, math.inf, 0)}


def row_values(c: float, s0: float) -> tuple[float, float, float, float, float, float, float]:
    m, sd = C.post(c)
    lo, hi = A * (m - C.Z975 * sd), A * (m + C.Z975 * sd)
    worth = (vol / s0) ** 2 if math.isfinite(s0) else 0.0
    return worth, A * m, lo, hi, float(stats.norm.cdf(-m / sd)), c * fhat, sd


def row_anchor(c: float, s0: float, dw: int) -> str:
    worth, am, lo, hi, p, _fb, _ = row_values(c, s0)
    s0_txt = v(s0, 2, pct=True) if math.isfinite(s0) else "inf"
    return (f"A sigma0 {s0_txt}; worth {v(worth, dw)} years; c {v(c, 3, 2)}; mean {v(am, 1, pct=True)}; 95% "
            f"{v(lo, 1, pct=True)} to {v(hi, 1, pct=True)}; Pr(mu<=0) {sig(p, 2)}; Bayes fraction {v(c * fhat, 2)}")


ROWS_PRINTED = {
    "q": "| Quarter Kelly | 2.25 | 71.29 | 0.250 | 3.8 | 0.0 to 7.7 | 0.024 | 1.07 |",
    "h": "| Half Kelly | 3.89 | 23.76 | 0.500 | 7.7 | 2.3 to 13.1 | 0.0026 | 2.14 |",
    "10": "| 10 points | 10.00 | 3.59 | 0.869 | 13.4 | 6.3 to 20.5 | 0.00011 | 3.72 |",
    "flat": "| Flat | ∞ | 0 | 1 | 15.4 | 7.8 to 23.0 | 0.000038 | 4.28 |",
}
for key, (c, s0, _) in TABLE.items():
    worth, am, lo, hi, p, fb, _sd = row_values(c, s0)
    p_txt = f"{p:.2g}" if p >= 1e-3 else f"{p:.1e}"
    p_dec = format(float(f"{p:.2g}"), "f").rstrip("0")
    cells = [f"{100 * s0:.2f}" if math.isfinite(s0) else "∞", f"{worth:.2f}" if worth else "0",
             f"{c:.3f}" if key != "flat" else "1", f"{100 * am:.1f}", f"{100 * lo:.1f} to {100 * hi:.1f}",
             p_dec, f"{fb:.2f}"]
    built = ROWS_PRINTED[key].split(" | ")
    assert built[1:-1] + [built[-1].rstrip(" |")] == cells, (key, cells, ROWS_PRINTED[key], p_txt)
    has(f"X4 row {key}", ROWS_PRINTED[key])
    for val, fmt in ((worth, ".2f"), (100 * am, ".1f"), (100 * lo, ".1f"), (100 * hi, ".1f"), (fb, ".2f")):
        assert not tie(val, fmt), (key, val, fmt)
        if near(val, fmt):
            NEAR.append(f"X4 row {key}: {val!r} printed {format(val, fmt)}")
    m_ = p / 10 ** math.floor(math.log10(p))
    if near(m_, ".1f"):
        NEAR.append(f"X4 row {key}: Pr {p!r}")
anchor("A24-28", "c = 1/4: " + row_anchor(0.25, sig_q, 1))
anchor("A24-29", "c = 1/2: " + row_anchor(0.5, sig_h, 1))
anchor("A24-30", "A sigma0 = 10: " + row_anchor(c10, 0.10, 2))
p_flat = float(stats.norm.cdf(-Rb / se))
anchor("A24-20", "flat: " + row_anchor(1.0, math.inf, 0) + f"; LM21's one-sided p-value Phi(-{t_u:.6f}) "
       f"{sig(float(stats.norm.cdf(-t_u)), 2)}")
# the note: the first two rows are defined by c, so their worth is 3 and 1 times the sample's span (m2)
chk("years, four decimals (priors note)", years, ".4f", "23.7645")
chk("quarter-Kelly worth from printed 3 x 23.7645", 3 * 23.7645, ".2f", "71.29")
chk("half-Kelly worth from printed 23.7645", 23.7645, ".2f", "23.76")
has("priors note (m2)", "their priors are worth three times and once the sample's 23.7645 years")
chk("A sigma0 for c = 1/4", 100 * sig_q, ".2f", "2.25")
chk("A sigma0 for c = 1/4 from printed 3.89/sqrt(3)", 3.89 / sqrt(3), ".2f", "2.25")
anchor("A24-14", f"A sigma0 = SE/sqrt(3) for c = 1/4: {v(sig_q, 2, pct=True)} (from printed 3.89: {v(3.89 / sqrt(3), 2, extra=3)}; "
       f"from 3.9: {v(3.9 / sqrt(3), 2, extra=3)}); = SE for c = 1/2: {v(sig_h, 2, pct=True)}")
# E5
_, _, lo_f, hi_f, _, _, _ = row_values(1.0, math.inf)
chk("E5 lower", 100 * lo_f, ".1f", "7.8")
chk("E5 upper", 100 * hi_f, ".1f", "23.0")
chk("E5 lower from printed", 15.38 - 1.96 * 3.89, ".1f", "7.8")
chk("E5 upper from printed", 15.38 + 1.96 * 3.89, ".1f", "23.0")
sci("E5 Pr(mu<=0), flat", p_flat, 1, "3.8 -5")
sci("LM21's one-sided p-value with s_u", float(stats.norm.cdf(-t_u)), 1, "3.8 -5")
_, _, lo10, hi10, p10, _, _ = row_values(c10, 0.10)
chk("E5 at 10 points: lower", 100 * lo10, ".1f", "6.3")
chk("E5 at 10 points: upper", 100 * hi10, ".1f", "20.5")
sci("E5 at 10 points: Pr(mu<=0)", p10, 1, "1.1 -4")
pr_pos_q = 1 - float(stats.norm.cdf(-0.25 * Rb / (0.5 * se)))
pr_pos_h = 1 - float(stats.norm.cdf(-0.5 * Rb / (sqrt(0.5) * se)))
chk("Pr(mu>0 | data), quarter-Kelly prior", 100 * pr_pos_q, ".1f", "97.6")
chk("Pr(mu>0 | data), half-Kelly prior", 100 * pr_pos_h, ".1f", "99.7")
assert float(stats.norm.sf(0.0)) == 0.5          # each prior itself, centred at zero, puts 50% on mu > 0 (U1)
has("U1: the posterior under the first row's prior", "Even under the prior of the first row, the posterior puts 97.6% on")
has("U1: the sceptics after the data", "After the data, both sceptics put high probability on a positive mean, 97.6% and 99.7%")
_, _, lo_h, hi_h, _, _, _ = row_values(0.5, sig_h)
has("pitfall 4 interval", "the same data give 2.3% to 13.1%")
assert (f"{100 * lo_h:.1f}", f"{100 * hi_h:.1f}") == ("2.3", "13.1")

# ====================================================================== section 5: James-Stein
km = np.array([1.0, 2.0, 3.0, 6.0])
kss = float(((km - km.mean()) ** 2).sum())
kc = 1 - (4 - 3) * 1.0 / kss
assert Fraction(kc).limit_denominator(100) == Fraction(13, 14) and kss == 14
has("KC5 sum", "$4+1+0+9=14$")
has("KC5 c_hat", r"\hat c=1-(4-3)\times1/14=13/14")
ests = [float(km.mean() + kc * (x - km.mean())) for x in km]
for x, p in zip(ests, ("1.14", "2.07", "3.00", "5.79")):
    chk(f"KC5 estimate {p}", x, ".2f", p)
assert Fraction(3) + Fraction(13, 14) * 3 == Fraction(81, 14)
has("KC5 exact", "5.79 (81/14 exactly)")
anchor("A24-21", f"means 1,2,3,6, noise 1: grand {km.mean():g}; sum {kss:g}; c_hat 13/14 = {kc:.6f}; estimates "
       f"8/7, 29/14, 3, 81/14 = {', '.join(v(x, 2) for x in ests)}")
# Experiment 1
e1 = C.experiment1()
raw1, js1, pp1, by1 = (C.mc_mean_se(e1[k]) for k in ("raw", "js", "pp", "bayes"))
chk("E6 raw", raw1[0], ".1f", "28.1")
chk("E6 JS", js1[0], ".1f", "15.5")
chk("E6 positive part", pp1[0], ".1f", "15.5")
chk("E6 Bayes", by1[0], ".1f", "14.0")
has("E6 standard errors", "Their standard errors are 0.08, 0.04, 0.04 and 0.04")
for lab_, (_, e_) , p in (("raw", raw1, "0.08"), ("JS", js1, "0.04"), ("pp", pp1, "0.04"), ("Bayes", by1, "0.04")):
    assert format(e_, ".2f") == p and not tie(e_, ".2f"), (lab_, e_)
    if near(e_, ".2f"):
        NEAR.append(f"E6 SE {lab_}: {e_!r} printed {p}")
chk("E6 mean c_hat", float(e1["c_pp"].mean()), ".2f", "0.50")
has("E6 theory", "$N-(N-3)/(1+\\sigma_0^2)=28-25/2=15.5$")
has("E6 Bayes theory", "$Nc\\sigma^2/T=14$")
assert 28 - 25 / 2 - 28 / 2 == 1.5
has("E6 cost", "costs 1.5 of the 14 that knowing them saves")
# the theorem's and the risk formula's source (SOURCES, Efron and Hastie 2016: (7.12)-(7.16) and §7.5)
has("theorem source", "Stated without proof (Efron and Hastie 2016, §7.1 and §7.5).")
has("risk formula source", "is stated without proof (Efron and Hastie 2016, equation 7.14)")
has("Efron and Hastie reference", "§7.1 (the James–Stein estimator toward the grand mean, its risk and the James–Stein theorem, "
    "equations 7.12–7.16) and §7.5 (the positive part)")
has("Wasserman citation (M2 c)", "(Wasserman 2004, ch. 11)")
has("Wasserman reference (M2 c)", "New York: Springer, ch. 11 (Bayesian inference)")
assert "Chopra" not in RAW_MD and "\\Gamma(a+1)" not in RAW_MD and "\\chi^2_k" not in RAW_MD   # m1; m3 (a, nu)
# N-4: the first Deep Dive declares m and v in its first sentence; the notation note scopes x in Section 5's Deep Dive
has("N-4 Deep Dive", "> [!deepdive]- Completing the square\n> Let $m$ and $v>0$ be numbers. By (24.1),")
assert "for numbers $m$ and $v>0$" not in RAW_MD
has("N-4 notation", "$x$ a value of $\\theta$ (in Section 5's Deep Dive, the argument of the $\\chi^2_\\nu$ density);")
anchor("A24-42", f"Experiment 1, 10,000 cross-sections: raw {mcs(e1['raw'])}; JS {mcs(e1['js'])}; positive part "
       f"{mcs(e1['pp'])}; Bayes 0.5x {mcs(e1['bayes'])}; mean c_hat (positive part) "
       f"{v(float(e1['c_pp'].mean()), 2, extra=2)}; mean unclipped 1 - 25/S {v(float(e1['c_js'].mean()), 2, extra=2)}")
anchor("A24-43", f"N - (N-3)/(1 + spread^2) at spread 0, 1, 3: {C.N - (C.N - 3)}, {C.N - (C.N - 3) / 2:g}, "
       f"{C.N - (C.N - 3) / 10:g}; Bayes N/2 = {C.N / 2:g} at spread 1")
has("Efron and Morris", "18 players' batting averages after their first 45 at-bats of 1970")

# ====================================================================== section 6: the sector halves
nz_r, sp1, b_r, c_r = C.js(C.X[:C.H])
chk("E7 noise", 100 * nz_r, ".2f", "7.18")
chk("E7 spread (divisor 28)", 100 * sp1, ".2f", "4.50")
chk("E7 1 - c_hat", b_r, ".2f", "2.27")
chk("E7 1 - c_hat from printed 7.18, 4.50", 25 * 7.18**2 / (28 * 4.50**2), ".2f", "2.27")
assert c_r == 0.0
co_f = C.c_opt(C.M1, C.M2)
chk("E7 best weight in hindsight", co_f, ".2f", "-0.09")
nz_d, sp_d, b_d, c_d = C.js(C.XD[:C.H])
assert abs(sp_d - sp1) < 1e-12 and c_d == 0.0          # removing each day's mean leaves the deviations unchanged
chk("E7 noise, common removed", 100 * nz_d, ".2f", "4.79")
chk("E7 1 - c_hat, common removed", b_d, ".2f", "1.01")
chk("E7 1 - c_hat, common removed, from printed", 25 * 4.79**2 / (28 * 4.50**2), ".2f", "1.01")
_, sp2, _, _ = C.js(C.X[C.H:])
chk("E7 second half spread", 100 * sp2, ".2f", "8.49")
# M3: one common noise variance stands in for 28 unequal ones (total noise, first half)
noise_i = C.A28 * np.sqrt(C.X[:C.H].var(axis=0, ddof=0) / C.H)
assert abs(float(np.sqrt((noise_i**2).mean())) - nz_r) < 1e-15          # E7's noise is the root of their average
chk("M3 smallest sector noise", 100 * float(noise_i.min()), ".1f", "4.8")
chk("M3 largest sector noise", 100 * float(noise_i.max()), ".1f", "9.7")
chk("M3 ratio of the noise variances (about 4)", float(noise_i.max() / noise_i.min()) ** 2, ".0f", "4")
b_min = (C.N - 3) * float(noise_i.min()) ** 2 / (C.N * sp1**2)          # 1 - c_hat if every noise were the smallest
assert b_min > 1                                                       # so c_hat = 0 under any average of the noises
print(f"N-1: 1 - c_hat with every sector at the smallest noise {b_min:.4f}; from printed 4.8, 4.50: "
      f"{25 * 4.8**2 / (28 * 4.50**2):.4f}")
assert 25 * 4.8**2 / (28 * 4.50**2) > 1                                 # the same from the printed values
has("M3 paragraph", "the sectors' noise variances differ by a factor of about 4 (half-widths 9 to 19 points in [[ex:forest]])")
has("M3 known", "Their average, estimated from 2,191 returns, is treated as known.")
has("M3 smallest noise (N-1)", "(24.4) gives $\\hat c=0$ even if every sector had the smallest noise, 4.8 points (the largest "
    "is 9.7), so $\\hat c=0$ does not depend on the averaging")
assert "lies below every sector's noise" not in RAW_MD
has("M3 l.289", "sum to zero each day, still co-move and have unequal noise")
anchor("A24-44", f"first half: noise {v(nz_r, 1, pct=True)}; spread SD (divisor 28) {v(sp1, 1, pct=True)}; 1 - c_hat "
       f"{v(b_r, 2)}; c_hat {c_r:g}")
anchor("A24-17", f"common removed, first half: noise {v(nz_d, 1, pct=True)}; 1 - c_hat {v(b_d, 2)}; c_hat {c_d:g}")
anchor("A24-45", f"optimal c (forward) {v(co_f, 2)}; deviations RMSE c=0 {v(C.oos(C.M1, C.M2, 0, True), 1, pct=True)}, "
       f"c=1 {v(C.oos(C.M1, C.M2, 1, True), 1, pct=True)}")
anchor("A24-46", f"second half spread SD (divisor 28) {v(sp2, 1, pct=True)}")
# X5
hw = C.A28 * C.Z975 * C.X[:C.H].std(axis=0, ddof=0) / sqrt(C.H)
chk("X5 smallest half-width", 100 * float(hw.min()), ".0f", "9")
chk("X5 largest half-width", 100 * float(hw.max()), ".0f", "19")
has("X5 half-widths", "half-widths from 9 to 19 points")
gap = np.abs(a1 - gm1) - hw
assert np.all(np.abs(gap) > C.EPS)
excl = int((gap >= C.EPS).sum())
assert excl == 0
has("X5 every interval contains", "Every interval contains the first half's grand mean, 10.49%")
anchor("A24-32", f"half-widths Phi^-1(0.975) A s_i/sqrt(2191): {v(float(hw.min()), 0, pct=True)} "
       f"({names[int(hw.argmin())]}) to {v(float(hw.max()), 0, pct=True)} ({names[int(hw.argmax())]})")
anchor("A24-33", f"first-half intervals excluding the first-half grand mean: {excl} of {C.N}; smallest margin "
       f"(half-width - abs(mean - grand mean)) {v(float(-gap.max()), 1, pct=True)} ({names[int(gap.argmax())]})")
# E8 and X6 (reverse)
_, _, b_rr, c_rr = C.js(C.X[C.H:])
_, _, b_dr, c_dr = C.js(C.XD[C.H:])
chk("E8 c_hat", c_rr, ".2f", "0.25")
chk("E8 c_hat, common removed", c_dr, ".2f", "0.59")
rev = {k: C.oos(C.M2, C.M1, c) for k, c in (("0", 0.0), ("chat", c_rr), ("cd", c_dr), ("1", 1.0))}
chk("E8 miss at c = 0", 100 * rev["0"], ".1f", "4.5")
chk("E8 miss at c_hat", 100 * rev["chat"], ".1f", "5.1")
chk("E8 miss at c_hat (common removed)", 100 * rev["cd"], ".1f", "6.9")
chk("E8 miss at c = 1", 100 * rev["1"], ".1f", "9.8")
has("X6 reverse values", "4.5, 5.1, 6.9 and 9.8 at $c=0$, 0.25, 0.59 and 1")
anchor("A24-34", f"estimated on the second half: c_hat {v(c_rr, 2)}; common removed {v(c_dr, 2)}; judged on the first: "
       f"RMSE c=0 {v(rev['0'], 1, pct=True)}, c=c_hat {v(rev['chat'], 1, pct=True)}, c=c_hat(common) "
       f"{v(rev['cd'], 1, pct=True)}, c=1 {v(rev['1'], 1, pct=True)}; optimal c {v(C.c_opt(C.M2, C.M1), 2)}")
# KC section 6
dev1, dev2 = C.M1 - C.M1.mean(), C.M2 - C.M2.mean()
assert np.all(np.abs(dev1) > C.EPS) and np.all(np.abs(dev2) > C.EPS)
agree = int(((dev1 >= C.EPS) & (dev2 >= C.EPS)).sum() + ((dev1 <= -C.EPS) & (dev2 <= -C.EPS)).sum())
chk("KC6 same side", agree, "d", "13")
has("KC6", "13 of 28. Independent halves would put a sector on the same side with probability $\\tfrac12$, so 14 on average")
anchor("A24-22", f"same side of the grand mean in both halves: {agree} of {C.N} (independent halves: {C.N / 2:g} expected)")

# ====================================================================== section 7: Kelly
f_star = C.kelly_exact(Rb)
kx10, kq10 = C.kelly_exact(pm10), C.kelly_bayes_quad(c10)
kxh, kxq = C.kelly_exact(0.5 * Rb), C.kelly_exact(0.25 * Rb)
chk("E9 f_B", c10 * fhat, ".2f", "3.72")
chk("E9 f_B from printed 0.869 x 4.28", 0.869 * 4.28, ".2f", "3.72")
chk("E9 exact (shifted)", kx10, ".2f", "3.62")
chk("E9 posterior-integrated", kq10, ".2f", "3.62")
chk("fhat* (LM17's 4.1381)", f_star, ".2f", "4.14")
assert f"{f_star:.4f}" == "4.1381"
ksd = psd10 / s**2
chk("E9 posterior SD of mu/sigma^2", ksd, ".2f", "1.01")
chk("E9 from printed 1.08 sqrt(0.869)", 1.08 * sqrt(0.869), ".2f", "1.01")
chk("LM20's mean-only SE of fhat", 1 / (s * sqrt(T)), ".2f", "1.08")
chk("E9 95% lower", c10 * fhat - C.Z975 * ksd, ".1f", "1.7")
chk("E9 95% upper", c10 * fhat + C.Z975 * ksd, ".1f", "5.7")
chk("E9 95% lower from printed", 3.72 - 1.96 * 1.01, ".1f", "1.7")
chk("E9 95% upper from printed", 3.72 + 1.96 * 1.01, ".1f", "5.7")
chk("E9 gap at c = 1", fhat - f_star, ".2f", "0.14")
chk("E9 gap at c = 1 from printed", 4.28 - 4.14, ".2f", "0.14")
chk("E9 gap at 10 points", c10 * fhat - kx10, ".2f", "0.10")
chk("E9 gap at 10 points from printed", 3.72 - 3.62, ".2f", "0.10")
chk("E9 exact at c = 1/2", kxh, ".2f", "2.11")
chk("E9 gap at c = 1/2", 0.5 * fhat - kxh, ".2f", "0.03")
chk("E9 gap at c = 1/2 from printed", 2.14 - 2.11, ".2f", "0.03")
chk("E9 1 - c at 10 points (%)", 100 * (1 - c10), ".0f", "13")
# M1: what the gap at c = 1 is made of. (4.2) with its mu^2 term gives Rbar / (s^2 + Rbar^2); the rest is non-normal.
quad_mu2 = Rb / (s**2 + Rb**2)
chk("E9 (4.2) with the mu^2 term", quad_mu2, ".2f", "4.27")
chk("E9 mu^2 part of the gap", fhat - quad_mu2, ".2f", "0.01")
chk("E9 the rest of the gap", quad_mu2 - f_star, ".2f", "0.13")
chk("E9 mu^2 part from printed 4.28 - 4.27", 4.28 - 4.27, ".2f", "0.01")
chk("E9 the rest from printed 4.27 - 4.14", 4.27 - 4.14, ".2f", "0.13")
assert 0.02 < (quad_mu2 - f_star) / quad_mu2 < 0.05                    # "a few per cent off a fraction"
# the cause test of PITFALLS section 7: the days mirrored about their mean keep the tails and drop the skewness
_sym = np.concatenate([C.R, 2 * Rb - C.R])
f_sym = float(optimize.brentq(lambda f: float((_sym / (1 + f * _sym)).mean()), 1e-6, 1 / abs(float(_sym.min())) - 1e-6,
                              xtol=1e-14))
tails_part, skew_part = quad_mu2 - f_sym, f_sym - f_star
print(f"M1 split at c = 1: mu^2 {fhat - quad_mu2:.4f}; tails {tails_part:.4f} (mirrored root {f_sym:.5f}); "
      f"skewness {skew_part:.4f}")
assert tails_part > 0.04 and skew_part > 0.04                           # both fat tails and skewness matter
skew = float((((C.R - Rb) / s) ** 3).mean())
assert f"{skew:.4f}" == "-0.3384" and "| Skewness | −0.3384 |" in (ROOT / "src" / "lm19.md").read_text(encoding="utf-8")
has("E9 mu^2 sentence", "Keeping the $\\mu^2$ term of (4.2), which (24.5) drops, gives $\\bar R/(s^2+\\bar R^2)=4.27$ at "
    "$c=1$: it explains only 0.01 of the gap")
has("E9 rest sentence", "The other 0.13 comes from the days' fat tails and negative skewness ([[LM19]])")
has("kelly note (M1)", "comes mostly from the days' fat tails and negative skewness; (4.2)'s $\\mu^2$ term adds 0.01 at "
    "full Kelly")
has("departures (M1)", "**Non-normal days.** Fat tails and a negative skewness make the quadratic rule overstate")
assert "fat tails' effect" not in RAW_MD and "The fat tails shave" not in RAW_MD
gb, gp = C.growth(c10 * fhat, pm10), C.growth(fhat, pm10)
chk("E9 Bayes growth (%)", 100 * gb, ".0f", "25")
chk("E9 plug-in share (%)", 100 * gp / gb, ".1f", "97.7")
chk("E9 plug-in share from printed (4.15)", 100 * (1 - (1 - 1 / 0.869) ** 2), ".1f", "97.7")
assert abs(gp / gb - (1 - (1 - 1 / c10) ** 2)) < 1e-12
anchor("A24-35", f"quadratic minus exact: c=1 {fhat:.5f} - {f_star:.5f} = {v(fhat - f_star, 2)}; c(10) {c10 * fhat:.5f} - "
       f"{kx10:.5f} = {v(c10 * fhat - kx10, 2)}; c=1/2 {0.5 * fhat:.5f} - {v(kxh, 2)} = {v(0.5 * fhat - kxh, 2)}; c=1/4 "
       f"{0.25 * fhat:.5f} - {kxq:.5f} = {v(0.25 * fhat - kxq, 2)}; 1 - c(10) {v(1 - c10, 2)}")
anchor("A24-36", f"A sigma0 = 10: c fhat {v(c10 * fhat, 2)}; exact (shifted) {v(kx10, 2)}; posterior-integrated "
       f"{v(kq10, 2)}; fhat* {v(f_star, 2, extra=4)} (lm17.md:239 prints 4.1381)")
anchor("A24-47", f"posterior SD of mu/sigma^2 {v(ksd, 2)}; 95% {v(c10 * fhat - C.Z975 * ksd, 1)} to "
       f"{v(c10 * fhat + C.Z975 * ksd, 1)}; at c = 1, 1/(s sqrt(T)) {v(1 / (s * sqrt(T)), 2)} (LM20's mean-only SE of fhat)")
anchor("A24-48", f"A sigma0 = 10: Bayes {v(gb, 0, pct=True)}, plug-in {v(gp, 0, pct=True)}, share {v(gp / gb, 3)} "
       f"(1-(1-1/c)^2 = {1 - (1 - 1 / c10) ** 2:.6f})")
# E10
gbh, gph = C.growth(0.5 * fhat, 0.5 * Rb), C.growth(fhat, 0.5 * Rb)
gbq, gpq = C.growth(0.25 * fhat, 0.25 * Rb), C.growth(fhat, 0.25 * Rb)
assert abs(gph) < 1e-12 and abs(gpq / gbq + 8) < 1e-9
has("E10 sigma0^2", "$(A\\sigma_0)^2=3.89^2/3$")
chk("E10 Bayes growth, half Kelly (%)", 100 * gbh, ".1f", "8.2")
chk("E10 c = 1/2 fraction", 0.5 * fhat, ".2f", "2.14")
chk("E10 plug-in growth, quarter Kelly (%)", 100 * gpq, ".1f", "-16.5")
chk("E10 Bayes growth, quarter Kelly (%)", 100 * gbq, ".2f", "2.06")
chk("E10 -8 x 2.06 from printed", -8 * 2.06, ".1f", "-16.5")
has("E10 ratio", "$1-(1-4)^2=-8$")
has("E10 worth", "a prior worth three times the sample, 71.3 years")
anchor("A24-49", f"c = 1/2: Bayes {v(gbh, 1, pct=True)}, plug-in {gph:.1e}; c = 1/4: Bayes {v(gbq, 2, pct=True)}, "
       f"plug-in {v(gpq, 1, pct=True)} (ratio {gpq / gbq:.6f}); Pr(mu>0) {v(pr_pos_q, 1, pct=True)} and "
       f"{v(pr_pos_h, 1, pct=True)}")
# X7 note
chk("X7 quarter-Kelly fraction", 0.25 * fhat, ".2f", "1.07")
has("X7 note values", "2.25 points (quarter Kelly, 1.07), 3.89 (half Kelly, 2.14; exact 2.11) and 10 (3.72; exact 3.62)")
# KC section 7: a prior centred at 8% a year
pm8, _ = C.post(0.5, 0.08)
fb8 = pm8 / s**2
chk("KC7 posterior mean", 100 * A * pm8, ".2f", "11.69")
chk("KC7 posterior mean from printed", 8 + 0.5 * (15.38 - 8), ".2f", "11.69")
chk("KC7 Bayes fraction", fb8, ".2f", "3.25")
chk("KC7 Bayes fraction from printed", 11.69 / 15.38 * 4.28, ".2f", "3.25")
chk("KC7 ratio to fhat", fb8 / fhat, ".2f", "0.76")
chk("KC7 c fhat", 0.5 * fhat, ".2f", "2.14")
anchor("A24-23", f"prior centred at 8% a year, A sigma0 = SE (c = 1/2): posterior mean {v(A * pm8, 2, pct=True)}; "
       f"Bayes fraction {v(fb8, 2)}; ratio to fhat {v(fb8 / fhat, 2)}; c fhat {v(0.5 * fhat, 2)}")
has("what breaks: T", "At $T=5,849$ this matters little")
has("what breaks: the prior of BDA3's section 3.3 (M2 a)",
    "Under the conjugate prior of Gelman et al. (2013, §3.3), whose prior SD of $\\mu$ is proportional to $\\sigma$")
has("M4: growth over tau years", "is therefore $(f\\mu-\\tfrac12f^2\\sigma^2)A\\tau$")

# ====================================================================== section 8: the code's comments and the KC
post_ = stats.beta(82 + 8, 82 + 4)
has("code comment", "# 0.5114, 0.1526")
assert (f"{float(post_.mean()):.4f}", f"{float(post_.sf(0.55)):.4f}") == ("0.5114", "0.1526")
_, _, b_d1, _ = C.js(C.XD[:C.H], ddof=1)
chk("KC8 1 - c_hat with ddof=1", b_d1, ".3f", "1.009")
chk("KC8 1 - c_hat with ddof=0", b_d, ".3f", "1.008")
has("KC8 factor", "$2,191/2,190$")
anchor("A24-24", f"common removed, 1 - c_hat with ddof=1 {v(b_d1, 3)} against ddof=0 {v(b_d, 3)} (factor 2191/2190)")
# the printed functions give the module's numbers
X_half = C.X[:C.H]
m_ = X_half.mean(axis=0)
noise_ = (X_half.var(axis=0, ddof=0) / C.H).mean()
assert max(0.0, 1 - (C.N - 3) * noise_ / ((m_ - m_.mean()) ** 2).sum()) == 0.0

# ====================================================================== practice problems
chk("P1 B", 7 / 16, ".4f", "0.4375")
chk("P1 A", 4 / 6, ".3f", "0.667")
chk("P1 C", 7 / 10, ".3f", "0.700")
assert Fraction(3, 10) + Fraction(6, 16) * (Fraction(4, 6) - Fraction(3, 10)) == Fraction(7, 16)
has("S1 route", r"0.3+\tfrac{6}{16}(\tfrac46-0.3)")
anchor("A24-50", f"Beta(3,7), 4 of 6: {Fraction(7, 16)} = {v(7 / 16, 4)}; data alone {v(4 / 6, 3)}; 7/10 {v(0.7, 3)}")
chk("P2 C", 36 / 52, ".2f", "0.69")
chk("P2 A", 6 / 10, ".2f", "0.60")
chk("P2 B", 16 / 52, ".2f", "0.31")
anchor("A24-51", f"prior SD 6, SE 4: c 36/52 = {v(36 / 52, 2)}; 6/10 {v(0.6, 2)}; 16/52 {v(16 / 52, 2)}")
chk("P3 A", 1 / sqrt(1 / 36 + 1 / 16), ".2f", "3.33")
chk("P3 A as sqrt(c) x 4", sqrt(36 / 52) * 4, ".2f", "3.33")
chk("P3 B", sqrt(52), ".2f", "7.21")
chk("P3 C", 6 * 4 / 10, ".2f", "2.40")
anchor("A24-52", f"posterior SD {v(1 / sqrt(1 / 36 + 1 / 16), 2)}; sqrt(52) {v(sqrt(52), 2)}; 6 x 4/10 {v(2.4, 2)}")
chk("P4 B", 1 - 7 / 18, ".3f", "0.611")
chk("P4 A", 1 - 8 / 18, ".3f", "0.556")
chk("P4 C", 7 / 18, ".3f", "0.389")
anchor("A24-53", f"N=10, sum 18: c_hat 1-7/18 {v(1 - 7 / 18, 3)}; N-2: {v(1 - 8 / 18, 3)}; 7/18 {v(7 / 18, 3)}")
chk("P5 A", 0.4 * 3, ".2f", "1.20")
chk("P5 B", sqrt(0.4) * 3, ".2f", "1.90")
chk("P5 C", 0.16 * 3, ".2f", "0.48")
anchor("A24-54", f"fhat 3.0, c 0.4: {v(0.4 * 3, 2)}; sqrt(c) {v(sqrt(0.4) * 3, 2)}; c^2 {v(0.16 * 3, 2)}")
assert 1 - (1 - 2) ** 2 == 0 and 1 - (1 - 0.5) ** 2 == 0.75
has("P6 options", "   - **A.** 75%\n   - **B.** 50%\n   - **C.** 0%")
anchor("A24-55", "c = 1/2: plug-in = 2 x Bayes, 1-(1-2)^2 = 0; distractors 1-(1-1/2)^2 = 0.75, 0.5")
# P7 (b) and P9: A sigma0 = 5 points
c5 = C.weight(0.05)
pm5, psd5 = C.post(c5)
chk("P7/P9 c", c5, ".3f", "0.623")
chk("P7/P9 c from printed 3.89", 25 / (25 + 3.89**2), ".3f", "0.623")
chk("P7 variance of the posterior mean", c5 * 25, ".1f", "15.6")
chk("P7 expected posterior variance", (1 - c5) * 25, ".1f", "9.4")
chk("P7 from printed c", 0.623 * 25, ".1f", "15.6")
chk("P7 from printed c (2)", 0.377 * 25, ".1f", "9.4")
has("P7 sum", "they sum to the prior's 25.0")
chk("P9 posterior mean", 100 * A * pm5, ".1f", "9.6")
chk("P9 posterior mean from printed", 0.623 * 15.38, ".1f", "9.6")
chk("P9 posterior SD", 100 * A * psd5, ".1f", "3.1")
chk("P9 posterior SD from printed", sqrt(0.623) * 3.89, ".1f", "3.1")
chk("P9 lower", 100 * A * (pm5 - C.Z975 * psd5), ".1f", "3.6")
chk("P9 upper", 100 * A * (pm5 + C.Z975 * psd5), ".1f", "15.6")
chk("P9 lower from printed", 0.623 * 15.38 - 1.96 * sqrt(0.623) * 3.89, ".1f", "3.6")
chk("P9 upper from printed", 0.623 * 15.38 + 1.96 * sqrt(0.623) * 3.89, ".1f", "15.6")
# m2: the two-decimal values the solution prints, and the interval a reader computes from them
chk("P9 posterior mean, two decimals from printed 0.623 x 15.38", 0.623 * 15.38, ".2f", "9.58")
chk("P9 posterior SD, two decimals from printed", sqrt(0.623) * 3.89, ".2f", "3.07")
chk("P9 posterior SD, two decimals", 100 * A * psd5, ".2f", "3.07")
chk("P9 lower from printed 9.58, 3.07", 9.58 - 1.96 * 3.07, ".1f", "3.6")
chk("P9 upper from printed 9.58, 3.07", 9.58 + 1.96 * 3.07, ".1f", "15.6")
assert format(9.6 - 1.96 * 3.1, ".1f") == "3.5"   # why the solution prints the two-decimal values (m2)
has("P9 two-decimal values", "=9.58%$, or 9.6% to one decimal, and the SD is $\\sqrt{0.623}\\times3.89=3.07$ points, or "
    "3.1. From these two-decimal values, the 95% credible interval runs from 3.6% to 15.6%")
p5_ = float(stats.norm.cdf(-pm5 / psd5))
chk("P9 Pr(mu<=0)", p5_, ".4f", "0.0009")
chk("P9 Pr(mu<=0) from printed", float(stats.norm.cdf(-0.623 * 15.38 / (sqrt(0.623) * 3.89))), ".4f", "0.0009")
chk("P9 fraction", c5 * fhat, ".2f", "2.67")
chk("P9 fraction from printed", 0.623 * 4.28, ".2f", "2.67")
chk("P9 worth", (vol / 0.05) ** 2, ".1f", "14.4")
chk("P9 worth from printed", (18.96 / 5) ** 2, ".1f", "14.4")
anchor("A24-56", f"A sigma0 = 5: c {v(c5, 3)} (from printed 3.89: {25 / (25 + 3.89**2):.5f}); mean {v(A * pm5, 1, pct=True)}; "
       f"SD {v(A * psd5, 1, pct=True)}; 95% {v(A * (pm5 - C.Z975 * psd5), 1, pct=True)} to "
       f"{v(A * (pm5 + C.Z975 * psd5), 1, pct=True)}; Pr(mu<=0) {sig(p5_, 1)}; "
       f"fraction {v(c5 * fhat, 2)}; worth {v((vol / 0.05) ** 2, 1)} years (from printed (18.96/5)^2 = {(18.96 / 5) ** 2:.3f})")
# P10: Experiment 2
e2 = C.experiment2()
res = []
ses = []
for spread, (r_p, j_p, p_p) in zip((0.0, 1.0, 3.0), (("28.0", "3.0", "2.1"), ("28.0", "15.5", "15.5"),
                                                     ("28.0", "25.5", "25.5"))):
    d = e2[spread]
    for k, p in (("raw", r_p), ("js", j_p), ("pp", p_p)):
        m, se_ = C.mc_mean_se(d[k])
        chk(f"P10 spread {spread:g} {k}", m, ".1f", p)
        ses.append(se_)
    res.append(f"spread {spread:g}: raw {mcs(d['raw'])}, JS {mcs(d['js'])}, positive part {mcs(d['pp'])}")
chk("P10 smallest SE", min(ses), ".2f", "0.02")
chk("P10 largest SE", max(ses), ".2f", "0.05")
has("P10 SE range", "standard errors from 0.02 to 0.05")
has("P10 theory", "theory gives 3, 15.5 and 25.5")
anchor("A24-57", "Experiment 2, 20,000 each: " + "; ".join(res))
# P11: the TAIEX price index removed
nz_e, sp_e, b_e, c_e = C.js(C.XE[:C.H])
assert abs(sp_e - sp1) < 1e-12 and c_e == 0.0
me1, me2 = C.XE[:C.H].mean(axis=0), C.XE[C.H:].mean(axis=0)
miss_e, miss_e_dev = C.oos(me1, me2, 0), C.oos(me1, me2, 0, True)
chk("P11 noise", 100 * nz_e, ".1f", "5.0")
chk("P11 1 - c_hat", b_e, ".2f", "1.10")
chk("P11 miss of the grand mean", 100 * miss_e, ".1f", "12.1")
chk("P11 deviations' miss", 100 * miss_e_dev, ".1f", "8.5")
chk("P11 deviations' miss, two decimals (K2)", 100 * miss_e_dev, ".2f", "8.49")
assert abs(miss_e_dev - C.oos(C.M1, C.M2, 0, True)) < 1e-12           # the same deviations as in E7
has("P11 stem (K2)", "while the miss of the deviations from each half's grand mean stays 8.5?")
has("P11 solution (K2)", "the deviations from each half's grand mean, and their miss of 8.49, do not change")
chk("P11 average excess, first half", 100 * C.A28 * float(me1.mean()), ".1f", "-0.3")
chk("P11 average excess, second half", 100 * C.A28 * float(me2.mean()), ".1f", "-9.0")
chk("P11 TAIEX, first half", 100 * C.A28 * float(C.TX[:C.H].mean()), ".1f", "10.8")
chk("P11 TAIEX, second half", 100 * C.A28 * float(C.TX[C.H:].mean()), ".1f", "19.1")
anchor("A24-58", f"TAIEX removed: noise {v(nz_e, 1, pct=True)}; 1 - c_hat {v(b_e, 1)}; c_hat {c_e:g}; RMSE c=0 "
       f"{v(miss_e, 1, pct=True)} (deviations {v(miss_e_dev, 1, pct=True)}); average excess "
       f"{v(C.A28 * float(me1.mean()), 1, pct=True)} -> {v(C.A28 * float(me2.mean()), 1, 0, pct=True)}; TAIEX "
       f"{v(C.A28 * float(C.TX[:C.H].mean()), 1, pct=True)} -> {v(C.A28 * float(C.TX[C.H:].mean()), 1, pct=True)}")
# P12
pr1624 = C.beta_sf(98, 90, C.P55)
chk("P12 mean", 98 / 188, ".3f", "0.521")
chk("P12 Pr(theta>=0.55)", 100 * float(pr1624), ".1f", "21.6")
chk("P12 record frequency", 16 / 24, ".3f", "0.667")
chk("LM13's 18.02% (lm13.md:530)", 100 * (0.1 / 0.9 * 1.9780) / (1 + 0.1 / 0.9 * 1.9780), ".2f", "18.02")
anchor("A24-59", f"16 of 24, Beta(98,90): mean {98 / 188:.5f}; Pr(theta>=0.55) {v(float(pr1624), 1, pct=True)} exact; "
       f"LM13 18.02% (lm13.md:530)")
thirds = [len(a) for a in np.array_split(np.arange(C.T28), 3)]
anchor("A24-60", f"thirds of {C.T28}: {thirds} -> sorted {sorted(thirds)}")
# N-3: the lab's thirds (np.array_split of U28's 4,382 returns): each third's means against the next third's
parts = np.array_split(C.X, 3)
assert [len(p) for p in parts] == [1461, 1461, 1460]                  # the lengths the lab's extension prints
for k, (rho_p, slope_p) in enumerate((("0.13", "0.09"), ("0.24", "0.61"))):
    mk, mn = parts[k].mean(axis=0), parts[k + 1].mean(axis=0)
    chk(f"thirds {k + 1} -> {k + 2}: correlation of the means", float(np.corrcoef(mk, mn)[0, 1]), ".2f", rho_p)
    chk(f"thirds {k + 1} -> {k + 2}: hindsight slope", C.c_opt(mk, mn), ".2f", slope_p)
has("N-3 thirds", "The reverse direction and the lab's thirds show how much the misses move; in the thirds the correlation "
    "is 0.13 and 0.24, and the hindsight slope 0.09 and 0.61.")
has("N-3 paragraph", "\n\nThe misses, the hindsight slope and the case's correlation come from one fixed split")
anchor("A24-37", f"inputs A Rbar {A * Rb:.8f}; sqrt(A) s {vol:.8f}; years {years:.6f}; fhat {fhat:.6f}; initial readouts "
       f"at A sigma0 0.10: years {v(years, 2)}; SE {v(A * se, 2, pct=True)}; c {v(c10, 3)}; mean "
       f"{v(A * pm10, 1, pct=True)}; SD {v(A * psd10, 1, pct=True)}; 95% {v(A * (pm10 - C.Z975 * psd10), 1, pct=True)} to "
       f"{v(A * (pm10 + C.Z975 * psd10), 1, pct=True)}; fraction {v(c10 * fhat, 2)}")

# ====================================================================== front matter (overview) and summary
has("overview: 10.0% to 15.3%", "from 10.0% to 15.3%")
has("overview: c and posterior", "get $c=0.869$, and the posterior mean is 13.4% a year against the sample's 15.38%")
has("overview: flat", "7.8% to 23.0% a year")
has("overview: E6", "it cuts the total squared error from 28.1 to 15.5; the Bayes rule that knows the prior reaches 14.0")
has("overview: case", "9.8 against 8.5 points a year")
has("overview: sceptics", "prior standard deviation is 2.25 or 3.89 points a year")
has("overview: gaps", "by 0.14 at full Kelly and by 0.10 at $c=0.869$, while the prior shaves 13%")
has("overview: 8%", "centred at 8% a year, the Bayes bet is 0.76 of the plug-in, not $c=0.50$")

# ====================================================================== structure: labels and citations
ex_labels = re.findall(r"\[!exhibit\][^\n]*\{#([\w-]+)\}", RAW_MD)
eg_labels = re.findall(r"\[!example\][^\n]*\{#([\w-]+)\}", RAW_MD)
assert len(ex_labels) == 7 and len(eg_labels) == 10, (ex_labels, eg_labels)
for lab in ex_labels:
    assert f"[[ex:{lab}]]" in RAW_MD, f"exhibit {lab} is never cited"
for kind, lab in re.findall(r"\[\[(ex|eg):([\w-]+)\]\]", RAW_MD):
    assert lab in (ex_labels if kind == "ex" else eg_labels), (kind, lab)
tags = re.findall(r"\\tag\{(24\.\d+)\}", RAW_MD)
assert tags == ["24.1", "24.2", "24.3", "24.4", "24.5"], tags
assert "\t" not in RAW_MD and "\b" not in RAW_MD and "\f" not in RAW_MD
print(f"labels: {len(ex_labels)} exhibits, {len(eg_labels)} examples, every exhibit cited; tags {', '.join(tags)}")
# XB10: the English at the first use of each Chinese term in each box (the boxes in order)
zh_boxes = re.findall(r"> \[!zh\][^\n]*\n((?:>[^\n]*\n?)+)", RAW_MD)
assert len(zh_boxes) == 5, len(zh_boxes)
GLOSSES = [["參數（parameter）", "分布（distribution）", "二項資料（binomial data）", "事後平均數（posterior mean）",
            "加權平均（weighted average）", "資料權重（data's weight）", "懷疑性事前分布（sceptical prior）"],
           ["變異數（variance）", "平均數（mean）", "常態分布（normal distribution）", "標準差（standard deviation）",
            "事後平均數（posterior mean）", "加權平均（weighted average）", "資料權重（data's weight）"],
           ["機率（probability）", "可靠區間（credible interval）", "信賴區間（confidence interval）",
            "重複抽樣（repeated sampling）", "平均報酬（mean return）"],
           ["估計值（estimate）", "平均報酬（mean return）", "誤差（error）", "彼此相關（correlated）",
            "共同成分（common component）", "離差（deviation）", "橫斷面平均（cross-sectional mean）"],
           ["波動率（volatility）", "期望對數成長（expected log growth）", "貝氏下注（Bayes bet）",
            "事前標準差（prior standard deviation）", "估計值（estimate）", "資料權重（data's weight）"]]
for k, (box, glosses) in enumerate(zip(zh_boxes, GLOSSES)):
    for g in glosses:
        term = g.split("（")[0]
        assert term in box and box.index(term) == box.index(g), (k + 1, g)   # the first use carries the English
# XB11: 樂詞網's 懷疑性事前分布 at the box's one use of the prior; 懷疑者的事前標準差 and the title stay
assert "懷疑者的事前分布" not in RAW_MD and RAW_MD.count("懷疑性事前分布") == 1
print(f"XB10, XB11: {sum(map(len, GLOSSES))} first-use glosses checked in the {len(zh_boxes)} boxes")

# ====================================================================== report
body = TEXT.split("\n## Glossary", 1)[0]
nums = set(re.findall(r"(?<![\w.])\d+\.\d+|(?<![\w.,])\d{1,3}(?:,\d{3})+", body))
left = sorted(n for n in nums if n not in COVERED)
print(f"\nnumbers with a decimal point or thousands separator not covered by a check ({len(left)}):")
print("   " + " ".join(left))
print(f"\nvalues within a tenth of a printed unit of a rounding boundary ({len(NEAR)}):")
for x in NEAR:
    print("   ", x)
print(f"\nanchor differences ({len(ANCHOR_DIFFS)}):")
for x in ANCHOR_DIFFS:
    print("   ", x)
print(f"\nall {N_CHECKS} checks passed")
