# LM13 Lab — Probability Foundations and Bayes

Companion to *From Calculus to Kelly*, Learning Module 13. The notebook rebuilds the module's exhibits and computational examples from the TAIEX total-return index (events and the axioms, conditional probability after a big move, independence of consecutive days, total probability and Bayes' rule across the two limit regimes, the empirical distribution function), recounts every threshold with exact fractions, and works the computational practice problems.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM13_lab/LM13_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM13_lab.ipynb
```

`build/make_lab13.py` generates the notebook and this README: edit the generator, not the generated files. Each `show` line prints a value beside the number the module prints and stops if they differ.

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
| `data/taiex_tr.csv` | `date`, `price`: the daily closes of the TAIEX total-return index (FinMind `TaiwanStockTotalReturnIndex`, data_id TAIEX, cash dividends reinvested), 2003-01-02 → 2026-10-08, 5,850 rows |
