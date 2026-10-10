# LM2 Lab — Limits and Derivatives

Companion to *From Calculus to Kelly*, Learning Module 2.

## Run

From the repository root, after building `data/` (see below):

```bash
uv sync                  # install the locked Python environment (uv.lock)
uv run --with jupyterlab jupyter lab labs/LM02_lab/LM02_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. It is regenerated from the repository
root by `uv run python build/make_lab02.py` and re-executed from inside this folder with

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM02_lab.ipynb
```

## Contents

| Part | Topic |
|:--|:--|
| 1 | Limits: the squeeze on $(e^x-1)/x$, the perpetuity limit |
| 2 | Difference quotients and the exact derivative of a 10-year 2% bond; duration |
| 3 | The TX account: near-month roll, the motivating case, leverage path, April 2025 and margin calls |
| 4 | Elasticity of levered positions from 0050 data: 00631L and a margin-financed account |
| 5 | Finite differences: error versus step $\Delta y$ on a log–log grid, orders of convergence, rounding |
| 6 | Duration by bumping yields; SymPy checks |
| 7 | Computational practice problems; extension: Richardson extrapolation |

## Data (FinMind; not in the repository)

The notebook reads FinMind files that you download once with your own token. FinMind's licence does not allow the
book to redistribute the data, so `data/` is git-ignored. From the repository root:

```bash
export FINMIND_TOKEN=...              # your FinMind API token
uv run python data/fetch_finmind.py   # rebuild data/raw/, checked against
                                      # data/raw_manifest.json
uv run python data/make_lab_data.py   # write this folder and every
                                      # other lab's
```

After that, the notebook runs offline. The folder then holds the files the module uses (FinMind, retrieved
2026-10-10):

| File | Content |
|:--|:--|
| `data/TX__2025-04-01__2025-10-31.csv` | `TaiwanFuturesDaily`, TX, regular session: `date, contract_date, close, settlement_price, volume, open_interest`, six contract months per day |
| `data/TAIEX__2025-04-01__2025-10-31.csv` | `TaiwanStockPrice`, TAIEX: `date, close, spread` |
| `data/0050_daily_raw.csv` | 0050 daily close and FinMind `spread`, 2014-10-31 → 2026-10-08 (unadjusted; FinMind chunks concatenated) |
| `data/00631L_daily_raw.csv` | 00631L daily close and `spread`, same period (unadjusted) |
| `data/0050_dividends.csv` | 0050 ex-dividend dates and cash dividends (`TaiwanStockDividendResult`) |

Notes on the TX file: on each expiry day the expiring contract shows `settlement_price = 0.0` (its final settlement
price is not in the file), and thinly traded back months can show `close = 0.0` with no trades. The notebook uses
settlement prices only and rolls to the next month at the close of the day before expiry.

Every stock and index close was verified against FinMind's own `spread` column (close − previous close). The only
mismatches are 0050's ex-dividend days and the two split days (0050 4-for-1 on 2025-06-18, 00631L 22-for-1 on
2026-03-31); Part 4 re-runs this check.

The TX contract multiplier (NT$200 per index point) is from the TAIFEX contract specification. The NT$350,000 initial
margin used in Part 3 is an illustrative assumption, not a TAIFEX figure; the illustrative maintenance margin
scales it by the ratio of TAIFEX's official TX maintenance and initial margins (538,000 / 701,000, effective 2026-08-12).
