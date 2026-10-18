"""Every number that LM15 (Distributions in Finance) prints, computed from TR23 and checked against src/lm15.md.

Run:  uv run python data/lm15_numbers.py      (after data/vol3_series.py has written processed/vol3_taiex.parquet)

Input: data/processed/vol3_taiex.parquet, built and checked by data/vol3_series.py: TR23, the TAIEX total-return
index (FinMind TaiwanStockTotalReturnIndex, data_id TAIEX, retrieved 2026-10-18), closes 2003-01-02 .. 2026-10-08,
and R, its simple daily return. T = 5,849 returns from 2003-01-03; moments divide by T (or by the size of the part in
use); years = calendar days / 365.25; A = T / years. Counts against a threshold use the guard of PITFALLS section 5
(R <= -x + 1e-12, R >= x - 1e-12) and are asserted equal to an exact recount with fractions.Fraction from the
two-decimal closes. An empirical quantile is LM14's order statistic R_(ceil(uT)) (np.quantile, inverted_cdf). LM15
simulates nothing, so no generator is created. The text of src/lm05.md is read for the values LM15 cites from LM5.

The script prints each check and asserts three things:
  * chk(label, value, fmt, printed): the value prints as printed, does not sit on a rounding tie at that precision
    (a reader rounding by hand could go either way), and the printed string appears in src/lm15.md (after replacing
    the minus sign by '-', '{,}' by ',' and '\\%' by '%');
  * a printed figure that the text derives from other printed figures is recomputed from those printed strings
    (PITFALLS section 7), with the same chk;
  * has(label, text): a date, a count or a phrase appears in the text as written.
It compares its values with the anchors of plans/vol-3-anchors.md (LM15) and reports a difference without forcing
it, and it checks that every [[ex:...]] and [[eg:...]] label resolves and every exhibit is cited. It ends by printing
"all N checks passed".
"""
import itertools
import math
import re
import warnings
from datetime import date
from fractions import Fraction
from pathlib import Path

import numpy as np
import polars as pl
from numpy.typing import NDArray
from scipy import integrate, optimize, special, stats

Vec = NDArray[np.float64]

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TR23 = HERE / "processed" / "vol3_taiex.parquet"
MD = ROOT / "src" / "lm15.md"
TEXT = MD.read_text(encoding="utf-8")
NORM = TEXT.replace("{,}", ",").replace("−", "-").replace("\\%", "%")
LM05 = (ROOT / "src" / "lm05.md").read_text(encoding="utf-8").replace("{,}", ",").replace("−", "-")
ANCHORS_MD = ROOT / "plans" / "vol-3-anchors.md"
EPS = 1e-12
LIMIT_CHANGE = "2015-06-01"          # the daily price limit was 7% before this date and 10% from it on
N_CHECKS = 0
ANCHOR_DIFFS: list[str] = []


def in_text(printed: str) -> bool:
    """The printed number appears in the text as a whole number (not inside a longer one: 2.09 is not in 2.095)."""
    return re.search(r"(?<![\d.])" + re.escape(printed) + r"(?![\d])", NORM) is not None


def tie(value: float, fmt: str) -> bool:
    """True when value lies on a rounding boundary of fmt (".3f", ".2%"...; 'g' formats are not tested)."""
    m = re.search(r"\.(\d+)([f%])", fmt)
    if not m:
        return False
    d = int(m.group(1))
    scaled = abs(value) * 10**d * (100 if m.group(2) == "%" else 1)
    return abs(scaled - math.floor(scaled) - 0.5) < 1e-6


def chk(label: str, value: float, fmt: str, printed: str, in_md: bool = True) -> None:
    """A printed value: it must print as `printed`, not sit on a tie, and appear in src/lm15.md."""
    global N_CHECKS
    got = format(value, fmt)
    print(f"CHECK {label}: {got} (printed {printed}) {'ok' if got == printed else 'MISMATCH'}")
    assert got == printed, (label, got, printed)
    assert not tie(value, fmt), ("rounding tie: print more digits", label, value)
    if in_md:
        assert in_text(printed), f"{label}: {printed!r} not found in src/lm15.md"
    N_CHECKS += 1


def chk_s(label: str, got: str, printed: str) -> None:
    """A value formatted by a helper (scientific, significant figures); it must equal the printed text."""
    global N_CHECKS
    print(f"CHECK {label}: {got} (printed {printed}) {'ok' if got == printed else 'MISMATCH'}")
    assert got == printed, (label, got, printed)
    assert printed in NORM, f"{label}: {printed!r} not found in src/lm15.md"
    N_CHECKS += 1


def has(label: str, text: str) -> None:
    global N_CHECKS
    t = text.replace("{,}", ",").replace("−", "-").replace("\\%", "%")
    assert t in NORM, f"{label}: {text!r} not found in src/lm15.md"
    print(f"CHECK {label}: '{text}' in text ok")
    N_CHECKS += 1


def lm05_has(label: str, text: str) -> None:
    """A value LM15 cites from LM5 must still be printed there."""
    global N_CHECKS
    assert text in LM05, f"{label}: {text!r} not found in src/lm05.md"
    print(f"CHECK {label} (LM5): '{text}' ok")
    N_CHECKS += 1


def load_anchors() -> dict[str, str]:
    md = ANCHORS_MD.read_text(encoding="utf-8")
    sec = md.split("\n## LM15", 1)[1].split("\n## ", 1)[0]
    out: dict[str, str] = {}
    for line in sec.splitlines():
        if line.startswith("| A15-"):
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
            out[cells[0]] = cells[3].replace("\\|", "|")
    return out


ANCH = load_anchors()


def anchor(aid: str, got: str) -> None:
    """Compare with plans/vol-3-anchors.md: the script's value must appear in the anchor's value column."""
    ok = got in ANCH[aid]
    print(f"ANCHOR {aid}: {got} {'ok' if ok else 'DIFFERS: ' + ANCH[aid]}")
    if not ok:
        ANCHOR_DIFFS.append(f"{aid}: script {got}; anchor {ANCH[aid]}")


def sig3(v: float) -> str:
    """Three significant figures, trailing zeros kept (79.0, 5.00); whole numbers from 100 up; a\\times10^{-b} below 0.001."""
    if v >= 100:
        return f"{v:.0f}"
    if v >= 1e-3:
        return f"{v:#.3g}".rstrip(".")
    m, e = f"{v:.1e}".split("e")
    return f"{m}\\times10^{{{int(e)}}}"


def days_fmt(v: float) -> str:
    """Expected months as X3 prints them: one decimal from 10 up, three significant figures to 0.001, two below."""
    if v >= 10:
        return f"{v:.1f}"
    return sig3(v)


def plain(s: str) -> str:
    """LaTeX scientific form to Python's: 8.1\\times10^{-5} -> 8.1e-05."""
    m = re.fullmatch(r"([\d.]+)\\times10\^\{(-?\d+)\}", s)
    return f"{m.group(1)}e{int(m.group(2)):+03d}" if m else s


# ====================================================================== data
df = pl.read_parquet(TR23).sort("date")
dates_c = [d.isoformat() for d in df["date"].to_list()]
closes: Vec = np.asarray(df["tr"].to_numpy(), dtype=np.float64)
assert df["R"].null_count() == 1 and df["R"][0] is None
R: Vec = np.asarray(df["R"].to_numpy()[1:], dtype=np.float64)
dates = dates_c[1:]
T = len(R)
assert np.abs(R - (closes[1:] / closes[:-1] - 1)).max() < 1e-15
days = (date.fromisoformat(dates_c[-1]) - date.fromisoformat(dates_c[0])).days
years = days / 365.25
A = T / years
assert (T, dates[0], dates[-1], dates_c[0]) == (5849, "2003-01-03", "2026-10-08", "2003-01-02")
chk("T", T, ",", "5,849")
has("first return", "3 January 2003")
has("last return", "8 October 2026")
chk("years", years, ".4f", "23.7645")
chk("A", A, ".2f", "246.12")
has("span of the closes", "The closes, 2 January 2003 – 8 October 2026, span 23.7645 years")
anchor("A15-03", f"{T} returns {dates[0]} .. {dates[-1]}")
anchor("A15-04", f"{days} calendar days; {years:.6f} years; A = {A:.6f}")

levels = [Fraction(repr(float(v))) for v in closes]           # the two-decimal closes, exactly
assert all((100 * lv).denominator == 1 for lv in levels)
RX = [levels[i] / levels[i - 1] - 1 for i in range(1, len(levels))]


def le(x: float, sample: Vec | None = None) -> int:
    """Days with R <= -x (x > 0), with the guard."""
    xs = R if sample is None else sample
    return int((xs <= -x + EPS).sum())


def ge(x: float) -> int:
    return int((R >= x - EPS).sum())


for k in range(1, 11):
    xk = Fraction(k, 100)
    assert le(float(xk)) == sum(1 for v in RX if v <= -xk), k
    assert ge(float(xk)) == sum(1 for v in RX if v >= xk), k
