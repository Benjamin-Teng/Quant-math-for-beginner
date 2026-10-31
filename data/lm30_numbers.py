"""Every number that LM30 (Estimation Error and Robust Portfolios) prints, computed and checked against src/lm30.md.

Run:  uv run python data/lm30_numbers.py
      (after data/vol5_series.py, data/vol5_rules.py and data/vol2_series.py; and after data/lm30_charts.py, whose
      chart files and widget block this script checks)

Inputs and conventions: data/lm30_common.py, the computations of data/vol5_anchors_lm30.py with the same names (E5
from data/processed/vol5_frames.parquet; the through case from data/vol5_rules.py and its
data/processed/vol5_rules.parquet; U28 from data/processed/vol2_closes.parquet; LM10's printed C_pw). The module
text is src/lm30.md; plans/vol-5-anchors.md, "LM30", holds the Stage 1 anchors A30-01 .. A30-43.

Part 1 compares every anchor line, exactly as data/vol5_anchors_lm30.py prints it (lm30_common.LINES), with the
anchors table's Value column: a difference is reported, never forced.

Part 2 checks the text. Each check records a failure and the script exits 1 at the end if any failed:
  chk(label, value, fmt, printed)  format(value, fmt) equals the printed string, the value is not a rounding tie of
                                   that format, and the printed string is in the module as a whole number. Hand
                                   computations are redone from the printed, rounded inputs (PITFALLS section 7).
  mcv(label, x, se, printed, printed_se)  a Monte Carlo result: the SE rounds to one significant digit and the result
                                   prints at that digit (plans/vol-5.md, decision on the second recomputation).
  has(label, text)                 a literal string (a phrase, a table row) is in the module.
  flag(label, value, d)            reports a printed value within a tenth of a unit of a rounding boundary at d
                                   decimals (the anchors' NEAR flag); it fails nothing.
At the end the script lists the numbers of the module that no check covered and prints "all N checks passed".
"""
import json
import math
import re
import sys
from math import sqrt

import lm30_common as C
import numpy as np

ROOT = C.HERE.parent
MD = ROOT / "src" / "lm30.md"
ANCHORS = ROOT / "plans" / "vol-5-anchors.md"
DATA = ROOT / "src" / "data"


# ====================================================================== text helpers
def norm_text(s: str) -> str:
    """The module text with TeX thousands separators, escaped percent signs, \\text{} and minus signs made plain."""
    s = s.replace("{,}", ",").replace("\\%", "%").replace("\u2212", "-").replace("\\,", "")
    return re.sub(r"\\text\{\s*([^}]*)\}", r" \1", s)


RAW = MD.read_text(encoding="utf-8")
TEXT = norm_text(RAW)
N_CHECKS = 0
FAILS: list[str] = []
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
    return abs(scaled - math.floor(scaled) - 0.5) < 1e-9


def fail(msg: str) -> None:
    FAILS.append(msg)
    print("FAIL", msg)


def chk(label: str, value: float, fmt: str, printed: str, in_md: bool = True) -> None:
    global N_CHECKS
    N_CHECKS += 1
    is_int = fmt.endswith("d")
    got = format(int(value), fmt) if is_int else format(float(value), fmt)
    if got != printed:
        fail(f"{label}: computed {got}, printed {printed}")
        return
    if not is_int and tie(float(value), fmt):
        fail(f"{label}: {value!r} is a rounding tie at {fmt}")
    if in_md and not in_text(printed):
        fail(f"{label}: {printed!r} not found in src/lm30.md")
        return
    COVERED.add(printed.lstrip("-"))
    print(f"CHECK {label}: {got}")


def vals(label: str, values: list[float] | np.ndarray, fmt: str, printed: str) -> None:
    """Several values printed in one list, 'a, b, c' (each checked on its own)."""
    for i, (v, p) in enumerate(zip(values, printed.split(", "), strict=True)):
        chk(f"{label} [{i}]", float(v), fmt, p)


def k_of(se: float) -> int:
    return -math.floor(math.log10(float(f"{se:.0e}")))


def mcv(label: str, x: float, se: float, printed: str, printed_se: str, in_md: bool = True) -> None:
    """A Monte Carlo result and its SE, both printed at the SE's first significant digit."""
    k = k_of(se)
    chk(label, x, f".{k}f", printed, in_md)
    chk(label + " SE", se, f".{k}f", printed_se, in_md=False)
    if in_md and printed_se not in TEXT:
        fail(f"{label}: SE {printed_se} not in the text")


def has(label: str, text: str) -> None:
    global N_CHECKS
    N_CHECKS += 1
    if norm_text(text) not in TEXT:
        fail(f"{label}: {text[:90]!r} not found in src/lm30.md")
        return
    print(f"CHECK {label}: '{text[:70]}' in text")
    for num in re.findall(r"\d[\d,]*\.?\d*", norm_text(text)):
        COVERED.add(num.rstrip(".,"))


def flag(label: str, value: float, d: int) -> None:
    y_ = abs(value) * 10**d
    if abs(y_ - math.floor(y_) - 0.5) < 0.1:
        FLAGS.append(f"{label}: {value:.{d + 3}f} lies within a tenth of a unit of a boundary at {d} decimals")


def pct(x: float) -> float:
    return 100 * float(x)


# ====================================================================== part 1: the anchors
def anchor_rows() -> dict[str, str]:
    rows: dict[str, str] = {}
    sec = ANCHORS.read_text(encoding="utf-8").split("\n## LM30", 1)[1].split("\n## ", 1)[0]
    for line in sec.splitlines():
        if line.startswith("| A30-"):
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
            rows[cells[0]] = cells[3].strip("`").replace("\\|", "|")
    return rows


ROWS = anchor_rows()
assert len(ROWS) == 43, len(ROWS)
assert len(C.LINES) == 43
for line in C.LINES:
    aid, val = line.split(" ", 1)
    if ROWS[aid] == val:
        print(f"ANCHOR {aid}: ok")
    else:
        print(f"ANCHOR {aid}: DIFFERS")
        ANCHOR_DIFFS.append(f"{aid}:\n      script {val}\n      anchor {ROWS[aid]}")

