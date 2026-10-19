"""Volume IV's basis sample TX23: the TX near-month settlement and the TAIEX close on TR23's 5,850 dates, checked.

F is the regular-session daily settlement price of the TX contract held at each close, S the TAIEX price close of
TR23 (data/processed/vol3_taiex.parquet, column price, from data/vol3_series.py). A monthly contract's last trading
day is its last regular-session row in TaiwanFuturesDaily; the position rolls to the next month at the close of the
day before that day (LM2's rule), so no row from a contract's last trading day enters: from 2008-12-17 FinMind prints
the expiring contract's settlement as 0 on that day (data/README.md, vol4/). For the one contract still trading at
the end of the raw file, the last trading day is the TAIFEX rule's third Wednesday of the month (the file runs past
TR23's last date, so that contract is not rolled inside the sample either way).

The script stops on the first failed check:
  1. the raw file has the expected columns, no empty values, no duplicate (date, contract) and is sorted;
  2. the regular-session calendar equals TR23's 5,850 dates, with 5 or 6 monthly contracts on each date;
  3. for every row in the window, spread = close - the contract's previous settlement when the contract traded
     (close > 0), and spread = volume = 0 when it did not; on the SAME_DAY_SPREAD date (2007-03-12) every row's
     spread is instead its close minus the same day's settlement, and the next session's rows follow the rule;
  4. no date repeats another date's rows (a copied day, project/PITFALLS.md section 3);
  5. each closed contract's last row lies in its delivery month, from the third Wednesday to 14 days after it
     (a holiday shift); the zero settlements are exactly the last rows of the contracts that expire from 2008-12-17;
  6. every price used (the held contract's settlement today and the previous contract's settlement today) is
     positive and comes from a contract whose last trading day is after the date;
  7. no daily log change of the held position (rF) exceeds MAX_LOG_MOVE, and |ln(F/S)| stays below MAX_LOG_BASIS.
When the optional cross-check file raw/vol4_settlement/ is present (TaiwanFuturesFinalSettlementPrice, Backer), each
monthly contract's official final-settlement date must equal its last trading day (contracts from 200901) or the
next trading day (contracts to 200712); the file has no rows for 2006, 2008, 2014 and 2020 (and 2000).

Outputs (git-ignored): data/processed/vol4_tx23.parquet, one row per TR23 date:
  date, S (TAIEX close), F (settlement of the contract held from this close), contract (its month, YYYYMM),
  last_day (its last trading day), days (calendar days from date to last_day), basis = ln(F/S),
  F_held (today's settlement of the contract held from the previous close; differs from F on roll days),
  rF = ln(F_held / F[previous date]) (the roll-free daily log change of the position), rS = ln(S / S[previous date]),
  roll (true when the contract held from this close differs from the one held at the previous close),
  volume, open_interest (of the contract held from this close);
and data/processed/vol4_series.txt (this report).

Run:  PYTHONUTF8=1 uv run python data/vol4_series.py     (exit 0 only when every check passes; run vol3_series.py first)
"""
import datetime as dt
import itertools
import sys
from pathlib import Path
from typing import NoReturn

import polars as pl

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
PROC = HERE / "processed"
TX_FILE = RAW / "vol4" / "TX__1998-07-21__2026-10-16.csv"
SETTLE_FILE = RAW / "vol4_settlement" / "TX__1998-07-21__2026-10-16.csv"   # optional cross-check (Backer)
TR23_FILE = PROC / "vol3_taiex.parquet"
TX_COLS = ["date", "contract_date", "close", "spread", "settlement_price", "volume", "open_interest"]

N_DATES = 5850                 # TR23's closes, 2003-01-02 .. 2026-10-08 (data/vol3_series.py)
# The one date of the window whose spreads break the rule: on 2007-03-12 every listed month's spread is its close minus
# the SAME day's settlement (0, 0, 0, 11, 0), and the next session's spreads, which follow the rule, confirm those
# settlements. Check 3 asserts this pattern on every row of the date.
SAME_DAY_SPREAD = ("2007-03-12",)
ZERO_SETTLE_FROM = "2008-12-17"   # first last trading day on which FinMind prints the expiring settlement as 0
MAX_LOG_MOVE = 0.106           # TX's price limit was 7% to 2015-05-29 and 10% from 2015-06-01: |ln 0.9| = 0.1054
MAX_LOG_BASIS = 0.08           # widest -0.0793 on 2008-10-27 (TX -7%, its limit; TAIEX -4.6%); a misdated row moves it

LINES: list[str] = []

def out(s: str = "") -> None:
    print(s)
    LINES.append(s)