assert sum(1 for v in RX if v == 0) == 0
big = np.abs(R) >= 0.03 - EPS
assert int(big.sum()) == sum(1 for v in RX if abs(v) >= Fraction(3, 100))
print("guarded counts at 1% .. 10% and |R| >= 3% equal the Fraction recounts")

Rbar, s = float(R.mean()), float(R.std())
r: Vec = np.log1p(R)
rbar, s_r = float(r.mean()), float(r.std())
exk = float(stats.kurtosis(R))
assert abs(exk - (((R - Rbar) ** 4).mean() / s**4 - 3)) < 1e-12
skw = float(stats.skew(R))
anchor("A15-09", f"{100 * Rbar:.8f}%")
anchor("A15-10", f"{100 * s:.8f}%")
chk("mean, %", 100 * Rbar, ".4f", "0.0625")
chk("s, %, four decimals", 100 * s, ".4f", "1.2084")
chk("s, %, five decimals (exhibit notes)", 100 * s, ".5f", "1.20836")
chk("excess kurtosis (LM14's)", exk, ".2f", "5.27")
chk("skewness (LM14's)", skw, ".2f", "-0.34")
anchor("A15-49", f"{exk:.6f}")
anchor("A15-02", f"{skw:.6f}")
loc_n, sc_n = (float(v) for v in stats.norm.fit(R))
assert abs(loc_n - Rbar) < 1e-15 and abs(sc_n - s) < 1e-15                 # norm.fit returns Rbar and s, divisor T
anchor("A15-54", f"norm.fit - (Rbar, s): {loc_n - Rbar:.3e}, {sc_n - s:.3e}")
srt = np.sort(R)
order = np.argsort(R, kind="stable")


def emp(u: str, xs: Vec | None = None) -> tuple[int, float]:
    """LM14's empirical quantile: the order statistic R_(ceil(uT)), equal to NumPy's inverted_cdf."""
    v = np.sort(R if xs is None else xs)
    j = math.ceil(Fraction(u) * len(v))
    assert float(np.quantile(v, float(u), method="inverted_cdf")) == float(v[j - 1])
    return j, float(v[j - 1])


# ====================================================================== fits used throughout
nu_m, loc_m, sc_m = (float(v) for v in stats.t.fit(R))


def nll(p: Vec) -> float:
    return float(-stats.t.logpdf(R, p[0], p[1], math.exp(p[2])).sum()) if p[0] > 0.5 else 1e18


for start in ((3.0, Rbar, math.log(0.6 * s)), (5.0, 0.0, math.log(s)), (2.2, 0.001, math.log(0.007)),
              (10.0, Rbar, math.log(0.8 * s))):
    res = optimize.minimize(nll, np.array(start), method="Nelder-Mead",
                            options={"xatol": 1e-10, "fatol": 1e-10, "maxiter": 20000, "maxfev": 40000})
    assert abs(res.x[0] - nu_m) < 1e-3 and res.fun >= nll(np.array([nu_m, loc_m, math.log(sc_m)])) - 1e-3, start
print(f"t.fit: nu {nu_m:.6f}, loc {loc_m:.6%}, scale {sc_m:.6%}; four Nelder-Mead starts agree")
anchor("A15-13", f"nu {nu_m:.6f}; loc {100 * loc_m:.6f}%; scale {100 * sc_m:.6f}%")
chk("ML nu", nu_m, ".3f", "3.065")
chk("ML location, %", 100 * loc_m, ".4f", "0.0997")
chk("ML scale, %", 100 * sc_m, ".4f", "0.7761")
nu_k = 4 + 6 / exk
sc_k = s * math.sqrt((nu_k - 2) / nu_k)
chk("kurtosis-fit nu (exhibit notes)", nu_k, ".3f", "5.139")
chk("kurtosis-fit nu", nu_k, ".2f", "5.14")


def e_norm(x: float) -> float:            # expected days with R <= x under the fitted normal
    return T * float(stats.norm.cdf((x - Rbar) / s))


def e_ml(x: float) -> float:
    return T * float(stats.t.cdf(x, nu_m, loc_m, sc_m))


def e_k(x: float) -> float:
    return T * float(stats.t.cdf((x - Rbar) / sc_k, nu_k))


def e_norm_p(x: float) -> float:          # from the printed 0.0625% and 1.20836% (exhibit notes)
    return 5849 * float(stats.norm.cdf((100 * x - 0.0625) / 1.20836))


def e_ml_p(x: float) -> float:            # from the printed 3.065, 0.0997%, 0.7761%
    return 5849 * float(stats.t.cdf((100 * x - 0.0997) / 0.7761, 3.065))


def e_k_p(x: float) -> float:             # from the printed 5.139, 0.0625%, 1.20836%
    return 5849 * float(stats.t.cdf((100 * x - 0.0625) / (1.20836 * math.sqrt(3.139 / 5.139)), 5.139))


# ====================================================================== Introduction and the case
lm05_has("0050's normal days at -5%", "0.058")
lm05_has("0050's actual days at -5%", "The data contain **nine**")
has("LM5's verdict", "The model expected 0.058 days at or below −5% in twelve years, and 9 occurred")
c5 = le(0.05)
chk("TAIEX days at -5%", c5, "d", "15")
chk("case: normal at -5% from the printed 0.0625%, 1.2084%", 5849 * float(stats.norm.cdf((-5 - 0.0625) / 1.2084)),
    ".2f", "0.08")
chk("X1 normal at -5% (from the printed 1.20836%)", e_norm_p(-0.05), ".3g", "0.0817")
chk("X1 normal at -5%", e_norm(-0.05), ".3g", "0.0817")
assert format(5849 * float(stats.norm.cdf((-5 - 0.0625) / 1.2084)), ".3g") == "0.0818"   # why the notes print 1.20836%
chk("ML days at -5%", e_ml(-0.05), ".1f", "19.6")
chk("ML days at -5% from the printed parameters", e_ml_p(-0.05), ".1f", "19.6")
chk("ML days at -5% with nu = 3.07", 5849 * float(stats.t.cdf((-5 - 0.0997) / 0.7761, 3.07)), ".1f", "19.5")
anchor("A15-11", f"{e_norm(-0.05):.6f}")
anchor("A15-14", f"{e_ml(-0.05):.6f}")
chk("X1 normal at -2%", e_norm(-0.02), ".0f", "257")
chk("X1 ML at -2%", e_ml(-0.02), ".0f", "210")
chk("X1 TAIEX at -2%", le(0.02), "d", "252")

months = sorted({d[:7] for d in dates})
mon_idx = np.array([months.index(d[:7]) for d in dates])
cnt_m: Vec = np.bincount(mon_idx, weights=big.astype(float), minlength=len(months))
sess_m: Vec = np.bincount(mon_idx, minlength=len(months)).astype(float)
lam = float(cnt_m.mean())
var_m = float(cnt_m.var())
assert (len(months), months[0], months[-1], int(sess_m[0]), int(sess_m[-1])) == (286, "2003-01", "2026-10", 18, 6)
chk("months", len(months), "d", "286")
has("January 2003 sessions", "January 2003 (18 sessions)")
has("October 2026 sessions", "October 2026 (6 sessions)")
chk("large-move days", int(big.sum()), "d", "175")
has("lambda hat", r"\hat\lambda=175/286")
chk("lambda hat", lam, ".3f", "0.612")
chk("monthly variance", var_m, ".3f", "1.846")
chk("variance / mean", var_m / lam, ".2f", "3.02")
chk("variance / mean from the printed 1.846, 0.612", 1.846 / 0.612, ".2f", "3.02")
anchor("A15-15", f"{lam:.8f}")
anchor("A15-16", f"{var_m:.8f}")
anchor("A15-17", f"{var_m / lam:.6f}")
eight = [m for m, c in zip(months, cnt_m, strict=True) if c == 8]
assert eight == ["2008-09", "2008-10", "2020-03"] and int(cnt_m.max()) == 8
has("months with eight", "Three months had eight: September and October 2008, and March 2020")
chk("December 2008's count", int(cnt_m[months.index("2008-12")]), "d", "6", in_md=False)
has("December 2008 had six", "December 2008 had six")
five_up = int((cnt_m >= 5).sum())
chk("months with five or more", five_up, "d", "9")
chk("Poisson months with five or more", len(months) * float(stats.poisson.sf(4, lam)), ".3f", "0.123")
chk("Poisson five or more from the printed 0.612", 286 * float(stats.poisson.sf(4, 0.612)), ".3f", "0.123")

