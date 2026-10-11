"""Volume II sector-index closes: merge the FinMind chunks, repair the closes FinMind served wrongly, validate every row.

What it does. TaiwanStockPrice serves the TWSE sector indices (and TAIEX) with rows copied from another date
(data/README.md "sectors/", project/PITFALLS.md section 3). This script
  1. merges the 13 chunks per series in raw/sectors/ (31 series: TAIEX, 28 leaf sectors, 2 aggregate indices) onto the
     TAIEX calendar;
  2. flags every (series, date) whose served close must be repaired, by three rules:
       (i)   the close is contradicted on both sides by the spread (close[t]-close[t-1] != spread[t] and
             close[t+1]-close[t] != spread[t+1]) with mismatches of opposite sign and similar size;
       (ii)  the close equals the same series' close on another date and the row is contradicted on at least one side;
       (iii) the stage-1 OHLC test (cloned open/high/low in FinMind's full records, which are not in the repo, so
             this script cannot run it; its 563 rows are all caught by (i) or (ii) except three whose closes the
             13:30:00 values confirm);
       (iv)  a close that the validation step below found still contradicted on both sides: RULE_IV lists them;
  3. replaces each flagged close with the 13:30:00 value of TaiwanStockEvery5SecondsIndex (kind twse), read from the
     raw files registered in raw/sectors_close/ (<ID>__<date>.csv, one per repaired close). A flagged close that is
     not repaired must belong to the set recorded in FLAGGED_KEPT_N / FLAGGED_KEPT_SHA (each equalled its 13:30:00
     value when it was registered), or the script stops;
     A registered value that differs from the served close on a date the rules did not flag is repaired as well
     (rule "5s"); a registered value equal to the served close is counted as confirmed;
  4. validates every row of every series after the repair. A remaining spread mismatch is accepted only as a stale
     spread: an isolated mismatch whose two closes each agree with their other neighbour (a wrong spread on a sound
     close path); each is counted and listed. A close still contradicted on both sides (two mismatches in a row)
     stops the script with a list, unless it is in EXCEPTIONS with its evidence. So do a daily move above 10.5%.

Closes and spreads are compared exactly, in whole cents (Decimal parsing; no tolerance): a clean row has
close[t] - close[t-1] == spread[t] to the cent.

TAIEX's spread prints 0.0 on 52 dates (2017-12 .. 2026-02), so the spread cannot validate those closes. Each of them
is compared with the official 13:30:00 TAIEX value of TaiwanVariousIndicators5Seconds registered in
raw/taiex_close/TAIEX__<date>.csv: equal -> validated; different -> repaired and listed (rule "taiex0").

raw/sectors_close/ holds one file per REPAIRED sector close and nothing else. The registered values that merely
equalled the served close were checked once, when they were registered, and their files were dropped to keep the repair
download small; their count is kept in CONFIRMED_RECORDED below and printed in the report. The 13:30:00 values on dates
without a served close are not used; they are listed in the report (UNUSED_RECORDED holds the four whose files were
dropped).

Rows before a gap (a date of the TAIEX calendar without a close in that series) and the first and last row of a series
cannot be checked on both sides; they are listed when they show a mismatch.

Outputs (git-ignored): data/processed/vol2_closes.parquet (date x 31 series, null where a series has no close),
data/processed/vol2_repairs.json (series, date, served close, repaired close, rule; the confirmed ones separately),
data/processed/vol2_series.txt (this report) and data/processed/vol2_flagged_kept.txt (the kept pairs of the last
passing run, so that a later STOP can name the pairs that appeared or disappeared).

Run:  PYTHONUTF8=1 uv run python data/vol2_series.py     (exit 0 only when every row validates)
"""
import hashlib
import json
import sys
from decimal import Decimal
from pathlib import Path

import numpy as np
import polars as pl
from numpy.typing import NDArray

