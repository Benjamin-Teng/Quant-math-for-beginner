"""LM21 anchors (Hypothesis Testing and Multiple Testing): every number the Stage 1 brief quotes.

Reads TR23 from data/processed/vol3_taiex.parquet (columns date, tr, price, R, Rp; R is the total-return index's
simple daily return, null on the first row; built and checked by data/vol3_series.py, which must run first). Reads U28
through data/lm10_series.py (Volume II's sector sample; data/vol2_series.py must run first) only for A21-61, which
recounts LM16's printed counts. Writes nothing.

Conventions (plans/vol-4.md, "Shared decisions" and "Editor's decisions on the LM19-LM25 drafts"):
  * Sample TR23: T = 5,849 simple returns R_t = P_t / P_{t-1} - 1, 2003-01-03 -> 2026-10-08; years = calendar days
    between the first and last close / 365.25 (exactly days * 4 / 1461); A = T / years = 246.12 (used only to
    annualize a Sharpe ratio).
  * Owners: Rbar, s and the Sharpe ratio are LM19's statistics, SE(Rbar) and the interval for the mean LM20's; they are
    anchored here because LM21 quotes them. The t-stats and every test are LM21's.
  * Divisors: s divides by T, s_u by T - 1 (NumPy ddof passed explicitly). The t-stat of a mean (21.1) is
    (Rbar - mu_null) / (s_u / sqrt(T)); the two-sample statistic (21.3) is (Rbar_1 - Rbar_2) /
    sqrt(s_u1^2 / T_1 + s_u2^2 / T_2), unpooled variances. p-values are two-sided against the standard normal unless
    stated; the t_{T-1} values and SciPy's ttest_ind(..., equal_var=False) are printed beside them as checks.
  * The Sharpe ratio has r_f = 0: SR = Rbar / s per day, annualized by sqrt(A) (so SR_annual * sqrt(years) =
    Rbar / s * sqrt(T)).
  * Regimes by return date: before 2015-06-01 (7% limit, 3,077 returns) and from 2015-06-01 (10%, 2,772).
  * The pair space is LM13's: the 5,848 pairs (R_{t-1}, R_t); down means R < 0 (no return is 0). A fall is
    R <= -3%. LM15's blocks: the first 5,840 returns in 292 consecutive blocks of 20; an up day has R > 0.
  * The calendar family: 12 months and 5 weekdays (Monday-Friday) of the return's date, each tested against all other
    returns of TR23 (two-sample statistic); TR23's 23 Saturday sessions belong to no weekday and to every "rest".
  * Counts against a threshold use the guard (<= -x + 1e-12, >= x - 1e-12, > 1e-12 for an up day) and are recounted
    exactly with Fraction on the two-decimal closes. Constructed p-values are compared exactly with Fraction.
  * Simulation (AUTHORING section 8): each experiment creates its generator once, at its start, as
    np.random.default_rng([e, 20261011]), e its number in the brief:
      e = 8 (E8): B = 10,000 permutations, perm = g8.permutation(T) each; the shuffled series is R[perm] placed on
        TR23's dates in their order, so every month and weekday keeps its dates and its size and receives the returns
        R[perm] at its positions; the 17 statistics are recomputed on each shuffled series;
      e = 10 (E10, X7): 10,000 random long-short rules on TR23, every position drawn in one call
        integers(0, 2, size=(10000, T), dtype=int8) (rule i is row i, position 2 x - 1), processed in chunks of 500;
      e = 11 (Problem 11): 10,000 families of 17 independent standard normal statistics, standard_normal((10000, 17)).
  * Monte Carlo errors: a share p_hat of B draws has the standard error sqrt(p_hat (1 - p_hat) / B) ((18.2) on
    indicators); a mean of B draws s / sqrt(B), s with divisor B; the standard deviation of E10's 10,000 t-stats (s,
    divisor 10,000) has LM18's batch standard error: s on each of the 20 chunks of 500 rules, the standard deviation of
    the 20 values (divisor 20) over sqrt(20).
  * Rounding: chk(anchor, label, value, printed) checks one printed form. It asserts that the unrounded value rounds
    to the printed string at the string's own precision (its decimals, or its mantissa's decimals for "7.6e-05") and
    reports on stderr every printed form within a tenth of a last-digit unit of a rounding boundary ("NEAR"); an exact
    tie fails (print more digits). Exact rationals (counts, fractions of counts, exact binomial tails, the years) are
    passed as Fraction and rounded exactly. Every printed form of the brief and of anchors.md goes through chk; a
    mismatch makes the script exit with status 1 after printing the anchors.

Run from the repository root:
    PYTHONUTF8=1 uv run python data/vol4_anchors_lm21.py [repository root]
Prints one line per anchor, "A21-NN <value>", in ID order.
"""
import datetime as dt
import sys
from fractions import Fraction
from math import comb, floor, log, sqrt
from pathlib import Path

import numpy as np
import polars as pl
from scipy import stats
from statsmodels.stats.multitest import multipletests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lm10_series import S5, u28

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
SEED = 20261011
EPS = 1e-12
LIMIT_SWITCH = dt.date(2015, 6, 1)
C975 = float(stats.norm.isf(0.025))
C80 = float(stats.norm.ppf(0.8))
C95 = float(stats.norm.isf(0.05))

OUT: list[str] = []
NEARS: list[str] = []
FAILS: list[str] = []


def put(value: str) -> None:
    OUT.append(f"A21-{len(OUT) + 1:02d} {value}")


def rng(e: int) -> np.random.Generator:
    """The generator of experiment e: the experiment number first, then the root seed."""
    return np.random.default_rng([e, SEED])


def printed(x: float, d: int) -> str:
    """x rounded to d decimals, flagged NEAR when within a tenth of a last-digit unit of a rounding boundary."""
    u = abs(x) * 10**d
    frac = u - floor(u)
    flag = " NEAR" if abs(frac - 0.5) < 0.1 else ""
    return f"{x:.{d}f}{flag}"


def chk(aid: str, label: str, value: float | np.integer | Fraction, shown: str, note: str = "") -> None:
    """Check a printed form against its unrounded value at the printed form's own precision."""
    want = shown.replace(",", "")
    mant, _, ex_s = want.partition("e")
    d = len(mant.split(".")[1]) if "." in mant else 0
    ex = int(ex_s) if ex_s else 0
    if isinstance(value, (int, np.integer)):
        value = Fraction(int(value))
    if isinstance(value, Fraction):
        u = abs(value) * Fraction(10) ** (d - ex)
        n = floor(u)
        near = abs(u - n - Fraction(1, 2)) < Fraction(1, 10)
        if u - n == Fraction(1, 2):
            FAILS.append(f"A21-{aid} {label}: {value} is an exact tie at {shown}; print more digits")
            return
        if u - n > Fraction(1, 2):
            n += 1
        digits = str(n).rjust(d + 1, "0")
        got = digits[:-d] + "." + digits[-d:] if d else digits
        if ex_s:
            got = f"{got}e{ex:+03d}"
        if value < 0 and n:
            got = "-" + got
        note = note or "exact"
    else:
        x = float(value)
        uf = abs(x) * 10.0 ** (d - ex)
        r = uf - floor(uf)
        if r == 0.5:
            FAILS.append(f"A21-{aid} {label}: {x!r} is a tie at {shown}; print more digits")
            return
        near = abs(r - 0.5) < 0.1
        got = f"{x:.{d}e}" if ex_s else f"{x:.{d}f}"
    if got != want:
        FAILS.append(f"A21-{aid} {label}: {value} rounds to {got}, printed {shown}")
    if near:
        NEARS.append(f"NEAR A21-{aid} {label}: {float(value)!r} printed {shown}" + (f" ({note})" if note else ""))


