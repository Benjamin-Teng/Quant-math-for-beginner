"""Every number quoted in LM1 (Exponentials, Logarithms and Compounding).

Run after build_series.py:  python3 data/lm01_numbers.py
Prints each quantity at the precision used in src/lm01.md, grouped by the place it appears.
Inputs: processed/etf_daily_returns.parquet (0050 and 00631L total returns on common dates, base
close 2014-10-31), raw/0050__*.csv and raw/00631L__*.csv (trading calendars), raw/0050_dividends.csv.
"""
import glob
import json
import math
import datetime as dt
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
LN2, E = math.log(2), math.e
BASE = dt.date(2014, 10, 31)                      # last close before the first daily return
OUT = {}                                           # collected for the lab's assertions


def P(label, *vals):
    print(f"{label:<44s}", *vals)


def keep(key, val):
    OUT[key] = float(val)
    return val


def head(t):
    print("\n" + "=" * 100 + "\n" + t + "\n" + "=" * 100)


# ---------------------------------------------------------------- data
df = pl.read_parquet(HERE / "processed" / "etf_daily_returns.parquet").with_columns(pl.col("date").str.to_date())
R = df["R_0050"].to_numpy()
RL = df["R_00631L"].to_numpy()
dates = [BASE] + df["date"].to_list()
W = np.concatenate([[1.0], np.cumprod(1 + R)])     # 0050 total-return index, W[0] = 1 on 2014-10-31
WL = np.concatenate([[1.0], np.cumprod(1 + RL)])   # 00631L
IDX = {d: k for k, d in enumerate(dates)}
END = dates[-1]


def on_or_before(d):
    while d not in IDX:
        d -= dt.timedelta(days=1)
    return d


def growth(a, b):
    """Total-return growth factor of 0050 from the close of a to the close of b."""
    return W[IDX[b]] / W[IDX[a]]


# ================================================================ 1. Introduction: the case
head("1. INTRODUCTION — motivating case (Exhibit 'case')")
G = keep("G", W[-1])
lnG = keep("lnG", math.log(G))
days = (END - BASE).days
T = keep("T", days / 365.25)
RG = keep("RG", G ** (1 / T) - 1)
g = keep("g", lnG / T)
P("period", BASE, "->", END, f"days={days}", f"T=days/365.25={T:.4f} ({T:.2f} years)")
P("growth factor G", f"{G:.6f} -> {G:.4f}")
P("NT$100,000 becomes", f"NT${100000 * G:,.0f}")
P("holding-period (total) return G-1", f"{G - 1:.4%} -> +{(G - 1) * 100:.2f}%")
P("annualized R_G = G^(1/T)-1", f"{RG:.4%} -> {RG:.2%} ({RG:.1%})")
P("log growth ln G", f"{lnG:.5f} -> {lnG:.4f}")
P("continuously compounded g = lnG/T", f"{g:.4%} -> {g:.2%} ({g:.1%})")
P("check ln(1+R_G) = g", f"{math.log1p(RG):.6f} vs {g:.6f}")
P("check (1+R_G)^T", f"{(1 + RG) ** T:.4f}", "check e^(gT)", f"{math.exp(g * T):.4f}")
P("ACT/365 alternative: T, R_G, g", f"T={days / 365:.4f}", f"R_G={G ** (365 / days) - 1:.2%}", f"g={lnG * 365 / days:.2%}")
P("simple annualization (G-1)/T", f"{(G - 1) / T:.2%}", f"check 1+0.7558*T={1 + (G - 1) / T * T:.4f}")
keep("simple_ann", (G - 1) / T)
P("simple annualization / R_G", f"{(G - 1) / T / RG:.2f}")

