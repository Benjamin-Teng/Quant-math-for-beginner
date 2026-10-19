# LM23 Lab — Linear Regression

Companion to *From Calculus to Kelly*, Learning Module 23. The notebook repairs the sector closes, rebuilds the module's exhibits and computational examples, and works the computational practice problems. It covers OLS by hand and in statsmodels, confidence and prediction bands, hat values, and White and Newey–West standard errors on LM18's paths and on overlapping sums. It also covers the market model, rolling betas, a regression hedge, LM2's slope, the 28 alphas and their corrections, and a factor named in advance.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM23_lab/LM23_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM23_lab.ipynb
```

`build/make_lab23.py` generates the notebook and this README: edit the generator, not the generated files.

## Data (FinMind; not in the repository)

The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

The same steps in a shell (`data/raw/` and this folder's `data/` are git-ignored):

```bash
export FINMIND_TOKEN=...               # your FinMind API token
uv run python data/fetch_finmind.py    # rebuilds and verifies data/raw/
uv run python data/make_lab_data.py    # writes every lab's data/ folder
```

`fetch_finmind.py` checks every file against `data/raw_manifest.json`. The notebook reads only the files in its own `data/` folder:

| File | Content |
|:--|:--|
| `data/sectors_close_raw.csv` | the daily closes FinMind's `TaiwanStockPrice` serves for TAIEX and the 30 TWSE sector indices, one column per series |
| `data/sectors_close_repairs.csv` | `id`, `date`, `close_1330`: the 561 closes that FinMind copied from another date or series, each with its official 13:30:00 value from `TaiwanStockEvery5SecondsIndex` (a paid dataset: on the free plan the values are empty and the notebook drops those closes) |
| `data/taiex_tr.csv` | `date`, `price`: the TAIEX total-return index (FinMind `TaiwanStockTotalReturnIndex`), 2003-01-02 → 2026-10-08 |
| `data/0050_daily_raw.csv`, `data/00631L_daily_raw.csv` | `date`, `close`, `spread` of the two funds (`TaiwanStockPrice`) |
| `data/0050_dividends.csv` | 0050's cash dividends (`TaiwanStockDividendResult`) |
