"""Every number that LM17 (Law of Large Numbers and Central Limit Theorem) quotes, computed and checked against src/lm17.md.

Run:  PYTHONUTF8=1 uv run python data/lm17_numbers.py      (after data/vol3_series.py has built TR23)

Input: data/processed/vol3_taiex.parquet (TR23: the TAIEX total-return index from FinMind's
TaiwanStockTotalReturnIndex, closes 2003-01-02 .. 2026-10-08; columns date, tr, price, R, Rp), written and checked
by data/vol3_series.py. The module text is src/lm17.md; plans/vol-3-anchors.md holds the Stage 1 anchors (A17-nn).

Conventions (as the module states them): T = 5,849 simple daily returns R_t from 2003-01-03; log returns
r_t = ln(1 + R_t) for every sum; moments, correlations and kurtosis divide by the number of terms (scipy.stats.kurtosis
defaults: excess kurtosis, bias=True); years = calendar days between the first and last close / 365.25; A = T / years;
a horizon of tau years is m = round(A tau) whole sessions. The iid model draws days from TR23's empirical law, so
mu = Rbar, g = rbar, sigma_r = s_r; gbar(f) and s_r(f) are the mean and standard deviation of ln(1 + f R_t).
Counts use the guard R > 1e-12 (an up day) and are recounted exactly with Fraction on the two-decimal closes.
LM17 simulates nothing, so no random generator is created.

Checks (each stops the script on a failure):
  chk(label, value, fmt, printed)  format(value, fmt) equals the printed string, the value does not sit on a rounding
                                   tie of that format (lm11's tie()), and the printed string is in the module as a
                                   whole number. Hand computations are redone from the printed, rounded inputs
                                   (project/PITFALLS.md section 7).
  has(label, text)                 a literal string (a table row, a date, a phrase) is in the module.
  anchor(id, got)                  compares a value with plans/vol-3-anchors.md and reports a difference (never forced).
At the end the script lists the numbers of the module that no check covered, for the writer's and reviewer's eyes,
and prints "all N checks passed".
"""
import math
import re
from fractions import Fraction
from math import comb, exp, log, sqrt
from pathlib import Path

import numpy as np
import polars as pl
from numpy.typing import NDArray
from scipy import optimize, stats

Vec = NDArray[np.float64]

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PARQUET = HERE / "processed" / "vol3_taiex.parquet"
MD = ROOT / "src" / "lm17.md"
ANCHORS = ROOT / "plans" / "vol-3-anchors.md"
EPS = 1e-12
LIMIT_SWITCH = "2015-06-01"
Z95 = float(stats.norm.ppf(0.95))


def norm_text(s: str) -> str:
    """The module text with TeX thousands separators, escaped percent signs, \\text{} and minus signs made plain."""
    s = s.replace("{,}", ",").replace("\\%", "%").replace("\u2212", "-").replace("\\,", "")
    return re.sub(r"\\text\{\s*([^}]*)\}", r" \1", s)


TEXT = norm_text(MD.read_text(encoding="utf-8"))
N_CHECKS = 0
COVERED: set[str] = set()
ANCHOR_DIFFS: list[str] = []


def in_text(printed: str) -> bool:
    """The printed number appears as a whole number (2.323 is not inside 2.3235, 0.32 not inside 10.32)."""
    return re.search(r"(?<![\d.])" + re.escape(printed) + r"(?![\d])", TEXT) is not None


def tie(value: float, fmt: str) -> bool:
    """True when value lies on a rounding boundary of fmt (a reader rounding by hand could go either way)."""
    m = re.search(r"\.(\d+)", fmt)
    d = int(m.group(1)) if m else 0
    if fmt.endswith(("e", "g")):
        return False
    scaled = abs(value) * 10**d * (100 if "%" in fmt else 1)
    return abs(scaled - math.floor(scaled) - 0.5) < 1e-6


def chk(label: str, value: float, fmt: str, printed: str) -> None:
    global N_CHECKS
    got = format(value, fmt)
    ok = got == printed and in_text(printed) and not tie(value, fmt)
    print(f"CHECK {label}: {got} (printed {printed}) {'ok' if ok else 'MISMATCH'}")
    assert got == printed, (label, got, printed)
    assert not tie(value, fmt), ("rounding tie: print more digits", label, value)
    assert in_text(printed), f"{label}: {printed!r} not found in src/lm17.md"
    COVERED.add(printed)
    N_CHECKS += 1


def has(label: str, text: str) -> None:
    global N_CHECKS
    assert text in TEXT, f"{label}: {text!r} not found in src/lm17.md"
    print(f"CHECK {label}: '{text}' in text ok")
    for num in re.findall(r"\d[\d,]*\.?\d*", text):
        COVERED.add(num.rstrip(".,"))
    N_CHECKS += 1


def same(label: str, got: str, printed: str, in_md: bool = True) -> None:
    """A value produced as a string (a fraction, a date) equals the printed one; in_md: it appears in the text."""
    global N_CHECKS
    assert got == printed, (label, got, printed)
    assert not in_md or printed in TEXT, f"{label}: {printed!r} not found in src/lm17.md"
    print(f"CHECK {label}: {got} ok")
    COVERED.add(printed)
    N_CHECKS += 1


def sci(label: str, value: float, digits: int, printed: str) -> None:
    """A number printed as m\\times10^{e} in the text: printed is 'm e', e.g. '2.7 -10'."""
    global N_CHECKS
    mant, ex = printed.split()
    got = f"{value:.{digits}e}"
    assert float(got) == float(f"{mant}e{ex}") and len(mant.replace(".", "").lstrip("-")) == digits + 1, (label, got, printed)
    tex = f"{mant}\\times10^{{{ex}}}"
    assert tex in TEXT, f"{label}: {tex!r} not found in src/lm17.md"
    print(f"CHECK {label}: {got} (printed {tex}) ok")
    COVERED.add(mant)
    N_CHECKS += 1


def _anchor_values() -> dict[str, str]:
    rows: dict[str, str] = {}
    sec = ANCHORS.read_text(encoding="utf-8").split("## LM17", 1)[1].split("\n## ", 1)[0]
    for line in sec.splitlines():
        if line.startswith("| A17-"):
            cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
            rows[cells[0]] = cells[3].strip("`")
    return rows


ANCHOR_ROWS = _anchor_values()
assert len(ANCHOR_ROWS) == 94, len(ANCHOR_ROWS)


def anchor(aid: str, got: str) -> None:
    """Compare with plans/vol-3-anchors.md; a difference is reported, not forced."""
    expected = ANCHOR_ROWS[aid]
    tag = "ok" if got == expected else "DIFFERS"
    print(f"ANCHOR {aid}: {got} (anchor {expected}) {tag}")
    if got != expected:
        ANCHOR_DIFFS.append(f"{aid}: script {got} | anchor {expected}")


def kurt_ex(x: Vec) -> float:
    """Excess kurtosis, divisor = number of terms (scipy.stats.kurtosis defaults), checked against SciPy below."""
    xc = x - x.mean()
    return float((xc**4).mean() / (xc**2).mean() ** 2 - 3)


def corr(a: Vec, b: Vec) -> float:
    a, b = a - a.mean(), b - b.mean()
    return float((a * b).mean() / sqrt(float((a * a).mean() * (b * b).mean())))


def window_sums(x: Vec, m: int) -> Vec:
    """All len(x) - m + 1 overlapping sums of m consecutive terms."""
    c = np.concatenate([[0.0], np.cumsum(x)])
    return c[m:] - c[:-m]


Phi = stats.norm.cdf

