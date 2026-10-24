"""Batch 4's fund sample E5 and the checkpoint funds: daily total returns on TR23's calendar, checked (plans/vol-5.md).

E5 is five Taiwan-listed ETFs: 0050, 00646, 00679B, 00635U and 00642U (the through case); the checkpoint funds are 0056,
00662 and 00720B (LM35's lab). Raw files (data/raw/vol5/, registered in data/raw_manifest.json): each fund's daily
`date, open, max, min, close, spread, volume` from TaiwanStockPrice, 2016-12-01 to 2026-10-08; the distributions of 0050,
00679B, 0056 and 00720B from TaiwanStockDividendResult (each fund's own label, PITFALLS section 3); every split from
TaiwanStockSplitPrice. The calendar is TR23's (data/processed/vol3_taiex.parquet, built by data/vol3_series.py).

Checks (the script stops on the first failure, writes the failure into its report and removes its outputs):
  1. every file has its columns and no empty cell; dates unique, sorted, on TR23's calendar; every close, open, high and
     low positive, open and close within [low, high]; volume an integer >= 0; a distribution file exists exactly for
     the funds that pay (PAYERS);
  2. every close equals the previous close plus the spread, in exact decimal arithmetic, except on an ex-date and on
     a split date. On an ex-date the previous close equals the distribution's before_price, before_price minus
     after_price equals the cash within one tick (TWSE's ETF ticks: 0.01 below 50, 0.05 from 50), and FinMind prints
     the spread as 0.0. On a split date the previous close equals the split's before_price and the close minus the
     split's reference price equals the spread;
  3. every distribution and every split of a fund falls on a date with a close; the split ratio is an integer;
  4. no row (open, high, low, close, volume) repeats another date's row of the same fund, and no two funds share a row
     on the same date: a row copied from another date or series, with its spread recomputed, would pass check 2
     (PITFALLS section 3);
  5. 0050's and 00679B's closes and distributions equal the Volume I raw files (data/raw/0050__*.csv, 00679B__*.csv,
     *_dividends.csv) on every common date.
What these checks cannot see, for the six funds that have no second source: a close that is wrong but consistent with
its spreads and inside the day's range, and a cash amount wrong by less than a tick.

Two frames per sample (plans/vol-5.md, "E5's two frames"). A total return is (P_t + D_t) / (P_prev / s_t) - 1.
  - estimation frame: the dates on which every fund has a one-session return (the fund has closes on t and on the
    previous TR23 date), so a return that spans a halt drops out;
  - wealth frame: every TR23 date after the base close; a fund with no close that day earns 0 and cannot trade, and its
    return over the halt is booked on the day it trades again (P_prev is its last close).

Outputs (git-ignored), written only when every check passes: data/processed/vol5_frames.parquet (sample, frame, date,
fund, R, traded), data/processed/vol5_ohlc.parquet (the checked daily rows) and data/processed/vol5_series.txt (this
report). Other scripts read them through frames(sample) and ohlc(fund); SAMPLES names the samples.
Run:  PYTHONUTF8=1 uv run python data/vol5_series.py     (exit 0 only when every check passes)
"""
import re
import sys
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from itertools import pairwise
from pathlib import Path
from typing import NoReturn

import numpy as np
import polars as pl
from numpy.typing import NDArray

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
V5 = RAW / "vol5"
PROC = HERE / "processed"
TR23 = PROC / "vol3_taiex.parquet"
OUT_FRAMES = PROC / "vol5_frames.parquet"
OUT_OHLC = PROC / "vol5_ohlc.parquet"
REPORT = PROC / "vol5_series.txt"
WINDOW = "2016-12-01__2026-10-08"
LAST = "2026-10-08"
E5 = ["0050", "00646", "00679B", "00635U", "00642U"]
CHECKPOINT = ["0056", "00662", "00720B"]
SAMPLES = {"E5": E5, "checkpoint": CHECKPOINT, "E5+checkpoint": E5 + CHECKPOINT}
PAYERS = ["0050", "00679B", "0056", "00720B"]   # the funds with distributions; the others pay none (survey)
PRICE_COLS = ["date", "open", "max", "min", "close", "spread", "volume"]

Mat = NDArray[np.float64]
_log: list[str] = []


def fail(msg: str) -> NoReturn:
    PROC.mkdir(exist_ok=True)
    for f in (OUT_FRAMES, OUT_OHLC):
        f.unlink(missing_ok=True)
    REPORT.write_text("\n".join([*_log, f"FAILED: {msg}"]) + "\n", encoding="utf-8", newline="\n")
    sys.exit(f"vol5_series: FAILED: {msg}")