# ================================================================ 2. Exponents and logarithms
head("2. EXPONENTS AND LOGARITHMS")
p0, p1 = 65.30, 114.95 * 4                          # close 2014-10-31; close 2026-10-08 in pre-split shares (4-for-1, 2025-06-18)
Gp = keep("G_price", p1 / p0)
dv = df.filter(pl.col("d0050") > 0).select("date", "p0050", "d0050")
div_log = keep("div_log", float(np.log1p(dv["d0050"].to_numpy() / dv["p0050"].to_numpy()).sum()))
P("number of cash dividends in window", dv.height, dv["date"][0], "->", dv["date"][-1])
P("price-only: 114.95x4 / 65.30", f"P_end(pre-split)={p1:.2f}", f"G_price={Gp:.4f}", f"return={Gp - 1:.2%}")
P("ln G_price", f"{math.log(Gp):.4f}", " dividends sum ln(1+D/P)", f"{div_log:.4f}", " sum", f"{math.log(Gp) + div_log:.4f}", " lnG", f"{lnG:.4f}")
P("exact check lnG - lnGp - div", f"{lnG - math.log(Gp) - div_log:.2e}")
P("dividend share of log growth", f"{div_log / lnG:.1%}")
P("dividend reinvestment factor e^div", f"{math.exp(div_log):.4f}", f"check G_price*factor={Gp * math.exp(div_log):.4f}")
P("doublings: total, price, dividends", f"{lnG / LN2:.3f}", f"{math.log(Gp) / LN2:.3f}", f"{div_log / LN2:.3f}")
P("tenfold increases log10 G", f"{lnG / math.log(10):.3f}", " ln 10", f"{math.log(10):.4f}")
P("price-only annualized, cc", f"{Gp ** (1 / T) - 1:.2%}", f"{math.log(Gp) / T:.2%}", " dividends per year (log)", f"{div_log / T:.2%}")
for k, (lab, a, b) in enumerate([("2015", "2015-04-27", "2015-08-24"), ("2025", "2025-01-07", "2025-04-09")]):
    wa, wb = W[IDX[dt.date.fromisoformat(a)]], W[IDX[dt.date.fromisoformat(b)]]
    P(f"log-chart: {lab} drawdown {a}->{b}", f"W {wa:.2f}->{wb:.2f}", f"drop {wa - wb:.2f} units", f"{wb / wa - 1:.1%}", f"log depth {math.log(wb / wa):.2f}")
P("ratio of unit drops 2025/2015", f"{(W[IDX[dt.date(2025, 1, 7)]] - W[IDX[dt.date(2025, 4, 9)]]) / (W[IDX[dt.date(2015, 4, 27)]] - W[IDX[dt.date(2015, 8, 24)]]):.1f}")
P("doubling dates of the index (first close >= 2,4,8)")
prev = BASE
for lev in (2, 4, 8):
    k = int(np.argmax(W >= lev))
    P(f"   W >= {lev}", dates[k], f"W={W[k]:.3f}", f"years since previous level {(dates[k] - prev).days / 365.25:.1f}")
    prev = dates[k]
P("KC: log2(1000)", f"{math.log(1000) / LN2:.2f}")
P("laws examples: 1.05^2, 1.05^-1, 1.01725^(1/12)-1", f"{1.05 ** 2:.4f}", f"{1.05 ** -1:.4f}", f"{1.01725 ** (1 / 12) - 1:.4%}")

# ================================================================ 3. Compounding and e
head("3. COMPOUNDING FREQUENCY AND THE NUMBER e")
FREQ = [("Annual", 1), ("Semiannual", 2), ("Quarterly", 4), ("Monthly", 12), ("Weekly", 52), ("Daily", 365)]
P("EAR table: n | periodic 15% | EAR 1.725% | EAR 15%")
for lab, n in FREQ:
    P(f"   {lab:<10s} n={n:<4d}", f"{0.15 / n:.6%}", f"{(1 + 0.01725 / n) ** n - 1:.4%}", f"{(1 + 0.15 / n) ** n - 1:.3%}")
P("   Continuous", f"{math.expm1(0.01725):.4%}", f"{math.expm1(0.15):.3%}")
P("continuous - annual (bp): 1.725%, 15%", f"{(math.expm1(0.01725) - 0.01725) * 1e4:.1f}", f"{(math.expm1(0.15) - 0.15) * 1e4:.0f}")
P("r^2/2 check (bp): 1.725%, 15%", f"{0.01725 ** 2 / 2 * 1e4:.1f}", f"{0.15 ** 2 / 2 * 1e4:.0f}")
# deposit example
dep_m = (1 + 0.01725 / 12) ** 12 - 1
P("deposit 1.725% monthly: periodic, EAR", f"{0.01725 / 12:.5%}", f"{dep_m:.4%}")
P("NT$1,000,000: 整存整付 interest", f"NT${1e6 * dep_m:,.0f}", " 存本取息 (365 days)", f"NT${1e6 * 0.01725:,.0f}", " diff", f"NT${1e6 * (dep_m - 0.01725):,.0f}")
P("存本取息 monthly interest 31d, 30d, 28d", f"{1e6 * 0.01725 * 31 / 365:,.2f}", f"{1e6 * 0.01725 * 30 / 365:,.2f}", f"{1e6 * 0.01725 * 28 / 365:,.2f}")
P("equivalent stated rates for EAR 1.7387%: n=1, cont", f"{dep_m:.4%}", f"{math.log1p(dep_m):.4%}")
# card example
cd = (1 + 0.15 / 365) ** 365 - 1
P("card: daily periodic rate", f"{0.15 / 365:.6%}", "(萬分之", f"{0.15 / 365 * 1e4:.2f})")
P("card: simple 1y on NT$100,000", "NT$15,000", " daily compound EAR", f"{cd:.3%}", f"NT${1e5 * cd:,.0f}", " cont", f"{math.expm1(0.15):.3%}")
P("card: saving from no-compounding rule", f"NT${1e5 * (cd - 0.15):,.0f}")
P("card: stated rate with daily compounding that gives 15% EAR", f"{365 * ((1.15) ** (1 / 365) - 1):.3%}")
# Bernoulli sequence
P("Bernoulli (1+1/n)^n")
for n in (1, 2, 4, 12, 52, 365, 8760, 525600):
    P(f"   n={n}", f"{(1 + 1 / n) ** n:.6f}", f"gap to e {E - (1 + 1 / n) ** n:.6f}")
