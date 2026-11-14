"""Every number that LM33 (The Statistics of the Sharpe Ratio) prints, computed and checked against src/lm33.md.

Run:  uv run python data/lm33_numbers.py
      (after data/vol5_series.py, data/vol5_rules.py and data/vol3_series.py; and after data/lm33_charts.py, whose
      chart and widget data this script checks)

Inputs and conventions: data/lm33_common.py, which keeps the code of data/vol6_anchors_lm33.py (the Stage 1 anchor
script): E5 through vol5_series.frames("E5"), the eight rules through vol5_rules (no rule is re-implemented here), TR23
through data/processed/vol3_taiex.parquet. The module text is src/lm33.md; plans/vol-6-anchors.md, "LM33", holds the
Stage 1 anchors A33-01 .. A33-67.

Part 1 compares each anchor line, as data/lm33_common.py recomputes it, with the anchor table's Value column: a
difference is reported, never forced.

Part 2 checks the text (each check stops the script on a failure):
  chk(label, value, fmt, printed)  format(value, fmt) equals the printed string, the value is not a rounding tie of
                                   that format, and the printed string is in the module as a whole number. Results the
                                   module computes beside their inputs are redone from the printed, rounded inputs
                                   (PITFALLS section 7, "from printed").
  has(label, text)                 a literal string (a date, a phrase, a table row built from the values) is in the
                                   module.
Numbers quoted from published modules are checked against those modules' lines. At the end the script lists the
numbers of the module that no check covered and prints "all N checks passed".
"""
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arch
import lm33_common as K
import numpy as np
import scipy
from scipy import stats

ROOT = HERE.parent
MD = ROOT / "src" / "lm33.md"
ANCHORS = ROOT / "plans" / "vol-6-anchors.md"
RAW = MD.read_text(encoding="utf-8")
Z95, Z975 = float(stats.norm.ppf(0.95)), 1.959964


# ====================================================================== text helpers
def norm_text(s: str) -> str:
    """The module text with TeX thousands separators, escaped percent signs, \\text{} and minus signs made plain."""
    s = s.replace("{,}", ",").replace("\\%", "%").replace("\u2212", "-").replace("\\,", "")
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
    assert not in_md or in_text(printed), f"{label}: {printed!r} not found in src/lm33.md"
    COVERED.add(printed.lstrip("+-"))
    N_CHECKS += 1


def pct(label: str, frac: float, d: int, printed: str, in_md: bool = True) -> None:
    chk(label, 100 * frac, f".{d}f", printed, in_md)


def has(label: str, text: str) -> None:
    global N_CHECKS
    assert text in TEXT or text in RAW, f"{label}: {text!r} not found in src/lm33.md"
    print(f"CHECK {label}: '{text[:90]}' in text")
    for num in re.findall(r"\d[\d,]*\.?\d*", text):
        COVERED.add(num.rstrip(".,"))
    N_CHECKS += 1


def published(label: str, module: str, text: str) -> None:
    """A number quoted from a published module: the quoted text is on that module's page."""
    global N_CHECKS
    src = (ROOT / "src" / module).read_text(encoding="utf-8")
    assert text in src, f"{label}: {text!r} not in src/{module}"
    print(f"CHECK {label}: '{text[:60]}' in src/{module}")
    N_CHECKS += 1


# ====================================================================== part 1: the anchors
def _anchor_values() -> dict[str, str]:
    rows: dict[str, str] = {}
    sec = ANCHORS.read_text(encoding="utf-8").split("\n## LM33", 1)[1].split("\n## ", 1)[0]
    for line in sec.splitlines():
        if line.startswith("| A33-"):
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
            rows[cells[0]] = cells[3].strip("`").replace("\\|", "|")
    return rows


ANCHOR_ROWS = _anchor_values()
assert len(ANCHOR_ROWS) == 67, len(ANCHOR_ROWS)
for line in K.OUT:
    aid, got = line.split(" ", 1)
    ok = got == ANCHOR_ROWS[aid]
    print(f"ANCHOR {aid}: {'ok' if ok else 'DIFFERS'}")
    if not ok:
        ANCHOR_DIFFS.append(f"{aid}:\n      script {got}\n      anchor {ANCHOR_ROWS[aid]}")
assert "A33-" not in RAW, "anchor IDs stay out of the module text"

# ====================================================================== part 2: the text
RULES, T, Aw, sqA, tau = K.RULES, K.T, K.Aw, K.sqA, K.tau
SR, mom, SE9, SEH, SEN = K.SR, K.mom, K.SE9, K.SEH, K.SEN
SRy = {k: SR[k] * sqA for k in RULES}

# ---------------------------------------------------------------- data role (case, notation, hygiene, X1 note)
chk("T", T, ",d", "1,851")
assert (K.dates[0], K.dates[1], K.dates[-1]) == ("2019-03-04", "2019-03-05", "2026-10-08")
has("first trade's close", "from the close of 4 March 2019 to 8 October 2026")
has("first return", "5 March 2019 to 8 October 2026")
chk("calendar years", K.cal_years, ".2f", "7.60")
chk("calendar years, 4 dp", K.cal_years, ".4f", "7.5975")
chk("years of sessions", tau, ".2f", "7.60")
chk("years of sessions, 4 dp", tau, ".4f", "7.5995")
has("calendar years in the case", "7.60 calendar years")
has("years of sessions in the notation note", "is the record in years of sessions")
chk("wealth frame sessions", len(K.fr.wealth_dates), ",d", "2,368")
chk("A_w", Aw, ".2f", "243.57")
chk("TR23 T", K.Tt, ",d", "5,849")
chk("TR23 A", K.At, ".2f", "246.12")
has("fixed in advance", "fixed on 24 October 2026, before any result was computed")
has("r_f", "$r_f=1.5\\%$")
assert K.RF == 0.015
has("four families", "Four families of tests run on these returns: eight one-sided tests against zero, the seven pairs "
    "against R1 by two methods, and the eight two-sided tests behind the haircuts.")
assert K.L == 7 and K.Lt == 9 and K.lag_rule(K.TM) == 3 and K.TM == 90
has("lag rule values", "7 for 1,851 returns, 9 for TR23's 5,849 and 3 for 90 months")

# ---------------------------------------------------------------- the case box and the overview
best, worst = K.best, K.worst
assert (best, worst) == ("R2", "R4")
chk("case: R2 a year", SRy["R2"], ".2f", "1.14")
chk("case: R1 a year", SRy["R1"], ".2f", "0.98")
chk("case: R4 a year", SRy["R4"], ".2f", "0.63")
chk("case: R2's SE (20.9)", SE9["R2"] * sqA, ".3f", "0.367")
chk("case: R2's interval lo", K.CI9["R2"][0], ".2f", "0.42")
chk("case: R2's interval hi", K.CI9["R2"][1], ".2f", "1.86")
inside = sum(1 for k in RULES if k != "R2" and abs(SR[k] - SR["R2"]) < Z975 * SE9["R2"])
assert inside == 7
has("case: all seven inside", "holds all seven other estimates")
chk("case: R2 - R1", SRy["R2"] - SRy["R1"], ".2f", "0.16")
chk("case: correlation R2-R1", K.r21, ".2f", "0.70")
chk("case: LW p-value (HAC)", K.PAIR["R2"]["p_hac"], ".2f", "0.52")
chk("case: LW p-value (bootstrap)", K.PAIR["R2"]["p_boot"], ".2f", "0.52")
chk("case: best of eight under the null", K.SR0_8 * sqA, ".2f", "0.52")
has("case: best of eight", "the best of their estimates would still average 0.52 a year over 1,851 daily returns")
kmin = min(mom[k][3] for k in RULES)
kmax = max(mom[k][3] for k in RULES)
chk("overview: raw kurtosis low", kmin, ".0f", "10")
chk("overview: raw kurtosis high", kmax, ".0f", "23")
has("overview: kurtosis", "Negative skewness and raw kurtosis of 10 to 23 lift (20.9)'s standard error only from 0.363 to "
    "at most 0.371, if the data have the fourth moment it needs.")
assert all(f"{SEN[k] * sqA:.3f}" == "0.363" for k in RULES)
chk("max SE (20.9)", max(SE9.values()) * sqA, ".3f", "0.371")
chk("min SE (20.9)", min(SE9.values()) * sqA, ".3f", "0.367")
ratio_h = {k: SEH[k] / SE9[k] for k in RULES}
chk("overview: HAC move low (%)", 100 * (min(ratio_h.values()) - 1), "+.0f", "-8")
chk("overview: HAC move high (%)", 100 * (max(ratio_h.values()) - 1), "+.0f", "+4")
has("overview: HAC moves", "moves it by −8% to +4%")
has("overview: months", "lowers R1's annual ratio from 1.06 to 0.92")
has("overview: correction's noise", "0.38 on a ratio of 1.31")
has("overview: PSR", "0.999 for R2. Against zero R2 needs 523 sessions, 2.15 years of sessions")
has("overview: LW", "R2's lead of 0.16 over R1 within noise: a p-value of 0.52")
has("overview: DSR", "R2's benchmark is 0.52 a year and its DSR 0.955")
has("overview: correlation", "The rules correlate 0.82 on average, and their effective number of trials is 2.07.")
has("overview: haircut", "cuts R2's ratio by 21%, to 0.90")