# ====================================================================== part 2: the text
F5 = C.F5
i50, i646, i679, i635, i642 = (F5.index(k) for k in ("0050", "00646", "00679B", "00635U", "00642U"))

# ---------------------------------------------------------------- front matter, case and X1
chk("case: window", C.WINDOW, "d", "504")
chk("case: 00646 tangency weight", pct(C.w_tan[i646]), ".1f", "62.6")
chk("case: 00642U short", -pct(C.w_tan[i642]), ".1f", "14.7")
chk("case: SR* (2 dp)", C.sr_star, ".2f", "0.88")
chk("case: SR(1/N) (2 dp)", C.sr_1n, ".2f", "0.33")
mcv("case: SD of the 00646 exposure", pct(C.sd_b[i646]), pct(C.se_sd[i646]), "67.1", "0.5")
mcv("case: mean SR, both", C.mb, C.sb, "0.423", "0.003")
mcv("case: mean SR, covariances only", C.ms, C.ss, "0.87686", "0.00002")
chk("case: SR* (3 dp)", C.sr_star, ".3f", "0.880")
has("case: SEs", "The simulation's standard errors are 0.5 points, 0.003 and 0.00002.")
chk("case: R3 realized", pct(C.vols["R3"]), ".2f", "9.96")
chk("case: R1 realized", pct(C.vols["R1"]), ".2f", "12.48")
chk("case: R5 - R3", pct(C.vols["R5"] - C.vols["R3"]), ".2f", "0.01")
chk("X1: R5 realized", pct(C.vols["R5"]), ".2f", "9.97")
wt = [pct(v) for v in C.w_tan]
has("X1: tangency weights", "11.8 / 62.6 / 37.8 / 2.6 / −14.7%")
vals("X1: tangency weights", wt, ".1f", "11.8, 62.6, 37.8, 2.6, -14.7")
chk("X1: weights sum as printed", sum(round(v, 1) for v in wt), ".1f", "100.1")
chk("X1: SR(1/N)", C.sr_1n, ".3f", "0.327")
mcv("X1: mean SR, means only", C.mm, C.sm, "0.425", "0.003")
has("X1: SD row", "| SD of the 00646 exposure: both estimated / covariances only (points) | 67.1 / 4.73 |")
mcv("X1: SD covariances only, 00646", pct(C.sd_s[i646]), pct(C.se_sd[C.N5 + i646]), "4.73", "0.03")
has("X1: realized row", "| Realized volatility, net of costs: R1 / R3 / R5 | 12.48 / 9.96 / 9.97% |")
has("X1: note SEs", "SEs 0.003, 0.003 and 0.00002 for the Sharpe ratios, 0.5 and 0.03 points for the SDs.")
chk("X1: A", C.A, ".2f", "242.95")
chk("X1: R1 fixed weights, full sample", pct(C.vol(C.w1, C.cov0(C.fr.X), C.A)), ".2f", "11.49")
has("X1: dates", "13 February 2017 to 27 February 2019")
assert (C.d_first, C.d_last) == ("2017-02-13", "2019-02-27")
has("X1/X5 through-case span", "2019-03-05 → 2026-10-08")
assert (C.pd1[1], C.pd1[-1]) == ("2019-03-05", "2026-10-08")
chk("notation: U28 A", C.AU, ".4f", "245.4794")
chk("notation: U28 halves", C.H, ",d", "2,191")

# ---------------------------------------------------------------- section 2
vals("S2: annual means", [pct(v) for v in C.mu_a[:4]], ".1f", "7.5, 10.0, 2.6, 0.8")
chk("S2: 00642U mean", pct(C.mu_a[i642]), ".1f", "-1.4")
vals("S2: volatilities", [pct(v) for v in C.sd_a[:4]], ".1f", "13.5, 11.9, 8.5, 9.4")
chk("S2: 00642U volatility", pct(C.sd_a[i642]), ".1f", "23.2")
corr = C.C0[C.iu]
chk("S2: lowest correlation", float(corr.min()), ".2f", "-0.30")
chk("S2: highest correlation", float(corr.max()), ".2f", "0.54")
chk("S2: delta", C.delta_m, ".2f", "11.27")
chk("S2: sign flips", C.nneg, ",d", "2,115")
chk("S2: share of sign flips (coarser safe form)", 100 * C.p9, ".0f", "21")
se9 = 100 * sqrt(C.p9 * (1 - C.p9) / C.n1)
assert k_of(se9) == 1 and tie(100 * C.p9, ".1f") and C.nneg * 100 == 2115 * C.n1 // 100   # 21.15% exactly: a tie
chk("S2: SE of the share", se9, ".1f", "0.4", in_md=False)
has("S2: sign flips sentence", "In 2,115 of 10,000 samples (21%, SE 0.4 points)")
mcv("X2: SD 00679B both", pct(C.sd_b[i679]), pct(C.se_sd[i679]), "80.7", "0.6")
mcv("X2: SD 00679B covariances only", pct(C.sd_s[i679]), pct(C.se_sd[C.N5 + i679]), "4.79", "0.04")
has("X2: note SDs", "the SDs are 67.1 and 80.7 points, against 4.73 and 4.79 with the covariances alone (batch SEs "
                    "0.5, 0.6, 0.03 and 0.04)")
