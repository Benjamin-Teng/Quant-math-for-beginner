"""Every number that LM29 (Convex Optimization in Practice) prints, computed and checked against src/lm29.md.

Run:  PYTHONUTF8=1 uv run python data/lm29_numbers.py
      (after data/vol5_series.py, data/vol5_rules.py and data/vol2_series.py, whose processed files
      data/lm29_common.py reads; and after data/lm29_charts.py, whose chart files and widget block this script checks)

Inputs: data/lm29_common.py, which is the Stage 1 anchor script data/vol5_anchors_lm29.py with its computations
unchanged (E5 through vol5_series.frames("E5"), the through case's rules through vol5_rules: schedule, WINDOW, RF,
SPREAD, the cost model, cov0, minvar, maxsharpe and the solver options; U28 through lm10_series.u28). No rule of the
through case is re-implemented here.

Part 1 compares each of the 35 anchor lines, as data/lm29_common.py rebuilds them, with the Value column of
plans/vol-5-anchors.md, "## LM29": a difference is reported, never forced.

Part 2 checks the text (each check stops the script on a failure):
  chk(label, value, fmt, printed)   format(value, fmt) equals the printed string, the value is not a rounding tie of
                                    that format, and the printed string is in the module as a whole number;
  sci(label, value, digits, printed)  the same for a number printed as m\\times10^{e};
  has(label, text)                  a literal string (a date, a phrase, a table row) is in the module;
  flag(label, value, d)             reports a printed value within a tenth of a unit of a rounding boundary at d
                                    decimals (the anchors' NEAR flag); it fails nothing.
Hand computations shown in the text are redone from the printed, rounded inputs (PITFALLS section 7). At the end the
script lists the numbers of the module that no check covered and prints "all N checks passed".
"""
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lm29_common as C  # computes every anchor quantity on import

ROOT = HERE.parent
MD = ROOT / "src" / "lm29.md"
ANCHORS = ROOT / "plans" / "vol-5-anchors.md"
CHARTS = ROOT / "src" / "data"


# ====================================================================== text helpers
def norm_text(s: str) -> str:
    """The module text with TeX thousands separators, escaped percent signs, thin spaces and minus signs made plain."""
    s = s.replace("{,}", ",").replace("\\%", "%").replace("\u2212", "-").replace("\\,", "").replace("\\\\", "\\")
    return re.sub(r"\\text\{\s*([^}]*)\}", r" \1", s)


RAW = MD.read_text(encoding="utf-8")
TEXT = norm_text(RAW)
N_CHECKS = 0
COVERED: set[str] = set()
ANCHOR_DIFFS: list[str] = []
FLAGS: list[str] = []


def in_text(printed: str) -> bool:
    """The printed number appears as a whole number (2.323 is not inside 2.3235, 0.32 not inside 10.32)."""
    return re.search(r"(?<![\d.])" + re.escape(printed) + r"(?![\d])", TEXT) is not None


def tie(value: float, fmt: str) -> bool:
    m = re.search(r"\.(\d+)", fmt)
    d = int(m.group(1)) if m else 0
    if fmt.endswith(("e", "g")):
        return False
    scaled = abs(value) * 10**d
    return abs(scaled - math.floor(scaled) - 0.5) < 1e-6


def chk(label: str, value: float, fmt: str, printed: str, in_md: bool = True) -> None:
    global N_CHECKS
    got = format(value, fmt)
    if got in ("-0", "-0.0", "-0.00"):
        got = got[1:]
    print(f"CHECK {label}: {got} (printed {printed})")
    assert got == printed, (label, got, printed)
    assert not tie(value, fmt), ("rounding tie: print more digits", label, value)
    assert not in_md or in_text(printed), f"{label}: {printed!r} not found in src/lm29.md"
    COVERED.add(printed.lstrip("-+"))
    N_CHECKS += 1


def sci(label: str, value: float, digits: int, printed: str) -> None:
    """A number printed as m\\times10^{e}: printed is 'm e', e.g. '8.6 -4'."""
    global N_CHECKS
    mant, ex = printed.split()
    got = f"{value:.{digits}e}"
    assert float(got) == float(f"{mant}e{ex}"), (label, got, printed)
    tex = f"{mant}\\times10^{{{ex}}}"
    assert tex in TEXT, f"{label}: {tex!r} not found in src/lm29.md"
    print(f"CHECK {label}: {got} (printed {tex})")
    COVERED.add(mant.lstrip("-"))
    N_CHECKS += 1


def below(label: str, value: float, exp: int, where: str) -> None:
    """A rounding-level value printed as the bound 'below 10^{exp}' (in the text at the given phrase)."""
    global N_CHECKS
    assert abs(value) < 10.0**exp, (label, value, exp)
    assert where in TEXT, f"{label}: {where!r} not found"
    print(f"CHECK {label}: |{value:.2e}| < 1e{exp} ('{where[:60]}')")
    N_CHECKS += 1


def has(label: str, text: str) -> None:
    global N_CHECKS
    t = norm_text(text)
    assert t in TEXT, f"{label}: {t!r} not found in src/lm29.md"
    print(f"CHECK {label}: '{t[:80]}' in text")
    for num in re.findall(r"\d[\d,]*\.?\d*", t):
        COVERED.add(num.rstrip(".,"))
    N_CHECKS += 1


def flag(label: str, value: float, d: int) -> None:
    y_ = abs(value) * 10**d
    if abs(y_ - math.floor(y_) - 0.5) < 0.1:
        FLAGS.append(f"{label}: {value:.{d + 3}f} lies within a tenth of a unit of a boundary at {d} decimals")


def pct(x: float, d: int) -> str:
    return f"{100 * x:.{d}f}"


# ====================================================================== part 1: anchors
def anchor_values() -> dict[str, str]:
    rows: dict[str, str] = {}
    sec = ANCHORS.read_text(encoding="utf-8").split("\n## LM29", 1)[1].split("\n## ", 1)[0]
    for line in sec.splitlines():
        if line.startswith("| A29-"):
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
            rows[cells[0]] = cells[3].strip("`").replace("\\|", "|")
    return rows


AV = anchor_values()
assert len(AV) == 35 and len(C.LINES) == 35, (len(AV), len(C.LINES))
for line in C.LINES:
    aid, val = line.split(" ", 1)
    tag = "ok" if val == AV[aid] else "DIFFERS"
    print(f"ANCHOR {aid}: {tag}")
    if val != AV[aid]:
        ANCHOR_DIFFS.append(f"{aid}:\n      script {val}\n      anchor {AV[aid]}")

# ====================================================================== part 2: the text
FUNDS = C.FUNDS
iF = {s: i for i, s in enumerate(FUNDS)}

