"""LM34 anchors (Backtesting Without Fooling Yourself): every number the Stage 1 brief quotes (2026-10-24, third revision;
last pass 2026-10-25; fresh check of the whole of Stage 1, 2026-10-31).

The fresh check (2026-10-31) changed: A34-16 and A34-17 trade at the close after the signal's close (section 2's
protocol), and A34-16 also prints E5's slip, the scale traded at its own close; A34-17 adds the held growth at 2.07,
half of the printed root; A34-24 and A34-32 flag the block-length estimates at 0 decimals; f() tests the boundary on
the exact decimal of repr(x); A34-26 prints the lab's every-12th-signal trades and the OSQP gap as a bound; A34-33
prints the Monte Carlo SEs of the two means and (21.9)'s mean of the maximum; A34-38 (new) is the through case's
growth at r_f = 0 and 2%.

Reads only data/processed/*.parquet through the shared builders, plus the registered raw files named here (run the
builders first):
  * E5 (the through case): data/vol5_series.py's frames("E5") and ohlc(fund) (data/processed/vol5_frames.parquet,
    vol5_ohlc.parquet), and data/vol5_rules.py's signals(), schedule(), wealth_path() and summary(), which every
    Volume V-VI script imports; no rule is re-implemented here. 0050's distributions, the split table and the price
    files of 00635U and 00642U are read from their registered raw files under data/raw/vol5/, read-only:
    vol5_series's own readers delete its outputs on a failed check, so they are not called.
  * TR23 (Volume III): data/processed/vol3_taiex.parquet (columns date, tr, price, R, Rp; R the total-return index's
    simple daily return), for LM21's Experiment 10 (recomputed with LM21's seed) and the TR23 problems.
  * LM34's survivorship files, registered under data/raw/vol6/ (data/README.md): TaiwanStockDelisting (ids from
    "00"), the daily prices of 00672L, 00673R, 00674R and 00677U (Free), and two TaiwanStockPrice snapshots of every
    ETF on 2017-01-17 and 2026-10-08 (no data_id, served only above FinMind's Free plan). A34-18 alone reads the
    snapshots; on a Free account they are fetched with --exclude vol6/etf_snapshot, and A34-18 prints a note instead
    of its value. The other files are required.

Conventions (plans/vol-5.md, shared decisions and the editor's decisions on the briefs). The through case's settings
are vol5_rules.py's (window WINDOW = 504 estimation rows, month-end signals, trade at the next session's close on which
every fund trades, costs COMMISSION and TAX, cash at RF = 1.5% a year, borrowing at RF + SPREAD, valuation to
2026-10-08 with no terminal liquidation). "Growth" is ln(final wealth) / years from the cash of 1 at the first trade's
close (years = calendar days / 365.25 from the close before a sample's first return to its last close, AUTHORING
section 8); "gross" is the same path with cost_mult = 0 (trading costs removed, financing
kept); "costs" are the sum over trades of cost / pre-trade wealth; "turnover" is the sum of one-way turnovers after the
first purchase per year (summary()). A rule's Sharpe ratio, volatility, VaR and drawdown are other modules' statistics
(LM33, LM30-LM31, LM32) and are not printed; the cost arithmetic of a single trade is LM27's and is echoed. The PBO
grid (declared before it was computed; the brief's "PBO grid") reuses signals() with vol5_rules.WINDOW set to 126, 252
or 504 for the call and restored after it, and keeps the through case's schedule from its first signal; a k-month
configuration trades at signals 1, 1 + k, 1 + 2k, ... A34-38 sets vol5_rules.RF to 0 and 0.02 for the call in the
same way and restores it. TR23's statistics use r_f = 0 (Volume IV), except one sensitivity of the Kelly walk-forward
that charges BORROW on the exposure above 1; TR23's rules follow section 2's protocol: a signal set at a close is
traded at the next close, so it first earns the return of the session after that.
Block lengths follow LM22's rule (lm22.md:254): the largest stationary Politis-White estimate among the squared
demeaned series the statistic involves, rounded; for a comparison with R1, the differences from R1.
Quantiles and medians: inverted_cdf. Counts against a threshold use the guard EPS = 1e-12.
Simulation (AUTHORING section 8): one generator per experiment, np.random.default_rng([e, 20261011]):
  e = 1  the reality check on Experiment 10 (stationary bootstrap, mean block length 145 by LM22's rule on the 10,000
         rules' squared demeaned returns, as LM22's TR23 length, drawn by LM22's stationary_idx, lm22.md:372-380; B_RC resamples in
         batches of 1,000);
  e = 2  noise strategies under CSCV (Model): N_NOISE panels of 60 iid normal strategies on the grid's evaluation days,
         each panel one draw standard_normal((1851, 60)) x 0.01 (rows days, columns strategies), the panels in
         sequence on the one generator;
  e = 3  the widget's grid (Model): N_STATE panels per state, each one draw standard_normal((1851, n)) x 0.01 (rows
         days) with strategy 1 (column 0) given its drift, the panels in sequence and the states in the order
         printed, all on the one generator;
  e = 4  the reality check on the PBO grid against R1 monthly (stationary bootstrap, mean block length by LM22's rule
         on the 59 differences from R1);
  e = 5  the same at ELL_SENS = 17, R1 monthly's own Politis-White length, rounded (the editor's sensitivity).
LM21's Experiment 10 keeps LM21's generator default_rng([10, 20261011]). A Monte Carlo proportion's standard error is
sqrt(p (1 - p) / B); the SE of a Monte Carlo mean is the SD of the panel values (divisor the panel count) over the
square root of that count.

Rounding flags. Every number the brief prints passes through f(x, k1, k2, ...), which shows x with max(k) + 3 decimals
and flags it "NEAR" for each printed precision k at which x lies within a tenth of a last-digit unit of a rounding
boundary (|frac(10^k |x|) - 0.5| < 0.1, computed on the exact decimal of repr(x), so that a value such as 0.3754 is
not flagged by binary rounding). The brief prints a flagged value as rounded from the unrounded value here.

Prints one line per anchor, "A34-NN <value>", in ID order (A34-21 is withdrawn and keeps its ID; A34-37, problem 10's
means of X5's printed factors, was added by the third revision, and A34-38, the paths at r_f = 0 and 2%, by the fresh
check; they print last), and writes nothing.

Run:  PYTHONUTF8=1 uv run python data/vol6_anchors_lm34.py
"""
import csv
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from itertools import combinations
from math import comb, log, sqrt
from pathlib import Path