sd_closed = 100 * np.sqrt(np.diag(C.Si) / C.WINDOW) / C.delta_m       # (28.9) and (16.4): Sigma^-1 / (delta^2 T)
chk("S2: means-only SD of 00646, closed form", float(sd_closed[i646]), ".1f", "65.7")
mcv("E1: mean SR, both", C.mb, C.sb, "0.423", "0.003")
mcv("E1: mean SR, means only", C.mm, C.sm, "0.425", "0.003")
mcv("E1: mean SR, covariances only", C.ms, C.ss, "0.87686", "0.00002")
mcv("E1: median SR", C.q50(C.sr_b), C.med_se, "0.489", "0.004")
sdb, sds = 100 * C.sd_b, 100 * C.sd_s
seb, ses = 100 * C.se_sd[:C.N5], 100 * C.se_sd[C.N5:]
mcv("E1: smallest SD, both", float(sdb.min()), float(seb[int(np.argmin(sdb))]), "28.8", "0.2")
mcv("E1: largest SD, both", float(sdb.max()), float(seb[int(np.argmax(sdb))]), "80.7", "0.6")
assert int(np.argmin(sdb)) == i642 and int(np.argmax(sdb)) == i679
mcv("E1: smallest SD, cov only", float(sds.min()), float(ses[int(np.argmin(sds))]), "1.75", "0.01")
mcv("E1: largest SD, cov only", float(sds.max()), float(ses[int(np.argmax(sds))]), "4.79", "0.04")
assert all(0.15 <= v < 0.65 for v in seb) and all(0.005 <= v < 0.045 for v in ses)   # "batch SEs 0.2 to 0.6, 0.01 to 0.04"
assert [f"{v:.1f}" for v in (seb.min(), seb.max())] == ["0.2", "0.6"]
assert [f"{v:.2f}" for v in (ses.min(), ses.max())] == ["0.01", "0.04"]
has("E1: SD ranges", "Exposure SDs run from 28.8 to 80.7 points with both estimated and from 1.75 to 4.79 with the "
                     "covariances alone (batch SEs 0.2 to 0.6 and 0.01 to 0.04).")
assert (C.jlo, C.jhi) == (i646, i635)
mcv("E1: smallest ratio", float(C.ratio[C.jlo]), float(C.se_ratio[C.jlo]), "14.2", "0.1")
mcv("E1: largest ratio", float(C.ratio[C.jhi]), float(C.se_ratio[C.jhi]), "18.0", "0.1")
mcv("E1: SD 00635U both", pct(C.sd_b[i635]), pct(C.se_sd[i635]), "72.0", "0.5", in_md=True)
mcv("E1: SD 00635U cov only", pct(C.sd_s[i635]), pct(C.se_sd[C.N5 + i635]), "3.99", "0.03", in_md=True)
has("E1: ratios", "The ratio runs from 14.2 (00646: 67.1 against 4.73) to 18.0 (00635U: 72.0 against 3.99), batch SEs 0.1.")
rs = [pct(v) for v in C.rs_true]
chk("E1: smallest true risk share", min(rs), ".1f", "1.1")
chk("E1: largest true risk share", max(rs), ".1f", "50.2")
rsd, rse = 100 * C.rs_sd, 100 * C.rs_se
mcv("E1: smallest risk-share SD", float(rsd.min()), float(rse[int(np.argmin(rsd))]), "1.031", "0.007")
mcv("E1: largest risk-share SD", float(rsd.max()), float(rse[int(np.argmax(rsd))]), "1.67", "0.01")
has("E1: risk shares", "R1's true shares, 1.1% to 50.2%, are estimated with SDs of 1.031 to 1.67 points (batch SEs "
                       "0.007 and 0.01)")
has("E1: batches", "SEs of medians and SDs come from 20 batches of 500 samples.")
assert C.NB == 20 and C.n1 // C.NB == 500
chk("E2: tau", C.tau, ".4f", "2.0745")
flag("E2: tau at 3 dp", C.tau, 3)
vals("E2: volatilities", [pct(v) for v in C.sd_a], ".2f", "13.50, 11.87, 8.54, 9.39, 23.17")
se_from_printed = [v / sqrt(2.0745) for v in (13.50, 11.87, 8.54, 9.39, 23.17)]
vals("E2: SEs from the printed inputs", se_from_printed[:4], ".1f", "9.4, 8.2, 5.9, 6.5")
chk("E2: 00642U SE from the printed inputs", se_from_printed[4], ".1f", "16.1")
vals("E2: SEs, unrounded", [pct(v) for v in C.se_mean[:4]], ".1f", "9.4, 8.2, 5.9, 6.5")
chk("E2: 00642U SE, unrounded", pct(C.se_mean[4]), ".1f", "16.1")
has("E2: four of five", "So four of the five means lie within one SE of zero.")
assert C.nbelow == 4
chk("E2: RMS relative error of S_hat", 100 * C.rms_rel, ".1f", "8.5")
mcv("E2: predicted minimum variance", pct(C.mv_pred.mean()), pct(C.mv_pred.std() / sqrt(C.n1)), "4.990", "0.002")
mcv("E2: true minimum variance", pct(C.mv_true.mean()), pct(C.mv_true.std() / sqrt(C.n1)), "5.0353", "0.0001")
chk("E2: sigma_min", pct(C.vol(C.w_mv, C.S_d, C.A)), ".2f", "5.02")
chk("KC2: SE of 00646", pct(C.se_mean[i646]), ".1f", "8.2")
chk("KC2: SE over sqrt 2, from the printed 8.2", 8.2 / sqrt(2), ".1f", "5.8")
chk("KC2: SE over sqrt 2, unrounded", pct(C.se_mean[i646]) / sqrt(2), ".1f", "5.8")

# ---------------------------------------------------------------- section 3
has("S3: DGU abstract", "compared 14 models with 1/N on seven datasets")
assert [T for T, *_ in C.EXP2] == [126, 252, 504, 1008, 2016, 4032, 8064] and C.n2 == 2000
has("S3: experiment 2 design", "It draws 2,000 samples at each of seven lengths from 126 to 8,064 days")
E2m = [m for _, m, _, _, _ in C.EXP2]
E2s = [s_ for _, _, s_, _, _ in C.EXP2]
for (T, m, se_, _, _), p in zip(C.EXP2, ["0.230", "0.322", "0.422", "0.546", "0.672", "0.759", "0.816"], strict=True):
    mcv(f"E3: mean SR at T {T}", m, se_, p, f"{se_:.{k_of(se_)}f}", in_md=True)
