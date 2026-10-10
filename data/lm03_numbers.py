"""Every number quoted in LM3 (src/lm03.md), recomputed and checked against the text.

Run after data/lm03_stats.py:  uv run python data/lm03_numbers.py

Each check prints a label and the value as the module prints it, and fails if the value no longer appears in
src/lm03.md. Where the module shows a computation, the check also recomputes it from the printed (rounded) inputs,
so that a reader who redoes the arithmetic gets the printed result.
"""

import json
import math
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
TEXT = (HERE.parent / "src" / "lm03.md").read_text(encoding="utf-8").replace("−", "-").replace("{,}", ",")
ST = json.loads((HERE / "processed" / "lm03_stats.json").read_text(encoding="utf-8"))
LN2 = math.log(2)


def rd(x, k):
    """Round half away from zero to k decimals, as a printed table does."""
    q = Decimal(1).scaleb(-k)
    return float(Decimal(repr(float(x))).quantize(q, rounding=ROUND_HALF_UP))


def f(x, k):
    """Format with k decimals, rounding half away from zero."""
    return f"{rd(x, k):.{k}f}"


def chk(label, s, *, text=True):
    """Print a value; unless text=False, require it to appear in the module (ASCII minus, no TeX thousands)."""
    print(f"{label:44s} {s}")
    if text:
        assert s.replace("−", "-") in TEXT, f"{label}: {s} not found in src/lm03.md"


def same(label, a, b):
    """Printed-input check: the result recomputed from printed inputs equals the printed result."""
    assert a == b, f"{label}: recomputed {a} but printed {b}"


full, daily, q22 = ST["full"], ST["daily"], ST["qqq2022"]
years = {y["label"]: y for y in ST["years"]}

# ---------------------------------------------------------------- case and the paradox exhibit
chk("0050 total return %", f(100 * full["ret0050"], 2))
chk("00631L total return %", f(100 * full["ret00631L"], 1).replace("4354", "4,354"))
chk("2 x 0050 %", f(200 * full["ret0050"], 1).replace("1804", "1,804"))
same("2 x printed 902.25", f(2 * 902.25, 1), f(200 * full["ret0050"], 1))
chk("0050 growth factor", f(1 + full["ret0050"], 2))
chk("00631L growth factor", f(1 + full["ret00631L"], 2))
chk("leveraged / twice index", f(full["ret00631L"] / full["twice0050"], 1))
chk("years", f(full["years"], 2))
chk("days in sample", f"{full['days']:,}")
chk("A = n x 365.25 / days", f(full["n"] * 365.25 / full["days"], 1))
chk("CAGR 0050 %", f(100 * full["cagr0050"], 1))
chk("CAGR 00631L %", f(100 * full["cagr00631L"], 1))
same("CAGR 0050 from printed", f(100 * (10.0225 ** (1 / 11.94) - 1), 1), f(100 * full["cagr0050"], 1))
same("CAGR 00631L from printed", f(100 * (44.545 ** (1 / 11.94) - 1), 1), f(100 * full["cagr00631L"], 1))
chk("QQQ 2022 %", f(100 * q22["QQQ"], 2))
chk("TQQQ 2022 %", f(100 * q22["TQQQ"], 2))
chk("3 x QQQ %", f(100 * q22["thrice"], 1))
same("3 x printed -32.58", f(3 * -32.58, 1), f(100 * q22["thrice"], 1))
assert ST["span_sessions"] == {"2025-06-18": 6, "2026-03-31": 5}, ST["span_sessions"]
assert full["n"] == 2902 and ST["own0050"]["n"] == 2906

# ---------------------------------------------------------------- Example approx: ln(1.05) and e^0.05
x = 0.05
ln_ex, T = math.log1p(x), [x, x - x**2 / 2, x - x**2 / 2 + x**3 / 3]
chk("ln 1.05", f(ln_ex, 7))
for t in T[2:]:
    chk("T3 ln", f(t, 7))
for t in T:
    chk("ln error", f"{rd(ln_ex - t, 7):+.7f}")