P("   e", f"{E:.9f}")
P("Taylor partial sums of sum 1/k!")
s = 0.0
for k in range(0, 9):
    s += 1 / math.factorial(k)
    P(f"   k<={k}", f"{s:.6f}")
P("bound 1+1+1/2+1/4+... = 3")
# widget default r=100%, n=4
P("widget default r=100% n=4: EAR, limit, gap, cc", f"{(1.25) ** 4 - 1:.3%}", f"{E - 1:.3%}", f"{(1.25) ** 4 - E:.2%}", f"{math.log(1.25 ** 4):.3%}")
P("  quarterly balances", [round(1.25 ** k, 4) for k in range(5)], " e^t at quarters", [round(math.exp(k / 4), 4) for k in range(5)])
P("  EARs at r=100% for n list", [f"{(1 + 1 / n) ** n - 1:.2%}" for n in (1, 2, 4, 12, 52, 365)], f"{E - 1:.2%}")
# KC: bank A 6.00% annual vs bank B 5.85% monthly
eb = (1 + 0.0585 / 12) ** 12 - 1
P("KC: EAR A 6.00% annual, B 5.85% monthly", "6.0000%", f"{eb:.4%}", " cc A, B", f"{math.log(1.06):.4%}", f"{12 * math.log1p(0.0585 / 12):.4%}")
P("pitfall: stated 1.725% monthly vs 1.74% annual", f"{dep_m:.4%}", "1.7400%")
# r^(n) family for 0050 R_G
P("stated rates equivalent to EAR = R_G (0050):")
for lab, n in FREQ:
    P(f"   r^({n})", f"{n * ((1 + RG) ** (1 / n) - 1):.2%}")
P("   r^(inf) = g", f"{math.log1p(RG):.2%}")

# ================================================================ 4. HPR, annualized, cc
head("4. HOLDING-PERIOD, ANNUALIZED AND CONTINUOUSLY COMPOUNDED RETURNS")
P("conversion exhibit: HPR, R_G, ln G, g", f"+{(G - 1) * 100:.2f}%", f"{RG:.2%}", f"{lnG:.4f}", f"{g:.2%}")
P("example three: R_G formula", f"10.0225^(1/11.937) - 1 = {G ** (1 / T) - 1:.4%}")
P("example three: g formula", f"ln(10.0225)/11.937 = {lnG / T:.4%}")
P("example three (3dp, robust to rounded inputs)", f"R_G={10.0225 ** (1 / 11.9370) - 1:.3%}", f"g={2.30483 / 11.9370:.3%}",
  f"e^0.19308-1={math.expm1(0.19308):.3%}", f"ln1.21298={math.log(1.21298):.5f}")
P("example three exact", f"R_G={RG:.3%}", f"g={g:.3%}")
# trailing windows (nominal window length in years; since-start uses days/365.25)
P("trailing windows to", END, " (start = close on or before the nominal date)")
WIN = [("3 months", dt.date(2026, 7, 8), 0.25), ("6 months", dt.date(2026, 4, 8), 0.5), ("1 year", dt.date(2025, 10, 8), 1.0),
       ("3 years", dt.date(2023, 10, 8), 3.0), ("5 years", dt.date(2021, 10, 8), 5.0), ("10 years", dt.date(2016, 10, 8), 10.0),
       ("Since 31 Oct 2014", BASE, T)]
trail = []
for lab, nominal, yrs in WIN:
    s0 = on_or_before(nominal)
    Gw = growth(s0, END)
    row = dict(window=lab, start=str(s0), years=yrs, hpr=Gw - 1, ann=Gw ** (1 / yrs) - 1, cc=math.log(Gw) / yrs)
    trail.append(row)
    P(f"   {lab:<18s} from {s0}", f"T={yrs:.3f}", f"HPR={Gw - 1:.2%}", f"ann={Gw ** (1 / yrs) - 1:.2%}", f"cc={math.log(Gw) / yrs:.2%}")
