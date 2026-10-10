# LM6 Lab — Sequences, Series and the Time Value of Money

Companion to *From Calculus to Kelly*, Learning Module 6.

## Run

From the repository root:

```bash
uv sync    # installs the locked Python environment (uv.lock)
uv run --with jupyterlab jupyter lab labs/LM06_lab/LM06_lab.ipynb
```

To re-execute the notebook, run this inside `labs/LM06_lab`:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM06_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. `build/make_lab06.py` generates it;
edit the generator, not the notebook.

## Data (FinMind, as retrieved 2026-10-10; not in the repository)

The notebook reads FinMind files that you download once with your own token. From the repository root, run
`uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow
the book to redistribute the data. After that, the notebook runs offline.

```bash
export FINMIND_TOKEN=...              # your FinMind API token
uv run python data/fetch_finmind.py   # rebuilds data/raw/ and checks each
                                      # file against data/raw_manifest.json
uv run python data/make_lab_data.py   # writes every lab's data/ folder
```

The folder then holds:

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

Conventions: time to expiry = calendar days / 365 (actual/365, as DBS Taiwan accrues NTD deposits; see LM1);
financing-rate proxy $r_f = 2\%$ (continuously compounded), the central bank's discount rate throughout 2025. TAIEX
closes on a 13:25–13:30 call auction, while the TX daily settlement is the volume-weighted price of the last minute
before 13:45, so the daily basis is noisy (sample standard deviation of daily changes ≈ 83 index points); the module
explains how averaging and calendar spreads handle this. Back months trade a few dozen lots a day or fewer (the
December 2025 contract a median of 14.5), and when a contract has no trade in the final minute TAIFEX sets its
settlement by rule: the notebook prints volumes wherever a result leans on them. Dividends measured from the
total-return index are counted on their ex-dates, not their payment dates. Loan totals of interest are undiscounted;
the notebook also values each repayment schedule at a discount rate.

The optional helper in the extension exercise refreshes data for the 2024 season with your own token
(`export FINMIND_TOKEN=...`), through the standard library's `urllib`.
