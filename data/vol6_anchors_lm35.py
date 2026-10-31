"""LM35 anchors (Stress Testing): every number the Stage 1 brief quotes (drafted 2026-10-24, revised the same day to
the editor's decisions on the briefs, on the first revision and on the second recomputation, plans/vol-5.md; labels
repaired on 2026-10-25 after a verifier's check, no value changed; finished the same day to the decisions on the third
revision: A35-48 adds the checkpoint funds' extreme returns and 00720B's exact return of 2020-03-19, which TPEx's
no-limit rule allows, "Listing markets"). Changed on 2026-10-31 by the fresh check of the whole of Stage 1, no row
added or withdrawn: A35-02 prints the rebuild's largest difference as a bound (below 1e-13); A35-33 adds problem 8's
inputs (0050's and 00679B's means and SDs, the 3x3 correlation matrix's smallest eigenvalue from A27-11's printed
echoes, and (35.3) from the printed 4-dp inputs); A35-35 adds the tail correlation's normal-theory standard error, its
gap to (16.10) in standard errors and its Fisher-z 95% interval; A35-40 checks and bounds complementary slackness
beside the stationarity residual; A35-41 adds each frozen book's lowest value over each window's dates, stopping
unless R6's falls at the window's last close. In 2015 GLD stands in for 00635U, although that fund traded from
2015-04-15, so both hypothetical years use the same four proxies (the editor's decision on the fresh check).

Reads only data/processed/*.parquet through the shared builders, plus the registered raw files the plan names (run the
builders first: data/vol3_series.py, data/vol4_series.py, data/build_series.py, data/vol5_series.py, data/vol5_rules.py):
  * E5 (the through case): vol5_series.frames("E5"): the estimation frame (T = 2,362 joint one-session returns,
    2017-01-18 .. 2026-10-08) and the wealth frame (2,368 TR23 sessions; a halted fund earns 0 and books its spanning
    return when it trades again); vol5_series.ohlc(fund) for the daily open, high, low, close and volume. The
    checkpoint sample "E5+checkpoint" (E5 plus 0056, 00662 and 00720B).
  * The rules' books: data/processed/vol5_trades.parquet (each trade's target exposures and its cost / pre-trade
    wealth) and vol5_rules.parquet (wealth after each day's trade). This script rebuilds each rule's holdings between
    trades with the through case's recursion (drift with the wealth frame's returns, cash at RF, borrowing at
    RF + SPREAD, post-trade wealth W (1 - cost)) and stops unless the rebuilt wealth equals vol5_rules.parquet to 1e-12;
    it re-implements no rule (the targets come from the parquet). vol5_rules.signals() is called once with CAP set to
    infinity, only to echo R8's uncapped exposure ratio (LM31 owns R8's exposure path).
  * TR23 (Volume III): data/processed/vol3_taiex.parquet (columns date, tr, price, R, Rp): the scenario windows.
  * TX23 (Volume IV): data/processed/vol4_tx23.parquet: TX settlement moves on limit days; F on 2026-10-08.
  * LM2's sample: data/processed/etf_daily_returns.parquet: 0050 and 00631L total returns from 2014-11-03 (0050 in the
    2015 window; 00631L on 2025-04-07 and 2025-04-08).
  * T5S (Volume IV): data/raw/intraday/taiex5s/<year>/<date>.csv for the five named days only, used for per-day
    statistics: the log change from the previous close (printed at 09:00:00) to 09:01:00, the day's low and its time,
    the close; and, for 2025-04-07, the 09:00:05 value (the daily open).
  * US proxies (capability B5, registered in 6b02e71, retrieved 2026-10-24): data/raw/vol6/<SYM>__us_2007-07-02__
    2026-10-08.csv for SPY, TLT, GLD, USO and DBO (USStockPrice: date, adj_close, close) and data/raw/vol6/USD_TWD__
    2007-07-02__2026-10-08.csv (TaiwanExchangeRate, USD: date, spot_buy, spot_sell; FinMind's -1 rows filtered out
    at registration). The script stops if a file is absent (rebuild data/raw/ with data/fetch_finmind.py).
  * 0050 in 2008 (registered the same way): data/raw/vol6/0050__2007-07-02__2008-12-31.csv (TaiwanStockPrice: date,
    close, spread) and data/raw/vol6/0050_dividends__2007-07-02__2008-12-31.csv (TaiwanStockDividendResult, 0050's
    label 息). The script checks every close against the spread in exact arithmetic (ex-dates only excepted, with the
    previous close equal to before_price) and the dates against TR23's, and replays 2008 on 0050's own total return
    (P_t + D_t) / P_{t-1} - 1.

Conventions. Returns are simple and printed in percent unless a line says log. A scenario window runs from a peak
close to a trough close of TR23: the trough is TR23's lowest close of the named calendar year (2008, 2015, 2020) or of
the 20 sessions from the named day (2024-08-05, 2025-04-07); the peak is TR23's highest close after the previous
scenario's trough (for 2008, from TR23's first close) and before the trough. The named day of a window is its worst
TR23 day; the worst 5 and 20 sessions are the worst compound TR23 returns of m consecutive sessions ending inside the
window (peak, trough], printed from the close before the first of the m returns to the close of the last. A frozen
replay holds the book's exposures f at the window's first close fixed (LM8's (8.4) with the compound returns R_sc
over the window): loss = f'R_sc, interest on cash and on borrowing left out. A named-day replay uses the exposures at
the previous close (no rule trades on a named day). The rules' actual path is their wealth ratio over the window
(their own trades included). A proxy's TWD value for US session D is the adjusted close of D (as retrieved on
2026-10-24) times the mid rate (spot_buy + spot_sell) / 2 of the first FX row dated after D; a Taiwan date d takes
the last US session before d, so its return compounds the US sessions D with d_prev <= D < d and the FX change
(plans/vol-5.md, capability B5). 0050 is itself in every hypothetical book: its own 2007-2008 files in 2008, LM2's
sample in 2015, the wealth frame in the 2020 proxy check. Weekly returns compound daily returns within ISO weeks,
keys (ISO year, ISO week); the first and last week of a span, in which it starts and ends, are dropped, complete or
not (LM27's convention; plans/vol-5.md, "Weeks and months"). Mahalanobis distances use the full estimation frame's
mean and covariance (divisor T); the reverse stress test minimizes d^2 = (x - mu)' S^-1 (x - mu) subject to
f'x = -l (closed form) and, bounded, with 0050's shock >= -10% (cvxpy: CLARABEL and OSQP in percent units, which the
shared decision "Solver output" allows with the KKT residuals printed; tolerances printed; the stationarity
residual with CLARABEL's multipliers, complementary slackness and the closed form with the active bound checked). The
objective is given as cp.quad_form(x - mu, cp.psd_wrap(S^-1)): the solvers' statuses and an inactive multiplier
depend on the form (given as cp.sum_squares of a Cholesky factor of S^-1 times x - mu, CLARABEL's inactive multiplier
for R8 is about 6e-12, and OSQP's status for R2 can fall to optimal_inaccurate: in about half of 40 last-bit
perturbations of S in two verifiers' checks, 2026-10-25 and 2026-10-31, against none of 40 with quad_form), so the
brief states it.
Betas are OLS slopes with an intercept on the estimation frame (TR23's R on the same dates). The ruin leverage of a
loss R < 0 is -1/R (1 + L R <= 0). Counts on two-decimal prices use Fraction; counts on computed values the guard
1e-12.

Rounding flags. Every number the brief prints passes through f(x, k1, k2, ...), which shows x with max(k) + 3 decimals
and flags it "NEAR" for each printed precision k at which x lies within a tenth of a last-digit unit of a rounding
boundary (|frac(10^k |x|) - 0.5| < 0.1). The brief prints a flagged value as rounded from the unrounded value here
(the flags stay in the anchors table; decision C11). A number computed from an adjusted close (the US proxies) is
printed to 1 dp and flagged "CENT" when a change of one cent in each adjusted close it uses could move its 1-dp
rounding (PITFALLS section 3: a re-fetch re-rounds the column); the brief prints such a number to 0 dp, or as "about"
when the flag says 0 dp is not safe either, so a CENT value is checked for NEAR at 0 dp only. Solver residuals, gaps
and an inactive constraint's multiplier print as bounds (the script stops if a residual or gap is exceeded), because
their digits are rounding noise.

Prints one line per anchor, "A35-NN <value>", in ID order, and writes nothing.

Run:  PYTHONUTF8=1 uv run python data/vol6_anchors_lm35.py
"""
import sys
from bisect import bisect_left, bisect_right
from datetime import date
from fractions import Fraction
from math import floor, inf, log, sqrt
from pathlib import Path
from statistics import NormalDist

import cvxpy as cp
import numpy as np
import polars as pl
from numpy.typing import NDArray

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import vol5_rules as vr
from vol5_rules import RF, RULES, SPREAD, cov0, schedule
from vol5_series import frames, ohlc

