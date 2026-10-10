"""Generate labs/LM01_lab/LM01_lab.ipynb (Polars-first) and its offline data snapshot.

Run from the repository root:  python3 build/make_lab01.py
Then execute inside the lab folder:
  cd labs/LM01_lab && jupyter nbconvert --to notebook --execute LM01_lab.ipynb --output LM01_lab.ipynb
"""
import glob
from pathlib import Path

import nbformat as nbf
import polars as pl

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "LM01_lab"
(LAB / "data").mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- data snapshot (copies of the verified raw files)
for sym in ("0050", "00631L"):
    files = sorted(glob.glob(str(ROOT / "data" / "raw" / f"{sym}__*.csv")))
    df = pl.concat([pl.read_csv(f, schema_overrides={"close": pl.Utf8, "spread": pl.Utf8}) for f in files]).sort("date")
    assert df["date"].is_unique().all()
    df.write_csv(LAB / "data" / f"{sym}_daily_raw.csv")
(LAB / "data" / "0050_dividends.csv").write_text((ROOT / "data" / "raw" / "0050_dividends.csv").read_text(encoding="utf-8"), encoding="utf-8")

cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s.strip("\n")))
code = lambda s: cells.append(nbf.v4.new_code_cell(s.strip("\n")))

md(r"""
# LM1 Lab — Exponentials, Logarithms and Compounding

Companion notebook to **From Calculus to Kelly, LM1**. It rebuilds every exhibit and computational example in the module from verified price files, and solves the computational practice problems.

| Part | Rebuilds |
|:--|:--|
| 1 | Total-return series from raw closes, dividends and the split; the case (Exhibit 1) and the price/dividend split (Example 1) |
| 2 | Logarithms and log-scale charts (Exhibits 2–3) |
| 3 | Compounding frequency and the number $e$ (Exhibits 4–5, Examples 2–3) |
| 4 | Holding-period, annualized and continuously compounded returns (Exhibits 6–7, Examples 4–6) |
| 5 | Aggregation across time, positions and currencies (Exhibit 8, Examples 7–8) |
| 6 | Growth equations, doubling, drawdowns and recovery (Exhibits 9–12, Examples 9–10) |
| 7 | Practice-problem solutions and an extension exercise |

**Data.** `data/` holds a snapshot of FinMind `TaiwanStockPrice` closes for 0050 and 00631L (2014-10-31 → 2026-10-08) and 0050 cash dividends from `TaiwanStockDividendResult`, retrieved 2026-10-10. Every close was checked against FinMind's own `spread` column (close − previous close); the only mismatches are ex-dividend days and the two split days, which Part 1 handles explicitly.

**Environment.** `uv pip install polars pyarrow numpy matplotlib`.
""")

code(r"""
import math
from datetime import date
from pathlib import Path

import numpy as np
import polars as pl
import matplotlib.pyplot as plt

DATA = Path("data")
BASE = date(2014, 10, 31)                     # last close before the first daily return
pl.Config.set_tbl_rows(30)
pl.Config.set_float_precision(6)
plt.rcParams.update({"figure.figsize": (9, 4.5), "axes.grid": True, "grid.alpha": 0.3,
                     "axes.spines.top": False, "axes.spines.right": False})
""")

md(r"""
## Part 1 — Total-return series and the case

On an ex-dividend day $t$ the total return is $R_t=(P_t+D_t)/P_{t-1}-1$; on a split day with ratio $k$ it is $P_t/(P_{t-1}/k)-1$. 0050 split 4-for-1 on **2025-06-18**; 00631L split 22-for-1 on **2026-03-31** and paid no dividends in the sample.
""")

