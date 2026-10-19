# Volume IV — Statistical Inference and Econometrics: shared decisions and spines

Volume IV turns the probability models of Volume III into estimates a reader can defend. A sample mean becomes an
estimator with a standard error, a frequency a test, a slope a regression coefficient with an interval, a past mean a
prior to be shrunk, a price series a process with or without a unit root, and a day's squared return a noisy view of
a variance that changes over time. The volume teaches each tool on Taiwan data, says what it assumes and shows where
the assumption fails (ROADMAP, "Module boundaries").

The reader reads English as a second language and wants the tools learned systematically (SPEC §2). Worked examples,
diagrams and formulas carry each module; the prose connects them. Volumes I–III are published: link to their results
with [[LMn]] instead of repeating them, and honour every forward link they make to LM19–LM26 (listed per spine).

This file holds the editor's Stage 1 decisions (2026-10-19): the shared decisions, the capability check sent to the
owner, the decisions on the Stage 1 survey and its fresh check, and one spine per module. One agent per module drafts
its brief from the spine; a fresh agent checks the briefs across the volume; the editor decides and the briefs are
revised (TODO, Stage 1). The briefs and `plans/vol-4-anchors.md` then replace the spines below.

## Shared decisions

- **Length and voice.** AUTHORING §1: at most 6,000 words of prose and 36 pages; first drafts under 5,500 words;
  sentences average under 16 words and never exceed 30; paragraphs at most 80 words; connectors kept.
  `uv run python build/qa/style.py src/lmNN.md` shows no FAIL before a draft is handed back. Volume III's modules ran
  about 5,700 words in six or seven sections; each spine below is cut to fit that.
- **Section pattern.** A small numeric case or a picture first, then the definition, estimator or test with all its
  conditions, a short derivation, a worked example on Taiwan data, at most one pitfall, the 中文導讀 and the
  knowledge check. Each estimator is first computed by hand in NumPy from its formula; a package (if approved) is then
  shown to give the same number.
- **Rigor.** Every estimator, test and theorem states its conditions: iid or stationary data, finite moments,
  independence of errors, the null hypothesis, the large-sample approximation used. A result is derived in the text or
  in a Deep Dive, or labelled *stated without proof* with a reference. Asymptotic results are stated, not proved; each
  module says what "large $T$" means in its examples. Measure theory and martingale limit theorems stay out of scope.
- **Estimate, standard error, interval.** Every estimate the volume prints for data comes with its standard error or
  interval, or with a sentence saying why it has none. A standard error states its method (iid formula, HAC, block
  bootstrap) and, for a bootstrap, the number of resamples, the block length and the seed.
- **Divisors.** The book keeps its rule: $s$ and $s^2$ divide by $T$ (AUTHORING §6; Volumes I–III and $\hat\Sigma$
  agree, and LM14 reads them as the moments of $\hat F$). Volume IV adds $s_{\mathrm u}^2:=\frac{T}{T-1}s^2$, the
  unbiased variance, which LM20 derives (keeping lm10.md:166) and which the $t$ statistics and the packages use
  (NumPy's `ddof=1`, Polars' default); and a regression's $s_\varepsilon^2=\text{RSS}/(T-d)$ (LM23). For a normal
  model the maximum-likelihood $\hat\sigma$ equals $s$. Every script passes `ddof` explicitly. Daily samples change in
  the fifth significant figure; the 23 calendar years, 2×2 tables and the 28-value cross-sections change by 2% or more,
  so a module that prints such a statistic names its divisor. The editor fixes AUTHORING §6, whose $\mu$, $\sigma$ row
  ("say whether $s$ divides by $T$ or $T-1$") contradicts its probability row ("divisor $T$"), before any writer
  starts.