PROC = HERE / "processed"
T5S = HERE / "raw" / "intraday" / "taiex5s"
V6 = HERE / "raw" / "vol6"
PROXY_WINDOW = "2007-07-02__2026-10-08"
PROXIES = {"00646": "SPY", "00679B": "TLT", "00635U": "GLD", "00642U": "USO"}
EPS = 1e-12
LOSS = 0.10                      # the reverse stress test's one-day loss
TX_MARGIN = (701_000, 538_000)   # TAIFEX initial and maintenance margin per TX contract, effective 2026-08-12
                                 # (lm02.md:462, LM2's dated official table; cited, not re-read here)
Vec = NDArray[np.float64]
Mat = NDArray[np.float64]

OUT: list[str] = []
NEAR: list[str] = []
CENT: list[str] = []


def put(value: str) -> None:
    """One anchor line; values that f() found near a rounding boundary, and proxy values that a cent per adjusted
    close could move at 1 dp, are listed at its end."""
    tail = f" [NEAR a rounding boundary: {'; '.join(NEAR)}]" if NEAR else ""
    tail += f" [CENT, print 0 dp: {'; '.join(CENT)}]" if CENT else ""
    OUT.append(f"A35-{len(OUT) + 1:02d} {value}{tail}")
    NEAR.clear()
    CENT.clear()


def f(x: float, *ks: int, plus: bool = False, dec: int | None = None) -> str:
    """x with max(ks) + 3 decimals (or dec); flagged for each printed precision k within 0.1 of a last-digit unit of a
    boundary."""
    x = float(x)
    for k in ks:
        u = abs(x) * 10**k
        if abs(u - floor(u) - 0.5) < 0.1:
            NEAR.append(f"{x:.{k + 3}f} at {k} dp")
    return f"{x:{'+' if plus else ''}.{max(ks) + 3 if dec is None else dec}f}"


def pc(x: float, *ks: int, dec: int | None = None) -> str:
    """A return in percent, signed, through f()."""
    return f(100 * float(x), *ks, plus=True, dec=dec)


def pu(x: float, u: float) -> str:
    """A proxy-based return in percent to 1 dp (via pc); CENT when x +- u (u: the one-cent bound, decimal) straddles a
    1-dp rounding boundary."""
    lo, hi = 100 * (x - u), 100 * (x + u)
    if floor(10 * lo + 0.5) != floor(10 * hi + 0.5):
        ok0 = floor(lo + 0.5) == floor(hi + 0.5)
        CENT.append(f"{100 * x:.4f} +- {100 * u:.4f}" + ("" if ok0 else " (0 dp too: write 'about')"))
        return pc(x, 0, dec=4)                   # printed at 0 dp: flag that precision only
    return pc(x, 1)


def lu(x: float, u: float) -> str:
    """The ruin leverage -1/x of a proxy-based loss x < 0 to 1 dp; CENT when -1/(x +- u) straddles a 1-dp boundary."""
    a, b = -1 / (x - u), -1 / (x + u)
    if floor(10 * a + 0.5) != floor(10 * b + 0.5):
        ok0 = floor(a + 0.5) == floor(b + 0.5)
        CENT.append(f"L {-1 / x:.4f} in [{a:.4f}, {b:.4f}]" + ("" if ok0 else " (0 dp too: write 'about')"))
        return f(-1 / x, 0, dec=4)               # printed at 0 dp: flag that precision only
    return f(-1 / x, 1)


def fail(msg: str) -> None:
    sys.exit(f"vol6_anchors_lm35: FAILED: {msg}")


# ---------------------------------------------------------------- data
fr = frames("E5")
FUNDS = fr.funds
WD = fr.wealth_dates
WIDX = {d: i for i, d in enumerate(WD)}
tr = pl.read_parquet(PROC / "vol3_taiex.parquet").sort("date")
TD = [x.isoformat() for x in tr["date"].to_list()]
TPOS = {d: i for i, d in enumerate(TD)}
LV = np.asarray(tr["tr"].to_numpy(), dtype=np.float64)
PRICE = np.asarray(tr["price"].to_numpy(), dtype=np.float64)
RT = np.asarray(tr["R"].fill_null(np.nan).to_numpy(), dtype=np.float64)
TRADES = pl.read_parquet(PROC / "vol5_trades.parquet")
RULEW = pl.read_parquet(PROC / "vol5_rules.parquet")


PRE: dict[str, dict[str, Vec]] = {}     # rule -> trade date -> drifted exposures before that trade


def book(rule: str) -> tuple[list[str], Mat, Vec]:
    """The rule's exposures h/W after each day's trade and its wealth, from its first trade (rebuilt, then checked)."""
    t = TRADES.filter(pl.col("rule") == rule).sort("trade")
    tgt = {r["trade"]: (np.array([r[s] for s in FUNDS], dtype=np.float64), float(r["cost"]))
           for r in t.iter_rows(named=True)}
    i0 = WIDX[t["trade"][0]]
    h = np.zeros(len(FUNDS))
    c = 1.0
    dts: list[str] = []
    ex: list[Vec] = []
    ws: list[float] = []
    PRE[rule] = {}
    for i in range(i0, len(WD)):
        if i > i0:
            h = h * (1 + fr.W[i])
            c *= 1 + ((RF if c >= 0 else RF + SPREAD) / fr.A_wealth)
        w = float(h.sum() + c)
        if WD[i] in tgt:
            PRE[rule][WD[i]] = h / w
            tf, cost = tgt[WD[i]]
            w = w * (1 - cost)
            h = w * tf
            c = w * (1 - float(tf.sum()))
        dts.append(WD[i])
        ex.append(h / w)
        ws.append(w)
    ref = RULEW.filter(pl.col("rule") == rule).sort("date")
    if ref["date"].to_list() != dts:
        fail(f"{rule}: rebuilt dates differ from vol5_rules.parquet")
    err = float(np.max(np.abs(np.array(ws) / np.asarray(ref["wealth"].to_numpy(), dtype=np.float64) - 1)))
    if err > EPS:
        fail(f"{rule}: rebuilt wealth differs from vol5_rules.parquet by {err:.1e}")
    BOOKERR[rule] = err
    return dts, np.array(ex), np.array(ws)


BOOKERR: dict[str, float] = {}
BOOKS = {k: book(k) for k in RULES}


def expo(rule: str, d: str) -> Vec:
    dts, ex, _ = BOOKS[rule]
    return ex[dts.index(d)]


def wealth(rule: str, d: str) -> float:
    dts, _, ws = BOOKS[rule]
    return float(ws[dts.index(d)])


def growth(a: str, b: str) -> Vec:
    """Each fund's compound wealth-frame return over (a, b]."""
    return np.prod(1 + fr.W[WIDX[a] + 1:WIDX[b] + 1], axis=0) - 1


def weeks(dates: list[str], x: Mat) -> tuple[int, Mat]:
    """Compound daily returns (rows of x) within ISO weeks, keys (ISO year, ISO week); the first and last week of the
    span, in which it starts and ends, are dropped, complete or not (LM27's convention). Returns the count and the
    rows."""
    keys = [date.fromisoformat(d).isocalendar()[:2] for d in dates]
    uk = sorted(set(keys))
    acc = {k: np.ones(x.shape[1]) for k in uk}
    for k, r in zip(keys, x, strict=True):
        acc[k] = acc[k] * (1 + r)
    kept = uk[1:-1]
    return len(kept), np.array([acc[k] - 1 for k in kept])


def rules_line(vals: dict[str, float], k: int = 2) -> str:
    return ", ".join(f"{r} {pc(v, k)}" for r, v in vals.items())


def funds_line(names: list[str], vals: Vec, k: int = 2) -> str:
    return ", ".join(f"{s} {pc(float(v), k)}" for s, v in zip(names, vals, strict=True))


# ---------------------------------------------------------------- samples
put(f"E5: estimation frame T = {len(fr.est_dates)} ({fr.est_dates[0]} .. {fr.est_dates[-1]}), A = {f(fr.A, 2)}; "
    f"wealth frame {len(WD)} sessions, A_w = {f(fr.A_wealth, 2)}; years {f(fr.years, 4)}")
first = TRADES.filter(pl.col("rule") == "R1").sort("trade")
if max(BOOKERR.values()) >= 1e-13:              # printed as a bound: its digits are rounding noise
    fail(f"rebuilt wealth differs from vol5_rules.parquet by {max(BOOKERR.values()):.1e}, not below 1e-13")
put(f"rules' books: {first.height} trades, first {first['trade'][0]} (signal {first['signal'][0]}), last "
    f"{first['trade'][-1]}; valuation to {WD[-1]}; rebuilt wealth against vol5_rules.parquet, largest relative "
    "difference over the eight rules below 1e-13")
put(f"TR23: {int(np.isfinite(RT).sum())} returns {TD[1]} .. {TD[-1]} (published, lm19.md:46)")