# ====================================================================== Section 2: binomial
up = (R > 0).astype(float)
chk("first block's up days", int(up[:20].sum()), "d", "12", in_md=False)
assert dates[19] == "2003-02-07"
has("first block", "TR23's first 20 returns, 3 January to 7 February 2003, contain 12 up days")
NB = T // 20
blocks = up[: NB * 20].reshape(NB, 20).sum(axis=1)
p_hat = float(up[: NB * 20].mean())
assert (NB, T - NB * 20, dates[NB * 20], dates[NB * 20 - 1]) == (292, 9, "2026-09-24", "2026-09-23")
chk("blocks", NB, "d", "292")
chk("returns in blocks", NB * 20, ",", "5,840")
has("excluded", "the last 9 returns, 24 September – 8 October 2026, are excluded")
has("X2 sample", "3 January 2003 – 23 September 2026")
chk("up days in blocks", int(up[: NB * 20].sum()), ",", "3,200")
chk("p hat", p_hat, ".3f", "0.548")
anchor("A15-22", f"{p_hat:.8f}")
chk("E1 mean from the printed 0.548", 20 * 0.548, ".2f", "10.96")
chk("E1 variance from the printed 0.548", 20 * 0.548 * 0.452, ".2f", "4.95")
chk("E1 variance from the unrounded p", 20 * p_hat * (1 - p_hat), ".2f", "4.95")
chk("E1 standard deviation from the printed 0.548", math.sqrt(20 * 0.548 * 0.452), ".2f", "2.23")
assert abs(12 - 20 * 0.548) < math.sqrt(20 * 0.548 * 0.452)                  # the first block lies within one sd
has("first block within one sd", "The first block's 12 up days lie within one standard deviation, 2.23, of the mean 10.96")
chk("blocks' mean", float(blocks.mean()), ".2f", "10.96")
chk("blocks' variance (divisor 292)", float(blocks.var()), ".2f", "4.72")
anchor("A15-31", f"mean {blocks.mean():.6f}; variance {blocks.var():.6f}")
t5, t16 = float(stats.binom.cdf(5, 20, 0.548)), float(stats.binom.sf(15, 20, 0.548))
chk("Pr(X <= 5)", t5, ".3g", "0.00677")
chk("Pr(X >= 16)", t16, ".4g", "0.01807")
chk("blocks with <= 5 from the printed 0.00677", 292 * 0.00677, ".2f", "1.98")
chk("blocks with <= 5", NB * t5, ".2f", "1.98")
chk("blocks with >= 16 from the printed 0.01807", 292 * 0.01807, ".2f", "5.28")
chk("blocks with >= 16", NB * t16, ".2f", "5.28")
assert (int((blocks <= 5).sum()), int((blocks >= 16).sum())) == (2, 3)
has("observed tails", "against 2 observed")
has("observed tails 16", "or 5.28 blocks, against 3")
outside = NB * (float(stats.binom.cdf(3, 20, p_hat)) + float(stats.binom.sf(17, 20, p_hat)))
chk("binomial outside 4..17", outside, ".2f", "0.34")
assert int(blocks.min()) >= 4 and int(blocks.max()) <= 17
anchor("A15-37", f"outside 4..17: {outside:.4f}")
down = R < 0
pc = float((down[:-1] & down[1:]).sum() / down[:-1].sum())
pd_ = float(down[1:].mean())
chk("Pr(down | down)", pc, ".4f", "0.4639")
chk("Pr(down), day pairs", pd_, ".4f", "0.4521")
chk("day pairs", T - 1, ",", "5,848")
assert format(float(down.mean()), ".4f") == "0.4520"      # over all 5,849 days: the text quotes the pairs' 0.4521
rho_p = (0.4639 - 0.4521) / (1 - 0.4521)
chk("rho1 from the printed frequencies", rho_p, ".4f", "0.0215")
assert abs(0.4521 * (0.4639 - 0.4521) / (0.4521 * (1 - 0.4521)) - rho_p) < 1e-15      # cov / var, as the text says
assert abs((0.4521 * 0.4639 - 0.4521**2) - 0.4521 * (0.4639 - 0.4521)) < 1e-15       # E[X1 X2] - E[X1] E[X2]
chk("rho1 from the unrounded frequencies", (pc - pd_) / (1 - pd_), ".4f", "0.0214")
rho_direct = float(np.corrcoef(down[:-1].astype(float), down[1:].astype(float))[0, 1])
assert format(rho_direct, ".4f") == "0.0214", rho_direct                             # the lag-1 correlation itself
has("rho1 text", "(0.0214 from the unrounded frequencies)")
has("covariance defined", r"Their covariance $\E[X_1X_2]-\E[X_1]\E[X_2]$ ([[LM16]]) is $0.4521\times(0.4639-0.4521)$")
has("both days 0.4521", "indicate falls on adjacent days, both taken at frequency 0.4521 (the first day's is 0.4519)")
chk("Pr(down) on the first day of the pairs", float(down[:-1].mean()), ".4f", "0.4519")    # 2,643 / 5,848, LM13's 0.4519
assert int(down[:-1].sum()) == 2643
chk("block variance with rho1, from printed inputs", 20 * 0.548 * 0.452 * (1 + 2 * (19 / 20) * 0.0215), ".2f", "5.16")
chk("block variance with rho1, unrounded", 20 * p_hat * (1 - p_hat) * (1 + 2 * (19 / 20) * (pc - pd_) / (1 - pd_)),
    ".2f", "5.16")
anchor("A15-30", f"{rho_p:.6f}")
assert 20 / 4 == 5 and abs(20 * 0.548 * 0.452 - 5) < 0.05
has("KC n/4", "Its maximum is $n/4=5$")

# ====================================================================== Section 3: Poisson
p3 = float(big.mean())
chk("p of a large move", p3, ".5f", "0.02992")
chk("p from 175/5,849", 175 / 5849, ".5f", "0.02992")
chk("E2 lambda = 20 x 0.02992", 20 * 0.02992, ".4f", "0.5984")
bin_pmf = [float(stats.binom.pmf(j, 20, 0.02992)) for j in range(3)]
poi_pmf = [float(stats.poisson.pmf(j, 0.5984)) for j in range(3)]
for j, (b, pp_, pb, ppo) in enumerate(zip(bin_pmf, poi_pmf, ("0.5447", "0.3360", "0.09845"),
                                          ("0.5497", "0.3289", "0.09842"), strict=True)):
    chk(f"E2 binomial j={j}", b, ".4f" if j < 2 else ".5f", pb)
    chk(f"E2 Poisson j={j}", pp_, ".4f" if j < 2 else ".5f", ppo)
chk("E2 largest gap", max(abs(b - p) for b, p in zip(bin_pmf, poi_pmf, strict=True)), ".4f", "0.0071")
chk("E2 largest gap from the printed pmfs", 0.3360 - 0.3289, ".4f", "0.0071")
for n_, pr in ((20, "0.53711"), (250, "0.54186"), (10_000, "0.54226")):
    chk(f"(1 - 0.612/n)^n, n = {n_}", (1 - 0.612 / n_) ** n_, ".5f", pr)
chk("e^-0.612", math.exp(-0.612), ".5f", "0.54227")
chk("gap at n = 20 from the printed values", 0.54227 - 0.53711, ".4f", "0.0052")
chk("gap at n = 250 from the printed values", 0.54227 - 0.54186, ".4f", "0.0004")
chk("e^-lambda lambda^2/(2n) at n = 20, printed inputs", 0.54227 * 0.612**2 / 40, ".4f", "0.0051")
chk("e^-lambda lambda^2/(2n) at n = 250, printed inputs", 0.54227 * 0.612**2 / 500, ".4f", "0.0004")
chk("e^-lambda lambda^2/(2n) at n = 20, unrounded", math.exp(-0.612) * 0.612**2 / 40, ".4f", "0.0051")
has("E2 gap text", "is close to $e^{-\\lambda}\\lambda^2/(2n)$ with $\\lambda=0.612$ (0.0051 and 0.0004)")
has("E2 reason", "and the error of the approximation is of order $1/n^2$")
err_n2 = []
for n_ in (20, 250, 10_000):             # gap - e^-lambda lambda^2/(2n) is of order 1/n^2: n^2 times it settles
    g = math.exp(-0.612) - (1 - 0.612 / n_) ** n_
    if n_ < 10_000:
        assert abs(g / (math.exp(-0.612) * 0.612**2 / (2 * n_)) - 1) < 0.02
    err_n2.append(n_**2 * (g - math.exp(-0.612) * 0.612**2 / (2 * n_)))
assert abs(err_n2[1] / err_n2[2] - 1) < 0.05 and abs(err_n2[0] / err_n2[2] - 1) < 0.3, err_n2
has("E2 stem 0.612", "Then take the case's monthly mean, 0.612 ($\\hat\\lambda$ of [[eg:bigmoves]])")
has("E2 n", "for $n=20$, 250 and 10,000")
anchor("A15-57", f"j=0: Bin(20, 0.02992) {bin_pmf[0]:.6f} against Poisson(0.5984) {poi_pmf[0]:.6f}")
anchor("A15-58", f"n=20: {(1 - 0.612 / 20) ** 20:.6f}")
obs_m = [int((cnt_m == j).sum()) for j in range(9)]
exp_m = [len(months) * float(stats.poisson.pmf(j, lam)) for j in range(9)]
assert obs_m == [210, 38, 9, 16, 4, 5, 1, 0, 3]
printed_m = ["155.1", "94.9", "29.0", "5.92", "0.906", "0.111", "0.0113", r"9.9\times10^{-4}", r"7.6\times10^{-5}"]
for j, (v, pm) in enumerate(zip(exp_m, printed_m, strict=True)):
    chk_s(f"X3 expected months j={j}", days_fmt(v), pm)