# ====================================================================== data (notation note, case)
assert PARQUET.exists(), "run data/vol3_series.py first"
df = pl.read_parquet(PARQUET).sort("date")
dates_all = [str(d) for d in df["date"].to_list()]
tr = df["tr"].to_numpy().astype(np.float64)
assert df["R"][0] is None and len(set(dates_all)) == len(dates_all)
R = df["R"].to_numpy()[1:].astype(np.float64)
assert np.allclose(R, tr[1:] / tr[:-1] - 1, rtol=0, atol=1e-15)
dates = dates_all[1:]
T = len(R)
r = np.log1p(R)
days = (df["date"][-1] - df["date"][0]).days
years = days / 365.25
A = T / years
Rb, s = float(R.mean()), float(R.std())
rb, sr = float(r.mean()), float(r.std())
G = float(tr[-1] / tr[0])
print(f"TR23: {len(tr)} closes {dates_all[0]} .. {dates_all[-1]}, T = {T}, {days} days, {years:.6f} years, A = {A:.6f}")
assert (len(tr), T, dates_all[0], dates[0], dates_all[-1]) == (5850, 5849, "2003-01-02", "2003-01-03", "2026-10-08")
anchor("A17-01", f"{len(tr)}")
anchor("A17-02", f"{T}")
anchor("A17-03", f"{days}")
anchor("A17-04", f"{years:.6f}")
anchor("A17-05", f"{A:.6f}")
chk("T", T, ",", "5,849")
chk("years", years, ".4f", "23.7645")
chk("A", A, ".2f", "246.12")
chk("years, two decimals (X6 note)", years, ".2f", "23.76")
chk("years, one decimal", years, ".1f", "23.8")
has("first close", "2 January 2003")
has("first return", "3 January 2003")
has("last close", "8 October 2026")
has("retrieval", "retrieved 18 October 2026")

# exact signs from the two-decimal closes; the guard agrees
trf = [Fraction(str(x)) for x in df["tr"].to_list()]
RF = [trf[i] / trf[i - 1] - 1 for i in range(1, len(trf))]
up_x, dn_x, zero_x = sum(x > 0 for x in RF), sum(x < 0 for x in RF), sum(x == 0 for x in RF)
up_g, dn_g = int((R > EPS).sum()), int((R < -EPS).sum())
assert (up_g, dn_g) == (up_x, dn_x) and zero_x == 0
anchor("A17-06", f"up {up_x}; down {dn_x}; zero {zero_x} (guard count {up_g})")
chk("up days", up_x, ",", "3,205")
chk("down days", dn_x, ",", "2,644")
has("no unchanged day", "finds no unchanged day")

# the case
chk("growth factor G", G, ".1f", "25.2")
chk("G, X1 end label", G, ".2f", "25.20")
anchor("A17-08", f"{G:.4f}")
anchor("A17-09", f"{Rb:.10%}")
chk("Rbar, the case (5 s.f.)", 100 * Rb, ".5f", "0.06251")
chk("Rbar, 6 decimals (E4, X6)", 100 * Rb, ".6f", "0.062505")
chk("Rbar, six significant figures (E4)", 100 * Rb, ".7f", "0.0625051")
chk("rbar", 100 * rb, ".6f", "0.055170")
chk("rbar, six significant figures (E4)", 100 * rb, ".7f", "0.0551696")
chk("s_r", 100 * sr, ".4f", "1.2107")
chk("case: (1.0006251)^T from the printed mean", 1.0006251**T, ".1f", "38.7")
chk("case: unrounded mean path", (1 + Rb) ** T, ".1f", "38.7")
chk("mean path (1+Rbar)^T", (1 + Rb) ** T, ".2f", "38.66")
chk("mean path from printed 0.062505%", 1.00062505**T, ".2f", "38.66")
anchor("A17-10", f"from 0.06251%: {1.0006251**T:.4f}; unrounded: {(1 + Rb) ** T:.4f}")
anchor("A17-14", f"{1.000625**T:.4f}")
anchor("A17-37", f"0.062505%: {1.00062505**T:.4f}; 0.06251%: {1.0006251**T:.4f}")
c4p, c4u = (1 + 4 * 0.0006251) ** T, (1 + 4 * Rb) ** T
assert f"{c4p / 1e6:.1f}" == f"{c4u / 1e6:.1f}" == "2.2"
has("case at f = 4", "2.2 million times the start at $f=4$")
anchor("A17-11", f"from 0.06251%: {c4p:.6g}; unrounded: {c4u:.6g}")


def gbar(f: float) -> float:
    return float(np.log1p(f * R).mean())


def sdl(f: float) -> float:
    return float(np.log1p(f * R).std())


def gbar_d(f: float) -> float:
    return float((R / (1 + f * R)).mean())


i_min = int(R.argmin())
fmax = 1 / abs(float(R[i_min]))
fstar = float(optimize.brentq(gbar_d, 0.0, fmax - 1e-6))
fzero = float(optimize.brentq(gbar, fstar, fmax - 1e-9))
w_star = exp(T * gbar(fstar))
chk("f*", fstar, ".2f", "4.14")
chk("f*, four decimals (E5)", fstar, ".4f", "4.1381")
chk("wealth at f*", w_star, ",.0f", "2,147")
chk("zero growth", fzero, ".2f", "8.04")
anchor("A17-12", f"f* {fstar:.6f}; exp(T gbar(f*)) {w_star:.2f}")
anchor("A17-13", f"{fzero:.6f}")
assert abs(gbar(1) - rb) < 1e-15

# ====================================================================== Section 2
avgs = [Fraction(a + b, 2) for a in (Fraction(2), Fraction(-1)) for b in (Fraction(2), Fraction(-1))]
assert sorted(avgs) == [Fraction(-1), Fraction(1, 2), Fraction(1, 2), Fraction(2)]
mean2 = sum(avgs) / 4
var2 = sum((a - mean2) ** 2 for a in avgs) / 4
var1 = (Fraction(3, 2) ** 2 + Fraction(3, 2) ** 2) / 2
assert (mean2, var2, var1) == (Fraction(1, 2), Fraction(9, 8), Fraction(9, 4))
chk("two trades: variance (%^2)", float(var2), ".3f", "1.125")
chk("one trade: variance (%^2)", float(var1), ".2f", "2.25")
has("two trades: averages", "2%, 0.5%, 0.5% or −1%".replace("\u2212", "-"))
anchor("A17-18", "averages 2%, 0.5%, 0.5%, -1%; mean 0.5%; variance "
       f"{float(var2):.4f} %^2; one trade {float(var1):.4f} %^2")
# E1: LM3's bet, sigma = 1.5% (lm03.md: s^2 = 0.000225), mean 0.5%
assert abs(sqrt(0.000225) - 0.015) < 1e-15
chk("E1: n = 100", 1.5 / sqrt(100), ".2f", "0.15")
chk("E1: n = 10,000", 1.5 / sqrt(10000), ".3f", "0.015")
n36 = math.ceil((1.5 / 0.25) ** 2)
assert n36 == 36 and 1.5 / sqrt(35) > 0.25 >= 1.5 / sqrt(36)
chk("E1: smallest n", n36, "d", "36")
anchor("A17-63", f"{1.5 / sqrt(100):g}%, {1.5 / sqrt(10000):g}%; n = {n36}; edge 0.5% (lm03.md:363)")
chk("KC 2: four independent days", 1.2 / sqrt(4), ".1f", "0.6")
anchor("A17-23", f"{1.2 / sqrt(4):.1f}%; {1.2:.1f}%")

# ====================================================================== Section 3


def coin_tail(n: int) -> float:
    """Exact Pr(|j/n - 1/2| >= 0.1), Bin(n, 1/2), compared in integers: |10 j - 5 n| >= n."""
    return float(Fraction(sum(comb(n, j) for j in range(n + 1) if abs(10 * j - 5 * n) >= n), 2**n))


ct = {n: coin_tail(n) for n in (10, 100, 1000)}
chk("coin, n = 10", ct[10], ".4f", "0.7539")
chk("coin, n = 100", ct[100], ".5f", "0.05689")
sci("coin, n = 1,000", ct[1000], 1, "2.7 -10")
for n, p in ((10, "2.5"), (100, "0.25"), (1000, "0.025")):
    assert abs(0.25 / n / 0.1**2 - 25 / n) < 1e-15
    chk(f"Chebyshev 25/n, n = {n}", 25 / n, "g", p)
