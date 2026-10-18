# LM15 Lab — Distributions in Finance

Companion to *From Calculus to Kelly*, Learning Module 15. The notebook rebuilds the module's exhibits and computational examples (up days against the binomial, large moves against the Poisson, normal quantiles and the QQ plot, a lognormal for 23 calendar years, two Student-t fits, tail counts, chords and the two limit regimes) from TAIEX's total-return index, and works the computational practice problems.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM15_lab/LM15_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM15_lab.ipynb
```

`build/make_lab15.py` generates the notebook and this README: edit the generator, not the generated files.

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
| `data/taiex_tr.csv` | `date`, `price`: the closes of TAIEX's total-return index that FinMind's `TaiwanStockTotalReturnIndex` serves, 2003-01-02 → 2026-10-08 |
