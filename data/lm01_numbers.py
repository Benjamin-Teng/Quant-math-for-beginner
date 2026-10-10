"""Every number quoted in LM1 (Exponentials, Logarithms and Compounding).

Run after build_series.py:  python3 data/lm01_numbers.py
Prints each quantity at the precision used in src/lm01.md, grouped by the place it appears.

Notation follows AUTHORING.md section 6: T = number of returns (or periods), tau = a span in years
(calendar days / 365.25), A = periods per year used to annualize, DD = drawdown, D = cash dividend.
Analytic quantities (rate tables) are computed in exact decimal arithmetic and rounded half up, so that
values such as 15.5625% print as 15.563% rather than suffering binary floating-point artefacts.

Inputs: processed/etf_daily_returns.parquet (0050 and 00631L total returns on common dates, base close
2014-10-31), raw/0050__*.csv and raw/00631L__*.csv (trading calendars), raw/0050_dividends.csv.
"""
import glob
import json
import math
import datetime as dt
from decimal import Decimal as Dec, ROUND_HALF_UP, getcontext
from pathlib import Path

import numpy as np
import polars as pl

getcontext().prec = 50
HERE = Path(__file__).resolve().parent
LN2, E = math.log(2), math.e
BASE = dt.date(2014, 10, 31)                      # last close before the first daily return
YEAR = 365.25                                     # a horizon in years is calendar days / 365.25 (AUTHORING 8)
OUT = {}


def P(label, *vals):
    print(f"{label:<46s}", *vals)


def head(t):
    print("\n" + "=" * 100 + "\n" + t + "\n" + "=" * 100)


def hu(x, dp):
    """Round half up: x a Decimal, str or float (floats via their shortest repr)."""
    d = x if isinstance(x, Dec) else Dec(repr(float(x))) if not isinstance(x, str) else Dec(x)
    return str(d.quantize(Dec(1).scaleb(-dp), rounding=ROUND_HALF_UP))


def pct(x, dp):
    d = x if isinstance(x, Dec) else Dec(repr(float(x)))
    return hu(d * 100, dp) + "%"


# ---------------------------------------------------------------- data
df = pl.read_parquet(HERE / "processed" / "etf_daily_returns.parquet").with_columns(pl.col("date").str.to_date())
R = df["R_0050"].to_numpy()
RL = df["R_00631L"].to_numpy()
dates = [BASE] + df["date"].to_list()
W = np.concatenate([[1.0], np.cumprod(1 + R)])     # 0050 total-return index, W[0] = 1 on 2014-10-31
WL = np.concatenate([[1.0], np.cumprod(1 + RL)])   # 00631L
IDX = {d: k for k, d in enumerate(dates)}
END = dates[-1]
yrs = np.array([d.year for d in df["date"].to_list()])


def on_or_before(d):
    while d not in IDX:
        d -= dt.timedelta(days=1)
    return d


def growth(a, b):
    """Total-return growth factor of 0050 from the close of a to the close of b."""
    return W[IDX[b]] / W[IDX[a]]


# ================================================================ 1. Introduction: the case
head("1. INTRODUCTION — motivating case")
G = W[-1]
lnG = math.log(G)
days = (END - BASE).days
tau = days / YEAR
RG = G ** (1 / tau) - 1
g = lnG / tau
OUT.update(G=G, lnG=lnG, tau=tau, RG=RG, g=g)
P("period", BASE, "->", END, f"days={days}", f"tau=days/365.25={tau:.4f} ({tau:.2f} years)")
P("growth factor G", f"{G:.6f} -> {G:.4f}")
P("NT$100,000 becomes", f"NT${100000 * G:,.0f}")
P("holding-period (total) return G-1", f"{G - 1:.4%} -> +{(G - 1) * 100:.2f}%")
P("annualized R_G = G^(1/tau)-1", f"{RG:.4%} -> {RG:.2%} ({RG:.1%})")
P("log growth ln G", f"{lnG:.5f} -> {lnG:.4f}")
P("continuously compounded g = lnG/tau", f"{g:.4%} -> {g:.2%} ({g:.1%})")
P("check ln(1+R_G) = g", f"{math.log1p(RG):.6f} vs {g:.6f}")
P("simple annualization (G-1)/tau", f"{(G - 1) / tau:.2%}", f"check 1+0.7558*11.94={1 + 0.7558 * 11.94:.2f}")
P("simple annualization / R_G (1 dp)", f"{(G - 1) / tau / RG:.1f}")