code(r"""
SPLITS = {"0050": ("2025-06-18", 4.0), "00631L": ("2026-03-31", 22.0)}
div = pl.read_csv(DATA / "0050_dividends.csv")

def load_raw(sym):
    df = pl.read_csv(DATA / f"{sym}_daily_raw.csv").sort("date")
    gap = (pl.col("close") - pl.col("close").shift(1) - pl.col("spread")).abs()
    bad = df.with_columns(gap.alias("gap")).filter(pl.col("gap") > 0.005)
    expected = (set(div["date"]) if sym == "0050" else set()) | {SPLITS[sym][0]}
    unexplained = sorted(set(bad["date"]) - expected)
    print(f"{sym}: {df.height} rows, checksum mismatches {bad.height}, unexplained {unexplained}")
    assert not unexplained
    return df

def total_returns(sym):
    df = load_raw(sym)
    sd, k = SPLITS[sym]
    d = (div.select("date", pl.col("cash_dividend").alias("D")) if sym == "0050"
         else pl.DataFrame({"date": [], "D": []}, schema={"date": pl.Utf8, "D": pl.Float64}))
    return (df.join(d, on="date", how="left")
              .with_columns(pl.col("D").fill_null(0.0),
                            pl.when(pl.col("date") == pl.lit(sd)).then(pl.lit(k)).otherwise(pl.lit(1.0)).alias("k"))
              .select("date", pl.col("close").alias(f"P_{sym}"), pl.col("D").alias(f"D_{sym}"), pl.col("k").alias(f"k_{sym}")))

raw0050, raw631 = total_returns("0050"), total_returns("00631L")

def add_returns(df, sym):
    R = (pl.col(f"P_{sym}") + pl.col(f"D_{sym}")) / (pl.col(f"P_{sym}").shift(1) / pl.col(f"k_{sym}")) - 1
    return df.with_columns(R.alias(f"R_{sym}"))

# (a) 0050 on its own trading days; (b) the series of the module, aligned with 00631L on common dates (as in LM3)
own = add_returns(raw0050, "0050").drop_nulls("R_0050").with_columns(pl.col("date").str.to_date())
aligned = (add_returns(add_returns(raw0050.join(raw631, on="date", how="inner").sort("date"), "0050"), "00631L")
           .drop_nulls("R_0050").with_columns(pl.col("date").str.to_date()))
R = aligned["R_0050"].to_numpy(); RL = aligned["R_00631L"].to_numpy()
dates = [BASE] + aligned["date"].to_list()
W = np.concatenate([[1.0], np.cumprod(1 + R)]); WL = np.concatenate([[1.0], np.cumprod(1 + RL)])
print(f"own series: {own.height} returns; aligned series: {aligned.height} returns")
print(f"growth factor: own {np.prod(1 + own['R_0050'].to_numpy()):.6f}  aligned {W[-1]:.6f}")
""")

code(r"""
# Exhibit 1: one growth factor, three returns
G = W[-1]; lnG = math.log(G)
days = (dates[-1] - BASE).days; T = days / 365.25
RG = G ** (1 / T) - 1; g = lnG / T
case = {"G": G, "NT$100,000 ->": 100_000 * G, "HPR": G - 1, "days": days, "T (years)": T,
        "annualized R_G": RG, "log growth ln G": lnG, "continuously compounded g": g}
for k, v in case.items():
    print(f"{k:28s} {v:,.6f}")
assert round(G, 4) == 10.0225 and round(RG, 4) == 0.2130 and round(g, 4) == 0.1931 and round(lnG, 4) == 2.3048
print(f"check: ln(1+R_G) = {math.log1p(RG):.6f} = g;  simple-interest 'annualization' (G-1)/T = {(G - 1) / T:.2%}")
""")

code(r"""
# Example 1: split the log growth into price and dividends
P0 = float(raw0050["P_0050"][0]); P1 = float(raw0050["P_0050"][-1]) * 4        # base close; last close in pre-split shares
G_price = P1 / P0
exd = aligned.filter(pl.col("D_0050") > 0)
div_log = float(np.log1p((exd["D_0050"] / exd["P_0050"]).to_numpy()).sum())
print(f"P0 = {P0}, P1 (pre-split shares) = {P1:.2f}, G_price = {G_price:.4f}, price return = {G_price - 1:.2%}")
print(f"ln G_price = {math.log(G_price):.4f} + dividends {div_log:.4f} = {math.log(G_price) + div_log:.4f}  (ln G = {lnG:.4f})")
print(f"{exd.height} dividends; share of log growth {div_log / lnG:.1%}; doublings {math.log(G_price)/math.log(2):.3f} + {div_log/math.log(2):.3f} = {lnG/math.log(2):.3f}")
assert abs(math.log(G_price) + div_log - lnG) < 1e-12
""")

