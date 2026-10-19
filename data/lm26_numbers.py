"""Every number that LM26 (Time Series II: Volatility Models) prints, computed and checked against src/lm26.md.

Run:  PYTHONUTF8=1 uv run python data/lm26_numbers.py
      (after data/vol3_series.py, data/vol4_series.py and data/vol4_rv.py; and after data/lm26_charts.py, whose
      widget data this script checks)

Inputs and conventions: data/lm26_common.py (TR23 from data/processed/vol3_taiex.parquet; the per-day realized
variances data/derived/vol4_rv.csv; TX23 from data/processed/vol4_tx23.parquet; the raw 5-second TAIEX files and the
2025 TX 1-minute bars under data/raw/intraday/ for the statistics marked "raw download"). The module text is
src/lm26.md; plans/vol-4-anchors.md, "LM26", holds the Stage 1 anchors A26-01 .. A26-66, which data/vol4_anchors_lm26.py
prints and this script started from.

Part 1 recomputes every anchor line exactly as data/vol4_anchors_lm26.py prints it and compares it with the anchor
table's Value column: a difference is reported, never forced. Lines that need the raw intraday download are skipped,
and said to be skipped, when the download is missing.

Part 2 checks the text (each check stops the script on a failure):
  chk(label, value, fmt, printed)  format(value, fmt) equals the printed string, the value is not a rounding tie of
                                   that format, and the printed string is in the module as a whole number. Hand
                                   computations are redone from the printed, rounded inputs (PITFALLS section 7).
  sci(label, value, digits, printed)  the same for a number printed as m\times10^{e}.
  has(label, text)                 a literal string (a date, a phrase, a table row) is in the module.
  flag(label, value, d)            reports a printed value within a tenth of a unit of a rounding boundary at d
                                   decimals (the anchors' NEAR flag), so that it can be watched; it fails nothing.
At the end the script lists the numbers of the module that no check covered and prints "all N checks passed".
"""
import json
import math
import re
import sys

import lm26_common as C
import numpy as np
import statsmodels.api as sm
from lm26_common import (
    EPS,
    IV,
    LAM,
    NAMES,
    NN,
    O2,
    RV,
    SEED,
    V15,
    A,
    T,
    Vmap,
    Vt,
    ann,
    batch_se_median,
    dates,
    days_span,
    half_life,
    i05,
    iso,
    month,
    nw_lags,
    nw_se,
    ols_hc0,
    pos,
    qinv,
    qlike,
    reg,
    rv_dates,
    ryear,
    starts,
    y,
    years,
)
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch

ROOT = C.ROOT
MD = ROOT / "src" / "lm26.md"
ANCHORS = ROOT / "plans" / "vol-4-anchors.md"
WIDGET = ROOT / "src" / "data" / "lm26-garchterm.json"
RAW = C.raw5_available() and C.tx25_available()


# ====================================================================== text helpers
def norm_text(s: str) -> str:
    """The module text with TeX thousands separators, escaped percent signs, \\text{} and minus signs made plain."""
    s = s.replace("{,}", ",").replace("\\%", "%").replace("\u2212", "-").replace("\\,", "")
    return re.sub(r"\\text\{\s*([^}]*)\}", r" \1", s)


TEXT = norm_text(MD.read_text(encoding="utf-8"))
N_CHECKS = 0
COVERED: set[str] = set()
ANCHOR_DIFFS: list[str] = []
SKIPPED: list[str] = []
FLAGS: list[str] = []


def in_text(printed: str) -> bool:
    """The printed number appears as a whole number (2.323 is not inside 2.3235, 0.32 not inside 10.32)."""
    return re.search(r"(?<![\d.])" + re.escape(printed) + r"(?![\d])", TEXT) is not None


def tie(value: float, fmt: str) -> bool:
    m = re.search(r"\.(\d+)", fmt)
    d = int(m.group(1)) if m else 0
    if fmt.endswith(("e", "g")):
        return False
    scaled = abs(value) * 10**d * (100 if "%" in fmt else 1)
    return abs(scaled - math.floor(scaled) - 0.5) < 1e-6


def chk(label: str, value: float, fmt: str, printed: str, in_md: bool = True) -> None:
    global N_CHECKS
    got = format(value, fmt)
    print(f"CHECK {label}: {got} (printed {printed})")
    assert got == printed, (label, got, printed)
    assert not tie(value, fmt), ("rounding tie: print more digits", label, value)
    assert not in_md or in_text(printed), f"{label}: {printed!r} not found in src/lm26.md"
    COVERED.add(printed.lstrip("-"))
    N_CHECKS += 1


def has(label: str, text: str) -> None:
    global N_CHECKS
    assert text in TEXT, f"{label}: {text!r} not found in src/lm26.md"
    print(f"CHECK {label}: '{text[:80]}' in text")
    for num in re.findall(r"\d[\d,]*\.?\d*", text):
        COVERED.add(num.rstrip(".,"))
    N_CHECKS += 1


def sci(label: str, value: float, digits: int, printed: str) -> None:
    """A number printed as m\\times10^{e}: printed is 'm e', e.g. '8.2 -51'."""
    global N_CHECKS
    mant, ex = printed.split()
    got = f"{value:.{digits}e}"
    assert float(got) == float(f"{mant}e{ex}"), (label, got, printed)
    tex = f"{mant}\\times10^{{{ex}}}"
    assert tex in TEXT, f"{label}: {tex!r} not found in src/lm26.md"
    print(f"CHECK {label}: {got} (printed {tex})")
    COVERED.add(mant)
    N_CHECKS += 1


def flag(label: str, value: float, d: int) -> None:
    y_ = abs(value) * 10**d
    if abs(y_ - math.floor(y_) - 0.5) < 0.1:
        FLAGS.append(f"{label}: {value:.{d + 3}f} lies within a tenth of a unit of a boundary at {d} decimals")


# ====================================================================== anchors (part 1)
def near(x: float, d: int) -> bool:
    yy = abs(x) * 10**d
    return abs(yy - math.floor(yy) - 0.5) < 0.1


def v(x: float, shown: int, *printed: int, sign: bool = False) -> str:
    flagged = [d for d in printed if near(x, d)]
    shown = max([shown] + [d + 2 for d in flagged])
    return f"{x:{'+' if sign else ''}.{shown}f}" + (f" NEAR({','.join(map(str, flagged))})" if flagged else "")


def sci_a(x: float, shown: int, printed: int) -> str:
    mant = abs(x) / 10 ** math.floor(math.log10(abs(x)))
    return f"{x:.{shown}e}" + (" NEAR" if near(mant, printed) else "")


def _anchor_values() -> dict[str, str]:
    rows: dict[str, str] = {}
    sec = ANCHORS.read_text(encoding="utf-8").split("\n## LM26", 1)[1].split("\n## ", 1)[0]
    for line in sec.splitlines():
        if line.startswith("| A26-"):
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
            rows[cells[0]] = cells[3].strip("`").replace("\\|", "|")
    return rows


ANCHOR_ROWS = _anchor_values()
assert len(ANCHOR_ROWS) == 66, len(ANCHOR_ROWS)


def anchor(nn: int, got: str) -> None:
    aid = f"A26-{nn:02d}"
    expected = ANCHOR_ROWS[aid]
    tag = "ok" if got == expected else "DIFFERS"
    print(f"ANCHOR {aid}: {tag}")
    if got != expected:
        ANCHOR_DIFFS.append(f"{aid}:\n      script {got}\n      anchor {expected}")


def skip(nn: int) -> None:
    SKIPPED.append(f"A26-{nn:02d}")


# ---------------------------------------------------------------- data role
anchor(1, f"T {T} returns {dates[0]} .. {dates[-1]}; days {days_span}; years {years:.6f}; A {A:.6f}")
regimes = []
for s_ in (60, 15, 10, 5):
    idx = np.flatnonzero(reg == s_)
    regimes.append(f"{s_}s: {len(idx)} days {rv_dates[idx[0]]} .. {rv_dates[idx[-1]]}")