# ================================================================ 2. Exponents and logarithms
head("2. EXPONENTS AND LOGARITHMS")
p0, p1 = 65.30, 114.95 * 4                          # close 2014-10-31; close 2026-10-08 in pre-split shares (4-for-1, 2025-06-18)
Gp = p1 / p0
dv = df.filter(pl.col("d0050") > 0).select("date", "p0050", "d0050")
div_log = float(np.log1p(dv["d0050"].to_numpy() / dv["p0050"].to_numpy()).sum())
OUT.update(G_price=Gp, div_log=div_log)
P("number of cash dividends in window", dv.height, dv["date"][0], "->", dv["date"][-1])
P("price-only: 114.95x4 / 65.30", f"P_end(pre-split)={p1:.2f}", f"G_P={Gp:.4f}", f"return={Gp - 1:.2%}")
P("ln G_P + sum ln(1+D/P) = ln G", f"{math.log(Gp):.4f} + {div_log:.4f} = {math.log(Gp) + div_log:.4f}", f"(ln G {lnG:.4f})")
P("exact check lnG - lnGp - div", f"{lnG - math.log(Gp) - div_log:.2e}")
P("price factor product with restated split day", f"{np.prod([W[i] / W[i - 1] / (1 + (df['d0050'][i - 1] / df['p0050'][i - 1])) for i in range(1, len(W))]):.4f}")
P("price product WITHOUT restating split day (wrong)", f"{Gp / 4:.4f}")
P("dividend share of log growth", f"{div_log / lnG:.1%}")
P("dividend effect e^0.3530 - 1, factor", f"{math.exp(div_log) - 1:.1%}", f"{math.exp(div_log):.3f}")
P("doublings: total, price, dividends", f"{lnG / LN2:.3f}", f"{math.log(Gp) / LN2:.3f}", f"{div_log / LN2:.3f}")
P("tenfold increases log10 G; ln 10", f"{lnG / math.log(10):.3f}", f"{math.log(10):.4f}")
P("price-only annualized, cc; dividends per year (log)", f"{Gp ** (1 / tau) - 1:.2%}", f"{math.log(Gp) / tau:.2%}", f"{div_log / tau:.2%}")
for lab, a, b in (("Apr-Aug 2015", "2015-04-27", "2015-08-24"), ("Jan-Apr 2025", "2025-01-07", "2025-04-09")):
    wa, wb = W[IDX[dt.date.fromisoformat(a)]], W[IDX[dt.date.fromisoformat(b)]]
    P(f"log-chart: {lab} decline {a}->{b}", f"W {wa:.2f}->{wb:.2f}", f"drop {wa - wb:.2f} units", f"{wb / wa - 1:.1%}", f"log points {math.log(wb / wa):.2f}")
P("ratio of unit drops 2025/2015", f"{(W[IDX[dt.date(2025, 1, 7)]] - W[IDX[dt.date(2025, 4, 9)]]) / (W[IDX[dt.date(2015, 4, 27)]] - W[IDX[dt.date(2015, 8, 24)]]):.1f}")
i7 = IDX[dt.date(2025, 4, 7)]; i9 = IDX[dt.date(2025, 4, 9)]
P("share of the Jan-Apr 2025 decline falling in April 7-9", f"{W[i9] / W[i7 - 1] - 1:.2%} of {W[i9] / W[IDX[dt.date(2025, 1, 7)]] - 1:.2%}")
prev = BASE
for lev in (2, 4, 8):
    k = int(np.argmax(W >= lev))
    P(f"doubling: first close W >= {lev}", dates[k], f"W={W[k]:.3f}", f"years since previous level {(dates[k] - prev).days / YEAR:.1f}")
    prev = dates[k]
P("KC: log2(1000) = ln1000/ln2", f"{math.log(1000):.4f}/{LN2:.4f} = {math.log(1000) / LN2:.2f}")
P("laws: 1.05^-1, 1.01725^(1/12)-1", f"{1.05 ** -1:.4f}", f"{1.01725 ** (1 / 12) - 1:.4%}")

