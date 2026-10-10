# LM4 Lab — Optimization in One Variable

Companion to *From Calculus to Kelly*, Learning Module 4.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM04_lab/LM04_lab.ipynb
```

To re-execute it in place, run this inside `labs/LM04_lab/`:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM04_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. Each part ends with `check(...)` lines that compare the computed values with the numbers printed in the module and stop if any differs at the printed precision.

## Contents

| Part | Rebuilds |
|:--|:--|
| 1 | 0050 total returns (dividends, 4-for-1 split, common trading days with 00631L), verified against FinMind's `spread` |
| 2 | The case table, the growth curve, exact Kelly leverage 5.42 and zero-growth leverage 9.74; the quadratic rule and why it overshoots (mainly excess kurtosis; the two ±10% days explain about a quarter) |
| 3 | Kelly leverages in the full calendar years 2015–2025 (and the partial years left out), corner solutions on [0, 2] |
| 4 | Binary Kelly bet (gain b, loss a per unit staked), sensitivity to the win probability, relative entropy |
| 5 | Bisection and Newton traces (in double precision and in 50-digit arithmetic), the degree of the cleared Kelly condition, yield to maturity, two-IRR pitfall |
| 6 | Fractional Kelly, flat top, financing via the envelope theorem, the sampling-error band of the Kelly leverage, rolling three-year Kelly |
| 7 | `scipy.optimize`: the module's code, `brentq`, `newton`, bounded `minimize_scalar`, and why the unbounded search fails |
| 8 | Computational practice problems (3, 4, 6, 7, 8, 11, 12, 13) and a walk-forward Kelly extension exercise |

Exhibit and example numbers in the notebook are generated from the labels in `src/lm04.md`, so they always match the module. `build/make_lab04.py` writes the notebook: change the generator and regenerate rather than editing the notebook.

## Data (FinMind; not in the repository)

The notebook reads FinMind files that you download once with your own token. FinMind's licence does not allow the book to redistribute the data, so `data/` is git-ignored. From the repository root:

```bash
export FINMIND_TOKEN=...              # your FinMind API token
uv run python data/fetch_finmind.py   # rebuilds data/raw/
uv run python data/make_lab_data.py   # writes this folder and every other lab's
```

`fetch_finmind.py` checks every raw file against `data/raw_manifest.json`. After that, the notebook runs offline. The folder then holds:

| File | Content |
|:--|:--|
| `data/0050_daily_raw.csv` | 0050 daily close and FinMind `spread`, 2014-10-31 → 2026-10-08 (unadjusted) |
| `data/00631L_daily_raw.csv` | 00631L daily close and `spread`, same period (unadjusted); used only for the common trading days |
| `data/0050_dividends.csv` | 0050 ex-dividend dates and cash dividends (`TaiwanStockDividendResult`) |

These are the windows the book retrieved on 2026-10-10. Every close was checked against FinMind's own `spread` column (close − previous close); the only mismatches are 0050's 22 ex-dividend days in the window and the two split days (0050 4-for-1 on 2025-06-18, 00631L 22-for-1 on 2026-03-31). Part 1 re-runs the check.

The in-sample Kelly leverage computed here describes 2014–2026; it is not a recommendation (see Section 7 of the module).
