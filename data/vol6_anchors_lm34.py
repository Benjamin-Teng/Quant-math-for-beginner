"""LM34 anchors (Backtesting Without Fooling Yourself): every number the Stage 1 brief quotes (2026-10-24).

Reads only data/processed/*.parquet through the shared builders, plus the raw files named here (run the builders first):
  * E5 (the through case): data/vol5_series.py's frames("E5") and ohlc(fund) (data/processed/vol5_frames.parquet,
    vol5_ohlc.parquet), and data/vol5_rules.py's signals(), schedule(), wealth_path() and summary(), which every
    Volume V-VI script imports; no rule is re-implemented here. 0050's distributions and the split table are read from
    their registered raw files (data/raw/vol5/0050_dividends.csv, data/raw/vol5/splits__2016-12-01__2026-10-08.csv),
    read-only: vol5_series's own readers delete its outputs on a failed check, so they are not called.
  * TR23 (Volume III): data/processed/vol3_taiex.parquet (columns date, tr, price, R, Rp; R the total-return index's
    simple daily return), for LM21's Experiment 10 (recomputed with LM21's seed) and the TR23 problems.
  * LM34's survivorship data, PENDING REGISTRATION under data/raw/vol6/ (the brief's "Open before Stage 2" lists the
    exact --add commands): TaiwanStockDelisting (ids from "00"), TaiwanStockPrice snapshots of every ETF on 2017-01-17
    and 2026-10-08, and the daily prices of the cohort funds from 2016-12-01. The anchors that need them print a
    "PENDING REGISTRATION" note when the files are absent; their IDs stay fixed (A34-18 to A34-21). A34-18 alone reads
    the two snapshots (TaiwanStockPrice without a data_id, served only above FinMind's Free tier); A34-19 to A34-21
    need only Free files. The environment variable LM34_VOL6 may point at unregistered copies of these files, for a
    test run only.

Conventions (plans/vol-5.md, shared decisions). The through case's settings are vol5_rules.py's (window WINDOW = 504
estimation rows, month-end signals, trade at the next session's close on which every fund trades, costs COMMISSION and
TAX, cash at RF = 1.5% a year, borrowing at RF + SPREAD, valuation to 2026-10-08 with no terminal liquidation).
"Growth" is ln(final wealth) / years from the cash of 1 at the first trade's close (years = calendar days / 365.25);
"gross" is the same path with cost_mult = 0 (trading costs removed, financing kept); "costs" are the sum over trades of
cost / pre-trade wealth; "turnover" is the sum of one-way turnovers after the first purchase per year (summary()).
A rule's Sharpe ratio, volatility, VaR and drawdown are other modules' statistics (LM33, LM30-LM31, LM32) and are not
printed. The PBO grid (declared before it was computed; the brief's "PBO grid") reuses signals() with
vol5_rules.WINDOW set to 126, 252 or 504 for the call and restored after it, and keeps the through case's schedule from
its first signal; a k-month configuration trades at signals 1, 1 + k, 1 + 2k, ... TR23's statistics use r_f = 0
(Volume IV), except one sensitivity of the Kelly walk-forward that charges BORROW on the exposure above 1.
Quantiles: inverted_cdf. Counts against a threshold use the guard EPS = 1e-12.
Simulation (AUTHORING section 8): one generator per experiment, np.random.default_rng([e, 20261011]):
  e = 1  the reality check on Experiment 10 (stationary bootstrap, mean block length 145, LM22's TR23 length, drawn by
         LM22's stationary_idx, lm22.md:371-379; B_RC resamples in batches of 1,000);
  e = 2  noise strategies under CSCV (Model): N_NOISE panels of 60 iid normal strategies on the grid's evaluation days;
  e = 3  the widget's grid (Model): N_STATE panels per state, states in the order printed;
  e = 4  the reality check on the PBO grid against R1 monthly (stationary bootstrap, mean block length by LM22's rule,
         lm22.md:254: the largest Politis-White estimate among the configurations' squared demeaned returns, rounded);
  e = 5  the same at R1 monthly's own Politis-White length, rounded (a block-length sensitivity, LM22's advice).
LM21's Experiment 10 keeps LM21's generator default_rng([10, 20261011]). A Monte Carlo proportion's standard error is
sqrt(p (1 - p) / B).

Rounding flags. Every number the brief prints passes through f(x, k1, k2, ...), which shows x with max(k) + 3 decimals
and flags it "NEAR" for each printed precision k at which x lies within a tenth of a last-digit unit of a rounding
boundary (|frac(10^k |x|) - 0.5| < 0.1). The brief prints a flagged value as rounded from the unrounded value here.

Prints one line per anchor, "A34-NN <value>", in ID order, and writes nothing.

Run:  PYTHONUTF8=1 uv run python data/vol6_anchors_lm34.py
"""
import csv
import os
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from itertools import combinations
from math import comb, floor, log, sqrt
from pathlib import Path

import cvxpy as cp
import numpy as np
import polars as pl
import vol5_rules as V
from arch.bootstrap import optimal_block_length
from numpy.typing import NDArray
from scipy import stats
from scipy.optimize import brentq
from vol5_series import Frames, frames, ohlc

HERE = Path(__file__).resolve().parent
PROC = HERE / "processed"
RAW5 = HERE / "raw" / "vol5"
RAW6 = Path(os.environ.get("LM34_VOL6", HERE / "raw" / "vol6"))   # override only to test unregistered copies
EPS = 1e-12
SEED = 20261011
B_RC = 10_000          # reality-check resamples (experiments 1 and 4)
N_NOISE = 200          # noise panels (experiment 2)
N_STATE = 40           # panels per widget state (experiment 3)
BLOCKS = 16            # CSCV blocks
ELL_TR23 = 145         # LM22's mean block length for TR23 (lm22.md:427)
BORROW = V.RF + V.SPREAD   # 3.5% a year, the through case's illustrative borrowing rate, for the Kelly lab's sensitivity
BASE, END = "2017-01-17", "2026-10-08"
FUTURES6 = ["00635U", "00642U", "00672L", "00673R", "00674R", "00677U"]
COHORT33 = ["00631L", "00632R", "00633L", "00634R", "00635U", "00637L", "00638R", "00640L", "00641R", "00642U",
            "00647L", "00648R", "00650L", "00651R", "00653L", "00654R", "00655L", "00656R", "00658L", "00659R",
            "00663L", "00664R", "00665L", "00666R", "00669R", "00672L", "00673R", "00674R", "00675L", "00676R",
            "00677U", "00680L", "00681R"]
E5_FILES = ("00635U", "00642U")    # cohort funds already in E5 (read through ohlc)
Vec = NDArray[np.float64]
Mat = NDArray[np.float64]

