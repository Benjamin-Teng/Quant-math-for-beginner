#!/usr/bin/env python3
"""Download Volume IV's intraday FinMind series one day per request, with their own manifest (run from the repo root).

FinMind serves these datasets one day per request (a request with an end_date answers HTTP 400 "we only send one day
data"), so they cannot live in data/raw_manifest.json, whose entries are one request each and are all checked by
`fetch_finmind.py --verify` and `./build.sh --data`. This script keeps data/raw_intraday_manifest.json instead (one
entry per line and per day: path, dataset, data_id, date, rows, sha256, retrieved). The build reads these files only
through data/vol4_rv.py, which rebuilds its output only from a complete download.

Series:
  taiex5s  TaiwanVariousIndicators5Seconds (Free, no data_id): TAIEX every 5 seconds from 2014-12-29 (every minute to
           2011-01-14, then every 15 and 10 seconds), on every TAIEX trading day 2005-01-03 .. 2026-10-08, the
           calendar of the raw TAIEX price files (data/raw/vol3/ and data/raw/sectors/): 5,351 days, about 310 MB.
  tx1m     TaiwanFuturesKBar (Sponsor) data_id TX, calendar 2025: 1-minute bars of every listed month and spread. A
           calendar date D holds 00:00-04:59 of the night session that began on D-1 and the 08:45-13:45 and 15:00-23:59
           sessions of D, so the days are the trading days plus each calendar day after one (Saturdays, the first day of
           a holiday): 297 days.
Files are data/raw/intraday/<series>/<year>/<date>.csv, exactly as returned: FinMind's columns in its order, every
value as printed in its JSON. data/raw/ is git-ignored (FinMind's licence forbids redistributing raw data).

    export FINMIND_TOKEN=...
    uv run python data/fetch_intraday.py --dry-run             # what a fetch would request, the calls and the time
    uv run python data/fetch_intraday.py --series taiex5s      # T5S only (a Free plan), then --check
    uv run python data/fetch_intraday.py                       # both series (tx1m needs the Sponsor plan)
    uv run python data/fetch_intraday.py --series tx1m --from 2025-06-01 --to 2025-06-30   # part of one series
    uv run python data/fetch_intraday.py --verify              # every listed file against the manifest; no network
    uv run python data/fetch_intraday.py --check               # the per-day checks below; no network

A fetch skips days already listed whose file matches the manifest and logs every request to
data/raw/intraday/fetch_intraday.log. It saves the manifest every 25 days and on exit, each time merging its new
entries into the manifest on disk under fetch_finmind.py's lock, so runs in parallel keep each other's entries. When
FinMind answers that the hourly request limit ("upper limit") is reached, it stops with exit status 2 and a resume
message: re-run the same command later. An empty answer on a TAIEX trading day (any taiex5s day; a tx1m day that is a
trading day) is a failure: it is logged FAILED and not listed, so the next run asks again; only a day listed in
EXCEPTIONS as "drop" may be empty. A tx1m day off the trading calendar that answers no rows is listed with rows 0 and
no file. A re-fetched day that differs from its manifest entry is written as <date>.csv.new and the run exits 1
(FinMind revised it: inspect it before replacing anything; data/README.md says how to accept it). Other failures are
logged and the run goes on; it stops after 25 in a row.

--verify checks every listed file's row count and SHA-256, and reports any .new file waiting for a decision and any
file under data/raw/intraday/<series>/ that the manifest does not list (an interrupted run: re-run the fetch).

Per-day checks (--check, after a fetch, and in data/vol4_rv.py):
  taiex5s  every value a decimal number above 0; times strictly increasing and dated on the file's day; rows equal a
           sampling regime (271 = every minute, 1,081 = 15 s, 1,621 = 10 s, 3,241 = 5 s) and the times exactly that
           regime's grid from 09:00:00 to 13:30:00, unless the day is a "grid" exception; the 09:00:00 value equal to
           the previous trading day's TAIEX close and the 13:30:00 value equal to the day's (TaiwanStockPrice, the raw
           price files), within 0.005 (FinMind prints the previous close at 09:00:00; the two catch a misdated day); no
           change in log value between consecutive values from 09:01:00 to 13:29 above MAX_LOG_STEP (by sampling
           regime; the closing step is checked against the close), unless the day is a "steps" exception; no day's values
           between 09:00:00 and 13:30:00 identical to another day's (a copied day, project/PITFALLS.md section 3; a
           copy that kept the right 09:00:00 and 13:30:00 values passes every per-day check). A warning, which fails
           nothing: values unchanged for more than 10 minutes before 13:25:00 (a frozen feed; the 13:25-13:30 closing
           call auction is left out). The report gives each regime's first and last day (the switches) and the
           largest change in log value seen.
  tx1m     no duplicate (contract, minute); every row dated on the file's day; the last regular-session bar
           (08:45-13:45) of the near month against TaiwanFuturesDaily's close (data/raw/vol4/TX__*.csv), reported as
           an agreement rate, not a stop.
A "drop" exception may be empty or fail any check: its problems are printed as notes, and vol4_rv.py leaves it out.
Problems go to stderr, summaries to stdout.
"""
import argparse
import csv
import datetime as dt
import hashlib
import io
import itertools
import json
import math
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import NamedTuple