# ---------------------------------------------------------------- front matter, data and windows (A29-01 .. A29-03)
assert len(C.fr.est_dates) == 2362 and len(C.WD) == 2368 and C.WINDOW == 504 and len(C.SCH) == 92
chk("A (estimation frame; echo A27-02)", C.A, ".2f", "242.95")
flag("A at 3 dp", C.A, 3)
chk("signals", len(C.SCH), "d", "92")
chk("window rows", C.WINDOW, "d", "504")
assert (C.sgL, C.dL[0], C.dL[-1]) == ("2026-09-30", "2024-08-23", "2026-09-30")
assert (C.sg0, C.d0[0], C.d0[-1]) == ("2019-02-27", "2017-02-13", "2019-02-27")
has("last window, case", "23 August 2024 to 30 September 2026")
has("last window, X1 note", "on the 504 joint dates 2024-08-23 → 2026-09-30")
has("first window, problem 9", "First window, 2017-02-13 to 2019-02-27")
chk("kappa low", C.kmin[0], ".2f", "9.72")
chk("kappa high", C.kmax[0], ".2f", "20.46")
flag("kappa high at 2 dp", C.kmax[0], 2)
assert min(C.lo_eig) > 0                                   # A Sigma_hat positive definite at all 92 windows
chk("r_f", 100 * C.RF, ".1f", "1.5")

# ---------------------------------------------------------------- the case and X1 (A29-04 .. A29-07)
mu2, vol2, e2 = [pct(v, 2) for v in C.muL], [pct(v, 2) for v in C.volL], [pct(v, 2) for v in C.eL]
wt2 = [pct(v, 2) for v in C.wtL]
w42 = ["0" if abs(v) < C.ZERO else pct(v, 2) for v in C.w4L]
for i, s in enumerate(FUNDS):
    has(f"X1 row {s}", f"| {s} | {mu2[i]} | {vol2[i]} | {e2[i]} | {wt2[i]} | {w42[i]} |")
    for v in (C.muL[i], C.eL[i], C.volL[i], C.wtL[i]):
        flag(f"X1 {s}", 100 * v, 2)
assert mu2 == ["48.78", "17.94", "-5.78", "20.68", "36.10"] and e2 == ["47.28", "16.44", "-7.28", "19.18", "34.60"]
assert vol2 == ["26.32", "17.89", "13.11", "24.30", "49.71"]
sr_t, sr_4 = C.sr(C.wtL, C.SL, C.eL), C.sr(C.w4L, C.SL, C.eL)
vt, v4 = C.vol(C.wtL, C.SL), C.vol(C.w4L, C.SL)
gross_t = float(np.abs(C.wtL).sum())
has("X1 Sharpe row", f"| Sharpe ratio | | | | {sr_t:.2f} | {sr_4:.2f} |")
has("X1 gross row", f"| Gross exposure (%) | | | | {100 * gross_t:.0f} | 100 |")
has("X1 volatility row", f"| Volatility (%) | | | | {pct(vt, 2)} | {pct(v4, 2)} |")
flag("gross at 0 dp", 100 * gross_t, 0)
flag("tangency volatility", 100 * vt, 2)
flag("R4 volatility", 100 * v4, 2)
# the printed weights sum to 100.00, and each Sharpe ratio recomputes from the printed weights, e and volatility
assert abs(sum(float(x) for x in wt2) - 100) < 1e-9 and abs(sum(float(x) for x in w42) - 100) < 1e-9
e2f = [float(x) for x in e2]
chk("X1 tangency SR from printed", sum(float(w) * e for w, e in zip(wt2, e2f, strict=True)) / 100 / float(pct(vt, 2)),
    ".2f", "2.18")
chk("X1 R4 SR from printed", sum(float(w) * e for w, e in zip(w42, e2f, strict=True)) / 100 / float(pct(v4, 2)),
    ".2f", "2.11")
for v, p in zip(C.wtL, ["114.24", "-27.75", "-48.48", "31.07", "30.92"], strict=True):
    chk("case: tangency weight", 100 * float(v), ".2f", p)
chk("case: gross", 100 * gross_t, ".0f", "252")
chk("case: SR tangency", sr_t, ".2f", "2.18")
chk("case: 92 month-ends that short", C.shorts, "d", "92")
chk("case: SR R4", sr_4, ".2f", "2.11")
for i, p in ((0, "62.77"), (3, "18.37"), (4, "18.86")):
    chk("case: R4 weight", 100 * C.w4L[i], ".2f", p)
assert all(C.w4L[i] < C.ZERO for i in (1, 2))
chk("case: 00646's e", 100 * C.eL[1], ".2f", "16.44")
has("case box dates", "On 30 September 2026 the through case re-estimates its inputs from its last 504 joint trading days")

# ---------------------------------------------------------------- Section 2 and 3
has("cap 40%", "40% cap")
has("gross 150%", "gross exposure at most 150%")
has("volatility 25%", "volatility at most 25%")
has("floor", "\\mathbf w^{\\top}\\Sigma\\mathbf w\\ge0.01")
has("ellipsoid", "\\mathbf w^{\\top}\\Sigma\\mathbf w\\le(25%)^2")
has("cost KC", "0.1425%\\,\\lvert\\Delta_i\\rvert")
mu3 = [f"{100 * v:.3f}" for v in C.muL]
assert mu3 == ["48.775", "17.937", "-5.776", "20.678", "36.096"]
for i in (0, 4, 3):
    chk("E2 mean (3 dp)", 100 * C.muL[i], ".3f", mu3[i])
chk("E2 LP mean (A29-17)", 100 * float(C.muL @ C.vlp), ".2f", "38.08")
chk("E2 LP mean from the printed 3-dp means", 0.4 * 48.775 + 0.4 * 36.096 + 0.2 * 20.678, ".2f", "38.08")
assert np.abs(C.vlp - np.array([0.4, 0, 0, 0.2, 0.4])).max() < 1e-6
assert C.pdef.solver_stats.solver_name == "CLARABEL"
has("problem 3 means", "(48.775, 17.937, -5.776, 20.678, 36.096)%")
assert C.pinf.status == "infeasible" and C.punb.status == "unbounded" and C.dcp == "DCPError"
assert C.pinf.value == math.inf and C.punb.value == math.inf and C.wv.value is None and C.wv2.value is None
has("E3 infeasible", "`infeasible`, with `prob.value` `inf` and `w.value` `None`")
has("E3 unbounded", "`unbounded`, again with `prob.value` `inf` and `w.value` `None`")
has("E3 DCPError", "cvxpy raises a `DCPError`")
has("caps sum", "The caps sum to 75%")
chk("E3: R3's variance lambda/2 (A29-12)", C.lam3 / 2, ".4f", "0.0102")
assert C.lam3 / 2 >= 0.01                                  # with the budget the floor excludes nothing

# ---------------------------------------------------------------- Section 4: KKT, the LP read as a KKT point, U28
chk("E2 KKT: lambda", -20.678, ".3f", "-20.678")
for name, val, p in (("cap 0050", 48.775 - 20.678, "28.097"), ("cap 00642U", 36.096 - 20.678, "15.418"),
                     ("bound 00646", 20.678 - 17.937, "2.741"), ("bound 00679B", 20.678 + 5.776, "26.454")):
    chk(f"LP multiplier {name} from the printed means", val, ".3f", p)
