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

This file holds the editor's Stage 1 decisions (2026-10-24): the shared decisions for both volumes, the capability
check and the owner's answers, the decisions on the survey and on the spines' fresh check, the Stage 4 list, and one
spine per module. The briefs of LM27–LM31 will follow in this file and those of LM32–LM35 in `plans/vol-6.md`; the
anchors go to `plans/vol-5-anchors.md` and `plans/vol-6-anchors.md`. Until Stage 3 the briefs and anchors are the
plan; from Stage 3 the module sources and their numbers scripts are authoritative (as in `plans/vol-4.md`).

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
  $(1-\text{shrinkage})\hat\Sigma+\text{shrinkage}\cdot\bar\lambda I$ to 1e-17), which matches the book. Every script
  passes `ddof` explicitly.
- **Return type and the domain of log growth.** Portfolio returns are simple: $R_p=\mathbf w^{\top}\mathbf R$ (8.3)
  for weights summing to 1, $\mathbf f^{\top}\mathbf R$ for exposures (8.4). Wealth compounds simple returns; log
  returns are used for sums over days and for growth rates, as Volume III. Every $\ln(1+R)$ states its domain $R>-1$.
  A leveraged or short position checks $1+\mathbf f^{\top}\mathbf R>0$ on every date it is applied to; a path that
  reaches wealth $\le0$ is reported as ruin at that date, never truncated, dropped or floored (guidance).