def read_text_csv(f: Path, cols: list[str], optional: tuple[str, ...] = ()) -> pl.DataFrame:
    """A raw file with exactly these columns, every cell a non-empty string (except in the optional columns)."""
    if not f.exists():
        fail(f"missing {f.relative_to(HERE)}: run data/fetch_finmind.py")
    df = pl.read_csv(f, infer_schema=False)
    if df.columns != cols:
        fail(f"{f.name}: columns {df.columns}, expected {cols}")
    need = [c for c in cols if c not in optional]
    if df.select(need).null_count().sum_horizontal()[0] or any((df[c] == "").any() for c in need):
        fail(f"{f.name}: an empty cell")
    return df.sort(cols[0])


def calendar() -> list[str]:
    if not TR23.exists():
        fail("run data/vol3_series.py first (it builds data/processed/vol3_taiex.parquet)")
    return [d.isoformat() for d in pl.read_parquet(TR23)["date"].to_list()]


def raw_rows(sym: str) -> list[tuple[str, ...]]:
    return list(read_text_csv(V5 / f"{sym}__{WINDOW}.csv", PRICE_COLS).iter_rows())


def distributions(sym: str) -> dict[str, tuple[Decimal, Decimal, Decimal]]:
    """Ex-date -> (before_price, after_price, cash per unit); empty for a fund that pays none."""
    f = V5 / f"{sym}_dividends.csv"
    if f.exists() != (sym in PAYERS):
        fail(f"{sym}: a distribution file {'exists' if f.exists() else 'is missing'}, but PAYERS says otherwise")
    if not f.exists():
        return {}
    dv = read_text_csv(f, ["date", "before_price", "after_price", "cash_dividend"])
    return {d: (Decimal(b), Decimal(a), Decimal(c)) for d, b, a, c in dv.iter_rows()}


def splits(sym: str) -> dict[str, tuple[int, Decimal, Decimal]]:
    """Split date -> (integer ratio, price before, reference price after)."""
    sp = read_text_csv(V5 / f"splits__{WINDOW}.csv", ["date", "stock_id", "type", "before_price", "after_price"],
                       optional=("type",))           # FinMind leaves 00631L's type empty (2026-03-31); not used
    out = {}
    for d, _, _, b, a in sp.filter(pl.col("stock_id") == sym).iter_rows():
        ratio = Decimal(b) / Decimal(a)
        k = int(ratio.to_integral_value())
        if abs(ratio - k) > Decimal("0.01") or k < 2:
            fail(f"{sym}: split on {d} has ratio {ratio}, not an integer")
        out[d] = (k, Decimal(b), Decimal(a))
    return out


def tick(p: Decimal) -> Decimal:
    return Decimal("0.01") if p < 50 else Decimal("0.05")


def check_fund(sym: str, cal: set[str]) -> None:
    rows = raw_rows(sym)
    dates = [r[0] for r in rows]
    if len(set(dates)) != len(dates):
        fail(f"{sym}: dates repeated")
    off = [d for d in dates if d not in cal]
    if off:
        fail(f"{sym}: {len(off)} dates off TR23's calendar, first {off[:3]}")
    for d, o, hi, lo, c, _, v in rows:
        o_, hi_, lo_, c_ = map(Decimal, (o, hi, lo, c))
        if not re.fullmatch(r"\d+", v):
            fail(f"{sym}: volume {v!r} on {d} is not an integer >= 0")
        if min(o_, hi_, lo_, c_) <= 0 or not (lo_ <= o_ <= hi_ and lo_ <= c_ <= hi_):
            fail(f"{sym}: implausible row on {d}: open {o} high {hi} low {lo} close {c}")
    div, spl = distributions(sym), splits(sym)
    have = set(dates)
    for d in [*div, *spl]:
        if d not in have:
            fail(f"{sym}: distribution or split on {d}, a date without a close")
    silent = []
    for r0, r1 in pairwise(rows):
        c0, (d, c1, sp) = Decimal(r0[4]), (r1[0], Decimal(r1[4]), Decimal(r1[5]))
        if d in spl:
            _, before, after = spl[d]
            if before != c0 or c1 - after != sp:
                fail(f"{sym}: split day {d}: previous close {c0} against {before}, or close {c1} minus {after} "
                     f"is not the spread {sp}")
        elif d in div:
            before, after, cash = div[d]
            if before != c0:
                fail(f"{sym}: ex-date {d}: previous close {c0} is not before_price {before}")
            if abs(before - after - cash) > tick(before):
                fail(f"{sym}: ex-date {d}: before {before} minus after {after} is not the cash {cash} within a tick")
            if sp != 0:
                fail(f"{sym}: ex-date {d}: spread {sp}, where FinMind prints 0.0")
            if c1 == c0:
                silent.append(d)
        elif c1 - c0 != sp:
            fail(f"{sym}: {d}: close {c1} minus previous close {c0} is not the spread {sp}")
    seen: dict[tuple, str] = {}
    for d, o, hi, lo, c, _, v in rows:
        key = (o, hi, lo, c, v)
        if key in seen:
            fail(f"{sym}: the row of {d} repeats the row of {seen[key]} (values copied from another date?)")
        seen[key] = d
    _log.append(f"{sym}: {len(rows)} rows {dates[0]} .. {dates[-1]}, {len(div)} distributions"
                + (f" (silent ex-dates, close unchanged: {', '.join(silent)})" if silent else "")
                + (f", splits {', '.join(f'{d} ({k} for 1)' for d, (k, _, _) in spl.items())}" if spl else ", no split"))