# ---------------------------------------------------------------- Exhibit 1 (case): the two tables
for k in RULES:
    loh, hih = K.CIH[k]
    row = (f"| {k} | {SRy[k]:.3f} | {SE9[k] * sqA:.3f} | {SEH[k] * sqA:.3f} | {loh:.2f} to {hih:.2f} | "
           f"{K.PSR0[k]:.3f} |")
    has(f"X1 (a) {k}", row)
    for v, fm in ((SRy[k], ".3f"), (SE9[k] * sqA, ".3f"), (SEH[k] * sqA, ".3f"), (loh, ".2f"), (hih, ".2f"),
                  (K.PSR0[k], ".3f")):
        assert not tie(v, fm), (k, v, fm)
    # each interval follows from the printed ratio and SE
    sr_p, se_p = float(f"{SRy[k]:.3f}"), float(f"{SEH[k] * sqA:.3f}")
    assert f"{sr_p - Z975 * se_p:.2f} to {sr_p + Z975 * se_p:.2f}" == f"{loh:.2f} to {hih:.2f}", (k, "from printed")
for k in RULES[1:]:
    p = K.PAIR[k]
    row = (f"| {k} - R1 | {p['d']:+.3f} | {p['se']:.3f} | {p['p_hac']:.2f} | {p['p_boot']:.2f} | "
           f"{min(p['holm_hac'], p['holm_boot']):.2f} |")
    has(f"X1 (b) {k}", row)
    assert p["holm_hac"] == 1.0 and p["holm_boot"] == 1.0
    for v, fm in ((p["d"], ".3f"), (p["se"], ".3f"), (p["p_hac"], ".2f"), (p["p_boot"], ".2f")):
        assert not tie(v, fm), (k, v, fm)
    d_p, se_p = float(f"{p['d']:.3f}"), float(f"{p['se']:.3f}")
    assert f"{2 * stats.norm.sf(abs(d_p / se_p)):.2f}" == f"{p['p_hac']:.2f}", (k, "HAC p from printed")
chk("X1 note: DSR at n = 8", K.dsr_at(8), ".3f", "0.955")
assert K.b_rule == 22 and K.B == 9999
has("X1 note: bootstrap", "circular blocks of $b=22$ with $B=9{,}999$ resamples, seed `[1, 20261011]`, Monte Carlo SE "
    "at most 0.005")
assert max(p["p_se"] for p in K.PAIR.values()) <= 0.005

# ---------------------------------------------------------------- Section 2: E1, E2, R4, r_f
m2, s2, sk2, ku2 = mom["R2"]
pct("E1 mean", m2, 4, "0.0564")
pct("E1 s", s2, 3, "0.774")
chk("E1 skewness", sk2, ".3f", "-0.112")
chk("E1 raw kurtosis", ku2, ".2f", "13.58")
chk("E1 ratio from printed", 0.0564 / 0.774, ".4f", "0.0729")
chk("E1 ratio", SR["R2"], ".4f", "0.0729")
chk("E1 skew term from printed", 0.0729 * 0.112, ".4f", "0.0082")
chk("E1 kurtosis term from printed", 12.58 / 4 * 0.0729**2, ".4f", "0.0167")
chk("E1 skew term", -SR["R2"] * sk2, ".4f", "0.0082")
chk("E1 kurtosis term", (ku2 - 1) / 4 * SR["R2"] ** 2, ".4f", "0.0167")
chk("E1 V from printed", 1 + 0.0082 + 0.0167, ".4f", "1.0249")
chk("E1 V", K.v209(SR["R2"], sk2, ku2), ".4f", "1.0249")
chk("E1 12.58", ku2 - 1, ".2f", "12.58")
chk("E1 SE daily from printed", math.sqrt(1.0249 / 1851), ".4f", "0.0235")
chk("E1 SE a year from printed", 0.0235 * math.sqrt(243.57), ".3f", "0.367")
chk("E1 t-stat from printed", 0.0729 * math.sqrt(1851), ".2f", "3.14")
chk("E1 t-stat", SR["R2"] * math.sqrt(T), ".2f", "3.14")
assert 1.8 < ((ku2 - 1) / 4 * SR["R2"] ** 2) / (-SR["R2"] * sk2) < 2.2
has("E1 twice", "The kurtosis term is about twice the skewness term.")
for k in RULES:
    m, s, sk, ku = mom[k]
    se_m = s / math.sqrt(T) * Aw
    se_v = s * math.sqrt((ku - 1) / (4 * T)) * sqA
    row = (f"| {k} | {100 * m * Aw:.2f} ({100 * se_m:.2f}) | {100 * s * sqA:.2f} ({100 * se_v:.2f}) | {sk:.2f} | "
           f"{ku:.1f} |")
    has(f"E2 row {k}", row)
    for v, fm in ((100 * m * Aw, ".2f"), (100 * se_m, ".2f"), (100 * s * sqA, ".2f"), (100 * se_v, ".2f"),
                  (sk, ".2f"), (ku, ".1f")):
        assert not tie(v, fm), (k, v, fm)
assert all(mom[k][2] < 0 and mom[k][3] > 10 for k in RULES)
has("E2: negative skewness, kurtosis above 10", "since every skewness is negative and every raw kurtosis exceeds 10")
has("E2: unrounded", "[[ex:case]] (a) gives each Sharpe ratio, the mean over the volatility from unrounded values, "
    "with its (20.9) standard error.")
has("E2: SE range", "(20.9) raises it to between 0.367 and 0.371")
chk("R4 interval lo", K.CI9["R4"][0], ".2f", "-0.09")
chk("R4 interval hi", K.CI9["R4"][1], ".2f", "1.35")
chk("R4 one-sided p", 1 - K.PSR0["R4"], ".3f", "0.044")
chk("R4 PSR(0)", K.PSR0["R4"], ".3f", "0.956")
assert min(K.PSR0.values()) > 0.95 and min(K.PSR0, key=lambda k: K.PSR0[k]) == "R4"
assert max(K.PSR0, key=lambda k: K.PSR0[k]) == "R2"
chk("R2 PSR(0)", K.PSR0["R2"], ".3f", "0.999")
chk("Holm largest adjusted", max(K.HOLM_PSR.values()), ".3f", "0.044")
assert sum(1 for a in K.HOLM_PSR.values() if a <= 0.05 + 1e-12) == 8
has("Holm on eight", "Holm (21.7) on the eight one-sided p-values rejects all eight at 5%, with a largest adjusted "
    "p-value of 0.044")
z90 = float(stats.norm.ppf(0.95))
chk("KC 2: 90% lo", (SR["R4"] - z90 * SE9["R4"]) * sqA, ".2f", "0.02")
chk("KC 2: 90% hi", (SR["R4"] + z90 * SE9["R4"]) * sqA, ".2f", "1.23")
for rate, lo_, hi_ in ((0.0, "0.09", "0.15"), (0.02, "0.03", "0.05")):
    chg = [abs(K.rf_sr[rate][k] - SR[k]) * sqA for k in RULES]
    chk(f"r_f {rate}: smallest change", min(chg), ".2f", lo_)
    chk(f"r_f {rate}: largest change", max(chg), ".2f", hi_)
    assert max(RULES, key=lambda k: K.rf_sr[rate][k]) == "R2" and min(RULES, key=lambda k: K.rf_sr[rate][k]) == "R4"
    for k in RULES:     # the change is the change in rate over the rule's volatility
        assert abs(abs(K.rf_sr[rate][k] - SR[k]) * sqA - abs(K.RF - rate) / (mom[k][1] * sqA)) < 1e-12
chk("r_f 2%: R4's PSR(0)", K.rf_psr[0.02]["R4"], ".3f", "0.948")
assert sum(1 for a in K.rf_holm[0.02] if a <= 0.05 + 1e-12) == 7
assert sum(1 for a in K.rf_holm[0.0] if a <= 0.05 + 1e-12) == 8
has("r_f paragraph", "At 0% every Sharpe ratio rises by 0.09 to 0.15, the change in rate over the rule's volatility, "
    "and at 2% each falls by 0.03 to 0.05.")
has("r_f: Holm at 2%", "but at 2% R4's PSR(0) is 0.948 and Holm rejects seven of the eight")
has("r_f: borrowing", "R8's borrowing at 3.5% keep their rates")
has("hygiene date", "The rules and their settings were fixed on 24 October 2026, before any result was computed")
has("moment flag start", "The data may lack (20.9)'s fourth moment.")
has("r_f: illustrative, as LM27", "The rate $r_f=1.5\\%$ is illustrative, as in [[LM27]].")
published("LM27's illustrative rate", "lm27.md", "Cash earns an illustrative $r_f=1.5\\%$ a year")
# the moment (20.9) needs, and what large T means here (PITFALLS section 7, decision XB7; shared decision "Rigor")
has("large T", "it holds for large $T$, here 1,851 daily returns or TR23's 5,849")
published("LM20's t fit of TR23", "lm20.md", "| Student-t, TR23 | 5,849 | 3.065 (0.144) |")
published("LM20's pitfall", "lm20.md", "$\\nu=3.065<4$ and $\\E R^4=\\infty$")
has("moment flag", "[[LM20]]'s Student-t fit to TR23 has 3.065 degrees of freedom, below 4, so its fourth moment is "
    "infinite. The rules' raw kurtosis of 10 to 23 has no standard error.")