- **Data.** Five samples; never mix two within one statistic, and name the sample in every caption.
  - **E5** (new, the through case): five Taiwan-listed ETFs, daily total returns in New Taiwan dollars. 0050
    (元大台灣50), 00646 (元大S&P500), 00679B (元大美債20年), 00635U (期元大S&P黃金) and 00642U (期元大S&P石油).
    Closes 2017-01-17 → 2026-10-08 on TR23's calendar, built by a new `data/vol5_series.py`. Total return
    $(P_t+D_t)/(P_{t-1}/s_t)-1$ as Volume I (`data/README.md`): distributions from `TaiwanStockDividendResult` with
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
    return of a portfolio use the wealth frame. A single fund's statistics use that fund's own dates. (Without the
    wealth frame every rule would miss 2025-06-10 → 06-18: 00642U +12.82%, R1 about +2.7%; fresh check. PITFALLS §3,
    "Aligned samples change the counts".) The scripts print the authoritative counts.
  - **Timing of E5.** The four foreign funds close at 13:30 Taipei time and carry the previous US session (survey:
    00646's daily correlation with SPY's previous session 0.681, with the same-dated session 0.118). 0050 at the same
    close also reflects that US session, so a same-day correlation is not simply biased in one direction (fresh
    check: 0050 with 00646 0.601 daily, 0.592 weekly, 0.567 monthly; with 00679B −0.105, −0.020, −0.014). LM27 shows
    daily, weekly and monthly correlations once and says the daily figure can differ either way; other modules state
    the frequency they use. The rules estimate $\hat\Sigma$ from daily returns.
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
    Sharpe ratio on the window's sample means in excess of $r_f=1.5\%$ ($r_f/A$ a day), solved as the homogenized
    QP $\min\mathbf y^{\top}\hat\Sigma\mathbf y$ subject to $\hat{\mathbf e}^{\top}\mathbf y=1$, $\mathbf y\ge0$,
    $\mathbf w=\mathbf y/\mathbf 1^{\top}\mathbf y$; if no fund's mean exceeds $r_f/A$, R4 holds R3 (the fresh check
    found two or more funds above it at every one of the 93 E5 month-ends; the fallback serves other universes).
    **R5** R3 with the Ledoit–Wolf covariance (scaled-identity target, scikit-learn). **R6** equal risk
    contributions, long-only. **R7** hierarchical risk parity as López de Prado (2016) publishes it: the distance
    $\sqrt{(1-\rho_{ij})/2}$, the Euclidean distance between columns of that matrix, single linkage,
    quasi-diagonalization and recursive bisection with inverse-variance weights inside clusters (the brief checks
    every step against the paper). **R8** R6 scaled by $L_t=\min\!\big(1.5,\ \bar\sigma_t/\hat\sigma_{t+1\mid t}\big)$,
    set at each monthly trade and drifting between trades. $\hat\sigma^2_{t+1\mid t}$ is LM26's EWMA ($\lambda=0.94$,
    uncentred, daily simple returns in decimals) of the returns of the R6 book as held, started at the window's
    sample variance at the window's first row. $\bar\sigma_t$ is the R6 book's realized daily volatility over the
    same 504 rows (divisor $T$). So R8 targets R6's own two-year volatility, with no level chosen in advance. Cash
    ($1-L_t>0$) earns $r_f=1.5\%$; borrowing ($L_t>1$) costs $r_f+2$ points $=3.5\%$ a year, an illustrative
    financing rate (Research hygiene puts financing among the costs; no official rate exists), with sensitivities
    at spreads of 0 and 5 points.
  - **Costs** (the cost model below) on every trade: the value traded is $W\lVert\mathbf w_t-\mathbf w^{\mathrm{drift}}_t\rVert_1=2W\,\mathrm{TO}_t$;
    the cost is $0.1425\%\times(\text{buys}+\text{sells})+\sum_i\text{tax}_i\times\text{sales}_i$, scale-free (no
    minimum fee), deducted from wealth at the trade.
  - **Comparison criteria, fixed now.** Net of costs: annualized log growth $\ln(W_{\mathrm{end}}/W_{\mathrm{start}})$
    divided by the years (calendar days ÷ 365.25, AUTHORING §8); the Sharpe ratio of daily returns in excess of
    $r_f=1.5\%$, $\times\sqrt A$ (one $r_f$ for every rule, since R8 holds cash); maximum drawdown; average annual
    turnover; total costs. The benchmark is R1. LM33 tests each of R2–R8 against R1 (seven pairs, Ledoit and Wolf
    2008) and deflates the best rule for $n=8$.
  - **Owners.** Each rule is defined by its module: R3 and R4 by LM28 (unconstrained) and LM29 (long-only, the
    through-case form), R5 by LM30, R6–R8 by LM31; R1 and R2 by LM27. One owner per statistic of the rules, all
    computed by `vol5_rules.py`, net of costs unless the owner shows gross against net: LM27 the accounting
    identities and the wealth recursion; LM29 costs as a term in the objective; LM30 the realized out-of-sample
    volatility of R1, R3 and R5; LM31 R6–R8's weights, risk shares, exposure path and realized volatility; LM32 their
    VaR, ES and drawdowns; LM33 their Sharpe ratios, intervals and tests; LM34 net wealth, log growth, turnover,
    costs and gross against net; LM35 their scenario losses. A module that needs another's number cites it.
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
  LM34 or this decision before LM34 by a pointer). Commission 0.1425% of the value traded on each side: TWSE's
  Operating Rules Art. 94 lets brokers set their rates and requires notice above 1.425‰, so it is the posted
  reference, not a cap, and brokers' discounts are not modelled. Securities transaction tax on sales: 0.1% for ETFs
  (Securities Transaction Tax Act, as amended 2025-01-02, Art. 2), 0 for bond ETFs to 2026-12-31 (Art. 2-1, which
  suspends it from 2017-01-01 for securities-investment-trust bond ETFs, leveraged and inverse ones excluded; 00679B
  was exempt throughout E5). The futures ETFs 00635U and 00642U are taxed at 0.1% only if the Stage 1 source check
  confirms it (Art. 2's "其他經政府核准之有價證券" is the likely category); no number uses their tax before. No
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
  | $\mathbf w$, $N$, $\mathbf w_{t-1}$ | weights ($\mathbf 1^{\top}\mathbf w=1$), number of assets, weights set at the previous close (lm12.md) | as §6 |
  | $\mathbf w^{\mathrm{drift}}_t$ | weights after a period's returns, before trading | new; a tilde stays "centred" |
  | $\mathbf f$, $L$, $L_t$ | exposures, total exposure $\mathbf 1^{\top}\mathbf f$, R8's exposure | as §6; a gross limit is written as a number on $\lVert\mathbf f\rVert_1$, not as $L$; LM30 and LM32 write no Cholesky $L$ in the main text |
  | $\lVert\mathbf x\rVert_1$ | the 1-norm; gross exposure $\lVert\mathbf f\rVert_1$ (LM8, lm08.md:178–180) | new row |
  | $\mu_p$, $\sigma_p$, $\sigma_p^2$, $s_p$ | portfolio mean, standard deviation, variance (model and sample) | add $\mu_p$ to the $\sigma_p^2$ row |
  | $\mathbf e=\boldsymbol\mu-r_f\mathbf 1$ | excess returns (LM7, lm07.md:60) | new row (§6 mentions it only in the basis-vector row); LM27–LM31 write no basis vector $\mathbf e_i$ |
  | $\delta$ | risk aversion in the exposure form $\mathbf f^{\top}\mathbf e-\tfrac{\delta}{2}\mathbf f^{\top}\Sigma\mathbf f$ with a riskless asset; LM28 cites LM7's two-asset $\mathbf f^*=L^*\mathbf w^{\mathrm{tan}}$ (lm07.md:484) and leaves the N-asset Kelly identity to LM43 | new; LM25's $\delta$ is not cited in Volume V |
  | $\lambda$, $\nu_i$, $\mathcal L$ | equality and inequality multipliers, Lagrangian, LM7's signs; a second equality multiplier takes a letter subscript ($\lambda_b$, $\lambda_\mu$) | as §6; in LM30 multipliers are $\nu$ ($\lambda_k$, $\bar\lambda$ are eigenvalues); in LM31 $\lambda$ is only LM26's decay |
  | $K$, $\mathbf b$ | constraint matrix and right-hand side, $K\mathbf w=\mathbf b$ (LM28, LM29; modules without bets) | scoped as §6's $M\mathbf x=\mathbf b$ |
  | $\mathbf w^{\mathrm{mv}}$, $\sigma^2_{\min}$, $\mathbf w^{\mathrm{tan}}$, $\mathrm{SR}^*$ | minimum-variance weights and variance, tangency weights (LM7), best Sharpe ratio | new for mv; star only for an optimum |
  | $\beta_{i,p}$, $\beta_i$ | an asset's beta to its portfolio, $\operatorname{Cov}(R_i,R_p)/\sigma_p^2$; its market beta (LM23's (23.1)) | new for $\beta_{i,p}$ (LM27) |
  | $\mathrm{TO}_t$; $\text{tax}_i$ | one-way turnover $\tfrac12\lVert\mathbf w_t-\mathbf w^{\mathrm{drift}}_t\rVert_1$; a fund's tax rate on sales (upright word) | new; no scalar cost symbol next to $\mathrm{TO}$ |
  | $c$, $\hat\Sigma_{\mathrm{tgt}}$, $\hat\Sigma_c=c\hat\Sigma+(1-c)\hat\Sigma_{\mathrm{tgt}}$ | the data's weight in a shrunk covariance (LM24's $c$; scikit-learn's `shrinkage_` is $1-c$), target, shrunk matrix (LM30) | extends §6's $c$ row (LM24) to LM30, which has no Kelly fraction |
  | $n_0$, $\mathbf w_{\mathrm{ref}}$, $\mathbf e_{\mathrm{eq}}$, $K\mathbf e=\mathbf b+\boldsymbol\varepsilon$, $\Xi$ | Black–Litterman: prior worth in observations ($\tau=1/n_0$; LM24's $n_0$), reference weights, implied excess returns $\delta\Sigma\mathbf w_{\mathrm{ref}}$, views on excess returns, view-error covariance | new; $P$, $Q$, $\Omega$, $\tau$, $\pi$ are taken book-wide |
  | $\mathrm{MRC}_i$, $\mathrm{RC}_i$ | marginal and component risk contribution, $\mathrm{RC}_i=w_i(\Sigma\mathbf w)_i/\sigma_p$, $\sum_i\mathrm{RC}_i=\sigma_p$ (LM27 owns, LM31 uses) | new |
  | $\mathbf b$ in LM31 | risk budgets (shares summing to 1); LM31 writes its constraints out, without $K\mathbf w=\mathbf b$ | scoped |
  | $d_{ij}$ | HRP's correlation distance $\sqrt{(1-\rho_{ij})/2}$ (LM31), half of LM8's per-date distance $\sqrt{2(1-\rho)}$ (lm08.md:290); the second distance takes a symbol the brief chooses (no tilde, no prime) | new, entries only; $d^2$ (LM16) and $d$ (LM23) do not occur in LM31 |
  | $\bar\sigma_t$, $\hat\sigma_{t+1\mid t}$ | R8's window volatility and EWMA forecast | as LM26 |
  | $u$, $\operatorname{VaR}_u$, $\operatorname{ES}_u$, $m$ | tail probability ($u=0.01$ for "99% VaR"); value at risk $-F_{R_p}^{-1}(u)$ and expected shortfall, positive for a loss; horizon in days | §6's $u$ |
  | in LM32 | $\alpha$ is the tail index (LM15, LM20); GARCH is cited by tag with its coefficients named in words; $k$ is Hill's count, a number of standard deviations is written in words; $\ell$ is a block length (LM32 cites no log-likelihood) | scoped, one meaning per module |
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
- **Solver output.** Solvers get annualized inputs ($A\hat\Sigma$, $A\hat{\boldsymbol\mu}$; fresh check: on
  daily-unit $\hat\Sigma$ CLARABEL's defaults missed the exact long-only solution by up to 4.6e-4 in a weight, and
  annualizing brought OSQP and CLARABEL within 4.1e-6). Tolerances are set and printed (CLARABEL `tol_gap_abs`,
  `tol_gap_rel`, `tol_feas` 1e-10; OSQP `eps_abs`, `eps_rel` 1e-10 with polishing); the status must be `optimal`;
  every printed solution is checked by its KKT residuals and against a closed form or a second solver, and the text
  names the solver. R6 is computed in `vol5_rules.py` by Newton or fixed-point iteration to 1e-12, with cvxpy's
  log-barrier form as the cross-check. A weight with $\lvert w_i\rvert<10^{-6}$ prints as 0, and a constraint is
  active when its slack is below $10^{-6}$. Every printed number comes from a fresh `Problem` (no warm start).
  Near-collinear assets need a stated tie-break before their weights are printed. cvxpy's `Variable.value` is typed
  `ndarray | None`: narrow it with an `assert` before use (ty).
- **Counting, simulation, quantiles, rounding.** As Volume IV: one counting guard or exact arithmetic; one generator
  per experiment, `np.random.default_rng([e, 20261011])`, with draws, seed and standard error printed; every quantile
  $\hat F^{-1}(u)=x_{(\lceil uT\rceil)}$ (`method="inverted_cdf"`); flag values within a tenth of a rounding unit of a
  boundary. The historical ES estimator is fixed in the LM32 brief (Acerbi and Tasche's weighted form, or the mean of
  the $\lceil uT\rceil$ worst returns) and used by every module.
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
  budgets need a source beyond Maillard et al. (equal contributions); the LM31 brief finds one. Not printed until
  read in the original: Chopra and Ziemba's ratios, Black and Litterman's own claims, Mertens (2002; LM20 derives
  (20.9) without it), Christoffersen's test details beyond the formula, Ledoit and Wolf's (2008) bootstrap scheme.
  PBO uses combinatorially symmetric cross-validation, not a bootstrap.
- **Chinese terms.** AUTHORING §1 (樂詞網; English in parentheses at first use in each box). Looked up 2026-10-24
  (survey); recorded in SOURCES at Stage 1. From 樂詞網: 投資組合, 效率前緣, 最小變異數投資組合, 資本市場線, 風險規避,
  二次規劃, 凸規劃 (convex optimization; 凸函數, 凸集), 拉格朗日乘數, 收縮, 收縮估計量, 共變異數矩陣, 估計誤差, 條件數,
  風險平價 (risk parity; 風險平價投資組合 in the statistics listing), 風險預算, 層次叢集法, 樹形圖, 風險值, 夏普比率,
  過度配適, 交易成本, 週轉率, 壓力測試, 情境分析, 敏感度分析, 無風險利率, 資產配置, 槓桿, 限制條件, 目標函數, 對偶問題,
  交叉確認, 資料偵伺, 選擇偏誤, 歷史模擬法, 保證金追繳, 條件風險值 (CVaR, named once). The book's own forms, printed
  with their English in every box that uses them: 切點投資組合 (tangency portfolio, LM7's Glossary; lm07.md:511's
  切點組合 follows at Stage 4), KKT 條件, 預期短缺 (expected shortfall, LM5's settled form), 回撤, 最大回撤, 回測,
  波動率目標 (volatility targeting), 層次風險平價 (hierarchical risk parity), 前視偏誤 (look-ahead bias), 存活者偏誤
  (survivorship bias), 滾動前進測試 (walk-forward test; the brief may keep the English only), 尾部風險 (tail risk),
  一致性風險量數 (coherent risk measure; 風險量數 is the statistics listing's), 劣加性 (subadditivity, the mathematics
  listing's 劣加性函數).
- **Research hygiene.** Volumes V–VI are the first where *Out-of-sample* results lead. The through case's settings
  are *fixed in advance* (above) and say so in each note; an in-sample frontier or allocation is *In-sample*, a
  simulated one *Model*, a hand-built scenario *constructed* or *hypothetical*. Every module states how many rules or
  versions it compared on the same data (LM21's rule).
- **Charts.** As Volume IV (AUTHORING §7) plus the additions the owner approves (capability check). At most four named
  series: E5 has five funds, so a chart of all five uses small multiples, four funds plus one in `"var(--muted)"`
  named in the caption, or portfolios as series and funds as categories (survey: a fifth series without a colour draws
  black). A dashed curve is one series, never a chain of segments (survey: segments lose the dash). A dendrogram is
  drawn with scatter `lines` (survey prototype). Every value the text cites is plotted or printed; JSON at most
  300 KB; no intraday price path is published (per-day statistics only).
- **Widgets.** A browser widget runs no optimizer: it uses closed forms, precomputed grids from the module's script,
  or module-local code under 30 lines (for example a 5×5 solve with a positive-definiteness check) tested against
  Python as `data/lm15_charts.py` does. Student-$t$ quantiles come from an embedded grid (`Book.dist.tInv` was not
  approved, ROADMAP). `Book.controls`, `Book.rng`, `Book.dist`; the initial state computes within the PDF printer's
  wait.
- **Labs.** One per module, `build/make_labNN.py`, reading only its own `data/` folder (`data/make_lab_data.py`). A
  lab gets the rules' per-date weights and the wealth frame as derived files from `make_lab_data.py` (no copy of
  `vol5_rules.py`); it re-implements only its own module's rule as an exercise and checks it against those weights.
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
| Checkpoint after Volume VI: allocate and stress under leverage, turnover and cost limits; out-of-sample comparison; scenario losses; explain how constraints change the allocation (g:44) | adopted, adjusted | the modules practise each part on E5; LM35's lab ends with the whole task on a universe the modules did not use, so that the reader cannot reuse E5's answers (checkpoints may reuse data, g:49; a fresh universe is the editor's choice for that reason); no new module (SPEC §4) |
| Checkpoint after Volume IV (a strategy's characteristics and uncertainty, g:43) | adjusted | Volume IV is published; LM33's first section does that task on the through case's returns |
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
| Two Boyd papers on risk-constrained and robust Kelly (g:133–138) | left to Volume VIII | Kelly sizing; their drawdown definition is checked in the original there |

## Capability check (2026-10-24)

What the spines need and the repository lacks (survey, its critic and the fresh check: `book.js` rendered in headless
Chromium, `build/`, `data/`, `pyproject.toml`). **Owner's answers: pending**, except (A).

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
  5. Optional, LM35: US proxies for the 2008 and 2015 replays, when 00646, 00679B, 00635U and 00642U did not exist
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
  $\hat\Sigma_{t+1\mid t}=\lambda\hat\Sigma_{t\mid t-1}+(1-\lambda)\mathbf r_t\mathbf r_t^{\top}$ in one paragraph;
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
  2025-04-07, when 0050 traded at 158.4 all day, exactly −10%). A limit is computed from the official rule, which the
  LM35 brief sources: whether cross-border ETFs have a daily limit at all (survey, explored: 00646 fell 12.59% that
  day). A locked day is shown by the daily open, high, low and close: on 2025-04-07 0050 traded 29.6 million shares,
  all at 158.4 (fresh check), so sales executed at the limit, none below it, queued orders were not guaranteed to
  fill, and the next open was 151.2.
- **Unexplained extremes.** 2026-07-17 (TR23 −6.46%) and 2026-07-31 (+7.98%) are real in the data (T5S 13:30:00
  equals the close); a cause is printed only from a dated source. The same holds for every scenario's narrative.

## Stage 4 changes to earlier modules

Collected here as the briefs add them; applied at publication with the edition note.

- Leads: LM4 gains 33 and 34; LM5 32; LM7 30 and 31; LM11 34 (published forward links with no lead; survey). The
  briefs' prerequisites add more (fresh check, draft: LM19 → 27; LM8 → 28; LM4, LM9, LM11, LM12 → 29; LM11 → 31;
  LM1, LM10 → 32; LM1, LM23, LM26 → 35); each brief lists its own.
- lm07.md:511: 切點組合 → 切點投資組合 (the Glossary's form, lm07.md:771).
- lm07.md:786: Chopra and Ziemba (1993) gains its issue number, 19(2): 6–11.
- lm21.md:373: White (2000) and Romano–Wolf (2005) correct a search on the same data; testing the best rule on later
  data is the other half of LM34. Reword so the sentence says both.
- `src/syllabus.yaml`: LM31's line ("Euler risk contributions and risk-based allocation") becomes risk budgeting with
  LM27's contributions.
- Each brief's "Stage 4 for earlier modules".

## Spines

Each spine gives the module's question, its draft prerequisites, the forward links it must honour (from the survey;
the brief rechecks each line), what it owns and leaves, its data, a candidate case, exhibits and widget, and what the
brief must settle. Numbers marked "explored" are the survey's first look; only anchors may be printed.

### LM27 Portfolio Return and Risk

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

### LM28 Mean–Variance Optimization

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

### LM29 Convex Optimization in Practice

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

### LM30 Estimation Error and Robust Portfolios

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

### LM31 Risk Parity, HRP and Volatility Targeting

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

### LM32 VaR, Expected Shortfall and Drawdown

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

### LM33 The Statistics of the Sharpe Ratio

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

### LM34 Backtesting Without Fooling Yourself

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

### LM35 Stress Testing

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

**Data.** E5's wealth frame and the rules' holdings; TR23 and the 27 sector closes from 2007-07-02 for 2008; T5S
per-day statistics; TX23 on limit days; US proxies if approved; the checkpoint universe (0056, 00662, 00720B with
E5's funds as the brief decides).

**Candidate exhibits.** Scenario losses of four rules across the five scenarios (bars); the 2025-04-07 gap and the
day's low from T5S statistics; the reverse-stress shock vector; R8 at higher caps against the ruin line. **Widget:** a
scenario builder (sliders for shocks to the five funds; the portfolio loss for the selected rule's weights; closed
form).

**Hygiene.** Replays of the rules' own holdings *Descriptive* (historical paths); replays on chosen weights and proxies
*hypothetical*; hand-built shocks *hypothetical*; no probability is attached to any scenario.

**Brief settles.** Each scenario's window (peak to trough, the worst day, the worst 5 and 20 days) from the anchors;
the weights replayed in 2008 and 2015; the proxy rule; the official price-limit rule for domestic and cross-border
ETFs; the checkpoint's universe and its rubric.
