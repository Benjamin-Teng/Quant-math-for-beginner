# LM4 Lab — Optimization in One Variable

Companion to *From Calculus to Kelly*, Learning Module 4.

## Run

```bash
cd ~/projects && source .venv/bin/activate
uv pip install polars pyarrow numpy scipy matplotlib jupyter
cd LM04_lab && jupyter lab LM04_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. Each part ends with `check(...)` lines that compare the computed values with the numbers printed in the module and stop if any differs at the printed precision.

## Contents

| Part | Rebuilds |
|:--|:--|
| 1 | 0050 total returns (dividends, 4-for-1 split, common trading days with 00631L), verified against FinMind's `spread` |
| 2 | Empirical growth function, exact Kelly leverage 5.42, zero-growth leverage 9.74: Exhibits 1 and 3, Examples 1 and 3 |
| 3 | Year-by-year Kelly leverages and corner solutions on [0, 2]: Exhibit 4, Example 4 |
| 4 | Binary Kelly bet, sensitivity to the win probability, envelope derivative, relative entropy: Exhibit 5, Examples 5 and 6 |
| 5 | Bisection and Newton traces, yield to maturity, moment truncations, two-IRR pitfall: Exhibit 6, Examples 7 and 8 |
| 6 | Fractional Kelly, flat top, financing via the envelope theorem, sampling error, rolling three-year Kelly: Exhibits 7 and 8, Examples 9 and 10 |
| 7 | `scipy.optimize`: `brentq`, `newton`, bounded `minimize_scalar`, and why the unbounded search fails |
| 8 | Computational practice problems (3, 4, 6, 7, 8, 9, 10, 13, 14, 15) and a walk-forward Kelly extension exercise |

## Data (FinMind, retrieved 2026-10-10; not in the repository)

FinMind's licence does not allow its raw data in a public repository, so `data/` is git-ignored. Build it from the repository root with your own FinMind token:

```bash
export FINMIND_TOKEN=...           # your FinMind API token
python3 data/fetch_finmind.py      # rebuilds data/raw/ and checks every file against data/raw_manifest.json
python3 data/make_lab_data.py      # writes this folder and every other lab's
```

The folder then holds:

| File | Content |
|:--|:--|
| `data/0050_daily_raw.csv` | 0050 daily close and FinMind `spread`, 2014-10-31 → 2026-10-08 (unadjusted) |
| `data/00631L_daily_raw.csv` | 00631L daily close and `spread`, same period (unadjusted); used only for the common trading days |
| `data/0050_dividends.csv` | 0050 ex-dividend dates and cash dividends (`TaiwanStockDividendResult`) |

The files are generated from the verified chunks in `data/raw/` by `build/make_lab04.py`. Every close was checked against FinMind's own `spread` column (close − previous close); the only mismatches are 0050's 22 ex-dividend days in the window and the two split days (0050 4-for-1 on 2025-06-18, 00631L 22-for-1 on 2026-03-31). Part 1 re-runs the check.

The in-sample Kelly leverage computed here describes 2014–2026; it is not a recommendation (see Section 7 of the module).
