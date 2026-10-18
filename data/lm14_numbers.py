"""Every number that LM14 (Random Variables, Expectation and Jensen's Inequality) quotes, computed and checked.

Run:  uv run python data/lm14_numbers.py     (after data/vol3_series.py and data/lm14_charts.py)

Inputs: data/processed/vol3_taiex.parquet (TR23, through data/lm14_common.py), the closes of the same file for the
exact-fraction recount, src/lm14.md (the text the checks compare against), the chart specs src/data/lm14-*.json,
src/lm01.md, src/lm04.md and src/lm05.md (values LM14 quotes from them), and plans/vol-3-anchors.md (the LM14 anchor
rows, compared and reported, never forced).

Sample TR23: T = 5,849 simple daily returns of the TAIEX total-return index, 2003-01-03 .. 2026-10-08. The empirical
law puts mass 1/T on each return, so every moment divides by T; years = calendar days / 365.25; A = T / years.
Calendar years 2003-2025, 2003 from its first close (2003-01-02); 2026 is partial and left out. Counts use the guard
(<= c + 1e-12, >= c - 1e-12), and the -3% count is recounted with exact fractions of the two-decimal closes. Quantiles
of the empirical law are order statistics R_(ceil(uT)), numpy's method="inverted_cdf". No simulation (no seed).

Checks: chk(label, value, fmt, printed) asserts that format(value, fmt) equals the printed string, that the value is
not a rounding tie of that format (a reader rounding by hand could go either way), and that the string appears in
src/lm14.md (after replacing the Unicode minus by '-' and '{,}' by ','). Figures that a reader recomputes from printed
inputs are checked from those inputs too (project/PITFALLS.md section 7). has(label, s) asserts that a string appears.
anchor(id, piece) reports whether the anchor row's value contains the script's value; differences are listed at the
end, not forced.
"""
import json
import math
import re
from fractions import Fraction
from itertools import pairwise
from math import ceil

import numpy as np
from lm14_common import (
    EPS,
    LIMIT_CHANGE,
    PRESETS,
    ROOT,
    law,
    load,
    two_point,
    year_points,
)
from scipy import stats

TEXT = (ROOT / "src" / "lm14.md").read_text(encoding="utf-8")
NORM = TEXT.replace("{,}", ",").replace("−", "-")
LM01 = (ROOT / "src" / "lm01.md").read_text(encoding="utf-8")
LM04 = (ROOT / "src" / "lm04.md").read_text(encoding="utf-8")
LM05 = (ROOT / "src" / "lm05.md").read_text(encoding="utf-8")
N_CHECKS = 0
DIFFS: list[str] = []


def in_text(printed: str) -> bool:
    """The printed number appears as a whole number (2.323 is not found in 2.3235)."""
    return re.search(r"(?<![\d.])" + re.escape(printed) + r"(?!\d)", NORM) is not None


def tie(value: float, fmt: str) -> bool:
    """True when value lies on a rounding boundary of fmt."""
    m = re.search(r"\.(\d+)f", fmt)
    if not m:
        return False
    scaled = abs(value) * 10 ** int(m.group(1))
    return abs(scaled - math.floor(scaled) - 0.5) < 1e-6


def chk(label: str, value: float, fmt: str, printed: str) -> None:
    global N_CHECKS
    got = format(value, fmt).replace("−", "-")
    ok = got == printed and in_text(printed)
    print(f"CHECK {label}: {got} (printed {printed}) {'ok' if ok else 'MISMATCH'}")
    assert got == printed, (label, got, printed)
    assert not tie(value, fmt), ("rounding tie: print more digits", label, value)
    assert in_text(printed), f"{label}: {printed!r} not found in src/lm14.md"
    N_CHECKS += 1


def has(label: str, printed: str) -> None:
    global N_CHECKS
    assert printed in NORM, f"{label}: {printed!r} not found in src/lm14.md"
    print(f"CHECK {label}: '{printed}' in text ok")
    N_CHECKS += 1


def truth(label: str, cond: bool) -> None:
    global N_CHECKS
    print(f"CHECK {label}: {'ok' if cond else 'FALSE'}")
    assert cond, label
    N_CHECKS += 1


def sci(v: float, d: int) -> str:
    """LaTeX scientific form with d decimals, as printed: 1.464\\times10^{-4}."""
    m, e = f"{v:.{d}e}".split("e")
    return f"{m}\\times10^{{{int(e)}}}"


def g10(x: float) -> str:
    return f"{float(x):.10g}"


ANCHORS: dict[str, str] = {}
for line in (ROOT / "plans" / "vol-3-anchors.md").read_text(encoding="utf-8").splitlines():
    if line.startswith("| A14-"):
        cells = [c.strip() for c in line.split("|")]
        ANCHORS[cells[1]] = cells[4]


def anchor(aid: str, piece: str) -> None:
    """Compare with plans/vol-3-anchors.md: the anchor's value must contain piece; a difference is reported."""
    val = ANCHORS.get(aid, "")
    tag = "ok" if piece in val else "DIFFERS"
    print(f"ANCHOR {aid}: {piece} {tag}")
    if tag != "ok":
        DIFFS.append(f"{aid}: script {piece}; anchor {val}")


# ====================================================================== sample (notation, case)
d = load()
R, T = d.R, d.T
r = np.log1p(R)
Rbar, rbar = float(R.mean()), float(r.mean())
s, s_r = float(R.std()), float(r.std())
RG = float(np.expm1(rbar))
z = (R - Rbar) / s
print(f"sample: T = {T}, {d.rdates[0]} .. {d.rdates[-1]}, {d.days} calendar days, years {d.years:.6f}, A {d.A:.4f}")
assert T == 5849 and str(d.rdates[0]) == "2003-01-03" and str(d.rdates[-1]) == "2026-10-08" and str(d.dates[0]) == "2003-01-02"
anchor("A14-01", "5849; first return 2003-01-03; last 2026-10-08")
anchor("A14-02", f"{d.days} calendar days; {g10(d.years)}")
anchor("A14-03", g10(d.A))
has("T", "T=5,849")
has("first return", "3 January 2003")
has("last return", "8 October 2026")
has("first close", "2 January 2003")
truth("the years run from the first close, 2 January 2003 (8,680 days), not from the first return",
      d.days == 8680 and (d.rdates[-1] - d.dates[0]).days == 8680 and (d.rdates[-1] - d.rdates[0]).days == 8679)
has("span of the closes", "the closes from 2 January 2003 span 23.7645 years")
chk("years", d.years, ".4f", "23.7645")
chk("A", d.A, ".2f", "246.12")

# ---- calendar years
ny = d.year_R.size
ann = law(d.year_R, np.full(ny, 1 / ny))
cagr = float(np.prod(1 + d.year_R) ** (1 / ny) - 1)
r08, r09 = (float(d.year_R[d.year_ids.index(y)]) for y in (2008, 2009))
assert d.year_ids[0] == 2003 and d.year_ids[-1] == 2025
chk("number of calendar years", ny, "d", "23")
has("years 2003-2025", "2003–2025".replace("−", "-"))
chk("arithmetic mean of the years %", ann["mu"] * 100, ".2f", "14.97")
chk("compound rate of the years %", cagr * 100, ".2f", "12.35")
chk("2008 %", r08 * 100, ".2f", "-43.07")
chk("2009 %", r09 * 100, ".2f", "83.34")
chk("average of 2008, 2009 from printed %", (-43.07 + 83.34) / 2, ".1f", "20.1")
chk("average of 2008, 2009 unrounded %", (r08 + r09) / 2 * 100, ".1f", "20.1")
chk("two years together from printed %", (0.5693 * 1.8334 - 1) * 100, ".1f", "4.4")
chk("two years together unrounded %", ((1 + r08) * (1 + r09) - 1) * 100, ".1f", "4.4")
anchor("A14-04", f"{g10(ann['mu'] * 100)}%")
anchor("A14-05", f"{g10(cagr * 100)}%")
anchor("A14-06", f"2008 {g10(r08 * 100)}%; 2009 {g10(r09 * 100)}%")

