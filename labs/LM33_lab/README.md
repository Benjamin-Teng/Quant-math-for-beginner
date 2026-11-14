# LM33 Lab — The Statistics of the Sharpe Ratio

Companion to *From Calculus to Kelly*, Learning Module 33. The notebook rebuilds the module's exhibits and computational examples:

- the eight rules' Sharpe ratios with (20.9)'s standard errors, the checkpoint table and the illustrative risk-free rate;
- the HAC standard error (33.1) by hand, its lag curve and TR23's long record;
- Lo's correction on 90 calendar months, with the noise of the correction;
- the probabilistic Sharpe ratio and the minimum track record, with Bailey and López de Prado's 2012 example;
- Ledoit and Wolf's test of each rule against R1, by HAC and by their circular block bootstrap (experiments 1 and 3);
- the expected maximum of $n$ trials, the effective number of trials (experiment 2) and the deflated Sharpe ratio;
- Harvey and Liu's haircuts.

It also works the computational practice problems and ends with R2's PSR(0) on rolling windows, a stability check.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM33_lab/LM33_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM33_lab.ipynb
```

`build/make_lab33.py` generates the notebook and this README: edit the generator, not the generated files.

## Data (FinMind; not in the repository)

The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

On FinMind's free plan, run `uv run python data/fetch_finmind.py --exclude sectors_close/ --exclude vol4_settlement/ --exclude vol6/etf_snapshot` instead, as the book's Getting Started page says. This lab needs none of the excluded files.

The same steps in a shell (`data/raw/` and this folder's `data/` are git-ignored):

```bash
export FINMIND_TOKEN=...               # your FinMind API token
uv run python data/fetch_finmind.py    # rebuilds and verifies data/raw/
uv run python data/make_lab_data.py    # writes every lab's data/ folder
```

`fetch_finmind.py` checks every file against `data/raw_manifest.json`. The notebook reads only the files in its own `data/` folder:

| File | Content |
|:--|:--|
| `data/rule_wealth_net.csv` | the through case's eight rules (`data/vol5_rules.py`): `rule`, `date`, `wealth`, the net wealth after each day's trade on every session of E5's wealth frame from the first trade, 4 March 2019, to 8 October 2026 (FinMind `TaiwanStockPrice`, `TaiwanStockDividendResult`, `TaiwanStockSplitPrice`) |
| `data/taiex_tr.csv` | TR23, the TAIEX total-return index (`date`, `price`; FinMind `TaiwanStockTotalReturnIndex`, data_id TAIEX), 2 January 2003 to 8 October 2026 |
