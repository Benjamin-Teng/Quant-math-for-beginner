# LM5 Lab — Integration

Companion to *From Calculus to Kelly*, Learning Module 5.

## Run

```bash
cd ~/projects && source .venv/bin/activate
uv pip install polars pyarrow numpy scipy sympy matplotlib jupyter
cd LM05_lab && jupyter lab LM05_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. Each part ends with `check(...)` lines that compare a computed value with the number printed in the module and stop if any differs at the printed precision (70 checks).

## Contents

| Part | Rebuilds |
|:--|:--|
| 1 | 0050 total returns (dividends, 4-for-1 split, trading days common with 00631L), verified against FinMind's `spread`; robustness on all 2,906 trading days of 0050 |
| 2 | Left, right and midpoint Riemann sums for a rising deposit rate, with fitted error orders: Example 1, Exhibit 2 |
| 3 | Fundamental theorem, substitution and parts: tail-probability sensitivity to σ, the centre band, LM2's forward curve integrated with SymPy: Examples 2–4 |
| 4 | The Gaussian integral, truncated Pareto moments, 0050's unstable sample kurtosis: Example 5, Exhibit 4 |
| 5 | Monthly rent as right, left and midpoint Riemann sums of a continuous stream; duration; the compounding-convention pitfall: Example 6 |
| 6 | The nine −5% days, thresholds against the normal model and an illustrative Student-t, Mills bounds, tail means, the lognormal mean: Exhibits 1, 6, 7; Examples 7–9 |
| 7 | Trapezoid and Simpson errors and ratios, Richardson extrapolation, the whole-line trapezoid rule, `scipy.integrate.quad`: Example 10, Exhibit 8 |
| 8 | Computational practice problems (1, 2, 4, 5, 7, 8, 9, 10, 11, 13, 14, 15, 16) and an extension on volatility clustering |

## Data (offline snapshot, retrieved 2026-10-10 from FinMind)

| File | Content |
|:--|:--|
| `data/0050_daily_raw.csv` | 0050 daily close and FinMind `spread`, 2014-10-31 → 2026-10-08 (unadjusted) |
| `data/00631L_daily_raw.csv` | 00631L daily close and `spread`, same period (unadjusted); used only to align trading days with the book's standard series |
| `data/0050_dividends.csv` | 0050 ex-dividend dates and cash dividends (`TaiwanStockDividendResult`) |

Every close was verified against FinMind's own `spread` column (close − previous close). The only mismatches are 0050's 22 ex-dividend days in the window and the two split days: 0050 4-for-1 on 2025-06-18 and 00631L 22-for-1 on 2026-03-31. Part 1 re-runs this check. The files are the chunks in the repository's `data/raw/`, concatenated by `build/make_lab05.py`.