# ================================================================ 3. Compounding and e
head("3. COMPOUNDING FREQUENCY AND THE NUMBER e (exact decimals, rounded half up)")
FREQ = [("Annual", 1), ("Semiannual", 2), ("Quarterly", 4), ("Monthly", 12), ("Weekly", 52), ("Daily", 365)]
r1, r2 = Dec("0.01725"), Dec("0.15")
P("EAR table: n | periodic i at 15% | EAR at 1.725% | EAR at 15%")
for lab, n in FREQ:
    P(f"   {lab:<10s} n={n:<4d}", pct(r2 / n, 4), pct((1 + r1 / n) ** n - 1, 4), pct((1 + r2 / n) ** n - 1, 3))
P("   Continuous", pct(r1.exp() - 1, 4), pct(r2.exp() - 1, 3))
P("   semiannual 15% exact value", (1 + r2 / 2) ** 2 - 1)
P("continuous - annual (bp): 1.725%, 15%", hu((r1.exp() - 1 - r1) * 10000, 1), hu((r2.exp() - 1 - r2) * 10000, 0))
dep_m = (1 + r1 / 12) ** 12 - 1
P("deposit 1.725% monthly: periodic i, EAR", pct(r1 / 12, 5), pct(dep_m, 4))
P("NT$1,000,000: 整存整付 interest / 存本取息 / diff", f"NT${hu(dep_m * 10 ** 6, 0)}", "NT$17,250", f"NT${hu((dep_m - r1) * 10 ** 6, 0)}", f"= {hu((dep_m - r1) * 10 ** 4, 2)} bp")
P("存本取息 monthly interest 31d, 30d, 28d (actual/365)", *[hu(Dec(10 ** 6) * r1 * dd / 365, 2) for dd in (31, 30, 28)])
cd = (1 + r2 / 365) ** 365 - 1
P("card: daily periodic rate i = 0.15/365", pct(r2 / 365, 6), f"萬分之 {hu(r2 / 365 * 10000, 2)}", " 1+i =", hu(1 + r2 / 365, 8))
P("card: daily-compounded EAR, NT$ on 100,000, continuous", pct(cd, 3), f"NT${hu(cd * 10 ** 5, 0)}", pct(r2.exp() - 1, 3))
P("card: saving from no-compounding rule", f"NT${hu((cd - r2) * 10 ** 5, 0)}")
P("card: daily stated rate giving a 15% EAR", pct(365 * ((Dec("1.15")).ln() / 365).exp() - 365, 3))
P("pitfall: 1.74% annual vs 1.725% monthly", pct(dep_m, 4), "1.7400%", f"{hu((Dec('0.0174') - dep_m) * 10 ** 4, 2)} bp")
P("Bernoulli (1+1/n)^n and distance to e")
for n in (1, 2, 4, 12, 52, 365, 8760, 525600):
    v = (1 + Dec(1) / n) ** n
    P(f"   n={n}", hu(v, 6), hu(Dec(1).exp() - v, 6))
P("   e", hu(Dec(1).exp(), 9))
s = Dec(0)
sums = []
for j in range(0, 7):
    s += Dec(1) / math.factorial(j)
    sums.append(hu(s, 6))
P("partial sums of sum 1/j!, j<=1..6", sums[1:])
P("widget default r=100%, n=4: EAR, limit, gap, ln(1+EAR)", pct(Dec("1.25") ** 4 - 1, 3), pct(Dec(1).exp() - 1, 3),
  pct(Dec("1.25") ** 4 - Dec(1).exp(), 2), pct((Dec("1.25") ** 4).ln(), 3))
eb = (1 + Dec("0.0585") / 12) ** 12 - 1
P("KC: EAR 5.85% monthly; cc of each", pct(eb, 4), pct(12 * (1 + Dec("0.0585") / 12).ln(), 4), pct(Dec("1.06").ln(), 4))
P("stated rates with the same EAR as R_G (0050):", *[f"r^({n})={n * ((1 + RG) ** (1 / n) - 1):.2%}" for _, n in FREQ], f"r={math.log1p(RG):.2%}")

# ================================================================ 4. HPR, annualized, cc
head("4. HOLDING-PERIOD, ANNUALIZED AND CONTINUOUSLY COMPOUNDED RETURNS")
P("conversion exhibit: HPR, R_G, ln G, g", f"+{(G - 1) * 100:.2f}%", f"{RG:.2%}", f"{lnG:.4f}", f"{g:.2%}")
P("example (3 dp, robust to 4-dp inputs)", f"R_G=10.0225^(1/11.9370)-1={10.0225 ** (1 / 11.9370) - 1:.3%}",
  f"g=2.30483/11.9370={2.30483 / 11.9370:.3%}", f"e^0.19308-1={math.expm1(0.19308):.3%}", f"ln1.21298={math.log(1.21298):.5f}")