# ---- daily case
chk("Rbar %", Rbar * 100, ".4f", "0.0625")
chk("R_G daily %", RG * 100, ".4f", "0.0552")
chk("drag Rbar - R_G bp", (Rbar - RG) * 1e4, ".4f", "0.7320")
chk("s^2/2 bp", s**2 / 2 * 1e4, ".4f", "0.7301")
truth("drag within 0.002 bp of s^2/2", 0 < (Rbar - RG - s**2 / 2) * 1e4 < 0.002)
has("within 0.002 bp", "within 0.002 bp")
chk("Rbar to six decimals of a percent", Rbar * 100, ".6f", "0.062505")
chk("R_G to six decimals", RG * 100, ".6f", "0.055185")
chk("s to six decimals", s * 100, ".6f", "1.208364")
chk("gap from four-decimal rates bp", (0.0625 - 0.0552) * 100, ".2f", "0.73")
has("retrieval date", "retrieved 18 October 2026")
anchor("A14-09", f"{g10(Rbar * 100)}%")
anchor("A14-10", f"{g10(RG * 100)}%; r_bar {g10(rbar * 100)}%")
anchor("A14-11", f"{g10((Rbar - RG) * 1e4)} bp")
anchor("A14-13", f"{g10(s**2 / 2 * 1e4)} bp")
anchor("A14-14", f"{g10(s * 100)}%")

# ---- case chart (X1)
case = json.loads((ROOT / "src" / "data" / "lm14-case.json").read_text(encoding="utf-8"))
truth("X1 has 23 bars 2003..2025", case["categories"] == [str(y) for y in range(2003, 2026)])
truth("X1 bars are the yearly returns", np.allclose(case["series"][0]["values"], d.year_R, atol=1e-8))
truth("X1 hlines at the mean and the compound rate",
      abs(case["ann"][0]["y"] - ann["mu"]) < 1e-8 and abs(case["ann"][1]["y"] - cagr) < 1e-8)

# ====================================================================== Section 2
# ---- E1 / X2: LM13's two trades at f = 25
f_star = 0.5 / 0.01 - 0.5 / 0.02
truth("Kelly exposure of the +2%/-1% bet is 25", f_star == 25 and 1 + 25 * 0.02 == 1.5 and 1 - 25 * 0.01 == 0.75)
has("f=25", "f=25")
outcomes = {"++": 1.5 * 1.5, "+-": 1.5 * 0.75, "-+": 0.75 * 1.5, "--": 0.75 * 0.75}
values = sorted(set(outcomes.values()))
pmf = {v: Fraction(sum(1 for w in outcomes.values() if w == v), 4) for v in values}
truth("X values and pmf", values == [0.5625, 1.125, 2.25] and list(pmf.values()) == [Fraction(1, 4), Fraction(1, 2), Fraction(1, 4)])
cdf = {v: sum(pmf[u] for u in values if u <= v) for v in values}
truth("F_X jumps from 1/4 to 3/4 at 1.125", cdf[0.5625] == Fraction(1, 4) and cdf[1.125] == Fraction(3, 4) and cdf[2.25] == 1)


def medians(vals: list[float], probs: list[Fraction]) -> list[float]:
    """Values among the support that are medians: Pr(X <= x) >= 1/2 and Pr(X >= x) >= 1/2."""
    return [x for x in vals if sum(p for v, p in zip(vals, probs, strict=True) if v <= x) >= Fraction(1, 2)
            and sum(p for v, p in zip(vals, probs, strict=True) if v >= x) >= Fraction(1, 2)]


truth("the only median is 1.125", medians(values, list(pmf.values())) == [1.125])
truth("F_X^-1(0.1) = 0.5625", min(v for v in values if cdf[v] >= Fraction(1, 10)) == 0.5625)
has("10% quantile", "is 0.5625")
for w, v in outcomes.items():
    chk(f"X2 half log at {w} %", 0.5 * math.log(v) * 100, ".4f", {"++": "40.5465", "+-": "5.8892", "-+": "5.8892", "--": "-28.7682"}[w])
anchor("A14-22", "0.5625: 0.25, 1.125: 0.5, 2.25: 0.25; F_X 0.25, 0.75, 1")
anchor("A14-36", "F^-1(0.1) 0.5625; median 1.125")

