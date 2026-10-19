# LM20 Lab — Estimation Theory and Maximum Likelihood

Companion to *From Calculus to Kelly*, Learning Module 20. The notebook rebuilds the module's exhibits and computational examples and works the computational practice problems.

The notebook covers the sampling distributions of a mean and a volatility, standard errors by sampling interval and the coverage of confidence intervals. It fits the normal and Student-t models by maximum likelihood, with their observed information and profile likelihood. Then come the delta method for the volatility, the Kelly fraction and the Sharpe ratio, and the Hill estimator.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM20_lab/LM20_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM20_lab.ipynb
```

`build/make_lab20.py` generates the notebook and this README: edit the generator, not the generated files.

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
| `data/taiex_tr.csv` | `date`, `price`: the daily closes of the TAIEX total-return index (FinMind `TaiwanStockTotalReturnIndex`, data_id TAIEX), 2003-01-02 → 2026-10-08 |
| `data/0050_daily_raw.csv`, `data/00631L_daily_raw.csv` | `date`, `close`, `spread`: FinMind `TaiwanStockPrice` closes of 0050 and 00631L from 2014-10-31, for LM4's 2,902 common-date 0050 returns |
| `data/0050_dividends.csv` | 0050's cash dividends from `TaiwanStockDividendResult` |
| `data/sectors_close_raw.csv` | the daily closes FinMind's `TaiwanStockPrice` serves for TAIEX and the 30 TWSE sector indices (Problem 6) |
| `data/sectors_close_repairs.csv` | `id`, `date`, `close_1330`: the closes that FinMind copied from another date or series, each with its official 13:30:00 value from `TaiwanStockEvery5SecondsIndex` (a paid dataset; empty on the free plan, where Problem 6 drops those closes) |
