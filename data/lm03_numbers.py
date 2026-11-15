"""Every number quoted in LM3 (src/lm03.md), recomputed and checked against the text.

Run after data/lm03_stats.py:  uv run python data/lm03_numbers.py

Each check prints a label and the value as the module prints it, and fails if the value no longer appears in
src/lm03.md. Where the module shows a computation, the check also recomputes it from the printed (rounded) inputs,
so that a reader who redoes the arithmetic gets the printed result.

The 2022 example of QQQ and TQQQ (and its lines in the case and the paradox exhibit) uses FinMind's adjusted closes,
which FinMind rebuilds at every retrieval. Its strings are checked whole, each occurring once, and a seeded simulation
of re-fetches asserts that none of them changes (see the section "Example tqqq").
"""

import csv
import io
import json
import math
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import fetch_finmind as FF
import numpy as np
import polars as pl
from lm03_stats import WINDOW_2022, qqq_tqqq_2022

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
# the 2022 sentence of the case and the exhibit's 2022 row and note: in the section "Example tqqq" below
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

# ---------------------------------------------------------------- Example tqqq, and 2022 in the case and the exhibit
# FinMind rebuilds USStockPrice's Adj_Close backward from the latest day at every retrieval: each later distribution
# rescales the column and re-rounds it to cents, and data/fetch_finmind.py accepts such a re-fetch (other columns
# identical, the adjusted column within its rounding allowance). The module therefore quotes the adjusted levels with
# their retrieval date and prints each derived value only to digits that a re-fetch cannot move. tqqq_phrases()
# builds every printed string of the case's 2022 sentence, the exhibit's 2022 row and note and Example tqqq from the
# computed values; each occurs once in the module, and the stability check rebuilds them from simulated re-fetches.
LEVELS = {  # the printed levels: raw file, column, last close of 2021, last close of 2022
    "QQQ adjusted": ("QQQ__us_2022.csv", "adj_close", 386.63, 260.68),
    "TQQQ adjusted": ("TQQQ__us_2022.csv", "adj_close", 39.55, 8.27),
    "QQQ close": ("QQQ__us_2022.csv", "close", 397.85, 266.28),
}
COST = 0.0086 + 2 * 0.0168  # expense ratio after waivers (1 Oct 2022) + 2 x average effective fed funds 2022
MOVE = "0.002"              # printed: how far a later retrieval can move the residual (checked after refetch)
MANIFEST = {e["path"]: e for e in json.loads((HERE / "raw_manifest.json").read_text(encoding="utf-8"))["files"]}
RAW_FILES = {name: (HERE / "raw" / name).read_bytes() for name in ("QQQ__us_2022.csv", "TQQQ__us_2022.csv")}
SEED, N_SIM, FACTORS = 20261115, 1000, (0.80, 1.00)   # the stability check's design (see refetch)


def lost(x, k):
    """A loss printed without its sign ("lost 32.6%"); a gain would print with a minus sign and fail the match."""
    return f(-100 * x, k)


def window(data):
    """Dates, adjusted closes and closes of a raw file inside WINDOW_2022, parsed as lm03_stats parses them."""
    rows = [r for r in csv.DictReader(io.StringIO(data.decode("utf-8")))
            if WINDOW_2022[0] <= r["date"] <= WINDOW_2022[1]]
    return ([r["date"] for r in rows], np.array([float(r["adj_close"]) for r in rows]),
            np.array([float(r["close"]) for r in rows]))


def example_2022(files):
    """lm03_stats.qqq_tqqq_2022 on the bytes of the two raw files."""
    dq, qa, qc = window(files["QQQ__us_2022.csv"])
    dt, ta, tc = window(files["TQQQ__us_2022.csv"])
    assert dq == dt and (dq[0], dq[-1]) == WINDOW_2022
    return qqq_tqqq_2022(qa, qc, ta, tc)


def check_levels(files):
    """The printed levels against the data. A file with its registered bytes, and any close (fetch_finmind requires
    the closes to reproduce exactly), must hold the printed levels exactly. A re-fetched adjusted column must pass
    fetch_finmind's check, and the printed levels' ratio must equal the data's within that check's daily allowance
    (ADJ_K half-cents on each of the four values): a re-fetch passes, a level mistyped beyond its cents fails."""
    for label, (name, col, p0, p1) in LEVELS.items():
        data = files[name]
        _, adj, close = window(data)
        d0, d1 = (float(close[0]), float(close[-1])) if col == "close" else (float(adj[0]), float(adj[-1]))
        if col == "close" or FF.sha256(data) == MANIFEST[name]["sha256"]:
            assert (d0, d1) == (p0, p1), f"{label}: printed {p0} to {p1}, data {d0} to {d1}"
        else:
            assert FF.matches(MANIFEST[name], data), f"{name} is not a re-fetch that fetch_finmind accepts"
            tol = FF.ADJ_K * 0.005 * (1 / p0 + 1 / p1 + 1 / d0 + 1 / d1)
            gap = abs(math.log(p1 / p0) - math.log(d1 / d0))
            assert gap <= tol, f"{label}: printed ratio {p1}/{p0} is {gap:.5f} off the data's {d1}/{d0} (> {tol:.5f})"