- **Notation.** AUTHORING §6 plus the table below, which the editor copies into §6 (with the amendments it names)
  before any writer starts. Each module lists its local symbols in its notation note. The briefs may propose changes
  with reasons; the cross-check decides them.

  | Symbol | Meaning (from Volume IV) | Against §6 |
  |:--|:--|:--|
  | $\theta$, $\hat\theta$, $\boldsymbol\theta$ | a parameter, its estimator, a parameter vector (LM20–LM24, LM26); in LM21 also a binomial probability under test | $\theta$ is an angle in LM9, LM11, LM12; Volume IV has no angle (LM23 cites LM12's $\cos^2\theta$ by its tag only). Amend the $\theta$ row |
  | $\operatorname{Bias}$, $\operatorname{MSE}$, $\operatorname{SE}$ | bias, mean squared error, standard error of an estimator, upright operators: $\operatorname{SE}(\bar R)$ | new |
  | $s_{\mathrm u}$; $s_\varepsilon$ | standard deviation with divisor $T-1$; a regression's residual standard deviation, divisor $T-d$ | new; $s$ keeps divisor $T$ |
  | $\bar R$; $\hat\mu$ | the sample mean; $\hat\mu$ only where the text treats it as an estimator of $\mu$ ($\hat\mu=\bar R$ in LM20) | as §6 |
  | $\mathcal L(\theta)$, $\ell(\theta)$ | likelihood and log-likelihood $\ell=\ln\mathcal L$ (LM20, LM24, LM26) | $\mathcal L$ is the Lagrangian in modules with constraints; Volume IV has none. Amend the $\lambda$, $\nu$, $\mathcal L$ row |
  | $\mathcal I(\theta)$ | Fisher information | $I$ is the identity matrix |
  | $H_0$, $H_1$ | null and alternative hypotheses | subscripted; $H$ stays the Hessian |
  | $\text{t-stat}$ | a t-statistic, upright, with its estimate when needed: $\text{t-stat}(\hat\beta)$; the Dickey–Fuller statistic is "the DF t-stat" | $t$ stays the date index and $t_\nu$ the distribution |
  | $p_i$, $p_{(i)}$; $m$; $q$ | the p-values of $m$ tests and their ordered values; the number of tests; the false-discovery level (LM21 only, which has no bets and no $m$-day sums). Elsewhere "p-value" is written in words | amend the $p$, $q$ row's scope |
  | $\alpha$ | one meaning per module: the significance level (LM21, LM22); the regression intercept and Jensen's alpha (LM23); a GARCH coefficient (LM26); the tail index (LM20, as LM15). A module with another $\alpha$ writes the level as a percentage ("the 5% level") | new row |
  | $\beta$, $\hat\beta$, $\hat{\boldsymbol\beta}$ | regression slope or coefficients (LM23, LM25's cointegrating coefficient); a GARCH coefficient (LM26) | as §6 (common notation) |
  | $\alpha_0$, $\beta_0$ | the parameters of a beta prior, $\operatorname{Beta}(\alpha_0,\beta_0)$ (LM24, which has no regression slope) | subscripted |
  | $\mu_0$, $\sigma_0$ | prior mean and standard deviation of a mean parameter (LM24); densities of parameters are written $f$ with a subscript | §6's subscripted densities |
  | $\varepsilon_t$, $\hat\varepsilon_t$ | a regression's error and residual (LM23); LM26's innovation $\varepsilon_t=\sigma_t\xi_t$ | as §6 |
  | $\eta_t$ | white-noise innovation of an AR or MA model (LM25, which cites LM6's residual $\varepsilon$ of (6.25) by its tag) | $\eta$ (LM5's constant) does not occur in LM25 |
  | $\xi_t$ | iid standardized innovation, mean 0 and variance 1, normal or scaled Student $t$ (LM26) | $Z$ stays a standard normal |
  | $X$, $d$ | LM23's $T\times d$ design matrix, first column $\mathbf 1$; $d$ the number of coefficients | LM23 writes no random variable $X$; $d^2$ (Mahalanobis) is LM16's |
  | $\rho_k$, $\hat\rho_k$; $\gamma_k$, $\hat\gamma_k$; $k$ | autocorrelation and autocovariance at lag $k$, model and sample (LM19, LM22, LM25, LM26); $k$ the lag. LM20 may use $k$ for the Hill estimator's tail count, declared | $\gamma$ (cash-flow growth) does not occur in Volume IV; amend the $k$ row |
  | $\operatorname{VR}(m)$ | variance ratio of $m$-day log-return sums (LM19, LM22, LM25) | $m$ as §6 |
  | $\phi_j$, $\theta_j$; $c$; $\delta$ | AR and MA coefficients, always subscripted ($\phi_1$ even in an AR(1)); an AR intercept; the Dickey–Fuller coefficient $\delta=\phi_1-1$ (LM25, which has no Kelly fraction) | $\varphi$ stays the normal density; amend the $c$ row's scope |
  | $\Delta x_t$ | $x_t-x_{t-1}$ | as §6 ("a change") |
  | $F_t$, $S_t$; $\tau$ | TX settlement price and TAIEX close; time to expiry in years (LM25), as LM6 | $F_X$ keeps its subscript; LM25 writes no $S_n$ |
  | $\sigma_t^2$, $\sigma^2_{t+1\mid t}$; $\lambda$; $\omega$, $\alpha$, $\beta$; $a$, $b$ | conditional variance of day $t$ and its forecast made on day $t$; the EWMA decay; GARCH coefficients; the coefficients of LM26's auxiliary regressions (ARCH test, Mincer–Zarnowitz) (LM26 only, which has no sample space, Poisson rate, bet or market-model regression) | amend the $\lambda$ and $\Omega$, $\omega$ rows |
  | $\mathrm{RV}_t$ | realized variance of day $t$, the sum of squared intraday log returns at a stated interval (LM26) | §6's $\mathrm{RV}$ is the same idea on simple returns; LM26 says so |
  | $B$; $\ell$ | number of bootstrap resamples; block length or mean block length (LM22, which has no likelihood) | as LM18 |

  Words with one meaning each: "unconditional variance" for GARCH's $\omega/(1-\alpha-\beta)$ (LM26), "long-run
  variance" for the HAC target (LM23). Not used in Volume IV: $P$ for probability, $R^2$ for R-squared (written in
  words, or 判定係數), a star for a bootstrap draw ($\bar R_{\text{boot}}$, as LM18), $I$ for information, $L$ for a lag
  operator (write $x_{t-1}$), $\tau$ for a Dickey–Fuller statistic, $Z_t$ for a non-normal innovation.
- **Data.** Four samples; never mix two within one statistic, and name the sample in every caption.
  - **TR23** (Volume III): the TAIEX total-return index, closes 2003-01-02 → 2026-10-08, $T=5{,}849$ daily returns,
    $A=246.12$ (`data/vol3_series.py`). The main sample of LM19–LM22, LM24 and LM26's daily models.
  - **U28** (Volume II): the 28 leaf TWSE sector price indices and the TAIEX price index, returns 2008-12-02 →
    2026-10-08, $T=4{,}382$, $A=245.4794$ (`data/lm10_series.py`); the halves are LM11's (2,191 returns each,
    2008-12-02 → 2017-10-06 and 2017-10-11 → 2026-10-08). Cross-sections of 28 estimates: LM23's betas and alphas,
    LM24's shrinkage. Price indices, no dividends: every caption says so, and every alpha says that it includes the
    gap between the sector's dividend yield and the index's. LM23's named factor uses the Electronic sector index
    (an aggregate outside U28, repaired by `data/vol2_series.py`), labelled *constructed*.
  - **TX23** (new): the TX near-month regular-session settlement price and the TAIEX close on TR23's 5,850 dates (the
    two calendars agree on every date, fresh check). Each monthly contract's last trading day is its last
    regular-session row in `TaiwanFuturesDaily`; the series rolls at the close of the day before that day (LM2's rule),
    so no expiry day enters (FinMind prints the expiring contract's settlement as 0 from 2008-12-17). LM25's basis.
  - **T5S** (new): TAIEX every 5 seconds (`TaiwanVariousIndicators5Seconds`, Free), 2005-01-03 → 2026-10-08. Rows per
    day show the sampling regime: 271 (1-minute snapshots) to 2011-01-14, then 1,081 (15 seconds), 1,621 (10 seconds)
    and 3,241 (5 seconds) from 2014-12-29; `data/vol4_series.py` finds each switch from the data. LM26's realized
    variance: a 5-minute daily series from 2005 and the sampling-interval study from 2015. The 13:30:00 value equals
    the official close (8 sampled days, 2005–2025); the index freezes during the closing call auction (13:25:05 to
    13:29:55 from 2014-12-29; each regime's window stated).
  - Recorded uses of earlier samples: LM20 and LM23 may recompute LM2's and LM4's 0050 and 00631L numbers under their
    own module's name (LM2's slope 1.887, LM4's interval), and LM20 recomputes LM16's U28 correlation 0.5749 and LM15's
    $t$ fit; everything else from Volumes I–III is quoted as printed, with its module and sample (LM16's numbers that
    LM19 and LM26 quote are U28 price-index numbers).
- **One owner per statistic.** LM19 owns TR23's descriptive statistics in Volume IV (location, dispersion, sample
  autocorrelations of $r$, $\lvert r\rvert$ and $r^2$, variance ratios); LM20 the standard errors and intervals of
  $\bar R$, $s$, the Kelly fraction (delta method) and the iid Sharpe ratio, and the MLE fits; LM21 the tests of TR23's
  mean and the calendar family; LM22 the bootstrap intervals (Sharpe ratio, Kelly fraction, a variance ratio, LM16's
  crash correlation, LM11's eigenvalue share); LM23 the betas, the alphas and their multiple testing; LM24 the
  posteriors and the shrunk sector means; LM25 the basis statistics, the robust autocorrelation band, Ljung–Box and the
  unit-root tests; LM26 the GARCH and EWMA fits and the realized-variance series. The briefs list the values each owns.
- **Return type.** As Volume III: one-day statistics on simple returns $R$, sums over days on log returns $r$; LM25's
  basis on log prices; LM26's models on daily log returns in percent (so that the fitted constants are readable and
  arch does not warn about scale), labelled in every caption.
- **Sharpe ratio.** $\mathrm{SR}=(\mu-r_f)/\sigma$ per day with $r_f=0$ (FinMind has no Taiwan interest-rate series,
  survey), annualized by $\sqrt A$ only with LM19's condition stated (uncorrelated returns; Lo 2002). LM23's alphas
  are market-model intercepts on raw returns; the text says by how much a risk-free rate of at most 2% a year (LM6's
  proxy) would move them, $(1-\beta)r_f/A$ per day.
- **Counting.** As Volume III: one guard (`<= -x + 1e-12`, `>= x - 1e-12`) or exact arithmetic (PITFALLS §5).
- **Simulation.** As Volume III (AUTHORING §8): each simulated experiment creates `rng = np.random.default_rng([e,
  20261011])` once at its start, with its stated number `e` first; every Monte Carlo or bootstrap result states the
  number of draws or resamples, the seed and its standard error, and keeps only the digits its standard error
  supports. arch's bootstraps accept a NumPy `Generator` as `seed` (survey): pass the experiment's generator. Widgets
  use `Book.rng(seed)`.
- **Python.** NumPy and SciPy first, Polars for data, as before. If the owner approves the packages (capability
  check): statsmodels for unit-root and cointegration p-values (MacKinnon), HAC cross-checks, Ljung–Box and ARIMA;
  arch for GARCH, block bootstraps and the automatic block length. Book code passes NumPy arrays and converts outputs
  with `.to_numpy()`; it never imports pandas. Package facts are checked on the pinned versions and recorded in SOURCES
  before they are printed: statsmodels' `multipletests` defaults to Holm–Šidák, not Holm; statsmodels' robust
  covariances (HAC) set `use_t=False`, so their p-values are normal; `adfuller` and `kpss` take `result_object=True`,
  `coint` takes `return_results`; `acorr_ljungbox` and `optimal_block_length` return DataFrames;
  `scipy.stats.bootstrap` resamples iid only and defaults to BCa; `scipy.stats.false_discovery_control` gives BH and
  BY (survey and fresh check).
- **References.** Cite only entries in `project/SOURCES.md`. Stage 1 adds the Volume IV entries the survey verified
  (Crossref, publishers, the authors' pages), with the unresolved points open until checked: Engle (1982) end page
  1007 or 1008; James and Stein (1961) end page 379 or 380; the origin of the volatility signature plot; Jorion's
  (1986) shrinkage target; Casella and Berger's theorem numbers; Lo and MacKinlay's (1988) equation numbers; Hill's
  (1975) formula as printed; Gelman et al.'s (2.10) and RiskMetrics §5.3.2 rechecked in the documents before they are
  printed. No source derives fractional Kelly as *the* Bayesian answer; LM24 states its result inside its model and
  cites Browne and Whitt (1996) for the posterior-mean rule under log utility. FinMind's Pricing and Disclaimer pages
  join SOURCES ("Market data").
- **Chinese terms.** AUTHORING §1 (樂詞網; English in parentheses at first use in each box). Looked up on 2026-10-19
  (survey; recorded in SOURCES at Stage 1). Decided: **波動率** for volatility (the statistics listing gives 波動；波動率,
  and TAIFEX names its index 臺指選擇權波動率指數); at Stage 4 the five printed 波動度 become 波動率 (lm05.md:191,
  lm07.md:354, lm07.md:512, lm10.md:228, lm10.md:449). **時間序列** for time series (the mathematics listing; the
  statistics listing writes 時間數列). Terms: 敘述統計, 樣本變異數, 估計量, 不偏估計量, 偏誤, 均方誤差, 一致估計量, 標準誤,
  抽樣分布, 信賴區間, 概度函數, 最大概度估計, 費雪訊息, 克萊姆-饒歐下界, 希爾估計量, 假設檢定, 虛無假設, 對立假設,
  顯著水準, p值, 檢定力, 第一型錯誤, 第二型錯誤, 多重假設檢定 (multiple testing), 族系誤差率, 偽發現率, Bonferroni 校正,
  資料偵伺, 重抽樣, 自助重抽法, 百分位數信賴區間, 變異數比, 自我相關, 自我相關函數, 偏自我相關函數, 迴歸,
  普通最小平方法, 殘差, 判定係數, 高斯-馬可夫定理, 最佳線性不偏估計量, 變異數非齊一性, 穩健標準誤,
  變異數非齊一與自我相關一致估計量 (HAC), 貝氏推論, 事前分布, 事後分布, 共軛事前分布, 收縮估計量, 經驗貝氏估計量,
  平穩, 白噪音, 隨機漫步, 自我迴歸模型, 移動平均模型, 自我迴歸移動平均模型, 單根, 單根檢定, 增廣 Dickey-Fuller 檢定,
  共整合, 誤差修正模型, 波動群聚現象, 條件變異數, 指數加權移動平均模型, 廣義自我迴歸條件變異數非齊一模型 (GARCH),
  高頻資料. The book's own forms, no 樂詞網 entry, printed with their English in every box that uses them: 區塊自助重抽法
  (block bootstrap), 平穩自助重抽法 (stationary bootstrap), 已實現變異數 (realized variance), 已實現波動率 (realized
  volatility), 市場微結構雜訊 (market microstructure noise).
- **Research hygiene.** The site's Research hygiene page and each module's declaration. Volume IV is the first with
  inference and with out-of-sample results: a test or interval on data is *In-sample* unless the text evaluates it on
  data the estimate did not see; LM24's shrinkage (estimated on the first half of U28, judged on the second) and LM26's
  forecasts (rolling estimation, judged on the next day) are *Out-of-sample*; comparing the two limit regimes or the
  halves is a *Stability check*; simulated nulls are *Model*. Every test reports how many tests the module ran on the
  same data (LM21's rule, cited before LM21 by a pointer).
- **Charts.** As Volume III (AUTHORING §7) plus the additions the owner approves (capability check). At most four named
  series; every value the text cites is plotted or printed; two quantities with different units go in two stacked
  charts with the same $x$ range, never on two $y$ axes. A chart or widget carries at most 300 KB of JSON (thin a
  20-year daily chart by week or by extremes per pixel, keeping every cited value); a widget over many series embeds
  precomputed statistics, not the series.
- **Widgets.** Use `Book.controls`, `Book.rng` and `Book.dist` instead of copying them; a widget's initial state
  computes within the PDF printer's wait (keep a bootstrap at $B\le1{,}000$ per click); the text quotes only numbers a
  script in `data/` reproduces.
- **Labs.** One per module, `build/make_labNN.py`, reading only its own `data/` folder (`data/make_lab_data.py`). The
  briefs name the files; a lab that needs a Backer- or Sponsor-tier file, or T5S, says so and has a fallback.
- **Problems.** Each stem states its sample, divisor, $A$, rounding, the test's null and level, the standard-error
  method and, for a simulation or bootstrap, the seed, the draws and the block length. Every distractor is computed
  and fails for a reason worth explaining.
- **Leads and tags.** As Volume III: a module's `leads` are the modules that cite one of its tags or that its text
  points to with [[LMn]]; cite another module's exhibit or example in words with [[LMn]].

## Capability check (2026-10-19, sent to the owner)

What the spines need and the repository lacks (survey and fresh check: `book.js`, `build/`, `data/`,
`pyproject.toml`). Nothing is built before the owner approves; each approved piece is reviewed by a fresh agent (0
differences on the published pages).

- **(A) Packages.** statsmodels 0.15.0 (BSD-3) and arch 8.0.0 (NCSA); arch requires statsmodels, so they are one
  decision. They bring pandas 3.0.6, patsy 1.0.3, formulaic 1.2.2, narwhals 2.27.1, wrapt 2.5.1, interface-meta 2.0.1
  and tzdata 2026.5: about 82 MB unpacked, cp313 Windows wheels for all, metadata-compatible with the locked NumPy
  2.5.3 and SciPy 1.18.1. Runtime is unverified: arch 8.0.0 predates pandas 3. Needed for: MacKinnon p-values of the
  ADF, KPSS and Engle–Granger tests (LM25; transcribing the response-surface tables by hand is error-prone); GARCH with
  Student-$t$ errors, robust standard errors and forecasts (LM26); the automatic block length of Politis and White
  (LM22); HAC and Ljung–Box cross-checks (LM23, LM25). The text derives every estimator in NumPy first. Proposed in
  the main dependencies, because the labs import them. After approval: `uv add`, then a smoke test in an empty
  `UV_PROJECT_ENVIRONMENT` (PITFALLS) that runs `arch_model(..., dist="t")` fit and forecast,
  `StationaryBootstrap(seed=Generator)`, `optimal_block_length`, `adfuller`, `kpss`, `coint`, `acorr_ljungbox` and an
  OLS HAC fit; if arch fails on pandas 3, the fallback is a pandas pin agreed with the owner.
- **(B) Data pipeline.**
  1. TX23: `TaiwanFuturesDaily` TX (Free; the whole history in one call) into `data/raw/vol4/`, registered in the
     manifest; a new `data/vol4_series.py` builds TX23 and checks it: calendar against TR23's, `spread` = close − the
     previous settlement (with the five 2007 exceptions listed), last trading days from the daily rows, the
     expiry-day zeros. `TaiwanFuturesFinalSettlementPrice` (Backer) only as an optional cross-check (it lacks every
     monthly contract of 2000, 2006, 2008, 2014 and 2020).
  2. T5S: FinMind serves it one day per request, so the present manifest (one request per entry, checked byte for
     byte) cannot hold it. A new `data/fetch_intraday.py` keeps its own manifest (`data/raw_intraday_manifest.json`, one
     entry per day: date, rows, SHA-256), downloads about 5,350 days into `data/raw/vol4/taiex5s/<year>/` (about 310
     MB of CSV, on the owner's disk only), logs rows per day, resumes after an interruption and stops at the hourly
     quota (under one hour on the Sponsor plan). It checks every day: the row count of its regime, strictly increasing
     times, no repeated day, the 13:30:00 value against the TAIEX close in `TaiwanStockPrice` (an independent series,
     PITFALLS §3). `fetch_finmind.py --verify` and `./build.sh --data` leave T5S out unless its files are present.
  3. Shared files: `make_lab_data.py` entries for LM19–LM26, `build.sh` `DATA_STEPS`, `data/README.md`, AUTHORING
     §8–§9, SOURCES.
- **(B′) What is committed from T5S** (the owner's call on the licence). FinMind's Pricing page marks
  "再散布原始資料、建立鏡像 API" as not allowed, and its Disclaimer (§2, §3.2–3.3) forbids redistributing its data and
  asks for credit to the original agency. Proposed: commit one derived file, `data/derived/vol4_rv.csv`: per day, the
  realized variance at eight sampling intervals and the number of returns in each (about 5,350 rows, under 1 MB),
  credited to FinMind and TWSE, never intraday prices or returns; LM26's lab reads it, so a reader needs no 5,350
  calls (about nine hours on a registered Free account at 600 calls an hour). ROADMAP's data rule then drops its
  example "5-minute returns", which is the price path up to scale. Without the file, the lab reads one year of raw T5S.
- **(C) Chart kit** (`book.js`, `build.py`, AUTHORING §7).
  1. A log $x$ axis on line charts, with a build check that $x$ stays positive (LM19's variance ratio against $m$,
     LM20's standard error against the sampling interval, LM21's largest t-stat against the number of tests, LM22's
     interval width against block length, LM26's signature plot); about 8 lines.
  2. Tick labels on scatter axes, with the left margin growing to fit (forest plots of estimates with intervals:
     LM22, LM23, LM24); about 6 lines.
  3. Filled bands in scatter charts, with `check_bands` extended (LM23's confidence and prediction bands on a one-year
     fit; on the full U28 sample the confidence band is about one pixel wide); about 10 lines. Optional: dashed band
     edges are the fallback.
  4. A shared $x$ for every series of a line chart, with `check_bands` taught to read it (LM26's daily volatility
     chart, LM19's rolling scale): about 40% less JSON for three series, 30% for two; about 8 lines.
  5. A size check in `build.py`: fail on a chart or widget JSON over 300 KB, warn on a page over 2 MB (published
     pages reach 1.50 MB, LM7; nothing checks it now).
- **(D) `Book.dist` and `Book.rng` for inference.** `Book.dist.tInv` (LM20's $t_{T-1}$ interval, LM21's widget) and
  `rng.studentT(nu)` with a gamma sampler for non-integer $\nu$ (LM20's coverage widget under LM15's $\nu=3.065$),
  tested against SciPy in `build/qa/test_bookjs_dist.py`.
- **(E) Optional data.** TX 1-minute bars for 2025 only (`TaiwanFuturesKBar`, Sponsor, about 300 calls): a futures
  signature plot beside the index's (bid–ask bounce against stale prices) in LM26, and LM25's check of how much of the
  basis noise comes from the 15-minute gap between TX's settlement and the TAIEX close. Text exhibits only; no lab
  needs it.

Not proposed (fallbacks are good enough): a second $y$ axis (stacked charts), bands on bar charts (dashed lines),
markers on line series (annotation points), a separate colour matrix for heatmaps (no p-value heatmaps), beta and
chi-square quantiles in `Book.dist` (LM24's beta–binomial posterior is a static exhibit).

## Decisions on the survey and its fresh check (2026-10-19)

- **Autocorrelation.** LM19 owns the sample autocorrelation $\hat\rho_k$ (full-sample mean, divisor $T$ in numerator
  and denominator, statsmodels' `acf` convention), TR23's values for $r$, $\lvert r\rvert$ and $r^2$, their link with
  LM17's pair correlations (0.1224 against 0.1228 at lag 20, reviews/lm17.md:36) and the iid band $\pm1.96/\sqrt T$,
  drawn as the iid band with one sentence: clustering widens it (on log returns $\hat\rho_1=0.0393$ has an iid
  standard error 0.0131 and a heteroskedasticity-robust one 0.0205; fresh check). LM25 owns the robust band, the
  Ljung–Box test and the variance-ratio test (Lo and MacKinlay, named with its robust form); LM22 owns a block-bootstrap
  interval for a variance ratio. Stage 4 changes `build/make_lab17.py:486` ("the autocorrelation convention stays
  LM26's") to LM19.
- **The annual-volatility gap.** On 2003–2025 log returns, LM17's 18.563% against LM15's 22.207% needs a variance
  ratio of 1.43, but VR(246) is about 1.05 there (fresh check); the full TR23 gives about 1.2, and beyond a year VR
  falls below 1 (0.75 at $m=492$, 0.44–0.62 at $m=1{,}231$, where the overlapping estimator is biased down). So LM19
  compares the three numbers on one sample and return type, shows VR($m$) up to $m=1{,}231$ with the bias stated, and
  says that most of the gap is the sampling error of 23 annual values, which LM20 measures.
- **The multiple-testing case.** Sector-minus-index differences measure beta and dividend yields, not skill (10 of 28
  have $\lvert\text{t-stat}\rvert>1.96$; fresh check). LM21 tests a calendar family on TR23 (12 months and 5
  weekdays) and a simulated strategy search; LM23 tests the 28 market-model alphas (one $\lvert\text{t-stat}\rvert>1.96$,
  Semiconductor, against 1.4 expected) and applies LM21's corrections, stating that the alphas are correlated across
  sectors and include dividend-yield gaps.
- **Sharpe and Kelly intervals.** LM20 owns the delta-method standard errors of the Kelly fraction and of the Sharpe
  ratio under iid returns; LM22 owns bootstrap intervals (iid and block) for both, compared with LM20's; LM33 owns the
  Sharpe ratio's standard error under non-iid returns (Lo 2002), the Probabilistic and Deflated Sharpe ratios and the
  minimum track record; LM45 owns sizing from a bootstrap distribution.
- **Promises without an owner, assigned.** LM16's crash correlation (0.788 against the model's 0.860, lm16.md:514,
  "for [[LM21]] and [[LM22]]") → LM22, a block-bootstrap interval, with LM21's test framing in one sentence. LM11's
  eigenvalue error (lm11.md:406, `make_lab11.py:571`) → LM22, a definite example (PC1's share from 250 returns). The
  maximum-likelihood $\boldsymbol\mu$ and $\Sigma$ of $\mathcal N_N$ (plans/vol-3.md:1241) → LM20, stated, as the
  reason $\hat\Sigma$ divides by $T$. Economic factor models (ROADMAP's boundary table, the syllabus, lm11.md:309) →
  LM23, with a factor named in advance (the electronics sector against the index), set beside LM11's warning that
  nothing makes PC2 "electronics".
- **LM24's James–Stein case** is reported as the data give it: on U28's halves the first- and second-half sector means
  correlate −0.05, their spread is smaller than their sampling noise, the positive-part estimate shrinks fully to the
  grand mean, and out-of-sample error falls all the way to full shrinkage (fresh check). The lesson is that 28 sector
  means carry almost no information beyond their average. The theorem's conditions (independent normal estimates with
  equal known variances; $N\ge4$ when the target is the estimated grand mean) do not hold for correlated sectors: the
  brief says what is lost and whether removing the common component helps. A partial-shrinkage example appears only
  if the data give one.
- **LM24's Kelly result holds** (fresh check): with GBM returns of known $\sigma$ and a normal prior centred at zero,
  the growth-optimal fixed fraction is $\E[\mu\mid\text{data}]/\sigma^2$, the plug-in fraction times the data's
  weight $c=\sigma_0^2/(\sigma_0^2+\sigma^2/T)$, so the fraction of full Kelly (§6's $c$) is the data's weight; the
  horizon does not change it under log utility. On TR23, $c=0.87$
  for a prior standard deviation of 10 points a year; LM4's "a quarter to a half" needs a sceptic's prior of about 2.3
  to 3.9 points. The module says so.
- **Package facts corrected:** the normal p-values under HAC are statsmodels' (`use_t=False`), not arch's.
- **Defects in published pages, fixed at Stage 4** with the Volume IV publication: the literal `[[LM20]]` in the
  LM11 lab (`build/make_lab11.py:571`, flagged in reviews/lm12.md:171); the front matter `leads` that miss Volume IV
  targets their text already links (lm02 23; lm03 19; lm04 19, 24; lm05 19, 20, 26; lm07 20; lm11 20, 22; lm18 23),
  checked again then against the final briefs; Volume III's brief cites LM18's old equation numbers (plans/vol-3.md,
  frozen): Volume IV cites the published (18.4), (18.7), (18.8), (18.9).

## Stage 4 changes to earlier modules

Collected here as the briefs add them; applied at publication with the edition note.

- 波動度 → 波動率 in lm05.md:191, lm07.md:354, lm07.md:512, lm10.md:228, lm10.md:449.
- `build/make_lab17.py:486`: the autocorrelation convention is LM19's.
- `build/make_lab11.py:571`: the literal `[[LM20]]` becomes "LM20".
- Leads of Volumes I–III gain the Volume IV modules that cite them (each brief's "Stage 4 for earlier modules").

## Spines

Each spine gives the module's question, its draft prerequisites, the forward links it must honour (from the survey
and the fresh check; the brief rechecks each line), what it owns and leaves, its data, a candidate case, exhibits and
widget, and what the brief must settle. Numbers marked "explored" are the editor's or the fresh check's first look;
only anchors may be printed.

### LM19 Descriptive Statistics of Returns

**Question.** How volatile is the TAIEX in a year? On 2003–2025 log returns, LM17's iid scaling gives 18.563% and the
spread of the 23 calendar-year log returns gives 22.207% (LM15). LM19 measures how daily variances add up (the
variance of a sum, the variance ratio), finds that autocorrelation explains little of this gap on that sample, and
hands the rest, the sampling error of 23 values, to LM20. On the way it shows which statistics of a return series are
robust and which hang on a few days.

**Prereq (draft).** LM1, LM3 ((3.7), (3.9), the volatility drag), LM5, LM14 (moments, $\operatorname{Skew}$,
$\operatorname{Kurt}$, quantiles), LM15 (the annual fit, tail measures), LM16 ((16.3) the variance of a sum), LM17
((17.1), (17.7), the kurtosis of sums).

**Forward links to honour.** lm03.md:330 (skewness "the asymmetry of moves around the mean"); lm04.md:132 (0050's
excess kurtosis 8.12, "develops this measure of tail weight"); lm05.md:367 and 745 (the sample version with $\hat\mu$
and $s$; skewness as a standardized moment); lm14.md:211 ($T$ or $T-1$, shared with LM20); lm15.md:263 and 447 (the
annual spread 0.1856 against 0.22207; TR23's skewness −0.34 as a statistic); lm16.md:623 (the model factor 1.0797,
18.53%, a U28 number); lm17.md:80, 347, 384 (whether daily variances add up; 22.207% against 18.563%; sample kurtosis
and its divisor); lm18.md:373 (the windows' spread of $\ln G$, 0.283 against 0.425: does it grow like $\sqrt m$?);
`make_lab03.py:273`; `make_lab15.py:443` ("the sampling error of such statistics": LM19 splits, LM20 measures).

**Owns.** Location (mean, median, trimmed mean; $\bar R$ against $\bar r$ against $R_G$, citing LM3); dispersion ($s$
with divisor $T$, and $s_{\mathrm u}$ introduced in one paragraph with LM20's pointer; mean absolute deviation,
interquartile range, the robust scale estimates $1.4826\cdot$MAD and IQR$/1.349$ under a normal model); shape (sample
skewness and excess kurtosis with divisor-$T$ moments, the adjusted versions, and one robust measure each, sources
checked); the sample autocorrelation $\hat\rho_k$, its convention and its iid band; the variance of an $m$-day sum,
$m\gamma_0+2\sum_{k=1}^{m-1}(m-k)\gamma_k$, and $\operatorname{VR}(m)=1+2\sum_{k=1}^{m-1}(1-k/m)\rho_k$; TR23's
$\hat\rho_k$ for $r$, $\lvert r\rvert$, $r^2$ and its variance ratios up to $m=1{,}231$ (overlapping and
non-overlapping sums, the small-sample bias of the overlapping estimator stated); annualization rules (mean $\times A$,
variance $\times A$, volatility $\times\sqrt A$, Sharpe ratio $\times\sqrt A$) and when each fails (Lo 2002); weekly,
monthly and yearly returns from daily data.

**Leaves.** Standard errors of every statistic, the sampling error of 23 annual values → LM20; the robust band, the
Ljung–Box and variance-ratio tests → LM25; a block-bootstrap interval for a variance ratio → LM22; models of
clustering → LM26; Sharpe ratio statistics → LM33; drawdown statistics → LM32. LM15 keeps the kurtosis's fragility
around 7 April 2025 (cite, do not recompute).

**Data.** TR23 only (calendar years 2003–2025 as Volume III defined them); LM16's U28 numbers quoted as printed. No
simulation, unless the brief wants one iid comparison (then the seed rule).

**Candidate exhibits.** The three annual volatilities on one sample; a bar chart of $\hat\rho_k$ for $r$ and
$\lvert r\rvert$, $k=1,\dots,30$, with the dashed iid band labelled as such; the variance ratio against $m$ (log $x$ if
approved); robust against classical scale on rolling years. **Widget:** an aggregation explorer ($m$ slider: the
annualized volatility from $m$-day sums against $\sqrt A\,s$, with VR($m$)).

**Hygiene.** *Descriptive*; the two limit regimes as a *Stability check*.

**Brief settles.** The robust shape measures and their sources; overlapping against non-overlapping sums (the
overlap's own dependence, said once); the one sample on which the three annual numbers are compared.

### LM20 Estimation Theory and Maximum Likelihood

**Question.** How precisely do 23.8 years of TAIEX data pin down the expected return? $A\bar R$ is about 15.4% a year
with a standard error near 3.9 points (explored); sampling every 5 minutes would not shrink that error, because the
precision of a mean depends on the calendar span, while the precision of a variance improves with the sampling
frequency (Merton 1980).

**Prereq (draft).** LM4 (the interval at lm04.md:541–547), LM5 ((5.12), the normal fit), LM10 ((10.4)), LM14, LM15
(the $t$ fit, (15.6)), LM16 ((16.3)), LM17 ((17.1), (17.5)), LM18 ((18.8)), LM19.

**Forward links to honour.** lm04.md:541 and 573 (derive $s/\sqrt T$, develop confidence intervals; the example SE
0.0230% a day, interval 0.042%–0.132%, Kelly band 2.7–7.6); `make_lab04.py:506`; lm05.md:449 (divisor $T$ "is the
maximum-likelihood choice"), lm05.md:497 (estimates $\nu$); lm07.md:507 (SE $\approx\sigma/\sqrt{\text{years}}$: 7.36
points for 0050, 6.09 for 00679B); lm10.md:166 ($T-1$ removes a small bias "under assumptions that [[LM20]] states");
lm11.md:406 and `make_lab11.py:571` (an eigenvalue's sampling error, "[[LM20]] gives the tools"; the example is
LM22's); lm14.md:51 and 211; lm15.md:62, 349, 419, 440, 615 (standard errors in general; $\nu=3.065$; regimes without
standard errors; "estimates a tail index with its standard error"; the regime fits); lm16.md:177 (the error of
$\hat\rho=0.5749$); lm17.md:71 and 310 ($s$ in place of $\sigma$; $n\ge9{,}604$ a model property); lm18.md:149, 345
and 527 (standard errors and intervals for data; "derives the same $s/\sqrt T$", 0.01580%).

**Owns.** An estimator as a random variable and its sampling distribution (shown by simulation from a model); bias,
variance, MSE and their trade-off (a scaled mean $\eta\bar R$ as the bridge to LM24); consistency, stated;
$\operatorname{SE}(\bar R)=\sigma/\sqrt T$ from (16.3) and (17.1), estimated by $s/\sqrt T$; the bias of $s^2$ and
the unbiased $s_{\mathrm u}^2$; confidence intervals for $\mu$ (normal approximation by (17.5); the $t_{T-1}$
interval for a normal model); Merton's point: the standard error of an annualized mean is the annual volatility over
$\sqrt{\text{years}}$ at any sampling interval, while the variance estimate sharpens with frequency (its standard
error depends on the kurtosis); the sampling error of 23 annual values (LM19's gap); likelihood, log-likelihood, the
normal MLE ($\hat\sigma=s$), the MLE of $\mathcal N_N$ stated (why $\hat\Sigma$ divides by $T$), Student-$t$ MLE
(LM15's fit, now with standard errors from the observed information); Fisher information and asymptotic normality,
stated; Cramér–Rao, stated (attained by $\bar R$ in the normal model); the delta method: the annualized volatility,
the Kelly fraction $\bar R/s^2$ and the Sharpe ratio under iid returns; the Hill estimator of the tail index with its
standard error (LM15's promise), as one example against LM15's chords.

**Leaves.** Tests and p-values → LM21; bootstrap standard errors and intervals → LM22; regression standard errors →
LM23; Bayesian intervals → LM24; GARCH likelihood → LM26 (uses LM20's machinery); the Sharpe ratio under non-iid
returns → LM33.

**Data.** TR23; U28's pair for $\hat\rho$ (LM16's sample, in a problem); LM4's 0050 numbers recomputed under LM20's
name if the brief uses them. Simulations under the seed rule.

**Candidate exhibits.** The sampling distribution of $\bar R$ and of $s$ under an iid model fitted to TR23, by
simulation; the 95% interval for $A\bar R$ against years of data; Merton's chart: the standard error of the annual
mean and of the annual variance against the sampling interval (log $x$ if approved); the log-likelihood of the $t$
fit against $\nu$ with its curvature. **Widget:** coverage of a 95% interval (normal or $t$ model, $T$ slider,
seeded).

**Hygiene.** *In-sample* estimates; *Model* simulations; regimes as a *Stability check* (LM15's fits with standard
errors).

**Brief settles.** The two-parameter MLE example; the Hill estimator's tail count and its source check; which LM4 and
LM7 promises are recomputed and which quoted; what goes to problems (the $\hat\rho$ delta method) to stay within
6,000 words.

### LM21 Hypothesis Testing and Multiple Testing

**Question.** Is the TAIEX's mean return positive, and is there a best month to own it? TR23's t-stat is about 3.96
(explored; about 2.05 before June 2015 and 3.68 after). Test 12 months and 5 weekdays and some will look special by
chance; search many rules and the best t-stat grows with the search. The $t>3$ hurdle (Harvey, Liu and Zhu 2016)
follows.

**Prereq (draft).** LM13 ((13.2), the union bound), LM15 ((15.1), (15.8), (15.9)), LM16 (the $\chi^2_N$ law, (16.9)),
LM17 ((17.5)), LM19, LM20.

**Forward links to honour.** lm13.md:59, 218, 536 (1,226 down-after-down days against 1,195.0 under independence, "31
days in 5,848"); `make_lab13.py:463`; lm15.md:62, 104, 615 (block variance 4.72 against 5.16 and 4.95;
$\rho_1=0.0215$; the regimes); lm16.md:62, 88, 369, 384, 430, 514 (3.29, "a descriptive ratio, not evidence";
$\chi^2$ tests; 177 days against a binomial mean 48.68 and SD 6.94; 0.788 against 0.860, whose interval is LM22's);
`make_lab16.py:571` (regime correlations 0.6544 against 0.5564; 93 against 84 days beyond radius 3);
research-hygiene.md:7, 29, 62 ("[[LM21]] and [[LM33]] measure that risk"; "covers multiple testing").

**Owns.** Null and alternative, test statistic, null distribution, p-value, size, rejection region, type I and II
errors, power; the one-sample t-test of a mean (normal and $t_{T-1}$ reference) and its duality with LM20's interval;
power and sample size: the years needed to detect an annual Sharpe ratio at a given level and power; tests of a
frequency (binomial, normal approximation, $\theta$ for the probability under test) and the $\chi^2$ test of
independence for LM13's 2×2 sign table, with the caveat that clustering breaks the independence of days; the
two-sample Welch test (the limit regimes; a month against the other days); multiple testing: family-wise error,
Bonferroni, Holm, the false discovery rate and Benjamini–Hochberg (independence condition stated; Benjamini–Yekutieli
in one sentence); the calendar family of 17 tests under each rule; the $t>3$ hurdle and what a search does to the
largest t-stat (a simulated family under a seeded null, mainly in the widget).

**Leaves.** Bootstrap tests and tests under dependence → LM22; regression t and F tests, and the 28 sector alphas
under LM21's corrections → LM23; the robust autocorrelation and variance-ratio tests, Ljung–Box and unit-root tests →
LM25; ARCH tests → LM26; Sharpe ratio tests, PSR and DSR → LM33; backtest overfitting, the reality check and PBO →
LM34 (named here, with White 2000 and Romano–Wolf as references). The Jarque–Bera test goes to a problem.

**Data.** TR23; seeded simulations.

**Candidate exhibits.** The null distribution with the observed t-stat; power against years for annual Sharpe ratios
0.25, 0.5, 1; the 17 calendar t-stats as a bar chart; sorted p-values against the Bonferroni and BH lines; the largest
t-stat of $m$ null strategies against $m$ (log $x$ if approved). **Widget:** a multiple-testing simulator ($m$ null
tests, seeded; the largest t-stat and the BH line), or power and sample size.

**Hygiene.** *In-sample* tests, with the number of tests stated; regimes as a *Stability check*; simulated nulls
*Model*.

**Brief settles.** Which TR23 sign or frequency test honours lm13.md:218 and lm16.md:384 without claiming independence
the data do not have; the calendar family's exact definition (months and weekdays as stated, each against the rest);
the anchored outcome, reported whatever it is.

### LM22 Resampling Methods

**Question.** How wide is the interval for the TAIEX's Sharpe ratio and for its Kelly fraction, and does the answer
change when the resampling keeps the clusters? TR23's daily Kelly fraction $\bar R/s^2$ is about 4.3 (explored); LM4
gave 0050 a band of 2.7 to 7.6.

**Prereq (draft).** LM4 (the Kelly band, lm04.md:547–551), LM11 (PC1's share), LM16 (the crash correlation), LM17,
LM18 ((18.1)–(18.3), (18.8), (18.9)), LM19, LM20, LM21.

**Forward links to honour.** lm11.md:406 (an eigenvalue's sampling error); lm16.md:62 and 514 (the crash correlation
0.788 against 0.860, "whether a gap could be chance is for [[LM21]] and [[LM22]]"); `make_lab16.py:571`; lm18.md:50,
366, 373, 381, 389 ("resamples blocks"; the windows' $\Pr(G<1)$ 4.1% with "none here"; "their error needs a bootstrap
of blocks"; "reading a range of resamples as an interval … left to [[LM22]]"); `make_lab04.py:642` (the walk-forward
Kelly, "LM22 … and LM45 return"). Stay consistent with LM18's iid results (5.6% ± 0.2; quantiles 0.97, 1.94, 3.94;
SD of $\ln G$ 0.424 ± 0.003; resampling destroys clustering, lm18.md:379) and LM7's Sharpe ratios.

**Owns.** The bootstrap principle as inference (LM18 owns the mechanics): bootstrap standard error, the percentile
and basic intervals, BCa stated (SciPy's default); when the iid bootstrap fails (dependence: the variance of a 20-day
sum, the autocorrelation of $\lvert r\rvert$); the moving-block, circular and stationary bootstraps; block length
(Politis and White's automatic choice if arch is approved; otherwise a stated rule and a sensitivity table);
intervals for the Sharpe ratio and the Kelly fraction by iid and by block resampling, compared with LM20's delta
method; a block-bootstrap interval for a variance ratio (LM19's statistic); the interval for LM16's crash correlation
and for LM11's PC1 share from 250 returns; a bootstrap test (resampling under the null) for one LM21 question; the
error of LM18's windows (lm18.md:373).

**Leaves.** Sizing from the bootstrap distribution, bootstrap Kelly → LM45; resampled portfolios → LM30; the reality
check and PBO → LM34; the Sharpe ratio's analytic standard error under non-iid returns → LM33.

**Data.** TR23; U28 for the crash correlation and PC1's share. Every resample under the seed rule.

**Candidate exhibits.** Histograms of bootstrap Sharpe ratios, iid against block, with their intervals; interval
width against block length (log $x$ if approved); the Kelly interval against LM20's delta-method interval (forest
plot); one resampled path that keeps clusters beside one that does not. **Widget:** a block-bootstrap explorer (block
length, statistic, $B\le1{,}000$, seeded with `Book.rng`).

**Hygiene.** *In-sample* intervals; resampled paths are *Model*.

**Brief settles.** Which statistic shows the block bootstrap's difference most clearly on TR23 (the Sharpe ratio may
not, a 20-day variance does); how arch's bootstraps take the generator; the block length used for every printed
number.

### LM23 Linear Regression

**Question.** What is a sector's beta, how sure are we of it, and is its alpha real? The market model of each U28
sector on the TAIEX price index gives betas from about 0.51 (CommunicationsInternet) to 1.21 (Semiconductor) (fresh
check); standard errors change with the method (classical, White, Newey–West), overlapping returns need HAC errors,
and among 28 alphas one t-stat passes 1.96 where chance predicts 1.4.

**Prereq (draft).** LM2 (the slope 1.887), LM8 (hedges), LM9, LM10, LM11 (named factors, lm11.md:309), LM12
((12.1)–(12.4), (12.6): projection, residuals, R-squared as geometry), LM16 ((16.2), (16.6), (16.8)), LM20, LM21.

**Forward links to honour.** lm02.md:492–496 (00631L on 0050: slope 1.887 over 2,902 daily total-return pairs,
correlation 0.974, by year 1.717 to 1.984, unadjusted closes 0.846); lm08.md:112 ("[[LM23]] sizes hedges by
regression"); lm09.md:412; lm11.md:309 (an economic factor model names its factors in advance and estimates exposures
by regression); lm12.md:124 (R-squared "as a statistic"); lm16.md:348 and 354–355 ("its standard error is [[LM23]]'s":
$\beta=0.4591$, residual SD 0.996%); lm18.md:153 (the batch standard error of a slope, 2.18 ± 0.01 against 2.1584).
Stay consistent with lm12.md:19–20, 169, 604.

**Owns.** Simple and multiple OLS in matrix form (citing LM12's projection; $\hat{\boldsymbol\beta}=(X^\top X)^{-1}
X^\top\mathbf y$); the assumptions and the Gauss–Markov theorem stated for linear unbiased estimators (Hansen 2022 and
its comment read before stating more); $s_\varepsilon^2=\text{RSS}/(T-d)$; standard errors, t-stats, intervals;
R-squared as a statistic (adjusted R-squared and the F test in one sentence each); White's
heteroskedasticity-consistent errors; Newey–West HAC (Bartlett weights, the lag choice, `use_correction`); the market
model, beta and alpha; the CAPM's statement and why a raw-return intercept on price indices is not Jensen's alpha
($r_f$ and dividend yields); the 28 alphas under LM21's corrections; a hedge ratio by regression on U28 (LM8's
promise); an economic factor model with a factor named in advance (the Electronic index's excess over the TAIEX,
*constructed*) and the collinearity it brings.

**Leaves.** Regression on nonstationary series (spurious regression) → LM25; LM26's auxiliary regressions → LM26;
factor risk in portfolios → LM27 (bookkeeping) and LM30; cross-sectional asset-pricing tests (Fama–MacBeth) → not in
the book, one sentence.

**Data.** U28 (28 sectors on the TAIEX price index; the Electronic index for the factor); LM2's 0050/00631L sample for
lm02.md:492.

**Candidate exhibits.** A scatter of one sector on the TAIEX over one year with the fitted line, confidence and
prediction bands; the 28 betas with intervals (forest plot), classical against HAC; standard errors of a 20-day
overlapping regression, classical against Newey–West; the 28 alpha t-stats with the Bonferroni and Holm lines.
**Widget:** a regression explorer over precomputed per-sector statistics (sector, window, error method), or a
leverage-point demonstration.

**Hygiene.** *In-sample*; rolling betas and the halves as a *Stability check*.

**Brief settles.** The HAC lag rule; whether the factor model's second factor is the electronics excess return (no new
data) or needs another series; the year shown in the scatter.

### LM24 Bayesian Inference and Shrinkage

**Question.** Should you believe a sector's past mean return, and how much of the Kelly bet should a sceptic place?
Estimated on the first half of U28 and judged on the second, the 28 sector means do best when shrunk all the way to
their average (fresh check): their spread is smaller than their noise. Under log utility, GBM returns with known
$\sigma$ and a normal prior centred at zero, the Bayes bet is Kelly at the posterior mean, which is the plug-in Kelly
bet times the data's weight in the posterior: fractional Kelly inside a stated model.

**Prereq (draft).** LM4 (Kelly, lm04.md:558), LM13 ((13.9), (13.10), the manager example), LM14, LM15, LM16 ((16.5),
(16.6), (16.8)), LM20, LM21, LM23.

**Forward links to honour.** lm04.md:558 (fractional Kelly at "a quarter to a half of $f^*$. [[LM24]] and [[LM44]]
formalize it"); lm13.md:334–336 (the manager: prior 10%, 8 good months of 12, likelihood ratio 1.4064, posterior
13.5%; "applies the same rule to an unknown parameter"). Stay consistent with lm04.md:563 ("size from a haircut
estimate"), lm11.md:480 and lm07.md:509 (repairs belong to LM30 and LM45).

**Owns.** Bayes' rule for a parameter (prior, likelihood, posterior); the beta–binomial model (the manager's success
probability with a $\operatorname{Beta}(\alpha_0,\beta_0)$ prior, as a static exhibit); the normal model with known
variance (posterior precision = prior precision + data precision); credible against confidence intervals; the
James–Stein estimator with its conditions, its empirical-Bayes reading and U28's out-of-sample test, reported as the
data give it; the Bayes Kelly fraction $c\bar R/\sigma^2$ in the stated model, its size on TR23 for several priors
(the sceptic's prior that LM4's "quarter to a half" needs), and what breaks it (unknown $\sigma$, fat tails, other
utilities).

**Leaves.** Covariance shrinkage and Black–Litterman → LM30; CRRA utility and fractional Kelly as risk aversion →
LM44; parameter uncertainty in practice, bootstrap Kelly → LM45; shrinking betas, hierarchical models and MCMC → not
in the book, one sentence each.

**Data.** TR23 (the posterior of the mean and the Kelly fraction); U28 split into LM11's halves; LM13's manager example
(hypothetical, as printed).

**Candidate exhibits.** Prior, likelihood and posterior on one chart; the beta–binomial posterior for the manager; 28
raw means against shrunk means, first half against second half (forest plot); out-of-sample error against the
shrinkage factor; the Bayes Kelly fraction against the prior's standard deviation. **Widget:** prior–posterior
explorer (prior SD, years of data) showing the posterior mean and the implied fraction $c$.

**Hygiene.** *In-sample* posteriors; the split-half test *Out-of-sample*; the Kelly result *Model*.

**Brief settles.** The James–Stein variant (known or estimated common variance; positive part) and its source
equation; whether removing the common component (the cross-sectional mean each day) gives a fairer test; the
derivation's approximation and its size on TR23 (second-order growth against GBM's exact rate).

### LM25 Time Series I: ARMA, Unit Roots and Cointegration

**Question.** Is the futures–spot basis mean-reverting while the index is not? On TX23, $\ln S_t$ behaves like a
random walk and the log basis $\ln F_t-\ln S_t$ returns toward its carry, with a half-life of days; since theory fixes
the cointegrating vector at $(1,-1)$, a unit-root test on the basis is a cointegration test. LM6's basis becomes a time
series.

**Prereq (draft).** LM6 ((6.25), the basis decomposition, the dividend season), LM12, LM16, LM19 ($\hat\rho_k$,
VR($m$)), LM20, LM21, LM23.

**Forward links to honour.** lm06.md:650 ("[[LM25]] models it as a mean-reverting spread"); stay consistent with LM6's
decomposition (carry − dividends + residual, the $r_f=2\%$ proxy, actual/365; the 2025 numbers at lm06.md:583,
597–603, 616–624, 672, 676) and with the lag-1 values printed in LM15, LM16 and LM17.

**Owns.** Weak stationarity, white noise, the random walk; the autocorrelation and partial autocorrelation of AR(1)
and MA(1) models; the robust autocorrelation band and the Ljung–Box test (TR23 returns, citing LM19's values); the
variance-ratio test named with its robust form; AR estimation by OLS and the half-life; ARMA named and fitted once;
the unit root: the Dickey–Fuller regression, why its t-stat is not $t$ distributed (a seeded simulation), ADF lags,
MacKinnon p-values; KPSS in one paragraph as the reverse null; spurious regression (two independent random walks,
seeded); cointegration with a known vector (the basis) and Engle–Granger named for an estimated one, with an
error-correction model in one sentence; the basis's convergence at expiry, the roll, and the dividend season as a
seasonal mean.

**Leaves.** Ornstein–Uhlenbeck in continuous time → LM39; volatility models → LM26; Johansen and threshold
cointegration → named, one sentence each (Taiwan studies cited); pairs trading → not in the book.

**Data.** TX23; TR23 returns for the Ljung–Box and ARMA examples; seeded simulations.

**Candidate exhibits.** $\ln S_t$ and the log basis in two stacked charts; ACF and PACF of the basis; the DF t-stat's
simulated distribution against $t$; two independent random walks with their spurious regression; the basis around
expiry days. **Widget:** an AR(1) path simulator ($\phi_1$ from 0 to 1, seeded), showing the half-life and the random
walk at $\phi_1=1$.

**Hygiene.** *In-sample*; subperiods as a *Stability check*; simulations *Model*.

**Brief settles.** Settlement or close for $F_t$ and the 15-minute gap to the TAIEX close (lm06.md:672; option E);
the deterministic part removed before testing the basis (a constant, the carry $(r_f-q)\tau$, the dividend season)
and the notation for $q$ if used; the sample start (TR23's 2003).

### LM26 Time Series II: Volatility Models

**Question.** What will the TAIEX's volatility be tomorrow? EWMA, GARCH(1,1) and yesterday's realized variance
compete, judged out of sample against 5-minute realized variance from T5S, with a loss that a noisy proxy cannot
fool (Patton 2011).

**Prereq (draft).** LM3 ((3.11) $\mathrm{RV}$), LM5, LM13 (falls after falls), LM15 (overdispersion), LM16 (the
size correlation), LM17 (the $\lvert r\rvert$ correlations), LM19, LM20, LM21, LM23.

**Forward links to honour.** lm05.md:529 (1.859% a day is 29.0% a year; clustered −5% days); `make_lab05.py:529`
(trailing 60-day $\sigma$, EWMA); lm13.md:159 (12.04% after a fall against 4.48% and 1.85%); `make_lab13.py:463`;
lm15.md:163, 170 (monthly counts overdispersed 3.02 times); lm16.md:170 (sizes correlate 0.183; 1.28% after a big move
against 0.75%; U28 numbers); lm17.md:392 ($\lvert r\rvert$ correlates 0.161 at lag 1 and 0.123 at lag 20; $r$ 0.039;
pair correlations); lm18.md:381; reviews/lm17.md:36 (the convention, now LM19's).

**Owns.** Volatility clustering as a model's target; Engle's ARCH test (one paragraph); EWMA as a weighted variance,
its effective window and RiskMetrics' $\lambda=0.94$; GARCH(1,1): definition, positivity and stationarity conditions
($\omega>0$, $\alpha,\beta\ge0$, $\alpha+\beta<1$), the unconditional variance $\omega/(1-\alpha-\beta)$ in %², persistence
and half-life; its MLE fit on TR23 (normal errors; Student-$t$ errors as one table row) and multi-step forecasts;
realized variance from T5S: the sum of squared intraday log returns, the volatility signature over sampling
intervals from 5 seconds to 30 minutes, why an index's stale prices bias it down at high frequency, the closing
auction's frozen minutes, the overnight return; forecast evaluation out of sample with MSE and QLIKE, and the
Mincer–Zarnowitz regression (one paragraph).

**Leaves.** VaR from a volatility forecast → LM32; volatility targeting → LM31; stochastic volatility in continuous
time → LM39; covariance forecasting → LM30 and LM31 (a sentence); HAR models and two-scale estimators → named, one
sentence each.

**Data.** TR23 (daily models); T5S (realized variance); option E only if approved.

**Candidate exhibits.** Daily $\lvert r\rvert$ with EWMA and GARCH volatility; the signature plot; out-of-sample
forecasts against realized variance for one turbulent year (2020 or 2025); the losses of the three forecasts by year.
**Widget:** EWMA $\lambda$ slider over TR23 against realized volatility, or GARCH $(\alpha,\beta)$ sliders with the
forecast's term structure.

**Hygiene.** *In-sample* fits; *Out-of-sample* forecast comparison with rolling estimation; the signature plot
*Descriptive*.

**Brief settles.** The rolling window and refit frequency; how the overnight return enters the daily target (T5S
starts at 09:00, TR23 is close to close); the loss functions' units; the year shown in detail.