e_ex, E = math.exp(x), [1 + x, 1 + x + x**2 / 2, 1 + x + x**2 / 2 + x**3 / 6]
chk("e^0.05", f(e_ex, 7))
for t in E:
    chk("exp error", f"{rd(e_ex - t, 7):+.7f}")
chk("ratio ln n=1, n=2 (1/30, 1/27)", f"1/{1 / (x * 2 / 3):.0f}, 1/{1 / (x * 3 / 4):.0f}", text=False)
chk("ratio exp n=1, n=2 (1/60, 1/80)", f"1/{3 / x:.0f}, 1/{4 / x:.0f}", text=False)

# ---------------------------------------------------------------- knowledge check: monthly from annual
c2 = (1 / 12) * (1 / 12 - 1) / 2
chk("11/288 x 0.09^2", f(-c2 * 0.09**2, 6))
chk("1 + 0.0075 - 0.000309", f(1 + 0.0075 - 0.000309, 6))
chk("exact monthly %", f(100 * (1.09 ** (1 / 12) - 1), 4))
assert (1 / 12) * (1 / 12 - 1) * (1 / 12 - 2) / 6 > 0  # neglected third-order term is positive

# ---------------------------------------------------------------- pitfall: +150% year; working limit
chk("1.5 - 1.125", f(1.5 - 1.5**2 / 2, 3))
chk("ln 2.5", f(math.log(2.5), 3))
assert max(abs(math.log1p(v) - (v - v * v / 2)) for v in (-0.1, 0.1)) < 4e-4

# ---------------------------------------------------------------- Example fisher
i, pi = 0.01725, 0.018
chk("real exact %", f(100 * ((1 + i) / (1 + pi) - 1), 5))
chk("i - pi %", f(100 * (i - pi), 5))
chk("second order %", f(100 * ((i - pi) - pi * (i - pi)), 5))
assert abs((1 + i) / (1 + pi) - 1 - ((i - pi) - pi * (i - pi))) < 1e-6

# ---------------------------------------------------------------- remainder exhibit
for v in (-0.20, -0.10, -0.05, -0.01, 0.01, 0.05, 0.10, 0.20, 0.50):
    ex, t2 = math.log1p(v), v - v * v / 2
    bound = abs(v) ** 3 / (3 * (1 + min(v, 0.0)) ** 3)
    assert abs(ex - t2) <= bound
    de = 7 if abs(v) < 0.05 else 6  # the +-0.01 rows show one more digit for the error and the bound
    err = f(ex - t2, de) if v < 0 else f"+{f(ex - t2, de)}"
    chk(f"remainder row x={v:+.2f}", f"{f(v, 2) if v < 0 else '+' + f(v, 2)} | {f(ex, 6)} | {f(t2, 6)} | {err} | "
        f"{f(bound, de)} |")

# ---------------------------------------------------------------- Example worstdays (0050's crash days)
big = {b["date"]: b for b in ST["big"]}
for dd, pct in (("2024-08-05", "9.130"), ("2025-04-07", "10.000")):
    b = big[dd]
    chk(f"{dd} fall %", f(-100 * b["R"], 3))
    assert f(-100 * b["R"], 3) == pct
    chk(f"{dd} R", f(b["R"], 6))
    chk(f"{dd} ln(1+R)", f(b["log"], 6))
    chk(f"{dd} T2", f(b["T2"], 6))
    chk(f"{dd} T1 error bp", f(1e4 * (b["T1"] - b["log"]), 1))
    chk(f"{dd} T2 error bp", f(1e4 * (b["T2"] - b["log"]), 1))
    chk(f"{dd} bound bp", f(1e4 * b["bound2"], 1))
own = ST["own0050"]["worst"]
assert [w["date"] for w in own] == ["2025-04-07", "2024-08-05", "2018-10-11"], own
chk("third-worst day % (2018-10-11)", f(100 * own[2]["R"], 2))
same("bound 2024 from printed", f(1e4 * 0.091299**3 / (3 * 0.908701**3), 1), f(1e4 * big["2024-08-05"]["bound2"], 1))

