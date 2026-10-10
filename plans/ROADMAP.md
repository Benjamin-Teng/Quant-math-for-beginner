# Roadmap — Volumes II to IX

Preliminary plan (2026-10-10) for the 43 modules after Volume I. Module titles and one-line descriptions are in
[`../src/syllabus.yaml`](../src/syllabus.yaml); the dependency map is the Roadmap figure on the site's front page.
Each batch starts only after the previous one is published, and begins with a brief file (`plans/vol-N.md`, in the
format of [`vol-1.md`](vol-1.md)).

## Batches

| Batch | Volumes | Modules | Needs published | Edition |
|:--|:--|--:|:--|:--|
| 0 | I Calculus for Finance (finish review and publish) | 7 | — | 0.2 |
| 1 | II Linear Algebra for Portfolios · III Probability | 5 + 6 | I | 0.3 |
| 2 | IV Statistical Inference and Econometrics · V Stochastic Calculus | 8 + 5 | II, III | 0.4 |
| 3 | VI Portfolio Optimization · VII Measuring True Risk and Return | 5 + 4 | II, IV | 0.5 |
| 4 | VIII The Kelly Criterion and Optimal Leverage | 6 | V, VI, VII | 0.6 |
| 5 | IX Capstone | 4 | all | 1.0 |

Dependencies behind the order: I → II (gradients, Lagrange) and I → III (integrals, series); III → IV (distributions)
and III → V (random walks); II and IV → VI (wᵀΣw with estimated μ and Σ); IV → VII (sampling error); V, VI and VII →
VIII (Itô and GBM, the tangency portfolio, uncertainty in μ). The two volumes in a batch can be written in parallel.

**Effort.** Volume I took about 70 minutes of parallel writing, 25–40 minutes of independent review and 40–80
minutes of revision, plus data collection. Expect one working session of roughly 3–5 hours per
batch, longer when new data must be collected. New FinMind data come through the owner's computer, which must be
on for that part.

## Data rule

**Historical market data come only from FinMind** (owner, 2026-10-10). Shioaji is not used for historical data.

- Daily data (prices, dividends, futures, options, indices) go through the FinMind MCP in windows under 500 rows,
  checked with `data/check_chunk.py`, as in Volume I.
- Intraday data are too large for 500-row windows (one day of 5-second TAIEX is about 3,240 rows). Download them
  with a FinMind API token from a session that can reach FinMind (for example Claude Code on the owner's computer),
  with a script in `data/` that logs rows per day. Commit the derived series the text uses (for example 5-minute
  returns); keep the raw download reproducible rather than committing very large raw files.
- `TaiwanStockPriceAdj` (adjusted prices) is a useful cross-check of the hand-built total-return series.

**FinMind access: the owner has a Sponsor plan** (2026-10-10). It allows 6,000 API calls an hour and every dataset
marked Free, Backer or Sponsor in `list_datasets`. Intraday datasets need a `data_id` and return one day per request
(whole-day, all-product downloads are Sponsor Pro only), so 15 years of TX minute bars is about 3,700 calls, well
inside an hour. The licence is non-commercial, forbids redistributing raw data and requires citing FinMind.

Sponsor datasets this book will use: `TaiwanFuturesKBar` (futures 1-minute bars from 2011), `TaiwanStockKBar` (stock
and TAIEX 1-minute bars from 2019), `TaiwanFuturesTick` / `TaiwanStockPriceTick` / `TaiwanOptionTick` (ticks; stocks
from 2018-12-07), `TaiwanStockEvery5SecondsIndex` (sector indices every 5 seconds; 13:30:00 is the official close),
`TaiwanFuturesFinalSettlementPrice` (official final settlement prices), `TaiwanFuturesSpreadTrading` (calendar-spread
quotes), `TaiwanStockMarketValueWeight` and `TaiwanStockMarketValue` (TAIEX weights and market caps),
`TaiwanStockIndustryChain` (industry classification), `TaiwanStockInfoWithWarrantSummary` (warrant strikes and
ratios), `TaiwanStockTradingDailyReport` (broker-branch flows), `USStockPriceMinute`.

## Per-volume notes

| Volume | Main FinMind data (tier) | New Python tools | Notes |
|:--|:--|:--|:--|
| II | sector index closes (`TaiwanStockEvery5SecondsIndex`, value at 13:30:00) or large caps grouped by `TaiwanStockIndustryChain`; TAIEX weights (`TaiwanStockMarketValueWeight`); daily prices (`TaiwanStockPrice`, `TaiwanStockPriceAdj`) | NumPy linear algebra | LM11 "eigen-portfolios of Taiwan sectors"; LM12 simulates correlated returns with Cholesky |
| III | long TAIEX and 0050 daily history (`TaiwanStockPrice`, `TaiwanStockTotalReturnIndex`, Free) | SciPy distributions | LM15 fits normal, lognormal, Student-t and Poisson to TAIEX returns; LM16 crash correlation; LM18 Monte Carlo and bootstrap |
| IV | stock and index returns; TX and TAIEX for the basis (`TaiwanFuturesDaily`), with calendar spreads (`TaiwanFuturesSpreadTrading`) and official final settlement prices (`TaiwanFuturesFinalSettlementPrice`); intraday data for realized volatility: TX 1-minute bars from 2011 (`TaiwanFuturesKBar`), TAIEX 1-minute bars from 2019 (`TaiwanStockKBar`) or 5-second TAIEX (`TaiwanVariousIndicators5Seconds`) | statsmodels, arch | LM25 cointegration of the futures–spot basis; LM26 compares EWMA and GARCH forecasts with realized volatility, including the choice of sampling interval (ticks show microstructure noise) |
| V | TAIEX opens and closes for overnight gaps; TXO (`TaiwanOptionDaily`, `TaiwanOptionTick`); warrants with strikes and ratios (`TaiwanStockInfoWithWarrantSummary`); `TaiwanOptionVix` only from 2026-03 | — | LM30 Merton jumps for Taiwan gap days and Ornstein–Uhlenbeck spreads; LM31 Black–Scholes bridge with TXO and warrants |
| VI | Taiwan ETFs (0050, 00679B and others) and US ETFs (`USStockPrice`, Free) | cvxpy, scikit-learn (Ledoit–Wolf) | long-only, leverage and turnover constraints; 1/N, shrinkage, Black–Litterman, risk parity, HRP |
| VII | TAIEX daily back to 2008 for stress tests; intraday paths for drawdowns within the day (`TaiwanFuturesKBar`) | — | Taiwan securities and futures transaction taxes and broker fees must come from official sources; stress scenarios 2008, 2015, 2020, 2024-08-05, 2025-04-07 |
| VIII | TX, MTX, TMF daily and 1-minute bars (`TaiwanFuturesDaily`, `TaiwanFuturesKBar`); final settlement prices; 00631L; TQQQ (`USStockPrice`, `USStockPriceMinute`) | — | official TAIFEX margin tables, dated; intraday paths decide margin calls, so leverage limits are tested on minute bars; continuous-time Kelly g(f), fractional Kelly and drawdown control, parameter uncertainty |
| IX | as needed by each capstone, e.g. broker-branch flows (`TaiwanStockTradingDailyReport`) for a flow-based strategy | — | capstone A: Taiwan core–satellite portfolio walk-forward; B: Kelly sizing of a single strategy on TX; C: multi-strategy allocation |

## Open decisions for the owner

- **Capstone B:** use the backtest returns of one of the owner's own strategies, or a strategy built in the book.