anchor(2, f"T5S {len(rv_dates)} days {rv_dates[0]} .. {rv_dates[-1]}; " + "; ".join(regimes))
tr_from05 = [d for d in dates if d >= "2005-01-03"]
anchor(3, f"T5S dates equal TR23's dates from 2005-01-03: {len(tr_from05)} = {len(rv_dates)}")
counts = []
for name, h in IV:
    ok = ~np.isnan(NN[name])
    assert np.all(NN[name][ok] == 14400 // h)
    counts.append(f"{name} {14400 // h} ({int(ok.sum())} days)")
anchor(4, "returns a day on 09:30:00-13:30:00: " + ", ".join(counts))
div_share = float(np.sum(y[i05:] ** 2 - (100 * C.rp[i05:]) ** 2) / np.sum(y[i05:] ** 2))
anchor(5, f"mean r^2 (TR23, total return) {np.mean(y[i05:] ** 2):.6f} %^2, mean r_p^2 (price index) "
          f"{np.mean((100 * C.rp[i05:]) ** 2):.6f} %^2 on the 5,351 T5S days; (sum r^2 - sum r_p^2)/sum r^2 {div_share:.5%}")

# ---------------------------------------------------------------- fits and forecasts
FF = C.full_fits()
gn, gn_c, gt, gt_c = FF["gn"], FF["gn_c"], FF["gt"], FF["gt_c"]
pn, pt, cvn, cvt = FF["pn"], FF["pt"], FF["cvn"], FF["cvt"]
s2_hand, ll_hand, bc_full = FF["s2"], FF["ll_hand"], FF["bc"]
xin, xit = FF["xin"], FF["xit"]
FO = C.forecasts()
W, first, oos, FC, refits = FO["W"], FO["first"], FO["oos"], FO["FC"], FO["refits"]
ew = C.ewma_path()

# ---------------------------------------------------------------- case
i7, i2, i8 = pos["2025-04-07"], pos["2025-04-02"], pos["2025-04-08"]
assert i7 == i2 + 1
R = C.R
rank = int(np.argsort(R)[0])
anchor(6, f"2025-04-07: R {v(100 * R[i7], 4, 2, 4)}% (rank 1 of {T}: {rank == i7}); r {v(y[i7], 4, 2, 4)}%; 2025-04-02 r "
          f"{y[i2]:.4f}%")
case = []
for k in ("garch_n", "ewma", "roll60", "v_prev"):
    f = FC[k][i7]
    case.append(f"{NAMES[k]} {v(math.sqrt(f), 4, 2, 4)}% a day ({v(ann(f), 2, 1)}% a year), r/sigma "
                f"{v(y[i7] / math.sqrt(f), 3, 1)}")
anchor(7, "forecasts for 2025-04-07 made on 2025-04-02: " + "; ".join(case))
anchor(8, f"2025-04-07: V {V15[i7]:.4f} %^2 (sqrt {v(math.sqrt(V15[i7]), 4, 2, 4)}%), o2 share "
          f"{v(100 * (1e4 * O2[rv_dates.index('2025-04-07')] / V15[i7]), 4, 2)}%, r^2 {v(y[i7] ** 2, 4, 4)} %^2; "
          f"V/r^2 {V15[i7] / y[i7] ** 2:.4f}")
case8 = [f"{NAMES[k]} {v(math.sqrt(FC[k][i8]), 4, 2, 4)}% ({ann(FC[k][i8]):.2f}% a year)"
         for k in ("garch_n", "ewma", "roll60", "v_prev")]
anchor(9, "forecasts for 2025-04-08 made on 2025-04-07: " + "; ".join(case8) + f"; V on 2025-04-08 {V15[i8]:.4f} %^2 "
          f"(sqrt {v(math.sqrt(V15[i8]), 4, 2, 4)}%); r {v(y[i8], 4, 2, 4)}%")
pre = np.arange(i7 - 20, i7)
post = np.arange(i7, i7 + 20)
anchor(10, f"20 sessions to 2025-04-02 ({dates[pre[0]]}..): realized sqrt(A mean V) {v(ann(float(V15[pre].mean())), 2, 1)}%; "
           f"20 from 2025-04-07 (..{dates[post[-1]]}): {v(ann(float(V15[post].mean())), 2, 1)}%; GARCH normal forecasts "
           f"over those 20: {v(ann(float(FC['garch_n'][post].mean())), 2, 1)}%; EWMA "
           f"{v(ann(float(FC['ewma'][post].mean())), 2, 1)}%")

# ---------------------------------------------------------------- ARCH test
yc = y - y.mean()


def arch_test(x: np.ndarray, K: int) -> tuple[np.ndarray, float, float, float]:
    z = x[K:] ** 2
    X = np.column_stack([np.ones(len(x) - K)] + [x[K - j - 1 : len(x) - j - 1] ** 2 for j in range(K)])
    b, *_ = np.linalg.lstsq(X, z, rcond=None)
    e = z - X @ b
    r2 = 1 - float(e @ e) / float((z - z.mean()) @ (z - z.mean()))
    lm = (len(x) - K) * r2
    hh = het_arch(x, nlags=K, result_object=True)
    assert abs(hh.lm - lm) < 1e-6 * lm
    return b, r2, lm, float(stats.chi2.sf(lm, K))


b1, r21, lm1, p1 = arch_test(yc, 1)
anchor(11, f"K=1 on r - rbar (%): a {v(b1[0], 4, 4)}, b_1 {v(b1[1], 4, 3, 4)}, R-squared {r21:.5f}, LM (T-1)R2 "
           f"{v(lm1, 2, 1)}, p {sci_a(p1, 3, 1)} (LM19's rho_hat_1(r^2) 0.194, A19-40)")
b5, r25, lm5, p5 = arch_test(yc, 5)
anchor(12, f"K=5: a {b5[0]:.4f}, b_1..b_5 {', '.join(f'{x:.4f}' for x in b5[1:])}, sum b {v(float(b5[1:].sum()), 4, 3)}, "
           f"R-squared {v(r25, 5, 3)}, LM {v(lm5, 2, 0, 1)}, p {sci_a(p5, 3, 1)}; chi2_5 5% point "
           f"{v(float(stats.chi2.ppf(0.95, 5)), 4, 2)}")
_, r2x, lmx, px = arch_test(xin - xin.mean(), 5)
anchor(13, f"K=5 on GARCH-normal standardized residuals: R-squared {r2x:.5f}, LM {v(lmx, 2, 1)}, p {v(px, 4, 2, 3)}")

# ---------------------------------------------------------------- EWMA
wts = (1 - LAM) * LAM ** np.arange(10000)
anchor(14, f"weights sum {wts.sum():.10f}; effective window 1/(1-lam) {v(1 / (1 - LAM), 4, 1)}; mean lag lam/(1-lam) "
           f"{LAM / (1 - LAM):.4f}; weight half-life ln(1/2)/ln(lam) {v(math.log(0.5) / math.log(LAM), 4, 1)} days; weight "
           f"on the last 75 days {v(100 * (1 - LAM**75), 4, 1)}%; lam^75 {LAM**75:.5f}")
anchor(15, f"start sigma^2 = mean r^2 of the first 246 returns {v(ew[0], 4, 2)} %^2; lam^1231 {sci_a(LAM**1231, 3, 0)} "
           f"(first OOS day)")
s_a, s_b = math.sqrt(ew[i7]), math.sqrt(ew[i8])
assert abs(LAM * ew[i7] + (1 - LAM) * y[i7] ** 2 - ew[i8]) < 1e-12
anchor(16, f"sigma for 2025-04-07 {v(s_a, 4, 2, 3, 4)}% ({v(ew[i7], 4, 4)} %^2); for 2025-04-08 {v(s_b, 4, 2, 3, 4)}% = "
           f"sqrt(0.94 x {ew[i7]:.4f} + 0.06 x {y[i7] ** 2:.4f}) = sqrt({v(0.94 * ew[i7], 4, 4)} + "
           f"{v(0.06 * y[i7] ** 2, 4, 4)}); from the printed 1.560 and -10.203: "
           f"{math.sqrt(0.94 * 1.560**2 + 0.06 * 10.203**2):.4f}")
lams = np.round(np.arange(0.800, 0.9951, 0.005), 3)
hV = V15[oos]
qv_arr = np.array([float(qlike(hV, C.ewma_path(float(lam))[oos]).mean()) for lam in lams])
ib = int(qv_arr.argmin())
q_garch = float(qlike(hV, FC["garch_n"][oos]).mean())
anchor(17, f"QLIKE of EWMA r^2 on the OOS days against V, lam = 0.800..0.995 (step 0.005): best lam {lams[ib]:.3f} QLIKE "
           f"{v(float(qv_arr[ib]), 4, 4)}; lam 0.94 {v(float(qv_arr[list(lams).index(0.94)]), 4, 4)}; lam 0.97 "
           f"{v(float(qv_arr[list(lams).index(0.97)]), 4, 4)}; lam 0.80 {qv_arr[0]:.4f}; GARCH normal {v(q_garch, 4, 4)}")

# ---------------------------------------------------------------- GARCH
sen, ser = gn_c.std_err.to_numpy(), gn.std_err.to_numpy()
anchor(18, "GARCH normal, full TR23: " + ", ".join(f"{nm} {v(pv, 6, 4)} (classic {v(sc, 6, 4)}, robust {v(sr, 6, 4)})"
                                                   for nm, pv, sc, sr in zip(("g", "omega", "alpha", "beta"), pn, sen, ser))
       + f"; loglik {v(gn.loglikelihood, 4, 2)}")
anchor(19, f"backcast {v(bc_full, 6, 2)} %^2; hand loglik {ll_hand:.6f}, minus arch {ll_hand - gn.loglikelihood:.2e}; "
           f"max |sigma^2 hand - arch| {np.max(np.abs(s2_hand[:T] - cvn**2)):.1e}")
pers, uvar = FF["pers"], FF["uvar"]
anchor(20, f"alpha+beta {v(pers, 6, 5, 6)}; unconditional variance omega/(1-alpha-beta) {v(uvar, 6, 3, 4)} %^2 (sigma "
           f"{v(math.sqrt(uvar), 6, 3)}% a day); annualized {v(ann(uvar), 4, 2)}%; TR23's sqrt(A) s_r 18.99% (LM19, A19-54)")


def hl_delta(p: np.ndarray, cov: np.ndarray) -> tuple[float, float]:
    ps = p[2] + p[3]
    grad = -math.log(0.5) / (ps * math.log(ps) ** 2)
    return half_life(ps), math.sqrt(grad**2 * (cov[2, 2] + cov[3, 3] + 2 * cov[2, 3]))


hl_n, se_hl_c = hl_delta(pn, gn_c.param_cov.to_numpy())
_, se_hl_r = hl_delta(pn, gn.param_cov.to_numpy())
covr, covc = gn.param_cov.to_numpy(), gn_c.param_cov.to_numpy()
se_pers_r = math.sqrt(covr[2, 2] + covr[3, 3] + 2 * covr[2, 3])
se_pers_c = math.sqrt(covc[2, 2] + covc[3, 3] + 2 * covc[2, 3])
z975 = float(stats.norm.ppf(0.975))
lo_p, hi_p = pers - z975 * se_pers_r, pers + z975 * se_pers_r
anchor(21, f"half-life ln(1/2)/ln(alpha+beta) {v(hl_n, 4, 1)} sessions; delta-method SE classic {v(se_hl_c, 4, 1)}, robust "
           f"{v(se_hl_r, 4, 1)}; robust delta interval {v(hl_n - z975 * se_hl_r, 2, 0)} to {v(hl_n + z975 * se_hl_r, 2, 0)}; "
           f"SE(alpha+beta) classic {se_pers_c:.5f}, robust {v(se_pers_r, 5, 4)}; robust interval for alpha+beta "
           f"{v(lo_p, 5, 5)} to {v(hi_p, 5, 5)}, mapped to half-lives {v(half_life(lo_p), 2, 0)} to {v(half_life(hi_p), 2, 0)}")
stc, strr = gt_c.std_err.to_numpy(), gt.std_err.to_numpy()
pers_t = float(pt[2] + pt[3])
hl_t, se_hlt = hl_delta(pt, gt.param_cov.to_numpy())
uvar_t = float(pt[1] / (1 - pers_t))
anchor(22, "GARCH t, full TR23: " + ", ".join(f"{nm} {v(pv, 6, d)} (classic {v(sc, 6, d)}, robust {v(sr, 6, d)})"
                                              for nm, d, pv, sc, sr in zip(("g", "omega", "alpha", "beta", "nu"),
                                                                           (4, 4, 4, 4, 2), pt, stc, strr))
       + f"; loglik {v(gt.loglikelihood, 4, 2)}; ell gain {v(gt.loglikelihood - gn.loglikelihood, 2, 2)}; alpha+beta "
       f"{v(pers_t, 6, 5)}; half-life {v(hl_t, 4, 1)} (robust SE {se_hlt:.2f}); unconditional variance "
       f"{v(uvar_t, 6, 3)} %^2, annualized {v(ann(uvar_t), 2, 2)}%")
MOM: dict[str, tuple[float, float]] = {}
moments = []
for nm, x in (("xi normal", xin), ("xi t", xit), ("r", y)):
    xc = x - x.mean()
    sk = float((xc**3).mean() / (xc**2).mean() ** 1.5)
    ku = float((xc**4).mean() / (xc**2).mean() ** 2 - 3)
    MOM[nm] = (sk, ku)
    moments.append(f"{nm}: mean {x.mean():.4f}, s {x.std():.4f}, skew {v(sk, 4, 2)}, excess kurtosis {v(ku, 4, 2)}")
anchor(23, "; ".join(moments) + " (divisor T, LM19's (19.3))")
lbn = acorr_ljungbox(np.abs(xin), lags=[10]).to_numpy()
lbt = acorr_ljungbox(np.abs(xit), lags=[10]).to_numpy()
lbr = acorr_ljungbox(np.abs(y), lags=[10]).to_numpy()
lbn2 = acorr_ljungbox(xin**2, lags=[10]).to_numpy()
anchor(24, f"Q_LB(10) |xi| normal {v(lbn[0, 0], 2, 1)} p {v(lbn[0, 1], 4, 3)}; |xi| t {v(lbt[0, 0], 2, 1)} p {lbt[0, 1]:.4f}; "
           f"xi^2 normal {lbn2[0, 0]:.2f} p {lbn2[0, 1]:.4f}; |r| {v(lbr[0, 0], 2, 0)} (LM25's 1,820, A25-22); chi2_10 5% "
           f"point {stats.chi2.ppf(0.95, 10):.4f}")
den4 = 1 - pers**2 - 2 * pn[2] ** 2
kurt_n = 3 * (1 - pers**2) / den4
kxi = 3 * (pt[4] - 2) / (pt[4] - 4)
cond_t = pers_t**2 + (kxi - 1) * pt[2] ** 2
anchor(25, f"normal GARCH: 1-(a+b)^2-2a^2 {den4:.6f}; Kurt 3(1-(a+b)^2)/(...) {v(kurt_n, 4, 2)}, excess "
           f"{v(kurt_n - 3, 4, 2)}; t GARCH: Kurt(xi) 3(nu-2)/(nu-4) {v(kxi, 4, 2)}; (a+b)^2+(Kurt(xi)-1)a^2 "
           f"{v(cond_t, 6, 3)} (>= 1: no finite fourth moment)")
s2_7 = s2_hand[i7 + 1]
assert abs(s2_7 - (pn[1] + pn[2] * (y[i7] - pn[0]) ** 2 + pn[3] * cvn[i7] ** 2)) < 1e-12
fcarch = gn.forecast(horizon=250, start=i7, reindex=False).variance.to_numpy()[0]
p7 = C.term(s2_7, pers, uvar)
fc_diff = float(np.max(np.abs(p7 - fcarch)))
assert fc_diff < 1e-12
P26_M = {1: (3,), 5: (2,), 20: (2, 3), 44: (2,), 60: (2,), 250: (2,)}
P26_AVG = {1: (2,), 20: (2, 1), 250: (2, 1)}
anchor(26, f"from 2025-04-07 (full-sample normal fit): sigma_t {v(float(cvn[i7]), 4, 3)}%, sigma_t+1|t "
           f"{v(math.sqrt(s2_7), 4, 3)}% ({v(s2_7, 4, 4)} %^2); "
           + ", ".join(f"m={m}: {v(math.sqrt(p7[m - 1]), 4, *d)}%" for m, d in P26_M.items())
           + "; annualized average over m days: " + ", ".join(f"m={m} {v(ann(float(p7[:m].mean())), 2, *d)}%"
                                                             for m, d in P26_AVG.items())
           + f"; arch forecast equal (max diff {fc_diff:.0e})")
s2_T = s2_hand[T]
pT = C.term(s2_T, pers, uvar)
anchor(27, f"from 2026-10-08: sigma_T+1|T {v(math.sqrt(s2_T), 4, 3)}% ({s2_T:.4f} %^2, {v(ann(s2_T), 2, 2)}% a year); "
           f"m=250: {math.sqrt(pT[-1]):.4f}%; annualized average over 20 days {v(ann(float(pT[:20].mean())), 2, 2)}%, "
           f"250 days {v(ann(float(pT.mean())), 2, 2)}%; unconditional {v(ann(uvar), 2, 2)}%")
anchor(28, f"widget initial state: alpha {v(pn[2], 4, 4)}, beta {v(pn[3], 4, 4)}, unconditional variance {v(uvar, 4, 4)} "
           f"%^2 ({v(ann(uvar), 2, 2)}% a year), start {v(math.sqrt(s2_7), 3, 3)}% (after 2025-04-07) or "
           f"{v(math.sqrt(s2_T), 3, 3)}% (2026-10-08); half-life {v(hl_n, 1, 1)}")
fall = R <= -0.03 + EPS
rise = R > 0.03 + EPS
idf = np.flatnonzero(fall[:-1])
idr = np.flatnonzero(rise[:-1])
snext = np.sqrt(s2_hand[1 : T + 1])
zthr = (100 * math.log(0.97) - pn[0]) / snext
Femp = np.searchsorted(np.sort(xin), zthr, side="right") / T
Fnor = stats.norm.cdf(zthr)
anchor(29, f"observed: {len(idf)} falls of 3% or more, {int(fall[idf + 1].sum())} followed by a fall; {len(idr)} rises "
           f"above 3%, {int(fall[idr + 1].sum())} followed by a fall; {int(fall[1:].sum())} falls on days 2..T. GARCH "
           f"normal, xi's own distribution: expected {v(float(Femp[idf].sum()), 2, 1)} after falls ({Femp[idf].mean():.4f}), "
           f"{v(float(Femp[idr].sum()), 2, 1)} after rises ({Femp[idr].mean():.4f}), {v(float(Femp[:-1].sum()), 1, 1)} on all "
           f"days ({Femp[:-1].mean():.4f}); normal xi: {Fnor[idf].sum():.2f}, {Fnor[idr].sum():.2f}, {Fnor[:-1].sum():.1f}")
_, mi = np.unique(np.array(month), return_inverse=True)
nm_ = int(mi.max()) + 1
big = np.abs(R) >= 0.03 - EPS
cnt = np.bincount(mi, weights=big.astype(float), minlength=nm_)
obs_disp = float(cnt.var() / cnt.mean())
SIM: dict[int, dict[str, float]] = {}


def simulate(e: int, p: np.ndarray, dist: str, pr: dict[str, tuple[int, ...]]) -> str:
    """Experiment e (AUTHORING section 8): 1,000 paths of T days, sigma^2 started at the unconditional variance, each
    day one vector of 1,000 innovations (element k for path k); medians with LM18's batch standard error."""
    rng = np.random.default_rng([e, SEED])
    npath = 1000
    g, om, al, be = p[:4]
    s2 = np.full(npath, om / (1 - al - be))
    ys = np.empty((npath, T))
    for t in range(T):
        if dist == "normal":
            xi = rng.standard_normal(npath)
        else:
            xi = rng.standard_t(p[4], npath) * math.sqrt((p[4] - 2) / p[4])
        eps = np.sqrt(s2) * xi
        ys[:, t] = g + eps
        s2 = om + al * eps**2 + be * s2
    Rs = np.expm1(ys / 100)
    disp = np.empty(npath)
    for k in range(npath):
        c = np.bincount(mi, weights=(np.abs(Rs[k]) >= 0.03 - EPS).astype(float), minlength=nm_)
        disp[k] = c.var() / c.mean()
    yc_ = ys - ys.mean(axis=1, keepdims=True)
    kurt = (yc_**4).mean(axis=1) / (yc_**2).mean(axis=1) ** 2 - 3
    SIM[e] = {"disp_med": qinv(disp, 0.5), "disp_se": batch_se_median(disp), "disp_q05": qinv(disp, 0.05),
              "disp_q95": qinv(disp, 0.95), "kurt_med": qinv(kurt, 0.5), "kurt_se": batch_se_median(kurt),
              "kurt_share": float(np.mean(kurt >= 5.428))}
    return (f"dispersion median {v(qinv(disp, 0.5), 4, *pr['disp_med'])} (batch SE {v(batch_se_median(disp), 4, 3)}), 5% "
            f"{v(qinv(disp, 0.05), 6, *pr['disp_q'])}, 95% {v(qinv(disp, 0.95), 6, *pr['disp_q'])}, share >= observed "
            f"{v(float(np.mean(disp >= obs_disp - 1e-12)), 3, *pr['disp_share'])}; excess kurtosis median "
            f"{v(qinv(kurt, 0.5), 3, *pr['kurt_med'])} (batch SE {v(batch_se_median(kurt), 3, 3)}), 5% "
            f"{v(qinv(kurt, 0.05), 3, *pr['kurt_q'])}, 95% {v(qinv(kurt, 0.95), 3, *pr['kurt_q'])}, share >= 5.428 "
            f"{v(float(np.mean(kurt >= 5.428)), 3, *pr['kurt_share'])}")


anchor(30, f"observed months {nm_}, monthly count variance/mean {v(obs_disp, 4, 2)} (LM15's 3.02); experiment 1 (GARCH "
           f"normal, 1,000 paths): " + simulate(1, pn, "normal", {"disp_med": (2,), "disp_q": (2,), "disp_share": (2,),
                                                                 "kurt_med": (2,), "kurt_q": (), "kurt_share": (3,)}))
anchor(31, "experiment 2 (GARCH t, 1,000 paths): " + simulate(2, pt, "t", {"disp_med": (2,), "disp_q": (), "disp_share": (),
                                                                            "kurt_med": (1,), "kurt_q": (1,),
                                                                            "kurt_share": (2,)}))

# ---------------------------------------------------------------- realized variance (file)
d_arr = np.array(rv_dates)
periods = {
    "2005-2010": (d_arr >= "2005-01-01") & (d_arr <= "2010-12-31"),
    "2011-01-17..2012": (d_arr >= "2011-01-17") & (d_arr <= "2012-12-31"),
    "2015-2026": (d_arr >= "2015-01-01"),
    "2025": ryear == "2025",
}
SIG: dict[str, dict[str, float]] = {}
lines = []
for pname, msk in periods.items():
    m5 = float(np.mean(RV["5m"][msk]))
    ratios = {name: float(np.mean(RV[name][msk])) / m5 for name, _ in IV if not np.isnan(RV[name][msk]).any()}
    SIG[pname] = ratios
    prec = {"2025": {"5s": (1, 2), "15s": (3,)}}.get(pname, {})
    lines.append(f"{pname} ({int(msk.sum())} days): " + ", ".join(
        f"{k} {v(val, 6, *prec.get(k, (2,) if val >= 10 else (3,)))}" for k, val in ratios.items()))
anchor(32, "mean RV(h)/mean RV(5m): " + "; ".join(lines))
lines = []
for s_ in (60, 15, 10, 5):
    msk = reg == s_
    m5 = float(np.mean(RV["5m"][msk]))
    lines.append(f"{s_}s: " + ", ".join(f"{name} {float(np.mean(RV[name][msk])) / m5:.3f}" for name, _ in IV
                                        if not np.isnan(RV[name][msk]).any()))
anchor(33, "by sampling regime (check rows): " + "; ".join(lines))
m5s, m15 = reg == 5, reg == 15
m25 = ryear == "2025"
vr5 = float(np.mean(RV["10s"][m5s]) / np.mean(RV["5s"][m5s]) - 1)
vr15 = float(np.mean(RV["30s"][m15]) / np.mean(RV["15s"][m15]) - 1)
vr5m = float(np.mean(RV["10m"]) / np.mean(RV["5m"]) - 1)
YEARS = sorted(set(ryear))
R1_5 = {yy: float(np.mean(RV["1m"][ryear == yy]) / np.mean(RV["5m"][ryear == yy])) for yy in YEARS}
R10_5 = {yy: float(np.mean(RV["10m"][ryear == yy]) / np.mean(RV["5m"][ryear == yy]) - 1) for yy in YEARS}

# ---------------------------------------------------------------- raw downloads (anchors 34-42)
PA = C.raw5()
TX = C.tx25()
R1 = {}
if PA is not None and TX is not None:
    r5 = C.pooled(PA, m5s, "f")
    r15 = C.pooled(PA, m15, "f")
    r5m = C.pooled(PA, np.ones(len(rv_dates), bool), "m5")
    anchor(34, f"pooled rho_1 (raw) against RV(2h)/RV(h) - 1 (file): 5 s, 5-second days {v(r5, 4, 3)} vs {v(vr5, 4, 3)}; "
               f"15 s, 15-second days {v(r15, 4, 4)} vs {v(vr15, 4, 3)}; 5 min, all days {v(r5m, 4, 3)} vs {v(vr5m, 4, 3)}")
    yr_lines = []
    maxdiff = 0.0
    for yy in YEARS:
        msk = ryear == yy
        a1, a5 = C.pooled(PA, msk, "m1"), C.pooled(PA, msk, "m5")
        maxdiff = max(maxdiff, abs(a1 - C.pooled(PA, msk, "m1", True)), abs(a5 - C.pooled(PA, msk, "m5", True)))
        R1[yy] = a1
        yr_lines.append(f"{yy} {v(a1, 4, 2, 3)} / {v(a5, 4, 2, 3)} / {v(R1_5[yy], 3, 3)}")
    anchor(35, "by year, rho_1 of 1-minute / 5-minute returns (raw, uncentred, pooled) / RV(1m)/RV(5m) (file): "
               + "; ".join(yr_lines) + f"; max |uncentred - centred| {maxdiff:.1e}; iid SE of a year's 1-minute rho_1 "
               f"1/sqrt(240 x 246) {v(1 / math.sqrt(240 * 246), 4, 3)}")
    rd = PA["rho1_day"][m25]
    ratio_day = RV["5s"][m25] / RV["5m"][m25]
    p25 = C.pooled(PA, m25, "f")
    anchor(36, f"2025, each day's rho_1 of 5-second returns (own mean, divisor n): min {v(float(rd.min()), 4, 2)}, 25% "
               f"{v(qinv(rd, 0.25), 4, 2)}, median {v(qinv(rd, 0.5), 4, 2)}, 75% {v(qinv(rd, 0.75), 4, 2)}, max "
               f"{v(float(rd.max()), 4, 2)} ({int(m25.sum())} days); RV(5s)/RV(5m) per day: median "
               f"{v(qinv(ratio_day, 0.5), 2, 1)}, max {v(float(ratio_day.max()), 2, 1)} "
               f"({rv_dates[int(np.flatnonzero(m25)[ratio_day.argmax()])]}); pooled 2025 rho_1 {v(p25, 4, 3)}")
    anchor(37, f"MA(1) noise reading, -rho_1 = sigma_u^2/(var e + 2 sigma_u^2) <= 1/2: noise share 2|rho_1| of a "
               f"5-second return's variance: 2025 {v(2 * abs(p25), 4, 2)}, 5-second days {2 * abs(r5):.4f}")
    noise = []
    for yy in [str(x) for x in range(2015, 2027)]:
        msk = ryear == yy
        g1 = PA["f_p1"][msk].sum() / PA["f_n"][msk].sum()
        noise.append(f"{yy} {v(1e4 * math.sqrt(-g1), 3, 1, 3)}")
    anchor(38, "sqrt(-gamma_1) of 5-second log returns, bp (pooled, uncentred; check rows): " + ", ".join(noise))
    anchor(39, f"TX near month 2025: {len(TX['days'])} days; first label {sorted(TX['first_lab'])}; last label counts "
               f"{dict(sorted(TX['last_lab'].items()))}; bars a day {dict(sorted(TX['nbar'].items()))}; last bar's close = "
               f"daily close on {TX['eq']} of {len(TX['days'])}; minutes without a bar in 09:29-13:29: "
               f"{dict(TX['miss_days'])}")
    TXA = TX["RV"]
    keep = np.array([d not in TX["miss_days"] for d in TX["days"]])
    txr = ", ".join(f"{h}m {v(float(TXA[h].mean() / TXA[5].mean()), 4, 2)}" for h in (1, 10, 15, 30))
    txr_k = ", ".join(f"{h}m {float(TXA[h][keep].mean() / TXA[5][keep].mean()):.4f}" for h in (1, 10, 15, 30))
    anchor(40, f"TX 2025 mean RV(h)/RV(5m): {txr}; without the {len(TX['miss_days'])} locked days: {txr_k}; pooled rho_1 "
               f"of 1-minute returns {v(TX['rho1'], 4, 3)}; annualized sqrt(A mean RV): "
               + ", ".join(f"{h}m {v(100 * math.sqrt(A * float(TXA[h].mean())), 4, 1, 2)}%" for h in (1, 5, 10, 15, 30)))
    assert [rv_dates[i] for i in np.flatnonzero(m25)] == TX["days"]
    ixv = ", ".join(f"{name} {v(100 * math.sqrt(A * float(np.mean(RV[name][m25]))), 4, 1, 2)}%" for name, _ in IV)
    rat = ", ".join(f"{name} {v(float(np.mean(RV[name][m25])) / float(TXA[h].mean()), 3, 2)}" for name, h in
                    (("1m", 1), ("5m", 5), ("10m", 10), ("15m", 15), ("30m", 30)))
    anchor(41, f"TAIEX 2025 annualized sqrt(A mean RV(h)): {ixv}; index/TX mean RV: {rat}; TAIEX 2025 pooled rho_1 of "
               f"1-minute returns {v(R1['2025'], 4, 3)}")
    aus = []
    for s_ in (60, 15, 10, 5):
        msk = reg == s_
        aus.append(f"{s_}s: frozen on {int(PA['frozen_all'][msk].sum())} of {int(msk.sum())} days, share of RV(5m) "
                   f"{v(float(PA['auct2'][msk].mean() / np.mean(RV['5m'][msk])), 4, 3)}")
    anchor(42, "closing auction (values from 13:25:00 + one step to 13:30:00 - one step all equal; (ln P_13:30 - ln "
               "P_13:25)^2 over mean RV(5m), against 1/48 = 0.0208): " + "; ".join(aus))
else:
    for nn in range(34, 43):
        skip(nn)
mo = np.isin(np.array(rv_dates), [dates[i] for i in oos])
anchor(43, f"o2 share of V: mean 1e4 o2 / mean V, all {len(rv_dates)} days "
           f"{v(float(np.mean(1e4 * O2) / np.mean(Vt['15m'])), 4, 2)}, OOS days "
           f"{v(float(np.mean(1e4 * O2[mo]) / np.mean(Vt['15m'][mo])), 4, 2)}; " +
           ", ".join(f"{s_}s {float(np.mean(O2[reg == s_]) / np.mean(O2[reg == s_] + RV['15m'][reg == s_])):.4f}"
                     for s_ in (60, 15, 10, 5)))
y2 = y[i05:] ** 2
dV = Vt["15m"] - y2
nl_all = nw_lags(len(dV))
y2o = y[oos] ** 2
dVo = V15[oos] - y2o
t_vr2 = float(dV.mean() / nw_se(dV, nl_all))
anchor(44, f"mean V {np.mean(Vt['15m']):.4f} vs mean r^2 {np.mean(y2):.4f} %^2 over the 5,351 days: ratio "
           f"{v(float(np.mean(Vt['15m']) / np.mean(y2)), 4, 3)}, difference t-stat (Newey-West, {nl_all} lags) "
           f"{v(t_vr2, 2, 2)}; OOS days ratio {v(float(V15[oos].mean() / y2o.mean()), 4, 3)}, t "
           f"{dVo.mean() / nw_se(dVo, 9):.2f}; V(5m) ratio {np.mean(Vt['5m']) / np.mean(y2):.4f}, V(30m) "
           f"{np.mean(Vt['30m']) / np.mean(y2):.4f}; by year V/r^2: " +
           ", ".join(f"{yy} {v(float(np.mean(Vt['15m'][ryear == yy]) / np.mean(y2[ryear == yy])), 3, *d)}"
                     for yy, d in (("2008", (3,)), ("2020", ()), ("2024", ()), ("2025", (3,)))))

# ---------------------------------------------------------------- forecast evaluation
nl = nw_lags(len(oos))
anchor(45, f"W {W} = round(5A); first OOS day {dates[first]} (window {dates[first - W]} .. {dates[first - 1]}); OOS days "
           f"{len(oos)} ({dates[oos[0]]} .. {dates[oos[-1]]}); refits per model {len(refits['normal'])}; Newey-West lags {nl}")
pr_ = np.array([p for _, p in refits["normal"]])
apr = next(p for d_, p in refits["normal"] if d_ == "2025-04-01")
pab = pr_[:, 2] + pr_[:, 3]
anchor(46, f"rolling GARCH normal: alpha {v(float(pr_[:, 2].min()), 4, 3)}..{v(float(pr_[:, 2].max()), 4, 3)}, beta "
           f"{v(float(pr_[:, 3].min()), 4, 3)}..{v(float(pr_[:, 3].max()), 4, 3)}, alpha+beta {v(float(pab.min()), 4, 3)}.."
           f"{v(float(pab.max()), 4, 3)}; refit of 2025-04-01: g {apr[0]:.4f}, "
           f"omega {apr[1]:.4f}, alpha {apr[2]:.4f}, beta {apr[3]:.4f}, alpha+beta {apr[2] + apr[3]:.4f}")
targets = {"V15": V15[oos], "V5": np.array([Vmap["5m"][dates[i]] for i in oos]),
           "V30": np.array([Vmap["30m"][dates[i]] for i in oos]), "r2": y[oos] ** 2}
X7: dict[str, dict[str, float]] = {}
tab = []
for k in FC:
    f = FC[k][oos]
    h = targets["V15"]
    X = np.column_stack([np.ones(len(f)), f])
    bmz, semz, r2mz = ols_hc0(X, h)
    chkm = sm.OLS(h, X).fit(cov_type="HC0")
    assert np.allclose(chkm.bse, semz, rtol=1e-9)
    X7[k] = {"mean": float(f.mean()), "mse": float(((h - f) ** 2).mean()), "qlike": float(qlike(h, f).mean()),
             "a": float(bmz[0]), "a_se": float(semz[0]), "b": float(bmz[1]), "b_se": float(semz[1]),
             "tb": float((bmz[1] - 1) / semz[1]), "r2": r2mz}
    tab.append(f"{NAMES[k]}: mean f {v(X7[k]['mean'], 6, 3)}, MSE {v(X7[k]['mse'], 3, 2)}, QLIKE {v(X7[k]['qlike'], 4, 4)}, "
               f"a {bmz[0]:.3f} ({semz[0]:.3f}), b {v(float(bmz[1]), 3, 3)} ({v(float(semz[1]), 3, 3)}), t(b=1) "
               f"{(bmz[1] - 1) / semz[1]:.2f}, R-squared {v(r2mz, 4, 3)}")
anchor(47, f"target V (mean {v(float(targets['V15'].mean()), 4, 3)} %^2): " + "; ".join(tab))
LD: dict[tuple[str, str], dict[str, float]] = {}
dl = []
for k in ("garch_t", "ewma", "roll60", "v_prev", "ewma_v"):
    for lname in ("MSE", "QLIKE"):
        h = targets["V15"]
        if lname == "MSE":
            d = (h - FC[k][oos]) ** 2 - (h - FC["garch_n"][oos]) ** 2
        else:
            d = qlike(h, FC[k][oos]) - qlike(h, FC["garch_n"][oos])
        se_nw = nw_se(d, nl)
        if k == "ewma" and lname == "QLIKE":
            hac = sm.OLS(d, np.ones(len(d))).fit(cov_type="HAC", cov_kwds={"maxlags": nl})
            assert abs(float(hac.bse[0]) - se_nw) < 1e-10 * se_nw
        tt = float(d.mean() / se_nw)
        pval = float(2 * stats.norm.sf(abs(tt)))
        LD[(k, lname)] = {"mean": float(d.mean()), "t": tt, "p": pval}
        p_mean = ((4,) if lname == "QLIKE" else (3,)) if k == "ewma" else ()
        p_p = (3,) if (k, lname) == ("ewma", "QLIKE") else ()
        dl.append(f"{NAMES[k]} {lname} {v(float(d.mean()), 4, *p_mean, sign=True)} (SE {se_nw:.4f}, t {v(tt, 2, 2)}, p "
                  f"{v(pval, 4, *p_p)})")
anchor(48, "loss minus GARCH normal's, V target: " + "; ".join(dl))
ORDERS: dict[str, list[str]] = {}
rob = []
for tg in ("V5", "V30", "r2"):
    h = targets[tg]
    ql_ = {k: float(qlike(h, FC[k][oos]).mean()) for k in FC}
    ms_ = {k: float(((h - FC[k][oos]) ** 2).mean()) for k in FC}
    order_q = sorted(FC, key=lambda k: ql_[k])
    order_m = sorted(FC, key=lambda k: ms_[k])
    ORDERS[tg] = order_q
    rob.append(f"{tg}: QLIKE order {', '.join(NAMES[k] for k in order_q)} ({ql_[order_q[0]]:.4f} .. "
               f"{ql_[order_q[-1]]:.4f}); MSE order {', '.join(NAMES[k] for k in order_m)}")
order_v = sorted(FC, key=lambda k: float(qlike(targets["V15"], FC[k][oos]).mean()))
ORDERS["V15"] = order_v
anchor(49, f"V target QLIKE order {', '.join(NAMES[k] for k in order_v)}; " + "; ".join(rob))
MZ: dict[str, dict[str, float]] = {}
mzr = []
for tg in ("V15", "r2"):
    X = np.column_stack([np.ones(len(oos)), FC["garch_n"][oos]])
    bmz, semz, r2mz = ols_hc0(X, targets[tg])
    MZ[tg] = {"a": float(bmz[0]), "a_se": float(semz[0]), "b": float(bmz[1]), "b_se": float(semz[1]),
              "t": float((bmz[1] - 1) / semz[1]), "r2": r2mz}
    d3, d2 = ((3,), (2,)) if tg == "V15" else ((), ())
    mzr.append(f"{tg}: a {v(float(bmz[0]), 4, *d3)} ({v(float(semz[0]), 4, *d3)}), b {v(float(bmz[1]), 4, *d3)} "
               f"({v(float(semz[1]), 4, *d3)}), t(b=1) {v(float((bmz[1] - 1) / semz[1]), 2, *d2)}, R-squared {v(r2mz, 4, 3)}")
anchor(50, "Mincer-Zarnowitz, GARCH normal (HC0): " + "; ".join(mzr) + "; Andersen-Bollerslev's 0.047 and 0.026 against "
           "squared returns (SOURCES)")
oy = np.array([dates[i][:4] for i in oos])
BY: dict[str, tuple[float, float, float]] = {}
by = []
win_e = 0
for yy in sorted(set(oy)):
    msk = oy == yy
    qn = float(qlike(targets["V15"][msk], FC["garch_n"][oos][msk]).mean())
    qe = float(qlike(targets["V15"][msk], FC["ewma"][oos][msk]).mean())
    qp = float(qlike(targets["V15"][msk], FC["v_prev"][oos][msk]).mean())
    BY[yy] = (qn, qe, qp)
    win_e += int(qn < qe)
    by.append(f"{yy} ({int(msk.sum())}) {v(qn, 4, 3)} / {v(qe, 4, 3)} / {v(qp, 4, 3)}")
anchor(51, "QLIKE by year, GARCH normal / EWMA / yesterday's V: " + "; ".join(by) + f"; GARCH normal below EWMA in "
           f"{win_e} of {len(set(oy))} years")
w25 = sorted({iso[i] for i in oos if dates[i].startswith("2025")})
wk = []
for w_ in w25:
    ids = [i for i in oos if iso[i] == w_ and dates[i].startswith("2025")]
    wk.append((dates[ids[-1]], ids))
i_w = next(j for j, (_, ids) in enumerate(wk) if i7 in ids)
_, ids7 = wk[i_w]
ids25 = [i for _, ids in wk for i in ids]
own25 = sum(1 for w_ in w25 if w_[0] == 2025)
other25 = "".join(f" and {w_[0]}-W{w_[1]:02d} ({dates[ids[0]]}..{dates[ids[-1]]})" for w_, (_, ids) in zip(w25, wk)
                  if w_[0] != 2025)
W7 = {k: ann(float(FC[k][ids7].mean())) for k in ("garch_n", "ewma", "v_prev")}
W7["real"] = ann(float(V15[ids7].mean()))
real25 = ann(float(V15[ids25].mean()))
anchor(52, f"2025 weekly points: {len(wk)} weeks (the {len(ids25)} sessions dated 2025 by ISO week: {own25} weeks of ISO "
           f"year 2025{other25}); week of 2025-04-07 ({dates[ids7[0]]}..{dates[ids7[-1]]}, {len(ids7)} sessions): realized "
           f"sqrt(A mean V) {v(W7['real'], 2, 2)}%, GARCH normal {v(W7['garch_n'], 2, 2)}%, EWMA {v(W7['ewma'], 2, 2)}%, "
           f"yesterday's V {v(W7['v_prev'], 2, 2)}%; 2025 means: realized {v(real25, 2, 2)}%")
SENS: dict[int, tuple[float, float, float]] = {}
sens = []
for wv in (1000, 2461):
    rg2 = C.rolling_garch(wv)
    f0 = next(i for i in starts if i >= wv)
    o2_ = np.arange(f0, T)
    qn = float(qlike(V15[o2_], rg2["normal"][o2_]).mean())
    qt = float(qlike(V15[o2_], rg2["t"][o2_]).mean())
    qe = float(qlike(V15[o2_], ew[o2_]).mean())
    SENS[wv] = (qn, qt, qe)
    sens.append(f"W={wv}: first OOS {dates[f0]}, {len(o2_)} days, QLIKE normal {qn:.4f}, t {qt:.4f}, EWMA {qe:.4f}")
anchor(53, "; ".join(sens))
wkall: dict[tuple[int, int], list[int]] = {}
for i, w_ in enumerate(iso):
    wkall.setdefault(w_, []).append(i)
wends = [ids[-1] for ids in wkall.values()]
ig, ie = int(np.argmax(cvn)), int(np.argmax(ew[:T]))
extra = sorted({ig, ie} - set(wends))
real_w = [(ids[-1], ann(float(np.mean(V15[ids])))) for ids in wkall.values() if dates[ids[0]] >= "2005-01-03"]
jr = int(np.argmax([x for _, x in real_w]))
anchor(54, f"weekly chart: {len(wends)} ISO weeks (last session of each), plus {len(extra)} extreme dates; GARCH normal "
           f"sigma_t max {v(ann(float(cvn[ig] ** 2)), 2, 2)}% a year on {dates[ig]}; EWMA sigma_t|t-1 max "
           f"{v(ann(float(ew[ie])), 2, 2)}% on {dates[ie]}; weekly realized max {v(real_w[jr][1], 2, 2)}% (week ending "
           f"{dates[real_w[jr][0]]}); realized weeks {len(real_w)}")
k1 = [b1[0] + b1[1] * x**2 for x in (3.0, 0.5)]
k1p = [1.1779 + 0.1960 * x**2 for x in (3.0, 0.5)]
anchor(55, f"KC 2: ARCH(1) fit after |r - rbar| = 3% and 0.5%: {v(k1[0], 4, 2)} and {v(k1[1], 4, 2)} %^2 (sd "
           f"{v(math.sqrt(k1[0]), 4, 2)}%, {v(math.sqrt(k1[1]), 4, 2)}%); from the printed 1.1779 and 0.1960: "
           f"{v(k1p[0], 4, 2)}, {v(k1p[1], 4, 2)} (sd {v(math.sqrt(k1p[0]), 4, 2)}%, {v(math.sqrt(k1p[1]), 4, 2)}%)")
anchor(56, f"lam 0.97: 1/(1-lam) {v(1 / 0.03, 4, 1)}; mean lag lam/(1-lam) {v(0.97 / 0.03, 4, 1)}; weight half-life "
           f"{v(math.log(0.5) / math.log(0.97), 4, 1, 2)} days")
anchor(57, f"alpha+beta 0.98: half-life {v(half_life(0.98), 4, 1)}; 0.5/(1-0.98) {0.5 / 0.02:.1f}; 1/(1-0.98) "
           f"{1 / 0.02:.1f}; alpha+beta 0.990978 (t fit): {v(half_life(0.990978), 2, 1)}")
anchor(58, f"QLIKE at f = V/2: {v(2 - math.log(2) - 1, 4, 4)}; at f = 2V: {v(0.5 + math.log(2) - 1, 4, 4)}; MSE with V = 1: "
           f"{(1 - 0.5) ** 2:.2f} and {(1 - 2) ** 2:.2f}")
u2 = 0.025 / (1 - 0.09 - 0.89)
u2b = 0.025 / (1 - 0.89)
anchor(59, f"Problem 2: omega/(1-alpha-beta) {u2:.4f} %^2, annualized sqrt(246.12 x) {v(math.sqrt(246.12 * u2), 4, 1)}%; "
           f"omega/(1-beta) {u2b:.4f} %^2 -> {v(math.sqrt(246.12 * u2b), 4, 1)}%; sqrt(1.25) {v(math.sqrt(u2), 4, 2)}% (a day)")
anchor(60, f"Problem 5: 1 + rho_1 with rho_1 = -0.40: {1 - 0.40:.2f}; 1 + 2 rho_1 {1 - 0.80:.2f}; 1 - rho_1 {1 + 0.40:.2f}")
if PA is not None:
    anchor(61, f"KC 6: 15-second days, RV(30s)/RV(15s) = {v(float(np.mean(RV['30s'][m15]) / np.mean(RV['15s'][m15])), 4, 4)} "
               f"(file); 1 + pooled rho_1 (raw) {1 + C.pooled(PA, m15, 'f'):.4f}")
else:
    skip(61)
anchor(62, f"KC 5: robust/classic SE ratio: alpha {v(ser[2] / sen[2], 3, 2, 1)}, beta {v(ser[3] / sen[3], 3, 1)}, omega "
           f"{v(ser[1] / sen[1], 3, 1)}, g {ser[0] / sen[0]:.3f}")
z5 = -4.107
xo = (y[oos] - np.array([next(p for d_, p in refits["normal"] if d_[:7] == dates[i][:7])[0] for i in oos])) / np.sqrt(
    FC["garch_n"][oos])
n_xi = int((xin <= z5 + EPS).sum())
n_s = int(((y - y.mean()) / y.std() <= z5 + EPS).sum())
anchor(63, f"standardized residuals at or below -4.107: in-sample GARCH normal {n_xi} of {T} (normal model expects "
           f"{v(float(T * stats.norm.cdf(z5)), 3, 3)}); raw returns standardized by TR23's s: {n_s}; out of sample "
           f"(rolling GARCH normal) {int((xo <= z5 + EPS).sum())} of {len(oos)} (expects {len(oos) * stats.norm.cdf(z5):.3f}); "
           f"smallest in-sample xi {xin.min():.3f} on {dates[int(xin.argmin())]}")
big2 = np.abs(R[:-1]) >= 0.02 - EPS
nxt = np.abs(R[1:])
exi = float(np.mean(np.abs(xin)))
pred = exi * snext[:-1] / 100
anchor(64, f"after |R| >= 2% ({int(big2.sum())} days): next-day mean |R| {v(100 * float(nxt[big2].mean()), 4, 2)}%, after the "
           f"others {v(100 * float(nxt[~big2].mean()), 4, 2)}%, all {nxt.mean():.4%}; GARCH normal mean |xi| {exi:.4f} x "
           f"sigma_t+1|t: {v(100 * float(pred[big2].mean()), 4, 2)}% and {v(100 * float(pred[~big2].mean()), 4, 2)}%; "
           f"rho_hat_1 of |r| 0.161 (LM17, lm17.md:392)")
ns = [14400 // h for _, h in IV[:6]]
mv = [float(np.mean(RV[name][m5s]) / np.mean(RV["5m"][m5s])) for name, _ in IV[:6]]
slopes = [(mv[j] - mv[j + 1]) / (ns[j] - ns[j + 1]) for j in range(5)]
anchor(65, "5-second days, rise of mean RV(h)/RV(5m) per extra return a day between neighbouring intervals (constant under "
           "iid noise): " + ", ".join(f"{IV[j][0]}-{IV[j + 1][0]} {s_ * 1e3:.3f}e-3" for j, s_ in enumerate(slopes)))
anchor(66, "by year, RV(10m)/RV(5m) - 1 (file; approximates the 5-minute rho_1 by A26-34): " +
           ", ".join(f"{yy} {v(R10_5[yy], 3, 3)}" for yy in YEARS))

# ====================================================================== the text (part 2)
# ---------------------------------------------------------------- front matter, introduction, case, X1
chk("T", T, ",", "5,849")
chk("A", A, ".2f", "246.12")
chk("T5S sessions", len(rv_dates), ",", "5,351")
has("first return", "3 January 2003")
has("last date", "8 October 2026")
has("T5S start", "3 January 2005")
has("TR23 retrieval", "`TaiwanStockTotalReturnIndex` (TAIEX), retrieved 18 October 2026")
has("T5S retrieval", "`TaiwanVariousIndicators5Seconds` (TWSE's TAIEX), retrieved 19 October 2026")
chk("LM19's rho_1 of r^2 (A19-40, cited)", 0.194403, ".3f", "0.194")
f_g7, f_e7, f_r7, f_v7 = (math.sqrt(FC[k][i7]) for k in ("garch_n", "ewma", "roll60", "v_prev"))
f_g8, f_e8, f_r8, f_v8 = (math.sqrt(FC[k][i8]) for k in ("garch_n", "ewma", "roll60", "v_prev"))
chk("case: GARCH for 7 April", f_g7, ".2f", "1.72")
chk("case: GARCH for 7 April, a year", ann(FC["garch_n"][i7]), ".1f", "27.0")
chk("case: EWMA for 7 April", f_e7, ".2f", "1.56")
chk("case: fall of 7 April (simple)", -100 * R[i7], ".2f", "9.70")
chk("case: log return of 7 April", y[i7], ".2f", "-10.20")
chk("case: GARCH standard deviations", -y[i7] / f_g7, ".1f", "5.9")
assert rank == i7
chk("case: GARCH for 8 April", f_g8, ".2f", "3.60")
chk("case: EWMA for 8 April", f_e8, ".2f", "2.92")
chk("case: realized volatility of 7 April", f_v8, ".2f", "10.09")
chk("case: realized volatility of 8 April", math.sqrt(V15[i8]), ".2f", "3.39")
for lab_, val, pr_s in (("GARCH 7", f_g7, "1.7222"), ("EWMA 7", f_e7, "1.5605"), ("60-day 7", f_r7, "1.3226"),
                        ("V 7", f_v7, "0.7004"), ("realized 7", math.sqrt(V15[i7]), "10.0859"), ("r 7", y[i7], "-10.2029"),
                        ("GARCH 8", f_g8, "3.6031"), ("EWMA 8", f_e8, "2.9215"), ("60-day 8", f_r8, "1.8665"),
                        ("V 8", f_v8, "10.0859"), ("realized 8", math.sqrt(V15[i8]), "3.3873"), ("r 8", y[i8], "-4.0990")):
    chk(f"X1: {lab_}", val, ".4f", pr_s)
has("X1 row 1", "| 2 April → 7 April | 1.7222 | 1.5605 | 1.3226 | 0.7004 | 10.0859 | −10.2029 |".replace("−", "-"))
has("X1 row 2", "| 7 April → 8 April | 3.6031 | 2.9215 | 1.8665 | 10.0859 | 3.3873 | −4.0990 |".replace("−", "-"))
chk("X1 note: o2 share on 7 April", 100 * 1e4 * O2[rv_dates.index("2025-04-07")] / V15[i7], ".2f", "99.99")
flag("X1 V 7 (0.700351)", f_v7, 4)
flag("X1 sqrt V 7", math.sqrt(V15[i7]), 2)

# ---------------------------------------------------------------- section 2
chk("ARCH K=1: a", b1[0], ".4f", "1.1779")
chk("ARCH K=1: b_1", b1[1], ".3f", "0.196")
chk("ARCH K=1: b_1, four decimals (KC)", b1[1], ".4f", "0.1960")
chk("ARCH K=1: R-squared", r21, ".5f", "0.03844")
chk("ARCH K=1: T - 1", T - 1, ",", "5,848")
chk("ARCH K=1: statistic", lm1, ".1f", "224.8")
chk("ARCH K=1: statistic from the printed R-squared", 5848 * 0.03844, ".1f", "224.8")
sci("ARCH K=1: p-value", p1, 1, "8.2 -51")
chk("ARCH K=5: statistic", lm5, ".1f", "696.3")
chk("chi2_5 5% point", float(stats.chi2.ppf(0.95, 5)), ".2f", "11.07")
assert p5 < 1e-100
has("ARCH K=5 p-value", "below $10^{-100}$")
chk("ARCH K=5: slopes' sum", float(b5[1:].sum()), ".3f", "0.529")
for xx, pv_, sd_ in ((3.0, "2.94", "1.72"), (0.5, "1.23", "1.11")):
    chk(f"KC 2: variance after {xx}%", b1[0] + b1[1] * xx**2, ".2f", pv_)
    chk(f"KC 2: variance after {xx}% (printed inputs)", 1.1779 + 0.1960 * xx**2, ".2f", pv_)
    chk(f"KC 2: sd after {xx}%", math.sqrt(b1[0] + b1[1] * xx**2), ".2f", sd_)
    chk(f"KC 2: sd after {xx}% (printed inputs)", math.sqrt(1.1779 + 0.1960 * xx**2), ".2f", sd_)
has("cited LM13", "12.04% of the time, against 1.85% overall")
has("cited LM17", "correlate only 0.039, but their sizes correlate 0.161")
chk("cited LM25 Ljung-Box (recomputed)", lbr[0, 0], ",.0f", "1,820")

# ---------------------------------------------------------------- section 3
chk("E2: forecast for 7 April, %^2", ew[i7], ".4f", "2.4351")
chk("E2: forecast for 7 April, %", s_a, ".4f", "1.5605")
chk("E2: r^2", y[i7] ** 2, ".4f", "104.0999")
chk("E2: 0.94 x 2.4351", 0.94 * 2.4351, ".4f", "2.2890")
chk("E2: 0.06 x 104.0999", 0.06 * 104.0999, ".4f", "6.2460")
chk("E2: sum", 2.2890 + 6.2460, ".4f", "8.5350")
chk("E2: forecast for 8 April", s_b, ".4f", "2.9215")
chk("E2: forecast for 8 April from the printed parts", math.sqrt(8.5350), ".4f", "2.9215")
chk("E2: effective window", 1 / (1 - LAM), ".1f", "16.7")
chk("E2: weights' half-life", math.log(0.5) / math.log(LAM), ".1f", "11.2")
chk("E2: last 75 days' weight", 100 * (1 - LAM**75), ".1f", "99.0")
chk("E2: start", ew[0], ".2f", "1.84")
assert first == 1240 and dates[first] == "2008-01-02"   # ew[t] = lam^t ew[0] + ...: the start's weight on day t
chk("E2: the first test day's index", first, ",", "1,240")
sci("E2: start's weight on 2 January 2008", LAM**first, 0, "5 -34")
chk("X2: weeks", len(wends), ",", "1,224")
chk("X2: realized weeks", len(real_w), ",", "1,120")
chk("X2: GARCH unconditional, a year", ann(uvar), ".2f", "19.83")
chk("X2: GARCH max", ann(float(cvn[ig] ** 2)), ".2f", "70.41")
chk("X2: EWMA max", ann(float(ew[ie])), ".2f", "60.11")
chk("X2: realized max", real_w[jr][1], ".2f", "100.16")
assert dates[ig] == dates[ie] == dates[real_w[jr][0]] == "2025-04-11"
has("X2: the week", "week ending 11 April 2025")
chk("E3: QLIKE at 0.94", float(qv_arr[list(lams).index(0.94)]), ".4f", "0.5153")
chk("E3: QLIKE at 0.97", float(qv_arr[list(lams).index(0.97)]), ".4f", "0.5436")
chk("E3: best QLIKE", float(qv_arr[ib]), ".4f", "0.5087")
chk("E3: best lambda", float(lams[ib]), ".3f", "0.905")
chk("E3: GARCH", q_garch, ".4f", "0.5032")
has("E3: grid", "from 0.800 to 0.995 in steps of 0.005")
chk("KC 3: effective window at 0.97", 1 / 0.03, ".1f", "33.3")
chk("KC 3: half-life at 0.97", math.log(0.5) / math.log(0.97), ".2f", "22.76")
has("RiskMetrics: 75 effective days", "Table 5.9 lists 75 effective days at 0.94")
# RiskMetrics' effective days K solve lam^K = tolerance (its section 5.3.1.2, Eq. [5.26]); at a 1% tolerance K = 74.4,
# and its Table 5.9 prints 75: the last 75 days carry at least 99% of the weight, the last 74 less.
assert 1 - LAM**75 >= 0.99 > 1 - LAM**74
has("RiskMetrics: 99% of the weight", "the most recent days, which carry 99% of the weight")

# ---------------------------------------------------------------- section 4
chk("E4: alpha+beta", pers, ".5f", "0.98443")
chk("E4: unconditional variance", uvar, ".4f", "1.5971")
chk("E4: sigma_t+1|t", math.sqrt(s2_7), ".3f", "3.517")
chk("E4: sigma^2_t+1|t", s2_7, ".4f", "12.3695")
for m_, pv_ in ((5, "3.42"), (20, "3.10"), (44, "2.66"), (250, "1.35")):
    chk(f"E4: sigma_t+{m_}|t", math.sqrt(p7[m_ - 1]), ".2f", pv_)
    pp = C.term(12.3695, 0.98443, 1.5971)
    chk(f"E4: sigma_t+{m_}|t (printed inputs)", math.sqrt(pp[m_ - 1]), ".2f", pv_)
has("E4: horizons", "$m$ = 5, 20, 44 and 250 sessions")
chk("E4: sigma", math.sqrt(uvar), ".3f", "1.264")
chk("E4: half-life", hl_n, ".1f", "44.2")
chk("E4: half-life (printed input)", half_life(0.98443), ".1f", "44.2")
chk("E4: 20-day average, a year", ann(float(p7[:20].mean())), ".1f", "51.8")
chk("E4: 250-day average, a year", ann(float(p7.mean())), ".1f", "32.6")
pp = C.term(12.3695, 0.98443, 1.5971)
chk("E4: 20-day average (printed inputs)", ann(float(pp[:20].mean())), ".1f", "51.8")
chk("E4: 250-day average (printed inputs)", ann(float(pp.mean())), ".1f", "32.6")
chk("E4: forecast on 8 October 2026", math.sqrt(s2_T), ".3f", "1.092")
chk("E4: forecast on 8 October 2026, a year", ann(s2_T), ".2f", "17.13")
has("E4: arch forecast", "gives the same values to $10^{-12}$")
chk("pitfall 4: m = 1, a year", ann(float(p7[0])), ".2f", "55.18")
chk("pitfall 4: 250-day average, a year", ann(float(p7.mean())), ".2f", "32.57")
chk("KC 4: half-life at 0.98", half_life(0.98), ".1f", "34.3")
chk("KC 4: half-life at 0.99098", half_life(0.99098), ".1f", "76.5")
chk("KC 4: t fit's alpha+beta", pers_t, ".5f", "0.99098")

# ---------------------------------------------------------------- section 5
X3n = [("g", pn[0], sen[0], ser[0]), ("omega", pn[1], sen[1], ser[1]), ("alpha", pn[2], sen[2], ser[2]),
       ("beta", pn[3], sen[3], ser[3])]
X3t = [("g", pt[0], stc[0], strr[0]), ("omega", pt[1], stc[1], strr[1]), ("alpha", pt[2], stc[2], strr[2]),
       ("beta", pt[3], stc[3], strr[3])]
rows_x3 = {"g": r"$g$ (% a day)", "omega": r"$\omega$ (%²)", "alpha": r"$\alpha$", "beta": r"$\beta$"}
for (nm, a_, b_, c_), (_, d_, e_, f_) in zip(X3n, X3t):
    cells = [format(x, ".4f") for x in (a_, b_, c_, d_, e_, f_)]
    has(f"X3 row {nm}", norm_text(f"| {rows_x3[nm]} | " + " | ".join(cells) + " |"))
    for x in (a_, b_, c_, d_, e_, f_):
        assert not tie(x, ".4f")
        flag(f"X3 {nm}", x, 4)
has("X3 row nu", f"| $\\nu$ | — | | | {pt[4]:.2f} | {stc[4]:.2f} | {strr[4]:.2f} |")
has("X3 row alpha+beta", f"| $\\alpha+\\beta$ | {pers:.5f} | | | {pers_t:.5f} | | |")
has("X3 row sigma^2", f"| $\\sigma^2$ (%²), a year | {uvar:.3f}, {ann(uvar):.2f}% | | | {uvar_t:.3f}, {ann(uvar_t):.2f}% | | |")
has("X3 row half-life", f"| Half-life (sessions) | {hl_n:.1f} | | | {hl_t:.1f} | | |")
has("X3 row l", f"| $\\ell$ | {gn.loglikelihood:,.2f} | | | {gt.loglikelihood:,.2f} | | |")
flag("X3 t sigma^2 (1.651463)", uvar_t, 3)
chk("X3: half-life t from the printed alpha+beta", half_life(0.99098), ".1f", "76.5")
chk("E5: g", pn[0], ".4f", "0.0809")
chk("E5: omega", pn[1], ".4f", "0.0249")
chk("E5: alpha", pn[2], ".4f", "0.0913")
chk("E5: beta", pn[3], ".4f", "0.8932")
chk("E5: l", gn.loglikelihood, ",.2f", "-8,647.25")
assert abs(ll_hand - gn.loglikelihood) < 1e-6
chk("E5: backcast", bc_full, ".2f", "2.78")
chk("E5: sigma^2", uvar, ".3f", "1.597")
chk("E5: TR23's sqrt(A) s_r (LM19, A19-54)", ann(float(y.var())), ".2f", "18.99")
chk("E5: delta-method SE", se_hl_r, ".1f", "16.1")
chk("E5: delta interval, low", hl_n - z975 * se_hl_r, ".0f", "13")
chk("E5: delta interval, high", hl_n + z975 * se_hl_r, ".0f", "76")
chk("E5: delta interval, low (printed)", 44.2 - 1.96 * 16.1, ".0f", "13")
chk("E5: delta interval, high (printed)", 44.2 + 1.96 * 16.1, ".0f", "76")
chk("E5: SE(alpha+beta)", se_pers_r, ".4f", "0.0056")
chk("E5: interval for alpha+beta, low", lo_p, ".5f", "0.97342")
chk("E5: interval for alpha+beta, high", hi_p, ".5f", "0.99544")
chk("E5: mapped, low", half_life(lo_p), ".0f", "26")
chk("E5: mapped, high", half_life(hi_p), ".0f", "152")
chk("E5: mapped, low (printed)", half_life(0.97342), ".0f", "26")
chk("E5: mapped, high (printed)", half_life(0.99544), ".0f", "152")
chk("E5: nu", pt[4], ".2f", "5.54")
chk("E5: l gain", gt.loglikelihood - gn.loglikelihood, ".2f", "183.35")
chk("E5: t half-life", hl_t, ".1f", "76.5")
chk("KC 5: robust over classic, alpha", ser[2] / sen[2], ".2f", "1.80")
chk("KC 5: from the printed X3", 0.0137 / 0.0076, ".2f", "1.80")
assert {f"{ser[i_] / sen[i_]:.1f}" for i_ in (1, 2, 3)} == {"1.7", "1.8"}   # omega, alpha, beta
has("summary: 1.7 to 1.8", "1.7 to 1.8 times the classic ones")
chk("E6: excess kurtosis of xi", MOM["xi normal"][1], ".2f", "2.57")
chk("E6: skewness of xi", MOM["xi normal"][0], ".2f", "-0.59")
chk("E6: skewness of r", MOM["r"][0], ".2f", "-0.47")
chk("E6: excess kurtosis of r (LM17's 5.428)", MOM["r"][1], ".3f", "5.428")
chk("E6: Ljung-Box of |xi|", lbn[0, 0], ".1f", "27.6")
chk("E6: its p-value", lbn[0, 1], ".3f", "0.002")
chk("E6: ARCH on xi", lmx, ".1f", "14.3")
chk("E6: its p-value", px, ".3f", "0.014")
chk("E6: days at or below -4.107 by s", n_s, "d", "17", in_md=False)
chk("E6: by GARCH", n_xi, "d", "9", in_md=False)
has("E6: the counts", "lie 17 days standardized by $s$ and 9 standardized by GARCH")
chk("E6: normal model", T * stats.norm.cdf(z5), ".3f", "0.117")
chk("DD2: alpha", pn[2], ".6f", "0.091254")
chk("DD2: alpha+beta", pers, ".6f", "0.984432")
chk("DD2: denominator", den4, ".6f", "0.014239")
chk("DD2: denominator (printed inputs)", 1 - 0.984432**2 - 2 * 0.091254**2, ".6f", "0.014239")
chk("DD2: kurtosis", kurt_n, ".2f", "6.51")
chk("DD2: kurtosis (printed inputs)", 3 * (1 - 0.984432**2) / (1 - 0.984432**2 - 2 * 0.091254**2), ".2f", "6.51")
chk("DD2: excess", kurt_n - 3, ".2f", "3.51")
chk("DD2: nu", pt[4], ".3f", "5.544")
chk("DD2: E xi^4", kxi, ".2f", "6.89")
chk("DD2: E xi^4 (printed nu)", 3 + 6 / (5.544 - 4), ".2f", "6.89")
chk("DD2: the t condition", cond_t, ".3f", "1.008")
chk("DD2: the t condition (printed X3)", 0.99098**2 + (3 + 6 / 1.544 - 1) * 0.0663**2, ".3f", "1.008")
chk("E7: falls", len(idf), "d", "108")
chk("E7: falls after falls", int(fall[idf + 1].sum()), "d", "13")
chk("E7: expected after falls", float(Femp[idf].sum()), ".1f", "7.8")
chk("E7: independent days (LM21's A21-25)", 108 * 108 / 5848, ".1f", "2.0")
chk("E7: rises", len(idr), "d", "67")
chk("E7: expected after rises", float(Femp[idr].sum()), ".1f", "5.4")
chk("E7: falls after rises", int(fall[idr + 1].sum()), "d", "3", in_md=False)
has("E7: rises sentence", "After the 67 rises above 3% it expects 5.4, where 3 fell.")
chk("E7: days with |R| >= 2%", int(big2.sum()), "d", "489")
chk("E7: next-day size after", 100 * float(nxt[big2].mean()), ".2f", "1.27")
chk("E7: next-day size after others", 100 * float(nxt[~big2].mean()), ".2f", "0.80")
chk("E7: GARCH after", 100 * float(pred[big2].mean()), ".2f", "1.35")
chk("E7: GARCH after others", 100 * float(pred[~big2].mean()), ".2f", "0.79")
chk("E7: months", nm_, "d", "286")
chk("E7: TR23's dispersion (LM15's 3.02)", obs_disp, ".2f", "3.02")
chk("exp 1: median dispersion", SIM[1]["disp_med"], ".2f", "3.15")
chk("exp 1: its batch SE", SIM[1]["disp_se"], ".3f", "0.035")
chk("exp 1: 5%", SIM[1]["disp_q05"], ".2f", "2.04")
chk("exp 1: 95%", SIM[1]["disp_q95"], ".2f", "5.14")
chk("exp 1: median excess kurtosis", SIM[1]["kurt_med"], ".2f", "1.63")
chk("exp 1: share at or above 5.428", 100 * SIM[1]["kurt_share"], ".1f", "5.3")
chk("exp 2: median excess kurtosis", SIM[2]["kurt_med"], ".1f", "7.0")
flag("exp 1: batch SE", SIM[1]["disp_se"], 3)
flag("exp 1: 95%", SIM[1]["disp_q95"], 2)
has("exp seeds", "`default_rng([1, 20261011])`")
has("exp seeds", "`default_rng([2, 20261011])`")
has("LM18 resample numbers", "0.598 over 0.612")
assert abs(0.598 / 0.612 - 1) < 0.05

# ---------------------------------------------------------------- section 6
chk("returns a day at 5 s", 14400 // 5, ",", "2,880")
chk("returns a day at 15 min", 14400 // 900, "d", "16")
chk("14,400 seconds", 14400, ",", "14,400")
chk("dividends' share (below 0.01%)", 100 * div_share, ".5f", "0.00647", in_md=False)
assert 100 * div_share < 0.01
has("dividends", "by less than 0.01% in total")
chk("signature: 2015-2026 5 s", SIG["2015-2026"]["5s"], ".1f", "11.7")
chk("signature: 2025 5 s", SIG["2025"]["5s"], ".1f", "24.3")
chk("signature: 2005-2010 1 min", SIG["2005-2010"]["1m"], ".3f", "0.483")
chk("X4 note: 2005-2010 days", int(periods["2005-2010"].sum()), ",", "1,493")
chk("X4 note: 2011-2012 days", int(periods["2011-01-17..2012"].sum()), "d", "487")
chk("X4 note: 2015-2026 days", int(periods["2015-2026"].sum()), ",", "2,867")
chk("S12: 5 s, two decimals", SIG["2015-2026"]["5s"], ".2f", "11.71")
chk("S12: 30 min", SIG["2015-2026"]["30m"], ".3f", "0.930")
chk("E8: file, 5-second days", vr5, ".3f", "-0.381")
chk("E8: file, 15-second days", vr15, ".3f", "-0.281")
chk("E8: file, 5 minutes", vr5m, ".3f", "0.056")
chk("KC 6: RV(30s)/RV(15s)", vr15 + 1, ".4f", "0.7189")
chk("KC 6: implied rho_1 (printed ratio)", 0.7189 - 1, ".3f", "-0.281")
chk("X6 top: 2008", R1_5["2008"], ".3f", "0.397")
chk("X6 top: 2025", R1_5["2025"], ".3f", "2.968")
assert min(R1_5, key=lambda k: R1_5[k]) == "2008" and max(R1_5, key=lambda k: R1_5[k]) == "2025"
assert sorted(k for k in YEARS if R1_5[k] < 1) == [str(x) for x in range(2005, 2013)] + ["2020"]
chk("X6 bottom: 2007", R10_5["2007"], ".3f", "0.256")
chk("X6 bottom: 2025", R10_5["2025"], ".3f", "-0.257")
chk("X6 bottom: 2024", R10_5["2024"], ".3f", "-0.177")
assert max(R10_5, key=lambda k: R10_5[k]) == "2007" and min(R10_5, key=lambda k: R10_5[k]) == "2025"
assert sorted(k for k in YEARS if R10_5[k] < -0.1 - EPS) == ["2024", "2025"]
has("X6 threshold", "below −0.1 only in 2024".replace("−", "-"))
chk("DD3: smallest rise per return", min(slopes) * 1e3, ".1f", "3.1")
chk("DD3: largest rise per return", max(slopes) * 1e3, ".1f", "4.9")
has("DD3: the range", r"from $3.1\times10^{-3}$ to $4.9\times10^{-3}$")
chk("auction: 1/48", 100 / 48, ".1f", "2.1")
chk("opening share, all days", 100 * float(np.mean(1e4 * O2) / np.mean(Vt["15m"])), ".0f", "66")
chk("E10: opening share, OOS days", 100 * float(np.mean(1e4 * O2[mo]) / np.mean(Vt["15m"][mo])), ".0f", "68")
if PA is not None and TX is not None:
    r5_, r15_, r5m_ = C.pooled(PA, m5s, "f"), C.pooled(PA, m15, "f"), C.pooled(PA, np.ones(len(rv_dates), bool), "m5")
    p25_ = C.pooled(PA, m25, "f")
    rd_ = PA["rho1_day"][m25]
    rat_day = RV["5s"][m25] / RV["5m"][m25]
    chk("E8: raw, 5-second days", r5_, ".3f", "-0.380")
    chk("E8: raw, 15-second days", r15_, ".4f", "-0.2815")
    chk("KC 6: raw", r15_, ".4f", "-0.2815")
    chk("E8: raw, 5 minutes", r5m_, ".3f", "0.056")
    chk("E8: 2025 pooled", p25_, ".3f", "-0.386")
    chk("E8: noise share 2025", 100 * 2 * abs(p25_), ".0f", "77")
    chk("E8: noise share from the printed -0.386", 100 * 2 * 0.386, ".0f", "77")
    chk("S8: 2 x 0.386", 2 * 0.386, ".3f", "0.772")
    chk("E8: daily min", float(rd_.min()), ".2f", "-0.52")
    chk("E8: daily max", float(rd_.max()), ".2f", "-0.19")
    chk("E8: daily 25%", qinv(rd_, 0.25), ".2f", "-0.41")
    chk("E8: daily 75%", qinv(rd_, 0.75), ".2f", "-0.33")
    chk("E8: median day's ratio", qinv(rat_day, 0.5), ".1f", "25.2")
    chk("E8: largest ratio", float(rat_day.max()), ".1f", "62.6")
    TXA = TX["RV"]
    chk("E9: index 1-minute rho_1", R1["2025"], ".3f", "-0.421")
    chk("E9: index 1-minute volatility", 100 * math.sqrt(A * float(np.mean(RV["1m"][m25]))), ".1f", "22.8")
    chk("E9: TX rho_1", TX["rho1"], ".3f", "-0.011")
    chk("E9: TX 1-minute volatility", 100 * math.sqrt(A * float(TXA[1].mean())), ".2f", "9.26")
    for h_, pv_ in ((1, "1.00"), (10, "1.02"), (15, "0.98"), (30, "1.00")):
        chk(f"E9: TX ratio at {h_} min", float(TXA[h_].mean() / TXA[5].mean()), ".2f", pv_)
    has("E9: TX ratios", "1.00, 1.02, 0.98 and 1.00 at 1, 10, 15 and 30 minutes")
    for h_, nm, pv_ in ((1, "1m", "6.08"), (5, "5m", "2.04"), (15, "15m", "1.34"), (30, "30m", "1.14")):
        chk(f"index/TX at {nm}", float(np.mean(RV[nm][m25])) / float(TXA[h_].mean()), ".2f", pv_)
    keep = np.array([d not in TX["miss_days"] for d in TX["days"]])
    for h_ in (1, 10, 15, 30):
        assert f"{TXA[h_].mean() / TXA[5].mean():.4f}" == f"{TXA[h_][keep].mean() / TXA[5][keep].mean():.4f}"
    assert sorted(TX["miss_days"]) == ["2025-04-07", "2025-04-10"]
    has("X5: locked days", "7 and 10 April leave TX's ratios unchanged to four decimals")
    chk("X5: sessions", len(TX["days"]), "d", "243")
    assert all(PA["frozen_all"] == 1)
    chk("auction share, 5-second days", 100 * float(PA["auct2"][m5s].mean() / np.mean(RV["5m"][m5s])), ".1f", "7.3")
else:
    print("RAW: the raw intraday download is missing; the numbers marked 'raw download' and E9's were not rechecked")

# ---------------------------------------------------------------- section 7
chk("design: W", W, ",", "1,231")
chk("design: refits", len(refits["normal"]), "d", "226")
assert len(refits["t"]) == 226
chk("design: days", len(oos), ",", "4,609")
assert dates[first] == "2008-01-02" and dates[first - 1] == "2007-12-31"
has("design: first day", "2 January 2008")
chk("design: Newey-West lags", nl, "d", "9", in_md=False)
has("design: 9 lags", "9 lags for 4,609 days")
for k, row in (("roll60", "Rolling 60-day"), ("ewma", "EWMA 0.94"), ("garch_n", "GARCH normal"), ("garch_t", "GARCH $t$"),
               ("v_prev", "Yesterday's $V$"), ("ewma_v", "EWMA of $V$")):
    r_ = X7[k]
    tcol = "—" if k == "garch_n" else f"{LD[(k, 'QLIKE')]['t']:.2f}"
    cells = (f"{r_['mean']:.3f} | {r_['mse']:.2f} | {r_['qlike']:.4f} | {r_['b']:.3f} ({r_['b_se']:.3f}) | {r_['r2']:.3f} | "
             f"{tcol}")
    has(f"X7 row {k}", f"| {row} | {cells} |")
    for val, fm in ((r_["mean"], ".3f"), (r_["mse"], ".2f"), (r_["qlike"], ".4f"), (r_["b"], ".3f"), (r_["b_se"], ".3f"),
                    (r_["r2"], ".3f")):
        assert not tie(val, fm)
chk("X7 note: target mean", float(targets["V15"].mean()), ".3f", "1.368")
for tg in ("V5", "V30", "r2"):
    assert ORDERS[tg][:2] == ["garch_n", "garch_t"] and ORDERS[tg][-2:] == ["roll60", "v_prev"]
SAME_ORDER = {tg: ORDERS[tg] == ORDERS["V15"] for tg in ("V5", "V30", "r2")}
# the text: the same order with V(5 min) and V(30 min); with r^2 only the two EWMAs swap places
assert SAME_ORDER["V5"] and SAME_ORDER["V30"] and not SAME_ORDER["r2"]
sw = list(ORDERS["V15"])
ie_, iv_ = sw.index("ewma"), sw.index("ewma_v")
sw[ie_], sw[iv_] = sw[iv_], sw[ie_]
assert ORDERS["r2"] == sw and ORDERS["r2"][-1] == "v_prev"
has("X7 note: orders", "with $r_t^2$ only the two EWMAs swap places")
has("orders against r^2", "There the two GARCH forecasts again rank first and second, and yesterday's $V$ last.")
has("P4: the two GARCH forecasts", "while the two GARCH forecasts keep the two lowest QLIKE scores")
print("QLIKE orders:", {tg: [NAMES[k] for k in ORDERS[tg]] for tg in ORDERS})
chk("E10: GARCH QLIKE", X7["garch_n"]["qlike"], ".4f", "0.5032")
chk("E10: GARCH MSE", X7["garch_n"]["mse"], ".2f", "10.37")
chk("E10: EWMA QLIKE difference", LD[("ewma", "QLIKE")]["mean"], ".4f", "0.0121")
chk("E10: its t-stat", LD[("ewma", "QLIKE")]["t"], ".2f", "1.83")
chk("E10: its p-value", LD[("ewma", "QLIKE")]["p"], ".3f", "0.067")
chk("E10: EWMA MSE difference", LD[("ewma", "MSE")]["mean"], ".3f", "0.428")
chk("E10: its t-stat", LD[("ewma", "MSE")]["t"], ".2f", "2.98")
chk("E10: GARCH t QLIKE", LD[("garch_t", "QLIKE")]["t"], ".2f", "1.40")
chk("E10: GARCH t MSE", LD[("garch_t", "MSE")]["t"], ".2f", "0.62")
chk("E10: yesterday's V QLIKE", LD[("v_prev", "QLIKE")]["t"], ".2f", "11.96")
chk("E10: MZ a", MZ["V15"]["a"], ".3f", "-0.015")
chk("E10: MZ a SE", MZ["V15"]["a_se"], ".3f", "0.135")
chk("E10: MZ b", MZ["V15"]["b"], ".3f", "0.980")
chk("E10: MZ b SE", MZ["V15"]["b_se"], ".3f", "0.114")
chk("E10: MZ t(b=1)", MZ["V15"]["t"], ".2f", "-0.18")
chk("E10: MZ R-squared", MZ["V15"]["r2"], ".3f", "0.172")
chk("E10: MZ R-squared against r^2", MZ["r2"]["r2"], ".3f", "0.119")
has("Andersen-Bollerslev (SOURCES)", "found 0.047 and 0.026 against squared returns")
chk("V against r^2: ratio", float(np.mean(Vt["15m"]) / np.mean(y2)), ".3f", "0.933")
chk("V against r^2: t-stat", t_vr2, ".2f", "-3.26")
chk("V against r^2: 2025", float(np.mean(Vt["15m"][ryear == "2025"]) / np.mean(y2[ryear == "2025"])), ".3f", "0.918")
chk("V against r^2: 2008", float(np.mean(Vt["15m"][ryear == "2008"]) / np.mean(y2[ryear == "2008"])), ".3f", "1.011")
assert nl_all == 9
chk("X8: GARCH below EWMA, years", win_e, "d", "12", in_md=False)
has("X8: 12 of 19", "GARCH beats EWMA in 12 of 19 years")
chk("X8: 2025 GARCH", BY["2025"][0], ".3f", "0.611")
chk("X8: 2025 EWMA", BY["2025"][1], ".3f", "0.733")
chk("X8: 2020 GARCH", BY["2020"][0], ".3f", "0.666")
chk("X8: 2020 EWMA", BY["2020"][1], ".3f", "0.785")
chk("X8: 2026 days", int((oy == "2026").sum()), "d", "185")
chk("windows: 1,000 GARCH", SENS[1000][0], ".4f", "0.5029")
chk("windows: 2,461 GARCH", SENS[2461][0], ".4f", "0.5332")
chk("windows: 1,000 EWMA", SENS[1000][2], ".4f", "0.5126")
chk("windows: 2,461 EWMA", SENS[2461][2], ".4f", "0.5421")
assert all(SENS[w_][0] < min(SENS[w_][1], SENS[w_][2]) for w_ in SENS)
chk("windows: 2,461", 2461, ",", "2,461")
chk("X9: 2025 realized", real25, ".2f", "23.33")
chk("X9: week of 7 April, realized", W7["real"], ".2f", "100.16")
chk("X9: week of 7 April, GARCH", W7["garch_n"], ".2f", "55.86")
chk("X9: week of 7 April, EWMA", W7["ewma"], ".2f", "47.22")
chk("X9: week of 7 April, yesterday's V", W7["v_prev"], ".2f", "99.52")
chk("X9: weeks", len(wk), "d", "52")
chk("X9: sessions", len(ids25), "d", "243")
chk("case resolution: 20 after", ann(float(V15[post].mean())), ".1f", "54.3")
chk("case resolution: 20 before", ann(float(V15[pre].mean())), ".1f", "19.8")
chk("case resolution: GARCH", ann(float(FC["garch_n"][post].mean())), ".1f", "48.9")
chk("case resolution: EWMA", ann(float(FC["ewma"][post].mean())), ".1f", "50.1")
chk("KC 7: QLIKE at half", 2 - math.log(2) - 1, ".4f", "0.3069")
chk("KC 7: QLIKE at double", 0.5 + math.log(2) - 1, ".4f", "0.1931")
chk("KC 7: MSE at half", 0.25, ".2f", "0.25")

# ---------------------------------------------------------------- section 8
chk("code comment: ARCH K=5", lm5, ".1f", "696.3")
chk("code comment: Ljung-Box", lbn[0, 0], ".1f", "27.6")
chk("KC 8: variance in decimals", float(np.var(C.r)), ".6f", "0.000147")
chk("KC 8: variance in %^2", float(np.var(y)), ".2f", "1.47")
has("KC 8: arch's range", "[0.1, 10,000)")

# ---------------------------------------------------------------- problems and solutions
chk("P1: B", 1 / 0.03, ".1f", "33.3")
chk("P1: A", math.log(0.5) / math.log(0.97), ".2f", "22.76")
chk("P1: C", 0.97 / 0.03, ".1f", "32.3")
chk("P2: A", math.sqrt(246.12 * u2), ".1f", "17.5")
chk("P2: B", math.sqrt(246.12 * u2b), ".1f", "7.5")
chk("P2: C", math.sqrt(u2), ".2f", "1.12")
chk("S2: 1.25", u2, ".2f", "1.25")
chk("S2: 0.2273", u2b, ".4f", "0.2273")
chk("P3: C", half_life(0.98), ".1f", "34.3")
chk("P3: A", 0.5 / 0.02, ".0f", "25")
chk("P3: B", 1 / 0.02, ".0f", "50")
chk("P5: B", 1 - 0.40, ".2f", "0.60")
chk("P5: A", 1 + 0.40, ".2f", "1.40")
chk("P5: C", 1 - 0.80, ".2f", "0.20")
chk("P6: alpha+beta", pers, ".6f", "0.984432")
s20 = 1.5971 + 0.984432**19 * (12.3695 - 1.5971)
chk("S6: sigma^2_t+20|t", s20, ".4f", "9.5925")
chk("S6: sigma_t+20|t", math.sqrt(s20), ".3f", "3.097")
chk("S6: sigma_t+20|t (unrounded)", math.sqrt(p7[19]), ".3f", "3.097")
chk("S6: gap", 12.3695 - 1.5971, ".4f", "10.7724")
chk("S6: 1 - alpha - beta", 1 - 0.984432, ".6f", "0.015568")
avg20 = 1.5971 + 10.7724 * (1 - 0.984432**20) / (20 * 0.015568)
chk("S6: 20-day average variance", avg20, ".4f", "10.9157")
chk("S6: annualized", math.sqrt(246.12 * 10.9157), ".1f", "51.8")
chk("S6: annualized (unrounded)", ann(float(p7[:20].mean())), ".1f", "51.8")
chk("S9: denominator", 1 - 0.984432**2 - 2 * 0.091254**2, ".6f", "0.014239")
chk("S10: l", gn.loglikelihood, ",.2f", "-8,647.25")
chk("S10: sigma_t on 7 April", float(cvn[i7]), ".3f", "1.737")
chk("S11: EWMA QLIKE", X7["ewma"]["qlike"], ".4f", "0.5153")

# ---------------------------------------------------------------- the widget's data (written by data/lm26_charts.py)
WJ = json.loads(WIDGET.read_text(encoding="utf-8"))["widget"]
assert WJ["A"] == round(A, 6) and WJ["alpha"] == round(float(pn[2]), 6) and WJ["beta"] == round(float(pn[3]), 6)
psw = WJ["alpha"] + WJ["beta"]
uw = WJ["uvar"]
for start_key, s2s in (("apr", WJ["start"]["apr"]), ("oct", WJ["start"]["oct"])):
    pw = uw + psw ** (np.arange(250)) * (s2s - uw)
    if start_key == "apr":
        chk("widget: m = 1", math.sqrt(WJ["A"] * pw[0]), ".2f", "55.18")
        chk("widget: 20-day average", math.sqrt(WJ["A"] * float(pw[:20].mean())), ".2f", "51.83", in_md=False)
        chk("widget: 250-day average", math.sqrt(WJ["A"] * float(pw.mean())), ".2f", "32.57")
        chk("widget: start", math.sqrt(s2s), ".3f", "3.517")
    else:
        chk("widget: start, October", math.sqrt(s2s), ".3f", "1.092")
chk("widget: half-life", half_life(psw), ".1f", "44.2")
chk("widget: alpha+beta", psw, ".5f", "0.98443")
chk("widget: unconditional", math.sqrt(WJ["A"] * uw), ".2f", "19.83")
chk("widget: unconditional variance", uw, ".4f", "1.5971")

# ====================================================================== structure: labels and citations
md_raw = MD.read_text(encoding="utf-8")
ex_labels = re.findall(r"\[!exhibit\][^\n]*\{#([\w-]+)\}", md_raw)
eg_labels = re.findall(r"\[!example\][^\n]*\{#([\w-]+)\}", md_raw)
assert len(ex_labels) == 9 and len(eg_labels) == 10, (ex_labels, eg_labels)
# build/build.py keys labels by name alone, so an exhibit and an example must never share one
assert len(set(ex_labels) | set(eg_labels)) == len(ex_labels) + len(eg_labels), "a label is used twice"
for lab in ex_labels:
    assert f"[[ex:{lab}]]" in md_raw, f"exhibit {lab} is never cited"
for kind, lab in re.findall(r"\[\[(ex|eg):([\w-]+)\]\]", md_raw):
    assert lab in (ex_labels if kind == "ex" else eg_labels), (kind, lab)
tags = re.findall(r"\\tag\{(26\.\d+)\}", md_raw)
assert tags == [f"26.{k}" for k in range(1, 10)], tags
for name in re.findall(r'data-chart="(lm26-[\w-]+)"', md_raw):
    assert (ROOT / "src" / "data" / f"{name}.json").exists(), name
print(f"labels: {len(ex_labels)} exhibits, {len(eg_labels)} examples, tags (26.1)-(26.9), every exhibit cited")

# ====================================================================== report
body = TEXT.split("\n## Glossary", 1)[0]
nums = set(re.findall(r"(?<![\w.])\d+\.\d+|(?<![\w.,])\d{1,3}(?:,\d{3})+", body))
left = sorted(n for n in nums if n not in COVERED)
print(f"\nnumbers with a decimal point or thousands separator not covered by a check ({len(left)}):")
print("   " + " ".join(left))
print(f"\nvalues near a rounding boundary at their printed precision ({len(FLAGS)}):")
for fl in FLAGS:
    print("   ", fl)
print(f"\nanchors skipped (raw intraday download missing): {', '.join(SKIPPED) if SKIPPED else 'none'}")
print(f"anchor differences ({len(ANCHOR_DIFFS)}):")
for a in ANCHOR_DIFFS:
    print("   ", a)
print(f"\nall {N_CHECKS} checks passed")
sys.exit(0)