# ---------------------------------------------------------------- Example rule72
R = 0.06
chk("doubling, unrounded constants", f(LN2 / R + LN2 / 2, 3))
chk("doubling, 0.693/R + 0.347", f(0.693 / R + 0.347, 3))
chk("doubling, exact", f(LN2 / math.log1p(R), 3))
chk("rule of 72 at 6%", f"{72 / 6:.0f}", text=False)
chk("R where 100 ln2 (1 + R/2) = 72, %", f(100 * 2 * (72 / (100 * LN2) - 1), 2))
lo, hi = 0.05, 0.10  # rule of 72 equals the exact doubling time
for _ in range(60):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if 72 / (100 * mid) > LN2 / math.log1p(mid) else (lo, mid)
chk("R where 72/(100R) is exact, %", f(100 * lo, 2))
chk("100 ln2, 50 ln2", f"{100 * LN2:.1f} + {50 * LN2:.1f}", text=False)

# ---------------------------------------------------------------- knowledge check: e^-0.3 with T4
t4 = sum((-0.3) ** k / math.factorial(k) for k in range(5))
chk("bound 0.3^5/120", f"{0.3**5 / 120 * 1e5:.3f}")
chk("e^-0.3", f(math.exp(-0.3), 7))
chk("T4(-0.3)", f(t4, 7))
chk("actual error x1e5", f((math.exp(-0.3) - t4) * 1e5, 2))

# ---------------------------------------------------------------- simple vs log exhibit
for v in (-0.5, -0.2, -0.1, -0.01, 0.01, 0.1, 0.2, 0.5, 1.0):
    r = math.log1p(v)
    dd = 3 if abs(v) < 0.05 else 2  # the +-1% rows show one more digit
    sr = f(100 * r, dd) if v < 0 else "+" + f(100 * r, dd)
    same(f"simplelog gap from printed R={v:+.0%}", f(100 * v - rd(100 * r, dd), dd), f(100 * (v - r), dd))
    chk(f"simplelog R={v:+.0%}", f"| {sr}% | {f(100 * (v - r), dd)}% | {f(100 * v * v / 2, dd)}% |")

# ---------------------------------------------------------------- Section 5: the gap in real data
chk("mean R %", f(100 * daily["meanR"], 4))
chk("mean r %", f(100 * daily["meanr"], 4))
chk("gap % per day", f(100 * daily["diff"], 4))
chk("gap bp", f(1e4 * daily["diff"], 2))
chk("half mean square bp", f(1e4 * daily["half_m2"], 3))
chk("half variance bp", f(1e4 * daily["half_var"], 3))
chk("code: mean R", f"{daily['meanR']:.6%}")
chk("code: mean r", f"{daily['meanr']:.6%}")
chk("code: gap bp", f"{daily['diff'] * 1e4:.3f}")
chk("gap x A, percentage points", f(daily["diff"] * full["A"] * 100, 1))

# ---------------------------------------------------------------- knowledge check: portfolio of two assets
chk("ln 1.02 %", f(100 * math.log(1.02), 3))
chk("ln 1.1, ln 0.9", f"{f(math.log(1.1), 5)}, {f(math.log(0.9), 5)}", text=False)
wl = 0.6 * math.log(1.1) + 0.4 * math.log(0.9)
chk("weighted log %", f(100 * wl, 3))
same("weighted log from printed logs", f(100 * (0.6 * 0.09531 + 0.4 * -0.10536), 3), f(100 * wl, 3))