chk("R3 smallest weight over 92 (A29-09)", 100 * C.r3min[0], ".2f", "0.13")
assert C.r3zero == 0 and C.r3min[1:] == ("0050", "2024-11-29")
has("R3 smallest weight", "its smallest weight is 0.13% (0050, 2024-11-29)")
assert C.u.X.shape[0] == 4382
has("U28 T", "$T=4,382$")
chk("U28 A (Volume II's)", C.u.A, ".2f", "245.48")
assert len(C.heldU) == 9 and len(C.outU) == 19
chk("U28 volatility", 100 * C.vol(C.wU, C.SU), ".2f", "12.10")
chk("U28 lambda", C.lamU, ".4f", "0.0293")
chk("U28 lambda = 2 sigma^2 from the printed 12.10%", 2 * 0.1210**2, ".4f", "0.0293")
chk("U28 lowest excluded beta (Cement)", C.bU[C.imin], ".6f", "1.000019")
assert C.u.names[C.imin] == "Cement" and C.u.names[C.imax] == "Optoelectronic"
chk("U28 highest excluded beta", C.bU[C.imax], ".3f", "1.480")
has("19 excluded", "The 19 excluded sectors")
chk("U28 unconstrained shorts (echo A28-13)", int((C.wuU < -C.ZERO).sum()), "d", "12")
chk("U28 unconstrained gross (echo A28-13)", float(np.abs(C.wuU).sum()), ".2f", "2.24")
assert len(C.held1) == 9 and len(set(C.held1) & set(C.heldU)) == 7
has("first half (echo A30-22)", "again holds 9 sectors, only 7 of them the full sample's")
has("2^28", "2^{28}=268,435,456")
assert 2**28 == 268_435_456

# ---------------------------------------------------------------- Section 5: R4 (A29-06 .. A29-11, A29-35)
chk("lambda (R4)", C.lam4, ".5f", "0.45062")
for i, p in ((1, "0.02337"), (2, "0.02920")):
    chk(f"nu {FUNDS[i]}", C.nu4[i], ".5f", p)
    flag(f"nu {FUNDS[i]}", C.nu4[i], 5)
has("E5 beta row", "| $\\beta_{i,p}$ | 1.190 | 0.544 | -0.020 | 0.483 | 0.871 |")
for i, p in enumerate(["1.190", "0.544", "-0.020", "0.483", "0.871"]):
    chk(f"beta {FUNDS[i]}", C.b4[i], ".3f", p)
has("E5 nu row", "| $\\nu_i$ | 0 | 0.02337 | 0.02920 | 0 | 0 |")
has("E5 nu/lambda row", "| $\\nu_i/\\lambda$ (points) | 0 | 5.19 | 6.48 | 0 | 0 |")
assert all(C.w4L[i] > C.ZERO for i in (0, 3, 4))
for i, p in ((1, "5.19"), (2, "6.48")):
    chk(f"nu/lambda {FUNDS[i]}", 100 * C.short[i], ".2f", p)
chk("mu_p - r_f (2 dp)", 100 * C.ep, ".2f", "39.72")
chk("mu_p - r_f (3 dp)", 100 * C.ep, ".3f", "39.722")
chk("00646 beta (5 dp)", C.b4[1], ".5f", "0.54436")
chk("00646 e (3 dp)", 100 * C.eL[1], ".3f", "16.437")
chk("00646 asks (from the printed inputs)", 0.54436 * 39.722, ".3f", "21.623")
chk("00646 asks (A29-10)", 100 * C.b4[1] * C.ep, ".3f", "21.623")
chk("KC 5: shortfall from the printed inputs", 0.54436 * 39.722 - 16.437, ".2f", "5.19")
chk("KC 5: shortfall unrounded", 100 * C.short[1], ".5f", "5.18612")
assert all(abs(C.nu4[i] / C.lam4 - C.short[i]) < 1e-12 for i in range(5))
assert (C.hist[1], C.hist[2], C.hist[3], C.hist[4], C.hist[5]) == (2, 21, 56, 13, 0)
has("R4 supports", "R4 holds one, two, three, four or five funds at 2, 21, 56, 13 and 0 signals")
chk("e>0 excluded", C.pos_out, "d", "80")
chk("fund-signals", 5 * len(C.SCH), "d", "460")
chk("hedges", C.neg_in, "d", "6")
hed = next(h for h in C.hedges if h[0] == "00679B" and h[1] == "2021-08-31")
chk("hedge weight", 100 * hed[2], ".1f", "14.4")
chk("hedge e", 100 * hed[3], ".2f", "-1.74")
has("hedge date", "00679B on 2021-08-31, for example, at 14.4% with $e_i=-1.74%$")
assert len(C.wrong) == 22
has("22 windows (echo A28-23)", "the 22 windows where [[LM28]]'s tangency does not")
chk("r_f sensitivity: largest weight change", 100 * C.chg[0], ".2f", "1.15")
assert C.chg[1:] == ("00635U", "0")
w_rf0 = C.maxsharpe(C.SL, C.muL, "x")
w_rf2 = C.maxsharpe(C.SL, C.muL - 0.02, "x")
assert w_rf0 is not None and w_rf2 is not None
sr_rf0 = C.sr(w_rf0, C.SL, C.muL)
sr_rf2 = C.sr(w_rf2, C.SL, C.muL - 0.02)
chk("R4 SR at r_f 0", sr_rf0, ".2f", "2.19")
chk("R4 SR at r_f 2%", sr_rf2, ".2f", "2.08")
# E6, the bumps (A29-11)
chk("SR (4 dp)", C.srL, ".4f", "2.1067")
chk("SR (6 dp)", C.srL, ".6f", "2.106733")
bump_sr = {}
for name in ("00646", "00679B"):
    i = iF[name]
    lb = np.zeros(5)
    lb[i] = -0.01
    wb = C.homog(C.SL, C.eL, f"bump {name}", lb=lb)
    bump_sr[name] = C.sr(wb, C.SL, C.eL)
chk("bump 00646 level", bump_sr["00646"], ".6f", "2.107817")
chk("bump 00646 gain", bump_sr["00646"] - C.srL, ".6f", "0.001084")
chk("bump 00646 first-order", C.srL**3 * C.nu4[1] * 0.01 / 2, ".6f", "0.001093")
flag("bump 00646 first-order", C.srL**3 * C.nu4[1] * 0.01 / 2, 6)
chk("bump 00646 first-order from the printed SR and nu", 2.106733**3 * 0.02337 * 0.01 / 2, ".6f", "0.001093")
chk("bump 00679B level", bump_sr["00679B"], ".6f", "2.108091")
flag("bump 00679B level", bump_sr["00679B"], 6)
chk("bump 00679B gain", bump_sr["00679B"] - C.srL, ".6f", "0.001358")
chk("bump 00679B first-order", C.srL**3 * C.nu4[2] * 0.01 / 2, ".6f", "0.001365")
chk("bump 00679B first-order from the printed SR and nu", 2.106733**3 * 0.02920 * 0.01 / 2, ".6f", "0.001365")
has("bump size", "relax $y_i\\ge0$ to $y_i\\ge-0.01$")

