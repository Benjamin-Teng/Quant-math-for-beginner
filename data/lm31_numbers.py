"""Every number that LM31 (Risk Parity, HRP and Volatility Targeting) prints, computed and checked against src/lm31.md.

Run:  uv run python data/lm31_numbers.py
      (after data/vol5_series.py, data/vol5_rules.py and data/vol2_series.py; and after data/lm31_charts.py, whose
      widget data this script checks)

Inputs and conventions: data/lm31_common.py, which keeps the code of data/vol5_anchors_lm31.py (the Stage 1 anchor
script): E5 through vol5_series.frames("E5"), the through case through vol5_rules (no rule is re-implemented here),
U28 through lm10_series.u28(). The module text is src/lm31.md; plans/vol-5-anchors.md, "LM31", holds the Stage 1
anchors A31-01 .. A31-46.

Part 1 compares each anchor line, as data/lm31_common.py recomputes it, with the anchor table's Value column: a
difference is reported, never forced.

Part 2 checks the text (each check stops the script on a failure):
  chk(label, value, fmt, printed)  format(value, fmt) equals the printed string, the value is not a rounding tie of
                                   that format, and the printed string is in the module as a whole number. Hand
                                   computations are redone from the printed, rounded inputs (PITFALLS section 7).
  sci(label, value, printed)       a number printed as m\\times10^{e}, compared at the printed mantissa.
  has(label, text)                 a literal string (a date, a phrase, a table row) is in the module.
At the end the script lists the numbers of the module that no check covered and prints "all N checks passed".
"""
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lm31_common as K
import numpy as np
from vol5_rules import R2, cov0

ROOT = HERE.parent
MD = ROOT / "src" / "lm31.md"
ANCHORS = ROOT / "plans" / "vol-5-anchors.md"
WIDGET = ROOT / "src" / "data" / "lm31-ercthree.json"
RAW = MD.read_text(encoding="utf-8")


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
    assert not in_md or in_text(printed), f"{label}: {printed!r} not found in src/lm31.md"
    COVERED.add(printed.lstrip("-"))
    N_CHECKS += 1


def pct(label: str, frac: float, d: int, printed: str, in_md: bool = True) -> None:
    chk(label, 100 * frac, f".{d}f", printed, in_md)


def chks(label: str, values: list[float] | np.ndarray, fmt: str, printed: list[str]) -> None:
    for k, (v, p) in enumerate(zip(values, printed, strict=True)):
        chk(f"{label} [{k + 1}]", float(v), fmt, p)


def has(label: str, text: str) -> None:
    global N_CHECKS
    assert text in TEXT or text in RAW, f"{label}: {text!r} not found in src/lm31.md"
    print(f"CHECK {label}: '{text[:80]}' in text")
    for num in re.findall(r"\d[\d,]*\.?\d*", text):
        COVERED.add(num.rstrip(".,"))
    N_CHECKS += 1


def sci(label: str, value: float, printed: str) -> None:
    """printed is the TeX in the module, m\\times10^{e}; the value must round to m at m's digits."""
    global N_CHECKS
    m = re.fullmatch(r"([\d.]+)\\times10\^\{(-?\d+)\}", printed)
    assert m, printed
    mant, ex = m.group(1), int(m.group(2))
    digits = len(mant.split(".")[1]) if "." in mant else 0
    got = f"{value / 10**ex:.{digits}f}"
    assert got == mant, (label, got, printed)
    assert printed in RAW, f"{label}: {printed!r} not found in src/lm31.md"
    print(f"CHECK {label}: {value:.3e} (printed {printed})")
    COVERED.add(mant)
    N_CHECKS += 1


def iso(d: str) -> str:
    """2019-02-27 -> '27 February 2019' as the module prints a date."""
    y, mo, dd = d.split("-")
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
              "November", "December"]
    return f"{int(dd)} {months[int(mo) - 1]} {y}"


# ====================================================================== part 1: the anchors
def _anchor_values() -> dict[str, str]:
    rows: dict[str, str] = {}
    sec = ANCHORS.read_text(encoding="utf-8").split("\n## LM31", 1)[1].split("\n## ", 1)[0]
    for line in sec.splitlines():
        if line.startswith("| A31-"):
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
            rows[cells[0]] = cells[3].strip("`").replace("\\|", "|")
    return rows


ANCHOR_ROWS = _anchor_values()
assert len(ANCHOR_ROWS) == 46, len(ANCHOR_ROWS)
for line in K.OUT:
    aid, got = line.split(" ", 1)
    ok = got == ANCHOR_ROWS[aid]
    print(f"ANCHOR {aid}: {'ok' if ok else 'DIFFERS'}")
    if not ok:
        ANCHOR_DIFFS.append(f"{aid}:\n      script {got}\n      anchor {ANCHOR_ROWS[aid]}")

# ====================================================================== part 2: the text
fr, sigs, sch = K.fr, K.sigs, K.sch
A, Aw = K.A, K.Aw
S0 = K.S0
J = K.J
shares, vol = K.shares, K.vol

# ---------------------------------------------------------------- data role (notation note, case note)
chk("T", len(K.est), ",d", "2,362")
has("estimation frame dates", "from 18 January 2017 to 8 October 2026")
assert (K.est[0], K.est[-1]) == ("2017-01-18", "2026-10-08")
chk("A", A, ".2f", "242.95")
chk("wealth sessions", len(fr.wealth_dates), ",d", "2,368")
chk("A_w", Aw, ".2f", "243.57")
chk("years", fr.years, ".4f", "9.7221")
chk("U28 T", len(K.u.X), ",d", "4,382")
chk("U28 A", K.u.A, ".2f", "245.48")
assert K.WINDOW == 504 and len(sch) == 92 and in_text("504") and in_text("92")
s0, t0, r0 = sch[0]
assert (s0, t0, K.est[r0 - K.WINDOW], K.est[r0 - 1]) == ("2019-02-27", "2019-03-04", "2017-02-13", "2019-02-27")
has("first window", "13 February 2017 to 27 February 2019")
assert (sch[-1][0], sch[-1][1]) == ("2026-09-30", "2026-10-01")
has("last signal", "30 September 2026")
mlen = K.mlen
assert (len(mlen), min(mlen), max(mlen)) == (91, 12, 23) and len(K.p8.dates) - 1 - K.idx[-1] == 5
has("holding months", "12 to 23 sessions; the 91 complete ones leave out the last 5 sessions")
chk("out-of-sample sessions", len(K.p8.dates) - 1, ",d", "1,851")
assert K.p8.dates[1] == "2019-03-05"
has("out of sample from", "Over the 1,851 sessions from 5 March 2019")