# ---------------------------------------------------------------- scenario windows (TR23)
SCEN = [("2008", "year"), ("2015", "year"), ("2020", "year"), ("2024-08-05", "day"), ("2025-04-07", "day")]
WIN: dict[str, tuple[str, str, str]] = {}      # name -> (peak, trough, named day)
WORST: dict[str, dict[int, tuple[float, int]]] = {}   # name -> m -> (worst m-session return, index of its last close)
prev = -1
for name, kind in SCEN:
    if kind == "year":
        idx = [i for i, d in enumerate(TD) if d[:4] == name]
        k = idx[0] + int(np.argmin(LV[idx[0]:idx[-1] + 1]))
    else:
        i = TPOS[name]
        k = i + int(np.argmin(LV[i:i + 20]))
    p = prev + 1 + int(np.argmax(LV[prev + 1:k + 1]))
    nd = p + 1 + int(np.argmin(RT[p + 1:k + 1]))
    worst = {}
    for m in (5, 20):
        g = [(LV[j] / LV[j - m] - 1, j) for j in range(p + 1, k + 1)]
        worst[m] = min(g)
    rank = int((RT[np.isfinite(RT)] < RT[nd] - EPS).sum()) + 1
    WIN[name] = (TD[p], TD[k], TD[nd])
    WORST[name] = worst
    gap = (date.fromisoformat(TD[nd]) - date.fromisoformat(TD[nd - 1])).days
    put(f"scenario {name}: peak {TD[p]}, trough {TD[k]}, {k - p} sessions, TR23 {pc(LV[k] / LV[p] - 1, 2)}; worst day "
        f"{TD[nd]} {pc(RT[nd], 2)} (rank {rank} of 5849; previous session {TD[nd - 1]}, {gap} calendar days); worst 5 "
        f"sessions from the close of {TD[worst[5][1] - 5]} to {TD[worst[5][1]]} {pc(worst[5][0], 2)}; worst 20 sessions "
        f"from the close of {TD[worst[20][1] - 20]} to {TD[worst[20][1]]} {pc(worst[20][0], 2)}")
    prev = k
k25, k24 = TPOS["2025-04-09"], TPOS["2024-08-05"]
put(f"running-peak drawdown (LM1's DD_t) at the troughs: 2024-08-05 {pc(1 - LV[k24] / LV[:k24 + 1].max(), 2)} and "
    f"2025-04-09 {pc(1 - LV[k25] / LV[:k25 + 1].max(), 2)}, both from {TD[int(np.argmax(LV[:k25 + 1]))]} "
    f"({k25 - int(np.argmax(LV[:k25 + 1]))} sessions to 2025-04-09)")
gaps = np.array([(date.fromisoformat(TD[i]) - date.fromisoformat(TD[i - 1])).days for i in range(1, len(TD))])
r1 = RT[1:]
long = gaps >= 4
worst10 = np.argsort(r1)[:10]
put(f"returns spanning 4 or more calendar days: {int(long.sum())} of {len(r1)} ({pc(long.mean(), 1)}); mean |R| "
    f"{f(100 * np.abs(r1[long]).mean(), 2)}% against {f(100 * np.abs(r1[~long]).mean(), 2)}%; among the 10 worst days: "
    + ", ".join(f"{TD[i + 1]} ({gaps[i]} days)" for i in worst10 if gaps[i] >= 4))

# ---------------------------------------------------------------- the case: 2025-04-07
i7 = WIDX["2025-04-07"]
put(f"2025-04-07 (from the 2025-04-02 close): {funds_line(FUNDS, fr.W[i7])}; TR23 {pc(RT[TPOS['2025-04-07']], 2)}")
o50 = ohlc("0050")
row = {d: (o, h, lo, c, v) for d, o, h, lo, c, v in o50.select("date", "open", "max", "min", "close", "volume").iter_rows()}


def fx2(x: float) -> Fraction:
    return Fraction(f"{x:.2f}")


o, h, lo, c, v = row["2025-04-07"]
c0, o8 = row["2025-04-02"][3], row["2025-04-08"][0]
exact = fx2(c) / fx2(c0) - 1
put(f"0050 on 2025-04-07: open {o} high {h} low {lo} close {c}, volume {v:,} shares; previous close {c0}; return "
    f"{exact} exactly (Fraction); next open (2025-04-08) {o8}: {pc(o8 / c - 1, 2)} from the locked close, "
    f"{pc(o8 / c0 - 1, 2)} from 2025-04-02")
day7 = {k: float(expo(k, "2025-04-02") @ fr.W[i7]) for k in RULES}
net7 = {k: wealth(k, "2025-04-07") / wealth(k, "2025-04-02") - 1 for k in RULES}   # no trade on 2025-04-07
full7 = max(abs(net7[k] - day7[k]) for k in RULES if k != "R8")
if full7 > EPS:
    fail(f"a fully invested rule's wealth ratio on 2025-04-07 differs from f'R by {full7:.1e}")
put(f"rules' one-day scenario loss on 2025-04-07, exposures at the 2025-04-02 close: {rules_line(day7)}; R8's total "
    f"exposure {f(expo('R8', '2025-04-02').sum(), 3)}; against the wealth ratio of that session: R1-R7 (no cash) equal "
    f"below 1e-12, R8 {pc(net7['R8'], 2)} (one session's interest on its borrowing included), "
    f"{f(100 * (day7['R8'] - net7['R8']), 3)} points below f'R")
parts = []
for k in ("R1", "R3", "R6", "R8"):
    e = expo(k, "2025-04-02")
    kk = (2, 3) if k == "R6" else (2,)           # R6's parts print to 3 dp (their 2-dp roundings miss the total)
    parts.append(f"{k}: " + ", ".join(f"{s} {pc(e[j] * fr.W[i7, j], *kk)}" for j, s in enumerate(FUNDS)))
put("attribution f_i R_i on 2025-04-07 (points): " + "; ".join(parts))

# ---------------------------------------------------------------- replays on the rules' holdings
for name in ("2020", "2024-08-05", "2025-04-07"):
    a, b, nd = WIN[name]
    g = growth(a, b)
    frozen = {k: float(expo(k, a) @ g) for k in RULES}
    put(f"{name} window {a} -> {b}, frozen at {a}: funds {funds_line(FUNDS, g)}; rules {rules_line(frozen)}; "
        f"R8's exposure {f(expo('R8', a).sum(), 3)}")
    ind = WIDX[nd]
    eve = WD[ind - 1]
    named = {k: float(expo(k, eve) @ fr.W[ind]) for k in RULES}
    put(f"{name} named day {nd} (exposures at {eve}): funds {funds_line(FUNDS, fr.W[ind])}; rules {rules_line(named)}; "
        f"R8's exposure {f(expo('R8', eve).sum(), 3)}")
act = []
for name in ("2020", "2024-08-05", "2025-04-07"):
    a, b, _ = WIN[name]
    act.append(f"{name}: " + rules_line({k: wealth(k, b) / wealth(k, a) - 1 for k in RULES}))
put("rules' actual paths over the windows (their own trades and costs included, Descriptive): " + "; ".join(act))

# ---------------------------------------------------------------- 0050 against TR23 (the 2008 stand-in)
ci = [TPOS[d] for d in fr.est_dates]
rt_est = RT[ci]
etf = pl.read_parquet(PROC / "etf_daily_returns.parquet").sort("date")
ed = etf["date"].to_list()
r0050 = np.asarray(etf["R_0050"].to_numpy(), dtype=np.float64)
r631 = np.asarray(etf["R_00631L"].to_numpy(), dtype=np.float64)
EPOS = {d: i for i, d in enumerate(ed)}
in15 = [d for d in TD if "2015-04-27" < d <= "2015-08-24"]
if any(d not in EPOS for d in in15):
    fail("etf_daily_returns.parquet misses a TR23 date of the 2015 window")
g0050_15 = float(np.prod(1 + r0050[[EPOS[d] for d in in15]]) - 1)
win_cmp = []
for name in ("2020", "2024-08-05", "2025-04-07"):
    a, b, _ = WIN[name]
    win_cmp.append(f"{name} 0050 {pc(growth(a, b)[0], 2)} TR23 {pc(LV[TPOS[b]] / LV[TPOS[a]] - 1, 2)}")
put(f"0050 against TR23: daily correlation on the estimation frame {f(np.corrcoef(fr.X[:, 0], rt_est)[0, 1], 3)}; "
    f"annual log-growth gap (0050 minus TR23) {pc((np.log1p(fr.X[:, 0]).sum() - np.log1p(rt_est).sum()) / fr.years, 2)}; "
    f"windows: 2015 0050 {pc(g0050_15, 2)} (LM2's sample, {len(in15)} returns) TR23 "
    f"{pc(LV[TPOS['2015-08-24']] / LV[TPOS['2015-04-27']] - 1, 2)}; " + "; ".join(win_cmp))