def report() -> None:
    PROC.mkdir(exist_ok=True)
    (PROC / "vol4_series.txt").write_text("\n".join(LINES) + "\n", encoding="utf-8", newline="\n")

def stop(msg: str) -> NoReturn:
    out(f"STOP: {msg}")
    report()
    sys.exit(1)

def third_wednesday(month: str) -> dt.date:
    d = dt.date(int(month[:4]), int(month[4:]), 1)
    return d + dt.timedelta(days=(2 - d.weekday()) % 7 + 14)

def read_tx() -> pl.DataFrame:
    if not TX_FILE.exists():
        stop(f"missing {TX_FILE.relative_to(HERE)}: run uv run python data/fetch_finmind.py")
    raw = pl.read_csv(TX_FILE, infer_schema=False)
    if raw.columns != TX_COLS or raw.height == 0 or raw.null_count().sum_horizontal()[0]:
        stop(f"{TX_FILE.name}: columns {raw.columns}, {raw.height} rows or empty values: run fetch_finmind.py --verify")
    tx = raw.with_columns(pl.col("close", "spread", "settlement_price").cast(pl.Float64, strict=False),
                          pl.col("volume", "open_interest").cast(pl.Int64, strict=False))
    if tx.null_count().sum_horizontal()[0]:
        stop(f"{TX_FILE.name}: a price, volume or open interest is not a number")
    keys = tx.select(pl.concat_str("date", "contract_date", separator=" "))["date"]
    if keys.n_unique() != tx.height or not keys.is_sorted():
        stop(f"{TX_FILE.name}: duplicate or unsorted (date, contract) rows")
    return tx