# 90-day example
a90, b90 = dt.date(2026, 7, 9), dt.date(2026, 10, 7)
G90 = growth(a90, b90)
N90 = IDX[b90] - IDX[a90]
d90 = (b90 - a90).days
keep("G90", G90)
P("90-day window", a90, "->", b90, f"days={d90}", f"sessions={N90}")
P("  closes and dividend", df.filter(pl.col("date") == a90)["p0050"][0], df.filter(pl.col("date") == b90)["p0050"][0],
  df.filter((pl.col("date") > a90) & (pl.col("date") <= b90) & (pl.col("d0050") > 0)).select("date", "d0050").rows())
P("  price-only return", f"{df.filter(pl.col('date') == b90)['p0050'][0] / df.filter(pl.col('date') == a90)['p0050'][0] - 1:.2%}")
P("  HPR", f"{G90 - 1:.2%}", f"({G90 - 1:.4%})")
P("  calendar (1+R)^(365/90)-1", f"{G90 ** (365 / d90) - 1:.2%}")
P("  trading 252: (1+R)^(252/61)-1", f"{G90 ** (252 / N90) - 1:.2%}")
P("  trading 243.8: (1+R)^(243.8/61)-1", f"{G90 ** (243.8 / N90) - 1:.2%}")
P("  cc per year ln(1+R)*365/90", f"{math.log(G90) * 365 / d90:.2%}", " ln(1+R)", f"{math.log(G90):.4f}")
P("  simple R*365/90", f"{(G90 - 1) * 365 / d90:.2%}")
# daily mean log return
lr = np.log1p(R)
obs_per_year = len(R) / T
P("daily log returns: n, mean", len(R), f"{lr.mean():.6%}", f"({lr.mean() * 1e4:.3f} bp)")
P("  x252", f"{lr.mean() * 252:.2%}", " obs per year n/T", f"{obs_per_year:.1f}", " x obs/yr", f"{lr.mean() * obs_per_year:.2%}")
P("  x243.8 (TWSE average)", f"{lr.mean() * 243.8:.2%}")
P("  gap 252 vs obs/yr (pp)", f"{(lr.mean() * 252 - lr.mean() * obs_per_year) * 100:.2f}")
P("  as EAR: e^(x252)-1, e^(g)-1", f"{math.expm1(lr.mean() * 252):.2%}", f"{math.expm1(g):.2%}")
# trading days per year (TWSE sessions = union of 0050 and 00631L dates)
def date_set(sym):
    s = set()
    for f in glob.glob(str(HERE / "raw" / f"{sym}__*.csv")):
        s |= set(pl.read_csv(f)["date"].to_list())
    return s
d0050, d631 = date_set("0050"), date_set("00631L")
union = sorted(d0050 | d631)
cnt = {y: sum(1 for x in union if x.startswith(str(y))) for y in range(2015, 2026)}
P("TWSE sessions per year 2015-2025", cnt)
P("  min, max, mean", min(cnt.values()), max(cnt.values()), f"{np.mean(list(cnt.values())):.1f}")
keep("twse_mean", np.mean(list(cnt.values())))
P("  0050 missing sessions (traded by 00631L only)", sorted(d631 - d0050))
P("  00631L missing sessions", sorted(d0050 - d631))
P("  sessions in window after base date: TWSE, 0050, common", sum(1 for x in union if x > "2014-10-31"),
  sum(1 for x in d0050 if x > "2014-10-31"), len(R))
# KC: 18% over 30 months
P("KC: 18% over 30 months: annualized, cc/yr", f"{1.18 ** (12 / 30) - 1:.2%}", f"{math.log(1.18) * 12 / 30:.2%}")
P("pitfall: 6-month 45.99% annualized", f"{trail[1]['ann']:.2%}")

# ================================================================ 5. Aggregation
head("5. ADDING RETURNS ACROSS TIME AND ASSETS")
bounds = [BASE] + [on_or_before(dt.date(y, 10, 31)) for y in (2016, 2018, 2020, 2022, 2024)] + [END]
blocks = []
for a, b in zip(bounds[:-1], bounds[1:]):
    Gb = growth(a, b)
    blocks.append(dict(start=str(a), end=str(b), days=(b - a).days, R=Gb - 1, r=math.log(Gb)))
    P(f"   {a} -> {b}", f"days={(b - a).days}", f"R={Gb - 1:.2%}", f"r={math.log(Gb):.4f}")