OUT: list[str] = []
NEAR: list[str] = []


def flagged(value: str) -> str:
    """value with the NEAR flags that f() has collected since the last call, which it clears."""
    tail = f" [NEAR a rounding boundary: {'; '.join(NEAR)}]" if NEAR else ""
    NEAR.clear()
    return value + tail


def put(value: str) -> None:
    """One anchor line; values that f() found near a rounding boundary are listed at its end."""
    OUT.append(f"A34-{len(OUT) + 1:02d} {flagged(value)}")


def f(x: float, *ks: int, plus: bool = False) -> str:
    """x with max(ks) + 3 decimals; flagged for each printed precision k within 0.1 of a last-digit unit of a boundary."""
    x = float(x)
    for k in ks:
        u = abs(x) * 10**k
        if abs(u - floor(u) - 0.5) < 0.1:
            NEAR.append(f"{x:.{k + 3}f} at {k} dp")
    return f"{x:{'+' if plus else ''}.{max(ks) + 3}f}"


def years(d0: str, d1: str) -> float:
    return (date.fromisoformat(d1) - date.fromisoformat(d0)).days / 365.25


def rng(e: int) -> np.random.Generator:
    return np.random.default_rng([e, SEED])


def stationary_idx(g: np.random.Generator, T: int, ell: float) -> NDArray[np.int64]:
    """LM22's stationary bootstrap indices (lm22.md:371-379), drawn in arch's order."""
    start = g.integers(T, size=T)
    new = g.random(T) <= 1 / ell
    new[0] = True
    first = np.flatnonzero(new)
    blk = np.cumsum(new) - 1
    step = np.arange(T) - first[blk]
    return (start[first][blk] + step) % T


def num(m: dict[str, float | str], key: str) -> float:
    v = m[key]
    assert isinstance(v, float)
    return v


def read_rows(p: Path) -> list[dict[str, str]]:
    with p.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


SPLITS = [(r["stock_id"], r["date"], Decimal(r["before_price"]), Decimal(r["after_price"]))
          for r in read_rows(RAW5 / "splits__2016-12-01__2026-10-08.csv")]


def split_factor(sym: str) -> dict[str, float]:
    """Date -> s, new units per old unit (k for a k-for-1 split, 1/k for a k-to-1 reverse split), from SPLITS."""
    out = {}
    for s, d, b, a in SPLITS:
        if s == sym:
            q = b / a if b >= a else a / b
            k = int(q.to_integral_value())
            assert k >= 2 and abs(q - k) < Decimal("0.01"), (sym, d, q)
            out[d] = float(k) if b >= a else 1 / k
    return out


# ================================================================ the through case (LM34 owns its net results)
@dataclass
class Case:
    fr: Frames
    sigs: list[V.Signal]
    paths: dict[str, V.WealthPath]
    ev_years: float


def through_case() -> Case:
    fr = frames("E5")
    sigs = V.signals(fr, [])
    rules = V.RULES
    put(f"E5: estimation frame T = {len(fr.est_dates)} ({fr.est_dates[0]} .. {fr.est_dates[-1]}), A = {f(fr.A, 2)}; "
        f"wealth frame {len(fr.wealth_dates)} sessions, A_w = {f(fr.A_wealth, 2)}; years {f(fr.years, 4)} "
        "(echo of vol5_series)")                                                                          # 01
    first_w = V.schedule(fr)[0]
    ev_years = years(sigs[0].trade, fr.wealth_dates[-1])
    paths = {k: V.wealth_path(fr, sigs, k) for k in rules}
    n_days = len(paths["R1"].wealth) - 1
    put(f"signals {len(sigs)}: first {sigs[0].signal} (trade {sigs[0].trade}; window rows "
        f"{fr.est_dates[first_w[2] - V.WINDOW]} .. {fr.est_dates[first_w[2] - 1]}), last {sigs[-1].signal} (trade "
        f"{sigs[-1].trade}); valuation to {fr.wealth_dates[-1]}; {n_days} daily returns after the first trade "
        f"({paths['R1'].dates[1]} .. {paths['R1'].dates[-1]}); evaluation years {f(ev_years, 2, 4)}")      # 02
    gross = {k: V.wealth_path(fr, sigs, k, cost_mult=0.0) for k in rules}
    summ = {k: V.summary(fr, paths[k]) for k in rules}
    gsum = {k: V.summary(fr, gross[k]) for k in rules}
    for k in rules:
        assert "ruin" not in summ[k] and "ruin" not in gsum[k]
    put("net final wealth: " + ", ".join(f"{k} {f(paths[k].wealth[-1], 2, 3)}" for k in rules))           # 03
    put("net growth a year: " + ", ".join(f"{k} {f(num(summ[k], 'growth'), 3, 4)}" for k in rules))        # 04
    put("gross growth a year (trading costs 0, financing kept): "
        + ", ".join(f"{k} {f(num(gsum[k], 'growth'), 3, 4)}" for k in rules)
        + "; gross minus net: "
        + ", ".join(f"{k} {f(num(gsum[k], 'growth') - num(summ[k], 'growth'), 4, 5)}" for k in rules))     # 05
    put("turnover a year (one-way, after the first purchase): "
        + ", ".join(f"{k} {f(num(summ[k], 'turnover'), 2, 3)}" for k in rules)
        + f"; trades {len(paths['R1'].trades)} each")                                                      # 06
    put("costs (sum of cost / pre-trade wealth): " + ", ".join(f"{k} {f(num(summ[k], 'costs'), 4, 5)}" for k in rules)
        + "; per year: " + ", ".join(f"{k} {f(num(summ[k], 'costs') / ev_years, 4, 5)}" for k in rules)
        + "; ln(gross / net final wealth): "
        + ", ".join(f"{k} {f(log(gross[k].wealth[-1] / paths[k].wealth[-1]), 4, 5)}" for k in rules)
        + "; the identity -sum ln(1 - cost / pre-trade wealth) against it, largest difference over the rules "
        + f"{max(abs(log(gross[k].wealth[-1] / paths[k].wealth[-1]) + sum(log(1 - t.cost) for t in paths[k].trades))
                 for k in rules):.1e}")                                                                     # 07
    rank_net = sorted(rules, key=lambda k: -num(summ[k], "growth"))
    rank_gross = sorted(rules, key=lambda k: -num(gsum[k], "growth"))
    put(f"ranked by net growth: {' > '.join(rank_net)}; by gross growth: {' > '.join(rank_gross)}")        # 08
    saved = dict(V.TAX)
    try:
        V.TAX.update({s: 0.0 for s in V.TAX})
        comm = {k: num(V.summary(fr, V.wealth_path(fr, sigs, k)), "costs") for k in rules}
    finally:
        V.TAX.clear()
        V.TAX.update(saved)
    put("costs with the tax set to 0 (commission only): " + ", ".join(f"{k} {f(comm[k], 4, 5)}" for k in rules)
        + "; tax share of the costs: "
        + ", ".join(f"{k} {f(1 - comm[k] / num(summ[k], 'costs'), 2, 3)}" for k in rules))                # 09
    twice = {k: V.summary(fr, V.wealth_path(fr, sigs, k, cost_mult=2.0)) for k in rules}
    put("growth at twice the costs: " + ", ".join(f"{k} {f(num(twice[k], 'growth'), 3, 4)}" for k in rules)
        + "; change: "
        + ", ".join(f"{k} {f(num(twice[k], 'growth') - num(summ[k], 'growth'), 4, 5)}" for k in rules)
        + f"; ranked: {' > '.join(sorted(rules, key=lambda k: -num(twice[k], 'growth')))}")                # 10
    r8 = [num(V.summary(fr, V.wealth_path(fr, sigs, "R8", spread=s)), "growth") for s in (0.0, V.SPREAD, 0.05)]
    ex = [t.exposure for t in paths["R8"].trades]
    put("R8 growth at borrowing spreads 0, 2, 5 points: " + ", ".join(f(v, 3, 4) for v in r8)
        + f"; R8 exposure at the trades (echo of LM31, A31-29): mean {f(float(np.mean(ex)), 2, 3)}, min "
        f"{f(min(ex), 2, 3)}, max "
        f"{f(max(ex), 2, 3)}, above 1 at {sum(v > 1 + EPS for v in ex)} of {len(ex)} trades")             # 11
    t0 = paths["R1"].trades[0]
    to1 = [t.turnover for t in paths["R1"].trades[1:]]
    co1 = [t.cost for t in paths["R1"].trades[1:]]
    put(f"first purchase (every rule, from cash; echo of LM27, A27-23): turnover {f(t0.turnover, 2)}, cost / wealth "
        f"{f(t0.cost, 6)} "
        f"(0.001425 / 1.001425 = {f(V.COMMISSION / (1 + V.COMMISSION), 6)}); R1's later rebalances: mean one-way "
        f"turnover {f(float(np.mean(to1)), 4)} (largest {f(max(to1), 4)}, LM27's A27-24), mean cost / wealth "
        f"{f(float(np.mean(co1)), 6)}")                                                                     # 12
    v = 1_000_000
    buy, tax_eq, tax_bd = v * V.COMMISSION, v * V.TAX["0050"], v * V.TAX["00679B"]
    put(f"NT$1,000,000 bought and later sold at the same price: commission {buy:.0f} on each side, tax {tax_eq:.0f} "
        f"(equity and futures ETFs) or {tax_bd:.0f} (00679B); round trip {2 * buy + tax_eq:.0f} = "
        f"{f((2 * buy + tax_eq) / v, 4)} or {2 * buy + tax_bd:.0f} = {f((2 * buy + tax_bd) / v, 4)} of the value; one "
        f"side's commission plus the tax (problem 1's distractor) {buy + tax_eq:.0f}")                     # 13
    return Case(fr, sigs, paths, ev_years)


