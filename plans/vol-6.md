# Volume VI — Measuring True Risk and Return: briefs

Volume VI (LM32–LM35) is the second half of batch 4. Its shared decisions, the through case (E5 and the rules R1–R8),
the capability check and the owner's answers, the editor's decisions on the survey and on the briefs, the Stage 4 list
and the spines are in [`vol-5.md`](vol-5.md); they apply here unchanged. Every number a brief quotes is an anchor in
[`vol-6-anchors.md`](vol-6-anchors.md), printed by `data/vol6_anchors_lmNN.py`. Until Stage 3 the briefs and anchors are
the plan; from Stage 3 the module sources and their numbers scripts are authoritative.

Status: the drafters' briefs and anchors of 2026-10-24, before the revisions that the editor's decisions in plans/vol-5.md require; anchors recomputed independently (416 of 423 reproduced as defined).

## LM32 VaR, Expected Shortfall and Drawdown

Stage 1 brief, drafted 2026-10-24 from the editor's spine (`plans/vol-5.md`, "### LM32 VaR, Expected Shortfall and
Drawdown") and the shared decisions above it. Every number carries its anchor ID at first appearance;
`data/vol6_anchors_lm32.py` prints them all (55 rows, `## LM32` of `plans/vol-6-anchors.md`). Numbers quoted from
published modules carry their file:line instead; the through case's definitions are cited to LM27–LM31 (their briefs'
tags, rechecked when those modules are written). Statistics owned by another module are not printed (shared decision
"Owners").

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
- LM14: the quantile function $F_X^{-1}(u)=\min\{x:F_X(x)\ge u\}$ (lm14.md:85–86) and its sample form
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
- LM19: TR23's sample (lm19.md:46: $T=5{,}849$, 23.7645 years, $A=246.12$) and $\bar R$, $s$ (lm19.md:19); the variance
  of an $m$-day sum (19.7), for the $\sqrt m$ rule; the promise that a drawdown is a path statistic (lm19.md:138).
- LM20: Hill's estimator and its SE (20.10) with $k=108$ and $\hat\alpha=3.63$ at 3% (lm20.md:441); the Student-$t$ fit
  of TR23, $\nu=3.065$ (0.144), location 0.0997% (0.0124), scale 0.7761% (lm20.md:269); the promises of lm20.md:276 and
  449.
- LM21: the exact binomial tail as a test of a frequency (lm21.md:95, 207) and of a count after an event; one-sided
  p-values (21.2); Bonferroni (21.6); the rule that every module reports how many tests ran on the same data.
- LM22: the stationary bootstrap (22.3) and the book's block rule (lm22.md:254: 145 for TR23); LM18's five returns as
  a hand example (lm22.md:75).
- LM26: EWMA (26.2), GARCH(1,1) (26.3), its unconditional variance and $m$-step forecasts (26.4); the forecast design
  (1,231 returns, monthly refits, 4,609 days; lm26.md:357) and the 2 April → 7 April forecasts 1.7222 and 1.5605
  (lm26.md:39); variance forecasts scored by (26.8) and (26.9), contrasted in §7 with scoring a quantile.
- LM27: the wealth recursion (27.1)–(27.2) whose path the drawdowns use, E5's two frames, $\sigma_p$ (27.4), and R1 and
  R2.