r4 = [round(x["r"], 4) for x in blocks]
P("sum of printed r (4dp) vs ln G (4dp)", f"{sum(r4):.4f}", f"{lnG:.4f}")
Rp = [round(x["R"] * 100, 2) for x in blocks]
P("sum of printed simple R (2dp) vs exact", f"{sum(Rp):.2f}%", f"{sum(x['R'] for x in blocks) * 100:.2f}%")
P("days sum", sum(x["days"] for x in blocks))
P("share of log growth in last block", f"{blocks[-1]['r'] / lnG:.0%}", " last two blocks", f"{(blocks[-1]['r'] + blocks[-2]['r']) / lnG:.0%}")
# portfolio example: 50/50 0050 + 00631L buy and hold over full period
GL = WL[-1]
Gport = 0.5 * G + 0.5 * GL
P("00631L G, return, lnG", f"{GL:.4f}", f"+{(GL - 1) * 100:.2f}%", f"{math.log(GL):.4f}")
P("50/50 portfolio G (2dp), return", f"{Gport:.2f}", f"+{(Gport - 1) * 100:,.0f}%", f" check 0.5*(10.02+44.54)={0.5 * (10.02 + 44.54):.2f}")
P("portfolio log return", f"{math.log(Gport):.4f}")
avg_log = 0.5 * lnG + 0.5 * math.log(GL)
P("average of log growths", f"{avg_log:.4f}", f"check 0.5*(2.3048+3.7965)={0.5 * (2.3048 + 3.7965):.5f}", " e^avg", f"{math.exp(avg_log):.2f}",
  f"-> +{(math.exp(avg_log) - 1) * 100:,.0f}%", " sqrt(G*GL)", f"{math.sqrt(G * GL):.2f}")
P("understatement (pp)", f"{(Gport - math.exp(avg_log)) * 100:,.0f}")
# FX example (hypothetical)
Rusd, fx0, fx1 = 0.20, 32.0, 29.6
Rfx = fx1 / fx0 - 1
P("FX: R_fx, TWD return exact", f"{Rfx:.2%}", f"{(1 + Rusd) * (1 + Rfx) - 1:.2%}")
P("FX: logs", f"{math.log1p(Rusd):.5f}", f"{math.log1p(Rfx):.5f}", f"sum {math.log1p(Rusd) + math.log1p(Rfx):.5f}", f"-> {math.expm1(math.log1p(Rusd) + math.log1p(Rfx)):.2%}")
P("FX: naive sum, cross term", f"{Rusd + Rfx:.2%}", f"{Rusd * Rfx:.2%}")
# KC: log returns +0.10 and -0.10, 50/50
kc = 0.5 * math.exp(0.10) + 0.5 * math.exp(-0.10) - 1
P("KC: portfolio simple, log (r=+0.1,-0.1)", f"{kc:.4%}", f"{math.log1p(kc):.4%}", " simple returns of each", f"{math.expm1(0.1):.2%}", f"{math.expm1(-0.1):.2%}")
# real return identity example (illustrative)
P("real: nominal 1.725%, inflation 1.8%: exact real, log real", f"{1.01725 / 1.018 - 1:.4%}", f"{math.log(1.01725) - math.log(1.018):.4%}")

# ================================================================ 6. Growth equations
head("6. SOLVING GROWTH EQUATIONS")
P("doubling table: R | exact ln2/ln(1+R) | rule of 72 | ln2/g with g=ln(1+R)")
for Rr in (0.01725, 0.04, 0.08, 0.15, RG):
    P(f"   R={Rr:.3%}", f"{LN2 / math.log1p(Rr):.2f}", f"{72 / (100 * Rr):.2f}", f"{LN2 / math.log1p(Rr):.2f}")
P("simple interest doubling at 15%", f"{1 / 0.15:.2f}")
P("continuous: ln2 / 0.19308", f"{LN2 / g:.2f}")
P("0050 index doublings observed (Section 2)", f"{lnG / LN2:.3f} in {T:.2f} years -> years per doubling {T / (lnG / LN2):.2f}")
# retirement example
W0, WT, TT = 3e6, 20e6, 25
req = (WT / W0) ** (1 / TT) - 1
P("retire: required R_G, g", f"{req:.3%}", f"{math.log(WT / W0) / TT:.3%}", " ln(20/3)", f"{math.log(WT / W0):.4f}")
P("retire: time at 6%", f"{math.log(WT / W0) / math.log(1.06):.2f} years", f"age {35 + math.log(WT / W0) / math.log(1.06):.1f}")
P("retire: wealth at 60 if 6%", f"NT${W0 * 1.06 ** 25:,.0f}")
nom_target = WT * 1.02 ** TT
req_nom = (nom_target / W0) ** (1 / TT) - 1
P("retire: real target, nominal target, req nominal", f"NT${nom_target:,.0f}", f"{req_nom:.2%}",
  " logs:", f"{math.log(WT / W0) / TT:.4%} + {math.log(1.02):.4%} = {math.log(WT / W0) / TT + math.log(1.02):.4%}",
  f"-> {math.expm1(math.log(WT / W0) / TT + math.log(1.02)):.2%}")
P("retire: exact (1+req)(1.02)-1", f"{(1 + req) * 1.02 - 1:.2%}")
P("retire (2dp, as printed): R, g, ln1.02, sum, e^0.0957-1, 1.0788*1.02-1", f"{req:.2%}", f"{math.log(WT / W0) / TT:.2%}", f"{math.log(1.02):.2%}",
  f"{round(math.log(WT / W0) / TT * 100, 2) + round(math.log(1.02) * 100, 2):.2f}%", f"{math.expm1(0.0957):.2%}", f"{1.0788 * 1.02 - 1:.2%}")
