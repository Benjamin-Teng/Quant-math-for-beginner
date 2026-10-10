# LM1 Lab — Exponentials, Logarithms and Compounding

Companion to *From Calculus to Kelly*, Learning Module 1. The notebook rebuilds every exhibit and computational example of the module (the 0050 case, log-scale charts, compounding tables, return conversions and trailing returns, aggregation examples, drawdown episodes) and solves the computational practice problems.

## Run

```bash
cd ~/projects && source .venv/bin/activate
uv pip install polars pyarrow numpy matplotlib jupyter
cd LM01_lab && jupyter lab LM01_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. It is regenerated from `build/make_lab01.py` (which also refreshes the `data/` snapshot from the repository's `data/raw/`) and executed with `jupyter nbconvert --to notebook --execute LM01_lab.ipynb --output LM01_lab.ipynb` from inside this folder.

## Data (offline snapshot, retrieved 2026-10-10 from FinMind)

| File | Content |
|:--|:--|
| `data/0050_daily_raw.csv` | 0050 daily close and FinMind `spread`, 2014-10-31 → 2026-10-08 (unadjusted) |
| `data/00631L_daily_raw.csv` | 00631L daily close and `spread`, same period (unadjusted) |
| `data/0050_dividends.csv` | 0050 ex-dividend dates and cash dividends (`TaiwanStockDividendResult`) |

Every close was verified against FinMind's own `spread` column (close − previous close). The only mismatches are 0050's 22 ex-dividend days in the window and the two split days: 0050 4-for-1 on 2025-06-18 and 00631L 22-for-1 on 2026-03-31. Part 1 of the notebook re-runs this check.

Two daily series are built. The module's case series aligns 0050 with 00631L on their 2,902 common trading days, as in LM3; 0050's own series has 2,906 returns because it keeps four March 2026 sessions on which 00631L did not trade. Growth factors, drawdowns and recovery dates are identical in both. 00631L is needed only for the portfolio example (Part 5) and the extension exercise.