import fetch_finmind as ff

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTRADAY = RAW / "intraday"
MANIFEST = ROOT / "data" / "raw_intraday_manifest.json"
LOG = INTRADAY / "fetch_intraday.log"
TX_DAILY = RAW / "vol4" / "TX__1998-07-21__2026-10-16.csv"
API = "https://api.finmindtrade.com/api/v4/data"
PAUSE = 0.7                    # seconds between requests: about 3,600 an hour, inside the Sponsor plan's 6,000
SAVE_EVERY = 25                # days between manifest saves
MAX_CONSECUTIVE_FAILURES = 25
SERIES = {
    "taiex5s": {"dataset": "TaiwanVariousIndicators5Seconds", "data_id": "", "first": "2005-01-03",
                "last": "2026-10-08"},
    "tx1m": {"dataset": "TaiwanFuturesKBar", "data_id": "TX", "first": "2025-01-01", "last": "2025-12-31"},
}
COLUMNS = {"taiex5s": ["date", "TAIEX"],              # as FinMind returns them; a change stops the fetch
           "tx1m": ["date", "futures_id", "contract_date", "minute", "open", "high", "low", "close", "volume"]}
REGIMES = {271: 60, 1081: 15, 1621: 10, 3241: 5}     # rows per day -> seconds between values, 09:00:00 to 13:30:00
OPEN_S, CLOSE_S = 9 * 3600, 13 * 3600 + 30 * 60
STEP_FROM_S = OPEN_S + 60      # 09:01:00: the index takes the first seconds of trading to reflect the open
# bound on |change in log value| between consecutive values from 09:01:00 to 13:29:xx, by seconds between values
# (the step into 13:30:00 is the closing auction's, checked against the day's close instead); `--check` prints the largest
# step seen per run; a real larger step is a "steps" exception
MAX_LOG_STEP = {5: 0.015, 10: 0.015, 15: 0.015, 60: 0.03}
AUCTION_S = 13 * 3600 + 25 * 60   # 13:25:00, start of the closing call auction
FROZEN_S = 600                 # warn when the values stay unchanged longer than this before 13:25:00
TOLERANCE = Decimal("0.005")
# Days that break a rule, by series: date -> (kind, the reason found when the day was inspected). None so far.
#   "grid"  the rows match no sampling regime but every value check passes: the day is kept, its row count and time
#           grid are not checked, and vol4_rv.py uses the grid times present
#   "drop"  the day is unusable (no rows, or values that fail a check): its problems are notes, vol4_rv.py leaves it out
#   "steps" a step above MAX_LOG_STEP was inspected and is real (a market move): the day is kept, the bound waived
EXCEPTIONS: dict[str, dict[str, tuple[str, str]]] = {"taiex5s": {}, "tx1m": {}}
KINDS = ("grid", "drop", "steps")

