# Volume VI — Measuring True Risk and Return: briefs

Volume VI (LM32–LM35) is the second half of batch 4. Its shared decisions, the through case (E5 and the rules R1–R8),
the capability check and the owner's answers, the editor's decisions on the survey, on the briefs and on their three
revisions (with "Listing markets"), the Stage 4 list and the spines are in [`vol-5.md`](vol-5.md); they apply here
unchanged. Every number a brief quotes is an anchor in [`vol-6-anchors.md`](vol-6-anchors.md) (printed by
`data/vol6_anchors_lmNN.py`), an anchor of [`vol-5-anchors.md`](vol-5-anchors.md) cited by its ID, or a published line
cited by file and line. Until Stage 3 the briefs and anchors are
the plan; from Stage 3 the module sources and their numbers scripts are authoritative.

Status: revised three times and given a last pass on 2026-10-24/25, each revision verified by fresh agents; revised on 2026-10-31 to the fresh check of the whole of Stage 1 ("Decisions on the fresh check of the whole of Stage 1", `plans/vol-5.md`), whose fixes and changed anchors fresh agents verified the same day.

## LM32 VaR, Expected Shortfall and Drawdown

Stage 1 brief, drafted 2026-10-24 from the editor's spine (`plans/vol-5.md`, "### LM32 VaR, Expected Shortfall and
Drawdown") and the shared decisions above it, revised the same day to the editor's decisions on the briefs (cross-module
A–G and "Per module"), the independent recomputation, the cross-module check and decision F's source check, and revised
a third time to the "Decisions on the second recomputation and cross-check" (the second recomputation's findings, the
cross-check's Y items and the second source hunt), then on 2026-10-25 to the third revision's verifier and the
"Decisions on the third revision" (no number changed), and on 2026-10-31 to the fresh check of the whole of Stage 1
(its verifier's items, with the editor's choices: outcome 3 at [D], LM22's labels, the lab refitting LM26's laws; no
computed figure changed, Problems 10 and 11 print $1.15\times10^{-9}$ and 3.634, and A32-17, A32-21, A32-24 and A32-53 print new
lines). Every number carries its anchor ID at first appearance;
`data/vol6_anchors_lm32.py` prints them all (57 rows, `## LM32` of `plans/vol-6-anchors.md`). Numbers quoted from
published modules carry their file:line instead; the through case's definitions are cited to LM27–LM31 by their briefs'
tags (decision C8), rechecked when those modules are written. Statistics owned by another module are not printed, or are
echoed with the owner's anchor ID (shared decision "Owners", decision A).

**Prereq:** `[1, 5, 10, 12, 14, 15, 16, 18, 19, 20, 21, 22, 26, 27, 28, 29, 30, 31]`. What each supplies (tags rechecked
in `src/` on 2026-10-24):

- LM1: $\mathrm{DD}_t:=1-W_t/\max(W_0,\dots,W_t)$, the running peak including $W_0$, and the recovery gain
  $\mathrm{DD}/(1-\mathrm{DD})$, (1.17) (lm01.md:519–521).
- LM5: the normal conditional tail mean $\E[R\mid R\le\kappa]=\mu-\sigma\varphi(z)/\Phi(z)$, (5.11) (lm05.md:506), and
  its promise that, with $\kappa$ at the VaR level, its negative is LM32's ES (lm05.md:509, 785). LM32 writes no
  $\kappa$ (the book-wide condition number); (32.3) puts $F_R^{-1}(u)$ in its place.
- LM10: $s_p^2=\mathbf w^{\top}\hat\Sigma\mathbf w$, (10.4), for the normal VaR of a portfolio in §5's subadditivity
  argument.
- LM12: colouring standard normal draws with the Cholesky factor (12.8) (lm12.md:502–504), for one sentence of §6 and
  the lab's portfolio Monte Carlo (LM12 already lists 32 in its leads).
- LM14: the quantile function $F_X^{-1}(u)=\min\{x:F_X(x)\ge u\}$ (lm14.md:85–87) and its sample form
  $\hat F^{-1}(u)=R_{(\lceil uT\rceil)}$ (lm14.md:96–98); TR23's 1% and 0.1% quantiles −3.567% and −6.313%
  (lm14.md:105) and its median 0.0879% (lm14.md:103); NumPy's `linear` default against `inverted_cdf` (lm14.md:120).
- LM15: normal quantiles (15.6); the $t_\nu$ density (15.9), its variance (15.10) and the scaled model
  $R=\mu+\sigma\sqrt{(\nu-2)/\nu}\,Y$ (15.11); the ML fit's 1% quantile −3.365% against −3.567% and the verdict "too
  heavy from −5%" (lm15.md:461); the tail-mean comparison (lm15.md:469).
- LM16: (16.4), $\Var(\mathbf a^{\top}\mathbf X)=\mathbf a^{\top}\Sigma\mathbf a$; (16.7), linear maps of normal vectors
  and colouring.
- LM18: the inverse transform (18.1), behind (32.1)'s tail-mean form; the Monte Carlo estimator, its standard error and
  interval (18.2), (18.3), and the batch standard error (lm18.md:153); antithetic and control variates (18.5), (18.6),
  named in one sentence; importance sampling (18.7) with its second moment $e^{k^2}\Phi(-2k)$ (lm18.md:300).
- LM19: TR23's sample (lm19.md:46: $T=5{,}849$, 23.7645 years, $A=246.12$), $\bar R=0.0625\%$ (lm19.md:18; 0.062505% at
  lm19.md:80) and $s=1.2084\%$ (lm19.md:19); the variance
  of an $m$-day sum (19.7), for the $\sqrt m$ rule; the promise that a drawdown is a path statistic (lm19.md:138).
- LM20: Hill's estimator and its SE (20.10) with $k=108$ and $\hat\alpha=3.63$ at 3% (lm20.md:441); the Student-$t$ fit
  of TR23, $\nu=3.065$ (0.144), location 0.0997% (0.0124), scale 0.7761% (lm20.md:269); the promises of lm20.md:276 and
  449.
- LM21: the exact binomial tail as a test of a frequency (lm21.md:95, 207) and of a count after an event; one-sided
  p-values (21.2); Bonferroni (21.6); the rule that every module reports how many tests ran on the same data.
- LM22: the stationary bootstrap (22.3) and the book's block rule (lm22.md:254: 145 for TR23); LM18's five returns as
  a hand example (lm22.md:75).
- LM26: EWMA (26.2), GARCH(1,1) (26.3), its unconditional variance and $m$-step forecasts (26.4); the forecast design
  (1,231 returns, monthly refits, 4,609 days; lm26.md:357), the 2 April → 7 April forecasts 1.7222 and 1.5605
  (lm26.md:39) and 7 April's return, −9.70%, a log return of −10.20% (lm26.md:32; decision A5); variance forecasts
  scored by (26.8) and (26.9), contrasted in §7 with scoring a quantile.
- LM27: the wealth recursion (27.1)–(27.2) whose path the drawdowns use, E5's two frames, $\sigma_p$ (27.4), R1 and
  R2, and the cost of the first purchase (A27-23, echoed in §8).
- LM28 and LM29: R3 and R4 (LM29's long-only forms); LM29's convex sets and functions (29.1) and the global minimum of
  a convex problem (29.3), for Problem 12's expected-shortfall minimization, a linear program (shared decision "LM29's
  scope").
- LM30: R5. LM31: R6–R8, (31.7) for R8's exposure $L_t$ (cited, not printed).

A later module's numbers are echoed with its owner's ID (decisions A1, A5, C12): each rule's loss on 7 April 2025 is
cited to LM35's A35-13 without a value, and the lab echoes LM35's T5S closes and lows of 7 April 2025 and 5 August
2024 (A35-45) at LM35's two decimals.

**Leads:** `[33, 34, 35, 36, 39, 44]`: LM33 (§8's forward pointer: the rules' Sharpe ratios beside their tail risk;
LM33's brief cites no LM32 tag), LM34 (§8's forward pointer: net results beside the rules' drawdowns; LM34's brief
cites no LM32 tag, so the lead stands on the pointer, decision C9), LM35 (its brief contrasts scenario losses with VaR
and ES in words and cites (32.9) and the rules' drawdowns, A32-35, in its four failure forms; it owns each rule's loss
on 7 April 2025, decision A1), LM36 (Brownian motion, behind (32.10); §8's pointer), LM39 (jumps, the day GARCH could
not see; §6's pointer), LM44 (drawdown control and drawdown probabilities under a model; §8's pointer). LM36, LM39 and
LM44 are not briefed yet: they are leads by the pointers, and the tags they may cite are listed when their briefs are
written.

**Forward links honoured.**

| Earlier text | Promise | Kept in |
|:--|:--|:--|
| lm05.md:369 | "prefer tail measures that need fewer moments ([[LM15]], [[LM32]])" | §3: VaR needs no moment and ES only a first; TR23's $t$ fit ($\nu=3.065$) has a variance but no fourth moment, and Hill's $\hat\alpha=3.63$ leaves ES finite [A32-14, A32-17] |
| lm05.md:509 | (5.11) at the VaR level, negated, is LM32's expected shortfall | §3: (32.3) is derived from (5.11) with $\kappa=F_R^{-1}(u)$ |
| lm05.md:785 | Glossary: 條件尾端平均 … minus the expected shortfall (預期短缺) of LM32 | §2's definition; 預期短缺 in every box (Chinese terms) |
| lm14.md:122 | "[[LM32]] turns lower quantiles into value at risk" | §2: (32.1); E2 echoes −3.567% and −6.313% (lm14.md:105) [A32-11] |
| lm15.md:194 | the sign-reversed 1% quantile is the one-day 99% VaR | §2's definition and §3's (32.3) from (15.6) |
| lm15.md:469 | the mean return beyond a quantile, sign reversed, is LM32's ES | §2: (32.1)'s tail-mean form; §3, X3: the $t$'s ES |
| lm18.md:300 | "[[LM32]] applies these estimators to value at risk" | §6 and Problem 10: (18.7) for the probability of 7 April's loss under GARCH-n (4,927 of 10,000 shifted draws land in the tail, against 0.000011 plain draws expected) [A32-53]; one sentence on (18.5), (18.6) |
| lm19.md:138 | "A drawdown does, so it is a path statistic; [[LM32]] studies it" | §8: the rules' MDDs under permutation and the stationary bootstrap, X9 [A32-36, A32-37] |
| lm20.md:276 | the median's "standard error is [[LM32]]'s" | §4, E5: the median's SE 0.0116 points by (32.6) and its distribution-free interval 0.069% to 0.114% by (32.5), against LM20's location SE 0.0124 [A32-18, A32-19] |
| lm20.md:449 | "Value at risk from a tail model is [[LM32]]'s; extreme value theory beyond Hill's estimator is not in this book" | §3: Hill-tail VaR and ES in one paragraph, Problem 11 [A32-17]; no EVT |
| lm26.md:183 | "[[LM32]] turns it into a value-at-risk" | §6: (32.8) on LM26's forecasts, E7 [A32-05, A32-26] |

The grep of `src/*.md` and `src/pages/*.md` for `[[LM32]]` finds exactly these eleven lines (lm05:369, 509, 785;
lm14:122; lm15:194, 469; lm18:300; lm19:138; lm20:276, 449; lm26:183), the spine's list; `build/make_lab*.py` has no
"LM32". Plan promises with no published link, also kept: `plans/vol-2.md:578` and ROADMAP's Simulation row (Monte
Carlo VaR → LM32; LM12's leads list 32): §6's ten-day Monte Carlo and the lab's coloured portfolio draws;
`plans/vol-3.md:1627` (LM17's Leaves: drawdown statistics → LM32): §8. Not taken: `plans/vol-3.md:1543` lists LM32
among the users of (16.10), the correlation given an event; LM32 does not need it, and LM35's brief uses it in its §5
and E7 (O9, closed).

**Outcomes** ("After this module you should be able to:"; the level in brackets is the brief's, and the page keeps
AUTHORING §3's form, the level showing in the verb):

1. [D] derive the historical, normal and Student-t forms of VaR and ES from their definitions by the quantile function
2. [C] compute historical, normal, Student-t and Hill-tail VaR and ES, and diagnose what each model misses
3. [D] derive a quantile's distribution-free interval, compute its standard error, and explain why 250 returns are too few
4. [D] derive ES as a convex minimum, state the coherence axioms, and show VaR failing subadditivity
5. [C] turn EWMA and GARCH forecasts into VaR and ES, and compute how rare a loss is
6. [C] backtest VaR forecasts with exact binomial tests and Basel's traffic light, counting every test
7. [C] compute drawdowns from the peak and from initial wealth, and resample returns to test their order
8. [U] explain what the $\sqrt m$ rule, Basel's ES and the Brownian drawdown result assume, and choose a measure

Taught, practised, assessed (REVIEW_PROMPT item 10): 1 — §2, §3 (derivations, Deep Dive §3); E1, E3; Problems 2,
3, 5. 2 — §2, §3, §9; E2, E3; X3; Problems 1, 11; KC §9. 3 — §4; E5; Problem 6; KC §4. 4 — §5 (Deep Dive §5); E6;
Problems 7, 12 (a); KC §5 (its axiom question). 5 — §6; E7, E8; Problem 10; KC §6. 6 — §7; E9; Problems 8, 9; KC §7. 7 — §8; E10; Problem 4;
KC §8 (a), (c). 8 — §3, §5, §8; E4; KCs §3, §5, §8.

**Owns.** VaR and ES defined from the quantile of an $m$-day simple return at tail probability $u$, positive for a
loss, (32.1), with the continuous-case tail mean by (18.1); the historical estimators (32.2), $-R_{(j)}$ and Acerbi and
Tasche's tail mean of $\hat F$ (the book's one ES estimator, every later module uses it; decision D); normal VaR and
ES (32.3), derived from (15.6) and (5.11); Student-$t$ VaR and ES (32.4), derived; the moments each needs; Hill-tail
VaR and ES (one paragraph, Problem 11); the horizon $m$, the $\sqrt m$ rule and its conditions, the ten-session VaR of
TR23 (E4); the precision of a quantile: the distribution-free interval (32.5), the asymptotic SE (32.6) *stated
without proof*, iid and block bootstrap SEs, 250 returns; coherence (four axioms, Artzner et al. 1999),
subadditivity of normal VaR, a constructed portfolio where VaR fails it (E6), ES coherent (Acerbi and Tasche 2002,
*stated*), Rockafellar and Uryasev's minimum (32.7), derived, and the minimum-ES linear program (Problem 12, citing
LM29's (29.1) and (29.3)); ES at 97.5% against VaR at 99% (BCBS 2019, MAR33.3); filtered VaR and ES (32.8) from
LM26's forecasts; the ten-day Monte Carlo VaR under GARCH-t; how rare a loss is under a model, with importance
sampling (Problem 10);
backtesting: exceedances, the exact binomial coverage test, Basel's 1996 traffic light, an independence check by
LM21's exact count, twelve tests and Bonferroni, and Kupiec's and Christoffersen's likelihood ratios, named in §7's
two sentences on Kupiec (1995) and Christoffersen (1998) with a pointer to the lab, which computes them (decision E);
$\mathrm{DD}_t$ (LM1), MDD, the longest spell under water and
$\mathrm{DD}^0_t$ (32.9); the rules' VaR, ES and drawdowns; MDD under permutation and the stationary bootstrap, with
the bootstrap's atoms; the Brownian-motion expected maximum drawdown (32.10), *stated without proof* with its model.
Values owned: every A32 anchor except the echoes (TR23's sample, LM14's quantiles, LM15's and LM20's fits, LM26's
forecast SDs and 7 April's return (lm26.md:32), LM27's frames and its first-purchase cost A27-23, LM35's T5S closes
and lows of two days, A35-45), which are cited to their modules.

**Leaves.** The rules' Sharpe ratios, intervals and tests → LM33. Net wealth, log growth, turnover, costs → LM34 (the
drawdown criterion of the shared decision is LM32's). Each rule's loss on 7 April 2025 → LM35 (A35-13, a frozen book
without the day's interest; decision A1). Scenario replays without probabilities, limit locks, holidays,
the overnight gap → LM35 (LM32 says once that 7 April's return spans four non-trading days and that limits capped it).
Brownian motion → LM36; jump models → LM39; drawdown probabilities under a model, drawdown control and limits
(Busseti, Ryu and Boyd's bound is relative to initial wealth, guidance g:136) → LM44; Kelly sizing under a VaR or ES
limit → Volume VIII. Not in the book (one sentence each): backtests of ES, extreme value theory beyond Hill
(lm20.md:449), multivariate GARCH (shared decision), conditional drawdown measures. To the lab and problems (density,
g:60–63): Hill-tail VaR (Problem 11), importance sampling (Problem 10), the minimum-ES LP (Problem 12), a coloured
portfolio Monte Carlo, Kupiec's and Christoffersen's likelihood ratios beside LM21's exact tests (A32-56), intraday
log falls from T5S (per-day statistics), a 250-return backtest window (the extension).

**Uses before taught** (one sentence each in the text):

- §8: "Brownian motion, the continuous-time limit of a random walk, is [[LM36]]'s subject; (32.10) is stated here
  without proof, with its model."
- §6: "A move that no variance forecast anticipates is a jump, which [[LM39]] models."
- §8: "Choosing a position size so that drawdowns stay inside a limit is [[LM44]]'s subject."

**Data role.**

- **TR23** (Volume III), through `data/lm26_common.py`, which reads `data/processed/vol3_taiex.parquet` (built and
  checked by `data/vol3_series.py`; FinMind `TaiwanStockTotalReturnIndex`, data_id TAIEX, retrieved 18 October 2026)
  and the committed `data/derived/vol4_rv.csv`. $T=5{,}849$ simple returns of the total-return index, 3 January 2003
  → 8 October 2026, 23.7645 years (calendar days ÷ 365.25 from the close of 2 January 2003, the close before the
  first return), $A=246.12$ [A32-01] (lm19.md:46). Log returns $r_t=\ln(1+R_t)$, defined since every $R_t>-1$ (the
  minimum is −9.70%), in percent for EWMA and GARCH (LM26's units, lm26.md:47). 7 April 2025's return is LM26's (lm26.md:32); the script checks that it is the exact minimum, with
  `Fraction` on the two-decimal closes, and counts the four days without a session before it [A32-02].
- **LM26's forecasts** (`forecasts()`): window $\operatorname{round}(5A)=1{,}231$, GARCH(1,1) with normal and with $t$
  innovations refitted at each calendar month's first session (226 refits per law), EWMA 0.94 with zero mean;
  forecast days 2 January 2008 → 8 October 2026, $n=4{,}609$ [A32-04]. HS and N use the trailing 1,231 simple returns
  of each day (for 7 April 2025, 12 March 2020 → 2 April 2025); the $t$ model refits `scipy.stats.t.fit` on the 1,231
  returns before each month's first session (LM26's schedule; its fit of 1 April 2025 uses 10 March 2020 → 31 March
  2025) [A32-05]. The window is LM26's, fixed before LM32 (decision D).
- **E5's wealth frame and the rules** (Volume V): `vol5_series.frames("E5")` and `vol5_rules` (`signals`,
  `wealth_path`), recomputed and asserted equal to `data/processed/vol5_rules.parquet` [A32-03]. A rule's return is its
  net wealth ratio; the returns run from the session after the first trade, 1,851 sessions, 5 March 2019 → 8 October
  2026, 7.60 years (calendar days ÷ 365.25 from the first trade's close of 4 March 2019, the close before the first
  return) [A32-03; the counts echo LM28's A28-02 and A28-03]; the drawdown path starts at the cash of 1
  before the first purchase, as `summary()` does, so the first purchase's cost (0.142% for R1 and R2, LM27's A27-23,
  echoed in [A32-40]) is in it. No path reaches wealth ≤ 0 (asserted; guidance g:94). Problem 12 uses the through
  case's first window, the 504 rows of the estimation frame (joint dates) to 27 February 2019 [A32-24].
- **T5S** (Volume IV), lab only: three raw days under `data/raw/intraday/taiex5s/` (7 April 2025, 5 August 2024, 19
  March 2020), the TAIEX price index; 09:00:00 is the previous close (PITFALLS §3); every change is a log change from
  it (decision C7); per-day statistics only, never a path [A32-44]. The closes and lows of 7 April 2025 and 5 August
  2024 are LM35's (A35-45) and echoed; the falls from the running peak and 19 March 2020 are LM32's.
- **Constructed and hypothetical inputs:** E6's bonds [A32-22] and Problem 7's [A32-50]; Problem 4's wealth path
  [A32-48]; Problem 9's counts [A32-52]; the 20% drawdown limit of §8; the Brownian example's $\sigma=20\%$, ten years
  [A32-38]; Problem 2's five returns [A32-46], Problem 3's normal law [A32-47], Problem 8's count [A32-51] and KC
  §6's −4% log quantile [A32-29] (hypothetical).
- **Conventions.** VaR and ES are positive for a loss; $u$ is the tail probability, "99%" is $u=0.01$; one day unless
  $m$ is named; an $m$-day return compounds simple returns. Quantiles $\hat F^{-1}(u)=R_{(\lceil uT\rceil)}$
  (`method="inverted_cdf"`, passed explicitly). Historical ES (32.2). Normal: $\bar R$ and $s$ with divisor $T$
  (`ddof=0`). Student $t$: maximum likelihood on returns in percent, written in (15.11)'s form. Filtered models: (32.8)
  on $r$ in percent, mapped to $R$ by $e^{r/100}-1$. An exceedance is $R_t<-\operatorname{VaR}_t-10^{-12}$, and the smallest
  margin $\min_t\lvert R_t+\operatorname{VaR}_t\rvert$ is printed (0.011 percentage points for HS) [A32-31]. Coverage:
  one-sided exact binomial upper tail; independence: the count of exceedances followed by another against
  $\operatorname{Bin}(\text{trials},x/n)$ (LM21's exact form); Basel zones by BCBS (1996a)'s cumulative probabilities;
  the lab's likelihood ratios: Kupiec's $\mathrm{LR}_{\mathrm{uc}}$ on the 4,609 days, $\chi^2_1$; Christoffersen's
  $\mathrm{LR}_{\mathrm{ind}}$ ($\chi^2_1$, a first-order Markov chain on the 4,608 consecutive pairs, conditioning on
  the first day) and $\mathrm{LR}_{\mathrm{cc}}$ by its definition ($\chi^2_2$), which equals
  $\mathrm{LR}_{\mathrm{uc}}+\mathrm{LR}_{\mathrm{ind}}$ when the first day is ignored [A32-56]. Drawdowns in sessions;
  years are calendar days ÷ 365.25 from the close before a sample's first return (AUTHORING §8, decision C7), except a
  model's "once in so many years", which divides sessions by $A$ and says so. Every count against a threshold uses one
  guard.
- **Seeds** (one generator per experiment, `np.random.default_rng([e, 20261011])`, created once): 1 the ten-day GARCH-t
  Monte Carlo (100,000 paths; each of the ten steps draws all paths' innovations at once) [A32-28]; 2 importance
  sampling (10,000 draws) [A32-53]; 3 permutations of each rule's returns (10,000 per rule, rules in order) [A32-36]; 4
  the stationary bootstrap of each rule's returns (10,000 per rule, rules in order) [A32-37]; 5 and 6 the iid and
  stationary bootstrap of TR23's 1% quantile (10,000 each) [A32-20]; 7 ten iid sessions from TR23 (100,000 sums, each
  batch a 5,000 × 10 array of day indices) [A32-55]. Every stationary resample is drawn as LM22's `stationary_idx`
  (lm22.md:365–383), start days then uniforms, which equals arch's `StationaryBootstrap` (asserted on twin generators;
  shared decision "Counting, simulation"), one resample after another. Batch standard errors use 20 consecutive
  batches (divisor 20), as LM18. E8's split reuses experiment 1's draws for two deterministic variance paths (common
  random numbers, no new generator) [A32-57]. The widget does not simulate.
- **Published files** (Volume IV's X37 rule): no file carries a daily series in date order. X4 plots three models'
  $-\operatorname{VaR}$ thinned to weekly points plus every cited day, and the returns of exceedance days only (HS and
  GARCH-t, at most 133 dated points); X7 thins the drawdown paths to weekly points plus every cited peak, trough and
  recovery; X2 is a histogram; the widget embeds each rule's 186 worst returns sorted, without dates; no T5S value is
  published.
- **Scripts.** `data/lm32_numbers.py` (every printed value, asserted against `src/lm32.md`, compared with the anchors,
  rounding flags) and `data/lm32_charts.py` (X2, X4, X5, X7, X9 and the widget block); both after `data/vol3_series.py`,
  `data/vol5_series.py` and `data/vol5_rules.py` (and LM26's committed `vol4_rv.csv`). The anchors script runs in under a
  minute.

**Hygiene declaration.** *Out-of-sample:* the six models' one-day forecasts on 4,609 days, each from data before its
day, with LM26's window and refit schedule fixed before LM32, and the 7 April forecasts; the module runs 12 tests on
these forecasts (coverage and independence for six models) and corrects for them (§7); the lab adds Kupiec's and
Christoffersen's 18 likelihood ratios on the same forecasts and corrects for its 30 tests [A32-56]. *Out-of-sample
(fixed in advance, 2026-10-24):* the rules' returns, 5 March 2019 → 8 October 2026; their historical VaR, ES and
drawdowns describe that record for all eight rules, none selected; §8 also runs one permutation test of order
per rule on that record (eight tests, labelled below; none reaches 5%, the smallest share being R2's 557 of 10,000
[A32-36]). *In-sample:* TR23's full-sample normal, $t$ and
Hill fits; the rules' normal and $t$ fits (A32-41, A32-42); the SEs of experiments 5 and 6, and the resampled MDDs and
permutation tests of experiments 3 and 4 (each resamples the record it describes: their quantiles and counts are intervals and tests, which lm22.md:57 labels in-sample; no resampled path is shown); the minimum-ES portfolio of the first
window (Problem 12; an illustration outside the through case's family, so $n=8$ is unchanged). *Model:* experiments 1, 2 and 7,
the rarity of 7 April under each GARCH law, the Brownian result. *Constructed* and *hypothetical:* the bonds, Problem
4's path, Problem 9's counts, the 20% limit, Problem 2's returns, Problem 3's law, Problem 8's count, KC §6's quantile. *Descriptive:* TR23's full-sample historical VaR and ES and E4's overlapping sums; T5S per-day statistics (lab). Local note: "TAIEX forecasts
are out of sample: each day's value at risk uses only earlier returns, with the window and refits fixed before this
module. Sections 7 and 8 count their twelve and eight tests. The eight rules were fixed on 24 October 2026; their tail
and drawdown figures describe their out-of-sample record, 5 March 2019 to 8 October 2026, and all eight are reported.
Full-sample historical tails are descriptive; fits and resamples are in-sample; simulations are model results."

**Notation.** AUTHORING §6 (its $\alpha$, $k$ and $B$, $\ell$ rows scope LM32) and the shared table's "in LM32" row
(plans/vol-5.md:232: $\alpha$ the tail index, GARCH coefficients in
words, $k$ Hill's count, as §6's $k$ row now scopes it for LM20 and LM32, $\ell$ a block length, no log-likelihood).
Used: $R$, $r$ (in percent in LM26's models, lm26.md:47), $T$,
$t$, $A$, $A_{\mathrm w}$, $u$, $U$ (18.1), $m$, $n$, $j$, $R_{(j)}$, $f_R$ ((32.6)), $F_R$, $F_R^{-1}$, $\hat F$, $\hat F^{-1}$, $\E$,
$\Pr$, $\mathbf 1\{\cdot\}$, $\varphi$, $\Phi$, $\Phi^{-1}$, $\mu$, $\sigma$, $\bar R$, $s$, $\bar r$, $s_r$, $Z$,
$Y\sim t_\nu$ (a value $y$), $f_Y$, $F_Y^{-1}$, $\nu$, $\operatorname{Bin}(n,u)$, $\chi^2_1$, $\chi^2_2$ (§7's words and the lab), $\alpha$,
$\hat\alpha$, $k$, $x_0$ (LM20's), $g$,
$\sigma_{t+1\mid t}$, $\xi_t$ (LM26's), $\operatorname{SE}$, $B$, $\ell$, $W_t$, $W_0$, $\mathrm{DD}_t$, MDD,
$\mathrm{DD}^0_t$, $\mathbf w$, $\mathbf R_t$, $\sigma_p$, $L_t$ (R8's exposure, cited), $\tau$ (years in (32.10)), $\lambda$ (LM26's EWMA decay, 0.94, in X1; AUTHORING §6's $\lambda$ row).
Local symbols:

| Symbol | Meaning | Check |
|:--|:--|:--|
| $\operatorname{VaR}_u$, $\operatorname{ES}_u$ | (32.1), over $m$ days when $m$ is named; `\operatorname`, no macro | Portfolios table |
| $j=\lceil uT\rceil$; $j_1$, $j_2$ | the rank of the VaR order statistic; the ranks of (32.5) | §6's $j$, $R_{(j)}$; LM32 has no pmf index |
| $X$, $x$ | the count of exceedances and its value | a random variable; LM32 writes no data matrix (Problem 12 writes $\mathbf R_t$) |
| $n$ | forecast days of a backtest (4,609), the trials of $\operatorname{Bin}(n,u)$ | §6's $n$; Monte Carlo draws are written as numbers, not $n$ |
| $\theta$ | the threshold variable of (32.7) | §6's parameter $\theta$; LM32 has no angle and no other parameter symbol |
| $q$ | $F_Y^{-1}(u)$ in (32.4), the Deep Dive and Problem 5 | §6's $p$, $q$ row: LM32 has no bets and no dividend yield (as LM21's $q$) |
| $v$ | the variable of integration in (32.1) | §6's discount factor does not occur in LM32 |
| $a$ | the shift of (18.7)'s first line (Problem 10) | §6: a generic constant in a module without bets |
| $\mathcal R(\cdot)$ | a risk measure in the coherence axioms | new: Artzner et al.'s $\rho$ is the book's correlation (accepted, decision B5) |
| $R_1$, $R_2$ | the returns of two positions (E6's bonds) | asset index, as $R_{i,t}$ |
| $\eta$, $\zeta$ | the constants of the axioms (scale and shift) | LM5's letters (§6) |
| $F_\xi^{-1}(u)$ | the quantile of LM26's standardized innovation: $\Phi^{-1}(u)$, or $\sqrt{(\nu-2)/\nu}\,F_Y^{-1}(u)$ | subscripted; no $z_u$ |
| $\tau$ | years in (32.10) | §6: a span in years when $T$ is a count |
| $\mathrm{LR}_{\mathrm{uc}}$, $\mathrm{LR}_{\mathrm{ind}}$, $\mathrm{LR}_{\mathrm{cc}}$ | Kupiec's and Christoffersen's likelihood ratios (the lab; §7 names the ratios in words) | upright abbreviations, as PSR; no log-likelihood symbol ($\ell$ is the block length) |
| $n_{00}$, $n_{01}$, $n_{10}$, $n_{11}$; $\hat p$, $\hat p_{01}$, $\hat p_{11}$, $\hat p_2$ | the lab only: the 4,608 consecutive forecast-day pairs counted by the first day's and the second day's indicator (1 an exceedance); the rates $\hat p=x/n$, $\hat p_{01}=n_{01}/(n_{00}+n_{01})$, $\hat p_{11}=n_{11}/(n_{10}+n_{11})$, $\hat p_2=(n_{01}+n_{11})/(n-1)$. The lab writes the three ratios out in full in these, as A32-56 does, with no likelihood symbol | subscripted counts beside $n$; $p$ is $\operatorname{Bin}(n,p)$'s letter in a module without bets; Christoffersen's $\hat\pi$ is not used ($\pi$ is the constant in (32.10)); no $L$ (R8's exposure) and no $\mathcal L$ (§6's $B$, $\ell$ row: LM32 writes no likelihood) |

Not used: $\kappa$ (LM5's threshold; the condition number book-wide), $\alpha$ for a level, $\rho$ for a risk measure,
$L$ for a loss (R8's $L_t$; losses are $-R$), a Cholesky $L$ in the main text, $\gamma$ for Magdon-Ismail et al.'s
constant (book-wide a growth rate; (32.10) writes $\sqrt{\pi/2}$), $z_u$, $k$ for a number of standard deviations
(written in words; Problem 10 writes (18.7)'s first line with the shift $a$, a generic constant in a module without
bets, declared), $\hat\sigma_{t+1\mid t}$ (LM26 writes no hat; decision B1).

**Motivating case: "Did any model see 7 April coming?"** (box, about 165 words in three paragraphs of at most 80
words, decision C10; 12 sentences, the longest 20 words, mean under 14)

> Wednesday 2 April 2025 was the last session before the Qingming holiday. That evening six models forecast the next
> session's one-day 99% value at risk of the TAIEX total-return index. Their answers ran from 2.66% (a normal law on
> its last 1,231 returns) to 4.14% (GARCH with Student-t innovations) [A32-05]. The next session came after four days
> without trading [A32-02; the holiday's name, lm26.md:32].
>
> On Monday 7 April the index fell 9.70%, the worst of its 5,849 daily returns since 2003 [A32-02; lm26.md:32]. That
> loss was 2.3 to 3.6 times each model's value at risk, and 1.8 to 3.2 times its expected shortfall [A32-05, A32-54].
> Over the ten sessions from 7 April it lost 8.92% in all [A32-28]. It was also the worst day for seven of the eight
> allocation rules of the through case [A32-06]. What each rule lost is [[LM35]]'s replay.
>
> Was every model wrong, or was the day just rare? How precise is a 99% value at risk in the first place? And what
> does a one-day number say about the fall from a peak?

Resolved: (a) the models: §6, E7 (under GARCH-n the loss was a once-in-3.7-million-years day, under GARCH-t once in
32.6 years, years of TR23's 246.12 sessions [A32-27]) and §7 (every model counted it as an exceedance [A32-34]; over
4,609 days no model passes both tests at the Bonferroni level [A32-32]); (b) precision: §4 (the 1% quantile's SE is
0.145 points by (32.6) for iid days and 0.257 by the block bootstrap; from 250 returns it has no distribution-free
lower bound [A32-19, A32-20, A32-21]); (c) the path: §8 (the rules' maximum drawdowns run from 18.42% to 33.56%: R1's
fall ran from January to March 2020, the others' from peaks in January to March 2022 to troughs in October 2022, R4's
in March 2023 [A32-35]). The rules' losses on 7 April are cited from LM35 (A35-13), not printed as LM32's (decision
A1).
The case is the sample's extreme, and says so (AUTHORING §8): the ten-session figure is its multi-day check, and the
caption adds that the 10% limit capped many stocks that day (936 listed stocks closed limit-down; Atkinson (7 April
2025), TechNews, as lm13.md:592 and lm14.md:627 cite it), so the index return understates the selling.

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | the layer added: LM27's $\sigma_p$ measures typical risk, LM32 measures the tail and the path; case + X1; roadmap; notation and hygiene notes | 340 |
| 2 | Value at Risk and Expected Shortfall {1,2} | (32.1) at level $u$ and horizon $m$, positive for a loss, "99%" is $u=0.01$; the tail-mean form for continuous $F_R$ by (18.1); (32.2) from $\hat F$ (two-line derivation), equal to the mean of the $uT$ worst returns when $uT$ is whole; E1; X2; E2; LM5's (5.11) and LM15's tail mean are ES (lm05.md:509, lm15.md:469); pitfall: three ES estimators and NumPy's default quantile; 導讀; KC (50 returns) | 560 |
| 3 | Normal, Student-t and Tail Models {1,2,8} | (32.3) from (15.6) and (5.11); (32.4), the $t$'s tail integral derived (Deep Dive); X3; E3; the moments each measure needs (lm05.md:369); Hill-tail VaR and ES in one paragraph ((20.10); Problem 11); the horizon: the $\sqrt m$ rule, exact only for an $m$-day log return of iid normal days with zero mean ((19.7) gives its variance; a non-normal law changes the quantile's scaling, a mean adds $m$ times, and compounding to $e^r-1$ bends it), E4 (fat tails against the order of days); 導讀; KC ($\sqrt{10}$) | 600 |
| 4 | How Precise Is a Value at Risk? {3} | (32.5) derived ($R_{(j)}\le F_R^{-1}(u)$ exactly when at least $j$ returns lie at or below $F_R^{-1}(u)$, so the count $X\sim\operatorname{Bin}(T,u)$ fixes both ends), with A32-18's equal-tail ranks ($j_1$ the largest with $\Pr(X\le j_1-1)\le0.025$, $j_2$ the smallest with $\Pr(X\le j_2-1)\ge0.975$); (32.6) *stated without proof* (Glasserman 2003, (9.7)); E5 (TR23's 1% quantile and median; lm20.md:276); iid and block bootstrap SEs (LM22's tools; dependence doubles the SE); 250 returns, Basel's minimum of one year of observations; pitfall: a 99% VaR from 250 returns; KC (8.11%) | 480 |
| 5 | Coherence and Expected Shortfall {4,8} | a risk measure's four axioms (Artzner et al. 1999), definition box; normal VaR is subadditive for jointly normal returns and $u<\tfrac12$ ((16.4), (16.7): $\sigma_p\le\sigma_1+\sigma_2$); E6 (bonds); ES coherent (Acerbi and Tasche 2002, *stated*); (32.7) derived (Deep Dive: continuous $F$, then $\hat F$, A32-25); the LP of Problem 12 ([[LM29]]; its minimum exists and is unique here, a plug-in estimate); ES 97.5% against VaR 99% (BCBS 2019, MAR33.3); 導讀; KC | 520 |
| 6 | Value at Risk from Volatility Forecasts {5} | quantile equivariance and (32.8); LM26's forecasts into VaR and ES (lm26.md:183); E7 (the 2 April forecasts, VaR, ES, rarity); ten days: (26.4)'s mean reversion and the Monte Carlo of E8, with its split on the same draws; a portfolio by LM12's colouring in one sentence; importance sampling (18.7) for a tail probability, (18.5) and (18.6) in one sentence, Problem 10 (lm18.md:300); jumps → [[LM39]]; KC (log to simple) | 530 |
| 7 | Backtesting Value at Risk {6} | exceedances as Bernoulli($u$) under a correct model; the exact binomial count (LM21); E9 (Basel's table recomputed); X4, X5, X6a, X6b; independence by LM21's exact count (the book's own form); two sentences naming Kupiec (1995) and Christoffersen (1998) for the likelihood-ratio forms, and a pointer to the lab, which computes them; 12 tests and Bonferroni; the reading: HS has the right count but clusters; the filtered models cluster far less than HS, not rejected at the Bonferroni level, but exceed too often; 7 April; scoring a quantile against LM26's (26.8), (26.9); pitfall: the 4,609-day zones are Basel's probabilities applied, not Basel's table; 導讀; KC | 620 |
| 8 | Drawdowns of the Rules {7,8} | (32.9): $\mathrm{DD}_t$ (LM1), MDD, the longest spell, $\mathrm{DD}^0_t$; the two definitions (g:92); X7, X8a, X8b; E10 (R1's episode; R2's MDD against its $\mathrm{DD}^0$; R6 against R8 by ES and MDD); a hypothetical 20% limit; the path statistic: permutations and the stationary bootstrap, X9, the 2020 atoms; (32.10) stated with its model; pointers to [[LM33]], [[LM34]], [[LM35]], [[LM44]]; 導讀; KC | 640 |
| 9 | Risk Measures in Python {2} | `np.quantile(..., method="inverted_cdf")`; (32.2) as a function; `scipy.stats.t.fit`, `t.ppf`, `t.pdf`; `quad` for (32.4); the forecasts from LM26's code; cvxpy for Problem 12 with CLARABEL's tolerances; lab box | 160 |
| — | Summary (7) / Problems (12) / Solutions | | 130 / 400 / 500 |
| | **Total** | | **5,480** |

**Elements.** 10 examples (E1, E2 §2; E3, E4 §3; E5 §4; E6 §5; E7, E8 §6; E9 §7; E10 §8). Knowledge checks:

- §2: 50 returns at $u=1\%$ give $j=\lceil0.5\rceil=1$, so the historical VaR and ES are both the worst return
  [A32-12]: a short sample sees nothing beyond its worst day.
- §3: TR23's ten-session 99% VaR is 10.49% from 5,840 overlapping sums, against $\sqrt{10}$ times the one-day 3.567%
  [A32-11], 11.28% [A32-16]. What does the $\sqrt m$ rule assume, and which way does each failure push? (Fat tails that
  average out and a positive mean push the true value down; dependence between days pushes it up, the real order
  of days in E4 and GARCH's variance feedback in E8.)
- §4: with 250 iid returns, the chance that none falls below the true 1% quantile is $0.99^{250}=8.11\%$ [A32-21],
  the first cell of Basel's Table 2; so no order statistic is a 95% lower bound for the 1% quantile.
- §5: under a normal law with zero mean, ES at 2.5% is $2.338\sigma$ and VaR at 1% is $2.326\sigma$ (ratio 1.005) [A32-23]. Why could
  Basel switch measures without changing the normal case's capital, and why does the switch bite on TR23 (ES at 2.5%
  ÷ VaR at 1%, X3: historical 1.05, $t$ 1.11)? Which of the four axioms does E6's VaR break, and does ES keep it
  there? (Subadditivity: 29.00% against the halves' −2.00%; ES keeps it, 29.20% against 47.60% [A32-22].)
- §6: a 1% quantile of $-4\%$ for the log return is $e^{-0.04}-1=-3.92\%$ for the simple return [A32-29]. Quantiles
  pass through an increasing map; why does the same step not give the ES?
- §7: HS's 56 exceedances against 46.09 expected; the binomial SD is 6.75, so $z=1.47$ [A32-33]. The count passes;
  what does the count not test?
- §8: (a) R2's MDD is 22.97% but its largest loss from the starting capital is 0.39%, on 8 March 2019 [A32-40],
  0.142 points of it the purchase cost (LM27's A27-23). Which number answers an investor who started in March 2019?
  (b) (32.10) gives 0.793 for $\sigma=20\%$ over ten years [A32-38]; which of its assumptions does R1 break?
  (c) 557 of 10,000 permutations of R2's returns reach its MDD of 22.97% [A32-36]: is R2's order of days unusual at
  the 5% level, and what does a permutation keep? (No, 5.57%; it keeps the returns and destroys their order.)
- §9: `np.quantile(R, 0.01)` gives −3.5668% by default and −3.5671% with `inverted_cdf` [A32-43].

§7's words on the likelihood ratios (decision E as amended and the second source hunt: the papers at section level,
in the versions read, no page or equation; two sentences and a pointer to the lab, which alone states the relabelling
of Christoffersen's indicator, by the decision on the third revision): "Kupiec (1995; §IV of its Federal Reserve
working paper) tests the same count with a likelihood ratio, two-sided and asymptotically $\chi^2_1$. Christoffersen
(1998; §3 of the author's manuscript) adds a ratio for independence, against exceedances whose chance depends on the day
before (a first-order Markov chain), and a joint one ($\chi^2_2$). The lab computes all three beside the exact tests."

中文導讀 in §2 (風險值 (value at risk), 預期短缺 (expected shortfall), 分位數 (quantile), 順序統計量 (order
statistic), 歷史模擬法 (historical simulation)), §3 (厚尾 (fat tails), 尾部風險 (tail risk), the $\sqrt m$ rule),
§5 (一致性風險量數 (coherent risk measure), 劣可加性 (subadditivity; the shared list, decision C1), 條件風險值
(CVaR), named once as ES's other name), §7 (回測 (backtest), 二項分布 (binomial distribution), 獨立性檢定 (independence test)), §8 (回撤 (drawdown),
最大回撤 (maximum drawdown), 排列檢定 (permutation test; decision on the Chinese terms), 區塊自助重抽法 (block
bootstrap)). Deep Dives: §3 "The
Student-t tail mean": $\frac{d}{dy}(1+y^2/\nu)^{-(\nu-1)/2}=-\frac{\nu-1}{\nu}\,y\,(1+y^2/\nu)^{-(\nu+1)/2}$, so
$\int_{-\infty}^{q}y\,f_Y(y)\,dy=-\frac{\nu+q^2}{\nu-1}f_Y(q)$ for $\nu>1$, checked by quadrature [A32-15]. §5 "Why the
minimum is the expected shortfall": for continuous $F_R$ the function of (32.7) is convex with derivative
$1-\Pr(-R>\theta)/u$, zero at $\theta=\operatorname{VaR}_u$, where its value is $\operatorname{ES}_u$
(Rockafellar and Uryasev 2000, Theorem 1 of their 1999 working paper); for $\hat F$ it is piecewise linear with kinks
at the losses $-R_t$, its slope $1-\#\{t:-R_t>\theta\}/(uT)$ changes sign at the $j$th largest loss (when $uT$ is
whole it is zero between the $(j+1)$th and the $j$th largest losses, and every $\theta$ there attains the minimum), and
its value there is (32.2) (TR23: 4.689% at 3.567% [A32-25]). A loss is written $-R_t$, never $L_t$ (R8's exposure; decision on
the cross-check, Y7).

**Exhibits.**

- X1 `case` (table, §1): "7 April 2025 against the forecasts of 2 April". Rows: historical (the 1,231 returns 12 March
  2020 → 2 April 2025), normal (same window), Student $t$ (the fit of 1 April on the 1,231 returns to 31 March), EWMA
  ($\lambda=0.94$), GARCH normal, GARCH $t$. Columns: 99% VaR (%) 3.53, 2.66, 3.08, 3.57, 3.83, 4.14 [A32-05]; 99% ES
  (%) 4.58, 3.06, 4.38, 4.07, 4.39, 5.26 [A32-54]; loss ÷ VaR 2.75, 3.65, 3.15, 2.72, 2.53, 2.34 [A32-05] (two
  decimals, so that each follows from the printed 9.70 and VaR); "one day in" (GARCH rows only) 3.7 million years
  and 32.6 years [A32-27]. Foot rows: the loss 9.70% (log −10.20%; lm26.md:32); ten sessions 7–18 April −8.92%
  [A32-28]. Note: forecasts from data through 2 April, out of sample; TAIEX total-return
  index; "years" are TR23's 246.12 sessions; the return spans four non-trading days, and the 10% limit capped many
  stocks; the eight rules' losses that day are [[LM35]]'s replay (A35-13). Source: FinMind
  `TaiwanStockTotalReturnIndex`, retrieved 18 October 2026; LM26's forecasts. Computations: `data/lm32_numbers.py`.
- X2 `tail` (line, `step: true`, §2): the lowest 5% of TR23's returns (the 293 worst [A32-11]) as a histogram of
  losses, bins of 0.25 points from 1.75% to 10.00%, $x$ the loss in % (`fmt: "n2"`), $y$ days. Solid `vline`s at the
  historical VaR 3.57% and ES 4.69%; dashed at the normal's 2.75% and 3.16% [A32-11, A32-13]. Note: the 59 worst days
  lie at or beyond the VaR; ES averages them, weighting the 59th by (32.2). Descriptive, full sample (*In-sample* for
  the normal lines).
- X3 `models` (table, §3): TR23 at $u=$ 0.1%, 1%, 2.5%: historical VaR, ES (32.2) and the mean of the $j$ worst
  (6.31, 7.36, 7.33; 3.57, 4.69, 4.68; 2.65, 3.74, 3.73) [A32-11]; normal (3.67, 4.01; 2.75, 3.16; 2.31, 2.76) [A32-13];
  Student $t$ (7.58, 11.37; 3.37, 5.19; 2.34, 3.73) [A32-14]; Hill at 0.1% and 1% (6.69, 9.23; 3.55, 4.90) [A32-17].
  Note: in-sample fits; the $t$ is LM15's and LM20's ($\nu=3.065$), its cells from the unrounded fit (E3's rounded parameters change the 0.1% ES's last digit); Hill on the 108 losses of 3% or more, valid for
  $u\le k/T$; the historical 0.1% figures rest on six days. Point estimates: E5 gives the 1% quantile's SE (0.145
  points for iid days, 0.257 with blocks [A32-19, A32-20]); the other cells carry none, since §4's methods apply to
  each unchanged.
- X4 `rollvar` (line, date, §7): $-\operatorname{VaR}$ of historical (1), GARCH-t (2) and normal (3), 2 January 2008
  → 8 October 2026, weekly points plus every cited day; `point` annotations for the exceedance days' returns of HS and
  GARCH-t (56 and 77 [A32-31]) and a labelled point "7 Apr 2025" at −9.70% with the three forecasts −3.53, −4.14 and
  −2.66 [A32-05]. Note: out of sample; the X37 thinning; counts 56, 77, 110 against 46.09 expected [A32-31, A32-04].
- X5 `zones` (`bar`, §7): six models' exceedances 56, 110, 69, 103, 102, 77 (`valueLabels`) [A32-31]; dashed `hline`
  "expected 46.09" [A32-04]; `hline`s "yellow from 57" and "red from 73" [A32-30]. Note: the zones are Basel's 1996
  probabilities (95% and 99.99%) applied to 4,609 days, not Basel's 250-day table.
- X6a `coverage` (table, §7; split from the first plan's ten-column table so that no PDF page shrinks, decision C10):
  rows the six models; five columns: exceedances, their rate, $\Pr(X\ge x)$, zone, mean VaR (HS 56, 1.22%, 0.085,
  green, 3.24%; N 110, 2.39%, $6.5\times10^{-16}$, red, 2.58%; t 69, 1.50%, $9.1\times10^{-4}$, yellow, 3.09%; EWMA 103,
  2.23%, $2.7\times10^{-13}$, red, 2.51%; GARCH-n 102, 2.21%, $6.2\times10^{-13}$, red, 2.43%; GARCH-t 77, 1.67%,
  $1.8\times10^{-5}$, red, 2.66%) [A32-31]. Note: out of sample, 4,609 days, 46.09 expected; zones by Basel's 1996
  probabilities applied to 4,609 days [A32-30].
- X6b `clusters` (table, §7): rows the six models; five columns: exceedances followed by another, of those with a next
  forecast day (9 of 56, 15 of 110, 12 of 69, 6 of 103, 6 of 102, 5 of 77), expected under independence (0.68, 2.63,
  1.03, 2.30, 2.26, 1.29), p-value ($2.6\times10^{-8}$, $6.4\times10^{-8}$, $5.1\times10^{-10}$, 0.028, 0.026, 0.0095),
  shares of 250-day windows in Basel's yellow and red (20.0 and 3.4%; 32.2 and 17.0%; 21.8 and 9.5%; 70.8 and 0.4%;
  60.6 and 2.9%; 43.2 and 0.4%), the most in one window (12, 27, 16, 10, 11, 10) [A32-31]; a foot row: the Bonferroni
  level 0.0042, rejecting coverage for N, t, EWMA, GARCH-n and GARCH-t and independence for HS, N and t [A32-32]. Note:
  out of sample, 12 tests on the same forecasts; overlapping windows are dependent, so their shares are descriptive;
  each maximum is first reached in the window ending 8 January 2009 (HS, N, t; N again in June 2009), 18 October 2010
  (EWMA; again in March 2020 and March 2022), 25 April 2022 (GARCH-n) or 7 April 2025 (GARCH-t), and 7 to 19
  windows tie at it [A32-31].
- X7 `underwater` (line, date, §8): $-\mathrm{DD}_t$ of R1 (1), R3 (2), R6 (3) and R8 (4), 4 March 2019 → 8 October 2026,
  weekly points plus every cited peak, trough and recovery; points at the troughs R1 −23.19% (19 Mar 2020), R3 −19.11%,
  R6 −18.90%, R8 −18.42% (21 Oct 2022) [A32-35]; a dashed `hline` at −20% "hypothetical 20% limit". Note: the chart
  plots $-\mathrm{DD}_t$ (AUTHORING §6); out of sample, net of costs, fixed in advance; R2, R4, R5 and R7 are in X8b.
- X8a `rulestail` (table, §8; the first plan's twelve-column table is split in two, decision C10): rows R1–R8; four
  columns: historical VaR 1%, ES 1% and ES 2.5% [A32-07], normal VaR 1% [A32-41]. Note: the rules' out-of-sample net
  returns, 1,851 sessions, 5 March 2019 → 8 October 2026; the normal column is *In-sample*; each rule's worst day was 7
  April 2025, except R7's, 19 March 2020 [A32-06], and what each lost that day is [[LM35]]'s (A35-13); Sharpe ratios
  are LM33's and net wealth LM34's; each figure is a point estimate from 1,851 returns, without a standard error (§4's
  methods apply; the 1% figures rest on 19 days [A32-07]).
- X8b `rulesdd` (table, §8): rows R1–R8; four columns: MDD, the longest spell under water (sessions below the peak; 484–733), max
  $\mathrm{DD}^0$, $\mathrm{DD}_t$ on 8 October 2026 [A32-35]. Note: the dates, kept out of the columns: each MDD's
  peak → trough → back, the longest spells' peaks and ends, and the dates of max $\mathrm{DD}^0$ (R3, R5, R7 and R8 on 5
  March 2019, their first day, chiefly the purchase cost) [A32-35]; paths from the cash of 1 before the first purchase.
- X9 `mddboot` (`scatter`, forest plot, §8): $y$ = R1–R8 (`ticks` 1–8 with `tickLabels`); $x$ MDD in % (`fmt:
  "n1"`). For each rule an unnamed thin grey `lines` entry for the permutation 5–95% range and a thick one for the
  stationary bootstrap's [A32-36, A32-37]; named point series "realized MDD" [A32-35], "permutation median" and
  "bootstrap median". Values cited: R1 23.19 [A32-35] against the medians 17.2 and 20.7; resampled MDDs at or above
  the realized one, 1,069 and 3,305 of 10,000; R2's 557 under permutation [A32-36, A32-37] (printed as counts: as
  percentages at one decimal several are exact ties). Note: experiments 3 and 4, 10,000 resamples each (*In-sample*: each resamples the record it describes); the stationary
  bootstrap in LM22's draw order, block lengths 17–22 by LM22's rule (decision D); in 399 to 1,737 of the 10,000
  bootstrap resamples, by rule, one realized fall into 19 March 2020 (from 21 February, 24 February or 9 March) sits
  whole in one block and is the resample's MDD, so the bootstrap distribution has an atom, and R5's and R6's medians
  sit on it; 223 of R1's 3,305 equal its realized MDD exactly (a block that holds the whole fall of 6 January → 19
  March 2020 rebuilds it) [A32-37].

**Widget `varLevel` — "VaR and ES of a rule at any level."** `Book.controls`: rule (select, R1–R8), tail probability
$u$ (slider, 0.1% to 10.0% in steps of 0.1%). Chart: `bar`, categories "historical", "normal", "Student t"; series
"VaR" and "ES" (two colours). Readouts: $j=\lceil1851u\rceil$, the $j$th worst return, ES ÷ VaR for each method, the
fitted $\nu$. Computation: historical by (32.2) from the embedded 186 worst returns of each rule (enough for $u\le10\%$:
$\lceil0.1\cdot1851\rceil=186$ [A32-42]); normal by (32.3) with each rule's mean and $s$ (`Book.dist.PhiInv`,
`Book.dist.phi`); Student $t$ by (32.4) with an embedded grid of $F_Y^{-1}(u)$ for each rule's $\nu$ (100 values per
rule; `Book.dist.tInv` was not approved) and `Book.dist.tPdf`. Module-local code under 30 lines, tested against Python
as `data/lm15_charts.py` does. Initial state (PDF): R1 at 1%: historical 2.10 / 3.38, normal 1.80 / 2.08, $t$ 2.05 /
3.07 [A32-42]. Data block `chart-lm32-varLevel` from `data/lm32_charts.py`: 8 × 186 sorted returns without dates, means,
SDs, $t$ parameters and quantile grids (about 30 KB). No simulation.

**Examples** (results recomputed from the printed inputs):

- E1 §2 `five`, LM18's returns +1.2, −0.8, +0.3, −2.5, +0.6% (lm22.md:75) at $u=0.3$ (large, so that the hand work
  shows the formula): $j=\lceil1.5\rceil=2$, $\operatorname{VaR}=-R_{(2)}=0.80\%$; (32.2):
  $-\frac{1}{0.3}\big[\frac{-2.5}{5}+(0.3-\tfrac15)(-0.8)\big]=1.93\%$; the mean of the two worst 1.65%, and the
  floor-count estimator of Acerbi and Tasche (2002b), $\lfloor uT\rfloor=1$ return, 2.50% [A32-10]. Three readings of
  one quantity spread from 1.65% to 2.50% in a tiny sample; (32.2) is the ES of $\hat F$ itself.
- E2 §2 `tr23hist`, TR23 at four levels (X3's first block): at 1%, $j=59$, VaR 3.567% (LM14's), ES 4.69% against 4.68%
  for the mean of the 59 worst; at 0.1%, $j=6$, 6.313% and 7.36%; at 2.5%, $j=147$, 2.65% and 3.74%; at 5%, $j=293$,
  1.86% and 2.97% [A32-11]. ES ÷ VaR is 1.31 at 1% and 1.41 at 2.5% [A32-12]: ES adds about a third to VaR here.
- E3 §3 `normt`, TR23 at 1% by (32.3) and (32.4): the normal ($\bar R=0.0625\%$, $s=1.2084\%$) gives VaR 2.75% and ES
  3.16% [A32-13], the $t$ ($\nu=3.065$, location 0.0997%, scale 0.7761%, LM20's fit; the scale is (32.4)'s
  $\sigma\sqrt{(\nu-2)/\nu}$ and is used directly, since the SD rounded to 1.317% changes the ES's last digit) 3.37%
  and 5.19% [A32-14], the data 3.57% and
  4.69% [A32-11]. The normal misses both; the $t$ comes close on VaR but overshoots ES, "too heavy from −5%"
  (lm15.md:461). (32.4) agrees with quadrature to better than 1e-12 [A32-15].
- E4 §3 `horizon`, ten sessions of TR23: 5,840 overlapping compound returns give a 99% VaR of 10.49%; $\sqrt{10}$
  times the one-day VaR gives 11.28%; iid normal log returns give 8.02% [A32-16]; ten days drawn independently from
  TR23's own returns give 8.75% (experiment 7, 100,000 sums, batch SE 0.04) [A32-55]. The daily law's non-normal
  shape (fat tails and skewness, not separated here) raises the iid figure from 8.02% to 8.75%; keeping the real order
  of days, with its serial dependence (volatility clustering among it, not separated here), raises it to 10.49%. The $\sqrt{10}$ rule scales a fat-tailed one-day quantile, while
  a sum of ten iid days is already close to its normal counterpart (8.75% against 8.02%), so the rule overstates. R1
  over 20 sessions: 8.66% against $\sqrt{20}$ times its one-day 2.102% [A32-07], 9.40% [A32-09]. Neighbouring
  overlapping sums share nine of their ten days, so 10.49% is itself imprecise; the text says so.
- E5 §4 `precision`, TR23's 1% quantile $R_{(59)}=-3.567\%$: by (32.5) the equal-tail ranks 44 and 75 give −4.016% to −3.425%
  with coverage 0.9587 [A32-18]; (32.6) with the spacing density gives an SE of 0.145 points [A32-19], against the exact
  interval's 0.151 (half its width ÷ 1.96) [A32-18]: at 5,849 days "large $T$" holds and the two nearly agree, while at
  250 returns the interval has no lower end [A32-21]; the iid
  bootstrap 0.119 (batch SE 0.0014) and the stationary bootstrap with $\ell=145$, in LM22's draw order, 0.257
  (0.0019), 2.2 times as large [A32-20]. The median (lm20.md:276): $R_{(2925)}=0.0879\%$, interval 0.069% to
  0.114% (ranks 2,850 and 3,000, coverage 0.9502) [A32-18], SE 0.0116 points against LM20's location SE 0.0124
  (lm20.md:269) [A32-19]. (32.5) assumes iid days; the block bootstrap says dependence more than doubles the
  uncertainty of a tail quantile.
- E6 §5 `bonds` (*constructed*): two independent bonds, each losing 60% with probability 0.8% and gaining 2% otherwise.
  At $u=1\%$ one bond's VaR is −2.00% (a gain, since default is rarer than 1%) and its ES 47.60%. Half in each: some
  default has probability 1.59%, above 1%, so the VaR is 29.00% while the halves' VaRs sum to −2.00%; the ES is 29.20%,
  below 47.60% [A32-22]. Diversifying raised VaR and lowered ES.
- E7 §6 `filtered`, the forecasts for 7 April made on 2 April (LM26's): $\sigma_{t+1\mid t}$ 1.5605% (EWMA), 1.7222%
  (GARCH-n), 1.7040% (GARCH-t) a day [A32-26] (lm26.md:39); with the refits' means 0.1020% and 0.1190% and $\nu=6.39$
  [A32-26], (32.8) gives VaR 3.57%, 3.83% and 4.14% [A32-05], and ES 4.07%, 4.39% and 5.26% [A32-54]. The day's log
  return −10.20% (lm26.md:32) lies $-5.98$ forecast SDs from the refit's mean under GARCH-n (lm26.md:32's 5.9 divides the return itself by 1.7222), probability $1.1\times10^{-9}$, once in 3.7 million
  years. Under GARCH-t it is $-6.06$, probability $1.2\times10^{-4}$, once in 8,014 sessions, 32.6 years, both
  from the unrounded fit and probability [A32-27]. A year
  here is TR23's 246.12 sessions (decision C7). Both are *Model* statements: the law's tail, not the data, decides
  the answer.
- E8 §6 `mc10`, ten days under GARCH-t from 2 April (experiment 1, 100,000 paths, the 1 April refit, innovations scaled
  to variance 1, each step drawn for all paths at once, batches of 5,000 consecutive paths): the ten-day 99% VaR is
  10.5% (batch SE 0.07 points) against $\sqrt{10}$ times the one-day 4.142% [A32-05], 13.10%; the realized ten
  sessions lost 8.92% [A32-28]. Two runs on experiment 1's own draws (common random numbers) split the gap
  [A32-57]. Ten days at the constant $\sigma_{t+1\mid t}=1.7040\%$ [A32-26] give 10.9% (batch SE 0.05), 2.2 points
  below 13.10%. The rule scales the whole one-day loss by $\sqrt{10}$, while ten days add the mean ten times and
  average their $t$ innovations (E4's effect). This run does not separate these effects. (26.4)'s deterministic path toward
  the fit's unconditional 1.116% a day [A32-26] gives 9.9% (0.06): mean reversion takes one point more. The
  variance's random feedback in the full model adds 0.6 back (batch SE of the difference 0.04), to 10.5%.
- E9 §7 `basel`: Basel's Table 2 recomputed: for 250 days at 99%, $\Pr(X\le x)$ is 8.11, 28.58, 54.32, 75.81, 89.22%
  for 0–4 and 95.88% at 5, so yellow starts at 5 and red at 10 (99.99%) [A32-30], every cell as BCBS (1996a) prints it.
  The same rule gives 9 and 15 for 500 days and 57 and 73 for 4,609 [A32-30]. HS's 56 exceedances are green,
  $\Pr(X\ge56)=0.085$; the $t$'s 69 yellow; the other four red [A32-31].
- E10 §8 `r1dd`, R1's path: MDD 23.19%, from the peak of 6 January 2020 to the trough of 19 March 2020 (45 sessions)
  and back on 13 January 2021 (205 more); its longest spell under water is another episode, 484 sessions below the peak of 7 March
  2022, back at it on 5 March 2024; its largest loss from the start is 10.24%, on 19 March 2020 [A32-08]; recovering the MDD needed
  +30.19% (1.17) [A32-40]. Permuting R1's 1,851 returns 10,000 times (experiment 3) gives a median MDD of 17.2%,
  and 1,069 permutations reach 23.19% [A32-36]. The stationary bootstrap, which keeps blocks of days, gives 20.7% and
  3,305 [A32-37]. R2's MDD is 22.97% (2022), but its loss from the start never exceeded 0.39%, reached on 8
  March 2019, its first week [A32-40, A32-35]; 0.142 points of it is the purchase cost (LM27's A27-23). The two
  definitions answer different investors. R6 against R8, its volatility-scaled version (LM31's): R8's 1% ES is higher
  (3.16% against 2.86%), yet its MDD is lower (18.42% against 18.90%) [A32-39], so the one-day tail and the path rank
  the two rules in opposite orders. Their losses on 7 April are [[LM35]]'s (A35-13; decision A1).

**Problems plan** (12; MC keys C, A, B, A, B, C; the lab solves 6–12). Stems state the sample or the
hypothetical inputs, the tail probability and horizon, the quantile rule ($\hat F^{-1}(u)=R_{(\lceil uT\rceil)}$), the
ES estimator (32.2), divisors, the drawdown definition (from the running peak including $W_0$), the test and its level,
the seed and draws, and the rounding; problem 12 states the window, the feasible set, the solver and its tolerances,
and the label *In-sample*.

1. MC: $T=250$ daily returns, $u=1\%$, the book's rule; which order statistic is the historical VaR? A $R_{(2)}$
   ($\lfloor uT\rfloor$). B halfway between $R_{(2)}$ and $R_{(3)}$ (interpolating at 2.5). **C** $R_{(3)}$ [A32-45].
2. MC: $T=180$, $u=2.5\%$, the five worst returns −6.1, −4.8, −4.2, −3.7, −3.3%; ES by (32.2). **A** 4.544%. B 4.42%
   (the mean of the $\lceil uT\rceil=5$ worst). C 4.70% (the mean of the $\lfloor uT\rfloor=4$ worst) [A32-46].
3. MC: normal, $\mu=0.05\%$, $\sigma=1.2\%$ a day, $u=1\%$, one day; ES. A 2.742% (the VaR). **B** 3.148%. C 3.248%
   (the mean's sign reversed) [A32-47].
4. MC: hypothetical wealth 1.00, 1.08, 1.02, 0.90, 0.95, 1.10, 1.04, 1.12 ($W_0=1$); MDD. **A** 16.67%. B 10.0% (the
   largest loss from $W_0$). C 20.00% (the recovery gain (1.17) at the MDD) [A32-48]. The solution lists every
   $\mathrm{DD}_t$ (0, 0, 5.56, 16.67, 12.04, 0, 5.45, 0%).
5. Derive (32.4) for $R=\mu+\sigma\sqrt{(\nu-2)/\nu}\,Y$, $Y\sim t_\nu$, $\nu>2$: show
   $\int_{-\infty}^{q}y\,f_Y(y)\,dy=-(\nu+q^2)f_Y(q)/(\nu-1)$, then check it on TR23's fit at 1% (5.19%) [A32-14,
   A32-15].
6. Derive (32.5) for iid returns with a continuous distribution function; for $T=1{,}000$ and $u=1\%$ find the
   equal-tail 95% ranks of §4 ($j_1$ the largest rank with $\Pr(X\le j_1-1)\le0.025$, $j_2$ the smallest with
   $\Pr(X\le j_2-1)\ge0.975$, $X\sim\operatorname{Bin}(T,u)$) and the coverage: 4 and 18, 0.9761, around the point $R_{(10)}$ [A32-49]. Python part: the ranks by
   `scipy.stats.binom`.
7. MC (*constructed*): two independent bonds, each −60% with probability 4% and +2% otherwise, $u=5\%$; the VaR of
   half in each. A −2.00% (the halves' VaRs summed). **B** 29.00%. C 47.60% (one bond's ES) [A32-50]. The solution adds
   one bond's VaR −2.00% and ES 47.60%, some default 7.84%, and the mixture's ES 29.99%.
8. MC: Basel's rule applied to 500 days of 99% VaR with 9 exceedances; the zone. A green (because
   $\Pr(X\ge9)=0.0671$ exceeds 5%). B red. **C** yellow [A32-51]. The solution: yellow starts where
   $\Pr(X\le x)\ge95\%$ (0.9689 at 9), one count before a one-sided 5% test would reject; red from 15.
9. Hypothetical: 2,000 days, 60 exceedances, 59 with a next day, 6 of them followed by another. Find the expected
   count under independence (1.77) and the exact p-value $\Pr(\operatorname{Bin}(59,0.03)\ge6)=0.0084$ [A32-52]; is it
   significant at 5% alone, and at the Bonferroni level of twelve tests, 0.0042 [A32-32]?
10. Python, importance sampling (experiment 2, `default_rng([2, 20261011])`, 10,000 draws): estimate
    $\Phi(-a)$ for $a=5.9836$, 7 April's GARCH-n value, by (18.7)'s first line with $h=\mathbf 1\{\cdot\}$:
    $(1.15\pm0.03)\times10^{-9}$ (the draws are `standard_normal(10_000)`) against the exact $1.091\times10^{-9}$; plain draws would expect
    0.000011 tail draws, the shifted ones get 4,927, and the variance falls by a factor $1.34\times10^8$ [A32-53].
11. Python, Hill-tail VaR (LM20's $x_0=3\%$, $k=108$): $\hat\alpha=3.634$ (LM20's 3.63, lm20.md:441, to the third decimal that the 0.1% figures need; decision C12); VaR and ES at 1% 3.55% and 4.90%, at 0.1%
    6.69% and 9.23%, against the historical 3.57%, 4.69%, 6.31%, 7.36% [A32-17]; why $u$ must stay below $k/T$.
12. Minimum ES (*In-sample*, citing LM29's (29.1) and (29.3)). (a) Show that for fixed $\mathbf w$ the objective of (32.7)
    under $\hat F$ is minimized at the $j$th largest loss, $j=\lceil uT\rceil$, with value (32.2) (the Deep Dive's
    argument). (b) Python: on the through case's first window (the 504
    rows of the estimation frame, joint dates 13 February 2017 → 27 February 2019), $u=2.5\%$, long-only weights
    summing to 1, solve (32.7) as a linear program in cvxpy with CLARABEL (tolerances 1e-12) and check with HiGHS:
    weights 0.078, 0.203, 0.398, 0.290, 0.030 (rounded; their sum prints as 0.999), ES 0.857%, $\theta^*=0.693\%$ =
    VaR; R3's ES 0.880% and R1's 1.303% on the same rows [A32-24]. The stem and solution say that the minimum exists
    (the weights lie in the simplex, and for fixed $\mathbf w$ the objective grows without bound as
    $\lvert\theta\rvert\to\infty$) and is unique here (within $10^{-9}$ of the minimum no weight moves by more than $10^{-7}$,
    and HiGHS's solution equals CLARABEL's), that the inputs are daily returns in percent, so the KKT residuals are
    printed (below $10^{-12}$), and that the weights are plug-in estimates whose error is not measured [A32-24].

**Lab parts** (`build/make_lab32.py`; reads only its `data/`: `taiex_tr.csv` (TR23, as LM23's lab), and the derived
files `data/make_lab_data.py` builds from `data/raw/` under the shared decision "Labs" (decision C6): the wealth frame
with its traded flags, the estimation frame (Problem 12's window), the rules' per-date targets (R3's first target,
for Problem 12's R3 ES of 0.880%), the eight rules' net wealth paths and the three raw T5S days; the lab refits LM26's two GARCH laws and runs its EWMA
on `taiex_tr.csv` itself, as Lab 26 does, for each day's $\sigma_{t+1\mid t}$, each refit's constant mean and the $t$
refit's $\nu$, since LM26's forecast series hold variances only): 1 data, conventions, the sample counts; 2 historical VaR and ES, (32.2)
against the two count means, E1, E2, X2, `np.quantile`'s methods; 3 normal, $t$ and Hill (Problem 11), (32.4) by
quadrature, E4 with experiment 7; 4 precision: (32.5), (32.6), experiments 5 and 6 (E5), Problem 6; 5 coherence: E6 and
Problem 7 exactly, (32.7) on TR23, Problem 12; 6 filtered VaR and ES: E7, A32-54's quadrature, E8 (experiment 1) and its
split on the same draws [A32-57], Problem 10 (experiment 2), a portfolio VaR by colouring with LM12's Cholesky factor,
checked against (32.3) with $\sigma_p$; 7 backtests: X4–X6b, E9, Problems 8 and 9, and Kupiec's
$\mathrm{LR}_{\mathrm{uc}}$ with Christoffersen's $\mathrm{LR}_{\mathrm{ind}}$ and $\mathrm{LR}_{\mathrm{cc}}$ for the
six models beside LM21's exact tests [A32-56]. HS's count passes ($\mathrm{LR}_{\mathrm{uc}}=2.01$, p-value 0.16,
two-sided where the exact test is one-sided). At the Bonferroni level of the lab's 30 tests (the 12 exact and the 18
ratios), 0.0017, $\mathrm{LR}_{\mathrm{uc}}$ rejects the same five models as the exact coverage test,
$\mathrm{LR}_{\mathrm{ind}}$ the same three as the exact count, and $\mathrm{LR}_{\mathrm{cc}}$ all six; the exact
tests' verdicts are those of the 12-test level. $\mathrm{LR}_{\mathrm{cc}}$ differs from
$\mathrm{LR}_{\mathrm{uc}}+\mathrm{LR}_{\mathrm{ind}}$ only through the first day (0.03 at most). The lab codes an
exceedance as 1, where Christoffersen's indicator is 1 inside the interval; the relabelling leaves the statistics
unchanged (stated here only, decision on the third revision). It writes the three ratios out in the pair counts and
rates (the notation note's lab row), with no likelihood symbol. 8 drawdowns: X7–X9 with experiments 3 and 4, the
atoms, E10; the largest intraday log falls from the running peak (the previous close included) on 7 April 2025, 5
August 2024 and 19 March 2020, 10.31%, 8.96% and 7.84%, each at the day's low (TAIEX price index; log changes,
decision C7; per-day statistics only) [A32-44]; the first two days' lows
and closes are LM35's (A35-45), echoed at its two decimals. Extension (*Out-of-sample*, one variant declared in
advance): rerun the HS and normal backtests with a 250-return window, Basel's minimum one year (BCBS 1996b, B.4(d)), and
compare the counts with X6a; the closing sentence says that the second window is a second trial on the same data, which
LM34 treats. Labs write plain "LM29", never `[[LM29]]`.

**Cross-module tags** (the later modules whose revised briefs of 2026-10-24 cite each by number, decision C8: LM35
cites (32.9); it contrasts its scenario losses with VaR and ES in words, without a tag; LM33 and LM34 cite no LM32
tag; Volumes VII–VIII are not briefed yet, so their planned uses stay under Leads):

- (32.1) $\operatorname{VaR}_u:=-F_R^{-1}(u)$, $\operatorname{ES}_u:=-\frac1u\int_0^uF_R^{-1}(v)\,dv$, for the
  $m$-day simple return $R$, $0<u<1$, $\E\lvert R\rvert<\infty$ for ES; for continuous $F_R$,
  $\operatorname{ES}_u=-\E[R\mid R\le F_R^{-1}(u)]$ (in-module).
- (32.2) $\operatorname{VaR}=-R_{(j)}$ and
  $\operatorname{ES}=-\frac1u\big[\frac1T\sum_{i<j}R_{(i)}+(u-\frac{j-1}{T})R_{(j)}\big]$, $j=\lceil uT\rceil$: (32.1)
  under $\hat F$ (the book's one historical ES estimator, shared decision "Counting, simulation"; no later brief
  prints a historical ES yet).
- (32.3) normal: $\operatorname{VaR}_u=-\mu-\sigma\Phi^{-1}(u)$, $\operatorname{ES}_u=-\mu+\sigma\varphi(\Phi^{-1}(u))/u$
  (in-module).
- (32.4) $R=\mu+\sigma\sqrt{(\nu-2)/\nu}\,Y$, $Y\sim t_\nu$, $\nu>2$, $q=F_Y^{-1}(u)$:
  $\operatorname{VaR}_u=-\mu-\sigma\sqrt{(\nu-2)/\nu}\,q$,
  $\operatorname{ES}_u=-\mu+\sigma\sqrt{(\nu-2)/\nu}\,\frac{(\nu+q^2)f_Y(q)}{(\nu-1)u}$ (in-module).
- (32.5) for iid returns with continuous $F_R$ and $j_1<j_2$:
  $\Pr\big(R_{(j_1)}\le F_R^{-1}(u)<R_{(j_2)}\big)=\Pr(j_1\le X\le j_2-1)$, $X\sim\operatorname{Bin}(T,u)$
  (in-module).
- (32.6) $\operatorname{SE}\big(R_{(\lceil uT\rceil)}\big)\approx\sqrt{u(1-u)/T}\,/\,f_R\big(F_R^{-1}(u)\big)$ for iid
  returns with a positive continuous density at the quantile, large $T$, *stated without proof* (Glasserman 2003, (9.7))
  (in-module).
- (32.7) $\operatorname{ES}_u=\min_\theta\big\{\theta+\tfrac1u\E[(-R-\theta)^+]\big\}$, attained at
  $\theta=\operatorname{VaR}_u$; convex in $\theta$, and jointly convex with the weights when $R=\mathbf w^{\top}\mathbf
  R_t$ (in-module: Problem 12).
- (32.8) $r=g+\sigma_{t+1\mid t}\xi_{t+1}$ with $\xi$ iid of quantile $F_\xi^{-1}(u)$:
  $\operatorname{VaR}_u=1-\exp\big(g+\sigma_{t+1\mid t}F_\xi^{-1}(u)\big)$ (log returns in decimals) (in-module).
- (32.9) $\mathrm{MDD}:=\max_t\mathrm{DD}_t$ with LM1's $\mathrm{DD}_t$; $\mathrm{DD}^0_t:=\max(0,1-W_t/W_0)$; a spell
  under water runs from a peak to the first date with $W_t$ at or above it, and its length is the number of sessions below the peak (LM35: the rules' drawdowns, A32-35).
- (32.10) for $\ln W_t$ a Brownian motion with zero drift and volatility $\sigma$ a year, the expected maximum drop of
  $\ln W$ over $\tau$ years is $\sqrt{\pi/2}\,\sigma\sqrt\tau$, *stated without proof* (Magdon-Ismail et al. 2004)
  (in-module).

Tags of earlier briefs that LM32 cites by number (for their lists): (27.1)–(27.2) and (27.4) (LM27's lists name
LM32); (29.1) and (29.3), for Problem 12 (LM29's lists take LM32 from the cross-check's tag-user table, Y1, by the
decision on the second cross-check); (31.7) (LM31's list names LM32; its (31.8) names no later user).

**Pitfalls to pre-empt.**

- Signs and levels: VaR and ES are positive for a loss; "99%" is $u=0.01$; a VaR can be negative (E6). Never write
  $\alpha$ for the level (LM32's $\alpha$ is the tail index).
- The quantile rule: `np.quantile`'s default `linear` differs from $R_{(\lceil uT\rceil)}$ (A32-43); pass
  `method="inverted_cdf"` in every printed snippet.
- Three ES estimators: (32.2), the mean of the $\lceil uT\rceil$ worst and the mean of the $\lfloor uT\rfloor$ worst
  differ little on TR23 (4.689% against 4.679% at 1% [A32-11]) and a lot on small samples (E1); the book uses (32.2).
- Log against simple: quantiles pass through $e^r-1$, means do not; the ES of a log-return model is not
  $1-e^{-\text{log ES}}$ (A32-54's formula).
- Moments: name the moment each measure needs (PITFALLS §7): VaR none, ES a first ($\nu>1$, $\alpha>1$), the normal
  fit a variance; TR23's $t$ has no fourth moment, so no kurtosis-based SE applies to it.
- The $\sqrt m$ rule is exact only for an $m$-day log return of iid normal days with zero mean; on TR23 it overstates
  the ten-day VaR (E4, E8), while E4's iid figures understate it because they drop the order of days; never call an effect the cause without the comparison that isolates it (A32-55 for the data,
  A32-57 for the GARCH-t model).
- Precision: a 99% VaR from 250 returns is the third worst; its distribution-free interval has no lower end (A32-21);
  dependence more than doubles a tail quantile's SE (A32-20).
- Backtests: twelve tests on the same forecasts (Bonferroni), 30 in the lab with the likelihood ratios; Kupiec's
  ratio is two-sided (it also rejects too few exceedances), the exact coverage test one-sided; the 4,609-day zones
  apply Basel's probabilities, not its table; exceedance counts in overlapping 250-day windows are dependent (X6b's
  shares are descriptive), and a window's maximum can recur (X6b names the first window and the ties); the guard and
  its smallest margin are printed.
- 7 April spans four non-trading days, and the 10% limit capped many stocks (936 listed limit-down; Atkinson (7 April 2025), lm13.md:592): a one-day
  forecast met a five-calendar-day gap, and the index return understates the selling (PITFALLS §7, limit days).
- Drawdowns: $\mathrm{DD}_t$ against the running peak including $W_0$, $\mathrm{DD}^0_t$ against the start; the rules'
  paths start at the cash of 1 before the first purchase, so the purchase cost is a drawdown (R3, R5, R7, R8 reach
  their largest $\mathrm{DD}^0$ on their first day, A32-35); an underwater chart plots $-\mathrm{DD}_t$ and says so.
- The block bootstrap of an MDD has atoms (a short crash fits in one block): report the atom; a median on it has no
  batch SE (A32-37).
- (32.10) is for log wealth, zero drift and constant $\sigma$; $1-e^{-0.7927}=54.7\%$ is the fall that equals the
  mean log drawdown, not the mean percentage drawdown (Jensen, LM14's (14.10)) [A32-38]. (KC §8 prints the mean log
  drawdown as 0.793; the fall needs its fourth decimal, since $1-e^{-0.793}$ gives 54.8%.)
- Ownership: the rules' VaR, ES and drawdowns are LM32's; their Sharpe ratios LM33's, net wealth and costs LM34's,
  scenario losses LM35's (each rule's loss on 7 April 2025 included, A35-13), exposures LM31's, the cost of the first
  purchase LM27's (A27-23); LM26 owns the variance forecasts, LM32 their VaR.
- Unexplained extremes: TR23's −6.46% of 17 July 2026, the worst of the last 250 returns (A32-21), gets no cause
  without a dated source (shared decision).

**Curriculum guidance carried** (`plans/vol-5.md`'s table; `plans/curriculum-guidance.md`):

- g:25, tie the tools together: the through case's eight rules are measured by VaR, ES and drawdowns, net of costs,
  out of sample.
- g:30, capability layer: §1 says that LM27 measured typical risk by $\sigma_p$, and LM32 measures the tail (VaR, ES)
  and the path (drawdowns).
- g:54–58, outcome levels: [D] for (32.1)–(32.5) and (32.7), [C] for estimation, filtering, backtests and drawdowns,
  [U] for the $\sqrt m$ rule, Basel's choice and (32.10).
- g:60–63, density: LM32 is one of the four dense modules; Hill, importance sampling, the LP, the coloured portfolio
  Monte Carlo, Kupiec's and Christoffersen's likelihood ratios and intraday log falls go to problems and the lab.
- g:87–90, failure forms: LM32 shows the drawdown-limit failure on the same rules: a hypothetical 20% limit is breached
  by R1, R2 and R4 (23.19%, 22.97%, 33.56% [A32-35]); weak growth is LM34's, funding and ruin LM35's.
- g:92, define drawdown: $\mathrm{DD}_t$ and $\mathrm{DD}^0_t$, with R2 as the example where they differ (E10).
- g:93, a probability bound keeps its model: (32.10) is stated with its model (log wealth, zero drift, constant
  $\sigma$) and applied only to a hypothetical $\sigma$.
- g:94, wealth ≤ 0: no rule's path reaches it (asserted), so no truncation arises; the text says it was checked.
- g:111, fixed in advance: the backtest's window, refits and models are LM26's, fixed before LM32; the twelve tests are
  counted, and the lab's likelihood ratios bring its count to 30; the lab's 250-return window is declared as one more
  trial.
- g:124, taught, practised, assessed: the map under "Outcomes".

**Stage 4 for earlier modules.**

- `leads` gain 32 in lm01.md:6 ((1.17), $\mathrm{DD}_t$), lm05.md:6 ((5.11); on the Stage 4 list), lm10.md:6 ((10.4)),
  lm21.md:6 (the exact binomial tests, (21.6)) and lm22.md:6 ((22.3), the block rule). lm12, lm14, lm15, lm16, lm18,
  lm19, lm20 and lm26 already list 32; LM12 keeps it through §6's colouring sentence. These five are on the editor's
  merged list (decision G).
- lm04.md:46–50 and 510 print maximum drawdowns as negative numbers (−93.3%); with §6's $\mathrm{DD}\ge0$ and LM32's MDD
  they become 93.3% (the column header stays "Maximum drawdown"). Optional (decision G lists it so).
- No other wording change: lm20.md:276's "its standard error is [[LM32]]'s" is kept by E5; lm18.md:300's "applies these
  estimators to value at risk" by §6 and Problem 10 (a tail probability at a loss level is the inverse question of a
  VaR, and the lab also reads a VaR off the weighted draws).

**Sources** (as verified on 2026-10-24 by the drafter, decision F's source check, the second source hunt and the
SOURCES drafts for Volume VI, whose readings override earlier wording here; bibliographic data from Crossref unless
another record is named; section, equation and page numbers are those of the version named; paraphrased, nothing
quoted beyond a phrase):

- Artzner, P., F. Delbaen, J.-M. Eber and D. Heath (1999). "Coherent Measures of Risk." *Mathematical Finance* 9 (3):
  203–228, July 1999 (online 25 December 2001). DOI 10.1111/1467-9965.00068. Read in the authors' ETH preprint of 22
  July 1998: the four axioms that define coherence (translation invariance, subadditivity, positive homogeneity,
  monotonicity; relevance is a separate axiom). The journal's numbering was not compared, so the text cites the paper
  for the definition only and prints no axiom or theorem number.
- Acerbi, C. and D. Tasche (2002). "On the coherence of expected shortfall." *Journal of Banking & Finance* 26 (7):
  1487–1503, July 2002. DOI 10.1016/S0378-4266(02)00283-2. Read in arXiv cond-mat/0104295v5 (2 May 2002; arXiv's
  journal reference gives the same volume and pages): Definition 2.6 (the tail mean and ES, the form of (32.2)),
  Corollary 4.3 (independence of the quantile convention, by its statement there) and Proposition 3.1 (coherence).
  The journal's numbering was not compared, so the text cites "Acerbi and Tasche (2002)" without numbers. Source of
  the book's historical ES (32.2) in every module (decision D).
- Acerbi, C. and D. Tasche (2002b). "Expected Shortfall: A Natural Coherent Alternative to Value at Risk." *Economic
  Notes* 31 (2): 379–388, July 2002 (online 2 December 2003). DOI 10.1111/1468-0300.00091. A different paper from the
  previous one. Read in arXiv cond-mat/0105191v1 (9 May 2001): the sample estimator that averages the `⌊nu⌋` worst
  outcomes; used only for E1's third reading.
- Rockafellar, R. T. and S. Uryasev (2000). "Optimization of conditional value-at-risk." *Journal of Risk* 2 (3):
  21–41, 2000 (Crossref gives the year only). DOI 10.21314/jor.2000.038. Read in the working paper of 5 September
  1999: the function of its eq. (4), Theorem 1 (the minimum formula, with VaR the left end of the set of minimizers)
  and Theorem 2 (joint minimization). The equation and theorem numbers are the working paper's, and the Deep Dive
  says so. The paper assumes a density, so the Deep Dive derives the $\hat F$ case itself.
- Rockafellar, R. T. and S. Uryasev (2002). "Conditional value-at-risk for general loss distributions." *Journal of
  Banking & Finance* 26 (7): 1443–1471, July 2002. DOI 10.1016/S0378-4266(02)00271-6. Bibliographic data only: not
  relied on, and not cited unless Stage 2 reads it.
- Kupiec, P. H. (1995). "Techniques for Verifying the Accuracy of Risk Measurement Models." *Journal of Derivatives* 3
  (2): 73–84 (Crossref: issued 30 November 1995). DOI 10.3905/jod.1995.407942. Read by the second source hunt in its
  working-paper version, FEDS 95-24 (Board of Governors of the Federal Reserve System; May 1995 on the cover, April
  1995 on the title page; 47 pages; FRASER item 717921, retrieved 2026-10-24): §IV, "Verification Tests Based on
  Daily Monitoring", its part "Tests Based on the Number of Failures": the likelihood-ratio statistic on the
  proportion of failures, eq. (6), p. 19, $\chi^2_1$ under the null (the same statistic as eq. (8), p. 23, §V); with one
  failure, on the sample's last day, it reduces to the time-until-first-failure ratio, eq. (2), p. 11 (the brief's
  algebra, not a statement of the paper), whose $\chi^2$ law footnote 12 calls
  asymptotic and whose acceptance region (Table 1) has two bounds; independence is assumed, not tested (p. 7 and
  footnote 9). The journal text was not compared, so §7 names the paper at section level (§IV of the working paper) and prints no equation or page number; "POF" is not presented
  as Kupiec's word, no table of non-rejection regions is printed, and Kupiec's Table 2 is not used as a check.
- Christoffersen, P. F. (1998). "Evaluating Interval Forecasts." *International Economic Review* 39 (4): 841–862,
  November 1998. DOI 10.2307/2527341 (Crossref holds the first page only; the end page comes from the journal's RePEc
  record). Read by the second source hunt in the author's final manuscript (28 pages, PDF dated 7 July 1998, thanking
  "two referees"; CiteSeerX's cached copy of his McGill posting, through the Internet Archive): Definition 1, §2.1 (the
  indicator is 1 when the outcome lies inside the interval; a VaR is a one-sided interval); $\mathrm{LR}_{\mathrm{uc}}$,
  §3.1, $\chi^2_1$ (footnote 6 credits Kupiec (1995) with a similar test of unconditional coverage);
  $\mathrm{LR}_{\mathrm{ind}}$ against a first-order Markov chain, conditioning on the first observation, §3.2,
  $\chi^2_1$; $\mathrm{LR}_{\mathrm{cc}}$, §3.3, $\chi^2_2$, equal to
  $\mathrm{LR}_{\mathrm{uc}}+\mathrm{LR}_{\mathrm{ind}}$ when the first observation is ignored. The page numbers are the
  manuscript's and the journal's were not compared, so §7 names the paper at section level (§3 of the manuscript), with
  no page or equation number. The lab codes an exceedance as 1 and says once that the relabelling leaves the three
  statistics unchanged (the lab only, by the decision on the third revision; §7 names the papers in words and states
  no relabelling); LM21's exact-count independence check
  is the book's own and is not attributed to Christoffersen.
- Basle Committee on Banking Supervision (1996a). *Supervisory framework for the use of "backtesting" in conjunction
  with the internal models approach to market risk capital requirements* (BCBS 22). The BIS page (bcbs22.htm, which
  prints 'backtesting' in single quotes): published 4 January 1996, status Superseded, PDF of 15 pages; a technical
  note of the package that amended the 1988 Accord for market risks. Read in the BIS PDF: §III's three zones; Table 2
  (250 observations, 99% VaR): green 0–4 exceptions, yellow 5–9, red 10 or more, with the cumulative probabilities
  8.11% … 99.99%, all reproduced (A32-30); yellow starts where the cumulative probability reaches 95%, red where it
  reaches 99.99%.
- Basle Committee on Banking Supervision (1996b). *Amendment to the Capital Accord to incorporate market risks* (BCBS
  24). The BIS page (bcbs24.htm): published 4 January 1996, status Superseded, PDF of 56 pages; the page names the
  "Modifications to the market risk amendment" of 19 September 1997 as the subsequent version. Read in the BIS PDF:
  Part B.4 "Quantitative standards", (a)–(d): daily VaR; a 99th percentile, one-tailed; a ten-day holding period, with
  square-root-of-time scaling allowed; at least one year of observations. The 1996 documents spell the committee
  "Basle".
- Basel Committee on Banking Supervision (2019). *Minimum capital requirements for market risk* (d457). The BIS page
  (d457.htm): published 14 January 2019, a corrected version on 25 February 2019 (typos, with an errata list), status
  Consolidated (integrated into the Basel Framework); it replaces the standard of January 2016; PDF of 136 pages,
  whose cover reads "January 2019 (rev. February 2019)". MAR33.3, ES at a 97.5th percentile, one-tailed: read in the
  BIS PDF.
- Magdon-Ismail, M., A. F. Atiya, A. Pratap and Y. S. Abu-Mostafa (2004). "On the maximum drawdown of a Brownian
  motion." *Journal of Applied Probability* 41 (1): 147–161, March 2004. DOI 10.1239/jap/1077134674. Read in the
  authors' preprint dated 1 September 2003: with zero drift the expected maximum drawdown is $2\gamma\sigma\sqrt T$
  with $\gamma=\sqrt{\pi/8}\approx0.6267$, eq. (16), which the preprint takes from Bond (2003); the journal's equation
  number was not compared, so the text cites the paper without it. Bond (2003) is unverified and not cited. Not the
  two-author *Risk* article "Maximum drawdown".
- Glasserman (2003), §9.1.2 and (9.7), in SOURCES' first papers list (LM18's closing check): the asymptotic variance of
  a quantile estimate through the density at the quantile; cited for (32.6).
- In SOURCES and used through earlier modules: Hill (1975) (LM20's tail estimates), Politis and Romano (1994) and
  Politis and White (2004) with Patton, Politis and White (2009) (LM22: the stationary bootstrap and the block rule,
  through arch's `optimal_block_length`), the RiskMetrics document's $\lambda=0.94$ and the GARCH sources (LM26), and
  TechNews 2025-04-07 (936 listed stocks closed limit-down; SOURCES' row, cited by LM13 and LM14 as "Atkinson (7 April
  2025)").
- Checked, not cited (none was read in its published form; the survey read Chekhlov et al.'s January 2003 working
  paper): Chekhlov, Uryasev and Zabarankin (2005), *International Journal of Theoretical
  and Applied Finance* 8 (1): 13–58; Jorion, *Value at Risk: The New Benchmark for Managing Financial Risk*, 3rd ed.,
  McGraw-Hill (its year is unverified: Open Library's record gives 19 October 2006, the publisher's page © 2007);
  McNeil, Frey and Embrechts, *Quantitative Risk Management*, revised edition, Princeton University Press, 2015.

**Chinese terms** (AUTHORING §1; English in parentheses at first use in each box; a Latin name before Chinese takes a
space, as LM16 writes Mahalanobis 距離):

- From the shared list: 風險值 (value at risk), 條件風險值 (CVaR, named once), 歷史模擬法 (historical simulation),
  劣可加性 (subadditivity, 數學名詞; decision C1); the book's forms 預期短缺 (expected shortfall; LM5), 回撤 (drawdown;
  LM1), 最大回撤 (maximum drawdown), 回測 (backtest), 尾部風險 (tail risk), 一致性風險量數 (coherent risk measure).
- From LM22: 區塊自助重抽法 (block bootstrap, lm22.md:235).
- Looked up on 樂詞網 on 2026-10-24 (the drafter's phrase search, `lm32/terms/`, and the fresh pass of 1,817 searches,
  which confirmed it with the additions below):
  - value at risk (VaR): 風險值 (統計學名詞; also 管理學名詞 "value-at-risk {=VaR}" and 管理學名詞-會計學); conditional
    value at risk: 條件風險值 (統計學名詞, 管理學名詞); tail value at risk: 尾端風險值 (統計學名詞, not used).
  - expected shortfall: 期望損失 (統計學名詞, which gives the same form to "expected loss"), 預期損失 (管理學名詞); the
    book keeps LM5's 預期短缺 (lm05.md:785; one term per concept).
  - order statistic: 順序統計量 (數學名詞; 統計學名詞 順序統計量；有序統計量), as LM14 (lm14.md:603); quantile: 分位數
    (數學名詞, 統計學名詞); sample quantile: 樣本分位數 (數學名詞).
  - fat tail: 厚尾 (管理學名詞; 統計學名詞 重尾；厚尾 for "heavy tail").
  - subadditivity: 劣可加性 (數學名詞); finite subadditivity: 有限[的]次加性；有限[的]劣加性.
  - risk measure: 風險量數 (統計學名詞); "coherent risk measure": no entry, so 一致性風險量數 stays the book's form.
  - backtesting: 回溯測試 (管理學名詞); the book keeps 回測 (SOURCES, Volume V line).
  - historical simulation method: 歷史模擬法 (管理學名詞).
  - binomial distribution: 二項分布 (統計學名詞), as LM15 and LM17; binomial test: 二項檢驗 (數學名詞, not used).
  - independence test: 獨立性檢定 (數學名詞; 統計學名詞 for "test of independence").
  - permutation test: 排列檢定 (統計學名詞), the book's form by the decision on the Chinese terms (the book names every
    test 檢定); 數學名詞's 置換檢驗 is not used.
  - importance sampling: 重要抽樣 (統計學名詞), as LM18 (not in a box here).
  - no entry: drawdown, coherent risk measure, tail risk, exceedance, positive homogeneity, translation invariance;
    the axioms' names stay in English in the text, and "exceedance" is glossed 超過 VaR 的日子 in the §7 box.

**Open before Stage 2** (revised a third time on 2026-10-24: the editor's decisions settle O1 and O3–O10, the second
source hunt settles O2, and the decisions on the second recomputation and cross-check settle the rest; each is closed
below with how, and the fresh check of 2026-10-31 closed its own items, last below).

Closed by the decisions:

- **O1, the historical ES estimator:** (32.2), Acerbi and Tasche's tail mean of $\hat F$, in every module (decision D;
  the shared decision "Counting, simulation, quantiles, rounding" says so).
- **O2, Kupiec (1995) and Christoffersen (1998):** both read by the second source hunt, Kupiec in FEDS 95-24 and
  Christoffersen in his manuscript of 7 July 1998 (Sources). Decision E as amended: §7's tests stay LM21's exact
  binomial tail and exact count, and two sentences name both papers at section level for the likelihood-ratio forms
  (§IV of Kupiec's working paper, §3 of Christoffersen's manuscript), with no page or equation, and a third points to
  the lab; the lab computes $\mathrm{LR}_{\mathrm{uc}}$, $\mathrm{LR}_{\mathrm{ind}}$ and $\mathrm{LR}_{\mathrm{cc}}$
  for the six models beside the exact tests and counts its 30 tests [A32-56]; the lab alone relabels Christoffersen's
  indicator to exceedances and says the statistics are unchanged (the decision on the third revision); LM21's exact
  count stays the book's own.
- **O3, the backtest window and the block length:** LM26's 1,231 returns, and LM22's rule per rule, drawn in LM22's
  order (decision D); A32-20 and A32-37 were recomputed in that order and reproduced by the second recomputation.
  A32-28 and A32-55 state their draw layouts.
- **O4, the lab's data:** the shared decision "Labs" lists both E5 frames (the wealth frame with its traded flags),
  the rules' net wealth paths and the T5S raw days, all from
  `make_lab_data.py` (decision C6), and the lab refits LM26's GARCH laws on `taiex_tr.csv` as Lab 26 does; the lab list now names the estimation frame, Problem 12's window (the second
  recomputation's minor 4).
- **O5, the new and revised anchors:** accepted (decision D). This revision adds A32-56 (the lab's likelihood ratios)
  and A32-57 (E8's split) and changes the definitions of A32-02, A32-15, A32-31 and A32-44; the anchors' Status lists
  every change, and the third revision's recomputation reproduced them at full printed precision (2026-10-25). Derived results follow from the inputs printed beside them (the pitfall's
  $1-e^{-0.7927}$, E8's 2.2, one point and 0.6).
- **O6, notation:** $\mathcal R(\cdot)$ for a general risk measure is accepted (B5); $\sigma_{t+1\mid t}$ has no hat
  (B1); a loss is $-R$, never $L_t$ (Y7); §6's $k$ row scopes Hill's count for LM32 (Y10); LM32 writes no split-ratio
  symbol (B6); $\mathrm{LR}_{\mathrm{uc}}$, $\mathrm{LR}_{\mathrm{ind}}$, $\mathrm{LR}_{\mathrm{cc}}$ are declared.
- **O7, 劣可加性:** the shared list prints it (C1). 排列檢定 replaces 置換檢驗 (the decision on the Chinese terms).
- **O8, importance sampling and VaR:** kept as proposed; the lab reads a far-level VaR off the weighted draws, with no
  anchor.
- **O9, leads and plan promises:** kept as proposed. LM12's lead stands on §6's colouring sentence; (16.10) is LM35's;
  LM34's lead stands on §8's pointer (decision C9).
- **O10, the 4,609-day traffic light:** kept, labelled "Basel's rule applied to 4,609 days" (X5, X6a).
- **Owners (decisions A1, A5, C12):** each rule's loss on 7 April 2025 is LM35's (A35-13); TR23's 7 April returns are
  cited to lm26.md:32, and A32-02 keeps only the exact-minimum check and the four days without a session; the T5S
  closes and lows of 7 April 2025 and 5 August 2024 are LM35's (A35-45), echoed in the lab at two decimals (A32-44);
  the first purchase's cost is LM27's A27-23, echoed at three decimals against LM27's four (A32-40).
- **Tags (C8, Y1):** (32.1) names no speculative user; LM29's lists take LM32 for (29.1) and (29.3) from the
  cross-check's table; LM31's (31.7) names LM32. LM35 cites (32.9) and A32-35.
- **Text conventions (C7, C10, C11):** years run from the close before a sample's first return (A32-01, A32-03); the
  case box names its count of returns instead of "five years" and is cut into three paragraphs of at most 80 words;
  the brief's text carries no NEAR flag mark (the flags stay in the anchors table).
- **The second recomputation's pending items (closed):** the cross-check ran (Y1–Y20; this revision applies Y1, Y5, Y7, Y10,
  Y12 and Y18, with C7); B6 concerns no LM32 symbol; LM30's ownership of R2's first-window mean excess return and
  volatility touches no LM32 number; the sources' consequences for LM27–LM30 and LM35 touch none.

Closed on 2026-10-25 (the third revision's verifier, five minor items, and the decisions on the third revision): E8
says the run "does not separate these effects"; §7's likelihood-ratio words are counted as two sentences and a pointer
to the lab in Owns, the §7 row and O2, and the notation note's LR row says that §7 names the ratios in words;
$\chi^2_1$, $\chi^2_2$ are marked as §7's and the lab's, and the lab writes its ratios out in the declared pair
counts and rates with no likelihood symbol (A32-56's definition follows); Kupiec's entry ties footnote 12 and Table 1
to eq. (2); the relabelling of Christoffersen's indicator is the lab's alone. Listing markets: no LM32 statement
cites a fund's market rule, page or calendar (7 April's 10% limit is said of the index's stocks, with TechNews's
count), so nothing changes.

Closed on 2026-10-31 (the fresh check of the whole of Stage 1; its verifier confirmed the items and gave the edits,
applied here): E7's and X3's figures from unrounded fits say so; Problem 11 prints $\hat\alpha=3.634$; (32.9) counts a
spell's sessions below the peak; the rank rule, the $\sqrt m$ rule's conditions, outcomes 3 and 4 at [D] with their
verbs, the assessments of outcomes 4 and 7, Problem 12's existence, uniqueness and KKT residuals, §8's eight tests, the
labels (LM22's precedent), the missing SE sentences, $r$ in place of $y$, the notation rows, and the lab's data (the
rules' targets; LM26's laws refitted on `taiex_tr.csv`). The anchor script now prints A32-24's KKT residuals, HiGHS on a
fresh problem and the uniqueness probe as asserted bounds, A32-53 to its SE's digit and A32-17 at 3 dp; these rows
were reproduced by the fresh verification of 2026-10-31 (the anchors' Status).

Still open: none for LM32's Stage 2 writer. One optional reading: Rockafellar and Uryasev (2002), on general loss
distributions, is unread; recommendation: leave it uncited, since the 2000 paper's theorems (in its working paper)
and the Deep Dive's own $\hat F$ derivation carry every claim the text makes.

## LM33 The Statistics of the Sharpe Ratio

Stage 1 brief, drafted 2026-10-24 from the editor's spine (`plans/vol-5.md`, "### Spine of LM33 The Statistics of the
Sharpe Ratio") and the shared decisions above it, and revised the same day to the editor's decisions on the briefs
(`plans/vol-5.md`, "Editor's decisions on the briefs (2026-10-24)": A3, B5, C7–C10, D, F, G and the LM33 line), the
independent recomputation (M1, m1–m6) and the source check of decision F (its report of 2026-10-24 read Ledoit and
Wolf's JEF text, the authors' versions of Bailey and López de Prado 2012 and 2014, and Harvey and Liu's JPM text).
Revised a third time the same day to the second recomputation (MAJOR 1–5, minor 1–9 and its PENDING list), the
cross-check of the nine revised briefs (Y1, Y9, Y11, Y18), "Decisions on the first revision" and "Decisions on the
second recomputation and cross-check" (2026-10-24), and the second source hunt (Lo; Andrews and Monahan); the shared
decision "Risk-free rate", which the earlier versions missed, is now applied in E2 (A33-66).
Revised a fourth time on 2026-10-25 to the third verifier's four minor items and the LM33 line of "Decisions on the
third revision (2026-10-25)": A33-66 stays, with the rules' paths at 1.5%, and lm19.md:359 becomes a required Stage 4
rewording. No value changed.
Revised a fifth time on 2026-10-31 to the fresh check of the whole of Stage 1 (its verifier's items R33-01 to R33-09,
B33-01 to B33-23 and the shared items that name LM33) and the editor's choices: option (A) on B33-04, so problems 7, 8,
9 and 12 gain the parts that assess outcomes 4 to 7 (problem 8 (b) with the new A33-67), the prose total staying under
5,500 words; option (A) on B33-05, so the section names "Method" and "Multiple Testing Framework" stay, now recorded in
SOURCES' Harvey and Liu entry. $\hat F^{-1}_{\text{boot}}(0.95)$ prints one decimal with its Monte Carlo SE (A33-33 to
A33-39), and A33-40 adds the ratio at $\ell=0$; the changed and added anchor rows were reproduced by the fresh verification of 2026-10-31.
Every number carries its anchor ID at first appearance in a passage; `data/vol6_anchors_lm33.py` prints them all (67
rows, `## LM33` of `plans/vol-6-anchors.md`). Numbers quoted from published modules carry
their file:line. Statistics another module owns (shared decision "Owners") are echoed with that module's anchor ID
where they are printed, at most at the owner's precision (decision C12).

**Prereq:** `[4, 16, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 29, 30, 31]`. What each supplies (tags rechecked in
`src/`; LM27–LM31 are briefs, so their results are cited with the tags and anchor IDs their briefs propose):

- LM4: the Sharpe ratio $(\mu-r_f)/\sigma$ and its promise (lm04.md:120); the quadratic fraction (4.3)
  $f_q\approx\mu/\sigma^2$ and the pitfall's $f^*\approx\mathrm{SR}/\sigma$ (lm04.md:561); "size from a haircut
  estimate, then take a fraction of Kelly" (lm04.md:563).
- LM16: (16.3) the variance of a weighted sum, for the variance of a difference of two correlated estimates (§6,
  problem 6); (16.7) normal linear maps (problem 8; experiment 2 colours $\mathcal N_8(\mathbf 0,C)$ draws by it).
- LM18: (18.2) the standard error of a Monte Carlo mean (experiment 2); the standard error of a proportion,
  $\sqrt{\hat p(1-\hat p)/n}$ (lm18.md:151), for bootstrap p-values.
- LM19: (19.3) sample skewness and raw kurtosis, divisor $T$; (19.5) $\hat\rho_k$; (19.7) the variance of an
  $m$-period sum; (19.9) $\mathrm{SR}(m)$; TR23's (the TAIEX total-return index's) daily 0.0517 and annual 0.81, and
  the log-return 0.715 that (19.9) turns into 0.650 (lm19.md:370, 372); the pointer to Lo (2002) (lm19.md:359).
- LM20: (20.2) the standard error of a mean, annualized; (20.8) the delta method; (20.9) for the Sharpe ratio, with raw
  kurtosis; $\operatorname{SE}(s)\approx\sigma\sqrt{(\operatorname{Kurt}-1)/(4T)}$ (lm20.md:362); TR23's (total-return
  index) 0.0517 (SE 0.0132) and 0.81 (SE 0.207, interval 0.40 to 1.22) (lm20.md:390, 401); the pitfall that a plug-in
  standard error needs the moments it plugs in (lm20.md:409).
- LM21: (21.1) the t-stat and the identity $\sqrt T\bar R/s=\mathrm{SR}\sqrt\tau$ (lm21.md:172); (21.2) one- and
  two-sided p-values; (21.3) the statistic for two independent samples (the contrast of §6); (21.4) power and the record
  a Sharpe ratio needs, 11.9 years of daily data for TR23, the total-return index (lm21.md:177, 183); (21.6) Bonferroni;
  (21.7) Holm; (21.9) $\Pr(\max_iZ_i\le x)=\Phi(x)^m$; the rule that every test reports how many ran on the same data
  (lm21.md:284).
- LM22: (22.1) the bootstrap standard error; (22.2) percentile and basic intervals; (22.4) the bootstrap p-value of a
  t-stat; circular blocks (lm22.md:192); the book's block-length rule (lm22.md:254) and its use of one length for every
  scheme; TR23's (total-return index) Sharpe standard errors by scheme, 0.205, 0.247, 0.244, 0.233 (lm22.md:216–219).
- LM23: (23.7) Newey–West with Bartlett weights; the lag rule $\ell=\lfloor4(T/100)^{2/9}\rfloor$ (lm23.md:223); the
  pointer to LM33 (lm23.md:266).
- LM24: Bayes' rule (24.1) and the normal posterior (24.3); under a flat prior the posterior probability of a negative
  mean equals the one-sided p-value to the printed digits, yet one is a statement about $\mu$ and the other about the
  data (lm24.md:203–205). LM33 reads PSR in that light (§5, one sentence).
- LM25: (25.4) the robust standard error of $\hat\rho_k$; (25.6) the variance-ratio t-stat with iid and robust
  standard errors.
- LM27–LM31 (briefs above): the eight rules (R1 and R2, LM27; R3 and R4, LM28–LM29; R5, LM30; R6–R8, LM31, with R8's
  exposure (31.7)); the portfolio return and the wealth recursion with costs, (27.1)–(27.2), which give each rule's net
  wealth $W_t$ (LM27); the realized volatilities of R1, R3 and R5 (LM30, A30-12) and of R6–R8 (LM31, A31-27), echoed in
  the checkpoint table.

**Leads:** `[34, 35, 45]` (decision C9). LM34 cites the rules' Sharpe ratios, their tests against R1 and the deflated
Sharpe ratio by pointer and re-teaches none of them (shared decision, "LM34 against the Research hygiene page and
LM21"); it cites no LM33 tag. LM35's lab checkpoint compares rules by "the Sharpe ratio with LM33's interval", that
is (33.1)'s; LM35's prerequisites gain 33. LM45 sizes from an uncertain Sharpe ratio (§8's pointer); it has no brief
yet, so no tag is claimed for it.

**Forward links honoured.**

| Earlier text | Promise | Kept in |
|:--|:--|:--|
| lm04.md:120 | "[[LM33]] studies its estimation" | §2–§4: the standard error, dependence, annualization |
| lm04.md:563 | backtests overstate Sharpe ratios: size from a haircut, then a fraction of Kelly | §8, E9: the haircut of R2 and its effect on (4.3)'s fraction; sizing proper to LM45 |
| lm19.md:359 | Lo (2002): the $\sqrt{12}$ rule's conditions; "[[LM33]] gives the Sharpe ratio's standard error when returns are correlated" | §3 ((33.1)) and §4 (Lo's correction on 90 calendar months) |
| lm20.md:407 | "The Sharpe ratio of dependent returns is [[LM33]]'s", since $\sqrt A$ is exact only for log returns on uncorrelated days | §3, §4, E5; KC §4 |
| lm21.md:373 | "[[LM33]] deflates a Sharpe ratio for the number of trials" (reworded at Stage 4 in LM34's wording, which keeps LM33's part; decision G) | §7, E8: DSR at $n=8$ and $n_{\mathrm{eff}}$ |
| lm22.md:141 | standard errors for dependent returns, PSR, DSR and Ledoit and Wolf's (2008) test are [[LM33]]'s | §3, §5, §6, §7 |
| lm23.md:266 | "[[LM33]] applies the long-run variance to a Sharpe ratio" | §3, (33.1) with (23.7) and the book's lag |
| lm24.md:376 | "Haircuts for a backtest's Sharpe ratio are [[LM33]]'s" | §8, (33.7) |
| research-hygiene.md:7 (中文), 29, 62 | LM21 and LM33 measure the risk that the best version is lucky; LM33 covers the Probabilistic and Deflated Sharpe ratios | §5, §7; the hygiene note counts the eight rules |

The grep of `src/*.md` and `src/pages/*.md` for `LM33` finds exactly these 11 lines, and `build/make_lab*.py` has
none; the spine missed nothing. Leads that already list 33: LM16, 19, 20, 21, 22, 23, 24, 25; LM4 and LM18 gain it
at Stage 4 (decision G).

**Outcomes** ("After this module you should be able to:"; the level in brackets is the brief's, not the page's; each
within 30 words, decision C10, and 15.6 on average):

1. [C] compute a Sharpe ratio's standard error and interval by (20.9), with raw kurtosis
2. [D] derive a Sharpe ratio's HAC standard error by the delta method, and check its lag sensitivity
3. [C] annualize a Sharpe ratio of autocorrelated returns by Lo's correction, and judge whether the data need it
4. [D] derive the probabilistic Sharpe ratio and the minimum track record length, and relate them to power
5. [C] compare two Sharpe ratios by Ledoit and Wolf's test, and correct a family of such tests
6. [C] deflate the best of $n$ Sharpe ratios, and estimate the effective number of correlated trials
7. [U] explain how a haircut corrects a Sharpe ratio for multiple testing, and its effect on sizing
8. [C] compute these statistics in NumPy, and check them against SciPy and arch with every option passed

| Outcome | Taught | Practised | Assessed |
|:--|:--|:--|:--|
| 1 | §2 | E1, E2 | KC §2; problems 1, 2 |
| 2 | §3 and its Deep Dive | E3, E4 | KC §3; problem 11 (a) derivation, (b) computation |
| 3 | §4 | E5 | KC §4; problems 5, 10 |
| 4 | §5 | E6 | KC §5; problems 3, 7 (power: its last part) |
| 5 | §6 | E7 | KC §6; problems 6, 12 (Holm: part (b)) |
| 6 | §7 and its Deep Dive | E8 | KC §7; problems 4, 8 ($n_{\mathrm{eff}}$: part (b)) |
| 7 | §8 | E9 | KC §8; problem 9 (sizing: its last part) |
| 8 | §9 | the lab | KC §9; problems 10–12 |

**Owns** (shared decision "Owners", decisions A3 and A4). Out of sample, on the through case's 1,851 sessions after the
first trade: the rules' mean excess returns, R2's and R4's realized volatility, their Sharpe ratios and every standard
error, interval and test of the checkpoint table (Volume IV's checkpoint, guidance g:44). R2's first-window mean excess
return and volatility are LM30's (A30-24, decision A4), and LM33 prints neither. The methods: (20.9) applied with raw
kurtosis to the eight rules; the HAC standard error (33.1), the delta method (20.8) with (23.7)'s long-run covariance,
Bartlett weights and the book's lag (decision D), which is Lo's (2002) GMM standard error with the book's lag; Lo's
annualization of autocorrelated returns, applied through (19.9), with (25.6) for the noise of the correction; the
probabilistic Sharpe ratio (33.2) and the minimum track record length (33.3) (Bailey and López de Prado 2012),
one-sided, with $\sqrt{T-1}$ and the "1 +" term, against (21.4); the expected maximum $\E Z_{(n)}$ (33.4) from (21.9)
and the deflated Sharpe ratio (Bailey and López de Prado 2014), the track record after $n$ trials (33.5), an effective
number of trials (experiment 2); Ledoit and Wolf's (2008) difference of two Sharpe ratios (33.6), by HAC and by their
studentized circular block bootstrap with $b=22$ (the scheme read in their JEF text, decision F), on the seven pairs
R2–R8 against R1, with Holm; haircuts (33.7) (Harvey and Liu 2015) by Bonferroni and independent tests, as they define
them, and by Holm on the eight rules' own p-values (the book's adaptation); the haircut's effect on (4.3)'s fraction
(one paragraph). Values owned: every A33 anchor except the echoed numbers of LM19, LM20, LM21 and LM22 (file:line in the
anchors) and the volatilities of R1, R3 and R5 (LM30, A30-12) and of R6–R8 (LM31, A31-27).

**Leaves.** Testing rules fixed in advance on later data, White's reality check, PBO and gross against net Sharpe
ratios → LM34 (one sentence each in §6 and §7). Sizing from an uncertain Sharpe ratio (bootstrap Kelly, shrinkage of
the fraction) → LM45 (§8, one sentence). Bayesian shrinkage of a Sharpe ratio toward a prior → LM24's tools, one
sentence (§5). Ledoit and Wolf's calibration of the block size (their Algorithm 3.1) and their prewhitened
quadratic-spectral kernel → named once, not used (§6). The test of one
Sharpe ratio against a benchmark index (the information ratio) → not in the book, one sentence (§6). Harvey and Liu's
false-discovery haircut (their BHY version) → named once (§8); LM21 owns the false discovery rate. Whether two rules'
volatilities differ beyond chance → not in the book (LM31 drops that promise; the editor's LM33 decision).

**Uses before taught** (one sentence each in the text):

- §6: "Testing rules fixed in advance on later data, and White's (2000) reality check of a whole search, are
  [[LM34]]'s; this section compares two rules fixed in advance."
- §7: "The probability that a search's best in-sample configuration is overfit, PBO, is [[LM34]]'s."
- §7: "Bailey and López de Prado derive their approximation of $\E Z_{(n)}$ in their Appendix A.1; the module states
  it without proof and computes the exact integral instead."
- §8: "Choosing a position size from an uncertain Sharpe ratio is [[LM45]]'s; here the haircut only rescales (4.3)'s
  fraction."

**Data role.**

- **E5's wealth frame, the through case** (shared decisions "Data", "E5's two frames" and "Through case").
  `data/vol5_series.py`'s `frames("E5")` reads `data/processed/vol5_frames.parquet` (FinMind `TaiwanStockPrice`,
  `TaiwanStockDividendResult` and `TaiwanStockSplitPrice`, registered 2026-10-24); `data/vol5_rules.py` gives the
  eight rules (`signals`, `wealth_path`, `summary`), net of costs through (27.1)–(27.2); no rule is re-implemented. A
  rule's own returns are a portfolio's, so they use the wealth frame and $A_{\mathrm w}$. The wealth paths equal
  `data/processed/vol5_rules.parquet` exactly, none is ruined, and $\sqrt{A_{\mathrm w}}\,\bar x/s$ equals
  `summary()`'s Sharpe ratio to 1e-12. Daily: $T=1{,}851$ net returns $R_t=W_t/W_{t-1}-1$, 5 March 2019 → 8 October
  2026, from the session after the first trade (4 March 2019) [A33-01; LM28's A28-03]; $A_{\mathrm w}=243.57$ from the wealth
  frame's 2,368 sessions (LM27's A27-03); $r_f=1.5\%$ accrues 0.616 bp a session [A33-02]; the rate is illustrative (LM7's), and E2
  says what 0% or 2% would change (shared decision "Risk-free rate"): only the rate in the Sharpe ratio changes, and
  the rules' own paths keep $r_f=1.5\%$ (R4's signal and R8's cash; R8 borrows at 3.5%). Excess returns $x_t=R_t-r_f/A_{\mathrm w}$.
- **Years** (decision C7: every "years" names its count). A span is calendar days ÷ 365.25 from the close before a
  sample's first return to its last close (AUTHORING §8): the record runs 7.60 calendar years (7.5975) from the first
  trade's close, 4 March 2019, the close before its first return, to 8 October 2026 [A33-01]. A track record's length
  is its sessions ÷ $A$ of the sample, "years of sessions": MinTRL, the years a gap needs, and
  $\tau=T/A_{\mathrm w}=7.60$ (7.5995) for the observed record [A33-01]. The text names the count at its first use in
  each passage and compares a MinTRL with the record in sessions (1,796 against 1,851 [A33-49]).
- **Months.** The 90 full calendar months April 2019 → September 2026, 12 to 23 sessions each; the 19 returns of March
  2019 and the 6 of October 2026 are left out, and the text says so [A33-03]. Dropping the sample's first and last
  calendar month, LM27's rule (decision "Weeks and months"), gives the same 90. A month's log excess return is the log
  change of net wealth between month-end sessions minus the month's accrued log interest, sessions $\times
  \ln(1+r_f/A_{\mathrm w})$. Log returns, because (19.9) needs sums; every log is defined, since $1+R_t>0$ on every
  date (no rule is ruined).
- **TR23** (Volume III), the TAIEX total-return index: `data/processed/vol3_taiex.parquet`'s $R$, $T=5{,}849$ returns
  2003-01-03 → 2026-10-08, 23.76 calendar years from the close of 2 January 2003, $A=246.12$, $r_f=0$ (Volume IV's
  convention) [A33-05]: the long
  record against which the through case's 7.60 calendar years [A33-01] are judged. LM19's and LM20's numbers are quoted
  as printed and recomputed only as checks [A33-21].
- **Conventions.** Sharpe ratios are per observation in every formula and annualized only for printing:
  $\sqrt{A_{\mathrm w}}$ for E5's days, $\sqrt{12}$ for months, $\sqrt A$ for TR23, always a convention on simple
  returns (LM19). Means, $s$, skewness and raw kurtosis divide by $T$ (19.3); every kurtosis printed says "raw" or
  "excess" (shared decisions, "LM33's load"). (20.9) is the plug-in with the sample moments; "normal" sets skewness 0
  and kurtosis 3, which is Lo's IID formula (9), $\sqrt{(1+\mathrm{SR}^2/2)/T}$ (his IID case takes the normal value
  $2\sigma^4/T$ for the variance of $\hat\sigma^2$). HAC (decision D): (23.7)'s Bartlett
  weights, the book's lag, 7 at $T=1{,}851$, 9 for TR23 and 3 for 90 months [A33-04], no small-sample factor.
  Two-sided normal intervals $\pm1.959964$ standard errors; PSR, MinTRL and DSR are one-sided at 95%, with
  $\sqrt{T-1}$ (decision D). These are large-$T$ results, stated without proof (shared decision "Rigor"): "large" is
  the 1,851 daily returns and TR23's 5,849; the 90 months are the small sample, and E5 says so.
- **Bootstrap** (shared decision "Counting", decision D). Circular blocks of $b=22$: LM22's rule (lm22.md:254), the
  largest stationary estimate among the squared demeaned return series the statistic involves, is R4's 22.41
  [A33-32]. Ledoit and Wolf's statistic for a pair involves the two rules' own returns, and the seven pairs share one
  set of block starts, so the rule runs over the eight rules. The circular scheme uses the same length, as LM22 used
  145 for every scheme (lm22.md:221, 254); the circular estimates themselves reach 25.65 [A33-32]. $T=1{,}851$ is
  $84\times22+3$: a resample draws 85 block starts, joins the blocks and keeps the first 1,851 rows; its moments are
  centred at its own means; its Götze–Künsch covariance uses the 84 complete blocks only [A33-32]. The source check
  read Ledoit and Wolf's JEF text (decision F) and found the script's scheme in it: circular blocks of return pairs
  (§3.2.2, p. 854), the centred studentized statistic, the Götze–Künsch variance on the $\lfloor T/b\rfloor$ complete
  blocks with each resample centred at its own estimates, and the p-value with "+1" (Remark 3.2, eq. (9), p. 855).
  So the bootstrap is printed beside the HAC test. Three settings are the book's, and the text labels them so: the
  Bartlett HAC error with $\ell=7$ (theirs: a kernel estimate with a $T/(T-4)$ factor, §3.1, and for the bootstrap's
  original-data error the prewhitened quadratic-spectral kernel, §3.2.2, p. 854), $b$ by LM22's rule (theirs:
  calibrated by Algorithm 3.1, pp. 854–855), and the resample's length when $T$ is not a multiple of $b$ (the paper
  does not say).
- **Guard and exact checks.** Bootstrap counts use $\ge$ the statistic $-10^{-12}$; Holm's rejections use
  $\le0.05+10^{-12}$. A bootstrap p-value is a multiple of 1/10,000 and is printed to two decimals.
- **Seeds.** Experiment 1: the seven Ledoit–Wolf tests, `default_rng([1, 20261011])`, $B=9{,}999$ circular-block
  resamples of the 1,851 dates with $b=22$, one set of block starts per resample shared by the seven pairs. Experiment
  2: $10^6$ draws of $\mathcal N_8(\mathbf 0,C)$, `default_rng([2, 20261011])`. Experiment 3: R2 against R1 at block
  sizes 1, 5, 10, 26, 50 and 100, $B=9{,}999$ each, `default_rng([3, 20261011])`, drawn in that order (the first
  draft's grid, kept; 26 is the largest circular estimate, and $b=22$ itself is experiment 1's). Monte Carlo
  standard errors: $\sqrt{p(1-p)/B}$ for a p-value (lm18.md:151), SD ÷ $\sqrt{10^6}$ for experiment 2's mean (18.2).
  The widget does not simulate.
- **Published files.** Only statistics: per-rule moments and estimates, lag and block-size curves, model curves. No
  daily series of a rule in date order is published, and no intraday path (shared decision "Charts", X37).
- **Scripts.** `data/lm33_numbers.py` (every printed value, asserted against `src/lm33.md`, compared with the anchors,
  rounding boundaries flagged) and `data/lm33_charts.py` (X2–X7 and the widget's data block); both import `frames` from
  `data/vol5_series.py` and `signals`, `wealth_path` and `summary` from `data/vol5_rules.py`, read
  `vol5_rules.parquet` and `vol3_taiex.parquet` (the shared builders run first), and re-implement no rule.

**Hygiene declaration.** *Out-of-sample:* every Sharpe ratio, interval, PSR, test, DSR and haircut of the eight rules
(rules, windows, costs and criteria fixed on 2026-10-24 before any result; 1,851 sessions after the first trade). The
family is R1–R8, $n=8$ (shared decision, "The count of trials"). On the same returns the module runs four families
of tests and says so: eight one-sided PSR(0) tests (§2, §5; Holm), the seven pair tests against R1 by HAC and the same
seven by bootstrap (§6; two families, Holm in each), and eight two-sided tests of a zero Sharpe ratio for the haircuts
(§8; Bonferroni, independent tests and Holm). *Stability check:* the HAC lag curves (X3, $\ell=0$ to 60), the
block-size sensitivity (experiment 3), the monthly against daily ratios, $r_f$ at 0% and 2% in the Sharpe ratio (E2;
the rules' paths keep $r_f=1.5\%$, and R8 still borrows at 3.5%). *In-sample:* TR23's
figures, as LM19–LM22 printed them. *Model:* X4's track-record curves (normal returns), experiment 2, the widget, the
published examples of Bailey and López de Prado and of Harvey and Liu (their inputs). *Descriptive:* the rules'
correlations and autocorrelations. Local note, two paragraphs: "The eight rules and their settings were fixed on 24 October 2026, before any result
was computed. Their Sharpe ratios are therefore out of sample: 1,851 daily net returns, 5 March 2019 to 8 October
2026, with $r_f=1.5\%$. The module runs four families of tests on these returns. They are eight one-sided tests
against zero, the seven pairs against R1 by two methods, and the eight two-sided tests behind the haircuts." /
"Section 7 deflates the best for $n=8$ and says what independence that count assumes. Lag and block-size curves are
stability checks. TR23's figures are in sample, as [[LM19]] and [[LM20]] printed them; the track-record curves and
the correlated simulation are model results."

**Notation.** AUTHORING §6 with the Portfolios table. Used: $R_t$, $r$, $T$ (a count), $t$, $\tau$ (years of
sessions), $A$, $A_{\mathrm w}$, $r_f$, $W_t$, $\mathrm{SR}$, $\widehat{\mathrm{SR}}$, $\mathrm{SR}_0$, PSR, DSR,
MinTRL, $\mu$, $\sigma$, $s$, $\widehat{\operatorname{Skew}}$, $\widehat{\operatorname{Kurt}}$ (raw), $\rho_k$,
$\hat\rho_k$, $\hat\rho$, $C$ (the rules' correlation matrix), $\bar\rho$ (the mean of its off-diagonal entries,
§7), (19.7)'s ratio written out (no $\operatorname{VR}$
symbol, as LM26 does), $\E$, $\Var$, $\Cov$, $\Phi$, $\Phi^{-1}$, $\varphi$,
$\mathcal N$, $\mathcal N_8$, $Z$, $\mathbf Z$, $\operatorname{SE}$, $\text{t-stat}$, $H_0$, $H_1$, $\alpha$ (the
significance level, LM33's meaning), $n$ (trials), $m$ (periods summed in (19.9)), $k$ (a lag), $B$, $\ell$ (the HAC
lag), $\hat F^{-1}_{\text{boot}}$ (LM22's), $\boldsymbol\theta$, $\hat{\boldsymbol\theta}$, $\nabla h$ ((20.8)), $f_q$
((4.3), §8 only). Local symbols, declared in the notation note and accepted as declared (decision B5):

| Symbol | Meaning | Check against §6 |
|:--|:--|:--|
| $x_t$, $\bar x$ | a rule's daily excess return $R_t-r_f/A_{\mathrm w}$, its mean; $s$ is its SD (divisor $T$, equal to that of $R_t$) | LM19's generic series $x_t$ of (19.5); LM33 writes no data matrix $X$ and no random variable $X$ |
| $\widehat{\mathrm{SR}}_j$, $\Delta$, $\hat\Delta$ | rule $j$'s estimate ($j=1,\dots,8$ for R1–R8); $\mathrm{SR}_j-\mathrm{SR}_1$ and its estimate | common $\Delta$ for a difference; "a year" marks annual values |
| $\hat V_{\mathrm{SR}}$ | $1-\widehat{\mathrm{SR}}\,\widehat{\operatorname{Skew}}+\tfrac14(\widehat{\operatorname{Kurt}}-1)\widehat{\mathrm{SR}}^2$, (20.9)'s plug-in, so $\operatorname{SE}=\sqrt{\hat V_{\mathrm{SR}}/T}$ | new; no SVD $V$ in LM33; Bailey and López de Prado's $V$ (the variance across trials) is written in words |
| $\mathbf v_t$, $\Psi$, $\hat\Psi$, $\hat\Gamma_k$ | the per-date terms of a statistic (a column); their long-run covariance; (23.7)'s estimate; the lag-$k$ sample autocovariance of $\mathbf v_t$ (divisor $T$) | new; the discount factor $v$ is not in LM33; $\hat\Gamma_k$ as LM23's |
| $b$ | the block size of the circular block bootstrap (Ledoit and Wolf's letter), 22 here | §6's $B$, $\ell$ row: LM33 declares two letters, $\ell$ the lag (LM23's) and $b$ the block; LM33 has no bets |
| $\hat\Delta_{\text{boot},i}$ | the difference in resample $i$ | LM22's subscript; no star |
| $Z_{(n)}$, $\E Z_{(n)}$ | the largest of $n$ iid standard normals; its mean | as §6's $R_{(j)}$; $n$ is §6's number of trials |
| $n_{\mathrm{eff}}$ | the effective number of trials | new, subscripted |
| $\gamma_{\mathrm E}$ | Euler's constant, 0.5772 (in the approximation of (33.4)) | subscripted; $\gamma$ (growth of cash flows) is not in LM33 |
| $\mathrm{HSR}$, $\text{t-stat}_{\text{adj}}$ | the haircut Sharpe ratio; the t-stat whose single-test p-value equals the adjusted one | new, local (decision B5); HSR upright like PSR |

Not used: $\eta(q)$ for Lo's scale factor (LM5's $\eta$; written "the scale factor"), a star on a bootstrap quantile or
an adjusted t-stat, $d$ for Ledoit and Wolf's studentized statistic (written out), $\gamma_3$, $\gamma_4$ for the
moments, $p_{\mathrm S}$, $p_{\mathrm M}$ (p-values in words, as §6 asks outside LM21), $L$ (R8's exposure appears only
through LM31), $q$. LM33 says once that (21.6)–(21.9)'s $m$ tests read as $n$ trials.

**Motivating case: "Better, or lucky?"** (box, 155 words by `build/qa/style.py --strict`, in three paragraphs of at
most 80; 10 sentences, each within 30 words and 15.5 on average; no FAIL; decision C10)

> Eight rules for five Taiwan-listed funds were fixed on 24 October 2026, before any result was computed. Net of
> costs, they earned 1,851 daily returns from the close of 4 March 2019 to 8 October 2026, 7.60 calendar years
> [A33-01]. The constructed reference mix R2 has the highest Sharpe ratio, 1.14 a year. Equal weights, R1, earn 0.98,
> and the maximum-Sharpe rule R4 the lowest, 0.63 [A33-14].
>
> Is R2 better, or lucky? Its standard error is 0.367, so its 95% interval runs from 0.42 to 1.86 [A33-07] and holds
> all seven other estimates [A33-14]. R2 beats R1 by 0.16 a year, and their daily returns correlate 0.70. Ledoit and
> Wolf's test of the gap gives a p-value of 0.52, by HAC and by bootstrap alike [A33-33].
>
> R2 is also the best of eight. If eight independent rules all had a true Sharpe ratio of zero, the best of their
> estimates would still average 0.52 a year over 1,851 daily returns [A33-45].

Resolved: (a) the precision of one ratio: §2–§4, X1, X2 (HAC interval 0.39 to 1.89 [A33-07]; Lo's monthly ratio 0.94
[A33-22]); (b) how long a record must be: §5, X4 (MinTRL against zero, 523 sessions or 2.15 years of sessions
[A33-26]; 1,796 sessions, 7.37 years of sessions, after eight trials [A33-49], against the 1,851 observed [A33-01]);
(c) R2 against R1: §6, X5 (HAC p-value 0.52 and interval −0.33 to +0.66, bootstrap p-value 0.52 and interval −0.34 to
+0.67 [A33-33]; 146 years of sessions for 80% power if the gap were true [A33-41]); (d) the best of eight: §7–§8,
X6, X7 (DSR 0.955 at $n=8$ [A33-46], 0.994 at the effective 2.07 trials [A33-48]; a haircut of 21% [A33-54]). The
verdict the module reaches: R2's one-sided test against zero gives PSR(0) 0.999 [A33-16] and DSR 0.955 after eight
trials [A33-46]. Yet 7.60 calendar years cannot rank it above R1, so the data do not support allocating more to R2
than to R1 (guidance g:116).

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | the layer LM33 adds: Volume IV gave one Sharpe ratio an error bar, Volume VI compares eight rules and corrects for picking the best; case + X1; roadmap; notation and hygiene notes (trimmed by 130 words for the four problem parts of the fresh check, the editor's choice (A) on B33-04) | 230 |
| 2 | The Checkpoint: Eight Rules with Error Bars {1} | Volume IV's checkpoint on the through case (g:44): (20.9) applied, raw kurtosis named; E1 (R2 by hand); E2 (all eight: mean excess, volatility and Sharpe ratio with standard errors); X2; R4's two-sided interval and one-sided test; the illustrative $r_f$ at 0% and 2% in the Sharpe ratio only (three sentences); pitfall: excess kurtosis typed into (20.9); 導讀; KC | 575 |
| 3 | Dependent Days: the HAC Standard Error {2} | why returns that are nearly uncorrelated still need care (R1's squares have $\hat\rho_1=0.246$ [A33-19]); (33.1) from (20.8) and (23.7); conditions stated; Deep Dive: (33.1) at $\ell=0$ is (20.9); X3, the lag curve; E3 (HAC over (20.9) 0.92 to 1.04 for the Sharpe ratio [A33-18], 1.51 to 1.60 for the volatility [A33-20]); E4 (TR23 against LM20 and LM22); one sentence: (33.1) is Lo's GMM standard error with the book's lag; 導讀 (HAC, long-run variance); KC | 500 |
| 4 | Annualizing Autocorrelated Returns {3} | (19.9) as Lo's scale factor; one sentence: [[LM19]] estimated (19.9) with the overlapping variance ratio of (19.8), while E5 uses (19.7)'s form in $\hat\rho_1,\dots,\hat\rho_{11}$ (Lo's eq. (20)), whose standard error is (25.6); Lo's AR(1) check; E5 on 90 calendar months; the correction's own noise by (25.6); simple against log ratios; KC | 480 |
| 5 | The Probabilistic Sharpe Ratio and the Minimum Track Record {4} | (33.2) as one minus a one-sided p-value (21.2), not a probability without a prior ([[LM24]]); (33.3) by inversion; against (21.4): one-sided, power ½, the "1 +" and $\hat V_{\mathrm{SR}}$; $T$ against $T-1$; X4; E6; TR23; the published example reproduced; pitfall: $\mathrm{SR}_0$ is a benchmark, not another rule's estimate; 導讀 (one-sided test); KC | 620 |
| 6 | Comparing Two Sharpe Ratios {5} | Ledoit and Wolf's delta method on four moments (33.6) with (23.7); correlation shrinks the error ((16.3)), against (21.3); the studentized circular block bootstrap with $b=22$ by the book's rule, its p-value against (22.4); the book's three settings labelled (Bartlett $\ell=7$, $b$, the last block); X5; E7; the seven pairs and Holm; the years of sessions a gap of 0.16 needs [A33-41]; one sentence each on [[LM34]] and the information ratio; 導讀 (studentized interval, circular blocks); KC | 640 |
| 7 | Deflating the Best of Eight {6} | the winner's expected maximum from (21.9), (33.4), Deep Dive; the approximation stated; DSR at $n=8$; what $n=8$ assumes; the effective number (experiment 2) beside Bailey and López de Prado's eq. (9); the cross-section's dispersion; (33.5); X6; E8; the published example reproduced; one sentence on PBO ([[LM34]]); pitfall: a DSR near 0.95 is not a verdict; 導讀 (selection bias, order statistic); KC | 600 |
| 8 | Haircuts and Sizing {7} | Harvey and Liu's haircut (33.7): Bonferroni and independent tests as theirs, Holm on the eight rules' own p-values as the book's adaptation; X7; E9; their example reproduced; Holm's running maximum; the haircut on (4.3)'s fraction, then a fraction of Kelly (LM4's promise), [[LM45]] pointer; "the data are too thin" as a valid conclusion; KC | 400 |
| 9 | Sharpe Statistics in Python {8} | NumPy by hand; `scipy.stats.skew` and `kurtosis` with `fisher`, `bias` passed; arch `optimal_block_length`'s two columns; the bootstrap loop with one generator; lab box | 180 |
| — | Summary (7) / Problems (12) / Solutions | the Summary trimmed by 40 words and §2 by 65; the problems' five added parts (7, 8 (b), 9, 11 (a), 12 (b)) about 115 words and their solutions about 120 | 100 / 515 / 640 |
| | **Total** | | **5,480** |

**Elements.** 9 examples (E1, E2 §2; E3, E4 §3; E5 §4; E6 §5; E7 §6; E8 §7; E9 §8). Knowledge checks:

- §2: R4's two-sided 95% interval, −0.09 to 1.35, contains 0, yet its PSR(0) is 0.956 [A33-17]. Why both? The interval
  is two-sided at 5%; PSR is one-sided, and its two-sided twin at 10%, 0.02 to 1.23, excludes 0 [A33-17].
- §3: R1's daily excess returns have $\hat\rho_1=-0.054$, its squared deviations 0.246 [A33-19]. Which standard error
  should dependence move more, the mean's or the volatility's? The volatility's, which rests on the squares: HAC over
  iid is 1.51 for R1's volatility [A33-20] but 0.94 for its mean, 4.25% against 4.53% [A33-06, A33-65].
- §4: for monthly AR(1) returns with $\rho_1=0.2$, so that $\rho_k=0.2^k$, (19.9) gives a scale factor 2.879 against
  $\sqrt{12}=3.464$ [A33-24]. The $\sqrt{12}$ rule overstates the annual ratio by 20% (a factor 1.203); Lo's Table 2
  prints 2.88 [A33-24].
- §5: setting $\mathrm{SR}_0$ to R1's estimate makes R2's MinTRL 106 years of sessions and its PSR 0.67 [A33-31]. What
  is wrong? R1's 0.98 [A33-06] is an estimate with its own error; comparing two estimates is §6's test.
- §6: the standard error of R2 − R1 that treats the two as independent is 0.521 a year, Ledoit and Wolf's 0.253
  [A33-40]. Why is the second smaller? The daily returns correlate 0.70 [A33-33], so the two errors move together
  ((16.3)). With equal errors and no other term, (16.3) would give the ratio $\sqrt{1-\hat\rho}=0.55$; the full
  delta method at $\ell=0$ gives 0.54, and HAC at $\ell=7$ lowers it to 0.49 [A33-40].
- §7: $\E Z_{(8)}$ is 1.424; the approximation gives 1.459 and (21.9)'s median 1.39 [A33-44]. Why is the mean above the
  median? The maximum's distribution is skewed to the right.
- §8: Holm's haircut of R4 is 0% while Bonferroni's is 75% [A33-53]. Why? R4 has the largest p-value, which Holm
  compares with the level itself; the adjusted value cannot fall below the running maximum, so R6, R7 and R8 share
  0.71 [A33-53].
- §9: `scipy.stats.kurtosis` of R2's excess returns with its defaults (`fisher=True`, `bias=True`) gives 10.58, the
  excess kurtosis; (20.9) needs the raw 13.58 [A33-64].

中文導讀 in §2 (夏普比率 (Sharpe ratio), 標準誤 (standard error), 偏態 (skewness), 峰態 (kurtosis): raw against excess), §3 (自我相關
(autocorrelation), 變異數非齊一與自我相關一致估計量 (HAC), 長期變異數 (long-run variance)), §5 (單邊檢定 (one-sided test), 檢定力 (power); PSR and
MinTRL kept in English), §6 (Student化信賴區間 (studentized confidence interval), 循環區塊 (circular block), 區塊自助重抽法 (block
bootstrap)), §7 (選擇偏誤 (selection bias), 順序統計量 (order statistic), 多重假設檢定 (multiple testing); DSR kept in English). Deep
Dives: §3 "Why the HAC error at lag zero is (20.9)": $\hat\Gamma_0$ of $\mathbf v_t$ has entries $s^2$,
$s^3\widehat{\operatorname{Skew}}$ and $s^4(\widehat{\operatorname{Kurt}}-1)$, and $\nabla h^{\top}\hat\Gamma_0\nabla h$
is $\hat V_{\mathrm{SR}}$ term by term (the script asserts it to 1e-15). §7 "The expected maximum from (21.9)": $\E
Y=\int_0^\infty(1-F_Y)\,dy-\int_{-\infty}^0F_Y\,dy$ for $Y$ with a finite mean, by integration by parts on each
half-line, with $F_Y=\Phi^n$; the approximation *stated without proof* (Bailey and López de Prado 2014, their
Appendix A.1).

**Exhibits.**

- X1 `case` (two tables, §1, split so that no PDF page shrinks, decision C10): the eight rules, daily net excess
  returns, 5 March 2019 → 8 October 2026, $r_f=1.5\%$; rows in the order fixed in advance (not sorted by result).
  (a) Per rule, six columns: rule; Sharpe ratio a year; SE by (20.9); SE by (33.1), $\ell=7$; 95% interval (HAC);
  PSR(0); the ratio carries three decimals so that each interval follows from the printed ratio and SE. R1 0.976,
  0.370, 0.363, 0.26 to 1.69 [A33-06], 0.996 [A33-16]; R2 1.138, 0.367, 0.382, 0.39 to 1.89 [A33-07], 0.999 [A33-16];
  R3 0.775, 0.370, 0.373, 0.04 to 1.51 [A33-08], 0.982 [A33-16]; R4 0.629, 0.368, 0.340, −0.04 to 1.30 [A33-09], 0.956
  [A33-16]; R5 0.843, 0.370, 0.374, 0.11 to 1.58 [A33-10], 0.989 [A33-16]; R6 0.955, 0.371, 0.370, 0.23 to 1.68
  [A33-11], 0.995 [A33-16]; R7 0.918, 0.370, 0.368, 0.20 to 1.64 [A33-12], 0.993 [A33-16]; R8 0.935, 0.371, 0.368, 0.21
  to 1.66 [A33-13], 0.994 [A33-16]. Note row: DSR of R2 at $n=8$ 0.955 [A33-46]. (b) Each rule against
  R1, six columns: pair; $\hat\Delta$ a year; $\operatorname{SE}(\hat\Delta)$, $\ell=7$; HAC p-value; bootstrap
  p-value; Holm-adjusted p-value, for both families ($\hat\Delta$ to three decimals, so that each HAC p-value follows
  from the printed $\hat\Delta$ and SE). R2 +0.162, 0.253, 0.52, 0.52 [A33-33]; R3 −0.201, 0.243, 0.41, 0.41 [A33-34];
  R4 −0.347, 0.285, 0.22, 0.25 [A33-35]; R5 −0.134, 0.229, 0.56, 0.56 [A33-36]; R6 −0.022, 0.137, 0.87, 0.88 [A33-37];
  R7 −0.058, 0.207, 0.78, 0.78 [A33-38]; R8 −0.041, 0.163, 0.80, 0.81 [A33-39]; Holm 1.00 for every pair in both
  families [A33-43]. Note: out of sample; net of costs; $A_{\mathrm w}=243.57$ [A33-02]; the bootstrap is Ledoit and
  Wolf's (circular blocks, $B=9{,}999$, seed `[1, 20261011]`, Monte Carlo SE at most 0.005 [A33-33]), with the
  book's $\ell=7$, $b=22$ and last-block rule. Source: FinMind `TaiwanStockPrice`, `TaiwanStockDividendResult`,
  `TaiwanStockSplitPrice`, registered 24 October 2026; Computations: `data/lm33_numbers.py`.
- X2 `forest` (`scatter`, forest plot, §2): y the eight rules, `ticks` 1–8 with `tickLabels` R1 … R8 in fixed order; x
  the annual Sharpe ratio, −0.2 to 2.0 (`fmt: "n2"`). One named point series "estimate" (colour 1); per rule an unnamed
  thick `lines` entry for the (20.9) interval (colour 1) and a thin grey one, offset by 0.2 in y, for the HAC interval
  ($\ell=7$); a dashed `lines` entry (`dash: true`, `extend: true`) at $x=0$, since scatter charts take no `ann`. Values cited: the eight intervals of A33-06 to A33-13; R2's 0.42 to 1.86 and 0.39 to
  1.89 [A33-07]; R4's −0.09 to 1.35 [A33-09]. Note: names the two interval styles; out of sample.
- X3 `haclag` (`line`, §3): x the lag $\ell$, 0 to 60 (`fmt: "n0"`); y the Sharpe ratio's SE a year (`fmt: "n3"`);
  series R1, R2, R4 (colours 1–3); dashed `hline` at the normal SE 0.363 [A33-06]; dashed `vline` at $\ell=7$. Values
  cited: R1 0.370, 0.363, 0.359, 0.367; R2 0.367, 0.382, 0.393, 0.389; R4 0.368, 0.340, 0.316, 0.300 at $\ell=0$, 7,
  20, 60 [A33-18]. Note: $\ell=0$ is (20.9); a stability check.
- X4 `psrT` (`line`, log x, §5): x years of sessions of daily data, 0.5 to 15 (`ticks` 0.5, 1, 2, 5, 10); y PSR(0)
  (`fmt: "n3"`, 0.5 to 1); series "annual SR 0.5", "1.0", "1.5" (colours 1–3), normal returns, $A_{\mathrm w}$; dashed
  `hline` 0.95; dashed `vline` at $\tau=7.60$; `point`s at the crossings. Values cited: MinTRL 10.83, 2.72 and 1.21
  years of sessions; PSR(0) at 7.60 years of sessions 0.916, 0.997, 1.000 [A33-29]. Note: *Model*; the estimate held
  fixed as the record lengthens.
- X5 `pairs` (`scatter`, forest plot, §6): y R2 … R8 against R1 (`ticks` 1–7, `tickLabels` "R2 − R1" …); x $\hat\Delta$
  a year, −1.0 to 0.8; points "difference" (colour 1), thick `lines` for the HAC normal 95% intervals, thin grey
  ones, offset by 0.2 in y, for the bootstrap intervals; a dashed `lines` entry (`dash: true`, `extend: true`) at $x=0$. Values cited: A33-33 to A33-39; R2 − R1
  +0.16, HAC −0.33 to +0.66, bootstrap −0.34 to +0.67 [A33-33]; R4 − R1 −0.35, HAC −0.91 to +0.21, bootstrap −0.95 to
  +0.25 [A33-35]. Note: Ledoit and Wolf's HAC interval with (23.7), $\ell=7$; their symmetric studentized bootstrap
  interval with circular blocks, $b=22$, $B=9{,}999$, seed `[1, 20261011]`, Monte Carlo SE of the interval ends at most 0.006 [A33-33 to
  A33-39] ($\ell$ and $b$ the book's choices); seven
  tests on the same returns, none rejected after Holm [A33-43].
- X6 `deflate` (`line`, log x, §7): x the number of trials $n$, 1 to 10,000; y the deflated benchmark
  $\mathrm{SR}_0$ a year (`fmt: "n2"`); series "exact, (33.4)" (colour 1, $n=1$ to 10,000) and "approximation" (colour 2, dashed, from $n=2$, since it is $-\infty$ at $n=1$);
  dashed `hline` at R2's pass line 0.53 ("the largest $\mathrm{SR}_0$ R2 passes at 95%") [A33-52]; dashed `vline`s at
  $n=8$ and $n_{\mathrm{eff}}=2.07$ [A33-48]. Values cited: 0, 0.20, 0.52, 0.56, 0.91, 1.18, 1.40 at $n=1$, 2, 8, 10, 100, 1,000,
  10,000 [A33-52]; approximation 0.529 at 8 [A33-45]; $n_{\mathrm{eff}}$ [A33-48]. Note: $T=1{,}851$; the null
  standard deviation $1/\sqrt{T-1}$, 0.363 a year [A33-45].
- X7 `haircut` (`bar`, §8): categories R1–R8; series "Sharpe ratio", "HSR, independent tests", "HSR, Holm" (colours 1–3;
  `fmt: "n2"`). Values cited: A33-53; R2 1.14 [A33-07], 0.90, 0.89 [A33-53]. Note: $n=8$; two-sided normal p-values of
  $\widehat{\mathrm{SR}}\sqrt T$; Holm on the eight rules' own p-values is the book's adaptation of Harvey and Liu;
  the rules are correlated, so independence overstates the haircut (§7).

**Widget `minTrack` — "How long must a record be?"** `Book.controls`: start from (select R1–R8, setting the next
three to that rule's unrounded moments), annual Sharpe ratio (0.2 to 2.5, step 0.0001), skewness (−2 to 1, step
0.0001), raw kurtosis (3 to 25, step 0.001), trials $n$ (select 1, 2, 3, 5, 8, 10, 20, 50, 100, 1,000), observations a year
(select 12, 52, 243.57), confidence (select 90%, 95%, 99%). Readouts: $\E Z_{(n)}$, exact, and approximate for $n\ge2$ (a dash at $n=1$); MinTRL by
(33.5) in observations and years of sessions; PSR(0) and DSR at the through case's 7.60 years of sessions [A33-01],
that is $7.60A$ observations. Chart: DSR against years of sessions
(0.5 to 20, log x), dashed `hline` at the confidence, dashed `vline` at MinTRL. $\E Z_{(n)}$ by module-local Simpson
quadrature of (33.4) on [−10, 10] with `Book.dist.Phi` (under 30 lines), tested against the script's values to 1e-6
as `data/lm15_charts.py` tests its code; quantiles by `Book.dist.PhiInv`. Initial state (PDF): R2, $n=8$, 95%, 243.57 observations a year:
MinTRL 1,796 sessions, 7.37 years of sessions [A33-49], DSR 0.955 [A33-46]; at $n=1$ 2.15 years of sessions [A33-26].
A range input snaps its value to its step, so these steps keep R2's initial readouts at these values, and the
widget's test asserts 1,796 sessions, 7.37 and 2.15 at that state.
Data block `chart-lm33-minTrack`: the eight rules' $\widehat{\mathrm{SR}}$, skewness, raw kurtosis and $T$ (32
numbers).

**Examples** (results recomputed from the printed inputs):

- E1 §2 `r2hand`, R2 by hand: $\bar x=0.0564\%$, $s=0.774\%$, $\widehat{\mathrm{SR}}=0.0729$ a day [A33-15],
  skewness −0.112 and raw kurtosis 13.58 [A33-64]; $\hat V_{\mathrm{SR}}=1+0.0082+0.0167=1.0249$; SE 0.0235 a day,
  0.367 a year; $\widehat{\mathrm{SR}}\sqrt T=3.14$, the t-stat of the mean excess return with divisor $T$, by LM21's
  identity (lm21.md:172) [A33-15]. The skewness term is small because R2's skewness is only −0.112; kurtosis adds
  more.
- E2 §2 `checkpoint`, all eight rules (guidance g:44), on the 1,851 out-of-sample net returns: mean excess returns a
  year from 7.71% (R3) to 13.74% (R2) with iid SEs 3.61% and 4.38% [A33-07, A33-08]; realized volatilities from 9.96%
  (R3, LM30's [A30-12]) to 16.53% (R4) [A33-09], with iid SEs 0.45% and 0.59% [A33-08, A33-09]; raw kurtosis 10.3
  (R4) to 23.0 (R8) [A33-09, A33-13]; the normal SE 0.363 for every rule, (20.9) 0.367 to 0.371 [A33-06 to A33-13].
  The table's volatilities of R1, R3 and R5 are LM30's [A30-12] and those of R6–R8 LM31's [A31-27], echoed at their
  owners' two decimals; R2's and R4's, and every SE, are LM33's (decision A3).
  Every other rule's estimate lies inside R2's interval [A33-14]. R4: two-sided 95% −0.09 to 1.35; one-sided PSR(0)
  0.956 [A33-17]. All eight PSR(0) exceed 0.95, from 0.956 (R4) to 0.999 (R2), and Holm (21.7) on the eight one-sided
  p-values rejects all eight, the largest adjusted p-value 0.044 [A33-16]. The rate $r_f=1.5\%$ is illustrative
  (LM7's). The rules' own paths keep $r_f=1.5\%$: R4's signal uses it, R8's cash earns it, and R8 borrows at
  3.5% (1.5% plus 2 points). Only the rate in the Sharpe ratio changes. At 0% every Sharpe ratio rises by 0.09 to 0.15, the change in rate over the rule's volatility, and at 2% it
  falls by 0.03 to 0.05 [A33-66]. R2 stays the best and R4 the worst; at 2%, R4's PSR(0) is 0.948 and Holm rejects
  seven of the eight [A33-66].
- E3 §3 `hac`, R1, R2 and R4 by lag: R2's SE grows from 0.367 at $\ell=0$ to 0.382 at 7 and 0.393 at 20; R4's falls to
  0.340 at 7 [A33-18]; HAC over (20.9) at $\ell=7$ runs from 0.92 (R4) to 1.04 (R2) [A33-18]. The volatility's SE
  rises by half: HAC over iid 1.51 to 1.60 at $\ell=7$, and the SE of R1's realized volatility, 0.576%, becomes
  0.872%, 1.026% and 1.156% at $\ell=7$, 20, 60 [A33-20]. Days are nearly uncorrelated ($\hat\rho_1$ from −0.054 to 0.002
  [A33-19]); their squares are not. Interval with HAC: R2 0.39 to 1.89 [A33-07].
- E4 §3 `tr23`, the long record (TAIEX total-return index): TR23's 0.81 a year (0.0517 a day), skewness −0.34, raw
  kurtosis 8.27; SE 0.207 by (20.9), as LM20 printed (lm20.md:401), 0.213 by (33.1) at $\ell=9$ and 0.243 at
  $\ell=145$, against LM22's blocks of 145, 0.233 stationary, 0.244 circular, 0.247 moving (lm22.md:216–221)
  [A33-21]. HAC at the block length agrees with the blocks.
- E5 §4 `monthly`, 90 calendar months of log excess returns: R1's monthly ratio 0.305 gives 1.06 by $\sqrt{12}$ and
  0.92 by (19.9) with $\hat\rho_1,\dots,\hat\rho_{11}$; its ratio $1+2\sum_k(1-k/12)\hat\rho_k=1.309$ has a robust SE
  of 0.38 by (25.6) [A33-22], and its excess over 1, 0.309, is 0.78 iid SEs of 0.395 [A33-23]. R2: 1.05 and 0.94;
  R4: 0.62 and 0.49 [A33-22]. The scale factors run from 2.74 to 3.33 against 3.46 [A33-23]. The daily log-return
  ratios, 0.54 (R4) to 1.08 (R2) [A33-25], show the simple-against-log gap separately. (19.9)'s ratio and the
  robust SE of (25.6) are large-$T$ results, and 90 months is a small sample for them. Conclusion: 90 months cannot
  tell whether the correction is needed, and the corrected ratio carries the noise of 11 autocorrelations.
- E6 §5 `mintrl`: R2's PSR(0) 0.999 and MinTRL(0) 523 sessions, 2.15 years of sessions (normal moments 2.10); R1's
  0.996, 720 sessions, 2.96 (2.85); R4's 0.956, 1,717 sessions, 7.05 (6.85) [A33-26], against the 1,851 sessions
  observed [A33-01]. $T$ against $T-1$: R2's z-value 3.097 with $\sqrt{T-1}$, 3.098 with $\sqrt T$, larger by the factor
  $\sqrt{T/(T-1)}=\sqrt{1{,}851/1{,}850}$, that is by 0.027% [A33-27]. TR23, the TAIEX total-return index, with a daily ratio of 0.05173 [A33-21] and E4's skewness −0.34 and raw
  kurtosis 8.27: PSR(0) 0.99995, MinTRL 1,035 sessions, 4.20 years of sessions [A33-28]. (21.4) one-sided at power ½
  gives 4.11 years of sessions from the annual 0.8115 (as lm21.md:183 prints it); LM21's two-sided 80% power needs
  11.9 years of daily data (lm21.md:183) [A33-28]. The published check: Bailey and López de Prado (2012, authors'
  version, p. 11) print a MinTRL of 3.24 years for normal monthly returns and 4.99 years with skewness −0.72 and raw
  kurtosis 5.78; (33.3) with their appendix code's inputs gives 38.9 and 59.9 months, 3.24 and 4.99 years
  (months ÷ 12) [A33-30].
- E7 §6 `lw`, R2 against R1: $\hat\Delta=+0.162$ a year, correlation 0.70, $\operatorname{SE}(\hat\Delta)=0.253$
  ($\ell=7$), t-stat +0.64, HAC p-value 0.52 and HAC normal interval −0.33 to +0.66 [A33-33]. Ledoit and Wolf's
  bootstrap ($b=22$): p-value 0.52 (Monte Carlo SE 0.005), $\hat F^{-1}_{\text{boot}}(0.95)=2.0$ (Monte Carlo SE 0.02) and the interval
  −0.34 to +0.67 [A33-33]. Independent-samples SE 0.521 [A33-40]. If the gap were truly 0.1617 a year, with the SE
  0.2528 of 7.60 years of sessions [A33-33, A33-01], 80% power at 5% two-sided would need 146 years of sessions, and a
  one-sided 95% test at power ½ 50 years of sessions [A33-41]. Experiment 3: block sizes 1, 5, 10, 26, 50 and 100 give p-values
  0.53 to 0.56 [A33-42], against 0.52 at $b=22$ [A33-33]. At $\ell=0$, 7, 22 and 60 the SE is 0.280, 0.253, 0.250
  and 0.243 [A33-40]. All seven pairs: none rejected after Holm, by either p-value; the smallest adjusted p-value is
  1.00 [A33-43].
- E8 §7 `dsr`, R2 deflated: $\E Z_{(8)}=1.424$ (1.4236) [A33-44], so $\mathrm{SR}_0=0.52$ a year (0.517) [A33-45]
  and DSR 0.955; with the approximation 0.951, with R2's HAC SE 0.948; DSR falls to 0.95 at $n=8.8$ [A33-46].
  Correlations: mean 0.821, R3–R5 0.998, R6–R8 0.96, R2–R1 0.70 [A33-47]. Experiment 2: $\E\max$ of $\mathcal
  N_8(\mathbf 0,C)$ 0.588 (Monte Carlo SE 0.0009), $n_{\mathrm{eff}}=2.07$ (2.06 to 2.07 at ±2 Monte Carlo SE),
  $\mathrm{SR}_0=0.21$, DSR 0.994 [A33-48]. Bailey and López de Prado's own interpolation (eq. (9) of their 31 July
  2014 version), $\bar\rho+(1-\bar\rho)8$ at the mean correlation $\bar\rho=0.821$ [A33-47], gives 2.25 [A33-48]. The
  eight estimates have SD 0.141 a year, about the 0.144 that equal true ratios would give [A33-50]. Bailey and López
  de Prado scale the threshold by the standard deviation of the trials' own estimates (their eq. (1)). Here (33.4)
  uses instead the standard deviation of one estimate when the true ratio is zero, $1/\sqrt{T-1}$, 0.363 a year
  [A33-45]. With the eight estimates' standard deviation, 0.141 a year, their recipe gives $\mathrm{SR}_0=0.21$ and
  DSR 0.994 [A33-50]. MinTRL after $n$
  trials (33.5), with E1's $\widehat{\mathrm{SR}}=0.0729$ and $\hat V_{\mathrm{SR}}=1.0249$ [A33-15], in years of sessions: 2.15
  at $n=1$; 7.37 at 8, that is 1,796 sessions from $\E Z_{(8)}=1.4236$; 3.9 at $n_{\mathrm{eff}}$ (one decimal, since
  the second is Monte Carlo noise); 13.5 at 100, from $\E Z_{(100)}=2.508$ [A33-44, A33-49]. The published check:
  Bailey and López de Prado's example (2014, authors' version, pp. 9–10) gives $\mathrm{SR}_0=0.1132$ a day and DSR
  0.9004 at $n=100$ trials, 0.9505 at $n=46$ and, for normal returns, 0.9505 at $n=88$, as they print [A33-51].
- E9 §8 `haircut`, R2: t-stat 3.137, single two-sided p-value 0.00171; adjusted for eight independent tests 0.0136
  (Bonferroni 0.0137); $\text{t-stat}_{\text{adj}}=2.47$; HSR 0.90 a year, a haircut of 21% [A33-54]. At a fixed
  volatility, (4.3)'s fraction falls by the same 21% [A33-56]. The published check: Harvey and Liu's example after
  their eq. (5), in their section "Method" (240 months, 0.75 a year, 200 tests), with the normal reference gives
  0.0008, 0.15 and 0.32, as they print; their "approximately 60%" is (0.75 − 0.32)/0.75, 57% [A33-55]. With $t_{239}$,
  as their eqs. (1) and (3) say, the HSR is 0.31 [A33-55].

**Problems plan** (12; MC keys B, C, A, B, C, A; the lab solves 10, 11 (b), 12). Stems state the sample (E5's through case:
daily net returns 5 March 2019 → 8 October 2026, $T=1{,}851$, $A_{\mathrm w}=243.57$, $r_f=1.5\%$, the rules fixed in
advance, traded monthly with the shared costs, *Out-of-sample*; or the hypothetical inputs), the period of each Sharpe
ratio, raw or excess kurtosis, divisor $T$, normal or (20.9), one- or two-sided, the level, the count behind "years",
and rounding; problems 11 and 12 give the lag, the block size, the last-block handling, $B$ and the seed.

1. MC: normal returns, daily Sharpe ratio 0.06, $T=1{,}851$, $A=243.57$; the annual SE. A 0.0233 (not annualized).
   **B** 0.363. C 5.67 (times $A$, not $\sqrt A$) [A33-57].
2. MC: monthly Sharpe ratio 0.30, skewness −1.0, raw kurtosis 8.0, $T=90$; the SE by (20.9). A 0.124 (excess kurtosis 5
   typed as raw). B 0.108 (normal). **C** 0.127 [A33-58].
3. MC: normal returns, daily Sharpe ratio 0.05, $\mathrm{SR}_0=0$, 95%, $A=243.57$; MinTRL in years of sessions. **A**
   4.45. B 6.32 ($\Phi^{-1}(0.975)$, a two-sided quantile). C 0.028 (the annual ratio in the daily formula) [A33-59].
4. MC: $\E Z_{(5)}$. A 1.193 (the approximation). **B** 1.163. C 1.129 ((21.9)'s median) [A33-60].
5. MC: monthly log returns with $\rho_1=0.1$ and no other autocorrelation; the scale factor to a year. A 3.464
   ($\sqrt{12}$). B 3.833 (the sign of $\rho_1$ reversed). **C** 3.184 [A33-61].
6. MC: two annual Sharpe ratio estimates 1.0 and 0.8, each SE 0.36, whose estimation errors correlate 0.9; the SE
   of their difference by (16.3). **A** 0.161
   (t-stat 1.24). B 0.509 (independent; t-stat 0.39). C 0.036 ($0.36\times(1-0.9)$) [A33-62].
7. Derive (33.3) from (33.2) by setting PSR equal to $1-\alpha$; then (33.5) from (33.4); check that (33.5) at $n=1$ is
   (33.3), and that R2's 1,796 sessions (from E1's 0.0729 and 1.0249 [A33-15] and $\E Z_{(8)}=1.4236$ [A33-44]) [A33-49] lie below its
   1,851 observed [A33-01], consistent with DSR 0.955 [A33-46]; and show that (33.3)
   with $\hat V_{\mathrm{SR}}=1$, $\mathrm{SR}_0=0$ and without the 1 is (21.4) one-sided at power ½.
8. (a) Show $\E\max(Z_1,Z_2)=1/\sqrt\pi=0.5642$ for independent standard normals, from $\max(Z_1,Z_2)=\tfrac12(Z_1+Z_2+\lvert
   Z_1-Z_2\rvert)$, (16.3), (16.7) and (19.2)'s $\E\lvert R-\mu\rvert=\sigma\sqrt{2/\pi}$; compare (33.4)'s integral at
   $n=2$ and the approximation 0.520 [A33-44]. (b) Python: if $Z_1$ and $Z_2$ correlate 0.5, the same
   steps give $\sqrt{0.5/\pi}=0.3989$; the $n$ with $\E Z_{(n)}=0.3989$ by (33.4) is $n_{\mathrm{eff}}=1.608$, against
   1.5 by eq. (9) of Bailey and López de Prado's 31 July 2014 version [A33-67].
9. Haircut (hypothetical): t-stat 2.5, ten independent tests; the single and adjusted p-values 0.01242 and 0.1175,
   $\text{t-stat}_{\text{adj}}=1.565$, haircut 37.4%; Bonferroni's adjusted 0.1242, 1.537 and 38.5% [A33-63]; why
   Bonferroni cuts more; and by how much (4.3)'s fraction falls at a fixed volatility (37.4%; Bonferroni
   38.5%) [A33-63].
10. Python: R1's 90 monthly log excess returns (calendar months); the monthly ratio 0.305, 1.06 by $\sqrt{12}$, 0.92 by
    (19.9), the ratio 1.31 and its robust SE 0.38 by (25.6) [A33-22]; would you apply the correction?
11. (a) Show that at $\ell=0$ the quadratic form $\nabla h^{\top}\hat\Gamma_0\nabla h$ of (33.1) equals
    $\hat V_{\mathrm{SR}}$ term by term, from $\hat\Gamma_0$'s entries $s^2$, $s^3\widehat{\operatorname{Skew}}$ and
    $s^4(\widehat{\operatorname{Kurt}}-1)$. (b) Python: (33.1) for R2 at $\ell=0$, 7, 20, 60: 0.367, 0.382, 0.393,
    0.389 a year [A33-18]; check $\ell=0$ against (20.9).
12. Python: Ledoit and Wolf's test of R4 against R1, $\ell=7$, $b=22$ (85 blocks drawn and cut to 1,851 rows, the
    block covariance from the 84 complete blocks), $B=9{,}999$, seed `[1, 20261011]` (the block starts do not depend
    on the pairs, so one pair reproduces experiment 1): $\hat\Delta=-0.347$, SE 0.285, HAC p-value 0.22 and HAC
    normal interval −0.91 to +0.21; bootstrap p-value 0.25 (Monte Carlo SE 0.004),
    $\hat F^{-1}_{\text{boot}}(0.95)=2.1$ (Monte Carlo SE 0.02), interval −0.95 to +0.25 [A33-35]. (b) Apply Holm (21.7) to the seven
    HAC p-values of [[ex:case]] (b): every adjusted p-value is 1.00 [A33-43].

**Lab parts** (`build/make_lab33.py`; reads only its `data/`: the eight rules' net wealth paths on the wealth frame's
dates, a derived file from `data/make_lab_data.py` built locally and never committed (shared decision "Labs"), and
`taiex_tr.csv` (TR23)): 1 data: $R_t$, $x_t$, $T$, $A_{\mathrm w}$, the 90 calendar months, a check against the
criteria's Sharpe ratios; 2 X1, X2, E1, E2, `scipy.stats` with `fisher=False, bias=True` passed; 3 (33.1) by hand, X3,
E3, E4, problem 11 (b); 4 E5, Lo's AR(1) check, problem 10; 5 X4, E6, the 2012 appendix example; 6 Ledoit and Wolf by
hand, X5, E7, problem 12, experiments 1 and 3; 7 (33.4) by quadrature against the approximation, experiment 2, X6,
E8, the 2014 example; 8 X7, E9, Harvey and Liu's example. Extension (*Stability check*): R2's PSR(0) on rolling
windows of 730 sessions (about three years of sessions), with a closing sentence that picking a window after seeing
the curve is one more trial ([[LM34]]'s subject; the lab writes plain "LM34").

**Cross-module tags** (decision C8: each lists only the later modules that cite it).

- (33.1) $\operatorname{SE}_{\mathrm{HAC}}(\widehat{\mathrm{SR}})=\sqrt{\nabla h^{\top}\hat\Psi\nabla h/T}$, $\nabla
  h=(1/s,\,-\bar x/(2s^3))^{\top}$, $\hat\Psi$ by (23.7) on $\mathbf v_t=(x_t-\bar x,\,(x_t-\bar x)^2-s^2)^{\top}$ with
  the book's lag; at $\ell=0$ it is (20.9)'s plug-in; stationary returns with fading (mixing) dependence and a finite moment of
  order a little above 4 (Ledoit and Wolf's p. 852, for the same delta method), large $T$ (stated). Cited by LM35 (the lab checkpoint's interval).
- (33.2) $\operatorname{PSR}(\mathrm{SR}_0)=\Phi\big((\widehat{\mathrm{SR}}-\mathrm{SR}_0)\sqrt{T-1}/\sqrt{\hat
  V_{\mathrm{SR}}}\big)$, one minus the one-sided p-value of $H_0:\mathrm{SR}\le\mathrm{SR}_0$; per observation. No
  later brief cites it.
- (33.3) $\mathrm{MinTRL}=1+\hat V_{\mathrm{SR}}\big(\Phi^{-1}(1-\alpha)/(\widehat{\mathrm{SR}}-\mathrm{SR}_0)\big)^2$
  observations, for $\widehat{\mathrm{SR}}>\mathrm{SR}_0$; with $\hat V_{\mathrm{SR}}=1$, $\mathrm{SR}_0=0$ and without
  the 1 it is (21.4) one-sided at power ½. No later brief cites it.
- (33.4) $\E Z_{(n)}=\int_0^\infty(1-\Phi(z)^n)\,dz-\int_{-\infty}^0\Phi(z)^n\,dz$; DSR $=\operatorname{PSR}(\E
  Z_{(n)}/\sqrt{T-1})$, iid trials with true ratio zero under $H_0$, on the null scale $1/\sqrt{T-1}$ of one estimate
  (the book's; Bailey and López de Prado's eq. (1) scales by the standard deviation of the trials' own estimates); the
  approximation
  $(1-\gamma_{\mathrm E})\Phi^{-1}(1-1/n)+\gamma_{\mathrm E}\Phi^{-1}(1-1/(ne))$ stated. No later brief cites it (LM34
  cites the deflated ratio by pointer).
- (33.5) $T\ge1+\big((\Phi^{-1}(1-\alpha)\sqrt{\hat V_{\mathrm{SR}}}+\E Z_{(n)})/\widehat{\mathrm{SR}}\big)^2$, the
  track record that makes DSR $\ge1-\alpha$ after $n$ trials, for $\widehat{\mathrm{SR}}>0$ (with
  $\widehat{\mathrm{SR}}\le0$ no record length suffices). No later brief cites it.
- (33.6) $\operatorname{SE}(\hat\Delta)=\sqrt{\nabla h^{\top}\hat\Psi\nabla h/T}$ for
  $h(\boldsymbol\theta)=\theta_1/\sqrt{\theta_3-\theta_1^2}-\theta_2/\sqrt{\theta_4-\theta_2^2}$ at
  $\hat{\boldsymbol\theta}=(\bar x_j,\bar x_1,\overline{x_j^2},\overline{x_1^2})$, $\hat\Psi$ by (23.7) on
  $\mathbf v_t=(x_{j,t}-\bar x_j,\,x_{1,t}-\bar x_1,\,x_{j,t}^2-\overline{x_j^2},\,x_{1,t}^2-\overline{x_1^2})^{\top}$; the bootstrap
  p-value $\big(\#\{i:\lvert\hat\Delta_{\text{boot},i}-\hat\Delta\rvert/\operatorname{SE}(\hat\Delta_{\text{boot},i})\ge
  \lvert\hat\Delta\rvert/\operatorname{SE}(\hat\Delta)\}+1\big)/(B+1)$ with circular blocks (Ledoit and Wolf's
  Remark 3.2, eq. (9)). No later brief cites it (LM34 cites the tests by pointer).
- (33.7) adjusted p-value $1-(1-\text{p-value})^n$ (independent tests), $\min(1,n\,\text{p-value})$ (Bonferroni) or
  (21.7)'s; $\mathrm{HSR}=\Phi^{-1}(1-\text{adjusted p-value}/2)/\sqrt T$ per observation. No later brief cites it.

**Pitfalls to pre-empt.**

- Raw against excess kurtosis: (20.9), PSR and MinTRL take raw kurtosis; `scipy.stats.kurtosis` returns excess by
  default (10.58 against 13.58 for R2 [A33-64]); the raw 8.27 of TR23, the TAIEX total-return index (lm20.md:370,
  388, 403), is excess 5.27 (lm19.md:20),
  and 0050's 8.12 in LM4–LM5 (lm04.md:132) is excess. Problem 2's distractor is this error.
- Moments the formulas need (PITFALLS §7): (20.9) needs a finite fourth moment; (33.1) and Ledoit and Wolf's (4)
  need a finite moment of order a little above 4 and a mixing condition for time series (their p. 852); the rules'
  raw kurtosis
  runs to 23.0 (R8) [A33-13] and carries no standard error itself (LM20's pitfall).
- One-sided against two-sided: PSR, MinTRL and DSR are one-sided at 95%; the intervals and (21.4) are two-sided; R4 sits
  between [A33-17]. Never compare a PSR with a two-sided interval without saying so.
- $\mathrm{SR}_0$ is a fixed benchmark. Setting it to another rule's estimate ignores that estimate's error (106 years
  of sessions, [A33-31]); comparing two rules is (33.6).
- Correlated rules: the independent-samples error of a difference is about twice Ledoit and Wolf's here (0.52 against
  0.25 [A33-40]); yet even the right error leaves the gap far inside noise.
- PSR is not a probability that the true ratio exceeds $\mathrm{SR}_0$ without a prior ([[LM24]]); Bailey and López de
  Prado's wording is paraphrased with that caveat.
- The count of trials: $n=8$ treats the rules as independent; they correlate 0.82 on average [A33-47], so
  $n_{\mathrm{eff}}=2.07$ [A33-48]. The in-sample variants of LM28–LM31 are not candidates (shared decision); had 100
  versions been tried, R2 would need 13.5 years of sessions [A33-49]. Say which $n$ every DSR uses.
- A DSR near the line: 0.955 by the exact integral, 0.951 by the approximation, 0.948 with the HAC error [A33-46]. Print
  the number and its method, never "passes".
- Holm's haircut keeps a running maximum: R6, R7 and R8 share 0.71 and R4 keeps its whole ratio [A33-53]; it is not
  "no correction".
- Annualization: $\sqrt A$ on simple returns is a convention (LM19); the criteria's Sharpe ratios are on simple returns,
  Lo's correction on log returns; say which in every caption (E5).
- Two counts of years: the record's 7.60 calendar years and its 7.60 years of sessions agree here (7.5975 and 7.5995
  [A33-01]), but a MinTRL is a count of sessions; compare it with the record in sessions (decision C7).
- Bootstrap: Ledoit and Wolf centre the resampled statistic at $\hat\Delta$ (they resample the data, not a null world);
  a count of uncentred $\lvert\hat\Delta_{\text{boot},i}\rvert$ would test nothing. The "+1" makes the p-value never 0.
  Two decimals only (Monte Carlo SE 0.005 [A33-33]). With $T$ not a multiple of $b$, say how the last block is handled:
  Ledoit and Wolf's paper does not say, the book's convention is the shared one, and the independent recomputation
  found that another handling moves a printed second decimal.
- The block-length rule takes the stationary estimate (lm22.md:254) even for circular blocks, as LM22 did (145 for
  every scheme); here that is 22, against the circular estimate's 26 [A33-32]. The choice moves nothing that is
  printed in a conclusion: $b$ from 1 to 100 gives 0.52 to 0.56 [A33-33, A33-42].
- Ownership: the volatilities of R1, R3, R5 (LM30, A30-12) and R6–R8 (LM31, A31-27) are echoed; net wealth, log growth,
  turnover and gross against net are LM34's; nothing re-implements a rule.

**Curriculum guidance carried** (`plans/vol-5.md`'s table):

- g:30, the layer added: §1 says it (Volume IV gave one ratio an error bar; LM33 compares rules and corrects for
  picking the best).
- g:44, Volume IV's checkpoint: §2 does it on the through case (E2, X1, X2).
- g:54–58, outcome levels: [D] 2 and 4, [C] 1, 3, 5, 6 and 8, [U] 7.
- g:111, fixed in advance: every caption and the hygiene note say the rules were fixed on 24 October 2026.
- g:116, "the data are too thin to support more leverage" is a valid conclusion: the case's verdict (§6–§8), E7's 146
  years of sessions.
- g:124, taught, practised, assessed: the outcome table above.

**Stage 4 for earlier modules.** `leads` gain 33 in lm04.md:6 and lm18.md:6 (decision G's merged list; LM33 cites
(18.2) and lm18.md:151). LM16, LM19–LM25 already list 33; the Volume V briefs' leads should include 33 (each brief's own
list), and LM35's prerequisites gain 33 (decision C9). Every forward link above is honoured as written (lm21.md:373
is reworded in LM34's wording, which keeps LM33's part). One rewording is required ("Decisions on the third revision",
LM33; the owner's rule that every citation is checked to exist as cited): lm19.md:359 states Lo's "as much as 65%"
"for a hedge fund in his illustrative example" (Lo 2002, p. 36), as `plans/vol-5.md`'s Stage 4 list records.

**Sources** (verified 2026-10-24 in the versions named; paraphrased, nothing quoted beyond a phrase; bibliographic data
from Crossref unless another record is named; the entries match `project/SOURCES.md`, and where an entry records
a difference from the earlier brief, the entry is followed):

- Lo, A. W., "The Statistics of Sharpe Ratios", *Financial Analysts Journal* 58(4): 36–52, July 2002, DOI
  10.2469/faj.v58.n4.2453. In SOURCES under LM19 and LM20; the Volume VI locations below are added. Read in the
  journal's layout, a copy posted by a university student group (neither the author's nor the publisher's; no open
  copy of either exists), with the abstract confirmed on the journal's own article page (the second source hunt; the editor
  kept its locations, "Sources read by the second hunt"):
  - Lo's IID formula: $V_{\mathrm{IID}}$, eq. (8), and the standard error $\sqrt{(1+\mathrm{SR}^2/2)/T}$, eq. (9),
    p. 38. Its variance of the variance estimate, $2\sigma^4/T$, is the normal value, so the brief writes "Lo's IID
    formula (9)" and calls the book's version "normal"; "iid-normal" is not Lo's label.
  - The GMM standard error, eqs. (14)–(15), pp. 39–40, with Newey–West weights $1-j/(m+1)$ and divisor $T$,
    (A12)–(A14), p. 47: (23.7)'s weights and divisor, so (33.1) is Lo's GMM standard error with the book's lag (§3's
    sentence).
  - The scale factor for aggregated returns, eq. (20), p. 40, derived for sums of returns with compounding ignored,
    which is E5's setting of monthly log returns.
  - The AR(1) form, eq. (22), and Table 2, p. 41: 2.88 at a monthly first-order autocorrelation of 20% and $q=12$, and
    3.46 for iid returns, both also stated in the text beside the table (recomputed, A33-24).
  - The abstract's "as much as 65 percent", p. 36, is for a hedge fund in his illustrative example of mutual and hedge
    funds; the module does not print the figure, and lm19.md:359, which drops the scope, gains it at Stage 4 (required).
  - Not Lo's: (25.6), the noise of the correction, and E5's numbers are the book's own.
- Bailey, D. H., and M. López de Prado, "The Sharpe Ratio Efficient Frontier", *Journal of Risk* 15(2): 3–44,
  December 2012 (Crossref: online December 2012, no print date), DOI 10.21314/jor.2012.255; SSRN 1821643. Read in the
  authors' version of July 2012 (the survey, the drafter and the source check of decision F): the estimate's asymptotic
  distribution, (8), and the $n-1$ (Bessel's correction) in its standard deviation, §2.5, p. 8; PSR, eq. (11), p. 9,
  with $\sqrt{n-1}$ and raw kurtosis; MinTRL, eqs. (12)–(13), pp. 10–11, counted in observations, with the "1 +" term;
  the examples, p. 11, among them 3.24 years (months ÷ 12) for normal monthly returns and 4.99 years with skewness
  −0.72 and kurtosis 5.78, both reproduced (A33-30) from the inputs of the code in Appendix A.3, p. 20 (monthly mean 2, standard deviation
  $\sqrt{12}$, reference $1/\sqrt{12}$; the page prints 59.895 months). Equation and page numbers are the authors'
  version's, and the text says so; the journal's were not compared.
- Bailey, D. H., and M. López de Prado, "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest
  Overfitting, and Non-Normality", *Journal of Portfolio Management* 40(5): 94–107, 2014 (Crossref: print and online
  30 September 2014), DOI 10.3905/jpm.2014.40.5.094; SSRN 2460551. Read in the authors' version of 31 July 2014 (the
  survey, the drafter and the source check): the expected maximum of $N$ independent trials with the Euler–Mascheroni
  constant, eq. (1), p. 7, derived in Appendix A.1, eqs. (3)–(6), p. 12; DSR, eq. (2), p. 8, a PSR at eq. (1)'s
  threshold without its mean term, with $\sqrt{T-1}$ and raw kurtosis (eq. (1) scales by the standard deviation of
  the trials' estimated Sharpe ratios, the example's variance ½; (33.4)'s $1/\sqrt{T-1}$ is the book's); the example, pp. 9–10 ($N=100$, variance ½,
  $T=1{,}250$, skewness −3, kurtosis 10: threshold ≈ 0.1132 and DSR ≈ 0.9004; 0.9505 at $N=46$; 0.9505 at $N=88$ for
  normal returns; reproduced, A33-51); eq. (9), Appendix A.3, p. 14, the implied number of independent trials
  $\hat N=\hat\rho+(1-\hat\rho)M$ with $\hat\rho$ the average correlation of eq. (8), not the expected maximum (printed
  as A33-48's 2.25, cited "eq. (9) of the authors' 31 July 2014 version"). The journal's equation numbers were not
  compared.
- Ledoit, O., and M. Wolf, "Robust performance hypothesis testing with the Sharpe ratio", *Journal of Empirical
  Finance* 15(5): 850–859, December 2008, DOI 10.1016/j.jempfin.2008.03.002 (Crossref spells the first author
  "Oliver"). The drafter read IEW Working Paper 320 (January 2008); the source check read the journal text (the
  published article hosted at UZH), whose numbers the brief cites:
  - §3, pp. 851–852: the parameter as a function of the means and uncentred second moments, (1)–(2), the delta method
    (4) and the standard error (5); p. 852: finite fourth moments for iid data, and a moment of order a little above 4
    with a mixing condition for time series.
  - §3.1, pp. 852–853: HAC inference with a kernel estimate and a $T/(T-4)$ degrees-of-freedom factor, Bartlett named as
    the $q=1$ kernel; the normal p-value and interval, p. 853.
  - §3.2, p. 853: the test inverts a symmetric studentized interval, (6)–(7), resampling the observed data.
  - §3.2.2, p. 854: the circular block bootstrap of return pairs with a fixed $b$ (footnote 7: circular rather than
    moving blocks; footnote 8: a prewhitened Parzen kernel does about as well); the original-data standard error by
    Andrews and Monahan's prewhitened quadratic-spectral kernel; the Götze–Künsch standard error in each resample on
    the $\lfloor T/b\rfloor$ complete blocks, centred at the resample's own estimates, (8) (footnote 9: $b=1$ is the
    iid case).
  - Algorithm 3.1, pp. 854–855, calibrates $b$ on a fitted model; Remark 3.2, eq. (9), p. 855, the p-value
    $(\#\{\tilde d^{*}\ge d\}+1)/(M+1)$ (the journal omits the "#").
  - The paper does not say how a resample is cut when $T$ is not a multiple of $b$. The text labels three settings as
    the book's (Bartlett with $\ell=7$; $b$ by LM22's rule; the resample's length) and cites the JEF text's footnote
    numbers only (the working paper's footnote 5 is the JEF's 7).
- Harvey, C. R., and Y. Liu, "Backtesting", *Journal of Portfolio Management* 42(1): 13–28, 2015 (Crossref: print and
  online 31 October 2015), DOI 10.3905/jpm.2015.42.1.013. Read in the JPM layout hosted at Duke (the drafter and the
  source check). That copy's running heads number its pages 12–28 and Crossref gives 13–28, so the brief and the module
  cite sections and equations, not pages:
  - Section "Method": the t-statistic $\hat\mu/(\hat\sigma/\sqrt T)$, with $T-1$ degrees of freedom under iid normal
    returns, eq. (1); the Sharpe ratio, eq. (2); the single-test p-value, eq. (3); $p^M=1-(1-p^S)^N$ for $N$ independent
    tests, eq. (4); the haircut Sharpe ratio, eq. (5), and the haircut; the example after eq. (5) (240 months, 0.75 a
    year: $p^S=0.0008$; with $N=200$, $p^M=0.15$, HSR 0.32, "approximately 60%"), reproduced with the normal reference
    (A33-55).
  - Section "Multiple Testing Framework": Bonferroni and Holm under the family-wise error rate (its subsection
    "P-value Adjustment under FWER"), BHY under the false discovery rate ("P-value Adjustment under FDR"); for Holm
    and BHY the other p-values come from a model of more than 300 factors, described in the FDR subsection. So Holm on
    the eight rules' own p-values is the book's adaptation and says so; Bonferroni and the independent-tests form are
    theirs directly.
- Götze, F., and H. R. Künsch, "Second-order correctness of the blockwise bootstrap for stationary observations",
  *Annals of Statistics* 24(5): 1914–1933, October 1996, DOI 10.1214/aos/1069362303. Bibliographic data only: named as
  Ledoit and Wolf's source for the resample's standard error.
- Andrews, D. W. K., and J. C. Monahan, "An Improved Heteroskedasticity and Autocorrelation Consistent Covariance
  Matrix Estimator", *Econometrica* 60(4): 953–966, July 1992, DOI 10.2307/2951574. Crossref holds the first page only;
  the end page 966 comes from the Econometric Society's article page and RePEc's record of the journal (the second
  source hunt),
  and Crossref's issue listing starts the next article at p. 967. Their abstract and Cowles Foundation Discussion Paper
  942 (1990), §1, p. 3: prewhitened kernel estimators with a vector autoregression in the prewhitening stage. The
  journal text was not read; the module names the paper once, as the source of Ledoit and Wolf's prewhitened kernel,
  and relies on nothing in it.
- Named once and not relied on: Jobson and Korkie (1981), *Journal of Finance* 36(4): 889–908, in SOURCES (LM22),
  bibliographic data only; Opdyke, J. D., "Comparing Sharpe ratios: So where are the p-values?", *Journal of Asset
  Management* 8(5): 308–336, 2007 (Crossref: online 30 November 2007, print December 2007), DOI
  10.1057/palgrave.jam.2250084, abstract only, not cited unless the text needs it.
- Through earlier modules (SOURCES): Newey and West (1987) and the lag rule (LM23; Crossref holds the first page, 703,
  only); Politis and Romano's circular blocks via Lahiri (2003) §2.7.1, p. 33, and LM22 (the 1992 original is unread, as
  SOURCES says); Politis and White (2004) with Patton, Politis and White (2009) for `optimal_block_length` (LM22).
- Not cited: Memmel (2003) (unverified in SOURCES); Mertens (2002) (no copy and no Crossref record, so its content is
  unverified; LM20 derives (20.9) without it); Harvey, Liu and Zhu, the source of Harvey and Liu's factor model (LM34's,
  if anyone's).
- Kept out, as the source reports say: Lo's numbers under a label he does not use, and his 65 percent without its
  scope; Harvey and Liu's page numbers; Bailey and López de Prado's journal pages and equation numbers; Ledoit and
  Wolf's working-paper footnote numbers; any of the book's three bootstrap settings, Holm on the rules' own p-values, or
  (33.4)'s null scale $1/\sqrt{T-1}$, presented as the authors'.
- Python: SciPy 1.18.1's `stats.kurtosis` defaults (`fisher=True`, `bias=True`) checked by running them (A33-64); arch
  8.0.0's `optimal_block_length` returns `stationary` and `circular` columns (A33-32).

**Chinese terms** (AUTHORING §1; English in parentheses at first use in each box; 樂詞網 searched 2026-10-24 by the
fresh pass of 1,817 searches, and the decisions' "Chinese terms" bullet of the second recomputation):

- 樂詞網, statistics listing: 夏普比率 (Sharpe ratio), 偏態 (skewness), 峰態 (kurtosis), 選擇偏誤 (selection bias;
  the listing gives 選擇偏誤；選擇偏差), Student化信賴區間 (studentized confidence interval, the listing's form, which
  the decision keeps), 單邊檢定 (one-sided test, the listing's entry for that term and LM25's form, lm25.md:264; the
  listing gives 單尾檢定 to "one-tailed test"), 序列相關 (serial correlation, also in the mathematics listing; LM33
  writes the book's 自我相關 instead, LM19's term for the same concept).
- 樂詞網, statistics and mathematics listings: 順序統計量 (order statistic, as lm14.md:603), Euler 常數 (Euler's
  constant; both listings write Euler常數, and the book puts a space after a Latin name, as LM16's Mahalanobis 距離).
- The book's settled forms: 標準誤 (standard error), 自我相關 (autocorrelation, LM19), 變異數非齊一與自我相關一致估計量
  (HAC, LM23), delta 法 (delta method, LM20), 檢定力 (power, LM21), 多重假設檢定 (multiple testing) and 族系誤差率
  (family-wise error rate, LM21), 循環區塊 (circular block) and 區塊自助重抽法 (block bootstrap, LM22), 資料偵伺 (data
  snooping, LM21).
- No entry in any listing ("long-run variance", "expected maximum", "haircut", "deflated", "track record", "effective
  number"): PSR, DSR, MinTRL and haircut stay in English in every box, glossed in plain Chinese (for example
  考慮試驗次數後的夏普比率); 長期變異數 (long-run variance) is the book's own form, labelled so in the Glossary.

**Open before Stage 2** (each with a recommendation).

Settled by the editor's decisions of 2026-10-24 and closed here: the block size ($b=22$, LM22's rule as written, the
circular scheme on the same length, the last block as the shared "Counting" decision says; decision D); the HAC kernel
(Bartlett with $\ell=7$, Ledoit and Wolf's prewhitened quadratic-spectral kernel named once; D); the owners of the
checkpoint's means and volatilities (A3, A4; the five other volatilities echoed with A30-12 and A31-27 at their owners'
precision, C12); $T$ against $T-1$ ($\sqrt{T-1}$ as Bailey and López de Prado, one sentence on (20.9)'s $\sqrt T$,
0.027% [A33-27]; D); the effective number of trials ($n=8$ as the headline, 0.955 [A33-46], with
$n_{\mathrm{eff}}=2.07$ beside it [A33-48]; D), and its MinTRL printed as 3.9 years of sessions ("Decisions on the second
recomputation"); a DSR on the line (the number and its method, never a pass or fail; D); the lab's data (the eight
rules' net wealth paths, shared "Labs"); the notation (HSR, $b$, $\hat V_{\mathrm{SR}}$, $\mathbf v_t$, $\Psi$ accepted as
local symbols, B5; a moment of order a little above 4 in words, Y9); the widget's quadrature (module-local code under 30
lines tested against Python, shared "Widgets"); LM31's volatility promise (dropped from LM31, nothing added here); the
flag marks (none in this text, C11).

Closed by the source check of decision F: Ledoit and Wolf's journal text (the JEF §3 has the script's scheme, so the
bootstrap numbers are printed beside the HAC test in the case, X1 (b), X5, E7, problem 12 and the lab, with the book's
three settings labelled); Bailey and López de Prado's eq. (9) (it is $\hat N=\hat\rho+(1-\hat\rho)M$, so E8 prints 2.25
beside 2.07 [A33-48]); the printed values of the published examples, each cited with its location under Sources.

Closed in this revision:

- **The series behind $b$** (the old item 1). The shared "Counting" decision now reads "for a statistic of several
  series' own returns, the largest length among them, as LM33's Ledoit–Wolf test", and "Decisions on the first
  revision" keep $b=22$. The Bootstrap paragraph above follows both; the estimate on the differences from R1 (37,
  [A33-32]) stays a comparison only.
- **Andrews and Monahan's pages** (the old item 3): 953–966, from the Econometric Society's article page and RePEc's
  record (the second source hunt; "Sources read by the second hunt"), cited so under Sources.
- **Lo's copy and labels.** The second hunt read the journal's layout in a student group's copy, with the abstract on
  the journal's own article page; the editor kept its locations, written "Lo's IID formula (9)". Lo's p. 41 is confirmed by
  the second recomputation and the second hunt.
- **Harvey and Liu's pages.** The brief cites their sections and equations (E9, Sources), since the hosted copy's page
  numbers differ from Crossref's.
- **The illustrative $r_f$** (shared decision "Risk-free rate", missed by the earlier versions). E2 says that 1.5% is
  illustrative and what 0% or 2% would change [A33-66]: the order's ends stay, but at 2% R4's PSR(0) falls below 0.95
  and Holm rejects seven of the eight, so E2's "all eight" carries its rate. The editor kept A33-66 ("Decisions on the
  third revision"): only the rate in the Sharpe ratio changes, the rules' paths keeping $r_f=1.5\%$ (R4's signal and R8's cash;
  R8 borrows at 3.5%), and E2 and A33-66 say so.
- **lm19.md:359's scope** (the old item 2, from the second hunt). LM19 prints Lo's "as much as 65%" without his scope.
  The editor made the rewording a required Stage 4 item ("for a hedge fund in his illustrative example"; "Decisions on
  the third revision"); see "Stage 4 for earlier modules". LM33 does not print the figure, so nothing in LM33 waits
  on it.

Closed by the fresh check of Stage 1 (2026-10-31):

- **Harvey and Liu's sections** (the old item 1 of "Still open"; the editor's choice (A) on B33-05). A source agent
  read the headings in the Duke copy on 2026-10-31: the section names the brief uses, "Method" and "Multiple Testing
  Framework", are right, and the Harvey and Liu entry of `project/SOURCES.md` now records every section and subsection
  title with what each holds, so SOURCES and the text cite the same locations. E9, Sources and A33-55 keep their
  section names.
- **Assessment of outcomes 2 and 4 to 7** (B33-03, B33-04, choice (A)): problem 11 (a) derives (33.1) at $\ell=0$;
  problems 7, 8 (b), 9 and 12 (b) assess power, $n_{\mathrm{eff}}$ (A33-67), sizing and Holm; the Sections table keeps
  the total at 5,480 words.
- **Monte Carlo digits of the bootstrap quantile** (B33-21): $\hat F^{-1}_{\text{boot}}(0.95)$ prints one decimal with
  its batch-means Monte Carlo SE, 0.02, and the interval ends' SE is at most 0.006 (A33-33 to A33-39).

Still open: none.

## LM34 Backtesting Without Fooling Yourself

Stage 1 brief, drafted 2026-10-24 from the editor's spine (`plans/vol-5.md`, "### LM34 Backtesting Without Fooling
Yourself") and the shared decisions above it, and revised three times the same day: to the editor's decisions on the
briefs and decision F's source check (Hansen, Romano and Wolf, Bailey et al., the Ministry of Finance and TWSE); to
the decisions on the first revision; and to the second recomputation, the second cross-check (Y items), the second
source hunt (the Ministry's tax ruling, the six survivorship funds, TWSE's overview page) and the "Decisions on the
second recomputation and cross-check" (`plans/vol-5.md`, 2026-10-24). A fresh verifier's check of the third revision
was applied on 2026-10-25 (the six funds' sources, the case box's count, the lab's extension, A34-23's label), and a
last pass the same day applied its re-check and the "Decisions on the third revision" (B6's written-out product, the
extension accepted, problem 9's 4.14, the `TaiwanStockInfo` query in SOURCES, and the listing markets: 00679B trades
on TPEx, so TPEx's rules stand beside TWSE's). The fresh check of the whole of Stage 1 (2026-10-31) was applied
with the editor's choices: both TR23 rules follow §2's protocol (problems 8 and 9, lab part 7; A34-16 and A34-17
recomputed), (34.3) states White's conditions as read in the published article and §6 says what large $T$ means,
the word plan is fixed, and A34-38 prints the rules' growth at $r_f$ of 0% and 2%; the changed anchors were reproduced by the fresh verification of 2026-10-31. Every number carries its anchor ID at first appearance;
`data/vol6_anchors_lm34.py` prints them all from the registered files (38 rows, A34-21 withdrawn; `## LM34` of
`plans/vol-6-anchors.md`). Numbers quoted from published modules carry their file:line; values another module owns
("Owners", shared decision "Through case", and decisions A4–A5) are echoed with that module's anchor ID at its
precision (decision C12) and are not LM34's to print. LM34's survivorship files are registered (`data/raw/vol6/`,
`data/README.md`). Values near a rounding boundary are flagged in the anchors table only (decision C11); this brief
prints each rounded from its unrounded value.

**Prereq:** `[4, 11, 17, 18, 20, 21, 22, 23, 26, 27, 28, 29, 30, 31, 33]`. What each supplies (tags rechecked in `src/`;
LM27–LM33 are briefs, so their results are named, with the tags their briefs propose):

- LM4: (4.5), the condition $\bar g'(f)=\frac1T\sum_tR_t/(1+fR_t)=0$ whose root is the in-sample Kelly fraction
  (lm04.md:180), for the lab's walk-forward and problem 9; "a grid search returns the highest bump, which is largely
  noise" (lm04.md:209), which §7 measures; "backtests overstate Sharpe ratios" (lm04.md:563).
- LM11: the definition of an out-of-sample test, "fits on earlier data and judges on later data that the fit never
  used" (lm11.md:406), which §2 turns into a protocol.
- LM17: (17.3), $\frac1m\ln(W_m/W_0)\to g$ (lm17.md:193), the reason log growth is the criterion; (17.5), the central
  limit theorem (lm17.md:276), behind every normal approximation in §6 and §7.
- LM18: (18.2), the standard error $s_Y/\sqrt n$ of a Monte Carlo mean (lm18.md:141), applied to proportions as
  $\sqrt{p(1-p)/B}$; (18.8), the iid bootstrap's moments (lm18.md:337); "a bootstrap is no test on later data"
  (lm18.md:50, 389).
- LM20: (20.9), $T\Var(\widehat{\mathrm{SR}})\approx1-\mathrm{SR}\operatorname{Skew}+\dots$ (lm20.md:382), which at
  $\mathrm{SR}=0$ gives a per-day standard error $1/\sqrt{920}$ over the 920 in-sample days of E10 and problem 12.
- LM21: (21.1) the t-stat with $s_{\mathrm u}$ (lm21.md:115); (21.2) its one-sided p-value (lm21.md:76); (21.6)
  Bonferroni's bound (lm21.md:267); (21.9) $\Pr(\max_iZ_i\le x)=\Phi(x)^m$ for independent normals (lm21.md:353),
  read as $n$ trials (shared notation decision); Experiment 10, 10,000 random long–short rules on TR23 (the TAIEX
  total-return index) with `default_rng([10, 20261011])`, best t-stat 3.97 (rule 7,840), 13 at or above 3
  (lm21.md:359–364), recomputed [A34-22]; the rule that every module counts its tests.
- LM22: (22.3), the stationary bootstrap's geometric block lengths (lm22.md:189), and its `stationary_idx`
  (lm22.md:372–380), which §6 and the script reuse; (22.4), a bootstrap p-value as a share of resampled statistics
  (lm22.md:337); the book's block-length rule, "the largest stationary estimate among the squared demeaned
  simple-return series the statistic involves, rounded" (lm22.md:254), 145 for TR23, the total-return index
  (lm22.md:427), applied to the differences from R1 for a comparison with R1 (shared decision "Counting"); the
  total-return index's exact in-sample Kelly root $\hat f^*=4.14$ (lm22.md:125, [[LM17]]'s), which problem 9 prints as
  LM22 does; A34-17 recomputes it and shows that the printed 4.14 gives problem 9's printed growth [A34-17].
- LM23: (23.1), OLS, for the performance-degradation slope of §7; "data snooping that [[LM34]] treats"
  (lm23.md:369).
- LM26: (26.2), the EWMA with $\lambda=0.94$ (lm26.md:99; LM26 prints it on log returns, lm26.md:47), for problem
  8's daily scale on daily simple returns in decimals, as R8 uses it, run through each window as R8 runs it; (26.8),
  QLIKE (lm26.md:361), named in §2 as the loss on which a volatility model's choice would be judged on later data
  (lm26.md:54, `make_lab26.py:1115`).
- LM27 (brief): E5's wealth frame, (27.1) the book's return and drift, (27.2) the self-financing trade with
  $\operatorname{cost}(\mathbf x)=0.1425\%\lVert\mathbf x\rVert_1+\sum_i\text{tax}_i\max(0,-x_i)$, (27.3) $\mathrm{TO}_t$;
  R1 and R2; the cost arithmetic of a single trade (decision A5): the first purchase (A27-23), R1's largest rebalance
  (A27-24) and a switch of NT\$1 million between two funds (A27-43), echoed in E2.
- LM28–LM30 (briefs): R3 and R4 (LM28 unconstrained, LM29 long-only, the through-case form), R5 (LM30).
- LM31 (brief): R6, R7 and R8 ((31.7), R8's exposure $L_t$); R8's exposure path (A31-29), echoed in E3.
- LM33 (brief): the rules' Sharpe ratios, their tests against R1 and the deflated Sharpe ratio for $n=8$ with an
  effective number of trials, all cited by pointer in §6 and §8; LM34 prints none of them.

**Leads:** `[35, 45, 46, 48, 49, 50]`: LM35 (its adjusted prices carry their build date as (34.2)'s
$P^{\mathrm{adj}}_{t\mid t'}$, decision B6; it cites LM34's net log growth and cost sources); LM45, LM46, LM48, LM49 and
LM50, which the text points to forward (§2, §3 and §8, "Uses before taught"; decision C9 adds 46). The Volume VIII–IX
briefs, not yet written, decide which tags they cite.

**Forward links honoured.**

| Earlier text | Promise | Kept in |
|:--|:--|:--|
| lm04.md:209 | a grid search returns "the highest bump, which is largely noise" | §7, X7, E9: the declared grid's best, 18.62% a year against a median of 10.96% [A34-27]; PBO 0.663 [A34-29] |
| lm04.md:563 | "Backtests overstate Sharpe ratios ([[LM33]], [[LM34]])" | §6–§8: why the best of a search overstates (E7, E10); sizing from a haircut stays [[LM33]]'s and [[LM45]]'s |
| lm11.md:406 | an out-of-sample test fits on earlier data and judges on later data ([[LM34]]) | §2: the walk-forward protocol and its timing |
| lm17.md:51, lm21.md:57, lm25.md:54, lm26.md:54 | "Nothing is tested on later data ([[LM34]])" | §2 (one paragraph: what a test on later data needs, with LM26's model choice judged by (26.8) as the example) |
| lm18.md:50, 389 | a bootstrap is no test on later data ([[LM34]] tests on later data) | §2 (the protocol), §6 (the bootstrap used for a different job: a search's null) |
| lm21.md:373 | [[LM34]] tests the best rule of a search on later data (White 2000; Romano and Wolf 2005) | §6 (White, Romano–Wolf on the same data), §2 (rules fixed in advance, judged on later data); the sentence is reworded at Stage 4 |
| lm22.md:57 | "Nothing here is out-of-sample ([[LM34]])" | §2 |
| lm22.md:144 | "a walk-forward test is [[LM34]]'s" (of the Kelly fraction) | lab part 7: TR23's trailing Kelly root walked forward [A34-17] |
| lm22.md:352 | "Testing many strategies with the bootstrap (the reality check) is [[LM34]]'s" | §6, E7, E8 |
| lm23.md:369 | "Searching many sectors, rules or windows and keeping the best is the data snooping that [[LM34]] treats" | §6, §7 |
| research-hygiene.md:7, 62 | LM34 covers look-ahead and survivorship bias, costs, walk-forward testing and PBO | §2–§7, one each |
| research-hygiene.md:35 | "[[LM34]] gives Taiwan's official rates" | §3 and its sources (TWSE Operating Rules Art. 94 and, for 00679B on TPEx, TPEx's Business Rules Art. 64, applied to ETFs by its ETF rules' Art. 15 ¶1; the Securities Transaction Tax Act Arts. 2 and 2-1; for the futures ETFs, the Ministry of Finance's ruling of 2008-08-11 under Art. 2 item 2, with TWSE's ETF rules page and 財政統計通報 No. 21 in support) |
| `make_lab04.py:642` | the month-end Kelly walk-forward ("LM34 (walk-forward tests)") | lab part 7 (on TR23, as the spine decides; Lab 4 runs it on 0050) |
| `make_lab23.py:901` | choosing among many rules is the data snooping LM34 treats | §6–§7 |
| `make_lab25.py:836` | a year-by-year table is a stability check ("LM34 tests on later data") | §2 |
| `make_lab26.py:1115` | a GARCH variant chosen in sample ("LM34 tests such choices on later data") | §2, the same paragraph as (26.8) |

The grep of `src/*.md` and `src/pages/*.md` for `[[LM34]]` finds lm04:209, 563; lm11:406; lm17:51; lm18:50, 389;
lm21:57, 373; lm22:57, 144, 352; lm23:369; lm25:54; lm26:54; research-hygiene:7, 35, 62 (17 lines); the grep of
`build/make_lab*.py` for "LM34" finds make_lab04:642, make_lab23:14 (a style note), 901, make_lab25:836,
make_lab26:1115. The spine listed every one of them; the style note at make_lab23:14 holds no promise.

**Outcomes** ("After this module you should be able to:"; the level in brackets, shared decision "Outcome levels";
decision C10; average 15.5 words, longest 18; with the case box, 20 sentences and 276 words, average 13.8):

1. [C] run a walk-forward backtest fixed in advance, and report its net wealth, growth, turnover and costs
2. [D] derive the log gap (34.1) between gross and net wealth, and compute costs at Taiwan's official rates
3. [C] detect look-ahead, and measure it by rerunning with only what each decision knew
4. [C] measure survivorship bias by fixing the universe from a dated list that includes delisted funds
5. [C] test whether the best of many rules beats a benchmark, using White's reality check
6. [C] estimate the probability of backtest overfitting by CSCV on a declared grid, and read its logits
7. [D] derive the in-sample best Sharpe ratio of $n$ skill-free strategies and its expected out-of-sample value
8. [U] choose among the reality check, Romano–Wolf, Hansen's test, PBO and deflation, and say when no rule is supported

Taught, practised, assessed (`reviews/REVIEW_PROMPT.md` item 10):

| Outcome | Taught | Practised | Assessed |
|:--|:--|:--|:--|
| 1 [C] | §2 | E1, lab 1 | KC §2, problem 9(c) |
| 2 [D] | §3 (Deep Dive) | E2, E3, lab 2 | KC §3, problems 1, 2, 7 |
| 3 [C] | §4 | E4, E5, lab 3 | KC §4, problems 8, 9 |
| 4 [C] | §5 | E6, lab 4 | KC §5, problem 10 |
| 5 [C] | §6 | E7, E8, lab 5 | KC §6, problems 5, 11 |
| 6 [C] | §7 | E9, widget, lab 6 | KC §7, problems 3, 4 |
| 7 [D] | §7 | E10 | problem 12 |
| 8 [U] | §6, §8 | §8's checklist | KC §8, problem 6 |

**Owns.** The walk-forward protocol: the information set at each decision (the month-end close is known after 13:30,
so the trade is at the next close on which every fund trades; the rolling 504-row window; the first purchase from
cash; valuation without terminal liquidation), applied to R1–R8 with the cost model and its official sources, each
fund under its own market's rules (TWSE Operating Rules Art. 94 for the TWSE funds and, for 00679B on TPEx, TPEx's
Business Rules Art. 64, applied to ETFs by its ETF rules' Art. 15 ¶1; the Securities Transaction Tax Act, Art. 2 item
2 and Art. 2-1, whose bond-ETF suspension covers 上市及上櫃 funds; for the futures ETFs, the Ministry of Finance's ruling
台財稅字第09700161260號 of 2008-08-11, with TWSE's ETF rules page and the Ministry's 財政統計通報 No. 21 in support; shared
decision "Cost model"); the rules' net wealth, net log growth, annual turnover and costs (decision A2), gross against
net, the costs' tax share, the sensitivity at twice the costs, R8's growth at borrowing spreads of 0, 2 and 5 points, R4's and R8's growth at $r_f$ of 0 and 2%;
the identity (34.1) and its Deep Dive; look-ahead shown on data (in the text: adjusted prices rebuilt backward,
(34.2), and the through case's rebalances traded at the signal's own close; in problems: a daily scale that uses the
same day's close, a full-sample Kelly root); survivorship on delisted Taiwan ETFs; White's reality check by the
stationary bootstrap on Experiment 10's 10,000 rules and on the grid, with its studentized form, (34.3); Romano–Wolf's
stepdown and Hansen's SPA *stated* as the source check read them, with the SPA p-value and the stepdown's first step
on Experiment 10 (the full stepdown in the lab); the declared PBO grid, CSCV, (34.4), its logit distribution and
performance degradation; the noise benchmark and its (21.9) derivation; the widget. Values owned: every A34 anchor
except the echoes (A34-01 from `vol5_series`, A34-11's exposures from LM31's A31-29, A34-12's first purchase and
largest rebalance from LM27's A27-23 and A27-24, A34-13 = LM27's A27-43, A34-22 recomputing LM21's Experiment 10,
A34-17's full-sample root recomputing lm22.md:125's 4.14, and A34-16's TR23 return of 7 April 2025, −9.70%, an input
of its scaled returns, cited to lm26.md:32 and not anchored again, decision A5); A34-21 is withdrawn.

**Leaves.** The cost arithmetic of a single trade → LM27 (decision A5; echoed in E2). Sharpe-ratio standard errors,
intervals and tests of the rules, the probabilistic and deflated Sharpe ratios, effective trials and haircuts → LM33
(cited; LM34 prints no rule's Sharpe ratio). VaR, expected shortfall and drawdowns of the rules → LM32. Scenario
losses → LM35. R8's exposure path → LM31 (echoed). Kelly sizing of a backtested strategy → LM45 and LM49; the
capstone's walk-forward → LM48; monitoring and re-estimation → LM50. To the lab (density, guidance): Romano–Wolf's
full stepdown and the Kelly walk-forward on TR23. Not in the book, one sentence each: slippage and market-impact
models (no sourced spread or impact figure exists for these funds, shared decision "Cost model"), cross-validation that
removes overlapping labels (the through case has none), the multiple-testing literature beyond White,
Romano–Wolf and Hansen (Harvey, Liu and Zhu's hurdle is LM21's, lm21.md:371).

**Uses before taught** (one sentence each in the text):

- §2: "Choosing how much to lever a backtested strategy is [[LM45]]'s subject; LM34 takes each rule's leverage as given."
- §3: "Margin and the instruments that carry leverage are [[LM46]]'s; R8's borrowing rate here is illustrative."
- §6: "Romano and Wolf's stepdown and Hansen's test are stated without proof; both rest on large-$T$ bootstrap theory
  beyond this book."
- §8: "A walk-forward comparison with a Kelly-type rule among the candidates is [[LM48]]'s capstone; sizing one
  backtested strategy is [[LM49]]'s, and monitoring a chosen rule is [[LM50]]'s."

**Data role.**

- **E5, the through case** (shared decision): `data/vol5_series.py`'s `frames("E5")` (`data/processed/vol5_frames.parquet`;
  FinMind `TaiwanStockPrice`, `TaiwanStockDividendResult` and `TaiwanStockSplitPrice`, registered 2026-10-24),
  estimation frame $T=2{,}362$ from 2017-01-18, $A=242.95$; wealth frame 2,368 sessions, $A_{\mathrm w}=243.57$
  [A34-01; LM27's A27-01 to A27-03]. Rules from `data/vol5_rules.py` (imported, never re-implemented): 92 month-end signals, the first on
  2019-02-27 with the window 2017-02-13 → 2019-02-27, traded 2019-03-04; the last on 2026-09-30, traded 2026-10-01;
  1,851 daily returns 2019-03-05 → 2026-10-08 (the schedule and the count echo LM28's A28-02 and A28-03); $\tau=7.5975$ years, calendar days ÷ 365.25 from the close of the
  first trade (2019-03-04, the close before the first return) to 2026-10-08 (decision C7, AUTHORING §8; LM33's
  $T/A_{\mathrm w}$ is a count of sessions, said where it appears) [A34-02]. Gross paths remove commission and tax only
  (`cost_mult=0`; cash interest and R8's borrowing kept).
- **The PBO grid (declared 2026-10-24, before any result of it was computed; the drafter had seen only the through
  case's summary, `data/processed/vol5_rules.txt`).** Rules R1–R8 exactly as `vol5_rules.py` defines them (costs,
  cash, financing, valuation end, drift). Estimation window (trailing rows of E5's estimation frame through the
  signal): 126, 252, 504; R1 and R2 use none. Rebalancing every 1, 3 or 6 month-end signals from the through case's
  first signal (2019-02-27, traded 2019-03-04): the $q$-month version trades at signals 1, 1 + q, 1 + 2q, … of the
  through case's schedule (92, 31 and 16 trades [A34-26]). Configurations: R1 and R2 at three frequencies (6), R3–R8
  at three windows and three frequencies (54): $n=60$; the through case is 8 of them (R1, R2 monthly; R3–R8 at 504
  rows, monthly). Performance series: each configuration's daily net return on the wealth frame, 2019-03-05 →
  2026-10-08. CSCV: $S=16$ blocks of equal length, the earliest rows that do not fill a block dropped; each of the
  $\binom{16}{8}=12{,}870$ [A34-35] choices of 8 blocks is an in-sample set and its complement the out-of-sample set;
  performance is the Sharpe ratio of daily returns in excess of $r_f/A_{\mathrm w}$; the in-sample best $k^*$ (ties:
  the first in grid order); its out-of-sample rank $j$ among the 60 (1 = worst); $\omega=j/61$; logit
  $\ln(\omega/(1-\omega))$; PBO the share of splits with logit ≤ 0; performance degradation, the OLS slope of $k^*$'s
  out-of-sample Sharpe ratio on its in-sample one, and the share of splits with an out-of-sample ratio below 0. Grid
  order: R1 1m, 3m, 6m; R2 1m, 3m, 6m; then R3 … R8, each by window 126, 252, 504 and frequency 1, 3, 6. The
  declaration was written to the drafter's notes before the grid was run and is reproduced here unchanged; the text
  prints it in §7 as declared. Dropping the earliest rows is the book's convention (Bailey et al.'s Algorithm 2.3 asks
  only for equal blocks; Sources), and with $n=60$ no logit is exactly 0, so "≤ 0" and "< 0" agree. The grid calls
  `signals()` with `vol5_rules.WINDOW` set for the call and restored, and checks that the 504-row signals equal the
  through case's; CLARABEL's cross-check failed once (R4, window 126, 2025-06-30), and the polished OSQP solution was
  checked against the exact solution instead (gap below 1e-15, floating-point noise) [A34-26], which meets the shared solver rule. As
  `vol5_rules` defines R4, it holds R3 at four of the grid's signals, where no window mean exceeds $r_f/A$ (window 126
  on 2022-09-30 and 2023-02-24; 252 on 2023-03-31 and 2023-04-28; none at 504) [A34-26]. The grid's median is taken as
  every quantile of the book (`inverted_cdf`, the 30th of 60, decision D).
- **TR23** (Volume III, the TAIEX total-return index): `data/processed/vol3_taiex.parquet` (FinMind
  `TaiwanStockTotalReturnIndex`, retrieved 2026-10-18), 5,849 returns 2003-01-03 → 2026-10-08 (lm20.md:57), $r_f=0$ (Volume IV).
  Uses: Experiment 10 recomputed with LM21's seed [A34-22]; the reality check on it (experiment 1, $\ell=145$: the largest of
  LM22's estimates on the 10,000 rules' squared demeaned returns, 145.44, rounds to TR23's own length, 145,
  lm22.md:427) [A34-24]; problem 8's daily
  volatility scale on daily simple returns in decimals, each scale traded at the close after the one it is set at
  (§2), 5,344 days 2005-01-12 → 2026-10-08, 21.74 years from the close of 2005-01-11, $A=245.83$ sessions a year
  [A34-16]; the lab's Kelly walk-forward, 250 calendar month-ends 2005-12-30 → 2026-09-30, each root traded at the
  next close (§2), 5,103 days, 20.76 years from the close of 2006-01-02, $A=245.76$ for these days [A34-17].
- **0050's adjusted prices** (§4): `ohlc("0050")` with `data/raw/vol5/0050_dividends.csv` (filter `^息$`, PITFALLS §3)
  and the 2025-06-18 4-for-1 split from `splits__2016-12-01__2026-10-08.csv` (the registered prices' ratio, 4.00021,
  rounded to 4), read directly; 20 distributions after 2017-01-17 [A34-14]. The adjusted series is the book's own,
  (34.2), compounding Volume I's total returns: on the split day the previous close is restated per current share,
  divided by 4, as `data/README.md` and LM27's §4 write it (no split-ratio symbol, decision B6). Its levels are exact
  for a stated build date. FinMind's
  `TaiwanStockPriceAdj` is not used (not registered; its levels change at every retrieval, PITFALLS §3), and no FinMind
  adjusted level is printed.
- **Survivorship** (§5; capability B4; registered under `data/raw/vol6/`, retrieved 2026-10-24, `data/README.md`):
  `TaiwanStockDelisting` (ids from "00", 63 rows [A34-18]), the daily prices of 00672L, 00673R, 00674R and 00677U (00635U and
  00642U come from E5's files), and `TaiwanStockPrice` snapshots of every ETF listed on TWSE or TPEx on 2017-01-17 and
  2026-10-08 (both markets: the TPEx-listed 00679B is in both). The snapshots have no `data_id`, which FinMind serves
  only above its Free plan: a Free account fetches the others with `--exclude vol6/etf_snapshot`, and then A34-18
  alone prints a note instead of its value. 69 ETFs had a row on 2017-01-17; 10 had none on 2026-10-08, each in the
  delisting list [A34-18]. The six funds of §5 are the ETFs on the 2017 list whose names name an S&P gold or oil index
  or the VIX (FinMind `TaiwanStockInfo`, retrieved 2026-10-24; the delisting file confirms 00672L's and 00677U's
  names; SOURCES records the query with its date and the six codes and names, and no extract is registered, decision
  on the third revision). The issuers' and TWSE's documents (Sources) confirm that all six are futures-trust ETFs on
  futures indices, all listed on TWSE (so TWSE's rules apply to them), and that three are daily leveraged or inverse:
  00672L +2× crude oil, 00673R −1× crude oil, 00674R −1× gold. A fund's growth factor skips untraded rows (close 0)
  and accepts a zero spread only on the first traded row after an untraded one (00674R: 11 of each); every other close
  equals the previous traded close plus the spread. Splits are restated with integer ratios (00673R 1 for 4 on
  2025-10-22, 00674R 1 for 5 on 2026-04-22; the registered prices are exact multiples), and none of the six pays
  distributions [A34-19]. A delisted fund is valued at its last traded close, kept as cash at 0: its holders' actual
  liquidation payout is not in FinMind (accepted, O9). Problem 10's means are those of X5's printed factors, 0.7233
  and 1.0540 [A34-37]; E6's 0.7234 and 1.0539 are the unrounded factors' [A34-20].
- **Conventions.** Growth $g=\ln W_{\text{end}}/\tau$ from the cash of 1 at the first trade's close (the first
  purchase's cost counts; LM27's criteria); costs = the sum over trades of cost ÷ pre-trade wealth; turnover = the
  one-way $\mathrm{TO}$ of the 91 trades after the first purchase, summed, ÷ $\tau$ [A34-06]. CSCV Sharpe ratios use
  population moments over each half's days; annualized by $\sqrt{A_{\mathrm w}}$ only for display. t-stats (21.1)
  divide by $s_{\mathrm u}$. Quantiles and medians `inverted_cdf`.
- **Guard and exact checks.** Counts against a threshold use the guard 1e-12 (t ≥ 3, bootstrap shares, logit ≤ 0). The
  identity (34.1) is checked on every rule: the largest gap is below 2e-14, floating-point noise [A34-07]. No path is
  ruined (the script asserts $1+R_p>0$ on every day of every path, and $1+fR>0$ on TR23's scaled paths).
- **Seeds and block lengths.** One generator per experiment, `default_rng([e, 20261011])`, created once: $e=1$ the
  reality check on Experiment 10 ($B=10{,}000$, $\ell=145$); $e=2$ the noise panels (200 panels of 60 strategies, each
  panel one draw `standard_normal((1851, 60))` × 1%, rows days, the panels in sequence); $e=3$ the widget's grid (40
  panels per state, each `standard_normal((1851, n))` × 1% with strategy 1 in column 0 plus its drift, the panels in
  sequence and the states in the printed order, $n$ outer); $e=4$ the grid's reality check ($B=10{,}000$, $\ell=75$,
  LM22's rule on the 59 differences from R1, decision D); $e=5$ its sensitivity at $\ell=17$ (R1 monthly's own
  estimate, rounded); $e=6$, in the lab only, the extension's reality check (Lab parts). Experiment 10 keeps LM21's
  `default_rng([10, 20261011])`. Every Monte Carlo proportion prints its standard error $\sqrt{p(1-p)/B}$; the noise
  PBO prints the SD of the 200 panel values ÷ √200.
- **Published files** (plan; Volume IV's rule X37, shared decision "Charts"). X2 stores the eight rules' wealth at the
  last session of each week (week keys by ISO year and week) plus every cited value, about 400 dated points a series,
  under 100 KB; X9 stores every fifth split (2,574 points, no dates); X6 and X8 store bin counts only; the widget stores
  30 precomputed means and a synthetic test matrix. No raw FinMind value is published; the survivorship exhibit stores
  six growth factors.
- **Scripts.** `data/lm34_numbers.py` (every printed value, asserted against `src/lm34.md`, compared with the anchors,
  rounding flags) and `data/lm34_charts.py` (X2, X3, X5–X9 and the widget block, with a Node check of the widget's
  CSCV against Python's, as `data/lm15_charts.py` does); both after `data/vol3_series.py`, `data/vol5_series.py` and
  `data/vol5_rules.py` have written `data/processed/`.

**Hygiene declaration.** *Out-of-sample:* the eight rules' results (windows, dates, timing, costs and criteria fixed
in advance on 2026-10-24, before any result was computed); the daily scale (problem 8) and
the Kelly walk-forward (lab), each traded at the close after its signal (§2) and a *hypothetical* rule judged on data
after its estimate. *In-sample:* the
60-configuration grid, by design, declared after the through case's results were seen, the grid's reality check
against R1, and the lab's 68-configuration extension, declared after the grid's results were seen; the reality check
on Experiment 10 is a *model* result on TR23's returns, as LM21 labels the experiment (lm21.md:364).
*Model:* Experiment 10, the noise panels, the widget's grid and simulator. *Descriptive:* fund histories, the ETF
lists, adjusted prices, the survivorship gap. Look-ahead versions (rebalances at the signal's own close, the daily
scale traded at its own close or computed with the same day's return, the full-sample Kelly root) are labelled *look-ahead, not achievable*. Count of versions on the same data: the
8 rules ($n=8$, [[LM33]]'s count), 52 more grid configurations ($n=60$ in all), LM21's 10,000 random rules
(recomputed), and the variants labelled where they appear (gross, twice the costs, three borrowing spreads, two other risk-free rates, the
signal's own close; three daily scales; in the lab, four Kelly versions and the extension's 8 more configurations,
$n=68$). Local note: "The eight rules' results are
**out-of-sample**: their windows, dates, costs and criteria were fixed on 24 October 2026, before any result existed.
The 60-configuration grid is **in-sample** by design and was declared after those results were seen. Experiment 10,
the noise panels and the widget are **model** results. Fund histories and adjusted prices are **descriptive**. This
module compares 60 configurations, the 8 rules among them, and [[LM21]]'s 10,000 random rules on the same data, and
corrects both searches."

**Notation.** AUTHORING §6 with the "Portfolios, risk and backtests" table. Used: $R$, $r$, $T$, $t$, $A$,
$A_{\mathrm w}$, $N=5$ (E5's funds), $i$ (a fund), $W$, $W^{\mathrm{pre}}_t$ (§6, decision B2), $\mathbf w$, $\mathbf f$,
$\mathbf w^{\mathrm{drift}}_t$, $\mathrm{TO}_t$, $\text{tax}_i$, $\lVert\mathbf x\rVert_1$, $L_t$ (R8's), $r_f$,
$\mathrm{SR}$, $\widehat{\mathrm{SR}}$, $g$, $G$, $\tau$ (a span in years, since $T$ is a count), $P$, $D$ (no
split-ratio symbol: the split day's restated close is said in words, decision B6), $f$, $\hat f^*$ (lab),
$\bar\sigma_t$, $\sigma_{t+1\mid t}$ (no hat, as LM26 prints it; decision B1), $\lambda=0.94$ (only LM26's decay,
problem 8), $\bar R$, $s_{\mathrm u}$, $\text{t-stat}$, $\Phi$, $\Phi^{-1}$, $B$, $\ell$ (a mean block length,
§6's scoped row), $n$ (strategies tried; LM21's $m$ tests read as $n$ trials, shared notation decision), PBO. Local
symbols, declared in the notation note (accepted, decision B5):

| Symbol | Meaning | Check |
|:--|:--|:--|
| $W^{\text{net}}_t$, $W^{\text{gross}}_t$ | a rule's wealth with and without commission and tax (financing kept), from the cash of 1 at the first trade | superscripted §6 $W$; §6's $W^{\mathrm{pre}}_t$ cited |
| $\operatorname{cost}$ | LM27's cost of a trade, (27.2); in (34.1) each term is one trade's cost ÷ its pre-trade wealth | an operator, not a scalar symbol (§6: no scalar cost symbol) |
| $G_{t,t'}$ | total-return growth factor from the close of $t$ to that of $t'$, $(1+R_{t+1})\cdots(1+R_{t'})$ with Volume I's total returns (34.2) | §6's $G$ with two dates; written out, with no index letter ($j$ is the rank below; decision B6) |
| $P^{\mathrm{adj}}_{t\mid t'}$ | adjusted close of day $t$ in a series built on day $t'$, (34.2) | new; upright superscript; LM35 uses it (B6) |
| $k$, $n$ | a strategy (rule, configuration) and the number tried | §6's $n$ (Volume VI); LM34 writes no lag and no count of SDs, so $k$ is free |
| $\bar R_k$, $\bar R_{k,\text{boot}}$ | strategy $k$'s mean daily return (in excess of the benchmark's); its value on a resample | subscripted $\bar R$; "boot" as LM22's $\hat\theta_{\text{boot}}$, no star |
| $S$ | the number of CSCV blocks, 16 | Bailey et al.'s letter; LM34 has no SVD and no TAIEX close $S_t$ |
| $q$ | rebalancing every $q$ month-end signals (1, 3, 6; the lab's 12) | free: LM34 has no bet, no dividend yield and no false-discovery level |
| $k^*$ | the in-sample best strategy of a split | star for an optimum (§6) |
| $j$, $\omega$ | $k^*$'s out-of-sample rank among the $n$ (1 = worst: $k^*$ is the $j$th smallest) and its relative rank $j/(n+1)$ | §6's $j$; $\omega$ displaces the sample-space outcome, which LM34 does not use |
| logit | $\ln(\omega/(1-\omega))$, written as a word | not $\lambda$ (LM26's decay appears in problem 8) |

Not used: $c$ (no Kelly fraction, and no scalar cost), $\lambda$ for the logit, a letter for White's statistic (written
$\max_k\sqrt T\,\bar R_k$; $V$ and "RC" are taken: $\mathrm{RC}_i$ is a risk contribution), $m$ for a block's length
(written $\lfloor T/S\rfloor$), $P$ for a probability, a star for a bootstrap draw, a hat on the EWMA forecast.

**Motivating case: "The grid's winner"** (box, three paragraphs of at most 80 words, decision C10; 12 sentences,
average 12.7 words, longest 27)

> From March 2019 to October 2026, the through case's eight rules grew between 8.70% (R3) and 14.49% (R2) a year after
> Taiwan's commission and tax [A34-04]. Now vary each rule's estimation window (126, 252 or 504 sessions; R1 and R2
> use none) and how often it trades (every one, three or six month-ends). That gives 60 configurations [A34-26]. The
> best, maximum Sharpe on a 252-session window traded every six month-ends, grew 18.62% a year [A34-27].
>
> The median configuration grew 10.96%, and maximum Sharpe as fixed in advance (R4) grew 10.51% [A34-04]. Would
> you trade the winner?
> Three questions come first. Did the test use only what was known at each decision? Did its universe include the
> funds that later vanished?
>
> Of the six gold, oil and VIX futures funds trading in January 2017, two were delisted. The six together lost 27.7%,
> while the four survivors gained 5.4% [A34-20]. And how much of 18.62% is the search itself?

Resolved: (a) timing: §2's protocol and §4 (on the monthly rules, moving each rebalance to the signal's own close
changes growth by −0.41 to +0.89 points a year, and seven of the eight rules gain [A34-36]; on a daily rule scaled on
TR23, the TAIEX total-return index, a scale that also uses the day's own return turns 15.08% into 16.70% [A34-16]); (b) the universe: §5, E6, and
E5's own funds are among the survivors; (c) the search: §6–§7. No configuration's mean return beats R1's beyond chance
(the largest t-stat, 1.30, has a reality-check p-value of 0.375 [A34-32]), and the in-sample best ranks in the lower
half out of sample in 0.663 of the splits [A34-29]. The winner is the highest bump of lm04.md:209.

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | a backtest as an experiment with hidden choices; the layer LM34 adds (LM27–LM31 built the rules, LM33 measured their Sharpe ratios; LM34 tests the procedure that produced them); case + X1; roadmap; notation and hygiene notes | 450 |
| 2 | The Walk-Forward Protocol {1} | the information set at a decision; signal at a month-end close, known after 13:30 on both markets (TWSE's Art. 3; for 00679B, TPEx's Art. 40), trade at the next close on which every fund trades (Research hygiene); rolling against expanding windows (one sentence; the through case rolls 504 rows); first purchase from cash; valuation without liquidation (its cost is not charged, said once); what "fixed in advance" fixes; a test on later data of a model choice, LM26's GARCH variants judged by (26.8), one paragraph; E1; X2; [[LM33]] tests the differences; pitfall: re-running a "fixed" test after a change is a second trial; 導讀; KC | 520 |
| 3 | Costs at Taiwan's Official Rates {2} | the rates and their sources, each fund under its own market's rules (TWSE's Art. 94 for the TWSE funds beside TPEx's Art. 64, applied to ETFs by its ETF rules' Art. 15 ¶1, for 00679B: on both markets 0.1425% is the level above which a broker must give notice, not a cap; tax 0.1% on ETF sales under Art. 2 item 2, whose 1‰ covers "other securities approved by the government": the Act names no ETF, and TWSE's ETF rules page and the Ministry's notice give ETF sales that rate; bond ETFs exempt to 2026-12-31 by Art. 2-1, which suspends the tax on 上市及上櫃 (listed and OTC-listed) bond ETFs, so 00679B on TPEx throughout; the futures ETFs at 0.1% by the Ministry's ruling of 2008-08-11, which taxes a transfer of futures-trust fund certificates at 1‰ under Art. 2 item 2); (27.2) and LM27's cost arithmetic cited (the first purchase, A27-23; a switch of NT\$1 million, A27-43); E2; (34.1) with its Deep Dive; X3; the tax share; E3: twice the costs (why no slippage model: no sourced figure), R8's borrowing spreads; pitfall: one constant subtracted at the end (Research hygiene); 導讀; KC | 600 |
| 4 | Look-Ahead Bias {3} | definition: a rule may use only what was known when it acted; (34.2), adjusted levels change with the build date; E4, X4: returns from adjusted prices are total returns, levels are not; E5: the rebalances traded at the signal's own close over the same span, small for monthly rules but a gain for seven of eight; the daily scale (problem 8) and the full-sample Kelly root (problem 9) named; pitfall: a statistic fitted to all data inside a rule; KC | 500 |
| 5 | Survivorship Bias {4} | a list of today's funds leaves out the vanished; TaiwanStockDelisting; X5; E6; E5's own universe: 00635U and 00642U were chosen in 2026 from survivors, and the leveraged oil fund 00672L was delisted in 2020 (LM27's §4 points here); what the six are: futures-trust ETFs on futures indices, all listed on TWSE, three of them daily leveraged or inverse (00672L +2×, 00673R and 00674R −1×), whose multiple holds for one day only, so under daily compounding their long-run returns depart from the multiple (TWSE's overview page, §四) and the gap mixes product types, said once; a roll in 正價差 (contango) "may" lose (可能, TWSE's word), one sentence; data policy: fix the universe from a dated list of the funds listed on TWSE or TPEx (Research hygiene's "Fix the universe"); the last close as a valuation (O9); funds that disappear tend to have done poorly (Elton, Gruber and Blake 1996, abstract); 導讀 (前視偏誤, 存活者偏誤, 下市, 正價差); KC | 450 |
| 6 | Correcting a Search on the Same Data {5,8} | recap of [[LM21]]'s Experiment 10, (21.6) and (21.9) (no re-teaching); White's null (the best has no superiority over the benchmark) and statistic; recentred stationary resamples (LM22's (22.3)), (34.3), *stated without proof* (White 2000, Corollary 2.4); E7; X6; studentized form (Romano and Wolf 2005, §4.1; Hansen 2005); what large $T$ means here: White's theory holds for a fixed number of rules as $T$ grows, so Experiment 10's 10,000 rules on 5,849 days lie outside it, and the grid's 59 differences on 1,851 days are closer to it; Romano–Wolf's stepdown and Hansen's SPA stated (one paragraph each, from the originals; E7 prints the SPA p-value and the stepdown's first step, and says where the code departs from the papers); E8: correlated rules, where the bootstrap's threshold 2.42 sits far below Bonferroni's 3.14 [A34-32]; the block-length rule and its sensitivity; pitfall: the reality check asks whether the best beats the benchmark, not which rules do; 導讀 (資料偵伺, 族系誤差率, 平穩自助重抽法); KC | 700 |
| 7 | The Probability of Backtest Overfitting {6,7} | the declared grid as declared; X7: the highest bump; CSCV definition box; (34.4); why $\binom{16}{8}=12{,}870$ (the paper prints 12,780) and which logits are possible; E9; X8; performance degradation, X9; what PBO measures (selection within a grid, not profit: its out-of-sample Sharpe ratio is below 0 in only 0.99% of splits [A34-29]); E10, the noise benchmark and (21.9)'s derivation; PBO's own noise (0.12 to 0.87 across noise panels [A34-33]); the widget; pitfall: adding configurations after a result is another search; 導讀 (過度配適, 交叉確認, 對數勝算, 秩 glossed once as 名次); KC | 780 |
| 8 | Reading a Backtest {8} | the case resolved; a checklist (timing, universe, costs inside, the count of versions, reality check or PBO, [[LM33]]'s deflation); which tool answers which question; "the data do not support the rule" as a valid conclusion (guidance); the lab's Kelly walk-forward in one sentence; KC | 300 |
| 9 | Backtesting in Python {1,5,6} | `vol5_rules`' `wealth_path` with `cost_mult`; LM22's `stationary_idx` against arch's `StationaryBootstrap`; CSCV in NumPy: block sums, `itertools.combinations(range(16), 8)` and one mask product; lab box | 180 |
| — | Summary (8) / Problems (12) / Solutions | | 120 / 420 / 450 |
| | **Total** | | **5,470** |

**Elements.** 10 examples (E1 §2; E2, E3 §3; E4, E5 §4; E6 §5; E7, E8 §6; E9, E10 §7). Knowledge checks:

- §2: why does the first trade fall on 4 March 2019 and not on the signal day, 27 February? The signal uses that day's
  close, known only after 13:30, so the earliest trade is the next session's close on which every fund trades
  [A34-02]. R2 ends with wealth 3.0079 after $\tau=7.5975$ years; what is its growth? It is $\ln3.0079/7.5975=14.49\%$
  [A34-03, A34-04].
- §3: R4's costs summed over 92 trades are 4.22% of wealth, and its gross growth exceeds the net by 0.56 points a year
  (rounded from the unrounded rates; X3's 11.06% and 10.51% are rounded separately); why do $0.0422/7.5975$ and 0.56
  points agree? By (34.1) the log gap is $-\sum\ln(1-\text{cost}/W^{\mathrm{pre}})$: 0.0422296 against the sum
  0.0422153, so the two differ only in the fifth decimal [A34-05, A34-07].
- §4: a screen buys 0050 when its trailing dividend yield exceeds 10%. On a series adjusted on 8 October 2026, 0050's
  2017 distributions yield 15.44% of the year-end close; on the actual close, 2.92% [A34-15]. Which number could the
  screen have seen in 2017, and why?
- §5: E5 holds 00642U, an oil futures ETF. Which oil fund trading on 17 January 2017 did not survive, and what was
  its last traded close worth per unit of its close that day? 00672L, last traded on 12 November 2020 and delisted the
  next day, $G=0.038$ [A34-19].
- §6: on Experiment 10 (TR23, the TAIEX total-return index), White's p-value 0.283 and (21.9)'s 0.298 nearly agree
  [A34-23, A34-24]; on the grid the
  bootstrap's 95% point for the largest t-stat is 2.42 against Bonferroni's 3.14 [A34-32]. Why the difference? The
  random rules' positions are independent coins, so their returns are uncorrelated and their t-stats nearly
  independent, as (21.9) assumes; the grid's differences from R1 correlate with median 0.78.
- §7: with $n=60$, which logits can occur, and why is none exactly 0? $\ln(j/(61-j))$ for $j=1,\dots,60$: from
  −4.094 to 4.094, and $\omega=j/61$ is never $\tfrac12$ (at $j=30$ and 31 the logit is ∓0.0328) [A34-35].
- §8: the grid's PBO is 0.663 while the in-sample best's out-of-sample Sharpe ratio is below 0 in only 0.99% of the
  splits [A34-29]. What does each number say about the search, and what about the rules?
- §9: how many rows does `combinations(range(16), 8)` yield, and why does the code multiply a 12,870 × 16 mask by the
  16 block sums instead of summing each split's days? 12,870; each split's sums are a fixed combination of the block
  sums, so one product gives them all [A34-35].

中文導讀 in §2 (回測 (backtest), 滾動前進測試 (walk-forward test), 樣本外 (out of sample)), §3 (交易成本 (transaction
cost), 手續費 (commission), 證券交易稅 (securities transaction tax), 週轉率 (turnover)), §5 (前視偏誤 (look-ahead
bias), 存活者偏誤 (survivorship bias), 下市 (delisting), 正價差 (contango, TWSE's word)), §6 (資料偵伺 (data
snooping), 族系誤差率 (familywise error rate), 平穩自助重抽法 (stationary bootstrap)), §7 (過度配適 (overfitting),
交叉確認 (cross-validation), 對數勝算 (logit), 秩 (rank), glossed once as 名次, a configuration's place in the
ordering, since the book's other 秩 is a matrix's rank; decision on the Chinese terms). Deep Dives: §3 "The log gap
between gross and net wealth": with scale-free costs and the same targets, the two paths hold the same exposures
after every trade and earn the same percentage returns between trades (cash interest and borrowing included), so
wealth differs only by the factors $1-\text{cost}/W^{\mathrm{pre}}$ at the trades; hence (34.1), and the bound by
$\ln(1-x)\le-x$. §6 "Why the resamples are recentred": the null that no strategy beats the benchmark is tested at its
least favourable point, every mean difference 0, so each resampled mean is measured from its own sample mean; the
resampled maximum of recentred means is White's (2000) Corollary 2.4, and its validity for large $T$ is *stated
without proof*. §7 "Counting the splits": $\binom{16}{8}$ by symmetry and
Pascal's rule, and why the halves are complementary, so that for means the out-of-sample sum is the full-sample sum
minus the in-sample one.

**Exhibits.**

- X1 `case` (table, §1): the grid's winner against the through case. Rows: R4 as fixed in advance (504 rows,
  monthly) 10.51% a year, rank 39 of 60; the grid's best (R4, 252, every 6 month-ends) 18.62%; second (R4, 126, 6
  month-ends) 17.38%; median (R3, 126, 6 month-ends) 10.96%; worst (R7, 126, monthly) 7.60% [A34-27]; R2 as fixed
  14.49%, rank 8 [A34-04, A34-27]; PBO 0.663 [A34-29]; reality-check p-value of the best t-stat against R1, 0.375
  [A34-32]; the six futures ETFs held from 17 January 2017: all −27.7%, survivors +5.4% [A34-20]. Note: E5's wealth
  frame, net of commission and tax, 5 March 2019 to 8 October 2026; the grid is in-sample by design. The reality
  check is studentized ($B=10{,}000$, `default_rng([4, 20261011])`, MC SE 0.0048). Survivorship rows: the six funds
  from their closes of 17 January 2017 to their last traded close on or before 8 October 2026, descriptive. Source: FinMind `TaiwanStockPrice`, `TaiwanStockDividendResult`, `TaiwanStockSplitPrice` (E5,
  registered 2026-10-24) and `TaiwanStockDelisting` (registered 2026-10-24); Computations: `data/lm34_numbers.py`.
- X2 `wealth` (line, date axis with shared `x.values`, §2): net wealth of the eight rules from the cash of 1 at 4
  March 2019 to 8 October 2026, weekly points plus every cited value (X37); R1 (colour 1), R2 (2), R4 (3), R8 (4)
  named, R3, R5, R6 and R7 as `quiet` lines named in the caption, their final values as labelled `ann` points. Values cited (labels; E1 prints four decimals):
  final wealth 2.662, 3.008, 1.937, 2.221, 2.040, 2.272, 2.183, 2.412 [A34-03]. Note: out-of-sample, fixed in advance;
  no terminal liquidation.
- X3 `grossnet` (bar, `stack: true`, approved C1, §3; decision E): categories R1–R8; series "net growth" (colour 1)
  and "commission and tax" (colour 2, gross minus net), so each bar's total is the gross growth and its label shows
  it; `fmt: "pct2"`. Values cited: net 12.89%, 14.49%, 8.70%, 10.51%, 9.38%, 10.80%, 10.28%, 11.59% [A34-04]; gross
  12.99%, 14.58%, 8.85%, 11.06%, 9.52%, 10.91%, 10.44%, 11.99% [A34-05]. Note: gross keeps cash interest and R8's
  borrowing; the tax share of the costs is 17% to 22% [A34-09]; each segment and each total is rounded separately
  from the unrounded values, so the two printed parts can miss the printed total by 0.01.
- X4 `adjusted` (table, §4): 0050's close of 17 January 2017 and the same day in adjusted series built on three later
  dates: 72.30; 65.12 (built 2 January 2020), 55.20 (31 December 2024), 13.25 (8 October 2026) [A34-14]; the 2017
  distributions NT\$1.70 and NT\$0.70 over the previous close, 2.32% and 0.85%, and over the adjusted close of a series
  built on 8 October 2026, 12.65% and 4.54%; the year's two distributions over the year-end close, 2.92% against
  15.44% [A34-15]. Note: descriptive; the book's adjustment (34.2) with the registered distributions and the 4-for-1
  split of 18 June 2025; FinMind's `TaiwanStockPriceAdj` is rebuilt at every retrieval (PITFALLS §3).
- X5 `survivors` (bar, §5): categories the six futures ETFs with a row on 17 January 2017; series "survivors"
  (colour 1) and "delisted" (colour 2), each null for the other's funds; `hline`s at the all-six mean 0.723 and the
  survivors' 1.054 [A34-20]. Values cited: 00635U 2.198, 00642U 1.593, 00672L 0.038 (delisted 13 November 2020),
  00673R 0.140, 00674R 0.285, 00677U 0.086 (delisted 3 June 2021) [A34-19]. Note: growth factor from the close of 17
  January 2017 to the last traded close on or before 8 October 2026; a delisted fund's last close is kept as cash;
  descriptive.
- X6 `rc` (line, `step` histogram, §6): Experiment 1's 10,000 resampled maxima of the studentized statistic, bins of
  0.1, scaled to a density (count ÷ (B × 0.1)); a second series, (21.9)'s density of the largest of 10,000 independent standard normals; dashed `vline`s at the
  observed 3.97 [A34-22], the bootstrap 95% point 4.77 [A34-25] and (21.9)'s 4.41 [A34-23]. Note: model on the returns
  of TR23 (the TAIEX total-return index); $B=10{,}000$, `default_rng([1, 20261011])`, mean block 145 (LM22's rule);
  p-values 0.283 (White) and 0.281 (studentized), MC SE 0.0045 [A34-24, A34-25].
- X7 `bumps` (scatter, §7): the 60 configurations' net growth; x the rule (ticks at R1…R8 with `tickLabels`, windows
  offset within a rule), series by frequency "monthly", "3 month-ends", "6 month-ends" (colours 1–3); the through
  case's eight as marked `points`; a dashed `lines` entry (`dash: true`, `extend: true`) at the median 10.96%, labelled "median 10.96%" (scatter charts take no `ann`). Values cited: best 18.62%, second 17.38%, worst
  7.60% [A34-27]; R4's configurations from 10.51% to 18.62%, R1's from 12.85% to 12.96% [A34-28]. Note: in-sample by
  design; declared 24 October 2026 before it was computed.
- X8 `logits` (bar, §7): the 12,870 splits' logits in 18 bins of 0.5 from −4.5 to 4.5 (ends clipped) [A34-31], series
  "the grid" (colour 1) and "noise, mean of 200 panels" (colour 2, scaled to 12,870 splits; chart data only).
  Values cited: PBO 0.663, median −0.72 [A34-29]; extremes −4.09 and 3.38 [A34-31]. Note: CSCV with 16 blocks of 115
  days, 11 earliest days dropped.
- X9 `degrade` (scatter, §7): $k^*$'s in-sample against out-of-sample Sharpe ratio, annualized by
  $\sqrt{A_{\mathrm w}}$, every fifth split (2,574 points); the OLS line as a dashed `curve` labelled "slope −0.86";
  the means 1.31 and 0.80 as a marked point [A34-29]. Note: annualization for display only; the regression uses all
  12,870 splits.

**Widget `pboSim` — "How often does the best backtest disappoint?"** `Book.controls`: number of strategies $n$
(select: 2, 5, 10, 20, 60, 100), the true annual Sharpe ratio of strategy 1 (select: 0, 0.5, 1, 1.5, 2; the others
0), and a "new draw" button (seed + 1). The browser draws $1{,}851\times n$ normal returns with `Book.rng(seed)` (daily
SD 1%, strategy 1's drift $\mathrm{SR}/\sqrt{A_{\mathrm w}}\times1\%$), runs CSCV with $S=16$ (module-local code under 30
lines: block sums, the 12,870 masks of 8 of 16 bits, ranks, logits) and shows the logit histogram (X8's bins) with
the panel's PBO; a readout gives the mean PBO of 40 panels for the chosen state, precomputed by experiment 3 [A34-34]
(for example $n=60$: 0.51 at a true ratio of 0, 0.05 at 2), and one sentence explains the 0.65 at $n=5$: "For odd
$n$ the middle rank has a logit of exactly 0, which PBO counts, so with no skill PBO is $(n+1)/(2n)$: 0.6 at $n=5$." Initial state (PDF): $n=60$, ratio 0, seed 1. Data
block `chart-lm34-pboSim`: the 30 means, their largest SE 0.051 [A34-34], and a synthetic 160 × 5 test matrix (seeded
normal draws, no market data) with its Python logits, against which `data/lm34_charts.py` checks the widget's CSCV in
Node. Cost: $1{,}851\times100$ draws and $12{,}870\times100$ comparisons at most, well within the PDF printer's wait.
*Model*; the simulator's draws are not NumPy's, so a panel's value differs from experiment 3's panels; the readout
prints experiment 3's 40-panel mean for the chosen state.

**Examples** (results recomputed from the printed inputs):

- E1 §2 `netresults`, the through case net of costs: final wealth R2 3.0079, R1 2.6620, R8 2.4119, R6 2.2722, R4
  2.2214, R7 2.1829, R5 2.0400, R3 1.9367 [A34-03]; growth $\ln W/\tau$ 14.49%, 12.89%, 11.59%, 10.80%, 10.51%,
  10.28%, 9.38%, 8.70% a year over $\tau=7.5975$ years (calendar days ÷ 365.25 from the close of 4 March 2019)
  [A34-02, A34-04]; turnover from 0.18 a year (R2) to 1.45 (R4) [A34-06];
  ranking R2 > R1 > R8 > R6 > R4 > R7 > R5 > R3 [A34-08]. The two rules without estimates lead; whether any difference
  beats chance is [[LM33]]'s test.
- E2 §3 `costs`: LM27's cost arithmetic first (decision A5): the first purchase costs $0.001425/1.001425=0.1423\%$ of
  wealth for R1–R7 (LM27's A27-23), and R8's is smaller because its first exposure is below 1 [A34-12]; switching
  NT\$1,000,000 from 0050 into 00679B costs NT\$3,850, and back NT\$2,850 (LM27's A27-43) [A34-13]. LM34's totals:
  R1's 91 later rebalances turn over 1.96% of wealth on average (the largest 8.06%, LM27's A27-24) and cost 0.0073%
  of wealth each on average [A34-12]; summed over 92 trades the costs are 0.81% of wealth for R1 and 4.22% for R4, and (34.1) gives R1's
  log gap 0.0080768 against the sum 0.0080755 [A34-07]; the tax is 17% to 22% of the costs [A34-09].
- E3 §3 `twice`: at twice the costs R4 falls 0.56 points to 9.95% and drops below R7; R1 loses 0.11 points (12.78%);
  the order becomes R2 > R1 > R8 > R6 > R7 > R4 > R5 > R3 [A34-10]. R8's growth at borrowing spreads of 0, 2 and 5
  points: 11.99%, 11.59%, 10.99% [A34-11]; at a spread of 0 R8 still pays commission and tax, so this 11.99% is not
  its gross growth, which also rounds to 11.99% [A34-05]. R8 borrows at 62 of its 92 trades (LM31's A31-29, echoed in
  A34-11). Cash earns $r_f=1.5\%$, LM7's illustrative rate, which R4's signal also uses. At 0% or 2%, the spread
  kept, R4 grows 10.88% or 10.31% and R8 11.79% or 11.52%; no other rule moves, and at 0% R4 passes R6 [A34-38].
- E4 §4 `builddate`: 0050 closed at 72.30 on 17 January 2017. In an adjusted series built on 2 January 2020 that day
  shows 65.12; built on 31 December 2024, 55.20; built on 8 October 2026, after 20 distributions and the 4-for-1 split,
  13.25 [A34-14]. Its February 2017 distribution of NT\$1.70 yielded 2.32% of the previous close but reads as 12.65%
  on today's adjusted series [A34-15]. Total returns from the closes and distributions equal the returns of every adjusted series, whatever
  its build date; only the levels moved.
- E5 §4 `sameclose`: move each of the 91 later trades to its signal day's own close (impossible: the close is known
  only after 13:30), and keep the first purchase on 4 March 2019, so that both paths start from the same cash and
  cover the same 7.5975 years (calendar days ÷ 365.25 from the close of 4 March 2019). Growth: R1 13.14%, R2 14.59%,
  R4 10.09%, R8 12.48%; the changes from the through case, from unrounded values, run from −0.41 points (R4) to +0.89
  (R8), and seven of the eight rules gain [A34-36]. For monthly rules the one-day shift is small; problem 8 shows a
  daily rule where a worse mistake, a scale that uses the day's own return, is large.
- E6 §5 `survgap`: of the 69 ETFs listed on TWSE or TPEx with a row on 17 January 2017, 10 had none on 8 October
  2026, and each is in the delisting list [A34-18]. The six gold, oil and VIX futures ETFs of January 2017: equal
  amounts held to 8 October 2026 grew to 0.7234 (−27.7%, −3.33% a year); the four survivors to 1.0539 (+5.4%, +0.54% a
  year); the gap is 3.87 points a year over 9.7221 years (calendar days ÷ 365.25 from the close of 17 January 2017)
  [A34-20]. These means come from the unrounded factors; X5's printed factors average 0.7233 and 1.0540 (problem 10)
  [A34-37]. E5's 00635U and 00642U are two of the survivors. Three of the six are daily leveraged or inverse, so the
  gap mixes product types.
- E7 §6 `rc10`, Experiment 10 on TR23 (the total-return index) corrected: the best t-stat 3.9738 (LM21 prints
  3.97) [A34-22]; its one-sided p-value $3.54\times10^{-5}$, Bonferroni's $10{,}000\times3.54\times10^{-5}=0.354$,
  (21.9)'s $1-(1-3.54\times10^{-5})^{10{,}000}=0.298$ [A34-23]; White's reality check (stationary
  bootstrap, $\ell=145$ by LM22's rule, $B=10{,}000$, `default_rng([1, 20261011])`) 0.283, studentized 0.281, both
  with MC SE 0.0045; the bootstrap's 95% point for the largest t-stat is 4.77, and no rule's t-stat reaches it, so
  Romano and Wolf's first step rejects nothing [A34-24, A34-25]. That step divides by each rule's sample $s_{\mathrm u}$
  inside the resamples (their footnote 22's variant) and centres at the sample means (their Remark 3.4). Hansen's
  consistent SPA recentres the 9,814 rules with t ≥ $-\sqrt{2\ln\ln T}=-2.079$ and gives 0.277 (MC SE 0.0045); the code
  uses each rule's iid $s_{\mathrm u}$ where Hansen recommends a kernel estimate, and its count "at or above" gives the
  same 0.277 as his strict count [A34-25]. The best of 10,000 random rules is what chance gives.
- E8 §6 `rcgrid`, the grid against R1 monthly: the largest t-stat of the 59 mean differences is 1.296 (R4, 126, every
  6 month-ends), one-sided p-value 0.0975, Bonferroni's $59\times0.0975>1$, so 1; the studentized reality check with
  $\ell=75$ (LM22's rule on the 59 differences from R1: R4 126 monthly's gives 74.63) has p-value 0.375 (MC SE
  0.0048), and at $\ell=17$ (R1 monthly's own estimate, rounded) 0.421 (MC SE 0.0049); the bootstrap's 95% point is
  2.42 against Bonferroni's 3.14, because the differences correlate with median 0.78 [A34-32].
- E9 §7 `pbo`, CSCV on the declared grid: 16 blocks of 115 days (11 earliest days dropped), 12,870 splits; PBO 0.663;
  logits' median −0.72; $k^*$'s out-of-sample Sharpe ratio is below 0 in 0.99% of the splits; its mean annualized
  ratio falls from 1.31 in sample to 0.80 out of sample; the slope of out-of-sample on in-sample is −0.86 [A34-29].
  The in-sample best is most often R2 monthly (19.1% of splits), R4 252 6m (18.8%) and R4 126 6m (13.8%), 31
  configurations in all [A34-30].
- E10 §7 `noise` (*Model*): 200 panels of 60 independent strategies with zero mean over the same 1,851 days
  (`default_rng([2, 20261011])`, each panel one draw `standard_normal((1851, 60))` × 1%, rows days, the panels in
  sequence): PBO 0.50 (SE 0.012), from 0.12 to 0.87 across panels; $k^*$'s annualized Sharpe
  ratio averages 1.20 (SE 0.007) in sample and 0.00 (SE 0.016) out of sample; (21.9) with a per-day standard error
  $1/\sqrt{920}$ ((20.9) at SR 0) gives the in-sample best a median of 1.17 and a mean of 1.19 [A34-33]. PBO near one half is what no skill gives; one panel's
  PBO can sit anywhere from 0.12 to 0.87.

**Problems plan** (12; MC keys B, A, C, B, A, C; the lab solves problems 8 to 12). Stems state the sample (E5's wealth
frame, 5 March 2019 → 8 October 2026, net of commission 0.1425% each side and tax 0.1% on sales, 0 for 00679B; or
TR23, the TAIEX total-return index, 2003–2026, $r_f=0$), the window, the rebalancing dates and the label (shared
decision "Problems"), the seed and draws, and the rounding.

1. MC: which sale of an E5 fund on 1 October 2026 pays no securities transaction tax? A 00635U (a futures ETF, taxed
   at 0.1% like other ETFs). **B** 00679B (a bond ETF of a securities investment trust, listed on TPEx, exempt to
   2026-12-31 by Art. 2-1, which covers 上市及上櫃 bond ETFs). C 00646 (holding foreign stocks exempts no fund from Art.
   2's 0.1%).
2. MC: R1's costs over its 92 trades sum to 0.0080755 of pre-trade wealth [A34-07]; which is true of
   $\ln(W^{\text{gross}}/W^{\text{net}})$? **A** it is slightly larger, 0.0080768, because $-\ln(1-x)>x$. B it equals
   the sum, because the costs are scale-free. C it is smaller, because later trades are made on a smaller net book.
3. MC: CSCV with 16 blocks; the number of splits. A 12,780 (the figure the paper prints; shared decision
   "References"). B 65,536 (every subset of the blocks). **C** 12,870 [A34-35].
4. MC: $n=60$ configurations; the in-sample best ranks 31st of 60 out of sample (1 = worst); its logit. A −0.0328
   (counts the rank from the best). **B** 0.0328. C 4.094 (uses its in-sample rank, 60) [A34-35].
5. MC: the best of 10,000 independent null t-stats is 3.9738 (Experiment 10 on TR23, the TAIEX total-return index);
   (21.9)'s probability that the maximum reaches it. **A** 0.298. B $3.54\times10^{-5}$ (one test's p-value). C 0.354
   (Bonferroni's bound) [A34-22, A34-23].
6. MC: a grid's PBO is 0.663, and its in-sample best earns a negative out-of-sample Sharpe ratio in 0.99% of the
   splits. The best reading: A every configuration is overfit and loses money out of sample. B the reality check must
   reject. **C** the in-sample best is no better than the median member out of sample in two splits of three, while the
   members' common positive return is not the search's doing [A34-29].
7. Derive (34.1) for scale-free costs and the same targets, and show $\sum\text{cost}/W^{\mathrm{pre}}\le\ln(W^{\text{gross}}
   /W^{\text{net}})$; check on R4 (0.0422153 against 0.0422296) [A34-07].
8. Look-ahead in a daily rule (TR23, the TAIEX total-return index, $r_f=0$, cash and borrowing at 0; daily simple
   returns $R_t$ in decimals, in (26.2) as R8 uses it; 5,344 days from 12 January 2005 to 8 October 2026, 21.74 years
   in calendar days ÷ 365.25 from the close of 11 January 2005, volatility $s\sqrt A$ with $A=245.83$ sessions a year):
   the scale $\min(1.5,\bar\sigma_t/\sigma_{t+1\mid t})$, with $\bar\sigma_t^2$ the uncentred mean square of the 504
   returns through $t$ and $\sigma^2_{t+1\mid t}$ from (26.2) with $\lambda=0.94$, run through the same 504 returns from
   $\bar\sigma_t^2$ (R8's convention). Set at a close and traded at the next close (§2's protocol), it grows 15.08% a year
   (volatility 18.27%, worst day −7.50%). Computed with the same day's return, it grows 16.70% (17.04%, −4.93%)
   [A34-16]. On 7 April 2025 TR23 fell 9.70% (lm26.md:32): the scales were 0.703 and 0.428, the scaled returns −6.81%
   and −4.15% [A34-16]. Which version could a trader run, and why does the other look safer? The solution adds that
   the index itself grew 13.32% with volatility 18.62% over the same days, and that the scale traded at its own close,
   E5's slip, grows 14.90% [A34-16].
9. A full-sample parameter (lab; TR23, the TAIEX total-return index, daily simple returns; 5,103 days after
   2006-01-02, 20.76 years in calendar days ÷ 365.25 from the close of 2 January 2006, 245.76 sessions a year): the
   exact Kelly root of (4.5) on all of TR23 is 4.14 (lm22.md:125); held from the close of 2 January 2006 it grows
   31.70% a year,
   against 22.27% for the trailing 729-return root capped to [0, 3], set at each month-end close and traded at the
   next, and 13.38% for $f=1$; borrowing at 3.5% a year on $f-1$, accrued as 3.5% ÷ 245.76 a session, turns 31.70%
   into 20.71% and 22.27% into 16.63% [A34-17]. (a) Why is 31.70% not a backtest result? (b) What does the borrowing
   rate change, and why is even 16.63% *hypothetical*? (c) State the protocol behind 22.27% (window, signal and trade
   dates, label).
10. Survivorship: the six growth factors of X5 as printed [A34-19]; equal amounts on 17 January 2017; compute the mean
    of all six and of the four survivors and the gap in log growth over 9.7221 years (calendar days ÷ 365.25 from the
    close of 17 January 2017): 0.7233, 1.0540 and $\ln(1.0540/0.7233)/9.7221$, 3.87 points a year [A34-37]. The
    solution adds that E6's 0.7234 comes from the unrounded factors and gives the same 3.87 [A34-20].
11. Python: White's reality check on Experiment 10 (TR23, the TAIEX total-return index) with LM22's `stationary_idx`
    (`default_rng([1, 20261011])`, $B=10{,}000$, $\ell=145$): p-value 0.283 (MC SE 0.0045); studentized 0.281 [A34-24,
    A34-25]. Then run the studentized reality check of the grid's 59 differences from
    R1 monthly ($B=10{,}000$). At $\ell=75$ with `default_rng([4, 20261011])` it gives 0.375 (MC SE 0.0048); at
    $\ell=17$ with `default_rng([5, 20261011])`, 0.421 (MC SE 0.0049) [A34-32]. Why does LM22's rule take the largest
    length?
12. For $n=60$ independent zero-skill strategies over 920 in-sample days, derive with (21.9) and (20.9) the median
    of the in-sample best's annualized Sharpe ratio: $\Phi^{-1}(0.5^{1/60})\sqrt{A_{\mathrm w}/920}=1.17$ with
    $A_{\mathrm w}=243.57$. Say why its expected out-of-sample value is 0. Check them against E10's means, 1.20 (SE
    0.007) and 0.00 (SE 0.016) (`default_rng([2, 20261011])`, 200 panels). Why does the mean of this maximum lie above
    its median, 1.19 against 1.17 by (21.9) [A34-33]?

**Lab parts** (`build/make_lab34.py`; reads only its `data/`, built by `data/make_lab_data.py` as the shared "Labs"
decision lists: the rules' per-date targets and exposures, the wealth frame, the eight rules' net and gross wealth
paths and the grid's 60 daily net-return series, `lm34_grid.csv`; and LM34's own files, `taiex_tr.csv` (TR23),
`0050_daily_raw.csv`, `0050_dividends.csv`, the split list (`splits__2016-12-01__2026-10-08.csv`: 0050 4-for-1 on
2025-06-18, 00673R 1 for 4 on 2025-10-22, 00674R 1 for 5 on 2026-04-22), the delisting list and the six futures
funds' prices, all Free (the snapshots are not lab files, so part 4 quotes E6's 69 and 10 from A34-18; O7)). Rebuilding (27.2) from these files, with cash at $r_f$, R8's borrowing and the
costs, is the walk-forward protocol LM34 owns, so under the shared "Labs" decision it is LM34's own procedure
(decision on the third revision); part 1 does it for R1, the extension for all eight rules. Parts: 1 the protocol:
rebuild R1's net path from its targets with (27.2), check it against the derived wealth, E1, X2; 2 costs: (34.1) for
every rule, X3, E3; 3 look-ahead: X4 and E4 from the closes and distributions, problem 8 on TR23; 4 survivorship: X5,
E6, problem 10; 5 the reality check: E7 (experiment 1), problem 11, Romano–Wolf's stepdown on Experiment 10 by their
Algorithm 4.1 with footnote 22's variant (the sample's $s_{\mathrm u}$ inside the resamples, as E7) and by Algorithm 4.2
(each resample's own), pp. 1252–1253; 6 CSCV:
E9, X8, X9 from `lm34_grid.csv`, E10 on all 200 panels; 7 the Kelly walk-forward on TR23 (lm22.md:144,
`make_lab04.py:642`): problem 9, labelled *hypothetical* (each root traded at the close after its month-end, §2's protocol, a session later than Lab 4's scaffold;
daily rebalancing to the month's leverage, no trading costs,
borrowing at 0 or 3.5%; four versions: the walk-forward, $f=1$, the full-sample root 4.14 and half of it, 2.07,
the last two *look-ahead, not achievable*); 8 problem 12. Extension (*In-sample*; declared here on 2026-10-25, before anyone has
run it and after the grid's results were seen, whose two best configurations trade every 6 month-ends [A34-27];
printed by the lab before it runs): a fourth frequency, every 12 month-end signals (signals 1, 13, …, 85 of the
through case's schedule, 2019-02-27 to 2026-02-26, 8 trades [A34-26]), for R1–R8 at the through case's own targets (R3–R8 at
504 rows), placed after the 60 in rule order, so $n=68$. The lab builds their daily net returns on the wealth frame
with its own (27.2) from the per-date targets and exposures (costs, cash at $r_f$, R8's borrowing, no terminal
liquidation), after the same code has reproduced the eight net paths and the 16 series of `lm34_grid.csv` that trade
the through case's targets every 3 or 6 month-ends. Then CSCV as in §7 ($S=16$; $\omega=j/69$, never $\tfrac12$) and
the studentized reality check against R1 monthly on the 67 differences ($\ell$ by LM22's rule on them, $B=10{,}000$,
`default_rng([6, 20261011])`). A closing sentence says that the extension is another search on the same data. Labs
write plain "LM33", "LM45", never `[[…]]`.

**Cross-module tags** (decision C8: the later briefs that cite each; Volume VIII–IX briefs are not yet written):

- (34.1) $\ln\big(W^{\text{gross}}_T/W^{\text{net}}_T\big)=-\sum_{\text{trades}}\ln\big(1-\operatorname{cost}/W^{\mathrm{pre}}\big)
  \ge\sum_{\text{trades}}\operatorname{cost}/W^{\mathrm{pre}}$, for scale-free costs, both paths trading to the same
  targets, and financing proportional to wealth (no Volume V–VI brief cites it).
- (34.2) $P^{\mathrm{adj}}_{t\mid t'}=P_{t'}/G_{t,t'}$ with $G_{t,t'}=(1+R_{t+1})(1+R_{t+2})\cdots(1+R_{t'})$, the
  compounded total returns of Volume I, $R_t=(P_t+D_t)/P_{t-1}-1$, the previous close restated per current share on a
  split day (divided by 4 on 2025-06-18, in words; no split-ratio symbol, decision B6). It depends on the build date
  $t'$, so a level from an adjusted series is look-ahead for any rule acting before $t'$. Cited by LM35, whose
  adjusted prices carry their build date as $P^{\mathrm{adj}}_{t\mid t'}$, in this written-out form. The product is
  written out because $j$ is §7's rank, as decision B6 writes it.
- (34.3) White's reality check: the share of $B$ recentred stationary resamples with
  $\max_k\sqrt T(\bar R_{k,\text{boot}}-\bar R_k)\ge\max_k\sqrt T\,\bar R_k$ ($\bar R_k$ in excess of the benchmark);
  studentized with $s_{\mathrm u,k}/\sqrt T$ (Romano and Wolf 2005, §4.1; Hansen 2005). No Volume V–VI brief cites
  it. White's (2000) Corollary 2.4 makes the unstudentized check valid as $T\to\infty$ (*stated without proof*). In
  LM34's examples large $T$ means 5,849 days for Experiment 10's 10,000 rules and 1,851 days for the grid's 59
  differences. The grid's window estimates are fixed functions of past data, so its rules count as fixed in advance
  (the editor's reading). For such rules (his case (i), with no estimated parameters), the corollary's hypotheses are:
  - each difference has a finite moment of order $6+\varepsilon$, for some $\varepsilon>0$;
  - the differences from the benchmark form a strictly stationary series whose dependence fades fast (α-mixing, its
    coefficients falling with the lag at least as fast as a power whose exponent exceeds $3(6+\varepsilon)/\varepsilon$);
  - the differences' long-run covariance matrix is positive definite (Assumption A; White adds that a singular one
    keeps the corollary, pp. 1105–1106);
  - the mean block length $\ell$ grows with $T$, but more slowly ($\ell\to\infty$ and $\ell/T\to0$);
  - the number of rules stays fixed as $T$ grows; White treats a number growing with $T$ only heuristically, and
    Experiment 10 has more rules than days.
- (34.4) CSCV and $\mathrm{PBO}=\#\{\text{splits with logit}\le0\}/\binom{S}{S/2}$, logit $=\ln\big(\omega/(1-\omega)\big)$,
  $\omega=j/(n+1)$ (no Volume V–VI brief cites it).

**Pitfalls to pre-empt.**

- Timing: the signal's close is known only after 13:30; a trade at that close is look-ahead (E5). A daily rule that
  uses the same day's return in its own scale looks safer and richer than any trader could be (problem 8).
- Adjusted prices: returns are fine, levels depend on the build date (34.2); never quote an adjusted level without
  its build date, and never feed one to a rule that acts earlier (E4; PITFALLS §3).
- Universe: E5 itself was chosen in 2026 from survivors; say so once in §5, do not change the fixed through case.
  A delisted fund is valued at its last close, an approximation (O9).
- Costs: inside the recursion, never a constant subtracted at the end (Research hygiene); 0.1425% is the notice level
  of TWSE's Art. 94 and TPEx's Art. 64, not a cap, each fund under its own market's rule, and brokers' discounts are
  not modelled; no slippage model, and the text says why the twice-the-costs sensitivity stands in for it; the
  bond-ETF exemption runs to 2026-12-31 as Art. 2-1 reads on 2026-10-24.
- The reality check asks whether the best beats the benchmark; a large p-value does not show that the rules are
  equal, and a small one does not say which rules beat it. Its block length follows LM22's rule on the series the
  statistic involves; report the sensitivity (0.375 against 0.421, E8) [A34-32].
- PBO measures how well in-sample ranks carry over within one grid, not whether the rules make money (E9); one
  sample's PBO is itself noisy (0.12 to 0.87 across noise panels, E10) [A34-33]. Adding configurations after seeing
  results is a new search: count it.
- CSCV's count is $\binom{16}{8}=12{,}870$; the paper prints 12,780 (shared decision "References").
- The Kelly walk-forward on TR23 (the TAIEX total-return index) borrows for free unless the stem says otherwise; its
  leverage sits at the cap of 3 at 178 of the 250 month-ends [A34-17], so the cap, chosen in LM4's lab, drives the
  result.
- Ownership: no rule's Sharpe ratio, volatility, VaR or drawdown is printed (LM33, LM30–LM31, LM32); R8's exposures
  are LM31's and the cost arithmetic of single trades LM27's (decision A5), echoed with their anchors.
- Near-twins (decision C7): $\tau=7.5975$ years counts calendar days ÷ 365.25 from the close before the first return,
  while LM33's span counts sessions ÷ $A_{\mathrm w}$ [A34-02]; every year count names its start (E1, E5, E6,
  problems 8–10); R8's 11.99% at a spread of 0 is not its gross 11.99% (E3) [A34-05, A34-11]; TR23 is named as the
  TAIEX total-return index beside its numbers; "month" is a month-end signal or a calendar month-end, said each time.
- Rounding: values near a rounding boundary are flagged in the anchors table only (decision C11), and the text prints
  each rounded from its unrounded value. Parts rounded separately say so where a reader could add them (X3, KC §3, E5).
  Never print a difference of two printed rounded values (for example the two scales' growth gap) unless the script
  prints it, and print an input at the digits its derived result needs (E1's wealth, E7's 3.9738, E8's 1.296).
- References: White (2000) read in a copy of the article by the drafter, for its statistic, the recentred bootstrap
  maximum (Corollary 2.4) and its p-value (one minus the observed statistic's rank among the sorted resampled ones,
  over their number); Romano and Wolf (2005) and Hansen (2005) as decision F's source check read them, with the code's
  departures said where the numbers are printed (E7); Bailey, Borwein, López de Prado and Zhu (2017) for CSCV, in the
  book's own words; Elton, Gruber and Blake (1996) only for its abstract's claim; Brown, Goetzmann, Ibbotson and Ross
  (1992) bibliographic only (Sources). The futures ETFs' tax cites the Ministry's ruling; "unsuitable for long
  holding" appears only as the issuers' own words for their four leveraged, inverse or VIX funds, never for 00635U or
  00642U.

**Curriculum guidance carried** (`plans/vol-5.md`'s table):

- Decision flow, data visible at decision time (g:69–85): §2 and §4 (what is known at 13:30; the trade at the next
  close).
- Fix windows, frequency, limits, costs and criteria before evaluation (g:111): the through case and the grid's
  declaration, printed as declared.
- "Data too thin to support more leverage" is a valid conclusion (g:116): §8 ends on it, with E8 and E9.
- Wealth ≤ 0 ends log growth (g:94): no path is ruined, and the script asserts it.
- Density (g:60–63): LM34 carries the most topics of Volume VI; Romano–Wolf's stepdown, the Kelly walk-forward and
  the extension go to the lab; Hansen's test is stated in a paragraph.
- Each outcome taught, practised and assessed (g:124): the outcome table above.
- Different failures in one case (g:87–90): LM34 shows weak growth net of costs; drawdowns and funding are LM32's
  and LM35's.

**Stage 4 for earlier modules** (decision G).

- `leads`: lm04.md:6 gains 34, lm11.md:6 gains 34 and lm20.md:6 gains 34 ((20.9), E10 and problem 12), as decision G
  lists them. lm17, lm18, lm21, lm22, lm23, lm25 and lm26 already list 34.
- lm21.md:373 (on the plan's list), proposed wording: "[[LM4]] warned that backtests overstate Sharpe ratios. [[LM33]]
  deflates a Sharpe ratio for the number of trials. [[LM34]] corrects a search on the same data (White 2000; Romano
  and Wolf 2005) and tests rules fixed in advance on later data."
- No other wording change: lm04.md:209's "largely noise" agrees with E8 and E9; research-hygiene.md:35 and 62 are kept
  by §3–§7; `make_lab04.py:642` stays on 0050 (Lab 4's own data), and LM34's lab says that it repeats the exercise on
  TR23's longer history.

**Sources** (full citations, with the version read and the locations it verified; paraphrase only, never more than a
sentence quoted; the bibliographic data follow SOURCES, from Crossref unless another source is named):

- White, H., "A Reality Check for Data Snooping", *Econometrica* 68(5): 1097–1126, September 2000, DOI
  [10.1111/1468-0262.00152](https://doi.org/10.1111/1468-0262.00152). In SOURCES ("LM21"); Crossref re-read
  2026-10-24. Read by the drafter in a copy of the article (2026-10-24): the statistic is the maximum over models of
  $\sqrt n$ times the mean performance against the benchmark; its bootstrap counterpart is the maximum of the recentred
  resampled means (Corollary 2.4); the p-value is one minus the observed statistic's rank among the sorted resampled
  ones, over their number; the resamples use Politis and Romano's stationary bootstrap. Corollary 2.4's hypotheses
  (those of Theorem 2.3, with Assumptions A and B of the appendix, pp. 1117 and 1119) and its fixed number of models
  (pp. 1110–1111) were read by Stage 1's fresh check in the published article (SOURCES). Used for (34.3) and §6's
  Deep Dive; no other result of the paper is cited.
- Romano, J. P., and M. Wolf, "Stepwise Multiple Testing as Formalized Data Snooping", *Econometrica* 73(4):
  1237–1282, July 2005, DOI [10.1111/j.1468-0262.2005.00615.x](https://doi.org/10.1111/j.1468-0262.2005.00615.x). In
  SOURCES ("LM21"); read by decision F's source check in the published article (the copy hosted at UZH, running pages
  1237–1282). The setting (p. 1245): strategies relabelled from the largest statistic to the smallest, one common
  critical value, a stepdown method (footnote 12). Algorithm 3.1 (p. 1247): reject each remaining hypothesis whose
  statistic exceeds the bootstrap quantile, at the test's level, of the maximum of the centred statistics over the
  hypotheses not yet rejected, and repeat until nothing new is rejected. Algorithm 3.2 (p. 1251) uses at least 1,000
  bootstrap data matrices, and Remark 3.4 (p. 1251) lets the sample value replace the centring parameter for a linear
  statistic under the Efron, circular or stationary bootstrap. The studentized form (§4.1, pp. 1252–1253): Algorithm
  4.1, and Algorithm 4.2 with each resample's own standard error; footnote 22: the original sample's standard error
  inside the resamples, Hansen's choice, is first-order consistent, though the resample's own is preferred. E7's first
  step uses footnote 22's variant centred at the sample means (Remark 3.4); the lab codes Algorithms 4.1 and 4.2.
- Hansen, P. R., "A Test for Superior Predictive Ability", *J. Business & Economic Statistics* 23(4): 365–380, October
  2005, DOI [10.1198/073500105000000063](https://doi.org/10.1198/073500105000000063). In SOURCES (its own entry,
  "LM21"); read by decision F's source check in the University of North
  Carolina repository's postprint, which carries the journal's layout without page numbers (its 16 pages counted from
  365). The loss differences, the benchmark's loss minus model $k$'s, and the null that their means are at most 0,
  eq. (1), p. 367; the statistic, the largest studentized mean difference floored at 0, p. 368; the consistent version
  recentres only the models whose t-statistic is at or above $-\sqrt{2\ln\ln T}$ (his $n$ is the number of returns;
  p. 368, and the bootstrap form, §3, p. 372), the logarithm being natural, from the law of the iterated logarithm
  (p. 370); the others keep their negative means. The lower and upper versions give bounds (Theorem 2, p. 371), and
  only the recentred one gives a consistent p-value (Corollary 2). Hansen uses the stationary bootstrap, recommends a
  kernel estimate of each standard deviation and keeps the test valid without it (pp. 371–372), and counts resamples
  strictly above the statistic over $B$, with no "+1" (p. 372). A34-25 follows him except for the iid $s_{\mathrm u}$
  and the count "at or above", which gives the same 0.277; E7 says both.
- Politis, D. N., and J. P. Romano, "The Stationary Bootstrap", *JASA* 89(428): 1303–1313, December 1994; Politis, D.
  N., and H. White, "Automatic Block-Length Selection for the Dependent Bootstrap", *Econometric Reviews* 23(1):
  53–70, 2004, with Patton, Politis and White's correction, 28(4): 372–375, 2009: in SOURCES ("LM22"), Crossref
  re-read 2026-10-24; the stationary resamples (LM22's draw order) and the block lengths through arch's
  `optimal_block_length` ($\ell=145$ on Experiment 10, $\ell=75$ on the grid).
- Bailey, D. H., J. M. Borwein, M. López de Prado and Q. J. Zhu, "The probability of backtest overfitting", *Journal of
  Computational Finance* 20(4): 39–69, April 2017, first published online 2016-09-19, DOI
  [10.21314/JCF.2016.322](https://doi.org/10.21314/JCF.2016.322). Crossref holds no volume, issue or pages; they come
  from the publisher's article page at risk.net (read by decision F's source check and again for the SOURCES draft:
  "Volume 20, Number 4 (April 2017)", "Pages: 39-69"); the year printed is 2017. CSCV (Algorithm 2.3) was read in the
  authors' Lawrence Berkeley National Laboratory manuscript of 27 February 2015 (eScholarship, which lists the article
  as *J. Computational Finance* 20(4), 2017); the JCF text was not compared. The steps: the $T\times n$ matrix of the
  trials' synchronous performance; $S$ equal blocks of rows, $S$ even; every choice of $S/2$ blocks as the in-sample
  set, eq. (2.3), each half kept in time order, the rest out of sample; the in-sample best's out-of-sample rank over
  $n+1$ and its logit; their relative frequency, eq. (2.4). PBO is the mass of logits at or below 0 (§3.1), and §3.2
  adds the degradation regression and the probability of loss. The manuscript prints 12,780 for
  $\binom{16}{8}=12{,}870$, calls the in-sample set the testing set in step c) and drops the bars in step f), so §7
  states the steps in the book's own words, citing the manuscript. Dropping the earliest rows to make 16 equal blocks
  is the book's convention, said once. Used for (34.4) and §7.
- Elton, E. J., M. J. Gruber and C. R. Blake, "Survivor Bias and Mutual Fund Performance", *Review of Financial
  Studies* 9(4): 1097–1120, October 1996, DOI [10.1093/rfs/9.4.1097](https://doi.org/10.1093/rfs/9.4.1097). Abstract
  only (OpenAlex's copy, read 2026-10-24): funds that disappear tend to do so after poor performance; the study tracks
  every fund that existed at the end of 1976 and follows mergers. Text not read; one sentence in §5.
- Brown, S. J., W. Goetzmann, R. G. Ibbotson and S. A. Ross, "Survivorship Bias in Performance Studies", *Review of
  Financial Studies* 5(4): 553–580, October 1992, DOI [10.1093/rfs/5.4.553](https://doi.org/10.1093/rfs/5.4.553).
  Bibliographic data only: the abstract OpenAlex holds describes a conference presentation of March 1994, not this
  article, so no claim rests on it. Optional; the text needs it only as a second name beside Elton et al.
- Sullivan, R., A. Timmermann and H. White, "Data-Snooping, Technical Trading Rule Performance, and the Bootstrap",
  *Journal of Finance* 54(5): 1647–1691, October 1999, DOI
  [10.1111/0022-1082.00163](https://doi.org/10.1111/0022-1082.00163): in SOURCES ("LM21", its abstract: the reality
  check applied to technical rules on 100 years of daily Dow Jones data); one sentence in §6, at the level of that
  abstract.
- Bailey and López de Prado (2014), the deflated Sharpe ratio, *JPM* 40(5): 94–107, and Harvey and Liu (2015),
  "Backtesting", *JPM* 42(1): 13–28 (Crossref's pages): LM33's sources, cited by pointer only; LM34 prints no page or
  equation of either (Harvey and Liu are cited by section and equation where LM33 cites them, not by the Duke copy's
  page numbers).
- Not relied on: Bailey, Borwein, López de Prado and Zhu, "Pseudo-Mathematics and Financial Charlatanism: The Effects
  of Backtest Overfitting on Out-of-Sample Performance", *Notices of the AMS* 61(5): 458–471, May 2014, DOI
  [10.1090/noti1105](https://doi.org/10.1090/noti1105) (Crossref holds the first page only; the end page comes from the
  AMS PDF's running heads).
- 證券交易稅條例 (Securities Transaction Tax Act), [law.moj.gov.tw, pcode
  G0340078](https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=G0340078), read 2026-10-24 by the drafter, the SOURCES
  draft and the second source hunt (the database's data cut-off 115-10-16). Art. 2: the seller pays on each trade's
  price, item 1 千分之三 on the shares of a company, item 2 千分之一 on corporate bonds and other securities approved by the
  government (其他經政府核准之有價證券); Art. 2 was last amended on 1993-01-30. Art. 2-1 ¶2: from 2017-01-01 to 2026-12-31 the tax
  on sales of listed and OTC-listed (上市及上櫃) bond ETFs of securities investment trust enterprises is suspended,
  leveraged and inverse bond ETFs excluded, so on TWSE and TPEx alike (00679B is on TPEx); Art. 2-1 was last amended
  on 2016-12-30, and its three paragraphs were read again on 2026-10-25 by the TPEx source check. The Act's last
  amendment, 2025-01-02, changed only Arts. 2-2 and 12. The Act names no ETF: that ETF sales pay item 2's rate is
  stated by TWSE's ETF rules page and the Ministry's notice, and for futures-trust funds by the Ministry's ruling
  (next entries); §3 says so rather than reading the statute as naming them (Y16).
- 財政部 (Ministry of Finance), ruling 97/08/11 台財稅字第09700161260號函, in its ruling database (法令彙編函釋檢索系統,
  [ttc.mof.gov.tw/FB/FB120/139155](https://ttc.mof.gov.tw/FB/FB120/139155)), filed under 證券交易稅條例 (114年版),
  Art. 2; read 2026-10-24 by the second source hunt. It taxes a transfer of the beneficial certificates of a futures
  trust fund at 1‰ of each trade's price under Art. 2 item 2 (受益憑證之轉讓，應依證券交易稅條例第2條第2款規定，按每次
  交易成交價格1‰課徵證券交易稅). The direct official statement for 00635U's and 00642U's 0.1% (shared decision "Cost
  model"); problem 1's key stands.
- 臺灣證券交易所股份有限公司營業細則 (TWSE Operating Rules), version 115.09.24 as read on 2026-10-24 (the page carried 115.10.19 on 2026-10-31, Arts. 3 and 94 unchanged), [twse-regulation.twse.com.tw, FID
  FL007304](https://twse-regulation.twse.com.tw/m/LawContent.aspx?FID=FL007304), read 2026-10-24 by the drafter and
  the SOURCES draft: Art. 94, a broker may set its own rate and must notify a client before the order, and keep a
  record, when the rate exceeds 1.425‰ of the value traded, so 0.1425% is a reference, not a cap; Art. 3, the session
  runs from 09:00 to 13:30 (the close is known only after 13:30, §2). These are TWSE's rules, for the TWSE-listed
  funds (0050, 00646 and the six survivorship funds, 00635U and 00642U among them).
- 財團法人中華民國證券櫃檯買賣中心證券商營業處所買賣有價證券業務規則 (TPEx Business Rules), current version 2026-10-21, [selaw
  LW10812069](https://www.selaw.com.tw/Chinese/RegulatoryInformationResult?sysNumber=LW10812069), and TPEx's
  指數股票型基金及主動式交易所交易基金受益憑證買賣辦法 (the ETF rules), current version 2025-09-30, [selaw
  LW10845400](https://www.selaw.com.tw/Chinese/RegulatoryInformationResult?sysNumber=LW10845400), the database to
  which TPEx's ETF rules page refers; read 2026-10-25 by the TPEx source check and its verifier. Business Rules Art.
  64, applied to ETFs by the ETF rules' Art. 15 ¶1 (準用上櫃股票規定之費率辦理): TPEx drafts the rate and the authority approves
  it; a broker may set its own schedule but must notify a client before applying, and keep a record, a rate above
  千分之一點四二五 of the value traded, so 0.1425% is a reference on TPEx too. ¶1–¶3 are unchanged since 2008-02-12 (the
  article was last amended on 2011-12-16, in ¶4 and ¶5 only). Art. 40 item 一, applied to ETFs by the ETF rules' Art. 4
  ¶2: matching from 09:00 to 13:30, so 00679B's close is also known only after 13:30 (§2). 00679B has traded on TPEx
  since 2017-01-17 (TPEx's listing notice of 2017-01-13; TWSE's ISIN page), and TPEx's product page gives its tax as
  「依證券交易稅條例第2條之1規定」.
- 財政部統計處 財政統計通報 (Ministry of Finance, statistics notice) No. 21, 2024-11-14, on ETF trading in
  January–September 2024,
  [service.mof.gov.tw](https://service.mof.gov.tw/public/Data/statistic/bulletin/113/%E7%AC%AC21%E8%99%9F_ETF%E8%AD%89%E4%BA%A4%E7%A8%85.pdf)
  (`Last-Modified` 2024-11-13); read on 2026-10-24 by the editor (decision F) and, as a page image, by the source
  check; the second hunt's copy is byte-identical. Paragraph 1 gives the ETF rate, 千分之1, below the rate on ordinary stocks;
  paragraph 2 the bond-ETF exemption from 民國106 to 115 (2017–2026); the table "113年1-9月ETF成交狀況－按投資標的分"
  has a 原型期貨 (plain futures ETF) column with its turnover and its tax (0.2 億元). The notice prints no rate per
  column, so it supports the ruling and is not cited as stating the futures ETFs' rate.
- TWSE, ETF 專區, the rules page,
  [twse.com.tw/zh/products/securities/etf/overview/rules.html](https://www.twse.com.tw/zh/products/securities/etf/overview/rules.html),
  read 2026-10-24 by the source check and the SOURCES draft; the page prints no date (footer ©2023; the server's
  `Last-Modified` 2026-10-22). Its tax row: "證交稅：ETF賣方課徵0.1% (債券ETF免徵證交稅10年至2026年)". It speaks for TWSE-listed ETFs;
  for 00679B, TPEx's product page (the TPEx entry above) gives the exchange-level support.
- TWSE, ETF 總覽 (the overview page),
  [twse.com.tw/zh/products/securities/etf/overview/introduction.html](https://www.twse.com.tw/zh/products/securities/etf/overview/introduction.html)
  (`Last-Modified` 2026-10-22), read 2026-10-24 by the reviser and confirmed in a saved copy by the second source
  hunt. Under §三, 期貨轉倉成本: a futures-trust ETF tracks a futures index and rolls by the index's rules; when far
  contracts cost more than near ones (正價差) the manager buys high and sells low, and the losses the roll may produce
  (可能產生之損失) cannot be avoided. Under §四: a leveraged or inverse ETF's multiple holds for a single day, and under
  daily compounding its long-run return departs from the multiple. The page does not call futures ETFs in general
  unsuitable for long holding. §5 prints the roll sentence with its "may" and the §四 point for 00672L, 00673R and
  00674R.
- The six survivorship funds (the second source hunt, 2026-10-24): Yuanta's fund pages (00635U, 00642U, 00673R,
  00674R) and TWSE's ETF e添富 fund pages of the four listed funds
  (`twse.com.tw/zh/ETFortune-institute/etfInfo/<code>`). The two delisted funds rest on TWSE's announcements (00672L:
  2020-07-07 and 2020-10-12; 00677U: 2021-04-29), Yuanta's umbrella prospectus (00672L; 元大標普油金傘型期貨信託基金,
  `Last-Modified` 2026-10-08) and Fubon's releases of 2016-12-06 and 2021-05-03 (00677U). No fund page of either is
  cited: Yuanta's page for 00672L answers 查無此商品, and e添富's pages for 00672L and 00677U return its home page. Each is a
  futures-trust ETF on a futures index: 00635U, S&P GSCI Gold Excess Return (COMEX gold); 00642U, S&P GSCI Crude Oil
  Enhanced Excess Return (NYMEX WTI); 00672L, S&P GSCI crude oil ER, daily +2× (WTI futures; the index's exact title
  is not in the documents read); 00673R, S&P GSCI Crude Oil 1x Inverse Index ER; 00674R, S&P GSCI Gold 1x Inverse
  Index ER; 00677U, 標普500波動率短期期貨ER指數, S&P 500 VIX Short-term Futures Index Excess Return (Fubon's release of 2016;
  near- and next-month VIX futures, rolled daily). All six are listed on TWSE, none on TPEx (TWSE's ISIN page for the
  four listed funds and TWSE's announcements for the two delisted ones; the TPEx source check, 2026-10-25), so their
  cost rules are TWSE's. 00672L was delisted on 2020-11-13 and 00677U on 2021-06-03, as A34-19 finds. The issuers' own
  warnings may be quoted only as theirs and only for their funds: Yuanta's prospectus cover for 00672L, 00673R and
  00674R (策略交易型產品，不適合長期持有) and Fubon (2016) for 00677U (不適合長期作為買方); never for 00635U or 00642U.
- FinMind datasets `TaiwanStockPrice`, `TaiwanStockDividendResult`, `TaiwanStockSplitPrice`,
  `TaiwanStockTotalReturnIndex` and `TaiwanStockDelisting` (retrieval dates under Data role), cited in every exhibit's
  Source line; `TaiwanStockInfo`, retrieved 2026-10-24 by the drafter with no file kept, for the six funds' names
  (`FUTURES6` in the script; the delisting file confirms 00672L's and 00677U's): SOURCES records the query, its date
  and the six codes and names, and no extract is registered (decisions on the first and third revisions; the query's
  parameters were not kept); arch's `optimal_block_length` and `StationaryBootstrap` (SOURCES, "Python (Volume IV)").

**Chinese terms** (樂詞網, searched 2026-10-24 by the drafter and re-run by the fresh pass of 1,817 searches, whose
readings this table follows; the shared decision's list for the rest):

| English | 樂詞網 | Book |
|:--|:--|:--|
| backtest; backtesting | none; 回溯測試 (管理學名詞) | 回測 (book's form, shared decision; lm21.md:189) |
| walk-forward test | none | 滾動前進測試 (book's form; the brief keeps it, with the English in every box) |
| look-ahead bias; survivorship bias | none (survivorship curve 存活曲線 in the life sciences only) | 前視偏誤; 存活者偏誤 (book's forms, shared decision) |
| data snooping | 資料偵伺 (統計學名詞) | 資料偵伺 (LM21) |
| overfitting | 過度配適 (統計學名詞) | 過度配適 |
| cross-validation | 交叉確認 (統計學名詞; 經濟學 交叉驗證) | 交叉確認 |
| selection bias | 選擇偏誤；選擇偏差 (統計學名詞); 選擇偏差 (管理學名詞) | 選擇偏誤 |
| familywise error rate | 族系誤差率 (統計學名詞) | 族系誤差率 (LM21) |
| logit | 對數勝算；邏輯式 (統計學名詞) | 對數勝算 |
| rank | 秩 (統計學名詞, 數學名詞) | 秩, glossed once in §7's box as 名次 (the book's other 秩 is a matrix's rank, lm09.md:473) |
| bootstrap; stationary bootstrap | 自助重抽法；靴拔重抽法 (統計學名詞); none | 自助重抽法; 平穩自助重抽法 (LM22's form) |
| transaction cost | 交易成本 (管理學名詞; also 經濟學 and 管理學名詞-會計學) | 交易成本 |
| commission | 佣金 (管理學名詞, also 管理學名詞-會計學); 傭金，手續費 (會計學) | 手續費 (as LM27) |
| securities transaction tax | 證券交易稅 (管理學名詞, also 會計學; 經濟學 lists only "transaction tax" 交易稅) | 證券交易稅 (the listing's form and the statute's name) |
| turnover; turnover rate | 離職；週轉 (管理學名詞); 周轉率 (管理學名詞), 週轉率 (會計學, 電子計算機名詞) | 週轉率 (shared decision; as LM27, LM29, LM31) |
| delisting | none (電子計算機名詞 刪除表列; 下市 occurs only in 管理學名詞-會計學's 下市交易, "going-private transaction", another idea) | 下市 (the common form) |
| contango | 正向市場 (管理學名詞); 延期交割費 (會計學); no entry for 正價差 | 正價差, TWSE's word (§5) |
| benchmark | 基準 (統計學名詞); 比較基準 (管理學名詞) | 基準 |

**Open before Stage 2** (each with a recommendation and its evidence). Closed by the editor's decisions, decision F's
source check and the second source hunt of 2026-10-24, the decisions on the third revision of 2026-10-25 and the
editor's choices on the fresh check of the whole of Stage 1 (2026-10-31), kept here only as a record:

- O1 (the survivorship files are registered, commit 6b02e71, with `--exclude vol6/etf_snapshot` for a Free account;
  the 33-fund cohort is not registered and A34-21 is withdrawn).
- O2 (the notice and TWSE's ETF page were read; the notice's URL is under Sources, from the second hunt; the futures
  ETFs' 0.1% cites the Ministry's ruling, with the page and the notice in support, as decided).
- O3 (Hansen's threshold $-\sqrt{2\ln\ln T}$, p. 368, keeps A34-25; E7 prints the SPA p-value 0.277 with the code's two
  departures and names Romano and Wolf's first step with footnote 22's variant and Remark 3.4's centring; the lab codes
  Algorithms 4.1 and 4.2).
- O4 (decision E: X3 shows gross against net log growth); O5 (the prerequisite tags as listed; lm20.md gains lead 34
  at Stage 4, decision G); O6 (decision D: $\ell=75$, 17 as the sensitivity); O7 (the shared "Labs" decision lists
  `lm34_grid.csv`); O8 (*J. Computational Finance* 20(4): 39–69, April 2017, online 2016-09-19; 2017 is printed); O9
  (the last traded close values a delisted fund, said in X5's note and §5); O10 (the widget runs CSCV live, checked in
  Node); O11 (LM27's §4 points to §5, which says once that E5 was chosen from survivors).
- O12, the six funds (closed by the second source hunt). The issuers' and TWSE's documents confirm that all six are
  futures-trust ETFs on futures indices, three of them daily leveraged or inverse (Sources), so §5 may call them
  futures ETFs and says that the gap mixes product types. No extract is registered: SOURCES records the
  `TaiwanStockInfo` query (2026-10-24, the six codes and names; decision on the third revision).
- O13, TWSE's futures-ETF sentence (closed by the second source hunt, which confirmed it in a saved copy). §5 prints
  the roll's possible loss in 正價差 with TWSE's "may" (可能) and the URL; "unsuitable for long holding" appears, if
  at all, only as Yuanta's and Fubon's own words for 00672L, 00673R, 00674R and 00677U.
- The Executive Yuan draft on the bond-ETF exemption is dropped (no source is recorded; decision on the second
  recomputation).
- Tag users and leads (decisions C8 and C9; closed by the second cross-check, which found every tag of LM30–LM35
  listed correctly and every cited tag present with the content its user assumes; "Tags and leads (Y1, Y13, Y14)"
  asks nothing of LM34). LM34's list stands: (34.2) is cited by LM35; (34.1), (34.3) and (34.4) by no Volume V–VI
  brief; of the leads `[35, 45, 46, 48, 49, 50]`, LM35 cites (34.2) and each of the others has a pointer sentence in
  the text ("Uses before taught").
- The split-ratio symbol (Y2, decision B6): gone from the brief, (34.2), the Notation note, the Data role and A34-14's
  definition; the split day's restated close is said in words.

- O14, the index letter of (34.2) (closed by the decisions on the third revision). $j$ is §7's out-of-sample rank
  (notation table; AUTHORING §6: an index letter keeps one meaning in a module), so (34.2) writes the product out,
  $(1+R_{t+1})(1+R_{t+2})\cdots(1+R_{t'})$, with no index letter; decision B6 now reads the same, and LM35 cites this
  form.
- O15, the lab's extension (closed by the decisions on the third revision). The fourth window of 756 rows (in the Lab
  parts since the first draft) cannot run: the grid's first 12 signals (2019-02-27 to 2020-01-31) have fewer than 756
  estimation rows, and the lab carries no copy of `vol5_rules.py` to compute R3–R8 at a new window (shared decision
  "Labs"). The editor accepted the replacement, a fourth frequency, every 12 month-end signals at the through case's
  own targets ($n=68$), declared before it is run and after the grid's results were seen, as the declaration says;
  rebuilding (27.2) with cash, borrowing and costs from the shared files is LM34's own procedure under "Labs".
- The fresh check of the whole of Stage 1 (closed by the editor's choices of 2026-10-31). B34-01, option (A): both
  TR23 rules follow §2's protocol; problem 8 compares 15.08% with 16.70% on 5,344 days and its solution adds E5's
  slip, 14.90%, and the index's 13.32%; problem 9 and lab part 7 trade each Kelly root at the next close (A34-16 and
  A34-17 recomputed). B34-07: White's conditions, read in the published article, are in (34.3) and in SOURCES, and
  §6 says that Experiment 10 lies outside White's fixed number of rules while the grid lies closer to it. B34-12,
  option (A): the word plan. B34-28, option (a): A34-38, the rules' growth at $r_f$ of 0% and 2%. The changed rows
  were reproduced by the fresh verification of 2026-10-31 (`## LM34` of `plans/vol-6-anchors.md`).

Still open: none.

## LM35 Stress Testing

Stage 1 brief, drafted 2026-10-24 from the editor's spine (`plans/vol-5.md`, "### Spine of LM35 Stress Testing") and
the shared decisions above it, and revised three times the same day: to the editor's decisions on the briefs
(`plans/vol-5.md`, "Editor's decisions on the briefs", A–G and "Per module") with the first recomputation, the
cross-module check and decision F's source check; then to the "Decisions on the first revision"; and now to the
"Decisions on the second recomputation and cross-check" with the second recomputation's findings, the cross-check's Y
items and the second source hunt (BCBS d450, Breuer et al., Fubon's and Invesco's pages, TWSE's 2020 schedule); a
fresh verifier's ten minor findings on that third revision were repaired on 2026-10-25, and the brief was finished
the same day to a re-check's five minor findings and the "Decisions on the third revision" (LM35 and "Listing
markets": 00679B and 00720B trade on TPEx, the other funds on TWSE). The fresh check of the whole of Stage 1
(2026-10-31) is applied: its confirmed findings, with the editor's choices (GLD stands in for 00635U in 2015; E7's
tail correlation carries its standard error; checkpoint task (e) runs R8 at the cap 1.5 only), and the anchor changes
they need (A35-02, A35-33, A35-35, A35-40, A35-41). Every number carries its
anchor ID at first appearance; `data/vol6_anchors_lm35.py` prints them all (58 rows, `## LM35` of
`plans/vol-6-anchors.md`) from the registered raw files, the US proxies and 0050's 2007–2008 files included
(`6b02e71`, retrieved 2026-10-24). Numbers quoted from published modules carry their file:line instead. An echo of a
sibling brief's number cites the owner's anchor ID where it is printed, at no more than the owner's precision
(decision C12). The anchors table flags a value within a tenth of a unit of a rounding boundary; the text prints
the value rounded from its unrounded one, without a flag mark (decision C11).

**Prereq:** `[1, 2, 8, 16, 23, 26, 27, 28, 29, 30, 31, 32, 33, 34]` (tags rechecked in `src/` on 2026-10-24; LM27–LM34
are briefs, so their tags are the briefs' of 2026-10-24 and are rechecked at Stage 3). What each supplies:

- LM1: drawdown $\mathrm{DD}_t:=1-W_t/\max(W_0,\dots,W_t)$ (lm01.md:519) and (1.17), the gain needed to recover
  (lm01.md:521). E1 contrasts a window's own peak with this running peak.
- LM2: 00631L's −19.995% and 0050's −10.000% on 7 April 2025, both at their limits, and the next session's −11.20%
  and −3.25% (lm02.md:498); TWSE's limit of 10% times the multiple for a leveraged ETF on a domestic index (same
  line); TAIFEX's margins of NT\$701,000 initial and NT\$538,000 maintenance per TX contract, effective 12 August 2026
  (lm02.md:462); leverage as notional ÷ equity (lm02.md:460).
- LM8: (8.2) $\Delta W=\mathbf h^{\top}\Delta\mathbf P$ (lm08.md:102), (8.4) $\Delta W=W_0\,\mathbf f^{\top}\mathbf R$
  (lm08.md:130), (8.13) $Y\mathbf h$, the P&L of one book on many dates (lm08.md:387). A scenario is one more row of
  $Y$. LM8 already lists 35 in its leads.
- LM16: (16.4) $\mathbf a^{\top}\Sigma\mathbf a=\Var(\mathbf a^{\top}\mathbf X)$ (lm16.md:220); the squared Mahalanobis
  distance $d^2$ defined with (16.7) (lm16.md:322); (16.8), the conditional law of a normal pair and
  $\beta=\sigma_{XY}/\sigma_X^2$ (lm16.md:339); (16.9), the $\chi^2_2$ tail of $d^2$ (lm16.md:365), which LM35 does
  **not** attach to any scenario (shared decision "LM35 against LM39"); (16.10), the correlation given an event
  (lm16.md:444), which `plans/vol-3.md:1543` routes to LM32 and LM35, with its remark that a one-sided tail narrows
  the spread of a normal variable (lm16.md:449). LM16 already lists 35.
- LM23: (23.1) OLS (lm23.md:66), for the funds' betas on TR23; TX's settlement price $F_t=49{,}357$ on 8 October 2026
  and a contract worth $200F_t$ NT\$ (lm23.md:327).
- LM26: (26.2), the EWMA forecast (lm26.md:99), through LM31's R8; TR23's −9.70% on 2025-04-07, its largest fall
  (lm26.md:32), which LM35 cites there and does not anchor again (decision A5).
- LM27 (brief): (27.1) the portfolio return, drift and the ruin rule $1+R_{p,t}\le0$; (27.2) the wealth recursion with
  costs; (27.3) the one-way turnover (the checkpoint's limit); (27.5) $\beta_{i,p}$ (problem 7); (27.8) the factor
  split of $\sigma_p^2$ (E6); R1 and R2; the full-sample correlations of A27-11. (27.3)'s user list gains LM35 by the
  cross-check's tag table (Y1; decision "Tags and leads").
- LM28 (brief): (28.1), the minimum of a quadratic form under linear equalities with LM7's signs, used for the reverse
  stress test (35.4) and its bounded version; R3 and R4 unconstrained. (28.1)'s user list gains LM35 by the same
  table.
- LM29 (brief): (29.4), KKT conditions and their sufficiency for convex problems, the solver-output rule and cvxpy,
  for the bounded reverse stress test; R3 and R4 in their long-only form. (29.4)'s user list gains LM35 by the same
  table.
- LM30 (brief): R5; (30.4), constraints as implicit shrinkage (Jagannathan and Ma 2003), for the checkpoint's "how
  constraints change the allocation".
- LM31 (brief): R6 (31.1), R7, and R8's exposure (31.7) with its cap of 1.5, cash and borrowing; R8's exposure path,
  whose largest uncapped ratio, 2.14 (A31-29), 0.884 after the trade of 2 March 2020 (A31-33) and 1.33 after that of
  1 April 2025 (A31-32) LM35 echoes; LM31 hands LM35 "what R8 lost on 7 April 2025" and "R8's crash behaviour and its
  caps against the ruin line".
- LM32 (brief): VaR and ES as statistics of a return distribution, (32.9)'s $\mathrm{DD}^0_t$ and $\mathrm{MDD}$, the
  rules' drawdowns (A32-35); LM35 contrasts a scenario loss with them and cites the drawdowns in the four failure forms
  (§9).
- LM33 (brief): the Sharpe ratio's HAC standard error (33.1), for the checkpoint's out-of-sample comparison (decision
  C9: LM33's leads gain 35).
- LM34 (brief): the rules' net log growth (A34-04, the first failure form, §9); (34.2)'s adjusted price
  $P^{\mathrm{adj}}_{t\mid t'}=P_{t'}/G_{t,t'}$, which compounds Volume I's total returns,
  $G_{t,t'}=(1+R_{t+1})\cdots(1+R_{t'})$, with no split-ratio symbol (decision B6), and carries its build date $t'$
  (the US proxies); the official cost sources. The product is written out as LM34 writes it (its O14), since an index
  letter $j$ would also clash with LM35's fund index $j$.

**Leads:** `[39, 44, 46]`: LM39 (§7's pointer: jump models for the gaps that LM35 replays without probabilities),
LM44 (§8's pointer: drawdown control), LM46 (§8's pointer: margin regimes and leverage instruments). These are the
forward pointers of the text (shared decision "Leads and tags"); LM45 and LM48 are not leads, since no sentence of the
text points to them (decision "Tags and leads", Y13). No later brief exists yet, so the tag list below names no user
module (decision C8); Volume VIII and IX briefs add theirs.

**Forward links honoured.**

| Earlier text | Promise | Kept in |
|:--|:--|:--|
| `src/syllabus.yaml:87` | "Taiwan crash scenarios (2008, 2015, 2020, 2024/8/5, 2025/4/7) and overnight gaps, replayed on a portfolio" | §2 (the five windows), §3 (replays on the rules' books), §4 (2008, 2015 on proxies), §7 (T5S gaps) |
| `plans/vol-2.md:158` | "shocks (LM35)" in LM8's list of later uses | §3: a scenario is (8.4) with $\mathbf R^{\mathrm{sc}}$ |
| `plans/vol-2.md:259–262` | (8.2) and (8.13) cited by LM35 | §3, (35.1): $W_0\mathbf f^{\top}\mathbf R^{\mathrm{sc}}$; the frozen book is LM8's buy-and-hold $\mathbf h$ |
| `plans/vol-3.md:1543` | (16.10) for LM32 and LM35 | §5, E7: (16.10) against the data on 0050's 48 worst days |
| ROADMAP, Module boundaries, Stress row | replay historical or specified shocks, assign no probabilities | §6 (a distance, not (16.9)), §9 |
| ROADMAP, Per-volume notes, VI row | scenarios 2008, 2015, 2020, 2024-08-05, 2025-04-07 without probabilities; T5S per-day statistics for overnight gaps | §2, §7 (X5) |
| LM27 brief ("LM35 shows a book that can" reach wealth ≤ 0) | a book that can be ruined | §8: ruin leverage (35.2), X7 |
| LM31 brief §7 ("What R8 lost on 7 April 2025 is LM35's replay"); Leaves ("R8's crash behaviour and its caps against the ruin line") | R8's crash loss; caps against ruin | §1 and §3 (X1's note row and X3's table: R8's loss on 2025-04-07 [A35-13]; E3: R8's trade of 3 March 2025 from 1.005 to 1.319 [A35-42]), §8 (X7 with the cap and R8's largest uncapped ratio, 2.14 [A31-29]; decision E) |
| LM30 brief, tags ((30.4) for the checkpoint) | how constraints change the allocation | Lab part 9 (checkpoint task (d), rubric item 7) |
| LM33 brief, leads (decision C9) | the Sharpe ratio's interval in the checkpoint | Lab part 9 (task (b), (33.1)) |

The grep of `src/*.md` and `src/pages/*.md` for `[[LM35` finds no line, and `build/make_lab*.py` has no "LM35"
(2026-10-24): no published text promises anything to LM35. The rows above are the plans' and the sibling briefs'
promises; the spine missed none of the published ones (there are none) and listed the plans' three.

**Outcomes** ("After this module you should be able to:"; the level in brackets is the brief's, the page keeps
AUTHORING §3's form):

1. [C] replay a historical scenario: define its window, split the frozen and named-day losses by fund, and compare
   the rule's own path
2. [C] replay a hypothetical scenario on proxies, convert US returns into New Taiwan dollars, and check each proxy
   against its fund
3. [D] derive a factor shock through betas and a partial scenario from the conditional mean (16.8), and check a
   correlation break for positive semidefiniteness
4. [D] derive the reverse stress test, the shock of least Mahalanobis distance reaching a loss, and solve it under a
   price limit in cvxpy, checked by KKT
5. [C] compute a levered book's loss at a limit lock and at the next open, its ruin leverage $-1/R$, and the fall
   that triggers a margin call
6. [U] explain how price limits, holidays and overnight gaps change a "one-day" loss, and which funds have no daily
   limit under TWSE's and TPEx's rules
7. [U] explain why a stress test assigns no probability and why surviving the named scenarios does not cover unseen
   losses
8. [U] compare weak growth, a drawdown limit, funding and ruin as four failures of the same rules

(Words per outcome, AUTHORING §1's count without the level mark: 21, 20, 23, 26, 26, 24, 19, 16; the draft's 1, 2, 4,
5 and 7 ran over 30 and are cut, or split into 7 and 8, decision C10; outcomes 1, 2, 3 and 5, at 25–27 words in the
second revision, are trimmed for the cross-check's Y20; outcome 6 names both markets, decision "Listing markets".)

| Outcome | Taught | Practised | Assessed |
|:--|:--|:--|:--|
| 1 [C] | §2, §3 | E1–E3; Lab 2–3 | KC §2, §3; problems 1, 9, 10 |
| 2 [C] | §4 | E4, E5; Lab 4 | KC §4; problem 4 |
| 3 [D] | §5 | E6, E7; Lab 5 | KC §5; problems 6, 8 |
| 4 [D] | §6 | E8; Lab 6 | KC §6; problems 5, 7, 11 |
| 5 [C] | §7, §8 | E9, E10; Lab 7 | KC §7, §8; problems 2, 3, 12 |
| 6 [U] | §2, §7 | E1 (holiday spans), E9, X5, X8 | KC §2, §7; problem 3 |
| 7 [U] | §6, §9 | E8 (the worst loss within the sample's largest distance); Lab 9 (rubric item 6) | KC §6, §9 |
| 8 [U] | §8, §9 | §9's table; E10 (funding against ruin) | KC §8; problem 12's last question |

**Owns.** Historical replay: scenario windows on TR23 (peak, trough, the worst day, the worst 5 and 20 sessions;
the definitions below); the frozen replay (35.1) on a book's exposures at the window's first close, the named-day
replay on the previous close's exposures, and the rule's actual path, for 2020, 2024-08-05 and 2025-04-07 on the
rules' own books; 2008 and 2015 on the rules' first weights, on 0050 itself and on US proxies (capability B5),
labelled *hypothetical*; the proxy pairing rule (35.5) and its blind spot (US holidays); loss attribution
$f_iR^{\mathrm{sc}}_i$; returns that span holidays; hypothetical shocks: a factor shock through betas, the partial
scenario (35.3) with (16.8), a correlation break checked for positive semidefiniteness, the constructed "worst of
each" day; reverse stress testing (35.4) with the Mahalanobis distance as a ranking, closed form and a version
bounded by 0050's limit (cvxpy, KKT); leverage and ruin (35.2), $1+L R^{\mathrm{sc}}_p\le0$, reported, never
floored; limit locks (sales only at the limit; the next open's loss); TWSE's and TPEx's limit rules for domestic
and cross-border ETFs; the overnight gap from T5S per-day statistics; TX on limit days and the dated TAIFEX margin; the
four failure forms compared on the same rules (guidance g:87–90). The rules' scenario losses are LM35's numbers,
each rule's loss on 2025-04-07 included (shared decision "Owners", decision A1: LM32 points here), and the T5S
per-day lows of 2025-04-07 and 2024-08-05 (A35-45; decision A5: LM32's lab echoes them). Values owned: every A35
anchor except the echoed inputs. The text prints each echo with its owner's ID at no more than the owner's precision
(decision C12): the full-sample correlations −0.105, 0.599 and −0.023 (A27-11); R8's largest uncapped ratio 2.14
(A31-29) and its exposures after the trades of 2 March 2020, 0.884 (A31-33), and 1 April 2025, 1.33 (A31-32);
00631L's −19.995% and −11.20% (lm02.md:498); TR23's 5,849 returns (lm19.md:46) and its −9.70% on 2025-04-07
(lm26.md:32); TX's $F_t=49{,}357$ (lm23.md:327). The rules' weights (A35-23, A35-38, LM27–LM31's) are replay inputs
that LM35's rows echo from `vol5_rules`' files. R8's exposures at its trades into the windows are LM35's A35-42,
except the two that LM31 prints (A31-32, A31-33), which the text prints with LM31's IDs. The lab's final part is the
batch's checkpoint.

**Leaves.** Probabilities of extreme moves and jump models → LM39. Margin regimes, margin trading (融資) and leverage
instruments → LM46. Drawdown control and drawdown probabilities under a model → LM44 (LM32's drawdowns are empirical).
Kelly sizing under gaps and fat tails → LM45, and the capstone's own data and scenarios → LM48 (both scope notes
only: the text names neither, so neither is a lead). Margin calls tested on intraday paths → Volume VIII (ROADMAP's
VIII row: minute bars). VaR, ES and their backtests → LM32 (cited). Filtered
historical simulation, scenario generation by empirical likelihood and stress tests of liquidity → not in the book, one
sentence in §9.

**Uses before taught** (one sentence each in the text):

- §7: "Prices that jump between one close and the next open are what [[LM39]] models; this module replays such jumps
  and gives them no probability."
- §8: "How exchanges set margins, and how margin loans and futures carry leverage, is [[LM46]]'s subject; this module
  uses TAIFEX's table effective 12 August 2026, as [[LM2]] quotes it."
- §8: "Rules that cut exposure as a drawdown deepens are [[LM44]]'s drawdown control; here exposure stays fixed through
  the scenario."

**Data role.**

- **E5's wealth frame and the rules' books** (`vol5_series.frames("E5")`, `vol5_trades.parquet`,
  `vol5_rules.parquet`): estimation frame $T=2{,}362$ (2017-01-18 → 2026-10-08), $A=242.95$; wealth frame 2,368
  sessions, $A_{\mathrm w}=243.57$; both over 9.72 calendar years from the close of 2017-01-17, the close before the
  first return (decision C7) [A35-01; LM27's A27-01 to A27-03]. The script rebuilds each rule's exposures day by day from the stored
  targets and costs with the through case's recursion and stops unless the rebuilt wealth matches `vol5_rules.parquet`
  to 1e-12 (largest difference below 1e-13 over 92 trades, 2019-03-04 → 2026-10-01) [A35-02]; no rule is re-implemented.
- **TR23** (`vol3_taiex.parquet`): 5,849 returns 2003-01-03 → 2026-10-08 [A35-03], for the windows, the holiday spans,
  the betas' factor and the 2022 illustration.
- **0050 in 2007–2008** (registered, `data/raw/vol6/0050__2007-07-02__2008-12-31.csv` and its distributions,
  registered on 2026-10-24 and approved by the owner on 2026-10-31): the script checks every close against the spread in exact arithmetic,
  the two ex-dates (2007-10-24, 2008-10-24) against `before_price`, and the dates against TR23's, and stops on a
  mismatch. For 2015, LM2's sample (`etf_daily_returns.parquet`, all 82 TR23 dates of the window present) [A35-22].
- **US proxies** (registered, capability B5; DBO approved by the owner on 2026-10-24): `USStockPrice` `adj_close` and
  `close` of SPY, TLT, GLD, USO and DBO, 2007-07-02 → 2026-10-08, and `TaiwanExchangeRate` USD `spot_buy`,
  `spot_sell` (mid; FinMind's −1 rows filtered out at registration): 4,849 US sessions and 4,793 FX rows [A35-24].
  An adjusted close is LM34's $P^{\mathrm{adj}}_{t\mid t'}$ of (34.2), a level divided back by the compounded total
  returns $G_{t,t'}$ (decision B6), here built by FinMind with $t'$ the latest US session it held when the file was retrieved on
  2026-10-24 (`data/README.md`);
  LM35 writes no split ratio. The pairing rule (35.5) is the capability check's: the New York close of a US session
  takes the first FX row dated after that session, and a Taiwan date compounds the US sessions since the previous Taiwan date.
  Of 4,736
  TR23 dates from 2007-07-03, 170 have no new US session, 4,421 one, 94 two and 51 three or more; one date
  (2012-01-02) has its FX row after it [A35-24].
- **T5S** (Volume IV): the raw files of the five named days only, through per-day statistics (log changes from the
  previous close to 09:01:00, to the day's low and to the close; the low's time; for 2025-04-07 also the stale 09:00:05
  open) [A35-45]. The script stops unless each day's 09:00:00 value equals TR23's previous price close (PITFALLS §3).
  Nothing intraday is published.
- **TX23** (`vol4_tx23.parquet`): settlement moves of 9.95% or more since 2015-06-01, TAIEX's price return those days,
  near-month volume, and $F_t$ on 2026-10-08 [A35-44].
- **The checkpoint universe** (`frames("E5+checkpoint")`): E5 plus 0056 (元大高股息), 00662 (富邦NASDAQ) and 00720B
  (元大投資級公司債), the short names of TWSE's ISIN page and TPEx's product page (SOURCES' listing-markets and TPEx rows and its short-names item, read 2026-10-25);
  00720B trades on TPEx, as E5's 00679B does, and the other six funds on TWSE; base 2018-02-01 (00720B's listing);
  estimation $T=2{,}104$ (2018-02-02 → 2026-10-08), $A=242.35$; wealth frame 2,110 sessions, $A_{\mathrm w}= 243.04$;
  79 month-end signals with 504 rows, the first 2020-03-31 (trade 2020-04-01), the last 2026-09-30 (trade 2026-10-01)
  [A35-47]; its years count from the close of 2018-02-01 (decision C7). 00720B tracks the Bloomberg US 20+ Year BBB
  Corporate Bond liquid index (Yuanta's page), 00662 the Nasdaq-100 (TWSE's e添富 fund page, 國外股票ETF, and Fubon's page;
  decision "LM35" of the first revision) and 0056 the FTSE TWSE Taiwan Dividend+ Index (Yuanta's page), all read
  2026-10-24; 0056 and 00720B's labels are the capability check's. The frames show no halt and no split of 00662 or
  the other two through 2026-10-08 (drafter's check of `frames`, confirmed by the recomputation). Since 2025-09-30
  both markets let an issuer apply to suspend an SITC or futures-trust ETF during a foreign closure of five or more
  consecutive business days (TWSE's 受益憑證買賣辦法 Arts. 5-1 and 5-2; TPEx's ETF rules, Arts. 4-2 and 4-3). The fund's NAV
  must then be at most NT\$3 billion, or its premium or discount must have reached 3% on each of the two business days
  before the application. So "no halt" rests on the frames, not on the rules. 00662 has a 5-for-1 split scheduled: no trading 2026-11-11 → 11-16, trading again from 2026-11-17 (TWSE's split
  table, second hunt), after the sample's end, so a re-fetch after mid-November 2026 contains it (watch item, Open
  item 2).
- **Scenario windows** (TR23, the TAIEX total-return index; adopted by the editor's decision D, 2026-10-24): the
  trough is TR23's lowest close of the named calendar year (2008, 2015, 2020) or of the 20 sessions from the named day
  (2024-08-05, 2025-04-07); the peak is TR23's highest close after the previous scenario's trough (for 2008, from
  TR23's first close) and before the trough; the window's worst day is its worst TR23 return; the worst $m$ sessions
  ($m=5,20$) are the worst compound TR23 returns over $m$ consecutive sessions ending in (peak, trough], which may
  start before the peak. A span of $m$ sessions is printed from the close before its first return to the close of its
  last ("from the 2025-03-31 close to 2025-04-09" holds five returns).
- **Replays.** Frozen: the exposures at the window's first close held fixed, $\mathbf f^{\top}\mathbf R^{\mathrm{sc}}$
  with each fund's compound wealth-frame return over (peak, trough], interest on cash and borrowing left out (the text
  says so). Named day: the exposures at the previous close times that day's returns (no rule trades on a named day:
  none is a trade date), also without the session's interest (decision A1). R1–R7 hold no cash, so their wealth fell
  by exactly $\mathbf f^{\top}\mathbf R$ on 2025-04-07; R8's wealth, one session's borrowing interest included, fell
  7.94328%, 0.005 points more than its replay's 7.93853% [A35-13]. Actual: the rule's wealth at the trough ÷ wealth at
  the peak − 1, trades and costs included.
- **Conventions.** Simple returns in percent; T5S statistics are log changes of the TAIEX price index and say so;
  every TAIEX number names its index (TR23 total return; the price index for T5S and the TX comparison; decision C7).
  Years are calendar days ÷ 365.25 from the close before a sample's first return to its last close (decision C7,
  AUTHORING §8); a window's length is given in sessions.
  $\hat\Sigma$ and $\bar{\mathbf R}$ of the full estimation frame, divisor $T$ (`cov0`, `ddof` passed). Betas: OLS slope
  with an intercept on TR23's same-day $R$. Mahalanobis $d=\sqrt{d^2}$ with that mean and $\hat\Sigma$. Ruin leverage
  $-1/R$ for a loss $R<0$. Quantiles `inverted_cdf`. Weekly returns compound the daily ones within ISO weeks, keys
  (ISO year, ISO week), with the span's first and last week dropped, complete or not (LM27's convention; decision D
  and the first revision's "Weeks and months").
  Solver settings as the shared decision "Solver output" (CLARABEL 1e-12, OSQP 1e-10 polished), in percent units,
  which that decision allows with the KKT residuals printed. The objective is given to cvxpy as
  `cp.quad_form(x - Rbar, cp.psd_wrap(Sigma_inv))`, $\hat\Sigma^{-1}$ wrapped as positive semidefinite. In that form
  both solvers report `optimal`, the stationarity residuals (CLARABEL's multipliers) are below 1e-13 and complementary
  slackness below 1e-9, CLARABEL, OSQP and the closed form agree to 1e-9,
  and an inactive constraint's multiplier is below 1e-12 [A35-40]. The statuses and that multiplier depend on the
  form. Given as `cp.sum_squares` of a Cholesky factor of $\hat\Sigma^{-1}$ times $\mathbf x-\bar{\mathbf R}$,
  CLARABEL's inactive multiplier for R8 is about 6e-12, and OSQP's status for R2 can fall to `optimal_inaccurate`
  (in about half of 40 last-bit perturbations of $\hat\Sigma$; `quad_form` gave `optimal` in all 40; two
  verifiers' scratch checks, 2026-10-25 and 2026-10-31, each with its own perturbation scheme). So the text, problem 11 and lab part 6 state the form (decisions C5, X19;
  residuals, gaps and an inactive multiplier print as bounds because their digits are rounding noise).
- **Guard and exact checks.** Counts against a threshold use the guard 1e-12; 0050's −10% on 2025-04-07 is exactly
  $-1/10$ by `Fraction` on the two-decimal closes [A35-12]; the lock days are those with open = high = low = close
  [A35-46].
- **Rounding.** Every printed value passes through `f(x, digits…)`, which flags values within a tenth of a last-digit
  unit of a rounding boundary ("NEAR") at each precision the brief prints. The flags stay in the anchors table, whose
  "Printed as" column also lists the flagged values of X3's eight-rule table and X4's bars; the text prints every
  value rounded from its unrounded one, without a mark (decision C11), and `data/lm35_numbers.py` does the same. A
  number computed from an adjusted close is also flagged "CENT" when a change of one cent in each adjusted close
  could move its first decimal: it prints to 0 dp, or with "about" when 0 dp is not safe either (PITFALLS §3,
  "Back-adjusted prices change at every retrieval"), and it is checked for NEAR at 0 dp only. The largest such effect
  on a proxy return is 0.17 points in the 2020–2025 windows and 0.22 points on 2015-08-24 [A35-26, A35-30]. The
  registered files are byte-identical to the drafter's copies (recomputation, `cmp` on all eight), so every proxy
  value stands; a later re-fetch re-rounds the adjusted closes, and the CENT flags are re-read then. A derived result
  follows from the inputs printed beside it, or the text says it comes from unrounded values.
- **Seeds.** None: LM35 simulates nothing, and its widget draws nothing.
- **Published files** (Stage 2). No file carries a daily series in date order: X2–X4 and X6 are per-scenario or
  per-fund bars, X7 straight lines from (35.2), X5 and X8 tables of per-day statistics. The widget embeds
  $\bar{\mathbf R}$, $\hat\Sigma$ and $\hat\Sigma^{-1}$ (5×5), the eight current books, the preset shock vectors and the 2,362
  historical distances sorted, without dates (about 30 KB) [A35-37].
- **Scripts.** `data/lm35_numbers.py` (every printed value, asserted against `src/lm35.md`, compared with the anchors,
  flags NEAR and CENT), `data/lm35_charts.py` (X2–X4, X6, X7 and the widget block); after `data/vol3_series.py`,
  `data/vol4_series.py`, `data/build_series.py`, `data/vol5_series.py` and `data/vol5_rules.py`. The checkpoint's
  reference answers (Lab 9) come from `data/lm35_numbers.py` with `vol5_rules`' functions on the checkpoint frames.

**Hygiene declaration.** *Descriptive:* the five windows on TR23 and the holiday spans; the frozen, named-day and
actual replays of the rules' own books (the books come from rules fixed in advance on 2026-10-24, so they are the
through case's out-of-sample holdings; the replay estimates nothing); limit days, locks, TX volumes and the T5S
per-day statistics; the 2022 illustration. *In-sample:* the betas, $\bar{\mathbf R}$ and $\hat\Sigma$ of the full
estimation frame (they include the scenario days), the historical distances, the partial scenario, the reverse stress
tests and the (16.10) check. *Hypothetical:* 2008 and 2015 on the rules' first weights with 0050 and proxies, and
the 2020 check of that replay (0050 itself with the proxies against the funds): the replays that combine data sources
within one number, by construction, each source named (the shared decision "Data"'s one exception, decisions X27,
C4); the factor shock; the
correlation break (a *constructed* correlation of 0.30); the worst-of-each day (*constructed*); the TX position at the
2026 margins; the widget's presets applied to the current books; every problem's inputs. *Out-of-sample* (lab part 9): the checkpoint's comparison of R1, R3, R6 and R8 on the
eight-fund universe, trading from 2020-04-01, with settings fixed by decision D before any result; $n=4$. No
probability is attached
to any scenario. Count: the eight through-case rules ($n=8$, none selected or ranked by a scenario), five named
scenarios, one illustration, four hand-built shocks and one reverse stress test per book; the reverse stress test
searches over shocks, not over rules. Local note, in two text blocks (each a paragraph of at most 80 words, AUTHORING
§1): "Stress tests here are replays and constructions, not forecasts. The rules' books come from the through case,
fixed on 24 October 2026; replaying them on past windows estimates nothing." / "Betas, distances and the reverse
stress test use the full sample's mean and covariance, which include the scenario days, so they are in-sample. 2008
and 2015 are hypothetical: US proxies stand in for the four foreign funds, and the books are the rules' first weights.
Of those funds only 00635U traded in 2015 (from 15 April); GLD stands in for it too, as in 2008. No scenario carries
a probability, and no rule
is chosen by its scenario losses."

**Notation.** AUTHORING §6 with the Portfolios table. Used: $R$, $r$ (T5S log changes), $R_{i,t}$, $R_{p,t}$ ((27.1), the checkpoint's book return), $\mathbf R_t$, $T$,
$t$, $A$, $A_{\mathrm w}$, $N=5$, $i$, $j$ (funds), $m$ (sessions in a window, 5 or 20), $\mathbf f$, $f_i$, $L$
(total exposure $\mathbf 1^{\top}\mathbf f$; a unit book scaled by $L$ has total exposure $L$), $W$, $W_0$,
$\mathrm{DD}_t$ (LM1's), $\mathrm{DD}^0_t$ and $\mathrm{MDD}$ (LM32's, cited), $\bar{\mathbf R}$, $\hat\Sigma$,
$\hat\Sigma^{-1}$, $\Sigma$, $\boldsymbol\mu$ (in the derivations), $\sigma_{ij}$, $\sigma_{ii}$ and $\mu_i$, $\mu_j$,
the entries of $\Sigma$ and $\boldsymbol\mu$ ($\sigma_{ii}$ a variance, not a squared $\sigma_i$; as lm10.md:50
declares $\hat\sigma_{ij}$ and $\hat\sigma_{ii}=s_i^2$), in (35.3) and §5's Deep Dive, $s_p$, $\sigma_p$, $\rho$,
$\hat\rho$, $C$ (a correlation matrix, §5), $\lambda_N$ (its smallest eigenvalue), $\beta_i$ (a fund's market beta on
TR23, (23.1)), $\beta_{i,p}$ (LM27's, in problem 7), $d^2$ (§6's) and $d=\sqrt{d^2}$, $k$ (a number of standard
deviations: the bound $d\le k$), $\mathbf R^{\mathrm{sc}}$ and $R^{\mathrm{sc}}_i$, $\mathbf x$ and $x_{0050}$ (a shock vector and its 0050
entry, §6), $x$ (the value fixed in (35.3)), $\E$, $\Var$, $\Cov$, $\mathcal
N$, $F_t$ (TX's settlement price), $P_t$, $r_f$, $\lambda$ and $\nu$ (the multipliers of §6's Deep Dive, LM7's signs),
$K$ and $\mathbf b$ (the two active constraints of the bounded problem, as LM28–LM29 write them; AUTHORING §6's row
now scopes them to LM28, LM29 and LM35, Y10), $\mathrm{TO}_t$ and $\mathbf w^{\mathrm{drift}}_t$ (the checkpoint's
turnover limit, §6's Portfolios rows). Local symbols, declared in the notation note:

| Symbol | Meaning | Check |
|:--|:--|:--|
| $R^{\mathrm{sc}}_p$ | a book's scenario return $\mathbf f^{\top}\mathbf R^{\mathrm{sc}}$ | subscript $p$ as $\sigma_p$; §6's $\mathbf R^{\mathrm{sc}}$ row |
| $\mathbf R^{\mathrm{sc}*}$, $d^*$ | the reverse stress shock and its distance | a star marks an optimum (§6) |
| $\ell$ | the loss a reverse stress test must reach (10% in the text) | §6's $B,\ell$ row now scopes LM35's $\ell$ as this loss level (decision B3); LM35 writes no block length, lag or likelihood |
| $L_{\mathrm{ruin}}$ | $-1/R^{\mathrm{sc}}_p$, the total exposure at which a scenario ruins a book | subscripted $L$, the same quantity as §6's $L$ (decision B5) |
| $\mathrm{FX}_t$ | the USD/TWD mid rate attached to a US close by (35.5) | upright, as TO, MRC; $X$ stays free (no data matrix is written), $S_t$ stays the TAIEX close (decision B5) |
| $P^{\mathrm{adj}}_{t\mid t'}$, $P^{\mathrm{TWD}}_t$ | a US fund's adjusted close for session $t$ as built on date $t'$, LM34's (34.2), here $t'$ is the latest session FinMind held at the retrieval of 2026-10-24; its value in New Taiwan dollars | LM34's symbol with its build date; (34.2) compounds total returns, with no split-ratio symbol (decision B6) |
| $t^{\mathrm{US}}$ | the last US session before Taiwan date $t$ | $D$ stays a dividend (decision B5) |
| $S_t(\text{09:01:00})$ | TAIEX's value at 09:01:00 on day $t$ (per-day statistics only) | §6's $S_t$ with a time |

Not used: $\mathbf h$ (LM35 writes exposures; the shared table says so), $V$ for a value, $D$ for a date, $g$ for a gap
(it is the log growth rate), a split ratio as a symbol (decision B6), a probability for any scenario, $\Pr$ or
$\chi^2$ with a distance, $\kappa$, $\alpha$.

**Motivating case: "Five days, one session"** (box in three paragraphs of 70, 65 and 47 words, 182 in all, without
the anchor tags; 13 sentences, the longest 21 words, average 14.0; decision C10, the cross-check's Y5)

> After its close on 2 April 2025, Taiwan's market did not trade again until 7 April. That session the TAIEX total-return
> index (TR23) fell 9.70%, its worst day since 2003 (lm26.md:32). Its five sessions to 9 April lost 15.96%, second
> only to March 2020's 16.51% [A35-58]. 0050 traded at one price all day, 158.40, exactly 10% below its last close
> [A35-12]. Its 29.6 million units changed hands at that price, none lower [A35-12].
>
> 00646 and 00642U have no daily limit, and they fell 12.59% and 14.62% [A35-11]. The through case's eight rules lost
> from 5.06% (R7) to 8.33% (R4) of wealth [A35-13]. R8 had raised its exposure to 1.319 at its trade of 3 March, and it
> lost 7.94% [A35-42, A35-13]. A beta model fitted on 2,362 days, that day included, gives R1 a loss of 3.62%,
> under half the actual 7.70% [A35-01, A35-32].
>
> Three questions follow. What did each rule lose in the four other scenarios that this module replays? Which shock,
> not seen yet, would cost a rule a tenth of its wealth? And what would a book of 0050 levered five times have lost at
> the next open?

The box's day is the extreme of TR23's 5,849 daily returns (rank 1 [A35-08]; lm26.md:32 calls it TR23's largest
fall), and its multi-day figure (AUTHORING §8) is the window's worst five sessions, rank 2 of TR23's 5,845 overlapping
five-session spans, behind only 2020's span ending 2020-03-19 [A35-58]. The draft's claim that the day was also the
extreme of a multi-day measure was false and is dropped (decision LM35; first recomputation, finding 4): its
20-session loss ranks 8th of 5,830 spans [A35-58].

Resolved: (a) §2–§4, X2, X3: the five windows and the rules' losses in each, with 2008 and 2015 hypothetical; (b) §6,
E8, X6: R8's current book reaches a 10% loss at $d^*=12.27$, below 2025-04-07's own distance of 12.94 [A35-39,
A35-37]; (c) §7–§8, E9: a fivefold book of 0050 loses 50.00% at the locked close and 70.45% at the next open, 151.20
[A35-52]; its ruin leverage at the next open is $L_{\mathrm{ruin}}=7.10$ [A35-43].

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | the layer added (LM32 measures losses as statistics of a distribution; LM35 asks what named and constructed shocks do to the same books, with no probability); case + X1; roadmap; notation and hygiene notes | 340 |
| 2 | Scenarios from History {1,6} | a scenario as a return vector, $W_0\mathbf f^{\top}\mathbf R^{\mathrm{sc}}$ by (8.4); the window rule (peak, trough, worst day, worst $m$ sessions); X2; E1 (2025's window against LM1's running peak); holiday spans (A35-10; 2020-01-30 after the Lunar New Year closure, TWSE's 2020 schedule); pitfall: a "one-day" return can span ten calendar days; 導讀 (壓力測試, 情境分析, 歷史情境); KC | 510 |
| 3 | Replaying the Rules {1} | frozen replay (35.1) and attribution; named-day replay; the actual path; X3, X4; E2 (R1 on 2025-04-07); E3 (R8: frozen against actual; the 3 March trade raised the book, A35-42); interest left out, said once (R8's 0.005 points [A35-13], decision A1); pitfall: a frozen book ignores the rule's own trades; KC | 540 |
| 4 | Funds That Did Not Exist {2} | the pairing rule (35.5), the 13:30 close against New York's (shared decision "Timing of E5"); 0050 itself in 2008; E4 (2008 at the first weights); E5 (proxies checked in 2020; USO against DBO; the US-holiday blind spot); pitfall: a proxy's error is part of the scenario; 導讀 (代理資產, 匯率); KC | 520 |
| 5 | Hypothetical Shocks {3} | factor shock through betas (23.1), said once to be in-sample OLS estimates printed without standard errors, since the factor shock is a construction whose error on 2025-04-07 is the model's (E6), not sampling error; E6 (the beta model on 2025-04-07; the partial scenario (35.3) from (16.8), the most plausible choice for an elliptical law whose density falls with $d$, by Breuer et al.'s Proposition 1); correlation break with a PSD check; E7 (the break; 2022, when 0050 and 00679B fell together; (16.10) on 0050's 48 worst days); 導讀 (因子模型, 條件期望值); KC | 560 |
| 6 | Reverse Stress Testing {4,7} | the problem; derivation by LM28's Lagrangian; (35.4); the worst loss within $d\le k$, Breuer et al.'s worst loss over a Mahalanobis ellipsoid (§2.3); the distance as a ranking, not (16.9): the sample's distances (A35-37), the largest an oil gain; E8 (each book's mean and $s_p$; R1, R2, R4, R5, R8; the bounded version for R2, cvxpy and KKT); X6; Deep Dive (the bounded problem's feasible set, a non-empty polyhedron, its strictly convex objective and single minimizer; KKT and the closed form with both constraints active, $K$ of full row rank); one sentence: the reverse stress shocks and distances are plug-in estimates from $\bar{\mathbf R}$ and $\hat\Sigma$, whose sampling error this module does not measure; pitfall: the closest shock may break a price limit; Python block; 導讀 (反向壓力測試, Mahalanobis 距離); KC | 590 |
| 7 | Limits, Locks and Overnight Gaps {5,6} | the rules by market: TWSE's 受益憑證買賣辦法 Art. 8 (unchanged for these funds since 2016-06-03) gives 0050 and 0056 the 10% limit and 00646, 00662, 00635U and 00642U none; TPEx's ETF rules, Art. 7 ¶1 item 一 (the 成分證券 text since 2017-03-01; TPEx's listing notices give both funds no limit from their first day), give 00679B and 00720B none, so the rules cover E5's span; 00720B's −11.25% of 2020-03-19 (A35-48) fits; X8; a lock: sales only at the limit, none below (0050's OHLC); the next open; T5S's gap, low and close (X5); the stale 09:00:05 open; E9 (0050 and 00631L; TX's volume on limit days); pitfall: the daily open is not the opening price level; 導讀 (漲跌幅限制, 鎖跌停, 跳空, 隔夜); KC | 495 |
| 8 | Leverage, Ruin and Margin {5,8} | (35.2), ruin reported, never floored ((27.1)'s rule); X7 (R6's book scaled by $L$; R8's cap 1.5 and its largest uncapped ratio, 2.14 [A31-29]; the ruin line in place of replays at higher caps, decision E); E10 (TX at TAIFEX's 2026 margins: $f=14.08$, the margin call after 1.65%, equity below zero on a limit day [A35-44]); funding as a failure distinct from ruin; 導讀 (槓桿, 權益歸零 for ruin, 保證金追繳); KC | 440 |
| 9 | What a Stress Test Cannot Say {7,8} | no probability (ROADMAP's Stress row); BCBS (2018): scenarios "severe but plausible" (Principle 4, p. 6), and reverse stress tests that look for the scenarios that could make a bank fail (p. 6); Breuer et al. (2009): plausibility by a Mahalanobis distance (§2.1, p. 209) and the worst loss within it (§2.3, p. 211), which §6 computes; the four failure forms on the same rules (table citing LM34's A34-04 and LM32's A32-35); the closing pitfall: surviving the scenarios does not cover unseen losses; the lab box and the checkpoint; KC | 400 |
| — | Summary (8) / Problems (12) / Solutions | | 150 / 400 / 545 |
| | **Total** | | **5,490** |

**Elements.** 10 examples (E1 §2; E2, E3 §3; E4, E5 §4; E6, E7 §5; E8 §6; E9 §7; E10 §8). Knowledge checks:

- §2: TR23's worst day of 2020's window, 2020-01-30 (−5.75%, rank 8 of 5,849), came ten calendar days after the
  previous session, 2020-01-20 [A35-06], across the Lunar New Year closure of 21–29 January (TWSE's 2020 schedule): is
  it one day of news? Returns that span four or more calendar days are 140 of 5,849 (2.4%), and their mean absolute
  size is 1.39% against 0.83% for the rest [A35-10].
- §3: R8's 2025 window frozen at 2025-02-21 lost 10.15% [A35-19], but its own path lost 13.84% [A35-21]. Why? Its trade
  of 3 March raised its exposure from 1.005 to 1.319, and that book frozen over the whole window would have lost 13.35%
  [A35-42]. The trade of 1 April took it only to 1.33 [A31-32].
- §4: on 2008-01-22 every proxy returns exactly 0 [A35-28]. Why? No US session lies between the Taiwan dates
  2008-01-21 and 2008-01-22, so both carry the same New York close and FX row. E5's estimation frame has 80 such dates, on which 00646
  still moved 0.43% on average, against 0.67% on dates with one US session [A35-57].
- §5: under the correlation break R4's loss stays 6.89% [A35-33]. Why? R4's current book holds no 00679B (0.000)
  [A35-38].
- §6: R4's $d^*=9.91$ lies below 2025-04-07's 12.94 [A35-39, A35-37]. What does that say? A shock less unusual than a
  day already in the sample reaches a 10% loss; within $d\le12.937$, that day's distance, R4's worst loss is
  $12.937\times1.0174\%-0.078\%=13.08\%$ (E8's $s_p$ and mean) [A35-39]. Neither number is a probability: (16.9) and
  LM16's law behind it hold only for normal returns, and these returns are not normal.
- §7: (a) TX's near month traded 2,736 contracts on 2025-04-07, against 211,207 on 2024-08-05 and 152,423 on 2025-04-08
  [A35-44]. What does the volume say about selling at the limit? (b) On that day 00646 fell 12.59% while 0050 stopped
  at −10.00% [A35-11]: which rule of which market allows each, and what did the TAIEX price index show by 09:01:00?
  TWSE's Art. 8 ¶1 item 1 leaves 00646, an index ETF with foreign constituents, without a limit; 0050 takes the
  listed-stock limit. The log change to 09:01:00 was −10.28%, against −5.52% at the stale 09:00:05 open [A35-45].
- §8: R6's book survives every replay of 2020–2025 at any $L$ below its smallest ruin leverage, $1/0.13036=7.671$
  (2020's window, a loss of 13.036% a unit) [A35-41]. Does $L=5$ make it safe? No: the replays are a few past paths;
  the worst-of-each day already costs its current book 11.11% at $L=1$ [A35-36], five times that at $L=5$, and a gap
  leaves no chance to cut the exposure first. A margin call or a financing limit can end the book long before ruin
  (E10).
- §9: name two losses the replay set cannot show: a shock beyond the sample's largest distance (the worst-of-each day
  sits at 19.07 against 15.02 [A35-36, A35-37]); a lock that blocks the exit (§7).

中文導讀 in §2 (壓力測試 (stress testing), 情境分析 (scenario analysis), 歷史情境 (historical scenario)), §4 (代理資產 (proxy), 匯率
(exchange rate)), §5 (因子模型 (factor model), 條件期望值 (conditional expectation)), §6 (反向壓力測試 (reverse stress test),
Mahalanobis 距離 (Mahalanobis distance)), §7 (漲跌幅限制 (price limit), 鎖跌停 (limit-down lock), 跳空 (gap), 隔夜 (overnight)), §8
(槓桿 (leverage), 權益歸零 (ruin: zero equity), 保證金追繳 (margin call)). Deep Dives: §6 "The bounded reverse stress test": its
feasible set $\{\mathbf x:\mathbf f^{\top}\mathbf x\le-10\%,\ x_{0050}\ge-10\%\}$ is a non-empty polyhedron, since every
book holds a fund besides 0050. The objective $d^2$ is strictly convex and grows without bound, so exactly one minimizer
exists. The constraints are linear, so (29.4)'s conditions are necessary and sufficient. With
both constraints active, $K\mathbf R=\mathbf b$ ($K$'s rows are $\mathbf f^{\top}$ and $(1,0,0,0,0)$, written out, of
full row rank because $\mathbf f$ is not a multiple of $(1,0,0,0,0)$),
the minimizer is $\bar{\mathbf R}+\hat\Sigma K^{\top}(K\hat\Sigma K^{\top})^{-1}(\mathbf b-K\bar{\mathbf R})$ ((28.1)
with $\hat\Sigma^{-1}$ in place of $\Sigma$ and the shock measured from $\bar{\mathbf R}$), and KKT sufficiency (29.4)
makes it the answer when both multipliers are non-negative (R1: 37.3 and 0.8877 in percent units [A35-40]). §5
"Conditional means without normality": the value $\mu_j+(\sigma_{ij}/\sigma_{ii})(x-\mu_i)$ is the best linear
predictor of $R_j$ from $R_i$ for any law with finite variances (LM23's slope). Normality makes it the conditional
mean ((16.8)). For an elliptical law whose density falls with the Mahalanobis distance $d$, these conditional values
give the most plausible scenario that fixes the stressed fund. That is Breuer et al.'s Proposition 1 (2009, §2.2, p.
210); the alternatives they compare are Kupiec's (1998), as they describe them.

**Exhibits.**

- X1 `case` (table, §1): 2025-04-07, E5's wealth frame. Rows: the five funds. Columns: daily limit (10% / none, §7's
  rules: TWSE's for four funds, TPEx's for 00679B); the day's return from the 2025-04-02 close: 0050 −10.00%, 00646
  −12.59%, 00679B +1.81%, 00635U −3.10%, 00642U −14.62% [A35-11]; beta on TR23 (estimation frame): 1.048, 0.527,
  −0.071, 0.161, 0.198 [A35-31]; beta × TR23's −9.70% (lm26.md:32): −10.17, −5.11, +0.69, −1.56, −1.92 [A35-32]. Note
  row: the rules' losses R1 −7.70% … R8 −7.94% (R8 at exposure 1.331) [A35-13]; R1's beta-model loss −3.62% [A35-32].
  Note: TR23 is the TAIEX total-return index; the betas are in-sample; the day's returns span five calendar days;
  interest is left out (R8's wealth, with a session's borrowing interest, fell 0.005 points more). Source: FinMind
  `TaiwanStockPrice`, `TaiwanStockDividendResult`, `TaiwanStockSplitPrice`, `TaiwanStockTotalReturnIndex`, retrieval
  dates as registered in `data/raw_manifest.json` (`data/vol5_series.py`, `data/vol3_series.py`); Computations:
  `data/lm35_numbers.py`.
- X2 `windows` (`bar`, §2): categories the five scenarios; four series "worst day", "worst 5 sessions", "worst 20
  sessions", "peak to trough" (`fmt: "pct2"`, the precision of the values printed here; at `pct1` five of them would
  sit near a boundary, first recomputation finding 10 and second recomputation minor 1): 2008 −6.51, −12.55, −27.69,
  −56.02 [A35-04]; 2015 −4.82, −9.72, −12.49, −23.18 [A35-05]; 2020 −5.75, −16.51, −25.99, −28.55 [A35-06];
  2024-08-05 −8.33, −10.44, −15.14, −18.31 [A35-07]; 2025-04-07 −9.70 (lm26.md:32), −15.96, −22.38, −26.54 [A35-08].
  Note: TR23, the TAIEX total-return index; each window's dates in the note (peak → trough: 2007-10-29 → 2008-11-20,
  265 sessions; …), each span of $m$ sessions from the close before its first return; TWSE's stock limit was 7% until
  2015-06-01 (SOURCES, "TWSE company history"); the 2024-08-05 window's worst 20 sessions start before its peak (from
  the 2024-07-04 close); each worst day's rank among TR23's 5,849 daily returns (1 = worst): 2008-01-22 4, 2015-08-24
  17, 2020-01-30 8, 2024-08-05 2, 2025-04-07 1 [A35-04 to A35-08].
- X3 `replay` (`bar`, §3): categories the three scenarios on the rules' own books (2020, 2024-08-05, 2025-04-07,
  *Descriptive*); series R1, R3, R6, R8 (`fmt: "pct2"`): frozen window losses. 2020: −19.84, −10.17, −13.04, −17.04
  [A35-15]; 2024: −5.84, +0.11, −3.25, −3.61 [A35-17]; 2025: −12.97, −8.03, −10.10, −10.15 [A35-19]. A table under the
  chart gives all eight rules in the three scenarios on their own books, the actual paths and the named-day losses beside the frozen
  losses [A35-15 to A35-21; the anchors' "Printed as" column lists the table's flagged values, rounded from their
  unrounded ones], and 2008 and 2015 as a separate block labelled *hypothetical* (R1, R3, R6 and R8, frozen window
  losses only, since no actual path exists; first weights, 0050 itself, oil by USO), each value at the digits that a cent in the adjusted closes leaves safe (A35-27's and A35-29's flags): 2008 R1
  −24.5, R3 −9, R6 −15, R8 −12 [A35-27]; 2015 R1 −7.2, R3 +1.8, R6 −2.1, R8 −1.8 [A35-29]. (The hypothetical values
  stay out of the bars: one series format cannot show 0 dp beside 2 dp, and the two labels differ.) Note: frozen at
  each rule's book at the window's first close; interest left out; in 2015 GLD stands in for 00635U, although that
  fund traded from 2015-04-15.
- X4 `attrib` (`bar`, `stack: true`, approved C1, §3): categories R1, R3, R6, R8; five series: 0050, 00646, 00635U,
  00642U in colours 1–4 and 00679B in `"var(--muted)"`, named in the caption (the only fund that gained); values
  $f_iR_i$ on 2025-04-07 [A35-14]; the category total is the rule's loss [A35-13]. Note: R6's parts rounded to two
  decimals (−1.35, −2.73, +0.56, −0.68, −1.75) add to −5.95, not its −5.96 (A35-14 against A35-13), so the note gives
  R6's parts to three decimals, −1.351, −2.733, +0.556, −0.684, −1.752, which add to its −5.964 (pitfall below); R1's,
  R3's and R8's two-decimal parts add to their totals.
- X5 `gaps` (table, §7): the five named days. Columns: log change of the TAIEX price index from the previous close to
  09:01:00; to the day's low and its first time; to the close; gap ÷ close, computed from the unrounded log changes.
  Values: 2008-01-22 −6.56%, −6.94% at 12:50:00, −6.74%, 0.97; 2015-08-24 −1.66%, −7.79% at 10:25:45, −4.96%, 0.34;
  2020-01-30 −3.48%, −5.95% first at 13:25:00 and unchanged through 13:29:55, the closing call auction (AUTHORING §8),
  −5.92%, 0.59; 2024-08-05 −5.07%, −8.96% at 13:03:10, −8.72%, 0.58; 2025-04-07 −10.28%, −10.31% at 09:00:20, −10.20%,
  1.01 [A35-45]. Note row: 2025-04-07's daily open (09:00:05) gives −5.52% [A35-45] (PITFALLS §3). Note: per-day
  statistics of TAIEX's 5-second values (FinMind `TaiwanVariousIndicators5Seconds`, TWSE), log changes; the ratio
  column comes from the unrounded changes (2015-08-24's printed −1.66 ÷ −4.96 would give 0.33, the unrounded ratio
  0.34; second recomputation, finding 5), and the note says so; a tied low is given at its first time; no intraday
  path is published.
- X6 `reverse` (`bar`, §6): categories the five funds; series "R1" (closed form) −10.47, −8.79, −1.21, −6.12, −23.00;
  "R8" −8.90, −7.65, −4.57, −6.75, −14.14 [A35-39]; "R2, 0050 ≥ −10%" −10.00, −10.81, −9.89, −8.67, −0.34 [A35-40];
  "each fund's worst day" −10.00, −12.59, −7.15, −11.09, −22.20 [A35-36]. Note: shocks of least Mahalanobis distance
  reaching a one-day loss of 10% for each rule's book at the 2026-10-08 close; full-sample mean and covariance
  (in-sample); distances 13.52, 12.27 and 17.01 against 19.07 for the worst-of-each day [A35-39, A35-40, A35-36]; a
  distance, not a probability.
- X7 `ruin` (`line`, §8): $x$ the total exposure $L$ from 0 to 20; $y$ wealth after the scenario, $1+LR^{\mathrm{sc}}_p$
  (`fmt: "pct0"`), four series: R6's 2020 window (−13.04% a unit), R6's 2025 window (−10.10%), R6 on 2025-04-07
  (−5.964%, to three decimals so that its crossing follows) [A35-41], and 0050 to the next open of 2025-04-08
  (−14.09%) [A35-43]; `hline` at 0, labelled "ruin", which the caption and the §8 box give as 權益歸零 (decision
  "Chinese terms"), never 破產; dashed `vline`s at R8's cap 1.5 and its largest uncapped ratio, 2.14 [A31-29].
  Values cited: the ruin leverages 7.67, 9.90, 16.77 and 7.10,
  where each line crosses zero [A35-41, A35-43]. Note: frozen books, no trades inside the scenario; a book rebalanced
  to constant leverage daily would differ. (In place of the spine's replays at higher caps: the cap bound at no window
  start, decision E.)
- X8 `limits` (table, §7): E5's funds. Columns: the market, the limit and its clause (TWSE's 受益憑證買賣辦法 Art. 8
  for 0050, 00646, 00635U and 00642U; TPEx's ETF rules, Art. 7 ¶1 item 一, for 00679B); the wealth frame's
  lowest and highest return; days beyond ±10%: 0050 −10.00 / +10.00, 0; 00646 −12.59 / +10.39, 2; 00679B −7.15 /
  +8.57, 0; 00635U −11.09 / +7.74, 1; 00642U −22.20 / +33.10, 14 [A35-46]. Note row: 0050 locked (open = high = low =
  close) on 2025-04-07 and 2025-04-10 [A35-46]; the checkpoint's 0056 locked at 31.66 on 2025-04-07, and its
  00720B, on TPEx without a limit, closed −11.25% on 2020-03-19, from 40.00 to 35.50 [A35-48].

**Widget `scenarioBuilder` — "Build a shock, see the loss."** `Book.controls`: rule (select R1–R8); preset (select:
2025-04-07, 2020 window, 2024 window, 2025 window, factor −10%, correlation break, worst of each, the rule's reverse
stress shock, custom); five shock sliders (−50% to +50%, step 0.1%, wide enough for every preset: 2020's window has 00642U at
−46.42% [A35-15]); total exposure $L$ (0 to 20, step 0.1). Bars:
each fund's $Lf_iR^{\mathrm{sc}}_i$ (stacked, approved C1) and the total. Readouts: the loss $L\,\mathbf f^{\top}
\mathbf R^{\mathrm{sc}}$, wealth after it (ruin flagged at $\le0$, never floored), $L_{\mathrm{ruin}}$, the
Mahalanobis distance $d$ of the shock and how many of the 2,362 historical days lie farther (a count, not a
probability) [A35-37], for the one-day presets and custom shocks only; for the three window presets the readout says
"a window, not a day: no daily distance". The reverse stress preset is (35.4) in closed form for the selected book (module-local code
under 30 lines, a 5×5 product with the embedded $\hat\Sigma$, tested against Python as `data/lm15_charts.py` does).
Initial state (PDF): R1's current book under the 2025-04-07 returns at $L=1$: loss 7.78%, $L_{\mathrm{ruin}}=12.85$
(two decimals, so that $1/0.0778$ gives it), $d=12.94$ [A35-49]. Data block `chart-lm35-scenarioBuilder`: the eight
books at 2026-10-08 [A35-38], the presets' vectors, $\bar{\mathbf R}$, $\hat\Sigma$, $\hat\Sigma^{-1}$ and the
sorted distances (about 30 KB), computed by `data/lm35_charts.py`. No optimizer and no simulation (shared decision
"Widgets").

**Examples** (results recomputed from the printed inputs):

- E1 §2 `window25`, the 2025 window: peak 2025-02-21, trough 2025-04-09, 30 sessions, −26.54%; worst day 2025-04-07,
  −9.70% (lm26.md:32), rank 1, five calendar days after 2025-04-02; worst 5 sessions from the 2025-03-31 close to
  04-09 (the returns of 04-01, 04-02, 04-07, 04-08 and 04-09), −15.96%; worst 20 from the 2025-03-10 close to 04-09,
  −22.38% [A35-08]. Among all 5,845 overlapping five-session spans of TR23, only the one ending 2020-03-19 lost more
  [A35-58]. LM1's running peak tells another story: TR23 stood 27.72% below its peak of 2024-07-11 on 2025-04-09, 176
  sessions later, and 18.31% below it on 2024-08-05 [A35-09]; the window rule keeps the two scenarios apart. Holiday
  spans: 140 of 5,849 returns cover four or more calendar days, and two of the ten worst days are among them,
  2025-04-07 (five days) and 2020-01-30 (ten, across the Lunar New Year closure of 21–29 January, TWSE's 2020
  schedule) [A35-10].
- E2 §3 `day25`, R1 on 2025-04-07: exposures at the 2025-04-02 close times the day's returns give −7.70% [A35-13], of
  which 0050 −2.00, 00646 −2.53, 00679B +0.36, 00635U −0.62 and 00642U −2.91 points [A35-14] (they add to −7.70 as
  printed); 00646 and 00642U supply the two largest parts. R3, the long-only minimum-variance book, loses 5.40%, 4.07
  points of it from 00646 [A35-13, A35-14]. Equal weights are not equal risk on a crash day. The replay leaves out the
  session's interest; R1 holds no cash, so its wealth fell by exactly this [A35-13].
- E3 §3 `frozen`, frozen against actual: 2020's window (2020-01-14 → 03-19) frozen at the first close costs R1 19.84%,
  R6 13.04% and R8 17.04% [A35-15]; their own paths lost 21.44%, 14.43% and 12.58% [A35-21]. R8 entered at exposure
  1.307 [A35-15], and its trades of 3 February and 2 March cut it to 0.991 [A35-42] and 0.884 [A31-33]; frozen over
  the whole window, those books lose 13.20% and 11.68% [A35-42]. In 2025 the order reverses: frozen at 2025-02-21 R8
  loses 10.15% at exposure 1.005 [A35-19], its path 13.84% [A35-21]. Its trade of 3 March raised the exposure from
  1.005 to 1.319, and that book frozen over the whole window loses 13.35% [A35-42]. The trade of 1 April took it only
  to 1.33 [A31-32], and that book loses 13.42% over the window [A35-42]. So the 3 March trade did the raising, and
  the cap of 1.5 bound at neither. R8
  scales by its two-year volatility over its EWMA forecast, so a ratio of 1.319 at the signal of 27 February means the
  forecast lay below the two-year figure (31.7). The named day of 2020, 2020-01-30, cost R1 1.60% but gave R3 +0.91%,
  as 00679B rose 5.26% [A35-16].
- E4 §4 `y2008`, 2008 at the rules' first weights (*hypothetical*): over 2007-10-29 → 2008-11-20 0050 itself lost
  55.66% (TR23 56.02%); in New Taiwan dollars SPY −44%, TLT +19% and DBO −27% (whole percent, since a cent in the
  adjusted closes could move the first decimal), GLD −4.1% and USO −37.3%;
  USD/TWD rose from 32.390 to 33.390 (+3.09%) [A35-27]. R1 at its first weights [A35-23] loses 24.5% with USO and 22%
  with DBO; R2 (no oil) 25.9%; R3 9% [A35-27]. The oil proxy alone moves R1 by about two points (from the unrounded
  losses, A35-27). On 2008-01-22, TR23's worst day of the window [A35-04], 0050 fell 6.93% and every proxy returned
  0, since the data hold no US session on 21 January [A35-28]; R2 loses 2.8% that day.
- E5 §4 `proxycheck`, the proxies where the funds exist (*hypothetical* in the replay line): daily correlations with
  their funds on the estimation frame 0.705 (SPY), 0.783 (TLT), 0.745 (GLD), 0.655 (USO), 0.696 (DBO), and 0.944,
  0.952, 0.926, 0.845, 0.894 over its 500 ISO weeks, the first and last dropped [A35-25]; the daily figures are lower
  because the funds close at 13:30 Taipei time, hours after the New York close they are paired with (shared decision
  "Timing of E5"). Over 2020's window 00642U lost 46.42%, USO 60.7% and DBO about 46% [A35-26]. USCF states USO's
  roll (the near-month contract, moved to the next over five days each month); Invesco's page names DBO's index, the
  DBIQ Optimum Yield Crude Oil Index Excess Return, but states no roll rule, so the text compares the two oil proxies
  by their data only. Replayed on 0050 itself and the proxies, as 2008 is, R1 loses 21.5% with USO and 19% with DBO,
  against 19.84% on the funds [A35-26]: a proxy's error is part of a hypothetical scenario. On the 80 dates of E5's estimation frame without
  a new US session the proxies cannot move at all [A35-57].
- E6 §5 `factor`, the beta model on 2025-04-07: betas on TR23 of 1.048 for 0050 (R-squared 0.924) and 0.527 for 00646
  (0.363); the other three lie near zero, 00679B −0.071, 00635U 0.161 and 00642U 0.198 [A35-31]. Times TR23's −9.70%
  (lm26.md:32) they give 00646 −5.11% against −12.59% actual, 00642U −1.92% against −14.62%, and R1 −3.62% against
  −7.70% [A35-32]. A factor shock of −10% on the current books costs R1 3.77% and R4 7.28%, from the unrounded betas and books [A35-31]. Partial scenario
  (35.3): with 0050 at −10% and the other funds at their conditional means, 00646 −4.79%, 00679B +0.71%, 00635U
  −1.46%, 00642U −1.69% [A35-33]. Both shocks are averages of ordinary days. (27.8) shows the gap: 00642U's R-squared
  is under 1%, so almost all of its variance is residual, which a factor shock leaves at its mean.
- E7 §5 `break`: setting the correlation of 0050 and 00679B from −0.105 [A27-11] to a *constructed* +0.30 keeps the
  correlation matrix positive definite (smallest eigenvalue 0.298) and turns 00679B's conditional move from +0.71% to
  −2.04% [A35-33]. R3's loss rises from 1.41% to 2.95%, R7's from 1.40% to 3.00% [A35-33]. 2022 shows a real case
  (an illustration, not one of the five scenarios): from 2022-01-17 to 2022-10-25 TR23 lost 28.47%, 0050 33.93% and 00679B
  22.15%; frozen at the start, R2 lost 22.37% and R4 29.86% [A35-34]. Their daily correlation inside the window was
  −0.138, and +0.019 over the window's 38 ISO weeks [A35-34], against −0.023 over the full sample's 500 [A27-11]: the
  bonds fell with the stocks while the correlation stayed near zero, because both trended down. On the 48 days when
  0050 fell two standard deviations or more, its correlation with 00646 was 0.540, against 0.669 from (16.10)
  [A35-35] and 0.599 in the full sample [A27-11]. For a normal variable a one-sided tail narrows the spread
  (lm16.md:449), but 0050's variance on those days (divisor 48, as the full sample's divides by $T$) is 1.449 times
  its full-sample variance [A35-35]: its fat tail widens the spread. So (16.10) raises the correlation above
  0.599, while the data's 0.540 lies below it. On 48 days that figure's standard error is about 0.10 (normal theory),
  so its gap of 0.13 to (16.10) is 1.3 standard errors: a direction, not a proven difference [A35-35].
- E8 §6 `reverse`, the current books (2026-10-08) and a 10% one-day loss. Each book's mean $\mathbf f^{\top}\bar{\mathbf
  R}$ and $s_p$ give $d^*=(10\%+\mathbf f^{\top}\bar{\mathbf R})/s_p$: R1 0.048% and 0.7434%, so $d^*=13.52$; R2
  0.055% and 0.7216%, 13.93; R4 0.078% and 1.0174%, 9.91; R5 0.030% and 0.5717%, 17.54; R8 0.051% and 0.8191%, 12.27
  [A35-39]. R1's shock is 0050 −10.47%, 00646 −8.79%, 00679B −1.21%, 00635U −6.12%, 00642U −23.00% [A35-39]. The
  sample's largest distance is 15.017 on 2026-03-09, when 00642U rose 33.10%; then 12.971 (2020-03-09) and 12.937
  (2025-04-07); the median is 1.60 [A35-37]. Within $d\le15.017$ R1 can lose $15.017\times0.7434\%-0.048\%=11.12\%$,
  Breuer et al.'s worst loss over the ellipsoid [A35-39]. R1's shock puts 0050 below its limit; with
  $R^{\mathrm{sc}}_{0050}\ge-10\%$ R1's distance barely moves (13.52) but R2's rises from 13.93 to 17.01, its shock
  needing 00679B at −9.89%, beyond that fund's worst day (−7.15%) [A35-39, A35-40, A35-36]. CLARABEL, OSQP and the
  closed form agree to 1e-9; the stationarity residuals are below 1e-13 and complementary slackness below 1e-9 [A35-40].
- E9 §7 `lock`: 0050 on 2025-04-07 opened, peaked, bottomed and closed at 158.40, exactly −1/10 from 176.00, on
  29,578,872 units [A35-12]. A sale not filled at the lock had to wait for 2025-04-08, which opened at 151.20: 4.55%
  below the lock and 14.09% below 2 April [A35-12]. 00631L, limited at 20%, fell 19.995% and then 11.20%
  (lm02.md:498) [A35-43]. TX settled 10.00% down that day against the TAIEX price index's −9.70% on 2,736 contracts
  [A35-44]: the futures locked too.
- E10 §8 `margin`: one TX contract at $F_t=49{,}357$ (lm23.md:327) is NT\$9,871,400 of exposure; with TAIFEX's initial
  margin of NT\$701,000 as the only equity, $f=14.08$ (lm02.md:462) [A35-44]. A fall of 1.65% reaches the maintenance
  margin of NT\$538,000, and a 10% limit day loses 1.41 times the equity, leaving NT\$−286,140 [A35-44]: ruined, and
  the loss is reported, not floored. R6's unit book, by contrast, has ruin leverage 7.67 in 2020's window, 9.90 in
  2025's and 16.77 on 2025-04-07 [A35-41]; R8's uncapped ratio peaked at 2.14 [A31-29].

**Problems plan** (12; MC keys B, A, C, B, C; the lab solves 4, 9, 10, 11 and 12). Stems state the book (exposures, $L$), the
scenario (returns and their span), simple returns, that interest and costs are left out, and the rounding; an
optimization stem states the feasible set, the solver and its tolerances.

1. MC: exposures 0.6 to 0050 and 0.4 to 00679B (hypothetical), scenario −10% and +1.81%; the book's return. A −8.19%
   (the returns added). **B** −5.28%. C −6.00% (the 0050 line alone) [A35-50].
2. MC: a unit book loses 8% in a scenario; the total exposure at which the scenario ruins it. **A** 12.5. B 8.0 (the
   percent read as a multiple). C 11.5 ($(1-0.08)/0.08$) [A35-51]. The solution adds that ruin is $1+LR\le0$.
3. MC: $L=5$ on 0050 (frozen holdings, interest left out), locked at 158.40 from 176.00 on 2025-04-07. A sell order
   placed that day is not filled at the lock; the next open is 151.20. The loss from the 2025-04-02 close at the first
   possible sale: A −50.00% (at the locked close). B −22.73% (from the locked close only). **C** −70.45% [A35-52].
4. MC: a US fund gains 1.0% and then loses 4.0% over the two New York sessions before a Taiwan date, and USD/TWD moves
   from 32.00 to 32.48; the return in New Taiwan dollars. A −3.04% (US dollars). **B** −1.59%. C −4.47% (the FX rate
   applied the wrong way, $\times32.00/32.48$) [A35-53].
5. MC: $s_p=0.8\%$ a day, mean 0, a one-day loss of 10%; $d^*$. A 156.25 ($d^{*2}$). B 3.54 (a square root). **C**
   12.5 [A35-54].
6. A book holds 40% 0050 and 60% of a bond fund. 0050 falls 10%; the bond fund's beta on 0050 is −0.07 in normal
   times and +0.30 in a break (hypothetical). Take both funds' means as 0, so the bond fund moves by its beta times
   0050's move. Compute the bond fund's move and the book's return in both cases: the
   bond fund +0.70% or −3.00%, the book −3.58% or −5.80%, 2.22 points apart [A35-55]. Explain why diversification
   fails exactly when it is needed.
7. Derive (35.4) by a Lagrangian: the shock of least $d^2$ with $\mathbf f^{\top}\mathbf R^{\mathrm{sc}}=-\ell$, its
   $d^*$, and the worst loss $k\sigma_p-\mathbf f^{\top}\boldsymbol\mu$ within $d\le k$ (Cauchy–Schwarz in the
   $\Sigma^{-1}$ inner product). Then two funds with SDs 1.2% and 0.8%, correlation −0.1, $\mathbf f=(0.5,0.5)$,
   mean 0, $\ell=5\%$: $\sigma_p=0.687\%$, $d^*=7.28$, shock −7.12% and −2.88%; show that the shock is $-\ell\beta_{i,p}$
   with LM27's $\beta_{i,p}$ of (27.5), 1.424 and 0.576 [A35-56].
8. Derive the partial scenario (35.3) from (16.8) for each fund. Take the correlation matrix of 0050, 00679B and
   00642U (0050–00679B −0.105, 0050–00642U 0.092, 00679B–00642U −0.18 [A27-11]). Check by its smallest eigenvalue that
   it stays positive definite when −0.105 becomes 0.30 (0.819, then 0.605) [A35-33]. Apply (35.3) with the estimation
   frame's means 0.0995% and −0.0040% and standard deviations 1.2898% and 0.8657% (0050, 00679B; divisor $T$). With
   0050 at −10%, 00679B then moves +0.71% at −0.105 and −2.04% at 0.30 [A35-33].
9. Python: from the lab's weights file, R1's exposures at the 2025-04-02 close and the day's returns; reproduce −7.70%
   and the five contributions [A35-13, A35-14].
10. Python: 2020's window frozen against actual for R6 and R8 (−13.04% and −17.04% frozen, −14.43% and −12.58% actual)
    [A35-15, A35-21]; explain the sign of each difference from the rules' trades (R8's are listed in A35-42).
11. Python: the bounded reverse stress test for R2's current book, its exposures at the 2026-10-08 close [A35-38].
    (a) Minimize $d^2$, with the full estimation frame's $\bar{\mathbf R}$ and $\hat\Sigma$ (divisor $T$), over
    $\mathbf f^{\top}\mathbf x\le-10\%$ and $x_{0050}\ge-10\%$ in cvxpy. Give the objective as
    `cp.quad_form(x - Rbar, cp.psd_wrap(Sigma_inv))` in percent units; CLARABEL with `tol_gap_abs`, `tol_gap_rel`,
    `tol_feas` 1e-12; OSQP with `eps_abs`, `eps_rel` 1e-10, polished; status `optimal` required of both. Answer:
    $d=17.01$, 00679B −9.89%. (b) Check the stationarity residual (below 1e-13), complementary slackness (below 1e-9) and
    the agreement with OSQP and with the closed form for both constraints active (below 1e-9) [A35-40].
12. TX at $F_t=49{,}357$, NT\$200 a point, with the initial margin NT\$701,000 (TAIFEX, effective 2026-08-12) as the
    only equity: $f$, the fall that reaches the maintenance margin NT\$538,000, and the equity after a 10% limit day:
    14.08, 1.65%, NT\$−286,140 [A35-44]. Why does a margin call come long before ruin, and why can a locked market
    prevent meeting it?

**Lab parts** (`build/make_lab35.py`; reads only its `data/`, built locally by `make_lab_data.py` and never committed
(shared decision "Labs", decisions C6, X21): E5's estimation frame and its wealth frame with the traded flags
("Decisions on the first revision", Labs), the rules' per-date targets and
exposures and their net wealth paths, `taiex_tr.csv` (TR23), the five T5S days (per-day statistics and the raw days
the lab studies), the TX23 limit-day rows, LM2's files (`0050_daily_raw.csv`, `0050_dividends.csv`, `00631L_daily_raw.csv`), the
daily open, high, low, close and volume of 0050, 0056 and 00720B (`vol5_series.ohlc`, for E9 and X8), LM35's proxies
and 0050's 2007–2008 files, and
the checkpoint universe's frames): 1 data, frames, windows' dates; 2 X2, E1 (the window rule and LM1's running peak),
holiday spans; 3 X1, X3, X4, E2, E3, problems 9 and 10; 4 the pairing rule (35.5) implemented and checked against the
anchors, E4, E5, problem 4; 5 betas, E6, E7, the PSD check, (16.10) on 0050's worst days; 6 (35.4) by hand, E8, X6, cvxpy
with both solvers (objective `cp.quad_form` of $\hat\Sigma^{-1}$ with `cp.psd_wrap`, percent units, as the
Conventions state) and the KKT check, problem 11; 7 X5 from the five T5S days (per-day statistics only), X8, E9, X7,
E10, problem 12; 8 the widget's presets reproduced; 9 **the batch's checkpoint** (below). Labs write plain "LM39",
"LM44", "LM46", never `[[…]]`. Extension (*hypothetical*): replay 2008 for R1 and R6 with R2's
fixed mix in place of each one's first weights and with DBO instead of USO, and say for each which choice moves the
loss more (the answers differ: the oil proxy for R1, the weights for R6; A35-27's values).

**Checkpoint (Lab part 9; guidance g:45, adjusted by the shared decisions; universe and rules adopted by the editor's
decision D, 2026-10-24).** Universe: E5 plus 0056 (元大高股息), 00662 (富邦NASDAQ, on the Nasdaq-100) and 00720B (元大投資級公司債,
on the Bloomberg US 20+ Year BBB Corporate Bond liquid index; on TPEx, as 00679B is), so that E5's answers cannot be
reused (A35-47). Before any result the reader writes down, in one cell that is not edited afterwards: the rules (R1,
R3, R6 and R8 with the cap 1.5; R2's fixed mix is defined only for E5), the 504-row window, the month-end signals and
next-session trades, the cost model (the shared decision's, with LM34's sources: commission 0.1425% on both markets,
TWSE's Operating Rules Art. 94 and, for 00679B and 00720B, TPEx's Business Rules Art. 64, applied to ETFs by its ETF
rules' Art. 15 ¶1; tax 0.1% on ETF sales, 0056, 00662 and the two futures ETFs included, the futures ETFs by the
Ministry of Finance's ruling 台財稅字第09700161260號 of 2008-08-11, shared decision "Cost model"; 0 on the bond ETFs 00679B
and 00720B through 2026-12-31, by the Securities Transaction Tax Act's Art. 2-1 ¶2, which names listed and OTC-listed
(上市及上櫃) bond ETFs), long-only limits, for R3 a 30% cap per fund, and a one-way turnover limit of 20% per trade after
the first purchase (decision D, X24: the guidance's "turnover limits"). The limit's form is decided ("Decisions on the
first revision", LM35): the first purchase is exempt, and a trade whose target $\mathbf f_t$ would need
$\mathrm{TO}_t=\tfrac12\lVert\mathbf f_t-\mathbf w^{\mathrm{drift}}_t\rVert_1>0.20$ ((27.3), R8's total exposure
included) stops on the straight line to the target, at $\mathbf w^{\mathrm{drift}}_t+(0.20/\mathrm{TO}_t)(\mathbf
f_t-\mathbf w^{\mathrm{drift}}_t)$. Tasks: (a) allocate and run the wealth recursion ((27.1)–(27.2)) from 2020-04-01
to 2026-10-08, checking $1+R_{p,t}>0$ on every date and counting the trades the turnover limit cut; (b) compare out of
sample: net log growth (LM34), the Sharpe ratio with its HAC interval (33.1), maximum drawdown ((32.9)), turnover and
costs, naming $n=4$; (c) stress: the 2024-08-05 and 2025-04-07 windows and named days on the rules' own books (frozen
and actual), 2020 on the first weights (the first trade comes after that window; the funds' 2020 returns are
A35-48's), and each final book's reverse stress test at 10% with the limit bounds of 0050 and 0056 (the two funds with
a limit); (d) explain how the cap, long-only and the turnover limit change R3's allocation, with its multipliers
((29.4)) and (30.4); (e) the failure forms of R8 at the cap 1.5: its exposure path and largest uncapped ratio against
each scenario's ruin leverage $-1/R$, as X7 draws them. Rubric (each item
observable in the notebook): 1 settings fixed before results, the turnover limit among them; 2 every number names its
sample and label; 3 the wealth recursion matches an independent recomputation to 1e-12 and checks $1+R_{p,t}>0$; 4 the
comparison gives intervals and the count of rules; 5 frozen and actual losses for two windows, contributions adding to
the loss; 6 reverse stress shocks checked by KKT and a second solver, the distance compared with the sample's largest,
no probability attached; 7 the active constraints and their multipliers explained; 8 a conclusion with its evidence,
which may be "the data do not support more leverage" (g:116). The reference answers (Stage 2, `data/lm35_numbers.py`)
sit in a collapsed cell after the reader's own. `vol5_rules.py` has neither R3's cap nor the turnover limit, so
`data/lm35_numbers.py` runs both on top of `vol5_rules`' functions, labelled as checkpoint settings (the same
decision); no shared code changes.

**Cross-module tags.**

- (35.1) Scenario P&L $\Delta W=W_0\,\mathbf f^{\top}\mathbf R^{\mathrm{sc}}$ ((8.4) with a scenario's returns); a
  frozen book over a window uses $R^{\mathrm{sc}}_i=\prod_t(1+R_{i,t})-1$ (fixed holdings, no trades, interest left
  out), and the loss splits exactly into $f_iR^{\mathrm{sc}}_i$ (used within LM35).
- (35.2) A unit book with $R^{\mathrm{sc}}_p<0$, scaled to total exposure $L$, is ruined when
  $1+LR^{\mathrm{sc}}_p\le0$, that is from $L_{\mathrm{ruin}}=-1/R^{\mathrm{sc}}_p$; frozen holdings within the
  scenario (used within LM35). Over a window the test applies on every date, so $R^{\mathrm{sc}}_p$ is then the book's
  lowest value in the window. R6's frozen books, which X7 and KC §8 use, reach it at each window's last close. R3's and
  R5's 2024 books reach it on 2024-07-26, at −1.40% and −1.47%, and end at +0.11% and −0.07% [A35-41].
- (35.3) Partial scenario: $\E[R_j\mid R_i=x]=\mu_j+(\sigma_{ij}/\sigma_{ii})(x-\mu_i)$ for a normal vector ((16.8)
  fund by fund). For any law with finite variances the right-hand side is the best linear predictor of $R_j$ from $R_i$ (not in
  general the conditional mean); for an elliptical law whose
  density falls with $d$, the most plausible scenario that fixes $R_i$ (Breuer et al. 2009, Proposition 1) (used
  within LM35).
- (35.4) Reverse stress test: let $\Sigma$ be positive definite, $\mathbf f\ne\mathbf 0$ and
  $\ell+\mathbf f^{\top}\boldsymbol\mu>0$ (the loss lies beyond the book's mean). Then
  $d^2=(\mathbf x-\boldsymbol\mu)^{\top}\Sigma^{-1}(\mathbf x-\boldsymbol\mu)$ is strictly convex, and on the non-empty
  hyperplane $\mathbf f^{\top}\mathbf x=-\ell$ it has exactly one minimizer, $\mathbf
  R^{\mathrm{sc}*}=\boldsymbol\mu-(\ell+\mathbf f^{\top}\boldsymbol\mu)\Sigma\mathbf f/\sigma_p^2$, with
  $d^*=(\ell+\mathbf f^{\top}\boldsymbol\mu)/\sigma_p$; the half-space $\mathbf f^{\top}\mathbf x\le-\ell$, which
  excludes $\boldsymbol\mu$, gives the same point. The largest loss with $d\le k$ is
  $k\sigma_p-\mathbf f^{\top} \boldsymbol\mu$, Breuer et al.'s worst loss over the ellipsoid (2009, §2.3); a
  distance, not a probability (used within LM35).
- (35.5) A US fund's Taiwan-date return in New Taiwan dollars:
  $P^{\mathrm{TWD}}_t=P^{\mathrm{adj}}_{t^{\mathrm{US}}\mid t'}\,\mathrm{FX}_{t^{\mathrm{US}}}$, with LM34's (34.2)
  build date $t'$ (the latest session FinMind held at the retrieval) and the FX row the first dated after that New York close, and
  $R_t=P^{\mathrm{TWD}}_t/P^{\mathrm{TWD}}_{t-1}-1$ (used within LM35).

No later brief exists, so no tag lists a user module (decision C8); the briefs of Volumes VIII and IX add theirs.

**Pitfalls to pre-empt.**

- A "one-day" return can span holidays: 2025-04-07 covers five calendar days, 2020-01-30 ten, across the Lunar New
  Year closure of 2020-01-21 → 01-29 (TWSE's 2020 schedule) [A35-08, A35-06]; say the span with every named day
  (shared decision "LM35 against LM39").
- A window's peak is not LM1's running peak (E1); the worst 20 sessions of 2024's window start before its peak. A
  span of $m$ sessions is dated from the close before its first return, or a reader counts $m+1$ sessions.
- A frozen replay ignores the rule's own trades: R8 lost more on its own path in 2025 and less in 2020 (E3). Report
  both, and name the trade that moved the book (A35-42 lists every trade into a window).
- A stacked bar's parts must add to its label as printed (AUTHORING §7): R6's rounded contributions do not (X4).
- Proxies: the pairing rule gives 0 on US holidays [A35-57]; the adjusted closes re-round at every retrieval, so a
  value that a cent could move prints to 0 dp and every proxy number is re-run after a re-fetch (PITFALLS §3); the
  choice of oil proxy matters (USO −60.7% against DBO about −46% in 2020 [A35-26]), and the text describes DBO by its
  data only, since Invesco states no roll rule and changed the index's method on 2025-11-10, after the replays (second
  hunt); never call a proxy the fund.
- A hypothetical book combines sources (0050, proxies, FX) in one number by design: name each in the caption, and
  never mix them in a statistic of the through case (the shared decision "Data"'s one exception covers only these
  replays).
- Mahalanobis distance ranks how unusual a shock is, in both directions: the sample's most unusual day was an oil gain
  of 33.10% [A35-37]. It is not (16.9)'s probability: (16.9) and LM16's law behind it hold only for normal returns, and these are not
  normal. Breuer
  et al. measure plausibility by it (2009, §2.1); the book attaches no probability to it.
- The closest shock can be impossible in one day: R1's puts 0050 at −10.47% (E8) [A35-39]; bound it by the limit.
- The daily open is stale: on 2025-04-07 it gives a gap of −5.52% against −10.28% by 09:01:00 [A35-45] (PITFALLS §3,
  "An intraday index opens at the previous close").
- Limit ratios: on 2025-04-07 the ratio of 00631L's to 0050's return shows the limits, not the fund (PITFALLS §7;
  lm02.md:498).
- Ruin and losses beyond 100%: report $1+LR\le0$ as ruin with its date or scenario, never floor wealth at 0 (shared
  decision "Return type and the domain of log growth"); a futures book can lose more than its equity (E10).
- Margins only from dated official tables: TAIFEX's table effective 2026-08-12 via LM2; no 2025 margin is quoted
  (PITFALLS §3, "2025 TX margins").
- Causes: a scenario's narrative is printed only from a dated source (shared decision "Unexplained extremes"): the
  April 2025 tariffs (White House fact sheet, 2 April 2025) and the TWD's rise of 2 to 5 May 2025 (TechNews, FTV) are in
  SOURCES; 2008, 2015, 2020, 2022 and 2026-03-09 are described by their data only, unless the editor adds a dated
  source. A calendar fact is not a cause: 2020-01-30's span is printed with TWSE's 2020 schedule, and nothing is said
  about why the market fell that day.
- The limit rules, by market: TWSE's 受益憑證買賣辦法 Art. 8 was last amended on 2024-12-31 (2025-09-30 is the
  rules' version date, and that amendment changed other articles), and its items 1–3 have had the same content since 2016-06-03 (item 1 reworded on 2024-12-31)
  (source check); TPEx's ETF rules, Art. 7 ¶1 item 一, have read 成分證券 since 2017-03-01, and before that TPEx's
  listing notice of 2017-01-13 already gave 00679B no limit (TPEx source check). So the text says that TWSE's rule
  for its four E5 funds has applied since June 2016 and that TPEx gave 00679B no limit from its listing, which covers
  E5's span, and X8's extremes agree. Each fund cites its own market's rule. For the
  hypothetical 2008 and 2015 replays the rules then in force are not asserted: there the text says "under each
  market's current rules" (TWSE's Art. 8 for the stand-ins of 00646, 00635U and 00642U; TPEx's Art. 7 for TLT,
  00679B's), and 0050's own returns carry the limit then in force (7% until 2015-06-01).

**Curriculum guidance carried** (`plans/vol-5.md`'s table; `plans/curriculum-guidance.md`):

- Each module says which layer it adds (g:30): §1's first paragraph.
- Three outcome levels and taught/practised/assessed (g:54–58, g:124): the Outcomes table.
- Checkpoint after Volume VI (g:45, adjusted): Lab part 9 on the eight-fund universe, with the rubric above.
- Different failures in one case (g:87–90): §9's table on R1, R6 and R8: weak growth (LM34's net log growth, A34-04:
  12.89%, 10.80% and 11.59% a year), a drawdown limit (LM32's MDD and largest $\mathrm{DD}^0$ by (32.9), A32-35:
  23.19%, 18.90% and 18.42%; 10.24%, 0.60% and 0.15%), funding (the margin call of E10;
  R8's borrowing at 3.5%), ruin ($L_{\mathrm{ruin}}$, (35.2), A35-41). LM35 prints the last two and cites the first
  two by anchor (the cross-module check's H1); the cited values are the owners' and are rechecked against their final
  anchors at Stage 2. The Summary's last bullet compares the four failure forms on the same rules (the shared table's
  "LM35's summary compares the four").
- Wealth ≤ 0 is reported, never hidden (g:94): (35.2), E10, X7, the widget's readout.
- Surviving the scenarios does not cover unseen losses (g:95): §9's closing pitfall, KC §9.
- Decision flow (g:69–85), LM35's part: a lock removes the trade the flow assumes; a month-end rule meets a gap with
  last month's exposure (E3, E9).
- "Data too thin to support more leverage" is a valid conclusion (g:116): the checkpoint's rubric item 8.
- Not carried here: Kelly-type sizing (Volume VIII), probability bounds for drawdowns (LM44; g:93).

**Stage 4 for earlier modules.** `leads` gain 35 in lm01.md:6 (DD$_t$, (1.17)), lm02.md:6 (00631L's limit day, the TX
margins), lm23.md:6 ((23.1), TX's $F_t$) and lm26.md:6 ((26.2) through R8); all four are on the plan's Stage 4 list
(list G). lm08.md:6 and
lm16.md:6 already list 35. LM27–LM34's briefs (revised 2026-10-24) all list 35 in their leads, LM33's by decision C9;
this list matches the editor's merged Stage 4 list (decision G: lm01 +35, lm02 +35, lm23 +35, lm26 +35). No wording
change in published modules: none promises LM35 anything.

**Sources** (verified 2026-10-24 in the versions named, the TPEx sources, the listing markets and the short names 2026-10-25; paraphrased, nothing quoted
beyond a phrase; bibliographic data, fund names and pages as `project/SOURCES.md` records them; readings as decision F's source check, the second hunt and the TPEx source check with its verifier
record them, the hunt's replacing the first drafts' "not read" for BCBS d450, Breuer et al.'s text and TWSE's 2020
schedule):

- TWSE, 臺灣證券交易所受益憑證買賣辦法 (Rules Governing Trading of Beneficial Certificates), Art. 8:
  [ZH](https://twse-regulation.twse.com.tw/TW/law/DAT0201.aspx?FLCODE=FL007114),
  [EN](https://twse-regulation.twse.com.tw/EN/law/DAT0201.aspx?FLCODE=FL007114), [Art. 8
  alone](https://twse-regulation.twse.com.tw/TW/law/DOC01.aspx?FLCODE=FL007114&FLNO=8) and the [amendment
  history](https://twse-regulation.twse.com.tw/TW/law/DAT01.aspx?FLCODE=FL007114). Read in the original by decision
  F's source check and again by the SOURCES draft. ¶1: a listed beneficial certificate follows the listed-stock limit,
  except four kinds with no daily limit: (1) index ETFs with foreign constituent securities and their attached
  listings, (2) futures-trust ETFs tracking a foreign futures index, (3) offshore ETFs, (4) active ETFs with foreign
  constituent securities. ¶2: a leveraged or inverse ETF on an all-domestic index has 10% times its multiple, one with
  any foreign constituent none. Art. 8 was last amended on 2024-12-31 (臺證上二字第1131705681號, effective at once), which
  added item 4 and reworded item 1; items 1–3 and ¶2 read the same in the versions of 2016-06-03 (臺證交字第1050009905號)
  and 2024-02-23, and the history page names Art. 8 in no amendment between, so the rule for index and futures ETFs
  has stood since 2016-06-03 (earlier versions not read). 2025-09-30 is the rules' version date; that amendment
  (臺證交字第1140205581號) amended Art. 14 and added Arts. 5-1 and 5-2, which let the issuer of an SITC or a futures-trust
  ETF apply to suspend trading during a foreign closure of five or more consecutive business days. The fund's NAV
  must then be at most NT\$3 billion, or its premium or discount must have reached 3% on each of the two business days
  before the application. These rules
  govern the TWSE-listed funds. Applied with TWSE's own classes (e添富, below): 0050 and 0056 10% (台股ETF); 00646 and
  00662 none (國外股票ETF, item 1); 00635U and 00642U none (期貨ETF on foreign futures indices, item 2); 00631L 20%
  (股票槓反ETF, ¶2). Consistent with these funds' extreme days (X8, A35-48).
- TPEx, 指數股票型基金及主動式交易所交易基金受益憑證買賣辦法 (the ETF rules; named 「…指數股票型基金受益憑證買賣辦法」 before
  2024-12-31), in the rules database that TPEx's ETF rules page refers to,
  [selaw LW10845400](https://www.selaw.com.tw/Chinese/RegulatoryInformationResult?sysNumber=LW10845400), read
  2026-10-25 by the TPEx source check and its verifier (anonymous requests). These rules govern the TPEx-listed
  00679B and 00720B. Art. 7 ¶1 item 一: no daily limit (採無升降幅度限制) for 國外成分證券 index ETFs; Art. 2-1 ¶1 item
  二(二) counts an index of bonds with at least one foreign bond as foreign-constituent, so neither fund has a limit.
  Art. 7 was amended 2017-02-13 (in force 2017-03-01), 2018-08-09, 2023-09-15 and 2024-12-31, and the exception stood
  in every text: to 2017-02-28 for an index whose 成分股 (constituent shares) include foreign securities, from
  2017-03-01 for its 成分證券. TPEx's listing notices 證櫃債字第10600009612號 (2017-01-13: 00679B, trading from
  2017-01-17) and 證櫃債字第10700020421號 (2018-01-25: 00720B, from 2018-02-01) and its product pages, for
  [00679B](https://www.tpex.org.tw/zh-tw/product/etf/product/detail.html?type=bond&code=00679B) and
  [00720B](https://www.tpex.org.tw/zh-tw/product/etf/product/detail.html?type=bond&code=00720B), state
  無漲跌幅度限制 for both. Arts. 4-2 and 4-3, added 2025-09-30, are the counterparts of TWSE's Arts. 5-1 and 5-2. The
  listing markets (00679B and 00720B 上櫃; 0050, 00646, 00635U, 00642U, 0056 and 00662 上市) and the short names the
  checkpoint prints (0056 元大高股息, 00662 富邦NASDAQ, 00720B 元大投資級公司債) are SOURCES' listing-markets row (TPEx's
  ETF list and quotes, TWSE's ISIN pages) and TPEx row; the commission rule (the ETF rules' Art. 15 ¶1, the Business
  Rules' Art. 64) is LM34's source. Consistent with the two funds' extreme days (X8, A35-48) and with FinMind
  printing no limits for them.
- TWSE's [ETF rules page](https://www.twse.com.tw/zh/products/securities/etf/overview/rules.html) (ETF 專區, 交易規則):
  ticks 0.01 below NT\$50 and 0.05 from NT\$50; the daily limit as for stocks (10%), none for an ETF holding overseas
  stocks; tax 0.1% on ETF sales, bond ETFs exempt through 2026. The page prints no date (footer ©2023; the server's
  Last-Modified header 2026-10-22). The text cites Art. 8 for the TWSE funds' limits, since the page's sentence is
  narrower.
- TWSE's ETF e添富 fund pages (`https://www.twse.com.tw/zh/ETFortune-institute/etfInfo/<code>`, read by the SOURCES
  draft): the exchange's class and index of each fund: 0050 and 0056 台股ETF; 00646 and 00662 國外股票ETF, 00662 on
  the NASDAQ-100指數; 00635U and 00642U 期貨ETF, on the S&P GSCI Gold Excess Return Index and the S&P GSCI Crude Oil
  Enhanced Excess Return; 00631L
  股票槓反ETF. 00662's page announces a 5-for-1 split, no trading 2026-11-11 → 11-16, trading again from 2026-11-17, after the sample. For
  00679B and 00720B, which are TPEx-listed, the pattern returned the e添富 home page; TPEx's product pages (above)
  class both 被動式國外債券及固定收益ETF.
- Fund pages read 2026-10-24: Yuanta's for 0050, 00646, 00635U, 00642U, 0056 and 00720B (the tracked index and the
  listing date; 00720B: Bloomberg US 20+ Year BBB Corporate Bond liquid index, listed 2018-02-01; 0056: FTSE TWSE
  Taiwan Dividend+ Index); the short names, read 2026-10-25 (Fubon's table 2026-10-24; SOURCES' short-names item), are
  元大高股息 (0056) and 富邦NASDAQ (00662), from TWSE's ISIN and e添富 pages, which Fubon's table also prints, and TPEx's
  元大投資級公司債 (00720B), from its product page, whose full name, 元大20年期以上BBB級美元公司債券ETF證券投資信託基金, SOURCES'
  TPEx row records; [Fubon's 00662
  page](https://www.fubon.com/asset-management/ph/NASDAQ00662/index.html) (追蹤標的指數 Nasdaq-100指數, data date 2026.08;
  second hunt), which with TWSE's page settles 00662's index ("Decisions on the first revision"); USCF's [USO
  page](https://www.uscfinvestments.com/uso) (the near-month NYMEX light sweet crude contract, moved to the next over
  five days at the start of each month; operations from 2006-04-10; a 1-for-8 reverse split on 2020-04-28, which
  FinMind's US closes already absorb, as the SOURCES draft checked); Invesco's [DBO
  page](https://www.invesco.com/us/en/financial-products/etfs/invesco-db-oil-fund.html) (the DBIQ Optimum Yield Crude
  Oil Index Excess Return, a rules-based index of WTI futures, rebalanced annually in November; inception 2007-01-05).
  Invesco states no roll rule beyond the name, and its index method changed on 2025-11-10, after the replays: no DBO
  roll rule is printed (decision "Sources read by the second hunt").
- TWSE's limit history (7% to 10% on 2015-06-01) and TAIFEX's TX specification (±10%), TAIFEX's margins effective
  2026-08-12: SOURCES rows "TWSE company history", "TAIFEX TX", "TAIFEX index margins" (via lm02.md:462).
- TWSE Holiday Schedule 2025 (SOURCES): 3 April, the observed holiday for Children's Day and Tomb-sweeping Day (both
  on 4 April), and 4 April itself, so 7 April followed four non-trading days.
- TWSE, 中華民國109年有價證券集中交易市場開（休）市日期表 (the 2020 holiday schedule), read by the second hunt in the
  Internet Archive's copy of 2020-06-04 (TWSE's API returns no rows for 2018–2020): the last session before the Lunar
  New Year was 2020-01-20; no trading 21–22 January (settlement only); 23 January an adjusted holiday; 24 January the
  eve; 25–29 January the holiday; trading again from 30 January. So the market was closed 2020-01-21 → 01-29
  (decision "Sources read by the second hunt"), and 2020-01-30's return spans ten calendar days (A35-06, A35-10); SOURCES'
  2020-schedule row.
- Basel Committee on Banking Supervision (2018), *Stress testing principles* (d450), October 2018, ISBN
  978-92-9259-207-3: [BIS page](https://www.bis.org/publications/201810-guidelines-stress-testing-principles)
  (Guidelines, published 17 October 2018; the old `bcbs/publ/d450.htm` address redirects there) and
  [PDF](https://www.bis.org/publications/201810-guidelines-stress-testing-principles.pdf), read by the second hunt.
  The BIS page lists it as replacing the principles of May 2009 (now superseded); the PDF calls itself their update
  (Introduction, p. 1) and says the principles are guidelines, not standards (also p. 1); Principle 4, p. 6: scenarios
  should be "severe but plausible"; p. 6: reverse stress tests explore scenarios that could make a bank fail, and so
  help it find its core vulnerabilities. §9 prints both, paraphrased, with only the phrase "severe but plausible"
  quoted.
- Breuer, T., M. Jandačka, K. Rheinberger and M. Summer (2009), "How to Find Plausible, Severe, and Useful Stress
  Scenarios", *International Journal of Central Banking* 5(3): 205–224, September 2009; no DOI (Crossref searches find
  only SSRN working papers by the same authors). [Journal
  page](https://www.ijcb.org/journal/v5n3/how-find-plausible-severe-and-useful-stress-scenarios) (the old
  `ijcb09q3a7.htm` address redirects there), read by the second hunt in the journal PDF linked there, pages 205–224
  from its first and last pages. The abstract: a region of plausibility defined from the risk factors' distribution,
  searched for the scenario with the worst portfolio loss. §2.1, p. 209: plausibility by the Mahalanobis distance in
  its square-root form, as LM35's $d$, a large distance meaning low plausibility. §2.2, p. 210, Proposition 1: for an
  elliptical law whose density falls with that distance, setting the unstressed factors to their conditional
  expectations gives the most plausible scenario among those that fix the stressed ones; the four options compared are
  credited to Kupiec (1998). §2.3, p. 211: the worst loss over the ellipsoid of distance at most $k$. So §6's worst
  loss within $d\le k$ is their construction, not the book's own, and (35.3) cites Proposition 1 for its conditional
  choice under ellipticity.
- Kupiec (1998), "Stress Testing in a Value at Risk Framework", *The Journal of Derivatives* 6(1): 7–24 (Crossref: 31
  August 1998), DOI [10.3905/jod.1998.408008](https://doi.org/10.3905/jod.1998.408008). Text not read (the publisher's
  page needs a login; OpenAlex holds no abstract): cited only as Breuer et al. describe it, for the four options of
  §2.2 (decision "Sources read by the second hunt"); (35.3) is derived from (16.8).
- Boyer, Gibson and Loretan (1999), Theorem 1, for (16.10), and Wasserman (2004) for $d^2$: via LM16 (SOURCES).
- Jagannathan and Ma (2003), Proposition 1, via LM30's (30.4) (shared decision "References").
- News already in SOURCES: White House fact sheet of 2 April 2025 (the April tariffs); Atkinson (7 April 2025),
  TechNews: 936 listed stocks closed limit-down; TechNews and FTV, 5 May 2025: USD/TWD 31.064 on 2 May and 30.145 on 5
  May (SOURCES' TechNews and FTV row, on the TWD surge), the day of 00679B's worst return [A35-36].
- FinMind datasets `USStockPrice`, `TaiwanExchangeRate`, `TaiwanStockPrice`, `TaiwanStockDividendResult`,
  `TaiwanStockSplitPrice`, `TaiwanStockTotalReturnIndex`, `TaiwanVariousIndicators5Seconds`, `TaiwanFuturesDaily`:
  SOURCES' FinMind rows (licence, attribution); retrieval dates in every `Source:` line.

Kept out (the source reports' advice): any DBO roll rule; Breuer et al.'s OeNB working-paper listing (unverified);
Kupiec's (1998) own text; the limit rules in force in 2008 and 2015 (TWSE's before 2016-06-03 were not read; the text says "under each
market's current rules");
any cause of a scenario without a dated source.

**Chinese terms** (AUTHORING §1; English in parentheses at first use in each box). On the plan's list
(`plans/vol-5.md`, "Chinese terms"): 壓力測試, 情境分析, 敏感度分析, 歷史模擬法, 保證金追繳, 槓桿, 共變異數矩陣, 尾部風險, 回撤,
最大回撤. Decided by the fresh 樂詞網 pass ("Decisions on the second recomputation", "Chinese terms"): 漲跌幅限制 for
price limit, as five published modules print it (lm04.md:212, lm12.md:527, lm13.md:342, lm17.md:450, lm22.md:355;
管理學名詞's 漲跌停限制 is recorded in SOURCES, not printed); Mahalanobis 距離 with a space, as LM16 prints it
(lm16.md:429, 660), though the listings write Mahalanobis距離; 權益歸零 for ruin in X7's caption and the §8 box, never
破產 (統計學名詞's 賭者破產 is gambler's ruin; AUTHORING §1 keeps 權益歸零 for zero equity); 有效限制 for an active
constraint, LM7's Glossary form (lm07.md:769, 緊限制式（有效限制）), if the §6 box names the bound that binds in E8.
From 樂詞網 (2026-10-24):
conditional expectation → 條件期望值 (數學, 統計學); factor model → 因子模型 (統計學名詞); overnight → 隔夜 (統計學名詞's
only entry is 隔夜拆款利率, the overnight interbank call loan rate); worst-case scenario → 新聞傳播學名詞's 最差情況；最糟情境
(another field's entry; not printed in a box). No 樂詞網 entry (0 results for "reverse stress test", "reverse stress
testing", "stress scenario", "historical scenario", "hypothetical scenario", "gap risk", "proxy variable", "zero
equity", "price gap"): the book's forms 反向壓力測試, 壓力情境 (心理學名詞's 壓力情境 is "stressful situation", so it always
carries its English), 歷史情境, 假設情境 (土木工程名詞 gives it for "what-if scenario"), 跳空 (gap), 代理資產 (proxy;
樂詞網's "proxy" entries are 管理學名詞 委託書, 管理學名詞-會計學 參考值；替代, 會計學 代理，委託 and 電子計算機名詞
代理伺服器) and 鎖跌停 (limit-down lock), each with its English in every box. AUTHORING's own: 權益歸零 (zero equity),
never 斷頭.

**Open before Stage 2** (revised 2026-10-24 a third time, finished 2026-10-25 and brought up to date on 2026-10-31
after the fresh check of the whole of Stage 1: how every earlier item closed, then the items still open, each with the
reviser's recommendation).

Closed:

- The draft's ten items closed in the first revision, as recorded there: registrations (`6b02e71`, byte-identical to
  the drafter's copies), DBO (approved by the owner), 0050 in 2008 (registered), the windows and the 2008 and 2015
  weights (decision D), the checkpoint (decision D, with the turnover limit), the limit rule (decision F's source
  check), the symbol $\ell$ (decision B3), the four failure forms (§9's table), R8 at higher caps (decision E: X7's
  ruin line), and the unread sources (below).
- The second revision's item 1, the checkpoint's turnover limit and R3's cap: decided in "Decisions on the first
  revision" (LM35): the first purchase exempt, the straight-line stop at
  $\mathbf w^{\mathrm{drift}}_t+(0.20/\mathrm{TO}_t)(\mathbf f_t-\mathbf w^{\mathrm{drift}}_t)$ with $\mathrm{TO}_t$ by
  (27.3), both run in `data/lm35_numbers.py` on top of `vol5_rules.py`. The Checkpoint paragraph states it as decided.
- Item 2, tag users in the sibling briefs: decided ("Tags and leads"): LM27–LM29 take the cross-check's tag-user table
  (Y1), which adds LM35 to (27.3), (28.1) and (29.4); every other tag LM35 cites already lists it. LM35's own tags list
  no user module, and its speculative "pointed to by" notes are gone (Y1).
- Item 3, sources outside the source check's list: read by the second hunt and decided ("Sources read by the second
  hunt"): BCBS d450 and Breuer et al. may be printed (§9, §6, (35.3)); 00662's index is the Nasdaq-100 (TWSE's fund
  page and Fubon's); DBO's index is named and its roll rule stays out; the 2020 Lunar New Year closure is printed with
  TWSE's schedule (KC §2, E1, pitfalls). The Sources section above now prints them at their locations.
- Item 4, the spine's 27 sector closes: dropped ("Decisions on the first revision"; the spine's data line now reads
  "0050's own 2007–2008 closes").
- The cross-check's Y20, outcomes 1–5 at 25–27 words (optional): outcomes 1, 2, 3 and 5 are trimmed to 20–26 words;
  outcome 4 keeps its 26 words, since they bind the problem to its constraint and its check.
- The second recomputation's findings (major 1–6, minor 1–6) and its PENDING list: applied; the final message to the
  editor lists each change. The cross-check's Y items naming LM35: Y1, Y2 (B6, with LM34's written-out product), Y4,
  Y5, Y10, Y11, Y12, Y13, Y18 and Y20 are applied in the text; Y14 and Y15 concern the shared text, which now carries
  list G and the spine's new data line, and the Stage 4 list below matches list G.
- The fresh verifier's ten minor findings on the third revision (2026-10-25): applied. R8's exposure after the trade
  of 1 April 2025 prints as LM31's 1.33 [A31-32]; (35.3) and §5's Deep Dive index funds by $i$, $j$ (AUTHORING §6
  keeps $k$ for the bound $d\le k$), and (35.3) states Proposition 1's hypothesis; the local note is two blocks; the
  cvxpy form is stated; X2's note prints the worst days' ranks; published numbers cite file:line (lm19.md:46,
  lm23.md:327); the futures ETFs' indices are named in full.
- The re-check's five minor findings and its question (2026-10-25), with the "Decisions on the third revision":
  applied. The Conventions and A35-40 state what the `cp.sum_squares` form changes as the re-check measured it; the
  Used list declares $\sigma_{ij}$, $\sigma_{ii}$, $\mu_i$ and $\mu_j$; E4 prints whole percents without a flag
  mark; problem 11 states OSQP's settings and the agreement tolerance; §5's Deep Dive sentence is split. The short
  names 元大高股息 (0056), 富邦NASDAQ (00662) and 元大投資級公司債 (00720B) print, since SOURCES records them (decision
  "LM35"). By "Listing markets", outcome 6, §7's row, X1, X8, the limit pitfall and the Sources name each fund's
  market and rule (TWSE's Art. 8; TPEx's ETF rules, Art. 7 ¶1 item 一); X8's note and §7 cite 00720B's −11.25% of
  2020-03-19 [A35-48]; the checkpoint's costs cite both markets' commission rules and Art. 2-1 ¶2's 上市及上櫃; "no
  halt" rests on the frames. BCBS d450's "guidelines, not standards" moves to p. 1, as the SOURCES pass reads it.
- The SOURCES rows (the earlier item 1): every row this brief cites is in `project/SOURCES.md` (`9575efa`), and the
  e添富 row names the briefs that cite it (LM27, LM34 and LM35). LM35's writer cites only rows in `project/SOURCES.md`.
- The fresh check of the whole of Stage 1 (2026-10-31): its confirmed findings are applied, with the editor's
  choices. The local note and the 2015 replay say that GLD stands in for 00635U, which traded from 2015-04-15
  (option b). E7's tail correlation carries its standard error, about 0.10, and a softened conclusion [A35-35].
  Checkpoint task (e) runs R8 at the cap 1.5 only (option b). The anchor changes are made: A35-02 prints its
  difference as a bound, A35-33 problem 8's inputs, A35-35 the standard error, A35-40 complementary slackness and
  A35-41 the frozen books' lowest values; those rows were reproduced by the fresh verification of 2026-10-31.

Still open:

1. **0050's 2007–2008 files:** closed. The owner approved them on 2026-10-31, so the 2008 replay keeps 0050's own
   data and no number changes.
2. **00662's split after the sample (watch item).** TWSE suspends 00662's trading 2026-11-11 → 11-16 for a 5-for-1 split; trading resumes 2026-11-17.
   No LM35 number changes, since the data end on 2026-10-08. Recommendation: none now; if the checkpoint's data are
   ever extended past that date, `vol5_series.py`'s split check (FinMind `TaiwanStockSplitPrice`) must see the event
   before any number is reprinted.
