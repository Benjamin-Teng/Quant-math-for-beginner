"""Every number that LM22 (Resampling Methods) prints, computed and checked against src/lm22.md.

Run:  uv run python data/lm22_numbers.py      (after data/vol3_series.py and data/vol2_series.py; about three minutes)

Inputs (data/lm22_common.py): data/processed/vol3_taiex.parquet (TR23, the TAIEX total-return index),
data/processed/vol2_closes.parquet through u28() of data/lm10_series.py (U28, the 28 repaired sector price indices), and
src/lm22.md (the text the checks compare against). Started from data/vol4_anchors_lm22.py, whose conventions it keeps
(plans/vol-4-anchors.md, "LM22": samples, divisors, seeds np.random.default_rng([e, 20261011]), quantiles by
inverted_cdf, LM18's batch standard errors, the guard 1e-12 for threshold counts).

Checks, each of which stops the script on a mismatch:
  chk(label, value, fmt, printed)  format(value, fmt) must equal `printed`, the string must appear in src/lm22.md as
                                   a whole number, and the value must not sit on a rounding tie of fmt. A value within
                                   a tenth of a unit of its last printed digit from a rounding boundary is listed at the
                                   end ("near a rounding boundary"); it is correctly rounded. Values a reader computes
                                   by hand are also recomputed from the inputs printed next to them.
  has(label, text)                 a literal string (a seed, a date, a code line) appears in the text.
  mc(label, value, mcse, nd)       a bootstrap number printed with nd decimals has a Monte Carlo standard error (LM18's
                                   batches) below 2.5 units of its last printed digit (Volume III's precedent,
                                   plans/vol-3.md:2308: 0.0530 +- 0.0022 printed as 5.3%, 2.2 units).
  atmost(label, value, printed)    a bound the text prints ("at most 0.04") is at or above the value it bounds.
  anchor(id, got, expected)        compares with plans/vol-4-anchors.md (LM22 rows, the anchor script's unrounded
                                   values); a difference is reported at the end, not forced.
The printed code blocks of Section 9 and of Problem 10's solution are run as printed, and their outputs are checked.
If src/data/lm22-*.json exist (data/lm22_charts.py), the values the text cites from them are checked too.
It ends by printing "all N checks passed".
"""
import contextlib
import inspect
import io
import json
import math
import re
import textwrap
from fractions import Fraction
from itertools import product
from math import ceil, sqrt
from types import SimpleNamespace
from typing import Any, cast

import lm22_common as C
import numpy as np
from arch.bootstrap import (
    CircularBlockBootstrap,
    MovingBlockBootstrap,
    StationaryBootstrap,
)
from scipy import stats

ROOT = C.ROOT
MD = ROOT / "src" / "lm22.md"
TEXT = MD.read_text(encoding="utf-8")
NORM = TEXT.replace("{,}", ",").replace("−", "-").replace("\\%", "%")
N_CHECKS = 0
COVERED: set[str] = set()
ANCHOR_DIFFS: list[str] = []
NEAR: list[str] = []
B = C.B
D = C.D
R, r, T, SQA = D.R, D.r, D.T, D.SQA
OBS = C.OBS


def in_text(printed: str) -> bool:
    return re.search(r"(?<![\d.])" + re.escape(printed) + r"(?![\d])", NORM) is not None


def decimals(fmt: str) -> int:
    m = re.search(r"\.(\d+)", fmt)
    return int(m.group(1)) if m else 0


def tie(value: float, fmt: str) -> bool:
    scaled = abs(value) * 10 ** decimals(fmt)
    return abs(scaled - math.floor(scaled) - 0.5) < 1e-6


def chk(label: str, value: float, fmt: str, printed: str) -> None:
    global N_CHECKS
    got = format(value, fmt)
    if got.startswith("-") and float(got.replace(",", "")) == 0:
        got = got[1:]
    print(f"CHECK {label}: {got} (printed {printed}) {'ok' if got == printed else 'MISMATCH'}")
    assert got == printed, (label, got, printed)
    assert not tie(value, fmt), ("rounding tie: print more digits", label, value)
    assert in_text(printed), f"{label}: {printed!r} not found in src/lm22.md"
    scaled = abs(value) * 10 ** decimals(fmt)
    if abs(scaled - math.floor(scaled) - 0.5) < 0.1:
        NEAR.append(f"{label}: {value:.{decimals(fmt) + 3}f} printed {printed}")
    COVERED.add(printed)
    N_CHECKS += 1


def has(label: str, text: str) -> None:
    global N_CHECKS
    assert text in NORM, f"{label}: {text!r} not found in src/lm22.md"
    print(f"CHECK {label}: '{text[:70]}' in text ok")
    COVERED.add(text)
    N_CHECKS += 1


def mc(label: str, value: float, mcse: float, nd: int) -> None:
    """A printed bootstrap number keeps only the digits its Monte Carlo standard error supports: the error is below
    2.5 units of the last printed digit (Volume III printed 0.0530 +- 0.0022 as 5.3%, 2.2 units; review M4)."""
    global N_CHECKS
    print(f"MC {label}: {value:.6g}, Monte Carlo SE {mcse:.2g}, last digit {10.0 ** -nd:g}")
    assert mcse < 2.5 * 10.0 ** (-nd), (label, value, mcse, nd)
    N_CHECKS += 1


def atmost(label: str, value: float, printed: str) -> None:
    """The text's bound "at most <printed>" holds: value <= printed, and the bound appears in the text."""
    global N_CHECKS
    print(f"BOUND {label}: {value:.6g} <= {printed}")
    assert value <= float(printed), (label, value, printed)
    assert in_text(printed), f"{label}: {printed!r} not found in src/lm22.md"
    COVERED.add(printed)
    N_CHECKS += 1


def anchor(label: str, got: str, expected: str) -> None:
    tag = "ok" if got == expected else "DIFFERS"
    print(f"ANCHOR {label}: {got} (anchor {expected}) {tag}")
    if got != expected:
        ANCHOR_DIFFS.append(f"{label}: script {got}, anchor {expected}")


def g6(x: float) -> str:
    return f"{x:.6g}"


def pct2(v: tuple[float, float]) -> str:
    return f"{v[0]:.6g} to {v[1]:.6g}"


def iv(s: C.Summary, nd: int, scale: float = 1.0) -> tuple[str, str]:
    return f"{s.lo * scale:.{nd}f}", f"{s.hi * scale:.{nd}f}"


def chk_iv(label: str, s: C.Summary, nd: int, scale: float = 1.0, basic: bool = False) -> None:
    """Percentile (or basic) ends at nd decimals, as printed "lo to hi"; Monte Carlo errors of the ends checked."""
    lo, hi = (s.blo, s.bhi) if basic else (s.lo, s.hi)
    a, b = f"{lo * scale:.{nd}f}".replace("-0.00", "0.00"), f"{hi * scale:.{nd}f}"
    chk(f"{label} low", lo * scale, f".{nd}f", a)
    chk(f"{label} high", hi * scale, f".{nd}f", b)
    assert any(in_text(f"{a}{p} {w} {b}") for p in ("", "%") for w in ("to", "and")) or in_text(f"{a}–{b}") \
        or in_text(f"{a}%–{b}"), (label, a, b)
    lo_b, hi_b = (s.hi_b, s.lo_b) if basic else (s.lo_b, s.hi_b)    # a basic end mirrors a percentile end
    mc(f"{label} low end", lo * scale, lo_b * scale, nd)
    mc(f"{label} high end", hi * scale, hi_b * scale, nd)


# ====================================================================== data (notation note, case)
anchor("A22-01", f"closes {len(D.dates_all)} {D.dates_all[0]} to {D.dates_all[-1]}; T {T} returns {D.dates[0]} to "
       f"{D.dates[-1]}; 7% regime {int(D.pre.sum())}, 10% regime {int((~D.pre).sum())}",
       "closes 5850 2003-01-02 to 2026-10-08; T 5849 returns 2003-01-03 to 2026-10-08; 7% regime 3077, 10% regime 2772")
assert D.dates[int(np.flatnonzero(D.pre)[-1])] == "2015-05-29" and D.dates[int(np.flatnonzero(~D.pre)[0])] == "2015-06-01"
chk("T", float(T), ",.0f", "5,849")
chk("7% regime returns", float(D.pre.sum()), ",.0f", "3,077")
chk("10% regime returns", float((~D.pre).sum()), ",.0f", "2,772")
has("sample dates", "2 January 2003 → 8 October 2026")
has("first return", "3 January 2003")
has("regime end", "29 May 2015")
has("10% regime start", "1 June 2015")
anchor("A22-02", f"days {D.days}; years {D.years:.7f}; A {D.A:.6f}; sqrt(A) {SQA:.6f}",
       "days 8680; years 23.7645448; A 246.122955; sqrt(A) 15.688306")
chk("A", D.A, ".2f", "246.12")
assert 23 <= D.years < 24
has("23-year sample", "a 23-year sample")
anchor("A22-03", f"Rbar {D.Rb:.10%}; s {D.s:.8%}; Skew {D.skew:.8f}; Kurt {D.kurt:.8f}",
       "Rbar 0.0625050622%; s 1.20836434%; Skew -0.33844418; Kurt 8.26803008")
chk("Rbar %", 100 * D.Rb, ".6f", "0.062505")
chk("s %", 100 * D.s, ".4f", "1.2084")
chk("Kurt (LM14's)", D.kurt, ".2f", "8.27")
anchor("A22-04", f"U28 T {C.TU} returns {C.U.dates[0]} to {C.U.dates[-1]}; A {C.U.A:.6f}; pair "
       f"{C.U.names[C.I_SEMI]}, {C.U.names[C.I_FIN]}",
       "U28 T 4382 returns 2008-12-02 to 2026-10-08; A 245.479371; pair Semiconductor, FinancialInsurance")
chk("U28 T", float(C.TU), ",.0f", "4,382")
has("U28 start", "2 December 2008")
SRd = D.Rb / D.s
anchor("A22-05", f"SR per day {SRd:.8f}; annualized {SRd * SQA:.6f}", "SR per day 0.05172700; annualized 0.811509")
chk("SR per day", SRd, ".4f", "0.0517")
chk("SR annual", SRd * SQA, ".2f", "0.81")
KEL, VOL, FX = OBS["Kelly"], OBS["vol"], OBS["fx"]
anchor("A22-06", f"f_hat {KEL:.6f}; f_hat* {FX:.6f}", "f_hat 4.280745; f_hat* 4.138091")
chk("f_hat", KEL, ".2f", "4.28")
chk("f_hat* (LM17's)", FX, ".2f", "4.14")
anchor("A22-07", f"{VOL:.6%}", "18.957190%")
chk("volatility %", 100 * VOL, ".2f", "18.96")
pwR, pwR2, pwr2 = C.pw(R), C.pw((R - D.Rb) ** 2), C.pw((r - D.rb) ** 2)
CAP = ceil(min(3 * sqrt(T), T / 3))
anchor("A22-08", f"R: {pwR[0]:.6f}, {pwR[1]:.6f}; (R - Rbar)^2: {pwR2[0]:.6f}, {pwR2[1]:.6f}; (r - rbar)^2: "
       f"{pwr2[0]:.6f}; ell {C.ELL}; cap {CAP}",
       "R: 3.067077, 3.510927; (R - Rbar)^2: 144.591746, 165.516231; (r - rbar)^2: 144.019622; ell 145; cap 230")