# ---------------------------------------------------------------- the rules' first weights (the 2008 and 2015 books)
FIRST = {k: np.array([TRADES.filter(pl.col("rule") == k).sort("trade").row(0, named=True)[s] for s in FUNDS],
                     dtype=np.float64) for k in RULES}
put("rules' first target exposures (trade 2019-03-04; owners LM27-LM31, echoed as replay inputs): "
    + "; ".join(f"{k} " + "/".join(f(x, 3) for x in FIRST[k]) for k in RULES)
    + f" (order {'/'.join(FUNDS)}; R8 sums to {f(FIRST['R8'].sum(), 3)})")

# ---------------------------------------------------------------- proxies (registered, retrieved 2026-10-24)
need = [V6 / f"{s}__us_{PROXY_WINDOW}.csv" for s in ("SPY", "TLT", "GLD", "USO", "DBO")]
need += [V6 / f"USD_TWD__{PROXY_WINDOW}.csv", V6 / "0050__2007-07-02__2008-12-31.csv",
         V6 / "0050_dividends__2007-07-02__2008-12-31.csv"]
if missing := [p.name for p in need if not p.exists()]:
    fail(f"{', '.join(missing)} absent from {V6}: rebuild data/raw/ with data/fetch_finmind.py")
fx = pl.read_csv(V6 / f"USD_TWD__{PROXY_WINDOW}.csv", infer_schema=False)
fxd = fx["date"].to_list()
fxm = (np.asarray(fx["spot_buy"].cast(pl.Float64).to_numpy(), dtype=np.float64)
       + np.asarray(fx["spot_sell"].cast(pl.Float64).to_numpy(), dtype=np.float64)) / 2
if fxm.min() <= 0:
    fail("USD_TWD: a non-positive rate (FinMind's -1 sentinel?)")
PV: dict[str, Vec] = {}
ADJ: dict[str, Vec] = {}
usd: list[str] = []
for s in ("SPY", "TLT", "GLD", "USO", "DBO"):
    df = pl.read_csv(V6 / f"{s}__us_{PROXY_WINDOW}.csv", infer_schema=False)
    if usd and df["date"].to_list() != usd:
        fail(f"{s}: US sessions differ from SPY's")
    usd = df["date"].to_list()
    ADJ[s] = np.asarray(df["adj_close"].cast(pl.Float64).to_numpy(), dtype=np.float64)
USRATE = np.array([fxm[j] if (j := bisect_right(fxd, d)) < len(fxd) else np.nan for d in usd])
for s, adj in ADJ.items():
    PV[s] = adj * USRATE
LASTD = np.array([bisect_left(usd, d) - 1 for d in TD], dtype=np.int64)
first_tw = TPOS["2007-07-03"]
ns = [int(LASTD[i] - LASTD[i - 1]) for i in range(first_tw, len(TD))]
late = [TD[i] for i in range(first_tw, len(TD))
        if (j := bisect_right(fxd, usd[LASTD[i]])) < len(fxd) and fxd[j] > TD[i]]
put(f"proxy data: {len(usd)} US sessions {usd[0]} .. {usd[-1]}; {len(fxd)} FX rows; TR23 dates "
    f"{TD[first_tw]} .. {TD[-1]} ({len(ns)}) with 0 / 1 / 2 / 3+ US sessions: {ns.count(0)} / {ns.count(1)} / "
    f"{ns.count(2)} / {sum(1 for x in ns if x >= 3)}; dates whose FX row comes after the date: {late}")


def prox(s: str, a: str, b: str) -> float:
    return float(PV[s][LASTD[TPOS[b]]] / PV[s][LASTD[TPOS[a]]] - 1)


def cent(s: str, a: str, b: str) -> float:
    """How far a change of one cent in each of the two adjusted closes can move the proxy return (to first order;
    PITFALLS section 3: a re-fetch re-rounds the column, so print proxy numbers only to digits a cent cannot move)."""
    if LASTD[TPOS[a]] == LASTD[TPOS[b]]:
        return 0.0                               # the same US close at both ends: exactly 0 whatever its rounding
    pa, pb = ADJ[s][LASTD[TPOS[a]]], ADJ[s][LASTD[TPOS[b]]]
    return (1 + prox(s, a, b)) * 0.01 * (1 / pa + 1 / pb)


def cents(pairs: list[tuple[str, str, str]]) -> str:
    return f"largest one-cent effect {f(100 * max(cent(s, a, b) for s, a, b in pairs), 3)} points"


def book_u(e: Vec, us: list[float]) -> float:
    """The one-cent bound of f'R_sc: 0050's own return (index 0) is exact."""
    return float(sum(abs(float(e[j])) * us[j] for j in range(1, len(e))))


rows = []
for fund, s in [*PROXIES.items(), ("00642U", "DBO")]:
    j = FUNDS.index(fund)
    rp = np.array([PV[s][LASTD[i]] / PV[s][LASTD[i - 1]] - 1 for i in ci])
    nwk, wkr = weeks(fr.est_dates, np.column_stack([rp, fr.X[:, j]]))
    gapy = (np.log1p(fr.X[:, j]).sum() - np.log1p(rp).sum()) / fr.years
    rows.append(f"{fund}~{s} daily {f(np.corrcoef(rp, fr.X[:, j])[0, 1], 3)} weekly "
                f"{f(np.corrcoef(wkr[:, 0], wkr[:, 1])[0, 1], 3)} gap {pc(gapy, 2)}")
put(f"proxies against the funds on the estimation frame (correlation daily and over {nwk} ISO weeks, the first and "
    "last dropped; annual log-growth gap, fund minus proxy): " + "; ".join(rows))

out = []
for name in ("2020", "2024-08-05", "2025-04-07"):
    a, b, _ = WIN[name]
    g = growth(a, b)
    out.append(f"{name}: " + ", ".join(f"{fund} {pc(g[FUNDS.index(fund)], 2)} / {s} "
                                      f"{pu(prox(s, a, b), cent(s, a, b))}"
                                      for fund, s in [*PROXIES.items(), ("00642U", "DBO")]))
a, b, _ = WIN["2020"]
gfund = growth(a, b)
for oil in ("USO", "DBO"):
    gp = np.array([gfund[0], prox("SPY", a, b), prox("TLT", a, b), prox("GLD", a, b), prox(oil, a, b)])
    us = [0.0, cent("SPY", a, b), cent("TLT", a, b), cent("GLD", a, b), cent(oil, a, b)]
    out.append(f"2020 rules on 0050 itself and the proxies ({oil}) against the funds: "
               + ", ".join(f"{k} {pu(float(expo(k, a) @ gp), book_u(expo(k, a), us))} / "
                           f"{pc(float(expo(k, a) @ gfund), 2)}" for k in RULES))
pairs = [(s, *WIN[n][:2]) for n in ("2020", "2024-08-05", "2025-04-07") for s in ("SPY", "TLT", "GLD", "USO", "DBO")]
put("windows, fund / proxy (TWD): " + "; ".join(out) + "; " + cents(pairs))

px = pl.read_csv(V6 / "0050__2007-07-02__2008-12-31.csv", infer_schema=False)
dv = pl.read_csv(V6 / "0050_dividends__2007-07-02__2008-12-31.csv", infer_schema=False)
divs = {d: (Fraction(bp), Fraction(cd)) for d, bp, _, cd in dv.iter_rows()}
ds = px["date"].to_list()
cl = [Fraction(x) for x in px["close"].to_list()]
spr = [Fraction(x) for x in px["spread"].to_list()]
if ds != [d for d in TD if "2007-07-02" <= d <= "2008-12-31"]:
    fail("0050 2007-2008: its dates differ from TR23's")
R50: dict[str, float] = {}       # 0050's own total return, 2007-07-03 .. 2008-12-31
for i in range(1, len(ds)):
    dvd = divs.get(ds[i])
    if dvd is None and cl[i] - cl[i - 1] != spr[i]:
        fail(f"0050 {ds[i]}: close against spread")
    if dvd is not None and (spr[i] != 0 or dvd[0] != cl[i - 1]):
        fail(f"0050 {ds[i]}: ex-date row is not as TaiwanStockDividendResult says")
    R50[ds[i]] = float((cl[i] + (dvd[1] if dvd else 0)) / cl[i - 1] - 1)
