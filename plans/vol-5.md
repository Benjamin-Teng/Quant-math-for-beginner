# Volumes V and VI — Portfolio Optimization; Measuring True Risk and Return: shared decisions and spines

Batch 4 turns LM7's two-asset prototype, LM10's $\mathbf w^{\top}\hat\Sigma\mathbf w$ and Volume IV's estimates into
allocations a reader can defend, and then measures what those allocations, and any track record, really deliver.
Volume V (LM27–LM31) builds the portfolio, solves for it under constraints and shows how estimation error breaks the
solution. Volume VI (LM32–LM35) measures tail risk, the precision of a Sharpe ratio, the honesty of a backtest and the
damage of a crash. One through case, five Taiwan-listed funds and eight allocation rules fixed in advance, runs through
both volumes (shared decision "Through case").

The reader reads English as a second language and wants the tools learned systematically (SPEC §2). Volumes I–IV are
published: link to their results with [[LMn]] instead of repeating them, and honour every forward link they make to
LM27–LM35 (listed per spine; the brief rechecks each line).

This file holds the editor's Stage 1 decisions (2026-10-24/25): the shared decisions for both volumes, the capability
check and the owner's answers, the decisions on the survey and on the spines' fresh check, on the briefs and on their
three revisions, the Stage 4 list, one spine per module and the briefs of LM27–LM31. The briefs of LM32–LM35 are in
`plans/vol-6.md`, the anchors in `plans/vol-5-anchors.md` and `plans/vol-6-anchors.md`. Until Stage 3 the briefs and anchors are the
plan; from Stage 3 the module sources and their numbers scripts are authoritative (as in `plans/vol-4.md`).

Status: revised three times and given a last pass on 2026-10-24/25, each revision verified by fresh agents; revised on 2026-10-31 to the fresh check of the whole of Stage 1 ("Decisions on the fresh check of the whole of Stage 1", `plans/vol-5.md`), whose fixes and changed anchors fresh agents verified the same day.

The Stage 1 survey (2026-10-24: eight read-only surveyors and an adversarial critic) and a fresh adversarial check of
the first spines (the same day) are summarized where each decision uses them. Their reports were working files; every
fact a decision rests on is stated here with its evidence.

## Shared decisions

- **Length and voice.** AUTHORING §1: at most 6,000 words of prose and 36 pages; first drafts under 5,500 words;
  sentences average under 16 words and never exceed 30; paragraphs at most 80 words; connectors kept.
  `uv run python build/qa/style.py src/lmNN.md` shows no FAIL before a draft is handed back.
- **Section pattern.** As Volume IV: a small numeric case or a picture first, then the definition, problem or
  estimator with all its conditions, a short derivation, a worked example on the through case, at most one pitfall,
  the 中文導讀 and the knowledge check. Each method is first computed by hand in NumPy from its formula; a package
  (cvxpy, scikit-learn, SciPy, arch) is then shown to give the same number. Each module opens by saying which layer
  of capability it adds to the earlier modules (guidance, below).
- **Outcome levels.** Each brief marks every outcome with its level: **[D]** derive without the solution, **[C]**
  compute and diagnose, **[U]** know the use and the limits (ROADMAP, "Brief format"). The published front matter
  keeps AUTHORING §3's form (6–8 outcomes, each starting with a verb); the level shows in the verb (derive; compute,
  check; explain, choose). A visible mark on the page would be a code change and is not proposed. The reviews check
  that each outcome is taught, practised and assessed (`reviews/REVIEW_PROMPT.md` item 10).
- **Rigor.** Every optimization states its feasible set, the convexity of its objective and constraints, and whether
  the solution exists and is unique ($\Sigma$ positive definite, or the reason it is not). The N-asset results of
  LM28 are derived in full. LM29 derives KKT sufficiency for the convex problems the volume uses; the general theorem,
  and necessity (which needs a constraint qualification; linear constraints satisfy one), are *stated without proof*
  (Boyd and Vandenberghe 2004, as LM7 does). Asymptotic results (Ledoit and Wolf's consistency, the Sharpe ratio's
  distribution, the reality check) are stated, not proved, with what "large $T$" means in the module's examples.
  Results that need Volume VII (Brownian-motion drawdown theory) are *stated without proof*, keeping their model
  (guidance), or left to LM44.
- **Estimate, standard error, interval.** Volume IV's rule holds for statistics. An optimizer's output (weights, a
  frontier point, a risk contribution) is also an estimate: a module prints its sampling variability where it
  measures it (LM30's simulation and resampling, LM33's intervals) and otherwise says once that the number is a
  plug-in estimate with an unmeasured error.
- **Divisors.** As Volume IV: $s$, $s^2$ and $\hat\Sigma$ divide by $T$; $s_{\mathrm u}^2$ by $T-1$. scikit-learn's
  `LedoitWolf` and `OAS` (with `assume_centered=False`) shrink the divisor-$T$ sample covariance toward
  $\bar\lambda I$, $\bar\lambda=\operatorname{tr}\hat\Sigma/N$ (survey and the project environment: equal to
  $(1-\text{shrinkage})\hat\Sigma+\text{shrinkage}\cdot\bar\lambda I$ to rounding error), which matches the book. Every script
  passes `ddof` explicitly.
- **Return type and the domain of log growth.** Portfolio returns are simple: $R_p=\mathbf w^{\top}\mathbf R$ (8.3)
  for weights summing to 1, $\mathbf f^{\top}\mathbf R$ for exposures (8.4). Wealth compounds simple returns; log
  returns are used for sums over days and for growth rates, as Volume III. Every $\ln(1+R)$ states its domain $R>-1$.
  A leveraged or short position checks $1+\mathbf f^{\top}\mathbf R>0$ on every date it is applied to; a path that
  reaches wealth $\le0$ is reported as ruin at that date, never truncated, dropped or floored (guidance).
- **Data.** Five shared samples, plus single-module files (LM34's survivorship ETFs and snapshots; LM35's checkpoint
  universe, built by `vol5_series.py` as one sample of eight funds, its US proxies and 0050's 2007–2008 closes); never
  mix two within one statistic, and name the sample in every caption. The one
  exception: LM35's hypothetical replays of 2008 and 2015 combine funds and proxies in one portfolio return by design,
  labelled *hypothetical*, with each input's source named (decision X27).
  - **E5** (new, the through case): five Taiwan-listed ETFs, daily total returns in New Taiwan dollars. 0050
    (元大台灣50), 00646 (元大S&P500), 00679B (元大美債20年), 00635U (期元大S&P黃金) and 00642U (期元大S&P石油).
    Closes 2017-01-17 → 2026-10-08 on TR23's calendar, built by a new `data/vol5_series.py`. Total return
    $(P_t+D_t)/P_{t-1}-1$ as Volume I (`data/README.md`; on a split day the previous close is restated per current
    share, $P_{t-1}/4$ on 2025-06-18): distributions from `TaiwanStockDividendResult` with
    each fund's own label (0050 `息`, 00679B `除息`; PITFALLS §3), the 0050 4-for-1 split of 2025-06-18 from
    `TaiwanStockSplitPrice`. 00646, 00635U and 00642U pay no distributions (survey and fresh check: 0 dividend rows,
    0 spread mismatches, 0 zero closes, 0 repeated rows). The underlying indices are checked on the issuers' pages in
    the briefs, not assumed from the names. Fund returns are after the funds' fees and the withholding inside them
    (survey: 00646 ran about 1.0 point a year behind SPY's total return in TWD, 2016–2026; the split of that gap is
    not sourced, so no split is printed).
  - **E5's two frames.** The **estimation frame** holds the dates on which every fund has a one-session return
    (`lm10_series.one_session`; a return that spans a fund's halt is dropped): $T=2{,}362$ from 2017-01-18 (fresh
    check), $A=242.951$. The **wealth frame** holds every TR23 session from 2017-01-18 to 2026-10-08 (2,368, fresh
    check): each fund earns its own close-to-close return, a halted fund earns 0 and its spanning return is booked on
    the day it trades again (0050: flat 2025-06-11 → 06-17, then $(4\times47.57)/188.65-1$ on 06-18). Covariances,
    means and every statistic of joint returns use the estimation frame; wealth, drift, costs, drawdowns and every
    return of a portfolio use the wealth frame. A joint computation's inputs ($\hat{\boldsymbol\mu}$, $\hat\Sigma$ and
    its diagonal) use the estimation frame and say so ("on the 2,362 joint dates"); a fund described alone uses its
    own dates, annualized by its own sessions per year (editor's decision on the briefs, X18). (Without the
    wealth frame every rule would miss 2025-06-10 → 06-18: 00642U +12.82%, R1 about +2.7%; fresh check. PITFALLS §3,
    "Aligned samples change the counts".) The scripts print the authoritative counts.
  - **Timing of E5.** The four foreign funds close at 13:30 Taipei time and carry the previous US session (survey:
    00646's daily correlation with SPY's previous session 0.681, with the same-dated session 0.118; not printed,
    since it mixes E5 with US data and needs LM35's pairing rule). 0050 at the same close also reflects that US
    session, so a same-day correlation is not simply biased in one direction (LM27's A27-11, simple returns, ISO weeks
    and calendar months without the sample's first and last: 0050 with 00646 0.599 daily, 0.588 weekly, 0.552
    monthly; with 00679B −0.105, −0.023, −0.013). LM27 shows daily, weekly and monthly
    correlations once and says the daily figure can differ either way; other modules state the frequency they use.
    The rules estimate $\hat\Sigma$ from daily returns.
  - **U28** (Volume II): the 28 TWSE sector price indices, 2008-12-02 → 2026-10-08, $T=4{,}382$, $A=245.4794$, for
    large $N$: covariance-only methods (minimum variance, shrinkage, condition numbers, risk parity, HRP). Price
    indices, no dividends: every caption says so, and no expected return of U28 is used to allocate.
  - **TR23** (Volume III): the TAIEX total-return index, 2003-01-02 → 2026-10-08, $T=5{,}849$, $A=246.12$: Taiwan's
    long history (2008, 2015), Sharpe-ratio statistics, VaR backtests.
  - **T5S** (Volume IV): TAIEX every 5 seconds since 2005, used only through per-day statistics (ROADMAP's data rule:
    no intraday prices or returns are published). The overnight gap is the log change from the previous close to the
    09:01:00 value: the 09:00:00 value is the previous close, and the daily `open` is the stale 09:00:05 value. On
    2025-04-07 the daily open gives a log gap of −5.52% against −10.28% by 09:01:00 (levels verified by the survey).
  - **TX23** (Volume IV): TX settlement prices, for the futures on limit days (LM35).
  - Recorded uses of earlier samples: LM7's 0050/00679B numbers (2,363 returns, keeping the return that spans 0050's
    2025 halt) are quoted as printed; E5's pair has 2,362 joint returns, and LM27 says why once. LM4's, LM19's,
    LM20's and LM22's Sharpe and Kelly numbers are quoted as printed with their module and sample.
- **Through case** (fixed in advance on 2026-10-24, before any result of it was computed; the survey's scouting
  correlations are not results of the rules). Eight rules allocate E5, implemented once in `data/vol5_rules.py`,
  which every module's script imports; no module re-implements a rule. The editor writes `vol5_series.py` and
  `vol5_rules.py` in Stage 1, and a fresh agent verifies them before any writer starts.
  - **Window and dates.** Each signal uses the trailing 504 rows of the estimation frame through the last session of
    a month. The trade is at the close of the next session of the wealth frame on which every fund trades (the
    close is known only after 13:30; Research hygiene). The first signal is the first month-end with 504 rows (fresh
    check: 2019-02-27), its trade the next session (2019-03-04). The last signal is September 2026's (traded
    2026-10-01); valuation ends 2026-10-08 with no terminal liquidation (its cost is not charged; the text says so).
    Before the first trade every rule holds cash; the first purchase pays costs.
  - **Drift.** Between trades, weights drift: $w^{\mathrm{drift}}_{t,i}=w_{t-1,i}(1+R_{i,t})/(1+R_{p,t})$.
  - **R1** equal weights (1/N). **R2** a fixed reference mix, 40% 0050, 20% 00646, 30% 00679B, 10% 00635U, labelled
    *constructed* (LM30's Black–Litterman reference). **R3** long-only minimum variance. **R4** long-only maximum
    Sharpe ratio on the window's sample means in excess of $r_f=1.5\%$ ($r_f/A$ a day, with the estimation frame's $A$, 0.617 bp), solved as the homogenized
    QP $\min\mathbf y^{\top}\hat\Sigma\mathbf y$ subject to $\hat{\mathbf e}^{\top}\mathbf y=1$, $\mathbf y\ge0$,
    $\mathbf w=\mathbf y/\mathbf 1^{\top}\mathbf y$; if no fund's mean exceeds $r_f/A$, R4 holds R3 (the fresh check
    found two or more funds above it at every one of the 92 signals; the fallback serves other universes).
    **R5** R3 with the Ledoit–Wolf covariance (scaled-identity target, scikit-learn). **R6** equal risk
    contributions, long-only. **R7** hierarchical risk parity as López de Prado (2016) publishes it: the distance
    $\sqrt{(1-\rho_{ij})/2}$, the Euclidean distance between columns of that matrix, single linkage,
    quasi-diagonalization and recursive bisection with inverse-variance weights inside clusters (the review of
    2026-10-24 confirmed each step against the paper's SSRN version, abstract 2708678, and the author's HRP.py; its
    Example 2 reproduces; the JPM body was not read, so LM31 cites the article as a whole without a JPM page, decision "Sources read by the second hunt"). **R8** R6 scaled by $L_t=\min\!\big(1.5,\ \bar\sigma_t/\sigma_{t+1\mid t}\big)$,
    set at each monthly trade and drifting between trades. Both volatilities come from one series: R6's new weights
    applied to the window's 504 daily returns (a constant-weight series, defined at every signal, before any book is
    held). $\bar\sigma_t^2$ is its uncentred mean square over the window, and $\sigma^2_{t+1\mid t}$ LM26's EWMA
    ($\lambda=0.94$, uncentred, daily simple returns in decimals) run through the window from the start value
    $\bar\sigma_t^2$ (editor's clarification, 2026-10-24, before any result: the fresh check asked which series). So
    R8 targets R6's own two-year volatility, with no level chosen in advance. Cash
    ($1-L_t>0$) earns $r_f=1.5\%$; borrowing ($L_t>1$) costs $r_f+2$ points $=3.5\%$ a year, an illustrative
    financing rate (Research hygiene puts financing among the costs; no official rate exists), with sensitivities
    at spreads of 0 and 5 points.
  - **Costs** (the cost model below) on every trade, self-financing: with pre-trade wealth $W^{\mathrm{pre}}_t$,
    holdings in money $W^{\mathrm{pre}}_t\mathbf w^{\mathrm{drift}}_t$ and target exposures $\mathbf f$, the post-trade
    wealth $W_t$ solves $W_t=W^{\mathrm{pre}}_t-\operatorname{cost}(W_t\mathbf f-W^{\mathrm{pre}}_t\mathbf w^{\mathrm{drift}}_t)$,
    where the cost of trades $\boldsymbol\Delta$ is
    $0.1425\%\times\lVert\boldsymbol\Delta\rVert_1+\sum_i\text{tax}_i\max(0,-\Delta_i)$, scale-free (no minimum fee);
    the turnover is $\mathrm{TO}_t=\tfrac12\lVert\mathbf f-\mathbf w^{\mathrm{drift}}_t\rVert_1$ (LM8's $\mathbf h$
    counts units and a prime is a derivative, so neither is used here; decision B2). LM27, which owns the wealth recursion,
    prints this equation.
  - **Comparison criteria, fixed now** (precise definitions, 2026-10-24; `vol5_rules.py`, `summary()`). Net of costs:
    annualized log growth $\ln W_{\mathrm{end}}$ divided by the years (calendar days ÷ 365.25, AUTHORING §8), from the
    cash of 1 at the first trade's close, so the first purchase's cost counts; the Sharpe ratio of the daily returns
    from the session after the first trade, in excess of $r_f=1.5\%$, $\times\sqrt{A_{\mathrm w}}$ (one $r_f$ for
    every rule, since R8 holds cash; $A_{\mathrm w}$ is the wealth frame's sessions per year, 243.57 against the
    estimation frame's 242.95, and interest accrues $r_f/A_{\mathrm w}$ per session), and their volatility; the
    maximum drawdown of the path with the starting 1; the annual turnover, the sum of the one-way turnovers after the
    first purchase per year; the costs, the sum over trades of cost ÷ pre-trade wealth (about $\ln$ of gross over net
    wealth). The benchmark is R1. LM33 tests each of R2–R8 against R1 (seven pairs, Ledoit and Wolf 2008) and
    deflates the best rule for $n=8$.
  - **Owners.** Each rule is defined by its module: R3 and R4 by LM28 (unconstrained) and LM29 (long-only, the
    through-case form), R5 by LM30, R6–R8 by LM31; R1 and R2 by LM27. One owner per statistic of the rules, all
    computed by `vol5_rules.py`, net of costs unless the owner shows gross against net: LM27 the accounting
    identities, the wealth recursion, the cost of a trade and the first purchase, MRC, RC and Euler's identity, and R1's first-window risk shares (A27-21); LM28
    every statistic of the first window (its frontier, $\mathbf w^{\mathrm{mv}}$, $\sigma_{\min}$, the funds'
    volatilities and correlations; not the risk shares, nor R2's mean excess return and volatility), the 92 windows'
    $\sigma_{\min}$ range and the U28 halves' gross exposure; LM29 costs as a term in the objective and "R3's bounds
    never bind" (A29-09); LM30 the realized out-of-sample volatility of R1, R3 and R5, the U28 halves' 1/N and minimum
    variance, and R2's first-window mean excess return and volatility (Black–Litterman's calibration, A30-24); LM31 R6–R8's
    weights, risk shares (and R2's first-window shares), exposure path and realized volatility, and the per-trade
    statistics of R8's exposure; LM32 the rules' VaR, ES and drawdowns; LM33 their mean excess returns, R2's and R4's
    realized volatility, their Sharpe ratios, every standard error, interval and test; LM34 net wealth, log growth,
    annual turnover of all eight rules, costs and gross against net; LM35 their scenario losses, including each
    rule's loss on 2025-04-07, and the T5S per-day lows of 2025-04-07 and 2024-08-05 (A35-45). A module that needs another's number cites it with the anchor ID (decisions A1–A6).
  - **The count of trials.** The out-of-sample family is R1–R8 only, so $n=8$. Other variants (LM28's unconstrained
    solutions, LM29's caps and penalties, LM30's Black–Litterman and resampled weights, LM31's inverse-volatility and
    risk-triggered versions) are *In-sample* illustrations or lab exercises. A module may also show one fixed split
    in LM7's pattern (estimate on the first window, hold to the end), labelled *Out-of-sample* and counted in that
    module's hygiene note; none of these is a candidate for "the best rule". LM33 says that $n=8$ treats the rules
    as independent trials while R3 and R5, and R6 and R8, are close, and gives an effective number of trials (Bailey
    and López de Prado 2014). LM34's PBO grid is a separate, declared search made after the fact.
  - The briefs may change a parameter only by a recorded decision in this file before any result is printed.
- **Risk-free rate.** FinMind has no Taiwan interest-rate series (survey: `InterestRate` lists 12 central banks, not
  the CBC). Sharpe ratios keep Volume IV's $r_f=0$ convention, stated in each caption, except in the through case
  (above) and where a riskless asset is part of the problem (LM28's capital market line and tangency, LM29's financed
  leverage), which use $r_f=1.5\%$ a year, LM7's illustrative rate, accrued as $r_f/A$ a day (simple accrual). The
  text says it is illustrative and how much 0% or 2% would change the result.
- **Cost model** (official sources read 2026-10-24; LM34 owns the sources and prints them, every other module cites
  LM34 or this decision before LM34 by a pointer). Each fund follows the rules of its own market: 00679B (E5) and
  00720B (checkpoint) trade on TPEx, the other funds on TWSE. Commission 0.1425% of the value traded on each side:
  TWSE's Operating Rules Art. 94 and, for the TPEx funds, TPEx's 證券商營業處所買賣有價證券業務規則 Art. 64 (¶1–¶3
  unchanged since 2008-02-12), applied to ETFs by TPEx's ETF rules Art. 15 ¶1, let brokers set their rates and
  require notice above 1.425‰, so it is the posted
  reference, not a cap, and brokers' discounts are not modelled. Securities transaction tax on sales: 0.1% for ETFs
  (Securities Transaction Tax Act Art. 2 item 2, 千分之一 on "other securities approved by the government"; Art. 2 last
  amended 1993-01-30, the Act last on 2025-01-02, Arts. 2-2 and 12), 0 for bond ETFs to 2026-12-31 (Art. 2-1, last
  amended 2016-12-30, which suspends it from 2017-01-01 for listed and OTC-listed (上市及上櫃) securities-investment-trust
  bond ETFs, leveraged and inverse ones excluded; 00679B was exempt throughout E5, 00720B from its listing on
  2018-02-01). The futures ETFs 00635U and 00642U pay the same 0.1%: the
  Ministry of Finance's ruling 台財稅字第09700161260號 (2008-08-11) taxes a transfer of futures-trust fund certificates
  at 1‰ under Art. 2 item 2. TWSE's ETF rules page gives 0.1% on every ETF sale with bond ETFs exempt through 2026,
  and the Ministry's 財政統計通報 No. 21 (2024-11-14) states the ETF rate 千分之1 and lists 原型期貨 ETFs' turnover and
  tax, whose ratio fits it (all read 2026-10-24). No
  slippage model, because no sourced spread or impact figure exists for these funds (survey); a sensitivity at twice
  the costs stands in for it, and the text says why the Research hygiene page's rule is met only that way.
- **Sharpe ratio.** As Volume IV: $\mathrm{SR}=(\mu-r_f)/\sigma$ per period, annualized by $\sqrt A$ as a convention on
  simple returns (exact for log returns on uncorrelated days; LM19's (19.9), Lo 2002). LM33 owns the corrections; it
  applies (19.9) and (20.9) rather than re-deriving them. A module that uses monthly returns writes $A=12$ and says
  so.
- **Notation.** AUTHORING §6 plus the table below, which the editor copies into §6 before any writer starts. The
  briefs may propose changes with reasons; the cross-check decides them.

  | Symbol | Meaning (from Volume V) | Against §6 |
  |:--|:--|:--|
  | $\mathbf w$, $N$, $\mathbf w_{t-1}$ | weights ($\mathbf 1^{\top}\mathbf w=1$), number of assets, weights set at the previous close (lm12.md); the held $\mathbf w_{t-1}$ and $\mathbf w^{\mathrm{drift}}_t$ are each fund's value over wealth and sum to the book's exposure ($\mathbf 1^{\top}\mathbf f$ on a trade date, drifting between trades; (27.1)–(27.3), R8) | as §6, scoped |
  | $\mathbf w^{\mathrm{drift}}_t$ | weights after a period's returns, before trading | new; a tilde stays "centred" |
  | $\mathbf f$, $L$, $L_t$ | exposures, total exposure $\mathbf 1^{\top}\mathbf f$, R8's exposure | as §6; a gross limit is written as a number on $\lVert\mathbf f\rVert_1$, not as $L$; LM30 and LM32 write no Cholesky $L$ in the main text |
  | $\lVert\mathbf x\rVert_1$ | the 1-norm; gross exposure $\lVert\mathbf f\rVert_1$ (LM8, lm08.md:178–180) | new row |
  | $\mu_p$, $\sigma_p$, $\sigma_p^2$, $s_p$ | portfolio mean, standard deviation, variance (model and sample) | add $\mu_p$ to the $\sigma_p^2$ row |
  | $\mathbf e=\boldsymbol\mu-r_f\mathbf 1$ | excess returns (LM7, lm07.md:60) | new row (§6 mentions it only in the basis-vector row); LM27–LM31 write no basis vector $\mathbf e_i$ |
  | $\delta$ | risk aversion in the exposure form $\mathbf f^{\top}\mathbf e-\tfrac{\delta}{2}\mathbf f^{\top}\Sigma\mathbf f$ with a riskless asset; LM28 cites LM7's two-asset $\mathbf f^*=L^*\mathbf w^{\mathrm{tan}}$ (lm07.md:484) and leaves the N-asset Kelly identity to LM43 | new; LM25's $\delta$ is not cited in Volume V |
  | $\lambda$, $\nu_i$, $\mathcal L$ | equality and inequality multipliers, Lagrangian, LM7's signs; a second equality multiplier takes a letter subscript ($\lambda_b$, $\lambda_\mu$) | as §6; in LM30 multipliers are $\nu$ ($\lambda_k$, $\bar\lambda$ are eigenvalues); in LM31, LM32 and LM34 $\lambda$ is only LM26's decay |
  | $K$, $\mathbf b$ | constraint matrix and right-hand side, $K\mathbf w=\mathbf b$ (LM28, LM29, LM35; modules without bets) | scoped as §6's $M\mathbf x=\mathbf b$ |
  | $\mathbf w^{\mathrm{mv}}$, $\sigma^2_{\min}$, $\mathbf w^{\mathrm{tan}}$, $\mathrm{SR}^*$ | minimum-variance weights and variance, tangency weights (LM7), best Sharpe ratio | new for mv; star only for an optimum |
  | $\beta_{i,p}$, $\beta_i$ | an asset's beta to its portfolio, $\operatorname{Cov}(R_i,R_p)/\sigma_p^2$; its market beta (LM23's (23.1)) | new for $\beta_{i,p}$ (LM27) |
  | $\mathrm{TO}_t$; $\text{tax}_i$ | one-way turnover $\tfrac12\lVert\mathbf w_t-\mathbf w^{\mathrm{drift}}_t\rVert_1$; a fund's tax rate on sales (upright word) | new; no scalar cost symbol next to $\mathrm{TO}$ |
  | $c$, $\hat\Sigma_{\mathrm{tgt}}$, $\hat\Sigma_c=c\hat\Sigma+(1-c)\hat\Sigma_{\mathrm{tgt}}$ | the data's weight in a shrunk covariance (LM24's $c$; scikit-learn's `shrinkage_` is $1-c$), target, shrunk matrix (LM30) | extends §6's $c$ row (LM24) to LM30, which has no Kelly fraction |
  | $n_0$, $\mathbf w_{\mathrm{ref}}$, $\mathbf e_{\mathrm{eq}}$, $K\mathbf e=\mathbf b+\boldsymbol\varepsilon$, $\Xi$ | Black–Litterman: prior worth in observations ($\tau=1/n_0$; LM24's $n_0$), reference weights, implied excess returns $\delta\Sigma\mathbf w_{\mathrm{ref}}$, views on excess returns, view-error covariance | new; $P$, $Q$, $\Omega$, $\tau$, $\pi$ are taken book-wide |
  | $\mathrm{MRC}_i$, $\mathrm{RC}_i$ | marginal and component risk contribution, $\mathrm{RC}_i=w_i(\Sigma\mathbf w)_i/\sigma_p$, $\sum_i\mathrm{RC}_i=\sigma_p$ (LM27 owns, LM31 uses) | new |
  | $\mathbf b$ in LM31 | risk budgets (shares summing to 1); LM31 writes its constraints out, without $K\mathbf w=\mathbf b$ | scoped |
  | $d_{ij}$ | HRP's correlation distance $\sqrt{(1-\rho_{ij})/2}$ (LM31), half of LM8's per-date distance $\sqrt{2(1-\rho)}$ (lm08.md:290); the second distance takes a symbol the brief chooses (no tilde, no prime) | new, entries only; $d^2$ (LM16) and $d$ (LM23) do not occur in LM31 |
  | $\bar\sigma_t$, $\sigma_{t+1\mid t}$; $\Sigma_{t+1\mid t}$ | R8's window volatility and EWMA forecast (no hat, as LM26 prints it); the EWMA covariance matrix $\lambda\Sigma_{t\mid t-1}+(1-\lambda)\mathbf R_t\mathbf R_t^{\top}$ on simple returns | as LM26 |
  | $W^{\mathrm{pre}}_t$, $A_{\mathrm w}$ | wealth before the day's trade; the wealth frame's sessions per year | new (decision B2) |
  | $\mathbf y$ | LM29's homogenized variable of the maximum-Sharpe QP, and LM31's ERC variable before normalizing | scoped (LM29, LM31; a module without least squares) |
  | $u$, $\operatorname{VaR}_u$, $\operatorname{ES}_u$, $m$ | tail probability ($u=0.01$ for "99% VaR"); value at risk $-F_{R_p}^{-1}(u)$ and expected shortfall, positive for a loss; horizon in days | §6's $u$ |
  | in LM32 | $\alpha$ is the tail index (LM15, LM20); GARCH is cited by tag with its coefficients named in words; $k$ is Hill's count, a number of standard deviations is written in words; $\ell$ is a block length (LM32 cites no log-likelihood) | scoped, one meaning per module |
  | $\ell$ in LM34, LM35 | LM34's mean block length; LM35's loss level of a reverse stress test | scoped |
  | in LM33 | $\alpha$ is the significance level and (23.8) is not cited; the HAC lag and the block length take different letters, declared | scoped |
  | $\mathrm{DD}_t$, $\mathrm{MDD}$, $\mathrm{DD}^0_t$ | drawdown from the running peak (LM1, $\ge0$), its maximum, the loss from initial wealth $\max(0,1-W_t/W_0)$; an underwater chart plots $-\mathrm{DD}_t$ and says so | DD as §6; MDD, $\mathrm{DD}^0$ new |
  | $\widehat{\mathrm{SR}}$, $\mathrm{SR}_0$, $n$ | estimated Sharpe ratio, a benchmark ratio (no star), number of trials (§6's $n$); LM33 and LM34 say once that (21.6)–(21.9)'s $m$ tests read as $n$ trials | $\mathrm{SR}_0$ new |
  | PSR, DSR, MinTRL, PBO | upright abbreviations (LM33, LM34) | new |
  | $\mathbf R^{\mathrm{sc}}$ | a stress scenario's return vector; P&L $W_0\mathbf f^{\top}\mathbf R^{\mathrm{sc}}$ (LM8's (8.2) with exposures; LM35 writes no holdings $\mathbf h$) | new |

  Not used in Volumes V–VI: Merton's scalars $a,b,c,d$ for the frontier (they clash with the bets, the Kelly fraction
  and the coefficient count; write the frontier with $\mathbf 1^{\top}\Sigma^{-1}\mathbf 1$ and its kin), $\gamma$ or
  $\lambda$ for risk aversion, $\alpha$ for a VaR level or a shrinkage intensity, $P$/$Q$/$\Omega$/$\tau$ for
  Black–Litterman, $\kappa$ for a VaR threshold (LM5's local $\kappa$; $\kappa$ is the condition number), a scalar
  "tc".
- **Solver output.** Solvers get annualized inputs ($A\hat\Sigma$, $A\hat{\boldsymbol\mu}$; LM29's A29-24: at the
  92 signals CLARABEL's defaults missed the exact long-only solution by up to 2.1e-3 in a weight on daily units and
  3.4e-5 on annualized ones; inputs in percent, as LM35's reverse stress test uses, are allowed with their KKT
  residuals printed). Tolerances are set and printed (CLARABEL `tol_gap_abs`, `tol_gap_rel`, `tol_feas` 1e-12 for
  quadratic and linear programs and 1e-10 for cone programs, where 1e-12 ends at `optimal_inaccurate`; OSQP
  `eps_abs`, `eps_rel` 1e-10 with polishing; a conic cross-check of an exact solution agrees to 1e-5, as
  `vol5_rules.py`'s ERC check; decision X19); the status must be `optimal`;
  every printed solution is checked by its KKT residuals and against a closed form or a second solver, and the text
  names the solver. R6 is computed in `vol5_rules.py` by Newton's method on $\tfrac12\mathbf y^{\top}\Sigma\mathbf y-\tfrac1N\sum_i\ln y_i$ (stopped when $\max_i\lvert y_i(\Sigma\mathbf y)_i-1/N\rvert<10^{-13}$, its risk shares then equal to 1e-10), with cvxpy's
  log-barrier form as the cross-check, agreeing to 1e-5 (a fixed point need not settle, LM31's E3). A weight with $\lvert w_i\rvert<10^{-6}$ prints as 0, and a constraint is
  active when its slack is below $10^{-6}$. Every printed number comes from a fresh `Problem` (no warm start).
  Near-collinear assets need a stated tie-break before their weights are printed. cvxpy's `Variable.value` is typed
  `ndarray | None`: narrow it with an `assert` before use (ty).
- **Counting, simulation, quantiles, rounding.** As Volume IV: one counting guard or exact arithmetic; one generator
  per experiment, `np.random.default_rng([e, 20261011])`, with draws, seed and standard error printed; every quantile
  $\hat F^{-1}(u)=x_{(\lceil uT\rceil)}$ (`method="inverted_cdf"`); flag values within a tenth of a rounding unit of a
  boundary. The historical ES estimator is (32.2), Acerbi and Tasche's form on the empirical distribution (LM32's
  decision), used by every module. Block bootstraps follow LM22: the stationary bootstrap draws each resample as
  LM22's `stationary_idx` does (`integers` then `random`, identical to arch's `StationaryBootstrap`), the block length
  is LM22's rule (lm22.md:254) applied to the series the statistic involves (for a statistic of the differences from
  R1, those differences, as LM34's reality check; for a statistic of several series' own returns, the largest length
  among them, as LM33's Ledoit–Wolf test), and a circular block bootstrap uses the same length; with $T$ not a multiple of $b$, a
  resample draws $\lceil T/b\rceil$ blocks and is cut to $T$, and a Götze–Künsch block variance uses the
  $\lfloor T/b\rfloor$ complete blocks (decisions D, X15). Week keys are (ISO year, ISO week).
- **Python.** NumPy and SciPy first, Polars for data. cvxpy 1.9.3 and scikit-learn 1.9.1 are in the main dependencies
  (approved 2026-10-11; added 2026-10-24, `40e1876`: 12 packages, no existing pin changed, `./build.sh --data`
  unchanged). cvxpy's default QP solver is OSQP; CLARABEL, SCS, HiGHS and SciPy are installed. scikit-learn's
  shrinkage target is $\bar\lambda I$ only (no constant-correlation target, no Black–Litterman, no HRP): those are
  the book's own code. HRP uses `scipy.cluster.hierarchy`: symmetrize the correlation matrix, set its diagonal to 1
  and the distance's diagonal to 0 (`np.corrcoef` is asymmetric at 1e-16, which `squareform` rejects; fresh check:
  symmetrizing alone still fails in 191 of 200 cases). arch (locked) gives GARCH VaR.
- **References.** Cite only entries in `project/SOURCES.md`. Stage 1 adds the batch's entries after the briefs'
  source checks. Verified on Crossref by the survey's critic and the fresh check (DOIs and pages): Merton (1972),
  Tobin (1958), Black and Litterman (1992), Ledoit and Wolf (2003 JEF, 2004 JMVA, 2004 JPM; three targets,
  scikit-learn uses JMVA 2004), DeMiguel, Garlappi and Uppal (2009), Jagannathan and Ma (2003), Chopra and Ziemba
  (1993, 19(2): 6–11), Maillard, Roncalli and Teïletche (2010), López de Prado (2016), Moreira and Muir (2017),
  Artzner, Delbaen, Eber and Heath (1999), Acerbi and Tasche (2002), Kupiec (1995), Christoffersen (1998),
  Magdon-Ismail et al. (2004), Ledoit and Wolf (2008), Bailey and López de Prado (2012, 2014), Bailey, Borwein, López
  de Prado and Zhu (*J. Computational Finance* 20(4): 39–69; it counts $\binom{16}{8}=12{,}870$, not the 12,780 the
  paper prints). Idzorek's chapter is 2007, not 2005; He and Litterman (1999) is a Goldman Sachs note. Unequal risk
  budgets: Bruder and Roncalli (2012), as LM31 cites them; Maillard et al. cover equal contributions. Not printed
  until read in the original: Chopra and Ziemba's ratios, Black and Litterman's own claims, Mertens (2002; LM20
  derives (20.9) without it). Christoffersen (1998, in the author's final manuscript) and Ledoit and Wolf's (2008)
  bootstrap scheme (in the JEF text) have been read (decision F; "Sources read by the second hunt").
  PBO uses combinatorially symmetric cross-validation, not a bootstrap.
- **Chinese terms.** AUTHORING §1 (樂詞網; English in parentheses at first use in each box). Looked up 2026-10-24
  (survey); recorded in SOURCES at Stage 1. From 樂詞網: 投資組合, 效率前緣, 最小變異數投資組合, 資本市場線, 風險規避,
  二次規劃, 凸規劃 (convex optimization; 凸函數, 凸集), 拉格朗日乘數, 收縮, 收縮估計量, 共變異數矩陣, 估計誤差, 條件數,
  風險平價 (risk parity; 風險平價投資組合 in the statistics listing), 風險預算, 層次叢集法, 樹形圖, 風險值, 夏普比率,
  過度配適, 交易成本, 週轉率, 壓力測試, 情境分析, 敏感度分析, 無風險利率, 資產配置, 槓桿, 限制條件, 目標函數, 對偶問題,
  交叉確認, 資料偵伺, 選擇偏誤, 歷史模擬法, 保證金追繳, 條件風險值 (CVaR, named once). The book's own forms, printed
  with their English in every box that uses them: 切點投資組合 (tangency portfolio, LM7's Glossary; lm07.md:511–512's
  切點組合 follows at Stage 4), KKT 條件, 預期短缺 (expected shortfall, LM5's settled form), 回撤, 最大回撤, 回測,
  波動率目標 (volatility targeting), 層次風險平價 (hierarchical risk parity), 前視偏誤 (look-ahead bias), 存活者偏誤
  (survivorship bias), 滾動前進測試 (walk-forward test; the brief may keep the English only), 尾部風險 (tail risk),
  一致性風險量數 (coherent risk measure; 風險量數 is the statistics listing's). From 樂詞網's mathematics listing
  (checked 2026-10-24): 劣可加性 (subadditivity; the survey's "no entry" was a query error).
- **Research hygiene.** Volumes V–VI are the first where *Out-of-sample* results lead. The through case's settings
  are *fixed in advance* (above) and say so in each note; an in-sample frontier or allocation is *In-sample*, a
  simulated one *Model*, a hand-built scenario *constructed* or *hypothetical*. Every module states how many rules or
  versions it compared on the same data (LM21's rule).
- **Charts.** As Volume IV (AUTHORING §7) plus the additions the owner approves (capability check). At most four named
  series: E5 has five funds, so a chart of all five uses small multiples, four funds plus one in `"var(--muted)"`
  named in the caption, or portfolios as series and funds as categories (survey: a fifth series without a colour draws
  black). A dashed curve is one series, never a chain of segments (survey: segments lose the dash). A dendrogram is
  drawn with scatter `lines` (survey prototype). Every value the text cites is plotted or printed; JSON at most
  300 KB; no intraday price path is published (per-day statistics only). Volume IV's rule X37 holds: no published
  file carries a daily series derived from FinMind data in date order at full resolution, or anything from which one
  can be rebuilt (buy-and-hold weights rebuild price ratios); a chart over many years is thinned to weekly points plus
  every cited value, and no file carries more than 1,172 dated points of a market series (decision X6).
- **Widgets.** A browser widget runs no optimizer: it uses closed forms, precomputed grids from the module's script,
  or module-local code under 30 lines (for example a 5×5 solve with a positive-definiteness check) tested against
  Python as `data/lm15_charts.py` does. Student-$t$ quantiles come from an embedded grid (`Book.dist.tInv` was not
  approved, ROADMAP). `Book.controls`, `Book.rng`, `Book.dist`; the initial state computes within the PDF printer's
  wait.
- **Labs.** One per module, `build/make_labNN.py`, reading only its own `data/` folder (`data/make_lab_data.py`). A
  lab gets derived files from `make_lab_data.py`, built locally from `data/raw/` and never committed: the rules'
  per-date targets and exposures, E5's estimation frame and its wealth frame with the traded flags, the eight rules' net and gross wealth paths, LM34's 60-configuration
  daily returns (`lm34_grid.csv`), the T5S days the labs use (per-day statistics and, for
  the days a lab studies, the raw day), the checkpoint universe's frames, LM35's proxies and its daily rows (open, high, low, close, volume) of 0050, 0056 and 00720B (decision X21); LM32's lab refits LM26's GARCH laws and runs its EWMA on TR23 itself, as Lab 26 does. A lab
  carries no copy of `vol5_rules.py`; it re-implements only its own module's rule as an exercise and checks it
  against those files. LM35's checkpoint (lab part 9) is the exception: the reader implements R1, R3 with its 30% cap,
  R6 and R8 on the checkpoint universe, and the reference answers from `data/lm35_numbers.py` sit in a collapsed
  cell. The derived files also include TX23's limit-day rows (LM35); `lm34_grid.csv` needs a processed source, which LM34's numbers script writes to
  `data/processed/` (proposed with the `make_lab_data.py` change).
  LM35's lab ends with the batch's checkpoint (guidance, below).
- **Problems.** As Volume IV, plus: an optimization stem states the feasible set, the solver tolerance and the
  rounding; a backtest stem states the window, the rebalancing dates, the costs and the label.
- **Leads and tags.** As Volume IV: a module's `leads` are the modules that cite one of its tags or results, and the
  modules its text points to forward. LM32–LM35 list the Volume V modules whose rules or results they cite as
  prerequisites (a module-level link; ROADMAP's volume map, "IV → VI", is unchanged, since a module's own
  prerequisites are its front matter).

### Curriculum guidance (`plans/curriculum-guidance.md`), adopted for batch 4

| Recommendation | Decision | Reason |
|:--|:--|:--|
| V–VI tie estimation, constraints, costs and hygiene together (g:25) | adopted | the through case does it: the same rules are estimated, constrained, costed, measured, backtested and stressed |
| Each module says which capability layer it adds (g:30) | adopted | section pattern |
| Three outcome levels per brief (g:54–58) | adopted, in the briefs | ROADMAP's brief format; the page keeps AUTHORING §3 (above) |
| Checkpoint after Volume VI: allocate and stress under leverage, turnover and cost limits; out-of-sample comparison; scenario losses; explain how constraints change the allocation (g:45) | adopted, adjusted | the modules practise each part on E5; LM35's lab ends with the whole task on a universe the modules did not use, so that the reader cannot reuse E5's answers (checkpoints may reuse data, g:49; a fresh universe is the editor's choice for that reason); no new module (SPEC §4) |
| Checkpoint after Volume IV (a strategy's characteristics and uncertainty, g:44) | adjusted | Volume IV is published; LM33's first section does that task on the through case's returns |
| Density: reading time is not mastery (g:60–63) | adopted | LM29, LM30, LM32 and LM34 carry the most topics; their spines name what moves to the lab and to problems |
| Decision flow (data visible at decision time; target from estimate; trades from current holdings; costs and cash in the wealth recursion; periodic re-estimation against risk-triggered change, g:69–85) | adopted for V–VI's part | LM27 (drift, trades, the wealth recursion), LM29 (costs in the objective), LM31 (periodic rebalancing against a volatility trigger), LM34 (timing); the full flow is Volume VIII's |
| Different failures in one case: weak growth, a drawdown limit, funding, wealth ≤ 0 (g:87–90) | adopted | the through case shows them together: LM34 (net log growth), LM32 (drawdowns), LM35 (funding and ruin under R8's leverage); LM35's summary compares the four on the same rules |
| Define drawdown: from the peak or from initial wealth (g:92) | adopted | $\mathrm{DD}_t$ and $\mathrm{DD}^0_t$ (notation) |
| A probability bound keeps its risk definition and model (g:93) | adopted | LM32's Brownian-motion drawdown results are stated with their model |
| Wealth ≤ 0 or a net return ≤ −100% ends log growth; never hidden (g:94) | adopted | "Return type and the domain of log growth" |
| Surviving the scenarios does not cover unseen losses (g:95) | adopted | LM35's closing pitfall |
| Fix windows, frequency, limits, costs and criteria before evaluation (g:111) | adopted | "Through case" |
| Compare fixed positions, volatility targeting and Kelly-type rules (g:113) | adjusted | R1, R2 and R8 in V–VI; Kelly-type sizing is Volume VIII's (ROADMAP's Kelly row) |
| "Data too thin to support more leverage" is a valid conclusion (g:116) | adopted | LM33 (minimum track record), LM34 |
| Check that each outcome is taught, practised and assessed (g:124) | adopted | `reviews/REVIEW_PROMPT.md` item 10 |
| Two Boyd papers on risk-constrained and robust Kelly (g:134–139) | left to Volume VIII | Kelly sizing; their drawdown definition is checked in the original there |

## Capability check (2026-10-24)

What the spines need and the repository lacks (survey, its critic and the fresh check: `book.js` rendered in headless
Chromium, `build/`, `data/`, `pyproject.toml`). **The owner approved every item on 2026-10-24:** (A); (B1)–(B4);
(B5) with US proxies; (C1)–(C3); and option (i) for (D). Each piece is built by the editor and reviewed by a fresh
agent (0 differences on the published pages) before any writer starts. On the same day the owner also approved DBO as a second oil proxy for
  LM35 (00642U tracks an enhanced crude-oil index; in 2020 it lost 46.4% against USO's 60.7% and DBO's about 46%).
  0050's own 2007–2008 closes and distributions extend an E5 fund's data for LM35's replay on "the funds that existed"
  (B1's E5 data, registered the same way; the editor's reading of B1, which covers 0050 only over E5's span,
  awaits the owner's confirmation).

- **(A) Packages: approved 2026-10-11; added 2026-10-24 (`40e1876`).** cvxpy 1.9.3 (Apache-2.0) and scikit-learn
  1.9.1 (BSD-3-Clause) with 10 more packages, about 78 MB unpacked, cp313 Windows wheels for all, no existing pin
  changed; every data step reproduced the committed outputs.
- **(B) Data and shared code.**
  1. E5 and the checkpoint universe: register with the existing `fetch_finmind.py --add` (no change to it) the
     prices of 00646, 00635U and 00642U, and of 0056, 00662 and 00720B for LM35's checkpoint, with the columns
     `date, open, max, min, close, spread` (a locked day shows as open = high = low = close), their distributions
     (`TaiwanStockDividendResult`: 0056 `息`, 00720B `除息`, each label checked on the fund's own records) and the
     splits (`TaiwanStockSplitPrice`); one OHLC file for 0050 over E5's span (the registered 0050 files keep only
     `date, close, spread`). About 15 calls, all Free.
  2. A new `data/vol5_series.py` builds E5's two frames and the checkpoint universe and checks them: TR23's
     calendar, the spread column against each close in exact arithmetic, every ex-date and split, zero closes, and
     values repeated from another date or another series (PITFALLS §3).
  3. A new `data/vol5_rules.py`: the eight rules, the cost model and the wealth recursion, imported by the nine
     modules' scripts; `make_lab_data.py` gains the derived weights and the wealth frame for the labs.
  4. LM34's survivorship example: `TaiwanStockDelisting` (Free) and the prices of a few delisted ETFs
     (`TaiwanStockPrice` still serves them), registered with `--add`.
  5. Optional, LM35: US proxies for the 2008 and 2015 replays, when 00646, 00679B, 00635U and 00642U did not exist (00635U in
     fact traded from 2015-04-15, before the 2015 window opens at the 2015-04-27 peak: fresh check of 2026-10-31;
     GLD still stands in for it)
     (`USStockPrice` for SPY, TLT, GLD and USO, and USD/TWD from `TaiwanExchangeRate`, both Free, about 6 calls),
     paired as the survey found the data behave: the New York close of date D with the first FX row dated after D,
     and a Taiwan date compounding the US sessions before it (FX rows also exist on Taiwan closures). Depends on (D).
- **(C) Chart kit** (`book.js`, `build.py`, AUTHORING §7), each optional with a fallback.
  1. Stacked bars, `stack: true` in `barChart`, with negative values stacked below zero (risk contributions, LM27
     and LM31; loss attribution, LM35): about 30 lines and a build check. Fallback: grouped bars.
  2. `curves` in scatter plots (a dashed frontier or capital market line through a cloud of portfolios, LM28 and
     LM30): about 15 lines and a length check. Fallback: line-chart branches.
  3. A build check that a chart with more than four series gives each a colour: about 6 lines.
- **(D) A defect in published Volume I data (technical; found by the survey, confirmed by the editor 2026-10-24).**
  FinMind's `Adj_Close` is rebuilt backward from the latest day at each retrieval. A re-fetch of LM3's
  `QQQ__us_2022.csv` today differs from the registered file by one cent in two cells (2022-06-24, 2022-08-19;
  `Close` and TQQQ unchanged). `fetch_finmind.py` then writes `QQQ__us_2022.csv.new` and exits 1, so a reader who
  builds `data/raw/` from the API never gets the file, `./build.sh --fetch` stops, and `make_lab_data.py` (which
  builds every lab's files in one dictionary) fails for all labs. QQQ's next distribution will rescale the whole
  column. Options: (i) let `fetch_finmind.py` verify entries marked as back-adjusted by their returns, or by levels
  normalized to the window's first day, to a stated tolerance, and accept such a re-fetch (fixes QQQ and makes (B5)
  safe); (ii) register `close` plus the distributions implied at registration as a derived committed file; (iii)
  as a stopgap, make `make_lab_data.py` skip a lab whose inputs are missing, with a message. The editor recommends
  (i), reviewed by a fresh agent, with LM3's numbers rechecked.

Not proposed (fallbacks are good enough): a shared linear-algebra helper in `book.js` (widgets embed grids or a
module-local solve), ETF minute bars (the daily high, low and close show a limit lock), more TX minute bars, published
intraday paths (per-day statistics suffice; ROADMAP's data rule), a market-value pipeline for Black–Litterman (R2 is
the constructed reference), and any Taiwan interest-rate history from outside FinMind (the owner's data rule).

## Decisions on the survey and the fresh check (2026-10-24)

- **Risk decomposition.** LM27 owns the bookkeeping: $\sigma_p^2$, $\operatorname{Cov}(R_i,R_p)$, $\beta_{i,p}$,
  $\mathrm{MRC}_i$, $\mathrm{RC}_i$ and Euler's identity, and "which split is meaningful" (lm10.md:225). LM31 uses
  contributions as targets (budgets, ERC). Factor risk: LM27 decomposes a portfolio's variance with LM23's market
  betas ((23.1)); LM30 owns its estimation (ROADMAP's Factors row, amended). The syllabus line of LM31 follows at
  Stage 4.
- **Covariance forecasting** (lm26.md:409, "LM30's and LM31's subject"): LM31 forecasts the portfolio's variance with
  LM26's EWMA (R8) and states the EWMA covariance matrix
  $\Sigma_{t+1\mid t}=\lambda\Sigma_{t\mid t-1}+(1-\lambda)\mathbf R_t\mathbf R_t^{\top}$ (no hat, simple returns, B1)
  in one paragraph;
  LM30 compares the sample and shrunk matrices out of sample (with LM26's QLIKE, (26.8), if the brief wants a loss);
  multivariate GARCH is out of scope.
- **LM29's scope.** Convex sets and functions in general (lm07.md:268, lm10.md:446), KKT for inequality constraints
  on portfolios (lm07.md:522), quadratic programs, cvxpy. Linear programs appear as the case of a linear objective;
  Rockafellar–Uryasev's expected-shortfall minimization is a problem in LM32, citing LM29.
- **LM28 and Kelly.** LM28 states the N-asset tangency portfolio, writes risk aversion in the exposure form, and cites
  LM7's two-asset Kelly–tangency result; the N-asset identity and growth-optimal leverage stay LM43's.
- **LM32's load** (published promises beyond the syllabus line): the standard error of a sample quantile
  (lm20.md:276), VaR from a tail model (lm20.md:449), GARCH and EWMA VaR (lm26.md:183), importance-sampling Monte
  Carlo VaR (lm18.md:300), tail measures needing fewer moments (lm05.md:369), drawdown as a path statistic
  (lm19.md:138). All are kept; the spine names what goes to the lab or problems. LM32 cites LM18's published tags
  (18.1)–(18.3) and (18.5)–(18.7); the Volume III brief's tag list is stale (survey).
- **LM33's load:** HAC (23.7), Ledoit and Wolf's (2008) two-Sharpe test (a studentized block bootstrap: its scheme is
  checked in the original; LM22's (22.4) and circular blocks, lm22.md:192), deflation for the number of trials (with
  (21.9)), haircuts (Harvey and Liu 2015), the minimum track record (one-sided at $\mathrm{SR}_0$, with its "1 +"
  term; linked to (21.4), which is two-sided). PSR uses (20.9) with raw kurtosis: TR23's raw 8.27 is at lm20.md:370,
  388 and 403 (excess 5.27 at lm19.md:20), 0050's 8.12 in LM4–LM5 is excess: every kurtosis printed says which.
- **LM34 against the Research hygiene page and LM21.** The page states rules without mathematics; LM21 owns FWER,
  Holm, BH, (21.9) and Experiment 10 (10,000 random rules on TR23, seed `[10, 20261011]`). LM34 adds what corrects
  a search under dependence (White's reality check by the stationary bootstrap, the dependent counterpart of (21.9);
  Romano–Wolf and Hansen's SPA stated) on Experiment 10's family, PBO by CSCV, walk-forward protocols, look-ahead and
  survivorship shown on data, and costs. It re-teaches none of Bonferroni, Holm, BH or DSR. ROADMAP's Research
  hygiene row gains the reality check under dependence.
- **LM35 against LM39 and Volume VIII.** LM35 replays gaps and crashes without probabilities; LM39 models jumps.
  Margin calls appear only with dated official TAIFEX tables (ROADMAP's Volume VIII row); otherwise LM35 checks
  equity, not margin. A one-day return that spans holidays says so (2025-04-07 follows four non-trading days;
  survey). The reverse stress test ranks shocks by LM16's Mahalanobis distance (lm16.md:322) as a distance only:
  LM16's tail probability for it ((16.9), lm16.md:363) is not attached (ROADMAP's Stress row).
- **Limits and locks.** FinMind's `TaiwanStockPriceLimit` is wrong for ETFs (survey: 0050's `limit_down` 158.5 on
  2025-04-07, when 0050 traded at 158.4 all day, exactly −10%). TWSE's ETF rules page (read 2026-10-24): the daily
  limit is 10% as for stocks, but an ETF holding overseas stocks has none; ticks are 0.01 below 50 and 0.05 from 50.
  The rule's full scope is TWSE's 受益憑證買賣辦法 Art. 8 ¶1 (read in the original on 2026-10-24 by the source check):
  no daily limit for index ETFs with foreign constituents (bonds included), futures-trust ETFs tracking a foreign
  futures index, offshore ETFs and foreign-constituent active ETFs; ¶2 gives a leveraged or inverse ETF on an
  all-domestic index 10% times its multiple. Art. 8 was last amended on 2024-12-31 (the rules' version date,
  2025-09-30, changed other articles), and items 1–3 have had the same content since 2016-06-03 (item 1 reworded on 2024-12-31), so the
  rule covers E5's whole
  span for the TWSE funds. The TPEx funds 00679B and 00720B follow TPEx's 指數股票型基金及主動式交易所交易基金受益憑證買賣辦法
  Art. 7 ¶1 item 一 (Art. 7 as amended 2024-12-31; foreign bonds defined in Art. 2-1): no daily limit for an index ETF
  with foreign constituent securities; that text has stood since 2017-03-01, and TPEx's listing notices (00679B
  2017-01-13, 00720B 2018-01-25) state 無漲跌幅度限制. Among the funds used only 0050 and 0056 have the 10% limit (the
  data agree: 00646 fell 12.59% on 2025-04-07, 00720B closed −11.25% on 2020-03-19). A locked day is shown by the
  daily open, high, low and close: on 2025-04-07 0050 traded 29.6 million shares,
  all at 158.4 (fresh check), so sales executed at the limit, none below it, queued orders were not guaranteed to
  fill, and the next open was 151.2.
- **Unexplained extremes.** 2026-07-17 (TR23 −6.46%) and 2026-07-31 (+7.98%) are real in the data (T5S 13:30:00
  equals the close); a cause is printed only from a dated source. The same holds for every scenario's narrative.

## Editor's decisions on the briefs (2026-10-24)

The nine briefs were drafted (an interrupted first run, resumed from its files), their 423 anchors recomputed
independently (416 reproduced as defined; the seven others trace to an unstated bootstrap convention, a median rule,
an EWMA start and a week key, decided below), and a fresh agent checked the nine briefs across modules (items X1–X27;
no critical item). The editor checked the critical arithmetic himself. Each brief is revised to these decisions, and
the anchors a revision adds or changes are recomputed independently afterwards. The shared decisions above already
carry the decisions marked there (Owners, Solver output, Charts, Labs, frames, bootstrap conventions, notation,
limits).

### Across modules

- **A. Owners.** A1: each rule's loss on 2025-04-07 is LM35's (LM35's replay is a frozen book, $\mathbf f^{\top}\mathbf R$,
  without the day's interest; LM32's case keeps the six TAIEX models' VaR forecasts and points to LM35 for the rules'
  losses; LM32's X8 drops its "7 April return" column and E10 compares ES and MDD only). A2: annual turnover of every
  rule is LM34's; LM31 prints only R8's per-trade exposure statistics (mean over the 91 trades after the first
  purchase, largest trade), and LM29's X5 prints its planned turnover relative to $\theta=0$, labelled *planned*,
  pointing to LM34. A3: LM33 owns the rules' mean excess returns, R2's and R4's realized volatility and every
  standard error; LM29's Leaves read "R3 → LM30, R4 → LM33". A4: LM28 owns every first-window statistic except
  the risk shares (R1's are LM27's, A27-21; R2's are LM31's) and R2's mean excess return and volatility,
  Black–Litterman's calibration (LM30's, A30-24; LM31 echoes them). A5: duplicates get one owner — the U28 halves'
  1/N and minimum variance are LM30's, the 92 windows' $\sigma_{\min}$ range and the halves' gross exposure LM28's, the
  cost arithmetic of a trade and the first purchase LM27's, "R3's bounds never bind" LM29's (A29-09), the T5S per-day
  lows of 2025-04-07 and 2024-08-05 LM35's (A35-45; LM32's lab echoes them); TR23's 2025-04-07 returns are cited to
  lm26.md:32, not anchored again. A6: MRC, RC and Euler's identity are derived in LM27 only; LM31 cites (27.5)–(27.6), and
  its outcome 1 becomes "derive the budget conditions (31.1) and show when ERC gives inverse-volatility weights".
- **B. Notation** (AUTHORING §6 follows). B1: the EWMA forecast has no hat, $\sigma_{t+1\mid t}$, as LM26 prints it;
  the matrix is $\Sigma_{t+1\mid t}=\lambda\Sigma_{t\mid t-1}+(1-\lambda)\mathbf R_t\mathbf R_t^{\top}$ on simple
  returns. B2: $W^{\mathrm{pre}}_t$ and $A_{\mathrm w}$ are book-wide from Volume V; the cost recursion uses them
  (shared decision "Costs"). B3: scoped rows for $\mathbf y$ (LM29, LM31), $\ell$ (LM32, LM34, LM35) and $\delta$
  (LM28, LM29, LM30). B4: LM30 states its multiplier scale against LM29's once (Jagannathan and Ma's
  $\hat\Sigma\mathbf w=\nu_0\mathbf 1+\boldsymbol\nu$ is half of (29.5)'s), and its $\hat{\mathbf f}$ is the vector form.
  B5: the briefs' local symbols are accepted as declared (LM28 $\mathrm{SR}_\infty$ and the bold $\boldsymbol\lambda$
  with its rule; LM29 $\theta$, $\nu^{\mathrm{cap}}$, $\Delta^{\pm}$, $u$, $v$, $\omega$, $\mathcal C$, and $V$
  declared; LM30 $\hat\Sigma_\nu$, $\mathbf w^{\mathrm{lo}}$, $\sigma^2_{\hat\Sigma}$, $\mathbf e_{\mathrm{BL}}$,
  $\mathbf f_{\mathrm{BL}}$, $\hat\Sigma_F$; LM31 $\sigma^2_{(1)}$, $\sigma^2_{(2)}$, $d_j$; LM32 $\mathcal R(\cdot)$ for a
  general risk measure; LM33 HSR, $b$, $\hat V_{\mathrm{SR}}$, $v_t$, $\Psi$; LM34 $W^{\mathrm{net}}$,
  $W^{\mathrm{gross}}$, $G_{t,t'}$, $P^{\mathrm{adj}}_{t\mid t'}$, $S$, $\omega$, logit; LM35 $\mathrm{FX}_t$,
  $L_{\mathrm{ruin}}$, $t^{\mathrm{US}}$). B6: LM29 writes the borrowing spread in words (its $s$ clashed with $s_p$);
  no module writes a split ratio as a symbol ($s_i$ are standard deviations, AUTHORING §6): LM27's §4 writes the split
  day's return as $(P_t+D_t)/(P_{t-1}/4)-1$, and LM34's (34.2) compounds Volume I's total returns,
  $G_{t,t'}=(1+R_{t+1})(1+R_{t+2})\cdots(1+R_{t'})$, written out because LM34's $j$ is a rank (LM35 cites it); one
  TAIEX variance symbol,
  $\sigma^2_{\mathrm{mkt}}$ (LM27, LM30); LM35's adjusted price carries its retrieval date as LM34's
  $P^{\mathrm{adj}}_{t\mid t'}$.
- **C. Text conventions.** C1: the shared corrections are made (timing correlations, solver numbers, limits, 劣可加性,
  the cost notation). C2: frames (shared "E5's two frames"): LM27's case and X5 say "on the 2,362 joint dates"; LM28's
  X1 states its annualizer (each fund's own sessions per year). C3: X37 holds in every brief: LM27's X2 is thinned to
  weekly points plus every cited extreme. C4: LM35's hypothetical replays are the one mixed-sample exception. C5:
  solver tolerances as the shared decision now says; LM31 states its conic cross-check tolerance (1e-5). C6: lab data
  as the shared "Labs" decision now lists. C7: labels for near-twins (X22): every R1 volatility names its window
  (full-sample fixed weights 11.49% against out-of-sample 12.48%); "years" names its count (calendar days ÷ 365.25
  from the close before a sample's first return to its last close, as AUTHORING §8, everywhere; a count of sessions
  over $A$ says so); "month" names calendar or holding months; price index and total-return index are named
  beside every TAIEX number; every T5S change is a log change. C8: tags are cited by number ((27.5)–(27.6), (32.9),
  (34.2) …), and a brief lists only the modules that actually cite its tags. C9: prerequisites and leads both ways
  (X14: LM34's leads gain 46; LM33's leads gain 35 and LM35's prerequisites 33; LM32's lead 34 stands on the
  forward pointer). C10: every outcome and every sentence of the case box stays within 30 words (AUTHORING §1; X25
  lists LM29 1, 3, 6, 7; LM32 1, 2, 7; LM34 1–3), and a case box is cut into paragraphs of at most 80 words; wide
  tables are split (LM32 X6 and X8, LM30 X5, LM33 X1) so that no PDF page shrinks. C11: NEAR flags live in the
  anchors tables; a brief's text and the module print the rounded value without a flag mark. C12: an echo cites the
  owner's anchor ID where it is printed and prints at most the owner's precision, unless a computation shown beside it
  needs more.
- **D. Parameters fixed before any further result** (each brief's proposals accepted, with these settings): LM27 the
  full-sample $\hat\Sigma$ on the estimation frame, the 92 windows as a stability check, weekly $A=51.56$ (LM19's count of
  weeks with data); LM28 no realized Sharpe ratio for held portfolios; LM29 the $\theta$ grid and the constructed
  limits, the cost sweep's formulation named, $\lambda=2\mathbf y^{\top}\Sigma\mathbf y$ stated in A29-25, problem 11's
  "excess return after financing"; LM30 Black–Litterman with one relative view $K=(-1,1,0,0,0)$,
  $\Xi=K\hat\Sigma K^{\top}/T$ (so $c=T/(T+n_0)$) and $\delta=9.74$ from R2's window mean, the U28 window grid kept and
  labelled as chosen after the halves' result (an illustration, not evidence); LM31 the lab's trigger threshold 0.5,
  fixed now, HRP on E5 in the text, the CCD widget; LM32 ES (32.2), the backtest window of 1,231 days, block lengths by
  LM22's rule per rule, the stationary bootstrap in LM22's draw order (A32-20 and A32-37 recomputed), and A32-28's
  draw layout stated; LM33 $b=22$ (LM22's rule; the circular bootstrap uses the same length), Bartlett HAC with
  $\ell=7$, $\sqrt{T-1}$ as Bailey and López de Prado, $n=8$ as the headline with $n_{\mathrm{eff}}=2.07$ beside it,
  the last-block handling of the shared decision; LM34 the declared PBO grid, $\ell=75$ (LM22's rule on the
  differences from R1; 17 as a sensitivity), the grid median by `inverted_cdf` (10.96%, A34-27), problem 8's EWMA
  run through the window from $\bar\sigma^2$ as R8's (A34-16 recomputed), A34-12 "R1–R7" (R8's first purchase is
  smaller), A34-36 compared over the same span; LM35 the window rule and the first weights for 2008 and 2015, the
  checkpoint on the eight funds with R1, R3, R6 and R8 plus a one-way turnover limit of 20% per trade (the
  guidance's "turnover limits", X24), week keys by ISO year (A35-25, A35-34 recomputed), R8's 2025 exposure credited
  to the 2025-03-03 trade (A35-42 prints every trade into a window).
- **E. Departures from the spines** (X23), all accepted with their evidence: LM31's CCD widget and HRP on E5 in the
  text; LM32's tests are LM21's exact binomial tail and exact count, with Kupiec's and Christoffersen's likelihood
  ratios named in §7 and computed in the lab (see the second recomputation's decisions); LM34's X3 as gross against net log growth; LM35's ruin-line chart in place of higher caps; LM27's widget with
  three matrices; LM28's held-portfolio returns on the wealth frame.
- **F. Sources.** Before Stage 2 a fresh agent reads, in the original where it can be had, and records in SOURCES:
  Ledoit and Wolf (2008, JEF; read: its §3 has the script's scheme, so LM33 prints the bootstrap p-values beside
  the HAC test), Hansen (2005, JBES; read: LM34 prints the SPA p-value), Romano and Wolf (2005), Kupiec (1995) and
  Christoffersen (1998), Bailey and López de Prado (2014, eq. (9)), Tobin (1958), Choueifaty and Coignard (2008),
  DeMiguel, Garlappi and Uppal (2009; read: E3 prints their calibration, decisions on the first revision), Michaud and
  Michaud (2008), Bruder and Roncalli (2012),
  Moreira and Muir (2017) against the JF text, TWSE's 受益憑證買賣辦法 Art. 8, the Ministry of Finance's 財政統計通報
  No. 21 (read by the editor on 2026-10-24: it states the ETF rate 千分之1, and its table's 原型期貨 turnover and tax
  fit that rate, though no rate is printed per column; the futures-ETF tax stands) and TWSE's ETF rules page. A
  claim whose source is not read stays out of the text. The two general theorems LM29 could not source are dropped
  (LM29 proves optimality by exhibiting a KKT point).
- **G. Stage 4 leads** (merged, X list G3): lm01 +27, +32, +35; lm02 +35; lm03 +27; lm04 +29, +33, +34; lm05 +32; lm07
  +30, +31; lm08 +28, +29; lm09 +29, +30; lm10 +32; lm11 +29, +31, +34; lm12 +28, +29; lm14 +30; lm15 +30; lm18 +33; lm19 +27;
  lm20 +27, +28, +34; lm21 +32; lm22 +32; lm23 +28, +35; lm26 +35. Stage 4 rewordings: lm07.md:511–512, lm07.md:786, lm19.md:359 (LM33's wording), lm21.md:373
  (LM34's wording), the syllabus line of LM31 (LM31's wording), LM3's TQQQ example; optional: lm08.md:290, lm04.md's
  MDD sign (46–50, 510).

### Per module (beyond the cross-module decisions)

- **LM27.** Print every derived result so that it follows from the printed inputs (recompute: E1's 2.55% from the
  printed 0.0252, or print 0.02524; problem 6's stem gives ρ = 0.5521; KC §9 and E3 carry the digit their product
  needs; MRC, shares and $\beta s_p$ in E7 and E9 carry a digit or say "from unrounded inputs"); parts sum as printed
  (A27-26 to three decimals, A27-16, X8 and E10); "$A=2{,}362\times365.25/3{,}551$" as lm10.md:41 writes it; the 22
  negative 00679B windows as "22 of the 36 windows from May 2019 to April 2022, the last −0.0023%"; R1's and R2's
  $\mu_p$ get anchors; the widget's monthly and window matrices get anchors; A27-18 "to about $10^{-16}$"; X5's −0.11
  flagged; §4's timing uses trading sessions and frequencies, without SPY's numbers.
- **LM28.** The widget's first draw uses the data block's exact $\boldsymbol\mu$ and $\Sigma$ until a slider moves;
  A28-08 states its annualizer and prints the gap on a common $A$; Tobin is cited directly, as read in
  Cowles Foundation Discussion Paper No. 14 (1956), §3.6, with his limits (decisions on the first revision; F).
- **LM29.** As D; A29-21 names the formulation of the cost sweep ("a few 1e-6"); the two unsourced theorems go.
- **LM30.** Experiment 2: "about equal at 1.04 years (0.322, SE 0.008, against 0.327); well above at 2.07"; E4 credits
  fat tails, chiefly 0050's, on top of 00642U's large variance, and E6 drops 00646's kurtosis from the explanation;
  experiment 4's printed shares keep only the digits their SEs support, and every Monte Carlo mean prints its SE.
- **LM31.** A31-36 "over the 91 trades after the first purchase"; owner labels fixed (X10: first-window numbers are
  LM28's).
- **LM32.** As D and A1; §7 reads "cluster far less than HS; not rejected at the Bonferroni level".
- **LM33.** As D and F; X12's promise from LM31 (whether R6 and R7 differ in volatility beyond chance) is dropped
  from LM31, not added to LM33.
- **LM34.** As D; the stale "pending" notes go; the survivorship spread check allows a zero spread only right after an
  untraded row; A34-21 states integer split ratios if kept (the 33-fund cohort is not registered: keep the ID
  withdrawn); "about 0.1%" for `TaiwanStockPriceAdj` gets an anchor or goes; A34-17 states the month-end mean.
- **LM35.** As D; the case box drops the "also of a multi-day measure" claim (2020's five sessions were worse);
  A35-35's label is the full-over-conditional ratio, and the text says the tail widens the spread; stationarity
  residuals "below 1e-13" and complementary slackness below 1e-9; problem 4's distractor C is labelled as the FX applied the wrong way; E10, KC §8 and E6 wordings as
  the recomputation says; the "worst 5 sessions" start date is the close before the first return; the stale open items
  1–3 close.

### Decisions on the first revision (2026-10-24)

The source check (F) read twelve of its thirteen items; a second hunt read the thirteenth, Kupiec (1995) and
Christoffersen (1998) (next section). LM27–LM30 were revised before its report, so its consequences for them are decided here; LM31–LM35 were
revised with it.

- **Sources.** LM27 cites Choueifaty and Coignard (2008) for the diversification ratio's definition (eq. (1), p. 41),
  written in the book's notation (their $\Sigma$ is a vector of volatilities), and "the ratio exceeds 1" carries their
  condition (a long-only portfolio not equivalent to a single asset). LM28 cites Tobin directly, "read in Cowles
  Foundation Discussion Paper No. 14 (1956), §3.6", with its limits (riskless cash at zero yield, no borrowing,
  non-negativity not binding) and no page of the RES text; Sharpe's lecture is no longer the go-between. LM30's E3 may
  print DeMiguel, Garlappi and Uppal's US calibration (1/N's Sharpe ratio 0.12 a month against the tangency's 0.15;
  more than 3,000 months with 25 assets for the sample-based rule to beat 1/N, §4, pp. 1939–1941) and says their
  criterion is the certainty equivalent, not experiment 2's mean true Sharpe ratio; §7 attributes resampled averaging
  to Michaud (1998) "as described by Michaud and Michaud (2008)", paraphrased, with experiment 4 (averaging
  maximum-Sharpe portfolios) named a variant, and Michaud (1989) at the level of its abstract. LM29's sentence on
  cvxpy's rewriting cites Agrawal et al. (2018) only once the paper is read (Stage 2's source pass).
- **Weeks and months.** LM27's weekly and monthly returns drop the sample's first and last ISO week and calendar
  month, complete or not (2026-W41 holds four sessions and is dropped; the rule needs no holiday calendar).
- **Labs.** `make_lab_data.py` writes both E5 frames, the wealth frame with its traded flags (shared "Labs").
- **Leads.** LM28's tangency beta identity, $\beta_{i,\mathrm{tan}}=e_i/(\mu_{\mathrm{tan}}-r_f)$, puts $\mathbf
  w_{\mathrm{tan}}$ in the market's place in LM23's CAPM equation (lm23.md:285): prerequisite 23, and lm23 gains +28
  (G).
- **LM31.** A holding month's realized and target volatilities are both annualized with the estimation frame's $A$,
  so their ratio is the daily one (45.3% against 7.84%, 5.78), and the text says so.
- **LM33.** $b=22$ stands; the shared "Counting" decision now says which series the rule runs on for each kind of
  statistic. Andrews and Monahan (1992) is cited with the pages a fresh check confirms.
- **LM34.** Before §5 calls the survivorship funds futures ETFs, each fund's index is confirmed on its issuer's or
  TWSE's page, and the `TaiwanStockInfo` query that named them is recorded in SOURCES; TWSE's ETF overview page
  supports the roll-loss sentence (its word is 正價差), not "unsuitable for long holding".
- **LM35.** The checkpoint's turnover limit: the first purchase is exempt; above the limit a trade stops on the
  straight line $\mathbf w^{\mathrm{drift}}+(0.20/\mathrm{TO})(\mathbf f-\mathbf w^{\mathrm{drift}})$, with
  $\mathrm{TO}$ by (27.3); it runs in `data/lm35_numbers.py` on top of `vol5_rules.py`, as does R3's 30% cap. The
  spine's 27 sector indices go (0050's own 2007–2008 closes cover 2008); 00662's index is NASDAQ-100 (TWSE's fund
  page); DBO's index is DBIQ Optimum Yield Crude Oil Index Excess Return (Invesco's page, which states no roll rule).
- **Kept.** LM29's own count "7 of the 9" beside the echo of A30-22; the futures-ETF tax of 0.1% (the Ministry of
  Finance's notice and TWSE's ETF page; the statute stays the legal basis).
- **Across briefs.** Tag users, echoes, owners, prerequisites and leads are reconciled by one cross-check of the nine
  revised briefs (C8, C9).

### Decisions on the second recomputation and cross-check (2026-10-24)

Nine fresh recomputers reproduced all 185 added or changed anchors and audited every printed number; no wrong value
would be printed, and the findings are derived results that do not follow from the inputs printed beside them,
bounds that their values exceed, ambiguous definitions and wording. A fresh cross-check of the nine revised briefs
found no critical item (Y1–Y20). Each brief is revised once more: every finding of its recomputation is fixed as the
report proposes, every Y item naming it is applied, and the items the editor decided earlier are written into the
brief text. These choices settle the open alternatives:

- **Shared text.** B6 (no split-ratio symbol), A4's exceptions, A5's single owners, C7's year count, C10's 80-word
  paragraphs, C11 (NEAR flags) and C12 (echoes) are written above; AUTHORING §6 scopes $k$ (LM32) and $K$, $\mathbf b$
  (LM35), and §8 states where a sample's years start.
- **Tags and leads (Y1, Y13, Y14).** LM27–LM29 take the cross-check's tag-user table and rewrite their Leads
  sentences from it; speculative users go. LM35's leads drop 45 and 48 (no text points to them). lm07.md:786
  (Chopra and Ziemba's issue number) joins the Stage 4 list of the brief that cites the paper, LM30 if it does, else
  LM28.
- **Notation (Y6–Y10).** LM32 writes a loss as $-R$; LM30 writes residual variances with LM27's "res" subscript;
  LM33 writes "a moment of order a little above 4" for its $4+\delta$; LM28 outcome 1 reads "of $N$ assets".
- **LM27.** E5 says no daily–weekly gap reaches two weekly standard errors and prints the 00679B–00642U monthly gap
  without naming a cause (2.3 normal-theory standard errors, 2.0 plug-in; A27-11 prints it); E7's sentence becomes
  "only Euler's parts add up to the book's volatility, and only they price a switch", with the stand-alone and
  variance sums beside it.
- **LM28.** A weight vector or column printed at one decimal carries "rounded separately; sums to 100.1" (the
  PITFALLS rule allows saying so) rather than more digits.
- **LM29.** A29-31 and problem 11 state SCS's settings (eps 1e-9, 200,000 iterations); R4's Sharpe ratio uses the
  printed 18.85%; problem 11 prints $\mathbf f$ to two decimals.
- **LM30.** The span echoes A28-02 (2.05 calendar years from the close of 2017-02-10). Monte Carlo digits: the last
  printed digit sits at the standard error's first significant digit, everywhere, except a tie at that digit, which
  prints at the next coarser digit beside its exact count (A30-09; decisions on the fresh check) (experiment 4's shares then print
  one decimal, 3.8% to 35.2%). Bounds read "SEs 0.003", "SEs 0.008 to 0.001" and "the largest gap is 13.1 points".
- **LM31.** KC §7 is rewritten on the win and loss totals (A31-35 extended and relabelled "the EWMA's two largest
  QLIKE values"); A31-26 reads "the mean of R6's 92 target weights"; A31-19 and A31-30 are cited where the text uses
  them or withdrawn.
- **LM33.** $n_{\mathrm{eff}}$'s MinTRL prints 3.9 years (its second decimal is Monte Carlo noise); the other derived
  results carry the digit their reports give.
- **LM34.** The Executive Yuan draft is dropped (no source is recorded); problem 8's stem says daily simple returns,
  as R8 uses (26.2); A34-33 and A34-34 state their draw layout.
- **LM35.** A35-39's bound uses the unrounded distances, printed as 12.937 and 15.017; E8 prints each book's mean;
  A35-35 states its divisor 48.
- **Sources read by the second hunt** (two fresh agents; their consequences apply as they state them):
  - LM32: Kupiec (1995) read in FEDS 95-24 and Christoffersen (1998) in the author's final manuscript (7 July 1998).
    §7 names both at section level with those versions (no journal page or equation), Christoffersen's indicator
    relabelled to exceedances with the statistics unchanged; the lab computes $\mathrm{LR}_{\mathrm{uc}}$,
    $\mathrm{LR}_{\mathrm{ind}}$ and $\mathrm{LR}_{\mathrm{cc}}$ for the six models beside LM21's exact tests (new
    anchors); LM21's exact-count check stays the book's own.
  - LM29 cites Agrawal et al. (2018) for cvxpy's canonicalization (arXiv v2, abstract, §1.3 and §4); solver names and
    defaults rest on A29-22.
  - LM33: Lo (2002) read in the journal's layout (a copy posted by a student group; the abstract on the journal's own article
    page): its locations stand, written "Lo's IID formula (9)". Andrews and Monahan (1992) is pp. 953–966.
  - LM31: Maillard, Roncalli and Teïletche in their 2009 working paper, López de Prado in SSRN 2708678 (23 May 2016)
    and Harvey et al. (2018) in the journal reprint, with the hunt's wording corrections; no JPM page of the first two.
  - LM34: the futures-ETF tax cites the Ministry's ruling (shared "Costs"); the six survivorship funds are
    futures-trust ETFs on futures indices, three of them daily leveraged or inverse, and §5 says the gap mixes the
    product types; the roll-loss sentence keeps TWSE's "may" (可能).
  - LM35: BCBS d450 ("severe but plausible", Principle 4, p. 6) and Breuer et al. (2009, §2.1 p. 209, §2.3 p. 211) may
    be printed; the worst loss within $d\le k$ is Breuer et al.'s construction; Kupiec (1998) only "as described by
    Breuer et al."; DBO's roll rule stays out (its index methodology changed on 2025-11-10, after the replays); the
    2020 Lunar New Year closure is 2020-01-21 → 01-29 (TWSE's schedule, an archived copy).
- **Chinese terms** (a fresh 樂詞網 pass, 1,817 searches): LM33 單邊檢定 (as lm25.md:264); LM35 漲跌幅限制 (as the
  published modules); a Latin name before Chinese takes a space (Mahalanobis 距離, Euler 常數, as LM16), and
  studentized takes 統計學名詞's form where it lists one; LM31 指數加權移動平均模型 (as lm26.md:132); LM29's 對偶變量
  carries "dual variable" at first use (LM18's 對偶變數 is antithetic variates); LM32 排列檢定; LM31's 導讀 says once
  that its 風險預算 is a budget per asset (LM7's is a volatility limit); LM34's 導讀 glosses its 秩 as 名次; active
  constraint 有效限制 (LM7's Glossary); ruin is 權益歸零 in captions and §8; the Stage 4 change to lm07.md covers lines
  511–512.

### Decisions on the third revision (2026-10-25)

The nine briefs were revised to the decisions above and each revision was checked by a fresh verifier (with one
repair and re-check for LM30, LM31, LM34 and LM35). No critical or major item is left; the minor ones are fixed in a
last pass, with these answers to the verifiers' questions:

- **LM27.** E5's two gap sentences are scoped to the five pairs shown; the 00679B–00642U gap is "from the unrounded
  correlations"; the lab's file list adds R1's and R2's net wealth paths. The timing decision's note on the
  superseded first figures is dropped.
- **LM28.** Its A28-02 and A28-06 rows record the forms LM30's E2 prints under their IDs ($T/A=2.0745$, the
  volatilities to two decimals).
- **LM30.** $\tau$ stays 2.0745, its reason reworded (three decimals suffice for (20.2); the fourth keeps it off a
  rounding boundary); experiment 2's lengths read "years of sessions".
- **LM31.** The Leads sentence guessing at Volume VIII's modules goes.
- **LM32.** Christoffersen's indicator is relabelled in the lab only; §7 names the papers in words.
- **LM33.** A33-66 stays: the risk-free-rate sensitivity changes only the rate in the Sharpe ratio, the rules' paths
  keeping $r_f=1.5\%$ (R8 still borrows at 3.5%), and E2 says so. lm19.md:359's "as much as 65%" becomes a required Stage 4 rewording ("for a hedge
  fund in his illustrative example").
- **LM34.** (34.2) is written out (B6). The lab's extension trades every 12 month-end signals at the through case's
  targets ($n=68$, declared before it is run and after the grid's results were seen, which the declaration says);
  rebuilding (27.2) with cash, borrowing and costs from the shared files is LM34's own procedure under "Labs". Problem
  9 prints 4.14 as lm22.md:125 does. SOURCES records the `TaiwanStockInfo` query (2026-10-24, the six codes and names);
  no extract is registered.
- **LM35.** The short names of 0056, 00662 and 00720B print once SOURCES records them, which this pass does.
- **Listing markets** (a SOURCES verifier's finding, then a fresh read of TPEx's rules; shared "Costs" and "Limits and
  locks" now say which market's rule applies). LM27's timing names both markets: 0050, 00646, 00635U and 00642U on
  TWSE and 00679B on TPEx, both matching 09:00–13:30 with a closing call from 13:25 (TPEx 業務規則 Art. 40, applied to
  ETFs by its ETF rules' Art. 4 ¶2). LM34 prints TPEx's Art. 64 (applied to ETFs by its ETF rules' Art. 15 ¶1) beside
  TWSE's Art. 94 and quotes Art. 2-1's 上市及上櫃, and a universe of funds is "listed on TWSE or TPEx" (its six
  survivorship funds are all on TWSE). LM35 splits by market its limit paragraph, outcome 6 and its §7 row (TWSE Art. 8
  for 00646, 00662, 00635U and 00642U; TPEx Art. 7 for 00679B and 00720B), may cite 00720B's −11.25% of 2020-03-19 as
  consistent with no limit, and names 00720B 元大投資級公司債 (TPEx's short name). Since 2025-09-30 both markets let an
  issuer request a suspension during a long foreign closure (TWSE Arts. 5-1 and 5-2, TPEx Arts. 4-2 and 4-3), so a
  "no halt" statement rests on the frames. No number changes.

### Decisions on the fresh check of the whole of Stage 1 (2026-10-31)

The editor reran the nine anchor scripts (437 rows, each output equal to its Value cell) and sent the whole of Stage 1
to 23 fresh read-only agents. Nine recomputers rebuilt E5, the checkpoint funds and the through case from the
registered raw files and recomputed every anchor: every value reproduced at its printed digits; the digits that did
not reproduce were machine-precision residuals and one iteration count, now printed as bounds or dropped. Nine brief
checkers checked the mathematics, the decisions, the problems (blind-solved), the links and the citations; two
cross-module checks, a check of this decisions log and two SOURCES checks (the papers against their originals; the
Python, Taiwan, FinMind and 樂詞網 facts against official pages) completed the round. A fresh adversarial verifier per
module, and one for the shared items, merged the 431 findings into 379 items: 8 critical, 85 major and 274 minor
survive, 12 are refuted. Every surviving item is fixed with the verifier's exact edit except V5-01
(`make_lab_data.py`, a code change put to the owner below), the anchors it changes are recomputed by their scripts, and fresh agents
verified the fixes and recomputed every changed anchor (all reproduced; their minor findings are fixed). The critical items:

- **LM27.** With the other weights fixed, $\partial\mathrm{MRC}_i/\partial w_i=\sigma_i^2(1-\rho_{i,p}^2)/\sigma_p\ge0$;
  the brief had $\sigma_i^2/\sigma_p$, which holds only with $\sigma_p$ held fixed.
- **LM28.** The normalized $\Sigma^{-1}\mathbf e$ is the lowest-Sharpe fully invested portfolio only for
  $r_f>\mu_{\mathrm{mv}}$; at $r_f=\mu_{\mathrm{mv}}$ the normalization divides by zero.
- **LM29.** Problem 1's set drops the budget: $\{\mathbf w:\mathbf w^{\top}\Sigma\mathbf w\ge0.01\}$ holds $\mathbf w$
  and $-\mathbf w$ but not $\mathbf 0$, for every positive definite $\Sigma$. With the budget, the last window's set is
  the whole hyperplane (R3's variance 0.0102 exceeds the floor), which is convex.
- **LM30.** The pseudoinverse portfolio of a singular $\hat\Sigma$ is the minimum within the column space, not a
  minimum-variance portfolio (1.78% predicted against 0).
- **LM31.** CCD's update is defined for a zero budget (it sets that fund to 0, outside $\mathbf y>0$); Harvey et al.'s
  50 futures and forwards do not include credit.
- **LM34.** The TR23 daily scale and the Kelly walk-forward trade at the next close, as §2's protocol says; the
  same-close versions (14.93%, 21.75%) were E5's slip, and the day's own return is a different look-ahead.
- **LM35.** 00635U traded from 2015-04-15, before the 2015 window; see LM35 below.

The editor's choices where a verifier offered options (each the verifier's recommendation unless said):

- **(27.1)–(27.3).** $\mathbf w_{t-1}$ and $\mathbf w^{\mathrm{drift}}_t$ are each fund's value over wealth, summing to
  the book's exposure (1 when fully invested, $L_t$ for R8, 0 before the first purchase); AUTHORING §6 scopes the row.
  A new symbol would touch five modules for no gain in clarity.
- **Outcomes taught but not assessed** (LM27–LM33, LM35): each gains a problem part or a question inside the
  section's one knowledge check; no outcome is narrowed, since each clause is taught and promised by a published
  forward link or the spine.
- **LM27.** Choueifaty and Coignard's sentence under their eq. (1), p. 41, is their own wording, so §5 names the
  ratio, cites eq. (1) and gives no gloss; (27.7) needs none.
- **LM28.** Two-fund separation is practised in E4, after $\mathbf w_{\mathrm{tan}}$ exists ($t=0.905$), and assessed
  by problem 8(d); E8's "most of all the volatilities" is backed by its counterfactual: the test volatilities alone raise the minimum from 5.02% to 8.35% of 9.63%
  (A28-31).
- **LM29.** The bp columns' shown fourth decimals are flagged like the totals'; $r_f$ at 0% and 2% changes R4's
  long-only tangency and the financed exposures as A29-35 prints.
- **LM30.** R1's full-sample 11.49% (A27-13) prints in X1's note beside the out-of-sample 12.48%. A Monte Carlo share
  whose exact count sits at the standard error's digit prints at the next coarser digit beside the exact count:
  "2,115 of 10,000 (21%, SE 0.4 points)" (A30-09; Volume IV's LM23 precedent). This closes the brief's Open 1.
- **LM31.** The lab's GARCH variant averages (26.4) over the next 21 sessions, fixed before any lab result (a holding
  month's own length is known only from the calendar, and a closure can change it after the signal).
- **LM32.** Outcome 3 is [D], as problem 6 asks. Labels follow LM22: historical tails *Descriptive*, fitted tails and
  resamples *In-sample*, simulations *Model*. The lab refits LM26's two GARCH laws and runs the EWMA on
  `taiex_tr.csv`, as Lab 26 does; no derived forecast file is added.
- **LM33.** Four problem parts assess the second halves of outcomes 4–7 (A33-67). A source agent read Harvey and Liu
  in the Duke copy on 2026-10-31: "Method" and "Multiple Testing Framework" are the paper's section titles, and SOURCES
  records every title and what it holds.
- **LM34.** (34.3) states White's conditions as read on 2026-10-31 in the published article (Theorem 2.3, case (i):
  rules fixed in advance, no estimated parameters; a fixed number of rules as $T$ grows), and §6 says that Experiment
  10's 10,000 rules on 5,849 days lie outside that setting. The rules' window estimates are fixed functions of past
  data, so case (i) applies (the editor's reading, stated as such). The word plan is §1 450, §5 450, Summary 120 and
  Solutions 450 (5,470 in all). A34-38 prints the rules' growth at $r_f$ of 0% and 2%.
- **LM35.** Both hypothetical years hold the same four US proxies on one FX pairing: 2015 replays GLD for 00635U too,
  and the note says that 00635U traded from 15 April 2015 (0050 uses its own data in both years, as the spine asks).
  E7's 48-day tail correlation carries its standard error and a conclusion its 1.3 standard errors support.
  Checkpoint task (e) is replaced, so no cap-3 variant of R8 is introduced.
- **Questions for the owner** (technical; sent 2026-10-31): 0050's 2007–2008 files were registered on 2026-10-24 as
  an extension of B1, which approved one OHLC file over E5's span, and no approval of the wider range is recorded; and
  how `make_lab_data.py` should obtain the Volume V–VI derived files (B3). The brief's interim wording stands until he
  answers.
- **Refuted** (12): the five spines found stale (LM27, LM28, LM31, LM32, LM34) stay the first plan, their departures
  recorded as decision E; LM30's X3 note "years of sessions are sessions over $A$" stays (decision C7); three numbers
  of LM30 said to lack a tag are not first appearances; LM32's case box "2.3 to 3.6" follows from its printed inputs;
  no rule asks a brief for a page plan (the 36 pages are a Stage 2–3 gate); LM27's third-revision decisions are all
  applied.

## Stage 4 changes to earlier modules

Collected here as the briefs add them; applied at publication with the edition note.

- Leads: list G of "Editor's decisions on the briefs" (merged from the briefs' prerequisites); each brief's "Stage 4
  for earlier modules" names the files and lines.
- lm07.md:511–512: 切點組合 → 切點投資組合 (the Glossary's form, lm07.md:771).
- lm07.md:786: Chopra and Ziemba (1993) gains its issue number, 19(2): 6–11.
- lm19.md:359: Lo's "as much as 65%" is stated for a hedge fund in his illustrative example (Lo 2002, p. 36); the
  sentence says so (LM33's Sources).
- lm21.md:373: White (2000) and Romano–Wolf (2005) correct a search on the same data; testing rules fixed in advance on
  later data is the other half of LM34. Reword so the sentence says both.
- `src/syllabus.yaml`: LM31's line ("Euler risk contributions and risk-based allocation") becomes risk budgeting with
  LM27's contributions.
- LM3's TQQQ example (lm03.md:45, 464, 467, 469, 471; capability D). A re-fetch of QQQ's back-adjusted closes
  re-rounds them: the exact rebalancing effect $-0.31325$ (unrounded −0.3132492, 0.42 of a unit from the five-decimal
  boundary) became −0.31324, and the four-decimal −0.3132 sits 8e-7 from its own boundary. After the next distribution
  every adjusted level moves (the review's simulation of 300 rescaled re-fetches: ln(8.27/39.55) = −1.56493 changed
  in 299, 3 ln G = −1.18252 and the residual −0.0692 in 277, TQQQ's −79.09% in 205, QQQ's dividends 0.0074 in 168,
  the residual against unadjusted closes −0.047 in 129, "6.7% of value" in 118, T3 −0.3107 in 67, QQQ's −32.58% in
  31; RV and √RV in none), and `data/lm03_numbers.py:313` asserts the levels (39.55, 8.27) exactly, so `build.sh
  --data` would fail on a fresh checkout. Fix in LM3: quote levels with their retrieval date (2026-10-10) or from
  unadjusted closes, print each derived value only to digits a cent per value cannot move, replace the exact-level
  assert by a ratio check, and align Lab 3 Part 6.
- `build/make_lab04.py`'s walk-forward extension sets each month's leverage from data through the month-end close and
  holds it from that close, E5's slip; shift it one session (trade at the next close), as LM34's lab does, and say
  so in the scaffold (it prints no number in the module).
- Each brief's "Stage 4 for earlier modules".

## Spines

Each spine gives the module's question, its draft prerequisites, the forward links it must honour (from the survey;
the brief rechecks each line), what it owns and leaves, its data, a candidate case, exhibits and widget, and what the
brief must settle. Numbers marked "explored" are the survey's first look; only anchors may be printed.

### Spine of LM27 Portfolio Return and Risk

**Question.** A reader holds LM7's two funds and adds three more. What is the portfolio's return when the weights
drift, what does rebalancing cost, and which fund carries the risk? Equal weights in E5 look diversified, yet one
fund can carry far more than a fifth of the variance (explored: 00642U about 46% of R1's risk on the full-sample
$\hat\Sigma$): LM27 finds out which, from $\Sigma$ alone.

**Prereq (draft).** LM7 ((7.1)–(7.3), the two-asset prototype), LM8 ((8.2)–(8.4), (8.11)–(8.13)), LM9, LM10
((10.2), (10.4), (10.6), (10.9)), LM11 ((11.2), (11.4)), LM12 ((12.3)), LM16 ((16.2), (16.4)), LM19, LM23 ((23.1),
the market model).

**Forward links to honour.** lm07.md:57 (matrix notation for $N$ assets); lm09.md:444 (cap weights drift with prices;
the 0.50 → 0.858 drift of a 50/50 sector mix, lm09.md:436–438); lm10.md:225 and 425 (splitting $s_p^2$ into shares,
"judging which split is meaningful"; $2\hat\Sigma\mathbf w$ is a rate of change, not a share); lm16.md:225; lm23.md:416
(factor risk as bookkeeping). Leads already listing 27: LM7, 8, 9, 10, 11, 12, 16, 23.

**Owns.** $R_p=\mathbf w^{\top}\mathbf R$ against the drifted weights of a buy-and-hold book; the wealth recursion with
trades, turnover $\mathrm{TO}_t$ and costs (citing the cost model); E5's two frames and why they differ; simple
returns aggregate across assets, log returns across time; $\mu_p$, $\sigma_p^2=\mathbf w^{\top}\Sigma\mathbf w$ and
annualization with $A$; $\operatorname{Cov}(R_i,R_p)=(\Sigma\mathbf w)_i$ and $\beta_{i,p}$; marginal and component
risk contributions and Euler's identity $\sum_i\mathrm{RC}_i=\sigma_p$; when a contribution is negative and what that
means; factor decomposition of $\sigma_p^2$ with market betas (systematic and residual parts); diversification
measured ($\sum_i w_i\sigma_i/\sigma_p$, with LM8's (8.11)); R1 and R2 defined; the asynchronous closes of E5 (daily,
weekly, monthly correlations). Net and gross exposure are LM8's, cited.

**Leaves.** Choosing weights → LM28; constraints and costs in the objective → LM29; the error in $\hat\Sigma$ → LM30;
contributions as targets → LM31; the rules' net results → LM34; the cost sources → LM34.

**Data.** E5 (main case; both frames); U28 for the factor decomposition (the TAIEX price index as the factor, price
indices said so). LM7's pair quoted as printed.

**Candidate exhibits.** Weights of a buy-and-hold E5 book drifting from 1/N; weight share against risk share for R1
and R2 (stacked bars if approved, else grouped); daily, weekly and monthly correlations of 0050 with the four
foreign funds. **Widget:** a risk-budget explorer (four weight sliders, the fifth fund taking the rest, with a
warning when it goes negative; bars of $\mathrm{RC}_i$ and $\sigma_p$ from an embedded $\hat\Sigma$).

**Hygiene.** *Descriptive* (full-sample $\hat\Sigma$); the drift and rebalancing paths are *Descriptive* histories,
not tests.

**Brief settles.** The sample window for the full-sample $\hat\Sigma$ (all of E5, or the through case's first
window); how far the factor decomposition goes before LM30; the turnover and cost of R1's monthly rebalancing as the
running cost example (equity-ETF tax only, until the futures-ETF tax is confirmed).

### Spine of LM28 Mean–Variance Optimization

**Question.** Given $\boldsymbol\mu$ and $\Sigma$, which portfolio has the least variance for a target mean, and
which the best Sharpe ratio? On E5's first window the answers are exact; LM28 then tests them on the following years,
as LM7 did with two funds (predicted 9.22%, realized 12.44%; lm07.md:23, 38–40).

**Prereq (draft).** LM7 ((7.4)–(7.6), (7.10)–(7.12), the Lagrangian and its signs), LM8, LM9 ((9.4), (9.5)), LM10
((10.4), (10.8)), LM11 ((11.4), (11.8)), LM16 ((16.4)), LM27.

**Forward links to honour.** lm07.md:457 (tangency: the highest Sharpe ratio, where the line from $r_f$ touches the
risky set); lm10.md:446 (the least-variance portfolio); lm10.md:449 (PSD ⇔ convex, "the foundation of LM28 and
LM29"); lm11.md:419 ($\hat\Sigma\mathbf x=\mathbf 1$ rescaled is LM28's minimum-variance portfolio). Leads already
listing 28: LM7, 9, 10, 11, 16.

**Owns.** The N-asset Lagrangian with LM7's signs; the global minimum-variance portfolio
$\mathbf w^{\mathrm{mv}}=\Sigma^{-1}\mathbf 1/(\mathbf 1^{\top}\Sigma^{-1}\mathbf 1)$ and $\sigma^2_{\min}$; the
frontier as a parabola in $(\sigma_p^2,\mu_p)$, a hyperbola in $(\sigma_p,\mu_p)$, written without Merton's scalars;
two-fund separation; the tangency portfolio $\mathbf w^{\mathrm{tan}}\propto\Sigma^{-1}\mathbf e$ and the capital
market line with $r_f=1.5\%$; risk aversion $\delta$ in the exposure form with a riskless asset, and LM7's
two-asset Kelly result cited; conditions ($\Sigma$ positive definite, $\boldsymbol\mu$ not proportional to
$\mathbf 1$); sensitivity of $\mathbf w^{\mathrm{tan}}$ to $\boldsymbol\mu$ (a small change in one mean, a large change
in weights); the in-sample frontier of the first window against the realized risk of its unconstrained portfolios
held to the end (one split, LM7's pattern, *Out-of-sample*), as the bridge to LM29 and LM30.

**Leaves.** Long-only and other constraints, and the through-case forms of R3 and R4 → LM29; estimation error and its
repairs → LM30; leverage and Kelly → LM43; the statistics of the realized Sharpe ratio → LM33.

**Data.** E5's estimation frame: the through case's first window for the in-sample frontier, the following years for
realized risk; U28 for the minimum-variance portfolio at large $N$ (covariance only).

**Candidate exhibits.** The E5 frontier with the five funds, $\mathbf w^{\mathrm{mv}}$, $\mathbf w^{\mathrm{tan}}$
and the capital market line; tangency weights against a 1-point change in one fund's mean; predicted against
realized volatility of the first window's portfolios. **Widget:** a frontier explorer (sliders for two funds' means
and one correlation; the frontier, tangency weights and CML in closed form, with a 5×5 solve and a
positive-definiteness check).

**Hygiene.** *In-sample* frontier; the single split *Out-of-sample* (fixed in advance), counted in the note.

**Brief settles.** The derivation route (Lagrangian in matrix form, as LM7); which sensitivity example; how the
unconstrained solutions are labelled against the through case's long-only R3 and R4.

### Spine of LM29 Convex Optimization in Practice

**Question.** LM28's tangency portfolio shorts a fund and levers another. A reader can do neither cheaply. How do
long-only, leverage, concentration and turnover limits change the answer, how does a solver find it, and how can the
reader tell that the solver's answer is right?

**Prereq (draft).** LM4 (convexity in one variable), LM7 ((7.13), KKT stated without proof, the sign convention),
LM9, LM10 ((10.1), (10.9), (10.10): quadratic convex ⇔ PSD), LM11 ((11.9)), LM12 ((12.6)), LM27, LM28.

**Forward links to honour.** lm07.md:268 ("LM29 develops convexity"); lm07.md:522 (KKT "applied to larger portfolios");
lm10.md:446 (the argument for functions that are not quadratic); lm10.md:449. Leads already listing 29: LM7, LM10.

**Owns.** Convex sets and functions in $\mathbb R^N$ (definitions, the chord and gradient tests, sums and maxima,
why a local minimum is global); quadratic programs in standard form, linear programs in one paragraph; KKT conditions
for inequality constraints, derived for the long-only minimum-variance problem, sufficiency for convex problems,
necessity under a constraint qualification stated; the multipliers as shadow prices (how much a limit costs in
variance); active sets and why long-only weights hit zero; R3 and R4 in their through-case (long-only) form; one cap
and one cost-penalty example in the text (costs as a term in the objective); modelling in cvxpy, solvers, scaling,
tolerances and the solver-output rule; checking an answer (KKT residuals, a second solver, a closed form where one
exists). The wealth recursion is LM27's, cited.

**Leaves.** Robust and shrunk inputs → LM30; risk-parity formulations → LM31; expected-shortfall minimization → a
problem in LM32; duality beyond shadow prices is out of scope. To the lab and problems (density): leverage and
turnover-limit versions, the OSQP-against-CLARABEL comparison, infeasible and unbounded problems (also the pitfall).

**Data.** E5's estimation frame (R3, R4 and their constrained versions on the through case's windows).

**Candidate exhibits.** Unconstrained, long-only and capped weights of the maximum-Sharpe portfolio side by side; the
efficient frontier with and without long-only limits; the multiplier of the long-only constraint for each fund;
turnover and cost against the cost-penalty weight. **Widget:** a two-fund-plus-cash active-set explorer (a slider for
the cap; the KKT conditions shown holding or failing, closed form).

**Hygiene.** *In-sample* optimization; out-of-sample results of R3 and R4 are LM30's, LM33's and LM34's, cited by
pointer.

**Brief settles.** How much convex analysis is derived against stated; the cost-penalty example; which solver
comparison is printed in the text against the lab.

### Spine of LM30 Estimation Error and Robust Portfolios

**Question.** Why does the plug-in optimum lose to equal weights so often? LM30 measures how much of the problem
comes from errors in means and how much from errors in $\hat\Sigma$, and tests the repairs: shrink the covariance,
constrain the weights, start from a reference portfolio (Black–Litterman), and average over resamples.

**Prereq (draft).** LM7 (Chopra–Ziemba, lm07.md:509), LM10 ((10.2), (10.3), (10.6), (10.7)), LM11 ((11.4)–(11.9),
condition numbers), LM12 ((12.5)–(12.7)), LM16 ((16.4)), LM18 ((18.4), the simulated-covariance error), LM20 ((20.1),
(20.2), (20.5)), LM22, LM23 ((23.1), (23.9)), LM24 ((24.1), (24.3), (24.4)), LM26 ((26.2), (26.8)), LM28, LM29.

**Forward links to honour.** lm07.md:509 (estimation error and shrinkage "take up the repair"); lm10.md:55;
lm10.md:386 (the nearest valid correlation matrix: Rousseeuw–Molenberghs 1993, Higham 2002b); lm11.md:480 and 486
(pulling small eigenvalues up lowers $\kappa$; "covariance shrinkage, the subject of LM30"); lm16.md:225; lm22.md:390
(resampled portfolios); lm23.md:416 (factor risk's estimation); lm24.md:44 (shrinking a covariance matrix "follows the
same idea"); lm24.md:291 (Jorion 1986 "into portfolio choice": one sentence on his Bayes–Stein means); lm26.md:409;
`build/make_lab07.py:601` (the monthly re-estimation exercise: "LM30 returns to this question with shrinkage
estimators"). Leads already listing 30: LM10, 11, 12, 16, 18, 20, 22, 23, 24, 26 (LM7 gains one at Stage 4).

**Owns.** The error in plug-in weights (a simulation from a known $\Sigma$ and $\boldsymbol\mu$: weights scatter,
mostly from $\hat{\boldsymbol\mu}$); the 1/N benchmark and DeMiguel, Garlappi and Uppal's result, stated with its
conditions; covariance shrinkage toward $\bar\lambda I$ (Ledoit and Wolf 2004: the oracle intensity derived, the
estimated $c$ and its consistency stated, computed by hand and by scikit-learn), with its effect on eigenvalues and
$\kappa$ (U28); constraints as implicit shrinkage (Jagannathan and Ma 2003, Proposition 1 stated); Black–Litterman
with R2 as the reference ($\mathbf e_{\mathrm{eq}}=\delta\Sigma\mathbf w_{\mathrm{ref}}$, one view on excess returns,
the posterior mean as LM24's precision-weighted average); Jorion's Bayes–Stein means in one sentence; the realized
out-of-sample volatility of R1, R3 and R5, and of sample against shrunk minimum variance on U28's halves.

**Leaves.** Shrinkage of means beyond LM24's → LM24 (cited); covariance forecasting by EWMA → LM31; the significance
of out-of-sample differences → LM33; net results of every rule → LM34; Kelly under uncertainty → LM45. To the lab and
problems (density): the repair of a non-PSD correlation matrix (one paragraph in the text, the clipping in the lab;
honours lm10.md:386), resampled efficiency (one paragraph, the bootstrap in the lab; honours lm22.md:390), the
make_lab07 exercise, the depth of the Ledoit–Wolf derivation (a Deep Dive).

**Data.** E5 (through case), U28 (large $N$, covariance only; halves as LM11), simulations under the seed rule.

**Candidate exhibits.** Scatter of plug-in tangency weights across simulated samples; eigenvalue spectrum of U28's
$\hat\Sigma$ and of the shrunk matrix (log $y$); out-of-sample volatility of sample and shrunk minimum-variance
portfolios on U28; Black–Litterman weights as the view's confidence rises. **Widget:** a shrinkage slider ($c$ from 0
to 1: the spectrum, $\kappa$ and minimum-variance weights from an embedded grid).

**Hygiene.** Simulations *Model*; U28's halves *Out-of-sample* (fixed in advance); E5's rules *Out-of-sample*;
Black–Litterman and resampled weights *In-sample* illustrations, not in the through case.

**Brief settles.** The Black–Litterman view and its confidence; whether the make_lab07 exercise is answered in the
lab only; the simulation's design (which $\Sigma$, $\boldsymbol\mu$ and $T$).

### Spine of LM31 Risk Parity, HRP and Volatility Targeting

**Question.** If means cannot be estimated, allocate by risk alone. LM31 gives each fund an equal share of risk (ERC),
builds a portfolio from a tree of correlations (HRP), and scales the whole book by a volatility forecast (R8), then
asks what each choice costs in turnover and leverage.

**Prereq (draft).** LM7 (lm07.md:94, the marginal variance), LM8 (lm08.md:290, the per-date distance), LM10 ((10.4),
(10.8)), LM11 ((11.3)), LM26 ((26.2)–(26.4), (26.8)), LM27 (risk contributions), LM28, LM29.

**Forward links to honour.** lm07.md:94 ("a fact LM31 builds into risk budgeting"); lm08.md:290 ("LM31 groups assets
by this distance"); lm10.md:225, 425; lm16.md:225; lm26.md:183 ("LM31 scales a position by such a forecast");
lm26.md:409. Leads already listing 31: LM8, 10, 16, 26 (LM7 gains one at Stage 4).

**Owns.** Inverse-volatility weights (ERC when correlations are equal); ERC and risk budgets: the conditions
$\mathrm{RC}_i=b_i\sigma_p$, existence and uniqueness for long-only budgets (Maillard, Roncalli and Teïletche 2010
for equal budgets; a sourced reference for unequal ones), solved by a Newton or fixed-point iteration and checked with
cvxpy's convex form; HRP as published (R7's steps; the factor 2 to LM8's distance; some implementations link on the
distance matrix directly, so trees can differ); R8: the EWMA forecast, the exposure path, the cap, cash and financing,
and the turnover it adds; periodic rebalancing against a risk trigger (guidance; the trigger as an in-sample
illustration); the EWMA covariance matrix in one paragraph; the evidence on volatility management (Moreira and Muir
2017) stated with its sample. R6–R8's weights, risk shares, exposure and realized volatility are LM31's numbers.

**Leaves.** Kelly-type sizing → Volume VIII; tail risk of the scaled book → LM32; net results → LM34; crash behaviour
of a levered book → LM35. To the lab (density): HRP on E5 and the risk-triggered variant.

**Data.** E5 (R6, R7, R8); U28 for HRP's tree in the text (28 sectors; price indices, covariance only).

**Candidate exhibits.** Risk shares of R1, R6 and R7 (stacked bars if approved); U28's correlation heatmap in HRP order
with its dendrogram; R8's exposure path and realized volatility against its window volatility. **Widget:** ERC for
three funds (sliders for volatilities and one correlation; weights and risk shares by fixed-point iteration, tested
against Python).

**Hygiene.** In-sample trees and weights *Descriptive*; R6–R8 in the through case *Out-of-sample*.

**Brief settles.** The ERC solution method shown by hand; the source for unequal budgets; how R8's realized
volatility is judged (against its window volatility, with the number of months).

### Spine of LM32 VaR, Expected Shortfall and Drawdown

**Question.** How much can the through case's portfolios lose on a bad day, a bad month, and from their peak? On
2025-04-07 the TAIEX fell 9.70% (TR23's worst day; it followed four non-trading days). LM32 asks which VaR model
would have seen it coming, why expected shortfall answers a better question than VaR, and why drawdowns are path
statistics that one-day measures cannot give.

**Prereq (draft).** LM1 ((1.17), drawdown), LM5 ((5.11)), LM10 ((10.4)), LM12, LM14, LM15 ((15.6), (15.10), (15.11),
(15.13), the $t$ fit), LM16 ((16.4), (16.7)), LM18 ((18.1)–(18.3), (18.5)–(18.7)), LM19, LM20 ((20.10), Hill), LM26
((26.1)–(26.4), (26.8), (26.9)), LM27–LM31 (the rules; LM29 for the ES problem).

**Forward links to honour.** lm05.md:369 (tail measures that need fewer moments); lm05.md:509 and 785 (−(5.11) at the
VaR level is LM32's expected shortfall; 預期短缺); lm14.md:122; lm15.md:194 (the 1% quantile as one-day 99% VaR);
lm15.md:469; lm18.md:300 (the variance-reduction estimators applied to VaR); lm19.md:138 (drawdown as a path
statistic); lm20.md:276 (the standard error of a sample quantile); lm20.md:449 (VaR from a tail model; no extreme
value theory beyond Hill); lm26.md:183 (a variance forecast into a VaR). Leads already listing 32: LM12, 14, 15, 16,
18, 19, 20, 26 (LM5 gains one at Stage 4).

**Owns.** VaR and ES defined from the return quantile, with the horizon $m$ and the level $u$; historical, normal and
Student-$t$ VaR; filtered VaR with EWMA and GARCH forecasts (LM26); the standard error of a quantile estimate;
coherence, subadditivity and a constructed example where VaR fails it; ES at 97.5% against VaR at 99% (the Basel FRTB
choice, stated with its document); backtesting VaR: exceedance counts, Kupiec's test and the Basel traffic light
(1996), Christoffersen's independence test stated; drawdown $\mathrm{DD}_t$, maximum drawdown and its duration,
drawdown from initial wealth $\mathrm{DD}^0_t$; the drawdown distribution by block bootstrap (Brownian-motion results
stated without proof, with their model). The rules' VaR, ES and drawdowns are LM32's numbers.

**Leaves.** Sharpe-ratio statistics → LM33; drawdown probabilities under a model and drawdown control → LM44 (LM32's
drawdown statistics are empirical); jumps → LM39; scenario losses without probabilities → LM35. To the lab and
problems (density): Hill-tail VaR, importance-sampling Monte Carlo VaR (honours lm18.md:300 with a worked problem),
Christoffersen's details, intraday drawdowns from T5S (per-day statistics), Rockafellar–Uryasev ES minimization (a
problem citing LM29).

**Data.** TR23 (one-day VaR models and their backtests, 2003–2026); E5's wealth frame for the rules R1–R8 (VaR, ES and
drawdowns over the out-of-sample period); T5S per-day statistics in the lab.

**Candidate exhibits.** TR23's returns with rolling 99% VaR from three models and the exceedances marked; a loss
histogram with VaR and ES lines; Kupiec results by model with the traffic-light zones; the underwater chart of R1, R3,
R6 and R8. **Widget:** a VaR level slider (historical, normal and $t$ VaR and ES of the selected rule from embedded
sorted returns and an embedded grid of $t$ quantiles).

**Hygiene.** Rolling one-day VaR forecasts *Out-of-sample* (estimated on data before each day); full-sample tails
*In-sample*; simulations *Model*.

**Brief settles.** The historical ES estimator (shared decision); the rolling window of the VaR backtest; the
drawdown bootstrap's block length.

### Spine of LM33 The Statistics of the Sharpe Ratio

**Question.** Of the eight rules, one has the highest Sharpe ratio over the out-of-sample years. Is it better, or
lucky? LM33 first does Volume IV's checkpoint on the through case (each rule's mean, volatility and Sharpe ratio with
their uncertainty), then measures the Sharpe ratio's precision when returns are fat-tailed and dependent, asks how
long a track record must be before its Sharpe ratio is believable, and deflates the winner for the number of rules
tried.

**Prereq (draft).** LM4, LM16 ((16.3)), LM19 ((19.7), (19.9)), LM20 ((20.2), (20.8), (20.9)), LM21 ((21.1), (21.3),
(21.4), (21.6), (21.9)), LM22 ((22.1), (22.4), circular blocks), LM23 ((23.7)), LM25 ((25.4), (25.6)), LM27–LM31 (the
rules).

**Forward links to honour.** lm04.md:120 ("LM33 studies its estimation"); lm04.md:563 (backtests overstate Sharpe
ratios: size from a haircut, then a fraction of Kelly); lm19.md:359 (Lo 2002; the √12 rule's conditions);
lm20.md:407; lm21.md:373 (deflation for the number of trials); lm22.md:141 (dependent-return standard errors, PSR,
DSR, Ledoit–Wolf's 2008 test); lm23.md:266 (the long-run variance applied to a Sharpe ratio); lm24.md:376 (haircuts);
research-hygiene.md:7 (the 中文 box), 29 and 62. Leads already listing 33: LM16, 19, 20, 21, 22, 23, 24, 25 (LM4 gains
one at Stage 4).

**Owns.** $\widehat{\mathrm{SR}}$'s standard error under iid returns with skewness and kurtosis ((20.9) applied, raw
kurtosis), and under dependence (Lo 2002 with HAC (23.7)); annualization when returns are autocorrelated (Lo's
correction, applied with (19.9)); the probabilistic Sharpe ratio and the minimum track record length (Bailey and
López de Prado 2012), against (21.4); the deflated Sharpe ratio for $n$ trials (Bailey and López de Prado 2014), with
(21.9)'s expected maximum and an effective number of trials; the difference of two Sharpe ratios (Ledoit and Wolf
2008, studentized block bootstrap); haircuts (Harvey and Liu 2015) and what they imply for sizing (pointer to LM45).
The rules' Sharpe ratios, intervals and tests are LM33's numbers.

**Leaves.** The search across rules on later data and PBO → LM34; sizing from an uncertain Sharpe ratio → LM45.

**Data.** E5's wealth frame for R1–R8 (out-of-sample period, daily and monthly); TR23 (the long record: 0.81 ± 0.21
annual, LM20's numbers quoted as printed).

**Candidate exhibits.** The eight rules' Sharpe ratios with iid and HAC intervals (forest plot); PSR against track
record length for three true Sharpe ratios; the deflated benchmark as $n$ grows. **Widget:** a minimum-track-record
calculator (sliders for the Sharpe ratio, skewness, kurtosis and $n$; closed forms with `Book.dist`).

**Hygiene.** The rules' Sharpe ratios *Out-of-sample*; the deflation counts $n=8$ (the through case), names it and
states the independence it assumes.

**Brief settles.** The HAC bandwidth (LM23's rule); $T$ against $T-1$ in PSR (the book's (20.9) uses $T$; say how much
the other changes); the effective number of trials.

### Spine of LM34 Backtesting Without Fooling Yourself

**Question.** A backtest is an experiment with many hidden choices. LM34 runs the through case's eight rules as an
honest walk-forward test with Taiwan's official costs, shows on real data how look-ahead and survivorship inflate
results, corrects a search over many rules on the same data, and estimates the probability that the best in-sample
configuration is overfit.

**Prereq (draft).** LM4 (lm04.md:209), LM11 (lm11.md:406), LM17, LM18, LM21 ((21.6), (21.8), (21.9), Experiment 10),
LM22 ((22.2), (22.4)), LM23, LM26 ((26.1), (26.8), (26.9)), LM27–LM31 (the rules), LM33.

**Forward links to honour.** lm04.md:209 (a grid search returns "the highest bump", largely noise); lm04.md:563;
lm11.md:406; the hygiene notes of lm17.md:51, lm18.md:50 and 389, lm21.md:57, lm22.md:57, lm25.md:54, lm26.md:54
("Nothing is tested on later data"); lm21.md:373 (reworded at Stage 4); lm22.md:144 (a walk-forward test of the Kelly
fraction is LM34's) and `make_lab04.py:642` (month-end Kelly leverage walked forward): a lab part on TR23 tests a
trailing-window Kelly fraction walk-forward (Kelly sizing proper stays Volume VIII's); lm22.md:352 (the reality
check); lm23.md:369 (data snooping); research-hygiene.md:7, 35, 62 ("LM34 gives Taiwan's official rates";
look-ahead, survivorship, costs, walk-forward, PBO); the labs' `make_lab23.py:901`, `make_lab25.py:836`,
`make_lab26.py:1115`. Leads already listing 34: LM17, 18, 21, 22, 23, 25, 26 (LM4 and LM11 gain one at Stage 4).

**Owns.** The walk-forward protocol (the through case's windows, dates, timing and costs) applied to R1–R8 with the
cost model and its official sources; net wealth, log growth, turnover and costs, gross against net; look-ahead shown
on data (one case in the text: adjusted prices rebuilt backward; two in problems: a close used before 13:30, a
full-sample parameter); survivorship shown on delisted Taiwan ETFs; correcting a search on the same data (White's
reality check by the stationary bootstrap on Experiment 10's 10,000 rules; Romano–Wolf and Hansen's SPA stated); PBO
by combinatorially symmetric cross-validation on a declared grid of rule configurations, its logit distribution and
the performance degradation; the grid's "highest bump" (lm04.md:209).

**Leaves.** Sharpe-ratio intervals and deflation → LM33 (cited); stress replays → LM35; Kelly sizing of a backtested
strategy → Volume VIII. To the lab (density): Romano–Wolf, the Kelly walk-forward.

**Data.** E5's wealth frame (through case); TR23 and Experiment 10 (LM21's seed); delisted ETFs (capability B4).

**Candidate exhibits.** Net wealth of R1–R8 (four named and the rest muted, or two panels); gross against net
Sharpe ratio by rule; reality-check $p$-value against the naive best $t$; the PBO logit histogram. **Widget:** a
backtest-overfitting simulator (strategies with zero true Sharpe; slider for the number tried; CSCV logits recomputed
with `Book.rng`).

**Hygiene.** The walk-forward results *Out-of-sample* (fixed in advance on 2026-10-24); the grid search *In-sample* by
design and declared after the fact; the simulator *Model*.

**Brief settles.** The PBO grid (rules × windows × rebalancing frequencies) and its count; which delisted ETFs; the
futures-ETF tax (verified in Stage 1 before any number uses it).

### Spine of LM35 Stress Testing

**Question.** What would the through case's portfolios have lost in the five scenarios ROADMAP names (2008, 2015,
2020, 2024-08-05, 2025-04-07), and what could they lose in one that has not happened? LM35 replays the scenarios,
builds hypothetical shocks, searches for the smallest shock that breaks a loss limit, and shows what leverage, price
limits and holidays do to a "one-day" loss.

**Prereq (draft).** LM1, LM8 ((8.2), (8.13)), LM16 (the Mahalanobis distance, lm16.md:322), LM23 ((23.1), betas),
LM26, LM27–LM31 (the rules; R8's leverage), LM32.

**Forward links to honour.** None in published text (survey). The plans' promises: (8.2) and (8.13) for shocks
(`plans/vol-2.md:158`, 259–262); LM16's dependence results (`plans/vol-3.md:1543`; the brief rechecks which tag);
ROADMAP's Stress row (no probabilities; jumps are LM39's). Leads already listing 35: LM8, LM16.

**Owns.** Historical replay: 2020, 2024-08-05 and 2025-04-07 on the rules' holdings at the event's start (the rules
hold E5 from 2019-03); 2008 and 2015 replayed on a stated set of weights (the rules' first weights, or R2), on the
funds that existed and on proxies where they did not (capability B5), labelled *hypothetical*; hypothetical shocks (a
factor shock through betas, a correlation break, a gap); reverse stress testing (the smallest shock in Mahalanobis
distance that reaches a loss, a distance, not a probability); leverage and ruin ($1+L R\le0$; 00631L's −19.995% on
2025-04-07; wealth ≤ 0 reported); limit locks (sales at the limit only; the next open's loss); returns that span
holidays; the overnight gap from T5S per-day statistics; funding and margin only with dated official tables; the four
failure forms compared on the same rules (guidance). The rules' scenario losses are LM35's numbers. The lab's final
part is the batch's checkpoint.

**Leaves.** Probabilities of extreme moves and jump models → LM39; margin regimes and leverage instruments → LM46;
drawdown control → LM44; the capstone's own data → LM48.

**Data.** E5's wealth frame and the rules' holdings; TR23 and 0050's own 2007–2008 closes for 2008; T5S
per-day statistics; TX23 on limit days; US proxies if approved; the checkpoint universe (0056, 00662, 00720B with
E5's funds as the brief decides).

**Candidate exhibits.** Scenario losses of four rules across the five scenarios (bars); the 2025-04-07 gap and the
day's low from T5S statistics; the reverse-stress shock vector; R8 at higher caps against the ruin line (replaced by decision E:
X7's ruin line of R6's book scaled by $L$, with R8's cap 1.5 and its largest uncapped ratio). **Widget:** a
scenario builder (sliders for shocks to the five funds; the portfolio loss for the selected rule's weights; closed
form).

**Hygiene.** Replays of the rules' own holdings *Descriptive* (historical paths); replays on chosen weights and proxies
*hypothetical*; hand-built shocks *hypothetical*; no probability is attached to any scenario.

**Brief settles.** Each scenario's window (peak to trough, the worst day, the worst 5 and 20 days) from the anchors;
the weights replayed in 2008 and 2015; the proxy rule; the official price-limit rule for domestic and cross-border
ETFs; the checkpoint's universe and its rubric.

<!-- briefs LM27-LM31 below: assembled from the drafters' files; edit them through the revision rounds -->

## LM27 Portfolio Return and Risk

Stage 1 brief, drafted 2026-10-24 from the editor's spine (`plans/vol-5.md`, "### Spine of LM27 Portfolio Return and
Risk") and the shared decisions of the same file; revised the same day to the editor's decisions on the briefs
(`plans/vol-5.md`, "Editor's decisions on the briefs (2026-10-24)", A–G and "Per module"), after the first independent
recomputation (46 of 46 anchors reproduced) and the cross-module check; and revised again the same day to the second
recomputation (49 of 49 anchors reproduced, 208 printed numbers audited), the second cross-check (Y1–Y20) and the
decisions on them ("Decisions on the first revision" and "Decisions on the second recomputation and cross-check"); and
revised a third time on 2026-10-25 to the last verification (four minor items, one question) and "Decisions on the
third revision (2026-10-25)", including "Listing markets"; and revised a fourth time on 2026-10-31 to the fresh
check of the whole of Stage 1 (49 of 49 active anchors reproduced; one critical, six major and 24 minor items fixed,
two refuted; the editor's choices on B27-03, B27-06 and SP-01), with seven anchor rows extended (A27-05, A27-16,
A27-20, A27-22, A27-23, A27-39, A27-45; no earlier value changed). Every number carries its anchor ID at first appearance;
`data/vol5_anchors_lm27.py` prints them all (50 rows, A27-46 withdrawn; `## LM27` of `plans/vol-5-anchors.md`).
Numbers quoted from published modules carry their file:line and are echoed by the script where it says so. Each
derived figure is printed with the digits its printed inputs need, so that a reader recomputes it from them; where no
precision does that, the brief says "from unrounded inputs" (PITFALLS, "Printed numbers that do not recompute"). The
script reads only `data/processed/vol5_frames.parquet`, `vol5_ohlc.parquet` and
`vol2_closes.parquet` (built from the registered raw files) through the shared builders (`vol5_series.frames`, `ohlc`;
`vol5_rules.schedule`, `signals`, `wealth_path`, `cov0`; `lm10_series.u28`), writes nothing, and passes `ruff check`
and `ty check`.

**Layer added.** LM7 priced two funds held at fixed weights; LM8 wrote a book's P&L and returns as dot products; LM10
made $\mathbf w^{\top}\hat\Sigma\mathbf w$ a sample quantity; LM16 its population form; LM23 the market model. LM27 adds
time and attribution: the weights a book really holds drift between trades, every trade costs money and comes out of
wealth, the five-fund sample needs two date frames, and the book's risk splits among its funds in one meaningful way.

**Prereq:** `[1, 3, 7, 8, 9, 10, 11, 12, 16, 19, 20, 23]`. What each supplies (tags rechecked in `src/`):

- LM1: (1.12) $\ln G=\sum_tr_t$ (lm01.md:404); (1.13) $R_p=\sum_jw_jR_j$ with start-of-period weights, any sign
  (lm01.md:427); (1.14) averaging log returns across a long-only book understates its log return (lm01.md:433), and
  the example of averaged logs, 27.28 against 21.13 (lm01.md:438–445).
- LM3: the working rule, simple returns across positions and log returns across time (lm03.md:266–271).
- LM7: the two-asset variance and $\operatorname{Cov}(R_1,R_p)$, the marginal variance as twice the covariance with the
  portfolio (lm07.md:94); the pair 0050/00679B, 2,363 returns, $\rho=-0.11$, 0050 +767.3% (lm07.md:36, 45–50).
- LM8: (8.2) $\Delta W=\mathbf h^{\top}\Delta\mathbf P$ with holdings in units (lm08.md:102); (8.3) $R_p=\mathbf w^{\top}\mathbf R$
  for weights summing to 1 (lm08.md:120); (8.4) $\Delta W=W_0\mathbf f^{\top}\mathbf R$ for exposures (lm08.md:130); the
  1-norm and net and gross exposure (lm08.md:178–182); (8.11) $s_p\le\sum_iw_is_i$ for $w_i\ge0$, equality only when all
  correlations among held assets are 1 (lm08.md:294–296); (8.12) $X\mathbf w$ is a daily-rebalanced book and (8.13)
  $Y\mathbf h$ a fixed book (lm08.md:381–387); the pair's $A=243.0543$, $\rho=-0.1056$ and volatilities 20.11% and
  13.50% (lm08.md:284).
- LM9: the buy-and-hold mix whose weight drifts 0.50 → 0.858, low 0.457, high 0.883 (lm09.md:437), and the
  cap-weighted index whose weights drift (lm09.md:444).
- LM10: (10.2) $\hat\Sigma=\tilde X^{\top}\tilde X/T$ (lm10.md:127); (10.3) $C$ (lm10.md:148); (10.4)
  $s_p^2=\mathbf w^{\top}\hat\Sigma\mathbf w$ exact for constant weights (lm10.md:181); (10.5) $\mathbf w^{\top}\hat\Sigma\mathbf w\ge0$ (lm10.md:185), for the widget; (10.6) the equal-weight split
  (lm10.md:208); (10.8) $\nabla(\mathbf w^{\top}M\mathbf w)=(M+M^{\top})\mathbf w$, which is $2M\mathbf w$ for symmetric
  $M$ (lm10.md:403); (10.9) the exact second-order expansion (lm10.md:409); the U28 book's 15.75%, 21.94%, 4.22%, 7.2%
  and 92.8% (lm10.md:21, 36, 41, 220); the form "$T$ returns times 365.25, divided by the sample's calendar days" for
  $A$ (lm10.md:41).
- LM11: (11.4) $\lambda_N\le\mathbf u^{\top}M\mathbf u\le\lambda_1$ for unit $\mathbf u$ (lm11.md:184), in one knowledge
  check. The spine's (11.2) is not used.
- LM12: (12.3) slopes from covariances (lm12.md:120), so $\beta_{i,p}$ is a regression slope; (12.4) R-squared (lm12.md:126), for KC §8; an index return is
  $\mathbf w_{t-1}^{\top}\mathbf R_t$ with weights set at the previous close (lm12.md:155–160).
- LM16: (16.2) covariance (lm16.md:142); (16.4) $\Cov(M\mathbf X+\mathbf b)=M\Sigma M^{\top}$ (lm16.md:220); (16.8) the
  conditional mean in a normal pair (lm16.md:339), for the loss-share reading of a risk contribution.
- LM19: (19.3) the sample raw kurtosis, divisor $T$ (lm19.md:158), for the condition of the plug-in standard error;
  weekly and monthly returns built from daily data, (19.7) the variance of an $m$-period sum (lm19.md:283) and the annualization rules with their conditions
  (lm19.md:353, 363–372; outcomes at lm19.md:15–16); a year counted as the periods with data, 1,185/23 = 51.52 weeks or 12
  months (lm19.md:39).
- LM20: the normal-theory standard error of a correlation, $\Var\hat\rho\approx(1-\rho^2)^2/T$, and its plug-in
  counterpart (Practice Problem 6, lm20.md:558); a standard error built from fourth moments needs them finite
  (lm20.md:364).
- LM23: (23.1) OLS (lm23.md:66); (23.8) the dividend term of Jensen's regression (lm23.md:293), for the price-index pitfall; the market model and beta (lm23.md:279–283); U28's market betas, 0.507 to 1.207
  (lm23.md:46); residual correlations across the 378 pairs, mean 0.112 (lm23.md:359).

**Leads:** `[28, 29, 30, 31, 32, 33, 34, 35]`. Each later module cites LM27's tags by number (decision C8). The users
below come from the cross-check's tag table of the revised briefs (Y1; decision "Tags and leads"), and "Cross-module
tags" lists them per tag. LM28: (27.4)–(27.6), $\mu_p$, $\sigma_p^2$, $\beta_{i,p}$ and $\mathrm{RC}_i$, so that at
$\mathbf w^{\mathrm{mv}}$ every $\beta_{i,p}=1$; it echoes E5's frame counts, A27-01 to A27-03, and names R1's
first-window shares as LM27's (A27-21). LM29: (27.1)–(27.5), drift, costs, turnover, $\sigma_p^2$ and $\beta_{i,p}$; it
echoes A27-02 and A27-03. LM30: (27.1), (27.2), (27.4), (27.5) and (27.8), the wealth recursion behind a rule's
realized volatility, $\sigma_p^2$, the reading of its multipliers and the single-index matrix; it echoes A27-13 and
A27-21. LM31: (27.1)–(27.3) for R8's drift, cash and borrowing, and (27.5)–(27.6) as the definitions its budgets build
on (decision A6); it echoes A27-01 to A27-03, A27-13 and A27-21. LM32: (27.1), (27.2) and (27.4), the wealth path
and $\sigma_p$; it echoes A27-23. LM33: (27.1) and (27.2), the rules' net returns, with R1 as the benchmark. LM34:
(27.1)–(27.3), net wealth, turnover and costs of every rule; it echoes A27-23, A27-24 and A27-43. LM35: (27.1)–(27.3),
(27.5) and (27.8), the replays, the ruin rule, the checkpoint's turnover limit, $\beta_{i,p}$ and factor shocks; it
echoes A27-11. Every one of them lists 27 among its prerequisites (decision C9). No later brief cites (27.7).

**Forward links honoured.**

| Earlier text | Promise | Kept in |
|:--|:--|:--|
| lm07.md:57 | "Matrix notation for $N$ assets waits for [[LM10]] and [[LM27]]" | §2 (27.1) and §5 (27.4) write the book in matrix form for $N=5$; E6 extends LM7's pair to five funds |
| lm09.md:444 | a sector index weights stocks by market value, "so its weights drift with prices ([[LM27]])" | §2: (27.1) is the drift; a cap-weighted index is a buy-and-hold book between changes of its members or share counts (lm12.md:161); X2 for E5; LM9's 0.50 → 0.858 echoed [A27-27] |
| lm10.md:225 | "Splitting $s_p^2$ into one share per asset, and judging which split is meaningful, is the subject of [[LM27]] and [[LM31]]" | §6: three splits compared (stand-alone, variance terms, Euler) [A27-16]; four reasons for Euler's; LM31 uses the shares as targets |
| lm10.md:425 | "entry $i$ of $2\hat\Sigma\mathbf w$ is a rate of change, not asset $i$'s share of the risk ([[LM27]], [[LM31]])" | §6: $\mathrm{MRC}_i$ is that rate divided by $2s_p$; the share needs $w_i$ times it; E8's switch, exact against linear [A27-19] |
| lm16.md:225 | "Splitting $\sigma_p^2$ among assets is the work of [[LM27]] and [[LM31]]" | §6 derives (27.5)–(27.6) in population form from (16.2) and (16.4), then evaluates them at $\hat\Sigma$ |
| lm23.md:416 | "Factor risk in a portfolio is [[LM27]]'s bookkeeping and [[LM30]]'s estimation problem" | §8: (27.8), the exact in-sample split into systematic and residual parts; the diagonal-residual shortcut shown once and its estimation left to LM30 |

`grep '\[\[LM27'` over `src/*.md` and `src/pages/*.md` finds exactly these six lines (lm07:57, lm09:444, lm10:225,
lm10:425, lm16:225, lm23:416); `grep LM27 build/make_lab*.py` finds none. The spine missed none. Published lines
without a pointer that LM27 also keeps consistent: lm12.md:159 (weights set at the previous close), lm08.md:383–387
(daily-rebalanced $X\mathbf w$ against a fixed book), lm07.md:94 (the marginal variance; LM31's promise, which LM31
keeps with (31.1) built on LM27's (27.6), decision A6).

**Outcomes** ("After this module you should be able to:"; level in brackets, AUTHORING §3's form on the page;
average 15.4 words, longest 18):

1. [C] compute a book's return from the weights set at the previous close, and track how buy-and-hold weights drift
2. [D] derive the wealth recursion with trades, turnover and costs, and solve it for the post-trade wealth
3. [U] explain why E5 needs an estimation frame and a wealth frame, and why its daily correlations can mislead
4. [C] compute a portfolio's mean, variance and volatility from $\boldsymbol\mu$ and $\Sigma$, and measure its diversification
5. [D] derive each asset's covariance and beta with the portfolio, its risk contributions, and Euler's identity
6. [U] choose a meaningful split of portfolio risk, and interpret a negative or unstable contribution
7. [C] split a portfolio's variance into systematic and residual parts with market betas
8. [C] compute risk contributions and the wealth recursion in NumPy, and check them against their identities

Taught, practised and assessed (REVIEW_PROMPT item 10):

| Outcome | Taught | Practised | Assessed |
|:--|:--|:--|:--|
| 1 [C] | §2 (27.1) | E1 | KC §2; P1, P3 |
| 2 [D] | §3 (27.2), (27.3), Deep Dive | E2, E3 | KC §3; P2, P8 (derive), P12 |
| 3 [U] | §4 | E4, E5 | KC §4; P6, P11 |
| 4 [C] | §5 (27.4), (27.7) | E6 | KC §5; P4, P10 |
| 5 [D] | §6 (27.5), (27.6), Deep Dive | E7, E8 | KC §6; P7 (derive), P10 |
| 6 [U] | §6, §7 | E7, E9 | KC §7; P5 |
| 7 [C] | §8 (27.8) | E10 | KC §8; P9 |
| 8 [C] | §9 | lab Parts 3, 6 | KC §9; P11, P12 |

**Owns.** The book's return from weights set at the previous close, with exposures and cash, and the drift of
weights between trades (27.1); buy-and-hold against rebalanced books (the drift exhibit; a cap-weighted index as a
buy-and-hold book between changes of its members or share counts, lm12.md:161); the wealth recursion with trades, the self-financing equation, its existence and uniqueness,
turnover $\mathrm{TO}_t$ and the cost of a trade (27.2)–(27.3), citing the cost model and LM34 for its sources; the
cost arithmetic of a trade and of the first purchase (decision A5; LM32 echoes A27-23, and LM34 echoes A27-23, A27-24
and A27-43); the first purchase and one dated rebalance of R1 as worked trades; E5's two frames and why they differ
(counts, $A$ and $A_{\mathrm w}$, the June 2025 halt, LM7's 2,363 against E5's 2,362 [A27-02, A27-07]); the domain of
log growth ($1+R_{p,t}>0$; ruin otherwise); simple returns across assets and log returns across time on E5; the
asynchronous closes of E5 (daily, weekly and monthly correlations with their standard errors and the funds' raw
kurtosis, which the plug-in error's condition needs); $\mu_p$, $\sigma_p^2$ and annualization (27.4), with R1's and
R2's $\mu_p$; the diversification ratio, the weighted average volatility over the book's, from (8.11) (27.7);
$\Cov(R_i,R_p)=(\Sigma\mathbf w)_i$ and $\beta_{i,p}$ (27.5); $\mathrm{MRC}_i$, $\mathrm{RC}_i$ and Euler's identity
(27.6), derived here only (decision A6); which split is meaningful and why; negative contributions; R1's full-sample
$s_p$ (A27-13, which LM30 and LM31 echo); the risk shares of R1 across the 92 windows, the first window's included (a
stability check; decision A4 leaves R1's first-window shares, A27-21, with LM27, and LM30 and LM31 echo them); the
factor split of $\sigma_p^2$ with market betas (27.8) on U28; R1 and R2 defined. Values owned: every A27 anchor except
those echoed from LM7–LM10 and LM23, which are cited to their modules. LM27 prints no comparison criterion of any rule
(shared decision "Owners").

**Leaves.** Choosing weights, minimum variance and tangency → LM28. Every statistic of the first window → LM28
(decision A4), except the risk shares (R1's are LM27's, A27-21; R2's are LM31's) and R2's first-window mean excess
return and volatility, Black–Litterman's calibration (LM30's, A30-24; LM31 echoes them). One sentence: at LM28's
minimum-variance portfolio every $\beta_{i,p}$ equals 1, so risk shares equal weights. Constraints and costs as a term
in the objective → LM29. The error in $\hat\Sigma$ and factor-model covariances as estimators (the single-index
target) → LM30. The risk shares stay plug-in estimates whose error LM27 does not measure, said once (shared decision
"Estimate, standard error, interval"); [[LM30]] measures that of R1's first-window shares by simulation, standard
deviations of 1.0 to 1.7 points (A30-42), and X7 shows how the shares move across windows. Contributions as targets
(risk budgets, ERC), HRP, R8's exposure and its financing rate → LM31. Contributions to VaR or expected shortfall →
not in the book (one sentence citing Qian 2006 for VaR). The rules' net wealth, log growth, annual turnover, costs and
the cost sources → LM34 (decision A2). Scenario losses → LM35. Net and gross exposure → LM8, cited.

**Uses before taught** (one sentence each in the text):

- §3: "The rates are Taiwan's posted commission and transaction tax; [[LM34]] gives their official sources."
- §3: "[[LM31]] sets R8's exposure, which may exceed 1, and the rate at which R8 borrows."
- §3: "The other six rules, R3 to R8, are defined in [[LM28]] to [[LM31]]; every rule trades by (27.2)."
- §4: "The five funds were chosen in 2026 among funds still listed; [[LM34]] shows what such a choice can hide."
- §5: "Every matrix here is a plug-in estimate with an error this module does not measure; [[LM30]] measures the
  error of $\hat\Sigma$ and of R1's risk shares."
- §6: "Equal contributions as a target are [[LM31]]'s risk parity."
- §8: "Estimating a factor model's covariance, and the cost of ignoring residual covariances, is [[LM30]]'s subject."

**Data role.**

- **E5** (shared decision "Data"): `vol5_series.frames("E5")` reads `data/processed/vol5_frames.parquet` (built and
  checked by `data/vol5_series.py`; FinMind `TaiwanStockPrice`, `TaiwanStockDividendResult` and
  `TaiwanStockSplitPrice`, retrieved 2026-10-24 as `data/README.md` records). Funds and the indices their issuer's
  pages name (read 2026-10-24): 0050 元大台灣50 (FTSE TWSE Taiwan 50 Index), 00646 元大S&P500 (S&P 500 Index), 00679B
  元大美債20年 (ICE US Treasury 20+ Year, SOURCES), 00635U 期元大S&P黃金 (S&P GSCI Gold Excess Return Index; COMEX gold
  futures), 00642U 期元大S&P石油 (S&P GSCI Crude Oil Enhanced Excess Return; NYMEX WTI futures). Base close 17 January
  2017, the close before the first return; last close 8 October 2026; 3,551 calendar days, 9.7221 years (calendar
  days ÷ 365.25 from the close before the first return to the last close, decision C7) [A27-01]. Total returns as
  Volume I: $R_{i,t}=(P_t+D_t)/P_{t-1}-1$; on 0050's 4-for-1 split day the previous close is restated per current
  share, so 18 June 2025's return is $(P_t+D_t)/(P_{t-1}/4)-1$ (decision B6: no split-ratio symbol).
- **Estimation frame:** $T=2{,}362$ one-session returns, 18 January 2017 → 8 October 2026; $A$ is 2,362 returns times
  365.25, divided by the sample's 3,551 calendar days, $A=242.951$ [A27-02], as lm10.md:41 writes U28's. Every
  covariance, correlation, mean and risk share, labelled "on the 2,362 joint dates" (decision C2). **Wealth frame:**
  2,368 sessions, $A_{\mathrm w}=2{,}368\times365.25/3{,}551=243.569$; the six dates 11–18 June 2025 are in it only;
  0050 has no close on five of them [A27-03]. Its 18 June return, $4\times47.57/188.65-1=0.864\%$ (exact on the
  two-decimal closes), is booked that day [A27-04]. Every return, drift, trade and wealth. Growth factors differ by
  frame (00642U 1.593 against 1.412) [A27-06]. A fund described alone would use its own dates and its own sessions a
  year (decision X18); LM27 describes no fund alone beyond that frame comparison.
- **LM7's pair** (recorded use): 2,363 returns between common closes, recomputed to LM8's $\rho=-0.1056$ and 20.11%,
  13.50% [A27-07]; E5's frame gives −0.105 on 2,362, without 2025-06-18.
- **Weekly and monthly returns:** compound the estimation frame's daily returns within ISO weeks (keys ISO year, ISO
  week) and calendar months. The first and last period, in which the sample starts and ends, are dropped, complete or
  not (decision "Weeks and months"; the rule needs no holiday calendar): 500 weeks and 116 calendar months [A27-10].
  Weeks are annualized as LM19 counts a year (lm19.md:39), by the periods with data (decision D):
  $A=500\times365.25/3{,}542=51.56$, the 500 weeks with a session over 9.6975 years from the close of 20 January 2017,
  before the first weekly return, to that of 2 October 2026 (decision C7; the span of the 506 calendar weeks, six of
  them Lunar New Year weeks without a session). Months use $A=12$, the book's monthly convention (shared decision
  "Sharpe ratio") [A27-12]. Each caption says so. The last ISO week, 5–8 October 2026, holds all four of its sessions
  (TX's settlement file, `data/raw/vol4/`, has no session on 9 October) and is dropped by the rule; keeping it would
  move 0050–00679B's weekly correlation from −0.023 to −0.024 [A27-10], a figure the module does not print.
- **Windows:** `vol5_rules.schedule`: the trailing 504 estimation rows through each of the 92 signals, 27 February 2019
  → 30 September 2026 [A27-20]; the first window runs 13 February 2017 → 27 February 2019 [A27-21]. A window's
  covariance is annualized with the full sample's $A=242.951$, as `vol5_rules.signals` does.
- **The through case:** R1 and R2 from `vol5_rules.signals` and `wealth_path` (costs as the shared decision); LM27 uses
  their first purchases of 4 March 2019, R1's trade of 1 April 2026 and R1's return over 10–18 June 2025, all scale-free.
- **U28** (Volume II, through `lm10_series.u28()`): 28 sector price indices and the TAIEX price index, $T=4{,}382$,
  $A=245.4794$ [A27-27]; price indices, no dividends: every caption says so, and only their covariances are used.
- **Timing of the closes** (decision on LM27; "Listing markets"): §4 argues from the trading sessions and from the
  correlations by frequency. 0050, 00646, 00635U and 00642U trade on TWSE and 00679B on TPEx. Both markets match
  orders from 09:00 to 13:30 Taipei time, with a closing call auction from 13:25: TWSE's Operating Rules Art. 3 and
  its trading system page; TPEx's Business Rules (業務規則) Art. 40, applied to ETFs by its ETF rules' Art. 4 ¶2, and
  its trading system page. New York's core stock session, 9:30 a.m. to 4:00 p.m. New York time (NYSE), ends at 04:00
  Taipei time in US summer time and 05:00 otherwise (IANA time-zone data). So the 13:30 closes of 00646 and 00679B
  follow the previous New York session, and 0050 at the same close reacts to that session too. TWSE's ETF overview
  page adds that a futures-trust ETF on a foreign futures index is valued on European and US futures, so the time
  difference is a risk. The text claims no fixing time for the futures funds' indices (no source states one) and
  prints no SPY figure.
- **Conventions.** Simple returns; divisor $T$ everywhere (`ddof=0` passed explicitly); every printed number rounded
  from its unrounded value; sample values of model symbols are plug-in values at $\hat\Sigma$ (the notation note says
  so). A correlation's standard error is printed both by normal theory and by LM20's plug-in formula. Both assume
  independent periods, and the plug-in one needs finite fourth moments, so §4 prints the funds' raw kurtosis beside
  it [A27-50]. Every R1 volatility names its sample and weights ("full sample, weights reset daily": 11.49%; LM30's
  out-of-sample 12.48%, A30-12, is another number, decision C7). Counts against a threshold (00679B's negative shares, R2's 0050 share above 70%) use the guard $10^{-12}$, and the script prints their smallest margins [A27-20, A27-45].
- **Scripts.** `data/lm27_numbers.py` (every printed value, asserted against `src/lm27.md` and compared with the anchors)
  and `data/lm27_charts.py` (X2, X4, X6, X7 and the widget block), both after `data/vol5_series.py`,
  `data/vol5_rules.py`, `data/vol2_series.py` and `data/lm10_series.py`.

**Hygiene declaration.** *Descriptive:* the full-sample covariance matrix, correlations by frequency with the funds'
kurtosis, every risk split of R1's and R2's weights, the drift path, the U28 factor split, LM7's and LM9's echoes, and
Problem 6 (E5's monthly correlation). *Stability check:* R1's risk shares in the 92 trailing windows. *Through case,
fixed in advance (2026-10-24):* the trades of R1 and R2, shown as accounting, not compared: the module prints no
comparison criterion. *Constructed:* R2's weights; Problems 1–4 and 10. Versions on the same data: two rules (R1, R2)
and one variant shown only by its weights (the buy-and-hold book). Local note: "Every matrix and risk share here
describes E5's 2,362 joint daily returns from 18 January 2017 to 8 October 2026, or U28's sector price indices from
2008 to 2026: descriptive. R1's shares in its 92 trailing windows are a stability check. The trades are the through
case's, fixed in advance on 24 October 2026; they show the accounting, and no rule is judged here. Nothing is tested
on later data: [[LM30]], [[LM33]] and [[LM34]] do that."

**Notation.** AUTHORING §6 with the Portfolios table. Used: $R$, $r$, $T$ (returns at the stated frequency), $t$, $A$,
$N$ (5, or 28 on U28), $i$, $j$ (assets), $\mathbf R_t$, $X$, $\tilde X$, $\bar{\mathbf R}$, $\hat\Sigma$, $\Sigma$, $\mathbf s$,
$C$, $\rho$, $\hat\rho$, $\mathbf w$, $\mathbf w_{t-1}$, $\mathbf w^{\mathrm{drift}}_t$, $\mathbf f$, $\lVert\cdot\rVert_1$,
$\mu_p$, $\sigma_p$, $\sigma_p^2$, $s_p$, $\boldsymbol\mu$, $\beta_{i,p}$, $\beta_i$ (market beta, LM23), $\mathrm{MRC}_i$,
$\mathrm{RC}_i$, $\mathrm{TO}_t$, $\text{tax}_i$, $W$, $W^{\mathrm{pre}}_t$ (wealth before the day's trade; $W_t$ after
it, equal on a date without a trade), $A_{\mathrm w}$ (243.569; both book-wide from Volume V, decision B2), $G$, $P$,
$D$, $r_f$ (1.5%, cash only), $\lambda_k$ (KC §5), $\boldsymbol\Delta$ (LM10's change of weights,
$\mathbf 1^{\top}\boldsymbol\Delta=0$), $\E$, $\Var$, $\Cov$, $\mathcal N$, $\operatorname{SE}$. Local symbols, declared in
the notation note:

| Symbol | Meaning | Check |
|:--|:--|:--|
| $R_{p,t}$, $R_{i,t}$ | the book's and fund $i$'s simple return on date $t$ | as LM8's $R_{j,t}$ |
| $\operatorname{cost}(\mathbf x)$ | the cost of trades $\mathbf x$ in money, $0.1425\%\,\lVert\mathbf x\rVert_1+\sum_i\text{tax}_i\max(0,-x_i)$ | upright function name; no scalar cost symbol (§6) |
| $R_{\text{mkt},t}$, $\sigma_{\text{mkt}}^2$, $\boldsymbol\beta$ | TAIEX price return (LM23's), its variance, the vector of the $N$ market betas | as LM23; one TAIEX variance symbol in LM27 and LM30 (decision B6); $\boldsymbol\beta$ here collects $\beta_i$ across assets |
| $\varepsilon_{i,t}$, $\hat\varepsilon_{i,t}$, $\Sigma_{\mathrm{res}}$ | sector $i$'s market-model error and its OLS residual (AUTHORING §6, as LM23); the $N\times N$ covariance matrix of the errors, and in sample of the residuals (divisor $T$) | new: LM23's $\Sigma_\varepsilon$ is the error covariance across dates |

Sample values are plug-in values: the text writes $s_p$ for a computed volatility and "at $\hat\Sigma$" for
contributions, without hats on $\beta_{i,p}$, $\mathrm{MRC}_i$, $\mathrm{RC}_i$ (one sentence in the note). Counts: $N$
assets ($i$, $j$), $T$ returns ($t$); the number of windows (92) and rebalances (91) are written as numbers. Positions
in money are written $W^{\mathrm{pre}}_t\mathbf w^{\mathrm{drift}}_t$ (LM8's $\mathbf h$ counts units); cash is
$W_t(1-\mathbf 1^{\top}\mathbf w_t)$, which is $W_t(1-\mathbf 1^{\top}\mathbf f_t)$ after a trade, with no cash symbol. In (27.1)–(27.3) $\mathbf w_{t-1}$ and $\mathbf w^{\mathrm{drift}}_t$ are each fund's value over wealth, so they sum to the book's exposure, not necessarily to 1; total exposure is $\mathbf 1^{\top}\mathbf f$ ($L$ is R8's, in
LM31); the ratio (27.7), the commission rate and the raw kurtosis ((19.3)) are written in words and numbers. The split
day's restated close is written $P_{t-1}/4$ inside the return itself (decision B6), since $s_i$ and $s_p$ are standard
deviations. Not used: $c$, $\mathbf e$ and $\mathbf e_i$.

**Motivating case: "Which fund carries the risk?"** (box, about 160 words in three paragraphs of at most 80 words,
decision C10; 11 sentences, average 14.6 words, longest 25)

> A reader holds [[LM7]]'s two funds, 0050 and 00679B, and adds three: 00646 (the S&P 500), 00635U (gold futures) and
> 00642U (crude-oil futures). She puts a fifth of her money in each. On the 2,362 joint dates from January 2017 to
> October 2026, when all five funds traded, their volatilities ran from 13.49% to 37.43% a year [A27-08]. Yet the mix,
> reset to a fifth each day, had a volatility of 11.49% on the same dates [A27-13].
>
> Which fund carried that risk? 00642U held a fifth of the money and 45.9% of the risk; 00679B held a fifth and
> 2.6% [A27-15]. Left alone, the weights drift. Bought on 4 March 2019 and held, 0050 grew to 48.6% of the book by
> 8 October 2026 [A27-26].
>
> Resetting the weights each month costs money. The largest of 91 monthly resets, on 1 April 2026, traded 8.06% of the
> book and cost 0.031% of its value [A27-24]. How should the risk be split, and what does each trade cost?

Resolved: (a) the split: §6, E7 (00642U's share is its weight times its beta to the book, $0.2\times2.295$
[A27-14]), X6; (b) the drift: §2, (27.1), X2 (0050 from 19.1% in August 2019 to 49.1% in July 2026 [A27-26]); (c) the
cost: §3, E3 and X3 (on a book of NT\$10 million before the trade, NT\$2,294 of commission and NT\$806 of tax, NT\$3,100
in all [A27-44]); (d) why 45.9% is one estimate among many: §7, X7 (32.7% to 54.3% across the 92 windows [A27-20]).
The case says that 1 April 2026 is the largest of R1's 91 rebalances (AUTHORING §8); LM34 reports their annual total.

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | the layer added; case + X1; roadmap; notation and hygiene notes | 380 |
| 2 | The Return of a Book {1} | weights set at the previous close (lm12.md:159), (8.3), (1.13); exposures and cash, (8.4); (27.1) and the drift; daily-rebalanced $X\mathbf w$ against a book that never trades ((8.12), (8.13)); a cap-weighted index as such a book between changes of its members or share counts (lm09.md:444, lm12.md:161); X2; E1 (the June 2025 span: simple returns add across funds, log returns over the six days, averaged logs understate); the domain $1+R_{p,t}>0$ and ruin; pitfall: averaging log returns across funds; 導讀; KC | 560 |
| 3 | Trades, Turnover and Costs {2} | the trade at the next close (Research hygiene); (27.2): pre-trade wealth, the self-financing equation, existence and uniqueness (Deep Dive); the cost model (pointer to LM34); (27.3) $\mathrm{TO}_t$ and the approximation with its error bound; E2 (first purchase); E3 + X3 (2026-04-01); cash at $r_f$, R8 by pointer; no terminal sale in the through case; pitfall: turnover counted on both sides; 導讀; KC | 600 |
| 4 | E5: Two Frames and Asynchronous Closes {3} | the five funds and their indices; total returns with distributions and the split day's restated close, $P_{t-1}/4$ (Volume I's rule, decision B6); the universe chosen among listed funds (pointer to LM34); E4 (why two frames; 2,362 against 2,368 and LM7's 2,363; the six June 2025 dates; growth factors by frame); the rule (joint statistics on the estimation frame, wealth on the wealth frame, one fund on its own dates; PITFALLS §3); asynchronous closes from the trading sessions (the 13:30 close of TWSE, where four funds trade, and of TPEx, where 00679B trades; NYSE's core session ending at 04:00 or 05:00 Taipei time; TWSE's ETF overview page on futures-trust ETFs); X4; E5 (correlations by frequency with both SEs, their conditions and the funds' raw kurtosis; among the five pairs, the one daily–monthly gap of two SEs, no cause named; R1's volatility by frequency); Burns, Engle and Mezrich (1998) in one sentence; the rules use daily $\hat\Sigma$; 導讀; KC | 600 |
| 5 | Portfolio Mean and Variance {4} | (27.4) from (16.4) and (10.4); annualization, a convention on simple returns, and the variance rule's condition ((19.7)); X5; E6 (R1 and R2: $\mu_p$, $s_p$; (10.6)'s split; the diversification ratio (27.7) with (8.11) and Choueifaty and Coignard's name and condition, against U28's); the plug-in sentence; KC ((11.4)) | 470 |
| 6 | Which Fund Carries the Risk {5,6} | (27.5) $\Cov(R_i,R_p)=(\Sigma\mathbf w)_i$ and $\beta_{i,p}$; (27.6) $\mathrm{MRC}_i=\partial\sigma_p/\partial w_i$ from (10.8) and the chain rule, for $\sigma_p>0$; Euler's identity derived, the homogeneity theorem in a Deep Dive (Maillard et al. 2010); X6; E7 (R1's split; three splits compared, with what each adds up to); which split is meaningful: it adds up to the book's volatility, it is the variance term plus half of each covariance term, it prices a switch (MRC differences, lm10.md:425), it is the slope of a fund's line on the book (12.3), and under joint normality the expected share of a move ((16.8); Qian 2006); E8 (switch of 5 points, (10.9)); the widget; LM28's minimum-variance sentence; 導讀; KC | 740 |
| 7 | Negative and Moving Contributions {6} | $\mathrm{RC}_i<0$ exactly when $w_i\Cov(R_i,R_p)<0$; a hedge at the margin only ($\partial\mathrm{MRC}_i/\partial w_i=(\sigma_i^2-\beta_{i,p}^2\sigma_p^2)/\sigma_p=\sigma_i^2(1-\rho_{i,p}^2)/\sigma_p\ge0$ with the other weights fixed, $\rho_{i,p}$ the correlation of $R_i$ with $R_p$, so $\mathrm{MRC}_i$ never falls as $w_i$ grows); E9 (the window through 2020-02-27); X7 (R1's shares across 92 windows: stability check; LM30 measures the first window's error); pitfall: a negative share is not a hedge at any size; KC | 360 |
| 8 | Systematic and Residual Risk {7} | the market model per asset ((23.1)); the book's beta $\mathbf w^{\top}\boldsymbol\beta$; (27.8) exact in sample (normal equations); per-asset split of $\mathrm{RC}_i$; E10 + X8 (U28's book); the diagonal-residual shortcut (single-index model) once, and its error; price indices; LM30 pointer; 導讀; KC | 460 |
| 9 | Portfolio Accounts in Python {8} | `cov0` / `np.cov(..., ddof=0)`; `S @ w`, contributions, checks ($\sum\mathrm{RC}_i=s_p$, the slope check); Polars weekly and monthly returns (`dt.iso_year`, `dt.week`, `group_by`, `pl.col(...).add(1).product()`); the recursion in ten lines; lab box | 200 |
| — | Summary (7) / Problems (12) / Solutions | | 140 / 420 / 520 |
| | **Total** | | **5,450** |

**Elements.** 10 examples (E1 §2; E2, E3 §3; E4, E5 §4; E6 §5; E7, E8 §6; E9 §7; E10 §8). Knowledge checks:

- §2: a fifth in each fund at the close of 10 June 2025, no trade: 00642U's weight at 18 June's close is 21.97%
  (0.2 × 1.12816 over the book's 1.02685) [A27-42, A27-05].
- §3: switching NT\$1,000,000 from 00679B to 0050 costs about NT\$2,850 (commission on both sides); the reverse switch
  NT\$3,850, because 0050's sale pays the 0.1% tax and 00679B's would not [A27-43].
- §4: why E5's 0050/00679B pair has 2,362 returns and LM7's 2,363: the estimation frame drops 18 June 2025, whose return
  spans 0050's halt; LM7's pair keeps it, both funds measured from 10 June [A27-02, A27-07].
- §5: by (11.4), $s_p^2$ of the 1/N weights lies between $\lambda_5/5=23.61$ and $\lambda_1/5=285.98$ (%², annual); it is
  132.09, the square of R1's full-sample 11.493% [A27-32, A27-13].
- §6: in R2, 0050 holds 40% of the money and $0.4\times1.587=63.5\%$ of the risk; the five shares sum to 1 because
  $\sum_iw_i\beta_{i,p}=\mathbf w^{\top}\Sigma\mathbf w/\sigma_p^2$ [A27-17].
- §7: 00642U carries 45.9% of R1's risk on the full sample and 32.7% to 54.3% across the 92 windows [A27-15, A27-20]: is 45.9% a forecast? No: each share describes its own sample, X7 is a stability check, and [[LM30]] measures the first window's error. In the window through 27 February 2020, would selling some 00679B lower R1's risk? No: its $\mathrm{MRC}$ is
  −0.77%, and the other four funds' MRCs are all positive there. So selling a little of it into any of them, or into cash, raises the volatility at the margin [A27-22].
- §8: why the systematic share of the U28 book's variance, 83.4%, equals the R-squared of the book's regression on the
  TAIEX price index [A27-28]: both are $(\mathbf w^{\top}\boldsymbol\beta)^2\sigma_{\text{mkt}}^2/s_p^2$, by (12.4) and
  (27.8).
- §9: `np.cov(X, rowvar=False)` divides by $T-1$: on 2,362 returns it raises every volatility by the factor 1.000212,
  so R1's full-sample 11.493% becomes 11.495% [A27-34].

中文導讀 in §2 (再平衡 (rebalancing), 買進持有 (buy-and-hold), 權重 (weights) 漂移, 簡單報酬 and 對數報酬), §3 (交易成本
(transaction cost), 週轉率 (turnover), 手續費 (commission), 證券交易稅 (securities transaction tax), 自我融資
(self-financing)), §4 (指數股票型基金 (ETF), 非同步 (asynchronous) 收盤, 相關係數 by frequency, 峰態 (kurtosis)), §6
(投資組合 (portfolio), 風險貢獻 (risk contribution), 邊際風險貢獻 (marginal risk contribution), 一次齊性函數
(homogeneous function of degree 1), Euler 定理 (Euler's theorem), 風險分散 (diversification); beta in English as
LM23), §8 (系統性風險 (systematic risk), 殘差 (residual), 市場模型 (market model), 單一指標模型 (single index model)).
Deep Dives: §3 "One post-trade wealth": the map $g(W)=W+\operatorname{cost}(W\mathbf f_t-W^{\mathrm{pre}}_t\mathbf w^{\mathrm{drift}}_t)$ is continuous
and strictly increasing when $(0.1425\%+\max_i\text{tax}_i)\lVert\mathbf f_t\rVert_1<1$ (its slope is at least $1$ minus
that number, since cost is Lipschitz in $W$), so $g(W)=W^{\mathrm{pre}}_t$ has one root; it is at most
$W^{\mathrm{pre}}_t$ because $g(W^{\mathrm{pre}}_t)\ge W^{\mathrm{pre}}_t$, and positive when
$g(0)=\operatorname{cost}(-W^{\mathrm{pre}}_t\mathbf w^{\mathrm{drift}}_t)<W^{\mathrm{pre}}_t$ (selling the whole book
costs less than the book), which holds for every E5 rule; the fixed-point iteration
$W\mapsto W^{\mathrm{pre}}_t-\operatorname{cost}(\cdot)$ contracts by the factor $(0.1425\%+\max_i\text{tax}_i)\lVert\mathbf f_t\rVert_1$; with the signs of the trades known the
root is a ratio of two linear expressions (E3 checks it). §6 "Euler's theorem": a differentiable $h$ with $h(a\mathbf x)=
ah(\mathbf x)$ for all $a>0$ satisfies $\sum_ix_i\,\partial h/\partial x_i=h(\mathbf x)$ (differentiate in $a$ at $a=1$);
volatility is such a function wherever $\sigma_p>0$ (at a zero-variance book it is not differentiable), and variance,
homogeneous of degree 2, gives $\sum_iw_i\,\partial\sigma_p^2/\partial w_i=2\sigma_p^2$, and LM10's gradient
$2\Sigma\mathbf w$ ((10.8)), twice each fund's covariance with the book, turns this into $\sum_iw_i\Cov(R_i,R_p)=\sigma_p^2$. The working paper of Maillard et al. states the split this way (§2.1, p. 4, and its footnote).

**Exhibits.**

- X1 `case` (table, §1): rows the five funds (code, tracked index from the issuer's page); columns: R1 weight, annual
  volatility, R1 risk share, R2 weight, R2 risk share; footer rows: the mix's volatility 11.49% and 11.17% (full
  sample, weights reset daily), weighted average volatility 20.75% and 16.97%, their ratio 1.81 and 1.52 [A27-08,
  A27-13, A27-15, A27-17]. Note: daily total returns on the 2,362 joint dates ($A=242.951$), divisor $T$; R2
  *constructed*; descriptive. Source: FinMind `TaiwanStockPrice`, `TaiwanStockDividendResult`, `TaiwanStockSplitPrice`,
  retrieved 24 October 2026; Computations: `data/lm27_numbers.py`. Seven columns with the index names (cross-check
  Y20): Stage 2 runs `build/qa/print_width.py` on the draft, and if X1 is wider than the A4 text width, the index
  names move to the note.
- X2 `drift` (`line`, date, shared `x.values`, §2): weights of a book bought at 1/N at the close of 4 March 2019 and
  held to 8 October 2026, five series: 0050, 00646, 00679B, 00642U in colours 1–4, 00635U in `"var(--muted)"` (named
  in the caption); dashed `hline` at 20%. Thinned (decisions C3, X37: buy-and-hold weights rebuild price ratios) to
  402 dated points: the last session of each ISO week (392), the purchase date and every fund's lowest and highest
  weight (ten extremes on nine dates: 00646's low and 00679B's high both fall on 2020-03-23) [A27-26]. Values cited:
  end weights to three decimals, so that they sum to 100.000%: 48.619%, 19.734%, 5.422%, 14.513%, 11.712%; 0050 19.1%
  (2019-08-15) to 49.1% (2026-07-01); 00679B 28.0% (2020-03-23); 00642U 21.3% (2019-04-23) and 7.0% (2020-11-02)
  [A27-26]. Note: wealth frame; the last session of each ISO week, the purchase date and every fund's lowest and
  highest weight; no trade and no cost after the purchase (a purchase cost scales every holding alike, so weights do
  not depend on it); descriptive history, not a rule of the through case.
- X3 `trade` (table, §3, inside E3): R1's trade of 1 April 2026 on a book of NT\$10,000,000 before the trade. Rows the
  five funds; columns: pre-trade holding, trade, holding after the trade, commission, tax [A27-44, A27-41]; total row:
  TO 8.06%, cost NT\$3,100 (commission 291, 197, 185, 472, 1,149, in all 2,294; tax 806 on 00642U's sale), wealth
  after the trade NT\$9,996,900, NT\$1,999,380 in each fund. Whole NT\$; every column sums as printed (holdings to
  10,000,000, trades to −3,100). Note: the through case's R1, signal 31 March 2026; the book's size is hypothetical (the
  recursion is scale-free); rates per the shared cost model, sources in LM34.
- X4 `freq` (`bar`, §4): categories 0050–00646, 0050–00679B, 0050–00635U, 0050–00642U, 00679B–00642U; series daily,
  weekly, monthly (colours 1–3); `fmt: "n3"`. Values cited [A27-11]. Note: simple returns on the 2,362 joint dates, 500
  ISO weeks and 116 calendar months (the first and last period dropped, complete or not); normal-theory standard
  errors near zero correlation about 0.02, 0.045 and 0.09 (0050–00679B: 0.020, 0.045, 0.093); the plug-in ones are
  1.4 to 2.4 times as large on daily data (0050–00679B: 0.040, 0.053, 0.095). Both assume independent periods, and the
  plug-in one finite fourth moments.
- X5 `cov` (table, §5): annualized volatilities and means of the five funds and the correlation matrix to two decimals
  [A27-08, A27-09]. Note: on the 2,362 joint dates (decision C2), divisor $T$, $A=242.951$; descriptive.
- X6 `shares` (`bar`, `stack: true`, approved C1, §6): categories "R1 money", "R1 risk", "R2 money", "R2 risk"; five
  series by fund (00635U muted, named in the caption), `y.fmt: "pct1"`; each bar sums to 100% [A27-15, A27-17].
  Fallback: grouped bars, funds as categories and the four series. Note: risk shares $w_i\beta_{i,p}$ at the
  full-sample $\hat\Sigma$ on the 2,362 joint dates; descriptive.
- X7 `windows` (`line`, date, §7): R1's risk shares at the 92 signals, each from its trailing 504 rows; five series
  (00635U muted); dashed `hline`s at 0 and 20%. Values cited: 00642U 54.3% (window through 2020-02-27) and 32.7%
  (2026-02-26); 00679B −1.89% (2020-02-27), negative in 22 of the 36 windows from May 2019 to April 2022, the last
  (through 2022-04-29) −0.0023%, too small to see on the chart [A27-20]; first window [A27-21]. Note: stability check;
  plug-in shares, whose error [[LM30]] measures for the first window; window covariances annualized with the full
  sample's $A$.
- X8 `factor` (table, §8): U28 equal-weight book: volatility 15.75% (lm10.md:36), TAIEX price index 17.82%, book beta
  0.807; shares of the variance to three decimals, so that they sum: systematic 83.426% (equal to the R-squared),
  residual 16.574% = 4.037% from residual variances + 12.537% from residual covariances; as volatilities 14.4% and
  6.4%; the book's volatility with residual covariances set to 0, 14.73%; Semiconductor's share 3.82% = 4.46% − 0.64%;
  largest GlassCeramic 5.21%, smallest CommunicationsInternet 1.99%, against 3.57% [A27-28, A27-29, A27-30]. Note:
  daily price indices (no dividends), 4,382 returns, OLS with an intercept, in-sample and exact; the shares use the
  unrounded betas and variances (the printed 0.807, 17.82% and 15.75% give 83.4% to one decimal); descriptive. Source:
  as LM23's X1 (FinMind `TaiwanStockPrice`, retrieved 11 October 2026, repaired closes).

**Widget `riskSplit` — "Weights against risk shares."** `Book.controls`: four sliders (0050, 00646, 00679B, 00635U;
−0.2 to 1, step 0.01), 00642U takes the rest, with a warning line when its weight is negative ("00642U is sold
short"); a select for the covariance matrix (three matrices, decision E): "daily, 2017–2026" (initial), "monthly,
2017–2026", "daily, window to 27 Feb 2020". Chart: grouped `bar`, funds as categories, series "money" and "risk"
(colours 1, 2). Readouts: $s_p$; while every weight is non-negative, the weighted average volatility and the ratio (27.7), else $\sum_i\lvert w_i\rvert s_i$ and its ratio, labelled "(8.11) with a short"; the sum of the shares (always 100%).
Module-local code under 30 lines: $\Sigma\mathbf w$, $s_p=\sqrt{\mathbf w^{\top}\Sigma\mathbf w}$, shares
$w_i(\Sigma\mathbf w)_i/s_p^2$; no optimizer (shared decision "Widgets"); the matrices are positive semidefinite by
(10.5), so no check is needed beyond $s_p>0$. Data block `chart-lm27-riskSplit`: three annualized $5\times5$ matrices,
ten decimals, from `data/lm27_charts.py`: daily on the 2,362 joint dates [A27-33], monthly on the 116 calendar months
with $A=12$ [A27-48], daily on the window 29 January 2018 → 27 February 2020 with $A=242.951$ [A27-49]; each anchor
also prints R1's $s_p$ and shares under its matrix, which the charts script tests the JavaScript formula against, with
two other weight vectors, as `data/lm15_charts.py` does. Initial state (PDF): R1, daily, full sample: $s_p=11.49\%$,
shares 21.2%, 17.7%, 2.6%, 12.6%, 45.9% [A27-15].

**Examples** (results recomputed from the printed inputs):

- E1 §2 `span`, 10–18 June 2025 (six sessions of the wealth frame): fund returns +0.864%, −1.689%, −0.792%, +2.226%,
  +12.816% [A27-05] (three decimals, so that the average of the printed values equals the printed 2.685%; the
  two-decimal forms would not). A book bought at a fifth each on 10 June earns their average, 2.685%, by (27.1)
  applied once over the span. Averaging the log returns gives 0.02524, and $e^{0.02524}-1=2.56\%$ is too low, as (1.14)
  says [A27-05]. R1 itself, holding its drifted weights, earned 2.73% [A27-05]; its log return is the sum of its six
  daily log returns (1.12). 00642U's weight rose to 21.97% [A27-42].
- E2 §3 `first`, R1's first purchase at the close of 4 March 2019: from cash of 1, every trade is a buy, so
  $W_t=1-0.001425\,W_t$ and $W_t=1/1.001425=0.998577$; the cost is 0.1423% of the pre-trade wealth of 1, and $\mathrm{TO}_t=\tfrac12
  \lVert\mathbf f_t\rVert_1=0.5$ [A27-23]. R2's purchase is the same.
- E3 §3 `rebalance` (X3), R1 on 1 April 2026 (signal 31 March): pre-trade weights 17.954%, 18.611%, 18.697%, 16.680%,
  28.058% (three decimals, so that the turnover and the approximation follow from them); $\mathrm{TO}_t=8.058\%$; cost
  0.03100% of pre-trade wealth by the exact solution and 0.03102% by (27.3)'s approximation
  $0.285\%\times8.058\%+0.1\%\times8.058\%$ (only 00642U is sold: its pre-trade weight exceeds the target by 8.058 points) [A27-24, A27-41]; on a NT\$10
  million book, NT\$3,100 [A27-44]. The cost per unit of turnover is 0.285% with no taxed sale and up to 0.385% when
  every sale is taxed [A27-25].
- E4 §4 `frames`: 2,362 against 2,368 dates; the six June 2025 dates; 0050 flat on five, then +0.864% on 18 June
  [A27-02, A27-03, A27-04]. Over the estimation frame 00642U's growth factor is 1.412, over the wealth frame 1.593
  [A27-06]: the dropped days include its +12.816% span [A27-05]. LM7's pair keeps the spanning return, 2,363 returns,
  $\rho=-0.1056$ (lm08.md:284), recomputed [A27-07].
- E5 §4 `async`: 0050 with 00679B: −0.105 daily, −0.023 weekly, −0.013 monthly; with 00635U: 0.180, 0.228, 0.187; with
  00646: 0.599, 0.588, 0.552; 00679B with 00642U: −0.18, −0.20, −0.36 [A27-11]. 0050–00679B's normal-theory standard
  errors are 0.020, 0.045 and 0.093; the plug-in ones, which do not assume normality (LM20's Problem 6), are 1.4 to 2.4
  times as large on daily data across the five pairs (0.040 for 0050–00679B) [A27-11]. Both assume independent
  periods, and the plug-in one needs finite fourth moments. So read the plug-in errors of 00642U's pairs with care: its
  raw kurtosis, 26.6 on daily and 12.3 on monthly returns, is the largest of the five (the other four 11.2 to 21.0 and
  4.3 to 5.7) [A27-50]. Of the five pairs, no daily–weekly gap reaches two weekly standard errors of either kind; the
  largest, 0.082 for 0050–00679B, is 1.8 normal-theory ones [A27-11]. The daily figure can differ from the weekly one
  either way: it is higher for 0050–00646, 0050–00642U and 00679B–00642U, lower for 0050–00679B and 0050–00635U
  [A27-11]. Of the five pairs, one daily–monthly gap reaches two monthly standard errors: 00679B–00642U's daily and
  monthly correlations differ by 0.1815 (from the unrounded correlations), which is 2.3 normal-theory standard errors
  (0.0806) and 2.0 plug-in ones (0.0888) [A27-11]. The text names no cause. Monthly correlations from 116 calendar
  months carry normal-theory errors near 0.09 when they are near zero, and plug-in errors up to 0.16 [A27-11]. R1's
  weights on the full sample give 11.49%, 10.55% and 10.02% a year at the three frequencies ($A=242.951$, 51.56 and
  12), and 00642U's share 45.9%, 41.9% and 45.0% [A27-12].
- E6 §5 `mix`: R1: $\mu_p$ is the average of the five annual means 24.16%, 14.87%, −0.97%, 9.26%, 10.53% [A27-08],
  11.57% [A27-47]; $s_p=11.49\%$ (full sample, weights reset daily); variance terms 76.4% of $s_p^2$, covariance terms
  23.6% [A27-13], against 7.2% and 92.8% for U28's book (lm10.md:220, recomputed [A27-31]). Weighted average
  volatility 20.75%, so the diversification ratio (27.7) is 1.81. R2:
  $\mu_p=0.4\times24.16\%+0.2\times14.87\%+0.3\times(-0.97\%)+0.1\times9.26\%=13.27\%$ [A27-47]; $s_p=11.17\%$,
  weighted average 16.97%, ratio 1.52 [A27-17]; U28's book 21.94% over 15.75%, 1.393 [A27-31]. Each ratio exceeds 1,
  as Choueifaty and Coignard's condition says for a long-only book not equivalent to a single asset.
- E7 §6 `split`, R1 at the full-sample $\hat\Sigma$ on the 2,362 joint dates [A27-14, A27-15, A27-16]:
  $A(\hat\Sigma\mathbf w)_i$ = 139.80, 117.05, 17.22, 83.25, 303.13 (%²); dividing by $s_p^2=132.09$ (%²) gives
  $\beta_{i,p}$ = 1.058, 0.886, 0.130, 0.630, 2.295, and the shares $w_i\beta_{i,p}$ are 21.2%, 17.7%, 2.6%, 12.6%,
  45.9% (sum 100.0%). $\mathrm{MRC}_i$ = 12.16%, 10.18%, 1.50%, 7.24%, 26.37% and $\mathrm{RC}_i$ = 2.43, 2.04, 0.30,
  1.45, 5.27 points, summing to 11.49, are computed from unrounded inputs (the text says so: dividing the printed
  covariances by the printed 11.49 moves four MRCs by 0.01). Three splits compared, in a table: Euler's shares (one
  decimal, sum 100.0%); the stand-alone split $w_is_i/\mathbf w^{\top}\mathbf s$, 19.4%, 15.5%, 13.0%, 16.0%, 36.1%
  (sum 100.0%); the variance terms to three decimals, from unrounded inputs, so that they sum, 12.240%, 7.873%, 5.514%, 8.340%, 42.433%, a
  total of only 76.400% (the 76.4% of E6) [A27-16]. Only Euler's parts add up to the book's volatility, 11.49 points,
  and only they price a switch; the stand-alone parts $w_is_i$ add up to the weighted average volatility, 20.75%, and
  the variance terms to 76.4% of the variance [A27-13, A27-15, A27-16]. The slopes of $w_iR_{i,t}$ on $R_{p,t}$ equal
  the shares to about $10^{-16}$, machine precision [A27-18].
- E8 §6 `switch`, R1 on the full sample: move 5 points from 00642U to 00679B. The linear prediction $0.05\,(\mathrm{MRC}_{00679B}-
  \mathrm{MRC}_{00642U})$ is −1.24 points; the exact change by (10.9) is −1.10 points, 11.49% → 10.39% (variance 132.09
  → 107.92 %², linear term −28.59, quadratic +4.42) [A27-19].
- E9 §7 `hedge`, the window through 27 February 2020 (29 January 2018 → 27 February 2020): R1's $s_p=8.13\%$ on that
  window; 00679B correlates −0.067 with the book, $\beta_{i,p}=-0.0944$, $\mathrm{MRC}=-0.0944\times8.13\%=-0.77\%$,
  share $0.2\times(-0.0944)=-1.89\%$; 00642U's share 54.3% [A27-22]. The same 5-point switch lowers $s_p$ to 7.07%.
  00679B's share was negative in 22 of the 36 windows from May 2019 to April 2022; the last of them, through 29 April
  2022, was −0.0023% [A27-20].
- E10 §8 `factor` (X8): the U28 book's beta $\mathbf w^{\top}\boldsymbol\beta=0.807$ (betas 0.507 to 1.207, lm23.md:46).
  Shares of the variance, to three decimals so that they sum: systematic 83.426%, equal to the R-squared on the TAIEX
  price index; residual 16.574%, of which 4.037% comes from residual variances and 12.537% from residual covariances
  (from the unrounded betas and variances; the printed 0.807, 17.82% and 15.75% give 83.4%) [A27-28]. Setting the
  residual covariances to 0 gives 14.73% instead of 15.75% [A27-29]. Semiconductor's share 3.82% = 4.46% systematic −
  0.64% residual: its residual covaries negatively with the rest of the book's residual [A27-30]. The off-diagonal
  residual part is positive, as the residuals' mean correlation, 0.112 (lm23.md:359), leads one to expect; the text
  says "consistent with", since a mean correlation does not fix the sign of a weighted sum.

**Problems plan** (12; MC keys B, C, A, C, A, B; the lab solves 10–12). Stems state the frame or the hypothetical
inputs, simple returns, the divisor, the annualization, the cost rates (commission 0.1425% each side, tax 0.1% on
sales of every E5 fund except 00679B), and the rounding.

1. MC: two funds at 50/50, returns +10% and −5% over a period, no trade; fund 1's weight afterwards. A 0.55 (not
   renormalized). **B** 0.537. C 0.50 (rebalanced) [A27-35].
2. MC: pre-trade weights 0.30, 0.20, 0.15, 0.15, 0.20 in E5's order, target 1/5, E5's rates; the cost as a share of
   wealth by (27.3). A 0.0285% (tax omitted). B 0.0670% (commission on twice the turnover). **C** 0.0385% (exact
   0.0385%) [A27-36].
3. MC: 50/50 bought and held, growth factors 1.40 and 0.80; the book's return. **A** 10.00%. B 5.83% (averaged log
   returns). C 5.67% (an average log return read as a simple return) [A27-37].
4. MC: volatilities 20%, 10%, 30%; correlations $\rho_{12}=0.2$, $\rho_{13}=0.6$, $\rho_{23}=-0.2$; weights 0.4, 0.4,
   0.2; asset 1's risk share. A 36.2% (variance term). B 44.4% (stand-alone). **C** 56.1% [A27-38].
5. MC (no numbers): in a window, a fund held long ($w_i>0$) has a negative risk contribution to the book. Which statement always holds? **A** Moving a small
   weight into it from a fund with a positive $\mathrm{MRC}$ lowers the book's volatility. B Raising its weight lowers
   the volatility at any size. C Selling it lowers the volatility. The solution derives $\partial\mathrm{MRC}_i/\partial w_i=\sigma_i^2(1-\rho_{i,p}^2)/\sigma_p\ge0$, the other weights fixed.
6. MC: E5's monthly 0050–00646 correlation, 0.5521 on 116 calendar months (E5's data, descriptive); its normal-theory
   standard error, to four decimals. A 0.0060 ($T$ for $\sqrt T$). **B** 0.0645. C 0.0928 ($1-\rho^2$ omitted)
   [A27-40]; the solution adds the plug-in value 0.081 [A27-11].
7. Derive $\partial\sigma_p/\partial w_i=(\Sigma\mathbf w)_i/\sigma_p$ for $\sigma_p>0$ from (10.8), Euler's identity
   (27.6), the shares $w_i\beta_{i,p}$ and $\sum_iw_i\beta_{i,p}=1$; show that the Euler share is the variance term plus
   half of each covariance term.
8. Derive the self-financing solution of (27.2) when the signs of the trades are known, then (27.3)'s approximation and
   its bound $\lvert\text{error}\rvert\le(\operatorname{cost}/W^{\mathrm{pre}}_t)(0.1425\%+\max_i\text{tax}_i)\lVert\mathbf f_t\rVert_1$;
   check on E3 (0.0310028% against 0.0310231%) [A27-24].
9. Show that (27.8) holds exactly in sample when each $\beta_i$ is the OLS slope with an intercept (the residuals have
   zero sample covariance with $R_{\text{mkt},t}$, (12.3)); split $\mathrm{RC}_i$ into its two parts; say the sign of the
   error from dropping the residual covariances of an equal-weight book, such as E10's, when they average positive.
10. Same inputs as 4, with annual means 8%, 4% and 10%: the book's $\mu_p$ (6.80%) and its diversification ratio (27.7), $18\%/13.30\%=1.35$; all three contributions; then a switch of 5 points from asset 3 to asset 2: linear −0.96 points,
    exact −0.89 points, $\sigma_p$ 13.30% → 12.41% [A27-38, A27-39]. Python part: check with (10.9).
11. Python: build E5's two frames from the lab's closes, distributions and split, and check them against the lab's
    derived frames; reproduce 2,362 and 2,368, 0.864% on 18 June 2025, the growth factors of A27-06, and the
    correlations of X4 from the ISO weeks and calendar months without the first and last [A27-02–A27-06, A27-10,
    A27-11]. Then say, from §4's sessions, why a daily correlation of these funds can mislead. Say also which of
    the five pairs' daily–monthly gaps reach two monthly normal-theory SEs (only 00679B–00642U's, 2.3; no cause named)
    [A27-11].
12. Python: run (27.2) for R1 from cash of 1 at the close of 4 March 2019 to 8 October 2026 (the through case,
    fixed in advance). Trade at the lab's trade dates, the first session after each month-end signal on which all five
    funds trade, to its per-date targets with the shared cost rates. Print the largest absolute difference from the
    lab's R1 net wealth path (below $10^{-12}$), not the path. Then print the 1 April 2026 trade (X3) and R1's risk
    shares in the 92 windows (X7) [A27-20, A27-24].

**Lab parts** (`build/make_lab27.py`; reads only its `data/`): the five E5 price files, the 0050 and 00679B
distributions and the split file (copied from `data/raw/vol5/` by `data/make_lab_data.py`), `taiex_tr.csv` (TR23's
calendar), the derived files of the shared decision "Labs" (E5's estimation frame and its wealth frame with the traded
flags, as the decision "Labs" of the first revision writes them, R1's and R2's per-date targets, and R1's and R2's net
wealth paths; from `make_lab_data.py`, no copy of `vol5_rules.py`), and `sectors_close_raw.csv`,
`sectors_close_repairs.csv` (U28 and the TAIEX price index, as LM23's lab builds them). Parts: 1 both frames from raw
files and their checks, against the derived frames (P11); 2 the span and the drift (E1, X2); 3 the recursion: E2, E3,
X3, R1 and R2 re-implemented from their per-date targets and checked against their net wealth paths, printing only the largest difference (P12); 4
asynchronous closes (E5, X4) with both SEs and the funds' kurtosis; 5 $\hat\Sigma$, $s_p$, (10.6) and the ratio (E6,
X5); 6 risk splits, the slope check and the switch (E7, E8, X6); 7 the 92 windows (E9, X7); 8 U28's factor split (E10,
X8); 9 Problems 10–12. Extension (*descriptive*, stability check): R2's risk shares in the 92 windows: 0050's runs from
55.3% to 72.1% and exceeds 70% in 13 windows, against its 40% of the money [A27-45]; a closing sentence says that
turning shares into targets is LM31's subject. Labs write plain "LM30", "LM31" and "LM34", never `[[…]]`.

**Cross-module tags** (the later modules that cite each, from the cross-check's tag table of the revised briefs, Y1;
decision C8):

- (27.1) $R_{p,t}=\mathbf w_{t-1}^{\top}\mathbf R_t+(1-\mathbf 1^{\top}\mathbf w_{t-1})\,r_f/A_{\mathrm w}$ and
  $w^{\mathrm{drift}}_{t,i}=w_{t-1,i}(1+R_{i,t})/(1+R_{p,t})$, with $\mathbf w_{t-1}$ each fund's value over wealth after $t-1$'s close, summing to 1 for R1–R7, to R8's exposure for R8 and to 0 before the first purchase;
  cash earns $r_f$ when $\mathbf 1^{\top}\mathbf w_{t-1}<1$, and a negative cash balance ($\mathbf 1^{\top}\mathbf w_{t-1}>1$)
  pays [[LM31]]'s financing rate in place of $r_f$ (as `vol5_rules.wealth_path` does); for weights summing to 1 the
  cash term vanishes and this is (8.3); needs $1+R_{p,t}>0$, otherwise the book is ruined at $t$ (LM29, LM30, LM31,
  LM32, LM33, LM34, LM35).
- (27.2) $W^{\mathrm{pre}}_t=W_{t-1}(1+R_{p,t})$; on a trade date $W_t=W^{\mathrm{pre}}_t-\operatorname{cost}\big(W_t\mathbf f_t
  -W^{\mathrm{pre}}_t\mathbf w^{\mathrm{drift}}_t\big)$ and $\mathbf w_t=\mathbf f_t$, otherwise $W_t=W^{\mathrm{pre}}_t$ and
  $\mathbf w_t=\mathbf w^{\mathrm{drift}}_t$; $\operatorname{cost}(\mathbf x)=0.1425\%\lVert\mathbf x\rVert_1+\sum_i\text{tax}_i
  \max(0,-x_i)$; one solution when $(0.1425\%+\max_i\text{tax}_i)\lVert\mathbf f_t\rVert_1<1$, with
  $0<W_t\le W^{\mathrm{pre}}_t$ when selling the whole book would cost less than $W^{\mathrm{pre}}_t$ (LM29, LM30, LM31,
  LM32, LM33, LM34, LM35).
- (27.3) $\mathrm{TO}_t=\tfrac12\lVert\mathbf f_t-\mathbf w^{\mathrm{drift}}_t\rVert_1$ and
  $\operatorname{cost}/W^{\mathrm{pre}}_t\approx0.285\%\,\mathrm{TO}_t+\sum_i\text{tax}_i\max(0,w^{\mathrm{drift}}_{t,i}-f_{t,i})$,
  error at most $(\operatorname{cost}/W^{\mathrm{pre}}_t)(0.1425\%+\max_i\text{tax}_i)\lVert\mathbf f_t\rVert_1$ (LM29, LM31,
  LM34, LM35).
- (27.4) $\mu_p=\mathbf w^{\top}\boldsymbol\mu$, $\sigma_p^2=\mathbf w^{\top}\Sigma\mathbf w$ for $R_p=\mathbf w^{\top}\mathbf R$ with
  constant $\mathbf w$; annual $A\mu_p$ and $\sqrt A\,\sigma_p$, conventions on simple returns (the variance rule is exact only for log returns on uncorrelated periods, (19.7); lm19.md:353, 368–369) (LM28, LM29, LM30, LM32).
- (27.5) $\Cov(R_i,R_p)=(\Sigma\mathbf w)_i$, $\beta_{i,p}=(\Sigma\mathbf w)_i/\sigma_p^2$, $\sum_iw_i\beta_{i,p}=1$
  ($\sigma_p>0$) (LM28, LM29, LM30, LM31, LM35).
- (27.6) for $\sigma_p>0$: $\mathrm{MRC}_i=\partial\sigma_p/\partial w_i=(\Sigma\mathbf w)_i/\sigma_p$,
  $\mathrm{RC}_i=w_i\mathrm{MRC}_i$, $\sum_i\mathrm{RC}_i=\sigma_p$, $\mathrm{RC}_i/\sigma_p=w_i\beta_{i,p}$ (LM28, LM31:
  decision A6).
- (27.7) $\mathbf w^{\top}\mathbf s/s_p\ge1$ for $\mathbf w\ge\mathbf 0$ with $s_p>0$, equal to 1 only when every correlation among held
  assets is 1 ((8.11)); the ratio is Choueifaty and Coignard's diversification ratio (2008, eq. (1), p. 41), which
  exceeds 1 for a long-only book not equivalent to a single asset (used within LM27; no later brief cites it).
- (27.8) $\sigma_p^2=(\mathbf w^{\top}\boldsymbol\beta)^2\sigma_{\text{mkt}}^2+\mathbf w^{\top}\Sigma_{\mathrm{res}}\mathbf w$ and
  $\mathrm{RC}_i=\big[w_i\beta_i(\mathbf w^{\top}\boldsymbol\beta)\sigma_{\text{mkt}}^2+w_i(\Sigma_{\mathrm{res}}\mathbf w)_i\big]/\sigma_p$,
  when residuals are uncorrelated with the factor (exact in sample for OLS with an intercept) (LM30, LM35).

**Pitfalls to pre-empt.**

- A joined frame's dates (PITFALLS §3): a statistic of joint returns uses the estimation frame; wealth, drift and costs
  the wealth frame; one fund's statistic its own dates. Name the frame next to every count and $A$.
- Averaging log returns across funds understates a book's return ((1.14), E1); compounding weights across days needs
  the drift, not the target weights.
- Turnover: one-way is half the 1-norm; a script that adds buys and sells and calls it turnover doubles it; the cost
  uses the 1-norm (both sides pay commission), the tax only the sales (Problem 2's distractor B).
- Positions in money are $W^{\mathrm{pre}}_t\mathbf w^{\mathrm{drift}}_t$, since LM8's $\mathbf h$ counts units; the
  post-trade wealth is $W_t$ (AUTHORING §6).
- A gradient entry is not a share (lm10.md:425): $2(\Sigma\mathbf w)_i$ prices a marginal change; the share needs $w_i$.
  Volatilities do not add (lm10.md:220); Euler's contributions add to $\sigma_p$ because $\sigma_p$ is homogeneous of
  degree 1 (and differentiable where $\sigma_p>0$).
- A negative contribution is a hedge only at the margin; its $\mathrm{MRC}$ grows with its weight (Problem 5).
- Risk shares are plug-in estimates: 00642U's 45.9% ranges from 32.7% to 54.3% across windows (X7); the module never
  calls a share a forecast.
- Daily correlations of funds priced on different sessions (E5): compare frequencies with their standard errors, state
  what each error assumes (independent periods; finite fourth moments for the plug-in one), and do not name a cause the
  data do not show (the shared decision's "Unexplained extremes" rule).
- Printed parts and products: every column of X3, the end weights of X2 and the variance shares of E7 and X8 sum as
  printed; E3's weights carry the digit that its turnover needs; E7's MRC, RC and three-decimal variance terms say "from unrounded inputs"; E5's
  00679B–00642U gap says "from the unrounded correlations" (the printed −0.18 and −0.36 give 0.18), and its multiples
  of the standard errors follow from the printed gap and errors.
- Statements about "the largest" or "only one" gap hold for the five pairs E5 shows, and E5 says so: over all ten pairs
  00646–00679B has a larger daily–weekly gap and 00635U–00642U a second daily–monthly gap of two monthly normal-theory
  errors [A27-11], as a reader who computes the full matrix in Lab Part 4 would find.
- R1's own results: the module prints R1's trades, never its net wealth, growth, turnover total or costs total (LM34);
  E3 is scaled to a NT\$10 million book so that R1's wealth level stays unprinted.
- Price indices in U28: only their covariances are used; under (23.8)'s assumption that dividends accrue evenly, the dividend gap moves the intercepts, not the covariances; every caption says price indices.
- Weekly and monthly statistics drop the first and last periods, complete or not; the caption says so (AUTHORING §7).

**Curriculum guidance carried** (plans/vol-5.md's table):

- V–VI tie estimation, constraints, costs and hygiene (g:25): costs enter the wealth recursion here, before any
  optimizer; R1's windows show the estimate moving.
- Each module says which layer it adds (g:30): the introduction's first paragraph ("Layer added" above).
- Three outcome levels (g:54–58) and taught/practised/assessed (g:124): the Outcomes table.
- Decision flow, LM27's part (g:69–85): data visible at the signal's close, the trade at the next close, trades from
  current (drifted) holdings, costs and cash in the wealth recursion (27.1)–(27.3).
- Wealth ≤ 0 ends log growth (g:94): (27.1)'s domain and ruin rule; R1 and R2 cannot reach it (long-only, fully
  invested, every $R_{i,t}>-1$), which §2 says in one sentence; LM35 shows a book that can.
- Fix windows, frequency, limits, costs and criteria before evaluation (g:111): the hygiene note states that the
  through case was fixed on 2026-10-24; LM27 evaluates nothing.
- Not carried here: drawdown definitions (LM32), checkpoints (LM33, LM35), volatility targeting (LM31).

**Stage 4 for earlier modules.** `leads` gain 27 in lm01.md:6 ((1.12)–(1.14)), lm03.md:6 (the working rule,
lm03.md:266–271), lm19.md:6 (weekly and monthly returns, (19.3), (19.7)) and lm20.md:6 (Problem 6's standard error),
as decision G lists; lm07, lm08, lm09, lm10, lm11, lm12, lm16 and lm23 already list 27. No wording change in published
modules.

**Sources** (as the source checks and the SOURCES drafts of 2026-10-24 record them, with the version read and the
location; paraphrased, none quoted beyond a phrase; bibliographic data from Crossref unless another record is named):

- Maillard, S., T. Roncalli and J. Teïletche (2010). "The Properties of Equally Weighted Risk Contribution Portfolios."
  *Journal of Portfolio Management* 36(4): 60–70 (Crossref: print and online 31 July 2010). DOI
  10.3905/jpm.2010.36.4.060. The journal text is not openly available and was not read. Read in the authors' working
  paper "On the properties of equally-weighted risk contributions portfolios" (first version June 2008, this version
  May 2009; thierry-roncalli.com/download/erc.pdf, 23 pages; read by the LM27 drafter and verified by the second source
  hunt): §2.1, p. 4, defines the marginal risk contribution as $\partial\sigma/\partial x_i$ and the total contribution
  as $x_i\,\partial\sigma/\partial x_i$, the contributions summing to $\sigma$; footnote 1 on p. 4 (the second note so
  numbered) says that $\sigma$ is homogeneous of degree 1 and so satisfies Euler's theorem. Used for (27.6) and the
  Deep Dive. The text cites the journal article at article level with the working paper's section and page, and
  prints no JPM page or equation number.
- Qian, E. (2006). "On the Financial Interpretation of Risk Contribution: Risk Budgets Do Add Up." *Journal of
  Investment Management* 4(4): 41–51, Fourth Quarter 2006; no DOI. joim.com's 2006 listing places it in Vol. 4, No. 4
  (the listing prints no pages, and the text needs a login). The pages are printed on the first page of PanAgora's
  copy (read by the LM27 drafter, by local text extraction) and, a secondary source, in the reference list of Haugh,
  Iyengar and Song, *Journal of Computational Finance* 21(2): 29–60 and DOI 10.21314/JCF.2017.329 as the copy at
  columbia.edu prints them (that DOI is not registered: Crossref and doi.org, not found, 2026-10-25). Fact used, from
  PanAgora's copy: under normality a component's expected share of a portfolio loss is its percentage risk
  contribution plus a term that shrinks as the loss grows (his equation (3) and the paragraph after it), for the
  standard deviation and, with a Cornish–Fisher expansion, for VaR. The working paper is SSRN 684221, DOI
  10.2139/ssrn.684221 (Crossref: posted content, 2005). Used in §6 and in the Leaves sentence on VaR contributions.
- Choueifaty, Y. and Y. Coignard (2008). "Toward Maximum Diversification." *Journal of Portfolio Management* 35(1):
  40–51, Fall 2008. DOI 10.3905/jpm.2008.35.1.40. Read by the source check in the JPM layout (hosted by TOBAM).
  Equation (1), p. 41, defines the diversification ratio (their $\Sigma$ there is the vector of volatilities, not a
  covariance matrix). The sentence below it glosses the ratio in words that the book does not reuse unquoted. Also on p. 41: a long-only portfolio's ratio is strictly above 1 unless the portfolio is
  equivalent to a single asset, when it equals 1. Used in §5 for (27.7)'s name and that condition (decision on the
  first revision, "Sources"). (27.7) is written in the book's notation, $\mathbf w^{\top}\mathbf s/s_p$, and derived
  from (8.11); their symbols are not copied, and §5 states (27.7) in the book's notation without their p. 41 gloss.
- Burns, P., R. F. Engle and J. J. Mezrich (1998). "Correlations and Volatilities of Asynchronous Data." *Journal of
  Derivatives* 5(4): 7–18. DOI 10.3905/jod.1998.408000. Abstract only (OpenAlex's copy): when markets close at
  different times, returns look predictable and correlations are understated; the authors synchronize the returns by
  estimating asset values while markets are closed. Text not read; used for that one sentence in §4, as the abstract
  states it.
- Yuanta fund pages, `https://www.yuantaetfs.com/product/detail/<code>/Basic_information`, read 2026-10-24 by the LM27
  drafter and again by the SOURCES draft (HTTP 200; the fields are in the server-rendered HTML): 0050 臺灣50指數, FTSE
  TWSE Taiwan 50 Index, 50 constituents, listed 2003-06-30; 00646 標普500指數, S&P 500 Index, listed 2015-12-14; 00635U
  標普高盛黃金超額回報指數, S&P GSCI Gold Excess Return Index, on COMEX gold futures, no distribution, listed
  2015-04-15; 00642U 標普高盛原油增強超額回報指數, S&P GSCI Crude Oil Enhanced Excess Return, on NYMEX WTI futures, no
  distribution, listed 2015-09-07. 00679B (ICE US Treasury 20+ Year) is in SOURCES. The visible text of none of these
  pages mentions a currency hedge, an exchange rate or a fund currency (their other tabs were not read), so the text
  says nothing about hedging. TWSE's ETF e添富 fund pages (read 2026-10-24) give the same indices and classify 0050 as
  台股ETF, 00646 as 國外股票ETF and 00635U and 00642U as 期貨ETF.
- TWSE, for 0050, 00646, 00635U and 00642U (TWSE-listed: TWSE's ISIN page and `STOCK_DAY_ALL`, SOURCES): the trading
  system page (SOURCES: the 09:00–13:30 session, closing call auction from 13:25) and the Operating Rules (營業細則,
  version 115.09.24 as read on 2026-10-24; the page carried 115.10.19 on 2026-10-31, Art. 3 unchanged), Art. 3, trading time 09:00–13:30 (read 2026-10-24), for "the funds close at 13:30".
- TPEx, for 00679B (TPEx-listed from 2017-01-17: TPEx's listing notice 證櫃債字第10600009612號 of 2017-01-13, its ETF
  list and TWSE's ISIN page, SOURCES; read 2026-10-25 by the TPEx source check and its verifier, anonymous requests):
  the Business Rules (證券商營業處所買賣有價證券業務規則), Art. 40 item 一, trading time 09:00–13:30 for stocks on the
  等價成交系統 (last amended 2014-09-23, in item 二 only, so the hour held over E5's span), applied to ETFs by the ETF
  rules (指數股票型基金及主動式交易所交易基金受益憑證買賣辦法) Art. 4 ¶2; TPEx's trading system page (交易系統簡介,
  `Last-Modified` 26 March 2026): matching 09:00–13:30, a call auction from 13:25 to the 13:30 close. Used in §4 for
  "both markets close at 13:30".
- TWSE's ETF overview page (ETF 總覽, `Last-Modified` 22 October 2026, read 2026-10-24): a futures-trust ETF on
  a foreign futures index is valued on European and US futures, so the time difference is a risk; used in §4 for that
  sentence only.
- NYSE, [Holidays & Trading Hours](https://www.nyse.com/markets/hours-calendars), read 2026-10-24 by the LM27 drafter
  and again by the SOURCES draft: the core trading session runs 9:30 a.m. to 4:00 p.m. ET (the page lists early closes
  at 1:00 p.m. on named days). The page says nothing about Taipei time: the offsets come from the IANA time-zone data
  (Python `zoneinfo`, tzdata 2026.5, run 2026-10-24), with Taipei at UTC+8 without daylight saving, so 4:00 p.m. in
  New York is 04:00 in Taipei in US summer time and 05:00 otherwise. Used in §4.
- The cost model: plans/vol-5.md's "Cost model" decision, each fund under its own market's rules; LM34 owns and
  prints its official sources (TWSE Operating Rules Art. 94 for the four TWSE funds; for 00679B, TPEx's Business Rules
  Art. 64, ¶1–¶3 unchanged since 2008-02-12, applied to ETFs by its ETF rules' Art. 15 ¶1; the Securities Transaction
  Tax Act Art. 2 item 2 and Art. 2-1, whose 上市及上櫃 covers a TPEx bond ETF; the Ministry of Finance's ruling
  台財稅字第09700161260號 of 2008-08-11 on futures-trust fund certificates; TWSE's ETF rules page; the Ministry's 財政統計通報
  No. 21). LM27 cites them by pointer only.
- Checked and not used (bibliographic data only, Crossref): Litterman, R. (1997), "Hot Spots™ and Hedges," *Journal of
  Portfolio Management* 23(5): 52–75, DOI 10.3905/jpm.1996.052 (Crossref dates the print issue 1997-08-31 and the
  online version 1996-12-31; text not read); Sharpe, W. F. (1963), "A Simplified Model for Portfolio Analysis,"
  *Management Science* 9(2): 277–293, January 1963, DOI 10.1287/mnsc.9.2.277 (abstract only; the single-index model is
  LM30's to cite, and SOURCES lists it there); Scholes, M. and J. Williams (1977), "Estimating Betas from Nonsynchronous
  Data," *Journal of Financial Economics* 5(3): 309–327, December 1977, DOI 10.1016/0304-405X(77)90041-1 (text not
  read).
- Kept out, as the source checks require: Choueifaty and Coignard's symbols (their $\Sigma$); any JPM page or equation
  number of Maillard et al.; Burns et al. beyond their abstract; a fixing time for the futures funds' indices; any
  statement on currency hedging; SPY's correlations (decision on LM27).

**Chinese terms.** From plans/vol-5.md's list: 投資組合 (portfolio), 共變異數矩陣 (covariance matrix), 交易成本
(transaction cost), 週轉率 (turnover; 管理學名詞 writes 周轉率 for "turnover rate", 會計學 and 電子計算機名詞 週轉率), 無風險利率
(risk-free rate). Already printed by the book: 再平衡 (rebalancing, lm08.md:403), 買進持有 (buy-and-hold) and 漂移 (drift,
lm09.md:473), 等權重 (equal weights, lm10.md:391), 權重 (weights, Volume IV; 統計學名詞 lists 權數), 峰態 (kurtosis, LM14,
LM19), 市場模型 (market model, LM23), 殘差 (residual, LM23). New terms, as the LM27 drafter recorded them and the fresh
樂詞網 pass of 2026-10-24 confirmed them (481 query strings in all listings, 統計學名詞 and 數學名詞, 374 of them also in
管理學名詞; 1,817 searches, anonymous requests), with that pass's additions:

| English | 樂詞網 (listing) | Book |
|:--|:--|:--|
| rebalancing; rebalance | 重新平衡 (管理學名詞-會計學, "rebalancing"); 再平衡 (電子計算機名詞, "rebalance"); 再平衡；重新平衡 (一般性常見術語) | 再平衡 (as lm08.md:403) |
| systematic risk | 系統性風險 (統計學名詞); 系統風險 (管理學名詞) | 系統性風險 |
| idiosyncratic risk; unsystematic risk | 特質風險; 非系統風險 (管理學名詞) | not used: the module says 殘差 (residual) |
| single index model | 單一指標模型 (統計學名詞) | 單一指標模型 |
| factor model | 因子模型 (統計學名詞, 管理學名詞) | 因子模型 |
| variance decomposition | 變異數分解 (統計學名詞) | 變異數分解 |
| homogeneous function; positively homogeneous | 齊性函數; 正齊次的 (數學名詞) | 一次齊性函數 (homogeneous function of degree 1), composed |
| Euler's theorem | no entry in 統計學名詞, 數學名詞 or 管理學名詞 (數學名詞 writes Euler數, Euler常數); 歐拉定理 in 測量學, 測繪學辭典, 地理學名詞-測繪學名詞, 海洋地質學 and 電子計算機名詞; 物理學名詞 歐拉勒定理 | Euler 定理, with the space the book puts between a Latin name and Chinese (Mahalanobis 距離, LM16) |
| diversification | 多樣化 (統計學名詞); 多角化 (管理學名詞, also 市場學); 風險分散極限原則 ("limit of diversification"), 充分分散風險的投資組合 ("well-diversified portfolio") and 完全分散風險的投資組合 ("completely diversified portfolio") (管理學名詞); 風險分化 (經濟學) | 風險分散, the management listing's compounds (多角化 is a firm's business lines) |
| risk contribution; marginal contribution; risk decomposition; risk attribution | no entry; contribution rate 貢獻率 (統計學名詞) | 風險貢獻, 邊際風險貢獻: the book's own forms, English in every box |
| commission | 佣金 (管理學名詞, 管理學名詞-會計學); 傭金，手續費 (會計學) | 手續費 (commission), the brokers' word |
| securities transaction tax | 證券交易稅 (管理學名詞, for four English headwords; 會計學, for "transfer tax (on stock)") | 證券交易稅 |
| exchange traded fund | 指數股票型基金 (統計學名詞, 管理學名詞) | 指數股票型基金 |
| self-financing | 自籌資金 (管理學名詞, a firm's own funds) | 自我融資 (self-financing), composed: the listing's sense differs |
| asynchronous | 非同步的；異步的 (數學名詞) | 非同步 |
| hedge | 避險 (管理學名詞) | 避險 |

**Open before Stage 2.** None: items 1 and 2 closed in the second revision, item 3 in the third, and the fresh check
of the whole of Stage 1 (2026-10-31) opened none (its fixes are in the text, and its seven extended anchor rows were reproduced by the fresh verification of 2026-10-31).

1. **The ratio (27.7)'s name.** Closed by the decision on the first revision ("Sources"): §5 names the ratio the
   diversification ratio and cites Choueifaty and Coignard (2008, eq. (1), p. 41) in the book's notation; "the ratio
   exceeds 1" carries their condition, a long-only book not equivalent to a single asset (E6, (27.7), Sources).
2. **The last ISO week.** Closed by the decision "Weeks and months": the first and last week and month are dropped,
   complete or not. The Data role, X4, the Pitfalls and A27-10 word the rule so, and the Departures no longer list it.
3. **The shared decision's parenthesis.** Closed by the decisions on the third revision: the shared decision "Timing
   of E5" quotes A27-11's figures (simple returns, the first and last period dropped), and its note on the superseded
   first figures is dropped. A27-46, which checked that note, is withdrawn; its ID stays so that later IDs do not move.

Settled by the decisions of 2026-10-24 and 2026-10-25 (closed): the recursion's notation ($W^{\mathrm{pre}}_t$,
$A_{\mathrm w}$ book-wide, B2; the shared "Costs" sentence rewritten); what LM27 prints of R1 (two trades and the June 2025 span; the
annual totals are LM34's, A2 and A5); the full-sample $\hat\Sigma$ on the estimation frame with the 92 windows as a
stability check, and weekly $A=51.56$ by LM19's count (D); the timing correlations (C1: the shared decision quotes
A27-11, without its former note; A27-46 withdrawn, item 3); the timing evidence (per-module decision: sessions and
frequencies, no SPY figure; both listing markets named, "Listing markets"); the widget's three matrices (E; anchored,
A27-33, A27-48, A27-49); the retrieval date of E5's files (`data/README.md`: 2026-10-24); the split day's return
without a symbol (B6); R1's first-window shares as LM27's (A4); the year count from the close before the first return
(C7); the monthly-gap sentence of E5 and the "adds up" sentence of E7 (decisions on LM27, second recomputation); E5's
two gap sentences scoped to the five pairs shown, the 00679B–00642U gap "from the unrounded correlations",
Choueifaty and Coignard's gloss not reused (it is their own sentence on p. 41; fresh check of Stage 1), and R1's and R2's net wealth paths in the lab's files
(decisions on LM27, third revision); NEAR flags in the anchors table only (C11); echoes
at the owner's ID and precision (C12: A30-12, A30-24, A30-42); both E5 frames in the lab ("Labs"); the tag users and
Leads (Y1); the Chinese terms (the fresh pass). Kept as this brief proposed, since no decision changed them: 風險分散
and Euler 定理, and the factor split's depth (the exact in-sample (27.8) with the full residual covariance, the
per-asset split of $\mathrm{RC}_i$, the diagonal-residual shortcut once; no factor model of E5). The survivorship
pointer that LM34's brief left to this brief (its O11) is taken: §4's "Uses before taught" sentence.

Departures from the spine or the shared decisions, with evidence: the spine's equity-tax-only proviso is superseded by
the cost model; the prerequisite list (the spine's (11.2) is not used; LM1, LM3 and LM20 are added: LM20's Problem 6
supplies the correlation's standard error); the widget's three matrices (decision E); one statistic beyond the spine,
the funds' raw kurtosis [A27-50], which states the plug-in standard error's condition (the second recomputation's
Minor 6). R1's first-window risk shares stay with LM27 under decision A4 as amended, so they are no departure.

## LM28 Mean–Variance Optimization

Stage 1 brief, drafted 2026-10-24 from the editor's spine (`plans/vol-5.md`, "### LM28 Mean–Variance Optimization",
commit d05750b) and the shared decisions above it; revised the same day to the editor's decisions on the briefs, on
the first revision and on the second recomputation and cross-check (`plans/vol-5.md`), and to the two independent
recomputations of its anchors; finished on 2026-10-25 to the third revision's verifier and the decisions on the third
revision; revised on 2026-10-31 to the fresh check of the whole of Stage 1 (its verifier's confirmed items, with the
editor's choices on two-fund separation and E8's counterfactual), whose changed anchor rows were reproduced by the fresh verification of 2026-10-31. Every number carries its anchor ID at first appearance; `data/vol5_anchors_lm28.py`
prints them all (46 rows, `## LM28` of `plans/vol-5-anchors.md`). Numbers quoted from published modules carry their
file:line instead; a number another brief owns carries the owner's anchor ID (decision C12).
The script imports `vol5_series.frames`, `vol5_rules.schedule`, `WINDOW`, `RF`, `cov0`, `minvar` (only to compare
it with LM28's closed form) and the solver options; it recomputes no rule of R1–R8 and prints no rule statistic.

**Prereq:** `[7, 8, 9, 10, 11, 12, 16, 20, 23, 27]`. What each supplies (tags rechecked in `src/lmNN.md`, 2026-10-24):

- LM7: the Lagrangian with its signs, $\mathcal L=h-\lambda(\psi-b)$ (lm07.md:310, Glossary lm07.md:765), (7.5)
  and the shadow price (7.6) (lm07.md:309, 323); the two-asset minimum variance (7.7)–(7.9) (lm07.md:374–382),
  $\lambda^*=2\sigma^2_{\min}$ and "each asset has the same covariance with the portfolio" (lm07.md:388–390); the
  2017–2021 inputs and results reused by problem 9 (lm07.md:409, 412–414); the tangency (7.10), $\mathrm{SR}^*$ (7.11),
  the Kelly fractions (7.12) and $\mathbf f^*=L^*\mathbf w^{\text{tan}}$ (lm07.md:461, 465, 479, 484); "when the
  denominator of (7.10) is near zero the tangency weights explode" (lm07.md:469); the case pattern, predicted 9.22%
  against realized 12.44% (lm07.md:38–40) and its resolution by (7.9) (lm07.md:443–446); the convexity remark that a
  convex objective with a linear constraint makes a candidate global (lm07.md:312); KKT (7.13), stated without proof,
  cited only as LM29's starting point.
- LM8: (8.3) $R_p=\mathbf w^{\top}\mathbf R$ (lm08.md:120), (8.4) exposures (lm08.md:130), net and gross exposure
  (lm08.md:178–180). (8.11), which the Volume II plan listed for LM28 (`plans/vol-2.md:261–262`), is carried by LM27's
  diversification bound (27.7) and is not cited here (the drafter's proposal, accepted).
- LM9: (9.4) Cramer's rule and (9.5) the 2×2 inverse (lm09.md:202, 285), for the frontier's 2×2 system and problem 9;
  (9.6) invertibility (lm09.md:295).
- LM10: (10.4) $s_p^2=\mathbf w^{\top}\hat\Sigma\mathbf w$ (lm10.md:181), the basis of §6's exact split; (10.8)
  gradients (lm10.md:403); (10.9) the exact expansion (lm10.md:409), which proves (28.1) and (28.3); the theorem "PSD ⇔
  convex, PD ⇔ strictly convex" (lm10.md:436–437, the theorem box); the equal-weight U28 volatility 15.75% (lm10.md:36).
- LM11: (11.4) (lm11.md:184) for KC §2's bounds on $\sigma_{\min}$; (11.8) $\hat\Sigma^{-1}\mathbf b$ by eigenvectors
  (lm11.md:421) for §5's mechanism; U28's halves and the cosine 0.690 of their solutions of $\hat\Sigma\mathbf x=\mathbf 1$
  (lm11.md:467), which E2 re-reads as minimum-variance portfolios; $\kappa(\hat\Sigma^{(1)})=126.05$ (lm11.md:468).
- LM12: a symmetric matrix is positive definite exactly when it has a Cholesky factor (the theorem and (12.8),
  lm12.md:402–411; LM10's table of tests, lm10.md:273, gives only the "if" direction), for §2's pitfall, KC §7 and the
  widget's check.
- LM16: (16.4) (lm16.md:220): $\sigma_p^2=\mathbf w^{\top}\Sigma\mathbf w\ge0$ and $\Sigma$ PSD in a model.
- LM20: (20.2) $\operatorname{SE}(A\bar R)=A\sigma/\sqrt T$ (lm20.md:114) and $\operatorname{SE}(s)\approx
  \sigma\sqrt{(\operatorname{Kurt}-1)/(4T)}$ (lm20.md:362, unnumbered; "probably too small" under clustering,
  lm20.md:376), for §5's standard errors of means and §6's realized volatilities.
- LM23: the CAPM's equation $\E[R_i]-r_f=\beta_i(\E[R_{\text{mkt}}]-r_f)$ (lm23.md:285, unnumbered), which §4 meets as
  (28.6)'s beta identity (A28-45).
- LM27 (brief, by tag): E5, its funds and its two frames (their counts are LM27's A27-01 to A27-03, which A28-01
  echoes); (27.4) $\mu_p$, $\sigma_p^2$ and annualization with $A$; (27.5)
  $\operatorname{Cov}(R_i,R_p)=(\Sigma\mathbf w)_i$ and $\beta_{i,p}$; (27.6) $\mathrm{RC}_i/\sigma_p=w_i\beta_{i,p}$.
  E1 applies (27.5)–(27.6) at $\mathbf w^{\mathrm{mv}}$ (every $\beta_{i,p}=1$, every risk share equals its weight)
  and §4 applies (27.5) at $\mathbf w^{\mathrm{tan}}$ (decision C8).

**Leads:** `[29, 30, 31, 32, 33, 34, 35, 43]` (each of LM29–LM35 lists 28 among its prerequisites). The tag users
are the cross-check's table (decisions C8 and Y1): LM29 cites (28.1), (28.2) and (28.4)–(28.8), for the long-only
forms of R3 and R4; LM30 cites (28.2), (28.3), (28.6), (28.8) (inverted for Black–Litterman's
$\mathbf e_{\mathrm{eq}}=\delta\Sigma\mathbf w_{\mathrm{ref}}$) and (28.9), and takes the first window's estimates as
its simulation's model; LM31 cites (28.2), the minimum-variance end of its ordering; LM35 cites (28.1), for its
reverse stress test. LM32–LM34 cite the rules R3 and R4, which LM28 defines in unconstrained form (shared rule "Leads
and tags"). LM43 is a lead by §4's forward pointer: the N-asset Kelly identity is LM43's.

**Forward links honoured.**

| Earlier text | Promise | Kept in |
|:--|:--|:--|
| lm07.md:457 | the tangency portfolio has the highest Sharpe ratio, "where a line from the risk-free rate touches the set of risky portfolios ([[LM28]])" | §4: (28.6) proved for $N$ assets, the CML (28.7) drawn on X2, and the condition under which the touching point exists ($r_f<\mu_{\mathrm{mv}}$; it fails in 22 of the through case's 92 windows [A28-23]) |
| lm10.md:446 | "Finding the portfolio of least variance is the subject of [[LM28]]; this module stops at the gradient" | §2: (28.1)–(28.3) from LM10's (10.8) and (10.9), with existence and uniqueness |
| lm10.md:449 (中文) | 二次函數是凸函數若且唯若矩陣半正定，「這是 [[LM28]] 與 [[LM29]] 求解最佳化的基礎」 | §2: uniqueness from LM10's theorem (PD ⇒ strictly convex) and directly from (28.3); §2's 導讀 says it in Chinese; general convexity is LM29's |
| lm11.md:419 | "Rescaled to sum to 1, the solution of $\hat\Sigma\mathbf x=\mathbf 1$ is the minimum-variance portfolio of [[LM28]]" | §2: (28.2) is that rescaling; E2 re-reads LM11's U28 halves as minimum-variance portfolios (the cosine 0.690 is unchanged by rescaling) |

The grep of `src/*.md` and `src/pages/*.md` for `[[LM28]]` finds exactly these four lines; plain "LM28" in
`build/make_lab*.py` finds none. Two published lines without a pointer are honoured too: lm07.md:469 (weights explode
when the denominator of (7.10) nears zero: §4's pitfall and §5's (28.9), with the 2024-03-29 window, gross 29.1 [A28-23]) and
the syllabus line (`src/syllabus.yaml:76`: "Lagrangian derivation, global minimum variance, the frontier, tangency
and the CML"). The plans' tag lists promise LM28 (8.3), (8.11), (9.4), (9.5), (10.4), (10.8), (11.4), (11.8) and (16.4)
(`plans/vol-2.md:259–262, 388, 479, 560`; `plans/vol-3.md:1525–1527`); all but (8.11) are used as listed above.

**Outcomes** ("After this module you should be able to:"; levels as `plans/vol-5.md`, "Outcome levels"):

1. [D] derive the minimum-variance portfolio of $N$ assets from the Lagrangian, and state when it exists and is unique
2. [D] derive the frontier as a parabola in variance and mean, and explain two-fund separation
3. [D] derive the tangency portfolio and the capital market line, and state when the tangency portfolio exists
4. [C] compute a risk-averse investor's exposures beside a riskless asset, and relate them to the tangency portfolio
5. [C] compute how tangency weights respond to one mean, and compare that change with the mean's standard error
6. [C] split the gap between predicted and realized volatility into a moved minimum and a weight error
7. [C] compute frontier portfolios in NumPy from linear systems, and check them and their multipliers with cvxpy
8. [U] explain why unconstrained mean–variance weights are in-sample estimates, not recommendations

(`build/qa/style.py`'s count, formulas as one token: 18, 14, 16, 16, 17, 16, 16, 10; average 15.4; outcome 1 reads "of
$N$ assets", decision on Y6.) Taught, practised, assessed
(REVIEW_PROMPT item 10): 1 — §2, E1, E2, KC §2, problems 1, 2, 7, 9; 2 — §3, E3, E4, KC §3, problems 3, 8(a), 8(b), 8(d); 3 — §4, E4,
KC §4, problems 4, 6, 8(c); 4 — §4, E5, problem 5; 5 — §5, E6, X3, KC §5, problem 10; 6 — §6, E7, E8, X4, KC §6,
problem 12; 7 — §7, E9, KC §7, problem 11; 8 — §5's and §6's pitfalls, the summary, problems 6 and 10(c).

**Owns.**

- The equality-constrained minimum-variance problem in matrix form (28.1), with LM7's signs:
  $\min\mathbf w^{\top}\Sigma\mathbf w$ subject to $K\mathbf w=\mathbf b$ ($K$ is $k\times N$ of full row rank,
  $\Sigma$ positive definite); the solution $\mathbf w^*=\Sigma^{-1}K^{\top}(K\Sigma^{-1}K^{\top})^{-1}\mathbf b$, the
  value $\mathbf b^{\top}(K\Sigma^{-1}K^{\top})^{-1}\mathbf b$, the multipliers $\boldsymbol\lambda=2(K\Sigma^{-1}
  K^{\top})^{-1}\mathbf b$; and the exact identity $\mathbf w^{\top}\Sigma\mathbf w=\mathbf w^{*\top}\Sigma\mathbf w^*
  +(\mathbf w-\mathbf w^*)^{\top}\Sigma(\mathbf w-\mathbf w^*)$ for every feasible $\mathbf w$, from (10.9), because the
  cross term $2(\mathbf w-\mathbf w^*)^{\top}\Sigma\mathbf w^*=(\mathbf w-\mathbf w^*)^{\top}K^{\top}\boldsymbol\lambda=0$.
  Existence and uniqueness follow from the identity itself (the second term is positive unless $\mathbf w=\mathbf w^*$),
  so the N-asset results need no KKT theory: derived in full, as the shared decision "Rigor" asks. $K\Sigma^{-1}K^{\top}$
  is positive definite because $\Sigma^{-1}$ is (by (11.8) its eigenvalues are the reciprocals of $\Sigma$'s, said in
  words in the text) and $K^{\top}$ has independent columns.
- The global minimum-variance portfolio (28.2): $\mathbf w^{\mathrm{mv}}=\Sigma^{-1}\mathbf 1/(\mathbf 1^{\top}
  \Sigma^{-1}\mathbf 1)$, $\sigma^2_{\min}=1/(\mathbf 1^{\top}\Sigma^{-1}\mathbf 1)$, $\lambda^*=2\sigma^2_{\min}$ (LM7's,
  now for $N$ assets), $\Sigma\mathbf w^{\mathrm{mv}}=\sigma^2_{\min}\mathbf 1$: every asset, and every fully invested
  portfolio, has covariance $\sigma^2_{\min}$ with $\mathbf w^{\mathrm{mv}}$, so every $\beta_{i,p}=1$ and every risk
  share $\mathrm{RC}_i/\sigma_p$ equals the weight (LM27's (27.5)–(27.6)); the identity (28.3)
  $\mathbf w^{\top}\Sigma\mathbf w=\sigma^2_{\min}+(\mathbf w-\mathbf w^{\mathrm{mv}})^{\top}\Sigma(\mathbf w-
  \mathbf w^{\mathrm{mv}})$ for $\mathbf 1^{\top}\mathbf w=1$, LM7's (7.9) for $N$ assets; the bounds
  $\lambda_N/N\le\sigma^2_{\min}\le\lambda_1/N$ from (11.4) (KC §2).
- The frontier (28.4)–(28.5) without Merton's scalars: $\mathbf w(\mu_p)=\mathbf w^{\mathrm{mv}}+\frac{\mu_p-
  \mu_{\mathrm{mv}}}{\mathrm{SR}_\infty^2}\Sigma^{-1}(\boldsymbol\mu-\mu_{\mathrm{mv}}\mathbf 1)$ and
  $\sigma_p^2=\sigma^2_{\min}+(\mu_p-\mu_{\mathrm{mv}})^2/\mathrm{SR}_\infty^2$, with
  $\mathrm{SR}_\infty^2:=(\boldsymbol\mu-\mu_{\mathrm{mv}}\mathbf 1)^{\top}\Sigma^{-1}(\boldsymbol\mu-\mu_{\mathrm{mv}}
  \mathbf 1)$: a parabola in $(\sigma_p^2,\mu_p)$, a hyperbola in $(\sigma_p,\mu_p)$ with vertex
  $(\sigma_{\min},\mu_{\mathrm{mv}})$ and asymptotes $\mu_p=\mu_{\mathrm{mv}}\pm\mathrm{SR}_\infty\sigma_p$; the
  efficient branch $\mu_p\ge\mu_{\mathrm{mv}}$; the condition that $\boldsymbol\mu$ is not proportional to $\mathbf 1$
  ($K$ of rank 2; otherwise every portfolio has the same mean and $\mathrm{SR}_\infty=0$); the multiplier $\lambda_\mu=
  d\sigma_p^2/d\mu_p$ as the shadow price of the target mean, (7.6); two-fund separation (weights are affine in $\mu_p$,
  so any two frontier portfolios span it; Merton 1972).
- The tangency portfolio and the capital market line (28.6)–(28.7): with exposures $\mathbf f$ and cash $1-L$ at $r_f$,
  (28.1) with $K=\mathbf e^{\top}$ gives every efficient book proportional to $\Sigma^{-1}\mathbf e$; normalized,
  $\mathbf w^{\mathrm{tan}}=\Sigma^{-1}\mathbf e/(\mathbf 1^{\top}\Sigma^{-1}\mathbf e)$ and $\mathrm{SR}^{*2}=\mathbf e^{\top}
  \Sigma^{-1}\mathbf e$; the identity $\mathbf 1^{\top}\Sigma^{-1}\mathbf e=(\mu_{\mathrm{mv}}-r_f)/\sigma^2_{\min}$, so the
  tangency portfolio exists exactly when $r_f<\mu_{\mathrm{mv}}$; $\mu_{\tan}-r_f=\mathrm{SR}^{*2}\sigma^2_{\min}/
  (\mu_{\mathrm{mv}}-r_f)$ and $\sigma_{\tan}=\mathrm{SR}^*\sigma^2_{\min}/(\mu_{\mathrm{mv}}-r_f)$; (28.7)
  $\mathrm{SR}^{*2}=\mathrm{SR}_\infty^2+(\mu_{\mathrm{mv}}-r_f)^2/\sigma^2_{\min}$ and the CML $\mu_p=r_f+\mathrm{SR}^*
  \sigma_p$; separation with a riskless asset, derived from (28.6): the mix of risky funds does not depend on how
  much of the book they take. §4 credits Tobin (1958), read in Cowles Foundation Discussion Paper No. 14 (1956), §3.6
  (decision on the first revision), with his limits: the riskless asset is cash at zero yield, there is no borrowing,
  and non-negativity is assumed but not binding. (28.6) allows any $r_f<\mu_{\mathrm{mv}}$ and borrowing at $r_f$; on
  the first window the tangency portfolio shorts oil, which his non-negativity assumption excludes (binding
  constraints are LM29's). What the formula returns when $r_f>\mu_{\mathrm{mv}}$: the fully invested portfolio with
  the lowest Sharpe ratio, $-\mathrm{SR}^*$ (at $r_f=\mu_{\mathrm{mv}}$ the normalization divides by zero); the upper branch's Sharpe ratio then rises toward $\mathrm{SR}_\infty$
  without reaching it (§4's pitfall prints the window of 2024-04-30, A28-24). The beta identity: (28.6) gives
  $\Sigma\mathbf w^{\mathrm{tan}}=\mathbf e/(\mathbf 1^{\top}\Sigma^{-1}\mathbf e)$, so by (27.5) every fund's beta to
  the tangency portfolio is proportional to
  its excess return, $\beta_{i,\tan}=e_i/(\mu_{\tan}-r_f)$: the tangency's counterpart of the minimum's "each asset
  has the same covariance with the portfolio" (lm07.md:388–390). That is the CAPM's equation (lm23.md:285) with
  $\mathbf w^{\mathrm{tan}}$ in the market's place; conversely, a fully invested portfolio with $\mu_p\ne r_f$ that
  satisfies it for every fund is $\Sigma^{-1}\mathbf e/(\mathbf 1^{\top}\Sigma^{-1}\mathbf e)$. The identity holds on
  any data, so it is no evidence for the CAPM [A28-45].
- Risk aversion in the exposure form (28.8): for $\delta>0$, maximizing $\mathbf f^{\top}\mathbf e-\tfrac{\delta}{2}
  \mathbf f^{\top}\Sigma\mathbf f$ over every $\mathbf f$ (cash $1-L$ at $r_f$, borrowing and lending without limit)
  has a strictly concave objective ($\Sigma$ positive definite), so $\mathbf f^*=\Sigma^{-1}\mathbf e/\delta$ is its unique
  solution for any $r_f$, with volatility $\mathrm{SR}^*/\delta$; when $r_f<\mu_{\mathrm{mv}}$,
  $\mathbf f^*=L\,\mathbf w^{\mathrm{tan}}$ with $L=\mathbf 1^{\top}\Sigma^{-1}\mathbf e/\delta>0$; LM7's two-asset $\mathbf f^*=L^*\mathbf w^{\text{tan}}$
  (lm07.md:484) cited; the N-asset Kelly identity and growth-optimal leverage left to LM43 (shared decision "LM28 and
  Kelly").
- The sensitivity of $\mathbf w^{\mathrm{tan}}$ to the means (28.9): the exposures change exactly by $\Delta\mathbf f^*=
  \Sigma^{-1}\Delta\mathbf e/\delta$; the normalized weights by the Jacobian $\partial\mathbf w^{\mathrm{tan}}/\partial
  \mathbf e^{\top}=(I-\mathbf w^{\mathrm{tan}}\mathbf 1^{\top})\Sigma^{-1}/(\mathbf 1^{\top}\Sigma^{-1}\mathbf e)$, a
  first-order approximation; the exact changes for a 1-point rise in each mean (X3) against each mean's standard error.
- The one split (LM7's pattern): the first window's $\mathbf w^{\mathrm{mv}}$ and $\mathbf w^{\mathrm{tan}}$ held at
  constant weights to 2026-10-08; predicted against realized volatility and mean with their standard errors; the exact
  split of the realized variance by (28.3) with the test period's own moments.
- U28 at $N=28$: the in-sample $\mathbf w^{\mathrm{mv}}$ (12 shorts, gross 2.24 [A28-13]), LM11's halves re-read: their shorts,
  gross exposures and cosine (decision A5; the halves' minimum variance and 1/N are LM30's, A30-19).
- The scan of the 92 windows' unconstrained solutions (Descriptive): the range of $\sigma_{\min}$ and the first
  window's rank (LM28's, decision A5), the 22 windows with $r_f\ge\mu_{\mathrm{mv}}$. That no window's
  $\mathbf w^{\mathrm{mv}}$ has a negative weight, so that R3's long-only bounds never bind, is LM29's statement
  (A29-09, its single owner by decision A5 and Y12): A28-12's zero count, smallest weight (0.13%) and gap to R3 echo
  it.
- Python: the closed forms with `np.linalg.solve`, the KKT linear system, one cvxpy check under the solver-output rule,
  and the sign of cvxpy's equality duals.
- Values owned: every A28 anchor except the echoes of LM7, LM10 and LM11 (cited to their lines) and E5's frame counts
  (A28-01 and A28-03's six dates echo LM27's A27-01 to A27-03, printed at most at LM27's precision; decision C12) and
  A28-12's check of R3 (its zero count, smallest weight and gap), which echoes LM29's A29-09.
  LM28 owns every statistic of the first window (decision A4): the funds' means, volatilities and correlations,
  $\mathbf w^{\mathrm{mv}}$, $\sigma_{\min}$, the frontier and the tangency, and equal weights' first-window mean and
  volatility (3.91%, 7.38% [A28-15]; R1's target in sample, not R1's realized volatility, which is LM30's). A4's exceptions,
  none of which LM28 prints: the risk shares (R1's are LM27's, A27-21; R2's are LM31's) and R2's mean excess return
  and volatility (Black–Litterman's calibration, LM30's A30-24). LM28 also owns the 92 windows' $\sigma_{\min}$ range
  and the U28 halves' gross exposure (decision A5).

**Leaves.** Long-only, caps, leverage and turnover limits, costs in the objective, KKT for inequalities, active sets,
the long-only frontier and the through-case forms of R3 and R4 → LM29 (including the statement that R3's bounds never
bind on E5, A29-09: the unconstrained $\mathbf w^{\mathrm{mv}}$ has no negative weight in any of the 92 windows, which
A28-12 echoes). Financing at a rate above $r_f$ → LM29 ("financed leverage"). Estimation error by simulation, the 1/N
result, shrinkage, constraints as shrinkage, Black–Litterman (whose implied returns invert (28.8)), resampled frontiers and U28's halves out of sample
→ LM30. Risk budgets and ERC against minimum variance → LM31. The statistics of a realized Sharpe ratio → LM33. Net
results of R1–R8 → LM34. Equilibrium: §4 shows only that the CAPM's equation (lm23.md:285) is (28.6)'s beta identity
with the market in the tangency portfolio's place; why the market should be that portfolio is equilibrium theory,
which LM28 does not teach. Leverage and Kelly → LM43; Kelly under uncertainty → LM45. To the lab and problems
(density): the 92-window scan's details, the U28 halves' weights, adding funds one at a time, the N = 2 reduction to
LM7 (problem 9).

**Uses before taught** (one sentence each in the text):

- §2: "Long-only weights add inequality constraints, which need the KKT conditions of [[LM7]]'s (7.13); [[LM29]]
  applies them."
- §4: "Borrowing without limit at the riskless rate is an idealization; [[LM29]] adds a financing spread and limits."
- §5: "A Jacobian matrix stacks as rows the gradients of several functions, each as in (10.8)."
- §5: "Shrinking the means or the covariance matrix is the repair of [[LM30]]."
- §6: "Large squared returns cluster, so the iid standard error of a volatility is probably too small ([[LM20]])."
  (lm20.md:376's own wording; citing only LM20 keeps the prerequisites as listed.)
- §6: "How precisely a realized Sharpe ratio is known, and whether two differ, is [[LM33]]'s question."

**Data role.**

- **E5's estimation frame** (`data/vol5_series.py`, `frames("E5")`; FinMind `TaiwanStockPrice`,
  `TaiwanStockDividendResult`, `TaiwanStockSplitPrice`, registered 2026-10-24 in d05750b): $T=2{,}362$
  joint returns 2017-01-18 → 2026-10-08, $A=242.95$; wealth frame 2,368 sessions, $A_{\mathrm w}=243.57$ [A28-01;
  LM27's A27-02, A27-03]. LM27 describes the funds and why the frames differ; LM28 cites it.
- **The first window**: the through case's, the 504 estimation rows through the first signal, 2017-02-13 → 2019-02-27,
  2.05 calendar years from the close of 2017-02-10; the trade is at the close of 2019-03-04 [A28-02]
  (`vol5_rules.schedule`). Inputs:
  $\boldsymbol\mu:=A\bar{\mathbf R}$ and $\Sigma:=A\hat\Sigma$ (divisor $T$), the plug-in estimates treated as known,
  as the rules' signals annualize them (solver scaling, shared decision "Solver output"). $r_f=1.5\%$ a year, simple,
  $r_f/A=0.617$ bp a day [A28-04].
- **The test period**: the 1,851 wealth-frame returns 2019-03-05 → 2026-10-08, 7.60 calendar years from the trade
  close; the estimation frame has 1,845 rows there, without 2025-06-11 → 06-18 (LM27's A27-03) [A28-03]. Held
  portfolios earn $\mathbf w^{\top}\mathbf R_t$ on the wealth frame (0050 earns 0 from 11 to 17 June 2025 and its
  six-session return on 18 June), constant weights, rebalanced every session, no costs; $1+\mathbf w^{\top}\mathbf R_t>0$ on every date
  (smallest 0.949 and 0.929, [A28-29, A28-30]). The test period's covariance matrix, ex-post frontier and (28.3) split
  use the estimation frame, "on the 1,845 joint test dates" (joint statistics). X1's fund volatilities use each fund's
  own one-session dates, annualized by its own sessions per year over E5 (decision C2): $A_{\mathrm w}=243.57$ for the
  four funds that trade on every session and $A=242.95$ for 0050, whose own dates are the estimation frame's
  [LM27's A27-02, A27-03]. On a common $A$ they differ from the joint matrix's diagonal by at most 0.07 points (00642U)
  [A28-08].
- **The 92 windows** (Descriptive scan): every signal's 504-row window, unconstrained solutions only [A28-12, A28-23].
- **U28** (Volume II; `data/lm10_series.py`'s `u28()`): 28 sector price indices, 4,382 returns 2008-12-02 →
  2026-10-08, $A=245.48$; halves of 2,191 (LM11's) [A28-13, A28-14]. Covariance only: no mean of U28 is used, and every
  caption says "price indices, no dividends".
- **Conventions.** Weights in percent; "shorts" are weights below $-10^{-6}$; gross exposure $\lVert\mathbf w\rVert_1$.
  Volatilities annualized by $\sqrt A$ (estimation frame), $\sqrt{A_{\mathrm w}}$ (wealth frame) or the fund's own
  sessions per year (a fund described alone), said in each caption. Years are calendar days ÷ 365.25 from the close
  before the first return (AUTHORING §8, decision C7), "a year" in a growth rate likewise. A vector printed at one
  decimal whose entries do not add as printed says "rounded separately; sums to …" (decision on LM28, A28-46); no
  digit is added for it. The text prints rounded values without flag marks (decision C11). Standard errors: (20.2)
  for means;
  lm20.md:362 with the raw sample kurtosis for volatilities, labelled iid. Every linear system is solved, never
  inverted; the Jacobian of (28.9) needs $\Sigma^{-1}$ itself, which the script solves for column by column. A residual
  at machine precision is printed as a bound ("below 1e-15"), since its digits depend on the order of operations. No
  simulation, so no seed. No count against a threshold except "shorts", which use the $10^{-6}$ rule of the shared
  decision.
- **Published files** (rule X37, shared decision "Charts"). No dated series at all: X2–X5 carry curves, points and
  weights; X4 plots two predicted and two realized points; the widget embeds $\boldsymbol\mu$ and $\Sigma$ of the
  first window only (31 numbers).
- **Scripts.** `data/lm28_numbers.py` (every printed value, asserted against `src/lm28.md`; compares with the anchors)
  and `data/lm28_charts.py` (X2–X5 and the widget's data block, with the widget's closed forms recomputed in Python),
  after `data/vol5_series.py`, `data/vol5_rules.py` (for `schedule`) and `data/vol2_series.py`.

**Hygiene declaration.** *In-sample:* every frontier, weight, multiplier, Sharpe ratio and sensitivity of §2–§5 (the
first window's plug-in moments); U28's $\mathbf w^{\mathrm{mv}}$ (full sample and each half). *Out-of-sample:* two
portfolios, $\mathbf w^{\mathrm{mv}}$ and $\mathbf w^{\mathrm{tan}}$, fixed by the spine before any result (the first
window, held to the end), §6; no other portfolio is evaluated on the test period, and neither is a candidate for "the
best rule" (shared decision "The count of trials"). *In-sample* on later
data: the test period's own frontier and ex-post optimum (E7, X4), used only to split the miss. *Descriptive:* the
92-window scan. *Hypothetical:* $\delta$, the 10% volatility target, the 1-point changes of a mean and the illustrative
rates 0% and 2% (E4). Local note: "Sections 2–5 use the first window's sample means and covariances as if they were
known: every weight there is In-sample. Section 6 holds two portfolios, chosen before any result, from 4 March 2019 to
8 October 2026 without costs: that test is Out-of-sample. The test period's own frontier is In-sample on later data and
only explains the miss. U28's sector figures are price indices, covariance only. None of these portfolios is a rule of
the through case." Weights and frontiers are plug-in estimates with an unmeasured error; §5 shows its size and LM30
measures it (said once, shared decision "Estimate, standard error, interval").

**Notation.** AUTHORING §6 with the Volume V table. Used: $R$, $\mathbf R_t$, $T$ (a count: 504, 1,845, 1,851, 4,382),
$t$, $A$, $A_{\mathrm w}$, $N$ (5 or 28), $i$, $j$ (funds), $\boldsymbol\mu$, $\Sigma$, $\hat\Sigma$, $\bar{\mathbf R}$,
$\sigma_i$, $\rho$, $\mathbf 1$, $I$, $\mathbf w$, $\mu_p$, $\sigma_p$, $\sigma_p^2$, $s_p^2$ ((10.4) cited),
$\mathbf w^{\mathrm{mv}}$, $\sigma^2_{\min}$, $\mathbf w^{\mathrm{tan}}$, $\mathrm{SR}^*$, $\mathrm{SR}$, $\mathbf e$, $r_f$,
$\mathbf f$, $L$, $\delta$ (risk aversion, the scoped row of §6: LM28, LM29, LM30), $\lambda$, $\mathcal L$, $K$,
$\mathbf b$, $\lVert\mathbf w\rVert_1$, $\lambda_1$, $\lambda_N$ ((11.4) in KC §2 only), $\kappa$ (U28 only),
$\beta_{i,p}$ (LM27's (27.5); $\beta_{i,\tan}$ in §4), $\mathrm{RC}_i$ (LM27's (27.6), E1), $\beta_i$ (LM23's market
beta, quoted once in §4), $\operatorname{SE}$, $\operatorname{Kurt}$, $\Delta$. Local symbols, declared in the notation
note (accepted as declared, decision B5):

| Symbol | Meaning | Check |
|:--|:--|:--|
| $\mu_{\mathrm{mv}}$ | the minimum-variance portfolio's mean, $\boldsymbol\mu^{\top}\mathbf w^{\mathrm{mv}}$ | subscripted $\mu$, as $\mu_p$ |
| $\mu_{\tan}$, $\sigma_{\tan}$ | the tangency portfolio's mean and volatility | subscripted, as $\mu_p$, $\sigma_p$ |
| $\mathrm{SR}_\infty$ | slope of the frontier's asymptotes, $\mathrm{SR}_\infty^2=(\boldsymbol\mu-\mu_{\mathrm{mv}}\mathbf 1)^{\top}\Sigma^{-1}(\boldsymbol\mu-\mu_{\mathrm{mv}}\mathbf 1)$: the Sharpe ratio, measured from $\mu_{\mathrm{mv}}$, that a frontier portfolio approaches as $\sigma_p$ grows | new; no star (not an optimum), not LM33's $\mathrm{SR}_0$ or LM7's asset ratio $\mathrm{SR}_i$ (integer subscript); replaces Merton's $D/C$ (accepted, decision B5) |
| $K$ ($k\times N$), $\mathbf b$, $k$ | equality constraints $K\mathbf w=\mathbf b$; their number | the Volume V row (LM28, LM29, LM35); $k$ an integer count, LM28 has no $k$ standard deviations or lag |
| $\boldsymbol\lambda$ | the vector of the $k$ equality multipliers in (28.1); in §3 its entries are $\lambda$ (budget) and $\lambda_\mu$ (target mean) | bold $\lambda$ is new; its entries are never written with an integer subscript, so $\lambda_1$, $\lambda_N$ stay eigenvalues (KC §2 only) |
| $\boldsymbol\Delta$; $\Delta\mu_i$, $\Delta\mathbf e$ | a weight change with $\mathbf 1^{\top}\boldsymbol\Delta=0$ (LM10's (10.9)); a change of a mean | §6's common $\Delta$ |
| $\partial\mathbf w^{\mathrm{tan}}/\partial\mathbf e^{\top}$ | the $N\times N$ Jacobian, entry $(i,j)=\partial w^{\mathrm{tan}}_i/\partial e_j$ | introduced in one sentence (Uses before taught) |

Not used: Merton's $a,b,c,d$ (and his $A$, $B$, $C$, $D$, which clash with $A$, the bets and $C$); $\gamma$ or $\lambda$
for risk aversion; $\theta$ (LM28 has no angle; $\mathrm{SR}_\infty$ replaces a slope letter); a Cholesky $L$ ($L$ is
total exposure); $\mathbf e_i$ (written "column $i$ of $\Sigma^{-1}$"); E5's $\kappa$ (see Pitfalls); $m$ (a number of
days; LM28 sums no days); $\mathbf h$ (no holdings). The examples set $\boldsymbol\mu:=A\bar{\mathbf R}$ and
$\Sigma:=A\hat\Sigma$ and say once that LM28 treats these plug-in estimates as the model's inputs; the theory keeps
$\boldsymbol\mu$ and $\Sigma$ unhatted, as LM7 did.

**Motivating case: "Five funds, two years, one optimizer"** (box; `build/qa/style.py`'s count with the anchor tags
removed: 160 words, 11 sentences, average 14.5, longest 24; three paragraphs of 60, 42 and 58 words, within decision
C10's 80)

> At the end of February 2019 a TWD investor holds five Taiwan-listed funds. They track Taiwan stocks (0050), US stocks
> (00646), long US Treasuries (00679B), gold futures (00635U) and crude-oil futures (00642U). The investor has 504 days
> of joint returns, from 13 February 2017 to 27 February 2019 [A28-02]. Which mix has the least variance, and which the
> best Sharpe ratio?
>
> On those days the calculus is exact. The minimum-variance mix holds every fund, 41.4% in the bond fund, and predicts
> 5.02% volatility a year [A28-10]. At a 1.5% riskless rate the best Sharpe ratio is 0.88, at 7.81% volatility, with
> oil sold short [A28-18].
>
> Hold both mixes from 4 March 2019 to 8 October 2026. The first realizes 10.05%, twice its prediction; the second
> 14.15% [A28-29, A28-30]. And one more point of expected return on gold, under a sixth of its standard error, would
> lift gold's weight from 2.6% to 12.8% [A28-27]. Was the calculus wrong, were the weights wrong, or did the inputs
> change?

Typicality (AUTHORING §8, in the paragraph after X1): the first window was the third calmest of the 92 windows by
$\sigma_{\min}$ (4.97% to 10.42%) [A28-12]. Resolved: (a) the miss, §6, E7: the test period's own minimum, on its 1,845 joint dates at constant weights, was 9.63%,
so no fully invested mix could have had less there, and the weight error added only 0.41 points to $\mathbf w^{\mathrm{mv}}$
(4.51 to $\mathbf w^{\mathrm{tan}}$) [A28-31]; the realized means lie 1.3 and 0.5 standard errors from the
predicted ones, while the volatilities moved by 13 and 12 of their own [A28-29, A28-30]; (b) the fragility, §5,
E6, X3: a 1-point change in gold's mean, 0.15 of its standard error, moves gold's weight by 10.3 points (2.576% →
12.845%), the largest change in X3 [A28-25, A28-27]. (The case box's rounded 2.6% and 12.8% are not subtracted
anywhere.)

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | which layer LM28 adds (LM27's bookkeeping → an optimum and its sensitivity); case + X1; typicality; roadmap; notation and hygiene notes | 380 |
| 2 | The Minimum-Variance Portfolio {1} | the problem with $\Sigma$ PD and its feasible set; the Lagrangian (LM7's signs) and (10.8); (28.1) with proof by (10.9), existence and uniqueness, the PD condition; (28.2), $\lambda^*=2\sigma^2_{\min}$, $\Sigma\mathbf w^{\mathrm{mv}}=\sigma^2_{\min}\mathbf 1$; (28.3); E1; E2 (U28, 12 shorts; LM11's halves); one sentence that R3 is this problem kept long-only ([[LM29]]) and that on E5 no window's $\mathbf w^{\mathrm{mv}}$ shorts; pitfall: solve, never invert, and check positive definiteness first; 導讀; KC | 750 |
| 3 | The Frontier and Two-Fund Separation {2} | two constraints, $K=(\mathbf 1\ \boldsymbol\mu)^{\top}$, the 2×2 system by (9.5); (28.4), (28.5); parabola and hyperbola, vertex, asymptotes, $\mathrm{SR}_\infty$; the efficient branch; $\lambda_\mu$ as a shadow price (7.6); two-fund separation (Merton 1972); X2; E3 (equal weights inside the frontier); pitfall: $\boldsymbol\mu$ proportional to $\mathbf 1$; 導讀; KC | 650 |
| 4 | The Tangency Portfolio and the Capital Market Line {3,4} | the riskless asset and exposures (8.4); (28.1) with $K=\mathbf e^{\top}$; (28.6) and the existence condition $r_f<\mu_{\mathrm{mv}}$; (28.7) and the CML on X2; separation with a riskless asset, credited to Tobin (1958) as read in Cowles Foundation Discussion Paper No. 14 (1956), §3.6, with his limits (cash at zero yield, no borrowing, non-negativity not binding), one sentence; the beta identity by (27.5) and the CAPM's equation (lm23.md:285), two sentences; E4 ($r_f$ = 0, 1.5%, 2%); risk aversion (28.8) for $\delta>0$ (exposures unconstrained, objective strictly concave, $\mathbf f^*$ unique; $\mathbf f^*=L\,\mathbf w^{\mathrm{tan}}$ when $r_f<\mu_{\mathrm{mv}}$), $\sigma_p=\mathrm{SR}^*/\delta$; E5; LM7's two-asset Kelly result cited, [[LM43]]; pitfall: $r_f\ge\mu_{\mathrm{mv}}$ (22 of 92 windows; the window of 2024-04-30); 導讀; KC | 880 |
| 5 | How Tangency Weights React to the Means {5,8} | $\Delta\mathbf f^*=\Sigma^{-1}\Delta\mathbf e/\delta$ exactly; (11.8)'s $1/\lambda_k$ weights in words; the Jacobian (28.9); X3; E6 (gold +1 point); each mean's SE by (20.2); Best and Grauer (1991) in one sentence, Chopra and Ziemba as [[LM7]] cites them; pitfall: a derivative is local (11.2 against 10.3 points [A28-26, A28-25]); [[LM30]]; 導讀; KC | 600 |
| 6 | The First Window Held to the End {6,8} | the split fixed in advance; constant weights on the wealth frame, no costs; X4; E7 (the split by (28.3) with (10.4)); E8 (means and volatilities with SEs); the case resolved; the unconstrained solutions are not R3 and R4 ([[LM29]]); pitfall: a frontier fitted to the past is not an opportunity set; [[LM30]], [[LM33]]; 導讀; KC | 700 |
| 7 | Mean–Variance in Python {7} | `np.linalg.solve` for (28.2), (28.4), (28.6); the KKT system of (28.1); E9: one cvxpy problem under the solver-output rule (annualized inputs, tolerances, status, residuals) and the sign of its duals; [[LM29]] for solvers; lab box | 250 |
| — | Summary (7) / Problems (12) / Solutions | | 150 / 450 / 600 |
| | **Total** | | **5,410** |

**Elements.** 9 examples (E1, E2 §2; E3 §3; E4, E5 §4; E6 §5; E7, E8 §6; E9 §7). Knowledge checks:

- §2: Show $\lambda_N/N\le\sigma^2_{\min}\le\lambda_1/N$ from (11.4) and $\lVert\mathbf w\rVert^2\ge1/N$ for
  $\mathbf 1^{\top}\mathbf w=1$; in volatilities on the first window, $\sqrt{\lambda_N/N}=3.18\%\le\sigma_{\min}=5.02\%\le7.38\%$ (equal weights) $\le\sqrt{\lambda_1/N}=10.69\%$ [A28-44].
- §3: Why does the frontier not exist when $\boldsymbol\mu=c\mathbf 1$? ($K$ has rank 1; every portfolio has mean $c$;
  $\mathrm{SR}_\infty=0$ and (28.5) divides by 0.) And why is equal weighting inefficient on the first window? (Its mean,
  3.913%, lies 0.42 points below $\mu_{\mathrm{mv}}=4.335\%$, so $\mathbf w^{\mathrm{mv}}$ has both the higher mean and
  the lower volatility) [A28-15].
- §4: In 22 of the 92 windows $r_f>\mu_{\mathrm{mv}}$ [A28-23]. What does $\Sigma^{-1}\mathbf e/(\mathbf 1^{\top}
  \Sigma^{-1}\mathbf e)$ give there? (The fully invested portfolio with the lowest Sharpe ratio, $-\mathrm{SR}^*$:
  −1.20 on 2024-04-30, gross 86.0 [A28-24].)
- §5: The exposures change linearly with $\mathbf e$ but the weights do not: why? (The weights divide by
  $\mathbf 1^{\top}\Sigma^{-1}\mathbf e$, which moves too: at $\delta=8.80$ a 1-point change in gold's mean raises $L$
  by 11.3 points [A28-28].)
- §6: Which part of E7's miss could any choice of weights have avoided? (Only the weight error, 0.41 points for
  $\mathbf w^{\mathrm{mv}}$; the moved minimum, 5.02% → 9.63%, binds every fully invested portfolio on the 1,845 joint test dates [A28-31].)
- §7: Why `np.linalg.solve(S, ones)` rather than `np.linalg.inv(S) @ ones`, and what a failed `np.linalg.cholesky`
  tells you before any solve.

中文導讀 in §2 (最小變異數投資組合 (minimum-variance portfolio), 拉格朗日乘數 (Lagrange multiplier), 共變異數矩陣 (covariance
matrix), 凸函數 (convex function); lm10.md:449's 「基礎」 said in Chinese), §3 (效率前緣 (efficient frontier), 拋物線
(parabola), 雙曲線 (hyperbola), 漸近線 (asymptote), 分離定理 (separation theorem), 兩基金分離 (two-fund separation)), §4
(切點投資組合 (tangency portfolio), 資本市場線 (capital market line), 無風險資產 (risk-free asset), 無風險利率 (risk-free
rate), 風險規避 (risk aversion)), §5 (敏感度 (sensitivity), 估計誤差 (estimation error)), §6 (樣本內／樣本外 (in-sample /
out-of-sample), LM7's form). Every term carries its English at first use in each box (shared decision "Chinese terms").
Deep Dive, §3: "The frontier from the 2×2 system", the route through Cramer's rule (9.4), for readers who want the
multipliers explicitly; the main text uses the shorter route through $\mathbf w^{\mathrm{mv}}+\boldsymbol\Delta$.

**Exhibits.**

- X1 `case` (table, §1): first window (2017-02-13 → 2019-02-27, 504 returns) and test period (2019-03-05 → 2026-10-08).
  Rows: the five funds with window mean 7.5 / 10.0 / 2.6 / 0.8 / −1.4% [A28-05], window volatility 13.5 / 11.9 / 8.5 /
  9.4 / 23.2% [A28-06], test volatility on each fund's own dates 21.6 / 17.2 / 14.6 / 18.1 / 40.7% [A28-08], $\mathbf w^{\mathrm{mv}}$ 10.7 / 22.5
  / 41.4 / 25.0 / 0.4% [A28-10], $\mathbf w^{\mathrm{tan}}$ 11.8 / 62.6 / 37.8 / 2.6 / −14.7% [A28-18]; then the two
  portfolios: predicted volatility 5.02 / 7.81%, realized 10.05 / 14.15%; predicted mean 4.34 / 8.38%, realized 9.14
  / 10.79% [A28-29, A28-30]. Note: daily total returns in NT\$; $r_f=1.5\%$. The window's rows are the optimizer's inputs, on its
  504 joint dates, annualized by $A=242.95$. Each test volatility uses the fund's own one-session dates, annualized by
  its own sessions per year over E5: $A_{\mathrm w}=243.57$, and $A=242.95$ for 0050 (decision C2) [A28-01, A28-08;
  LM27's A27-02, A27-03]. The realized columns use the wealth frame, $A_{\mathrm w}=243.57$, at constant weights and
  without costs (shared decision "E5's two frames"). The weights are in-sample plug-in estimates, and the
  $\mathbf w^{\mathrm{tan}}$ row is rounded separately (it sums to 100.1) [A28-46].
  Source: FinMind `TaiwanStockPrice`,
  `TaiwanStockDividendResult`, `TaiwanStockSplitPrice`, registered 2026-10-24; `data/vol5_series.py`; Computations:
  `data/lm28_numbers.py`.
- X2 `frontier` (`scatter` with `curves`, §3–§4): x volatility 0–25% (`fmt: "n1"`), y mean −2 to 12%. Series "funds"
  (five points, labelled by ticker; color 1). Curves: the efficient branch (solid, color 2), the inefficient branch
  (dashed, color 2, one curve), the CML from (0, 1.5) through the tangency to 12% (dashed, color 3) — each one curve
  (shared decision "Charts"). Points: $\mathbf w^{\mathrm{mv}}$ (5.02, 4.34), tangency (7.81, 8.38), equal weights on
  the first window (7.38, 3.91) [A28-10, A28-15, A28-18]. Values cited: $\mathrm{SR}_\infty=0.675$, frontier volatility
  5.05% at equal weights' mean, efficient mean 7.99% at its volatility [A28-15]. Note: in-sample, first window,
  plug-in; the asymptotes' slope is $\mathrm{SR}_\infty$; borrowing at $r_f$ assumed on the CML.
- X3 `sensitivity` (`heatmap`, §5): rows "weight of" the five funds, columns "mean of … +1 point"; cells the exact
  change of $\mathbf w^{\mathrm{tan}}$ in points (`fmt: "n1"`, min −12, max 12, `valueName` "change, points"); diagonal
  +6.6, +4.7, +7.6, +10.3, +1.9; 0050's column +6.6 / −6.4 / +0.8 / −1.6 / +0.5 [A28-25]. Note: in-sample, first window,
  $r_f=1.5\%$. Each mean's standard error is 9.4 / 8.2 / 5.9 / 6.5 / 16.1 points [A28-27]. The cells are exact
  recomputations, not (28.9)'s linear prediction, which gives 11.2 for gold's own weight [A28-26]. They are rounded
  separately, so 0050's and 00646's columns sum to −0.1, not 0 [A28-46].
- X4 `heldout` (`scatter` with `curves` and `vectors`, §6): the first window's efficient branch (solid, color 2) and the
  test period's ex-post efficient branch (dashed, color 4); arrows from predicted to realized (volatility, mean) for
  $\mathbf w^{\mathrm{mv}}$ (5.02, 4.34) → (10.05, 9.14) and $\mathbf w^{\mathrm{tan}}$ (7.81, 8.38) → (14.15, 10.79)
  [A28-29, A28-30]; point "test-period minimum" (9.63, 8.22) [A28-31, A28-32]. Note: an out-of-sample test of two portfolios fixed in advance, without costs. The realized points
  use the wealth frame; the ex-post frontier uses the estimation frame's 1,845 test rows (in-sample on later data). The
  realized means' standard errors are 3.6 and 5.1 points [A28-29, A28-30], so the vertical moves are within noise and
  the horizontal ones are not.
- X5 `u28mv` (`bar`, §2, optional): U28's 28 minimum-variance weights, sorted, one series (`fmt: "pct1"`), `hline` at 0;
  values cited: CommunicationsInternet 53.6%, Optoelectronic −10.8%, 12 shorts, gross 2.24, $\sigma_{\min}=10.98\%$
  [A28-13]. Note: price indices, no dividends; in-sample; covariance only; $A=245.48$. If the editor cuts it for
  length, E2 keeps its numbers in the text.

**Widget `frontierLab` — "Frontier, tangency and one correlation."** `Book.controls`: sliders for 00646's mean (0% to
20%, step 0.1, initial 10.0%), 00635U's mean (−5% to 10%, step 0.1, initial 0.8%) and corr(0050, 00646) (−0.95 to
0.99, step 0.01, initial 0.54 [A28-07]). Module-local code (under 30 lines, shared decision "Widgets"): a 5×5 Cholesky that
doubles as the positive-definiteness check, two triangular solves, then (28.2), (28.5) and (28.6). Chart: X2's layout
(funds, both branches, CML, $\mathbf w^{\mathrm{mv}}$ and tangency points); bars of $\mathbf w^{\mathrm{tan}}$ against
the first window's (two series). Readouts: $\mathbf w^{\mathrm{mv}}$, $\sigma_{\min}$, $\mu_{\mathrm{mv}}$,
$\mathbf w^{\mathrm{tan}}$, $\mathrm{SR}^*$, gross exposure. Messages: "$\Sigma$ is not positive definite: no frontier"
when the Cholesky fails (the window's matrix stays PD for the correlation strictly between −0.736 and 0.969 [A28-42],
so the slider, in steps of 0.01, reaches both failures); "$r_f\ge\mu_{\mathrm{mv}}$: no tangency portfolio" when $\mathbf 1^{\top}\Sigma^{-1}\mathbf e\le0$ (the frontier is still drawn). Initial state
(decision on LM28): the first draw, and so the PDF, uses the data block's exact $\boldsymbol\mu$ and $\Sigma$, and
equals X2. The sliders start at the rounded values 10.0%, 0.8% and 0.54, and an entry switches to its slider's value
only when that slider moves. With all three moved back to their starting values the readouts are
$\mathbf w^{\mathrm{tan}}=(11.8, 62.4, 37.8, 2.7, -14.7)\%$, $\mathrm{SR}^*=0.878$, $\mu_{\mathrm{mv}}=4.33\%$ against the first window's
62.6 and 2.6 (X1, E4), 0.880 (E4) and 4.34% (X2) [A28-42, A28-18, A28-10]; a line under the readouts says that the sliders move in rounded steps. Data block
`chart-lm28-frontierLab`: $\boldsymbol\mu$, $\Sigma$ (annual), $r_f$ — 31 numbers. `data/lm28_charts.py` recomputes
the initial state, the all-rounded state and five slider settings (including both PD failures and one
$r_f\ge\mu_{\mathrm{mv}}$ case) in NumPy and stores the expected readouts for `build/qa/` to compare, as
`data/lm15_charts.py` does. No simulation.

**Examples** (results recomputed from the printed inputs):

- E1 §2 `mv5`, the first window: solve $\Sigma\mathbf x=\mathbf 1$ and rescale: $\mathbf w^{\mathrm{mv}}=(10.7, 22.5,
  41.4, 25.0, 0.4)\%$, $\sigma^2_{\min}=0.0025152$, $\sigma_{\min}=5.02\%$, $\mu_{\mathrm{mv}}=4.34\%$,
  $\lambda^*=2\sigma^2_{\min}=0.00503$ [A28-10] ($\sigma^2_{\min}$ carries seven decimals because $\sqrt{0.002515}$
  would give 5.01%); every fund's covariance with the mix equals $\sigma^2_{\min}$, 0.0025152 (so by (27.5)–(27.6)
  every $\beta_{i,p}=1$ and the risk shares equal the weights) [A28-11]. The 5.02% lies below every fund's volatility,
  the lowest being 00679B's 8.5% [A28-06]. The smallest weight is 0.36% (oil) [A28-10]; in none of the 92 windows
  does an unconstrained weight turn negative (the smallest is 0.13%) [A28-12, an echo of LM29's A29-09], which is why
  R3's bounds never bind on E5 ([[LM29]]'s statement).
- E2 §2 `u28mv`, $N=28$: $\mathbf w^{\mathrm{mv}}$ shorts 12 sectors, gross 2.24, $\sigma_{\min}=10.98\%$ against 15.75%
  for equal weights (lm10.md:36) and 13.67% for the least volatile sector, CommunicationsInternet (53.6% of the
  weight); Optoelectronic −10.8%; $\kappa=108.1$ [A28-13]. The halves give 10 and 13 shorts, gross 2.44 and 2.06, and
  the cosine 0.690 of LM11's solutions (lm11.md:467) [A28-14]: rescaling leaves a cosine unchanged. In-sample on each
  half; how such weights fare on the other half is LM30's.
- E3 §3 `inside`, equal weights on the first window: mean 3.913%, 0.42 points below $\mu_{\mathrm{mv}}=4.335\%$,
  volatility 7.38%; by (28.5) the frontier portfolio with that mean has $\sqrt{0.0025152+0.0042^2/0.4554}=5.05\%$,
  and the efficient portfolio with 7.38% has mean 7.99%, weights (11.7, 58.8, 38.1, 4.7, −13.3)% [A28-10, A28-15,
  A28-19]; at that point $\lambda=-0.00193$ and $\lambda_\mu=d\sigma_p^2/d\mu_p=
  2\times3.6565\%/0.4554=0.161$ [A28-16]. Each extra point of target mean moves 00646's weight by +9.9 points and gold's
  by −5.6 [A28-17].
- E4 §4 `tan5`: $\mu_{\mathrm{mv}}=4.335\%>r_f$, so $\mathbf 1^{\top}\Sigma^{-1}\mathbf e=(\mu_{\mathrm{mv}}-r_f)/
  \sigma^2_{\min}=0.02835/0.0025152=11.27>0$; $\mathbf w^{\mathrm{tan}}=(11.8, 62.6, 37.8, 2.6, -14.7)\%$ (rounded
  separately; sums to 100.1), gross 1.29, mean 8.376%, volatility 7.810%, so $\mathrm{SR}^*=(8.376-1.5)/7.810=0.880$,
  against 0.72 for the best single fund, 00646, from unrounded inputs (X1's rounded 10.0% and 11.9% give 0.71) [A28-10, A28-18, A28-46]; (28.7): $0.7750=0.4554+0.5653^2$ [A28-15,
  A28-19]. Two-fund separation: E3's efficient weights are $\mathbf w^{\mathrm{mv}}+0.905(\mathbf w^{\mathrm{tan}}-\mathbf w^{\mathrm{mv}})$,
  where $0.905=3.6565/4.0405$, the two portfolios' mean gaps to $\mu_{\mathrm{mv}}$ in points [A28-16, A28-18]. By (27.5) each fund's beta to $\mathbf w^{\mathrm{tan}}$ is $e_i/(\mu_{\tan}-r_f)$, checked to below 1e-15;
  no beta is printed [A28-45]. With $r_f=0$: $(11.4, 48.7, 39.1, 10.3, -9.5)\%$, $\mathrm{SR}^*=1.10$; with 2%: $(12.0, 71.1, 37.0, -2.2,
  -18.0)\%$ (rounded separately; sums to 99.9), 0.82 [A28-20, A28-46]: the illustrative rate moves 00646's weight by
  22 points (shared decision "Risk-free rate").
- E5 §4 `cml10`, a 10% volatility on the CML (hypothetical target): mean $1.5\%+0.880\times10\%=10.30\%$; it needs
  $\delta=\mathrm{SR}^*/0.10=8.80$ and $L=11.27/8.80=1.28$, borrowing 0.28 of capital; exposures
  $\Sigma^{-1}\mathbf e/\delta=(15.1, 80.1, 48.4, 3.3, -18.9)\%$ from unrounded inputs (the last is −18.860, so
  $1.28\times(-14.7)$ would print −18.8) [A28-18, A28-21]. The investor with $\delta=11.27$ holds the tangency portfolio and no
  cash [A28-22].
- E6 §5 `bump`, gold's mean up 1 point (0.78% → 1.78%, a hypothetical change of 0.15 standard errors, the SE being
  6.5 points [A28-27]): gold's weight 2.576% → 12.845%, +10.3 points; 00679B −5.7, 00646 −2.8 points [A28-25,
  A28-27]; the exposures at $\delta=8.80$ change exactly by
  column 4 of $\Sigma^{-1}$ times 0.01/δ: (−2.0, +3.2, −3.6, +14.6, −0.9) points [A28-28]; (28.9) predicts 11.2 for
  gold's own weight against the exact 10.3 [A28-26].
- E7 §6 `held`, the split by (28.3) on the test rows: $\sigma^2_{\min}=0.00927$, $\sigma_{\min}=9.63\%$ (against 5.02%);
  $\mathbf w^{\mathrm{mv}}$: $0.00927+0.00081=0.01008$, 10.04%, the weight error adding 0.41 points;
  $\mathbf w^{\mathrm{tan}}$: $0.00927+0.01071=0.01998$, 14.14%, adding 4.51 [A28-31] (five decimals, so that the parts
  add as printed). The wealth frame's 10.05% and 14.15% differ in the second decimal because its six more sessions raise the annualizer to $A_{\mathrm w}=243.57$ [A28-01, A28-31]. On a common $A$ those sessions lower both volatilities slightly [A28-31]. The ex-post optimum itself moved:
  $\mathbf w^{\mathrm{mv}}=(8.0, 22.4, 46.1, 17.0, 6.5)\%$, $\mathbf w^{\mathrm{tan}}=(69.7, 8.8, -11.9, 27.6, 5.9)\%$
  (rounded separately; sums to 100.1) [A28-32, A28-46].
- E8 §6 `realized`: $\mathbf w^{\mathrm{mv}}$ realized 10.05% (SE 0.40; iid, raw kurtosis 12.6), mean 9.14% (SE 3.6),
  log growth 8.63% a year [A28-29]; $\mathbf w^{\mathrm{tan}}$ 14.15% (SE 0.53), mean 10.79% (SE 5.1), 9.79% a year
  [A28-30]. The first SE follows from the printed 10.05%, 12.6 and $T=1{,}851$; the second prints no kurtosis, since
  the rounded 14.15% and 11.6 would give 0.54, not 0.53 [A28-30]. The volatilities moved by 13 and 12 of their own
  SEs ((10.05 − 5.02)/0.40 and (14.15 − 7.81)/0.53; whole numbers, which the rounded inputs also give); the means by
  1.3 and 0.5 [A28-29, A28-30]. Resolution: the
  calculus and the weights were right in sample; the inputs changed, and most of all the volatilities (every fund's
  rose, X1); the bond fund's negative correlations shrank too, 0050–00679B from −0.30 to −0.09 and 00646–00679B from
  −0.26 to −0.06 [A28-07, A28-09] (joint, estimation frame). With the window's correlations, the test volatilities alone
  would raise the minimum from 5.02% to 8.35%, most of the way to 9.63% [A28-31].
- E9 §7 `kkt`: the KKT system $\begin{pmatrix}2\Sigma&K^{\top}\\K&0\end{pmatrix}\begin{pmatrix}\mathbf w\\
  -\boldsymbol\lambda\end{pmatrix}=\begin{pmatrix}\mathbf 0\\\mathbf b\end{pmatrix}$ at E3's point reproduces (28.1)'s
  closed form and (28.4) to below 1e-15. cvxpy 1.9.3 on the annualized inputs, a fresh `Problem` per solver: OSQP 1.1.3
  (`eps_abs` and `eps_rel` 1e-10, polishing) and CLARABEL 0.11.1 (`tol_gap_abs`, `tol_gap_rel`, `tol_feas` 1e-12), as
  the shared decision "Solver output" sets them; status `optimal` for both; weight gaps to the closed form below 1e-15
  (OSQP) and below 1e-11 (CLARABEL, whose interior-point gap is printed as a bound); KKT residuals (stationarity
  with cvxpy's duals in place of $-\boldsymbol\lambda$, and feasibility) below 1e-13; `dual_value` +0.00193 and −0.161, the negatives of LM7's $\lambda$ and $\lambda_\mu$
  [A28-33]. The sign is the installed package's behaviour, so the text tells the reader to check it against a closed
  form rather than citing a convention.

**Problems plan** (12; MC keys B, A, C, B, A, C; the lab solves 10–12). Stems state the sample (E5's first window,
504 estimation-frame returns 2017-02-13 → 2019-02-27, $A=242.95$ [A28-01; LM27's A27-02], divisor $T$,
$r_f=1.5\%$ simple a year) or the hypothetical inputs, the feasible set (fully invested, otherwise unconstrained;
problem 5 with a riskless asset), the rounding, in problem 11 the solvers and their tolerances, and in problem 12 the holding rule, the costs and the
label (shared decision "Problems").

1. MC: three uncorrelated assets, volatilities 10%, 20%, 20%: the first asset's minimum-variance weight. A 50.0%
   (inverse volatility). **B** 66.7%. C 33.3% (equal) [A28-34]. The solution adds $\sigma_{\min}=8.16\%$.
2. MC: two assets, 20% and 10%, $\rho=0.6$: the first asset's minimum-variance weight. **A** −7.7% (it shorts, since
   $\rho>\sigma_2/\sigma_1=0.5$, LM7). B 0% (long-only intuition). C 20.0% (inverse variance, correlation ignored)
   [A28-35].
3. MC: $\sigma_{\min}=5\%$, $\mu_{\mathrm{mv}}=4\%$, $\mathrm{SR}_\infty=0.5$; the volatility of the frontier portfolio
   with mean 8%. A 13.0% (adds volatilities). B 8.0% ($\sigma_{\min}$ dropped). **C** 9.43% [A28-36].
4. MC: the same, $r_f=1.5\%$; $\mathrm{SR}^*$. A 0.50 (the asymptote's slope). **B** 0.707. C 1.00 (unsquared terms
   added) [A28-37]. The solution adds $\mu_{\tan}=6.50\%$.
5. MC: $\mathrm{SR}^*=0.8$, $\mathbf 1^{\top}\Sigma^{-1}\mathbf e=8$ (annual units), $\delta=4$; the book's volatility and
   $L$. **A** 20%, 2.0. B 20%, 0.5 ($L=\delta/8$). C 320%, 2.0 ($\mathrm{SR}^*\delta$) [A28-38].
6. MC: $r_f$ exceeds $\mu_{\mathrm{mv}}$; what is $\Sigma^{-1}\mathbf e/(\mathbf 1^{\top}\Sigma^{-1}\mathbf e)$? A the
   tangency portfolio, levered. B the equal-weight portfolio. **C** the fully invested portfolio with the lowest Sharpe
   ratio [A28-39, A28-24].
7. Derive (28.1) from the Lagrangian and (10.8); prove the identity with (10.9) and deduce uniqueness; specialize to
   (28.2) and $\lambda^*=2\sigma^2_{\min}$.
8. (a) Derive (28.5) from (28.4); (b) show the asymptotes $\mu_p=\mu_{\mathrm{mv}}\pm\mathrm{SR}_\infty\sigma_p$; (c) derive
   (28.7) by splitting $\mathbf e=(\boldsymbol\mu-\mu_{\mathrm{mv}}\mathbf 1)+(\mu_{\mathrm{mv}}-r_f)\mathbf 1$ and showing the
   cross term is zero; (d) for $r_f<\mu_{\mathrm{mv}}$, show that every frontier portfolio is
   $\mathbf w^{\mathrm{mv}}+t(\mathbf w^{\mathrm{tan}}-\mathbf w^{\mathrm{mv}})$ and find $t$ (two-fund separation).
9. With $N=2$, show that (28.2) is LM7's (7.7)–(7.8); with LM7's 2017–2021 inputs ($\sigma_1^2=0.026800$,
   $\sigma_2^2=0.018353$, $\sigma_{12}=-0.004908$; lm07.md:409) get 42.3%, 9.22% and $\lambda^*=0.0170$ [A28-40].
10. Sensitivity (E5, first window): (a) raise 0050's mean by 1 point and recompute $\mathbf w^{\mathrm{tan}}$: +6.6
    points in 0050, −6.4 in 00646 [A28-41]; (b) explain with the 0.54 correlation and column 1 of $\Sigma^{-1}$ (82.8,
    −48.1, 25.8, −17.3, −0.7) [A28-41]; (c) compare 1 point with 0050's standard error, 9.4 points [A28-27], and say what
    the data do and do not support.
11. Python: on the first window compute (28.2), (28.6), and (28.4) at E3's efficient mean, with `np.linalg.solve`. That
    mean is the frontier mean at equal weights' volatility, computed from unrounded inputs (7.99%) [A28-15]. Solve the KKT
    system at that mean. Check both with cvxpy on the annualized inputs, a fresh `Problem` per solver: OSQP with `eps_abs`
    and `eps_rel` 1e-10 and polishing, CLARABEL with `tol_gap_abs`, `tol_gap_rel` and `tol_feas` 1e-12. Report the
    status, the largest weight gap, the KKT residuals and the duals' signs [A28-16, A28-33].
12. Python (*Out-of-sample*): hold the first window's $\mathbf w^{\mathrm{mv}}$ at constant weights, rebalanced every
    session without costs, on the wealth frame's 1,851 returns 2019-03-05 → 2026-10-08 [A28-03]. Compute its realized
    volatility with $A_{\mathrm w}=243.57$ and its iid SE by lm20.md:362 with the raw kurtosis (10.05%, 0.40) [A28-01,
    A28-29; LM27's A27-03]. Then split its variance by (28.3) on the estimation frame's 1,845 test rows, divisor $T$,
    $A=242.95$ (9.63% and 0.41 points) [A28-31].

**Lab parts** (`build/make_lab28.py`; reads only its `data/`, built locally by `make_lab_data.py` and never committed
(shared decision "Labs", decision C6): E5's estimation frame and its wealth frame with the traded flags, both written by
`make_lab_data.py` (decision on the first revision), and the rules' per-date targets; `sectors_close_raw.csv`
and `sectors_close_repairs.csv` for U28, built as LM23's lab builds them): 1 data, the first window, $A$, $A_{\mathrm w}$;
2 E1 by hand, $\Sigma\mathbf w^{\mathrm{mv}}=\sigma^2_{\min}\mathbf 1$, risk shares; 3 X2, E3, two-fund separation (any
two frontier portfolios rebuild a third); 4 E4, E5, $r_f$ = 0, 1.5%, 2%, the tangency betas against $e_i/(\mu_{\tan}-r_f)$;
5 X3, E6, (28.9) against exact; 6 X4, E7, E8;
7 E2 (U28, halves); 8 E9 (KKT system, cvxpy, dual signs); 9 problems 10–12; 10 the 92-window scan: recompute
$\mathbf w^{\mathrm{mv}}$ at every signal and check it against R3's target weights from the derived file (the
anchor script finds `vol5_rules.minvar` equal to it to below 1e-15 at all 92 signals, because no weight is negative:
A28-12, which echoes LM29's A29-09, the owner of that statement), and mark the 22 windows with $r_f\ge\mu_{\mathrm{mv}}$
(the lab re-implements only LM28's forms, shared decision "Labs"). Extension (*In-sample*): add the funds one at a time
(0050, then 00646, …) and plot $\mathrm{SR}^*$ and $\sigma_{\min}$ against $N$ on the first window; a closing sentence
says that a gain in sample promises nothing out of sample (§6) and that LM30 tests it. Labs write plain "LM29",
never `[[LM29]]`.

**Cross-module tags** (each with the briefs that cite it by number: the cross-check's table, decisions C8 and Y1).

- (28.1) For $\Sigma$ positive definite and $K$ ($k\times N$) of full row rank, $\min\mathbf w^{\top}\Sigma\mathbf w$
  subject to $K\mathbf w=\mathbf b$ has the unique solution $\mathbf w^*=\Sigma^{-1}K^{\top}(K\Sigma^{-1}K^{\top})^{-1}
  \mathbf b$, value $\mathbf b^{\top}(K\Sigma^{-1}K^{\top})^{-1}\mathbf b$, multipliers $\boldsymbol\lambda=2(K\Sigma^{-1}
  K^{\top})^{-1}\mathbf b$, and $\mathbf w^{\top}\Sigma\mathbf w=\mathbf w^{*\top}\Sigma\mathbf w^*+(\mathbf w-\mathbf w^*)^{\top}
  \Sigma(\mathbf w-\mathbf w^*)$ on the feasible set (LM29, LM35).
- (28.2) $\mathbf w^{\mathrm{mv}}=\Sigma^{-1}\mathbf 1/(\mathbf 1^{\top}\Sigma^{-1}\mathbf 1)$, $\sigma^2_{\min}=
  1/(\mathbf 1^{\top}\Sigma^{-1}\mathbf 1)$, $\Sigma\mathbf w^{\mathrm{mv}}=\sigma^2_{\min}\mathbf 1$ (LM29, LM30, LM31).
- (28.3) $\mathbf w^{\top}\Sigma\mathbf w=\sigma^2_{\min}+(\mathbf w-\mathbf w^{\mathrm{mv}})^{\top}\Sigma(\mathbf w-
  \mathbf w^{\mathrm{mv}})$ for $\mathbf 1^{\top}\mathbf w=1$; with a sample $\hat\Sigma$ and (10.4) it splits a realized
  variance exactly (LM30; in LM28, E7 and problem 12).
- (28.4) $\mathbf w(\mu_p)=\mathbf w^{\mathrm{mv}}+\frac{\mu_p-\mu_{\mathrm{mv}}}{\mathrm{SR}_\infty^2}\Sigma^{-1}
  (\boldsymbol\mu-\mu_{\mathrm{mv}}\mathbf 1)$, $\boldsymbol\mu$ not proportional to $\mathbf 1$ (LM29).
- (28.5) $\sigma_p^2=\sigma^2_{\min}+(\mu_p-\mu_{\mathrm{mv}})^2/\mathrm{SR}_\infty^2$ (LM29).
- (28.6) $\mathbf w^{\mathrm{tan}}=\Sigma^{-1}\mathbf e/(\mathbf 1^{\top}\Sigma^{-1}\mathbf e)$ when $r_f<\mu_{\mathrm{mv}}$,
  equivalently $\mathbf 1^{\top}\Sigma^{-1}\mathbf e=(\mu_{\mathrm{mv}}-r_f)/\sigma^2_{\min}>0$; $\mathrm{SR}^{*2}=
  \mathbf e^{\top}\Sigma^{-1}\mathbf e$ (LM29, LM30).
- (28.7) $\mathrm{SR}^{*2}=\mathrm{SR}_\infty^2+(\mu_{\mathrm{mv}}-r_f)^2/\sigma^2_{\min}$; the CML $\mu_p=r_f+
  \mathrm{SR}^*\sigma_p$ (LM29).
- (28.8) For $\delta>0$, $\max_{\mathbf f}\ \mathbf f^{\top}\mathbf e-\tfrac{\delta}{2}\mathbf f^{\top}\Sigma\mathbf f$ over
  every $\mathbf f$ has the unique solution $\mathbf f^*=\Sigma^{-1}\mathbf e/\delta$, volatility $\mathrm{SR}^*/\delta$;
  when $r_f<\mu_{\mathrm{mv}}$, $\mathbf f^*=L\,\mathbf w^{\mathrm{tan}}$ with $L=\mathbf 1^{\top}\Sigma^{-1}\mathbf e/\delta>0$;
  borrowing and lending at $r_f$ (LM29, LM30 inverted as $\mathbf e_{\mathrm{eq}}=
  \delta\Sigma\mathbf w_{\mathrm{ref}}$).
- (28.9) $\Delta\mathbf f^*=\Sigma^{-1}\Delta\mathbf e/\delta$ exactly; $\partial\mathbf w^{\mathrm{tan}}/\partial
  \mathbf e^{\top}=(I-\mathbf w^{\mathrm{tan}}\mathbf 1^{\top})\Sigma^{-1}/(\mathbf 1^{\top}\Sigma^{-1}\mathbf e)$ (LM30).

**Pitfalls to pre-empt.**

- The existence condition. $r_f>\mu_{\mathrm{mv}}$ in 22 of the 92 windows (every month-end from 2022-06-30 to
  2024-04-30 except 2024-03-29, where $\mathbf 1^{\top}\Sigma^{-1}\mathbf e=0.614$ and the gross exposure is 29.1)
  [A28-23]. There the formula returns the worst portfolio, not the best. On 2024-04-30, $\mu_{\mathrm{mv}}=1.34\%$ and
  $\mathbf 1^{\top}\Sigma^{-1}\mathbf e=-0.185$; the normalized $\Sigma^{-1}\mathbf e$ has Sharpe ratio −1.20 with
  gross 86.0, while the upper branch's Sharpe ratio rises toward $\mathrm{SR}_\infty=1.2023$ without reaching it
  (0.7864, 1.1928 and 1.2020 at 10, 100 and 1,000 points above $\mu_{\mathrm{mv}}$) [A28-24]. The through case's R4
  survives because it is long-only (LM29); a script that normalizes $\Sigma^{-1}\mathbf e$ without the sign test is
  wrong.
- Units. $\mathbf w^{\mathrm{mv}}$ does not change when $\Sigma$ is rescaled; $\mathbf w^{\mathrm{tan}}$ needs
  $\boldsymbol\mu$, $\Sigma$ and $r_f$ in the same units (annual here, $r_f/A$ a day). $\mathrm{SR}^*$ is annual because
  $\boldsymbol\mu$ and $\Sigma$ are. Solvers get the annualized inputs (shared decision "Solver output").
- E5's condition number, 11.271, and $\mathbf 1^{\top}\Sigma^{-1}\mathbf e=11.272$ agree to four significant
  figures (11.27) and differ in the third decimal, by coincidence [A28-43]: the text prints no $\kappa$ for E5 (only
  U28's, E2), so a reader never meets two 11.27s.
- Never call the unconstrained $\mathbf w^{\mathrm{mv}}$ and $\mathbf w^{\mathrm{tan}}$ R3 and R4: the rules are their
  long-only forms re-solved every month with costs (LM29, LM34). The held portfolios of §6 are not rules, are not
  costed, and are counted in LM28's hygiene note, not in $n=8$.
- A predicted volatility at an in-sample optimum is biased low, because the optimizer favours directions where
  $\hat\Sigma$ is small; one sentence, with LM30 as the owner. E7 does not claim that bias explains the miss: the
  minimum itself moved (5.02% → 9.63%), and the first window was the third calmest of 92.
- Causes (PITFALLS §7). The text says "the volatilities rose" (X1, an observation) and that the means' miss is within
  noise (E8); it does not name a market cause for 2020–2026 without a dated source.
- Standard errors: the realized volatility's iid SE (0.40) understates its error under clustering (lm20.md:376); the
  normal-days SE is 0.17 [A28-29]. A gap of 13 standard errors [A28-29] survives any
  reasonable inflation of the SE, which is the point made.
- A derivative is local: (28.9) gives 11.2 points where the exact change is 10.3 (X3 uses exact changes) [A28-26].
- cvxpy's equality duals carry the opposite sign to LM7's $\lambda$ (E9); check signs against a closed form.
- Do not print a realized Sharpe ratio of the held portfolios as a finding (LM33 owns its precision); the reader can
  form one from E8's numbers, and the text says why it is not reported (decision D).
- Fund descriptions (underlying indices, futures roll) come from LM27, which checks the issuers' pages; LM28's case
  names asset classes only.

**Curriculum guidance carried** (`plans/vol-5.md`, the adopted table):

- Capability layer (g:30): §1's first paragraph says LM28 turns LM27's bookkeeping of a given $\mathbf w$ into the
  choice of $\mathbf w$, with its conditions and its sensitivity.
- Outcome levels (g:54–58): marked above; three [D], four [C], one [U].
- Estimation, constraints, costs and hygiene tied together (g:25): §5 shows the inputs' error, §6 the out-of-sample
  miss, and both hand over to LM29 (constraints) and LM30 (estimation error) by name.
- Fix windows before evaluation (g:111): the one split is the through case's first window, fixed 2026-10-24; the brief
  adds no other portfolio to the test (hygiene declaration).
- "Data too thin" is a valid conclusion (g:116): problem 10(c) asks for it, and §5's summary sentence says that two years
  of means cannot carry tangency weights to the nearest 10 points. The evidence: a 1-point change in gold's mean,
  0.15 of its standard error, moves gold's weight by 10.3 points [A28-25, A28-27].
- Taught, practised, assessed (g:124): the outcome map above.
- Density (g:60–63): the 92-window scan, U28's halves and the N = 2 reduction go to the lab and problems; §2–§6 each keep
  one worked case.

**Stage 4 for earlier modules.**

- `leads` gain 28 in lm08.md:6, lm12.md:6 (the Cholesky test, lm12.md:402–411), lm20.md:6 ((20.2) and the volatility SE, lm20.md:362)
  and lm23.md:6 (§4 cites the CAPM's equation, lm23.md:285), all four on decision G's list.
- lm07.md:511–512: 切點組合 → 切點投資組合, three times (the plan's Stage 4 list; the Chinese-terms decision of the second
  recomputation extends it to line 512).
- lm07.md:786 (Chopra and Ziemba's issue number, 19(2)) goes to LM30's list, since LM30 cites the paper (decision on
  Y14); LM28 cites it only as lm07.md:509 does.
- No wording change: lm07.md:457's "where a line from the risk-free rate touches the set of risky portfolios" is a
  two-asset sentence about LM7's windows; LM28 adds the general condition ($r_f<\mu_{\mathrm{mv}}$) without
  rewording LM7.

**Sources** (the verified readings of 2026-10-24: bibliographic data from Crossref, re-read for SOURCES,
"Papers and books (Volume V)", unless another source is named; Tobin as the source check of decision F read him;
paraphrased, no quotation over one sentence; section, equation and page numbers are those of the version named):

- Markowitz, H. (1952). "Portfolio Selection." *Journal of Finance* 7(1): 77–91, March 1952. DOI
  10.1111/j.1540-6261.1952.tb01525.x. Already in SOURCES and lm07.md:777. Used for the origin of mean–variance only.
- Merton, R. C. (1972). "An Analytic Derivation of the Efficient Portfolio Frontier." *Journal of Financial and
  Quantitative Analysis* 7(4): 1851–1872. DOI 10.2307/2329621. Crossref holds the first page only; the pages
  1851–1872 come from RePEc and fit Crossref's issue listing (the next article starts at p. 1873). Abstract (RePEc):
  explicit frontiers for more than three assets, the separation theorem stated and proved as a mutual-fund theorem,
  and the graphical method incorrect under some conditions. Text not read. Used, at the abstract's level, for the
  closed-form frontier and two-fund separation; his notation is not used. The Cambridge-style DOI
  10.1017/S0022109000017798 is not registered (Crossref and doi.org return 404): cite 10.2307/2329621.
- Tobin, J. (1958). "Liquidity Preference as Behavior Towards Risk." *Review of Economic Studies* 25(2): 65–86,
  February 1958. DOI 10.2307/2296205. Crossref holds the first page only; the end page 86 comes from RePEc and fits
  Crossref's issue listing (the next article starts at p. 87). The RES text is on JSTOR only and was not compared.
  Read by the source check in Cowles Foundation Discussion Paper No. 14, dated 17 July 1956, an image-only typescript
  (cowles.yale.edu/sites/default/files/2022-08/d0014.pdf; RePEc lists it as Cowles Foundation Discussion Papers 14,
  1956), §3.6 "Multiple alternatives to cash", typescript pp. 31–36.
  With cash riskless, the dominant combinations of the non-cash assets lie on one ray from the origin (pp. 34–35); so
  their proportionate mix does not depend on their total share, and the investor behaves as if there were one
  composite asset (pp. 35–36); the opportunity locus is a line, (3.25); the result holds only while cash is riskless
  (p. 36). Limits: the riskless asset is cash at zero yield; no borrowing (the total stays at most the investor's
  balance); non-negativity is assumed but not treated as binding (the proof solves the linear system (3.22)); the mix
  depends on the investor's own estimates. §4 cites "Tobin (1958), read in Cowles Foundation Discussion Paper No. 14
  (1956), §3.6" with those limits, beside Merton (1972); it prints no page or section number of the RES text, and the
  typescript's pages and equation numbers stay in SOURCES.
- Best, M. J., and R. R. Grauer (1991). "On the Sensitivity of Mean-Variance-Efficient Portfolios to Changes in Asset
  Means: Some Analytical and Computational Results." *Review of Financial Studies* 4(2): 315–342. DOI
  10.1093/rfs/4.2.315. Abstract (OpenAlex's copy, re-read for SOURCES; the first drafter read RePEc's): with only a
  budget constraint, an efficient portfolio's weights, mean and variance can be extremely sensitive to changes in the
  asset means; with non-negativity added, the weights stay extremely sensitive while the portfolio's return and
  standard deviation barely move; a surprisingly small rise in one asset's mean drives half the securities out. Text
  not read. Used in §5 for one sentence at the abstract's level (the first clause).
- Chopra, V. K., and W. T. Ziemba (1993). "The Effect of Errors in Means, Variances, and Covariances on Optimal Portfolio
  Choice." *Journal of Portfolio Management* 19(2): 6–11. DOI 10.3905/jpm.1993.409440. Cited only as lm07.md:509 states
  its finding; no ratio of theirs is printed (shared decision "References"). lm07.md:786's missing issue number is
  LM30's Stage 4 item (decision on Y14).
- Boyd, S., and L. Vandenberghe (2004). *Convex Optimization*. Cambridge University Press. DOI
  10.1017/CBO9780511804441 (Crossref: monograph issued 2004-03-08). Read in the authors' PDF
  (web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf, seventh printing with corrections, 2009; pages re-checked in a
  fresh download for SOURCES): §4.4.1 "Examples", subsection "Markowitz portfolio optimization", p. 155, and §4.7.6
  "Examples", subsection "Risk-return trade-off in portfolio optimization", pp. 185–186. Used as the pointer for the
  QP form ([[LM29]]).
- LM23's statement of the CAPM (lm23.md:285): cited by line for the equation only; its sources (Campbell, Lo and
  MacKinlay 1997, ch. 5; Sharpe 1964; Lintner 1965) are LM23's. Sharpe (1964) is bibliographic data only in SOURCES, so
  LM28 does not cite it as the source of the term "capital market line".
- cvxpy 1.9.3 with OSQP 1.1.3 and CLARABEL 0.11.1 (the locked environment; SOURCES, "Python (Volumes V and VI)", "The packages (Volumes V and VI)" and "cvxpy 1.9.3"). The
  documentation's "Advanced Features" page (cvxpy.org/tutorial/advanced/, the site's latest documentation, not pinned
  to 1.9.3) says that a constraint's `dual_value` holds its optimal dual variable (Lagrange multiplier) and prints no
  sign convention for equalities. The installed package returns, for the budget equality of a variance minimization,
  the negative of LM7's $\lambda$ (the toy run in SOURCES' "cvxpy 1.9.3" entry, "Dual signs", and A28-33 on the first window). E9 reports that
  behaviour and tells the reader to check signs against a closed form. The tolerances are `vol5_rules.py`'s
  `OSQP_OPTS` and `CLARABEL_OPTS` (shared decision "Solver output").
- NumPy 2.5.3 (`linalg.solve`, `linalg.cholesky`, `linalg.eigvalsh`) and SciPy 1.18.1, the locked versions (SOURCES,
  Python entries).
- FinMind `TaiwanStockPrice`, `TaiwanStockDividendResult` and `TaiwanStockSplitPrice` (E5, registered and retrieved
  2026-10-24, through `vol5_series.py`; LM27 owns the data description) and `TaiwanStockPrice` sector indices with the
  Volume II repairs (U28). No FinMind call was made for this brief.
- Checked, not cited: Sharpe (1990), Nobel Lecture "Capital Asset Prices with and without Negative Holdings",
  7 December 1990 (the date on nobelprize.org's lecture page), published in *Journal of Finance* 46(2): 489–509, June
  1991, DOI 10.1111/j.1540-6261.1991.tb02671.x (its reference list misdates Tobin's paper as 1969). With Tobin read
  directly the lecture is no longer the go-between; Markowitz (1959),
  named only inside the lecture, is unverified and not cited. Michaud (1989), Kan and Zhou (2007), DeMiguel et al.
  (2009) and Jagannathan and Ma (2003) are LM30's.

**Chinese terms** (樂詞網, searched 2026-10-24 with the URL pattern of SOURCES' Volume III entry, all listings, and
rechecked the same day by the fresh pass of 1,817 searches recorded in SOURCES, "Chinese terms (Volumes V and
VI)", whose corrections are applied here; on the plan's list unless marked new):

| English | 樂詞網 (listing) | LM28 |
|:--|:--|:--|
| efficient frontier | 效率前緣 (管理學名詞) | 效率前緣 |
| efficient portfolio | 效率投資組合 (管理學名詞) — new | 效率投資組合 |
| minimum-variance portfolio | 最小變異數投資組合 (管理學名詞, found only with the hyphen); 最低變異數資產組合 (經濟學) | 最小變異數投資組合 (the management listing's form and LM7's Glossary, lm07.md:770) |
| capital market line | 資本市場線 (管理學名詞, headword "capital market line、 CML"; 經濟學) | 資本市場線 |
| risk-free asset | 無風險資產 (管理學名詞; 經濟學, also for "riskless asset") — new | 無風險資產 |
| risk aversion | 風險規避 (管理學名詞); 風險袪避 (經濟學) | 風險規避 |
| separation theorem | 分離定理 (統計學名詞, 經濟學, 電子計算機名詞) — new | 分離定理 |
| two-fund separation | no entry for "two-fund separation" or "two-fund"; the query `two fund` finds 管理學名詞's "two fund monetary separation" 兩基金的貨幣分離 — new | 兩基金分離 (composed from 分離定理, a form that entry supports; printed with its English in every box) |
| tangency portfolio | no entry | 切點投資組合 (the book's form, lm07.md:771) |
| parabola; hyperbola; asymptote | 拋物線, 雙曲線 (數學名詞); 漸近線 (數學名詞, headword "asymptote ; asymptotic line"; 統計學名詞) — new | 拋物線, 雙曲線, 漸近線 |
| mean–variance | compounds only: 平均數-變異數分析, 平均數-變異數準則 (管理學名詞); 平均報酬與風險為抵換分析法 (經濟學) — new | 平均數-變異數 (only if a box needs it) |
| sensitivity | 敏感度 (數學名詞, 統計學名詞) | 敏感度 |
| Jacobian matrix | Jacobi矩陣 (數學名詞; "Jacobian" is Jacobi行列式) — new | not in a box (English in the text); a box would write Jacobi 矩陣, with the space that the Chinese-terms decision puts after a Latin name |

The boxes also use, from the shared list or the published modules: 拉格朗日乘數 (the engineering listings' form, printed
at lm04.md:282, lm07.md:353 and lm11.md:312), 共變異數矩陣, 凸函數, 無風險利率 (lm23.md:340), 估計誤差 (the statistics
listing's headwords "error of estimation" and "estimate error") and 樣本內／樣本外 (lm07.md:773). SOURCES records the
table from the fresh pass.

**Open before Stage 2:** none in the brief. The second revision's three open items and the fresh check's items are
closed (next list), and the decisions leave nothing else open for LM28. The fresh check's changed anchor rows (A28-01,
A28-18, A28-31, A28-33) were reproduced by the fresh verification of 2026-10-31.

**Closed by the editor's decisions (2026-10-24, 2026-10-25 and 2026-10-31)**, with how:

- The fresh check of the whole of Stage 1 (2026-10-31): two-fund separation is practised in E4
  ($t=0.905=3.6565/4.0405$) and assessed by problem 8(d), with A28-18 extended (B28-05, the editor's option (a));
  E8's "most of all the volatilities" is backed by the counterfactual 8.35%, with A28-31 extended (B28-14, option
  (a)); E7 names the higher annualizer as the cause of the wealth frame's second decimal, and A28-31 adds the common-$A$
  volatilities, not printed (R28-02); CLARABEL's stationarity residual prints as a bound, below 1e-13 (A28-33,
  R28-07); A28-01 flags $A_{\mathrm w}$ at 3 dp (R28-09); A28-13's dates were reproduced (R28-11, B28-15). The
  check's other confirmed items are closed by the text edits its verifier gave.

- Tobin (1958), the second revision's open item 1: cited directly in §4, "read in Cowles Foundation Discussion Paper
  No. 14 (1956), §3.6", with his limits and no RES page (decision on the first revision; Y4). Sharpe's lecture is no
  longer cited.
- The CAPM sentence and LM23's lead, open item 2: accepted. The beta identity puts $\mathbf w^{\mathrm{tan}}$ in the
  market's place in lm23.md:285 (A28-45); prerequisite 23 stays, and lm23 +28 is on decision G's list.
- Lab data, open item 3: `make_lab_data.py` writes both E5 frames, the wealth frame with its traded flags (shared
  decision "Labs"), so the lab reads the estimation frame directly.
- Tag users and leads (Y1): (28.1) gains LM35, (28.2) LM31 and (28.3) LM30, as the cross-check's table gives them; the
  Leads paragraph is rewritten from it, and the speculative mention of LM43's and LM45's future citations goes. LM43
  stays in `leads` by §4's forward pointer and must not re-derive (28.6)–(28.8) (shared decision "LM28 and Kelly").
  LM27's lists name LM28 for (27.4)–(27.6), so the second revision's note for the cross-check closes.
- Owners (A4, A5; Y12, Y17): R1's first-window risk shares are LM27's (A27-21), R2's are LM31's, and R2's mean excess
  return and volatility are LM30's (A30-24); LM28 prints none of them. "R3's bounds never bind" is LM29's (A29-09),
  so A28-12's zero count, smallest weight and gap to R3 are echoes of A29-09 (LM29's third revision asks the same);
  A28-12 keeps the $\sigma_{\min}$ range and the first window's rank, LM28's by A5. E1, the Leaves and the lab point
  to LM29.
- Echoes (C12): E5's frame counts cite LM27's A27-01 to A27-03 (A28-01, A28-03), at most at LM27's precision, and
  $A=242.95$ and $A_{\mathrm w}=243.57$ cite A27-02 and A27-03 wherever they print (data role, X1's note, problem
  stems; the third revision's verifier). For the briefs that echo LM28 (Y11): the first window's means and
  volatilities print at one decimal (X1; 00635U's mean at two in E6), their standard errors at one (X3's note) and
  $\mathbf w^{\mathrm{tan}}$ at one (A28-18); the Printed-as column names each form's place. Three briefs print
  first-window statistics beyond LM28's precision, each beside a computation that needs the digit (decision C12's
  exception). LM30's E2 prints $T/A=2.0745$ and the five volatilities 13.50, 11.87, 8.54, 9.39 and 23.17% beside (20.2)'s
  computation (decisions on the third revision). LM29's widget readout prints 0050's and 00646's excess means 6.04% and
  8.53%, volatilities 13.50% and 11.87% and correlation 0.539 (A29-27). LM31's E1 prints 0050's and 00679B's
  volatilities 13.50% and 8.54% (A31-07), and its E5 prints their squares beside the window's variances. LM31's E2 prints all five volatilities to two decimals beside its inverse-volatility weights (A31-06), and its widget the correlations 0050–00642U and 00679B–00642U, which LM28 does not print (A31-39). The Printed-as
  cells of A28-02 and A28-05 to A28-07 record them.
- Listing markets (decisions on the third revision): 00679B trades on TPEx and the other four funds on TWSE. LM28
  calls them "Taiwan-listed", true of both, and prints no session, cost or price-limit rule, so nothing changes;
  LM27 (sessions), LM34 (costs) and LM35 (limits) print the markets' rules.
- The year count (C7, AUTHORING §8; Y3): years run from the close before a sample's first return, so the first
  window is 2.05 calendar years from the close of 2017-02-10 (A28-02), and LM30 echoes that value.
- NEAR flags (C11, Y18): the brief's text prints rounded values without flag marks; the flags stay in the anchors
  table, whose Printed-as column now repeats every flag of a printed form.
- Rounded vectors (the decision on LM28; the recomputation's major 1): $\mathbf w^{\mathrm{tan}}$ in X1 and E4, E4's
  $r_f=2\%$ weights and E7's ex-post $\mathbf w^{\mathrm{tan}}$ say "rounded separately; sums to 100.1" (or 99.9), and
  X3's note names the two columns that sum to −0.1, all from A28-46.
- The recomputation's minor items: A28-24's numbers print in §4's pitfall, and every other Printed-as entry names
  where it prints or says "not printed" (2); the missing printed forms and repeated flags are added (3); A28-16 states
  $\mathbf b=(1,\mu_p)$ with A28-15's unrounded $\mu_p$ (4); the case box is recounted with `build/qa/style.py` (5);
  CLARABEL's weight gap prints as "below 1e-11" (6); the year rule cites AUTHORING §8 and decision C7 (7); the
  annualizer of A28-08 over all of E5 stays, as the report proposes ("no change needed") and the cross-check
  recommends, since no printed value changes (8).
- One more derived result: E1, E3 and E4 print $\sigma^2_{\min}=0.0025152$, since $\sqrt{0.002515}$ gives 5.01%, not
  the printed 5.02% (A28-10).
- Outcome 1 reads "of $N$ assets" (Y6). The split-ratio rule (B6): LM28 writes no split symbol; the data role describes
  0050's 18 June 2025 return in words.
- R3 equals the unconstrained $\mathbf w^{\mathrm{mv}}$ at every signal (A29-09, echoed by A28-12): LM28 states the
  unconstrained fact once (E1, §2) with LM29's anchor, and LM29 owns it and builds its active-set example on U28 and R4, not on R3
  (decision D: the briefs' proposals accepted).
- No unconstrained tangency in 22 of the 92 windows (A28-23): §4's pitfall and KC use it, and LM29 says that R4's
  long-only QP is defined there (decision D).
- $\mathrm{SR}_\infty$ and the bold $\boldsymbol\lambda$ with its rule (entries $\lambda$ and $\lambda_\mu$ only, so
  $\lambda_1$, $\lambda_N$ stay eigenvalues): accepted as declared (decision B5).
- No realized Sharpe ratio for the held portfolios; one sentence points to LM33 (decision D).
- (8.11) stays with LM27: its brief's (27.7) cites (8.11) (the proposal, accepted with the briefs' proposals, decision D).
- The held portfolios keep constant weights without costs, as LM7 did; a costed version would be a ninth candidate
  and is not added (decision D).
- LM27's tags: cited by number, (27.4)–(27.6) (decision C8). The funds' underlying indices are LM27's to verify on the
  issuers' pages; LM28's case names asset classes only (shared decision "Data").
- The spine's **Data** line: held portfolios earn their returns on the wealth frame (1,851 returns), and only the test
  period's joint statistics use its 1,845 estimation rows [A28-03]. The two frames give 10.05% against 10.04% and
  14.15% against 14.14% [A28-31], so nothing in §6 turns on the choice (decision E accepts the departure).
- The widget's initial state, A28-08's annualizer and the gap on a common $A$ follow the per-module decision on LM28
  and decision C2.
- The first window is the third calmest of 92 [A28-12], so §6's miss is partly the luck of the split. The text says
  so; a second split would be a second test and is not added (g:111).

## LM29 Convex Optimization in Practice

Stage 1 brief, drafted 2026-10-24 from the editor's spine (`plans/vol-5.md`, "### LM29 Convex Optimization in
Practice", commit d05750b) and the shared decisions above it. Revised the same day, first to the editor's decisions on
the briefs (`plans/vol-5.md`, "Editor's decisions on the briefs (2026-10-24)"), after the independent recomputation (34
of 34 anchors reproduced) and the cross-module check (X2, X3, X8, X9, X13, X16, X17, X19, X20, X25 and X26 name LM29);
then a second time to "Decisions on the first revision" and "Decisions on the second recomputation and cross-check"
(commit ef66607), after the second recomputation (12 of 12 changed anchors reproduced, about 450 printed numbers
audited; three major and ten minor findings, all applied below) and the second cross-check (Y1, Y4, Y5 and Y12 name
LM29, and Y18's book-wide rule (C11) applies). A last pass (2026-10-25) applies the third verifier's five minor
findings and "Decisions on the third revision", whose listing-market item does not name LM29; no number changes.
Every number carries its anchor ID at first appearance; `data/vol5_anchors_lm29.py` prints them all (35
rows, `## LM29` of `plans/vol-5-anchors.md`). Numbers quoted from published modules carry their file:line, and a
number another module owns carries the owner's anchor ID where it is printed, at no more than the owner's precision
unless a computation beside it needs more (decision C12). The script imports `vol5_series.frames`, `vol5_rules`
(`schedule`, `WINDOW`, `RF`, `SPREAD`, the cost model, `cov0`, `minvar`, `maxsharpe` and the solver options) and
`lm10_series.u28`; it re-implements no rule and prints no statistic of a rule's wealth path. The anchors that the
third revision changed are listed in the anchors' Status; its verifier recomputed them, and the last pass changes
none. The fresh check of the whole of Stage 1 (2026-10-31; "Decisions on the fresh check of the whole of Stage 1")
found 33 issues in LM29, merged into 31 items (one critical: problem 1's set; five major), and every item is applied
below. It adds A29-35 ($r_f$ at 0% and 2%) and changes ten anchors' lines, definitions or Printed-as cells (listed
in the anchors' Status), which were reproduced by the fresh verification of 2026-10-31.

**Prereq:** `[4, 7, 8, 9, 10, 11, 12, 27, 28]`. What each supplies (tags rechecked in `src/lmNN.md`, 2026-10-24):

- LM4: convexity in one variable (the definition box, lm04.md:152–155, mixing weight $w\in[0,1]$); the
  second-derivative test, stated without proof there (lm04.md:157); "a critical point of a differentiable concave
  function is a global maximum" (lm04.md:159); corner solutions on an interval and the derivative at a binding corner
  as a shadow price (lm04.md:222–237, the reading at lm04.md:237; outcome lm04.md:12); the envelope result (4.16)
  (lm04.md:518). §2 reduces convexity in $\mathbb R^N$ to LM4's one-variable test along segments.
- LM7: the Lagrangian with its signs, $\mathcal L=h-\lambda(\psi-b)$ (Glossary lm07.md:765); (7.5) and the shadow
  price (7.6) $J'(b)=\lambda^*$ (lm07.md:309, 323); the global-optimum remark LM29 develops (lm07.md:268); the KKT
  theorem (7.13) for a maximization under linearly independent binding gradients, stated without proof, "for a
  minimization, apply (7.13) to $-h$" (lm07.md:528–531); slack and binding, enumeration of binding sets and the capped
  long-only Kelly example with its seven candidates (lm07.md:522–569, [[ex:kkt]] at lm07.md:553); the Glossary's
  影子價格 and KKT 條件 (lm07.md:766, 768) and the box's 緊/鬆弛 and 互補鬆弛性 (lm07.md:571–572).
- LM8: net exposure $\mathbf 1^{\top}\mathbf f$ and gross exposure $\lVert\mathbf f\rVert_1$ (lm08.md:178–180), for
  §3's gross limit, §6 and problem 11.
- LM9: (9.6) invertibility (lm09.md:295), for the KKT systems of §4 and the widget (a binding set whose system is
  singular gives no candidate); (9.8) solvability (lm09.md:364).
- LM10: (10.1) symmetrization (lm10.md:72); (10.8) gradients (lm10.md:403); (10.9) the exact expansion
  (lm10.md:409); (10.10) the chord identity (lm10.md:434) and the theorem "a quadratic is convex exactly when its
  matrix is PSD, strictly convex exactly when PD" (lm10.md:436–437); the promise at lm10.md:446.
- LM11: (11.9), the relative error of a solve bounded by $\kappa$ (lm11.md:429), for §8's scaling paragraph; $\kappa$
  as §6's table defines it.
- LM12: (12.6) $\kappa(\tilde X^{\top}\tilde X)=\kappa(\tilde X)^2$ (lm12.md:262) and the Cholesky factor: the exact
  solver of `vol5_rules.py` works with the Cholesky factor of $\Sigma$, whose condition number is $\sqrt{\kappa(\Sigma)}$
  (§8, one sentence).
- LM27 (brief): E5, its two frames and the drift (27.1); the cost function and the self-financing trade with
  $W^{\mathrm{pre}}_t$ (27.2); $\mathrm{TO}_t$ and the cost approximation (27.3); $\mu_p$ and $\sigma_p^2$ (27.4);
  $\operatorname{Cov}(R_i,R_p)=(\Sigma\mathbf w)_i$ and $\beta_{i,p}$ with $\sum_iw_i\beta_{i,p}=1$ (27.5). LM29 cites
  these by tag number (decision C8).
- LM28 (brief): (28.1) the equality-constrained minimum and its multipliers; (28.2) $\mathbf w^{\mathrm{mv}}$
  and $\Sigma\mathbf w^{\mathrm{mv}}=\sigma^2_{\min}\mathbf 1$; (28.4)–(28.5) the frontier with $\mathrm{SR}_\infty$;
  (28.6) $\mathbf w^{\mathrm{tan}}$ and its existence condition; (28.7) the CML; (28.8) the exposure form with $\delta$;
  E9's sign of cvxpy's equality duals (A28-33). LM28's numbers that LM29 quotes, each cited to its anchor where it
  is printed (decisions A4, C12): the 92 signals and the first window's dates (A28-02), the first window's inputs,
  $\mathbf w^{\mathrm{mv}}$ and $\sigma^2_{\min}$ (A28-05 to A28-07, A28-10), $\mathbf w^{\mathrm{tan}}$ and
  $\mathrm{SR}^*=0.880$ (A28-18), the 22 windows with $r_f\ge\mu_{\mathrm{mv}}$ (A28-23, A28-24), U28's unconstrained
  $\mathbf w^{\mathrm{mv}}$ (A28-13). That R3's bounds never bind on E5 is LM29's own result (A29-09, decision A5),
  which LM28's A28-12 and LM30's A30-16 echo.

**Leads:** `[30, 31, 32, 33, 34, 35]`, from the second cross-check's tag-user table (Y1; decision "Tags and leads").
LM30 cites (29.3) for the uniqueness of its long-only minimizer, (29.4) and (29.5) for constraints as implicit
shrinkage, its (30.4), whose multipliers are half of (29.5)'s (LM30 says so once; decision B4), and (29.6) for the
homogenized QP of its resampling experiment. LM31 cites (29.2), (29.3) and (29.5) for the ERC problem's strict
convexity, its unique minimizer and the equal $(\Sigma\mathbf w)_i$ of held funds. LM32 cites (29.1) and (29.3) for
problem 12's expected-shortfall minimization, and LM35 cites (29.4) for its bounded reverse stress test. LM33 and LM34
cite no tag; they use R3 and R4 in the long-only form LM29 defines. Each of LM30–LM35 lists 29 among its prerequisites
(their briefs, 2026-10-24), so the leads hold both ways (decision C9). LM43 is not listed.

**Forward links honoured.**

| Earlier text | Promise | Kept in |
|:--|:--|:--|
| lm07.md:268 | a PSD Hessian everywhere makes $h$ convex and any critical point a global minimum, "stated without proof; [[LM29]] develops convexity" | §2: (29.1) in $\mathbb R^N$; (29.2) the Hessian test derived from LM4's one-variable test along segments; the gradient inequality (Deep Dive); critical point ⇒ global minimum and local ⇒ global, (29.3) |
| lm07.md:522 | the KKT conditions, "[[LM29]] applies the conditions to larger portfolios" | §4–§5: (7.13) written for a minimization, (29.4); derived for long-only minimum variance, (29.5); sufficiency proved for convex problems with linear constraints, necessity stated; R3 and R4 on five funds, long-only minimum variance on U28's 28 sectors |
| lm10.md:446 | "For functions that are not quadratic, the same conclusion needs the argument of [[LM29]]" | §2: the Hessian test for any twice-differentiable function on a convex open set; §7 adds the cost function, convex as a sum of maxima of linear functions, where no Hessian exists |
| lm10.md:449 (中文) | 二次函數是凸函數若且唯若矩陣半正定，「這是 [[LM28]] 與 [[LM29]] 求解最佳化的基礎」 | §2 and §4: PD ⇒ strictly convex ⇒ at most one minimizer; §2's 導讀 says it in Chinese |
| lm07.md:531 | sufficiency "see Boyd and Vandenberghe (2004, §5.5.3)" | §4 proves sufficiency for linear constraints and cites §5.5.3 (p. 244) for the general statement |
| src/syllabus.yaml:77 | "Quadratic programs, KKT conditions, cvxpy; long-only, leverage and turnover limits" | §3 (limits as constraints), §6 (the gross limit in X2), problems 10 (turnover) and 11 (financed leverage), the lab |

The grep of `src/*.md` and `src/pages/*.md` for `[[LM29]]` finds exactly lm07.md:268, lm07.md:522, lm10.md:446 and
lm10.md:449, the spine's four; no plain "LM29" occurs in `src/`, and `build/make_lab*.py` has none. The spine missed
none. lm07.md:531 has no pointer but holds the sufficiency claim that LM29 proves, and the syllabus line names leverage
and turnover limits; both are added here.

**Outcomes** ("After this module you should be able to:"; the level shows in the verb; each within 30 words,
decision C10):

1. [D] prove that a convex problem's local minimum is global, and test convexity by Hessians, sums and maxima
2. [C] write portfolio limits as linear constraints, and recognize infeasible, unbounded and non-convex problems
3. [D] derive the KKT conditions of long-only minimum variance, and prove them sufficient for convex problems
4. [C] compute R3 and R4 in their long-only form, and explain each zero weight by its multiplier
5. [C] compute the shadow price of a limit, and check it by moving the limit
6. [C] add trading costs to the objective, find the no-trade band, and weigh turnover against in-sample risk
7. [C] solve a problem in cvxpy with scaled inputs and set tolerances, and verify it by KKT residuals
8. [U] explain what KKT necessity needs and what a solver's status guarantees, and choose a solution method

**Owns.** Convex sets in $\mathbb R^N$ (segments, intersections; hyperplanes, half-spaces, the long-only orthant, a
cap, the 1-norm ball of a gross limit, the risk ellipsoid $\mathbf w^{\top}\Sigma\mathbf w\le(25\%)^2$) and two
non-convex sets (a volatility floor alone, which holds $\mathbf w$ and $-\mathbf w$ but not $\mathbf 0$; a limit on the number of funds); convex functions: the chord definition
(29.1), the Hessian test derived along segments from LM4 (29.2), the gradient inequality (Deep Dive), sums with
non-negative weights and pointwise maxima ($\lvert x\rvert$, $\max(0,-x)$, $\lVert\cdot\rVert_1$, LM27's
$\operatorname{cost}(\cdot)$), strict convexity; the convex problem (29.3): a local minimum is global, a critical point
of a differentiable convex objective on an open set is a global minimum, a strictly convex objective has at most one
minimizer; quadratic programs in standard form and linear programs as the case of a linear objective (E2's optimum
by a direct comparison); infeasible, unbounded and non-convex problems and the solver statuses that report them; the
KKT conditions for a minimization (29.4) with LM7's signs, derived for long-only minimum variance (29.5), sufficiency
proved for convex objectives with linear constraints, necessity stated (a constraint qualification, which linear
constraints satisfy); each optimum proved by exhibiting a KKT point (no existence theorem is used; decision F);
active sets, why long-only weights hit zero, and why solvers do not enumerate $2^N$ active sets; R3 and R4 in their
through-case (long-only) form, R4's homogenization derived (29.6) and its KKT reading (29.7), a fund held only when
its excess return pays for its beta to the portfolio; multipliers as shadow prices (29.8), local and global, checked
by moving a limit; one cap (R3 with 40% on any fund) and the cost of limits in Sharpe ratio; the long-only frontier
against LM28's; costs as a term in the objective (29.9), the no-trade band and its threshold, the cost weight's
units, the turnover–risk trade-off on R3's path (planned figures, relative to $\theta=0$); modelling in cvxpy,
default solvers, scaling, tolerances, statuses, dual signs and the shared "Solver output" rule; checking an answer
(feasibility, KKT residuals, a second solver, a closed form on the active set). Values owned: every A29 anchor except
the echoes inside them, which are cited to their owners where printed (decision C12): LM27's E5 frame counts (A27-02,
A27-03, in A29-01), LM28's first-window figures (A28-02 in A29-02; A28-05 to A28-07 in A29-27; A28-10 in A29-23 and
A29-29), A28-13, A28-23 and A28-24, and LM30's A30-22 (U28's first half). LM29 is the single owner of "R3's bounds
never bind on E5" (A29-09; decision A5, Y12).

**Leaves.** Shrunk and robust inputs, and constraints as implicit shrinkage (Jagannathan and Ma 2003) → LM30. Realized
out-of-sample volatility: R3 → LM30, R4 → LM33 (decision A3); R3's and R4's Sharpe statistics and every standard error
→ LM33; their executed turnover, annual turnover, costs and net results → LM34 (decision A2). U28's halves (their
long-only portfolios, 1/N and minimum variance) → LM30 (decision A5). Risk-parity formulations (the log-barrier ERC
problem, risk budgets) → LM31. Expected-shortfall minimization (Rockafellar–Uryasev, a linear program) → a problem in
LM32, citing (29.1) and (29.3). The wealth recursion and the cost function → LM27, cited. Duality beyond shadow
prices, the dual problem, Slater's condition in general, second-order cone theory and the algorithms (active-set,
operator splitting, interior point) → named, not developed (out of scope). Integer limits (a number of funds, round lots) → one sentence:
not convex, out of scope. Multi-period trading by convex optimization (Boyd et al. 2017) → one sentence. To the lab
and problems (density, spine): the turnover limit (problem 10), financed leverage (problem 11), the 92-signal solver
audit (problem 12 and the lab), infeasible and unbounded problems (§3's pitfall, problem 4).

**Uses before taught** (one sentence each in the text):

- §3: "A limit on volatility, such as $\mathbf w^{\top}\Sigma\mathbf w\le(25\%)^2$, is a second-order cone constraint; cvxpy
  sends such problems to a conic solver, and this module does not develop cone programming." (The solver is the
  installed cvxpy's choice, CLARABEL [A29-22]; Agrawal et al. 2018 describe the rewriting, not this case.)
- §4: "Constraining weights also acts as a shrinkage of $\hat\Sigma$, which [[LM30]] studies (Jagannathan and Ma 2003)."
- §5: "How R3 and R4 fare after their windows is the question of [[LM30]], [[LM33]] and [[LM34]]."
- §6: "Minimizing expected shortfall is a linear program ([[LM32]])."
- §7: "The executed trades, a session after the signal, and their costs in the wealth recursion are [[LM27]]'s and
  [[LM34]]'s; this section plans the trade at the signal close."
- §8: "OSQP solves a quadratic program by operator splitting and CLARABEL by an interior-point method; neither method is
  derived here (Stellato et al. 2020; Goulart and Chen 2024)."

**Data role.**

- **E5's estimation frame** (the through case): `vol5_series.frames("E5")` (`data/processed/vol5_frames.parquet`, built
  and checked by `data/vol5_series.py`), $T=2{,}362$ joint one-session total returns 2017-01-18 → 2026-10-08,
  $A=242.95$, the years counted in calendar days ÷ 365.25 from the close of 2017-01-17, the close before the first
  return (LM27's A27-02; decision C7, AUTHORING §8) [A29-01]. Windows: the trailing 504 joint dates (rows of the
  estimation frame) through each month-end signal, 92 signals, the first 2019-02-27 (window 2017-02-13 → 2019-02-27,
  traded 2019-03-04; LM28's A28-02), the last 2026-09-30 (window 2024-08-23 → 2026-09-30, traded 2026-10-01)
  [A29-02]. Inputs: $\Sigma=A\hat\Sigma$ (divisor $T$, `cov0`),
  $\boldsymbol\mu=A\bar{\mathbf R}$, $\mathbf e=\boldsymbol\mu-r_f\mathbf 1$ with $r_f=1.5\%$, LM7's illustrative rate (shared decision "Risk-free rate"; §5, §6 and problem 11 give 0% and 2% [A29-35]), annual, treated as known
  (*In-sample*). $A\hat\Sigma$ is positive definite at all 92 windows, smallest eigenvalue 0.0050 a year, $\kappa$ from
  9.72 to 20.46 [A29-03]. The case, §3, §5–§6 and E9 part 2 use the last window; problem 9, the widget, E9 part 1, X7's first column, KC §8 and problem 12(a) the first; §7 the windows of 2025-03-31 and 2025-04-30 (X5 every window). Every caption
  and note says "on the 504 joint dates" of its window, or "on each window's 504 joint dates" for the 92 signals
  (decision C2): X1–X4 and X6 the first form, X5 and X7 the second.
- **E5's wealth frame** (2,368 sessions; LM27's A27-03 [A29-01]): only for drift (each fund's own close-to-close
  return, a halted fund earning 0, LM27's (27.1)), in §7's E8 and X6, X5's cost sweep and problems 7 and 10: the
  target of the 2025-03-31 signal, traded at the close of 2025-04-01, drifts to the close of the 2025-04-30 signal
  [A29-19], which E8, X6 and problems 7 and 10 use [A29-20, A29-30, A29-32]; the cost sweep drifts each penalized
  target the same way [A29-21].
- **U28** (Volume II): `lm10_series.u28()` (`data/processed/vol2_closes.parquet`; FinMind `TaiwanStockPrice`, retrieved
  2026-10-11, with each flagged close replaced by the 13:30:00 value of `TaiwanStockEvery5SecondsIndex`, the Volume II
  repair, `data/README.md:114–130`), $T=4{,}382$ daily price returns and $A=245.48$ (lm10.md:41) [A29-13]. Covariance only (shared
  decision "Data"); price indices, said so in every caption. The halves (LM11's, lm11.md:387) are LM30's (decision A5):
  LM29 echoes the first half's held set (A30-22) in one sentence.
- **Conventions.** Solvers get the annual inputs, with the book's tolerances (`OSQP_OPTS`: `eps_abs` = `eps_rel` =
  1e-10, polishing; `CLARABEL_OPTS`: `tol_gap_abs` = `tol_gap_rel` = `tol_feas` = 1e-12 for quadratic and linear
  programs) unless a line says "default"; problem 11's cone problem uses 1e-10, as the shared decision "Solver output"
  now says, and its second solver, SCS, `eps` 1e-9 with 200,000 iterations (`SCS_OPTS` in the anchor script; the
  defaults cvxpy gives SCS are looser, 1e-5, `scs_conif.py:210–212`); the text states both. A fresh `Problem` each
  time; status `optimal` required; a weight with $\lvert w_i\rvert<10^{-6}$ prints as 0; a constraint is active when
  its slack is below $10^{-6}$. Every printed solution is checked against `vol5_rules`' exact solution (Cholesky
  factor and SciPy's `nnls`), a closed form or a second solver, and by its KKT residuals; the script stops if a check
  fails. A residual or gap at rounding level
  prints as a bound ("below 1e-15"), because its digits depend on the exact reference's own rounding. Multipliers
  follow (29.4); cvxpy's duals are printed as cvxpy reports them. Planned turnover and cost are fractions of pre-trade
  wealth at the signal close, $\tfrac12\lVert\mathbf w-\mathbf w^{\mathrm{drift}}\rVert_1$ and LM27's
  $\operatorname{cost}(\cdot)$ (0.1425% on each side, tax 0.1% on sales except 00679B; the cost model's rates, cited by
  pointer); X5 prints its planned totals relative to $\theta=0$, so it uses no count of years. The cost-penalized
  problem goes to cvxpy as LM27's formula, `COMMISSION * cp.norm1(w - w_drift) + tax @ cp.pos(w_drift - w)`; the KKT
  derivation splits buys and sells, and solver gaps depend on the formulation (decision D). Weights print in percent;
  the max-Sharpe portfolios printed whole at two decimals (so that each sums to 100.00 as printed), a single weight quoted alone and the others at one. A
  derived result follows from the inputs printed beside it: X1's footer and X2 print the volatilities at two decimals,
  so that each Sharpe ratio recomputes from the printed weights, excess returns and volatility (R4's 2.11 from 18.85%;
  decision on the second recomputation), and problem 11 prints its exposures at two decimals with the three-decimal
  $\mathbf e$ of X4.
- **Seeds.** The text simulates nothing and the widget draws nothing. The lab's Part 2 is experiment 1: it draws its random chords with `default_rng([1, 20261011])`, created once, and prints the number of chords and the seed (AUTHORING §8).
- **Published files.** No daily series (decision X37): the chart JSON holds weights, frontier points computed on a
  grid of target means by `data/lm29_charts.py` (each a QP, checked as above), KKT quantities and the band; the widget
  embeds five numbers of the first window (echo of A28-05 to A28-07, unrounded in the data block, since the widget
  computes from them).
- **Scripts.** `data/lm29_numbers.py` (every printed value, asserted against `src/lm29.md`; compares with the anchors;
  flags rounding boundaries, e-notation included) and `data/lm29_charts.py` (X2–X4, X6 and the widget block), after
  `data/vol5_series.py`, `data/vol5_rules.py` (imported) and `data/lm10_series.py`.

**Hygiene declaration.** *In-sample:* every optimization (R3 and R4 on their windows' inputs, the caps, the limits,
the frontiers, the LP, the cost penalty, the turnover limit, financed leverage), every in-sample Sharpe ratio and
volatility, and the cost sweep, which plans trades on R3's own path with the inputs visible at each signal close (no
look-ahead, but no out-of-sample claim either). *Echo:* U28's first half (LM30's A30-22), one sentence. *Descriptive:*
the 92-signal counts of active sets and of hedges. *Constructed:* the 40% cap, the 150% gross limit, the 5% turnover
limit, the 25% volatility limit, the cost weights $\theta$, the −0.01 bounds of E6, the 15% cap and the 0.01
volatility floor of E1 and E3, X3's 40% target mean, the widget's $\delta=4$ and cap 1, and problem 2's hypothetical
numbers, chosen by the drafter as illustrations, not rules. Count: on the last window the module compares four
maximum-Sharpe versions (X2), R3 at five cap levels (none, 39%, 40%, 41%, 42%), R4 with two relaxed bounds (E6), one LP
with a 40% cap (E2), one target mean on the two frontiers (X3) and three status examples (E3); on R3's path seven cost
weights (X5); at one signal one turnover limit (problem 10); financed leverage at two spreads (problem 11); R4 and problem 11's 2-point optimum at $r_f$ of 0% and 2% (shared decision "Risk-free rate"); and the
widget's initial state. None is a candidate rule: the out-of-sample family stays R1–R8, $n=8$ (shared decision "The
count of trials"). Local note: "Every portfolio here treats its sample's means and covariance matrix as known, so its weights, Sharpe
ratio and volatility are in-sample plug-in estimates with an unmeasured error. The windows are the through case's, fixed
in advance; R3 and R4 are two of its eight rules. The caps, limits and cost weights are illustrations, not rules, and
none is tested on later data. How R3 and R4 fare after their windows is the subject of [[LM30]], [[LM33]] and [[LM34]]."

**Notation.** AUTHORING §6 with the "Portfolios, risk and backtests" table. Used: $\mathbf w$, $N$ ($N=5$; 28 for
U28), $i$, $j$, $\mathbf 1$, $I$, $\Sigma$ (here $A\hat\Sigma$ of a window, treated as known), $\hat\Sigma$,
$\boldsymbol\mu$, $\mathbf e$, $r_f$, $\mu_p$, $\sigma_p$, $\sigma_p^2$, $\sigma_i$ (a fund's volatility: X1's column, the widget's $\sigma_1$, $\sigma_2$), $\rho$ (the correlation of the widget's two funds), $s_p$ (a sample portfolio volatility, §4's
U28 example), $\mathrm{SR}$, $\mathrm{SR}^*$ (the optimum of (29.6); LM28's unconstrained value is quoted as LM28's), $\mathbf w^{\mathrm{mv}}$, $\sigma^2_{\min}$, $\mathbf w^{\mathrm{tan}}$,
$\mathbf f$, $L$ (problem 11's total exposure $\mathbf 1^{\top}\mathbf f$), $\delta$ (LM28's; §6's $\delta$ row names
LM29), $\lVert\mathbf x\rVert_1$, $x$ (a generic real number in $\lvert x\rvert$ and $\max(0,-x)$, declared), $\mathbf y$ (§6's scoped row for LM29, decision B3), $K$, $\mathbf b$,
$\lambda$, $\boldsymbol\lambda$ (the vector of equality multipliers in (29.4), as LM28's), $\nu_i$, $\mathcal L$, $h$ (an objective), $\psi_i$ (a constraint function, LM7's), $J$ (LM7's
optimal value as a function of a limit), $H$ (a Hessian), $\nabla$, $\beta_{i,p}$, $\mathrm{TO}_t$, $\text{tax}_i$,
$\mathbf w^{\mathrm{drift}}_t$, $\mathbf w_{t-1}$, $\boldsymbol\Delta$ (a trade, LM27's cost argument),
$W^{\mathrm{pre}}_t$ (LM27's, cited in §7), $A$, $T$, $t$, $\tau$ (a holding period in years, §7), $\kappa$,
$\lambda_N$ (the smallest eigenvalue, subscripted), $\operatorname{cost}(\cdot)$ (LM27's, upright), $\operatorname{Cov}$.
Local symbols, declared in the notation note (decision B5 accepts them):

| Symbol | Meaning | Check |
|:--|:--|:--|
| $\mathbf y$ | R4's homogenized variable, $\mathbf w=\mathbf y/\mathbf 1^{\top}\mathbf y$ (shared decision "Through case") | §6's scoped row (LM29, LM31); LM29 has no regression; LM10's generic $\mathbf y$ in (10.10) becomes $\mathbf v$ here |
| $\mathbf u$, $\mathbf v$, $\omega$ | two generic points of $\mathbb R^N$ and the mixing weight of (29.1) | $\omega$ as LM10's (10.10); LM29 has no sample space; $u$ (a probability level) does not occur in LM29 |
| $\mathcal C$ | a convex set | calligraphic; $C$ stays a correlation matrix |
| $b_i$ | the level of inequality $i$, $\psi_i(\mathbf w)\le b_i$ (LM7's), and a cap's level in $w_i\le b_i$ | §6's $\psi$ row; not an entry of $\mathbf b$, the right-hand side of $K\mathbf w=\mathbf b$, which LM29 never writes entrywise |
| $\nu^{\mathrm{cap}}_i$ | the multiplier of a cap $w_i\le b_i$ | as §6's $\nu$, superscripted |
| $V$ | the optimal variance $\mathbf w^{*\top}\Sigma\mathbf w^*$ of a capped problem (E7, problem 8) | declared (X20); $\sigma_p^2$ stays a portfolio's variance in general |
| $\boldsymbol\Delta^{+}$, $\boldsymbol\Delta^{-}$ | buys and sells, $\boldsymbol\Delta=\boldsymbol\Delta^{+}-\boldsymbol\Delta^{-}$, both $\ge\mathbf 0$ | Boyd and Vandenberghe's $u_{\text{buy}}$, $u_{\text{sell}}$ (p. 156) in the book's letters |
| $\mathbf w^{+}$, $\mathbf w^{-}$ | long and short parts, $\mathbf w=\mathbf w^{+}-\mathbf w^{-}$, both $\ge\mathbf 0$ (§3's gross limit) | as $\boldsymbol\Delta^{\pm}$ |
| $\theta$ | the weight of a trading penalty in the objective: on $\operatorname{cost}$ in (29.9), annual variance per unit of wealth paid once; on $\mathrm{TO}$ in problem 10, annual variance per unit of turnover | §6: a parameter in a module without angles; LM4's (4.16) writes a parameter $\theta$ too |
| $\mathbb R^N$ | the space of $N$-vectors | standard |

Not used: $\mathbf x$ as a point or a variable (generic points are $\mathbf u$, $\mathbf v$, standard forms are
written in $\mathbf w$, and $\lVert\mathbf x\rVert_1$ is only §6's definition); $\mathbf e_i$ (LM27–LM31 write
none); $\gamma$ or $\lambda$ for risk aversion (§6's "Not used"); a scalar cost symbol beside $\mathrm{TO}$; a letter for
the borrowing spread (problem 11 writes it in words, $\text{spread}$; decision B6: $s$ would clash with $s_p$); $p^*$
for an optimal value (LM7's $J$ instead); $L$ as a Cholesky factor (LM29 names the factor in words); a star except on
an optimum ($\mathbf w^*$, $\mathbf y^*$, $\mathrm{SR}^*$).

**Motivating case: "Why does the long-only portfolio drop two funds?"** (box, about 160 words in three paragraphs of
at most 80 words; every sentence within 30 words, decision C10)

> On 30 September 2026 the through case re-estimates its inputs from its last 504 joint trading days, 23 August 2024
> to 30 September 2026 [A29-02]. Fed those means and that covariance matrix, LM28's tangency formula puts 114.24% in
> 0050 [A29-05]. It sells short 27.75% of 00646 and 48.48% of 00679B, and it buys 31.07% of 00635U and 30.92% of
> 00642U. Its gross exposure is 252%, for an in-sample Sharpe ratio of 2.18.
>
> The formula shorts at every one of the through case's 92 month-ends [A29-07]. A reader with a cash account can
> neither short nor borrow. Forbid both, and the best Sharpe ratio falls only to 2.11 [A29-06]. That portfolio holds
> 62.77% in 0050, 18.37% in 00635U and 18.86% in 00642U, and nothing in the other two.
>
> Three questions follow. Why is 00646's weight zero, when it earns 16.44 points a year above cash [A29-04]? What does
> each limit cost? And when a solver prints these weights, how can the reader tell they are right?

Resolved: (a) §5, X4: at R4, a fund is held only if its excess return pays for its beta to the portfolio; 00646 earns
16.437 points, but its beta to the portfolio, 0.54436, asks for $\beta_{i,p}(\mu_p-r_f)=0.54436\times39.722=21.623$, so
it falls 5.19 points short, and 00679B 6.48 [A29-04, A29-10]; (b) §6, X2: the Sharpe ratio falls from 2.18
(unconstrained) to 2.16 (gross ≤ 150%), 2.11 (long-only) and 2.00 (long-only with a 40% cap) [A29-15], and a
multiplier prices a small step of a limit (E6) [A29-11]; (c) §8, E9: every KKT residual of the two cvxpy solutions
(stationarity, signs, complementarity) is below 1e-13, a second solver agrees to 1.7e-13 in a weight, and LM28's
tangency formula applied to the three held funds reproduces R4 to rounding level, below 1e-15 [A29-25].

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | the layer LM29 adds (LM28 solved equalities in closed form; LM29 adds inequalities, a solver and the checks that the solver is right); case + X1; roadmap; notation and hygiene notes | 340 |
| 2 | Convex Sets and Convex Functions {1} | segments and convex sets; the portfolio sets (budget hyperplane, long-only orthant, a cap's half-space, the gross ball, the risk ellipsoid) and two that are not convex (a volatility floor alone; at most three funds); E1; (29.1), with LM10's (10.10) as the quadratic case; (29.2) by restriction to segments and LM4's test (honours lm07.md:268, lm10.md:446); the gradient inequality (Deep Dive); sums and maxima: $\lvert x\rvert$, $\max(0,-x)$, $\lVert\cdot\rVert_1$ and LM27's cost are convex; (29.3): local ⇒ global (proof, Boyd and Vandenberghe §4.2.2), critical point ⇒ global, strictly convex ⇒ unique; no existence theorem (decision F); 導讀; KC | 520 |
| 3 | Quadratic and Linear Programs {2} | the QP standard form (Boyd and Vandenberghe (4.34), p. 152) with $K\mathbf w=\mathbf b$ and inequality rows; long-only, caps, the gross limit by splitting $\mathbf w=\mathbf w^{+}-\mathbf w^{-}$ (LM8's gross exposure), a turnover limit; the volatility limit as a cone constraint, one sentence; the LP as the linear case: E2, its optimum proved by a direct comparison (no general vertex theorem; decision F); E3: infeasible, unbounded, not convex; pitfall: the status is part of the answer; KC | 400 |
| 4 | KKT Conditions for Long-Only Portfolios {3, 8} | (7.13) for a minimization, (29.4); derived for long-only minimum variance, (29.5): $\lambda=2\sigma_p^2$, held funds $\beta_{i,p}=1$, excluded $\beta_{i,p}\ge1$; sufficiency theorem and its two-line proof by the gradient inequality, general statement cited (Boyd and Vandenberghe §5.5.3, p. 244); necessity stated: a constraint qualification, which linear constraints satisfy (p. 227 with p. 244), LM7's independent gradients another; an optimum is proved by exhibiting a KKT point; E2's comparison read as a KKT point; on E5 R3's bounds never bind, its smallest weight over the 92 signals 0.13% (0050, 2024-11-29) [A29-09] (LM29 owns this; LM28 and LM30 echo it, decision A5); E4 on U28; the first half's held set in one sentence (LM30's A30-22, [[LM30]]); $2^{28}$ active sets and why solvers do not enumerate (SciPy's `nnls` is an active-set method, Lawson and Hanson 1995); 導讀; KC | 660 |
| 5 | R3 and R4 in the Through Case {4, 5} | R3 is (29.5) on each window; R4: scale invariance of the Sharpe ratio and the homogenized QP (29.6) derived (the change of variables of Boyd and Vandenberghe §4.3.2, p. 151, as the model), defined when some $e_i>0$; (29.7): held funds earn $\beta_{i,p}(\mu_p-r_f)$, excluded funds earn less; X4 and E5 at the last signal; $r_f=1.5\%$ is illustrative: at 0% and 2% R4 holds the same three funds, no weight moves more than 1.15 points, and its in-sample Sharpe ratio is 2.19 and 2.08 [A29-35]; the 92 signals: active sets, exclusions with $e_i>0$, hedges with $e_i\le0$ (A29-07, A29-08); R4 exists in LM28's 22 windows (A28-23); shadow prices (29.8), local (Boyd and Vandenberghe §5.6.3, p. 251, stated) and checked by E6; the case resolved (a); 導讀; KC | 680 |
| 6 | Caps, Gross Limits and the Long-Only Frontier {5, 2} | E7 (R3 with a 40% cap): $\lambda=2V+0.40\,\nu^{\mathrm{cap}}$, betas, the price of one point of cap, the linear prediction a lower bound ((5.57), p. 250, stated); the cap binds at 63 of 92 signals [A29-14]; X2: the cost of each limit in Sharpe ratio, the case resolved (b); X3: the frontiers with and without long-only limits; financed leverage in one paragraph (problem 11: the long-only tangency at the borrowing rate, scaled; at $r_f$ of 0% and 2% its 2-point optimum has $L=132.2\%$ and 130.6% [A29-35]); pitfall: a shadow price is a rate, not a total gain; KC | 470 |
| 7 | Costs in the Objective {6} | the cost model (LM27's (27.2), the cost decision); (29.9); $\theta$'s units and $\theta=2/(\delta\tau)$ with LM28's $\delta$; convexity (§2); buys and sells split for the KKT conditions (Boyd and Vandenberghe p. 156), so they need no subgradients, while cvxpy receives the cost as written; the band; E8 on 2025-04-30 with X6; the no-trade threshold (Deep Dive); X5 on R3's path, relative to $\theta=0$; a turnover limit is a penalty at the right $\theta$ (problem 10); hygiene: planned figures, illustrations; [[LM34]] for executed turnover and costs; Boyd et al. (2017) in one sentence (their abstract: a single-period trade solves a convex problem trading off expected return, risk, transaction cost and holding cost; the multi-period method named only); 導讀; KC | 620 |
| 8 | Solvers and How to Check Them {7, 8} | cvxpy in one paragraph (Diamond and Boyd 2016; problems built from convex atoms; "cvxpy rewrites (canonicalizes) a problem into the standard form of a solver it selects", Agrawal et al. 2018, read in arXiv v2: abstract, §1.3, §4); the default solvers, their names and defaults resting on the installed cvxpy 1.9.3 (A29-22), not on the paper; scaling: absolute tolerances against the objective's size, E9 part 1 and X7; tolerances, polishing and the shared rule; statuses; the checking procedure on R4 (E9 part 2): feasibility, stationarity, signs, complementarity, a second solver, a closed form on the active set; cvxpy's dual signs; which tool when: a closed form (no inequality binds), an exact active-set solution (small long-only QPs), a general solver (caps, costs, cones); pitfall: "optimal" on badly scaled inputs; KC | 540 |
| 9 | Convex Optimization in Python {7} | code: R3 and R4 in cvxpy with the book's options; `nnls` for the exact answer; a KKT check of a few lines; lab box | 180 |
| — | Summary (8) / Problems (12) / Solutions | | 140 / 400 / 520 |
| | **Total** | | **5,470** |

**Elements.** 9 examples (E1 §2; E2, E3 §3; E4 §4; E5, E6 §5; E7 §6; E8 §7; E9 §8). Outcome map (taught /
practised / assessed, REVIEW_PROMPT item 10): 1 §2 / E1 / KC §2, P1, P8(c); 2 §3 / E2, E3 / KC §3, P3, P4; 3 §4 / the
derivation, E4 / P8, P2; 4 §5 / E5 / KC §5, P5, P9; 5 §5–§6 / E6, E7 / KC §6, P10; 6 §7 / E8, X5 / KC §7, P7, P10; 7 §8–§9
/ E9 / KC §8, P6, P11, P12; 8 §4, §8 / E9 / KC §4, KC §9, P12(c). Knowledge checks:

- §2: Show that LM27's cost, $\sum_i[0.1425\%\lvert\Delta_i\rvert+\text{tax}_i\max(0,-\Delta_i)]$, is convex using only
  sums and maxima ($\lvert x\rvert=\max(x,-x)$). Then show that "at most three funds" is not convex: two three-fund
  portfolios can average to one that holds all five.
- §3: Write "at most 40% in any fund, at least 10% in 00679B, gross exposure at most 150%" as linear rows, splitting
  $\mathbf w=\mathbf w^{+}-\mathbf w^{-}$ for the gross limit. Why is a 15% cap on each of five funds infeasible
  [A29-18]?
- §4: At U28's long-only minimum variance, Cement is excluded with $\beta_{i,p}=1.000019$, the closest of the 19
  excluded sectors to the threshold 1 [A29-13]. What do (29.5)'s conditions say about it, and what would a slightly
  lower covariance with the portfolio change? Why must R3 satisfy (29.5) at all (necessity needs a constraint
  qualification, which linear constraints satisfy)? (The active set itself is an estimate; [[LM30]].)
- §5: From $\beta_{i,p}=0.54436$, $\mu_p-r_f=39.722\%$ and $e_i=16.437\%$ [A29-04, A29-10], find 00646's
  shortfall: $0.54436\times39.722-16.437=5.19$ points (5.18612 unrounded).
- §6: With $\nu^{\mathrm{cap}}=0.01054$ [A29-14], predict the change in R3's variance when the cap rises from 40% to
  41%: $-0.000105$. The exact change is $-0.000102$. Why does the linear prediction overstate the gain (the optimal
  value is convex in the limit, so its tangent lies below it)?
- §7: At $\theta=1$ on 2025-04-30, 0050's gradient is 0.017684, while the band runs from 0.015235 (buy) to 0.019085
  (sell) [A29-20]. Why is 0050 left untouched?
- §8: CLARABEL's default absolute tolerance is 1e-8 [A29-22]. At the first signal R3's optimal variance is 1.035e-5 in
  daily units and 2.515e-3 in annual units (LM28's $\sigma^2_{\min}$, A28-10), $A$ times larger [A29-23]. Why does
  the daily problem miss the weights by 8.6e-4 and the annual one by only 1.6e-5?
- §9: In cvxpy 1.9.3, which solver does `cp.Problem(cp.Maximize(mu @ w), [cp.sum(w) == 1, w >= 0, w <= 0.4]).solve()`
  call [A29-17]? Why should a script name its solver anyway?

中文導讀 in §2 (凸集 (convex set), 凸函數 (convex function), 凸組合 (convex combination), 半正定 (positive
semidefinite), 嚴格凸函數 (strictly convex function); LM10's PSD sentence restated), §4 (KKT 條件, 互補鬆弛性
(complementary slackness), 影子價格 (shadow price), 約束規範 (constraint qualification); LM7's 緊 and 鬆弛, and the
active constraints called 有效限制 (active constraint), as LM7's Glossary does; "active set" kept in English), §5
(切點投資組合 (tangency portfolio), 夏普比率 (Sharpe ratio); why a positive excess return is not enough), §7 (交易成本
(transaction cost), 週轉率 (turnover), 懲罰函數 (penalty function); "no-trade band" kept in English), §8 (目標函數
(objective function), 限制條件 (constraint), 對偶變量 (dual variable) with its English at first use, and one sentence
that a solver's dual variables are the KKT multipliers, LM7's 乘數; 內點法 (interior-point method) if the box names
the method; a solver's status read before its weights). The box writes 對偶變量, never LM18's 對偶變數 (antithetic
variates). Terms and sources under "Chinese terms" below.

Deep Dives: §2 "The gradient inequality": for a differentiable convex $h$, (29.1) with $\mathbf u+\omega(\mathbf
v-\mathbf u)$ gives $[h(\mathbf u+\omega(\mathbf v-\mathbf u))-h(\mathbf u)]/\omega\le h(\mathbf v)-h(\mathbf u)$, and
$\omega\to0$ gives $h(\mathbf v)\ge h(\mathbf u)+\nabla h(\mathbf u)^{\top}(\mathbf v-\mathbf u)$ (Boyd and Vandenberghe
§3.1.3, p. 69; for a quadratic it is (10.9) with $\boldsymbol\Delta^{\top}M\boldsymbol\Delta\ge0$). §7 "When not
trading is optimal": at $\mathbf w=\mathbf w^{\mathrm{drift}}$ with every drifted weight positive, (29.9)'s conditions
ask for one $\lambda$ with $(2\Sigma\mathbf w^{\mathrm{drift}})_i-\theta(0.1425\%+\text{tax}_i)\le\lambda\le
(2\Sigma\mathbf w^{\mathrm{drift}})_j+\theta\,0.1425\%$ for all $i$, $j$, which exists exactly when $\theta\ge
\max_{i\ne j}[(2\Sigma\mathbf w^{\mathrm{drift}})_i-(2\Sigma\mathbf w^{\mathrm{drift}})_j]/(2\times0.1425\%+\text{tax}_i)$.

**Exhibits.**

- X1 `case` (table, §1): the last window, 2024-08-23 → 2026-09-30 (504 joint daily total returns, annualized with
  $A=242.95$ (LM27's A27-02) [A29-01]). Rows: the five funds. Columns: mean, volatility, excess return $e_i$ (% a
  year); unconstrained tangency and R4 weights (%, two decimals). Values: means 48.78, 17.94, −5.78, 20.68, 36.10;
  volatilities 26.32,
  17.89, 13.11, 24.30, 49.71; $e_i$ 47.28, 16.44, −7.28, 19.18, 34.60 [A29-04]; tangency 114.24, −27.75, −48.48, 31.07,
  30.92 [A29-05]; R4 62.77, 0, 0, 18.37, 18.86 [A29-06]. Footer rows: Sharpe ratio 2.18 against 2.11, gross 252%
  against 100%, volatility 31.94% against 18.85% [A29-05, A29-06], two decimals so that each ratio recomputes from the
  printed weights and $e_i$ (decision on the second recomputation). Note: in-sample, on the 504 joint dates;
  $r_f=1.5\%$; the tangency is LM28's (28.6), not a rule. Source: FinMind `TaiwanStockPrice`, `TaiwanStockDividendResult`,
  `TaiwanStockSplitPrice` (E5, retrieved 2026-10-24, `data/README.md`); Computations: `data/lm29_numbers.py`.
- X2 `limits` (`bar`, grouped, §6): categories the five funds; series the four maximum-Sharpe portfolios
  "unconstrained", "gross ≤ 150%", "long-only (R4)", "long-only, cap 40%" (four colour tokens; portfolios as series,
  funds as categories, shared decision "Charts"); `y` weight in % (`fmt: "n2"`), `hline` at 0. Values: (114.24, −27.75,
  −48.48, 31.07, 30.92), (78.82, −7.59, −17.41, 23.36, 22.82), (62.77, 0, 0, 18.37, 18.86), (40.00, 14.37, 0, 27.48,
  18.15); Sharpe ratios 2.18, 2.16, 2.11, 2.00; volatilities 31.94%, 23.01%, 18.85%, 16.40% [A29-15], given in the
  legend names or the note, two decimals so that each ratio recomputes from the printed weights and X1's $e_i$.
  Note: in-sample, on the last window's 504 joint dates; the limits are constructed.
- X3 `frontier` (`scatter` with `curves`, approved C2, §6): $x$ volatility, $y$ mean (% a year), last window. Curves:
  the unconstrained frontier (dashed) and the long-only frontier (solid) on a grid of target means that includes the cited 4.12%, 30.44% and 40% [A29-16], the two capital
  market lines from $r_f$ (dashed, thin; slopes 2.18 and 2.11). Points: the five funds (one named series, labels);
  `points` for R3 = global minimum variance (mean 8.46%, volatility 10.10%), R4 (41.22%, 18.85%) and the unconstrained
  tangency (71.13%, 31.94%), two decimals so that each slope recomputes from its point [A29-05, A29-06, A29-16]. Values
  cited: the curves coincide for target means from 4.12% to 30.44%; at a target of 40% the volatility is 18.29%
  unconstrained and 18.32% long-only; the long-only frontier ends at 0050 (48.8%, 26.3%) [A29-16]. Note: in-sample,
  on the last window's 504 joint dates; the long-only frontier lies on or to the right of the unconstrained one.
- X4 `kktR4` (`bar`, §5): categories the five funds; series "excess return $e_i$" and "beta × (μ_p − r_f)" (% a year,
  `fmt: "n3"`, three decimals so that the gaps recompute from the bars): 0050 47.275 and 47.275, 00646 16.437 and
  21.623, 00679B −7.276 and −0.797, 00635U 19.178 and 19.178, 00642U 34.596 and 34.596 [A29-04, A29-10]. Note: R4 at the
  last signal; equal bars mark held funds, (29.7); the two gaps are 5.19 and 6.48 points ($\nu_i/\lambda$) [A29-10];
  in-sample, on the last window's 504 joint dates.
- X5 `costsweep` (table, §7): R3's path with the cost penalty, 91 rebalancing signals, planned at each signal close.
  Rows $\theta$ = 0, 0.25, 0.5, 1, 2, 5, 10. Columns: planned turnover and planned cost, each summed over the 91
  signals as a percentage of $\theta=0$'s (decision A2); signals without a trade; in-sample volatility given up (bp,
  mean and largest). Values: 100.0, 100.0, 0, 0.0, 0.0; 58.4, 59.0, 11, 0.4, 1.5; 44.7, 45.5, 18, 1.5, 3.8; 31.5,
  31.8, 31, 4.9, 10.8; 22.3, 22.5, 40, 15.3, 27.7; 9.4, 9.7, 74, 47.9, 112.8; 4.7, 4.9, 85, 71.0, 283.0 [A29-21]. Note:
  in-sample illustration, not a rule, on each window's 504 joint dates; *planned* at the signal close, relative to R3
  itself ($\theta=0$); R3's own turnover and costs, executed a session later, are [[LM34]]'s; $\theta=2/(\delta\tau)$,
  so $\delta=4$ with monthly rebalancing (a holding period of $\tau=1/12$ year) is $\theta=6$ [A29-21].
- X6 `band` (`bar`, §7): 2025-04-30 at $\theta=1$: bars of $(2\Sigma\mathbf w)_i$ at the penalized solution (0.017684,
  0.019085, 0.015235, 0.015235, 0.019085; `fmt: "n6"`); dashed `hline`s at the buy edge 0.015235, the taxed sell edge
  0.019085 and 00679B's sell edge 0.018085 [A29-20]. Note: bought funds sit on the buy edge, sold funds on their sell
  edge, 0050 inside the band, untouched; in-sample, on the 2025-04-30 window's 504 joint dates.
- X7 `solvers` (table, §8): R3, largest weight gap to the exact solution, by units (daily, annual), solver (OSQP,
  CLARABEL) and tolerances (default, the book's). Columns: first signal; worst of the 92 signals. Values: daily OSQP
  default 8.3e-9 / 1.1e-8; daily CLARABEL default 8.6e-4 / 2.1e-3; daily CLARABEL book 3.2e-8 / 3.2e-7; annual OSQP
  default below 1e-15 / below 1e-15; annual CLARABEL default 1.6e-5 / 3.4e-5; annual CLARABEL book 2.0e-11 / 8.9e-9
  [A29-23, A29-24]; R4's worst row (annual CLARABEL default 9.5e-7) in the note. Note: on each window's 504 joint
  dates; cvxpy 1.9.3, OSQP 1.1.3, CLARABEL 0.11.1; the defaults are CLARABEL's 1e-8 gaps and cvxpy's OSQP 1e-5 with
  polishing [A29-22]; OSQP at the book's tolerances gives the same gaps as at its defaults in both units (8.3e-9 /
  1.1e-8 daily, below 1e-15 annual), so its two rows are left out and the note says so; a cell at rounding level is
  printed as a bound; the lab prints all 16 cells of A29-24.

**Widget `kktPair` — "Active sets with two funds and cash."** `Book.controls`: a slider for the cap on net exposure
$f_1+f_2\le$ cap (0.2 to 2.0, step 0.05), a slider for $\delta$ (1 to 10, step 0.5). Problem: maximize
$\mathbf f^{\top}\mathbf e-\tfrac{\delta}{2}\mathbf f^{\top}\Sigma\mathbf f$ subject to the cap, $f_1\ge0$, $f_2\ge0$,
the rest in cash at $r_f$ (LM28's exposure form with LM7's KKT example's constraints). Chart (`scatter`): the
$(f_1,f_2)$ plane with the feasible triangle (`lines`), utility contours (`ellipses` with $\mathrm{cov}=\Sigma^{-1}$
about the unconstrained optimum $\Sigma^{-1}\mathbf e/\delta$), and the candidates of the eight binding sets (`points`:
the optimum, the only candidate passing both feasibility and signs, in colour 1 and labelled; the others in muted
grey). Readouts: a table of the seven solvable binding sets ($f_1$, $f_2$, multipliers, feasible?, signs?, utility);
the binding set at the optimum; one line saying how many candidates pass each test and that only the optimum passes
both. Caption: "first window, 2017-02-13 → 2019-02-27, on its 504 joint dates; in-sample" (A28-02), naming the sample
of $\mathbf e$, $\sigma$ and $\rho$ (shared decision "Data"). Initial state (PDF): cap 1, $\delta=4$, first window,
0050 and 00646: unconstrained $(0.16, 1.42)$ breaks the
cap; the optimum binds the cap and $f_1\ge0$ at $(0,1)$ with multipliers 0.0289 and 0.0031 and utility 0.0571; of the
7 solvable binding sets 4 pass feasibility and 3 the signs, but only the optimum passes both: the unconstrained point
and the cap-only point pass the signs and are infeasible [A29-27]. Data block `chart-lm29-kktPair`: $e_1$, $e_2$,
$\sigma_1$, $\sigma_2$, $\rho$ of the first window, unrounded, from `data/lm29_charts.py`; the readout prints them as
6.04%, 8.53%, 13.50%, 11.87% and 0.539 (echo of A28-05 to A28-07). That is one digit more than LM28 prints, because the
readout's unconstrained point (0.16, 1.42) is computed from them and LM28's printed inputs (one decimal, the
correlation two) do not reproduce it (decision C12's exception). Each candidate solves a system of at most 5×5
(two exposures and up to three binding constraints) with a determinant check, module-local code under 30 lines,
tested against the anchor script's `pair_kkt` as `data/lm15_charts.py` does (shared decision "Widgets"); no optimizer
in the browser.

**Examples** (results recomputed from the printed inputs):

- E1 §2 `sets`: the budget $\mathbf 1^{\top}\mathbf w=1$ (a hyperplane), $\mathbf w\ge\mathbf 0$ (an orthant), $w_i\le
  40\%$ (a half-space), $\lVert\mathbf w\rVert_1\le1.5$ (a 1-norm ball) and $\mathbf w^{\top}\Sigma\mathbf w\le(25\%)^2$
  (an ellipsoid, $\Sigma$ PD) are convex, so their intersection is; a volatility floor $\mathbf w^{\top}\Sigma\mathbf
  w\ge0.01$ is not (it holds $\mathbf w$ and $-\mathbf w$ but not $\mathbf 0$; cvxpy refuses it with a `DCPError` [A29-18]), nor is "at most three funds". The variance $\mathbf w^{\top}\Sigma\mathbf w$ is strictly convex by (29.2), since its Hessian $2\Sigma$ is PD.
- E2 §3 `lp`: last window, maximize $\boldsymbol\mu^{\top}\mathbf w$ subject to $\mathbf 1^{\top}\mathbf w=1$ and
  $0\le w_i\le40\%$, with the means 48.775% (0050), 36.096% (00642U) and 20.678% (00635U) the three highest: 40% in
  0050, 40% in 00642U and 20% in 00635U, mean $0.4\times48.775+0.4\times36.096+0.2\times20.678=38.08\%$ [A29-04,
  A29-17]. A direct comparison proves it: since both portfolios sum to 1, $\boldsymbol\mu^{\top}\mathbf w-
  \boldsymbol\mu^{\top}\mathbf w^*=\sum_i(w_i-w^*_i)(\mu_i-20.678\%)$, and every term is $\le0$: the two top funds have
  $w_i\le40\%=w^*_i$ and a higher mean, the third fund's term is 0, and the other two have $w_i\ge0=w^*_i$ and a lower
  mean. §4 reads the same numbers as a KKT point of $\min-\boldsymbol\mu^{\top}\mathbf w$: $\lambda=-20.678\%$, minus the third mean, the caps' multipliers $\mu_i-20.678\%$ and the bounds' $20.678\%-\mu_i$, all non-negative. Since the five means differ, the difference is 0 only when the other four funds hold $\mathbf w^*$'s weights, and the budget then fixes the third: the optimum is unique. A linear objective concentrates up to the
  limits; only a risk term diversifies.
- E3 §3 `status`: a 15% cap on five funds is `infeasible` (`prob.value` `inf`, `w.value` `None`); maximizing the mean with only the budget is
  `unbounded` (also `prob.value` `inf`, `w.value` `None`); the volatility floor alone is not a convex set and cvxpy will not build it [A29-18]. With the budget, on the last window, it would exclude nothing. Every fully invested portfolio there has a variance of at least R3's, 0.0102 [A29-12], because R3's bounds do not bind [A29-09].
- E4 §4 `u28`: long-only minimum variance of U28's 28 sector price indices (full sample, covariance only): 9 of 28 held,
  volatility 12.10% in sample, $\lambda=0.0293$; the 19 excluded sectors have $\beta_{i,p}$ from 1.000019 (Cement) to
  1.480 (Optoelectronic), each $\ge1$ as (29.5) requires [A29-13]; LM28's unconstrained $\mathbf w^{\mathrm{mv}}$ holds 12
  shorts with gross 2.24 (A28-13). There are $2^{28}=268{,}435{,}456$ candidate active sets [A29-13]. On U28's first
  half alone, which [[LM30]] studies, the long-only portfolio again holds 9 sectors (LM30's A30-22), but only 7 of them
  are among the full sample's 9 [A29-13]: the active set is itself an estimate.
- E5 §5 `r4` (X4): R4 at the last signal. $\lambda=0.45062$; $\nu$ = 0.02337 (00646) and 0.02920 (00679B), 0 for the
  held funds; $\beta_{i,p}$ = 1.190, 0.544, −0.020, 0.483, 0.871; $\mu_p-r_f=39.72\%$; $\nu_i/\lambda$ = 5.19 and 6.48
  points [A29-10]. Over the 92 signals R4 holds one, two, three, four or five funds at 2, 21, 56, 13 and 0 signals; a
  fund with $e_i>0$ was excluded 80 times in 460, and a fund with $e_i\le0$ held 6 times, as a hedge with
  $\beta_{i,p}<0$ (for example 00679B on 2021-08-31 at 14.4% with $e_i=-1.74\%$) [A29-07, A29-08].
- E6 §5 `bump` (shadow price): relax $y_i\ge0$ to $y_i\ge-0.01$ in R4's homogenized QP, where
  $\mathrm{SR}=1/\sqrt{\mathbf y^{*\top}\Sigma\mathbf y^*}=2.1067$. For 00646 the Sharpe ratio rises by 0.001084, against
  the first-order gain $\mathrm{SR}^3\nu_i\times0.01/2=0.001093$ of (29.8) with $\nu_i=0.02337$; for 00679B it rises by
  0.001358 against 0.001365 ($\nu_i=0.02920$) [A29-10, A29-11]. The levels: 2.106733 → 2.107817 (00646) and 2.108091
  (00679B) [A29-11].
- E7 §6 `cap`: R3 with $w_i\le40\%$, last window. R3 holds 56.5% in 00679B [A29-06]; capped: 6.0, 26.9, 40.0, 19.3,
  7.8%, volatility 10.52% against 10.10%; $V=0.0110665$, $\nu^{\mathrm{cap}}=0.010543$ and
  $\lambda=0.026350=2V+0.40\,\nu^{\mathrm{cap}}$; the four free funds have $\beta_{i,p}=\lambda/2V=1.191$, 00679B
  $(\lambda-\nu^{\mathrm{cap}})/2V=0.714$; raising the cap to 41% changes the variance by $-0.000102$ against the
  first-order $-0.000105$ [A29-14]. R3's largest weight exceeds 40% at 63 of 92 signals [A29-14].
- E8 §7 `rebal` (X6): 2025-04-30. The 2025-03-31 target, traded on 2025-04-01, has drifted to 2.2, 31.8, 35.7, 23.9,
  6.4%; trading to the new R3 would turn over 18.72% and cost 0.072% of wealth [A29-19]. With $\theta=1$ the
  penalized trade buys 4.6 points of 00679B and 6.7 of 00635U, sells 9.9 of 00646 and 1.4 of 00642U, and leaves 0050;
  turnover 11.30%, cost 0.0435%, in-sample volatility 9.03% against R3's 8.97% and no trade's 9.51%; $\lambda=0.016660$,
  band 0.015235 to 0.019085 (0.018085 for 00679B) [A29-20]. No trade is optimal for $\theta\ge3.20$, set by selling
  00646 against buying 00635U [A29-19].
- E9 §8 `check`: (1) units: at the first signal CLARABEL's defaults miss R3's weights by 8.6e-4 on daily inputs and
  1.6e-5 on annual ones; OSQP's polishing reaches 8.3e-9 and rounding level, below 1e-15 [A29-23]. (2) R4 at the last
  signal, both solvers `optimal`, the residuals computed from each solver's $\mathbf y$ with
  $\lambda=2\mathbf y^{\top}\Sigma\mathbf y$ (the value that $\mathbf e^{\top}\mathbf y=1$ gives): OSQP's stationarity
  on held funds, smallest $\nu$ and complementarity are below 1e-15; CLARABEL's are 9.3e-15, −9.3e-15 and 1.5e-14, and
  its weights lie 1.7e-13 from the exact ones; LM28's (28.6) on {0050, 00635U, 00642U} gives R4 to below 1e-15
  [A29-25]. (3) cvxpy's dual of the equality is $-\lambda$: −0.020396 for R3's budget (so $\sigma_p=\sqrt{\lambda/2}=10.10\%$), −0.4506
  for R4's $\mathbf e^{\top}\mathbf y=1$; the bound duals are the $\nu_i$: 0.0234 and 0.0292 [A29-26, A29-12].

**Problems plan** (12; MC keys C, A, B, C, A, B; the lab solves 9–12). Stems state the window (dates, 504 joint daily
total returns), $A=242.95$ (A27-02), the divisor $T$, annual inputs, $r_f=1.5\%$, the solver and its tolerances, the
zero threshold $10^{-6}$, weights in % to the printed decimals, and for costs 0.1425% on each side and tax 0.1% on sales
(0 for 00679B), planned at the signal close.

1. MC: the set $\{\mathbf w\in\mathbb R^N:\mathbf w^{\top}\Sigma\mathbf w\ge0.01\}$, $\Sigma$ PD, is: A
   convex, because $\Sigma$ is PD. B convex, because its constraint is a polynomial. **C** not convex: it holds $-\mathbf w$
   whenever it holds $\mathbf w$, but not their midpoint $\mathbf 0$ (cvxpy: `DCPError` [A29-18]).
2. MC (hypothetical): long-only minimum variance, $\min\mathbf w^{\top}\Sigma\mathbf w$ with (29.5)'s multipliers, at $\sigma_p^2=0.0102$ (annual); an excluded fund has $\operatorname{Cov}(R_i,R_p)
   =0.015$. Its multiplier $\nu_i$: **A** 0.0096. B 0.0048 (the 2 dropped). C −0.0096 (the sign reversed). Its
   $\beta_{i,p}=1.47$ [A29-28].
3. MC: last window, means (48.775, 17.937, −5.776, 20.678, 36.096)% [A29-04]; maximize the mean subject to the budget
   and $0\le w_i\le40\%$. A 20% each. **B** 40% 0050, 40% 00642U, 20% 00635U (mean 38.08%). C 100% 0050 (the cap
   ignored) [A29-17].
4. MC: minimum variance with the budget and a 15% cap on each of five funds. A each fund at 15%. B unbounded. **C**
   infeasible: the caps sum to 75% [A29-18].
5. MC: cvxpy reports the dual −0.4506 of $\mathbf e^{\top}\mathbf y=1$ in R4's homogenized QP on the last window; the in-sample Sharpe ratio is:
   **A** $\sqrt{2/0.4506}=2.107$. B $\sqrt{1/0.4506}=1.490$ (the 2 dropped). C 0.4506 (the dual read as the ratio)
   [A29-34].
6. MC: cvxpy reports the budget dual −0.020396 for R3 on the last window; R3's volatility: A 14.28% ($\sqrt\lambda$,
   the 2 dropped). **B** $\sqrt{0.020396/2}=10.10\%$. C undefined (the sign kept) [A29-33].
7. 2025-04-30: the variance gradient at the drifted weights, $2\Sigma\mathbf w^{\mathrm{drift}}=(0.02318, 0.02513,
   0.01383, 0.01280, 0.02503)$ [A29-32], every drifted weight positive. Find the smallest $\theta$ at which no trade is
   optimal and the pair that sets it: 3.20 (3.2026 from these inputs, 3.2022 unrounded), selling 00646 against buying
   00635U [A29-32, A29-19].
8. Derive: (a) the KKT conditions are sufficient for $\min h(\mathbf w)$, $h$ convex and differentiable, subject to
   $K\mathbf w=\mathbf b$ and $\mathbf w\ge\mathbf 0$; (b) with the budget and caps $w_i\le b_i$, show that $\lambda=
   2V+\sum_ib_i\nu^{\mathrm{cap}}_i$ at $h=\mathbf w^{\top}\Sigma\mathbf w$, and check it on E7: $0.026350=2\times
   0.0110665+0.40\times0.010543$ [A29-14]. (c) Prove from (29.1) that a convex problem's local minimum is global, and show by (29.2) that $-\sum_i\ln w_i$ is strictly convex on $\mathbf w>\mathbf 0$.
9. First window (2017-02-13 → 2019-02-27; A28-02): R3 equals LM28's $\mathbf w^{\mathrm{mv}}$, (10.7, 22.5, 41.4,
   25.0, 0.4)% (A28-10), because no bound binds [A29-09]. Compute R4: 10.57% 0050, 52.44% 00646, 36.99% 00679B,
   in-sample Sharpe ratio 0.802 against LM28's unconstrained 0.880 (A28-18), with $\nu_i/\lambda$ of 0.25 points
   (00635U) and 8.01 (00642U) [A29-29]; check R4 by LM28's (28.6) on the three held funds. Python part: the closed form
   against `nnls`.
10. Python: 2025-04-30, R3 with planned turnover at most 5% (CLARABEL, the book's tolerances): (2.2, 27.4, 36.9, 27.7,
    5.8)%, volatility 9.24%, multiplier 0.00825 [A29-30]. Show that the penalty $\theta\,\mathrm{TO}$ with $\theta$ equal
    to that multiplier gives the same weights (gap below 1e-9), and explain by the KKT conditions of both problems. Then weigh turnover against risk: the limit gives 9.24% [A29-30], against R3's 8.97% at a turnover of 18.72% [A29-19, A29-20] and no trade's 9.51% [A29-20].
11. Python: financed leverage on the last window: maximize
    $\mathbf f^{\top}\mathbf e-\text{spread}\times\max(0,\mathbf 1^{\top}\mathbf f-1)$ subject to
    $\mathbf f^{\top}\Sigma\mathbf f\le25\%^2$, $\mathbf f\ge\mathbf 0$, $\lVert\mathbf f\rVert_1\le1.5$, for a spread of
    0 and of 2 points over $r_f$ (R8's financing rate, shared decision), with the window's unrounded $\mathbf e$. Solve
    it with CLARABEL at 1e-10 (a cone problem; at 1e-12 it returns `optimal_inaccurate`) and with SCS (eps 1e-9,
    200,000 iterations; SCS 3.3.1 [A29-22]), and check both against the exact solution below. With no spread: R4
    scaled by $25/18.85=1.326$, $\mathbf f=(83.23, 0, 0, 24.36, 25.00)\%$, $L=132.6\%$, excess return 52.67%. With 2
    points the borrowed part costs $r_f$ plus 2 points, so the optimum is the long-only tangency at 3.5%, (64.40, 0, 0,
    16.67, 18.93)%, scaled by $25/19.08=1.310$: $\mathbf f=(84.36, 0, 0, 21.83, 24.81)\%$, $L=131.0\%$, excess return
    52.65% before financing and 52.03% after it ($2\times0.310=0.62$ points). The 1.5% is illustrative: at $r_f$ of 0% and 2% the 2-point optimum has $L=132.2\%$ and 130.6%, and excess returns of 54.01% and 51.38% after financing [A29-35]. Each exposure is the scale times the
    unrounded weight, so it can differ in its last digit from the product of the printed numbers. The excess returns
    recompute from the printed exposures and X4's three-decimal $\mathbf e$, but solving with those $\mathbf e$ would print 00642U's 18.93 as 18.94. CLARABEL and SCS agree with these to within 1e-6 [A29-31]. Explain both,
    and why the volatility limit binds and the gross limit does not.
12. Python: (a) solve R3 at the first signal in daily and in annual units with OSQP and CLARABEL, at default and the
    book's tolerances, and report the weight gaps to `nnls` [A29-23]; (b) repeat over the 92 signals and for R4
    [A29-24]; (c) explain the pattern from the size of the objective (1.035e-5 against 2.515e-3, LM28's $\sigma^2_{\min}$,
    A28-10) and CLARABEL's absolute tolerance 1e-8, and why OSQP's polishing hides it [A29-22, A29-23].

**Lab parts** (`build/make_lab29.py`; reads only its `data/`: E5's estimation and wealth frames and R3's and R4's
per-signal target weights, derived by `make_lab_data.py`, which writes both frames (shared decision "Labs";
decisions on the first revision);
`sectors_close_raw.csv` and `sectors_close_repairs.csv` for U28, built as LM23's lab builds them): 1 data, $A$, the 92
windows, eigenvalues [A29-01 to A29-03]; 2 convexity checked numerically on random chords (experiment 1, `default_rng([1, 20261011])`; the variance and the cost;
no claim beyond the check), E1; 3 R3 and R4 by `scipy.optimize.nnls` on the Cholesky factor and by cvxpy, checked
against the derived targets at all 92 signals (the lab re-implements only LM29's long-only forms); 4 X4, E5, the
hedges, E6; 5 E4 (the halves are LM30's lab); 6 E7, X2, X3, E2, E3; 7 E8, X6, X5; 8 E9, X7 with all 16 cells of
A29-24; 9 problems 9–12. Extension (*In-sample*): enumerate R4's 31 non-empty supports at the first signal
($2^5-1$), solve LM28's (28.6) on each, keep those that are non-negative and pass the sign test of (29.7), confirm
that exactly one survives and equals `nnls`'s, time the loop, and extrapolate to U28's $2^{28}$ sets; a closing
sentence says that the surviving active set is itself an estimate (LM30). Labs write plain "LM30", never `[[LM30]]`.

**Cross-module tags.** The users are the second cross-check's table (Y1, taken by grep of the revised briefs, the
"tags I cite" notes excluded) and are cited by number (decision C8); a tag lists only the modules that cite it, and
speculative users are not listed.

- (29.1) $\mathcal C$ convex: $\omega\mathbf u+(1-\omega)\mathbf v\in\mathcal C$ for $\mathbf u,\mathbf v\in\mathcal C$,
  $\omega\in[0,1]$; $h$ convex on convex $\mathcal C$: $h(\omega\mathbf u+(1-\omega)\mathbf v)\le\omega h(\mathbf u)+
  (1-\omega)h(\mathbf v)$; strictly, with $<$ for $\mathbf u\ne\mathbf v$ and $0<\omega<1$ (LM32).
- (29.2) for $h$ twice differentiable on a convex open set: convex ⇔ $H(\mathbf u)$ PSD everywhere; $H$ PD everywhere ⇒
  strictly convex; and, for differentiable convex $h$, $h(\mathbf v)\ge h(\mathbf u)+\nabla h(\mathbf u)^{\top}(\mathbf
  v-\mathbf u)$ (LM31).
- (29.3) a convex problem, $\min h(\mathbf w)$ subject to $\psi_i(\mathbf w)\le b_i$ ($h$, $\psi_i$ convex) and $K\mathbf
  w=\mathbf b$: every local minimum is global; a strictly convex $h$ has at most one minimizer (LM30, LM31, LM32).
- (29.4) KKT for a minimization with LM7's signs: $\nabla h(\mathbf w^*)=K^{\top}\boldsymbol\lambda-\sum_i\nu_i\nabla
  \psi_i(\mathbf w^*)$, $\psi_i(\mathbf w^*)\le b_i$, $\nu_i\ge0$, $\nu_i\big(b_i-\psi_i(\mathbf w^*)\big)=0$, $K\mathbf
  w^*=\mathbf b$; sufficient for a convex problem (proved for linear $\psi_i$); necessary under a constraint
  qualification, which linear constraints satisfy (stated); for $\mathbf w\ge\mathbf 0$ the term is $+\boldsymbol\nu$,
  for a cap $-\nu^{\mathrm{cap}}_i$ (LM30, LM35).
- (29.5) long-only minimum variance: $2\Sigma\mathbf w^*=\lambda\mathbf 1+\boldsymbol\nu$, $\boldsymbol\nu\ge\mathbf 0$,
  $\nu_iw^*_i=0$; $\lambda=2\sigma_p^2$; $\nu_i=2[\operatorname{Cov}(R_i,R_p)-\sigma_p^2]$, so $\beta_{i,p}=1$ for held
  and $\beta_{i,p}\ge1$ for excluded funds (LM30, whose multipliers are half of these; LM31).
- (29.6) when some $e_i>0$: $\max\mathbf e^{\top}\mathbf w/\sqrt{\mathbf w^{\top}\Sigma\mathbf w}$ over $\mathbf w\ge
  \mathbf 0$, $\mathbf 1^{\top}\mathbf w=1$ is solved by $\mathbf w^*=\mathbf y^*/\mathbf 1^{\top}\mathbf y^*$, $\mathbf
  y^*$ minimizing $\mathbf y^{\top}\Sigma\mathbf y$ subject to $\mathbf e^{\top}\mathbf y=1$, $\mathbf y\ge\mathbf 0$;
  $\mathrm{SR}^*=(\mathbf y^{*\top}\Sigma\mathbf y^*)^{-1/2}$ and $\lambda=2/\mathrm{SR}^{*2}$ (LM30).
- (29.7) at R4: $\nu_i/\lambda=\beta_{i,p}(\mu_p-r_f)-e_i\ge0$, with equality for held funds (cited by no later brief;
  §5 and X4 use it).
- (29.8) shadow prices: $\partial J/\partial b_i=-\nu_i$ where $J$ is differentiable (stated, Boyd and Vandenberghe
  §5.6.3), and relaxing one level $b_i$ by any amount lowers $J$ by at most $\nu_i$ times that amount, for a convex problem with linear
  constraints (stated, their (5.57), which needs strong duality; the refined Slater condition gives it for linear
  constraints, p. 227) (cited by no later brief).
- (29.9) cost-penalized rebalancing: $\min\mathbf w^{\top}\Sigma\mathbf w+\theta\operatorname{cost}(\mathbf w-\mathbf
  w^{\mathrm{drift}})$ subject to $\mathbf 1^{\top}\mathbf w=1$, $\mathbf w\ge\mathbf 0$; at the optimum
  $(2\Sigma\mathbf w)_i=\lambda-\theta\,0.1425\%$ for a bought fund, $\lambda+\theta(0.1425\%+\text{tax}_i)$ for a sold
  fund still held, and in between for an untouched fund still held ($w_i>0$); with every drifted weight positive, no trade iff $\theta\ge\max_{i
  \ne j}[(2\Sigma\mathbf w^{\mathrm{drift}})_i-(2\Sigma\mathbf w^{\mathrm{drift}})_j]/(2\times0.1425\%+\text{tax}_i)$
  (cited by no later brief).

**Pitfalls to pre-empt.**

- Units. A solver's absolute tolerance is set against the objective's size: daily inputs make R3's variance 1.035e-5,
  and CLARABEL's default 1e-8 then misses weights by 8.6e-4 (up to 2.1e-3 over the 92 signals) [A29-23, A29-24]. Give
  solvers annual inputs (shared decision "Solver output").
- Status first. `infeasible`, `unbounded` and `optimal_inaccurate` are answers; a `DCPError` means the problem as
  written is not convex (E3). Read the status before the weights; `Variable.value` is `None` when there is no solution.
- Near-zeros. An interior-point solution leaves weights and trades of 1e-13 to a few 1e-6 where the exact answer has zeros
  (CLARABEL's $\min y=2.0\text{e-}13$ [A29-25]; on the cost sweep, with the cost given to cvxpy as `norm1` and `pos`,
  its weights differ from OSQP's by a few 1e-6 [A29-21]); print $\lvert w_i\rvert<10^{-6}$ as 0 and count active
  constraints by the stated slack.
- Dual signs. cvxpy's dual of an equality is $-\lambda$ in LM7's convention; its inequality duals are the $\nu_i\ge0$
  [A29-26]; LM28's E9 says the same (A28-33). Problems 5 and 6 test the misreadings.
- A shadow price is a rate, not a total gain (PITFALLS §7): the 41% cap gains $0.000102$, not the predicted $0.000105$,
  and the first-order estimate is always on the optimistic side for a convex problem (E7).
- Homogenization needs some $e_i>0$, and $\mathbf w=\mathbf y/\mathbf 1^{\top}\mathbf y$ needs $\mathbf 1^{\top}\mathbf
  y>0$; with no positive excess mean R4 falls back to R3 (shared decision; never on E5).
- The active-set example: R3's bounds never bind on E5 [A29-09] (LM29 owns this; LM28's A28-12 and LM30's A30-16 echo
  it, decision A5), so §4 uses U28 and §5 R4 (LM28's proposal, accepted by decision D).
- Enumeration: each inequality doubles the number of binding sets (8 for the widget's three, $2^{28}$ for U28's
  bounds); list them all, as LM7 and the widget do (PITFALLS §7: an enumeration once missed two cases).
- $\theta$ has units: a one-time cost against an annual variance. Changing the rebalancing interval changes the
  $\theta$ that a given risk aversion implies ($\theta=2/(\delta\tau)$).
- Planned against executed: §7's turnover and costs are planned at the signal close and printed relative to
  $\theta=0$; LM34 owns R3's executed and annual figures.
- Labels: the unconstrained solutions are LM28's, not R3 and R4 (LM28's pitfall); every figure here is *In-sample*.
- KKT necessity needs a constraint qualification; for a non-convex problem a KKT point need not be optimal (one
  sentence in §4).
- References: LM29 cites Boyd and Vandenberghe by the pages read in the authors' PDF; Nocedal and Wright's Theorem 12.1
  (LM7's citation) is not relied on (Sources).

**Curriculum guidance carried** (`plans/curriculum-guidance.md`, as adopted in the shared decisions).

- The capability layer (g:30): §1 says what LM29 adds to LM28: inequalities, a solver, and the checks.
- Outcome levels (g:54–58): marked above; the outcome map under Elements (g:124, REVIEW_PROMPT item 10).
- Density (g:60–63): the turnover limit and financed leverage go to problems 10–11, the 92-signal solver audit to
  problem 12 and the lab, the support enumeration to the lab; U28's halves are LM30's.
- Decision flow (g:69–85), LM29's part: §7 takes the target from the window's estimate at the signal close, plans the
  trade from the drifted holdings, and puts the costs in the objective; execution a session later and the costs in
  the wealth recursion are LM27's and LM34's, said in one sentence.
- Checkpoint after Volume VI (g:45, "explain how constraints change the allocation"): X2, E5 and E7 are its LM29 part.
- Limits and costs fixed before evaluation (g:111): none of LM29's limits is evaluated out of sample; they are
  declared illustrations, counted in the hygiene note.

**Stage 4 for earlier modules.** `leads` gain 29 in lm04.md:6, lm08.md:6, lm09.md:6, lm11.md:6 and lm12.md:6, as the
plan's merged list (decision G) has them; lm07.md:6 and lm10.md:6 already list 29. No wording change: lm07.md:268,
522 and 531 and lm10.md:446 and 449 read correctly against the plan.

**Sources** (full citations; the version read and the locations, as the source checks verified them: decision F's
check, the second hunt (`plans/vol-5.md`, "Sources read by the second hunt") and the SOURCES drafts of 2026-10-24,
whose Crossref records were re-read anonymously; paraphrase only).

- Boyd, S., and L. Vandenberghe (2004). *Convex Optimization*. Cambridge University Press. DOI
  10.1017/CBO9780511804441 (Crossref: monograph issued 2004-03-08; print ISBN 978-0-521-83378-3, online ISBN
  978-0-511-80444-1); in SOURCES' first papers list ("Boyd & Vandenberghe (2004) — Stanford PDF"), with the sections below under "Entries already in this list: Volume V locations". Read in the authors' PDF
  (`web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf`, whose copyright page reads "First published 2004" and "Seventh
  printing with corrections 2009"); every page below was re-checked in a fresh download of that PDF and by the second
  recomputation: first-order conditions §3.1.3, p. 69; second-order conditions §3.1.4, p. 71; pointwise maximum §3.2.3,
  p. 80; local and global optima §4.2.2, p. 138; linear-fractional programs and their change of variables §4.3.2, p.
  151; the QP form (4.34), §4.4, p. 152; §4.4.1, subsection "Markowitz portfolio optimization", p. 155, and its linear
  transaction costs with buy and sell variables, p. 156; the refined Slater condition (5.27), §5.2.3, p. 226,
  which reduces to feasibility for linear constraints (p. 227); KKT conditions sufficient for convex problems, and necessary and
  sufficient under Slater's condition, §5.5.3, p. 244; the global inequality (5.57), §5.6.2, p. 250; local
  sensitivity, §5.6.3, p. 251. The text cites sections and pages of this printing. SOURCES records the sections.
- Diamond, S., and S. Boyd (2016). "CVXPY: A Python-Embedded Modeling Language for Convex Optimization." *Journal of
  Machine Learning Research* 17(83): 1–5. No DOI. Abstract only (the JMLR page, `jmlr.org/papers/v17/15-408.html`,
  re-read: authors, volume, pages): a modelling language embedded in Python, in which a problem is written in natural
  syntax instead of a solver's standard form. Text not read; cited for the language only. Its solver list is outdated
  (survey), so the text names the solvers from A29-22.
- Agrawal, A., R. Verschueren, S. Diamond and S. Boyd (2018). "A Rewriting System for Convex Optimization Problems."
  *Journal of Control and Decision* 5(1): 42–60 (Crossref: issued 2018-01-02, online 2018-01-19). DOI
  10.1080/23307706.2017.1397554. Read in full by the second hunt in arXiv:1709.04494v2 (22 January 2019; v1 13
  September 2017), which describes CVXPY 1.0: the abstract (p. 1), §1.3 (pp. 4–5) and §4 (p. 15) say that cvxpy
  finds a suitable solver and rewrites (the paper's word is "canonicalizes") the problem into that solver's standard
  form. §8 prints that sentence (decision "Sources read by the second hunt"). The locations are arXiv v2's; the text
  cites no journal page. Kept out: where cvxpy 1.9.3 sends a volatility limit, and every solver name and default,
  which rest on A29-22 (the paper does not treat that case).
- Stellato, B., G. Banjac, P. Goulart, A. Bemporad and S. Boyd (2020). "OSQP: An Operator Splitting Solver for
  Quadratic Programs." *Mathematical Programming Computation* 12(4): 637–672 (Crossref: online 2020-02-20, print
  December 2020). DOI 10.1007/s12532-020-00179-2. Cited only for the method's name, which the title states; text not
  read.
- Goulart, P. J., and Y. Chen (2024). "Clarabel: An Interior-Point Solver for Conic Programs with Quadratic
  Objectives." arXiv:2405.12762 (v1, 21 May 2024; the arXiv API record and abstract, re-read: a general-purpose
  interior-point solver for conic problems, based on a homogeneous embedding and distributed as a standard solver of
  the Python CVXPY suite). A preprint; no journal version checked. Cited for the method's name.
- Boyd, S., E. Busseti, S. Diamond, R. N. Kahn, K. Koh, P. Nystrup and J. Speth (2017). "Multi-Period Trading via
  Convex Optimization." *Foundations and Trends in Optimization* 3(1): 1–76, August 2017. DOI 10.1561/2400000023.
  Crossref lists the seven authors as Boyd, Diamond, Koh, Nystrup, Busseti, Kahn, Speth; Boyd's page
  (`web.stanford.edu/~boyd/papers/cvx_portfolio.html`) and arXiv:1705.00109, both re-read, give the order printed
  here, which is cited. Abstract only (all three agree): in single-period optimization the trades solve a convex
  problem that trades off expected return, risk, transaction cost and holding cost. Text not read; used for that one
  sentence.
- Lawson, C. L., and R. J. Hanson (1995). *Solving Least Squares Problems*. SIAM. DOI 10.1137/1.9781611971217
  (Crossref: monograph issued 1995-01-01; print ISBN 978-0-89871-356-5, online ISBN 978-1-61197-121-7). The series
  name is not printed: no record checked confirms it. Cited through the `scipy.optimize.nnls` docstring of SciPy 1.18.1 [A29-22]
  (re-read in the project environment), which cites the book as "SIAM, 1995" and says the function uses an active-set
  method that solves the KKT conditions of non-negative least squares. The book was not read.
- Kuhn and Tucker (1951), Karush (1939) and Kjeldsen (2000): through LM7's reference list (lm07.md:780–782), by
  pointer, with no new claim; SOURCES holds no reading of Karush's thesis.
- Jagannathan, R., and T. Ma (2003), *Journal of Finance* 58(4): 1651–1683: LM30's entry (shared decision
  "References"); LM29 names it once, in §4's shrinkage sentence, lists it in its References and claims nothing beyond LM30's reading.
- Software facts (the installed environment and `uv.lock`; the SOURCES draft's cvxpy entries, read in the installed
  source): cvxpy 1.9.3, OSQP 1.1.3, CLARABEL 0.11.1, SCS 3.3.1 and SciPy 1.18.1 [A29-22]; the default solver of each problem class,
  observed by `Problem.solver_stats.solver_name` [A29-17, A29-22] and read in `cvxpy/problems/problem_form.py:373–387`;
  cvxpy's OSQP defaults (`eps_abs` = `eps_rel` = 1e-5, `max_iter` 10,000, polishing on a fresh solve;
  `reductions/solvers/qp_solvers/osqp_qpif.py:111–114, 147–148`) and CLARABEL's `DefaultSettings()` (gaps and
  feasibility 1e-8, 200 iterations) [A29-22]; for SCS, cvxpy turns `eps` into `eps_abs` and `eps_rel` and sets both
  when neither is given (`reductions/solvers/conic_solvers/scs_conif.py:206–212`), so problem 11 states its settings;
  `psd_wrap` asserts that a matrix is PSD without testing it (`atoms/affine/wraps.py:83–96`), and every matrix the
  anchor script wraps is a window's $A\hat\Sigma$ or its daily version, positive definite at all 92 windows (A29-03);
  the statuses of A29-18;
  cvxpy's dual signs as the installed version reports them [A29-26]. cvxpy's "Advanced Features" page (re-read; not
  pinned to 1.9.3) says that a constraint's `dual_value` holds its optimal dual variable and states no sign for
  equalities, so the text checks the sign against a closed form, as LM28's E9 does. cvxpy's "Solver Features" page is
  not relied on.
- The cost model's rates (commission 0.1425%, tax 0.1% on sales, 0 for 00679B): the shared decision "Cost model",
  cited by pointer; LM34 owns and prints the sources. Each fund follows its own market's rules (00679B on TPEx, the
  other four on TWSE; the shared decision as amended on 2026-10-25), and the model charges 0.1425% on each side on both markets. That is the posted reference rate: TWSE's
  Art. 94 and TPEx's 業務規則 Art. 64 ¶1–¶3 (unchanged since 2008-02-12; applied to ETFs by its ETF rules' Art. 15
  ¶1) let brokers set their own rates and require notice to the client above 1.425‰. It is not a cap, and brokers'
  discounts are not modelled. No rate of LM29's changes. The 0.1% on the futures ETFs 00635U and 00642U rests on the
  Ministry of Finance's ruling 台財稅字第09700161260號 (2008-08-11), with TWSE's ETF page and 財政統計通報 No. 21 in
  support; the decisions on the first revision keep the rate, so A29-19 to A29-21, A29-30 and A29-32 stand.
- Bibliographic data only (checked, not relied on): Nocedal, J., and S. J. Wright (2006). *Numerical Optimization*,
  2nd ed. Springer Series in Operations Research and Financial Engineering. New York: Springer. DOI
  10.1007/978-0-387-40065-5; LM7's source for KKT necessity (its Theorem 12.1, text not read). Further reading only, if
  Stage 2 wants it: Cornuéjols, Peña and Tütüncü (2018), *Optimization Methods in Finance*, 2nd ed., Cambridge
  University Press, DOI 10.1017/9781107297340; Kolm, Tütüncü and Fabozzi (2014), "60 Years of Portfolio Optimization:
  Practical Challenges and Current Trends", *European Journal of Operational Research* 234(2): 356–371, DOI
  10.1016/j.ejor.2013.10.060 (Crossref; texts not read).
- Dropped (decision F): the general extreme-value theorem in $N$ variables and the vertex theorem of linear
  programming, for which no verified source was found; LM29 proves each optimum by exhibiting a KKT point, and E2 by a
  direct comparison.

**Chinese terms** (樂詞網, terms.naer.edu.tw: the drafter's queries and the fresh pass of 2026-10-24, 1,817 searches,
whose readings this table follows; phrase match; AUTHORING §1; the shared decision "Chinese terms" and the decisions on
the second recomputation):

| English | 中文 | Listing |
|:--|:--|:--|
| convex set | 凸集 | 數學名詞, 統計學名詞 (工業工程名詞: 凸集合) |
| convex function; strictly convex function | 凸函數; 嚴格凸函數 | 數學名詞, 統計學名詞 (統計學名詞 also 狹義凸函數) |
| convex combination | 凸組合 | 數學名詞, 統計學名詞 |
| half space; hyperplane; convex polyhedron | 半空間; 超平面; 凸多面體 | 數學名詞 |
| convex programming | 凸規劃 | 數學名詞, 統計學名詞 (the plan's list; "convex optimization" has only 電子工程名詞's 凸形最佳化) |
| quadratic programming | 二次規劃 | 統計學名詞 (數學名詞: 二次型規劃; the plan keeps 二次規劃) |
| linear programming | 線性規劃 | 數學名詞, 統計學名詞 |
| feasible region | 可行解區域 | 數學名詞 (工業工程名詞: 可行區域) |
| complementary slackness | 互補鬆弛性 | 數學名詞 (LM7's box, lm07.md:572) |
| shadow price | 影子價格 | 數學名詞, also 經濟學 (lm04.md:734; LM7's Glossary, lm07.md:766) |
| constraint qualification | 約束規範 | 數學名詞 |
| sufficient condition; necessary condition | 充分條件; 必要條件 | 數學名詞 |
| positive semidefinite | 半正定 | 數學名詞 (lm10.md:302) |
| penalty function | 懲罰函數 | 數學名詞 |
| multiplier; dual variable | 乘數; 對偶變量 | 數學名詞 (乘數 as LM7). 對偶變量 carries "dual variable" at first use; it is not LM18's 對偶變數 (antithetic variates, lm18.md:570), and 電子計算機名詞 gives 對偶變量 to antithetic variates |
| active constraint | 有效限制 | 經濟學 (數學名詞: 起作用的約束); LM7's Glossary 緊限制式（有效限制） (lm07.md:769); "active set" has no entry and stays English |
| interior-point method | 內點法 | 統計學名詞 (數學名詞: interior point 內點); used only if a box names the method |
| slack; binding | 鬆弛; 緊 | LM7's box (lm07.md:571–572) |
| objective function; constraint | 目標函數; 限制條件 | 統計學名詞, 數學名詞 目標函數; 統計學名詞 限制條件 (LM7 also prints 限制式, lm07.md:353) |
| transaction cost; turnover | 交易成本; 週轉率 | 交易成本 管理學名詞 (also 經濟學, 管理學名詞-會計學); 週轉率 會計學 and 電子計算機名詞 (管理學名詞 writes 周轉率 for "turnover rate"); the LM27, LM31 and LM34 briefs plan 週轉率 too |
| Lagrange multiplier | 拉格朗日乘數 | engineering listings only; printed at lm04.md:282, lm07.md:353, lm11.md:312 |

Kept in English in the boxes: active set, no-trade band, operator splitting, solver (no entries). LM7's own 緊
(binding) and 鬆弛 (slack) are kept. SOURCES holds these terms (its Chinese-terms tables for Volumes V and VI, among them "LM29, LM30 and LM31 (new terms)").

**Open before Stage 2.** None; every item below is closed.

Closed by the editor's decisions on the briefs (the first draft's items, by number): 1, the shared solver numbers
(C1, X17): "Solver output" now quotes A29-24's 2.1e-3 and 3.4e-5, and the text prints A29-23 and A29-24 with their
definitions; 2, cone tolerances (C5, X19): the shared rule now gives 1e-12 for quadratic and linear programs and
1e-10 for cone programs, and problem 11 states 1e-10 and the status at 1e-12; 3, the cost weight's units and grid (D):
accepted, §7 works $\theta=1$ and states $\theta=2/(\delta\tau)$ once; 4, planned turnover (A2, X2): X5 prints its
totals relative to $\theta=0$, labelled *planned*, with a pointer to LM34, and no annual turnover or cost of R3; 5,
notation (B3, B5, B6, X20): $\mathbf y$ has §6's scoped row, the local symbols and $V$ are declared, and the spread is
written in words; 6, the case window: kept; 7, U28's halves (A5): LM30's, so A29-13 drops the halves' held sets and
echoes the first half's (A30-22); 8, the two unsourced theorems (F, X26): dropped, E2 proved by a direct comparison;
9, LM43: not listed; 10, E5's retrieval date (X9): `data/README.md:185` gives 2026-10-24, and X1's Source line cites
it; 11, the constructed limits (D): accepted, labelled *constructed* and counted in the hygiene note, which now also
counts E6's bounds, E1's and E3's settings, X3's target mean and the widget's state (recomputation, minor 8).

Closed by the decisions on the first revision and on the second recomputation (the first revision's four items, by
number): 1, the lab's estimation frame: `make_lab_data.py` writes both E5 frames, the wealth frame with its traded
flags (shared decision "Labs"; decisions on the first revision), so lab part 3 recomputes R3 and R4 at all 92
signals; 2, Agrawal et al. (2018): read in arXiv v2 by the second hunt, so §8 prints the canonicalization sentence
with its locations (abstract, §1.3, §4) and the solver names and defaults rest on A29-22 (decision "Sources read by
the second hunt"; Sources above); 3, the futures-ETF tax: kept at 0.1% (decisions on the first revision, "Kept"),
now resting on the Ministry of Finance's ruling (shared decision "Cost model"), so A29-19 to A29-21, A29-30 and
A29-32 stand and nothing is recomputed; 4, LM29's own count beside LM30's echo: "7 of the 9" is kept (decisions on the
first revision, "Kept"), in E4 beside A30-22.

Also settled in this revision, with no item left behind: the tag users and the Leads sentences (Y1, "Tags and
leads"); the single owner of "R3's bounds never bind" (A29-09; A5, Y12); the case box's paragraphs (C10, Y5); SCS's
settings, R4's volatility at 18.85% and problem 11's exposures at two decimals (the LM29 decision on the second
recomputation); echoes at the owner's precision, with the widget's inputs as the computation exception (C12); and
the Chinese terms 對偶變量 and 有效限制 (the decision's "Chinese terms").

Closed by the last pass (2026-10-25): the third verifier's five minor findings (the closing paragraph, the echoes of
$A$, the widget's caption, the header's Y list, the Notation list's unused symbol), and "Decisions on the third revision", whose
listing-market item names LM27, LM34 and LM35, not LM29; the cost model's amended market split changes none of LM29's
rates (Sources).

Closed by the fresh check of the whole of Stage 1 (2026-10-31): its 31 items on LM29, each applied with the
verifier's edit. Problem 1's set drops the budget; problem 11 solves with the unrounded $\mathbf e$; the shared
decision "Risk-free rate" is applied (§5, §6 and problem 11, A29-35); problem 8(c) assesses outcome 1's proof and
Hessian test, and problem 10 outcome 6's last clause; (29.8) relaxes one level $b_i$ at a time; the local note says
"plug-in estimates with an unmeasured error". The editor's choices: the bp columns' shown fourth decimals are flagged
(A29-21), and A29-35 is new. The anchors these items changed are recomputed by the script and listed in the anchors'
Status; the fresh verification of 2026-10-31 reproduced
them.

Nothing remains open for LM29. LM28's brief and anchors table (A28-12) and LM30's A30-16 cite A29-09 as the owner
(decision A5); nothing remains for the cross-check. No brief cites (29.7)–(29.9), so their tag lines name no user.

## LM30 Estimation Error and Robust Portfolios

Stage 1 brief, drafted 2026-10-24 from the editor's spine (`plans/vol-5.md`, "### LM30 Estimation Error and Robust
Portfolios"), the shared decisions, the capability check and the decisions on the survey and the fresh check; revised
the same day to the editor's decisions on the briefs (`plans/vol-5.md`, "Editor's decisions on the briefs", A–G and
"Per module"), the independent recomputation and the cross-module check; revised again the same day to the "Decisions
on the first revision", the "Decisions on the second recomputation and cross-check", the second recomputation and the
cross-check's Y items; finished on 2026-10-25 to the "Decisions on the third revision"; revised on 2026-10-31 to the
"Decisions on the fresh check of the whole of Stage 1" and its verifier's edits (the anchor rows they change, A30-05,
A30-12, A30-13, A30-22 and A30-26, are recomputed and were reproduced by the fresh verification of 2026-10-31). Every number carries its
anchor ID at first appearance; an echo cites its owner's anchor at the owner's precision, unless a computation shown
beside it needs more (decision C12; E2's $\tau$ and volatilities), and the anchors table names the LM30 row that
recomputes it.
`data/vol5_anchors_lm30.py` prints them all (43 rows, A30-41 withdrawn; the anchors section `## LM30`). Numbers quoted
from published modules carry their file:line instead. The through case's rules are imported from `data/vol5_rules.py`
and never recomputed. LM30 prints the statistics that the "Owners" bullet and decisions A4–A5 give it (the realized
out-of-sample volatility of R1, R3 and R5; the U28 halves' statistics; R2's first-window mean excess return and
volatility, the Black–Litterman calibration), every result of its own experiments, repairs and Black–Litterman
portfolios, and these statistics of the rules' targets: R5's intensity $\hat c$ at the 92 signals, R3's and R5's
weights at 2026-03-31 and their gaps, and the mean of R3's predicted volatility over its 92 windows.

**Prereq:** `[7, 9, 10, 11, 12, 14, 15, 16, 18, 20, 22, 23, 24, 26, 27, 28, 29]`. What each supplies (tags rechecked in
`src/lmNN.md` on 2026-10-24; LM27–LM29's from their Stage 1 briefs, to recheck at Stage 3):

- LM7: the two-asset tangency weights (7.10) and Kelly fractions (7.12) with their window-to-window swings (the
  exhibit {#kelly}, lm07.md:497–502); the pitfall that a mean's error is about $\sigma/\sqrt{\text{years}}$ (7.36
  points for 0050 over 2017–2021, lm07.md:507) and the Chopra–Ziemba sentence that hands the repair to LM30
  (lm07.md:509), which §2 cites as LM7 does.
- LM9: (9.5), the $2\times2$ inverse (problem 5; the variance-inflation reading of $\Sigma^{-1}$).
- LM10: (10.2) $\hat\Sigma$ with divisor $T$; (10.3) $C\leftrightarrow\hat\Sigma$; (10.5) $\mathbf w^{\top}\hat\Sigma\mathbf w\ge0$; (10.6) the variance of
  the 1/N portfolio, $\overline{\operatorname{var}}/N+(1-1/N)\overline{\operatorname{cov}}$ (§3, once: what 1/N's risk
  depends on);
  (10.7) $\operatorname{rank}\hat\Sigma\le\min(N,T-1)$, so U28's last 20 returns give a singular matrix; the constructed
  $C_{\text{pw}}$, its entries 0.982, 0.199, −0.444 and $\det C_{\text{pw}}=-0.374592$ (lm10.md:365–378), and the hand-over
  of its repair (lm10.md:386).
- LM11: (11.3) $M=Q\Lambda Q^{\top}$ (shrinkage toward $\bar\lambda I$ keeps $Q$ and moves $\Lambda$); (11.4) the
  eigenvalue bounds; (11.7) the instability of eigenvectors with close eigenvalues (what shrinkage cannot repair);
  (11.8) $\hat\Sigma^{-1}\mathbf b$ by components (the widget's closed form); (11.9) and U28's first-half
  $\kappa(\hat\Sigma^{(1)})=126.05$ (lm11.md:453, 468); the halves (2,191 returns each).
- LM12: (12.5) eigenvalues of $\hat\Sigma$ as squared singular values of $\tilde X/\sqrt T$; (12.6)
  $\kappa(\hat\Sigma)=\kappa(\tilde X)^2$; (12.7) the pseudoinverse (the singular $T=20$ row of [[ex:windows]]).
- LM14: (14.5), the kurtosis (raw, divisor-$T$ moments in every LM30 figure).
- LM15: TR23's maximum-likelihood $t$ fit, with 3.065 degrees of freedom, where the kurtosis is infinite (lm15.md:349, 378): the reason
  Ledoit and Wolf's moment conditions are stated with a warning (§4 pitfall).
- LM16: (16.4) $\Var(\mathbf a^{\top}\mathbf X)=\mathbf a^{\top}\Sigma\mathbf a$ (true volatility of an estimated
  portfolio); (16.8) the conditional law in a normal pair (the Black–Litterman posterior, coordinate by coordinate).
- LM18: (18.2) the variance of a mean (lm18.md:141), for §4's Deep Dive; (18.4) $\E\lVert\hat\Sigma_{\text{sim}}-\Sigma\rVert_F^2=(\lVert\Sigma\rVert_F^2+(\operatorname{tr}\Sigma)^2)/n$ and
  the Frobenius norm (lm18.md:165–167, Glossary lm18.md:568): the noise term of the oracle for normal returns.
- LM20: (20.1) $\operatorname{MSE}=\Var+\operatorname{Bias}^2$ (the oracle is its matrix form); (20.2)
  $\operatorname{SE}(A\bar R)=\sqrt A\sigma/\sqrt\tau$ with $\tau=T/A$, which depends on the years, not the number of
  days (LM20's second outcome); (20.5) the normal MLE divides by $T$; (20.9) the Sharpe ratio's variance (lm20.md:382), for §2's sentence on its noise.
- LM22: the iid bootstrap and (22.1) (experiment 4); the hand-over of resampled portfolios (lm22.md:390).
- LM23: (23.1) OLS betas (the single-index matrix of §7); (23.9) the VIF (problem 5 extends it to
  $(\Sigma^{-1})_{ii}=\operatorname{VIF}_i/\sigma_i^2$).
- LM24: (24.1) Bayes' rule; (24.3) the normal posterior mean with $c=T/(T+n_0)$ (the oracle's shape in §4 and the
  Black–Litterman weight in §6); (24.4) James–Stein; the sector halves, where every mean was shrunk to the grand mean
  and the second half's means spread by 8.49 points against the first half's 4.50 (lm24.md:279–285): means move.
- LM26: (26.2), named once as the recursion LM31 uses to forecast a covariance matrix (lm26.md:409's hand-over).
- LM27: R1 and R2, E5's two frames; (27.1)–(27.2), the wealth recursion behind a rule's realized volatility; (27.4)
  $\sigma_p^2=\mathbf w^{\top}\Sigma\mathbf w$; (27.5) $\Cov(R_i,R_p)=(\Sigma\mathbf w)_i$ (the reading of (30.4)'s
  multipliers); (27.8), the single-index split, whose diagonal-residual form is §7's matrix, with its $\Sigma_{\mathrm{res}}$;
  R1's first-window risk shares (A27-21, LM27's by decision A4), the truth of A30-42; R1's full-sample fixed-weight
  volatility 11.49% (A27-13), named beside the out-of-sample 12.48% [A30-12] in X1's note (decision C7).
- LM28: (28.2) $\mathbf w^{\mathrm{mv}}$ and $\Sigma\mathbf w^{\mathrm{mv}}=\sigma^2_{\min}\mathbf 1$; (28.3) the split of
  a fully invested portfolio's variance into $\sigma^2_{\min}$ and its weight error (the optimism of §2); (28.6)
  $\mathbf w^{\mathrm{tan}}$ and $\mathrm{SR}^{*2}=\mathbf e^{\top}\Sigma^{-1}\mathbf e$; (28.8) the exposure form
  $\Sigma^{-1}\mathbf e/\delta$ (LM28's $\mathbf f^*$, which LM30 does not write; inverted in §6 as $\mathbf e_{\mathrm{eq}}=\delta\hat\Sigma\mathbf w_{\mathrm{ref}}$);
  (28.9), cited in LM30's symbols as $\hat{\mathbf f}-\mathbf w^{\mathrm{tan}}=\Sigma^{-1}(\hat{\mathbf e}-\mathbf e)/\delta$ for the means-only plug-in (why errors in means move exposures; no $\mathbf f^*$ is printed); every statistic of
  the first window (decision A4), which LM30 echoes as its simulation's model at LM28's precision (decision C12):
  A28-02 (the window's dates and its calendar span, 2.05 years from the close of 2017-02-10; it computes $T/A$ and does
  not print it, and LM30's E2 prints it beside (20.2)), A28-05 to A28-07 (means and volatilities at one decimal, correlations at two; E2 prints the volatilities at two beside (20.2)), A28-10 ($\sigma_{\min}$),
  A28-15 (equal weights' mean and volatility), A28-18 ($\mathbf w^{\mathrm{tan}}$, $\mathrm{SR}^*$), A28-22 ($\delta$),
  A28-27 (the SEs of the means, one decimal); A28-12 (the 92 windows' $\sigma_{\min}$ range) and A28-14 (the halves'
  gross exposure), decision A5.
- LM29: (29.3), a strictly convex objective has at most one minimizer (so $\mathbf w^{\mathrm{lo}}$ is unique when
  $\hat\Sigma$ is PD); (29.4) and (29.5), the KKT conditions of the long-only minimum-variance problem in LM29's
  scaling $2\Sigma\mathbf w^*=\lambda\mathbf 1+\boldsymbol\nu$; (29.6), R4's homogenized QP (experiment 4); R3 and R4 in
  their through-case form; R3 never binds on E5 (A29-09, the single owner by decision A5); cvxpy and the
  solver-output rule (multipliers as dual values).

**Leads:** `[31, 32, 33, 34, 35, 45]`: LM31 (R1's, R3's and R5's realized volatility and minimum variance on U28's
halves, cited beside R6–R8), LM32 (R5's VaR, ES and drawdowns), LM33 (R5's Sharpe ratio and the volatilities LM30
owns; R3 and R5 as near-duplicate trials when it counts effective trials), LM34 (R5's net results), LM35 ((30.4) for
the checkpoint's "how constraints change the allocation"; R5's scenario losses), LM45 (the forward pointer of §6).

**Forward links honoured.**

| Earlier text | Promise | Kept in |
|:--|:--|:--|
| lm07.md:509 | "[[LM30]] (estimation error and shrinkage) … take up the repair" after Chopra and Ziemba (1993) | §2 (Chopra and Ziemba cited as LM7 does; experiment 1 measures the share of the loss due to means on E5's model), §4, §5 |
| lm10.md:55 | "[[LM30]] treats estimation error" | §2 ($\hat\Sigma$'s error by (18.4)), §4 |
| lm10.md:386 | repairing a non-PSD correlation matrix, "for example with the nearest valid one (Rousseeuw and Molenberghs 1993; Higham 2002b)" | §7, E9: three repairs of LM10's $C_{\text{pw}}$ (shrinkage toward $I$, clipping, the nearest correlation matrix); the lab's code |
| lm11.md:480, 486 | pulling small eigenvalues up lowers $\kappa$; "covariance shrinkage, the subject of [[LM30]], does this" | §4, (30.1): eigenvalues $c\lambda_k+(1-c)\bar\lambda$, $\kappa$ 126.05 → 121.38 on the halves [A30-18], 438 → 68.1 on 60 returns [A30-20]; X4; widget |
| lm16.md:225 | "how far $\hat\Sigma$ lies from $\Sigma$ is [[LM30]]'s" | §2 (relative error 8.5% at $T=504$ by (18.4) [A30-06]), §4 (the noise $\sigma^2_{\hat\Sigma}$ in (30.2), its estimate in (30.3)) |
| lm22.md:390 | "Resampled portfolios are [[LM30]]'s" | §7, experiment 4 (one paragraph: Michaud's resampled efficiency as Michaud and Michaud (2008) describe it, experiment 4 a variant), lab part 8 (the bootstrap) |
| lm23.md:416 | factor risk is [[LM30]]'s "estimation problem" | §7: the single-index matrix (Sharpe 1963), (27.8)'s diagonal-residual form with (23.1)'s betas, 57 parameters against 406 [A30-29], judged on U28's second half (X8) |
| lm24.md:44 | "Shrinking a covariance matrix, the subject of [[LM30]], follows the same idea" | §4: (30.2) has (24.3)'s shape; §6: Black–Litterman's weight on a data view is (24.3)'s $c$ |
| lm24.md:291 | Jorion (1986) "carried an empirical-Bayes estimate of means into portfolio choice ([[LM30]])" | §6, one sentence, the abstract's claim only (SOURCES: the target is unconfirmed) |
| lm26.md:409 | "Forecasting a whole covariance matrix is [[LM30]]'s and [[LM31]]'s subject" | §4 (X5), §5 (E7) and §7 (X8): sample, shrunk, constrained and single-index matrices as forecasts of the second half, judged by the realized volatility of their minimum-variance portfolios; the EWMA matrix $\Sigma_{t+1\mid t}$ is LM31's (one sentence, pointer) |
| `build/make_lab07.py:601` | "LM30 returns to this question with shrinkage estimators" (monthly re-estimation on 6/12/24/36-month windows) | lab extension: the same windows with the shrunk $2\times2$ matrix, estimated on E5's estimation frame and held on its wealth frame |

The grep of `src/*.md` and `src/pages/*.md` for `[[LM30]]` finds exactly lm07:509, lm10:55, lm10:386, lm11:480,
lm11:486, lm16:225, lm22:390, lm23:416, lm24:44, lm24:291, lm26:409; plain "LM30" in `build/make_lab*.py` finds only
make_lab07.py:601. The spine missed none. ROADMAP's rows also hand LM30 "the repair of a correlation matrix that is not
PSD" (Covariance), "the estimation of factor risk" (Factors), "resampled portfolios" (Resampling) and "covariance
shrinkage and Black–Litterman weights" (Shrinkage); the syllabus line is "The 1/N puzzle, Ledoit–Wolf shrinkage,
Black–Litterman, resampling". Each is kept above. LM27's brief hands LM30 "the error in $\hat\Sigma$ and in the risk
shares" and "factor-model covariances as estimators": §2 measures the error of R1's risk shares in experiment 1
[A30-42], and §7 judges the single-index matrix out of sample.

**Outcomes** ("After this module you should be able to:"; level in brackets, AUTHORING §3 form on the page):

1. [C] simulate plug-in portfolios from a known model and measure the loss due to estimated means
2. [U] explain why equal weights are hard to beat, and state the conditions of the 1/N evidence
3. [D] derive the oracle shrinkage weight as a bias–variance trade-off
4. [C] compute Ledoit–Wolf shrinkage by hand and with scikit-learn, and diagnose its effect on eigenvalues and weights
5. [D] derive the long-only minimum-variance portfolio as an unconstrained one on an adjusted covariance matrix
6. [D] derive the Black–Litterman posterior for one view and compute the weights it implies
7. [U] choose a repair (shrinkage, constraints, a reference portfolio, a factor model or resampling) for a given ratio of observations to assets
8. [C] compare out-of-sample volatilities of sample, shrunk and constrained portfolios, labelling each result

Taught, practised, assessed (REVIEW_PROMPT item 10): 1 §2, E1–E2, KC §2, P1, P11; 2 §3, E3, KC §3, P1 (a mean's
error falls only with years), P11 (how often 1/N wins; the conditions); 3 §4 (derived), Deep Dive, P3 (the oracle when the target is
the truth), P7; 4 §4, §8, E4–E6, KC §4, KC §8, P2, P5 (the inverse's entry through the VIF and the small eigenvalue),
P10; 5 §5 (derived), E7, KC §5, P6, P8; 6 §6 (derived), E8, KC §6, P4, P9; 7 §7 and the Summary's table, E5, E9, KC
§7, P12 (which repair each ratio of observations to assets favours); 8 §3–§5, §7, X5, X8, E5–E7, P12.

**Owns.** Which layer LM30 adds: LM28 and LM29 solved for weights as if $\boldsymbol\mu$ and $\Sigma$ were known; LM30
measures the error in the inputs and tests repairs. The error in plug-in weights by simulation from a known model
(the first window's estimates), split into the part from $\hat{\boldsymbol\mu}$ and the part from $\hat\Sigma$, in the
exposure form, and the error of R1's risk shares in the same draws (LM27's hand-over); why the error of a mean
depends on years ((20.2)) while $\hat\Sigma$'s falls with the number of days ((18.4)); the optimism of an in-sample
minimum variance ((28.3)); the 1/N benchmark and DeMiguel, Garlappi and Uppal (2009) as their article states it (the
certainty-equivalent criterion of their §4, the US calibration, the conditions for optimizing to win), and what decides the
window an optimizer needs (experiment 2); covariance shrinkage toward
$\bar\lambda I$ (30.1), with its eigenvalues, $\kappa_c$ and the 1/N end at $c=0$; the oracle weight (30.2) derived as
(20.1)'s bias–variance split in the Frobenius norm and read as (24.3)'s weight; Ledoit and Wolf's (2004) estimate
(30.3) and its consistency *stated without proof*; by hand and by scikit-learn; the ratio of observations to assets
(U28's windows, experiment 3); the shrinkage path of the through case (R5 against R3); constraints as implicit
shrinkage (30.4), derived from LM29's KKT conditions, with Jagannathan and Ma's (2003) Proposition 1 for its positive
semidefiniteness; Black–Litterman with R2 as the reference (reverse optimization, one view on excess returns, the
posterior (30.5) from (16.8), its weights along the view portfolio); Jorion's Bayes–Stein means in one sentence;
resampled weights as a variant of Michaud's (1998) resampled efficiency, as Michaud and Michaud (2008) describe it
(one paragraph); the single-index matrix as the estimation of factor risk; the repair of a correlation matrix that is
not PSD (one paragraph). Values owned: every A30 anchor except the echoes, which belong to `vol5_series.py`,
`vol5_rules.py`, LM27, LM28, LM29 and LM11, and which the text cites by their owners' IDs: A30-01, A30-02; A30-03's
dates, calendar span and $\tau$ (A28-02); A30-04 (A28-05 to A28-07); in A30-05 $\mathbf w^{\mathrm{tan}}$, $\mathrm{SR}^*$,
$\delta$, $\mathbf w^{\mathrm{mv}}$, $\sigma_{\min}$ and equal weights' mean and volatility (A28-18, A28-22, A28-10,
A28-15); the SEs of A30-06 and A30-39 (A28-27); A30-12's range of R3's predicted volatility (A28-12) and R1's full-sample fixed-weight volatility (A27-13); A30-16's count
of R3's zero weights (A29-09); A30-17; $\kappa=126.05$ in A30-18 (LM11); the gross exposure at $T=2{,}191$ in A30-19
and A30-20 (A28-14); the true shares in A30-42 (A27-21). A28-02 computes $\tau=T/A$ without printing it; only in E2
does LM30 print it, to four decimals, and A28-06's volatilities to two, beside (20.2)'s computation of A28-27's SEs
(decision C12's exception). That computation needs the volatilities' second decimal and three decimals of $\tau$
(2.07 gives 8.3 for 00646, not 8.2); the fourth keeps $\tau$ off a rounding boundary (2.0744888 is flagged at 3 dp).
A28-02's and A28-06's rows record these prints (decisions on the third revision). The model's
$\mathrm{SR}(1/N)=0.327$ [A30-05] is LM30's, computed from A28-15's mean and volatility, which LM28 prints without the ratio,
and so is its ratio to $\mathrm{SR}^*$ (A30-43). By decision A5
LM30 owns the U28 halves' statistics: 1/N and minimum variance (sample, shrunk, long-only and single index, A30-19)
and the first half's long-only portfolio, its binding set and multipliers (A30-22, A30-23); LM29 and LM31 cite them.
By decision A4 LM30 owns R2's first-window mean excess return and volatility (A30-24), and LM31 echoes the volatility
(A31-16).

**Leaves.** Shrinkage of means beyond LM24's (24.3)–(24.4) and Jorion's sentence → LM24, cited. Forecasting a
covariance matrix day by day (the EWMA matrix $\Sigma_{t+1\mid t}$ with (26.2)'s recursion) → LM31; multivariate
GARCH → out of scope. Whether R5's realized volatility, Sharpe ratio or any out-of-sample difference is significant,
and every standard error of the rules' statistics → LM33 (decision A3; LM30 tests nothing). Net wealth, growth,
turnover and costs of every rule, R5 included → LM34. R5's tails and drawdowns → LM32; scenario losses → LM35. Kelly
sizing under parameter uncertainty → LM45. Not in the book (one sentence each): nonlinear shrinkage of eigenvalues, the
constant-correlation target (Ledoit and Wolf 2004, JPM) beyond a sentence, shrinkage toward the single-index matrix
(Ledoit and Wolf 2003) beyond a sentence, the full resampled-efficiency frontier (Michaud and Michaud 2008 average
matched portfolios along it; experiment 4 averages one kind). To the lab and problems (density, the
spine's list): the repair of $C_{\text{pw}}$ in code (clipping and Higham's alternating projections), the bootstrap of
resampled weights, the make_lab07 exercise, R5 re-implemented and checked, and the Deep Dive's depth of the
Ledoit–Wolf argument (problems 7 and 10).

**Uses before taught** (one sentence each in the text):

- §2: "A Sharpe ratio estimated from returns is itself noisy ((20.9)); [[LM33]] tests the rules' Sharpe ratios, while
  here the model knows the true one."
- §3: "Costs, turnover and net growth of the rules are [[LM34]]'s numbers, and the standard errors of their statistics
  [[LM33]]'s; this module reports only volatility."
- §4: "Forecasting the matrix day by day, with the recursion (26.2) applied to $\mathbf R_t\mathbf R_t^{\top}$, is
  [[LM31]]'s method."
- §6: "Sizing a position when the means are uncertain is [[LM45]]'s subject."
- §7: "Picking the best of several estimators judged on the same split is a search, which [[LM34]] corrects."

**Data role.**

- **E5** (shared decision "Data"): `vol5_series.frames("E5")`. Estimation frame $T=2{,}362$ returns, 2017-01-18 →
  2026-10-08, $A=242.95$; wealth frame 2,368 sessions, $A_{\mathrm w}=243.57$ [A30-01]. The through case's schedule:
  92 signals, 2019-02-27 (trade 2019-03-04) to 2026-09-30 (trade 2026-10-01), windows of 504 estimation rows [A30-02].
  **The first window** (LM28's): 504 returns on the joint dates of the estimation frame, 2017-02-13 → 2019-02-27, a
  calendar span of 2.05 years from the close of 2017-02-10 [A28-02]; $\tau=T/A$, a count of 504 sessions over E5's
  $A$, which A28-02 computes and E2 prints beside (20.2)'s computation (LM30's A30-03 recomputes both). Its annual means 7.5, 10.0, 2.6, 0.8, −1.4% [A28-05] and volatilities 13.5, 11.9, 8.5, 9.4,
  23.2% [A28-06] (0050, 00646, 00679B, 00635U, 00642U), correlations from −0.30 to 0.54 [A28-07]: LM28 prints them
  (LM30's A30-04 recomputes them), and E2 prints the volatilities to two decimals beside (20.2)'s computation (13.50,
  11.87, 8.54, 9.39, 23.17%; decision C12); LM30 takes them as the model of experiments 1 and 2, and experiment 4 resamples the window's own rows. A fund's kurtosis or
  volatility inside a window is computed on that window's joint dates, because each enters a joint computation (Ledoit
  and Wolf's noise, the shrinkage target; decision C2).
- **U28** (Volume II): `lm10_series.u28()`. $T=4{,}382$ price returns 2008-12-02 → 2026-10-08, $A=245.4794$; LM11's
  halves 2008-12-02 → 2017-10-06 and 2017-10-11 → 2026-10-08, 2,191 each [A30-17]. The window lengths of
  [[ex:windows]] are the last $T$ returns of the first half, all ending 2017-10-06 [A30-20]. Price indices, no
  dividends: every caption says so; no U28 mean is used (minimum variance only). The TAIEX price index is the single
  index of §7 (same dates), named so beside every TAIEX figure.
- **LM10's $C_{\text{pw}}$** (constructed by LM10 from three years' pairwise correlations): its printed entries only
  (lm10.md:365, 376–378) [A30-28].
- **The rules.** `vol5_rules.signals`, `wealth_path` and `summary` give R1, R3 and R5's paths and targets
  [A30-12, A30-16]; R5's intensities are recomputed with scikit-learn on the same windows [A30-14] and its realized
  volatility is checked against `data/processed/vol5_rules.parquet` [A30-12]. A rule's realized volatility is named by
  its span: out of sample, net of costs, on the 1,851 daily returns from 2019-03-05 to 2026-10-08 (R1's 12.48%, not
  LM27's full-sample fixed-weight 11.49%, A27-13; decision C7).
- **Conventions.** Divisor $T$ everywhere (`cov0`, scikit-learn's empirical covariance; `ddof=0` passed in every
  NumPy call); annual inputs are $A$ times the daily ones with the sample's own $A$; excess returns over $r_f=1.5\%$
  ($r_f/A$ a day), as the through case. Years: $\tau=T/A$ with E5's $A$, LM20's form of (20.2), for the first window and
  for every simulated length, a count of sessions over $A$ that the text names as such; a dated span's calendar years
  run from the close before its first return to its last close, in days ÷ 365.25 (AUTHORING §8, decision C7). Volatility is
  $\sqrt{A\,\mathbf w^{\top}\Sigma\mathbf w}$ ((27.4)): "predicted" with the estimation sample's matrix, "realized"
  with U28's second half, "true" with a simulation's model; a rule's realized volatility is `summary()`'s (daily net
  returns from the session after the first trade, $\sqrt{A_{\mathrm w}}$). Each optimization states its feasible set,
  its convexity and whether its solution exists and is unique (shared decision "Rigor"). Unconstrained minimum variance
  by `np.linalg.solve` ($\hat\Sigma$ PD); long-only by `vol5_rules.minvar` (exact NNLS with its KKT check) and once by
  cvxpy (CLARABEL at the shared tolerances, 1e-12 for this QP, annual inputs, status `optimal`, multipliers checked to
  3.7e-10 [A30-23]); the nearest correlation matrix by Higham's projections and once by cvxpy (CLARABEL at the cone
  tolerance 1e-10) [A30-28]. A weight below $10^{-6}$ is 0. Medians use `inverted_cdf`; counts against a threshold use
  the guard $10^{-12}$ and print their smallest margin.
- **Seeds.** Five experiments (the fifth in the lab only), each with its generator created once (AUTHORING §8): $e=1$ `default_rng([1, 20261011])`,
  10,000 samples of 504 days from $\mathcal N_5$ with the first window's mean and matrix, one
  `standard_normal((504, 5))` call per sample [A30-07]; $e=2$ `default_rng([2, 20261011])`, 2,000 samples at each of
  seven lengths from 126 to 8,064 days, in that order [A30-11]; $e=3$ `default_rng([3, 20261011])`, U28's first-half
  matrix as the truth (mean 0), 1,000 samples at each of seven lengths from 20 to 2,191 days [A30-21]; $e=4$
  `default_rng([4, 20261011])`, 1,000 iid bootstrap resamples of the first window's rows [A30-27]; the lab's stationary-bootstrap variant has its
  own, $e=5$ `default_rng([5, 20261011])`, 1,000 resamples. Every printed Monte
  Carlo result carries its standard error, printed to one significant digit, and the result's last printed digit sits
  at that digit (decision on the second recomputation; so experiment 4's mean weights print one decimal, 3.8% to 35.2%,
  and experiment 1's covariances-only mean five, 0.87686 with SE 0.00002). A mean's SE is its SD (divisor $n$) over
  $\sqrt n$, a paired difference's the same on the per-sample differences, a proportion's $\sqrt{p(1-p)/n}$; a median,
  an SD or a ratio of SDs of experiment 1 gets a batch SE (20 consecutive batches of 500 samples). Several SEs print
  as their rounded range ("SEs 0.008 to 0.001") or their common rounded value ("SEs 0.003"). An exact tie at the
  printed digit prints the coarser safe form, as Volume IV (A30-09's 21.15% prints 21%, beside the exact count 2,115
  of 10,000; "Decisions on the fresh check of the whole of Stage 1").
- **Published files.** X2 stores 2 × 1,000 simulated points (no dates); X6 the 92 intensities by signal date; the
  widget's block holds per-window eigenvalues and eigenvectors of U28 and the second half's matrix (derived statistics,
  about 45 KB). No file carries a daily series in date order, or anything from which one can be rebuilt (X37, shared
  decision "Charts").
- **Scripts.** `data/lm30_numbers.py` (every printed value, asserted against `src/lm30.md` and compared with these
  anchors; rounding flags) and `data/lm30_charts.py` (X2–X4, X6, X7, the widget block), after `data/vol5_series.py`,
  `data/vol5_rules.py`, `data/vol2_series.py` and `data/lm10_series.py`.

**Hygiene declaration.** *Model:* experiments 1–3 and every "true" value (their truth is the first window's estimates
or U28's first-half matrix). *In-sample:* the first window's tangency and minimum-variance portfolios (LM28's), every
intensity, eigenvalue and condition number, the long-only decomposition (30.4), R2's implied returns and every
Black–Litterman portfolio, experiment 4's resampled weights (iid bootstraps of the first window's own rows), the
single-index fit, the "best $c$ in hindsight" (chosen on the second half itself).
*Out-of-sample:* the through case's R1, R3 and R5 from March 2019 (fixed in advance on 2026-10-24; three of the eight
rules, $n=8$ belongs to LM33); U28's estimators fitted on the first half and judged on the second, one split that LM11
fixed. On that split the module compares five estimators (sample, shrunk, long-only, single index, 1/N) and seven
window lengths for two of them; the window grid was chosen by this brief after the halves' result was computed, so it
illustrates the ratio of observations to assets and is no evidence (decision D). *Constructed:* R2 (LM27's reference
mix) and LM10's $C_{\text{pw}}$. Local note, two paragraphs (62 and 26 words): "The simulations of experiments 1 to 3 are *Model*: they draw
from a fixed model built on real estimates. Weights, intensities, resampled weights and Black–Litterman portfolios
fitted to one window are *In-sample*. Two comparisons are *Out-of-sample*: the through case's R1, R3 and R5 from March
2019, fixed in advance, and U28's estimators fitted on its first half and judged on the second." / "That split
compares five estimators, and seven window lengths for two of them on a grid chosen after the halves' result; none is
called the best."

Said once in §1, after the hygiene note (shared decision "Estimate, standard error, interval"): "The weights fitted
to one window in E6–E8 and X7 are plug-in estimates with an unmeasured error; experiments 1, 3 and 4 measure such
errors by simulation and resampling." (29 words)

**Notation.** AUTHORING §6 with its Volume V rows. Used: $R$, $T$, $t$, $A$, $A_{\mathrm w}$, $N$, $i$, $j$, $k$ (an
eigenvalue's index), $\tau$ (years, $T/A$), $n$ (simulated samples), $B$ (bootstrap resamples, lab), $\mathbf R_t$,
$\bar{\mathbf R}$, $X$, $\tilde X$, $\boldsymbol\mu$, $\Sigma$, $\hat\Sigma$, $C$, $\mathbf s$, $\rho$, $\sigma$,
$\sigma_p$, $\lambda_k$, $\mathbf q_k$, $Q$, $\Lambda$, $\kappa$, $\operatorname{tr}$, $\mathbf w$, $\mathbf f$,
$\mathbf e$, $r_f$, $\mathrm{SR}$, $\mathrm{SR}^*$, $\mathbf w^{\mathrm{mv}}$, $\sigma^2_{\min}$, $\mathbf w^{\mathrm{tan}}$,
$\delta$, $c$, $\hat\Sigma_{\mathrm{tgt}}$, $\hat\Sigma_c$, $n_0$, $\mathbf w_{\mathrm{ref}}$, $\mathbf e_{\mathrm{eq}}$,
$K$, $\Xi$, $\nu$, $\E$, $\Var$, $\operatorname{Kurt}$, $\mathcal N_N$, $\operatorname{MSE}$, $\operatorname{SE}$,
$\operatorname{VIF}$ ((23.9)), $\lVert\mathbf x\rVert_1$ (gross exposure), $\hat\Sigma^{(1)}$, $\hat\Sigma^{(2)}$ (LM11's
halves), $C_{\text{pw}}$ (LM10's). Local symbols, declared in the notation note (accepted by decision B5):

| Symbol | Meaning | Check |
|:--|:--|:--|
| $\hat{\mathbf e}$ | the window's sample excess means: $\bar{\mathbf R}-(r_f/A)\mathbf 1$ a day, or $A\bar{\mathbf R}-r_f\mathbf 1$ a year | a hat for an estimate of LM7's $\mathbf e$ |
| $\hat{\mathbf f}$ | plug-in exposures $\hat\Sigma^{-1}\hat{\mathbf e}/\delta$ at the section's $\delta$: in §2–§3 the model's $\delta=\mathbf 1^{\top}\Sigma^{-1}\mathbf e=11.27$ [A28-22], so that the truth's optimum is $\mathbf w^{\mathrm{tan}}$; in §6 R2's $\delta=9.74$ [A30-24], the one $\mathbf f_{\mathrm{BL}}$ uses | the vector form of LM20's scalar $\hat f$ (one asset at $\delta=1$; decision B4); LM30 has no Kelly fraction and writes no $\mathbf f^*$ |
| $\mathrm{SR}(\mathbf f)$ | the model's annualized Sharpe ratio of exposures $\mathbf f$, $\sqrt A\,\mathbf f^{\top}\mathbf e/\sqrt{\mathbf f^{\top}\Sigma\mathbf f}$ with the model's daily $\mathbf e$ and $\Sigma$ (on LM28's annual inputs the same ratio has no $\sqrt A$) | SR as a function, declared with its units |
| $\bar\lambda$; $\Sigma_{\mathrm{tgt}}$ | $\operatorname{tr}\hat\Sigma/N$, so $\hat\Sigma_{\mathrm{tgt}}=\bar\lambda I$; the model's target $(\operatorname{tr}\Sigma/N)I$ in (30.2) | §6 (LM30 scope); the unhatted target belongs to the model |
| $\hat c$, $c^*$, $\kappa_c$ | Ledoit and Wolf's estimate of $c$; the oracle (an optimum, so a star); the condition number of $\hat\Sigma_c$ | §6's $c$ row; scikit-learn's `shrinkage_` is $1-\hat c$, said once |
| $\lVert M\rVert_F$ | the Frobenius norm (LM18) | as LM18, unscaled (Ledoit and Wolf's $1/N$ cancels) |
| $\sigma^2_{\hat\Sigma}$, $\hat\sigma^2_{\hat\Sigma}$ | the noise $\E\lVert\hat\Sigma-\Sigma\rVert_F^2$; its estimate in (30.3) | subscripted $\sigma^2$; the papers' $\alpha$, $\beta$, $\delta$, $d$, $b$ are all taken in the book, so none is used |
| $\nu_0$, $\boldsymbol\nu$ | multipliers of $\mathbf 1^{\top}\mathbf w=1$ and of $\mathbf w\ge\mathbf 0$, scaled as Jagannathan and Ma's, $\hat\Sigma\mathbf w=\nu_0\mathbf 1+\boldsymbol\nu$ | half of LM29's (29.5), said once in §5 in words: $\nu_0=\sigma_p^2$ is half of (29.5)'s equality multiplier, and each $\nu_i$ half of LM29's (no bare $\lambda$ is printed; decision B4); LM30 writes its multipliers $\nu$ (§6) |
| $\hat\Sigma_\nu$ | the adjusted covariance matrix $\hat\Sigma-(\boldsymbol\nu\mathbf 1^{\top}+\mathbf 1\boldsymbol\nu^{\top})$, (30.4) (Jagannathan and Ma's adjusted matrix; $\hat\Sigma_c$ alone is the shrunk matrix) | a tilde means centred (§6), so Jagannathan and Ma's $\tilde S$ is not used |
| $\mathbf w^{\mathrm{lo}}$ | long-only minimum-variance weights (R3's form) | local (decision B5) |
| $b$, $\varepsilon$ | the one view's value and its error, $K\mathbf e=b+\varepsilon$, $\Var\varepsilon=\Xi$ ($1\times1$) | §6's $K\mathbf e=\mathbf b+\boldsymbol\varepsilon$ with one view, so scalars; the several-view statement and KC §6 use §6's vector form, $\Xi$ one row and column per view (KC §6: $K=I$, $\Xi=\hat\Sigma/T$); LM30 has no bets |
| $\mathbf e_{\mathrm{BL}}$, $\mathbf f_{\mathrm{BL}}$ | posterior mean of $\mathbf e$; exposures $\hat\Sigma^{-1}\mathbf e_{\mathrm{BL}}/\delta$ | new, subscripted |
| $\hat\Sigma_{\mathrm F}$, $\hat\beta_i$, $\sigma_{\mathrm{mkt}}^2$, $\hat\sigma^2_{\mathrm{res},i}$ | single-index matrix $\sigma_{\mathrm{mkt}}^2\hat{\boldsymbol\beta}\hat{\boldsymbol\beta}^{\top}+\operatorname{diag}(\hat\sigma^2_{\mathrm{res},1},\dots,\hat\sigma^2_{\mathrm{res},N})$, (27.8) with diagonal residuals; (23.1)'s market betas; the TAIEX price index's variance (divisor $T$); residual variances, the diagonal of LM27's $\Sigma_{\mathrm{res}}$ | $\sigma^2_{\mathrm{mkt}}$ as LM27 writes it (decision B6); the "res" subscript as LM27's, since $\varepsilon$ is the view's error (decision on notation, Y8); divisor $T$, so not LM23's $s_\varepsilon$ ($T-d$); no $D$ (a dividend) for the diagonal |

Not used: $\alpha$ (any meaning; a shrinkage intensity is never $\alpha$), $\nu$ for degrees of freedom (written in words; $\nu$ are multipliers), $\lambda$ as a multiplier, $\lambda$ for risk
aversion, a Cholesky $L$ in the main text (the simulations colour normals "with $\Sigma$'s Cholesky factor, [[LM12]]"
in words), $\tilde S$, $P$, $Q$ (a matrix of views; $Q$ is the eigenvector matrix), $\Omega$, $\pi$, $\tau$ for
Black–Litterman (the literature's scalar is written $1/n_0$ and named in words once, since $\tau$ is LM30's span in
years), $d^2$ (no Mahalanobis distance), $D$ for a diagonal matrix, $\mathbf e_i$, a hat on an EWMA forecast,
$\varepsilon$ for a regression residual, a split ratio as a symbol (decision B6; LM30 restates no split).

**Motivating case: "Five funds, two years, and positions nobody should hold"** (box, three paragraphs, about 160 words)

> On 27 February 2019 the through case reads its first window: 504 daily returns of five funds [A28-02]. Fed the
> window's means and covariances, the tangency formula of [[LM28]] puts 62.6% in 00646 and shorts 14.7% of 00642U [A28-18].
> Its in-sample Sharpe ratio is 0.88 [A28-18], against 0.33 for equal weights [A30-05].
>
> Now suppose those estimates were the truth, and draw another 504 days from them, 10,000 times. Re-estimated on the
> new days, the position in 00646 has a standard deviation of 67.1 points [A30-08]. The portfolio's true Sharpe ratio
> averages 0.423 [A30-07]. If only the covariances had to be estimated, it would average 0.87686, close to the
> possible 0.880. The simulation's standard errors are 0.5 points, 0.003 and 0.00002 [A30-07, A30-08].
>
> Out of sample the through case agrees. From March 2019 to October 2026, minimum variance, which uses no means,
> realized 9.96% volatility net of costs, against 12.48% for equal weights [A30-12]. Shrinking its covariance matrix
> changed that by 0.01 points [A30-12]. Which errors matter, and which repairs work?

(`build/qa/style.py --strict` on the box alone as a `[!case]` callout, 2026-10-24: 160 words without the anchor
tags (170 with them), 12 sentences, average 13.3 (14.2), no FAIL and no sentence of 25 words or more; the three
paragraphs have 48, 66 and 46 words (decision C10). The outcomes as sentences: 116 words, 8 sentences, average 14.5, none over 30.)
Resolved: (a) the means: §2, X2, E1–E2 (almost all of the loss; a mean's
error shrinks only with years); (b) why shrinkage changed nothing: §4, X5, E5–E6 (504 days for five funds is a high
ratio of observations to assets; at 30 returns for 28 sectors shrinkage cuts the realized volatility from 43.1% to
12.5% [A30-20]); (c) the repairs: §5–§7, X8 and the Summary's table.

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | the layer LM30 adds (LM28–LM29 treat inputs as known); case + X1; roadmap; notation and hygiene notes | 400 |
| 2 | How Far Plug-in Weights Fall from the Truth {1} | the model (first window as truth, normal iid, $T=504$, experiment 1); Chopra and Ziemba (1993) as [[LM7]] cites them (errors in means far more damaging than errors in covariances, lm07.md:509), which experiment 1 measures on E5's model; three plug-ins (both, means only, covariances only); why exposures, not weights summing to 1 (2,115 of 10,000 samples have $\mathbf 1^{\top}\hat{\mathbf f}\le0$, 21%, SE 0.4 points); X2; E1, with the error of R1's risk shares (LM27's hand-over); (20.2) against (18.4): E2; the in-sample minimum variance's optimism by (28.3) (4.990% predicted and 5.0353% true, SEs 0.002 and 0.0001, against the possible 5.02% [A30-10, A28-10]); pitfall: a fixed model measures sampling error alone (its truth is an in-sample estimate, its returns iid normal and its means fixed, while real means move, LM24's halves); 導讀; KC | 720 |
| 3 | Equal Weights as a Benchmark {2} | DeMiguel, Garlappi and Uppal (2009), read in the published article: 14 models, seven datasets, compared by Sharpe ratio, certainty-equivalent return and turnover (abstract); the window calculation of their §4 judges the sample-based rule by its certainty-equivalent return; in the calibration of their Figure 1, panel E (US stocks), 1/N's monthly Sharpe ratio is 0.12 against the tangency's 0.15, and the sample-based rule needs more than 3,000 months with 25 assets (§4, pp. 1939–1941); their conditions for optimizing to win (a long window, a best Sharpe ratio well above 1/N's, few assets; p. 1919); experiment 2, X3, E3: against 1/N's 0.327 the plug-in's mean true Sharpe ratio is about equal at 1.04 years of sessions (0.322, SE 0.008) and well above at 2.07 (0.422, SE 0.007) [A30-11]; why this model's answer is short (1/N reaches 0.37 of the best here against their 0.8 [A30-43], and the model's means do not move); Kan and Zhou (2007) in one sentence; the through case out of sample: R1 12.48%, R3 9.96% [A30-12]; 1/N is the $c=0$ end of (30.1) (pointer to §4); pointers to LM33, LM34; KC | 470 |
| 4 | Shrinking the Covariance Matrix {3,4,8} | definition (30.1); eigenvectors kept, eigenvalues $c\lambda_k+(1-c)\bar\lambda$ by (11.3), $\kappa_c$, the 1/N end; the oracle theorem (30.2) with its conditions, derived; its (24.3) reading; (18.4) for normal returns; Ledoit and Wolf's (30.3) with consistency stated, and what "large" means there ($N/T$ bounded as both grow; here $N/T$ runs from 5/504 to 28/20, and experiment 3's mean $\hat c$ from 0.810 (SE 0.002) at 20 returns to 0.997963 (SE 0.000002) at 2,191 [A30-21]); E4 (by hand, scikit-learn, the normal oracle, where the excess noise comes from); X4; X5 and E5 (window lengths; at $T=20$ the sample problem has no unique minimum and the pseudoinverse gives the minimum within the column space); experiment 3 in two sentences; X6 and E6 (R5 against R3; the target's scale); widget; Deep Dive; pitfall: the moment conditions and fat tails; 導讀; KC | 1,000 |
| 5 | Constraints as Implicit Shrinkage {5} | LM29's KKT conditions for $\mathbf w\ge\mathbf 0$ and the multiplier scale against (29.5), said once; the feasible set ($\mathbf w\ge\mathbf 0$, $\mathbf 1^{\top}\mathbf w=1$) is closed and bounded, so a minimizer exists, and with $\hat\Sigma$ PD the objective is strictly convex, so it is unique ((29.3)); (30.4) derived; positive semidefiniteness stated (Jagannathan and Ma 2003, Proposition 1); the reading by (27.5) (excluded assets' covariances lowered by $\nu_i+\nu_j$, variances by $2\nu_i$); E7 on U28's first half; out of sample the constraint raises the realized volatility from 11.78% to 12.14% at 2,191 returns [A30-19], and in experiment 3 it helps at 30 or 60 returns and costs from 120 on (paired differences); E5's through case: R3 never hits a zero weight (0 of 92 signals, LM29's A29-09); 導讀; KC | 460 |
| 6 | Starting from a Reference Portfolio: Black–Litterman {6} | reverse optimization $\mathbf e_{\mathrm{eq}}=\delta\hat\Sigma\mathbf w_{\mathrm{ref}}$ with R2 (constructed) and $\delta$ calibrated to R2's window mean (decision D); the prior worth $n_0$ observations (the literature's scalar $1/n_0$, no consensus value); one view on excess returns, $K=(-1,1,0,0,0)$, $\Xi=K\hat\Sigma K^{\top}/T$; (30.5) derived from (16.8); a data view gives $c=T/(T+n_0)$, (24.3); weights move along $K^{\top}$ only (He and Litterman's statement); several views stated; X7; E8; Jorion one sentence; pitfall: the reference carries the prior; 導讀; KC | 680 |
| 7 | Resampling, Factor Structure and Repair {7,8} | resampled weights, one paragraph: error maximization at the level of Michaud's (1989) abstract; resampled efficiency, which Michaud (1998) proposed, as Michaud and Michaud (2008) describe it, paraphrased (draw means and covariances around the estimates, compute the frontier for each draw, average the weights of matched portfolios); experiment 4 is a variant that averages R4's long-only rule over 1,000 bootstrap resamples (the maximum-Sharpe portfolio (29.6) where some fund's mean exceeds $r_f$, R3's minimum variance in the 12 where none does): it holds every fund (3.8% to 35.2%, SEs 0.4 and 0.9 points), though each fund is excluded in 18% to 72% of the resamples (SEs 1 to 2 points) [A30-27]; the single-index matrix ((27.8) with diagonal residuals), 57 against 406 parameters [A30-29], realized 12.67% against 11.78% [A30-19] (a wrong structure costs); X8, the five estimators on U28's halves; the repair of $C_{\text{pw}}$, E9; choosing a repair by $T/N$ (the Summary's table previewed); 導讀; KC | 480 |
| 8 | Estimation-Robust Portfolios in Python {4} | `LedoitWolf(assume_centered=False)`: divisor $T$, target $\bar\lambda I$ only, `shrinkage_` $=1-\hat c$, scale-free; `OAS` (Chen et al. 2010) differs and drops a $2/p$ factor; cvxpy's long-only problem with annual inputs, tolerances, status and dual values as $\boldsymbol\nu$; lab box | 200 |
| — | Summary (7) / Problems (12) / Solutions | the Summary ends with a table: repair, what it fixes, when it helps ($T/N$), its cost | 140 / 400 / 520 |
| | **Total** | | **5,470** |

**Elements.** 9 examples (E1, E2 §2; E3 §3; E4, E5, E6 §4; E7 §5; E8 §6; E9 §7). Knowledge checks:

- §2: twice as many days over the same span leave the error of 00646's annual mean at 8.2 points; twice the span cuts
  it to 5.8 [A28-27, A30-39], by (20.2).
- §3: 1/N has a true Sharpe ratio of 0.33 against the best 0.88, yet it beats the plug-in in 31.4% of samples (Monte
  Carlo SE 0.5 points) [A30-07]. Why can the worse portfolio win so often?
- §4: a $2\times2$ correlation matrix with $\rho=0.9$ shrunk with $c=0.5$ toward $I$: eigenvalues 1.9 and 0.1 become
  1.45 and 0.55, and $\kappa$ falls from 19 to 2.64 [A30-40]; and show that $c=0$ gives the 1/N portfolio.
- §5: on U28's first half 19 constraints bind [A30-22]: which way did the constraint move those sectors'
  covariances, and why did the second half's volatility still rise from 11.78% to 12.14% [A30-19]?
- §6: all five window means as views with $\Xi=\hat\Sigma/T$ give $\mathbf f_{\mathrm{BL}}=c\hat{\mathbf f}+(1-c)\mathbf w_{\mathrm{ref}}$;
  at $c=0.5$, 0050's exposure is 26.8% (the plug-in's 13.6% at $\delta=9.74$ and R2's 40%) [A30-26, A30-25].
- §7: the largest $c$ that keeps $cC_{\text{pw}}+(1-c)I$ PSD is $1/(1-\lambda_3)=0.861$ [A30-28].
- §8: scikit-learn reports `shrinkage_` 0.0325 for the first window: $\hat c=0.9675$, and annualizing the returns
  leaves it unchanged (the intensity is a ratio of squared norms) [A30-13].

中文導讀 in §2 (估計誤差 (estimation error), 抽樣誤差 (sampling error), 代入原則 (plug-in principle), 超額報酬 (excess
return)), §4 (收縮 (shrinkage), 收縮估計量 (shrinkage estimator), 均方誤差 (mean squared error), 偏誤及變異數之抵換
(bias–variance tradeoff), 特徵值 (eigenvalue), 條件數 (condition number)), §5 (限制條件 (constraint), 非負性條件
(nonnegativity condition), 有效限制 (active constraint, LM7's Glossary), 最小變異數投資組合 (minimum-variance
portfolio)), §6 (事前分布 (prior distribution), 事後分布
(posterior distribution), 參考投資組合 (reference portfolio, the book's own), 隱含超額報酬 (implied excess returns, the
book's own), 觀點 (view, the book's own)), §7 (重抽樣 (resampling), 單一指標模型 (single index model), 相關矩陣
(correlation matrix)). Deep Dive in §4, "Why Ledoit and Wolf's noise estimate works": $\hat\Sigma$ is an average of the
$T$ matrices $(\mathbf R_t-\bar{\mathbf R})(\mathbf R_t-\bar{\mathbf R})^{\top}$, so (as (18.2) for a mean) its noise is
their spread divided by $T$, which $\hat\sigma^2_{\hat\Sigma}$ estimates; the cap $\min(\cdot,\lVert\hat\Sigma-\bar\lambda I\rVert_F^2)$
keeps $\hat c\ge0$; the Pythagorean identity behind (30.2) (Ledoit and Wolf's §2 in the 2001 working paper);
consistency *stated without proof* with its three assumptions.

**Exhibits.**

- X1 `case` (table, §1): E5, first window (504 returns on the joint dates, 2017-02-13 → 2019-02-27) and the through
  case. Rows: the tangency weights 11.8 / 62.6 / 37.8 / 2.6 / −14.7% (rounded separately; they sum to 100.1) and
  $\mathrm{SR}^*=0.880$ [A28-18], 1/N's 0.327 [A30-05]; experiment 1 mean true Sharpe ratios 0.423 (both estimated)
  and 0.425 (means only), SEs 0.003, and 0.87686 (covariances only, SE 0.00002) [A30-07]; SD of the 00646 exposure
  67.1 against 4.73 points (batch SEs 0.5 and 0.03) [A30-08]; through case
  realized volatility, out of sample from 2019-03-05 to 2026-10-08, net of costs: R1 12.48%, R3 9.96%, R5 9.97%
  [A30-12]. Note: the first two blocks are *In-sample* and *Model*; the last *Out-of-sample* (R1's 12.48% is this
  window's, net of costs; fixed equal weights over the whole estimation frame had 11.49% [A27-13], decision C7). Source: FinMind
  `TaiwanStockPrice`, `TaiwanStockDividendResult`, `TaiwanStockSplitPrice` (registered 2026-10-24;
  `data/vol5_series.py`); Computations: `data/lm30_numbers.py`, `data/vol5_rules.py`.
- X2 `scatter` (`scatter`, §2): experiment 1's first 1,000 samples; $x$ the 00646 exposure, $y$ the 00679B exposure
  (in %, `fmt: "n1"`); two named series "means and covariances estimated" and "covariances only (means known)"; a
  marked point "truth (62.6, 37.8)" [A28-18]. Values cited: SDs 67.1 and 80.7 against 4.73 and 4.79 points (batch
  SEs 0.5, 0.6, 0.03 and 0.04) [A30-08]. Note: *Model*; exposures scaled by the model's $\delta$, so the truth's sum
  to 1.
- X3 `years` (`line`, log $x$, §3): experiment 2; $x$ years of sessions ($T/A$ at E5's $A$, a count of sessions,
  0.52 to 33.2), $y$ mean true Sharpe ratio; series "means and covariances estimated" and "covariances only"; dashed
  `hline`s at 0.880 ("best") and 0.327 ("equal weights"). Values cited: 0.322 at 1.04 years of sessions (within one
  SE of 0.327), 0.422 at 2.07, 0.816 at 33.2; covariances only 0.8660 at 0.52 years of sessions (SE 0.0002) [A30-11].
  Note: *Model*; SEs 0.008 to 0.001 for the first series; years of sessions are sessions over $A$.
- X4 `spectrum` (`line`, log $y$, §4): U28; $x$ the index $k=1,\dots,28$; series "sample, last 60 returns of the
  first half", "shrunk (Ledoit–Wolf, c = 0.874)", "sample, whole first half"; annual eigenvalues. Values cited: $\kappa$ 438 →
  68.1 and 126.05 [A30-20, A30-18]. Note: price indices; *In-sample*; shrinkage keeps the eigenvectors.
- X5 `windows` (table, §4; five columns, so that no PDF page shrinks): U28, fitted on the last $T$ returns of the first
  half (to 2017-10-06), judged on the second half. Rows $T$ = 20, 30, 60, 120, 250, 504, 2,191; columns, each at one
  precision: $T$; $\hat c$ (three decimals); $\kappa$ sample → shrunk (whole numbers → one decimal); sample predicted
  / realized volatility (two decimals); shrunk realized volatility (two decimals) [A30-20]. Values cited: $T=30$:
  0.823, 116,097 → 59.9, 1.34 / 43.12% (gross exposure 13.48), shrunk 12.46%; $T=60$: 0.874, 438 → 68.1, 3.96 /
  13.85% against 12.04%; $T=2{,}191$: 0.995, 126 → 121.4, 11.40 / 11.78% against 11.78%; $T=20$: 0.790, singular
  (rank 19, so no sample $\kappa$ or volatility; the note gives the pseudoinverse's 1.78 / 17.03%), shrunk $\kappa_c$
  49.5 and 12.59% [A30-20]; the other rows at the same precisions (A30-20's Printed-as lists every cell). Note: price
  indices, no dividends; *Out-of-sample*, one split per row, the grid chosen after the halves' result (an
  illustration, not evidence).
- X6 `chat` (`line`, date $x$, §4): $\hat c$ at each of the 92 signals (R5's windows); a marked point at 2026-03-31
  (0.781). Values cited: first 0.968, median 0.962, maximum 0.979 (2024-04-30), minimum 0.781, 19 signals below 0.9,
  the first 2020-03-31 [A30-14]. Note: *In-sample* (each intensity is fitted to its own window, as the hygiene
  declaration says); the windows are 504 daily returns of E5 on joint dates.
- X7 `bl` (`bar`, §6): five funds as categories; series "R2 ($c=0$)", "$c=0.5$", "$c=1$", "plug-in" (four colours;
  portfolios as series, shared decision "Charts"). Values cited: $c=0.5$ 22.5 / 37.5 / 30 / 10 / 0%, $c=1$ 4.9 / 55.1 /
  30 / 10 / 0%, plug-in 13.6 / 72.4 / 43.8 / 3.0 / −17.1% [A30-25]. Note: *In-sample*, first window; R2 is
  *constructed*; $\delta=9.74$ [A30-24].
- X8 `halves` (table, §7; three columns): U28, fitted on the first half (2,191 returns), judged on the second. Rows
  sample, shrunk, long-only, single index, 1/N, and "best $c$ in hindsight"; columns estimator, predicted volatility,
  realized volatility. Values cited: 11.40 / 11.78%, 11.41 / 11.78%, 12.74 / 12.14%, 11.01 / 12.67%, 15.98 / 15.51%,
  and $c=0.98$ with 11.78% [A30-19]. Note: price indices, no dividends; *Out-of-sample* (LM11's split, fixed in
  advance), five estimators compared and none called the best; the last row is *In-sample* on the second half.

**Widget `shrinkPath` — "Shrinkage from equal weights to minimum variance."** `Book.controls`: window (select: the last
30, 60 or 250 returns of U28's first half, or the whole half) and $c$ (slider 0 to 1, step 0.01, starting at the
window's $\hat c$; a button resets it there). Chart: the 28 annual eigenvalues on a log $y$ axis, sample (series 1) and
shrunk (series 2). Readouts: $\hat c$, $\kappa_c$, predicted volatility $\sqrt{A\mathbf w^{\top}\hat\Sigma_c\mathbf w}$,
realized volatility on the second half, gross exposure $\lVert\mathbf w\rVert_1$, the largest weight. The weights come
from (11.8) with the shrunk eigenvalues, $\mathbf w\propto\sum_k\mathbf q_k(\mathbf q_k^{\top}\mathbf 1)/(c\lambda_k+(1-c)\bar\lambda)$:
under 30 lines of module code and no optimizer (shared decision "Widgets"), tested against Python as
`data/lm15_charts.py` does (A30-20's realized volatilities at each window's $\hat c$). Data block `chart-lm30-shrinkPath`:
per window the 28 eigenvalues, the $28\times28$ eigenvectors and $\hat c$; the second half's $28\times28$ matrix; about
45 KB. Initial state (PDF): the last 60 returns, $c=\hat c=0.874$: $\kappa_c=68.1$, realized 12.04% [A30-20]. At $c=0$ the
readout shows 1/N's 15.51%. No simulation. Note under the widget: the realized volatility uses the second half, so the
$c$ that minimizes it is hindsight.

**Examples** (results recomputed from the printed inputs):

- E1 §2 `split`, experiment 1: the model is the first window's mean and matrix ($\mathrm{SR}^*=0.880$ [A28-18],
  $\delta=11.27$ [A28-22]); 10,000 samples of 504 days. Mean true Sharpe ratio of $\hat{\mathbf f}$: 0.423 (SE 0.003)
  with means and covariances estimated, 0.425 (SE 0.003) with the means alone estimated, 0.87686 (SE 0.00002) with
  the covariances alone [A30-07]. Exposure SDs run from 28.8 to 80.7 points against 1.75 to 4.79 points (batch SEs
  0.2 to 0.6 and 0.01 to 0.04); fund by fund the ratio runs from 14.2 (00646: 67.1 against 4.73) to 18.0 (00635U:
  72.0 against 3.99), batch SEs 0.1 [A30-08]. In 2,115 samples (21%, SE 0.4 points) the exposures sum to zero or
  less [A30-09], so weights normalized to sum to 1 would flip sign: hence the exposure form. The median true Sharpe
  ratio is 0.489 (batch SE 0.004) [A30-07]: the mean is pulled down by a long left tail. The same draws measure the
  error in [[LM27]]'s risk shares: R1's true shares, 1.1% to 50.2% [A27-21], are estimated with SDs of 1.031 to 1.67
  points (batch SEs 0.007 and 0.01) [A30-42].
- E2 §2 `years`, why the means: by (20.2) the SE of an annual mean is $\sqrt A s/\sqrt\tau$, with $\tau=T/A=2.0745$
  years, a count of sessions [A28-02]. The annual volatilities $\sqrt A s$, 13.50, 11.87, 8.54, 9.39 and 23.17%
  [A28-06], give SEs of 9.4, 8.2, 5.9, 6.5, 16.1 points [A28-27] against means of 7.5, 10.0, 2.6, 0.8, −1.4% [A28-05];
  four of five means lie within one SE of zero [A30-06]. By (18.4), for normal returns with a known mean, the
  matrix's root-mean-square relative error at $T=504$ is 8.5% [A30-06]. More days over the same span shrink the second, not the first (KC). The
  plug-in minimum variance, which needs no mean, predicts 4.990% (SE 0.002) and delivers 5.0353% (SE 0.0001) against
  the possible 5.02% [A30-10, A28-10]. By (28.3) its true variance exceeds $\sigma^2_{\min}$ by its weight error's
  quadratic form, so no estimated portfolio can deliver less than $\sigma_{\min}$.
- E3 §3 `critical`, experiment 2: mean true Sharpe ratio 0.230, 0.322, 0.422, 0.546, 0.672, 0.759, 0.816 at 0.52 to
  33.2 years of sessions ($T/A$, sessions over $A$; SEs 0.008 to 0.001); with the covariances alone estimated, already
  0.8660 (SE 0.0002) at 0.52 years of sessions [A30-11]. Against 1/N's 0.327, the plug-in is about equal at 1.04 years
  of sessions (0.322, SE 0.008) and
  well above at 2.07 (0.422, SE 0.007) [A30-11]. In the window calculation of their §4, DeMiguel, Garlappi and Uppal judge the
  sample-based rule by its certainty-equivalent return, not by experiment 2's mean true Sharpe ratio. In their Figure 1's panel E, calibrated to US stocks, 1/N's
  monthly Sharpe ratio is 0.12 against the tangency's 0.15, and the sample-based rule needs more than 3,000 months
  with 25 assets to beat 1/N (§4, pp. 1939–1941). There 1/N reaches 0.8 of the best; in this model only 0.37 (0.327
  against 0.880) [A30-43], so the plug-in has much to gain, and the model's means do not move. The through case's
  out-of-sample volatilities, net of costs from March 2019, R1 12.48% against R3 9.96% [A30-12], are the evidence on E5; LM33 compares the rules' Sharpe
  ratios.
- E4 §4 `lwhand`, the first window by hand: $\bar\lambda=0.0204$ a year (a volatility of 14.3%),
  $\lVert\hat\Sigma-\bar\lambda I\rVert_F^2=1.885\times10^{-3}$, $\hat\sigma^2_{\hat\Sigma}=6.12\times10^{-5}$, so
  $\hat c=1-6.12\times10^{-5}/1.885\times10^{-3}=0.9675$; scikit-learn's `shrinkage_` 0.0325 equals $1-\hat c$ to rounding error (below $10^{-15}$)
  [A30-13]. With (18.4) for normal returns the oracle is $c^*=0.9851$; the data's noise estimate is 2.14 times the
  normal value [A30-13]. The excess comes from fat tails, chiefly 0050's (raw kurtosis 13.3 [A30-15]; its rows carry
  36% of the excess), and from 00642U's milder tails (raw kurtosis 4.5 [A30-15]) weighted by the largest variance
  (volatility 23.2% [A28-06]; 39% of the excess) [A30-13].
- E5 §4 `shortT`, U28's window lengths ([[ex:windows]]): on the last 30 returns of the first half the sample matrix has
  $\kappa=116{,}097$; its minimum-variance portfolio predicts 1.34% and realizes 43.12% on the second half, with gross
  exposure 13.48; shrunk with $\hat c=0.823$ it realizes 12.46% [A30-20]. On 20 returns the sample matrix is singular
  (rank 19, (10.7)): 18% of the vector $\mathbf 1$'s length lies outside its column space, so fully invested portfolios
  with zero predicted variance exist and the minimum is not unique [A30-20]. The pseudoinverse (12.7) gives the
  minimum-variance portfolio within the column space; it predicts 1.78% and realizes 17.03%, the shrunk matrix 12.59%
  [A30-20]. On the whole first half, $\hat c=0.9951$, $\kappa$ 126.05 → 121.38 and both realize 11.78% [A30-18,
  A30-19]. Experiment 3 confirms the pattern on average (mean true volatility at 60 returns 15.51% sample (SE 0.04),
  13.46% shrunk (SE 0.02); at 2,191, 11.4659% sample and 11.4651% shrunk (SEs 0.0006) against the possible 11.40%)
  [A30-21].
- E6 §4 `r5`, the through case: $\hat c$ ranged from 0.781 (2026-03-31) to 0.979 (2024-04-30), median 0.962 [A30-14].
  The largest gap between R5's and R3's weights is 13.1 points, at 2026-03-31 (00679B 55.1% → 42.0%); the median
  gap is 1.6 points [A30-16]. In that window 00642U's raw kurtosis is 48.9, its rows carry 84% of the excess noise,
  and the noise estimate is 13.1 times the normal value [A30-15]. With the normal value in its place, $\hat c$ would be 0.983, not
  0.781 [A30-15]: fat tails, not a short window, drove the shrinkage. The scaled-identity target raises the bond
  fund's variance (volatility 13.4%) toward the average and lowers 00642U's (43.0%), so weight leaves the bond fund
  [A30-16]. Realized volatility: R5 9.97%, R3 9.96% [A30-12].
- E7 §5 `jm`, U28's first half: $\hat\Sigma$ is PD (smallest annual eigenvalue 0.0058 [A30-18]), so the long-only
  problem, on a closed and bounded feasible set, has a minimizer, and only one ((29.3)). It holds 9 sectors, so 19 constraints bind [A30-22]; $\hat\Sigma_\nu$'s
  unconstrained minimum-variance weights equal them to rounding error (below $10^{-15}$), its smallest annual eigenvalue is 0.0059
  (PD), and Optoelectronic's variance falls by 20.7% [A30-22]; cvxpy's dual values give the same $\boldsymbol\nu$ to
  $3.7\times10^{-10}$ of the largest $\nu_i$ [A30-23]. Second half: 12.14% against the unconstrained 11.78% [A30-19].
  In experiment 3, paired on the same samples, the constraint lowers the true volatility against the shrunk
  portfolio by 0.38 points (SE 0.03) at 30 returns and 0.06 (SE 0.02) at 60, and raises it from 120 on (0.49
  points, SE 0.01, at 120; 1.2981, SE 0.0005, at 2,191) [A30-21].
- E8 §6 `bl`, R2 on the first window: mean excess 4.383%, volatility 6.709%, so $\delta=9.74$ and
  $\mathbf e_{\mathrm{eq}}=$ 7.79, 5.14, 0.46, 1.02, 3.71% [A30-24]. View $K=(-1,1,0,0,0)$, "00646 beats 0050": the
  window says $b=2.491$ points, the reference implies −2.649, $\sqrt{K\hat\Sigma K^{\top}}=12.264\%$ [A30-25]. With
  $n_0=504$, $c=0.5$ and $\mathbf f_{\mathrm{BL}}=$ 22.5 / 37.5 / 30 / 10 / 0%; with $c=1$, 4.9 / 55.1 / 30 / 10 / 0%;
  only 0050 and 00646 move [A30-25]. The plug-in at the same $\delta$: 13.6 / 72.4 / 43.8 / 3.0 / −17.1%, a total of
  115.8% before rounding [A30-25].
- E9 §7 `repair`, LM10's $C_{\text{pw}}$: eigenvalues −0.1621, 1.1471, 2.0149 [A30-28]. Shrinking toward $I$ with
  $c=1/(1-\lambda_3)=0.8605$ gives off-diagonal entries 0.845, 0.171, −0.382; clipping $\lambda_3$ to 0 and rescaling gives 0.852, 0.154,
  −0.385; the nearest correlation matrix (Higham 2002b) 0.864, 0.139, −0.379, PSD to rounding, and a second solver
  (cvxpy's CLARABEL) agrees to $1.4\times10^{-7}$; Frobenius distances to $C_{\text{pw}}$ 0.216, 0.211 and 0.209
  [A30-28]. The nearest correlation matrix minimizes $\lVert X-C_{\text{pw}}\rVert_F^2$ over PSD matrices with unit
  diagonal. That set is closed, bounded and convex, and the objective is strictly convex, so the minimizer exists and
  is unique. *Constructed* (LM10's).

**Problems plan** (12; MC keys C, A, B, C, A, B; the lab solves 10, 11, 12). Stems state the sample or the
hypothetical inputs, the divisor ($T$), the target ($\bar\lambda I$), the multiplier scaling ($\hat\Sigma\mathbf w=\nu_0\mathbf 1+\boldsymbol\nu$),
the units (a day or a year), the label and the rounding; problem 11 gives the seed and the draws.

1. MC: daily returns with $\sigma=20\%$ a year, $A=243$, $T=972$ returns (four years of sessions); the SE of the annual mean. A 0.64 points
   (divides by $\sqrt T$ days). B 5.0 (divides by the years). **C** 10.0 [A30-30].
2. MC: a $2\times2$ covariance matrix with eigenvalues 4 and 1 (%² a day) shrunk toward $\bar\lambda I$ with $c=0.8$;
   its condition number. **A** 2.85. B 4.00 (shrinkage read as a rotation). C 3.20 ($c$ times $\kappa$) [A30-31].
3. MC: normal returns with $\Sigma=\sigma^2I$, $N=10$, $T=250$; the oracle $c^*$. A 0.96 ($T/(T+N)$). **B** 0 (the
   target is the truth). C 1 (the sample matrix is unbiased) [A30-32].
4. MC: one data view with $T=504$ and a prior worth $n_0=1{,}512$ observations; the view says 4%, the reference
   implies 0%; the posterior along the view. A 3.0% (weights swapped). B 2.0% (equal weights). **C** 1.0% [A30-33].
5. MC: two funds, $\sigma_1=20\%$, $\rho=0.9$; the $(1,1)$ entry of $\Sigma^{-1}$ (a year). **A** 131.6 ($\operatorname{VIF}/\sigma_1^2$).
   B 25.0 (ignores $\rho$). C 250.0 ($1-\rho$ for $1-\rho^2$) [A30-34]. The solution adds that $1-\rho^2$ is the
   product of the correlation matrix's eigenvalues 1.9 and 0.1 (KC §4's matrix [A30-40]), so the small one drives the
   inverse that plug-in weights use, and shrinkage lifts it.
6. MC: long-only minimum variance; $w_3\ge0$ binds with $\nu_3=0.0002$ (daily units, the stem's scaling); in
   $\hat\Sigma_\nu$ asset 3's variance is lowered by. A $\nu_3$. **B** $2\nu_3=0.0004$. C 0 (only covariances change)
   [A30-35].
7. Derive (30.2); evaluate it for $\Sigma=\operatorname{diag}(4,1)$ (%² a day), normal returns with a known mean,
   $T=100$: $\lVert\Sigma-\bar\lambda I\rVert_F^2=4.5$, noise $0.42$ by (18.4), $c^*=0.9146$ [A30-36].
8. Derive (30.4) from the KKT conditions; two funds with daily volatilities 1% and 2% and $\rho=0.8$: unconstrained
   weights 133.3% and −33.3%, long-only (1, 0), $\nu_0=1$, $\nu_2=0.6$ (%² a day), $\hat\Sigma_\nu$ with entries 1, 1
   and 2.8, whose minimum-variance weights are (100%, 0) [A30-37].
9. Derive (30.5) for one view by (16.8), and show $\mathbf f_{\mathrm{BL}}=\mathbf w_{\mathrm{ref}}+K^{\top}c(b-K\mathbf e_{\mathrm{eq}})/(\delta K\hat\Sigma K^{\top})$;
   two funds, volatilities 20% and 10% a year, $\rho=0$ (their matrix is $\hat\Sigma$), $\mathbf w_{\mathrm{ref}}=(50\%,50\%)$, $\delta=4$, view $b=0$ on fund 2
   minus fund 1, $c=0.5$: $\mathbf e_{\mathrm{eq}}=(8\%,2\%)$, $\mathbf e_{\mathrm{BL}}=(5.6\%,2.6\%)$,
   $\mathbf f_{\mathrm{BL}}=(35\%,65\%)$ [A30-38].
10. Python: Ledoit–Wolf on E5's first window by hand and with scikit-learn ($\hat c=0.9675$); the normal oracle 0.9851;
    the ratio 2.14, each fund's share of the excess, and what they say about the tails [A30-13, A30-15].
11. Python: experiment 1 (`default_rng([1, 20261011])`, 10,000 samples): the mean true Sharpe ratios 0.423, 0.425 and
    0.87686 with their SEs, the share of samples in which 1/N's true Sharpe ratio is higher (31.4%, SE 0.5 points),
    and the 2,115 samples with $\mathbf 1^{\top}\hat{\mathbf f}\le0$; why 1/N wins so often, and which of
    DeMiguel, Garlappi and Uppal's three conditions for optimizing to win (p. 1919) the first window meets (a best
    Sharpe ratio well above 1/N's, 0.880 against 0.327, and few assets, but not a long window) [A30-07, A30-09, A28-18, A30-05].
12. Python: U28's windows of 30 and 2,191 returns ([[ex:windows]]'s rows), each result labelled *Out-of-sample*, and
    which repair the ratio of observations to assets favours at each length; the check of (30.4) on the first half
    (19 binding constraints; the weights agree to $10^{-15}$) [A30-20, A30-22].

**Lab parts** (`build/make_lab30.py`; reads only its `data/`, built locally by `data/make_lab_data.py` from
`data/raw/` and never committed, as the shared "Labs" decision lists: E5's estimation frame and its wealth frame with
the traded flags (both frames, decision on the first revision); the rules' per-date targets and exposures; the eight
rules' net and gross wealth paths, of which LM30 uses R1's, R3's and R5's net paths; `sectors_close_raw.csv` and `sectors_close_repairs.csv` for U28 and
the TAIEX price index, as LM23's lab builds them; $C_{\text{pw}}$'s three printed entries typed in; file names as `make_lab_data.py` sets them at Stage 3): 1 data, the first window, $T$,
$A$, U28's halves; 2 experiment 1 (E1, E2, X2, the sign flips, R1's risk shares), experiment 2 (E3, X3); 3 Ledoit–Wolf
by hand and scikit-learn (E4), (30.1)'s spectrum and $\kappa_c$ (X4), the path from 1/N at $c=0$; 4 U28's windows (X5,
E5), experiment 3, the pseudoinverse at $T=20$; 5 R5 re-implemented with scikit-learn's matrix and R3's exact solver,
checked against the targets at all 92 signals, X6, E6, the realized volatilities of R1, R3 and R5 from the wealth
paths; 6 (30.4) on U28 (E7) with cvxpy's dual values; 7 Black–Litterman (E8, X7, KC §6); 8 experiment 4 (resampled
weights with LM22's iid bootstrap; as a variant (lab only), LM22's stationary bootstrap with its own generator `default_rng([5, 20261011])`, 1,000
resamples in `stationary_idx`'s draw order, its
block length by LM22's rule (lm22.md:254) on the five funds' returns, the largest of the five, as the shared
"Counting" decision says), the single-index matrix (X8), the repairs of
$C_{\text{pw}}$ with Higham's alternating projections (E9); 9 problems 10–12. Extension (*Out-of-sample*, versions
declared, X40-style): LM7's question (make_lab07.py:601) answered on E5: the 0050/00679B
minimum-variance weight re-estimated each month on 6, 12, 24 and 36 calendar months of the estimation frame and held
on the wealth frame (shared "E5's two frames"), with the sample and the shrunk
$2\times2$ matrix (eight versions, all reported); a closing sentence says that choosing among them is LM34's subject.
Labs write plain "LM7" and "LM34", never `[[LM7]]`.

**Cross-module tags.** Only LM35's brief cites an LM30 tag ((30.4)); the other modules cite R5 and LM30's results by
anchor (decision C8; the cross-check confirms the list, Y1).

- (30.1) $\hat\Sigma_c:=c\hat\Sigma+(1-c)\bar\lambda I$, $\bar\lambda=\operatorname{tr}\hat\Sigma/N$, $0\le c\le1$: the
  eigenvectors of $\hat\Sigma$, eigenvalues $c\lambda_k+(1-c)\bar\lambda$, $\kappa_c=(c\lambda_1+(1-c)\bar\lambda)/(c\lambda_N+(1-c)\bar\lambda)$;
  PD for $c<1$ even when $\hat\Sigma$ is singular; the minimum-variance portfolio of $\hat\Sigma_0$ is 1/N.
- (30.2) $c^*=\lVert\Sigma-\Sigma_{\mathrm{tgt}}\rVert_F^2/\big(\lVert\Sigma-\Sigma_{\mathrm{tgt}}\rVert_F^2+\sigma^2_{\hat\Sigma}\big)$ minimizes
  $\E\lVert c\hat\Sigma+(1-c)\Sigma_{\mathrm{tgt}}-\Sigma\rVert_F^2$ over nonrandom $c$, when $\E\hat\Sigma=\Sigma$ (a known
  mean), $\Sigma_{\mathrm{tgt}}$ is nonrandom and fourth moments are finite; for normal returns
  $\sigma^2_{\hat\Sigma}=(\lVert\Sigma\rVert_F^2+(\operatorname{tr}\Sigma)^2)/T$ by (18.4).
- (30.3) $\hat c=1-\min\big(\hat\sigma^2_{\hat\Sigma},\lVert\hat\Sigma-\bar\lambda I\rVert_F^2\big)/\lVert\hat\Sigma-\bar\lambda I\rVert_F^2$,
  $\hat\sigma^2_{\hat\Sigma}=T^{-2}\sum_t\lVert(\mathbf R_t-\bar{\mathbf R})(\mathbf R_t-\bar{\mathbf R})^{\top}-\hat\Sigma\rVert_F^2$
  (Ledoit and Wolf 2004; consistency *stated without proof*; scikit-learn's `shrinkage_` is $1-\hat c$).
- (30.4) $\hat\Sigma_\nu=\hat\Sigma-(\boldsymbol\nu\mathbf 1^{\top}+\mathbf 1\boldsymbol\nu^{\top})$, with
  $\hat\Sigma\mathbf w^{\mathrm{lo}}=\nu_0\mathbf 1+\boldsymbol\nu$, $\boldsymbol\nu\ge\mathbf 0$, $\nu_iw^{\mathrm{lo}}_i=0$:
  $\hat\Sigma_\nu$ is PSD and $\mathbf w^{\mathrm{lo}}$ is one of its unconstrained minimum-variance portfolios
  (Jagannathan and Ma 2003, Proposition 1, *stated*); with $\hat\Sigma$ PD, $\hat\Sigma_\nu$ is PD and $\mathbf w^{\mathrm{lo}}$
  the only one, since $\mathbf x^{\top}\hat\Sigma_\nu\mathbf x=(\mathbf 1^{\top}\mathbf x)^2\nu_0+\mathbf y^{\top}\hat\Sigma\mathbf y$
  with $\mathbf y=\mathbf x-(\mathbf 1^{\top}\mathbf x)\mathbf w^{\mathrm{lo}}$ and $\nu_0=\sigma_p^2>0$ (LM35's checkpoint).
- (30.5) for one view $K\mathbf e=b+\varepsilon$, with $\varepsilon\sim\mathcal N(0,\Xi)$ independent of $\mathbf e$, on the prior $\mathbf e\sim\mathcal N(\mathbf e_{\mathrm{eq}},\hat\Sigma/n_0)$:
  $\mathbf e_{\mathrm{BL}}=\mathbf e_{\mathrm{eq}}+\hat\Sigma K^{\top}c\,(b-K\mathbf e_{\mathrm{eq}})/(K\hat\Sigma K^{\top})$ with
  $c=(K\hat\Sigma K^{\top}/n_0)/(K\hat\Sigma K^{\top}/n_0+\Xi)$, which is $T/(T+n_0)$ for a data view
  ($\Xi=K\hat\Sigma K^{\top}/T$); $\mathbf f_{\mathrm{BL}}=\mathbf w_{\mathrm{ref}}+K^{\top}c\,(b-K\mathbf e_{\mathrm{eq}})/(\delta K\hat\Sigma K^{\top})$.

**Pitfalls to pre-empt.**

- Normalizing plug-in tangency weights to sum to 1 divides by $\mathbf 1^{\top}\hat{\mathbf f}$, which is zero or
  negative in 2,115 of 10,000 samples (21%, SE 0.4 points) [A30-09]: §2 works with exposures at the model's fixed
  $\delta$, and says so.
- A simulation from a fixed model measures sampling error alone, under ideal conditions. Its truth is an in-sample
  estimate ($\mathrm{SR}^*=0.880$ is the first window's own optimum), and its returns are iid normal. Its means stay
  fixed, while real means move (LM24: the second half's sector means spread almost twice as widely, lm24.md:283). Experiment 2's result (about equal to 1/N at 1.04 years of sessions,
  well above at 2.07) is no recommendation; R1's and R3's realized volatilities are the evidence.
- Predicted against realized: an optimized in-sample variance is biased down (U28, $T=30$: 1.34% against 43.12%; E5:
  R3's windows predicted 8.84% on average [A30-12], 4.97% to 10.42% [A28-12], against 9.96% realized). Inputs
  that moved add to the gap, as in LM7.
- scikit-learn: `shrinkage_` is the target's weight $1-\hat c$; the divisor is $T$; `assume_centered=False` removes the
  mean; the target is $\bar\lambda I$ only; `OAS` is another estimator and omits Chen et al.'s $2/p$ factor (its
  source comment, read in the installed 1.9.1). The intensity is scale-free, so annual or daily inputs give the same
  $\hat c$ [A30-13]; solvers still get annual inputs (shared decision).
- Ledoit and Wolf's conditions: the oracle needs finite fourth moments and the consistency result bounded eighth
  moments (Assumption 2 of the working paper). TR23's $t$ fit has 3.065 degrees of freedom, so its kurtosis is infinite (lm15.md:349);
  E5's window to 2026-03-31 has a raw kurtosis of 48.9 (00642U), and there the noise estimate reacts to tails (13.1
  times the normal value; $\hat c$ 0.781 instead of 0.983) [A30-15]. Say what $\hat c$ responds to; never call it
  "the right amount of shrinkage".
- The scaled-identity target ignores unequal variances: it moved 13.1 points out of the bond fund at 2026-03-31
  [A30-16]. Shrinking the correlation matrix instead (keeping each variance) is another estimator; the through case
  keeps R5 as fixed.
- Shrinkage toward $\bar\lambda I$ keeps $\hat\Sigma$'s eigenvectors (30.1), so it cannot repair the unstable
  eigenvectors of LM11's (11.7); it only moves eigenvalues.
- A singular $\hat\Sigma$ has no unique minimum-variance portfolio (U28, $T=20$: zero-variance portfolios exist
  [A30-20]). The pseudoinverse gives the minimum within the column space, not the minimum: it predicts a volatility
  of 1.78% against 0 [A30-20]. Shrinkage with $c<1$ restores a unique minimum.
- Constraints are not free: wrong constraints cost when data are long (U28's second half 12.14% against 11.78%
  [A30-19]; in experiment 3 at 2,191 returns the long-only portfolio's true volatility is 1.2981 points above the
  shrunk one's, paired SE 0.0005 [A30-21]). In E5 the long-only constraint of R3 never binds (0 of 92 signals)
  [A29-09], so (30.4) is shown on U28.
- "Best $c$ in hindsight" is fitted on the judging half: *In-sample*, never an achievable result.
- Black–Litterman: the reference carries the prior, and R2 is *constructed* (no Taiwan market portfolio of these
  funds exists; `TaiwanStockMarketValueWeight` starts 2024-10-30, ROADMAP); $\delta$ is calibrated to R2's own window
  mean; the literature's scalar has no consensus value (Idzorek 2007 reports values near zero, 0.01–0.05, 1, and about
  one over the number of observations, each attributed there to other authors); the optimizer here uses $\hat\Sigma$,
  not the posterior covariance (said once).
- Counting: U28's split compares five estimators and seven window lengths; LM30 names no winner and points to LM34.
- Notation: a tilde means centred (so $\hat\Sigma_\nu$, not $\tilde S$); no $\alpha$ for an intensity; multipliers
  $\nu$, at half of LM29's scale; $\tau$ is years.
- Ownership: the first window's statistics, $\mathbf w^{\mathrm{tan}}$ and $\mathbf w^{\mathrm{mv}}$ are LM28's,
  echoed with LM28's IDs at LM28's precision, except E2's $\tau$ and volatilities beside (20.2)'s computation
  (decision C12); R1's first-window risk shares are LM27's (A27-21) and
  "R3 never binds" LM29's (A29-09); the U28 halves' statistics and R2's first-window mean excess return and
  volatility are LM30's; R1–R8's Sharpe ratios and standard errors, VaR, net results and scenario losses are LM33's,
  LM32's, LM34's and LM35's.

**Curriculum guidance carried** (`plans/vol-5.md`, table "Curriculum guidance"):

- Tie estimation, constraints, costs and hygiene (g:25): §5 shows a constraint acting on the estimate; R5 is the
  through case's estimation-robust rule, its hygiene fixed in advance.
- Say which layer the module adds (g:30): the first paragraph: LM28–LM29 assumed the inputs known; LM30 measures their
  error and repairs it.
- Three outcome levels (g:54–58): marked above, with the taught/practised/assessed map.
- Density (g:60–63): LM30 is one of the four dense modules; the code of the non-PSD repair, the bootstrap, the make_lab07
  exercise, R5's re-implementation and the depth of the Ledoit–Wolf argument go to the lab, problems and a Deep Dive.
- Fix windows, frequency, costs and criteria before evaluation (g:111): R5's settings are the through case's; U28's
  split is LM11's; the window grid is declared as chosen after the halves' result.
- "Data too thin to support more" (g:116): §2–§3 conclude that two years of daily data cannot support weights built on
  sample means (the plug-in keeps 0.423 of 0.880 on average, SE 0.003, and 1/N wins in 31.4% of samples, SE 0.5
  points).
- The checkpoint after Volume VI (g:45): LM30 practises "explain how constraints change the allocation" ((30.4), E7)
  and an out-of-sample comparison (X5, X8).
- Taught, practised, assessed (g:124): the map under the outcomes.

**Stage 4 for earlier modules.** `leads` gain 30 in lm07.md:6, lm09.md:6 ((9.5)), lm14.md:6 ((14.5)) and lm15.md:6
(the $t$ fit's 3.065 degrees of freedom), all on decision G's list; lm10, lm11, lm12, lm16, lm18, lm20, lm22, lm23, lm24 and lm26 already list 30.
lm07.md:786: Chopra and Ziemba (1993) gains its issue number, 19(2): 6–11 (on the plan's Stage 4 list; LM30 carries
it because §2 cites the paper as lm07.md:509 does, decision "Tags and leads"). No other wording change in the
published text: every hand-over above is kept as written (lm11.md:480's "pulling the small sample eigenvalues up" is
what (30.1) does; it also pulls the large ones down, which §4 says).

**Sources** (every reference LM30 cites, with the version read and the locations used; bibliographic data from
Crossref as project/SOURCES.md records them ("### LM30" and "Entries already in this list: Volume V locations"),
which override the earlier brief where the two differ; paraphrased, no quotation over one sentence):

- Ledoit, O. and M. Wolf (2004). "A Well-Conditioned Estimator for Large-Dimensional Covariance Matrices." *Journal of
  Multivariate Analysis* 88(2): 365–411, February 2004 (Crossref's issue date; OpenAlex dates it 2003, the online
  year). DOI 10.1016/S0047-259X(03)00096-4. Read in the authors' working paper of February 2001 (ledoit.net, the
  survey's copy): §2 (the oracle, Lemma 2.1 and Theorem 2.1, mean-zero data, finite fourth moments), §3 (Assumptions
  1–3: $p/n$ bounded, bounded eighth moments, a condition on products; Lemmas 3.2–3.5; the estimator (14); Theorem 3.2,
  consistency; Theorem 3.4, asymptotic optimality; Theorem 3.5, a bounded condition number). Lemma and theorem numbers
  are the working paper's: the text cites them as such or at section level. The journal text was not compared.
- Ledoit, O. and M. Wolf (2003). "Improved Estimation of the Covariance Matrix of Stock Returns with an Application to
  Portfolio Selection." *Journal of Empirical Finance* 10(5): 603–621, December 2003. DOI
  10.1016/S0927-5398(03)00007-0. The single-index target, from the abstract of the working paper of October 2001 (an
  optimally weighted average of the sample covariance matrix and the single-index covariance matrix). One sentence
  only.
- Ledoit, O. and M. Wolf (2004). "Honey, I Shrunk the Sample Covariance Matrix." *Journal of Portfolio Management*
  30(4): 110–119. DOI 10.3905/jpm.2004.110. The constant-correlation target, from the survey's reading of the working
  paper of November 2003 (§3.2, not re-read); abstract (OpenAlex): shrinkage pulls the most extreme coefficients toward
  the centre, and the challenge is the intensity. One sentence only.
- DeMiguel, V., L. Garlappi and R. Uppal (2009). "Optimal Versus Naive Diversification: How Inefficient is the 1/N
  Portfolio Strategy?" *Review of Financial Studies* 22(5): 1915–1953, May 2009 (online 2007-12-03; cite 2009). DOI
  10.1093/rfs/hhm075. Read by the source check in the published article (the copy on Garlappi's site). Printed, at
  these locations: the abstract (14 models, seven datasets, none consistently better than 1/N in Sharpe ratio,
  certainty-equivalent return or turnover); the criterion (§4, pp. 1937–1938: the expected mean-variance utility loss,
  that is the certainty equivalent, eqs. (18)–(22) and Proposition 1, for the sample-based rule under iid normal
  returns); the calibration of Figure 1's panel E to US stocks (p. 1939: monthly Sharpe ratios 0.15 for the tangency
  and 0.12 for 1/N); "more than 3000" months for 25 assets and more than 6000 for 50 (p. 1941; "around 3000" in the
  abstract, p. 1919 and the Conclusions, p. 1947); the conditions under which optimizing wins (p. 1919: a long
  estimation window, an ex ante Sharpe ratio well above 1/N's, few assets). Kept out: "1/N lies close to the tangency
  portfolio" (not in the paper), and Table 6's monthly values (p. 1943): the paper says that panel E's 0.12 comes from
  Table 6, whose 1/N values are 0.1356–0.1466, so only panel E's calibration is quoted, labelled as such.
- Jagannathan, R. and T. Ma (2003). "Risk Reduction in Large Portfolios: Why Imposing the Wrong Constraints Helps."
  *Journal of Finance* 58(4): 1651–1683, August 2003. DOI 10.1111/1540-6261.00580. Abstract (Crossref): non-negativity
  can reduce the risk of estimated optimal portfolios even when the constraints are wrong, and with it the sample
  covariance matrix does as well as factor models, shrinkage and daily data. Proposition 1 read in NBER Working Paper
  8922 (May 2002; the survey's copy): with only the non-negativity constraint the adjusted matrix is
  $S-(\lambda\mathbf 1^{\top}+\mathbf 1\lambda^{\top})$ in their letters, symmetric and PSD, and the constrained
  portfolio is one of its minimum-variance portfolios; the 2019 note places it on p. 1655 of the article. Cited with
  Jagannathan, R., T. Ma and J. Zhang (2019). "A Note on 'Risk Reduction in Large Portfolios: Why Imposing the Wrong
  Constraints Helps'." *Journal of Finance* 74(5): 2689–2696, October 2019. DOI 10.1111/jofi.12824 (its abstract: it
  corrects the proof of Proposition 2, not Proposition 1).
- Black, F. and R. Litterman (1992). "Global Portfolio Optimization." *Financial Analysts Journal* 48(5): 28–43. DOI
  10.2469/faj.v48.n5.28. Text not read (image-only scan): cited as the model's origin only, with no claim of its own.
- He, G. and R. Litterman (1999). "The Intuition Behind Black-Litterman Model Portfolios." Goldman Sachs Investment
  Management Research, December 1999 (date and series as Idzorek's reference list prints them; single-sourced); SSRN
  334304, DOI 10.2139/ssrn.334304 (Crossref: posted content, 2002). Abstract (Crossref): the unconstrained optimal
  portfolio is the scaled market equilibrium portfolio plus a weighted sum of view portfolios. Text not read; §6
  derives the statement for one view and cites the note for the general case.
- Idzorek, T. (2007). "A Step-by-Step Guide to the Black-Litterman Model." In S. Satchell (ed.), *Forecasting Expected
  Returns in the Financial Markets*, Elsevier (Academic Press), pp. 17–38. ISBN 978-0-7506-8321-0, DOI
  10.1016/B978-075068321-0.50003-0 (Crossref: book chapter, 2007, with no editor recorded; the editor from Open
  Library's record of the book). Read in the author's draft of 20 July 2004 (the survey's copy): reverse optimization,
  Formula (1); the posterior mean, (3); the scarce guidance on the scalar (values near zero, 0.01–0.05, 1, and about
  one over the number of observations, each attributed there to other authors). Formula numbers are the draft's.
- Jorion, P. (1986). "Bayes-Stein Estimation for Portfolio Analysis." *JFQA* 21(3): 279–292. DOI 10.2307/2331042.
  Already in SOURCES (LM24): abstract only; §6 states only that an empirical Bayes estimator of the means should
  outperform the sample mean in a portfolio; the shrinkage target stays unconfirmed.
- Chopra, V. K. and W. T. Ziemba (1993). "The Effect of Errors in Means, Variances, and Covariances on Optimal
  Portfolio Choice." *Journal of Portfolio Management* 19(2): 6–11. DOI 10.3905/jpm.1993.409440. In SOURCES (LM7).
  §2 cites it as lm07.md:509 states its finding; its ratios are not printed (shared decision "References");
  lm07.md:786 gains the issue number at Stage 4.
- Michaud, R. O. (1989). "The Markowitz Optimization Enigma: Is 'Optimized' Optimal?" *Financial Analysts Journal*
  45(1): 31–42. DOI 10.2469/faj.v45.n1.31. Abstract (the journal's own article page, saved 2026-10-24): mean–variance
  optimization tends to maximize the effects of errors in its inputs, and unconstrained optimization can give results
  inferior to equal weighting. Text not read (403); §7 cites it at this level only.
- Michaud, R. O. and R. O. Michaud (2008). "Estimation Error and Portfolio Optimization: A Resampling Solution."
  *Journal of Investment Management* 6(1), First Quarter 2008; no DOI; pages unverified (joim.com lists the issue, not
  the pages). Read by the source check in the New Frontier Advisors pre-publication copy (©2007, marked not to be
  quoted or reproduced without the authors' permission, so paraphrase only; its page numbers are the copy's). Printed,
  paraphrased: resampled efficiency was first proposed in Michaud (1998), chs. 6–7 (p. 3); its steps (p. 5): draw a
  mean vector and a covariance matrix around the point estimates (from an assumed distribution, or by the bootstrap),
  compute the efficient frontier of each draw, repeat, and average the weights of matched efficient portfolios, such
  as all the minimum-variance or all the maximum-return portfolios, or portfolios matched by utility (pp. 5–7);
  constraints are optional. Kept out: any quotation, the journal's pages, the authors' illustration (footnote 14) and
  the method's trademark and patent status. Experiment 4, which averages R4's long-only maximum-Sharpe portfolios (R3's minimum variance in the 12
  resamples where no fund's mean exceeds $r_f$), is named a variant.
- Michaud, R. O. (1998). *Efficient Asset Management*. Harvard Business School Press (publisher and year as the
  pre-publication copy's reference list prints them; Open Library: Boston, 152 pp., ISBN 0-87584-743-9). Not read;
  cited only as Michaud and Michaud (2008) describe it. The 2008 second edition (Oxford University Press) is not cited.
- Sharpe, W. F. (1963). "A Simplified Model for Portfolio Analysis." *Management Science* 9(2): 277–293, January 1963.
  DOI 10.1287/mnsc.9.2.277. Abstract (Crossref): a model with few parameters for the Markowitz analysis, 2,000
  securities analysed at a small fraction of the cost, with very nearly the same results. The single-index model's
  origin; text not read.
- Higham, N. J. (2002b), *IMA J. Numer. Anal.* 22(3): 329–343, and Rousseeuw, P. J. and G. Molenberghs (1993), *Comm.
  Stat. Theory Methods* 22(4): 965–984: in SOURCES (Volume II), data as Crossref holds them. Abstracts (OpenAlex):
  Higham, the nearest correlation matrix in two weighted Frobenius norms by modified alternating projections;
  Rousseeuw and Molenberghs, methods based on shrinking, a method based on eigenvalues and a new geometric method. §7
  attributes only these.
- Chen, Y., A. Wiesel, Y. C. Eldar and A. O. Hero (2010). "Shrinkage Algorithms for MMSE Covariance Estimation." *IEEE
  Transactions on Signal Processing* 58(10): 5016–5029, October 2010. DOI 10.1109/TSP.2010.2053029. Abstract
  (OpenAlex): for Gaussian samples, an improvement on Ledoit–Wolf and the oracle approximating shrinkage (OAS)
  estimator as the limit of an iterative approximation. Named in §8 as OAS's source; text not read.
- Kan, R. and G. Zhou (2007). *JFQA* 42(3): 621–656. DOI 10.1017/S0022109000004129. In SOURCES (LM24); Crossref's
  abstract: the plug-in portfolio can perform very poorly out of sample, and a portfolio that optimally combines the riskless
  asset, the sample tangency portfolio and the sample global minimum-variance portfolio dominates a portfolio of the
  first two alone. One
  sentence.
- Best, M. J. and R. R. Grauer (1991): not cited by LM30 (LM28's §5 cites it).
- Software: scikit-learn 1.9.1, installed source read 2026-10-24 (file:line as SOURCES's "scikit-learn 1.9.1" entry records them):
  `LedoitWolf.fit` centres the columns (`covariance/_shrunk_covariance.py:603-606`), divides by $T$, and returns
  $(1-\text{shrinkage})S+\text{shrinkage}\,\bar\lambda I$ (`:38-41`); `shrinkage_` is the target's weight (`:506-508`,
  set at `:610`), so $\hat c=1-$`shrinkage_`; `ledoit_wolf_shrinkage` (`:297-400`) is (30.3) term by term with a
  common factor $1/N$, and the hand computation agrees to rounding error (below $10^{-15}$) [A30-13]; `OAS`'s `_oas` (`:46-94`) omits Chen
  et al.'s $2/p$ factor and says so (`:66-71`). cvxpy 1.9.3 with CLARABEL 0.11.1: dual values of `y >= 0` [A30-23]; the
  nearest correlation matrix as a cone program [A30-28]; `psd_wrap` asserts positive semidefiniteness without testing
  it (`atoms/affine/wraps.py:83-96`), so the script wraps only a matrix it has built as one.

**Chinese terms** (`plans/vol-5.md`'s list, and 樂詞網 searched 2026-10-24 with the survey's script, all listings, 16
queries; rechecked the same day by the fresh pass of 1,817 searches that the decisions on the second recomputation
cite, whose minor additions are entered below; a Latin name before Chinese takes a space, as Frobenius 範數):

| English | 樂詞網 | Book |
|:--|:--|:--|
| shrinkage; shrinkage estimator | 收縮 (統計學名詞); 收縮估計量 (統計學名詞) | 收縮, 收縮估計量 (plan's list; LM24) |
| covariance matrix; estimation error; condition number | 共變異數矩陣; 估計誤差 (統計學名詞 "error of estimation"); 條件數 (統計學名詞, 數學名詞) | as listed (plan's list) |
| mean squared error | 均方誤差 (統計學名詞, "mean squared error (MSE)") | 均方誤差 |
| bias–variance tradeoff | 偏誤及變異數之抵換 (統計學名詞) | 偏誤及變異數之抵換 |
| sampling error | 抽樣誤差 (統計學名詞, 數學名詞, 管理學名詞) | 抽樣誤差 |
| Monte Carlo simulation | 蒙地卡羅模擬 (統計學名詞, 管理學名詞) | 蒙地卡羅模擬 |
| plug-in | plug-in principle 代入原則 (統計學名詞); no bare entry | 代入 (代入原則's form); 代入投資組合 the book's own |
| out-of-sample | out-of-sample forecasting 樣本外預測 (統計學名詞); no bare entry | 樣本外 (LM11's 樣本外檢定) |
| excess return | 超額報酬 (統計學名詞; 經濟學 "Excess returns"; 管理學名詞's 超額報酬 is its "abnormal return") | 超額報酬 (LM23) |
| eigenvalue | 特徵值；固有值 (統計學名詞); 固有值 (數學名詞, whose 特徵值 is "characteristic value; proper value") | 特徵值 (LM11) |
| Frobenius norm | Frobenius範數 (數學名詞) | Frobenius 範數 (LM18's Glossary) |
| ill-conditioned matrix | 病態矩陣 (統計學名詞, 數學名詞) | 病態矩陣 |
| correlation matrix | 相關矩陣 (統計學名詞, 數學名詞) | 相關矩陣 |
| nonnegativity | nonnegativity condition 非負性條件 (數學名詞) | 非負性條件 |
| active constraint | — (經濟學 有效限制; 數學名詞 起作用的約束) | 有效限制, as LM7's Glossary 緊限制式（有效限制） (lm07.md:769; decision on the Chinese terms) |
| weighted average | 加權平均(數) (統計學名詞) | 加權平均 |
| prior, posterior distribution | 事前分布; 事後分布 (SOURCES, Volume IV) | as LM24 |
| resampling; bootstrap | 重抽樣; 自助重抽法 (SOURCES, Volume IV) | as LM22 |
| factor model; single index model | 因子模型 (統計學名詞); 單一指標模型 (統計學名詞) | 因子模型; 單一指標模型 |
| equilibrium | 均衡；平衡 (統計學名詞); market equilibrium 市場均衡 (管理學名詞) | 均衡 |
| implied | compounds only (implied volatility 隱含波動度, 管理學名詞) | 隱含超額報酬 (implied excess returns), the book's own |
| reference portfolio; view; equal weights | no entry ("reference portfolio" 0 results; "views" none in these listings; "equally weighted index" 等權指數, 管理學名詞) | 參考投資組合, 觀點 (the book's own); 等權重 (LM10's) |
| Black–Litterman; Ledoit–Wolf; James–Stein | none for the first two; James-Stein估計量 (統計學名詞) | English kept; James–Stein 估計量 |

**Open before Stage 2.** None. A30-09's tie is settled by the "Decisions on the fresh check of the whole of Stage 1"
(2026-10-31): the coarser safe form, "2,115 of 10,000 (21%, SE 0.4 points)", as recommended. The question as it
stood:

1. **A30-09's exact tie.** The share of samples with $\mathbf 1^{\top}\hat{\mathbf f}\le0$ is exactly 21.15% (2,115 of
   10,000), and its SE of 0.4 points puts the last printed digit at one decimal, where 21.15 is a tie. The decision on
   the second recomputation ("the last printed digit sits at the standard error's first significant digit") gives no
   rule for a tie; Volume IV prints a tie with more digits or with a coarser form whose rounding is safe
   (`plans/vol-4.md`, LM23's 0.69645 printed as 0.696). Applied: "2,115 of 10,000 (21%, SE 0.4 points)" in the §2
   row, E1 and the first pitfall (problem 11 prints the count). Recommendation: keep this form, since the count carries
   the exact value and 21% keeps no digit that the SE does not support; the alternative is "21.15%", named as the exact
   share of these samples.

Closed in the revisions (2026-10-24 and 25, to the decisions on the first revision, on the second recomputation and
on the third revision):

- The first revision's Open 1, DeMiguel, Garlappi and Uppal (2009) beyond the abstract: the source check read the
  published article. E3 prints panel E's calibration (monthly Sharpe ratios 0.12 for 1/N and 0.15 for the tangency, p. 1939) and
  "more than 3,000 months" for 25 assets (§4, pp. 1939–1941), and it names the criterion of their §4, the certainty equivalent.
  It compares their ratio, 0.8, with this model's 0.37 (A30-43). "1/N lies close to the tangency portfolio" and
  Table 6's values stay out (Sources).
- The first revision's Open 2, Michaud: §7 attributes resampled efficiency to Michaud (1998) as Michaud and Michaud
  (2008) describe it, paraphrased; experiment 4 is named a variant, and Michaud (1989) stays at the level of its
  abstract (decisions on the first revision).
- The first revision's Open 3, the owner of R2's first-window mean excess return and volatility: LM30, by decision
  A4's exception; LM31 echoes the volatility as A31-16 prints it (6.709%).
- The first revision's Open 4, the tags LM30 cites: settled by the cross-check's tag table (Y1). The revised briefs of
  LM27–LM29 name LM30 as the user of (27.1), (27.2), (27.4), (27.5), (27.8), (28.2), (28.3), (28.6), (28.8), (28.9), (29.3), (29.4),
  (29.5) and (29.6), which are exactly the tags LM30 cites; only LM35 cites an LM30 tag, (30.4).
- The first window's span (the second recomputation's finding 1, Y3): A30-03 now measures from the close before the
  first return and echoes A28-02's 2.05 calendar years; $\tau=T/A$ is A28-02's as well, and LM30 prints it only in E2
  (decision C12's exception for a computation shown beside it). The verifier's check (2026-10-25) found that the
  computation also needs the volatilities' second decimal (11.9 over $\sqrt{2.0745}$ gives 8.26, which prints 8.3, not
  A28-27's 8.2), so E2 prints them at two decimals, 13.50, 11.87, 8.54, 9.39 and 23.17%, and all five SEs reproduce
  (A30-04, A30-06). The re-check found three decimals of $\tau$ enough (2.074 gives the same five SEs); $\tau$ stays
  2.0745, its fourth decimal keeping it off a rounding boundary, and A28-02's and A28-06's rows record both prints
  (decisions on the third revision).

Closed by the decisions on the briefs (2026-10-24): the first window's statistics are LM28's and LM30 echoes them
(A4; draft Open 1); the simulation's model is kept, with experiment 2 worded as "about equal at 1.04 years, well
above at 2.07" (D and "Per module"; draft Open 2; its lengths read "years of sessions" by the decisions on the third
revision); Black–Litterman uses one relative view, $\Xi=K\hat\Sigma K^{\top}/T$ and
$\delta=9.74$ (D; draft Open 3, so A30-41's alternative $\delta$ is withdrawn); no QLIKE loss (D, the brief's proposal
accepted; draft Open 4); the U28 window grid stays, labelled as chosen after the halves' result (D; draft Open 5); R5 is unchanged,
since no recorded decision changed the rules fixed in advance (shared "Through case"; draft Open 6); the first half's
long-only portfolio and the U28 halves' minimum variance are LM30's, LM29 cites them (A5; draft Open 7); (30.4)'s identity is
derived and its positive semidefiniteness stated (D, accepted; draft Open 8); the notation proposals and the multiplier
scale, said once in §5 (B4, B5; draft Open 9). Michaud (draft Open 10) became the first revision's Open 2, closed above.

## LM31 Risk Parity, HRP and Volatility Targeting

Stage 1 brief, drafted 2026-10-24 from the editor's spine (`plans/vol-5.md`, "### LM31 Risk Parity, HRP and Volatility
Targeting") and the shared decisions above it; revised the same day to the editor's decisions on the briefs
(`plans/vol-5.md`, "Editor's decisions on the briefs", A–G and "Per module", and "Decisions on the first revision")
and to the source check's report (decision F); revised a third time to "Decisions on the second recomputation and
cross-check" (the round-2 recomputation's findings, the cross-check's Y1, Y11, Y17–Y19, and the second hunt's
readings of LM31's sources); given a last pass on 2026-10-25 to the third revision's check and "Decisions on the
third revision"; revised on 2026-10-31 to the fresh check of the whole of Stage 1 (its changed anchors, A31-19 and
A31-39 among them, were reproduced by the fresh verification of 2026-10-31). Every number carries its anchor ID at first appearance; `data/vol5_anchors_lm31.py`
prints them all (46 rows, `## LM31` of `plans/vol-5-anchors.md`; A31-46 is a source check). Numbers quoted from
published modules carry their file:line; statistics another module owns ("Owners", shared decision "Through case";
decisions A1–A6) are echoed with that module's name and anchor ID, at most at the owner's precision unless a
computation shown beside them needs more (decision C12), and are not LM31's to print.

**Prereq:** `[7, 8, 10, 11, 16, 26, 27, 28, 29, 30]`. What each supplies (tags rechecked in `src/`; LM27–LM30's tags
as their briefs number them, cited by number, decision C8):

- LM7: the marginal variance $\partial V/\partial w_1=2(w_1\sigma_1^2+w_2\sigma_{12})$, twice the covariance with the
  portfolio (lm07.md:92–94), from which LM27 derives $\mathrm{MRC}_i$ and on which §2's budgets (31.1) build; (7.7), the
  two-asset minimum-variance weight
  (lm07.md:374), E1's comparison; Newton's method for two variables (lm07.md:619), which §3 runs in five as its first
  solver.
- LM8: (8.10), $\lVert\tilde{\mathbf x}/s_x-\tilde{\mathbf y}/s_y\rVert^2=2T(1-\rho)$ (lm08.md:288), and its per-date
  distance $\sqrt{2(1-\rho)}$ (lm08.md:290); (8.8), the triangle inequality (lm08.md:249), which makes $d_{ij}$ a metric;
  (8.5), the norm of the column distance.
- LM10: (10.4) $s_p^2=\mathbf w^{\top}\hat\Sigma\mathbf w$ (lm10.md:181); (10.8) $\nabla(\mathbf w^{\top}M\mathbf w)=2M\mathbf w$ for
  symmetric $M$ (lm10.md:403); the theorem that a quadratic is strictly convex exactly when its matrix is positive
  definite (lm10.md:437); the pitfalls at lm10.md:225 and :425; U28's equal-weight volatility 15.75% (lm10.md:36).
- LM11: (11.3), the spectral theorem (lm11.md:119), behind "positive definite"; (11.4), the bounds by the extreme eigenvalues (lm11.md:184), for §3's Deep Dive (in words); the eigenvalues $1+(N-1)\rho$ and
  $1-\rho$ of an equal-correlation matrix (lm11.md:222), which give the condition $-1/(N-1)<\rho<1$ of §2's result; the extreme value theorem on a closed and bounded set (lm11.md:249), for §3's Deep Dive;
  U28's halves, 2,191 returns each (lm11.md:387, 400).
- LM16: (16.4), $\Cov(M\mathbf X)=M\Sigma M^{\top}$ and $\mathbf a^{\top}\Sigma\mathbf a=\Var(\mathbf a^{\top}\mathbf X)\ge0$
  (lm16.md:220), for $\sigma_p^2$ and, by its argument, for the EWMA matrix being positive semidefinite; the link at lm16.md:225.
- LM26: (26.2), the EWMA (lm26.md:99), with $\lambda=0.94$ and its 11.2-day half-life (lm26.md:113); "EWMA has no
  long-run level, so its forecast for every later day equals tomorrow's" (lm26.md:142); (26.3)–(26.4), GARCH and its
  multi-step forecast (lm26.md:146, 163), for one sentence of §7 and the lab's extension; (26.8), QLIKE (lm26.md:361).
- LM27 (brief): E5's two frames; (27.1)–(27.3), the wealth recursion with drift, cash and borrowing, costs and
  $\mathrm{TO}_t$, for R8; R1 and R2; (27.5) $\operatorname{Cov}(R_i,R_p)=(\Sigma\mathbf w)_i$ and $\beta_{i,p}$, and
  (27.6) $\mathrm{MRC}_i$, $\mathrm{RC}_i$ and Euler's $\sum_i\mathrm{RC}_i=\sigma_p$, derived there only (decision A6)
  and cited by §2; R1's first-window risk shares (A27-21; decision A4 excepts them from LM28's first-window
  statistics), which X2 echoes.
- LM28 (brief): (28.2), the global minimum-variance portfolio, equal to R3 on the first window because every weight
  is positive there (A28-10), so that it gives the lower end of §2's ordering on that window; the first window's
  statistics (decision A4): the funds' volatilities and correlations (A28-06, A28-07, printed by LM28 to one and two
  decimals, and here at that precision unless a computation beside them needs more, decision C12), R1's volatility
  (A28-15) and $\mathbf w^{\mathrm{mv}}$ (A28-10), echoed in E1–E4 and KC §2.
- LM29 (brief): (29.2)–(29.3), convexity (a positive definite Hessian makes a function strictly convex; a strictly
  convex function has at most one minimizer; a local minimum of a convex function is global), for theorem (31.2);
  (29.5), KKT for long-only minimum variance (every held fund has the same $(\Sigma\mathbf w)_i$), for KC §2; R3 in its
  through-case form, the long-only minimum variance that is the lower end of Maillard et al.'s ordering; cvxpy,
  CLARABEL, tolerances and the solver-output rule.
- LM30 (brief): the realized out-of-sample volatility of R1, R3 and R5 (A30-12), 1/N and minimum variance on U28's
  halves (A30-19) and R2's first-window volatility (A30-24; decision A4's exception), echoed in §5 and E4.

**Leads:** `[32, 33, 34, 35]`, each of which lists 31 among its prerequisites (decision C9): LM32 (VaR, ES and
drawdowns of R6–R8; (31.7) for R8's exposure), LM33 (R6–R8's Sharpe ratios and tests; their realized volatilities,
A31-27, echoed), LM34 (its own net results, costs, annual turnover and financing sensitivity for R6–R8; it cites (31.7) and
echoes R8's exposure path, A31-29), LM35 (R6 by (31.1), R7, R8 by (31.7); R8's leverage into the 2020 and 2025 scenarios and its
caps against the ruin line).

**Forward links honoured.**

| Earlier text | Promise | Kept in |
|:--|:--|:--|
| lm07.md:94 | the marginal variance is twice the covariance with the portfolio, "a fact [[LM31]] builds into risk budgeting" | §2: LM27 turns it into (27.6), $\mathrm{MRC}_i=(\Sigma\mathbf w)_i/\sigma_p$ (decision A6); the budget conditions (31.1) are built on (27.6) and so on this fact |
| lm08.md:290 | "[[LM31]] groups assets by this distance" ($\sqrt{2(1-\rho)}$) | §4: HRP's $d_{ij}$ is half of it; single linkage on LM8's distance gives the same tree with doubled heights [A31-21]; HRP then clusters on the column distance of $d$ (Stage 4 note below) |
| lm10.md:225 | splitting $s_p^2$ into one share per asset, "and judging which split is meaningful", is [[LM27]]'s and [[LM31]]'s | LM27 owns the split; §2 uses it as a target and §5 judges it after the fact (R6's ex-post shares; each holding month's own target weights, on that holding month's covariance, give some fund a negative share in 29 of 91 holding months [A31-26]) |
| lm10.md:425 | entry $i$ of $2\hat\Sigma\mathbf w$ is a rate of change, not asset $i$'s share ([[LM27]], [[LM31]]) | §2: minimum variance equalizes the rates $(\Sigma\mathbf w)_i$ of held funds ((29.5)), ERC equalizes the products $w_i(\Sigma\mathbf w)_i$; KC §2 |
| lm16.md:225 | splitting $\sigma_p^2$ among assets is [[LM27]]'s and [[LM31]]'s | as lm10.md:225; LM27 derives (27.5)–(27.6) from (16.4), which §2 cites |
| lm26.md:183 | "[[LM31]] scales a position by such a forecast" | §6: R8 scales R6 by the EWMA (26.2); the lab's extension uses (26.4)'s GARCH forecast instead |
| lm26.md:409 | "Forecasting a whole covariance matrix is [[LM30]]'s and [[LM31]]'s subject" | §6: the EWMA matrix (31.8) in one paragraph, with the identity that R8's portfolio EWMA is its quadratic form [A31-31]; multivariate GARCH out of scope |

The grep of `src/*.md` and `src/pages/*.md` for `[[LM31]]` finds exactly these seven lines (lm07:94, lm08:290,
lm10:225, lm10:425, lm16:225, lm26:183, lm26:409); `build/make_lab*.py` has no plain "LM31". The spine missed none.

**Outcomes** ("After this module you should be able to:"; the level in brackets is the brief's, the page keeps the
verb):

1. [D] derive the budget conditions (31.1) and show when ERC gives inverse-volatility weights
2. [D] prove that a long-only risk-budget portfolio exists and is unique when $\Sigma$ is positive definite
3. [C] compute equal-risk and risk-budget weights by Newton's method and coordinate descent, and check them with cvxpy
4. [C] build an HRP portfolio from a correlation matrix, and explain why implementations can give different trees
5. [U] explain what risk-based weights assume, and why risk shares set in advance differ after the fact
6. [C] compute a volatility-targeted exposure from an EWMA forecast, with its cap, cash and borrowing
7. [C] judge a volatility target out of sample, and explain how periodic and risk-triggered rebalancing differ
8. [U] state the evidence on volatility-managed portfolios with its sample and design

Outcome 1 is decision A6's wording (LM27 derives the risk contributions). As sentences (§1 count, a formula one
token; decision C10): 12, 15, 16, 16, 16, 14, 15 and 11 words, 115 in all, average 14.4, none over 30. Taught /
practised / assessed (REVIEW_PROMPT item 10): 1 §2 / E1, E2 / P1–P3, P5's first part, KC §2; 2 §3 / E4 / P4, P5, KC §3; 3 §3, §8 / E3 / P5, P11;
4 §4, §8 / E5, E6 / P6, P7, P12, KC §4, KC §8; 5 §2, §5 / E7 / KC §5, P10's distractor A; 6 §6 / E8 / P8, P9, KC §6's first
part; 7 §7 / E9, E10 / P10, KC §7 (a), (b); 8 §6 / E8's last sentence / KC §6's second part.

**Owns.** Risk budgets $b_i>0$, $\sum_ib_i=1$, and the budget conditions $w_i(\Sigma\mathbf w)_i=b_i\,\mathbf w^{\top}\Sigma\mathbf w$
(31.1), derived from LM27's (27.6), which carries lm07.md:94 (MRC, RC and Euler's identity are LM27's, decision A6);
ERC as $b_i=1/N$; inverse-volatility weights and the two cases in
which they are ERC (two assets for any $\rho>-1$; equal correlations) (31.3), derived; ERC against minimum variance
(rates against products) and the ordering $\sigma_{\mathrm{mv}}\le\sigma_{\mathrm{erc}}\le\sigma_{1/N}$ (Maillard,
Roncalli and Teïletche 2010, *stated without proof*; their $\sigma_{\mathrm{mv}}$ is the long-only minimum variance,
Appendix A.3 of their 2009 working paper), with Bruder and Roncalli's (2012, §2.3.4, p. 10) ordering for
unequal budgets stated; existence and uniqueness of the long-only budget portfolio for positive definite $\Sigma$ and
positive budgets (31.2), *derived in full* (the minimizer's existence in a Deep Dive), with Bruder and Roncalli (2012,
§2.3.3, pp. 9–10) as the source for unequal budgets, whose argument there is a sketch (source check, decision F); why
uniqueness needs long-only and positive budgets (Jacobi's non-long-only solution on E5; zero budgets, §2.2, pp. 4–5);
Newton's method on $h$ (as `vol5_rules.erc`), cyclical coordinate descent (31.4) (Griveau-Billion, Richard and
Roncalli 2013; convergence *stated without proof*, Tseng 2001), the fixed point $w_i\propto b_i/\beta_{i,p}$ (a
property of the solution, Bruder and Roncalli's eq. (7), p. 9) and its failure as an iteration, cvxpy's log form as the
check; HRP as published (López de Prado 2016): $d_{ij}$ and the factor 2 to
LM8's distance, the column distance, single linkage, the quasi-diagonal order, recursive bisection (31.5)–(31.6); why
implementations differ (the author's code against linking on $d$); that the bisection cuts the ordered list, not the
tree; R6's and R7's weights and ex-ante risk shares across the 92 signals, R6's ex-post risk shares, and the realized
volatility of R6, R7 and R8; R2's first-window risk shares (decision A4's exception); U28's tree, its heatmap, and the out-of-sample volatility of
inverse-volatility, ERC and HRP on U28's halves (1/N and minimum variance there are LM30's, decision A5); R8 (31.7): the
EWMA forecast of R6's book, $L_t$, the cap, cash and financing, the exposure path, the per-trade statistics of R8's
exposure (decision A2), the domain check; the EWMA covariance matrix in one paragraph and its identity with R8's
forecast (31.8); judging R8 holding month by holding month against its target and judging the forecast by QLIKE;
periodic re-estimation against a risk trigger (the April 2025 case; the trigger itself an in-sample lab illustration,
its threshold fixed by decision D); the evidence on volatility management (Moreira and Muir 2017; Harvey et al. 2018)
stated with its sample and design. Values owned: every A31 anchor except the echoes named in "Data role".

**Leaves.** Kelly-type sizing and its comparison with volatility targeting → Volume VIII (LM41–LM43; ROADMAP's Kelly
row). VaR, ES and drawdowns of R6–R8 → LM32. Their Sharpe ratios, intervals and tests → LM33. Net wealth,
growth, costs, gross against net, the annual turnover of every rule (A34-06; decision A2) and R8's financing
sensitivity at spreads of 0 and 5 points → LM34. Each rule's loss on 7 April 2025, R8's crash behaviour and its caps
against the ruin line → LM35 (decision A1). The first window's fund statistics, R1's first-window volatility and R3's
first-window weights → LM28 (decision A4); R1's first-window risk shares → LM27 (A4's carve-out, A27-21). 1/N,
minimum variance and shrinkage on U28's halves, R1's, R3's and R5's realized volatility (decision A5), and R2's
first-window volatility (A4's exception, A30-24) → LM30. Multivariate GARCH → out of scope (one
sentence). Choosing $\lambda$, the cap or a trigger threshold by backtest → LM34's search. Other linkages and
tree-following splits → not in the book, one sentence (López de Prado notes that stage 3 could split along the tree's
clusters instead, p. 11 of the SSRN version). To the lab (density): R7 re-implemented at all 92 signals,
the risk-triggered variant of R8, the GARCH-scaled variant.

**Uses before taught** (one sentence each in the text):

- §6: "The financing rate, 3.5% a year, is the through case's illustrative rate, since no official one exists. [[LM34]] gives the sources of the commission and the tax, and R8's growth at other spreads."
- §6: "The tail risk of the scaled book, its value at risk and expected shortfall, is [[LM32]]'s subject."
- §7: "What R8 lost on 7 April 2025 is [[LM35]]'s replay; this module reports only its exposure and that holding
  month's volatility."
- §7: "R8's annual turnover and what it costs are [[LM34]]'s; this module reports the size of its trades."

**Data role.**

- **E5** (shared decision "Data"; `data/vol5_series.py` → `data/processed/vol5_frames.parquet`, through
  `vol5_series.frames("E5")`; FinMind `TaiwanStockPrice`, `TaiwanStockDividendResult`, `TaiwanStockSplitPrice`,
  retrieved 24 October 2026). Estimation frame $T=2{,}362$ joint one-session returns, 2017-01-18 → 2026-10-08,
  $A=242.95$ [A31-01]; wealth frame 2,368 sessions, $A_{\mathrm w}=243.57$, 9.7221 years (calendar days ÷ 365.25
  from the close before the first return, 17 January 2017, to 8 October 2026; AUTHORING §8, decision C7) [A31-02]
  (LM27 describes both, A27-01–A27-03, and prints $A$ and $A_{\mathrm w}$ to three decimals; here to two decimals). Schedule: 92 signals, 27 February 2019 (traded 4 March 2019) to 30
  September 2026 (traded 1 October 2026); the first window is the 504 estimation rows 13 February 2017 → 27 February 2019
  (LM28's A28-02) [A31-03]. Out-of-sample returns: 1,851 sessions from 5 March 2019 (LM28's A28-03); 91 complete holding months of 12–23 sessions, the
  5-session tail to 8 October 2026 left out [A31-04]. A holding month runs from the session after a trade through the
  next trade and is named by those dates (the one after the 1 April 2025 trade is 2 April → 2 May 2025); "month" in
  this module always means a holding month, never a calendar month (decision C7). Funds named as the plan names them:
  0050, 00646, 00679B (the bond fund), 00635U (the gold-futures fund), 00642U (the oil-futures fund); LM27's brief
  records each index from its issuer, and LM31 uses LM27's wording.
- **The through case** (`data/vol5_rules.py`, imported, never re-implemented for a printed number): R6, R7 and R8 from
  `signals()`, their paths from `wealth_path()` and criteria from `summary()`. The script recomputes R8's two
  volatilities from R6's weights and asserts them equal to `signals()`'s, and replays HRP's steps on the first window,
  asserted equal to `hrp()`.
- **U28** (Volume II; `data/lm10_series.py`'s `u28()`, FinMind `TaiwanStockPrice`, retrieved 11 October 2026, closes
  repaired by `data/vol2_series.py`): $T=4{,}382$, $A=245.48$; halves of 2,191 (LM11's) [A31-05]. Price indices,
  covariance only: every caption says so, and no mean of U28 is used.
- **Echoes** (other modules' statistics, printed only with their owner and anchor named, at most at the owner's
  precision unless a computation beside them needs more; decisions A4, A5, C12): the first window's fund volatilities
  and correlations (LM28's A28-06, A28-07; one and two decimals, except E1's and E2's volatilities, whose weights need two, and
  E5's variances, taken from the unrounded $\hat\Sigma$) [A31-06]; R1's first-window risk shares (LM27's A27-21, A4's
  carve-out) and volatility (LM28's A28-15), R3's first-window weights and volatility (LM28's A28-10) [A31-12,
  A31-13]; R2's first-window volatility (LM30's A30-24, A4's exception; LM30 prints 6.709% beside its $\delta$)
  [A31-16]; 1/N and minimum variance on U28's halves (LM30's A30-19) [A31-23]; the realized volatility of R1, R3 and R5
  (LM30's A30-12) [A31-27]. R2's first-window risk shares are LM31's (A4's exception) [A31-16]. A31-36 holds only R8's
  per-trade statistics (decision A2); annual turnover is LM34's A34-06, not printed here.
- **Conventions.** Covariances divide by $T$ (`cov0`). Annualized volatilities: $\sqrt A$ with the estimation frame's
  $A$ for window quantities, U28's $A$ for U28, $\sqrt{A_{\mathrm w}}$ for a rule's realized volatility over the
  out-of-sample period. Risk shares $\mathrm{RC}_i/\sigma_p$ ((27.6)). Weights and risk shares are scale-free: ERC on
  the daily or the annualized covariance agrees to rounding (below $10^{-15}$) [A31-15]. Realized volatility of a rule:
  `summary()`'s centred standard deviation (divisor $T$) of daily net returns. A holding month's realized volatility: the uncentred
  root mean square of its daily net returns (as $\bar\sigma_t$ is uncentred), divided by $\bar\sigma_t$ at its signal,
  in daily units; where an annual figure is printed beside such a ratio, the holding month's figure and its target are both
  annualized with the target's $A=242.95$, so that the ratio reads off the printed figures [A31-34] (decision on the
  first revision, LM31). The SD of the log ratio divides by the 91 holding months (the book's divisor $T$). QLIKE is
  (26.8), with the holding month's mean squared daily return as $V$; the EWMA wins a holding month when its QLIKE is the lower,
  and a win's gain or a loss's cost is the gap between the two QLIKE values [A31-35]. Quantiles `inverted_cdf`;
  counts with the 1e-12 guard. A gap at machine precision prints as a bound ("to rounding"), since its digits depend on
  the order of the operations. Weights and shares are rounded separately from unrounded values that sum to 1; where
  the printed parts do not sum to the total, the text says "rounded separately" and gives their printed sum
  (PITFALLS). Values within a tenth of a unit of a rounding boundary at the precision printed here are flagged in the
  anchor's Printed column only; the text prints the rounded value without a mark (decision C11).
- **No simulation in the text.** The widget's test in `data/lm31_charts.py` draws 500 random positive definite
  $3\times3$ matrices with `default_rng([1, 20261011])` (experiment 1) to compare the widget's code with `erc()`; it
  prints no statistic.
- **Published files.** X7 holds 92 values (one per trade) and X8 91 (one per holding month); X2–X6 are per-window or
  full-sample statistics. No file carries a daily series (the X37 rule, decision C3).
- **Scripts.** `data/lm31_numbers.py` (every printed value, asserted against `src/lm31.md`, compared with the anchors),
  `data/lm31_charts.py` (X2–X4, X7, X8, the widget block and its Node test); both after `data/vol5_series.py`,
  `data/vol5_rules.py`'s outputs and `data/vol2_series.py`.

**Hygiene declaration.** *Descriptive:* the first window's weights, risk shares and trees (E1–E6, X2); U28's
full-sample tree, heatmap and in-sample volatilities (X3, X4, X6's in-sample column). *Out-of-sample* (fixed in advance
on 2026-10-24): R6, R7 and R8 in the through case (weights at each signal, exposure path, realized volatility, ex-post
risk shares, holding-month ratios), three of the through case's eight rules; the two variance forecasts made at each signal
and scored by QLIKE; U28's halves, one fixed split in LM7's pattern, LM31's three portfolios (inverse volatility, ERC,
HRP) beside LM30's 1/N and its long-only and sample minimum variance (A30-19): six portfolios on one split. *In-sample illustrations*, not
candidates: inverse-volatility weights on E5, the budget portfolio of E4, the tree linked on $d$, Jacobi's fixed point,
and the lab's risk-triggered variant (its threshold, 0.5, fixed by the editor on 2026-10-24 before any lab result,
decision D) and GARCH-scaled variant. *Constructed:* the widget's and the problems' inputs. Local
note: "R6, R7 and R8 are three of the eight rules fixed on 24 October 2026, before any result was computed. Their
weights use only the 504 joint dates up to and including each month-end, and they trade at the next session's close.
So every through-case result is out of sample. Whether one rule beats another is [[LM33]]'s test, across eight
rules." A second paragraph follows: "Weights, risk shares and trees on one window are descriptive plug-in estimates whose sampling error this module does not measure. On U28 one split was fixed in advance, and three
risk-based portfolios are compared with [[LM30]]'s 1/N and its two minimum-variance portfolios. Other variants are illustrations, not
candidates."

**Notation.** AUTHORING §6 with the Portfolios table. Used: $R$, $\mathbf R_t$, $T$, $t$, $A$, $A_{\mathrm w}$ (the
through case's), $N$ ($N=5$ on E5, 28 on U28), $i$, $j$, $\mathbf w$, $w_i$, $\mathbf 1$, $\Sigma$, $\hat\Sigma$,
$\sigma_i$, $\sigma_{ij}$, $\rho$, $\rho_{ij}$, $\bar\rho$, $C$, $\sigma_p$, $\sigma_p^2$, $\beta_{i,p}$,
$\mathrm{MRC}_i$, $\mathrm{RC}_i$ (LM27's), $\mathbf f$, $L_t$, $\lambda$ (LM26's decay only), $r_f$, $\mathrm{TO}_t$,
$\lVert\cdot\rVert$ ((8.5)), $\Var$, $\Cov$, $\kappa$ not used. Local symbols, declared in the notation note:

| Symbol | Meaning | Check |
|:--|:--|:--|
| $\mathbf b$, $b_i$ | risk budgets, $b_i>0$, $\sum_ib_i=1$ | §6's scoped row; LM31 writes its constraints out, without $K\mathbf w=\mathbf b$; no bets |
| $\mathbf y$, $y_i$ | unnormalized positions, $\mathbf w=\mathbf y/\mathbf 1^{\top}\mathbf y$ | §6's scoped row ("in LM31 the ERC variable before normalizing"; decision B3); LM31 has no least squares and no yield |
| $h(\mathbf y)$ | $\tfrac12\mathbf y^{\top}\Sigma\mathbf y-\sum_ib_i\ln y_i$ on $\mathbf y>\mathbf 0$ | §6's generic function $h$ |
| $d_{ij}$; $\mathbf d_j$ | HRP's distance $\sqrt{(1-\rho_{ij})/2}$; column $j$ of the matrix $(d_{ij})$, so the column distance is $\lVert\mathbf d_i-\mathbf d_j\rVert$ | §6's row; $\mathbf d_j$ accepted as declared (decision B5; §6 "column $j$ of a matrix is $\mathbf m_j$") |
| $\sigma^2_{(1)}$, $\sigma^2_{(2)}$ | the variances of the two halves' inverse-variance portfolios in a bisection | accepted as declared (decision B5); not $V$ (LM26's realized measure, which §7's QLIKE uses) nor the paper's $\alpha$ |
| $\bar\sigma_t$, $\sigma_{t+1\mid t}$ | R8's window volatility, uncentred, and the EWMA forecast of R6's book at signal $t$ | as §6, no hat, as LM26 prints it (decision B1) |
| $\Sigma_{t+1\mid t}$ | the EWMA covariance matrix (31.8), on simple returns $\mathbf R_t$ | as §6 (decision B1) |
| $\mathbf w_t^{\text{R6}}$ | R6's target weights at signal $t$, in (31.7) | an upright label, as $\mathbf w^{\mathrm{mv}}$ |
| $\Sigma_{\text{start}}$ | the start of (31.8) in P9: the window's uncentred second-moment matrix | a subscripted standard symbol (AUTHORING §6) |
| $V$ | a holding month's mean squared daily return, the target of (26.8) | LM26's $V_t$ role; only in §7 |
| $m$, $k$ | sessions in a holding month; the holding-month index (1–91) | §6's $m$ (days summed); $k$ is no lag here |

Not used: $\lambda$ as a multiplier ((29.5)'s multipliers are cited in words), $c$ (the Kelly fraction; the coordinate
update writes $(\Sigma\mathbf y)_i-\sigma_i^2y_i$), $\alpha$ (the paper's split factor), $\tilde d$ or $d'$, $V$ for a
cluster variance, $\sigma_{\mathrm{tgt}}$ (§6's fixed volatility target; R8 has none), $K\mathbf w=\mathbf b$,
$\mathbf e_i$, $\kappa$.

**Motivating case: "Equal risk, then a forecast"** (box; 162 words in three paragraphs of 56, 74 and 32; 11 sentences,
average 14.7 words, the longest 24, which carries one chain of reasoning to its "so"; decision C10)

> A fund that cannot trust estimated means can still share risk evenly. On 31 March 2025 rule R6 did that for E5's
> five funds. It put 30.7% in the bond fund 00679B and 12.0% in the oil fund 00642U, so each fund carried a fifth of the
> risk [A31-32]. Rule R8 then scales R6 by a forecast.
>
> R6's book had been calm: its EWMA forecast was 5.89% a year, against 7.84% over the last 504 sessions. So on 1
> April R8 held 1.33 times its equity in the funds, borrowing the extra 0.33 at 3.5% a year [A31-32, A31-37]. On 7
> April, the first session after the Qingming holiday, the forecast jumped to 23.58%, an implied exposure of 0.33. R8
> trades only after a month-end, so it kept its leverage until 2 May.
>
> Over that holding month its realized volatility was 5.78 times its target, the worst of all 91 [A31-34]. Does a
> forecast keep risk steady? And what does an equal share of risk buy?

Resolved: (a) the forecast: §7, E9, E10: over 91 holding months R8's realized-to-target ratio has median 0.98 against
R6's 0.83, but the same spread (SD of its logarithm 0.421 for both) [A31-34]; as a forecast of R6's next holding month
the EWMA's mean QLIKE is 0.791 against the window's 0.691, and without the one holding month 2 April → 2 May 2025 the
order reverses [A31-35], because a one-day forecast stands for a whole holding month (lm26.md:142) and a month-end rule
cannot meet a gap. (b) equal risk: §2, §5, E7: the shares are equal on the window by construction; on the covariance
of the 1,845 joint dates that followed (5 March 2019 → 8 October 2026), the mean of R6's 92 target weights carried
20.5, 19.2, 19.2, 23.1 and 18.0% of the risk, while each holding month's own target weights, on that holding month's
covariance, gave shares that ranged widely, and some share was negative in 29 of 91 holding months [A31-26]. The
qualifying date (the "first session after the Qingming holiday") is PITFALLS §7's; no cause of the fall is printed.

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | capability layer: allocate by risk alone, then scale the book by a forecast; case + X1; roadmap; notation and hygiene notes | 380 |
| 2 | Risk Contributions as Targets {1,5} | R1's first-window shares (LM27's A27-21) as the picture; (27.5)–(27.6) cited, not re-derived (decision A6; lm07.md:94's fact is in (27.6)); budgets and (31.1), derived from (27.6); ERC; E1 (two funds: inverse volatility for any $\rho>-1$); equal correlations → inverse volatility, derived, with LM11's condition (that it is the only solution is (31.2), Section 3); minimum variance equalizes rates, ERC products (lm10.md:425; (29.5)); the ordering stated (Maillard et al.; its lower end is the long-only minimum variance, R3, which equals (28.2)'s $\mathbf w^{\mathrm{mv}}$ on the first window); E2, X2; pitfall: a risk share is not a weight and not a loss share; 導讀 (its 風險預算 is a budget per asset, where LM7's capped the total volatility); KC | 590 |
| 3 | Budgets: Existence, Uniqueness and Computation {2,3} | theorem (31.2), three hypotheses listed, proof in the text by (29.2)–(29.3), existence of the minimizer in a Deep Dive; why long-only and positive budgets (Bruder and Roncalli 2012, §2.2); Newton (gradient $\Sigma\mathbf y-\mathbf b/\mathbf y$, Hessian $\Sigma+\operatorname{diag}(\mathbf b/\mathbf y^2)$); CCD (31.4) and its convergence stated; Jacobi's fixed point; cvxpy's log form as the check, with its tolerance (decision C5); E3, E4; pitfall: a fixed point that is not a descent; 導讀; KC | 650 |
| 4 | Hierarchical Risk Parity {4} | X3, X4 (U28); $d_{ij}$ (31.5) as half of (8.10)'s per-date distance, a metric by (8.8); the column distance; single linkage; scaling leaves the tree (LM8's promise); quasi-diagonal order (each merge lists its lower-numbered member first: the assets are numbered 1 to $N$, E5's in the order 0050, 00646, 00679B, 00635U, 00642U, and the cluster of merge $k$ is number $N+k$, as SciPy's `linkage` and `leaves_list` do); bisection (31.6), the first half of $n$ items taking $\lfloor n/2\rfloor$; no inverse needed; U28's full-sample weights and in-sample volatilities (X4's note, A31-22); E5 (three funds by hand), E6 (R7's first weights; the cut separates 0050 from 00646); pitfall: two codes, two trees (the author's code reads the square matrix as observations and gives the column-distance tree at all 92 windows and on U28, A31-19; linking on $d$ changes 17 of 92 orders, A31-20); 導讀; KC | 670 |
| 5 | R6 and R7 Out of Sample {5} | X5: weights and ex-ante shares across 92 signals; E7: R6's ex-post shares; realized volatility 10.32% and 10.14% (A31-27), beside LM30's R1, R3 and R5 (A30-12; R1's 12.48% named as out of sample, decision C7); X6: U28's halves, HRP the lowest out of sample of 1/N (LM30's) and LM31's three (IV, ERC, HRP), and above LM30's long-only minimum variance (A30-19); López de Prado's Monte Carlo stated with its design; whether one rule beats another is [[LM33]]'s (the hygiene note); KC | 480 |
| 6 | Volatility Targeting: R8 {6,8} | (31.7): $\bar\sigma_t$, (26.2) on R6's book (simple returns, uncentred), the cap, cash at 1.5%, borrowing at 3.5%, drift, cash and borrowing in the wealth recursion by (27.1)–(27.3); domain check; E8 (first signal by hand); X7 (exposure path; the ranges of $\bar\sigma_t$ and the forecast over the 92 signals, A31-30; the largest uncapped ratio, A31-29); the EWMA matrix (31.8) and its identity; evidence: Moreira and Muir (design and sample), Harvey et al. (where the Sharpe ratio improves, where only the vol of vol and the left tail do); pointers to [[LM32]], [[LM34]]; pitfall: R8's target moves with R6's own past; 導讀 (指數加權移動平均模型, as LM26); KC | 650 |
| 7 | Judging the Target Out of Sample {7} | X8: 91 holding months' ratios, R6 against R8; E10: QLIKE of the window and the EWMA, the EWMA's wins against its losses, the one holding month that decides the comparison, the two crash holding months; R8's realized volatility over the whole period (A31-27); why (lm26.md:142; (26.4) reverts); E9: April 2025, periodic re-estimation against a risk trigger (guidance); the trigger as a lab illustration, its threshold 0.5 fixed by decision D; the size of R8's trades (mean 9.2% one-way over the 91 trades after the first purchase, the largest 45.2%, A31-36; annual turnover is [[LM34]]'s, decision A2); the data do not support R8's leverage on E5 (guidance g:116); case resolved; pitfall: a month-end rule cannot meet a gap; 導讀; KC | 590 |
| 8 | Risk-Based Allocation in Python {3,4} | NumPy CCD and Newton; cvxpy `Minimize(0.5*quad_form(y, psd_wrap(S)) - b @ log(y))` with CLARABEL and the status check; SciPy `linkage(squareform(D2), "single")` after symmetrizing `D2` and setting its diagonal to 0 (then `squareform`'s checks pass, so `checks=False` is not needed), `leaves_list`, the `ClusterWarning` that a square, symmetric, non-negative, hollow matrix triggers; lab box | 200 |
| — | Summary (8) / Problems (12) / Solutions | | 150 / 420 / 540 |
| | **Total** | | **5,320** |

**Elements.** 10 examples (E1, E2 §2; E3, E4 §3; E5, E6 §4; E7 §5; E8 §6; E9, E10 §7). Knowledge checks:

- §2: On the first window R3 holds 41.4% in 00679B, and 41.4% of its risk is there (LM28's A28-10, A28-11: a
  minimum-variance share equals its weight) [A31-13]. R6 holds 33.9% in 00679B, yet that fund carries only 20% of R6's
  risk [A31-10, A31-13]. Why less than its weight? Minimum variance equalizes the rates $(\Sigma\mathbf w)_i$ of held funds
  ((29.5)); ERC equalizes the products $w_i(\Sigma\mathbf w)_i$. 00679B's rate is low, since it is the calmest fund
  (8.5%, LM28's A28-06) and moves against the equity funds, so a large weight buys only a fifth of the risk.
- §3: R2 holds no 00642U. Can its weights serve as risk budgets for all five funds? No: a zero budget removes that
  fund's log term, so (31.1) can have several solutions (Bruder and Roncalli 2012, §2.2, pp. 4–5) and theorem (31.2)
  does not apply. CCD's update (31.4) still runs, but it sets that fund's $y_i$ to 0 whenever
  $(\Sigma\mathbf y)_i-\sigma_i^2y_i\ge0$, outside $\mathbf y>\mathbf 0$. Drop the fund and budget the other four (E4).
- §4: Build the tree with LM8's $\sqrt{2(1-\rho)}$ instead of $d_{ij}$: every distance doubles, single linkage
  compares distances only, so the merges are the same and the heights double [A31-21].
- §5: The mean of R6's 92 target weights took 23.1% of the realized risk from 00635U, not 20% [A31-26]. Why can
  equal ex-ante shares end unequal? The shares are set on the trailing window's $\hat\Sigma$; the covariances moved.
- §6: (a) At the first signal $\bar\sigma_t=5.45\%$ and the EWMA forecast 6.42% a year; find $L$ and the cash
  [A31-28]: 0.849 and 15.1%. (b) Name two ways in which Moreira and Muir's managed portfolio differs from R8: it scales
  by the inverse of the previous calendar month's realized variance, not by a ratio of volatilities; its constant is
  set so that its full-sample volatility matches the unmanaged portfolio's, which uses the whole sample; its main
  results have no cap.
- §7: (a) The EWMA forecast had the lower QLIKE in 56 of 91 holding months, yet its mean QLIKE is the higher [A31-35].
  How? Its 56 wins gain 17.25 in all, 0.308 each on average; its 35 losses cost 26.37, 0.753 each. The net cost,
  9.12, spread over 91 holding months, is the gap in means, 0.100. One holding month, 2 April → 2 May 2025, costs
  13.3 by itself: the EWMA scored 27.50 against the window's 14.17. Without it the EWMA's mean is the lower, 0.494
  against 0.541. QLIKE punishes a forecast that is far too low, so one such holding month can decide the average.
  (b) Could a risk trigger have cut R8's exposure before the loss of 7 April 2025? No: a trigger acts only after a
  close, and the first close that showed the jump was 7 April's [A31-32]. A periodic rule waits for the next
  month-end; a trigger trades at the next close after its threshold is crossed.
- §8: Why does SciPy reject `squareform(D)` for a correlation distance built with `np.corrcoef`? The matrix is asymmetric at machine precision (nonzero, below $10^{-15}$), and its diagonal is not exactly 0.
  So `squareform`'s checks reject it on some of E5's windows [A31-19] (shared decision "Python"). Symmetrize it
  and set the diagonal to 0 first.

中文導讀 in §2 (風險貢獻 (risk contribution), 風險預算 (risk budget), 風險平價 (risk parity), 等風險貢獻 (equal risk
contribution); one sentence says that this 風險預算 is a budget per asset, while LM7's 風險預算 (lm07.md:354) capped the
total volatility of two strategies), §3 (嚴格凸函數 (strictly convex function), 唯一性 (uniqueness), 牛頓法 (Newton's method), 座標下降法
(coordinate descent), 不動點 (fixed point)), §4 (層次叢集法 (hierarchical clustering), 樹形圖 (dendrogram), 單一連接叢集法
(single linkage clustering), 歐氏距離 (Euclidean distance), 層次風險平價 (hierarchical risk parity)), §6 (波動率目標
(volatility targeting), 指數加權移動平均模型 (EWMA; LM26's form, lm26.md:132), 槓桿 (leverage), 曝險 (exposure)), §7 (再平衡 (rebalancing), the
difference between 定期再估計 (periodic re-estimation) and 風險觸發 (risk trigger), 門檻 (threshold)). Terms and listings
below, "Chinese terms". Deep Dive (§3): "Why the
minimizer exists": on $\mathbf y>\mathbf 0$, $\mathbf y^{\top}\Sigma\mathbf y$ is at least the smallest eigenvalue of
$\Sigma$ times $\lVert\mathbf y\rVert^2$ (11.4), and that eigenvalue is positive because $\Sigma$ is positive definite (the
bound is written in words: in LM31 $\lambda$ is only LM26's decay, AUTHORING §6's $\lambda$ row, and no eigenvalue
symbol is written). So
$h\to\infty$ as any $y_i\to0^+$ or $\lVert\mathbf y\rVert\to\infty$; a sublevel set is closed and bounded, and a continuous
function attains its minimum on it (the extreme value theorem, stated without proof as [[LM11]] states it for a closed and bounded set, lm11.md:249).

**Exhibits.**

Every exhibit's note ends with a `Source:` line (AUTHORING §8): X1's for X1, X2, X5, X7 and X8 (E5); for X3, X4
and X6 (U28), FinMind `TaiwanStockPrice`, retrieved 11 October 2026, with the repaired closes as lm10.md:41 states them.

- X1 `case` (table, §1): R6 on 31 March 2025: weights 13.5, 21.6, 30.7, 22.2, 12.0% (0050, 00646, 00679B, 00635U,
  00642U; one decimal, so that they sum to 100.0 as printed); $\bar\sigma_t$ 7.84%; EWMA 5.89%; $L$ 1.33 from 1 April; EWMA on 7 April 23.58%, implied exposure 0.33; next
  trade 2 May at 0.45 [A31-32]; R8's realized volatility over the holding month 45.3% against its 7.84% target, ratio
  5.78, the largest of 91 holding months; the median ratio over the 91 holding months 0.98 for R8, 0.83 for R6
  [A31-34]. Note: out of sample, fixed in advance on 24 October 2026. Window volatilities and the holding month's
  realized volatility are annualized with $A=242.95$, so that the ratio is the printed figures' (the ratio itself is
  taken in daily units). EWMA (26.2) with $\lambda=0.94$ on R6's constant-weight daily simple returns. The holding
  month runs from 2 April to 2 May 2025. Source: FinMind `TaiwanStockPrice`, `TaiwanStockDividendResult` and `TaiwanStockSplitPrice`, retrieved
  24 October 2026; Computations: `data/lm31_numbers.py` (through `data/vol5_rules.py`).
- X2 `shares` (`bar`, `stack: true`, approved C1, §2): eight categories, "R1 weights", "R1 risk", "IV weights", "IV
  risk", "R6 weights", "R6 risk", "R7 weights", "R7 risk"; five series, the funds: 0050 colour 1, 00646 colour 2,
  00679B colour 3, 00642U colour 4, 00635U `"var(--muted)"`, named in the caption; `y.fmt` `pct1`, `valueLabels`
  false (every bar totals 100% before rounding). Values cited: R1's 00642U share 50.2% (LM27's A27-21) [A31-12]; IV's
  shares 23.8, 23.0, 9.8, 18.7, 24.8% [A31-09]; R6 20% each [A31-10]; R7 13.0, 24.0, 26.3, 30.0, 6.6% [A31-11]. The
  caption says that the cited shares are rounded separately: IV's sum to 100.1 and R7's to 99.9 as printed. Note:
  first window, 504 estimation rows, 13 February 2017 → 27 February 2019; ex-ante shares on that window's
  $\hat\Sigma$; descriptive.
- X3 `u28corr` (`heatmap`, §4): U28's 28×28 correlation matrix in HRP's order, `min` 0, `max` 1 (all 378 correlations
  lie between 0.217 and 0.755 [A31-22]), `fmt` `n2`; the note lists the 28 sectors in order (labels drop out on a
  phone). Values cited: the first merge, ComputerPeripheralEquipment with ElectronicPartsComponents. Note: daily price
  returns, 2 December 2008 → 8 October 2026, $T=4{,}382$; descriptive; price indices, no dividends.
- X4 `u28tree` (`scatter`, dendrogram, §4): 27 merges as `lines` (three per merge), $y$ ticks 1–28 with `tickLabels` in
  HRP order, $x$ the column distance at each merge (0.501 to 0.743 [A31-22]); `equal` false; height about 420 px.
  Values cited: first merge 0.5012, root 0.7426; on the full sample HRP's weights run from 12.87%
  (CommunicationsInternet) to 1.29% (GlassCeramic) and ERC's from 6.06% to 2.43% (the same two sectors); in-sample
  volatilities ($A=245.48$) 1/N 15.75% (lm10.md:36), inverse volatility 15.28%, ERC 15.18%, HRP 14.48% [A31-22]. Note:
  single linkage on $\lVert\mathbf d_i-\mathbf d_j\rVert$; descriptive (in sample).
- X5 `rules` (table, §5): per fund, R6's and R7's mean (min–max) weight across the 92 signals [A31-24, A31-25]; R7's mean
  ex-ante share [A31-25]; R6's ex-post share (the mean of its 92 target weights on the out-of-sample covariance) and,
  over the holding months, the 10–90% range of the share that each holding month's own target weights carry on that
  holding month's covariance [A31-26]; the caption says that the columns are rounded separately (R7's mean
  shares sum to 1.001 as printed); last row, realized volatility 10.32% (R6), 10.14% (R7) [A31-27], beside LM30's R1
  12.48%, R3 9.96% and R5 9.97% (A30-12, echoed in A31-27). Note: out of sample, net of costs; daily returns 5 March
  2019 → 8 October 2026, annualized with $A_{\mathrm w}$. R1's 12.48% is this window's, not LM27's full-sample 11.49%
  for fixed weights (A27-13; decision C7). The ex-post shares use the 1,845 joint estimation rows of the same span.
- X6 `u28halves` (table, §5): inverse volatility, ERC, HRP: weights from the first half held constant, volatility in
  the first half and the second: 15.70/15.20, 15.57/15.11, 15.22/14.96% [A31-23]; beside them LM30's rows (A30-19,
  echoed in A31-23): 1/N 15.98/15.51, long-only minimum variance 12.74/12.14, sample minimum variance 11.40/11.78%.
  Values cited: on the second half HRP is the lowest of 1/N (LM30's) and LM31's three, and above both
  minimum-variance portfolios. Note: U28's
  halves (2,191 returns each, LM11's); one split fixed in advance; out of sample in the second column; price indices,
  covariance only.
- X7 `exposure` (`line`, dates, §6): $L_t$ at the 92 trade dates, `step: true`, `fmt` `n2`; dashed `hline`s at 1 and
  1.5 ("cap"); labelled points 4 March 2019 (0.85), 1 April 2020 (0.295, the minimum), 1 April 2025 (1.33)
  [A31-28, A31-29, A31-32]. Values cited: mean 1.14; at the cap at 14 of the 92 trades, above 1 at 62, below at 30;
  the uncapped ratio $\bar\sigma_t/\sigma_{t+1\mid t}$ reached 2.14 [A31-29]. Over the 92 signals $\bar\sigma_t$ ran
  from 5.37% to 11.24% a year (mean 9.42%) and the forecast from 3.66% (31 May 2019) to 31.48% (31 March 2020, whose
  trade set the minimum 0.295) [A31-30, A31-33]. Note: out of sample; $L_t$ is set at each trade and drifts between
  trades.
- X8 `target` (`line`, log $y$, §7): realized ÷ target volatility for R6 (colour 1) and R8 (colour 2) at the starts
  of the 91 holding months; dashed `hline` at 1; labelled points 3 March 2020 (R6 5.60, R8 4.90) and 2 April 2025 (R6
  4.25, R8 5.78) [A31-34]. Values cited: medians 0.83 and 0.98, SD of the logarithm 0.421 for both, 11 holding months
  above 1.5 for both, 21 and 13 below 2/3 [A31-34]. Note: the target is $\bar\sigma_t$ at each signal. Realized: the uncentred
  RMS of daily net returns from the session after a trade through the next trade (12–23 sessions), in daily units.
  The partial holding month to 8 October 2026 is left out. Out of sample.

**Widget `ercThree` — "Equal risk, or a budget, for three funds."** `Book.controls`: three volatility sliders (2–40%,
step 0.5), three correlation sliders (−0.9 to 0.9, step 0.05), and fund 1's budget $b_1$ (0.10–0.80, step 0.01; the
other two share $1-b_1$ equally). Code under 30 lines: a positive-definiteness check (Cholesky of the $3\times3$
matrix; if it fails, the chart says so and shows no solution), CCD (31.4) to $10^{-12}$ with at most 1,000 sweeps.
CCD rather than the spine's fixed-point iteration: at the widget's own initial state Jacobi's fixed point from 1/3
settles at $(-32.5,54.5,-20.9)$ (rounded separately; the printed entries sum to 1.1), every share a third but two
weights negative [A31-39] (accepted, decisions D and E). Chart: X2's stacked bars for 1/N, inverse volatility and the
budget portfolio (weights and risk shares, six categories, three series). Readouts: weights, risk shares, $\sigma_p$
of each, sweeps. Initial state (PDF): the first window's 0050, 00679B and 00642U (volatilities 13.5, 8.5, 23.2%,
LM28's A28-06; correlations −0.30, 0.20, −0.08 from A28-07's matrix, of which LM28 prints only the first; both at LM28's precision, decision C12),
$b_1=1/3$: ERC 0.3061, 0.5400, 0.1539 in 9 sweeps, $\sigma_p$ 6.55%; inverse volatility's shares 34.1, 23.6, 42.3%;
1/N's 25.7, 2.8, 71.5% [A31-39]. These readouts follow from the unrounded inputs, which the text says. Data block:
the initial values only, unrounded; the first draw uses them until a slider moves (the sliders show the nearest
step), so that the PDF's readouts are the anchor's (as LM28's widget, per-module decision on LM28). Test: `data/lm31_charts.py` runs the widget's function in Node (as
`data/lm15_charts.py` does) against `erc()` and the CCD of the anchors on the initial state and 500 random positive
definite matrices (experiment 1, `default_rng([1, 20261011])`), stopping on a difference above $10^{-9}$. No general-purpose
optimizer (CCD is module-local code under 30 lines, which decisions D and E accept), no simulation, no Student $t$ in
the browser (shared decision "Widgets").

**Examples** (results recomputed from the printed inputs):

- E1 §2 `twofunds`: 0050 and 00679B on the first window, volatilities 13.50% and 8.54% (LM28's A28-06, which prints
  one decimal; the weights below need two, decision C12), $\rho=-0.30$ (A28-07) [A31-07]. Equal contributions (31.1)
  mean $w_1^2\sigma_1^2+w_1w_2\sigma_{12}=w_2^2\sigma_2^2+w_1w_2\sigma_{12}$, so $w_1\sigma_1=w_2\sigma_2$ whatever
  $\rho$: weights 0.3875 and 0.6125, risk 50/50. (7.7)'s minimum variance puts
  0.331 in 0050, at 6.1% against ERC's 6.2% [A31-07]. With two funds ERC ignores the correlation; with five it does
  not (E2).
- E2 §2 `firstshares`: five funds, first window: volatilities 13.50, 11.87, 8.54, 9.39 and 23.17% (LM28's A28-06, at
  the two decimals the weights below need, decision C12) and correlations from LM28's A28-07 [A31-06]; the risk shares
  and volatilities come from the window's unrounded $\hat\Sigma$, and the text says so.
  Inverse-volatility weights 0.174, 0.198, 0.275, 0.251, 0.102 leave 00679B only 9.8% of the risk and 00642U 24.8%,
  because 00679B correlates −0.30 and −0.26 with the equity funds (A28-07) [A31-09]. R6 (0.1561, 0.1828, 0.3386,
  0.2372, 0.0854; rounded separately, these sum to 1.0001 as printed) gives each 20% [A31-10]. Volatilities 5.02% (R3,
  the long-only minimum variance, here equal to (28.2)'s $\mathbf w^{\mathrm{mv}}$ because every weight is positive;
  LM28's A28-10) $\le$ 5.45% (R6) $\le$ 7.38% (R1; LM28's A28-15) [A31-12], as Maillard et al.'s ordering says. With every
  correlation set to the mean 0.0533, ERC equals inverse volatility [A31-08].
- E3 §3 `solvers`: R6's first weights four ways [A31-14]. Newton from `erc()`'s start, $y_i=1/\sigma_i$ rescaled so that $\mathbf y^{\top}\Sigma\mathbf y=1/N$: 6 steps. CCD: 12 sweeps,
  within $3.5\times10^{-13}$ of Newton. cvxpy's log form (CLARABEL with `tol_gap_abs`, `tol_gap_rel`, `tol_feas`
  $10^{-10}$, a cone program): within $1.2\times10^{-6}$ over the 92 windows, inside the conic cross-check's stated
  tolerance $10^{-5}$ (decision C5). Jacobi's fixed point from 1/N, stopped when no weight moves by $10^{-12}$ or more
  in a step, settles after 220 steps at $(-1.307,-1.306,2.132,2.408,-0.927)$: every share is 20%, yet three weights
  are negative, so it solves (31.1) outside the long-only set; at 45 of 92 windows it does not settle in 10,000
  steps. The weights are the same on daily or annualized $\hat\Sigma$ [A31-15].
- E4 §3 `budgets`: R2's mix as risk budgets on the four funds it holds (0.4, 0.2, 0.3, 0.1; 00642U's zero weight cannot
  be a budget). CCD gives weights 0.2466, 0.1773, 0.4190, 0.1571 in 12 sweeps (cvxpy within $4.4\times10^{-7}$)
  [A31-16]. R2 itself puts 71.1% of its risk in 0050 (LM31's, decision A4's exception). Volatilities: the four funds'
  long-only minimum variance 5.016% (not R3's 5.02%, LM28's A28-10, which holds all five) $\le$ budgets 5.326% $\le$
  R2 6.709% (LM30's A30-24, printed there to three decimals) (Bruder and Roncalli's ordering, §2.3.4). A 40% risk
  budget for 0050 is a 24.7% weight.
- E5 §4 `hrp3`: three funds by hand [A31-17]. $\rho$ 0.54, −0.30, −0.26 (LM28's A28-07, two decimals) give $d$
  0.480, 0.806, 0.794; from there three decimals throughout, so that each step follows from the one printed before
  it: column distances 0.679 (0050, 00646), 1.182, 1.169. 0050 and 00646 merge at 0.679; 00679B joins at
  $\min(1.182,1.169)=1.169$. Order (00679B, 0050, 00646). First cut [00679B] | [0050, 00646]: inverse-variance
  variances 72.96 and 121.95 (%² a year), so 00679B takes $121.95/(72.96+121.95)=0.6257$. Second cut: 0050's 182.29
  against 00646's 140.88, so 0050 takes 0.4359 of 0.3743. Weights 0.1632, 0.2111, 0.6257. The variances come from the
  window's unrounded $\hat\Sigma$ (squaring E1's 13.50% and 8.54% would give 182.25 and 72.93), and the text says
  so.
- E6 §4 `hrp5`: R7's first weights [A31-18]. Merges: 0050 + 00646 at 0.6835, then 00642U at 0.8576, 00679B + 00635U at
  0.8861, root 0.9822. Order (00642U, 0050, 00646, 00679B, 00635U). The first cut takes the first two items,
  [00642U, 0050] | [00646, 00679B, 00635U], with left share 0.1516: it separates 0050 from 00646, the tree's first
  pair. Weights 0.1131, 0.2189, 0.3443, 0.2852, 0.0384, risk shares 13.0, 24.0, 26.3, 30.0, 6.6% (each list rounded
  separately; they sum to 0.9999 and 99.9 as printed); volatility on the window 5.13% [A31-11, A31-18].
- E7 §5 `expost`: what R6's equal shares became [A31-26]. The mean of R6's 92 target weights (A31-24), on the
  covariance of the 1,845 joint out-of-sample dates, carries 20.5, 19.2, 19.2, 23.1 and 18.0% of the risk. Holding
  month by holding month, each holding month's own target weights, on that holding month's covariance, give 00635U
  a share from 8.7% to 47.0% (10% and 90% quantiles) and 00679B one from −0.9% to 41.1%; some share is negative in
  29 of 91 holding months. Equal risk is an ex-ante statement about $\hat\Sigma$.
- E8 §6 `r8first`: R8 at the first signal by hand [A31-28]. $\bar\sigma_t=0.0034991$ a day (5.45% a year), the EWMA
  0.0041204 (6.42%), so $L=0.0034991/0.0041204=0.8492$; exposures 0.8492 × R6 = 0.1326, 0.1552, 0.2875, 0.2014, 0.0725;
  cash 0.151 at 1.5%. The start value's weight after 504 days is $0.94^{504}=2.9\times10^{-14}$ [A31-38]. Harvey et al.
  scale to a fixed 10% target, with a zero-mean EWMA of half-life 20 days, $\lambda=0.5^{1/20}=0.9659$ [A31-38]; R8
  targets $\bar\sigma_t$, and its EWMA's half-life is 11.2 days.
- E9 §7 `april2025` (the case): signal 31 March 2025, $\bar\sigma_t$ 7.84%, EWMA 5.89%, $L$ 1.33 [A31-32]. Continued
  daily on R6's constant-weight returns, the EWMA reads 6.34% on 2 April and 23.58% on 7 April, an exposure of 0.33;
  R8 trades next on 2 May, at 0.452 [A31-32]. Over the holding month 2 April → 2 May its realized volatility, 45.3%
  (annualized with the target's $A$), is 5.78 times the target; R6's is 4.25 times [A31-34]. A risk trigger could act
  only after a close: the first close that showed the jump was 7 April's, after the day's loss [A31-32]. In the
  holding month from 3 March 2020 R8 entered at 0.884 and its ratio, 4.90, was below R6's 5.60 [A31-33, A31-34]. Each
  trade moved R8's exposures by 9.2% one way on average over the 91 trades after the first purchase; the largest,
  45.2%, was the 2 May 2025 cut to 0.452 [A31-36]. R8's annual turnover is LM34's (A34-06), not printed here.
- E10 §7 `judge`: the 91 holding months [A31-34, A31-35]. Ratios: median 0.83 (R6) and 0.98 (R8); SD of the logarithm
  0.421 and 0.421; above 1.5: 11 and 11; below 2/3: 21 and 13. Over the whole period R8's realized volatility was
  11.52% against R6's 10.32% [A31-27]. QLIKE of R6's holding month: mean 0.691 for the window and 0.791 for the EWMA;
  medians 0.165 and 0.087. The EWMA is lower in 56 holding months, which gain 17.25 in all, and higher in 35, which cost
  26.37. Its two largest QLIKE values are 27.50 (2 April → 2 May 2025; the window's 14.17), its largest loss, by
  13.3, and 20.33 (3 March → 1 April 2020; the window's 26.96), its largest win, by 6.63. Without the 2025 holding
  month the means are 0.541 (window) and 0.494 (EWMA); without both crash holding months 0.244 and 0.271. R8 moved the
  typical holding month to its target; it did not narrow the spread.

**Problems plan** (12; MC keys B, A, C, A, B; the lab solves 6, 8, 11, 12). Stems state long-only weights, risk shares
as $\mathrm{RC}_i/\sigma_p$, annual volatilities, the rounding; backtest stems (10) state E5's first signal, the
504-row window, a trade at the next close after each month-end, the costs (LM34's model, by pointer), the 91 complete holding months
and the label *Out-of-sample*. Problem 2 asks for a budget, not a contribution, so that it does not repeat LM27's
problem 4 (the first cross-check's item X5).

1. MC: two funds, volatilities 20% and 10%, $\rho=0.5$; the ERC weight of the first. A 0.200 (inverse variance). **B**
   0.333. C 0.500 (equal weights) [A31-40].
2. MC: the same funds; for which budget $b_1$ is 50/50 the risk-budget portfolio (31.1)? **A** 0.714 (fund 1's share
   of $\sigma_p$ at 50/50, by (27.6)). B 0.667 (stand-alone $w_i\sigma_i$ over their sum). C 0.800 (variance terms
   only) [A31-41].
3. MC: volatilities 10, 20, 40%, every correlation 0.3; the ERC weight of the 40% fund. A 0.048 (inverse variance). B
   0.333. **C** 0.143 [A31-42].
4. Prove theorem (31.2): $h$ strictly convex on $\mathbf y>\mathbf 0$ for positive definite $\Sigma$ ((29.2)), so it
   has at most one minimizer ((29.3)), and one exists (the Deep Dive's argument, which the solution cites); its first-order
   condition $y_i(\Sigma\mathbf y)_i=b_i$; $\mathbf w=\mathbf y/\mathbf 1^{\top}\mathbf y$ satisfies (31.1); any long-only
   solution of (31.1) rescales to the minimizer. Then explain why E3's Jacobi point, with equal shares, does not
   contradict uniqueness.
5. Two funds, $\rho=0$, volatilities 20% and 10%, budgets 0.7 and 0.3: show $w_i\propto\sqrt{b_i}/\sigma_i$, compute
   $w_1=0.4330$ and check the shares; show that CCD reaches it in one sweep when $\rho=0$ [A31-43].
6. HRP by hand (constructed): $\rho_{12}=0.8$, $\rho_{13}=0.1$, $\rho_{23}=0.2$, volatilities 20, 25, 10%, with Section 4's ordering rule (lower number first, the first cluster numbered 4) and the first half of $\lfloor n/2\rfloor$ items, both stated in the stem: $d$ 0.3162,
   0.6708, 0.6325; column distances (from the unrounded $d$, which the stem's exact $\rho$ give) 0.4489, 1.0000,
   0.9622; merges 0.4489, 0.9622; order (3, 1, 2); weights 0.1141, 0.0730, 0.8128 (rounded separately; they sum to
   0.9999 as printed, and the solution says so) [A31-44]. Python part: check with SciPy.
7. MC: single linkage on LM8's $\sqrt{2(1-\rho)}$ instead of $d_{ij}$ gives: **A** the same tree, heights doubled. B
   a different tree. C the same tree and heights [A31-21].
8. R8 by hand: $\bar\sigma_t=8\%$, forecasts 5% and 16% a year: $L$ 1.5 (uncapped 1.6) and 0.5; the next day the funds'
   book returns −3%; cash 1.5% and borrowing 3.5% a year accrue over $A_{\mathrm w}=243.57$ sessions: book returns
   −4.5072% and −1.4969% [A31-45]; why the cap binds.
9. Show (31.8)'s identity: if $\mathbf w^{\top}\Sigma_{\text{start}}\mathbf w=\bar\sigma^2$, then $\mathbf w^{\top}
   \Sigma_{t+1\mid t}\mathbf w$ is the EWMA of $(\mathbf w^{\top}\mathbf R_t)^2$; show $\Sigma_{t+1\mid t}$ is positive
   semidefinite, $\mathbf a^{\top}\Sigma_{t+1\mid t}\mathbf a=\lambda\,\mathbf a^{\top}\Sigma_{t\mid t-1}\mathbf a+(1-\lambda)(\mathbf a^{\top}\mathbf R_t)^2\ge0$, by induction from a positive semidefinite start (the argument of (16.4)); and why the start matters little after 504 days ($2.9\times10^{-14}$ [A31-38]).
10. MC: over 91 holding months (the stem gives the window, the timing, the costs, *Out-of-sample*), R8's realized ÷ target
    ratio has median 0.98 and SD of its logarithm 0.421; R6's 0.83 and 0.421. Which is supported? A targeting halved
    the spread across holding months (and the equal shares held). **B** targeting moved the typical holding month to
    its target but left the spread unchanged. C the EWMA forecast beat the window in every holding month [A31-34,
    A31-35].
11. Python: R6's first weights by CCD and by Newton, checked with cvxpy and by their shares; then Jacobi from 1/N and
    its non-long-only point (first window, 504 rows, annualized $\hat\Sigma$; $\mathbf y>\mathbf 0$; CCD from $y_i=1/\sigma_i$
    until $\max_i\lvert y_i(\Sigma\mathbf y)_i-1/5\rvert<10^{-12}$, Newton from `erc()`'s start until it is below $10^{-13}$;
    cvxpy with CLARABEL at `tol_gap_abs`, `tol_gap_rel`, `tol_feas` $10^{-10}$, status `optimal`, agreeing to $10^{-5}$;
    Jacobi stopped when no weight moves by $10^{-12}$, at most 10,000 steps; weights to four decimals) [A31-10, A31-14].
12. Python: R7's first weights with SciPy, by the column distance and by $d$ directly; count the signals where the leaf
    order differs (17 of 92), over the 92 month-end signals from 27 February 2019 to 30 September 2026, each on its
    trailing 504 estimation rows [A31-18, A31-20].

**Lab parts** (`build/make_lab31.py`; reads only its `data/`: E5's estimation frame and its wealth frame with the
traded flags (decisions on the first revision, "Labs"), the rules' per-date
targets and exposures, the eight rules' net and gross wealth paths (shared decision "Labs", decision C6), and
`sectors_close_raw.csv` with
`sectors_close_repairs.csv` for U28, as LM23's lab builds them; all from `data/make_lab_data.py`): 1 data, $T$, $A$,
$A_{\mathrm w}$, the schedule, the first window; 2 risk contributions, E1, E2, X2, equal correlations; 3 ERC and budgets:
Newton, CCD, Jacobi, cvxpy (E3, E4, problem 11); 4 HRP by hand (E5, E6), the author's code and its `ClusterWarning`,
linking on $d$ across 92 signals, then R7 re-implemented at every signal and checked against the derived weights to
$10^{-12}$ (problem 12); 5 U28: X3, X4, X6; 6 R8 re-implemented at every signal and checked; the EWMA matrix identity;
X7, E8; 7 X8, QLIKE, E9, E10; 8 the risk-triggered variant (*In-sample* illustration; rule and threshold fixed by the
editor on 2026-10-24, before any lab result, decision D: after each close, update the EWMA of R6's drifted book; when
the implied exposure differs from the held one by more than 0.5, trade to it at the next session's close with the
through case's costs; count the trades and compare the holding months' ratios; a closing sentence says that choosing
the threshold is LM34's search); 9 problems 6 and 8. Extension (lm26.md:183): replace the
EWMA by a GARCH(1,1) fit on each window (`arch`, LM26's settings) and its average forecast over the next 21 sessions (a fixed horizon near a holding month's 12–23 sessions, A31-04, set before any lab result) by
(26.4); compare QLIKE with the window's and the EWMA's; label it one more variant. Labs write plain "LM33", "LM34",
never `[[LM34]]`.

**Cross-module tags** (each with the later briefs that cite it by number, decision C8; the others are numbered because
LM31 itself refers to them).

- (31.1) Risk-budget conditions $w_i(\Sigma\mathbf w)_i=b_i\,\mathbf w^{\top}\Sigma\mathbf w$, i.e. $\mathrm{RC}_i=b_i\sigma_p$,
  for $\mathbf 1^{\top}\mathbf w=1$ and budgets $b_i>0$, $\sum_ib_i=1$; the risk-budget portfolio is their long-only solution ($\mathbf w\ge\mathbf 0$, hence $\mathbf w>\mathbf 0$; (31.2)); ERC is $b_i=1/N$ (LM35, for R6;
  LM32–LM34 cite R6 by name).
- (31.2) Theorem: for positive definite $\Sigma$ and positive budgets, $h(\mathbf y)=\tfrac12\mathbf y^{\top}\Sigma\mathbf y-
  \sum_ib_i\ln y_i$ has one minimizer on $\mathbf y>\mathbf 0$, and $\mathbf y^*/\mathbf 1^{\top}\mathbf y^*$ is the only
  long-only solution of (31.1) (in-module).
- (31.3) $w_i=\sigma_i^{-1}/\sum_j\sigma_j^{-1}$ is ERC for two assets (any $\rho>-1$; at $\rho=-1$ its $\sigma_p$ is 0) and for equal
  correlations $-1/(N-1)<\rho<1$, the only long-only ERC portfolio there by (31.2) (in-module).
- (31.4) CCD: $y_i\leftarrow\big(-a_i+\sqrt{a_i^2+4\sigma_i^2b_i}\big)/(2\sigma_i^2)$ with $a_i:=(\Sigma\mathbf y)_i-
  \sigma_i^2y_i$ written out in the text, not as a symbol (in-module, lab); the brief's $a_i$ is a placeholder.
- (31.5) $d_{ij}=\sqrt{(1-\rho_{ij})/2}$, half of (8.10)'s per-date distance; the column distance
  $\lVert\mathbf d_i-\mathbf d_j\rVert$ (in-module, lab).
- (31.6) Bisection: the halves of the ordered list receive $\sigma^2_{(2)}/(\sigma^2_{(1)}+\sigma^2_{(2)})$ and
  $\sigma^2_{(1)}/(\sigma^2_{(1)}+\sigma^2_{(2)})$ of the parent's weight (in-module).
- (31.7) R8: $L_t=\min\big(1.5,\ \bar\sigma_t/\sigma_{t+1\mid t}\big)$, $\bar\sigma_t^2$ the window's uncentred mean square of
  R6's book, $\sigma^2_{t+1\mid t}$ (26.2) on it from $\bar\sigma_t^2$; exposures $L_t\mathbf w_t^{\text{R6}}$, cash
  $1-L_t$ at $r_f$, borrowing at $r_f+2$ points, booked by (27.1)–(27.2) (LM32, LM33, LM34, LM35).
- (31.8) $\Sigma_{t+1\mid t}=\lambda\Sigma_{t\mid t-1}+(1-\lambda)\mathbf R_t\mathbf R_t^{\top}$, positive semidefinite, and
  $\mathbf w^{\top}\Sigma_{t+1\mid t}\mathbf w$ equals the EWMA of $(\mathbf w^{\top}\mathbf R_t)^2$ from matching starts
  (in-module; LM30 points to it in words; no later brief cites it).

Tags of earlier briefs that LM31 cites by number: (27.1)–(27.3), (27.5)–(27.6), whose lists in LM27's brief name
LM31; (28.2), (29.2), (29.3) and (29.5), which the cross-check's tag-user table (Y1) adds LM31 to, and which LM28's and
LM29's briefs take from that table (decision "Tags and leads"). LM31's own lists were checked against the revised
LM32–LM35 briefs and the same table: (31.1) is cited by LM35, (31.7) by LM32, LM33, LM34 and LM35, (31.8) by none.

**Pitfalls to pre-empt.**

- A risk share is not a weight (E2, E4) and not a share of losses; the gradient entry $(\Sigma\mathbf w)_i$ is a rate,
  the share is $w_i$ times it over $\sigma_p^2$ (lm10.md:425). Ex post a share can be negative: each holding month's
  own target weights, on that holding month's covariance, give some fund a negative share in 29 of 91 holding months.
- Uniqueness holds only for long-only weights and positive budgets: Jacobi's point satisfies (31.1) with negative
  weights; a zero budget is not allowed (drop the fund).
- A fixed point is not an algorithm: $w_i\propto b_i/\beta_{i,p}$ need not settle (45 of 92 windows). CCD and Newton
  descend a strictly convex $h$. Check any answer by its risk shares, not by the solver's status alone.
- ERC and HRP weights are scale-free, but solvers are not: annualize for cvxpy (shared decision "Solver output").
- HRP: the column distance, not $d$ itself; the author's code gets it by passing the square matrix to SciPy, which
  reads rows as observations and warns, and so builds the column-distance tree at all 92 windows and on U28
  [A31-19]; symmetrize `np.corrcoef` and zero the diagonal before `squareform`; the
  bisection halves the ordered list and can split the tree's closest pair (E6); single-linkage trees change with small
  changes in correlations.
- The factor 2 to LM8's distance changes no tree (A31-21); say so where (8.10) is cited.
- (26.2) in LM26 is written for log returns; R8 applies it to the book's simple daily returns in decimals, uncentred,
  from the start $\bar\sigma_t^2$. Say so once.
- R8 targets R6's own volatility over the trailing 504 joint dates, not a fixed level; the cap binds at 14 of 92 signals
  [A31-29]; cash earns 1.5% and borrowing costs 3.5%; check $1+R_t>0$ on every date [A31-37], and leave the worst day
  to LM35.
- A one-day EWMA forecast is also its forecast for every later day (lm26.md:142); a month-end rule meets a gap with
  the exposure set at the last month-end (E9). A risk trigger reacts after the day's loss, not before it.
- Holding-month ratios: uncentred RMS against the uncentred $\bar\sigma_t$; daily units on both sides (an annual
  figure printed beside a ratio uses the target's $A$ for both); the partial last holding month left out; 91 holding
  months is a short record for comparing spreads.
- Ownership (decisions A1–A6): R1's first-window shares are LM27's (A4's carve-out); the first window's fund
  statistics, R1's first-window volatility and R3's weights LM28's, echoed at LM28's precision unless a computation
  beside them needs more (C12); R2's first-window shares LM31's and its first-window volatility LM30's (A4's
  exceptions); R1/R3/R5's realized volatility and 1/N and minimum variance on U28's halves LM30's; Sharpe ratios
  LM33's; VaR and drawdowns LM32's; annual turnover and costs LM34's; each rule's loss on 7 April 2025 and crash losses
  LM35's.
- The evidence: Moreira and Muir scale factor returns monthly by the inverse of the previous calendar month's
  realized variance, with a constant set on the full sample (1926–2015 for the market, size, value and momentum,
  later starts for the others; caps of 1 and 1.5 only as robustness checks). Harvey et al., on more than 60 assets,
  find that the Sharpe ratio improves slightly for equity indexes and credit and hardly changes for bonds, currencies
  and commodities, while the vol of vol and the left tail improve for almost all of their futures, forwards and
  credit (for US 10-year Treasury futures the left tail is similar). Neither tests E5's funds; do not carry their Sharpe
  ratios over.
- References: Maillard et al. read in their May 2009 working paper and López de Prado in SSRN 2708678 (23 May 2016),
  so the text cites both JPM articles without a JPM page or equation number; Bruder and Roncalli in their March 2012
  working paper, with its section, equation and page numbers; Harvey et al. in the complete journal reprint, with its
  pages; Moreira and Muir cited as the JF article, its design read in NBER WP 22208 and the authors' 25 October 2016
  draft, so the text prints no JF page or equation number (see "Sources"; decision F and the second hunt).

**Curriculum guidance carried** (`plans/vol-5.md`'s table; `plans/curriculum-guidance.md`):

- g:30, capability layer: §1's first paragraph says what LM31 adds: weights from risk alone (no means), then a book
  scaled by a forecast.
- g:54–58, outcome levels: [D] for (31.1)–(31.3) and the theorem, [C] for the algorithms, HRP and R8, [U] for what the
  rules assume and the evidence.
- g:69–85, decision flow (LM31's part): data visible at decision time (the 504 rows through the signal; the trade at
  the next close); the target from the estimate ($L_t$ from $\bar\sigma_t$ and the EWMA); trades from current holdings
  and cash and financing in the wealth recursion (LM27's, with R8's cash and borrowing); periodic re-estimation against
  a risk trigger kept apart and named (§7, E9; the trigger in the lab).
- g:87–90, failure forms: LM31 shows R8's exposure path and its levered entry into April 2025; funding, ruin and the
  worst day are LM35's.
- g:94, wealth ≤ 0: the domain check for the levered R8 (A31-37); no truncation.
- g:111, fixed in advance: R6–R8's window, frequency, cap, rates and criteria were fixed on 2026-10-24; the lab's
  trigger threshold, 0.5, was fixed by the editor the same day, before the lab is run (decision D).
- g:113, fixed positions against volatility targeting: §7 compares R8 with the unscaled R6; the comparison with R1 and
  R2 is LM33's and LM34's; Kelly-type sizing is Volume VIII's.
- g:116, "data too thin to support more leverage": §7 concludes that on E5 the forecast that drives R8's leverage did
  not narrow the spread of risk across holding months, so the data do not support levering R6 to 1.5.
- g:124, taught, practised, assessed: the map under "Outcomes".
- g:60–63, density: R7 at every signal, the trigger and the GARCH variant go to the lab; the Ledoit–Wolf-style depth
  of convergence proofs stays *stated*.

**Stage 4 for earlier modules.**

- `leads` gain 31 in lm07.md:6 and lm11.md:6 ((11.3) and the equal-correlation eigenvalues); both are on decision G's
  merged list (lm07 +30, +31; lm11 +29, +31, +34). lm08, lm10, lm16 and lm26 already list 31.
- lm08.md:290 (optional, decision G): "[[LM31]] groups assets by this distance" → "[[LM31]] builds a tree of assets
  from half this distance", since HRP clusters on the column distance of $d$, not on $\sqrt{2(1-\rho)}$ itself.
- `src/syllabus.yaml` (decision G, LM31's wording): LM31's line reads "Risk budgets from LM27's contributions, HRP's
  tree, and volatility targeting."
- No other wording change: lm26.md:183's "such a forecast" covers the EWMA as well as GARCH.

**Sources** (each read on 2026-10-24 in the version named; bibliographic data from Crossref, queried anonymously,
unless another record is named; paraphrased, nothing quoted beyond a phrase; the text prints only the claims listed
here, at these locations, and keeps out what an entry says to keep out):

- Maillard, S., T. Roncalli and J. Teïletche (2010). "The Properties of Equally Weighted Risk Contribution Portfolios."
  *Journal of Portfolio Management* 36 (4): 60–70. DOI 10.3905/jpm.2010.36.4.060 (Crossref: print and online 31 July
  2010). The JPM text could not be obtained (OpenAlex marks it closed; SSRN 1271972 refuses automated access), so the
  text cites the article as a whole and prints no JPM page or equation number. Read by the survey, the drafter and the
  second hunt in the authors' working paper "On the properties of equally-weighted risk contributions portfolios"
  (first version June 2008, this version May 2009; thierry-roncalli.com/download/erc.pdf, 23 pages; its title differs
  from the journal's). Locations in that version: §2.1, p. 4, the marginal contribution $\partial\sigma/\partial x_i$
  and the total contribution $x_i\,\partial\sigma/\partial x_i$, which sum to $\sigma$ by Euler's theorem for a
  function homogeneous of degree 1 (the second footnote numbered 1 on p. 4); (1)–(2), pp. 4–5, the ERC conditions with
  weights in $[0,1]^n$; §3.1, p. 5, the two-asset solution $\sigma_1^{-1}/(\sigma_1^{-1}+\sigma_2^{-1})$, which does
  not depend on $\rho$; §3.2, p. 5, inverse volatility under a constant correlation (footnote 3 allows
  $\rho\ge-1/(n-1)$; (31.3)'s strict bounds are the positive definite case); §3.3, p. 7, uniqueness for a positive
  definite covariance (an informal argument, so LM31 derives (31.2) in full); §3.4, p. 8, minimum variance equalizes the
  marginal contributions and ERC the total ones; p. 9 and Appendix A.3, p. 22, $\sigma_{\mathrm{mv}}\le\sigma_{\mathrm{erc}}\le\sigma_{1/n}$, proved
  with program (8) under a budget constraint and non-negative weights, so their minimum variance is the long-only one
  (the text says so). Not used: Appendix A.1 (ERC equals minimum variance at the lowest constant correlation).
- Bruder, B. and T. Roncalli (2012). "Managing Risk Exposures Using the Risk Budgeting Approach." SSRN working paper
  2009778, DOI 10.2139/ssrn.2009778 (Crossref: posted content, 2012; the title page writes "using" in lower case).
  Read by the drafter in the author-hosted copy (thierry-roncalli.com, `download/risk-budgeting.pdf`) and by the
  source check in the version whose title page reads "First version: January 2012 – This version: March 2012" (the
  source check calls it the SSRN version; its saved file bears the author-hosted copy's name). Locations in that
  version: Definition (3), p. 5 (weights in $[0,1]^n$; budgets strictly positive, summing to 1); §2.2, pp. 4–5 (a zero
  budget can give several solutions, as budgets (50%, 50%, 0%) do, hence
  $b_i>0$); eq. (7), p. 9 (weights proportional to $b_i/\beta_i$); §2.3.3, pp. 9–10 (existence and uniqueness for a
  positive definite covariance from the log-barrier program (9), footnote 13 on $b_i>0$; a short argument, not a
  formal theorem, so LM31 derives (31.2) in full); §2.3.4, p. 10 ($\sigma_{\mathrm{mv}}\le\sigma_{\mathrm{rb}}\le
  \sigma_{\mathrm{wb}}$, proved in Appendix A.3). LM31's source for unequal budgets (shared decision "References").
  Whether a journal version exists was not checked; the text cites the working paper.
- Griveau-Billion, T., J.-C. Richard and T. Roncalli (2013). "A Fast Algorithm for Computing High-dimensional Risk
  Parity Portfolios." arXiv:1311.4057 (v1, 16 November 2013, the arXiv record; the PDF is dated September 2013); also
  SSRN 2325255, DOI 10.2139/ssrn.2325255 (Crossref types it as a 2013 article in "SSRN Electronic Journal", writes
  "High-Dimensional" and misspells the first author's given name). Read in the arXiv version: the budget definition
  (citing Roncalli 2013), the CCD update, eq. (4), convergence by Tseng (2001, Theorem 5.1; their Remark 2), positive
  budgets (Remark 3), and the appendix's account of Chaves et al.'s fixed point and Newton method and of Spinu's
  Newton method. A preprint; no journal version was checked. Used for (31.4) and the widget, and as the route to
  Chaves et al. and Tseng.
- Chaves, D., J. Hsu, F. Li and O. Shakernia (2012). "Efficient Algorithms for Computing Risk Parity Portfolio
  Weights." *Journal of Investing* 21 (3): 150–163. DOI 10.3905/joi.2012.21.3.150 (Crossref: print and online 31
  August 2012; Crossref's title runs "RiskParity" together). Text not read: the text names the fixed point as
  Griveau-Billion et al. describe it.
- Tseng, P. (2001). "Convergence of a Block Coordinate Descent Method for Nondifferentiable Minimization." *Journal of
  Optimization Theory and Applications* 109 (3): 475–494, June 2001. DOI 10.1023/A:1017501703105. Text not read:
  cited as Griveau-Billion et al. cite it (Theorem 5.1), so CCD's convergence is *stated without proof*.
- López de Prado, M. (2016). "Building Diversified Portfolios that Outperform Out of Sample." *Journal of Portfolio
  Management* 42 (4): 59–69. DOI 10.3905/jpm.2016.42.4.059 (Crossref: print 31 May 2016, online 31 July 2016). The JPM
  body was not read (the publisher's page asks for a login), so the text cites the article as a whole and prints no
  JPM page. Abstract (OpenAlex's copy): HRP addresses the instability, concentration and underperformance of quadratic
  optimizers, needs no invertible covariance matrix, and in Monte Carlo experiments gives a lower out-of-sample
  variance than the critical line algorithm. Read in SSRN 2708678, "This version: May 23, 2016" (SSRN's own file,
  stamped on every page, from a third-party mirror because SSRN refuses automated access; byte-identical to the
  drafter's copy; Crossref records DOI 10.2139/ssrn.2708678 as posted content dated 2019, titled "… Out-of-Sample"),
  and in the author's `HRP.py` (header 2015-12-27). Locations in the SSRN version: the distance
  $\sqrt{\tfrac12(1-\rho)}$, Stage 1, p. 5, a proper metric by Appendix A.1, p. 13; the column distance, the Euclidean
  distance between columns of the distance matrix, p. 5, with Examples 1–2 (0.5659, 0.9747, 1.1225, which the script
  reproduces [A31-46]); single linkage, the nearest point algorithm of Example 4, p. 6; quasi-diagonalization, Stage
  2, p. 7; recursive bisection, Stage 3, p. 8 (the ordered list is halved, the first half taking the integer part of
  half its length; each half's variance uses inverse-variance weights; the first half's weights are scaled by the
  second half's share of the two variances); inverse variance optimal for a diagonal covariance, Appendix A.2, pp.
  13–14; p. 11, stage 3 could instead split top-down along the clusters of stage 1 (the source for leaving
  tree-following splits out); no inverse needed, the abstract (p. 2) and p. 5; the Monte Carlo design, p. 10 (10
  series of Gaussian returns with 520 observations, a 260-observation look-back, re-estimated and rebalanced every 22
  observations, 10,000 runs); the author's code passes the square distance matrix to SciPy's `linkage`, Appendix A.3
  and `HRP.py` lines 90–91.
- Moreira, A. and T. Muir (2017). "Volatility-Managed Portfolios." *Journal of Finance* 72 (4): 1611–1644, August 2017
  (online 15 May 2017). DOI 10.1111/jofi.12513. Abstract (Crossref's copy): managed portfolios that take less risk
  when volatility is high raise Sharpe ratios, because changes in volatility are not offset by proportional changes in
  expected returns. The JF text could not be read (the publisher answers every client with a challenge page). Read:
  NBER Working Paper 22208, by the drafter (April 2016) and by the source check (the revision of June 2016), DOI
  10.3386/w22208 (Crossref: report, April 2016, titled "Volatility Managed Portfolios"); and, by the source check, the
  authors' draft of 25 October 2016, which thanks the editor and two referees. The two agree on every design fact:
  eq. (1) scales the factor's next-month return by $c$ over the previous calendar month's realized variance, which eq. (2)
  computes from that month's daily returns (22 days); $c$ makes the managed portfolio's unconditional standard
  deviation equal buy-and-hold's, is computed on the full sample and does not change the Sharpe ratio (footnote 5);
  samples (Table I's note) 1926–2015 for the market, SMB, HML and momentum, 1963–2015 for RMW and CMA, 1967–2015 for
  ROE and IA, 1983–2015 for the FX carry factor; leverage caps of 1 and 1.5 only as robustness checks, none in the
  main results. Equation, footnote and table numbers are those versions'; the text cites the JF article, names the
  two versions read, calls the month a calendar month (decision C7), and prints no JF page or equation number.
- Harvey, C. R., E. Hoyle, R. Korgaonkar, S. Rattray, M. Sargaison and O. Van Hemert (2018). "The Impact of Volatility
  Targeting." *Journal of Portfolio Management* 45 (1): 14–33. DOI 10.3905/jpm.2018.45.1.014 (Crossref: print 31
  October 2018, online 1 November 2018; Crossref files the last author as "Hemert, Otto Van"). Read by the second hunt
  in the complete journal reprint (cover and pp. 14–33, people.duke.edu/~charvey, the server's date 1 November 2018);
  the drafter's saved copy was damaged. Locations (journal pages): more than 60 assets, with daily data beginning as
  early as 1926 (p. 14; "60+ assets", pp. 14 and 31); volatility as the zero-mean, exponentially weighted standard
  deviation of daily returns (p. 16, footnote 8), with a 20-day half-life by default and 10 to 90 days compared for US
  equities (Exhibit 5, p. 20); returns scaled by the 10% target over the estimate from returns up to $t-2$, with a
  constant chosen after the fact so that the target is realized over the full sample (p. 16); US equities with daily
  data from July 1926 (p. 15) and statistics for 1927–2017 (Exhibits 1 and 5); US bonds, yields from 1962 (p. 15) and
  statistics for 1963–2017 (Exhibits 9 and 11); 50 futures and forwards (19 commodities, 9 currencies, 10
  equity indexes, 9 bonds, 3 rate contracts, p. 16) and credit, for 1988–2017 as the results exhibits print it (Exhibits 15 and
  18–20); the Sharpe ratio improves slightly for equity indexes and credit and is similar for the other assets (p. 25),
  the effect negligible for fixed income, currencies and commodities (p. 31); the vol of vol and the left tail (mean
  shortfall) improve for almost all of the futures, forwards and credit (p. 25), but for US 10-year Treasury
  futures the left tail is similar (p. 25; Exhibit 13, p. 26); for a 60–40 portfolio with scaling at the asset and the
  portfolio level, 1988–2017, the cumulative return and the vol of vol improve (pp. 27–28, Exhibits 16–17); footnote
  7, p. 16, says that Moreira and Muir scaled by variance for most of their analysis. Kept out of the text: their
  Sharpe ratios and any statement that their results apply to E5's funds.
- Already in `project/SOURCES.md`: *RiskMetrics — Technical Document* (1996) for $\lambda=0.94$ (through LM26); Boyd and
  Vandenberghe (2004) through LM29, with no section of its own.
- Software: SciPy 1.18.1 (the v1.18.0 docs read and the installed 1.18.1 run on 2026-10-24).
  `scipy.cluster.hierarchy.linkage` reads a 1-D input as a condensed distance matrix and a 2-D one as observation
  vectors (`cluster/hierarchy/_hierarchy_impl.py:727-731`), so a square, symmetric, non-negative, hollow input is read
  as observations and raises `ClusterWarning` (`:934-944`); `method="single"` is the nearest-point rule (`:773-780`).
  `scipy.spatial.distance.squareform` with `checks=True` requires exact symmetry and an exactly zero diagonal
  (`spatial/distance.py:2283-2284`, `:2399-2409`; on 200 toy correlation matrices `np.corrcoef` was asymmetric in all
  200, and the symmetrized matrix with its diagonal set to 0 passed in all). cvxpy 1.9.3 with CLARABEL 0.11.1, as
  `vol5_rules.py` logs them; the solver settings rest on the shared decision "Solver output".
- Checked and not used: Roncalli, T. (2014), *Introduction to Risk Parity and Budgeting*, Chapman & Hall/CRC, DOI
  10.1201/b15151 (the publisher's record: 1st edition, ©2014, 440 pp., hardback ISBN 978-1-4822-0715-6; the Library of
  Congress record gives [2014], Open Library's own date 2013 and Crossref's e-book record 19 April 2016; not read;
  Griveau-Billion et al. cite it as
  Roncalli 2013); Spinu, F. (2013), "An Algorithm for Computing Risk Parity Weights", SSRN 2297383, DOI
  10.2139/ssrn.2297383 (Crossref only; its abstract describes a provably convergent Newton method for risk parity and
  risk budgets; not read); Raffinot, T. (2017), "Hierarchical Clustering-Based Asset Allocation", *Journal of
  Portfolio Management* 44 (2): 89–99, DOI 10.3905/jpm.2018.44.2.089 (Crossref: online 22 December 2017, print 31
  December 2017; not read); Cederburg, O'Doherty, Wang and Yan (2020), "On the performance of volatility-managed
  portfolios", *Journal of Financial Economics* 138 (1): 95–117, October 2020, DOI 10.1016/j.jfineco.2020.04.015
  (bibliographic data only; its findings stay out of the text, decision F).

**Chinese terms** (AUTHORING §1; English in parentheses at first use in each box; 樂詞網 searched on 2026-10-24 by the
drafter and again in the fresh pass of 1,817 searches the same day, whose corrections are applied here):

- From `plans/vol-5.md`'s list: 風險平價 (risk parity; 統計學名詞 lists only "risk-parity portfolio" 風險平價投資組合),
  風險預算 (risk budget; an entry only in 電子工程名詞 and 電機工程名詞, so another field's entry, AUTHORING §1),
  層次叢集法 (hierarchical clustering), 樹形圖 (dendrogram), 共變異數矩陣, 槓桿 (leverage), 週轉率 (turnover),
  交易成本, 無風險利率, 估計誤差, 凸函數, 目標函數, 限制條件; the book's forms 層次風險平價 (hierarchical risk parity),
  波動率目標 (volatility targeting). The §2 box says once that LM31's 風險預算 is a budget per asset, while LM7's
  風險預算 (lm07.md:354) capped the total volatility of two strategies (decision on Chinese terms).
- Looked up on 樂詞網 (all-listings phrase search, the survey's method):
  - single linkage clustering: 單一連接叢集法；最近連接叢集法 (統計學名詞) → 單一連接叢集法.
  - Euclidean distance: 歐氏距離 (數學名詞, 統計學名詞).
  - correlation matrix: 相關矩陣 (數學名詞, 統計學名詞), as LM10 and LM11 print it.
  - strictly convex function: 嚴格凸函數 (數學名詞; 統計學名詞 adds 狹義凸函數) → 嚴格凸函數.
  - uniqueness: 唯一性 (數學名詞, 統計學名詞).
  - positive definite: 正定的 (數學名詞, 統計學名詞); positive definite matrix 正定方陣 (數學名詞); LM10 prints 正定
    (lm10.md:302).
  - Newton's method: 牛頓法 (數學名詞), as LM4.
  - fixed point: 不動點；定點 (數學名詞) → 不動點.
  - coordinate: 坐標 (數學名詞); descent method: 下降法 (數學名詞); "coordinate descent" has no entry → 座標下降法,
    composed with the book's 座標 (LM1, LM11, LM12 print 座標; one term per concept keeps it).
  - rebalancing: 重新平衡 (管理學名詞-會計學); "rebalance" 再平衡 (電子計算機名詞) and 再平衡；重新平衡 (一般性常見術語);
    the book keeps 再平衡 (lm08.md:403; also LM3, LM9, LM10).
  - EWMA: "EWMA model" 指數加權移動平均模型 (統計學名詞 and 管理學名詞; 管理學名詞 also 指數加權移動平均數). The §6 box
    names the model 指數加權移動平均模型（EWMA）, as LM26 prints it (lm26.md:132; Glossary lm26.md:550).
  - leverage: 槓桿；槓桿作用 (統計學名詞); exposure: the book's 曝險 (LM8's Glossary, lm08.md:597).
  - no entry: risk contribution, marginal contribution (→ 風險貢獻, 邊際風險貢獻, as LM27's brief prints them), coordinate
    descent, inverse variance or volatility, quasi-diagonalization, equal risk contribution, recursive bisection,
    volatility targeting (→ 波動率目標). Composed forms kept with their English: 等風險貢獻 (ERC), 反波動率權重
    (inverse-volatility weights), 準對角化 (quasi-diagonalization), 遞迴二分 (recursive bisection; not 二分法, which
    樂詞網 gives for the root-finding bisection method).
  - reestimation: 再估計 (統計學名詞). periodic: no entry in the statistics, mathematics or management listings
    (動物學名詞 周期性；定期的; 國防部新編國軍簡明美華軍語辭典 定期，週期的) → 定期. trigger: no bare entry in those
    listings (管理學名詞 has only the compound "trigger price" 觸發價格; 一般性常見術語 觸發；觸發點; 電子計算機名詞
    觸發；觸發器; "trigger point" 記錄點 in 管理學名詞-會計學 is another idea). threshold: 閾值；門檻 (數學名詞). Composed
    forms, kept with their English: 定期再估計 (periodic re-estimation; 再估計 is the statistics listing's), 風險觸發
    (risk trigger); 門檻 (threshold) as the mathematics listing gives it.

**Open before Stage 2.** The editor's decisions of 2026-10-24 and 2026-10-25 settle every item of the draft, the three revisions and
the last pass, and the fresh check of 2026-10-31 closed its own items (below); the fresh verification of
the anchor rows that check changed reproduced them (2026-10-31), so nothing remains open before Stage 2.

- *Closed in the first revision.* O1 (turnover): decision A2; LM31 prints only R8's per-trade statistics over the 91
  trades after the first purchase (A31-36), and annual turnover is LM34's A34-06. O2 (other modules' numbers):
  decisions A4 and A5; every echo names its owner's anchor (A27-21, A28-06, A28-07, A28-10, A28-15, A30-12, A30-19,
  A30-24), and LM30's A30-19 prints both long-only and sample minimum variance on U28's halves, which X6 shows. O3 (lab
  data): the shared decision "Labs" lists the eight rules' net and gross wealth paths (C6). O4 (notation): AUTHORING §6
  as amended (no hat on $\sigma_{t+1\mid t}$, $\Sigma_{t+1\mid t}$ on $\mathbf R_t$, the scoped $\mathbf y$ row;
  decisions B1, B3, B5); the Deep Dive writes no eigenvalue symbol. O5 (the trigger threshold): fixed at 0.5 by decision
  D. O7 (HRP on E5 in the text) and O11 (the CCD widget): accepted, decisions D and E. O8 (the funds' indices): LM27's
  brief records them from the issuers, and LM31 uses LM27's wording. O9 (prerequisites): confirmed both ways (decision
  C9). O10 (lm08.md:290): optional at Stage 4, decision G (below). O6 (sources): decision F, then R3 below. The forward
  promise "whether R6's and R7's realized volatilities differ by more than chance" is dropped (per-module decision on
  LM33). The first recomputation's findings were applied then (A31-34's divisor 91, holding months named by their
  dates, gaps at machine precision as bounds, Newton's count following `erc()`, A31-39's annualized $\Sigma$, E8's $L$
  to four decimals).
- *Closed in the second and third revisions.* R1 (annualizing a holding month beside its ratio): decided as the brief proposed
  ("Decisions on the first revision", LM31): the realized and target volatilities both use the estimation frame's
  $A$, so their ratio is the daily one (45.3% against 7.84%, 5.78), and the Data role, X1 and E9 say so. R2 (tag lists
  of earlier briefs): the cross-check's table (Y1) adds LM31 to (28.2), (29.2), (29.3) and (29.5), and LM27–LM29 take
  it (decision "Tags and leads"); LM31's own lists stand ("Cross-module tags"). R3 (sources): the second hunt read
  Maillard et al. in their May 2009 working paper, López de Prado in SSRN 2708678 (23 May 2016) and Harvey et al. in
  the complete journal reprint; the decision prints their claims with the hunt's wording and no JPM page of the first
  two, whose JPM texts are closed ("Sources" now gives every location); Chaves et al. and Tseng stay cited as
  Griveau-Billion et al. describe them, the source the text actually read (decision F). The round-2 recomputation's
  findings are applied: KC §7 and E10 rest on the EWMA's wins and losses (A31-35 extended and relabelled); A31-26 reads
  "the mean of R6's 92 target weights"; printed parts that do not sum say "rounded separately" with their sum, and
  X1 prints one decimal; E5's variances are named as the unrounded $\hat\Sigma$'s; every value in a Printed column is
  in the text or marked "not in the brief's text"; U28's halves compare 1/N (LM30's) with LM31's three; Jacobi's
  stopping rule is named; "month" and "years" carry their labels (C7); "Owns" names R6's ex-post shares only; the
  anchors' status lists every changed definition. Of the cross-check's items, Y11 (LM31 prints A31-29's 2.14, which
  LM35 echoes), Y17 (A4's carve-out for R1's shares), Y18 (no flag marks in the text) and Y19 (A31-19 and A31-30 cited
  in §4, §6 and X7) are applied, and the echoes print at their owners' precision (C12): the first window's
  volatilities to one decimal and correlations to two, except E1's volatilities, whose weights need two decimals.
- *Repaired after the third revision's check.* The holding-month shares name their weights, each holding month's own
  target weights on that holding month's covariance (A31-26's definition), in Resolved (b), the forward-links row for
  lm10.md:225, X5, E7 and the Pitfalls; E4 cites R3's 5.02% as LM28's A28-10 (C12); (31.2) lists no speculative user
  (C8); KC §7's month is a holding month (C7); E5 prints the squares of E1's 13.50% and 8.54% beside the variances
  (A31-17).
- *Closed in the fresh check of Stage 1 (2026-10-31).* KC §3: with a zero budget CCD's update still runs but can set
  that fund to 0, outside $\mathbf y>\mathbf 0$;
  Harvey et al.'s 50 instruments are futures and forwards, with credit added on top; E3 and P11 name Newton's start,
  `erc()`'s rescaled $y_i=1/\sigma_i$ (6 steps either way, A31-14); the quasi-diagonal order states SciPy's merge
  numbering, which decides P6 and E5; (31.1) is the equations, with long-only stated for the portfolio; E2 prints the
  two-decimal volatilities its weights need and takes its shares from the unrounded $\hat\Sigma$ (C12); outcome 8 is
  practised in E8 (Harvey et al.'s 20-day half-life, $\lambda=0.9659$, against R8's 11.2 days, A31-38) and outcome 7's
  second clause is assessed; the plug-in sentence, the LM11 pointer for the extreme value theorem, P11's tolerances
  and stopping rules, the Sources' claims and pages, the hygiene and exhibit notes, §8's `squareform` row and the
  status lines are corrected; A31-39 no longer prints Jacobi's step count, which depends on the order of the
  floating-point operations; KC §8's asymmetry is anchored as a bound and true/false checks on E5's windows (A31-19).
  The lab's GARCH variant averages (26.4) over the next 21 sessions, fixed before any lab result (the editor's
  decision on R31-07).

Left to a later stage by the decisions (not before Stage 2):

- **lm08.md:290's rewording** (optional, decision G). Recommendation: make it at Stage 4 as "Stage 4 for earlier
  modules" words it. The present sentence is not wrong, since the factor 2 changes no tree (A31-21), but HRP builds its
  tree on the column distance of half that distance, and the new wording says so.