# ---------------------------------------------------------------- frequency exhibit
# R-bar and s at five significant figures reproduce the printed approximations; errors are computed before
# rounding (approximation - exact, in bp), as the exhibit's note says.
FREQ_FMT = {"1d": (6, 4, 4, 2), "1w": (5, 4, 4, 2), "1mo": (4, 4, 4, 1), "1q": (4, 3, 3, 1), "1y": (3, 3, 2, 1)}
for fr in ST["freq"]:
    dm, ds, dv, de = FREQ_FMT[fr["freq"]]
    m_p, s_p = rd(100 * fr["mu"], dm) / 100, rd(100 * fr["sd"], ds) / 100
    a1, a2 = f(100 * fr["approx1"], dv), f(100 * fr["approx2"], dv)
    same(f"freq {fr['freq']} approx1 from printed", f(100 * (m_p - s_p**2 / 2), dv), a1)
    same(f"freq {fr['freq']} approx2 from printed", f(100 * (m_p - (s_p**2 + m_p**2) / 2), dv), a2)
    row = (f"{fr['n']:,} | {f(100 * fr['mu'], dm)}% | {f(100 * fr['sd'], ds)}% | {f(100 * fr['geo'], dv)}% | {a1}% | "
           f"{f(1e4 * fr['err1'], de)} | {f(100 * fr['g_log'], dv)}% | {a2}% | {f(1e4 * fr['err2'], de)}")
    chk(f"freq {fr['freq']}", row)
yr_f = ST["freq"][-1]
chk("annual max %", f(100 * yr_f["max"], 1))
chk("annual min %", f(100 * yr_f["min"], 1))

# ---------------------------------------------------------------- Example fiveyears: 0050 in 2020-2024
rets = [100 * years[str(y)]["ret0050"] for y in range(2020, 2025)]
printed = [rd(v, 2) for v in rets]
chk("2020-2024 returns", ", ".join(f"{v:.2f}%" for v in printed).replace("-", "−"), text=False)
Rs = np.array(rets) / 100
mu, s2 = Rs.mean(), Rs.var()
geo = np.prod(1 + Rs) ** (1 / 5) - 1
P = np.array(printed) / 100
same("mean from printed", f(100 * P.mean(), 2), f(100 * mu, 2))
same("variance from printed", f(P.var(), 5), f(s2, 5))
same("R_G from printed", f(100 * (np.prod(1 + P) ** 0.2 - 1), 2), f(100 * geo, 2))
chk("mean %", f(100 * mu, 2))
chk("variance", f(s2, 5))
chk("s %", f(100 * math.sqrt(s2), 2))
chk("s^2/2 %", f(100 * s2 / 2, 2))
chk("approx (3.9) %", f(100 * (mu - s2 / 2), 2))
chk("R_G %", f(100 * geo, 2))
same("approx from printed mean and half-variance", f(21.56 - 2.70, 2), f(100 * (mu - s2 / 2), 2))
chk("approx low by bp", f(1e4 * (geo - (mu - s2 / 2)), 0))
chk("overstatement pp", f(100 * (mu - geo), 1))

# ---------------------------------------------------------------- Example bet: +2% / -1%, whole capital staked
a, b = 0.02, -0.01
mu = (a + b) / 2
s2 = ((a - mu) ** 2 + (b - mu) ** 2) / 2
geo, g = math.sqrt((1 + a) * (1 + b)) - 1, (math.log1p(a) + math.log1p(b)) / 2
chk("s^2", f"{s2:.6f}")
chk("R_G %", f(100 * geo, 5))
chk("g %", f(100 * g, 5))
chk("(3.9) %", f(100 * (mu - s2 / 2), 5))
chk("(3.8) %", f(100 * (mu - (s2 + mu * mu) / 2), 5))
same("(3.9) error from printed", f(1e4 * (0.0048875 - 0.0048881), 3), f(1e4 * (mu - s2 / 2 - geo), 3))
same("(3.8) error from printed", f(1e4 * (0.0048750 - 0.0048761), 3), f(1e4 * (mu - (s2 + mu * mu) / 2 - g), 3))
chk("share of edge lost %", f(100 * (mu - geo) / mu, 1))

# ---------------------------------------------------------------- pitfall +100% / -50% and Practice Problem 6
chk("+100/-50 approx %", f(100 * (0.25 - 0.75**2 / 2), 1))
chk("PP6 exact %", f(100 * (math.sqrt(1.6 * 0.6) - 1), 3))
chk("PP6 gap pp", f(100 * abs(-0.025 - (math.sqrt(0.96) - 1)), 2))