anchor("A17-19", "; ".join(f"n={n}: {ct[n]:.6g} vs {25 / n:g}" for n in (10, 100, 1000)))
e2 = 0.25 / (0.01**2 * 0.05)
chk("E2", e2, ",.0f", "50,000")
anchor("A17-64", f"{e2:.0f}")
run_up = np.cumsum(R > EPS) / np.arange(1, T + 1)
m1, m5, m10, m40 = round(A), round(5 * A), round(10 * A), round(40 * A)
assert (m1, m5, m10, m40) == (246, 1231, 2461, 9845)
chk("running up share, n = 246", run_up[245], ".4f", "0.5163")
chk("running up share, n = 1,231", run_up[m5 - 1], ".4f", "0.5378")
p_hat = up_x / T
chk("p hat", p_hat, ".4f", "0.5480")
chk("X2 band half-width at T", 2 * sqrt(p_hat * (1 - p_hat) / T), ".4f", "0.0130")
anchor("A17-38", "; ".join(f"n={n}: {run_up[n - 1]:.5f}" for n in (246, m5, T)))
anchor("A17-39", f"{2 * sqrt(p_hat * (1 - p_hat) / T):.6f}")
chk("KC 3: count sd, n = 100", sqrt(100) / 2, "g", "5")
chk("KC 3: count sd, n = 10,000", sqrt(10000) / 2, "g", "50")
chk("KC 3: frequency sd, n = 100", 0.5 / sqrt(100), ".2f", "0.05")
chk("KC 3: frequency sd, n = 10,000", 0.5 / sqrt(10000), ".3f", "0.005")
anchor("A17-24", f"{sqrt(100) / 2:g}, {sqrt(10000) / 2:g}; {0.5 / sqrt(100):g}, {0.5 / sqrt(10000):g}")

# ====================================================================== Section 4
ew10 = Fraction(5, 4) ** 10
paths = [comb(10, j) for j in range(11)]
prob = [Fraction(c, 1024) for c in paths]
wealth = [Fraction(2) ** (2 * j - 10) for j in range(11)]
contrib = [p * w for p, w in zip(prob, wealth, strict=True)]
assert sum(contrib) == ew10 and sum(paths) == 1024
chk("E3: E W10", float(ew10), ".4f", "9.3132")
same("E3: Pr(W10 = W0)", str(Fraction(comb(10, 5), 1024)), "63/256")
chk("E3: Pr(W10 = W0), decimal", float(prob[5]), ".4f", "0.2461")
same("E3: Pr(W10 <= W0) numerator", f"{sum(paths[:6])}/1,024", "638/1,024")
assert sum(paths[:6]) == sum(paths[5:])
above = [j for j in range(11) if wealth[j] > ew10]
assert above == [7, 8, 9, 10] and wealth[7] == 16 and wealth[6] == 4
same("E3: Pr(W10 > E W10)", str(sum(prob[7:])), "11/64")
chk("E3: Pr(W10 > E W10), decimal", float(sum(prob[7:])), ".4f", "0.1719")
chk("E3: contribution of j >= 7", float(sum(contrib[7:])), ".4f", "8.1875")
chk("E3: share of the mean", float(100 * sum(contrib[7:]) / ew10), ".1f", "87.9")
same("E3: Pr(W10 < W0)", str(sum(prob[:5])), "193/512")
chk("E3: Pr(W10 < W0), decimal", float(sum(prob[:5])), ".4f", "0.3770")
# 100 rounds: W_100 / W0 = 2^(2j - 100) exceeds 1.25^100 exactly when j >= 67
j100 = next(j for j in range(101) if Fraction(2) ** (2 * j - 100) > Fraction(5, 4) ** 100)
assert j100 == 67
sci("E3: E W100", 1.25**100, 2, "4.91 9")
p_above_100 = Fraction(sum(comb(100, j) for j in range(j100, 101)), 2**100)
p_below_100 = Fraction(sum(comb(100, j) for j in range(50)), 2**100)
chk("E3: Pr(W100 > E W100)", float(p_above_100), ".5f", "0.00044")
chk("E3: Pr(W100 < W0)", float(p_below_100), ".4f", "0.4602")
anchor("A17-66", f"E W {1.25**100:.4e}; Pr(j>={j100}) {float(p_above_100):.4e}; Pr(j<=49) {float(p_below_100):.4f}")
anchor("A17-40", f"paths {2**10}; E W10 {float(ew10):.5f}; Pr(j>=7) {sum(prob[7:])} = {float(sum(prob[7:])):.6f}; "
       f"contribution {float(sum(contrib[7:])):.4f} = {float(sum(contrib[7:]) / ew10):.4%}")
anchor("A17-65", f"E W10 {float(ew10):.5f}; Pr(W=1) {prob[5]} = {float(prob[5]):.4f}; Pr(W>EW) 11/64 = "
       f"{11 / 64:.4f}; share {float(sum(contrib[7:]) / ew10):.4%}; Pr(W<1) {sum(prob[:5])} = {float(sum(prob[:5])):.4f}")


def wtxt(w: Fraction) -> str:
    return f"1/{w.denominator:,}" if w < 1 else f"{int(w):,}"


rounded_contrib = []
for j in range(11):
    pr, ctb = f"{float(prob[j]):.4f}", f"{float(contrib[j]):.4f}"
    assert not tie(float(prob[j]), ".4f") and not tie(float(contrib[j]), ".4f")
    rounded_contrib.append(float(ctb))
    has(f"X3 row j = {j}", f"| {j} | {wtxt(wealth[j])} | {paths[j]:,} | {pr} | {ctb} |")
assert f"{sum(rounded_contrib):.4f}" == "9.3132", "X3: the printed contributions do not add up to the printed total"
has("X3 total row", "| Total | | 1,024 | | 9.3132 |")
# Peters (2019): +50% / -40%
chk("Peters: expected factor", 0.5 * 1.5 + 0.5 * 0.6, ".2f", "1.05")
chk("Peters: (1/2) ln 0.9", 0.5 * log(0.9), ".4f", "-0.0527")
chk("Peters: sqrt(0.9)", sqrt(0.9), ".3f", "0.949")
assert abs(0.5 * log(1.5) + 0.5 * log(0.6) - 0.5 * log(0.9)) < 1e-15
anchor("A17-67", f"1.05; {0.5 * log(0.9):.5f}; {sqrt(0.9):.5f}")

# E4: the case resolved
delta = log(1 + Rb) - rb
chk("E4: delta (bp)", 1e4 * delta, ".4f", "0.7316")
chk("E4: delta from the six-figure printed means (bp)", 1e4 * (log(1.000625051) - 0.000551696), ".4f", "0.7316")
assert f"{1e4 * (log(1.00062505) - 0.00055170):.4f}" != "0.7316", "the six figures would no longer be needed"
anchor("A17-15", f"{1e4 * delta:.5f} bp")
anchor("A17-68", f"Rbar {Rb:.7%}, rbar {rb:.7%}; gap from 6 s.f. {1e4 * (log(1.000625051) - 0.000551696):.5f} bp; "
       f"from 0.062505%, 0.055170%: {1e4 * (log(1.00062505) - 0.00055170):.5f} bp")
chk("E4: T delta from printed", 5849 * 0.7316e-4, ".4f", "0.4279")
chk("E4: T delta", T * delta, ".4f", "0.4279")
chk("E4: exp(0.4279)", exp(0.4279), ".3f", "1.534")
chk("E4: 38.66 / 25.20", 38.66 / 25.20, ".3f", "1.534")
chk("E4: realized e^(T rbar)", exp(T * rb), ".2f", "25.20")
anchor("A17-16", f"T*delta {T * delta:.5f}; exp {exp(T * delta):.5f}")
anchor("A17-36", f"{G:.4f}; {(1 + Rb) ** T:.4f}; {exp(T * rb):.4f}")
z_case_p = sqrt(5849) * 0.7316e-4 / 0.012107
z_case = sqrt(T) * delta / sr
chk("E4: z from printed inputs", z_case_p, ".3f", "0.462")
chk("E4: z", z_case, ".3f", "0.462")
chk("E4: Pr(W > EW) from printed z", float(Phi(-0.462)), ".2f", "0.32")
chk("E4: Pr(W > EW)", float(stats.norm.sf(z_case)), ".2f", "0.32")
need_p = (1.645 * 0.012107 / 0.7316e-4) ** 2
need = (Z95 * sr / delta) ** 2
assert round(need_p, -3) == round(need, -3) == 74000 and round(need_p / 246.12, -2) == round(need / A, -2) == 300
has("E4: days for 5%", "about 74,000 days, or 300 years")
chk("Phi^{-1}(0.95)", Z95, ".3f", "1.645")
anchor("A17-46", f"{Z95:.6f}")
anchor("A17-69", f"{need:.0f} days = {need / A:.2f} years; from 1.645, 1.2107%, 0.7316 bp: {need_p:.0f} days = "
       f"{need_p / 246.12:.2f} years")