assert f"{max(E2s):.3f}" == "0.008" and f"{min(E2s):.3f}" == "0.001"
assert all(k_of(s_) == 3 for s_ in E2s)
has("E3: SE range", "(SEs 0.008 to 0.001)")
yrs = [T / C.A for T, *_ in C.EXP2]
chk("E3: shortest length in years", yrs[0], ".2f", "0.52")
chk("E3: 252 days in years", yrs[1], ".2f", "1.04")
chk("E3: 504 days in years", yrs[2], ".2f", "2.07")
chk("E3: longest length in years", yrs[-1], ".1f", "33.2")
_, _, _, cm0, cs0 = C.EXP2[0]
mcv("E3: covariances only at 0.52 years", cm0, cs0, "0.8660", "0.0002")
has("E3: 1.04", "about equal to 1/N at 1.04 years of sessions (0.322, SE 0.008) and well above at 2.07 (0.422, SE 0.007)")
assert abs((E2m[1] - C.sr_1n) / E2s[1]) < 1          # "within one SE of 0.327" (X3's note)
has("X3: note", "0.322 at 1.04 years of sessions lies within one SE of 1/N's 0.327")
has("E3: DGU calibration", "1/N's monthly Sharpe ratio is 0.12 against the tangency's 0.15")
has("E3: DGU months", "needs more than 3,000 months with 25 assets to beat 1/N (pp. 1939–1941)")
chk("E3: their ratio", 0.12 / 0.15, ".1f", "0.8")
chk("E3: this model's ratio", C.sr_1n / C.sr_star, ".2f", "0.37")
has("E3: ratio inputs", "only 0.37 (0.327 against 0.880)")
chk("S3: 1,851 returns", len(C.pd1) - 1, ",d", "1,851")
chk("S3: R3 predicted, mean", pct(C.pred3.mean()), ".2f", "8.84")
chk("S3: R3 predicted, lowest", pct(C.pred3.min()), ".2f", "4.97")
chk("S3: R3 predicted, highest", pct(C.pred3.max()), ".2f", "10.42")
mcv("KC3: 1/N wins", 100 * C.p_lose, 100 * C.p_se, "31.4", "0.5")
has("KC3: question", "1/N has a true Sharpe ratio of 0.33 against the best 0.88, yet it beats the plug-in in 31.4% of "
                     "samples (SE 0.5 points)")

# ---------------------------------------------------------------- section 4
lamA = C.A * C.lam0
chk("E4: lam_bar", lamA, ".4f", "0.0204")
chk("E4: lam_bar as a volatility", 100 * sqrt(lamA), ".1f", "14.3")
chk("E4: |S - lam I|^2", C.A**2 * C.d20, ".3e", "1.885e-03", in_md=False)
chk("E4: noise estimate", C.A**2 * C.b20, ".2e", "6.12e-05", in_md=False)
has("E4: the two norms", "$\\lVert\\hat\\Sigma-\\bar\\lambda I\\rVert_F^2=1.885\\times10^{-3}$ and "
                         "$\\hat\\sigma^2_{\\hat\\Sigma}=6.12\\times10^{-5}$")
chk("E4: c_hat from the printed inputs", 1 - 6.12e-5 / 1.885e-3, ".4f", "0.9675")
chk("E4: c_hat", C.ch0, ".4f", "0.9675")
chk("E4: shrinkage_", 1 - C.ck0, ".4f", "0.0325")
assert abs(C.ch0 - C.ck0) < C.BOUND
has("E4: rounding bound", "equal to $1-\\hat c$ to rounding error (below $10^{-15}$)")
chk("E4: normal oracle", C.oracle_c(C.S_d, C.WINDOW), ".4f", "0.9851")
chk("E4: noise over normal value", C.b20 / C.normal_noise(C.S_d, C.WINDOW), ".2f", "2.14")
chk("E4: 0050 raw kurtosis", float(C.k0[i50]), ".1f", "13.3")
chk("E4: 00642U raw kurtosis", float(C.k0[i642]), ".1f", "4.5")
chk("E4: 0050 share", pct(C.share0[i50]), ".0f", "36")
chk("E4: 00642U share", pct(C.share0[i642]), ".0f", "39")
chk("E4: 00642U volatility", pct(C.sd_a[i642]), ".1f", "23.2")
# X4 and the case for the spectrum
x60 = C.X1[-60:]
ev60 = np.sort(np.linalg.eigvalsh(C.cov0(x60)))[::-1]
c60 = C.c_lw(x60)
chk("X4: kappa, 60 returns", ev60[0] / ev60[-1], ".0f", "438")
chk("X4: kappa_c, 60 returns", C.WIN[60]["kc"], ".1f", "68.1")
chk("X4: c_hat, 60 returns", c60, ".3f", "0.874")
chk("X4: kappa, first half", C.kappa(C.S1), ".2f", "126.05")
# X5, row by row
ROWS5 = {20: "| 20 | 0.790 | singular → 49.5 | — | 12.59 |"}
for T in (30, 60, 120, 250, 504, 2191):
    w = C.WIN[T]
    ROWS5[T] = (f"| {T:,} | {w['c']:.3f} | {w['kappa']:,.0f} → {w['kc']:.1f} | {w['pred']:.2f} / {w['real']:.2f} | "
                f"{w['shrunk_real']:.2f} |")
for T, row in ROWS5.items():
    has(f"X5: row T {T}", row)
    w = C.WIN[T]
    for key, d in (("c", 3), ("kc", 1), ("shrunk_real", 2), ("pred", 2), ("real", 2), ("kappa", 0)):
        if key in w:
            flag(f"X5: T {T} {key}", w[key], d)
            assert not tie(w[key], f".{d}f"), (T, key)