P("example exact", f"R_G={RG:.3%}", f"g={g:.3%}")
P("trailing windows to", END, " (start = last close on or before the same calendar date; tau = days/365.25)")
WIN = [("3 months", dt.date(2026, 7, 8)), ("6 months", dt.date(2026, 4, 8)), ("1 year", dt.date(2025, 10, 8)),
       ("3 years", dt.date(2023, 10, 8)), ("5 years", dt.date(2021, 10, 8)), ("10 years", dt.date(2016, 10, 8)),
       ("Since 31 Oct 2014", BASE)]
trail = []
for lab, nominal in WIN:
    s0 = on_or_before(nominal)
    Gw = growth(s0, END)
    tw = (END - s0).days / YEAR
    row = dict(window=lab, start=str(s0), days=(END - s0).days, tau=tw, hpr=Gw - 1, ann=Gw ** (1 / tw) - 1, cc=math.log(Gw) / tw)
    trail.append(row)
    P(f"   {lab:<18s} from {s0}", f"days={row['days']}", f"tau={tw:.4f}", f"HPR={Gw - 1:.2%}", f"ann={row['ann']:.2%}", f"cc={row['cc']:.2%}")
P("pitfall: 6-month annualized / best full calendar year", f"{trail[1]['ann']:.2%}", f"ratio {trail[1]['ann'] / float(np.prod(1 + R[yrs == 2024]) - 1):.2f}",
  f"best 2015-2025 {max(float(np.prod(1 + R[yrs == y]) - 1) for y in range(2015, 2026)):.2%} (2024)")
# 90-day example
a90, b90 = dt.date(2026, 7, 9), dt.date(2026, 10, 7)
G90 = growth(a90, b90)
T90 = IDX[b90] - IDX[a90]
d90 = (b90 - a90).days
t90 = d90 / YEAR
P("90-day window", a90, "->", b90, f"d={d90}", f"T={T90} sessions", f"tau={t90:.4f}")
P("  closes and dividend", df.filter(pl.col("date") == a90)["p0050"][0], df.filter(pl.col("date") == b90)["p0050"][0],
  df.filter((pl.col("date") > a90) & (pl.col("date") <= b90) & (pl.col("d0050") > 0)).select("date", "d0050").rows())
P("  HPR, 1+HPR", f"{G90 - 1:.4%}", f"{G90:.6f}")
q90 = round(G90, 6)                                            # the text quotes 1 + HPR = 1.103302; worked steps use it
P("  calendar (1+R)^(365.25/90)-1", f"{G90 ** (1 / t90) - 1:.2%}", f"from {q90}: {q90 ** (1 / t90) - 1:.2%}", f" [with 365: {G90 ** (365 / d90) - 1:.2%}]")
P("  trading A=252: (1+R)^(252/61)-1", f"{G90 ** (252 / T90) - 1:.2%}", f"from {q90}: {q90 ** (252 / T90) - 1:.2%}")
P("  trading A=243.8: (1+R)^(243.8/61)-1", f"{G90 ** (243.8 / T90) - 1:.2%}", f"from {q90}: {q90 ** (243.8 / T90) - 1:.2%}")
P("  cc per year ln(1+R)*365.25/90", f"{math.log(G90) / t90:.2%}", f"ln({q90})={math.log(q90):.6f}", f"365.25/90={1 / t90:.4f}",
  f"product of the printed factors {round(math.log(q90), 6) * round(1 / t90, 4):.2%}")
P("  simple R*365.25/90", f"{(G90 - 1) / t90:.2%}", f"from {q90 - 1:.6f}: {(q90 - 1) / t90:.2%}")
P("  range of the five figures", f"{min(math.log(G90) / t90, (G90 - 1) / t90):.1%} to {G90 ** (252 / T90) - 1:.1%}")
# daily mean log return and the annualization factor A
lr = np.log1p(R)
A_sample = len(R) / tau
P("daily log returns: T, mean", len(R), f"{lr.mean():.6%}")
P("  x252, as EAR", f"{lr.mean() * 252:.2%}", f"{lr.mean() * 252:.5f}", f"e^x-1={math.expm1(lr.mean() * 252):.2%}")
P("  sample A = T/tau, mean x A (= g)", f"{A_sample:.1f}", f"{lr.mean() * A_sample:.2%}")
P("  gap 252 vs A (pp, 1 dp)", f"{(lr.mean() * 252 - lr.mean() * A_sample) * 100:.1f}")
OUT.update(A_sample=A_sample)


