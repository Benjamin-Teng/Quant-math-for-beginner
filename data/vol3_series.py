"""Volume III's main sample TR23: the TAIEX total-return index, checked against the TAIEX price index on every date.

TaiwanStockTotalReturnIndex has no spread column, so data/check_chunk.py cannot test it, and a row copied from another
date (project/PITFALLS.md section 3) would pass the manifest's checksum. The price index is an independent series on
the same calendar, so this script tests each total-return row against it:
  1. the two series have the same dates (5,850 from 2003-01-02), sorted, without duplicates or empty values;
  2. every price close agrees with its spread to the cent (Decimal), except the 52 dates on which TAIEX's spread prints
     0.0, each of which must equal its official 13:30:00 value in raw/taiex_close/ (data/vol2_series.py does the same);
  3. on each date the total return minus the price return (the day's dividend yield) lies in [GAP_LO, GAP_HI]. A wrong
     total-return level moves the gaps on both sides of its date in opposite directions, so a copied, stale or
     misdated row on a day without dividends leaves the range on one side; on an ex-dividend day a level can still be
     off by up to that day's yield. The first and last levels have one side only, so their gaps must be rounding
     (|gap| <= -GAP_LO): neither date is an ex-dividend day;
  4. no total-return level repeats the day before's, and no daily move of either index exceeds MAX_MOVE (the limit was
     7% before 2015-06-01 and 10% from then on).
It stops on the first failed check. The price index comes from the raw chunks, not from vol2_closes.parquet, so the
sample does not depend on Volume II's paid 13:30:00 sector data.

Outputs (git-ignored): data/processed/vol3_taiex.parquet (date, tr, price, R, Rp: the closes and the simple daily
returns of the total-return and price indices, null on the first date) and data/processed/vol3_series.txt (this report).

Run:  PYTHONUTF8=1 uv run python data/vol3_series.py     (exit 0 only when every check passes)
"""
import itertools
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import NoReturn

import polars as pl

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
PROC = HERE / "processed"
TR_FILE = RAW / "vol3" / "TAIEX_TR__2003-01-01__2026-10-08.csv"
PRICE_FILES = [RAW / "vol3" / "TAIEX__2003-01-01__2007-07-01.csv", *sorted((RAW / "sectors").glob("TAIEX__*.csv"))]
TAIEX_CLOSE = RAW / "taiex_close"

GAP_LO = -0.05e-4            # total minus price return, per day: rounding of two-decimal levels stays above -0.05 bp
GAP_HI = 0.01                # and no day's dividends add 1% to TAIEX (the sample's largest is 84 bp, on 2016-06-27)
MAX_MOVE = 0.105             # the 10% limit plus rounding; a larger daily move is a data error
N_ZERO_SPREAD = 52           # TAIEX dates whose spread prints 0.0 (data/README.md "sectors/")

LINES: list[str] = []

def out(s: str = "") -> None:
    print(s)
    LINES.append(s)

def report() -> None:
    PROC.mkdir(exist_ok=True)
    (PROC / "vol3_series.txt").write_text("\n".join(LINES) + "\n", encoding="utf-8", newline="\n")

def stop(msg: str) -> NoReturn:
    out(f"STOP: {msg}")
    report()
    sys.exit(1)

def read_csv(f: Path, cols: list[str]) -> pl.DataFrame:
    """A raw file as text columns; STOP if it is missing, has other columns, has no rows or has empty values."""
    if not f.exists():
        stop(f"missing {f.relative_to(HERE)}: run uv run python data/fetch_finmind.py")
    df = pl.read_csv(f, infer_schema=False) if f.stat().st_size else pl.DataFrame()
    if df.columns != cols or df.height == 0:
        stop(f"{f.relative_to(HERE)} has columns {df.columns} and {df.height} rows: run fetch_finmind.py --verify")
    if df.select(cols).null_count().sum_horizontal()[0]:
        stop(f"{f.relative_to(HERE)} has empty values")
    return df.select(cols)