# ---------------------------------------------------------------- the case and its exhibit (April 2025)
k25 = K.k25
assert sigs[k25].signal == "2025-03-31" and sigs[k25].trade == "2025-04-01" and sigs[k25 + 1].trade == "2025-05-02"
w25 = K.w25
for f_, p_ in zip(K.funds, ["13.5", "21.6", "30.7", "22.2", "12.0"], strict=True):
    pct(f"X1 R6 weight {f_}", float(w25[J[f_]]), 1, p_)
assert f"{sum(float(f'{100 * x:.1f}') for x in w25):.1f}" == "100.0"
has("X1 weights row", "| 13.5, 21.6, 30.7, 22.2, 12.0% |")
sb25_ann = math.sqrt(A) * K.sb[k25]
sf25_ann = math.sqrt(A) * K.sf[k25]
pct("case: window volatility", sb25_ann, 2, "7.84")
pct("case: EWMA forecast", sf25_ann, 2, "5.89")
chk("case: L", float(K.L[k25]), ".2f", "1.33")
chk("case: borrowed", float(K.L[k25]) - 1, ".2f", "0.33")
# the EWMA continued daily on R6's constant-weight returns (as A31-32)
s2 = K.ewma(K.p25, K.sb25)
cont: dict[str, float] = {}
j = K.rw25
while K.est[j] <= "2025-04-09":
    s2 = K.LAM * s2 + (1 - K.LAM) * float(fr.X[j] @ w25) ** 2
    cont[K.est[j]] = s2
    j += 1
pct("2 April EWMA", math.sqrt(A * cont["2025-04-02"]), 2, "6.34")
pct("7 April EWMA", math.sqrt(A * cont["2025-04-07"]), 2, "23.58")
chk("7 April implied exposure", min(K.CAP, math.sqrt(K.sb25 / cont["2025-04-07"])), ".2f", "0.33")
chk("next trade L (X1)", float(K.L[k25 + 1]), ".2f", "0.45")
chk("next trade L (E9)", float(K.L[k25 + 1]), ".3f", "0.452")
m25 = K.trades.index("2025-04-01")
pct("R8 realized, annualized with A", math.sqrt(A * K.vmon["R8"][m25]), 1, "45.3")
chk("R8 ratio April 2025", float(K.ratio["R8"][m25]), ".2f", "5.78")
assert int(np.argmax(K.ratio["R8"])) == m25, "5.78 is the largest of the 91"
chk("ratio from the printed figures", 45.3 / 7.84, ".2f", "5.78")
chk("R6 ratio April 2025", float(K.ratio["R6"][m25]), ".2f", "4.25")
q6, q8 = K.ratio["R6"], K.ratio["R8"]
med6 = float(np.quantile(q6, 0.5, method="inverted_cdf"))
med8 = float(np.quantile(q8, 0.5, method="inverted_cdf"))
chk("median ratio R6", med6, ".2f", "0.83")
chk("median ratio R8", med8, ".2f", "0.98")
has("case dates", "On 31 March 2025 rule R6")
has("case: Qingming", "On 7 April, the first session after the Qingming holiday")
has("case: 2 May", "it kept its leverage until 2 May")
assert K.p8.dates[K.idx[m25] + 1] == "2025-04-02" and K.p8.dates[K.idx[m25 + 1]] == "2025-05-02"
has("X1 holding month", "| 2 April → 2 May | R8's realized volatility | 45.3% |")
chk("financing rate", 100 * (K.RF + K.SPREAD), ".1f", "3.5")
chk("cash rate", 100 * K.RF, ".1f", "1.5")

# ---------------------------------------------------------------- Section 2
pct("R1's 00642U share (LM27's A27-21)", float(shares(K.w1, S0)[J["00642U"]]), 1, "50.2")
v0 = K.v0
vol2 = [f"{100 * x:.2f}" for x in v0]
assert vol2 == ["13.50", "11.87", "8.54", "9.39", "23.17"], vol2
for f_, p_ in zip(K.funds, vol2, strict=True):
    pct(f"first-window volatility {f_} (LM28's A28-06)", float(v0[J[f_]]), 2, p_)
chk("rho 0050-00679B (A28-07)", float(K.C0[0, 2]), ".2f", "-0.30")
chk("rho 00646-00679B", float(K.C0[1, 2]), ".2f", "-0.26")
chk("rho 0050-00646", float(K.C0[0, 1]), ".2f", "0.54")
# E1 by hand from the printed volatilities
chk("E1 w1 from printed", 8.54 / (13.50 + 8.54), ".4f", "0.3875")
chk("E1 w1", float(K.w_two[0]), ".4f", "0.3875")
chk("E1 w2", float(K.w_two[1]), ".4f", "0.6125")
has("E1 printed", "$w_1=8.54/(13.50+8.54)=0.3875$")
chk("E1 MV weight", float(K.mv_two[0]), ".3f", "0.331")
pct("E1 MV vol", vol(K.mv_two, K.S2), 1, "6.1")
pct("E1 ERC vol", vol(K.w_two, K.S2), 1, "6.2")
assert np.abs(shares(K.w_two, K.S2) - 0.5).max() < 1e-12
# E2
iv_printed = 1 / np.array([13.50, 11.87, 8.54, 9.39, 23.17])
iv_printed /= iv_printed.sum()
for k, p_ in enumerate(["0.174", "0.198", "0.275", "0.251", "0.102"]):
    chk(f"E2 IV weight {k + 1} from printed vols", float(iv_printed[k]), ".3f", p_)
    chk(f"E2 IV weight {k + 1}", float(K.iv0[k]), ".3f", p_)