PROXY_RET: dict[str, dict[str, Vec]] = {}
PROXY_U: dict[str, dict[str, list[float]]] = {}
SYMS = ("SPY", "TLT", "GLD")
for name in ("2008", "2015"):
    a, b, nd = WIN[name]
    pd_ = TD[TPOS[nd] - 1]
    if name == "2015":
        stand, stand_d, lab = g0050_15, float(r0050[EPOS[nd]]), "0050 itself (LM2's sample)"
    else:
        stand = float(np.prod([1 + R50[d] for d in TD if a < d <= b]) - 1)
        stand_d, lab = R50[nd], f"0050 itself (its 2007-2008 files; TR23 {pc(LV[TPOS[b]] / LV[TPOS[a]] - 1, 2)})"
    fxa, fxb = float(USRATE[LASTD[TPOS[a]]]), float(USRATE[LASTD[TPOS[b]]])
    res: dict[str, Vec] = {}
    uu: dict[str, list[float]] = {}
    for oil in ("USO", "DBO"):
        res[oil] = np.array([stand, *(prox(s, a, b) for s in SYMS), prox(oil, a, b)])
        uu[oil] = [0.0, *(cent(s, a, b) for s in SYMS), cent(oil, a, b)]
    PROXY_RET[name], PROXY_U[name] = res, uu
    put(f"{name} window {a} -> {b} (hypothetical): 0050 {pc(stand, 2)} ({lab}), "
        + ", ".join(f"{s} {pu(prox(s, a, b), cent(s, a, b))}" for s in (*SYMS, "USO", "DBO"))
        + f" (TWD); USD/TWD {f(fxa, 3)} -> {f(fxb, 3)} ({pc(fxb / fxa - 1, 2)}); rules at their first weights, oil "
        "USO / DBO: "
        + ", ".join(f"{k} {pu(float(FIRST[k] @ res['USO']), book_u(FIRST[k], uu['USO']))} / "
                    f"{pu(float(FIRST[k] @ res['DBO']), book_u(FIRST[k], uu['DBO']))}" for k in RULES)
        + "; " + cents([(s, a, b) for s in (*SYMS, "USO", "DBO")]))
    dayv = {oil: np.array([stand_d, *(prox(s, pd_, nd) for s in SYMS), prox(oil, pd_, nd)]) for oil in ("USO", "DBO")}
    ud = [0.0, *(cent(s, pd_, nd) for s in SYMS), cent("USO", pd_, nd)]
    nus = int(LASTD[TPOS[nd]] - LASTD[TPOS[pd_]])
    put(f"{name} named day {nd} (hypothetical; {nus} US sessions since {pd_}): 0050 {pc(stand_d, 2)}, "
        + ", ".join(f"{s} {pu(prox(s, pd_, nd), cent(s, pd_, nd))}" for s in (*SYMS, "USO", "DBO"))
        + "; rules at first weights (USO): "
        + ", ".join(f"{k} {pu(float(FIRST[k] @ dayv['USO']), book_u(FIRST[k], ud))}" for k in RULES)
        + "; " + cents([(s, pd_, nd) for s in (*SYMS, "USO", "DBO")]))

# ---------------------------------------------------------------- hypothetical shocks
X = fr.X
MU = X.mean(axis=0)
S = cov0(X)
SI = np.linalg.inv(S)
LAST = WD[-1]
CUR = {k: expo(k, LAST) for k in RULES}


def ols(y: Vec, x: Vec) -> tuple[float, float]:
    xc, yc = x - x.mean(), y - y.mean()
    b = float(xc @ yc / (xc @ xc))
    e = yc - b * xc
    return b, 1 - float(e @ e) / float(yc @ yc)


beta = np.array([ols(X[:, j], rt_est)[0] for j in range(len(FUNDS))])
r2 = np.array([ols(X[:, j], rt_est)[1] for j in range(len(FUNDS))])
put("betas on TR23 (estimation frame, OLS with intercept; R-squared): "
    + ", ".join(f"{s} {f(b, 3)} ({f(q, 3)})" for s, b, q in zip(FUNDS, beta, r2, strict=True))
    + f"; factor shock TR23 -10%: rules' current books ({LAST}) "
    + rules_line({k: float(CUR[k] @ (beta * -0.10)) for k in RULES}))
pred = beta * RT[TPOS["2025-04-07"]]
put(f"factor model on 2025-04-07 (beta x TR23's {pc(RT[TPOS['2025-04-07']], 2)}): predicted {funds_line(FUNDS, pred)}; "
    f"actual {funds_line(FUNDS, fr.W[i7])}; R1 predicted {pc(float(expo('R1', '2025-04-02') @ pred), 2)} against "
    f"{pc(day7['R1'], 2)}, R8 {pc(float(expo('R8', '2025-04-02') @ pred), 2)} against {pc(day7['R8'], 2)}")
def cond_shock(Sg: Mat, m: Vec, x0: float) -> Vec:
    """E[R | R_0050 = x0] fund by fund, (16.8): mu_j + beta_j (x0 - mu_0), beta_j = S_j0 / S_00."""
    return m + Sg[:, 0] / Sg[0, 0] * (x0 - m[0])


RHO_BRK = 0.30                                  # constructed: 0050 and 00679B correlated +0.30, the rest unchanged
sd = np.sqrt(np.diag(S))
Cb = S / np.outer(sd, sd)
Cb[0, 2] = Cb[2, 0] = RHO_BRK
Sb = Cb * np.outer(sd, sd)
lam_min = float(np.linalg.eigvalsh(Cb).min())
full, brk = cond_shock(S, MU, -0.10), cond_shock(Sb, MU, -0.10)
# Problem 8: the 3x3 correlation matrix of 0050/00679B/00642U from A27-11's printed echoes (decision C12: -0.105 and
# 0.092 at 3 dp, -0.18 at 2 dp), checked against the unrounded correlations; (35.3) from the printed 4-dp inputs.
ECHO3 = {(0, 2): (-0.105, 3), (0, 4): (0.092, 3), (2, 4): (-0.18, 2)}
for (i_, j_), (v_, k_) in ECHO3.items():
    if round(float(S[i_, j_] / sd[i_] / sd[j_]), k_) != v_:
        fail(f"problem 8: the correlation of {FUNDS[i_]} and {FUNDS[j_]} does not round to A27-11's {v_}")
C3 = np.eye(3)
C3[0, 1] = C3[1, 0] = -0.105
C3[0, 2] = C3[2, 0] = 0.092
C3[1, 2] = C3[2, 1] = -0.18
lam3 = float(np.linalg.eigvalsh(C3).min())
C3[0, 1] = C3[1, 0] = RHO_BRK
lam3b = float(np.linalg.eigvalsh(C3).min())
m4 = [round(100 * float(MU[j_]), 4) for j_ in (0, 2)]
s4 = [round(100 * float(sd[j_]), 4) for j_ in (0, 2)]
p8 = [m4[1] + rho_ * s4[1] / s4[0] * (-10.0 - m4[0]) for rho_ in (-0.105, RHO_BRK)]
if [round(x, 2) for x in p8] != [round(100 * float(full[2]), 2), round(100 * float(brk[2]), 2)]:
    fail("problem 8: the printed 4-dp inputs do not reproduce E7's 00679B moves at 2 dp")
put(f"correlation break, 0050 -10% (partial scenario, the rest at their conditional means): full-sample correlation "
    f"0050/00679B {f(S[0, 2] / sd[0] / sd[2], 3)} (LM27 owns it), constructed {f(RHO_BRK, 2)} "
    f"(smallest eigenvalue of the changed correlation matrix {f(lam_min, 3)}); shocks full {funds_line(FUNDS, full)}; "
    f"constructed {funds_line(FUNDS, brk)}; rules' current books full / constructed: "
    + ", ".join(f"{k} {pc(float(CUR[k] @ full), 2)} / {pc(float(CUR[k] @ brk), 2)}" for k in RULES)
    + f"; problem 8: means (percent, estimation frame) 0050 {f(100 * MU[0], 4)} 00679B {f(100 * MU[2], 4)}, SDs "
    f"(divisor T) {f(100 * sd[0], 4)} {f(100 * sd[2], 4)}; 3x3 correlation matrix of 0050/00679B/00642U from A27-11's "
    f"printed echoes (-0.105, 0.092, -0.18): smallest eigenvalue {f(lam3, 3)}, with -0.105 set to 0.30 {f(lam3b, 3)}; "
    f"(35.3) from the 4-dp inputs, 00679B {f(p8[0], 2, plus=True)} / {f(p8[1], 2, plus=True)}")
i22 = [i for i, d in enumerate(TD) if d[:4] == "2022"]
k22 = i22[0] + int(np.argmin(LV[i22[0]:i22[-1] + 1]))
a20 = TPOS[WIN["2020"][1]]
p22 = a20 + 1 + int(np.argmax(LV[a20 + 1:k22 + 1]))
a, b = TD[p22], TD[k22]
g22 = growth(a, b)
ep = np.array([a < d <= b for d in fr.est_dates])


nwf, wf = weeks(fr.est_dates, X)
nwe, we = weeks([d for d, m in zip(fr.est_dates, ep, strict=True) if m], X[ep])
put(f"2022 (an illustration, not a ROADMAP scenario): TR23 peak {a}, trough {b}, {k22 - p22} sessions, "
    f"{pc(LV[k22] / LV[p22] - 1, 2)}; funds {funds_line(FUNDS, g22)}; 0050/00679B correlation daily "
    f"{f(np.corrcoef(X[ep, 0], X[ep, 2])[0, 1], 3)} and over the window's {nwe} ISO weeks "
    f"(its first and last dropped) {f(np.corrcoef(we[:, 0], we[:, 2])[0, 1], 3)} (full sample, {nwf} ISO weeks: "
    f"{f(np.corrcoef(wf[:, 0], wf[:, 2])[0, 1], 3)}, LM27's A27-11); rules frozen at {a}: "
    + rules_line({k: float(expo(k, a) @ g22) for k in RULES}))
