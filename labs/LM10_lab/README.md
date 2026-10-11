# LM10 Lab — Quadratic Forms and Covariance Matrices

Companion to *From Calculus to Kelly*, Learning Module 10. The notebook repairs the sector closes, builds the sample covariance matrix of U28 (the 28 leaf sector indices among the 30 TWSE sector indices that FinMind serves daily) three ways, reproduces the module's exhibits and computational examples (portfolio variance, tests of definiteness, rank and pairwise deletion, gradients), and works the computational practice problems.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM10_lab/LM10_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM10_lab.ipynb
```

`build/make_lab10.py` generates the notebook and this README: edit the generator, not the generated files.

## Data (FinMind; not in the repository)

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
| `data/sectors_close_raw.csv` | daily closes of TAIEX and the 30 TWSE sector indices as FinMind's `TaiwanStockPrice` serves them, 2007-07-02 → 2026-10-08, one column per series, empty where a series has no close |
| `data/sectors_close_repairs.csv` | the 561 closes the book repairs (`id`, `date`, `close_1330`: the 13:30:00 value of `TaiwanStockEvery5SecondsIndex`, empty without that file) |
| `data/0050_daily_raw.csv`, `data/00631L_daily_raw.csv`, `data/00679B_daily_raw.csv` | daily close and FinMind `spread` (unadjusted) |
| `data/0050_dividends.csv`, `data/00679B_dividends.csv` | ex-dividend dates, before/after prices and cash dividends (`TaiwanStockDividendResult`) |

FinMind's daily sector series copies some closes from other dates or from another series; Part 1 replaces the 561 listed closes with their 13:30:00 values, 524 of them in this module's sample. `sectors_close_repairs.csv` needs FinMind's paid `TaiwanStockEvery5SecondsIndex`; on the free plan (`fetch_finmind.py --exclude sectors_close/`) its `close_1330` column is empty, Part 1 drops those closes, and the notebook says which of its numbers then differ from the module's.