# ---------------------------------------------------------------- knowledge check: two funds, 20 years
chk("(1.095/1.055)^20", f((1.095 / 1.055) ** 20, 2))
chk("e^(20 x 0.04) with (3.8)", f(math.exp(20 * ((0.1 - 0.02 / 2) - (0.1 - 0.10 / 2))), 2))

# ---------------------------------------------------------------- Section 7: decomposition exhibit and text
chk("log growth 0050", f(full["log0050"], 5))
chk("power 2 x log", f(full["power"], 4))
same("power from printed", f(2 * 2.30483, 4), f(full["power"], 4))
chk("G0^2", f(full["G0"] ** 2, 2))
chk("exact rebalancing", f(full["exact"], 5))
chk("T2", f(full["T2"], 5))
chk("T3", f(full["T3"], 5))
chk("T4", f(full["T4"], 5))
chk("residual", f(full["residual"], 4))
chk("00631L log growth", f(full["actual"], 4))
same("log points add up", f(4.6097 - 0.44729 - 0.3659, 4), f(full["actual"], 4))
chk("factor exact", f(math.exp(full["exact"]), 3))
chk("factor residual", f(math.exp(full["residual"]), 3))
chk("product of unrounded factors", f(full["G0"] ** 2 * math.exp(full["exact"]) * math.exp(full["residual"]), 2))
chk("product of printed factors (not printed)", f(100.45 * 0.639 * 0.694, 2), text=False)
chk("exact - T2 (< 0.0001)", f"{full['gap']:.6f}", text=False)
assert abs(full["gap"]) < 1e-4
chk("third-order term", f"+{f(full['term3'], 4)}")
chk("fourth-order term", f(full["term4"], 4))
chk("trend / asymmetry parts of 2 sum R^3", f"{full['term3_trend']:.4f} / {full['term3_central']:.4f}", text=False)
chk("running gap, max |.|", f(abs(full["path_gap_max"]), 4))
assert full["path_gap_date"] == "2025-04-09"
chk("drag 0.4473 / 11.94", f(0.4473 / 11.94, 4))
same("drag per year from printed", f(0.4473 / 11.94, 4), f(full["drag_per_year"], 4))
chk("s^2 A from printed s and A", f(0.012385**2 * 243.1, 4))
same("s^2 A", f(0.012385**2 * 243.1, 4), f(full["s2A"], 4))
chk("mean^2 A", f(full["mu2A"], 4))
same("mean^2 A from printed", f(0.000871**2 * 243.1, 4), f(full["mu2A"], 4))
assert min(y["RV"] for y in ST["years"][1:-1]) == years["2017"]["RV"]  # lowest variance of any full year
chk("end values: Taylor, exact daily 2x", f"{f(full['end_taylor'], 3)} and the exact daily 2× {f(full['end_exact2x'], 3)}")
chk("residual per year", f(full["residual_per_year"], 3))
same("residual per year from printed", f(-0.3659 / 11.94, 3), f(full["residual_per_year"], 3))
chk("residual per year, % of value", f(100 * math.expm1(full["residual_per_year"]), 1))
chk("drag per year, % of value", f(100 * math.expm1(-full["drag_per_year"]), 1), text=False)

# ---------------------------------------------------------------- yearly exhibit
sums = {"T2": 0.0, "exact": 0.0, "residual": 0.0}
for y in ST["years"]:
    p0050 = rd(100 * y["ret0050"], 3)
    same(f"{y['label']} 2 x printed 0050", f(2 * p0050, 2), f(100 * y["twice0050"], 2))
    row = (f"{p0050:.3f}% | {f(100 * y['ret00631L'], 2)}% | {f(100 * y['twice0050'], 2)}% | {f(y['T2'], 4)} | "
           f"{f(y['exact'], 4)} | {'+' if y['residual'] > 0 else ''}{f(y['residual'], 4)}")
    chk(f"yearly {y['label']}", row)
    for k in sums:
        sums[k] += rd(y[k], 4)