chk("E4: Chebyshev's bound from printed", 0.012107**2 / (5849 * 0.7316e-4**2), ".2f", "4.68")
chk("E4: Chebyshev's bound", sr**2 / (T * delta**2), ".2f", "4.68")
anchor("A17-70", f"{sr**2 / (T * delta**2):.4f}; from printed {0.012107**2 / (T * 0.7316e-4**2):.4f}")
z1, p1 = sqrt(T) * delta / sr, float(stats.norm.sf(sqrt(T) * delta / sr))

# E5: leverage
lev_rows = {1: ("25.20", "13.58", "38.66"), 2: ("267.7", "23.52", "1,491"), 4: ("2,127.8", "32.24", "2.20 6"),
            6: ("405.6", "25.27", "3.23 9"), 8: ("1.175", "0.68", "4.68 12")}
lev_fmt = {1: ".2f", 2: ".1f", 4: ",.1f", 6: ".1f", 8: ".3f"}
lev_anchor = []
for f, (pw, pg, pm) in lev_rows.items():
    w = exp(T * gbar(f))
    chk(f"E5: W_T at f = {f}", w, lev_fmt[f], pw)
    chk(f"E5: A gbar at f = {f}", 100 * A * gbar(f), ".2f", pg)
    chk(f"E5: A gbar from the printed W_T at f = {f}", 100 * log(float(pw.replace(",", ""))) / years, ".2f", pg)
    chk(f"E5: A gbar from the printed W_T and 23.7645 at f = {f}", 100 * log(float(pw.replace(",", ""))) / 23.7645,
        ".2f", pg)
    mp = (1 + f * Rb) ** T
    if " " in pm:
        mant, ex = pm.split()
        assert f"{mp:.2e}" == f"{mant}e+{int(ex):02d}" and f"{(1 + f * 0.00062505) ** T:.2e}" == f"{mant}e+{int(ex):02d}"
        mant_tex = f"${mant}\\times10^{{{ex}}}$"
        mp_txt = mant_tex
    else:
        assert format(mp, ",.0f" if f > 1 else ".2f") == pm == format((1 + f * 0.00062505) ** T, ",.0f" if f > 1 else ".2f")
        mp_txt = pm
    has(f"E5 row f = {f}", f"| {f} | {pw} | {pg}% | {mp_txt} |")
    lev_anchor.append(f"f={f}: W {w:.6g}, A gbar {A * gbar(f):.4%} (ln of printed W / years "
                      f"{log(float(f'{w:.4g}')) / years:.4%}), mean path {mp:.4e}"
                      f" (from 0.062505% {(1 + f * 0.00062505) ** T:.4e})")
anchor("A17-71", "; ".join(lev_anchor))
chk("E5: A gbar(f*)", 100 * A * gbar(fstar), ".2f", "32.28")
chk("E5: wealth at f* / G", w_star / G, ".0f", "85")
chk("E5: printed 2,147 / 25.20", 2147 / 25.20, ".0f", "85")
chk("E5: zero growth / f*", fzero / fstar, ".2f", "1.94")
chk("E5: printed 8.04 / 4.1381", 8.04 / 4.1381, ".2f", "1.94")
anchor("A17-72", f"f* {fstar:.6f}; A gbar(f*) {A * gbar(fstar):.4%}; W {w_star:.2f}; /G {w_star / G:.3f}; "
       f"zero growth {fzero:.6f}; /f* {fzero / fstar:.4f}")
d_star = log(1 + fstar * Rb) - gbar(fstar)
s_star = sdl(fstar)
chk("E5: delta(f*) (bp)", 1e4 * d_star, ".2f", "12.72")
chk("E5: s_r(f*) (%)", 100 * s_star, ".3f", "5.079")
z_star = sqrt(T) * d_star / s_star
chk("E5: z at f*", z_star, ".3f", "1.915")
chk("E5: z at f* from printed inputs", sqrt(5849) * 12.72e-4 / 0.05079, ".3f", "1.915")
chk("E5: Pr(W > EW) at f*", float(stats.norm.sf(z_star)), ".3f", "0.028")
chk("E5: Pr(W > EW) at f* from printed z", float(Phi(-1.915)), ".3f", "0.028")
anchor("A17-73", f"delta(f*) {1e4 * d_star:.4f} bp; s_r(f*) {s_star:.5%}; z {z_star:.5f}; Pr {float(stats.norm.sf(z_star)):.5f}")
anchor("A17-17", f"f=1: {p1:.5f}; f*: {float(stats.norm.sf(z_star)):.5f}")
wl = np.concatenate([[1.0], np.exp(np.cumsum(np.log1p(fstar * R)))])
dd = 1 - wl / np.maximum.accumulate(wl)
chk("E5: drawdown at f*", 100 * dd.max(), ".1f", "98.5")
same("E5: date of the trough", dates_all[int(dd.argmax())], "2008-11-20", in_md=False)
has("E5: trough date in words", "20 November 2008")
anchor("A17-74", f"{dd.max():.4%} at {dates_all[int(dd.argmax())]}")
# X4
chk("X4: A gbar(1) (LM14's)", 100 * A * rb, ".2f", "13.58")
chk("X4: A ln(1 + Rbar)", 100 * A * log(1 + Rb), ".2f", "15.38")
chk("X4: domain edge", fmax, ".2f", "10.31")
chk("X4: worst day (%)", 100 * float(R[i_min]), ".4f", "-9.6997")
same("X4: worst day's date", dates[i_min], "2025-04-07", in_md=False)
anchor("A17-41", f"A gbar(1) {A * gbar(1):.4%}; A ln(1+Rbar) {A * log(1 + Rb):.4%}; f* {fstar:.4f}, "
       f"A gbar(f*) {A * gbar(fstar):.4%}; zero growth {fzero:.4f}")
anchor("A17-42", f"1/abs(R_(1)) {fmax:.4f}; R_(1) {R[i_min]:.4%} on {dates[i_min]}")
# pitfall: level spread
chk("pitfall: s_r sqrt(T)", sr * sqrt(T), ".4f", "0.9259")
chk("pitfall: s_r sqrt(T) from printed s_r", 0.012107 * sqrt(5849), ".4f", "0.9259")
chk("pitfall: exp(0.9259)", exp(0.9259), ".2f", "2.52")
anchor("A17-92", f"{sr * sqrt(T):.6f}; exp {exp(sr * sqrt(T)):.4f}")
# KC 4: LM3's bet over 1,000 trades
chk("KC 4: mean path", 1.005**1000, ".2f", "146.58")
chk("KC 4: median path", exp(1000 * 0.0048761), ".2f", "131.12")
chk("KC 4: LM3's g (lm03.md prints 0.48761%)", 100 * (0.5 * log(1.02) + 0.5 * log(0.99)), ".5f", "0.48761")
anchor("A17-25", f"{1.005**1000:.4f}; {exp(1000 * 0.0048761):.4f}")
anchor("A17-26", f"{0.5 * log(1.02) + 0.5 * log(0.99):.7%} (printed 0.48761%, lm03.md:363)")

