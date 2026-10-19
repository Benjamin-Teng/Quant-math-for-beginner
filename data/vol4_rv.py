"""LM26's realized variance: per-day statistics of TAIEX every 5 seconds (T5S), written to data/derived/vol4_rv.csv.

Input: the taiex5s days of data/raw_intraday_manifest.json (data/fetch_intraday.py; data/raw/intraday/taiex5s/, not
committed) and the TAIEX closes of the raw price files (data/raw/vol3/, data/raw/sectors/). Every day must pass
fetch_intraday.py's per-day checks (its --help lists them), or the script stops with exit status 1 and lists the
failing days on stderr. A day that fetch_intraday.EXCEPTIONS lists as "drop" is left out, its reason in the report.

FinMind's 09:00:00 value is the previous trading day's close, and the index takes the first seconds of trading to
reflect the open, so a grid starting at 09:00:00 would put the overnight gap into its first return. Every grid runs on
the common window 09:30:00 to 13:30:00 instead (240 minutes, which all nine intervals divide), and the gap from the
previous close to 09:30:00 is a column of its own.

Output, committed (the owner's decision of 2026-10-19: per-day statistics only, never intraday prices or returns,
credited to FinMind and TWSE): data/derived/vol4_rv.csv, a comment line crediting the source, then one row per
trading day:
  date
  regime_s       seconds between the day's values (60 to 2011-01-14, then 15, 10, and 5 from 2014-12-29)
  rv_<h>, n_<h>  for the nine intervals h = 5s, 10s, 15s, 30s, 1m, 5m, 10m, 15m and 30m: the sum of squared log
                 returns on the grid 09:30:00, 09:30:00 + h, ..., 13:30:00, and the number of returns (14,400 s / h);
                 both NaN when h is not a multiple of regime_s (finer than the day's sampling, or 15 s under 10-second
                 sampling). On a "grid" exception day a missing grid time merges two returns into one, so n falls short.
  o2             the squared log change from the previous trading day's TAIEX close (TaiwanStockPrice; the checks
                 require FinMind's 13:30:00 value of that day and 09:00:00 value of this one to equal it within 0.005)
                 to the 09:30:00 value. For 2005-01-03 it is 2004-12-31's close, from the raw price files.
The file holds no signed return and no price level. Values carry seven significant digits. Read it with
pl.read_csv(path, comment_prefix="#").

The file is rebuilt only from a complete download (every TAIEX trading day 2005-01-03 .. 2026-10-08 listed, its file
matching the manifest). Otherwise the committed file stays, and the script says why on stderr and exits 0, so
./build.sh --data works without the download. --allow-partial --out <path> computes the days present (a test).

Run:  PYTHONUTF8=1 uv run python data/vol4_rv.py      (report: data/processed/vol4_rv.txt)
"""
import argparse
import math
import sys
from pathlib import Path

import fetch_intraday as fi
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "derived" / "vol4_rv.csv"
REPORT = HERE / "processed" / "vol4_rv.txt"
CREDIT = ("# Derived from FinMind TaiwanVariousIndicators5Seconds and TaiwanStockPrice (TWSE TAIEX); "
          "per-day statistics only")
START_S = 9 * 3600 + 30 * 60   # 09:30:00
WINDOW_S = fi.CLOSE_S - START_S
INTERVALS = [("5s", 5), ("10s", 10), ("15s", 15), ("30s", 30), ("1m", 60), ("5m", 300), ("10m", 600), ("15m", 900),
             ("30m", 1800)]
COLUMNS = ["date", "regime_s", *[f"{k}_{name}" for name, _ in INTERVALS for k in ("rv", "n")], "o2"]

def day_stats(secs: list[int], vals: list[str], prev_close: str | None) -> dict:
    """Per-day statistics of one day's checked values (times in seconds after midnight)."""
    lv = np.log(np.array(vals, dtype=float))
    pos = {s: i for i, s in enumerate(secs)}
    regime = int(np.bincount(np.diff(secs)).argmax())
    row: dict = {"regime_s": regime}
    for name, h in INTERVALS:
        if h % regime:
            row[f"rv_{name}"] = row[f"n_{name}"] = math.nan
            continue
        idx = [pos[t] for t in range(START_S, fi.CLOSE_S + 1, h) if t in pos]
        r = np.diff(lv[idx])
        row[f"rv_{name}"], row[f"n_{name}"] = float(r @ r), len(r)
    i0 = pos.get(START_S)
    row["o2"] = (float(lv[i0]) - math.log(float(prev_close))) ** 2 if i0 is not None and prev_close else math.nan
    return row