# ---------------------------------------------------------------- Section 6: cap, limits, frontier, leverage
chk("R3 00679B (last window)", 100 * C.w3L[2], ".1f", "56.5")
wc1 = [f"{100 * v:.1f}" for v in C.wc]
assert wc1 == ["6.0", "26.9", "40.0", "19.3", "7.8"] and abs(sum(float(x) for x in wc1) - 100) < 1e-9
has("E7 weights", "6.0, 26.9, 40.0, 19.3 and 7.8%")
chk("E7 capped volatility", 100 * math.sqrt(C.vc), ".2f", "10.52")
chk("R3 volatility", 100 * C.vol(C.w3L, C.SL), ".2f", "10.10")
chk("V", C.vc, ".7f", "0.0110665")
flag("V at 6 dp", C.vc, 6)
chk("nu_cap (6 dp)", C.nuc, ".6f", "0.010543")
chk("nu_cap (5 dp, KC 6)", C.nuc, ".5f", "0.01054")
chk("lambda (cap)", C.lamc, ".6f", "0.026350")
chk("lambda = 2V + 0.40 nu_cap from the printed inputs", 2 * 0.0110665 + 0.40 * 0.010543, ".6f", "0.026350")
chk("beta free", C.b_free, ".3f", "1.191")
flag("beta free", C.b_free, 3)
chk("beta free from the printed inputs", 0.026350 / (2 * 0.0110665), ".3f", "1.191")
chk("beta capped", C.b_cap, ".3f", "0.714")
chk("beta capped from the printed inputs", (0.026350 - 0.010543) / (2 * 0.0110665), ".3f", "0.714")
chk("41% first-order", -C.nuc * 0.01, ".6f", "-0.000105")
chk("41% first-order from the printed nu_cap (KC 6)", -0.01054 * 0.01, ".6f", "-0.000105")
chk("41% exact", C.v41 - C.vc, ".6f", "-0.000102")
chk("cap binds at", C.nbind, "d", "63")
has("41% cap", "a 41% cap should change the variance")
srs = [C.sr(w, C.SL, C.eL) for w in C.lims.values()]
vols = [C.vol(w, C.SL) for w in C.lims.values()]
for v, p in zip(srs, ["2.18", "2.16", "2.11", "2.00"], strict=True):
    chk("X2 Sharpe ratio", v, ".2f", p)
for v, p in zip(vols, ["31.94", "23.01", "18.85", "16.40"], strict=True):
    chk("X2 volatility", 100 * v, ".2f", p)
has("X2 note", "in-sample Sharpe ratios 2.18, 2.16, 2.11 and 2.00, volatilities 31.94%, 23.01%, 18.85% and 16.40%")
LIM = json.loads((CHARTS / "lm29-limits.json").read_text(encoding="utf-8"))
for ser, v, p in zip(LIM["series"], vols, ["2.18", "2.16", "2.11", "2.00"], strict=True):
    printed_w = [f"{x:.2f}" for x in ser["values"]]
    assert abs(sum(float(x) for x in printed_w) - 100) < 1e-9, (ser["name"], printed_w)
    chk(f"X2 {ser['name']}: SR from the plotted weights, X1's e and the printed volatility",
        sum(float(w) * e for w, e in zip(printed_w, e2f, strict=True)) / 100 / float(f"{100 * v:.2f}"), ".2f", p,
        in_md=False)
assert LIM["series"][1]["values"] == [78.82, -7.59, -17.41, 23.36, 22.82]
assert abs(sum(abs(x) for x in LIM["series"][1]["values"]) - 150) < 1e-9
assert LIM["series"][3]["values"] == [40.0, 14.37, 0.0, 27.48, 18.15]
chk("frontier: coincidence from", 100 * C.lo_m, ".2f", "4.12")
chk("frontier: coincidence to", 100 * C.hi_m, ".2f", "30.44")
chk("frontier: 40% unconstrained", 100 * C.vol(C.w30u, C.SL), ".2f", "18.29")
chk("frontier: 40% long-only", 100 * C.vol(C.w30l, C.SL), ".2f", "18.32")
chk("frontier: 0050 mean", 100 * C.muL[0], ".1f", "48.8")
chk("frontier: 0050 volatility", 100 * C.volL[0], ".1f", "26.3")
has("frontier end", "It ends at 0050, the highest mean (48.8%, 26.3%)")
chk("X3: R3's mean", 100 * C.mgmv, ".2f", "8.46")
chk("X3: tangency mean", 100 * float(C.wtL @ C.muL), ".2f", "71.13")
chk("X3: R4 mean", 100 * float(C.w4L @ C.muL), ".2f", "41.22")
has("X3 points", "R3, the global minimum (8.46%, 10.10%); R4 (41.22%, 18.85%); the tangency (71.13%, 31.94%)")
chk("X3: tangency slope from the printed point", (71.13 - 1.5) / 31.94, ".2f", "2.18")
chk("X3: R4 slope from the printed point", (41.22 - 1.5) / 18.85, ".2f", "2.11")
has("X3 slopes", "capital market lines from $r_f=1.5%$, slopes 2.18 and 2.11")
FRO = json.loads((CHARTS / "lm29-frontier.json").read_text(encoding="utf-8"))
lo_curve = FRO["curves"][1]
for m, vv in ((0.40, C.vol(C.w30l, C.SL)), (round(C.lo_m, 6), None), (round(C.hi_m, 6), None)):
    assert m in lo_curve["y"], m
    if vv is not None:
        assert abs(lo_curve["x"][lo_curve["y"].index(m)] - round(vv, 6)) < 1e-9
assert [p["at"] for p in FRO["points"]] == [[round(C.vol(C.w3L, C.SL), 6), round(C.mgmv, 6)],
                                            [round(v4, 6), round(float(C.w4L @ C.muL), 6)],
                                            [round(vt, 6), round(float(C.wtL @ C.muL), 6)]]
L_rf = [float(m.group(1)) for m in re.finditer(r"L ([\d.]+)%", C.LINES[34])]
chk("leverage at r_f 0 (A29-35)", L_rf[0], ".1f", "132.2")
chk("leverage at r_f 2% (A29-35)", L_rf[1], ".1f", "130.6")
has("leverage sentence", "At a 2-point spread and $r_f$ of 0% and 2%, $L=132.2%$ and 130.6%")

