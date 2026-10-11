# Roadmap — Volumes II to IX

Preliminary plan (2026-10-10, reordered 2026-10-11) for the 43 modules after Volume I. Module titles and one-line
descriptions are in [`../src/syllabus.yaml`](../src/syllabus.yaml); the volume-level dependency map is the Roadmap
figure on the site's front page. Each batch starts only after the previous one is published, and begins with a brief
file (`plans/vol-N.md`, in the format below).

## Batches

| Batch | Volumes | Modules | Needs published | Edition |
|:--|:--|--:|:--|:--|
| 0 | I Calculus for Finance (published 2026-10-11) | 7 | — | 0.2, 0.2.1 |
| 1 | II Linear Algebra for Portfolios | 5 | I | 0.3 |
| 2 | III Probability | 6 | I | 0.4 |
| 3 | IV Statistical Inference and Econometrics | 8 | III | 0.5 |
| 4 | V Portfolio Optimization · VI Measuring True Risk and Return | 5 + 4 | II, IV | 0.6 |
| 5 | VII Stochastic Calculus | 5 | III | 0.7 |
| 6 | VIII The Kelly Criterion and Optimal Leverage | 6 | V, VI, VII | 0.8 |
| 7 | IX Capstone | 4 | all | 1.0 |

Volumes II and III were planned as one batch; on 2026-10-11 the owner started Volume II on its own. The same day,
after a review of the roadmap by Codex, the owner adopted the editor's proposal to put portfolio optimization and
risk measurement before stochastic calculus, and LM27–LM40 were renumbered (table below).

Dependencies behind the order: I → II (gradients, Lagrange) and I → III (integrals, series); III → IV (distributions)
and III → VII (random walks); II and IV → V (wᵀΣw with estimated μ and Σ); IV → VI (sampling error); V, VI and VII →
VIII (the tangency portfolio, uncertainty in μ, Itô and GBM). These are volume-level links; a module's own
prerequisites are its front matter (LM32's Monte Carlo VaR, for example, needs LM18). After Volume VI a reader has the
practical portfolio and risk tools. Volume VII is required, not optional: Volume VIII's continuous-time results use it
(LM42 in full; LM44–LM46 as far as their briefs decide), while LM43 starts from LM7's quadratic approximation and LM40
(option pricing) is the one optional module. The two volumes of batch 4 can be written in parallel.

**Effort.** Volume I took about 70 minutes of parallel writing, 25–40 minutes of independent review and 40–80
minutes of revision per round, plus data collection; with the editor's gates, three or four rounds, closing passes
and publishing it ran about 9.5 hours from the first drafts to publication (git timestamps). Plan a batch over more
than one session. New FinMind data come through the owner's computer, which must be on for that part.

### Renumbering of 2026-10-11

| Old | New | Module |
|:--|:--|:--|
| LM32–LM36 | LM27–LM31 | Portfolio Return and Risk; Mean–Variance Optimization; Convex Optimization in Practice; Estimation Error and Robust Portfolios; Risk Parity, HRP and Volatility Targeting |
| LM37–LM40 | LM32–LM35 | VaR, Expected Shortfall and Drawdown; The Statistics of the Sharpe Ratio; Backtesting Without Fooling Yourself; Stress Testing |
| LM27–LM31 | LM36–LM40 | From Random Walk to Brownian Motion; The Itô Integral and Itô's Lemma; Geometric Brownian Motion; Beyond GBM; Option Pricing Bridge (Optional) |

The old numbers belonged only to unpublished modules. Volume I's references, leads and lab, AUTHORING's example and
`plans/vol-1.md` follow the new numbers; the review records in `reviews/` written before the change keep the old ones.

## Brief format

Each volume's brief gives, per module: prerequisites and leads; **Owns**; **Leaves** (each item with the module that
takes it); **Uses before taught** (each with a one-sentence introduction and a pointer); **Data role** (what the data
illustrate, the sample, any cleaning); **Hygiene declaration** (whether results are descriptive, in-sample, a
stability check or out-of-sample); **Notation** (local symbols, checked against AUTHORING §6); the motivating case with
**verified anchor numbers** and the scripts that print them; sections; exhibits with their chart types; the widget;
a problems plan; lab parts; and cross-module tags (equations other modules cite).

## Module boundaries

Who owns what where modules touch; a brief may refine a line but not move a topic without changing this table.