# ================================================================ look-ahead 1: adjusted prices rebuilt backward
def adjusted_prices() -> None:
    px = ohlc("0050")
    d50 = [str(d) for d in px["date"].to_list()]
    c50 = np.asarray(px["close"].to_numpy(), dtype=np.float64)
    div50 = {r["date"]: float(r["cash_dividend"]) for r in read_rows(RAW5 / "0050_dividends.csv")}
    sp50 = split_factor("0050")
    assert list(sp50) == ["2025-06-18"]
    tr50 = np.ones(len(c50))
    for i in range(1, len(c50)):
        tr50[i] = (c50[i] + div50.get(d50[i], 0.0)) / (c50[i - 1] / sp50.get(d50[i], 1.0))
    cum = np.cumprod(tr50)

    def adj(at: str, built: str) -> float:
        """0050's adjusted close for `at` in a series built on `built`: that day's close / total-return growth since."""
        i, j = d50.index(at), d50.index(built)
        return float(c50[j] / (cum[j] / cum[i]))

    i17 = d50.index(BASE)
    put(f"0050 close {BASE} {c50[i17]:.2f}; adjusted close of that day in a series built on 2020-01-02 "
        f"{f(adj(BASE, '2020-01-02'), 2)}, on 2024-12-31 {f(adj(BASE, '2024-12-31'), 2)}, on {END} "
        f"{f(adj(BASE, END), 2)}; close {END} {c50[-1]:.2f}; distributions after {BASE}: "
        f"{sum(1 for d in div50 if BASE < d <= END)}, split 2025-06-18 (4 for 1); growth factor {BASE} -> {END} "
        f"{f(float(cum[-1] / cum[i17]), 4)}")                                                               # 14
    ex17 = sorted(d for d in div50 if d.startswith("2017"))
    y_act = [div50[d] / c50[d50.index(d) - 1] for d in ex17]
    y_adj = [div50[d] / adj(d50[d50.index(d) - 1], END) for d in ex17]
    end17 = max(d for d in d50 if d.startswith("2017"))
    ttm_act = sum(div50[d] for d in ex17) / c50[d50.index(end17)]
    ttm_adj = sum(div50[d] for d in ex17) / adj(end17, END)
    put(f"0050's 2017 distributions: {', '.join(f'{d} NT${div50[d]:.2f}' for d in ex17)}; yield on the previous "
        "close " + ", ".join(f(y, 3, 4) for y in y_act) + f"; on the adjusted close of a series built on {END} "
        + ", ".join(f(y, 3, 4) for y in y_adj) + f"; distributions of 2017 over the close of {end17}: "
        f"{f(ttm_act, 3, 4)} actual, {f(ttm_adj, 3, 4)} adjusted")                                         # 15


# ================================================================ TR23: two look-ahead problems
def tr23() -> tuple[Vec, list[str]]:
    tr = pl.read_parquet(PROC / "vol3_taiex.parquet").sort("date").drop_nulls("R")
    R = np.asarray(tr["R"].to_numpy(), dtype=np.float64)
    TD = [d.isoformat() for d in tr["date"].to_list()]
    assert len(R) == 5849 and TD[0] == "2003-01-03" and TD[-1] == END
    return R, TD


