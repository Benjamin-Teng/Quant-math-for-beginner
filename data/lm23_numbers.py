"""Every number that LM23 (Linear Regression) prints, computed and checked against src/lm23.md and its charts.

Run:  uv run python data/lm23_numbers.py      (after data/vol2_series.py, data/vol3_series.py, data/build_series.py
                                              and data/vol4_series.py, and after data/lm23_charts.py: this script
                                              also checks the chart files src/data/lm23-*.json)

The computations live in data/lm23_common.py (its docstring states the samples and conventions: U28's T = 4,382 daily
price returns, A = 245.4794, OLS with s_eps^2 = RSS / (T - d), classical, White (HC0) and Newey-West standard errors
with the lag floor(4 (n/100)^(2/9)), divisor T for descriptive moments, LM19's rho_hat_k, F_hat^-1 by inverted_cdf, the
guard 1e-12, experiment 1 with default_rng([1, 20261011]) and LM18's paths with default_rng([3, 20261011])).

Checks (each stops the script on a failure):
  chk(label, value, fmt, printed)  format(value, fmt) equals the printed string, the value does not sit on a rounding
                                   tie of that format, and the printed string is in the module as a whole number.
                                   Hand computations are redone from the printed, rounded inputs (PITFALLS section 7).
  has(label, text)                 a literal string (a phrase, a table row) is in the module (after normalization).
  anchor(id, got)                  rebuilds the anchor row A23-NN of plans/vol-4-anchors.md from data/lm23_common.py
                                   with the anchor script's own formatting and reports a difference, never forcing it.
At the end the script lists the decimal numbers of the module that no check covered, and prints "all N checks passed".
"""
import inspect
import json
import math
import re
import sys
from math import floor, sqrt
from pathlib import Path

import numpy as np
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.multitest import multipletests

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import lm23_common as c

MD = ROOT / "src" / "lm23.md"
ANCHORS = ROOT / "plans" / "vol-4-anchors.md"
CHARTS = ROOT / "src" / "data"


def norm_text(s: str) -> str:
    """The module text with TeX thousands separators, escaped percent signs, \\text{} and minus signs made plain."""
    s = s.replace("{,}", ",").replace("\\%", "%").replace("\u2212", "-").replace("\\,", "").replace("\\$", "$")
    return re.sub(r"\\text\{\s*([^}]*)\}", r" \1", s)


RAW = MD.read_text(encoding="utf-8")
TEXT = norm_text(RAW)
N_CHECKS = 0
COVERED: set[str] = set()
ANCHOR_DIFFS: list[str] = []


def in_text(printed: str) -> bool:
    return re.search(r"(?<![\d.])" + re.escape(printed) + r"(?![\d])", TEXT) is not None


def tie(value: float, fmt: str) -> bool:
    m = re.search(r"\.(\d+)", fmt)
    d = int(m.group(1)) if m else 0
    scaled = abs(value) * 10**d * (100 if "%" in fmt else 1)
    return abs(scaled - math.floor(scaled) - 0.5) < 1e-6


def chk(label: str, value: float, fmt: str, printed: str) -> None:
    global N_CHECKS
    got = format(value, fmt)
    assert got == printed, (label, got, printed)
    assert not tie(value, fmt), ("rounding tie: print more digits", label, value)
    assert in_text(printed), f"{label}: {printed!r} not found in src/lm23.md"
    print(f"CHECK {label}: {got} ok")
    COVERED.add(printed.lstrip("-+"))
    N_CHECKS += 1


def has(label: str, text: str) -> None:
    global N_CHECKS
    assert text in TEXT, f"{label}: {text!r} not found in src/lm23.md"
    print(f"CHECK {label}: '{text[:70]}' in text ok")
    for num in re.findall(r"\d[\d,]*\.?\d*", text):
        COVERED.add(num.rstrip(".,"))
    N_CHECKS += 1


def same(label: str, got: object, expected: object) -> None:
    global N_CHECKS
    assert got == expected, (label, got, expected)
    print(f"CHECK {label}: {got} ok")
    N_CHECKS += 1


# ====================================================================== anchors (A23-NN), rebuilt as the anchor script does
def _anchor_values() -> dict[str, str]:
    rows: dict[str, str] = {}
    sec = ANCHORS.read_text(encoding="utf-8").split("## LM23", 1)[1].split("\n## ", 1)[0]
    for line in sec.splitlines():
        if line.startswith("| A23-"):
            cells = [x.strip() for x in line.strip().strip("|").split(" | ")]
            rows[cells[0]] = cells[3].strip("`")
    return rows


ANCHOR_ROWS = _anchor_values()
assert len(ANCHOR_ROWS) == 58, len(ANCHOR_ROWS)
_NEAR: list[str] = []


def f(x: float, *ks: int, plus: bool = False) -> str:
    """The anchor script's formatting: max(ks) + 3 decimals, NEAR flags within 0.1 of a last-digit unit."""
    x = float(x)
    for k in ks:
        u = abs(x) * 10**k
        if abs(u - floor(u) - 0.5) < 0.1:
            _NEAR.append(f"{x:.{k + 3}f} at {k} dp")
    return f"{x:{'+' if plus else ''}.{max(ks) + 3}f}"


def anchor(aid: str, value: str) -> None:
    global N_CHECKS
    tail = f" [NEAR a rounding boundary: {'; '.join(_NEAR)}]" if _NEAR else ""
    _NEAR.clear()
    got = value + tail
    expected = ANCHOR_ROWS[aid]
    tag = "ok" if got == expected else "DIFFERS"
    print(f"ANCHOR {aid}: {tag}")
    if got != expected:
        ANCHOR_DIFFS.append(f"{aid}: script {got} | anchor {expected}")
    N_CHECKS += 1


T, A, H, D = c.T, c.A, c.H, c.DATES
SEMI, FIN = c.SEMI, c.FIN
anchor("A23-01", f"T {T}; returns {D[0]} .. {D[-1]}; closes {c.CLOSE_DATES[0]} .. {c.CLOSE_DATES[-1]}")
anchor("A23-02", f"years {f(c.YEARS, 4)}; A {f(A, 4, 2)}")
anchor("A23-03", f"halves {H} + {T - H}: {D[0]} .. {D[H - 1]} and {D[H]} .. {D[-1]}")
anchor("A23-04", f"L = floor(4 (n/100)^(2/9)): n=4382 -> {c.nw_lag(4382)}, 2902 -> {c.nw_lag(2902)}, 2191 -> "
       f"{c.nw_lag(2191)}, 250 -> {c.nw_lag(250)}, 243 -> {c.nw_lag(243)}, 185 -> {c.nw_lag(185)}")
cnt_y = {y: int((c.YRS == y).sum()) for y in sorted(set(c.YRS))}
fy = {y: n for y, n in cnt_y.items() if "2009" <= y <= "2025"}
anchor("A23-05", f"2008 {cnt_y['2008']} returns (December); 2009-2025 {min(fy.values())}..{max(fy.values())} a year; "
       f"2025 {cnt_y['2025']}; 2026 {cnt_y['2026']} (to {D[-1]}); last 250 {D[T - 250]} .. {D[-1]}")
anchor("A23-06", f"Electronic: {len(c.EL)} returns, no null close; corr(TAIEX, Electronic) {f(c.RHO_ME, 3)}")
anchor("A23-07", f"LM2 sample: {len(c.R50)} pairs, {c.ETF_DATES[0]} .. {c.ETF_DATES[-1]}")
anchor("A23-08", f"TR23 on U28 dates: max abs(Rp - TAIEX) {np.abs(c.RP - c.MKT).max():.1e}; q_m = A mean(R - Rp) "
       f"{f(100 * c.QM, 2)}%; growth TR {f(np.prod(1 + c.RT), 2)} vs price {f(np.prod(1 + c.RP), 2)}")
anchor("A23-09", f"Semiconductor {c.SEMI_CLOSE[0]} -> {c.SEMI_CLOSE[-1]}: x{f(c.SEMI_CLOSE[-1] / c.SEMI_CLOSE[0], 1)}; "
       f"TAIEX {float(c.TAIEX_CLOSE[0]):.2f} -> {float(c.TAIEX_CLOSE[-1]):.2f}: "
       f"x{f(float(c.TAIEX_CLOSE[-1] / c.TAIEX_CLOSE[0]), 1)}")
anchor("A23-10", f"beta {f(SEMI.b[1], 3, 4)}; alpha {f(1e4 * SEMI.b[0], 2)} bp/day; A*alpha {f(100 * A * SEMI.b[0], 2)}%; "
       f"R-squared {f(SEMI.r2, 4, 5)}")
anchor("A23-11", f"SE(beta) classical {f(SEMI.se_c[1], 4)}, White {f(SEMI.se_w[1], 4)}, HAC(L={SEMI.lag}) "
       f"{f(SEMI.se_n[1], 4)}; SE(alpha) bp {f(1e4 * SEMI.se_c[0], 2)}, {f(1e4 * SEMI.se_w[0], 2)}, "
       f"{f(1e4 * SEMI.se_n[0], 2)}")
ta = [c.TA["c"], c.TA["w"], c.TA["n"]]
anchor("A23-12", "t(alpha) classical, White, HAC " + ", ".join(f(t, 2) for t in ta) + "; p "
       + ", ".join(f(c.two_sided(t), 3) for t in ta))
anchor("A23-13", f"halves beta {f(c.SH1.b[1], 3)} (HAC L={c.SH1.lag} {f(c.SH1.se_n[1], 3)}), {f(c.SH2.b[1], 3)} "
       f"(HAC {f(c.SH2.se_n[1], 3)}); alpha bp {f(1e4 * c.SH1.b[0], 2)}, {f(1e4 * c.SH2.b[0], 2)}")
lo_b, hi_b = min(c.BETAS, key=c.BETAS.__getitem__), max(c.BETAS, key=c.BETAS.__getitem__)
anchor("A23-14", f"betas {lo_b} {f(c.BETAS[lo_b], 3)} .. {hi_b} {f(c.BETAS[hi_b], 3)}")


def _bey(tt: dict[str, float]) -> list[str]:
    return [f"{k} {f(tt[k], 2, 3, 4, plus=True)}" for k in c.beyond(tt)]


anchor("A23-15", f"abs(t(alpha)) > 1.96: classical {_bey(c.T_C)}; White {_bey(c.T_W)}; HAC {_bey(c.T_N)}; expected "
       f"28 x 0.05 = {28 * 0.05:.1f}")
F4 = c.F4
anchor("A23-16", f"beta {f(F4.b[1], 1)}, alpha {f(F4.b[0], 1)}, RSS {f(F4.s2 * 2, 1)}, s_eps^2 {f(F4.s2, 1)}; SE(beta) "
       f"{f(F4.se_c[1], 3)}, SE(alpha) {f(F4.se_c[0], 3)}; t(beta) {f(F4.b[1] / F4.se_c[1], 2)}; t_2 quantile "
       f"{f(c.T2Q, 3)}; t interval {f(F4.b[1] - c.T2Q * F4.se_c[1], 2)}..{f(F4.b[1] + c.T2Q * F4.se_c[1], 2)}; 1.96 "
       f"interval {f(F4.b[1] - 1.96 * F4.se_c[1], 2)}..{f(F4.b[1] + 1.96 * F4.se_c[1], 2)}")
