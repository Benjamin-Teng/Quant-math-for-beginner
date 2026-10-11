# LM9 Lab — Linear Systems, Inverses and Rank

Companion to *From Calculus to Kelly*, Learning Module 9. The notebook repairs the sector closes, rebuilds the four-day case of 7–10 April 2025 in exact arithmetic, draws both pictures of a linear system, computes determinants, Cramer's rule, elimination and inverses, counts solutions with the rank, builds the two 50/50 mixes of Semiconductor and Financial, and works the computational practice problems.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM09_lab/LM09_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM09_lab.ipynb
```

`build/make_lab09.py` generates the notebook and this README: edit the generator, not the generated files.

## Data (FinMind, retrieved 2026-10-11; not in the repository)

The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

The same steps in a shell (`data/raw/` and this folder's `data/` are git-ignored):

```bash
export FINMIND_TOKEN=...               # your FinMind API token
uv run python data/fetch_finmind.py    # rebuilds and verifies data/raw/
uv run python data/make_lab_data.py    # writes every lab's data/ folder
```

On FinMind's free plan, run `uv run python data/fetch_finmind.py --exclude sectors_close/` instead: the repair values come from a paid dataset. The notebook then drops the listed closes and says which of its numbers change.

The notebook reads only the files in its own `data/` folder:

| File | Content |
|:--|:--|
| `data/sectors_close_raw.csv` | `date`, then TAIEX and the 30 TWSE sector indices: the daily closes FinMind's `TaiwanStockPrice` serves, 2007-07-02 → 2026-10-08, empty where a series has no close |
| `data/sectors_close_repairs.csv` | `id`, `date`, `close_1330`: the 561 closes FinMind copied from another date or series, with the official 13:30:00 value of `TaiwanStockEvery5SecondsIndex` (empty on the free plan) |

Part 1 replaces each listed close by its 13:30:00 value, or drops it when the value is missing. The sector indices are market-value-weighted price indices; `Electronic` and `ChemicalBiotechnologyMedicalCare` aggregate other sector indices and stay out of the 28-sector set U28.