def vol_scale(R: Vec, TD: list[str]) -> None:
    """A daily volatility scale min(1.5, sigma_bar / sigma_EWMA) set at the previous close or at the same close."""
    T, W = len(R), 504
    cs = np.concatenate([[0.0], np.cumsum(R**2)])
    sbar2 = np.full(T, np.nan)
    for t in range(W - 1, T):
        sbar2[t] = (cs[t + 1] - cs[t + 1 - W]) / W
    ew = np.full(T, np.nan)                       # ew[t] = sigma^2_{t+1|t}: (26.2) on R up to t
    ew[W - 1] = sbar2[W - 1]
    for t in range(W, T):
        ew[t] = 0.94 * ew[t - 1] + 0.06 * R[t] ** 2
    scale = np.minimum(1.5, np.sqrt(sbar2 / ew))  # known at the close of t
    honest = np.full(T, np.nan)
    honest[W:] = scale[W - 1:-1]                  # day t uses the scale set at the close of t - 1
    peek = np.full(T, np.nan)
    peek[W:] = scale[W:]                          # day t uses the scale that already knows R_t
    ok = ~np.isnan(honest)
    yrs = years(TD[W - 1], TD[-1])
    A = int(ok.sum()) / yrs

    def run(lv: Vec) -> tuple[float, float, float]:
        x = lv[ok] * R[ok]
        assert (1 + x).min() > 0
        return float(np.log1p(x).sum() / yrs), float(x.std() * sqrt(A)), float(x.min())

    i7 = TD.index("2025-04-07")
    gh, vh, mh = run(honest)
    gp, vp, mp = run(peek)
    put(f"TR23 volatility scale, 504-day uncentred window, (26.2) with lambda 0.94, cap 1.5, cash and borrowing at 0: "
        f"{int(ok.sum())} days {TD[W]} .. {TD[-1]} ({f(yrs, 2)} years, A {f(A, 2)}); set at the previous close: growth "
        f"{f(gh, 3, 4)}, volatility {f(vh, 3, 4)}, worst day {f(mh, 4)}; using the same day's close: growth "
        f"{f(gp, 3, 4)}, volatility {f(vp, 3, 4)}, worst day {f(mp, 4)}; 2025-04-07 (R {f(R[i7], 4)}): scale "
        f"{f(honest[i7], 3)} against {f(peek[i7], 3)}, the scaled return {f(honest[i7] * R[i7], 4)} against "
        f"{f(peek[i7] * R[i7], 4)}; TR23 itself on these days: growth "
        f"{f(float(np.log1p(R[ok]).sum() / yrs), 3, 4)}, volatility {f(float(R[ok].std() * sqrt(A)), 3, 4)}")  # 16


def kelly_root(x: Vec) -> float:
    lo, hi = -1 / x.max() * (1 - 1e-12), 1 / abs(x.min()) * (1 - 1e-12)
    return float(brentq(lambda v: float(np.mean(x / (1 + v * x))), lo, hi, xtol=1e-12))


def kelly_walk(R: Vec, TD: list[str]) -> None:
    """LM4's lab exercise on TR23: the root of (4.5) on the trailing 729 returns, capped to [0, 3], held a month."""
    T, W = len(R), 729
    ends = [i for i in range(T - 1) if TD[i][:7] != TD[i + 1][:7] and i >= W - 1]
    lev = np.full(T, np.nan)
    fs = []
    for k, e in enumerate(ends):
        v = min(max(kelly_root(R[e - W + 1:e + 1]), 0.0), 3.0)
        fs.append(v)
        nxt = ends[k + 1] if k + 1 < len(ends) else T - 1
        lev[e + 1:nxt + 1] = v
    mk = ~np.isnan(lev)
    yk = years(TD[ends[0]], TD[-1])
    full = kelly_root(R)

    def grow(x: Vec) -> float:
        assert (1 + x).min() > 0
        return float(np.log1p(x).sum() / yk)

    ak = int(mk.sum()) / yk

    def fin(lv: Vec) -> Vec:
        """lv R minus interest on the borrowed part, BORROW / A_k a session on max(lv - 1, 0)."""
        return lv * R[mk] - np.maximum(lv - 1, 0.0) * BORROW / ak

    put(f"Kelly walk-forward on TR23: {len(ends)} month-ends {TD[ends[0]]} .. {TD[ends[-1]]}, window {W} returns, "
        f"root of (4.5) capped to [0, 3]; {int(mk.sum())} days ({f(yk, 2)} years); leverage mean "
        f"{f(float(np.mean(fs)), 2)}, at the cap {sum(v >= 3 - EPS for v in fs)} months, at 0 "
        f"{sum(v <= EPS for v in fs)}; growth {f(grow(lev[mk] * R[mk]), 3, 4)}; f = 1: {f(grow(R[mk]), 3, 4)}; the "
        f"full-sample root {f(full, 2, 3)} held: {f(grow(full * R[mk]), 3, 4)}; half of it: "
        f"{f(grow(full / 2 * R[mk]), 3, 4)}; with borrowing at {BORROW:.3f} a year on the exposure above 1 "
        f"(accrued over A_k = {f(ak, 2)} sessions a year; cash at 0): walk-forward {f(grow(fin(lev[mk])), 3, 4)}, "
        f"full-sample root {f(grow(fin(np.full(int(mk.sum()), full))), 3, 4)}")                          # 17


# ================================================================ survivorship (PENDING REGISTRATION: data/raw/vol6/)
def growth_to_end(sym: str, raw6: Path) -> tuple[float, str]:
    """Growth factor from BASE's close to the last traded close on or before END. Untraded rows (close 0) are
    skipped and splits come from the registered table. Checked: every other traded close equals the previous traded
    close plus the spread (FinMind prints 0.0 after an untraded day), and a split's before_price equals the previous
    traded close. None of these funds pays distributions (no ex-date mismatch in their records)."""
    if sym in E5_FILES:
        o = ohlc(sym)
        rows = [{"date": str(d), "close": repr(float(c)), "spread": "0"} for d, c in
                zip(o["date"].to_list(), o["close"].to_list(), strict=True)]
    else:
        rows = read_rows(raw6 / f"{sym}__2016-12-01__2026-10-08.csv")
    sp = split_factor(sym)
    before = {d: b for s, d, b, _ in SPLITS if s == sym}
    rows = [r for r in rows if Decimal(r["close"]) != 0 and BASE <= r["date"] <= END]
    assert rows[0]["date"] == BASE, (sym, rows[0]["date"])
    g, prev = 1.0, Decimal(rows[0]["close"])
    for r in rows[1:]:
        c = Decimal(r["close"])
        if r["date"] in sp:
            assert before[r["date"]] == prev, (sym, r["date"])
            g *= float(c) / (float(prev) / sp[r["date"]])
        else:
            spread = Decimal(r["spread"])
            assert spread == 0 or c - prev == spread, (sym, r["date"])
            g *= float(c / prev)
        prev = c
    return g, rows[-1]["date"]


