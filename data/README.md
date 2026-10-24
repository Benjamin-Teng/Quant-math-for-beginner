# Data pipeline

Run from the repository root.

## Getting the raw data

FinMind's licence forbids redistributing raw data, so `data/raw/` and the labs' `data/` folders are not in the
repository. [`raw_manifest.json`](raw_manifest.json) records, for every raw file, the FinMind query (dataset,
`data_id`, dates), the columns kept, any row filter, the row count and a SHA-256 of the file.

```bash
export FINMIND_TOKEN=...            # your FinMind API token
uv run python data/fetch_finmind.py       # rebuild data/raw/ and verify every file (or ./build.sh --fetch)
uv run python data/make_lab_data.py       # build labs/LMNN_lab/data/ from data/raw/ (sectors_close/ optional)
uv run python data/fetch_finmind.py --verify   # later: confirm local files still match, no network
```

Every file must match the manifest byte for byte (a back-adjusted entry: within its rounding tolerance, and listed
at the end of the run). If FinMind has revised a series, the fetched file is written as `<name>.new` and the script
stops, so the book's numbers never change silently. New raw files are registered with `fetch_finmind.py --add` (see its `--help`).

Volume IV's intraday series are served one request per day, so they have their own script and manifest,
[`raw_intraday_manifest.json`](raw_intraday_manifest.json) (one entry per day: dataset, `data_id`, date, rows, SHA-256,
retrieval date), and live in `raw/intraday/`; `fetch_finmind.py --verify` does not look at them. The realized
variances derived from them are committed (`derived/`, below), so a reader needs the download only to rebuild that
file.

```bash
uv run python data/fetch_intraday.py --dry-run           # the days still to request, the API calls and the time
uv run python data/fetch_intraday.py --series taiex5s    # T5S: 5,351 one-day requests; resumable; then --check
uv run python data/fetch_intraday.py --verify            # listed files, pending .new files, unlisted files; no network
uv run python data/fetch_intraday.py --check             # the per-day checks; no network
```

T5S is a Free dataset. On a registered Free account (600 calls an hour) its 5,351 requests take about nine hours: the
script stops with exit status 2 whenever the hourly limit is reached, and you re-run the same command after the hour
(listed days are skipped). Without `--series` the command also fetches `tx1m` (297 requests), which needs the Sponsor
plan. With the download present, `./build.sh --data` runs `vol4_rv.py`: an incomplete download leaves the committed
`derived/vol4_rv.csv` as it is, while a complete one is checked day by day and rebuilds the file, so a day that fails
a check stops the build.

An empty answer on a TAIEX trading day is logged as FAILED, is not listed, and is asked again on the next run. A day
that stays empty, or whose data fail a check for a reason you have confirmed, goes into `EXCEPTIONS` in
`fetch_intraday.py` with its reason: kind `drop` (`vol4_rv.py` leaves the day out), kind `grid` (the values are
sound but the rows miss the regime's grid; the day is kept) or kind `steps` (a step above the bound was inspected
and is a real market move; the day is kept). Edit the manifest or `EXCEPTIONS` only while no fetch is running.