# ====================================================================== Section 5
gs = 0.5 * log(1.5) + 0.5 * log(0.75)
sg = 0.5 * (log(1.5) - log(0.75))
thr = log(4 / 3) / log(2)
assert abs(sg - log(2) / 2) < 1e-15
chk("g* (LM4: 5.889%)", 100 * gs, ".3f", "5.889")
chk("g*, seven decimals", gs, ".7f", "0.0588915")
chk("sigma_r = ln2/2", sg, ".7f", "0.3465736")
chk("threshold ln(4/3)/ln 2", thr, ".7f", "0.4150375")
chk("threshold as LM4 prints it", thr, ".5f", "0.41504")
anchor("A17-75", f"{thr:.7f} (printed 0.41504, lm04.md:366)")


def coin(n: int) -> tuple[int, float, float, float, float]:
    """LM4's coin at f* = 25 after n trades: largest losing j, exact, normal, corrected, z."""
    jmax = math.ceil(thr * n) - 1
    assert jmax < thr * n < jmax + 1
    z = -gs * sqrt(n) / sg
    return (jmax, float(stats.binom.cdf(jmax, n, 0.5)), float(Phi(z)),
            float(Phi((jmax + 0.5 - n / 2) / (sqrt(n) / 2))), z)


c100, c10, c400 = coin(100), coin(10), coin(400)
assert c100[0] == 41 and c10[0] == 4 and c400[0] == 166
chk("E6: exact, n = 100", c100[1], ".5f", "0.04431")
chk("E6: z, n = 100", c100[4], ".5f", "-1.69925")
assert abs(c100[4] - (thr * 100 - 50) / 5) < 1e-12
chk("E6: normal, n = 100", c100[2], ".5f", "0.04464")
chk("E6: normal from the printed z", float(Phi(-1.69925)), ".5f", "0.04464")
assert f"{float(Phi(-1.6993)):.5f}" != "0.04464", "five figures of z would do"
sci("E6: distance above the rounding boundary 0.044635", c100[2] - 0.044635, 1, "1.0 -6")
chk("E6: corrected, n = 100", c100[3], ".5f", "0.04457")
chk("E6: Phi(-1.7)", float(Phi(-1.7)), ".5f", "0.04457")
chk("E6: exact, n = 10", c10[1], ".5f", "0.37695")
chk("E6: normal, n = 10", c10[2], ".5f", "0.29551")
chk("E6: corrected, n = 10", c10[3], ".5f", "0.37591")
anchor("A17-44", f"exact {c100[1]:.6f}; normal {c100[2]:.7f}; cc {c100[3]:.6f}")
anchor("A17-76", f"g* {gs:.7f}; sigma_r {sg:.7f}; z {c100[4]:.6f}; n=100 exact {c100[1]:.6f}, normal {c100[2]:.7f}, "
       f"cc {c100[3]:.6f}; normal minus the boundary 0.044635 {c100[2] - 0.044635:.2e}; n=10 exact {c10[1]:.6f}, "
       f"normal {c10[2]:.6f}, cc {c10[3]:.6f}")
anchor("A17-43", "f* = 25, g* = 5.889% (printed in lm04.md:345)")
e7 = 1.96**2 * 0.25 / 0.01**2
chk("E7", e7, ",.0f", "9,604")
anchor("A17-77", f"{e7:.2f}")
# pitfall and Problem 6: n = 400
chk("P6: exact", c400[1], ".6f", "0.000394")
chk("P6: z", c400[4], ".4f", "-3.3985")
chk("P6: normal", c400[2], ".6f", "0.000339")
chk("P6: normal from printed z", float(Phi(-3.3985)), ".6f", "0.000339")
chk("P6: corrected", c400[3], ".6f", "0.000404")
chk("P6: Phi(-3.35)", float(Phi(-3.35)), ".6f", "0.000404")
chk("P6: threshold at n = 400", thr * 400, ".3f", "166.015")
chk("P6: threshold at n = 100", thr * 100, ".3f", "41.504")
chk("P6: absolute error from printed values", 0.000394 - 0.000339, ".6f", "0.000055")
chk("P6: absolute error", c400[1] - c400[2], ".6f", "0.000055")
chk("P6: relative error at n = 400 (% low)", -100 * (c400[2] / c400[1] - 1), ".0f", "14")
chk("P6: relative error at n = 100 (% high)", 100 * (c100[2] / c100[1] - 1), ".1f", "0.7")
anchor("A17-87", f"exact {c400[1]:.6f}; z {c400[4]:.4f}, normal {c400[2]:.6f}; cc {c400[3]:.6f}; "
       f"relative errors n=400 {c400[2] / c400[1] - 1:+.2%}, n=100 {c100[2] / c100[1] - 1:+.2%}")
# KC 5
chk("KC 5: exact Pr(j >= 60)", 100 * float(stats.binom.sf(59, 100, 0.5)), ".2f", "2.84")
chk("KC 5: corrected", 100 * float(stats.norm.sf((59.5 - 50) / 5)), ".2f", "2.87")
anchor("A17-27", f"exact {float(stats.binom.sf(59, 100, 0.5)):.6f}; cc {float(stats.norm.sf(1.9)):.6f}")

# ====================================================================== Section 6


def row(m: int) -> tuple[float, float, float, float, float, float]:
    """Median, mean path, 5% and 95% quantiles, Pr(W < W0), Pr(W > EW) of the iid model at f = 1."""
    return (exp(m * rb), (1 + Rb) ** m, exp(m * rb - Z95 * sr * sqrt(m)), exp(m * rb + Z95 * sr * sqrt(m)),
            float(Phi(-rb * sqrt(m) / sr)), float(stats.norm.sf(sqrt(m) * delta / sr)))


def row_p(m: int) -> tuple[float, float, float, float, float, float]:
    """The same from the printed inputs 0.062505%, 0.055170%, 1.2107%, 0.7316 bp and 1.645."""
    gp, sp = 0.00055170, 0.012107
    return (exp(m * gp), 1.00062505**m, exp(m * gp - 1.645 * sp * sqrt(m)), exp(m * gp + 1.645 * sp * sqrt(m)),
            float(Phi(-gp * sqrt(m) / sp)), float(stats.norm.sf(sqrt(m) * 0.7316e-4 / sp)))


x6 = {246: (".4f", ".4f", ".4f", ".4f", ".2f", ".1f"), 2461: (".2f", ".2f", ".2f", ".2f", ".2f", ".1f"),
      5849: (".2f", ".2f", ".2f", ".1f", ".2f", ".1f")}
x6_label = {246: "One year, 246", 2461: "Ten years, 2,461", 5849: "Sample, 5,849"}
for m, fmts in x6.items():
    u, p = row(m), row_p(m)
    cells = []
    for k, (vu, vp, ft) in enumerate(zip(u, p, fmts, strict=True)):
        scale = 100 if k >= 4 else 1
        cu, cp = format(scale * vu, ft), format(scale * vp, ft)
        assert cu == cp, ("X6 differs between unrounded and printed inputs", m, k, cu, cp)
        assert not tie(scale * vu, ft) and not tie(scale * vp, ft), ("X6 tie", m, k)
        cells.append(cu + ("%" if k >= 4 else ""))
    has(f"X6 row m = {m}", f"| {x6_label[m]} | " + " | ".join(cells) + " |")
fp = "median {:.5f}; mean path {:.5f}; 5% {:.5f}; 95% {:.5f}; Pr(W<W0) {:.6f}; Pr(W>EW) {:.5f}"
anchor("A17-47", fp.format(*row(m1)))
anchor("A17-48", fp.format(*row(m10)))
anchor("A17-49", fp.format(*row(T)))
anchor("A17-29", f"{m1} (A = {A:.4f})")
anchor("A17-45", f"{m10} (10A = {10 * A:.4f})")
anchor("A17-07", f"{m5} (5A = {5 * A:.4f})")
anchor("A17-59", f"{m40} (40A = {40 * A:.4f})")
chk("one year m", m1, "d", "246")
chk("ten years m", m10, ",", "2,461")
chk("five years m", m5, ",", "1,231")
gp, sp = 0.00055170, 0.012107
anchor("A17-52", f"rbar {rb:.6%}, s_r {sr:.5%}; from 0.055170%, 1.2107%, 1.645: ten-year 5% "
       f"{exp(m10 * gp - 1.645 * sp * sqrt(m10)):.4f}, sample 5% {exp(T * gp - 1.645 * sp * sqrt(T)):.4f}, "
       f"sample 95% {exp(T * gp + 1.645 * sp * sqrt(T)):.2f}")
