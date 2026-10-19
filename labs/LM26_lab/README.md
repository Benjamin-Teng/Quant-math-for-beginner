# LM26 Lab — Time Series II: Volatility Models

Companion to *From Calculus to Kelly*, Learning Module 26. The notebook rebuilds the module's exhibits and computational examples (the ARCH test, EWMA by hand and in hindsight, GARCH(1,1) fitted by hand and with arch under normal and Student-t innovations, standardized residuals, the term structure of a forecast, what GARCH explains with two simulated experiments, the volatility signature and the ratios of realized variances by year, and the out-of-sample comparison of six variance forecasts), computes the widget's starting values, works the computational practice problems and ends with an asymmetric GARCH.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM26_lab/LM26_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM26_lab.ipynb
```

It ran in about 25 seconds when the book was built, although the out-of-sample comparison refits two GARCH models every month, about 1,300 fits in all.

`build/make_lab26.py` generates the notebook and this README: edit the generator, not the generated files.

## Data (FinMind; not in the repository)

The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline. The realized variances come with the repository (`data/derived/vol4_rv.csv`); rebuilding them needs the 5-second TAIEX download, `uv run python data/fetch_intraday.py --series taiex5s` (5,351 requests, about nine hours on a free registered FinMind account at 600 calls an hour, re-run after each hourly stop).

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
| `data/vol4_rv.csv` | a copy of `data/derived/vol4_rv.csv`: per session from 2005-01-03, the sampling interval, the realized variances of 09:30:00–13:30:00 at nine intervals with their return counts, and the squared opening change `o2` (derived from FinMind `TaiwanVariousIndicators5Seconds` and `TaiwanStockPrice`; TWSE the original source; per-day statistics only) |
| `data/taiex5s_2025/` | optional, for Part 9 only: the 243 files of 2025 from `uv run python data/fetch_intraday.py --series taiex5s --from 2025-01-01 --to 2025-12-31`, copied from `data/raw/intraday/taiex5s/2025/` |
