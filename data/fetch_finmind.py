#!/usr/bin/env python3
"""Rebuild data/raw/ from FinMind and verify it against data/raw_manifest.json (run from the repository root).

FinMind's licence forbids redistributing raw data, so data/raw/ and the labs' data/ folders are git-ignored. The
manifest records, for every raw file, the FinMind query that produced it, the columns kept, any row filter, the row
count and a SHA-256 of the file. A re-fetch must reproduce the file byte for byte (a back-adjusted entry: within the
tolerance below); if FinMind has revised its data the new file is written next to the old path as <name>.new and the
script exits with status 1, so the book's numbers never change silently.

A fetch never stops at the first failing entry (for example a dataset that your FinMind plan does not cover, a
network timeout or a dropped connection): any exception is logged with its type and message, the run goes on, and a
summary of the failed entries is printed at the end with exit status 1. An answer with no rows where the manifest
expects rows counts as failed too (usually the plan or the dataset access, not a revision of the data). The run pauses
after a failure as after a success, and stops early, with the summary, after 25 failures in a row or when FinMind
reports that the request quota ("upper limit") is used up. Re-run to retry; entries that already match are skipped.
--verify and --add behave as before.

    export FINMIND_TOKEN=...                     # your FinMind API token
    uv run python data/fetch_finmind.py                # fetch missing or changed files, verify all
    uv run python data/fetch_finmind.py --verify       # verify local files only (no network)
    uv run python data/fetch_finmind.py --only 00679B  # restrict to manifest paths containing a substring
    uv run python data/fetch_finmind.py --exclude sectors_close/   # skip paths containing a substring (repeatable),
                                                       # e.g. on FinMind's free plan, which lacks that dataset
                                                       # (and vol4_settlement/, an optional Backer cross-check)
    uv run python data/make_lab_data.py                # then rebuild every lab's data/ folder (needs data/raw/*.csv,
                                                       # lm06/ and sectors/; uses sectors_close/ when present)

--verify accepts a missing file in an OPTIONAL folder (vol4_settlement/: a cross-check that vol4_series.py skips when
the file is absent), so a checkout without it still passes --verify; a present file must match like any other.

Register a new raw file (after verifying it with data/check_chunk.py). --add re-fetches the query (it needs
FINMIND_TOKEN) and refuses to register it unless the result matches the file (byte for byte, or for --adjusted as
below): FinMind's labels differ between instruments, so a filter copied from another entry can drop every row.
--no-check skips the test fetch for a
session without API access; run the full fetch in a clean checkout before relying on such an entry.

    uv run python data/fetch_finmind.py --add TX__2025-04-01__2025-10-31.csv --dataset TaiwanFuturesDaily --data-id TX \
        --start 2025-04-01 --end 2025-10-31 --filter trading_session=^position$ --filter 'contract_date=^\\d{6}$'

Volume IV's intraday series (one request per day, 5,648 days) are not in this manifest: data/fetch_intraday.py
downloads them into data/raw/intraday/ with its own manifest, data/raw_intraday_manifest.json (saved under this
script's lock), and --verify here does not look at them.

A back-adjusted column (USStockPrice's Adj_Close) is rebuilt by FinMind backward from the latest day at every
retrieval: the next distribution rescales the whole column, and even without one the factor jitters enough to flip a
value sitting on a half cent, so such a file cannot be reproduced byte for byte. Register it with --adjusted <column>
(an entry with "adjusted" in the manifest; the file must keep its close column): every other field must then match
exactly, the adjusted column must follow the close within three cent-rounding allowances on every day that is not a
registered ex-date, and the window's distribution yield (the sum over days of the adjusted log return minus the
close's) must agree within the rounding of its two end values. Only the ex-dates and that yield are stored, never a
price. A re-fetch that passes is accepted, written and listed at the end of the run.

    uv run python data/fetch_finmind.py --add QQQ__us_2022.csv --dataset USStockPrice --data-id QQQ \
        --start 2021-12-30 --end 2023-01-03 --map adj_close=Adj_Close --map close=Close --adjusted adj_close

Columns are kept under the FinMind names unless mapped with --map out=source (for example
--map cash_dividend=stock_and_cache_dividend). A new daily series can be one file: the API returns the whole
window in one query. Some intraday datasets answer one day per request.

A dataset that accepts only a start date (TaiwanStockEvery5SecondsIndex answers "we only send one day data, so
end_date parameter need be none") is registered by leaving out --end: the manifest entry then has "end_date": null and
the request carries no end_date, so the response is that one day. Always pass --data-id: without it the request returns
every series of the day (about 200,000 rows). --filter then keeps the one row you need:

    uv run python data/fetch_finmind.py --add sectors_close/Semiconductor__2025-06-11.csv \
        --dataset TaiwanStockEvery5SecondsIndex --data-id Semiconductor --start 2025-06-11 \
        --filter time=^13:30:00$ --filter kind=^twse$
"""
import argparse
import contextlib
import csv
import hashlib
import io
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from itertools import pairwise
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
MANIFEST = ROOT / "data" / "raw_manifest.json"
LOCK = ROOT / "data" / "raw_manifest.lock"
API ="https://api.finmindtrade.com/api/v4/data"
PAUSE = 0.7                                                # seconds between requests, far below the hourly API limit
MAX_CONSECUTIVE_FAILURES = 25
LAB_INPUTS = ("lm06/", "sectors/", "vol3/", "vol4/")      # folders make_lab_data.py needs, besides the top level
OPTIONAL = ("vol4_settlement/",)   # cross-checks their script skips when absent: --verify accepts them missing