P("retire: 1.8971/0.05827, ln1.06", f"{1.8971 / 0.05827:.2f}", f"{math.log(1.06):.5f}")
# recovery table
P("recovery table: D | gain needed | log loss | years at 8% | years at R_G")
for D in (0.10, 0.20, 0.25, 1 / 3, 0.50, 0.75, 0.90):
    P(f"   D={D:.1%}", f"{D / (1 - D):.1%}", f"{-math.log1p(-D):.4f}", f"{-math.log1p(-D) / math.log(1.08):.2f}", f"{-math.log1p(-D) / g:.2f}")
# drawdown episodes
peak = np.maximum.accumulate(W)
dd = W / peak - 1
eps, k, n = [], 1, len(W)
in_dd = False
for k in range(1, n):
    if dd[k] < 0 and not in_dd:
        in_dd, s0 = True, k - 1
    if in_dd and dd[k] >= 0:
        t = s0 + int(np.argmin(dd[s0:k]))
        eps.append((s0, t, k))
        in_dd = False
deep = [(s, t, r) for s, t, r in eps if dd[t] <= -0.15]
P("drawdown episodes deeper than 15% (calendar days)")
episodes = []
for s, t, r in deep:
    D = -dd[t]
    longrun_days = -math.log1p(-D) / g * 365.25
    row = dict(peak=str(dates[s]), trough=str(dates[t]), recovered=str(dates[r]), depth=D, gain=D / (1 - D),
               pt_days=(dates[t] - dates[s]).days, tr_days=(dates[r] - dates[t]).days, tr_sessions=r - t,
               pt_sessions=t - s, log_depth=-math.log1p(-D), longrun_days=longrun_days)
    episodes.append(row)
    P(f"   {dates[s]} {dates[t]} {dates[r]}", f"depth={-D:.2%}", f"gain={D / (1 - D):.2%}", f"pk->tr={row['pt_days']}d/{row['pt_sessions']}s",
      f"tr->rec={row['tr_days']}d/{row['tr_sessions']}s", f"log={row['log_depth']:.4f}", f"at g: {longrun_days:.0f}d ({longrun_days / 365.25:.2f}y)")
P("max drawdown in sample", f"{dd.min():.2%}", dates[int(np.argmin(dd))])
# April 2025 example details
for x in ("2025-04-02", "2025-04-07", "2025-04-08", "2025-04-09", "2025-04-10"):
    i = IDX[dt.date.fromisoformat(x)]
    P(f"   {x}", f"R={W[i] / W[i - 1] - 1:+.2%}", f"W={W[i]:.4f}", f"DD={dd[i]:.2%}")
i7, i9 = IDX[dt.date(2025, 4, 7)], IDX[dt.date(2025, 4, 9)]
P("three sessions 04-07..04-09 cumulative", f"{W[i9] / W[i7 - 1] - 1:.2%}", " log", f"{math.log(W[i9] / W[i7 - 1]):.4f}")
P("drawdown at close of 2025-04-02 (before crash)", f"{dd[i7 - 1]:.2%}", " log", f"{math.log1p(dd[i7 - 1]):.4f}")
P("log split of the 2025 loss: before + crash = total", f"{math.log1p(dd[i7 - 1]):.4f} + {math.log(W[i9] / W[i7 - 1]):.4f} = {math.log1p(dd[i9]):.4f}",
  " printed-sum check", f"{round(math.log1p(dd[i7 - 1]), 4) + round(math.log(W[i9] / W[i7 - 1]), 4):.4f}")
P("2024 episode: gain via printed 0.2130/0.7870, log -ln(0.7870)", f"{0.2130 / 0.7870:.2%}", f"{-math.log(0.7870):.4f}")
P("2025 episode: gain via printed 0.2749/0.7251", f"{0.2749 / 0.7251:.2%}", f" exact log {-math.log1p(dd[i9]):.4f}", f" 0.3214/0.1931={0.3214 / 0.1931:.2f}",
  f" 99 days in years {99 / 365.25:.2f}")
P("rebound needed from 04-09 close: gain", f"{1 / (1 + dd[i9]) - 1:.2%}")
P("2025-04-10 return", f"{R[i9]:+.2%}")
P("0050 suspended sessions in 2025 recovery window", sorted(x for x in d631 - d0050 if "2025-04-09" < x < "2025-07-17"))
# 2024
i5 = IDX[dt.date(2024, 8, 5)]
P("2024-08-02, 08-05 returns", f"{W[i5 - 1] / W[i5 - 2] - 1:+.2%}", f"{W[i5] / W[i5 - 1] - 1:+.2%}")
# KC: -40% at 15%
P("KC: D=40%: gain, years at 15%", f"{0.4 / 0.6:.2%}", f"{-math.log(0.6) / math.log(1.15):.2f}")

