# LM18 Lab — Monte Carlo Simulation and the Bootstrap

Companion to *From Calculus to Kelly*, Learning Module 18. The notebook rebuilds the module's exhibits and computational examples (TR23's five-year windows, seeds and common random numbers, the inverse transform, the Monte Carlo estimator and its error, Monte Carlo against quadrature, variance reduction and the iid bootstrap) with the seeds the module prints, and works the computational practice problems.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM18_lab/LM18_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM18_lab.ipynb
```

`build/make_lab18.py` generates the notebook and this README: edit the generator, not the generated files. Printed simulation numbers rest on the NumPy version that `uv.lock` pins: NumPy promises identical random streams only for the same version and build.

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
| `data/taiex_tr.csv` | `date`, `price`: the closes of the TAIEX total-return index (FinMind's `TaiwanStockTotalReturnIndex`, data_id TAIEX), 2003-01-02 → 2026-10-08 |
