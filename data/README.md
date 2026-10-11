# Data pipeline

Run from the repository root.

## Getting the raw data

FinMind's licence forbids redistributing raw data, so `data/raw/` and the labs' `data/` folders are not in the
repository. [`raw_manifest.json`](raw_manifest.json) records, for every raw file, the FinMind query (dataset,
`data_id`, dates), the columns kept, any row filter, the row count and a SHA-256 of the file.

```bash
export FINMIND_TOKEN=...            # your FinMind API token
uv run python data/fetch_finmind.py       # rebuild data/raw/ and verify every file byte for byte (or ./build.sh --fetch)
uv run python data/make_lab_data.py       # build labs/LMNN_lab/data/ from data/raw/ (sectors_close/ optional)
uv run python data/fetch_finmind.py --verify   # later: confirm local files still match, no network
```

If FinMind has revised a series, the fetched file is written as `<name>.new` and the script stops, so the book's
numbers never change silently. New raw files are registered with `fetch_finmind.py --add` (see its `--help`).

## Scripts

`./build.sh --data` runs every step below in this order.

| Module | Script | Output |
|:--|:--|:--|
| all | `check_chunk.py <file>` | verifies one raw chunk: rows, first/last date, `spread` mismatches |
| all | `build_series.py` | `processed/etf_daily_returns.parquet` (0050 and 00631L on common dates, dividends and splits applied) |
| LM1 | `lm01_numbers.py`, `lm01_charts.py` | prints every LM1 number; `../src/data/lm01-*.json` |
| LM2 | `lm02_case.py`, `lm02_numbers.py`, `lm02_charts.py` | TX/TAIEX leverage case (near month, rolled the day before expiry); every other LM2 number with SymPy checks; `../src/data/lm02-*.json` |
| LM3 | `lm03_stats.py`, `lm03_numbers.py`, `lm03_charts.py` | `processed/lm03_stats.json`; LM3's example and problem numbers; `../src/data/lm03-*.json` |
| LM4 | `lm04_stats.py`, `lm04_numbers.py`, `lm04_charts.py` | `processed/lm04_stats.json`; LM4's example and problem numbers; `../src/data/lm04-*.json` |
| LM5 | `lm05_numbers.py`, `lm05_charts.py` | `processed/lm05_numbers.json` and every LM5 number; `../src/data/lm05-*.json` |
| LM6 | `lm06_basis.py`, `lm06_numbers.py`, `lm06_charts.py` | TX basis decomposition through the 2025 dividend season; every other LM6 number; `../src/data/lm06-*.json` |
| LM7 | `lm07_series.py`, `lm07_stats.py`, `lm07_numbers.py`, `lm07_tables.py`, `lm07_charts.py` | `processed/lm07_returns.parquet` (0050 and 00679B total returns), `processed/lm07_stats.json`; LM7 numbers and tables; `../src/data/lm07-*.json` |

`processed/` is not committed; `./build.sh --data` recreates it.

## Raw files (`raw/`)

All files are exactly as returned by FinMind (retrieved 2026-10-10), in the windows in which they were first downloaded (a new series may be a single file); they are listed in
`raw_manifest.json` and rebuilt by `fetch_finmind.py`.

