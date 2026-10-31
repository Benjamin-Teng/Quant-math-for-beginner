# LM29 Lab — Convex Optimization in Practice

Companion to *From Calculus to Kelly*, Learning Module 29. The notebook rebuilds the module's exhibits and computational examples:

- convexity checked on random chords;
- R3 and R4 at all 92 signals by `nnls` on the Cholesky factor and by cvxpy, against the through case's targets;
- the KKT quantities of R4, the shadow prices and the cap on R3;
- U28's long-only minimum variance;
- the frontiers with and without long-only limits, a linear program and the solver statuses;
- costs in the objective: one rebalance and the cost sweep along R3's path;
- the solver audit in daily and annual units.

It also works the computational practice problems and ends with an enumeration of R4's active sets.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM29_lab/LM29_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM29_lab.ipynb
```

`build/make_lab29.py` generates the notebook and this README: edit the generator, not the generated files.

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
| `data/e5_estimation.csv` | E5's estimation frame: the dates on which 0050, 00646, 00679B, 00635U and 00642U all have a one-session total return, 2017-01-18 → 2026-10-08 (FinMind `TaiwanStockPrice`, `TaiwanStockDividendResult`, `TaiwanStockSplitPrice`) |
| `data/e5_wealth.csv` | E5's wealth frame: every TAIEX session, a halted fund earning 0, with a `traded` flag |
| `data/rule_targets_R3_R4.csv` | the through case's targets of R3 and R4 at each of the 92 signals (`data/vol5_rules.py`) |
| `data/sectors_close_raw.csv`, `data/sectors_close_repairs.csv` | the TWSE sector closes (FinMind `TaiwanStockPrice`) and the copied closes with their 13:30:00 values (`TaiwanStockEvery5SecondsIndex`, a paid dataset; on the free plan those closes are dropped, and the U28 numbers differ) |