assert C.WIN[20]["rank"] == 19 and f"{C.WIN[20]['c']:.3f}" == "0.790" and f"{C.WIN[20]['kc']:.1f}" == "49.5"
chk("X5: T 20 shrunk realized", C.WIN[20]["shrunk_real"], ".2f", "12.59")
chk("X5/E5: pseudoinverse predicted", C.WIN[20]["pinv_pred"], ".2f", "1.78")
chk("X5/E5: pseudoinverse realized", C.WIN[20]["pinv_real"], ".2f", "17.03")
has("X5: note date", "(to 6 October 2017)")
assert C.s.dates[C.H - 1] == "2017-10-06"
chk("E5: kappa at 30", C.WIN[30]["kappa"], ",.0f", "116,097")
chk("E5: predicted at 30", C.WIN[30]["pred"], ".2f", "1.34")
chk("E5: realized at 30", C.WIN[30]["real"], ".2f", "43.12")
chk("E5: gross at 30", C.WIN[30]["gross"], ".2f", "13.48")
chk("E5: c_hat at 30", C.WIN[30]["c"], ".3f", "0.823")
chk("E5: shrunk realized at 30", C.WIN[30]["shrunk_real"], ".2f", "12.46")
chk("E5: share of 1 outside the column space", 100 * C.WIN[20]["outside"], ".0f", "18")
chk("E5: c_hat, first half", C.c1, ".4f", "0.9951")
chk("E5: kappa_c, first half", float(C.evc[-1] / C.evc[0]), ".2f", "121.38")
chk("E5: realized, first half", C.WIN[2191]["real"], ".2f", "11.78")
chk("E5: shrunk realized, first half", C.WIN[2191]["shrunk_real"], ".2f", "11.78")
assert C.n3 == 1000
has("E5: experiment 3 draws", "Experiment 3 draws 1,000 samples at each length")
e3 = C.EXP3
mcv("Exp3: sample at 60", *e3[60]["sample"], "15.51", "0.04")
mcv("Exp3: shrunk at 60", *e3[60]["shrunk"], "13.46", "0.02")
mcv("Exp3: sample at 2,191", *e3[2191]["sample"], "11.4659", "0.0006")
mcv("Exp3: shrunk at 2,191", *e3[2191]["shrunk"], "11.4651", "0.0006")
chk("Exp3: true minimum", pct(C.vol(C.w_true, C.S1, C.AU)), ".2f", "11.40")
mcv("Exp3: mean c_hat at 20", *e3[20]["c"], "0.810", "0.002")
mcv("Exp3: mean c_hat at 2,191", *e3[2191]["c"], "0.997963", "0.000002")
has("S4: N/T", "Here $N/T$ runs from 5/504 on E5 to 28/20 on U28.")
cs = C.cs
sig_dates = [d for d, _, _ in C.sch]
chk("X6: first c_hat", float(cs[0]), ".3f", "0.968")
chk("X6: median c_hat", C.q50(cs), ".3f", "0.962")
chk("X6: highest c_hat", float(cs.max()), ".3f", "0.979")
chk("X6: lowest c_hat", float(cs.min()), ".3f", "0.781")
assert sig_dates[int(np.argmax(cs))] == "2024-04-30" and sig_dates[int(np.argmin(cs))] == "2026-03-31"
chk("X6: below 0.9", C.n_low, "d", "19")
assert sig_dates[int(np.argmax(cs < 0.9))] == "2020-03-31"
has("X6: note", "First 0.968, median 0.962, highest 0.979 (2024-04-30), lowest 0.781 (2026-03-31); 19 signals lie "
                "below 0.9, the first on 2020-03-31.")
print(f"X6: smallest margin to the 0.9 threshold {float(np.abs(cs - 0.9).min()):.1e}")
chk("E6: largest weight gap", pct(C.d35.max()), ".1f", "13.1")
assert C.sigs[C.jm].signal == "2026-03-31"
chk("E6: R3's 00679B weight", pct(C.sigs[C.jm].targets["R3"][i679]), ".1f", "55.1")
chk("E6: R5's 00679B weight", pct(C.sigs[C.jm].targets["R5"][i679]), ".1f", "42.0")
chk("E6: median gap", pct(C.q50(C.d35)), ".1f", "1.6")
chk("E6: 00642U kurtosis, 2026-03-31 window", float(C.km[i642]), ".1f", "48.9")
chk("E6: 00642U share there", pct(C.share_m[i642]), ".0f", "84")
chk("E6: noise over normal there", C.bm / C.normal_noise(C.cov0(C.xm), C.WINDOW), ".1f", "13.1")
chk("E6: c_hat with the normal value", C.c_norm_m, ".3f", "0.983")
chk("E6: average variance as a volatility", 100 * sqrt(float(np.mean(C.sdm**2))), ".1f", "26.5")
chk("E6: bond fund's volatility", pct(C.sdm[i679]), ".1f", "13.4")
chk("E6: 00642U's volatility", pct(C.sdm[i642]), ".1f", "43.0")
has("E6: realized", "Out of sample R5 realized 9.97% and R3 9.96%.")
chk("pitfall: TR23 t fit's degrees of freedom (lm15.md:349)", 3.065, ".3f", "3.065")
# the widget's text and its data block (written by data/lm30_charts.py)
WJ = json.loads((DATA / "lm30-shrinkPath.json").read_text(encoding="utf-8"))["widget"]
S2w = np.array(WJ["S2"])


def widget_solve(win: dict, c: float) -> tuple[np.ndarray, float]:
    lam = np.array(win["lam"])
    Q = np.array(win["q"]).T
    d = c * lam + (1 - c) * lam.mean()
    x = Q @ ((Q.T @ np.ones(len(lam))) / d)
    return x / x.sum(), float(d[0] / d[-1])


w60 = WJ["windows"][int(WJ["init"]["win"])]
assert w60["T"] == 60 and w60["chat"] == C.WIN[60]["c"]
wi, ki = widget_solve(w60, w60["chat"])
chk("widget: c_hat", w60["chat"], ".3f", "0.874")
chk("widget: kappa_c", ki, ".1f", "68.1")
chk("widget: realized", 100 * sqrt(float(wi @ S2w @ wi)), ".2f", "12.04")
w0, _ = widget_solve(w60, 0.0)
chk("widget: 1/N realized at c = 0", 100 * sqrt(float(w0 @ S2w @ w0)), ".2f", "15.51")
chk("KC4: eigenvalue 1 + rho", 1.9, ".1f", "1.9")
chk("KC4: shrunk eigenvalue", 0.5 * 1.9 + 0.5, ".2f", "1.45")
chk("KC4: shrunk eigenvalue", 0.5 * 0.1 + 0.5, ".2f", "0.55")
chk("KC4: kappa", 1.9 / 0.1, ".0f", "19")
chk("KC4: kappa_c", 1.45 / 0.55, ".2f", "2.64")