md(r"""
## Part 2 — Logarithms and log-scale charts

Change of base: $\log_b x=\ln x/\ln b$ (eq. 1.3). On a log axis equal distances are equal ratios and constant growth $W_0e^{gt}$ is a straight line.
""")

code(r"""
print(f"ln G = {lnG:.4f}; doublings log2 G = {lnG / math.log(2):.3f}; tenfold increases log10 G = {lnG / math.log(10):.3f}; ln 10 = {math.log(10):.4f}")
print(f"log2(1000) = {math.log(1000) / math.log(2):.2f}")
print(f"laws: 1.05^-1 = {1.05 ** -1:.4f};  1.01725^(1/12) - 1 = {1.01725 ** (1 / 12) - 1:.4%}")
prev = BASE
for lev in (2, 4, 8):
    k = int(np.argmax(W >= lev))
    print(f"first close >= {lev}: {dates[k]}  ({(dates[k] - prev).days / 365.25:.1f} years after the previous level)")
    prev = dates[k]
for a, b in (("2015-04-27", "2015-08-24"), ("2025-01-07", "2025-04-09")):
    ia, ib = dates.index(date.fromisoformat(a)), dates.index(date.fromisoformat(b))
    print(f"{a} -> {b}: drop {W[ia] - W[ib]:.2f} units, {W[ib] / W[ia] - 1:.1%}, {math.log(W[ib] / W[ia]):.2f} log points")
""")

code(r"""
# Exhibit 3: linear and log axes, with the constant-rate path and doubling gridlines
t = np.array([(d - BASE).days / 365.25 for d in dates]); path = G ** (t / T)
fig, axes = plt.subplots(2, 1, figsize=(9, 8), sharex=True)
for ax, scale in zip(axes, ("linear", "log")):
    ax.plot(dates, W, label="0050 total return"); ax.plot(dates, path, "--", color="grey", label=f"constant {RG:.1%} a year")
    ax.set_yscale(scale); ax.set_yticks([1, 2, 4, 8]); ax.set_yticklabels(["1×", "2×", "4×", "8×"])
    ax.set_title(f"Growth of 1 unit, {scale} axis"); ax.legend(loc="upper left")
plt.tight_layout(); plt.show()
""")

md(r"""
## Part 3 — Compounding frequency and the number $e$

EAR $=(1+r^{(n)}/n)^n-1$ (eq. 1.4); continuous limit $e^r-1$ (eqs. 1.6–1.8).
""")

code(r"""
FREQ = [("Annual", 1), ("Semiannual", 2), ("Quarterly", 4), ("Monthly", 12), ("Weekly", 52), ("Daily", 365)]
ear = pl.DataFrame({"compounding": [f for f, _ in FREQ] + ["Continuous"], "n": [n for _, n in FREQ] + [None]})
ear = ear.with_columns(
    pl.when(pl.col("n").is_null()).then(None).otherwise(pl.lit(0.15) / pl.col("n")).alias("periodic at 15%"),
    pl.when(pl.col("n").is_null()).then(pl.lit(math.expm1(0.01725))).otherwise((1 + pl.lit(0.01725) / pl.col("n")) ** pl.col("n") - 1).alias("EAR at 1.725%"),
    pl.when(pl.col("n").is_null()).then(pl.lit(math.expm1(0.15))).otherwise((1 + pl.lit(0.15) / pl.col("n")) ** pl.col("n") - 1).alias("EAR at 15%"))
ear   # Exhibit 4
""")

code(r"""
# Exhibit 5: Bernoulli's sequence, and the series sum 1/k!
bern = pl.DataFrame({"n": [1, 2, 4, 12, 52, 365, 8760, 525600]}).with_columns(
    ((1 + 1 / pl.col("n").cast(pl.Float64)) ** pl.col("n")).alias("(1+1/n)^n")).with_columns(
    (pl.lit(math.e) - pl.col("(1+1/n)^n")).alias("distance to e"))
print([round(sum(1 / math.factorial(j) for j in range(k + 1)), 6) for k in range(1, 7)])
bern
""")