def date_set(sym):
    s = set()
    for f in glob.glob(str(HERE / "raw" / f"{sym}__*.csv")):
        s |= set(pl.read_csv(f)["date"].to_list())
    return s


d0050, d631 = date_set("0050"), date_set("00631L")
union = sorted(d0050 | d631)
cnt = {y: sum(1 for x in union if x.startswith(str(y))) for y in range(2015, 2026)}
twse_window = sum(1 for x in union if x > "2014-10-31")
P("TWSE sessions per year 2015-2025", cnt)
P("  min, max, mean", min(cnt.values()), max(cnt.values()), f"{np.mean(list(cnt.values())):.1f}")
P("  sessions after base date: TWSE, 0050 own, aligned", twse_window, sum(1 for x in d0050 if x > "2014-10-31"), len(R),
  f"TWSE per year in window {twse_window / tau:.1f}")
P("  0050 suspended sessions", sorted(d631 - d0050))
P("  00631L suspended sessions (merged in aligned series)", sorted(d0050 - d631))
P("KC: 18% over 30 months (tau=2.5)", f"{1.18 ** (1 / 2.5) - 1:.2%}", f"{math.log(1.18) / 2.5:.2%}")

# ================================================================ 5. Aggregation
head("5. ADDING RETURNS ACROSS TIME AND ASSETS")
bounds = [BASE] + [on_or_before(dt.date(y, 10, 31)) for y in (2016, 2018, 2020, 2022, 2024)] + [END]
blocks = []
for a, b in zip(bounds[:-1], bounds[1:]):
    Gb = growth(a, b)
    blocks.append(dict(start=str(a), end=str(b), days=(b - a).days, R=Gb - 1, r=math.log(Gb)))
    P(f"   {a} -> {b}", f"days={(b - a).days}", f"R={Gb - 1:.2%}", f"r={math.log(Gb):.4f}")
P("sum of printed r (4dp) vs ln G (4dp)", f"{sum(round(x['r'], 4) for x in blocks):.4f}", f"{lnG:.4f}")
P("sum of printed simple R (2dp)", f"{sum(round(x['R'] * 100, 2) for x in blocks):.2f}%", " days", sum(x["days"] for x in blocks))
P("last two blocks share of log growth", f"{(blocks[-1]['r'] + blocks[-2]['r']) / lnG:.0%}", " last/second ratios", f"{blocks[-1]['R'] / blocks[1]['R']:.1f}", f"{blocks[-1]['r'] / blocks[1]['r']:.2f}")
GL = WL[-1]
Gport = 0.5 * G + 0.5 * GL
avg_log = 0.5 * lnG + 0.5 * math.log(GL)
P("00631L G, ln G", f"{GL:.4f}", f"{math.log(GL):.4f}")
P("50/50 portfolio G, return, ln", f"{Gport:.2f}", f"+{(Gport - 1) * 100:,.0f}%", f"check 0.5*(10.02+44.54)={0.5 * (10.02 + 44.54):.2f}", f"ln27.28={math.log(27.28):.3f}")
P("average of logs, e^avg, sqrt(G*GL), understatement", f"{avg_log:.4f}", f"{math.exp(avg_log):.2f} (+{(math.exp(avg_log) - 1) * 100:,.0f}%)",
  f"{math.sqrt(G * GL):.2f}", f"{(Gport - math.exp(avg_log)) * 100:,.0f} pp")
wS, rS = (1.5, -0.5), (0.10, 0.20)
rpS = math.log(wS[0] * math.exp(rS[0]) + wS[1] * math.exp(rS[1]))
P("short counterexample w=(1.5,-0.5), r=(0.10,0.20)", f"r_p={rpS:.4f}", f"sum w r={wS[0] * rS[0] + wS[1] * rS[1]:.4f}")
Rusd, fx0, fx1 = 0.20, 32.0, 29.6
Rfx = fx1 / fx0 - 1
P("FX (hypothetical): R_fx, exact TWD", f"{Rfx:.2%}", f"{(1 + Rusd) * (1 + Rfx) - 1:.2%}")
P("FX logs", f"{math.log1p(Rusd):.5f} + ({math.log1p(Rfx):.5f}) = {math.log1p(Rusd) + math.log1p(Rfx):.5f}", f"-> {math.expm1(math.log1p(Rusd) + math.log1p(Rfx)):.2%}",
  f"naive {Rusd + Rfx:.2%}", f"cross {Rusd * Rfx:.2%}")