# ---------------------------------------------------------------- Section 7: costs (A29-19 .. A29-21)
drift1 = [f"{100 * v:.1f}" for v in C.wdc]
assert drift1 == ["2.2", "31.8", "35.7", "23.9", "6.4"] and abs(sum(float(x) for x in drift1) - 100) < 1e-9
has("E8 drifted row", "| Drifted weight (%) | 2.2 | 31.8 | 35.7 | 23.9 | 6.4 |")
tr1 = ["0" if abs(v) < C.ZERO else f"{100 * v:+.1f}".replace("+-", "-") for v in C.dp1]
assert tr1 == ["0", "-9.9", "+4.6", "+6.7", "-1.4"] and abs(sum(float(x) for x in tr1)) < 1e-9, tr1
has("E8 trade row", "| Trade at $\\theta=1$ (points) | 0 | -9.9 | +4.6 | +6.7 | -1.4 |")
chk("E8 turnover to R3", 100 * 0.5 * float(np.abs(C.w3c - C.wdc).sum()), ".2f", "18.72")
chk("E8 cost to R3", 100 * C.cost(C.w3c - C.wdc), ".3f", "0.072")
chk("E8 penalized turnover", 100 * 0.5 * float(np.abs(C.dp1).sum()), ".2f", "11.30")
chk("E8 penalized cost", 100 * C.cost(C.dp1), ".4f", "0.0435")
chk("E8 penalized volatility", 100 * C.vol(C.wp1, C.Sc), ".2f", "9.03")
flag("E8 penalized volatility", 100 * C.vol(C.wp1, C.Sc), 2)
chk("E8 R3 volatility", 100 * C.vol(C.w3c, C.Sc), ".2f", "8.97")
chk("E8 no-trade volatility", 100 * C.vol(C.wdc, C.Sc), ".2f", "9.51")
flag("E8 no-trade volatility", 100 * C.vol(C.wdc, C.Sc), 2)
chk("E8 lambda", C.lam_b, ".6f", "0.016660")
chk("band: buy edge", C.lam_b - C.COMMISSION, ".6f", "0.015235")
chk("band: taxed sell edge", C.lam_b + C.COMMISSION + 0.001, ".6f", "0.019085")
chk("band: 00679B's sell edge", C.lam_b + C.COMMISSION, ".6f", "0.018085")
chk("band: buy edge from the printed lambda", 0.016660 - 0.001425, ".6f", "0.015235")
chk("band: sell edge from the printed lambda", 0.016660 + 0.001425 + 0.001, ".6f", "0.019085")
chk("band: 00679B's edge from the printed lambda", 0.016660 + 0.001425, ".6f", "0.018085")
chk("KC 7: 0050's gradient", C.gp1[0], ".6f", "0.017684")
assert C.lam_b - C.COMMISSION < C.gp1[0] < C.lam_b + C.COMMISSION + 0.001
chk("no-trade threshold", C.bar, ".2f", "3.20")
assert (FUNDS[C.pair[0]], FUNDS[C.pair[1]]) == ("00646", "00635U")
has("threshold pair", "set by selling 00646 against buying 00635U")
has("theta units", "$\\theta=2/(\\delta\\tau)$; $\\delta=4$ with monthly trading, $\\tau=1/12$, gives $\\theta=6$")
assert 2 / (4 * (1 / 12)) == 6
BAND = json.loads((CHARTS / "lm29-band.json").read_text(encoding="utf-8"))
assert [a["y"] for a in BAND["ann"]] == [round(C.lam_b - C.COMMISSION, 6), round(C.lam_b + C.COMMISSION, 6),
                                         round(C.lam_b + C.COMMISSION + 0.001, 6)]
sweep = {}
for m in re.finditer(r"theta ([\d.]+): planned turnover ([\d.]+)% of theta 0's, planned cost ([\d.]+)% of theta 0's, "
                     r"no trade at (\d+) of 91, in-sample volatility given up mean ([\d.]+) bp, largest ([\d.]+) bp",
                     C.LINES[20]):
    sweep[m.group(1)] = [float(m.group(k)) for k in (2, 3, 5, 6)] + [int(m.group(4))]
assert list(sweep) == ["0", "0.25", "0.5", "1", "2", "5", "10"], list(sweep)
for th, (to, cs, vm, vx, q) in sweep.items():
    row = f"| {th} | {to:.1f} | {cs:.1f} | {q} | {vm:.1f} | {vx:.1f} |"
    has(f"X5 row theta {th}", row)
    for val in (to, cs, vm, vx):
        flag(f"X5 theta {th}", val, 1)
chk("X5: 91 signals", len(C.SCH) - 1, "d", "91")
chk("theta 1: planned turnover share", sweep["1"][0], ".1f", "31.5")
chk("theta 1: untraded", sweep["1"][4], "d", "31")
chk("theta 1: volatility given up", sweep["1"][2], ".1f", "4.9")
assert C.sweep_gap < 1e-5

# ---------------------------------------------------------------- Section 8: solvers (A29-22 .. A29-26)
assert C.names == {"R3 QP": "OSQP", "volatility limit (SOCP)": "CLARABEL", "cost-penalized QP": "OSQP"}
has("versions", "cvxpy 1.9.3 the default solver is OSQP 1.1.3")
has("CLARABEL version", "CLARABEL 0.11.1")
has("SCS version", "SCS 3.3.1")
has("SciPy version", "SciPy 1.18.1")
assert (C.dflt.tol_gap_abs, C.dflt.tol_gap_rel, C.dflt.tol_feas, C.dflt.max_iter) == (1e-8, 1e-8, 1e-8, 200)
assert [m.group(1) for m in C.osqp_def.values() if m is not None] == ["1e-5", "1e-5", "10000"]
has("defaults", "cvxpy's defaults are OSQP's $10^{-5}$ with 10,000 iterations and polishing, and CLARABEL's "
               "$10^{-8}$ with 200")
w30d = C.minvar(C.cov0(C.x0), "R3 first daily")
v_daily = float(w30d @ C.cov0(C.x0) @ w30d)
v_annual = float(w30d @ (C.A * C.cov0(C.x0)) @ w30d)
sci("daily optimal variance", v_daily, 3, "1.035 -5")
sci("annual optimal variance (echo A28-10)", v_annual, 3, "2.515 -3")
chk("tolerance share, daily", 100 * 1e-8 / v_daily, ".1f", "0.1")
chk("tolerance share, annual", 100 * 1e-8 / v_annual, ".4f", "0.0004")
gap_first = {}
for part in C.LINES[22].split(": ", 1)[1].split("; "):
    m = re.match(r"(daily|annual) (OSQP|CLARABEL) (default|book) ([\d.e+-]+)", part)
    if m:
        gap_first[" ".join(m.groups()[:3])] = float(m.group(4))
gap_worst = {}
for part in C.LINES[23].split(": ", 1)[1].split("; "):
    m = re.match(r"(R3|R4) (daily|annual) (OSQP|CLARABEL) (default|book) ([\d.e+-]+)", part)
    if m:
        gap_worst[" ".join(m.groups()[:4])] = float(m.group(5))
assert len(gap_first) == 8 and len(gap_worst) == 16
x7 = [("Daily", "OSQP", "default", "8.3 -9", "1.1 -8"), ("Daily", "CLARABEL", "default", "8.6 -4", "2.1 -3"),
      ("Daily", "CLARABEL", "the book's", "3.2 -8", "3.2 -7"), ("Annual", "CLARABEL", "default", "1.6 -5", "3.4 -5"),
      ("Annual", "CLARABEL", "the book's", "2.0 -11", "8.9 -9")]
for unit, sv, tol, p1, p2 in x7:
    key = f"{unit.lower()} {sv} {'book' if tol == 'the book' + chr(39) + 's' else 'default'}"
    sci(f"X7 first {key}", gap_first[key], 1, p1)
    sci(f"X7 worst {key}", gap_worst[f"R3 {key}"], 1, p2)
    m1, e1 = p1.split()
    m2, e2_ = p2.split()
    has(f"X7 row {key}", f"| {unit} | {sv} | {tol} | ${m1}\\times10^{{{e1}}}$ | ${m2}\\times10^{{{e2_}}}$ |")
below("X7 annual OSQP first", gap_first["annual OSQP default"], -15, "| Annual | OSQP | default | below $10^{-15}$ | "
      "below $10^{-15}$ |")