code(r"""
# Example 2 (deposit) and Example 3 (credit card), plus the Section 3 knowledge check
dep = (1 + 0.01725 / 12) ** 12 - 1
print(f"整存整付: periodic {0.01725 / 12:.5%}, EAR {dep:.4%}, interest NT${1e6 * dep:,.0f};  存本取息: NT${1e6 * 0.01725:,.0f}; difference NT${1e6 * (dep - 0.01725):,.0f}")
print("存本取息 monthly payments (31, 30, 28 days):", [round(1e6 * 0.01725 * d / 365, 2) for d in (31, 30, 28)])
card = (1 + 0.15 / 365) ** 365 - 1
print(f"card: daily rate {0.15 / 365:.6%}, simple NT$15,000, daily compounding {card:.3%} = NT${1e5 * card:,.0f}, continuous {math.expm1(0.15):.3%}")
print(f"stated daily-compounded rate that yields a 15% EAR: {365 * (1.15 ** (1 / 365) - 1):.3%}")
print(f"KC: EAR of 5.85% monthly {(1 + 0.0585 / 12) ** 12 - 1:.4%}; cc equivalents {12 * math.log1p(0.0585 / 12):.4%} and {math.log(1.06):.4%}")

# convergence picture: EAR vs n at r = 100% and r = 15%
ns = np.unique(np.round(np.logspace(0, 3, 60)).astype(int))
fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
for ax, r in zip(axes, (1.0, 0.15)):
    ax.semilogx(ns, (1 + r / ns) ** ns - 1, marker=".", label="(1 + r/n)^n − 1")
    ax.axhline(math.expm1(r), color="grey", ls="--", label="e^r − 1"); ax.set_title(f"r = {r:.0%}"); ax.set_xlabel("n"); ax.legend()
plt.tight_layout(); plt.show()
""")

md(r"""
## Part 4 — Holding-period, annualized and continuously compounded returns

$R_G=G^{1/T}-1$ (1.9), $g=\ln G/T=\ln(1+R_G)$ (1.10); over $h$ days or $N$ sessions, $R_G=(1+R_h)^{365/h}-1$ or $(1+R_N)^{D/N}-1$ (1.11).
""")

code(r"""
# Exhibit 6 values and Example 4 (the same growth quoted at several frequencies)
print(f"HPR {G - 1:.2%}  R_G {RG:.3%}  ln G {lnG:.4f}  g {g:.3%};  e^g - 1 = {math.expm1(g):.3%}")
for n in (1, 2, 4, 12, 52, 365):
    print(f"  stated rate compounded {n:>3}x a year with the same EAR: {n * ((1 + RG) ** (1 / n) - 1):.2%}")
print(f"  continuous: {math.log1p(RG):.2%}")
""")

code(r"""
# Exhibit 7: trailing windows (start = last close on or before the nominal date)
IDX = {d: k for k, d in enumerate(dates)}
def on_or_before(d):
    while d not in IDX:
        d = date.fromordinal(d.toordinal() - 1)
    return d
END = dates[-1]
rows = []
for label, nominal, yrs in [("3 months", date(2026, 7, 8), 0.25), ("6 months", date(2026, 4, 8), 0.5), ("1 year", date(2025, 10, 8), 1.0),
                            ("3 years", date(2023, 10, 8), 3.0), ("5 years", date(2021, 10, 8), 5.0), ("10 years", date(2016, 10, 8), 10.0),
                            ("Since 31 Oct 2014", BASE, T)]:
    s = on_or_before(nominal); Gw = W[IDX[END]] / W[IDX[s]]
    rows.append({"window": label, "from": s, "HPR": Gw - 1, "annualized": Gw ** (1 / yrs) - 1, "cont. comp.": math.log(Gw) / yrs})
pl.DataFrame(rows)
""")