anchor("A23-17", f"s_eps (T-2) {f(100 * sqrt(SEMI.s2), 5)}%; divisor T {f(100 * c.SEMI_SDT, 5)}%; TAIEX mean "
       f"{f(100 * c.MX, 4)}%, s_x {f(100 * c.SX, 3)}%; s_eps/(sqrt(T) s_x) {f(sqrt(SEMI.s2) / (sqrt(T) * c.SX), 4)}")
anchor("A23-18", f"95% interval for beta: classical {f(SEMI.b[1] - 1.96 * SEMI.se_c[1], 3)}.."
       f"{f(SEMI.b[1] + 1.96 * SEMI.se_c[1], 3)}; HAC {f(SEMI.b[1] - 1.96 * SEMI.se_n[1], 3)}.."
       f"{f(SEMI.b[1] + 1.96 * SEMI.se_n[1], 3)}")
Q = c.Q_T
anchor("A23-19", f"t quantiles 0.975: df 4380 {f(Q[4380], 4)}, df 248 {f(Q[248], 3)}, df 241 {f(Q[241], 3, 4)}, df 183 "
       f"{f(Q[183], 3)}, normal {f(c.Q_N, 3, 4)}; t_183 / normal - 1 {f(100 * (Q[183] / c.Q_N - 1), 1)}%")
anchor("A23-20", f"adjusted R-squared {f(c.ADJ_R2, 5)}; F = t(beta)^2 {f(c.F_STAT, 0)} (t {f(SEMI.b[1] / SEMI.se_c[1], 2)})")
F25 = c.F25
anchor("A23-21", f"FinancialInsurance 2025: T {len(c.X25)}; beta {f(F25.b[1], 3)} (classical {f(F25.se_c[1], 3, 4)}, White "
       f"{f(F25.se_w[1], 3)}, HAC L={F25.lag} {f(F25.se_n[1], 3)}; White/classical {f(F25.se_w[1] / F25.se_c[1], 2)}); "
       f"alpha {f(1e4 * F25.b[0], 2)} bp; s_eps {f(100 * sqrt(F25.s2), 3)}%; R-squared {f(F25.r2, 4)}; TAIEX mean "
       f"{f(100 * float(c.X25.mean()), 4)}%, s_x {f(100 * float(c.X25.std(ddof=0)), 4)}%, min "
       f"{f(100 * float(c.X25.min()), 2, 4)}%, max {f(100 * float(c.X25.max()), 2)}%")
anchor("A23-22", f"x0 -5%: fitted {f(100 * c.YHAT0, 2)}%; SE(fit) {f(100 * c.SE_FIT, 3)}%; confidence "
       f"{f(100 * (c.YHAT0 - 1.96 * c.SE_FIT), 2)}..{f(100 * (c.YHAT0 + 1.96 * c.SE_FIT), 2)}%; prediction "
       f"{f(100 * (c.YHAT0 - 1.96 * c.SE_PRED), 2)}..{f(100 * (c.YHAT0 + 1.96 * c.SE_PRED), 2)}%; half-widths "
       f"{f(100 * 1.96 * c.SE_FIT, 2)} and {f(100 * 1.96 * c.SE_PRED, 2)} points; full-sample confidence half-width at "
       f"-5% {f(100 * c.HALF_FULL, 3)} points")
anchor("A23-23", f"2025-04-07: TAIEX {f(100 * float(c.R7), 2)}% (exact sample minimum by Fraction), FinancialInsurance "
       f"{f(100 * c.Y25[c.J7], 2)}%; leverage {f(c.H7, 3, 4)} (equals the formula 1/T + (x_t - xbar)^2/(T s_x^2)); "
       f"average d/T {f(2 / len(c.X25), 4)}; ratio {f(c.H7 / (2 / len(c.X25)), 0)}; beta without it {f(c.F25B.b[1], 3)} "
       f"(SE classical {f(c.F25B.se_c[1], 3)}, White {f(c.F25B.se_w[1], 3)}); shift of beta in classical SEs "
       f"{f((F25.b[1] - c.F25B.b[1]) / F25.se_c[1], 1)}; 2025 days with TAIEX <= -5%: {c.N5} (guard {c.N5})")
anchor("A23-24", f"beta = 1, Semiconductor: classical t {f(c.T_B1['c'], 1)}, HAC t {f(c.T_B1['n'], 1)}; against 0 with "
       f"HAC {f(c.T_B1['n0'], 1)}")
anchor("A23-25", f"m {c.M5}; rbar {100 * c.RBAR_TR:.7f}%, s_r {100 * c.SR_TR:.6f}%; beta hat {f(c.F18.b[1], 4)}; classical "
       f"{f(c.F18.se_c[1], 4)}; White {f(c.F18.se_w[1], 4)}; batch (LM18) {f(c.BSE, 4)}; model: beta "
       f"{f(c.BETA_MODEL, 4)}, sandwich SE {f(c.SE_SAND, 4)}, classical-formula SE {f(c.SE_CLASS_MODEL, 4)}; residual RMS "
       f"by tercile of ln G (cuts F^-1(1/3), F^-1(2/3); {', '.join(str(n) for n in c.TERC_N)} paths) "
       + ", ".join(f(v, 3) for v in c.TERC))
rl, rh = min(c.RATIO_W, key=c.RATIO_W.__getitem__), max(c.RATIO_W, key=c.RATIO_W.__getitem__)
nl, nh = min(c.RATIO_N, key=c.RATIO_N.__getitem__), max(c.RATIO_N, key=c.RATIO_N.__getitem__)
anchor("A23-26", f"SE(beta) White/classical {rl} {f(c.RATIO_W[rl], 2)} .. {rh} {f(c.RATIO_W[rh], 2)}; HAC/classical {nl} "
       f"{f(c.RATIO_N[nl], 2)} .. {nh} {f(c.RATIO_N[nh], 2)}")
F16 = c.F16
anchor("A23-27", f"LM16 pair: beta {f(F16.b[1], 4)} (lm16.md:354 prints 0.4591); SE classical {f(F16.se_c[1], 4)}, White "
       f"{f(F16.se_w[1], 4)}, HAC(9) {f(F16.se_n[1], 4)}; HAC interval {f(F16.b[1] - 1.96 * F16.se_n[1], 3)}.."
       f"{f(F16.b[1] + 1.96 * F16.se_n[1], 3)}; s_eps (T-2) {f(100 * sqrt(F16.s2), 5)}%, divisor T "
       f"{f(100 * float(F16.e.std(ddof=0)), 5)}% (lm12.md:436 prints 0.996%)")


def ov_txt(nm: str) -> str:
    o = c.OV[nm]
    return (f"{nm}: daily log beta {f(o.daily.b[1], 3)} (classical {f(o.daily.se_c[1], 4)}); overlapping "
            f"({len(o.ov.e)} windows) beta {f(o.ov.b[1], 3)}, classical {f(o.ov.se_c[1], 4)}, White {f(o.ov.se_w[1], 4)}, "
            f"NW(19) {f(o.ov.se_n[1], 4)}, NW(38) {f(o.ov38.se_n[1], 4)}; non-overlapping ({o.nwin} windows from the "
            f"first return) beta {f(o.non.b[1], 3)}, classical {f(o.non.se_c[1], 4)}; 20 starting days "
            f"{f(min(o.offs), 3)}..{f(max(o.offs), 3)}")


anchor("A23-28", ov_txt("Semiconductor"))
anchor("A23-29", "overlap residual rho_hat_k (LM19) " + ", ".join(f"lag {k} {f(c.RHO_OV[k], 3)}" for k in (1, 10, 19, 20))
       + f"; iid model (m - k)/m: lag 1 {19 / 20:.2f}, lag 10 {10 / 20:.2f}, lag 19 {1 / 20:.2f}, lag 20 0")
anchor("A23-30", ov_txt("FinancialInsurance") + " // " + ov_txt("Food"))
anchor("A23-31", "NW SE of Semiconductor's beta by L (0 = White): pooled residuals "
       + ", ".join(f"L{lg} {f(c.CURVE_AT[lg][0], 4)}" for lg in (0, 9, 50, 200))
       + f"; residuals of yearly fits ({c.N_YEAR_FITS} fits, 2008 its own) "
       + ", ".join(f"L{lg} {f(c.CURVE_AT[lg][1], 4)}" for lg in (0, 9, 50, 200)))
CI = c.CI
anchor("A23-32", f"(1 - beta) r_f / A at r_f = 2%: CommunicationsInternet beta {f(CI.b[1], 3)}: {f(1e4 * c.ADJ_CI, 2)} "
       f"bp/day ({f(100 * (1 - CI.b[1]) * 0.02, 2)}% a year), raw alpha {f(1e4 * CI.b[0], 2)} bp (SE classical "
       f"{f(1e4 * CI.se_c[0], 2)}), Jensen-type {f(1e4 * (CI.b[0] - c.ADJ_CI), 2)} bp; Semiconductor "
       f"{f(1e4 * c.ADJ_SEMI, 2)} bp/day ({f(100 * (1 - SEMI.b[1]) * 0.02, 2)}% a year)")
anchor("A23-33", f"dividend gap (q_i - beta q_m)/A: one point of yield = {f(1e4 * 0.01 / A, 2)} bp/day; Semiconductor with "
       f"q_i = q_m: {f(1e4 * c.GAP_SEMI, 2)} bp/day ({f(100 * (1 - SEMI.b[1]) * c.QM, 2)}% a year); alpha then "
       f"{f(1e4 * c.ALPHA_J_SEMI, 2)} bp/day with r_f = 2%")
big = c.HALF_SORTED
low_z = min(c.HALVES, key=lambda h: abs(h[3]))
anchor("A23-34", f"halves (HAC L=7 each): {c.N_HALF_SIG} of 28 differ by more than 1.96 SE; corr of halves' betas "
       f"{f(c.corr(c.B1V, c.B2V), 3)}; largest falls of beta {big[0][0]} {f(big[0][1], 3)} -> {f(big[0][2], 3)} "
       f"(z {f(big[0][3], 1)}), {big[1][0]} {f(big[1][1], 3)} -> {f(big[1][2], 3)}, {big[2][0]} {f(big[2][1], 3)} -> "
       f"{f(big[2][2], 3)}; largest rise {big[-1][0]} {f(big[-1][1], 3)} -> {f(big[-1][2], 3)} (z {f(big[-1][3], 1)}); "
       f"smallest abs(z) {low_z[0]} {f(abs(low_z[3]), 2)}")
roll_txt = []
for nm in ("FinancialInsurance", "Semiconductor"):
    rb = c.ROLL[nm][0]
    roll_txt.append(f"{nm} max {f(rb.max(), 3)} ({c.ROLL_DATES[int(rb.argmax())]}), min {f(rb.min(), 3)} "
                    f"({c.ROLL_DATES[int(rb.argmin())]}), last {f(rb[-1], 3)}")
anchor("A23-35", f"rolling 250-return betas ({T - 249} windows, first ends {D[249]}): " + "; ".join(roll_txt))
anchor("A23-36", "FinancialInsurance hedge ratios (beta, R-squared): "
       + "; ".join(f"{k} {f(v[0], 4)}, {f(v[1], 4)}" for k, v in c.HB.items())
       + f"; TX23 on {c.LAST if hasattr(c, 'LAST') else D[-1]}: F {c.F_LAST:.0f} (contract {c.CONTRACT}; TAIEX "
       f"{float(c.TAIEX_CLOSE[-1]):.2f}); NT$100m / (200 F): notional {f(c.NOTIONAL, 2)} contracts, full beta "
       f"{f(c.HB['full'][0] * c.NOTIONAL, 2)}, last-250 beta {f(c.HB['last250'][0] * c.NOTIONAL, 2)}")