class QuotaReached(Exception):
    """FinMind's hourly request limit."""

def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def kind(series: str, date: str) -> str:
    """The day's exception kind, "" when it is not an exception."""
    k, why = EXCEPTIONS[series].get(date, ("", ""))
    if k and (k not in KINDS or not why):
        raise SystemExit(f"EXCEPTIONS[{series!r}][{date!r}]: the kind must be one of {KINDS}, with a reason")
    return k

def hms(s: int) -> str:
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"

# ---------------------------------------------------------------- calendars

def taiex_closes() -> dict[str, str]:
    """TAIEX closes of TaiwanStockPrice by date, as printed, from the raw price files of fetch_finmind.py."""
    files = [RAW / "vol3" / "TAIEX__2003-01-01__2007-07-01.csv", *sorted((RAW / "sectors").glob("TAIEX__*.csv"))]
    if not files[0].exists() or len(files) < 2:
        raise SystemExit("missing data/raw/vol3/ or data/raw/sectors/ TAIEX files: run uv run python "
                         "data/fetch_finmind.py first (they give the calendar and the closes)")
    closes: dict[str, str] = {}
    for f in files:
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if closes.setdefault(r["date"], r["close"]) != r["close"]:
                    raise SystemExit(f"TAIEX files disagree on {r['date']}: run fetch_finmind.py --verify")
    return closes

def previous_days(closes: dict[str, str]) -> dict[str, str]:
    """Each TAIEX trading day -> the trading day before it (the raw price files start on 2003-01-02)."""
    days = sorted(closes)
    return dict(zip(days[1:], days))

def calendar(series: str, closes: dict[str, str]) -> list[str]:
    s = SERIES[series]
    trading = sorted(closes)
    if series == "taiex5s":
        days = set(trading)
    else:                                                # the night session's early hours fall on the next day
        days = set(trading) | {(dt.date.fromisoformat(d) + dt.timedelta(days=1)).isoformat() for d in trading}
    return sorted(d for d in days if s["first"] <= d <= s["last"])

def rel_path(series: str, date: str) -> str:
    return f"intraday/{series}/{date[:4]}/{date}.csv"

def series_of(entry: dict) -> str:
    return entry["path"].split("/")[1]

# ---------------------------------------------------------------- manifest and log

def load_manifest() -> dict[str, dict]:
    if not MANIFEST.exists():
        return {}
    return {e["path"]: e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["files"]}

def write_manifest(entries: dict[str, dict]) -> None:
    """One entry per line, sorted by path; written atomically."""
    lines = [json.dumps(entries[p], ensure_ascii=False) for p in sorted(entries)]
    text = '{\n "files": [\n  ' + ",\n  ".join(lines) + "\n ]\n}\n" if lines else '{\n "files": []\n}\n'
    tmp = MANIFEST.with_name(MANIFEST.name + ".tmp")
    tmp.write_bytes(text.encode("utf-8"))
    os.replace(tmp, MANIFEST)

def save_manifest(added: dict[str, dict]) -> None:
    """Merge this run's new entries into the manifest on disk, under fetch_finmind.py's lock."""
    if not added:
        return
    with ff.manifest_lock():
        entries = load_manifest()
        entries.update(added)
        write_manifest(entries)