def survivorship_files(raw6: Path) -> list[Path]:
    """Free datasets (TaiwanStockDelisting; TaiwanStockPrice with a data_id): needed by A34-19 to A34-21."""
    return [raw6 / "delisting__2000-01-01__2026-10-08.csv"] + [raw6 / f"{s}__2016-12-01__2026-10-08.csv"
                                                               for s in FUTURES6 if s not in E5_FILES]


def snapshot_files(raw6: Path) -> list[Path]:
    """TaiwanStockPrice without a data_id (all securities on one date; FinMind serves it only above the Free tier):
    needed by A34-18 alone."""
    return [raw6 / f"etf_snapshot__{BASE}.csv", raw6 / f"etf_snapshot__{END}.csv"]


def pending(raw6: Path, files: list[Path], what: str) -> str:
    miss = [q.name for q in files if not q.exists()]
    more = f" and {len(miss) - 3} more" if len(miss) > 3 else ""
    return f"PENDING REGISTRATION ({what}): {raw6} lacks {', '.join(miss[:3])}{more}; skipped"


def survivorship(raw6: Path) -> list[str]:
    """The four survivorship anchors (A34-18 to A34-21) from the vol6 files in raw6, each with its own NEAR flags.
    A34-18 needs the two ETF snapshots; A34-19 to A34-21 need only Free files."""
    if not all(q.exists() for q in survivorship_files(raw6)):
        return [pending(raw6, survivorship_files(raw6), "Free files")] * 4
    lines: list[str] = []
    dl = read_rows(raw6 / "delisting__2000-01-01__2026-10-08.csv")
    dld = {r["stock_id"]: r["date"] for r in dl}
    if not all(q.exists() for q in snapshot_files(raw6)):
        lines.append(pending(raw6, snapshot_files(raw6), "the two ETF snapshots, above FinMind's Free tier"))
    else:
        s0 = read_rows(raw6 / f"etf_snapshot__{BASE}.csv")
        s1 = {r["stock_id"] for r in read_rows(raw6 / f"etf_snapshot__{END}.csv")}
        ids0 = sorted({r["stock_id"] for r in s0})
        assert all(s in ids0 for s in FUTURES6)
        gone = [i for i in ids0 if i not in s1]
        assert all(i in dld for i in gone) and not [i for i in ids0 if i in dld and i in s1]
        by_year: dict[str, int] = {}
        for r in dl:
            by_year[r["date"][:4]] = by_year.get(r["date"][:4], 0) + 1
        idle = [r["stock_id"] for r in s0 if float(r["close"]) == 0]
        lines.append(flagged(f"ETFs with a row on {BASE}: {len(ids0)} ({len(idle)} untraded that day: "
                             f"{', '.join(idle)}); without a row on {END}: {len(gone)} "
                             f"({', '.join(f'{i} {dld[i]}' for i in gone)}); survivors {len(ids0) - len(gone)}; ETFs "
                             f"with a row on {END}: {len(s1)}; delisted ids from '00', {min(dld.values())} .. "
                             f"{max(dld.values())}: {len(dl)}, by year "
                             + ", ".join(f"{y} {n}" for y, n in sorted(by_year.items()))))                  # 18
    g6 = {s: growth_to_end(s, raw6) for s in FUTURES6}
    lines.append(flagged(f"commodity and volatility futures ETFs with a row on {BASE}: "
                 + ", ".join(f"{s} G {f(g6[s][0], 3, 4)} to {g6[s][1]}"
                             + (f" (delisted {dld[s]})" if s in dld else "") for s in FUTURES6)))         # 19
    all6 = float(np.mean([g6[s][0] for s in FUTURES6]))
    sur6 = float(np.mean([g6[s][0] for s in FUTURES6 if s not in dld]))
    y = years(BASE, END)
    lines.append(flagged(f"equal amounts on {BASE}, held (a delisted fund's last close kept as cash at 0): all six "
                 f"{f(all6, 3, 4)} ({f(all6 - 1, 3, 4, plus=True)}), log growth {f(log(all6) / y, 3, 4)} a year; "
                 f"the four survivors {f(sur6, 3, 4)} ({f(sur6 - 1, 3, 4, plus=True)}), {f(log(sur6) / y, 3, 4)} a "
                 f"year; gap {f(log(sur6) / y - log(all6) / y, 3, 4)} a year; years {f(y, 4)}"))          # 20
    absent = [s for s in COHORT33 if s not in E5_FILES and not (raw6 / f"{s}__2016-12-01__2026-10-08.csv").exists()]
    if absent:
        lines.append(f"optional cohort (codes ending L, R or U, {len(COHORT33)} funds): PENDING REGISTRATION "
                     f"({len(absent)} files absent); skipped")                                              # 21
    else:
        gc = {s: growth_to_end(s, raw6)[0] for s in COHORT33}
        a = float(np.mean(list(gc.values())))
        b = float(np.mean([v for s, v in gc.items() if s not in dld]))
        lines.append(flagged(f"optional cohort (codes ending L, R or U with a row on {BASE}): {len(gc)} funds, "
                     f"{sum(s in dld for s in gc)} delisted ({', '.join(s for s in gc if s in dld)}); equal "
                     f"amounts held: all {f(a, 2, 3)} ({f(log(a) / y, 3, 4)} a year), survivors {f(b, 2, 3)} "
                     f"({f(log(b) / y, 3, 4)} a year); median G {f(float(np.median(list(gc.values()))), 2, 3)}; "
                     f"G below 1: {sum(v < 1 for v in gc.values())} of {len(gc)}"))                        # 21
    return lines