has("X3 list", r"155.1, 94.9, 29.0, 5.92, 0.906, 0.111, 0.0113, $9.9\times10^{-4}$ and $7.6\times10^{-5}$")
chk("E3 none from the printed 0.612", 286 * math.exp(-0.612), ".1f", "155.1")
chk("E3 one from the printed 0.612", 286 * 0.612 * math.exp(-0.612), ".1f", "94.9")
eight_up = len(months) * float(stats.poisson.sf(7, lam))
chk_s("eight or more", sig3(eight_up), r"8.1\times10^{-5}")
chk_s("eight or more from the printed 0.612", sig3(286 * float(stats.poisson.sf(7, 0.612))), r"8.1\times10^{-5}")
has("E3 observed", "and 210 had none. One large move: 94.9 expected, 38 observed. Five or more: 0.123 against 9. "
    r"Eight or more: $8.1\times10^{-5}$ against 3")
nbar, nvar = float(sess_m.mean()), float(sess_m.var())
assert (int(sess_m.min()), int(sess_m.max())) == (6, 24)
has("sessions a month", "6 to 24 sessions")
chk("unequal months' variance", nbar * p3 * (1 - p3) + p3**2 * nvar, ".2f", "0.60")
pre_m = np.array([m < LIMIT_CHANGE[:7] for m in months])
rr = [float(cnt_m[k].var() / cnt_m[k].mean()) for k in (pre_m, ~pre_m)]
assert (int(pre_m.sum()), int((~pre_m).sum())) == (149, 137)
chk("ratio before June 2015", rr[0], ".2f", "2.95")
chk("ratio from June 2015", rr[1], ".2f", "3.01")
has("X9 months", "January 2003 – May 2015 (149) and June 2015 – October 2026 (137)")
anchor("A15-48", f"{rr[0]:.6f} / {rr[1]:.6f}")
anchor("A15-32", f"five or more {len(months) * float(stats.poisson.sf(4, lam)):.6f}")
chk("P2 Pr(X=0), three significant figures", math.exp(-0.612), ".3g", "0.542")
chk("P2 Pr(X>=5)", float(stats.poisson.sf(4, 0.612)), ".3g", "0.000431")
chk("P2 months from the printed 0.000431", 286 * 0.000431, ".3f", "0.123")
has("P2 counts", r"$286e^{-0.612}=155.1$ and $286\times0.000431=0.123$ months")
chk("P3 inverted ratio", 0.612 / 1.846, ".2f", "0.33")
has("P3 B", "**B.** 1.00")

# ====================================================================== Section 4: normal quantiles
for u, pr in (("0.95", "1.6449"), ("0.975", "1.9600"), ("0.99", "2.3263"), ("0.999", "3.0902")):
    chk(f"Phi^-1({u})", float(stats.norm.ppf(float(u))), ".4f", pr)
lm04 = (ROOT / "src" / "lm04.md").read_text(encoding="utf-8")
assert "1.96 is the value a standard normal variable exceeds with probability 2.5%" in lm04
has("LM4's 1.96", "[[LM4]] used 1.96")
normq = {}
for u, ph, pr in (("0.05", 1.6449, "-1.925"), ("0.025", 1.9600, "-2.306"), ("0.01", 2.3263, "-2.749"),
                  ("0.001", 3.0902, "-3.672")):
    normq[u] = 0.0625 - 1.2084 * ph
    chk(f"normal {u} quantile from the printed inputs", normq[u], ".3f", pr)
    chk(f"normal {u} quantile, unrounded", 100 * (Rbar + s * float(stats.norm.ppf(float(u)))), ".3f", pr)
chk("normal 99% quantile from the printed inputs", 0.0625 + 1.2084 * 2.3263, ".3f", "2.874")
has("P5 99%", "+2.874%")
empq = {}
for u, rank, pr in (("0.05", 293, "-1.862"), ("0.025", 147, "-2.648"), ("0.01", 59, "-3.567"), ("0.001", 6, "-6.313"),
                    ("0.99", 5791, "3.125")):
    j, v = emp(u)
    assert j == rank, (u, j)
    empq[u] = v
    chk(f"TAIEX {u} quantile (rank {rank})", 100 * v, ".3f", pr)
    chk(f"rank of the {u} quantile", rank, ",", f"{rank:,}", in_md=rank != 5791)
has("rank 5,791", r"R_{(5,791)}=+3.125\%")
assert dates[int(order[5])] == "2018-10-11"
has("rank 6's date", "sixth-worst day, 11 October 2018")
chk("1% gap from the printed quantiles", -2.749 - -3.567, ".2f", "0.82")
chk("0.1% gap from the printed quantiles", -3.672 - -6.313, ".2f", "2.64")
chk("99% gap from the printed quantiles", 3.125 - 2.874, ".2f", "0.25")
anchor("A15-50", f"0.01: #59 {100 * empq['0.01']:.4f}%")
anchor("A15-51", f"0.01: {100 * (Rbar + s * float(stats.norm.ppf(0.01))):.4f}%")
pp = (np.arange(1, T + 1) - 0.5) / T
qq: Vec = np.asarray(stats.norm.ppf(pp), dtype=np.float64)
zs = (srt - Rbar) / s
keep = [0]                               # X4's thinning, as data/lm15_charts.py draws it
for j in range(1, T):
    if j in (58, T - 1) or qq[j] - qq[keep[-1]] >= 0.05 or zs[j] - zs[keep[-1]] >= 0.2:
        keep.append(j)
chk("QQ points plotted", len(keep), "d", "130")
assert 58 in keep and keep[-1] == T - 1
has("QQ thinning rule", "each rank at least 0.05 right of the last plotted point or 0.2 above it")
for lab, (a, b), (pa, pb) in (("worst", (qq[0], zs[0]), ("-3.758", "-8.079")), ("best", (qq[-1], zs[-1]), ("3.758", "7.604")),
                              ("rank 59", (qq[58], zs[58]), ("-2.326", "-3.004"))):
    chk(f"QQ {lab} x", a, ".3f", pa)
    chk(f"QQ {lab} y", b, ".3f", pb)
assert dates[int(order[0])] == "2025-04-07" and dates[int(order[-1])] == "2025-04-10"
chk("QQ worst y from the printed min and s", (-9.6997 - 0.0625) / 1.2084, ".3f", "-8.079")
chk("QQ best y from the printed max and s", (9.2512 - 0.0625) / 1.2084, ".3f", "7.604")
e_min = integrate.quad(lambda z: z * T * float(stats.norm.pdf(z)) * float(stats.norm.sf(z)) ** (T - 1), -12, 0,
                       points=[-3.7], limit=200)[0]                    # E[min of T standard normals]; mass above 0 is nil
med_min = float(stats.norm.ppf(1 - 0.5 ** (1 / T)))                      # its median
print(f"lowest of {T} normal draws: mean {e_min:.4f}, median {med_min:.4f}, plotting position {qq[0]:.4f}")
assert (format(e_min, ".3f"), format(med_min, ".3f")) == ("-3.718", "-3.676")
chk("E[min] to one decimal", -e_min, ".1f", "3.7", in_md=False)
chk("median of the min to one decimal", -med_min, ".1f", "3.7", in_md=False)
has("about 3.7", "lies about 3.7 standard deviations below the mean")
chk("QQ worst y to two decimals", -zs[0], ".2f", "8.08")
chk("rank 59 gap from the printed point", -3.004 - -2.326, ".2f", "-0.68", in_md=False)
chk("rank 59 gap from the printed 1% gap", 0.82 / 1.2084, ".2f", "0.68")
anchor("A15-39", f"rank 1 ({qq[0]:.6f}, {zs[0]:.6f})")
phi15 = float(stats.norm.ppf(15 / T))
chk("Phi^-1(15/T)", phi15, ".4f", "-2.7988")
chk("sigma for 15 days from the printed inputs", -5.0625 / -2.7988, ".3f", "1.809")
chk("sigma for 15 days, unrounded", 100 * (-0.05 - Rbar) / phi15, ".3f", "1.809")
chk("days at -2% under sigma = 1.809%", 5849 * float(stats.norm.cdf(-2.0625 / 1.809)), ".0f", "743")
has("KC 4 inputs", r"(-5.0625\%)/\sigma")
anchor("A15-23", f"sigma {100 * (-0.05 - Rbar) / phi15:.6f}%")