# ---------------------------------------------------------------- section 5
chk("E7: smallest eigenvalue of S1", C.AU * float(C.ev1[0]), ".4f", "0.0058")
chk("E7: sectors held", int(C.act.sum()), "d", "9")
chk("E7: constraints binding", int((~C.act).sum()), "d", "19")
chk("E7: smallest eigenvalue of S_nu", C.AU * float(np.linalg.eigvalsh(C.S_nu)[0]), ".4f", "0.0059")
chk("E7: largest variance reduction", pct(C.red.max()), ".1f", "20.7")
assert C.s.names[int(np.argmax(C.red))] == "Optoelectronic"
has("E7: rounding bound", "equal the long-only weights to rounding error (below $10^{-15}$)")
gap23 = float(np.abs(C.nu_cv - C.nu).max() / C.nu.max())
chk("E7: cvxpy multipliers", gap23, ".1e", "3.7e-10", in_md=False)
has("E7: cvxpy", "to $3.7\\times10^{-10}$ of the largest $\\nu_i$")
assert C.prob.status == "optimal"
chk("E7: long-only realized", pct(C.vol(C.w_lo, C.S2, C.AU)), ".2f", "12.14")
chk("E7: sample realized", pct(C.vol(C.w_s, C.S2, C.AU)), ".2f", "11.78")
mcv("S5: long-only minus shrunk at 30", -e3[30]["diff"][0], e3[30]["diff"][1], "0.38", "0.03")
mcv("S5: long-only minus shrunk at 60", -e3[60]["diff"][0], e3[60]["diff"][1], "0.06", "0.02")
mcv("S5: long-only minus shrunk at 120", e3[120]["diff"][0], e3[120]["diff"][1], "0.49", "0.01")
mcv("S5: long-only minus shrunk at 2,191", e3[2191]["diff"][0], e3[2191]["diff"][1], "1.2981", "0.0005")
assert e3[30]["diff"][0] < 0 and e3[60]["diff"][0] < 0 and e3[120]["diff"][0] > 0
assert all(e3[T]["diff"][0] > 0 for T in (120, 250, 504, 2191))       # "raises it from 120 returns on"
chk("S5: R3 zero weights (A29-09)", C.z3, "d", "0")
has("S5: 92 signals", "at none of the 92 signals")

# ---------------------------------------------------------------- section 6
assert [C.R2[k] for k in F5] == [0.40, 0.20, 0.30, 0.10, 0.0]
has("S6: R2", "40% 0050, 20% 00646, 30% 00679B and 10% 00635U")
has("S6: Idzorek", "Idzorek (2007) reports values near 0, from 0.01 to 0.05, 1, and about one over the number of "
                   "observations")
chk("E8: R2 mean excess", pct(C.mex), ".3f", "4.383")
chk("E8: R2 volatility", 100 * sqrt(C.vref), ".3f", "6.709")
chk("E8: delta from the printed inputs", 0.04383 / 0.06709**2, ".2f", "9.74")
chk("E8: delta", C.dl, ".2f", "9.74")
vals("E8: implied returns", [pct(v) for v in C.e_eq[:4]], ".2f", "7.79, 5.14, 0.46, 1.02")
chk("E8: implied 00642U", pct(C.e_eq[i642]), ".2f", "3.71")
chk("E8: b", pct(C.b), ".3f", "2.491")
chk("E8: K e_eq", pct(C.kq), ".3f", "-2.649")
chk("E8: sqrt(K S K')", 100 * sqrt(C.KSK), ".3f", "12.264")
chk("E8: b - K e_eq from the printed inputs", 0.02491 + 0.02649, ".5f", "0.05140")
move_p = 0.5 * 0.05140 / (9.74 * 0.12264**2)
chk("E8: the move from the printed inputs", move_p, ".3f", "0.175")
move = 0.5 * (C.b - C.kq) / (C.dl * C.KSK)
chk("E8: the move in points", 100 * move, ".1f", "17.5")
chk("E8: the move in points, printed inputs", 100 * move_p, ".1f", "17.5")
fbl = {c: C.wref + C.K * c * (C.b - C.kq) / (C.dl * C.KSK) for c in (0.5, 1.0)}
has("E8: c = 0.5", "22.5 / 37.5 / 30 / 10 / 0%")
vals("E8: c = 0.5", [pct(v) for v in fbl[0.5][:2]], ".1f", "22.5, 37.5")
has("E8: c = 1", "4.9 / 55.1 / 30 / 10 / 0%")
vals("E8: c = 1", [pct(v) for v in fbl[1.0][:2]], ".1f", "4.9, 55.1")
chk("E8: c = 0.5 from the printed move", 40 - 17.544, ".1f", "22.5", in_md=False)
has("E8: plug-in", "13.6 / 72.4 / 43.8 / 3.0 / −17.1%")
vals("E8: plug-in", [pct(v) for v in C.fp], ".1f", "13.6, 72.4, 43.8, 3.0, -17.1")
chk("E8: plug-in total", pct(C.fp.sum()), ".1f", "115.8")
chk("E8: n0", C.WINDOW, "d", "504")
chk("KC6: 0050 from the printed inputs", 0.5 * 13.6 + 0.5 * 40, ".1f", "26.8")
chk("KC6: 0050", pct(C.f_all[i50]), ".1f", "26.8")
assert abs(pct(C.f_all[i50]) - (0.5 * pct(C.fp[i50]) + 20)) < 1e-12