Vec = NDArray[np.float64]
Flags = NDArray[np.bool_]

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
SECT = RAW / "sectors"
CLOSE = RAW / "sectors_close"
TAIEX_CLOSE = RAW / "taiex_close"
PROC = HERE / "processed"
KEPT_LIST = PROC / "vol2_flagged_kept.txt"      # the kept pairs of the last passing run; a later STOP names the difference

CANCEL = 2                   # cents: two opposite mismatches cancel (rule i) to within 2 cents or 10% of the larger
MAX_MOVE = 0.105             # no sector index moves more than about 10.1% in a day (its stocks stop at 10%)

# Rule (iv): wrong closes that rules (i) and (ii) miss and the validation step found (two consecutive mismatches that do
# not cancel). Each is flagged here and its 13:30:00 value registered in raw/sectors_close/.
# Chemical 2009-08-25 and 2009-08-26: served 92.75 and 91.57 against the 13:30:00 values 93.19 and 91.29. The spreads
# 0.72, -1.9 and 0.52 chain 92.47 (2009-08-24) to 93.19, 91.29 and 91.81 (2009-08-27) exactly, and both 92.47 and 91.81
# agree with the 13:30:00 values, so the two closes in between were the wrong fields.
RULE_IV: set[tuple[str, str]] = {("Chemical", "2009-08-25"), ("Chemical", "2009-08-26")}

# Closes that stay contradicted on both sides (or move above MAX_MOVE) after the repair and are accepted anyway.
# (series, date) -> evidence. Empty unless a case is explained.
EXCEPTIONS: dict[tuple[str, str], str] = {}

# Registered 13:30:00 values whose files were dropped (data/raw/sectors_close/ keeps repairs only). They are recorded
# here as counts, with the figures of the run that dropped them (2026-10-11): 3,029 values equalled the served close
# (103 of them TAIEX's), 561 differed and are the repairs, 4 fell on dates without a served close.
CONFIRMED_RECORDED = 3029
# Flagged by a rule but equal to the 13:30:00 value (so no file is kept): how many, and the SHA-256 of the sorted
# "<series> <date>" lines, so that any change to the flagged set stops the script until it is checked again.
FLAGGED_KEPT_N = 1488
FLAGGED_KEPT_SHA = "bc6f4c537deb80ddf9897fe1ba84a1b6abac412b2e4e587c0d5466cc17b0b5f1"
# Registered values on dates where TaiwanStockPrice serves no close: (series, date) -> value.
# TradingConsumersGoods has no close before 2008-12-01 except three stray ones; the 5-second data show that the index
# existed on these four sessions.
UNUSED_RECORDED: dict[tuple[str, str], str] = {
    ("TradingConsumersGoods", "2007-12-11"): "124.48",
    ("TradingConsumersGoods", "2007-12-12"): "124.23",
    ("TradingConsumersGoods", "2008-02-21"): "142.94",
    ("TradingConsumersGoods", "2008-02-22"): "144.8",
}

LINES: list[str] = []


def out(s: str = "") -> None:
    LINES.append(s)
    print(s)


# ------------------------------------------------------------------ loading
def cents(text: str) -> float:
    """A price or spread as printed (at most two decimals) in whole cents, exactly; a float holds the integer."""
    v = Decimal(text) * 100
    assert v == v.to_integral_value(), f"more than two decimals: {text}"
    return float(v)


def load_chunks(name: str) -> pl.DataFrame:
    files = sorted(SECT.glob(f"{name}__*.csv"))
    assert files, f"no files for {name}"
    df = pl.concat([pl.read_csv(f, schema_overrides={"spread": pl.String, "close": pl.String}) for f in files])
    df = df.with_columns(pl.col(c).map_elements(cents, return_dtype=pl.Float64) for c in ("close", "spread"))
    assert df["date"].n_unique() == df.height, f"{name}: duplicate dates across chunks"
    return df.sort("date")