assert C.ELL == 145 and CAP == 230
chk("PW on R", pwR[0], ".2f", "3.07")
chk("PW on R, one decimal", pwR[0], ".1f", "3.1")
chk("PW circular on R", pwR[1], ".2f", "3.51")
chk("PW on squares", pwR2[0], ".2f", "144.59")
chk("PW on squares, one decimal", pwR2[0], ".1f", "144.6")
chk("PW circular on squares", pwR2[1], ".2f", "165.52")
chk("PW on squared log returns", pwr2[0], ".2f", "144.02")
chk("cap", float(CAP), ".0f", "230")
chk("ell", float(C.ELL), ".0f", "145")
has("rule of the cap", "$\\lceil\\min(3\\sqrt T,T/3)\\rceil$".replace("\\%", "%"))

# ====================================================================== experiments 2 and 3 (case, E2-E5, X1-X4)
IID = C.exp_tr(2, "iid", 1)
SB = C.exp_tr(3, "sb", C.ELL)
S = {k: (C.summ(IID[k], OBS[k]), C.summ(SB[k], OBS[k])) for k in ("SR", "Kelly", "vol", "acf", "VR20", "fx")}
sr_i, sr_b = S["SR"]
k_i, k_b = S["Kelly"]
v_i, v_b = S["vol"]
for aid, key, exp_iid, exp_blk in (
        ("A22-09/12", "SR", "SE 0.205379; 0.414682 to 1.21419; basic 0.408823 to 1.20834; mean 0.811582",
         "SE 0.232871; 0.365834 to 1.27315; basic 0.349869 to 1.25718; mean 0.819693"),
        ("A22-10/13", "Kelly", "SE 1.10099; 2.16944 to 6.46551; basic 2.09598 to 6.39205; mean 4.28738",
         "SE 1.34226; 1.82728 to 7.06741; basic 1.49408 to 6.73421; mean 4.37896"),
        ("A22-11/14", "vol", "SE 0.00331744; 0.183048 to 0.196049; basic 0.183095 to 0.196096; mean 0.189507",
         "SE 0.0129617; 0.164834 to 0.215004; basic 0.16414 to 0.21431; mean 0.189038"),
        ("A22-21", "fx", "SE 1.02601; 2.13088 to 6.13719; basic 2.13899 to 6.1453; mean 4.13453",
         "SE 1.2297; 1.80649 to 6.6171; basic 1.65908 to 6.46969; mean 4.20452")):
    for s, ex, nm in ((S[key][0], exp_iid, "iid"), (S[key][1], exp_blk, "block")):
        anchor(f"{aid} {key} {nm}", f"SE {g6(s.se)}; {g6(s.lo)} to {g6(s.hi)}; basic {g6(s.blo)} to {g6(s.bhi)}; "
               f"mean {g6(s.mean)}", ex)
# the case and X1
chk("SR iid SE", sr_i.se, ".3f", "0.205")
mc("SR iid SE", sr_i.se, sr_i.se_b, 3)
chk_iv("SR iid percentile", sr_i, 2)
chk_iv("SR iid basic", sr_i, 2, basic=True)
chk("SR block SE", sr_b.se, ".3f", "0.233")
mc("SR block SE", sr_b.se, sr_b.se_b, 3)
chk_iv("SR block percentile", sr_b, 2)
chk("Kelly iid SE", k_i.se, ".2f", "1.10")
mc("Kelly iid SE", k_i.se, k_i.se_b, 2)
chk_iv("Kelly iid percentile", k_i, 1)
chk_iv("Kelly iid basic", k_i, 1, basic=True)
chk("Kelly block SE", k_b.se, ".2f", "1.34")
chk_iv("Kelly block percentile", k_b, 1)
chk_iv("Kelly block basic", k_b, 1, basic=True)
chk("vol iid SE points", 100 * v_i.se, ".2f", "0.33")
mc("vol iid SE points", 100 * v_i.se, 100 * v_i.se_b, 2)
chk_iv("vol iid percentile %", v_i, 1, 100)
chk("vol block SE points", 100 * v_b.se, ".2f", "1.30")
mc("vol block SE points", 100 * v_b.se, 100 * v_b.se_b, 2)
chk_iv("vol block percentile %", v_b, 1, 100)
fx_i, fx_b = S["fx"]
chk("f_hat* iid SE", fx_i.se, ".2f", "1.03")
chk_iv("f_hat* iid percentile", fx_i, 1)
chk_iv("f_hat* block percentile", fx_b, 1)
assert fx_i.se < k_i.se and fx_i.mean < k_i.mean and fx_i.hi - fx_i.lo < k_i.hi - k_i.lo   # "lower and narrower"
wr = {k: (S[k][1].hi - S[k][1].lo) / (S[k][0].hi - S[k][0].lo) for k in ("SR", "Kelly", "vol")}
mx_end = {k: max(S[k][0].lo_b, S[k][0].hi_b, S[k][1].lo_b, S[k][1].hi_b) for k in ("SR", "Kelly", "vol")}
anchor("A22-15", f"width ratios {wr['SR']:.6f}, {wr['Kelly']:.6f}, {wr['vol']:.6f}; ends' batch SEs "
       f"{mx_end['SR']:.6g}, {mx_end['Kelly']:.6g}, {mx_end['vol']:.6g}",
       "width ratios 1.134835, 1.219748, 3.859053; ends' batch SEs 0.0081987, 0.0386706, 0.000298675")
chk("width ratio SR", wr["SR"], ".1f", "1.1")
chk("width ratio Kelly", wr["Kelly"], ".1f", "1.2")
chk("width ratio vol", wr["vol"], ".1f", "3.9")
assert 3.5 < wr["vol"] < 4                                                     # "almost four times as wide"
atmost("ends' MC SE, Sharpe", mx_end["SR"], "0.009")                         # review m1: 0.0082, not 0.008
atmost("ends' MC SE, Kelly", mx_end["Kelly"], "0.04")
atmost("ends' MC SE, volatility points", 100 * mx_end["vol"], "0.03")
has("X1 MC sentence", "at most 0.009, 0.04 and 0.03 points")
has("X1 width ratios unrounded", "Width ratios from unrounded ends")
for lit in ("`[2, 20261011]`", "`[3, 20261011]`", "`default_rng([1, 20261011])`", "`default_rng([2, 20261011])`",
            "`default_rng([3, 20261011])`", "`integers(0, T, size=(500, T))`", "`default_rng([e, 20261011])`"):
    has(f"literal {lit}", lit)

# ====================================================================== E1: five returns
five = np.array([0.012, -0.008, 0.003, -0.025, 0.006])
allres = np.array(list(product(range(5), repeat=5)))
mean_all = five[allres].mean(axis=1)
med_all = np.quantile(five[allres], 0.5, axis=1, method="inverted_cdf")
assert np.array_equal(med_all, np.sort(five[allres], axis=1)[:, 2])
b1 = C.gen(1).integers(0, 5, size=(1000, 5))
m1 = five[b1].mean(axis=1)
md1 = np.quantile(five[b1], 0.5, axis=1, method="inverted_cdf")
s5 = float(five.std())
probs = {float(x): Fraction(int((med_all == x).sum()), 3125) for x in np.sort(five)}
anchor("A22-17", f"mean {five.mean():.4%}; s {s5:.6%}; SE mean {mean_all.std():.6%}, median {med_all.std():.6%}; "
       f"B 1000: {m1.std():.6%} ({C.bse(m1, C.sd):.4%}), {md1.std():.6%} ({C.bse(md1, C.sd):.4%})",
       "mean -0.2400%; s 1.303227%; SE mean 0.582821%, median 0.858763%; B 1000: 0.587515% (0.0102%), "
       "0.869247% (0.0239%)")
chk("E1 mean %", 100 * five.mean(), ".2f", "-0.24")
chk("E1 s %", 100 * s5, ".4f", "1.3032")
chk("E1 resamples", 3125.0, ",.0f", "3,125")
chk("E1 SE mean %", 100 * float(mean_all.std()), ".3f", "0.583")
assert abs(float(mean_all.std()) - s5 / sqrt(5)) < 1e-15
chk("E1 s/sqrt5 from printed s", 1.3032 / sqrt(5), ".3f", "0.583")
assert probs == {-0.025: Fraction(181, 3125), -0.008: Fraction(811, 3125), 0.003: Fraction(1141, 3125),
                 0.006: Fraction(811, 3125), 0.012: Fraction(181, 3125)}
# the law of the median: at most the j-th smallest when at least three of five draws are
for j, x in enumerate(sorted(five), start=1):
    cdf = sum(math.comb(5, k) * Fraction(j, 5) ** k * Fraction(5 - j, 5) ** (5 - k) for k in range(3, 6))
    assert cdf == sum(p for v, p in probs.items() if v <= x)
for lit in ("181/3,125", "811/3,125", "1,141/3,125"):
    has(f"E1 {lit}", lit)
chk("E1 SE median %", 100 * float(med_all.std()), ".3f", "0.859")
mc_m, mc_md = C.bse(m1, C.sd), C.bse(md1, C.sd)
chk("E1 B=1000 SE mean %", 100 * float(m1.std()), ".2f", "0.59")
chk("E1 batch SE mean %", 100 * mc_m, ".2f", "0.01")
chk("E1 B=1000 SE median %", 100 * float(md1.std()), ".2f", "0.87")
chk("E1 batch SE median %", 100 * mc_md, ".2f", "0.02")
has("E1 printed", "$0.59%\\pm0.01%$ and $0.87%\\pm0.02%$")
chk("divisor factor", sqrt((B - 1) / B), ".5f", "0.99995")
chk("rank low", float(ceil(0.025 * B)), ",.0f", "250")
chk("rank high", float(ceil(0.975 * B)), ",.0f", "9,750")
has("ranks", "250th and 9,750th")

# ====================================================================== E2: delta method and SciPy
SR, skew, kurt = SRd, D.skew, D.kurt
se_sr = sqrt((1 - SR * skew + SR**2 * (kurt - 1) / 4) / T)
se_sr_n = sqrt((1 + SR**2 / 2) / T)
z975 = float(stats.norm.ppf(0.975))
dlo, dhi = (SR - z975 * se_sr) * SQA, (SR + z975 * se_sr) * SQA
anchor("A22-18", f"delta SE annual {se_sr * SQA:.6f}; normal {se_sr_n * SQA:.6f}; 1/sqrt(T) {1 / sqrt(T):.8f}; "
       f"interval {dlo:.6f} to {dhi:.6f}",
       "delta SE annual 0.207414; normal 0.205270; 1/sqrt(T) 0.01307553; interval 0.404984 to 1.218034")
