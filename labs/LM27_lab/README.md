# LM27 Lab — Portfolio Return and Risk

Companion to *From Calculus to Kelly*, Learning Module 27. The notebook rebuilds the module's exhibits and computational examples:

- E5's two frames, the estimation frame and the wealth frame, from the raw closes, distributions and split;
- the June 2025 span and the drift of a buy-and-hold book;
- the wealth recursion with costs, for R1 and R2 from their per-date targets, and R1's trade of 1 April 2026;
- correlations by frequency with both standard errors and the funds' kurtosis;
- means, variances, the diversification ratio, Euler's risk split, the slope check and a switch;
- R1's risk shares in the 92 trailing windows, and the factor split of an equal-weight U28 book.

It also checks the widget's starting values, works the computational practice problems and ends with R2's risk shares in the 92 windows.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM27_lab/LM27_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM27_lab.ipynb
```

`build/make_lab27.py` generates the notebook and this README: edit the generator, not the generated files.

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
| `data/<fund>__2016-12-01__2026-10-08.csv` | `date, open, max, min, close, spread, volume` of 0050, 00646, 00679B, 00635U and 00642U (FinMind `TaiwanStockPrice`) |
| `data/0050_dividends__…`, `data/00679B_dividends__…` | the cash distributions (`TaiwanStockDividendResult`) |
| `data/splits__2016-12-01__2026-10-08.csv` | every split in `TaiwanStockSplitPrice`, among them 0050's 4-for-1 of 2025-06-18 |
| `data/taiex_tr.csv` | `date`, `price`: the TAIEX total-return closes (`TaiwanStockTotalReturnIndex`), whose dates are TR23's calendar |
| `data/e5_estimation.csv`, `data/e5_wealth.csv` | E5's two frames in long form, built by `data/vol5_series.py` |
| `data/rule_targets_R1_R2.csv`, `data/rule_wealth_net_R1_R2.csv` | R1's and R2's trades and net wealth paths, built by `data/vol5_rules.py` |
| `data/sectors_close_raw.csv`, `data/sectors_close_repairs.csv` | the sector and TAIEX closes and the repairs of the closes FinMind copied from other dates or series (the repair values need FinMind's `TaiwanStockEvery5SecondsIndex`, a paid dataset; without them Part 8 drops those closes) |
