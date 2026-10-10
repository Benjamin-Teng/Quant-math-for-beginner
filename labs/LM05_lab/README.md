# LM5 Lab — Integration

Companion to *From Calculus to Kelly*, Learning Module 5.

## Run

From the repository root:

```bash
uv sync      # installs the locked Python environment (uv.lock)
uv run --with jupyterlab jupyter lab labs/LM05_lab/LM05_lab.ipynb
```

To re-execute the saved notebook, inside `labs/LM05_lab`:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM05_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. Each part ends with `check(...)` lines
that compare a computed value with the number printed in the module and stop if any differs at the printed precision
(115 checks).

## Contents

| Part | Rebuilds |
|:--|:--|
| 1 | 0050 total returns (dividends, 4-for-1 split, trading days common with 00631L), verified against FinMind's `spread`; robustness on all 2,906 trading days of 0050 |
| 2 | Left, right and midpoint Riemann sums for a rising deposit rate and their error orders (Example 1, Exhibit 2) |
| 3 | Fundamental theorem, substitution and parts: tail sensitivity to σ, the centre band, LM2's forward curve integrated with SymPy (Examples 2–4) |
| 4 | The Gaussian integral, truncated Pareto moments, 0050's unstable sample kurtosis (Example 5, Exhibit 4) |
| 5 | Monthly rent as right, left and midpoint Riemann sums of a continuous stream; duration; the compounding-convention pitfall (Example 6) |
| 6 | The nine −5% days, thresholds against the normal model and an illustrative Student-t, Mills bounds, tail means, the lognormal mean (Exhibit 1, Exhibit 6, Exhibit 7, Examples 7–9) |
| 7 | Trapezoid and Simpson errors and ratios, Richardson extrapolation, the whole-line trapezoid rule, `scipy.integrate.quad` (Example 10, Exhibit 8) |
| 8 | Computational practice problems (1, 2, 4, 5, 7, 8, 9, 10, 11, 13, 14, 15, 16) and an extension on volatility clustering |

## Data (FinMind, retrieved 2026-10-10; not in the repository)

The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline. The first command reads your FinMind API token from the environment variable `FINMIND_TOKEN`:

```bash
uv run python data/fetch_finmind.py   # rebuilds and verifies data/raw/
uv run python data/make_lab_data.py   # writes every lab's data/ folder
```

The folder then holds:

| File | Content |
|:--|:--|
| `data/0050_daily_raw.csv` | 0050 daily close and FinMind `spread`, 2014-10-31 → 2026-10-08 (unadjusted) |
| `data/00631L_daily_raw.csv` | 00631L daily close and `spread`, same period (unadjusted); used only to align trading days with the book's standard series |
| `data/0050_dividends.csv` | 0050 ex-dividend dates and cash dividends (`TaiwanStockDividendResult`) |

Every close was verified against FinMind's own `spread` column (close − previous close). The only mismatches are
0050's 22 ex-dividend days in the window and the two split days: 0050 4-for-1 on 2025-06-18 and 00631L 22-for-1 on
2026-03-31. Part 1 re-runs this check.