chk("delta SR SE plug-in (LM20's)", se_sr * SQA, ".3f", "0.207")
chk("delta SR SE normal (LM20's)", se_sr_n * SQA, ".3f", "0.205")
chk("delta SR interval low", dlo, ".2f", "0.40")
chk("delta SR interval high", dhi, ".2f", "1.22")
has("delta SR interval", "0.40 to 1.22")
chk("1/sqrt(T)", 1 / sqrt(T), ".4f", "0.0131")
chk("bootstrap SE daily ~ 1/sqrt(T)", sr_i.se / SQA, ".4f", "0.0131")


def sr_vec(x: np.ndarray, axis: int = -1) -> np.ndarray:
    return SQA * x.mean(axis=axis) / x.std(axis=axis)


def kel_vec(x: np.ndarray, axis: int = -1) -> np.ndarray:
    return x.mean(axis=axis) / x.var(axis=axis)


sp = {}
for meth in ("percentile", "basic", "BCa"):
    for nm, fn in (("SR", sr_vec), ("Kelly", kel_vec)):                 # stream 2 re-created on purpose
        sp[(meth, nm)] = stats.bootstrap((R,), fn, n_resamples=B, batch=C.CHUNK, vectorized=True, method=meth,
                                         rng=C.gen(2))
assert np.array_equal(sp[("percentile", "SR")].bootstrap_distribution, IID["SR"])
assert np.allclose(sp[("percentile", "Kelly")].bootstrap_distribution, IID["Kelly"], rtol=0, atol=1e-12)


def ci(meth: str, nm: str) -> tuple[float, float]:
    c = sp[(meth, nm)].confidence_interval
    return float(c.low), float(c.high)


se_sp = float(sp[("percentile", "SR")].standard_error)
anchor("A22-19", f"SR percentile {pct2(ci('percentile', 'SR'))}; BCa {pct2(ci('BCa', 'SR'))}; SE {se_sp:.8f} "
       f"against {sr_i.se:.8f}",
       "SR percentile 0.415719 to 1.21421; BCa 0.419021 to 1.21901; SE 0.20538880 against 0.20537853")
chk("SciPy SR BCa low", ci("BCa", "SR")[0], ".2f", "0.42")
chk("SciPy SR BCa high", ci("BCa", "SR")[1], ".2f", "1.22")
has("SciPy SR BCa", "0.42 to 1.22")
chk("SciPy percentile low (linear)", ci("percentile", "SR")[0], ".4f", "0.4157")
chk("book's percentile low", sr_i.lo, ".4f", "0.4147")
chk("SciPy standard_error", se_sp, ".5f", "0.20539")
chk("divisor B SE", sr_i.se, ".5f", "0.20538")
chk("SciPy default resamples", 9999.0, ",.0f", "9,999")
_sig = inspect.signature(stats.bootstrap).parameters
assert _sig["n_resamples"].default == 9999 and _sig["method"].default == "BCa"

# ====================================================================== E3: Kelly delta method and BCa
se_k = sqrt((1 - 2 * SR * skew + SR**2 * (kurt - 1)) / (D.s**2 * T))
se_k_n = sqrt((1 + 2 * SR**2) / (D.s**2 * T))
se_k_m = 1 / (D.s * sqrt(T))
klo, khi = KEL - z975 * se_k, KEL + z975 * se_k
anchor("A22-20", f"delta {se_k:.6f}, {se_k_n:.6f}, {se_k_m:.6f}; interval {klo:.6f} to {khi:.6f}; BCa "
       f"{pct2(ci('BCa', 'Kelly'))}",
       "delta 1.111160, 1.084976, 1.082085; interval 2.102913 to 6.458578; BCa 2.18961 to 6.48412")
chk("delta Kelly SE plug-in", se_k, ".3f", "1.111")
chk("delta Kelly SE normal", se_k_n, ".3f", "1.085")
chk("delta Kelly SE mean only", se_k_m, ".3f", "1.082")
chk("delta Kelly low", klo, ".2f", "2.10")
chk("delta Kelly high", khi, ".2f", "6.46")
has("delta Kelly interval", "2.10 to 6.46")
chk("SciPy Kelly BCa low", ci("BCa", "Kelly")[0], ".1f", "2.2")
chk("SciPy Kelly BCa high", ci("BCa", "Kelly")[1], ".1f", "6.5")
has("Kelly BCa", "BCa interval 2.2 to 6.5")


def bca_ends(vals: np.ndarray) -> tuple[float, float]:
    """SciPy's BCa interval of f_hat from a given bootstrap distribution (n_resamples=0 reuses it as it is)."""
    res = stats.bootstrap((R,), kel_vec, n_resamples=0, vectorized=True, method="BCa",
                          bootstrap_result=cast(Any, SimpleNamespace(bootstrap_distribution=vals)))
    return float(res.confidence_interval.low), float(res.confidence_interval.high)


assert np.allclose(bca_ends(IID["Kelly"]), ci("BCa", "Kelly"), rtol=0, atol=1e-12)
bca_b = np.array([bca_ends(c) for c in np.split(IID["Kelly"], 20)]).std(axis=0) / sqrt(20)   # LM18's batches
e3_ends = {"f_hat iid": max(k_i.lo_b, k_i.hi_b), "f_hat BCa": float(bca_b.max()), "f_hat* iid": max(fx_i.lo_b, fx_i.hi_b),
           "f_hat blocks": max(k_b.lo_b, k_b.hi_b), "f_hat* blocks": max(fx_b.lo_b, fx_b.hi_b)}
print("E3 ends' batch SEs:", {k: round(v, 4) for k, v in e3_ends.items()})
atmost("E3 every end's MC SE (BCa's 0.041 and 0.042 included)", max(e3_ends.values()), "0.05")
has("E3 MC sentence", "(Monte Carlo errors of every end at most 0.05)")

# relative error, LM4's band, the knowledge check of section 3
rel = 1 / (SR * sqrt(T))
anchor("A22-38", f"{rel:.6f}", "0.252780")
chk("relative error %", 100 * rel, ".1f", "25.3")
chk("relative error % from printed SR", 100 / (0.0517 * sqrt(T)), ".1f", "25.3")
chk("1.96 relative errors %", 196 * rel, ".0f", "50")
chk("SR sqrt T", SR * sqrt(T), ".2f", "3.96")
sr4 = 0.0871 / 1.2385                                     # LM4's printed mean and s of 0050 (lm04.md:547)
chk("LM4 SR sqrt T", sr4 * sqrt(2902), ".2f", "3.79")
chk("LM4 relative error %", 100 / (sr4 * sqrt(2902)), ".0f", "26")
chk("LM4 printed ratio %", 100 * 0.0230 / 0.0871, ".0f", "26")
hwt = (k_i.hi - k_i.lo) / 2 / KEL
anchor("A22-16", f"TR23 {hwt:.6f}", "TR23 0.501790")   # the anchor's LM4 part (2.7 to 7.6, the exact optimum) is
chk("TR23 half-width %", 100 * hwt, ".0f", "50")       # superseded: review U6 compares LM4's band for mu/s^2
chk("TR23 half-width % from printed", 100 * (6.5 - 2.2) / 2 / 4.28, ".0f", "50")
# LM4's band for 0050's mu-hat / s^2: 2.7 to 8.6 around 5.68 (lm04.md:547, :39), from a shifted mean
chk("LM4 half-width % (1.96 x 0.0230 / 0.0871)", 100 * 1.96 * 0.0230 / 0.0871, ".0f", "52")
chk("LM4 half-width % from its band", 100 * (8.6 - 2.7) / 2 / 5.68, ".0f", "52")
has("LM4's band", "2.7 to 8.6 for 0050's $\\hat\\mu/s^2$")
has("LM4's quadratic rule", "52% of 5.68")
has("LM7's rate", "$r_f=1.5%$")

# ====================================================================== E4: what resampling days cannot see
a_ = np.abs(r)
pc1 = float(np.corrcoef(a_[:-1], a_[1:])[0, 1])
acf_i, acf_b = S["acf"]
n_ge = int((IID["acf"] >= OBS["acf"]).sum())
n_abs = int((np.abs(IID["acf"]) >= OBS["acf"]).sum())
anchor("A22-22", f"acf {OBS['acf']:.6f}; LM17 {pc1:.6f}; iid SE {g6(acf_i.se)}; {g6(acf_i.lo)} to {g6(acf_i.hi)}; "
       f"basic {g6(acf_i.blo)} to {g6(acf_i.bhi)}; mean {g6(acf_i.mean)}; at or above {n_ge}; block "
       f"{g6(acf_b.lo)} to {g6(acf_b.hi)}; mean {g6(acf_b.mean)}",
       "acf 0.160615; LM17 0.160650; iid SE 0.013045; -0.025048 to 0.0260827; basic 0.295148 to 0.346278; mean "
       "-6.55409e-05; at or above 0; block 0.0994618 to 0.214506; mean 0.155559")
chk("acf |r|", OBS["acf"], ".3f", "0.161")
chk("LM17's pair correlation", pc1, ".3f", "0.161")
chk("acf iid mean", acf_i.mean, ".4f", "-0.0001")
mc("acf iid mean", acf_i.mean, acf_i.se / 100, 4)
chk_iv("acf iid percentile", acf_i, 3)
assert n_ge == 0 and n_abs == 0                                               # "none of 10,000 reaches 0.161"
has("none of 10,000", "none of 10,000 reaches 0.161")
chk("acf block mean", acf_b.mean, ".3f", "0.156")
mc("acf block mean", acf_b.mean, acf_b.se / 100, 3)
chk_iv("acf block percentile", acf_b, 2)
chk("acf iid SE (the null law's)", acf_i.se, ".3f", "0.013")                     # section 8, independence
chk("0.161 in iid standard errors", OBS["acf"] / acf_i.se, ".0f", "12")
chk("0.161 in iid standard errors, from printed", 0.161 / 0.013, ".0f", "12")
has("independence rejected", "None reaches 0.161, which lies 12 standard errors (0.013) above 0")
chk("P4 basic low", acf_i.blo, ".3f", "0.295")
chk("P4 basic high", acf_i.bhi, ".3f", "0.346")
has("P4 basic", "0.295 to 0.346")
chk("P4 bias", acf_i.bias, ".3f", "-0.161")
vr_i, vr_b = S["VR20"]
anchor("A22-23", f"VR20 {OBS['VR20']:.6f}; iid SE {g6(vr_i.se)}; {g6(vr_i.lo)} to {g6(vr_i.hi)}; mean "
       f"{g6(vr_i.mean)}; block SE {g6(vr_b.se)}; {g6(vr_b.lo)} to {g6(vr_b.hi)}; mean {g6(vr_b.mean)}",
       "VR20 1.035904; iid SE 0.0654613; 0.876646 to 1.13124; mean 0.996677; block SE 0.0607722; 0.918504 to "
       "1.15698; mean 1.03701")
