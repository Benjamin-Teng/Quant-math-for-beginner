# LM12 Lab — Cholesky, SVD and Least Squares

Companion to *From Calculus to Kelly*, Learning Module 12. The notebook repairs the sector closes, rebuilds the module's exhibits and computational examples (TAIEX rebuilt from its sector indices, the SVD and conditioning, December 2008's rank-deficient fit, Cholesky factors and whitened returns), and works the computational practice problems.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM12_lab/LM12_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM12_lab.ipynb
```

`build/make_lab12.py` generates the notebook and this README: edit the generator, not the generated files.

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
| `data/sectors_close_raw.csv` | the daily closes FinMind's `TaiwanStockPrice` serves for TAIEX and the 30 TWSE sector indices, 2007-07-02 → 2026-10-08, one column per series, empty where a series has no close |
| `data/sectors_close_repairs.csv` | `id`, `date`, `close_1330`: the 561 closes that FinMind copied from another date or series, each with its official 13:30:00 value from `TaiwanStockEvery5SecondsIndex` |

The first part of the notebook replaces each listed close with its 13:30:00 value. `TaiwanStockEvery5SecondsIndex` is a paid FinMind dataset: on the free plan `close_1330` is empty, the notebook drops those closes instead (never estimating one), and the common sample keeps 4,307 of its 4,382 returns. The notebook then says which of its numbers differ from the module's; December 2008, the last 250 returns and the calendar years 2014, 2023, 2024 and 2026 do not change.
