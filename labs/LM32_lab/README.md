# LM32 Lab — VaR, Expected Shortfall and Drawdown

Companion to *From Calculus to Kelly*, Learning Module 32. The notebook rebuilds the module's exhibits and computational examples:

- historical, normal, Student-t and Hill-tail VaR and ES on TR23, the TAIEX total-return index;
- the precision of a quantile: the distribution-free interval, the asymptotic standard error and two bootstraps;
- the constructed bonds, the Rockafellar–Uryasev minimum and the minimum-ES portfolio of the first window;
- LM26's GARCH and EWMA forecasts refitted and turned into VaR and ES, with a ten-day Monte Carlo;
- the backtests of six models, with the exact tests, Basel's zones and Kupiec's and Christoffersen's likelihood ratios;
- the eight rules' VaR, ES and drawdowns, with permutations and the stationary bootstrap.

It also works the computational practice problems and ends with a 250-return backtest.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM32_lab/LM32_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM32_lab.ipynb
```

`build/make_lab32.py` generates the notebook and this README: edit the generator, not the generated files.

## Data (FinMind; not in the repository)

The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

On FinMind's free plan, run `uv run python data/fetch_finmind.py --exclude sectors_close/ --exclude vol4_settlement/ --exclude vol6/etf_snapshot` instead, as the book's Getting Started page says. This lab reads none of the excluded files.

Part 8's intraday cell also reads three raw days of the 5-second TAIEX (`TaiwanVariousIndicators5Seconds`, a free dataset). Download them once with `uv run python data/fetch_intraday.py --series taiex5s --dates 2020-03-19,2024-08-05,2025-04-07` before `make_lab_data.py`; without them that cell says so and is skipped.

The same steps in a shell (`data/raw/` and this folder's `data/` are git-ignored):

```bash
export FINMIND_TOKEN=...               # your FinMind API token
uv run python data/fetch_finmind.py    # rebuilds and verifies data/raw/
uv run python data/fetch_intraday.py --series taiex5s --dates 2020-03-19,2024-08-05,2025-04-07
uv run python data/make_lab_data.py    # writes every lab's data/ folder
```

The notebook reads only the files in its own `data/` folder:

| File | Content |
|:--|:--|
| `data/taiex_tr.csv` | `date`, `price`: the TAIEX total-return index (FinMind `TaiwanStockTotalReturnIndex`, data_id TAIEX), 2003-01-02 to 2026-10-08 |
| `data/e5_estimation.csv` | E5's estimation frame: `base`, `date`, `fund`, `R` (FinMind `TaiwanStockPrice`, `TaiwanStockDividendResult`, `TaiwanStockSplitPrice`) |
| `data/e5_wealth.csv` | E5's wealth frame: every session after the base close of 2017-01-17, with `traded` per fund |
| `data/rule_targets.csv` | the through case's trades (`data/vol5_rules.py`): rule, signal, trade, the five target exposures, exposure, turnover, cost |
| `data/rule_wealth_net.csv` | the eight rules' net wealth paths from the first trade's close |
| `data/taiex5s_<date>.csv` | the TAIEX price index every 5 seconds (FinMind `TaiwanVariousIndicators5Seconds`) on 2020-03-19, 2024-08-05 and 2025-04-07; per-day statistics only |