def tqqq_phrases(q):
    """(label, string) for every printed string of the 2022 example, the case and the exhibit, built from q
    (qqq_tqqq_2022) and the printed levels, with ASCII minus signs as in TEXT."""
    (a0, a1), (t0, t1), (c0, c1) = ((v[2], v[3]) for v in LEVELS.values())
    qqq, tqqq, thrice = f(100 * q["QQQ"], 1), f(100 * q["TQQQ"], 1), f(100 * q["thrice"], 0)
    res, bench_u = math.exp(q["residual"]), q["taylor_value_unadj"]
    return [
        ("case, 2022", (f"QQQ lost {lost(q['QQQ'], 1)}%; the 3× fund TQQQ lost {lost(q['TQQQ'], 1)}%. Three times "
                       f"QQQ's loss is {thrice}%, so TQQQ lost")),
        ("exhibit, 2022 row", f"| Calendar 2022 | QQQ: {qqq}% | TQQQ (3×): {tqqq}% | 3 × ({qqq}%) = {thrice}% |"),
        ("exhibit note", (f"QQQ and TQQQ use adjusted closes, which include their distributions; on its close alone, "
                         f"TQQQ lost {lost(q['TQQQ_close'], 1)}%.")),
        ("levels", (f"In 2022 QQQ's adjusted close fell from {a0:.2f} to {a1:.2f} ({qqq}%) and TQQQ's from {t0:.2f} to "
                   f"{t1:.2f} ({tqqq}%). These levels are FinMind's as retrieved on 10 October 2026")),
        ("RV", (rf"realized variance $\mathrm{{RV}}={f(q['RV'], 3)}$, a realized volatility $\sqrt{{\mathrm{{RV}}}}$ "
               rf"of {f(100 * q['sqrtRV'], 1)}%.")),
        ("power", (rf"Index power: $G={a1:.2f}/{a0:.2f}$, so the power term $G^3$ alone is a "
                  rf"{lost(q['G'] ** 3 - 1, 0)}% loss.")),
        ("drag", (rf"$-\tfrac{{3\cdot2}}{{2}}\mathrm{{RV}}=-3\times{f(q['RV'], 3)}={f(q['T2'], 3)}$; adding the "
                 rf"third-order term $8\sum R_t^3$ gives ${f(q['T3'], 3)}$. The exact rebalancing effect "
                 rf"$\sum[\ln(1+3R_t)-3\ln(1+R_t)]$ is ${f(q['exact'], 3)}$.")),
        ("residual", (rf"Residual: TQQQ's growth factor was ${t1:.2f}/{t0:.2f}={f(q['GT'], 3)}$. The power and the "
                     rf"exact effect alone give $G^3e^{{{f(q['exact'], 3)}}}={f(q['exact_value'], 3)}$, so the "
                     rf"residual factor is ${f(q['GT'], 3)}/{f(q['exact_value'], 3)}={f(res, 2)}$. In log points the "
                     rf"residual is about ${f(q['residual'], 2)}$, or {lost(res - 1, 0)}% of value. Against the "
                     rf"second-order drag it is {f(q['T2'] - q['exact'], 3)} more negative.")),
        ("precision", (f"coarse near its year-end level of {t1:.2f}. A later retrieval can therefore move the residual "
                      f"by about {MOVE}, so it is quoted to two decimals.")),
        ("cost", rf"Roughly three-fifths of the residual is cost, about $0.0086+2\times0.0168={f(COST, 3)}$."),
        ("dividends", (rf"Most of the rest, about $3\times{f(q['div_qqq'], 3)}={f(3 * q['div_qqq'], 2)}$, is a "
                      rf"benchmark difference. QQQ's adjusted close includes its dividends, worth "
                      rf"{f(q['div_qqq'], 3)} log points in 2022.")),
        ("unadjusted residual", (f"Against QQQ's unadjusted close the residual is about {f(q['residual_unadj'], 2)}. "
                                f"Fees and financing leave less than 0.01 of it")),
        ("resolution", (rf"“3 × {qqq}% = {thrice}%” compares the fund to the wrong benchmark. The right benchmark is "
                       rf"$G^3e^{{-3\,\mathrm{{RV}}}}={f(q['taylor_value'], 3)}$, a {lost(q['taylor_value'] - 1, 1)}% "
                       rf"loss before costs ({lost(q['exact_value'] - 1, 1)}% with the exact rebalancing effect). On "
                       rf"QQQ's unadjusted closes ({c0:.2f} to {c1:.2f}), which approximate the index TQQQ targets, it "
                       rf"is ${f(q['G_unadj'] ** 3, 4)}\times{f(math.exp(-3 * q['RV_unadj']), 3)}={f(bench_u, 3)}$, a "
                       rf"{lost(bench_u - 1, 1)}% loss.")),
    ]


