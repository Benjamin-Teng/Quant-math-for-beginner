# LM30 Lab — Estimation Error and Robust Portfolios

Companion to *From Calculus to Kelly*, Learning Module 30. The notebook rebuilds the module's exhibits and computational examples:

- experiments 1 and 2: plug-in portfolios simulated from the first window's estimates, the error of R1's risk shares and the window the plug-in needs;
- Ledoit–Wolf shrinkage by hand and with scikit-learn, its spectrum and condition number;
- U28's short windows, the pseudoinverse and experiment 3;
- R5 re-implemented and checked against the through case's targets, and the realized volatility of R1, R3 and R5;
- the long-only constraint as an adjusted matrix, with cvxpy's dual values;
- Black–Litterman with one view, resampled weights, the single-index matrix and the repairs of LM10's pairwise correlation matrix.

It also works the computational practice problems and ends with LM7's monthly re-estimation question, answered with shrinkage.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM30_lab/LM30_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM30_lab.ipynb
```

`build/make_lab30.py` generates the notebook and this README: edit the generator, not the generated files.

## Data (FinMind; not in the repository)

The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

The same steps in a shell (`data/raw/` and this folder's `data/` are git-ignored):

```bash
export FINMIND_TOKEN=...               # your FinMind API token
uv run python data/fetch_finmind.py    # rebuilds and verifies data/raw/
uv run python data/make_lab_data.py    # writes every lab's data/ folder
```

The notebook reads only the files in its own `data/` folder:

| File | Content |
|:--|:--|
| `data/e5_estimation.csv` | E5's estimation frame, long format (`base`, `date`, `fund`, `R`): the dates on which 0050, 00646, 00679B, 00635U and 00642U all have a one-session total return, 2017-01-18 → 2026-10-08 (FinMind `TaiwanStockPrice`, `TaiwanStockDividendResult`, `TaiwanStockSplitPrice`) |
| `data/e5_wealth.csv` | E5's wealth frame, the same columns and `traded`: every session, a halted fund earning 0 |
| `data/rule_targets.csv` | the through case's target exposures of R1–R8 at each signal, with trade dates, turnover and cost (`data/vol5_rules.py`) |
| `data/rule_wealth.csv` | each rule's net and gross wealth after each session's trade, from the first trade |
| `data/sectors_close_raw.csv` | the closes of TAIEX and the TWSE sector indices as FinMind `TaiwanStockPrice` serves them |
| `data/sectors_close_repairs.csv` | the closes FinMind copied from another date or series, with their 13:30:00 values from `TaiwanStockEvery5SecondsIndex` (a paid dataset; empty on the free plan, and the notebook then drops those closes and says so) |