s0 = X[:, 0].std(ddof=0)                      # divisor T, as the book's s
ev = X[:, 0] <= MU[0] - 2 * s0 + EPS
vs = X[ev, 0].var(ddof=0)                     # divisor n, the number of tail days (48), as T for the full sample
out = []
model646 = r646 = 0.0
for j in (1, 2):
    rho = float(np.corrcoef(X[:, 0], X[:, j])[0, 1])
    model = rho / sqrt(rho**2 + (1 - rho**2) * s0**2 / vs)
    rt_ = float(np.corrcoef(X[ev, 0], X[ev, j])[0, 1])
    if j == 1:
        model646, r646 = model, rt_
    out.append(f"{FUNDS[j]}: data {f(rt_, 3)}, (16.10) {f(model, 3)}, full {f(rho, 3)}")
nev = int(ev.sum())
se646 = (1 - r646**2) / sqrt(nev)                # normal-theory standard error of a correlation on n days
zq = NormalDist().inv_cdf(0.975)
fz = (np.tanh(np.arctanh(r646) - zq / sqrt(nev - 3)), np.tanh(np.arctanh(r646) + zq / sqrt(nev - 3)))
put(f"(16.10) on the days 0050 fell 2 standard deviations or more below its mean ({nev} days; variance "
    f"ratio full / tail {f(s0**2 / vs, 3)}, both with divisor the count (T = {len(X)}, {nev}), so 0050's "
    f"variance on the tail days is {f(vs / s0**2, 3)} times the full sample's): " + "; ".join(out)
    + f"; 00646's tail correlation: normal-theory standard error (1 - r^2)/sqrt({nev}) {f(se646, 2)}, gap to (16.10) "
    f"{f(model646 - r646, 2)} = {f((model646 - r646) / se646, 1)} standard errors; Fisher-z 95% interval "
    f"{fz[0]:.4f} .. {fz[1]:.4f}")


def maha(x: Vec) -> float:
    z = x - MU
    return sqrt(float(z @ SI @ z))


wi = [int(np.argmin(fr.W[:, j])) for j in range(len(FUNDS))]
woe = np.array([fr.W[wi[j], j] for j in range(len(FUNDS))])
dt = np.sqrt(np.einsum("ij,jk,ik->i", X - MU, SI, X - MU))
order = np.argsort(-dt)
r7 = int(np.where(np.array(fr.est_dates)[order] == "2025-04-07")[0][0]) + 1
put("worst of each fund on one day (constructed): " + ", ".join(f"{s} {pc(woe[j], 2)} ({WD[wi[j]]})" for j, s in
                                                             enumerate(FUNDS))
    + f"; Mahalanobis distance {f(maha(woe), 2)}; rules' current books " + rules_line({k: float(CUR[k] @ woe) for k in RULES}))
put(f"historical Mahalanobis distances (estimation frame): largest {f(dt[order[0]], 2, 3)} on {fr.est_dates[order[0]]}, "
    f"then {f(dt[order[1]], 2, 3)} ({fr.est_dates[order[1]]}), {f(dt[order[2]], 2, 3)} ({fr.est_dates[order[2]]}); "
    f"2025-04-07 {f(dt[fr.est_dates.index('2025-04-07')], 2, 3)}, rank {r7} of {len(dt)}; median "
    f"{f(np.quantile(dt, 0.5, method='inverted_cdf'), 2)}; returns on {fr.est_dates[order[0]]}: "
    f"{funds_line(FUNDS, X[order[0]])}; on {fr.est_dates[order[1]]}: {funds_line(FUNDS, X[order[1]])}")

# ---------------------------------------------------------------- reverse stress test
put(f"current books ({LAST} close; owners LM27-LM31, echoed as inputs): "
    + "; ".join(f"{k} " + "/".join(f(x, 3) for x in CUR[k]) for k in RULES))
lines = []
XSTAR: dict[str, Vec] = {}
kmax, k7 = float(dt.max()), float(dt[fr.est_dates.index("2025-04-07")])   # unrounded bounds k (printed to 3 dp)
for k in RULES:
    e = CUR[k]
    sp = sqrt(float(e @ S @ e))
    mp = float(e @ MU)
    dstar = (LOSS + mp) / sp
    XSTAR[k] = MU - (LOSS + mp) * (S @ e) / sp**2
    lines.append(f"{k} mean f'R {f(100 * mp, 3)}% sigma_p {f(100 * sp, 3, 4)}% d* {f(dstar, 2)}, worst loss "
                 f"within d <= k_max {f(100 * (kmax * sp - mp), 2)}% and within d <= k_0407 "
                 f"{f(100 * (k7 * sp - mp), 2)}%")
put(f"reverse stress, one-day loss {f(100 * LOSS, 0)}%, full-sample mean and covariance; bounds k at the unrounded "
    f"distances k_max = {f(kmax, 3)} (the sample's largest) and k_0407 = {f(k7, 3)} (2025-04-07's): " + "; ".join(lines)
    + "; shock x* R1 " + funds_line(FUNDS, XSTAR["R1"]) + "; R8 " + funds_line(FUNDS, XSTAR["R8"]))

S100, MU100 = 1e4 * S, 100 * MU
SI100 = np.linalg.inv(S100)
SI100 = (SI100 + SI100.T) / 2


def bounded(e: Vec) -> tuple[Vec, float, str]:
    """min d^2 s.t. e'x <= -10 (percent), x_0050 >= -10, by CLARABEL and OSQP with the objective
    quad_form(x - mu, psd_wrap(S^-1)) (the form the brief states); stationarity (below 1e-13), complementary slackness
    (below 1e-9, both with CLARABEL's multipliers) and the closed form checked."""
    sols = []
    duals = None
    for solver, opts in ((cp.CLARABEL, vr.CLARABEL_OPTS), (cp.OSQP, vr.OSQP_OPTS)):
        x = cp.Variable(len(e))
        cons = [e @ x <= -100 * LOSS, x[0] >= -10.0]
        prob = cp.Problem(cp.Minimize(cp.quad_form(x - MU100, cp.psd_wrap(SI100))), cons)
        prob.solve(solver=solver, **opts)
        if prob.status != "optimal":
            fail(f"bounded reverse stress: {solver} status {prob.status}")
        v = x.value
        assert v is not None
        sols.append(np.asarray(v, dtype=np.float64))
        if solver == cp.CLARABEL:
            d0, d1 = cons[0].dual_value, cons[1].dual_value
            assert d0 is not None and d1 is not None
            duals = (float(np.asarray(d0)), float(np.asarray(d1)))
    xs = sols[0]
    assert duals is not None
    grad = 2 * SI100 @ (xs - MU100) + duals[0] * e - duals[1] * np.eye(len(e))[0]
    active = xs[0] < -10 + 1e-6
    if active:                                       # closed form with both constraints as equalities
        K = np.vstack([e, np.eye(len(e))[0]])
        bvec = np.array([-100 * LOSS, -10.0])
        cf = MU100 + S100 @ K.T @ np.linalg.solve(K @ S100 @ K.T, bvec - K @ MU100)
    else:
        cf = MU100 - (100 * LOSS + e @ MU100) * (S100 @ e) / float(e @ S100 @ e)
    gap_cf = float(np.abs(xs - cf).max())
    gap_osqp = float(np.abs(xs - sols[1]).max())
    kkt = float(np.abs(grad).max())                  # stationarity, with CLARABEL's multipliers
    cs = max(abs(duals[0] * float(e @ xs + 100 * LOSS)), abs(duals[1] * float(xs[0] + 10.0)))   # complementary slackness
    if gap_cf > 1e-9 or gap_osqp > 1e-9 or kkt > 1e-13 or cs > 1e-9:   # printed as bounds: their digits are noise
        fail(f"bounded reverse stress: closed form gap {gap_cf:.1e}, OSQP gap {gap_osqp:.1e}, stationarity residual "
             f"{kkt:.1e}, complementary slackness {cs:.1e}")
    mult = [("below 1e-12" if abs(d) < 1e-12 else f(d, 1 if abs(d) >= 1 else 4))   # an inactive one is solver noise
            for d in duals]
    return xs / 100, sqrt(float((xs - MU100) @ SI100 @ (xs - MU100))), (
        f"bound {'active' if active else 'inactive'}, multipliers {mult[0]} and {mult[1]}, stationarity residual "
        f"below 1e-13, complementary slackness below 1e-9, closed-form and OSQP gaps below 1e-9")


lines = []
for k in ("R1", "R2", "R8"):
    xb, db, note = bounded(CUR[k])
    lines.append(f"{k}: d {f(db, 2)}, shock {funds_line(FUNDS, xb)} ({note})")