P("KC: simple returns of log +-0.10, portfolio", f"{math.expm1(0.1):.2%}", f"{math.expm1(-0.1):.2%}", f"{0.5 * math.expm1(0.1) + 0.5 * math.expm1(-0.1):.2%}")

# ================================================================ 6. Growth equations
head("6. SOLVING GROWTH EQUATIONS")
P("doubling table: R | exact ln2/ln(1+R) | rule of 72")
for Rr in (0.01725, 0.04, 0.08, 0.15, RG):
    P(f"   R={Rr:.3%}", f"{LN2 / math.log1p(Rr):.2f}", f"{72 / (100 * Rr):.2f}")
P("simple interest doubling at 15%; continuous ln2/g", f"{1 / 0.15:.2f}", f"{LN2 / g:.2f}")
P("0050 doublings in tau years, years per doubling", f"{lnG / LN2:.3f} in {tau:.2f}", f"{tau / (lnG / LN2):.2f}")
W0, Wtau, tauR = 3e6, 20e6, 25
req = (Wtau / W0) ** (1 / tauR) - 1
P("retire: required R_G, g (2dp); ln(20/3)", f"{req:.2%}", f"{math.log(Wtau / W0) / tauR:.2%}", f"{math.log(Wtau / W0):.4f}")
P("retire: time at 6%: 1.8971/0.05827, age", f"{math.log(Wtau / W0) / math.log(1.06):.2f}", f"{35 + math.log(Wtau / W0) / math.log(1.06):.1f}", f"ln1.06={math.log(1.06):.5f}")
P("retire: wealth at 60 if 6%", f"NT${W0 * 1.06 ** 25:,.0f}")
P("retire: nominal: 7.59%+1.98%=9.57% -> e^0.0957-1; 1.0788*1.02-1", f"{math.log(1.02):.2%}", f"{math.expm1(0.0957):.2%}", f"{1.0788 * 1.02 - 1:.2%}",
  f"exact {(1 + req) * 1.02 - 1:.2%}")
P("recovery table: DD | gain DD/(1-DD) | -ln(1-DD) | years at 8% | years at R_G")
for DDv in (Dec("0.10"), Dec("0.20"), Dec("0.25"), Dec(1) / 3, Dec("0.50"), Dec("0.75"), Dec("0.90")):
    ld = -(1 - DDv).ln()
    P(f"   DD={pct(DDv, 1)}", pct(DDv / (1 - DDv), 1), hu(ld, 4), hu(ld / Dec("1.08").ln(), 2), hu(ld / Dec(repr(g)), 2))
# drawdown episodes; DD_t = 1 - W_t / running peak (positive), the running peak includes W_0 = 1
peak = np.maximum.accumulate(W)
DD = 1 - W / peak
eps, in_dd = [], False
for k in range(1, len(W)):
    if DD[k] > 0 and not in_dd:
        in_dd, s0 = True, k - 1
    if in_dd and DD[k] <= 0:
        t = s0 + int(np.argmax(DD[s0:k]))
        eps.append((s0, t, k))
        in_dd = False
episodes = []
P("drawdown episodes with DD > 15% (calendar days; at-g days = -ln(1-DD)/g x 365.25)")
for s, t, r in eps:
    if DD[t] <= 0.15:
        continue
    D_ = DD[t]
    row = dict(peak=str(dates[s]), trough=str(dates[t]), recovered=str(dates[r]), DD=D_, gain=D_ / (1 - D_),
               pt_days=(dates[t] - dates[s]).days, tr_days=(dates[r] - dates[t]).days, tr_sessions=r - t,
               log_dist=-math.log1p(-D_), longrun_days=-math.log1p(-D_) / g * YEAR)
    episodes.append(row)
    P(f"   {dates[s]} {dates[t]} {dates[r]}", f"DD={D_:.2%}", f"gain={row['gain']:.2%}", f"pk->tr={row['pt_days']}d",
      f"tr->rec={row['tr_days']}d/{row['tr_sessions']}s", f"log={row['log_dist']:.4f}", f"at g {row['longrun_days']:.0f}d")
P("max drawdown in sample", f"{DD.max():.2%}", dates[int(np.argmax(DD))])
for x in ("2025-04-02", "2025-04-07", "2025-04-08", "2025-04-09", "2025-04-10"):
    i = IDX[dt.date.fromisoformat(x)]
    P(f"   {x}", f"R={W[i] / W[i - 1] - 1:+.2%}", f"DD={DD[i]:.2%}")