chk("yearly sums T2, exact, residual", " ".join(f"{v:.4f}" for v in sums.values()), text=False)
assert abs(sums["T2"] - full["T2"]) < 2e-4 and abs(sums["exact"] - full["exact"]) < 2e-4
assert abs(sums["residual"] - full["residual"]) < 2e-4
gaps = {y["label"]: y["gap"] for y in ST["years"]}
assert max(abs(v) for v in gaps.values()) == abs(gaps["2026"]) and f(gaps["2026"], 4) == "0.0025"
chk("2026 gap exact - T2", f(gaps["2026"], 4))
full_years = [years[str(y)]["residual"] for y in range(2015, 2026)]
chk("mean residual 2015-2025", f(np.mean(full_years), 3))
chk("residual 2021, 2024, 2026", f"{f(years['2021']['residual'], 3)}, {f(years['2024']['residual'], 3)}, "
    f"{f(years['2026']['residual'], 3)}", text=False)
for yy, k in (("2017", "exact2x"), ("2017", "twice0050"), ("2022", "exact2x"), ("2022", "ret0050"),
              ("2022", "twice0050"), ("2022", "ret00631L"), ("2015", "exact2x"), ("2015", "ret00631L"),
              ("2015", "twice0050")):
    chk(f"{yy} {k} %", f(100 * abs(years[yy][k]), 1))

# ---------------------------------------------------------------- Example tqqq: TQQQ in 2022
chk("QQQ closes", "386.63 to 260.68", text=False)
chk("3 ln G", f(q22["power"], 5))
chk("G^3", f(q22["G"] ** 3, 4))
chk("RV", f(q22["RV"], 4))
chk("sqrt RV %", f(100 * q22["sqrtRV"], 1))
chk("-3 RV", f(-3 * rd(q22["RV"], 4), 4))
chk("third-order", f(q22["T3"], 4))
chk("exact rebalancing", f(q22["exact"], 4))
chk("exact rebalancing (5 dp)", f(q22["exact"], 5))
chk("ln(8.27/39.55)", f(math.log(8.27 / 39.55), 5))
assert (q22["tqqq_first"], q22["tqqq_last"]) == (39.55, 8.27)
chk("residual vs exact", f(q22["residual"], 4))
same("residual from printed", f(-1.56493 + 1.18252 + 0.31325, 4), f(q22["residual"], 4))
chk("residual, % of value", f(100 * -math.expm1(q22["residual"]), 1))
chk("residual vs second order", f(q22["residual_vs_T2"], 4))
same("residual vs T2 from printed", f(-1.56493 + 1.18252 + 0.30900, 4), f(q22["residual_vs_T2"], 4))
costs = 0.0086 + 2 * 0.0168  # expense ratio after waivers (1 Oct 2022) + 2 x average effective fed funds 2022
chk("costs, log points", f(costs, 3))
same("costs from printed terms", f(0.0086 + 2 * 0.0168, 3), "0.042")
chk("costs / residual (roughly three-fifths)", f(costs / -q22["residual"], 2), text=False)
assert 0.55 < costs / -q22["residual"] < 0.65
# benchmark difference: QQQ's adjusted close includes its dividends; TQQQ targets the NDX price index
chk("QQQ dividends 2022, log points", f(q22["div_qqq"], 4))
chk("3 x dividends", f(3 * q22["div_qqq"], 3))
same("3 x printed 0.0074", f(3 * 0.0074, 3), f(3 * q22["div_qqq"], 3))
assert 3 * q22["div_qqq"] > 0.5 * (-q22["residual"] - costs)  # most of the rest
assert (q22["qqq_close_first"], q22["qqq_close_last"]) == (397.85, 266.28)
chk("residual vs unadjusted QQQ", f(q22["residual_unadj"], 3))
same("residual vs unadjusted from printed", f(-0.0692 + 0.022, 3), f(q22["residual_unadj"], 3))
chk("beyond fees and financing", f(-q22["residual_unadj"] - costs, 3))
same("beyond fees and financing from printed", f(0.047 - 0.042, 3), f(-q22["residual_unadj"] - costs, 3))
chk("e^(-0.309)", f(math.exp(-0.309), 3))
chk("Taylor value 0.3065 x 0.734", f(0.3065 * 0.734, 3))
chk("Taylor loss %", f(100 * (1 - q22["taylor_value"]), 1))
chk("exact loss %", f(100 * (1 - q22["exact_value"]), 1))
# the same benchmark on QQQ's unadjusted closes, which approximate the NDX price index that TQQQ targets
chk("QQQ unadjusted closes", "unadjusted closes (397.85 to 266.28)")
Gu3 = q22["G_unadj"] ** 3
chk("G_u^3", f(Gu3, 4))
same("G_u^3 from printed closes", f((266.28 / 397.85) ** 3, 4), f(Gu3, 4))
same("G_u^3 = exp(3 ln G_u)", f(math.exp(q22["power_unadj"]), 4), f(Gu3, 4))
same("e^(-3 RV) on unadjusted closes", f(math.exp(-3 * q22["RV_unadj"]), 3), "0.734")
chk("unadjusted benchmark 0.2998 x 0.734", f(0.2998 * 0.734, 3))
same("unadjusted benchmark, unrounded", f(q22["taylor_value_unadj"], 3), f(0.2998 * 0.734, 3))
chk("unadjusted benchmark loss %", f(100 * (1 - 0.220), 1))
same("unadjusted benchmark loss, unrounded", f(100 * (1 - q22["taylor_value_unadj"]), 1), "78.0")
chk("unadjusted exact-effect loss % (not printed)", f(100 * (1 - q22["exact_value_unadj"]), 1), text=False)