def log(msg: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8", newline="\n") as f:
        f.write(f"{dt.datetime.now().isoformat(timespec='seconds')} {msg}\n")

def matches(entry: dict) -> bool:
    f = RAW / entry["path"]
    if entry["rows"] == 0:
        return not f.exists()
    return f.exists() and sha256(f.read_bytes()) == entry["sha256"]

# ---------------------------------------------------------------- fetch

def get_day(series: str, date: str, token: str) -> list[dict]:
    """One day's records, every value kept as printed in FinMind's JSON (numbers as strings)."""
    s = SERIES[series]
    params = {"dataset": s["dataset"], "start_date": date}
    if s["data_id"]:
        params["data_id"] = s["data_id"]
    url = API + "?" + urllib.parse.urlencode({**params, "token": token})
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "User-Agent": "calculus-to-kelly"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            body, code = r.read().decode("utf-8"), r.status
    except urllib.error.HTTPError as e:                  # FinMind explains a refusal in the body
        body, code = e.read().decode("utf-8", "replace"), e.code
    try:
        payload = json.loads(body, parse_float=str, parse_int=str)
    except json.JSONDecodeError:
        payload = None
    if not isinstance(payload, dict):
        raise TypeError(f"HTTP {code}: unexpected answer {body[:100]!r}")
    msg = str(payload.get("msg", ""))                    # never log the whole body: it can echo the token's tail
    status = str(payload.get("status", code))
    if "upper limit" in msg.lower() or status == "402" or code == 402:
        raise QuotaReached(f"HTTP {code} status {status}: {msg}")
    if code != 200 or status != "200" or not isinstance(payload.get("data"), list):
        raise RuntimeError(f"HTTP {code} status {status}: {msg}")
    return payload["data"]

def render(series: str, records: list[dict]) -> bytes:
    if not records:
        return b""
    header = list(records[0])
    if header != COLUMNS[series] or any(list(r) != header for r in records):
        raise RuntimeError(f"columns {header} differ from {COLUMNS[series]} or between rows")
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows([["" if r[k] is None else r[k] for k in header] for r in records])
    return buf.getvalue().encode("utf-8")

def fetch(args, entries: dict[str, dict], plan: dict[str, list[str]], closes: dict[str, str]) -> int:
    token = os.environ.get("FINMIND_TOKEN")
    if not token:
        raise SystemExit("set FINMIND_TOKEN to your FinMind API token")
    today = dt.date.today().isoformat()
    added: dict[str, dict] = {}                          # entries new in this run, merged into the manifest on save
    done = changed = failed = run = 0
    total = sum(len(v) for v in plan.values())
    status = 0
    log(f"start: {total} days to request ({', '.join(f'{s} {len(v)}' for s, v in plan.items())})")
    try:
        for series, days in plan.items():
            s = SERIES[series]
            for date in days:
                path = rel_path(series, date)
                try:
                    records = get_day(series, date, token)
                    if not records and date in closes and kind(series, date) != "drop":
                        raise RuntimeError("no rows on a TAIEX trading day (often temporary): not listed; re-run to "
                                           "retry, or list the day as a drop exception once it is known to be empty")
                    data = render(series, records)
                except QuotaReached as exc:
                    left = total - done - failed
                    log(f"STOP quota {series} {date}: {exc}")
                    print(f"\nSTOPPED: FinMind's hourly request limit is reached ({exc}). {done} days fetched in "
                          f"this run, {left} left. Re-run the same command later: listed days are skipped.",
                          file=sys.stderr)
                    return 2
                except Exception as exc:  # noqa: BLE001  one bad day must not stop the run (Ctrl-C still does)
                    failed += 1
                    run += 1
                    msg = " ".join(f"{type(exc).__name__}: {exc}".split())
                    log(f"FAILED {series} {date}: {msg}")
                    print(f"FAILED  {path}: {msg}", file=sys.stderr)
                    if run >= MAX_CONSECUTIVE_FAILURES:
                        print(f"\nSTOPPED: {run} failures in a row; check the network, the token and the plan, then "
                              "re-run.", file=sys.stderr)
                        return 1
                    time.sleep(args.pause)
                    continue
                run = 0
                n = data.count(b"\n") - 1 if data else 0
                digest = sha256(data) if data else None
                out = RAW / path
                old = entries.get(path)
                if old is not None and (old["rows"], old["sha256"]) != (n, digest):
                    out.parent.mkdir(parents=True, exist_ok=True)
                    Path(str(out) + ".new").write_bytes(data)
                    changed += 1
                    log(f"CHANGED {series} {date}: {n} rows vs {old['rows']} listed; written as {out.name}.new")
                    print(f"CHANGED {path}: {n} rows vs {old['rows']} in the manifest; written as {out.name}.new",
                          file=sys.stderr)
                else:
                    if data:
                        out.parent.mkdir(parents=True, exist_ok=True)
                        out.write_bytes(data)
                    if old is None:                      # a listed day re-fetched unchanged keeps its entry
                        entries[path] = added[path] = {"path": path, "dataset": s["dataset"], "data_id": s["data_id"],
                                                       "date": date, "rows": n, "sha256": digest, "retrieved": today}
                    log(f"{series} {date} rows={n}" + (f" sha256={digest[:12]}" if digest else " (no rows, no file)"))
                    print(f"fetched {path} ({n} rows)" if n else f"empty   {date} ({series}: no rows, listed)")
                done += 1
                if done % SAVE_EVERY == 0:
                    save_manifest(added)
                time.sleep(args.pause)
    finally:
        save_manifest(added)
        log(f"end: {done} days requested, {failed} failed, {changed} changed")
    if changed:
        print(f"\n{changed} day(s) differ from the manifest: inspect the .new files before replacing anything "
              "(data/README.md)", file=sys.stderr)
        status = 1
    if failed:
        print(f"\n{failed} day(s) could not be fetched (data/raw/intraday/fetch_intraday.log): re-run to retry",
              file=sys.stderr)
        status = 1
    return status

# ---------------------------------------------------------------- checks

def seconds(hms_: str) -> int:
    h, m, s = hms_.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)