P("2025: DD at 04-02, three-session fall, total; log split",
  f"{DD[i7 - 1]:.2%}", f"{W[i9] / W[i7 - 1] - 1:.2%}", f"{DD[i9]:.2%}",
  f"{math.log1p(-DD[i7 - 1]):.4f} + {math.log(W[i9] / W[i7 - 1]):.4f} = {math.log1p(-DD[i9]):.4f}",
  f"(printed sum {round(math.log1p(-DD[i7 - 1]), 4) + round(math.log(W[i9] / W[i7 - 1]), 4):.4f})")
i5 = IDX[dt.date(2024, 8, 5)]
P("2024-08-02, 08-05 returns", f"{W[i5 - 1] / W[i5 - 2] - 1:+.2%}", f"{W[i5] / W[i5 - 1] - 1:+.2%}")
for e in episodes:
    if e["peak"][:4] in ("2022", "2024", "2025"):
        P(f"   intermediates {e['peak'][:4]}: DD/(1-DD), -ln(1-DD)", f"{e['DD']:.5f}/{1 - e['DD']:.5f} = {e['gain']:.2%}", f"{e['log_dist']:.4f}")
P("2025: at-g years 0.3214/0.1931; actual 99 days in years", f"{0.3214 / 0.1931:.2f}", f"{99 / YEAR:.2f}")
P("2025-04-10 return", f"{R[i9]:+.2%}")
P("0050 suspended sessions inside the 2025 recovery", sorted(x for x in d631 - d0050 if "2025-04-09" < x < "2025-07-17"))
i18 = IDX[dt.date(2025, 6, 18)]
P("split-day return 2025-06-18 spans", f"from {dates[i18 - 1]} close", f"{sum(1 for x in union if str(dates[i18 - 1]) < x <= '2025-06-18')} market sessions",
  f"R={R[i18 - 1]:+.3%}", f"check 47.57/(188.65/4)-1={47.57 / (188.65 / 4) - 1:+.3%}")
P("KC: DD=40%: gain, years at 15%: 0.5108/0.1398", f"{0.4 / 0.6:.2%}", f"{-math.log(0.6) / math.log(1.15):.2f}")
P("Sec 6 text: 2022 peak->trough days", [e for e in episodes if e["peak"].startswith("2022")][0]["pt_days"])

# ================================================================ Practice problems
head("PRACTICE PROBLEMS")
P("PP1 log2(25) | ln25/log10(2) | 25/2", f"{math.log(25) / LN2:.2f}", f"{math.log(25) / math.log10(2):.2f}", "12.50", f"ln25={math.log(25):.4f}")
P("PP2 EAR 12% monthly | continuous", pct((1 + Dec("0.01")) ** 12 - 1, 2), pct(Dec("0.12").exp() - 1, 2))
q4 = (1 + Dec("0.006")) ** 4 - 1
P("PP3 2.4% quarterly: EAR, r^(12), cc", pct(q4, 4), pct(12 * ((1 + q4).ln() / 12).exp() - 12, 4), pct((1 + q4).ln(), 4), f"1.006^4={hu(1 + q4, 6)}")
P("PP4 e^0.08-1 | ln1.08", pct(Dec("0.08").exp() - 1, 2), pct(Dec("1.08").ln(), 2))
P("PP6 price-only R_G, g_P, dividends (log/yr)", f"{Gp ** (1 / tau) - 1:.2%}", f"{math.log(Gp) / tau:.2%}", f"{div_log / tau:.2%}",
  f"check 1.9518/11.937={1.9518 / 11.937:.2%}", f"0.3530/11.937={0.3530 / 11.937:.2%}")
P("PP7 6% in 4 months: 1.06^3-1 | 6%x4 | 1.06^4-1", pct(Dec("1.06") ** 3 - 1, 2), "24.00%", pct(Dec("1.06") ** 4 - 1, 2))
y3x = [float(np.prod(1 + R[yrs == y]) - 1) for y in (2023, 2024, 2025)]
y3 = [round(v, 4) for v in y3x]                       # stated to 0.01% in the problem; the solution uses the stated values
G3 = float(np.prod([1 + v for v in y3]))
l3 = [math.log1p(v) for v in y3]
P("PP8 stated returns", [f"{v:.2%}" for v in y3], f"cum {G3 - 1:.2%}", f"ann {G3 ** (1 / 3) - 1:.2%}", f"G3={G3:.5f}")
P("PP8 logs 5dp, printed sum, ln G3, cc, sum simple", [f"{v:.5f}" for v in l3], f"{sum(round(v, 5) for v in l3):.5f}", f"{math.log(G3):.5f}",
  f"{math.log(G3) / 3:.2%}", f"{sum(y3):.2%}")
