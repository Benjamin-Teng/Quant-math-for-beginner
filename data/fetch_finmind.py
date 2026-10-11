#!/usr/bin/env python3
"""Rebuild data/raw/ from FinMind and verify it against data/raw_manifest.json (run from the repository root).

FinMind's licence forbids redistributing raw data, so data/raw/ and the labs' data/ folders are git-ignored. The
manifest records, for every raw file, the FinMind query that produced it, the columns kept, any row filter, the row
count and a SHA-256 of the file. A re-fetch must reproduce the file byte for byte; if FinMind has revised its data
the new file is written next to the old path as <name>.new and the script exits with status 1, so the book's numbers
never change silently.

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
    uv run python data/make_lab_data.py                # then rebuild every lab's data/ folder (needs data/raw/*.csv,
                                                       # lm06/ and sectors/; uses sectors_close/ when present)

Register a new raw file (after verifying it with data/check_chunk.py). --add re-fetches the query (it needs
FINMIND_TOKEN) and refuses to register it unless the result matches the file byte for byte: FinMind's labels differ
between instruments, so a filter copied from another entry can drop every row. --no-check skips the test fetch for a
session without API access; run the full fetch in a clean checkout before relying on such an entry.

    uv run python data/fetch_finmind.py --add TX__2025-04-01__2025-10-31.csv --dataset TaiwanFuturesDaily --data-id TX \
        --start 2025-04-01 --end 2025-10-31 --filter trading_session=^position$ --filter 'contract_date=^\\d{6}$'

Columns are kept under the FinMind names unless mapped with --map out=source (for example
--map cash_dividend=stock_and_cache_dividend). The FinMind MCP server caps a query at 500 rows; the API that this
script calls returned 4,737 daily rows in one query, so a new daily series can be one file. Intraday datasets need this
script (some answer one day per request).

A dataset that accepts only a start date (TaiwanStockEvery5SecondsIndex answers "we only send one day data, so
end_date parameter need be none") is registered by leaving out --end: the manifest entry then has "end_date": null and
the request carries no end_date, so the response is that one day. Always pass --data-id: without it the request returns
every series of the day (about 200,000 rows). --filter then keeps the one row you need:

    uv run python data/fetch_finmind.py --add sectors_close/Semiconductor__2025-06-11.csv \
        --dataset TaiwanStockEvery5SecondsIndex --data-id Semiconductor --start 2025-06-11 \
        --filter time=^13:30:00$ --filter kind=^twse$
"""
import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
MANIFEST = ROOT / "data" / "raw_manifest.json"
LOCK = ROOT / "data" / "raw_manifest.lock"
API ="https://api.finmindtrade.com/api/v4/data"
PAUSE = 0.7                                                # seconds between requests, far below the hourly API limit
MAX_CONSECUTIVE_FAILURES = 25
LAB_INPUTS = ("lm06/", "sectors/")                         # folders make_lab_data.py needs, besides the top level

def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def load_manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {"files": []}

def save_manifest(m):
    m["files"].sort(key=lambda e: e["path"])
    tmp = MANIFEST.with_name(MANIFEST.name + ".tmp")
    tmp.write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, MANIFEST)                              # a reader never sees a half-written manifest

def register(entry):
    """Add or replace one manifest entry under a lock, so parallel --add runs cannot drop each other's entries."""
    for _ in range(300):                                   # wait up to 30 s for another --add to finish writing
        try:
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            time.sleep(0.1)
    else:
        raise SystemExit(f"not registered: data/{LOCK.name} exists (another --add is writing, or delete a stale lock)")
    try:
        m = load_manifest()
        m["files"] = [e for e in m["files"] if e["path"] != entry["path"]] + [entry]
        save_manifest(m)
    finally:
        os.close(fd)
        LOCK.unlink()

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

def verify_local(entry):
    f = RAW / entry["path"]
    return f.exists() and sha256(f.read_bytes()) == entry["sha256"]

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
    token = os.environ.get("FINMIND_TOKEN")
    if args.no_check:
        print("warning: registered without a test fetch; run fetch_finmind.py in a clean checkout before relying on it")
    elif not token:
        raise SystemExit("not registered: set FINMIND_TOKEN so --add can test-fetch the query (or pass --no-check)")
    else:                                                  # the query must rebuild the file byte for byte
        data, n = render(entry, fetch(entry, token))
        if sha256(data) != entry["sha256"]:
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
    args = ap.parse_args()
    if args.add:
        return add(args)
    if "" in args.exclude:
        ap.error("--exclude needs a non-empty substring (an empty one matches every path)")
    entries = [e for e in load_manifest()["files"]
               if args.only in e["path"] and not any(x in e["path"] for x in args.exclude)]
    if args.verify:
        bad = [e["path"] for e in entries if not verify_local(e)]
        for e in entries:
            print(("ok      " if e["path"] not in bad else "MISSING/CHANGED ") + e["path"])
        sys.exit(1 if bad else 0)
    token = os.environ.get("FINMIND_TOKEN")
    if not token:
        raise SystemExit("set FINMIND_TOKEN to your FinMind API token")
    changed = 0
    fetched: list[str] = []
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
        if sha256(data) == e["sha256"]:
            out.write_bytes(data); fetched.append(e["path"]); print(f"fetched {e['path']} ({n} rows)")
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
    if problems:
        sys.exit("; ".join(problems))
    if args.only or args.exclude:
        print(f"{len(entries)} entries selected: {len(fetched)} fetched in this run, {len(entries) - len(fetched)} "
              "already matched; the other manifest entries were left out by --only/--exclude."
              + (" Fetched now:" if fetched else ""))
        for p in fetched:
            print(f"  {p}")
        # make_lab_data.py reads the top level of data/raw, lm06/ and sectors/; sectors_close/ only when present
        need = [e["path"] for e in load_manifest()["files"]
                if ("/" not in e["path"] or e["path"].startswith(LAB_INPUTS)) and not verify_local(e)]
        if need:
            print(f"make_lab_data.py needs {len(need)} more files (data/raw/*.csv, lm06/, sectors/): run "
                  "fetch_finmind.py with no --only and no --exclude (on the free plan: --exclude sectors_close/ only) "
                  "before it.")
        else:
            print("make_lab_data.py has every file it needs; next: uv run python data/make_lab_data.py")
    else:
        print("data/raw matches the manifest; next: uv run python data/make_lab_data.py")

if __name__ == "__main__":
    main()