def fmt(x) -> str:
    if isinstance(x, float):
        return "NaN" if math.isnan(x) else f"{x:.7g}"
    return str(x)

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--allow-partial", action="store_true", help="compute the days present (needs --out)")
    ap.add_argument("--out", type=Path, default=OUT, help="output CSV (default data/derived/vol4_rv.csv)")
    args = ap.parse_args()
    if args.allow_partial and args.out.resolve() == OUT.resolve():
        ap.error("--allow-partial writes a test file: pass --out outside data/derived/")
    if any(WINDOW_S % h for _, h in INTERVALS):
        raise SystemExit("an interval does not divide the 09:30:00-13:30:00 window")
    closes = fi.taiex_closes()
    prev = fi.previous_days(closes)
    cal = fi.calendar("taiex5s", closes)
    listed = {e["date"]: e for e in fi.load_manifest().values() if fi.series_of(e) == "taiex5s"}
    present = {d: e for d, e in listed.items() if e["rows"] and fi.matches(e)}
    keep = "kept data/derived/vol4_rv.csv" if OUT.exists() else "data/derived/vol4_rv.csv does not exist yet"
    if not present:
        print(f"vol4_rv.py: no T5S download (data/raw/intraday/taiex5s/): {keep}", file=sys.stderr)
        return 0
    missing = [d for d in cal if d not in listed or (listed[d]["rows"] and d not in present)]
    if missing and not args.allow_partial:
        print(f"vol4_rv.py: the T5S download is incomplete ({len(cal) - len(missing)} of {len(cal)} days; run "
              f"uv run python data/fetch_intraday.py --series taiex5s): {keep}", file=sys.stderr)
        return 0
    # a full run checks every listed day (an empty day fails unless it is a "drop" exception)
    checked = fi.check_taiex5s(present if missing else listed, closes)   # summary to stdout, problems to stderr
    if checked.failing:
        print(f"STOP: {len(checked.failing)} T5S days fail the per-day checks (FAIL lines above); "
              f"{args.out.name} not written", file=sys.stderr)
        return 1
    dropped = sorted(d for d in (present if missing else listed) if fi.kind("taiex5s", d) == "drop")
    stats = {}
    for d in sorted(present):
        if d in dropped:
            continue
        secs, vals = fi.read_taiex5s((fi.RAW / present[d]["path"]).read_text(encoding="utf-8"), d)
        stats[d] = day_stats(secs, vals, closes.get(prev.get(d, "")))
    rows = [[d] + [s[c] for c in COLUMNS[1:]] for d, s in sorted(stats.items())]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    text = CREDIT + "\n" + ",".join(COLUMNS) + "\n" + "".join(",".join(fmt(x) for x in r) + "\n" for r in rows)
    args.out.write_bytes(text.encode("utf-8"))
    lines = ["[check]", *checked.summary]
    lines.append(f"[rv] {len(rows)} days {rows[0][0]} .. {rows[-1][0]}" + (" (partial: test days only)" if missing
                 else "") + f"; {len(text):,} bytes -> {args.out.name}; grids 09:30:00 .. 13:30:00")
    for d in dropped:
        lines.append(f"[rv] left out {d}: {fi.EXCEPTIONS['taiex5s'][d][1]}")
    short = [d for d, s in sorted(stats.items())
             if any(not math.isnan(s[f"n_{name}"]) and s[f"n_{name}"] != WINDOW_S // h for name, h in INTERVALS)]
    lines.append(f"[rv] days with a grid return merged over a missing time: {len(short)}"
                 + (f" ({', '.join(short[:10])})" if short else ""))
    no_o2 = [d for d, s in sorted(stats.items()) if math.isnan(s["o2"])]
    lines.append(f"[rv] days without o2: {len(no_o2)}" + (f" ({', '.join(no_o2[:10])})" if no_o2 else ""))
    print("\n".join(lines[len(checked.summary) + 1:]))
    if not missing:
        REPORT.parent.mkdir(exist_ok=True)
        REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
