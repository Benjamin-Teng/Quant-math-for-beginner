# LM35 Lab — Stress Testing

Companion to *From Calculus to Kelly*, Learning Module 35. The notebook rebuilds the module's exhibits and computational examples:

- the five scenario windows on TR23 and the returns that span holidays;
- the rules' books rebuilt from their trades, with frozen, named-day and actual replays and their attribution;
- the hypothetical years 2008 and 2015 on 0050 itself and US proxies, and the proxies checked against the funds;
- the factor shock, the partial scenario and the correlation break;
- the reverse stress test in closed form and in cvxpy with a price limit, checked by KKT;
- the overnight gaps from five days of 5-second TAIEX statistics, the price limits, a limit lock, ruin and a TX margin call.

It solves the computational practice problems, reproduces the widget's starting state, and ends with the batch's checkpoint on eight funds, whose reference answers sit in a collapsed cell.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM35_lab/LM35_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM35_lab.ipynb
```

`build/make_lab35.py` generates the notebook and this README: edit the generator, not the generated files.

## Data (FinMind; not in the repository)

The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

Part 7 also reads the five named days of the 5-second TAIEX. `make_lab_data.py` copies them when `data/raw/intraday/taiex5s/` holds them, which `uv run python data/fetch_intraday.py --series taiex5s --dates 2008-01-22,2015-08-24,2020-01-30,2024-08-05,2025-04-07` fetches (five requests); without them Part 7 says so and skips those statistics.

The same steps in a shell (`data/raw/` and this folder's `data/` are git-ignored):

```bash
export FINMIND_TOKEN=...               # your FinMind API token
uv run python data/fetch_finmind.py    # rebuilds and verifies data/raw/
uv run python data/make_lab_data.py    # writes every lab's data/ folder
```

`fetch_finmind.py` checks every file against `data/raw_manifest.json`. The notebook reads only the files in its own `data/` folder:

| File | Content |
|:--|:--|
| `data/e5_estimation.csv`, `data/e5_wealth.csv` | E5's estimation frame (the 2,362 joint dates) and wealth frame (every session, with `traded` per fund): 0050, 00646, 00679B, 00635U, 00642U (FinMind `TaiwanStockPrice`, `TaiwanStockDividendResult`, `TaiwanStockSplitPrice`) |
| `data/e5_checkpoint_estimation.csv`, `data/e5_checkpoint_wealth.csv` | the same for the checkpoint universe, E5 plus 0056, 00662 and 00720B, from 2018-02-01 |
| `data/rule_targets.csv`, `data/rule_wealth_net.csv` | the through case's trades (target exposures, exposure, turnover, cost) and net wealth paths (`data/vol5_rules.py`) |
| `data/taiex_tr.csv` | TR23, the TAIEX total-return index (`TaiwanStockTotalReturnIndex`) |
| `data/taiex5s_<date>.csv` | the five named days of the 5-second TAIEX (`TaiwanVariousIndicators5Seconds`), read for per-day statistics only |
| `data/tx23_limit_days.csv` | TX23's rows on its limit days since 2015-06-01, 2025-04-08 and 2026-10-08 (`TaiwanFuturesDaily`) |
| `data/0050_daily_raw.csv`, `data/0050_dividends.csv`, `data/00631L_daily_raw.csv` | LM2's 0050 and 00631L files |
| `data/ohlc_0050_0056_00720B.csv` | the daily open, high, low, close and volume of 0050, 0056 and 00720B |
| `data/SPY__us_…csv` … `data/DBO__us_…csv`, `data/USD_TWD__…csv` | the US proxies' adjusted closes (`USStockPrice`) and USD/TWD (`TaiwanExchangeRate`), 2007-07-02 to 2026-10-08 |
| `data/0050__2007-07-02__2008-12-31.csv`, `data/0050_dividends__2007-07-02__2008-12-31.csv` | 0050's own closes and distributions in 2007–2008 |