# E8
chk("E8: z, one year", gp * sqrt(246) / sp, ".4f", "0.7147")
chk("E8: z, one year (unrounded)", rb * sqrt(246) / sr, ".4f", "0.7147")
chk("E8: loss, one year", 100 * row(246)[4], ".2f", "23.74")
chk("E8: loss from printed z", 100 * float(Phi(-0.7147)), ".2f", "23.74")
chk("E8: z, ten years", gp * sqrt(2461) / sp, ".3f", "2.261")
chk("E8: z, ten years (unrounded)", rb * sqrt(2461) / sr, ".3f", "2.261")
chk("E8: loss, ten years", 100 * row(2461)[4], ".2f", "1.19")
chk("E8: loss from printed z, ten years", 100 * float(Phi(-2.261)), ".2f", "1.19")
anchor("A17-79", f"one year z {rb * sqrt(m1) / sr:.5f}; ten years z {rb * sqrt(m10) / sr:.5f}; "
       f"from printed inputs {gp * sqrt(m1) / sp:.5f}, {gp * sqrt(m10) / sp:.5f}")
anchor("A17-31", f"{row(m1)[4]:.6f}")
# calendar years 2003-2025 (2003 from its first close); exact arithmetic on the closes
year_end: dict[str, int] = {}
for i, d in enumerate(dates_all):
    year_end[d[:4]] = i
loss_years, ann = [], []
for y in range(2003, 2026):
    base = 0 if y == 2003 else year_end[str(y - 1)]
    g_y = trf[year_end[str(y)]] / trf[base]
    ann.append(log(float(g_y)))
    if g_y < 1:
        loss_years.append(y)
assert loss_years == [2008, 2011, 2015, 2018, 2022]
chk("losing years", len(loss_years), "d", "5")
has("losing years listed", "(2008, 2011, 2015, 2018, 2022)")
has("23 calendar years", "5 of the 23 calendar years 2003–2025")
anchor("A17-50", f"{len(loss_years)} of 23: " + ", ".join(
    f"{y} {float(trf[year_end[str(y)]] / trf[0 if y == 2003 else year_end[str(y - 1)]] - 1):.2%}" for y in loss_years))
in_win = np.array([d <= "2025-12-31" for d in dates])
r_w = r[in_win]
rb_w, sr_w = float(r_w.mean()), float(r_w.std())
p_w = float(Phi(-rb_w * sqrt(m1) / sr_w))
chk("E8: returns 2003-2025", len(r_w), ",", "5,664")
chk("E8: refitted daily model, losing-year chance", 100 * p_w, ".2f", "26.54")
chk("E8: expected losing years", 23 * p_w, ".2f", "6.10")
chk("E8: expected losing years from printed 26.54%", 23 * 0.2654, ".2f", "6.10")
la = np.array(ann)
chk("E8: LM15's fit, Pr(G < 1)", 100 * float(Phi(-la.mean() / la.std())), ".1f", "30.0")
chk("E8: mean annual log return (LM15)", 100 * la.mean(), ".3f", "11.646")
chk("E8: sd of annual log returns (LM15, divisor 23)", 100 * la.std(), ".3f", "22.207")
chk("E8: 246 rbar' (2003-2025)", 100 * m1 * rb_w, ".3f", "11.634")
chk("E8: sqrt(246) s_r' (2003-2025)", 100 * sqrt(m1) * sr_w, ".3f", "18.563")
chk("E8: Phi(-11.634/18.563)", 100 * float(Phi(-11.634 / 18.563)), ".2f", "26.54")
anchor("A17-51", f"{len(r_w)} returns to {dates[int(np.flatnonzero(in_win)[-1])]}: Pr(W_246 < W0) {p_w:.6f}; "
       f"23 x = {23 * p_w:.4f}")
anchor("A17-80", f"annual log returns mean {la.mean():.5f}, sd {la.std():.5f}; Pr(G<1) "
       f"{float(Phi(-la.mean() / la.std())):.5f}; daily model on 2003-2025: 246 rbar {m1 * rb_w:.5f}, "
       f"sqrt(246) s_r {sqrt(m1) * sr_w:.5f}")
i25 = year_end["2025"]
rise26 = trf[-1] / trf[i25] - 1
chk("E8: the 2026 rise", 100 * float(rise26), ".1f", "73.0")
anchor("A17-93", f"{dates_all[i25]} {float(trf[i25]):.2f} -> {dates_all[-1]} {float(trf[-1]):.2f}: {float(rise26):.4%}")
# LM5's printed lognormal (lm05.md, example "lognormal")
lm05 = (ROOT / "src" / "lm05.md").read_text(encoding="utf-8")
assert "$e^{0.19308}=1.2130$" in lm05 and "=1.2358$" in lm05, "LM5 no longer prints 1.2130 and 1.2358"
has("LM5's median and mean", "median growth factor 1.2130 and mean 1.2358")
anchor("A17-20", "1.2130; 1.2358 (printed in lm05.md:521)")
assert "243.1" in lm05
has("LM5's year", "about 243 daily log returns")
# widget: five years
chk("five-year loss (widget, LM18's case)", 100 * float(Phi(-rb * sqrt(m5) / sr)), ".2f", "5.49")
anchor("A17-60", f"{float(Phi(-rb * sqrt(m5) / sr)):.6f}")
anchor("A17-61", f"f=1: {gbar(1):.8f}, {sdl(1):.8f}; f=2: {gbar(2):.8f}, {sdl(2):.8f}")
anchor("A17-62", f"f=1: lognormal {exp(T * (gbar(1) + sdl(1) ** 2 / 2)):.4f}, iid {(1 + Rb) ** T:.4f}; "
       f"f=8: lognormal {exp(T * (gbar(8) + sdl(8) ** 2 / 2)):.4e}, iid {(1 + 8 * Rb) ** T:.4e}")
# KC 6: f = 2
chk("KC 6: gbar(2) (%)", 100 * gbar(2), ".6f", "0.095571")
chk("KC 6: s_r(2) (%)", 100 * sdl(2), ".4f", "2.4288")
chk("KC 6: z from printed inputs", 0.00095571 * sqrt(246) / 0.024288, ".4f", "0.6172")
chk("KC 6: z", gbar(2) * sqrt(246) / sdl(2), ".4f", "0.6172")
chk("KC 6: Pr from printed z", 100 * float(Phi(-0.6172)), ".2f", "26.86")
chk("KC 6: Pr", 100 * float(Phi(-gbar(2) * sqrt(246) / sdl(2))), ".2f", "26.86")
anchor("A17-28", f"gbar(2) {gbar(2):.6%}; s_r(2) {sdl(2):.5%}")
z2, z2p = gbar(2) * sqrt(m1) / sdl(2), 0.00095571 * sqrt(m1) / 0.024288
anchor("A17-30", f"z {z2:.5f}, Pr {float(Phi(-z2)):.5f}; printed inputs z {z2p:.5f}, Pr {float(Phi(-z2p)):.5f}")

# ====================================================================== Section 7
k1 = kurt_ex(r)
assert abs(k1 - float(stats.kurtosis(r))) < 1e-12
chk("daily excess kurtosis of r", k1, ".3f", "5.428")
chk("daily excess kurtosis of r, two decimals", k1, ".2f", "5.43")
anchor("A17-32", f"{k1:.5f}")
chk("E9: 5.428/5", 5.428 / 5, ".2f", "1.09")
chk("E9: 5.428/20", 5.428 / 20, ".2f", "0.27")
ms = (1, 2, 5, 10, 20, 60)
km = {m: kurt_ex(window_sums(r, m)) for m in ms}
for m, p in zip(ms, ("5.43", "5.04", "3.63", "3.02", "2.29", "3.20"), strict=True):
    assert abs(km[m] - float(stats.kurtosis(window_sums(r, m)))) < 1e-12
    if m == 2:
        assert not tie(km[m], ".2f") and f"{km[m]:.2f}" == p    # chart only
        continue
    chk(f"X7: overlapping {m}-day sums", km[m], ".2f", p)