has("moment flag for (33.1)", "which TR23 may lack (Section 2)")
published("TR23 raw kurtosis 8.27", "lm20.md", "skewness −0.34 and kurtosis 8.27")
published("TR23 excess kurtosis 5.27", "lm19.md", "excess kurtosis from 5.27")
published("0050 excess kurtosis 8.12", "lm04.md", "excess kurtosis** of 8.12")
chk("KC 9: scipy default kurtosis", float(stats.kurtosis(K.X["R2"])), ".2f", "10.58")
chk("KC 9: raw kurtosis", float(stats.kurtosis(K.X["R2"], fisher=False)), ".2f", "13.58")

# ---------------------------------------------------------------- Section 3: HAC
rho1 = {k: K.rho1(K.X[k]) for k in RULES}
chk("rho_1 R1", rho1["R1"], ".3f", "-0.054")
chk("rho_1 R4", rho1["R4"], ".3f", "0.002")
assert min(rho1, key=lambda k: rho1[k]) == "R1" and max(rho1, key=lambda k: rho1[k]) == "R4"
chk("rho_1 of R1's squares", K.rho1((K.X["R1"] - K.X["R1"].mean()) ** 2), ".3f", "0.246")
lc = K.LAGCURVE
for k, lg, p_ in (("R2", 0, "0.367"), ("R2", 7, "0.382"), ("R2", 20, "0.393"), ("R4", 7, "0.340"),
                  ("R2", 60, "0.389")):
    chk(f"E3 {k} at lag {lg}", lc[k][lg], ".3f", p_)
assert [f"{lc['R1'][lg]:.3f}" for lg in (0, 7, 20, 60)] == ["0.370", "0.363", "0.359", "0.367"]
assert [f"{lc['R4'][lg]:.3f}" for lg in (0, 7, 20, 60)] == ["0.368", "0.340", "0.316", "0.300"]
chk("E3 HAC/iid low", min(ratio_h.values()), ".2f", "0.92")
chk("E3 HAC/iid high", max(ratio_h.values()), ".2f", "1.04")
assert min(ratio_h, key=lambda k: ratio_h[k]) == "R4" and max(ratio_h, key=lambda k: ratio_h[k]) == "R2"
chk("E3 vol HAC/iid low", min(K.vr.values()), ".2f", "1.51")
chk("E3 vol HAC/iid high", max(K.vr.values()), ".2f", "1.60")
se_v1 = mom["R1"][1] * math.sqrt((mom["R1"][3] - 1) / (4 * T)) * sqA
pct("E3 R1 vol SE iid", se_v1, 3, "0.576")
pct("E3 R1 vol SE lag 7", K.se_vol_hac(K.X["R1"], 7) * sqA, 3, "0.872")
pct("E3 R1 vol SE lag 20", K.se_vol_hac(K.X["R1"], 20) * sqA, 3, "1.026")
pct("E3 R1 vol SE lag 60", K.se_vol_hac(K.X["R1"], 60) * sqA, 3, "1.156")
chk("KC 3: R1 vol ratio from printed", 0.872 / 0.576, ".2f", "1.51")
mean_ratio = K.se_mean_hac(K.X["R1"], 7) / (mom["R1"][1] / math.sqrt(T))
chk("KC 3: R1 mean ratio", mean_ratio, ".2f", "0.94")
pct("KC 3: R1 mean SE HAC", K.se_mean_hac(K.X["R1"], 7) * Aw, 2, "4.25")
pct("KC 3: R1 mean SE iid", mom["R1"][1] / math.sqrt(T) * Aw, 2, "4.53")
chk("KC 3: mean ratio from printed", 4.25 / 4.53, ".2f", "0.94")
chk("E4 TR23 daily", K.srt, ".4f", "0.0517")
chk("E4 TR23 a year", K.srt * math.sqrt(K.At), ".2f", "0.81")
chk("E4 TR23 skewness", K.skt, ".2f", "-0.34")
chk("E4 TR23 raw kurtosis", K.kut, ".2f", "8.27")
chk("E4 (20.9)", math.sqrt(K.v209(K.srt, K.skt, K.kut) / K.Tt) * math.sqrt(K.At), ".3f", "0.207")
chk("E4 HAC lag 9", K.se_sr_hac(K.Rt, 9) * math.sqrt(K.At), ".3f", "0.213")
chk("E4 HAC lag 145", K.se_sr_hac(K.Rt, 145) * math.sqrt(K.At), ".3f", "0.243")
published("LM20's 0.207", "lm20.md", "| Sharpe ratio a year, TR23 | 0.81 | — | 0.205 | 0.207 | 0.40 to 1.22 |")
for scheme, v in (("Moving blocks", "0.247"), ("Circular blocks", "0.244"), ("Stationary bootstrap", "0.233")):
    published(f"LM22's {scheme}", "lm22.md", f"| {scheme} |")
    assert re.search(rf"\| {scheme} \|.*\| {v} \|", (ROOT / "src" / "lm22.md").read_text(encoding="utf-8"))
for row in ("| (20.9), as [[LM20]] printed it | 0.207 |", "| (33.1) at the book's lag, 9 | 0.213 |",
            "| (33.1) at [[LM22]]'s block length, 145 | 0.243 |",
            "| [[LM22]]'s stationary bootstrap, blocks of 145 | 0.233 |", "| [[LM22]]'s circular blocks of 145 | 0.244 |",
            "| [[LM22]]'s moving blocks of 145 | 0.247 |"):
    has("E4 table row", row)
# E3's table: (33.1) a year at lags 0, 7, 20, 60 for R1, R2, R4, and R1's volatility SE in percent
for k in ("R1", "R2", "R4"):
    has(f"E3 table {k}", f"| Sharpe ratio, {k} | " + " | ".join(f"{lc[k][lg]:.3f}" for lg in (0, 7, 20, 60)) + " |")
vol_se = [se_v1] + [K.se_vol_hac(K.X["R1"], lg) * sqA for lg in (7, 20, 60)]
has("E3 table R1 volatility", "| Volatility of R1, % | " + " | ".join(f"{100 * v:.3f}" for v in vol_se) + " |")
for v in [lc[k][lg] for k in ("R1", "R2", "R4") for lg in (0, 7, 20, 60)] + [100 * v for v in vol_se]:
    assert not tie(v, ".3f"), v
assert abs(K.se_vol_hac(K.X["R1"], 0) / (mom["R1"][1] * math.sqrt((mom["R1"][3] - 1) / (4 * T))) - 1) < 1e-12
has("E3 HAC interval of R2", "R2's HAC interval is 0.39 to 1.89")
assert f"{K.CIH['R2'][0]:.2f} to {K.CIH['R2'][1]:.2f}" == "0.39 to 1.89"
# "rises by half": HAC over iid for the volatility's SE, 1.51 to 1.60 at lag 7
assert all(1.45 <= v < 1.65 for v in K.vr.values())
has("by half", "The volatility's error rests on the squares, and it rises by half.")
published("LM19's 0.0517 and 0.81", "lm19.md", "| Sharpe ratio, $r_f=0$ | 0.0517 (0.0456) | $\\times\\sqrt A$ | 0.81 (0.715)")
assert 0.233 <= K.se_sr_hac(K.Rt, 145) * math.sqrt(K.At) <= 0.247

# ---------------------------------------------------------------- Section 4: annualizing
assert int(K.nsess.min()) == 12 and int(K.nsess.max()) == 23 and K.mar19 == 19 and K.oct26 == 6
has("E5 months", "The 90 calendar months run from April 2019 to September 2026, 12 to 23 sessions each. The 19 "
    "returns of March 2019 and the 6 of October 2026 are excluded.")
chk("E5 R1 monthly ratio", K.srm_["R1"], ".3f", "0.305")
chk("E5 R1 sqrt12", K.srm_["R1"] * math.sqrt(12), ".2f", "1.06")
chk("E5 R1 sqrt12 from printed", 0.305 * math.sqrt(12), ".2f", "1.06")
chk("E5 R1 ratio", K.den["R1"], ".3f", "1.309")
chk("E5 R1 ratio, 2 dp", K.den["R1"], ".2f", "1.31")
chk("E5 R1 Lo", K.srm_["R1"] * K.eta["R1"], ".2f", "0.92")
chk("E5 R1 Lo from printed", 0.305 * math.sqrt(12 / 1.309), ".2f", "0.92")
chk("E5 R2 sqrt12", K.srm_["R2"] * math.sqrt(12), ".2f", "1.05")
chk("E5 R2 Lo", K.srm_["R2"] * K.eta["R2"], ".2f", "0.94")
chk("E5 R4 sqrt12", K.srm_["R4"] * math.sqrt(12), ".2f", "0.62")
chk("E5 R4 Lo", K.srm_["R4"] * K.eta["R4"], ".2f", "0.49")
assert sorted(K.eta) == sorted(RULES)              # "over the eight rules"
has("E5 table sqrt12", "| By $\\sqrt{12}$ | " + " | ".join(f"{K.srm_[k] * math.sqrt(12):.2f}" for k in ("R1", "R2", "R4"))
    + " |")
