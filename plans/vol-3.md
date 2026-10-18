# Volume III — Probability: module briefs

Volume III turns the sample facts of Volumes I and II into probability models. A day's return becomes a random
variable, a frequency becomes a probability, a sample mean an expectation and a sample covariance matrix the estimate
of a population one. The volume teaches the language and the tools; estimation and testing wait for Volume IV and
stochastic processes for Volume VII (ROADMAP, "Module boundaries").

The reader reads English as a second language and wants the tools learned systematically, not a lot of material
(SPEC §2). So worked examples, diagrams and formulas carry each module, and the prose connects them. Each brief lists
what its module owns and what it leaves to others. Volumes I and II are published: link to their results with
[[LMn]] instead of repeating them, and honour every forward link they make to LM13–LM18 (listed per module).

Each brief was drafted from the editor's spine by one agent, checked across the volume by a fresh agent (32 findings,
10 major, all decided below) and revised. Every number a brief quotes is an anchor in `plans/vol-3-anchors.md`,
printed by `data/vol3_anchors_lmNN.py`. Until Stage 3 this brief and the anchors are the plan. From Stage 3 the module
sources and their numbers scripts are authoritative: review corrections to statements of fact are applied here, but
values and wording that a revision changes in a module are not copied back (`reviews/lm13.md` … `lm18.md` record
them).

## Shared decisions

- **Length and voice.** AUTHORING §1: at most 6,000 words of prose and 36 pages; first drafts under 5,500 words;
  sentences average under 16 words and never exceed 30; paragraphs at most 80 words; connectors kept.
  `uv run python build/qa/style.py src/lmNN.md` shows no FAIL before a draft is handed back.
- **Section pattern.** A small numeric case or a picture first, then the definition or theorem with all its
  conditions, a short derivation, a worked example, at most one pitfall, the 中文導讀 and the knowledge check.
  Probability is learned on small sample spaces first (a coin, a die, two days), then on the data.
- **Rigor.** Every theorem states its conditions: finite mean or variance, independence, identical distribution,
  integrability, differentiability. A result is derived in the text or in a Deep Dive, or labelled *stated without
  proof* with a reference. Measure theory is out of scope: LM13 says what countable additivity and an event of
  probability zero mean; LM17 says what "with probability one" means for a path. No more.
- **Population and sample.** Volume I called the divisor-$T$ statistics "population" variance and standard deviation
  (LM3, LM4, LM5); Volume II called them sample statistics with divisor $T$ (LM10). From Volume III, **population**
  means a property of a random variable or a model ($\mu$, $\sigma$, $\Sigma$, $\rho$), and **sample** means a
  statistic of data ($\bar R$, $s$, $\hat\Sigma$, $\hat\rho$), with its divisor stated. The empirical distribution of
  a sample (mass $1/T$ on each observation) is a probability model whose population moments are the divisor-$T$
  sample moments. LM13 states this bridge without the word "population"; LM14 introduces the vocabulary once, with a
  pointer back to LM3's wording.
