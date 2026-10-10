# LM7 Lab — Multivariable Calculus and Lagrange Multipliers

Companion to *From Calculus to Kelly*, Learning Module 7. The notebook builds the total-return series of 0050 and 00679B (all 37 00679B ex-dates, the 0050 split), reproduces the module's exhibits and computational examples, and works the computational practice problems.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM07_lab/LM07_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM07_lab.ipynb
```

`build/make_lab07.py` generates the notebook and this README: edit the generator, not the generated files.

## Data (FinMind, as retrieved 2026-10-10; not in the repository)

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
| `data/0050_daily_raw.csv` | 0050 daily close and FinMind `spread`, 2014-10-31 → 2026-10-08 (unadjusted) |
| `data/00679B_daily_raw.csv` | 00679B daily close and `spread`, 2017-01-17 → 2026-10-08 (unadjusted) |
| `data/0050_dividends.csv` | 0050 ex-dividend dates, before/after prices and cash dividends (`TaiwanStockDividendResult`) |
| `data/00679B_dividends.csv` | 00679B ex-dividend dates (37 quarterly distributions in the window) |

Every close was verified against FinMind's own `spread` column (close − previous close). The only mismatches are ex-dividend days (spread printed as 0) and 0050's 4-for-1 split on 2025-06-18. Two 00679B ex-dates (2019-03-05 and 2025-08-21) had an unchanged close and therefore show no mismatch; their dividends are still applied, and Part 1 checks that the previous close equals FinMind's `before_price` on every ex-date. 0050 was halted 2025-06-11..17 for its split while 00679B traded, so returns are taken between consecutive common trading dates.

00679B tracks the ICE US Treasury 20+ Year Bond Index and is quoted in New Taiwan dollars without a currency hedge, so its returns include USD/TWD moves.