# ---------------------------------------------------------------- section 7
assert C.B4 == 1000
chk("Exp4: fallback count", C.fallback, "d", "12")
mw, sw = 100 * C.mw, 100 * C.sw
mcv("Exp4: smallest mean weight", float(mw.min()), float(sw[int(np.argmin(mw))]), "3.8", "0.4")
mcv("Exp4: largest mean weight", float(mw.max()), float(sw[int(np.argmax(mw))]), "35.2", "0.9")
assert int(np.argmin(mw)) == i642 and int(np.argmax(mw)) == i646 and (C.Wb.min(axis=0) >= 0).all()
pz, sz = 100 * C.pz, 100 * C.sz
mcv("Exp4: smallest exclusion share", float(pz.min()), float(sz[int(np.argmin(pz))]), "18", "1")
mcv("Exp4: largest exclusion share", float(pz.max()), float(sz[int(np.argmax(pz))]), "72", "1")
assert int(np.argmin(pz)) == i646 and int(np.argmax(pz)) == i642
assert sorted({f"{v:.0e}" for v in sz}) == ["1e+00", "2e+00"]          # "SEs 1 to 2 points"
has("Exp4: shares", "each fund is excluded in 18% (00646) to 72% (00642U) of the resamples, SEs 1 to 2 points")
chk("S7: single-index parameters", 2 * C.NU + 1, "d", "57")
chk("S7: sample parameters", C.NU * (C.NU + 1) // 2, "d", "406")
H5 = {"Sample": (C.w_s, C.S1), "Shrunk (Ledoit–Wolf)": (C.w_c, C.Sc1), "Long-only": (C.w_lo, C.S1),
      "Single index": (C.w_f, C.SF), "1/N": (C.wN, C.S1)}
for name, (w, M) in H5.items():
    p, r = pct(C.vol(w, M, C.AU)), pct(C.vol(w, C.S2, C.AU))
    has(f"X8: {name}", f"| {name} | {p:.2f} | {r:.2f} |")
    flag(f"X8: {name} predicted", p, 2)
best = float(C.grid_c[int(np.argmin(C.rv))])
has("X8: hindsight", f"| Best $c$ in hindsight, {best:.2f} | | {100 * float(C.rv.min()):.2f} |")
chk("S7: single index realized", pct(C.vol(C.w_f, C.S2, C.AU)), ".2f", "12.67")
has("E9: entries", "has entries 0.982, 0.199 and −0.444 and $\\det C_{\\text{pw}}=-0.374592$")
chk("E9: det", float(np.linalg.det(C.Cp)), ".6f", "-0.374592")
vals("E9: eigenvalues", [float(v) for v in C.evp[::-1]], ".4f", "2.0149, 1.1471, -0.1621")
chk("E9: c_max", C.cmax, ".4f", "0.8605")


def offd(M: np.ndarray) -> list[float]:
    return [float(M[0, 1]), float(M[0, 2]), float(M[1, 2])]


chk("E9: shrunk entries from the printed c", 0.982 * 0.8605, ".3f", "0.845")
vals("E9: shrunk entries", offd(C.Csh)[:2], ".3f", "0.845, 0.171")
chk("E9: shrunk entry 3", offd(C.Csh)[2], ".3f", "-0.382")
vals("E9: clipped", offd(C.Ccl)[:2], ".3f", "0.852, 0.154")
chk("E9: clipped 3", offd(C.Ccl)[2], ".3f", "-0.385")
vals("E9: nearest", offd(C.Y)[:2], ".3f", "0.864, 0.139")
chk("E9: nearest 3", offd(C.Y)[2], ".3f", "-0.379")
has("E9: second solver", "agrees to $1.4\\times10^{-7}$")
chk("E9: second solver gap", C.gap_ncm, ".1e", "1.4e-07", in_md=False)
fro = [float(np.sqrt(C.fro2(M - C.Cp))) for M in (C.Csh, C.Ccl, C.Y)]
vals("E9: distances", fro[:2], ".3f", "0.216, 0.211")
chk("E9: distance 3", fro[2], ".3f", "0.209")
assert float(np.linalg.eigvalsh(C.Y)[0]) > -1e-12                    # "PSD to rounding"
chk("KC7: lambda_3", float(C.evp[0]), ".3f", "-0.162")
chk("KC7: 1 - lambda_3 from the printed value", 1 + 0.162, ".3f", "1.162")
chk("KC7: c_max from the printed value", 1 / 1.162, ".3f", "0.861")
chk("KC7: c_max", C.cmax, ".3f", "0.861")

# ---------------------------------------------------------------- section 8
has("S8: code A", "A = 242.951422")
chk("S8: code A", C.A, ".6f", "242.951422")
has("S8: code comment", "c_hat = 1 - lw.shrinkage_                       # 0.9675")
chk("KC8: c_hat from the printed shrinkage_", 1 - 0.0325, ".4f", "0.9675")
has("lab box: standard wording", "The notebook reads FinMind files that you download once with your own token. From "
    "the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. "
    "FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.")

# ---------------------------------------------------------------- problems and solutions (A30-30 .. A30-38)
chk("P1: sigma/sqrt(years)", 20 / sqrt(4), ".1f", "10.0")
chk("P1: sigma/years", 20 / 4, ".1f", "5.0")
chk("P1: sigma/sqrt(T)", 20 / sqrt(972), ".2f", "0.64")
chk("P1: T", 4 * 243, "d", "972")
p2 = (0.8 * 4 + 0.2 * 2.5, 0.8 * 1 + 0.2 * 2.5)
chk("P2: shrunk eigenvalue 1", p2[0], ".2f", "3.70")
chk("P2: shrunk eigenvalue 2", p2[1], ".2f", "1.30")
chk("P2: kappa_c", p2[0] / p2[1], ".2f", "2.85")
chk("P2: distractor B", 4.0, ".2f", "4.00")
chk("P2: distractor C", 0.8 * 4, ".2f", "3.20")
chk("P3: T/(T + N)", 250 / 260, ".2f", "0.96")
chk("P4: n0", 3 * 504, ",d", "1,512")
chk("P2/S7: lam_bar of eigenvalues 4 and 1", (4 + 1) / 2, ".1f", "2.5")
chk("S7: distance of each eigenvalue from lam_bar", 4 - 2.5, ".1f", "1.5")
chk("S8: 2 nu_2", 2 * 0.6, ".1f", "1.2")
chk("S8: 2 rho sigma_1 sigma_2 (%^2)", 2 * 0.8 * 1 * 2, ".1f", "3.2")
has("E8: printed inputs of delta", "$\\delta=0.04383/0.06709^2=9.74$")
has("S4: working paper's theorems", "Theorems 3.2 and 3.4 of their 2001 working paper")
chk("P4: c", 504 / (504 + 1512), ".2f", "0.25")
chk("P4: posterior", 0.25 * 4, ".1f", "1.0")
chk("P4: swapped", 0.75 * 4, ".1f", "3.0")
chk("P4: equal", 0.5 * 4, ".1f", "2.0")
chk("P5: VIF", 1 / (1 - 0.81), ".3f", "5.263")
chk("P5: (S^-1)_11", 1 / (0.04 * 0.19), ".1f", "131.6")
chk("P5: from the printed VIF", 5.263 / 0.04, ".1f", "131.6")
chk("P5: ignores rho", 1 / 0.04, ".1f", "25.0")
chk("P5: 1 - rho", 1 / (0.04 * 0.1), ".1f", "250.0")
chk("P6: 2 nu_3", 2 * 0.0002, ".4f", "0.0004")
d7 = 1.5**2 + 1.5**2
n7 = (16 + 1 + 25) / 100
chk("S7: distance", d7, ".1f", "4.5")
chk("S7: noise", n7, ".2f", "0.42")
chk("S7: c*", d7 / (d7 + n7), ".4f", "0.9146")
chk("S7: denominator", d7 + n7, ".2f", "4.92")
assert abs(C.normal_noise(np.diag([4.0, 1.0]), 100) - n7) < 1e-15
w8 = (4 - 1.6) / (1 + 4 - 3.2)
chk("S8: unconstrained weight", 100 * w8, ".1f", "133.3")
chk("S8: short weight", 100 * (1 - w8), ".1f", "-33.3")
chk("S8: nu_2", 1.6 - 1, ".1f", "0.6")
chk("S8: S_nu (2,2)", 4 - 1.2, ".1f", "2.8")
chk("S8: S_nu weights", 100 * (2.8 - 1) / (1 + 2.8 - 2), ".0f", "100")
eq9 = (4 * 0.04 * 0.5, 4 * 0.01 * 0.5)
chk("S9: e_eq 1", 100 * eq9[0], ".0f", "8")
chk("S9: e_eq 2", 100 * eq9[1], ".0f", "2")
chk("S9: K S K'", 0.04 + 0.01, ".2f", "0.05")
chk("S9: factor", 0.5 * 0.06 / 0.05, ".1f", "0.6")
chk("S9: e_BL 1", 100 * (0.08 - 0.6 * 0.04), ".1f", "5.6")
chk("S9: e_BL 2", 100 * (0.02 + 0.6 * 0.01), ".1f", "2.6")
chk("S9: f_BL 1", 100 * (0.5 - 0.6 / 4), ".0f", "35")
chk("S9: f_BL 2", 100 * (0.5 + 0.6 / 4), ".0f", "65")
chk("S12: T/N at 30", 30 / 28, ".1f", "1.1")
chk("S12: T/N at 2,191", 2191 / 28, ".0f", "78")
has("S12: check", "The check of (30.4) finds 19 binding constraints and weights that agree to $10^{-15}$.")

# ---------------------------------------------------------------- the chart files' cited values
J = {n: json.loads((DATA / f"lm30-{n}.json").read_text(encoding="utf-8"))
     for n in ("scatter", "years", "spectrum", "chat", "bl", "shrinkPath")}
assert [f"{v:.3f}" for v in J["years"]["series"][0]["y"]] == ["0.230", "0.322", "0.422", "0.546", "0.672", "0.759",
                                                              "0.816"]
assert f"{J['years']['series'][1]['y'][0]:.4f}" == "0.8660"
assert f"{min(J['chat']['series'][0]['y']):.3f}" == "0.781" and f"{max(J['chat']['series'][0]['y']):.3f}" == "0.979"
assert [f"{100 * v:.1f}" for v in J["bl"]["series"][3]["values"]] == ["13.6", "72.4", "43.8", "3.0", "-17.1"]
sp = J["spectrum"]["series"]
assert f"{sp[0]['y'][0] / sp[0]['y'][-1]:.0f}" == "438" and f"{sp[2]['y'][0] / sp[2]['y'][-1]:.2f}" == "126.05"
assert J["scatter"]["points"][0]["label"] == "truth (62.6, 37.8)" and len(J["scatter"]["series"][0]["x"]) == 1000
for n, spec in J.items():
    assert len(json.dumps(spec, separators=(",", ":")).encode("utf-8")) < 300_000, n
print("chart files: the values the text cites are plotted")

# ====================================================================== structure: labels, citations, tags
ex_labels = re.findall(r"\[!exhibit\][^\n]*\{#([\w-]+)\}", RAW)
eg_labels = re.findall(r"\[!example\][^\n]*\{#([\w-]+)\}", RAW)
assert ex_labels == ["case", "scatter", "years", "spectrum", "windows", "chat", "bl", "halves"], ex_labels
assert eg_labels == ["split", "means", "critical", "lwhand", "shortT", "r5", "jm", "blview", "repair"], eg_labels
assert len(set(ex_labels) | set(eg_labels)) == len(ex_labels) + len(eg_labels), "a label is used twice"
for lab in ex_labels:
    assert f"[[ex:{lab}]]" in RAW, f"exhibit {lab} is never cited"
for kind, lab in re.findall(r"\[\[(ex|eg):([\w-]+)\]\]", RAW):
    assert lab in (ex_labels if kind == "ex" else eg_labels), (kind, lab)
tags = re.findall(r"\\tag\{(30\.\d+)\}", RAW)
assert tags == [f"30.{k}" for k in range(1, 6)], tags
for name in re.findall(r'data-chart="(lm30-[\w-]+)"', RAW):
    assert (DATA / f"{name}.json").exists(), name
for word in ("Model", "In-sample", "Out-of-sample", "Constructed"):
    assert f"*{word}*" in RAW, word
print(f"labels: {len(ex_labels)} exhibits, {len(eg_labels)} examples, tags (30.1)-(30.5), every exhibit cited")

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
if FAILS:
    print(f"\n{len(FAILS)} of {N_CHECKS} checks FAILED:")
    for m in FAILS:
        print("   ", m)
    sys.exit(1)
print(f"\nall {N_CHECKS} checks passed")
sys.exit(0)