def tqqq_claims(q):
    """The comparisons the example states in words; they must hold on every retrieval."""
    assert q["QQQ"] < 0 and q["thrice"] < q["TQQQ"] < 0      # TQQQ lost less than three times QQQ's loss
    assert q["TQQQ_close"] < q["TQQQ"]                       # the close alone leaves out TQQQ's distribution
    assert q["residual_vs_T2"] < q["residual"] < 0           # more negative against the second-order drag
    assert 0.55 < COST / -q["residual"] < 0.65               # roughly three-fifths of the residual is cost
    assert 3 * q["div_qqq"] > 0.5 * (-q["residual"] - COST)  # most of the rest is the benchmark difference
    assert 0 < -q["residual_unadj"] - COST < 0.01            # fees and financing leave less than 0.01


qq = example_2022(RAW_FILES)
assert all(math.isclose(v, q22[k], rel_tol=0, abs_tol=1e-12) for k, v in qq.items() if k != "n"), "stats JSON is stale"
check_levels(RAW_FILES)
tqqq_claims(qq)
PHRASES = tqqq_phrases(qq)
for label, s in PHRASES:
    n = TEXT.count(s)
    print(f"{'2022: ' + label:44s} {s[:70]}{'…' if len(s) > 70 else ''}")
    assert n == 1, f"2022 {label}: occurs {n} times in src/lm03.md, not once: {s}"
# a reader who redoes the arithmetic from the printed numbers gets the printed results
(a0, a1), (t0, t1), (c0, c1) = ((v[2], v[3]) for v in LEVELS.values())
resf = math.exp(qq["residual"])
same("QQQ % from printed levels", f(100 * (a1 / a0 - 1), 1), f(100 * qq["QQQ"], 1))
same("TQQQ % from printed levels", f(100 * (t1 / t0 - 1), 1), f(100 * qq["TQQQ"], 1))
same("3 x printed QQQ %", f(3 * rd(100 * qq["QQQ"], 1), 0), f(100 * qq["thrice"], 0))
same("power loss from printed levels", f(100 * (1 - (a1 / a0) ** 3), 0), lost(qq["G"] ** 3 - 1, 0))
same("-3 x printed RV", f(-3 * rd(qq["RV"], 3), 3), f(qq["T2"], 3))
same("growth factor from printed levels", f(t1 / t0, 3), f(qq["GT"], 3))
same("G^3 e^(printed exact)", f((a1 / a0) ** 3 * math.exp(rd(qq["exact"], 3)), 3), f(qq["exact_value"], 3))
same("residual factor from printed factors", f(rd(qq["GT"], 3) / rd(qq["exact_value"], 3), 2), f(resf, 2))
same("log residual from printed factor", f(math.log(rd(resf, 2)), 2), f(qq["residual"], 2))
same("% of value from printed factor", f(100 * (1 - rd(resf, 2)), 0), lost(resf - 1, 0))
same("printed drags differ by", f(rd(qq["T2"], 3) - rd(qq["exact"], 3), 3), f(qq["T2"] - qq["exact"], 3))
assert 0.55 < rd(COST, 3) / -rd(qq["residual"], 2) < 0.65                       # three-fifths, from printed
same("3 x printed dividends", f(3 * rd(qq["div_qqq"], 3), 2), f(3 * qq["div_qqq"], 2))
assert rd(3 * qq["div_qqq"], 2) > 0.5 * (-rd(qq["residual"], 2) - rd(COST, 3))   # most of the rest, from printed
assert 0 < -rd(qq["residual_unadj"], 2) - rd(COST, 3) < 0.01                    # less than 0.01, from printed
same("benchmark from printed levels and RV", f((a1 / a0) ** 3 * math.exp(-3 * rd(qq["RV"], 3)), 3),
     f(qq["taylor_value"], 3))