# ====================================================================== Section 5: lognormal
last: dict[int, float] = {}
for d, c in zip(dates_c, closes, strict=True):
    last[int(d[:4])] = float(c)
yrs = list(range(2003, 2026))
G = np.array([last[y] / (float(closes[0]) if y == 2003 else last[y - 1]) for y in yrs])
muX, sX = float(np.log(G).mean()), float(np.log(G).std())
chk("calendar years", len(yrs), "d", "23")
chk("mu_X", muX, ".5f", "0.11646")
chk("sigma_X", sX, ".5f", "0.22207")
anchor("A15-40", f"mu_X {muX:.8f}; sigma_X {sX:.8f}")
chk("arithmetic mean return, %", 100 * (float(G.mean()) - 1), ".2f", "14.97")
chk("compound rate, %", 100 * (math.exp(muX) - 1), ".2f", "12.35")
chk("median from the printed mu_X", math.exp(0.11646), ".4f", "1.1235")
assert format(math.exp(0.1165), ".4f") != "1.1235"           # five decimals are needed
chk("median, unrounded", math.exp(muX), ".4f", "1.1235")
chk("mean from the printed inputs", math.exp(0.11646 + 0.22207**2 / 2), ".4f", "1.1516")
chk("mean, unrounded", math.exp(muX + sX**2 / 2), ".4f", "1.1516")
chk("mean return, % (from the printed 1.1516)", 100 * (1.1516 - 1), ".2f", "15.16")
chk("sd from the printed inputs", math.sqrt((math.exp(0.22207**2) - 1) * math.exp(2 * 0.11646 + 0.22207**2)), ".4f",
    "0.2589")
chk("sd, unrounded", math.sqrt((math.exp(sX**2) - 1) * math.exp(2 * muX + sX**2)), ".4f", "0.2589")
chk("z of a losing year", -0.11646 / 0.22207, ".4f", "-0.5244")
ploss = float(stats.norm.cdf(-0.11646 / 0.22207))
chk("Pr(G < 1), %", 100 * ploss, ".1f", "30.0")
chk("Pr(G < 1), unrounded, %", 100 * float(stats.norm.cdf(-muX / sX)), ".1f", "30.0")
chk("expected losing years", 23 * ploss, ".2f", "6.90")
losing = [y for y, g in zip(yrs, G, strict=True) if g < 1]
assert losing == [2008, 2011, 2015, 2018, 2022]
has("losing years", "5 observed (2008, 2011, 2015, 2018 and 2022)")
chk("P6 A: 5/23, %", 100 * 5 / 23, ".1f", "21.7")
chk("P6 C: Pr(G > 1), %", 100 * (1 - ploss), ".1f", "70.0")
chk("5% quantile from the printed inputs", math.exp(0.11646 - 1.6449 * 0.22207), ".4f", "0.7797")
chk("95% quantile from the printed inputs", math.exp(0.11646 + 1.6449 * 0.22207), ".4f", "1.6189")
chk("5% quantile, unrounded", math.exp(muX + sX * float(stats.norm.ppf(0.05))), ".4f", "0.7797")
chk("95% quantile, unrounded", math.exp(muX + sX * float(stats.norm.ppf(0.95))), ".4f", "1.6189")
lgn = stats.lognorm(s=0.22207, scale=math.exp(0.11646))
for v, pr in ((float(lgn.median()), "1.1235"), (float(lgn.mean()), "1.1516"), (float(lgn.std()), "0.2589"),
              (float(lgn.ppf(0.05)), "0.7797"), (float(lgn.ppf(0.95)), "1.6189")):
    chk("SciPy lognorm (P7)", v, ".4f", pr)
outside_y = [(y, g) for y, g in zip(yrs, G, strict=True) if g < 0.7797 or g > 1.6189]
assert [y for y, _ in outside_y] == [2008, 2009]
chk("2008's factor", G[5], ".4f", "0.5693")
chk("2009's factor", G[6], ".4f", "1.8334")
chk("expected outside 5%-95%", 0.1 * 23, ".1f", "2.3")
gs = np.sort(G)
assert yrs[int(np.argsort(G)[11])] == 2013
chk("empirical median", gs[11], ".4f", "1.1514")
has("empirical median year", "1.1514 (2013)")
anchor("A15-41", f"median {math.exp(muX):.6f}")
anchor("A15-43", f"{gs[11]:.6f} (2013)")
# LM17's iid daily model, on the window of the 23 calendar years
m1 = round(A)
win = np.array([d <= "2025-12-31" for d in dates])
r_w: Vec = r[win]
assert abs(float(r_w.sum()) - float(np.log(G).sum())) < 1e-12
assert dates[int(np.flatnonzero(win)[-1])] == "2025-12-31"
chk("m = round(A)", m1, "d", "246")
chk("log returns in the window", len(r_w), ",", "5,664")
has("window", "5,664 log returns from 3 January 2003 to 31 December 2025")
mu_w, sd_w = m1 * float(r_w.mean()), float(r_w.std()) * math.sqrt(m1)
chk("LM17 model mean", mu_w, ".4f", "0.1163")
chk("LM17 model sd", sd_w, ".4f", "0.1856")
chk("LM17 model Pr(losing year), %", 100 * float(stats.norm.cdf(-mu_w / sd_w)), ".1f", "26.5")
chk("LM17 model from the printed 0.1163, 0.1856, %", 100 * float(stats.norm.cdf(-0.1163 / 0.1856)), ".1f", "26.5")
# VX2: 26.5% is (17.6)'s normal approximation of that model (LM17 prints 26.54% by (17.6)), and the text says so
has("E6 normal approximation", "By [[LM17]]'s normal approximation, a losing year then has probability 26.5%.")
has("overview about 26.5%", "a model of independent days gives about 26.5%")
has("zh normal approximation", "以常態逼近（normal approximation）計算，虧損年機率降為約 26.5%")
anchor("A15-64", f"Pr(loss year) = Phi(-mean/sd) = {float(stats.norm.cdf(-mu_w / sd_w)):.6f}")
chk("rbar, %", 100 * rbar, ".5f", "0.05517")
chk("s_r, %", 100 * s_r, ".4f", "1.2107")
chk("lognormal days at -5% from the printed inputs",
    5849 * float(stats.norm.cdf((math.log(0.95) - 0.0005517) / 0.012107)), ".4f", "0.0541")
chk("lognormal days at -5%", T * float(stats.norm.cdf((math.log(0.95) - rbar) / s_r)), ".4f", "0.0541")
anchor("A15-34", f"{T * float(stats.norm.cdf((math.log(0.95) - rbar) / s_r)):.6f}")
chk("normal on G: mean", float(G.mean()), ".4f", "1.1497")
chk("normal on G: sd (divisor 23)", float(G.std()), ".4f", "0.2370")
chk_s("normal on G: Pr(G < 0)", sig3(float(stats.norm.cdf(-1.1497 / 0.2370))), r"6.1\times10^{-7}")
anchor("A15-25", f"{float(stats.norm.cdf(-G.mean() / G.std())):.4e}")

# ====================================================================== Section 6: gamma function and Student-t
for v, pr in ((special.gamma(0.5), "1.772454"), (special.gamma(1.5), "0.886227"), (special.gamma(2.5), "1.329340")):
    chk("Gamma", float(v), ".6f", pr)
assert abs(special.gamma(0.5) - math.sqrt(math.pi)) < 1e-15 and special.gamma(2.0) == 1.0
assert (special.gamma(3.0), special.gamma(4.0)) == (2.0, 6.0)
has("Gamma(2..4)", r"$\Gamma(2)=1$, $\Gamma(3)=2$, $\Gamma(4)=6$")


def c_nu(nu: float) -> float:
    """The constant of (15.9)."""
    return math.exp(float(special.gammaln((nu + 1) / 2) - special.gammaln(nu / 2))) / math.sqrt(nu * math.pi)


chk("constant at nu = 3", c_nu(3), ".4f", "0.3676")
chk("2/(pi sqrt 3)", 2 / (math.pi * math.sqrt(3)), ".4f", "0.3676")
assert abs(c_nu(3) - 2 / (math.pi * math.sqrt(3))) < 1e-15
for y_ in (0.0, 0.7, 2.5):                                # 2/(pi sqrt3) (1 + y^2/3)^-2 = 6 sqrt3 / (pi (3 + y^2)^2)
    assert abs(2 / (math.pi * math.sqrt(3)) * (1 + y_**2 / 3) ** -2 - 6 * math.sqrt(3) / (math.pi * (3 + y_**2) ** 2)) < 1e-15