def read_taiex5s(text: str, date: str) -> tuple[list[int], list[str]]:
    """Times (seconds after midnight) and values as printed; ValueError when the file is malformed."""
    rows = list(csv.reader(io.StringIO(text)))
    if not rows or rows[0] != COLUMNS["taiex5s"]:
        raise ValueError(f"header {rows[:1]}")
    secs, vals = [], []
    for stamp, v in rows[1:]:
        day, _, clock = stamp.partition(" ")
        if day != date:
            raise ValueError(f"row dated {stamp}")
        secs.append(seconds(clock))
        vals.append(v)
    return secs, vals

class DayCheck(NamedTuple):
    problems: list[str]
    warnings: list[str]
    step: int                  # seconds between values; 0 when the rows match no regime
    digest: str                # SHA-256 of the values between the first and the last, to find a copied day
    move: float                # largest |change in log value| between consecutive values from 09:01:00
    move_at: str               # the time of the later value

def check_taiex5s_day(date: str, text: str, close: str | None, prev_close: str | None, kind_: str = "") -> DayCheck:
    """One day's problems and warnings. close and prev_close: TaiwanStockPrice's TAIEX close of the day and of the
    trading day before (None when the raw price files lack it); kind_: the day's exception kind."""
    try:
        secs, vals = read_taiex5s(text, date)
    except ValueError as exc:
        return DayCheck([f"malformed: {exc}"], [], 0, "", 0.0, "")
    digest = sha256(",".join(vals[1:-1]).encode())      # without 09:00:00 and 13:30:00, which a copy could keep
    problems: list[str] = []
    warnings: list[str] = []
    if any(b <= a for a, b in itertools.pairwise(secs)):
        problems.append("times not strictly increasing")
    step = REGIMES.get(len(secs), 0)
    if kind_ != "grid":
        if not step:
            problems.append(f"{len(secs)} rows match no regime {sorted(REGIMES)}")
        elif secs != list(range(OPEN_S, CLOSE_S + 1, step)):
            problems.append(f"times are not the {step}-second grid from 09:00:00 to 13:30:00")
    nums: list[Decimal] = []
    bad: list[str] = []
    for t, v in zip(secs, vals):
        try:
            x = Decimal(v)
        except InvalidOperation:
            x = Decimal("NaN")
        if not x.is_finite() or x <= 0:
            bad.append(f"{hms(t)} {v!r}")
        nums.append(x)
    if bad:
        problems.append(f"{len(bad)} values are not decimal numbers above 0 (first: {bad[0]})")
        return DayCheck(problems, warnings, step, digest, 0.0, "")
    value = dict(zip(secs, nums))
    for t, ref, what in ((OPEN_S, prev_close, "the previous trading day's TAIEX close"),
                         (CLOSE_S, close, "the day's TAIEX close")):
        v = value.get(t)
        if v is None:
            problems.append(f"no {hms(t)} value")
        elif ref is None:
            problems.append(f"the raw price files lack {what}")
        elif abs(v - Decimal(ref)) > TOLERANCE:
            problems.append(f"{hms(t)} value {v} differs from {what} {ref}")
    move, move_at = 0.0, ""
    lv = [math.log(x) for x in nums]
    for (t0, a), (t1, b) in itertools.pairwise(zip(secs, lv)):
        if t0 >= STEP_FROM_S and t1 < CLOSE_S and abs(b - a) > move:
            move, move_at = abs(b - a), hms(t1)
    bound = MAX_LOG_STEP.get(step, max(MAX_LOG_STEP.values()))
    if move > bound and kind_ != "steps":
        problems.append(f"change in log value {move:.4f} at {move_at}, above the bound {bound}")
    start = 0
    for k in range(1, len(nums) + 1):
        if k == len(nums) or nums[k] != nums[start]:
            span = min(secs[k - 1], AUCTION_S) - secs[start]
            if span > FROZEN_S:
                warnings.append(f"values unchanged for {span / 60:.1f} minutes, {hms(secs[start])} to "
                                f"{hms(secs[k - 1])}")
            start = k
    return DayCheck(problems, warnings, step, digest, move, move_at)