has("E5 table (19.9)", "| By (19.9) | " + " | ".join(f"{K.srm_[k] * K.eta[k]:.2f}" for k in ("R1", "R2", "R4")) + " |")
has("E5 scale over eight", "Over the eight rules the scale factors run from 2.74 to 3.33 against 3.46.")
chk("E5 scale low", min(K.eta.values()), ".2f", "2.74")
chk("E5 scale high", max(K.eta.values()), ".2f", "3.33")
chk("E5 sqrt12", math.sqrt(12), ".2f", "3.46")
chk("E5 robust SE", K.serob["R1"], ".2f", "0.38")
chk("E5 excess over 1", K.den["R1"] - 1, ".3f", "0.309")
chk("E5 iid SE", K.se_iid12, ".3f", "0.395")
chk("E5 iid SEs", (K.den["R1"] - 1) / K.se_iid12, ".2f", "0.78")
chk("E5 iid SEs from printed", 0.309 / 0.395, ".2f", "0.78")
has("E5 eleven", "the corrected ratio carries the noise of 11 autocorrelations")
dlog = {k: K.xd[k].mean() / K.xd[k].std() * sqA for k in RULES}
chk("log ratios low", min(dlog.values()), ".2f", "0.54")
chk("log ratios high", max(dlog.values()), ".2f", "1.08")
assert min(dlog, key=lambda k: dlog[k]) == "R4" and max(dlog, key=lambda k: dlog[k]) == "R2"
has("simple ratios range", "against 0.63 to 1.14")
chk("KC 4: AR(1) scale factor", K.ar, ".3f", "2.879")
chk("KC 4: sqrt12", math.sqrt(12), ".3f", "3.464")
chk("KC 4: factor", math.sqrt(12) / K.ar, ".3f", "1.203")
chk("KC 4: factor from printed", 3.464 / 2.879, ".3f", "1.203")
pct("KC 4: overstatement", math.sqrt(12) / K.ar - 1, 0, "20")
has("KC 4: Lo's Table 2", "Lo's Table 2 (his p. 41) prints 2.88")

# ---------------------------------------------------------------- Section 5: PSR and MinTRL
chk("z with sqrt(T-1)", K.zt, ".3f", "3.097")
chk("z with sqrt(T)", K.zt * math.sqrt(T / (T - 1)), ".3f", "3.098")
pct("sqrt(T/(T-1)) - 1", math.sqrt(T / (T - 1)) - 1, 3, "0.027")
has("T/(T-1)", "$\\sqrt{1{,}851/1{,}850}$")
for a, pm, pp in zip(K.X4_SR, ("10.83", "2.72", "1.21"), ("0.916", "0.997", "1.000"), strict=True):
    chk(f"X4 MinTRL at {a}", K.X4_MIN[a], ".2f", pm)
    chk(f"X4 PSR at 7.60, {a}", K.X4_AT[a], ".3f", pp)
for k, p0, n0, y0, yn in (("R2", "0.999", "523", "2.15", "2.10"), ("R1", "0.996", "720", "2.96", "2.85"),
                          ("R4", "0.956", "1,717", "7.05", "6.85")):
    _, _, sk, ku = mom[k]
    n_ = K.mintrl(SR[k], 0, sk, ku)
    chk(f"E6 {k} PSR(0)", K.PSR0[k], ".3f", p0)
    chk(f"E6 {k} MinTRL sessions", n_, ",.0f", n0)
    chk(f"E6 {k} MinTRL years", n_ / Aw, ".2f", y0)
    chk(f"E6 {k} normal MinTRL years", K.mintrl(SR[k], 0, 0, 3) / Aw, ".2f", yn)
    assert f"{float(n0.replace(',', '')) / 243.57:.2f}" == y0     # also from the printed count
    assert n_ < T
chk("E6 R2 MinTRL from printed", 1 + 1.0249 * (Z95 / 0.0729) ** 2, ".0f", "523")
chk("E6 R2 years from printed", 523 / 243.57, ".2f", "2.15")
chk("E6 TR23 daily", K.srt, ".5f", "0.05173")
chk("E6 TR23 PSR(0)", K.psr(K.srt, 0, K.Tt, K.skt, K.kut), ".5f", "0.99995")
chk("E6 TR23 MinTRL", K.n_tr, ",.0f", "1,035")
chk("E6 TR23 years", K.n_tr / K.At, ".2f", "4.20")
n_tr_p = 1 + K.v209(0.05173, -0.34, 8.27) * (Z95 / 0.05173) ** 2
chk("E6 TR23 MinTRL from printed", n_tr_p, ",.0f", "1,035")
chk("E6 TR23 years from printed, unrounded count", n_tr_p / 246.12, ".2f", "4.20")
assert f"{1035 / 246.12:.2f}" == "4.21"           # hence "from the unrounded counts" in the text
has("E6 unrounded counts", "Years of sessions divide the unrounded counts by $A_{\\mathrm w}$, or by TR23's $A$.")
chk("E6 TR23 normal MinTRL years", K.mintrl(K.srt, 0, 0, 3) / K.At, ".2f", "4.12")
e6 = ("R2", "R1", "R4")
e6_mt = [K.mintrl(SR[k], 0, mom[k][2], mom[k][3]) for k in e6]
has("E6 table head", "| Record | R2 | R1 | R4 | TR23 |")
has("E6 table PSR", "| PSR(0) | " + " | ".join(f"{K.PSR0[k]:.3f}" for k in e6) + " | 0.99995 |")
has("E6 table sessions", "| MinTRL, sessions | " + " | ".join(f"{n:,.0f}" for n in e6_mt) + " | 1,035 |")
has("E6 table years", "| MinTRL, years of sessions | " + " | ".join(f"{n / Aw:.2f}" for n in e6_mt) + " | 4.20 |")
has("E6 table normal", "| The same, normal moments | "
    + " | ".join(f"{K.mintrl(SR[k], 0, 0, 3) / Aw:.2f}" for k in e6) + " | 4.12 |")
has("E6 TR23 inputs", "TR23 uses the daily ratio 0.05173 and [[eg:tr23]]'s moments.")
chk("E6 TR23 annual", K.srt * math.sqrt(K.At), ".4f", "0.8115")
chk("E6 (21.4) one-sided", (Z95 / (K.srt * math.sqrt(K.At))) ** 2, ".2f", "4.11")
chk("E6 (21.4) from printed", (1.645 / 0.8115) ** 2, ".2f", "4.11")
published("LM21's 11.9 and 0.8115", "lm21.md", "TR23's ratio, 0.8115 to four decimals, needs 11.9 years")
chk("E6 BLdP normal months", K.n12n, ".1f", "38.9")
chk("E6 BLdP months", K.n12, ".1f", "59.9")
chk("E6 BLdP normal years", K.n12n / 12, ".2f", "3.24")
chk("E6 BLdP years", K.n12 / 12, ".2f", "4.99")
chk("E6 BLdP years from printed (normal)", 38.9 / 12, ".2f", "3.24")
chk("E6 BLdP years from printed", 59.9 / 12, ".2f", "4.99")
has("E6 BLdP inputs", "a monthly ratio $2/\\sqrt{12}$ against $1/\\sqrt{12}$")
has("E6 BLdP table, normal", "| Normal | 38.9 | 3.24 |")
has("E6 BLdP table", "| Skewness −0.72, raw kurtosis 5.78 | 59.9 | 4.99 |")
chk("pitfall: R4 sessions", K.mintrl(SR["R4"], 0, mom["R4"][2], mom["R4"][3]), ",.0f", "1,717")
has("LM24's reading", "In [[LM24]] a flat prior gives a posterior probability equal to the one-sided p-value to the "
    "printed digits")
published("LM24's agreement", "lm24.md", "and the two agree to the printed digits")
has("Leaves: shrinkage", "Shrinking a Sharpe ratio toward a prior uses [[LM24]]'s tools and is not done here.")
chk("KC 5: misuse years", K.mintrl(SR["R2"], SR["R1"], sk2, ku2) / Aw, ".0f", "106")
chk("KC 5: misuse PSR", K.psr(SR["R2"], SR["R1"], T, sk2, ku2), ".2f", "0.67")

# ---------------------------------------------------------------- Section 6: two Sharpe ratios
p21 = K.PAIR["R2"]
chk("E7 Delta", p21["d"], "+.3f", "+0.162")
chk("E7 SE", p21["se"], ".3f", "0.253")
chk("E7 t-stat", p21["t"], "+.2f", "+0.64")
chk("E7 HAC lo", p21["hac_lo"], "+.2f", "-0.33")
chk("E7 HAC hi", p21["hac_hi"], "+.2f", "+0.66")
chk("E7 bootstrap MC SE", p21["p_se"], ".3f", "0.005")
chk("E7 quantile", p21["q"], ".1f", "2.0")
chk("E7 quantile MC SE", p21["q_se"], ".2f", "0.02")
chk("E7 boot lo", p21["boot_lo"], "+.2f", "-0.34")
chk("E7 boot hi", p21["boot_hi"], "+.2f", "+0.67")
chk("E7 t from printed", 0.162 / 0.253, "+.2f", "+0.64")
chk("E7 HAC lo from printed", 0.162 - Z975 * 0.253, "+.2f", "-0.33")
chk("E7 HAC hi from printed", 0.162 + Z975 * 0.253, "+.2f", "+0.66")
chk("E7 boot lo from printed", 0.162 - 2.0 * 0.253, "+.2f", "-0.34")
chk("E7 boot hi from printed", 0.162 + 2.0 * 0.253, "+.2f", "+0.67")
chk("E7 HAC multiple", Z975, ".2f", "1.96")
has("E7 table HAC", "| HAC, normal | 0.52 | 1.96 | −0.33 to +0.66 |")
has("E7 table bootstrap", "| Bootstrap | 0.52 (0.005) | 2.0 (0.02) | −0.34 to +0.67 |")
chk("experiment 3 largest MC SE", max(math.sqrt(p * (1 - p) / K.B) for p in K.sens_p.values()), ".3f", "0.005")
chk("experiment 3 smallest MC SE", min(math.sqrt(p * (1 - p) / K.B) for p in K.sens_p.values()), ".3f", "0.005")
has("experiment 3 B and MC SE", "repeats the bootstrap with $B=9{,}999$ at $b=1$, 5, 10, 26, 50 and 100. Its p-values "
    "run from 0.53 to 0.56, each with a Monte Carlo SE of 0.005.")