# ================================================================ LM21's Experiment 10 and the reality check
def reality_check(R: Vec) -> None:
    T, M = len(R), 10_000
    pos = np.random.default_rng([10, SEED]).integers(0, 2, size=(M, T), dtype=np.int8)
    dbar = np.empty(M)
    s_u = np.empty(M)
    for c in range(0, M, 500):
        x = (2.0 * pos[c:c + 500].astype(np.float64) - 1.0) * R
        dbar[c:c + 500] = x.mean(axis=1)
        s_u[c:c + 500] = x.std(axis=1, ddof=1)
    tt = dbar / (s_u / sqrt(T))
    best = int(np.argmax(tt))
    put(f"Experiment 10 (LM21, default_rng([10, 20261011])): best t-stat {f(tt[best], 2)} (rule {best + 1}); t >= 3: "
        f"{int((tt >= 3 - EPS).sum())}; mean {f(float(tt.mean()), 2)}, s {f(float(tt.std(ddof=0)), 3)}; s_u of the "
        f"rules' daily returns {f(float(s_u.min()), 6)} .. {f(float(s_u.max()), 6)}")                       # 22
    p1 = float(stats.norm.sf(tt[best]))
    put(f"the best rule's one-sided normal p-value {p1:.3e}; times 10,000 (Bonferroni) {f(min(1.0, M * p1), 3)}; "
        f"(21.9) for 10,000 independent rules: Pr(max >= {tt[best]:.4f}) = {f(1 - stats.norm.cdf(tt[best]) ** M, 3)}; "
        f"(21.9)'s 95% quantile of the max {f(float(stats.norm.ppf(0.95 ** (1 / M))), 2)}; one-sided Bonferroni level "
        f"for 10,000 tests at 5% {f(float(stats.norm.isf(0.05 / M)), 2)}")                                 # 23
    g1 = rng(1)
    thr = sqrt(2 * log(log(T)))                   # Hansen's threshold on the t scale
    keep = tt >= -thr                             # rules recentred by the consistent SPA
    mw, mt, mc = np.empty(B_RC), np.empty(B_RC), np.empty(B_RC)
    batch, chunk = min(1000, B_RC), 2000
    for b0 in range(0, B_RC, batch):
        C = np.empty((T, batch))
        for j in range(batch):
            C[:, j] = np.bincount(stationary_idx(g1, T, ELL_TR23), minlength=T)
        RC = R[:, None] * C / T
        w_, t_, c_ = np.full(batch, -np.inf), np.full(batch, -np.inf), np.full(batch, -np.inf)
        for r0 in range(0, M, chunk):
            Fb = 2.0 * pos[r0:r0 + chunk].astype(np.float64) - 1.0
            Db = Fb @ RC                          # resampled means, rules x resamples
            se = s_u[r0:r0 + chunk, None] / sqrt(T)
            dc = Db - dbar[r0:r0 + chunk, None]
            w_ = np.maximum(w_, sqrt(T) * dc.max(axis=0))
            z = dc / se
            t_ = np.maximum(t_, z.max(axis=0))
            c_ = np.maximum(c_, np.where(keep[r0:r0 + chunk, None], z, Db / se).max(axis=0))
        mw[b0:b0 + batch], mt[b0:b0 + batch], mc[b0:b0 + batch] = w_, t_, c_
    Vw = sqrt(T) * float(dbar.max())
    pw = float((mw >= Vw - EPS).mean())
    pt = float((mt >= tt[best] - EPS).mean())
    pc = float((np.maximum(mc, 0.0) >= max(float(tt[best]), 0.0) - EPS).mean())
    q95 = float(np.quantile(mt, 0.95, method="inverted_cdf"))
    put(f"reality check, experiment 1 (stationary bootstrap, mean block {ELL_TR23}, B = {B_RC}): White's statistic "
        f"max of sqrt(T) x mean = {f(Vw * 100, 4)} percent, p-value {f(pw, 3)} (MC SE {f(sqrt(pw * (1 - pw) / B_RC), 3)}); "
        f"the best rule by mean is the best by t-stat: {int(np.argmax(dbar)) == best}")                     # 24
    put(f"studentized (max t-stat): p-value {f(pt, 3)} (MC SE {f(sqrt(pt * (1 - pt) / B_RC), 3)}); bootstrap 95% "
        f"quantile of the max {f(q95, 2)}; Romano-Wolf's first step at 5% rejects {int((tt > q95 + EPS).sum())} rules; "
        f"Hansen's consistent SPA ({int(keep.sum())} rules recentred, those with t >= -{f(thr, 3)}): p-value "
        f"{f(pc, 3)} (MC SE {f(sqrt(pc * (1 - pc) / B_RC), 3)})")                                           # 25


# ================================================================ the PBO grid (declared in the brief before it was run)
SKIPPED: list[str] = []       # grid cross-checks where CLARABEL failed (OSQP checked instead)
ORIG_CHECK = V.cvx_check


def cvx_check_grid(S: Mat, a: Vec, exact: Vec, label: str) -> tuple[float, float]:
    """vol5_rules.cvx_check; when CLARABEL fails, the polished OSQP solution alone is compared with the exact one."""
    try:
        return ORIG_CHECK(S, a, exact, label)
    except cp.error.SolverError:
        y = cp.Variable(len(a))
        prob = cp.Problem(cp.Minimize(cp.quad_form(y, cp.psd_wrap(S))), [a @ y == 1, y >= 0])
        prob.solve(solver=cp.OSQP, **V.OSQP_OPTS)
        assert prob.status == "optimal" and y.value is not None
        yv = np.asarray(y.value, dtype=float)
        gap = float(np.abs(yv / yv.sum() - exact).max())
        assert gap <= V.OSQP_TOL, (label, gap)
        SKIPPED.append(f"{label} (window {V.WINDOW}; OSQP gap {gap:.1e})")
        return gap, float("nan")


@contextmanager
def window(w: int) -> Generator[None]:
    """vol5_rules with WINDOW = w and the grid's cross-check, both restored on exit."""
    old = V.WINDOW
    # setattr, not assignment: ty types the module constant as Literal[504]; both are restored below
    setattr(V, "WINDOW", w)  # noqa: B010
    setattr(V, "cvx_check", cvx_check_grid)  # noqa: B010
    try:
        yield
    finally:
        setattr(V, "WINDOW", old)  # noqa: B010
        setattr(V, "cvx_check", ORIG_CHECK)  # noqa: B010