def load_registered(series: list[str]) -> dict[tuple[str, str], float]:
    """The 13:30:00 closes of the twse index in raw/sectors_close/: (series, date) -> price in cents."""
    known = set(series)
    vals: dict[tuple[str, str], float] = {}
    for f in sorted(CLOSE.glob("*.csv")):
        df = pl.read_csv(f, schema_overrides={"price": pl.String}).filter(
            (pl.col("time") == "13:30:00") & (pl.col("kind") == "twse"))
        prefix = f.name.split("__")[0]
        for d, sid, p in df.select("date", "stock_id", "price").iter_rows():
            assert sid == prefix, f"{f.name}: stock_id {sid}"
            assert sid in known, f"{f.name}: {sid} is not one of the 31 series"
            key = (sid, d)
            assert key not in vals or vals[key] == cents(p), f"{key}: two registered values {vals[key]} and {p}"
            vals[key] = cents(p)
    return vals


def load_taiex_official() -> dict[str, float]:
    """The official 13:30:00 TAIEX value of TaiwanVariousIndicators5Seconds in raw/taiex_close/: date -> cents."""
    vals: dict[str, float] = {}
    for f in sorted(TAIEX_CLOSE.glob("TAIEX__*.csv")):
        df = pl.read_csv(f, schema_overrides={"TAIEX": pl.String})
        assert df.height == 1, f"{f.name}: {df.height} rows"
        stamp, price = df.row(0)
        day, clock = stamp.split(" ")
        assert clock == "13:30:00" and f.name == f"TAIEX__{day}.csv", f"{f.name}: {stamp}"
        vals[day] = cents(price)
    return vals


# ------------------------------------------------------------------ rules
def mismatch(c: Vec, s: Vec) -> Vec:
    """g[t] = close[t] - close[t-1] - spread[t] in cents on the calendar (NaN where a close or the spread is missing)."""
    g = np.full(len(c), np.nan)
    g[1:] = c[1:] - c[:-1] - s[1:]
    return g


def rule_i(g: Vec) -> Flags:
    """Contradicted on both sides by mismatches of opposite sign and similar size (cancelling to within 10%)."""
    n = len(g)
    gg = np.nan_to_num(g)
    m = gg != 0
    flag = np.zeros(n, dtype=bool)
    a, b = gg[1:-1], gg[2:]
    big = np.maximum(np.abs(a), np.abs(b))
    flag[1:-1] = m[1:-1] & m[2:] & (a * b < 0) & (np.abs(a + b) <= np.maximum(CANCEL, 0.1 * big))
    return flag


def rule_ii(c: Vec, g: Vec) -> Flags:
    """The close repeats the series' close on another date and the row is contradicted on at least one side."""
    m = np.nan_to_num(g) != 0
    contra = m.copy()
    contra[:-1] |= m[1:]
    r = c
    ok = ~np.isnan(r)
    vals, counts = np.unique(r[ok], return_counts=True)
    dup = np.zeros(len(c), dtype=bool)
    dup[ok] = counts[np.searchsorted(vals, r[ok])] > 1
    return dup & contra