chk("constant at nu = 1", c_nu(1), ".4f", "0.3183")
chk("constant at nu = 30", c_nu(30), ".4f", "0.3956")
chk("constant at nu = 1,000", c_nu(1000), ".4f", "0.3988")
chk("1/sqrt(2 pi)", 1 / math.sqrt(2 * math.pi), ".4f", "0.3989")
assert abs(c_nu(4) - 3 / 8) < 1e-15 and abs(special.gamma(2.5) / (math.sqrt(4 * math.pi) * special.gamma(2)) - 3 / 8) < 1e-15
has("P8 constant", r"=3/8")
for v in (nu_m, nu_k, 3.0, 5.0, 3.065, 5.139):           # (15.9) integrates to 1
    area = integrate.quad(lambda y, v=v: c_nu(v) * (1 + y * y / v) ** (-(v + 1) / 2), -np.inf, np.inf)[0]
    assert abs(area - 1) < 1e-8, (v, area)
for v in (5.0, 6.0, 7.5):                                # (15.10) against quad, and the Deep Dive's E[Y^4]
    e2 = integrate.quad(lambda y, v=v: y**2 * float(stats.t.pdf(y, v)), -np.inf, np.inf)[0]
    e4 = integrate.quad(lambda y, v=v: y**4 * float(stats.t.pdf(y, v)), -np.inf, np.inf, limit=200)[0]
    assert abs(e2 - v / (v - 2)) < 1e-7 and abs(e4 - 3 * v**2 / ((v - 2) * (v - 4))) < 1e-4 * e4, (v, e2, e4)
    assert abs(e4 / e2**2 - (3 + 6 / (v - 4))) < 1e-4
assert float(stats.t(5).stats(moments="k")) == 6.0 and float(stats.t(6).stats(moments="k")) == 3.0
assert (5 / 3, 3 + 6 / 1, 6 / 4, 3 + 6 / 2) == (5 / 3, 9, 1.5, 6)
lm05_has("t_5's kurtosis 9", "finite (9)")
has("P8 values", "$t_5$ has variance $5/3$ and kurtosis 9, and $t_6$ has variance $3/2$ and kurtosis 6")
has("KC 8", "SciPy prints 6 for the kurtosis of $t_5$")
for v in (2.5, 7.0):                                     # (15.11): mean mu and standard deviation sigma
    sc_ = 0.02 * math.sqrt((v - 2) / v)
    assert abs(float(stats.t(v, loc=0.001, scale=sc_).std()) - 0.02) < 1e-14
    assert abs(float(stats.t(v, scale=2.0).var()) - 4 * v / (v - 2)) < 1e-12        # SciPy: scale^2 df/(df-2)
chk("kurtosis-fit nu from the printed 5.27", 4 + 6 / 5.27, ".2f", "5.14")
chk("kurtosis-fit scale from the printed inputs, %", 1.2084 * math.sqrt(3.14 / 5.14), ".3f", "0.944")
chk("kurtosis-fit scale, unrounded, %", 100 * sc_k, ".3f", "0.944")
chk("P9 A: 6/5.27", 6 / 5.27, ".2f", "1.14")
chk("P9 B: 4 + 6/(5.27 - 3)", 4 + 6 / (5.27 - 3), ".2f", "6.64")
anchor("A15-26", f"nu {nu_k:.6f}; scale {100 * sc_k:.6f}%")
sd_m = sc_m * math.sqrt(nu_m / (nu_m - 2))
chk("ML sigma from the printed inputs, %", 0.7761 * math.sqrt(3.065 / 1.065), ".3f", "1.317")
chk("ML sigma, unrounded, %", 100 * sd_m, ".3f", "1.317")
chk("ML sigma / s - 1, %", 100 * (sd_m / s - 1), ".0f", "9", in_md=False)
chk("ML sigma / s - 1 from the printed values, %", 100 * (1.317 / 1.2084 - 1), ".0f", "9", in_md=False)
has("9% above s", "9% above $s$")
anchor("A15-55", f"{100 * sd_m:.6f}%")
med_j = (T + 1) // 2
chk("sample median, %", 100 * float(srt[med_j - 1]), ".4f", "0.0879")
LM14 = (ROOT / "src" / "lm14.md").read_text(encoding="utf-8")
assert "the median is the 2,925th return, 0.0879%" in LM14.replace("{,}", ",")       # LM14 owns the median
assert "The data have 175 such days" in LM14                                     # and states the 175 days first
has("LM14's median cited", "[[LM14]]'s sample median, 0.0879%")
has("LM14's 175 days cited", "among 5,849 ([[LM14]]); set $p$ to the frequency $175/5,849=0.02992$ a session")
chk("kurtosis fit at -5%", e_k(-0.05), ".3g", "8.17")
chk("KC 6: kurtosis at nu = 5.139 from the printed nu", 3 + 6 / 1.139, ".2f", "8.27")
LV = [k / 100 for k in range(2, 11)]
z_pr = ["-1.707", "-2.534", "-3.362", "-4.190", "-5.017", "-5.845", "-6.672", "-7.500", "-8.327"]
n_pr = ["257", "32.9", "2.26", "0.0817", "0.00153", r"1.5\times10^{-5}", r"7.4\times10^{-8}", r"1.9\times10^{-10}",
        r"2.4\times10^{-13}"]
k_pr = ["232", "64.3", "21.2", "8.17", "3.59", "1.75", "0.926", "0.524", "0.313"]
m_pr = ["210", "79.0", "36.6", "19.6", "11.6", "7.41", "5.00", "3.52", "2.57"]
a_pr = ["252", "108", "44", "15", "6", "2", "2", "1", "0"]
for x, zp, np_, kp, mp, ap in zip(LV, z_pr, n_pr, k_pr, m_pr, a_pr, strict=True):
    chk(f"X6 z at -{x:.0%}", (-x - Rbar) / s, ".3f", zp)
    chk(f"X6 z at -{x:.0%} from the printed inputs", (-100 * x - 0.0625) / 1.20836, ".3f", zp)
    for f_, pr, lab in ((e_norm, np_, "normal"), (e_norm_p, np_, "normal, printed inputs"), (e_k, kp, "kurtosis fit"),
                        (e_k_p, kp, "kurtosis fit, printed inputs"), (e_ml, mp, "ML"), (e_ml_p, mp, "ML, printed inputs")):
        chk_s(f"X6 {lab} at -{x:.0%}", sig3(f_(-x)), pr)
    chk(f"X6 TAIEX at -{x:.0%}", le(x), "d", ap)
row = {f"{k}%": f"| {k}% | {zp.replace('-', '−')} | " for k, zp in zip(range(2, 11), z_pr, strict=True)}
for k in range(2, 11):
    has(f"X6 row {k}%", row[f"{k}%"].replace("−", "-"))
anchor("A15-24", ", ".join(str(le(x)) for x in LV))
anchor("A15-27", ", ".join(f"{e_ml(-x):.6g}" for x in LV))
anchor("A15-45", ", ".join(f"{e_k(-x):.6g}" for x in LV))
anchor("A15-35", ", ".join(f"{e_norm(-x):.6g}" for x in LV))
has("X7 range", "from −10.5% to −1.0%")

# ====================================================================== Section 7: tail measures
i7 = dates.index("2025-04-07")
eve, aft = R[:i7], R[: i7 + 1]
assert (len(eve), len(aft), dates[i7 - 1]) == (5478, 5479, "2025-04-02")
chk("returns to 2 April 2025", len(eve), ",", "5,478")
chk("returns to 7 April 2025", len(aft), ",", "5,479")
has("2 April", "returns to 2 April 2025")
k_eve, k_aft = float(stats.kurtosis(eve)), float(stats.kurtosis(aft))
chk("excess kurtosis on the eve", k_eve, ".2f", "4.25")
chk("excess kurtosis after 7 April 2025", k_aft, ".2f", "4.94")
chk("its change", k_aft - k_eve, ".2f", "0.69")
chk("its change from the printed values", 4.94 - 4.25, ".2f", "0.69")
q_eve, q_aft = emp("0.01", eve)[1], emp("0.01", aft)[1]
chk("1% quantile on the eve", 100 * q_eve, ".3f", "-3.538")
chk("1% quantile after", 100 * q_aft, ".3f", "-3.543")
chk("its change from the printed values", 3.543 - 3.538, ".3f", "0.005")
chk("days at -3% on the eve", le(0.03, eve), "d", "96")
chk("days at -3% after", le(0.03, aft), "d", "97")
n56_eve, n56_aft = (le(0.05, eve), le(0.06, eve)), (le(0.05, aft), le(0.06, aft))
assert (n56_eve, n56_aft) == ((12, 4), (13, 5)), (n56_eve, n56_aft)
has("E10 counts at -5% and -6%", "The days at or below −5% and −6% went from 12 and 4 to 13 and 5")
ch_eve, ch_aft = math.log(12 / 4) / math.log(1.2), math.log(13 / 5) / math.log(1.2)
chk("chord -5% to -6% on the eve", ch_eve, ".2f", "6.03")
chk("chord -5% to -6% after", ch_aft, ".2f", "5.24")
chk("its change from the printed values", 6.03 - 5.24, ".2f", "0.79")
assert format(ch_eve - ch_aft, ".2f") == "0.78"        # unrounded 0.785: the text subtracts its printed 6.03 and 5.24
has("E10 chord", "the count by one day and the chord by 0.79, from 6.03 to 5.24")
has("overview chord", "the chord from −5% to −6% rests on a few days and fell from 6.03 to 5.24")
has("E10 stem", "and the chord (15.13) from −5% to −6%, defined below")
chk("without 7 April 2025", float(stats.kurtosis(np.delete(R, i7))), ".2f", "4.71")
dev = R - Rbar
top4 = np.argsort(-np.abs(dev), kind="stable")[:4]
assert [dates[int(i)] for i in top4] == ["2025-04-07", "2025-04-10", "2024-08-05", "2026-07-31"]
has("four largest", "(7 and 10 April 2025, 5 August 2024 and 31 July 2026)")
chk("without the four largest", float(stats.kurtosis(np.delete(R, top4))), ".2f", "3.74")
top10 = np.argsort(-(dev**4), kind="stable")[:10]
chk("top ten, share of the fourth powers, %", 100 * float((dev[top10] ** 4).sum() / (dev**4).sum()), ".1f", "35.0")
chk("top ten, share of the squares, %", 100 * float((dev[top10] ** 2).sum() / (dev**2).sum()), ".1f", "6.7")
for t_ in ("8.12", "7.05", "3.85", "5.84", "7.63", "62.8%", "14.1%"):
    lm05_has(f"LM5's {t_}", t_)