- **Notation.** AUTHORING §6 plus the table below, which the editor copies into §6 before any writer starts (with
  the amendments it names). Every local symbol is in the module's notation note.

  | Symbol | Meaning (from Volume III) | Against §6 |
  |:--|:--|:--|
  | $\Omega$, $\omega$ | sample space; an outcome; outcomes of trades or days written as $+$/$-$ strings ($\{++,+-,-+,--\}$) | new; $W$, $L$, $H$, $T$ are taken |
  | $A$, $B$; $A^c$ | events, in LM13 only (LM13 does not annualize); the complement. Other modules write events as sets, $\{R\le-3\%\}$, or name them in the note | $A$ annualizes elsewhere |
  | $\Pr(\cdot)$, $\Pr(B\mid A)$ | probability (LM5's symbol); conditional probability, `\mid` | never $P$, the price |
  | $\mathcal A$, $\mathcal B$ | an event in a general statement, in a module that annualizes (LM14–LM18) | new; added to AUTHORING §6 |
  | $\mathbf 1_{\mathcal A}$, $\mathbf 1\{\cdot\}$ | indicator of an event, always with a subscript or braces; $\E[\mathbf 1_{\mathcal A}]=\Pr(\mathcal A)$ is LM14's (14.1) | bold $\mathbf 1$ alone stays the vector of ones; KaTeX has no blackboard 1 |
  | $X$, $Y$, $Z$; $x$, $y$, $z$ | random variables, capitals; their values, lower case; $Z$ standard normal (LM5); $R$ and $r$ keep their meaning as random returns. In a purely mathematical passage of a module without yields, $y$ may be a generic coordinate or an integration variable, declared (LM15's gamma function) | Volume III does not use the data matrix $X$ (cite (10.2) by its tag) |
  | $\mathbf X$, $\mathbf Z$ | random vectors, bold capitals; $\mathbf Z$ a standard normal vector | $\mathbf z_t$ stays LM12's whitened data vector |
  | $p_X$, $f_X$, $F_X$, $F_X^{-1}$ | pmf, density, distribution function and quantile function $F_X^{-1}(u):=\min\{x:F_X(x)\ge u\}$ of $X$, always with the subscript; $F_R$ is a model's law of $R$ | $f$ is an exposure and $p$ a win probability |
  | $\hat F$, $\hat F^{-1}$ | empirical distribution function of a sample (mass $1/T$ on each return) and its quantile function, whose values are order statistics | new |
  | $u$; $U$ | a probability level in $F^{-1}(u)$, or a value of a uniform random variable $U\sim\operatorname{Unif}(0,1)$ | amend §6's "$h$, $u$" row |
  | $\E$, $\Var$, $\Cov$, $\operatorname{Corr}$, $\E_{\hat F}$ | expectation, variance, covariance, correlation (macros `\E`, `\Var`, `\Cov`); expectation under the empirical law | LM5's `\mathrm{Var}` is the same symbol |
  | $\operatorname{Skew}(X)$, $\operatorname{Kurt}(X)$ | standardized third and fourth moments; excess kurtosis is $\operatorname{Kurt}(X)-3$ (LM5's term) | $\gamma$ and $\kappa$ are taken |
  | $\mu_X$, $\sigma_X$, $\sigma_{XY}$, $\rho_{XY}$ | mean, standard deviation, covariance, correlation of random variables; unsubscripted $\mu$, $\sigma$, $\rho$ keep the return's | $\rho$ is a population correlation; a sample one is $\hat\rho$ in a module that has both |
  | $\bar R$, $s$; $\bar r$, $s_r$; $g$, $\sigma_r$ | sample mean and standard deviation of $R$, and of $r=\ln(1+R)$, divisor $T$; in a model $\mu$, $\sigma$ for $R$, and $g=\E[\ln(1+R)]$ (per day) and $\sigma_r$ for $r$. $\bar g(f)$ only as LM4's (4.4), with $\bar g(1)=\bar r$ said once; $R_G$ the compound rate (LM3) | AUTHORING allows $\hat\mu$; Volume III writes $\bar R$ |
  | $\boldsymbol\mu$, $\Sigma$ | mean vector and covariance matrix of a random vector; $\hat\Sigma$ the sample one (10.2) | as §6 |
  | $\mathcal N(\mu,\sigma^2)$, $\mathcal N_N(\boldsymbol\mu,\Sigma)$, $t_\nu$, $\chi^2_N$, $\operatorname{Bin}(n,p)$, $\operatorname{Poisson}(\lambda)$, $\operatorname{Exp}(\lambda)$, $\operatorname{Unif}(0,1)$ | distributions; $\sim$ "is distributed as"; "iid" independent and identically distributed | $\lambda$: a Poisson mean or an exponential rate (amend §6); $\nu$ already allowed |
  | $n$, $\bar X_n$, $S_n$ | number of independent draws or trials; their mean and sum | $T$ stays the number of returns in a data sample |
  | $m$ | number of days summed or compounded in a model or in an $m$-day sum, whole sessions; a horizon of $\tau$ years is $m=\operatorname{round}(A\tau)$ ($m=1{,}231$ for five years) | new |
  | $j$; $R_{(j)}$ | the value of a count in a pmf ($\Pr(X=j)$); the $j$th smallest return | index, declared |
  | $k$ | a number of standard deviations, $k\ge0$ (not an integer) | not a required return in Volume III |
  | $d^2$ | squared Mahalanobis distance $(\mathbf x-\boldsymbol\mu)^{\top}\Sigma^{-1}(\mathbf x-\boldsymbol\mu)$ | LM12's $\lVert\mathbf z_t\rVert^2$ is its sample version |
  | $L$ | Cholesky factor of $\Sigma$, in LM16 and LM18, declared | neither module has leverage |
  | $B$ | number of bootstrap resamples, in LM18 (no Brownian motion), declared | amend §6's $B$ row |
  | $\eta$, $\zeta$ | constants in $\Var(\eta X+\zeta)$ (LM5's letters) | $a$, $b$ are the bet's |

  Not used in Volume III: $P$ for probability, $E$ without blackboard bold, $\hat\mu$ for TR23's mean, $\kappa$ for a
  threshold (it is a condition number; cite LM5's (5.11) by its tag), $\theta$ for a parameter (an angle), $q$ for a
  quantile, a star for anything but an optimum.
- **Data.** One main sample, **TR23**: the TAIEX total-return index (`TaiwanStockTotalReturnIndex`, data_id TAIEX,
  retrieved 2026-10-18), closes 2003-01-02 → 2026-10-08, $T=5{,}849$ simple daily returns from 2003-01-03, 8,680
  calendar days $=23.7645$ years, $A=246.12$. It is the investor's TAIEX: cash dividends reinvested, no costs. Its
  base date is 31 December 2002 and it starts at the TAIEX price level (Taiwan Index Plus; SOURCES). `data/vol3_series.py`
  builds it (`processed/vol3_taiex.parquet`) and checks it against the TAIEX price index on every date. Calendar years
  are **2003–2025, 2003 from its first close** (2 January 2003, so 2003 misses the year's first session, on which the
  price index rose 1.63%); every exhibit with years says so. Facts every module keeps: the daily price limit was 7%
  until 29 May 2015 and 10% from 1 June 2015 (PITFALLS §7); 7 April 2025 (−9.6997%) is TR23's worst day and was capped
  by the limit for many stocks. LM16 uses Volume II's **U28** sample (sector price indices and the TAIEX price index,
  2008-12-02 → 2026-10-08, $T=4{,}382$, $A=245.4794$), because its subject is several assets; every LM16 caption says
  "TAIEX price index (no dividends), U28 dates", and elsewhere in Volume III "TAIEX" is TR23. Never mix samples
  within a module. Recorded exceptions: LM18 uses LM12's *printed* S5 Cholesky factor as model parameters (it
  loads no U28 data); Volume I's 0050 samples are cited, never recomputed under another name; LM16 quotes figures that
  LM7 and LM11 printed on other samples (LM7's 2022 joint loss of 0050 and 00679B, LM11's ellipse on LM7's sample) as
  printed, with their module, never recomputed.
- **Return type.** Statistics of one day use simple returns $R$ (as LM5); sums over days use log returns $r$, labelled
  "log returns" in every caption. One owner per statistic, cited elsewhere by module: LM14 owns TR23's full-sample
  moments of $\hat F$ (Skew −0.34, Kurt 8.27, excess kurtosis 5.27) and the bound tables; LM15 owns the tail measures
  that need fewer moments (quantiles, exceedance counts, tail-index chords) and the fragility of the kurtosis (the
  7 April 2025 jump, the removals, the top-ten shares, the two limit regimes), the lm05.md:369 promise; LM17 owns the
  running sample kurtosis as a law of large numbers that does not settle (the lm05.md:366–368 promise, drawn in its
  X9 and citing LM15's jump), the kurtosis of $m$-day log-return sums and the lag correlations of $\lvert r\rvert$;
  LM13 owns the threshold counts it states first (108 days at or below −3%, 15 at or below −5%).
- **Counting.** Every count against a threshold uses one guard (`<= -x + 1e-12`, `>= x - 1e-12`) or exact arithmetic
  (PITFALLS §5): two-decimal index levels make round returns exact ties.
- **Simulation.** Each simulated experiment (an example, a problem, an exhibit, a lab part) creates its generator once,
  at its start: `rng = np.random.default_rng([e, 20261011])`, with `e` the experiment's stated number first (NumPy's
  recommended order: varying IDs before the root seed), and never
  reseeds inside it. Different `e` give streams that are independent with very high probability (NumPy's
  `SeedSequence`), and each experiment draws only from its own stream, so resizing one leaves the others unchanged. The stem or note prints the seed. LM18's reproduction of LM12's lab keeps that lab's
  `default_rng(20261011)`. Every printed Monte Carlo or bootstrap result states the number of draws, the seed and its
  standard error, and keeps only the digits its standard error supports. NumPy promises identical streams only for
  the same version and build, so printed simulation numbers rest on `uv.lock`'s pinned NumPy (SOURCES). A widget that
  simulates uses `Book.rng(seed)` with a fixed initial state (the PDF shows it); the text quotes only numbers that a
  script in `data/` reproduces. At Stage 4 Getting Started's seed sentence says the same.
- **Python.** NumPy's `Generator` (`default_rng`, `standard_normal`, `integers`, `choice`), SciPy's `stats`
  distributions (`norm`, `lognorm`, `t`, `poisson`, `binom`, `chi2`, `multivariate_normal`), Polars for data. Facts
  checked 2026-10-18 on the NumPy 2.x and SciPy 1.18 references (SOURCES): `lognorm(s, scale)` with `s`$=\sigma_X$ and
  `scale`$=e^{\mu_X}$; `t(df, loc, scale)` has variance `scale²·df/(df−2)` for `df > 2` (computed, not stated on the
  page); `fit` is maximum likelihood unless `method="MM"`; `stats.kurtosis` returns excess kurtosis with divisor-$T$
  moments by default (`fisher=True`, `bias=True`) and `stats.skew` uses `bias=True`; `default_rng` wraps PCG64 and
  accepts a sequence of integers as its seed; `choice` samples with replacement by default; `integers` excludes its
  upper end by default; `Generator.multivariate_normal` factorizes by SVD by default.
- **References.** Cite only entries in `project/SOURCES.md` ("Papers and books", Volume III), with the corrections
  found in Stage 1: Gigerenzer and Hoffrage (1995) say "frequency formats" and "natural sampling", not "natural
  frequencies" (Study 1: Bayesian answers rose from 16% to 46% with the standard menu and from 28% to 50% with the
  short menu, probability formats against frequency formats); Blitzstein and Hwang's
  section numbers were inferred from a contents list and are checked in the book before printing; Efron and
  Tibshirani's section number for the bootstrap standard error (§6.2, Algorithm 6.1, (6.6) with divisor $B-1$) was confirmed from
  Google Books snippets; the general strong law (iid, $\E\lvert X\rvert<\infty$) is cited to Durrett (2019),
  Theorem 2.4.1, or Wasserman (2004), Theorem 5.18 (Blitzstein and Hwang's Theorem 10.2.1 assumes a finite variance);
  Grinstead and Snell
  have no Jensen inequality and no multivariate normal. Section and theorem numbers not in SOURCES are checked before
  they are printed.
- **Chinese terms.** AUTHORING §1 (樂詞網, statistics or mathematics listing; English in parentheses at first use in
  each box). Looked up on 樂詞網 on 2026-10-18 (245 English forms; SOURCES): **分布** for "distribution" from Volume III
  (the statistics listing writes 分布 in every compound; 條件分布, 分布函數 and 依分布收斂 have no 分配 form in either
  listing), and at Stage 4 LM5's three nouns become 累積分布函數, 常態分布函數 and 常態分布, so the book has one form.
  Terms: 樣本空間, 事件, 機率公設, 條件機率, 獨立, 成對獨立, 互相獨立, 互斥, 餘事件, 全機率法則, 貝氏定理, 基本率 (心理學),
  事前機率, 事後機率, 隨機變數, 期望值, 機率質量函數, 分位數, 分位數函數, 分位數-分位數點圖 (QQ plot), 中位數, 動差,
  偏態, 峰態, 超額峰態 (printed), 指示函數,
  馬可夫不等式, 謝比雪夫不等式, Cantelli 不等式, Jensen 不等式, 算幾不等式, 柏努利分布, 二項分布, 卜瓦松分布, t 分布,
  卡方分布, 常態分布, 對數常態分布, 均勻分布, 指數分布, 經驗分布, 伽瑪函數, 自由度, 過度離散, 聯合分布, 邊際分布,
  條件分布, 聯合機率密度函數, 條件期望值, 雙重期望值定理, 多變量常態分布, Mahalanobis 距離, 大數法則, 弱大數法則,
  強大數法則, 賭者謬誤 (gambler's fallacy), 中央極限定理, 依機率收斂, 幾乎必然收斂, 依分布收斂, 常態逼近, 獨立同分布
  (數學名詞; the statistics listing has only the noun phrase 獨立且相同分布隨機變數), 蒙地卡羅法, 隨機數, 擬隨機數,
  隨機數產生器, 隨機種子, 逆變換法, 標準誤, 變異數縮減, 對偶變數, 控制變量, 重要抽樣, 自助重抽法, 重抽樣, 放回抽樣, 母體,
  樣本平均數. The book's own forms, with no 樂詞網 entry, printed with their English in every box that uses them:
  檢察官謬誤 (prosecutor's fallacy), 標準化動差 (standardized moment), 全變異數法則 (law of total variance),
  條件相關係數 (conditional correlation), 超越相關係數 (exceedance correlation), 放回重抽樣 (resampling with
  replacement). LOTUS keeps its English name only. Statistical 獨立 is never LM9's 線性獨立: one sentence in LM13 says
  so. 尾部指數 and 厚尾 stay as printed in LM5; 隨機數 replaces LM12's second form 亂數 from now on.
- **Research hygiene.** The site's Research hygiene page and each module's declaration. A frequency in TR23 is
  *Descriptive*; a fitted distribution is *In-sample*; comparing 2003-01-03 → 2015-05-29 with 2015-06-01 →
  2026-10-08 (the two limit regimes) is a *Stability check*; a model result (a lognormal path, a Monte Carlo
  estimate) is labelled a model, not a forecast. Nothing in Volume III is out-of-sample. Volume III stays on the
  model side of LM20–LM22: no confidence interval for a data estimate, no test statistic, no "the data leave the
  band"; a Monte Carlo interval ($\pm1.96$ standard errors of a simulation) is a property of the simulation.
- **Charts.** `line` (with the approved `step`, band, `quiet` and `dash` options), `bar`, `heatmap`, `scatter` and
  `vector` (AUTHORING §7); the approved `sci`, `sig` and `n6` format codes; at most four series that the legend
  names; every value the text cites is plotted or printed. A histogram is a step line; a QQ plot is a `scatter` with
  a 45° line; a pmf is a `bar` chart. A log $x$ axis is not available: plot $\log_{10}$ values on a numeric axis with
  `tickLabels`.
- **Widgets.** Use the approved `Book.controls`, `Book.rng` and `Book.dist` helpers instead of copying them. A widget
  may draw its own SVG with the coordinates `Book.lineChart` returns (as `lm05.js` does).
- **Labs.** One per module, generated by `build/make_labNN.py`, reading only its own `data/` folder
  (`data/make_lab_data.py`): `taiex_tr.csv` (`date`, `price`, the raw TR23 closes) in LM13–LM15, LM17 and LM18; LM16's
  lab holds only the Volume II sector files and repair cell. Labs write "LM18", never `[[LM18]]` (the generator
  resolves only `ex:` and `eg:` labels).
- **Problems.** Each stem states its sample, divisor, $A$, rounding, the quantile rule where a quantile is asked
  ($R_{(\lceil uT\rceil)}$, `method="inverted_cdf"`), and, for a simulation, the seed and the number of draws
  (PITFALLS §7). Every distractor is computed and fails for a reason worth explaining.
- **Leads and tags.** A module's `leads` are the modules that cite one of its tags or that its text points to with
  [[LMn]]; a tag's "users" list names only briefs that cite that tag. A module cites another module's exhibit or
  example in words with [[LMn]] (the builder resolves `[[ex:…]]` only within the module being built).

## Capability check (2026-10-18)

The owner approved, on 2026-10-18 (ROADMAP, "Decided by the owner"): (A) line-chart `step` series, bands between two
lines, `quiet` series and dashed `hline`/`vline`; (B) `Book.fmt` codes for scientific notation, significant figures
and `n6`; (C) shared helpers `Book.rng`, `Book.dist` and `Book.controls`; (D) the TR23 data pipeline (`data/raw/vol3/`,
`data/vol3_series.py`, the lab files). No new package: SciPy 1.18 covers every distribution and fit. (D) is committed
(`aa0fe4c`). The drafts' remaining requests have fallbacks and need no further approval: a log $x$ axis ($\log_{10}$
values with `tickLabels`), LM13's icon array (drawn by `lm13.js`), a tree diagram (a table of counts), ellipses drawn
above points (fill-less ellipses; already an owner option in TODO), a labelled point without a dot (a `points` entry
with `color: "transparent"`, as LM13's X2 does: the label keeps its own colour, while `r: 0` falls back to the default
radius, book.js:840).

## Editor's decisions on the drafts (2026-10-18)

The cross-module check's findings (C1–C32) and the drafters' open questions, decided. Each brief below already
follows them.

- **Ownership.** C1: one owner per TR23 statistic (Shared decisions, "Return type"). C3: LM14 prints the Chebyshev
  and Cantelli bounds against TR23's frequencies and the normal only at $k=4$ (LM5's PP9 promise); the normal's day
  counts at −3% and −5% are LM15's case. C4: LM14 owns the quantile function, the general median, empirical
  quantiles as order statistics (`method="inverted_cdf"`) and the interpolation pitfall, on TR23's empirical
  quantiles only; LM15 owns $\Phi^{-1}$, (15.6), the comparison with the normal and QQ plots; LM18 cites LM14's
  definition and proves only $F^{-1}(u)\le x\iff u\le F(x)$. C5: LM14's case prints the average day against the
  compound daily rate, $\bar R-R_G=0.7320$ bp against $s^2/2=0.7301$ bp (LM3's (3.9)); LM17 cites LM14 for the daily
  gap and keeps the factor $38.66/25.20$ and $\Pr(W_m>\E W_m)$. C9: LM13 states independence for $n$ discrete random
  variables (product of pmfs; iid named); LM16 states the general $n$-variable definition, $\E[\prod g_i(X_i)]=\prod
  \E[g_i(X_i)]$ and the variance of an $n$-term sum; LM13 gives no density version. C16: $\E[\mathbf 1_{\mathcal A}]=\Pr(\mathcal A)$ is
  LM14's tagged result. C21: clustering is shown once per tool (LM13 conditional probability, LM15 overdispersion,
  LM16 uncorrelated against dependent, LM17 kurtosis of sums, LM18 what resampling destroys), with one LM26 pointer
  per module. C22: LM16 owns the sum rule (16.3); LM17 cites it and owns $\Var(\bar X_n)=\sigma^2/n$; LM18 states its
  bootstrap mean path as (17.4) under $\hat F$. C23: LM13 explains countable additivity and events of probability
  zero; LM17 owns the path statement behind lm04.md:304; LM16 cites LM13. C24: LM14 reuses LM13's two-trade space in
  $+$/$-$ notation and adds the median and the expectation; LM14's problems use another law.
- **Models.** C2: LM15's lognormal fitted to the 23 calendar-year growth factors and LM17's iid daily model over one
  year are both kept and named apart, compared on the same window (2003–2025, 2003 from its first close): each module
  prints the other's losing-year probability in one sentence (LM15 26.5% for LM17's model, LM17 30.0% for LM15's
  fit). On 2003–2025 the means agree by construction (11.634% against 11.646% a year: the model's year is 246
  sessions, close to the years' average count), so the gap comes from the dispersion of annual log returns, 0.222 against the
  daily model's 0.186 (printed 0.22207 and 0.1856 in LM15, 22.207% and 18.563% in LM17). LM19 examines the √T
  scaling.
- **Inference edge.** C26: LM17 draws the model band without counting exits and gives the $n$ a precision needs as a
  model property, not applied to TR23; LM16 prints the model count's mean and standard deviation beside 177 without
  a ratio. A descriptive ratio of observed to model counts, such as LM14 E8's 17 days "92 times the expected count",
  or of a joint frequency to the product of its margins (LM16 E1's 3.29), is allowed when the text labels it
  descriptive and reads nothing from it; it is never offered as evidence. LM18 keeps its bootstrap variance $s^2/T$ as a property of the bootstrap model and says that LM20 derives
  the same $s/\sqrt T$ as the sampling error of $\bar R$. LM18 calls $\pm1.96$ standard errors "a 95% Monte Carlo
  interval".
- **Notation.** C6–C8, C11–C15 are in the table above; each module declares its local constants and residuals.
- **Facts the drafts corrected.** Of the 108 falls of 3% or more, 29.6% came the day after a move of 2% or more, so
  "crashes tend to follow big moves" (70.4% within five sessions, a lab item), never "most crashes". The pair-space
  comparison for signs is 0.4639 against 0.4521. The three months with eight moves of 3% or more are September 2008,
  October 2008 and March 2020. $(1+\bar R)^T=38.659$, printed 38.7 from $\bar R=0.06251\%$. Over the volume the up-day
  blocks are 20 sessions from 3 January 2003 (292 blocks; the last 9 returns left out), and their variance (4.72
  against 4.95) cannot see LM13's small sign dependence either way. $(R_t,\lvert R_{t+1}\rvert)$ correlate −0.130, so
  LM16's uncorrelated pair is $(R_t,R_{t+1})$ and its dependent pair $(\lvert R_t\rvert,\lvert R_{t+1}\rvert)$. The
  kurtosis of $m$-day log-return sums falls from 5.43 to 2.29 at $m=20$ (overlapping windows; independence predicts
  0.27) and stalls near 3.2 by $m=60$.
- **Per module.** LM13: prereq gains LM3 ((3.7)); the `bayes` widget's initial state shows the sample's 5,848
  day-pairs with exact counts (32, 76, 457, 5,283), its 1,000-day picture as an option; "prior" and "posterior"
  probability for events, with LM24 for parameters. LM14: the Jensen-chord widget, starting from 2008 and 2009; the
  exact Jensen-gap series (14.13) stays. LM15: "tail index" (LM5's term), reported as the range of log–log chords
  between adjacent levels, 2.09 (2%→3%) to 5.03 (5%→6%), no single value and no Hill estimate (LM20); a −10% row (2.57 expected under the $t$ fit, 0 actual) shows the
  limit; the gamma function's variable is $y$; exhibits print $\nu=3.065$ where 3.07 would not reproduce 19.6 days.
  LM16: prereq gains LM15 (the binomial count); the widget's model values come from a precomputed grid; the ellipse
  promise of lm11.md:148 is shown on the U28 pair (39.35% inside under the model against 56.16% in the data); the
  28-dimensional all-down comparison stays out of Volume III; LM10's 0.851 is cited as LM10's value from its printed
  returns. LM17: the mean path is printed beside the honest slowness of the median result ($\Pr(W>\E W)$ is about 32%
  after 23.8 years at $f=1$); the full-Kelly path's 98.5% loss by November 2008 is said once, with LM41; Peters (2019)
  is cited for the $+50\%/-40\%$ coin. LM18: prereq gains LM2 (common random numbers, (2.11)); the exponential law is
  LM18's; five years is $m=1{,}231$ sessions, and every module prints 5.49%; the $t$ model is a lab extension; the
  antithetic option stays in the widget because it shows when the method gains nothing; (18.9) is derived in a Deep
  Dive.

## Editor's decisions after the fresh check (2026-10-18)

A fresh check recomputed all 454 anchors from the raw files (all reproduced; A17-76's definition used the wrong rounding
boundary) and checked the briefs' claims, cross-references and sources. Decided: the ownership split of "Return type"
above (cross-check finding 1); $\mathcal A$ for an event in a general statement (finding 2); one leads rule (finding
3); the median written as a value $x$, never $m$ (finding 4); $k$ scoped in AUTHORING (finding 5); exhibits of other
modules cited in words (finding 6); NumPy's recommended seed order `[e, 20261011]` (sources); the general strong law
cited to Durrett or Wasserman; LM16 defines $\chi^2_N$ (the law of a sum of $N$ independent squared standard
normals, mean $N$), which LM21 and LM32 use; LM17's daily model is compared with LM15's annual fit on 2003–2025.
Every module's other findings are applied as each report proposes unless a decision above says otherwise; each brief
records any it declines.

## Stage 4 changes to earlier modules

Collected from the briefs; the editor applies them at publication, with the edition note.

- LM5:60 "[[LM14]] defines random variables" → "[[LM13]]"; LM5's 累積分配函數, 常態分配函數, 常態分配 → 累積分布函數,
  常態分布函數, 常態分布 (three strings).
- Getting Started's seed sentence (the Simulation decision above).
- Leads of Volumes I–II gain the Volume III modules that cite them for a result, by tag or by line, so that each
  earlier module's leads match the Volume III prereq lists (AUTHORING §3; each brief's "Stage 4 for earlier modules";
  a module that only honours an earlier module's forward link, as LM15 does lm04.md:541, is not added):
  lm01.md:6 gains 13, 14, 15, 16, 17, 18; lm02.md:6 gains 15, 18; lm03.md:6 gains 13, 15, 16, 17; lm04.md:6 gains 13,
  14, 17; lm05.md:6 gains 13, 16; lm07.md:6 gains 16; lm09.md:6 gains 16.

## LM13 Probability Foundations and Bayes

**Prereq** LM1 (the simple return; the total return with income reinvested, lm01.md:291–296), LM3 ((3.7), an average
with divisor $T$), LM4 (the binary bet $p$, $q=1-p$, $b$, $a$, traded "independently of other trades", lm04.md:296;
(4.7); "with probability one", lm04.md:304; the +2%/−1% bet with $f^*=25$ and $g^*=5.889\%$ [A13-01]), LM5 ($\Pr$ as an
area; $F(x):=\Pr(X\le x)$, $\Pr(a<X\le b)$ and the median, lm05.md:442–443; (5.9); (5.11), a ratio over
$\Pr(R\le\kappa)$, lm05.md:501–506; the price limit raised from 7% to 10% on 1 June 2015 [A13-02]). Front matter
`prereq: [1, 3, 4, 5]`; LM9 and LM12 are named only for a contrast and a pointer. **Leads**
`[14, 15, 16, 17, 18, 21, 24, 26]`: tags cited by 14–18; pointers to 21, 24, 26. Time "≈ 2.5 h + lab".
Syllabus line: "Sample spaces, conditional probability, Bayes' rule; a random variable is a function."

**Forward links honoured.**

| Source | Promise | Kept in |
|:--|:--|:--|
| lm05.md:440 | "[[LM13]] and [[LM14]] build probability theory properly" | §2–§6; expectation is LM14's |
| lm05.md:60 | "[[LM14]] defines random variables" | §6; Stage 4 retargets the link to [[LM13]] |
| lm05.md:442–443 | $F(x):=\Pr(X\le x)$, intervals $(a,b]$, the median | (13.11), same convention, for steps; discrete medians → LM14 |
| lm05.md:501–506 | (5.11) divides by $\Pr(R\le\kappa)$ | E4 and the (5.11) sentence |
| lm04.md:296, 300–304 | "independently of other trades"; $j/N\to p$ "with probability one" | (13.7); Deep Dive 1; the path statement → LM17 |
| lm02.md:763; lm03.md:360, 368; lm04.md:110, 302, 395 | bets "with equal probability", $g(f)$ and $\E$ before probability was defined | E1, E10; (13.3), whose expectations LM14 takes |
| lm12.md:504; 527 | "$N$ independent draws" (504, quoted); a 中文導讀 pointer with 亂數 (527) | (13.13); [[LM16]] for densities; 隨機數 from Volume III |
| lm09.md:354, 589 | **linearly independent**, 線性獨立 | §4: one sentence and the 中文導讀 |

**Outcomes** (each completes "After this module you should be able to:"):

1. "describe a random experiment by its sample space and events, and combine events with complements, unions and intersections"
2. "derive the complement rule, monotonicity and inclusion–exclusion from the axioms of probability, and apply them to equally likely outcomes and to the empirical distribution of a return sample"
3. "calculate conditional probabilities from counts and apply the multiplication rule to consecutive trading days"
4. "decide whether events, trials or discrete random variables are independent, distinguish pairwise from mutual independence and statistical from linear independence, and compute the probability of at least one event in independent trials"
5. "apply the law of total probability and Bayes' rule with base rates, counts and odds, and explain why a conditional probability and its inverse can differ several times over"
6. "define a random variable as a function on the sample space, and find the probability mass function and distribution function of a discrete random variable, an indicator included"
7. "compute conditional frequencies, Bayes' rule and independence checks from a return series in Python, counting threshold days with a tolerance for exact ties"

**Owns.** Sample spaces, outcomes, events and their operations; the axioms (countable additivity in Deep Dive 1) and
their consequences, complement rule, monotonicity, (13.1), (13.2); events of probability zero; equally likely outcomes
and the empirical distribution (mass $1/T$ on each day) as a probability model (13.3), in which every frequency is a
probability; conditional probability (13.4) and the chain (13.5); independence of events, complements, several events
(pairwise against mutual) and trials (13.6), (13.7); total probability (13.8), Bayes' rule (13.9) with base, hit and
false-alarm rates, prior and posterior probability of an event, the odds form (13.10), the prosecutor's fallacy;
random variables as functions on $\Omega$, indicators, $p_X$, $F_X$ (13.11), $\hat F$ (13.12); independence of $n$
discrete random variables and of functions of them (13.13), "iid". TR23's threshold counts it states first (108 at or
below −3%, 15 at or below −5%, X7).

**Leaves.** Expectation, moments, the median and quantiles, (14.1) $\E[\mathbf 1_{\mathcal A}]=\Pr(\mathcal A)$, the
words "population" and "sample" → LM14 (which reuses E1 and E10). Named distributions, the binomial count of orders,
fitting, counts per block → LM15. Joint laws, marginals, general independence and
$\E[\prod_ig_i(X_i)]=\prod_i\E[g_i(X_i)]$, conditional expectation ((5.11) as a case), covariance → LM16. $j/n\to p$
and "with probability one" for a path (lm04.md:304) → LM17. Drawing from $\hat F$, random numbers → LM18. Whether a
gap exceeds chance; the union bound as Bonferroni → LM21. Priors and posteriors for parameters → LM24.
Autocorrelation → LM25; volatility clustering models → LM26.

**Uses before taught.**

- §2, once each: "In this model every average is a sample average with divisor $T$, as in (3.7) of [[LM3]]; [[LM14]]
  shows why." "That a frequency settles near a probability as days accumulate is the law of large numbers of
  [[LM17]]."
- §3, E4: "Equation (5.11) of [[LM5]] is the mean of such a conditional distribution; [[LM16]] defines conditional
  expectation in general."
- §3, X3, the module's one clustering pointer: "Large moves come in clusters; [[LM26]] models them."
- §4, X4: "Whether a gap such as this is larger than chance alone produces is a question for the tests of [[LM21]]."
- §5, E9: "Counting the orders in which the good months can fall leads to the binomial distribution of [[LM15]]; Bayes'
  rule does not need that count, because it cancels." "[[LM24]] applies the same rule to an unknown parameter."
- §6, E10: "The probability-weighted average of a random variable is its expectation; [[LM14]] defines it and connects
  it with (5.9) of [[LM5]]."
- §6, after (13.13): "For random variables with densities, such as the normal draws of [[LM12]], [[LM16]] states
  independence through their joint distribution."

**Data role.** TR23 only, from `processed/vol3_taiex.parquet`, column `R`: 5,850 closes and $T=5{,}849$ simple returns
from 3 January 2003 to 8 October 2026 [A13-03]. Two consecutive days use the **pair space**, the 5,848 return dates
from 6 January 2003 that have a previous return [A13-04]; the first return, +2.24% on 3 January 2003 [A13-05], has
none. Thresholds are inclusive, counted with the shared guard; an exact `Fraction` recount from the two-decimal closes
agrees, finds no return equal to 0, ±1%, ±2%, ±3%, ±4% or ±5%, and finds 5,849 distinct returns [A13-06]. Scripts:
`data/lm13_numbers.py` (asserts every printed value against the anchors, LM10's `anchor()`) and `data/lm13_charts.py`.
No new data; no simulation, no seed.

**Hygiene declaration.** *Descriptive*: X1–X4, X6, X7, E2–E4, E8, the data counts of E6 and Problem 6, Problems 1,
4, 5, 10, the lab's 70.4%. *Stability check*: X5, E7, Problems 2, 7, 11 and the lab extension's per-regime shares
(returns 2003-01-03 → 2015-05-29, 3,077 days, against 2015-06-01 → 2026-10-08, 2,772 days [A13-07]). *In-sample
model*, labelled "model": every "if independent" figure (X4's second block, E2, E3, E6, Problems 5, 6, 10).
*Hypothetical*: E1, E5, E9, E10, Problems 3, 8, 9, 12, the widget away from its initial state. Nothing is
out-of-sample. Local note (66 words): "Every frequency in this module describes
TR23, 3 January 2003 to 8 October 2026: the probability of a day drawn at random from the sample, not a forecast.
Comparing the 7% and 10% limit regimes is a stability check. The independent-days figures are a model built from the
same days. The bets and the manager are hypothetical. [[LM21]] asks whether a gap is larger than chance."

**Notation.** Book-wide (§6): $R$, $R_t$ (on TR23 a random variable of the empirical model), $T$, $t$, $p$, $q$,
$b$, $a$, $f$, $f^*$, $g(f)$, $g^*$, $W_n$ (wealth after $n$ trades), $\Pr$. From the Probability table: $\Omega$,
$\omega$ with $+$/$-$ strings; events $A$, $B$, named in each example (the case's $A$: a fall of 3% or more today;
$B$: a move of 2% or more either way yesterday), complement $A^c$ (no annualizing, so no $\mathcal A$; no Kelly
fraction $c$); $\Pr(B\mid A)$; $\mathbf 1_A$, $\mathbf 1\{\cdot\}$; $X$, $Y$, $x$, $y$; $p_X$, $F_X$, $\hat F$; $n$,
the number of independent trials ($N$ stays the number of assets); $j$, a count of wins. Local, declared: $\cup$,
$\cap$, $\emptyset$, $\subseteq$; $\#A$, the number of outcomes in $A$ ($\lvert\cdot\rvert$ stays the absolute value);
$A_1,\dots,A_m$, a list of events or a partition. Counts and indices: $m$, a number of events (the table's $m$, days
summed, is unused); $i$, the index in (13.2), (13.8), (13.9), (13.13). $x_{\text{lo}}<x_{\text{hi}}$, the ends of an
interval in (13.11) ($a$, $b$ are the bet's; $x_1,\dots,x_n$ are values of $X_1,\dots,X_n$ in (13.13)). Thresholds
are numbers, never $c$. Not used: $\E$ outside citations; $\mu$, $\sigma$, $\Phi$, $Z$, $\kappa$, $k$, $u$, $\eta$,
$\zeta$, $C$, $P$; a joint pmf symbol.

**Motivating case: "After a big move"** (Descriptive, about 130 words).

> The TAIEX total-return index, dividends reinvested, gives 5,849 daily returns from 3 January 2003 to 8 October 2026.
> On 108 days it fell 3% or more: 1.85% of days [A13-08]. Big moves come in groups. Of the 108 falls, 32 (29.6%) came
> the day after a move of 2% or more either way [A13-09], against 7.96% of the other days [A13-10]. Yet of the 489 days
> after such a move [A13-11], only 32 fell 3% or more: 6.54% [A13-12]. That is 3.5 times the base rate [A13-13], but
> still under one day in fifteen.
>
> So "crashes tend to follow big moves" and "a big move rarely leads to a crash" are both true of the same 32 days.
> Why do the two shares differ, and how does Bayes' rule turn one into the other?

Resolved: (i) what "the share after a big move" is → §3, (13.4), X3; (ii) whether today's fall depends on yesterday →
§4, X4, E3 (in the sample, yes: 13 pairs of falls against 2.0 if days were independent, a model [A13-37]); (iii) why the shares
differ by a factor of 4.53 [A13-14] → §5, E8: a base rate of 1.85% against false alarms on 7.96% of 5,740 days
[A13-15]; (iv) how Bayes' rule converts one into the other → (13.9), (13.10), the widget. "Crash" only in the two
quoted sayings; never "most crashes".

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | a frequency becomes a probability; case + X1; roadmap; notation and hygiene notes | 400 |
| 2 | Sample Spaces, Events and the Axioms {1, 2} | E1; definitions; X2; axioms and consequences, a line each; (13.3), the empirical model, LM3/LM14 and LM17 sentences; E2; Deep Dive 1 | 760 |
| 3 | Conditional Probability {3} | "down after down" in X4's counts; (13.4); $\Pr(\cdot\mid A)$ obeys the axioms; (13.5); X3, LM26 sentence; E3; E4 | 620 |
| 4 | Independence {4} | (13.6), $\Pr(B\mid A)=\Pr(B)$ when $\Pr(A)>0$; X4, LM21 sentence; E5; (13.7) in LM4's words; E6; LM9's linear independence, one sentence; Deep Dive 2 | 660 |
| 5 | Total Probability and Bayes' Rule {5} | (13.8); E7 with X5; (13.9) from (13.4) twice; base, hit and false-alarm rates; E8; the frequency-format finding; (13.10); widget; E9 | 760 |
| 6 | Random Variables and Their Distributions {6} | E10 (two outcomes share a value); $\{X\le x\}$; indicators; $p_X$; (13.11); (13.12), X6; X7; (13.13), iid; LM14 and LM16 sentences; Deep Dive 3 | 680 |
| 7 | Probability in Python {7} | Polars `shift(1)` (a null in the first row, as in `R`); booleans with the guard; counts → Bayes; `Fraction`; lab box | 260 |
| — | Summary (7 bullets) / Practice Problems (12) / Solutions | | 140 / 400 / 560 |
| | **Total** | | **5,240** |

**Elements.** 10 examples; 6 knowledge checks (§2–§7); 5 中文導讀 (§2–§6); 6 pitfalls, one per section: §2 adding
overlapping events; §3 small denominators; §4 disjoint is not independent; §5 the prosecutor's fallacy; §6 $F_X(x)$
counts the point $x$; §7 exact ties at a threshold. Three Deep Dives:

1. (§2) Countable additivity, $\Pr(\bigcup_iA_i)=\sum_i\Pr(A_i)$ for disjoint $A_1,A_2,\dots$, and its consequence,
   continuity along a decreasing sequence of events and, by complements, along an increasing one. An event of
   probability zero: in a model of infinitely many independent fair trades (its existence *stated without proof*:
   Durrett (2019), §2.1.4, Theorem 2.1.21, Kolmogorov's extension theorem), "every trade loses" lies inside "the
   first $n$ trades lose", so its probability is at most $2^{-n}$ for every $n$, hence zero, though it is an outcome;
   "with probability one" names the complement of such an event. LM4's claim about wealth paths is LM17's. No
   σ-algebra. Reference: Wasserman (2004), §1.3 (axiom 3; Theorem 1.8, continuity).
2. (§4) If $A$ and $B$ are independent, so are $A$ and $B^c$, and $A^c$ and $B^c$; mutual independence of $m$ events
   needs $2^m-m-1$ product conditions, 4 for three events [A13-16]. Reference: Grinstead and Snell (1997), §4.1,
   Definition 4.2 and Exercises 7 and 17.
3. (§6) $F_X$ is non-decreasing and right-continuous, with limit 0 at $-\infty$ and 1 at $+\infty$, by Deep Dive 1's
   continuity (decreasing sequences for right-continuity and 0, increasing ones for 1); its jumps are the values of
   $p_X$.

Knowledge checks:

- §2: If $\Pr(A)=\Pr(B)=0.9$, how small can $\Pr(A\cap B)$ be? (0.8 [A13-17], from (13.1) and $\Pr(A\cup B)\le1$.)
- §3: $\Pr(\text{down today}\mid\text{down yesterday})=1{,}226/2{,}643=0.4639$ and the reverse
  $1{,}226/2{,}644=0.4637$ [A13-18]: why do they nearly agree (the margins almost match) when the case's pair differs
  4.5 times?
- §4: Are "up today" and "down today" independent? (Disjoint with positive probabilities: $\Pr$ of both is 0, the
  product $0.5480\times0.4520=0.2477$ [A13-19].)
- §5: With the case's hit and false-alarm rates (likelihood ratio 3.7215), what base rate makes $\Pr(A\mid B)=50\%$?
  (Prior odds $1/3.7215$, base rate 21.18% [A13-20].)
- §6: Is $\hat F(0)$ the share of down days? (Yes on TR23, 0.4520, as no return is 0; in general they differ by
  $\Pr(R=0)$.) And $\Pr(-1\%<R\le1\%)=\hat F(1\%)-\hat F(-1\%)=4{,}148/5{,}849=0.7092$ [A13-21].
- §7: What does `shift(1)` put in the first row, and why does the pair space have 5,848 days?

中文導讀: §2 樣本空間, 事件, 結果, 機率公設, 餘事件, 聯集, 交集, 互斥, 經驗分布; a TR23 frequency is an exact probability of the sample, not of tomorrow. §3 條件機率 shrinks the sample space
to the conditioning event (the 489 days after a big move). §4 獨立 against 互斥 and LM9's 線性獨立; 成對獨立 against
互相獨立; why the independence model overstates "at least one fall". §5 全機率法則, 貝氏定理, 基本率, 事前機率, 事後機率,
檢察官謬誤 (prosecutor's fallacy, the book's own form): 32 of 489 against 32 of 108. §6 隨機變數 as a function,
機率質量函數, 累積分布函數, 指示函數, 獨立同分布. 結果, 聯集, 交集 come from the same 樂詞網 lookup; odds, likelihood
ratio, hit and false-alarm rates, partition, inclusion–exclusion and frequency format stay in English.

References (details in SOURCES): Wasserman (2004), §1.3 (axioms, p. 5; Theorem 1.8, p. 7), §1.5–§1.7 (independence,
conditional probability, Bayes' theorem); Grinstead and Snell (1997), *Introduction to Probability*, 2nd rev. ed.,
AMS, §4.1 (Bayes' formula, Definitions 4.1–4.5, Theorem 4.1, Exercises 7 and 17); Durrett (2019), *Probability:
Theory and Examples*, 5th ed., §2.1.4, Theorem 2.1.21 (Deep Dive 1: an infinite sequence of independent random
variables with given distributions exists); Gigerenzer and Hoffrage (1995), *Psychological Review* 102(4), for one §5
sentence: stating the data as frequencies from natural sampling, rather than as probabilities, raised the share of
Bayesian answers from 16% to 46% (standard menu) and from 28% to 50% (short menu) [A13-22]. The paper says "frequency
formats", not "natural frequencies".

**Exhibits.**

- X1 table §1 {#case}, "Falls of 3% or more and the day before, TR23". Rows: after a move of 2% or more either way /
  after a smaller move / all; columns: fall of 3% or more today / other days / all. Cells 32, 457, 489 / 76, 5,283,
  5,359 / 108, 5,740, 5,848; a row-share column (6.54%, 1.42%, 1.85%) and a column-share row (29.63%, 7.96%, 8.36%)
  [A13-23]. Note: inclusive thresholds $\lvert R_{t-1}\rvert\ge2\%$, $R_t\le-3\%$; the 5,848 days with a previous day; no
  return equals ±2% or −3%; Source line (FinMind `TaiwanStockTotalReturnIndex`, TAIEX, retrieved 18 October 2026;
  dividends reinvested, no costs); Computations line.
- X2 `vector` §2 {#venn}, "Two events on the same days": $A$ = "fell 2% or more today", $B$ = "fell 2% or more
  yesterday" (as in the case), on the pair space; two circles (`ellipses`, `cov` $r^2I$, `fill`) inside a rectangle
  $\Omega$ (four `lines`); region counts as `points` with `label` and `color: "transparent"` (`r: 0` still draws a
  dot, book.js:840): 214 ($A$ only), 38, 214 ($B$ only), and 5,382 outside [A13-24]. Note: not to scale;
  $252+252-38=466$ days in $A\cup B$, (13.1).
- X3 `bar` §3 {#buckets}, "A fall of 3% or more, by yesterday's return": yesterday's return in $(-\infty,-3]$,
  $(-3,-2]$, $(-2,-1]$, $(-1,0]$, $(0,1]$, $(1,2]$, $(2,3]$, $(3,\infty)$ %; one series, the share of days that fell
  3% or more (`pct2`): 12.04, 5.56, 2.91, 1.60, 1.01, 1.15, 4.71, 4.48; `hline` 1.85% "all days". Note: days/falls
  per bucket 108/13, 144/8, 516/15, 1,875/30, 2,272/23, 696/8, 170/8, 67/3 [A13-25] (sums 5,848 and 108); a
  bucket holds its upper end, as LM5's intervals; no return sits on an edge; yesterday's returns end on 7 October
  2026, so $(-1,0]$ holds one day fewer than in X7.
- X4 table §4 {#signs}, "Down after down": rows yesterday down / up / all; columns down today, up today, days,
  $\Pr(\text{down today}\mid\text{row})$ to four decimals: 1,226, 1,417, 2,643, 0.4639 / 1,418, 1,787, 3,205, 0.4424 /
  2,644, 3,204, 5,848, 0.4521 [A13-26]; a second block, "if independent" (row total × column total ÷ 5,848, one decimal):
  1,195.0, 1,448.0 / 1,449.0, 1,756.0, sum 5,848.0 [A13-27]. Note: no return is 0, so "up" is "not down"; the second
  block is a model.
- X5 table §5 {#regimetab}, "Two limit regimes": rows 7% (returns 2003-01-03 → 2015-05-29), 10% (2015-06-01 →
  2026-10-08), all. Columns: days 3,077 / 2,772 / 5,849; share of days 52.61% / 47.39% / 100%; falls of 3% or more
  72 / 36 / 108, share 2.34% / 1.30% / 1.85%; after a big move, falls/days 17/303 (5.61%), 15/186 (8.06%), 32/489
  (6.54%); hit rate 23.61%, 41.67%, 29.63% [A13-28]. Note: pairs inside one regime (3,076 and 2,771); the pair 29 May →
  1 June 2015 (−0.12%, then −0.77%) is in neither and changes no count; Stability check.
- X6 `line` §6 {#ecdf}, "The distribution function of a TAIEX day": $\hat F$ with the approved `step` option from the
  5,849 sorted returns, x from −10% to +10% (`fmt: "pct2"`, `tfmt: "pct0"`), y from 0 to 1 (`fmt: "n4"`,
  `tfmt: "n1"`); point annotations at −3% (0.0185), 0 (0.4520) and +3% (0.9885) [A13-29]. Note: $\hat F$ jumps by
  $1/5{,}849$ at each return; the extremes −9.70% (7 April 2025) and +9.25% (10 April 2025) [A13-30] lie inside the
  axis.
- X7 `bar` §6 {#bins}, "A function of $R$: the 1% bin": 12 categories $(-\infty,-5]$, $(-5,-4]$, …, $(4,5]$,
  $(5,\infty)$ %, the pmf of the bin variable (`pct2`): 0.26, 0.50, 1.09, 2.46, 8.82, 32.07, 38.84, 11.90, 2.91, 0.63,
  0.29, 0.22. Note: counts 15, 29, 64, 144, 516, 1,876, 2,272, 696, 170, 37, 17, 13 [A13-31]; the first three bars hold
  the 108 falls, $\hat F(-3\%)$; the printed shares sum to 99.99%, so the note prints counts, not a total.

**Widget `bayes`, "From a hit rate to a conditional probability."** Controls (`Book.controls`): base rate $\Pr(A)$
0.1%–50%, hit rate $\Pr(B\mid A)$ and false-alarm rate $\Pr(B\mid A^c)$ 0–100%, steps of 0.01 points; a preset "TR23
counts", the initial state, sets the exact fractions 108/5,848, 32/108 and 457/5,740; a select "Days in the
picture": the sample's 5,848 (initial) or 1,000. The sliders snap to the grid (1.85%, 29.63%, 7.96%), so the preset
keeps its exact inputs apart and the labels show 1.847%, 29.63%, 7.962% until a slider moves. Readouts: $\Pr(B)$,
$\Pr(A\mid B)$, $\Pr(A\mid B^c)$, $\Pr(A\mid B)/\Pr(A)$ (in the preset labelled "÷ 108/5,848"), the likelihood
ratio, prior and posterior odds, the picture's four counts. A readout whose denominator is 0 shows "— (undefined)":
$\Pr(A\mid B)$ when both rates are 0; $\Pr(A\mid B^c)$ when both are 100%; the likelihood ratio and posterior odds
when the false-alarm rate is 0. Picture: an icon array of SVG squares drawn by `lm13.js`, 86 × 68 for 5,848 days or
40 × 25 for 1,000: fall after a big move (series 1), fall after a smaller move (series 2), big move without a fall
(series 1, light), neither (neutral). Initial state (the PDF): readouts 8.36%, 6.54%, 1.42%, 3.54 [A13-32],
likelihood ratio 3.7215, odds 0.018815 and 0.07002 [A13-33], printed so that prior × ratio reproduces the posterior;
squares 32, 76, 457, 5,283, the exact counts. At 1,000 days the counts become whole squares by largest remainder, 6, 13, 78, 903, noted "rounded
to whole days": the picture shows 6 of 84, 7.1% [A13-34], against the readout's 6.54%. No randomness, no seed.

**Examples** (inputs at the precision printed; every output follows from them).

- E1 §2 {#twotrades} Two trades as a sample space: LM4's +2%/−1% bet traded twice; $\Omega=\{++,+-,-+,--\}$; $A$ =
  "the first trade wins" $=\{++,+-\}$, $B$ = "at least one loss" $=\{+-,-+,--\}$; $A^c$, $A\cap B=\{+-\}$,
  $A\cup B=\Omega$. With the outcomes equally likely ($p=1/2$, independent trades, justified in §4):
  $\Pr(B)=1-\Pr(++)=3/4$, $\Pr(A\cap B)=1/4$; at $f=25$ wealth ends below its start only on $--$ [A13-35].
- E2 §2 {#twofalls} Inclusion–exclusion with X2's events: 252 days fell 2% or more today ($A$), 252 the day before
  ($B$), 38 both; $\Pr(A\cup B)=466/5{,}848=7.97\%$; adding without the overlap gives 504 days, 8.62%, the union bound
  (13.2); if the two days were independent (model), both would happen on about $5{,}848\times0.0431^2=10.9$ days
  [A13-36], not 38.
- E3 §3 {#fallsinarow} Two falls in a row: $\Pr(A_{\text{yesterday}})=108/5{,}848$ and
  $\Pr(A_{\text{today}}\mid A_{\text{yesterday}})=13/108=12.04\%$, so by (13.5) $\Pr(\text{both})=13/5{,}848=0.222\%$;
  against the base rate of 1.85% (108/5,848), a fall yesterday makes one today 6.5 times as frequent;
  independence (model) would give $108^2/5{,}848=2.0$ such pairs [A13-37].
- E4 §3 {#tail} Inside the tail: $\Pr(R\le-5\%\mid R\le-3\%)=15/108=13.9\%$ and
  $\Pr(R\le-4\%\mid R\le-3\%)=44/108=40.7\%$; the 108 days averaged −4.06% [A13-38] (an average as in LM3); the (5.11)
  sentence.
- E5 §4 {#pairwise} Pairwise is not mutual: two independent fair trades; $A_1$ = "the first wins", $A_2$ = "the second
  wins", $A_3$ = "the two agree"; each has probability 1/2 and each pair 1/4, but
  $\Pr(A_1\cap A_2\cap A_3)=1/4\ne1/8$ [A13-39].
- E6 §4 {#atleastone} At least one fall of 3% in 20 sessions: with independent days and $\Pr(A)=108/5{,}849=1.8465\%$,
  printed to five digits, (13.7) gives $1-(1-0.018465)^{20}=31.1\%$ (model), about 91 of TR23's 292 blocks of 20
  sessions from 3 January 2003 (the last 9 returns left out); the data have 61 such blocks, 20.9% [A13-40]. Falls
  cluster (§3), so they fill fewer blocks.
- E7 §5 {#regimes} Total probability across the limit regimes (Stability check), in counts:
  $\Pr(A)=\frac{72}{3{,}077}\cdot\frac{3{,}077}{5{,}849}+\frac{36}{2{,}772}\cdot\frac{2{,}772}{5{,}849}=\frac{108}{5{,}849}=1.85\%$
  by (13.8), with the rates 2.34% and 1.30% and the weights 52.6% and 47.4% printed for reading; by (13.9),
  $\Pr(10\%\text{ regime}\mid A)=36/108=33.3\%$ against the prior 47.4% [A13-41]. The rounded percentages would give
  33.4%.
- E8 §5 {#casebayes} The case by Bayes' rule, three ways: (a) X1 read down its columns as a tree of counts,
  $32/(32+457)=6.54\%$; (b) (13.9) with $\Pr(A)=1.847\%$, $\Pr(B\mid A)=29.63\%$, $\Pr(B\mid A^c)=7.962\%$, four
  significant digits: $0.01847\times0.2963/(0.01847\times0.2963+0.98153\times0.07962)=6.54\%$ [A13-42]; (c) (13.10): prior
  odds $108:5{,}740=0.018815$, likelihood ratio $(32/108)/(457/5{,}740)=3.7215$ from counts, posterior odds
  $0.018815\times3.7215=0.07002$ ($=32:457$), probability $0.07002/1.07002=6.54\%$. The case's rounded inputs give 6.55%,
  so the example says the case rounds.
- E9 §5 {#manager} A manager who beat the index in 8 of 12 months (hypothetical): before the record, 10% of managers
  are skilled and beat it in a month with probability 0.55, the others with 0.5; months independent given the manager's type (13.7). Likelihood
  ratio $0.55^8\times0.45^4/0.5^{12}=1.4064$; posterior odds $(0.1/0.9)\times1.4064=0.15627$;
  $\Pr(\text{skilled}\mid\text{record})=13.5\%$ [A13-43]. The LM15 and LM24 sentences.
- E10 §6 {#rvtrades} A random variable on two trades: $X=W_2/W_0$ at $f=25$ on E1's $\Omega$: $X(++)=1.5^2=2.25$,
  $X(+-)=X(-+)=1.125$, $X(--)=0.5625$; $p_X$: 1/4, 1/2, 1/4; $F_X(1)=\Pr(W_2<W_0)=1/4$; the per-trade log growth
  $\tfrac12\ln X$: $\ln1.5=40.55\%$, $\tfrac12\ln1.125=g^*=5.889\%$, $\ln0.75=-28.77\%$ [A13-44]; the indicator
  $\mathbf 1\{X<1\}$; the LM14 sentence. The weighted average is shown as an identity,
  $\tfrac14\ln1.5+\tfrac12g^*+\tfrac14\ln0.75=g^*$, since $\tfrac12(\ln1.5+\ln0.75)=g^*$; the printed percentages
  average to 5.8895, a tie (PITFALLS §7).

**Problems plan** (12; MC keys C, B, A, C; Python: 11). Each stem names its sample (5,849 returns, 5,848 pairs or
5,847 triples), inclusive thresholds, rounding and, for a model, the independence assumption; no stem needs
annualization, a quantile or a seed.

1. MC §2. On TR23, $\Pr(R\le-2\%)=4.31\%$ and $\Pr(R\ge2\%)=4.05\%$. Closest to $\Pr(\lvert R\rvert\ge2\%)$: **A**
   0.17% (the product: "or" read as "and"), **B** 8.19% ($1-(1-0.0431)(1-0.0405)$: subtracts an overlap that disjoint
   events lack), **C** 8.36% (disjoint, so add; exactly 489/5,849) [A13-45]. Key **C**.
2. MC §5. Inside the 10% regime (2,771 days with a previous day in it): base rate 1.299%, hit rate 41.67%, false-alarm
   rate 6.252%. Closest to $\Pr(\text{fall of 3\% or more}\mid\text{big move yesterday})$: **A** 41.7% (the inverted
   conditional), **B** 8.06% (exactly 15/186), **C** 1.30% (the base rate, evidence ignored) [A13-46]. Key **B**.
3. MC §4. E5's three events are: **A** pairwise but not mutually independent; **B** mutually independent
   ($\Pr(A_1\cap A_2\cap A_3)$ taken as 1/8 without counting); **C** not even pairwise independent ($A_3$ is built from
   $A_1$ and $A_2$, yet $\Pr(A_1\cap A_3)=\Pr(++)=1/4$). Key **A**.
4. §2. Derive inclusion–exclusion for three events from (13.1) applied twice; apply it to falls of 2% or more on three
   consecutive days over the 5,847 triples: 252, 252, 252; pairs 38, 34, 38; all three 8; union 654 (11.19%) against
   the union bound 756 (12.93%) [A13-47].
5. §3. Chain rule for three down days in a row, everything on the 5,847 triples: $0.4519\times0.4637\times0.4424=9.27\%$
   (counts 2,642, 1,225, 542); independent days with each day's own down share in the triples (2,642, 2,643 and 2,644
   of 5,847: 0.4519, 0.4520, 0.4522) give 9.24% [A13-48]. Comment: the third factor, 0.4424, is below the second.
6. §4. The smallest $n$ with $1-(1-108/5{,}849)^n\ge50\%$ is 38 (49.82% at 37, 50.75% at 38); TR23's 153 blocks of 38
   sessions (the last 35 returns left out) hold 50 with a fall of 3% or more, 32.68% [A13-49]. Explain the gap.
7. §5. E7's partition for falls of 5% or more: 8 of 3,077 and 7 of 2,772 days (0.2600% and 0.2525%); likelihood ratio
   0.971; $\Pr(10\%\text{ regime}\mid R\le-5\%)=7/15=46.7\%$ against the prior 47.4% [A13-50]: a ratio near 1 hardly moves
   a probability.
8. §5. E9 with 16 good months of 24: likelihood ratio 1.9780, posterior 18.02%; the prior that would make 8 of 12 give
   50% is 41.56% [A13-51].
9. §6. Three independent trades of the bet at $f=25$, $p=1/2$: list the 8 outcomes; $W_3/W_0$ takes 3.375, 1.6875,
   0.84375, 0.421875 with probabilities 1/8, 3/8, 3/8, 1/8 [A13-52]; $\Pr(W_3<W_0)=1/2$ although $g^*>0$ (LM17 for the
   long run).
10. §6. On the pair space, $X=\mathbf 1\{R_{t-1}<0\}$ and $Y=\mathbf 1\{R_t<0\}$ are not independent in the empirical
    model ($\Pr(X=1,Y=1)=1{,}226/5{,}848=0.2096$ against $0.4519\times0.4521=0.2043$ [A13-53]); explain why this alone
    does not show that returns depend on yesterday (LM21).
11. Python §7. From `taiex_tr.csv`: rebuild X1 with `shift(1)` and the guard; repeat inside the 10% regime (15/186 =
    8.06%, hit rate 15/36 = 41.67%, as in X5); confirm with `Fraction` that no return equals ±2% or −3%.
12. MC §6. $X$ = the number of losing trades in two independent trades with win probability 0.55. $F_X(1)$ is closest
    to **A** 0.4950 ($2pq$, the pmf at 1), **B** 0.6975 ($1-p^2$, wins counted instead of losses), **C** 0.7975
    ($1-q^2$) [A13-54]. Key **C**.

**Lab parts** (`build/make_lab13.py`; `taiex_tr.csv`): 1 data: returns, $T$, first and last dates, a `Fraction`
recount of the threshold days; 2 events and axioms: indicators, (13.1), (13.2), E2, X2's counts; 3 conditional
probability: X1, X3, E3, E4; 4 independence: X4, E5 by enumeration, E6 and the same count for 5, 10 and 60 sessions;
5 total probability and Bayes: X5, E7, E8 three ways, E9; 6 random variables: E10 by enumeration, X6, X7, the step at
a point; 7 Problems 4, 5, 6, 7, 10, 11. Extension (no conclusions): the fall share
after a move of 1%, 1.5%, 2% or 3% or more yesterday in each regime, with counts (Stability check); and, on all days, a
big move anywhere in the previous five sessions, which precedes 70.4% of the falls [A13-55] (5,844 days; Descriptive).

**Cross-module tags** (users: the briefs that cite the tag). (13.1) $\Pr(A\cup B)=\Pr(A)+\Pr(B)-\Pr(A\cap B)$. (13.2)
$\Pr(A_1\cup\dots\cup A_m)\le\sum_i\Pr(A_i)$. (13.3) $\Pr(A)=\#A/\#\Omega$ for equally likely outcomes; on a sample of
$T$ days, the number of days in $A$ divided by $T$ (LM15, LM17, LM18). (13.4) $\Pr(B\mid A):=\Pr(A\cap B)/\Pr(A)$,
$\Pr(A)>0$ (LM16). (13.5) $\Pr(A\cap B)=\Pr(A)\Pr(B\mid A)$ and its chain
$\Pr(A_1\cap\dots\cap A_m)=\Pr(A_1)\Pr(A_2\mid A_1)\cdots\Pr(A_m\mid A_1\cap\dots\cap A_{m-1})$, when
$\Pr(A_1\cap\dots\cap A_{m-1})>0$ (LM16). (13.6) $\Pr(A\cap B)=\Pr(A)\Pr(B)$ (LM16, LM17). (13.7) independent trials:
a given sequence with $j$ wins in $n$ has probability $p^jq^{n-j}$, and
$\Pr(A\text{ at least once in }n)=1-(1-\Pr(A))^n$ (LM15, LM17, LM18). (13.8) $\Pr(B)=\sum_i\Pr(B\mid A_i)\Pr(A_i)$ for a partition (LM16). (13.9)
$\Pr(A_i\mid B)=\Pr(B\mid A_i)\Pr(A_i)/\Pr(B)$, $\Pr(B)$ from (13.8). (13.10) posterior odds = prior odds × likelihood
ratio. (13.11) $F_X(x):=\Pr(X\le x)$, $\Pr(x_{\text{lo}}<X\le x_{\text{hi}})=F_X(x_{\text{hi}})-F_X(x_{\text{lo}})$
(LM14, LM15, LM16, LM18). (13.12) $\hat F(x)=\#\{t:R_t\le x\}/T$ (LM14, LM15, LM17, LM18). (13.13) discrete
$X_1,\dots,X_n$ are independent if and only if $\Pr(X_1=x_1,\dots,X_n=x_n)=\prod_ip_{X_i}(x_i)$ for all
$x_1,\dots,x_n$; iid if they also share one pmf (LM14, LM15, LM16, LM17, LM18). Tags with no user are used in words;
LM21 and LM24 add themselves.

**Pitfalls to pre-empt.**

- Conditions, besides those in the tags: $\Pr(B\mid A)=\Pr(B)$ as a test needs $\Pr(A)>0$; (13.8) a partition
  (disjoint, union $\Omega$) with each $\Pr(A_i)>0$, (13.9) also $\Pr(B)>0$; the odds form $0<\Pr(A)<1$ and
  $\Pr(B\mid A^c)>0$; (13.3) a finite $\Omega$ of equally likely outcomes; mutual independence every sub-collection;
  (13.7)'s "at least once" independent trials with one probability.
- Readings, besides the six section pitfalls: statistical is not linear independence; a frequency of the empirical
  model is not a forecast; E10's $\Pr(X<1.125)=1/4$ against $F_X(1.125)=3/4$; X3's outer buckets and E3 rest on 3 and
  13 days.
- Rounding (PITFALLS §7): compute from counts or print the digits E6, E7, E8 and the widget state; E10 by its
  identity.
- Data: 5,849 days for single-day shares, 5,848 for pairs, 5,847 for triples: $\Pr(\text{down})$ is 0.4520 on all days
  and 0.4521 on the pair space; X4 and Problem 5 compare inside one space. A ratio to the base rate names its
  denominator. Blocks say where they start and how many returns are left out. 7 April 2025 (−9.70%) was capped by the
  10% limit for many stocks. TR23's daily return exceeds the price index's on ex-dividend days by up to 84 bp
  [A13-56]; never mix the two. The guard stays in every script and printed code although TR23 has no exact ties
  (PITFALLS §5).

**Stage 4 for earlier modules.**

- Leads gain 13 (LM13 cites them): lm01.md:6 (now [2, 3, 5, 6, 8, 19, 38]), lm03.md:6 (now [4, 5, 6, 7,
  8, 10, 14, 37, 42, 46]), lm04.md:6 (now [6, 7, 12, 20, 41, 42]), lm05.md:6 (now [12, 14, 15, 17, 18]).
- lm05.md:60 "[[LM14]] defines random variables" → "[[LM13]]"; LM5's 累積分配函數 → 累積分布函數, which LM13's §6 box
  uses.

## LM14 Random Variables, Expectation and Jensen's Inequality

**Prereq:** LM1 ((1.9)–(1.10) $R_G$ and $g$; (1.12) $\ln G=\sum_tr_t$; the weighted AM–GM statement, (1.14) and the
short-position counterexample, lm01.md:431–435; the strict unweighted AM–GM, lm01.md:265), LM3 ((3.3) the series of
$\ln(1+x)$; $\ln(1+x)\le x$, lm03.md:247; (3.7)–(3.9), the volatility drag and the Result box, lm03.md:315–330; the
+100%/−50% pitfall, lm03.md:368), LM4 (concave and convex, the $h''$ test, lm04.md:152–157; the tangent-line Deep Dive,
lm04.md:166–170; (4.1), (4.4), (4.7); $\E[R^2]=\sigma^2+\mu^2$, lm04.md:57, 112; the normal approximations and 0050's
fourth moment, lm04.md:130–132; the +2%/−1% bet {#coin}, $f^*$, $g^*$, lm04.md:342–349; Practice Problem 13's third
moments and the +1%/−5% trade's exact Kelly exposure, lm04.md:718), LM5 ((5.5); (5.6); (5.7) and the normal moments,
lm05.md:305–327; Pareto moments and [[ex:tails]], lm05.md:331–348; the definitions and (5.9), lm05.md:442–447; (5.12),
lm05.md:511–523; Practice Problem 9, lm05.md:712, 749), LM13 ($\Omega$ in $+$/$-$ strings, events, $\Pr$, events of
probability zero; random variables as functions, $p_X$, $F_X$ (13.11), $\hat F$ (13.12); independence of discrete
random variables (13.13); E10's $X=W_2/W_0$). Front matter `prereq: [1, 3, 4, 5, 13]`.
**Leads:** LM15, 16, 17, 18, 19, 20, 32, 41 (LM15–LM18 cite its tags; its text points to the rest). Time "≈ 2.5 h +
lab". Syllabus line (src/syllabus.yaml:48): "LOTUS, moments, E[R²] = σ² + μ², and the real reason for volatility drag."

**Forward links honoured.**

| File:line | Promise | Kept in |
|:--|:--|:--|
| src/lm01.md:265, 421, 431–435 | the strict unweighted AM–GM; drag's "general form, Jensen's inequality"; weighted AM–GM with its conditions, derived from Jensen; (1.14) and its counterexample | §6: (14.10), (14.11) with LM1's conditions ($w_j=1/J$ for l.265, strict by Deep Dive 3); E9; pitfall; Problem 8; §7 (14.12) |
| src/lm03.md:315–330, 368 | (3.7) "needs no probability theory"; "population variance" $s^2$; drag $\bar R-R_G$ and (3.8)–(3.9) to second order, the rest depending on skewness; the +100%/−50% pitfall | §2 population/sample sentence; (3.7) is (14.4) under $\hat F$; §7 keeps the drag, names the Jensen gap; (3.8)–(3.9) are (14.13)'s second order, its third $-\operatorname{Skew}\cdot\sigma^3/(3(1+\mu)^3)$; X8 row 4 |
| src/lm03.md:545 | $\Var(Z^2)=2$ used without proof | (14.6) |
| src/lm04.md:57, 112, 130, 718 | $\E[R^2]=\sigma^2+\mu^2$, "the population form of (3.7)"; normal $m_3\approx3\mu\sigma^2$, $m_4\approx3\sigma^4$; the bet's third moment $\mu^3+3\mu\sigma^2$ | (14.4); (14.6) exact, E6 sizes the dropped terms; E5 |
| src/lm04.md:110, 166–170, 176–184, 302, 395 | (4.1), (4.4)–(4.7); tangent lines; "the sample version of $\E[R/(1+fR)]=0$" | E4, the differentiation sentence; proof of (14.10); Problem 9 |
| src/lm05.md:60, 440–447 | "[[LM14]] defines random variables" (→ [[LM13]] at Stage 4); "[[LM13]] and [[LM14]] build probability theory properly"; a median is a value $x$ with $F(x)=1/2$; (5.9) | §2 densities, $F_X$, quantiles, the general median; §3 (5.9) as LOTUS's continuous form |
| src/lm05.md:348, 366, 745 | normal kurtosis 3 stated without proof; excess kurtosis; skewness "its standardized form, [[LM19]]" | $\E[Z^4]=3$ derived; (14.5) for a distribution |
| src/lm05.md:516–523 | the lognormal factor $e^{\sigma_X^2/2}$ "is exact" | §7: the lognormal Jensen gap is exactly $\sigma_r^2/2$ |
| src/lm05.md:712, 749; reviews/lm05.md:181 | Cantelli's $1/(1+4^2)$ "of [[LM14]]", for "every distribution with a finite variance"; skewness | (14.9) with that condition; E8; (14.5) |
| build/build_index.py:143–144; src/pages/getting-started.md:124 | $\mu=\E[R]$, $\sigma^2=\Var(R)$, $g=\E[\ln(1+R)]$; divisor $T$ | the moments of $\hat F$; $g=\bar r$ under $\hat F$ |
| project/PITFALLS.md §7 (l.218, 224) | AM–GM conditions; a raw third moment is not skewness | §6; §4 pitfall |

**Outcomes** (each completes "After this module you should be able to:"):

1. describe a discrete or continuous random variable by its pmf or density and its distribution function, and find its
   quantiles and medians, including those of a sample's empirical distribution {lo=1}
2. calculate expectations as probability-weighted sums or integrals, check that they exist, and apply LOTUS and
   linearity, including to $g(f)=\E[\ln(1+fR)]$ {lo=2}
3. derive $\E[X^2]=\sigma_X^2+\mu_X^2$, $\Var(\eta X+\zeta)=\eta^2\Var(X)$, $\E[Z^4]=3$ and $\Var(Z^2)=2$, and compute
   the skewness and kurtosis of a distribution {lo=3}
4. apply Markov's, Chebyshev's and Cantelli's inequalities under their conditions and compare their bounds with TAIEX's
   tail frequencies {lo=4}
5. prove Jensen's inequality and its strict form from the tangent-line property, and derive the weighted AM–GM
   inequality from it {lo=5}
6. explain volatility drag through the Jensen gap $\ln(1+\mu)-g$ of the logarithm, compute both exactly, and judge
   when $\sigma^2/2$ describes them {lo=6}
7. compute the distribution, quantiles, moments and tail frequencies of an empirical distribution in Python, stating the
   quantile and moment conventions {lo=7}

**Owns.** Discrete and continuous random variables side by side: $p_X$ (LM13's), $f_X$ (LM5's), one
$F_X(x):=\Pr(X\le x)$. The quantile function $F_X^{-1}(u):=\min\{x:F_X(x)\ge u\}$, $0<u<1$ (LM15, LM18 and LM32 cite
it); the general median: a value $x$ is a median of $X$ if $\Pr(X\le x)\ge\tfrac12$ and
$\Pr(X\ge x)\ge\tfrac12$ (the medians form a closed interval, possibly one point); empirical quantiles as order
statistics, $\hat F^{-1}(u)=R_{(\lceil uT\rceil)}$ (`method="inverted_cdf"`), and the interpolation pitfall, on TR23's
empirical quantiles only (C4). TR23 under $\hat F$ and the population/sample sentence (Shared decisions; LM3's
"population variance" $s^2$ is the variance of $\hat F$). By "Return type": TR23's full-sample Skew, Kurt and excess
kurtosis (E6, X4) and the bound tables (X5, X6, E7, E8). Tags (14.1)–(14.13). The Jensen gap $\ln(1+\mu)-g$, named
apart from LM3's drag $\mu-R_G$; TR23's daily Jensen gap and drag (E10), the lognormal comparison and the $f=2$ Jensen
gap (LM17 cites them).

**Leaves.**

- Named distributions, $\Phi^{-1}$, (15.6), QQ plots, fits to TR23, the normal's day counts at −3% and −5%, tail
  measures that need fewer moments, the fragility of the kurtosis → LM15.
- Joint distributions, covariance, variance of a sum, independence in general, $\E[\prod g_i(X_i)]=\prod\E[g_i(X_i)]$
  → LM16.
- Laws of large numbers, the CLT, $\Var(\bar X_n)=\sigma^2/n$, mean and median paths, the running kurtosis, the
  kurtosis of $m$-day sums → LM17. Monte Carlo; resampling from $\hat F$ → LM18.
- Sample skewness and kurtosis → LM19; $T$ against $T-1$, standard errors → LM20; testing a tail frequency → LM21;
  value at risk → LM32; continuous-time drag → LM37, LM38; Kelly for a general $R$, differentiating under $\E$ → LM41.

**Uses before taught.**

- §2, after E2: "[[LM32]] turns lower quantiles into value at risk; [[LM15]] compares them with a normal model's."
- §3, E3: "The expectation of a product of independent factors is the product of the expectations, a rule [[LM16]]
  proves; here the four outcomes give it directly."
- §3, after (14.2): "That (5.9) equals $\int y\,f_Y(y)\,dy$ when $Y=h(X)$ has a density is stated without proof, for a
  continuous $h$ and an integral that exists (Grinstead and Snell 1997, §6.3, Theorem 6.11)." After (14.3): "For
  densities, $\E[X+Y]=\E[X]+\E[Y]$ is stated without proof (Grinstead and Snell 1997, §6.3, Theorem 6.10)." Everything
  else is derived; the $h''$ test stays LM4's (Simon and Blume 1994).
- §3, once each: "Why the average of many independent draws approaches the expectation is the law of large numbers of
  [[LM17]]." "Random variables that are neither discrete nor continuous need a more general integral, which this book
  does not use." After E4: "Differentiating under the expectation, as (4.5) does term by term, needs a condition when
  $R$ takes infinitely many values; [[LM41]] states it."
- §4, after (14.4): "The variance of a sum needs the covariance of its terms ([[LM16]])." After (14.5): "Applied to a
  sample, (14.5) gives the sample skewness and kurtosis; $T$ or $T-1$, and how far such numbers move between samples,
  are questions for [[LM19]] and [[LM20]]." At E6: "[[LM15]] fits distributions to TR23; this normal is only a
  benchmark."
- §7: "Which of the two rates an investor lives through over many periods is the subject of [[LM17]]."

**Data role.** TR23 only: $T=5{,}849$ [A14-01] returns, 8,680 calendar days $=23.7645$ years [A14-02], $A=246.12$
[A14-03], column `R` of `processed/vol3_taiex.parquet`. It enters as its empirical law $\hat F$ (mass $1/T$ per
return, moments with divisor $T$), so every identity and inequality checks exactly. Calendar
years 2003–2025, 2003 from its first close (2 January 2003); 2026 is partial and excluded. The small laws (E1, E5, X8,
Problems 1, 2, 4, 9) are exact; the 2008/2009 law uses the printed returns. 0050 values only as LM4 and LM5
print them; LM13's counts at −3% and −5% are cited as LM13's. No simulation. Scripts: `data/lm14_numbers.py` (asserts
every printed value; hand calculations from printed inputs; `tie()`) and `data/lm14_charts.py` (X1, X5, X7, widget).

**Hygiene declaration.** *Descriptive:* every TR23 frequency, quantile, moment, bound check, drag and Jensen gap.
*In-sample:* the normal with $\mu=\bar R$, $\sigma=s$ (X4, E6) and $\Phi(-4)$ in E8 (a descriptive ratio; C26).
*Model:* the small laws and the lognormal form. *Stability check:* the lab extension. Nothing out-of-sample; no
interval, no test. Local note: "Every frequency, quantile and moment of TAIEX in this module
describes its 5,849 days from 3 January 2003 to 8 October 2026, or its calendar years 2003–2025 (2003 from its first
close, 2 January 2003), as a probability model, the empirical distribution: none is a forecast. The normal model with
the same mean and standard deviation is fitted and judged on the same days. [[LM17]] asks when sample averages approach
expectations, and [[LM20]] treats estimation."

**Notation.** AUTHORING §6, Probability ($\mathcal A$ for an event in a general statement; $\eta$, $\zeta$; $k\ge0$).
Under $\hat F$: $\mu=\bar R$, $\sigma=s$, $g=\bar r$; $\bar g(f)$ only as (4.4), with $\bar g(1)=\bar r$ said once (E4);
$\E_{\hat F}$ and $\hat F^{-1}$ (vol-3 table; declared in the note). Local:

| Symbol | Meaning | Check |
|:--|:--|:--|
| $x_j$, $J$ | values of a discrete $X$ and their number ($J=\infty$ allowed, Problem 3); in §6 the numbers of AM–GM | $j$ an index, never a moment order |
| $x$ | a value of $X$ (the level in (14.7), a median); in §7 a coordinate ($\ln(1+x)$; $x=(R-\mu)/(1+\mu)$) | AUTHORING §6 |
| $h$; $\mathcal I$ | a generic function (LOTUS); in §6 concave or convex; its open interval | LM4's $I$ is now the identity |
| $\xi$ | Taylor's intermediate point | LM3's |
| $t$ | Cantelli's shift, Deep Dive 2 only, declared in its first sentence | the date elsewhere |

Two names: **volatility drag** is LM3's $\bar R-R_G$, in a model $\mu-R_G$ (lm03.md:327); the **Jensen gap** is
$\ln(1+\mu)-g$ in log points, named in §7 with $\mu-R_G=(1+\mu)\big(1-e^{-(\ln(1+\mu)-g)}\big)$. No symbol for
either (LM17 gives the Jensen gap one); every column, readout and figure carries one name. Not used: $P$, plain
$E$, LM4's $m_2,m_3,m_4$ and $m$ for a median ($m$ counts days), $\kappa$, $\gamma$, $\theta$, $q$, $\lambda$, $n$,
$N$, $L$, $B$, $d^2$, $\rho$, $\Sigma$, bold vectors, $A$ or $B$ for events (sets, $\{R\le-3\%\}$, or $\mathcal A$).

**Motivating case: "Two averages, one market."** Box text:

> Over the 23 calendar years 2003–2025 (2003 from its first close, 2 January 2003), the TAIEX total-return index
> (dividends reinvested) returned 14.97% [A14-04] a year on average. An investor who held it throughout earned 12.35%
> [A14-05] a year. The two extreme years show the gap at its widest: 2008's −43.07% and 2009's +83.34% [A14-06] average
> +20.1% [A14-07] a year, yet together the two years returned only +4.4% [A14-08]. Daily returns repeat the pattern on
> a small scale: the average day returned 0.0625% [A14-09], the compound daily rate 0.0552% [A14-10]. Their gap, the
> volatility drag of [[LM3]], is 0.7320 bp [A14-11], within 0.002 bp [A14-12] of half the daily variance, 0.7301 bp
> [A14-13]. Why is the compound rate never above the average? What exactly is the drag? And when does $\sigma^2/2$
> describe it?

X1's note prints the inputs to six decimals of a percent, $\bar R=0.062505\%$, $R_G=0.055185\%$,
$s=1.208364\%$ [A14-14], because the four-decimal rates give only 0.73 bp. Resolved: never above → §6 E9 and §7 (14.12);
exactly → the Jensen gap, E10 and X8; when → (14.13), X7, X8 and the lognormal form.

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | a day's return as a random variable; case + X1; roadmap; notation note; hygiene note | 380 |
| 2 | Random Variables and Their Distributions {1} | E1 + X2 on LM13's $\Omega$; pmf (LM13, two sentences) and density (LM5), one $F_X$; quantile function box and the general median; TR23 under $\hat F$ and the population/sample sentence; E2 + X3; pitfall: a median may be an interval, and $F_X(x)=\tfrac12$ may have no solution | 540 |
| 3 | Expectation and LOTUS {2} | (14.1), existence, $\E[\mathbf 1_{\mathcal A}]=\Pr(\mathcal A)$; (5.9) as the continuous case; no-mean cases (LM5's Cauchy, Problem 3); LOTUS (14.2), grouping proof; linearity (14.3); E3, E4; pitfall: $\E[h(X)]\ne h(\E X)$; 中文導讀 (§2–§3) | 540 |
| 4 | Variance and Higher Moments {3} | (14.4) and (3.7); standardization (5.5); existence nesting ($\lvert x\rvert\le1+x^2$, $x^2\le1+x^4$, $\lvert x\rvert^3\le1+x^4$); (14.5); E5; $\E[Z^4]=3$ by parts, $\Var(Z^2)=2$, (14.6) by expanding powers of $\mu+\sigma Z$; E6 + X4; pitfall: raw third moment against skewness, kurtosis against excess; 中文導讀 | 680 |
| 5 | Tail Bounds: Markov, Chebyshev and Cantelli {4} | (14.7) from $x\mathbf 1\{X\ge x\}\le X$; (14.8) by Markov on $(X-\mu_X)^2$; (14.9) (Deep Dive 2); conditions; every bound holds for $\hat F$ without approximation; E7, E8; X5, X6; pitfall: a bound is not a model; 中文導讀 | 540 |
| 6 | Jensen's Inequality {5} | widget; (14.10), proof from LM4's tangent at $\mu_X\in\mathcal I$ (in $\mathcal I$ because $X\in\mathcal I$ with probability one and $\mathcal I$ is an open interval); strict form (Deep Dive 3); convex form, $\E[X^2]\ge(\E X)^2$, $\E[e^X]\ge e^{\E X}$; (14.11), the strict unweighted case; (1.14); E9; pitfall: direction and non-negative weights; 中文導讀 | 600 |
| 7 | Volatility Drag and the Jensen Gap {6} | (14.12); a normal $R$ breaks its condition; the Jensen gap and the drag; (14.13) from (3.3), second order as (3.8)–(3.9), third as skewness; lognormal: exactly $\sigma_r^2/2$; E10 + X8; X7; $g(f)\le\ln(1+f\mu)$, Jensen gap about $\propto f^2$ (LM17, LM41); pitfall: $\sigma^2/2$ is second order; 中文導讀 | 640 |
| 8 | Random Variables and Expectations in Python {7} | $\hat F$ in NumPy; X9; the counting guard; pitfall: `np.quantile`'s default interpolates; lab box | 240 |
| — | Summary (7 bullets) / Practice Problems (11) / Solutions; References (two books) | | 130 / 340 / 470 |
| | **Total** | | **5,100** |

**Elements.** 10 examples. One knowledge check per numbered section: §2 the die's medians (every $x\in[3,4]$ [A14-15]);
§3 a ±10% day: $\E R=0$, $\E\ln(1+R)=\tfrac12\ln0.99=-0.5025\%$ [A14-16]; §4 TR23 at $f=2$: standard deviation 2.417%,
$\E[(2R)^2]=4\E[R^2]=5.856\times10^{-4}$ [A14-17] (2.417, not 2.4167: $2\times1.2084=2.4168$); §5 Chebyshev at $k=1$
says nothing; at $k=2$, 25% two-sided against Cantelli's 20% one-sided, TR23 319 and 188 days [A14-18]; §6 apply (14.10)
to the convex $h(x)=x^2$: $\E[X^2]\ge(\E X)^2$, the gap is $\Var X$; §7 TR23 at $f=2$: Jensen gap 2.936 bp against
$4\times0.7316$ [A14-19] $=2.926$ [A14-20]; §8 which call returns $\hat F^{-1}(0.001)$: −6.313% (`inverted_cdf`) or
−5.866% (the default) [A14-21]. 中文導讀 after §3 (隨機變數, 機率質量函數, 累積分布函數, 分位數函數, 中位數, 經驗分布, 期望值, 母體,
樣本平均數; LOTUS in English), §4 (動差, 標準化動差 (standardized moment), 偏態, 峰態, 超額峰態), §5 (指示函數, 馬可夫不等式,
謝比雪夫不等式, Cantelli 不等式), §6 (凹函數, 凸函數, Jensen 不等式, 算幾不等式), §7 (波動拖累; Jensen 差距 (Jensen gap), the book's
own form). Deep Dives: (1) LOTUS by grouping; (2) Cantelli, opening "Here $t>0$ is a
shift, not a date": $\{X-\mu_X\le-k\sigma_X\}\subseteq\{(\mu_X-X+t)^2\ge(k\sigma_X+t)^2\}$, Markov gives
$(\sigma_X^2+t^2)/(k\sigma_X+t)^2$, smallest at $t=\sigma_X/k$; the law $\mu_X-k\sigma_X$ with probability $1/(1+k^2)$
and $\mu_X+\sigma_X/k$ otherwise attains it (Chebyshev's attaining law, $\mu_X\pm k\sigma_X$ with probability
$1/(2k^2)$ each and $\mu_X$ otherwise, $k\ge1$, in one sentence); (3) the strict tangent inequality
$h(x)<h(\mu)+h'(\mu)(x-\mu)$ for $x\ne\mu$ from strict concavity at the midpoint, and the equality case of (14.10).

**Exhibits.**

- X1 `bar` §1 {#case}: TR23 calendar-year returns 2003–2025 (23 bars), `hline`s at 14.97% ("arithmetic mean") and 12.35%
  ("compound rate"); y `pct0`, tooltip `pct2`; 2008 and 2009 named in the note. Note: 2003 from its
  first close (2 January 2003); 2026 excluded (partial); the daily inputs to six decimals (case). Source: FinMind
  `TaiwanStockTotalReturnIndex` (data_id TAIEX), retrieved 18 October 2026; dividends reinvested, no costs.
- X2 table §2 {#omega}: LM13's $\Omega=\{++,+-,-+,--\}$: $\Pr(\omega)=\tfrac14$, $X(\omega)$, $\tfrac12\ln X(\omega)$
  (four decimals of a percent); below, $x$, $p_X(x)$, $F_X(x)$ for 0.5625, 1.125, 2.25 [A14-22]. Exact.
- X3 table §2 {#quantiles}: for $u=0.001,0.01,0.05,0.25,0.5,0.75,0.95,0.99,0.999$: $j=\lceil uT\rceil$,
  $\hat F^{-1}(u)=R_{(j)}$ and `np.quantile`'s default, three decimals of a percent [A14-21]. Note: the default
  interpolates; the two agree at the quartiles (here $(T-1)u$ is a whole number) and differ most in the far tails.
- X4 table §4 {#moments}: TR23 against $\mathcal N(\bar R,s^2)$: $\mu$, $\sigma$, $\E[R^2]$, $\E[R^3]$, $\E[R^4]$, Skew
  (three decimals), Kurt and excess kurtosis (two decimals), ratio of $\E[R^4]$. Raw moments in scientific notation,
  four significant figures; a row checks (3.7): $1.464\times10^{-4}=1.460\times10^{-4}+3.907\times10^{-7}$ [A14-23]
  (adds up at four figures; five, 1.4641 against 1.4601 + 0.0039, would not). Note: divisor-$T$ moments; 0050's
  8.12 [A14-24] ([[LM4]], [[LM5]]) is another sample's excess kurtosis.
- X5 `line` §5 {#bounds}, log y (0.5 to 6,000 days): x = $k$ from 1 to 8.5 (`n1`); Cantelli bound $T/(1+k^2)$ (2,924.5
  at $k=1$, 344.1 at $k=4$, 90.0 at $k=8$ [A14-25]) and TR23's days with $R\le\bar R-ks$ (a step line from the sorted
  $z$ values, ending at $k=8.08$, 7 April 2025, −9.6997%); `point` at $k=4$ (17 [A14-26] against 344.1). No normal
  series. Note: the 7% limit to 29 May 2015, 10% from 1 June 2015; 7 April 2025 was capped for many stocks.
- X6 table §5 {#boundtable}: $k=1,\dots,6$: TR23 days with $\lvert R-\bar R\rvert\ge ks$ (count, share) and $1/k^2$;
  days with $R-\bar R\le-ks$ (count, share) and $1/(1+k^2)$ [A14-18]. Shares to two decimals of a percent. No normal
  columns (LM15).
- X7 `scatter` §7 {#dragyears}: one point per calendar year 2003–2025 from that year's daily returns: x = half their
  variance (divisor: the year's count), y = their volatility drag, mean minus compound rate (bp); 45° line with
  `extend`; labels on 2008 (2.25 bp) and 2017 (0.14 bp); `n2`. Note: every point within 0.0097 bp (2024) of the line,
  at most 1.13% relative to half the variance [A14-27]; 2003 from its first close (2 January 2003).
- X8 table §7 {#dragtable}: rows TR23 daily (bp); TR23 years 2003–2025 (2003 from its first close, 2 January 2003);
  2008 and 2009 with equal probability (printed returns); +100%/−50% ([[LM3]]) (percentage or log points, in the
  headers). Columns $\mu$, $\sigma$, drag $\mu-R_G$, $\sigma^2/2$, Jensen gap $\ln(1+\mu)-g$, $\sigma^2/(2(1+\mu)^2)$,
  (14.13) through the fourth order. Values: daily 0.0625%, 1.2084%, 0.7320, 0.7301, 0.7316, 0.7292, 0.7316 [A14-28];
  annual 14.97%, 23.70% [A14-29], 2.62, 2.81, 2.31, 2.12, 2.30 [A14-30]; pair 20.1%, 63.2%, 17.97, 19.97, 16.20,
  13.84, 15.76 [A14-31]; +100%/−50% 25%, 75%, 25.00, 28.125, 22.31, 18.00, 21.24 [A14-32] (28.125 exact: two decimals
  would sit on a tie).
- X9 table §8 {#python}: call | returns | pass, for `np.mean`; `np.var`, `np.std` (divisor $T$); `np.quantile`
  (`"linear"` default interpolates; `"inverted_cdf"` is $\hat F^{-1}$); `np.median` (averages the middle pair);
  `stats.rv_discrete(values=(xk, pk))`, integer `xk` (the die's `.median()`, `.ppf(0.5)`: 3); `stats.skew`,
  `stats.kurtosis` (excess; `bias=True`); `stats.norm(loc, scale).moment(n)` (raw), `.expect` (`np.log1p` gives
  `nan`).

**Widget `jensen` — "Jensen's chord on a two-point return".** `Book.controls`: preset select ("TAIEX 2008 and 2009",
initial; "+2%/−1% bet at 25× [A14-33] ([[LM4]])", $b=50\%$, $a=25\%$; "+100%/−50% ([[LM3]])"); sliders $b\in[0,100\%]$
and $a\in[0,90\%]$ (step 0.01%), $p\in[0.05,0.95]$ (step 0.01). `line` chart, x from −90% to +100% (`pct0`): the curve
$\ln(1+x)$ (about 200 points), the chord from $(-a,\ln(1-a))$ to $(b,\ln(1+b))$ (dashed), `point`s at $(\mu,g)$
("average of the logs") and $(\mu,\ln(1+\mu))$ ("log of the average"), `vline` at $\mu$. Readouts: $\mu$, $\sigma$
(`pct1`); $g$, $\ln(1+\mu)$ (`pct3`, so the 25× preset shows E3's values); $R_G$, (3.9)'s $\mu-\sigma^2/2$
(`pct2`); Jensen gap, drag, $\sigma^2/2$, $\sigma^2/(2(1+\mu)^2)$ (points). Initial state (the PDF), $b=83.34\%$,
$a=43.07\%$, $p=0.5$, stored as printed: $\mu$ 20.1%, $\sigma$ 63.2%, $g$ 2.141%, $R_G$ 2.16%, $\ln(1+\mu)$ 18.345%,
Jensen gap 16.20, drag 17.97, $\sigma^2/2$ 19.97,
second-order 13.84, (3.9) 0.16% (all [A14-31]; $\mu$, $\sigma$ one decimal: ties). The 25× preset shows
$g=5.889\%$ [A14-34] against $\ln1.125=11.778\%$ [A14-35] (E3). No random numbers.

**Examples.**

- E1 §2 {#twotrades} One random variable, LM13's (E10): two trades of the bet at $f=25$,
  $X=W_2/W_0\in \{0.5625,1.125,2.25\}$ with $p_X=(\tfrac14,\tfrac12,\tfrac14)$. $F_X$ jumps from $\tfrac14$ to
  $\tfrac34$ at 1.125, so $F_X(x)=\tfrac12$ has no solution, yet 1.125 is the unique median
  ($\Pr(X\le1.125)=\Pr(X\ge1.125)=\tfrac34$); $F_X^{-1}(0.1)=0.5625$ [A14-36]. X2. Exact.
- E2 §2 {#empirical} TAIEX as a random variable: under $\hat F$, $\hat F(0)=2{,}644/5{,}849=0.4520$ [A14-37] (LM13's
  value; no day is exactly 0), so 3,205 days rose (54.8%) [A14-38]; $T$ is odd, so the median is the 2,925th return,
  0.0879% [A14-39], above the mean 0.0625%: 3,020 days (51.6%) [A14-40] beat the mean. The lower tail reaches further:
  $\hat F^{-1}(0.01)=-3.567\%$ against $\hat F^{-1}(0.99)=3.125\%$, $\hat F^{-1}(0.001)=-6.313\%$ against
  $\hat F^{-1}(0.999)=5.823\%$ [A14-21] (X3).
- E3 §3 {#lotus} Expectation two ways, on E1's $X$: $\sum_\omega X(\omega)\Pr(\omega)=\sum_xx\,p_X(x)=1.265625=1.125^2$
  [A14-41], the product of the two trades' expectations (the [[LM16]] sentence). LOTUS with $h(x)=\tfrac12\ln x$:
  $\tfrac14(40.5465\%)+\tfrac12(5.8892\%)+\tfrac14(-28.7682\%)$ [A14-42] $=\tfrac12\ln1.125=5.889\%$ [A14-34], LM4's
  $g^*$ again (LM13's promise), against $\tfrac12\ln\E[X]=\ln1.125=11.778\%$ [A14-35]: the log of the average is twice
  the average of the logs here. Four decimals: LM13's 40.55%, 5.889%, −28.77% give 5.8895, a tie.
- E4 §3 {#growth} The growth function as an expectation: (4.7) is LOTUS for $R\in\{b,-a\}$; (4.4) is LOTUS under
  $\hat F$, $\bar g(f)=\E_{\hat F}[\ln(1+fR)]$, and $\bar g(1)=\bar r=5.5170$ bp a day [A14-43]; $A\bar r=13.58\%$ a
  year [A14-44] $=\ln(25.2007)/23.7645$ [A14-45] by (1.12), the realized log growth over the whole sample, 2026
  included, unlike the case's calendar years: a compound rate of $25.2007^{1/23.7645}-1=14.54\%$ [A14-44].
- E5 §4 {#betmoments} The +2%/−1% bet: $\mu=0.5\%$, $\sigma=1.5\%$, $\E[R^2]=0.00025=\sigma^2+\mu^2$,
  $\E[R^3]=3.5\times10^{-6}=\mu^3+3\mu\sigma^2$ (lm04.md:718), Skew 0, Kurt 1 (excess −2) [A14-46]: a positive raw third
  moment with zero skewness. Exact.
- E6 §4 {#trmoments} TAIEX against the normal (X4): Skew −0.34 (−0.338 [A14-47]), Kurt 8.27, excess 5.27 [A14-48];
  $\E[R^3]=-3.231\times10^{-7}$ [A14-49] against the normal's $+2.740\times10^{-7}$ [A14-50];
  $\E[R^4]=1.751\times10^{-7}$ [A14-51], 2.72 [A14-52] times the normal's $6.430\times10^{-8}$ [A14-53] (LM4: 3.7 for
  0050 [A14-24]). LM4's approximations drop terms of order $(\bar R/s)^2=0.0027$: exactly $(\bar R/s)^2/3$ of
  $3\mu\sigma^2$, under 0.1%, and $2(\bar R/s)^2+(\bar R/s)^4/3$ of $3\sigma^4$, about 0.5% (the printed moments give
  0.07% and 0.53%) [A14-54]; $3\mu\sigma^2=2.738\times10^{-7}$, $3\sigma^4=6.396\times10^{-8}$ [A14-55]. The normal's
  moments use the six-decimal $\bar R$ and $s$ of the case note (four decimals give 6.431 and 6.397).
- E7 §5 {#threepct} Three bounds for a 3% day: Markov on $\lvert R\rvert$, $\E\lvert R\rvert=0.8402\%$ [A14-56]: 28.0%
  [A14-57]; Markov on $R^2$, $\E[R^2]=1.464\times10^{-4}$: 16.27% [A14-58]; actual $\lvert R\rvert\ge3\%$: 175 days,
  2.99% [A14-59]. One-sided: Cantelli at $k=(0.0625+3)/1.2084=2.534$: 13.47% [A14-60]; actual $R\le-3\%$: 108 days,
  1.85% [A14-61] (LM13's count). Printed inputs reproduce every bound.
- E8 §5 {#foursigma} LM5's Practice Problem 9 on TAIEX: Cantelli $1/17=5.88\%$ [A14-62]; normal
  $\Phi(-4)=3.17\times10^{-5}$ [A14-63], 0.185 expected days [A14-64]; TAIEX: 17 days [A14-26] at or below
  $\bar R-4s=-4.771\%$ [A14-65] (0.29%), 92 times the expected count and a twentieth of the bound [A14-66] (descriptive ratios, not a test). Two-sided:
  30 days (0.51%), Chebyshev 6.25% [A14-67], normal 0.37 days.
- E9 §6 {#amgm} (14.11) with $w_j=1/23$ and $x_j$ X1's 23 growth factors: $1.1497\ge1.1235$ [A14-68] (case question 1);
  the pair: $\tfrac12(0.5693+1.8334)=1.20135\ge\sqrt{0.5693\times1.8334}=1.02164$ [A14-69]. Then (1.14) as LM1 derived
  it.
- E10 §7 {#dragexact} The Jensen gap and the drag, exactly (X8): daily Jensen gap $\ln(1+\bar R)-\bar r=0.7316$ bp
  [A14-19] $=0.7292+0.0020+0.0004$ [A14-28] (second-, third-, fourth-order; negative skewness adds); drag
  $\bar R-R_G=(1+\bar R)(1-e^{-0.7316\text{ bp}})= 0.7320$ bp. Annual: Jensen gap 2.31 log points against 2.12 at
  second order and 2.30 through the fourth; drag 2.62 points against $\sigma^2/2=2.81$. The pair: Jensen gap 16.20
  against 13.84 and 15.76; drag 17.97 against 19.97. Lognormal form: TAIEX's $s_r^2/2=0.7329$ bp ($s_r=1.2107\%$)
  [A14-70] against the Jensen gap 0.7316 bp. Unrounded inputs except the pair.

**Problems plan** (11; MC keys 1 A, 3 C, 7 B, 9 C; Python: 11; the lab repeats 2, 4, 6, 10, 11). Every stem states its
law or sample, the divisor, the rounding, the quantile rule where a quantile is asked ($R_{(\lceil uT\rceil)}$,
`method="inverted_cdf"`; a median by §2's definition) and, for bets, independence and the probabilities.

1. MC (§2). Four days of the +2%/−1% bet: $G$ takes 0.960596, 0.989705, 1.019696, 1.050596, 1.082432 with probabilities
   $\tfrac1{16},\tfrac4{16},\tfrac6{16},\tfrac4{16},\tfrac1{16}$ [A14-71]. **A.** "Its only median is 1.019696, below
   its mean 1.020151"; B. "Every value from 0.989705 to 1.019696 is a median" ($F_G=\tfrac5{16}$ there, not
   $\tfrac12$); C. "Its median is its mean, 1.020151" (then $\Pr(G\ge1.020151)=\tfrac5{16}$).
2. (§2–§3) Same $G$: tabulate $F_G$; $\E[G]=1.02015=1.005^4$; $\E[\ln G]=4\times0.487615\%=1.95046\%$ by linearity;
   $\ln\E[G]=1.99502\%$; Jensen gap 4.456 bp [A14-72]; explain the sign. Six significant figures.
3. MC (§3). Which has a finite expectation? A. a payoff $2^j$ with probability $2^{-j}$, $j=1,2,\dots$ (the terms are
   all 1); B. LM5's Cauchy (no mean); **C.** the Pareto density $1.5x^{-2.5}$, $x\ge1$ (mean $1.5/0.5=3$ [A14-73]).
4. (§4) LM4's trade: +1% with probability 0.9, −5% otherwise: $\mu=0.4\%$, $\sigma=1.8\%$, $\E[R^2]=3.4\times10^{-4}$,
   $\E[R^3]=-1.16\times10^{-5}$, Skew $=-8/3=-2.67$, Kurt $=73/9=8.11$ (excess 5.11); at $f=8$, $\mu=3.2\%$,
   $\sigma=14.4\%$ [A14-74] and the same Skew and Kurt. Why do they not change, and what does an excess kurtosis near
   TAIEX's say about a two-point law? Exact fractions.
5. (§4) Show $\E[Z^6]=15$ by parts and $\Var(Z^3)=15$; for $X\sim\mathcal N(0.05,0.20^2)$ (illustrative) give
   $\E[X^3]=0.006125$ and $\E[X^4]=0.00540625$ [A14-75] from (14.6) and check with `stats.norm(0.05, 0.2).moment(3)`.
   Exact (five figures would tie).
6. (§5) With TR23's printed $\bar R=0.0625\%$ and $s=1.2084\%$ (divisor $T$), bound the share of days at or below −5%:
   $k=4.1894$, Cantelli 5.39%, Chebyshev 5.70%; actual 15 days (LM13's count), 0.26% [A14-76]. Which bound is tighter,
   and why must both hold for $\hat F$?
7. MC (§5). Pareto $1.5x^{-2.5}$, $x\ge1$: Chebyshev's bound on $\Pr(\lvert X-\mu_X\rvert\ge3\sigma_X)$ is A. 11.1%
   ($1/k^2$ without its condition); **B.** none: the variance is infinite; C. 10%, Cantelli's $1/(1+3^2)$ (it needs a
   finite variance too, and bounds one tail) [A14-77].
8. (§6) Prove (14.11) from (14.10), saying where each condition enters; show where the proof fails for LM1's weights
   $(1.5,-0.5)$ and confirm $\ln(1.5e^{0.10}-0.5e^{0.20})=0.0460<0.0500$ [A14-78]. Four decimals.
9. MC (§6). Which holds for every positive $X$ with finite expectations? Check on Problem 4's trade at its Kelly
   exposure, $X=1+8R\in\{1.08,0.60\}$ (four decimals). A. $\E[\ln X]\ge\ln\E[X]$ (1.82% against 3.15%); B.
   $\E[1/X]\le1/\E[X]$ ($1/x$ is convex: 1, by LM4's $\E[R/(1+fR)]=0$, against 0.9690); **C.**
   $\E[\sqrt X]\le\sqrt{\E X}$ (1.0128 against 1.0159) [A14-79].
10. (§7) TR23's calendar years (2003 from its first close) with printed $\mu=14.97\%$, $\sigma=23.70\%$ (divisor 23),
    Skew 0.19, Kurt 5.02 [A14-29]: (a) (3.9) gives 12.16%; (b) (14.13) through the fourth order:
    $2.1247-0.0555+0.2266=2.2958$ log points, $R_G=12.36\%$ [A14-80]; (c) the actual 12.35% [A14-05]: which term
    matters most, and why? Two decimals of a percent; four for the terms.
11. *(Python)* With the lab's TR23: (a) $T$, $A$, $\bar R$, $s$ and (3.7); (b) $\hat F^{-1}(0.001)$ as
    $R_{(\lceil uT\rceil)}$ (`method="inverted_cdf"`) and by `np.quantile`'s default; (c) X6's counts at $k=2,3,4$
    with the guard (319, 99, 30; 188, 61, 17); (d) the Jensen gap $\ln(1+\bar R)-\bar r$ and its three terms.

**Lab parts** (`build/make_lab14.py`; `taiex_tr.csv` only): 1 data: returns, $T$, $A$, the guard, the `Fraction`
recount (108); 2 distributions: the die (`rv_discrete`), E1's $X$ and the four-day bet by hand, $\hat F$ as a step plot,
X3 both ways; 3 expectation: E3, E4, $\bar g(f)$ on a grid against $\ln(1+f\bar R)$; 4
moments: (3.7) as (14.4), X4, `stats.skew`/`kurtosis` against the formulas, `norm.moment` and `norm.expect`; 5 bounds:
X5, X6, E7, E8, the attaining two-point laws; 6 Jensen: the chord for any two-point law, E9; 7 drag and Jensen gap:
X7, X8, the series term by term, $f=2$; 8 problems 2, 4, 6, 10, 11. Extension (stability check, no conclusions): the
drag, the Jensen gap's terms and the $k=4$ counts in each limit regime ($T=3{,}077$ to 29 May 2015, $T=2{,}772$ from
1 June 2015 [A14-81]), each with its own $\bar R$ and $s$; each regime's excess kurtosis cited from LM15.

**Cross-module tags** (users: briefs citing the tag).

- (14.1) $\E[X]=\sum_jx_jp_X(x_j)$ when $\sum_j\lvert x_j\rvert p_X(x_j)<\infty$ ($J$ finite or infinite);
  $\E[\mathbf 1_{\mathcal A}]=\Pr(\mathcal A)$ for an event $\mathcal A$ (LM15, LM16, LM17, LM18).
- (14.2) LOTUS $\E[h(X)]=\sum_jh(x_j)p_X(x_j)$ when $\sum_j\lvert h(x_j)\rvert p_X(x_j)<\infty$; (5.9) is its continuous
  form (LM15, LM16, LM18).
- (14.3) $\E[\eta X+\zeta]=\eta\E[X]+\zeta$; $\E[X+Y]=\E[X]+\E[Y]$ on a common $\Omega$ when both exist, proved on a
  countable $\Omega$, stated without proof for densities (LM16, LM17, LM18).
- (14.4) $\E[X^2]=\sigma_X^2+\mu_X^2$, $\Var(\eta X+\zeta)=\eta^2\Var(X)$, for $\E[X^2]<\infty$ (LM15, LM16, LM17,
  LM18).
- (14.5) $\operatorname{Skew}(X)=\E[(X-\mu_X)^3]/\sigma_X^3$, $\operatorname{Kurt}(X)=\E[(X-\mu_X)^4]/\sigma_X^4$, for
  $\E[X^4]<\infty$ (Skew: $\E\lvert X\rvert^3<\infty$) and $\sigma_X>0$ (LM15, LM17).
- (14.6) $\E[Z^3]=0$, $\E[Z^4]=3$, $\Var(Z^2)=2$; for $\mathcal N(\mu,\sigma^2)$, $\E[X^3]=\mu^3+3\mu\sigma^2$,
  $\E[X^4]=\mu^4+6\mu^2\sigma^2+3\sigma^4$ (LM15, LM16, LM17, LM18).
- (14.7) $\Pr(X\ge x)\le\E[X]/x$ for $X\ge0$, $x>0$ (none yet).
- (14.8) $\Pr(\lvert X-\mu_X\rvert\ge k\sigma_X)\le1/k^2$ for finite variance, $\sigma_X>0$, $k>0$ (LM17).
- (14.9) $\Pr(X-\mu_X\le-k\sigma_X)\le1/(1+k^2)$, same conditions, $k\ge0$ (LM15; LM5's pointer).
- (14.10) $\E[h(X)]\le h(\E X)$ for $h$ concave and differentiable on an open $\mathcal I$ with $\Pr(X\in\mathcal I)=1$,
  $\E\lvert X\rvert$ and $\E\lvert h(X)\rvert$ finite; strict when $h$ is strictly concave and $\Pr(X\ne\mu_X)>0$;
  reversed for convex $h$ (LM17).
- (14.11) $\sum_jw_jx_j\ge\prod_jx_j^{w_j}$ for $x_j>0$, $w_j\ge0$, $\sum_jw_j=1$, equality iff all $x_j$ with $w_j>0$
  are equal (LM1's pointer).
- (14.12) $g\le\ln(1+\mu)$, so $R_G\le\mu$, for $R>-1$ with probability one and finite $\E\lvert R\rvert$,
  $\E\lvert\ln(1+R)\rvert$; equality iff $\Pr(R=\mu)=1$ (LM17).
- (14.13) the Jensen gap
  $\ln(1+\mu)-g=\dfrac{\sigma^2}{2(1+\mu)^2}-\dfrac{\E[(R-\mu)^3]}{3(1+\mu)^3}+\dfrac{\E[(R-\mu)^4]}{4(1+\mu)^4}-\cdots$
  for $R$ with finitely many values, each with $\lvert R-\mu\rvert<1+\mu$; the third term is
  $-\operatorname{Skew}\cdot\sigma^3/(3(1+\mu)^3)$ (none yet).

**Pitfalls to pre-empt.**

- Jensen and AM–GM: the conditions of (14.10) and (14.11); only the differentiable case (it covers every $h$ in the
  book); negative weights are not probabilities.
- Logs need $R>-1$ with probability one: a normal $R$ puts mass below −1, so $\E[\ln(1+R)]$ does not exist under it
  (SciPy returns `nan`); (4.2) hides this; a lognormal model does not.
- Bounds: conditions as (14.7)–(14.9); Chebyshev is empty for $k\le1$; the normal appears only at $k=4$.
- Which gap, which variance: the drag $\mu-R_G$ against the Jensen gap $\ln(1+\mu)-g$ (log points); (14.13) and (3.9)
  use $\sigma^2$ of $R$, the lognormal form $\sigma_r^2$ of $r$ (0.7329 against 0.7301 bp).
- $\E[h(X)]\ne h(\E X)$: never $g=\ln(1+\bar R)$; never (3.9) at annual frequency (12.16% from printed inputs, 12.17%
  unrounded, against 12.35%) or for the pair (about 2 points off).
- A raw third moment is not skewness (E5). Kurt is not excess kurtosis: print "excess" whenever a number meets LM4,
  LM5 or LM15 (0050's 8.12 is excess).
- Data: the guard on every count; round thresholds tie exactly (−3%: guard and `Fraction` both give 108); $A=246.12$,
  never LM5's 243.1 [A14-82].
- Rounding: the pair's $\mu$ and $\sigma$ are two-decimal ties (one decimal); its row uses the printed returns
  (unrounded: $\sigma^2/2=19.98$, $R_G=2.17\%$, $\ln(1+\mu)=18.35\%$ [A14-83]); 28.125 printed exact.

**References.** Grinstead and Snell (1997), *Introduction to Probability*, 2nd rev. ed., AMS: §6.3, Theorems 6.10
(linearity) and 6.11 (LOTUS) for densities; theorem numbers from the free CHANCE edition, never pages (SOURCES). Simon
and Blume (1994), *Mathematics for Economists*, Norton, chapter 21 (the $h''$ test, as LM4 cites it).

**Stage 4 for earlier modules.** lm01.md:6 leads `[2, 3, 5, 6, 8, 19, 38]` gain 14; lm04.md:6 leads
`[6, 7, 12, 20, 41, 42]` gain 14. lm03.md:6 and lm05.md:6 already list 14. (lm05.md:60's retargeting and LM5's 分布
strings are in plans/vol-3.md, "Stage 4 changes".)

## LM15 Distributions in Finance

**Prereq:** LM1, 2, 3, 5, 13, 14. LM4 is named only for the normal's 2.5% point it used without proof (lm04.md:541), which (15.6) explains.

- LM1: (1.6) $(1+x/n)^n\to e^x$ (lm01.md:242), for the Poisson limit and $t_\nu\to\mathcal N(0,1)$; the binomial theorem and $n(n-1)\cdots(n-j+1)/n^j\to1$ (Deep Dive on $e$, lm01.md:264–271).
- LM2: the chain rule (2.5) (lm02.md:274), in Deep Dive 2.
- LM3: (3.2) $e^x=\sum_{j\ge0}x^j/j!$ (lm03.md:118), for the Poisson total, mean and variance.
- LM5: $\varphi$, $\Phi$, $\Phi(-z)=1-\Phi(z)$ (lm05.md:321); (5.4)–(5.7), (5.9), (5.11), (5.12); the normal fitted by its mean and standard deviation (lm05.md:327); the Pareto tail index $\alpha$, the tails exhibit, its kurtosis convention, the literature (lm05.md:331–350); the kurtosis pitfall (lm05.md:366–369); the scaled $t_3$ (lm05.md:486, 497; lm05.js:18, 41).
- LM13: (13.3), (13.7), (13.11), (13.12), (13.13): frequencies on a sample, independent trials, $F_X$, $\hat F$, independence of $n$ discrete random variables and iid; random variables as functions; pmf; TR23's sign frequencies; TR23's counts, 108 at −3% and 15 at −5% (cited).
- LM14: (14.1) as $\E[\mathbf 1\{\cdot\}]=\Pr(\cdot)$; LOTUS (14.2); (14.4); (14.5) and TR23's full-sample values, cited; $\E Z^4=3$ (14.6); $\hat F^{-1}(u)=R_{(\lceil uT\rceil)}$ (`method="inverted_cdf"`); the Chebyshev bound and Cantelli's (14.9); TR23's calendar-year returns.

**Leads:** LM16, 17, 18, 19, 20, 21, 26, 32, 38, 39 (tags and [[LMn]] pointers). ROADMAP gives LM39 its jumps.

**Forward links honoured.**

| Source | Promise | Kept in |
|:--|:--|:--|
| lm05.md:369 | "prefer tail measures that need fewer moments ([[LM15]], [[LM32]])" | §7, E9, E10, X9: counts, quantiles, chords; TR23's kurtosis per regime, around 7 April 2025, removals, top-ten shares; 0050's values cited; the running kurtosis (lm05.md:366–368) is [[LM17]]'s |
| lm05.md:497; :449 | "[[LM15]] fits tail models and [[LM20]] estimates $\nu$"; the normal fit is "the maximum-likelihood choice" | §6: two fits, `t.fit` named once ([[LM20]]); §8: `norm.fit` returns $\bar R$, $s$ |
| lm05.md:532; plans/vol-1.md:92 | 尾端需要自己的模型（LM15） | §6–§7; §6's 中文導讀 |
| lm05.md:335, 338, 342, 348, 486; lm05.js:18, 41; reviews/lm05.md A10 | $t$ density "up to a constant"; kurtosis $3+6/(\nu-4)$ unproved; infinite for $2<\nu\le4$, undefined for $\nu\le2$; $t_3$ scaled by $\sqrt{(\nu-2)/\nu}$ | (15.9)–(15.11), Deep Dive 2; E7 supplies LM5's missing constant and recovers its widget's $t_3$ density |
| lm05.md:511–523; :529; :60 | (5.12); tail days cluster ([[LM26]]); $X$ generic, $Z$ standard normal | §5; §3; Notation |
| lm04.md:541 | the normal's 2.5% point, unproved | §4: (15.6), E4 |

**Outcomes.**

1. calculate binomial probabilities, means and variances, and compare the binomial with up days in blocks of sessions
2. derive the Poisson distribution as the limit of rare binomial trials, and recognize overdispersion in counts of large moves
3. calculate normal quantiles with $\Phi^{-1}$, and read a QQ plot of returns against a fitted normal
4. derive the density, median, mean and variance of a lognormal growth factor, and fit one to annual growth factors
5. state the Student-t density, variance and kurtosis with their conditions, and fit a Student-t by matching kurtosis and by maximum likelihood
6. compare tail models through exceedance counts and quantiles, and read a tail index from log–log chords
7. choose a distribution for a stated question and name the assumption that limits it
8. implement the fits and counts with `scipy.stats` and the counting guard

**Owns.** Bernoulli and binomial ((15.1) by counting sequences of independent trials; (15.2) by the binomial theorem); up days in 20-session blocks. Poisson ((15.3); (15.4) by (1.6); (15.5) by (3.2)) and its failure on monthly counts of large moves. $\Phi^{-1}$, (15.6), TR23's quantiles against the normal's, QQ plots. Lognormal (15.7), fitted to the 23 calendar-year factors. $\Gamma$ (15.8). Student-t: (15.9), Cauchy and normal limits, (15.10) with LM5's convention, (15.11); fits by (15.12) and `t.fit`. Tail measures needing fewer moments: counts against models, quantiles, chords (15.13). The fragility of TR23's kurtosis: per regime, around 7 April 2025, the removals, the top-ten shares. Choosing a model (X10).

**Leaves.** TR23's full-sample moments and bound tables → LM14 (cited); the running sample kurtosis → LM17. Maximum likelihood, estimating $\nu$, the Hill estimator, standard errors → LM20. Tests → LM21. Sample skewness and kurtosis as statistics, the $\sqrt T$ rule → LM19. Volatility models → LM26. Value at risk, expected shortfall → LM32. Jumps → LM39. Inverse-transform draws; the fitted $t$ in its lab → LM18. Variance of a sum, total variance → LM16. Normal approximation, CLT, the iid daily year → LM17. Geometric Brownian motion → LM38. Extreme value theory: not in the book.

**Uses before taught.**

- Maximum likelihood (§6, once): "SciPy's `t.fit` picks the parameters that give the returns the largest joint density, the likelihood: maximum likelihood, which [[LM20]] develops."
- Variance of a sum (§2): "[[LM16]] reaches this variance in one line, adding the variances of independent indicators."
- Central limit theorem (§2): "[[LM17]] shows why a sum of many independent trials is close to normal." (§5): "[[LM17]] explains why a product of many independent factors is close to lognormal; [[LM38]] builds lognormal prices."
- Tests (§2 pitfall): "[[LM21]] tests whether a gap between observed and expected counts exceeds chance."
- Law of total variance (§3, E3): "[[LM16]]'s law of total variance handles months of unequal length."
- Clustering (§3, the one LM26 pointer): "Calm and turbulent months alternate because volatility changes over time; [[LM26]] models it."
- Jumps (§3): "[[LM39]] uses Poisson counts for price jumps."
- Value at risk (§4): "With its sign reversed, the 1% quantile of a daily return is the one-day value at risk at 99% ([[LM32]])."
- Asymmetry (§7): "Large falls outnumber large rises, 108 against 67 [A15-01]; [[LM14]] computed TR23's skewness, −0.34 [A15-02]; [[LM19]] studies it as a statistic."
- Inverse transform (§8): "[[LM18]] draws from these laws."
- EVT (no pointer): "Extreme value theory models the largest losses directly; it is beyond this book."

**Data role.** TR23 only: `data/processed/vol3_taiex.parquet` (column `R`), built and checked by `data/vol3_series.py` (FinMind `TaiwanStockTotalReturnIndex`, TAIEX, retrieved 2026-10-18). $T=5{,}849$ simple daily total returns, 3 January 2003 – 8 October 2026 (5,850 closes) [A15-03]; 8,680 calendar days, 23.7645 years, $A=246.12$ [A15-04]; divisor $T$. Illustrated: 292 blocks of 20 sessions from 3 January 2003, the last 9 returns (24 September – 8 October 2026) left out [A15-05]; 286 calendar months, January 2003 with 18 sessions, October 2026 with 6 [A15-06]; the 23 calendar-year factors 2003–2025, 2003 from its first close (2 January 2003); the limit regimes, 3 January 2003 – 29 May 2015 (3,077 returns, 7%) and 1 June 2015 – 8 October 2026 (2,772, 10%) [A15-07]. 7 April 2025, −9.6997%, is the worst day, capped by the limit for many stocks; the best is 10 April 2025, +9.2512% [A15-08]. No U28, no 0050 recomputation, no simulation, no seed. Scripts: `data/lm15_numbers.py` (asserts every printed value, `Fraction` recounts, the fit from four starts) and `data/lm15_charts.py`. Lab data: `taiex_tr.csv`.

**Hygiene declaration.** *Descriptive:* counts, empirical quantiles, annual returns, chords, 7 April 2025. *In-sample:* every fitted distribution and what it implies (expected counts, model quantiles, tail means, X10). *Stability check:* X9, overdispersion by regime. *Model statements:* the Poisson limit (E2), LM17's one-year probability. Nothing out-of-sample. Local note: "Every frequency here describes TAIEX total returns, 3 January 2003 – 8 October 2026. Every fitted distribution is in-sample, so a good fit is no evidence for later data. The 7% and 10% regimes are a stability check; [[LM20]] and [[LM21]] add standard errors and tests."

**Notation.** Book-wide, with their §6 meaning: $R$, $R_t$, $r$, $T$, $t$, $A$, $G$, $\varphi$, $\Phi$, $\Pr$, $\E$, $\Var$, $\operatorname{Skew}$, $\operatorname{Kurt}$; $\mu$, $\sigma$ (a model's mean and standard deviation of $R$); $\bar R$, $s$, $\bar r$, $s_r$ (divisor $T$); $p$ (a trial's success probability; no bet); $\nu$; $\lambda$; $n$ (trials); $j$, $R_{(j)}$; $u$; $z$ (LM5's standardized value: X6's $(-x-\bar R)/s$, the widget, Deep Dive 2); $p_X$, $f_X$, $F_X$, $F_X^{-1}$ ($F_R$, $F_G$ a model's law), $\hat F$, $\hat F^{-1}$ (TR23's empirical law); $\mathcal N(\mu,\sigma^2)$, $t_\nu$, $\operatorname{Bin}(n,p)$, $\operatorname{Poisson}(\lambda)$, $\sim$, iid; $m$ (sessions in LM17's one-year model, E6 only). "Student-t" with LM5's hyphen; $t_\nu$ in formulas.

| Symbol | Meaning in LM15 | Check |
|:--|:--|:--|
| $X$ | a generic random variable, per example (a count in §2–§3, $\ln G$ in §5), as lm05.md:60 | Volume III |
| $Y$; $y$ | $Y\sim t_\nu$, standard; $y$ a generic coordinate in (15.7)–(15.9) and Deep Dive 2: the argument of $f_G$, $F_G$, $f_Y$, the variable of integration in $\Gamma$ | Volume III: $y$ in a mathematical passage, no yields |
| $x$; $x_1<x_2$ | a loss level $x>0$ in $\{R\le-x\}$; two loss levels of a chord | one threshold convention (C15) |
| $a$ | the argument of $\Gamma$, $a>0$ | §6: generic constant, no bets |
| $\hat p$ | the blocks' up-day frequency, 3,200/5,840 (LM17's $\hat p$ uses all $T$ returns) | local |
| $\hat\lambda$ | the months' average count of days with $\lvert R\rvert\ge3\%$, $175/286=0.612$, the fitted Poisson mean (X3, E3) | local; $\lambda$ the model's mean |
| $\rho_1$ | the lag-1 correlation of the daily up-day indicators, a model value (§2 pitfall), in a model where only adjacent days are correlated | local; unsubscripted $\rho$ stays the return's |
| $\mu_X$, $\sigma_X$; $\Gamma$; $\alpha$ | mean and standard deviation of $X=\ln G$; gamma function; tail index | LM5; new; LM5's local symbol |

Not used: $P$, plain $E$, $\hat\mu$, $\kappa$ (cite (5.11)), $\theta$, $q$, $c$, $c_\nu$, $k$, $N$, $f$ alone, $g$, $\lambda_k$. QQ axes in words ("normal quantile", "standardized return"); levels as numbers ("the 1% quantile").

**Motivating case: "Which model for which question?"** (in-sample; 110 words)

> Take TAIEX's 5,849 daily total returns from 3 January 2003 to 8 October 2026. A normal model with their mean, 0.0625% [A15-09], and standard deviation, 1.2084% [A15-10], expects **0.08** days at or below −5% [A15-11]. TAIEX had **15** [A15-12] ([[LM13]]'s count). A Student-t fitted by maximum likelihood, with $\nu=3.065$ degrees of freedom [A15-13], expects **19.6** [A15-14] ([[ex:case]]).
>
> Now count the days with a move of 3% or more, either way, month by month. They average **0.612** a month [A15-15], but their variance is **1.846** [A15-16], three times the mean [A15-17]. Three months had eight: September and October 2008, and March 2020 [A15-18].
>
> Which model should answer which question? And what does the crowding of large moves into a few months say about independence?

Resolved in §6 (E8, X6, X7), §7 (X10, E9, E10) and §3 (E3, X3, [[LM26]]).

**Sections** (prose words):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | a distribution is a model with few parameters; LM5's 0050 verdict (0.058 days expected at −5%, 9 actual [A15-19]); case + X1; roadmap | 360 |
| 2 | Counting Successes: Bernoulli and Binomial {1} | one block first; Bernoulli $\mathbf 1\{\text{success}\}$, mean $p$ by (14.1), variance $p(1-p)$; (13.7), (13.13), (15.1); (15.2) via $\E[X(X-1)]$; E1 + X2; LM16, LM17 sentences | 500 |
| 3 | Rare Events: the Poisson Distribution {2} | $p=175/5{,}849=0.02992$ a session, about 20 a month; $\lambda=np$ fixed, (15.4) at $j=0$ by (1.6), Deep Dive 1; (15.3), (15.5) by (3.2); E2; E3 + X3; LM26, LM39 sentences; further reading Grinstead and Snell, §5.1 (Table 5.1) | 650 |
| 4 | The Normal Distribution: Quantiles and QQ Plots {3} | $\Phi^{-1}$, symmetry; $\Phi^{-1}(0.975)$ is [[LM4]]'s 1.96 [A15-20]; (15.6); TR23's quantiles by LM14's rule; E4; X4; E5; LM32 sentence | 560 |
| 5 | The Lognormal Distribution {4} | $G=e^X$; (15.7) by (5.4); (5.12), the variance from $2X$; mean above median; E6 + X5; LM17's daily model on the same years (C2); `lognorm`; LM17, LM38 sentences | 500 |
| 6 | The Student-t Distribution {5} | LM5's shape; bounds predict no count; (15.8) by (5.6), (5.7); (15.9), constant stated without proof (beta integral; SciPy's `t` page), checked numerically; E7; (15.10), Deep Dive 2; (15.11); (15.12), maximum likelihood; E8; X6; X7; widget | 780 |
| 7 | Tail Measures and Choosing a Model {6, 7} | kurtosis does not settle: E10 + X9; counts and quantiles need fewer moments; a power tail is a line of slope $-\alpha$; X8; E9 (15.13); EVT and asymmetry sentences; X10 resolves the case; tail means, LM32 sentence | 660 |
| 8 | Distributions in Python {8} | guarded counts, `norm.fit`, `t.fit`, `ppf`, `sf`, `lognorm`, `poisson`, `binom`; X11; LM18 sentence; lab box | 260 |
| — | Summary (7 bullets) / Practice Problems (12) / Solutions | | 140 / 380 / 500 |
| | **Total** | | **5,290** |

**Elements.** 10 examples (E1 §2; E2, E3 §3; E4, E5 §4; E6 §5; E7, E8 §6; E9, E10 §7); 7 knowledge checks (§2–§8); 5 中文導讀 (§3 for §2–§3; §4–§7), using 柏努利分布, 二項分布, 卜瓦松分布, 過度離散, 獨立同分布, 常態分布, 分位數, 分位數函數, 分位數-分位數點圖 (Q-Q plot; 樂詞網 statistics, 2026-10-18), 對數常態分布, 中位數, t 分布, 自由度, 伽瑪函數 (Γ 函數), 峰態, 超額峰態, 厚尾, 尾部指數, 經驗分布; "maximum likelihood" and "order statistic" stay English. One pitfall in each of §2–§8. Deep Dive 1: $\binom nj(\lambda/n)^j(1-\lambda/n)^{n-j}\to e^{-\lambda}\lambda^j/j!$ for every $j$, from $n(n-1)\cdots(n-j+1)/n^j\to1$, $(1-\lambda/n)^{-j}\to1$ and (1.6). Deep Dive 2 (its first sentence declares $y$, $z$): by (2.5), $y(1+y^2/\nu)^{-(\nu+1)/2}=-\frac{\nu}{\nu-1}\frac{d}{dy}(1+y^2/\nu)^{-(\nu-1)/2}$; parts (5.6), the boundary term vanishing for $\nu>2$; $y=z\sqrt{\nu/(\nu-2)}$ turns the rest into the reciprocal of (15.9)'s constant at $\nu-2$; $\Gamma(a+1)=a\Gamma(a)$ gives $\E Y^2=\nu/(\nu-2)$; once more, $\E Y^4=3\nu^2/\big((\nu-2)(\nu-4)\big)$ for $\nu>4$, so $\operatorname{Kurt}(Y)=3+6/(\nu-4)$.

Knowledge checks: §2 which $p$ maximizes $np(1-p)$, and TR23's 4.95 against $n/4=5$ [A15-21]; §3 why not a Poisson for up days ($\hat p=0.548$ [A15-22] is not small; variance 4.95, mean 10.96); §4 the $\sigma$ that makes the normal expect 15 days at −5%, 1.809%, which then expects 743 days [A15-23] at −2% against 252 [A15-24]; §5 a normal fitted to the 23 annual simple returns gives $\Pr(G<0)=6.1\times10^{-7}$ [A15-25], the lognormal 0; §6 which moments exist for $\nu=3.065$ and $\nu=5.139$ [A15-26]; §7 why the maximum-likelihood fit expects 2.57 days [A15-27] at or below −10% and TR23 has none; §8 why SciPy prints 6 for $t_5$'s kurtosis where LM5 prints 9 [A15-28].

Pitfalls: §2 "Independent trials with one $p$": a variance near $np(1-p)$ is consistent with independence, not proof. LM13's sign dependence (0.4639 against 0.4521 [A15-29]) is a lag-1 correlation of daily indicators, $\rho_1=(0.4639-0.4521)/(1-0.4521)=0.0215$; if only adjacent days are correlated, [[LM16]]'s variance of a sum carries it into a block, $20\times0.548\times0.452\times(1+2\cdot\tfrac{19}{20}\cdot0.0215)=5.16$ [A15-30] against 4.95, and the blocks give 4.72 [A15-31]: they cannot see it either way ([[LM21]] tests). §3 "Rare is not independent": the Poisson matches the average month and misses the bad ones (9 months with five or more against 0.123 [A15-32]). §4 "Which level does a QQ point stand for?": rank $j$ sits at $(j-\tfrac12)/T$, mid-step of $\hat F$ (at $j/T$ the best day would sit at $+\infty$); a quantile at a stated level keeps LM14's $\lceil uT\rceil$. §5 "A lognormal does not fix daily tails": with $\bar r=0.05517\%$, $s_r=1.2107\%$ [A15-33], 0.0541 days at −5% [A15-34] against the normal's 0.0817. §6 "Matching a moment the fit says does not exist": (15.12) presumes $\nu>4$, and $\nu=3.065$ makes the kurtosis infinite; SciPy's `scale` is not $\sigma$. §7 "The price limit truncates the tail": ±7% before 1 June 2015, ±10% after; 2.57 expected at −10%, none observed. §8 "Excess or not": SciPy's kurtosis numbers are excess kurtosis.

**Exhibits.** Notes carry the Source line (FinMind `TaiwanStockTotalReturnIndex`, TAIEX, retrieved 18 October 2026), $R_t=P_t/P_{t-1}-1$, 3 January 2003 – 8 October 2026, $T=5{,}849$, the counting guard, and for data quantiles $R_{(\lceil uT\rceil)}$ (`method="inverted_cdf"`). Notes with expected counts print $\bar R=0.0625\%$, $s=1.20836\%$ (1.2084% gives 0.0818 at −5%), the kurtosis fit's $\nu=5.139$ and the maximum-likelihood fit ($\nu=3.065$, location 0.0997%, scale 0.7761%).

- **X1 `case`** (table, §1). (a) Days at or below −2% and −5%: normal 257 [A15-35] and 0.0817; Student-t (maximum likelihood) 210 and 19.6; TAIEX 252 and 15. (b) Months, $\lvert R\rvert\ge3\%$: mean 0.612 (Poisson and data); variance 0.612 against 1.846; months with five or more 0.123 against 9.
- **X2 `binom`** (`bar`, §2). Up days in a block, 4 to 17; "Blocks observed" (colour 2) 0, 2, 4, 13, 21, 38, 34, 59, 46, 39, 26, 7, 3, 0 [A15-36]; "Binomial, p = 3,200/5,840: expected blocks" (colour 1) 0.39, 1.50, 4.56, 11.05, 21.77, 35.18, 46.91, 51.69, 46.99, 35.05, 21.24, 10.30, 3.90, 1.11 [A15-37]. Note: mean 10.96, variance 4.72 (divisor 292) against 10.96 and 4.95; outside 4 to 17 the binomial expects 0.34 blocks (unrounded values).
- **X3 `poisson`** (`bar`, §3). Large moves in a month, 0 to 8; observed 210, 38, 9, 16, 4, 5, 1, 0, 3 [A15-38]; Poisson($\hat\lambda=175/286$; one decimal from 10 up, three significant figures from 0.001, two below) 155.1, 94.9, 29.0, 5.92, 0.906, 0.111, 0.0113, $9.9\times10^{-4}$, $7.6\times10^{-5}$. Note: eight or more, $8.1\times10^{-5}$ expected; 2008-12 had six.
- **X4 `qq`** (`scatter`, §4). Horizontal: normal quantile $\Phi^{-1}\big((j-\tfrac12)/T\big)$; vertical: standardized return $(R_{(j)}-\bar R)/s$; 824 points: all 266 with a normal quantile beyond ±2, ranks 1, 11, 21, … and both extremes [A15-39]; `lines` on the 45° line (`extend`); labelled 7 April 2025 $(-3.758,-8.079)$ and 10 April 2025 $(3.758,7.604)$; n2. Note: below the line on the left and above it on the right mean heavier tails; rank 59, the 1% quantile, at $(-2.326,-3.004)$; the thinned middle hides no cited value.
- **X5 `lognormal`** (`line`, §5). $G$ from 0.5 to 1.9; cumulative probability. "Lognormal, μ_X = 0.11646, σ_X = 0.22207" [A15-40] (colour 1); "TAIEX, 23 calendar years" (colour 2, `step`, heights $i/23$). `vline`s at the median 1.1235 and the mean 1.1516 [A15-41]. Note: 2003–2025, 2003 from its first close (2 January 2003); beyond the model's 5% and 95% quantiles, 0.7797 or 1.6189, 2 years observed (2008, 0.5693; 2009, 1.8334) against 2.3 expected [A15-42]; empirical median 1.1514 (2013) [A15-43].
- **X6 `tailtable`** (table, §6). Rows −2% to −10%; columns $z=(-x-\bar R)/s$, three decimals [A15-44]; expected days, three significant figures (scientific, two below 0.001): normal 257, 32.9, 2.26, 0.0817, 0.00153, $1.5\times10^{-5}$, $7.4\times10^{-8}$, $1.9\times10^{-10}$, $2.4\times10^{-13}$; Student-t by kurtosis 232, 64.3, 21.2, 8.17, 3.59, 1.75, 0.926, 0.524, 0.313 [A15-45]; by maximum likelihood 210, 79.0, 36.6, 19.6, 11.6, 7.41, 5.00, 3.52, 2.57; TAIEX 252, 108, 44, 15, 6, 2, 2, 1, 0. Note: 108 and 15 are [[LM13]]'s counts.
- **X7 `tailchart`** (`line`, log $y$, §6). Days with $R$ at or below a return from −10.5% to −1.0%: TAIEX (colour 2, `step`), normal (colour 1, ends at 0.001 as LM5's chart does), maximum likelihood (colour 3), kurtosis fit (colour 4, `dash`); dashed `vline` at −5%, `hline` at 1 day. Returns stored to ten decimals. Carries the widget block.
- **X8 `loglog`** (`line`, log $y$, §7). Days with $R\le-x$ for $x$ from 1% to 10%, plotted at $\log_{10}x$ with `tickLabels` "1%" … "10%": TAIEX (colour 2, `step`), maximum likelihood (colour 3), normal (colour 1, ends at 0.001 as in X7), a dashed line of slope −3 through the data at 3% (colour 4; LM5's $\alpha\approx3$ [A15-46]). Note: chords of adjacent levels 2.09 (2%→3%), 3.12, 4.82, 5.03 (5%→6%) [A15-47] rise with the level (E9). The steepening beyond 5% rests on few days (15, 6, 2, 2, 1), and before June 2015 the 7% limit kept every return above −6.68% [A15-77].
- **X9 `stability`** (table, §7). Full sample; 7% limit; 10% limit. Columns: $T$; $s$ (%, three decimals); excess kurtosis; $\nu$ by kurtosis; $\nu$ by maximum likelihood (three decimals); 1% quantile, the order statistic $R_{(59)}$, $R_{(31)}$, $R_{(28)}$ of the part's 5,849, 3,077 or 2,772 returns (LM14's rule with the part's size; %, three decimals); days at or below −3% per 1,000; variance ÷ mean of monthly counts [A15-48]. Values: 5,849, 1.208, 5.27 [A15-49], 5.14, 3.065, −3.567 [A15-50], 18.5, 3.02 / 3,077, 1.257, 3.39, 5.77, 2.990, −3.621, 23.4, 2.95 / 2,772, 1.152, 8.07, 4.74, 3.237, −3.467, 13.0, 3.01. Note: a stability check; each part fitted on its own; no standard errors ([[LM20]]); 5.27 is [[LM14]]'s.
- **X10 `choice`** (table, §7). Question | model | evidence | limiting assumption. A −2% day: normal (257 against 252); fails from −3%. The 5% quantile: normal (−1.925% [A15-51] against −1.862%). −3% to −5%, the 1% quantile: maximum-likelihood $t$ (79.0, 36.6, 19.6 against 108, 44, 15; −3.365% [A15-52] against −3.567%); symmetric, too heavy from −5%. Beyond −7%: counts, or the kurtosis fit (1.75, 0.926, 0.524 against 2, 2, 1); few, truncated days. A year: lognormal (median +12.35%, the compound rate [A15-53]; mean +15.16% against 14.97%); independent years. Monthly large moves: no Poisson (1.846 against 0.612); clustering. Up days in a block: binomial (4.72 against 4.95); independence.
- **X11 `scipy`** (table, §8). Object | parameters in LM15's symbols | trap. `norm(loc, scale)`: $\mu$, $\sigma$. `lognorm(s, scale)`: $\sigma_X$, $e^{\mu_X}$. `t(df, loc, scale)`: $\nu$, $\mu$, $\sigma\sqrt{(\nu-2)/\nu}$ (variance `scale²·df/(df−2)` for `df > 2`). `poisson(mu)`: $\lambda$. `binom(n, p)`. `.fit`: maximum likelihood by default; `norm.fit` returns $\bar R$ and $s$ with divisor $T$ [A15-54]. `stats.kurtosis` (`fisher=True`, `bias=True`) and `.stats(moments="k")`: excess kurtosis, divisor-$T$ moments. Data quantiles: [[LM14]]'s `method="inverted_cdf"`.

**Widget `tdist`, "Student-t explorer: TAIEX histogram, normal and Student-t".** Modelled on LM5's `tails`; `Book.controls`; `Book.dist` (`tPdf`, `tCdf` for real $\nu>0$, `Phi`, `PhiInv`), build-checked against SciPy values in the JSON; the 1% quantile by bisection on `tCdf` in `lm15.js`, checked against `t.ppf`; scientific format below 0.001. Controls: fit ("Maximum-likelihood fit (ν = 3.065)" or "Same mean and σ as the data, choose ν"); $\nu$ slider 2.05–30, step 0.01, disabled at 3.065 in the first mode, from 5.14 in the second; loss level $x$ 1.0%–10.0%, step 0.1; density axis log or linear. Drawn: TR23 histogram as a step line (0.5-point bins, area 1; colour 2), normal density (colour 1, dashed), Student-t density (colour 3), $R\le-x$ shaded. Readouts: $z$; expected days with $R\le-x$ (normal, Student-t); TAIEX days (guard); their ratio; the Student-t's $\sigma$ and kurtosis ("infinite" for $2<\nu\le4$); its 1% quantile against −3.567%. Initial state (the PDF): maximum-likelihood fit, $x=5\%$, log axis: 0.0817, 19.6, 15, σ 1.317% [A15-55], kurtosis infinite, −3.365%. No random numbers. Data: the `widget` block of `chart-lm15-tailchart`.

**Examples.**

- **E1 §2 Up days in a block.** 3,200 up days in 5,840 returns, the blocks' up-day frequency $\hat p=0.548$; $np=10.96$, $np(1-p)=20\times0.548\times0.452=4.95$; observed 10.96 and 4.72. From the printed 0.548: $\Pr(X\le5)=0.00677$, 1.98 blocks (observed 2); $\Pr(X\ge16)=0.01807$, 5.28 (observed 3) [A15-56]. The probabilities carry the digits that reproduce them (0.0181 would give 5.29).
- **E2 §3 From a rare binomial to the Poisson.** $p=0.02992$, $n=20$, $\lambda=0.5984$: $\Pr(X=0)$ 0.5447 against 0.5497; $\Pr(X=1)$ 0.3360 against 0.3289; $\Pr(X=2)$ 0.09845 against 0.09842 [A15-57]. $(1-0.612/n)^n=0.53711$, 0.54186, 0.54226 for $n=20$, 250, 10,000; $e^{-0.612}=0.54227$ [A15-58].
- **E3 §3 Do large moves arrive like a Poisson count?** $\hat\lambda=175/286=0.612$. Expected months: none 155.1 (observed 210), one 94.9 (38), five or more 0.123 (9), eight or more $8.1\times10^{-5}$ (3) [A15-59]. Variance 1.846, ratio 3.02. Months of unequal length (6 to 24 sessions) would give a variance of only 0.60 [A15-60]. Regimes: 2.95, 3.01.
- **E4 §4 Normal quantiles against TAIEX's.** $\Phi^{-1}$ at 0.95, 0.975, 0.99, 0.999: 1.6449, 1.9600, 2.3263, 3.0902 [A15-61]. With $\bar R=0.0625\%$, $s=1.2084\%$, against $\hat F^{-1}(u)=R_{(\lceil uT\rceil)}$ (ranks 293, 147, 59, 6): 5% −1.925% against −1.862%; 2.5% −2.306% against −2.648%; 1% −2.749% against −3.567%; 0.1% −3.672% against −6.313% (11 October 2018). Three decimals.
- **E5 §4 Reading the QQ plot.** Worst $(-3.758,-8.079)$, best $(3.758,7.604)$, rank 59 $(-2.326,-3.004)$; the S shape is the heavy tail, and rank 59's gap is E4's 1% gap in standard deviations.
- **E6 §5 A lognormal for annual growth.** 23 calendar-year factors, 2003 from its first close (2 January 2003) [A15-62] (LM14: arithmetic mean 14.97%, compound 12.35%); $\mu_X=0.11646$, $\sigma_X=0.22207$ (divisor 23; five decimals, as 0.1165 gives a median of 1.1236). Median $e^{\mu_X}=1.1235$ (the compound rate); mean 1.1516 (+15.16% against 14.97%); standard deviation 0.2589; $\Pr(G<1)=\Phi(-0.5244)=30.0\%$, 6.90 of 23 years against 5 (2008, 2011, 2015, 2018, 2022) [A15-63]; 5% and 95% quantiles 0.7797, 1.6189. One sentence (C2): LM17's iid daily model on the same years (5,664 log returns, $m=246$) gives 26.5% [A15-64]: its annual log return has mean 0.1163, $\mu_X$ by construction (one year is 246 sessions, close to the years' average count), but standard deviation 0.1856 against $\sigma_X=0.22207$; independent days with $\sqrt m$ scaling understate the annual spread ([[LM19]] examines it).
- **E7 §6 Constants from the gamma function.** $\Gamma(1/2)=\sqrt\pi=1.772454$, $\Gamma(3/2)=0.886227$, $\Gamma(2)=1$, $\Gamma(5/2)=1.329340$ [A15-65]. At $\nu=3$ (15.9)'s constant is $\Gamma(2)/\big(\sqrt{3\pi}\,\Gamma(3/2)\big)=2/(\pi\sqrt3)=0.3676$, the constant LM5's text left out (lm05.md:338); $\frac{2}{\pi\sqrt3}(1+y^2/3)^{-2}=6\sqrt3/\big(\pi(3+y^2)^2\big)$ is the $t_3$ density LM5's widget draws (lm05.js:18). At $\nu=1$, $1/\pi=0.3183$ (Cauchy); as $\nu\to\infty$ the shape tends to $e^{-y^2/2}$ by (1.6) and the constant, numerically, to $1/\sqrt{2\pi}=0.3989$ (0.3956 at $\nu=30$, 0.3988 at 1,000) [A15-66]. Four decimals.
- **E8 §6 Two ways to fit a Student-t.** Kurtosis: excess 5.27 ([[LM14]]'s, cited), $\nu=4+6/5.27=5.14$ (5.139 where counts are recomputed), location $\bar R$, scale 0.944%. Maximum likelihood: $\nu=3.065$, location 0.0997%, scale 0.7761%; $\sigma=0.7761\%\sqrt{3.065/1.065}=1.317\%$, 9% above $s$; the location sits near the median, 0.0879% [A15-67], not the mean. Under the second fit the matched kurtosis is infinite. $\nu=3.07$ would give 19.5 at −5%.
- **E9 §7 Reading a tail index.** If $\Pr(R\le-x)$ is a constant multiple of $x^{-\alpha}$ between two levels, (15.13) returns $\alpha$ exactly; otherwise the chord is a reading. From X6's counts, adjacent levels 2%–6% give 2.09, 3.12, 4.82, 5.03 [A15-47]: the chord rises with the level; all ten pairs lie between 2.09 and 5.03, mostly inside LM5's 2–5. At 3%→6%: data 4.17; normal 14.4, maximum likelihood 2.77, kurtosis fit 4.16 [A15-68]. Two decimals. Report the chords, not one value; no Hill estimate ([[LM20]]).
- **E10 §7 One day, four tail measures.** 7 April 2025: excess kurtosis 4.25 → 4.94 (5,478 returns, then 5,479); 1% quantile −3.538% → −3.543%; days at or below −3%, 96 → 97 [A15-69]. Without that day, 4.71; without the four largest moves (7 and 10 April 2025, 5 August 2024, 31 July 2026), 3.74 [A15-70]. The ten largest fourth-power terms supply 35.0% of $\sum(R-\bar R)^4$ and 6.7% of $\sum(R-\bar R)^2$ [A15-71]; LM5's 0050: 8.12, 7.05, 3.85, 5.84 → 7.63 [A15-72], 62.8% and 14.1% [A15-73]. Tail means at −5%: data −6.26%, the normal's (5.11) −5.26%, maximum likelihood −7.57% [A15-74] (LM32 sentence).

**Problems plan** (12; MC keys A, C, B, C; Python 11, 12; the lab repeats 2, 5, 7, 10, 11, 12). Every stem names TR23 (TAIEX total returns, 3 January 2003 – 8 October 2026, $T=5{,}849$, $A=246.12$), divisor $T$, the guard, the rounding and, for a quantile, LM14's rule $R_{(\lceil uT\rceil)}$ (`method="inverted_cdf"`; in a part, with the part's size in place of $T$, given as a number: $R_{(31)}$ is the 1% quantile of the 3,077 returns before June 2015).

1. MC. Up days in a 20-session block modelled as $\operatorname{Bin}(20,0.548)$. The variance is *closest* to: **A 4.95** (key); B 10.96 ($np$, the mean); C 2.23 (the standard deviation).
2. Poisson with $\lambda=0.612$: $\Pr(X=0)=0.5423$, $\Pr(X\ge5)=0.000431$; over 286 months 155.1 and 0.123 against 210 and 9. Which months does the model miss, and why?
3. MC. Monthly counts of days with $\lvert R\rvert\ge3\%$: mean 0.612, variance 1.846 (divisor 286). Variance ÷ mean is *closest* to: A 0.33 (inverted); B 1.00 (the Poisson's own ratio); **C 3.02** (key).
4. Derive $\E X=\Var X=\lambda$ from (3.2) and $\E[X(X-1)]=\lambda^2$; show that $\operatorname{Bin}(n,\lambda/n)$ has variance $\lambda(1-\lambda/n)\to\lambda$.
5. With $\bar R=0.0625\%$, $s=1.2084\%$: the normal's 1% and 99% quantiles (−2.749%, +2.874%) against TAIEX's $R_{(59)}$ and $R_{(5{,}791)}$ (−3.567%, +3.125%); which tail does the normal miss more (0.82 against 0.25 points [A15-75])?
6. MC. The lognormal fitted to the 23 calendar-year growth factors 2003–2025, 2003 from its first close ($\mu_X=0.11646$, $\sigma_X=0.22207$), gives a losing year a probability *closest* to: A 21.7% (5 of 23, the sample's frequency); **B 30.0%** (key); C 70.0% (sign reversed).
7. For E6's lognormal: median 1.1235, mean 1.1516, standard deviation 0.2589, quantiles 0.7797 and 1.6189; check with `lognorm(s=0.22207, scale=np.exp(0.11646))`.
8. Show that (15.9)'s constant at $\nu=4$ is $\Gamma(5/2)/\big(\sqrt{4\pi}\,\Gamma(2)\big)=3/8$; the variance and kurtosis of $t_5$ (5/3, 9) and $t_6$ (3/2, 6); which exist for $t_4$ and $t_2$?
9. MC. TR23's excess kurtosis is 5.27. The matching $\nu$ is *closest* to: A 1.14 (the 4 forgotten); B 6.64 (the excess taken as the kurtosis) [A15-26]; **C 5.14** (key).
10. From 252, 44 and 6 days at −2%, −4%, −6%, compute the chords 2.52, 4.91, 3.40; why do they differ (2%→6% weights the other two by $\ln2$ and $\ln1.5$)? Compare with the maximum-likelihood $\nu=3.065$, that model's tail index.
11. *(Python, stability check)* Split at 1 June 2015: $T$, $s$, excess kurtosis, `t.fit`'s $\nu$, each part's 1% quantile (3,077 / 2,772; 1.257% / 1.152%; 3.39 / 8.07; 2.990 / 3.237; −3.621% / −3.467%). Which moved most, and which label does the comparison carry?
12. *(Python)* Days at or above +3% and +5% (67, 13) against the normal (44.0, 0.128), the maximum-likelihood $t$ (94.2, 22.0) [A15-76] and the lower tail (108, 15). Why can no symmetric model fit both tails?

**Lab parts** (`build/make_lab15.py`; plain "LM20" in cells, never `[[LM20]]`): 1 data, the guard against a `Fraction` recount; 2 binomial: X2, E1; 3 Poisson: X3, E2, E3, regimes, unequal months; 4 normal: X4, E4, E5; 5 lognormal: X5, E6, `lognorm`; 6 Student-t: E7, both fits from several starting points, X6, X7; 7 tail measures: X8, E9, X9, E10; 8 problems 2, 5, 7, 10, 11, 12. Extension (stability check, no conclusions): the Student-t fitted to non-overlapping five-session returns (pointers to LM17, LM19).

**Cross-module tags** (users: Volume III briefs citing the tag; later modules as ROADMAP plans). (15.1) $\Pr(X=j)=\binom nj p^j(1-p)^{n-j}$, $j=0,\dots,n$, $n$ independent trials with one $p$ (LM16, LM17, LM21). (15.2) $\E X=np$, $\Var X=np(1-p)$ (LM16, LM17). (15.3) $p_X(j)=e^{-\lambda}\lambda^j/j!$, $j=0,1,\dots$, $\lambda>0$ (LM26, LM39). (15.4) $\binom nj(\lambda/n)^j(1-\lambda/n)^{n-j}\to e^{-\lambda}\lambda^j/j!$ as $n\to\infty$, fixed $\lambda>0$ and $j$ (LM39). (15.5) $\E X=\Var X=\lambda$ (LM26, LM39). (15.6) $F_R^{-1}(u)=\mu+\sigma\Phi^{-1}(u)$ for $R\sim\mathcal N(\mu,\sigma^2)$, $\sigma>0$, $0<u<1$; $\Phi^{-1}(1-u)=-\Phi^{-1}(u)$ (LM17, LM18, LM20, LM32). (15.7) $G=e^X$, $X\sim\mathcal N(\mu_X,\sigma_X^2)$, $\sigma_X>0$: $f_G(y)=\varphi\big((\ln y-\mu_X)/\sigma_X\big)/(\sigma_Xy)$, $y>0$; $\Var G=(e^{\sigma_X^2}-1)e^{2\mu_X+\sigma_X^2}$; quantiles $e^{\mu_X+\sigma_X\Phi^{-1}(u)}$ (LM17, LM38). (15.8) $\Gamma(a)=\int_0^\infty y^{a-1}e^{-y}dy$, $a>0$; $\Gamma(a+1)=a\Gamma(a)$; $\Gamma(1/2)=\sqrt\pi$ (LM20, LM21). (15.9) $f_Y(y)=\frac{\Gamma((\nu+1)/2)}{\sqrt{\nu\pi}\,\Gamma(\nu/2)}(1+y^2/\nu)^{-(\nu+1)/2}$, $\nu>0$ (LM17, LM20, LM21). (15.10) $\Var Y=\nu/(\nu-2)$, $\nu>2$; $\operatorname{Kurt}(Y)=3+6/(\nu-4)$, $\nu>4$ (LM19, LM20, LM32). (15.11) $R=\mu+\sigma\sqrt{(\nu-2)/\nu}\,Y$, $\nu>2$, has mean $\mu$ and standard deviation $\sigma$ (LM32). (15.12) $\nu=4+6/(\operatorname{Kurt}-3)$ for positive excess kurtosis (LM19, LM20). (15.13) if $\Pr(R\le-x)$ is a constant multiple of $x^{-\alpha}$ for $x_1\le x\le x_2$, $0<x_1<x_2$, then $\alpha=\ln\big[\Pr(R\le-x_1)/\Pr(R\le-x_2)\big]/\ln(x_2/x_1)$; for other laws the right side, the chord, is a reading (LM20, LM32).

**Pitfalls to pre-empt.**

- *Conditions.* Beyond the tags: Student-t mean for $\nu>1$; kurtosis infinite for $2<\nu\le4$, undefined for $\nu\le2$; E2 sizes the "≈"; (15.9)'s constant stated without proof, checked numerically; a chord is a reading, not an estimate.
- *Precision.* The exhibit notes' parameters ($\nu=3.065$, $s=1.20836\%$, $\nu=5.139$); $\mu_X$, $\sigma_X$ to five decimals; E1's tails from the printed 0.548; E6's 0.1856 (0.186 gives 26.6%).
- *Data traps.* Before 1 June 2015 every return lies between −6.6789% and +6.7420%. Two-decimal levels make ties exact: use the guard. 2003 starts on 2 January; October 2026 has 6 sessions; SciPy's Poisson parameter is `mu`; NumPy's default quantile interpolates.
- *Boundary creep.* No standard errors, intervals, tests, Hill estimator (LM20, LM21), GARCH (LM26), simulation (LM18), normal approximation (LM17) or joint laws (LM16); value at risk and expected shortfall one sentence each (LM32); never "the" model of TAIEX.

**Stage 4 for earlier modules.** LM15 cites LM1's (1.6) and binomial-theorem Deep Dive, LM2's (2.5) and LM3's (3.2): 15 joins the leads of lm01.md:6, lm02.md:6 and lm03.md:6; lm05.md:6 already lists 15. lm04.md:6 does not gain 15: LM15 cites no LM4 result (it proves the 2.5% point lm04.md:541 used).

## LM16 Joint Distributions and Dependence

**Prereq** `[1, 3, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15]`. Results used (other modules' exhibits named in words):

- LM1: (1.12), log returns add over days.
- LM3: the variance of a sum of independent squared increments (lm03.md:545), an instance of (16.3).
- LM5: density, $F$, (5.9) (lm05.md:442–447); (5.5); $\E Z^2=1$ by parts (lm05.md:323–327); Fubini, stated without
  proof (lm05.md:310); the disc integral $2\pi(1-e^{-b^2/2})$ (lm05.md:313); (5.11) and PP14 (lm05.md:501–509, 759);
  the annualization caveat (lm05.md:523).
- LM7: the two-asset variance, $\sigma_{12}=\rho\sigma_1\sigma_2$, $\Cov(R_1,R_p)$ and $\Var(R_1-R_2)$ as sample
  identities (lm07.md:71–79); the 2022 joint loss (lm07.md:418).
- LM8: (8.6) and its proof (lm08.md:216–225); (8.9), divisor-free; the pair's correlation (lm08.md:345).
- LM9: (9.2), with $\lvert\det M\rvert$ the area of the columns' parallelogram (lm09.md:114–119), for Deep Dive 2.
- LM10: (10.2)–(10.5); the by-hand example (lm10.md:101–123); $A\hat\Sigma_3$ and its $(1,-1,0)$ form
  (lm10.md:61–63); the sample's $A$ (lm10.md:41).
- LM11: (11.1)–(11.3) for contour axes; the descriptive ellipse (lm11.md:148); the all-28 days (lm11.md:48).
- LM12: (12.8) by tag (lm12.md:407; its index $p$ is not reprinted); (12.9) and the exact mean $N$
  (lm12.md:453–461); the two-asset Cholesky example and the Cholesky exhibit's first rows (lm12.md:431–442); S5's
  largest $\lVert\mathbf z_t\rVert^2$ (lm12.md:483); the limit caveat (lm12.md:499–500); colouring (lm12.md:504, 527).
- LM13: (13.4)–(13.6) conditional probability, the multiplication rule, independent events; (13.8) total probability
  ((16.5) is its form for expectations); (13.11) $F_X$; (13.13) independence of $n$ discrete random variables;
  indicators; the empirical distribution as a probability model; events of probability zero.
- LM14: (14.1) expectation and $\E[\mathbf 1_{\mathcal A}]=\Pr(\mathcal A)$; (14.2) LOTUS with (5.9); (14.3)
  linearity; (14.4) $\E X^2=\sigma_X^2+\mu_X^2$, $\Var(\eta X+\zeta)=\eta^2\Var X$; (14.6) $\Var(Z^2)=2$.
- LM15: (15.1), (15.2) the binomial pmf, mean and variance (E8).

**Leads** `[17, 18, 19, 20, 21, 22, 23, 24, 26, 27, 28, 30, 31, 32, 33, 35]`: the modules the tags below name, and by
pointer LM22 (intervals for crash correlations) and LM26 (dependent but uncorrelated returns).
Time "≈ 3 h + lab". Syllabus: "Covariance, conditional expectation, the multivariate normal, crash correlation."

**Forward links honoured.**

| Promise | Kept in |
|:--|:--|
| lm07.md:75, 71–79: covariance, correlation, LM7's identities | §3 (16.2); §4 (16.3), E5 |
| lm08.md:336: orthogonal centred vectors ≠ unrelated assets | §3: (16.2) by LM8's argument; E3, E4, X3; $\hat\rho$ is the empirical distribution's correlation |
| lm10.md:133; AUTHORING §6 ($\sigma_p^2$ in a model) | §4 (16.4) beside (10.2), (10.3), (10.5); X7 |
| lm11.md:148: not a probability contour | §6, X5, on the U28 pair |
| lm12.md:461, 497, 499–500; make_lab12.py:475 | §6 (16.9), E8, E9, X6 |
| lm12.md:504, 527: colouring | §6 (16.7); a paragraph and the 導讀 separate "uncorrelated, variance 1" from "independent normal" |
| lm05.md:501–509: (5.11) | §5, a special case; KC |
| lm05.md:523; lm03.md:545 | §4, (16.3): sums of independent days |
| lm07.md:418; lm11.md:48 | §3 pitfall, §7 opening, as printed |
| make_lab11.py:324–327 | §6: rotation invariance, one sentence |
| plans/vol-2.md:560: (11.1)–(11.3) → LM16 | §6 contour axes, X5 |
| TODO.md:51–57 | X7 and the above |

**Outcomes** ("After this module you should be able to:"):

1. "compute joint, marginal and conditional distributions from counts or a joint density, and decide whether random variables are independent"
2. "define population covariance and correlation, prove $\lvert\rho\rvert\le1$, and show that uncorrelated variables can be dependent"
3. "compute the mean and variance of sums and portfolios, and explain why every covariance matrix is positive semidefinite"
4. "apply conditional expectation, the tower property and the law of total variance"
5. "describe the multivariate normal through linear maps, colouring, marginals and conditional distributions"
6. "define the chi-square law, and interpret probability contours and the squared Mahalanobis distance against it"
7. "compare a crash correlation with the bivariate normal benchmark under the same conditioning event"
8. "compute joint frequencies, conditional moments, Mahalanobis distances and normal benchmarks in Python with the right divisor, guard and tail function"

**Owns.** Joint pmf and density, marginals, conditional pmf and density. Independence of $n$ random variables (the
joint distribution function factorizes; equivalently the joint pmf or density) and the product rule (16.1), derived for
pmfs and densities; LM13 gives no density version. Covariance, correlation, $\lvert\rho\rvert\le1$ with its equality
case (16.2); independent ⇒ uncorrelated, not conversely. The sum rule (16.3): LM7's identities in population form,
$n$-term sums, $m$ independent days, counts of independent indicators. $\boldsymbol\mu$, $\Sigma$, $\sigma_p^2$,
$\operatorname{Corr}(\mathbf X)$, PSD (16.4). $\E[Y\mid X]$ and conditional expectation on an event; (16.5), (16.6),
exact on the empirical distribution. The multivariate normal: definition by linear combinations, linear maps,
marginals, colouring, whitening, density (16.7); rotation invariance; uncorrelated jointly normal ⇒ independent; the
normal pair's conditional law (16.8). The definition of $\chi^2_N$, the law of a sum of $N$ independent squared
standard normals ($N$ its degrees of freedom; mean $N$, variance $2N$); $d^2\sim\chi^2_N$,
contours (16.9). Crash correlation: (16.10) and exceedance correlations against their normal benchmark.

**Leaves.** Random generation and simulation error → LM18 (LM16 draws no random numbers). LLN, CLT,
$\Var(\bar X_n)=\sigma^2/n$ → LM17. Sample skewness, kurtosis, the √T rule in data → LM19. Standard errors of
$\hat\rho$, maximum likelihood for $\mathcal N_N$ → LM20. Tests → LM21; bootstrap intervals → LM22. Regression
inference → LM23. Clustering and time-varying correlation → LM26 (one pointer). Risk decomposition → LM27, LM31;
estimation error in $\hat\Sigma$ → LM30. Monte Carlo VaR → LM32; stress scenarios → LM35. Copulas: not in the book.
The 28-dimensional all-down comparison: not in Volume III.

**Uses before taught.**

- "Independent normal variables are jointly normal, and a normal vector's law is fixed by $\boldsymbol\mu$ and $\Sigma$
  (stated without proof; Blitzstein and Hwang 2019, §7.5)." The density (16.7), $\Sigma$ PD: "stated without proof;
  Wasserman 2004, §2.10: his equation (2.10) and Theorem 2.43" (SOURCES); Deep Dive 2 draws $N=2$. The writer
  reads §7.5's statements before citing them.
- "SciPy's `stats.chi2` gives $\chi^2_N$'s tails for $N>2$; [[LM21]] builds tests on it." The definition is LM16's;
  no $\chi^2_N$ density.
- "That a sum of many independent days is nearly normal is the central limit theorem of [[LM17]]." (§4)
- "Large moves cluster in time; [[LM26]] models how tomorrow's spread depends on today's move." (§3)
- "$\beta$ is the population slope that [[LM12]]'s least squares estimate; its standard error is [[LM23]]'s." (§6)
- "Drawing $\mathbf Z$ on a computer, and simulation error, are [[LM18]]'s." (§6)
- "Whether a crash correlation's gap from its benchmark could be chance is for [[LM21]] and [[LM22]]." (§7)
- "The exceedance benchmark has no closed form; the script integrates it with `quad`, as [[LM5]] did." (§7)
- "Splitting $\sigma_p^2$ among assets is [[LM27]]'s and [[LM31]]'s; how far $\hat\Sigma$ lies from $\Sigma$, [[LM30]]'s." (§4)

**Data role.** U28 only: `data/processed/vol2_closes.parquet`, loaded as `data/lm10_series.py` does (`u28()`, `date` a
string). Closes 2008-12-01 → 2026-10-08; $T=4{,}382$ simple daily price returns from 2008-12-02 [A16-01]; 6,520
calendar days, 17.8508 years [A16-02]; $A=245.4794$, printed 245.48 as in LM10 [A16-03]. No dividends. 524 closes on
38 dates are repaired [A16-04]; none on 2–10 April 2025, 5 August 2024, 5 May 2009 or the closes before them [A16-05].
Objects: the pair Semiconductor/FinancialInsurance; S5 (E9, X6); U28 (KC §6); the TAIEX price index on the same dates
(E4, X3, §4, P5, P6), captioned "TAIEX price index (no dividends), U28 dates" (LM16 never reads TR23). Figures earlier
modules printed on other samples (LM7's 2022 0050 and 00679B; LM11's ellipse on LM7's sample) are quoted as printed,
with their module, never recomputed. Scripts: `data/lm16_numbers.py` (every printed value, asserted against
`src/lm16.md`; hand examples from printed inputs) and `data/lm16_charts.py` (X3, X5, X6, X8, the widget grid).

**Hygiene declaration.** *Descriptive*: every count, frequency, sample or exceedance correlation and $d_t^2$.
*In-sample*: models with the same sample's moments (divisor $T$): expected counts, contour shares, $\chi^2$ tails, E5
(LM10's printed matrix), §4's year sum, E7–E10's model values, X8, X9, widget, P5, P7, P8, P10, P11, each "a model
fitted to the same days, not a forecast". *Stability check*: the lab extension only (2008-12-02 → 2015-05-29 against
2015-06-01 → 2026-10-08), no conclusion. *Constructed*: E2, E3, P2, P3, P4, P9, KC §3, KC §4. Nothing is
out-of-sample. Local note: "Every count and correlation here describes U28's 4,382 days, 2 December 2008 to 8 October
2026 (sectors and the TAIEX price index): descriptive. The normal model uses the same days' moments: in-sample
benchmarks, not forecasts. The lab's comparison of the two price-limit regimes is a stability check; whether gaps
could be chance is [[LM21]]'s and [[LM22]]'s question."

**Notation.** §6 and Volume III symbols keep their meanings, notably $\rho$ against $\hat\rho$ (LM16 has both),
$\mathbf R_t$ and $\mathbf z_t$ (data), $\bar r$, $s_r$ against $g$, $\sigma_r$, $m$, $k\ge0$, $d^2$, $\eta$, $\zeta$
(§6's row), $\mathcal A$ (an event in a general statement, (14.1)). Local:

| Symbol | Meaning | Check |
|:--|:--|:--|
| $p_{X,Y}$, $f_{X,Y}$; $p_{Y\mid X}$, $f_{Y\mid X}$ | joint and conditional pmf and density | extend $p_X$, $f_X$ |
| $\E[Y\mid X]$, $\E[Y\mid X=x]$, $\Var(Y\mid X)$ | conditional expectation (a random variable), its value, conditional variance | `\mid` |
| $\mathbf R$; $\sigma_{ij}$; $\operatorname{Corr}(\mathbf X)$ | random return vector; entries of $\Sigma$; $\operatorname{diag}(\sigma_i)^{-1}\Sigma\operatorname{diag}(\sigma_i)^{-1}$ | $\mathbf R_t$, $C$ stay sample |
| $a_i$, $\mathbf a$; $\mathbf b$ | coefficients of a combination (LM10's $\mathbf a$); constant vector of $M\mathbf X+\mathbf b$ | no bets in LM16; $\mathbf w$ sums to 1 |
| $J$ | number of rows of $M$ in (16.7), $\mathcal N_J$ | a count, as LM1's; $K$ stays §6's second matrix |
| $n$, $p$ | $\operatorname{Bin}(n,p)$'s trials and success probability: E8: $n=T$, $p=e^{-4.5}$ | no bets |
| $L$ | lower triangular, $\Sigma=LL^{\top}$, entries by (12.8) | declared; no leverage |
| $\beta$; $\varepsilon$ | $\sigma_{XY}/\sigma_X^2$; $Y-\mu_Y-\beta(X-\mu_X)$ in a normal pair | not LM12's $\hat{\boldsymbol\beta}$, $\hat{\boldsymbol\varepsilon}$ |
| $\mathcal S$; $d_t^2$ | set of values of $X$ an event conditions on; day $t$'s $d^2$, $=\lVert\mathbf z_t\rVert^2$ | $S$ is the SVD's |
| $\ell$ | $\varphi(k)/\Phi(-k)$, Deep Dive 3 only | declared there |

Counts $T$, $N$ (2, 5, 28; also $\chi^2_N$'s degrees of freedom), $J$, $n$, $m$; indices $i$, $j$, $t$. Bin day
counts are written in words (C15). Not used: $P$, events $A$, $B$, $\kappa$ ((5.11) with $z$), $\theta$ outside
(8.9), $q$, $U$, $V$ (LM7's two-asset variance is named in words), $c$.

**Motivating case** (box, about 120 words; X1):

> [!case] Do correlations rise in a crash?
> Semiconductor and FinancialInsurance are two of U28's sector indices. Over 4,382 daily returns, from 2 December 2008
> to 8 October 2026, their correlation is 0.5749 [A16-06]. Over 7–9 April 2025, the three sessions after the Qingming
> holiday, [[LM10]] found 0.851 [A16-07]. On 7 April both fell about 9.9% [A16-08], the pair's most extreme day of the
> sample [A16-09].
>
> [[LM12]] whitened the pair. In those coordinates 177 days [A16-10] lie outside the circle of radius 3. If the two
> returns were jointly normal with the sample's covariance matrix, about 49 would lie there [A16-11].
>
> So did the correlation rise in the crash, or would any sell-off look like this? What should a crash correlation be
> compared with, and how many extreme days does a normal model allow?

Resolution: "how many": E8 (mean 48.68, standard deviation 6.94 [A16-11], beside 177 without a ratio, C26) and X6.
"Compared with what": §7, the model's correlation under the same event. "Did it rise": E10; three days cannot say,
since 7 April is the sample's extreme (pair $d^2=72.05$, rank 1 [A16-09]), so X8 and X9 set the multi-day figures
beside the benchmark (AUTHORING §8).

**Sections** (prose words):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | samples measured co-movement; the model behind it; case, X1; roadmap; notation, hygiene | 330 |
| 2 | Joint, Marginal and Conditional Distributions {1} | X2; joint pmf, marginals, conditional pmf ((13.4), (13.5)); E1; joint density, double integrals (LM5's Fubini); E2; pitfall: margins do not fix the joint; 導讀; KC | 550 |
| 3 | Independence, Covariance and Correlation {1, 2} | (16.1); (16.2) by LM8's argument, equality case in Deep Dive 1 (probability one: [[LM13]]); E3; E4, X3; (8.9) is the empirical distribution's correlation; pitfall: zero correlation allows a joint loss (LM7's 2022); LM26 pointer; 導讀; KC | 620 |
| 4 | Sums, Portfolios and Covariance Matrices {3} | (16.3); uncorrelated suffices (LM3's increments); E5; $m$ independent days: mean $mg$, variance $m\sigma_r^2$ (LM5:523), on the TAIEX price index's log returns, $\bar r=0.05454\%$, $s_r=1.1392\%$ [A16-12], $m=245$ [A16-13]: 13.36% and 17.83% [A16-14]; shape → LM17; indicator counts: $np(1-p)$ (LM15) in one line; (16.4), PSD; pitfall: standard deviations do not add; KC | 560 |
| 5 | Conditional Expectation {4} | $\E[Y\mid X]$ (E2's); on an event, $\E[X\mathbf 1\{X\in\mathcal S\}]/\Pr(X\in\mathcal S)$ and (5.11); (16.5), proved for discrete $X$ from (13.8)'s partition (densities alike); (16.6); E6, X4; pitfall: equal weights (bin means average −0.0106% [A16-15]); 導讀; KC | 560 |
| 6 | The Multivariate Normal Distribution {5, 6} | definition (a constant is normal with variance 0); stated facts; (16.7), colouring, the LM12:527 distinction, whitening, rotation invariance; uncorrelated jointly normal ⇒ independent; (16.8); E7; $\chi^2_N$ defined: $Z_1^2+\dots+Z_N^2$, $N$ degrees of freedom, mean $N$ ($\E Z^2=1$), variance $2N$ ((14.6), (16.3)); (16.9) by whitening, $N=2$ by LM5's disc integral; contours: semi-axes $k\sqrt{\lambda_i}$ along $\mathbf q_i$ ((11.1), (11.3)), for the pair $\lambda_{1,2}=3.049$, 0.756 (%²) by (11.2) [A16-79]; X5, E8, X6, E9, X7; pitfall: normal marginals are not a normal vector; 導讀; KC | 830 |
| 7 | Correlation in a Crash {7} | the case's 0.851 and printed precedents; (16.10) from (16.8) (Boyer, Gibson and Loretan 1999; Forbes and Rigobon 2002); Deep Dive 3; X9; exceedance correlation (Longin and Solnik 2001; Ang and Chen 2002); X8; E10; widget; copulas, one sentence; pitfall: comparing with the full-sample correlation; 導讀; KC | 640 |
| 8 | Joint Distributions in Python {8} | X2 with the guard; $\hat\Sigma$ by `np.cov(..., rowvar=False, ddof=0)` (the default divides by $T-1$); $d_t^2$ by `cholesky`, `solve_triangular`; `stats.chi2.sf`; pitfall: `1 - cdf`; lab box | 220 |
| — | Summary (7 bullets) / Problems (12) / Solutions | | 130 / 380 / 480 |
| | **Total** | | **5,300** |

**Elements.** 10 examples; 7 knowledge checks (§2–§8); 5 中文導讀 (§2, §3, §5, §6, §7); 7 pitfalls (§2–§8). Deep Dive 1
(§3): $(\E[(X-\mu_X)(Y-\mu_Y)])^2\le\Var X\,\Var Y$ from $\E[(X-\mu_X-\eta(Y-\mu_Y))^2]\ge0$ for every real $\eta$,
and the equality case $\Pr(Y=\eta X+\zeta)=1$, $\eta\ne0$. Deep Dive 2 (§6): (16.7) for $N=2$ from $\mathbf
x=\boldsymbol\mu+L\mathbf z$ ($L$ maps the unit square onto its columns' parallelogram, area $\det L$ by [[LM9]],
so areas scale by $\det L=(\det\Sigma)^{1/2}$). Deep Dive 3 (§7): $\Var(Z\mid\lvert Z\rvert\ge
k)=1+k\varphi(k)/\Phi(-k)$ and $\Var(Z\mid Z\le-k)=1+k\ell-\ell^2$, by parts as LM5 found $\E Z^2$; at $k=2$,
$\ell=2.3732$ [A16-16], LM5's PP14. 導讀 terms (shared list): 聯合分布, 邊際分布, 條件分布, 機率質量函數, 聯合機率密度函數,
獨立 (never 線性獨立), 母體, 共變異數, 相關係數, 互不相關, 條件期望值, 雙重期望值定理, 全變異數法則 (law of total variance),
多變量常態分布, Mahalanobis 距離, 卡方分布, 自由度, 著色, 白化, 條件相關係數 (conditional correlation), 超越相關係數
(exceedance correlation), 隨機數; the book's own forms carry their English in every box. Knowledge checks:

- §2: $\Pr(\text{Semiconductor}\ge1\%\mid\text{FinancialInsurance}\le-1\%)=20/538=0.0372$ [A16-17].
- §3: $\Cov(X,\eta Y+\zeta)=\eta\Cov(X,Y)$; the correlation keeps its value for $\eta>0$, flips sign for $\eta<0$.
- §4: independent, variances 4 and 9: $\Var(X-Y)=13$, $\operatorname{Corr}(X,X+Y)=2/\sqrt{13}=0.555$ [A16-18].
- §5: $\E[Z\mid Z\le-2]=-2.3732$ (PP14) as a conditional expectation on an event.
- §6: 7 April 2025 tops S5's $d_t^2$ but ranks 15th among U28's (132.29; the largest, 209.55, is 5 May 2009) [A16-19].
  Why? 97.1% of 7 April's squared deviation lies along $\hat\Sigma$'s first eigenvector, the common move; on 5 May 2009
  sectors ran from −3.71% to +6.06% while the TAIEX price index rose 0.78% [A16-20].
- §7: the model's correlation given $\lvert X\rvert\ge\sigma_X$, $\rho=0.5749$, $\Var(Z\mid\lvert Z\rvert\ge1)=2.5251$
  [A16-21]: 0.745 [A16-22].
- §8: why `np.corrcoef` needs no `ddof` ((8.9)).

**Exhibits.**

- **X1 `case`** §1, table: $\hat\rho$ 0.5749; 7–9 April 0.851 ([[LM10]], from its printed returns −9.95, −3.99, −4.47
  and −9.89, +0.53, −5.61); 7 April −9.95% and −9.89%; pair $d^2$ 72.05, largest of 4,382; $d_t^2>9$: 177; model 48.7
  (1.11% [A16-23]), standard deviation 6.94. Source: FinMind `TaiwanStockPrice`, retrieved 11 October 2026; 524 closes on
  38 dates repaired from `TaiwanStockEvery5SecondsIndex`'s 13:30:00 values, none on these dates or the dates before;
  divisor $T$; `data/lm16_numbers.py`.
- **X2 `pmf`** §2, counts: Semiconductor (rows) × FinancialInsurance, bins $R\le-1\%$, between, $R\ge1\%$: 347, 478,
  34 / 171, 2,100, 248 / 20, 654, 330 [A16-24]; rows 859, 2,519, 1,004; columns 538, 3,232, 612 [A16-25]. Note: no return
  is exactly ±1% [A16-26]; probabilities are counts ÷ 4,382.
- **X3 `nextday`** §3, `line` (fmt n2): TAIEX price index (no dividends), U28 dates, 4,381 pairs [A16-27]; bins of
  $R_t$, $(\text{lower},\text{upper}]$, split at −3, −2, −1, 0, 1, 2, 3%, plotted at the bin's mean $R_t$; series: mean
  $R_{t+1}$ (far flatter) and mean $\lvert R_{t+1}\rvert$ (a V); dashed `hline` at 0.79% [A16-28], the overall mean
  $\lvert R_{t+1}\rvert$. Values (%) [A16-29]: days 60, 95, 389, 1,433, 1,770, 483, 112, 39; x −4.1416, −2.4494,
  −1.3877, −0.4033, 0.4305, 1.3867, 2.4174, 4.2277; mean $R_{t+1}$ −0.0614, 0.2245, 0.0037, 0.0039, 0.0730, 0.1366,
  0.2877, 0.4881; mean $\lvert R_{t+1}\rvert$ 2.0152, 1.2027, 0.9057, 0.8043, 0.6960, 0.6925, 0.9259, 1.3718. The note
  gives E4's correlations and the end bins' 60 and 39 days.
- **X4 `totalvar`** §5, table: FinancialInsurance by Semiconductor's bin (859, 2,519, 1,004 days): means −0.9505,
  0.0730, 0.8458; standard deviations 1.4122, 0.8426, 1.2201 (%, divisor the bin's days) [A16-30]; within 1.140, between
  0.342, total 1.482 (%², three decimals so the parts add), share 23.1% [A16-31]; the printed bin values reproduce these
  and their weighted mean, 0.0494% [A16-32], is FinancialInsurance's [A16-33]. Note: the normal model's share is
  $\hat\rho^2=0.3305$ [A16-34].
- **X5 `contours`** §6, `scatter`, fill-less `ellipses`: the pair's centred returns (% a day), 4,382 points; $\Sigma=
  \hat\Sigma$ (%²: 2.323354, 1.066603, 1.481729 [A16-35]) at `scale` 1, 2, 3, labelled 39.35%, 86.47%, 98.89%; 7 April a
  `point`. Note: model against data 39.35/56.16%, 86.47/87.95%, 98.89/95.96% [A16-36]; semi-axes $k\sqrt{\lambda_i}$,
  $\sqrt{\lambda_{1,2}}=1.746$, 0.869% [A16-79]; LM12's whitening exhibit ([[LM12]]) drew $k=3$ only; LM11's ellipse
  (another sample) cited by name.
- **X6 `chisq`** §6, two `line` charts with `y.type` `"log"` (counts 0.016 to 2,657.8), series "normal model, expected days" (dashed) and "U28 days". Pair, $x=k=1,\dots,5$, $d_t^2>k^2$: model
  share 60.65%, 13.53%, 1.11%, 0.0335%, 0.00037%; expected 2,657.8, 593.0, 48.7, 1.47, 0.016; actual 1,921, 528, 177,
  61, 25 [A16-37]. S5, $x=-\log_{10}(1-u)$ with `tickLabels` 50%, 90%, 99%, 99.9%, days above those $\chi^2_5$
  quantiles (4.35, 9.24, 15.09, 20.52): expected 2,191, 438.2, 43.8, 4.4; actual 1,411, 613, 291, 184 [A16-38]. Note:
  the means of $d_t^2$ are exactly 2 and 5 (12.9): only the shape is compared.
- **X7 `bridge`** §6, no numbers: sample result → population counterpart: LM7's average product → (16.2); (8.9) →
  $\rho_{XY}$; (8.6) → $\lvert\rho\rvert\le1$; LM7's two-asset variance → (16.3); (10.2), (10.3) → $\Sigma$, $\operatorname{Corr}
  (\mathbf X)$; (10.4)–(10.5) → $\Var(\mathbf w^{\top}\mathbf R)\ge0$; (12.9) → $L^{-1}(\mathbf X-\boldsymbol\mu)\sim
  \mathcal N_N(\mathbf 0,I)$, $\E d^2=N$; colouring → $\boldsymbol\mu+L\mathbf Z$. Note: under the empirical
  distribution the right column gives the left exactly (divisor $T$).
- **X8 `exceed`** §7, `line`: x in standard deviations, −2 to 2 (a fall of $k$ at $-k$); series: the pair's
  correlation on days both returns are at or below $\bar R_j-ks_j$, $k=0,0.25,\dots,2$; at or above $\bar R_j+ks_j$;
  the normal benchmark at $\rho=0.5749$, step 0.05; dashed `hline` 0.5749. Printed (n3), $k=0,1,2$: benchmark 0.332,
  0.229, 0.156 [A16-39]; falls 0.575, 0.465, 0.669 on 1,509, 228, 44 days [A16-40]; rises 0.430, 0.452, 0.541 on
  1,523, 170, 32 days [A16-41]. Note: full-sample moments, divisor $T$; every point has at least 30 days; the model
  expects 1,522.6, 306.3, 22.4 joint falls (probabilities 0.3475, 0.0699, 0.0051) [A16-42]; benchmark by numerical
  integration, in-sample.
- **X9 `condcorr`** §7, $k=1,2,2.5$. Semiconductor moves $k$ either way: 1,088, 223, 111 days; data 0.692, 0.788,
  0.811; model 0.745, 0.860, 0.894 [A16-43]. Falls $k$: 550, 105, 47; 0.474, 0.488, 0.485; model 0.299, 0.231, 0.205
  [A16-44]. Rises $k$: 538, 118, 64; 0.367, 0.429, 0.382 [A16-45]; model as falls. Note: (16.10) with
  $\Var(Z\mid\lvert Z\rvert\ge k)=2.5251$, 5.7464, 8.0569 and $\Var(Z\mid Z\le-k)=0.1991$, 0.1143, 0.0890 [A16-21].

**Widget `exceed`** — "What a normal model says about correlation in a crash." `Book.controls`: *Event* (both fall at
least $k$ (default); both rise; Semiconductor moves either way; Semiconductor falls), $\rho\in[0,0.95]$ step 0.0001,
$k\in[0,2.5]$ step 0.05. Chart: the model's correlation against $k$, the pair's values where at least 30 days, `vline`
at $k$, dashed `hline` 0.5749. Readouts: model correlation, probability and expected days in 4,382; the pair's
correlation and days ("fewer than 30 days" below that); $\hat\rho$. Model values from a grid `data/lm16_charts.py`
writes: joint falls at $\rho=0,0.01,\dots,0.95$ × $k=0,0.05,\dots,2.5$ (rises equal them by symmetry), interpolated in
$\rho$ through the four nearest points (cubic Lagrange, clamped at the ends; linear misreads last digits near 0.95);
largest error over the whole slider range below $10^{-5}$ (correlation), $2\times10^{-6}$ (probability), 0.01 days
[A16-46]. One-variable events: (16.10) with the grid's $\Var(Z\mid\text{event})$, probabilities by `Book.dist`'s
$\Phi$. Initial state (PDF): both fall, $\rho=0.5749$, $k=2$: model 0.156, probability 0.0051 (22.4 days); data 0.669
on 44 days. Note: "the model is fitted to the same days (in-sample)".

**Examples.**

- **E1** §2 [[eg:pmf]] (X2): $\Pr(\text{both}\le-1\%)=347/4{,}382=0.0792$; marginals 0.1960, 0.1228; product 0.0241,
  which independence would make equal; the joint frequency is 3.29 times it [A16-47] (descriptive, C26);
  $\Pr(\text{FinancialInsurance}\le-1\%\mid\text{Semiconductor}\le-1\%)=347/859=0.404$ against 0.1228; after a rise
  of 1% or more, $20/1{,}004=0.0199$ [A16-48].
- **E2** §2 [[eg:density]] (constructed): $f_{X,Y}=x+y$ on $[0,1]^2$; total 1; $f_X=x+\tfrac12$;
  $\Pr(X\le\tfrac12,Y\le\tfrac12)=1/8$; $f_{Y\mid X}=(x+y)/(x+\tfrac12)$; dependent. §5: $\E[Y\mid X=x]=(3x+2)/(6x+3)$,
  2/3 at 0, 5/9 at 1. P2: $\E X=7/12$, $\E X^2=5/12$, $\Var X=11/144$, $\E[XY]=1/3$, $\Cov=-1/144=-0.0069$,
  $\rho_{XY}=-1/11=-0.0909$ [A16-49].
- **E3** §3 [[eg:xsquared]] (constructed): $X$ uniform on $\{-1,0,1\}$, $Y=X^2$: $\Cov=\E X^3-\E X\,\E X^2=0$, yet
  $\Pr(Y=0\mid X=0)=1\ne\Pr(Y=0)=1/3$ [A16-50].
- **E4** §3 [[eg:nextday]] (TAIEX price index, U28 dates, 4,381 pairs): $\hat\rho(R_t,R_{t+1})=0.040$;
  $\hat\rho(\lvert R_t\rvert,\lvert R_{t+1}\rvert)=0.183$ [A16-27]; after the 306 days with $\lvert R_t\rvert\ge2\%$,
  mean $\lvert R_{t+1}\rvert$ 1.28%, after the others 0.75% [A16-28]. Independence would make both correlations zero
  and both means equal; [[LM26]].
- **E5** §4 [[eg:twoasset]]: the model whose annualized $\Sigma$ is LM10's printed 570.34, 261.83, 363.73 (%²)
  [A16-51]. 50/50: $\sigma_p^2=364.43$, 19.09%; $\Cov(R_1,R_p)=416.085$ (exact; print three decimals, not a rounded
  tie); $\Var(R_1-R_2)=410.41$, 20.26%, as LM10 printed [A16-52]. Under the empirical distribution: the sample values.
- **E6** §5 [[eg:totalvar]] (X4): within 1.140, between 0.342, total 1.482, share 23.1%; tower: weights 859, 2,519,
  1,004 over 4,382 give 0.0494% (never 0.0495%); a normal model's linear mean explains $\hat\rho^2=0.3305$ (§6).
- **E7** §6 [[eg:conditional]] Semiconductor falls 5%: inputs (daily, divisor $T$) means 0.0947%, 0.0494% [A16-33];
  standard deviations 1.5243%, 1.2173% [A16-53]; $\hat\rho=0.5749$. $\beta=0.4591$; $\E[Y\mid X=-5\%]=-2.29\%$;
  standard deviation $1.2173\sqrt{1-0.5749^2}=0.996\%$ (LM12's, lm12.md:436); $\Pr(Y\le-3\%\mid X=-5\%)=
  \Phi(-0.713)=0.238$ [A16-54]; unrounded inputs agree [A16-55]. Data: 17 days with Semiconductor in [−5.5%, −4.5%];
  FinancialInsurance mean −2.86%, standard deviation 2.00% (divisor the 17 days), 6 fell 3% or more
  [A16-56]: few days.
- **E8** §6 [[eg:outside]]: by (16.9) a day lies outside radius 3 with probability $p=e^{-4.5}=0.011109$ [A16-23];
  the count of $n=T=4{,}382$ independent indicators is $\operatorname{Bin}(n,p)$ ((15.1), (15.2)): mean 48.68, variance
  48.14, standard deviation 6.94 [A16-11]; data 177. No ratio, no test ([[LM21]]); the model's $\Sigma$ is the same
  days'.
- **E9** §6 [[eg:apr7model]]: S5's $d^2=89.30$ [A16-57]; a normal model with these moments gives
  $\Pr(\chi^2_5\ge89.30)=9.4\times10^{-18}$, once in about $4\times10^{14}$ years at $A=245.48$ [A16-58]; 184 days lie
  beyond the 99.9% quantile 20.52, a level it expects 4.4 times. The limit capped the day, so 89.30 understates it.
- **E10** §7 [[eg:crashcorr]]: 7–9 April put Semiconductor at −6.59, −2.68, −2.99 standard deviations [A16-59] (printed
  inputs: LM10's returns, E7's moments). Moves of 2 either way (223 days): 0.788 against the model's 0.860;
  at 1, 0.692 against 0.745: below the benchmark that Forbes and Rigobon's adjustment uses. Falls of 2 (105 days):
  0.488 against 0.231; joint falls of 2 (44 days): 0.669 against 0.156; joint rises (32): 0.541 against 0.156.
  One-sided events show higher correlations than the model's, falls more than rises, the direction Longin and Solnik
  (2001) report; three days cannot show it.

**Problems plan** (12; MC keys B, A, C, B; Python 12; the lab repeats 5–8, 10, 12). Data stems state U28 (2 December
2008 – 8 October 2026, $T=4{,}382$ daily price returns), divisor $T$, $A=245.48$ where used, "≤"/"≥" at each edge and
the rounding.

1. MC, from X2: $\Pr(\text{FinancialInsurance}\le-1\%\mid\text{Semiconductor}\le-1\%)$: A 0.079, **B 0.404**, C 0.645
   [A16-60]. A is the joint probability; C conditions the wrong way.
2. MC (constructed, E2): $\Cov(X,Y)$: **A −0.0069**, B 0.3333 ($\E[XY]$ alone), C 0 (independence assumed).
3. MC (constructed): $X\sim\mathcal N(0,1)$, $S=\pm1$ with probability 1/2, independent; $Y=SX$. A "independent,
   since uncorrelated and normal"; B "jointly normal, $\rho=0$"; **C "$Y$ normal, $\Cov=0$, yet dependent"**. A needs
   joint normality; B fails since $X+Y=0$ with probability 1/2, impossible for $\mathcal N(0,2)$.
4. (constructed) $\sigma_1=20\%$, $\sigma_2=15\%$, $\rho=0.5$, weights 0.6/0.4: $\sqrt{\Var(R_1-R_2)}=18.03\%$;
   $\Cov(R_1,R_p)=0.0300$; $\sigma_p=15.87\%$; $\operatorname{Corr}(R_1,R_p)=0.945$; wrong routes 5% ($\rho=1$) and 25%
   ($\rho=0$) [A16-61].
5. §4's model ($\bar r=0.05454\%$, $s_r=1.1392\%$, $m=245$) with adjacent days correlated 0.04, others not: factor
   $1+2(0.04)(244/245)=1.0797$, standard deviation 18.53% [A16-62]; wrong routes $245\times1.1392\%=279.1\%$ and
   $17.83\%\times1.0797=19.25\%$ [A16-63]. "A model, not data" (LM19).
6. The dependence in the spread (TAIEX price index, U28 dates, divisor each group's days): after the 306 days with
   $\lvert R_t\rvert\ge2\%$, $R_{t+1}$ had mean 0.2251%, standard deviation 1.8889%; after the other 4,075, 0.0496% and
   1.0570% [A16-64]. (16.5): 0.0619%; (16.6): within 1.288, between 0.002, total 1.290 (%²), share 0.16% [A16-65]; the
   spread is 1.79 times as large after a big day, which E4's 0.040 cannot see; wrong route: the equal-weight mean,
   0.13735% (exact) [A16-66].
7. E7's inputs, Semiconductor −3%: $\E[Y\mid X=-3\%]=-1.37\%$, standard deviation 0.996%, then from the printed
   −1.37: $\Pr(Y\le-2\%\mid X=-3\%)=\Phi(-0.6325)=0.264$; wrong routes: the unconditional standard deviation, 0.302;
   slope $\rho$, −1.73% [A16-67].
8. $d^2$ by hand, 5 August 2024: −9.48%, −6.93% [A16-68] (two decimals); E7's means; LM12's $L$ (1.5243, 0.6998,
   0.9960) [A16-69]: $z_1=-6.281$, $z_2=-2.594$, $d^2=46.18$, while unrounded inputs give 46.22 [A16-70];
   $e^{-23.09}=9.4\times10^{-11}$, about $4\times10^{-7}$ days in 4,382 [A16-71].
9. Proof: (a) $\lvert\rho\rvert\le1$ from $\Var(X/\sigma_X\pm Y/\sigma_Y)\ge0$, and when $\rho=1$; (b)
   $\Cov(M\mathbf X+\mathbf b)=M\Sigma M^{\top}$, so $\operatorname{Corr}(\mathbf X)$ is PSD.
10. (16.10) at 0.5749: 5.7464 gives 0.860, 0.1143 gives 0.231 [A16-72]; compare X9's 0.788, 0.488; which event raises
    the benchmark, and why?
11. MC: normal pair, $\rho=0.5749$, both fall 2 standard deviations: A 0.575 (no conditioning), **B 0.156**, C 0.860
    (two-sided, one variable).
12. Python: X2 with the guard and `Fraction`; pair $d_t^2$ by `np.linalg.cholesky`, `scipy.linalg.solve_triangular`;
    177 against `T * stats.chi2.sf(9, 2)` (48.68); `1 - stats.chi2.cdf(89.30, 5)` (0.0) against
    `stats.chi2.sf(89.30, 5)` (9.4e-18) [A16-73]; explain.

**Lab parts** (`build/make_lab16.py`; data: Volume II's `sectors_close_raw.csv` and `sectors_close_repairs.csv`,
`infer_schema_length=None`; no `taiex_tr.csv`; the notebook writes "LM18", never `[[LM18]]`):

1. Data: LM12's repair cell; returns, $T$, $A$; pair, S5, TAIEX price index. Free plan: listed closes dropped, $T=4{,}307$
   as in LM12's lab [A16-74]; windows without a listed close (7–9 April 2025) keep their values.
2. X2 with the guard and `Fraction`; E1.
3. E4, X3.
4. E5 (model value = sample value, asserted); §4's sum; P5.
5. X4, E6, the tower; P6.
6. E7; X5, X6; E8, E9; KC §6; P7, P8.
7. X8 with `quad`; X9; E10; P10.
8. P12.

Extension (stability check, full-sample standardization, no conclusion): 2008-12-02 → 2015-05-29, $T=1{,}610$,
$\hat\rho=0.6544$, 93 days with $d_t^2>9$; 2015-06-01 → 2026-10-08, $T=2{,}772$, 0.5564, 84 [A16-75]; X8 in each.

**Cross-module tags.**

- (16.1) $X_1,\dots,X_n$ are independent when $\Pr(X_1\le x_1,\dots,X_n\le x_n)=\prod_iF_{X_i}(x_i)$ for all $x_i$
  (for a joint pmf or density: it factorizes); then $\E[\prod_ig_i(X_i)]=\prod_i\E[g_i(X_i)]$ when each
  $\E\lvert g_i(X_i)\rvert<\infty$ (LM17, LM18).
- (16.2) $\Cov(X,Y):=\E[(X-\mu_X)(Y-\mu_Y)]=\E[XY]-\mu_X\mu_Y$, $\rho_{XY}:=\sigma_{XY}/(\sigma_X\sigma_Y)$, finite
  variances, $\sigma_X,\sigma_Y>0$; $\lvert\rho_{XY}\rvert\le1$, equality exactly when $\Pr(Y=\eta X+\zeta)=1$, $\eta\ne0$
  (LM17, LM20, LM23, LM27).
- (16.3) $\Var(\sum_ia_iX_i)=\sum_i\sum_ja_ia_j\sigma_{ij}$ when each $\E X_i^2<\infty$; uncorrelated:
  $\Var(\sum_iX_i)=\sum_i\Var X_i$ (LM17, LM18, LM19, LM20, LM33).
- (16.4) $\E\lVert\mathbf X\rVert^2<\infty$: $\Sigma:=\E[(\mathbf X-\boldsymbol\mu)(\mathbf X-\boldsymbol\mu)^{\top}]$;
  $\Cov(M\mathbf X+\mathbf b)=M\Sigma M^{\top}$; $\mathbf a^{\top}\Sigma\mathbf a=\Var(\mathbf a^{\top}\mathbf X)\ge0$
  (LM18, LM20, LM27, LM28, LM30, LM31, LM32).
- (16.5) $\E[\E[Y\mid X]]=\E Y$, $\E\lvert Y\rvert<\infty$ (LM20, LM24).
- (16.6) $\Var Y=\E[\Var(Y\mid X)]+\Var(\E[Y\mid X])$, $\E Y^2<\infty$ (LM20, LM23, LM24).
- (16.7) $\mathbf X$ is multivariate normal when every $\mathbf a^{\top}\mathbf X$ is normal (a constant counts, with
  variance 0), written $\mathcal N_N(\boldsymbol\mu,\Sigma)$, $\Sigma$ PSD; then $M\mathbf X+\mathbf b\sim\mathcal
  N_J(M\boldsymbol\mu+\mathbf b,M\Sigma M^{\top})$ for $M$ of size $J\times N$; $\boldsymbol\mu+L\mathbf
  Z\sim\mathcal N_N(\boldsymbol\mu,LL^{\top})$ for $\mathbf Z\sim\mathcal N_N(\mathbf 0,I)$; for $\Sigma$ PD the
  density is $(2\pi)^{-N/2}(\det\Sigma)^{-1/2}e^{-d^2/2}$ (LM18, LM20, LM32).
- (16.8) normal pair, $\sigma_X,\sigma_Y>0$: $Y=\mu_Y+\beta(X-\mu_X)+\varepsilon$, $\beta=\sigma_{XY}/\sigma_X^2$,
  $\varepsilon\sim\mathcal N(0,\sigma_Y^2(1-\rho^2))$ independent of $X$ (LM23, LM24).
- (16.9) $\chi^2_N$ is the law of $Z_1^2+\dots+Z_N^2$ for independent $\mathcal N(0,1)$ variables $Z_i$ ($N$ degrees
  of freedom; mean $N$, variance $2N$); $\mathbf X\sim\mathcal N_N(\boldsymbol\mu,\Sigma)$, $\Sigma$ PD:
  $d^2\sim\chi^2_N$; for $N=2$, $\Pr(d^2>k^2)=e^{-k^2/2}$ (LM21, LM32).
- (16.10) normal pair, $\sigma_X,\sigma_Y>0$, event $\{X\in\mathcal S\}$ with $\Pr(X\in\mathcal S)>0$ and
  $\Var(X\mid X\in\mathcal S)>0$:
  $\operatorname{Corr}(X,Y\mid X\in\mathcal S)=\rho\big/\sqrt{\rho^2+(1-\rho^2)\,\sigma_X^2/\Var(X\mid X\in\mathcal S)}$
  (Boyer, Gibson and Loretan 1999, Theorem 1) (LM32, LM35).

**Pitfalls to pre-empt.**

- *Conditions* are in the tags; also: "uncorrelated ⇒ independent" needs joint normality (P3); $e^{-k^2/2}$ is for
  $N=2$ only; adding variances does not make a sum normal (LM17).
- *Data traps.* Only `vol2_closes.parquet` (a raw read keeps copied closes, such as Semiconductor's on 5 June 2009;
  PITFALLS §3); LM10's 0.851 is computed from its printed returns (unrounded give 0.850 [A16-76]) and cited as LM10's;
  every edge uses the guard (`<= -0.01 + 1e-12`, `>= 0.01 - 1e-12`, `abs(R) >= 0.02 - 1e-12`), recounted with
  `Fraction` in the lab; points with fewer than 30 days are neither plotted nor quoted; 7 April 2025 was capped by the
  limit; say that 17, 44 and 32 days are few; $\hat\Sigma$ with `ddof=0` (or `bias=True`), never `np.cov`'s default.
- *Printed precision* (PITFALLS §7): E1's 3.29, E6, E7, E10, P6, P7, P8, P10 follow from their printed inputs; P7's
  $z$ (printed to four decimals, −0.6325, since $\Phi(-0.633)$ would give 0.263) and 0.302 use the printed −1.37; E10's 9 April becomes −3.00 from unrounded inputs [A16-80]; P8's solution
  names the unrounded 46.22.
- *Boundary creep.* No random numbers; no p-values, "significant", standard errors of data estimates, a count's
  distance from the model's mean in standard deviations, or a ratio offered as evidence (C26); no GARCH, regression
  standard errors, risk contributions, shrinkage, copulas, or laws beyond the normal and $\chi^2_N$.
- *Precedents.* Quote only printed text: in 2022 0050 and 00679B fell about 21–22% at a daily correlation of −0.06
  [A16-77]; all 28 sectors fell on 156 days and rose on 144 [A16-78]. LM7 prints no sentence about crises.

**Stage 4 for earlier modules.** Leads gain 16: lm01.md:6 (now [2, 3, 5, 6, 8, 19, 38]), lm03.md:6 (now [4, 5, 6,
7, 8, 10, 14, 37, 42, 46]), lm05.md:6 (now [12, 14, 15, 17, 18]), lm07.md:6 (now [8, 9, 10, 11, 12, 27, 28, 29,
43]), lm09.md:6 (now [10, 11, 12, 23, 27, 28, 43]). lm08, lm10, lm11 and lm12 already list 16.

## LM17 Law of Large Numbers and Central Limit Theorem

Stage 1 brief, revised after the fresh check and the editor's decisions of 2026-10-18 (`plans/vol-3.md`). Each number
carries its anchor ID at its first appearance; `data/vol3_anchors_lm17.py` prints them all.

**Prereq:** `[1, 3, 4, 5, 13, 14, 15, 16]`. LM1: (1.1), (1.6), (1.12), $A$. LM3: (3.3); the +2%/−1% bet and its $g$
(lm03.md:360–363); the +100%/−50% pitfall (lm03.md:367–368); the quadratic-variation Deep Dive (lm03.md:545). LM4: the
binary bet (lm04.md:296–304); (4.4), (4.7); the Kelly bet (lm04.md:345); zero growth at a fixed position (lm04.md:366);
"about twice the Kelly leverage" (lm04.md:199); the standard error and its normal quantile stated without proof
(lm04.md:541). LM5: $\varphi$, $\Phi$, (5.5), (5.9); the tails exhibit (lm05.md:337–348); lm05.md:350; the kurtosis
pitfall (lm05.md:366–369); (5.12) and the 0050 lognormal (lm05.md:511–523). LM13: (13.3) equally likely outcomes, the
empirical model; (13.6), (13.7) independent events and trials; (13.12) $\hat F$; (13.13) and "iid"; events of
probability zero (Deep Dive 1). LM14: (14.1) $\E[\mathbf 1_{\mathcal A}]=\Pr(\mathcal A)$, (14.3), (14.4)
$\Var(\eta X+\zeta)$, (14.5) $\operatorname{Kurt}$, (14.6) $\E Z^4=3$, (14.8) Chebyshev, (14.10) strict Jensen, (14.12);
TR23's daily Jensen gap (E10), the gap at $f=2$ (KC §7), $A\bar r$ (E4), the daily excess kurtosis of $R$ (E6). LM15:
(15.1)–(15.2), (15.6), (15.7); (15.9) at $\nu=1$, the Cauchy density; E10 (TR23's kurtosis of $R$ around 7 April 2025,
top-ten shares); E6 (the lognormal fitted to 23 annual growth factors). LM16: (16.1) independence and the product rule;
(16.2) covariance and correlation; (16.3) the sum rule; uncorrelated against independent.

**Leads:** `[18, 19, 20, 21, 22, 26, 34, 36, 38, 41, 42, 45]`: tag users and pointer targets (LM18 cites (17.1)
and (17.4)–(17.6)).

**Forward links honoured.**

| Earlier text | Promise | Kept in |
|:--|:--|:--|
| lm04.md:296, 300 | iid trials; $j/N\to p$ | §2 (iid from LM13); §3, (17.2) for frequencies; LM4's $N$ is $n$ |
| lm04.md:302 | (4.7) as the limit of per-trade log growth | §4: (17.3), (4.7) its two-outcome case |
| lm04.md:304 | "with probability one (Breiman 1961; Thorp 2006)" | §3: the strong law, Deep Dive (paths); §4 |
| lm04.md:541 | $s/\sqrt T$ without proof; the normal quantile | §2: $\Var\bar X_n=\sigma_X^2/n$ (model); §5: why normal; LM20 keeps $s/\sqrt T$ |
| lm05.md:512, 523 | annual log growth "is normal"; independent days | §6: the CLT as the reason, with conditions |
| lm05.md:346, 350 | Cauchy mean "does not exist"; stable laws | §8: E10; the law holds, the $\sqrt n$ CLT fails (stated) |
| lm05.md:366–368 | a kurtosis that never settles | §8: X9, citing LM15's 4.25 → 4.94 (lm05.md:369 is LM15's) |
| lm03.md:367–368 | "wealth goes nowhere" | §4: E3, X3 |
| lm03.md:545 | squared increments, variance $\to0$ | §3: "a weak-law argument"; Brownian motion stays LM36's |
| syllabus.yaml:51 | "Why the median path, not the mean path, is what you live through." | §4, §6, with the honest rate |

**Outcomes** ("After this module you should be able to:"):

1. calculate the mean and variance of sums and averages of independent random variables, and explain why the standard deviation of an average falls like $1/\sqrt n$
2. derive the weak law of large numbers from Chebyshev's inequality, state the conditions of the weak and strong laws, and apply them to frequencies and to LM4's binary bet
3. explain why realized log growth converges to $g=\E[\ln(1+R)]$ while expected wealth compounds at $\ln(1+\mu)$, and why the chance of ending above expected wealth tends to zero
4. state the central limit theorem with its conditions, and apply the normal approximation to binomial counts
5. compute the median, quantiles and loss probability of wealth under the lognormal approximation, with and without leverage
6. measure how fast sums of TAIEX log returns approach the normal shape, and explain how dependence slows the approach
7. identify when the laws fail (no mean, infinite variance, infinite fourth moment, dependence) and what each failure does to a sample statistic
8. compute running averages, $m$-day sums and normal approximations in Python, counting threshold days with the book's guard

**Owns.** $S_n$, $\bar X_n$ of iid draws; $\E\bar X_n=\mu_X$, $\Var\bar X_n=\sigma_X^2/n$ (17.1) from (16.3) and (14.4).
Convergence in probability; the weak law by Chebyshev (17.2), with uncorrelated draws of common mean and variance
sufficing. Convergence with probability one for a path; the strong law stated without proof (iid,
$\E\lvert X\rvert<\infty$; Wasserman 2004, Theorem 5.18). Frequencies converge to probabilities. Growth: (17.3);
$\E W_m=W_0(1+\mu)^m$ and $\Pr(W_m>\E W_m)\to0$ (17.4); mean path against median path, with the rate stated; leverage on
TR23 (hypothetical). Convergence in distribution; the CLT (17.5) stated without proof, with an mgf sketch; the normal
approximation to the binomial and the continuity correction. The lognormal approximation of $W_m$ (17.6). The excess
kurtosis of iid sums (17.7); TR23's kurtosis of $m$-day log-return sums, the lag correlations of $\lvert r\rvert$ and
X9's running kurtosis of $R$, a law that does not settle. When the laws fail.

**Leaves.** Random generation, Monte Carlo error → LM18 (no simulated path here). The $\sqrt T$ rule in data, sample
moments as estimators, $T$ against $T-1$ → LM19. Standard errors with $s$, confidence intervals → LM20. Tests of a
frequency → LM21. Bootstrap inference, block bootstraps → LM22. Volatility models → LM26. Drawdown statistics → LM32.
Tests on later data → LM34. Brownian motion → LM36. GBM's exact lognormal law → LM38. General Kelly, log utility → LM41;
continuous-time Kelly → LM42; drawdown control → LM44. Not in the book (a sentence each): the generalized CLT; ergodic
theorems; error bounds for the normal approximation.

**Uses before taught** (one sentence each in the text):

- §2 standard error: "$\sigma_X/\sqrt n$ is the average's standard error; [[LM4]] used it with $s$, and [[LM20]] derives
  that estimate."
- §2 pitfall: "Whether daily variances add up over months is a question about data, which [[LM19]] examines."
- §3 simulation: "[[LM18]] draws such paths and measures their error; here every probability is exact or an analytic
  approximation."
- §4 resampling: "The iid bootstrap of [[LM18]] has exactly this mean path."
- §4 Kelly: "General bets and what maximizing the median path assumes are [[LM41]]'s and [[LM42]]'s subjects."
- §6: "[[LM38]] derives the lognormal law exactly for geometric Brownian motion"; "more and smaller steps turn this
  random walk into Brownian motion ([[LM36]])."
- §7: "Sample kurtosis and its divisor are [[LM19]]'s subject; here the divisor is $T$, as in [[LM5]]"; "volatility that
  changes over time is modelled in [[LM26]]."
- §5 Deep Dive: $M_X(t):=\E[e^{tX}]$, defined there, $t$ declared as its argument.

**Data role.** TR23 only, from `data/processed/vol3_taiex.parquet` (`data/vol3_series.py`; FinMind
`TaiwanStockTotalReturnIndex`, data_id TAIEX, retrieved 2026-10-18): 5,850 closes [A17-01], 2003-01-02 → 2026-10-08;
$T=5{,}849$ [A17-02] simple returns from 2003-01-03; 8,680 calendar days [A17-03] $=23.7645$ years [A17-04]; $A=246.12$
[A17-05]. Log returns $r_t=\ln(1+R_t)$ for every sum. No exact zero return (`Fraction` on the two-decimal closes): 3,205
up days, 2,644 down days [A17-06]. Calendar years 2003–2025, 2003 from its first close (2 January 2003), only for the
loss-year count and the daily model refitted to them for LM15's comparison (E8). No U28, no 0050 recomputation, no new
data, no random numbers (no seed). Scripts: `data/lm17_numbers.py` (asserts every printed value, recounts with
`Fraction`, flags values near a rounding boundary), `data/lm17_charts.py` (X1, X2, X4, X5, X7, X9, widget block); lab
file `taiex_tr.csv`.

**Hygiene declaration.** *Descriptive:* TR23's path in X1, X2's running frequency, X7's TR23 bars, X9, lag correlations,
calendar-year losses. *In-sample:* the iid model on TR23's empirical law ($\mu=\bar R$, $g=\bar r$, $\sigma_r=s_r$),
also refitted to 2003–2025, and its lognormal approximation (X6, E4, E8, widget, X1's model paths, X2's band, X7's iid
bars); $\bar g(f)$ and the empirical Kelly leverage (X4, E5); the fitted median path ends at the realized wealth by
construction, as the text says. *Model, not a forecast:* every $\Pr(W_m<W_0)$, $\Pr(W_m>\E W_m)$ and quantile of $W_m$;
the constructed bets. *Stability check:* 20-day kurtosis by limit regime (X7 note, lab extension). *Hypothetical:*
leveraged TR23 paths. Local note: "Every TAIEX figure describes the total-return index, 3 January 2003 to 8 October 2026
(5,849 daily returns), except the calendar-year comparison, 2003–2025 (2003 from its first close, 2 January 2003). The
wealth model draws days independently from the sample's own returns: in-sample, a model, not a forecast. Leveraged paths
are hypothetical: daily rebalancing, free borrowing, no costs. Nothing is tested on later data ([[LM34]])."

**Notation.** AUTHORING §6 and the Volume III table. Used: $R$, $r$, $\mu$, $\sigma$, $\bar R$, $s$, $\bar r$, $s_r$
(divisor $T$), $g$, $\sigma_r$, $G$, $W$, $W_0$, $f$, $f^*$, $A$, $T$, $t$, $\tau$, $p$, $q=1-p$, $b$, $a$ (LM4's bet),
$\varphi$, $\Phi$, $\Phi^{-1}$, $\Pr$, $\E$, $\Var$, $\operatorname{Kurt}$, $X$, $Y$, $Z$, $x$, $z$, $\mu_X$,
$\sigma_X$, $\mathcal A$, $\mathbf 1_{\mathcal A}$, $\mathbf 1\{\cdot\}$, $\hat F$, $R_{(1)}$, $\mathcal N$,
$\operatorname{Bin}$, $t_\nu$, iid, $n$, $\bar X_n$, $S_n$, $j$, $m$, $\eta$, $\zeta$. Generic results ((17.1), (17.2),
(17.5), (17.7)) use $\mu_X$, $\sigma_X$; for draws of a return they are $\mu$, $\sigma$. $\bar g(f)$ only as LM4's
(4.4), with $\bar g(1)=\bar r$ said once. $T=5{,}849$ is the data count; a horizon of $\tau$ years is
$m=\operatorname{round}(A\tau)$ sessions ($m=1{,}231$ for five years [A17-07]), and $W_m$ is wealth after it. Local:

| Symbol | Meaning | Check |
|:--|:--|:--|
| $j$; $n$ | wins among $n$ trials; "[[LM4]]'s $N$ is $n$ here" | Volume III's $j$, $n$ |
| $Y_i=X_i-\mu_X$ | centred draws | capitals |
| $\varepsilon$ | a tolerance in (17.2), $\varepsilon>0$ | declared (LM16's is a residual) |
| $\delta$, $\delta(f)$ | $\ln(1+\mu)-g>0$, [[LM14]]'s daily Jensen gap: mean path's log rate minus median path's; at leverage $f$ | new |
| $g^*$ | LM4's Kelly growth per trade, $\tfrac12\ln1.5+\tfrac12\ln0.75$ (E6, X5) | LM4's (lm04.md:345) |
| $\alpha$ | a power tail's index, $\Pr(X>x)\propto x^{-\alpha}$ (X8's Pareto) | LM5's letter |
| $\hat p$ | TR23's up-day frequency | hatted sample statistic |
| $s_r(f)$ | standard deviation (divisor $T$) of $\ln(1+fR_t)$ | follows $s_r$ |
| $M_X(t)$ | mgf, §5 Deep Dive only | declared there |

Not used: $\hat\mu$, $\kappa$, $\lambda$, $\theta$, $P$, $E$, $q$ for a quantile, $k$, $N$, $L$, $B$, $d^2$, $\rho$
(correlations in words).

**Motivating case: "Compounding the average day."** (box, about 110 words)

> From 2 January 2003 to 8 October 2026 the TAIEX total-return index, with dividends reinvested and no costs, rose
> 25.2-fold [A17-08] over 5,849 trading days. Its average daily return was 0.06251% [A17-09]. Compounding that average
> 5,849 times gives 38.7 times the start [A17-10], against the index's 25.2. Now apply a constant leverage $f$ to the
> same days, rebalanced daily with free borrowing (a hypothetical). Compounding the average day then promises more for
> every $f$: 2.2 million times the start at $f=4$ [A17-11]. Realized wealth grows only up to $f=4.14$, to 2,147 times
> [A17-12], and is back at the start at $f=8.04$ [A17-13]. Which path does an investor live through, and why does the
> average day overstate it?

The box prints $\bar R=0.06251\%$ because 0.0625% gives 38.65 [A17-14]. Resolved: (a) which path: §4, (17.3), E4 (the
daily Jensen gap $\delta=0.7316$ bp [A17-15] is [[LM14]]'s; over 5,849 days it is 0.4279 log points, a factor 1.534
[A17-16]) and §6; (b) why the average overstates: (17.4), E3, X3 (rare paths carry the mean; strict Jensen); (c)
leverage: E5, X4, widget; (d) the chance of finishing above the mean path: E4, X6 (it tends to zero, slowly: 0.32 over
the sample at $f=1$, 0.028 at $f^*$ [A17-17], iid model).

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | averages settle, sums turn normal; case + X1; roadmap; notation and hygiene notes | 380 |
| 2 | Sums and Averages of Independent Variables {1} | two independent trades of LM3's bet ((13.6)): averages 2%, 0.5%, 0.5%, −1%; mean 0.5%, variance 1.125 (%²), half of one trade's 2.25 [A17-18]; iid; $\E S_n$, $\Var S_n$ cited from (16.3); (17.1); standard error named; E1; pitfall: correlated days do not average out ($\Var S_n=n^2\sigma_X^2$ for identical copies) | 470 |
| 3 | The Law of Large Numbers {2} | a fair coin: exact $\Pr(\lvert j/n-\tfrac12\rvert\ge0.1)$ = 0.7539, 0.05689, $2.7\times10^{-10}$ at $n$ = 10, 100, 1,000 against Chebyshev's $25/n$ = 2.5, 0.25, 0.025 [A17-19]; convergence in probability; (17.2), three-line proof; the uncorrelated remark; indicators ((14.1)) and LM4's $j/n\to p$; E2; X2; the strong law; Deep Dive; LM3's sentence; pitfall: gambler's fallacy | 600 |
| 4 | Growth: the Mean Path and the Median Path {3} | E3, X3; $\ln(W_m/W_0)=\sum r_t$; (17.3), conditions, (4.7) as its two-outcome case, Breiman's comparison of fractions; $\E W_m$ by LM16's product rule; strict Jensen; (17.4) proved from (17.2); E4; E5, X4; pitfall: the law fixes the rate, not the level | 620 |
| 5 | The Central Limit Theorem {4} | X5; convergence in distribution; (17.5), conditions, stated without proof; Deep Dive; normal approximation to the binomial, continuity correction; E6; E7; pitfall: a theorem about sums, poor in relative terms far in the tail | 560 |
| 6 | Wealth Is Approximately Lognormal {5} | $\ln W_m\approx\mathcal N(mg,m\sigma_r^2)$; median, quantiles, (17.6); LM5's annual normality explained, its 0050 median 1.2130 and mean 1.2358 cited [A17-20]; E8 with LM15's annual fit on 2003–2025, X6; widget; LM36, LM38; pitfall: a fitted median that matches the sample is not evidence | 520 |
| 7 | How Fast the Normal Arrives on TAIEX {6} | (17.7) by expanding $\E[(Y_1+\dots+Y_m)^4]$; $\operatorname{Bin}(m,\tfrac12)$ check; E9, X7; correlated squares; pitfall: overlapping windows are dependent, non-overlapping ones depend on the start | 460 |
| 8 | When the Laws Fail {7} | X8; no mean: E10, averages converge with probability zero (Durrett 2019, Theorem 2.3.8); infinite variance: the law holds, the $\sqrt n$ CLT fails, stable limits (Mandelbrot 1963); infinite fourth moment: X9 with 0050's 5.84 → 7.63 and shares 62.8% and 14.1% [A17-21] and TR23's 35.0% and 6.7% ([[LM15]]) [A17-22]; dependence; changing distributions; pitfall: a finite sample kurtosis shows no finite fourth moment | 490 |
| 9 | The Laws in Python {8} | running means; $m$-day sums; `stats.binom`, `stats.norm`; `stats.kurtosis` defaults; the guard; lab box | 200 |
| — | Summary (7) / Problems (11) / Solutions | | 140 / 380 / 480 |
| | **Total** | | **5,300** |

**Elements.** 10 examples (E1 §2; E2 §3; E3–E5 §4; E6, E7 §5; E8 §6; E9 §7; E10 §8). Knowledge checks:

- §2: four independent days with $\sigma=1.2\%$: $\sqrt{\Var\bar X_4}=0.6\%$; four identical copies, 1.2% [A17-23].
- §3: fair coin: the head count's standard deviation $\sqrt n/2$ grows (5 at $n=100$, 50 at 10,000) while the
  frequency's falls (0.05, 0.005) [A17-24].
- §4: LM3's bet, 1,000 trades: mean path $1.005^{1000}=146.58$, median path $e^{1000\times0.0048761}=131.12$ [A17-25],
  with LM3's $g=0.48761\%$ [A17-26].
- §5: at least 60 heads in 100 flips: continuity-corrected normal 2.87%, exact 2.84% [A17-27].
- §6: one-year loss probability at $f=2$ from $\bar g(2)=0.095571\%$, $s_r(2)=2.4288\%$ [A17-28], $m=246$ [A17-29]:
  $\Phi(-0.6172)=26.86\%$ [A17-30], against 23.74% at $f=1$ [A17-31].
- §7: daily excess kurtosis 5.428 [A17-32] needs $m\ge11$ [A17-33] for an iid sum's to fall below 0.5; TR23's 10-day
  value is 3.02 [A17-34].
- §8: with a power tail like lm05.md:350's, the running mean and variance settle, the running kurtosis does not; TR23's
  moved from 4.25 to 4.94 on 7 April 2025 [A17-35] ([[LM15]]'s E10).
- §9: `np.cumsum(r) / np.arange(len(r))` divides the first sum by zero and every later one by $n-1$.

中文導讀 in §3 (大數法則, 弱大數法則, 強大數法則, 依機率收斂, 幾乎必然收斂 (almost sure convergence), the text saying
"with probability one, or almost surely"), §4 (中位數, 期望值), §5 (中央極限定理, 依分布收斂, 常態逼近, 二項分布), §6
(對數常態分布, 分位數) and §8 (獨立同分布, 峰態, 超額峰態); also 標準誤, 樣本平均數, 母體, 賭者謬誤 (gambler's fallacy).
賭者謬誤 (樂詞網 statistics) and 期望值 are on the shared list; 獨立同分布 is 樂詞網's mathematics form (the
statistics listing writes 獨立且相同分布隨機變數 for the noun phrase), printed with its English. Other terms stay English unless found on 樂詞網. Deep Dives: §3 "What
'with probability one' adds": [[LM13]] says what an event of probability zero is; the strong law speaks about whole
paths (the paths along which $j/n\to p$ have probability one; the all-heads path exists with probability zero), the weak
law about each $n$. §5 "Why sums become normal": iid with an mgf near 0,
$[M_Y(t/(\sigma_X\sqrt n))]^n=[1+t^2/(2n)+o(1/n)]^n\to e^{t^2/2}$, using (3.3) to extend (1.6) to $x_n\to x$; that the
mgf's limit fixes the limit law is stated without proof, as Grinstead and Snell (1997, §10.3) and Blitzstein and Hwang
(2019, Theorem 10.3.1) do.

**Exhibits.**

- X1 `case` (`line`, §1): x date; y log (×). TR23 wealth $P_t/P_0$, the mean path $(1+\bar R)^t$, the fitted median path
  $e^{t\bar r}$. End labels 25.20, 38.66, 25.20 [A17-36] (38.66 needs $\bar R=0.062505\%$ [A17-37]; 0.06251% gives
  38.67). Note: the two model paths are in-sample; the median path ends at 25.20 by construction. Source: FinMind
  `TaiwanStockTotalReturnIndex` (TAIEX), retrieved 2026-10-18; Computations: `data/lm17_numbers.py`.
- X2 `upfreq` (`line`, §3): x $\log_{10}n$, $n=20,\dots,5{,}849$, `tickLabels` 20, 50, 100, 250, 1,000, 2,500, 5,849; y
  0.40–0.65 (`fmt: "n4"`, `tfmt: "n2"`). Running frequency of up days ($R_t>10^{-12}$); band
  $\hat p\pm2\sqrt{\hat p(1-\hat p)/n}$ labelled "iid model, $p$ fitted to the whole sample"; `hline` $\hat p$. Values:
  0.5163 at $n=246$, 0.5378 at 1,231, $\hat p=0.5480$ at 5,849 [A17-38]; band half-width 0.0130 at 5,849 [A17-39]. Note:
  in-sample; the band is a model property and no exits are counted.
- X3 `doubling` (table, §4): ten rounds of +100%/−50%: wins $j$, $W_{10}/W_0=2^{2j-10}$, $\binom{10}{j}$, probability
  and contribution to $\E W_{10}$ (4 dp). Totals row: 1,024 paths and $\E W_{10}=9.3132$ only (no probability total);
  rows $j\ge7$ (probability $11/64=0.1719$) carry 8.1875, 87.9% [A17-40].
- X4 `leverage` (`line`, §4): x $f$ from 0 to 10.31; y annual log rate (`pct2`), clipped at −100%. $A\bar g(f)$ and
  $A\ln(1+f\bar R)$. Points: $f=1$ (13.58%, [[LM14]]'s; 15.38%), $f^*=4.14$ (32.28%), zero growth 8.04 [A17-41]; dashed
  `vline` $1/\lvert R_{(1)}\rvert=10.31$ (7 April 2025, $R_{(1)}=-9.6997\%$) [A17-42]. Note: hypothetical; $A=246.12$.
- X5 `binom` (`line`, §5): x 25–75 (`fmt: "n1"`, `tfmt: "n0"`); y probability (`n4`). $\operatorname{Bin}(100,\tfrac12)$
  as a `step` histogram over $[j-\tfrac12,j+\tfrac12]$ and the density $\varphi((x-50)/5)/5$; band $x\le41.5$ and a
  dashed `vline` at 41.5 labelled "j ≤ 41: loss at f* = 25" (LM4's $f^*=25$ and $g^*=5.889\%$ [A17-43]). Note: exact
  0.04431, normal 0.04464, continuity-corrected 0.04457 [A17-44].
- X6 `lognormal` (table, §6): iid model on TR23's empirical law, $f=1$. Rows one year ($m=246$), ten years ($m=2{,}461$)
  [A17-45], the sample ($m=5{,}849$, 23.76 years). Columns: median $e^{m\bar r}$; mean path $(1+\bar R)^m$; 5% and 95%
  quantiles $e^{m\bar r\mp1.645\,s_r\sqrt m}$ (1.645 [A17-46]); $\Pr(W_m<W_0)$; $\Pr(W_m>\E W_m)$. Values: 1.1454,
  1.1662, 0.8381, 1.5653, 23.74%, 46.2% [A17-47]; 3.89, 4.65, 1.45, 10.44, 1.19%, 38.2% [A17-48]; 25.20, 38.66, 5.49,
  115.6, 0.02%, 32.2% [A17-49]. Descriptive line: 5 of the 23 calendar years 2003–2025 (2003 from its first close, 2
  January 2003) lost (2008, 2011, 2015, 2018, 2022) [A17-50], against 6.10 expected under the daily model refitted to
  those years (E8). Two decimals and 115.6 for those quantiles: the printed $\bar r=0.055170\%$, $s_r=1.2107\%$ [A17-52]
  give 1.4473, 5.4945, 115.59, the unrounded 1.4474, 5.4949, 115.58.
- X7 `kurtm` (`bar`, §7): $m$ = 1, 2, 5, 10, 20, 60. TR23 overlapping $m$-day log-return sums (`fmt: "n2"`): 5.43, 5.04,
  3.63, 3.02, 2.29, 3.20 [A17-53]; iid $5.428/m$ (`fmt: "n3"`): 5.428, 2.714, 1.086, 0.543, 0.271, 0.090 [A17-54]. Note:
  at $m=1$ both bars are the daily value; all $5{,}849-m+1$ windows; daily simple returns have excess kurtosis 5.27 ([[LM14]]) [A17-55]; non-overlapping 20-day
  windows give 0.69–4.49 by starting day (2.40 from the first return, 292 windows) [A17-56], and 60-day ones 0.42–7.22
  (2.76 from the first return, 97 windows) [A17-94], so the rise from 2.29 to 3.20 is evidence neither way; stability
  check: 20-day 1.96 before June 2015 and 2.66 after, against iid 0.17 and 0.42 from each regime's daily log-return
  value 3.44 and 8.41 [A17-57].
- X8 `failures` (table, §8): normal; $t_3$; Pareto $\alpha=1.5$; Cauchy; identical copies $X_t=X_1$ × mean, variance,
  fourth moment (as lm05.md:337–348), law of large numbers, CLT with $\sigma_X/\sqrt n$, sample kurtosis settles.
- X9 `runkurt` (`line`, §8): x date from the 246th return (2003-12-29); y 0–6 (`n2`). Running excess kurtosis of daily
  simple returns (divisor = days so far); `hline` 5.27 ([[LM14]]'s full-sample value); `point`s 4.25 (2025-04-02) and
  4.94 (2025-04-07), [[LM15]]'s E10. Note: the running annualized variance of $R$ (centred on the running mean, same
  divisor) stays between 0.0326 (2024-04-12) and 0.0580 (2004-06-23) after the first year and ends at 0.0359 [A17-58]:
  the second moment settles, the fourth does not.

**Widget `wealth` — "Mean, median and the range of wealth."** `Book.controls`: leverage $f$ (0.25–8, step 0.25, initial
1); horizon $m$ sessions (1–9,845 = 40 years [A17-59], step 1, initial 5,849), with $\tau=m/A$ shown. `line` chart, x
years 0–40, y log $10^{-2}$–$10^{6}$ (clipped; readouts give values): mean path $(1+f\bar R)^m$, median
$e^{m\bar g(f)}$, band $e^{m\bar g(f)\mp1.645\,s_r(f)\sqrt m}$, `hline` 1, `vline` at the horizon. Readouts: the four
values, $\Pr(W_m<W_0)\approx\Phi(-\bar g(f)\sqrt m/s_r(f))$, $\Pr(W_m>\E W_m)\approx\Phi(-\sqrt m\,\delta(f)/s_r(f))$,
$m$, $\tau$; $\Phi$ from `Book.dist`. Initial state (PDF): X6's sample row. At $m=1{,}231$ it reads 5.49% [A17-60],
[[LM18]]'s case. Data block `chart-lm17-wealth`: $\bar R$, $A$, the grid $(f,\bar g(f),s_r(f))$, $f=0.25,\dots,8$
($f=1$: 0.00055170, 0.01210727; $f=2$: 0.00095571, 0.02428841 [A17-61]). The mean path is the exact iid mean, not
$e^{m(\bar g+s_r^2/2)}$ (38.69 against 38.66 at $f=1$; $2.19\times10^{13}$ against $4.68\times10^{12}$ at $f=8$
[A17-62]); the note says which.

**Examples** (results recomputed from the printed inputs):

- E1 §2: LM3's bet has $\sigma=1.5\%$; $\sqrt{\Var\bar X_n}=1.5\%/\sqrt n$: 0.15% at $n=100$, 0.015% at 10,000; $n\ge36$
  gives at most 0.25%, half the 0.5% edge [A17-63].
- E2 §3: a frequency within one point of $p$ with probability at least 95% needs $n\ge0.25/(0.01^2\times0.05)=50{,}000$
  [A17-64] by Chebyshev, worst case $p=\tfrac12$. A model property; no TR23 margin.
- E3 §4 (X3): $\E W_{10}=1.25^{10}=9.3132$; median 1 ($\Pr(W_{10}=1)=63/256=0.2461$); $\Pr(W_{10}>\E W_{10})=11/64$,
  87.9% of the mean; $\Pr(W_{10}<1)=193/512=0.3770$ [A17-65]. At 100 rounds: $\E W=4.91\times10^9$,
  $\Pr(W>\E W)=0.00044$, $\Pr(W<1)=0.4602$ [A17-66]. Peters (2019)'s coin pays +50% or −40%; expected wealth grows by
  1.05 a round while log wealth falls by $\tfrac12\ln0.9=-0.0527$, a typical factor $\sqrt{0.9}=0.949$ [A17-67]: the
  average over investors against one investor's growth over time.
- E4 §4, the case: $(1+\bar R)^{5849}=38.66$ ($\bar R=0.062505\%$) against 25.20. Per day $\delta=0.7316$ bp ([[LM14]]'s
  E10; deriving it needs six significant figures, $\bar R=0.0625051\%$, $\bar r=0.0551696\%$ [A17-68]); × 5,849 =
  0.4279, $e^{0.4279}=1.534=38.66/25.20$. Under the iid model with $m=T$,
  $\Pr(W_m>\E W_m)\approx\Phi(-\sqrt{5849}\times0.7316\,\text{bp}/1.2107\%)=\Phi(-0.462)=0.32$ (normal approximation,
  forward to §5–§6); 5% needs about 74,000 days, about 300 years [A17-69]; Chebyshev's $\sigma_r^2/(T\delta^2)=4.68$
  [A17-70] says nothing. A typical investor lives the median path, yet over 23.8 years the mean path is still beaten
  with probability 0.32.
- E5 §4 (X4, hypothetical): $W_T$ = 25.20, 267.7, 2,128, 405.6, 1.175 at $f$ = 1, 2, 4, 6, 8, so
  $A\bar g(f)=\ln W_T/23.7645$ = 13.58%, 23.52%, 32.25%, 25.27%, 0.68%; mean path 38.66, 1,491, $2.20\times10^6$,
  $3.23\times10^9$, $4.68\times10^{12}$ [A17-71]. $f^*=4.1381$: 32.28% a year, ×2,147, 85 times the unlevered end; zero
  growth 8.04, 1.94 $f^*$ [A17-72] (lm04.md:199's "about twice"); $\Pr(W_m>\E W_m)\approx\Phi(-1.915)=0.028$ [A17-73].
  Once, with [[LM41]]: at $f^*$ the path lost 98.5% from its peak by 20 November 2008 [A17-74].
- E6 §5, LM4's coin at $f^*=25$: $W_n<W_0$ exactly when $j<0.4150375\,n$ (LM4's 0.41504 [A17-75]). $n=100$: exact
  $\Pr(j\le41)=0.04431$; normal $\Phi(-g^*\sqrt n/\sigma_r)=\Phi(-1.69925)=0.04464$ with $g^*=0.0588915$ and
  $\sigma_r=\ln2/2=0.3465736$ (per-trade log growth), identical to $\Phi\big((0.4150375n-n/2)/(\sqrt n/2)\big)$;
  corrected $\Phi(-1.7)=0.04457$. $z$ has six figures because 0.04464 lies $1.0\times10^{-6}$ from a rounding boundary.
  $n=10$: 0.37695, 0.29551, 0.37591 [A17-76].
- E7 §5: within one point with 95% by the CLT, $n\ge1.96^2\times0.25/0.01^2=9{,}604$ [A17-77] against 50,000 (1.96 from
  lm04.md:541 [A17-78]). A model property; no interval (LM20).
- E8 §6 (X6, iid model, in-sample): from $\bar r=0.055170\%$, $s_r=1.2107\%$: one year $z=0.7147$, 23.74%; ten years
  $z=2.261$, 1.19%, median 3.89, quantiles 1.45 and 10.44 [A17-79]; over the sample, median 25.20 by construction, range
  5.49–115.6. On [[LM15]]'s window, the model refitted to the 5,664 returns of 2003–2025 gives a losing year 26.54% of
  the time, 6.10 of 23 years against 5 observed [A17-51]; LM15's lognormal fitted to the 23 annual growth factors gives
  30.0%. The means agree by construction, 11.634% against 11.646% a year (one year is 246 sessions, close to the
  years' average count), so the gap is dispersion: annual log returns vary by 22.207%, the model's $\sqrt{246}\,s_r$ by
  18.563% [A17-80], and $\Phi(-11.634/18.563)$ gives the 26.54%. The full-sample 23.74% is lower because the index
  rose 73.0% in 2026's nine months [A17-93]. Independent days and $\sqrt m$ scaling are assumptions [[LM19]] examines.
- E9 §7: (17.7) predicts 1.09 at 5 days and 0.27 at 20; TR23 shows 3.63 and 2.29. Next-day log returns correlate 0.039;
  their absolute values 0.161, and 0.123 twenty days apart [A17-81]: correlated squares raise $\E[Y_i^2Y_j^2]$ above
  $\sigma_X^4$.
- E10 §8: the average of $n$ independent standard Cauchy draws is standard Cauchy (stated without proof; Grinstead and
  Snell 1997, §8.2, Example 8.8), so by (15.9) at $\nu=1$, $\Pr(\lvert\bar X_n\rvert>1)=1-\tfrac2\pi\arctan1=\tfrac12$
  for every $n$; normal draws give $2\Phi(-\sqrt n)$ = 0.317, 0.0455, $5.7\times10^{-7}$ at $n$ = 1, 4, 25 [A17-82].

**Problems plan** (11; MC keys A, C, B, C, B; the lab solves 6, 7, 8, 11). Stems state the sample (TR23, 3 January 2003
→ 8 October 2026, $T=5{,}849$), log or simple returns, divisor $T$, $A=246.12$, $m$ in sessions, window type, rounding,
the quantile rule where a quantile is asked, and "iid model, in-sample" where it applies. No problem simulates.

1. MC: 400 independent trades, standard deviation 1.2% each; the average's. **A** 0.06%. B 0.003% ($\sigma/n$). C 24%
   (the sum's) [A17-83].
2. MC: 2,500 tosses of a fair coin ($p=\tfrac12$); Chebyshev's bound on $\Pr(\lvert j/n-p\rvert\ge0.02)$. A 0.0455
   ($2\Phi(-2)$, not a guarantee). B 0.5 (square forgotten). **C** 0.25 [A17-84].
3. MC: +100%/−50%, four rounds, $\E W_4=2.4414$; $\Pr(W_4>\E W_4)$. A 1/16 (four wins only). **B** 5/16. C 11/16 (adds
   the six paths ending at 1) [A17-85].
4. MC: iid $t_{1.5}$. As $n$ grows, $\bar X_n$: A does not converge (the strong law needs only
   $\E\lvert X\rvert <\infty$). B is approximately normal with standard deviation $\sigma_X/\sqrt n$ ((17.5) needs a
   finite variance). **C** converges to $\mu_X$ with probability one, with no such normal approximation.
5. MC: iid daily log returns with excess kurtosis 5.43; the excess kurtosis of their 20-day sums. A 1.21 ($/\sqrt{20}$).
   **B** 0.27. C 5.43 [A17-86]. The solution adds TR23's 2.29.
6. LM4's coin, $n=400$: exact $\Pr(j\le166)=0.000394$; normal $\Phi(-3.3985)=0.000339$; corrected
   $\Phi(-3.35)=0.000404$; why the uncorrected value is 14% low here and 0.7% high at $n=100$ (small absolute error,
   large relative error) [A17-87].
7. TR23, iid model, in-sample, $\bar r=0.055170\%$, $s_r=1.2107\%$, model quantiles $e^{m\bar r\mp1.645\,s_r\sqrt m}$:
   (a) $m=246$: $z=0.7147$, 23.74%; (b) $m=2{,}461$: 1.19%, median 3.89, quantiles 1.45 and 10.44. Not LM15's annual
   fit.
8. Prove $\Pr(W_m>\E W_m)\le\sigma_r^2/(m\delta^2)$ from (17.2); at $f=2$ with [[LM14]]'s gap $\delta(2)=2.936$ bp
   [A17-88], $s_r(2)=2.4288\%$, $m=5{,}849$: bound 1.17, normal $\Phi(-0.9245)=0.178$ [A17-89].
9. Derive (17.7); check $\operatorname{Bin}(m,\tfrac12)$: $-2/m$, −0.1 at $m=20$ [A17-90].
10. From the Cauchy average's law, $\Pr(\lvert\bar X_n\rvert>1)=\tfrac12$ for every $n$; compare $2\Phi(-5)$; which step
    of (17.2)'s proof fails.
11. Python: running up-day frequency with `R > 1e-12` at $n$ = 246, 1,231; overlapping $m$-day log-return kurtosis for
    $m$ = 1, 5, 20, 60 with `stats.kurtosis`, against $5.428/m$.

**Lab parts** (`build/make_lab17.py`, reads only its `data/taiex_tr.csv`): 1 data, the `Fraction` zero check, $T$,
years, $A$, the guard; 2 the two-trade table, E1; 3 coin probabilities against Chebyshev, X2, the running annualized
mean log return (27.12% after 246 days, low 2.03% on 20 November 2008, 13.58% at the end [A17-91]); 4 X1, E3 with
`fractions`, E4; 5 the $\bar g(f)$ grid, $f^*$ and zero growth by `brentq`, X4, E5; 6 X5, E6, E7, the 60-heads check; 7
X6, the calendar-year count, the 2003–2025 refit, the widget grid; 8 X7 both window types, lag correlations; 9 X9, E10;
10 problems 6, 7, 8, 11. Extension (stability check): X7 per limit regime. Labs write plain "LM18".

**Cross-module tags.**

- (17.1) $\E\bar X_n=\mu_X$, $\Var\bar X_n=\sigma_X^2/n$; iid with finite variance, or uncorrelated with common mean and
  variance (LM18, 19, 20).
- (17.2) $\Pr(\lvert\bar X_n-\mu_X\rvert\ge\varepsilon)\le\sigma_X^2/(n\varepsilon^2)$ for every $\varepsilon>0$, same
  conditions (LM18, 20).
- (17.3) $\frac1m\ln(W_m/W_0)\to g=\E[\ln(1+R)]$ with probability one; iid, $1+R>0$, $\E\lvert\ln(1+R)\rvert<\infty$
  (LM38, 41, 42, 45).
- (17.4) $\E W_m=W_0(1+\mu)^m$ for independent $R_t$ with mean $\mu$, $\E\lvert R_t\rvert<\infty$; $\Pr(W_m>\E W_m)\to0$
  when also iid with $1+R>0$ and $0<\sigma_r<\infty$ (LM18, 38, 41, 42).
- (17.5) $\Pr\big((S_n-n\mu_X)/(\sigma_X\sqrt n)\le z\big)\to\Phi(z)$ for every $z$; iid, $0<\sigma_X^2<\infty$ (LM18,
  20, 21, 22, 36).
- (17.6) $\Pr(W_m<W_0)\approx\Phi(-g\sqrt m/\sigma_r)$; median $\approx W_0e^{mg}$; quantiles
  $\approx W_0e^{mg\pm\Phi^{-1}(0.95)\sigma_r\sqrt m}$; iid, $1+R>0$, $0<\sigma_r<\infty$, large $m$; "≈" is (17.5)'s
  error, large in relative terms far in the tail (E6, Problem 6); exact for iid normal log returns (LM18, 38, 42).
- (17.7) $\operatorname{Kurt}(S_m)-3=(\operatorname{Kurt}(X)-3)/m$; iid, $\E X^4<\infty$, $\sigma_X>0$ (LM19, 26).

**Pitfalls to pre-empt.**

- Conditions every time, as in the tags; on TR23's empirical law (17.3) needs $f<10.31$; $\Pr(W_m>\E W_m)\to0$ needs
  $\sigma_r>0$ (a constant return gives equality).
- Three modes, three words: "in probability", "with probability one", "in distribution". Never "the sample mean is
  normal": "approximately normal for large $n$, under (17.5)'s conditions".
- The law fixes the rate, not the level: $W_m/(W_0e^{mg})$ spreads like $e^{\pm\sigma_r\sqrt m}$, a factor 2.52 either
  way over the sample ($s_r\sqrt T=0.9259$ [A17-92]).
- Slowness, honestly: "→ 0" bites fast only with leverage or volatile assets.
- Inference edge: no standard error with $s$, no interval, no band exits, no test of $\hat p$ against $\tfrac12$; no
  model property applied to TR23 as a margin; E8's 5 against 6.10 is an observed against an expected count only.
- In-sample circularity: the fitted median equals 25.20 by construction; X2's band uses the full-sample frequency. Two
  windows: LM15's comparison alone uses 2003–2025 (E8).
- Data traps: log returns for sums, so labelled; divisor $T$ (`stats.kurtosis` defaults; Polars' `std` uses $T-1$); the
  guard; overlapping windows are dependent; 7 April 2025 hit the 10% limit; $A=246.12$, never 252; $m$ whole sessions.
- Ownership: TR23's daily excess kurtosis 5.27, the daily gaps and $A\bar r$ are [[LM14]]'s; its regime figures on $R$,
  7 April 2025 and the top-ten shares [[LM15]]'s; LM17's own are the $m$-day log-return kurtosis, the $\lvert r\rvert$
  lag correlations and X9's running curve.
- References (SOURCES; theorem numbers, not pages): weak law, Grinstead and Snell (1997, §8.1, Theorem 8.2) and
  Wasserman (2004, Theorem 5.6); strong law, Wasserman (2004, Theorem 5.18), proved in Durrett (2019, Theorem 2.4.1),
  its condition needed by Durrett's Theorem 2.3.8; CLT, Wasserman (Theorem 5.8) and Grinstead and Snell (§9.1–§9.3); the
  Cauchy average, Grinstead and Snell (§8.2, Example 8.8); the gambler's fallacy, Blitzstein and Hwang (2019, §10.2).
  Breiman (1961), Thorp (2006), Mandelbrot (1963), Cont (2001), Peters (2019) as before.
- Notation: $k$ is not the window length ($m$ is); LM4's $N$ is $n$; $T$ is a count; generic moments are $\mu_X$,
  $\sigma_X$.

**Stage 4 for earlier modules.** `leads` gain 17 in lm01.md:6, lm03.md:6 and lm04.md:6 (lm05.md:6 already lists 17).

## LM18 Monte Carlo Simulation and the Bootstrap

**Prereq** `[1, 2, 5, 12, 13, 14, 15, 16, 17]`. Results used:

- LM1: (1.12), log returns add, so $\ln G=\sum_t r_t$.
- LM2: (2.11), the central difference; bump and reprice (lm02.md:576).
- LM5: $\varphi$, $\Phi$; (5.9) with $\int\lvert h\rvert f<\infty$; (5.12) $\E e^X=e^{\mu_X+\sigma_X^2/2}$; 0050's
  normal tail $\Phi(-4.1074386)$ and its value (lm05.md:223, 581) [A18-01]; Simpson's rule (5.14) and LM5's
  numerical-integration exhibit (lm05.md:585–599); `quad` (lm05.md:603).
- LM12: the Cholesky factor, S5's printed factor (lm12.md:441–445, % a day), colouring (lm12.md:504), the lab's
  colouring gap (build/make_lab12.py:567–580, `np.cov(..., ddof=0)`).
- LM13: (13.3) a frequency on $T$ days as a probability; (13.7); (13.11) $F_X$; (13.12) $\hat F$; (13.13) iid discrete
  draws; the empirical distribution as a probability model.
- LM14: (14.1) with $\E[\mathbf 1_{\mathcal A}]=\Pr(\mathcal A)$; (14.2)–(14.4); (14.6) $\E Z^4=3$, $\Var(Z^2)=2$; the
  quantile function $F_X^{-1}(u):=\min\{x:F_X(x)\ge u\}$; empirical quantiles $R_{(\lceil uT\rceil)}$.
- LM15: $\Phi^{-1}$ and (15.6); TR23's monthly counts of days with $\lvert R\rvert\ge3\%$; the maximum-likelihood
  Student $t$ (lab extension).
- LM16: (16.1) independence and the product rule; (16.3); (16.4); (16.7), including
  $L\mathbf Z\sim\mathcal N_N(\mathbf 0,LL^{\top})$ and the bivariate normal law of two coordinates.
- LM17: (17.1); (17.2); the strong law (iid, $\E\lvert Y\rvert<\infty$; LM17 cites Durrett 2019, Theorem 2.4.1); (17.4);
  (17.5) and 1.96; (17.6), exact under iid normal log returns; the lag-1 correlation of $\lvert r_t\rvert$.

**Leads** `[19, 20, 22, 26, 30, 32, 34, 36, 38, 39, 45]` (tag users and [[LMn]] targets): LM20, LM22 cite (18.2),
(18.3), (18.7); LM22 also (18.1), (18.8); LM30 (18.9); LM32 (18.1)–(18.6); LM36, LM38 (18.2); LM39 (18.1); LM45 (18.8).
Pointers only: LM19, LM26, LM34. Time "≈ 3 h + lab". Syllabus line: "Random generation, simulation error, variance
reduction, resampling."

**Forward links honoured.**

| Source | Promise | Kept in |
|:--|:--|:--|
| lm12.md:504; 527 (導讀) | "[[LM16]] and [[LM18]] develop such simulations"; 著色 | §3, E4, (18.9); §3 導讀 |
| build/make_lab12.py:567–580; plans/vol-2.md:672 | gap 0.0250 [A18-02]; "LM18 explains the rate" | E4, X3, (18.9), lab part 4 |
| lm05.md:6; plans/vol-1.md:88 | Monte Carlo against LM5's quadrature | §5, E5, X4 |
| lm02.md:576 | "a Monte Carlo option value" under bump and reprice | §2 pitfall, Problem 11 |
| src/pages/getting-started.md:133 | seed once | §2's per-experiment rule (Stage 4 edit) |
| src/pages/research-hygiene.md:20 | "Split by time, never at random" | §7 pitfall, hygiene note |
| ROADMAP; plans/vol-2.md:577–578 | random generation, colouring, Monte Carlo error, iid bootstrap | Owns |

**Outcomes (7).** After this module you should be able to:

1. explain how a seeded generator makes a simulation reproducible, and bump and reprice with common random numbers
2. draw from the exponential, normal and empirical distributions by the inverse transform, and normal vectors by colouring
3. calculate a Monte Carlo estimate, its standard error and its 95% Monte Carlo interval, and explain the $1/\sqrt n$ rate
4. compare Monte Carlo integration with Simpson's rule, and explain why simulation wins in many dimensions
5. apply antithetic variates, control variates and importance sampling, and predict each one's variance reduction
6. apply the iid bootstrap to a mean and a five-year growth factor, and explain what resampling days keeps and destroys
7. implement reproducible simulations and bootstraps with NumPy's `Generator` and SciPy, in chunks

**Owns.** Pseudo-random numbers: a seeded deterministic recursion; PCG64 behind `default_rng`; one stream per
experiment; reproducing against replicating; common random numbers. $\operatorname{Unif}(0,1)$. The inverse transform
(18.1). $\operatorname{Exp}(\lambda)$ with its mean and median. Draws $\Phi^{-1}(U)$, $R_{(\lceil Tu\rceil)}$,
$L\mathbf Z$. The Monte Carlo estimator (18.2), the 95% Monte Carlo interval (18.3), the digits rule, the $1/\sqrt n$
rate, (18.9). Standard errors of other statistics: $s_Y/\sqrt{2n}$ for a standard deviation, 20 batches for a quantile or
slope. Monte Carlo against quadrature. Antithetic variates (18.4), control variates (18.5), importance sampling (18.6).
The iid bootstrap as drawing from $\hat F$, (18.7), (18.8), what resampling keeps and destroys. Chunking, memory,
method-dependent draws, `np.cov`'s divisor.

**Leaves.** Bootstrap confidence intervals and tests, block and stationary bootstraps → LM22. Standard errors and
confidence intervals for data, $T$ against $T-1$ → LM20. The data's five-year spread against $\sqrt m$ → LM19.
Volatility clustering models → LM26. Resampled portfolios, estimation error in $\hat\Sigma$ → LM30. Monte Carlo VaR and
portfolio tails → LM32. Tests on later data → LM34. Paths → LM36, LM38; jump times → LM39. Bootstrap Kelly → LM45. Tests
of generators: not in the book.

**Uses before taught.**

- §4: with $s_Y$ for $\sigma_Y$ the interval is approximate, negligibly so with thousands of draws; [[LM20]] develops
  standard errors and confidence intervals for data.
- §7: reading a range of resamples as an interval is bootstrap inference, and blocks keep part of the clustering
  ([[LM22]]); volatility that depends on yesterday's is [[LM26]]'s (the one LM26 pointer); [[LM19]] examines whether
  five-year spread grows like $\sqrt m$.
- §6: "When $Y=h(\mathbf Z)$ with $h$ non-decreasing in every coordinate (or non-increasing in every one), $\rho_-\le0$"
  (stated without proof; Glasserman 2003, §4.2, p. 207); "[[LM32]] applies these estimators to value at risk."
- §5, three sentences: Simpson's rule errs by $O(\Delta x^4)$ in each coordinate of a smooth integrand ((5.14) one
  coordinate at a time). With equal points on each of $N$ axes, $n$ evaluations give a spacing of order $n^{-1/N}$. So
  the error is $O(n^{-4/N})$. Then one quasi-Monte Carlo sentence (evenly spread points; not in the book).

**Data role.** TR23 only: `data/processed/vol3_taiex.parquet` from `data/vol3_series.py`; closes 2003-01-02 →
2026-10-08, $T=5{,}849$ [A18-03] simple returns $R_t=P_t/P_{t-1}-1$ from 2003-01-03, $r_t=\ln(1+R_t)$; 8,680 calendar
days, 23.7645 years, $A=246.12$ [A18-04]; moments divide by $T$. Guarded counts (= `Fraction` recount): 108 returns at
or below −3% and 15 at or below −5% (LM13's), 175 with $\lvert R\rvert\ge3\%$ (LM14's); none exactly on ±3% or ±5%
[A18-05]. Five years is $m=\operatorname{round}(5A)=1{,}231$ sessions [A18-06]. Quantiles are order statistics
$x_{(\lceil un\rceil)}$ (`method="inverted_cdf"`). Recorded exception: E4 uses LM12's **printed** S5 factor and loads no
U28 data. §5 quotes LM5's printed values.

Seeds `default_rng([e, 20261011])`, $e$ the experiment's number: E1 1 (its replication 16), E2 2, E3 3 (E7 reuses its
paths), E5 5, E6 6, E8 8, E9 9, E10 10 (Problem 12), common random numbers 11, X3 12, coverage 13, X7 14, the $t$
extension 15. Recorded departures: E4 keeps LM12's `default_rng(20261011)`; E1 re-creates stream 1 to show that a
rerun repeats its numbers; lab part 3 and the `multivariate_normal` pitfall re-create stream 2 on purpose. Chunks of
500 rows (rows = paths) are also the batches. Scripts: `data/lm18_numbers.py`, `data/lm18_charts.py`.

**Hygiene declaration.**

| Result | Label |
|:--|:--|
| Windows (case, X1, X6 row 1); X2, E2's draws from $\hat F$; monthly counts, lag-1 correlation (cited) | Descriptive |
| The iid normal log-return model; E3, E6, E7, coverage; E2's exponential; the $t$ extension | In-sample model (all of TR23) |
| Bootstrap results E9, E10, X6 row 4, X7's resamples | In-sample model (resampling all of TR23) |
| E4, X3 | In-sample model (LM12's $L$, fitted to U28's 4,382 days) |
| E1, E5, E8, Problem 11, the common-random-numbers lab part, the widget | Model (the standard normal; no data) |

No stability check or out-of-sample result. Local note: "Every model of TAIEX here is fitted to all of TR23, 2003–2026,
so its answers are in-sample, not forecasts. A 95% Monte Carlo interval measures simulation error only, never model
error. Resampling days ignores their order, so a bootstrap is not a test on later data ([[LM22]] resamples blocks of
days; [[LM34]] tests strategies on later data)."

**Notation.** Every symbol keeps its §6 meaning, $\mathcal A$ included. Declared: $L$ (Cholesky factor; no leverage);
$B$ (bootstrap resamples); $\lambda$ (an exponential rate per session); $k$ (a number of standard deviations: the
threshold $-k$); $a$ (the proposal's mean shift in (18.6); no bets here); $m$ (sessions in a path); $N$ (dimension of a
random vector or an integral: 5 for S5, $m$ for a path); $n$ (draws or evaluations); $p$, $\hat p$ (the probability an
indicator estimates, and its estimate). Local symbols:

| Symbol | Meaning |
|:--|:--|
| $Y$, $Y_i$, $\bar Y_n$; $\sigma_Y$, $s_Y$ | the simulated quantity, its $n$ independent draws, their mean; its standard deviation in the model and over the draws (divisor $n$) |
| $h$ | a generic function, $Y=h(\mathbf Z)$ |
| $Y_i^-$, $\rho_-$ | the antithetic partner of $Y_i$, from $-\mathbf Z_i$; $\operatorname{Corr}(Y_i,Y_i^-)$ |
| $X$, $\beta$, $\hat\beta$ | a control with known mean $\mu_X$; $\sigma_{XY}/\sigma_X^2$; its least-squares estimate over the draws |
| $\E_{\hat F}$, $\Var_{\hat F}$, $\Pr_{\hat F}$ | expectation, variance, probability when days are drawn from $\hat F$ |
| $\bar R_{\text{boot}}$, $G_{\text{boot}}$ | mean of one resample of $T$ days; growth factor of one resample of $m$ days |
| $\hat\Sigma_{\text{sim}}$, $\lVert M\rVert_F$ | $\frac1n\sum_i\mathbf X_i\mathbf X_i^{\top}$ over $n$ coloured draws (18.9); Frobenius norm. `np.cov(..., ddof=0)` gives "its centred version", in words |

Counts: $i$ draws, $t$ days of a path, $j$ ranks. Seeds are literals, `default_rng([3, 20261011])`. LM12's $T$ draws are
$n$ here (said once, E4). (18.1) and Deep Dive (a) use $Y$; Deep Dive (b) declares its $X_1$, $X_2$. Not used: a star on
bootstrap quantities, $C$ for a control, $w$ for a weight, $b$, $c$, a bare $\Pr$ as a number.

**Motivating case: "Under water after five years?"** (box, about 125 words; longest sentence 24)

> TR23 is the TAIEX total-return index, dividends reinvested: 5,849 daily returns from 3 January 2003 to 8 October
> 2026. Five years is 1,231 sessions. Of the 4,619 five-year windows that start on a close in the sample, 191 ended
> below their start: 4.1% [A18-07]. All 191 started between November 2003 and April 2004 or between June and
> December 2007 [A18-08]. So they record two episodes, and the sample holds fewer than five non-overlapping
> five-year periods [A18-09]. A model of independent, normal daily log returns fitted to TR23 answers 5.49%
> [A18-10] by a formula. A Monte Carlo simulation of that model answers 5.3% [A18-11], and an iid bootstrap of the
> days 5.6% [A18-12], each ± 0.2 points with 10,000 draws. How far can each answer be trusted, and what does each one
> assume?

Resolved: (a) what the ± measures, §4 (E3), §6; (b) why the model answers agree within their standard errors, §7 (E10,
X6: both give $\ln G$ mean $m\bar r$ and variance $ms_r^2$; over 1,231 days the CLT makes the shape matter little); (c)
why the windows differ, §7 (X7; two episodes; their error needs LM22). The 5.49% is LM17's too.

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | why simulate; case box; X1; roadmap; notation and hygiene notes | 380 |
| 2 | Pseudo-Random Numbers and Seeds {1} | E1 first; seed → state → uniforms on $[0,1)$; PCG64; the iid model imitated (LM13); one stream per experiment; reproducing, replicating; pitfall: bump and reprice ((2.11)) needs common random numbers; 導讀; KC | 470 |
| 3 | From Uniform Draws to Any Distribution {2} | X2 first; (18.1) for continuous strictly increasing $F_Y$, any $F_Y$ in Deep Dive (a); $\operatorname{Exp}(\lambda)$; $\Phi^{-1}(U)$ ((15.6)); $R_{(\lceil Tu\rceil)}$; E2; $L\mathbf Z$ ((16.7)); pitfall: $u=0$; 導讀; KC | 580 |
| 4 | The Monte Carlo Estimator and Its Error {3} | $\E Y$ as an integral ((5.9), (14.2)); (18.2) from (17.1), (17.2), the strong law; (18.3) from (17.5), digits rule; $\sqrt{p(1-p)/n}$ by (14.1); $s_Y/\sqrt{2n}$ for a standard deviation ((14.6)); 20 batches for a quantile or slope ((17.1), ≈); E3; E4, (18.9), X3, Deep Dive (b); pitfall: simulation error only; 導讀; KC | 780 |
| 5 | Monte Carlo Against Quadrature {4} | E5; X4; orders in $N$ dimensions ($\sigma_Y$ may grow with $N$); the path as a 1,231-dimensional integral; quasi-Monte Carlo; pitfall: zero hits, $0\pm0$; KC | 420 |
| 6 | Variance Reduction {5} | X5 first; (18.4), E6; antithetics on a tail; (18.5), $\beta$ as a least-squares slope ([[LM12]]), E7; (18.6), E8, Deep Dive (c); pitfall: a proposal too far out; widget; 導讀; KC | 760 |
| 7 | The iid Bootstrap {6} | resampling days = drawing from $\hat F$; (18.7), E9; (18.8) as (17.4) under $\hat F$; E10, X6; keeps the one-day law (the 15 days at or below −5% recur), destroys clustering (X7); pitfall: time order; 導讀; KC | 720 |
| 8 | Simulation and Resampling in Python {7} | X8; one generator per experiment, chunks of 500, $\ln G$ as a sum; memory; `np.cov`'s divisor; pitfall: another method, other draws; lab box; KC | 240 |
| — | Summary (7 bullets) / Practice Problems (12) / Solutions | | 130 / 380 / 440 |
| | **Total** | | **5,300** |

**Elements.** 10 examples (E1 §2; E2 §3; E3, E4 §4; E5 §5; E6–E8 §6; E9, E10 §7); 7 knowledge checks (§2–§8); 5 中文導讀
(§2, §3, §4 with §5, §6, §7); one pitfall in each of §2–§8. Deep Dives: (a) with LM14's $F_Y^{-1}$ and the
right-continuity of $F_Y$, prove $F_Y^{-1}(u)\le y\iff u\le F_Y(y)$, so $\Pr(F_Y^{-1}(U)\le y)=F_Y(y)$; (b) (18.9): the
first sentence declares $X_1$, $X_2$, two entries of $\mathbf X$, bivariate normal by (16.7), with standard
deviations $\sigma_1$, $\sigma_2$, correlation $\rho_{12}$, and $\Sigma$'s entries $\sigma_{11}=\sigma_1^2$,
$\sigma_{22}=\sigma_2^2$, $\sigma_{12}=\rho_{12}\sigma_1\sigma_2$; colour them with their own 2×2 factor,
$X_1=\sigma_1Z_1$, $X_2=\sigma_2(\rho_{12}Z_1+\sqrt{1-\rho_{12}^2}\,Z_2)$; $\E Z^4=3$ and independence give
$\Var(X_1X_2)=\sigma_{11}\sigma_{22}+\sigma_{12}^2$ and $\Var(X_1^2)=2\sigma_{11}^2$; summing these variances over all
$N^2$ positions of $\Sigma$, said in words (no index letters: $j$ and $k$ keep their meanings), and dividing by $n$
gives (18.9); centring
(`np.cov(..., ddof=0)`) changes the root-mean-square gap by under 0.4% for $n\ge100$ [A18-13]; (c)
$\E[\mathbf 1\{Z\le a-k\}e^{2aZ-a^2}]=e^{a^2}\Phi(-k-a)$ by completing the square ($e^{k^2}\Phi(-2k)$ at $a=k$). Stated
without proof: PCG64's period $2^{128}$ (O'Neill 2014), the antithetic sign; Simpson's order is sketched.

References (records in SOURCES): Glasserman (2003), §2.2.1, §2.3.3, §4.1, §4.2 (p. 207, the monotone condition), §4.6;
Wasserman (2004), §8.2, his equation (8.1) (divisor $B$, as LM18); Efron and Tibshirani (1993), §6.2, Algorithm 6.1
(their equation (6.6) divides by $B-1$; E9 says so); Grinstead and Snell (1997), §5.2, Corollary 5.2; O'Neill (2014), HMC-CS-2014-0905; NumPy 2.5 and SciPy
1.18 references (the calls of X8, `SeedSequence`, `PCG64`, compatibility policy).

Knowledge checks: §2 is a same-seed rerun a second check? (No: identical draws.) §3 why $-\ln U/\lambda$ is also
exponential; $u=0.5$ from $\hat F$ (rank 2,925, +0.0879%, the median [A18-14]). §4 E3's paths for a standard error of
0.1 point (about 52,000 [A18-15]). §5 the chance of no hit at $-4.1074386$ in $10^5$ draws (0.135 [A18-16]). §6 why
antithetics do not help $\Pr(Z\le-k)$ (correlation $-2.0\times10^{-5}$ [A18-17]). §7 the chance that 7 April 2025 is
absent from a resample ($(1-1/5{,}849)^{5849}=0.368$ by (13.7); about 63% of days appear [A18-18]). §8 the memory of
$10{,}000\times1{,}231$ draws (98.5 MB [A18-19]); why chunks change nothing.

中文導讀 terms (shared list, English at first use in each box): 蒙地卡羅法, 隨機數, 擬隨機數, 隨機數產生器, 隨機種子, 均勻分布, 逆變換法, 指數分布, 經驗分布函數,
獨立同分布, 標準誤, 中央極限定理, 變異數縮減, 對偶變數, 控制變量, 重要抽樣, 自助重抽法, 重抽樣, 放回抽樣; the book's own 放回重抽樣 (resampling with replacement) in
every box that uses it. Printed: 著色, 互不相關 (lm12.md:527). "Common random numbers" and "95% Monte Carlo interval" keep
their English names, described in Chinese (兩次計算共用同一組隨機數; 只量模擬誤差的區間), never 信賴區間. 隨機數, not 亂數.

**Exhibits.**

- X1 `line` §1 "Five years later": $x$ the window's first close (2003-01-02 → 2021-09-10), $y$ log, $P_{t+1231}/P_t$
  (4,619 points, `x2`); `hline` at 1; two `band`s labelled "range of under-water starts", 2003-11-03 → 2004-04-21 (116
  starts, 111 under water) and 2007-06-15 → 2007-12-07 (122, 80) [A18-08]. Note: 191 of 4,619 below 1 (4.1%); worst 0.78
  (2004-03-09 → 2009-02-24), best 3.43 (2021-05-17 → 2026-06-09) [A18-20]; descriptive; Source: FinMind
  `TaiwanStockTotalReturnIndex` (TAIEX), retrieved 2026-10-18.
- X2 `line` §3 "Inverse transform on TR23": $x$ return (`pct1`, −10% to +10%), $y$ 0–1 (`n2`); $\hat F$ as a `step`
  series; E2's three `point`s at $(R_{(j)},u)$. No normal curve.
- X3 `line` §4 "The $1/\sqrt n$ rate": $x$ numeric $\log_{10}n$, `ticks` 2–5, `tickLabels` "100" … "100,000"; $y$ log,
  relative gap (`n3`); series 1 root-mean-square gap of 200 runs (experiment 12) at $n$ = 100, 500, 1,000, 4,382,
  10,000, 50,000; series 2 (18.9), dashed; `point` LM12's 0.0250 at 4,382. Note: LM12's printed $L$,
  `np.cov(..., ddof=0)`; at 4,382 the formula gives 0.0289, the runs $0.0301\pm0.0007$ (20 batches of 10 runs; relative
  standard error below 2.7%); 82 of the 200 runs ($41\%\pm3\%$) come at or below 0.0250 [A18-21]; slope −1/2.
- X4 `line` §5 "Error against evaluations": $x$ numeric $\log_{10}$ of evaluations (0–10, `tickLabels`), $y$ log,
  relative error (`sci`); Simpson, LM5's printed errors ÷ $2.000355\times10^{-5}$ at 9 … 1,025 evaluations (0.484 …
  $1.23\times10^{-6}$ at 257 … $4.83\times10^{-9}$) [A18-22]; formulas $223.6/\sqrt n$ (plain) and $2.153/\sqrt n$
  (importance sampling) [A18-23].
- X5 table §6 "Three ways to cut simulation error": target | exact | method | draws | estimate | standard error |
  variance ÷. $\Pr(Z\le-4.1074386)$, $2.000355\times10^{-5}$: plain $10^6$, $1.8\times10^{-5}$, $0.4\times10^{-5}$
  [A18-24], 1; antithetic —, —, —, 1.00002; importance sampling $10^4$, $2.047\times10^{-5}$, $0.044\times10^{-5}$
  [A18-25], 10,786 [A18-26]. Five-year $\E G$, 2.1584 [A18-27]: plain 10,000 paths, 2.165, 0.010 [A18-28], 1; antithetic
  5,000 pairs, 2.155, 0.004, 6.06 [A18-29]; control $\ln G$, 2.161, 0.003, 11.4 [A18-30]. Five-year $\Pr(G<1)$, 0.0549:
  plain 0.053, 0.002, 1; antithetic 0.053, 0.002, 1.06 [A18-31]; control 0.054, 0.002, 1.31 [A18-32]. Note: experiments
  5, 8, 3, 6; "variance ÷" from exact formulas except the plain rows.
- X6 table §7 "Four answers to the case": rows windows | formula | Monte Carlo | bootstrap; columns $\Pr(G<1)$ | ± one
  standard error | 5%, 50%, 95% quantiles of $G$ | standard deviation of $\ln G$ | assumes. Windows: 4.1%, none here
  ([[LM22]]), 1.02 / 1.61 / 2.53 [A18-33], 0.283 [A18-34], two episodes (4.75 disjoint periods). Formula: 5.49%, exact,
  0.98 / 1.97 / 3.97, 0.425, iid normal log returns. Monte Carlo: 5.3%, 0.2, —, —, the same model. Bootstrap: 5.6%, 0.2,
  0.97 / 1.94 / 3.94 (± 0.008, 0.010, 0.034; 20 batches), $0.424\pm0.003$ [A18-12], iid days from $\hat F$. Note:
  the bootstrap median sits several standard errors below the formula's 1.97 because this run's mean $\ln G$ also lies
  below $m\bar r$ (E10, which prints both); the shapes differ little.
- X7 `bar` §7 "What resampling destroys": categories "0" … "8" (days with $\lvert R\rvert\ge3\%$ in a calendar month);
  TR23 months 210, 38, 9, 16, 4, 5, 1, 0, 3 (LM15's) [A18-35] against the average of 1,000 resamples (experiment 14) on
  TR23's dates, 154.3, 96.3, 28.8, 5.7, 0.8, 0.1, 0.0, 0.0, 0.0, standard errors at most 0.3 [A18-36]; `valueLabels`
  `n1`. Note: 286 months, the first and last partial (18 and 6 returns); variance 1.846 (LM15) against $0.598\pm0.002$
  in resamples, the value of independent days (exactly 0.597 with divisor 286); lag-1 correlation of $\lvert r_t\rvert$
  0.161 ([[LM17]]) [A18-37], near 0 in resamples ($0.0006\pm0.0004$) [A18-38]: properties of the iid-days model.
- X8 table §8 "NumPy and SciPy calls": `default_rng(seed)` → `Generator(PCG64)`; `random(size)` → $[0,1)$;
  `standard_normal(size)`; `integers(low, high, size)` → `high` excluded; `choice(a, size)` → `replace=True`;
  `multivariate_normal(mean, cov)` → `method='svd'`; `np.cov(x, rowvar=False)` → divisor $n-1$ unless `ddof=0`;
  `np.quantile(x, u, method="inverted_cdf")` → $x_{(\lceil un\rceil)}$; `stats.norm.ppf` → $\Phi^{-1}$.

**Widget `mcTail` — "Three ways to estimate a tail probability".** `Book.controls`: $k\in\{1,2,3,4.1074386,5\}$ (the
fourth "LM5's −5% day"); $n=10^2\dots10^6$ in quarter decades; run 1–5 (the `Book.rng` seed); method (plain, antithetic,
importance sampling with $a=k$). Chart (`line`): $x$ $\log_{10}n$ (`ticks` 2–6, `tickLabels`), $y$ estimate ÷
$\Phi(-k)$, linear 0–3 (higher values drawn at 3, flagged), three series at 41 log-spaced checkpoints, `hline` 1
"exact". Readouts (`sci`, `sig`): estimate, standard error, exact $\Phi(-k)$ (`Book.dist`), ratio, coverage, tail draws,
equivalent plain draws. One cached stream $Z=\Phi^{-1}(U)$ per run feeds all three methods ($-Z$, $Z-k$). Initial state
(the PDF): $k=4.1074386$, $n=10^6$, run 1, importance sampling; plain and antithetic sit at 0 until a hit, importance
sampling near 1; antithetic on plain shows a method that gains nothing. Note: "The widget's generator is not NumPy's;
the text quotes no widget value."

**Examples.** Each prints its seed, array shapes and, for every simulated number, a standard error.

- E1 §2 Same seed, same answer: $\Pr(Z\le-2)$ from `standard_normal(10_000)`. `default_rng([1, 20261011])` gives 249
  hits, and 249 again on a rerun; a replication, `default_rng([16, 20261011])`, gives 214. $\Phi(-2)=0.02275$ predicts
  227.5; each count has a standard error of about 15 (14.9 under the model) [A18-39]. A rerun reproduces; it does not
  replicate.
- E2 §3 A waiting time and a TAIEX day from three uniforms: experiment 2's `random(3)`, $u$ = 0.1396965, 0.4634985,
  0.1740834 [A18-40] (seven decimals: the second gives $Tu=2{,}711.003$). $\operatorname{Exp}(\lambda)$ with
  $\lambda=175/5{,}849=0.02992$ per session [A18-41], the rate of days with $\lvert R\rvert\ge3\%$: waits
  $-\ln(1-u)/\lambda$ = 5.03, 20.81, 6.39 sessions; mean 33.42, median 23.17 [A18-42]. Empirical: $\lceil5{,}849u\rceil$
  = 818, 2,712, 1,019 → −0.9468% (2021-12-14), +0.0247% (2007-02-01), −0.7785% (2005-09-23) [A18-43].
- E3 §4 The case by simulation: iid $\mathcal N(g,\sigma_r^2)$ daily log returns with $g=\bar r=0.05517\%$,
  $\sigma_r=s_r=1.2107\%$ [A18-44], $m=1{,}231$. Exactly, $\Pr(G<1)=\Phi(-g\sqrt m/\sigma_r)=\Phi(-1.5988)=5.49\%$
  (17.6), reproduced from the printed inputs [A18-45]. Experiment 3, 10,000 paths, `standard_normal((500, m))` twenty
  times, $\ln G=\sum_t(g+\sigma_rZ_t)$: 530 under water, $0.0530\pm0.0022$; the 95% Monte Carlo interval, about 4.9% to
  5.7%, covers 5.49%; printed "5.3% ± 0.2 points".
- E4 §4 Why LM12's gap was 0.0250: LM12's `default_rng(20261011)`, `standard_normal((4382, 5))` coloured with the
  printed $L$, `np.cov(..., ddof=0)`: one run, gap 0.0250. Semiconductor's simulated variance is 4.18% high, about two
  of its standard errors $\sqrt{2/4{,}382}=2.14\%$ ($\Var Z^2=2$) [A18-46]. (18.9) gives a run's root-mean-square
  relative gap $\sqrt{(1+(\operatorname{tr}\Sigma)^2/\lVert\Sigma\rVert_F^2)/n}=1.911/\sqrt n =0.0289$; in X3, 41% of
  200 runs come closer than 0.0250, an ordinary run; at 50,000 draws (18.9) gives 0.0085.
- E5 §5 Against Simpson: $\Pr(Z\le-4.1074386)=2.000355\times10^{-5}$ (LM5's 0050 −5% day). Experiment 5,
  `standard_normal(10**6)`: 18 hits (20.0 expected), $1.8\times10^{-5}\pm0.4\times10^{-5}$, exact relative standard
  error 22%; a 95% interval of ±1% needs $1.92\times10^9$ draws; Simpson's relative $1.2\times10^{-6}$ at 257
  evaluations needs about $3.5\times10^{16}$.
- E6 §6 Antithetic paths: $\E G=e^{m(g+\sigma_r^2/2)}=2.1584$ ((5.12)). Experiment 6, 5,000 pairs from $\mathbf Z$ and
  $-\mathbf Z$, `standard_normal((500, m))` ten times: $2.155\pm0.004$ against $2.165\pm0.010$ for E3's 10,000 paths;
  $\rho_-=-e^{-m\sigma_r^2}=-0.835$ with $m\sigma_r^2=0.1804$, so the variance falls by $1/(1+\rho_-)=6.06$. On the same
  pairs $\Pr(G<1)$: $0.0528\pm0.0022$; $\rho_-=-p/(1-p)=-0.058$ with $p=0.0549$ (disjoint events), ÷1.06.
- E7 §6 A control variate: E3's paths, $Y=G$, $X=\ln G$, $\mu_X=mg=0.6791$; $\hat\beta=2.18$ (batch standard error 0.01
  [A18-30]; exactly $\beta=\E G$, since $\Cov(G,\ln G)=m\sigma_r^2\E G$). Controlled $2.161\pm0.003$ against plain
  $2.165\pm0.010$. Exactly, $\rho_{XY}=\big(m\sigma_r^2/(e^{m\sigma_r^2}-1)\big)^{1/2}=0.955$ (completing the square as
  in (5.12)), variance ÷11.4. For $Y=\mathbf 1\{G<1\}$: $\rho_{XY}=-\varphi(1.5988)/\sqrt{p(1-p)}=-0.488$, ÷1.31;
  controlled $0.0535\pm0.0020$.
- E8 §6 Importance sampling: (18.6) with $a=k=4.1074386$, experiment 8, `standard_normal(10_000)`: 5,043 draws in the
  tail; $2.047\times10^{-5}\pm0.044\times10^{-5}$ (relative 2.1%), the exact value inside the interval. Per-draw
  variance $1.8546\times10^{-9}$ against plain $2.0003\times10^{-5}$ (five significant digits; three give 10,811):
  ÷10,786, so 10,000 draws do the work of $1.08\times10^8$ plain ones.
- E9 §7 Bootstrap of the mean day: experiment 9, $B=10{,}000$ resamples of 5,849 days, `integers(0, T, size=(500, T))`
  twenty times. Resample means average $0.06272\%\pm0.00016\%$ ($\bar R=0.06251\%$ [A18-47]); their standard deviation
  (divisor $B$; Efron and Tibshirani's equation (6.6) divides by $B-1$, which changes nothing at the printed precision for this $B$) is
  $0.01563\%\pm0.00011\%$ ($s_Y/\sqrt{2B}$), against the exact bootstrap value
  $s/\sqrt T=1.2084\%/\sqrt{5{,}849}=0.01580\%$ (18.7) [A18-48]. Say: a property of the bootstrap model; [[LM20]]
  derives the same $s/\sqrt T$ as $\bar R$'s sampling error.
- E10 §7 The case by bootstrap: experiment 10, $B=10{,}000$ resamples of $m=1{,}231$ days,
  `integers(0, T, size=(500, m))` twenty times: 561 under water, $0.0561\pm0.0023$, printed 5.6% ± 0.2.
  $\E_{\hat F}G_{\text{boot}}=(1+\bar R)^m=1.00062505^{1231}=2.1580$ (18.8). The plain estimate $2.136\pm0.009$ has a
  95% Monte Carlo interval, $2.136\pm1.96\times0.009$, 2.118 to 2.154, that misses 2.1580, as one run in twenty does; with $\ln G_{\text{boot}}$ as
  a control (mean $m\bar r$ exactly), $2.158\pm0.003$ [A18-49]. The same draws put the average $\ln G$ 2.4 standard
  errors below $m\bar r$ [A18-12], so the quantiles of $G_{\text{boot}}$, 0.97 / 1.94 / 3.94 (batch standard errors
  0.008, 0.010, 0.034), sit below the model's 0.98 / 1.97 / 3.97 (windows: 1.02 / 1.61 / 2.53). Standard deviation of
  $\ln G$: $0.424\pm0.003$ resampled, $\sqrt m\,s_r=0.425$ in the bootstrap model, 0.283 across windows. Print $\bar R$
  as 0.062505% (0.0625% gives 2.1579).

**Problems plan** (12; MC keys B, C, A, B, A; Python: 12; lab repeats 2, 4, 5, 7, 8, 9, 11, 12). Every stem states its
sample (TR23, 5,849 returns, 2003-01-03 → 2026-10-08), divisor $T$, $A=246.12$, $m=1{,}231$, rounding, the quantile rule
where a quantile appears ($R_{(\lceil uT\rceil)}$, `method="inverted_cdf"`), and for a simulation the seed, the array
shapes and the number of draws.

1. MC §4. To cut a Monte Carlo standard error by 10 with the same method, multiply $n$ by: A 10 (error taken as $1/n$);
   **B 100**; C $\sqrt{10}\approx3.16$ (square root inverted).
2. MC §5. Plain Monte Carlo for $p=\Pr(Z\le-3)=0.001350$ with $n=10^6$; the standard error is closest to: A 0.0367
   (forgot $n$); B $1.35\times10^{-9}$ (the variance); **C $3.67\times10^{-5}$** [A18-50].
3. MC §3. For $U\sim\operatorname{Unif}(0,1)$, a draw from $\operatorname{Exp}(\lambda)$ is: **A $-\ln(1-U)/\lambda$**;
   B $-\lambda\ln(1-U)$ (mean $\lambda$: 0.03 sessions instead of 33.4 at $\lambda=0.02992$); C $1-e^{-\lambda U}$
   (applies $F_Y$, not $F_Y^{-1}$; values below 0.0295) [A18-51].
4. §3. Returns +1.2%, −0.8%, +0.3%, −2.5%, +0.6%; draws for $u$ = 0.37, 0.95, 0.18 by $R_{(\lceil5u\rceil)}$: ranks 2,
   5, 1 → −0.8%, +1.2%, −2.5% [A18-52]; why $u=0$ has no rank.
5. §6. From E3's 10,000 paths, the plain estimate of $\E G$ has standard error 0.0097 (of the mean of $G$), that of
   $\Pr(G<1)$ 0.0022. (a) With 5,000 antithetic pairs: $0.0097\sqrt{1-0.835}=0.0039$ for $\E G$;
   $0.0022\sqrt{1-0.058}=0.0021$ for $\Pr(G<1)$ [A18-53]. (b) Prove $\rho_-=-e^{-m\sigma_r^2}$ for $G$ and its partner
   $e^{2mg}/G$ under the model, using (5.12).
6. MC §6. A control with $\rho_{XY}=0.95$: one controlled draw is worth about how many plain draws? A 1.11
   ($1/\rho_{XY}^2$); **B 10.3**; C 20 ($1/(1-\rho_{XY})$) [A18-54].
7. §6. Derive the weight of (18.6) and, at $a=k$, the per-draw second moment $e^{k^2}\Phi(-2k)$; for $k=3$:
   $p=\Phi(-3)=1.3499\times10^{-3}$, $e^9\Phi(-6)=7.994\times10^{-6}$, importance variance $6.17\times10^{-6}$ against
   plain $1.348\times10^{-3}$: ÷218 [A18-55].
8. §7. Prove $\Var_{\hat F}(\bar R_{\text{boot}})=s^2/T$ (divisor $T$); with $s=1.2084\%$, 0.01580%. Is E9's 0.01563% a
   flaw of the bootstrap? (No: 1.5 of its standard errors, $s_Y/\sqrt{2B}=0.00011\%$, from the exact value [A18-48].)
9. §7. Apply (17.4) under $\hat F$ ($\mu=\bar R$) to get (18.8); with $\bar R=0.062505\%$, $(1+\bar R)^{1231}=2.1580$;
   compare $e^{m\bar r}=1.9722$ ($\bar r=0.055170\%$) [A18-56]: mean path against median path (LM17).
10. MC §5. Simpson on a product grid in $N$ dimensions errs by $O(n^{-4/N})$, plain Monte Carlo by $O(n^{-1/2})$; Monte
    Carlo has the better order when: **A $N>8$**; B $N>4$ (the trapezoid's order); C $N>2$ (order 1) [A18-57].
11. §2. Slope of $\Pr(Z\le-k)$ at $k=2$ by (2.11), $\Delta k=0.01$, $n=100{,}000$: $\Phi(-2.01)=0.0222156$,
    $\Phi(-1.99)=0.0232955$ (seven decimals; six give a difference of 0.001079, not 0.001080); standard error 0.0333
    with independent draws, 0.0052 with common draws; exact $-\varphi(2)=-0.0540$ [A18-58].
12. Python §7–§8. A fresh `default_rng([10, 20261011])`, `integers(0, T, size=(500, m))` twenty times: reproduce E10
    ($0.0561\pm0.0023$; $2.136\pm0.009$ against 2.1580), and check that one call of size $(10{,}000,m)$ gives identical
    indices.

**Lab parts** (`build/make_lab18.py`; data: `taiex_tr.csv` only; text writes "LM12", "LM18" plainly). 0 environment; the
seed rule. 1 data: $R$, $r$, $T$, years, $A$; counts with the guard and with `Fraction`. 2 generators: E1, `print(rng)`,
the common-random-numbers pitfall (experiment 11, 200 repetitions of two `standard_normal(100_000)` arrays, the first
for $-2.01$, the second for $-1.99$: standard deviation $0.037\pm0.002$, against $0.0052\pm0.0003$ with the first array
twice; standard errors $s_Y/\sqrt{400}$ [A18-59]). 3 inverse transform: E2, X2, `norm.ppf` of E2's uniforms against
`standard_normal(3)` of a re-created stream 2 (−1.0817, −0.0916, −0.9382 against 0.1679, 0.2891, 0.7095 [A18-60]). 4
Monte Carlo: E3; coverage (experiment 13, 1,000 runs of $n=1{,}000$: 937 intervals cover 5.49% (standard error 7,
$\sqrt{1{,}000\times0.9437\times0.0563}$ under the exact coverage) [A18-61], against an exact binomial coverage of 94.4%: with about 55 hits a run the normal approximation is rough); E4
with LM12's $L$ typed in; X3. 5 quadrature: E5, X4, zero-hit runs at $n=10{,}000$ (0.8187). 6 variance reduction: E6–E8,
X5. 7 bootstrap: E9, E10, X6, X7. 8 the lab's problems. Extension (in-sample model; experiment 15): the five-year answer
under LM15's maximum-likelihood $t$ for daily $R$, with the unrounded `stats.t.fit` parameters (printed $\nu=3.065$,
location 0.0997%, scale 0.7761% [A18-62]), `standard_t(nu, size=(500, m))` twenty times: 0.9% ± 0.1 (10,000 paths), 5 of
them (standard error 2) with a day at or below −100% [A18-63]; rounded parameters give other draws (`standard_t`'s
stream depends on $\nu$); the reader explains why the answer moved (the location is not $\bar R$; no price limit).

**Cross-module tags.**

- (18.1) For $U\sim\operatorname{Unif}(0,1)$ and any distribution function $F_Y$, $F_Y^{-1}(U)$ has distribution
  function $F_Y$; for $\operatorname{Exp}(\lambda)$, $-\ln(1-U)/\lambda$ (LM22, LM32, LM39).
- (18.2) $Y_i$ iid, $\E\lvert Y\rvert<\infty$: $\E\bar Y_n=\E Y$; if $\sigma_Y^2<\infty$, $\Var\bar Y_n=\sigma_Y^2/n$,
  standard error $s_Y/\sqrt n$ (LM20, LM22, LM32, LM36, LM38).
- (18.3) 95% Monte Carlo interval $\bar Y_n\pm1.96\,s_Y/\sqrt n$, for $0<\sigma_Y^2<\infty$ and large $n$ (LM20, LM22,
  LM32).
- (18.4) $\Var\big(\tfrac1n\sum_{i=1}^n\tfrac12(Y_i+Y_i^-)\big)=\tfrac{\sigma_Y^2}{2n}(1+\rho_-)$, for
  $\sigma_Y^2<\infty$ and pairs independent across $i$ (LM32).
- (18.5) For iid pairs $(X_i,Y_i)$ with finite variances, $\sigma_X>0$ and $\mu_X$ known,
  $\bar Y_n-\beta(\bar X_n-\mu_X)$ has variance $(1-\rho_{XY}^2)\sigma_Y^2/n$ at $\beta=\sigma_{XY}/\sigma_X^2$ (LM32).
- (18.6) $\E h(Z)=\E\big[h(Z-a)\,e^{aZ-a^2/2}\big]$ for every $a$ when $\E\lvert h(Z)\rvert<\infty$; at $a=k$,
  $\Pr(Z\le-k)=\E\big[\mathbf 1\{Z\le0\}e^{kZ-k^2/2}\big]$ (LM32).
- (18.7) $\E_{\hat F}\bar R_{\text{boot}}=\bar R$, $\Var_{\hat F}(\bar R_{\text{boot}})=s^2/T$ (LM20, LM22).
- (18.8) $\E_{\hat F}G_{\text{boot}}=(1+\bar R)^m$, (17.4) under $\hat F$ (LM22, LM45).
- (18.9)
  $\E\lVert\hat\Sigma_{\text{sim}}-\Sigma\rVert_F^2=\big(\lVert\Sigma\rVert_F^2+(\operatorname{tr}\Sigma)^2\big)/n$ for
  $\hat\Sigma_{\text{sim}}=\frac1n\sum_i\mathbf X_i\mathbf X_i^{\top}$, $\mathbf X_i$ iid
  $\mathcal N_N(\mathbf 0,\Sigma)$ (LM30).

**Pitfalls to pre-empt.**

- Conditions. (18.1) needs $U$ in the open interval: `random` can return 0, so draw $-\ln(1-U)$ and ranks with
  `integers`. (18.3) needs a finite $\sigma_Y$ and enough hits: with none, $s_Y=0$ and the interval is $0\pm0$ (82% of
  plain runs of 10,000 at $k=4.1074386$). Importance sampling needs a proposal positive wherever $h\varphi\ne0$; a shift
  too small or too large loses (per-draw relative standard error 7.76 at $a=k/2$, 2.15 at $a=k$, 132 at $a=2k$
  [A18-64]). A control's mean must be known exactly; estimating $\beta$ from the same draws adds a bias of order $1/n$
  (stated). Antithetics help only when $\rho_-<0$.
- "=" against "≈": (18.7), (18.8) and $\Phi(-g\sqrt m/\sigma_r)$ under the model are exact; every simulated number is
  "≈", with the digits its standard error supports (0.0530 ± 0.0022 → 5.3%); a 95% interval misses one run in twenty
  (E10).
- The interval measures simulation error around the model's own answer: 5.3% ± 0.2 says nothing about TAIEX.
- Data traps. Overlapping windows are not independent and weight days unequally (mean $\ln G$ 0.502 against
  $m\bar r=0.679$). The horizon is a session count (calendar windows: 185 of 4,637, 3.99% [A18-65]). The bootstrap mixes
  both limit regimes (3,077 returns before 2015-06-01, 2,772 from it [A18-66]) and keeps 7 April 2025 (−9.6997%
  [A18-67]) in the pool.
- Simulation traps. A generator reseeded inside a loop repeats its draws; another method gives other numbers from the
  same stream (`norm.ppf(random)` against `standard_normal`; `multivariate_normal` against `z @ L.T` [A18-68]); `np.cov`
  divides by $n-1$ unless `ddof=0`; `np.quantile`'s default interpolates; chunks reproduce one call in the pinned NumPy,
  which NumPy does not promise: the script asserts it.
- Boundary creep: no bootstrap intervals, $p$-values, resample counts beyond a value, or block bootstrap (LM21, LM22);
  no VaR (LM32), GARCH (LM26), data standard error as inference (LM20), "right" sample or bootstrap, quasi-Monte Carlo,
  or 28-dimensional orthant probability.

**Stage 4 for earlier modules.** `lm01.md:6` leads gain 18 ((1.12)); `lm02.md:6` leads gain 18 ((2.11), lm02.md:576).
`lm05.md:6` and `lm12.md:6` already list 18.