red = []
for lab, key in (("none", "none"), ("notional 1", "notional"), ("first-half beta", "first"),
                 ("second-half beta (in-sample)", "second"), ("full beta", "full")):
    sd, rr = c.HEDGE_OOS[key]
    red.append(f"{lab} SD {f(100 * sd, 4)}%, reduction {f(100 * rr, 2)}%")
anchor("A23-37", "second half hedged: " + "; ".join(red))
F2, F2L, F2H = c.F2, c.FULL2[c.YLO], c.FULL2[c.YHI]
anchor("A23-38", f"LM2: slope {f(F2.b[1], 3, 4)} (lm02.md:496 prints 1.887), corr {f(c.corr(c.R50, c.R631), 3)}; SE "
       f"classical {f(F2.se_c[1], 4)}, White {f(F2.se_w[1], 4)}, HAC(L={F2.lag}) {f(F2.se_n[1], 4)}; (2 - slope)/HAC SE "
       f"{f((2 - F2.b[1]) / F2.se_n[1], 2)}; HAC interval {f(F2.b[1] - 1.96 * F2.se_n[1], 3)}.."
       f"{f(F2.b[1] + 1.96 * F2.se_n[1], 3)}; years 2015-2025: {c.YLO} {f(F2L.b[1], 3)} (HAC L={F2L.lag} "
       f"{f(F2L.se_n[1], 4)}), {c.YHI} {f(F2H.b[1], 3)} ({f(F2H.se_n[1], 4)}); difference z {f(c.ZDIFF, 2)}")
anchor("A23-39", "t(alpha) classical / HAC, ascending by classical: "
       + "; ".join(f"{k} {f(c.T_C[k], 2, 3, plus=True)}/{f(c.T_N[k], 2, 3, plus=True)}" for k in c.ORDER_T))
rej = {meth: (int(multipletests(c.P_C, alpha=0.05, method=meth)[0].sum()),
              int(multipletests(c.P_N, alpha=0.05, method=meth)[0].sum())) for meth in ("bonferroni", "holm", "fdr_bh")}
PS = np.sort(c.P_C)
bh_hand = sum(1 for i, p in enumerate(PS, start=1) if p <= 0.05 * i / 28)
HOLM_MIN = float(multipletests(c.P_C, method="holm")[1].min())
BH_MIN = float(multipletests(c.P_C, method="fdr_bh")[1].min())
BH_MIN_N = float(multipletests(c.P_N, method="fdr_bh")[1].min())
anchor("A23-40", f"Bonferroni p < {f(0.05 / 28, 5)}, abs(t) > {f(c.Z_BONF, 2)}; rejections (classical, HAC): {rej}; BH by "
       f"hand: largest i with p_(i) <= 0.05 i/28: {bh_hand}; smallest p {f(PS[0], 3)} vs 0.05/28; adjusted min: Holm "
       f"{f(HOLM_MIN, 3)}, BH {f(BH_MIN, 3)} (HAC {f(BH_MIN_N, 3)})")
RC = c.CRES[c.IU]
anchor("A23-41", f"residual correlations across sectors ({len(RC)} pairs): mean {f(RC.mean(), 3)}, min {f(RC.min(), 3)}, "
       f"max {f(RC.max(), 3)}")
anchor("A23-42", f"independent tests: count mean 1.4, SD {f(c.SD_IND, 3)}; Pr(>=1) {f(c.P_ANY_IND, 4)}; Pr(>=3) "
       f"{f(c.P3_IND, 3)}")
anchor("A23-43", f"experiment 1 (default_rng([1, 20261011]), {c.B1} draws): count mean {f(c.CNT_MEAN, 3)} (SE "
       f"{f(c.CNT_MEAN_SE, 3)}), SD {f(c.CNT_SD, 3)}; Pr(>=1) {c.N_ANY}/{c.B1} = {f(c.P_ANY, 3)} (binomial SE "
       f"{f(c.SE_ANY, 4)}); Pr(>=3) {c.N_GE3}/{c.B1} = {f(c.P_GE3, 3)} (SE {f(sqrt(c.P_GE3 * (1 - c.P_GE3) / c.B1), 4)})")
anchor("A23-44", f"corr(TAIEX, Electronic) {f(c.RHO_ME, 3)}, VIF {f(1 / (1 - c.RHO_ME**2), 1)}, condition number of the "
       f"correlation matrix {f((1 + c.RHO_ME) / (1 - c.RHO_ME), 0)}; corr(TAIEX, Electronic - TAIEX) {f(c.RHO_MF, 3)}, "
       f"VIF {f(1 / (1 - c.RHO_MF**2), 2)}, condition number {f((1 + c.RHO_MF) / (1 - c.RHO_MF), 2)}; SD daily: TAIEX "
       f"{f(100 * float(c.MKT.std(ddof=0)), 3)}%, factor {f(100 * float(c.FX.std(ddof=0)), 3)}%")


def frow(nm: str) -> str:
    t2f = c.TWO[nm]
    return (f"{nm}: one-factor {f(c.FITS[nm].b[1], 3)} (R2 {f(c.FITS[nm].r2, 4)}); market {f(t2f.b[1], 3)} "
            f"({f(t2f.se_c[1], 3)}; HAC {f(t2f.se_n[1], 3)}), electronics {f(t2f.b[2], 3, plus=True)} "
            f"({f(t2f.se_c[2], 3)}; HAC {f(t2f.se_n[2], 3)}); R2 {f(t2f.r2, 4)}")


FR = c.FRAW
anchor("A23-45", frow("Semiconductor") + f" // raw design (TAIEX, Electronic): {f(FR.b[1], 3, plus=True)} "
       f"({f(FR.se_c[1], 3)}), {f(FR.b[2], 3, plus=True)} ({f(FR.se_c[2], 3)}); market(excess) = market(raw) + "
       f"Electronic(raw) and the residuals agree within 1e-12")
anchor("A23-46", frow("FinancialInsurance"))
n_el_c = sum(1 for nm in c.NAMES if abs(c.T_EL_C[nm]) > 1.96 + c.EPS)
n_el_n = sum(1 for nm in c.NAMES if abs(c.T_EL_N[nm]) > 1.96 + c.EPS)
weak = min(c.NAMES, key=lambda k: abs(c.T_EL_C[k]))
assert weak == min(c.NAMES, key=lambda k: abs(c.T_EL_N[k]))
anchor("A23-47", f"electronics loadings abs(t) > 1.96: classical {n_el_c}, HAC {n_el_n} of 28 (smallest abs(t), both "
       f"methods: {weak} classical {f(c.T_EL_C[weak], 2, plus=True)}, HAC {f(c.T_EL_N[weak], 2, plus=True)}); halves' "
       f"loadings corr {f(c.corr(c.L1, c.L2), 3)}, cosine {f(c.cosine(c.L1, c.L2), 3)}; halves' betas corr "
       f"{f(c.corr(c.B1V, c.B2V), 3)}, cosine {f(c.cosine(c.B1V, c.B2V), 3)}")
anchor("A23-48", " // ".join(frow(nm) for nm in ("ElectronicPartsComponents", "ComputerPeripheralEquipment",
                                                "CommunicationsInternet", "Plastics")))
YFI = c.X[:, c.J["FinancialInsurance"]]
r_sm = sm.OLS(YFI, c.ZM).fit()
r_hc = sm.OLS(YFI, c.ZM).fit(cov_type="HC0")
r_hac = sm.OLS(YFI, c.ZM).fit(cov_type="HAC", cov_kwds={"maxlags": 9})
r_hac0 = sm.OLS(YFI, c.ZM).fit(cov_type="HAC", cov_kwds={"maxlags": 9, "use_correction": False})
r_hacc = sm.OLS(YFI, c.ZM).fit(cov_type="HAC", cov_kwds={"maxlags": 9, "use_correction": True})
dif = max(float(np.abs(np.asarray(r_sm.bse) / FIN.se_c - 1).max()), float(np.abs(np.asarray(r_hc.bse) / FIN.se_w - 1).max()),
          float(np.abs(np.asarray(r_hac.bse) / FIN.se_n - 1).max()), float(np.abs(np.asarray(r_hac0.bse) / FIN.se_n - 1).max()))
assert dif < 1e-12, dif
HACC = float(np.asarray(r_hacc.bse)[1])
anchor("A23-49", f"FinancialInsurance: beta {f(FIN.b[1], 4)}; SE classical {f(FIN.se_c[1], 4)}, HC0 {f(FIN.se_w[1], 4)}, "
       f"HAC(9) {f(FIN.se_n[1], 4)}; HAC use_correction=True {f(HACC, 5)} (x sqrt(T/(T-2)) {f(sqrt(T / (T - 2)), 6)}); "
       f"statsmodels agrees with NumPy (largest relative difference below 1e-12); HAC p-values normal: use_t "
       f"{r_hac.use_t}")
anchor("A23-50", f"P1 (T 12, d 2, RSS 0.0240): T-d {f(100 * sqrt(0.0240 / 10), 2)}%, T {f(100 * sqrt(0.0240 / 12), 2)}%, "
       f"T-1 {f(100 * sqrt(0.0240 / 11), 2)}%")
anchor("A23-51", f"P2 (s_eps 1%, s_x 1.2%, T 1000): {f(0.01 / (0.012 * sqrt(1000)), 4)}; {f(0.01 / 0.012, 3)}; "
       f"{f(0.01 / (0.012 * 1000), 6)}")
anchor("A23-52", f"P3 (beta 1.2073, SEs 0.0088 and 0.0185): {f((1.2073 - 1) / 0.0185, 1)}; "
       f"{f((1.2073 - 1) / 0.0088, 1)}; {f(1.2073 / 0.0185, 1)}")
anchor("A23-53", f"P4: sqrt(20) {f(sqrt(20), 1, 2)}; Semiconductor NW(19)/classical on the overlap "
       f"{f(c.OVS.ov.se_n[1] / c.OVS.ov.se_c[1], 2)}")
anchor("A23-54", f"P5 (beta 0.6, alpha 1.0 bp, r_f 2%, A 245.48): (1-beta) r_f/A {f(1e4 * 0.4 * 0.02 / 245.48, 3)} bp; "
       f"Jensen {f(1.0 - 1e4 * 0.4 * 0.02 / 245.48, 3)}; sign error {f(1.0 + 1e4 * 0.4 * 0.02 / 245.48, 3)}; beta "
       f"ignored {f(1.0 - 1e4 * 0.02 / 245.48, 3)}")
PP = [0.004, 0.011, 0.019, 0.030, 0.20]
anchor("A23-55", f"P6 rejections at 5%: Bonferroni {int(multipletests(PP, 0.05, 'bonferroni')[0].sum())}, Holm "
       f"{int(multipletests(PP, 0.05, 'holm')[0].sum())}, BH {int(multipletests(PP, 0.05, 'fdr_bh')[0].sum())}, "
       f"default 'hs' {int(multipletests(PP, 0.05)[0].sum())}")
XB, SXP = round(100 * float(c.X25.mean()), 4), round(100 * float(c.X25.std(ddof=0)), 4)
XT = round(100 * float(c.X25[c.J7]), 4)
anchor("A23-56", f"P8 from printed inputs (mean {XB}%, s_x {SXP}%, x_t {XT}%, T 243): h "
       f"{f(1 / 243 + (XT - XB) ** 2 / (243 * SXP**2), 4)}; sum of leverages {float(c.HAT25.sum()):.6f}")