# ---------------------------------------------------------------- knowledge check: flat index, RV = 0.04
chk("2x", f(100 * math.expm1(-0.04), 1))
chk("3x", f(100 * math.expm1(-0.12), 1))


# ---------------------------------------------------------------- Example bond and the bond exhibit
def price(y, c=0.02, n=10, face=100.0):
    return sum(c * face / (1 + y) ** t for t in range(1, n + 1)) + face / (1 + y) ** n


y0 = 0.02
P0 = price(y0)
dP = -sum(t * 2 / (1 + y0) ** (t + 1) for t in range(1, 11)) - 10 * 100 / (1 + y0) ** 11
d2P = sum(t * (t + 1) * 2 / (1 + y0) ** (t + 2) for t in range(1, 11)) + 110 * 100 / (1 + y0) ** 12
Dm, C = -dP / P0, d2P / P0
chk("D_mod", f(Dm, 4))
chk("C", f(C, 3))
errs = {}
for dy in (0.01, -0.01, 0.03):
    ex = price(y0 + dy) / P0 - 1
    d1, d2 = -Dm * dy, -Dm * dy + 0.5 * C * dy * dy
    same(f"dy={dy} duration from printed", f(100 * (-8.9826 * dy), 4), f(100 * d1, 4))
    same(f"dy={dy} dur+conv from printed", f(100 * (-8.9826 * dy + 0.5 * 93.995 * dy * dy), 4), f(100 * d2, 4))
    chk(f"bond dy={dy:+.2f}", f"{f(100 * ex, 4)}% | {f(100 * d1, 4)}% | {f(100 * d2, 4)}%".replace("| -", "| −"),
        text=False)
    errs[dy] = (rd(100 * ex, 4) - rd(100 * d1, 4), rd(100 * ex, 4) - rd(100 * d2, 4))
chk("duration-only errors at +-100 bp", f"{abs(errs[0.01][0]):.4f}, {abs(errs[-0.01][0]):.4f}", text=False)
chk("second-order errors at +-100 bp", f"{abs(errs[0.01][1]):.4f}, {abs(errs[-0.01][1]):.4f}", text=False)
chk("second-order error at +300 bp", f(abs(errs[0.03][1]), 4))
chk("ratio +300 / +100", f(abs(errs[0.03][1]) / abs(errs[0.01][1]), 1), text=False)

