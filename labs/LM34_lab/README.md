# LM34 Lab — Backtesting Without Fooling Yourself

Companion to *From Calculus to Kelly*, Learning Module 34. The notebook rebuilds the module's exhibits and computational examples:

- the through case's eight rules, net and gross of costs, rebuilt from their targets with the wealth recursion (27.2);
- the log gap (34.1), the tax share, twice the costs and the financing rates;
- 0050's adjusted series built on three dates, the rebalances moved to the signal's own close, and the daily scale on TR23;
- the survivorship gap of the six futures ETFs of January 2017;
- White's reality check, Hansen's SPA and Romano and Wolf's stepdown on Experiment 10, and the reality check of the grid against R1;
- CSCV on the declared grid and on 200 panels of skill-free strategies;
- the Kelly walk-forward on TR23.

It also works the computational practice problems and ends with a fourth rebalancing frequency ($n=68$).

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM34_lab/LM34_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM34_lab.ipynb
```

`build/make_lab34.py` generates the notebook and this README: edit the generator, not the generated files.

## Data (FinMind; not in the repository)

The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

On FinMind's free plan, run `uv run python data/fetch_finmind.py --exclude sectors_close/ --exclude vol4_settlement/ --exclude vol6/etf_snapshot` instead, as the book's Getting Started page says. The three excluded sets come from paid datasets; this lab reads none of them.

The same steps in a shell (`data/raw/` and this folder's `data/` are git-ignored):

```bash
export FINMIND_TOKEN=...               # your FinMind API token
uv run python data/fetch_finmind.py    # rebuilds and verifies data/raw/
uv run python data/make_lab_data.py    # writes every lab's data/ folder
```

`fetch_finmind.py` checks every file against `data/raw_manifest.json`. The notebook reads only the files in its own `data/` folder:

| File | Content |
|:--|:--|
| `data/e5_wealth.csv` | E5's wealth frame: every session after the base close of 2017-01-17, with `traded` per fund (FinMind `TaiwanStockPrice`, `TaiwanStockDividendResult`, `TaiwanStockSplitPrice`) |
| `data/rule_targets.csv` | the through case's trades (`data/vol5_rules.py`): rule, signal, trade, the five target exposures, exposure, turnover, cost |
| `data/rule_wealth.csv` | the eight rules' net and gross wealth paths from the first trade |
| `data/lm34_grid.csv` | the declared grid's 60 net-return series, first row the first purchase of 2019-03-04, then the 1,851 daily returns (`data/lm34_grid.py`) |
| `data/taiex_tr.csv` | the TAIEX total-return index (FinMind `TaiwanStockTotalReturnIndex`) |
| `data/0050_daily_raw.csv`, `data/0050_dividends.csv` | 0050's closes and distributions (FinMind `TaiwanStockPrice`, `TaiwanStockDividendResult`) |
| `data/splits__2016-12-01__2026-10-08.csv` | the registered splits (FinMind `TaiwanStockSplitPrice`) |
| `data/delisting__2000-01-01__2026-10-08.csv` | delisted ids from "00" (FinMind `TaiwanStockDelisting`) |
| `data/00635U__…csv` … `data/00677U__…csv` | the six futures ETFs' daily prices (FinMind `TaiwanStockPrice`) |
