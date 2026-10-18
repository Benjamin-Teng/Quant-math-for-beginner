#!/usr/bin/env python3
"""Build every lab's data/ folder from data/raw/ (run from the repository root).

Raw FinMind files are not committed (FinMind's licence forbids redistributing raw data), so a fresh clone first runs
`uv run python data/fetch_finmind.py` (needs FINMIND_TOKEN) and then this script. Values are copied as text, never
re-formatted, so the lab files match the raw files exactly.

Volume II's labs get two sector files. sectors_close_raw.csv holds the closes FinMind serves for TAIEX and the 30
sector indices (raw/sectors/), one column per series, empty where a series has no close. sectors_close_repairs.csv
lists every close that data/vol2_series.py repairs: the manifest registers one raw/sectors_close/ file per repaired
close, so the list is complete even without those files, and close_1330 holds the file's 13:30:00 value, or is empty
when the file is missing (FinMind's free plan lacks that dataset; the lab then drops the close).

Volume III's labs get taiex_tr.csv, the TAIEX total-return index as FinMind serves it (raw/vol3/), from which they
build TR23 (data/vol3_series.py checks it against the price index); LM16's lab also gets the two sector files.

    uv run python data/make_lab_data.py            # write labs/LMNN_lab/data/*
    uv run python data/make_lab_data.py --check    # compare with existing files, write nothing
"""
import csv
import io
import json
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

def sectors_raw():
    """The served closes of TAIEX and the 30 sector indices, one column per series (TAIEX first), on TAIEX's dates."""
    ids = sorted({p.name.split("__")[0] for p in (RAW / "sectors").glob("*.csv")})
    if "TAIEX" not in ids or len(ids) != 31:
        raise SystemExit(f"data/raw/sectors/ holds {len(ids)} series, not TAIEX and 30 sectors: run fetch_finmind.py")
    cols = {}
    for i in ids:
        h, rows = merged(f"sectors/{i}__*.csv")
        if h != ["date", "close", "spread"]:
            raise SystemExit(f"unexpected header in data/raw/sectors/{i}: {h}")
        cols[i] = {r[0]: r[1] for r in rows}
    order = ["TAIEX"] + [i for i in ids if i != "TAIEX"]
    dates = sorted(cols["TAIEX"])
    extra = {d for i in ids for d in cols[i]} - set(dates)
    if extra:
        raise SystemExit(f"sector closes on dates without a TAIEX close: {sorted(extra)[:5]}")
    return text(["date", *order], [[d, *(cols[i].get(d, "") for i in order)] for d in dates])

def sector_repairs():
    """Every close that vol2_series.py repairs (one manifest entry each), with its 13:30:00 value when the file exists."""
    manifest = json.loads((ROOT / "data" / "raw_manifest.json").read_text(encoding="utf-8"))
    rows = []
    for path in sorted(e["path"] for e in manifest["files"] if e["path"].startswith("sectors_close/")):
        sid, day = Path(path).stem.split("__")
        value = ""
        if (RAW / path).exists():
            h, body = read(RAW / path)
            if h != ["date", "time", "stock_id", "price", "kind"] or len(body) != 1 or \
                    body[0][:3] != [day, "13:30:00", sid] or body[0][4] != "twse":
                raise SystemExit(f"unexpected content in data/raw/{path}: run fetch_finmind.py --verify")
            value = body[0][3]
        rows.append([sid, day, value])
    if not rows:
        raise SystemExit("data/raw_manifest.json lists no sectors_close/ files")
    return text(["id", "date", "close_1330"], rows)

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
    sectors = {"sectors_close_raw.csv": sectors_raw(), "sectors_close_repairs.csv": sector_repairs()}
    tr23 = {"taiex_tr.csv": copy("vol3/TAIEX_TR__2003-01-01__2026-10-08.csv")}
    etfs = {**common, "00631L_daily_raw.csv": p631,
            "00679B_daily_raw.csv": p679, "00679B_dividends.csv": copy("00679B_dividends.csv")}
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
        "LM08_lab": {**sectors, **etfs, "TX__2025-04-01__2025-10-31.csv": tx},
        "LM09_lab": {**sectors},
        "LM10_lab": {**sectors, **etfs},
        "LM11_lab": {**sectors, **etfs},
        "LM12_lab": {**sectors},
        "LM13_lab": {**tr23},
        "LM14_lab": {**tr23},
        "LM15_lab": {**tr23},
        "LM16_lab": {**tr23, **sectors},
        "LM17_lab": {**tr23},
        "LM18_lab": {**tr23},
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