code(r"""
# Example 5: a 90-day return annualized five ways
a90, b90 = date(2026, 7, 9), date(2026, 10, 7)
G90 = W[IDX[b90]] / W[IDX[a90]]; N90 = IDX[b90] - IDX[a90]; h = (b90 - a90).days
print(f"{h} days, {N90} sessions, HPR {G90 - 1:.2%}")
print(f"calendar {G90 ** (365 / h) - 1:.2%} | D=252 {G90 ** (252 / N90) - 1:.2%} | D=243.8 {G90 ** (243.8 / N90) - 1:.2%} | "
      f"cont. {math.log(G90) * 365 / h:.2%} | simple {(G90 - 1) * 365 / h:.2%}")

# Example 6: mean daily log return x 252 vs x observations per year
lr = np.log1p(R); obs = len(R) / T
print(f"{len(R)} obs, mean {lr.mean():.6%}; x252 = {lr.mean() * 252:.2%}; obs/yr = {obs:.1f}; x obs/yr = {lr.mean() * obs:.2%} (= g); "
      f"EAR via 252: {math.expm1(lr.mean() * 252):.2%}")

# TWSE sessions per year: days on which 0050 or 00631L traded
u = pl.concat([pl.read_csv(DATA / "0050_daily_raw.csv").select("date"), pl.read_csv(DATA / "00631L_daily_raw.csv").select("date")]).unique()
per_year = (u.with_columns(pl.col("date").str.slice(0, 4).cast(pl.Int32).alias("year")).filter(pl.col("year").is_between(2015, 2025))
             .group_by("year").len().sort("year"))
print(per_year["len"].to_list(), "mean", per_year["len"].mean())
""")

md(r"""
## Part 5 — Aggregation across time, positions and currencies

Across time $\ln G=\sum_t r_t$ (1.12); across positions $R_p=\sum_i w_iR_i$ (1.13) and $r_p\ge\sum_iw_ir_i$ (1.14); across factors $r^{\text{TWD}}=r^{\text{USD}}+r^{\text{FX}}$ (1.15).
""")

code(r"""
# Exhibit 8: two-year blocks
bounds = [BASE] + [on_or_before(date(y, 10, 31)) for y in (2016, 2018, 2020, 2022, 2024)] + [END]
blocks = pl.DataFrame([{"start": a, "end": b, "days": (b - a).days, "R": W[IDX[b]] / W[IDX[a]] - 1,
                        "r": math.log(W[IDX[b]] / W[IDX[a]])} for a, b in zip(bounds[:-1], bounds[1:])])
print("sum of r:", round(blocks["r"].sum(), 6), " ln G:", round(lnG, 6), " sum of printed r (4 dp):", round(blocks["r"].round(4).sum(), 4))
print("sum of printed simple returns (2 dp, %):", round((blocks["R"] * 100).round(2).sum(), 2))
blocks
""")

code(r"""
# Example 7: 50/50 buy-and-hold of 0050 and 00631L, correct vs averaged log returns
GL = WL[-1]; Gp = 0.5 * G + 0.5 * GL; avg = 0.5 * lnG + 0.5 * math.log(GL)
print(f"00631L G {GL:.4f} (ln {math.log(GL):.4f}); portfolio G {Gp:.2f} = +{Gp - 1:.0%}; ln {math.log(Gp):.3f}")
print(f"average log {avg:.4f} -> e^avg {math.exp(avg):.2f} = +{math.exp(avg) - 1:.0%} (= sqrt(G*GL) {math.sqrt(G * GL):.2f}); "
      f"understatement {(Gp - math.exp(avg)) * 100:.0f} pp")

# Example 8: a USD asset seen from Taiwan (hypothetical numbers)
Rusd, Rfx = 0.20, 29.6 / 32.0 - 1
print(f"FX {Rfx:.2%}; exact {(1 + Rusd) * (1 + Rfx) - 1:.2%}; logs {math.log1p(Rusd):.5f} + {math.log1p(Rfx):.5f} = {math.log1p(Rusd) + math.log1p(Rfx):.5f}; "
      f"naive {Rusd + Rfx:.2%}; cross term {Rusd * Rfx:.2%}")
print(f"KC: log returns +0.1/-0.1 -> simple {math.expm1(0.1):.2%}, {math.expm1(-0.1):.2%}; portfolio {0.5 * math.expm1(0.1) + 0.5 * math.expm1(-0.1):.2%}")
""")

md(r"""
## Part 6 — Growth equations, doubling, drawdowns and recovery

$T=\ln(W_T/W_0)/\ln(1+R)$, $R=(W_T/W_0)^{1/T}-1$ (1.16); recovery gain $D/(1-D)$ (1.17) and log distance $-\ln(1-D)$.
""")