def read_price() -> pl.DataFrame:
    rows: dict[str, tuple[str, str]] = {}
    for f in PRICE_FILES:
        for d, c, s in read_csv(f, ["date", "close", "spread"]).iter_rows():
            if d in rows and rows[d] != (c, s):
                stop(f"chunks disagree on {d}: {rows[d]} vs {(c, s)}")
            rows[d] = (c, s)
    dates = sorted(rows)
    try:
        [Decimal(x) for c_s in rows.values() for x in c_s]
    except InvalidOperation:
        stop("a TAIEX close or spread is not a number: run fetch_finmind.py --verify")
    zero = 0
    for prev, d in itertools.pairwise(dates):
        c0, (c1, s1) = Decimal(rows[prev][0]), rows[d]
        if Decimal(s1) == 0:
            official = read_csv(TAIEX_CLOSE / f"TAIEX__{d}.csv", ["date", "TAIEX"]).row(0)
            try:
                same = official[0] == f"{d} 13:30:00" and Decimal(official[1]) == Decimal(c1)
            except InvalidOperation:
                same = False
            if not same:
                stop(f"TAIEX close {c1} on {d} differs from the 13:30:00 value {official}")
            zero += 1
        elif Decimal(c1) - c0 != Decimal(s1):
            stop(f"TAIEX close {c1} on {d} disagrees with its spread {s1} (previous close {c0})")
    if zero != N_ZERO_SPREAD:
        stop(f"{zero} zero-spread TAIEX dates, expected {N_ZERO_SPREAD}")
    out(f"[price] TAIEX price index: {len(dates)} closes {dates[0]} .. {dates[-1]}; every close agrees with its spread "
        f"to the cent, except {zero} zero-spread dates, each equal to its 13:30:00 value")
    return pl.DataFrame({"date": dates, "price": [float(rows[d][0]) for d in dates]})

def main() -> int:
    tr = read_csv(TR_FILE, ["date", "price"]).select("date", pl.col("price").cast(pl.Float64, strict=False).alias("tr"))
    if tr["tr"].null_count():
        stop("a total-return level is not a number: run fetch_finmind.py --verify")
    if tr["date"].n_unique() != tr.height or not tr["date"].is_sorted():
        stop("total-return dates are duplicated or unsorted")
    px = read_price().filter(pl.col("date") >= tr["date"][0])
    if tr["date"].to_list() != px["date"].to_list():
        a, b = set(tr["date"]), set(px["date"])
        stop(f"calendars differ: only total return {sorted(a - b)[:10]}, only price {sorted(b - a)[:10]}")
    df = tr.with_columns(price=px["price"]).with_columns(       # same dates in the same order, checked just above
        R=pl.col("tr") / pl.col("tr").shift(1) - 1, Rp=pl.col("price") / pl.col("price").shift(1) - 1)
    body = df.slice(1)
    dates, g = body["date"].to_list(), (body["R"] - body["Rp"]).to_numpy()
    bad = [(d, f"{x * 1e4:.3f} bp") for d, x in zip(dates, g) if not GAP_LO <= x <= GAP_HI]
    bad += [(d, f"{x * 1e4:.3f} bp at an end") for d, x in ((dates[0], g[0]), (dates[-1], g[-1]))
            if abs(x) > -GAP_LO and GAP_LO <= x <= GAP_HI]                  # a date out of range is listed once
    if bad:
        stop(f"{len(bad)} dates where total minus price return leaves its range: {bad[:10]}")
    if (body["R"] == 0).any():
        stop(f"total-return level repeats on {body.filter(pl.col('R') == 0)['date'].to_list()[:10]}")
    big = body.filter((pl.col("R").abs() > MAX_MOVE) | (pl.col("Rp").abs() > MAX_MOVE))
    if big.height:
        stop(f"daily move above {MAX_MOVE:.1%}: {big['date'].to_list()}")
    high = [d for d, x in zip(dates, g) if x > 0.004]
    out(f"[check] total minus price return per day: min {g.min() * 1e4:.3f} bp, max {g.max() * 1e4:.2f} bp; "
        f"{len(high)} dates above 40 bp ({', '.join(high)}); first and last day {g[0] * 1e4:.4f} and "
        f"{g[-1] * 1e4:.4f} bp")
    first, last = df["date"][0], df["date"][-1]
    t = body.height
    days = (pl.Series([last]).str.to_date() - pl.Series([first]).str.to_date()).dt.total_days()[0]
    years = days / 365.25
    out(f"[TR23] {df.height} closes {first} .. {last}; T = {t} simple returns from {dates[0]}; "
        f"{days} calendar days = {years:.4f} years; A = T / years = {t / years:.4f}")
    out(f"[TR23] growth factor {df['tr'][-1] / df['tr'][0]:.4f} (total return), {df['price'][-1] / df['price'][0]:.4f} "
        "(price)")
    PROC.mkdir(exist_ok=True)
    df.with_columns(pl.col("date").str.to_date()).write_parquet(PROC / "vol3_taiex.parquet")
    out(f"[out] data/processed/vol3_taiex.parquet: {df.height} rows x {df.width} columns (date, tr, price, R, Rp)")
    report()
    return 0

if __name__ == "__main__":
    sys.exit(main())