def cscv(x: Mat, ex: float, S: int = BLOCKS) -> tuple[Vec, Vec, Vec, NDArray[np.int64], int, int]:
    """Combinatorially symmetric cross-validation on per-day Sharpe ratios of x - ex (the brief's declaration):
    returns the logits, the in-sample best's in-sample and out-of-sample Sharpe ratios, its index, the block length
    and the number of earliest rows dropped."""
    n_t, n = x.shape
    m = n_t // S
    blk = (x[n_t - m * S:] - ex).reshape(S, m, n)
    s1, s2 = blk.sum(axis=1), (blk**2).sum(axis=1)
    cmb = np.array(list(combinations(range(S), S // 2)))
    mask = np.zeros((len(cmb), S))
    mask[np.arange(len(cmb))[:, None], cmb] = 1.0
    h = m * (S // 2)
    i1, i2 = mask @ s1, mask @ s2
    o1, o2 = s1.sum(axis=0) - i1, s2.sum(axis=0) - i2
    sr_i = (i1 / h) / np.sqrt(i2 / h - (i1 / h) ** 2)
    sr_o = (o1 / h) / np.sqrt(o2 / h - (o1 / h) ** 2)
    ns = np.argmax(sr_i, axis=1)
    rows = np.arange(len(cmb))
    so = sr_o[rows, ns]
    rank = 1 + (sr_o < so[:, None]).sum(axis=1)
    om = rank / (n + 1)
    return np.log(om / (1 - om)), sr_i[rows, ns], so, ns.astype(np.int64), m, n_t - m * S


def pbo_grid(case: Case) -> int:
    fr, sigs, rules = case.fr, case.sigs, V.RULES
    by_w: dict[int, list[V.Signal]] = {}
    for w in (126, 252, 504):
        with window(w):
            sg = V.signals(fr, [])
        k0 = next(i for i, s in enumerate(sg) if s.signal == sigs[0].signal)
        by_w[w] = sg[k0:]
        assert [s.signal for s in by_w[w]] == [s.signal for s in sigs]
    for a, b in zip(by_w[504], sigs, strict=True):
        assert all(np.array_equal(a.targets[k], b.targets[k]) for k in rules)
    conf = [(k, 0, q) for k in ("R1", "R2") for q in (1, 3, 6)]
    conf += [(k, w, q) for k in rules[2:] for w in (126, 252, 504) for q in (1, 3, 6)]
    n = len(conf)
    rets, growth = [], []
    for k, w, q in conf:
        p = V.wealth_path(fr, by_w[504 if w == 0 else w][::q], k)
        assert p.ruin is None and p.dates == case.paths["R1"].dates
        rets.append(p.wealth[1:] / p.wealth[:-1] - 1)
        growth.append(float(np.log(p.wealth[-1]) / case.ev_years))
    X = np.column_stack(rets)
    Tg = X.shape[0]
    name = [f"{k} {'-' if w == 0 else w} {q}m" for k, w, q in conf]
    order = list(np.argsort(-np.array(growth), kind="stable"))
    put(f"grid: {n} configurations (R1, R2 x 3 frequencies; R3-R8 x windows 126, 252, 504 x frequencies 1, 3, 6 "
        f"months); {Tg} daily net returns {case.paths['R1'].dates[1]} .. {case.paths['R1'].dates[-1]}; trades per "
        f"frequency {len(sigs)}, {len(sigs[::3])}, {len(sigs[::6])}; CLARABEL cross-checks that failed (OSQP "
        f"checked instead): {len(SKIPPED)} ({'; '.join(SKIPPED)})")                                       # 26
    tcase = [name.index(f"{k} {'-' if k in ('R1', 'R2') else 504} 1m") for k in rules]
    est = [i for i in order if conf[i][0] not in ("R1", "R2")]
    put(f"grid net growth a year: best {name[order[0]]} {f(growth[order[0]], 3, 4)}, second {name[order[1]]} "
        f"{f(growth[order[1]], 3, 4)}, median {f(float(np.median(growth)), 3, 4)}, worst {name[order[-1]]} "
        f"{f(growth[order[-1]], 3, 4)}; the through case's ranks (1 = best of {n}): "
        + ", ".join(f"{k} {order.index(i) + 1}" for k, i in zip(rules, tcase, strict=True))
        + f"; best estimated rule (R3-R8): {name[est[0]]} {f(growth[est[0]], 3, 4)}")                     # 27
    put("grid net growth by rule, min .. max over its configurations: "
        + ", ".join(f"{k} {f(min(g for c, g in zip(conf, growth, strict=True) if c[0] == k), 3, 4)} .. "
                    f"{f(max(g for c, g in zip(conf, growth, strict=True) if c[0] == k), 3, 4)}" for k in rules))  # 28
    aw = fr.A_wealth
    lg, is_, oos, ns, m, drop = cscv(X, V.RF / aw)
    sl, ic = np.polyfit(is_ * sqrt(aw), oos * sqrt(aw), 1)
    pbo = float((lg <= EPS).mean())
    put(f"CSCV: S = {BLOCKS} blocks of {m} days ({drop} earliest days dropped), C(16, 8) = {comb(16, 8)} splits (the "
        f"paper prints 12,780); PBO {f(pbo, 3)}; logit median {f(float(np.quantile(lg, 0.5, method='inverted_cdf')), 2)}, "
        f"mean {f(float(lg.mean()), 2)}; the in-sample best's out-of-sample Sharpe ratio is below 0 in "
        f"{f(float((oos < 0).mean()), 3)} of the splits; annualized (x sqrt A_w): in-sample best's mean {f(float(is_.mean()) * sqrt(aw), 2)} "
        f"in sample, {f(float(oos.mean()) * sqrt(aw), 2)} out of sample; OLS of out-of-sample on in-sample: slope "
        f"{f(sl, 2)}, intercept {f(ic, 2)}")                                                               # 29
    cnt = np.bincount(ns, minlength=n)
    top = list(np.argsort(-cnt, kind="stable")[:3])
    put("most frequent in-sample best: " + ", ".join(f"{name[i]} {int(cnt[i])} ({f(float(cnt[i]) / len(lg), 3)})" for i in top)
        + f"; distinct in-sample bests {int((cnt > 0).sum())}")                                            # 30
    edges = np.linspace(-4.5, 4.5, 19)
    hist = np.histogram(np.clip(lg, -4.5 + 1e-9, 4.5 - 1e-9), bins=edges)[0]
    put(f"logit histogram, bins of 0.5 from -4.5 to 4.5 (ends clipped): {', '.join(str(int(h)) for h in hist)}; min "
        f"{f(float(lg.min()), 2)}, max {f(float(lg.max()), 2)}; possible values ln(r / ({n + 1} - r)), r = 1..{n}")  # 31
    bench = name.index("R1 - 1m")
    oth = [i for i in range(n) if i != bench]
    D = X[:, oth] - X[:, [bench]]
    dm, su = D.mean(axis=0), D.std(axis=0, ddof=1)
    tg = dm / (su / sqrt(Tg))
    # LM22's rule (lm22.md:254): the largest stationary Politis-White estimate among the squared demeaned simple-return
    # series the statistic involves (the 60 configurations), rounded
    pws = [float(optimal_block_length((X[:, j] - X[:, j].mean()) ** 2)["stationary"].iloc[0]) for j in range(n)]
    jpw = int(np.argmax(pws))
    ell = float(round(pws[jpw]))
    def max_t(g: np.random.Generator, length: float) -> Vec:
        out = np.empty(B_RC)
        for b in range(B_RC):
            c = np.bincount(stationary_idx(g, Tg, length), minlength=Tg)
            out[b] = float((((c @ D) / Tg - dm) / (su / sqrt(Tg))).max())
        return out

    mx = max_t(rng(4), ell)
    ell1 = float(round(pws[bench]))
    mx1 = max_t(rng(5), ell1)                     # sensitivity: R1 monthly's own estimate, rounded
    jb = int(np.argmax(tg))
    pg = float((mx >= tg[jb] - EPS).mean())
    pg1 = float((mx1 >= tg[jb] - EPS).mean())
    cg = np.corrcoef(D, rowvar=False)
    iu = np.triu_indices(len(oth), 1)
    p1 = float(stats.norm.sf(tg[jb]))
    put(f"reality check on the grid against R1 monthly (experiment 4, B = {B_RC}, mean block {ell:.0f}, LM22's rule: the "
        f"largest Politis-White estimate on the 60 configurations' squared demeaned returns, {name[jpw]} "
        f"{f(pws[jpw], 2)}; smallest {f(min(pws), 2)}, R1 monthly's {f(pws[bench], 2)}): best t-stat {name[oth[jb]]} "
        f"{f(tg[jb], 2)}; "
        f"one-sided normal p {f(p1, 4)}, Bonferroni x {len(oth)} {f(min(1.0, len(oth) * p1), 3)}; reality-check p "
        f"{f(pg, 3)} (MC SE {f(sqrt(pg * (1 - pg) / B_RC), 3)}); bootstrap 95% quantile of the max t-stat "
        f"{f(float(np.quantile(mx, 0.95, method='inverted_cdf')), 2)} against Bonferroni's "
        f"{f(float(stats.norm.isf(0.05 / len(oth))), 2)}; correlations of the {len(oth)} differences: median "
        f"{f(float(np.median(cg[iu])), 2)}, min {f(float(cg[iu].min()), 2)}; sensitivity (experiment 5, mean block "
        f"{ell1:.0f}, R1 monthly's own estimate rounded): reality-check p {f(pg1, 3)} (MC SE "
        f"{f(sqrt(pg1 * (1 - pg1) / B_RC), 3)})")                                                           # 32
    return Tg


# ================================================================ Model: noise strategies under CSCV
def noise(Tg: int, aw: float) -> None:
    g2 = rng(2)
    n = 60
    pb, a_is, a_oos = [], [], []
    for _ in range(N_NOISE):
        lg, is_, oos, *_ = cscv(g2.standard_normal((Tg, n)) * 0.01, 0.0)
        pb.append(float((lg <= EPS).mean()))
        a_is.append(float(is_.mean()) * sqrt(aw))
        a_oos.append(float(oos.mean()) * sqrt(aw))
    mp, sp = float(np.mean(pb)), float(np.std(pb, ddof=0)) / sqrt(N_NOISE)
    half = (Tg // BLOCKS) * BLOCKS // 2
    put(f"noise (experiment 2, Model): {N_NOISE} panels of {n} iid normal strategies with mean 0, {Tg} days: PBO mean "
        f"{f(mp, 3)} (SE {f(sp, 3)}), range {f(min(pb), 3)} .. {f(max(pb), 3)}; the in-sample best's annualized Sharpe "
        f"ratio, mean over panels: {f(float(np.mean(a_is)), 2)} in sample, {f(float(np.mean(a_oos)), 2)} out of sample; "
        f"(21.9)'s median of the max of {n} standard normals times sqrt(A_w / {half}): "
        f"{f(float(stats.norm.ppf(0.5 ** (1 / n))) * sqrt(aw / half), 2)}")                                # 33
    g3 = rng(3)
    out: dict[tuple[int, float], tuple[float, float]] = {}
    for k in (2, 5, 10, 20, 60, 100):
        for sr in (0.0, 0.5, 1.0, 1.5, 2.0):
            v = []
            for _ in range(N_STATE):
                Z = g3.standard_normal((Tg, k)) * 0.01
                Z[:, 0] += sr / sqrt(aw) * 0.01
                v.append(float((cscv(Z, 0.0)[0] <= EPS).mean()))
            out[(k, sr)] = (float(np.mean(v)), float(np.std(v, ddof=0)) / sqrt(N_STATE))
    put(f"widget grid (experiment 3, Model; {N_STATE} panels per state, in the order printed; configuration 1 has the "
        "annual Sharpe ratio 0, 0.5, 1, 1.5, 2, the others 0): mean PBO "
        + "; ".join(f"N = {k}: " + " ".join(f(out[(k, s)][0], 2) for s in (0.0, 0.5, 1.0, 1.5, 2.0))
                    for k in (2, 5, 10, 20, 60, 100))
        + f"; largest SE {f(max(v[1] for v in out.values()), 3)}; {Tg} days, {BLOCKS} blocks")              # 34
    put(f"C(16, 8) = {comb(16, 8)}, C(10, 5) = {comb(10, 5)}, C(8, 4) = {comb(8, 4)}; every subset of 16 blocks "
        f"2^16 = {2**16}; logit ln(r / (N + 1 - r)): "
        f"N = 60, r = 30: {f(log(30 / 31), 4)}, r = 31: {f(log(31 / 30), 4)}, r = 60: {f(log(60 / 1), 3)}, r = 1: "
        f"{f(log(1 / 60), 3)}")                                                                              # 35


def same_close(case: Case) -> None:
    """The through case traded at the signal's own close (impossible: the close is known only after 13:30)."""
    fr, rules = case.fr, V.RULES
    idx = {d: i for i, d in enumerate(fr.wealth_dates)}
    ok = [bool(fr.traded[idx[s.signal]].all()) for s in case.sigs]
    early = [V.Signal(s.signal, s.signal, s.targets) for s in case.sigs]
    g = {k: num(V.summary(fr, V.wealth_path(fr, early, k)), "growth") for k in rules}
    base = {k: num(V.summary(fr, case.paths[k]), "growth") for k in rules}
    put(f"trading at the signal's own close ({sum(ok)} of {len(ok)} signal days with every fund trading; growth from "
        f"the cash of 1 at {early[0].trade}): " + ", ".join(f"{k} {f(g[k], 3, 4)}" for k in rules) + "; minus the "
        "through case's: " + ", ".join(f"{k} {f(g[k] - base[k], 4, 5, plus=True)}" for k in rules))       # 36


def main() -> None:
    case = through_case()
    adjusted_prices()
    R, TD = tr23()
    vol_scale(R, TD)
    kelly_walk(R, TD)
    for line in survivorship(RAW6):
        put(line)
    reality_check(R)
    Tg = pbo_grid(case)
    noise(Tg, case.fr.A_wealth)
    same_close(case)
    for line in OUT:
        print(line)


if __name__ == "__main__":
    main()