- `0050__<start>__<end>.csv`, `00631L__<start>__<end>.csv`: `date,close,spread` from `TaiwanStockPrice` (unadjusted), 2014-10-31 → 2026-10-08.
- `00679B__<start>__<end>.csv`: `date,close,spread`, 2017-01-17 → 2026-10-08. `00679B_dividends.csv`: 37 quarterly ex-dates with before/after prices and cash dividends from `TaiwanStockDividendResult`; on 2019-03-05 and 2025-08-21 the close was unchanged, so the spread check cannot flag them and the dividend file is the authority.
- `0050_dividends.csv`: ex-dividend dates, before/after prices and cash dividends from `TaiwanStockDividendResult`.
- `TAIEX__2025-04-01__2025-10-31.csv`: TAIEX daily closes (146 rows).
- `TX__2025-04-01__2025-10-31.csv`: `TaiwanFuturesDaily` for TX, regular session only, every listed contract month (876 rows). On its last trading day the expiring contract's `settlement_price` prints 0.0 (the final settlement price is not in this field; use `close` or TAIFEX's published final settlement price). On days a contract does not trade, `close` and `volume` print 0 while `settlement_price` is set by the exchange.
- `lm06/`: for LM6, TAIEX closes (`TaiwanStockPrice`) for 2024-12-31 → 2025-03-31 and 2025-11-03 → 2025-12-31, which with the main TAIEX file cover calendar 2025; the TWSE total-return index (`TaiwanStockTotalReturnIndex`, columns `date,stock_id,price`) for the same three windows; TAIEX open, high (`max`), low (`min`), close and spread for 2025-06-26 → 2025-07-01. `lm06_basis.py` checks that every close satisfies the spread rule across the chunks, that both indices share their dates, and that the total-return index never falls behind the price index except by rounding (it gains only on ex-dividend days).
- `QQQ__us_2022.csv`, `TQQQ__us_2022.csv`: `date,adj_close,close` from `USStockPrice`. Adjusted closes depend on the retrieval date; returns within the window do not.
- `sectors/` (Volume II, retrieved 2026-10-11): `date,close,spread` from `TaiwanStockPrice` for TAIEX and the 30 TWSE
  sector indices (`data_id` = the index id, e.g. `Semiconductor`), 2007-07-02 → 2026-10-08, in 13 windows of 18
  months per series (`<ID>__<start>__<end>.csv`, at most 378 rows each; 403 files). Every file passed `check_chunk.py`
  for duplicates and order and is rebuilt byte for byte by `fetch_finmind.py`, **but the sector closes are not usable
  as served.** FinMind copies values from elsewhere: 18 dates carry every sector's closes from another date (the set
  of 2026-06-29 appears on six of them, so Semiconductor prints 1531.87 on 2009-06-05 and on 2025-06-11, against
  68.65 and 643.65 at the 13:30:00 close of `TaiwanStockEvery5SecondsIndex`), and on 21 more dates Chemical carries the
  same-day close of ChemicalBiotechnologyMedicalCare. 1,528 other rows carry a stale spread (another day's spread,
  volume and turnover) while the close is sound, so a close is never repaired as the previous close plus the spread. The Volume II scripts replace each flagged close with the official 13:30:00 value of
  `TaiwanStockEvery5SecondsIndex`, itself registered here (PITFALLS §3). TAIEX in the same dataset is clean, but its
  spread prints 0.0 through parts of 2017-12, 2018-09 and 2026-02. TradingConsumersGoods has only three closes before
  2008-12-01 in this dataset (the index existed: `TaiwanStockEvery5SecondsIndex` has values on other dates) and is complete
  from then.
- `sectors_close/` (Volume II, retrieved 2026-10-11): the 13:30:00 value of `TaiwanStockEvery5SecondsIndex` (a
  Backer dataset) for each of the 561 sector closes that `vol2_series.py` repairs, one file per close
  (`<ID>__<date>.csv`, `data_id` = the index, filtered to `time` 13:30:00 and `kind` twse). The dataset takes only a
  start date, so these manifest entries have `end_date: null`.
- `taiex_close/` (Volume II, retrieved 2026-10-11): the 13:30:00 TAIEX value of `TaiwanVariousIndicators5Seconds`
  (Free) on each of the 52 dates where TAIEX's spread prints 0.0, so that those closes can be checked; all 52 equal
  the served close.

`vol2_series.py` builds the Volume II closes with exact decimal arithmetic. It flags a sector close that the spread
contradicts on both sides or that repeats another date's close, replaces the 561 wrong ones with their 13:30:00 values,
accepts 1,528 stale spreads (an isolated mismatch whose closes agree with their other neighbours), checks TAIEX's
zero-spread closes against `taiex_close/`, and stops on any close still contradicted on both sides or on any change in
the set of flagged closes it keeps as served. While the repair was built, 3,029 further 13:30:00 values were fetched
and equalled the served close, and a spot check of 20 unflagged closes, one a year from 2007 to 2026, found every one
equal to its 13:30:00 value; the script records the 3,029 count (not the files), and this paragraph records the spot
check. Its outputs, git-ignored in `processed/`,
are `vol2_closes.parquet` (4,737 dates × 31 series), `vol2_repairs.json` and `vol2_series.txt`. `vol2_anchors.py` is
the editor's exploration for the Volume II briefs (`processed/vol2_anchors.txt`).

## Verification

`build_series.py` checks, with exact decimal arithmetic, that `close[t] − close[t−1] = spread[t]` for every row of the merged series. FinMind prints `spread = 0.0` on ex-dividend days and computes it from the split-adjusted reference price on the first day after a split, so the script accepts a mismatch only on a dividend date from `0050_dividends.csv` (where it also checks that the previous close equals FinMind's `before_price`) or on a known split date, and stops on anything else. `lm07_series.py` applies the same rule to 00679B. Total return on an ex-date is $(P_t + D_t)/(P_{t-1}/s) - 1$, where $s$ is the split ratio on a split day and 1 otherwise.

The Taiwan central bank's policy rate is not in FinMind; modules that need it cite a dated news source.