anchor("A23-57", f"P9 (NT$50m, beta 0.75, R2 0.5, TX 20,000, NT$200 a point): contracts {0.75 * 50e6 / (200 * 20000):.3f}; "
       f"notional {50e6 / (200 * 20000):.2f}; residual SD factor {f(sqrt(0.5), 4)}")
anchor("A23-58", f"batch SE from 20 batches: relative error about 1/sqrt(2 x 20) = {f(100 / sqrt(40), 0)}%; LM18's batch / "
       f"model sandwich {f(c.BSE / c.SE_SAND, 2)}; White / model sandwich {f(c.F18.se_w[1] / c.SE_SAND, 2)}; classical / "
       f"model sandwich {f(c.F18.se_c[1] / c.SE_SAND, 2)} ({f(100 * c.F18.se_c[1] / c.SE_SAND, 0)}%)")
_NEAR.clear()

# ====================================================================== introduction, case, X1, notation, hygiene
same("T", T, 4382)
chk("T", T, ",", "4,382")
has("first return", "2 December 2008")
has("last return", "8 October 2026")
has("first close", "From 1 December 2008 to 8 October 2026")
chk("years", c.YEARS, ".4f", "17.8508")
chk("A", A, ".4f", "245.4794")
chk("half", H, ",", "2,191")
same("halves equal", T - H, H)
chk("Semiconductor growth", c.SEMI_CLOSE[-1] / c.SEMI_CLOSE[0], ".1f", "38.1")
chk("TAIEX price growth", float(c.TAIEX_CLOSE[-1] / c.TAIEX_CLOSE[0]), ".1f", "10.9")
has("case growth sentence", "rose 38.1-fold, against 10.9-fold for the TAIEX price index")
chk("beta", SEMI.b[1], ".3f", "1.207")
chk("beta four decimals", SEMI.b[1], ".4f", "1.2073")
chk("intercept bp", 1e4 * SEMI.b[0], ".2f", "2.10")
chk("intercept a year (%)", 100 * A * SEMI.b[0], ".2f", "5.16")
chk("intercept a year from the printed 2.10 bp", 100 * A * 2.10e-4, ".2f", "5.16")
chk("t classical", c.TA["c"], ".2f", "2.10")
chk("t White", c.TA["w"], ".2f", "2.10")
chk("t HAC", c.TA["n"], ".2f", "2.09")
chk("SE beta classical", SEMI.se_c[1], ".4f", "0.0088")
chk("SE beta White", SEMI.se_w[1], ".4f", "0.0129")
chk("SE beta HAC", SEMI.se_n[1], ".4f", "0.0185")
same("lag at T", SEMI.lag, 9)
chk("SE alpha classical bp", 1e4 * SEMI.se_c[0], ".2f", "1.00")
chk("SE alpha White bp", 1e4 * SEMI.se_w[0], ".2f", "1.00")
chk("SE alpha HAC bp", 1e4 * SEMI.se_n[0], ".2f", "1.01")
has("X1 beta row", "| Beta | 1.207 | 0.0088 | 0.0129 | 0.0185 |")
has("X1 intercept row", "| Intercept (bp a day) | 2.10 | 1.00 | 1.00 | 1.01 |")
has("X1 t row", "| t-stat of the intercept | | 2.10 | 2.10 | 2.09 |")
same("counts beyond 1.96 (classical, White, HAC)", (len(c.beyond(c.T_C)), len(c.beyond(c.T_W)), len(c.beyond(c.T_N))),
     (1, 1, 2))
same("classical and White: Semiconductor only", (c.beyond(c.T_C), c.beyond(c.T_W)), (["Semiconductor"], ["Semiconductor"]))
same("HAC adds Optoelectronic", c.beyond(c.T_N), ["Optoelectronic", "Semiconductor"])
has("X1 count row", "| 1 | 1 | 2 |")
chk("expected count", 28 * 0.05, ".1f", "1.4")
chk("R-squared", SEMI.r2, ".4f", "0.8112")
chk("halves first", c.SH1.b[1], ".3f", "1.089")
chk("halves second", c.SH2.b[1], ".3f", "1.294")
same("halves lag", (c.SH1.lag, c.SH2.lag), (7, 7))
chk("halves first, Newey-West SE", c.SH1.se_n[1], ".3f", "0.023")
chk("halves second, Newey-West SE", c.SH2.se_n[1], ".3f", "0.029")
has("case halves' SEs", "1.294 in the second (Newey–West standard errors 0.023 and 0.029)")
chk("smallest beta", c.BETAS["CommunicationsInternet"], ".3f", "0.507")
same("smallest and largest beta", (min(c.BETAS, key=c.BETAS.__getitem__), max(c.BETAS, key=c.BETAS.__getitem__)),
     ("CommunicationsInternet", "Semiconductor"))
has("X1 note betas", "run from 0.507 (CommunicationsInternet) to 1.207 (Semiconductor)")
rep = json.loads((HERE / "processed" / "vol2_repairs.json").read_text(encoding="utf-8"))["repairs"]
in_u28 = [r for r in rep if r["series"] in c.NAMES + ["TAIEX"] and c.CLOSE_DATES[0] <= r["date"] <= c.CLOSE_DATES[-1]]
in_el = [r for r in rep if r["series"] in c.NAMES + ["TAIEX", "Electronic"]
         and c.CLOSE_DATES[0] <= r["date"] <= c.CLOSE_DATES[-1]]
same("repaired closes in U28 (closes, dates)", (len(in_u28), len({r['date'] for r in in_u28})), (524, 38))
same("with Electronic", len(in_el), 542)
has("source line", "with 524 closes on 38 dates of U28 repaired")
has("references repairs", "repair 524 closes on 38 dates of U28, 542 with Electronic")

# ====================================================================== section 2
chk("four points beta", F4.b[1], ".1f", "1.4")
chk("four points alpha", F4.b[0], ".1f", "0.9")
chk("four points RSS", F4.s2 * 2, ".1f", "4.2")
chk("four points s2", F4.s2, ".1f", "2.1")
chk("x bar", float(c.X4.mean()), ".1f", "1.5")
chk("T s_x^2", float(((c.X4 - c.X4.mean()) ** 2).sum()), ".0f", "5")
chk("SE beta", F4.se_c[1], ".3f", "0.648")
chk("SE beta from printed", sqrt(2.1 / 5), ".3f", "0.648")
chk("SE alpha", F4.se_c[0], ".3f", "1.212")
chk("SE alpha from printed", sqrt(2.1 * (1 / 4 + 1.5**2 / 5)), ".3f", "1.212")
chk("t beta", F4.b[1] / F4.se_c[1], ".2f", "2.16")
chk("t beta from printed", 1.4 / 0.648, ".2f", "2.16")
chk("t_2 quantile", c.T2Q, ".3f", "4.303")
chk("t interval lo", F4.b[1] - c.T2Q * F4.se_c[1], ".2f", "-1.39")
chk("t interval hi", F4.b[1] + c.T2Q * F4.se_c[1], ".2f", "4.19")
chk("t interval lo from printed", 1.4 - 4.303 * 0.648, ".2f", "-1.39")
chk("t interval hi from printed", 1.4 + 4.303 * 0.648, ".2f", "4.19")
chk("1.96 interval lo", F4.b[1] - 1.96 * F4.se_c[1], ".2f", "0.13")
chk("1.96 interval hi", F4.b[1] + 1.96 * F4.se_c[1], ".2f", "2.67")
chk("1.96 interval lo from printed", 1.4 - 1.96 * 0.648, ".2f", "0.13")
chk("1.96 interval hi from printed", 1.4 + 1.96 * 0.648, ".2f", "2.67")
has("December 2008", "22 daily returns of December 2008 on the 28 sectors with an intercept: 29 columns of rank 22")
dec = [i for i, d in enumerate(D) if d.startswith("2008-12")]
Xd = np.column_stack([np.ones(len(dec)), c.X[dec]])
same("December 2008: returns, columns, rank", (len(dec), Xd.shape[1], int(np.linalg.matrix_rank(Xd))), (22, 29, 22))
b_dec = np.linalg.lstsq(Xd, c.MKT[dec], rcond=None)[0]
assert float(np.abs(c.MKT[dec] - Xd @ b_dec).max()) < 1e-12        # an exact fit: RSS = 0

# ====================================================================== section 3
same("smallest T - d of the later fits (widget's 2026)", min(v["T"] for v in c.window_table().values()) - 2, 183)
chk("t_183 quantile", c.Q_T[183], ".3f", "1.973")
chk("normal quantile", c.Q_N, ".3f", "1.960")
chk("t_183 excess (%)", 100 * (c.Q_T[183] / c.Q_N - 1), ".1f", "0.7")
has("fourth-moment caveat (decision XB7)", "Daily returns may lack a finite fourth moment ([[LM19]]), so these normal "
    "references are approximations.")