def main() -> int:
    if not TR23_FILE.exists():
        stop("missing data/processed/vol3_taiex.parquet: run uv run python data/vol3_series.py first")
    tr = pl.read_parquet(TR23_FILE).select(pl.col("date").dt.strftime("%Y-%m-%d"), pl.col("price").alias("S"))
    dates = tr["date"].to_list()
    if len(dates) != N_DATES:
        stop(f"TR23 has {len(dates)} dates, expected {N_DATES}")
    first, last = dates[0], dates[-1]
    tx = read_tx()
    all_dates = tx["date"].unique().sort().to_list()
    file_end = all_dates[-1]
    out(f"[raw] {TX_FILE.name}: {tx.height} regular-session monthly rows, {len(all_dates)} dates "
        f"{all_dates[0]} .. {file_end}, {tx['contract_date'].n_unique()} contracts")

    # 2. calendar
    in_win = [d for d in all_dates if first <= d <= last]
    if in_win != dates:
        a, b = set(in_win), set(dates)
        stop(f"calendars differ: only TX {sorted(a - b)[:10]}, only TR23 {sorted(b - a)[:10]}")
    win = tx.filter(pl.col("date").is_between(pl.lit(first), pl.lit(last)))
    per_day = win.group_by("date").len().sort("date")
    if not set(per_day["len"].unique().to_list()) <= {5, 6}:
        stop(f"monthly contracts per date: {per_day['len'].value_counts().sort('len').rows()}")
    runs: list[list] = []
    for d, n in per_day.iter_rows():
        if runs and runs[-1][0] == n:
            runs[-1][2] = d
        else:
            runs.append([n, d, d])
    out(f"[calendar] the regular-session dates equal TR23's {len(dates)} dates {first} .. {last}; monthly contracts "
        "per date: " + "; ".join(f"{n} from {a} to {b}" for n, a, b in runs))

    # 3. spread = close - previous settlement of the same contract
    chk = (tx.sort("contract_date", "date")
             .with_columns(prev=pl.col("settlement_price").shift(1).over("contract_date"))
             .filter(pl.col("date").is_between(pl.lit(first), pl.lit(last)) & pl.col("prev").is_not_null()))
    traded = pl.col("close") > 0
    bad_rule = (traded & ((pl.col("close") - pl.col("prev") - pl.col("spread")).abs() > 0.005)) | (
        ~traded & ((pl.col("spread") != 0) | (pl.col("volume") != 0)))
    bad = chk.filter(bad_rule)
    found = set(zip(bad["date"], bad["contract_date"]))
    same = chk.filter(pl.col("date").is_in(SAME_DAY_SPREAD))
    expected = set(zip(same["date"], same["contract_date"]))
    if found != expected:
        stop(f"rows breaking the spread rule: new {sorted(found - expected)[:10]}, following it on a same-day date "
             f"{sorted(expected - found)}")
    off = same.filter(~traded | ((pl.col("close") - pl.col("settlement_price") - pl.col("spread")).abs() > 0.005))
    if off.height:
        stop(f"on {', '.join(SAME_DAY_SPREAD)} the spread is not close - same-day settlement: {off.rows()[:5]}")
    nd = dict(itertools.pairwise(all_dates))
    confirm = chk.filter(pl.col("date").is_in([nd[d] for d in SAME_DAY_SPREAD])
                         & pl.col("contract_date").is_in(same["contract_date"].unique().to_list()))
    if confirm.height != same.height:
        stop(f"the session after {', '.join(SAME_DAY_SPREAD)} lacks some of its contracts")
    n_untraded = chk.filter(~traded).height
    out(f"[spread] {chk.height} rows with a previous settlement in the window: spread = close - previous settlement "
        f"on every traded row and spread = volume = 0 on the {n_untraded} untraded rows (close 0), except on "
        f"{', '.join(SAME_DAY_SPREAD)}, where each of the {same.height} months' spread is its close minus the same "
        f"day's settlement (the next session's {confirm.height} rows follow the rule against those settlements)")

    # 4. copied days
    sig = (win.group_by("date").agg(pl.concat_str(pl.exclude("date"), separator=",").sort().str.join(";").alias("k")))
    dup = sig.filter(pl.col("k").is_duplicated())
    if dup.height:
        stop(f"dates with identical rows: {dup['date'].sort().to_list()[:10]}")
    out(f"[copies] no two of the {sig.height} dates carry the same rows")

    # 5. last trading days and the expiry-day zeros
    ends = tx.group_by("contract_date").agg(pl.col("date").max().alias("end")).sort("contract_date")
    last_day: dict[str, dt.date] = {}
    shifted, open_ = [], []
    for c, e in ends.iter_rows():
        tw = third_wednesday(c)
        if e == file_end:                                   # still trading when the file ends
            if tw.isoformat() <= file_end:
                stop(f"contract {c} trades past its third Wednesday {tw}")
            last_day[c] = tw
            open_.append(c)
            continue
        ed = dt.date.fromisoformat(e)
        if c >= first[:4] + first[5:7] and not (tw <= ed <= tw + dt.timedelta(days=14)):
            stop(f"contract {c}: last row {e} is not within 14 days after its third Wednesday {tw}")
        if ed != tw and c >= first[:4] + first[5:7]:
            shifted.append(f"{c} {e}")
        last_day[c] = ed
    zero = set(tx.filter(pl.col("settlement_price") == 0).select("date", "contract_date").iter_rows())
    expect = {(d.isoformat(), c) for c, d in last_day.items() if c not in open_ and d.isoformat() >= ZERO_SETTLE_FROM}
    if zero != expect:
        stop(f"zero settlements off the expected last rows: extra {sorted(zero - expect)[:5]}, "
             f"missing {sorted(expect - zero)[:5]}")
    out(f"[expiry] last trading day = each contract's last regular-session row; {len(shifted)} contracts of the "
        f"window end after their third Wednesday (holiday shifts): {', '.join(shifted)}; still trading at the file's "
        f"end {file_end}: {', '.join(open_)} (third Wednesday used). Settlement prints 0 on exactly the {len(zero)} "
        f"last trading days from {ZERO_SETTLE_FROM}")

    # 6. the held contract
    settle = {(d, c): (s, v, oi) for d, c, s, v, oi in
              tx.select("date", "contract_date", "settlement_price", "volume", "open_interest").iter_rows()}
    months = {d: sorted(g) for d, g in tx.group_by("date").agg(pl.col("contract_date")).iter_rows()}
    nxt = dict(itertools.pairwise(all_dates))
    rows = []
    held_prev = None
    for d in dates:
        nd = nxt.get(d)
        if nd is None:
            stop(f"no session after {d} in the raw file: extend its end date")
        cand = [c for c in months[d] if last_day[c] > dt.date.fromisoformat(nd)]
        if not cand:
            stop(f"no contract on {d} trades beyond the next session {nd}")
        c = cand[0]
        s, v, oi = settle[(d, c)]
        f_held = None
        if held_prev is not None:
            if (d, held_prev) not in settle:
                stop(f"{held_prev} has no row on {d}")
            f_held = settle[(d, held_prev)][0]
            if not last_day[held_prev] > dt.date.fromisoformat(d):
                stop(f"{held_prev} is used on its last trading day {d}")
            if f_held <= 0:
                stop(f"settlement of {held_prev} on {d} is {f_held}")
        if not last_day[c] > dt.date.fromisoformat(d) or s <= 0:
            stop(f"{c} on {d}: last trading day {last_day[c]}, settlement {s}")
        rows.append({"date": d, "F": s, "contract": int(c), "last_day": last_day[c],
                     "days": (last_day[c] - dt.date.fromisoformat(d)).days, "F_held": f_held,
                     "roll": held_prev is not None and c != held_prev, "volume": v, "open_interest": oi})
        held_prev = c
    df = (pl.DataFrame(rows).join(tr, on="date", how="left", validate="1:1").sort("date")   # shift() needs the order
          .with_columns(basis=(pl.col("F") / pl.col("S")).log(),
                        rF=(pl.col("F_held") / pl.col("F").shift(1)).log(),
                        rS=(pl.col("S") / pl.col("S").shift(1)).log())
          .select("date", "S", "F", "contract", "last_day", "days", "basis", "F_held", "rF", "rS", "roll",
                  "volume", "open_interest"))
    if df["S"].null_count():
        stop("TR23 lacks a price close on a TX date")

    # 7. bounds
    body = df.slice(1)
    big = body.filter(pl.col("rF").abs() > MAX_LOG_MOVE)
    if big.height:
        stop(f"daily log change of the held position above {MAX_LOG_MOVE}: {big.select('date', 'rF').rows()[:10]}")
    wide = df.filter(pl.col("basis").abs() > MAX_LOG_BASIS)
    if wide.height:
        stop(f"|ln(F/S)| above {MAX_LOG_BASIS}: {wide.select('date', 'basis').rows()[:10]}")
    i_max = int(body["rF"].abs().arg_max() or 0)
    rolls = df.filter("roll")
    out(f"[TX23] {df.height} dates {first} .. {last}; {rolls.height} rolls; days to the last trading day "
        f"{df['days'].min()} .. {df['days'].max()}; near-month volume {df['volume'].min()} .. {df['volume'].max()} "
        "contracts")
    out(f"[TX23] rF: largest |daily log change| {abs(body['rF'][i_max]):.4f} on {body['date'][i_max]} "
        f"(bound {MAX_LOG_MOVE}); F unchanged on {int((body['rF'] == 0).sum())} dates")
    out(f"[TX23] basis ln(F/S): min {df['basis'].min():.4f}, median {df['basis'].median():.4f}, "
        f"max {df['basis'].max():.4f} (bound {MAX_LOG_BASIS})")
    sample = [rolls.row(i, named=True) for i in (0, 1, 2, rolls.height // 2, rolls.height - 2, rolls.height - 1)]
    prev_c = dict(zip(df["date"].shift(-1).to_list(), df["contract"].to_list()))
    out("[rolls] sample (rolled at the close of date, from contract to contract, the old one's last trading day): "
        + "; ".join(f"{r['date']} {prev_c[r['date']]}->{r['contract']} (expires {last_day[str(prev_c[r['date']])]})"
                    for r in sample))

    # optional cross-check: official final-settlement dates
    if SETTLE_FILE.exists():
        fin = pl.read_csv(SETTLE_FILE, infer_schema=False)
        n_same = n_next = 0
        for d, c, _ in fin.iter_rows():
            if c not in last_day or c in open_ or c < first[:4] + first[5:7] or c > last[:4] + last[5:7]:
                continue
            ld = last_day[c].isoformat()
            if c >= "200901" and d == ld:
                n_same += 1
            elif c <= "200712" and d == nxt.get(ld):
                n_next += 1
            else:
                stop(f"final settlement of {c} dated {d}, last trading day {ld}")
        held = sorted({str(c) for c in df["contract"].unique().to_list()} - set(open_))
        have = set(fin["contract_month"].to_list())
        missing = [c for c in held if c not in have]
        yrs = sorted({c[:4] for c in missing})
        out(f"[final] {SETTLE_FILE.parent.name}/{SETTLE_FILE.name}: of the {len(held)} closed contracts held, "
            f"{n_same + n_next} have an official final settlement, dated on the last trading day ({n_same}, from "
            f"200901) or the next session ({n_next}, to 200712); {len(missing)} have none (years {', '.join(yrs)})")
    else:
        out(f"[final] {SETTLE_FILE.parent.name}/ absent (Backer dataset): cross-check skipped")

    PROC.mkdir(exist_ok=True)
    df.with_columns(pl.col("date").str.to_date()).write_parquet(PROC / "vol4_tx23.parquet")
    out(f"[out] data/processed/vol4_tx23.parquet: {df.height} rows x {df.width} columns ({', '.join(df.columns)})")
    report()
    return 0

if __name__ == "__main__":
    sys.exit(main())
