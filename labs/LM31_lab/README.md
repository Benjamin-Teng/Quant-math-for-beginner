# LM31 Lab — Risk Parity, HRP and Volatility Targeting

Companion to *From Calculus to Kelly*, Learning Module 31. The notebook rebuilds the module's exhibits and computational examples:

- risk contributions and shares on E5's first window;
- equal risk contributions and risk budgets by Newton's method, coordinate descent, the fixed point and cvxpy;
- hierarchical risk parity by hand and at every signal, with the author's call to SciPy and linking on the distance itself;
- U28's correlation heatmap, tree and halves;
- R6 and R7 out of sample, R8's exposure at every signal and its holding months, judged by their ratios and by QLIKE.

It also tries a risk-triggered R8, works the computational practice problems and ends with a GARCH-scaled R8.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM31_lab/LM31_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM31_lab.ipynb
```

`build/make_lab31.py` generates the notebook and this README: edit the generator, not the generated files.

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
| `data/e5_estimation.csv` | E5's estimation frame: `base`, `date`, `fund`, `R`, the one-session total returns of 0050, 00646, 00679B, 00635U and 00642U on the 2,362 dates on which all five have one (FinMind `TaiwanStockPrice`, `TaiwanStockDividendResult`, `TaiwanStockSplitPrice`) |
| `data/e5_wealth.csv` | E5's wealth frame: every session after the base close of 2017-01-17, with `traded` per fund |
| `data/rule_targets.csv` | the through case's trades (`data/vol5_rules.py`): rule, signal, trade, the five target exposures, exposure, turnover, cost |
| `data/rule_wealth.csv` | the eight rules' net and gross wealth paths from the first trade |
| `data/sectors_close_raw.csv` | the closes FinMind's `TaiwanStockPrice` serves for TAIEX and the TWSE sector indices |
| `data/sectors_close_repairs.csv` | the sector closes the book repairs, with their 13:30:00 values from `TaiwanStockEvery5SecondsIndex` (empty on the free plan, where those closes are dropped) |
