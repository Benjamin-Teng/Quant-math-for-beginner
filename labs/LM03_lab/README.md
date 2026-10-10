# LM3 Lab — Taylor Series and Approximation

Companion to *From Calculus to Kelly*, Learning Module 3.

## Run

```bash
cd ~/projects && source .venv/bin/activate
uv pip install polars pyarrow numpy matplotlib jupyter
cd LM03_lab && jupyter lab LM03_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it.

## Data (FinMind, retrieved 2026-10-10; not in the repository)

FinMind's licence does not allow its raw data in a public repository, so `data/` is git-ignored. Build it from the repository root with your own FinMind token:

```bash
export FINMIND_TOKEN=...           # your FinMind API token
python3 data/fetch_finmind.py      # rebuilds data/raw/ and checks every file against data/raw_manifest.json
python3 data/make_lab_data.py      # writes this folder and every other lab's
```

The folder then holds:

| File | Content |
|:--|:--|
| `data/0050_daily_raw.csv` | 0050 daily close and FinMind `spread`, 2014-10-31 → 2026-10-08 (unadjusted) |
| `data/00631L_daily_raw.csv` | 00631L daily close and `spread`, same period (unadjusted) |
| `data/0050_dividends.csv` | 0050 ex-dividend dates and cash dividends (`TaiwanStockDividendResult`) |
| `data/QQQ_TQQQ_2022.csv` | QQQ and TQQQ adjusted and raw closes, 2021-12-30 → 2023-01-03 (`USStockPrice`) |

Every close was verified against FinMind's own `spread` column (close − previous close). The only mismatches are 0050's 22 ex-dividend days in the window and the two split days: 0050 4-for-1 on 2025-06-18 and 00631L 22-for-1 on 2026-03-31. Part 2 of the notebook re-runs this check.

The optional `finmind()` helper at the end refreshes data with your own token (`export FINMIND_TOKEN=...`).