**Accepting a revised day.** A listed day is requested again only when its file is missing or no longer matches the
manifest. When FinMind's answer then differs from the manifest, the fetch writes it as `<date>.csv.new` beside the
file, leaves the manifest unchanged and exits 1; `--verify` reports it as PENDING until you decide. To ask whether
FinMind has revised a listed day, move its file out of `data/raw/intraday/` (never delete it; a file left there
unlisted makes `--verify` fail) and fetch the day with `--series taiex5s --dates <date>`: an
unchanged answer is written back under the same entry, a changed one becomes `.new`. Compare the two files. To keep
the listed version, put your copy back and delete the `.new` file. To accept the revision, delete the `.new` file and
the day's line in `raw_intraday_manifest.json` (keep the JSON valid: the last entry has no trailing comma), then fetch
the day again with `uv run python data/fetch_intraday.py --series taiex5s --dates <date>` (one request); the day is
listed again with its new row count, SHA-256 and retrieval date. Then run `--check`, and `vol4_rv.py` if the day is
in `derived/vol4_rv.csv`. A reader who rebuilds from the committed manifest takes a revised day the same way.

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
| LM8–LM12 | `vol2_series.py` | `processed/vol2_closes.parquet` (TAIEX and the 30 sector indices, repaired from the 13:30:00 values), `processed/vol2_repairs.json`, `processed/vol2_series.txt` (the report); needs `raw/sectors_close/` |
| LM8 | `lm08_numbers.py`, `lm08_charts.py` | every LM8 number, asserted against `../src/lm08.md`; `../src/data/lm08-*.json` |
| LM9 | `lm09_numbers.py`, `lm09_charts.py` | every LM9 number, asserted against `../src/lm09.md`; `../src/data/lm09-*.json` (the widget presets are in `lm09-area.json`) |
| LM10 | `lm10_series.py` (imported), `lm10_numbers.py`, `lm10_charts.py` | the U28 sample and the ETFs' one-session returns; every LM10 number, asserted; `../src/data/lm10-*.json` |
| LM11 | `lm11_common.py` (imported), `lm11_numbers.py`, `lm11_charts.py` | every LM11 number, asserted; `../src/data/lm11-*.json` |
| LM12 | `lm12_numbers.py`, `lm12_charts.py` | every LM12 number, asserted against `../src/lm12.md`; `../src/data/lm12-*.json` |
| LM13–LM18 | `vol3_series.py` | `processed/vol3_taiex.parquet` (TR23: the TAIEX total-return and price indices from 2003-01-02, with their daily returns), `processed/vol3_series.txt` (the report); stops unless every total-return row agrees with the price index |
| LM13 | `lm13_common.py` (imported), `lm13_numbers.py`, `lm13_charts.py` | every LM13 number, asserted against `../src/lm13.md`; `../src/data/lm13-*.json` |
| LM14 | `lm14_common.py` (imported), `lm14_charts.py`, `lm14_numbers.py` | `../src/data/lm14-*.json`; every LM14 number, asserted against `../src/lm14.md` and the chart files |
| LM15 | `lm15_numbers.py`, `lm15_charts.py` | every LM15 number, asserted against `../src/lm15.md`; `../src/data/lm15-*.json`; the widget's arithmetic checked in Node against SciPy |
| LM16 | `lm16_numbers.py`, `lm16_charts.py` | every LM16 number (U28 sample), asserted against `../src/lm16.md`; `../src/data/lm16-*.json` |
| LM17 | `lm17_numbers.py`, `lm17_charts.py` | every LM17 number, asserted against `../src/lm17.md` and compared with the A17 anchors; `../src/data/lm17-*.json` |
| LM18 | `lm18_common.py` (imported), `lm18_numbers.py`, `lm18_charts.py` | every LM18 number, asserted against `../src/lm18.md`; `../src/data/lm18-*.json` |
| LM25 | `vol4_series.py` | `processed/vol4_tx23.parquet` (TX23: the TX near-month regular-session settlement and the TAIEX close on TR23's 5,850 dates, rolled at the close of the day before each contract's last trading day, with days to that day, the log basis and the roll-free daily changes), `processed/vol4_series.txt` (the report); stops unless the calendars agree and every row passes the checks of `raw/vol4/` below |
| LM26 | `vol4_rv.py` | `derived/vol4_rv.csv` (committed, below) from the T5S download, `processed/vol4_rv.txt` (the report); without `raw/intraday/taiex5s/` the build skips the step, with an incomplete download the script keeps the committed file, and with a complete one it checks every day and stops on a failing one |
| LM19 | `lm19_common.py` (imported), `lm19_charts.py`, `lm19_numbers.py` | `../src/data/lm19-*.json`; every LM19 number (TR23), asserted against `../src/lm19.md` and the chart files and compared with the A19 anchors |
| LM20 | `lm20_common.py` (imported), `lm20_charts.py`, `lm20_numbers.py` | `../src/data/lm20-*.json`; every LM20 number (TR23, U28, LM4's 0050 sample), asserted against `../src/lm20.md` and compared with the A20 anchors |
| LM21 | `lm21_common.py` (imported), `lm21_charts.py`, `lm21_numbers.py` | `../src/data/lm21-*.json`; every LM21 number (TR23; LM16's printed U28 counts recounted), asserted against `../src/lm21.md` and the chart files and compared with the A21 anchors |
| LM22 | `lm22_common.py` (imported), `lm22_charts.py`, `lm22_numbers.py` | `../src/data/lm22-*.json` (chart specs and the widget's precomputed histograms); every LM22 number (TR23, U28), asserted against `../src/lm22.md` and compared with the A22 anchors |
| LM23 | `lm23_common.py` (imported), `lm23_charts.py`, `lm23_numbers.py` | `../src/data/lm23-*.json`; every LM23 number (U28, TR23 on U28's dates, LM2's pairs, TX23's settlement on 2026-10-08), asserted against `../src/lm23.md` and the chart files and compared with the A23 anchors |
| LM24 | `lm24_common.py` (imported), `lm24_numbers.py`, `lm24_charts.py` | every LM24 number (TR23 and U28's halves), asserted against `../src/lm24.md` and compared with the A24 anchors; `../src/data/lm24-*.json` |
| LM25 | `lm25_common.py` (imported), `lm25_charts.py`, `lm25_numbers.py` | `../src/data/lm25-*.json`; every LM25 number (TX23, TR23), asserted against `../src/lm25.md` and the chart files and compared with the A25 anchors (experiments 1–4 re-simulated) |
| LM26 | `lm26_common.py` (imported), `lm26_charts.py`, `lm26_numbers.py` | `../src/data/lm26-*.json`; every LM26 number (TR23, `derived/vol4_rv.csv`), asserted against `../src/lm26.md` and compared with the A26 anchors; the raw-download statistics and the TX minute bars only when `raw/intraday/` is present, otherwise skipped and the committed `lm26-futures.json` kept |
| Volume IV | `fetch_intraday.py` | not run by the build: downloads and checks the intraday series `raw/intraday/taiex5s/` and `raw/intraday/tx1m/` (below) and keeps `raw_intraday_manifest.json` |

`processed/` is not committed; `./build.sh --data` recreates it. `derived/` is committed (below).

## Raw files (`raw/`)

All files are exactly as returned by FinMind (retrieved 2026-10-10), in the windows in which they were first downloaded (a new series may be a single file); they are listed in
`raw_manifest.json` and rebuilt by `fetch_finmind.py`.

- `0050__<start>__<end>.csv`, `00631L__<start>__<end>.csv`: `date,close,spread` from `TaiwanStockPrice` (unadjusted), 2014-10-31 → 2026-10-08.
- `00679B__<start>__<end>.csv`: `date,close,spread`, 2017-01-17 → 2026-10-08. `00679B_dividends.csv`: 37 quarterly ex-dates with before/after prices and cash dividends from `TaiwanStockDividendResult`; on 2019-03-05 and 2025-08-21 the close was unchanged, so the spread check cannot flag them and the dividend file is the authority.
- `0050_dividends.csv`: ex-dividend dates, before/after prices and cash dividends from `TaiwanStockDividendResult`.
- `TAIEX__2025-04-01__2025-10-31.csv`: TAIEX daily closes (146 rows).
- `TX__2025-04-01__2025-10-31.csv`: `TaiwanFuturesDaily` for TX, regular session only, every listed contract month (876 rows). On its last trading day the expiring contract's `settlement_price` prints 0.0. The final settlement price is not in this field, and the day's `close` is not it either: for the TX contracts of 200901 → 202609 in TAIFEX's file the two agree on 105 of 189 and differ by up to 4 points (`vol4_settlement/` holds TAIFEX's published final settlement prices). On days a contract does not trade, `close` and `volume` print 0 while `settlement_price` is set by the exchange.
- `lm06/`: for LM6, TAIEX closes (`TaiwanStockPrice`) for 2024-12-31 → 2025-03-31 and 2025-11-03 → 2025-12-31, which with the main TAIEX file cover calendar 2025; the TWSE total-return index (`TaiwanStockTotalReturnIndex`, columns `date,stock_id,price`) for the same three windows; TAIEX open, high (`max`), low (`min`), close and spread for 2025-06-26 → 2025-07-01. `lm06_basis.py` checks that every close satisfies the spread rule across the chunks, that both indices share their dates, and that the total-return index never falls behind the price index except by rounding (it gains only on ex-dividend days).
- `QQQ__us_2022.csv`, `TQQQ__us_2022.csv`: `date,adj_close,close` from `USStockPrice`. Adjusted closes depend on the retrieval date (FinMind rebuilds them backward from the latest day); returns within the window move only by cent rounding. Both entries are registered with `--adjusted adj_close`: `date` and `close` must match exactly, and `adj_close` must follow `close` within each day's cent-rounding allowance except on the registered ex-dates, with the window's distribution yield unchanged (`fetch_finmind.py`).
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

- `vol3/` (Volume III, retrieved 2026-10-18): the TAIEX total-return index (`TaiwanStockTotalReturnIndex`, columns
  `date,price`), 2003-01-02 → 2026-10-08 in one file (5,850 rows; FinMind serves it from 2003-01-02), and the TAIEX
  price index (`TaiwanStockPrice`, `date,close,spread`) for 2003-01-02 → 2007-06-29 (1,113 rows), which with
  `sectors/TAIEX__*.csv` covers the same dates. The total-return index has no spread column, so `check_chunk.py`
  cannot test it; `vol3_series.py` tests it against the price index instead: the two have the same 5,850 dates, every
  price close agrees with its spread (or, on the 52 zero-spread dates, with `taiex_close/`), and on every date the
  total return minus the price return lies between −0.035 and +84 basis points (and within rounding on the first and last dates), the 11 days above 40 basis points in late
  June or July, when most dividends go ex. A row copied from another date would leave that range. Its outputs are
  `processed/vol3_taiex.parquet` and `processed/vol3_series.txt`. `vol3_anchors_lm13.py` … `vol3_anchors_lm18.py`
  print every number of the Volume III briefs, one line per anchor of `../plans/vol-3-anchors.md` (LM16's reads
  `vol2_closes.parquet`); they write nothing.
- `vol4/` (Volume IV, retrieved 2026-10-19): `TX__1998-07-21__2026-10-16.csv`, `TaiwanFuturesDaily` for TX, the whole
  history in one query, regular session only (`trading_session` position) and monthly contracts only (`contract_date`
  of six digits; the calendar-spread rows are left out), columns
  `date,contract_date,close,spread,settlement_price,volume,open_interest` (36,437 rows, 7,009 dates, 343 contracts).
  `spread` is the close minus the contract's previous *settlement*, not its previous close; on a day a contract does
  not trade, `close`, `spread` and `volume` print 0 (646 rows in TR23's window; 639 of them after a first listing day). Within 2003-01-02 → 2026-10-08 the
  only rows that break this rule are the five months listed on 2007-03-12, whose spreads are the close minus the
  *same* day's settlement (the next session's spreads, which follow the rule, confirm those settlements);
  `vol4_series.py` asserts that pattern. A contract's last trading day is its last
  row: the third Wednesday of its month, or later after a holiday (eight contracts in the window). From 2008-12-17 the
  expiring contract's `settlement_price` prints 0 on that day (214 contracts). The regular-session dates equal TR23's
  5,850 dates, with five monthly contracts a date to 2018-06-29 and six from 2018-07-02. The file runs a week past
  TR23's last date so that the contract held on 2026-10-08 is known not to expire the next session. `check_chunk.py`
  does not apply (several contracts a date, and the spread is against the settlement); `vol4_series.py` checks all of
  the above and builds TX23. On 2008-10-27 TX fell by its 7% limit and TAIEX by 4.6%, so the near-month log basis
  reached −7.9%, the sample's widest. `vol4/` holds only this file; the intraday files are in `intraday/`.
  `vol4_anchors_lm19.py` … `vol4_anchors_lm26.py` print every number of the Volume IV briefs, one line per anchor of
  `../plans/vol-4-anchors.md`, from the `processed/` files (TR23, U28, the 0050/00631L pairs, TX23); LM26's also reads
  `derived/vol4_rv.csv`, this TX file and the intraday download in `raw/intraday/` (T5S and the 2025 TX bars, for the
  anchors marked raw), so it needs that download. They write nothing.
- `vol4_settlement/` (Volume IV, retrieved 2026-10-19; Backer, optional):
  `TaiwanFuturesFinalSettlementPrice` for TX, monthly contracts only (`contract_month` of six digits; the weekly
  `YYYYMMWn` rows are left out), columns `date,contract_month,settlement_price`: 277 official final settlement prices,
  199809 → 202609, with no rows for 2000, 2006, 2008, 2014 and 2020. `vol4_series.py` uses it only as a cross-check:
  the final-settlement date is the contract's last trading day from 200901 and the next session up to 200712, and the
  script skips the cross-check when the file is absent. `fetch_finmind.py --verify`, and so `./build.sh --data`,
  accepts the file missing (`OPTIONAL` in that script) but not changed. On a plan without this dataset, fetch with
  `--exclude vol4_settlement/`.
- `vol5/` (Volumes V–VI, retrieved 2026-10-24): the through case's funds E5 (0050, 00646, 00679B, 00635U, 00642U)
  and the checkpoint funds (0056, 00662, 00720B): `<id>__2016-12-01__2026-10-08.csv`, `TaiwanStockPrice` (Free),
  columns `date,open,max,min,close,spread,volume` (`volume` is `Trading_Volume`); `<id>_dividends.csv` for 0050 and
  0056 (filter `^息$`) and 00679B and 00720B (filter `^除息$`), `TaiwanStockDividendResult`; and
  `splits__2016-12-01__2026-10-08.csv`, every event of `TaiwanStockSplitPrice` in the window (its `type` is empty for
  00631L's 2026 split). `vol5_series.py` checks them (spreads, ex-dates within a tick, splits, copies, the Volume I
  files) and builds E5's estimation and wealth frames.
- `vol6/` (Volume VI, retrieved 2026-10-24): LM34's survivorship example — `delisting__2000-01-01__2026-10-08.csv`
  (`TaiwanStockDelisting`, ids beginning with "00", 63 rows), the price files of 00672L, 00673R, 00674R and 00677U
  (as `vol5/`; 00673R reverse-split on 2025-10-22, and 00674R prints a close of 0 on days without a trade) and two
  one-day snapshots of every ETF, `etf_snapshot__2017-01-17.csv` and `etf_snapshot__2026-10-08.csv` (`TaiwanStockPrice`
  without a `data_id`, which FinMind serves only above the Free plan: on a Free account fetch with
  `--exclude vol6/etf_snapshot`, and LM34 skips the one number that needs them). LM35's replays — SPY, TLT, GLD, USO
  and DBO (`USStockPrice`, `date,adj_close,close`, registered with `--adjusted adj_close`; USO's 1-for-8 reverse split
  of 2020-04-28 is one of its registered "ex-dates"), `USD_TWD__2007-07-02__2026-10-08.csv` (`TaiwanExchangeRate`,
  `spot_buy,spot_sell`, without FinMind's −1 rows) and 0050's 2007–2008 closes and distributions
  (`0050__2007-07-02__2008-12-31.csv`, `0050_dividends__2007-07-02__2008-12-31.csv`, as Volume I's files).
- `intraday/taiex5s/<year>/<date>.csv` and `intraday/tx1m/2025/<date>.csv` (Volume IV intraday, `fetch_intraday.py`,
  listed in `raw_intraday_manifest.json`, not in `raw_manifest.json`; the request log is
  `intraday/fetch_intraday.log`). Each file is one day exactly as returned: FinMind's columns in its order, every
  value as printed in its JSON.
  - `taiex5s`: `TaiwanVariousIndicators5Seconds` (Free, no `data_id`), columns `date,TAIEX` (`date` carries the time),
    every TAIEX trading day 2005-01-03 → 2026-10-08 (5,351 days, about 310 MB). The rows a day give the sampling: 271
    (every minute) to 2011-01-14, 1,081 (every 15 seconds) 2011-01-17 → 2014-02-21, 1,621 (every 10 seconds)
    2014-02-24 → 2014-12-27 (a Saturday session) and 3,241 (every 5 seconds) from 2014-12-29;
    `fetch_intraday.py --check` prints every regime's first and last day. FinMind prints the
    previous trading day's close at 09:00:00; the values after it move with the day's trading, and the first seconds
    carry the opening gap. `--check` requires the 09:00:00 value to equal the previous trading day's TAIEX close and
    the 13:30:00 value the day's (`TaiwanStockPrice`, within 0.005), and checks every value and the steps between
    consecutive values (`fetch_intraday.py --help`).
  - `tx1m`: `TaiwanFuturesKBar` (Sponsor) for TX, calendar 2025, columns
    `date,futures_id,contract_date,minute,open,high,low,close,volume`, every listed month and calendar spread. A bar
    is labelled by its start minute (inferred from the labels). A date holds 00:00–04:59 of the night session that began the session before,
    then 08:45–13:44 and 15:00–23:59 of its own sessions. A bar labelled with the closing minute itself appears on
    some dates: 13:45:00 on 31 dates of 2025 (on 30 of the 243 trading days for the near month), with a tiny volume
    and a close equal to the daily close, and 05:00:00 on 5 (`../project/SOURCES.md`, "TaiwanFuturesKBar"). Saturdays and the first day of a holiday hold only that
    00:00–04:59 tail; later holiday days and Sundays answer no rows. The calendar is the 243 trading days of 2025 plus the 54 calendar days after one (297
    requests); a day off the trading calendar that answers no rows is listed with `rows` 0 and no file, while an
    empty trading day is retried like a T5S day.

## Derived files (`derived/`)

Per-day statistics of raw data that a reader could otherwise rebuild only with a long download. They are committed
by the owner's decision of 2026-10-19 (`../plans/ROADMAP.md`, "Data rule"): per-day statistics only, never intraday
prices or returns. They are not covered by the repository's MIT licence: they derive from FinMind data, which remain
subject to FinMind's terms (non-commercial use; credit FinMind and the original source).

- `vol4_rv.csv` (LM26, `vol4_rv.py`), derived from FinMind's `TaiwanVariousIndicators5Seconds`, the TAIEX that the
  Taiwan Stock Exchange (TWSE) computes. Its first line is a comment with that credit; read it with
  `pl.read_csv("data/derived/vol4_rv.csv", comment_prefix="#")`. One row per TAIEX trading day 2005-01-03 →
  2026-10-08, less any day that `fetch_intraday.py` lists as a `drop` exception (`processed/vol4_rv.txt` gives the
  reason): `date`; `regime_s`, the seconds between the day's values; for each of the nine sampling intervals h (`5s`,
  `10s`, `15s`, `30s`, `1m`, `5m`, `10m`, `15m` and `30m`), `rv_<h>`, the sum of squared log returns on the grid
  09:30:00, 09:30:00 + h, …, 13:30:00, and `n_<h>`, the number of returns (14,400 s / h), both NaN when h is not a
  multiple of `regime_s` (Polars then reads that `n_<h>` column as floats); and `o2`, the squared log change from the
  previous trading day's TAIEX close (`TaiwanStockPrice`; for 2005-01-03, 2004-12-31's close from `raw/vol3/`) to the
  09:30:00 value. Values carry seven significant digits. The file holds no signed return and no price level. The grids
  start at 09:30:00 because FinMind's 09:00:00 value is the previous close (`raw/` above): a grid from 09:00:00 would
  put the overnight gap into its first return. The 240 minutes to 13:30:00 hold a whole number of every interval, so
  every grid covers the same window, and `o2` keeps the gap as its own column. `vol4_rv.py` rebuilds the file only
  from a complete download that passes `fetch_intraday.py`'s checks.

## Verification

`build_series.py` checks, with exact decimal arithmetic, that `close[t] − close[t−1] = spread[t]` for every row of the merged series. FinMind prints `spread = 0.0` on ex-dividend days and computes it from the split-adjusted reference price on the first day after a split, so the script accepts a mismatch only on a dividend date from `0050_dividends.csv` (where it also checks that the previous close equals FinMind's `before_price`) or on a known split date, and stops on anything else. `lm07_series.py` applies the same rule to 00679B. Total return on an ex-date is $(P_t + D_t)/(P_{t-1}/s) - 1$, where $s$ is the split ratio on a split day and 1 otherwise.

The Taiwan central bank's policy rate is not in FinMind; modules that need it cite a dated news source.