def check_across(funds: list[str]) -> None:
    by_date: dict[tuple[str, tuple], str] = {}
    for sym in funds:
        for d, o, hi, lo, c, _, v in raw_rows(sym):
            k = (d, (o, hi, lo, c, v))
            if k in by_date:
                fail(f"{sym} and {by_date[k]} have the same row on {d} (values copied from another series?)")
            by_date[k] = sym
    _log.append(f"no row repeats another date's row or another fund's row on the same date ({len(funds)} funds)")


def check_volume1() -> None:
    for sym in ("0050", "00679B"):
        old: dict[str, Decimal] = {}
        for f in sorted(RAW.glob(f"{sym}__*.csv")):
            for d, c in pl.read_csv(f, infer_schema=False).select("date", "close").iter_rows():
                old[d] = Decimal(c)
        new = {r[0]: Decimal(r[4]) for r in raw_rows(sym)}
        common = sorted(set(old) & set(new))
        bad = [d for d in common if old[d] != new[d]]
        if bad:
            fail(f"{sym}: closes differ from the Volume I files on {len(bad)} dates, first {bad[:3]}")
        vdiv = {d: Decimal(c) for d, c in pl.read_csv(RAW / f"{sym}_dividends.csv", infer_schema=False)
                .select("date", "cash_dividend").iter_rows()}
        ndiv = {d: c for d, (_, _, c) in distributions(sym).items()}
        lo, hi = max(min(old), min(new)), min(max(old), max(new))   # the price files' common span, so that a
        # distribution missing at either end of one file cannot shrink the window
        a = {d: c for d, c in vdiv.items() if lo <= d <= hi}
        b = {d: c for d, c in ndiv.items() if lo <= d <= hi}
        if a != b:
            fail(f"{sym}: distributions differ from the Volume I file between {lo} and {hi}")
        _log.append(f"{sym}: equals the Volume I raw files on all {len(common)} common dates and on the "
                    f"{len(a)} distributions from {lo} to {hi}")


@dataclass
class Frames:
    funds: list[str]
    base: str                  # the first date on which every fund has a close
    est_dates: list[str]       # estimation frame: every fund has a one-session return
    X: Mat                     # len(est_dates) x N
    wealth_dates: list[str]    # wealth frame: every TR23 date after base, through LAST
    W: Mat                     # len(wealth_dates) x N: close-to-close returns, 0 while a fund is halted
    traded: NDArray[np.bool_]  # len(wealth_dates) x N: the fund has a close that day
    years: float               # base to LAST, calendar days / 365.25
    A: float                   # len(est_dates) / years
    A_wealth: float            # len(wealth_dates) / years


def returns(sym: str, cal: list[str]) -> tuple[dict[str, float], dict[str, float]]:
    """(one-session returns, returns from the last close) keyed by date, both (P_t + D_t) / (P_prev / s_t) - 1."""
    px = {r[0]: float(r[4]) for r in raw_rows(sym)}
    div = {d: float(c) for d, (_, _, c) in distributions(sym).items()}
    spl = {d: float(k) for d, (k, _, _) in splits(sym).items()}
    one, own = {}, {}
    last = None
    for d0, d1 in pairwise(cal):
        if d0 in px:
            last = d0
        if d1 not in px or last is None:
            continue
        r = (px[d1] + div.get(d1, 0.0)) / (px[last] / spl.get(d1, 1.0)) - 1
        own[d1] = r
        if last == d0:
            one[d1] = r
    return one, own


def build_frames(funds: list[str], cal: list[str]) -> Frames:
    closes = [{r[0] for r in raw_rows(s)} for s in funds]
    base = min(set.intersection(*closes))
    tail = [d for d in cal if base < d <= LAST]
    per = [returns(s, cal) for s in funds]
    est = [d for d in tail if all(d in one for one, _ in per)]
    X = np.array([[one[d] for one, _ in per] for d in est], dtype=np.float64)
    W = np.array([[own.get(d, 0.0) for _, own in per] for d in tail], dtype=np.float64)
    traded = np.array([[d in own for _, own in per] for d in tail], dtype=np.bool_)
    years = (date.fromisoformat(LAST) - date.fromisoformat(base)).days / 365.25
    return Frames(list(funds), base, est, X, tail, W, traded, years, len(est) / years, len(tail) / years)