chk("circular estimates, largest", max(K.circ), ".2f", "25.65")
assert round(max(K.circ)) == 26 and 26 in K.sens_p
has("b = 26", "As in [[LM22]] it sets the circular blocks too, though the circular estimates reach 25.65, so "
    "experiment 3 includes $b=26$.")
has("QS kernel", "Andrews and Monahan's (1992) prewhitened quadratic-spectral kernel")
has("Algorithm 3.1", "(their Algorithm 3.1)")
for lg, p_ in ((0, "0.280"), (7, "0.253"), (22, "0.250"), (60, "0.243")):
    chk(f"E7 SE at lag {lg}", K.lw_parts(K.X["R2"], K.X["R1"], lg)[1] * sqA, ".3f", p_)
chk("E7 block sizes low", min(K.sens_p.values()), ".2f", "0.53")
chk("E7 block sizes high", max(K.sens_p.values()), ".2f", "0.56")
assert sorted(K.sens_p) == [1, 5, 10, 26, 50, 100]
chk("E7 gap, 4 dp", p21["d"], ".4f", "0.1617")
chk("E7 SE, 4 dp", p21["se"], ".4f", "0.2528")
c21 = 0.2528 * math.sqrt(7.60)
z80 = float(stats.norm.ppf(0.975) + stats.norm.ppf(0.8))
chk("E7 years for 80% power", (z80 * K.c21 * sqA / (K.dl21 * sqA)) ** 2, ".0f", "146")
chk("E7 years, one-sided", (Z95 * K.c21 * sqA / (K.dl21 * sqA)) ** 2, ".0f", "50")
chk("E7 years for 80% power from printed", (z80 * c21 / 0.1617) ** 2, ".0f", "146")
chk("E7 years, one-sided, from printed", (Z95 * c21 / 0.1617) ** 2, ".0f", "50")
chk("E7 one-year error from printed", c21, ".3f", "0.697")
chk("E7 one-year error", K.c21 * sqA, ".3f", "0.697")
chk("E7 80% power from the printed 0.697", (z80 * 0.697 / 0.1617) ** 2, ".0f", "146")
chk("E7 one-sided from the printed 0.697", (Z95 * 0.697 / 0.1617) ** 2, ".0f", "50")
has("E7 (21.4) scale", "so over one year it is $0.2528\\sqrt{7.60}=0.697$, where (21.4) has 1")
st = K.stat_
chk("block estimates low", min(st), ".2f", "16.66")
chk("block estimates high", max(st), ".2f", "22.41")
assert K.T == 84 * 22 + 3 and math.ceil(K.T / 22) == 85
has("last block", "a resample draws 85 blocks, keeps the first 1,851 rows and takes its block covariance from the 84 "
    "complete blocks")
has("T = 84 x 22 + 3", "$T=1{,}851=84\\times22+3$")
assert max(p["end_se"] for p in K.PAIR.values()) <= 0.006
has("X5 note", "Monte Carlo SE of the ends at most 0.006")
ph = {k: K.PAIR[k]["p_hac"] for k in RULES[1:]}
chk("pairs: smallest HAC p", min(ph.values()), ".2f", "0.22")
chk("pairs: largest HAC p", max(ph.values()), ".2f", "0.87")
assert min(ph, key=lambda k: ph[k]) == "R4" and max(ph, key=lambda k: ph[k]) == "R6"
assert min(K.hb) == 1.0 and min(K.hh) == 1.0
has("pairs: Holm", "Holm (21.7) on either family of seven adjusts every p-value to 1.00")
chk("KC 6: independent SE", K.naive * sqA, ".3f", "0.521")
chk("KC 6: sqrt(1 - rho)", math.sqrt(1 - K.r21), ".2f", "0.55")
chk("KC 6: sqrt(1 - rho) from printed", math.sqrt(1 - 0.70), ".2f", "0.55")
chk("KC 6: ratio at lag 0", K.lw_parts(K.X["R2"], K.X["R1"], 0)[1] / K.naive, ".2f", "0.54")
chk("KC 6: ratio at lag 7", K.sd21 / K.naive, ".2f", "0.49")
p4 = K.PAIR["R4"]
chk("S12 Delta", p4["d"], ".3f", "-0.347")
chk("S12 SE", p4["se"], ".3f", "0.285")
chk("S12 HAC p", p4["p_hac"], ".2f", "0.22")
chk("S12 HAC lo", p4["hac_lo"], "+.2f", "-0.91")
chk("S12 HAC hi", p4["hac_hi"], "+.2f", "+0.21")
chk("S12 boot p", p4["p_boot"], ".2f", "0.25")
chk("S12 boot MC SE", p4["p_se"], ".3f", "0.004")
chk("S12 quantile", p4["q"], ".1f", "2.1")
chk("S12 quantile MC SE", p4["q_se"], ".2f", "0.02")
chk("S12 boot lo", p4["boot_lo"], "+.2f", "-0.95")
chk("S12 boot hi", p4["boot_hi"], "+.2f", "+0.25")
chk("S12 boot lo from printed", -0.347 - 2.1 * 0.285, "+.2f", "-0.95")
chk("S12 boot hi from printed", -0.347 + 2.1 * 0.285, "+.2f", "+0.25")
assert 7 * min(ph.values()) > 1
has("S12 (b)", "The smallest HAC p-value, 0.22, times 7 exceeds 1")

# ---------------------------------------------------------------- Section 7: deflation
ez8 = K.emax(8)
chk("E Z_(8), 4 dp", ez8, ".4f", "1.4236")
chk("E Z_(8), 3 dp", ez8, ".3f", "1.424")
chk("approximation at 8", K.emax_bldp(8), ".3f", "1.459")
chk("median at 8", float(stats.norm.ppf(0.5 ** (1 / 8))), ".2f", "1.39")
chk("null SD a year", K.s0 * sqA, ".3f", "0.363")
chk("SR_0 at 8", K.SR0_8 * sqA, ".3f", "0.517")
chk("SR_0 from printed", 1.4236 * 0.363, ".3f", "0.517")
chk("E8 R2 a year", SRy["R2"], ".3f", "1.138")
chk("E8 gap from printed", 1.138 - 0.517, ".3f", "0.621")
zp = 0.621 * math.sqrt(1850 / 243.57) / math.sqrt(1.0249)
chk("E8 z from printed", zp, ".3f", "1.691")
z_exact = (SR["R2"] - K.SR0_8) * math.sqrt(T - 1) / math.sqrt(K.v209(SR["R2"], sk2, ku2))
chk("E8 z", z_exact, ".3f", "1.691")
chk("E8 DSR from printed", float(stats.norm.cdf(1.691)), ".3f", "0.955")
chk("E8 DSR", K.dsr_at(8), ".3f", "0.955")
chk("E8 DSR approx", K.psr(SR["R2"], K.emax_bldp(8) * K.s0, T, sk2, ku2), ".3f", "0.951")
chk("E8 DSR with HAC SE", K.dsr_at(8, SEH["R2"]), ".3f", "0.948")
chk("E8 n at 0.95", K.nstar, ".1f", "8.8")
assert 8.5 < K.nstar < 9.0
has("from nine trials on", "from nine trials on, R2's DSR is below 0.95")
assert K.dsr_at(9) < 0.95 < K.dsr_at(8)
has("X6 note: PSR line", "Dashed at 0.53, the $\\mathrm{SR}_0$ at which R2's PSR is 0.95")
assert abs(K.psr(SR["R2"], K.PASS_LINE / sqA, T, sk2, ku2) - 0.95) < 1e-9
has("null scale", "standard deviation $1/\\sqrt T$, which PSR's convention writes $1/\\sqrt{T-1}$")
Cm, off, iu = K.Cm, K.off, K.iu
chk("mean correlation", float(off.mean()), ".3f", "0.821")
chk("mean correlation, 2 dp", float(off.mean()), ".2f", "0.82")
chk("min correlation", float(Cm[iu].min()), ".2f", "0.61")
chk("max correlation", float(Cm[iu].max()), ".3f", "0.998")
assert (RULES[iu[0][K.pmin]], RULES[iu[1][K.pmin]], RULES[iu[0][K.pmax]], RULES[iu[1][K.pmax]]) == ("R3", "R4", "R3", "R5")
chk("R6-R8", float(Cm[5, 7]), ".2f", "0.96")
chk("R2-R1", float(Cm[1, 0]), ".2f", "0.70")
chk("experiment 2 mean", K.emc, ".3f", "0.588")
chk("experiment 2 MC SE", K.emc_se, ".4f", "0.0009")
chk("n_eff", K.neff, ".2f", "2.07")
chk("n_eff low", K.d_lo, ".2f", "2.06")
chk("n_eff high", K.d_hi, ".2f", "2.07")
chk("SR_0 at n_eff", K.emc * K.s0 * sqA, ".2f", "0.21")
chk("DSR at n_eff", K.psr(SR["R2"], K.emc * K.s0, T, sk2, ku2), ".3f", "0.994")
chk("eq. (9)", float(off.mean()) + (1 - float(off.mean())) * 8, ".2f", "2.25")
chk("eq. (9) from printed", 0.821 + (1 - 0.821) * 8, ".2f", "2.25")
chk("cross-section SD", K.cs_sd * sqA, ".3f", "0.141")
chk("expected SD", K.exp_sd * sqA, ".3f", "0.144")
chk("BLdP recipe SR_0", K.cs_sd * K.emax_bldp(8) * sqA, ".2f", "0.21")
chk("BLdP recipe from printed", 0.141 * 1.459, ".2f", "0.21")
chk("BLdP recipe DSR", K.psr(SR["R2"], K.cs_sd * K.emax_bldp(8), T, sk2, ku2), ".3f", "0.994")
sv = math.sqrt(1.0249)
for n_, ez, sess, yrs in ((1, 0.0, None, "2.15"), (8, 1.4236, "1,796", "7.37"), (100, 2.508, None, "13.5")):
    mt_p = 1 + ((Z95 * sv + ez) / 0.0729) ** 2
    if sess:
        chk(f"MinTRL at {n_} from printed", mt_p, ",.0f", sess)
        chk(f"MinTRL at {n_}", K.mintrl_n(ez8), ",.0f", sess)
    d_ = 1 if n_ == 100 else 2
    chk(f"MinTRL years at {n_} from printed", mt_p / 243.57, f".{d_}f", yrs)