has("LM5's values", "8.12, then 7.05 and 3.85 after the same removals, 5.84 to 7.63 in one day, and shares of 62.8% and 14.1%")
anchor("A15-69", f"excess kurtosis {k_eve:.4f} -> {k_aft:.4f}")
anchor("A15-70", f"{float(stats.kurtosis(np.delete(R, top4))):.4f}")
anchor("A15-71", f"{100 * float((dev[top10] ** 4).sum() / (dev**4).sum()):.4f}%")
pre = np.array([d < LIMIT_CHANGE for d in dates])
x9: dict[str, list[str]] = {}
for name, msk, dlo, dhi in (("full", np.ones(T, dtype=bool), "2003-01-03", "2026-10-08"),
                            ("7%", pre, "2003-01-03", "2015-05-29"), ("10%", ~pre, "2015-06-01", "2026-10-08")):
    x = R[msk]
    idx = np.flatnonzero(msk)
    assert (dates[int(idx[0])], dates[int(idx[-1])]) == (dlo, dhi)
    j1, q1 = emp("0.01", x)
    ek_ = float(stats.kurtosis(x))
    nu_r = float(stats.t.fit(x)[0])
    x9[name] = [f"{len(x):,}", f"{100 * float(x.std()):.3f}", f"{ek_:.2f}", f"{4 + 6 / ek_:.2f}", f"{nu_r:.3f}",
                f"{j1}", f"{100 * q1:.3f}", f"{1000 * le(0.03, x) / len(x):.1f}"]
    for v_, f_ in ((100 * float(x.std()), ".3f"), (ek_, ".2f"), (4 + 6 / ek_, ".2f"), (nu_r, ".3f"), (100 * q1, ".3f"),
                   (1000 * le(0.03, x) / len(x), ".1f")):
        assert not tie(v_, f_), (name, v_, f_)
    print(f"X9 {name}: {x9[name]}")
assert x9["full"] == ["5,849", "1.208", "5.27", "5.14", "3.065", "59", "-3.567", "18.5"]
assert x9["7%"] == ["3,077", "1.257", "3.39", "5.77", "2.990", "31", "-3.621", "23.4"]
assert x9["10%"] == ["2,772", "1.152", "8.07", "4.74", "3.237", "28", "-3.467", "13.0"]
for lab, i in (("Returns $T$", 0), ("$s$ (%)", 1), ("Excess kurtosis", 2), (r"$\nu$ by kurtosis, (15.12)", 3),
               (r"$\nu$ by maximum likelihood", 4), (r"Rank of the 1% quantile, $\lceil0.01T\rceil$", 5),
               ("1% quantile (%)", 6), (r"Days with $R\le-3\%$ per 1,000", 7)):
    has(f"X9 row {lab}", f"| {lab} | " + " | ".join(x9[k][i] for k in ("full", "7%", "10%")) + " |")
has("X9 ratio row", "variance ÷ mean | 3.02 | 2.95 | 3.01 |")
has("X9 dates", "| Dates | 3 Jan 2003 – 8 Oct 2026 | 3 Jan 2003 – 29 May 2015 | 1 Jun 2015 – 8 Oct 2026 |")
has("P11 figures", "$T=3,077$, $s=1.257\\%$, excess kurtosis 3.39, $\\nu=2.990$, 1% quantile −3.621%".replace("\\%", "%"))
has("P11 figures after", "$T=2,772$, $s=1.152\\%$, excess kurtosis 8.07, $\\nu=3.237$, 1% quantile −3.467%".replace("\\%", "%"))
anchor("A15-07", "full: T 5849 (2003-01-03 .. 2026-10-08), s 1.2084%")
cnt = {k: le(k / 100) for k in range(2, 7)}


def chord(n1: float, n2: float, x1: float, x2: float) -> float:
    return math.log(n1 / n2) / math.log(x2 / x1)


adj = [chord(cnt[k], cnt[k + 1], k, k + 1) for k in range(2, 6)]
for v, pr in zip(adj, ("2.09", "3.12", "4.82", "5.03"), strict=True):
    chk("adjacent chord", v, ".2f", pr)
assert all(a < b for a, b in itertools.pairwise(adj))
allc = [chord(cnt[i], cnt[j], i, j) for i in range(2, 7) for j in range(i + 1, 7)]
assert len(allc) == 10 and min(allc) == adj[0] and max(allc) == adj[-1]
assert sum(2 <= v <= 5 for v in allc) >= 6                               # "mostly inside LM5's 2 to 5"
has("chord range", "between 2.09 and 5.03")
chk("chord 3% to 6%", chord(108, 6, 3, 6), ".2f", "4.17")
chk("normal chord 3% to 6%", chord(e_norm(-0.03), e_norm(-0.06), 3, 6), ".1f", "14.4")
chk("ML chord 3% to 6%", chord(e_ml(-0.03), e_ml(-0.06), 3, 6), ".2f", "2.77")
chk("kurtosis-fit chord 3% to 6%", chord(e_k(-0.03), e_k(-0.06), 3, 6), ".2f", "4.16")
c24, c46, c26 = chord(252, 44, 2, 4), chord(44, 6, 4, 6), chord(252, 6, 2, 6)
chk("P10 2% to 4%", c24, ".2f", "2.52")
chk("P10 4% to 6%", c46, ".2f", "4.91")
chk("P10 2% to 6%", c26, ".2f", "3.40")
assert abs(c26 - (c24 * math.log(2) + c46 * math.log(1.5)) / math.log(3)) < 1e-12
assert c24 < nu_m < c46
# the maximum-likelihood fit's own chords at the same levels, from X6's printed 210, 36.6 and 11.6 days
chk("P10 ML chord 2% to 4%, printed days", chord(210, 36.6, 2, 4), ".2f", "2.52")
chk("P10 ML chord 4% to 6%, printed days", chord(36.6, 11.6, 4, 6), ".2f", "2.83")
chk("P10 ML chord 2% to 6%, printed days", chord(210, 11.6, 2, 6), ".2f", "2.64")
chk("P10 ML chord 2% to 4%, unrounded", chord(e_ml(-0.02), e_ml(-0.04), 2, 4), ".2f", "2.52")
chk("P10 ML chord 4% to 6%, unrounded", chord(e_ml(-0.04), e_ml(-0.06), 4, 6), ".2f", "2.83")
assert format(chord(e_ml(-0.02), e_ml(-0.06), 2, 6), ".2f") == "2.63"       # the text prints 2.64 from the printed days
assert format(c24, ".2f") == "2.52" and chord(e_ml(-0.04), e_ml(-0.06), 4, 6) < c46 - 2
has("P10 ML chords", "from [[ex:tailtable]]'s 210, 36.6 and 11.6 days, are 2.52, 2.83 and 2.64")
has("P10 comparison", "They equal the data's from −2% to −4% and lie far below them from −4% to −6%")
has("P10 deeper chord", "The deeper chord rests on 6 days and on the price limit ([[ex:loglog]])")
has("P10 stem", "the maximum-likelihood fit's chords at the same levels and its $\\nu=3.065$")
anchor("A15-47", f"2%->3% {adj[0]:.6f}")
anchor("A15-68", f"ML t {chord(e_ml(-0.03), e_ml(-0.06), 3, 6):.6f}")
lm05_has("LM5's tail index 2 to 5", "between 2 and 5")
lm05_has("LM5's alpha about 3", "\\alpha\\approx3")
chk("large falls", le(0.03), "d", "108")
chk("large rises", ge(0.03), "d", "67")
has("108 against 67", "108 against 67")
lim7 = R[pre]
chk("7% regime minimum, %", 100 * float(lim7.min()), ".4f", "-6.6789")
chk("7% regime maximum, %", 100 * float(lim7.max()), ".4f", "6.7420")
chk("7% regime minimum, two decimals", 100 * float(lim7.min()), ".2f", "-6.68")
chk("worst day, %", 100 * float(R.min()), ".4f", "-9.6997")
chk("best day, %", 100 * float(R.max()), ".4f", "9.2512", in_md=False)
assert dates[int(R.argmin())] == "2025-04-07"
has("limit dates", "at 7% until 29 May 2015 and at 10% from 1 June 2015")
anchor("A15-77", f"min {100 * float(lim7.min()):.4f}%")
anchor("A15-08", f"min {100 * float(R.min()):.4f}% (2025-04-07)")
q_ml = float(stats.t.ppf(0.01, nu_m, loc_m, sc_m))
chk("ML 1% quantile, %", 100 * q_ml, ".3f", "-3.365")
chk("ML 1% quantile from the printed parameters, %", 0.0997 + 0.7761 * float(stats.t.ppf(0.01, 3.065)), ".3f", "-3.365")
chk("ML 1% quantile in the code comment", q_ml, ".5f", "-0.03365")
chk("TAIEX 1% quantile in the code comment", empq["0.01"], ".5f", "-0.03567")
anchor("A15-52", f"1%: {100 * q_ml:.4f}%")
tail = R[R <= -0.05 + EPS]
z5 = (-0.05 - Rbar) / s
chk("tail mean at -5%, data, %", 100 * float(tail.mean()), ".2f", "-6.26")
chk("tail mean, normal (5.11), %", 100 * (Rbar - s * float(stats.norm.pdf(z5) / stats.norm.cdf(z5))), ".2f", "-5.26")
zp5 = (-5 - 0.0625) / 1.20836
chk("tail mean, normal, from the printed inputs, %",
    0.0625 - 1.20836 * float(stats.norm.pdf(zp5) / stats.norm.cdf(zp5)), ".2f", "-5.26")
