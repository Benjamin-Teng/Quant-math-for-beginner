# LM28 Lab — Mean–Variance Optimization

Companion to *From Calculus to Kelly*, Learning Module 28. The notebook rebuilds the module's exhibits and computational examples:

- the minimum-variance portfolio by hand, with its covariances, betas and risk shares;
- the frontier, equal weights inside it, and two-fund separation;
- the tangency portfolio at three riskless rates, the tangency betas and the capital market line;
- the sensitivity of the tangency weights to the means, exact and by the Jacobian;
- the first window's two portfolios held to October 2026 and the split of their variance;
- minimum variance on U28's 28 sector indices and its halves;
- the KKT system against cvxpy's OSQP and CLARABEL, with the sign of the duals.

It also computes the widget's starting values, works the computational practice problems, compares the 92 windows' minimum-variance portfolios with the through case's R3, and ends by adding the funds one at a time.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM28_lab/LM28_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM28_lab.ipynb
```

`build/make_lab28.py` generates the notebook and this README: edit the generator, not the generated files.

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
| `data/e5_estimation.csv` | `base`, `date`, `fund`, `R`: E5's estimation frame, the dates on which all five funds have a one-session total return, 2017-01-18 → 2026-10-08 (derived from FinMind `TaiwanStockPrice`, `TaiwanStockDividendResult` and `TaiwanStockSplitPrice`) |
| `data/e5_wealth.csv` | `base`, `date`, `fund`, `R`, `traded`: E5's wealth frame, every session, a halted fund earning 0 and booking its spanning return when it trades again |
| `data/rule_targets.csv` | the through case's trades (`data/vol5_rules.py`); the lab reads R3's 92 signal and trade dates and its long-only minimum-variance targets |
| `data/sectors_close_raw.csv` | the daily closes FinMind's `TaiwanStockPrice` serves for TAIEX and the 30 TWSE sector indices, one column per series |
| `data/sectors_close_repairs.csv` | `id`, `date`, `close_1330`: the 561 closes that FinMind copied from another date or series, each with its official 13:30:00 value from `TaiwanStockEvery5SecondsIndex` (a paid dataset: on the free plan the values are empty and the notebook drops those closes) |