sh_iv = shares(K.iv0, S0)
for k, p_ in enumerate(["23.8", "23.0", "9.8", "18.7", "24.8"]):
    pct(f"IV share {k + 1}", float(sh_iv[k]), 1, p_)
assert f"{sum(float(f'{100 * x:.1f}') for x in sh_iv):.1f}" == "100.1"
has("X2 caption sums", "they sum to 100.1 and 99.9")
for k, p_ in enumerate(["0.1561", "0.1828", "0.3386", "0.2372", "0.0854"]):
    chk(f"R6 first weight {k + 1}", float(K.w6[k]), ".4f", p_)
assert f"{sum(float(f'{x:.4f}') for x in K.w6):.4f}" == "1.0001"
has("E2 sum", "(rounded separately; 1.0001 as printed)")
assert np.abs(shares(K.w6, S0) - 0.2).max() < 1e-12
pct("R3 vol (LM28's A28-10)", vol(K.w3, S0), 2, "5.02")
pct("R6 vol", vol(K.w6, S0), 2, "5.45")
pct("R1 vol (LM28's A28-15)", vol(K.w1, S0), 2, "7.38")
assert vol(K.w3, S0) <= vol(K.w6, S0) <= vol(K.w1, S0) and float(K.w3.min()) > 0
chk("rho bar", K.rbar, ".4f", "0.0533")
assert np.abs(K.w_eq - K.iv0).max() < 1e-15
sh7 = shares(K.w7, S0)
for k, p_ in enumerate(["13.0", "24.0", "26.3", "30.0", "6.6"]):
    pct(f"R7 share {k + 1}", float(sh7[k]), 1, p_)
assert f"{sum(float(f'{100 * x:.1f}') for x in sh7):.1f}" == "99.9"
pct("R6 00679B weight", float(K.w6[J["00679B"]]), 1, "33.9")
pct("R3 00679B weight", float(K.w3[J["00679B"]]), 1, "41.4")
pct("R3 00679B share", float(shares(K.w3, S0)[J["00679B"]]), 1, "41.4")
pct("00679B volatility, one decimal (KC)", float(v0[J["00679B"]]), 1, "8.5")

# ---------------------------------------------------------------- Section 3
chk("Newton steps", K.it_n, "d", "6")
chk("CCD sweeps", K.it_c, "d", "12")
sci("CCD gap to Newton", float(np.abs(K.w_c - K.w6).max()), "3.5\\times10^{-13}")
assert K.ERC_OPTS == {"tol_gap_abs": 1e-10, "tol_gap_rel": 1e-10, "tol_feas": 1e-10} and K.ERC_CHECK_TOL == 1e-5
gap6 = float(K.gap6)
sci("cvxpy against Newton over the 92 windows", gap6, "1.2\\times10^{-6}")
has("cvxpy tolerances", "`tol_gap_abs`, `tol_gap_rel` and `tol_feas` at $10^{-10}$")
has("check tolerance", "so it checks Newton to $10^{-5}$")
chk("Jacobi steps", K.it_j, "d", "220")
has("Jacobi point", "$(-1.307,-1.306,2.132,2.408,-0.927)$")
assert [f"{x:.3f}" for x in K.w_j] == ["-1.307", "-1.306", "2.132", "2.408", "-0.927"]
assert np.abs(shares(K.w_j, S0) - 0.2).max() < 1e-9 and int((K.w_j < 0).sum()) == 3
chk("Jacobi fails", int(K.fails), "d", "45")
has("Jacobi fails text", "At 45 of the 92 windows it does not settle in 10,000 steps")
assert np.abs(K.erc(S0 / A) - K.w6).max() < 1e-15
# E4
assert [R2[f] for f in ("0050", "00646", "00679B", "00635U", "00642U")] == [0.4, 0.2, 0.3, 0.1, 0.0]
has("E4 R2 mix", "R2 holds 40% 0050, 20% 00646, 30% 00679B, 10% 00635U and no 00642U")
for k, p_ in enumerate(["0.2466", "0.1773", "0.4190", "0.1571"]):
    chk(f"E4 weight {k + 1}", float(K.w_rb[k]), ".4f", p_)
chk("E4 sweeps", K.it_rb, "d", "12")
sci("E4 cvxpy gap", float(np.abs(K.w_cvx - K.w_rb).max()), "4.4\\times10^{-7}")
pct("E4 0050 weight", float(K.w_rb[0]), 1, "24.7")
pct("R2's 0050 share", float(shares(K.b4, K.S4)[0]), 1, "71.1")
pct("four-fund minimum variance", vol(K.w_mv4, K.S4), 3, "5.016")
pct("budget portfolio vol", vol(K.w_rb, K.S4), 3, "5.326")
pct("R2 vol (LM30's A30-24)", vol(K.b4, K.S4), 3, "6.709")
assert np.abs(shares(K.w_rb, K.S4) - K.b4).max() < 1e-10
# the widget's start (the widget computes its readouts itself; the text prints Jacobi's point)
has("widget: Jacobi", "$(-32.5,54.5,-20.9)$ (rounded separately; 1.1 as printed)")
assert [f"{x:.1f}" for x in K.jw] == ["-32.5", "54.5", "-20.9"] and K.jit > 0
assert f"{sum(float(f'{x:.1f}') for x in K.jw):.1f}" == "1.1"
WJ = json.loads(WIDGET.read_text(encoding="utf-8"))["widget"]
assert WJ["vols"] == [float(x) for x in K.vw] and WJ["b1"] == 1 / 3
assert WJ["corr"] == [float(K.Cw[0, 1]), float(K.Cw[0, 2]), float(K.Cw[1, 2])]
vw_ = np.array(WJ["vols"])
cw_ = np.array([[1, WJ["corr"][0], WJ["corr"][1]], [WJ["corr"][0], 1, WJ["corr"][2]],
                [WJ["corr"][1], WJ["corr"][2], 1]])