below("X7 annual OSQP worst", gap_worst["R3 annual OSQP default"], -15, "| Annual | OSQP | default |")
for unit in ("daily", "annual"):                          # OSQP's book rows equal its default rows (left out)
    assert gap_first[f"{unit} OSQP book"] == gap_first[f"{unit} OSQP default"]
    assert gap_worst[f"R3 {unit} OSQP book"] == gap_worst[f"R3 {unit} OSQP default"]
sci("X7 note: R4's worst", gap_worst["R4 annual CLARABEL default"], 1, "9.5 -7")
assert max(gap_worst[k] for k in gap_worst if k.startswith("R4")) == gap_worst["R4 annual CLARABEL default"]
sci("worst daily gap (pitfall, overview)", gap_worst["R3 daily CLARABEL default"], 1, "2.1 -3")
sci("worst annual gap (overview)", gap_worst["R3 annual CLARABEL default"], 1, "3.4 -5")
# E9: R4's checks (A29-25) and cvxpy's duals (A29-26)
chk_line = C.LINES[24]


def grab(after: str, text: str) -> float:
    m = re.search(re.escape(after) + r" ([-\d.e+]+)", text)
    assert m, after
    return float(m.group(1))


osqp_part, clar_part = chk_line.split("CLARABEL status")
for key in ("weight gap", "stationarity on held funds", "smallest nu", "complementarity"):
    below(f"E9 OSQP {key}", grab(key, osqp_part), -15, "| Stationarity on held funds | below $10^{-15}$ |")
sci("E9 CLARABEL stationarity", grab("stationarity on held funds", clar_part), 1, "9.3 -15")
sci("E9 CLARABEL smallest nu", grab("smallest nu", clar_part), 1, "-9.3 -15")
sci("E9 CLARABEL complementarity", grab("complementarity", clar_part), 1, "1.5 -14")
sci("E9 CLARABEL weight gap", grab("weight gap", clar_part), 1, "1.7 -13")
sci("E9 CLARABEL min y", grab("min y", clar_part), 1, "2.0 -13")
below("E9 closed form on the active set", grab("against the exact solution", chk_line.split("closed form")[1]), -15,
      "gives R4 to below $10^{-15}$")
assert "OSQP status optimal" in chk_line and "CLARABEL status optimal" in chk_line
assert [FUNDS[i] for i in C.act] == ["0050", "00635U", "00642U"]
has("E9 held funds", "{0050, 00635U, 00642U}")
for row in ("| Smallest $\\nu$ | below $10^{-15}$ | $-9.3\\times10^{-15}$ |",
            "| Complementarity | below $10^{-15}$ | $1.5\\times10^{-14}$ |",
            "| Weight gap to the exact solution | below $10^{-15}$ | $1.7\\times10^{-13}$ |"):
    has("E9 table row", row)
dual_line = C.LINES[25]
chk("E9: R3's budget dual", grab("R3 OSQP: budget dual", dual_line), ".6f", "-0.020396")
chk("E9: R3's budget dual (CLARABEL)", grab("R3 CLARABEL: budget dual", dual_line), ".6f", "-0.020396")
chk("E9: sigma_p from the printed dual", 100 * math.sqrt(0.020396 / 2), ".2f", "10.10")
chk("E9: R4's dual", grab("dual of e'y = 1", dual_line), ".4f", "-0.4506")
chk("E9: bound dual 00646", grab("00646", dual_line.split("bound duals")[-1]), ".4f", "0.0234")
chk("E9: bound dual 00679B", grab("00679B", dual_line.split("bound duals")[-1]), ".4f", "0.0292")
chk("cvxpy's dual = -lambda (R3)", -C.lam3, ".6f", "-0.020396")
chk("lambda (R3, 6 dp)", C.lam3, ".6f", "0.020396")
flag("lambda (R3)", C.lam3, 6)
# KC 8 and the scaling paragraph
sci("KC 8: daily miss", gap_first["daily CLARABEL default"], 1, "8.6 -4")
sci("KC 8: annual miss", gap_first["annual CLARABEL default"], 1, "1.6 -5")
sci("first signal OSQP daily (E9 text omitted; X7)", gap_first["daily OSQP default"], 1, "8.3 -9")

# ---------------------------------------------------------------- problems and solutions
chk("P2: nu", 2 * (0.015 - 0.0102), ".4f", "0.0096")
chk("P2: distractor B", 0.015 - 0.0102, ".4f", "0.0048")
chk("P2: distractor C", -2 * (0.015 - 0.0102), ".4f", "-0.0096")
chk("P2: beta", 0.015 / 0.0102, ".2f", "1.47")
has("P2 stem", "$\\sigma_p^2=0.0102$ (annual), and an excluded fund has $\\Cov(R_i,R_p)=0.015$")
chk("P5: SR", math.sqrt(2 / 0.4506), ".3f", "2.107")
chk("P5: distractor", math.sqrt(1 / 0.4506), ".3f", "1.490")
chk("P5: exact SR (A29-34)", C.srL, ".3f", "2.107")
chk("P6: volatility", 100 * math.sqrt(0.020396 / 2), ".2f", "10.10")
chk("P6: distractor", 100 * math.sqrt(0.020396), ".2f", "14.28")
g5 = [f"{v:.5f}" for v in C.Gd]
assert g5 == ["0.02318", "0.02513", "0.01383", "0.01280", "0.02503"], g5
flag("P7 gradient 00679B", float(C.Gd[2]), 5)
has("P7 gradient", "=(0.02318, 0.02513, 0.01383, 0.01280, 0.02503)$")
chk("P7: threshold from the printed gradients", (0.02513 - 0.01280) / (2 * 0.001425 + 0.001), ".4f", "3.2026")
chk("P7: threshold (A29-32)", C.bar5, ".4f", "3.2026")
chk("P7: threshold unrounded", C.bar, ".4f", "3.2022")
chk("P7: denominator", 2 * 0.001425 + 0.001, ".5f", "0.00385")
w30 = [f"{100 * v:.1f}" for v in C.w30]
assert w30 == ["10.7", "22.5", "41.4", "25.0", "0.4"] and abs(sum(float(x) for x in w30) - 100) < 1e-9
flag("P9 R3 00642U", 100 * C.w30[4], 1)
has("P9 R3 (echo A28-10)", "(10.7, 22.5, 41.4, 25.0, 0.4)%")
w31 = [f"{100 * v:.2f}" for v in C.w31[:3]]
assert w31 == ["10.57", "52.44", "36.99"] and abs(sum(float(x) for x in w31) - 100) < 1e-9
assert all(C.w31[i] < C.ZERO for i in (3, 4))
has("S9 R4", "R4 holds 10.57% in 0050, 52.44% in 00646 and 36.99% in 00679B")
chk("S9: SR", C.sr(C.w31, C.S0, C.e0), ".3f", "0.802")
has("LM28's 0.880 (echo A28-18)", "0.880")
x31 = C.w31 / float(C.w31 @ C.e0)
nu31 = 2 * C.S0 @ x31 - float(2 * x31 @ C.S0 @ x31) * C.e0
lam31 = float(2 * x31 @ C.S0 @ x31)
chk("S9: 00635U nu/lambda", 100 * nu31[3] / lam31, ".2f", "0.25")
flag("S9: 00635U nu/lambda", 100 * nu31[3] / lam31, 2)
chk("S9: 00642U nu/lambda", 100 * nu31[4] / lam31, ".2f", "8.01")
vto1 = [f"{100 * v:.1f}" for v in C.vto]
assert vto1 == ["2.2", "27.4", "36.9", "27.7", "5.8"] and abs(sum(float(x) for x in vto1) - 100) < 1e-9
flag("S10 00679B", 100 * C.vto[2], 1)
has("S10 weights", "(2.2, 27.4, 36.9, 27.7, 5.8)%")
chk("S10: volatility", 100 * C.vol(C.vto, C.Sc), ".2f", "9.24")
chk("S10: multiplier", C.nuto, ".5f", "0.00825")
assert float(np.abs(C.vpen - C.vto).max()) < 1e-9
has("S10 gap", "gives the same weights within $10^{-9}$")
has("P10 limit", "\\tfrac12\\lVert\\mathbf w-\\mathbf w^{\\mathrm{drift}}_t\\rVert_1\\le0.05")
# problem 11 (A29-31, A29-35)
p11 = C.LINES[30]
sp0, sp2 = p11.split("spread 0.00:")[1].split("spread 0.02:")
scale0, scale2 = grab("% =", sp0), grab("% =", sp2)
chk("S11: scale 0 (A29-31)", scale0, ".3f", "1.326")
chk("S11: scale 0 from the printed volatility", 25 / 18.85, ".3f", "1.326")
chk("S11: scale 2 from the printed volatility", 25 / 19.08, ".3f", "1.310")
chk("S11: scale 2 (A29-31)", scale2, ".3f", "1.310")
vol_tan2 = grab("scaled by 25% /", sp2)
chk("S11: tangency at 3.5%, volatility", vol_tan2, ".2f", "19.08")