- LM28 and LM29: R3 and R4 (LM29's long-only forms); LM29's linear programs and convexity for Problem 12's
  expected-shortfall minimization (shared decision "LM29's scope").
- LM30: R5. LM31: R6–R8, (31.7) for R8's exposure $L_t$ (cited, not printed).

**Leads:** `[33, 34, 35, 36, 39, 44]`: LM33 (the rules' Sharpe ratios beside their tail risk; §8 points to it), LM34
(net results beside the rules' drawdowns, (32.9)), LM35 (VaR and ES against scenario losses, the 7 April forecasts,
(32.1)–(32.3), (32.8), (32.9)), LM36 (Brownian motion, behind (32.10)), LM39 (jumps, the day GARCH could not see; (32.3),
(32.4), (32.8)), LM44 (drawdown control and drawdown probabilities under a model; (32.7), (32.9), (32.10)).

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
among the users of (16.10), the correlation given an event; LM32 does not need it, and LM35's correlation break is its
natural user (Open O9).

**Outcomes** ("After this module you should be able to:"; the level in brackets is the brief's, and the page keeps
AUTHORING §3's form, the level showing in the verb):

1. [D] define $\operatorname{VaR}_u$ and $\operatorname{ES}_u$ over $m$ days from the quantile function, and derive the historical estimators and the normal and Student-t formulas
2. [C] compute historical, normal, Student-t and Hill-tail VaR and ES of a return sample in NumPy and SciPy, stating the quantile convention, and diagnose which part of the tail each model misses
3. [C] compute a distribution-free interval and a standard error for a VaR estimate, and explain why one year of returns cannot pin down a 99% VaR
4. [D] state the four coherence axioms, show with a constructed portfolio that VaR can fail subadditivity, and derive expected shortfall as the minimum of a convex function
5. [C] turn EWMA and GARCH forecasts into one-day and ten-day VaR and ES, by formula and by Monte Carlo, and compute how rare a loss is under each model
6. [C] backtest VaR forecasts by their exceedances with the exact binomial test, the Basel traffic light and an independence check, stating the number of tests
7. [C] compute a portfolio's drawdowns, maximum drawdown, longest spell under water and loss from initial wealth, and show by permutation and block bootstrap how much the order of returns matters
8. [U] explain what the $\sqrt m$ rule, the Basel choice of ES at 97.5% and the Brownian-motion drawdown result assume, and choose among VaR, ES and drawdown for a stated purpose

Taught, practised, assessed (REVIEW_PROMPT item 10): 1 — §2, §3 (derivations, Deep Dive §3); E1, E3; Problems 2, 3, 5.
2 — §2, §3, §9; E2, E3; X3; Problems 1, 11; KC §9. 3 — §4; E5; Problem 6; KC §4. 4 — §5 (Deep Dive §5); E6; Problems 7,
12; KC §5. 5 — §6; E7, E8; Problem 10; KC §6. 6 — §7; E9; Problems 8, 9; KC §7. 7 — §8; E10; Problem 4; KC §8. 8 — §3,
§5, §8; E4; KCs §3, §5, §8.

**Owns.** VaR and ES defined from the quantile of an $m$-day simple return at tail probability $u$, positive for a
loss, (32.1), with the continuous-case tail mean by (18.1); the historical estimators (32.2), $-R_{(j)}$ and Acerbi and
Tasche's tail mean of $\hat F$ (the book's one ES estimator, every later module uses it; decided below); normal VaR and
ES (32.3), derived from (15.6) and (5.11); Student-$t$ VaR and ES (32.4), derived; the moments each needs; Hill-tail
VaR and ES (one paragraph, Problem 11); the horizon $m$, the $\sqrt m$ rule and its conditions, the ten-session VaR of
TR23 (E4); the precision of a quantile: the distribution-free interval (32.5), the asymptotic SE (32.6) *stated
without proof*, iid and block bootstrap SEs, one year of returns; coherence (four axioms, Artzner et al. 1999),
subadditivity of normal VaR, a constructed portfolio where VaR fails it (E6), ES coherent (Acerbi and Tasche 2002,
*stated*), Rockafellar and Uryasev's minimum (32.7), derived, and the minimum-ES linear program (Problem 12, citing
LM29); ES at 97.5% against VaR at 99% (BCBS 2019, MAR33.3); filtered VaR and ES (32.8) from LM26's forecasts; the
ten-day Monte Carlo VaR under GARCH-t; how rare a loss is under a model, with importance sampling (Problem 10);
backtesting: exceedances, the exact binomial coverage test, Basel's 1996 traffic light, an independence check by
LM21's exact count, twelve tests and Bonferroni; $\mathrm{DD}_t$ (LM1), MDD, the longest spell under water and
$\mathrm{DD}^0_t$ (32.9); the rules' VaR, ES and drawdowns; MDD under permutation and the stationary bootstrap, with
the bootstrap's atoms; the Brownian-motion expected maximum drawdown (32.10), *stated without proof* with its model.
Values owned: every A32 anchor except the echoes (TR23's sample, LM14's quantiles, LM15's and LM20's fits, LM26's
forecast SDs, LM27's frames), which are cited to their modules.

**Leaves.** The rules' Sharpe ratios, intervals and tests → LM33. Net wealth, log growth, turnover, costs → LM34 (the
drawdown criterion of the shared decision is LM32's). Scenario replays without probabilities, limit locks, holidays,
the overnight gap → LM35 (LM32 says once that 7 April's return spans four non-trading days and that limits capped it).
Brownian motion → LM36; jump models → LM39; drawdown probabilities under a model, drawdown control and limits
(Busseti, Ryu and Boyd's bound is relative to initial wealth, guidance g:136) → LM44; Kelly sizing under a VaR or ES
limit → Volume VIII. Not in the book (one sentence each): backtests of ES, extreme value theory beyond Hill
(lm20.md:449), multivariate GARCH (shared decision), conditional drawdown measures. To the lab and problems (density,
g:60–63): Hill-tail VaR (Problem 11), importance sampling (Problem 10), the minimum-ES LP (Problem 12), a coloured
portfolio Monte Carlo, a likelihood-ratio form of the coverage and independence tests (only if read, O2), intraday
drawdowns from T5S (per-day statistics), a 250-return backtest window (the extension).

**Uses before taught** (one sentence each in the text):

- §8: "Brownian motion, the continuous-time limit of a random walk, is [[LM36]]'s subject; (32.10) is stated here
  without proof, with its model."
- §6: "A move that no variance forecast anticipates is a jump, which [[LM39]] models."
- §8: "Choosing a position size so that drawdowns stay inside a limit is [[LM44]]'s subject."

**Data role.**

- **TR23** (Volume III), through `data/lm26_common.py`, which reads `data/processed/vol3_taiex.parquet` (built and
  checked by `data/vol3_series.py`; FinMind `TaiwanStockTotalReturnIndex`, data_id TAIEX, retrieved 18 October 2026)
  and the committed `data/derived/vol4_rv.csv`. $T=5{,}849$ simple returns, 3 January 2003 → 8 October 2026, 23.7645
  years, $A=246.12$ [A32-01] (lm19.md:46). Log returns in percent $y_t=100\ln(1+R_t)$ for EWMA and GARCH (LM26's
  units). 7 April 2025 is checked to be the exact minimum with `Fraction` on the two-decimal closes [A32-02].
- **LM26's forecasts** (`forecasts()`): window $\operatorname{round}(5A)=1{,}231$, GARCH(1,1) with normal and with $t$
  innovations refitted at each month's first session (226 refits per law), EWMA 0.94 with zero mean; forecast days
  2 January 2008 → 8 October 2026, $n=4{,}609$ [A32-04]. HS and N use the same trailing 1,231 simple returns every day;
  the $t$ model refits `scipy.stats.t.fit` on them at each month's first session (LM26's schedule). The window is
  LM26's, fixed before LM32 (decided below).
- **E5's wealth frame and the rules** (Volume V): `vol5_series.frames("E5")` and `vol5_rules` (`signals`,
  `wealth_path`), recomputed and asserted equal to `data/processed/vol5_rules.parquet` [A32-03]. A rule's return is its
  net wealth ratio; the returns run from the session after the first trade, 1,851 sessions, 5 March 2019 → 8 October
  2026, 7.60 years [A32-03]; the drawdown path starts at the cash of 1 before the first purchase, as `summary()` does,
  so the first purchase's cost (0.142% for R2 [A32-40]) is in it. No path reaches wealth ≤ 0 (asserted; guidance g:94).
  Problem 12 uses the through case's first window, 504 estimation rows to 27 February 2019 [A32-24].
- **T5S** (Volume IV), lab only: three raw days under `data/raw/intraday/taiex5s/` (7 April 2025, 5 August 2024, 19
  March 2020), the TAIEX price index; 09:00:00 is the previous close (PITFALLS §3); per-day statistics only, never a
  path [A32-44].
- **Constructed and hypothetical inputs:** E6's bonds [A32-22] and Problem 7's [A32-50]; Problem 4's wealth path
  [A32-48]; Problem 9's counts [A32-52]; the 20% drawdown limit of §8; the Brownian example's $\sigma=20\%$, ten years
  [A32-38].
- **Conventions.** VaR and ES are positive for a loss; $u$ is the tail probability, "99%" is $u=0.01$; one day unless
  $m$ is named; an $m$-day return compounds simple returns. Quantiles $\hat F^{-1}(u)=R_{(\lceil uT\rceil)}$
  (`method="inverted_cdf"`, passed explicitly). Historical ES (32.2). Normal: $\bar R$ and $s$ with divisor $T$
  (`ddof=0`). Student $t$: maximum likelihood on returns in percent, written in (15.11)'s form. Filtered models: (32.8)
  on $y$, mapped to $R$ by $e^{y/100}-1$. An exceedance is $R_t<-\operatorname{VaR}_t-10^{-12}$, and the smallest
  margin is printed (1.1e-4 for HS) [A32-31]. Coverage: one-sided exact binomial upper tail; independence: the count of
  exceedances followed by another against $\operatorname{Bin}(\text{trials},x/n)$ (LM21's exact form); Basel zones by
  BCBS (1996)'s cumulative probabilities. Drawdowns in sessions; years are calendar days ÷ 365.25. Every count against
  a threshold uses one guard.
- **Seeds** (one generator per experiment, `np.random.default_rng([e, 20261011])`, created once): 1 the ten-day GARCH-t
  Monte Carlo (100,000 paths) [A32-28]; 2 importance sampling (10,000 draws) [A32-53]; 3 permutations of each rule's
  returns (10,000 per rule, rules in order) [A32-36]; 4 the stationary bootstrap of each rule's returns (10,000 per
  rule) [A32-37]; 5 and 6 the iid and stationary bootstrap of TR23's 1% quantile (10,000 each) [A32-20]; 7 ten iid
  sessions from TR23 (100,000) [A32-55]. Batch standard errors use 20 batches (divisor 20), as LM18. The widget does not
  simulate.
- **Published files** (Volume IV's X37 rule): no file carries a daily series in date order. X4 plots three models'
  $-\operatorname{VaR}$ thinned to weekly points plus every cited day, and the returns of exceedance days only (HS and
  GARCH-t, at most 133 dated points); X7 thins the drawdown paths to weekly points plus every cited peak, trough and
  recovery; X2 is a histogram; the widget embeds each rule's 186 worst returns sorted, without dates; no T5S value is
  published.
- **Scripts.** `data/lm32_numbers.py` (every printed value, asserted against `src/lm32.md`, compared with the anchors,
  rounding flags) and `data/lm32_charts.py` (X2, X4, X5, X7, X9 and the widget block); both after `data/vol3_series.py`,
  `data/vol5_series.py` and `data/vol5_rules.py` (and LM26's committed `vol4_rv.csv`). The anchors script runs in about
  35 seconds.

**Hygiene declaration.** *Out-of-sample:* the six models' one-day forecasts on 4,609 days, each from data before its
day, with LM26's window and refit schedule fixed before LM32, and the 7 April forecasts; the module runs 12 tests on
these forecasts (coverage and independence for six models) and corrects for them (§7). *Out-of-sample (fixed in
advance, 2026-10-24):* the rules' returns, 5 March 2019 → 8 October 2026; their historical VaR, ES and drawdowns
describe that record for all eight rules, none selected. *In-sample:* TR23's full-sample VaR and ES (historical,
normal, $t$, Hill); the rules' normal and $t$ fits (A32-41, A32-42); the minimum-ES portfolio of the first window
(Problem 12; an illustration outside the through case's family, so $n=8$ is unchanged). *Model:* experiments 1–7, the
rarity of 7 April under each GARCH law, the Brownian result. *Constructed* and *hypothetical:* the bonds, Problem 4's
path, Problem 9's counts, the 20% limit. *Descriptive:* T5S per-day statistics (lab). Local note: "TAIEX forecasts are
out of sample: each day's value at risk uses only earlier returns, with the window and refits fixed before this
module, and Section 7 counts its twelve tests. The eight rules were fixed on 24 October 2026; their tail and drawdown
figures describe their out-of-sample record, 5 March 2019 to 8 October 2026, and all eight are reported. Full-sample
tails are in-sample; simulations are model results."

**Notation.** AUTHORING §6 with the Portfolios table and its LM32 row ($\alpha$ the tail index, GARCH coefficients in
words, $k$ Hill's count, $\ell$ a block length, no log-likelihood). Used: $R$, $r$, $y$ (LM26's $100\ln(1+R)$), $T$,
$t$, $A$, $A_{\mathrm w}$, $u$, $U$ (18.1), $m$, $n$, $j$, $R_{(j)}$, $F_R$, $F_R^{-1}$, $\hat F$, $\hat F^{-1}$, $\E$,
$\Pr$, $\mathbf 1\{\cdot\}$, $\varphi$, $\Phi$, $\Phi^{-1}$, $\mu$, $\sigma$, $\bar R$, $s$, $\bar r$, $s_r$, $Z$,
$Y\sim t_\nu$, $f_Y$, $F_Y^{-1}$, $\nu$, $\operatorname{Bin}(n,u)$, $\alpha$, $\hat\alpha$, $k$, $x_0$ (LM20's), $g$,
$\sigma_{t+1\mid t}$, $\xi_t$ (LM26's), $\operatorname{SE}$, $B$, $\ell$, $W_t$, $W_0$, $\mathrm{DD}_t$, MDD,
$\mathrm{DD}^0_t$, $\mathbf w$, $\mathbf R_t$, $\sigma_p$, $L_t$ (R8's exposure, cited), $\tau$ (years in (32.10)).
Local symbols:

| Symbol | Meaning | Check |
|:--|:--|:--|
| $\operatorname{VaR}_u$, $\operatorname{ES}_u$ | (32.1), over $m$ days when $m$ is named; `\operatorname`, no macro | Portfolios table |
| $j=\lceil uT\rceil$; $j_1$, $j_2$ | the rank of the VaR order statistic; the ranks of (32.5) | §6's $j$, $R_{(j)}$; LM32 has no pmf index |
| $X$, $x$ | the count of exceedances and its value | a random variable; LM32 writes no data matrix (Problem 12 writes $\mathbf R_t$) |
| $n$ | forecast days of a backtest (4,609), the trials of $\operatorname{Bin}(n,u)$ | §6's $n$; Monte Carlo draws are written as numbers, not $n$ |
| $\theta$ | the threshold variable of (32.7) | §6's parameter $\theta$; LM32 has no angle and no other parameter symbol |
| $\mathcal R(\cdot)$ | a risk measure in the coherence axioms | new: Artzner et al.'s $\rho$ is the book's correlation (Open O6) |
| $R_1$, $R_2$ | the returns of two positions (E6's bonds) | asset index, as $R_{i,t}$ |
| $\eta$, $\zeta$ | the constants of the axioms (scale and shift) | LM5's letters (§6) |
| $F_\xi^{-1}(u)$ | the quantile of LM26's standardized innovation: $\Phi^{-1}(u)$, or $\sqrt{(\nu-2)/\nu}\,F_Y^{-1}(u)$ | subscripted; no $z_u$ |
| $\tau$ | years in (32.10) | §6: a span in years when $T$ is a count |

Not used: $\kappa$ (LM5's threshold; the condition number book-wide), $\alpha$ for a level, $\rho$ for a risk measure,
$L$ for a loss (R8's $L_t$; losses are $-R$), a Cholesky $L$ in the main text, $\gamma$ for Magdon-Ismail et al.'s
constant (book-wide a growth rate; (32.10) writes $\sqrt{\pi/2}$), $z_u$, $k$ for a number of standard deviations
(written in words; Problem 10 writes (18.7)'s first line with the shift $a$, a generic constant in a module without
bets, declared), $\hat\sigma_{t+1\mid t}$ (LM26 writes no hat; Open O6).

**Motivating case: "Did any model see 7 April coming?"** (box, about 160 words; 11 sentences, the longest 22 words)

> Wednesday 2 April 2025 was the last session before the Qingming holiday. That evening six models forecast the next
> session's one-day 99% value at risk of the TAIEX total-return index. Their answers ran from 2.66% (a normal law on
> five years of returns) to 4.14% (GARCH with Student-t innovations) [A32-05]. The next session came after four days
> without trading. On Monday 7 April the index fell 9.70%, the worst of its 5,849 days since 2003 [A32-02]. That loss
> was 2.3 to 3.6 times each model's value at risk, and 1.8 to 3.2 times its expected shortfall [A32-05, A32-54]. Over
> the ten sessions from 7 April it lost 8.92% in all [A32-28]. The eight allocation rules of the through case lost
> 5.06% to 8.33% that day, the worst day for seven of them [A32-06]. Was every model wrong, or was the day just rare?
> How precise is a 99% value at risk in the first place? And what does a one-day number say about the fall from a
> peak?

Resolved: (a) the models: §6, E7 (under GARCH-n the loss was a once-in-3.7-million-years day, under GARCH-t once in
32.6 years [A32-27]) and §7 (every model counted it as an exceedance [A32-34]; over 4,609 days no model passes
both tests at the Bonferroni level [A32-32]); (b) precision: §4 (the 1% quantile's SE is 0.145 points by (32.6) for
iid days and 0.256 by the block bootstrap; from 250 returns it has no distribution-free lower bound [A32-19, A32-20,
A32-21]); (c) the path: §8 (the rules' maximum drawdowns run from 18.42% to 33.56%, in 2020 for R1 and in 2022 for
the others [A32-35]).
The case is the sample's extreme, and says so (AUTHORING §8): the ten-session figure is its multi-day check, and the
caption adds that the 10% limit capped many stocks that day (936 listed stocks closed limit-down; SOURCES, TechNews
2025-04-07), so the index return understates the selling.

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | the layer added: LM27's $\sigma_p$ measures typical risk, LM32 measures the tail and the path; case + X1; roadmap; notation and hygiene notes | 340 |
| 2 | Value at Risk and Expected Shortfall {1} | (32.1) at level $u$ and horizon $m$, positive for a loss, "99%" is $u=0.01$; the tail-mean form for continuous $F_R$ by (18.1); (32.2) from $\hat F$ (two-line derivation), equal to the mean of the $uT$ worst returns when $uT$ is whole; E1; X2; E2; LM5's (5.11) and LM15's tail mean are ES (lm05.md:509, lm15.md:469); pitfall: three ES estimators and NumPy's default quantile; 導讀; KC (50 returns) | 560 |
| 3 | Normal, Student-t and Tail Models {1,2,8} | (32.3) from (15.6) and (5.11); (32.4), the $t$'s tail integral derived (Deep Dive); X3; E3; the moments each measure needs (lm05.md:369); Hill-tail VaR and ES in one paragraph ((20.10); Problem 11); the horizon: the $\sqrt m$ rule from (19.7) with iid days, E4 (fat tails against clustering); 導讀; KC ($\sqrt{10}$) | 600 |
| 4 | How Precise Is a Value at Risk? {3} | (32.5) derived (a quantile lies below $R_{(j)}$ when at least $j$ returns do); (32.6) *stated without proof* (Glasserman 2003, (9.7)); E5 (TR23's 1% quantile and median; lm20.md:276); iid and block bootstrap SEs (LM22's tools; dependence doubles the SE); one year of returns; pitfall: a 99% VaR from 250 returns; KC (8.11%) | 480 |
| 5 | Coherence and Expected Shortfall {4,8} | a risk measure's four axioms (Artzner et al. 1999), definition box; normal VaR is subadditive ((16.4): $\sigma_p\le\sigma_1+\sigma_2$); E6 (bonds); ES coherent (Acerbi and Tasche 2002, *stated*); (32.7) derived (Deep Dive: continuous $F$, then $\hat F$, A32-25); the LP of Problem 12 ([[LM29]]); ES 97.5% against VaR 99% (BCBS 2019, MAR33.3); 導讀; KC | 520 |
| 6 | Value at Risk from Volatility Forecasts {5} | quantile equivariance and (32.8); LM26's forecasts into VaR and ES (lm26.md:183); E7 (the 2 April forecasts, VaR, ES, rarity); ten days: (26.4)'s mean reversion and the Monte Carlo of E8; a portfolio by LM12's colouring in one sentence; importance sampling (18.7) for a tail probability, (18.5) and (18.6) in one sentence, Problem 10 (lm18.md:300); jumps → [[LM39]]; KC (log to simple) | 520 |
| 7 | Backtesting Value at Risk {6} | exceedances as Bernoulli($u$) under a correct model; the exact binomial count (LM21); E9 (Basel's table recomputed); X4, X5, X6; independence by LM21's count (Christoffersen 1998 named, O2); 12 tests and Bonferroni; the reading: HS has the right count but clusters, the filtered models do not cluster but exceed too often; 7 April; scoring a quantile against LM26's (26.8), (26.9); pitfall: the 4,609-day zones are Basel's probabilities applied, not Basel's table; 導讀; KC | 600 |
| 8 | Drawdowns of the Rules {7,8} | (32.9): $\mathrm{DD}_t$ (LM1), MDD, the longest spell, $\mathrm{DD}^0_t$; the two definitions (g:92); X7, X8; E10 (R1's episode; R2's MDD against its $\mathrm{DD}^0$); a hypothetical 20% limit; R6 against R8; the path statistic: permutations and the stationary bootstrap, X9, the 2020 atoms; (32.10) stated with its model; pointers to [[LM33]], [[LM34]], [[LM44]]; 導讀; KC | 640 |
| 9 | Risk Measures in Python {2} | `np.quantile(..., method="inverted_cdf")`; (32.2) as a function; `scipy.stats.t.fit`, `t.ppf`, `t.pdf`; `quad` for (32.4); the forecasts from LM26's code; cvxpy for Problem 12 with CLARABEL's tolerances; lab box | 160 |
| — | Summary (7) / Problems (12) / Solutions | | 130 / 400 / 500 |
| | **Total** | | **5,450** |

**Elements.** 10 examples (E1, E2 §2; E3, E4 §3; E5 §4; E6 §5; E7, E8 §6; E9 §7; E10 §8). Knowledge checks:

- §2: 50 returns at $u=1\%$ give $j=\lceil0.5\rceil=1$, so the historical VaR and ES are both the worst return
  [A32-12]: a short sample sees nothing beyond its worst day.
- §3: TR23's ten-session 99% VaR is 10.49% from 5,840 overlapping sums, against $\sqrt{10}$ times the one-day 3.567%
  [A32-11], 11.28% [A32-16]. What does the $\sqrt m$ rule assume, and which way does each failure push? (Fat tails that
  average out push the true value down, clustering pushes it up; E4.)
- §4: with 250 iid returns, the chance that none falls below the true 1% quantile is $0.99^{250}=8.11\%$ [A32-21],
  the first cell of Basel's Table 2; so no order statistic is a 95% lower bound for the 1% quantile.
- §5: under a normal law ES at 2.5% is $2.338\sigma$ and VaR at 1% is $2.326\sigma$ (ratio 1.005) [A32-23]. Why could
  Basel switch measures without changing the normal case's capital, and why does the switch bite on TR23 (historical
  ratio 1.048, $t$ 1.109)?
- §6: a 1% quantile of $-4\%$ for the log return is $e^{-0.04}-1=-3.92\%$ for the simple return [A32-29]. Quantiles
  pass through an increasing map; why does the same step not give the ES?
- §7: HS's 56 exceedances against 46.09 expected; the binomial SD is 6.75, so $z=1.47$ [A32-33]. The count passes;
  what does the count not test?
- §8: (a) R2's MDD is 22.97% but its largest loss from the starting capital is 0.39%, on 8 March 2019, 0.142 points
  of it the purchase cost [A32-40]. Which number answers an investor who started in March 2019? (b) (32.10) gives
  0.793 for $\sigma=20\%$ over ten years [A32-38]; which of its assumptions does R1 break?
- §9: `np.quantile(R, 0.01)` gives −3.5668% by default and −3.5671% with `inverted_cdf` [A32-43].

中文導讀 in §2 (風險值 (value at risk), 預期短缺 (expected shortfall), 分位數 (quantile), 順序統計量 (order
statistic), 歷史模擬法 (historical simulation)), §3 (厚尾 (fat tails), 尾部風險 (tail risk), the $\sqrt m$ rule),
§5 (一致性風險量數 (coherent risk measure), 劣可加性 (subadditivity; O7), 條件風險值 (CVaR), named once as ES's other
name), §7 (回測 (backtest), 二項分布 (binomial distribution), 獨立性檢定 (independence test)), §8 (回撤 (drawdown),
最大回撤 (maximum drawdown), 置換檢驗 (permutation test), 區塊自助重抽法 (block bootstrap)). Deep Dives: §3 "The
Student-t tail mean": $\frac{d}{dy}(1+y^2/\nu)^{-(\nu-1)/2}=-\frac{\nu-1}{\nu}\,y\,(1+y^2/\nu)^{-(\nu+1)/2}$, so
$\int_{-\infty}^{q}y\,f_Y(y)\,dy=-\frac{\nu+q^2}{\nu-1}f_Y(q)$ for $\nu>1$, checked by quadrature [A32-15]. §5 "Why the
minimum is the expected shortfall": for continuous $F_R$ the function of (32.7) is convex with derivative
$1-\Pr(-R>\theta)/u$, zero at $\theta=\operatorname{VaR}_u$, where its value is $\operatorname{ES}_u$
(Rockafellar and Uryasev 2000, Theorem 1); for $\hat F$ it is piecewise linear with kinks at the losses, its slope
$1-\#\{L_t>\theta\}/(uT)$ changes sign at the $j$th largest loss, and its value there is (32.2) (TR23: 4.689% at
3.567% [A32-25]).

**Exhibits.**

- X1 `case` (table, §1): "7 April 2025 against the forecasts of 2 April". Rows: historical (1,231 returns), normal
  (same window), Student $t$ (fit of 1 April), EWMA ($\lambda=0.94$), GARCH normal, GARCH $t$. Columns: 99% VaR (%)
  3.53, 2.66, 3.08, 3.57, 3.83, 4.14 [A32-05]; 99% ES (%) 4.58, 3.06, 4.38, 4.07, 4.39, 5.26 [A32-54]; loss ÷ VaR 2.7,
  3.6, 3.2, 2.7, 2.5, 2.3 [A32-05]; "one day in" (GARCH rows only) 3.7 million years and 32.6 years [A32-27]. Foot rows:
  the loss 9.70% (log −10.20%) [A32-02]; ten sessions 7–18 April −8.92% [A32-28]; the eight rules −5.06% (R7) to
  −8.33% (R4) [A32-06]. Note: forecasts from data through 2 April, out of sample; the return spans four non-trading
  days, and the 10% limit capped many stocks. Source: FinMind `TaiwanStockTotalReturnIndex`, retrieved 18 October 2026;
  LM26's forecasts. Computations: `data/lm32_numbers.py`.
- X2 `tail` (line, `step: true`, §2): the lowest 5% of TR23's returns (the 293 worst [A32-11]) as a histogram of
  losses, bins of 0.25 points from 1.75% to 10.00%, $x$ the loss in % (`fmt: "n2"`), $y$ days. Solid `vline`s at the
  historical VaR 3.57% and ES 4.69%; dashed at the normal's 2.75% and 3.16% [A32-11, A32-13]. Note: the 59 worst days
  lie at or beyond the VaR; ES averages them, weighting the 59th by (32.2). Descriptive, full sample (*In-sample* for
  the normal lines).
- X3 `models` (table, §3): TR23 at $u=$ 0.1%, 1%, 2.5%: historical VaR, ES (32.2) and the mean of the $j$ worst
  (6.31, 7.36, 7.33; 3.57, 4.69, 4.68; 2.65, 3.74, 3.73) [A32-11]; normal (3.67, 4.01; 2.75, 3.16; 2.31, 2.76) [A32-13];
  Student $t$ (7.58, 11.37; 3.37, 5.19; 2.34, 3.73) [A32-14]; Hill at 0.1% and 1% (6.69, 9.23; 3.55, 4.90) [A32-17].
  Note: in-sample fits; the $t$ is LM15's and LM20's ($\nu=3.065$); Hill on the 108 losses of 3% or more, valid for
  $u\le k/T$; the historical 0.1% figures rest on six days.
- X4 `rollvar` (line, date, §7): $-\operatorname{VaR}$ of historical (1), GARCH-t (2) and normal (3), 2 January 2008
  → 8 October 2026, weekly points plus every cited day; `point` annotations for the exceedance days' returns of HS and
  GARCH-t (56 and 77 [A32-31]) and a labelled point "7 Apr 2025" at −9.70% with the three forecasts −3.53, −4.14 and
  −2.66 [A32-05]. Note: out of sample; the X37 thinning; counts 56, 77, 110 against 46.09 expected [A32-31, A32-04].
- X5 `zones` (`bar`, §7): six models' exceedances 56, 110, 69, 103, 102, 77 (`valueLabels`) [A32-31]; dashed `hline`
  "expected 46.09" [A32-04]; `hline`s "yellow from 57" and "red from 73" [A32-30]. Note: the zones are Basel's 1996
  probabilities (95% and 99.99%) applied to 4,609 days, not Basel's 250-day table.
- X6 `backtest` (table, §7): the six models' exceedances and rate, $\Pr(X\ge x)$, zone, exceedances followed by another
  against expected and the p-value, the shares of 250-day windows in yellow and red, the most in one window and its
  last day, the mean VaR [A32-31]; a foot row: the Bonferroni level 0.0042 and which tests it rejects [A32-32]. Note:
  out of sample, 12 tests on the same forecasts.
- X7 `underwater` (line, date, §8): $-\mathrm{DD}_t$ of R1 (1), R3 (2), R6 (3) and R8 (4), 4 March 2019 → 8 October 2026,
  weekly points plus every cited peak, trough and recovery; points at the troughs R1 −23.19% (19 Mar 2020), R3 −19.11%,
  R6 −18.90%, R8 −18.42% (21 Oct 2022) [A32-35]; a dashed `hline` at −20% "hypothetical 20% limit". Note: the chart
  plots $-\mathrm{DD}_t$ (AUTHORING §6); out of sample, net of costs, fixed in advance; R2, R4, R5 and R7 are in X8.
- X8 `rules` (table, §8): R1–R8. Columns: 7 April return (−7.70 … −5.06%) and worst day [A32-06]; VaR 1%, ES 1%, ES
  2.5% [A32-07]; normal VaR 1% [A32-41]; MDD with peak → trough → back [A32-35]; longest spell under water (484–733
  sessions); max $\mathrm{DD}^0$ and its date; $\mathrm{DD}_t$ on 8 October 2026 [A32-35]. Note: the rules'
  out-of-sample returns, 1,851 sessions; the normal column is in-sample; Sharpe ratios are LM33's and net wealth
  LM34's.
- X9 `mddboot` (`scatter`, forest plot, §8): $y$ = R1–R8 (`ticks` 1–8 with `tickLabels`); $x$ MDD in % (`fmt:
  "n1"`). For each rule an unnamed thin grey `lines` entry for the permutation 5–95% range and a thick one for the
  stationary bootstrap's [A32-36, A32-37]; named point series "realized MDD" [A32-35], "permutation median" and
  "bootstrap median". Values cited: R1 23.19 against 17.2 and 21.0 [A32-35]; resampled MDDs at or above the realized
  one, 1,069 and 3,285 of 10,000; R2's 557 under permutation [A32-36, A32-37] (printed as counts: as percentages at one
  decimal several are exact ties). Note: experiments 3 and 4, 10,000 resamples each; block lengths 17–22
  by LM22's rule; in 400 to 1,820 of the 10,000 bootstrap resamples, by rule, the whole March 2020 fall sits in one
  block and is the resample's MDD, so the bootstrap distribution has an atom, and R5's and R6's medians sit on it
  [A32-37].

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
  3.16% [A32-13], the $t$ ($\nu=3.065$, location 0.0997%, scale 0.7761%) 3.37% and 5.19% [A32-14], the data 3.57% and
  4.69% [A32-11]. The normal misses both; the $t$ comes close on VaR but overshoots ES, "too heavy from −5%"
  (lm15.md:461). (32.4) agrees with quadrature to 7.7e-13 [A32-15].
- E4 §3 `horizon`, ten sessions of TR23: 5,840 overlapping compound returns give a 99% VaR of 10.49%; $\sqrt{10}$
  times the one-day VaR gives 11.28%; iid normal log returns give 8.02% [A32-16]; ten days drawn independently from
  TR23's own returns give 8.75% (experiment 7, 100,000 sums, batch SE 0.04) [A32-55]. The daily law's non-normal
  shape (fat tails and skewness, not separated here) raises the iid figure from 8.02% to 8.75%; keeping the real order
  of days, with its clustering, raises it to 10.49%. The $\sqrt{10}$ rule scales a fat-tailed one-day quantile, while
  a sum of ten iid days is already close to its normal counterpart (8.75% against 8.02%), so the rule overstates. R1
  over 20 sessions: 8.66%
  against the $\sqrt{20}$ rule's 9.40% [A32-09]. Neighbouring overlapping sums share nine of their ten days, so 10.49%
  is itself imprecise; the text says so.
- E5 §4 `precision`, TR23's 1% quantile $R_{(59)}=-3.567\%$: by (32.5) the ranks 44 and 75 give −4.016% to −3.425%
  with coverage 0.9587 [A32-18]; (32.6) with the spacing density gives an SE of 0.145 points [A32-19]; the iid
  bootstrap 0.119 (batch SE 0.0014) and the stationary bootstrap with $\ell=145$ 0.256 (0.0020), 2.1 times as large
  [A32-20]. The median (lm20.md:276): $R_{(2925)}=0.0879\%$, interval 0.069% to 0.114% (ranks 2,850 and 3,000, coverage
  0.9502) [A32-18], SE 0.0116 points against LM20's location SE 0.0124 (lm20.md:269) [A32-19]. (32.5) assumes iid days;
  the block bootstrap says clustering doubles the uncertainty of a tail quantile.
- E6 §5 `bonds` (*constructed*): two independent bonds, each losing 60% with probability 0.8% and gaining 2% otherwise.
  At $u=1\%$ one bond's VaR is −2.00% (a gain, since default is rarer than 1%) and its ES 47.60%. Half in each: some
  default has probability 1.59%, above 1%, so the VaR is 29.00% while the halves' VaRs sum to −2.00%; the ES is 29.20%,
  below 47.60% [A32-22]. Diversifying raised VaR and lowered ES.
- E7 §6 `filtered`, the forecasts for 7 April made on 2 April (LM26's): $\sigma_{t+1\mid t}$ 1.5605% (EWMA), 1.7222%
  (GARCH-n), 1.7040% (GARCH-t) a day [A32-26] (lm26.md:39); with the refits' means 0.1020% and 0.1190% and $\nu=6.39$
  [A32-26], (32.8) gives VaR 3.57%, 3.83% and 4.14% [A32-05], and ES 4.07%, 4.39% and 5.26% [A32-54]. The day's log
  return −10.20% [A32-02] is $-5.98$ forecast SDs under GARCH-n, probability $1.1\times10^{-9}$, once in 3.7 million
  years; under GARCH-t $-6.06$, probability $1.2\times10^{-4}$, once in 8,014 sessions, 32.6 years [A32-27]. Both are *Model*
  statements: the law's tail, not the data, decides the answer.
- E8 §6 `mc10`, ten days under GARCH-t from 2 April (experiment 1, 100,000 paths, the 1 April refit, innovations scaled
  to variance 1): the ten-day 99% VaR is 10.5% (batch SE 0.07 points) against $\sqrt{10}$ times the one-day 4.14%
  [A32-05], 13.10%; the realized ten sessions lost 8.92% [A32-28]. Two things pull the model's ten-day figure below the
  rule: the forecast variance reverts toward the fit's unconditional 1.116% a day [A32-26], by (26.4), and a sum of ten
  $t$ innovations is closer to normal than one (E4's effect); the brief does not split the two.
- E9 §7 `basel`: Basel's Table 2 recomputed: for 250 days at 99%, $\Pr(X\le x)$ is 8.11, 28.58, 54.32, 75.81, 89.22%
  for 0–4 and 95.88% at 5, so yellow starts at 5 and red at 10 (99.99%) [A32-30], every cell as BCBS (1996) prints it.
  The same rule gives 9 and 15 for 500 days and 57 and 73 for 4,609 [A32-30]. HS's 56 exceedances are green,
  $\Pr(X\ge56)=0.085$; the $t$'s 69 yellow; the other four red [A32-31].
- E10 §8 `r1dd`, R1's path: MDD 23.19%, from the peak of 6 January 2020 to the trough of 19 March 2020 (45 sessions)
  and back on 13 January 2021 (205 more); its longest spell under water is another episode, 484 sessions from 7 March
  2022 to 5 March 2024; its largest loss from the start is 10.24%, on 19 March 2020 [A32-08]; recovering the MDD needed
  +30.19% (1.17) [A32-40]. R2's MDD is 22.97% (2022), but its loss from the start never exceeded 0.39%, reached on 8
  March 2019, its first week, 0.142 points of it the purchase cost [A32-40, A32-35]: the two definitions answer
  different investors. R6 against R8, its volatility-scaled version (LM31's): on 7 April R8 lost 7.94% against 5.96%,
  1.33 times as much, and its 1% ES is higher (3.16% against 2.86%), yet its MDD is lower (18.42% against 18.90%)
  [A32-39]: the one-day tail and the path rank the two rules in opposite orders.

**Problems plan** (12; MC keys C, A, B, A, B, C; the lab solves 6, 9, 10, 11, 12). Stems state the sample or the
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
6. Derive (32.5) for iid returns with a continuous distribution function; for $T=1{,}000$ and $u=1\%$ find the 95%
   ranks and the coverage: 4 and 18, 0.9761, around the point $R_{(10)}$ [A32-49]. Python part: the ranks by
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
    $1.146\times10^{-9}\pm2.9\times10^{-11}$ against the exact $1.091\times10^{-9}$; plain draws would expect
    0.000011 tail draws, the shifted ones get 4,927, and the variance falls by a factor $1.34\times10^8$ [A32-53].
11. Python, Hill-tail VaR (LM20's $x_0=3\%$, $k=108$): $\hat\alpha=3.63$; VaR and ES at 1% 3.55% and 4.90%, at 0.1%
    6.69% and 9.23%, against the historical 3.57%, 4.69%, 6.31%, 7.36% [A32-17]; why $u$ must stay below $k/T$.
12. Python, minimum ES (*In-sample*, citing LM29): on the through case's first window (504 rows, 13 February 2017 → 27
    February 2019), $u=2.5\%$, long-only weights summing to 1, solve (32.7) as a linear program in cvxpy with CLARABEL
    (tolerances 1e-12) and check with HiGHS: weights 0.078, 0.203, 0.398, 0.290, 0.030, ES 0.857%, $\theta^*=0.693\%$
    = VaR; R3's ES 0.880% and R1's 1.303% on the same rows [A32-24].

**Lab parts** (`build/make_lab32.py`; reads only its `data/`: `taiex_tr.csv` (TR23, as LM23's lab), the rules' net
wealth paths and the wealth frame (derived files, O4), LM26's forecasts or the means to refit them (O4), and three T5S
days (O4)): 1 data, conventions, the sample counts; 2 historical VaR and ES, (32.2) against the two count means, E1,
E2, X2, `np.quantile`'s methods; 3 normal, $t$ and Hill (Problem 11), (32.4) by quadrature, E4 with experiment 7; 4
precision: (32.5), (32.6), experiments 5 and 6 (E5), Problem 6; 5 coherence: E6 and Problem 7 exactly, (32.7) on TR23,
Problem 12; 6 filtered VaR and ES: E7, A32-54's quadrature, E8 (experiment 1), Problem 10 (experiment 2), a portfolio
VaR by colouring with LM12's Cholesky factor, checked against (32.3) with $\sigma_p$; 7 backtests: X4–X6, E9, Problems
8 and 9; 8 drawdowns: X7–X9 with experiments 3 and 4, the atoms, E10; the intraday drawdowns of 7 April 2025, 5 August
2024 and 19 March 2020 from T5S (−9.80%, −8.57% and −7.54% lows, per-day statistics only) [A32-44]. Extension
(*Out-of-sample*, one variant declared in advance): rerun the HS and normal backtests with a 250-return window, Basel's
minimum one year (BCBS 1996b, B.4(d)), and compare the counts with X6; the closing sentence says that the second window
is a second trial on the same data, which LM34 treats. Labs write plain "LM29", never `[[LM29]]`.

**Cross-module tags.**

- (32.1) $\operatorname{VaR}_u:=-F_R^{-1}(u)$, $\operatorname{ES}_u:=-\frac1u\int_0^uF_R^{-1}(v)\,dv$, for the
  $m$-day simple return $R$, $0<u<1$, $\E\lvert R\rvert<\infty$ for ES; for continuous $F_R$,
  $\operatorname{ES}_u=-\E[R\mid R\le F_R^{-1}(u)]$ (LM35, LM39, LM44).
- (32.2) $\operatorname{VaR}=-R_{(j)}$ and
  $\operatorname{ES}=-\frac1u\big[\frac1T\sum_{i<j}R_{(i)}+(u-\frac{j-1}{T})R_{(j)}\big]$, $j=\lceil uT\rceil$: (32.1)
  under $\hat F$ (every module that prints a historical ES; LM34, LM35).
- (32.3) normal: $\operatorname{VaR}_u=-\mu-\sigma\Phi^{-1}(u)$, $\operatorname{ES}_u=-\mu+\sigma\varphi(\Phi^{-1}(u))/u$
  (LM35, LM39).
- (32.4) $R=\mu+\sigma\sqrt{(\nu-2)/\nu}\,Y$, $Y\sim t_\nu$, $\nu>2$, $q=F_Y^{-1}(u)$:
  $\operatorname{VaR}_u=-\mu-\sigma\sqrt{(\nu-2)/\nu}\,q$,
  $\operatorname{ES}_u=-\mu+\sigma\sqrt{(\nu-2)/\nu}\,\frac{(\nu+q^2)f_Y(q)}{(\nu-1)u}$ (LM39).
- (32.5) for iid returns with continuous $F_R$ and $j_1<j_2$:
  $\Pr\big(R_{(j_1)}\le F_R^{-1}(u)<R_{(j_2)}\big)=\Pr(j_1\le X\le j_2-1)$, $X\sim\operatorname{Bin}(T,u)$ (in-module;
  LM45 may cite).
- (32.6) $\operatorname{SE}\big(R_{(\lceil uT\rceil)}\big)\approx\sqrt{u(1-u)/T}\,/\,f_R\big(F_R^{-1}(u)\big)$ for iid
  returns with a positive continuous density at the quantile, large $T$, *stated without proof* (Glasserman 2003, (9.7))
  (in-module).
- (32.7) $\operatorname{ES}_u=\min_\theta\big\{\theta+\tfrac1u\E[(-R-\theta)^+]\big\}$, attained at
  $\theta=\operatorname{VaR}_u$; convex in $\theta$, and jointly convex with the weights when $R=\mathbf w^{\top}\mathbf
  R_t$ (LM44; Volume VIII's risk-limited sizing).
- (32.8) $r=g+\sigma_{t+1\mid t}\xi_{t+1}$ with $\xi$ iid of quantile $F_\xi^{-1}(u)$:
  $\operatorname{VaR}_u=1-\exp\big(g+\sigma_{t+1\mid t}F_\xi^{-1}(u)\big)$ (log returns in decimals) (LM35, LM39).
- (32.9) $\mathrm{MDD}:=\max_t\mathrm{DD}_t$ with LM1's $\mathrm{DD}_t$; $\mathrm{DD}^0_t:=\max(0,1-W_t/W_0)$; a spell
  under water runs from a peak to the first date with $W_t$ at or above it (LM34, LM35, LM44).
- (32.10) for $\ln W_t$ a Brownian motion with zero drift and volatility $\sigma$ a year, the expected maximum drop of
  $\ln W$ over $\tau$ years is $\sqrt{\pi/2}\,\sigma\sqrt\tau$, *stated without proof* (Magdon-Ismail et al. 2004)
  (LM44).

**Pitfalls to pre-empt.**

- Signs and levels: VaR and ES are positive for a loss; "99%" is $u=0.01$; a VaR can be negative (E6). Never write
  $\alpha$ for the level (LM32's $\alpha$ is the tail index).
- The quantile rule: `np.quantile`'s default `linear` differs from $R_{(\lceil uT\rceil)}$ (A32-43); pass
  `method="inverted_cdf"` in every printed snippet.
- Three ES estimators: (32.2), the mean of the $\lceil uT\rceil$ worst and the mean of the $\lfloor uT\rfloor$ worst
  differ little on TR23 (4.689% against 4.679% at 1%) and a lot on small samples (E1); the book uses (32.2).
- Log against simple: quantiles pass through $e^r-1$, means do not; the ES of a log-return model is not
  $1-e^{-\text{log ES}}$ (A32-54's formula).
- Moments: name the moment each measure needs (PITFALLS §7): VaR none, ES a first ($\nu>1$, $\alpha>1$), the normal
  fit a variance; TR23's $t$ has no fourth moment, so no kurtosis-based SE applies to it.
- The $\sqrt m$ rule assumes iid days; on TR23 it overstates the ten-day VaR while clustering understates the iid
  figures (E4, E8); never call either effect the cause without the comparison of A32-55.
- Precision: a 99% VaR from 250 returns is the third worst; its distribution-free interval has no lower end (A32-21);
  dependence doubles a tail quantile's SE (A32-20).
- Backtests: twelve tests on the same forecasts (Bonferroni); the 4,609-day zones apply Basel's probabilities, not its
  table; exceedance counts in overlapping 250-day windows are dependent (X6's shares are descriptive); the guard and its
  smallest margin are printed.
- 7 April spans four non-trading days, and the 10% limit capped many stocks (936 listed limit-down; SOURCES): a one-day
  forecast met a five-calendar-day gap, and the index return understates the selling (PITFALLS §7, limit days).
- Drawdowns: $\mathrm{DD}_t$ against the running peak including $W_0$, $\mathrm{DD}^0_t$ against the start; the rules'
  paths start at the cash of 1 before the first purchase, so the purchase cost is a drawdown (R3, R5, R7, R8 reach
  their largest $\mathrm{DD}^0$ on their first day, A32-35); an underwater chart plots $-\mathrm{DD}_t$ and says so.
- The block bootstrap of an MDD has atoms (a short crash fits in one block): report the atom; a median on it has no
  batch SE (A32-37).
- (32.10) is for log wealth, zero drift and constant $\sigma$; $1-e^{-0.793}=54.7\%$ is the fall that equals the mean
  log drawdown, not the mean percentage drawdown (Jensen, LM14's (14.10)).
- Ownership: the rules' VaR, ES and drawdowns are LM32's; their Sharpe ratios LM33's, net wealth and costs LM34's,
  scenario losses LM35's, exposures LM31's; LM26 owns the variance forecasts, LM32 their VaR.
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
  Monte Carlo, likelihood-ratio tests and intraday drawdowns go to problems and the lab.
- g:87–90, failure forms: LM32 shows the drawdown-limit failure on the same rules: a hypothetical 20% limit is breached
  by R1, R2 and R4 (23.19%, 22.97%, 33.56% [A32-35]); weak growth is LM34's, funding and ruin LM35's.
- g:92, define drawdown: $\mathrm{DD}_t$ and $\mathrm{DD}^0_t$, with R2 as the example where they differ (E10).
- g:93, a probability bound keeps its model: (32.10) is stated with its model (log wealth, zero drift, constant
  $\sigma$) and applied only to a hypothetical $\sigma$.
- g:94, wealth ≤ 0: no rule's path reaches it (asserted), so no truncation arises; the text says it was checked.
- g:111, fixed in advance: the backtest's window, refits and models are LM26's, fixed before LM32; the twelve tests are
  counted; the lab's 250-return window is declared as one more trial.
- g:124, taught, practised, assessed: the map under "Outcomes".

**Stage 4 for earlier modules.**

- `leads` gain 32 in lm01.md:6 ((1.17), $\mathrm{DD}_t$), lm05.md:6 ((5.11); on the Stage 4 list), lm10.md:6 ((10.4)),
  lm21.md:6 (the exact binomial tests, (21.6)) and lm22.md:6 ((22.3), the block rule). lm12, lm14, lm15, lm16, lm18,
  lm19, lm20 and lm26 already list 32; LM12 keeps it through §6's colouring sentence (O9).
- lm04.md:46–50 and 510 print maximum drawdowns as negative numbers (−93.3%); with §6's $\mathrm{DD}\ge0$ and LM32's MDD
  they become 93.3% (the column header stays "Maximum drawdown"). Optional and minor; the editor decides.
- No other wording change: lm20.md:276's "its standard error is [[LM32]]'s" is kept by E5; lm18.md:300's "applies these
  estimators to value at risk" by §6 and Problem 10 (a tail probability at a loss level is the inverse question of a
  VaR, and the lab also reads a VaR off the weighted draws, O8).

**Sources** (verified 2026-10-24 unless marked; paraphrased, nothing quoted beyond a phrase):

- Artzner, P., F. Delbaen, J.-M. Eber and D. Heath (1999). "Coherent Measures of Risk." *Mathematical Finance* 9 (3):
  203–228. DOI 10.1111/1467-9965.00068. Crossref (rechecked by the drafter: authors, title, 9(3), 203–228, July 1999).
  The four axioms (translation invariance, subadditivity, positive homogeneity, monotonicity) read in the authors'
  ETH preprint of 22 July 1998 (the survey's download; Axiom T and Axiom S read there). Cited for the definition only;
  the journal's numbering not compared, so no axiom or theorem number is printed.
- Acerbi, C. and D. Tasche (2002). "On the coherence of expected shortfall." *Journal of Banking & Finance* 26 (7):
  1487–1503. DOI 10.1016/S0378-4266(02)00283-2. Crossref rechecked. Definition 2.6 (the tail mean and ES, the form of
  (32.2)), its independence of the quantile convention (Corollary 4.3, by its statement there) and Proposition 3.1
  (coherence) read in arXiv cond-mat/0104295v5 (2 May 2002); the journal's numbering not compared, so the text cites
  "Acerbi and Tasche (2002)" without numbers.
- Acerbi, C. and D. Tasche (2002b). "Expected Shortfall: A Natural Coherent Alternative to Value at Risk." *Economic
  Notes* 31 (2): 379–388. DOI 10.1111/1468-0300.00091. Crossref rechecked. The sample estimator that averages the
  $\lfloor nu\rfloor$ worst outcomes read in arXiv cond-mat/0105191v1 (9 May 2001); used only for E1's third reading.
- Rockafellar, R. T. and S. Uryasev (2000). "Optimization of conditional value-at-risk." *Journal of Risk* 2 (3):
  21–41. DOI 10.21314/jor.2000.038. Crossref rechecked. Theorem 1 (the minimum formula, VaR as the left end of the set
  of minimizers) and Theorem 2 (joint minimization) read in the working paper of 5 September 1999; it assumes a
  density, so the Deep Dive derives the $\hat F$ case itself.
- Rockafellar, R. T. and S. Uryasev (2002). "Conditional value-at-risk for general loss distributions." *Journal of
  Banking & Finance* 26 (7): 1443–1471. DOI 10.1016/S0378-4266(02)00271-6. Crossref rechecked; **text not read**, not
  relied on, not cited unless Stage 2 reads it.
- Kupiec, P. H. (1995). "Techniques for Verifying the Accuracy of Risk Measurement Models." *Journal of Derivatives* 3
  (2): 73–84. DOI 10.3905/jod.1995.407942. Crossref rechecked (issued 30 November 1995). **Text not read**: the FEDS
  95-24 version could not be downloaded (both Federal Reserve URLs tried returned an HTML page); its test statistic
  and table are not relied on (O2).
- Christoffersen, P. F. (1998). "Evaluating Interval Forecasts." *International Economic Review* 39 (4): 841–862. DOI
  10.2307/2527341. Crossref rechecked: first page 841 only; the end page 862 rests on the survey's IDEAS and JSTOR
  citation. **Text not read**; its tests are not relied on (O2).
- Basle Committee on Banking Supervision (1996a). *Supervisory framework for the use of "backtesting" in conjunction
  with the internal models approach to market risk capital requirements.* January 1996 (BCBS 22). Read in the BIS PDF
  (the survey's download, reread by the drafter): §III's three zones, the 95% and 99.99% cumulative-probability rule,
  Table 2's cells (8.11% … 99.99%), all reproduced by A32-30.
- Basle Committee on Banking Supervision (1996b). *Amendment to the Capital Accord to incorporate market risks.* January
  1996 (BCBS 24). Part B.4 "Quantitative standards", (a)–(d): daily VaR, a 99th percentile one-tailed, a ten-day
  holding period with square-root-of-time scaling allowed, at least one year of observations (reread by the drafter in
  the survey's copy of the BIS PDF).
- Basel Committee on Banking Supervision (2019). *Minimum capital requirements for market risk.* January 2019, revised
  February 2019 (d457). MAR33.3: ES at a 97.5th percentile, one-tailed (reread by the drafter in the BIS PDF). The 1996
  documents spell the committee "Basle".
- Magdon-Ismail, M., A. F. Atiya, A. Pratap and Y. S. Abu-Mostafa (2004). "On the maximum drawdown of a Brownian
  motion." *Journal of Applied Probability* 41 (1): 147–161. DOI 10.1239/jap/1077134674. Crossref rechecked. The
  zero-drift expected maximum drawdown $2\gamma\sigma\sqrt T$ with $\gamma=\sqrt{\pi/8}\approx0.6267$ is eq. (16) of the
  authors' preprint dated 1 September 2003 (read by the drafter); the journal's equation number not compared, so the
  text cites the paper without it.
- Glasserman (2003), §9.1.2 and (9.7) (SOURCES, LM18's closing check): the asymptotic variance of a quantile estimate
  needs the density at the quantile; cited for (32.6).
- In SOURCES and used through earlier modules: Hill (1975) (LM20), Politis and Romano (1994) and the block rule's
  sources (LM22), the RiskMetrics document's $\lambda=0.94$ and the GARCH sources (LM26), TechNews 2025-04-07 (936
  listed stocks limit-down).
- Not cited (checked by the survey but not needed): Jorion (2007), McNeil, Frey and Embrechts (2015), Chekhlov,
  Uryasev and Zabarankin (2005).

**Chinese terms** (AUTHORING §1; English in parentheses at first use in each box):

- From `plans/vol-5.md`'s list: 風險值 (value at risk), 條件風險值 (CVaR, named once), 歷史模擬法 (historical
  simulation); the book's forms 預期短缺 (expected shortfall; LM5), 回撤 (drawdown; LM1), 最大回撤 (maximum
  drawdown), 回測 (backtest), 尾部風險 (tail risk), 一致性風險量數 (coherent risk measure).
- Looked up on 樂詞網 on 2026-10-24 (the first drafter's all-listings phrase search, `lm32/terms/`):
  - value at risk (VaR): 風險值 (統計學名詞); conditional value at risk: 條件風險值 (統計學名詞); tail value at risk:
    尾端風險值 (統計學名詞, not used).
  - expected shortfall: 期望損失 (統計學名詞), 預期損失 (管理學名詞); the book keeps LM5's 預期短缺 (lm05.md:785; one
    term per concept).
  - order statistic: 順序統計量 (數學名詞), as LM14; quantile: 分位數 (數學名詞, 統計學名詞); sample quantile: 樣本分位數.
  - subadditivity: 劣可加性 (數學名詞); finite subadditivity: 有限[的]次加性；有限[的]劣加性. The shared decision prints
    劣加性 (from 劣加性函數); the entry for the term itself is 劣可加性 (O7).
  - risk measure: 風險量數 (統計學名詞); "coherent risk measure": no entry, so 一致性風險量數 stays the book's form.
  - backtesting: 回溯測試 (管理學名詞); the book keeps 回測 (SOURCES, Volume V line).
  - historical simulation method: 歷史模擬法 (管理學名詞).
  - binomial distribution: 二項分布 (統計學名詞), as LM15 and LM17; binomial test: 二項檢驗 (數學名詞, not used).
  - independence test: 獨立性檢定 (數學名詞).
  - permutation test: 置換檢驗 (數學名詞).
  - importance sampling: 重要抽樣 (統計學名詞), as LM18 (not in a box here).
  - no entry: drawdown, coherent risk measure, tail risk, exceedance, positive homogeneity, translation invariance;
    the axioms' names stay in English in the text, and "exceedance" is glossed 超過 VaR 的日子 in the §7 box.

**Open before Stage 2** (each with the drafter's recommendation and evidence):

- **O1. The historical ES estimator** (the shared decision leaves it to this brief). Recommendation: (32.2), Acerbi and
  Tasche's tail mean of $\hat F$, in every module. Evidence: it is (32.1) applied to the book's own empirical
  distribution and independent of the quantile convention (their Corollary 4.3); it is continuous in $u$ (the widget's
  slider moves smoothly); Rockafellar and Uryasev's minimum on $\hat F$ equals it exactly (4.689045% on TR23 at 1%
  [A32-25]), so Problem 12's LP and the estimator agree; it equals the mean of the $uT$ worst when $uT$ is whole. The
  simpler mean of the $\lceil uT\rceil$ worst is close on TR23 at 1% (4.679% against 4.689% [A32-11]) but not in E1
  (1.65% against 1.93% [A32-10]); the text shows it once as an approximation.
- **O2. Kupiec and Christoffersen were not read.** The spine names "Kupiec's test" and "Christoffersen's independence
  test stated"; neither paper's text is in hand (Kupiec's FEDS PDF did not download; both journals are paywalled).
  Recommendation: the text's coverage test is LM21's exact binomial tail, introduced as the count test on which Basel's
  1996 framework rests (BCBS 1996a, read), and its independence check is LM21's exact count of consecutive exceedances
  (lm21.md:207); Kupiec (1995) and Christoffersen (1998) are cited by name, for the likelihood-ratio forms, only if
  Stage 2 reads them (the editor's or the owner's library access); otherwise they are left out. The anchors depend on
  neither paper.
- **O3. The backtest window and the bootstrap's block length** (the spine leaves both to the brief). Recommendation:
  LM26's 1,231 returns, fixed before LM32, so that all six models forecast the same 4,609 days [A32-04]; Basel's
  one-year minimum (BCBS 1996b) appears as the lab's declared extension, not as a second text result. For the
  drawdown bootstrap, LM22's rule per rule (17–22 days [A32-37]), stated as a rule, not the right length; the atoms of
  the March 2020 fall (400 to 1,820 of 10,000 resamples [A32-37]) are reported in X9's note, since they make a batch SE
  of the median meaningless for R5 and R6.
- **O4. The lab's data** (shared decision "Labs"). The lab needs each rule's net wealth path (not only weights and
  the wealth frame; LM31's O3 asks the same), LM26's daily forecasts (or the time to refit GARCH 226 times for each
  innovation law; LM26's lab does it), and three T5S days for the intraday drawdowns. Recommendation: `make_lab_data.py` writes the rules' net
  wealth paths and LM26's six forecast series as derived files for the labs that need them, and copies the three raw
  T5S days into LM32's `data/` (git-ignored, per-day statistics only in the notebook's output).
- **O5. Two new anchors and six revised rows.** A32-54 (the six models' ES forecasts for 7 April) gives X1 and the
  case their ES column, and A32-55 (ten iid sessions) separates fat tails from clustering in E4, which PITFALLS §7
  requires before a cause is named. A32-20, A32-35, A32-36, A32-37, A32-40 and A32-47 changed, and seven rows now
  check every printed precision for rounding flags (anchors' Status). Recommendation: accept them; no other module's
  number moves.
- **O6. Notation.** (a) A generic risk measure: Artzner et al. write $\rho$, the book's correlation; the brief proposes
  $\mathcal R(\cdot)$ (unused book-wide), or the axioms stated for $\operatorname{VaR}_u$ and $\operatorname{ES}_u$
  directly. (b) AUTHORING §6's Portfolios row writes $\hat\sigma_{t+1\mid t}$ "(LM26)", but LM26 writes
  $\sigma_{t+1\mid t}$ without a hat (lm26.md:99, and §6's Volume IV row); LM32 follows LM26, and the row should drop the
  hat (LM31's brief raises the same point).
- **O7. 劣加性 or 劣可加性.** The shared decision prints 劣加性 "(the mathematics listing's 劣加性函數)"; 樂詞網's entry for
  "subadditivity" itself is 劣可加性 (數學名詞), and 劣加性 appears only inside "finite subadditivity"'s alternatives.
  Recommendation: 劣可加性, the term's own entry; a change to the shared list, so the editor decides.
- **O8. Importance sampling and VaR** (lm18.md:300). Problem 10 estimates a tail probability at a given loss, the
  inverse of a VaR. Recommendation: keep it (it answers "how rare was 7 April", the case's question), and let the lab
  read a VaR at a far level off the same weighted draws, numbers produced by the lab; no anchor needed.
- **O9. Leads and plan promises.** LM12's published leads list 32: kept by one sentence of §6 (colouring for a
  portfolio Monte Carlo) and the lab part, as the plan promised (`plans/vol-2.md:578`). (16.10), which
  `plans/vol-3.md:1543` gives LM32 and LM35, is left to LM35 (a correlation break in a crash is a stress topic).
  Recommendation: as stated; the editor may instead drop 32 from LM12's leads at Stage 4 and the sentence here.
- **O10. The 4,609-day traffic light.** Basel's table is for 250 days; X5 and X6 apply its probabilities (95%,
  99.99%) to 4,609 days [A32-30]. Recommendation: keep, labelled "Basel's rule applied to 4,609 days", because a single
  250-day table would discard most of the sample; X6's 250-day window shares show Basel's own table in use.

## LM33 The Statistics of the Sharpe Ratio

Stage 1 brief, drafted 2026-10-24 from the editor's spine (`plans/vol-5.md`, "### LM33 The Statistics of the Sharpe
Ratio") and the shared decisions above it. Every number carries its anchor ID at first appearance in a passage;
`data/vol6_anchors_lm33.py` prints them all (64 rows, `## LM33` of `plans/vol-6-anchors.md`; draft in
`lm33_anchors.md`). Numbers quoted from published modules carry their file:line. Statistics another module owns
("Owners", shared decision "Through case") are echoed with that module's name.

**Prereq:** `[4, 16, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 29, 30, 31]`. What each supplies (tags rechecked in
`src/`; LM27–LM31 are briefs, so their results are named, not tagged):

- LM4: the Sharpe ratio $(\mu-r_f)/\sigma$ and its promise (lm04.md:120); the quadratic fraction (4.3)
  $f_q\approx\mu/\sigma^2$ and the pitfall's $f^*\approx\mathrm{SR}/\sigma$ (lm04.md:561); "size from a haircut
  estimate, then take a fraction of Kelly" (lm04.md:563).
- LM16: (16.3) the variance of a weighted sum, for the variance of a difference of two correlated estimates (§6,
  problem 6); (16.7) normal linear maps (problem 8; experiment 2 colours $\mathcal N_8(\mathbf 0,C)$ draws by it).
- LM18: (18.2) the standard error of a Monte Carlo mean (experiment 2); the standard error of a proportion,
  $\sqrt{\hat p(1-\hat p)/n}$ (lm18.md:151), for bootstrap p-values.
- LM19: (19.3) sample skewness and raw kurtosis, divisor $T$; (19.5) $\hat\rho_k$; (19.7) the variance of an
  $m$-period sum; (19.9) $\mathrm{SR}(m)$; TR23's daily 0.0517 and annual 0.81, and the log-return 0.715 that (19.9)
  turns into 0.650 (lm19.md:370, 372); the pointer to Lo (2002) (lm19.md:359).
- LM20: (20.2) the standard error of a mean, annualized; (20.8) the delta method; (20.9) for the Sharpe ratio, with
  raw kurtosis; $\operatorname{SE}(s)\approx\sigma\sqrt{(\operatorname{Kurt}-1)/(4T)}$ (lm20.md:362); TR23's 0.0517
  (SE 0.0132) and 0.81 (SE 0.207, interval 0.40 to 1.22) (lm20.md:390, 401); the pitfall that a plug-in standard error
  needs the moments it plugs in (lm20.md:409).
- LM21: (21.1) the t-stat and the identity $\sqrt T\bar R/s=\mathrm{SR}\sqrt\tau$ (lm21.md:172); (21.2) one- and
  two-sided p-values; (21.3) the statistic for two independent samples (the contrast of §6); (21.4) power and the years
  a Sharpe ratio needs, 11.9 years for TR23 (lm21.md:177, 183); (21.6) Bonferroni; (21.7) Holm; (21.9)
  $\Pr(\max_iZ_i\le x)=\Phi(x)^m$; the rule that every test reports how many ran on the same data (lm21.md:284).
- LM22: (22.1) the bootstrap standard error; (22.2) percentile and basic intervals; (22.4) the bootstrap p-value of a
  t-stat; circular blocks (lm22.md:192); the book's block-length rule (lm22.md:254); TR23's Sharpe standard errors by
  scheme, 0.205, 0.247, 0.244, 0.233 (lm22.md:216–219).
- LM23: (23.7) Newey–West with Bartlett weights; the lag rule $\ell=\lfloor4(T/100)^{2/9}\rfloor$ (lm23.md:223); the
  pointer to LM33 (lm23.md:266).
- LM24: Bayes' rule (24.1) and the normal posterior (24.3); under a flat prior the posterior probability of a negative
  mean equals the one-sided p-value to the printed digits, yet one is a statement about $\mu$ and the other about the
  data (lm24.md:203–205). LM33 reads PSR in that light (§5, one sentence).
- LM25: (25.4) the robust standard error of $\hat\rho_k$; (25.6) the variance-ratio t-stat with iid and robust
  standard errors.
- LM27–LM31 (briefs above): the eight rules (R1 and R2, LM27; R3 and R4, LM28–LM29; R5, LM30; R6–R8, LM31), the wealth
  recursion and the cost model (LM27); the realized volatilities of R1, R3 and R5 (LM30) and of R6–R8 (LM31), echoed
  in the checkpoint table.

**Leads:** `[34, 45]`: LM34 cites the intervals, (33.4) and (33.6) for its walk-forward comparison and re-teaches
none of them (shared decision, "LM34 against the Research hygiene page and LM21"); LM45 sizes from an uncertain
Sharpe ratio, citing (33.2), (33.3) and (33.7) (spine, "Leaves").

**Forward links honoured.**

| Earlier text | Promise | Kept in |
|:--|:--|:--|
| lm04.md:120 | "[[LM33]] studies its estimation" | §2–§4: the standard error, dependence, annualization |
| lm04.md:563 | backtests overstate Sharpe ratios: size from a haircut, then a fraction of Kelly | §8, E9: the haircut of R2 and its effect on (4.3)'s fraction; sizing proper to LM45 |
| lm19.md:359 | Lo (2002): the $\sqrt{12}$ rule's conditions; "[[LM33]] gives the Sharpe ratio's standard error when returns are correlated" | §3 ((33.1)) and §4 (Lo's correction on 90 months) |
| lm20.md:407 | "The Sharpe ratio of dependent returns is [[LM33]]'s", since $\sqrt A$ is exact only for log returns on uncorrelated days | §3, §4, E5; KC §4 |
| lm21.md:373 | "[[LM33]] deflates a Sharpe ratio for the number of trials" | §7, E8: DSR at $n=8$ and $n_{\mathrm{eff}}$ |
| lm22.md:141 | standard errors for dependent returns, PSR, DSR and Ledoit and Wolf's (2008) test are [[LM33]]'s | §3, §5, §6, §7 |
| lm23.md:266 | "[[LM33]] applies the long-run variance to a Sharpe ratio" | §3, (33.1) with (23.7) and the book's lag |
| lm24.md:376 | "Haircuts for a backtest's Sharpe ratio are [[LM33]]'s" | §8, (33.7) |
| research-hygiene.md:7 (中文), 29, 62 | LM21 and LM33 measure the risk that the best version is lucky; LM33 covers the Probabilistic and Deflated Sharpe ratios | §5, §7; the hygiene note counts the eight rules |

The grep of `src/*.md` and `src/pages/*.md` for `LM33` finds exactly these 11 lines, and `build/make_lab*.py` has
none; the spine missed nothing. Leads that already list 33: LM16, 19, 20, 21, 22, 23, 24, 25; LM4 and LM18 gain it
at Stage 4.

**Outcomes** ("After this module you should be able to:"; the level in brackets is the brief's, not the page's):

1. [C] compute a Sharpe ratio's standard error and interval from (20.9) with raw kurtosis, and name the moments it needs
2. [D] derive the standard error of a Sharpe ratio under dependent returns from the delta method and the long-run variance, and check its sensitivity to the lag
3. [C] annualize the Sharpe ratio of autocorrelated monthly returns with Lo's correction, and judge whether the data support the correction
4. [D] derive the probabilistic Sharpe ratio and the minimum track record length, and relate them to the power calculation for a mean
5. [C] test the difference of two Sharpe ratios with a HAC standard error and a studentized block bootstrap, and correct a family of such tests
6. [C] deflate the best of $n$ Sharpe ratios for the number of trials, and estimate an effective number of trials for correlated rules
7. [U] explain how a haircut adjusts a backtest's Sharpe ratio for multiple testing, and what it implies for position sizing
8. [C] compute these statistics in NumPy and check them against SciPy and arch with every option passed explicitly

| Outcome | Taught | Practised | Assessed |
|:--|:--|:--|:--|
| 1 | §2 | E1, E2 | KC §2; problems 1, 2 |
| 2 | §3 and its Deep Dive | E3, E4 | KC §3; problem 11 |
| 3 | §4 | E5 | KC §4; problems 5, 10 |
| 4 | §5 | E6 | KC §5; problems 3, 7 |
| 5 | §6 | E7 | KC §6; problems 6, 12 |
| 6 | §7 and its Deep Dive | E8 | KC §7; problems 4, 8 |
| 7 | §8 | E9 | KC §8; problem 9 |
| 8 | §9 | the lab | KC §9; problems 10–12 |

**Owns.** The rules' Sharpe ratios, their intervals and their tests (shared decision "Owners"), and with them the
uncertainty of each rule's mean excess return and volatility in the checkpoint table (Volume IV's checkpoint, guidance
g:43). The methods: (20.9) applied with raw kurtosis to the eight rules; the HAC standard error (33.1), the delta method
(20.8) with (23.7)'s long-run covariance and the book's lag; Lo's (2002) annualization of autocorrelated returns,
applied through (19.9), with (25.6) for the noise of the correction; the probabilistic Sharpe ratio (33.2) and the
minimum track record length (33.3) (Bailey and López de Prado 2012), one-sided, with $\sqrt{T-1}$ and the "1 +" term,
against (21.4); the expected maximum $\E Z_{(n)}$ (33.4) from (21.9) and the deflated Sharpe ratio (Bailey and López de
Prado 2014), the track record after $n$ trials (33.5), an effective number of trials (experiment 2); Ledoit and Wolf's
(2008) difference of two Sharpe ratios (33.6), HAC and a studentized circular block bootstrap, on the seven pairs
R2–R8 against R1, with Holm; haircuts (33.7) (Harvey and Liu 2015) by Bonferroni, Holm and independent tests; the
haircut's effect on (4.3)'s fraction (one paragraph). Values owned: every A33 anchor except the echoed numbers of LM19,
LM20, LM21 and LM22 (file:line in the anchors) and the volatilities LM30 and LM31 own (echoed).

**Leaves.** Testing the best rule of a search on later data, White's reality check, PBO and gross against net Sharpe
ratios → LM34 (one sentence each in §6 and §7). Sizing from an uncertain Sharpe ratio (bootstrap Kelly, shrinkage of
the fraction) → LM45 (§8, one sentence). Bayesian shrinkage of a Sharpe ratio toward a prior → LM24's tools, one
sentence (§5). Ledoit and Wolf's calibration of the block size (their Algorithm 3.1), their prewhitened
quadratic-spectral kernel and the GMM form of Lo's standard error → named once, not used (§6, §3). The test of one
Sharpe ratio against a benchmark index (the information ratio) → not in the book, one sentence (§6). Harvey and Liu's
false-discovery haircut (their BHY version) → named once (§8); LM21 owns the false discovery rate.

**Uses before taught** (one sentence each in the text):

- §6: "Testing the best rule of a search on later data, and White's (2000) reality check of a whole search, are
  [[LM34]]'s; this section compares two rules fixed in advance."
- §7: "The probability that a search's best in-sample configuration is overfit, PBO, is [[LM34]]'s."
- §7: "Bailey and López de Prado derive their approximation of $\E Z_{(n)}$ from extreme-value theory; the module states
  it without proof and computes the exact integral instead."
- §8: "Choosing a position size from an uncertain Sharpe ratio is [[LM45]]'s; here the haircut only rescales (4.3)'s
  fraction."

**Data role.**

- **E5's wealth frame, the through case** (shared decisions, "Data" and "Through case"). `data/vol5_series.py`'s
  `frames("E5")` reads `data/processed/vol5_frames.parquet` (FinMind `TaiwanStockPrice`, `TaiwanStockDividendResult`
  and `TaiwanStockSplitPrice`, registered 2026-10-24); `data/vol5_rules.py` gives the eight rules (`signals`,
  `wealth_path`, `summary`), net of costs; no rule is re-implemented. The wealth paths equal
  `data/processed/vol5_rules.parquet` exactly, none is ruined, and $\sqrt{A_{\mathrm w}}\,\bar x/s$ equals
  `summary()`'s Sharpe ratio to 1e-12. Daily: $T=1{,}851$ net returns $R_t=W_t/W_{t-1}-1$, 5 March 2019 → 8 October
  2026, from the session after the first trade (4 March 2019); $\tau=T/A_{\mathrm w}=7.60$ years [A33-01];
  $A_{\mathrm w}=243.5686$ from the wealth frame's 2,368 sessions; $r_f=1.5\%$ accrues 0.616 bp a session [A33-02].
  Excess returns $x_t=R_t-r_f/A_{\mathrm w}$.
- **Months.** The 90 full calendar months April 2019 → September 2026, 12 to 23 sessions each; the 19 returns of March
  2019 and the 6 of October 2026 are left out, and the text says so [A33-03]. A month's log excess return is the log
  change of net wealth between month-end sessions minus the month's accrued log interest, sessions $\times
  \ln(1+r_f/A_{\mathrm w})$. Log returns, because (19.9) needs sums.
- **TR23** (Volume III): `data/processed/vol3_taiex.parquet`'s $R$, $T=5{,}849$ returns 2003-01-03 → 2026-10-08,
  23.7645 years, $A=246.12$, $r_f=0$ (Volume IV's convention) [A33-05]: the long record against which the through
  case's 7.60 years [A33-01] are judged. LM19's and LM20's numbers are quoted as printed and recomputed only as checks
  [A33-21].
- **Conventions.** Sharpe ratios are per observation in every formula and annualized only for printing:
  $\sqrt{A_{\mathrm w}}$ for E5's days, $\sqrt{12}$ for months, $\sqrt A$ for TR23, always a convention on simple
  returns (LM19). Means, $s$, skewness and raw kurtosis divide by $T$ (19.3); every kurtosis printed says "raw" or
  "excess" (shared decisions, "LM33's load"). (20.9) is the plug-in with the sample moments; "normal" sets skewness 0
  and kurtosis 3, which is Lo's iid-normal $\sqrt{(1+\mathrm{SR}^2/2)/T}$. HAC: (23.7)'s Bartlett weights, the book's
  lag, 7 at $T=1{,}851$, 9 for TR23 and 3 for 90 months [A33-04], no small-sample factor. Two-sided normal intervals
  $\pm1.959964$ standard errors; PSR, MinTRL and DSR are one-sided at 95%. "Years" of a track record are sessions ÷ $A$
  of the sample (MinTRL), and $\tau=T/A_{\mathrm w}$ for the through case; the criteria's calendar years (7.5975
  [A33-01]) are LM34's.
- **Guard and exact checks.** Bootstrap counts use $\ge$ the statistic $-10^{-12}$; Holm's rejections use
  $\le0.05+10^{-12}$. A bootstrap p-value is a multiple of 1/10,000 and is printed to two decimals.
- **Seeds.** Experiment 1: the seven Ledoit–Wolf tests, `default_rng([1, 20261011])`, $B=9{,}999$ circular-block
  resamples of the 1,851 dates with $b=26$, one set of block starts per resample shared by the seven pairs. Experiment
  2: $10^6$ draws of $\mathcal N_8(\mathbf 0,C)$, `default_rng([2, 20261011])`. Experiment 3: R2 against R1 at block
  sizes 1, 5, 10, 26, 50 and 100, $B=9{,}999$ each, `default_rng([3, 20261011])`, drawn in that order. Monte Carlo
  standard errors: $\sqrt{p(1-p)/B}$ for a p-value (lm18.md:151), SD ÷ $\sqrt{10^6}$ for experiment 2's mean (18.2).
  The widget does not simulate.
- **Published files.** Only statistics: per-rule moments and estimates, lag and block-size curves, model curves. No
  daily series of a rule in date order is published, and no intraday path.
- **Scripts.** `data/lm33_numbers.py` (every printed value, asserted against `src/lm33.md`, compared with the anchors,
  rounding boundaries flagged) and `data/lm33_charts.py` (X2–X7 and the widget's data block); both read the outputs of
  `data/vol5_series.py`, `data/vol5_rules.py` and `data/vol3_series.py` and run none of them.

**Hygiene declaration.** *Out-of-sample:* every Sharpe ratio, interval, PSR, test, DSR and haircut of the eight rules
(rules, windows, costs and criteria fixed on 2026-10-24 before any result; 1,851 sessions after the first trade). The
family is R1–R8, $n=8$ (shared decision, "The count of trials"); the module runs eight PSR tests (one family, Holm) and
seven pair tests (one family, Holm) on the same returns, and says so. *Stability check:* the HAC lag curves (X3,
$\ell=0$ to 60), the block-size sensitivity (experiment 3), the monthly against daily ratios. *In-sample:* TR23's
figures, as LM19–LM22 printed them. *Model:* X4's track-record curves (normal returns), experiment 2, the widget, the
published examples of Bailey and López de Prado and of Harvey and Liu (their inputs). *Descriptive:* the rules'
correlations and autocorrelations. Local note: "The eight rules and their settings were fixed on 24 October 2026,
before any result was computed, so their Sharpe ratios are out of sample: 1,851 daily net returns, 5 March 2019 to 8
October 2026, with $r_f=1.5\%$. The module compares eight rules on the same returns: Section 7 deflates the best for
$n=8$ and says what independence that count assumes. Lag and block-size curves are stability checks; TR23's figures
are in sample, as [[LM19]] and [[LM20]] printed them; the track-record curves and the correlated simulation are model
results."

**Notation.** AUTHORING §6 with the Portfolios table. Used: $R_t$, $r$, $T$ (a count), $t$, $\tau$ (years), $A$,
$A_{\mathrm w}$, $r_f$, $W_t$, $\mathrm{SR}$, $\widehat{\mathrm{SR}}$, $\mathrm{SR}_0$, PSR, DSR, MinTRL, $\mu$,
$\sigma$, $s$, $\widehat{\operatorname{Skew}}$, $\widehat{\operatorname{Kurt}}$ (raw), $\rho_k$, $\hat\rho_k$,
$\hat\rho$, $C$ (the rules' correlation matrix), (19.7)'s ratio written out (no $\operatorname{VR}$ symbol, as LM26
does), $\E$, $\Var$, $\Cov$, $\Phi$, $\Phi^{-1}$, $\varphi$,
$\mathcal N$, $\mathcal N_8$, $Z$, $\mathbf Z$, $\operatorname{SE}$, $\text{t-stat}$, $H_0$, $H_1$, $\alpha$ (the
significance level, LM33's meaning), $n$ (trials), $m$ (periods summed in (19.9)), $k$ (a lag), $B$, $\ell$ (the HAC
lag), $\hat F^{-1}_{\text{boot}}$ (LM22's), $\boldsymbol\theta$, $\hat{\boldsymbol\theta}$, $\nabla h$ ((20.8)), $f_q$
((4.3), §8 only). Local symbols, declared in the notation note:

| Symbol | Meaning | Check against §6 |
|:--|:--|:--|
| $x_t$, $\bar x$ | a rule's daily excess return $R_t-r_f/A_{\mathrm w}$, its mean; $s$ is its SD (divisor $T$, equal to that of $R_t$) | LM19's generic series $x_t$ of (19.5); LM33 writes no data matrix $X$ and no random variable $X$ |
| $\widehat{\mathrm{SR}}_j$, $\Delta$, $\hat\Delta$ | rule $j$'s estimate ($j=1,\dots,8$ for R1–R8); $\mathrm{SR}_j-\mathrm{SR}_1$ and its estimate | common $\Delta$ for a difference; "a year" marks annual values |
| $\hat V_{\mathrm{SR}}$ | $1-\widehat{\mathrm{SR}}\,\widehat{\operatorname{Skew}}+\tfrac14(\widehat{\operatorname{Kurt}}-1)\widehat{\mathrm{SR}}^2$, (20.9)'s plug-in, so $\operatorname{SE}=\sqrt{\hat V_{\mathrm{SR}}/T}$ | new; no SVD $V$ in LM33; Bailey and López de Prado's $V$ (the variance across trials) is written in words |
| $\mathbf v_t$, $\Psi$, $\hat\Psi$, $\hat\Gamma_k$ | the per-date terms of a statistic (a column); their long-run covariance; (23.7)'s estimate; the lag-$k$ sample autocovariance of $\mathbf v_t$ (divisor $T$) | new; the discount factor $v$ is not in LM33; $\hat\Gamma_k$ as LM23's |
| $b$ | the block size of the circular block bootstrap (Ledoit and Wolf's letter) | §6's $B$, $\ell$ row: LM33 declares two letters, $\ell$ the lag (LM23's) and $b$ the block; LM33 has no bets |
| $\hat\Delta_{\text{boot},i}$ | the difference in resample $i$ | LM22's subscript; no star |
| $Z_{(n)}$, $\E Z_{(n)}$ | the largest of $n$ iid standard normals; its mean | as §6's $R_{(j)}$; $n$ is §6's number of trials |
| $n_{\mathrm{eff}}$ | the effective number of trials | new, subscripted |
| $\gamma_{\mathrm E}$ | Euler's constant, 0.5772 (in the approximation of (33.4)) | subscripted; $\gamma$ (growth of cash flows) is not in LM33 |
| $\mathrm{HSR}$, $\text{t-stat}_{\text{adj}}$ | the haircut Sharpe ratio; the t-stat whose single-test p-value equals the adjusted one | new; HSR upright like PSR (Open item 9) |

Not used: $\eta(q)$ for Lo's scale factor (LM5's $\eta$; written "the scale factor"), a star on a bootstrap quantile or
an adjusted t-stat, $d$ for Ledoit and Wolf's studentized statistic (written out), $\gamma_3$, $\gamma_4$ for the
moments, $p_{\mathrm S}$, $p_{\mathrm M}$ (p-values in words, as §6 asks outside LM21), $L$ (R8's exposure appears only
through LM31), $q$. LM33 says once that (21.6)–(21.9)'s $m$ tests read as $n$ trials.

**Motivating case: "Better, or lucky?"** (box, about 150 words)

> Eight rules for five Taiwan-listed funds were fixed on 24 October 2026, before any result was computed. Net of
> costs, they earned 1,851 daily returns from 5 March 2019 to 8 October 2026, 7.60 years [A33-01]. The constructed
> reference mix R2 has the highest Sharpe ratio, 1.14 a year. Equal weights, R1, earn 0.98, and the maximum-Sharpe rule
> R4 the lowest, 0.63 [A33-14]. Is R2 better, or lucky? Its standard error is 0.37, so its 95% interval runs from 0.42
> to 1.86 [A33-07] and holds all seven other estimates [A33-14]. R2 beats R1 by 0.16 a year, but their daily returns
> correlate 0.70, and Ledoit and Wolf's test gives a p-value of 0.53 [A33-33]. R2 is also the best of eight. If eight
> independent rules all had a true Sharpe ratio of zero, the best of them would still average 0.52 a year [A33-45].

Resolved: (a) the precision of one ratio: §2–§4, X1, X2 (HAC interval 0.39 to 1.89 [A33-07]; Lo's monthly ratio 0.94
[A33-22]); (b) how long a record must be: §5, X4 (MinTRL against zero, 2.15 years [A33-26]; 7.37 years after eight
trials [A33-49], against 7.60 observed [A33-01]); (c) R2 against R1: §6, X5 (HAC p-value 0.52, interval −0.35 to +0.67
[A33-33]; 146 years of data for 80% power if the gap were true [A33-41]); (d) the best of eight: §7–§8, X6, X7 (DSR
0.955 at $n=8$ [A33-46], 0.994 at the effective 2.07 trials [A33-48]; a haircut of 21% [A33-54]). The verdict the module
reaches: R2's Sharpe ratio is very probably above zero, but 7.60 years cannot rank it above R1, so the data do not
support allocating more to R2 than to R1 (guidance g:116).

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | the layer LM33 adds: Volume IV gave one Sharpe ratio an error bar, Volume VI compares eight rules and corrects for picking the best; case + X1; roadmap; notation and hygiene notes | 360 |
| 2 | The Checkpoint: Eight Rules with Error Bars {1} | Volume IV's checkpoint on the through case (g:43): (20.9) applied, raw kurtosis named; E1 (R2 by hand); E2 (all eight: mean excess, volatility and Sharpe ratio with standard errors); X2; R4's two-sided interval and one-sided test; pitfall: excess kurtosis typed into (20.9); 導讀; KC | 600 |
| 3 | Dependent Days: the HAC Standard Error {2} | why returns that are nearly uncorrelated still need care (R1's squares have $\hat\rho_1=0.246$ [A33-19]); (33.1) from (20.8) and (23.7); conditions stated; Deep Dive: (33.1) at $\ell=0$ is (20.9); X3, the lag curve; E3 (HAC over (20.9) 0.92 to 1.04 for the Sharpe ratio [A33-18], 1.51 to 1.60 for the volatility [A33-20]); E4 (TR23 against LM20 and LM22); one sentence on Lo's GMM form; 導讀 (HAC, long-run variance); KC | 500 |
| 4 | Annualizing Autocorrelated Returns {3} | (19.9) as Lo's scale factor; Lo's AR(1) check; E5 on 90 months; the correction's own noise by (25.6); simple against log ratios; KC | 480 |
| 5 | The Probabilistic Sharpe Ratio and the Minimum Track Record {4} | (33.2) as one minus a one-sided p-value (21.2), not a probability without a prior ([[LM24]]); (33.3) by inversion; against (21.4): one-sided, power ½, the "1 +" and $\hat V_{\mathrm{SR}}$; $T$ against $T-1$; X4; E6; TR23; the published example reproduced; pitfall: $\mathrm{SR}_0$ is a benchmark, not another rule's estimate; 導讀 (one-sided test); KC | 620 |
| 6 | Comparing Two Sharpe Ratios {5} | Ledoit and Wolf's delta method on four moments (33.6) with (23.7); correlation shrinks the error ((16.3)), against (21.3); the studentized circular block bootstrap, its p-value against (22.4); the block size by the book's rule; X5; E7; the seven pairs and Holm; the years a gap of 0.16 needs [A33-41]; one sentence each on [[LM34]] and the information ratio; 導讀 (studentized interval, circular blocks); KC | 640 |
| 7 | Deflating the Best of Eight {6} | the winner's expected maximum from (21.9), (33.4), Deep Dive; the approximation stated; DSR at $n=8$; what $n=8$ assumes; the effective number (experiment 2); the cross-section's dispersion; (33.5); X6; E8; the published example reproduced; one sentence on PBO ([[LM34]]); pitfall: a DSR near 0.95 is not a verdict; 導讀 (selection bias, order statistic); KC | 600 |
| 8 | Haircuts and Sizing {7} | Harvey and Liu's haircut (33.7): Bonferroni, Holm, independent tests; X7; E9; their example reproduced; Holm's running maximum; the haircut on (4.3)'s fraction, then a fraction of Kelly (LM4's promise), [[LM45]] pointer; "the data are too thin" as a valid conclusion; KC | 400 |
| 9 | Sharpe Statistics in Python {8} | NumPy by hand; `scipy.stats.skew` and `kurtosis` with `fisher`, `bias` passed; arch `optimal_block_length`'s two columns; the bootstrap loop with one generator; lab box | 180 |
| — | Summary (7) / Problems (12) / Solutions | | 140 / 400 / 520 |
| | **Total** | | **5,440** |

**Elements.** 9 examples (E1, E2 §2; E3, E4 §3; E5 §4; E6 §5; E7 §6; E8 §7; E9 §8). Knowledge checks:

- §2: R4's two-sided 95% interval, −0.09 to 1.35, contains 0, yet its PSR(0) is 0.956 [A33-17]. Why both? The interval
  is two-sided at 5%; PSR is one-sided, and its two-sided twin at 10%, 0.02 to 1.23, excludes 0 [A33-17].
- §3: R1's daily excess returns have $\hat\rho_1=-0.054$, its squared deviations 0.246 [A33-19]. Which standard error
  should dependence move more, the mean's or the volatility's? The volatility's: HAC over iid is 1.51 for R1's
  volatility [A33-20] but 0.98 for its Sharpe ratio [A33-18].
- §4: for monthly AR(1) returns with $\rho=0.2$, (19.9) gives a scale factor 2.88 against $\sqrt{12}=3.46$, so the
  $\sqrt{12}$ rule overstates the annual ratio by 20% (1.203) [A33-24]; Lo's Table 2 prints 2.88 [A33-24].
- §5: setting $\mathrm{SR}_0$ to R1's estimate makes R2's MinTRL 106 years and its PSR 0.67 [A33-31]. What is wrong?
  R1's 0.98 [A33-06] is an estimate with its own error; comparing two estimates is §6's test.
- §6: the standard error of R2 − R1 that treats the two as independent is 0.52 a year, Ledoit and Wolf's 0.25; the
  ratio 0.49 is near $\sqrt{1-\hat\rho}=0.55$ [A33-40], by (16.3) with equal errors.
- §7: $\E Z_{(8)}$ is 1.424; the approximation gives 1.459 and (21.9)'s median 1.39 [A33-44]. Why is the mean above the
  median? The maximum's distribution is skewed to the right.
- §8: Holm's haircut of R4 is 0% while Bonferroni's is 75% [A33-53]. Why? R4 has the largest p-value, which Holm
  compares with the level itself; the adjusted value cannot fall below the running maximum, so R6, R7 and R8 share
  0.71 [A33-53].
- §9: `scipy.stats.kurtosis` of R2's excess returns with its defaults (`fisher=True`, `bias=True`) gives 10.58, the
  excess kurtosis; (20.9) needs the raw 13.58 [A33-64].

中文導讀 in §2 (夏普比率 (Sharpe ratio), 標準誤 (standard error), 偏態 (skewness), 峰態 (kurtosis): raw against excess), §3 (自我相關
(autocorrelation), 變異數非齊一與自我相關一致估計量 (HAC), 長期變異數 (long-run variance)), §5 (單尾檢定 (one-sided test), 檢定力 (power); PSR and
MinTRL kept in English), §6 (Student化信賴區間 (studentized confidence interval), 循環區塊 (circular block), 區塊自助重抽法 (block
bootstrap)), §7 (選擇偏誤 (selection bias), 順序統計量 (order statistic), 多重假設檢定 (multiple testing); DSR kept in English). Deep
Dives: §3 "Why the HAC error at lag zero is (20.9)": $\hat\Gamma_0$ of $\mathbf v_t$ has entries $s^2$,
$s^3\widehat{\operatorname{Skew}}$ and $s^4(\widehat{\operatorname{Kurt}}-1)$, and $\nabla h^{\top}\hat\Gamma_0\nabla h$
is $\hat V_{\mathrm{SR}}$ term by term (the script asserts it to 1e-15). §7 "The expected maximum from (21.9)": $\E
Y=\int_0^\infty(1-F_Y)\,dy-\int_{-\infty}^0F_Y\,dy$ for $Y$ with a finite mean, by integration by parts on each
half-line, with $F_Y=\Phi^n$; the approximation *stated without proof* (Bailey and López de Prado 2014, from
extreme-value theory).

**Exhibits.**

- X1 `case` (table, §1): the eight rules, daily net excess returns, 5 March 2019 → 8 October 2026, $r_f=1.5\%$. Columns:
  Sharpe ratio a year; SE by (20.9); SE by (33.1), $\ell=7$; 95% interval (HAC); PSR(0); minus R1 a year; bootstrap
  p-value. Rows R1–R8 in the order fixed in advance (not sorted by result): R1 0.98, 0.370, 0.363, 0.26 to 1.69
  [A33-06], 0.996 [A33-16]; R2 1.14, 0.367, 0.382, 0.39 to 1.89 [A33-07], 0.999 [A33-16], +0.16, 0.53 [A33-33]; R3 0.77,
  0.370, 0.373, 0.04 to 1.51 [A33-08], 0.982 [A33-16], −0.20, 0.41 [A33-34]; R4 0.63, 0.368, 0.340, −0.04 to 1.30
  [A33-09], 0.956 [A33-16], −0.35, 0.24 [A33-35]; R5 0.84, 0.370, 0.374, 0.11 to 1.58 [A33-10], 0.989 [A33-16], −0.13,
  0.57 [A33-36]; R6 0.95, 0.371, 0.370, 0.23 to 1.68 [A33-11], 0.995 [A33-16], −0.02, 0.88 [A33-37]; R7 0.92, 0.370,
  0.368, 0.20 to 1.64 [A33-12], 0.993 [A33-16], −0.06, 0.79 [A33-38]; R8 0.94, 0.371, 0.368, 0.21 to 1.66 [A33-13],
  0.994 [A33-16], −0.04, 0.80 [A33-39]. Note row: DSR of R2 at $n=8$ 0.955 [A33-46]. Note: out of sample; net of costs;
  $A_{\mathrm w}=243.57$ [A33-02]; bootstrap $B=9{,}999$, $b=26$, seed `[1, 20261011]`, Monte Carlo SE at most 0.005
  [A33-33]. Source: FinMind `TaiwanStockPrice`, `TaiwanStockDividendResult`, `TaiwanStockSplitPrice`, registered 24
  October 2026; Computations: `data/lm33_numbers.py`.
- X2 `forest` (`scatter`, forest plot, §2): y the eight rules, `ticks` 1–8 with `tickLabels` R1 … R8 in fixed order; x
  the annual Sharpe ratio, −0.2 to 2.0 (`fmt: "n2"`). One named point series "estimate" (colour 1); per rule an unnamed
  thick `lines` entry for the (20.9) interval (colour 1) and a thin grey one, offset by 0.2 in y, for the HAC interval
  ($\ell=7$); dashed `vline` at 0. Values cited: the eight intervals of A33-06 to A33-13; R2's 0.42 to 1.86 and 0.39 to
  1.89 [A33-07]; R4's −0.09 to 1.35 [A33-09]. Note: names the two interval styles; out of sample.
- X3 `haclag` (`line`, §3): x the lag $\ell$, 0 to 60 (`fmt: "n0"`); y the Sharpe ratio's SE a year (`fmt: "n3"`);
  series R1, R2, R4 (colours 1–3); dashed `hline` at the normal SE 0.363 [A33-06]; dashed `vline` at $\ell=7$. Values
  cited: R1 0.370, 0.363, 0.359, 0.367; R2 0.367, 0.382, 0.393, 0.389; R4 0.368, 0.340, 0.316, 0.300 at $\ell=0$, 7,
  20, 60 [A33-18]. Note: $\ell=0$ is (20.9); a stability check.
- X4 `psrT` (`line`, log x, §5): x years of daily data, 0.5 to 15 (`ticks` 0.5, 1, 2, 5, 10); y PSR(0) (`fmt: "n3"`,
  0.5 to 1); series "annual SR 0.5", "1.0", "1.5" (colours 1–3), normal returns, $A_{\mathrm w}$; dashed `hline` 0.95;
  dashed `vline` at $\tau=7.60$; `point`s at the crossings. Values cited: MinTRL 10.83, 2.72 and 1.21 years; PSR(0) at
  7.60 years 0.916, 0.997, 1.000 [A33-29]. Note: *Model*; the estimate held fixed as the record lengthens.
- X5 `pairs` (`scatter`, forest plot, §6): y R2 … R8 against R1 (`ticks` 1–7, `tickLabels` "R2 − R1" …); x $\hat\Delta$
  a year, −1.0 to 0.8; points "difference" (colour 1), thick `lines` for the bootstrap 95% intervals; dashed `vline`
  at 0. Values cited: A33-33 to A33-39; R2 − R1 +0.16, −0.35 to +0.67 [A33-33]; R4 − R1 −0.35, −0.95 to +0.25
  [A33-35]. Note: Ledoit and Wolf's symmetric studentized interval, circular blocks $b=26$, $B=9{,}999$, seed
  `[1, 20261011]`; seven tests on the same returns, none rejected after Holm [A33-43].
- X6 `deflate` (`line`, log x, §7): x the number of trials $n$, 1 to 10,000; y the deflated benchmark
  $\mathrm{SR}_0$ a year (`fmt: "n2"`); series "exact, (33.4)" (colour 1) and "approximation" (colour 2, dashed);
  dashed `hline` at R2's pass line 0.53 ("the largest $\mathrm{SR}_0$ R2 passes at 95%"); dashed `vline`s at $n=8$
  and $n_{\mathrm{eff}}=2.07$. Values cited: 0, 0.20, 0.52, 0.56, 0.91, 1.18, 1.40 at $n=1$, 2, 8, 10, 100, 1,000,
  10,000 [A33-52]; approximation 0.529 at 8 [A33-45]; $n_{\mathrm{eff}}$ [A33-48]. Note: $T=1{,}851$; the null
  standard deviation $1/\sqrt{T-1}$, 0.363 a year [A33-45].
- X7 `haircut` (`bar`, §8): categories R1–R8; series "Sharpe ratio", "HSR, independent tests", "HSR, Holm" (colours 1–3;
  `fmt: "n2"`). Values cited: A33-53; R2 1.14 [A33-07], 0.90, 0.89 [A33-53]. Note: $n=8$; two-sided normal p-values of
  $\widehat{\mathrm{SR}}\sqrt T$; the rules are correlated, so independence overstates the haircut (§7).

**Widget `minTrack` — "How long must a record be?"** `Book.controls`: start from (select R1–R8, setting the next
three to that rule's unrounded moments), annual Sharpe ratio (0.2 to 2.5, step 0.01), skewness (−2 to 1, step 0.01),
raw kurtosis (3 to 25, step 0.1), trials $n$ (select 1, 2, 3, 5, 8, 10, 20, 50, 100, 1,000), observations a year
(select 12, 52, 243.57), confidence (select 90%, 95%, 99%). Readouts: $\E Z_{(n)}$, exact and approximate; MinTRL by
(33.5) in observations and years; PSR(0) and DSR at the through case's 7.60 years [A33-01], that is $7.60A$
observations. Chart: DSR against years of data
(0.5 to 20, log x), dashed `hline` at the confidence, dashed `vline` at MinTRL. $\E Z_{(n)}$ by module-local Simpson
quadrature of (33.4) on [−10, 10] with `Book.dist.Phi` (under 30 lines), tested against the script's values to 1e-6
as `data/lm15_charts.py` tests its code; quantiles by `Book.dist.PhiInv`. Initial state (PDF): R2, $n=8$, 95%:
MinTRL 1,796 sessions, 7.37 years [A33-49], DSR 0.955 [A33-46]; at $n=1$ 2.15 years [A33-26]. Data block
`chart-lm33-minTrack`: the eight rules' $\widehat{\mathrm{SR}}$, skewness, raw kurtosis and $T$ (32 numbers).

**Examples** (results recomputed from the printed inputs):

- E1 §2 `r2hand`, R2 by hand: $\bar x=0.0564\%$, $s=0.774\%$, $\widehat{\mathrm{SR}}=0.0729$ a day; $\hat
  V_{\mathrm{SR}}=1+0.0082+0.0167=1.0249$; SE 0.0235 a day, 0.367 a year; $\widehat{\mathrm{SR}}\sqrt T=3.14$, the
  t-stat of the mean excess return with divisor $T$, by LM21's identity (lm21.md:172) [A33-15]. The skewness term is
  small because R2's skewness is only −0.11 [A33-07]; kurtosis adds more.
- E2 §2 `checkpoint`, all eight rules (guidance g:43): mean excess returns a year from 7.71% (R3) to 13.74% (R2) with
  iid SEs 3.61% and 4.38%; volatilities 9.96% to 16.53% with iid SEs 0.45% and 0.59% [A33-07, A33-08, A33-09]; raw
  kurtosis 10.3 (R4) to 23.0 (R8) [A33-09, A33-13]; the normal SE 0.363 for every rule, (20.9) 0.367 to 0.371 [A33-06 to
  A33-13]. The volatilities of R1, R3 and R5 are LM30's and those of R6–R8 LM31's, echoed; their SEs are LM33's. Every
  other rule's estimate lies inside R2's interval [A33-14]. R4: two-sided 95% −0.09 to 1.35; one-sided PSR(0) 0.956
  [A33-17]. All eight PSR(0) exceed 0.95, from 0.956 (R4) to 0.999 (R2), and Holm (21.7) on the eight one-sided p-values
  rejects all eight, the largest adjusted p-value 0.044 [A33-16].
- E3 §3 `hac`, R1, R2 and R4 by lag: R2's SE grows from 0.367 at $\ell=0$ to 0.382 at 7 and 0.393 at 20; R4's falls to
  0.340 at 7 [A33-18]; HAC over (20.9) at $\ell=7$ runs from 0.92 (R4) to 1.04 (R2) [A33-18]. The volatility's SE
  rises by half: HAC over iid 1.51 to 1.60 at $\ell=7$, and R1's 0.58% becomes 0.87%, 1.03% and 1.16% at $\ell=7$, 20,
  60 [A33-20]. Days are nearly uncorrelated ($\hat\rho_1$ from −0.054 to 0.002 [A33-19]); their squares are not.
  Interval with HAC: R2 0.39 to 1.89 [A33-07].
- E4 §3 `tr23`, the long record: TR23's 0.81 a year (0.0517 a day), skewness −0.34, raw kurtosis 8.27; SE 0.207 by
  (20.9), as LM20 printed (lm20.md:401), 0.213 by (33.1) at $\ell=9$ and 0.243 at $\ell=145$, against LM22's blocks of
  145, 0.233 stationary, 0.244 circular, 0.247 moving (lm22.md:216–219) [A33-21]. HAC at the block length agrees with
  the blocks.
- E5 §4 `monthly`, 90 months of log excess returns: R1's monthly ratio 0.305 gives 1.06 by $\sqrt{12}$ and 0.92 by
  (19.9) with $\hat\rho_1,\dots,\hat\rho_{11}$; its ratio $1+2\sum_k(1-k/12)\hat\rho_k=1.31$ has a robust SE of 0.38
  by (25.6) [A33-22], and its distance from 1 is 0.78 iid SEs (0.40) [A33-23]. R2: 1.05 and 0.94; R4: 0.62 and 0.49
  [A33-22]. The scale factors run from 2.74 to 3.33 against 3.46 [A33-23]. The daily log-return ratios, 0.54 (R4) to
  1.08 (R2) [A33-25], show the simple-against-log gap separately. Conclusion: 90 months cannot tell whether the
  correction is needed, and the corrected ratio carries the noise of 11 autocorrelations.
- E6 §5 `mintrl`: R2's PSR(0) 0.999 and MinTRL(0) 523 sessions, 2.15 years (normal moments 2.10); R1's 0.996, 720
  sessions, 2.96 years (2.85); R4's 0.956, 1,717 sessions, 7.05 years (6.85) [A33-26] against its 7.60 [A33-01]. $T$
  against $T-1$: R2's z-value 3.097 with $\sqrt{T-1}$, 3.098 with $\sqrt T$, a factor of 0.027% [A33-27]. TR23: PSR(0)
  0.99995, MinTRL 1,035 sessions, 4.20 years; (21.4) one-sided at power ½ gives 4.11 years; LM21's two-sided 80% power
  needs 11.9 years (lm21.md:183) [A33-28]. The published check: Bailey and López de Prado's appendix inputs give 59.895
  months, 4.99 years, and PSR 0.95 at that length [A33-30].
- E7 §6 `lw`, R2 against R1: $\hat\Delta=+0.16$ a year, correlation 0.70, $\operatorname{SE}(\hat\Delta)=0.253$
  ($\ell=7$), t-stat +0.64, HAC p-value 0.52; bootstrap p-value 0.53 (Monte Carlo SE 0.005), $\hat
  F^{-1}_{\text{boot}}(0.95)=2.01$, interval −0.35 to +0.67 [A33-33]. Independent-samples SE 0.52 [A33-40]. If 0.16
  were the true gap, 80% power at 5% two-sided would need 146 years, and a one-sided 95% test at power ½ 50 years
  [A33-41]. Block sizes 1 to 100 give p-values 0.53 to 0.56 [A33-42]; lags 0 to 60 give SEs 0.280 to 0.243 [A33-40].
  All seven pairs: none rejected after Holm, smallest adjusted p-value 1.00 [A33-43].
- E8 §7 `dsr`, R2 deflated: $\E Z_{(8)}=1.424$ [A33-44], so $\mathrm{SR}_0=0.52$ a year (0.517) [A33-45] and DSR
  0.955; with the approximation 0.951, with R2's HAC SE 0.948; DSR falls to 0.95 at $n=8.8$ [A33-46]. Correlations:
  mean 0.82, R3–R5 0.998, R6–R8 0.96, R2–R1 0.70 [A33-47]. Experiment 2: $\E\max$ of $\mathcal N_8(\mathbf 0,C)$
  0.588 (Monte Carlo SE 0.0009), $n_{\mathrm{eff}}=2.07$, $\mathrm{SR}_0=0.21$, DSR 0.994 [A33-48]. The eight
  estimates have SD 0.141 a year, about the 0.144 that equal true ratios would give [A33-50]. MinTRL after $n$ trials
  (33.5): 2.15 years at $n=1$, 7.37 at 8 (1,796 sessions), 3.92 at $n_{\mathrm{eff}}$, 13.5 at 100 [A33-49]. The
  published check: Bailey and López de Prado's example gives DSR 0.900 at $N=100$, 0.9505 at 46 and, for normal
  returns, 0.9505 at 88 [A33-51].
- E9 §8 `haircut`, R2: t-stat 3.14, single two-sided p-value 0.0017; adjusted for eight independent tests 0.0136
  (Bonferroni 0.0137); $\text{t-stat}_{\text{adj}}=2.47$; HSR 0.90 a year, a haircut of 21% [A33-54]. At a fixed
  volatility, (4.3)'s fraction falls by the same 21% [A33-56]. The published check: Harvey and Liu's example (240
  months, 0.75 a year, 200 tests) with the normal reference gives 0.0008, 0.15 and 0.32, as they print; their
  "approximately 60%" is (0.75 − 0.32)/0.75, 57% [A33-55]. With $t_{239}$, as their text says, the HSR is 0.31
  [A33-55].

**Problems plan** (12; MC keys B, C, A, B, C, A; the lab solves 10, 11, 12). Stems state the sample (E5's through
case: daily net returns 5 March 2019 → 8 October 2026, $T=1{,}851$, $A_{\mathrm w}=243.57$, $r_f=1.5\%$; or the
hypothetical inputs), the period of each Sharpe ratio, raw or excess kurtosis, divisor $T$, normal or (20.9), one- or
two-sided, the level, and rounding; problems 11 and 12 give the lag, the block size, $B$ and the seed.

1. MC: normal returns, daily Sharpe ratio 0.06, $T=1{,}851$, $A=243.57$; the annual SE. A 0.0233 (not annualized).
   **B** 0.363. C 5.67 (times $A$, not $\sqrt A$) [A33-57].
2. MC: monthly Sharpe ratio 0.30, skewness −1.0, raw kurtosis 8.0, $T=90$; the SE by (20.9). A 0.124 (excess kurtosis 5
   typed as raw). B 0.108 (normal). **C** 0.127 [A33-58].
3. MC: normal returns, daily Sharpe ratio 0.05, $\mathrm{SR}_0=0$, 95%, $A=243.57$; MinTRL in years. **A** 4.45. B 6.32
   ($\Phi^{-1}(0.975)$, a two-sided quantile). C 0.028 (the annual ratio in the daily formula) [A33-59].
4. MC: $\E Z_{(5)}$. A 1.193 (the approximation). **B** 1.163. C 1.129 ((21.9)'s median) [A33-60].
5. MC: monthly log returns with $\rho_1=0.1$ and no other autocorrelation; the scale factor to a year. A 3.464
   ($\sqrt{12}$). B 3.833 (the sign of $\rho_1$ reversed). **C** 3.184 [A33-61].
6. MC: two annual Sharpe ratios 1.0 and 0.8, each SE 0.36, correlation 0.9; the SE of the difference. **A** 0.161
   (t-stat 1.24). B 0.509 (independent; t-stat 0.39). C 0.036 ($0.36\times(1-0.9)$) [A33-62].
7. Derive (33.3) from (33.2) by setting PSR equal to $1-\alpha$; then (33.5) from (33.4); check that (33.5) at $n=1$ is
   (33.3), and that R2's 7.37 years [A33-49] lie below its 7.60 observed [A33-01], consistent with DSR 0.955 [A33-46].
8. Show $\E\max(Z_1,Z_2)=1/\sqrt\pi=0.5642$ for independent standard normals, from $\max(a,b)=\tfrac12(a+b+\lvert
   a-b\rvert)$, (16.3), (16.7) and (19.2)'s $\E\lvert R-\mu\rvert=\sigma\sqrt{2/\pi}$; compare (33.4)'s integral at
   $n=2$ and the approximation 0.520 [A33-44].
9. Haircut (hypothetical): t-stat 2.5, ten independent tests; the single and adjusted p-values 0.0124 and 0.117,
   $\text{t-stat}_{\text{adj}}=1.565$, haircut 37.4%; Bonferroni's 1.537 and 38.5% [A33-63]; why Bonferroni cuts more.
10. Python: R1's 90 monthly log excess returns; the monthly ratio 0.305, 1.06 by $\sqrt{12}$, 0.92 by (19.9), the ratio
    1.31 and its robust SE 0.38 by (25.6) [A33-22]; would you apply the correction?
11. Python: (33.1) for R2 at $\ell=0$, 7, 20, 60: 0.367, 0.382, 0.393, 0.389 a year [A33-18]; check $\ell=0$ against
    (20.9).
12. Python: Ledoit and Wolf's test of R4 against R1, $\ell=7$, $b=26$, $B=9{,}999$, seed `[1, 20261011]` (the block
    starts do not depend on the pairs, so one pair reproduces experiment 1): $\hat\Delta=-0.35$, SE 0.285, HAC p-value
    0.22, bootstrap 0.24 (Monte Carlo SE 0.004), interval −0.95 to +0.25 [A33-35].

**Lab parts** (`build/make_lab33.py`; reads only its `data/`: the eight rules' net wealth paths on the wealth frame's
dates as one derived file from `data/make_lab_data.py` (Open item 7), and `taiex_tr.csv` (TR23)): 1 data: $R_t$, $x_t$,
$T$, $A_{\mathrm w}$, the 90 months, a check against the criteria's Sharpe ratios; 2 X1, X2, E1, E2, `scipy.stats`
with `fisher=False, bias=True` passed; 3 (33.1) by hand, X3, E3, E4, problem 11; 4 E5, Lo's AR(1) check, problem 10; 5
X4, E6, the 2012 appendix example; 6 Ledoit and Wolf by hand, experiment 1, X5, E7, experiment 3, problem 12; 7 (33.4)
by quadrature against the approximation, experiment 2, X6, E8, the 2014 example; 8 X7, E9, Harvey and Liu's example.
Extension (*Stability check*): R2's PSR(0) on rolling windows of 730 sessions (about three years), with a closing
sentence that picking a window after seeing the curve is one more trial ([[LM34]]'s subject; the lab writes plain
"LM34").

**Cross-module tags.**

- (33.1) $\operatorname{SE}_{\mathrm{HAC}}(\widehat{\mathrm{SR}})=\sqrt{\nabla h^{\top}\hat\Psi\nabla h/T}$, $\nabla
  h=(1/s,\,-\bar x/(2s^3))^{\top}$, $\hat\Psi$ by (23.7) on $\mathbf v_t=(x_t-\bar x,\,(x_t-\bar x)^2-s^2)^{\top}$ with
  the book's lag; at $\ell=0$ it is (20.9)'s plug-in; stationary terms with fading dependence and finite fourth moments,
  large $T$ (stated) (LM34, LM45).
- (33.2) $\operatorname{PSR}(\mathrm{SR}_0)=\Phi\big((\widehat{\mathrm{SR}}-\mathrm{SR}_0)\sqrt{T-1}/\sqrt{\hat
  V_{\mathrm{SR}}}\big)$, one minus the one-sided p-value of $H_0:\mathrm{SR}\le\mathrm{SR}_0$; per observation (LM34,
  LM45).
- (33.3) $\mathrm{MinTRL}=1+\hat V_{\mathrm{SR}}\big(\Phi^{-1}(1-\alpha)/(\widehat{\mathrm{SR}}-\mathrm{SR}_0)\big)^2$
  observations, for $\widehat{\mathrm{SR}}>\mathrm{SR}_0$; with $\hat V_{\mathrm{SR}}=1$, $\mathrm{SR}_0=0$ and without
  the 1 it is (21.4) one-sided at power ½ (LM45).
- (33.4) $\E Z_{(n)}=\int_0^\infty(1-\Phi(z)^n)\,dz-\int_{-\infty}^0\Phi(z)^n\,dz$; DSR $=\operatorname{PSR}(\E
  Z_{(n)}/\sqrt{T-1})$, iid trials with true ratio zero under $H_0$; the approximation
  $(1-\gamma_{\mathrm E})\Phi^{-1}(1-1/n)+\gamma_{\mathrm E}\Phi^{-1}(1-1/(ne))$ stated (LM34).
- (33.5) $T\ge1+\big((\Phi^{-1}(1-\alpha)\sqrt{\hat V_{\mathrm{SR}}}+\E Z_{(n)})/\widehat{\mathrm{SR}}\big)^2$, the
  track record that makes DSR $\ge1-\alpha$ after $n$ trials (LM34, LM45).
- (33.6) $\operatorname{SE}(\hat\Delta)=\sqrt{\nabla h^{\top}\hat\Psi\nabla h/T}$ for
  $h(\boldsymbol\theta)=\theta_1/\sqrt{\theta_3-\theta_1^2}-\theta_2/\sqrt{\theta_4-\theta_2^2}$ at
  $\hat{\boldsymbol\theta}=(\bar x_j,\bar x_1,\overline{x_j^2},\overline{x_1^2})$, $\hat\Psi$ by (23.7); the bootstrap
  p-value $\big(\#\{i:\lvert\hat\Delta_{\text{boot},i}-\hat\Delta\rvert/\operatorname{SE}(\hat\Delta_{\text{boot},i})\ge
  \lvert\hat\Delta\rvert/\operatorname{SE}(\hat\Delta)\}+1\big)/(B+1)$ with circular blocks (LM34).
- (33.7) adjusted p-value $1-(1-\text{p-value})^n$ (independent tests), $\min(1,n\,\text{p-value})$ (Bonferroni) or
  (21.7)'s; $\mathrm{HSR}=\Phi^{-1}(1-\text{adjusted p-value}/2)/\sqrt T$ per observation (LM45).

**Pitfalls to pre-empt.**

- Raw against excess kurtosis: (20.9), PSR and MinTRL take raw kurtosis; `scipy.stats.kurtosis` returns excess by
  default (10.58 against 13.58 for R2 [A33-64]); TR23's raw 8.27 (lm20.md:370, 388, 403) is excess 5.27 (lm19.md:20),
  and 0050's 8.12 in LM4–LM5 (lm04.md:132) is excess. Problem 2's distractor is this error.
- Moments the formulas need (PITFALLS §7): (20.9) needs a finite fourth moment, (33.1) and Ledoit and Wolf's (4) about
  4 + δ; the rules' raw kurtosis runs to 23.0 (R8) [A33-13] and carries no standard error itself (LM20's pitfall).
- One-sided against two-sided: PSR, MinTRL and DSR are one-sided at 95%; the intervals and (21.4) are two-sided; R4 sits
  between [A33-17]. Never compare a PSR with a two-sided interval without saying so.
- $\mathrm{SR}_0$ is a fixed benchmark. Setting it to another rule's estimate ignores that estimate's error (106 years,
  [A33-31]); comparing two rules is (33.6).
- Correlated rules: the independent-samples error of a difference is about twice Ledoit and Wolf's here (0.52 against
  0.25 [A33-40]); yet even the right error leaves the gap far inside noise.
- PSR is not a probability that the true ratio exceeds $\mathrm{SR}_0$ without a prior ([[LM24]]); Bailey and López de
  Prado's wording is paraphrased with that caveat.
- The count of trials: $n=8$ treats the rules as independent; they correlate 0.82 on average [A33-47], so
  $n_{\mathrm{eff}}=2.07$ [A33-48]. The in-sample variants of LM28–LM31 are not candidates (shared decision); had 100
  versions been tried, R2 would need 13.5 years [A33-49]. Say which $n$ every DSR uses.
- A DSR near the line: 0.955 by the exact integral, 0.951 by the approximation, 0.948 with the HAC error [A33-46]. Print
  the number and its method, never "passes".
- Holm's haircut keeps a running maximum: R6, R7 and R8 share 0.71 and R4 keeps its whole ratio [A33-53]; it is not
  "no correction".
- Annualization: $\sqrt A$ on simple returns is a convention (LM19); the criteria's Sharpe ratios are on simple returns,
  Lo's correction on log returns; say which in every caption (E5).
- Bootstrap: Ledoit and Wolf centre the resampled statistic at $\hat\Delta$ (they resample the data, not a null world);
  a count of uncentred $\lvert\hat\Delta_{\text{boot},i}\rvert$ would test nothing. The "+1" makes the p-value never 0.
  Two decimals only (Monte Carlo SE 0.005).
- The block-length rule names the stationary estimate (lm22.md:254); LM33 applies it to the circular scheme it uses
  and says so (Open item 1).
- Ownership: the volatilities of R1, R3, R5 (LM30) and R6–R8 (LM31) are echoed; net wealth, log growth, turnover and
  gross against net are LM34's; nothing re-implements a rule.

**Curriculum guidance carried** (`plans/vol-5.md`'s table):

- g:30, the layer added: §1 says it (Volume IV gave one ratio an error bar; LM33 compares rules and corrects for
  picking the best).
- g:43, Volume IV's checkpoint: §2 does it on the through case (E2, X1, X2).
- g:54–58, outcome levels: [D] 2 and 4, [C] 1, 3, 5, 6 and 8, [U] 7.
- g:111, fixed in advance: every caption and the hygiene note say the rules were fixed on 24 October 2026.
- g:116, "the data are too thin to support more leverage" is a valid conclusion: the case's verdict (§6–§8), E7's 146
  years.
- g:124, taught, practised, assessed: the outcome table above.

**Stage 4 for earlier modules.** `leads` gain 33 in lm04.md:6 (on the plan's Stage 4 list) and lm18.md:6 (new: LM33
cites (18.2) and lm18.md:151). LM16, LM19–LM25 already list 33; the Volume V briefs' leads should include 33 (each
brief's own list). No wording change: every forward link above is honoured as written.

**Sources** (verified 2026-10-24 unless marked; paraphrased, nothing quoted beyond a phrase):

- Lo, A. W., "The Statistics of Sharpe Ratios", *Financial Analysts Journal* 58(4): 36–52, July 2002, DOI
  10.2469/faj.v58.n4.2453. Crossref (run 2026-10-24) for the record; already in SOURCES (LM19). Read in the FAJ text
  (the survey's download, rechecked by the drafter): $V_{\mathrm{IID}}$ (eq. 8) and the iid-normal SE
  $\sqrt{(1+\mathrm{SR}^2/2)/T}$ (eq. 9), the scale factor for aggregated returns (eq. 20), the AR(1) form (eq. 22)
  and Table 2 (2.88 at a monthly first-order autocorrelation of 20% and $q=12$, 3.46 for iid returns; recomputed,
  A33-24); the abstract's "as much as 65 percent" (as lm19.md:359 prints).
- Bailey, D. H., and M. López de Prado, "The Sharpe Ratio Efficient Frontier", *Journal of Risk* 15(2): 3–44, December
  2012, DOI 10.21314/jor.2012.255 (Crossref). Read in the author-hosted July 2012 version: PSR and MinTRL in the
  appendix's Python code, with $\sqrt{\text{obs}-1}$ and the "1 +" term and raw kurtosis; the code's example inputs
  (mean 2, SD $\sqrt{12}$, skewness −0.72, kurtosis 5.78, reference $1/\sqrt{12}$, 59.895 observations, 95%)
  reproduced (A33-30). The printed equations are lost in text extraction; the journal's equation numbers are not used.
- Bailey, D. H., and M. López de Prado, "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest
  Overfitting, and Non-Normality", *Journal of Portfolio Management* 40(5): 94–107, 2014, DOI
  10.3905/jpm.2014.40.5.094 (Crossref; online 30 September 2014). Read in the author-hosted 31 July 2014 version: the
  approximation of the expected maximum with the Euler–Mascheroni constant (their code, `getExpMaxSR`); DSR as a PSR at
  that threshold; the numerical example (about 90% at $N=100$, 0.9505 at $N=46$, normal returns at $N=88$) reproduced
  (A33-51); Appendix A.3, the "implied independent trials" from an average correlation. **UNVERIFIED:** the exact
  form of their eq. (9) (its symbols are lost in the extracted text; the text says the estimate interpolates between
  one trial at correlation 1 and $M$ at 0); LM33 prints $\bar\rho+(1-\bar\rho)8$ only as that reading, flagged, and
  relies on experiment 2's own definition.
- Ledoit, O., and M. Wolf, "Robust performance hypothesis testing with the Sharpe ratio", *Journal of Empirical Finance*
  15(5): 850–859, December 2008, DOI 10.1016/j.jempfin.2008.03.002 (Crossref). Read in IEW Working Paper 320, University
  of Zurich, January 2008: $f(a,b,c,d)$ on uncentred second moments (their (1)–(2)), the delta method (4)–(5), HAC
  inference with a prewhitened quadratic-spectral kernel and a $T/(T-4)$ factor (§3.1), the symmetric studentized
  interval (6)–(7), the circular block bootstrap with the Götze–Künsch block-sum covariance in each resample (§3.2.2),
  the p-value (9) with "+1", the block-size calibration (Algorithm 3.1). Not compared with the journal text (as SOURCES
  already records).
- Harvey, C. R., and Y. Liu, "Backtesting", *Journal of Portfolio Management* 42(1): 13–28, 2015, DOI
  10.3905/jpm.2015.42.1.013 (Crossref). Read in the JPM PDF: the t-stat $\hat\mu/\hat\sigma\cdot\sqrt T$ with $T-1$
  degrees of freedom (eq. 1), the independent-test adjustment $1-(1-p)^N$ (eq. 4), the haircut Sharpe ratio (eq. 5),
  Bonferroni and Holm, the example (240 months, 0.75, $N=200$: 0.0008, 0.15, 0.32, "approximately 60%") reproduced
  with the normal reference (A33-55).
- Götze, F., and H. R. Künsch, "Second-order correctness of the blockwise bootstrap for stationary observations",
  *Annals of Statistics* 24(5): 1914–1933, 1996, DOI 10.1214/aos/1069362303 (Crossref). Bibliographic only: named as
  Ledoit and Wolf's source for the resample's standard error.
- Bibliographic only, named once and not relied on: Andrews, D. W. K., and J. C. Monahan, "An Improved
  Heteroskedasticity and Autocorrelation Consistent Covariance Matrix Estimator", *Econometrica* 60(4): 953–, 1992, DOI
  10.2307/2951574 (Crossref gives the first page only; **the end page is UNVERIFIED**); Jobson and Korkie (1981), in
  SOURCES; Opdyke, J. D., "Comparing Sharpe ratios: So where are the p-values?", *Journal of Asset Management* 8(5):
  308–336, 2007, DOI 10.1057/palgrave.jam.2250084 (Crossref; abstract only, not cited unless the text needs it).
- Through earlier modules (SOURCES): Newey and West (1987) and the lag rule (LM23); Politis and Romano's circular
  blocks via Lahiri (2003) §2.7.1 and LM22 (the 1992 original is unread, as SOURCES says); Politis and White (2004) with
  Patton, Politis and White (2009) for `optimal_block_length` (LM22).
- Not cited: Memmel (2003) (unverified in SOURCES), Mertens (2002) (no copy found; LM20 derives (20.9) without it),
  Harvey, Liu and Zhu (2016) (LM34's, if anyone's).
- Python: SciPy 1.18.1's `stats.kurtosis` defaults (`fisher=True`, `bias=True`) checked by running them (A33-64); arch
  8.0.0's `optimal_block_length` returns `stationary` and `circular` columns (A33-32).

**Chinese terms** (AUTHORING §1; English in parentheses at first use in each box):

- 樂詞網, statistics listing: 夏普比率 (Sharpe ratio), 偏態 (skewness), 峰態 (kurtosis), 選擇偏誤 (selection bias;
  the listing gives 選擇偏誤；選擇偏差), Student化信賴區間 (studentized confidence interval), 序列相關 (serial
  correlation; LM33 writes the book's 自我相關 instead, LM19's term for the same concept).
- 樂詞網, mathematics listing: 順序統計量 (order statistic), Euler常數 (Euler constant).
- The book's settled forms: 標準誤 (standard error), 自我相關 (autocorrelation), 變異數非齊一與自我相關一致估計量
  (HAC, LM23), delta 法 (delta method, LM20), 單尾檢定 (one-sided test, LM25), 檢定力 (power, LM21), 多重假設檢定
  (multiple testing) and 族系誤差率 (family-wise error rate, LM21), 循環區塊 (circular block) and 區塊自助重抽法 (block
  bootstrap, LM22), 資料偵伺 (data snooping, LM21).
- No 樂詞網 entry (searched 2026-10-24: "long-run variance", "expected maximum", "haircut", "deflated", "track record",
  "effective number" give nothing in statistics or mathematics): PSR, DSR, MinTRL and haircut stay in English in every
  box, glossed in plain Chinese (for example 考慮試驗次數後的夏普比率); 長期變異數 (long-run variance) is proposed as the
  book's own form, labelled so in the Glossary.

**Open before Stage 2** (each with the drafter's recommendation and evidence):

1. **Block size.** The book's rule takes the largest *stationary* estimate (lm22.md:254), which here is 22.41, so 22;
   Ledoit and Wolf use circular blocks, whose largest estimate is 25.65, so 26 [A33-32]. Recommendation: $b=26$, the
   rule applied to the scheme in use, said once in §6; the choice does not matter here, since $b=1$ to 100 give
   p-values 0.53 to 0.56 [A33-42]. Ledoit and Wolf's own calibration (Algorithm 3.1) is named, not run.
2. **The HAC kernel in (33.1) and (33.6).** Ledoit and Wolf use a prewhitened quadratic-spectral kernel with a $T/(T-4)$
   factor; the book has one long-run variance, (23.7) with Bartlett weights and its lag. Recommendation: Bartlett with
   $\ell=7$, Ledoit and Wolf's choice stated in one sentence; the lag curve of $\operatorname{SE}(\hat\Delta)$, 0.280 to
   0.243 over $\ell=0$ to 60 [A33-40], bounds what a kernel could change.
3. **Owners of the checkpoint's mean and volatility.** The shared decision gives LM33 the rules' Sharpe ratios,
   intervals and tests, LM30 the volatilities of R1, R3 and R5 and LM31 those of R6–R8; R2's and R4's volatilities and
   every rule's mean excess return have no owner. Recommendation: LM33 owns the mean excess returns, R2's and R4's
   volatilities and every standard error of the checkpoint, and echoes the five owned volatilities with their
   modules' names (they are the same `summary()` values, so no number can differ).
4. **$T$ against $T-1$** (the spine asks the brief to settle it). Recommendation: PSR, MinTRL and DSR as Bailey and
   López de Prado's code ($\sqrt{T-1}$, the "1 +"), with one sentence that (20.9)'s $\sqrt T$ moves R2's z-value by
   0.027% [A33-27]; the deflated benchmark uses the same $\sqrt{T-1}$.
5. **The effective number of trials** (the spine asks the brief to settle it). Recommendation: $n_{\mathrm{eff}}$ is the
   $n$ whose $\E Z_{(n)}$ equals experiment 2's mean maximum of eight correlated normals, 2.07 [A33-48]; the headline
   DSR stays at $n=8$ (0.955 [A33-46]) as the spine asks, labelled as assuming independence; Bailey and López de
   Prado's own recipe (the cross-section's SD, $\mathrm{SR}_0=0.21$, DSR 0.994 [A33-50]) is shown as the second
   correction; their eq. (9) reading, 2.25 [A33-48], is printed only if its formula is confirmed in the published text.
   Evidence: both corrections agree (0.994), and the cross-section's dispersion is what equal true ratios would give
   (0.141 against 0.144 [A33-50]).
6. **A DSR on the line.** 0.955, 0.951 and 0.948 by three defensible choices [A33-46]; the real $n$ at which DSR equals
   0.95 is 8.8 [A33-46]. Recommendation: print the number with its method and never a pass or fail; the module's verdict
   rests on the comparison with R1 (E7), which is not close.
7. **Lab data.** The shared decision gives the labs the rules' per-date weights and the wealth frame; LM33's lab needs
   each rule's net wealth path, which only the cost recursion (LM27's, in `vol5_rules.py`) produces. Recommendation:
   `make_lab_data.py` writes one derived file with the eight net wealth paths on the wealth frame's dates (statistics
   of FinMind data, built locally, never committed).
8. **Ledoit and Wolf's journal text.** The scheme is read in Working Paper 320 only. Recommendation: cite the JEF
   article with "read in IEW Working Paper 320", as SOURCES does for LM22, and compare the journal's §3 before Stage 3.
9. **Notation for §6 of AUTHORING.** HSR joins the row of PSR, DSR, MinTRL and PBO; $b$ (block size) and $\ell$ (lag)
   are LM33's two declared letters; $\hat V_{\mathrm{SR}}$, $\mathbf v_t$ and $\Psi$ are local. Recommendation: the
   cross-check decides; none clashes with a symbol LM33 uses in its book-wide meaning.
10. **The widget's quadrature.** The spine asks for closed forms with `Book.dist`; $\E Z_{(n)}$ has no closed form.
    Recommendation: module-local Simpson quadrature under 30 lines, tested against Python, with the closed-form
    approximation shown beside it.

## LM34 Backtesting Without Fooling Yourself

Stage 1 brief, drafted 2026-10-24 from the editor's spine (`plans/vol-5.md`, "### LM34 Backtesting Without Fooling
Yourself") and the shared decisions above it; continued the same day by a second drafter after the first stopped at a
usage limit (the script was kept and corrected, see the anchors' Status). Every number carries its anchor ID at first
appearance; `data/vol6_anchors_lm34.py` prints them all (36 rows, `## LM34` of `plans/vol-6-anchors.md`). Numbers
quoted from published modules carry their file:line; values another module owns ("Owners", shared decision "Through
case") are echoed with that module's name and anchor and are not LM34's to print. Rows A34-18 to A34-21 need LM34's
survivorship files, which are **pending registration** (Open O1); the brief quotes the values the script printed from
the drafter's scratch copies of exactly those files.

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
  $\mathrm{SR}=0$ gives a per-day standard error $1/\sqrt h$ for E10 and problem 12.
- LM21: (21.1) the t-stat with $s_{\mathrm u}$ (lm21.md:115); (21.2) its one-sided p-value (lm21.md:76); (21.6)
  Bonferroni's bound (lm21.md:267); (21.9) $\Pr(\max_iZ_i\le x)=\Phi(x)^m$ for independent normals (lm21.md:353),
  read as $n$ trials (shared notation decision); Experiment 10, 10,000 random long–short rules on TR23 with
  `default_rng([10, 20261011])`, best t-stat 3.97 (rule 7,840), 13 at or above 3 (lm21.md:359–364), recomputed
  [A34-22]; the rule that every module counts its tests.
- LM22: (22.3), the stationary bootstrap's geometric block lengths (lm22.md:189), and its `stationary_idx`
  (lm22.md:371–379), which §6 and the script reuse; (22.4), a bootstrap p-value as a share of resampled statistics
  (lm22.md:337); the book's block-length rule, "the largest stationary estimate among the squared demeaned
  simple-return series the statistic involves, rounded" (lm22.md:254), 145 for TR23 (lm22.md:427); TR23's exact
  in-sample Kelly root $\hat f^*=4.14$ (lm22.md:125, [[LM17]]'s), recomputed as 4.138 [A34-17].
- LM23: (23.1), OLS, for the performance-degradation slope of §7; "data snooping that [[LM34]] treats"
  (lm23.md:369).
- LM26: (26.2), the EWMA with $\lambda=0.94$ (lm26.md:99), for problem 8's daily scale; (26.8), QLIKE (lm26.md:361),
  named in §2 as the loss on which a volatility model's choice would be judged on later data (lm26.md:54,
  `make_lab26.py:1115`).
- LM27 (brief): E5's wealth frame, (27.1) drift, (27.2) the self-financing trade with
  $\operatorname{cost}(\mathbf x)=0.1425\%\lVert\mathbf x\rVert_1+\sum_i\text{tax}_i\max(0,-x_i)$, (27.3) $\mathrm{TO}_t$;
  R1 and R2; the first purchase (A27-23) and R1's largest rebalance (A27-24), echoed in E2.
- LM28–LM30 (briefs): R3 and R4 (LM28 unconstrained, LM29 long-only, the through-case form), R5 (LM30).
- LM31 (brief): R6, R7 and R8 ((31.7), R8's exposure $L_t$); R8's exposure path (A31-29), echoed in E3.
- LM33 (brief): the rules' Sharpe ratios, their tests against R1 and the deflated Sharpe ratio for $n=8$ with an
  effective number of trials, all cited by pointer in §6 and §8; LM34 prints none of them.

**Leads:** `[35, 45, 48, 49, 50]`: LM35 (the checkpoint's out-of-sample comparison and its costs: the protocol of §2,
(34.1); LM35's brief confirms), LM45 (frictions and financing costs in Kelly sizing, (34.1); the lab's walk-forward
Kelly), LM48 (the capstone's walk-forward comparison, §2's protocol, (34.3)), LM49 (from backtest returns to a size:
(34.3), (34.4) before any sizing), LM50 (monitoring a rule chosen from several, (34.4)). Volume VIII–IX briefs may
change the list; none is published.

**Forward links honoured.**

| Earlier text | Promise | Kept in |
|:--|:--|:--|
| lm04.md:209 | a grid search returns "the highest bump, which is largely noise" | §7, X7, E9: the declared grid's best, 18.62% a year against a median of 11.02% [A34-27]; PBO 0.663 [A34-29] |
| lm04.md:563 | "Backtests overstate Sharpe ratios ([[LM33]], [[LM34]])" | §6–§8: why the best of a search overstates (E7, E10); sizing from a haircut stays [[LM33]]'s and [[LM45]]'s |
| lm11.md:406 | an out-of-sample test fits on earlier data and judges on later data ([[LM34]]) | §2: the walk-forward protocol and its timing |
| lm17.md:51, lm21.md:57, lm25.md:54, lm26.md:54 | "Nothing is tested on later data ([[LM34]])" | §2 (one paragraph: what a test on later data needs, with LM26's model choice judged by (26.8) as the example) |
| lm18.md:50, 389 | a bootstrap is no test on later data ([[LM34]] tests on later data) | §2 (the protocol), §6 (the bootstrap used for a different job: a search's null) |
| lm21.md:373 | [[LM34]] tests the best rule of a search on later data (White 2000; Romano and Wolf 2005) | §6 (White, Romano–Wolf on the same data), §7 and §2 (later data); the sentence is reworded at Stage 4 |
| lm22.md:57 | "Nothing here is out-of-sample ([[LM34]])" | §2 |
| lm22.md:144 | "a walk-forward test is [[LM34]]'s" (of the Kelly fraction) | lab part 7: TR23's trailing Kelly root walked forward [A34-17] |
| lm22.md:352 | "Testing many strategies with the bootstrap (the reality check) is [[LM34]]'s" | §6, E7, E8 |
| lm23.md:369 | "Searching many sectors, rules or windows and keeping the best is the data snooping that [[LM34]] treats" | §6, §7 |
| research-hygiene.md:7, 62 | LM34 covers look-ahead and survivorship bias, costs, walk-forward testing and PBO | §2–§7, one each |
| research-hygiene.md:35 | "[[LM34]] gives Taiwan's official rates" | §3 and its sources (TWSE Operating Rules Art. 94; the Securities Transaction Tax Act Arts. 2 and 2-1) |
| `make_lab04.py:642` | the month-end Kelly walk-forward ("LM34 (walk-forward tests)") | lab part 7 (on TR23, as the spine decides; Lab 4 runs it on 0050) |
| `make_lab23.py:901` | choosing among many rules is the data snooping LM34 treats | §6–§7 |
| `make_lab25.py:836` | a year-by-year table is a stability check ("LM34 tests on later data") | §2 |
| `make_lab26.py:1115` | a GARCH variant chosen in sample ("LM34 tests such choices on later data") | §2, the same paragraph as (26.8) |

The grep of `src/*.md` and `src/pages/*.md` for `[[LM34]]` finds lm04:209, 563; lm11:406; lm17:51; lm18:50, 389;
lm21:57, 373; lm22:57, 144, 352; lm23:369; lm25:54; lm26:54; research-hygiene:7, 35, 62 (17 lines); the grep of
`build/make_lab*.py` for "LM34" finds make_lab04:642, make_lab23:14 (a style note), 901, make_lab25:836,
make_lab26:1115. The spine listed every one of them; the style note at make_lab23:14 holds no promise.

**Outcomes** ("After this module you should be able to:"; the level in brackets, shared decision "Outcome levels"):

1. [C] run a walk-forward backtest whose window, signal dates, trade timing, costs and valuation are fixed in advance, and report net wealth, log growth, turnover and costs
2. [D] derive the cost of a trade under Taiwan's commission and transaction tax, and prove that the log gap between gross and net wealth equals $-\sum\ln(1-\text{cost}/W^{\mathrm{pre}})$ when costs are scale-free
3. [C] detect look-ahead in a backtest (adjusted price levels, a close used before it is known, a full-sample parameter) and measure its effect by rerunning with the information available at each decision
4. [C] measure survivorship bias by fixing the universe from a dated list that includes delisted funds
5. [C] test whether the best of many rules beats a benchmark with White's reality check by the stationary bootstrap, and explain what Romano and Wolf's stepdown and Hansen's test add
6. [C] estimate the probability of backtest overfitting by combinatorially symmetric cross-validation on a declared grid, and read its logit distribution and performance degradation
7. [D] derive why the in-sample best of $n$ strategies without skill has a Sharpe ratio that grows with $n$ while its expected out-of-sample Sharpe ratio stays 0
8. [U] choose among the reality check, PBO and the deflated Sharpe ratio for a given question, and explain when the right conclusion is that the data do not support a rule

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
| 8 [U] | §8 | §8's checklist | KC §8, problem 6 |

**Owns.** The walk-forward protocol: the information set at each decision (the month-end close is known after 13:30,
so the trade is at the next close on which every fund trades; the rolling 504-row window; the first purchase from
cash; valuation without terminal liquidation), applied to R1–R8 with the cost model and its official sources (TWSE
Operating Rules Art. 94; the Securities Transaction Tax Act, Arts. 2 and 2-1, as amended 2025-01-02; the futures-ETF
rate, Open O2); the rules' net wealth, net log growth, turnover and costs, gross against net, the costs' tax share,
the sensitivity at twice the costs, R8's growth at borrowing spreads of 0, 2 and 5 points; the identity (34.1) and its
Deep Dive; look-ahead shown on data (in the text: adjusted prices rebuilt backward, (34.2), and the through case
traded at the signal's own close; in problems: a daily scale that uses the same day's close, a full-sample Kelly
root); survivorship on delisted Taiwan ETFs; White's reality check by the stationary bootstrap on Experiment 10's
10,000 rules and on the grid, with its studentized form, (34.4); Romano–Wolf's stepdown and Hansen's SPA *stated*
(their first step and statistic computed; the stepdown in the lab); the declared PBO grid, CSCV, (34.3), its logit
distribution and performance degradation; the noise benchmark and its (21.9) derivation; the widget. Values owned:
every A34 anchor except the echoes (A34-01 from `vol5_series`, A34-11's exposures from LM31's A31-29, A34-12's first
purchase and largest rebalance from LM27's A27-23 and A27-24, A34-22 recomputing LM21's Experiment 10, A34-17's 4.138
recomputing lm22.md:125).

**Leaves.** Sharpe-ratio standard errors, intervals and tests of the rules, the probabilistic and deflated Sharpe
ratios, effective trials and haircuts → LM33 (cited; LM34 prints no rule's Sharpe ratio). VaR, expected shortfall and
drawdowns of the rules → LM32. Scenario losses → LM35. R8's exposure path → LM31 (echoed). Kelly sizing of a
backtested strategy → LM45 and LM49; the capstone's walk-forward → LM48; monitoring and re-estimation → LM50. To the
lab (density, guidance): Romano–Wolf's full stepdown and the Kelly walk-forward on TR23. Not in the book, one sentence
each: slippage and market-impact models (no sourced spread or impact figure exists for these funds, shared decision
"Cost model"), purged and embargoed cross-validation (the through case has no overlapping labels), the multiple-testing
literature beyond White, Romano–Wolf and Hansen (Harvey, Liu and Zhu's hurdle is LM21's, lm21.md:25).

**Uses before taught** (one sentence each in the text):

- §2: "Choosing how much to lever a backtested strategy is [[LM45]]'s subject; LM34 only tests rules fixed in advance."
- §3: "Margin and the instruments that carry leverage are [[LM46]]'s; R8's borrowing rate here is illustrative."
- §6: "Romano and Wolf's stepdown and Hansen's test are stated without proof; both rest on large-$T$ bootstrap theory
  beyond this book."
- §8: "A walk-forward comparison with a Kelly-type rule among the candidates is [[LM48]]'s capstone."

**Data role.**

- **E5, the through case** (shared decision): `data/vol5_series.py`'s `frames("E5")` (`data/processed/vol5_frames.parquet`;
  FinMind `TaiwanStockPrice`, `TaiwanStockDividendResult` and `TaiwanStockSplitPrice`, registered 2026-10-24),
  estimation frame $T=2{,}362$ from 2017-01-18, $A=242.95$; wealth frame 2,368 sessions, $A_{\mathrm w}=243.57$
  [A34-01]. Rules from `data/vol5_rules.py` (imported, never re-implemented): 92 month-end signals, the first on
  2019-02-27 with the window 2017-02-13 → 2019-02-27, traded 2019-03-04; the last on 2026-09-30, traded 2026-10-01;
  1,851 daily returns 2019-03-05 → 2026-10-08; $\tau=7.5975$ years from the first trade [A34-02]. Gross paths remove
  commission and tax only (`cost_mult=0`; cash interest and R8's borrowing kept).
- **The PBO grid (declared 2026-10-24, before any result of it was computed; the drafter had seen only the through
  case's summary, `data/processed/vol5_rules.txt`).** Rules R1–R8 exactly as `vol5_rules.py` defines them (costs,
  cash, financing, valuation end, drift). Estimation window (trailing rows of E5's estimation frame through the
  signal): 126, 252, 504; R1 and R2 use none. Rebalancing every 1, 3 or 6 month-end signals from the through case's
  first signal (2019-02-27, traded 2019-03-04): the $q$-month version trades at signals 1, 1 + q, 1 + 2q, … of the
  through case's schedule (92, 31 and 16 trades [A34-26]). Configurations: R1 and R2 at three frequencies (6), R3–R8
  at three windows and three frequencies (54): $n=60$; the through case is 8 of them (R1, R2 monthly; R3–R8 at 504
  rows, monthly). Performance series: each configuration's daily net return on the wealth frame, 2019-03-05 →
  2026-10-08. CSCV: $S=16$ blocks of equal length, the earliest rows that do not fill a block dropped; each of the
  $\binom{16}{8}=12{,}870$ choices of 8 blocks is an in-sample set and its complement the out-of-sample set;
  performance is the Sharpe ratio of daily returns in excess of $r_f/A_{\mathrm w}$; the in-sample best $k^*$ (ties:
  the first in grid order); its out-of-sample rank $j$ among the 60 (1 = worst); $\omega=j/61$; logit
  $\ln(\omega/(1-\omega))$; PBO the share of splits with logit ≤ 0; performance degradation, the OLS slope of
  $k^*$'s out-of-sample Sharpe ratio on its in-sample one, and the share of splits with an out-of-sample ratio below 0.
  Grid order: R1 1m, 3m, 6m; R2 1m, 3m, 6m; then R3 … R8, each by window 126, 252, 504 and frequency 1, 3, 6. The
  declaration was written to the drafter's notes before the grid was run and is reproduced here unchanged; the text
  prints it in §7 as declared. The grid calls `signals()` with `vol5_rules.WINDOW` set for the call and restored, and
  checks that the 504-row signals equal the through case's; CLARABEL's cross-check failed once (R4, window 126,
  2025-06-30), and the polished OSQP solution was checked against the exact solution instead (gap 3.6e-17) [A34-26],
  which meets the shared solver rule.
- **TR23** (Volume III): `data/processed/vol3_taiex.parquet` (FinMind `TaiwanStockTotalReturnIndex`, TAIEX,
  retrieved 2026-10-18), 5,849 returns 2003-01-03 → 2026-10-08, $r_f=0$ (Volume IV). Uses: Experiment 10 recomputed
  with LM21's seed [A34-22]; the reality check on it (experiment 1, $\ell=145$, LM22's TR23 length) [A34-24]; problem
  8's daily volatility scale, 5,345 days 2005-01-11 → 2026-10-08 [A34-16]; the lab's Kelly walk-forward, 250
  month-ends 2005-12-30 → 2026-09-30, 5,104 days [A34-17].
- **0050's adjusted prices** (§4): `ohlc("0050")` with `data/raw/vol5/0050_dividends.csv` (filter `^息$`, PITFALLS §3)
  and the 2025-06-18 4-for-1 split from `splits__2016-12-01__2026-10-08.csv`, read directly; 20 distributions after
  2017-01-17 [A34-14]. The adjusted series is the book's own, (34.2), built from closes and distributions, so its
  levels are exact for a stated build date. FinMind's `TaiwanStockPriceAdj` (not registered; its levels change at
  every retrieval, PITFALLS §3) was compared by the drafter only as a check: its 2017-01-17 value differs from the
  book's by about 0.1%, which leaves §4's point unchanged; no FinMind adjusted level is printed.
- **Survivorship** (§5; capability B4; pending registration, O1): `TaiwanStockDelisting` (ids from "00"),
  `TaiwanStockPrice` snapshots of every ETF on 2017-01-17 and 2026-10-08, and the daily prices of the four futures
  ETFs that E5 does not hold (00672L, 00673R, 00674R, 00677U; 00635U and 00642U come from E5's own files), retrieved
  2026-10-24. The two snapshots are one-date queries without a `data_id`, which FinMind serves only above its Free
  tier (`list_datasets` marks `TaiwanStockPrice` "Free (w/ data_id)"; the owner's Sponsor plan served them), so only
  A34-18 reads them; A34-19 to A34-21 and the lab use Free files alone (O1). 69 ETFs had a row on 2017-01-17; 10 had
  none on 2026-10-08, each in the delisting list [A34-18]. A fund's
  growth factor skips untraded rows (close 0), checks every other close against the spread, and restates a
  registered split's previous close per new unit (00673R's and 00674R's reverse splits); none of the six pays
  distributions (no unexplained spread mismatch) [A34-19]. A delisted fund is valued at its last traded close, kept as
  cash at 0: its holders' actual liquidation payout is not in FinMind (O9).
- **Conventions.** Growth $g=\ln W_{\text{end}}/\tau$ from the cash of 1 at the first trade's close (the first
  purchase's cost counts; LM27's criteria); costs = the sum over trades of cost ÷ pre-trade wealth; turnover = the
  one-way $\mathrm{TO}$ of the 91 trades after the first purchase, summed, ÷ $\tau$ [A34-06]. CSCV Sharpe ratios use
  population moments over each half's days; annualized by $\sqrt{A_{\mathrm w}}$ only for display. t-stats (21.1)
  divide by $s_{\mathrm u}$. Quantiles `inverted_cdf`.
- **Guard and exact checks.** Counts against a threshold use the guard 1e-12 (t ≥ 3, bootstrap shares, logit ≤ 0).
  The identity (34.1) is checked on every rule: the largest gap is 1.3e-14 [A34-07]. No path is ruined (the script
  asserts $1+R_p>0$ on every day of every path, and $1+fR>0$ on TR23's scaled paths).
- **Seeds.** One generator per experiment, `default_rng([e, 20261011])`, created once: $e=1$ the reality check on
  Experiment 10 ($B=10{,}000$, $\ell=145$); $e=2$ the noise panels (200 panels of 60 strategies); $e=3$ the widget's
  grid (40 panels per state); $e=4$ the grid's reality check ($B=10{,}000$, $\ell=74$ by LM22's rule); $e=5$ its
  sensitivity at $\ell=17$. Experiment 10 keeps LM21's `default_rng([10, 20261011])`. Every Monte Carlo proportion
  prints its standard error $\sqrt{p(1-p)/B}$; the noise PBO prints the SD of the 200 panel values ÷ √200.
- **Published files** (plan). X2 stores weekly wealth points of the eight rules (every fifth session plus the last),
  under 100 KB; X9 stores every fifth split (2,574 points); X6 and X8 store bin counts only; the widget stores 30
  precomputed means and a test matrix. No raw FinMind value is published; the survivorship exhibit stores six growth
  factors.
- **Scripts.** `data/lm34_numbers.py` (every printed value, asserted against `src/lm34.md`, compared with the anchors,
  rounding flags) and `data/lm34_charts.py` (X2, X3, X5–X9 and the widget block, with a Node check of the widget's
  CSCV against Python's, as `data/lm15_charts.py` does); both after `data/vol3_series.py`, `data/vol5_series.py` and
  `data/vol5_rules.py` have written `data/processed/`, and after O1's registrations.

**Hygiene declaration.** *Out-of-sample:* the eight rules' results (windows, dates, timing, costs and criteria fixed in
advance on 2026-10-24, before any result was computed); the daily scale set at the previous close (problem 8) and the
Kelly walk-forward (lab), each a *hypothetical* rule judged on data after its estimate. *In-sample:* the 60-configuration
grid, by design, declared after the through case's results were seen, and the grid's reality check against R1; the
reality check on Experiment 10 is a *model* result on TR23's returns, as LM21 labels the experiment (lm21.md:364).
*Model:* Experiment 10, the noise panels, the widget's grid and simulator. *Descriptive:* fund histories, the ETF
lists, adjusted prices, the survivorship gap. Look-ahead versions (the signal's own close, the same-day scale, the
full-sample Kelly root) are labelled *look-ahead, not achievable*. Count of versions on the same data: the 8 rules
($n=8$, [[LM33]]'s count), 52 more grid configurations ($n=60$ in all), LM21's 10,000 random rules (recomputed), and
the variants labelled where they appear (gross, twice the costs, three borrowing spreads, the signal's own close; two
daily scales; four Kelly versions in the lab). Local note: "The eight rules' results are **out-of-sample**: their
windows, dates, costs and criteria were fixed on 24 October 2026, before any result existed. The 60-configuration grid
is **in-sample** by design and was declared after those results were seen. Experiment 10, the noise panels and the
widget are **model** results. Fund histories and adjusted prices are **descriptive**. This module compares 8 rules, 60
configurations and [[LM21]]'s 10,000 random rules on the same data, and corrects for the last two."

**Notation.** AUTHORING §6 with the "Portfolios, risk and backtests" table. Used: $R$, $r$, $T$, $t$, $A$,
$A_{\mathrm w}$, $N=5$ (E5's funds), $i$ (a fund), $W$, $W^{\mathrm{pre}}_t$ (LM27's), $\mathbf w$, $\mathbf f$,
$\mathbf w^{\mathrm{drift}}_t$, $\mathrm{TO}_t$, $\text{tax}_i$, $\lVert\mathbf x\rVert_1$, $L_t$ (R8's), $r_f$,
$\mathrm{SR}$, $\widehat{\mathrm{SR}}$, $g$, $G$, $\tau$ (a span in years, since $T$ is a count), $P$, $D$, $f$,
$\hat f^*$ (lab), $\bar\sigma_t$, $\hat\sigma_{t+1\mid t}$, $\lambda=0.94$ (only LM26's decay, problem 8), $\bar R$,
$s_{\mathrm u}$, $\text{t-stat}$, $\Phi$, $\Phi^{-1}$, $B$, $\ell$, $n$ (strategies tried; LM21's $m$ tests read as $n$
trials, shared notation decision), PBO. Local symbols, declared in the notation note:

| Symbol | Meaning | Check |
|:--|:--|:--|
| $W^{\text{net}}_t$, $W^{\text{gross}}_t$ | a rule's wealth with and without commission and tax (financing kept), from the cash of 1 at the first trade | superscripted §6 $W$; LM27's $W^{\mathrm{pre}}_t$ cited |
| $\operatorname{cost}$ | LM27's cost of a trade, (27.2); in (34.1) each term is one trade's cost ÷ its pre-trade wealth | an operator, not a scalar symbol (§6: no scalar cost symbol) |
| $G_{t,t'}$ | total-return growth factor from the close of $t$ to that of $t'$ | §6's $G$ with two dates |
| $P^{\mathrm{adj}}_{t\mid t'}$ | adjusted close of day $t$ in a series built on day $t'$, (34.2) | new; upright superscript |
| $k$, $n$ | a strategy (rule, configuration) and the number tried | §6's $n$ (Volume VI); LM34 writes no lag and no count of SDs, so $k$ is free |
| $\bar R_k$, $\bar R_{k,\text{boot}}$ | strategy $k$'s mean daily return (in excess of the benchmark's); its value on a resample | subscripted $\bar R$; "boot" as LM22's $\hat\theta_{\text{boot}}$, no star |
| $S$ | the number of CSCV blocks, 16 | Bailey et al.'s letter; LM34 has no SVD and no TAIEX close $S_t$ |
| $k^*$ | the in-sample best strategy of a split | star for an optimum (§6) |
| $j$, $\omega$ | $k^*$'s out-of-sample rank among the $n$ (1 = worst: $k^*$ is the $j$th smallest) and its relative rank $j/(n+1)$ | §6's $j$; $\omega$ displaces the sample-space outcome, which LM34 does not use |
| logit | $\ln(\omega/(1-\omega))$, written as a word | not $\lambda$ (LM26's decay appears in problem 8) |

Not used: $c$ (no Kelly fraction, and no scalar cost), $\lambda$ for the logit, a letter for White's statistic (written
$\max_k\sqrt T\,\bar R_k$; $V$ and "RC" are taken: $\mathrm{RC}_i$ is a risk contribution), $m$ for a block's length
(written $\lfloor T/S\rfloor$), $s_t$ for a split factor (written in words), $P$ for a probability, a star for a
bootstrap draw.

**Motivating case: "The grid's winner"** (box, about 150 words)

> From March 2019 to October 2026, the through case's eight rules grew between 8.70% (R3) and 14.49% (R2) a year,
> after Taiwan's commission and tax [A34-04]. Now vary each rule's estimation window (126, 252 or 504 sessions) and how
> often it trades (every 1, 3 or 6 months): 60 configurations [A34-26]. The best, maximum Sharpe on a 252-session
> window traded every six months, grew 18.62% a year, against 11.02% for the median configuration and 10.51% for the
> same rule as fixed in advance [A34-27]. Would you trade it? Three questions come first. Did the test use only what
> was known at each decision? Did its universe include the funds that later vanished? Of the six commodity and
> volatility futures ETFs listed in January 2017, two were delisted; the four survivors gained 5.4% in all, while the
> six together lost 27.7% [A34-20]. And how much of 18.62% is the search itself?

Resolved: (a) timing: §2's protocol and §4 (on monthly rules the signal's own close moves growth by −0.48 to +0.74
points [A34-36]; on a daily rule the same mistake turns 14.92% into 16.72% [A34-16]); (b) the universe: §5, E6, and E5's
own funds are among the survivors; (c) the search: §6–§7. No configuration's mean return beats R1's beyond chance (the
largest t-stat, 1.30, has a reality-check p-value of 0.375 [A34-32]), and the in-sample best ranks in the lower half
out of sample in 0.663 of the splits [A34-29]. The winner is the highest bump of lm04.md:209.

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | a backtest as an experiment with hidden choices; the layer LM34 adds (LM27–LM31 built the rules, LM33 measured their Sharpe ratios; LM34 tests the procedure that produced them); case + X1; roadmap; notation and hygiene notes | 320 |
| 2 | The Walk-Forward Protocol {1} | the information set at a decision; signal at a month-end close, known after 13:30, trade at the next close on which every fund trades (Research hygiene); rolling against expanding windows (one sentence; the through case rolls 504 rows); first purchase from cash; valuation without liquidation (its cost is not charged, said once); what "fixed in advance" fixes; a test on later data of a model choice, LM26's GARCH variants judged by (26.8), one paragraph; E1; X2; [[LM33]] tests the differences; pitfall: re-running a "fixed" test after a change is a second trial; 導讀; KC | 520 |
| 3 | Costs at Taiwan's Official Rates {2} | the rates and their sources (Art. 94: 0.1425% is the level above which a broker must give notice, not a cap; tax 0.1% on ETF sales, Art. 2; bond ETFs exempt to 2026-12-31, Art. 2-1, 00679B throughout; futures ETFs at 0.1%); (27.2) cited; the first purchase $0.001425/1.001425$; a round trip, 0.385% [A34-13]; E2; (34.1) with its Deep Dive; X3; the tax share; E3: twice the costs (why no slippage model: no sourced figure), R8's borrowing spreads; pitfall: one constant subtracted at the end (Research hygiene); 導讀; KC | 600 |
| 4 | Look-Ahead Bias {3} | definition: a rule may use only what was known when it acted; (34.2), adjusted levels change with the build date; E4, X4: returns from adjusted prices are total returns, levels are not; E5: the through case traded at the signal's own close, small and of either sign for monthly rules; the daily scale (problem 8) and the full-sample Kelly root (problem 9) named; pitfall: a statistic fitted to all data inside a rule; KC | 500 |
| 5 | Survivorship Bias {4} | a list of today's funds leaves out the vanished; TaiwanStockDelisting; X5; E6; E5's own universe: 00635U and 00642U were chosen in 2026 from survivors, and the leveraged oil fund 00672L was delisted in 2020; data policy: fix the universe from a dated list (Research hygiene's "Fix the universe"); the last close as a valuation (O9); funds that disappear tend to have done poorly (Elton, Gruber and Blake 1996, abstract); 導讀 (前視偏誤, 存活者偏誤); KC | 450 |
| 6 | Correcting a Search on the Same Data {5} | recap of [[LM21]]'s Experiment 10, (21.6) and (21.9) (no re-teaching); White's null (the best has no superiority over the benchmark) and statistic; recentred stationary resamples (LM22's (22.3)), (34.4), *stated without proof* (White 2000, Corollary 2.4); E7; X6; studentized form; Romano–Wolf's stepdown and Hansen's SPA stated (one paragraph each, no p-value of SPA until O3); E8: correlated rules, where the bootstrap's threshold 2.43 sits far below Bonferroni's 3.14 [A34-32]; the block-length rule and its sensitivity; pitfall: the reality check asks whether the best beats the benchmark, not which rules do; 導讀 (資料偵伺, 族系誤差率, 平穩自助重抽法); KC | 680 |
| 7 | The Probability of Backtest Overfitting {6,7} | the declared grid as declared; X7: the highest bump; CSCV definition box; (34.3); why $\binom{16}{8}=12{,}870$ (the paper prints 12,780) and which logits are possible; E9; X8; performance degradation, X9; what PBO measures (selection within a grid, not profit: its out-of-sample Sharpe ratio is below 0 in only 0.99% of splits [A34-29]); E10, the noise benchmark and (21.9)'s derivation; PBO's own noise (0.12 to 0.87 across noise panels [A34-33]); the widget; pitfall: adding configurations after a result is another search; 導讀 (過度配適, 交叉確認, 對數勝算, 秩); KC | 780 |
| 8 | Reading a Backtest {8} | the case resolved; a checklist (timing, universe, costs inside, the count of versions, reality check or PBO, [[LM33]]'s deflation); which tool answers which question; "the data do not support the rule" as a valid conclusion (guidance); the lab's Kelly walk-forward in one sentence; KC | 300 |
| 9 | Backtesting in Python {1,5,6} | `vol5_rules`' `wealth_path` with `cost_mult`; LM22's `stationary_idx` against arch's `StationaryBootstrap`; CSCV in NumPy: block sums, `itertools.combinations(range(16), 8)` and one mask product; lab box | 180 |
| — | Summary (8) / Problems (12) / Solutions | | 150 / 420 / 520 |
| | **Total** | | **5,420** |

**Elements.** 10 examples (E1 §2; E2, E3 §3; E4, E5 §4; E6 §5; E7, E8 §6; E9, E10 §7). Knowledge checks:

- §2: why does the first trade fall on 4 March 2019 and not on the signal day, 27 February? The signal uses that day's
  close, known only after 13:30, so the earliest trade is the next session's close on which every fund trades
  [A34-02].
- §3: R4's costs summed over 92 trades are 4.22% of wealth, and its gross growth exceeds the net by 0.56 points a year;
  why do $0.0422/7.5975$ and 0.56 points agree? By (34.1) the log gap is $-\sum\ln(1-\text{cost}/W^{\mathrm{pre}})$:
  0.0422296 against the sum 0.0422153, so the two differ only in the fifth decimal [A34-05, A34-07].
- §4: a screen buys 0050 when its trailing dividend yield exceeds 10%. On a series adjusted on 8 October 2026, 0050's
  2017 distributions yield 15.44% of the year-end close; on the actual close, 2.92% [A34-15]. Which number could the
  screen have seen in 2017, and why?
- §5: E5 holds 00642U, an oil futures ETF. Which oil fund listed in January 2017 did not survive, and what was it worth
  per unit of its first close when it was delisted? 00672L, delisted 13 November 2020, $G=0.038$ [A34-19].
- §6: on Experiment 10, White's p-value 0.283 and (21.9)'s 0.298 nearly agree [A34-23, A34-24]; on the grid the
  bootstrap's 95% point for the largest t-stat is 2.43 against Bonferroni's 3.14 [A34-32]. Why the difference? The
  random rules are independent by construction; the grid's differences from R1 correlate with median 0.78.
- §7: with $n=60$, which logits can occur, and why is none exactly 0? $\ln(j/(61-j))$ for $j=1,\dots,60$: from
  −4.094 to 4.094, and $\omega=j/61$ is never $\tfrac12$ (at $j=30$ and 31 the logit is ∓0.0328) [A34-35].
- §8: the grid's PBO is 0.663 while the in-sample best's out-of-sample Sharpe ratio is below 0 in only 0.99% of the
  splits [A34-29]. What does each number say about the search, and what about the rules?
- §9: how many rows does `combinations(range(16), 8)` yield, and why does the code multiply a 12,870 × 16 mask by the
  16 block sums instead of summing each split's days? 12,870; each split's sums are a fixed combination of the block
  sums, so one product gives them all [A34-35].

中文導讀 in §2 (回測 (backtest), 滾動前進測試 (walk-forward test), 樣本外 (out of sample)), §3 (交易成本 (transaction
cost), 手續費 (commission), 證券交易稅 (securities transaction tax), 週轉率 (turnover)), §5 (前視偏誤 (look-ahead
bias), 存活者偏誤 (survivorship bias), 下市 (delisting)), §6 (資料偵伺 (data snooping), 族系誤差率 (familywise error
rate), 平穩自助重抽法 (stationary bootstrap)), §7 (過度配適 (overfitting), 交叉確認 (cross-validation), 對數勝算
(logit), 秩 (rank)). Deep Dives: §3 "The log gap between gross and net wealth": with scale-free costs and the same
targets, the two paths hold the same exposures after every trade and earn the same percentage returns between trades
(cash interest and borrowing included), so wealth differs only by the factors $1-\text{cost}/W^{\mathrm{pre}}$ at the
trades; hence (34.1), and the bound by $\ln(1-x)\le-x$. §6 "Why the resamples are recentred": the null that no
strategy beats the benchmark is tested at its least favourable point, every mean difference 0, so each resampled mean
is measured from its own sample mean; consistency is *stated without proof* (White 2000, Theorem 2.3 and Corollary
2.4). §7 "Counting the splits": $\binom{16}{8}$ by symmetry and Pascal's rule, and why the halves are complementary,
so that for means the out-of-sample sum is the full-sample sum minus the in-sample one.

**Exhibits.**

- X1 `case` (table, §1): the grid's winner against the through case. Rows: R4 as fixed in advance (504 rows,
  monthly) 10.51% a year, rank 39 of 60; the grid's best (R4, 252, every 6 months) 18.62%; second (R4, 126, 6
  months) 17.38%; median 11.02%; worst (R7, 126, monthly) 7.60% [A34-27]; R2 as fixed 14.49%, rank 8 [A34-04,
  A34-27]; PBO 0.663 [A34-29]; reality-check p-value of the best t-stat against R1, 0.375 [A34-32]; the six futures
  ETFs held from 17 January 2017: all −27.7%, survivors +5.4% [A34-20]. Note: E5's wealth frame, net of commission
  and tax, 5 March 2019 to 8 October 2026; the grid is in-sample by design; survivorship rows descriptive. Source:
  FinMind `TaiwanStockPrice`, `TaiwanStockDividendResult`, `TaiwanStockSplitPrice` (E5, registered 2026-10-24) and
  `TaiwanStockDelisting` (retrieved 2026-10-24); Computations: `data/lm34_numbers.py`.
- X2 `wealth` (line, date axis with shared `x.values`, §2): net wealth of the eight rules from the cash of 1 at 4
  March 2019 to 8 October 2026, weekly points; R1 (colour 1), R2 (2), R4 (3), R8 (4) named, R3, R5, R6 and R7 as
  `quiet` lines named in the caption. Values cited: final wealth 2.662, 3.008, 1.937, 2.221, 2.040, 2.272, 2.183,
  2.412 [A34-03]. Note: out-of-sample, fixed in advance; no terminal liquidation.
- X3 `grossnet` (bar, `stack: true`, approved C1, §3): categories R1–R8; series "net growth" (colour 1) and
  "commission and tax" (colour 2, gross minus net), so each bar's total is the gross growth and its label shows it;
  `fmt: "pct2"`. Values cited: net 12.89%, 14.49%, 8.70%, 10.51%, 9.38%, 10.80%, 10.28%, 11.59% [A34-04]; gross 12.99%,
  14.58%, 8.85%, 11.06%, 9.52%, 10.91%, 10.44%, 11.99% [A34-05]. Note: gross keeps cash interest and R8's borrowing;
  the tax share of the costs is 17% to 22% [A34-09].
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
  0.1; a second series, (21.9)'s density of the largest of 10,000 independent standard normals; dashed `vline`s at the
  observed 3.97 [A34-22], the bootstrap 95% point 4.77 [A34-25] and (21.9)'s 4.41 [A34-23]. Note: model on TR23's
  returns; $B=10{,}000$, `default_rng([1, 20261011])`, mean block 145; p-values 0.283 (White) and 0.281 (studentized),
  MC SE 0.0045 [A34-24, A34-25].
- X7 `bumps` (scatter, §7): the 60 configurations' net growth; x the rule (ticks at R1…R8 with `tickLabels`, windows
  offset within a rule), series by frequency "monthly", "3 months", "6 months" (colours 1–3); the through case's
  eight as marked `points`; dashed `hline` at the median 11.02%. Values cited: best 18.62%, second 17.38%, worst 7.60%
  [A34-27]; R4's configurations from 10.51% to 18.62%, R1's from 12.85% to 12.96% [A34-28]. Note: in-sample by
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
(for example $n=60$: 0.51 at a true ratio of 0, 0.05 at 2, flagged). Initial state (PDF): $n=60$, ratio 0, seed 1. Data block
`chart-lm34-pboSim`: the 30 means, their largest SE 0.051 [A34-34], and a 160 × 5 test matrix with its Python logits,
against which `data/lm34_charts.py` checks the widget's CSCV in Node. Cost: $1{,}851\times100$ draws and
$12{,}870\times100$ comparisons at most, well within the PDF printer's wait. *Model*; the simulator's draws are not
NumPy's, so its panel values differ from experiment 3's while their means agree within the printed SE.

**Examples** (results recomputed from the printed inputs):

- E1 §2 `netresults`, the through case net of costs: final wealth R2 3.008, R1 2.662, R8 2.412, R6 2.272, R4 2.221,
  R7 2.183, R5 2.040, R3 1.937 [A34-03]; growth 14.49%, 12.89%, 11.59%, 10.80%, 10.51%, 10.28%, 9.38%, 8.70% a year over
  $\tau=7.5975$ years [A34-02, A34-04]; turnover from 0.18 a year (R2) to 1.45 (R4) [A34-06]; ranking R2 > R1 > R8 >
  R6 > R4 > R7 > R5 > R3 [A34-08]. The two rules without estimates lead; whether any difference beats chance is
  [[LM33]]'s test.
- E2 §3 `costs`: the first purchase costs $0.001425/1.001425=0.1423\%$ of wealth (LM27's A27-23); a round trip of
  NT\$1,000,000 in 0050 costs NT\$1,425 + NT\$1,425 + NT\$1,000 = NT\$3,850, 0.385%, and NT\$2,850 in 00679B [A34-13];
  R1's 91 later rebalances turn over 1.96% of wealth on average (the largest 8.06%, LM27's A27-24) and cost 0.0073%
  each [A34-12]; summed over 92 trades the costs are 0.81% of wealth for R1 and 4.22% for R4, and (34.1) gives R1's log
  gap 0.0080768 against the sum 0.0080755 [A34-07]; the tax is 17% to 22% of the costs [A34-09].
- E3 §3 `twice`: at twice the costs R4 falls 0.56 points to 9.95% and drops below R7; R1 loses 0.11 points (12.78%);
  the order becomes R2 > R1 > R8 > R6 > R7 > R4 > R5 > R3 [A34-10]. R8's growth at borrowing spreads of 0, 2 and 5
  points: 11.99%, 11.59%, 10.99% [A34-11]; R8 borrows at 62 of its 92 trades (LM31's A31-29, echoed in A34-11).
- E4 §4 `adjusted`: 0050 closed at 72.30 on 17 January 2017. In an adjusted series built on 2 January 2020 that day
  shows 65.12; built on 31 December 2024, 55.20; built on 8 October 2026, after 20 distributions and the 4-for-1 split,
  13.25 [A34-14]. Its February 2017 distribution of NT\$1.70 yielded 2.32% of the previous close but reads as 12.65%
  on today's adjusted series [A34-15]. Returns from either series agree; only the levels moved.
- E5 §4 `sameclose`: trade every signal at the signal day's own close (impossible: the close is known only after
  13:30). Growth from the cash of 1 at 27 February 2019: R1 13.01%, R2 14.44%, R4 10.03%, R8 12.33%; changes from the
  through case run from −0.48 points (R4) to +0.74 (R8) [A34-36]. For monthly rules the one-day shift is small and of
  either sign; problem 8 shows a daily rule where the same mistake is large.
- E6 §5 `survivors`: of 69 ETFs with a row on 17 January 2017, 10 had none on 8 October 2026, and each is in the
  delisting list [A34-18]. The six commodity and volatility futures ETFs of January 2017: equal amounts held to 8
  October 2026 grew to 0.723 (−27.7%, −3.33% a year); the four survivors to 1.054 (+5.4%, +0.54% a year); the gap is
  3.87 points a year over 9.7221 years [A34-20]. E5's 00635U and 00642U are two of the survivors.
- E7 §6 `rc10`, Experiment 10 corrected: the best t-stat 3.97 [A34-22]; its one-sided p-value $3.5\times10^{-5}$,
  Bonferroni's 0.354, (21.9)'s 0.298 [A34-23]; White's reality check (stationary bootstrap, $\ell=145$, $B=10{,}000$,
  `default_rng([1, 20261011])`) 0.283, studentized 0.281, both with MC SE 0.0045; the bootstrap's 95% point for the
  largest t-stat 4.77, so Romano and Wolf's first step rejects no rule [A34-24, A34-25]. The best of 10,000 random rules
  is what chance gives.
- E8 §6 `rcgrid`, the grid against R1 monthly: the largest t-stat of the 59 mean differences is 1.30 (R4, 126, every
  6 months), one-sided p-value 0.0975, Bonferroni's 1; the studentized reality check with $\ell=74$ (LM22's rule over
  the 60 configurations; R4 126 monthly gives 73.50) has p-value 0.375 (MC SE 0.0048), and at R1's own $\ell=17$,
  0.421 (MC SE 0.0049); the bootstrap's 95% point is 2.43 against Bonferroni's 3.14, because the differences correlate
  with median 0.78 [A34-32].
- E9 §7 `pbo`, CSCV on the declared grid: 16 blocks of 115 days (11 earliest days dropped), 12,870 splits; PBO 0.663;
  logits' median −0.72; $k^*$'s out-of-sample Sharpe ratio is below 0 in 0.99% of the splits; its mean annualized
  ratio falls from 1.31 in sample to 0.80 out of sample; the slope of out-of-sample on in-sample is −0.86 [A34-29].
  The in-sample best is most often R2 monthly (19.1% of splits), R4 252 6m (18.8%) and R4 126 6m (13.8%), 31
  configurations in all [A34-30].
- E10 §7 `noise` (*Model*): 200 panels of 60 independent strategies with zero mean over the same 1,851 days
  (`default_rng([2, 20261011])`): PBO 0.505 (SE 0.012), from 0.12 to 0.87 across panels; $k^*$'s annualized Sharpe
  ratio averages 1.20 in sample and −0.001 out of sample; (21.9) with a per-day standard error $1/\sqrt{920}$ ((20.9)
  at SR 0) predicts a median in-sample best of 1.17 [A34-33]. PBO near one half is what no skill gives; one panel's
  PBO can sit anywhere from 0.12 to 0.87.

**Problems plan** (12; MC keys B, A, C, B, A, C; the lab solves 9, 11 and 12). Stems state the sample (E5's wealth
frame, 5 March 2019 → 8 October 2026, net of commission 0.1425% each side and tax 0.1% on sales, 0 for 00679B; or
TR23, 2003–2026, $r_f=0$), the window, the rebalancing dates and the label (shared decision "Problems"), the seed and
draws, and the rounding.

1. MC: NT\$1,000,000 of 0050 bought and later sold at the same price, commission 0.1425% on each side, tax 0.1% on the
   sale; the round-trip cost. A NT\$2,850 (commission only: the 00679B case). **B** NT\$3,850. C NT\$2,425 (one side's
   commission plus the tax) [A34-13].
2. MC: a first purchase from cash at commission 0.1425%, self-financing; cost ÷ pre-trade wealth. **A** 0.1423%. B
   0.1425% (ignores that the cost reduces the amount bought). C 0.2850% (a round trip's commission) [A34-12, A34-13].
3. MC: CSCV with 16 blocks; the number of splits. A 12,780 (the figure the paper prints; `plans/vol-5.md:250`). B 65,536 (every subset of the
   blocks). **C** 12,870 [A34-35].
4. MC: $n=60$ configurations; the in-sample best ranks 31st of 60 out of sample (1 = worst); its logit. A −0.0328
   (counts the rank from the best). **B** 0.0328. C 4.094 (uses its in-sample rank, 60) [A34-35].
5. MC: the best of 10,000 independent null t-stats is 3.9738; (21.9)'s probability that the maximum reaches it.
   **A** 0.298. B $3.5\times10^{-5}$ (one test's p-value). C 0.354 (Bonferroni's bound) [A34-23].
6. MC: a grid's PBO is 0.663, and its in-sample best earns a negative out-of-sample Sharpe ratio in 0.99% of the
   splits. The best reading: A every configuration is overfit and loses money out of sample. B the reality check must
   reject. **C** picking the in-sample best adds nothing over the grid's typical member, while the members' common
   positive return is not the search's doing [A34-29].
7. Derive (34.1) for scale-free costs and the same targets, and show $\sum\text{cost}/W^{\mathrm{pre}}\le\ln(W^{\text{gross}}
   /W^{\text{net}})$; check on R1 (0.0080755 against 0.0080768) and R4 (0.0422153 against 0.0422296) [A34-07].
8. Look-ahead in a daily rule (TR23, $r_f=0$, cash and borrowing at 0): the scale $\min(1.5,\bar\sigma_t/\hat\sigma_{t+1\mid
   t})$, $\bar\sigma_t^2$ the uncentred mean square of the last 504 returns, $\hat\sigma$ by (26.2) with $\lambda=0.94$.
   Set at the previous close it grows 14.92% a year (volatility 18.21%, worst day −7.70%); computed with the same day's
   return, 16.72% (17.02%, −4.93%) [A34-16]. On 7 April 2025 TR23 fell 9.70%: the scales were 0.725 and 0.428, the
   scaled returns −7.03% and −4.15% [A34-16]. Which version could a trader run, and why does the other look safer?
   The solution adds that TR23 itself grew 13.34% with volatility 18.62% over the same days [A34-16].
9. A full-sample parameter (lab): the exact Kelly root of (4.5) on all of TR23 is 4.138; held from 2005-12-30 it grows
   31.42% a year, against 21.75% for the trailing 729-return root capped to [0, 3] and 13.31% for $f=1$; borrowing at
   3.5% a year on $f-1$ turns 31.42% into 20.43% and 21.75% into 16.11% [A34-17]. (a) Why is 31.42% not a backtest
   result? (b) What does the borrowing rate change, and why is even 16.11% *hypothetical*? (c) State the protocol behind 21.75% (window, signal and trade dates, label).
10. Survivorship: the six growth factors of X5 [A34-19]; equal amounts on 17 January 2017; compute the mean of all six
    and of the four survivors and the gap in log growth over 9.7221 years: 0.723, 1.054, 3.87 points a year [A34-20].
11. Python: White's reality check on Experiment 10 with LM22's `stationary_idx` (`default_rng([1, 20261011])`,
    $B=10{,}000$, $\ell=145$): p-value 0.283 (MC SE 0.0045); studentized 0.281 [A34-24, A34-25]. Then the grid against
    R1 at $\ell=74$ and 17: 0.375 and 0.421 [A34-32]; why LM22's rule takes the largest length.
12. Derive with (21.9) and (20.9) the median of the in-sample best's annualized Sharpe ratio for $n=60$ independent
    zero-skill strategies over 920 in-sample days, $\Phi^{-1}(0.5^{1/60})\sqrt{A_{\mathrm w}/920}=1.17$, and say why its
    expected out-of-sample value is 0; check against E10's 1.20 and −0.001 (`default_rng([2, 20261011])`, 200 panels)
    [A34-33].

**Lab parts** (`build/make_lab34.py`; reads only its `data/`, built by `data/make_lab_data.py`: the rules' per-date
targets and the wealth frame (the shared derived files of the Labs decision), the grid's 60 daily net-return series
(`lm34_grid.csv`, a new derived file, O7), `taiex_tr.csv` (TR23), `0050_daily_raw.csv` and `0050_dividends.csv`, and
after O1 the delisting list and the six futures funds' prices, all Free (the snapshots are not lab files)): 1 the protocol: rebuild R1's net path from its targets with (27.2), check it against
the derived wealth, E1, X2; 2 costs: (34.1) for every rule, X3, E3; 3 look-ahead: X4 and E4 from the closes and
distributions, problem 8 on TR23; 4 survivorship: X5, E6, problem 10; 5 the reality check: E7 (experiment 1), problem
11, Romano–Wolf's stepdown on Experiment 10 (the stepdown's details checked in the original first, O3); 6 CSCV: E9,
X8, X9 from `lm34_grid.csv`, E10 on 20 panels; 7 the Kelly walk-forward on TR23 (lm22.md:144, `make_lab04.py:642`):
problem 9, labelled *hypothetical* (daily rebalancing to the month's leverage, no trading costs, borrowing at 0 or
3.5%); 8 problems 9, 11, 12. Extension (*In-sample*, declared first): add a fourth window (756 rows) to the grid, write
the declaration before running it, and recompute PBO and the reality check with $n=78$; a closing sentence says that
the extension is another search on the same data. Labs write plain "LM33", "LM45", never `[[…]]`.

**Cross-module tags.**

- (34.1) $\ln\big(W^{\text{gross}}_T/W^{\text{net}}_T\big)=-\sum_{\text{trades}}\ln\big(1-\operatorname{cost}/W^{\mathrm{pre}}\big)
  \ge\sum_{\text{trades}}\operatorname{cost}/W^{\mathrm{pre}}$, for scale-free costs, both paths trading to the same
  targets, and financing proportional to wealth (LM35, LM45, LM48).
- (34.2) $P^{\mathrm{adj}}_{t\mid t'}=P_{t'}/G_{t,t'}$ with $G_{t,t'}$ the total-return growth factor (Volume I's
  $(P_t+D_t)/(P_{t-1}/s)-1$ compounded); it depends on the build date $t'$, so a level from an adjusted series is
  look-ahead for any rule acting before $t'$ (LM48, LM49).
- (34.3) CSCV and $\mathrm{PBO}=\#\{\text{splits with logit}\le0\}/\binom{S}{S/2}$, logit $=\ln\big(\omega/(1-\omega)\big)$,
  $\omega=j/(n+1)$ (LM48, LM49, LM50).
- (34.4) White's reality check: the share of $B$ recentred stationary resamples with
  $\max_k\sqrt T(\bar R_{k,\text{boot}}-\bar R_k)\ge\max_k\sqrt T\,\bar R_k$ ($\bar R_k$ in excess of the benchmark);
  studentized with $s_{\mathrm u,k}/\sqrt T$; valid for large $T$ under stationarity (*stated without proof*, White
  2000) (LM49, LM50).

**Pitfalls to pre-empt.**

- Timing: the signal's close is known only after 13:30; a trade at that close is look-ahead (E5). A daily rule that
  uses the same day's return in its own scale looks safer and richer than any trader could be (problem 8).
- Adjusted prices: returns are fine, levels depend on the build date (34.2); never quote an adjusted level without
  its build date, and never feed one to a rule that acts earlier (E4; PITFALLS §3).
- Universe: E5 itself was chosen in 2026 from survivors; say so once in §5, do not change the fixed through case.
  A delisted fund is valued at its last close, an approximation (O9).
- Costs: inside the recursion, never a constant subtracted at the end (Research hygiene); 0.1425% is the notice
  level of Art. 94, not a cap, and brokers' discounts are not modelled; no slippage model, and the text says why the
  twice-the-costs sensitivity stands in for it; the bond-ETF exemption runs to 2026-12-31 as the law reads on
  2026-10-24 (an Executive Yuan draft of 2026-10-01 to extend it is not law).
- The reality check asks whether the best beats the benchmark; a large p-value does not show that the rules are
  equal, and a small one does not say which rules beat it. Its block length follows LM22's rule; report the
  sensitivity (0.375 against 0.421, E8) [A34-32].
- PBO measures how well in-sample ranks carry over within one grid, not whether the rules make money (E9); one
  sample's PBO is itself noisy (0.12 to 0.87 across noise panels, E10) [A34-33]. Adding configurations after seeing results is a
  new search: count it.
- CSCV's count is $\binom{16}{8}=12{,}870$; the paper prints 12,780 (shared decision "References").
- The Kelly walk-forward borrows for free unless the stem says otherwise; its leverage sits at the cap of 3 in 178 of
  250 months [A34-17], so the cap, chosen in LM4's lab, drives the result.
- Ownership: no rule's Sharpe ratio, volatility, VaR or drawdown is printed (LM33, LM30–LM31, LM32); R8's exposures
  are LM31's and the single trades LM27's, echoed with their anchors.
- Rounding (flagged anchors, print as rounded from the unrounded values): R2's 14.49%, R4's 10.51%, R5's 9.38%, R7's
  10.28% [A34-04]; R4's gross minus net 0.56 points [A34-05]; R1's turnover 0.24 [A34-06]; R5's, R7's and R8's costs
  1.03%, 1.28%, 3.06% [A34-07]; 15.44% [A34-15]; the scale 0.725 and TR23's 18.62% [A34-16]; 2.57 [A34-17]; 1.593 and
  0.038 [A34-19]; the grid's best t-stat 1.30 [A34-32]; seven of the widget's 30 means [A34-34]. Never print a
  difference of two printed rounded values (for example the two scales' growth gap) unless the script prints it.
- References: White (2000) read in the original for its statistic and p-value (Corollary 2.4, the p-value $1-M/N$);
  Romano and Wolf (2005) and Hansen (2005) at the abstract level until O3; Bailey, Borwein, López de Prado and Zhu for
  CSCV; Elton, Gruber and Blake (1996) only for its abstract's claim; Brown, Goetzmann, Ibbotson and Ross (1992)
  bibliographic only (Sources).

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

**Stage 4 for earlier modules.**

- `leads`: lm04.md:6 gains 34 and lm11.md:6 gains 34 (both on the plan's list); lm20.md:6 gains 34 ((20.9), E10 and
  problem 12; new). lm17, lm18, lm21, lm22, lm23, lm25 and lm26 already list 34.
- lm21.md:373 (on the plan's list), proposed wording: "[[LM4]] warned that backtests overstate Sharpe ratios. [[LM33]]
  deflates a Sharpe ratio for the number of trials. [[LM34]] corrects a search on the same data (White 2000; Romano
  and Wolf 2005) and tests the best rule on later data."
- No other wording change: lm04.md:209's "largely noise" agrees with E8 and E9; research-hygiene.md:35 and 62 are kept
  by §3–§7; `make_lab04.py:642` stays on 0050 (Lab 4's own data), and LM34's lab says that it repeats the exercise on
  TR23's longer history.

**Sources** (full citations; how each was checked; paraphrase only, never more than a sentence quoted):

- White, H., "A Reality Check for Data Snooping", *Econometrica* 68(5): 1097–1126, September 2000, DOI
  [10.1111/1468-0262.00152](https://doi.org/10.1111/1468-0262.00152). In SOURCES ("LM21"); Crossref re-read
  2026-10-24 (volume, issue, pages); the article read in a copy by the drafter (2026-10-24): the statistic is the
  maximum over models of $\sqrt n$ times the mean performance against the benchmark, its bootstrap counterpart the
  maximum of the recentred resampled means (Corollary 2.4), and the p-value is one minus the rank of the observed
  statistic among the sorted resampled ones over their number; the resamples use Politis and Romano's stationary
  bootstrap. Used for (34.4) and §6's Deep Dive.
- Romano, J. P., and M. Wolf, "Stepwise Multiple Testing as Formalized Data Snooping", *Econometrica* 73(4):
  1237–1282, 2005, DOI [10.1111/j.1468-0262.2005.00615.x](https://doi.org/10.1111/j.1468-0262.2005.00615.x). In
  SOURCES; Crossref re-read 2026-10-24; abstract (OpenAlex record, 2026-10-24): a stepwise procedure that
  asymptotically controls the familywise error rate, studentization advocated, set as strategies against a benchmark.
  The stepdown's steps are not read in the original (O3): §6 states the idea; the lab's code waits for O3.
- Hansen, P. R., "A Test for Superior Predictive Ability", *J. Business & Economic Statistics* 23(4): 365–380, 2005,
  DOI [10.1198/073500105000000063](https://doi.org/10.1198/073500105000000063). In SOURCES (bibliographic); Crossref
  and the OpenAlex abstract read 2026-10-24: a studentized statistic and a sample-dependent null distribution make the
  test more powerful than the reality check and less sensitive to poor alternatives. **UNVERIFIED:** the threshold
  $-\sqrt{2\ln\ln T}$ that the script uses to select the recentred rules (A34-25); not relied on (O3).
- Politis, D. N., and J. P. Romano, "The Stationary Bootstrap", *JASA* 89(428): 1303–1313, 1994; Politis and White
  (2004) and Patton, Politis and White (2009) for the block length: in SOURCES ("LM22"), Crossref re-read 2026-10-24.
- Bailey, D. H., J. M. Borwein, M. López de Prado and Q. J. Zhu, "The probability of backtest overfitting", *Journal of
  Computational Finance*, DOI [10.21314/JCF.2016.322](https://doi.org/10.21314/JCF.2016.322). Crossref (2026-10-24):
  authors, title and journal; issued 2016-09; Crossref holds no volume or pages. Volume 20(4): 39–69 and the
  $\binom{16}{8}$ misprint are the editor's verified entries (`plans/vol-5.md`, "References"); the year to print (2016
  online or the print issue's year) is to be confirmed with the volume (O8). Abstract (OpenAlex, 2026-10-24): PBO is
  estimated by combinatorially symmetric cross-validation. Used for (34.3) and §7.
- Elton, E. J., M. J. Gruber and C. R. Blake, "Survivor Bias and Mutual Fund Performance", *Review of Financial
  Studies* 9(4): 1097–1120, 1996, DOI [10.1093/rfs/9.4.1097](https://doi.org/10.1093/rfs/9.4.1097). Crossref and the
  OpenAlex abstract (2026-10-24): funds that disappear tend to do so after poor performance; the study tracks every
  fund that existed at the end of 1976. One sentence in §5.
- Brown, S. J., W. Goetzmann, R. G. Ibbotson and S. A. Ross, "Survivorship Bias in Performance Studies", *Review of
  Financial Studies* 5(4): 553–580, 1992, DOI [10.1093/rfs/5.4.553](https://doi.org/10.1093/rfs/5.4.553). Crossref
  (2026-10-24) only: the abstract OpenAlex holds describes a 1994 conference presentation, not this article, so no
  claim rests on it. Optional, bibliographic.
- Sullivan, Timmermann and White (1999), *JF* 54(5): 1647–1691: in SOURCES ("LM21"); one sentence in §6 (the reality
  check applied to technical trading rules).
- Bailey and López de Prado (2014), the deflated Sharpe ratio, *JPM* 40(5): 94–107, and Harvey and Liu (2015),
  "Backtesting", *JPM* 42(1): 13–28: Crossref re-read 2026-10-24; LM33's, cited by pointer only.
- 證券交易稅條例 (Securities Transaction Tax Act), as amended 2025-01-02 (民國114年01月02日), Art. 2 (0.1% on "corporate
  bonds and other securities approved by the government", which covers fund certificates) and Art. 2-1 ¶2 (sales of
  bond ETFs issued by securities investment trust enterprises exempt from 2017-01-01 to 2026-12-31, leveraged and
  inverse ones excluded): [law.moj.gov.tw, pcode G0340078](https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=G0340078),
  read 2026-10-24 by the drafter.
- 臺灣證券交易所股份有限公司營業細則 (TWSE Operating Rules), version 115.09.24, Art. 94: brokers set their own rates
  and must notify a client before the order when the rate exceeds 1.425‰ of the value traded:
  [twse-regulation.twse.com.tw, FID FL007304](https://twse-regulation.twse.com.tw/m/LawContent.aspx?FID=FL007304), read
  2026-10-24 by the drafter.
- TWSE, the 原型期貨 ETF (futures ETF) page, read 2026-10-24 by the drafter (URL not recorded; the editor records it
  with O2): futures ETFs are issued by domestic futures trust enterprises under the futures trust fund rules; their
  code ends in U and their short name starts with 期; rolling futures in contango causes losses the manager cannot
  avoid, and the page says they are unsuited to long holding. Used in §5 (one sentence on why these funds shrink).
- 財政部統計處 統計通報 (Ministry of Finance, statistics notice) of 2024-11-14 on ETF trading and tax, as reported by
  [CNA, 2024-11-14](https://www.cna.com.tw/news/afe/202411140244.aspx) (read 2026-10-24): ETFs' tax rate is below
  stocks', and bond ETFs are exempt from 106 to 115 (2017–2026). The report does not mention futures ETFs; the shared
  decision's reading of the notice itself (futures ETFs among the ETFs taxed at 千分之1) is the editor's survey's, not
  re-read here (O2).
- FinMind datasets `TaiwanStockPrice`, `TaiwanStockDividendResult`, `TaiwanStockSplitPrice`,
  `TaiwanStockTotalReturnIndex` and `TaiwanStockDelisting` (retrieval dates under Data role), cited in every exhibit's
  Source line; arch's `optimal_block_length` and `StationaryBootstrap` (SOURCES, "Python (Volume IV)").
- Not relied on: Bailey, Borwein, López de Prado and Zhu, "Pseudo-Mathematics and Financial Charlatanism", *Notices of
  the AMS* 61(5), 2014, DOI 10.1090/noti1105 (Crossref gives the first page, 458, only).

**Chinese terms** (樂詞網, searched 2026-10-24 by the drafter, all listings and 統計學名詞; the shared decision's list
for the rest):

| English | 樂詞網 | Book |
|:--|:--|:--|
| backtest | none (回溯測試, 管理學名詞, SOURCES "Volume IV") | 回測 (book's form, shared decision) |
| walk-forward test | none | 滾動前進測試 (book's form; the brief keeps it, with the English in every box) |
| look-ahead bias; survivorship bias | none | 前視偏誤; 存活者偏誤 (book's forms, shared decision) |
| data snooping | 資料偵伺 (統計學名詞) | 資料偵伺 |
| overfitting | 過度配適 (統計學名詞) | 過度配適 |
| cross-validation | 交叉確認 (統計學名詞) | 交叉確認 |
| selection bias | 選擇偏誤；選擇偏差 (統計學名詞) | 選擇偏誤 |
| familywise error rate | 族系誤差率 (統計學名詞) | 族系誤差率 |
| logit | 對數勝算 (統計學名詞) | 對數勝算 |
| rank | 秩 (統計學名詞) | 秩 |
| bootstrap; stationary bootstrap | 自助重抽法 (統計學名詞); none | 自助重抽法; 平穩自助重抽法 (LM22's form) |
| transaction cost | 交易成本 (管理學名詞, 經濟學) | 交易成本 |
| commission | 佣金 (管理學名詞); 傭金，手續費 (會計學) | 手續費 (the exchange's and the statute's word) |
| securities transaction tax | 交易稅 (經濟學, "transaction tax") | 證券交易稅 (the statute's name) |
| turnover | 週轉 (管理學名詞) | 週轉率 (shared decision) |
| delisting | 刪除表列 (電子計算機名詞 only) | 下市 (the common form; 樂詞網's entry is a computing term) |
| benchmark | 基準 (統計學名詞) | 基準 |

**Open before Stage 2** (each with a recommendation and its evidence):

- **O1. Survivorship registrations (capability B4).** Recommendation: register the seven files below (the drafter
  used 38 FinMind calls in all, within the 40 allowed). Five are Free (the delisting list and the four price files,
  which A34-19 to A34-21 and the lab need); the two ETF snapshots are one-date queries without a `data_id`, outside
  FinMind's Free tier (`list_datasets`: `TaiwanStockPrice` "Free (w/ data_id)"; an inference from that label, the
  owner's Sponsor plan served them). A reader on a Free account could not rebuild the snapshots, as with Volume II's
  Backer files today; so the drafter recommends adding `"vol6/etf_snapshot"` to `fetch_finmind.py`'s `OPTIONAL` tuple
  (now `("vol4_settlement/",)`, a one-line code change for the owner to approve), after which `--verify` accepts them
  missing and the script prints A34-18's own PENDING note while A34-19 to A34-21 still compute (tested on a copy
  without the snapshots). The scratch copies at
  `…/scratchpad/s1/briefs/lm34/raw_vol6/` were rendered from FinMind answers of 2026-10-24 exactly as
  `fetch_finmind.py`'s `render()` writes, so they can be copied to `data/raw/vol6/` and registered; `--add` re-fetches
  each query and refuses a file it cannot rebuild byte for byte (it needs `FINMIND_TOKEN`). Then
  `uv run python data/check_chunk.py` on each price file, and the script's PENDING notes disappear; A34-18 to A34-20
  must then equal the values above (the scratch run used the same bytes).

  ```bash
  F=data/fetch_finmind.py
  uv run python $F --add vol6/delisting__2000-01-01__2026-10-08.csv --dataset TaiwanStockDelisting \
      --start 2000-01-01 --end 2026-10-08 --filter "stock_id=^00" --sort date --sort stock_id
  for D in 2017-01-17 2026-10-08; do
    uv run python $F --add vol6/etf_snapshot__$D.csv --dataset TaiwanStockPrice --start $D --end $D \
        --map volume=Trading_Volume --filter 'stock_id=^00\d{2,4}[A-Z]?$' --sort date --sort stock_id
  done
  for S in 00672L 00673R 00674R 00677U; do
    uv run python $F --add vol6/${S}__2016-12-01__2026-10-08.csv --dataset TaiwanStockPrice --data-id $S \
        --start 2016-12-01 --end 2026-10-08 --map volume=Trading_Volume
  done
  ```

  Columns: delisting `date, stock_id, stock_name` (63 rows); snapshots `date, stock_id, close, volume` (69 and 358
  rows; untraded funds print close 0, two on 2017-01-17); prices `date, open, max, min, close, spread, volume` (the
  E5 file layout; 967, 2,396, 2,396 and 1,078 rows). `--add` infers the kinds from the file (stock ids hold letters, so
  they stay strings). Run the `--filter` arguments from Git Bash with the single quotes shown (PowerShell would need
  other quoting). The optional cohort (A34-21: the 33 funds whose codes end in L, R or U with a row on 2017-01-17; 27
  more price files, same command) is **not recommended**: its equal-amount mean (4.127, against a median of 0.464 and
  20 of 33 below 1) is driven by a few leveraged winners, so it teaches less than the six futures funds; keep A34-21's
  ID with its PENDING note, or withdraw it.
- **O2. The futures-ETF tax source.** The shared decision rests the 0.1% for 00635U and 00642U on the Ministry of
  Finance's 統計通報 No. 21 and TWSE's ETF rules page. The drafter read the statute (Art. 2's 0.1% for "other
  securities approved by the government"; Art. 2-1 exempts only securities-investment-trust bond ETFs, and futures ETFs
  are futures-trust funds) and CNA's report of the notice, which does not mention futures ETFs. Recommendation: the
  editor re-reads the notice's futures-ETF line (or TWSE's ETF rules page) and records both URLs in SOURCES before Stage
  2; the rate itself is consistent with the statute.
- **O3. Hansen's SPA and Romano–Wolf's stepdown in the original.** A34-25 prints a consistent-SPA p-value (0.277)
  with a threshold the drafter took from memory, and the lab would code the stepdown. Recommendation: read Hansen
  (2005) §2 and Romano and Wolf (2005) §3–4 before Stage 2; until then the text states both in words, prints
  White's and the studentized p-values only, and E7 omits the SPA value. If the threshold differs, A34-25 changes.
- **O4. The spine's exhibit "gross against net Sharpe ratio by rule".** The Owners decision gives the rules' Sharpe
  ratios to LM33; LM34 owns growth, turnover and costs. Recommendation: X3 shows gross against net log growth
  (stacked bars); LM33 may show the Sharpe ratios gross and net if it wants them.
- **O5. Prerequisite tags.** The spine lists (22.2) and (26.1), (26.8), (26.9); LM34 uses (22.3) and (22.4) (the
  stationary bootstrap and its p-value) and (26.2) and (26.8); (21.8) is not used (LM34 re-teaches no FDR). It also
  adds LM20 for (20.9) (E10, problem 12), which puts 34 into lm20.md's leads at Stage 4. Recommendation: accept.
- **O6. The grid's reality-check block length.** The first drafter used the ceiling of R1's own Politis–White estimate
  (18), which is not LM22's rule. The script now takes LM22's rule over the 60 configurations (74, from R4 126
  monthly's 73.50) and prints the sensitivity at R1's own length rounded (17): p-values 0.375 and 0.421 [A34-32].
  Recommendation: keep LM22's rule as the printed result and the sensitivity in E8; both are far from rejecting.
- **O7. Lab data for the grid.** The lab cannot import `vol5_rules.py` (Labs decision), and CSCV needs the 60
  configurations' daily net returns. Recommendation: `data/make_lab_data.py` (the editor's file) writes
  `lm34_grid.csv` (1,851 rows × 60 columns, a derived series of portfolio returns, git-ignored like every lab file)
  from `vol5_rules` with the grid's windows, as it writes the through case's derived files.
- **O8. Bailey, Borwein, López de Prado and Zhu's year and pages.** Crossref holds only the DOI record (issued
  2016-09). Recommendation: the editor's verified 20(4): 39–69 stays, and the year printed is the print issue's,
  confirmed on the publisher's page with the volume when SOURCES gains the entry.
- **O9. A delisted fund's value.** The last traded close stands in for the liquidation payout, which FinMind does not
  hold (00672L's last traded close, on 2020-11-12, gives $G=0.038$ [A34-19]). Recommendation: state the convention in X5's note
  and §5; no payout figure is printed unless a dated official notice is found.
- **O10. The widget's live CSCV.** Recommendation: live CSCV in `src/lm34.js` (module-local, under 30 lines) with the
  30 precomputed means as a readout, checked in Node against Python on a fixed test matrix; the fallback is the
  precomputed means alone with one stored histogram per state (30 histograms of 18 counts).
- **O11. E5's own survivorship.** E5's 00635U and 00642U were chosen on 2026-10-24 from funds still listed; the
  leveraged oil fund of the same family (00672L) was delisted in 2020 [A34-19]. Recommendation: §5 says so once and
  the hygiene note keeps "fixed in advance" for the rules only; LM27's universe paragraph may gain a pointer to §5 at
  Stage 4 (the LM27 brief's choice).

## LM35 Stress Testing

Stage 1 brief, drafted 2026-10-24 from the editor's spine (`plans/vol-5.md`, "### LM35 Stress Testing") and the
shared decisions above it. Every number carries its anchor ID at first appearance; `data/vol6_anchors_lm35.py`
prints them all (57 rows, `## LM35` of `plans/vol-6-anchors.md`). Numbers quoted from published modules carry their
file:line instead. Rows marked *pending* (A35-24 to A35-30, the 2008 and 2015 parts of A35-41, and A35-57) read the
US proxies and 0050's 2007–2008 files, which are not registered yet ("Open before Stage 2", item 1). The script skips
them with a printed note when `data/raw/vol6/` lacks the files; the values quoted here come from the drafter's scratch
copies, fetched 2026-10-24 with `data/fetch_finmind.py`'s own `fetch()` and `render()`. They must be re-run after
registration, because a re-fetch re-rounds the adjusted closes.

**Prereq:** `[1, 2, 8, 16, 23, 26, 27, 28, 29, 30, 31, 32, 34]` (tags rechecked in `src/` on 2026-10-24; LM27–LM34 are
briefs, so their tags are the briefs' and are rechecked at Stage 3). What each supplies:

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
  (lm16.md:444), which `plans/vol-3.md:1543` routes to LM32 and LM35. LM16 already lists 35.
- LM23: (23.1) OLS (lm23.md:66), for the funds' betas on TR23; TX's settlement price $F_t=49{,}357$ on 8 October 2026
  and a contract worth $200F_t$ NT\$ (lm23.md:327).
- LM26: (26.2), the EWMA forecast (lm26.md:99), through LM31's R8.
- LM27 (brief): (27.1) the portfolio return, drift and the ruin rule $1+R_{p,t}\le0$; (27.2) the wealth recursion with
  costs; (27.8) the factor split of $\sigma_p^2$; R1 and R2. LM27's leads list 35 for (27.1), (27.2), (27.8).
- LM28 (brief): the N-asset Lagrangian with LM7's signs, used once for the reverse stress test (35.4); R3 and R4
  unconstrained.
- LM29 (brief): KKT sufficiency for convex problems, the solver-output rule and cvxpy, for the bounded reverse stress
  test; R3 and R4 in their long-only form.
- LM30 (brief): R5; (30.4), constraints as implicit shrinkage (Jagannathan and Ma 2003), for the checkpoint's "how
  constraints change the allocation".
- LM31 (brief): R6 (31.1), R7, and R8's exposure (31.7) with its cap of 1.5, cash and borrowing; LM31 hands LM35
  "what R8 lost on 7 April 2025" and "higher caps against the ruin line".
- LM32 (brief): VaR and ES as statistics of a return distribution, $\mathrm{DD}^0_t$ and $\mathrm{MDD}$, the rules'
  drawdowns; LM35 contrasts a scenario loss with them and cites the drawdowns in the four failure forms (§9).
- LM34 (brief): the rules' net log growth (the first failure form, §9) and the official cost sources.

**Leads:** `[39, 44, 45, 46, 48]`: LM39 (jump models for the gaps that LM35 replays without probabilities), LM44
(drawdown control; LM35's ruin leverage (35.2)), LM45 (Kelly sizing under gaps and fat tails; (35.2)), LM46 (margin
regimes and leverage instruments; LM35's TX margin example and (35.2)), LM48 (the capstone's own scenarios; (35.1),
(35.4)). These are the forward pointers of the text; Volume VIII and IX briefs may add citations of the tags.

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
| LM31 brief §7 ("What R8 lost on 7 April 2025 is LM35's replay"); Leaves ("higher caps against the ruin line") | R8's crash loss; caps against ruin | §3 (E3: R8's 1 April trade to 1.33 [A35-42]), §8 (X7 with the cap and R8's largest ratio) |
| LM30 brief, leads ((30.4) for the checkpoint) | how constraints change the allocation | Lab part 9 (checkpoint rubric item 7) |

The grep of `src/*.md` and `src/pages/*.md` for `[[LM35` finds no line, and `build/make_lab*.py` has no "LM35"
(2026-10-24): no published text promises anything to LM35. The rows above are the plans' and the sibling briefs'
promises; the spine missed none of the published ones (there are none) and listed the plans' three.

**Outcomes** ("After this module you should be able to:"; the level in brackets is the brief's, the page keeps
AUTHORING §3's form):

1. [C] replay a historical scenario on a portfolio: define its window, worst day and worst 5 and 20 sessions, compute
   the frozen and the named-day loss $\mathbf f^{\top}\mathbf R^{\mathrm{sc}}$ with each fund's contribution, and
   compare them with the rule's own path
2. [C] build a hypothetical scenario on proxies for funds that did not exist, convert a US fund's return into New
   Taiwan dollars by the pairing rule, and check the proxy against the fund where both exist
3. [D] derive a factor shock through betas and a partial scenario from the conditional mean (16.8), and check that a
   changed correlation matrix is still positive semidefinite
4. [D] derive the reverse stress test, the shock of least Mahalanobis distance that reaches a given loss, and solve its
   version with a price-limit bound in cvxpy, checked by KKT residuals and a closed form
5. [C] compute the loss of a levered book at a limit lock and at the next open, its ruin leverage $-1/R$, and a futures
   position's distance to its maintenance margin from a dated TAIFEX table
6. [U] explain how price limits, holidays and overnight gaps change a "one-day" loss, and which of the funds have no
   daily limit under TWSE's rules
7. [U] explain why a stress test assigns no probability, why surviving the named scenarios does not cover unseen
   losses, and how weak growth, a drawdown limit, funding and ruin differ as failures of the same rules

| Outcome | Taught | Practised | Assessed |
|:--|:--|:--|:--|
| 1 [C] | §2, §3 | E1–E3; Lab 2–3 | KC §2, §3; problems 1, 9, 10 |
| 2 [C] | §4 | E4, E5; Lab 4 | KC §4; problem 4 |
| 3 [D] | §5 | E6, E7; Lab 5 | KC §5; problems 6, 8 |
| 4 [D] | §6 | E8; Lab 6 | KC §6; problems 5, 7, 11 |
| 5 [C] | §7, §8 | E9, E10; Lab 7 | KC §7, §8; problems 2, 3, 12 |
| 6 [U] | §7 | E9, X5, X8 | KC §7 |
| 7 [U] | §6, §9 | §9's table; Lab 9 (checkpoint) | KC §9; problem 2's solution |

**Owns.** Historical replay: scenario windows on TR23 (peak, trough, the worst day, the worst 5 and 20 sessions;
the definitions below); the frozen replay (35.1) on a book's exposures at the window's first close, the named-day
replay on the previous close's exposures, and the rule's actual path, for 2020, 2024-08-05 and 2025-04-07 on the
rules' own books; 2008 and 2015 on the rules' first weights, on 0050 itself and on US proxies (capability B5),
labelled *hypothetical*; the proxy pairing rule (35.5) and its blind spot (US holidays); loss attribution
$f_iR^{\mathrm{sc}}_i$; returns that span holidays; hypothetical shocks: a factor shock through betas, the partial
scenario (35.3) with (16.8), a correlation break checked for positive semidefiniteness, the constructed "worst of
each" day; reverse stress testing (35.4) with the Mahalanobis distance as a ranking, closed form and a version
bounded by 0050's limit (cvxpy, KKT); leverage and ruin (35.2), $1+L R^{\mathrm{sc}}_p\le0$, reported, never
floored; limit locks (sales only at the limit; the next open's loss); TWSE's limit rule for domestic and
cross-border ETFs; the overnight gap from T5S per-day statistics; TX on limit days and the dated TAIFEX margin; the
four failure forms compared on the same rules (guidance g:87–90). The rules' scenario losses are LM35's numbers
(shared decision "Owners"). Values owned: every A35 anchor except the echoed inputs (A35-23, A35-38: the rules'
weights, LM27–LM31's; A35-42: R8's exposure path, LM31's; A35-33's full-sample correlation, LM27's; A35-43's
00631L figures, LM2's), which the text cites rather than prints. The lab's final part is the batch's checkpoint.

**Leaves.** Probabilities of extreme moves and jump models → LM39. Margin regimes, margin trading (融資) and leverage
instruments → LM46. Drawdown control and drawdown probabilities under a model → LM44 (LM32's drawdowns are empirical).
Kelly sizing under gaps and fat tails → LM45. Margin calls tested on intraday paths → Volume VIII (ROADMAP's VIII row:
minute bars). The capstone's own data and scenarios → LM48. VaR, ES and their backtests → LM32 (cited). Filtered
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
  sessions, $A_{\mathrm w}=243.57$ [A35-01]. The script rebuilds each rule's exposures day by day from the stored
  targets and costs with the through case's recursion and stops unless the rebuilt wealth matches `vol5_rules.parquet`
  to 1e-12 (largest difference 1.4e-14 over 92 trades, 2019-03-04 → 2026-10-01) [A35-02]; no rule is re-implemented.
- **TR23** (`vol3_taiex.parquet`): 5,849 returns 2003-01-03 → 2026-10-08 [A35-03], for the windows, the holiday spans,
  the betas' factor and the 2022 illustration.
- **0050** (pending): 0050's own 2007-07-02 → 2008-12-31 closes and distributions (two new files, Open item 1); the
  script checks every close against the spread in exact arithmetic, the two ex-dates against `before_price`, and the
  dates against TR23's. Without them TR23 stands in, and the caption says so. For 2015, LM2's sample
  (`etf_daily_returns.parquet`, all 82 TR23 dates of the window present) [A35-22].
- **US proxies** (pending, capability B5): `USStockPrice` `adj_close` and `close` of SPY, TLT, GLD, USO and DBO
  (DBO needs approval, Open item 2), 2007-07-02 → 2026-10-08, and `TaiwanExchangeRate` USD `spot_buy`, `spot_sell`
  (mid; FinMind's −1 rows filtered out): 4,849 US sessions and 4,793 FX rows [A35-24]. The pairing rule (35.5) is the
  capability check's: the New York close of session $D$ takes the first FX row dated after $D$, and a Taiwan date
  compounds the US sessions since the previous Taiwan date. Of 4,736 TR23 dates from 2007-07-03, 170 have no new US
  session, 4,421 one, 94 two and 51 three or more; one date (2012-01-02) has its FX row after it [A35-24].
- **T5S** (Volume IV): the raw files of the five named days only, through per-day statistics (log changes from the
  previous close to 09:01:00, to the day's low and to the close; the low's time; for 2025-04-07 also the stale 09:00:05
  open) [A35-45]. The script stops unless each day's 09:00:00 value equals TR23's previous price close (PITFALLS §3).
  Nothing intraday is published.
- **TX23** (`vol4_tx23.parquet`): settlement moves of 9.95% or more since 2015-06-01, TAIEX's price return those days,
  near-month volume, and $F_t$ on 2026-10-08 [A35-44].
- **The checkpoint universe** (`frames("E5+checkpoint")`): E5 plus 0056, 00662 and 00720B; base 2018-02-01 (00720B's
  listing); estimation $T=2{,}104$ (2018-02-02 → 2026-10-08), $A=242.35$; wealth frame 2,110 sessions, $A_{\mathrm w}=
  243.04$; 79 month-end signals with 504 rows, the first 2020-03-31 (trade 2020-04-01), the last 2026-09-30 (trade
  2026-10-01) [A35-47]. 00720B tracks the Bloomberg US 20+ Year BBB Corporate Bond liquid index (Yuanta's page, read
  2026-10-24); 0056 and 00720B's labels are the capability check's. The frames show no halt and no split of 00662 or
  the other two through 2026-10-08 (drafter's check of `frames`).
- **Scenario windows** (TR23; fixed here, Open item 4): the trough is TR23's lowest close of the named calendar year
  (2008, 2015, 2020) or of the 20 sessions from the named day (2024-08-05, 2025-04-07); the peak is TR23's highest
  close after the previous scenario's trough (for 2008, from TR23's first close) and before the trough; the window's
  worst day is its worst TR23 return; the worst $m$ sessions ($m=5,20$) are the worst compound TR23 returns over $m$
  consecutive sessions ending in (peak, trough], which may start before the peak.
- **Replays.** Frozen: the exposures at the window's first close held fixed, $\mathbf f^{\top}\mathbf R^{\mathrm{sc}}$
  with each fund's compound wealth-frame return over (peak, trough], interest on cash and borrowing left out (the text
  says so). Named day: the exposures at the previous close times that
  day's returns (no rule trades on a named day: none is a trade date). Actual: the rule's wealth at the trough ÷ wealth
  at the peak − 1, trades and costs included.
- **Conventions.** Simple returns in percent; T5S statistics are log changes and say so. $\hat\Sigma$ and
  $\bar{\mathbf R}$ of the full estimation frame, divisor $T$ (`cov0`, `ddof` passed). Betas: OLS slope with an
  intercept on TR23's same-day $R$. Mahalanobis $d=\sqrt{d^2}$ with that mean and $\hat\Sigma$. Ruin leverage
  $-1/R$ for a loss $R<0$. Quantiles `inverted_cdf`. Solver settings as the shared decision "Solver output"
  (CLARABEL 1e-12, OSQP 1e-10 polished), in percent units (the shared decision annualizes; for a distance
  minimization the scale only conditions the problem, and percent units gave KKT residuals of at most 1.4e-14
  [A35-40]).
- **Guard and exact checks.** Counts against a threshold use the guard 1e-12; 0050's −10% on 2025-04-07 is exactly
  $-1/10$ by `Fraction` on the two-decimal closes [A35-12]; the lock days are those with open = high = low = close
  [A35-46].
- **Rounding.** Every printed value passes through `f(x, k…)`, which flags values within a tenth of a last-digit unit
  of a rounding boundary ("NEAR"); the brief rounds them from the unrounded value. A number computed from an adjusted
  close is also flagged "CENT" when a change of one cent in each adjusted close could move its first decimal: it prints
  to 0 dp, or with "about" when 0 dp is not safe either (PITFALLS §3, "Back-adjusted prices change at every
  retrieval"). The largest such effect on a proxy return is 0.17 points in the 2020–2025 windows and 0.22 points on
  2015-08-24 [A35-26, A35-30] (pending).
- **Seeds.** None: LM35 simulates nothing, and its widget draws nothing.
- **Published files** (Stage 2). No file carries a daily series in date order: X2–X4 and X6 are per-scenario or
  per-fund bars, X7 straight lines from (35.2), X5 and X8 tables of per-day statistics. The widget embeds
  $\bar{\mathbf R}$, $\hat\Sigma^{-1}$ (5×5), the eight current books, the preset shock vectors and the 2,362
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
tests and the (16.10) check. *Hypothetical:* 2008 and 2015 on the rules' first weights with 0050 and proxies (the
one place LM35 combines data sources within one number, by construction, each source named); the factor shock; the
correlation break (a *constructed* correlation of 0.30); the worst-of-each day (*constructed*); the TX position at the
2026 margins; the widget's presets applied to the current books; every problem's inputs. No probability is attached
to any scenario. Count: the eight through-case rules ($n=8$, none selected or ranked by a scenario), five named
scenarios, one illustration, four hand-built shocks and one reverse stress test per book; the reverse stress test
searches over shocks, not over rules. Local note (about 90 words): "Stress tests here are replays and constructions,
not forecasts. The rules' books come from the through case, fixed on 24 October 2026; replaying them on past windows
estimates nothing. Betas, distances and the reverse stress test use the full sample's mean and covariance, which
include the scenario days, so they are in-sample. 2008 and 2015 are hypothetical: the foreign funds did not exist, US
proxies stand in for them, and the books are the rules' first weights. No scenario carries a probability, and no rule
is chosen by its scenario losses."

**Notation.** AUTHORING §6 with the Portfolios table. Used: $R$, $r$ (T5S log changes), $R_{i,t}$, $\mathbf R_t$, $T$,
$t$, $A$, $A_{\mathrm w}$, $N=5$, $i$, $j$ (funds), $m$ (sessions in a window, 5 or 20), $\mathbf f$, $f_i$, $L$
(total exposure $\mathbf 1^{\top}\mathbf f$; a unit book scaled by $L$ has total exposure $L$), $W$, $W_0$,
$\mathrm{DD}_t$ (LM1's), $\mathrm{DD}^0_t$ and $\mathrm{MDD}$ (LM32's, cited), $\bar{\mathbf R}$, $\hat\Sigma$,
$\hat\Sigma^{-1}$, $\Sigma$, $\boldsymbol\mu$ (in the derivations), $s_p$, $\sigma_p$, $\rho$, $\hat\rho$, $C$ (a
correlation matrix, §5), $\lambda_N$ (its smallest eigenvalue), $\beta_i$ (a fund's market beta on TR23, (23.1)),
$\beta_{i,p}$ (LM27's, in problem 7), $d^2$ (§6's) and $d=\sqrt{d^2}$, $k$ (a number of standard deviations: the bound
$d\le k$), $\mathbf R^{\mathrm{sc}}$ and $R^{\mathrm{sc}}_i$, $\E$, $\Var$, $\Cov$, $\mathcal N$, $F_t$ (TX's settlement
price), $P_t$, $r_f$, $\lambda$ and $\nu$ (the multipliers of §6's Deep Dive, LM7's signs), $K$ and $\mathbf b$ (the
two active constraints of the bounded problem, as LM28–LM29 write them). Local symbols, declared in the notation note:

| Symbol | Meaning | Check |
|:--|:--|:--|
| $R^{\mathrm{sc}}_p$ | a book's scenario return $\mathbf f^{\top}\mathbf R^{\mathrm{sc}}$ | subscript $p$ as $\sigma_p$; §6's $\mathbf R^{\mathrm{sc}}$ row |
| $\mathbf R^{\mathrm{sc}*}$, $d^*$ | the reverse stress shock and its distance | a star marks an optimum (§6) |
| $\ell$ | the loss a reverse stress test must reach (10% in the text) | §6's $B,\ell$ row scopes $\ell$ to LM22, LM23, LM32; LM35 writes no block length, lag or likelihood: a scoped row is proposed (Open item 7) |
| $L_{\mathrm{ruin}}$ | $-1/R^{\mathrm{sc}}_p$, the total exposure at which a scenario ruins a book | subscripted $L$, the same quantity as §6's $L$ |
| $\mathrm{FX}_t$ | the USD/TWD mid rate attached to a US close by (35.5) | upright, as TO, MRC; $X$ stays free (no data matrix is written), $S_t$ stays the TAIEX close |
| $P^{\mathrm{adj}}$, $P^{\mathrm{TWD}}$ | a US fund's adjusted close; its value in New Taiwan dollars | superscripted $P$ |
| $t^{\mathrm{US}}$ | the last US session before Taiwan date $t$ | $D$ stays a dividend |
| $S_t(\text{09:01:00})$ | TAIEX's value at 09:01:00 on day $t$ (per-day statistics only) | §6's $S_t$ with a time |

Not used: $\mathbf h$ (LM35 writes exposures; the shared table says so), $V$ for a value, $D$ for a date, $g$ for a gap
(it is the log growth rate), a probability for any scenario, $\Pr$ or $\chi^2$ with a distance, $\kappa$, $\alpha$.

**Motivating case: "Five days, one session"** (box, about 150 words; 11 sentences)

> The TAIEX closed on 2 April 2025 and did not trade again until 7 April. That session TR23 fell 9.70%, its worst day
> since 2003 [A35-08]. 0050 traded at one price all day, 158.40, exactly 10% below its last close: 29.6 million units
> changed hands, none lower [A35-12]. 00646 and 00642U have no daily limit, and they fell 12.59% and 14.62% [A35-11].
> The through case's eight rules lost from 5.06% (R7) to 8.33% (R4) of wealth in one session [A35-13]. R8 had raised
> its exposure to 1.33 at the trade of 1 April [A35-42], and it lost 7.94% [A35-13]. A beta model fitted on 2,362 days
> predicted a loss of 3.62% for R1, under half the actual 7.70% [A35-01, A35-32]. Three questions follow. What did
> each rule lose in the other scenarios that ROADMAP names? Which shock, not seen yet, would cost a rule a tenth of
> its wealth? And what would a book levered five times have lost at the next open?

Resolved: (a) §2–§4, X2, X3: the five windows and the rules' losses in each, with 2008 and 2015 hypothetical; (b) §6,
E8, X6: R8's current book reaches a 10% loss at $d^*=12.27$, below 2025-04-07's own distance of 12.94 [A35-39,
A35-37]; (c) §7–§8, E9: a fivefold book of 0050 loses 50.00% at the locked close and 70.45% at the next open, 151.20
[A35-52], and is ruined from $L_{\mathrm{ruin}}=7.10$ [A35-43]. The case's day is the extreme of TR23's 5,849 returns
(rank 1) and also of a multi-day measure: the worst 5 sessions of its window lost 15.96% (AUTHORING §8) [A35-08].

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | the layer added (LM32 measures losses as statistics of a distribution; LM35 asks what named and constructed shocks do to the same books, with no probability); case + X1; roadmap; notation and hygiene notes | 340 |
| 2 | Scenarios from History {1,6} | a scenario as a return vector, $W_0\mathbf f^{\top}\mathbf R^{\mathrm{sc}}$ by (8.4); the window rule (peak, trough, worst day, worst $m$ sessions); X2; E1 (2025's window against LM1's running peak); holiday spans (A35-10); pitfall: a "one-day" return can span ten calendar days; 導讀 (壓力測試, 歷史情境); KC | 500 |
| 3 | Replaying the Rules {1} | frozen replay (35.1) and attribution; named-day replay; the actual path; X3, X4; E2 (R1 on 2025-04-07); E3 (R8: frozen against actual, the 1 April trade); interest left out, said once; pitfall: a frozen book ignores the rule's own trades; 導讀; KC | 560 |
| 4 | Funds That Did Not Exist {2} | the pairing rule (35.5), the 13:30 close against New York's (shared decision "Timing of E5"); 0050 itself in 2008; E4 (2008 at the first weights); E5 (proxies checked in 2020; USO against DBO; the US-holiday blind spot); pitfall: a proxy's error is part of the scenario; 導讀 (代理資產, 匯率); KC | 520 |
| 5 | Hypothetical Shocks {3} | factor shock through betas (23.1); E6 (the beta model on 2025-04-07; the partial scenario (35.3) from (16.8)); correlation break with a PSD check; E7 (the break; 2022, when 0050 and 00679B fell together; (16.10) on 0050's 48 worst days); 導讀 (因子模型, 條件期望值); KC | 560 |
| 6 | Reverse Stress Testing {4} | the problem; derivation by LM28's Lagrangian; (35.4); the worst loss within $d\le k$; the distance as a ranking, not (16.9): the sample's distances (A35-37), the largest an oil gain; E8 (R1, R4, R8; the bounded version for R2, cvxpy and KKT); X6; Deep Dive (KKT and the closed form with both constraints active); pitfall: the closest shock may break a price limit; Python block; 導讀 (反向壓力測試, Mahalanobis距離); KC | 600 |
| 7 | Limits, Locks and Overnight Gaps {5,6} | TWSE's rule (受益憑證買賣辦法 Art. 8: which funds have a limit); X8; a lock: sales only at the limit, none below (0050's OHLC); the next open; T5S's gap, low and close (X5); the stale 09:00:05 open; E9 (0050 and 00631L; TX's volume on limit days); pitfall: the daily open is not the opening price level; 導讀 (漲跌停限制, 跳空, 隔夜); KC | 480 |
| 8 | Leverage, Ruin and Margin {5} | (35.2), ruin reported, never floored ((27.1)'s rule); X7 (R6's book scaled by $L$; R8's cap 1.5 and its largest ratio 2.135 [A35-42]); E10 (TX at TAIFEX's 2026 margins: $f=14.08$, the margin call after 1.65%, equity below zero on a limit day [A35-44]); funding as a failure distinct from ruin; 導讀 (權益歸零, 保證金追繳); KC | 440 |
| 9 | What a Stress Test Cannot Say {7} | no probability (ROADMAP's Stress row); BCBS (2018) on severe but plausible scenarios and Breuer et al. (2009) on plausibility, one sentence each; the four failure forms on the same rules (table citing LM34 and LM32); the closing pitfall: surviving the scenarios does not cover unseen losses; the lab box and the checkpoint; KC | 380 |
| — | Summary (7) / Problems (12) / Solutions | | 140 / 400 / 560 |
| | **Total** | | **5,480** |

**Elements.** 10 examples (E1 §2; E2, E3 §3; E4, E5 §4; E6, E7 §5; E8 §6; E9 §7; E10 §8). Knowledge checks:

- §2: 2020's worst day, 2020-01-30 (−5.75%, rank 8 of 5,849), came ten calendar days after the previous session
  [A35-06]: is it one day of news? Returns that span four or more calendar days are 140 of 5,849 (2.4%), and their mean
  absolute size is 1.39% against 0.83% for the rest [A35-10].
- §3: R8's 2025 window frozen at 2025-02-21 lost 10.15% [A35-19], but its own path lost 13.84% [A35-21]. Why? Its trade
  of 1 April raised its exposure from 1.005 to 1.330 [A35-42], two sessions before the drop.
- §4: on 2008-01-22 every proxy returns exactly 0 [A35-28]. Why? No US session lies between the Taiwan dates
  2008-01-21 and 2008-01-22, so both carry the same New York close and FX row. E5 has 80 such dates, on which 00646
  still moved 0.43% on average, against 0.67% on dates with one US session [A35-57] (pending).
- §5: under the correlation break R4's loss stays 6.89% [A35-33]. Why? R4's current book holds no 00679B (0.000)
  [A35-38].
- §6: R4's $d^*=9.91$ lies below 2025-04-07's 12.94 [A35-39, A35-37]. What does that say? A shock less unusual than a
  day already in the sample reaches a 10% loss; within $d\le12.94$ R4's worst loss is 13.08% [A35-39].
- §7: TX's near month traded 2,736 contracts on 2025-04-07, against 211,207 on 2024-08-05 and 152,423 on 2025-04-08
  [A35-44]. What does the volume say about selling at the limit?
- §8: R6's book survives every replay of 2020–2025 below $L=7.7$ (2020's window) [A35-41]. Does $L=5$ make it safe?
  No: the replays are a few past paths; the worst-of-each day already costs its current book 11.11% at $L=1$
  [A35-36], five times that at $L=5$, and a gap leaves no chance to cut the exposure first.
- §9: name two losses the replay set cannot show: a shock beyond the sample's largest distance (the worst-of-each day
  sits at 19.07 against 15.02 [A35-36, A35-37]); a lock that blocks the exit (§7).

中文導讀 in §2 (壓力測試 (stress testing), 情境分析 (scenario analysis), 歷史情境 (historical scenario)), §4 (代理資產
(proxy), 匯率 (exchange rate)), §5 (因子模型 (factor model), 條件期望值 (conditional expectation)), §6 (反向壓力測試
(reverse stress test), Mahalanobis距離 (Mahalanobis distance)), §7 (漲跌停限制 (price limit), 跳空 (gap), 隔夜
(overnight)), §8 (槓桿 (leverage), 權益歸零 (zero equity), 保證金追繳 (margin call)). Deep Dives: §6 "The bounded
reverse stress test": with both constraints active, $K\mathbf R=\mathbf b$ ($K$'s rows are $\mathbf f^{\top}$ and
$(1,0,0,0,0)$, written out), the minimizer is
$\bar{\mathbf R}+\hat\Sigma K^{\top}(K\hat\Sigma K^{\top})^{-1}(\mathbf b-K\bar{\mathbf R})$, and KKT sufficiency
(LM29) makes it the answer when both multipliers are non-negative (R1: 37.3 and 0.8877 in percent units [A35-40]).
§5 "Conditional means without normality": $\mu_j+(\sigma_{jk}/\sigma_{kk})(x-\mu_k)$ is the best linear predictor of
$R_j$ from $R_k$ for any law with finite variances (LM23's slope); normality makes it the conditional mean ((16.8)).

**Exhibits.**

- X1 `case` (table, §1): 2025-04-07, E5's wealth frame. Rows: the five funds. Columns: TWSE daily limit (10% / none,
  §7's rule); the day's return from the 2025-04-02 close: 0050 −10.00%, 00646 −12.59%, 00679B +1.81%, 00635U −3.10%,
  00642U −14.62% [A35-11]; beta on TR23 (estimation frame): 1.048, 0.527, −0.071, 0.161, 0.198 [A35-31]; beta × TR23's
  −9.70%: −10.17, −5.11, +0.69, −1.56, −1.92 [A35-32]. Note row: the rules' losses R1 −7.70% … R8 −7.94% (R8 at
  exposure 1.331) [A35-13]; R1's beta-model loss −3.62% [A35-32]. Note: the betas are in-sample; the day's returns span
  five calendar days. Source: FinMind `TaiwanStockPrice`, `TaiwanStockDividendResult`, `TaiwanStockSplitPrice`,
  `TaiwanStockTotalReturnIndex`, retrieval dates as registered in `data/raw_manifest.json` (`data/vol5_series.py`,
  `data/vol3_series.py`); Computations: `data/lm35_numbers.py`.
- X2 `windows` (`bar`, §2): categories the five scenarios; four series "worst day", "worst 5 sessions", "worst 20
  sessions", "peak to trough" (`fmt: "pct1"`): 2008 −6.51, −12.55, −27.69, −56.02 [A35-04]; 2015 −4.82, −9.72, −12.49,
  −23.18 [A35-05]; 2020 −5.75, −16.51, −25.99 (flagged; from −25.99467), −28.55 [A35-06]; 2024-08-05 −8.33, −10.44,
  −15.14, −18.31 [A35-07]; 2025-04-07 −9.70, −15.96, −22.38, −26.54 [A35-08]. Note: TR23, total return; each window's
  dates in the note (peak → trough: 2007-10-29 → 2008-11-20, 265 sessions; …); 2008's limit was 7% (SOURCES); the
  2024-08-05 window's worst 20 sessions start before its peak (2024-07-04).
- X3 `replay` (`bar`, §3): categories the five scenarios (2008 and 2015 marked "hypothetical"); series R1, R3, R6, R8
  (four named; the others in the note): frozen window losses. 2020: −19.84, −10.17, −13.04, −17.04 [A35-15]; 2024:
  −5.84, +0.11, −3.25, −3.61 [A35-17]; 2025: −12.97, −8.03, −10.10, −10.15 [A35-19]; 2008 (first weights, USO): −24.5,
  −9, −15, −12 [A35-27] (pending; CENT values at 0 dp); 2015: −7.2, +1.8, −2.1, −1.8 [A35-29] (pending). Note:
  2020–2025 frozen at each rule's book at the window's first close, Descriptive; 2008 and 2015 hypothetical; interest
  left out. Values cited also for the other four rules in a table under the chart.
- X4 `attrib` (`bar`, `stack: true`, approved C1, §3): categories R1, R3, R6, R8; five series: 0050, 00646, 00635U,
  00642U in colours 1–4 and 00679B in `"var(--muted)"`, named in the caption (the only fund that gained); values
  $f_iR_i$ on 2025-04-07 [A35-14]; the category total is the rule's loss [A35-13]. Note: R6's rounded parts do not add
  to its rounded total (A35-14 against A35-13), so the note gives the parts to three decimals, or the text cites only
  the total for R6 (pitfall below).
- X5 `gaps` (table, §7): the five named days. Columns: log change from the previous close to 09:01:00; to the day's
  low and its time; to the close; gap ÷ close. Values: 2008-01-22 −6.56%, −6.94% at 12:50:00, −6.74%, 0.97;
  2015-08-24 −1.66%, −7.79% at 10:25:45, −4.96%, 0.34; 2020-01-30 −3.48%, −5.95% at 13:25:00, −5.92%, 0.59; 2024-08-05
  −5.07%, −8.96% at 13:03:10, −8.72%, 0.58; 2025-04-07 −10.28%, −10.31% at 09:00:20, −10.20%, 1.01 [A35-45]. Note row:
  2025-04-07's daily open (09:00:05) gives −5.52% [A35-45] (PITFALLS §3). Note: per-day statistics of TAIEX's 5-second
  values (FinMind `TaiwanVariousIndicators5Seconds`, TWSE), log changes; no intraday path is published. Flagged values
  rounded from the unrounded ones.
- X6 `reverse` (`bar`, §6): categories the five funds; series "R1" (closed form) −10.47, −8.79, −1.21, −6.12, −23.00;
  "R8" −8.90, −7.65, −4.57, −6.75, −14.14 [A35-39]; "R2, 0050 ≥ −10%" −10.00, −10.81, −9.89, −8.67, −0.34 [A35-40];
  "each fund's worst day" −10.00, −12.59, −7.15, −11.09, −22.20 [A35-36]. Note: shocks of least Mahalanobis distance
  reaching a one-day loss of 10% for each rule's book at the 2026-10-08 close; full-sample mean and covariance
  (in-sample); distances 13.52, 12.27 and 17.01 against 19.07 for the worst-of-each day [A35-39, A35-40, A35-36].
- X7 `ruin` (`line`, §8): $x$ the total exposure $L$ from 0 to 20; $y$ wealth after the scenario, $1+LR^{\mathrm{sc}}_p$
  (`fmt: "pct0"`), four series: R6's 2020 window (−13.04% a unit), R6's 2025 window (−10.10%), R6 on 2025-04-07
  (−5.96%) [A35-41], and 0050 to the next open of 2025-04-08 (−14.09%) [A35-43]; `hline` at 0 ("ruin"); dashed
  `vline`s at R8's cap 1.5 and its largest uncapped ratio 2.135 [A35-42]. Values cited: ruin at 7.7, 9.9, 16.8 and
  7.10 [A35-41, A35-43]. Note: frozen books, no trades inside the scenario; a book rebalanced to constant leverage
  daily would differ.
- X8 `limits` (table, §7): E5's funds. Columns: TWSE limit and the clause (受益憑證買賣辦法 Art. 8); the wealth frame's
  lowest and highest return; days beyond ±10%: 0050 −10.00 / +10.00, 0; 00646 −12.59 / +10.39, 2; 00679B −7.15 /
  +8.57, 0; 00635U −11.09 / +7.74, 1; 00642U −22.20 / +33.10, 14 [A35-46]. Note row: 0050 locked (open = high = low =
  close) on 2025-04-07 and 2025-04-10 [A35-46]; the checkpoint's 0056 locked at 31.66 on 2025-04-07 [A35-48].

**Widget `scenarioBuilder` — "Build a shock, see the loss."** `Book.controls`: rule (select R1–R8); preset (select:
2025-04-07, 2020 window, 2024 window, 2025 window, factor −10%, correlation break, worst of each, the rule's reverse
stress shock, custom); five shock sliders (−25% to +25%, step 0.1%); total exposure $L$ (0 to 20, step 0.1). Bars:
each fund's $Lf_iR^{\mathrm{sc}}_i$ (stacked, approved C1) and the total. Readouts: the loss $L\,\mathbf f^{\top}
\mathbf R^{\mathrm{sc}}$, wealth after it (ruin flagged at $\le0$, never floored), $L_{\mathrm{ruin}}$, the
Mahalanobis distance $d$ of the shock and how many of the 2,362 historical days lie farther (a count, not a
probability) [A35-37]. The reverse stress preset is (35.4) in closed form for the selected book (module-local code
under 30 lines, a 5×5 product with the embedded $\hat\Sigma$, tested against Python as `data/lm15_charts.py` does).
Initial state (PDF): R1's current book under the 2025-04-07 returns at $L=1$: loss 7.78%, $L_{\mathrm{ruin}}=12.8$
(flagged; from 12.8495), $d=12.94$ [A35-49]. Data block `chart-lm35-scenarioBuilder`: the eight books at 2026-10-08
[A35-38], the presets' vectors, $\bar{\mathbf R}$, $\hat\Sigma$, $\hat\Sigma^{-1}$ and the sorted distances (about 30
KB), computed by `data/lm35_charts.py`. No optimizer and no simulation (shared decision "Widgets").

**Examples** (results recomputed from the printed inputs):

- E1 §2 `window25`, the 2025 window: peak 2025-02-21, trough 2025-04-09, 30 sessions, −26.54%; worst day 2025-04-07,
  −9.70%, rank 1, five calendar days after 2025-04-02; worst 5 sessions 2025-03-31 → 04-09, −15.96%; worst 20
  2025-03-10 → 04-09, −22.38% [A35-08]. LM1's running peak tells another story: TR23 stood 27.72% below its peak of
  2024-07-11 on 2025-04-09, 176 sessions later, and 18.31% below it on 2024-08-05 [A35-09]; the window rule keeps the
  two scenarios apart. Holiday spans: 140 of 5,849 returns cover four or more calendar days, and two of the ten worst
  days are among them, 2025-04-07 (five days) and 2020-01-30 (ten) [A35-10].
- E2 §3 `day25`, R1 on 2025-04-07: exposures at the 2025-04-02 close times the day's returns give −7.70% [A35-13], of
  which 0050 −2.00, 00646 −2.53, 00679B +0.36, 00635U −0.62 and 00642U −2.91 points [A35-14] (they add to −7.70 as
  printed); 00646 and 00642U supply the two largest parts. R3, the long-only minimum-variance book, loses 5.40%,
  4.07 points of it from 00646 [A35-13, A35-14]. Equal weights are not equal risk on a crash day.
- E3 §3 `frozen`, frozen against actual: 2020's window (2020-01-14 → 03-19) frozen at the first close costs R1 19.84%,
  R6 13.04% and R8 17.04% [A35-15]; their own paths lost 21.44%, 14.43% and 12.58% [A35-21]. R8 entered at exposure
  1.307 [A35-15] and its own trades cut the loss. In 2025 the order reverses: frozen at 2025-02-21 R8 loses 10.15% at
  exposure 1.005 [A35-19], its path 13.84% [A35-21], because the trade of 2025-04-01 raised its exposure to 1.330
  (uncapped ratio; the cap of 1.5 did not bind) [A35-42]. R8 scales by its two-year volatility over its EWMA
  forecast, and on 31 March the forecast lay below the two-year figure. The named day of 2020, 2020-01-30, cost R1
  1.60% but gave R3 +0.91%, as 00679B rose 5.26% [A35-16].
- E4 §4 `y2008`, 2008 at the rules' first weights (hypothetical, pending): over 2007-10-29 → 2008-11-20 0050 itself
  lost 55.66% (TR23 56.02%); in New Taiwan dollars SPY −44%, TLT +19%, GLD −4.1%, USO −37.3% and DBO −27% (0 dp:
  CENT); USD/TWD rose from 32.390 to 33.390 (+3.09%) [A35-27]. R1 at its first weights [A35-23] loses 24.5% with USO
  and 22% with DBO; R2 (no oil) 25.9%; R3 9% [A35-27]. The oil proxy alone moves R1 by about two points. On
  2008-01-22, TR23's worst day of the window [A35-04], 0050 fell 6.93% and every proxy returned 0, since the data
  hold no US session on 21 January [A35-28]; R2 loses 2.8% that day.
- E5 §4 `proxycheck`, the proxies where the funds exist (pending): daily correlations with their funds on the
  estimation frame 0.705 (SPY), 0.783 (TLT), 0.745 (GLD), 0.655 (USO), 0.696 (DBO), and 0.944, 0.952, 0.925, 0.845,
  0.894 over ISO weeks [A35-25]; the daily figures are lower because the funds close at 13:30 Taipei time, hours after
  the New York close they are paired with (shared decision "Timing of E5"). Over 2020's window 00642U lost 46.42%, USO
  60.7% and DBO about 46% [A35-26]; R1 on the proxies (0050 by TR23) loses 21.5% with USO against 19.84% on the funds
  [A35-26]. On the 80 E5 dates without a new US session the proxies cannot move at all [A35-57].
- E6 §5 `factor`, the beta model on 2025-04-07: betas on TR23 from 0.527 (00646) to 1.048 (0050) with R-squared 0.363
  and 0.924; 00679B −0.071 [A35-31]. Times TR23's −9.70% they predict 00646 −5.11% against −12.59% actual, 00642U
  −1.92% against −14.62%, and R1 −3.62% against −7.70% [A35-32]. A factor shock of −10% on the current books costs R1
  3.77%, R4 7.28% [A35-31]. Partial scenario (35.3): with 0050 at −10% and the other funds at their conditional means,
  00646 −4.79%, 00679B +0.71%, 00635U −1.46%, 00642U −1.69% [A35-33]. Both shocks are averages of ordinary days.
- E7 §5 `break`: setting the correlation of 0050 and 00679B from −0.105 (LM27's figure) to a *constructed* +0.30
  keeps the correlation matrix positive definite (smallest eigenvalue 0.298) and turns 00679B's conditional move from
  +0.71% to −2.04% [A35-33]. R3's loss rises from 1.41% to 2.95%, R7's from 1.40% to 3.00% [A35-33]. 2022 shows a real
  case (illustration, not a ROADMAP scenario): from 2022-01-17 to 2022-10-25 TR23 lost 28.47%, 0050 33.93% and 00679B
  22.15%; frozen at the start, R2 lost 22.37% and R4 29.86% [A35-34]. Their daily correlation inside the window was
  −0.138, and −0.008 over 40 ISO weeks [A35-34]: the bonds fell with the stocks while the correlation stayed near
  zero, because both trended down. On the 48 days when 0050 fell two standard deviations or more, its correlation with
  00646 was 0.540, against 0.669 from (16.10) and 0.599 in the full sample [A35-35]: the normal model's crash
  correlation is not the data's.
- E8 §6 `reverse`, the current books (2026-10-08) and a 10% one-day loss: R1's $s_p=0.743\%$ gives $d^*=13.52$, with
  the shock 0050 −10.47%, 00646 −8.79%, 00679B −1.21%, 00635U −6.12%, 00642U −23.00% [A35-39]. R4 needs only
  $d^*=9.91$, R5 17.54 [A35-39]. The sample's largest distance is 15.02 on 2026-03-09, when 00642U rose 33.10%; then
  12.97 (2020-03-09) and 12.94 (2025-04-07); the median is 1.60 [A35-37]. Within $d\le15.02$ R1 can lose 11.12%
  [A35-39]. R1's shock puts 0050 below its limit; with $R^{\mathrm{sc}}_{0050}\ge-10\%$ R1's distance barely moves
  (13.52) but R2's rises from 13.93 to 17.01, its shock needing 00679B at −9.89%, beyond that fund's worst day (−7.15%)
  [A35-39, A35-40, A35-36]. CLARABEL and OSQP agree within 7.6e-11, KKT residuals at most 1.4e-14 [A35-40].
- E9 §7 `lock`: 0050 on 2025-04-07 opened, peaked, bottomed and closed at 158.40, exactly −1/10 from 176.00, on
  29,578,872 units [A35-12]. A sale not filled at the lock had to wait for 2025-04-08, which opened at 151.20: 4.55%
  below the lock and 14.09% below 2 April [A35-12]. 00631L, limited at 20%, fell 19.995% and then 11.20% (lm02.md:498)
  [A35-43]. TX settled 10.00% down that day against TAIEX's −9.70% on 2,736 contracts [A35-44]: the futures locked
  too.
- E10 §8 `margin`: one TX contract at $F_t=49{,}357$ is NT\$9,871,400 of exposure; with TAIFEX's initial margin of
  NT\$701,000 as the only equity, $f=14.08$ (lm02.md:462) [A35-44]. A fall of 1.65% reaches the maintenance margin of
  NT\$538,000, and a 10% limit day loses 1.41 times the equity, leaving NT\$−286,140 [A35-44]: ruined, and the loss
  is reported, not floored. R6's unit book, by contrast, is ruined only from $L=7.7$ in 2020's window, 9.9 in
  2025's, 16.8 on 2025-04-07 [A35-41]; R8's uncapped ratio never exceeded 2.135 [A35-42].

**Problems plan** (12; MC keys B, A, C, B, C; the lab solves 9, 10, 11). Stems state the book (exposures, $L$), the
scenario (returns and their span), simple returns, that interest and costs are left out, and the rounding; an
optimization stem states the feasible set, the solver and its tolerances.

1. MC: exposures 0.6 to 0050 and 0.4 to 00679B (hypothetical), scenario −10% and +1.81%; the book's return. A −8.19%
   (the returns added). **B** −5.28%. C −6.00% (the 0050 line alone) [A35-50].
2. MC: a unit book loses 8% in a scenario; the total exposure at which the scenario ruins it. **A** 12.5. B 8.0 (the
   percent read as a multiple). C 11.5 ($(1-0.08)/0.08$) [A35-51]. The solution adds that ruin is $1+LR\le0$.
3. MC: $L=5$ on 0050, locked at 158.40 from 176.00, next open 151.20; the loss at the first possible sale. A −50.00% (at
   the locked close). B −22.73% (from the locked close only). **C** −70.45% [A35-52].
4. MC: a US fund gains 1.0% and then loses 4.0% over the two New York sessions before a Taiwan date, and USD/TWD moves
   from 32.00 to 32.48; the return in New Taiwan dollars. A −3.04% (US dollars). **B** −1.59% (flagged; from −1.5856).
   C −4.47% (the FX change subtracted) [A35-53].
5. MC: $s_p=0.8\%$ a day, mean 0, a one-day loss of 10%; $d^*$. A 156.25 ($d^{*2}$). B 3.54 (a square root).
   **C** 12.5 [A35-54].
6. A book holds 40% 0050 and 60% of a bond fund. 0050 falls 10%; the bond fund's beta on 0050 is −0.07 in normal
   times and +0.30 in a break (hypothetical). Compute the bond fund's move and the book's return in both cases: the
   bond fund +0.70% or −3.00%, the book −3.58% or −5.80%, 2.22 points apart [A35-55]. Explain why diversification
   fails exactly when it is needed.
7. Derive (35.4) by a Lagrangian: the shock of least $d^2$ with $\mathbf f^{\top}\mathbf R^{\mathrm{sc}}=-\ell$, its
   $d^*$, and the worst loss $ks_p-\mathbf f^{\top}\bar{\mathbf R}$ within $d\le k$ (Cauchy–Schwarz in the
   $\hat\Sigma^{-1}$ inner product). Then two funds with SDs 1.2% and 0.8%, correlation −0.1, $\mathbf f=(0.5,0.5)$,
   mean 0, $\ell=5\%$: $s_p=0.687\%$, $d^*=7.28$, shock −7.12% and −2.88%; show that the shock is $-\ell\beta_{i,p}$
   with LM27's $\beta_{i,p}$ = 1.424 and 0.576 [A35-56].
8. Derive the partial scenario (35.3) from (16.8) for each fund; check that changing one correlation of a $3\times3$
   correlation matrix keeps it PSD by its smallest eigenvalue; apply to E7's figures (0050 −10%: 00679B +0.71% with the
   full-sample correlation, −2.04% with 0.30) [A35-33].
9. Python: from the lab's weights file, R1's exposures at the 2025-04-02 close and the day's returns; reproduce −7.70%
   and the five contributions [A35-13, A35-14].
10. Python: 2020's window frozen against actual for R6 and R8 (−13.04% and −17.04% frozen, −14.43% and −12.58% actual)
    [A35-15, A35-21]; explain the sign of each difference from the rules' trades.
11. Python: the bounded reverse stress test for R2's current book with cvxpy (CLARABEL, `tol_gap_abs`, `tol_gap_rel`,
    `tol_feas` 1e-12; percent units; status `optimal` required): $d=17.01$, 00679B −9.89%; check the KKT residuals,
    OSQP's answer and the closed form with both constraints active [A35-40].
12. TX at $F_t=49{,}357$, NT\$200 a point, with the initial margin NT\$701,000 (TAIFEX, effective 2026-08-12) as the
    only equity: $f$, the fall that reaches the maintenance margin NT\$538,000, and the equity after a 10% limit day:
    14.08, 1.65%, NT\$−286,140 [A35-44]. Why does a margin call come long before ruin, and why can a locked market
    prevent meeting it?

**Lab parts** (`build/make_lab35.py`; reads only its `data/`: E5's estimation and wealth frames and the rules'
per-date exposures (derived files from `make_lab_data.py`), `taiex_tr.csv` (TR23), the five T5S days, the TX23
limit-day rows, LM2's 0050 and 00631L pairs, the proxies and 0050's 2007–2008 files once registered, and the
checkpoint universe's frames): 1 data, frames, windows' dates; 2 X2, E1 (the window rule and LM1's running peak),
holiday spans; 3 X3, X4, E2, E3, problems 9 and 10; 4 the pairing rule (35.5) implemented and checked against the
anchors, E4, E5, problem 4; 5 betas, E6, E7, the PSD check, (16.10) on 0050's worst days; 6 (35.4) by hand, E8,
cvxpy with both solvers and the KKT check, problem 11; 7 X5 from the five T5S days (per-day statistics only), X8,
E9, X7, E10, problem 12; 8 the widget's presets reproduced; 9 **the batch's checkpoint** (below). Labs write plain
"LM39", "LM44", "LM46", never `[[…]]`. Extension (*hypothetical*): replay 2008 with R2's fixed mix instead of the
first weights and with DBO instead of USO, and say which choice moves the loss more.

**Checkpoint (Lab part 9; guidance g:44, adjusted by the shared decisions).** Universe: E5 plus 0056 (元大高股息), 00662
(富邦NASDAQ) and 00720B (元大20年期以上BBB級美元公司債), so that E5's answers cannot be reused (A35-47). Before any result
the reader writes down, in one cell that is not edited afterwards: the rules (R1, R3, R6 and R8 with the cap 1.5;
R2's fixed mix is defined only for E5), the 504-row window, the month-end signals and next-session trades, the cost
model (commission 0.1425%, tax 0.1% on 0056 and 00662 sales, 0 on 00720B through 2026-12-31 as a bond ETF), long-only
limits and, for R3, a 30% cap per fund. Tasks: (a) allocate and run the wealth recursion (LM27's (27.1)–(27.2)) from
2020-04-01 to 2026-10-08, checking $1+R_{p,t}>0$ on every date; (b) compare out of sample: net log growth (LM34), the
Sharpe ratio with LM33's interval, maximum drawdown (LM32), turnover and costs, naming $n=4$; (c) stress: the 2024-08-05
and 2025-04-07 windows and named days on the rules' own books (frozen and actual), 2020 on the first weights
(the first trade comes after that window; the funds' 2020 returns are A35-48's), and each final book's reverse stress
test at 10% with the limit bounds of 0050 and 0056 (the two funds with a limit); (d) explain how the cap and long-only
change R3's allocation, with its multipliers (LM29) and (30.4); (e) the failure forms of R8 at caps 1.5 and 3: ruin
leverage against exposure. Rubric (each item observable in the notebook): 1 settings fixed before results; 2 every
number names its sample and label; 3 the wealth recursion matches an independent recomputation to 1e-12 and checks
$1+R_{p,t}>0$; 4 the comparison gives intervals and the count of rules; 5 frozen and actual losses for two windows,
contributions adding to the loss; 6 reverse stress shocks checked by KKT and a second solver, the distance compared
with the sample's largest, no probability attached; 7 the active constraints and their multipliers explained; 8 a
conclusion with its evidence, which may be "the data do not support more leverage" (g:116). The reference answers
(Stage 2, `data/lm35_numbers.py`) sit in a collapsed cell after the reader's own.

**Cross-module tags.**

- (35.1) Scenario P&L $\Delta W=W_0\,\mathbf f^{\top}\mathbf R^{\mathrm{sc}}$ ((8.4) with a scenario's returns); a
  frozen book over a window uses $R^{\mathrm{sc}}_i=\prod_t(1+R_{i,t})-1$ (fixed holdings, no trades, interest left
  out), and the loss splits exactly into $f_iR^{\mathrm{sc}}_i$ (LM44, LM46, LM48).
- (35.2) A unit book with $R^{\mathrm{sc}}_p<0$, scaled to total exposure $L$, is ruined when
  $1+LR^{\mathrm{sc}}_p\le0$, that is from $L_{\mathrm{ruin}}=-1/R^{\mathrm{sc}}_p$; frozen holdings within the
  scenario (LM44, LM45, LM46, LM48).
- (35.3) Partial scenario: $\E[R_j\mid R_k=x]=\mu_j+(\sigma_{jk}/\sigma_{kk})(x-\mu_k)$ for a normal vector ((16.8)
  fund by fund); for any law with finite variances, the best linear predictor (in-module; LM48).
- (35.4) Reverse stress test: for $\Sigma$ positive definite and $\mathbf f\ne\mathbf 0$, the minimizer of
  $d^2=(\mathbf x-\boldsymbol\mu)^{\top}\Sigma^{-1}(\mathbf x-\boldsymbol\mu)$ subject to $\mathbf f^{\top}\mathbf
  x=-\ell$ is $\mathbf R^{\mathrm{sc}*}=\boldsymbol\mu-(\ell+\mathbf f^{\top}\boldsymbol\mu)\Sigma\mathbf
  f/\sigma_p^2$, with $d^*=(\ell+\mathbf f^{\top}\boldsymbol\mu)/\sigma_p$; the largest loss with $d\le k$ is
  $k\sigma_p-\mathbf f^{\top} \boldsymbol\mu$; a distance, not a probability (LM44, LM46, LM48).
- (35.5) A US fund's Taiwan-date return in New Taiwan dollars: $P^{\mathrm{TWD}}=P^{\mathrm{adj}}_{t^{\mathrm{US}}}
  \mathrm{FX}$, the FX row the first dated after that New York close, and
  $R_t=P^{\mathrm{TWD}}_t/P^{\mathrm{TWD}}_{t-1}-1$ (in-module; LM48).

**Pitfalls to pre-empt.**

- A "one-day" return can span holidays: 2025-04-07 covers five calendar days, 2020-01-30 ten [A35-08, A35-06]; say the
  span with every named day (shared decision "LM35 against LM39").
- A window's peak is not LM1's running peak (E1); the worst 20 sessions of 2024's window start before its peak.
- A frozen replay ignores the rule's own trades: R8 lost more on its own path in 2025 and less in 2020 (E3). Report
  both.
- A stacked bar's parts must add to its label as printed (AUTHORING §7): R6's rounded contributions do not (X4).
- Proxies: the pairing rule gives 0 on US holidays [A35-57]; the adjusted closes re-round at every retrieval, so CENT
  values print to 0 dp and every proxy number is re-run after registration (PITFALLS §3); the oil proxy's roll rule
  matters (USO −60.7% against DBO about −46% in 2020 [A35-26]); never call a proxy the fund.
- A hypothetical book combines sources (0050, TR23, proxies, FX) in one number by design: name each in the caption,
  and never mix them in a statistic of the through case.
- Mahalanobis distance ranks how unusual a shock is, in both directions: the sample's most unusual day was an oil gain
  of 33.10% [A35-37]. It is not (16.9)'s probability: returns are not normal, and (16.9) holds for $N=2$ only.
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
  source.
- The limit rule: the current version of 受益憑證買賣辦法 Art. 8 (amended 2025-09-30) was read; earlier versions were
  not, so the text says "under TWSE's current rules" and backs the past with the data (X8).

**Curriculum guidance carried** (`plans/vol-5.md`'s table; `plans/curriculum-guidance.md`):

- Each module says which layer it adds (g:30): §1's first paragraph.
- Three outcome levels and taught/practised/assessed (g:54–58, g:124): the Outcomes table.
- Checkpoint after Volume VI (g:44, adjusted): Lab part 9 on the eight-fund universe, with the rubric above.
- Different failures in one case (g:87–90): §9's table on R1, R6 and R8: weak growth (LM34's net log growth), a
  drawdown limit (LM32's MDD and $\mathrm{DD}^0$), funding (the margin call of E10; R8's borrowing at 3.5%), ruin
  ($L_{\mathrm{ruin}}$, (35.2)); LM35 prints only the last two and cites the others by anchor once LM32's and LM34's
  exist (Open item 8).
- Wealth ≤ 0 is reported, never hidden (g:94): (35.2), E10, X7, the widget's readout.
- Surviving the scenarios does not cover unseen losses (g:95): §9's closing pitfall, KC §9.
- Decision flow (g:69–85), LM35's part: a lock removes the trade the flow assumes; a month-end rule meets a gap with
  last month's exposure (E3, E9).
- "Data too thin to support more leverage" is a valid conclusion (g:116): the checkpoint's rubric item 8.
- Not carried here: Kelly-type sizing (Volume VIII), probability bounds for drawdowns (LM44; g:93).

**Stage 4 for earlier modules.** `leads` gain 35 in lm01.md:6 (DD$_t$, (1.17)), lm02.md:6 (00631L's limit day, the TX
margins), lm23.md:6 ((23.1), TX's $F_t$) and lm26.md:6 ((26.2) through R8); all four are on the plan's Stage 4 list or
follow from this brief's prerequisites (the plan names LM1, LM23 and LM26; LM2 is added here). lm08.md:6 and
lm16.md:6 already list 35. LM27–LM34's front matter lists 35 from their own briefs (LM27, LM30, LM31 do; LM28's lists
LM32–LM35; LM29's, LM32's and LM34's briefs to confirm). No wording change in published modules: none promises LM35
anything.

**Sources** (verified 2026-10-24 unless marked; paraphrased, nothing quoted beyond a phrase):

- TWSE, 臺灣證券交易所受益憑證買賣辦法 (Rules Governing Trading of Beneficial Certificates), Art. 8, as amended
  2025-09-30, [ZH](https://twse-regulation.twse.com.tw/TW/law/DAT0201.aspx?FLCODE=FL007114) (already in SOURCES for
  ¶2): a listed beneficial certificate follows the listed-stock limit, except four kinds with no limit:
  foreign-constituent index ETFs (and their attached listings), ETFs tracking a foreign futures index, overseas ETFs and
  foreign-constituent active ETFs; a leveraged or inverse ETF on domestic constituents has 10% times its multiple,
  one with any foreign constituent none. Read through a page fetcher on 2026-10-24; the editor re-reads the article's
  text before Stage 3. Applied: 0050 and 0056 10% (domestic constituents); 00646, 00679B, 00662 and 00720B none
  (foreign-constituent index ETFs: US stocks, US Treasuries, US stocks, US corporate bonds); 00635U and 00642U none
  (futures ETFs on S&P GSCI gold and crude-oil indices, LM27's issuer check); 00631L 20%. Consistent with every fund's
  extreme days (X8) and with FinMind printing no limits for the bond ETFs (shared decision "Limits and locks").
- TWSE's limit history (7% to 10% on 2015-06-01) and TAIFEX's TX specification (±10%), TAIFEX's margins effective
  2026-08-12: SOURCES rows "TWSE company history", "TAIFEX TX", "TAIFEX index margins" (via lm02.md:462).
- TWSE Holiday Schedule 2025 (SOURCES): 3 April 2025 adjusted holiday, 4 April Children's Day and Tomb-sweeping Day,
  for "four non-trading days" before 7 April.
- Basel Committee on Banking Supervision (2018), *Stress testing principles*, BCBS d450, 17 October 2018,
  [BIS](https://www.bis.org/bcbs/publ/d450.htm): the BIS page confirms the title, the date and that it replaces the
  2009 principles (read 2026-10-24); its "severe but plausible" wording and its description of reverse stress tests are
  the survey's reading of the PDF (Volume VI survey, §3), to re-read before §9 prints them.
- Breuer, T., M. Jandačka, K. Rheinberger and M. Summer (2009), "How to Find Plausible, Severe, and Useful Stress
  Scenarios", *International Journal of Central Banking* 5(3), September 2009,
  [IJCB](https://www.ijcb.org/journal/ijcb09q3a7.htm): title, authors, volume, issue and date verified on the journal's
  page (2026-10-24); pages 205–224 from the survey's reading of the PDF headers; no DOI on Crossref (survey). The
  journal's summary: they define a plausible region from the risk factors' distribution and search it for the
  scenario with the largest loss. §6's "worst loss within $d\le k$" is that idea for an ellipsoid; that the paper
  measures plausibility by a Mahalanobis distance is the survey's reading, to confirm before §9 credits it.
- Boyer, Gibson and Loretan (1999), Theorem 1, for (16.10), and Wasserman (2004) for $d^2$: via LM16 (SOURCES).
- Jagannathan and Ma (2003), Proposition 1, via LM30's (30.4) (shared decision "References").
- Kupiec, P. H. (1998), "Stress Testing in a Value at Risk Framework", *The Journal of Derivatives* 6(1): 7–24, DOI
  10.3905/jod.1998.408008 (Crossref, 2026-10-24). Bibliographic only: the paper's treatment of shocks to some factors
  with the others at conditional values was not read (the publisher's page needs a login), so it is UNVERIFIED and not
  cited; (35.3) is derived from (16.8) without it.
- Fund pages: Yuanta's 00720B page (read 2026-10-24: 元大20年期以上BBB級美元公司債券ETF, Bloomberg US 20+ Year BBB
  Corporate Bond liquid index, listed 2018-02-01); the E5 funds' indices from LM27's brief (Yuanta pages read
  2026-10-24). USO, issuer page ([USCF](https://www.uscfinvestments.com/uso), read 2026-10-24): the benchmark is the
  near-month NYMEX light sweet crude contract, rolled over five days each month; operations began 2006-04-10; a
  1-for-8 reverse split on 2020-04-28. UNVERIFIED and not relied on: DBO's index and roll rule (Invesco's page did not
  load), 00662's index (Fubon's page was under maintenance; a press summary gives the Nasdaq-100).
- News already in SOURCES: White House fact sheet of 2 April 2025 (the April tariffs); Atkinson (7 April 2025),
  TechNews: 936 listed stocks closed limit-down; TechNews and FTV, 5 May 2025: USD/TWD 31.064 on 2 May and 30.145 on 5
  May (project/SOURCES.md:205), the day of 00679B's worst return [A35-36].
- FinMind datasets `USStockPrice`, `TaiwanExchangeRate`, `TaiwanStockPrice`, `TaiwanStockDividendResult`: SOURCES'
  FinMind rows (licence, attribution); retrieval dates in every `Source:` line.

**Chinese terms** (AUTHORING §1; English in parentheses at first use in each box). On the plan's list
(`plans/vol-5.md`, "Chinese terms"): 壓力測試, 情境分析, 敏感度分析, 歷史模擬法, 保證金追繳, 槓桿, 共變異數矩陣, 尾部風險, 回撤,
最大回撤. Looked up on 樂詞網 by the drafter (2026-10-24, saved result pages): Mahalanobis distance → Mahalanobis距離
(數學名詞, 統計學名詞); conditional expectation → 條件期望值 (數學, 統計學); factor model → 因子模型 (統計學名詞); price
limit → 漲跌停限制 (管理學名詞); worst-case scenario → 最糟情境 (新聞傳播學名詞, another field's entry); overnight → 隔夜
(統計學名詞's 隔夜拆款利率). No 樂詞網 entry (0 results for "reverse stress test", "reverse stress testing", "stress
scenario", "historical scenario", "hypothetical scenario", "gap risk", "proxy variable"): the common forms 反向壓力測試,
壓力情境, 歷史情境, 假設情境 (土木工程名詞 gives 假設情境 for "what-if scenario"), 跳空 (gap), 代理資產 (proxy; 樂詞網's
"proxy" entries are computing and accounting terms) and 鎖跌停 (limit-down lock), each with its English in every box.
AUTHORING's own: 權益歸零 (zero equity), never 斷頭.

**Open before Stage 2** (each with the drafter's recommendation and evidence):

1. **Registrations (capability B5 and 0050 in 2008).** Write the files under `data/raw/vol6/` with
   `fetch_finmind.py`'s own `fetch()` and `render()` (the drafter's scratch scripts
   `…/briefs/lm35/code/fetch_proxies.py`, with `OUT` set to `data/raw/vol6` and DBO added to its symbols if approved,
   and `…/code/fetch_0050_2008.py`; 8 Free calls), check the Taiwan files with `data/check_chunk.py` (0050: two
   mismatches, both ex-dates, 2007-10-24 and 2008-10-24, with spread 0.0 and the previous close equal to
   `before_price`; drafter's check), then register:

   ```text
   uv run python data/fetch_finmind.py --add vol6/SPY__us_2007-07-02__2026-10-08.csv --dataset USStockPrice \
       --data-id SPY --start 2007-07-02 --end 2026-10-08 --map adj_close=Adj_Close --map close=Close \
       --adjusted adj_close
   (the same for TLT, GLD, USO and, if approved, DBO)
   uv run python data/fetch_finmind.py --add vol6/USD_TWD__2007-07-02__2026-10-08.csv --dataset TaiwanExchangeRate \
       --data-id USD --start 2007-07-02 --end 2026-10-08 --filter 'spot_buy=^[1-9]'
   uv run python data/fetch_finmind.py --add vol6/0050__2007-07-02__2008-12-31.csv --dataset TaiwanStockPrice \
       --data-id 0050 --start 2007-07-02 --end 2008-12-31
   uv run python data/fetch_finmind.py --add vol6/0050_dividends__2007-07-02__2008-12-31.csv \
       --dataset TaiwanStockDividendResult --data-id 0050 --start 2007-07-02 --end 2008-12-31 \
       --map cash_dividend=stock_and_cache_dividend --filter 'stock_or_cache_dividend=^息$'
   ```

   (the dividend entry mirrors the registered `0050_dividends.csv`; the FX filter drops FinMind's −1 rows; the
   files' columns are `date,adj_close,close`, `date,spot_buy,spot_sell`, `date,close,spread` and
   `date,before_price,after_price,cash_dividend`). USO's reverse split of 2020-04-28 will show as an "ex-date" in its
   `--adjusted` summary, and that entry's stored "distributions" sum then includes the split; the check still works
   (a re-fetch has the same day), but `data/README.md` should say so. SPY's file also serves LM27's open item 5
   (00646 against SPY's previous session). Then re-run the script: A35-24–A35-30, A35-41's 2008 and 2015 parts and
   A35-57 replace the scratch values, and their CENT flags decide 1 dp or 0 dp. Recommendation: register all of them
   now; the brief's pending numbers change by at most their CENT bounds.
2. **DBO, beyond the approved proxies.** The owner approved SPY, TLT, GLD and USO (ROADMAP, "Batch 4 capabilities").
   DBO is the drafter's addition (one more Free call) and needs the owner's yes (memory: ask before widening an owner
   rule). Evidence: 00642U tracks an "enhanced" crude-oil index (LM27's issuer check), while USO holds the near month
   (USCF's page); over 2020's window 00642U lost 46.42%, USO 60.7%, DBO about 46% [A35-26]; daily correlations 0.655
   and 0.696; but over the whole frame USO's log growth is closer (gap +0.02 against −6.63 points a year) [A35-25]; the
   choice moves R1's 2008 loss by about two points [A35-27]. Recommendation: approve DBO and show both, which teaches
   that a proxy's error is part of a hypothetical scenario; if declined, print USO only and state its 2020 gap.
3. **0050 itself in 2008, a new Taiwan registration.** The spine says "on the funds that existed"; 0050 listed in
   2003, but the registered 0050 files start on 2014-10-31, so TR23 would stand in. Evidence that the stand-in errs:
   TR23 against 0050 over the windows −23.18 / −20.96 (2015), −18.31 / −21.30 (2024) [A35-22]; in 2008 −56.02 /
   −55.66, and on 2008-01-22 −6.51 / −6.93 [A35-04, A35-27, A35-28] (pending). Two Free calls. Recommendation:
   register (item 1); it is within the data rule (FinMind, `--add`), but it is not in the approved capability list, so
   the editor confirms it with the owner together with item 2.
4. **The scenario windows and the replayed weights.** The spine leaves both to the brief. Windows: the rule under
   "Data role" (trough of the named year or of the 20 sessions from the named day; peak after the previous trough). It
   keeps 2024 and 2025 apart (by LM1's running peak they merge: 27.72% from 2024-07-11 [A35-09]) and puts 2008's worst
   day in January (2008-01-22, −6.51%, rank 4), not in October [A35-04]. Weights for 2008 and 2015: the rules' first
   target exposures of 2019-03-04 [A35-23], all eight rules, R2's fixed mix among them; R8's first exposure is 0.849,
   the rest in cash [A35-23]. Recommendation: adopt both; the alternative windows (running peak; calendar month of the
   named day) go to the lab's extension, not the text.
5. **The checkpoint's universe and rubric.** Recommendation: the eight funds of `frames("E5+checkpoint")` [A35-47] and
   the four rules R1, R3, R6, R8 (R2 is E5's fixed mix), with the rubric above. Evidence: three new funds alone (0056,
   00662, 00720B) give $N=3$, too few for minimum variance and ERC to differ much; the eight-fund universe changes every
   answer, adds a second domestic fund with a limit (0056 locked at 31.66 on 2025-04-07 [A35-48]) and a bond fund
   without tax, and its first trade (2020-04-01) comes after 2020's window, so the reader must replay that window
   hypothetically. The reference answers are computed in Stage 2 (not anchors now). The editor confirms that
   `vol5_rules`' functions run R1, R3, R6 and R8 on the eight-fund frames unchanged (A35-47 shows `schedule()` does).
6. **The limit rule (settled; re-read).** TWSE's 受益憑證買賣辦法 Art. 8 (current version) gives 0050 and 0056 a 10% limit
   and none to 00646, 00679B, 00635U, 00642U, 00662 and 00720B (Sources). The shared decision "Limits and locks" wrote
   "an ETF holding overseas stocks has none"; the rule is wider (overseas bonds and foreign futures indices too), and
   the data agree (X8). Recommendation: the text states the rule as above, "under TWSE's current rules", after the
   editor re-reads the article's original text (the drafter read it through a page fetcher) and adds ¶1 to SOURCES'
   row.
7. **The loss level's symbol.** $\ell$ in (35.4) needs a scoped entry in §6's $B,\ell$ row ("LM35's loss level"), since
   the row lists LM22's block length, LM23's lag and LM32's block length. LM35 writes none of these. Alternatives:
   write the constraint with the number ($-10\%$) and the general case in words, losing (35.4)'s general form.
   Recommendation: the scoped row.
8. **The four failure forms (§9) depend on LM32 and LM34.** LM35 prints ruin and funding; growth and drawdowns are
   LM34's and LM32's numbers, which do not exist yet. Recommendation: §9's table cites their anchors by ID when their
   briefs are done, for R1, R6 and R8; until then the table has those two columns empty in the draft.
9. **R8 "at higher caps".** The cap did not bind at any window start (R8's exposures 1.307, 1.111, 1.005; the uncapped
   ratios at the preceding trades 1.308, 1.114, 1.005) [A35-42], so a higher cap changes none of the frozen replays.
   Recommendation: X7 shows the ruin line against $L$ with the cap and R8's largest uncapped ratio (2.135) marked,
   instead of replays at higher caps; the checkpoint's task (e) asks for caps 1.5 and 3 on the new universe.
10. **Smaller checks.** (a) 2020-01-30 follows ten calendar days without a session; name Taiwan's Lunar New Year
    closure only after checking TWSE's 2020 schedule (its JSON endpoint returned no 2020 rows on 2026-10-24). (b)
    BCBS (2018)'s wording on reverse stress tests is to be read in the PDF before §9 prints it. (c) 00662's issuer page
    before the lab names its index. (d) The spine's "27 sector closes from 2007-07-02 for 2008" are not needed: E5 has
    one Taiwan equity fund, and 0050 itself covers 2008 (item 3).