chk("s_eps T-2 (%)", 100 * sqrt(SEMI.s2), ".5f", "0.66239")
chk("s_eps T (%)", 100 * c.SEMI_SDT, ".5f", "0.66224")
chk("s_x (%)", 100 * c.SX, ".3f", "1.137")
chk("SE by hand", sqrt(SEMI.s2) / (sqrt(T) * c.SX), ".4f", "0.0088")
chk("SE by hand from printed", 0.66239 / (sqrt(4382) * 1.137), ".4f", "0.0088")
chk("classical interval lo", SEMI.b[1] - 1.96 * SEMI.se_c[1], ".3f", "1.190")
chk("classical interval hi", SEMI.b[1] + 1.96 * SEMI.se_c[1], ".3f", "1.225")
chk("classical interval lo from printed", 1.2073 - 1.96 * 0.0088, ".3f", "1.190")
chk("classical interval hi from printed", 1.2073 + 1.96 * 0.0088, ".3f", "1.225")
chk("HAC interval lo", SEMI.b[1] - 1.96 * SEMI.se_n[1], ".3f", "1.171")
chk("HAC interval hi", SEMI.b[1] + 1.96 * SEMI.se_n[1], ".3f", "1.244")
chk("HAC interval lo from printed", 1.2073 - 1.96 * 0.0185, ".3f", "1.171")
chk("HAC interval hi from printed", 1.2073 + 1.96 * 0.0185, ".3f", "1.244")
chk("p-value classical", c.two_sided(c.TA["c"]), ".3f", "0.036")
chk("p-value from printed 2.10", 2 * float(stats.norm.cdf(-2.10)), ".3f", "0.036")
chk("adjusted R-squared", c.ADJ_R2, ".5f", "0.81119")
chk("R-squared five decimals", SEMI.r2, ".5f", "0.81124")
assert f"{1 - (1 - 0.81124) * 4381 / 4380:.5f}" == "0.81120"     # so the text says "from unrounded values"
has("adjusted from unrounded", "0.81119 against 0.81124 (from unrounded values)")
chk("t beta classical", SEMI.b[1] / SEMI.se_c[1], ".2f", "137.20")
chk("F statistic", c.F_STAT, ",.0f", "18,824")
chk("F from printed 137.20", 137.20**2, ",.0f", "18,824")
has("LM12 identity", "[[LM12]]'s 0.99912 for TAIEX on its own sectors was an accounting identity")
same("2025 returns", len(c.X25), 243)
chk("2025 beta", F25.b[1], ".3f", "0.529")
chk("2025 classical SE", F25.se_c[1], ".4f", "0.0350")
chk("2025 White SE", F25.se_w[1], ".3f", "0.106")
chk("2025 s_eps (%)", 100 * sqrt(F25.s2), ".3f", "0.840")
same("days of 2025 at or below -5% (guard = Fraction)", c.N5, 2)
has("only 2 days", "a fall that only 2 days of 2025 reached")
chk("fitted at -5% (%)", 100 * c.YHAT0, ".3f", "-2.642")
chk("SE of the fit (points)", 100 * c.SE_FIT, ".4f", "0.1865")
chk("confidence lo", 100 * (c.YHAT0 - 1.96 * c.SE_FIT), ".2f", "-3.01")
chk("confidence hi", 100 * (c.YHAT0 + 1.96 * c.SE_FIT), ".2f", "-2.28")
chk("confidence lo from printed", -2.642 - 1.96 * 0.1865, ".2f", "-3.01")
chk("confidence hi from printed", -2.642 + 1.96 * 0.1865, ".2f", "-2.28")
chk("SE of prediction (points)", 100 * c.SE_PRED, ".3f", "0.860")
chk("prediction lo", 100 * (c.YHAT0 - 1.96 * c.SE_PRED), ".2f", "-4.33")
chk("prediction hi", 100 * (c.YHAT0 + 1.96 * c.SE_PRED), ".2f", "-0.96")
chk("prediction lo from printed", -2.642 - 1.96 * 0.860, ".2f", "-4.33")
chk("prediction hi from printed", -2.642 + 1.96 * 0.860, ".2f", "-0.96")
assert c.SE_PRED / c.SE_FIT > 4 and 0.860 / 0.1865 > 4
has("over four times", "is over four times as wide")
chk("full-sample half-width at -5%", 100 * c.HALF_FULL, ".3f", "0.105")
has("too narrow", "is 0.105 points, too narrow to show at this scale")
has("prediction interval condition", "The **prediction interval** for a new day also needs normal errors")
# M1: the band at -5% under White's errors, and the two days at or below -5%
chk("White SE of the fitted value at -5% (points)", 100 * c.SE_FIT_WHITE, ".3f", "0.557")
has("White fit SE sentence", "White's standard error of the fitted value there is 0.557 points, not 0.1865")
same("2025 days at or below -5%", [D[i] for i in np.flatnonzero(c.K25)[c.J5]], ["2025-04-07", "2025-04-09"])
same("their residuals in s_eps, two decimals", [f"{v:.2f}" for v in c.RES5], ["-5.67", "-3.03"])
chk("7 April residual (s_eps)", c.RES5[0], ".1f", "-5.7")
chk("9 April residual (s_eps)", c.RES5[1], ".1f", "-3.0")
same("both outside the 95% prediction band", c.OUT5, [True, True])
has("residuals sentence", "have residuals of −5.7 and −3.0 $s_\\varepsilon$, outside the prediction band".replace("−", "-"))
chk("7 April TAIEX fall (%)", -100 * float(c.R7), ".2f", "9.70")
chk("7 April FinancialInsurance fall (%)", -100 * c.Y25[c.J7], ".2f", "9.89")
has("7 April falls", "the TAIEX fell 9.70% and FinancialInsurance 9.89%")
chk("hat value", c.H7, ".4f", "0.1709")
chk("d/T", 2 / 243, ".4f", "0.0082")
chk("ratio", c.H7 / (2 / 243), ".0f", "21")
chk("ratio from printed", 0.1709 / 0.0082, ".0f", "21")
chk("beta without the day", c.F25B.b[1], ".3f", "0.432")
chk("shift in classical SEs", (F25.b[1] - c.F25B.b[1]) / F25.se_c[1], ".1f", "2.8")
chk("shift from printed", (0.529 - 0.432) / 0.0350, ".1f", "2.8")
chk("KC beta=1 classical", c.T_B1["c"], ".1f", "23.6")
chk("KC beta=1 HAC", c.T_B1["n"], ".1f", "11.2")
chk("KC beta=1 classical from printed", (1.2073 - 1) / 0.0088, ".1f", "23.6")
chk("KC beta=1 HAC from printed", (1.2073 - 1) / 0.0185, ".1f", "11.2")

