# LM8 Lab — Vectors and Matrices

Companion to *From Calculus to Kelly*, Learning Module 8. The notebook joins TX, 0050 and 00679B on their dates for the week of 7–11 April 2025, rebuilds the total-return frames of the ETF pairs and the repaired sample of 28 TWSE sector indices, reproduces the module's exhibits and computational examples, and works the computational practice problems.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM08_lab/LM08_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM08_lab.ipynb
```

`build/make_lab08.py` generates the notebook and this README: edit the generator, not the generated files.

## Data (FinMind; not in the repository)

The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

The same steps in a shell (`data/raw/` and this folder's `data/` are git-ignored):

```bash
export FINMIND_TOKEN=...               # your FinMind API token
uv run python data/fetch_finmind.py    # rebuilds and verifies data/raw/
uv run python data/make_lab_data.py    # writes every lab's data/ folder
```

On FinMind's free plan, fetch with `uv run python data/fetch_finmind.py --exclude sectors_close/`; the sector repair then drops the closes it cannot repair, and Part 5 says which printed numbers change.

`fetch_finmind.py` checks every file against `data/raw_manifest.json`. The notebook reads only the files in its own `data/` folder, which then holds:

| File | Content |
|:--|:--|
| `data/TX__2025-04-01__2025-10-31.csv` | TX daily rows from `TaiwanFuturesDaily`, every listed contract month: settlement price, close, volume, open interest |
| `data/0050_daily_raw.csv`, `data/00631L_daily_raw.csv`, `data/00679B_daily_raw.csv` | daily closes and FinMind `spread` (unadjusted) from `TaiwanStockPrice` |
| `data/0050_dividends.csv`, `data/00679B_dividends.csv` | ex-dividend dates, before and after prices and cash dividends from `TaiwanStockDividendResult` |
| `data/sectors_close_raw.csv` | the closes FinMind serves for TAIEX and the 30 TWSE sector indices, one column per series |
| `data/sectors_close_repairs.csv` | every sector close the book repairs, with its 13:30:00 value from `TaiwanStockEvery5SecondsIndex` (empty on the free plan) |

Every ETF close is checked against FinMind's own `spread` column; the only mismatches allowed are ex-dividend days and the splits of 0050 (4-for-1, 2025-06-18) and 00631L (22-for-1, 2026-03-31).