anchor("A17-53", ", ".join(f"m={m}: {km[m]:.5f}" for m in ms))
anchor("A17-34", f"{km[10]:.4f}")
for m, p in zip(ms, ("5.428", "2.714", "1.086", "0.543", "0.271", "0.090"), strict=True):
    assert f"{5.428 / m:.3f}" == p and not tie(5.428 / m, ".3f")
for p in ("1.086", "0.543", "0.271", "0.090"):
    chk(f"iid 5.428/m printed {p}", float(p), ".3f", p)
anchor("A17-54", ", ".join(f"{5.428 / m:.5f}" for m in ms))
chk("X7: windows of 20 days", T - 20 + 1, ",", "5,830")
r_abs = np.abs(r)
chk("E9: corr(r_t, r_t+1)", corr(r[:-1], r[1:]), ".3f", "0.039")
chk("E9: corr(|r_t|, |r_t+1|)", corr(r_abs[:-1], r_abs[1:]), ".3f", "0.161")
chk("E9: corr(|r_t|, |r_t+20|)", corr(r_abs[:-20], r_abs[20:]), ".3f", "0.123")
anchor("A17-81", f"r lag 1 {corr(r[:-1], r[1:]):.4f}; abs(r) lag 1 {corr(r_abs[:-1], r_abs[1:]):.4f}; "
       f"abs(r) lag 20 {corr(r_abs[:-20], r_abs[20:]):.4f}")