def main() -> int:
    names = sorted({p.name.split("__")[0] for p in SECT.glob("*.csv")})
    assert "TAIEX" in names and len(names) == 31, len(names)
    series = ["TAIEX", *[n for n in names if n != "TAIEX"]]
    chunks = {n: load_chunks(n) for n in series}
    cal = chunks["TAIEX"]["date"].to_list()
    idx = {d: i for i, d in enumerate(cal)}
    n_cal = len(cal)
    served: dict[str, Vec] = {}
    spread: dict[str, Vec] = {}
    for n in series:
        c = np.full(n_cal, np.nan)
        s = np.full(n_cal, np.nan)
        extra = [d for d in chunks[n]["date"].to_list() if d not in idx]
        assert not extra, f"{n}: dates outside the TAIEX calendar {extra[:5]}"
        ii = [idx[d] for d in chunks[n]["date"].to_list()]
        c[ii] = chunks[n]["close"].to_numpy()
        s[ii] = chunks[n]["spread"].to_numpy()
        served[n], spread[n] = c, s
    # TAIEX's spread prints 0.0 through parts of 2017-12, 2018-09 and 2026-02: it cannot validate those closes
    zero_taiex = [cal[i] for i in np.flatnonzero(spread["TAIEX"] == 0)]
    spread["TAIEX"][spread["TAIEX"] == 0] = np.nan
    out(f"[load] {len(series)} series, master calendar = TAIEX {n_cal} dates {cal[0]}..{cal[-1]}; "
        f"{sum(int((~np.isnan(served[n])).sum()) for n in series)} closes")
    reg = load_registered(series)
    out(f"[load] {len(reg)} registered 13:30:00 closes (raw/sectors_close/: {len(list(CLOSE.glob('*.csv')))} files)")
    official = load_taiex_official()
    out(f"[load] {len(official)} official TAIEX 13:30:00 values (raw/taiex_close/: {len(list(TAIEX_CLOSE.glob('*.csv')))} "
        f"files) for the {len(zero_taiex)} TAIEX dates whose spread prints 0.0")

    # --- 2. flag
    by_rule: dict[tuple[str, str], set[str]] = {}
    for n in series:
        g = mismatch(served[n], spread[n])
        r1, r2 = rule_i(g), rule_ii(served[n], g)
        for i in np.flatnonzero(r1 | r2):
            rules = by_rule.setdefault((n, cal[i]), set())
            if r1[i]:
                rules.add("i")
            if r2[i]:
                rules.add("ii")
    for key in RULE_IV:
        by_rule.setdefault(key, set()).add("iv")
    cnt = {r: sum(1 for v in by_rule.values() if r in v) for r in ("i", "ii", "iv")}
    out(f"[flag] {len(by_rule)} (series, date) pairs flagged: rule (i) {cnt['i']}, rule (ii) {cnt['ii']}, "
        f"rule (iv) {cnt['iv']} (rule (iii) is the stage-1 OHLC test, not reproducible here)")

    # --- 3. repair
    repaired = {n: served[n].copy() for n in series}
    repairs: list[dict[str, object]] = []
    confirmed: list[dict[str, object]] = []
    unused: list[str] = []
    for (n, d) in sorted(reg, key=lambda k: (k[1], k[0])):
        i = idx.get(d)
        if i is None or np.isnan(served[n][i]):
            unused.append(f"{n} {d} {reg[(n, d)] / 100}")
            continue
        rule = ",".join(sorted(by_rule.get((n, d), set()))) or "5s"
        if served[n][i] != reg[(n, d)]:
            repairs.append({"series": n, "date": d, "served": float(served[n][i]) / 100,
                            "repaired": reg[(n, d)] / 100, "rule": rule})
            repaired[n][i] = reg[(n, d)]
        else:
            confirmed.append({"series": n, "date": d, "close": float(served[n][i]) / 100, "rule": rule})
    n_flag_changed = sum(1 for r in repairs if r["rule"] != "5s")
    out(f"[repair] {len(repairs)} closes replaced ({n_flag_changed} flagged by a rule, {len(repairs) - n_flag_changed} "
        f"only by the 5-second value)")
    repaired_keys = {(str(r["series"]), str(r["date"])) for r in repairs}
    kept = sorted(k for k in by_rule if k not in repaired_keys)
    digest = hashlib.sha256("\n".join(f"{n} {d}" for n, d in kept).encode()).hexdigest()
    out(f"[repair] {CONFIRMED_RECORDED + len(confirmed)} registered 13:30:00 values equalled the served close "
        f"({CONFIRMED_RECORDED} recorded when their files were dropped, {len(confirmed)} still registered)")
    out(f"[repair] {len(kept)} flagged pairs are kept as served: each equalled its 13:30:00 value when it was registered "
        f"(recorded: {FLAGGED_KEPT_N}, sha256 of the sorted pairs {FLAGGED_KEPT_SHA[:12]})")
    kept_lines = [f"{n} {d}" for n, d in kept]
    if (len(kept), digest) != (FLAGGED_KEPT_N, FLAGGED_KEPT_SHA):
        out(f"[repair] STOP: the kept pairs differ from the ones verified against the 13:30:00 values "
            f"({len(kept)}, sha256 {digest})")
        out("    Check first: `uv run python data/fetch_finmind.py --verify --only sectors_close/`. A missing repair file "
            "lands here (its pair is then kept with the wrong served close); restore it before touching the constants.")
        if KEPT_LIST.exists():
            before = set(KEPT_LIST.read_text(encoding="utf-8").splitlines())
            now = set(kept_lines)
            gone, new = sorted(before - now), sorted(now - before)
            out(f"    against the last run that passed ({KEPT_LIST.name}): {len(new)} pairs appeared, {len(gone)} disappeared")
            for line in new:
                out(f"    appeared (kept as served, no repair): {line}")
            for line in gone:
                out(f"    disappeared (no longer flagged, or now repaired): {line}")
        else:
            out(f"    (no {KEPT_LIST.name} from an earlier passing run, so the pairs cannot be named)")
        out("    Only if the new flagged pairs are genuine: register their 13:30:00 values and update FLAGGED_KEPT_N and "
            "FLAGGED_KEPT_SHA.")
        return write_report(1)
    PROC.mkdir(exist_ok=True)
    KEPT_LIST.write_text("\n".join(kept_lines) + "\n", encoding="utf-8", newline="\n")
    out(f"[repair] {len(UNUSED_RECORDED) + len(unused)} 13:30:00 values on dates without a served close (not used; "
        f"{len(UNUSED_RECORDED)} recorded when their files were dropped, {len(unused)} still registered)")
    for (n, d), v in sorted(UNUSED_RECORDED.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        out(f"    no served close (recorded): {n} {d} {v}")
    for u in unused:
        out(f"    no served close: {u}")
    # TAIEX closes whose spread prints 0.0: compare each with the official 13:30:00 value
    stray = sorted(d for d in official if d not in zero_taiex)
    absent = [d for d in zero_taiex if d not in official]
    if absent:
        out(f"[taiex] STOP: {len(absent)} zero-spread TAIEX dates have no official 13:30:00 value: {absent[:10]}")
        return write_report(1)
    i_t = {d: idx[d] for d in zero_taiex}
    taiex_equal = [d for d in zero_taiex if served["TAIEX"][i_t[d]] == official[d]]
    taiex_diff = [d for d in zero_taiex if served["TAIEX"][i_t[d]] != official[d]]
    for d in taiex_diff:
        repairs.append({"series": "TAIEX", "date": d, "served": float(served["TAIEX"][i_t[d]]) / 100,
                        "repaired": official[d] / 100, "rule": "taiex0"})
        repaired["TAIEX"][i_t[d]] = official[d]
    out(f"[taiex] {len(zero_taiex)} TAIEX closes have spread 0.0 ({zero_taiex[0]}..{zero_taiex[-1]}); each compared "
        f"with the official 13:30:00 value: {len(taiex_equal)} equal (validated), {len(taiex_diff)} different (repaired)")
    for d in taiex_diff:
        out(f"    TAIEX {d} served {served['TAIEX'][i_t[d]] / 100} -> {official[d] / 100}")
    if stray:
        out(f"[taiex] {len(stray)} official values on dates whose spread is not 0.0: registered, unused: {stray[:10]}")
    unflagged_changed = [r for r in repairs if r["rule"] == "5s"]
    out(f"[repair] repaired closes that no rule flagged: {len(unflagged_changed)}")
    for r in unflagged_changed:
        out(f"    {r['series']} {r['date']} served {r['served']} -> {r['repaired']}")
    out("[repair] every repair (series, date, served -> repaired, rule):")
    for r in repairs:
        out(f"    {r['series']} {r['date']} {r['served']} -> {r['repaired']} rule {r['rule']}")

    # --- 4. validate
    problems: list[str] = []
    stale: dict[str, list[str]] = {}
    unchecked: list[str] = []
    one_cent: list[str] = []
    for n in series:
        c, s = repaired[n], spread[n]
        g = mismatch(c, s)
        m = np.nan_to_num(g) != 0
        for i in np.flatnonzero(m):
            gl = g[i - 1] if i >= 1 else np.nan
            gr = g[i + 1] if i + 1 < n_cal else np.nan
            if np.nan_to_num(gr) != 0:          # close[i] is contradicted on both sides
                if (n, cal[i]) not in EXCEPTIONS:
                    problems.append(f"{n} {cal[i]} close {c[i] / 100}: g[t]={g[i] / 100:.2f}, g[t+1]={gr / 100:.2f}")
            elif np.nan_to_num(gl) != 0:
                continue                        # the same run: close[i-1] is reported above
            elif np.isnan(gl) or np.isnan(gr):
                unchecked.append(f"{n} {cal[i]} g={g[i] / 100:.2f} (a neighbouring close or spread is missing)")
            else:
                stale.setdefault(n, []).append(cal[i])
                if abs(g[i]) == 1:
                    one_cent.append(f"{n} {cal[i]}")
        mv = c[1:] / c[:-1] - 1
        for i in np.flatnonzero(np.nan_to_num(np.abs(mv)) > MAX_MOVE):
            if (n, cal[i + 1]) not in EXCEPTIONS:
                problems.append(f"{n} {cal[i + 1]} moves {mv[i]:.2%} ({c[i] / 100} -> {c[i + 1] / 100})")
    n_stale = sum(len(v) for v in stale.values())
    out(f"[validate] exact comparison in whole cents, no tolerance. Accepted stale spreads (isolated mismatch, both "
        f"closes agree with their other neighbour): {n_stale} over {len(stale)} series, of which {len(one_cent)} are "
        f"off by exactly 0.01; the spread field is wrong there, the closes are used")
    if one_cent:
        out(f"    off by exactly 0.01: {', '.join(one_cent)}")
    for n, ds in stale.items():
        out(f"    {n}: {len(ds)} dates: {' '.join(ds)}")
    out(f"[validate] mismatches that cannot be corroborated (first or last row, or next to a gap): {len(unchecked)}")
    for u in unchecked:
        out(f"    {u}")
    if EXCEPTIONS:
        out(f"[validate] {len(EXCEPTIONS)} explicit exceptions:")
        for (n, d), why in EXCEPTIONS.items():
            out(f"    {n} {d}: {why}")
    if problems:
        out(f"[validate] STOP: {len(problems)} closes still contradicted on both sides or moving above {MAX_MOVE:.1%}:")
        for p in problems:
            out(f"    {p}")
        return write_report(1)
    out("[validate] every row validates: no close is contradicted on both sides; "
        f"largest |daily move| {max(float(np.nanmax(np.abs(repaired[n][1:] / repaired[n][:-1] - 1))) for n in series):.4%}; "
        f"the {len(zero_taiex)} TAIEX closes with spread 0.0 are validated by the official 13:30:00 value")

    # --- outputs
    PROC.mkdir(exist_ok=True)
    wide = pl.DataFrame({"date": cal, **{n: pl.Series(n, repaired[n] / 100, nan_to_null=True) for n in series}})
    wide.write_parquet(PROC / "vol2_closes.parquet")
    (PROC / "vol2_repairs.json").write_text(
        json.dumps({"repairs": repairs, "confirmed_total": CONFIRMED_RECORDED + len(confirmed),
                    "confirmed_unchanged": confirmed,
                    "taiex_zero_spread": {"checked": zero_taiex, "equal": taiex_equal, "repaired": taiex_diff}},
                   indent=1) + "\n",
        encoding="utf-8", newline="\n")
    out(f"[out] data/processed/vol2_closes.parquet: {wide.height} dates x {len(series)} series, "
        f"{sum(int(wide[n].null_count()) for n in series)} null closes")
    out(f"[out] data/processed/vol2_repairs.json: {len(repairs)} repairs, {len(confirmed)} confirmed (still registered)")
    return write_report(0)


def write_report(code: int) -> int:
    PROC.mkdir(exist_ok=True)
    (PROC / "vol2_series.txt").write_text("\n".join(LINES) + "\n", encoding="utf-8", newline="\n")
    return code


if __name__ == "__main__":
    sys.exit(main())
