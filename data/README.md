# Data pipeline

| Step | Script | Output |
|:--|:--|:--|
| 1. Verify each raw chunk | `check_chunk.py <file>` | prints rows, first/last date, `spread` mismatches |
| 2. Build total-return series | `build_series.py` | `processed/etf_daily_returns.parquet` (0050 and 00631L on common dates, dividends and splits applied) |
| 3. LM3 statistics | `lm03_stats.py` | `processed/lm03_stats.json` (full period, per year, frequencies, big days, QQQ/TQQQ 2022) |
| 4. LM3 chart data | `lm03_charts.py` | `../src/data/lm03-*.json` |
| — | `lm03_numbers.py` | prints every number quoted in LM3's examples and problems |

`processed/` is not committed; `./build.sh --data` recreates it.

## Raw files (`raw/`)

- `0050__<start>__<end>.csv`, `00631L__<start>__<end>.csv`: `date,close,spread` exactly as returned by FinMind `TaiwanStockPrice` (unadjusted), 2014-10-31 → 2026-10-08, in windows of fewer than 500 rows.
- `0050_dividends.csv`: ex-dividend dates, before/after prices and cash dividends from `TaiwanStockDividendResult`.
- `QQQ__us_2022.csv`, `TQQQ__us_2022.csv`: `date,adj_close,close` from `USStockPrice`. Adjusted closes depend on the retrieval date; returns within the window do not.

## Verification

`build_series.py` checks, with exact decimal arithmetic, that `close[t] − close[t−1] = spread[t]` for every row of the merged series. FinMind prints `spread = 0.0` on ex-dividend days and computes it from the split-adjusted reference price on the first day after a split, so the script accepts a mismatch only on a dividend date from `0050_dividends.csv` (where it also checks that the previous close equals FinMind's `before_price`) or on a known split date, and stops on anything else.