chk("VR(20)", OBS["VR20"], ".3f", "1.036")
chk("VR iid mean", vr_i.mean, ".3f", "0.997")
mc("VR iid mean", vr_i.mean, vr_i.se / 100, 3)
chk_iv("VR iid percentile", vr_i, 2)
chk("VR block mean", vr_b.mean, ".3f", "1.037")
chk_iv("VR block percentile", vr_b, 2)
chk("VR iid SE", vr_i.se, ".3f", "0.065")
chk("VR block SE", vr_b.se, ".3f", "0.061")
chk("iid factor of (19.8)", (1 - 20 / T) / (1 - 1 / T), ".3f", "0.997")
chk("VR m", 20.0, ".0f", "20")
has("E4 95% of them", "with 95% of them between 0.88 and 1.13")
has("E4 blocks 95%", "with 95% between 0.92 and 1.16")
atmost("E4 ends' MC SE, rho_1", max(acf_i.lo_b, acf_i.hi_b, acf_b.lo_b, acf_b.hi_b), "0.0007")
atmost("E4 ends' MC SE, VR(20)", max(vr_i.lo_b, vr_i.hi_b, vr_b.lo_b, vr_b.hi_b), "0.002")
has("E4 MC sentence", "at most 0.0007 ($\\hat\\rho_1$) and 0.002 ($\\operatorname{VR}(20)$)")
mc("VR block mean", vr_b.mean, vr_b.se / sqrt(B), 3)

# ====================================================================== E5 and X7: the volatility, four schemes
se_s = D.s * sqrt((kurt - 1) / (4 * T))
anchor("A22-24", f"SE(s) annual {se_s * SQA:.6%}; iid {v_i.se:.6%}; block {v_b.se:.6%}; ratio {v_b.se / v_i.se:.6f}",
       "SE(s) annual 0.334127%; iid 0.331744%; block 1.296173%; ratio 3.907143")
chk("LM20's SE(s) annual points", 100 * se_s * SQA, ".2f", "0.33")
chk("LM20's SE(s) from printed", 1.2084 * sqrt((8.27 - 1) / (4 * T)) * 15.69, ".2f", "0.33")
chk("SE ratio vol", v_b.se / v_i.se, ".1f", "3.9")
chk("SE ratio from printed", 1.30 / 0.33, ".1f", "3.9")
assert round(100 * v_b.se / VOL) == 7 and round(100 * 1.30 / 18.96) == 7       # "about 7%"
assert v_i.se / VOL < 0.02 and 0.33 / 18.96 < 0.02                              # "under 2%"
MB = C.exp_tr(5, "mb", C.ELL, fx=False)
CB = C.exp_tr(6, "cb", C.ELL, fx=False)
rows = (("iid", IID), ("moving", MB), ("circular", CB), ("stationary", SB))
x7 = {}
for nm, d_ in rows:
    fv, fk, fs = C.summ(d_["vol"], VOL), C.summ(d_["Kelly"], KEL), C.summ(d_["SR"], OBS["SR"])
    x7[nm] = (fv, fk, fs)
anchor("A22-25", "; ".join(f"{nm} {x7[nm][0].se:.6%} {x7[nm][0].lo:.6%}-{x7[nm][0].hi:.6%} {x7[nm][1].se:.6f} "
                           f"{x7[nm][1].lo:.6f}-{x7[nm][1].hi:.6f} {x7[nm][2].se:.6f}" for nm in ("moving", "circular")),
       "moving 1.124419% 16.491993%-20.961504% 1.451922 1.580098-7.239242 0.246807; circular 1.122172% "
       "16.733319%-21.146934% 1.405551 1.696136-7.136766 0.244011")
x7_printed = {"iid": ("0.33", "18.3", "19.6", "1.10", "2.2", "6.5", "0.205"),
              "moving": ("1.12", "16.5", "21.0", "1.45", "1.6", "7.2", "0.247"),
              "circular": ("1.12", "16.7", "21.1", "1.41", "1.7", "7.1", "0.244"),
              "stationary": ("1.30", "16.5", "21.5", "1.34", "1.8", "7.1", "0.233")}
names = {"iid": "iid days", "moving": "Moving blocks", "circular": "Circular blocks", "stationary": "Stationary bootstrap"}
for nm, pr_ in x7_printed.items():
    fv, fk, fs = x7[nm]
    got = (f"{100 * fv.se:.2f}", f"{100 * fv.lo:.1f}", f"{100 * fv.hi:.1f}", f"{fk.se:.2f}", f"{fk.lo:.1f}",
           f"{fk.hi:.1f}", f"{fs.se:.3f}")
    assert got == pr_, (nm, got, pr_)
    for x, nd in ((100 * fv.se, 2), (fk.se, 2), (fs.se, 3)):
        assert not tie(x, f".{nd}f")
    mc(f"X7 {nm} vol SE", 100 * fv.se, 100 * fv.se_b, 2)
    mc(f"X7 {nm} vol ends", 100 * fv.lo, 100 * max(fv.lo_b, fv.hi_b), 1)
    mc(f"X7 {nm} Kelly ends", fk.lo, max(fk.lo_b, fk.hi_b), 1)
    row = (f"| {names[nm]} | {pr_[0]} | {pr_[1]}% to {pr_[2]}% | {pr_[3]} | {pr_[4]} to {pr_[5]} | {pr_[6]} |")
    has(f"X7 row {nm}", row)
atmost("X7 vol ends' MC SE, points", max(100 * max(x7[nm][0].lo_b, x7[nm][0].hi_b) for nm in x7), "0.04")
atmost("X7 Kelly ends' MC SE", max(max(x7[nm][1].lo_b, x7[nm][1].hi_b) for nm in x7), "0.05")
has("X7 MC sentence", "Monte Carlo standard errors (batch) of the ends: at most 0.04 points (volatility) and 0.05 (Kelly)")
chk("moving and circular SE", 100 * x7["circular"][0].se, ".2f", "1.12")
assert max(abs(x7[a][0].se - x7[b][0].se) for a in ("moving", "circular", "stationary")
           for b in ("moving", "circular", "stationary")) < min(x7[a][0].se for a in ("moving", "circular")) - x7["iid"][0].se
nb = ceil(T / C.ELL)
anchor("A22-39", f"{nb}; {nb * C.ELL}; {nb * C.ELL - T}", "41; 5945; 96")
chk("moving blocks needed", float(nb), ".0f", "41")
chk("days held", float(nb * C.ELL), ",.0f", "5,945")
chk("days cut", float(nb * C.ELL - T), ".0f", "96")
chk("moving blocks in the sample", float(T - C.ELL + 1), ",.0f", "5,705")
# section 5: the conditions of Lahiri's Theorems 3.1 and 3.3 against TR23's tails (LM15's maximum-likelihood t fit)
nu_t = float(stats.t.fit(R)[0])
chk("LM15's nu", nu_t, ".3f", "3.065")
assert 2 < nu_t < 4                       # moments of order just above 2 exist (Theorem 3.1), of order above 4 do not
has("M3 moments", "its moments exist only below order 3.065")
# review N1 and decision XB7 (revision 2): Theorem 3.1 covers the mean of R_t (moments above order 2 exist), not the
# statistics that average squares or products of returns, which need moments above order 4 (nu < 4); nor does the
# iid percentile interval's smooth-function result for R-bar/s, whose mean of R_t^2 needs a finite fourth moment
# revision 3 (F1, X3 item 1): the stationary bootstrap of the mean needs Theorem 3.3's moments, so it rests on practice
has("N1 mean of R_t", "That meets Theorem 3.1's moment condition for the mean of $R_t$ but not Theorem 3.3's, so the "
    "stationary bootstrap of the mean ([[eg:btest]]) rests on practice too.")
# (the variance ratio and the windows' spread use log returns, so the text says "returns", not R_t); revision 3 (F2,
# X3 item 1) adds rho_1(|r|) and Section 7's correlations and component shares, which average products of returns.
# The share of windows under water averages indicators, so the list names the component shares only.
has("N1 squares", "The volatility, Sharpe ratio and Kelly fraction, $\\operatorname{VR}(20)$, $\\hat\\rho_1(\\lvert "
    "r\\rvert)$, the windows' spread and Section 7's correlations and component shares average squares or products "
    "of returns.")
has("N1 practice", "For these, Theorem 3.1 needs moments above order 4, so their intervals rest on the method's "
    "practice")
has("F5 BCa", "BCa's adjustments are stated here without proof (Efron 1987).")
# revision 3: F3, F4, X3 item 6 and XB11 (視窗 for window) in the boxes
has("F4 zh VR", "$\\operatorname{VR}(20)$ 以區塊自助重抽法（block bootstrap）算出的信賴區間是 0.92 到 1.16")
has("F3 zh", "使平均報酬（mean return）為零")
has("X3 item 6 zh", "重抽樣（resampling）的分布（distribution）若有")
has("X3 item 6 zh null", "成立時的分布（distribution）")
has("XB11 window zh", "五年視窗（window）虧損比例")
assert "區塊信賴區間" not in NORM and "五年期間" not in NORM
has("XB7 fourth moment", "For $\\bar R/s$ one mean is of $R_t^2$, whose variance needs a finite fourth moment; "
    "[[LM15]]'s $t_{3.065}$ fit lacks it, so TR23's intervals rest on practice.")
# decision XB8 (revision 2): sqrt(A) annualization is a convention on simple returns ([[LM19]])
has("XB8 case", "its Sharpe ratio is 0.81 a year and its volatility 18.96% a year, both by [[LM19]]'s $\\sqrt A$ "
    "convention")
has("XB8 note", "the Sharpe ratio and the volatility are annualized by $\\sqrt A$, a convention on simple returns "
    "([[LM19]])")
has("XB8 relative error", "times $\\sqrt A$, a convention on simple returns, exact only for log returns on "
    "uncorrelated days ([[LM19]]; Lo 2002)")
assert "if days are uncorrelated" not in NORM and "as if days were uncorrelated" not in NORM
# X2 items 8 and 9, XB9 (revision 2)
has("X2 item 8", "TR23's log returns have the variance ratio $\\operatorname{VR}(20)=1.036$ ([[LM19]])")
has("X2 item 9", "Patton, A. J., D. N. Politis and H. White (2009)")
assert "本書譯名" not in NORM and "本書自訂" not in NORM and "基本區間" not in NORM and "百分位數區間" not in NORM
# the pitfall of section 5: a block of at least m = 1,231 days, by (22.3)
p_long = (1 - 1 / C.ELL) ** (C.M5 - 1)
print(f"Pr(a block lasts at least {C.M5} days) = {p_long:.6e}, 1 in {1 / p_long:,.0f}")
assert 4900 < 1 / p_long < 5100
chk("1 in N blocks hold a five-year window", round(1 / p_long, -3), ",.0f", "5,000")
has("pitfall m3", "almost no block (about 1 in 5,000) holds a five-year window")

# ====================================================================== X5: two paths (experiment 7)
pi_, ps_ = C.exp7()
rv_t, rv_i, rv_b = C.roll_vol(R), C.roll_vol(R[pi_]), C.roll_vol(R[ps_])
anchor("A22-27", f"TR23 {rv_t.max():.6%} ({int(rv_t.argmax()) + 60}), {rv_t.min():.6%} ({int(rv_t.argmin()) + 60}); "
       f"iid {rv_i.max():.6%}, {rv_i.min():.6%}; block {rv_b.max():.6%}, {rv_b.min():.6%}",
       "TR23 44.253961% (1468), 7.212284% (2872); iid 27.944004%, 11.647796%; block 44.253961%, 7.212284%")
