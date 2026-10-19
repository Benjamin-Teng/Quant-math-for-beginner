# LM22 Lab — Resampling Methods

Companion to *From Calculus to Kelly*, Learning Module 22. The notebook rebuilds the module's exhibits and computational examples (the ideal bootstrap of five returns; iid and block-bootstrap intervals for TAIEX's Sharpe ratio, Kelly fraction and volatility, against the delta method and SciPy; what resampling days destroys; moving, circular and stationary blocks checked against arch; the block length; intervals for LM11's, LM16's and LM18's estimates; bootstrap tests of the mean) with the seeds the module prints, works the computational practice problems, and ends with an extension exercise. A full run takes a few minutes.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM22_lab/LM22_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM22_lab.ipynb
```

`build/make_lab22.py` generates the notebook and this README: edit the generator, not the generated files. Printed resampling numbers rest on the NumPy version that `uv.lock` pins: NumPy promises identical random streams only for the same version and build.

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
| `data/sectors_close_raw.csv` | the daily closes FinMind's `TaiwanStockPrice` serves for TAIEX and the 30 TWSE sector indices, one column per series, empty where a series has no close |
| `data/sectors_close_repairs.csv` | `id`, `date`, `close_1330`: the 561 closes that FinMind copied from another date or series, each with its official 13:30:00 value from `TaiwanStockEvery5SecondsIndex` |

The first part of the notebook replaces each listed sector close with its 13:30:00 value. `TaiwanStockEvery5SecondsIndex` is a paid FinMind dataset: on the free plan `close_1330` is empty, the notebook drops those closes instead (never estimating one), and the U28 sample keeps 4,307 of its 4,382 returns. The notebook then says which of its U28 numbers differ from the module's; every TR23 number is unchanged.