pp9 = 0.5 * math.exp(0.30) + 0.5 * math.exp(-0.10)
P("PP9 e^.3, e^-.1, mean, r_p | avg log | e^0.1-1 | R_p", f"{math.exp(0.3):.6f}", f"{math.exp(-0.1):.6f}", f"{pp9:.6f}", f"{math.log(pp9):.2%} ({math.log(pp9):.1%})",
  "10.0%", f"{math.expm1(0.1):.1%}", f"{pp9 - 1:.2%}")
P("PP10 1.04x1.05-1; logs; naive; cross", f"{1.04 * 1.05 - 1:.2%}", f"{math.log(1.04):.5f}+{math.log(1.05):.5f}={math.log(1.04) + math.log(1.05):.5f}", "9.00%", f"{0.04 * 0.05:.2%}")
P("PP11 ln4/ln1.06 | ln4/0.06 | difference (years, months)", f"{math.log(4):.4f}/{math.log(1.06):.5f}={math.log(4) / math.log(1.06):.2f}", f"{math.log(4) / 0.06:.2f}",
  f"{math.log(4) / math.log(1.06) - math.log(4) / 0.06:.2f}", f"{(math.log(4) / math.log(1.06) - math.log(4) / 0.06) * 12:.1f}")
P("PP12 5^(1/15)-1 | ln5/15 | 400%/15", f"{5 ** (1 / 15) - 1:.2%}", f"{math.log(5) / 15:.2%}", f"{4 / 15:.2%}")
P("PP13 0.35/0.65 | -ln0.65/ln1.10 | 0.65x1.30", f"{0.35 / 0.65:.2%}", f"{-math.log(0.65):.4f}/{math.log(1.10):.4f}={-math.log(0.65) / math.log(1.10):.2f}", f"{0.65 * 1.3:.3f}", f"{0.65 * 1.3 - 1:.2%}")
e22 = [x for x in episodes if x["peak"].startswith("2022")][0]
P("PP14 0.33929/0.66071 | -ln0.66071 | /0.19308 | days | actual/at-g", f"{0.33929 / 0.66071:.2%}", f"{-math.log(0.66071):.4f}",
  f"{-math.log(0.66071) / 0.19308:.3f}", f"{-math.log(0.66071) / 0.19308 * YEAR:.0f}", f"{e22['tr_days'] / e22['longrun_days']:.0%}")
b0, b1 = on_or_before(dt.date(2014, 12, 31)), on_or_before(dt.date(2024, 12, 31))
G10 = growth(b0, b1)
t10 = (b1 - b0).days / YEAR
m10 = np.array([(b0 < d <= b1) for d in df["date"].to_list()])
T10 = int(m10.sum())
A10 = T10 / t10
mlr = float(np.log1p(R[m10]).mean())
P("PP15 2015-2024", b0, "->", b1, f"days={(b1 - b0).days}", f"tau={t10:.4f}", f"G={G10:.4f}", f"R_G={G10 ** (1 / t10) - 1:.2%}", f"g={math.log(G10) / t10:.2%}")
P("PP15 T, A=T/tau, mean daily log; x252 (EAR); xA (EAR)", T10, f"{A10:.1f}", f"{mlr:.6%}", f"{mlr * 252:.2%} ({math.expm1(mlr * 252):.2%})",
  f"{mlr * A10:.2%} ({math.expm1(mlr * A10):.2%})", f"e^0.1433-1={math.expm1(0.1433):.2%}")
P("PP15 overstatement (log, EAR) pp", f"{(mlr * 252 - mlr * A10) * 100:.2f}", f"{(math.expm1(mlr * 252) - math.expm1(mlr * A10)) * 100:.2f}")

OUT.update({"trail": trail, "blocks": blocks, "episodes": episodes})
(HERE / "processed" / "lm01_numbers.json").write_text(json.dumps(OUT, indent=1, default=float), encoding="utf-8")
print("\nwrote processed/lm01_numbers.json")