| Topic | Owner and scope | Leaves to |
|:--|:--|:--|
| Covariance | LM10: the centred data matrix, sample $\hat\Sigma$, positive semidefiniteness, $\mathbf w^{\top}\hat\Sigma\mathbf w$ as a sample quantity | LM16 population covariance and joint distributions; LM19–LM20 descriptive statistics and estimators; LM27 portfolio bookkeeping and risk decomposition |
| Rank and conditioning | LM9 exact rank and solvability; LM11 spectrum and condition number | LM12 numerical rank, SVD, pseudoinverse |
| Factors | LM11 statistical factors (PCA), their stability, no economic labels | LM23 economic factor models; LM30 shrinkage in portfolios |
| Least squares | LM12 projection geometry, residual orthogonality, rank deficiency | LM23 OLS inference (standard errors, HAC, t-statistics) |
| Simulation | LM12 Cholesky as an algebraic map (whitening and colouring real returns) | LM16 the multivariate normal; LM18 random generation and Monte Carlo error; LM32 Monte Carlo VaR |
| Mean–variance | LM7 the two-asset prototype | LM27 N-asset representation and risk accounting; LM28 frontier, minimum variance, tangency; LM29 constraints; LM43 growth-optimal leverage and its equivalence with tangency, without re-deriving it |
| Resampling | LM18 random generation, Monte Carlo error, variance reduction, the mechanics of an iid bootstrap | LM22 bootstrap inference and block bootstraps; LM30 resampled portfolios; LM45 bootstrap Kelly |
| Shrinkage | LM24 priors, posteriors, mean shrinkage; fractional Kelly as a Bayesian answer only inside a stated model | LM30 covariance shrinkage and Black–Litterman weights |
| Spreads and volatility | LM25 cointegration (discrete time, empirical); LM26 GARCH and realized volatility (statistical forecasts) | LM39 Ornstein–Uhlenbeck and stochastic volatility (continuous-time processes) |
| Stress | LM35 replays historical or specified shocks on a portfolio and assigns them no probabilities | LM39 jump models |
| Kelly | LM4 the binary bet as a one-variable optimization | LM41 general discrete Kelly and when it applies; LM42 continuous time; LM43 several assets |
| Research hygiene | the site's Research hygiene page and each module's local note | LM21 multiple testing; LM33 Probabilistic and Deflated Sharpe; LM34 look-ahead, survivorship, costs, walk-forward, PBO |

## Data rule

**Historical market data come only from FinMind** (owner, 2026-10-10). Shioaji is not used for historical data.

- Daily data (prices, dividends, futures, options, indices) go through the FinMind MCP in windows under 500 rows,
  checked with `data/check_chunk.py`, as in Volume I. Check every new daily series also for rows copied from another
  date (PITFALLS §3): the spread check and the manifest's checksums both pass on them.