import cvxpy as cp
import numpy as np
import polars as pl
import vol5_rules as V
from arch.bootstrap import optimal_block_length
from numpy.lib.stride_tricks import sliding_window_view
from numpy.typing import NDArray
from scipy import integrate, stats
from scipy.optimize import brentq
from vol5_series import Frames, frames, ohlc

HERE = Path(__file__).resolve().parent
PROC = HERE / "processed"
RAW5 = HERE / "raw" / "vol5"
RAW6 = HERE / "raw" / "vol6"
EPS = 1e-12
SEED = 20261011
B_RC = 10_000          # reality-check resamples (experiments 1 and 4)
N_NOISE = 200          # noise panels (experiment 2)
N_STATE = 40           # panels per widget state (experiment 3)
BLOCKS = 16            # CSCV blocks
ELL_TR23 = 145         # LM22's mean block length for TR23 (lm22.md:427); checked against the rule in reality_check()
ELL_SENS = 17          # the grid's block-length sensitivity (editor's decision D): R1 monthly's own estimate, rounded
BORROW = V.RF + V.SPREAD   # 3.5% a year, the through case's illustrative borrowing rate, for the Kelly lab's sensitivity
F_LM22 = 4.14          # TR23's full-sample Kelly root as lm22.md:125 prints it (LM17's), which problem 9 prints
BASE, END = "2017-01-17", "2026-10-08"
# The six ETFs on the 2017-01-17 list whose names (FinMind TaiwanStockInfo, retrieved 2026-10-24, not registered) name
# an S&P gold or oil index or the VIX; 00672L's and 00677U's names are also in the registered delisting file.
FUTURES6 = {"00635U": "期元大S&P黃金", "00642U": "期元大S&P石油", "00672L": "元大S&P原油正2",
            "00673R": "期元大S&P原油反1", "00674R": "期元大S&P黃金反1", "00677U": "期富邦VIX"}
E5_FILES = ("00635U", "00642U")    # survivorship funds whose price files are E5's (data/raw/vol5/)
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
        u = abs(Decimal(repr(x))) * 10**k        # the exact decimal of the printed float, not its binary product
        if abs(u - int(u) - Decimal("0.5")) < Decimal("0.1"):
            NEAR.append(f"{x:.{k + 3}f} at {k} dp")
    return f"{x:{'+' if plus else ''}.{max(ks) + 3}f}"


def years(d0: str, d1: str) -> float:
    return (date.fromisoformat(d1) - date.fromisoformat(d0)).days / 365.25


def rng(e: int) -> np.random.Generator:
    return np.random.default_rng([e, SEED])


def stationary_idx(g: np.random.Generator, T: int, ell: float) -> NDArray[np.int64]:
    """LM22's stationary bootstrap indices (lm22.md:372-380), drawn in arch's order."""
    start = g.integers(T, size=T)
    new = g.random(T) <= 1 / ell
    new[0] = True
    first = np.flatnonzero(new)
    blk = np.cumsum(new) - 1
    step = np.arange(T) - first[blk]
    return (start[first][blk] + step) % T


def pw_stationary(x: Vec) -> float:
    """Politis-White's stationary block length of the squared demeaned series (LM22's rule, before the rounding)."""
    return float(optimal_block_length((x - x.mean()) ** 2)["stationary"].iloc[0])


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
    """Date -> new units per old unit (k for a k-for-1 split, 1/k for a k-to-1 reverse split), from SPLITS: on that
    day the previous close is restated per current share, divided by this ratio (Volume I's total return). The ratio
    is the registered before / after price (or its inverse) rounded to an integer; it must lie within 0.01 of one."""
    out = {}
    for s, d, b, a in SPLITS:
        if s == sym:
            q = b / a if b >= a else a / b
            k = int(q.to_integral_value())
            assert k >= 2 and abs(q - k) < Decimal("0.01"), (sym, d, q)
            out[d] = float(k) if b >= a else 1 / k
    return out


def split_ratios(sym: str) -> list[Decimal]:
    """The registered before / after price ratios (or their inverses, for a reverse split) of sym's splits."""
    return [b / a if b >= a else a / b for s, _, b, a in SPLITS if s == sym]