assert D.dates[int(rv_t.argmax()) + 59] == "2008-12-02" and D.dates[int(rv_t.argmin()) + 59] == "2014-07-29"
chk("X5 TR23 max %", 100 * float(rv_t.max()), ".1f", "44.3")
chk("X5 TR23 min %", 100 * float(rv_t.min()), ".1f", "7.2")
chk("X5 iid max %", 100 * float(rv_i.max()), ".1f", "27.9")
chk("X5 iid min %", 100 * float(rv_i.min()), ".1f", "11.6")
chk("X5 block max %", 100 * float(rv_b.max()), ".1f", "44.3")
chk("X5 block min %", 100 * float(rv_b.min()), ".1f", "7.2")
chk("X5 iid path low, whole %", 100 * float(rv_i.min()), ".0f", "12")
chk("X5 iid path high, whole %", 100 * float(rv_i.max()), ".0f", "28")
has("X5 dates", "7.2% (window ending 29 July 2014) to 44.3% (ending 2 December 2008)")
has("X5 even range", "an even 12% to 28% a year")

# ====================================================================== E6, X6: the block-length grid (experiment 4)
G4 = C.exp4()
grid = {1: IID, C.ELL: SB, **G4}
KEYS = ("SR", "Kelly", "vol", "VR20")
ratio = {e: {k: float(grid[e][k].std() / IID[k].std()) for k in KEYS} for e in sorted(grid)}
relb = {e: {k: C.bse(grid[e][k], C.sd) / float(grid[e][k].std()) for k in KEYS} for e in sorted(grid)}
rmc = {e: {k: sqrt(relb[e][k] ** 2 + relb[1][k] ** 2) for k in KEYS} for e in sorted(grid) if e != 1}
mc2 = max(rmc[e][k] for e in C.GRID for k in KEYS)
mc145 = max(rmc[C.ELL][k] for k in KEYS)
anchor("A22-26", "; ".join(f"ell {e}: " + ", ".join(f"{ratio[e][k]:.6f}" for k in KEYS) for e in (2, 3, 145, 400)),
       "ell 2: 1.034172, 1.045390, 1.175718, 1.105529; ell 3: 1.050151, 1.067507, 1.352341, 1.166004; ell 145: "
       "1.133864, 1.219147, 3.907143, 0.928368; ell 400: 1.020577, 1.088324, 4.634482, 0.838485")
chk("X6 vol at 2", ratio[2]["vol"], ".2f", "1.18")
chk("X6 vol at 145", ratio[145]["vol"], ".2f", "3.91")
chk("X6 vol at 400", ratio[400]["vol"], ".2f", "4.63")
assert ratio[400]["vol"] > ratio[200]["vol"] > ratio[145]["vol"]                    # "still rising"
chk("X6 SR at 3", ratio[3]["SR"], ".2f", "1.05")
chk("X6 SR at 145", ratio[145]["SR"], ".2f", "1.13")
chk("X6 VR at 145", ratio[145]["VR20"], ".2f", "0.93")
chk("X6 SR peak", max(ratio[e]["SR"] for e in ratio), ".2f", "1.15")
chk("X6 Kelly peak", max(ratio[e]["Kelly"] for e in ratio), ".2f", "1.24")
# review N4 (revision 2): both peaks lie at 50 or 100 days, whose ratios differ by less than two Monte Carlo standard
# errors of their difference (B = 2,000 at each length), so the text names the range, not one length
for k in ("SR", "Kelly"):
    top2 = sorted(sorted(ratio, key=lambda e, k=k: ratio[e][k])[-2:])
    d50 = ratio[50][k] - ratio[100][k]
    se_d = sqrt((relb[50][k] * ratio[50][k]) ** 2 + (relb[100][k] * ratio[100][k]) ** 2)
    print(f"X6 {k}: largest at {top2}; ratio at 50 minus at 100 = {d50:.4f}, Monte Carlo SE {se_d:.4f}")
    assert top2 == [50, 100] and abs(d50) < 2 * se_d, (k, top2, d50, se_d)
has("X6 peaks", "peak at 1.15 and 1.24, between $\\ell=50$ and 100")
chk("SR growth 3 -> 145 %", 100 * (ratio[145]["SR"] / ratio[3]["SR"] - 1), ".0f", "8")
chk("Kelly growth 3 -> 145 %", 100 * (ratio[145]["Kelly"] / ratio[3]["Kelly"] - 1), ".0f", "14")
chk("SR growth from printed ratios %", 100 * (1.13 / 1.05 - 1), ".0f", "8")
atmost("MC SE of a ratio, B 2,000 %", 100 * mc2, "2.2")                          # review m1: 2.16%, not 2%
chk("MC SE of a ratio at 145 %", 100 * mc145, ".0f", "1")
has("X6 MC", "at most 2.2%, about 1% at 145")
chk("B grid", float(C.B_GRID), ",.0f", "2,000")

# ====================================================================== E7: the crash correlation (experiments 8, 9)
cc0, mod0, n0 = C.crash(C.PAIR)
rho0 = C.corr0(C.PAIR[:, 0], C.PAIR[:, 1])
pw_p = [C.pw((C.PAIR[:, j] - C.PAIR[:, j].mean()) ** 2)[0] for j in (0, 1)]
ELL_P = round(max(pw_p))
z0 = (C.PAIR[:, 0] - C.PAIR[:, 0].mean()) / C.PAIR[:, 0].std()
assert int((np.abs(z0) > 2).sum()) == n0 and not np.any(np.abs(np.abs(z0) - 2) < 1e-9)
anchor("A22-28", f"{n0} days; data {cc0:.6f}; rho {rho0:.8f}; model {mod0:.6f}; gap {cc0 - mod0:.6f}; V {C.V2:.6f}; "
       f"PW {pw_p[0]:.8f}, {pw_p[1]:.8f}; ell {ELL_P}",
       "223 days; data 0.788446; rho 0.57485847; model 0.859842; gap -0.071396; V 5.746431; PW 53.30552289, "
       "130.04998459; ell 130")
chk("event days", float(n0), ".0f", "223")
chk("data corr (LM16's)", cc0, ".3f", "0.788")
chk("model (16.10) (LM16's)", mod0, ".3f", "0.860")
chk("data corr, four decimals", cc0, ".4f", "0.7884")
chk("model, four decimals", mod0, ".4f", "0.8598")
chk("gap, four decimals", cc0 - mod0, ".4f", "-0.0714")
chk("gap from printed", 0.7884 - 0.8598, ".4f", "-0.0714")
chk("rho (LM16's)", rho0, ".4f", "0.5749")
chk("Var(Z | |Z| >= 2)", C.V2, ".4f", "5.7464")
chk("rho, five decimals", rho0, ".5f", "0.57486")
chk("model from printed rho and V", 0.57486 / sqrt(0.57486**2 + (1 - 0.57486**2) / 5.7464), ".4f", "0.8598")
chk("model from LM16's printed rho, three decimals", 0.5749 / sqrt(0.5749**2 + (1 - 0.5749**2) / 5.7464), ".3f",
    "0.860")
chk("PW Semiconductor", pw_p[0], ".1f", "53.3")
chk("PW FinancialInsurance", pw_p[1], ".1f", "130.0")
chk("ell pair", float(ELL_P), ".0f", "130")
cr = {e: C.exp_crash(e, ell) for e, ell in ((8, 1), (9, ELL_P))}
for e in (8, 9):
    gap = cr[e]["corr"] - cr[e]["model"]
    assert not np.any(gap == 0) and int((gap >= 0).sum()) == 0
dc9, dg9 = C.summ(cr[9]["corr"], cc0), C.summ(cr[9]["corr"] - cr[9]["model"], cc0 - mod0)
dg8 = C.summ(cr[8]["corr"] - cr[8]["model"], cc0 - mod0)
anchor("A22-29/30", f"iid gap {g6(dg8.lo)} to {g6(dg8.hi)}; block corr SE {g6(dc9.se)}, {g6(dc9.lo)} to {g6(dc9.hi)}; "
       f"gap SE {g6(dg9.se)}, {g6(dg9.lo)} to {g6(dg9.hi)}; days {int(cr[9]['days'].min())} to "
       f"{int(cr[9]['days'].max())}",
       "iid gap -0.101768 to -0.0366189; block corr SE 0.0216884, 0.75271 to 0.838384; gap SE 0.01554, "
       "-0.0937043 to -0.0327202; days 182 to 255")
chk("crash corr block SE", dc9.se, ".3f", "0.022")
chk_iv("crash corr block", dc9, 2)
chk("gap block SE", dg9.se, ".3f", "0.016")
chk_iv("gap block", dg9, 3)
chk_iv("gap iid", dg8, 3)
has("event days in resamples", "(182 to 255 in the block resamples below)")
assert (int(cr[9]["days"].min()), int(cr[9]["days"].max())) == (182, 255)
has("none of the gaps", "none of the 10,000 gaps reaches 0")

# ====================================================================== E8: PC1's shares (experiments 10-13)
pc = {}
for y, e_iid, e_blk in (("2017", 10, 11), ("2020", 12, 13)):
    Xy = C.year_rows(y)
    est = C.pc1_share(Xy)
    pws = [C.pw((Xy[:, j] - Xy[:, j].mean()) ** 2)[0] for j in range(Xy.shape[1])]
    ell_y = round(max(pws))
    si = C.summ(C.exp_pc1(e_iid, y, 1), est)
    vb = C.exp_pc1(e_blk, y, ell_y)
    sb = C.summ(vb, est)
    pc[y] = (Xy.shape[0], est, max(pws), ell_y, si, sb, C.bse(vb, lambda c: float(c.mean())))
n17, e17, p17, l17, si17, sb17, _ = pc["2017"]
n20, e20, p20, l20, si20, sb20, mb20 = pc["2020"]
anchor("A22-31", f"{n17}; {e17:.6f}; PW {p17:.6f}; ell {l17}; iid {g6(si17.lo)} to {g6(si17.hi)}; block SE "
       f"{g6(sb17.se)}, {g6(sb17.lo)} to {g6(sb17.hi)}",
       "246; 0.345248; PW 6.787814; ell 7; iid 0.306612 to 0.389299; block SE 0.0236247, 0.301267 to 0.394041")
anchor("A22-32", f"{n20}; {e20:.6f}; PW {p20:.6f}; ell {l20}; iid {g6(si20.lo)} to {g6(si20.hi)}; block SE "
       f"{g6(sb20.se)}, {g6(sb20.lo)} to {g6(sb20.hi)}; basic {g6(sb20.blo)} to {g6(sb20.bhi)}; mean {g6(sb20.mean)}",
       "245; 0.666199; PW 18.379069; ell 18; iid 0.585607 to 0.727843; block SE 0.0711251, 0.495546 to 0.759243; "
       "basic 0.573155 to 0.836853; mean 0.64962")