chk("MinTRL years at 8", K.mintrl_n(ez8) / Aw, ".2f", "7.37")
chk("MinTRL years at 1", K.mintrl_n(0) / Aw, ".2f", "2.15")
chk("MinTRL years at 100", K.mintrl_n(K.emax(100)) / Aw, ".1f", "13.5")
chk("E Z_(100)", K.emax(100), ".3f", "2.508")
chk("MinTRL years at n_eff", K.mintrl_n(K.emc) / Aw, ".1f", "3.9")
assert f"{K.mintrl_n(K.emc - 2 * K.emc_se) / Aw:.1f}" == f"{K.mintrl_n(K.emc + 2 * K.emc_se) / Aw:.1f}" == "3.9"
chk("MinTRL at n_eff from printed", (1 + ((Z95 * sv + 0.588) / 0.0729) ** 2) / 243.57, ".1f", "3.9")
assert K.mintrl_n(ez8) < T
chk("BLdP 2014 SR_0", math.sqrt(K.v14) * K.emax_bldp(100), ".4f", "0.1132")
chk("BLdP 2014 DSR at 100", K.dsr14(100, -3, 10), ".4f", "0.9004")
chk("BLdP 2014 DSR at 46", K.dsr14(46, -3, 10), ".4f", "0.9505")
chk("BLdP 2014 DSR at 88, normal", K.dsr14(88, 0, 3), ".4f", "0.9505")
# the example's inputs, printed beside it (A33-51): SR 2.5 a year, T = 1,250 at 250 a year, variance 1/2, -3, 10
assert K.v14 == 0.5 / 250 and abs(K.sr14 - 2.5 / math.sqrt(250)) < 1e-15
assert K.dsr14(100, -3, 10) == K.psr(K.sr14, math.sqrt(K.v14) * K.emax_bldp(100), 1250, -3, 10)
has("BLdP 2014 inputs", "has a ratio of 2.5 a year over 1,250 days at 250 a year. The trials' annual ratios have "
    "variance ½.")
for row in ("| 100 | −3, 10 | 0.9004 |", "| 46 | −3, 10 | 0.9505 |", "| 88 | 0, 3 (normal) | 0.9505 |"):
    has("BLdP 2014 table", row)
has("BLdP 2014 SR_0", "$\\mathrm{SR}_0=0.1132$ a day at 100 trials")
# E8's MinTRL table: E Z_(n) and years of sessions at n = 1, n_eff, 8, 100
has("E8 table E Z", "| $\\E Z_{(n)}$ | 0 | 0.588 | 1.4236 | 2.508 |")
has("E8 table years", "| MinTRL, years of sessions | 2.15 | 3.9 | 7.37 | 13.5 |")
has("E8 table head", "| Trials $n$ | 1 | 2.07, effective | 8 | 100 |")
assert abs(K.emax(K.neff) - K.emc) < 1e-9                      # E Z at n_eff is experiment 2's mean
has("E8 1,796", "R2 needs the records below, 1,796 sessions at $n=8$")
ex6 = dict(zip(K.X6_N, K.X6_EXACT, strict=True))
for n_, p_ in ((1.0, "0"), (2.0, "0.20"), (8.0, "0.52"), (10.0, "0.56"), (100.0, "0.91"), (1000.0, "1.18"),
               (10000.0, "1.40")):
    if p_ != "0":
        chk(f"X6 at {n_:g}", ex6[n_], ".2f", p_)
    else:
        assert ex6[n_] == 0.0
has("X6 values", "Exact values: 0, 0.20, 0.52, 0.56, 0.91, 1.18 and 1.40 at $n=1$, 2, 8, 10, 100, 1,000 and 10,000")
chk("X6 approximation at 8", K.emax_bldp(8) * K.s0 * sqA, ".3f", "0.529")
chk("X6 pass line", K.PASS_LINE, ".2f", "0.53")
assert K.SR0_8 * sqA < K.PASS_LINE
has("gamma_E", "\\gamma_{\\mathrm E}&=0.5772")
assert f"{K.EULER:.4f}" == "0.5772"

# ---------------------------------------------------------------- Section 8: haircuts
pS2 = K.pS["R2"]
chk("E9 t-stat", SR["R2"] * math.sqrt(T), ".3f", "3.137")
chk("E9 p-value", pS2, ".5f", "0.00171")
chk("E9 independent", 1 - (1 - pS2) ** 8, ".4f", "0.0136")
chk("E9 Bonferroni", 8 * pS2, ".4f", "0.0137")
chk("E9 independent from printed", 1 - (1 - 0.00171) ** 8, ".4f", "0.0136")
chk("E9 Bonferroni from printed", 8 * 0.00171, ".4f", "0.0137")
t_adj = float(stats.norm.isf((1 - (1 - pS2) ** 8) / 2))
chk("E9 t-stat adj", t_adj, ".2f", "2.47")
chk("E9 t-stat adj from printed", float(stats.norm.isf(0.0136 / 2)), ".2f", "2.47")
chk("E9 HSR", K.HSR_IND["R2"], ".2f", "0.90")
chk("E9 HSR from printed", 1.138 * 2.47 / 3.137, ".2f", "0.90")
pct("E9 haircut", 1 - K.HSR_IND["R2"] / SRy["R2"], 0, "21")
pct("E9 haircut from printed", 1 - 2.47 / 3.137, 0, "21")
chk("X7 R2 Holm", K.HSR_HOLM["R2"], ".2f", "0.89")
has("X7 note", "R2: 1.14, 0.90 and 0.89")
# Bonferroni's HSR and haircut for R2, also Holm's (its first step multiplies the smallest p-value by n)
chk("E9 Bonferroni HSR", K.HSR_BON["R2"], ".2f", "0.89")
chk("E9 Bonferroni HSR from printed", 1.138 * float(stats.norm.isf(0.0137 / 2)) / 3.137, ".2f", "0.89")
pct("E9 Bonferroni haircut", 1 - K.HSR_BON["R2"] / SRy["R2"], 0, "21")
pct("E9 Bonferroni haircut from printed", 1 - float(stats.norm.isf(0.0137 / 2)) / 3.137, 0, "21")
assert min(RULES, key=lambda k: K.pS[k]) == "R2" and abs(K.HSR_HOLM["R2"] - K.HSR_BON["R2"]) < 1e-12
has("E9 Holm is Bonferroni", "Bonferroni's adjusted p-value is also Holm's for R2.")
has("E9 table independent", "| Eight independent tests | 0.0136 | 0.90 | 21% |")
has("E9 table Bonferroni", "| Bonferroni and Holm | 0.0137 | 0.89 | 21% |")
chk("HL normal p", K.two_sided(K.t240), ".4f", "0.0008")
chk("HL normal p_M", 1 - (1 - K.two_sided(K.t240)) ** 200, ".2f", "0.15")
chk("HL normal HSR", K.hn240, ".2f", "0.32")
pct("HL haircut from printed", (0.75 - 0.32) / 0.75, 0, "57")
chk("HL t239 HSR", K.h240, ".2f", "0.31")
has("HL example", "has 240 months, a ratio of 0.75 a year and 200 tests")
has("HL sixty", "their \"approximately 60%\"")
chk("KC 8: R4's p-value", K.pS["R4"], ".3f", "0.083")
pct("KC 8: Holm haircut of R4", 1 - K.HSR_HOLM["R4"] / SRy["R4"], 0, "0")
pct("KC 8: Bonferroni haircut of R4", 1 - K.HSR_BON["R4"] / SRy["R4"], 0, "75")
for k in ("R6", "R7", "R8"):
    chk(f"KC 8: Holm HSR {k}", K.HSR_HOLM[k], ".2f", "0.71")