def wts(part: str, after: str) -> list[float]:
    seg = part.split(after, 1)[1]
    return [float(m.group(1)) for m in re.finditer(r"(?:0050|00646|00679B|00635U|00642U) ([-\d.]+)", seg)][:5]


f0, f2 = wts(sp0, ": f "), wts(sp2, ": f ")
t2 = wts(sp2, "r_f + spread")
rows11 = [("R4", [C.w4L[i] * 100 for i in (0, 3, 4)], None, None),
          ("$\\mathbf f$, no spread", [f0[i] for i in (0, 3, 4)], grab("net exposure L", sp0),
           grab("excess return before financing", sp0)),
          ("Tangency at 3.5%", [t2[i] for i in (0, 3, 4)], None, None),
          ("$\\mathbf f$, 2 points", [f2[i] for i in (0, 3, 4)], grab("net exposure L", sp2),
           grab("excess return before financing", sp2))]
for name, ws, L_, er in rows11:
    cells = " | ".join(f"{v:.2f}" for v in ws)
    tail = " | | |" if L_ is None else f" | {L_:.1f} | {er:.2f} |"
    has(f"S11 row {name}", f"| {name} | {cells}{tail}")
for name, ws in (("f no spread", f0), ("f 2 points", f2), ("tangency 3.5%", t2)):
    for i in (1, 2):
        assert ws[i] == 0, (name, ws)
assert f0 == [83.22931, 0.0, 0.0, 24.36304, 25.00049] and f2[0] == 84.36397
chk("S11: financing", grab("financing spread x (L - 1)", sp2), ".2f", "0.62")
chk("S11: financing from the printed L", 2 * 0.310, ".2f", "0.62")
chk("S11: after financing", grab("excess return after financing", sp2), ".2f", "52.03")
chk("S11: after financing from the printed numbers", 52.65 - 0.62, ".2f", "52.03")
e3 = [47.275, 16.437, -7.276, 19.178, 34.596]
chk("S11: 52.67 from the printed exposures and X4's e", sum(float(f"{v:.2f}") * e for v, e in zip(f0, e3, strict=True))
    / 100, ".2f", "52.67")
chk("S11: 52.65 from the printed exposures and X4's e", sum(float(f"{v:.2f}") * e for v, e in zip(f2, e3, strict=True))
    / 100, ".2f", "52.65")
assert "'optimal_inaccurate'" in p11 and "SCS (eps 1e-9, max_iters 200,000)" in p11
has("P11 SCS settings", "SCS 3.3.1 (`eps` $10^{-9}$, 200,000 iterations)")
has("S11 tolerances", "CLARABEL and SCS agree within $10^{-6}$; at $10^{-12}$ CLARABEL returns `optimal_inaccurate`")
rf35 = C.LINES[34]
ex_rf = [float(m.group(1)) for m in re.finditer(r"excess return after financing ([\d.]+)%", rf35)]
chk("S11: r_f 0 after financing", ex_rf[0], ".2f", "54.01")
chk("S11: r_f 2% after financing", ex_rf[1], ".2f", "51.38")
has("S11 r_f", "$L=132.2%$ and 130.6%, and 54.01% and 51.38% after financing")
chk("S11: no-spread vol", 100 * v4, ".2f", "18.85")

# ---------------------------------------------------------------- the widget (A29-27)
WJ = json.loads((CHARTS / "lm29-kktPair.json").read_text(encoding="utf-8"))
blk = WJ["widget"]
assert blk["e"] == [float(C.pairE[0]), float(C.pairE[1])] and blk["cap"] == 1.0 and blk["delta"] == 4.0
assert abs(blk["s"][0] ** 2 - C.pairS[0, 0]) < 1e-15 and abs(blk["s"][1] ** 2 - C.pairS[1, 1]) < 1e-15
assert abs(blk["rho"] * blk["s"][0] * blk["s"][1] - C.pairS[0, 1]) < 1e-15
for v, p in zip([*blk["e"], *blk["s"]], ["6.04", "8.53", "13.50", "11.87"], strict=True):
    chk("widget readout input (echo A28-05, A28-06)", 100 * v, ".2f", p, in_md=False)
chk("widget readout correlation (echo A28-07)", blk["rho"], ".3f", "0.539", in_md=False)
DRIVER = r"""
const vm = require("vm"), fs = require("fs");
const ctx = { window: {}, document: { readyState: "loading", addEventListener() {} }, console };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[1], "utf8"), ctx);
vm.runInContext(fs.readFileSync(process.argv[2], "utf8"), ctx);
const M = ctx.window.Book.widgets.kktPair.math, q = JSON.parse(fs.readFileSync(0, "utf8"));
const S = [[q.s[0] * q.s[0], q.rho * q.s[0] * q.s[1]], [q.rho * q.s[0] * q.s[1], q.s[1] * q.s[1]]];
const fu = M.solve([[q.delta * S[0][0], q.delta * S[0][1]], [q.delta * S[1][0], q.delta * S[1][1]]], q.e);
process.stdout.write(JSON.stringify({ cands: M.candidates(q.e, S, q.delta, q.cap), fu: fu }));
"""
node = shutil.which("node")
assert node, "Node is needed to check the widget"
res = subprocess.run([node, "-e", DRIVER, str(ROOT / "src" / "assets" / "book.js"), str(ROOT / "src" / "lm29.js")],
                     input=json.dumps(blk), capture_output=True, text=True, encoding="utf-8", check=True)