def p2(z: float) -> float:
    """Two-sided normal p-value."""
    return float(2 * stats.norm.sf(abs(z)))


def two_sample(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    """Two-sample statistic (21.3) with unpooled divisor-(n-1) variances, and its standard error."""
    se = sqrt(float(a.var(ddof=1)) / len(a) + float(b.var(ddof=1)) / len(b))
    return (float(a.mean()) - float(b.mean())) / se, se


def holm_count(p: list[Fraction] | list[float], a: float | Fraction) -> int:
    ps, m, k = sorted(p), len(p), 0
    for i, pi in enumerate(ps):
        if pi <= a / (m - i):
            k += 1
        else:
            break
    return k


def bh_count(p: list[Fraction] | list[float], q: float | Fraction) -> int:
    ps, m = sorted(p), len(p)
    ok = [i + 1 for i, pi in enumerate(ps) if pi <= (i + 1) * q / m]
    return max(ok) if ok else 0


def bonf_count(p: list[Fraction] | list[float], a: float | Fraction) -> int:
    return sum(1 for pi in p if pi <= a / len(p))


# ---------------------------------------------------------------- data
df = pl.read_parquet(PROC / "vol3_taiex.parquet").sort("date")
dates_all: list[dt.date] = list(df["date"].to_list())
tr = df["tr"].to_numpy()
R = df["R"].to_numpy()[1:].astype(np.float64)
dates = dates_all[1:]
assert df["R"][0] is None and len(set(dates_all)) == len(dates_all)
T = len(R)
days = (dates_all[-1] - dates_all[0]).days
years = days / 365.25
years_f = Fraction(4 * days, 1461)
A = T / years
Rb = float(R.mean())
s = float(R.std(ddof=0))
su = float(R.std(ddof=1))
se = su / sqrt(T)
tstat = Rb / se

trf = [Fraction(str(x)) for x in tr]
RF = [trf[i] / trf[i - 1] - 1 for i in range(1, len(trf))]
up_x = sum(x > 0 for x in RF)
dn_x = sum(x < 0 for x in RF)
zero_x = sum(x == 0 for x in RF)
up_g = int((R > EPS).sum())
assert up_g == up_x and int((R < -EPS).sum()) == dn_x and zero_x == 0

pre = np.array([d < LIMIT_SWITCH for d in dates])
wd = np.array([d.weekday() for d in dates])
mo = np.array([d.month for d in dates])
WD_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MO_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# ---------------------------------------------------------------- data role
put(f"{len(dates_all)} closes, {dates_all[0]} -> {dates_all[-1]}")                                     # 01
chk("01", "closes", len(dates_all), "5,850")
put(f"{T} returns, {dates[0]} -> {dates[-1]}")                                                         # 02
chk("02", "T", T, "5,849")
assert (str(dates[0]), str(dates[-1])) == ("2003-01-03", "2026-10-08")
put(f"{days} days; {years:.6f} years")                                                                 # 03
chk("03", "days", days, "8,680")
for shown in ("23.7645", "23.76", "23.8"):
    chk("03", "years", years_f, shown)
put(f"{A:.6f}")                                                                                        # 04
chk("04", "A", Fraction(T) / years_f, "246.12")
i_pre = int(pre.sum())
put(f"before 2015-06-01: {i_pre} returns ({dates[0]} -> {dates[i_pre - 1]}); from 2015-06-01: {T - i_pre} "
    f"({dates[i_pre]} -> {dates[-1]})")                                                                # 05
chk("05", "before", i_pre, "3,077")
chk("05", "from", T - i_pre, "2,772")
put(f"pairs {T - 1} ({dates[1]} -> {dates[-1]}); blocks {T // 20} of 20 ({T // 20 * 20} returns, last "
    f"{T % 20} excluded, {dates[T // 20 * 20]} -> {dates[-1]})")                                       # 06
for v, shown in ((T - 1, "5,848"), (T // 20, "292"), (T // 20 * 20, "5,840"), (T % 20, "9")):
    chk("06", "pairs and blocks", v, shown)
cnt_wd = np.bincount(wd, minlength=7)
sats = [str(d) for d, w in zip(dates, wd) if w == 5]
put(", ".join(f"{WD_NAMES[k]} {cnt_wd[k]}" for k in range(7)) + f"; Saturdays: {', '.join(sats)}")    # 07
for k, shown in enumerate(("1,151", "1,181", "1,183", "1,168", "1,143", "23")):
    chk("07", WD_NAMES[k], cnt_wd[k], shown)
cnt_mo = np.bincount(mo, minlength=13)[1:]
put(", ".join(f"{MO_NAMES[k]} {cnt_mo[k]}" for k in range(12)))                                        # 08
for k, shown in enumerate(("450", "369", "532", "477", "503", "498", "524", "522", "491", "482", "492", "509")):
    chk("08", MO_NAMES[k], cnt_mo[k], shown)
put(f"up {up_x}; down {dn_x}; zero {zero_x} (Fraction); guard count up {up_g}")                         # 09
chk("09", "up", up_x, "3,205")
chk("09", "down", dn_x, "2,644")
chk("09", "zero", zero_x, "0")

# ---------------------------------------------------------------- case
put(f"{100 * Rb:.10f}% (printed {printed(100 * Rb, 4)}%)")                                             # 10
chk("10", "Rbar %", 100 * Rb, "0.0625")
put(f"s_u {100 * su:.6f}%; s {100 * s:.6f}% (printed s_u {printed(100 * su, 4)}%)")                     # 11
chk("11", "s_u %", 100 * su, "1.2085")
chk("11", "s %", 100 * s, "1.2084")
chk("11", "s % (case box)", 100 * s, "1.21")
put(f"SE {100 * se:.7f}%; t-stat {tstat:.6f} (printed {printed(tstat, 2)}); with s: {Rb / (s / sqrt(T)):.6f}")  # 12
chk("12", "SE %", 100 * se, "0.0158")
chk("12", "t-stat", tstat, "3.96", "from data")
chk("12", "t-stat (X1)", tstat, "3.956")
chk("12", "t-stat with s", Rb / (s / sqrt(T)), "3.956")
reg = []
for lab, x, shown in (("before", R[pre], ("0.0464", "1.2572", "0.0227", "2.05", "2.046", "0.041")),
                      ("from", R[~pre], ("0.0804", "1.1519", "0.0219", "3.68", "3.675", "0.00024"))):
    n = len(x)
    m_, su_ = float(x.mean()), float(x.std(ddof=1))
    t_ = m_ / (su_ / sqrt(n))
    reg.append(f"{lab} 2015-06-01: T {n}, mean {100 * m_:.6f}%, s_u {100 * su_:.5f}%, SE {100 * su_ / sqrt(n):.6f}%, "
               f"t {t_:.5f} (printed {printed(t_, 2)}), p {p2(t_):.6f}")
    for v, sh in zip((100 * m_, 100 * su_, 100 * su_ / sqrt(n), t_, t_, p2(t_)), shown):
        chk("13", f"{lab} regime", v, sh, "from data")
put("; ".join(reg))                                                                                    # 13
wed, oth = R[wd == 2], R[wd != 2]
z_wed, se_wed = two_sample(wed, oth)
pw_wed = float(stats.ttest_ind(wed, oth, equal_var=False).pvalue)
put(f"Wednesdays {len(wed)}: mean {100 * wed.mean():.5f}%; other days {len(oth)}: mean {100 * oth.mean():.5f}%; "
    f"difference {100 * (wed.mean() - oth.mean()):.5f}%; SE {100 * se_wed:.5f}%; z {z_wed:.5f} (printed "
    f"{printed(z_wed, 2)}); p normal {p2(z_wed):.6f}; p SciPy ttest_ind(equal_var=False) {pw_wed:.6f}")  # 14
for v, sh in ((len(wed), "1,183"), (len(oth), "4,666"), (100 * float(wed.mean()), "0.1332"),
              (100 * float(oth.mean()), "0.0446"), (100 * float(wed.mean() - oth.mean()), "0.0886"),
              (100 * se_wed, "0.0375"), (z_wed, "2.36"), (z_wed, "2.363"), (p2(z_wed), "0.018"), (pw_wed, "0.0182")):
    chk("14", "Wednesday", v, sh)
hi = []
for k, shown in ((2, ("0.1405", "1.33")), (12, ("0.1270", "1.53"))):
    a, b = R[mo == k], R[mo != k]
    hi.append(f"{MO_NAMES[k - 1]} {len(a)} days, mean {100 * a.mean():.5f}%, z {two_sample(a, b)[0]:.4f}")
    chk("15", f"{MO_NAMES[k - 1]} mean %", 100 * float(a.mean()), shown[0])
    chk("15", f"{MO_NAMES[k - 1]} z", two_sample(a, b)[0], shown[1], "from data")
order = np.argsort([-R[mo == k].mean() for k in range(1, 13)])
put("; ".join(hi) + f"; months by mean: {', '.join(MO_NAMES[i] for i in order)}")                       # 15

# ---------------------------------------------------------------- sections: the mean, the regimes, power
p_n, p_t, p_1 = p2(tstat), 2 * float(stats.t.sf(tstat, T - 1)), float(stats.norm.sf(tstat))
put(f"two-sided: normal {p_n:.4e}, t_(T-1) {p_t:.4e}; one-sided normal {p_1:.4e}")                     # 16
chk("16", "p normal", p_n, "7.6e-05")
chk("16", "p t", p_t, "7.7e-05")
chk("16", "p one-sided", p_1, "3.8e-05")
chk("16", "t against normal, % (KC 9: about 1%)", 100 * (p_t / p_n - 1), "1")
se_s = s / sqrt(T)
put(f"LM20's interval (A20-09), A Rbar +- 1.96 A s / sqrt(T): {100 * A * (Rb - 1.96 * se_s):.6f}% to "
    f"{100 * A * (Rb + 1.96 * se_s):.6f}%; daily, Rbar +- 1.96 s / sqrt(T): {100 * (Rb - 1.96 * se_s):.6f}% to "
    f"{100 * (Rb + 1.96 * se_s):.6f}%")                                                                # 17
chk("17", "interval low %", 100 * A * (Rb - 1.96 * se_s), "7.8")
chk("17", "interval high %", 100 * A * (Rb + 1.96 * se_s), "23.0")
z_reg, se_reg = two_sample(R[~pre], R[pre])
wr = stats.ttest_ind(R[~pre], R[pre], equal_var=False)
put(f"z {z_reg:.5f} (printed {printed(z_reg, 2)}); SE {100 * se_reg:.6f}%; p normal {p2(z_reg):.5f}; SciPy "
    f"ttest_ind(equal_var=False) df {float(wr.df):.1f}, p {float(wr.pvalue):.5f}")                     # 18
chk("18", "z regimes", z_reg, "1.08")
chk("18", "SE %", 100 * se_reg, "0.0315")
chk("18", "p", p2(z_reg), "0.28")
chk("18", "SciPy p", float(wr.pvalue), "0.280")
chk("18", "z from printed inputs", (0.0804 - 0.0464) / 0.0315, "1.08")
sr_d = Rb / s
sr_a = sr_d * sqrt(A)
put(f"SR per day {sr_d:.6f}; annual {sr_a:.5f} (printed {printed(sr_a, 2)}); SR_annual * sqrt(years) "
    f"{sr_a * sqrt(years):.6f} = Rbar / s * sqrt(T) {sr_d * sqrt(T):.6f}")                             # 19
chk("19", "SR per day", sr_d, "0.0517")
chk("19", "SR annual", sr_a, "0.81")
chk("19", "SR annual (4 dp)", sr_a, "0.8115")
chk("19", "identity", sr_a * sqrt(years), "3.956")
chk("19", "SR from printed inputs", sqrt(246.12) * 0.0625 / 1.2084, "0.81")
chk("19", "identity from printed inputs", 0.8115 * sqrt(23.7645), "3.956")


def years80(sr: float) -> float:
    return ((C975 + C80) / sr) ** 2


def power(sr: float, yrs: float) -> float:
    d = sr * sqrt(yrs)
    return float(stats.norm.cdf(d - C975) + stats.norm.cdf(-d - C975))


put(f"c {C975:.6f}; Phi^-1(0.8) {C80:.6f}; years for 80% power: " +
    ", ".join(f"SR {v:g}: {years80(v):.3f}" for v in (0.25, 0.5, 1.0)) +
    f", TR23's {sr_a:.6f}: {years80(sr_a):.3f}; power at those years (both tails): " +
    ", ".join(f"{power(v, years80(v)):.4f}" for v in (0.25, 0.5, 1.0, sr_a)))                         # 20
chk("20", "Phi^-1(0.975)", C975, "1.959964")
chk("20", "Phi^-1(0.8)", C80, "0.841621")
for v, sh in ((0.25, "125.6"), (0.5, "31.4"), (1.0, "7.85"), (sr_a, "11.9")):
    chk("20", f"years SR {v:.4g}", years80(v), sh)
put(f"at {years:.4f} years: " + ", ".join(f"SR {v:.4g}: {power(v, years):.5f}" for v in (0.25, 0.5, 1.0, sr_a)))  # 21
for v, sh in ((0.25, "0.23"), (0.5, "0.68"), (1.0, "0.998"), (sr_a, "0.977"), (sr_a, "0.98")):
    chk("21", f"power SR {v:.4g}", power(v, years), sh)

# ---------------------------------------------------------------- tests of frequencies and independence
th = up_x / T
z_up = (th - 0.5) / sqrt(0.25 / T)
p_up = float(stats.binom.sf(up_x - 1, T, 0.5))
put(f"theta_hat {th:.6f}; z {z_up:.5f}; exact Pr(X >= {up_x}) {p_up:.4e}; "
    f"normal Pr(Z >= z) {float(stats.norm.sf(z_up)):.4e}")                                            # 22
chk("22", "theta_hat", Fraction(up_x, T), "0.548")
chk("22", "z up", z_up, "7.3")
chk("22", "exact p", p_up, "1.2e-13")
prev_dn = [x < 0 for x in RF[:-1]]
now_dn = [x < 0 for x in RF[1:]]
n11 = sum(a and b for a, b in zip(prev_dn, now_dn))
n12 = sum(a and not b for a, b in zip(prev_dn, now_dn))
n21 = sum((not a) and b for a, b in zip(prev_dn, now_dn))
n22 = sum((not a) and (not b) for a, b in zip(prev_dn, now_dn))
npair = n11 + n12 + n21 + n22
assert npair == T - 1 and n11 == int(((R[:-1] < -EPS) & (R[1:] < -EPS)).sum())
tab = np.array([[n11, n12], [n21, n22]], dtype=float)
ex = tab.sum(1)[:, None] * tab.sum(0)[None, :] / npair
chi = float(((tab - ex) ** 2 / ex).sum())
rho = (n11 * n22 - n12 * n21) / sqrt((n11 + n12) * (n21 + n22) * (n11 + n21) * (n12 + n22))
c_y = stats.chi2_contingency(tab, correction=True)
c_n = stats.chi2_contingency(tab, correction=False)
assert abs(float(c_n.statistic) - chi) < 1e-9 and abs(npair * rho**2 - chi) < 1e-9
put(f"counts dd {n11}, du {n12}, ud {n21}, uu {n22}; expected {ex[0, 0]:.4f}, {ex[0, 1]:.4f}, {ex[1, 0]:.4f}, "
    f"{ex[1, 1]:.4f}; chi2 {chi:.5f} (= n rho^2), p {float(stats.chi2.sf(chi, 1)):.5f}; rho {rho:.6f}; "
    f"z = sqrt(n) rho {sqrt(npair) * rho:.5f}; Yates (SciPy default) {float(c_y.statistic):.5f}, "
    f"p {float(c_y.pvalue):.5f}")                                                                     # 23
for v, sh in ((n11, "1,226"), (n12, "1,417"), (n21, "1,418"), (n22, "1,787")):
    chk("23", "count", v, sh)
rows_, cols_ = (n11 + n12, n21 + n22), (n11 + n21, n12 + n22)
for v, sh in ((rows_[0], "2,643"), (rows_[1], "3,205"), (cols_[0], "2,644"), (cols_[1], "3,204")):
    chk("23", "margin", v, sh)
for (i, j), sh in zip(((0, 0), (0, 1), (1, 0), (1, 1)), ("1,194.95", "1,448.05", "1,449.05", "1,755.95")):
    chk("23", f"expected {i}{j}", Fraction(rows_[i] * cols_[j], npair), sh)
chk("23", "expected dd as LM13 printed it (lm13.md:212)", Fraction(rows_[0] * cols_[0], npair), "1,195.0",
    "exact; LM13's print")
for v, sh in ((chi, "2.69"), (float(stats.chi2.sf(chi, 1)), "0.10"), (rho, "0.0214"), (rho, "0.02143"),
              (sqrt(npair) * rho, "1.64"), (float(c_y.statistic), "2.60"), (float(c_y.pvalue), "0.107"),
              (5848 * 0.02143**2, "2.69")):
    chk("23", "sign table", v, sh)
f_dd = Fraction(n11, n11 + n12)
f_d = Fraction(n11 + n21, npair)
rho15 = (f_dd - f_d) / (1 - f_d)
put(f"LM15's rho_1 = (Pr(down given down) - Pr(down)) / (1 - Pr(down)): unrounded {float(rho15):.6f}; from printed "
    f"0.4639, 0.4521: {(0.4639 - 0.4521) / (1 - 0.4521):.6f} (printed 0.0215 and 0.0214, lm15.md:100)")  # 24
chk("24", "LM15 rho_1 unrounded", rho15, "0.0214")
chk("24", "LM15 rho_1 from printed", (0.4639 - 0.4521) / (1 - 0.4521), "0.0215")
fl_prev = [x <= Fraction(-3, 100) for x in RF[:-1]]
fl_now = [x <= Fraction(-3, 100) for x in RF[1:]]
f1, f2 = sum(fl_prev), sum(fl_now)
f12 = sum(a and b for a, b in zip(fl_prev, fl_now))
assert f12 == int(((R[:-1] <= -0.03 + EPS) & (R[1:] <= -0.03 + EPS)).sum())
exp_ff = f1 * f2 / npair
p_ff = float(stats.binom.sf(f12 - 1, f1, f2 / npair))
p_ffp = float(stats.poisson.sf(f12 - 1, exp_ff))
put(f"falls on day t-1 {f1}, on day t {f2}, both {f12}; expected {exp_ff:.5f}; exact Pr(X >= {f12}) for "
    f"Bin({f1}, {f2}/{npair}) {p_ff:.4e}; Poisson({exp_ff:.4f}) {p_ffp:.4e}")                         # 25
for v, sh in ((f1, "108"), (f2, "108"), (f12, "13"), (Fraction(f1 * f2, npair), "2.0"), (p_ff, "1.2e-07"),
              (p_ffp, "2.0e-07")):
    chk("25", "falls after falls", v, sh)
z16 = (177 - 48.68) / 6.94
put(f"printed 177, 48.68, 6.94 (lm16.md:382, 384): z {z16:.4f}; the SD that makes z = 3: {(177 - 48.68) / 3:.3f} "
    f"= {(177 - 48.68) / 3 / 6.94:.3f} x 6.94")                                                        # 26
chk("26", "z LM16", z16, "18.5")
chk("26", "SD for z = 3", (177 - 48.68) / 3, "42.8")
chk("26", "SD factor", (177 - 48.68) / 3 / 6.94, "6.2")
put("printed 43.8 expected and 291 U28 days beyond the chi2_5 99% quantile 15.09 (lm16.md:398-400)")   # 27

# ---------------------------------------------------------------- the calendar family
fam: list[tuple[str, int, float, float, float, float]] = []
for k in range(1, 13):
    a, b = R[mo == k], R[mo != k]
    z, _ = two_sample(a, b)
    fam.append((MO_NAMES[k - 1], len(a), 100 * float(a.mean()), z, p2(z),
                float(stats.ttest_ind(a, b, equal_var=False).pvalue)))
for k in range(5):
    a, b = R[wd == k], R[wd != k]
    z, _ = two_sample(a, b)
    fam.append((WD_NAMES[k], len(a), 100 * float(a.mean()), z, p2(z),
                float(stats.ttest_ind(a, b, equal_var=False).pvalue)))
M = len(fam)
pv = [f[4] for f in fam]
put("; ".join(f"{f[0]} {f[1]} {f[2]:.4f}% z {f[3]:.4f} p {f[4]:.5f} (SciPy t {f[5]:.5f})" for f in fam))  # 28
X5 = ("-0.32", "1.33", "-1.04", "0.59", "0.51", "-0.15", "1.00", "-0.50", "-1.13", "-1.10", "-0.34", "1.53",
      "-1.05", "-0.10", "2.36", "-0.63", "-0.42")
for f, sh in zip(fam, X5):
    chk("28", f"X5 z {f[0]}", f[3], sh, "from data")
chk("28", "Wed p", fam[14][4], "0.018")
chk("28", "Dec p", fam[11][4], "0.127")
n_sig = sum(1 for p in pv if p <= 0.05)
put(f"m = {M}; unadjusted p <= 0.05: {n_sig}; expected false rejections {M * 0.05:.2f}; FWER if independent "
    f"{1 - 0.95**M:.5f}; Bonferroni level {0.05 / M:.7f}, abs(z) >= {float(stats.norm.isf(0.025 / M)):.5f}")  # 29
fwer17 = 1 - Fraction(19, 20) ** M
for v, sh in ((M, "17"), (n_sig, "1"), (Fraction(M, 20), "0.85"), (fwer17, "0.58"), (fwer17, "0.582"),
              (Fraction(1, 20 * M), "0.00294"), (float(stats.norm.isf(0.025 / M)), "2.97"),
              (float(stats.norm.isf(0.025 / M)), "2.974")):
    chk("29", "family", v, sh)
pmin = min(pv)
put(f"smallest p {pmin:.6f}; Bonferroni-adjusted {M * pmin:.5f}; Sidak 1 - (1 - p)^17 {1 - (1 - pmin) ** M:.5f}")  # 30
chk("30", "smallest p", pmin, "0.018")
chk("30", "Bonferroni-adjusted", M * pmin, "0.31")
chk("30", "Sidak", 1 - (1 - pmin) ** M, "0.267")
# experiment 8: shuffle the dates (the series R[perm] on TR23's dates in order)
g8 = rng(8)
B8 = 10_000
grp_m, grp_w = mo - 1, wd
n_m = np.bincount(grp_m, minlength=12).astype(float)
n_w = np.bincount(grp_w, minlength=7)[:5].astype(float)
S_all, Q_all = float(R.sum()), float((R * R).sum())
zmax = np.empty(B8)
for b_ in range(B8):
    x = R[g8.permutation(T)]
    zs = []
    for grp, cnt, K in ((grp_m, n_m, 12), (grp_w, n_w, 5)):
        s1 = np.bincount(grp, weights=x, minlength=12)[:K]
        q1 = np.bincount(grp, weights=x * x, minlength=12)[:K]
        c2 = T - cnt
        m1, m2 = s1 / cnt, (S_all - s1) / c2
        v1 = (q1 - cnt * m1**2) / (cnt - 1)
        v2 = (Q_all - q1 - c2 * m2**2) / (c2 - 1)
        zs.append((m1 - m2) / np.sqrt(v1 / cnt + v2 / c2))
    zmax[b_] = float(np.abs(np.concatenate(zs)).max())
n8a = int((zmax >= C975 - EPS).sum())
n8b = int((zmax >= abs(z_wed) - EPS).sum())
fw8, pw8 = n8a / B8, n8b / B8
put(f"B {B8}: share with a test at abs(z) >= 1.959964: {fw8:.4f} (SE {sqrt(fw8 * (1 - fw8) / B8):.4f}); share with "
    f"max abs(z) >= {abs(z_wed):.4f}: {pw8:.4f} (SE {sqrt(pw8 * (1 - pw8) / B8):.4f})")                  # 31
chk("31", "shuffle FWER", Fraction(n8a, B8), "0.580")
chk("31", "its SE", sqrt(fw8 * (1 - fw8) / B8), "0.005")
chk("31", "shuffle, Wednesday's level", Fraction(n8b, B8), "0.266")
chk("31", "its SE", sqrt(pw8 * (1 - pw8) / B8), "0.004", "Monte Carlo SE")
ps_sorted = sorted(pv)
rej = {}
for meth in ("bonferroni", "holm", "fdr_bh", "hs"):
    rej[meth] = int(multipletests(pv, alpha=0.05, method=meth)[0].sum())
rej_bh10 = int(multipletests(pv, alpha=0.10, method="fdr_bh")[0].sum())
assert rej["bonferroni"] == bonf_count(pv, 0.05) and rej["holm"] == holm_count(pv, 0.05)
assert rej["fdr_bh"] == bh_count(pv, 0.05) and rej_bh10 == bh_count(pv, 0.10)
put(f"p_(1) {ps_sorted[0]:.5f} against Holm/Bonferroni/BH(0.05) {0.05 / M:.6f} and BH(0.10) {0.10 / M:.6f}; "
    f"p_(2) {ps_sorted[1]:.5f} against Holm {0.05 / (M - 1):.6f}, BH(0.05) {2 * 0.05 / M:.6f}, BH(0.10) "
    f"{2 * 0.10 / M:.6f}; rejections: Bonferroni {rej['bonferroni']}, Holm {rej['holm']}, BH q=0.05 "
    f"{rej['fdr_bh']}, BH q=0.10 {rej_bh10}, multipletests default (Holm-Sidak) {rej['hs']}")          # 32
chk("32", "BH(0.10) first threshold", Fraction(1, 10 * M), "0.00588")
chk("32", "Holm second threshold, an exact tie at five decimals", Fraction(1, 20 * (M - 1)), "0.003125")
for v in (rej["bonferroni"], rej["holm"], rej["fdr_bh"], rej_bh10, rej["hs"]):
    chk("32", "rejections", v, "0")
stab = []
for lab, sel, shown in (("before", pre, ("2.06", "0.040")), ("from", ~pre, ("1.25", "0.21"))):
    x, w = R[sel], wd[sel]
    z, _ = two_sample(x[w == 2], x[w != 2])
    stab.append(f"{lab} 2015-06-01: {int((w == 2).sum())} Wednesdays, mean {100 * x[w == 2].mean():.4f}% against "
                f"{100 * x[w != 2].mean():.4f}%, z {z:.4f}, p {p2(z):.4f}")
    chk("33", f"Wednesday {lab}", z, shown[0])
    chk("33", f"Wednesday {lab} p", p2(z), shown[1])
put("; ".join(stab))                                                                                    # 33
p3 = p2(3.0)
put(f"two-sided p at abs(t) = 3: {p3:.7f}; 0.05 / p = {0.05 / p3:.3f} tests; one-sided {float(stats.norm.sf(3)):.7f}")  # 34
chk("34", "p at 3", p3, "0.0027")
chk("34", "tests", 0.05 / p3, "18.5")
chk("34", "one-sided", float(stats.norm.sf(3)), "0.00135")


def maxq(u: float, m: int) -> float:
    return float(stats.norm.ppf(u ** (1 / m)))


put("; ".join(f"m={m}: median {maxq(0.5, m):.4f}, 5% {maxq(0.05, m):.4f}, 95% {maxq(0.95, m):.4f}, "
              f"Pr(max > 3) {1 - float(stats.norm.cdf(3)) ** m:.4f}" for m in (17, 100, 1000, 10000)))     # 35
for m, sh in ((17, "1.75"), (100, "2.46"), (1000, "3.20"), (10000, "3.81")):
    chk("35", f"median m={m}", maxq(0.5, m), sh)
chk("35", "5% m=1000", maxq(0.05, 1000), "2.75")
chk("35", "95% m=1000", maxq(0.95, 1000), "3.88", "exact constant")
for m, sh in ((17, "0.023"), (100, "0.13"), (1000, "0.74")):
    chk("35", f"Pr m={m}", 1 - float(stats.norm.cdf(3)) ** m, sh)
# experiment 10: random long-short rules on TR23
g10 = rng(10)
M10 = 10_000
pos = g10.integers(0, 2, size=(M10, T), dtype=np.int8)
tt = np.empty(M10)
for c in range(0, M10, 500):
    xr = (2.0 * pos[c:c + 500].astype(np.float64) - 1.0) * R
    tt[c:c + 500] = xr.mean(axis=1) / (xr.std(axis=1, ddof=1) / sqrt(T))
run = np.maximum.accumulate(tt)
put("; ".join(f"m={m}: {run[m - 1]:.4f}" for m in (1, 10, 17, 100, 1000, 10000)) + "; records (m, t): " +
    ", ".join(f"({i + 1}, {tt[i]:.4f})" for i in range(M10) if i == 0 or tt[i] > run[i - 1]))       # 36
for v, sh in ((run[0], "-1.18"), (run[99], "2.95"), (run[999], "2.95"), (tt[1021], "3.28"), (run[-1], "3.97")):
    chk("36", "search", float(v), sh)
for v, sh in ((int(np.argmax(tt[:100])) + 1, "90"), (int(np.argmax(tt[:1100])) + 1, "1,022"),
              (int(np.argmax(tt)) + 1, "7,840")):
    chk("36", "record rule", v, sh)
n3 = int((tt >= 3 - EPS).sum())
n196 = int((np.abs(tt) >= 1.96 - EPS).sum())
sd_t = float(tt.std(ddof=0))
sd_batches = np.array([tt[c:c + 500].std(ddof=0) for c in range(0, M10, 500)])
se_sd = float(sd_batches.std(ddof=0)) / sqrt(20)
put(f"t >= 3: {n3} (expected {M10 * float(stats.norm.sf(3)):.2f}); abs(t) >= 1.96: {n196} (expected "
    f"{M10 * p2(1.96):.1f}); mean {tt.mean():.4f} (SE s/sqrt(B) {sd_t / sqrt(M10):.4f}); s (divisor 10,000) "
    f"{sd_t:.4f} (batch SE {se_sd:.4f}, 20 batches of 500)")                                           # 37
for v, sh in ((n3, "13"), (M10 * float(stats.norm.sf(3)), "13.5"), (n196, "504"), (M10 * p2(1.96), "500"),
              (float(tt.mean()), "-0.01"), (sd_t / sqrt(M10), "0.01"), (sd_t, "0.995"), (se_sd, "0.007")):
    chk("37", "search counts and moments", v, sh)

# ---------------------------------------------------------------- knowledge checks
z_kc = (0.60 - 0.5) / sqrt(0.25 / 100)
put(f"z {z_kc:.4f}; p two-sided {p2(z_kc):.5f}")                                                       # 38
chk("38", "z", z_kc, "2.00")
chk("38", "p", p2(z_kc), "0.0455")
put(f"t {0.04 / (1 / sqrt(900)):.4f}; T for t = 2: {(2 * 1 / 0.04) ** 2:.0f}")                         # 39
chk("39", "t", 0.04 / (1 / sqrt(900)), "1.20")
chk("39", "T", Fraction(2 * 100, 4) ** 2, "2,500")
put(f"power at SR 0.5, 10 years {power(0.5, 10):.4f}; years for t = 3: SR 1 {(3 / 1) ** 2:.0f}, SR 0.5 "
    f"{(3 / 0.5) ** 2:.0f}")                                                                          # 40
chk("40", "power", power(0.5, 10), "0.35")
chk("40", "years SR 1", Fraction(3) ** 2, "9")
chk("40", "years SR 0.5", Fraction(6) ** 2, "36")
chi95 = float(stats.chi2.isf(0.05, 1))
put(f"chi2_1 5% point {chi95:.5f} = 1.959964^2; abs(rho) > {sqrt(chi95 / 10000):.6f}")                  # 41
chk("41", "chi2 point", chi95, "3.84")
chk("41", "rho", sqrt(chi95 / 10000), "0.0196")
put(f"expected {100 * 0.05:.0f}; Pr(at least one) {1 - 0.95**100:.5f}")                                # 42
chk("42", "expected", Fraction(100, 20), "5")
chk("42", "Pr", 1 - Fraction(19, 20) ** 100, "0.994")
kc6 = [Fraction(4, 1000), Fraction(12, 1000), Fraction(30, 1000)]
a5 = Fraction(5, 100)
put(f"Bonferroni {bonf_count(kc6, a5)}, Holm {holm_count(kc6, a5)}, BH {bh_count(kc6, a5)}")            # 43
for v, sh in ((bonf_count(kc6, a5), "2"), (holm_count(kc6, a5), "3"), (bh_count(kc6, a5), "3")):
    chk("43", "KC 7", v, sh)
m50 = log(0.5) / log(float(stats.norm.cdf(3)))
m_up = int(np.ceil(m50))
put(f"m = ln 0.5 / ln Phi(3) = {m50:.2f}; at m = {m_up}: {1 - float(stats.norm.cdf(3)) ** m_up:.5f}; at m = "
    f"{m_up - 1}: {1 - float(stats.norm.cdf(3)) ** (m_up - 1):.5f}")                                  # 44
chk("44", "m", m50, "513.1")
chk("44", "m rounded up", m_up, "514")
p29 = 2 * float(stats.t.sf(2, 29))
put(f"t_29 {p29:.5f}; normal {p2(2.0):.5f}")                                                            # 45
chk("45", "t_29", p29, "0.055")
chk("45", "normal", p2(2.0), "0.0455")

# ---------------------------------------------------------------- examples
pge8 = Fraction(sum(comb(12, j) for j in range(8, 13)), 4096)
pge9 = Fraction(sum(comb(12, j) for j in range(9, 13)), 4096)
pge10 = Fraction(sum(comb(12, j) for j in range(10, 13)), 4096)
th1 = Fraction(55, 100)
pow55 = sum(comb(12, j) * th1**j * (1 - th1) ** (12 - j) for j in range(10, 13))
put(f"Pr(X >= 8) {pge8} = {float(pge8):.5f}; Pr(X >= 9) {pge9} = {float(pge9):.5f}; Pr(X >= 10) {pge10} = "
    f"{float(pge10):.5f}; power at 0.55 {float(pow55):.5f}; type II {1 - float(pow55):.5f}")           # 46
assert pge8 == Fraction(794, 4096) and pge10 == Fraction(79, 4096)
for v, sh in ((pge8, "0.194"), (pge9, "0.073"), (pge10, "0.0193"), (pow55, "0.042"), (1 - pow55, "0.958"),
              (100 * pow55, "4")):
    chk("46", "E1", v, sh)
e9 = [Fraction(x) for x in ("0.002", "0.0054", "0.0061", "0.011", "0.024", "0.031", "0.09", "0.22", "0.47", "0.86")]
m9 = len(e9)
put(f"Bonferroni {bonf_count(e9, a5)} (level {float(a5 / m9):.4f}); Holm {holm_count(e9, a5)} (levels " +
    ", ".join(f"{float(a5 / (m9 - i)):.5f}" for i in range(4)) + f"); BH {bh_count(e9, a5)} (levels " +
    ", ".join(f"{float((i + 1) * a5 / m9):.3f}" for i in range(7)) + ")")                            # 47
for v, sh in ((bonf_count(e9, a5), "1"), (holm_count(e9, a5), "3"), (bh_count(e9, a5), "5")):
    chk("47", "E9 rejections", v, sh)
for i, sh in enumerate(("0.005", "0.00556", "0.00625", "0.00714")):
    chk("47", f"Holm level {i + 1}", a5 / (m9 - i), sh)
for i, sh in ((0, "0.005"), (4, "0.025"), (5, "0.030"), (6, "0.035")):
    chk("47", f"BH level {i + 1}", (i + 1) * a5 / m9, sh)

# ---------------------------------------------------------------- problems
put(f"{1 - 0.95**20:.5f}; 20 x 0.05 = {20 * 0.05:.2f}; one test {0.05:.2f}")                            # 48
chk("48", "P2 C", 1 - Fraction(19, 20) ** 20, "0.64")
chk("48", "P2 B", Fraction(20, 20), "1.00")
chk("48", "P2 A", Fraction(1, 20), "0.05")
put(f"{years80(0.5):.3f}; (1.959964/0.5)^2 {(C975 / 0.5) ** 2:.3f}; (1.959964 + 0.841621)/0.5 {(C975 + C80) / 0.5:.3f}")  # 49
chk("49", "P3 A", years80(0.5), "31.4")
chk("49", "P3 B", (C975 / 0.5) ** 2, "15.4")
chk("49", "P3 C", (C975 + C80) / 0.5, "5.60")
chi_p4 = 4000 * 0.03**2
put(f"chi2 {chi_p4:.3f}, p {float(stats.chi2.sf(chi_p4, 1)):.5f}; 4000 x 0.03 = {4000 * 0.03:.0f}; sqrt(4000) x 0.03 "
    f"= {sqrt(4000) * 0.03:.4f}")                                                                     # 50
chk("50", "P4 B", Fraction(4000 * 9, 10000), "3.60")
chk("50", "P4 p", float(stats.chi2.sf(3.6, 1)), "0.058")
chk("50", "P4 A", Fraction(4000 * 3, 100), "120")
chk("50", "P4 C", sqrt(4000) * 0.03, "1.90")
p5 = [Fraction(x) for x in ("0.003", "0.012", "0.020", "0.030", "0.40")]
put(f"Bonferroni {bonf_count(p5, a5)}, Holm {holm_count(p5, a5)}, BH {bh_count(p5, a5)}")              # 51
for v, sh in ((bonf_count(p5, a5), "1"), (holm_count(p5, a5), "2"), (bh_count(p5, a5), "4")):
    chk("51", "P5", v, sh)
n_months = ((C95 * 0.5 + C80 * sqrt(0.55 * 0.45)) / 0.05) ** 2
n_up = int(np.ceil(n_months))
cmin = int(stats.binom.isf(0.05, n_up, 0.5)) + 1
while float(stats.binom.sf(cmin - 1, n_up, 0.5)) > 0.05:
    cmin += 1
half, th55 = Fraction(1, 2), Fraction(11, 20)
size_x = sum(comb(n_up, j) for j in range(cmin, n_up + 1)) * half**n_up
pow_x = sum(comb(n_up, j) * th55**j * (1 - th55) ** (n_up - j) for j in range(cmin, n_up + 1))
size_prev = sum(comb(n_up, j) for j in range(cmin - 1, n_up + 1)) * half**n_up
assert size_x <= Fraction(1, 20) < size_prev
put(f"one-sided p {float(pge8):.4f}; Phi^-1(0.95) {C95:.6f}; months for 80% power at 0.55 (normal) {n_months:.2f} -> {n_up} = "
    f"{n_up / 12:.2f} years; exact at n = {n_up}: reject X >= {cmin}, size "
    f"{float(size_x):.5f}, power {float(pow_x):.5f}")                                                  # 52
for v, sh in ((pge8, "0.194"), (C95, "1.644854"), (C80, "0.841621"), (n_months, "616.16"),
              (((1.644854 * 0.5 + 0.841621 * sqrt(0.55 * 0.45)) / 0.05) ** 2, "616.16"), (n_up, "617"),
              (Fraction(n_up, 12), "51.4"), (cmin, "330"), (size_x, "0.0454"), (pow_x, "0.7874")):
    chk("52", "P6", v, sh)
nb = T // 20
blk = (R[: nb * 20] > EPS).reshape(nb, 20).sum(axis=1)
blk_f = [sum(1 for x in RF[20 * j: 20 * j + 20] if x > 0) for j in range(nb)]
assert list(blk) == blk_f
bm, bv = float(blk.mean()), float(blk.var(ddof=0))
ph = float(blk.sum()) / (nb * 20)
bin_v = 20 * ph * (1 - ph)
v516 = bin_v * (1 + 2 * 19 / 20 * float(rho15))
v516_p = 20 * 0.548 * 0.452 * (1 + 2 * 19 / 20 * 0.0215)
se_b = bin_v * sqrt(2 / nb)
se_b2 = v516 * sqrt(2 / nb)
n_blk = 2 * (C975 * 4.95 / (5.16 - 4.95)) ** 2
n_blk_up = int(np.ceil(n_blk))
put(f"blocks {nb}: mean {bm:.4f}, variance (divisor {nb}) {bv:.4f}; p_hat {ph:.5f}; 20 p q {bin_v:.4f}; LM15's 5.16 "
    f"unrounded {v516:.4f}, from printed {v516_p:.4f}; SE sigma^2 sqrt(2/292): {se_b:.4f} and {se_b2:.4f}; z "
    f"{(bv - bin_v) / se_b:.4f} and {(bv - v516) / se_b2:.4f}; from printed 4.72, 4.95, 5.16: "
    f"{(4.72 - 4.95) / (4.95 * sqrt(2 / 292)):.4f}, {(4.72 - 5.16) / (5.16 * sqrt(2 / 292)):.4f}; blocks n for "
    f"which a gap of 0.21 is 1.959964 SE, SE = 4.95 sqrt(2/n) (the binomial null, printed inputs): {n_blk:.2f}, "
    f"rounded up {n_blk_up} = {20 * n_blk_up} sessions = {20 * n_blk_up / A:.1f} years at A")         # 53
for v, sh, note in ((bv, "4.72", "LM15's print"), (bin_v, "4.95", "LM15's print"), (v516, "5.16", "LM15's print"),
                    ((4.72 - 4.95) / (4.95 * sqrt(2 / 292)), "-0.56", ""),
                    ((4.72 - 5.16) / (5.16 * sqrt(2 / 292)), "-1.03", ""), ((bv - bin_v) / se_b, "-0.58", ""),
                    ((bv - v516) / se_b2, "-1.03", ""), (n_blk, "4,268.7", ""), (n_blk_up, "4,269", ""),
                    (20 * n_blk_up, "85,380", ""), (20 * n_blk_up / A, "347", "")):
    chk("53", "P7", v, sh, note)
c11, c1r, c1c, cn = 347, 859, 538, 4382
c12, c21 = c1r - c11, c1c - c11
c22 = cn - c11 - c12 - c21
rho16 = (c11 * c22 - c12 * c21) / sqrt(c1r * (cn - c1r) * c1c * (cn - c1c))
put(f"from printed counts 347, 859, 538, 4,382 (lm16.md:71-74): table {c11}, {c12}, {c21}, {c22}; rho {rho16:.5f}; "
    f"chi2 {cn * rho16**2:.2f}; ratio {c11 * cn / (c1r * c1c):.4f} (printed 3.29, lm16.md:88)")        # 54
for v, sh in ((c12, "512"), (c21, "191"), (c22, "3,332"), (rho16, "0.423"), (cn * rho16**2, "784"),
              (Fraction(c11 * cn, c1r * c1c), "3.29"), (Fraction(c11 * cn, c1r * c1c), "3.2902")):
    chk("54", "P8", v, sh)
xc = R - Rb
m2_, m3_, m4_ = float((xc**2).mean()), float((xc**3).mean()), float((xc**4).mean())
sk, ku = m3_ / m2_**1.5, m4_ / m2_**2 - 3
jb = T / 6 * (sk**2 + ku**2 / 4)
jb_p = T / 6 * (0.34**2 + 5.27**2 / 4)
put(f"skew {sk:.5f}; excess kurtosis {ku:.5f}; JB {jb:.2f}; from printed -0.34, 5.27: {jb_p:.2f}; "
    f"log10 p = -JB / (2 ln 10): {-jb / (2 * log(10)):.1f}, from printed {-jb_p / (2 * log(10)):.1f}")  # 55
for v, sh in ((jb_p, "6,881"), (jb, "6,875"), (-jb_p / (2 * log(10)), "-1494"), (-jb / (2 * log(10)), "-1493")):
    chk("55", "P9", v, sh)
adj = sorted(float(v) for v in stats.false_discovery_control(pv, method="bh"))
put(f"multipletests rejections: default 'hs' {rej['hs']}, 'holm' {rej['holm']}, 'fdr_bh' {rej['fdr_bh']}, "
    f"'bonferroni' {rej['bonferroni']}; BH-adjusted p (false_discovery_control), two smallest: " +
    ", ".join(f"{v:.5f}" for v in adj[:2]))                                                    # 56
chk("56", "BH adjusted 1", adj[0], "0.308")
chk("56", "BH adjusted 2", adj[1], "0.669")
g11 = rng(11)
Z11 = g11.standard_normal((10_000, 17))
cb = float(stats.norm.isf(0.025 / 17))
n11u = int((np.abs(Z11) >= C975 - EPS).any(axis=1).sum())
n11b = int((np.abs(Z11) >= cb - EPS).any(axis=1).sum())
fw_u, fw_b = n11u / 10_000, n11b / 10_000
fwer17b = 1 - (1 - Fraction(1, 340)) ** 17
put(f"unadjusted {fw_u:.4f} (SE {sqrt(fw_u * (1 - fw_u) / 10_000):.4f}), exact {1 - 0.95**17:.5f}; Bonferroni "
    f"{fw_b:.4f} (SE {sqrt(fw_b * (1 - fw_b) / 10_000):.4f}), exact {float(fwer17b):.5f}")              # 57
for v, sh in ((Fraction(n11u, 10_000), "0.590"), (sqrt(fw_u * (1 - fw_u) / 10_000), "0.005"), (fwer17, "0.582"),
              (Fraction(n11b, 10_000), "0.051"), (sqrt(fw_b * (1 - fw_b) / 10_000), "0.002"), (fwer17b, "0.04884"),
              (cb, "2.974")):
    chk("57", "P11", v, sh)

# ---------------------------------------------------------------- hygiene: tests on TR23
tests = (["mean (E3)", "mean before 2015-06-01", "mean from 2015-06-01", "regimes' difference (E4)",
          "up-day frequency (E2)", "down after down (E6)", "falls after falls (E7)"]
         + [f"calendar: {f[0]}" for f in fam]
         + ["Wednesday before 2015-06-01", "Wednesday from 2015-06-01",
            "blocks' variance against 4.95 (Problem 7)", "against 5.16 (Problem 7)", "Jarque-Bera (Problem 9)"])
put(f"{len(tests)} tests: " + ", ".join(tests))                                                        # 58
chk("58", "tests on TR23", len(tests), "29")
chk("58", "without Problem 9's Jarque-Bera", len(tests) - 1, "28")

# ---------------------------------------------------------------- X2: the two reference laws
grid = np.linspace(-5, 5, 2001)
gap = float(np.abs(stats.t.pdf(grid, T - 1) - stats.norm.pdf(grid)).max())
t975 = float(stats.t.isf(0.025, T - 1))
put(f"t_(T-1) 97.5% point {t975:.5f} against {C975:.5f}; largest density gap on [-5, 5] {gap:.2e}")     # 59
chk("59", "t point", t975, "1.9604")
chk("59", "normal point", C975, "1.9600")
chk("59", "density gap", gap, "2.3e-05")
# ---------------------------------------------------------------- X1's note: t-stats from the printed inputs
t60 = [mm / (ss / sqrt(n)) for mm, ss, n in ((0.0625, 1.2085, T), (0.0464, 1.2572, i_pre), (0.0804, 1.1519, T - i_pre))]
put("from the four-decimal means and s_u: " + "; ".join(
    f"{lab} {v:.4f}" for lab, v in zip(("all", "before", "from"), t60)))                               # 60
for v, sh in zip(t60, ("3.955", "2.047", "3.675")):
    chk("60", "X1 from printed inputs", v, sh)

# ---------------------------------------------------------------- A21-61: LM16's printed counts recounted on U28
u = u28()
col = {c: i for i, c in enumerate(u.names)}
xs, xf = u.X[:, col["Semiconductor"]], u.X[:, col["FinancialInsurance"]]
nU = len(xs)
fs, ff = xs <= -0.01 + EPS, xf <= -0.01 + EPS


def mahal(x: np.ndarray) -> np.ndarray:
    """d_t^2 of every row with the sample's means and divisor-T covariance matrix ((12.9), LM16's convention)."""
    xc_ = x - x.mean(axis=0)
    lo = np.linalg.cholesky(xc_.T @ xc_ / x.shape[0])
    return (np.linalg.solve(lo, xc_.T) ** 2).sum(axis=0)


d2 = mahal(np.column_stack([xs, xf]))
d5 = mahal(u.X[:, [col[c] for c in S5]])
q99 = float(stats.chi2.ppf(0.99, 5))
n177 = int((~(d2 <= 9 + EPS)).sum())
n291 = int((~(d5 <= q99 + EPS)).sum())
p9 = float(np.exp(-4.5))
put(f"U28 {nU} days ({u.dates[0]} -> {u.dates[-1]}): Semiconductor <= -1% {int(fs.sum())}, FinancialInsurance <= -1% "
    f"{int(ff.sum())}, both {int((fs & ff).sum())}; pair d^2 > 9: {n177} against mean {nU * p9:.4f}, SD "
    f"{sqrt(nU * p9 * (1 - p9)):.4f} (z {(n177 - nU * p9) / sqrt(nU * p9 * (1 - p9)):.4f}); S5 d^2 above the chi2_5 "
    f"99% quantile {q99:.4f}: {n291} against {nU * 0.01:.2f}")                                          # 61
for v, sh in ((nU, "4,382"), (int(fs.sum()), "859"), (int(ff.sum()), "538"), (int((fs & ff).sum()), "347"),
              (n177, "177"), (nU * p9, "48.68"), (sqrt(nU * p9 * (1 - p9)), "6.94"),
              ((n177 - nU * p9) / sqrt(nU * p9 * (1 - p9)), "18.5"), (n291, "291"), (q99, "15.09"),
              (Fraction(nU, 100), "43.8")):
    chk("61", "LM16's counts on U28", v, sh)
assert (str(u.dates[0]), str(u.dates[-1])) == ("2008-12-02", "2026-10-08")

print("\n".join(OUT))
for line in NEARS:
    print(line, file=sys.stderr)
if FAILS:
    print("\n".join(["FAIL " + f for f in FAILS]), file=sys.stderr)
    sys.exit(1)