# ---------------------------------------------------------------- practice problems
chk("PP2 T2", f(0.08 - 0.08**2 / 2, 4))
chk("PP2 ln 1.08 %", f(100 * math.log(1.08), 3))
chk("PP2 gap to T2 (points)", f(100 * (math.log(1.08) - 0.0768), 3))
chk("PP2 third-order term (points)", f(100 * 0.08**3 / 3, 3))
chk("PP3 ln 0.92", f(math.log(0.92), 7))
chk("PP3 error", f(math.log(0.92) - (-0.0832), 7))
chk("PP3 bound", f(0.000512 / (3 * 0.778688), 6))
chk("PP3 share of bound %", f(100 * (math.log(0.92) + 0.0832) / -(0.000512 / (3 * 0.778688)), 0), text=False)
a3 = np.array([0.30, -0.20, 0.10])
chk("PP4 R_G %", f(100 * (np.prod(1 + a3) ** (1 / 3) - 1), 3))
chk("PP4 mean %", f(100 * a3.mean(), 3))
chk("PP4 population variance", f(a3.var(), 5))
chk("PP4 sample variance", f(a3.var(ddof=1), 5))
chk("PP4 (3.9) population %", f(100 * (a3.mean() - a3.var() / 2), 3))
chk("PP4 (3.9) sample %", f(100 * (a3.mean() - a3.var(ddof=1) / 2), 2))
chk("PP7 fund", f(100 * (1.2 * 0.8 - 1), 2))
chk("PP7 Taylor", f(0.9801 * math.exp(-0.02), 4))
chk("PP7 Taylor return %", f(100 * (0.9607 - 1), 2))
chk("PP7 fund log return", f(math.log(0.96), 4))
chk("PP7 power", f(2 * math.log(0.99), 4))
chk("PP7 drag", f(math.log(0.96) - 2 * math.log(0.99), 4))
chk("PP8 e^-0.27", f(math.exp(-0.27), 4))
chk("PP8 value", f(1.728 * 0.7634, 3))
chk("PP8 G^3 - 1 %", f(100 * (1.2**3 - 1), 1), text=False)
for yy, Gp, RVp in (("2017", "1.1813", "0.0088"), ("2015", "0.9369", "0.0266")):
    assert f(1 + years[yy]["ret0050"], 4) == Gp and f(years[yy]["RV"], 4) == RVp
    chk(f"PP9 {yy} |1-1/G|, sqrt RV", f"{f(abs(1 - 1 / float(Gp)), 3)}, {f(math.sqrt(float(RVp)), 3)}", text=False)
chk("PP10", f(100 * (-7.5 * 0.015 + 0.5 * 70 * 0.015**2), 2))
chk("PP13 exact %", f(100 * (1.03 / 1.025 - 1), 4))
df = pl.read_parquet(HERE / "processed" / "etf_daily_returns.parquet").with_columns(pl.col("date").str.to_date())
m = df["date"].dt.year().is_between(2020, 2023).to_numpy()
R0, RL = df["R_0050"].to_numpy()[m], df["R_00631L"].to_numpy()[m]
pw, exd = 2 * np.log1p(R0).sum(), (np.log1p(2 * R0) - 2 * np.log1p(R0)).sum()
t2, act = -(R0**2).sum(), np.log1p(RL).sum()
t3 = t2 + 2 * (R0**3).sum()
for lab, v in (("power", pw), ("exact", exd), ("T2", t2), ("T3", t3), ("residual", act - pw - exd), ("actual", act)):
    chk(f"PP14 {lab}", f(v, 5))
same("PP14 parts add up", f(rd(pw, 5) + rd(exd, 5) + rd(act - pw - exd, 5), 5), f(act, 5))
chk("PP14 00631L %", f(100 * math.expm1(act), 1))
chk("PP14 yearly residuals as printed", f(sum(rd(years[str(y)]["residual"], 4) for y in range(2020, 2024)), 4))
print("all LM3 numbers check out")