# ====================================================================== section 4
same("LM18's horizon", c.M5, 1231)
chk("LM18's horizon", c.M5, ",", "1,231")
chk("LM18's paths", len(c.G3), ",", "10,000")
same("batches of 500", len(c.G3) // 20, 500)
has("LM18 printed", "It reported $\\hat\\beta=2.18$ with batch standard error 0.01")
chk("E4 beta", c.F18.b[1], ".4f", "2.1759")
chk("E4 classical", c.F18.se_c[1], ".4f", "0.0067")
chk("E4 White", c.F18.se_w[1], ".4f", "0.0152")
chk("E4 batch", c.BSE, ".4f", "0.0113")
chk("E4 model SE", c.SE_SAND, ".4f", "0.0157")
chk("E4 model beta", c.BETA_MODEL, ".4f", "2.1584")
chk("classical / model (%)", 100 * c.F18.se_c[1] / c.SE_SAND, ".0f", "43")
chk("classical / model from printed (%)", 100 * 0.0067 / 0.0157, ".0f", "43")
chk("White / model", c.F18.se_w[1] / c.SE_SAND, ".2f", "0.97")
chk("White / model from printed", 0.0152 / 0.0157, ".2f", "0.97")
chk("batch / model", c.BSE / c.SE_SAND, ".2f", "0.72")
chk("batch / model from printed", 0.0113 / 0.0157, ".2f", "0.72")
chk("relative error of 20 batches (%)", 100 / sqrt(40), ".0f", "16")
assert 1 - c.BSE / c.SE_SAND < 2 / sqrt(40) and 1 - 0.72 < 2 * 0.16      # "misses by under two such errors"
has("under two", "so the batch value misses by under two such errors")
chk("tercile lower", c.TERC[0], ".3f", "0.260")
chk("tercile middle", c.TERC[1], ".3f", "0.179")
chk("tercile upper", c.TERC[2], ".3f", "0.378")
same("tercile sizes", c.TERC_N, [3334, 3333, 3333])
chk("White/classical min", min(c.RATIO_W.values()), ".2f", "1.19")
chk("White/classical max", max(c.RATIO_W.values()), ".2f", "1.91")
chk("2025 White / classical", F25.se_w[1] / F25.se_c[1], ".0f", "3")
has("three times", "it is 0.106, three times the classical 0.0350")
chk("2025 White without the day", c.F25B.se_w[1], ".3f", "0.097")
chk("LM16 slope", F16.b[1], ".4f", "0.4591")
chk("LM16 SE classical", F16.se_c[1], ".4f", "0.0099")
chk("LM16 SE White", F16.se_w[1], ".4f", "0.0165")
chk("LM16 SE HAC", F16.se_n[1], ".4f", "0.0229")
chk("LM16 HAC interval lo", F16.b[1] - 1.96 * F16.se_n[1], ".3f", "0.414")
chk("LM16 HAC interval hi", F16.b[1] + 1.96 * F16.se_n[1], ".3f", "0.504")
chk("LM16 interval lo from printed", 0.4591 - 1.96 * 0.0229, ".3f", "0.414")
chk("LM16 interval hi from printed", 0.4591 + 1.96 * 0.0229, ".3f", "0.504")
chk("LM16 s_eps divisor T (%)", 100 * float(F16.e.std(ddof=0)), ".5f", "0.99603")
chk("LM16 s_eps divisor T-2 (%)", 100 * sqrt(F16.s2), ".5f", "0.99626")
chk("LM12's printed 0.996", 100 * float(F16.e.std(ddof=0)), ".3f", "0.996")
assert abs(sqrt(F16.s2) / float(F16.e.std(ddof=0)) - sqrt(c.T / (c.T - 2))) < 1e-12
has("their ratio", r"They differ by the factor $\sqrt{4382/4380}$, and both round to 0.996%")

# ====================================================================== section 5
O = c.OVS
same("overlapping windows", len(O.ov.e), 4363)
chk("overlapping windows", len(O.ov.e), ",", "4,363")
chk("rho_hat_1 of the overlap residuals", c.RHO_OV[1], ".3f", "0.953")
chk("lag 9", c.nw_lag(4382), "d", "9")
same("lags 7 and 4", (c.nw_lag(2191), c.nw_lag(243), c.nw_lag(250)), (7, 4, 4))
chk("overlap beta", O.ov.b[1], ".3f", "1.157")
chk("daily log beta", O.daily.b[1], ".3f", "1.204")
chk("daily log classical SE", O.daily.se_c[1], ".4f", "0.0088")
chk("overlap classical", O.ov.se_c[1], ".4f", "0.0089")
chk("overlap White", O.ov.se_w[1], ".4f", "0.0115")
chk("overlap NW19", O.ov.se_n[1], ".4f", "0.0389")
chk("overlap NW38", O.ov38.se_n[1], ".4f", "0.0464")
same("overlap lags", (O.ov.lag, O.ov38.lag), (19, 38))
chk("NW19 / classical from the printed 0.0389 and 0.0089", 0.0389 / 0.0089, ".1f", "4.4")
assert abs(O.ov.se_n[1] / O.ov.se_c[1] - 4.4) < 0.06          # unrounded 4.3495: "about 4.4"
has("about 4.4", "gives 0.0389, about 4.4 times the classical value")
has("4.4 is larger", "can explain why Semiconductor's 4.4 is larger")
has("iid NW at 19", "and Newey–West with $\\ell=19$ would show about 3.17 (Deep Dive)")
same("non-overlapping sums", O.nwin, 219)
chk("non-overlapping beta", O.non.b[1], ".3f", "1.106")
chk("non-overlapping SE", O.non.se_c[1], ".4f", "0.0406")
chk("starting days min", min(O.offs), ".3f", "1.106")
chk("starting days max", max(O.offs), ".3f", "1.189")
assert abs((max(O.offs) - min(O.offs)) / O.non.se_c[1] - 2) < 0.1          # "about twice its standard error"
has("about twice", "from 1.106 to 1.189, about twice its standard error")
chk("iid factor", c.iid_overlap_factor(20), ".2f", "3.65")
chk("iid variance ratio", (2 * 400 + 1) / 60, ".2f", "13.35")
chk("iid factor from 801/60", sqrt(801 / 60), ".2f", "3.65")
chk("Bartlett at 19", c.iid_overlap_factor(20, 19), ".2f", "3.17")
chk("Bartlett at 38", c.iid_overlap_factor(20, 38), ".2f", "3.41")
assert abs(2 * sum(j * j for j in range(1, 20)) - 19 * 20 * 39 / 3) < 1e-9
has("X5 daily row", "| Daily beta (classical SE) | 1.204 (0.0088) | 0.824 (0.0103) | 0.538 (0.0117) |")
has("X5 overlap row", "| Overlapping beta, 4,363 windows | 1.157 | 0.801 | 0.444 |")
has("X5 classical row", "| SE classical | 0.0089 | 0.0106 | 0.0109 |")
has("X5 White row", "| SE White | 0.0115 | 0.0164 | 0.0159 |")
has("X5 NW19 row", "| SE Newey–West, $\\ell=19$ | 0.0389 | 0.0543 | 0.0535 |")
has("X5 NW38 row", "| SE Newey–West, $\\ell=38$ | 0.0464 | 0.0610 | 0.0628 |")
has("X5 non-overlap row", "| Non-overlapping beta, 219 sums (classical SE) | 1.106 (0.0406) | 0.867 (0.0509) | 0.518 (0.0515) |")
has("X5 start row", "| Non-overlapping beta, over the 20 starting days | 1.106 to 1.189 | 0.707 to 0.889 | 0.387 to 0.518 |")
for nm, vals in (("Semiconductor", ("1.204", "0.0088", "1.157", "0.0089", "0.0115", "0.0389", "0.0464", "1.106", "0.0406",
                                    "1.106", "1.189")),
                 ("FinancialInsurance", ("0.824", "0.0103", "0.801", "0.0106", "0.0164", "0.0543", "0.0610", "0.867",
                                         "0.0509", "0.707", "0.889")),
                 ("Food", ("0.538", "0.0117", "0.444", "0.0109", "0.0159", "0.0535", "0.0628", "0.518", "0.0515", "0.387",
                           "0.518"))):
    o = c.OV[nm]
    got = (f"{o.daily.b[1]:.3f}", f"{o.daily.se_c[1]:.4f}", f"{o.ov.b[1]:.3f}", f"{o.ov.se_c[1]:.4f}", f"{o.ov.se_w[1]:.4f}",
           f"{o.ov.se_n[1]:.4f}", f"{o.ov38.se_n[1]:.4f}", f"{o.non.b[1]:.3f}", f"{o.non.se_c[1]:.4f}", f"{min(o.offs):.3f}",
           f"{max(o.offs):.3f}")
    same(f"X5 column {nm}", got, vals)
chk("lag curve White (l=0)", c.CURVE_AT[0][0], ".4f", "0.0129")
chk("lag curve l=9", c.CURVE_AT[9][0], ".4f", "0.0185")
chk("lag curve l=50", c.CURVE_AT[50][0], ".4f", "0.0275")
chk("lag curve l=200", c.CURVE_AT[200][0], ".4f", "0.0390")
chk("yearly l=9", c.CURVE_AT[9][1], ".4f", "0.0152")
chk("yearly l=50", c.CURVE_AT[50][1], ".4f", "0.0160")
chk("yearly l=200", c.CURVE_AT[200][1], ".4f", "0.0123")
same("yearly fits", c.N_YEAR_FITS, 19)
same("2008's returns", int((c.YRS == "2008").sum()), 22)
for k, v in ((1, "0.953"), (10, "0.538"), (20, "0.038")):
    chk(f"overlap residual rho_hat_{k}", c.RHO_OV[k], ".3f", v)
for k, v in ((1, "0.95"), (10, "0.50")):
    chk(f"iid (20 - k)/20 at {k}", (20 - k) / 20, ".2f", v)
has("KC overlap answer", "their correlation $(20-k)/20$: 0.95, 0.50 and 0")
has("covariance of sums by (16.4), Deep Dive", "By (16.4) the error sums then have covariance")
has("covariance of sums by (16.4), knowledge check", "so by (16.4) their covariance")
assert RAW.count("(16.3)") == 1 and "By (16.3) the hedged return" in RAW   # (16.3) only for a variance (XB5)
assert 2 / 9 < 1 / 4                                           # the lag rule's exponent, as the text says
has("lag rule exponent", "whose exponent 2/9 is below 1/4: 9 for 4,382 returns")

# ====================================================================== section 6
chk("TR growth", float(np.prod(1 + c.RT)), ".2f", "20.23")
chk("price growth", float(np.prod(1 + c.RP)), ".2f", "10.91")
assert float(np.abs(c.RP - c.MKT).max()) == 0.0
chk("q_mkt (%)", 100 * c.QM, ".2f", "3.46")
chk("r_f term Semiconductor (bp, added to Jensen)", -1e4 * c.ADJ_SEMI, ".2f", "0.17")
chk("dividend term Semiconductor (bp, subtracted)", -1e4 * c.GAP_SEMI, ".2f", "0.29")
chk("Jensen's alpha Semiconductor", 1e4 * c.ALPHA_J_SEMI, ".2f", "1.98")
chk("Jensen's alpha from printed", 2.10 + 0.17 - 0.29, ".2f", "1.98")
chk("one point of yield (bp)", 1e4 * 0.01 / A, ".2f", "0.41")
has("adds 0.17", "adds 0.17 bp a day to Jensen's alpha, and equal dividend yields subtract 0.29 bp")
same("halves differing", c.N_HALF_SIG, 25)
has("25 of 28", "for 25 of 28 sectors")
for nm, a1, a2 in (("FinancialInsurance", "1.156", "0.578"), ("Cement", "0.982", "0.463"),
                   ("Semiconductor", "1.089", "1.294")):
    h = next(x for x in c.HALVES if x[0] == nm)
    chk(f"halves {nm} first", h[1], ".3f", a1)
    chk(f"halves {nm} second", h[2], ".3f", a2)
same("two largest falls, largest rise", (c.HALF_SORTED[0][0], c.HALF_SORTED[1][0], c.HALF_SORTED[-1][0]),
     ("FinancialInsurance", "Cement", "Semiconductor"))
chk("halves' betas correlation", c.corr(c.B1V, c.B2V), ".3f", "0.653")
fib, fise = c.ROLL["FinancialInsurance"]
seb, sese = c.ROLL["Semiconductor"]
same("rolling windows", len(fib), 4133)
chk("rolling windows", len(fib), ",", "4,133")
same("first window ends", c.ROLL_DATES[0], "2009-11-30")
has("first window", "the first ending 30 November 2009")
chk("FI max", fib.max(), ".3f", "1.377")
chk("FI min", fib.min(), ".3f", "0.251")
chk("FI last", fib[-1], ".3f", "0.308")
chk("SC min", seb.min(), ".3f", "0.914")
chk("SC max", seb.max(), ".3f", "1.658")
chk("SC last", seb[-1], ".3f", "1.168")
same("rolling extreme dates", (c.ROLL_DATES[int(fib.argmax())], c.ROLL_DATES[int(fib.argmin())],
                               c.ROLL_DATES[int(seb.argmin())], c.ROLL_DATES[int(seb.argmax())]),
     ("2010-02-23", "2026-05-26", "2011-05-18", "2020-01-17"))
has("rolling sentence FI", "fell from 1.377 (window ending 23 February 2010) to 0.251 (26 May 2026), and ends at 0.308")
has("rolling sentence SC", "ranged from 0.914 (18 May 2011) to 1.658 (17 January 2020), and ends at 1.168")
chk("full-sample FI beta (X8 note)", c.BETAS["FinancialInsurance"], ".3f", "0.823")
# E6: the hedge
chk("hedge full beta", c.HB["full"][0], ".5f", "0.82338")
chk("hedge full R-squared", c.HB["full"][1], ".4f", "0.5916")
chk("hedge last250 beta", c.HB["last250"][0], ".5f", "0.30847")
chk("hedge last250 R-squared", c.HB["last250"][1], ".4f", "0.1989")
same("last 250 returns", (c.DATES[c.T - 250], c.DATES[-1]), ("2025-09-25", "2026-10-08"))
same("TX23 F and contract", (c.F_LAST, c.CONTRACT), (49357.0, 202610))
chk("F_t", c.F_LAST, ",.0f", "49,357")
chk("contract value", 200 * c.F_LAST, ",.0f", "9,871,400")
chk("notional contracts", c.NOTIONAL, ".2f", "10.13")
chk("full-beta contracts", c.HB["full"][0] * c.NOTIONAL, ".2f", "8.34")
chk("last-250 contracts", c.HB["last250"][0] * c.NOTIONAL, ".2f", "3.12")
chk("full-beta contracts from printed", 0.82338 * 10.13, ".2f", "8.34")
chk("last-250 contracts from printed", 0.30847 * 10.13, ".2f", "3.12")
chk("notional from printed", 100e6 / 9_871_400, ".2f", "10.13")
chk("first-half beta", c.HB["first"][0], ".4f", "1.1556")
chk("second-half beta", c.HB["second"][0], ".4f", "0.5784")
chk("OOS first-half reduction (%)", 100 * c.HEDGE_OOS["first"][1], ".2f", "0.19")
chk("OOS notional reduction (%)", 100 * c.HEDGE_OOS["notional"][1], ".2f", "23.09")
chk("second half's own reduction (%)", 100 * c.HEDGE_OOS["second"][1], ".2f", "49.29")
assert abs(c.HEDGE_OOS["second"][1] - c.HB["second"][1]) < 1e-12        # in-sample reduction = R-squared
# E7: LM2's slope
same("LM2 pairs", (len(c.R50), c.ETF_DATES[0], c.ETF_DATES[-1]), (2902, "2014-11-03", "2026-10-08"))
chk("LM2 pairs", len(c.R50), ",", "2,902")
chk("LM2 printed slope", F2.b[1], ".3f", "1.887")
chk("LM2 slope", F2.b[1], ".4f", "1.8865")
chk("LM2 classical", F2.se_c[1], ".4f", "0.0081")
chk("LM2 White", F2.se_w[1], ".4f", "0.0154")
chk("LM2 HAC", F2.se_n[1], ".4f", "0.0211")
same("LM2 lag", F2.lag, 8)
chk("distance to 2", (2 - F2.b[1]) / F2.se_n[1], ".2f", "5.38")
chk("distance to 2 from printed", (2 - 1.8865) / 0.0211, ".2f", "5.38")
chk("LM2 interval lo", F2.b[1] - 1.96 * F2.se_n[1], ".3f", "1.845")
chk("LM2 interval hi", F2.b[1] + 1.96 * F2.se_n[1], ".3f", "1.928")
chk("LM2 interval lo from printed", 1.8865 - 1.96 * 0.0211, ".3f", "1.845")
chk("LM2 interval hi from printed", 1.8865 + 1.96 * 0.0211, ".3f", "1.928")
same("extreme years", (c.YLO, c.YHI), ("2024", "2021"))
chk("2024 slope", F2L.b[1], ".3f", "1.717")
chk("2021 slope", F2H.b[1], ".3f", "1.984")
chk("2024 HAC", F2L.se_n[1], ".4f", "0.0759")
chk("2021 HAC", F2H.se_n[1], ".4f", "0.0776")
same("yearly lag", (F2L.lag, F2H.lag), (4, 4))
chk("z of the difference", c.ZDIFF, ".1f", "2.5")
chk("z from printed", (1.984 - 1.717) / sqrt(0.0759**2 + 0.0776**2), ".1f", "2.5")
same("years of 2015-2025", len(c.FULL2), 11)
same("years beyond 1.96 own SEs from the full slope", c.YEARS_BEYOND, ["2017", "2019", "2023", "2024"])
same("the same years against the printed 1.8865",
     [k for k, v in c.FULL2.items() if abs((v.b[1] - 1.8865) / v.se_n[1]) > 1.96 + c.EPS], c.YEARS_BEYOND)
chk("expected count of 11 at 5%", 11 * 0.05, ".2f", "0.55")
has("four of 11", "Four of the 11 lie more than 1.96 of their own standard errors from 1.8865, against about 0.55 expected")
has("picked", "The extremes, 2.5 standard errors of the difference apart, prove less: they were picked from 11 years")
# KC: CommunicationsInternet
chk("CI beta", CI.b[1], ".3f", "0.507")
chk("CI raw intercept (bp)", 1e4 * CI.b[0], ".2f", "-0.18")
chk("CI classical SE (bp)", 1e4 * CI.se_c[0], ".2f", "0.99")
chk("1 - beta", 1 - 0.507, ".3f", "0.493")
chk("r_f term (bp)", 1e4 * c.ADJ_CI, ".2f", "0.40")
chk("r_f term from printed (bp)", 1e4 * 0.493 * 0.02 / 245.4794, ".2f", "0.40")
chk("r_f term a year (%)", 100 * (1 - CI.b[1]) * 0.02, ".2f", "0.99")
chk("Jensen-type CI (bp, one decimal)", 1e4 * (CI.b[0] - c.ADJ_CI), ".1f", "-0.6")
chk("Jensen-type CI from printed", -0.18 - 0.40, ".1f", "-0.6")
assert c.ADJ_CI / CI.se_c[0] < 0.5
has("KC answer", "about −0.6 bp a day".replace("\u2212", "-"))

# ====================================================================== section 7
chk("Optoelectronic HAC t", c.T_N["Optoelectronic"], ".3f", "-1.965")
chk("Bonferroni p", 0.05 / 28, ".5f", "0.00179")
chk("Bonferroni t", c.Z_BONF, ".2f", "3.12")
same("rejections (classical, HAC) by every method", rej, {"bonferroni": (0, 0), "holm": (0, 0), "fdr_bh": (0, 0)})
same("BH by hand", bh_hand, 0)
chk("smallest p", PS[0], ".3f", "0.036")
same("smallest p is Semiconductor's", c.NAMES[int(np.argmin(c.P_C))], "Semiconductor")
assert PS[0] > 0.05 / 28 and float(np.sort(c.P_N)[0]) > 0.05 / 28 and float(np.sort(c.P_C * 0 + [two for two in (
    c.two_sided(c.T_W[k]) for k in c.NAMES)])[0]) > 0.05 / 28
chk("residual correlation min", RC.min(), ".3f", "-0.430")
chk("residual correlation max", RC.max(), ".3f", "0.462")
chk("residual correlation mean", RC.mean(), ".3f", "0.112")
same("pairs", len(RC), 378)
chk("experiment 1 draws", c.B1, ",", "100,000")
same("U28's column order is Python's sorted (experiment 1's columns)", list(c.NAMES), sorted(c.NAMES))
same("sorted puts ElectricMachinery before ElectricalCable (case-folded order would not)",
     (c.NAMES.index("ElectricMachinery") < c.NAMES.index("ElectricalCable"),
      sorted(c.NAMES, key=str.casefold) == list(c.NAMES)), (True, False))
has("experiment 1 call", "`rng.standard_normal((100_000, 28)) @ L.T` with `L = np.linalg.cholesky(C)`")
has("experiment 1 column order (Problem 12)", "the sectors in U28's column order, Python's `sorted` of their FinMind "
    "names (ElectricMachinery before ElectricalCable)")
has("experiment 1 column order (example)", "U28's column order (Problem 12 gives the call)")
assert "alphabetical" not in TEXT and "$L$ its Cholesky" not in TEXT and "$L$ the Cholesky" not in TEXT
chk("count mean", c.CNT_MEAN, ".2f", "1.41")
chk("count mean SE", c.CNT_MEAN_SE, ".3f", "0.005")
chk("count SD", c.CNT_SD, ".2f", "1.46")
chk("count SD's SE (delta method)", c.CNT_SD_SE, ".3f", "0.006")
assert 0.001 < c.CNT_MEAN_SE < 0.01 and 0.001 < c.CNT_SD_SE < 0.01     # SEs in the third decimal: print two
has("count sentence", "The count has mean 1.41 (Monte Carlo SE 0.005), as for independent tests")
has("SD sentence", "Its standard deviation is 1.46 (SE 0.006)")
chk("independent SD", c.SD_IND, ".3f", "1.153")
chk("Pr(at least one)", c.P_ANY, ".3f", "0.696")
same("Pr(at least one) count, an exact tie at four decimals", c.N_ANY, 69645)
chk("Pr(at least one) SE", c.SE_ANY, ".4f", "0.0015")
chk("independent Pr(at least one)", c.P_ANY_IND, ".4f", "0.7622")
chk("Pr(three or more)", c.P_GE3, ".3f", "0.178")
chk("Pr(three or more) SE", c.SE_GE3, ".4f", "0.0012")
has("three or more", "three or more with 0.178 (SE 0.0012), against 0.163")
chk("independent Pr(three or more)", c.P3_IND, ".3f", "0.163")
chk("zh: independent Pr(at least one), three decimals", c.P_ANY_IND, ".3f", "0.762")
has("case resolution", "is one draw from 28, and no correction rejects")
chk("Newey-West half-width of beta", 1.96 * SEMI.se_n[1], ".2f", "0.04")

# ====================================================================== section 8
chk("corr(TAIEX, Electronic)", c.RHO_ME, ".4f", "0.9696")
chk("VIF raw", 1 / (1 - c.RHO_ME**2), ".1f", "16.7")
chk("VIF raw from printed", 1 / (1 - 0.9696**2), ".1f", "16.7")
chk("condition number raw", (1 + c.RHO_ME) / (1 - c.RHO_ME), ".0f", "65")
chk("condition number raw from printed", (1 + 0.9696) / (1 - 0.9696), ".0f", "65")
chk("corr(TAIEX, factor)", c.RHO_MF, ".3f", "0.365")
chk("VIF factor", 1 / (1 - c.RHO_MF**2), ".2f", "1.15")
chk("VIF factor from printed", 1 / (1 - 0.365**2), ".2f", "1.15")
chk("condition number factor", (1 + c.RHO_MF) / (1 - c.RHO_MF), ".2f", "2.15")
chk("condition number factor from printed", (1 + 0.365) / (1 - 0.365), ".2f", "2.15")
chk("KC: SE factor sqrt(VIF)", sqrt(1 / (1 - c.RHO_ME**2)), ".0f", "4")
TS, TF = c.TWO["Semiconductor"], c.TWO["FinancialInsurance"]
chk("SC market", TS.b[1], ".3f", "1.037")
chk("SC electronics", TS.b[2], "+.3f", "+1.552")
chk("SC R-squared two-factor", TS.r2, ".4f", "0.9163")
chk("FI electronics", TF.b[2], ".3f", "-1.580")
chk("FI R-squared one-factor", c.FITS["FinancialInsurance"].r2, ".4f", "0.5916")
chk("FI R-squared two-factor", TF.r2, ".4f", "0.7624")
chk("raw TAIEX coefficient", FR.b[1], ".3f", "-0.515")
chk("raw Electronic coefficient", FR.b[2], "+.3f", "+1.552")
chk("identity from printed", -0.515 + 1.552, ".3f", "1.037")
chk("raw market classical SE", FR.se_c[1], ".3f", "0.024")
chk("two-factor market classical SE", TS.se_c[1], ".3f", "0.006")
same("loadings beyond 1.96 (classical, HAC)", (n_el_c, n_el_n), (27, 27))
same("weakest loading", weak, "CommunicationsInternet")
chk("weakest classical t", c.T_EL_C[weak], ".2f", "-1.05")
chk("weakest HAC t", c.T_EL_N[weak], ".2f", "-0.68")
chk("halves' loadings cosine", c.cosine(c.L1, c.L2), ".3f", "0.807")
has("LM11 PC2 cosine", "against 0.297 for [[LM11]]'s second component")
X7 = {"ElectronicPartsComponents": "| ElectronicPartsComponents | 1.154 | 0.6842 | 1.105 (0.019) | +0.452 (0.058) | 0.6924 |",
      "ComputerPeripheralEquipment": "| ComputerPeripheralEquipment | 0.978 | 0.6561 | 0.950 (0.017) | +0.249 (0.057) | 0.6594 |",
      "Semiconductor": "| Semiconductor | 1.207 | 0.8112 | 1.037 (0.009) | +1.552 (0.033) | 0.9163 |",
      "CommunicationsInternet": "| CommunicationsInternet | 0.507 | 0.4368 | 0.511 (0.013) | -0.033 (0.048) | 0.4370 |",
      "FinancialInsurance": "| FinancialInsurance | 0.823 | 0.5916 | 0.997 (0.022) | -1.580 (0.053) | 0.7624 |",
      "Plastics": "| Plastics | 0.861 | 0.3797 | 1.048 (0.030) | -1.706 (0.078) | 0.4966 |"}
for nm, row in X7.items():
    t2f = c.TWO[nm]
    el = f"{t2f.b[2]:+.3f}"
    got = (f"| {nm} | {c.FITS[nm].b[1]:.3f} | {c.FITS[nm].r2:.4f} | {t2f.b[1]:.3f} ({t2f.se_n[1]:.3f}) | {el} "
           f"({t2f.se_n[2]:.3f}) | {t2f.r2:.4f} |")
    same(f"X7 row {nm}", got, row)
    has(f"X7 row {nm} in text", row)

# ====================================================================== section 9, practice problems
chk("statsmodels HAC with correction", HACC, ".5f", "0.02885")
chk("book HAC, seven decimals", FIN.se_n[1], ".7f", "0.0288448")
chk("sqrt(T/(T-2))", sqrt(T / (T - 2)), ".6f", "1.000228")
chk("correction from printed", 0.0288448 * 1.000228, ".5f", "0.02885")
same("HAC p-values normal (use_t)", bool(r_hac.use_t), False)
same("get_robustcov_results() default is HC1", sm.OLS(YFI, c.ZM).fit().get_robustcov_results().cov_type, "HC1")
same("multipletests default is Holm-Sidak", inspect.signature(multipletests).parameters["method"].default, "hs")
chk("P1 key", 100 * sqrt(0.0240 / 10), ".2f", "4.90")
chk("P1 A", 100 * sqrt(0.0240 / 12), ".2f", "4.47")
chk("P1 C", 100 * sqrt(0.0240 / 11), ".2f", "4.67")
chk("P2 key", 0.01 / (0.012 * sqrt(1000)), ".4f", "0.0264")
chk("P2 B", 0.01 / 0.012, ".3f", "0.833")
chk("P2 C", 0.01 / (0.012 * 1000), ".6f", "0.000833")
chk("P3 key", (1.2073 - 1) / 0.0185, ".1f", "11.2")
chk("P3 A", 1.2073 / 0.0185, ".1f", "65.3")
chk("P3 B", (1.2073 - 1) / 0.0088, ".1f", "23.6")
chk("P4 key", c.iid_overlap_factor(20), ".1f", "3.7")
chk("P4 C", sqrt(20), ".1f", "4.5")
chk("P4 C two decimals", sqrt(20), ".2f", "4.47")
chk("P5 A rounded", A, ".2f", "245.48")
chk("P5 1 - beta", 1 - 0.6, ".1f", "0.4")
chk("P3 1.2073 - 1", 1.2073 - 1, ".4f", "0.2073")
chk("P5 term", 1e4 * 0.4 * 0.02 / 245.48, ".3f", "0.326")
chk("P5 key", 1.0 - 1e4 * 0.4 * 0.02 / 245.48, ".3f", "0.674")
chk("P5 key from printed", 1.0 - 0.326, ".3f", "0.674")
has("P5 stem: dividends ignored", "and ignore dividends ($q_i=q_{ mkt}=0$)")
has("P5 solution: dividends ignored", "With $q_i=q_{ mkt}=0$, (23.8) gives")
chk("P5 A", 1.0 + 1e4 * 0.4 * 0.02 / 245.48, ".3f", "1.326")
chk("P5 B", 1.0 - 1e4 * 0.02 / 245.48, ".3f", "0.185")
chk("P5 r_f/A", 1e4 * 0.02 / 245.48, ".3f", "0.815")
same("P6 Bonferroni, Holm, BH, default", tuple(int(multipletests(PP, 0.05, m)[0].sum()) for m in
                                              ("bonferroni", "holm", "fdr_bh", "hs")), (1, 2, 4, 2))
chk("P6 0.05/4", 0.05 / 4, ".4f", "0.0125")
chk("P6 0.05/3", 0.05 / 3, ".4f", "0.0167")
chk("P8 mean (%)", 100 * float(c.X25.mean()), ".4f", "0.1062")
chk("P8 s_x (%)", 100 * float(c.X25.std(ddof=0)), ".4f", "1.5405")
chk("P8 x_t (%)", 100 * float(c.X25[c.J7]), ".4f", "-9.6997")
chk("P8 mean - x_t (points)", 0.1062 + 9.6997, ".4f", "9.8059")
chk("P8 h from printed", 1 / 243 + 9.8059**2 / (243 * 1.5405**2), ".4f", "0.1709")
same("P8 hat values sum to 2", round(float(c.HAT25.sum()), 12), 2.0)
chk("P9 contracts", 0.75 * 50e6 / (200 * 20000), ".3f", "9.375")
chk("P9 notional", 50e6 / (200 * 20000), ".2f", "12.50")
chk("P9 SD factor", sqrt(0.5), ".4f", "0.7071")
chk("P11 beta", FIN.b[1], ".4f", "0.8234")
chk("P11 classical", FIN.se_c[1], ".4f", "0.0103")
chk("P11 HC0", FIN.se_w[1], ".4f", "0.0183")
chk("P11 HAC", FIN.se_n[1], ".4f", "0.0288")
chk("P12 smallest t", c.T_C["Optoelectronic"], ".3f", "-1.935")
chk("P12 largest t", c.T_C["Semiconductor"], ".3f", "2.097")
same("P12 extremes", (c.ORDER_T[0], c.ORDER_T[-1]), ("Optoelectronic", "Semiconductor"))
chk("Holm smallest adjusted p", HOLM_MIN, ".3f", "1.000")
chk("BH smallest adjusted p", BH_MIN, ".3f", "0.742")

# ====================================================================== charts: every cited value is plotted
fin = json.loads((CHARTS / "lm23-fin2025.json").read_text(encoding="utf-8"))
same("X2 points", len(fin["series"][0]["x"]), 243)
assert fin["series"][0]["x"] == sorted(fin["series"][0]["x"])                    # stored by the TAIEX return, no dates
bx = fin["bands"][0]["x"]
i5 = bx.index(-5.0)
same("X2 bands at -5% (prediction, confidence)",
     (f"{fin['bands'][0]['lo'][i5]:.2f}", f"{fin['bands'][0]['hi'][i5]:.2f}", f"{fin['bands'][1]['lo'][i5]:.2f}",
      f"{fin['bands'][1]['hi'][i5]:.2f}"), ("-4.33", "-0.96", "-3.01", "-2.28"))
same("X2 band grid", (len(bx), bx[0], bx[-1]), (60, round(100 * float(c.X25.min()), 4), round(100 * float(c.X25.max()), 4)))
hl = json.loads((CHARTS / "lm23-haclag.json").read_text(encoding="utf-8"))
xv = hl["x"]["values"]
for lg, v0, v1 in ((9, "0.0185", "0.0152"), (50, "0.0275", "0.0160"), (200, "0.0390", "0.0123")):
    i = xv.index(lg)
    same(f"X4 at lag {lg}", (f"{hl['series'][0]['y'][i]:.4f}", f"{hl['series'][1]['y'][i]:.4f}"), (v0, v1))
same("X4 lag range", (xv[0], xv[-1]), (1, 400))
_iy = int(np.argmax(hl["series"][1]["y"]))
same("X4 alt-text values (pooled lag 1; yearly lag 1, maximum and its lag, lag 400)",
     (f"{hl['series'][0]['y'][0]:.4f}", f"{hl['series'][1]['y'][0]:.4f}", f"{hl['series'][1]['y'][_iy]:.4f}", xv[_iy],
      f"{hl['series'][1]['y'][-1]:.4f}"), ("0.0138", "0.0127", "0.0161", 39, "0.0083"))
assert ("rises from 0.0138 at lag 1 (White's 0.0129 is dashed) through 0.0185 at 9, 0.0275 at 50 and 0.0390 at 200"
        in hl["alt"] and "rises from 0.0127 to 0.0161 at lag 39 and falls to 0.0083 at 400" in hl["alt"])
al = json.loads((CHARTS / "lm23-alphas.json").read_text(encoding="utf-8"))
same("X6 sectors", len(al["categories"]), 28)
for nm, a2, b2 in (("Semiconductor", "2.10", "2.09"), ("Optoelectronic", "-1.94", "-1.96"), ("Cement", "-1.53", "-1.56")):
    i = al["categories"].index(nm)
    same(f"X6 {nm}", (f"{al['series'][0]['values'][i]:.2f}", f"{al['series'][1]['values'][i]:.2f}"), (a2, b2))
ro = json.loads((CHARTS / "lm23-rolling.json").read_text(encoding="utf-8"))
rx = ro["x"]["values"]
for nm, si, d, v in (("FinancialInsurance", 2, "2010-02-23", "1.377"), ("FinancialInsurance", 2, "2026-05-26", "0.251"),
                     ("Semiconductor", 3, "2011-05-18", "0.914"), ("Semiconductor", 3, "2020-01-17", "1.658")):
    same(f"X8 {nm} {d}", f"{ro['series'][si]['y'][rx.index(d)]:.3f}", v)
same("X8 last values", (f"{ro['series'][2]['y'][-1]:.3f}", f"{ro['series'][3]['y'][-1]:.3f}", rx[-1]),
     ("0.308", "1.168", "2026-10-08"))
assert len(rx) < 1172 and all(len(s.get("y", s.get("lo", []))) == len(rx) for s in ro["series"])
bt = json.loads((CHARTS / "lm23-betas.json").read_text(encoding="utf-8"))
labels = bt["y"]["tickLabels"]
for nm, v in (("Semiconductor", "1.207"), ("CommunicationsInternet", "0.507")):
    same(f"X3 {nm}", f"{bt['series'][0]['x'][labels.index(nm)]:.3f}", v)
for nm, a1, a2 in (("FinancialInsurance", "1.156", "0.578"), ("Cement", "0.982", "0.463"), ("Semiconductor", "1.089", "1.294")):
    i = labels.index(nm)
    same(f"X3 halves {nm}", (f"{bt['series'][1]['x'][i]:.3f}", f"{bt['series'][2]['x'][i]:.3f}"), (a1, a2))
iS = labels.index("Semiconductor")
same("X3 Semiconductor intervals (HAC, classical)",
     tuple(f"{v:.3f}" for v in (bt["lines"][iS]["from"][0], bt["lines"][iS]["to"][0], bt["lines"][28 + iS]["from"][0],
                                bt["lines"][28 + iS]["to"][0])), ("1.171", "1.244", "1.190", "1.225"))
wg = json.loads((CHARTS / "lm23-regWindows.json").read_text(encoding="utf-8"))["widget"]
r0 = wg["rows"]["full"][wg["names"].index("Semiconductor")]
z975 = float(stats.norm.ppf(0.975))
same("widget initial state = X1 (beta, NW SE, interval, bp, % a year, t, R-squared, s_eps)",
     (f"{r0[0]:.3f}", f"{r0[3]:.4f}", f"{r0[0] - z975 * r0[3]:.3f}", f"{r0[0] + z975 * r0[3]:.3f}", f"{1e4 * r0[4]:.2f}",
      f"{100 * wg['A'] * r0[4]:.2f}", f"{r0[4] / r0[7]:.2f}", f"{r0[8]:.4f}", f"{100 * r0[9]:.3f}"),
     ("1.207", "0.0185", "1.171", "1.244", "2.10", "5.16", "2.09", "0.8112", "0.662"))
same("widget windows", (len(wg["windows"]), wg["windows"][0]["T"], wg["windows"][0]["lag"]), (22, 4382, 9))

# ====================================================================== structure: labels, citations, equation tags
ex_labels = re.findall(r"\[!exhibit\][^\n]*\{#([\w-]+)\}", RAW)
eg_labels = re.findall(r"\[!example\][^\n]*\{#([\w-]+)\}", RAW)
assert len(ex_labels) == 8 and len(eg_labels) == 9, (ex_labels, eg_labels)
for lab in ex_labels:
    assert f"[[ex:{lab}]]" in RAW, f"exhibit {lab} is never cited"
for kind, lab in re.findall(r"\[\[(ex|eg):([\w-]+)\]\]", RAW):
    assert lab in (ex_labels if kind == "ex" else eg_labels), (kind, lab)
tags = re.findall(r"\\tag\{(23\.\d+)\}", RAW)
assert tags == [f"23.{k}" for k in range(1, 10)], tags
print(f"labels: {len(ex_labels)} exhibits, {len(eg_labels)} examples, tags {tags[0]}..{tags[-1]}")
# decision XB10: the English at a term's first use in each box (the editor's named terms and revision 2's own scan)
ZH = re.findall(r"^> \[!zh\][^\n]*\n> ([^\n]+)", RAW, flags=re.MULTILINE)
GLOSS = [["迴歸（regression）", "係數（coefficient）", "誤差（error）", "估計量（estimator）", "殘差（residual）",
          "變異數（variance）", "維度（dimension）", "互不相關（uncorrelated）"],
         ["係數（coefficient）", "標準誤（standard error）", "誤差（error）", "抽樣誤差（sampling error）", "檢定（test）"],
         ["誤差（error）", "變異數（variance）", "殘差（residual）", "互不相關（uncorrelated）",
          "參數漂移（parameter drift）"],
         ["迴歸（regression）", "標準誤（standard error）", "變異數（variance）", "殘差（residual）",
          "股利殖利率（dividend yield）"],
         ["殘差（residual）", "檢定（test）", "門檻（threshold）", "機率（probability）"]]
same("Chinese boxes", len(ZH), len(GLOSS))
for box, terms in zip(ZH, GLOSS, strict=True):
    for g in terms:
        assert g in box and box.index(g) <= box.index(g.split("（")[0]), ("XB10: no English at first use", g)
# decision XB11: one Chinese form per concept (參數漂移, 股利殖利率, 互不相關)
for old in ("彼此不相關", "在漂移", "與殖利率"):
    assert old not in RAW, ("XB11: superseded form", old)
print("XB10/XB11: the named terms carry their English at first use in each box, in the book's one form")

# ====================================================================== report
body = TEXT.split("\n## Glossary", 1)[0].split("\n---\n", 1)[1]
nums = set(re.findall(r"(?<![\w.])\d+\.\d+|(?<![\w.,])\d{1,3}(?:,\d{3})+", body))
left = sorted(n for n in nums if n not in COVERED)
print(f"\nnumbers with a decimal point or thousands separator not covered by a check ({len(left)}):")
print("   " + " ".join(left))
print(f"\nanchor differences ({len(ANCHOR_DIFFS)}):")
for a in ANCHOR_DIFFS:
    print("   ", a)
print(f"\nall {N_CHECKS} checks passed")