assert max(RULES, key=lambda k: K.pS[k]) == "R4" and abs(K.HSR_HOLM["R4"] - SRy["R4"]) < 1e-12
pct("sizing: same 21%", 1 - K.HSR_IND["R2"] / SRy["R2"], 0, "21")
has("sizing", "the haircut cuts the fraction by the same 21%")
has("sizing: excess mean", "is $f_q\\approx\\mu/\\sigma^2$, with [[LM4]]'s $r_f=0$. With $\\mu$ the mean excess return "
    "it is $\\mathrm{SR}/\\sigma$")
published("LM4's r_f = 0", "lm04.md", "With $r_f=0$, as here, it is $\\mu/\\sigma$ per period.")
has("KC 8: Holm's step", "which Holm multiplies by 1. The product exceeds every smaller p-value's adjusted value")
hp_sorted = sorted(K.pS.values())
holm_adj = np.maximum.accumulate([min(1.0, (8 - i) * p) for i, p in enumerate(hp_sorted)])
assert hp_sorted[-1] > holm_adj[-2] and abs(holm_adj[-1] - hp_sorted[-1]) < 1e-15
has("BHY", "Their false-discovery version (BHY) is not used: [[LM21]] owns the false discovery rate.")
has("verdict", "On E5, the one-sided test rejects $\\mathrm{SR}\\le0$ for R2 at 5%, with PSR(0) 0.999. After eight "
    "trials its DSR is 0.955, near 0.95 by each of Section 7's three methods. Yet 7.60 calendar years cannot rank it "
    "above R1.")
assert 1 - K.PSR0["R2"] < 0.05 and all(abs(v - 0.95) < 0.006 for v in (K.dsr_at(8), K.dsr_at(8, SEH["R2"]),
                                                                  K.psr(SR["R2"], K.emax_bldp(8) * K.s0, T, sk2, ku2)))
published("LM4's warning", "lm04.md", "size from a haircut estimate, then take a fraction of Kelly")
published("LM4's f*", "lm04.md", "$f^*\\approx\\mu/\\sigma^2=\\mathrm{SR}/\\sigma$")

# ---------------------------------------------------------------- practice problems and solutions
p1 = math.sqrt((1 + 0.06**2 / 2) / 1851)
chk("P1 daily", p1, ".4f", "0.0233")
chk("P1 annual", p1 * math.sqrt(243.57), ".3f", "0.363")
chk("P1 times A", p1 * 243.57, ".2f", "5.67")
chk("P2 factor", K.v209(0.3, -1, 8), ".4f", "1.4575")
chk("P2 SE", math.sqrt(K.v209(0.3, -1, 8) / 90), ".3f", "0.127")
chk("P2 excess as raw", math.sqrt(K.v209(0.3, -1, 5) / 90), ".3f", "0.124")
chk("P2 normal", math.sqrt(K.v209(0.3, 0, 3) / 90), ".3f", "0.108")
chk("S2 from printed", math.sqrt(1.4575 / 90), ".3f", "0.127")
chk("S2 terms", 1 + 0.30 + 0.25 * 7 * 0.09, ".4f", "1.4575")
chk("P3 V", K.v209(0.05, 0, 3), ".5f", "1.00125")
chk("P3 MinTRL", K.n3, ",.0f", "1,085")
chk("P3 years", K.n3 / 243.57, ".2f", "4.45")
chk("P3 from printed", 1 + 1.00125 * (1.644854 / 0.05) ** 2, ",.0f", "1,085")
chk("P3 two-sided", K.n3b / 243.57, ".2f", "6.32")
chk("P3 annual in daily", K.n3c / 243.57, ".3f", "0.028")
chk("P4 exact", K.emax(5), ".3f", "1.163")
chk("P4 approximation", K.emax_bldp(5), ".3f", "1.193")
chk("P4 median", float(stats.norm.ppf(0.5**0.2)), ".3f", "1.129")
chk("P5", 12 / math.sqrt(12 + 2 * 11 * 0.1), ".3f", "3.184")
chk("P5 reversed", 12 / math.sqrt(12 - 2 * 11 * 0.1), ".3f", "3.833")
chk("P5 sqrt12", math.sqrt(12), ".3f", "3.464")
chk("P6", 0.36 * math.sqrt(2 * 0.1), ".3f", "0.161")
chk("P6 t", 0.2 / (0.36 * math.sqrt(0.2)), ".2f", "1.24")
chk("P6 independent", 0.36 * math.sqrt(2), ".3f", "0.509")
chk("P6 independent t", 0.2 / (0.36 * math.sqrt(2)), ".2f", "0.39")
chk("P6 wrong", 0.36 * 0.1, ".3f", "0.036")
assert re.findall(r"^\d+\. \*\*([ABC])\*\* is correct", RAW, flags=re.MULTILINE) == ["B", "C", "A", "C", "B", "A"]
chk("P8 E max", 1 / math.sqrt(math.pi), ".4f", "0.5642")
chk("P8 E max by (33.4)", K.emax(2), ".4f", "0.5642")
chk("P8 approximation at 2", K.emax_bldp(2), ".3f", "0.520")
chk("P8 (b)", math.sqrt(0.5 / math.pi), ".4f", "0.3989")
chk("P8 (b) n", K.n05, ".3f", "1.608")
has("P8 (b) eq. (9)", "$0.5+0.5\\times2=1.5$")
p9 = K.two_sided(2.5)
chk("P9 p", p9, ".5f", "0.01242")
chk("P9 adjusted", 1 - (1 - p9) ** 10, ".4f", "0.1175")
chk("P9 adjusted from printed", 1 - (1 - 0.01242) ** 10, ".4f", "0.1175")
t9 = float(stats.norm.isf((1 - (1 - p9) ** 10) / 2))
chk("P9 t adj", t9, ".3f", "1.565")
chk("P9 t adj from printed", float(stats.norm.isf(0.1175 / 2)), ".3f", "1.565")
pct("P9 haircut", 1 - t9 / 2.5, 1, "37.4")
pct("P9 haircut from printed", 1 - 1.565 / 2.5, 1, "37.4")
chk("P9 Bonferroni", 10 * p9, ".4f", "0.1242")
tb = float(stats.norm.isf(10 * p9 / 2))
chk("P9 Bonferroni t", tb, ".3f", "1.537")
pct("P9 Bonferroni haircut", 1 - tb / 2.5, 1, "38.5")
pct("P9 Bonferroni haircut from printed", 1 - 1.537 / 2.5, 1, "38.5")
assert [f"{lc['R2'][lg]:.3f}" for lg in (0, 7, 20, 60)] == ["0.367", "0.382", "0.393", "0.389"]
has("S11 (b)", "The lab gives 0.367, 0.382, 0.393 and 0.389 a year")
has("S10", "The lab gives 0.305, 1.06 by $\\sqrt{12}$ and 0.92 by (19.9), from the ratio 1.31 with robust standard "
    "error 0.38")
assert (K.den["R1"] - 1) / K.serob["R1"] < 1
has("P12 stem", "Draw 85 blocks and cut them to 1,851 rows, with the block covariance from the 84 complete blocks.")
has("S7 R2", "For R2, (33.5) gives 1,796 sessions, below 1,851, so DSR exceeds 0.95.")

# ---------------------------------------------------------------- inputs of stems, quoted values, rounded restatements
has("P1 stem", "Sharpe ratio 0.06, $T=1{,}851$ and $A=243.57$ (constructed)")
has("P2 stem", "A monthly Sharpe ratio of 0.30 has skewness −1.0 and raw kurtosis 8.0 over $T=90$ months")
has("P3 stem", "Daily returns are normal with Sharpe ratio 0.05 (constructed)")
has("P5 stem", "Monthly log returns have $\\rho_1=0.1$ and no other autocorrelation")
has("P6 stem", "Two annual Sharpe ratio estimates are 1.0 and 0.8, each with standard error 0.36, and their "
    "estimation errors correlate 0.9")
has("P9 stem", "A backtest's t-stat is 2.5 among ten independent tests")
has("KC 4 stem", "with $\\rho_1=0.2$, so that $\\rho_k=0.2^k$")
has("S3 quantile", "$1+1.00125\\times(1.644854/0.05)^2=1{,}085$")
has("S3 two-sided", "B uses the two-sided quantile $\\Phi^{-1}(0.975)$")
has("E6 1.645", "$(1.645/0.8115)^2=4.11$")
has("E8 1,850", "$1/\\sqrt{1{,}850}$")
has("E8 z", "z&=\\frac{0.621\\sqrt{1{,}850/243.57}}{\\sqrt{1.0249}}=1.691")
has("E7 B", "Experiment 1 draws $B=9{,}999$ resamples")
has("LW Remark", "(their Remark 3.2, eq. (9))")
assert all(f"{SE9[k] * sqA:.2f}" == "0.37" for k in RULES)
has("overview: about 0.37", "Each standard error is about 0.37")
has("zh: 0.37", "八條規則的標準誤都在 0.37 左右")
assert f"{min(K.vr.values()):.1f}" == "1.5" and f"{max(K.vr.values()):.1f}" == "1.6"
has("zh: 1.5 to 1.6", "在落期 7 放大到 1.5 到 1.6 倍")
has("zh: 146 years of sessions", "146 年份的交易日")
has("zh: 4.20 years of sessions", "MinTRL 只要 4.20 年份的交易日")
assert "落後期" not in RAW, "the book's form for lag is 落期 (SOURCES, decision XB2)"
# every Chinese term glossed in a box, at its first use there, is the book's printed pairing
for term in ("夏普比率（Sharpe ratio）", "標準誤（standard error）", "偏態（skewness）", "峰態（kurtosis）",
             "超額峰態（excess kurtosis）", "自我相關（autocorrelation）", "長期變異數（long-run variance）",
             "落期（lag）", "單邊檢定（one-sided test）", "檢定力（power）", "循環區塊（circular block）",
             "區塊自助重抽法（block bootstrap）", "Student化信賴區間（studentized confidence interval）",
             "選擇偏誤（selection bias）", "順序統計量（order statistic）", "多重假設檢定（multiple testing）",
             "變異數非齊一與自我相關一致估計量（HAC）", "相依性（dependence）", "基準（benchmark）",
             "相關係數（correlation coefficient）", "彼此獨立（independent）"):
    assert term in RAW, term