def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def load_manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {"files": []}

def save_manifest(m):
    m["files"].sort(key=lambda e: e["path"])
    tmp = MANIFEST.with_name(MANIFEST.name + ".tmp")
    tmp.write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, MANIFEST)                              # a reader never sees a half-written manifest

@contextlib.contextmanager
def manifest_lock():
    """Hold data/raw_manifest.lock while a manifest is read, changed and written back. --add here and every manifest
    save of fetch_intraday.py take it, so runs in parallel cannot drop each other's entries."""
    for _ in range(300):                                   # wait up to 30 s for another run to finish writing
        try:
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            time.sleep(0.1)
    else:
        raise SystemExit(f"nothing written: data/{LOCK.name} exists (fetch_finmind.py --add or fetch_intraday.py is "
                         "writing a manifest, or delete a stale lock)")
    try:
        yield
    finally:
        os.close(fd)
        LOCK.unlink()

def register(entry):
    """Add or replace one manifest entry under the lock."""
    with manifest_lock():
        m = load_manifest()
        m["files"] = [e for e in m["files"] if e["path"] != entry["path"]] + [entry]
        save_manifest(m)

def fmt(value, kind):
    if kind == "float":
        return repr(float(value))
    if kind == "int":
        return str(int(float(value)))
    return str(value)

def fetch(entry, token):
    params = {"dataset": entry["dataset"], "start_date": entry["start_date"]}
    if entry.get("end_date"):                              # null/absent: the dataset takes a start date only
        params["end_date"] = entry["end_date"]
    if entry.get("data_id"):
        params["data_id"] = entry["data_id"]
    url = API + "?" + urllib.parse.urlencode({**params, "token": token})
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "User-Agent": "calculus-to-kelly"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            payload = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:                    # FinMind explains a refusal in the body (plan, quota, ...)
        body = e.read().decode("utf-8", "replace")[:300]
        raise RuntimeError(f"{entry['path']}: HTTP {e.code} {e.reason}: {body}") from e
    if not isinstance(payload, dict):
        raise TypeError(f"{entry['path']}: unexpected answer from FinMind: {str(payload)[:100]}")
    if payload.get("status") not in (200, None) or "data" not in payload:
        raise RuntimeError(f"{entry['path']}: FinMind returned {payload.get('status')} {payload.get('msg')}")
    return payload["data"]

def render(entry, records):
    cols, kinds = entry["columns"], entry["kinds"]          # columns: {output: source}
    flt = {k: re.compile(v) for k, v in entry.get("filter", {}).items()}
    rows = []
    for rec in records:
        if all(p.search(str(rec.get(k, ""))) for k, p in flt.items()):
            rows.append([fmt(rec[src], kinds[out]) for out, src in cols.items()])
    keys = [list(cols).index(k) for k in entry.get("sort", ["date"])]
    rows.sort(key=lambda r: tuple(r[i] for i in keys))
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(list(cols)); w.writerows(rows)
    return buf.getvalue().encode("utf-8"), len(rows)