num = integrate.quad(lambda x: x * float(stats.t.pdf(x, nu_m, loc_m, sc_m)), -np.inf, -0.05)[0]
chk("tail mean, ML t, %", 100 * num / float(stats.t.cdf(-0.05, nu_m, loc_m, sc_m)), ".2f", "-7.57")
anchor("A15-74", f"data {100 * float(tail.mean()):.4f}%")
has("X10 counts", "2, 2, 1 days at −7%, −8%, −9%; the kurtosis fit's 1.75, 0.926, 0.524 come close")
has("X10 ML", "79.0, 36.6, 19.6 days against 108, 44, 15; −3.365% against −3.567%")
has("X10 lognormal", "losing years 6.90 expected against 5; beyond the 5% and 95% quantiles 2.3 against 2; "
    "mean +15.16% against 14.97%")
has("KC 7", "expects 2.57 days at or below −10%, and TAIEX has none")
chk("upper tail +3%", ge(0.03), "d", "67")
chk("upper tail +5%", ge(0.05), "d", "13")
chk("normal at +3% from the printed inputs", 5849 * float(stats.norm.sf((3 - 0.0625) / 1.2084)), ".1f", "44.0")
chk("normal at +5% from the printed inputs", 5849 * float(stats.norm.sf((5 - 0.0625) / 1.2084)), ".3f", "0.128")
chk("ML at +3%", T * float(stats.t.sf(0.03, nu_m, loc_m, sc_m)), ".1f", "94.2")
chk("ML at +5%", T * float(stats.t.sf(0.05, nu_m, loc_m, sc_m)), ".1f", "22.0")
chk("ML at +3% from the printed parameters", 5849 * float(stats.t.sf((3 - 0.0997) / 0.7761, 3.065)), ".1f", "94.2")
chk("ML at +5% from the printed parameters", 5849 * float(stats.t.sf((5 - 0.0997) / 0.7761, 3.065)), ".1f", "22.0")
anchor("A15-76", f"+3%: {ge(0.03)}, normal {T * float(stats.norm.sf((0.03 - Rbar) / s)):.4f}")
# Solution 12: the fit overstates the upper tail at both levels, and, centred above 0, expects more rises than falls
assert T * stats.t.sf(0.03, nu_m, loc_m, sc_m) > ge(0.03) and T * stats.t.sf(0.05, nu_m, loc_m, sc_m) > ge(0.05)
assert e_ml(-0.03) < le(0.03) and e_ml(-0.05) > le(0.05) and loc_m > 0
assert T * stats.t.sf(0.03, nu_m, loc_m, sc_m) > e_ml(-0.03) and T * stats.t.sf(0.05, nu_m, loc_m, sc_m) > e_ml(-0.05)
has("P12 lower tail", "In the lower tail it understates at −3% (79.0 against 108) and overstates at −5% (19.6 against 15)")
has("P12 centre", "Centred at +0.0997%, the Student-t even expects more large rises than large falls")
has("P12 stem", "Why can no symmetric model centred near the median fit both tails?")
# X11, V2: SciPy's method of moments matches the first k raw moments, k the number of free parameters (rv_continuous.fit;
# three for t: df, loc, scale), and it fails on TR23
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    try:
        stats.t.fit(R, method="MM")
        mm_fails = False
    except ValueError:
        mm_fails = True
assert mm_fails, "stats.t.fit(R, method='MM') no longer raises on TR23: revise the trap in the scipy exhibit"
print("CHECK stats.t.fit(R, method='MM') raises ValueError on TR23 ok")
has("MM trap", "matches the first three raw moments of `t`, one per free parameter, not (15.12)'s kurtosis; fails on TR23")
assert stats.t.shapes == "df" and stats.t.numargs + 2 == 3     # df plus loc and scale: three free parameters
has("choice: the years", "The lognormal row uses the calendar years 2003–2025, 2003 from its first close.")
has("E10 lead-in", "TR23 shows both points, but a deep chord rests on a few days and moves too.")
has("zh chord caveat", "門檻越深越陡，但深處的弦只靠少數幾天，同樣不穩")
# VX8: each TR23 data exhibit after the case names its source as the case's
assert TEXT.count("Source: as [[ex:case]].") == 8
# VX5, VX4, VX6: the boxes name the index, and gloss these terms at first use
assert "台股" not in TEXT and TEXT.count("加權股價報酬指數") == 6
for term in ("樣本峰態（sample kurtosis）", "年度對數報酬（log return）", "的密度（density）"):
    has(f"zh gloss {term}", term)

# ====================================================================== Section 8 and the problems
has("code: guard", "down5 = int((R <= -0.05 + 1e-12).sum())        # 15 days: the guard")
chk("code: binomial blocks", 292 * float(stats.binom.cdf(5, 20, 0.548)), ".2f", "1.98")
chk("code: Poisson months", 286 * float(stats.poisson.pmf(0, 175 / 286)), ".1f", "155.1")
chk("P1 C: standard deviation", math.sqrt(20 * 0.548 * 0.452), ".2f", "2.23")
has("P5 inputs", r"$\Phi^{-1}(0.99)=2.3263$")
has("P7 call", "stats.lognorm(s=0.22207, scale=np.exp(0.11646))")
code = re.findall(r"```python\n(.*?)```", TEXT, re.DOTALL)
assert code and all(len(line) <= 80 for block in code for line in block.splitlines()), "a code line exceeds 80 characters"

# ====================================================================== labels, exhibits, characters
labels: dict[str, str] = {}
for kind, lab in re.findall(r"(?m)^(?:>\s?)+\[!(exhibit|example)\][+-]?\s.*\{#([\w-]+)\}\s*$", TEXT):
    assert lab not in labels, lab
    labels[lab] = kind
refs = re.findall(r"\[\[(ex|eg):([\w-]+)\]\]", TEXT)
for kind, lab in refs:
    assert lab in labels and labels[lab] == ("exhibit" if kind == "ex" else "example"), (kind, lab)
cited = {lab for kind, lab in refs if kind == "ex"}
uncited = [lab for lab, kind in labels.items() if kind == "exhibit" and lab not in cited]
assert not uncited, f"exhibits never cited: {uncited}"
assert sum(k == "exhibit" for k in labels.values()) == 11 and sum(k == "example" for k in labels.values()) == 10
for f in (MD, ROOT / "src" / "lm15.js", Path(__file__)):
    raw = f.read_text(encoding="utf-8")
    assert not re.search(r"[\t\b\f]", raw), f"{f.name} holds a tab, backspace or form feed"
assert "分配" not in TEXT, "use 分布, never 分配"
print(f"labels: {len(labels)} resolve; every exhibit is cited; no tab, backspace or form feed")

print(f"\nanchor differences ({len(ANCHOR_DIFFS)}):")
for a_ in ANCHOR_DIFFS:
    print("   ", a_)
print(f"\nall {N_CHECKS} checks passed")
