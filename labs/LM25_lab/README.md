# LM25 Lab — Time Series I: ARMA, Unit Roots and Cointegration

Companion to *From Calculus to Kelly*, Learning Module 25. The notebook builds TX23 (the TX near-month future against the TAIEX) from the daily futures file with the module's roll rule, rebuilds the module's exhibits and computational examples (stationarity, AR and MA models, tests for autocorrelation, unit-root tests, spurious regression and cointegration, the basis as a time series), runs the four simulation experiments and works the computational practice problems.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM25_lab/LM25_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM25_lab.ipynb
```

`build/make_lab25.py` generates the notebook and this README: edit the generator, not the generated files.

## Data (FinMind; not in the repository)

The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

The same steps in a shell (`data/raw/` and this folder's `data/` are git-ignored):

```bash
export FINMIND_TOKEN=...               # your FinMind API token
uv run python data/fetch_finmind.py    # rebuilds and verifies data/raw/
uv run python data/make_lab_data.py    # writes every lab's data/ folder
```

`fetch_finmind.py` checks every file against `data/raw_manifest.json`. The notebook reads only the files in its own `data/` folder, all from FinMind's free datasets:

| File | Content |
|:--|:--|
| `data/taiex_tr.csv` | `date`, `price`: the daily closes of the TAIEX total-return index (FinMind `TaiwanStockTotalReturnIndex`, data_id TAIEX), 2003-01-02 → 2026-10-08 |
| `data/taiex_price.csv` | `date`, `close`, `spread`: the TAIEX price closes (FinMind `TaiwanStockPrice`), on the same 5,850 dates |
| `data/tx_daily.csv` | `date`, `contract_date`, `close`, `spread`, `settlement_price`, `volume`, `open_interest`: the regular-session rows of the monthly TX contracts (FinMind `TaiwanFuturesDaily`, data_id TX), 1998-07-21 → 2026-10-16 |