Swj = cw_ * np.outer(vw_, vw_)
ew_, itw_ = K.ccd(Swj, np.full(3, 1 / 3))
for k, p_ in enumerate(["0.3061", "0.5400", "0.1539"]):
    chk(f"widget ERC weight {k + 1} (A31-39)", float(ew_[k]), ".4f", p_, in_md=False)
chk("widget sweeps (A31-39)", itw_, "d", "9", in_md=False)
pct("widget ERC volatility (A31-39)", vol(ew_, Swj), 2, "6.55", in_md=False)
ivw_ = (1 / vw_) / float((1 / vw_).sum())
for k, p_ in enumerate(["34.1", "23.6", "42.3"]):
    pct(f"widget IV share {k + 1} (A31-39)", float(shares(ivw_, Swj)[k]), 1, p_, in_md=False)
for k, p_ in enumerate(["25.7", "2.8", "71.5"]):
    pct(f"widget 1/N share {k + 1} (A31-39)", float(shares(np.full(3, 1 / 3), Swj)[k]), 1, p_, in_md=False)
for k, p_ in enumerate(["13.5", "8.5", "23.2"]):          # the sliders' first positions (step 0.1)
    pct(f"widget volatility slider {k + 1}", float(vw_[k]), 1, p_, in_md=False)
for k, p_ in enumerate(["-0.30", "0.20", "-0.08"]):      # step 0.01
    chk(f"widget correlation slider {k + 1}", float(WJ["corr"][k]), ".2f", p_, in_md=False)
JS = (ROOT / "src" / "lm31.js").read_text(encoding="utf-8")
assert "step: 0.1," in JS and "step: 0.01," in JS and "if (gap < 1e-12)" in JS and "n <= 1000" in JS

# ---------------------------------------------------------------- Section 4: HRP
for k, p_ in enumerate(["0.480", "0.806", "0.794"]):
    chk(f"E5 d {k + 1}", float([K.d3[0, 1], K.d3[0, 2], K.d3[1, 2]][k]), ".3f", p_)
dp = np.array([[0, 0.480, 0.806], [0.480, 0, 0.794], [0.806, 0.794, 0]])
colp = [float(np.linalg.norm(dp[:, a] - dp[:, b])) for a, b in ((0, 1), (0, 2), (1, 2))]
for k, p_ in enumerate(["0.679", "1.182", "1.169"]):
    chk(f"E5 column distance {k + 1} from the printed d", colp[k], ".3f", p_)
    chk(f"E5 column distance {k + 1}", float([K.dd3[0, 1], K.dd3[0, 2], K.dd3[1, 2]][k]), ".3f", p_)
chk("E5 first merge", float(K.Z3[0, 2]), ".3f", "0.679")
chk("E5 second merge", float(K.Z3[1, 2]), ".3f", "1.169")
assert [K.funds[K.three[i]] for i in K.o3] == ["00679B", "0050", "00646"]
has("E5 order", "the order is (00679B, 0050, 00646)")
(a1, b1_, va1, vb1), (a2, b2_, va2, vb2) = K.st3
chk("E5 variance 00679B", 1e4 * va1, ".2f", "72.96")
chk("E5 variance [0050, 00646]", 1e4 * vb1, ".2f", "121.95")
chk("E5 first share from printed", 121.95 / (72.96 + 121.95), ".4f", "0.6257")
chk("E5 first share", vb1 / (va1 + vb1), ".4f", "0.6257")
chk("E5 variance 0050", 1e4 * va2, ".2f", "182.29")
chk("E5 variance 00646", 1e4 * vb2, ".2f", "140.88")
chk("E5 0050's share of the pair", vb2 / (va2 + vb2), ".4f", "0.4359")
chk("E5 the pair's share", va1 / (va1 + vb1), ".4f", "0.3743")
chk("E5 0050 from printed", 0.4359 * 0.3743, ".4f", "0.1632")
chk("E5 00646 from printed", 0.5641 * 0.3743, ".4f", "0.2111")
for k, p_ in enumerate(["0.1632", "0.2111", "0.6257"]):
    chk(f"E5 weight {k + 1}", float(K.w3h[k]), ".4f", p_)
chk("E5 square of 13.50", 13.50**2, ".2f", "182.25")
chk("E5 square of 8.54", 8.54**2, ".2f", "72.93")
# E6
for k, p_ in enumerate(["0.6835", "0.8576", "0.8861", "0.9822"]):
    chk(f"E6 merge {k + 1}", float(K.Z5[k, 2]), ".4f", p_)
assert [(int(a), int(b)) for a, b, _, _ in K.Z5] == [(0, 1), (4, 5), (2, 3), (6, 7)]
assert [K.funds[i] for i in K.o5] == ["00642U", "0050", "00646", "00679B", "00635U"]
has("E6 order", "(00642U, 0050, 00646, 00679B, 00635U)")
la, ra, va, vb = K.st5[0]
assert [K.funds[i] for i in la] == ["00642U", "0050"]
chk("E6 first left share", vb / (va + vb), ".4f", "0.1516")
for k, p_ in enumerate(["0.1131", "0.2189", "0.3443", "0.2852", "0.0384"]):
    chk(f"R7 first weight {k + 1}", float(K.w7[k]), ".4f", p_)