chk("2017 returns", float(n17), ".0f", "246")
chk("2017 share %", 100 * e17, ".1f", "34.5")
chk("2017 PW max", p17, ".2f", "6.79")
chk("2017 ell", float(l17), ".0f", "7")
chk_iv("2017 iid %", si17, 1, 100)
chk("2017 block SE points", 100 * sb17.se, ".1f", "2.4")
chk_iv("2017 block %", sb17, 1, 100)
chk("2020 returns", float(n20), ".0f", "245")
chk("2020 share %", 100 * e20, ".1f", "66.6")
chk("2020 share %, two decimals", 100 * e20, ".2f", "66.62")
chk("2020 PW max", p20, ".2f", "18.38")
chk("2020 ell", float(l20), ".0f", "18")
chk_iv("2020 iid %", si20, 1, 100)
chk("2020 block SE points", 100 * sb20.se, ".1f", "7.1")
chk("2020 block SE points, two decimals (P3)", 100 * sb20.se, ".2f", "7.11")
chk_iv("2020 block %", sb20, 1, 100)
chk("2020 block low, two decimals", 100 * sb20.lo, ".2f", "49.55")
chk("2020 block high, two decimals", 100 * sb20.hi, ".2f", "75.92")
chk_iv("2020 block basic %", sb20, 1, 100, basic=True)
# review M4: the mean (64.96%) and the bias (-1.66) had a Monte Carlo error of 0.08 points; the text prints the bias
# to one decimal and no separate mean (65.0 - 66.62 would give -1.6)
chk("2020 bias points, below the share", -100 * sb20.bias, ".1f", "1.7")
mc("2020 bias points", -100 * sb20.bias, 100 * mb20, 1)
has("E8 bias", "average about 1.7 points below the 2020 share (a bias)")
has("E8 two decimals", "from the ends to two decimals, 49.55% and 75.92%")
assert e20 - sb20.lo > sb20.hi - e20                                         # "a long left tail"
assert si17.hi < si20.lo and sb17.hi < sb20.lo                               # the intervals do not overlap
yrs = sorted({y for y in C.YEARS_U if y >= "2009"})
anchor("A22-40", f"{yrs[0]}-{yrs[-1]}: {len(yrs)}", "2009-2026: 18")
chk("LM11's calendar years", float(len(yrs)), ".0f", "18")
for y_ in yrs:                                                               # 2017 and 2020 are LM11's extremes
    s_ = C.pc1_share(C.year_rows(y_))
    assert e17 <= s_ + 1e-15 and s_ <= e20 + 1e-15, y_
# Problem 3, from the stem's two-decimal inputs
st_e, st_l, st_h, st_s = 66.62, 49.55, 75.92, 7.11
chk("P3 basic low", 2 * st_e - st_h, ".2f", "57.32")
chk("P3 basic high", 2 * st_e - st_l, ".2f", "83.69")
chk("P3 basic low, one decimal", 2 * st_e - st_h, ".1f", "57.3")
chk("P3 basic high, one decimal", 2 * st_e - st_l, ".1f", "83.7")
chk("P3 normal low", st_e - 1.96 * st_s, ".1f", "52.7")
chk("P3 normal high", st_e + 1.96 * st_s, ".1f", "80.6")
has("P3 option B", "52.7% to 80.6%")

# ====================================================================== E9: LM18's windows (experiments 14, 15)
M5 = C.M5
trf = [Fraction(str(x)) for x in D.tr]
under = sum(trf[i + M5] < trf[i] for i in range(len(trf) - M5))
sh0, sd0 = C.windows(r)
assert under == round(sh0 * (T - M5 + 1))
anchor("A22-33", f"m {M5}; windows {T - M5 + 1}; under {under}; {sh0:.6%}; sd {sd0:.6f}; sqrt(m) s_r "
       f"{sqrt(M5) * D.sr:.6f}", "m 1231; windows 4619; under 191; 4.135094%; sd 0.283113; sqrt(m) s_r 0.424791")
chk("m", float(M5), ",.0f", "1,231")
chk("windows", float(T - M5 + 1), ",.0f", "4,619")
chk("under water", float(under), ".0f", "191")
chk("share under water %", 100 * sh0, ".2f", "4.14")
chk("sd ln G", sd0, ".3f", "0.283")
chk("sqrt(m) s_r", sqrt(M5) * D.sr, ".3f", "0.425")
has("E9 stem", "against $\\sqrt m\\,s_r=0.425$ for independent five-year paths ([[LM18]])")
W14, W15 = C.exp_windows(14, C.ELL), C.exp_windows(15, 1)
ws14, wd14 = C.summ(W14["share"], sh0), C.summ(W14["sd"], sd0)
ws15, wd15 = C.summ(W15["share"], sh0), C.summ(W15["sd"], sd0)
nz14 = int((W14["share"] == 0).sum())
anchor("A22-34", f"share SE {g6(ws14.se)}; {g6(ws14.lo)} to {g6(ws14.hi)}; basic {g6(ws14.blo)} to {g6(ws14.bhi)}; "
       f"none {nz14}; sd SE {g6(wd14.se)}; {g6(wd14.lo)} to {g6(wd14.hi)}; mean {g6(wd14.mean)}",
       "share SE 0.0992552; 0 to 0.330158; basic -0.247456 to 0.0827019; none 3248; sd SE 0.1238; 0.196043 to "
       "0.67511; mean 0.385543")
anchor("A22-35", f"share SE {g6(ws15.se)}; sd {g6(wd15.lo)} to {g6(wd15.hi)}",
       "share SE 0.0841454; sd 0.192662 to 0.583806")
chk("windows share SE points", 100 * ws14.se, ".1f", "9.9")
mc("windows share SE points", 100 * ws14.se, 100 * ws14.se_b, 1)
assert ws14.lo == 0 and nz14 > B * 0.025                    # the lower end is exactly 0: more than 250 resamples have none
chk_iv("windows share %", ws14, 0, 100)                     # review M4: 33.0% had a Monte Carlo error of 0.57 points
chk_iv("windows share basic %", ws14, 0, 100, basic=True)
chk("windows basic low from printed", 2 * 4.14 - 33, ".0f", "-25")
has("P8 basic end", "$2\\times4.14%-33%\\approx-25%$")
has("E9 basic", "The basic interval, -25% to 8%, leaves the range of a share")
has("zh basic end", "下界約是 -25%")
has("zh E8 bias", "比估計值低約 1.7 個百分點")
chk("resamples with none", float(nz14), ",.0f", "3,248")
chk("iid share SE points", 100 * ws15.se, ".1f", "8.4")
mc("iid share SE points", 100 * ws15.se, 100 * ws15.se_b, 1)
chk("sd ln G block SE", wd14.se, ".3f", "0.124")
mc("sd ln G block SE", wd14.se, wd14.se_b, 3)
chk_iv("sd ln G block", wd14, 2)
chk("sd ln G resampled mean", wd14.mean, ".3f", "0.386")
mc("sd ln G resampled mean", wd14.mean, wd14.se / sqrt(B), 3)
chk_iv("sd ln G iid", wd15, 2)
chk("sd ln G iid mean", wd15.mean, ".3f", "0.357")                               # review M2 (A22-35)
mc("sd ln G iid mean", wd15.mean, C.bse(W15["sd"], lambda c: float(c.mean())), 3)
has("E9 iid mean", "(iid days: 0.19 to 0.58, mean 0.357)")
assert sd0 < wd15.mean < wd14.mean < sqrt(M5) * D.sr                             # 0.283 < 0.357 < 0.386 < 0.425
# why iid days give 0.357, not 0.425: overlapping windows centred on their own mean understate the variance by about
# m/T (LM19's iid factor of VR(m), 0.790 at m = 1,231), and a mean of standard deviations lies below the square root
# of the mean variance. Exact expected variance about the windows' own mean under iid draws from F-hat:
nw = T - M5 + 1
lag = np.arange(-(M5 - 1), M5)
evar = M5 * D.sr**2 - D.sr**2 * float(((nw - np.abs(lag)) * (M5 - np.abs(lag))).sum()) / nw**2
print(f"windows, iid: E var / (m s_r^2) = {evar / (M5 * D.sr**2):.4f} against 1 - m/T = {1 - M5 / T:.4f}; "
      f"sqrt(E var) = {sqrt(evar):.4f}; mean sd {wd15.mean:.4f}; mean var {float((W15['sd'] ** 2).mean()):.4f}")
assert abs(evar / (M5 * D.sr**2) - (1 - M5 / T)) < 0.05                          # "by about m/T"
assert abs(float((W15["sd"] ** 2).mean()) - evar) < 3 * float((W15["sd"] ** 2).std()) / sqrt(B)
assert wd15.mean < sqrt(float((W15["sd"] ** 2).mean()))                          # the mean of SDs lies lower still
# review N3 (revision 2): m/T = 21% is the shortfall about m r-bar (LM19's centring); about the windows' own mean,
# as 0.283 is computed, the exact iid factor is 0.757, a shortfall of 24%
print(f"m/T = {M5 / T:.4f}; shortfall about the windows' own mean = {1 - evar / (M5 * D.sr**2):.4f}")
chk("E9 shortfall about their own mean %", 100 * (1 - evar / (M5 * D.sr**2)), ".0f", "24")
has("E9 m/T", "understate the variance even for independent days, by about $m/T$ ([[LM19]]'s "
    "$\\operatorname{VR}(m)$), 24% about their own mean")
# blocks keep LM19's variance ratios above 1 below 340 days (LM19: "first falls below 1 at m = 340")
vr_m = {m_: float(C.vr(r[None, :], m_)[0]) for m_ in range(2, M5 + 1)}
assert all(vr_m[m_] > 1 for m_ in range(2, 340)) and vr_m[340] < 1
chk("first m with VR(m) below 1", 340.0, ".0f", "340")
has("E9 340", "variance ratios above 1 below 340 days")
# closing check item 3: the pitfall's "below 1 beyond 340 days" holds up to the windows' m = 1,231
assert all(vr_m[m_] < 1 for m_ in range(340, M5 + 1))
has("C3 pitfall 340", "variance ratios below 1 beyond 340 days")
# closing fixes: X4 item 7 (Sharpe ratios), C22 item 1 (the docstring contradicts the columns), X4 item 5 (Sources)
has("X4.7 r_f", "while Volume IV's Sharpe ratios set $r_f=0$")
has("C1 docstring", "`stationary` and `circular`, but its docstring calls them `b_sb` and `b_cb`")
has("X4.5 forest", "1.8 to 6.6 (blocks). In-sample. Source: as [[ex:case]].")
has("X4.5 ell", "about 1% at 145. In-sample. Source: as [[ex:case]].")
has("N2", "that lift the resampled mean to 0.386")
assert abs(wd14.mean - sqrt(M5) * D.sr) < abs(wd14.mean - sd0)                   # the blocks' mean is nearer 0.425
assert 0.2 < nz14 / B < 0.4                                                      # "a third of the resamples"
# the note of the exhibit of earlier estimates: bounds on the ends' batch standard errors
atmost("X8 windows' share ends, points", 100 * max(ws14.lo_b, ws14.hi_b), "0.6")
atmost("X8 component shares' ends, points", 100 * max(sb17.lo_b, sb17.hi_b, sb20.lo_b, sb20.hi_b), "0.16")
atmost("X8 other ends", max(dc9.lo_b, dc9.hi_b, dg9.lo_b, dg9.hi_b, wd14.lo_b, wd14.hi_b, vr_b.lo_b, vr_b.hi_b), "0.005")
has("X8 MC sentence", "at most 0.6 points for the windows' share, 0.16 points for the component shares and 0.005 "
    "elsewhere")

