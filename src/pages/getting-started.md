---
title: Getting Started
description: Who the book is for, how to read a module, how to run the labs, and the conventions every module uses.
---

> [!zh] 這一頁講什麼
> 開始之前需要什麼程度、一個模組怎麼讀、lab 怎麼跑，以及全書共用的資料與計算慣例。設定好環境後，先做十分鐘的小測試：確認環境和資料都沒問題，再抓全部資料，從 [[LM1]] 開始。

## Who the book is for

The book is for a market professional who wants the mathematics behind portfolio work. You know the markets, but
your university mathematics is rusty. Volume I reviews calculus from the start, so school algebra is enough.

For the code you need basic Python: variables, functions, lists, loops and reading a table. You do not need to know
NumPy or Polars yet. The modules introduce them, and the code on this page only needs to run.

## How to read a module

A module opens with its learning outcomes and a case built on real Taiwan or US data. Numbered sections follow.
Each section moves from a small example to a definition, a derivation, a worked example and a short knowledge
check. A 中文導讀 box gives the intuition in Traditional Chinese. Practice problems with full solutions close the
module, and a lab notebook rebuilds every number in it.

Read the volumes in order: I, II, III, IV, V, VI, VII, VIII, IX. After Volume VI you can already analyse portfolios
and their risk. Volume VII adds the continuous-time tools that the Kelly volume needs. The
[roadmap on the front page](index.html#roadmap) shows how the volumes depend on each other.

## Set up the labs

1. Install [uv](https://docs.astral.sh/uv/), the tool that manages the book's Python environment.
2. Clone the [repository](https://github.com/Benjamin-Teng/Quant-math-for-beginner), and from its root run
   `uv sync`. It installs the exact package versions in `uv.lock`.
3. Open a lab in VS Code and choose the `.venv` kernel, or run `uv run --with jupyterlab jupyter lab` from the
   repository root.
4. Create an account on the [FinMind](https://finmindtrade.com/) site and copy your API token. Put it in the
   environment variable `FINMIND_TOKEN` on your own computer, and never write it into a file that you share. In
   PowerShell, type `$env:FINMIND_TOKEN = "your token"`; in bash, type `export FINMIND_TOKEN="your token"`. Either
   command lasts until you close the window.

## A ten-minute smoke test

Run this test before you fetch all the data. It checks your environment, and it teaches three lessons. First, fetch
only the 0050 files: `uv run python data/fetch_finmind.py --only 0050__`. Do not run `make_lab_data.py` yet, because
it needs the other files too. Then run this code from the repository root:

```python
from pathlib import Path

import polars as pl

files = sorted(Path("data/raw").glob("0050__*.csv"))
px = pl.concat([pl.read_csv(f) for f in files]).sort("date")
print(px.shape, px["date"][0], px["date"][-1])

px = px.with_columns(
    R=pl.col("close") / pl.col("close").shift(1) - 1,
    r=(pl.col("close") / pl.col("close").shift(1)).log(),
).drop_nulls()
for row in px.sort("R").head(3).iter_rows():  # three lowest returns
    print(row)

cut = int(0.7 * px.height)          # the first 70% of the returns
est, test = px[:cut], px[cut:]
print(est["date"][-1], "<", test["date"][0])

prev = px.row(0, named=True)["close"]
row = px.row(1, named=True)
print(row["date"], prev, row["close"], row["close"] / prev - 1, row["R"])
```

The code computes price returns, without dividends. The first line shows `(2907, 3)`: 2,907 rows and 3 columns,
from 2014-10-31 to 2026-10-08. The lowest return is −74.8% on 2025-06-18, the day of a stock split, not a crash. The
next two are the limit-down day of 2025-04-07 and 2024-08-05 (−9.1%). The estimation window ends on 2023-03-01, and
the test window starts on the next trading day. The last line checks one return by hand: 65.65 / 65.6 − 1 = 0.000762
on 2014-11-04.

The first lesson is the stock split: a raw price series is not yet a return series. The second is the cut by time:
the test window always comes after the estimation window, as the [Research hygiene](research-hygiene.html) page
explains. The third is in the second row: a fall from 176.00 to 158.40 is exactly −10%, yet Python prints
`-0.09999999999999998`. Floating point stores most decimals a little off, which the conventions below take into
account.

## Fetch the data

Run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. After that, every lab runs
offline. The book ships no market data, because FinMind's licence does not allow the book to redistribute it.

Volume I's files come from FinMind's free datasets, and so do Volume II's sector indices. One folder needs a paid
plan: `data/raw/sectors_close/`, 561 small files that repair FinMind's copied sector closes (see "Check, do not trust"
below). On the free plan, run `uv run python data/fetch_finmind.py --exclude sectors_close/`; `make_lab_data.py` does not
need those files, and Volume II's labs say what changes without them. The fetch skips any file that it cannot get, lists it at the end and stops with
an error code.

## Data you will meet

- **Close, adjusted close and total return.** A close is the price of the day's last trade; on TWSE it comes from the
  closing auction from 13:25 to 13:30. An adjusted close is rewritten backward
  after each dividend or split, so it depends on the day you download it. A total return adds the dividend back on
  the ex-dividend day. The book builds total returns itself and says which series each number uses.
- **Stock splits.** 0050 split four for one on 2025-06-18. Its raw close fell 74.8% that day, yet four new shares
  were worth 0.9% more than one old share. A return series must undo the split first.
- **Indices.** TAIEX and the TWSE sector indices are price indices: they leave dividends out. TWSE also publishes a
  total-return index, which includes them.
- **Futures.** A TX contract has a daily settlement price and a close, and the two can differ. The book says which
  one it uses.
- **Check, do not trust.** FinMind's sector-index series contain rows copied from other dates. Every data script in
  the book checks its input and stops on anything it cannot explain.

## Dates and missing values

- Use the exchange's trading dates, not a Monday-to-Friday calendar. The 0050 data contain nine Saturday trading
  days, such as 2016-01-30.
- When you combine two series, keep only the dates they share. That changes the number of returns, so every count in
  the book says which sample it comes from.
- A trading halt makes one return cover several days. 0050 was halted from 11 to 17 June 2025 for its split, so its
  return on 2025-06-18 covers six trading days.
- After a join, sort by date again. Never rely on the order of rows.

## Conventions

- A simple return is $R_t=(P_t+D_t)/P_{t-1}-1$, where $D_t$ is the cash dividend of a share that goes ex-dividend on
  day $t$ (zero on most days). Simple returns add across the assets of a portfolio, and log returns
  $r_t=\ln(1+R_t)$ add across time ([[LM1]]).
- Sample moments divide by $T$, the number of returns, and each module says so. NumPy's `np.cov` and Polars' `var`
  and `std` divide by $T-1$ unless you pass `ddof=0`; NumPy's `np.var` and `np.std` already divide by $T$.
- The number of periods per year, $A$, comes from the sample in use. It is the number of returns divided by the
  number of years, and the years are the calendar days divided by 365.25.
- Tables say whether a number is a percent or a decimal: 1% is 0.01.
- Vectors are columns. The [notation table on the front page](index.html#notation) lists the main symbols.

## Reproducible numbers

- Seed the random generator once, at the start of a notebook, for example `rng = np.random.default_rng(20261011)`.
  Every run then gives the same draws.
- Never test two computed numbers with `x == y`. Compare them with a tolerance that fits their size, such as
  `math.isclose(x, y, rel_tol=1e-9, abs_tol=1e-12)`: relative for large amounts, absolute near zero.
- Prices with two decimals make some returns exact. A move from 100.00 to 101.00 is exactly 1%. Floating point may
  store it a little above or below 1%, so a count of "returns of at least 1%" can be off by one ([[LM5]]).
- A printed number is rounded. Compute from the full value, and print one more digit when a reader will compute
  from it.

## From formula to code

Use four steps for every formula. First, compute a small case by hand. Second, write down the shape and the unit
of every object. Third, write the vectorized code. Fourth, check the code against the hand result.

For a portfolio of two assets with weights $\mathbf w=(0.6,\ 0.4)^{\top}$ and returns $\mathbf R=(0.02,\ {-0.01})^{\top}$,
the hand result is $0.6\times0.02+0.4\times(-0.01)=0.008$. The code gives the same number:

```python
import numpy as np

w = np.array([0.6, 0.4])     # weights, shape (2,), they sum to 1
R = np.array([0.02, -0.01])  # simple returns, shape (2,)
print(w @ R)                 # 0.008 (up to floating point)
```
