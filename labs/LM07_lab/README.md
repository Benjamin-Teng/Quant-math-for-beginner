# LM7 Lab — Multivariable Calculus and Lagrange Multipliers

Companion to *From Calculus to Kelly*, Learning Module 7.

## Run

```bash
cd ~/projects && source .venv/bin/activate
uv pip install polars pyarrow numpy scipy sympy matplotlib jupyter
cd LM07_lab && jupyter lab LM07_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it.

## Data (offline snapshot, retrieved 2026-10-10 from FinMind)

| File | Content |
|:--|:--|
| `data/0050_daily_raw.csv` | 0050 daily close and FinMind `spread`, 2014-10-31 → 2026-10-08 (unadjusted) |
| `data/00679B_daily_raw.csv` | 00679B daily close and `spread`, 2017-01-17 → 2026-10-08 (unadjusted) |
| `data/0050_dividends.csv` | 0050 ex-dividend dates, before/after prices and cash dividends (`TaiwanStockDividendResult`) |
| `data/00679B_dividends.csv` | 00679B ex-dividend dates (37 quarterly distributions in the window) |

Every close was verified against FinMind's own `spread` column (close − previous close). The only mismatches are ex-dividend days (spread printed as 0) and 0050's 4-for-1 split on 2025-06-18. Two 00679B ex-dates (2019-03-05 and 2025-08-21) had an unchanged close and therefore show no mismatch; their dividends are still applied, and Part 1 checks that the previous close equals FinMind's `before_price` on every ex-date. 0050 was halted 2025-06-11..17 for its split while 00679B traded, so returns are taken between consecutive common trading dates.

00679B tracks the ICE US Treasury 20+ Year Bond Index and is quoted in New Taiwan dollars without a currency hedge, so its returns include USD/TWD moves.
