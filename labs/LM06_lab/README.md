# LM6 Lab — Sequences, Series and the Time Value of Money

Companion to *From Calculus to Kelly*, Learning Module 6.

## Run

```bash
cd ~/projects && source .venv/bin/activate
uv pip install polars pyarrow numpy matplotlib jupyter
cd LM06_lab && jupyter lab LM06_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. It runs offline from `data/`.

## Data (offline snapshot, retrieved 2026-10-10 from FinMind)

| File | Content |
|:--|:--|
| `data/TX__2025-04-01__2025-10-31.csv` | TX regular-session settlements, `TaiwanFuturesDaily`: `date,contract_date,close,settlement_price,volume,open_interest`, six contracts a day (three nearest months, three quarterly months) |
| `data/TAIEX_2025.csv` | TAIEX closes and FinMind `spread`, `TaiwanStockPrice`, 2024-12-31 → 2025-12-31 |
| `data/TAIEX_TR_2025.csv` | TWSE total-return TAIEX (cash dividends reinvested), `TaiwanStockTotalReturnIndex`, same dates |
| `data/TAIEX_OHLC__2025-06-26__2025-07-01.csv` | TAIEX open, high (`max`), low (`min`) and close around 27 June 2025 |
| `data/0050_daily_raw.csv` | 0050 daily close and `spread`, 2014-10-31 → 2026-10-09 (unadjusted) |
| `data/0050_dividends.csv` | 0050 ex-dividend dates and cash dividends, `TaiwanStockDividendResult` |

Checks run in the notebook: every TAIEX and 0050 close satisfies `close − previous close = spread`, except on 0050's
ex-dividend days and its 4-for-1 split (2025-06-18); the price and total-return indices share the same dates; the
total-return index never falls behind the price index by more than rounding. In the TX file the expiring contract shows
`settlement_price = 0.0` on its expiry day (third Wednesday; the final settlement price is not in the file) and is
dropped; some illiquid quarterly months show `close = 0.0`, so the notebook always uses `settlement_price`.

Conventions: time to expiry = calendar days / 365; financing-rate proxy $r = 2\%$, the central bank's discount rate
throughout 2025. TX trades until 13:45 and TAIEX closes at 13:30, so the daily basis is noisy (standard deviation of
daily changes ≈ 83 index points); the module explains how averaging and calendar spreads handle this.

The extension exercise at the end refreshes data for the 2024 season with your own token (`export FINMIND_TOKEN=...`).