# ====================================================================== E10: bootstrap tests (experiments 16-18)
tests = {}
for lab, x, plan in (("7%", R[D.pre], ((16, 1), (17, None))), ("full", R, ((18, None),))):
    t0 = float(C.tstat(x[None, :])[0])
    ell_t = round(C.pw((x - x.mean()) ** 2)[0])
    p_n = 2 * float(stats.norm.sf(abs(t0)))
    for e, ell0 in plan:
        ell = ell_t if ell0 is None else ell0
        tb = C.exp_test(e, x, ell)
        assert not np.any(np.abs(tb) == abs(t0))
        k = int((np.abs(tb) >= abs(t0)).sum())
        tests[e] = (t0, p_n, ell, k, float(tb.std()))
t16, t17, t18 = tests[16], tests[17], tests[18]
anchor("A22-36", f"t {t16[0]:.6f}; p {t16[1]:.8f}; ell {t17[2]}; iid {t16[3]}, sd {t16[4]:.6f}; block {t17[3]}, "
       f"sd {t17[4]:.6f}", "t 2.046297; p 0.04072720; ell 108; iid 408, sd 1.006101; block 477, sd 1.025547")
anchor("A22-37", f"t {t18[0]:.6f}; p {t18[1]:.8f}; ell {t18[2]}; {t18[3]} of {B}",
       "t 3.955678; p 0.00007632; ell 145; 0 of 10000")
chk("7% t-stat (LM21's)", t16[0], ".2f", "2.05")
chk("7% normal p (LM21's)", t16[1], ".3f", "0.041")
chk("iid count", float(t16[3]), ".0f", "408")
p16, p17 = t16[3] / B, t17[3] / B
chk("iid p", p16, ".3f", "0.041")
chk("iid p MC SE", sqrt(p16 * (1 - p16) / B), ".3f", "0.002")
chk("ell 7% regime", float(t17[2]), ".0f", "108")
chk("block count", float(t17[3]), ".0f", "477")
chk("block p", p17, ".3f", "0.048")
chk("block p MC SE", sqrt(p17 * (1 - p17) / B), ".3f", "0.002")
has("p-values printed", "$0.041\\pm0.002$")
has("p-values printed", "$0.048\\pm0.002$")
chk("sd of t, block", t17[4], ".2f", "1.03")
chk("sd of t, iid", t16[4], ".2f", "1.01")
chk("full t-stat", t18[0], ".2f", "3.96")
chk("full normal p x1e5", t18[1] * 1e5, ".1f", "7.6")
has("full normal p", "$7.6\\times10^{-5}$")
assert t18[3] == 0 and t18[2] == 145
# review C1: zero hits make (22.4) zero but only bound the ideal p-value; the one-sided 95% bound after 0 of B is
# 1 - 0.05^(1/B) = 2.996/B
bound0 = 1 - 0.05 ** (1 / B)
chk("95% bound after zero hits", bound0, ".4f", "0.0003")
chk("3/B", 3 / B, ".4f", "0.0003")
assert abs(bound0 * B - 3) < 0.01
has("C1 bound", "zero hits only bound the p-value: below about $3/B=0.0003$ at the 95% level")
assert bound0 < 0.05                                                              # "the decision at the 5% level stands"
# knowledge check of section 8 (experiment 19)
tb_u = C.exp19()
anchor("A22-41", f"mean {tb_u.mean():.6f}; share {float((tb_u >= t18[0]).mean()):.4f}", "mean 3.960818; share 0.5023")
chk("uncentred mean t", float(tb_u.mean()), ".2f", "3.96")
assert abs(float((tb_u >= t18[0]).mean()) - 0.5) < 0.01                           # "half of them"
# Problem 7
chk("P7 p", p17, ".4f", "0.0477")
chk("P7 MC SE", sqrt(p17 * (1 - p17) / B), ".4f", "0.0021")
chk("P7 1 - p", 1 - p17, ".4f", "0.9523")
chk("P7 p + 2 SE", p17 + 2 * sqrt(p17 * (1 - p17) / B), ".3f", "0.052")
chk("P7 p + 2 SE from printed", 0.0477 + 2 * 0.0021, ".3f", "0.052")
chk("P7 B", p17 * (1 - p17) / 1e-6, ",.0f", "45,425")
chk("P7 B from printed", 0.0477 * 0.9523 / 1e-6, ",.0f", "45,425")
has("P7 about", "About 45,000")

# ====================================================================== Section 9 and Problem 10: the printed code
blocks = [textwrap.dedent(b) for b in re.findall(r"```python\n(.*?)```", TEXT, flags=re.DOTALL)]
assert len(blocks) == 3, len(blocks)
code9 = blocks[0]
ns: dict[str, Any] = {"R": R}
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    exec(code9, ns)  # noqa: S102 (the module's own printed code)
assert buf.getvalue().split() == ["True", "True", "True"], buf.getvalue()
has("code 9 output", "# True")
stationary_idx = ns["stationary_idx"]
g_a, g_b = C.gen(20), C.gen(20)
assert all(np.array_equal(stationary_idx(g_a, T, 145), C.sb_row(g_b, T, 145)) for _ in range(5))
same = []
for cls, fn in ((StationaryBootstrap, C.sb_row), (CircularBlockBootstrap, C.cb_row), (MovingBlockBootstrap, C.mb_row)):
    g1, g2 = C.gen(20), C.gen(20)                                               # experiment 20: twins
    bs = cls(C.ELL, R, seed=g1)
    ok = True
    for _ in bs.bootstrap(3):
        ok &= bool(np.array_equal(cast(np.ndarray, bs.index), fn(g2, T, C.ELL)))
    same.append(ok)
anchor("A22-42", f"same indices {same}", "same indices [True, True, True]")
assert all(same)
for line in code9.splitlines() + blocks[1].splitlines() + blocks[2].splitlines():
    assert len(line) <= 80, ("code line over 80 characters", line)
buf = io.StringIO()
ns2: dict[str, Any] = {"R": R, "np": np}
with contextlib.redirect_stdout(buf):
    exec(blocks[1], ns2)  # noqa: S102
ci_lo, ci_hi = ci("percentile", "SR")
adj = sqrt(D.A / 246.12)                       # the printed code uses A = 246.12, the sample's A rounded
c2 = ns2["res"].confidence_interval
assert abs(float(c2.low) * adj - ci_lo) < 1e-12 and abs(float(c2.high) * adj - ci_hi) < 1e-12
assert f"{float(c2.low):.6f}".startswith("0.4157") and f"{float(c2.high):.6f}".startswith("1.2142")
has("SciPy code comment", "# low=0.4157... high=1.2142...")
assert ns2["A"] == 246.12 and abs(sqrt(246.12) - SQA) < 1e-4                  # the printed A changes the 5th digit only
code10 = blocks[2]
buf = io.StringIO()
ns3: dict[str, Any] = {"R": R, "np": np, "stationary_idx": stationary_idx, "A": 246.12}   # as Section 9 sets it
with contextlib.redirect_stdout(buf):
    exec(code10, ns3)  # noqa: S102
q10 = np.quantile(ns3["vol"], [0.025, 0.975], method="inverted_cdf")
assert np.allclose(q10 * adj, [v_b.lo, v_b.hi], rtol=0, atol=1e-15), (q10, v_b.lo, v_b.hi)
assert f"{q10[0]:.6f}".startswith("0.1648") and f"{q10[1]:.6f}".startswith("0.2150")
has("P10 output", "It prints 0.1648... and 0.2150...")
has("experiment 20 seed", "np.random.default_rng([20, 20261011])")

# ====================================================================== the other problems
three = np.array([0.01, -0.02, 0.04])
res3 = three[np.array(list(product(range(3), repeat=3)))].mean(axis=1)
s3, su3 = float(three.std()), float(three.std(ddof=1))
anchor("A22-43", f"s {s3:.6%}; ideal {res3.std():.6%}; s_u/sqrt3 {su3 / sqrt(3):.6%}; s/3 {s3 / 3:.6%}",
       "s 2.449490%; ideal 1.414214%; s_u/sqrt3 1.732051%; s/3 0.816497%")
chk("P1 s %", 100 * s3, ".4f", "2.4495")
chk("P1 ideal SE %", 100 * float(res3.std()), ".3f", "1.414")
chk("P1 s_u/sqrt3 %", 100 * su3 / sqrt(3), ".3f", "1.732")
chk("P1 s/3 %", 100 * s3 / 3, ".3f", "0.816")
chk("P1 resamples", 27.0, ".0f", "27")
anchor("A22-44", f"{ceil(0.025 * B)}, {ceil(0.975 * B)}; {ceil(0.05 * B)}, {ceil(0.95 * B)}", "250, 9750; 500, 9500")
has("P2 option A", "the 500th and 9,500th smallest values")
has("P2 option B", "the 250th and 9,750th smallest values")
anchor("A22-46", f"{1 / C.ELL:.6f}; {1 - 1 / C.ELL:.6f}; {C.ELL / T:.6f}", "0.006897; 0.993103; 0.024791")
chk("P5 1/ell", 1 / C.ELL, ".4f", "0.0069")
chk("P5 1 - 1/ell", 1 - 1 / C.ELL, ".4f", "0.9931")
chk("P5 ell/T", C.ELL / T, ".4f", "0.0248")
b21 = C.exp_tr(21, "sb", 2, b=C.B_GRID, fx=False)
m21 = float(b21["acf"].mean())
bs21 = C.bse(b21["acf"], lambda c: float(c.mean()))
keep145 = (1 - 1 / C.ELL) + (1 / C.ELL) / T
keep2 = 0.5 + 0.5 / T
anchor("A22-47", f"{1 + (T - 1) / C.ELL:.6f}; {(1 - 1 / C.ELL) ** 59:.6f}; {keep145 * OBS['acf']:.6f}, "
       f"{keep2 * OBS['acf']:.6f}; e21 {m21:.6f} ({bs21:.6f})",
       "41.331034; 0.664775; 0.159508, 0.080321; e21 0.078312 (0.000476)")