js = json.loads(res.stdout)
solv = [c for c in js["cands"] if c["f"] is not None]
best = [c for c in solv if c["feasible"] and c["signs"]]
assert len(solv) == 7 and sum(c["feasible"] for c in solv) == 4 and sum(c["signs"] for c in solv) == 3 and len(best) == 1
b = best[0]
assert b["label"] == "cap, f\u2081\u22650"
chk("widget: unconstrained f1", js["fu"][0], ".2f", "0.16", in_md=False)
chk("widget: unconstrained f2", js["fu"][1], ".2f", "1.42", in_md=False)
chk("widget: optimum f1", abs(b["f"][0]) if abs(b["f"][0]) < 1e-12 else b["f"][0], ".2f", "0.00", in_md=False)
chk("widget: optimum f2", b["f"][1], ".2f", "1.00", in_md=False)
chk("widget: cap's multiplier", b["nu"][0], ".4f", "0.0289", in_md=False)
chk("widget: f1's multiplier", b["nu"][1], ".4f", "0.0031", in_md=False)
chk("widget: utility", b["utility"], ".4f", "0.0571", in_md=False)
signs_infeasible = sorted(c["label"] for c in solv if c["signs"] and not c["feasible"])
assert signs_infeasible == ["cap", "none"], signs_infeasible
has("widget sentence", "The widget lists the eight binding sets of a two-fund example.")
JS = (ROOT / "src" / "lm29.js").read_text(encoding="utf-8")
assert 'data-widget="kktPair"' in RAW and "B.widgets.kktPair = function" in JS
assert '"2017-02-13 → 2019-02-27, on its 504 joint dates; in-sample' in JS    # the widget's caption

# ---------------------------------------------------------------- overview (front matter) and other prose
has("overview: U28", "On U28, 19 sectors are excluded, the closest at 1.000019")
has("overview: 00646", "00646 earns 16.437 points a year above cash, but its beta asks for 21.623")
has("overview: cap", "raising R3's 40% cap to 41% lowers its variance by 0.000102, against the linear prediction 0.000105")
has("overview: sweep", "R3's path plans 31.5% of its turnover and leaves 31 of 91 signals untraded")
has("theta 1 text", "At $\\theta=1$ the path plans 31.5% of R3's turnover, leaves 31 signals untraded and gives up 4.9")
has("cost model", "0.1425% of $\\lVert\\boldsymbol\\Delta\\rVert_1$ plus a 0.1% tax on sales, none for 00679B")
has("problem conventions", "Costs are 0.1425% a side plus a 0.1% tax on sales (none for 00679B)")
has("tolerances", "CLARABEL's `tol_gap_abs`, `tol_gap_rel` and `tol_feas` to $10^{-12}$ for QPs and LPs, $10^{-10}$ "
                  "for cone programs")
has("P11 CLARABEL", "Solve by CLARABEL at $10^{-10}$")
has("lab box", "From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python "
               "data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, "
               "the notebook runs offline.")

# the 中文導讀 boxes and the constructed limits
chk("zh 5: 00646's e (2 dp)", 100 * C.eL[1], ".2f", "16.44")
chk("zh 5: 00646 asks (2 dp)", 100 * C.b4[1] * C.ep, ".2f", "21.62")
has("zh 5", "但它的 beta 要求 21.62")
has("zh 7", "$\\theta=1$ 只規劃 R3 原本 31.5% 的週轉率")
has("zh 7 bp", "平均高出 4.9 個基點")
has("zh 8", "R3 的目標函數（objective function）只有 $1.035\\times10^{-5}$")
has("zh 8 miss", "權重可能偏離 $2.1\\times10^{-3}$")
has("zh 5 months", "在貫穿案例的 92 個月底")
has("constructed: 10% in 00679B", "$-w_3\\le-0.10$")
has("constructed: cap row", "a 40% cap $w_i\\le0.40$")
has("E2 arithmetic", "0.4\\times48.775+0.4\\times36.096+0.2\\times20.678=38.08%")
for loc in ("§3.1.3, p. 69", "§3.2.3, p. 80", "§4.2.2, p. 138", "(4.34), p. 152", "§4.3.2, p. 151", "p. 156",
            "§5.5.3, p. 244", "(p. 227)", "§5.6.3, p. 251", "(5.57), p. 250"):
    has(f"Boyd and Vandenberghe {loc}", loc)
for tag in ("(7.13)", "(10.9)", "(10.10)", "(11.9)", "(12.6)", "(27.2)", "(27.5)", "(28.6)"):
    has(f"cited tag {tag}", tag)

# ====================================================================== structure: labels, tags, charts
ex_labels = re.findall(r"\[!exhibit\][^\n]*\{#([\w-]+)\}", RAW)
eg_labels = re.findall(r"\[!example\][^\n]*\{#([\w-]+)\}", RAW)
assert ex_labels == ["case", "kktR4", "limits", "frontier", "band", "costsweep", "solvers"], ex_labels
assert eg_labels == ["sets", "lp", "status", "u28", "r4", "bump", "cap", "rebal", "check"], eg_labels
assert len(set(ex_labels) | set(eg_labels)) == len(ex_labels) + len(eg_labels), "a label is used twice"
for lab in ex_labels:
    assert f"[[ex:{lab}]]" in RAW, f"exhibit {lab} is never cited"
for kind, lab in re.findall(r"\[\[(ex|eg):([\w-]+)\]\]", RAW):
    assert lab in (ex_labels if kind == "ex" else eg_labels), (kind, lab)
tags = re.findall(r"\\tag\{(29\.\d+)\}", RAW)
assert tags == [f"29.{k}" for k in range(1, 10)], tags
for name in re.findall(r'data-chart="(lm29-[\w-]+)"', RAW):
    assert (CHARTS / f"{name}.json").exists(), name
assert RAW.count("> [!kc]") == 8 and RAW.count("> [!zh]") == 5
assert "對偶變量（dual variable）" in RAW and "對偶變數" not in RAW and "有效限制（active constraint）" in RAW
assert "最優" not in RAW and "長期持有" not in RAW
print(f"labels: {len(ex_labels)} exhibits, {len(eg_labels)} examples, tags (29.1)-(29.9), every exhibit cited")

# ====================================================================== report
body = TEXT.split("\n## Glossary", 1)[0]
nums = set(re.findall(r"(?<![\w.])\d+\.\d+|(?<![\w.,])\d{1,3}(?:,\d{3})+", body))
left = sorted(n for n in nums if n not in COVERED)
print(f"\nnumbers with a decimal point or thousands separator not covered by a check ({len(left)}):")
print("   " + " ".join(left))
print(f"\nvalues near a rounding boundary at their printed precision ({len(FLAGS)}):")
for fl in FLAGS:
    print("   ", fl)
print(f"\nanchor differences ({len(ANCHOR_DIFFS)}):")
for a in ANCHOR_DIFFS:
    print("   ", a)
print(f"\nall {N_CHECKS} checks passed")
sys.exit(0)