k_daily_R = kurt_ex(R)
chk("daily excess kurtosis of R (LM14's)", k_daily_R, ".2f", "5.27")
anchor("A17-55", f"{k_daily_R:.4f}")
nw20, nw60 = T // 20, T // 60
k20_first = kurt_ex(r[: nw20 * 20].reshape(nw20, 20).sum(axis=1))
k20_off = [kurt_ex(r[o: o + (T - o) // 20 * 20].reshape(-1, 20).sum(axis=1)) for o in range(20)]
k60_first = kurt_ex(r[: nw60 * 60].reshape(nw60, 60).sum(axis=1))
k60_off = [kurt_ex(r[o: o + (T - o) // 60 * 60].reshape(-1, 60).sum(axis=1)) for o in range(60)]
chk("X7: non-overlapping 20-day windows", nw20, "d", "292")
chk("X7: 20-day from the first return", k20_first, ".2f", "2.40")
chk("X7: 20-day, smallest over offsets", min(k20_off), ".2f", "0.69")
chk("X7: 20-day, largest over offsets", max(k20_off), ".2f", "4.49")
chk("X7: non-overlapping 60-day windows", nw60, "d", "97")
chk("X7: 60-day from the first return", k60_first, ".2f", "2.76")
chk("X7: 60-day, smallest over offsets", min(k60_off), ".2f", "0.42")
chk("X7: 60-day, largest over offsets", max(k60_off), ".2f", "7.22")
anchor("A17-56", f"first return {k20_first:.4f} ({nw20} windows); offsets 0-19 {min(k20_off):.4f} to {max(k20_off):.4f}")
anchor("A17-94", f"first return {k60_first:.4f} ({nw60} windows); offsets 0-59 {min(k60_off):.4f} to {max(k60_off):.4f}")
pre = np.array([d < LIMIT_SWITCH for d in dates])
reg = {}
for lab, x in (("before", r[pre]), ("from", r[~pre])):
    reg[lab] = (len(x), kurt_ex(x), kurt_ex(window_sums(x, 20)))
chk("X7: daily kurtosis before June 2015", reg["before"][1], ".2f", "3.44")
chk("X7: daily kurtosis from June 2015", reg["from"][1], ".2f", "8.41")
chk("X7: 20-day before June 2015", reg["before"][2], ".2f", "1.96")
chk("X7: 20-day from June 2015", reg["from"][2], ".2f", "2.66")
chk("X7: iid 3.44/20", 3.44 / 20, ".2f", "0.17")
chk("X7: iid 8.41/20", 8.41 / 20, ".2f", "0.42")
has("limit regimes", "1 June 2015")
anchor("A17-57", "; ".join(f"{lab} 2015-06-01 ({v[0]}): daily {v[1]:.4f}, 20-day {v[2]:.4f}" for lab, v in reg.items())
       + f"; iid 3.44/20 = {3.44 / 20:.4f}, 8.41/20 = {8.41 / 20:.4f}")
# KC 7
m_kc = next(m for m in range(1, 100) if 5.428 / m < 0.5)
chk("KC 7: smallest m", m_kc, "d", "11")
chk("KC 7: 5.428/0.5", 5.428 / 0.5, ".3f", "10.856")
chk("KC 7: 10-day sums", km[10], ".2f", "3.02")
assert 5 < km[10] / 0.5428 < 6
anchor("A17-33", f"{m_kc}")

# ====================================================================== Section 8
for n, p in ((1, "0.317"), (4, "0.0455")):
    chk(f"E10: 2 Phi(-sqrt(n)), n = {n}", 2 * float(Phi(-sqrt(n))), ".3g", p)
sci("E10: n = 25", 2 * float(Phi(-5.0)), 1, "5.7 -7")
assert abs(1 - 2 / math.pi * math.atan(1.0) - 0.5) < 1e-15
anchor("A17-82", ", ".join(f"n={n}: {2 * float(stats.norm.sf(sqrt(n))):.4g}" for n in (1, 4, 25)))
dates_k = {"2025-04-02": dates.index("2025-04-02") + 1, "2025-04-07": dates.index("2025-04-07") + 1}
k_apr2, k_apr7 = kurt_ex(R[: dates_k["2025-04-02"]]), kurt_ex(R[: dates_k["2025-04-07"]])
chk("X9: kurtosis through 2 April 2025", k_apr2, ".2f", "4.25")
chk("X9: kurtosis through 7 April 2025", k_apr7, ".2f", "4.94")
assert dates_k["2025-04-07"] == dates_k["2025-04-02"] + 1
anchor("A17-35", f"{k_apr2:.4f} ({dates_k['2025-04-02']} returns) -> {k_apr7:.4f} ({dates_k['2025-04-07']} returns)")
xc = R - Rb
top = np.argsort(-(xc**4))[:10]
chk("top ten share of sum (R - Rbar)^4 (LM15's)", 100 * (xc[top] ** 4).sum() / (xc**4).sum(), ".1f", "35.0")
chk("their share of sum (R - Rbar)^2", 100 * (xc[top] ** 2).sum() / (xc**2).sum(), ".1f", "6.7")
anchor("A17-22", f"{(xc[top] ** 4).sum() / (xc**4).sum():.4%}; {(xc[top] ** 2).sum() / (xc**2).sum():.4%}")
assert all(s_ in lm05 for s_ in ("5.84", "7.63", "62.8%", "14.1%")), "LM5 no longer prints its kurtosis figures"
for p in ("5.84", "7.63", "62.8", "14.1"):
    chk(f"LM5's printed {p}", float(p), ".2f" if p in ("5.84", "7.63") else ".1f", p)
anchor("A17-21", "5.84 -> 7.63 (lm05.md:367); 62.8%; 14.1% (lm05.md:369)")
n_ = np.arange(1, T + 1)
va = A * (np.cumsum(R**2) / n_ - (np.cumsum(R) / n_) ** 2)
lo_i, hi_i = 245 + int(va[245:].argmin()), 245 + int(va[245:].argmax())
chk("X9: running variance, low", va[lo_i], ".4f", "0.0326")
chk("X9: running variance, high", va[hi_i], ".4f", "0.0580")
chk("X9: running variance, end", va[-1], ".4f", "0.0359")
same("X9: date of the low", dates[lo_i], "2024-04-12", in_md=False)
same("X9: date of the high", dates[hi_i], "2004-06-23", in_md=False)
has("X9: low date in words", "12 April 2024")
has("X9: high date in words", "23 June 2004")
same("X9: first plotted date", dates[245], "2003-12-29", in_md=False)
has("X9: first date in words", "246th return (29 December 2003)")
anchor("A17-58", f"min {va[lo_i]:.6f} ({dates[lo_i]}); max {va[hi_i]:.6f} ({dates[hi_i]}); end {va[-1]:.6f}")

# ====================================================================== Section 9: the printed code's comments
binom41 = float(stats.binom.cdf(41, 100, 0.5))
chk("code: binom.cdf(41, 100, 0.5)", binom41, ".5f", "0.04431")
chk("code: norm.cdf(-1.7)", float(stats.norm.cdf((41.5 - 50) / 5)), ".5f", "0.04457")
has("code: kurtosis comment", "# 5.43, 3.63, 2.29, 3.20")
has("code: T comment", "# T = 5,849 simple returns")

# ====================================================================== practice problems and solutions
chk("P1: A", 1.2 / sqrt(400), ".2f", "0.06")
chk("P1: B", 1.2 / 400, ".3f", "0.003")
chk("P1: C", 1.2 * sqrt(400), ".0f", "24")
anchor("A17-83", f"{1.2 / sqrt(400):g}%; {1.2 / 400:g}%; {1.2 * sqrt(400):g}%")
chk("P2: A, 2 Phi(-2)", 2 * float(Phi(-0.02 / (0.5 / sqrt(2500)))), ".4f", "0.0455")
chk("P2: B", sqrt(0.25) / (sqrt(2500) * 0.02), ".1f", "0.5")
chk("P2: C", 0.25 / (2500 * 0.02**2), ".2f", "0.25")
chk("P2: misses in standard deviations", 0.02 / (0.5 / sqrt(2500)), "g", "2")
anchor("A17-84", f"{2 * float(stats.norm.sf(0.02 / (0.5 / sqrt(2500)))):.4f}; {sqrt(0.25) / (sqrt(2500) * 0.02):g}; "
       f"{0.25 / (2500 * 0.02**2):g}")
chk("P3: E W4", 1.25**4, ".4f", "2.4414")
w4 = {j: Fraction(2) ** (2 * j - 4) for j in range(5)}
assert [j for j in range(5) if w4[j] > Fraction(5, 4) ** 4] == [3, 4]
same("P3: answer", str(Fraction(comb(4, 3) + comb(4, 4), 16)), "5/16")
same("P3: distractor A", str(Fraction(1, 16)), "1/16")
same("P3: distractor C", str(Fraction(comb(4, 2) + comb(4, 3) + comb(4, 4), 16)), "11/16")
anchor("A17-85", f"E W4 {1.25**4:.4f}; Pr(j=4) 1/16; Pr(j>=3) 5/16; Pr(j>=2) 11/16")
chk("P5: A", 5.43 / sqrt(20), ".2f", "1.21")
chk("P5: B", 5.43 / 20, ".2f", "0.27")
anchor("A17-86", f"{5.43 / sqrt(20):.4f}; {5.43 / 20:.4f}")
# P7: five years
z7 = gp * sqrt(1231) / sp
chk("P7: z", z7, ".3f", "1.599")
chk("P7: z (unrounded)", rb * sqrt(1231) / sr, ".3f", "1.599")
chk("P7: loss", 100 * float(Phi(-z7)), ".2f", "5.49")
chk("P7: loss from printed z", 100 * float(Phi(-1.599)), ".2f", "5.49")
chk("P7: 1231 rbar", 1231 * gp, ".4f", "0.6791")
chk("P7: median", exp(1231 * gp), ".2f", "1.97")
chk("P7: median from printed 0.6791", exp(0.6791), ".2f", "1.97")
chk("P7: median (unrounded)", exp(1231 * rb), ".2f", "1.97")
half = 1.645 * sp * sqrt(1231)
chk("P7: 1.645 s_r sqrt(m)", half, ".4f", "0.6988")
chk("P7: 5% quantile", exp(1231 * gp - half), ".2f", "0.98")
chk("P7: 5% quantile from printed exponents", exp(0.6791 - 0.6988), ".2f", "0.98")
chk("P7: 5% quantile (unrounded)", exp(1231 * rb - Z95 * sr * sqrt(1231)), ".2f", "0.98")
chk("P7: 95% quantile", exp(1231 * gp + half), ".2f", "3.97")
chk("P7: 95% quantile from printed exponents", exp(0.6791 + 0.6988), ".2f", "3.97")
chk("P7: 95% quantile (unrounded)", exp(1231 * rb + Z95 * sr * sqrt(1231)), ".2f", "3.97")
# P8
d2 = log(1 + 2 * Rb) - gbar(2)
chk("P8: delta(2) (bp, LM14's)", 1e4 * d2, ".3f", "2.936")
chk("P8: bound", 0.024288**2 / (5849 * 2.936e-4**2), ".2f", "1.17")
z8 = sqrt(5849) * 2.936e-4 / 0.024288
chk("P8: z", z8, ".4f", "0.9245")
chk("P8: Pr", float(Phi(-z8)), ".3f", "0.178")
chk("P8: Pr from printed z", float(Phi(-0.9245)), ".3f", "0.178")
chk("P8: Pr (unrounded)", float(stats.norm.sf(sqrt(T) * d2 / sdl(2))), ".3f", "0.178")
anchor("A17-88", f"{1e4 * d2:.4f} bp")
anchor("A17-89", f"bound {0.024288**2 / (T * 2.936e-4**2):.4f}; z {z8:.4f}; Pr {float(stats.norm.sf(z8)):.4f}")
# P9: binomial kurtosis
kb = float(stats.binom.stats(20, 0.5, moments="k"))
chk("P9: excess kurtosis of Bin(20, 1/2)", kb, ".1f", "-0.1")
assert abs(kb - (-2 / 20)) < 1e-12 and 6 * Fraction(7 * 6, 2) == 3 * 7 * 6
anchor("A17-90", f"{kb:.4f}")
# P11 repeats the running shares and the window kurtosis (checked above); the lab solves it
anchor("A17-91", f"n=246 {A * r[:246].mean():.4%}; min {min(A * np.cumsum(r)[245:] / n_[245:]):.4%} "
       f"({dates[245 + int((np.cumsum(r)[245:] / n_[245:]).argmin())]}); end {A * rb:.4%}")
anchor("A17-78", "1.96 (printed in lm04.md:541)")

# ====================================================================== structure: labels and citations
md_raw = MD.read_text(encoding="utf-8")
ex_labels = re.findall(r"\[!exhibit\][^\n]*\{#([\w-]+)\}", md_raw)
eg_labels = re.findall(r"\[!example\][^\n]*\{#([\w-]+)\}", md_raw)
assert len(ex_labels) == 9 and len(eg_labels) == 10, (ex_labels, eg_labels)
for lab in ex_labels:
    assert f"[[ex:{lab}]]" in md_raw, f"exhibit {lab} is never cited"
for kind, lab in re.findall(r"\[\[(ex|eg):([\w-]+)\]\]", md_raw):
    assert lab in (ex_labels if kind == "ex" else eg_labels), (kind, lab)
assert "\t" not in md_raw and "\b" not in md_raw and "\f" not in md_raw
print(f"labels: {len(ex_labels)} exhibits, {len(eg_labels)} examples, every exhibit cited")

# ====================================================================== report
body = TEXT.split("\n## Glossary", 1)[0]
nums = set(re.findall(r"(?<![\w.])\d+\.\d+|(?<![\w.,])\d{1,3}(?:,\d{3})+", body))
left = sorted(n for n in nums if n not in COVERED)
print(f"\nnumbers with a decimal point or thousands separator not covered by a check ({len(left)}):")
print("   " + " ".join(left))
print(f"\nanchor differences ({len(ANCHOR_DIFFS)}):")
for a in ANCHOR_DIFFS:
    print("   ", a)
print(f"\nall {N_CHECKS} checks passed")
