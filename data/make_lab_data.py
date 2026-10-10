#!/usr/bin/env python3
"""Build every lab's data/ folder from data/raw/ (run from the repository root).

Raw FinMind files are not committed (FinMind's licence forbids redistributing raw data), so a fresh clone first runs
`uv run python data/fetch_finmind.py` (needs FINMIND_TOKEN) and then this script. Values are copied as text, never
re-formatted, so the lab files match the raw files exactly.

    uv run python data/make_lab_data.py            # write labs/LMNN_lab/data/*
    uv run python data/make_lab_data.py --check    # compare with existing files, write nothing
"""
import csv
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    return rows[0], rows[1:]

def merged(pattern, drop=()):
    """Concatenate raw chunks matching pattern (sorted by date, exact duplicates removed), dropping columns."""
    files = sorted(RAW.glob(pattern))
    if not files:
        raise SystemExit(f"missing data/raw/{pattern}: run uv run python data/fetch_finmind.py first")
    header, rows = None, {}
    for f in files:
        h, body = read(f)
        if header is None:
            header = h
        elif h != header:
            raise SystemExit(f"header mismatch in {f.name}")
        for r in body:
            if r[0] in rows and rows[r[0]] != r:
                raise SystemExit(f"conflicting rows for {r[0]} in {pattern}")
            rows[r[0]] = r
    assert header is not None                              # files is not empty
    keep = [i for i, c in enumerate(header) if c not in drop]
    return [header[i] for i in keep], [[r[i] for i in keep] for _, r in sorted(rows.items())]

def text(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header); w.writerows(rows)
    return buf.getvalue()

def copy(name):
    return (RAW / name).read_text(encoding="utf-8")

def qqq_tqqq():
    hq, q = read(RAW / "QQQ__us_2022.csv"); ht, t = read(RAW / "TQQQ__us_2022.csv")
    assert hq == ht == ["date", "adj_close", "close"]
    tq = {r[0]: r for r in t}
    rows = [[r[0], r[1], r[2], tq[r[0]][1], tq[r[0]][2]] for r in q if r[0] in tq]
    return text(["date", "qqq_adj", "qqq_close", "tqqq_adj", "tqqq_close"], rows)

def build():
    p0050 = text(*merged("0050__*.csv"))
    p631 = text(*merged("00631L__*.csv"))
    p679 = text(*merged("00679B__*.csv"))
    d0050 = copy("0050_dividends.csv")
    common = {"0050_daily_raw.csv": p0050, "0050_dividends.csv": d0050}
    taiex = copy("TAIEX__2025-04-01__2025-10-31.csv")
    tx = copy("TX__2025-04-01__2025-10-31.csv")
    # calendar-2025 TAIEX and total-return index for LM6: the main window plus the two lm06/ windows
    h, rows = merged("lm06/TAIEX__*.csv")
    h2, main = read(RAW / "TAIEX__2025-04-01__2025-10-31.csv")
    assert h == h2
    taiex_2025 = text(h, sorted(rows + main))
    taiex_tr_2025 = text(*merged("lm06/TAIEX_TR__*.csv", drop=("stock_id",)))
    return {
        "LM01_lab": {**common, "00631L_daily_raw.csv": p631},
        "LM02_lab": {**common, "00631L_daily_raw.csv": p631,
                     "TAIEX__2025-04-01__2025-10-31.csv": taiex, "TX__2025-04-01__2025-10-31.csv": tx},
        "LM03_lab": {**common, "00631L_daily_raw.csv": p631, "QQQ_TQQQ_2022.csv": qqq_tqqq()},
        "LM04_lab": {**common, "00631L_daily_raw.csv": p631},
        "LM05_lab": {**common, "00631L_daily_raw.csv": p631},
        "LM06_lab": {**common, "TAIEX_2025.csv": taiex_2025, "TAIEX_TR_2025.csv": taiex_tr_2025,
                     "TAIEX_OHLC__2025-06-26__2025-07-01.csv": copy("lm06/TAIEX_OHLC__2025-06-26__2025-07-01.csv"),
                     "TX__2025-04-01__2025-10-31.csv": tx},
        "LM07_lab": {**common, "00679B_daily_raw.csv": p679, "00679B_dividends.csv": copy("00679B_dividends.csv")},
    }

if __name__ == "__main__":
    check = "--check" in sys.argv
    bad = 0
    for lab, files in build().items():
        d = ROOT / "labs" / lab / "data"
        for name, content in files.items():
            f = d / name
            if check:
                same = f.exists() and f.read_text(encoding="utf-8") == content
                bad += not same
                print(f"{'ok  ' if same else 'DIFF'} labs/{lab}/data/{name}")
            else:
                d.mkdir(parents=True, exist_ok=True); f.write_text(content, encoding="utf-8", newline="\n")
    if check and bad:
        sys.exit(1)
    print("lab data: " + ("all identical" if check else "written"))