class Checked(NamedTuple):
    failing: list[str]         # dates that fail a check ("drop" exceptions never do)
    summary: list[str]         # the lines printed to stdout

def check(entries: dict[str, dict], series_list: list[str], closes: dict[str, str]) -> int:
    bad = 0
    for series in series_list:
        cal = calendar(series, closes)
        listed = {e["date"]: e for e in entries.values() if series_of(e) == series}
        print(f"\n[{series}] {len(listed)} of the {len(cal)} calendar days listed in the manifest "
              f"({cal[0]} .. {cal[-1]}); {sum(1 for e in listed.values() if e['rows'] == 0)} with no rows")
        bad += len((check_taiex5s if series == "taiex5s" else check_tx1m)(listed, closes).failing)
    return 1 if bad else 0

def report(series: str, listed: dict[str, dict], problems: dict[str, list[str]], lines: list[str]) -> Checked:
    """Print the summary to stdout and every problem to stderr; count the failing dates."""
    drops = sum(1 for d in listed if kind(series, d) == "drop")
    for d, (k, why) in sorted(EXCEPTIONS[series].items()):
        lines.append(f"  exception {d} ({k}): {why}")
    lines.append(f"  {len(listed) - drops - len(problems)} of {len(listed)} listed days pass every check, "
                 f"{len(problems)} fail, {drops} dropped (exceptions)")
    print("\n".join(lines))
    for d in sorted(problems):
        for p in problems[d]:
            print(f"  FAIL {series} {d}: {p}", file=sys.stderr)
    return Checked(sorted(problems), lines)

