# LM11 Lab — Eigen-decomposition and PCA

Companion to *From Calculus to Kelly*, Learning Module 11. The notebook repairs the TWSE sector closes that FinMind serves wrongly, builds the U28 sample (the 28 leaf sector indices, 2 December 2008 to 8 October 2026) and LM7's 0050/00679B pair, reproduces the module's exhibits and computational examples, and works the computational practice problems.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM11_lab/LM11_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM11_lab.ipynb
```

`build/make_lab11.py` generates the notebook and this README: edit the generator, not the generated files.

## Data (FinMind, retrieved 2026-10-10 and 2026-10-11; not in the repository)

The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

The same steps in a shell (`data/raw/` and this folder's `data/` are git-ignored):

```bash
export FINMIND_TOKEN=...               # your FinMind API token
uv run python data/fetch_finmind.py    # rebuilds and verifies data/raw/
uv run python data/make_lab_data.py    # writes every lab's data/ folder
```

`fetch_finmind.py` checks every file against `data/raw_manifest.json`. The notebook reads only the files in its own `data/` folder, which then holds:

| File | Content |
|:--|:--|
| `data/sectors_close_raw.csv` | daily closes of TAIEX and the 30 TWSE sector indices as `TaiwanStockPrice` serves them, one column per series, empty where a series has no close |
| `data/sectors_close_repairs.csv` | the 561 closes FinMind serves wrongly (`id`, `date`) with their official 13:30:00 value from `TaiwanStockEvery5SecondsIndex` (`close_1330`, empty on FinMind's free plan) |
| `data/0050_daily_raw.csv`, `data/00631L_daily_raw.csv`, `data/00679B_daily_raw.csv` | daily closes and FinMind `spread` (unadjusted) |
| `data/0050_dividends.csv`, `data/00679B_dividends.csv` | ex-dividend dates, before/after prices and cash dividends (`TaiwanStockDividendResult`) |

Part 1 replaces each listed close with its 13:30:00 value; without that value (FinMind's free plan) it drops the close, U28's sample keeps 4,307 of its 4,382 returns, and most full-sample, half-sample and per-year numbers change (Part 1 lists which keep their values). Sector indices are price indices; the ETF series are total returns with every dividend and the 0050 and 00631L splits applied.