- Intraday data are too large for 500-row windows (one day of 5-second TAIEX is about 3,240 rows). Download them
  with a FinMind API token from a session that can reach FinMind (for example Claude Code on the owner's computer),
  with a script in `data/` that logs rows per day. Commit the derived series the text uses (for example 5-minute
  returns); keep the raw download reproducible rather than committing very large raw files.
- `TaiwanStockPriceAdj` (adjusted prices) is a useful cross-check of the hand-built total-return series.

**FinMind access: the owner has a Sponsor plan** (2026-10-10). It allows 6,000 API calls an hour and every dataset
marked Free, Backer or Sponsor in `list_datasets`. Intraday datasets need a `data_id` and return one day per request
(whole-day, all-product downloads are Sponsor Pro only), so 15 years of TX minute bars is about 3,700 calls, well
inside an hour. The licence is non-commercial, forbids redistributing raw data and requires citing FinMind.

Datasets above the Free tier that this book will use (tiers as `list_datasets` gives them, checked 2026-10-11):
Sponsor: `TaiwanFuturesKBar` (futures 1-minute bars from 2011), `TaiwanStockKBar` (stock and TAIEX 1-minute bars
from 2019), `TaiwanStockInfoWithWarrantSummary` (warrant strikes and ratios), `TaiwanStockTradingDailyReport`
(broker-branch flows). Backer: `TaiwanFuturesTick` / `TaiwanStockPriceTick` / `TaiwanOptionTick` (ticks; stocks from
2018-12-07), `TaiwanStockEvery5SecondsIndex` (sector indices every 5 seconds; 13:30:00 is the official close; one day
per request, `data_id` optional), `TaiwanFuturesFinalSettlementPrice` (official final settlement prices),
`TaiwanFuturesSpreadTrading` (calendar-spread quotes), `TaiwanStockMarketValueWeight` (TAIEX weights: dated, roughly
monthly snapshots from 2024-10-30 only, so they cannot select past constituents) and `TaiwanStockMarketValue` (market
caps), `TaiwanStockIndustryChain` (industry chains: the current classification only, no history), `USStockPriceMinute`.

**Daily sector indices need no intraday download.** `TaiwanStockPrice` serves the daily closes of the 30 TWSE
sector indices listed in `TaiwanStockInfo` with `industry_category` "Index" (`data_id` such as `Semiconductor`,
`FinancialInsurance`; from 2005-01-03, or 2007-07-02 for the eight electronics sub-industries and others). They are
price indices (no dividends); `Electronic` and `ChemicalBiotechnologyMedicalCare` cover the stocks of other sector
indices (eight electronics sub-industries; chemicals and biotech); the newest TWSE sectors (such as
`DigitalCloudServices`) and all TPEx sectors have no daily series there. FinMind copies one day's values onto other
dates in these series, so their closes are repaired from the 13:30:00 values of `TaiwanStockEvery5SecondsIndex`
before use (`data/README.md`). `TaiwanStockPriceAdj` is rebuilt backward from the latest day and did not adjust
2330's 1990s stock dividends, so record its retrieval date and check it against `TaiwanStockDividendResult`.

## Per-volume notes

| Volume | Main FinMind data (tier) | New Python tools | Notes |
|:--|:--|:--|:--|
| II | daily closes of the TWSE sector indices and TAIEX (`TaiwanStockPrice`, Free), from 2007-07-02, repaired from `TaiwanStockEvery5SecondsIndex` (Backer); Volume I's 0050, 00679B and TX files | NumPy linear algebra | LM11 "eigen-portfolios of Taiwan sectors" as data directions, not tradable portfolios; LM12 applies Cholesky to real returns (whitening), with simulation left to LM16 and LM18; brief in `plans/vol-2.md` |
| III | long TAIEX and 0050 daily history (`TaiwanStockPrice`, `TaiwanStockTotalReturnIndex`, Free) | SciPy distributions | LM15 fits normal, lognormal, Student-t and Poisson to TAIEX returns; LM16 crash correlation; LM18 Monte Carlo and bootstrap |
| IV | stock and index returns; TX and TAIEX for the basis (`TaiwanFuturesDaily`), with calendar spreads (`TaiwanFuturesSpreadTrading`) and official final settlement prices (`TaiwanFuturesFinalSettlementPrice`); intraday data for realized volatility: TX 1-minute bars from 2011 (`TaiwanFuturesKBar`), TAIEX 1-minute bars from 2019 (`TaiwanStockKBar`) or 5-second TAIEX (`TaiwanVariousIndicators5Seconds`) | statsmodels, arch | LM25 cointegration of the futures–spot basis; LM26 compares EWMA and GARCH forecasts with realized volatility, including the choice of sampling interval (ticks show microstructure noise) |
| V | Taiwan ETFs (0050, 00679B and others) and US ETFs (`USStockPrice`, Free) | cvxpy, scikit-learn (Ledoit–Wolf) | long-only, leverage and turnover constraints; 1/N, shrinkage, Black–Litterman, risk parity, HRP |
| VI | TAIEX daily back to 2008 for stress tests; intraday paths for drawdowns within the day (`TaiwanFuturesKBar`) | — | Taiwan securities and futures transaction taxes and broker fees must come from official sources; stress scenarios 2008, 2015, 2020, 2024-08-05, 2025-04-07, replayed without probabilities |
| VII | TAIEX opens and closes for overnight gaps; TXO (`TaiwanOptionDaily`, `TaiwanOptionTick`); warrants with strikes and ratios (`TaiwanStockInfoWithWarrantSummary`); `TaiwanOptionVix` only from 2026-03 | — | LM39 Merton jumps for Taiwan gap days and Ornstein–Uhlenbeck spreads; LM40 Black–Scholes bridge with TXO and warrants (optional) |
| VIII | TX, MTX, TMF daily and 1-minute bars (`TaiwanFuturesDaily`, `TaiwanFuturesKBar`); final settlement prices; 00631L; TQQQ (`USStockPrice`, `USStockPriceMinute`) | — | official TAIFEX margin tables, dated; intraday paths decide margin calls, so leverage limits are tested on minute bars; continuous-time Kelly g(f), fractional Kelly and drawdown control, parameter uncertainty. LM41 opens with when Kelly applies (below) |
| IX | as needed by each capstone, e.g. broker-branch flows (`TaiwanStockTradingDailyReport`) for a flow-based strategy | — | capstone A: Taiwan core–satellite portfolio walk-forward; B: Kelly sizing of a single strategy on TX; C: multi-strategy allocation |

**When Kelly applies (LM41).** LM4 owns the binary-bet derivation; LM41 recaps it in a few lines and states the
boundaries: Kelly maximizes expected log wealth, so it is the right goal when the goal is log utility, at any horizon;
what changes the answer is a different goal (liabilities, withdrawals, consumption, survival or shortfall
constraints). Its long-run superiority is an asymptotic claim, not a guarantee over a finite horizon. Fractional
Kelly reflects parameter uncertainty, risk aversion, model error or operating limits, and a drawdown constraint is a
different, constrained objective rather than another form of log utility. Each Volume VIII module lists the
Volume VII results it uses.

## Open decisions for the owner

- **Capstone B:** use the backtest returns of one of the owner's own strategies, or a strategy built in the book.