ADJ_K = 3     # a day off the registered ex-dates may differ from the close by K times its cent-rounding allowance

def adjusted_parts(data: bytes, column: str, reference: str):
    """The file without the adjusted column (CSV text re-serialized, for a SHA-256 of every other field), the dates,
    and per day d_t = change of ln(adjusted) minus change of ln(reference) with its rounding allowance e_t: half a cent
    on each of the four two-decimal values, 0.005 (1/a_{t-1} + 1/a_t + 1/c_{t-1} + 1/c_t). An adjusted price is the
    reference times a factor that moves only on ex-dates, so d_t is zero up to rounding on every other day. Raises
    ValueError on anything malformed."""
    try:
        rows = list(csv.reader(io.StringIO(data.decode("utf-8"), newline="")))
        j, k = rows[0].index(column), rows[0].index(reference)
        a = [float(r[j]) for r in rows[1:]]
        c = [float(r[k]) for r in rows[1:]]
    except (UnicodeDecodeError, csv.Error, IndexError) as exc:
        raise ValueError(f"malformed file: {exc}") from exc
    if len(a) < 2 or not all(math.isfinite(v) and v > 0 for v in a + c):
        raise ValueError(f"{column} and {reference} need two rows or more of positive numbers")
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerows([r[:j] + r[j + 1:] for r in rows])
    pairs = list(pairwise(zip(a, c, strict=True)))
    d = [math.log(a1 / a0) - math.log(c1 / c0) for (a0, c0), (a1, c1) in pairs]
    e = [0.005 * (1 / a0 + 1 / a1 + 1 / c0 + 1 / c1) for (a0, c0), (a1, c1) in pairs]
    return buf.getvalue().encode("utf-8"), [r[0] for r in rows[2:]], d, e, a

def adjusted_summary(data: bytes, column: str, reference: str = "close"):
    """What --adjusted registers: the SHA-256 of every other field, the ex-dates (days on which the adjusted column
    moves apart from the reference by more than rounding) and the window's total distribution yield, sum of d_t,
    rounded to 1e-9. No price is stored."""
    rest, dates, d, e, _ = adjusted_parts(data, column, reference)
    ex = [t for t, x, y in zip(dates, d, e, strict=True) if abs(x) > y]
    return {"column": column, "reference": reference, "other_sha256": sha256(rest), "ex_dates": ex,
            "distributions": round(math.fsum(d), 9), "k": ADJ_K}

def adjusted_match(entry, data: bytes) -> bool:
    """A back-adjusted file matches its entry when every other field is identical, the adjusted column follows the
    reference within K rounding allowances on every day that is not a registered ex-date (so a changed, copied or
    shifted value is refused), and the window's distribution yield agrees within the rounding of its two end values.
    A later rescaling, or a re-rounding, of the whole column passes."""
    adj = entry.get("adjusted")
    if not adj:
        return False
    try:
        rest, dates, d, e, a = adjusted_parts(data, adj["column"], adj["reference"])
    except ValueError:
        return False
    if sha256(rest) != adj["other_sha256"]:
        return False
    ex = set(adj["ex_dates"])
    if any(abs(x) > adj["k"] * y for t, x, y in zip(dates, d, e, strict=True) if t not in ex):
        return False
    return abs(math.fsum(d) - adj["distributions"]) <= 0.01 * (1 / a[0] + 1 / a[-1]) + 1e-9

def matches(entry, data: bytes) -> bool:
    return sha256(data) == entry["sha256"] or adjusted_match(entry, data)

def verify_local(entry):
    f = RAW / entry["path"]
    return f.exists() and matches(entry, f.read_bytes())