# ================================================================ Practice problems
head("PRACTICE PROBLEMS")
P("PP1 log2(25)", f"{math.log(25) / LN2:.2f}", " distractors ln25", f"{math.log(25):.2f}", " 25/2", "12.5")
P("PP2 EAR 12% monthly", f"{(1 + 0.12 / 12) ** 12 - 1:.2%}", " continuous", f"{math.expm1(0.12):.2%}")
q = (1 + 0.024 / 4) ** 4 - 1
P("PP3 2.4% quarterly: EAR, r^(12), cc", f"{q:.4%}", f"{12 * ((1 + q) ** (1 / 12) - 1):.4%}", f"{math.log1p(q):.4%}", f" check 4*ln(1.006)={4 * math.log(1.006):.4%}")
P("PP4 e^0.08-1, ln 1.08", f"{math.expm1(0.08):.2%}", f"{math.log(1.08):.2%}")
P("PP6 price-only: R_G, g, dividend g", f"{Gp ** (1 / T) - 1:.2%}", f"{math.log(Gp) / T:.2%}", f"{div_log / T:.2%}", f" total g {g:.2%}")
P("PP7 6% in 4 months: annualized, simple, x4", f"{1.06 ** 3 - 1:.2%}", "18.00%", "24.00%")
yrs = np.array([d.year for d in df["date"].to_list()])
y3x = [float(np.prod(1 + R[yrs == y]) - 1) for y in (2023, 2024, 2025)]
P("PP8 0050 2023-2025 returns (data)", [f"{v:.2%}" for v in y3x])
y3 = [round(v, 4) for v in y3x]                       # the problem states them to 0.01%; the solution uses the stated values
G3 = float(np.prod([1 + v for v in y3]))
l3 = [math.log1p(v) for v in y3]
P("PP8 from stated returns: cumulative, annualized", f"{G3 - 1:.2%}", f"{G3 ** (1 / 3) - 1:.2%}", f" G3={G3:.5f}")
P("PP8 logs (5dp), sum, cc/yr", [f"{v:.5f}" for v in l3], f"sum={sum(l3):.5f}", f"printed sum={sum(round(v, 5) for v in l3):.5f}",
  f"ln G3={math.log(G3):.5f}", f"cc={math.log(G3) / 3:.2%}")
P("PP8 sum of simple returns", f"{sum(y3):.2%}")
pp9 = 0.5 * math.exp(0.30) + 0.5 * math.exp(-0.10)
P("PP9 e^0.3, e^-0.1, avg, ln", f"{math.exp(0.3):.6f}", f"{math.exp(-0.1):.6f}", f"{pp9:.6f}", f"{math.log(pp9):.2%}", " simple", f"{pp9 - 1:.2%}")
P("PP10 TWD return 4% USD, FX 30->31.5", f"{1.04 * 1.05 - 1:.2%}", " logs", f"{math.log(1.04):.5f}+{math.log(1.05):.5f}={math.log(1.04) + math.log(1.05):.5f}",
  f"-> {math.expm1(math.log(1.04) + math.log(1.05)):.2%}", " naive", "9.00%")
P("PP11 x4 at 6% EAR, 6% cc", f"{math.log(4) / math.log(1.06):.2f}", f"{math.log(4) / 0.06:.2f}")
P("PP12 5x in 15y: R_G, cc, simple", f"{5 ** (1 / 15) - 1:.2%}", f"{math.log(5) / 15:.2%}", f"{4 / 15:.2%}")
P("PP13 -35%: gain, years at 10%, after +30%", f"{0.35 / 0.65:.2%}", f"{-math.log(0.65) / math.log(1.10):.2f}", f"{0.65 * 1.3 - 1:.2%}")
e22 = [x for x in episodes if x["peak"].startswith("2022")][0]
P("PP14 2022 episode: gain, log, years at g, days", f"{e22['gain']:.2%}", f"{e22['log_depth']:.4f}", f"{e22['log_depth'] / g:.2f}", f"{e22['longrun_days']:.0f}", f"actual {e22['tr_days']}")
P("PP14 with D=0.33929: gain, -ln(1-D), /0.19308 years, days", f"{0.33929 / 0.66071:.2%}", f"{-math.log(0.66071):.4f}",
  f"{-math.log(0.66071) / 0.19308:.3f}", f"{-math.log(0.66071) / 0.19308 * 365.25:.0f}")