def check_taiex5s(listed: dict[str, dict], closes: dict[str, str]) -> Checked:
    prev = previous_days(closes)
    problems: dict[str, list[str]] = {}
    notes: list[str] = []
    warnings: list[str] = []
    seen: dict[str, str] = {}
    regime: dict[int, list[str]] = {}
    largest = (0.0, "", "")
    for date in sorted(listed):
        e = listed[date]
        k = kind("taiex5s", date)
        found: list[str] = []
        if e["rows"] == 0:
            if k != "drop":
                found.append("listed with no rows: delete its line from the manifest and re-run the fetch")
        elif not matches(e):
            found.append("file missing or changed (run --verify)")
        else:
            c = check_taiex5s_day(date, (RAW / e["path"]).read_text(encoding="utf-8"), closes.get(date),
                                  closes.get(prev.get(date, "")), k)
            found += c.problems
            if c.digest and c.digest in seen:
                found.append(f"values identical to {seen[c.digest]}")
            seen.setdefault(c.digest, date)
            warnings += [f"{date}: {w}" for w in c.warnings]
            if k != "drop":
                regime.setdefault(c.step, []).append(date)
                largest = max(largest, (c.move, date, c.move_at))
        if k == "drop":
            notes += [f"  note {date} (dropped): {p}" for p in found]
        elif found:
            problems[date] = found
    lines: list[str] = []
    for step in sorted(regime, reverse=True):
        ds = regime[step]
        lines.append(f"  {f'every {step} s' if step else 'no regime (grid exceptions)'}: {len(ds)} days, "
                     f"{ds[0]} .. {ds[-1]}")
    lines.append(f"  largest change in log value between consecutive values from 09:01:00: {largest[0]:.5f} "
                 f"({largest[1]} {largest[2]}; bound {MAX_LOG_STEP})")
    lines.append(f"  {len(warnings)} warnings (values unchanged for more than {FROZEN_S // 60} minutes before "
                 "13:25:00)" + (":" if warnings else ""))
    lines += [f"    {w}" for w in warnings] + notes
    return report("taiex5s", listed, problems, lines)