assert f"{sum(float(f'{x:.4f}') for x in K.w7):.4f}" == "0.9999"
has("E6 sum", "(rounded separately; 0.9999 as printed)")
pct("R7 vol", vol(K.w7, S0), 2, "5.13")
# U28
chk("U28 pairs", len(K.off) // 2, "d", "378")
chk("U28 smallest correlation", float(K.off.min()), ".3f", "0.217")
chk("U28 largest correlation", float(K.off.max()), ".3f", "0.755")
assert K.first == ("ComputerPeripheralEquipment", "ElectronicPartsComponents")
has("U28 first merge", "joins ComputerPeripheralEquipment and ElectronicPartsComponents at 0.5012")
chk("U28 first merge height", float(K.Zu[0, 2]), ".4f", "0.5012")
chk("U28 root height", float(K.Zu[-1, 2]), ".4f", "0.7426")
pct("U28 HRP largest", float(K.wu_h.max()), 2, "12.87")
pct("U28 HRP smallest", float(K.wu_h.min()), 2, "1.29")
pct("U28 ERC largest", float(K.wu_e.max()), 2, "6.06")
pct("U28 ERC smallest", float(K.wu_e.min()), 2, "2.43")
assert K.nm[int(K.wu_h.argmax())] == K.nm[int(K.wu_e.argmax())] == "CommunicationsInternet"
assert K.nm[int(K.wu_h.argmin())] == K.nm[int(K.wu_e.argmin())] == "GlassCeramic"
has("U28 extremes", "from 12.87% (CommunicationsInternet) to 1.29% (GlassCeramic)")
for nm_, w_, p_ in (("1/N (lm10.md:36)", K.wu_1, "15.75"), ("IV", K.wu_iv, "15.28"), ("ERC", K.wu_e, "15.18"),
                    ("HRP", K.wu_h, "14.48")):
    pct(f"U28 in-sample vol {nm_}", math.sqrt(K.u.A) * vol(w_, K.Su), 2, p_)
order_names = [K.nm[i] for i in K.ou]
has("X3 order, first half", "The order, top to bottom: " + ", ".join(order_names[:14]) + ".")
has("X3 order, second half", "Then: " + ", ".join(order_names[14:]) + ".")
has("U28 sample", "daily price returns, 2 December 2008 to 8 October 2026, $T=4{,}382$")
assert (K.u.dates[0], K.u.dates[-1]) == ("2008-12-02", "2026-10-08")
has("U28 repairs (lm10.md:41)", "524 closes in this sample (on 38 dates) replaced by their 13:30:00 values")
assert "524 closes in this sample (on 38 dates)" in (ROOT / "src" / "lm10.md").read_text(encoding="utf-8")
assert K.same_obs and K.same_u and K.ok8 and K.diff_order == 17
has("pitfall: 17 of 92", "the leaf order differs at 17 of the 92 windows")
has("overview: 17 of 92", "changes the leaf order at 17 of 92 signals")
has("S12: 17 of 92", "changes the leaf order at 17 of the 92 signals")

# ---------------------------------------------------------------- Section 5
W6, W7 = K.W6, K.W7
pct("R6 00679B min", float(W6.min(0)[J["00679B"]]), 1, "29.7")
pct("R6 00679B max", float(W6.max(0)[J["00679B"]]), 1, "37.4")
pct("R7 00679B min", float(W7.min(0)[J["00679B"]]), 1, "21.7")
pct("R7 00679B max", float(W7.max(0)[J["00679B"]]), 1, "58.8")
n_post = len(K.est) - K.i_oos
chk("ex-post rows", n_post, ",d", "1,845")
assert K.est[K.i_oos] == "2019-03-05"
post = [f"{100 * x:.1f}" for x in K.sh_post]
assert post == ["20.5", "19.2", "19.2", "23.1", "18.0"], post
for k, p_ in enumerate(post):
    pct(f"ex-post share {k + 1}", float(K.sh_post[k]), 1, p_)
has("E7 ex-post shares", "carries 20.5, 19.2, 19.2, 23.1 and 18.0% of the risk")
pct("00635U q10", float(K.q10[J["00635U"]]), 1, "8.7")
pct("00635U q90", float(K.q90[J["00635U"]]), 1, "47.0")
pct("00679B q10", float(K.q10[J["00679B"]]), 1, "-0.9")
pct("00679B q90", float(K.q90[J["00679B"]]), 1, "41.1")
chk("holding months with a negative share", int((K.mon.min(1) < -K.EPS).sum()), "d", "29")
has("E7 count", "Some share is negative in 29 of the 91 holding months")
pct("overview: smallest ex-post share", float(K.sh_post.min()), 1, "18.0")
pct("overview: largest ex-post share", float(K.sh_post.max()), 1, "23.1")
# X5 rows, built from the values
mean7 = K.sh7.mean(0)
assert f"{sum(float(f'{100 * x:.1f}') for x in mean7):.1f}" == "100.1"
has("X5 share sum", "its means, rounded separately, sum to 100.1")
for f_ in K.funds:
    i = J[f_]

    def c(x: float) -> str:
        return f"{100 * x:.1f}".replace("-", "−")

    row = (f"| {f_} | {c(W6.mean(0)[i])} ({c(W6.min(0)[i])}–{c(W6.max(0)[i])}) | {c(W7.mean(0)[i])} "
           f"({c(W7.min(0)[i])}–{c(W7.max(0)[i])}) | {c(mean7[i])} | {c(K.sh_post[i])} | {c(K.q10[i])} to "
           f"{c(K.q90[i])} |")
    assert row in RAW, row
    print(f"CHECK X5 row {f_}: {row}")
    N_CHECKS += 1
    for x in (W6.mean(0)[i], W6.min(0)[i], W6.max(0)[i], W7.mean(0)[i], W7.min(0)[i], W7.max(0)[i], mean7[i],
              K.sh_post[i], K.q10[i], K.q90[i]):
        assert not tie(100 * float(x), ".1f")
        COVERED.add(f"{100 * float(x):.1f}".lstrip("-"))
vols_ = {k: float(K.summ[k]["vol"]) for k in ("R1", "R3", "R5", "R6", "R7", "R8")}
pct("R6 realized", vols_["R6"], 2, "10.32")
pct("R7 realized", vols_["R7"], 2, "10.14")
pct("R8 realized", vols_["R8"], 2, "11.52")
has("X5 realized row", "| Realized volatility | 10.32 | 10.14 | | | |")
pct("R1 realized (LM30's A30-12)", vols_["R1"], 2, "12.48")
pct("R3 realized (LM30's A30-12)", vols_["R3"], 2, "9.96")
pct("R5 realized (LM30's A30-12)", vols_["R5"], 2, "9.97")
pct("R1 full sample, fixed weights (LM27's A27-13)", math.sqrt(A) * vol(K.w1, cov0(fr.X)), 2, "11.49")
chk("U28 half", K.H, ",d", "2,191")
has("U28 halves dates", "2 December 2008 to 6 October 2017, and 11 October 2017 to 8 October 2026")
assert (K.u.dates[K.H - 1], K.u.dates[K.H]) == ("2017-10-06", "2017-10-11")
rows6 = {"1/N ([[LM30]])": K.echo30["1/N"], "Inverse volatility": K.halves["IV"], "ERC": K.halves["ERC"],
         "HRP": K.halves["HRP"], "Long-only minimum variance ([[LM30]])": K.echo30["long-only minimum variance"],
         "Sample minimum variance ([[LM30]])": K.echo30["sample minimum variance"]}
outs = {}
for nm_, w_ in rows6.items():
    vin = 100 * math.sqrt(K.u.A) * vol(w_, K.S1u)
    vout = 100 * math.sqrt(K.u.A) * vol(w_, K.S2u)
    outs[nm_] = vout
    has(f"X6 row {nm_}", f"| {nm_} | {vin:.2f} | {vout:.2f} |")
    assert not tie(vin, ".2f") and not tie(vout, ".2f")
    COVERED.update({f"{vin:.2f}", f"{vout:.2f}"})
chk("HRP second half", outs["HRP"], ".2f", "14.96")
assert outs["HRP"] == min(outs[k] for k in ("1/N ([[LM30]])", "Inverse volatility", "ERC", "HRP"))
assert outs["HRP"] > max(outs["Long-only minimum variance ([[LM30]])"], outs["Sample minimum variance ([[LM30]])"])
has("Lopez de Prado's design (SOURCES)", "10 series of 520 Gaussian observations, a 260-observation window, "
    "re-estimated and rebalanced every 22 observations, 10,000 runs")

# ---------------------------------------------------------------- Section 6: R8
sb, sf, L = K.sb, K.sf, K.L
chk("E8 sigma_bar a day", float(sb[0]), ".7f", "0.0034991")
chk("E8 EWMA a day", float(sf[0]), ".7f", "0.0041204")
pct("E8 sigma_bar a year", math.sqrt(A) * float(sb[0]), 2, "5.45")
pct("E8 EWMA a year", math.sqrt(A) * float(sf[0]), 2, "6.42")
chk("E8 L from printed", 0.0034991 / 0.0041204, ".4f", "0.8492")
chk("E8 L", float(L[0]), ".4f", "0.8492")
for k, p_ in enumerate(["0.1326", "0.1552", "0.2875", "0.2014", "0.0725"]):
    chk(f"E8 exposure {k + 1} from printed", 0.8492 * [0.1561, 0.1828, 0.3386, 0.2372, 0.0854][k], ".4f", p_)
    chk(f"E8 exposure {k + 1}", float(sigs[0].targets["R8"][k]), ".4f", p_)
chk("E8 cash", 1 - float(L[0]), ".3f", "0.151")
sci("E8 start weight", K.LAM**504, "2.9\\times10^{-14}")
chk("half-life of a 20-day EWMA", 0.5 ** (1 / 20), ".4f", "0.9659")
chk("R8's half-life (lm26.md:113)", math.log(0.5) / math.log(K.LAM), ".1f", "11.2")
chk("KC 6 L from printed", 5.45 / 6.42, ".3f", "0.849")
chk("KC 6 cash", 100 * (1 - 0.849), ".1f", "15.1")
chk("mean exposure", float(L.mean()), ".2f", "1.14")
chk("at the cap", len(K.capped), "d", "14")
chk("above 1", int((L > 1 + K.EPS).sum()), "d", "62")
chk("below 1", int((L < 1 - K.EPS).sum()), "d", "30")
chk("uncapped ratio max", float((sb / sf).max()), ".2f", "2.14")
pct("sigma_bar min", math.sqrt(A) * float(sb.min()), 2, "5.37")
pct("sigma_bar max", math.sqrt(A) * float(sb.max()), 2, "11.24")
pct("sigma_bar mean", math.sqrt(A) * float(sb.mean()), 2, "9.42")
pct("EWMA min", math.sqrt(A) * float(sf.min()), 2, "3.66")
pct("EWMA max", math.sqrt(A) * float(sf.max()), 2, "31.48")
assert sigs[int(sf.argmin())].signal == "2019-05-31" and sigs[int(sf.argmax())].signal == "2020-03-31"
assert int(L.argmin()) == int(sf.argmax()) and sigs[int(L.argmin())].trade == "2020-04-01"
chk("lowest exposure", float(L.min()), ".3f", "0.295")
has("X7 marks", "Marked: 4 March 2019 (0.85), 1 April 2020 (0.295) and 1 April 2025 (1.33)")
chk("X7 first L", float(L[0]), ".2f", "0.85")
assert sigs[0].trade == "2019-03-04"
assert K.err < 1e-14
has("EWMA matrix identity", "below $10^{-14}$ of $\\bar\\sigma_t^2$")
r8 = K.p8.wealth[1:] / K.p8.wealth[:-1]
assert bool((r8 > 0).all()) and K.p8.ruin is None and len(r8) == 1851
has("domain check", "R8 keeps $1+R_t>0$ on all 1,851 sessions")
has("Moreira and Muir's sample", "1926–2015 for the market, size, value and momentum")
has("Harvey et al.'s sample", "more than 60 assets with daily data from as early as 1926")

# ---------------------------------------------------------------- Section 7: judging the target
chk("SD log ratio R6", float(np.log(q6).std()), ".3f", "0.421")
chk("SD log ratio R8", float(np.log(q8).std()), ".3f", "0.421")
chk("R6 above 1.5", int((q6 > 1.5 + K.EPS).sum()), "d", "11")
chk("R8 above 1.5", int((q8 > 1.5 + K.EPS).sum()), "d", "11")
chk("R6 below 2/3", int((q6 < 2 / 3 - K.EPS).sum()), "d", "21")
chk("R8 below 2/3", int((q8 < 2 / 3 - K.EPS).sum()), "d", "13")
has("E10 counts", "Both have 11 holding months above 1.5; R6 has 21 below 2/3, R8 13.")
m20 = K.trades.index("2020-03-02")
chk("R6 ratio March 2020", float(q6[m20]), ".2f", "5.60")
chk("R8 ratio March 2020", float(q8[m20]), ".2f", "4.90")
assert K.p8.dates[K.idx[m20] + 1] == "2020-03-03" and K.p8.dates[K.idx[m20 + 1]] == "2020-04-01"
chk("R8 entry March 2020", float(L[K.k20]), ".3f", "0.884")
assert sigs[K.k20].trade == "2020-03-02"
loss, gq = K.loss, K.gq
chk("QLIKE mean window", float(loss["window"].mean()), ".3f", "0.691")
chk("QLIKE mean EWMA", float(loss["EWMA"].mean()), ".3f", "0.791")
chk("QLIKE median window", float(np.quantile(loss["window"], 0.5, method="inverted_cdf")), ".3f", "0.165")
chk("QLIKE median EWMA", float(np.quantile(loss["EWMA"], 0.5, method="inverted_cdf")), ".3f", "0.087")
won, lost = gq < 0, gq > 0
chk("EWMA wins", int(won.sum()), "d", "56")
chk("EWMA losses", int(lost.sum()), "d", "35")
chk("gains", float(-gq[won].sum()), ".2f", "17.25")
chk("mean gain", float(-gq[won].mean()), ".3f", "0.308")
chk("mean gain from printed", 17.25 / 56, ".3f", "0.308")
chk("costs", float(gq[lost].sum()), ".2f", "26.37")
chk("mean cost", float(gq[lost].mean()), ".3f", "0.753")
chk("mean cost from printed", 26.37 / 35, ".3f", "0.753")
chk("net cost", float(gq.sum()), ".2f", "9.12")
chk("net cost from printed", 26.37 - 17.25, ".2f", "9.12")
chk("gap in means", float(gq.mean()), ".3f", "0.100")
chk("gap in means from printed", 9.12 / 91, ".3f", "0.100")
worst, best = K.worst, K.best
assert worst == m25 and best == m20
chk("largest loss", float(gq[worst]), ".1f", "13.3")
chk("largest loss from printed", 27.50 - 14.17, ".1f", "13.3")
chk("EWMA QLIKE 2025", float(loss["EWMA"][worst]), ".2f", "27.50")
chk("window QLIKE 2025", float(loss["window"][worst]), ".2f", "14.17")
chk("largest win", float(-gq[best]), ".2f", "6.63")
chk("largest win from printed", 26.96 - 20.33, ".2f", "6.63")
chk("EWMA QLIKE 2020", float(loss["EWMA"][best]), ".2f", "20.33")
chk("window QLIKE 2020", float(loss["window"][best]), ".2f", "26.96")
assert sorted(int(x) for x in K.big) == sorted([worst, best])
chk("without 2025: window", float(np.delete(loss["window"], worst).mean()), ".3f", "0.541")
chk("without 2025: EWMA", float(np.delete(loss["EWMA"], worst).mean()), ".3f", "0.494")
chk("without both: window", float(np.delete(loss["window"], K.big).mean()), ".3f", "0.244")
chk("without both: EWMA", float(np.delete(loss["EWMA"], K.big).mean()), ".3f", "0.271")
to8 = K.to8
chk("trades after the first purchase", len(to8), "d", "91")
pct("mean one-way trade", float(to8.mean()), 1, "9.2")
pct("largest trade", float(to8.max()), 1, "45.2")
assert K.p8.trades[1 + int(to8.argmax())].trade == "2025-05-02"
has("largest trade date", "the cut of 2 May 2025")
has("trigger threshold", "by more than 0.5")
has("trigger fixed", "fixed by the editor on 24 October 2026 before any lab result")

# ---------------------------------------------------------------- Section 8 (knowledge check)
assert K.asym < 1e-15 and K.asym_nz and K.diag_nz and K.rejects and K.accepts
has("KC 8 bound", "asymmetric at machine precision (nonzero, below $10^{-15}$)")

# ---------------------------------------------------------------- practice problems and solutions
Sp = np.array([[0.04, 0.01], [0.01, 0.01]])
chk("P1 ERC", float(K.erc(Sp)[0]), ".3f", "0.333")
chk("P1 inverse variance", 0.25 / 1.25, ".3f", "0.200")
has("P1 options", "**A.** 0.200")
has("P1 option C", "**C.** 0.500")
wp = np.array([0.5, 0.5])
chk("P2 budget", float(shares(wp, Sp)[0]), ".3f", "0.714")
chk("P2 from printed", 0.0125 / 0.0175, ".3f", "0.714")
chk("P2 B", 0.1 / 0.15, ".3f", "0.667")
chk("P2 C", 0.01 / 0.0125, ".3f", "0.800")
assert np.abs(K.ccd(Sp, shares(wp, Sp))[0] - 0.5).max() < 1e-10
has("S2 Sigma w", "$\\Sigma\\mathbf w=(0.025,0.010)$")
v3 = np.array([0.1, 0.2, 0.4])
e3 = K.erc(np.outer(v3, v3) * (0.7 * np.eye(3) + 0.3))
chk("P3 ERC 40% fund", float(e3[2]), ".3f", "0.143")
chk("P3 from printed", (1 / 0.4) / (10 + 5 + 2.5), ".3f", "0.143")
chk("P3 inverse variance", 0.0625 / 1.3125, ".3f", "0.048")
chk("P3 1/N", 1 / 3, ".3f", "0.333")
w5p, sw5 = K.ccd(np.diag([0.04, 0.01]), np.array([0.7, 0.3]))
chk("P5 w1", float(w5p[0]), ".4f", "0.4330")
chk("P5 sqrt(.7)/.2", math.sqrt(0.7) / 0.2, ".4f", "4.1833")
chk("P5 sqrt(.3)/.1", math.sqrt(0.3) / 0.1, ".4f", "5.4772")
chk("P5 from printed", 4.1833 / (4.1833 + 5.4772), ".4f", "0.4330")
chk("P5 variance term 1", 0.4330**2 * 0.04, ".5f", "0.00750")
chk("P5 variance term 2", 0.5670**2 * 0.01, ".5f", "0.00321")
chk("P5 split", 0.00750 / (0.00750 + 0.00321), ".2f", "0.70")
assert sw5 == 1, "CCD reaches the uncorrelated solution in one sweep"
assert np.abs(shares(w5p, np.diag([0.04, 0.01])) - [0.7, 0.3]).max() < 1e-12
for k, (x, p_) in enumerate(zip([K.dp[0, 1], K.dp[0, 2], K.dp[1, 2]], ["0.3162", "0.6708", "0.6325"], strict=True)):
    chk(f"P6 d {k + 1}", float(x), ".4f", p_)
for k, (x, p_) in enumerate(zip([K.ddp[0, 1], K.ddp[0, 2], K.ddp[1, 2]], ["0.4489", "1.0000", "0.9622"],
                                strict=True)):
    chk(f"P6 column distance {k + 1}", float(x), ".4f", p_)
chk("P6 merge 1", float(K.Zp[0, 2]), ".4f", "0.4489")
chk("P6 merge 2", float(K.Zp[1, 2]), ".4f", "0.9622")
assert [int(i) + 1 for i in K.op] == [3, 1, 2]
has("P6 order", "so the order is (3, 1, 2)")
(_, _, pa, pb), (_, _, pc, pd) = K.stp
chk("P6 variance of [1, 2]", pb, ".6f", "0.043427")
assert abs(pb - 73 / 1681) < 1e-15
has("P6 fraction", "$73/1681=0.043427$")
chk("P6 first share", pb / (pa + pb), ".5f", "0.81283")
chk("P6 first share from printed", 0.043427 / (0.01 + 0.043427), ".5f", "0.81283")
chk("P6 second share", pd / (pc + pd), ".5f", "0.60976")
chk("P6 second share from printed", 0.0625 / 0.1025, ".5f", "0.60976")
chk("P6 remaining", 1 - pb / (pa + pb), ".5f", "0.18717")
chk("P6 w1 from printed", 0.60976 * 0.18717, ".4f", "0.1141")
chk("P6 w2 from printed", 0.39024 * 0.18717, ".4f", "0.0730")
for k, p_ in enumerate(["0.1141", "0.0730", "0.8128"]):
    chk(f"P6 weight {k + 1}", float(K.wpp[k]), ".4f", p_)
assert f"{sum(float(f'{x:.4f}') for x in K.wpp):.4f}" == "0.9999"
has("S6 sum", "(rounded separately; 0.9999 as printed)")
chk("P8 ratio 1", 8 / 5, ".1f", "1.6")
chk("P8 L 2", 8 / 16, ".1f", "0.5")
chk("P8 book 1", 100 * (1.5 * -0.03 - 0.5 * 0.035 / 243.57), ".4f", "-4.5072")
chk("P8 book 2", 100 * (0.5 * -0.03 + 0.5 * 0.015 / 243.57), ".4f", "-1.4969")
chk("P8 against the anchor", 100 * K.book[0], ".4f", "-4.5072")
chk("P8 against the anchor, 2", 100 * K.book[1], ".4f", "-1.4969")
has("P8 A_w", "$A_{\\mathrm w}=243.57$ sessions")
has("P10 stem", "Over 91 holding months R8's realized-to-target ratio has median 0.98 and SD of its logarithm 0.421, "
    "R6's 0.83 and 0.421")
has("P12 stem", "over the 92 month-ends from 27 February 2019 to 30 September 2026")
has("S11 counts", "(CCD in 12 sweeps, Newton in 6 steps)")

# ---------------------------------------------------------------- the overview's and summary's restatements
has("overview: steps", "in 6 steps and coordinate descent in 12 sweeps")
has("overview: R8", "its exposure averaged 1.14 over 92 trades and sat at the cap at 14 of them")
has("overview: QLIKE", "in 56 of 91 holding months, yet its mean QLIKE was the higher, 0.791 against 0.691")
has("summary: R8", "scales R6 to its window volatility, capped at 1.5.")

# ====================================================================== structure: labels, tags and citations
ex_labels = re.findall(r"\[!exhibit\][^\n]*\{#([\w-]+)\}", RAW)
eg_labels = re.findall(r"\[!example\][^\n]*\{#([\w-]+)\}", RAW)
assert len(ex_labels) == 8 and len(eg_labels) == 10, (ex_labels, eg_labels)
assert len(set(ex_labels) | set(eg_labels)) == 18, "a label is used twice"
for lab in ex_labels:
    assert f"[[ex:{lab}]]" in RAW, f"exhibit {lab} is never cited"
for kind, lab in re.findall(r"\[\[(ex|eg):([\w-]+)\]\]", RAW):
    assert lab in (ex_labels if kind == "ex" else eg_labels), (kind, lab)
tags = re.findall(r"\\tag\{(31\.\d+)\}", RAW)
assert sorted(tags) == [f"31.{k}" for k in range(1, 9)], tags
for name in re.findall(r'data-chart="(lm31-[\w-]+)"', RAW):
    assert (ROOT / "src" / "data" / f"{name}.json").exists(), name
assert len(re.findall(r"^> \[!kc\]", RAW, flags=re.MULTILINE)) == 7
print(f"labels: {len(ex_labels)} exhibits, {len(eg_labels)} examples, tags (31.1)-(31.8), every exhibit cited")

# ====================================================================== report
body = TEXT.split("\n## Glossary", 1)[0]
nums = set(re.findall(r"(?<![\w.])\d+\.\d+|(?<![\w.,])\d{1,3}(?:,\d{3})+", body))
left = sorted(n for n in nums if n not in COVERED)
print(f"\nnumbers with a decimal point or thousands separator not covered by a check ({len(left)}):")
print("   " + " ".join(left))
print(f"anchor differences ({len(ANCHOR_DIFFS)}):")
for a in ANCHOR_DIFFS:
    print("   ", a)
print(f"\nall {N_CHECKS} checks passed")
sys.exit(0)