put("reverse stress with 0050's limit (shock >= -10%; objective quad_form(x - mean, psd_wrap(inverse covariance)), "
    "percent units; CLARABEL tol 1e-12, OSQP eps 1e-10 polished): "
    + "; ".join(lines))

# ---------------------------------------------------------------- leverage, limits and ruin
ruin = []
for name in ("2020", "2024-08-05", "2025-04-07"):
    a, b, nd = WIN[name]
    eve = WD[WIDX[nd] - 1]
    lw = float(expo("R6", a) @ growth(a, b))
    ld = float(expo("R6", eve) @ fr.W[WIDX[nd]])
    ruin.append(f"{name}: window {pc(lw, 2, 3)} -> L {f(-1 / lw, 2, 3)}; named day {pc(ld, 2, 3)} -> L "
                + (f"{f(-1 / ld, 2, 3)}" if ld < 0 else "none (a gain)"))
for name in ("2008", "2015"):
    lw = float(FIRST["R6"] @ PROXY_RET[name]["USO"])
    lwd = float(FIRST["R6"] @ PROXY_RET[name]["DBO"])
    uw = book_u(FIRST["R6"], PROXY_U[name]["USO"])
    uwd = book_u(FIRST["R6"], PROXY_U[name]["DBO"])
    ruin.append(f"{name} (hypothetical, first weights, USO / DBO): {pu(lw, uw)} / {pu(lwd, uwd)} -> L "
                f"{lu(lw, uw)} / {lu(lwd, uwd)}")
lows = []                                       # (35.2) over a window: the frozen book's lowest value on its dates
for name in ("2020", "2024-08-05", "2025-04-07"):
    a, b, _ = WIN[name]
    path = np.cumprod(1 + fr.W[WIDX[a] + 1:WIDX[b] + 1], axis=0) - 1
    for k in RULES:
        v = path @ expo(k, a)
        j = int(np.argmin(v))
        if v[j] < v[-1] - EPS:
            if k == "R6":
                fail(f"R6's frozen {name} book reaches its lowest value before the window's last close")
            lows.append(f"{name} {k} {pc(float(v[j]), 2)} ({WD[WIDX[a] + 1 + j]}; last close {pc(float(v[-1]), 2)})")
put("R6's unit book: scenario loss and ruin leverage -1/R (frozen holdings): " + "; ".join(ruin)
    + "; each frozen book's lowest value over each window's dates (2020, 2024-08-05, 2025-04-07; eight rules): at the "
    "window's last close (A35-15, A35-17, A35-19) " + (f"except {', '.join(lows)}" if lows else "for every book"))
vars(vr)["CAP"] = inf                       # R8 uncapped, to echo its ratio (module global read by signals)
sigs = vr.signals(fr, [])
vars(vr)["CAP"] = 1.5
ratio = np.array([s.targets["R8"].sum() for s in sigs])
stored = np.asarray(TRADES.filter(pl.col("rule") == "R8").sort("trade")["exposure"].to_numpy(), dtype=np.float64)
if float(np.abs(np.minimum(1.5, ratio) - stored).max()) > 1e-12:
    fail("R8's uncapped ratio, capped at 1.5, does not reproduce the stored exposures")
r8t = TRADES.filter(pl.col("rule") == "R8").sort("trade")
r8tr, r8sg = r8t["trade"].to_list(), r8t["signal"].to_list()
into = []
for n in ("2020", "2024-08-05", "2025-04-07"):
    a, b, _ = WIN[n]
    g = growth(a, b)
    js = [max(i for i, d in enumerate(r8tr) if d <= a)] + [i for i, d in enumerate(r8tr) if a < d <= b]
    cells = []
    for i in js:
        d = r8tr[i]
        cells.append(f"trade {d} (signal {r8sg[i]}) exposure {f(PRE['R8'][d].sum(), 3)} -> {f(expo('R8', d).sum(), 3)} "
                     f"(uncapped ratio {f(ratio[i], 3)}), that book over the whole window {pc(float(expo('R8', d) @ g), 2)}")
    into.append(f"{n} ({a} -> {b}; frozen at {a}, exposure {f(expo('R8', a).sum(), 3)}: "
                f"{pc(float(expo('R8', a) @ g), 2)}; actual {pc(wealth('R8', b) / wealth('R8', a) - 1, 2)}): "
                + "; ".join(cells))
put(f"R8's uncapped exposure ratio (LM31 owns the path, A31-29; echoed): {len(ratio)} signals, range "
    f"{f(ratio.min(), 3)} .. {f(ratio.max(), 2, 3)} (max at signal {sigs[int(np.argmax(ratio))].signal}), {int((ratio >= 1.5 - EPS).sum())} at or "
    f"above the cap 1.5; R8's trades into each window (the last trade on or before its first close, then every trade "
    f"inside it; drifted exposure before -> target after; each post-trade book frozen over the whole window, (35.1)): "
    + " | ".join(into))
xo = o8 / c0 - 1
put(f"limit lock: a book of 0050 at leverage L loses 10.000% L at the 2025-04-07 close and {f(-100 * xo, 3)}% L at the "
    f"next open; ruin leverage {f(10.0, 2)} at the close, {f(-1 / xo, 2)} at the next open; 00631L (LM2's sample) "
    f"{pc(r631[EPOS['2025-04-07']], 3)} on 2025-04-07 and {pc(r631[EPOS['2025-04-08']], 2)} on 2025-04-08, 0050 "
    f"{pc(r0050[EPOS['2025-04-08']], 2)} (lm02.md:498)")
tx = pl.read_parquet(PROC / "vol4_tx23.parquet").sort("date").with_columns(
    (pl.col("rF").exp() - 1).alias("RF"), (pl.col("rS").exp() - 1).alias("RS"), pl.col("date").cast(pl.Utf8))
lim = tx.filter((pl.col("date") >= "2015-06-01") & (pl.col("RF").abs() >= 0.0995))
vol8 = tx.filter(pl.col("date") == "2025-04-08")["volume"][0]
F26 = float(tx.filter(pl.col("date") == LAST)["F"][0])
notional = 200 * F26
lev = notional / TX_MARGIN[0]
put("TX settlement moves of 9.95% or more since 2015-06-01 (TX23): "
    + "; ".join(f"{d} TX {pc(a, 3)}, TAIEX price {pc(b, 2)}, volume {v:,}" for d, a, b, v in
                lim.select("date", "RF", "RS", "volume").iter_rows())
    + f"; 2025-04-08 volume {vol8:,}; TX at {LAST}: F = {F26:,.0f} (lm23.md:327), notional NT$ {notional:,.0f}; with the "
    f"initial margin {TX_MARGIN[0]:,} as equity f = {f(lev, 2)}, a 10% limit day loses {f(lev * 0.10, 3)} times equity "
    f"(equity {notional * -0.10 + TX_MARGIN[0]:,.0f}); maintenance {TX_MARGIN[1]:,} is reached after a fall of "
    f"{f(100 * (TX_MARGIN[0] - TX_MARGIN[1]) / notional, 3)}% (lm02.md:462)")
gl = []
for name in ("2008", "2015", "2020", "2024-08-05", "2025-04-07"):
    nd = WIN[name][2]
    t5 = pl.read_csv(T5S / nd[:4] / f"{nd}.csv")
    tt = [x[11:] for x in t5["date"].to_list()]
    vv = np.asarray(t5["TAIEX"].to_numpy(), dtype=np.float64)
    p0 = vv[tt.index("09:00:00")]
    if abs(p0 - PRICE[TPOS[nd] - 1]) > 0.005:
        fail(f"T5S {nd}: 09:00:00 is not the previous close")
    after = np.array([x > "09:00:00" for x in tt])
    kl = int(np.argmin(np.where(after, vv, np.inf)))
    ties = [tt[i] for i in range(len(tt)) if after[i] and vv[i] == vv[kl] and i != kl]
    gap = log(vv[tt.index("09:01:00")] / p0)
    cl = log(PRICE[TPOS[nd]] / p0)
    stale = f", 09:00:05 (the daily open) {f(100 * log(vv[tt.index('09:00:05')] / p0), 2)}%" if nd == "2025-04-07" else ""
    tie = f" (first; the same value at {len(ties)} later times, the last {ties[-1]})" if ties else ""
    gl.append(f"{nd}: gap {f(100 * gap, 2)}%, low {f(100 * log(vv[kl] / p0), 2)}% at {tt[kl]}{tie}, close "
              f"{f(100 * cl, 2)}%, gap / close {f(gap / cl, 2)}{stale}")
put("T5S per-day statistics, log changes from the previous close (09:00:00) to 09:01:00, to the day's low, to the "
    "close: " + "; ".join(gl))