chk("P6 blocks", 1 + (T - 1) / C.ELL, ".1f", "41.3")
chk("P6 other positions", float(T - 1), ",.0f", "5,848")
chk("P6 long block", (1 - 1 / C.ELL) ** 59, ".3f", "0.665")
chk("P6 prediction at 145", keep145 * OBS["acf"], ".2f", "0.16")
chk("P6 prediction at 2", keep2 * OBS["acf"], ".2f", "0.08")
chk("P6 prediction at 145 from printed", (1 - 1 / 145) * 0.161, ".2f", "0.16")
chk("P6 prediction at 2 from printed", 0.5 * 0.161, ".2f", "0.08")
chk("P6 e21 mean", m21, ".3f", "0.078")
chk("P6 e21 batch SE", bs21, ".4f", "0.0005")
chk("P6 e3 mean", acf_b.mean, ".3f", "0.156")
# review K1: the expectation at ell = 2 (experiment 26, B = 200,000) and experiment 21's distance from it
b26 = C.exp_tr(26, "sb", 2, b=C.B_26, fx=False)["acf"]
m26, bs26 = float(b26.mean()), C.bse(b26, lambda c: float(c.mean()))
chk("P6 e26 mean", m26, ".4f", "0.0797")
chk("P6 e26 batch SE", bs26, ".5f", "0.00005")
mc("P6 e26 mean", m26, bs26, 4)
chk("P6 e26 mean, three decimals", m26, ".3f", "0.080")
chk("P6 e21 below the expectation, in its batch SEs", (m26 - m21) / bs21, ".0f", "3")
chk("B of experiment 26", float(C.B_26), ",.0f", "200,000")
has("K1 text", "At $\\ell=2$ the expectation is about 0.080 (experiment 26, $B=200,000$: $0.0797\\pm0.00005$)")


def boot_acf1_expectation(ell: float) -> tuple[float, float]:
    """First-order expectation of a stationary resample's lag-1 autocorrelation of |r| (19.5), E[numerator] /
    E[denominator], with and without the centring on each resample's own mean. Day indices wrap (day T, then day 1);
    positions k apart share a block with probability (1 - 1/ell)^k, else they are independent uniform days."""
    a = np.abs(r)
    mu, ac = float(a.mean()), a - a.mean()
    q = 1 - 1 / ell
    spec = np.fft.rfft(ac)
    cov = np.fft.irfft(spec * np.conj(spec), n=T) / T                      # circular autocovariances c_0 .. c_(T-1)
    k_ = np.arange(T)
    qk = q**k_
    var_mean = (T * cov[0] + 2 * float(((T - k_[1:]) * qk[1:] * cov[1:]).sum())) / T**2
    num = (T - 1) * q * cov[1] - (T + 1) * var_mean + 2 / T * float((qk * cov).sum())
    den = T * cov[0] - T * var_mean
    assert mu > 0
    return num / den, (T - 1) * q * cov[1] / (T * cov[0])


x145, x145_raw = boot_acf1_expectation(C.ELL)
x2, x2_raw = boot_acf1_expectation(2)
print(f"first-order expectations: ell 145 {x145:.5f} (no own-mean centring {x145_raw:.5f}); ell 2 {x2:.5f} "
      f"({x2_raw:.5f}); experiment 3 {acf_b.mean:.5f}, experiment 26 {m26:.5f}")
assert f"{x145:.3f}" == "0.156" and f"{x145_raw:.2f}" == "0.16" and x145 < x145_raw - 0.003   # the centring lowers it
assert abs(x2 - m26) < 1e-3     # agrees at ell = 2 (0.0801 against 0.0797; the ratio's own bias, order 1/T, is the rest)
has("K1 mechanism", "Each resample is centred on its own mean, which varies more under long blocks")
cnt = np.array([min(t, C.ELL, T - C.ELL + 1, T - t + 1) for t in range(1, T + 1)])
emb = float((cnt * R).sum() / cnt.sum())
anchor("A22-49", f"{cnt[0]}, {cnt[C.ELL - 1]}; {emb:.8%}; {1e4 * (emb - D.Rb):.6f} bp; {emb / D.Rb - 1:+.6%}",
       "1, 145; 0.06018495%; -0.232011 bp; -3.711880%")
assert cnt.sum() == C.ELL * (T - C.ELL + 1) and cnt[0] == 1 and cnt[C.ELL - 1] == C.ELL
assert int((cnt < C.ELL).sum()) == 2 * 144                                           # the first and last 144 days
chk("P9 block mean %", 100 * emb, ".6f", "0.060185")
chk("P9 difference %", 100 * (emb - D.Rb), ".5f", "-0.00232")
chk("P9 difference from printed", 0.060185 - 0.062505, ".5f", "-0.00232")
chk("P9 bp", 1e4 * (emb - D.Rb), ".2f", "-0.23")
chk("P9 percent", 100 * (emb / D.Rb - 1), ".1f", "-3.7")
chk("P9 percent from printed", 100 * (0.060185 / 0.062505 - 1), ".1f", "-3.7")
chk("P9 last days", 144.0, ".0f", "144")
# review K2: why the sign is negative
chk("P9 first 144 days' mean %", 100 * float(R[:144].mean()), ".2f", "0.13")
chk("P9 last 144 days' mean %", 100 * float(R[-144:].mean()), ".2f", "0.28")
assert R[:144].mean() > D.Rb and R[-144:].mean() > D.Rb                           # both count less and lie above R-bar
se_rb = D.s / sqrt(T)
chk("P9 difference in standard errors of R-bar", abs(emb - D.Rb) / se_rb, ".2f", "0.15")
chk("P9 the same with s_u", abs(emb - D.Rb) / (float(R.std(ddof=1)) / sqrt(T)), ".2f", "0.15")
has("P9 K2", "Both stretches averaged more than $\\bar R$ (0.13% and 0.28% a day), so the block mean is lower")
has("P9 SEs", "or 0.15 standard errors of $\\bar R$")
R10 = R[~D.pre]
k10 = float(R10.mean() / R10.var())
ell10 = round(C.pw((R10 - R10.mean()) ** 2)[0])
v22 = C.summ(C.exp_kelly_only(22, R10, "iid", 1), k10)
v23 = C.summ(C.exp_kelly_only(23, R10, "sb", ell10), k10)
anchor("A22-50", f"{R10.size}; {k10:.6f}; ell {ell10}; iid {g6(v22.lo)} to {g6(v22.hi)}; block {g6(v23.lo)} to "
       f"{g6(v23.hi)}", "2772; 6.062185; ell 36; iid 2.78781 to 9.57566; block 2.6444 to 10.1389")
chk("P11 f_hat", k10, ".2f", "6.06")
chk("P11 ell", float(ell10), ".0f", "36")
chk_iv("P11 iid", v22, 1)
chk_iv("P11 block", v23, 1)
assert k_i.lo < v22.lo < k_i.hi < v22.hi                                          # overlap "from 2.8 to 6.5"
assert k_b.lo < v23.lo < k_b.hi < v23.hi                                          # overlap "from 2.6 to 7.1"
assert (f"{v22.lo:.1f}", f"{k_i.hi:.1f}", f"{v23.lo:.1f}", f"{k_b.hi:.1f}") == ("2.8", "6.5", "2.6", "7.1")
has("P11 overlap", "from 2.8 to 6.5 and from 2.6 to 7.1")
has("P11 stem", "Compare them with the full sample's 2.2 to 6.5 (iid) and 1.8 to 7.1 (blocks)")
has("P11 regime days", "The full sample includes the regime's 2,772 days")

# ====================================================================== words that carry numbers
has("widget", "the 1,000 resampled values")
has("five returns", "+1.2%, −0.8%, +0.3%, −2.5% and +0.6%".replace("−", "-"))
has("three returns", "+1%, −2% and +4%".replace("−", "-"))
for e in (*range(1, 24), 26):                                                    # experiments 1-23 and 26 are named
    assert re.search(rf"[Ee]xperiments?[^.]{{0,70}}?\b{e}\b", NORM), e

# ====================================================================== chart files (data/lm22_charts.py)
CH = ROOT / "src" / "data"
if (CH / "lm22-ell.json").exists():
    ell_spec = json.loads((CH / "lm22-ell.json").read_text(encoding="utf-8"))
    xs = ell_spec["x"]["values"]
    for s_ in ell_spec["series"]:
        key = {"Sharpe ratio": "SR", "Kelly fraction": "Kelly", "Volatility": "vol", "VR(20)": "VR20"}[s_["name"]]
        for x_, y_ in zip(xs, s_["y"], strict=True):
            assert f"{y_:.2f}" == f"{ratio[int(x_)][key]:.2f}", (key, x_, y_)
    vls = sorted(a["x"] for a in ell_spec["ann"] if a["type"] == "vline")
    assert vls == [round(pwR[0], 2), round(pwR2[0], 2)], vls
    sr_spec = json.loads((CH / "lm22-srhist.json").read_text(encoding="utf-8"))
    vx = sorted(a["x"] for a in sr_spec["ann"] if a["type"] == "vline")
    assert vx == sorted([round(sr_i.lo, 4), round(sr_i.hi, 4), round(sr_b.lo, 4), round(sr_b.hi, 4),
                         round(OBS["SR"], 4)]), vx
    rv_spec = json.loads((CH / "lm22-rollvol.json").read_text(encoding="utf-8"))
    for s_, v_ in zip(rv_spec["series"], (rv_t, rv_i, rv_b), strict=True):
        assert f"{max(s_['y']):.1%}" == f"{v_.max():.1%}" and f"{min(s_['y']):.1%}" == f"{v_.min():.1%}", s_["name"]
    kspec = json.loads((CH / "lm22-kelly.json").read_text(encoding="utf-8"))
    ends = [(ln["from"][0], ln["to"][0]) for ln in kspec["lines"] if ln["from"][1] == ln["to"][1]]
    printed_k = [("2.10", "6.46"), ("2.2", "6.5"), ("2.1", "6.4"), ("2.2", "6.5"), ("1.8", "7.1"), ("1.5", "6.7"),
                 ("2.1", "6.1"), ("1.8", "6.6")]
    for (a_, b_), (pa, pb) in zip(ends, printed_k, strict=True):
        nd = len(pa.split(".")[1])
        assert (f"{a_:.{nd}f}", f"{b_:.{nd}f}") == (pa, pb), (a_, b_, pa, pb)
    print("CHECK chart files: X2, X3, X5 and X6 carry the values the text cites")
    N_CHECKS += 1
else:
    print("chart files not written yet (run data/lm22_charts.py); their values are not checked")

# numbers in the text that no check above covers (for the writer's and the reviewer's eyes; equation tags, section
# numbers, years in references, experiment numbers and the like are expected here)
body = NORM.split("## Glossary")[0].split("\n---\n", 1)[1]
body = re.sub(r"\(\d{1,2}\.\d{1,2}\)|\\tag\{[^}]*\}|\[\[[^\]]*\]\]|\{#[\w-]+\}|lo=[\d,]+|https?://\S+", " ", body)
nums = sorted({x.rstrip(".,") for x in re.findall(r"(?<![\w.])\d[\d,]*(?:\.\d+)?", body)} - {""})
uncovered = [x for x in nums if not any(re.search(r"(?<![\d.])" + re.escape(x) + r"(?!\d)", c) for c in COVERED)]
print("numbers in the text not covered by a check:", ", ".join(uncovered))

print()
if NEAR:
    print("near a rounding boundary (correctly rounded; listed for the anchors' flags):")
    for s_ in NEAR:
        print("  ", s_)
if ANCHOR_DIFFS:
    print("anchors that differ (reported, not forced):")
    for s_ in ANCHOR_DIFFS:
        print("  ", s_)
else:
    print("every anchor compared agrees")
print(f"\nall {N_CHECKS} checks passed")