# PP15 (Python): ten full calendar years 2015-2024
b0, b1 = BASE, on_or_before(dt.date(2024, 12, 31))
b0 = on_or_before(dt.date(2014, 12, 31))
G10 = growth(b0, b1)
m10 = np.array([(b0 < d <= b1) for d in df["date"].to_list()])
n10 = int(m10.sum())
mlr = float(np.log1p(R[m10]).mean())
P("PP15 2015-2024:", b0, "->", b1, f"G={G10:.4f}", f"R_G={G10 ** 0.1 - 1:.2%}", f"g={math.log(G10) / 10:.2%}", f"sessions={n10}", f"per year={n10 / 10:.1f}")
P("PP15 mean daily log, x252, x n/10", f"{mlr:.6%}", f"{mlr * 252:.2%}", f"{mlr * n10 / 10:.2%}",
  " as EAR: e^(x252)-1, e^(g)-1", f"{math.expm1(mlr * 252):.2%}", f"{math.expm1(mlr * n10 / 10):.2%}")
P("PP5 proof: no numbers")

# ================================================================ small derived figures quoted in the prose
head("DERIVED FIGURES IN THE PROSE")
P("Ex1: dividend effect e^0.3530 - 1", f"{math.exp(div_log) - 1:.1%}", f"factor {math.exp(div_log):.3f}")
P("Ex2: NT$137 per NT$1,000,000 in bp", f"{1e4 * (dep_m - 0.01725):.2f} bp")
P("pitfall: 1.74% annual vs 1.725% monthly (bp)", f"{(0.0174 - dep_m) * 1e4:.2f} bp")
P("pitfall: simple annualization / R_G (1 dp)", f"{(G - 1) / T / RG:.1f}")
P("pitfall: 6-month annualized / best calendar year 2024", f"{trail[1]['ann'] / float(np.prod(1 + R[yrs == 2024]) - 1):.2f}",
  f"best year 2015-2025 {max(float(np.prod(1 + R[yrs == y]) - 1) for y in range(2015, 2026)):.2%}")
P("Sec 5: last/second block simple and log ratios", f"{blocks[-1]['R'] / blocks[1]['R']:.1f}", f"{blocks[-1]['r'] / blocks[1]['r']:.2f}")
P("Sec 6: 2022 episode peak->trough days", [e for e in episodes if e["peak"].startswith("2022")][0]["pt_days"])
P("PP11: difference in years and months", f"{math.log(4) / math.log(1.06) - math.log(4) / 0.06:.2f}", f"{(math.log(4) / math.log(1.06) - math.log(4) / 0.06) * 12:.1f}")
P("PP14: actual / steady-growth days", f"{e22['tr_days'] / e22['longrun_days']:.0%}")
P("PP15: overstatement in log terms and as EAR (pp)", f"{(mlr * 252 - mlr * n10 / 10) * 100:.2f}", f"{(math.expm1(mlr * 252) - math.expm1(mlr * n10 / 10)) * 100:.2f}")
P("KC sec 6: years to recover 40% at 15%", f"{-math.log(0.6) / math.log(1.15):.2f}")
P("intermediates: ln25, ln1000, ln1.15, -ln0.6, ln1.10, -ln0.65",
  f"{math.log(25):.4f}", f"{math.log(1000):.4f}", f"{math.log(1.15):.4f}", f"{-math.log(0.6):.4f}", f"{math.log(1.10):.4f}", f"{-math.log(0.65):.4f}")
P("intermediates: 1+0.15/365, 1+0.01725/12, 1.006^4, 20/3", f"{1 + 0.15 / 365:.8f}", f"{1 + 0.01725 / 12:.7f}", f"{1.006 ** 4:.6f}", f"{20 / 3:.4f}")
P("intermediates: 0.079422%*252, 1+HPR90, ranges 39.9-50.1", f"{lr.mean() * 252:.5f}", f"{G90:.4f}", f"{math.log(G90) * 365 / d90:.1%}", f"{G90 ** (252 / N90) - 1:.1%}")
P("intermediates: depths to 5 dp (2024, 2025, 2022) and 1-D",
  *[f"{e['depth']:.5f}/{1 - e['depth']:.5f}" for e in episodes if e["peak"][:4] in ("2024", "2025", "2022")])
P("intermediates: PP9 option labels 12.0%, PP13 0.65*1.3", f"{math.log(pp9):.1%}", f"{0.65 * 1.30:.3f}", " PP3 quarterly stated", "2.4000%")
P("intermediates: 0.0411% (daily 15%), 0.2885% (weekly 15%)", f"{0.15 / 365:.4%}", f"{0.15 / 52:.4%}")

# ---------------------------------------------------------------- save for the lab
OUT.update({"trail": trail, "blocks": blocks, "episodes": episodes})
(HERE / "processed" / "lm01_numbers.json").write_text(json.dumps(OUT, indent=1, default=float), encoding="utf-8")
print("\nwrote processed/lm01_numbers.json")
