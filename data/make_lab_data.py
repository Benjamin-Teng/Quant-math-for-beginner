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
build TR23 (data/vol3_series.py checks it against the price index); LM16's lab gets the two sector files instead.

Volume IV's labs combine those files as their briefs name them (plans/vol-4.md, "Lab parts"). LM25's lab adds
taiex_price.csv, the TAIEX price index on TR23's dates (raw/vol3/ to mid-2007, then raw/sectors/), and tx_daily.csv,
the TX regular-session monthly rows (raw/vol4/), from which it builds TX23 (data/vol4_series.py's rules). LM26's lab
gets vol4_rv.csv, the committed per-day realized variances (data/derived/, built by data/vol4_rv.py from the
5-second download, which no lab needs).

Volumes V and VI's labs (LM27-LM35) get the files their briefs list (plans/vol-5.md and plans/vol-6.md, "Lab parts";
plans/vol-5.md, the shared decision "Labs"). Raw copies keep their raw names (data/raw/vol5/, raw/vol6/; the
distribution files gain the fetch window, since vol5/0050_dividends.csv differs from Volume I's 0050_dividends.csv);
the T5S days a brief names are copied as taiex5s_<date>.csv when data/raw/intraday/taiex5s/ is present and skipped
with a message otherwise. Derived files are rows of data/processed/*.parquet written as CSV, floats by repr (they
round-trip exactly, so a lab can check its own results to 1e-12), booleans as true/false:
  - e5_estimation.csv (base, date, fund, R) and e5_wealth.csv (base, date, fund, R, traded): E5's two frames, one row
    per date and fund (data/vol5_series.py); e5_checkpoint_estimation.csv and e5_checkpoint_wealth.csv: the same for
    the checkpoint universe (sample E5+checkpoint, LM35);
  - rule_targets.csv: each rule's trades (rule, signal, trade, the five target exposures, exposure, turnover, cost);
    rule_wealth.csv (rule, date, wealth, wealth_gross) and rule_wealth_net.csv (rule, date, wealth): the eight rules'
    paths from the first trade's close (data/vol5_rules.py); a lab whose brief names some rules only gets
    rule_targets_R1_R2.csv, rule_targets_R3_R4.csv or rule_wealth_net_R1_R2.csv;
  - ohlc_0050_0056_00720B.csv: the checked daily rows of those funds (data/vol5_series.py's vol5_ohlc.parquet);
  - tx23_limit_days.csv: TX23's rows (data/vol4_series.py) whose settlement moved 9.95% or more since 2015-06-01, with
    2025-04-08 and 2026-10-08 (LM35);
  - lm34_grid.csv: the 60 configurations' daily net returns, once data/lm34_numbers.py writes
    data/processed/lm34_grid.parquet (skipped with a message until then).
A missing processed file is built first by its script (vol3_series.py first, then vol4_series.py, and vol5_series.py
before vol5_rules.py), which writes only data/processed/; a missing raw input stops the script.

    uv run python data/make_lab_data.py            # write labs/LMNN_lab/data/*
    uv run python data/make_lab_data.py --check    # compare with existing files; writes no lab file (a missing
                                                   # data/processed/ input is still built)
"""
import csv
import io
import json
import os
import subprocess
import sys
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DERIVED = ROOT / "data" / "derived"
PROC = ROOT / "data" / "processed"
T5S = RAW / "intraday" / "taiex5s"
V5 = "2016-12-01__2026-10-08"                     # the fetch window of data/raw/vol5/ and the vol6/ fund files
E5 = ["0050", "00646", "00679B", "00635U", "00642U"]
FUTURES = ["vol6/00672L", "vol6/00673R", "vol6/00674R", "vol6/00677U", "vol5/00635U", "vol5/00642U"]
PROXIES = ["SPY__us_", "TLT__us_", "GLD__us_", "USO__us_", "DBO__us_", "USD_TWD__"]   # + the fetch window
# a processed file -> (the script that writes it, the processed files that script reads, the raw files it reads)
BUILDERS: dict[str, tuple[str, tuple[str, ...], tuple[str, ...]]] = {
    "vol3_taiex": ("vol3_series.py", (), ("vol3/TAIEX_TR__*.csv", "vol3/TAIEX__*.csv", "sectors/TAIEX__*.csv",
                                          "taiex_close/TAIEX__*.csv")),
    "vol4_tx23": ("vol4_series.py", ("vol3_taiex",), ("vol4/TX__*.csv",)),
    "vol5_frames": ("vol5_series.py", ("vol3_taiex",),
                    (*(f"vol5/{s}__{V5}.csv" for s in [*E5, "0056", "00662", "00720B", "splits"]),
                     *(f"vol5/{s}_dividends.csv" for s in ["0050", "00679B", "0056", "00720B"]),
                     "0050__*.csv", "00679B__*.csv", "0050_dividends.csv", "00679B_dividends.csv")),
    "vol5_rules": ("vol5_rules.py", ("vol5_frames",), ()),
}
BUILDERS["vol5_ohlc"] = BUILDERS["vol5_frames"]
BUILDERS["vol5_trades"] = BUILDERS["vol5_rules"]

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
    if not (RAW / name).exists():
        raise SystemExit(f"missing data/raw/{name}: run uv run python data/fetch_finmind.py first")
    return (RAW / name).read_text(encoding="utf-8")

def cell(v):
    """A parquet value as CSV text: floats by repr (round-trip exact), booleans as true/false, dates in ISO form."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        return repr(v)
    return "" if v is None else str(v)

def table(df):
    if df.is_empty():
        raise SystemExit("a derived lab file would be empty: rerun the data/ script that writes its processed input")
    return text(df.columns, [[cell(v) for v in r] for r in df.iter_rows()])

def processed(name):
    """data/processed/<name>.parquet, after running its builder (and theirs first) when the file is missing."""
    f = PROC / f"{name}.parquet"
    if not f.exists():
        script, needs, raws = BUILDERS[name]
        for n in needs:
            processed(n)
        for p in raws:
            if not any(RAW.glob(p)):
                raise SystemExit(f"missing data/raw/{p}: run uv run python data/fetch_finmind.py first")
        print(f"data/processed/{f.name} is missing: running data/{script}", flush=True)
        try:
            subprocess.run([sys.executable, str(ROOT / "data" / script)], check=True, cwd=ROOT,
                           env={**os.environ, "PYTHONUTF8": "1"})
        except subprocess.CalledProcessError:
            raise SystemExit(f"data/{script} failed (see its message above)") from None
        if not f.exists():
            raise SystemExit(f"data/{script} did not write data/processed/{f.name}")
    return pl.read_parquet(f)

def frame(sample, kind):
    """One frame of vol5_frames.parquet, one row per date and fund (the estimation frame has no halted fund-day)."""
    df = processed("vol5_frames").filter((pl.col("sample") == sample) & (pl.col("frame") == kind))
    return table(df.drop("sample", "frame", *(("traded",) if kind == "estimation" else ())))

def t5s_days(days):
    """The raw T5S days a brief names, or none (with a message) when the intraday download is absent."""
    if not T5S.is_dir():
        print(f"skipped T5S days {', '.join(days)}: no data/raw/intraday/taiex5s/ "
              "(uv run python data/fetch_intraday.py --series taiex5s)")
        return {}
    out = {}
    for d in days:
        f = T5S / d[:4] / f"{d}.csv"
        if not f.exists():
            raise SystemExit(f"missing data/raw/intraday/taiex5s/{d[:4]}/{d}.csv: run uv run python "
                             "data/fetch_intraday.py --series taiex5s first")
        out[f"taiex5s_{d}.csv"] = f.read_text(encoding="utf-8")
    return out

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
    tx_daily = {"tx_daily.csv": copy("vol4/TX__1998-07-21__2026-10-16.csv")}
    h1, r1 = merged("vol3/TAIEX__*.csv")
    h2, r2 = merged("sectors/TAIEX__*.csv")
    assert h1 == h2 and r1[-1][0] < r2[0][0]              # the vol3 file ends before the sector files begin
    tr_dates = [line.split(",")[0] for line in tr23["taiex_tr.csv"].splitlines()[1:]]
    prices = [r for r in r1 + r2 if tr_dates[0] <= r[0] <= tr_dates[-1]]
    assert [r[0] for r in prices] == tr_dates               # TR23's 5,850 dates, no gap, no extra
    taiex_price = {"taiex_price.csv": text(h1, prices)}
    rv = {"vol4_rv.csv": (DERIVED / "vol4_rv.csv").read_text(encoding="utf-8")}
    etfs = {**common, "00631L_daily_raw.csv": p631,
            "00679B_daily_raw.csv": p679, "00679B_dividends.csv": copy("00679B_dividends.csv")}
    # Volumes V and VI: raw copies under their raw names, derived files from data/processed/ (module docstring)
    e5_raw = {**{f"{s}__{V5}.csv": copy(f"vol5/{s}__{V5}.csv") for s in E5},
              **{f"{s}_dividends__{V5}.csv": copy(f"vol5/{s}_dividends.csv") for s in ("0050", "00679B")}}
    splits = {f"splits__{V5}.csv": copy(f"vol5/splits__{V5}.csv")}
    e5 = {"e5_estimation.csv": frame("E5", "estimation"), "e5_wealth.csv": frame("E5", "wealth")}
    checkpoint = {"e5_checkpoint_estimation.csv": frame("E5+checkpoint", "estimation"),
                  "e5_checkpoint_wealth.csv": frame("E5+checkpoint", "wealth")}
    trades, paths = processed("vol5_trades"), processed("vol5_rules")
    targets = {"rule_targets.csv": table(trades)}
    wealth = {"rule_wealth.csv": table(paths)}
    net = {"rule_wealth_net.csv": table(paths.drop("wealth_gross"))}
    ohlc = processed("vol5_ohlc").filter(pl.col("fund").is_in(["0050", "0056", "00720B"]))
    tx23 = processed("vol4_tx23")
    day = pl.col("date").cast(pl.Utf8)
    limit = (day >= "2015-06-01") & ((pl.col("rF").exp() - 1).abs() >= 0.0995)   # the anchors' 9.95%, simple move
    tx_limit = {"tx23_limit_days.csv": table(tx23.filter(limit | day.is_in(["2025-04-08", "2026-10-08"])).sort("date"))}
    grid = {}
    if (PROC / "lm34_grid.parquet").exists():
        grid = {"lm34_grid.csv": table(pl.read_parquet(PROC / "lm34_grid.parquet"))}
    else:
        print("skipped labs/LM34_lab/data/lm34_grid.csv until data/lm34_numbers.py writes "
              "data/processed/lm34_grid.parquet")
    futures = {f"{Path(p).name}__{V5}.csv": copy(f"{p}__{V5}.csv") for p in FUTURES}
    proxies = {f"{p}2007-07-02__2026-10-08.csv": copy(f"vol6/{p}2007-07-02__2026-10-08.csv") for p in PROXIES}
    y2008 = {n: copy(f"vol6/{n}") for n in ("0050__2007-07-02__2008-12-31.csv",
                                             "0050_dividends__2007-07-02__2008-12-31.csv")}
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
        "LM16_lab": {**sectors},                  # LM16 works on Volume II's U28 sample only
        "LM17_lab": {**tr23},
        "LM18_lab": {**tr23},
        "LM19_lab": {**tr23},
        "LM20_lab": {**tr23, **common, "00631L_daily_raw.csv": p631, **sectors},
        "LM21_lab": {**tr23},
        "LM22_lab": {**tr23, **sectors},
        "LM23_lab": {**sectors, **common, "00631L_daily_raw.csv": p631, **tr23},
        "LM24_lab": {**tr23, **sectors},
        "LM25_lab": {**tr23, **taiex_price, **tx_daily},
        "LM26_lab": {**tr23, **rv},
        "LM27_lab": {**e5_raw, **splits, **tr23, **e5,
                     "rule_targets_R1_R2.csv": table(trades.filter(pl.col("rule").is_in(["R1", "R2"]))),
                     "rule_wealth_net_R1_R2.csv": table(paths.filter(pl.col("rule").is_in(["R1", "R2"]))
                                                        .drop("wealth_gross")),
                     **sectors},
        "LM28_lab": {**e5, **targets, **sectors},
        "LM29_lab": {**e5, "rule_targets_R3_R4.csv": table(trades.filter(pl.col("rule").is_in(["R3", "R4"]))),
                     **sectors},
        "LM30_lab": {**e5, **targets, **wealth, **sectors},
        "LM31_lab": {**e5, **targets, **wealth, **sectors},
        "LM32_lab": {**tr23, **e5, **targets, **net, **t5s_days(["2025-04-07", "2024-08-05", "2020-03-19"])},
        "LM33_lab": {**net, **tr23},              # the paths lie on the wealth frame's dates
        "LM34_lab": {**targets, "e5_wealth.csv": e5["e5_wealth.csv"], **wealth, **grid, **tr23, **common,
                     **splits, "delisting__2000-01-01__2026-10-08.csv": copy("vol6/delisting__2000-01-01__2026-10-08.csv"),
                     **futures},
        "LM35_lab": {**e5, **targets, **net, **tr23,
                     **t5s_days(["2008-01-22", "2015-08-24", "2020-01-30", "2024-08-05", "2025-04-07"]),
                     **tx_limit, **common, "00631L_daily_raw.csv": p631,
                     "ohlc_0050_0056_00720B.csv": table(ohlc), **proxies, **y2008, **checkpoint},
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