# each box glosses its own first uses (lessons item 23); forms without a SOURCES row stay out (試驗, 標準化, 雙邊)
boxes = re.findall(r"^> \[!zh\][^\n]*\n((?:>[^\n]*\n?)+)", RAW, flags=re.MULTILINE)
assert len(boxes) == 5, len(boxes)
for term, box_no in (("基準（benchmark）", 2), ("基準（benchmark）", 4), ("相關係數（correlation coefficient）", 3),
                     ("相關係數（correlation coefficient）", 4), ("彼此獨立（independent）", 4),
                     ("相依性（dependence）", 3), ("two-sided", 2)):
    assert term in boxes[box_no], (term, box_no)
for absent in ("試驗", "標準化", "雙邊", "雙尾"):
    assert all(absent not in b for b in boxes), absent
has("zh: half", "差的標準誤（standard error）只有當成獨立樣本時的一半")
assert f"{K.sd21 / K.naive:.1f}" == "0.5"                            # 0.49, printed as "half"
has("zh: two independent rules", "效果約等於只有 2 條彼此獨立的規則")
assert round(K.neff) == 2
has("LM21's 11.9", "[[LM21]]'s two-sided test at 80% power needed 11.9 years of daily data")
has("pitfall: quoted kurtoses", "TR23's 8.27 in [[LM20]] is raw, its excess 5.27 in [[LM19]], while 0050's 8.12 in "
    "[[LM4]] is excess")

# ---------------------------------------------------------------- the charts and the widget block
for name in ("forest", "haclag", "psrT", "pairs", "deflate", "haircut", "mintrack"):
    spec = json.loads((ROOT / "src" / "data" / f"lm33-{name}.json").read_text(encoding="utf-8"))
    assert spec["alt"].strip(), name
wb = json.loads((ROOT / "src" / "data" / "lm33-mintrack.json").read_text(encoding="utf-8"))["widget"]
assert wb["rules"] == RULES and wb["T"] == [T] * 8 and wb["Aw"] == float(Aw) and wb["tau"] == float(tau)
for j, k in enumerate(RULES):
    assert wb["sr"][j] == SR[k] and wb["skew"][j] == mom[k][2] and wb["kurt"][j] == mom[k][3], k
hc = json.loads((ROOT / "src" / "data" / "lm33-haircut.json").read_text(encoding="utf-8"))
assert [f"{v:.2f}" for v in hc["series"][1]["values"]] == [f"{K.HSR_IND[k]:.2f}" for k in RULES]
print("charts: seven specs with alt text; the widget block equals the rules' unrounded moments")

# ====================================================================== structure: labels, tags and citations
ex_labels = re.findall(r"\[!exhibit\][^\n]*\{#([\w-]+)\}", RAW)
eg_labels = re.findall(r"\[!example\][^\n]*\{#([\w-]+)\}", RAW)
assert len(ex_labels) == 7 and len(eg_labels) == 9, (ex_labels, eg_labels)
assert len(set(ex_labels) | set(eg_labels)) == 16, "a label is used twice"
for lab in ex_labels:
    assert f"[[ex:{lab}]]" in RAW, f"exhibit {lab} is never cited"
for kind, lab in re.findall(r"\[\[(ex|eg):([\w-]+)\]\]", RAW):
    assert lab in (ex_labels if kind == "ex" else eg_labels), (kind, lab)
tags = re.findall(r"\\tag\{(33\.\d+)\}", RAW)
assert sorted(tags) == [f"33.{k}" for k in range(1, 8)], tags
for name in re.findall(r'data-chart="(lm33-[\w-]+)"', RAW):
    assert (ROOT / "src" / "data" / f"{name}.json").exists(), name
assert len(re.findall(r"^> \[!kc\]", RAW, flags=re.MULTILINE)) == 8
fm = RAW.split("\n---\n", 1)[0]
pm = re.search(r"prereq: \[([\d, ]+)\]", fm)
assert pm is not None
prereq = [int(x) for x in pm.group(1).split(",")]
body = RAW.split("\n---\n", 1)[1]
for n_ in prereq:
    assert f"[[LM{n_}]]" in body or re.search(rf"\({n_}\.\d+\)", body), f"prerequisite LM{n_} is never cited"
ml = re.search(r"leads: \[([\d, ]+)\]", fm)
assert ml is not None
leads = [int(x) for x in ml.group(1).split(",")]
for n_ in {int(x) for x in re.findall(r"\[\[LM(\d+)", body)}:      # decision C9: every link is a prereq or a lead
    assert n_ in prereq or n_ in leads, f"[[LM{n_}]] is neither a prerequisite nor a lead"
assert "[[LM7]]" not in RAW
# notation note: every declared local symbol is used outside the note (lessons item 21)
note = RAW.split("> [!note] Notation for this module", 1)[1].split("\n\n", 1)[0]
rest = RAW.replace(note, "")
for sym in ("\\hat\\Delta", "\\hat V_{\\mathrm{SR}}", "\\mathbf v_t", "\\hat\\Psi", "\\hat\\Gamma_k", "Z_{(n)}",
            "n_{\\mathrm{eff}}", "\\bar\\rho", "\\gamma_{\\mathrm E}", "\\text{t-stat}_{\\text{adj}}",
            "\\hat\\Delta_{\\text{boot},i}"):
    assert sym in rest, sym
assert "\\widehat{\\mathrm{SR}}_j" not in RAW and "\\Delta=\\mathrm{SR}_j" not in RAW
has("TR23 in the notation note", "TR23 is the TAIEX total-return index of Volumes III and IV, with $T=5{,}849$ "
    "returns and $A=246.12$ as in [[LM19]], and $r_f=0$.")
# paragraphs open with a named subject (lessons item 34)
for opener in ("Ledoit and Wolf do not say how to cut", "Bailey and López de Prado's example (2014, pp. 9–10)"):
    has("named subject", opener)
assert "The paper does not say" not in RAW and "Their example (2014" not in RAW
# plain verbs (lessons item 35), one term for the benchmark (item 24), no pass/fail verdict on a DSR (decision D)
for phrase in ("left out", "turn the adjusted", "From the smallest up", "hurdle", "survives eight", "clears",
               "pass line", "passes at"):
    assert phrase not in RAW, phrase
has("scale factor condition", "It equals $\\sqrt m$ when every $\\rho_k$ is 0, and more generally when the weighted "
    "sum in the denominator is 0.")
# quoted values and locations the checker listed (the page and table numbers come from the source check, the brief)
brief = (ROOT / "plans" / "vol-6.md").read_text(encoding="utf-8").split("## LM33 ", 1)[1].split("\n## LM34", 1)[0]
for loc in ("p. 852", "p. 11", "pp. 9–10", "p. 41", "approximately 60%", "Table 2"):
    assert loc in brief, loc
    has(f"location {loc}", loc)
assert f"{K.ar:.2f}" == "2.88"
has("Lo's 2.88", "Lo's Table 2 (his p. 41) prints 2.88")
assert all(abs(K.se_sr_hac(K.X[k], 0) - SE9[k]) < 1e-15 for k in RULES)
has("lag 0 to 1e-15", "$\\ell=0$ equals (20.9) to $10^{-15}$")
assert scipy.__version__ == "1.18.1" and arch.__version__ == "8.0.0", (scipy.__version__, arch.__version__)
has("versions", "checked against SciPy 1.18.1; arch 8.0.0")
print(f"labels: {len(ex_labels)} exhibits, {len(eg_labels)} examples, tags (33.1)-(33.7), every exhibit cited, "
      f"every prerequisite cited")

# ====================================================================== report
body_t = TEXT.split("\n## Glossary", 1)[0]
nums = set(re.findall(r"(?<![\w.])\d+\.\d+|(?<![\w.,])\d{1,3}(?:,\d{3})+", body_t))
left = sorted(n for n in nums if n not in COVERED)
print(f"\nnumbers with a decimal point or thousands separator not covered by a check ({len(left)}):")
print("   " + " ".join(left))
print(f"anchor differences ({len(ANCHOR_DIFFS)}):")
for a in ANCHOR_DIFFS:
    print("   ", a)
print(f"\nall {N_CHECKS} checks passed")
np.seterr(all="ignore")
sys.exit(0)