def split_ratio_gap(sym: str) -> float:
    """Largest |registered price ratio - integer ratio| over sym's splits."""
    gaps = [abs(q - q.to_integral_value()) for q in split_ratios(sym)]
    return float(max(gaps)) if gaps else 0.0


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
        f"({paths['R1'].dates[1]} .. {paths['R1'].dates[-1]}); evaluation years (calendar days / 365.25 from the "
        f"close of {sigs[0].trade}, the close before the first return) {f(ev_years, 2, 4)}")               # 02
    gross = {k: V.wealth_path(fr, sigs, k, cost_mult=0.0) for k in rules}
    summ = {k: V.summary(fr, paths[k]) for k in rules}
    gsum = {k: V.summary(fr, gross[k]) for k in rules}
    for k in rules:
        assert "ruin" not in summ[k] and "ruin" not in gsum[k]
    put("net final wealth: " + ", ".join(f"{k} {f(paths[k].wealth[-1], 3, 4)}" for k in rules))           # 03
    put("net growth a year: " + ", ".join(f"{k} {f(num(summ[k], 'growth'), 3, 4)}" for k in rules))        # 04
    put("gross growth a year (trading costs 0, financing kept): "
        + ", ".join(f"{k} {f(num(gsum[k], 'growth'), 3, 4)}" for k in rules)
        + "; gross minus net: "
        + ", ".join(f"{k} {f(num(gsum[k], 'growth') - num(summ[k], 'growth'), 4, 5)}" for k in rules))     # 05
    put("turnover a year (one-way, after the first purchase): "
        + ", ".join(f"{k} {f(num(summ[k], 'turnover'), 2, 3)}" for k in rules)
        + f"; trades {len(paths['R1'].trades)} each")                                                      # 06
    ident = max(abs(log(gross[k].wealth[-1] / paths[k].wealth[-1]) + sum(log(1 - t.cost) for t in paths[k].trades))
                for k in rules)
    assert ident < 2e-14, ident                   # (34.1) holds to rounding noise on every rule
    put("costs (sum of cost / pre-trade wealth): " + ", ".join(f"{k} {f(num(summ[k], 'costs'), 4, 7)}" for k in rules)
        + "; per year: " + ", ".join(f"{k} {f(num(summ[k], 'costs') / ev_years, 4, 5)}" for k in rules)
        + "; ln(gross / net final wealth): "
        + ", ".join(f"{k} {f(log(gross[k].wealth[-1] / paths[k].wealth[-1]), 7)}" for k in rules)
        + "; the identity -sum ln(1 - cost / pre-trade wealth) against it, largest difference over the rules below "
        + f"2e-14 (floating-point noise, {ident:.1e} in this run)")                                         # 07
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
    std = V.COMMISSION / (1 + V.COMMISSION)
    for k in rules[:7]:
        t0 = paths[k].trades[0]
        assert abs(t0.exposure - 1) < 1e-12 and abs(t0.turnover - 0.5) < 1e-12 and abs(t0.cost - std) < 1e-15, k
    t8 = paths["R8"].trades[0]
    l8 = t8.exposure
    assert abs(t8.cost - V.COMMISSION * l8 / (1 + V.COMMISSION * l8)) < 1e-15 and abs(t8.turnover - l8 / 2) < 1e-12
    to1 = [t.turnover for t in paths["R1"].trades[1:]]
    co1 = [t.cost for t in paths["R1"].trades[1:]]
    put(f"first purchase from cash: R1-R7 (exposures summing to 1) turnover {f(0.5, 2)}, cost / wealth {f(std, 6)} "
        f"(0.001425 / 1.001425; echo of LM27, A27-23, for R1 and R2); R8, first exposure L = {f(l8, 2)} below 1: "
        f"turnover {f(t8.turnover, 4)}, cost / wealth {f(t8.cost, 6)} (0.001425 L / (1 + 0.001425 L)); R1's later "
        f"rebalances: mean one-way turnover {f(float(np.mean(to1)), 4)} (largest {f(max(to1), 4)}, LM27's A27-24), "
        f"mean cost / wealth {f(float(np.mean(co1)), 6)}")                                                  # 12
    v = 1_000_000
    c1 = v * V.COMMISSION
    sw_bd, sw_eq = 2 * c1 + v * V.TAX["00679B"], 2 * c1 + v * V.TAX["0050"]
    put(f"echo of LM27, A27-43 (the cost arithmetic of a trade is LM27's): switching NT$1,000,000 between two funds, "
        f"(27.3)'s approximation (commission {c1:.0f} on each side, tax {v * V.TAX['0050']:.0f} on a taxed sale, no "
        f"cost on the cost): 00679B -> 0050 {sw_bd:.0f} NT$ = {f(sw_bd / v, 4)} of the value, 0050 -> 00679B "
        f"{sw_eq:.0f} NT$ = {f(sw_eq / v, 4)}")                                                             # 13
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
    (q50,) = split_ratios("0050")
    put(f"0050 close {BASE} {c50[i17]:.2f}; adjusted close of that day in a series built on 2020-01-02 "
        f"{f(adj(BASE, '2020-01-02'), 2)}, on 2024-12-31 {f(adj(BASE, '2024-12-31'), 2)}, on {END} "
        f"{f(adj(BASE, END), 2)}; close {END} {c50[-1]:.2f}; distributions after {BASE}: "
        f"{sum(1 for d in div50 if BASE < d <= END)}, split 2025-06-18 (4 for 1: the registered before / after "
        f"price ratio {f(float(q50), 5)}, {f(split_ratio_gap('0050'), 5)} from the integer 4, so the previous close "
        f"is restated per current share, divided by 4, as Volume I's total return); growth factor {BASE} -> {END} "
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
    """A daily volatility scale min(1.5, sigma_bar_t / sigma_{t+1|t}) set at the close of t and traded at the close of
    t + 1, so that it scales R_{t+2} (section 2's protocol); against it, the same scale applied to R_t itself (peeking)
    and traded at its own close, scaling R_{t+1} (E5's slip), all three on the honest version's days. As R8 (vol5_rules.signals): sigma_bar_t^2 is the uncentred mean square of the 504 returns through t, and
    sigma^2_{t+1|t} is (26.2) with lambda 0.94 run through those 504 returns from the start value sigma_bar_t^2."""
    T, W, lam = len(R), 504, V.LAM
    win = sliding_window_view(R**2, W)            # win[j] holds R^2 at t - W + 1 .. t, t = j + W - 1
    sbar2 = np.full(T, np.nan)
    sbar2[W - 1:] = win.mean(axis=1)
    ew = np.full(T, np.nan)                       # ew[t] = sigma^2_{t+1|t}: R8's loop over the window, in closed form
    ew[W - 1:] = lam**W * sbar2[W - 1:] + win @ ((1 - lam) * lam ** np.arange(W - 1, -1, -1))
    for t in (W - 1, TD.index("2025-04-07"), T - 1):  # the closed form against R8's literal loop
        s2 = float(sbar2[t])
        for r in R[t - W + 1:t + 1]:
            s2 = lam * s2 + (1 - lam) * r * r
        assert abs(s2 - ew[t]) <= 1e-12 * s2, (TD[t], s2, ew[t])
    scale = np.minimum(1.5, np.sqrt(sbar2 / ew))  # known at the close of t
    honest = np.full(T, np.nan)
    honest[W + 1:] = scale[W - 1:-2]              # section 2: set at the close of t - 2, traded at t - 1, earns R_t
    slip = np.full(T, np.nan)
    slip[W:] = scale[W - 1:-1]                    # E5's slip: traded at the close it is set (t - 1), earns R_t
    peek = np.full(T, np.nan)
    peek[W:] = scale[W:]                          # day t uses the scale that already knows R_t
    ok = ~np.isnan(honest)                        # all three versions on the honest version's days
    yrs = years(TD[W], TD[-1])
    A = int(ok.sum()) / yrs

    def run(lv: Vec) -> tuple[float, float, float]:
        x = lv[ok] * R[ok]
        assert (1 + x).min() > 0
        return float(np.log1p(x).sum() / yrs), float(x.std() * sqrt(A)), float(x.min())

    i7 = TD.index("2025-04-07")
    gh, vh, mh = run(honest)
    gp, vp, mp = run(peek)
    gs = run(slip)[0]
    first = int(np.flatnonzero(ok)[0])
    assert first == W + 1
    put(f"TR23 (total-return index) volatility scale, as R8: daily simple returns in decimals, 504-return uncentred "
        f"window, (26.2) with lambda 0.94 run through each window from its sigma_bar^2, cap 1.5, cash and borrowing "
        f"at 0: {int(ok.sum())} days {TD[first]} .. {TD[-1]} ({f(yrs, 2)} years, calendar days / 365.25 from the "
        f"close of {TD[first - 1]}, the close before the first return; A {f(A, 2)} sessions a year); set at a close "
        f"and traded at the next close (section 2): growth {f(gh, 3, 4)}, volatility {f(vh, 3, 4)}, worst day "
        f"{f(mh, 4)}; using the same day's close: growth {f(gp, 3, 4)}, volatility {f(vp, 3, 4)}, worst day "
        f"{f(mp, 4)}; traded at the close it is set (E5's slip): growth {f(gs, 3, 4)}; 2025-04-07 (R "
        f"{f(R[i7], 4)}): scale {f(honest[i7], 3)} against {f(peek[i7], 3)}, the scaled return "
        f"{f(honest[i7] * R[i7], 4)} against {f(peek[i7] * R[i7], 4)}; TR23 itself on these days: growth "
        f"{f(float(np.log1p(R[ok]).sum() / yrs), 3, 4)}, volatility {f(float(R[ok].std() * sqrt(A)), 3, 4)}")  # 16


def kelly_root(x: Vec) -> float:
    lo, hi = -1 / x.max() * (1 - 1e-12), 1 / abs(x.min()) * (1 - 1e-12)
    return float(brentq(lambda v: float(np.mean(x / (1 + v * x))), lo, hi, xtol=1e-12))


def kelly_walk(R: Vec, TD: list[str]) -> None:
    """LM4's lab exercise on TR23: the root of (4.5) on the trailing 729 returns at a month-end, capped to [0, 3],
    traded at the next close (section 2's protocol, a session later than Lab 4's scaffold) and held to the close after
    the next month-end."""
    T, W = len(R), 729
    ends = [i for i in range(T - 1) if TD[i][:7] != TD[i + 1][:7] and i >= W - 1]
    lev = np.full(T, np.nan)
    fs = []
    for k, e in enumerate(ends):
        v = min(max(kelly_root(R[e - W + 1:e + 1]), 0.0), 3.0)
        fs.append(v)
        stop = ends[k + 1] + 2 if k + 1 < len(ends) else T     # the last root is held to the last close
        lev[e + 2:stop] = v
    mk = ~np.isnan(lev)
    assert int(np.flatnonzero(mk)[0]) == ends[0] + 2
    yk = years(TD[ends[0] + 1], TD[-1])
    full = kelly_root(R)

    def grow(x: Vec) -> float:
        assert (1 + x).min() > 0
        return float(np.log1p(x).sum() / yk)

    ak = int(mk.sum()) / yk

    def fin(lv: Vec) -> Vec:
        """lv R minus interest on the borrowed part, BORROW / A_k a session on max(lv - 1, 0)."""
        return lv * R[mk] - np.maximum(lv - 1, 0.0) * BORROW / ak

    put(f"Kelly walk-forward on TR23 (total-return index): {len(ends)} calendar month-ends {TD[ends[0]]} .. "
        f"{TD[ends[-1]]}, window {W} returns, root of (4.5) capped to [0, 3], traded at the next close (section 2); "
        f"{int(mk.sum())} days ({f(yk, 2)} years, "
        f"calendar days / 365.25 from the close of {TD[ends[0] + 1]}, the close before the first return); mean of the "
        f"{len(fs)} month-end leverages {f(float(np.mean(fs)), 2)}, at the cap "
        f"{sum(v >= 3 - EPS for v in fs)} month-ends, at 0 "
        f"{sum(v <= EPS for v in fs)}; growth {f(grow(lev[mk] * R[mk]), 3, 4)}; f = 1: {f(grow(R[mk]), 3, 4)}; the "
        f"full-sample root {f(full, 2, 3)} held: {f(grow(full * R[mk]), 3, 4)}; half of it: "
        f"{f(grow(full / 2 * R[mk]), 3, 4)}; with borrowing at {BORROW:.3f} a year on the exposure above 1 "
        f"(accrued over A_k = {f(ak, 2)} sessions a year; cash at 0): walk-forward {f(grow(fin(lev[mk])), 3, 4)}, "
        f"full-sample root {f(grow(fin(np.full(int(mk.sum()), full))), 3, 4)}; at the root as lm22.md:125 prints "
        f"it, {F_LM22:.2f}: held {f(grow(F_LM22 * R[mk]), 3, 4)}, with borrowing "
        f"{f(grow(fin(np.full(int(mk.sum()), F_LM22))), 3, 4)}; half of it, {F_LM22 / 2:.2f}: held "
        f"{f(grow(F_LM22 / 2 * R[mk]), 3, 4)}")                                                          # 17


# ================================================================ survivorship (registered: data/raw/vol6/)
def growth_to_end(sym: str) -> tuple[float, str, int, int]:
    """Growth factor from BASE's close to the last traded close on or before END, with the last traded date, the
    untraded rows skipped (close 0) and the zero spreads accepted. Splits come from the registered table with integer
    ratios (split_factor), and a split's before_price must equal the previous traded close. Every other traded close
    must equal the previous traded close plus the spread, except that a spread of 0 is accepted on the first traded
    row right after an untraded row (FinMind prints 0.0 there). None of these funds pays distributions."""
    raw = RAW5 if sym in E5_FILES else RAW6
    rows = [r for r in read_rows(raw / f"{sym}__2016-12-01__2026-10-08.csv") if BASE <= r["date"] <= END]
    assert rows[0]["date"] == BASE and Decimal(rows[0]["close"]) != 0, (sym, rows[0])
    sp = split_factor(sym)
    before = {d: b for s, d, b, _ in SPLITS if s == sym}
    g, prev, idle_before, idle, zeros, last = 1.0, Decimal(rows[0]["close"]), False, 0, 0, BASE
    for r in rows[1:]:
        c = Decimal(r["close"])
        if c == 0:
            idle_before, idle = True, idle + 1
            continue
        if r["date"] in sp:
            assert before[r["date"]] == prev, (sym, r["date"])
            g *= float(c) / (float(prev) / sp[r["date"]])
        else:
            spread = Decimal(r["spread"])
            if spread == 0 and c != prev:
                assert idle_before, (sym, r["date"], "a zero spread not right after an untraded row")
                zeros += 1
            else:
                assert c - prev == spread, (sym, r["date"], c, prev, spread)
            g *= float(c / prev)
        prev, idle_before, last = c, False, r["date"]
    return g, last, idle, zeros


def survivorship() -> list[str]:
    """The survivorship anchors A34-18 to A34-20, each with its own NEAR flags, and A34-21 (withdrawn)."""
    lines: list[str] = []
    dl = read_rows(RAW6 / "delisting__2000-01-01__2026-10-08.csv")
    dld = {r["stock_id"]: r["date"] for r in dl}
    dln = {r["stock_id"]: r["stock_name"] for r in dl}
    snaps = [RAW6 / f"etf_snapshot__{BASE}.csv", RAW6 / f"etf_snapshot__{END}.csv"]
    if not all(q.exists() for q in snaps):
        lines.append(f"not computed: {RAW6} lacks the ETF snapshots {', '.join(q.name for q in snaps if not q.exists())}"
                     " (TaiwanStockPrice without a data_id, fetched only above FinMind's Free plan; see data/README.md)")
    else:
        s0 = read_rows(snaps[0])
        s1 = {r["stock_id"] for r in read_rows(snaps[1])}
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
    for s in ("00672L", "00677U"):
        assert dln[s] == FUTURES6[s], (s, dln[s])
    g6 = {s: growth_to_end(s) for s in FUTURES6}
    lines.append(flagged(f"the six ETFs on the {BASE} list that track an S&P gold or oil index or the VIX (names "
                 "from FinMind's TaiwanStockInfo): " + ", ".join(
                     f"{s} G {f(g6[s][0], 3, 4)} to {g6[s][1]}" + (f" (delisted {dld[s]})" if s in dld else "")
                     for s in FUTURES6)
                 + "; untraded rows (close 0) skipped: " + ", ".join(f"{s} {g6[s][2]}" for s in FUTURES6 if g6[s][2])
                 + "; zero spreads accepted on the first traded row after an untraded one: "
                 + ", ".join(f"{s} {g6[s][3]}" for s in FUTURES6 if g6[s][3])
                 + "; every other close equals the previous traded close plus the spread; splits: "
                 + ", ".join(f"{s} {d} ({'1 for ' + str(round(1 / k)) if k < 1 else str(round(k)) + ' for 1'})"
                             for s in FUTURES6 for d, k in split_factor(s).items())
                 + (", the registered prices exactly the integer ratios" if max(split_ratio_gap(s) for s in FUTURES6)
                    == 0 else f", registered prices within {max(split_ratio_gap(s) for s in FUTURES6):.6f} of the "
                    "integer ratios")))                                                                       # 19
    all6 = float(np.mean([g6[s][0] for s in FUTURES6]))
    sur6 = float(np.mean([g6[s][0] for s in FUTURES6 if s not in dld]))
    y = years(BASE, END)
    lines.append(flagged(f"equal amounts on {BASE}, held (a delisted fund's last close kept as cash at 0): all six "
                 f"{f(all6, 3, 4)} ({f(all6 - 1, 3, 4, plus=True)}), log growth {f(log(all6) / y, 3, 4)} a year; "
                 f"the four survivors {f(sur6, 3, 4)} ({f(sur6 - 1, 3, 4, plus=True)}), {f(log(sur6) / y, 3, 4)} a "
                 f"year; gap {f(log(sur6) / y - log(all6) / y, 3, 4)} a year; years (calendar days / 365.25 from the "
                 f"close of {BASE}) {f(y, 4)}"))                                                              # 20
    lines.append("withdrawn (editor's decision 2026-10-24: the 33-fund L/R/U cohort is not registered; the ID is "
                 "kept so that later IDs do not move)")                                                      # 21
    PRINTED6.update({s: (g6[s][0], s in dld) for s in FUTURES6})
    return lines


PRINTED6: dict[str, tuple[float, bool]] = {}    # the six growth factors and whether delisted, for A34-37


def printed_factors() -> None:
    """Problem 10 as a reader solves it: the means of X5's six growth factors as printed (three decimals), and the gap
    in log growth they give (A34-37; A34-20 is the same from the unrounded factors)."""
    r3 = {s: Decimal(repr(g)).quantize(Decimal("0.001")) for s, (g, _) in PRINTED6.items()}
    a6 = float(sum(r3.values()) / 6)
    s4 = float(sum(v for s, v in r3.items() if not PRINTED6[s][1]) / 4)
    y = years(BASE, END)
    put("problem 10 from X5's factors as printed (" + ", ".join(f"{s} {v}" for s, v in r3.items())
        + f"): mean of all six {f(a6, 3, 4)}, of the four survivors {f(s4, 3, 4)}; gap in log growth "
        f"ln({f(s4, 4)} / {f(a6, 4)}) / {f(y, 4)} = {f(log(s4 / a6) / y, 3, 4)} a year")                    # 37


@contextmanager
def risk_free(r: float) -> Generator[None]:
    """vol5_rules with RF = r and the grid's cross-check, both restored on exit (as window())."""
    old = V.RF
    setattr(V, "RF", r)  # noqa: B010
    setattr(V, "cvx_check", cvx_check_grid)  # noqa: B010
    try:
        yield
    finally:
        setattr(V, "RF", old)  # noqa: B010
        setattr(V, "cvx_check", ORIG_CHECK)  # noqa: B010


def rf_paths(case: Case) -> None:
    """The shared decision "Risk-free rate" for the rules' paths: the through case at r_f = 0 and 2% (A34-38). Only
    R4's excess means and R8's cash and borrowing use r_f; the other six rules must move by less than 1e-15."""
    fr, rules = case.fr, V.RULES
    base = {k: num(V.summary(fr, case.paths[k]), "growth") for k in rules}
    parts = []
    for r in (0.0, 0.02):
        with risk_free(r):
            sg = V.signals(fr, [])
            g = {k: num(V.summary(fr, V.wealth_path(fr, sg, k)), "growth") for k in rules}
        assert all(abs(g[k] - base[k]) < 1e-15 for k in rules if k not in ("R4", "R8")), r
        parts.append(f"r_f {r:g}: R4 {f(g['R4'], 3, 4)}, R8 {f(g['R8'], 3, 4)} (change "
                     f"{f(g['R4'] - base['R4'], 4, plus=True)}, {f(g['R8'] - base['R8'], 4, plus=True)}), ranked "
                     + " > ".join(sorted(rules, key=lambda k: -g[k])))
    put("r_f in the paths, set for the call and restored (R4's excess means; R8's cash at r_f and borrowing at r_f + 2 "
        "points; the other six rules move by less than 1e-15): " + "; ".join(parts))                      # 38


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
    put(f"Experiment 10 (LM21, default_rng([10, 20261011])): best t-stat {f(tt[best], 2, 4)} (rule {best + 1}); t >= 3: "
        f"{int((tt >= 3 - EPS).sum())}; mean {f(float(tt.mean()), 2)}, s {f(float(tt.std(ddof=0)), 3)}; s_u of the "
        f"rules' daily returns {f(float(s_u.min()), 6)} .. {f(float(s_u.max()), 6)}")                       # 22
    p1 = float(stats.norm.sf(tt[best]))
    put(f"the best rule's one-sided normal p-value {f(p1 * 1e5, 2)}e-05; times 10,000 (Bonferroni) "
        f"{f(min(1.0, M * p1), 3)}; "
        f"(21.9) for 10,000 independent rules: Pr(max >= the best t-stat {tt[best]:.7f}) = "
        f"{f(1 - stats.norm.cdf(tt[best]) ** M, 3)}; "
        f"(21.9)'s 95% quantile of the max {f(float(stats.norm.ppf(0.95 ** (1 / M))), 2)}; one-sided Bonferroni level "
        f"for 10,000 tests at 5% {f(float(stats.norm.isf(0.05 / M)), 2)}")                                 # 23
    # LM22's rule on the series the statistic involves, the 10,000 rules' returns (the benchmark is no position)
    pw = np.array([pw_stationary((2.0 * pos[k].astype(np.float64) - 1.0) * R) for k in range(M)])
    assert round(float(pw.max())) == ELL_TR23
    g1 = rng(1)
    thr = sqrt(2 * log(log(T)))                   # Hansen (2005) p. 368 and p. 372: the consistent SPA's threshold
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
    pw_ = float((mw >= Vw - EPS).mean())
    pt = float((mt >= tt[best] - EPS).mean())
    pc = float((np.maximum(mc, 0.0) >= max(float(tt[best]), 0.0) - EPS).mean())
    pc_strict = float((np.maximum(mc, 0.0) > max(float(tt[best]), 0.0) + EPS).mean())    # Hansen's count, p. 372
    q95 = float(np.quantile(mt, 0.95, method="inverted_cdf"))
    put(f"reality check, experiment 1 (stationary bootstrap, mean block {ELL_TR23}, B = {B_RC}; LM22's rule on the "
        f"10,000 rules' squared demeaned returns: largest {f(float(pw.max()), 0, 2)} (rule {int(pw.argmax()) + 1}), "
        f"smallest {f(float(pw.min()), 2)}, TR23's own {f(pw_stationary(R), 2)}): White's statistic max of sqrt(T) x "
        f"mean = {f(Vw * 100, 4)} percent, p-value {f(pw_, 3)} (MC SE {f(sqrt(pw_ * (1 - pw_) / B_RC), 3, 4)}); the "
        f"best rule by mean is the best by t-stat: {int(np.argmax(dbar)) == best}")                         # 24
    put(f"studentized (max t-stat; each resample's mean minus the sample mean, over the sample's s_u / sqrt(T)): "
        f"p-value {f(pt, 3)} (MC SE {f(sqrt(pt * (1 - pt) / B_RC), 3, 4)}); bootstrap 95% quantile of the max "
        f"{f(q95, 2)}; t-stats above it (Romano and Wolf's first step at 5%, their footnote 22 variant) "
        f"{int((tt > q95 + EPS).sum())}; Hansen's consistent SPA ({int(keep.sum())} rules recentred, those with "
        f"t >= -sqrt(2 ln ln T) = -{f(thr, 3)}, his p. 368; the others keep their means; each rule's iid s_u as his standard deviation): "
        f"p-value {f(pc, 3)} (MC SE {f(sqrt(pc * (1 - pc) / B_RC), 3, 4)}) as a share at or above, "
        f"{f(pc_strict, 3)} by Hansen's strict count")                                                     # 25


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
        assert gap <= V.OSQP_TOL and gap < 1e-15, (label, gap)
        SKIPPED.append(f"{label} (window {V.WINDOW}; OSQP gap below 1e-15, floating-point noise, {gap:.1e} in this run)")
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


def median_ic(x: Vec | list[float]) -> float:
    """The median as every quantile of the book: x_(ceil(T/2)), inverted_cdf."""
    return float(np.quantile(np.asarray(x, dtype=np.float64), 0.5, method="inverted_cdf"))


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
    # R4 holds R3 when no fund's window mean exceeds r_f / A (vol5_rules assigns R3's array itself)
    fallback = [f"{w} {s.signal}" for w in (126, 252, 504) for s in by_w[w] if s.targets["R4"] is s.targets["R3"]]
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
    assert float((1 + X).min()) > 0
    Tg = X.shape[0]
    name = [f"{k} {'-' if w == 0 else w} {q}m" for k, w, q in conf]
    order = list(np.argsort(-np.array(growth), kind="stable"))
    put(f"grid: {n} configurations (R1, R2 x 3 frequencies; R3-R8 x windows 126, 252, 504 x frequencies 1, 3, 6 "
        f"month-end signals); {Tg} daily net returns {case.paths['R1'].dates[1]} .. {case.paths['R1'].dates[-1]}; "
        f"trades per frequency {len(sigs)}, {len(sigs[::3])}, {len(sigs[::6])} (every 12th signal, the lab's "
        f"extension: {len(sigs[::12])}, {sigs[::12][0].signal} .. {sigs[::12][-1].signal}); R4 holds R3 (no window mean above "
        f"r_f / A) at {len(fallback)} signals (window, signal: {'; '.join(fallback)}); CLARABEL cross-checks that "
        f"failed (OSQP checked instead): {len(SKIPPED)} ({'; '.join(SKIPPED)})")                          # 26
    tcase = [name.index(f"{k} {'-' if k in ('R1', 'R2') else 504} 1m") for k in rules]
    est = [i for i in order if conf[i][0] not in ("R1", "R2")]
    med = median_ic(growth)
    imed = [i for i in range(n) if growth[i] == med]
    assert len(imed) == 1
    put(f"grid net growth a year: best {name[order[0]]} {f(growth[order[0]], 3, 4)}, second {name[order[1]]} "
        f"{f(growth[order[1]], 3, 4)}, median (inverted_cdf, the {(n + 1) // 2}th of {n} from the lowest) "
        f"{name[imed[0]]} {f(med, 3, 4)}, worst {name[order[-1]]} {f(growth[order[-1]], 3, 4)}; the through case's "
        f"ranks (1 = best of {n}): "
        + ", ".join(f"{k} {order.index(i) + 1}" for k, i in zip(rules, tcase, strict=True))
        + f"; best estimated rule (R3-R8): {name[est[0]]} {f(growth[est[0]], 3, 4)}")                     # 27
    put("grid net growth by rule, min .. max over its configurations: "
        + ", ".join(f"{k} {f(min(g for c, g in zip(conf, growth, strict=True) if c[0] == k), 3, 4)} .. "
                    f"{f(max(g for c, g in zip(conf, growth, strict=True) if c[0] == k), 3, 4)}" for k in rules))  # 28
    aw = fr.A_wealth
    lg, is_, oos, ns, m, drop = cscv(X, V.RF / aw)
    sl, ic = np.polyfit(is_ * sqrt(aw), oos * sqrt(aw), 1)
    pbo = float((lg <= EPS).mean())
    neg = int((oos < 0).sum())
    put(f"CSCV: S = {BLOCKS} blocks of {m} days ({drop} earliest days dropped), C(16, 8) = {comb(16, 8)} splits (the "
        f"paper prints 12,780); PBO {f(pbo, 3)} ({int((lg <= EPS).sum())} splits); logit median {f(median_ic(lg), 2)}, "
        f"mean {f(float(lg.mean()), 2)}; the in-sample best's out-of-sample Sharpe ratio is below 0 in {neg} splits, "
        f"{f(neg / len(lg), 3, 4)} of them; annualized (x sqrt A_w): in-sample best's mean "
        f"{f(float(is_.mean()) * sqrt(aw), 2)} in sample, {f(float(oos.mean()) * sqrt(aw), 2)} out of sample; OLS of "
        f"out-of-sample on in-sample: slope {f(sl, 2)}, intercept {f(ic, 2)}")                             # 29
    cnt = np.bincount(ns, minlength=n)
    top = list(np.argsort(-cnt, kind="stable")[:3])
    put("most frequent in-sample best: " + ", ".join(f"{name[i]} {int(cnt[i])} ({f(float(cnt[i]) / len(lg), 3)})" for i in top)
        + f"; distinct in-sample bests {int((cnt > 0).sum())}")                                            # 30
    edges = np.linspace(-4.5, 4.5, 19)
    hist = np.histogram(np.clip(lg, -4.5 + 1e-9, 4.5 - 1e-9), bins=edges)[0]
    put(f"logit histogram, bins of 0.5 from -4.5 to 4.5 (ends clipped): {', '.join(str(int(h)) for h in hist)}; min "
        f"{f(float(lg.min()), 2)}, max {f(float(lg.max()), 2)}; possible values ln(j / ({n + 1} - j)), j = 1..{n}")  # 31
    bench = name.index("R1 - 1m")
    oth = [i for i in range(n) if i != bench]
    D = X[:, oth] - X[:, [bench]]
    dm, su = D.mean(axis=0), D.std(axis=0, ddof=1)
    tg = dm / (su / sqrt(Tg))
    # LM22's rule (lm22.md:254) on the series the statistic involves: the 59 differences from R1 monthly
    pwd = [pw_stationary(D[:, j]) for j in range(len(oth))]
    jpw = int(np.argmax(pwd))
    ell = float(round(pwd[jpw]))
    pw_r1 = pw_stationary(X[:, bench])
    assert round(pw_r1) == ELL_SENS

    def max_t(g: np.random.Generator, length: float) -> Vec:
        out = np.empty(B_RC)
        for b in range(B_RC):
            c = np.bincount(stationary_idx(g, Tg, length), minlength=Tg)
            out[b] = float((((c @ D) / Tg - dm) / (su / sqrt(Tg))).max())
        return out

    mx = max_t(rng(4), ell)
    mx1 = max_t(rng(5), float(ELL_SENS))          # sensitivity: R1 monthly's own estimate, rounded
    jb = int(np.argmax(tg))
    pg = float((mx >= tg[jb] - EPS).mean())
    pg1 = float((mx1 >= tg[jb] - EPS).mean())
    cg = np.corrcoef(D, rowvar=False)
    iu = np.triu_indices(len(oth), 1)
    p1 = float(stats.norm.sf(tg[jb]))
    put(f"reality check on the grid against R1 monthly (experiment 4, B = {B_RC}, mean block {ell:.0f}, LM22's rule on "
        f"the {len(oth)} differences from R1 monthly (squared demeaned): largest {f(pwd[jpw], 0, 2)} ({name[oth[jpw]]} "
        f"minus R1), smallest {f(min(pwd), 2)}): best t-stat {name[oth[jb]]} {f(tg[jb], 2, 3)}; "
        f"one-sided normal p {f(p1, 4)}, Bonferroni x {len(oth)} {f(min(1.0, len(oth) * p1), 3)}; reality-check p "
        f"{f(pg, 3)} (MC SE {f(sqrt(pg * (1 - pg) / B_RC), 3, 4)}); bootstrap 95% quantile of the max t-stat "
        f"{f(float(np.quantile(mx, 0.95, method='inverted_cdf')), 2)} against Bonferroni's "
        f"{f(float(stats.norm.isf(0.05 / len(oth))), 2)}; correlations of the {len(oth)} differences: median "
        f"{f(median_ic(cg[iu]), 2)}, min {f(float(cg[iu].min()), 2)}; sensitivity (experiment 5, mean block "
        f"{ELL_SENS}, R1 monthly's own estimate {f(pw_r1, 0, 2)} rounded): reality-check p {f(pg1, 3)} (MC SE "
        f"{f(sqrt(pg1 * (1 - pg1) / B_RC), 3, 4)}), bootstrap 95% quantile "
        f"{f(float(np.quantile(mx1, 0.95, method='inverted_cdf')), 2)}")                                    # 32
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
    se_is, se_oos = (float(np.std(v, ddof=0)) / sqrt(N_NOISE) for v in (a_is, a_oos))
    half = (Tg // BLOCKS) * BLOCKS // 2
    # (21.9)'s mean of the maximum of n standard normals: the integral of z n phi(z) Phi(z)^(n - 1)
    mean_max = float(integrate.quad(lambda z: z * n * stats.norm.pdf(z) * stats.norm.cdf(z) ** (n - 1), -10, 10)[0])
    put(f"noise (experiment 2, Model): {N_NOISE} panels of {n} iid normal strategies with mean 0, {Tg} days: PBO mean "
        f"{f(mp, 3)} (SE {f(sp, 3)}), range {f(min(pb), 2, 3)} .. {f(max(pb), 2, 3)}; the in-sample best's annualized "
        f"Sharpe ratio, mean over panels: {f(float(np.mean(a_is)), 2)} (SE {f(se_is, 3)}) in sample, "
        f"{f(float(np.mean(a_oos)), 3)} (SE {f(se_oos, 3)}) out "
        f"of sample; (21.9)'s median of the max of {n} standard normals times sqrt(A_w / {half}): "
        f"{f(float(stats.norm.ppf(0.5 ** (1 / n))) * sqrt(aw / half), 2)}, its mean "
        f"{f(mean_max * sqrt(aw / half), 2)}")                                                               # 33
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
    put(f"widget grid (experiment 3, Model; {N_STATE} panels per state, in the order printed; strategy 1 has the "
        "annual Sharpe ratio 0, 0.5, 1, 1.5, 2, the others 0): mean PBO "
        + "; ".join(f"n = {k}: " + " ".join(f(out[(k, s)][0], 2) for s in (0.0, 0.5, 1.0, 1.5, 2.0))
                    for k in (2, 5, 10, 20, 60, 100))
        + f"; largest SE {f(max(v[1] for v in out.values()), 3)}; {Tg} days, {BLOCKS} blocks")              # 34
    put(f"C(16, 8) = {comb(16, 8)}, C(10, 5) = {comb(10, 5)}, C(8, 4) = {comb(8, 4)}; every subset of 16 blocks "
        f"2^16 = {2**16}; logit ln(j / (n + 1 - j)): "
        f"n = 60, j = 30: {f(log(30 / 31), 4)}, j = 31: {f(log(31 / 30), 4)}, j = 60: {f(log(60 / 1), 3)}, j = 1: "
        f"{f(log(1 / 60), 3)}")                                                                              # 35


def same_close(case: Case) -> None:
    """Look-ahead in the through case: the first purchase stays on its trade date (so that both paths start from the
    cash of 1 at the same close and cover the same span), and each of the 91 later trades moves to its signal day's
    own close, which is known only after 13:30."""
    fr, rules = case.fr, V.RULES
    idx = {d: i for i, d in enumerate(fr.wealth_dates)}
    later = case.sigs[1:]
    assert all(bool(fr.traded[idx[s.signal]].all()) for s in later)
    early = [case.sigs[0]] + [V.Signal(s.signal, s.signal, s.targets) for s in later]
    g = {k: num(V.summary(fr, V.wealth_path(fr, early, k)), "growth") for k in rules}
    base = {k: num(V.summary(fr, case.paths[k]), "growth") for k in rules}
    gain = sum(g[k] > base[k] for k in rules)
    put(f"the {len(later)} later trades at their signal day's own close (every fund traded on each of those days), the "
        f"first purchase on {early[0].trade} as in the through case, growth from the cash of 1 at that close over the "
        f"same {f(case.ev_years, 4)} years: " + ", ".join(f"{k} {f(g[k], 3, 4)}" for k in rules)
        + "; minus the through case's: " + ", ".join(f"{k} {f(g[k] - base[k], 4, 5, plus=True)}" for k in rules)
        + f"; rules that gain {gain} of {len(rules)}")                                                       # 36


def main() -> None:
    case = through_case()
    adjusted_prices()
    R, TD = tr23()
    vol_scale(R, TD)
    kelly_walk(R, TD)
    for line in survivorship():
        put(line)
    reality_check(R)
    Tg = pbo_grid(case)
    noise(Tg, case.fr.A_wealth)
    same_close(case)
    printed_factors()
    rf_paths(case)
    for line in OUT:
        print(line)


if __name__ == "__main__":
    main()