code(r"""
# Exhibit 9: doubling times
pl.DataFrame({"R": [0.01725, 0.04, 0.08, 0.15, RG]}).with_columns(
    (pl.lit(math.log(2)) / pl.col("R").log1p()).alias("exact T2"), (72 / (100 * pl.col("R"))).alias("rule of 72"))
""")

code(r"""
# Example 9: retirement target
x = 20 / 3
print(f"required R {x ** (1 / 25) - 1:.2%}, g {math.log(x) / 25:.2%}; time at 6%: {math.log(x) / math.log(1.06):.2f} years; "
      f"wealth at 60: NT${3e6 * 1.06 ** 25:,.0f}")
print(f"nominal with 2% inflation: {math.expm1(math.log(x) / 25 + math.log(1.02)):.2%} = {(x ** (1 / 25)) * 1.02 - 1:.2%}")

# Exhibit 10: recovery arithmetic
D = pl.DataFrame({"D": [0.10, 0.20, 0.25, 1 / 3, 0.50, 0.75, 0.90]})
D.with_columns((pl.col("D") / (1 - pl.col("D"))).alias("gain needed"), (-(1 - pl.col("D")).log()).alias("log distance")).with_columns(
    (pl.col("log distance") / math.log(1.08)).alias("years at 8%"), (pl.col("log distance") / g).alias("years at R_G"))
""")

code(r"""
# Exhibits 11-12: drawdown curve and episodes deeper than 15%
dd = W / np.maximum.accumulate(W) - 1
episodes, in_dd = [], False
for k in range(1, len(W)):
    if dd[k] < 0 and not in_dd:
        in_dd, s0 = True, k - 1
    if in_dd and dd[k] >= 0:
        tr = s0 + int(np.argmin(dd[s0:k])); in_dd = False
        if dd[tr] <= -0.15:
            Dd = -dd[tr]
            episodes.append({"peak": dates[s0], "trough": dates[tr], "depth": -Dd, "gain needed": Dd / (1 - Dd), "recovered": dates[k],
                             "days to recover": (dates[k] - dates[tr]).days, "sessions": k - tr,
                             "days at g": round(-math.log1p(-Dd) / g * 365.25)})
ep = pl.DataFrame(episodes)
fig, ax = plt.subplots(figsize=(9, 3.6))
ax.fill_between(dates, dd, 0, alpha=0.25); ax.plot(dates, dd, lw=1)
for d0 in (date(2024, 8, 5), date(2025, 4, 9)):
    ax.plot(d0, dd[dates.index(d0)], "o"); ax.annotate(f"{dd[dates.index(d0)]:.1%}", (d0, dd[dates.index(d0)]), xytext=(-45, 0), textcoords="offset points")
ax.set_title("0050 drawdown from the running peak (Exhibit 11)"); plt.show()
ep   # Exhibit 12
""")

code(r"""
# Example 10: the 2024 and 2025 episodes
for d0 in ("2025-04-02", "2025-04-07", "2025-04-08", "2025-04-09", "2025-04-10"):
    i = IDX[date.fromisoformat(d0)]
    print(d0, f"R {W[i] / W[i - 1] - 1:+.2%}  drawdown {dd[i]:.2%}")
i7, i9 = IDX[date(2025, 4, 7)], IDX[date(2025, 4, 9)]
print(f"log split: {math.log1p(dd[i7 - 1]):.4f} + {math.log(W[i9] / W[i7 - 1]):.4f} = {math.log1p(dd[i9]):.4f};  "
      f"at g: {-math.log1p(dd[i9]) / g:.2f} years vs actual {99 / 365.25:.2f}")
missing = sorted(set(pl.read_csv(DATA / "00631L_daily_raw.csv")["date"]) - set(pl.read_csv(DATA / "0050_daily_raw.csv")["date"]))
print("sessions on which 0050 did not trade:", missing)
""")

md(r"""
## Part 7 — Practice-problem solutions (computational) and an extension
""")