lk = []
for j, s in enumerate(FUNDS):
    w = fr.W[:, j]
    lk.append(f"{s} min {pc(w.min(), 2)} max {pc(w.max(), 2)}, |R| > 10%: {int((np.abs(w) > 0.10 + EPS).sum())}")
locked = [d for d, o_, h_, l_, c_, _ in o50.select("date", "open", "max", "min", "close", "volume").iter_rows()
          if o_ == h_ == l_ == c_ and d > "2016-12-01" and d in WIDX and abs(fr.W[WIDX[d], 0]) >= 0.099]
put("price limits in the wealth frame: " + "; ".join(lk) + f"; 0050 days with open = high = low = close and |R| >= 9.9%: "
    f"{locked}")

# ---------------------------------------------------------------- the checkpoint universe
fc = frames("E5+checkpoint")
sch = schedule(fc)
put(f"checkpoint sample {'/'.join(fc.funds)}: base {fc.base}; estimation T = {len(fc.est_dates)} ({fc.est_dates[0]} .. "
    f"{fc.est_dates[-1]}), A = {f(fc.A, 2)}; wealth frame {len(fc.wealth_dates)}, A_w = {f(fc.A_wealth, 2)}; "
    f"{len(sch)} month-end signals with {vr.WINDOW} rows, first {sch[0][0]} (trade {sch[0][1]}), last {sch[-1][0]} "
    f"(trade {sch[-1][1]})")
cw = {d: i for i, d in enumerate(fc.wealth_dates)}
lines = []
for name in ("2020", "2024-08-05", "2025-04-07"):
    a, b, nd = WIN[name]
    g = np.prod(1 + fc.W[cw[a] + 1:cw[b] + 1], axis=0) - 1
    lines.append(f"{name} window " + ", ".join(f"{s} {pc(g[j], 2)}" for j, s in enumerate(fc.funds) if j >= 5)
                 + " ; named day " + ", ".join(f"{s} {pc(fc.W[cw[nd], j], 2)}" for j, s in enumerate(fc.funds) if j >= 5))
o56 = ohlc("0056").filter(pl.col("date") == "2025-04-07").row(0)
ext = []
for j, s in enumerate(fc.funds):
    if j >= 5:                                   # the checkpoint's own funds (E5's are A35-46)
        w = fc.W[:, j]
        ext.append(f"{s} min {pc(w.min(), 2)} ({fc.wealth_dates[int(np.argmin(w))]}) max {pc(w.max(), 2)} "
                   f"({fc.wealth_dates[int(np.argmax(w))]}), |R| > 10%: {int((np.abs(w) > 0.10 + EPS).sum())}")
c720 = dict(ohlc("00720B").select("date", "close").iter_rows())
d720 = sorted(c720)
p720 = d720[d720.index("2020-03-19") - 1]
if p720 != fc.wealth_dates[cw["2020-03-19"] - 1]:
    fail("00720B: the close before 2020-03-19 is not the wealth frame's previous session")
x720 = fx2(c720["2020-03-19"]) / fx2(c720[p720]) - 1
if abs(float(x720) - fc.W[cw["2020-03-19"], fc.funds.index("00720B")]) > EPS:
    fail("00720B on 2020-03-19: the wealth-frame return is not the price change (a distribution that day?)")
put("checkpoint funds in the scenarios: " + "; ".join(lines) + f"; 0056 on 2025-04-07: open {o56[1]} high {o56[2]} low "
    f"{o56[3]} close {o56[4]}; extremes in the checkpoint wealth frame ({fc.wealth_dates[0]} .. {fc.wealth_dates[-1]}): "
    + "; ".join(ext) + f"; 00720B on 2020-03-19: close {c720['2020-03-19']} from {c720[p720]} ({p720}), return {x720} "
    "exactly (Fraction), equal to its wealth-frame return (no distribution that day)")

# ---------------------------------------------------------------- the widget's initial state
w7 = fr.W[i7]
put("widget initial state (current books under the 2025-04-07 shock vector, Mahalanobis distance "
    f"{f(maha(w7), 2)}): " + ", ".join(f"{k} {pc(float(CUR[k] @ w7), 2)} (ruin L {f(-1 / float(CUR[k] @ w7), 2)})"
                                        for k in RULES))

# ---------------------------------------------------------------- problems (hypothetical inputs)
p1 = 0.6 * -0.10 + 0.4 * 0.0181
put(f"P1 exposures 0.6 / 0.4 to 0050 / 00679B, scenario -10% / +1.81%: {pc(p1, 2)}; distractors: the two returns added "
    f"{pc(-0.10 + 0.0181, 2)}, the equity line alone {pc(0.6 * -0.10, 2)}")
put(f"P2 scenario loss -8%: ruin leverage {f(1 / 0.08, 2)}; distractors {f(8.0, 2)} (the loss in percent read as a "
    f"multiple) and {f((1 - 0.08) / 0.08, 2)} ((1 - 0.08) / 0.08)")
p3 = 5 * (151.2 / 176.0 - 1)
put(f"P3 L = 5 on 0050, locked at 158.40 from 176.00, next open 151.20: loss at the next open {pc(p3, 2)}; at the close "
    f"{pc(5 * -0.10, 2)}; from the locked close only {pc(5 * (151.2 / 158.4 - 1), 2)}")
p4 = 1.01 * 0.96 * (32.48 / 32.00) - 1
put(f"P4 US fund +1.0% then -4.0%, USD/TWD 32.00 -> 32.48: TWD return {pc(p4, 2)}; USD only {pc(1.01 * 0.96 - 1, 2)}; FX "
    f"applied the wrong way (x 32.00 / 32.48) {pc(1.01 * 0.96 * (32.00 / 32.48) - 1, 2)}")
put(f"P5 sigma_p 0.8% a day, mean 0, one-day loss 10%: d* {f(10 / 0.8, 2)}; d*^2 {f((10 / 0.8) ** 2, 2)}; sqrt "
    f"{f(sqrt(10 / 0.8), 2)}")
b_n, b_b = -0.07, 0.30
p6n, p6b = 0.4 * -0.10 + 0.6 * b_n * -0.10, 0.4 * -0.10 + 0.6 * b_b * -0.10
put(f"P6 40% 0050 / 60% bond fund, 0050 -10%, bond beta -0.07 (normal) or +0.30 (break): bond {pc(b_n * -0.10, 2)} / "
    f"{pc(b_b * -0.10, 2)}; book {pc(p6n, 2)} / {pc(p6b, 2)}; difference {f(100 * (p6n - p6b), 2)} points")
S2 = np.array([[0.012**2, -0.1 * 0.012 * 0.008], [-0.1 * 0.012 * 0.008, 0.008**2]])
e2 = np.array([0.5, 0.5])
sp2 = sqrt(float(e2 @ S2 @ e2))
xs2 = -0.05 * (S2 @ e2) / sp2**2
put(f"P7 two funds, sd 1.2% and 0.8%, correlation -0.1, f = (0.5, 0.5), mean 0, loss 5%: sigma_p {f(100 * sp2, 4)}%, "
    f"d* {f(0.05 / sp2, 3)}, x* {pc(xs2[0], 2)} / {pc(xs2[1], 2)} (beta_ip {f((S2 @ e2)[0] / sp2**2, 3)} / "
    f"{f((S2 @ e2)[1] / sp2**2, 3)})")

# ---------------------------------------------------------------- the proxy rule's blind spot
nus_e = np.array([int(LASTD[TPOS[d]] - LASTD[TPOS[d] - 1]) for d in fr.est_dates])
z, one = nus_e == 0, nus_e == 1
put(f"proxy rule's blind spot, E5 estimation frame: {int(z.sum())} dates with no new US session (every proxy, FX "
    f"included, returns exactly 0 there), {int(one.sum())} with one, {int((nus_e >= 2).sum())} with two or more; "
    "mean |R| of the foreign funds on dates with none / one: "
    + ", ".join(f"{s} {f(100 * np.abs(X[z, j]).mean(), 2)}% / {f(100 * np.abs(X[one, j]).mean(), 2)}%"
                for j, s in enumerate(FUNDS) if j >= 1))

# ---------------------------------------------------------------- the case's multi-day figure (AUTHORING section 8)
mr = []
for m in (5, 20):
    gm = LV[m:] / LV[:-m] - 1                        # every span of m consecutive TR23 returns, overlapping
    cells = []
    for name in ("2020", "2025-04-07"):
        x, jl = WORST[name][m]
        worse = [TD[i + m] for i in np.nonzero(gm < x - EPS)[0]]
        cells.append(f"{name}'s worst ({TD[jl - m]} -> {TD[jl]}, {pc(x, 2)}) rank {len(worse) + 1}"
                     + (f" (worse spans end {', '.join(worse)})" if worse else ""))
    mr.append(f"{m} sessions ({len(gm)} spans): " + "; ".join(cells))
put("multi-day ranks among all overlapping TR23 spans of m sessions, 2003-01-03 .. 2026-10-08 (1 = worst): "
    + " | ".join(mr))

print("\n".join(OUT))
