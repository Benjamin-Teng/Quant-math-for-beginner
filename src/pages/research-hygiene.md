---
title: Research hygiene
description: Six rules that keep a result from market data honest, and the labels that results carry from Volume II on.
---

> [!zh] 這一頁講什麼
> 用市場資料算出來的數字，看起來很精確，卻可能誤導。下面六條規則讓結果站得住腳。從第二卷起，每個會估計、選模型或回測的模組，都會用一個短框說明它用了哪幾條規則，以及結果該怎麼解讀；更完整的處理在 [[LM21]]、[[LM33]] 和 [[LM34]]。

A number computed from market data can look precise and still mislead. The six rules below keep the book's results
honest. From Volume II on, every module that estimates, selects or backtests carries a short note. The note says
which rules apply and how to read the results.

## Use only what was known at the time

A decision on a date may use only the information available on that date. A close is known only after the closing
auction ends at 13:30. FinMind's TAIEX weight snapshots start in October 2024, so they cannot give a stock's weight in
2015. An adjusted price is rewritten backward after each dividend, so today's file is not what an investor saw at
the time.

## Split by time, never at random

Market data come in time order, and tomorrow is never in today's sample. So the estimation window comes first and
the test window after it, as in [[LM7]]: weights estimated on 2017–2021 and tested on 2022–2026. Fit every input on
the estimation window only. That includes means, covariance matrices, principal components and any rescaling.

## Keep selection apart from evaluation

Choose a model or a parameter on one stretch of data, and judge it once on another. Count the versions you tried.
The more versions you try, the more likely it is that the best one is only lucky. [[LM21]] and [[LM33]] measure that
risk.

## Put costs inside the strategy

Taxes, broker fees, slippage, financing and delays belong in the strategy while it is built. A strategy that trades
more pays more, so one constant subtracted at the end hides the difference. [[LM34]] gives Taiwan's official rates.

## Fix the universe and the data policy first

Decide which assets and which dates you use before you look at any result. A list of today's stocks leaves out the
companies that were delisted, so it makes past returns look better than they were. Write down how you treat
dividends, splits, missing values and dates that two series do not share.

## Label every result

From Volume II on, every result carries at least one of the labels below. Volume I's results fall into the first four kinds;
the fifth, from Volume III on, marks the answer of a probability model:

| Label | Meaning | Example in the book |
|:--|:--|:--|
| Descriptive | a summary of the whole sample | 0050's total return of +902% from 2014 to 2026 ([[LM1]]) |
| In-sample | a model fitted and judged on the same data | a normal model fitted to 0050's 2,902 daily returns ([[LM5]]) |
| Stability check | the same calculation on two periods, compared | the two-asset Kelly fractions estimated in two windows ([[LM7]]) |
| Out-of-sample | fitted on earlier data and judged on later data that the fit never used | the minimum-variance weight estimated on 2017–2021 and held in 2022–2026 ([[LM7]]) |
| Model | the answer of a probability model, exact, approximate or simulated: a property of the model, not a forecast (a model fitted to the data is also in-sample) | the chance of a losing year if days are independent ([[LM17]]) |

A full-sample estimate describes the past. It is not a forecast.

Volume III also marks invented bets, positions and records as **hypothetical**, and examples built to make a point as
**constructed** ([[LM13]], [[LM16]]).

> [!note] Where the book goes deeper
> [[LM21]] covers multiple testing. [[LM33]] covers the Probabilistic and Deflated Sharpe ratios. [[LM34]] covers
> look-ahead and survivorship bias, costs, walk-forward testing and the probability of backtest overfitting.