code(r"""
L2 = math.log(2)
print("PP1 ", f"log2(25) = {math.log(25) / L2:.2f}")
print("PP2 ", f"{(1.01) ** 12 - 1:.2%}  (continuous {math.expm1(0.12):.2%})")
q = 1.006 ** 4 - 1
print("PP3 ", f"EAR {q:.4%}  r(12) {12 * ((1 + q) ** (1 / 12) - 1):.4%}  cc {math.log1p(q):.4%}")
print("PP4 ", f"{math.expm1(0.08):.2%}")
print("PP6 ", f"R_G {G_price ** (1 / T) - 1:.2%}  g_P {math.log(G_price) / T:.2%}  dividends {div_log / T:.2%}")
print("PP7 ", f"{1.06 ** 3 - 1:.2%}")
y = [0.2740, 0.4867, 0.3685]; G3 = np.prod([1 + v for v in y])
print("PP8 ", f"cum {G3 - 1:.2%}  ann {G3 ** (1 / 3) - 1:.2%}  logs {[round(math.log1p(v), 5) for v in y]} sum {sum(math.log1p(v) for v in y):.5f}  "
      f"cc {math.log(G3) / 3:.2%}  sum simple {sum(y):.2%}")
pp9 = 0.5 * (math.exp(0.3) + math.exp(-0.1))
print("PP9 ", f"r_p {math.log(pp9):.2%}  R_p {pp9 - 1:.2%}")
print("PP10", f"{1.04 * 1.05 - 1:.2%}  logs {math.log(1.04) + math.log(1.05):.5f}")
print("PP11", f"{math.log(4) / math.log(1.06):.2f}  {math.log(4) / 0.06:.2f}")
print("PP12", f"{5 ** (1 / 15) - 1:.2%}  (cc {math.log(5) / 15:.2%})")
print("PP13", f"{0.35 / 0.65:.2%}  {-math.log(0.65) / math.log(1.10):.2f} years  {0.65 * 1.3 - 1:.2%}")
print("PP14", f"{0.33929 / 0.66071:.2%}  {-math.log(0.66071):.4f}  {-math.log(0.66071) / 0.19308:.3f} years = {-math.log(0.66071) / 0.19308 * 365.25:.0f} days")
""")

code(r"""
# PP15: ten calendar years 2015-2024
a, b = date(2014, 12, 31), date(2024, 12, 31)
G10 = W[IDX[b]] / W[IDX[a]]
m = (pl.col("date") > pl.lit(a)) & (pl.col("date") <= pl.lit(b))
sub = aligned.filter(m)["R_0050"].log1p()
n10, mu = sub.len(), sub.mean()
print(f"G {G10:.4f}  R_G {G10 ** 0.1 - 1:.2%}  g {math.log(G10) / 10:.2%}")
print(f"{n10} sessions ({n10 / 10:.1f}/yr), mean daily log {mu:.6%}; x252 {mu * 252:.2%} (EAR {math.expm1(mu * 252):.2%}); "
      f"x{n10 / 10:.1f} {mu * n10 / 10:.2%} (EAR {math.expm1(mu * n10 / 10):.2%})")
""")

md(r"""
### Extension: drawdowns of a leveraged fund

Repeat Exhibit 12 for 00631L, the daily 2× fund (series `WL` above). For its April 2025 episode, compute the depth, the gain needed and the log distance, and compare the log distance with twice 0050's (0.3214). Why is the leveraged fund's log loss *more* than twice the index's in a crash, and what does that imply for its recovery time at a given growth rate? The variance-drag decomposition of LM3 gives the answer. A starting point:
""")

code(r"""
ddL = WL / np.maximum.accumulate(WL) - 1
k = int(np.argmin(np.where([(date(2025, 1, 1) <= d <= date(2025, 6, 30)) for d in dates], ddL, 0.0)))
print(f"00631L 2025 trough {dates[k]}: depth {ddL[k]:.2%}, gain needed {-ddL[k] / (1 + ddL[k]):.2%}, "
      f"log distance {-math.log1p(ddL[k]):.4f} vs 2 x 0050's {2 * -math.log1p(dd[IDX[date(2025, 4, 9)]]):.4f}")
""")

nb = nbf.v4.new_notebook()
nb["cells"] = cells
nb["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                  "language_info": {"name": "python"}}
out = LAB / "LM01_lab.ipynb"
nbf.write(nb, out)
print("wrote", out)