# ---- E2, X3: the empirical law of TR23
n_le0 = int((R <= 0 + EPS).sum())
n_pos = int((R > 0).sum())
n_zero = int((R == 0).sum())
truth("no zero returns and all returns distinct", n_zero == 0 and np.unique(R).size == T)
has("F(0) as a count", "2,644/5,849=0.4520")
chk("F(0)", n_le0 / T, ".4f", "0.4520")
chk("days that rose", n_pos, ",d", "3,205")
chk("share that rose %", n_pos / T * 100, ".1f", "54.8")
Rs = np.sort(R)
chk("median order", (T + 1) // 2, ",d", "2,925")
chk("median %", Rs[(T + 1) // 2 - 1] * 100, ".4f", "0.0879")
truth("np.median equals the 2,925th return", float(np.median(R)) == Rs[(T + 1) // 2 - 1])
n_above = int((R > Rbar).sum())
chk("days above the mean", n_above, ",d", "3,020")
chk("share above the mean %", n_above / T * 100, ".1f", "51.6")
anchor("A14-37", f"{n_le0}/{T} = {g10(n_le0 / T)}")
anchor("A14-38", f"{n_pos}; {g10(n_pos / T * 100)}%")
anchor("A14-39", f"{g10(Rs[(T + 1) // 2 - 1] * 100)}%")
anchor("A14-40", f"{n_above}; {g10(n_above / T * 100)}%")
for u in (0.001, 0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99, 0.999):
    j = ceil(u * T - 1e-9)
    inv = float(np.quantile(R, u, method="inverted_cdf"))
    lin = float(np.quantile(R, u))
    assert inv == Rs[j - 1]
    for v in (inv, lin):
        assert not tie(v * 100, ".3f"), (u, v)
    has(f"X3 row u={u}", f"| {u} | {j:,} | {inv * 100:.3f} | {lin * 100:.3f} |")
    if u in (0.25, 0.5, 0.75):
        truth(f"X3 columns agree at u={u}, (T-1)u whole", inv == lin and ((T - 1) * u).is_integer())
    else:
        truth(f"X3 columns differ at u={u}, (T-1)u not whole", inv != lin and not ((T - 1) * u).is_integer())
    truth(f"X3 printed columns agree at u={u} only at the quartiles, the median and 0.01",
          (f"{inv * 100:.3f}" == f"{lin * 100:.3f}") == (u in (0.01, 0.25, 0.5, 0.75)))
    if u == 0.01:
        truth("X3 at u=0.01: the columns differ in the fourth decimal", f"{inv * 100:.4f}" != f"{lin * 100:.4f}")
has("X3 note", "Elsewhere they differ, at $u=0.01$ only in the fourth decimal")
chk("F^-1(0.01) %", float(np.quantile(R, 0.01, method="inverted_cdf")) * 100, ".3f", "-3.567")
chk("F^-1(0.99) %", float(np.quantile(R, 0.99, method="inverted_cdf")) * 100, ".3f", "3.125")
chk("F^-1(0.001) %", float(np.quantile(R, 0.001, method="inverted_cdf")) * 100, ".3f", "-6.313")
chk("F^-1(0.999) %", float(np.quantile(R, 0.999, method="inverted_cdf")) * 100, ".3f", "5.823")
chk("default quantile at 0.001 %", float(np.quantile(R, 0.001)) * 100, ".3f", "-5.866")
anchor("A14-21", f"u=0.001: j=6 {g10(float(np.quantile(R, 0.001, method='inverted_cdf')) * 100)}% / linear "
       f"{g10(float(np.quantile(R, 0.001)) * 100)}%")

# ---- KC: the die; the coin of the pitfall
die = stats.rv_discrete(values=(np.arange(1, 7), np.full(6, 1 / 6)))
die_vals = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
truth("die: medians among the faces are 3 and 4", medians(die_vals, [Fraction(1, 6)] * 6) == [3.0, 4.0])
truth("die: every x in (3, 4) is a median", all(
    sum(Fraction(1, 6) for v in die_vals if v <= x) >= Fraction(1, 2) and sum(Fraction(1, 6) for v in die_vals if v >= x) >= Fraction(1, 2)
    for x in (3.25, 3.5, 3.75)))
truth("die: rv_discrete median and ppf(0.5) are 3, np.median is 3.5",
      float(die.median()) == 3 and float(die.ppf(0.5)) == 3 and float(np.median(np.arange(1, 7))) == 3.5)
has("die medians", "Every $x$ in $[3,4]$ is a median")
has("die np.median", "returns the midpoint 3.5")
coin = stats.rv_discrete(values=([0, 1], [0.5, 0.5]))
truth("coin: medians fill [0, 1], np.median 0.5, rv_discrete 0",
      medians([0.0, 1.0], [Fraction(1, 2)] * 2) == [0.0, 1.0] and float(coin.median()) == 0 and float(np.median([0, 1])) == 0.5)
anchor("A14-15", "medians [3, 4]; np.median 3.5; rv_discrete median 3")

# ====================================================================== Section 3
# ---- E3
EX = sum(float(p) * v for v, p in pmf.items())
truth("E[X] over outcomes and over values is 1.265625 = 1.125^2",
      sum(outcomes.values()) / 4 == EX == 1.265625 == 1.125**2 and 1 + 25 * 0.005 == 1.125)
has("E[X]", "=1.265625")
chk("LOTUS from printed half logs %", 0.25 * 40.5465 + 0.5 * 5.8892 + 0.25 * -28.7682, ".3f", "5.889")
e_half = sum(float(p) * 0.5 * math.log(v) for v, p in pmf.items())
chk("E[half ln X] %", e_half * 100, ".3f", "5.889")
truth("E[half ln X] = half ln 1.125 = LM4's g*", abs(e_half - 0.5 * math.log(1.125)) < 1e-15
      and abs(e_half - (0.5 * math.log(1.5) + 0.5 * math.log(0.75))) < 1e-15 and "5.889\\%" in LM04)
chk("half ln E[X] %", 0.5 * math.log(EX) * 100, ".3f", "11.778")
truth("log of the average is twice the average of the logs", abs(0.5 * math.log(EX) - 2 * e_half) < 1e-15)
has("a factor of two", "shows a factor of two")
anchor("A14-34", f"{g10(e_half * 100)}%")
anchor("A14-35", f"0.5 ln E X {g10(0.5 * math.log(EX) * 100)}%")
anchor("A14-41", "1.265625; 1.125^2 = 1.265625")

# ---- E4
chk("r_bar bp", rbar * 1e4, ".4f", "5.5170")
chk("A r_bar %", d.A * rbar * 100, ".2f", "13.58")
chk("A r_bar from printed %", 246.12 * 5.5170e-4 * 100, ".2f", "13.58")
G = float(d.tr[-1] / d.tr[0])
chk("G over the sample", G, ".4f", "25.2007")
chk("ln G / years from printed %", math.log(25.2007) / 23.7645 * 100, ".2f", "13.58")
truth("A r_bar = ln G / years (1.12)", abs(d.A * rbar - math.log(G) / d.years) < 1e-12)
chk("compound rate over the sample %", (G ** (1 / d.years) - 1) * 100, ".2f", "14.54")
chk("compound rate from printed %", (25.2007 ** (1 / 23.7645) - 1) * 100, ".2f", "14.54")
anchor("A14-43", f"{g10(rbar * 1e4)} bp")
anchor("A14-44", f"A r_bar {g10(d.A * rbar * 100)}%")
anchor("A14-45", g10(G))

# ---- pitfall and KC
J = float(np.log1p(Rbar)) - rbar
chk("ln(1 + Rbar) - r_bar bp", J * 1e4, ".4f", "0.7316")
chk("KC +-10% day %", (0.5 * math.log(1.1) + 0.5 * math.log(0.9)) * 100, ".4f", "-0.5025")
truth("KC: half ln 0.99", abs(0.5 * math.log(1.1) + 0.5 * math.log(0.9) - 0.5 * math.log(0.99)) < 1e-15)
anchor("A14-16", f"{g10((0.5 * math.log(1.1) + 0.5 * math.log(0.9)) * 100)}%")

# ====================================================================== Section 4
# ---- E5: the +2%/-1% bet, exact
bet_v = [Fraction(2, 100), Fraction(-1, 100)]
mu_b = sum(bet_v) / 2
var_b = sum((v - mu_b) ** 2 for v in bet_v) / 2
m2_b = sum(v * v for v in bet_v) / 2
m3_b = sum(v**3 for v in bet_v) / 2
truth("E5: mu 0.5%, sigma 1.5%, E R^2 0.00025, E R^3 3.5e-6",
      mu_b == Fraction(5, 1000) and var_b == Fraction(15, 1000) ** 2 and m2_b == Fraction(25, 100000) == var_b + mu_b**2
      and m3_b == Fraction(35, 10**7) == mu_b**3 + 3 * mu_b * var_b)
truth("E5: skewness 0, kurtosis 1", sum((v - mu_b) ** 3 for v in bet_v) == 0
      and sum((v - mu_b) ** 4 for v in bet_v) / 2 / var_b**2 == 1)
has("E5 values", "=0.00025=")
has("E5 third moment", "=3.5\\times10^{-6}")
truth("LM4 prints the bet's third moment (Practice Problem 13)", "3.5\\times10^{-6}" in LM04)
anchor("A14-46", "mu 0.005; sigma 0.015; E R^2 0.00025; E R^3 3.5e-06; mu^3+3mu sigma^2 3.5e-06; Skew 0; Kurt 1")

# ---- normal moments
truth("E[Z^4] = 3, Var(Z^2) = 2, E[Z^6] = 15", stats.norm.moment(4) == 3 and stats.norm.moment(4) - 1 == 2
      and abs(stats.norm.moment(6) - 15) < 1e-12)

# ---- E6, X4: TR23 against N(Rbar, s^2)
m2, m3, m4 = float((R**2).mean()), float((R**3).mean()), float((R**4).mean())
skew, exk = float(stats.skew(R)), float(stats.kurtosis(R))
chk("skewness (2 decimals)", skew, ".2f", "-0.34")
chk("skewness (3 decimals, X4)", skew, ".3f", "-0.338")
chk("kurtosis", exk + 3, ".2f", "8.27")
chk("excess kurtosis", exk, ".2f", "5.27")
truth("scipy skew and kurtosis use divisor T", abs(skew - float(((R - Rbar) ** 3).mean()) / s**3) < 1e-12
      and abs(exk + 3 - float(((R - Rbar) ** 4).mean()) / s**4) < 1e-10)
R6, s6 = 0.00062505, 0.01208364
n3 = Rbar**3 + 3 * Rbar * s**2
n4 = Rbar**4 + 6 * Rbar**2 * s**2 + 3 * s**4
n3p = R6**3 + 3 * R6 * s6**2
n4p = R6**4 + 6 * R6**2 * s6**2 + 3 * s6**4
has("E[R^2]", sci(m2, 3))
has("s^2", sci(s**2, 3))
has("Rbar^2", sci(Rbar**2, 3))
truth("(3.7) adds up at four figures", f"{1.460e-4 + 3.907e-7:.3e}" == "1.464e-04" and f"{1.4601e-4 + 3.9069e-7:.4e}" != f"{m2:.4e}")
has("E[R^3]", sci(m3, 3))
has("normal E[X^3]", sci(n3, 3))
truth("normal E[X^3] from the six-decimal inputs prints the same", sci(n3p, 3) == sci(n3, 3))
has("E[R^4]", sci(m4, 3))
has("normal E[X^4]", sci(n4p, 3))
truth("normal E[X^4] unrounded prints the same; four-decimal inputs would not",
      sci(n4, 3) == sci(n4p, 3) and sci(0.000625**4 + 6 * 0.000625**2 * 0.012084**2 + 3 * 0.012084**4, 3) != sci(n4, 3))
chk("ratio of fourth moments", m4 / n4, ".2f", "2.72")
chk("ratio from printed moments", 1.751e-7 / 6.430e-8, ".2f", "2.72")
has("X4 row E[R^3]", f"| $\\E[R^3]$ | ${sci(m3, 3)}$ | ${sci(n3, 3)}$ |")
has("X4 row E[R^4]", f"| $\\E[R^4]$ | ${sci(m4, 3)}$ | ${sci(n4, 3)}$ |")
has("X4 row (3.7)", f"| $s^2+\\bar R^2$, (3.7) | ${sci(s**2, 3)}+{sci(Rbar**2, 3)}$ |")
q2 = (Rbar / s) ** 2
chk("(Rbar/s)^2", q2, ".4f", "0.0027")
truth("third: the dropped share is exactly (Rbar/s)^2/3", abs(n3 / (3 * Rbar * s**2) - 1 - q2 / 3) < 1e-12)
truth("fourth: the dropped share is exactly 2(Rbar/s)^2 + (Rbar/s)^4/3",
      abs(n4 / (3 * s**4) - 1 - (2 * q2 + q2**2 / 3)) < 1e-12)
chk("third: dropped share %", q2 / 3 * 100, ".2f", "0.09")
chk("third: dropped share from printed 0.0027 %", 0.0027 / 3 * 100, ".2f", "0.09")
chk("fourth: dropped share %", (2 * q2 + q2**2 / 3) * 100, ".2f", "0.54")
chk("fourth: dropped share from printed 0.0027 %", (2 * 0.0027 + 0.0027**2 / 3) * 100, ".2f", "0.54")
has("E6 shares", "\\tfrac13(\\bar R/s)^2=0.09\\%$ of $3\\bar Rs^2=")
has("E6 shares", "\\tfrac13(\\bar R/s)^4=0.54\\%$ of $3s^4=")
has("3 Rbar s^2", sci(3 * Rbar * s**2, 3))
has("3 s^4", sci(3 * s**4, 3))
truth("3 s^4 from six-decimal inputs prints the same", sci(3 * s6**4, 3) == sci(3 * s**4, 3))
truth("E6 no longer prints shares from differences of four-figure moments", "the printed moments give" not in NORM)
truth("LM4 prints 0050's excess kurtosis 8.12 and the ratio 3.7", "excess kurtosis** of 8.12" in LM04 and "3.7 times" in LM04)
has("0050's 8.12", "8.12")
anchor("A14-47", g10(skew))
anchor("A14-48", f"Kurt {g10(exk + 3)}; excess {g10(exk)}")
anchor("A14-49", g10(m3))
anchor("A14-50", g10(n3))
anchor("A14-51", g10(m4))
anchor("A14-52", g10(m4 / n4))
anchor("A14-53", g10(n4))
anchor("A14-23", f"E R^2 {g10(m2)}; s^2 {g10(s**2)}; Rbar^2 {g10(Rbar**2)}")
anchor("A14-54", f"(Rbar/s)^2 {g10(q2)}")
anchor("A14-54", f"(Rbar/s)^2/3 {g10(q2 / 3 * 100)}%")
anchor("A14-54", f"2(Rbar/s)^2 + (Rbar/s)^4/3 {g10((2 * q2 + q2**2 / 3) * 100)}%")
anchor("A14-55", f"3 mu sigma^2 {g10(3 * Rbar * s**2)}; 3 sigma^4 {g10(3 * s**4)}")

# ---- KC: f = 2
chk("2s %", 2 * s * 100, ".3f", "2.417")
chk("2s to five decimals %", 2 * s * 100, ".5f", "2.41673")
chk("2 x printed s", 2 * 1.2084, ".4f", "2.4168")
has("E[(2R)^2]", sci(4 * m2, 3))
truth("4 x printed E[R^2] prints the same", f"{4 * 1.464e-4:.3e}" == f"{4 * m2:.3e}")
anchor("A14-17", f"2s {g10(2 * s * 100)}%")

# ====================================================================== Section 5
absR = np.abs(R)
chk("E|R| %", float(absR.mean()) * 100, ".4f", "0.8402")
chk("Markov on |R| from printed %", 0.8402 / 3 * 100, ".1f", "28.0")
chk("Markov on |R| unrounded %", float(absR.mean()) / 0.03 * 100, ".1f", "28.0")
chk("Markov on R^2 from printed %", 1.464e-4 / 0.0009 * 100, ".2f", "16.27")
chk("Markov on R^2 unrounded %", m2 / 0.0009 * 100, ".2f", "16.27")
n3a = int((absR >= 0.03 - EPS).sum())
chk("days |R| >= 3%", n3a, "d", "175")
chk("share |R| >= 3% %", n3a / T * 100, ".2f", "2.99")
k3p = (0.0625 + 3) / 1.2084
chk("k at -3% from printed", k3p, ".3f", "2.534")
chk("k at -3% unrounded", (Rbar + 0.03) / s, ".3f", "2.534")
chk("Cantelli at -3% from printed k", 1 / (1 + 2.534**2) * 100, ".2f", "13.47")
chk("Cantelli at -3% unrounded", 1 / (1 + ((Rbar + 0.03) / s) ** 2) * 100, ".2f", "13.47")
n3d = int((R <= -0.03 + EPS).sum())
closes = [Fraction(repr(float(v))) for v in d.tr]
n3x = sum(1 for a, b in pairwise(closes) if b / a - 1 <= Fraction(-3, 100))
truth("closes have two decimals", all((c * 100).denominator == 1 for c in closes))
truth("guard and exact fractions both give 108 at -3%", n3d == n3x == 108)
has("108 days", "108 days at or below −3%".replace("−", "-"))
chk("share at or below -3% %", n3d / T * 100, ".2f", "1.85")
anchor("A14-56", f"{g10(absR.mean() * 100)}%")
anchor("A14-59", f"{n3a}; {g10(n3a / T * 100)}%")
anchor("A14-60", f"k {g10((Rbar + 0.03) / s)}")
anchor("A14-61", f"{n3d}; {g10(n3d / T * 100)}%; exact-fraction recount {n3x}")

# ---- E8
chk("threshold Rbar - 4s %", (Rbar - 4 * s) * 100, ".3f", "-4.771")
chk("threshold from printed %", 0.0625 - 4 * 1.2084, ".3f", "-4.771")
chk("Cantelli at k = 4 %", 100 / 17, ".2f", "5.88")
has("1/17", "1/17=5.88")
phi4 = float(stats.norm.cdf(-4))
has("Phi(-4)", sci(phi4, 2))
truth("LM5 prints Phi(-4) = 3.17e-5", "3.17\\times10^{-5}" in LM05)
chk("normal expected days", T * phi4, ".3f", "0.185")
chk("normal expected days from printed", T * 3.17e-5, ".3f", "0.185")
n4 = int((z <= -4 + EPS).sum())
chk("days z <= -4", n4, "d", "17")
chk("share z <= -4 %", n4 / T * 100, ".2f", "0.29")
chk("ratio to the normal count", n4 / (T * phi4), ".0f", "92")
chk("ratio from printed 0.185", 17 / 0.185, ".0f", "92")
truth("about a twentieth of the bound", abs(n4 / T * 17 - 1 / 20) < 0.002)
n4t = int((np.abs(z) >= 4 - EPS).sum())
chk("days |z| >= 4", n4t, "d", "30")
chk("share |z| >= 4 %", n4t / T * 100, ".2f", "0.51")
chk("Chebyshev at k = 4 %", 100 / 16, ".2f", "6.25")
chk("normal two-sided expected days", 2 * T * phi4, ".2f", "0.37")
anchor("A14-26", f"{n4}; {g10(n4 / T * 100)}%")
anchor("A14-63", g10(phi4))
anchor("A14-64", f"T Phi(-4) {g10(T * phi4)}")
anchor("A14-65", f"{g10((Rbar - 4 * s) * 100)}%")
anchor("A14-66", g10(n4 / (T * phi4)))
anchor("A14-67", f"{n4t}; {g10(n4t / T * 100)}%")

# ---- X5 (bounds chart) and its note
imin = int(R.argmin())
has("Cantelli days at k = 1", "2,924.5")
truth("T/2 = 2,924.5", T / 2 == 2924.5)
chk("Cantelli days at k = 4", T / 17, ".1f", "344.1")
chk("Cantelli days at k = 8", T / 65, ".1f", "90.0")
chk("smallest z", -float(z[imin]), ".2f", "8.08")
truth("the smallest z is 7 April 2025", str(d.rdates[imin]) == "2025-04-07")
has("7 April 2025", "7 April 2025")
chk("worst day %", float(R[imin]) * 100, ".4f", "-9.6997")
truth("limit regimes: last 7% date 2015-05-29, first 10% date 2015-06-01",
      max(t for t in d.rdates if t < LIMIT_CHANGE).isoformat() == "2015-05-29" and str(LIMIT_CHANGE) == "2015-06-01"
      and "1 June 2015" in LM05)
has("limit dates", "7% until 29 May 2015 and 10% from 1 June 2015")
bnd = json.loads((ROOT / "src" / "data" / "lm14-bounds.json").read_text(encoding="utf-8"))
step = bnd["series"][1]
truth("X5 step: 665 at k = 1, 17 at k = 4, 1 up to k = 8.08",
      step["y"][0] == 665 and step["y"][[i for i, x in enumerate(step["x"]) if x <= 4][-1]] == 17
      and step["y"][-2] == 1 and round(step["x"][-1], 2) == 8.08)
cant = dict(zip(bnd["series"][0]["x"], bnd["series"][0]["y"], strict=True))
truth("X5 bound series holds 2,924.5, 344.1 and 90.0", round(cant[1.0], 1) == 2924.5 and round(cant[4.0], 1) == 344.1
      and round(cant[8.0], 1) == 90.0)
anchor("A14-25", f"Cantelli days T/(1+k^2) at k=1,4,8: {g10(T / 2)}, {g10(T / 17)}, {g10(T / 65)}; min z {g10(z[imin])}")

# ---- X6
for k in range(1, 7):
    nt = int((np.abs(z) >= k - EPS).sum())
    nl = int((z <= -k + EPS).sum())
    for v in (nt / T * 100, nl / T * 100, 100 / k**2, 100 / (1 + k**2)):
        assert not tie(v, ".2f"), (k, v)
    has(f"X6 row k={k}", f"| {k} | {nt:,} | {nt / T * 100:.2f}% | {100 / k**2:.2f}% | {nl:,} | {nl / T * 100:.2f}% | "
        f"{100 / (1 + k**2):.2f}% |")
    anchor("A14-18", f"k={k}: two-sided {nt} ({g10(nt / T * 100)}%)")
has("KC k = 2", "TAIEX had 319 days (5.45%) and 188 days (3.21%)")

# ====================================================================== Section 6
# ---- widget's initial state (2008 and 2009 from the printed returns) and X8's pair row
key0, _, b0, a0, p0 = PRESETS[0]
truth("the widget starts from the printed 2008 and 2009 returns", (b0, a0, p0) == (0.8334, 0.4307, 0.5))
pr = two_point(b0, a0, p0)
truth("the pair's mu and sigma are two-decimal ties", tie(pr["mu"] * 100, ".2f") and tie(pr["sd"] * 100, ".2f"))
chk("pair mu %", pr["mu"] * 100, ".1f", "20.1")
chk("pair sigma %", pr["sd"] * 100, ".1f", "63.2")
chk("pair g %", pr["g"] * 100, ".3f", "2.141")
chk("pair ln(1 + mu) %", pr["lnmu"] * 100, ".3f", "18.345")
chk("pair R_G %", pr["RG"] * 100, ".2f", "2.16")
chk("pair (3.9) %", (pr["mu"] - pr["var"] / 2) * 100, ".2f", "0.16")
chk("pair Jensen gap", pr["jensen"] * 100, ".2f", "16.20")
chk("pair drag", pr["drag"] * 100, ".2f", "17.97")
chk("pair sigma^2/2", pr["var"] / 2 * 100, ".2f", "19.97")
chk("pair second order", pr["t2"] * 100, ".2f", "13.84")
chk("pair through the fourth order", (pr["t2"] + pr["t3"] + pr["t4"]) * 100, ".2f", "15.76")
jw = json.loads((ROOT / "src" / "data" / "lm14-jensen.json").read_text(encoding="utf-8"))
truth("lm14-jensen presets match PRESETS", [(o["key"], o["b"], o["a"], o["p"]) for o in jw["widget"]["presets"]]
      == [(k, b, a, p) for k, _, b, a, p in PRESETS])
truth("lm14-jensen marks the pair's mean, g and ln(1 + mu)",
      abs(jw["ann"][0]["x"] - pr["mu"]) < 1e-6 and abs(jw["ann"][2]["y"] - pr["g"]) < 1e-6
      and abs(jw["ann"][1]["y"] - pr["lnmu"]) < 1e-6)
bet25 = two_point(0.50, 0.25, 0.5)
truth("the 25x preset shows E3's 5.889% and 11.778%", f"{bet25['g'] * 100:.3f}" == "5.889"
      and f"{bet25['lnmu'] * 100:.3f}" == "11.778")
anchor("A14-31", f"g {g10(pr['g'] * 100)}%; R_G {g10(pr['RG'] * 100)}%; ln(1+mu) {g10(pr['lnmu'] * 100)}%; "
       f"ln(1+mu)-g {g10(pr['jensen'] * 100)}; mu-R_G {g10(pr['drag'] * 100)}; sigma^2/2 {g10(pr['var'] / 2 * 100)}; "
       f"2nd-order {g10(pr['t2'] * 100)}; through 4th {g10((pr['t2'] + pr['t3'] + pr['t4']) * 100)}")
un = law(np.array([r08, r09]), np.array([0.5, 0.5]))
anchor("A14-83", f"sigma^2/2 {g10(un['var'] / 2 * 100)}; R_G {g10(un['RG'] * 100)}%")

# ---- E9
chk("1 + arithmetic mean", 1 + ann["mu"], ".4f", "1.1497")
chk("1 + compound rate", 1 + cagr, ".4f", "1.1235")
chk("pair AM from printed", (0.5693 + 1.8334) / 2, ".5f", "1.20135")
chk("pair GM from printed", math.sqrt(0.5693 * 1.8334), ".5f", "1.02164")
chk("pair compound rate from printed %", (math.sqrt(0.5693 * 1.8334) - 1) * 100, ".2f", "2.16")
anchor("A14-68", f"1 + mean {g10(1 + ann['mu'])}; geometric mean {g10(1 + cagr)}")
anchor("A14-69", f"AM {g10((0.5693 + 1.8334) / 2)}; GM {g10(math.sqrt(0.5693 * 1.8334))}")

# ====================================================================== Section 7
tr23 = law(R, np.full(T, 1 / T))
truth("law() reproduces the sample's moments", abs(tr23["mu"] - Rbar) < 1e-15 and abs(tr23["jensen"] - J) < 1e-15)
chk("daily second-order term bp", tr23["t2"] * 1e4, ".4f", "0.7292")
chk("daily third-order term bp", tr23["t3"] * 1e4, ".4f", "0.0020")
chk("daily fourth-order term bp", tr23["t4"] * 1e4, ".4f", "0.0004")
chk("daily terms through the fourth bp", (tr23["t2"] + tr23["t3"] + tr23["t4"]) * 1e4, ".4f", "0.7316")
chk("printed terms add up", 0.7292 + 0.0020 + 0.0004, ".4f", "0.7316")
has("terms as printed", "0.7292+0.0020+0.0004")
truth("third term is -Skew sigma^3 / (3 (1 + mu)^3) and positive", tr23["t3"] > 0
      and abs(tr23["t3"] - (-skew * s**3 / (3 * (1 + Rbar) ** 3))) < 1e-15)
chk("drag from the gap (exact identity) bp", (1 + Rbar) * -math.expm1(-J) * 1e4, ".4f", "0.7320")
chk("drag from printed 0.0625% and 0.7316 bp", 1.000625 * -math.expm1(-0.7316e-4) * 1e4, ".4f", "0.7320")
chk("annual Jensen gap", ann["jensen"] * 100, ".2f", "2.31")
chk("annual second order", ann["t2"] * 100, ".2f", "2.12")
chk("annual through the fourth", (ann["t2"] + ann["t3"] + ann["t4"]) * 100, ".2f", "2.30")
chk("annual drag", ann["drag"] * 100, ".2f", "2.62")
chk("annual sigma^2/2", ann["var"] / 2 * 100, ".2f", "2.81")
chk("annual sigma %", ann["sd"] * 100, ".2f", "23.70")
chk("annual skewness", ann["skew"], ".2f", "0.19")
chk("annual kurtosis", ann["kurt"], ".2f", "5.02")
chk("s_r %", s_r * 100, ".4f", "1.2107")
chk("s_r^2/2 bp", s_r**2 / 2 * 1e4, ".4f", "0.7329")
chk("s_r^2/2 from printed s_r bp", 0.012107**2 / 2 * 1e4, ".4f", "0.7329")
hm = two_point(1.0, 0.5, 0.5)
truth("+100%/-50%: mu 25%, sigma 75%, drag 25, sigma^2/2 28.125 exact, second order 18, through 4th 21.24",
      abs(hm["mu"] - 0.25) < 1e-15 and abs(hm["sd"] - 0.75) < 1e-15 and abs(hm["drag"] - 0.25) < 1e-15
      and hm["var"] / 2 == 0.28125 and abs(hm["t2"] - 0.18) < 1e-15 and abs(hm["t2"] + hm["t3"] + hm["t4"] - 0.2124) < 1e-15)
truth("28.125 would tie at two decimals", tie(28.125, ".2f"))
truth("+100%/-50%: (3.9)'s mu - sigma^2/2 = -3.125% exactly, a two-decimal tie (the widget prints three)",
      (hm["mu"] - hm["var"] / 2) * 100 == -3.125 and tie(-3.125, ".2f"))
chk("+100%/-50% Jensen gap", hm["jensen"] * 100, ".2f", "22.31")
has("X8 row daily", f"| TAIEX, daily (bp) | {Rbar * 100:.4f}% | {s * 100:.4f}% | {(Rbar - RG) * 1e4:.4f} | {s**2 / 2 * 1e4:.4f} | "
    f"{J * 1e4:.4f} | {tr23['t2'] * 1e4:.4f} | {(tr23['t2'] + tr23['t3'] + tr23['t4']) * 1e4:.4f} |")
has("X8 row years", f"| TAIEX, years | {ann['mu'] * 100:.2f}% | {ann['sd'] * 100:.2f}% | {ann['drag'] * 100:.2f} | "
    f"{ann['var'] / 2 * 100:.2f} | {ann['jensen'] * 100:.2f} | {ann['t2'] * 100:.2f} | "
    f"{(ann['t2'] + ann['t3'] + ann['t4']) * 100:.2f} |")
has("X8 row pair", f"| 2008 and 2009 | {pr['mu'] * 100:.1f}% | {pr['sd'] * 100:.1f}% | {pr['drag'] * 100:.2f} | "
    f"{pr['var'] / 2 * 100:.2f} | {pr['jensen'] * 100:.2f} | {pr['t2'] * 100:.2f} | "
    f"{(pr['t2'] + pr['t3'] + pr['t4']) * 100:.2f} |")
has("X8 row +100/-50", "| +100% or -50% | 25% | 75% | 25.00 | 28.125 | 22.31 | 18.00 | 21.24 |")
anchor("A14-19", f"{g10(J * 1e4)} bp")
anchor("A14-28", f"{g10(tr23['t2'] * 1e4)}, {g10(tr23['t3'] * 1e4)}, {g10(tr23['t4'] * 1e4)} bp")
anchor("A14-29", f"{g10(ann['sd'] * 100)}%; skew {g10(ann['skew'])}; kurt {g10(ann['kurt'])}")
anchor("A14-30", f"ln(1+mu)-g {g10(ann['jensen'] * 100)}; 2nd {g10(ann['t2'] * 100)}; "
       f"through 4th {g10((ann['t2'] + ann['t3'] + ann['t4']) * 100)}; mu-R_G {g10(ann['drag'] * 100)}; "
       f"sigma^2/2 {g10(ann['var'] / 2 * 100)}")
anchor("A14-32", f"ln(1+mu)-g {g10(hm['jensen'] * 100)}")
anchor("A14-70", f"s_r^2/2 {g10(s_r**2 / 2 * 1e4)} bp; s_r {g10(s_r * 100)}%")

# ---- X7: each year's drag against half its variance
pts = year_points(d)
gaps = max((abs(a - b), y) for y, a, b in pts)
rels = max((abs(a / b - 1), y) for y, a, b in pts)
lo = min(pts, key=lambda t: t[1])
hi = max(pts, key=lambda t: t[1])
chk("largest gap to the line bp", gaps[0], ".4f", "0.0097")
truth("largest gap in 2024 (absolute and relative)", gaps[1] == 2024 and rels[1] == 2024)
chk("largest relative gap %", rels[0] * 100, ".2f", "1.13")
chk("smallest drag bp (2017)", lo[1], ".2f", "0.14")
chk("largest drag bp (2008)", hi[1], ".2f", "2.25")
truth("extremes are 2017 and 2008", lo[0] == 2017 and hi[0] == 2008)
has("X7 extremes", "0.14 bp (2017) to 2.25 bp (2008)")
dy = json.loads((ROOT / "src" / "data" / "lm14-dragyears.json").read_text(encoding="utf-8"))
truth("X7 plots every year", len(dy["series"][0]["x"]) == 23
      and np.allclose(dy["series"][0]["y"], [g for _, g, _ in pts], atol=1e-6))
anchor("A14-27", f"min drag 2017 {g10(lo[1])} bp")
anchor("A14-27", f"largest absolute gap 2024 {g10(gaps[0])} bp")

# ---- pitfall: (3.9) at annual frequency
chk("(3.9) from printed %", 14.97 - 23.70**2 / 200, ".2f", "12.16")
chk("(3.9) unrounded %", (ann["mu"] - ann["var"] / 2) * 100, ".2f", "12.17")
has("(3.9) annual", "14.97\\%-23.70\\%^2/2=12.16\\%")

# ---- KC f = 2
j2 = (float(np.log1p(2 * Rbar)) - float(np.log1p(2 * R).mean())) * 1e4
chk("Jensen gap at f = 2 bp", j2, ".3f", "2.936")
chk("4 x printed 0.7316", 4 * 0.7316, ".3f", "2.926")
anchor("A14-20", f"{g10(j2)} bp")

# ====================================================================== Section 8
truth("X9 versions: NumPy 2.5.3 and SciPy 1.18.1", np.__version__ == "2.5.3" and __import__("scipy").__version__ == "1.18.1")
has("versions", "NumPy 2.5.3 and SciPy 1.18.1")
with np.errstate(all="ignore"):
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ex = stats.norm(Rbar, s).expect(np.log1p)
truth("norm(...).expect(np.log1p) returns nan", math.isnan(ex))
truth("np.var and np.std default to divisor T", float(np.var(R)) == float(((R - Rbar) ** 2).mean()) and np.std(R) == s)
truth("code: lower4 = 17 with the guard", int((z <= -4 + 1e-12).sum()) == 17)
has("code quantile comment", "# R_(6), -6.313%")
has("code kurtosis comment", "# 5.27, excess kurtosis")
has("code gap comment", "# Jensen gap, 0.7316 bp")
truth("code block lines fit 80 characters", all(len(ln) <= 80 for ln in TEXT.split("```python")[1].split("```")[0].splitlines()))

# ====================================================================== Practice problems
# ---- P1, P2: four days of the +2%/-1% bet
four = {Fraction(102, 100) ** j * Fraction(99, 100) ** (4 - j): Fraction(math.comb(4, j), 16) for j in range(5)}
fv = sorted(four)
for v, pstr in zip(fv, ("0.960596", "0.989705", "1.019696", "1.050596", "1.082432"), strict=True):
    chk(f"P1 value {pstr}", float(v), ".6f", pstr)
has("P1 probabilities", "1/16, 4/16, 6/16, 4/16 and 1/16")
EG = sum(v * p for v, p in four.items())
chk("P1 mean", float(EG), ".6f", "1.020151")
truth("P1 mean = 1.005^4", EG == Fraction(1005, 1000) ** 4)
truth("P1: the only median is 1.019696 (A)", medians([float(v) for v in fv], [four[v] for v in fv]) == [float(fv[2])])
FG = [sum(four[u] for u in fv if u <= v) for v in fv]
truth("P1/P2: F_G = 1/16, 5/16, 11/16, 15/16, 1", FG == [Fraction(1, 16), Fraction(5, 16), Fraction(11, 16), Fraction(15, 16), 1])
truth("P1 (C): Pr(G >= mean) = 5/16", sum(p for v, p in four.items() if v >= EG) == Fraction(5, 16))
has("P2 F_G", "1/16, 5/16, 11/16, 15/16 and 1")
chk("P2 E[G]", float(EG), ".5f", "1.02015")
truth("P2: by (14.1) and the binomial theorem, E[G] = ((1.02 + 0.99)/2)^4 = 1.005^4",
      EG == sum(Fraction(math.comb(4, j), 16) * Fraction(102, 100) ** j * Fraction(99, 100) ** (4 - j) for j in range(5))
      == ((Fraction(102, 100) + Fraction(99, 100)) / 2) ** 4 == Fraction(1005, 1000) ** 4)
has("P2 binomial", "((1.02+0.99)/2)^4=1.005^4=1.02015")
eln1 = 0.5 * math.log(1.02) + 0.5 * math.log(0.99)
chk("P2 E ln(1 + R) one day %", eln1 * 100, ".6f", "0.487615")
eln4 = sum(math.log(float(v)) * float(p) for v, p in four.items())
chk("P2 E ln G %", eln4 * 100, ".5f", "1.95046")
chk("P2 E ln G from printed %", 4 * 0.487615, ".5f", "1.95046")
chk("P2 ln E G %", math.log(float(EG)) * 100, ".5f", "1.99502")
chk("P2 gap bp", (math.log(float(EG)) - eln4) * 1e4, ".3f", "4.456")
chk("P2 gap from printed bp", (1.99502 - 1.95046) * 100, ".3f", "4.456")
anchor("A14-72", f"gap {g10((math.log(float(EG)) - eln4) * 1e4)} bp")

# ---- P3: Pareto mean; the two others diverge
truth("P3: Pareto mean 1.5/0.5 = 3", 1.5 / 0.5 == 3)
truth("P3 (A): partial sums of 2^j 2^-j grow without bound", sum(2**j * 2.0**-j for j in range(1, 1001)) == 1000)
truth("P3 (B): Cauchy partial integrals ln(1 + M^2)/pi grow like (2/pi) ln M, without bound",
      math.log(1 + 1e6**2) / math.pi - math.log(1 + 1e3**2) / math.pi > 4)
has("P3", "1.5/0.5=3")

# ---- P4: +1% w.p. 0.9, -5% otherwise, exact
v4, p4 = [Fraction(1, 100), Fraction(-5, 100)], [Fraction(9, 10), Fraction(1, 10)]
mu4 = sum(v * p for v, p in zip(v4, p4, strict=True))
var4 = sum((v - mu4) ** 2 * p for v, p in zip(v4, p4, strict=True))
sd4 = Fraction(18, 1000)
truth("P4: mu 0.4%, sigma 1.8%, E R^2 3.4e-4, E R^3 -1.16e-5", mu4 == Fraction(4, 1000) and var4 == sd4**2
      and sum(v * v * p for v, p in zip(v4, p4, strict=True)) == Fraction(34, 100000)
      and sum(v**3 * p for v, p in zip(v4, p4, strict=True)) == Fraction(-116, 10**7))
zs = [(v - mu4) / sd4 for v in v4]
truth("P4: standardized values 1/3 and -3", zs == [Fraction(1, 3), Fraction(-3)])
sk4 = sum(zv**3 * p for zv, p in zip(zs, p4, strict=True))
ku4 = sum(zv**4 * p for zv, p in zip(zs, p4, strict=True))
truth("P4: skewness -8/3, kurtosis 73/9", sk4 == Fraction(-8, 3) and ku4 == Fraction(73, 9))
chk("P4 skewness", float(sk4), ".2f", "-2.67")
chk("P4 kurtosis", float(ku4), ".2f", "8.11")
chk("P4 excess", float(ku4) - 3, ".2f", "5.11")
truth("P4 at f = 8: mu 3.2%, sigma 14.4%", 8 * mu4 == Fraction(32, 1000) and 8 * sd4 == Fraction(144, 1000))
m2_8 = sum((8 * v) ** 2 * p for v, p in zip(v4, p4, strict=True))
m3_8 = sum((8 * v) ** 3 * p for v, p in zip(v4, p4, strict=True))
truth("P4 at f = 8: E[(8R)^2] = 64 x 3.4e-4 = 0.02176 = 0.144^2 + 0.032^2",
      m2_8 == 64 * Fraction(34, 100000) == Fraction(2176, 100000) == Fraction(144, 1000) ** 2 + Fraction(32, 1000) ** 2)
truth("P4 at f = 8: E[(8R)^3] = 512 x (-1.16e-5) = -0.0059392", m3_8 == 512 * Fraction(-116, 10**7) == Fraction(-59392, 10**7))
has("P4 f = 8 second moment", "=64\\times3.4\\times10^{-4}=0.02176$, which is $0.144^2+0.032^2$")
has("P4 f = 8 third moment", "=512\\times(-1.16\\times10^{-5})=-0.0059392$")
truth("P4 squared deviations in %^2: 0.36, 29.16, variance 3.24", (Fraction(6, 10)) ** 2 == Fraction(36, 100)
      and Fraction(54, 10) ** 2 == Fraction(2916, 100) and Fraction(9, 10) * Fraction(36, 100) + Fraction(1, 10) * Fraction(2916, 100) == Fraction(324, 100))
truth("LM4 prints this trade's exact Kelly exposure 8", "exact 8" in LM04)
anchor("A14-74", "Skew -2.666666667 (-8/3); Kurt 8.111111111 (73/9), excess 5.111111111")

# ---- P5
truth("P5: E[Z^6] = 5 E[Z^4] = 15 = Var(Z^3)", 5 * 3 == 15 and abs(stats.norm.moment(6) - 15) < 1e-12)
mx, sx2 = Fraction(5, 100), Fraction(4, 100)
truth("P5: E X^3 = 0.000125 + 0.006 = 0.006125; E X^4 = 0.00000625 + 0.0006 + 0.0048 = 0.00540625",
      mx**3 == Fraction(125, 10**6) and 3 * mx * sx2 == Fraction(6, 1000) and mx**3 + 3 * mx * sx2 == Fraction(6125, 10**6)
      and mx**4 == Fraction(625, 10**8) and 6 * mx**2 * sx2 == Fraction(6, 10**4) and 3 * sx2**2 == Fraction(48, 10**4)
      and mx**4 + 6 * mx**2 * sx2 + 3 * sx2**2 == Fraction(540625, 10**8))
nz = stats.norm(0.05, 0.2)
truth("P5: SciPy's moment(3) and moment(4) agree", abs(nz.moment(3) - 0.006125) < 1e-15 and abs(nz.moment(4) - 0.00540625) < 1e-15)
has("P5 values", "=0.006125")
has("P5 values", "=0.00540625")

# ---- P6
k5 = (0.0625 + 5) / 1.2084
chk("P6 k from printed", k5, ".4f", "4.1894")
chk("P6 Cantelli from printed k %", 1 / (1 + 4.1894**2) * 100, ".2f", "5.39")
chk("P6 Chebyshev from printed k %", 1 / 4.1894**2 * 100, ".2f", "5.70")
n5 = int((R <= -0.05 + EPS).sum())
chk("P6 days at or below -5%", n5, "d", "15")
chk("P6 share %", n5 / T * 100, ".2f", "0.26")
anchor("A14-76", f"k from printed {g10(k5)}")

# ---- P7
chk("P7 option A %", 100 / 9, ".1f", "11.1")
truth("P7 option C 10%", 100 / (1 + 9) == 10)
truth("P7: the Pareto second moment diverges (partial integrals 3(sqrt M - 1))",
      3 * (math.sqrt(1e8) - 1) > 10 * 3 * (math.sqrt(1e6) - 1) - 1e-6)

# ---- P8: LM1's counterexample
chk("P8 1.5e^0.10 - 0.5e^0.20", 1.5 * math.exp(0.10) - 0.5 * math.exp(0.20), ".4f", "1.0471")
chk("P8 its logarithm", math.log(1.5 * math.exp(0.10) - 0.5 * math.exp(0.20)), ".4f", "0.0460")
chk("P8 weighted log returns", 1.5 * 0.10 - 0.5 * 0.20, ".4f", "0.0500")
truth("LM1 prints 0.0460 and 0.0500", "=0.0460$" in LM01 and "=0.0500$" in LM01)
anchor("A14-78", f"ln(1.5e^0.10 - 0.5e^0.20) {g10(math.log(1.5 * math.exp(0.10) - 0.5 * math.exp(0.20)))}")

# ---- P9: X = 1 + 8R at the Kelly exposure
f9 = 0.9 / 0.05 - 0.1 / 0.01
X9 = np.array([1.08, 0.60])
p9 = np.array([0.9, 0.1])
truth("P9: Kelly exposure 8 and X in {1.08, 0.60}", abs(f9 - 8) < 1e-12 and np.allclose(1 + 8 * np.array([0.01, -0.05]), X9))
EX9 = float((p9 * X9).sum())
chk("P9 E ln X %", float((p9 * np.log(X9)).sum()) * 100, ".2f", "1.82")
chk("P9 ln E X %", math.log(EX9) * 100, ".2f", "3.15")
has("P9 E[1/X] = 1", "\\E[1/X]=1$")
truth("P9 E[1/X] = 1 exactly", Fraction(9, 10) / Fraction(108, 100) + Fraction(1, 10) / Fraction(60, 100) == 1)
chk("P9 1/E X", 1 / EX9, ".4f", "0.9690")
chk("P9 E sqrt X", float((p9 * np.sqrt(X9)).sum()), ".4f", "1.0128")
chk("P9 sqrt E X", math.sqrt(EX9), ".4f", "1.0159")
anchor("A14-79", f"E ln X {g10((p9 * np.log(X9)).sum() * 100)}%")

# ---- P10: annual series from the printed moments
mp, sp, skp, kup = 0.1497, 0.2370, 0.19, 5.02
t2p = sp**2 / (2 * (1 + mp) ** 2)
t3p = -skp * sp**3 / (3 * (1 + mp) ** 3)
t4p = kup * sp**4 / (4 * (1 + mp) ** 4)
chk("P10 term 2", t2p * 100, ".4f", "2.1247")
chk("P10 term 3", t3p * 100, ".4f", "-0.0555")
chk("P10 term 4", t4p * 100, ".4f", "0.2266")
chk("P10 sum", (t2p + t3p + t4p) * 100, ".4f", "2.2958")
chk("P10 sum of the printed terms", 2.1247 - 0.0555 + 0.2266, ".4f", "2.2958")
chk("P10 R_G from the printed sum %", (1.1497 * math.exp(-0.022958) - 1) * 100, ".2f", "12.36")
chk("P10 R_G second order alone %", (1.1497 * math.exp(-0.021247) - 1) * 100, ".2f", "12.55")
truth("P10: the fourth-order term is about four times the third", 3.5 < abs(t4p / t3p) < 4.5)
chk("P10 R_G from the second- and fourth-order terms %", (1.1497 * math.exp(-(0.021247 + 0.002266)) - 1) * 100, ".2f", "12.30")
chk("P10 R_G from the second- and fourth-order terms, unrounded %", ((1 + mp) * math.exp(-(t2p + t4p)) - 1) * 100, ".2f",
    "12.30")
truth("P10: the third-order term raises the estimate from 12.30% to 12.36%", t3p < 0)
chk("P10 (3.9)'s drag sigma^2/2 from printed", 0.2370**2 / 2 * 100, ".2f", "2.81")
chk("P10 drag's leading term sigma^2/(2(1 + mu)) from printed", 0.2370**2 / (2 * 1.1497) * 100, ".2f", "2.44")
chk("P10 drag's leading term unrounded", ann["var"] / (2 * (1 + ann["mu"])) * 100, ".2f", "2.44")
truth("P10: the drag is (1 + mu)(1 - e^-gap), whose leading term carries 1/(1 + mu)",
      abs(ann["drag"] - (1 + ann["mu"]) * -math.expm1(-ann["jensen"])) < 1e-15)
truth("P10: the factor 1/(1 + mu)^2 would move (3.9) away from the actual rate",
      abs((mp - sp**2 / (2 * (1 + mp) ** 2)) - cagr) > abs((mp - sp**2 / 2) - cagr))
has("P10 (c) drag", "$\\sigma^2/(2(1+\\mu))=2.44$ points, and the higher terms bring it to the actual 2.62")
has("P10 (c) (3.9)", "it subtracts $\\sigma^2/2=2.81$ points as the drag")
has("P10 printed inputs", "$\\mu=14.97\\%$, $\\sigma=23.70\\%$ (divisor 23), skewness 0.19 and kurtosis 5.02")
anchor("A14-80", f"terms {g10(t2p * 100)}, {g10(t3p * 100)}, {g10(t4p * 100)}")

# ---- P11: as X6 and the text
has("P11 (c)", "319, 99 and 30 days; lower, 188, 61 and 17")

# ---- the lab's regimes (extension)
cut = np.array([t < LIMIT_CHANGE for t in d.rdates])
anchor("A14-81", f"T {int(cut.sum())} (to 2015-05-29); T {int((~cut).sum())} (from 2015-06-01)")

# ====================================================================== text hygiene
truth("no tab, backspace or form feed in src/lm14.md", not any(c in TEXT for c in "\t\b\f"))
truth("every [[ex:]] and [[eg:]] label is defined",
      set(re.findall(r"\[\[(?:ex|eg):([\w-]+)\]\]", TEXT)) <= set(re.findall(r"\{#([\w-]+)\}", TEXT)))
truth("every exhibit is cited", set(re.findall(r"\[!exhibit\][^\n]*\{#([\w-]+)\}", TEXT))
      <= set(re.findall(r"\[\[ex:([\w-]+)\]\]", TEXT)))
truth("no 分配 in the Chinese text", "分配" not in TEXT)

print()
if DIFFS:
    print(f"anchors that differ ({len(DIFFS)}):")
    for line in DIFFS:
        print("  " + line)
else:
    print("anchors: every compared value agrees with plans/vol-3-anchors.md")
print(f"\nall {N_CHECKS} checks passed")