def check_tx1m(listed: dict[str, dict], closes: dict[str, str]) -> Checked:
    daily: dict[str, tuple[str, str]] = {}               # date -> (near month, its regular-session close)
    lines: list[str] = []
    if TX_DAILY.exists():
        with open(TX_DAILY, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r["date"] not in daily:               # rows are sorted by date and contract: the first is nearest
                    daily[r["date"]] = (r["contract_date"], r["close"])
    else:
        lines.append(f"  {TX_DAILY.relative_to(ROOT)} missing: the close comparison is skipped (run fetch_finmind.py)")
    problems: dict[str, list[str]] = {}
    notes: list[str] = []
    agree, differ, night = 0, [], []
    for date in sorted(listed):
        e = listed[date]
        k = kind("tx1m", date)
        found: list[str] = []
        if e["rows"] == 0:
            if date in closes and k != "drop":
                found.append("listed with no rows on a trading day: delete its line from the manifest and re-run")
        elif not matches(e):
            found.append("file missing or changed (run --verify)")
        else:
            with open(RAW / e["path"], newline="", encoding="utf-8") as fh:
                rows = list(csv.DictReader(fh))
            keys = [(r["contract_date"], r["minute"]) for r in rows]
            if len(set(keys)) != len(keys):
                found.append(f"{len(keys) - len(set(keys))} duplicate (contract, minute) rows")
            if any(r["date"] != date for r in rows):
                found.append("rows dated on another day")
            if date not in closes:
                night.append(f"{date} ({len(rows)} rows, {min(x[1] for x in keys)}-{max(x[1] for x in keys)})")
            if date in daily and Decimal(daily[date][1]) > 0:
                c, close = daily[date]
                bars = sorted((r["minute"], r["close"]) for r in rows
                              if r["contract_date"] == c and "08:45:00" <= r["minute"] <= "13:45:00")
                if bars and Decimal(bars[-1][1]) == Decimal(close):
                    agree += 1
                else:
                    differ.append(f"{date} {c}: last bar {bars[-1] if bars else None}, daily close {close}")
        if k == "drop":
            notes += [f"  note {date} (dropped): {p}" for p in found]
        elif found:
            problems[date] = found
    n = agree + len(differ)
    lines.append(f"  days with rows off the trading calendar (night-session tails): {len(night)}"
                 + (": " + "; ".join(night) if night else ""))
    if n:
        lines.append(f"  near month's last regular-session bar = TaiwanFuturesDaily close on {agree} of {n} days "
                     f"({agree / n:.1%})" + (":" if differ else ""))
        lines += [f"    {x}" for x in differ]
    return report("tx1m", listed, problems, lines + notes)

# ---------------------------------------------------------------- main

def verify(entries: dict[str, dict], series_list: list[str]) -> int:
    sel = [e for e in entries.values() if series_of(e) in series_list]
    bad = [e["path"] for e in sel if not matches(e)]
    pending, unlisted = [], []
    for series in series_list:
        for f in sorted((INTRADAY / series).rglob("*")):
            rel = f.relative_to(RAW).as_posix()
            if not f.is_file():
                continue
            if f.name.endswith(".csv.new"):
                pending.append(rel)
            elif rel not in entries:
                unlisted.append(rel)
    for p in bad:
        print(f"MISSING/CHANGED {p}", file=sys.stderr)
    for p in pending:
        print(f"PENDING {p}: FinMind revised this day; accept or discard it (data/README.md)", file=sys.stderr)
    for p in unlisted:
        print(f"UNLISTED {p}: not in the manifest (an interrupted run); re-run the fetch, which lists or replaces a "
              "calendar day's file", file=sys.stderr)
    print(f"{len(sel) - len(bad)} of {len(sel)} listed days match the manifest "
          f"({sum(1 for e in sel if e['rows'] == 0)} of them listed with no rows and no file); "
          f"{len(pending)} .new files pending; {len(unlisted)} files not listed")
    return 1 if bad or pending or unlisted else 0

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--verify", action="store_true", help="every listed file against the manifest; no network")
    mode.add_argument("--check", action="store_true", help="the per-day checks; no network")
    mode.add_argument("--dry-run", action="store_true", help="list what a fetch would request; no network")
    ap.add_argument("--series", action="append", choices=sorted(SERIES), help="restrict to a series (repeatable)")
    ap.add_argument("--from", dest="start", default="", help="first calendar date (YYYY-MM-DD)")
    ap.add_argument("--to", dest="end", default="9999", help="last calendar date (YYYY-MM-DD)")
    ap.add_argument("--dates", default="", help="comma-separated dates to fetch (each must be in the calendar)")
    ap.add_argument("--pause", type=float, default=PAUSE, help=f"seconds between requests (default {PAUSE})")
    args = ap.parse_args()
    series_list = args.series or list(SERIES)
    entries = load_manifest()
    if args.verify:
        return verify(entries, series_list)
    closes = taiex_closes()
    if args.check:
        return check(entries, series_list, closes)
    wanted = set(args.dates.split(",")) - {""}
    plan: dict[str, list[str]] = {}
    for series in series_list:
        cal = calendar(series, closes)
        if wanted - set(cal) and len(series_list) == 1:
            raise SystemExit(f"not in the {series} calendar: {sorted(wanted - set(cal))}")
        days = [d for d in cal if args.start <= d <= args.end and (not wanted or d in wanted)]
        plan[series] = [d for d in days if not (rel_path(series, d) in entries
                                                and matches(entries[rel_path(series, d)]))]
        print(f"{series}: {len(days)} calendar days selected, {len(days) - len(plan[series])} already listed and "
              f"matching, {len(plan[series])} to request"
              + (f" ({plan[series][0]} .. {plan[series][-1]})" if plan[series] else ""))
    calls = sum(len(v) for v in plan.values())
    if args.dry_run:
        print(f"{calls} API calls; at {args.pause} s between requests plus about 0.3 s each, about "
              f"{calls * (args.pause + 0.3) / 60:.0f} minutes ({3600 / (args.pause + 0.3):.0f} calls an hour); "
              f"at a Free plan's 600 calls an hour, about {calls / 600:.1f} hours, re-running after each quota stop")
        return 0
    if not calls:
        print("nothing to fetch")
    status = fetch(args, entries, plan, closes) if calls else 0
    if status == 2:                                      # quota: resume later, the checks would be partial anyway
        return 2
    return max(status, check(load_manifest(), series_list, closes))

if __name__ == "__main__":
    sys.exit(main())
