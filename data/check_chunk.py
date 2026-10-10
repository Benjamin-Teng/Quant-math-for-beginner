#!/usr/bin/env python3
"""Verify a transcribed FinMind TaiwanStockPrice chunk: close[t]-close[t-1] == spread[t]."""
import csv, sys
from decimal import Decimal

def main(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print("EMPTY FILE"); return
    dates = [r["date"] for r in rows]
    dup = sorted({d for d in dates if dates.count(d) > 1})
    unsorted = any(dates[i] >= dates[i+1] for i in range(len(dates)-1))
    mism = []
    for i in range(1, len(rows)):
        p, c, s = (Decimal(rows[i-1]["close"]), Decimal(rows[i]["close"]), Decimal(rows[i]["spread"]))
        if abs((c - p) - s) > Decimal("0.005"):
            mism.append((rows[i]["date"], str(p), str(c), str(s)))
    print(f"file={path}")
    print(f"rows={len(rows)} first={dates[0]} last={dates[-1]} duplicates={dup} unsorted={unsorted}")
    print(f"mismatches={len(mism)}")
    for m in mism:
        print("  date={} prev_close={} close={} spread={}".format(*m))

if __name__ == "__main__":
    main(sys.argv[1])