def add(args):
    f = RAW / args.add
    if not f.exists():
        raise SystemExit(f"no such file: data/raw/{args.add}")
    header = next(csv.reader(io.StringIO(f.read_text(encoding="utf-8"))))
    mapping = dict(s.split("=", 1) for s in args.map)
    rows = list(csv.reader(io.StringIO(f.read_text(encoding="utf-8"))))[1:]
    kinds = {}
    for j, c in enumerate(header):
        vals = [r[j] for r in rows]
        if all(re.fullmatch(r"\d{4}-\d{2}-\d{2}", v) for v in vals): kinds[c] = "date"
        elif all(re.fullmatch(r"-?\d+", v) for v in vals): kinds[c] = "int"
        else:
            try: [float(v) for v in vals]; kinds[c] = "float"
            except ValueError: kinds[c] = "str"
    entry = {"path": args.add, "dataset": args.dataset, "data_id": args.data_id, "start_date": args.start,
             "end_date": args.end, "columns": {c: mapping.get(c, c) for c in header}, "kinds": kinds,
             "filter": dict(s.split("=", 1) for s in args.filter), "sort": args.sort or ["date"],
             "rows": len(rows), "sha256": sha256(f.read_bytes())}
    if args.adjusted:
        if args.adjusted not in header or "close" not in header or args.adjusted == "close":
            raise SystemExit(f"not registered: --adjusted needs a column other than close and the close column it is "
                             f"checked against, in data/raw/{args.add}")
        try:
            entry["adjusted"] = adjusted_summary(f.read_bytes(), args.adjusted)
        except ValueError as exc:
            raise SystemExit(f"not registered: {exc}") from exc
    token = os.environ.get("FINMIND_TOKEN")
    if args.no_check:
        print("warning: registered without a test fetch; run fetch_finmind.py in a clean checkout before relying on it")
    elif not token:
        raise SystemExit("not registered: set FINMIND_TOKEN so --add can test-fetch the query (or pass --no-check)")
    else:                                    # the query must rebuild the file (byte for byte, or as --adjusted says)
        data, n = render(entry, fetch(entry, token))
        if not matches(entry, data):
            raise SystemExit(f"not registered: this query re-fetches {n} rows that differ from data/raw/{args.add} "
                             f"({len(rows)} rows); check --filter, --map, --sort and the dates")
    register(entry)
    print(f"registered data/raw/{args.add}: {len(rows)} rows")

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verify", action="store_true", help="check local files against the manifest; no network")
    ap.add_argument("--only", default="", help="only manifest paths containing this substring")
    ap.add_argument("--exclude", action="append", default=[], metavar="SUBSTR",
                    help="skip manifest paths containing this substring (repeatable)")
    ap.add_argument("--add", help="register an existing data/raw file (path relative to data/raw)")
    ap.add_argument("--dataset"); ap.add_argument("--data-id", default="")
    ap.add_argument("--start"); ap.add_argument("--end")
    ap.add_argument("--filter", action="append", default=[], help="column=regex (records must match)")
    ap.add_argument("--map", action="append", default=[], help="output_column=finmind_column")
    ap.add_argument("--sort", action="append", help="sort keys (default: date)")
    ap.add_argument("--no-check", action="store_true", help="--add without test-fetching the query (offline only)")
    ap.add_argument("--adjusted", metavar="COLUMN",
                    help="--add: COLUMN is back-adjusted by FinMind; verify it day by day against close (see above)")
    args = ap.parse_args()
    if args.add:
        return add(args)
    if "" in args.exclude:
        ap.error("--exclude needs a non-empty substring (an empty one matches every path)")
    entries = [e for e in load_manifest()["files"]
               if args.only in e["path"] and not any(x in e["path"] for x in args.exclude)]
    if args.verify:
        absent = {e["path"] for e in entries if e["path"].startswith(OPTIONAL) and not (RAW / e["path"]).exists()}
        bad = [e["path"] for e in entries if e["path"] not in absent and not verify_local(e)]
        for e in entries:
            p = e["path"]
            print(("absent  (optional) " if p in absent else "MISSING/CHANGED " if p in bad else "ok      ") + p)
        sys.exit(1 if bad else 0)
    token = os.environ.get("FINMIND_TOKEN")
    if not token:
        raise SystemExit("set FINMIND_TOKEN to your FinMind API token")
    changed = 0
    fetched: list[str] = []
    rederived: list[str] = []
    failed: list[tuple[str, str]] = []
    run = 0                                                # consecutive failures
    stop_reason = ""
    left = 0
    for k, e in enumerate(entries):
        if verify_local(e):
            print(f"ok      {e['path']}"); continue
        try:
            data, n = render(e, fetch(e, token))
            if n == 0 and e["rows"] > 0:                   # no rows is a refusal, not a revision of the data
                raise RuntimeError(f"{e['path']}: FinMind returned no rows where the manifest expects {e['rows']}; "
                                   "likely cause: your FinMind plan does not cover this dataset, or the token lacks access to it")
        except Exception as exc:  # noqa: BLE001  one bad entry must not stop the run (Ctrl-C still does)
            msg = " ".join(f"{type(exc).__name__}: {exc}".split())
            failed.append((e["path"], msg))
            run += 1
            print(f"FAILED  {e['path']}: {msg}")
            if "upper limit" in msg.lower():
                stop_reason = "FinMind reports that the request quota (upper limit) is used up"
            elif run >= MAX_CONSECUTIVE_FAILURES:
                stop_reason = f"{run} failures in a row"
            if stop_reason:
                left = sum(1 for x in entries[k + 1:] if not verify_local(x))
                break
            time.sleep(PAUSE)                              # a failure costs a request too
            continue
        run = 0
        out = RAW / e["path"]; out.parent.mkdir(parents=True, exist_ok=True)
        if matches(e, data):
            note = ""
            if sha256(data) != e["sha256"]:
                rederived.append(e["path"]); note = "; back-adjusted column re-derived by FinMind, within tolerance"
            out.write_bytes(data); fetched.append(e["path"]); print(f"fetched {e['path']} ({n} rows{note})")
        else:
            Path(str(out) + ".new").write_bytes(data); changed += 1
            print(f"CHANGED {e['path']}: {n} rows vs {e['rows']} in the manifest; written as {out.name}.new")
        time.sleep(PAUSE)                                  # stay far below the hourly API limit
    if stop_reason:
        print(f"\nSTOPPED EARLY: {stop_reason}; {left} further entries were not tried. "
              "Check the plan and token (or wait for the quota to reset) and re-run: matching entries are skipped.")
    if failed:
        print(f"\n{len(failed)} of {len(entries)} entries failed to fetch:")
        for path, msg in failed:
            print(f"  {path}: {msg}")
    problems = []
    if changed:
        problems.append(f"{changed} file(s) differ from the manifest: inspect the .new files before replacing anything")
    if failed:
        problems.append(f"{len(failed)} entries could not be fetched (listed above)")
    if rederived:
        print(f"{len(rederived)} back-adjusted file(s) differ from the registered bytes within tolerance (a later "
              "distribution or a re-rounding; numbers computed from them can differ in their last digits): "
              + ", ".join(rederived))
    if problems:
        sys.exit("; ".join(problems))
    if args.only or args.exclude:
        print(f"{len(entries)} entries selected: {len(fetched)} fetched in this run, {len(entries) - len(fetched)} "
              "already matched; the other manifest entries were left out by --only/--exclude."
              + (" Fetched now:" if fetched else ""))
        for p in fetched:
            print(f"  {p}")
        # make_lab_data.py reads the top level of data/raw, lm06/, sectors/, vol3/ and vol4/ (Volume IV's labs);
        # sectors_close/ only when present; vol4_settlement/ is a cross-check for vol4_series.py only
        need = [e["path"] for e in load_manifest()["files"]
                if ("/" not in e["path"] or e["path"].startswith(LAB_INPUTS)) and not verify_local(e)]
        if need:
            print(f"make_lab_data.py needs {len(need)} more files (data/raw/*.csv, lm06/, sectors/, vol3/, vol4/): "
                  "run fetch_finmind.py with no --only and no --exclude (on the free plan: --exclude sectors_close/ "
                  "--exclude vol4_settlement/ only) before it.")
        else:
            print("make_lab_data.py has every file it needs; next: uv run python data/make_lab_data.py")
    else:
        print("data/raw matches the manifest; next: uv run python data/make_lab_data.py")

if __name__ == "__main__":
    main()