same("loss from printed benchmark", f(100 * (1 - rd(qq["taylor_value"], 3)), 1), lost(qq["taylor_value"] - 1, 1))
same("exact-effect loss from printed 0.224", f(100 * (1 - rd(qq["exact_value"], 3)), 1),
     lost(qq["exact_value"] - 1, 1))
same("G_u^3 from printed closes", f((c1 / c0) ** 3, 4), f(qq["G_unadj"] ** 3, 4))
same("e^(-3 x printed RV), unadjusted", f(math.exp(-3 * rd(qq["RV"], 3)), 3), f(math.exp(-3 * qq["RV_unadj"]), 3))
same("unadjusted benchmark from printed factors",
     f(rd(qq["G_unadj"] ** 3, 4) * rd(math.exp(-3 * qq["RV_unadj"]), 3), 3), f(qq["taylor_value_unadj"], 3))
same("unadjusted loss from printed benchmark", f(100 * (1 - rd(qq["taylor_value_unadj"], 3)), 1),
     lost(qq["taylor_value_unadj"] - 1, 1))


def refetch(rng, name):
    """One simulated re-fetch of a raw file. FinMind rounds each adjusted price (the close times its distribution
    factor) to cents, so the unrounded value behind a registered cell a lies within half a cent of it, and a later
    retrieval rounds that value times a new factor f. A simulated cell is therefore round((a + u) f, 2), with u drawn
    uniformly within half a cent for every cell and f uniformly from FACTORS for the file (0.80 is 20% of
    distributions, about 30 years of QQQ's 2022 yield). It lands within 0.005 (1 + f), at most a cent, of a f: on some
    days a cent away from a plain re-rounding of a f, never further than a re-rounding can reach. (Adding a cent to a
    re-rounded value would reach 1.5 cents, which no retrieval can produce.) Every such file passes fetch_finmind's
    check, as asserted here."""
    rows = list(csv.reader(io.StringIO(RAW_FILES[name].decode("utf-8"))))
    j = rows[0].index("adj_close")
    a = np.array([float(r[j]) for r in rows[1:]])
    new = np.round((a + rng.uniform(-0.005, 0.005, len(a))) * rng.uniform(*FACTORS), 2)
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerows(
        [rows[0], *([*r[:j], f"{v:.2f}", *r[j + 1:]] for r, v in zip(rows[1:], new, strict=True))])
    data = buf.getvalue().encode("utf-8")
    assert FF.adjusted_match(MANIFEST[name], data), f"{name}: a simulated re-fetch fails fetch_finmind's check"
    return data


# "A later retrieval can therefore move the residual by about 0.002, so it is quoted to two decimals": a cent on each
# of the four end values of the growth factors moves it by up to MOVE (to first order; the daily path adds little), no
# simulated re-fetch below moves it by 0.0025 or more, and some move its third decimal.
same("residual move from a cent per end value", f(0.01 * (1 / t0 + 1 / t1 + 3 / a0 + 3 / a1), 3), MOVE)

# The stability check is a test of the printed digits, so it starts from the registered bytes. On a re-fetched
# checkout the data are themselves one such re-fetch: the strings above were just checked on them.
if all(FF.sha256(b) == MANIFEST[name]["sha256"] for name, b in RAW_FILES.items()):
    rng = np.random.default_rng(SEED)
    moves, third = [], 0
    for i in range(N_SIM):
        sim = {name: refetch(rng, name) for name in RAW_FILES}
        check_levels(sim)
        qs = example_2022(sim)
        tqqq_claims(qs)
        for (label, s), (_, b) in zip(tqqq_phrases(qs), PHRASES, strict=True):
            assert s == b, f"simulated re-fetch {i}: 2022 {label} would print\n  {s}\nnot\n  {b}"
        moves.append(abs(qs["residual"] - qq["residual"]))
        third += f(qs["residual"], 3) != f(qq["residual"], 3)
    assert max(moves) < float(MOVE) + 0.0005, f"a simulated re-fetch moved the residual by {max(moves):.4f}"
    assert third > 0, "no simulated re-fetch moved the residual's third decimal"
    print(f"2022 stability: seed {SEED}, {N_SIM} simulated re-fetches (factors {FACTORS[0]:.2f}-{FACTORS[1]:.2f}, "
          f"each value within a cent of the rescaled registered one): all {len(PHRASES)} strings unchanged; the "
          f"residual moved by at most {max(moves):.4f}, its third decimal in {third}")
else:
    print("2022 stability: skipped, data/raw holds a re-fetch of QQQ or TQQQ (the strings were checked on it)")

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