def frames(sample: str) -> Frames:
    """A checked sample ("E5", "checkpoint", "E5+checkpoint") from data/processed/vol5_frames.parquet."""
    if not OUT_FRAMES.exists():
        sys.exit("vol5_series: run data/vol5_series.py first (it checks the raw files and writes vol5_frames.parquet)")
    funds = SAMPLES[sample]
    df = pl.read_parquet(OUT_FRAMES).filter(pl.col("sample") == sample)
    out = []
    for fr in ("estimation", "wealth"):
        part = df.filter(pl.col("frame") == fr).pivot(on="fund", index="date", values=["R", "traded"]).sort("date")
        out.append((part["date"].to_list(),
                    np.asarray(part.select([f"R_{s}" for s in funds]).to_numpy(), dtype=np.float64),
                    np.asarray(part.select([f"traded_{s}" for s in funds]).to_numpy(), dtype=np.bool_)))
    (est, X, _), (tail, W, traded) = out
    base = df["base"][0]
    years = (date.fromisoformat(LAST) - date.fromisoformat(base)).days / 365.25
    return Frames(list(funds), base, est, X, tail, W, traded, years, len(est) / years, len(tail) / years)


def ohlc(sym: str) -> pl.DataFrame:
    """The fund's checked daily rows (date as text; open, max, min, close as floats; volume as an integer)."""
    if not OUT_OHLC.exists():
        sys.exit("vol5_series: run data/vol5_series.py first (it checks the raw files and writes vol5_ohlc.parquet)")
    return pl.read_parquet(OUT_OHLC).filter(pl.col("fund") == sym).drop("fund").sort("date")


def main() -> None:
    cal = calendar()
    _log.append(f"TR23 calendar: {len(cal)} dates {cal[0]} .. {cal[-1]}")
    for sym in E5 + CHECKPOINT:
        check_fund(sym, set(cal))
    check_across(E5 + CHECKPOINT)
    check_volume1()
    parts = []
    for name, funds in SAMPLES.items():
        f = build_frames(funds, cal)
        for fr, dts, R, tr in (("estimation", f.est_dates, f.X, np.ones_like(f.X, dtype=np.bool_)),
                               ("wealth", f.wealth_dates, f.W, f.traded)):
            for j, s in enumerate(funds):
                parts.append(pl.DataFrame({"sample": name, "frame": fr, "base": f.base, "date": dts, "fund": s,
                                           "R": R[:, j], "traded": tr[:, j]}))
        halted = [(f.funds[j], f.wealth_dates[i]) for i, j in zip(*np.nonzero(~f.traded), strict=True)]
        _log.append(f"{name} ({', '.join(funds)}): base close {f.base}; estimation frame T = {len(f.est_dates)} "
                    f"({f.est_dates[0]} .. {f.est_dates[-1]}), A = {f.A:.6f}; wealth frame {len(f.wealth_dates)} "
                    f"dates, A_w = {f.A_wealth:.6f}; years {f.years:.8f}")
        _log.append(f"  halted fund-days in the wealth frame: {len(halted)}"
                    + (f" ({', '.join(f'{s} {d}' for s, d in halted)})" if halted else ""))
        _log.append("  growth factor over the wealth frame: "
                    + ", ".join(f"{s} {g:.6f}" for s, g in zip(f.funds, np.prod(1 + f.W, axis=0), strict=True)))
        _log.append("  growth factor over the estimation frame (drops returns spanning a halt): "
                    + ", ".join(f"{s} {g:.6f}" for s, g in zip(f.funds, np.prod(1 + f.X, axis=0), strict=True)))
    PROC.mkdir(exist_ok=True)
    pl.concat(parts).write_parquet(OUT_FRAMES)
    ohlc_rows = [(s, d, float(o), float(hi), float(lo), float(c), int(v))
                 for s in E5 + CHECKPOINT for d, o, hi, lo, c, _, v in raw_rows(s)]
    pl.DataFrame(ohlc_rows, schema=["fund", "date", "open", "max", "min", "close", "volume"],
                 orient="row").write_parquet(OUT_OHLC)
    for name, funds in SAMPLES.items():          # the stored frames reproduce the computed ones exactly
        a, b = build_frames(funds, cal), frames(name)
        if (a.est_dates != b.est_dates or a.wealth_dates != b.wealth_dates or not np.array_equal(a.X, b.X)
                or not np.array_equal(a.W, b.W) or not np.array_equal(a.traded, b.traded)):
            fail(f"{name}: the stored frames differ from the computed ones")
    text = "\n".join(_log) + "\n"
    REPORT.write_text(text, encoding="utf-8", newline="\n")
    print(text, end="")


if __name__ == "__main__":
    main()
