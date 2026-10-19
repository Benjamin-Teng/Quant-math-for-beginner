# Volume IV — Statistical Inference and Econometrics: shared decisions and briefs

Volume IV turns the probability models of Volume III into estimates a reader can defend. A sample mean becomes an
estimator with a standard error, a frequency a test, a slope a regression coefficient with an interval, a past mean a
prior to be shrunk, a price series a process with or without a unit root, and a day's squared return a noisy view of
a variance that changes over time. The volume teaches each tool on Taiwan data, says what it assumes and shows where
the assumption fails (ROADMAP, "Module boundaries").

The reader reads English as a second language and wants the tools learned systematically (SPEC §2). Worked examples,
diagrams and formulas carry each module; the prose connects them. Volumes I–III are published: link to their results
with [[LMn]] instead of repeating them, and honour every forward link they make to LM19–LM26 (listed per brief).

This file holds the editor's Stage 1 decisions (2026-10-19): the shared decisions, the capability check and the
owner's answers, the decisions on the survey, its fresh check and the drafts, and one brief per module. Each brief
was drafted by one agent from the editor's spine (the spines are in `plans/vol-4.md` at commit bcfa0d4, not in this
file), checked across the volume by a fresh agent, its anchors recomputed independently from the data, decided by
the editor and revised. Every number a brief quotes is an anchor in
`plans/vol-4-anchors.md`, printed by `data/vol4_anchors_lmNN.py`. Until Stage 3 this brief and the anchors are the
plan; from Stage 3 the module sources and their numbers scripts are authoritative (as in `plans/vol-3.md`).

## Shared decisions

- **Length and voice.** AUTHORING §1: at most 6,000 words of prose and 36 pages; first drafts under 5,500 words;
  sentences average under 16 words and never exceed 30; paragraphs at most 80 words; connectors kept.
  `uv run python build/qa/style.py src/lmNN.md` shows no FAIL before a draft is handed back. Volume III's modules ran
  about 5,700 words in six or seven sections; each brief below is cut to fit that.
- **Section pattern.** A small numeric case or a picture first, then the definition, estimator or test with all its
  conditions, a short derivation, a worked example on Taiwan data, at most one pitfall, the 中文導讀 and the
  knowledge check. Each estimator is first computed by hand in NumPy from its formula; a package is then
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
    and 3,241 (5 seconds) from 2014-12-29 (the 10-second regime ends on Saturday 2014-12-27); `fetch_intraday.py
    --check` prints each regime's first and last day. FinMind prints the previous close at 09:00:00, and the index
    absorbs the opening gap within about a minute; the 13:30:00 value equals the official close; the index freezes
    during the closing call auction (13:25:05 to 13:29:55 from 2014-12-29). `data/vol4_rv.py` builds per-day
    realized variances on the common window 09:30:00–13:30:00 at nine intervals (5, 10, 15 and 30 seconds; 1, 5,
    10, 15 and 30 minutes) with their counts, and `o2`, the squared log change from the previous close to 09:30:00
    (the overnight gap and the first half hour), into the committed `data/derived/vol4_rv.csv`. LM26: a 5-minute
    daily series from 2005 and the sampling-interval study from 2015.
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
  (block bootstrap), 平穩自助重抽法 (stationary bootstrap), 實現變異數 (realized variance, as LM3 printed it), 實現波動率 (realized
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

## Capability check (2026-10-19)

What the spines need and the repository lacks (survey and fresh check: `book.js`, `build/`, `data/`,
`pyproject.toml`). **The owner approved A, B, B′, C and E on 2026-10-19 (ROADMAP, "Decided by the owner"); D is not
approved.** Each approved piece is reviewed by a fresh agent (0 differences on the published pages).

- **(A) Packages.** statsmodels 0.15.0 (BSD-3) and arch 8.0.0 (NCSA); arch requires statsmodels, so they are one
  decision. They bring pandas 3.0.6, patsy 1.0.3, formulaic 1.2.2, narwhals 2.27.1, wrapt 2.5.1, interface-meta 2.0.1
  and tzdata 2026.5: about 82 MB unpacked, cp313 Windows wheels for all, metadata-compatible with the locked NumPy
  2.5.3 and SciPy 1.18.1. The smoke test of 2026-10-19 ran the stack without error (SOURCES, "Python (Volume IV)"). Needed for: MacKinnon p-values of the
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
     entry per day: date, rows, SHA-256), downloads about 5,350 days into `data/raw/intraday/taiex5s/<year>/` (about 310
     MB of CSV, on the owner's disk only), logs rows per day, resumes after an interruption and stops at the hourly
     quota (about 90 minutes on the Sponsor plan at the script's pace). It checks every day: the row count of its regime, strictly increasing
     times, no repeated day, the 13:30:00 value against the TAIEX close in `TaiwanStockPrice` (an independent series,
     PITFALLS §3). `fetch_finmind.py --verify` never reads T5S, and `./build.sh --data` rebuilds the derived file only from a
     complete download that passes every check.
  3. Shared files: `make_lab_data.py` entries for LM19–LM26, `build.sh` `DATA_STEPS`, `data/README.md`, AUTHORING
     §8–§9, SOURCES.
- **(B′) What is committed from T5S** (the owner's call on the licence). FinMind's Pricing page marks
  "再散布原始資料、建立鏡像 API" as not allowed, and its Disclaimer (§2, §3.2–3.3) forbids redistributing its data and
  asks for credit to the original agency. Proposed: commit one derived file, `data/derived/vol4_rv.csv`: per day, the
  realized variance at nine sampling intervals and the number of returns in each, and the squared opening change
  `o2` (editor, after the review: the 09:00:00 value is the previous close, so the grids start at 09:30:00 and the
  gap gets its own sign-free column; about 5,350 rows, under 1 MB),
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
- **(D) `Book.dist` and `Book.rng` for inference (not approved).** Widgets use `PhiInv` and draw a Student $t$ with
  an integer $\nu$ from normals in the module's own code. Proposed were `Book.dist.tInv` (LM20's $t_{T-1}$ interval, LM21's widget) and
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
  falls below 1 (0.783 at $m=492$ and 0.619 at $m=1{,}231$ centred at $m\bar r$, as decided below; the overlapping
  estimator is biased down there). So LM19
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
  for a prior standard deviation of 10 points a year; LM4's "a quarter to a half" needs a sceptic's prior of 2.25
  to 3.89 points. The module says so.
- **Package facts corrected:** `use_t=False` under HAC is statsmodels' switch (normal p-values); arch's `pvalues` are normal
  too (`stats.norm.sf`).
- **Defects in published pages, fixed at Stage 4** with the Volume IV publication: the literal `[[LM20]]` in the
  LM11 lab (`build/make_lab11.py:571`, flagged in reviews/lm12.md:171); the front matter `leads` that miss Volume IV
  targets their text already links (lm02 23; lm03 19; lm04 19, 24; lm05 19, 20, 26; lm07 20; lm11 20, 22; lm18 23),
  checked again then against the final briefs; Volume III's brief cites LM18's old equation numbers (plans/vol-3.md,
  frozen): Volume IV cites the published (18.4), (18.7), (18.8), (18.9).

## Editor's decisions on the LM19–LM25 drafts (2026-10-19)

Seven drafters wrote the briefs and anchor scripts from the spines; a fresh agent cross-checked them as a set (findings
X1–X40) and seven fresh agents recomputed every anchor from the definitions and the data (all 415 reproduced; A19-56's median had followed np.median against the
stated quantile rule, which was then applied). The
editor's decisions follow; each brief is revised to them, and LM26's brief starts from them.

- **No full daily series in published files** (X37). No chart, widget or other published file carries a daily series
  derived from FinMind data in date order at full resolution: prices, returns, or anything from which they can be
  rebuilt (a daily EWMA or GARCH variance with its inputs, for example). A chart over many years is thinned to weekly
  points plus every value the text cites; a widget embeds precomputed statistics (LM22's resample histograms, about
  100 KB). Sorted values (an ECDF, a QQ plot) and statistics of the series are allowed, as in Volumes II–III (no
  published file carries more than 1,172 dated points of a market series). LM25's X1 and LM22's widget change; LM26
  follows the rule from the start.
- **Owners** (X1–X8). LM19 owns TR23's $\sqrt A\,s=18.96\%$ and Sharpe ratio $0.0517$ a day, $0.81$ a year, both on
  $R$ with $r_f=0$ (log-return values in brackets); LM20 owns $\hat f=4.28$ and every standard error and interval
  (its delta table prints three decimals: 0.207, 0.205; 1.111, 1.085, 1.082); the other modules cite them. LM24
  cites LM21's t-stat with $s_{\mathrm u}$ (3.955678) and says that its own value differs only by the divisor. LM22
  sets its regime test beside LM21's 0.041 and names the reference distribution. LM20 writes the up-day frequency as
  $\hat\theta$. LM24 drops LM23 from its prerequisites (a pointer only) and LM23 drops 24 from its leads. LM21 keeps
  the shuffled-date null (*Model*); statistics computed from LM16's printed counts say so.
- **One variance-ratio estimator** (X9, X10). $\operatorname{VR}(m)$ is LM19's (19.8): overlapping $m$-day sums of log
  returns centred at $m\bar r$, over $m$ times the daily variance; LM22 bootstraps it and LM25 tests
  $(\operatorname{VR}(m)-1)/\operatorname{SE}$ as a large-sample approximation. The weighted sum $1+2\sum(1-k/m)\hat\rho_k$
  appears only as LM19's identity column; the test is attributed to Lo and MacKinlay only after their text is read.
  The spine's 0.75 and 0.44 (own-mean centring) become 0.783 and 0.619.
- **Robust standard errors** (X11). HC0 for heteroskedasticity; Newey–West with Bartlett weights and
  $\lfloor4(T/100)^{2/9}\rfloor$ lags (statsmodels' default HAC lag, which is Newey and West's (1994) pilot lag,
  not their recommended lag: the text says so; arch rounds up and is not used for it), no small-sample
  correction, normal reference. LM19's and LM25's robust standard error of $\hat\rho_k$ is HC0-type.
- **Resampling** (X12). Printed numbers use the stationary bootstrap with the book's block-length rule (LM22: one
  length per sample and statistic family, the largest Politis–White stationary estimate among the squared demeaned
  simple-return series the statistic involves, rounded: 145 for every TR23 statistic, whether on $R$ or on $r$),
  never
  called "the" right length; circular blocks get one sentence; $B=10{,}000$ unless stated.
- **Tests** (X13). A normal reference and two-sided tests unless the text says otherwise; Dickey–Fuller and KPSS are
  one-sided and say so; Ljung–Box uses the upper tail.
- **Quantiles, medians, Monte Carlo errors.** Every quantile and median, of data and of simulated or resampled values,
  is $\hat F^{-1}(u)$ (`method="inverted_cdf"`, LM14's quantile function); LM19's 246-grid median becomes 19.13%
  (19.1254%, flagged). A batch standard error follows LM18 (20 batches, divisor 20). A statistic without a finite
  variance across samples (the standard deviation of $t$ draws with $\nu<4$) gets no normal-theory Monte Carlo error:
  print the spread across seeds instead (LM20's experiment 1: "about 4").
- **Rounding.** Every printed value within a tenth of a unit of its rounding boundary is flagged in its anchor row, at
  the precision it is printed; an exact tie prints more digits or a coarser form whose rounding is safe (LM23's 0.69645 prints 0.696). Printed forms are rounded from unrounded values, never from a rounded Value column (LM22's
  130.0, not 130.1).
- **Calendar.** TR23's 23 Saturday sessions (2006–2018) stay in every group (LM21's treatment); TWSE's history page states
  that the market stopped trading on Saturday make-up workdays from 2019 (SOURCES, "Taiwan facts (Volume IV)"); that
  the 23 sessions were such days is an inference and is written as one. A year on 2003–2025 is LM17's 246 sessions.
- **LM25's ARMA** (X16, recompute finding 1). The default fit stops short of the likelihood maximum: fit with
  `method="innovations_mle"` (or restart from it), assert that the log-likelihood does not rise further, and take
  standard errors from the observed information, the numerical Hessian of $-\ell$ (`cov_type="approx"`; statsmodels'
  `"oim"` is Harvey's formula), as LM20 teaches. Walks are $x_t=z_1+\dots+z_t$. The fit's last unprinted digits
  depend on the optimizer's tolerance (about $10^{-7}$ from a Newton-refined maximum; four Value-column digits of
  A25-54 and A25-56 sit on a boundary there), so `lm25_numbers.py` compares ARMA values at their printed precision.
- **LM23** (recompute findings). Residual dispersion by tercile is the root mean square (what White's errors use),
  with the cut rule stated; overlapping-residual autocorrelations use LM19's $\hat\rho_k$; a t-stat says its method;
  the contract count of a TX hedge uses $200F_t$ (LM8's convention; TX23's $F_t$ on the last date), not the index.
- **Words.** "Leverage" stays the book's ($f>1$, 00631L's $L=2$): LM23 calls a regression point's influence its
  hat value. "Microstructure noise", stale prices and price bounce are named as hypotheses in LM25 and LM26, never
  as established mechanisms.
- **Notation** (X17–X24; AUTHORING §6 amended). $\ell$ is LM22's block length and LM23's Newey–West lag (neither
  writes a likelihood); LM19 writes the median $\operatorname{med}$ (a tilde means centred); $\hat f:=\bar R/s^2$ from
  LM20, $\hat f^*$ the exact in-sample root of (4.5) (LM22, LM24), $f_{\mathrm B}$ LM24's Bayes fraction with
  $f_{\mathrm B}=c\hat f$; $c$ is the data's weight in each LM24 model; LM24's $n_0$ and grand mean $\bar{\bar R}$,
  LM25's $b_t$, $a_j$, $J$, $u_t$, $\zeta_t$, $\alpha_F$, $\alpha_S$, $Q_{\mathrm{LB}}(K)$, $\tilde r_t$ and
  $\operatorname{SE}_{\text{iid}}$, $\operatorname{SE}_{\text{rob}}$, LM23's $\mathbf x_t$ (row $t$ of $X$ is
  $\mathbf x_t^\top$), $\Sigma_\varepsilon$, $q_i$, $q_{\text{mkt}}$, $R_{\text{mkt}}$, $R_{\text{el}}$, $\Gamma_k$,
  $h_t$, $\alpha_{\mathrm J}$ and $\beta_{j,\text{null}}$, and LM22's Deep Dive $\sigma_\psi$ are local, declared;
  LM25's $m$ is only the VR horizon.
- **Leads and tags** (X25–X29). As the cross-check lists them; the Stage 4 table below replaces the earlier list.
- **Sources** (X32–X36). The $t$ and $\chi^2$ laws of normal samples are cited to Blitzstein and Hwang as SOURCES
  records them (read 2026-10-19): Ex. 10.4.3 for $(n-1)S^2/\sigma^2\sim\chi^2_{n-1}$, Ex. 7.5.9 for the
  independence of the mean and variance, Def. 10.4.4 for $t_n$; the book does not state the $t_{n-1}$ law of the
  studentized mean, so LM20 and LM21 show its one-line derivation from those three; LM20's $\chi^2$ interval for the
  23 annual values returns, cited to Ex. 10.4.3, under the normal model it states; the $\chi^2$ density and a
  regression's $t_{T-d}$ stay *stated without proof*;
  Gauss–Markov stays at chapter level (Hayashi §1.3 or Greene ch. 4), for linear estimators only. SOURCES' arch line
  is corrected (`optimal_block_length` returns columns `stationary` and `circular`; the docstring says otherwise). The
  briefs' Python facts, new references and 樂詞網 terms are checked and recorded in SOURCES before Stage 2. No Welch
  paper (call (21.3) a two-sample statistic with unpooled variances), no AIC paper, the CAPM cited to Campbell, Lo and
  MacKinlay ch. 5 with Sharpe and Lintner as origins; LM19's robust measures and adjusted moments are printed as
  definitions, attributed only after the papers are read.
- **Scope** (X38–X40). LM22 cuts 60 words; LM23's interval lines stay unnamed; LM23's walk-forward hedge stays,
  labelled "one rule fixed in advance", with a pointer to LM34.
- **The drafters' other questions** are answered as the cross-check recommends (its §8), unless a decision above says
  otherwise.
- **The revisers' remaining questions** (2026-10-19). LM19: X5 drops the identity series, E9 drops the own-mean ratio,
  the model ratio has no symbol, X4's tooltips print five decimals. LM20: experiment 4's spread comes from 20
  replications drawn from one generator (§8's rule); the 樂詞網 forms now in SOURCES replace the placeholders (delta法,
  觀察訊息矩陣, 漸近常態性, 效率, 帕累托分布, 剖面概度). LM21: Problem 9 stays, with SciPy's Jarque–Bera formula and Jarque and
  Bera (1980) as the origin (bibliographic); the $\chi^2_1$ law of (21.5) for two series is *stated without proof*.
  LM22: X7 keeps its moving and circular rows as the one comparison of schemes; the widget design stands. LM23: X2's
  243 undated pairs of 2025 (sorted by the TAIEX return) are a scatter like LM16's, allowed; E6 prints the ratio 3.12
  and says "about 3 contracts". LM24: values printed beside their Monte Carlo error and theory value stand; LM20 lists
  LM24 among the users of (20.1), (20.5), (20.7). LM25: the ARMA standard errors as above; E10's sandwich sentence
  stays as one sentence with a pointer to LM26; the median volume follows the quantile rule (81,889); the simpler
  (25.6) with its check stands. SciPy's `bootstrap` and statsmodels' robust shape measures interpolate linearly:
  printed values use the book's quantile rule; KPSS's 10.356 prints as $p<0.01$.
- **LM26** (its drafter's questions, 2026-10-19). The derived file keeps its approved columns: the autocorrelation of
  intraday returns by year comes from the identity between adjacent intervals' realized variances, not from new
  columns. The forecast target is the opening return squared plus the 15-minute realized variance (the signature
  flattens near 15 minutes in most years; the ranking is the same at 5 and 30 minutes). Stale prices and price bounce
  are hypotheses, labelled so, until a source in SOURCES states either; the data show the ratio of 1-minute to 5-minute
  realized variance below 1 in 2005–2012 and 2020 and above 1 in the other years from 2013 (pooled lag-1
  autocorrelations of 1-minute returns are positive in 2006–2012 and negative from 2013; 2005's is negative too), and TX's 2025 signature is flat. The asymmetry after falls
  is named in words with Hansen and Lunde's (2005) "leverage effect"; HAR is named only once Corsi (2009) is in
  SOURCES; GARCH standard errors cite LM20's theory and arch's documented options. The weekly volatility paths and the
  model-only widget pass the no-full-series rule. The case's rolling fit and E4's full-sample fit are both kept,
  each labelled. The Chinese term is LM3's printed 實現變異數 (and 實現波動率), not the plan's earlier 已實現變異數.

## Stage 4 changes to earlier modules

Collected here as the briefs add them; applied at publication with the edition note.

- 波動度 → 波動率 in lm05.md:191, lm07.md:354, lm07.md:512, lm10.md:228, lm10.md:449.
- `build/make_lab17.py:486`: the autocorrelation convention is LM19's.
- `build/make_lab11.py:571`: the literal `[[LM20]]` goes (wording below).
- Leads of Volumes I–III gain the Volume IV modules that cite them (cross-check X25–X29, checked against the
  current front matter): lm01 20; lm02 20, 23; lm03 19, 25, 26; lm04 19, 21, 22, 24;
  lm05 19, 20, 21, 26; lm06 23; lm07 20; lm10 23, 24; lm11 20, 22, 24; lm12 20, 25; lm13 20, 22; lm14 21, 22, 24, 26;
  lm15 23, 24; lm16 25; lm17 23, 24, 25; lm18 21, 23, 25.
- `build/make_lab11.py:571`: "LM20 and LM22 give the tools; LM22 answers it for 2017 and 2020"; `make_lab15.py:443`
  and `make_lab17.py:486`: LM19's wording; `make_lab04.py:642`: LM22's wording (the briefs give each).
- lm15.md:263: LM20's rewording ("understate" claims a direction the data do not establish: the gap is 1.1 standard
  errors).

## LM19 Descriptive Statistics of Returns

Stage 1 brief, revised 2026-10-19 after the cross-check and the independent recomputation. Each number carries its
anchor ID at its first appearance; `data/vol4_anchors_lm19.py` prints them all, and its rows are in
`plans/vol-4-anchors.md`. Numbers quoted from published modules carry their file:line instead.

Revised to the editor's decisions (`plans/vol-4.md`, "Editor's decisions on the LM19–LM25 drafts"): LM19 owns TR23's
$\sqrt A\,s$ and Sharpe ratio on $R$ (X1); $\operatorname{VR}(m)$ is the overlapping estimator (19.8) only, and the
weighted sum of autocorrelations is an identity column (X9, X10); the median is $\operatorname{med}$ (X18); every
median and quantile, X7's included, is $\hat F^{-1}(u)$; the robust shape measures and the adjusted moments are
definitions, unattributed until the papers are read (X36); the Saturday sessions follow the "Calendar" decision
(TWSE's 2019 stop stated, their link to the 23 sessions written as an inference); tag users and leads as X1 and X27
give them, reconciled with the citing briefs after the fresh check; every printed value is rounded from its unrounded
value and flagged near a boundary.

**Prereq:** `[1, 3, 4, 5, 10, 14, 15, 16, 17, 18]`.

- LM1: (1.8) $r=\ln(1+R)$ (lm01.md:258); (1.9) $R_G=G^{1/\tau}-1$ (lm01.md:304); (1.12) $\ln G=\sum_t r_t$
  (lm01.md:404), the reason log returns add over days.
- LM3: (3.7) $\frac1T\sum R_t^2=s^2+\bar R^2$ (lm03.md:317); (3.9) volatility drag $R_G\approx\bar R-s^2/2$ (lm03.md:325);
  skewness named as "the asymmetry of moves around the mean" (lm03.md:330).
- LM4: 0050's excess kurtosis 8.12, the divisor-$T$ fourth moment over $s^4$, and its role in the Kelly overshoot
  (lm04.md:132).
- LM5: $\varphi$, $\Phi$ and (5.5); the sample excess kurtosis "uses $\hat\mu$ and $s$" (lm05.md:367); skewness "its
  standardized form" (lm05.md:745); the 7%→10% price limit of 1 June 2015 (lm05.md:364).
- LM10: (10.2) $\hat\Sigma$ with divisor $T$ (lm10.md:127); the pitfall on `np.cov` and $T-1$, "a small bias under
  assumptions that [[LM20]] states", factor 1.000114 at $T=4{,}382$ (lm10.md:166).
- LM14: $\hat F$ and the quantile function $\hat F^{-1}(u)=R_{(\lceil uT\rceil)}$ (lm14.md:96–97); the median as an
  interval (lm14.md:88); (14.3) linearity; (14.4); (14.5) Skew and Kurt; (14.12) $R_G\le\mu$; TR23's median 0.0879%
  (lm14.md:103), quartiles −0.490% and 0.681% (lm14.md:113, 115), skewness −0.338, kurtosis 8.27, excess 5.27
  (lm14.md:233, 246–248); the drag 0.7320 bp against $s^2/2=0.7301$ bp (lm14.md:34); $R_G=0.055185\%$ (lm14.md:39).
- LM15: (15.6) normal quantiles; (15.11) the scaled Student $t$ (Problem 10); the 23 calendar-year log returns, mean
  0.11646 and standard deviation 0.22207, divisor 23 (lm15.md:256); "Independent days scaled by $\sqrt m$ understate the
  annual spread" (lm15.md:263; Stage 4 rewords it with LM20's wording); $s$ and excess kurtosis by limit regime,
  1.257%/1.152% and 3.39/8.07 (lm15.md:410–411); the kurtosis jump 4.25 → 4.94 on 7 April 2025 (lm15.md:399), cited,
  not recomputed; falls outnumber rises beyond ±3%, 108 against 67 (lm15.md:447); the maximum-likelihood $\nu=3.065$
  (lm15.md:349).
- LM16: (16.1) independence; (16.2) covariance and correlation; (16.3) the sum rule; Problem 5's model factor 1.0797
  and 18.53% on U28's TAIEX price index (lm16.md:594, 623).
- LM17: (17.1); (17.5), for the band's normal approximation; (17.7) and its remark on the divisor (lm17.md:382–384); the
  2003–2025 refit, $\sqrt{246}\times1.18352\%=18.563\%$ against 22.207%, means 11.634% and 11.646% (lm17.md:347); the
  pair correlations 0.039, 0.161 and 0.123 (lm17.md:392); "whether daily variances add up over months" (lm17.md:80);
  the 73.0% rise of 2026's nine months (lm17.md:347).
- LM18: the 4,619 five-year windows of 1,231 sessions, spread of $\ln G$ 0.283 against 0.425, mean 0.502 against
  $m\bar r=0.679$ (lm18.md:373); "4.75 disjoint periods" (lm18.md:366); resampling destroys clustering (lm18.md:379); the
  standard deviation of Monte Carlo draws with divisor $n$ (lm18.md:47), for the standard error of a mean.

**Leads:** `[20, 21, 22, 23, 24, 25, 26, 32, 33]`. LM20: standard errors of every statistic here, the sampling error of
the 23 annual values, cites (19.1), (19.5), (19.7), (19.8); LM21: $s_{\mathrm u}$ in its t-stat and the number of looks
behind thirty autocorrelations, cites (19.1), (19.6); LM22: a block-bootstrap interval for $\operatorname{VR}(m)$, cites
(19.5), (19.7), (19.8); LM23: the overlap residuals' autocorrelations and the long-run variance behind HAC errors,
cites (19.5), (19.7); LM24: TR23's $A\bar R$, $\sqrt A\,s$ and Sharpe ratio from X8; LM25: weak stationarity, the
robust band, Ljung–Box and the variance-ratio test, cites (19.5), (19.6), (19.7), (19.8); LM26: models of the
clustering in X4 and the intraday variance ratios, cites (19.3), (19.5), (19.6), (19.7); LM32: drawdowns, a path
statistic (pointer in §3); LM33: the Sharpe ratio under correlated returns, cites (19.9).

**Forward links honoured.** The spine's list was complete: a grep of `src/lm*.md`, `src/pages/*.md` and
`build/make_lab*.py` for "LM19" finds exactly its 14 lines. Two related lines name another module and are kept
here too: `build/make_lab17.py:486` (the convention "stays LM26's"; Stage 4) and reviews/lm17.md:36.

| Earlier text | Promise | Kept in |
|:--|:--|:--|
| lm03.md:330 | skewness, "the asymmetry of moves around the mean ([[LM19]])" | §4: (19.3) as (14.5) under $\hat F$; quartile skewness (19.4); E6 |
| lm04.md:132 | 0050's excess kurtosis 8.12; "[[LM19]] develops this measure of tail weight" | §4: (19.3) is LM4's computation; adjusted 8.14 at $T=2{,}902$ (E5); octile kurtosis as a second measure; kurtosis weights the far tail, not the shoulders (X2 regimes) |
| lm05.md:367 | "the sample version uses $\hat\mu$ and $s$ ([[LM19]])" | §4: (19.3) with $\bar R$ (LM5's $\hat\mu$) and $s$, divisor $T$ |
| lm05.md:745 | skewness "(its standardized form, [[LM19]])" | §4: (19.3) |
| lm14.md:211 | "The choice of $T$ or $T-1$, and how far such numbers move between samples" (with LM20) | §3: (19.1), KC; §4: adjusted moments, E5 (23 values against 5,849); X2's regime and one-day columns, X7's grids (descriptive); [[LM20]] measures the sampling error |
| lm15.md:263 | "Independent days scaled by $\sqrt m$ understate the annual spread ([[LM19]])" (0.1856 against 0.22207) | case, §6–§7, E10: on 2003–2025 $\operatorname{VR}(246)=1.054$, so autocorrelation explains little; the 23-value spread runs from 11.9% to 25.0% with the cut. Stage 4 rewords the line (LM20's wording) |
| lm15.md:447 | TR23's skewness −0.34; "[[LM19]] studies it as a statistic" | §4: adjusted −0.3385; quartile skewness +0.013; one more −10% day moves it 26% (E6); regimes −0.2768 and −0.4163 (X2) |
| lm16.md:623 | factor 1.0797 and 18.53% (U28 price index, adjacent correlation 0.04 assumed); "[[LM19]] examines the data" | §6 E8: (19.7) gives 1.0797 as printed; on TR23 lag 1 alone gives 1.0784, all lags 1.280 (identity column), $\operatorname{VR}(246)=1.208$; the samples are named |
| lm17.md:80 | "Whether daily variances add up over months is a question about data, which [[LM19]] examines" | §6: X5 for $m=2,\dots,1{,}231$; X1's months 18.12% against days 18.56% |
| lm17.md:347 | 22.207% against 18.563%; "[[LM19]] examines the $\sqrt m$ scaling" | case; §7 E10 |
| lm17.md:384 | "Sample kurtosis and its divisor are [[LM19]]'s subject" | §4: (19.3) and its adjusted form |
| lm18.md:373 | windows' spread 0.283 against 0.425; "[[LM19]] asks whether the spread grows like $\sqrt m$" | §6 E9: $\operatorname{VR}(1{,}231)=0.619$ about $m\bar r$ against an iid expectation of 0.790 (LM18's 0.283 is about the windows' own mean); 4.75 disjoint periods; [[LM22]] for its error |
| `build/make_lab03.py:273` | "(LM19)" beside 0050's divisor-$T$ skewness and excess kurtosis | §4: (19.3) is that formula |
| `build/make_lab15.py:443` | "LM19 the sampling error of such statistics" | §6–§7: non-overlapping estimates vary with the starting day (X6, X7), descriptively; [[LM20]] measures; Stage 4 rewords the lab line |
| `build/make_lab17.py:486`; reviews/lm17.md:36 | the autocorrelation convention (0.1224 against 0.1228 at lag 20) | §5: (19.5), E7; Stage 4 changes the lab comment to LM19 |

**Outcomes** ("After this module you should be able to:"):

1. calculate the mean, median, trimmed mean, compound rate and mean log return of a return series, and explain why they differ
2. calculate the standard deviation with divisor $T$ and $T-1$, the mean absolute deviation, the interquartile range and the median absolute deviation, and convert the last two into normal-equivalent volatilities
3. compute sample skewness and excess kurtosis, their adjusted versions and quantile-based measures, and judge which of them hang on a few days
4. compute the sample autocorrelations of returns, absolute returns and squared returns under the book's convention, and read them against the iid band
5. derive the variance of an $m$-day sum from autocorrelations, estimate the variance ratio from overlapping and non-overlapping sums, and state the overlapping estimator's bias
6. apply the annualization rules for the mean, variance, volatility and Sharpe ratio, state the condition each needs, and explain why TAIEX's annual volatility depends on how it is measured
7. build weekly, monthly and yearly returns from daily data, and compute every statistic of the module in Python with explicit divisors and quantile rules

**Owns.** Measures of location: mean, median $\operatorname{med}$, the 5% trimmed mean; $\bar R$ against $\bar r$ against
$R_G$ (citing LM3 and LM14). Dispersion: $s$ (divisor $T$), $s_{\mathrm u}$ (19.1) introduced in one paragraph with
LM20's pointer, the mean absolute deviation, the interquartile range, the median absolute deviation (MAD) and the
normal-equivalent scales $1.4826\,\mathrm{MAD}$ and $\mathrm{IQR}/1.349$ (19.2), derived. Shape: (19.3) sample skewness
and excess kurtosis with divisor-$T$ moments and their adjusted versions; (19.4) quartile skewness and octile kurtosis;
the effect of one more day. The sample autocorrelation (19.5), its convention, and the iid band (19.6); TR23's
$\hat\rho_k$ for $r$, $\lvert r\rvert$ and $r^2$, $k\le30$. The variance of an $m$-day sum and the model's ratio (19.7);
the book's one variance ratio $\operatorname{VR}(m)$, the overlapping estimator, with its iid expectation, and the
non-overlapping $\operatorname{VR}_{\mathrm n}(m)$ (19.8); TR23's $\operatorname{VR}(m)$ for $m=2,\dots,1{,}231$.
Annualization of the mean, variance, volatility and Sharpe ratio, with the Sharpe ratio of $m$-day sums (19.9). TR23's
annual mean $A\bar R=15.38\%$, annual volatility $\sqrt A\,s=18.96\%$ and Sharpe ratio $0.0517$ a day, $0.81$ a year,
all on $R$ with $r_f=0$ (13.58%, 18.99%, 0.0456 and 0.715 on $r$) [A19-54]: [[LM20]]–[[LM24]] cite them, and
[[LM20]] gives their standard errors. Weekly, monthly and yearly log returns from
daily data; the three annual volatilities on 2003–2025 and the 246 grids of one-year blocks.

**Leaves.**

- Standard errors and intervals of every statistic here; the sampling error of 23 annual values; why $s_{\mathrm u}^2$ is
  unbiased → LM20.
- The number of looks and their correction → LM21 (cited in the §5 pitfall).
- A block-bootstrap interval for $\operatorname{VR}(m)$; the error of LM18's windows → LM22.
- The long-run variance and HAC errors → LM23 (one sentence in §6).
- Weak stationarity defined and tested, the robust autocorrelation band and its robust standard error, Ljung–Box, the
  variance-ratio test on (19.8) → LM25.
- Models of volatility clustering → LM26.
- Drawdown statistics → LM32. Sharpe ratio statistics under correlated returns, PSR, DSR → LM33.
- The kurtosis's fragility around 7 April 2025 (the removals, the top-ten shares) → stays LM15's, cited.

**Uses before taught** (one sentence each in the text):

- §3: "[[LM20]] shows that $s_{\mathrm u}^2$ is an unbiased estimator of $\sigma^2$ for iid draws, which is why software
  defaults to it."
- §3: "A drawdown depends on the order of the days, so it is a path statistic; [[LM32]] studies it."
- §4: "How far a sample skewness moves between samples is measured by its standard error ([[LM20]])."
- §5: "A series is weakly stationary when its mean, its variance and each lag covariance stay the same at every date;
  [[LM25]] defines this and tests for it."
- §5: "That $\hat\rho_k$ is approximately normal for large $T$ is *stated without proof* (a central limit theorem for
  dependent terms, beyond [[LM17]]'s (17.5)); [[LM25]] widens the band for clustering." Its reference waits for the
  open point below ("Open before Stage 2", 1).
- §5 pitfall: "Thirty looks at one band find about 1.5 bars outside by chance alone; [[LM21]] counts such looks."
- §6: "As $m$ grows, $\gamma_0$ times the model's ratio tends to the long-run variance that [[LM23]]'s HAC errors
  estimate"; "[[LM25]] turns $\operatorname{VR}(m)$ into a test, and [[LM22]] puts an interval around it."
- §7: "[[LM33]] gives the Sharpe ratio's standard error when returns are correlated."

**Data role.** TR23 only, from `data/processed/vol3_taiex.parquet` (`data/vol3_series.py`; FinMind
`TaiwanStockTotalReturnIndex`, data_id TAIEX, retrieved 2026-10-18): 5,850 closes [A19-01], 2003-01-02 → 2026-10-08;
$T=5{,}849$ simple returns [A19-02] from 2003-01-03; 8,680 calendar days $=23.7645$ years [A19-03]; $A=246.12$
[A19-04]. All 5,849 returns are distinct and none is exactly zero [A19-05] (`Fraction` on the closes), so order
statistics, quartiles and MAD have no ties (half the days, 2,925, lie within MAD of the median, checked exactly
[A19-26]). TR23 holds 23 Saturday sessions, 14 October 2006 to 22 December 2018 [A19-69]; they stay in every sample
and group (`plans/vol-4.md`, "Calendar"). X1's note names them and says that TWSE's history page states that the
market stopped trading on Saturday make-up workdays from 2019 (SOURCES, "Taiwan facts (Volume IV)"); that the 23
sessions were such days is an inference, written as one. Two named sub-samples, never mixed within a statistic:

- **2003–2025**: the 5,664 log returns [A19-06] dated 2003-01-03 → 2025-12-31, the calendar years of LM15 and LM17
  (2003 from its first close; 239–251 sessions a year, mean 246.26 [A19-06]). A year is 246 sessions, LM17's $m$; it
  holds 1,185 ISO weeks of 1–6 sessions (51.52 a year) and 276 months [A19-08]. The case, X1, E10, X7 and the widget's
  initial state use it. 185 returns are dated 2026 [A19-06].
- **Limit regimes**: 3,077 returns before 2015-06-01 and 2,772 from it [A19-07] (stability check).
- No U28, no TX23, no 0050 recomputation: LM16's 1.0797 (U28 price index) and LM4's 8.12 (0050) are quoted as printed
  and named as other samples.

Return type: one-day statistics on $R$ (§2–§4); sums, autocorrelations and variance ratios on $r$, $\lvert r\rvert$ and
$r^2$ (§5–§7), labelled "log returns" in every caption; X8 gives $R$ first and $r$ in brackets. Cleaning: none beyond
`vol3_series.py`'s checks. Seeds: one simulated experiment, $e=1$ (§6 Deep Dive, lab part 6): `rng =
np.random.default_rng([1, 20261011])`, created once, 10,000 samples of 5,849 iid standard normal log returns; each
mean carries its standard error (divisor $n$, as LM18). Published files carry statistics, never the daily series
(`plans/vol-4.md`, X37): X3 is thinned to weekly points, the widget embeds variance ratios. Scripts:
`data/lm19_numbers.py` (every printed value, asserted against the anchors; `Fraction` checks; the rounding-boundary
flags), `data/lm19_charts.py` (X1, X3, X4, X5, X7 and the widget block), both in `build.sh` `DATA_STEPS` after
`data/vol3_series.py` and listed in `data/README.md`; lab file `taiex_tr.csv`, built locally (`data/make_lab_data.py`
gains `"LM19_lab": {**tr23}`).

**Hygiene declaration.** *Descriptive*: every TR23 statistic, X1, X3–X7, the grids. *In-sample*: X2's normal law with
TR23's own $\bar R$ and $s$ (as [[LM14]] labels its normal comparison). *Model*: (19.2), the iid band (19.6), the iid
expectation (19.8) and its simulation ($e=1$). *Hypothetical*: the appended −10% day (E6, X2). *Stability check*: the
two limit regimes (X2, §5, the lab extension); 2003–2025 against the full sample (§7). Nothing is tested. Local
note: "Every TAIEX figure describes the total-return index's daily returns, 3 January 2003 to 8 October 2026 (5,849
returns), unless a caption names 2003–2025 (5,664 log returns, the calendar years of [[LM15]] and [[LM17]]) or a limit
regime. These numbers are **descriptive**: none carries a standard error, because measuring sampling error is
[[LM20]]'s subject. The normal law with the sample's own mean and standard deviation is **in-sample**; the iid band and
the iid expectation are **model** properties; the extra −10% day is **hypothetical**; the two limit regimes, and
2003–2025 against the whole sample, are **stability checks**. Nothing here is tested ([[LM21]], [[LM25]])."

**Notation.** AUTHORING §6 with its Volume IV table. Used: $R$, $r$, $\bar R$, $\bar r$, $s$, $s_r$ (divisor $T$),
$s_{\mathrm u}$, $R_G$, $G$, $\mu$, $\sigma$, $\sigma_r$, $g$, $A$, $T$, $t$, $m$ (days in a sum), $\mathrm{SR}$,
$\varphi$, $\Phi$, $\Phi^{-1}$, $\Pr$, $\E$, $\Var$, $\Cov$, $\operatorname{Skew}$, $\operatorname{Kurt}$, $Z$, $\hat F$,
$\hat F^{-1}$, $R_{(j)}$, $u$, $\mathcal N$, $t_\nu$, $\nu$ (Problem 10), iid, $\rho_k$, $\hat\rho_k$, $\gamma_k$,
$\hat\gamma_k$, $k$ (a lag), $\operatorname{med}$ (the sample median, §6's row from LM19), $\operatorname{VR}(m)$ (§6's
row: the overlapping estimator, (19.8)). The model's ratio in (19.7), $\Var r_t^{(m)}/(m\gamma_0)$, gets no symbol, so
that $\operatorname{VR}(m)$ keeps one meaning. Counts: $j$ (a rank), $j_0$, $k$, $m$, $o$. Local:

| Symbol | Meaning | Check |
|:--|:--|:--|
| $j_0$ | trimmed count, $\lfloor0.05T\rfloor=292$ | $j$ stays a rank |
| $\operatorname{IQR}$, $\operatorname{MAD}$ | $\hat F^{-1}(0.75)-\hat F^{-1}(0.25)$; the median of $\lvert R_t-\operatorname{med}\rvert$ | upright names, like $\operatorname{med}$ |
| $\widehat{\operatorname{Skew}}$, $\widehat{\operatorname{Kurt}}$; subscript adj | (14.5) under $\hat F$ (divisor $T$); the adjusted versions | hats mark statistics (Volume IV) |
| $\operatorname{Skew}_{\mathrm Q}$, $\operatorname{Kurt}_{\mathrm O}$ | quartile skewness; octile kurtosis (19.4) | new; printed as definitions, attributed only after the papers are read |
| $x_t$, $\bar x$ | a series ($r_t$, $\lvert r_t\rvert$ or $r_t^2$) and its sample mean, §5–§6 | lower case, a value |
| $r_t^{(m)}$ | $r_{t-m+1}+\dots+r_t$, the $m$-day log return ending on day $t$ | superscript in parentheses; $r(t)$ stays a rate |
| $\operatorname{VR}_{\mathrm n}(m)$; $o$ | the non-overlapping estimator (19.8); the number of returns skipped before its first block, $0\le o<m$ | subscripted; $o$ a count |
| $\mathrm{SR}(m)$ | Sharpe ratio of $m$-day log-return sums, $r_f=0$ | follows $\mathrm{SR}$ |

Not used: a tilde for the median (a tilde means centred, §6), $\hat\mu$ for TR23's mean (LM5's $\hat\mu$ is named as
$\bar R$ once), $\theta$, $\alpha$ (the 5% level is written so), $\beta$, $H_0$, t-stat, $Q$ (book-wide eigenvectors:
quartiles are $\hat F^{-1}(\cdot)$), $q$, $p$, $c$, $f$, $\hat f$, $W$, $L$, $B$, $\ell$, $G_1$/$G_2$ and $g_1$/$g_2$
(they clash with $G$ and $g$), $m_j$ for moments (LM4's raw moments), $N$, $X$.

**Motivating case: "How volatile is a year of TAIEX?"** (box, about 130 words)

> Take the TAIEX total-return index, with dividends reinvested and no costs, from 3 January 2003 to 31 December 2025:
> 5,664 daily log returns [A19-06]. Their standard deviation is 1.18352% a day [A19-09]. A year has about 246
> sessions, so independent days would give a yearly standard deviation of $\sqrt{246}\times1.18352\%=18.56\%$
> ([[LM17]]). Weekly and monthly log returns, scaled to a year the same way, give 18.09% and 18.12% [A19-10, A19-11].
> Yet the 23 calendar-year log returns have a standard deviation of 22.21% ([[LM15]]) [A19-12]. To reach it, the
> variance of a year's sum would have to be 1.43 times the sum of its daily variances [A19-13]. Do daily variances
> fail to add up over a year? Or do 23 numbers pin down a standard deviation too loosely to tell?

Resolved: (a) whether variances add up: §6, (19.7), X5 ($\operatorname{VR}(246)=1.0536$ on 2003–2025 [A19-53], so
19.05% [A19-55]; 19.48% after the bias of (19.8)); (b) how loosely 23 values pin a standard deviation down: §7, E10, X7
(the same 23 years cut into one-year blocks from other days give 11.89% to 25.04% [A19-56]); (c) the size of that
sampling error: [[LM20]]. A one-year figure is not one day, so AUTHORING §8's one-day rule does not arise; the tariff
week of E1 is the sample's most volatile week and says so.

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | one framing paragraph; case + X1; roadmap; notation and hygiene notes | 380 |
| 2 | Where Returns Centre {1} | E1 (the tariff week by hand); mean, median $\operatorname{med}$ ([[LM14]]), trimmed mean with $j_0$; "robust" defined (a statistic a few observations cannot move far); $R_G$ and $\bar r$ by (1.9), (1.12), $R_G=e^{\bar r}-1$ per day, $\bar R\ge R_G$ by (14.12), (3.9) with LM14's 0.7320 against 0.7301 bp; E2; pitfall; KC | 520 |
| 3 | How Far Returns Spread {2} | $s$; (19.1) $s_{\mathrm u}$ in one paragraph (lm10.md:166, [[LM20]]); mean absolute deviation, IQR, MAD; (19.2) derived for a normal law; E3; E4; X3; [[LM32]] pointer; pitfall; 中文導讀; KC | 600 |
| 4 | Skewness and Kurtosis as Statistics {3} | (19.3) and the adjusted versions; LM4's and LM5's promises; E5; (19.4) quartile skewness, octile kurtosis; X2; E6; the regime columns; LM15's 7 April jump cited; pitfall; 中文導讀; KC | 620 |
| 5 | Autocorrelation {4} | E7 (by hand, two conventions); (19.5); LM17's pair correlations against $\hat\rho_k$; (19.6) and Deep Dive; X4: $r$, $\lvert r\rvert$, $r^2$; the regimes as a stability check ($\hat\rho_1$ of $r$ 0.055 before June 2015, 0.018 after; of $\lvert r\rvert$ 0.113 and 0.217 [A19-42]); pitfall; 中文導讀; KC | 620 |
| 6 | How Daily Variances Add Up {5} | two days first (the model's ratio $1+\rho_1$); (19.7) from (16.3); E8; (19.8): $\operatorname{VR}(m)$ and $\operatorname{VR}_{\mathrm n}(m)$; Deep Dive (the iid expectation, $e=1$); the overlap's own dependence; X5, X6 (with the identity column); E9; [[LM23]], [[LM25]], [[LM22]] pointers; pitfall; KC | 750 |
| 7 | Annualizing, and the Annual Volatility {6, 7} | the four rules and their conditions; (19.9), Lo (2002); periods from daily data; X8 ($R$ first); E10 with X7; 2026's 185 sessions as a stability check; widget; pitfall; 中文導讀; KC | 650 |
| 8 | Descriptive Statistics in Python {7} | code: divisors, quantile rule, trimmed mean, MAD, `stats.skew`/`kurtosis` flags, $\hat\rho_k$ two ways, overlapping sums, Polars periods; lab box; KC | 220 |
| — | Summary (7) / Problems (12) / Solutions | | 140 / 420 / 520 |
| | **Total** | | **5,440** |

**Elements.** 10 examples (E1, E2 §2; E3, E4 §3; E5, E6 §4; E7 §5; E8, E9 §6; E10 §7). Knowledge checks:

- §2: replace −9.70% by −19.70% in the tariff week: the mean falls to −3.493%; the median (−4.016%) and the 20%
  trimmed mean (−2.339%) do not move [A19-17].
- §3: by what factor does $s_{\mathrm u}$ exceed $s$ for the five days of E1 and for TR23? $\sqrt{5/4}=1.118$ and
  $1.0000855$ [A19-19, A19-20].
- §4: why do the quartile skewness (+0.013) and the moment skewness (−0.338) differ in sign, and why does the octile
  kurtosis fall from 1.534 to 1.420 between the regimes while the excess kurtosis rises from 3.39 to 8.07 ([[LM15]])?
  [A19-30, A19-32, A19-33]
- §5: $\hat\rho_1$ of the six values 1, −1, 1, −1, 1, −1 is $-5/6$, not −1 [A19-35]: the divisor $T$ shrinks it by
  $(T-k)/T$.
- §6: with $\rho_1=0.04$ and $\rho_2=0$, (19.7) makes the variance of a 3-day sum $1+2\cdot\tfrac23\cdot0.04=1.0533$
  times $3\gamma_0$ [A19-59].
- §7: TR23's log-return Sharpe ratio is 0.0456 a day; $\times\sqrt{246.12}$ gives 0.715 a year for uncorrelated days,
  and dividing by $\sqrt{\operatorname{VR}(246)}=\sqrt{1.208}$ gives 0.650 [A19-54]. (On $R$, X8's 0.81 is the
  volume's figure.)
- §8: Polars' `std()` on the 23 calendar-year log returns prints 22.706%, not 22.207%: its default divides by 22
  [A19-61].

中文導讀 (樂詞網, English in parentheses at first use in each box; SOURCES "Chinese terms (Volume IV)", including the
terms this brief looked up, now recorded there):

- §3 "一般的一天與平均的一天": 敘述統計 (descriptive statistics), 中位數 (median), 截尾平均數 (trimmed mean),
  四分位距 (interquartile range), 中位數絕對離差 (median absolute deviation), 平均絕對偏差 (mean absolute deviation;
  數學名詞 only), 穩健統計 (robust statistics), 樣本變異數 (sample variance), 不偏估計量 (unbiased estimator), 波動率
  (volatility).
- §4: 偏態 (skewness), 峰態 (kurtosis), 超額峰態 (excess kurtosis, Volume III's printed form), 四分位數 (quartile),
  八分位數 (octile).
- §5: 自我相關 (autocorrelation), 自我相關函數 (autocorrelation function), 時間序列 (time series), 獨立同分布 (iid),
  波動群聚現象 (volatility clustering).
- §7: 變異數比 (variance ratio), 平穩 (stationary), 波動率, 標準誤 (standard error, pointing to LM20).

Sample autocorrelation, sample skewness and sample kurtosis have no 樂詞網 entry: the boxes write 樣本 plus the listed
term, as LM15 printed 樣本峰態.

Deep Dives: §5 "Why the iid band is ±1.96/√T": for iid $x_t$ with variance $\gamma_0$, replace $\bar x$ by $\E x_t$
(an error of order $1/T$); the products $(x_t-\E x_t)(x_{t-k}-\E x_t)$, $t=k+1,\dots,T$, have mean 0 and are
uncorrelated with variance $\gamma_0^2$ by (16.1), so by (16.3) $\Var(T\hat\gamma_k)\approx(T-k)\gamma_0^2$ and
$\Var\hat\rho_k\approx(T-k)/T^2\approx1/T$; approximate normality is *stated without proof*. When squares correlate,
$\E[(x_t-\E x_t)^2(x_{t-k}-\E x_t)^2]>\gamma_0^2$ and the band is too narrow ([[LM25]]). §6 "The overlapping estimator
under iid days": $\E[(r_t^{(m)}-m\bar r)^2]=m\sigma_r^2-2m\cdot m\sigma_r^2/T+m^2\sigma_r^2/T=m\sigma_r^2(1-m/T)$ by
(16.3) and (17.1), and $\E s_r^2=\sigma_r^2(1-1/T)$; the ratio of these expectations is (19.8)'s factor, an
approximation to the expectation of the ratio. Experiment $e=1$: 10,000 samples of 5,849 iid normal days
(`default_rng([1, 20261011])`) give mean values of $\operatorname{VR}(m)$ of $0.960\pm0.002$ at $m=246$ and
$0.791\pm0.005$ at $m=1{,}231$ (standard errors of a mean, divisor $n$), against 0.958 and 0.790 [A19-47, A19-48].

**Exhibits.**

- X1 `case` (`bar`, §1): categories "Days × √246", "Weeks × √51.52", "Months × √12", "Calendar years"; one series
  "TAIEX log returns, 2003–2025" (`fmt: "pct2"`, `valueLabels`), values 18.56%, 18.09%, 18.12%, 22.21% [A19-09–A19-12];
  y 0–25% (`tfmt: "pct0"`). Note: standard deviations of 5,664 daily, 1,185 weekly (ISO weeks, 1–6 sessions), 276
  monthly and 23 calendar-year log-return sums (2003 from its first close), each with divisor = the number of periods
  ([[LM15]]'s convention for the years); a year is 246 sessions ([[LM17]]), 1,185 ÷ 23 = 51.52 weeks or 12 months. The
  sample keeps its 23 Saturday sessions (2006–2018); each of the 17 six-session weeks holds one [A19-69]. TWSE's
  history page states that the market stopped trading on Saturday make-up workdays from 2019; that these 23 sessions
  were such days is an inference. Source:
  FinMind `TaiwanStockTotalReturnIndex` (data_id TAIEX), retrieved 18 October 2026; dividends reinvested, no costs.
  Computations: `data/lm19_numbers.py`. Shows: three ways of scaling short returns agree; the years do not.
- X2 `summary` (table, §2–§4; cited first in §2): rows mean; median; 5% trimmed mean; $s$; $s_{\mathrm u}$; mean
  absolute deviation; $1.4826\,\mathrm{MAD}$; $\mathrm{IQR}/1.349$; skewness; adjusted; quartile skewness; excess
  kurtosis; adjusted; octile kurtosis. Columns: TR23 (5,849); 7% limit (3,077); 10% limit (2,772); normal law with
  TR23's $\bar R$ and $s$; TR23 plus one −10% day (5,850). Location in % to four decimals, scale in % to three,
  skewness to four, the rest to three: TR23 0.0625, 0.0879, 0.0832; 1.208, 1.208, 0.836, 0.873, 0.868; −0.3384,
  −0.3385, 0.013; 5.268, 5.274, 1.471 [A19-18, A19-20, A19-21, A19-23, A19-27, A19-30]; 7% and 10% columns
  [A19-32, A19-33]; normal: 0.0625 for the three centres, $\sigma=1.208$, "—" for $s_{\mathrm u}$ and the two adjusted
  rows (sample statistics), 0.964, 1.208, 1.208, 0, 0, 0, 1.233 [A19-34]; plus one day [A19-31]. Note: daily
  simple returns; the two robust scales use the exact constants $1/\Phi^{-1}(0.75)$ and $2\Phi^{-1}(0.75)$, shown
  rounded in the labels; the regime columns are a stability check, each part on its own ($s$ and excess kurtosis also
  in [[LM15]]); the last column is hypothetical; no standard errors ([[LM20]]); 0.0879, −0.490/0.681 and 5.27 are
  [[LM14]]'s. Source and Computations as X1.
- X3 `rollscale` (`line`, §3): x date (window end, 2003-12-29 → 2026-10-08, `x.values` shared); y 0–40% (`pct0`, tooltip
  `pct1`). Series over the 5,604 windows of 246 returns: "standard deviation" (1), "1.4826 × MAD" (2), "IQR / 1.349"
  (3), each × $\sqrt A$; thinned to weekly points (every fifth window end) plus each series' maxima, minima and last
  value, as the no-full-series rule asks. Points: 35.2% (15 June 2009), 31.0% (15 December 2008), 8.2% (10 November
  2017), 7.6% (29 November 2017) [A19-25]. Note: simple returns; window medians and quartiles by the book's rule
  ($R_{(123)}$, $R_{(62)}$, $R_{(185)}$ of each window); the ratio of the first two series runs from 1.01 (window
  ending 17 October 2008) to 1.72 (30 March 2020) [A19-25], so a robust scale and $s$ differ most when a few days
  dominate a calm year. About 45 KB.
- X4 `acf` (`bar`, §5): categories 1–30 ("lag k, sessions"); series "r (log return)" (1) and "|r|" (2); `hline`s at
  ±0.02563 labelled "iid band ±1.96/√T" (bar `hline`s are dashed) [A19-37]; y −0.05 to 0.25 (`fmt: "n5"`, so that lag
  29 and the band differ in the tooltip; `tfmt: "n2"`). Note: TR23, 5,849 log returns, (19.5). $r$: $\hat\rho_1=0.0393$;
  9 of 30 lags outside the band (1, 4, 6, 8, 13, 14, 18, 20, 26), and lag 29 (−0.02561) lies just inside it [A19-38].
  $\lvert r\rvert$: 0.096 (lag 19) to 0.217 (lag 3), all 30 outside [A19-39]. $r^2$ (not drawn): 0.194, 0.213 and
  0.271 at lags 1–3, all 30 outside; 31.5% of the lag-3 value comes from one pair of days, 7 and 10 April 2025, against
  7.7% of $\lvert r\rvert$'s [A19-40]. The band assumes iid days; clustering widens it ([[LM25]]). Thirty looks find
  about 1.5 bars outside by chance ([[LM21]]).
- X5 `vr` (`line`, §6): `x.type: "log"`, $m=2,\dots,1{,}231$ in `x.values`; `ticks` 2, 5, 10, 20, 50, 100, 246, 500,
  1,231 with `tickLabels`; y 0.4–1.4 (`n2`, tooltip `n4`). Series: "TR23" (1); "2003–2025" (2); "iid expectation,
  T = 5,849" (3, `dash`). `hline` 1; dashed `vline`s at 246 and 1,231; points 1.208 and 0.619 (TR23), 1.054
  (2003–2025) [A19-46, A19-50, A19-53]. Note: log returns; $\operatorname{VR}(m)$ of (19.8), overlapping sums centred at
  $m\bar r$; TR23 peaks at 1.267 ($m=127$), first falls below 1 at $m=340$, reads 0.783 at 492 and bottoms at 0.508
  ($m=980$); 2003–2025 reads 0.692 at 492 and 0.468 at 1,231 [A19-52]; the dashed curve is what iid days would give on
  average. About 40 KB.
- X6 `vrtable` (table, §6): rows $m$ = 2, 5, 20, 60, 246, 1,231. Columns: windows $T-m+1$; $T/m$;
  $\operatorname{VR}(m)$; identity column, (19.7) with $\hat\rho_k$; $\operatorname{VR}_{\mathrm n}(m)$ from the first
  return; $\operatorname{VR}_{\mathrm n}(m)$, lowest–highest over the $m$ possible first blocks; iid factor. Values to
  three decimals, rounded from the unrounded values [A19-49] (so $m=5$'s 1.0465043 prints 1.047 and $m=246$'s
  1.1404908 prints 1.140). Note: TR23 log returns; non-overlapping blocks centred at $m\bar r$ of the whole sample; the
  identity column shows (19.7) on sample autocorrelations, which $\operatorname{VR}(m)$ does not equal exactly; the iid
  factor is (19.8)'s.
- X7 `grids` (`line`, §7): x first return of the grid, 0–245 sessions after 3 January 2003 (`n0`); y 10–26% (`pct0`,
  tooltip `pct2`). One series, "standard deviation of one-year sums" (246 points). Dashed `hline`s: 22.21% "calendar
  years", 19.05% "overlapping one-year sums", 18.56% "days × √246" [A19-55]. Points: 11.89% (171), 25.04% (212),
  20.18% (0) [A19-56]. Note: 2003–2025 log returns cut into consecutive 246-day blocks after skipping 0–245 returns
  (23 blocks for 0–6 skipped, 22 after); a year is 246 sessions ([[LM17]]); standard deviation about the blocks' mean,
  divisor the number of blocks; median 19.13% ($\hat F^{-1}(\tfrac12)$, the 123rd of the 246 sorted values); 46 of 246
  grids (18.7%) at or above the calendar years' 22.207% and 113 (45.9%) at or below 18.563% [A19-56]. The spread is
  descriptive, not an interval ([[LM20]]).
- X8 `rules` (table, §7): rows mean simple return, mean log return, variance, volatility, Sharpe ratio. Columns: per day
  (TR23) | annualize by | annual | exact when | wrong when. Values on $R$ first, $r$ in brackets: 0.0625%, $\times A$,
  15.38% (approximate: the 23 calendar years averaged 14.97%, lm14.md:39); 0.05517%, $\times A$, 13.58% (exact for
  sums, (1.12), (14.3)); $s^2$, $\times A$, 0.0359 ($r$: 0.0361); 1.2084%, $\times\sqrt A$, 18.96% ($r$: 1.2107%,
  18.99%); 0.0517, $\times\sqrt A$, 0.81 ($r$: 0.0456, 0.715, and 0.650 after $\div\sqrt{\operatorname{VR}(246)}$, by
  (19.9), which holds for log sums) [A19-20, A19-54]. Note: $A=246.12$; $r_f=0$; the conditions are (19.7) and (19.9);
  18.96% and 0.81 are the volume's figures ([[LM20]]–[[LM24]] cite them).

Exhibit JSON stays far under 300 KB (X3 about 45 KB, X5 about 40 KB, the widget block about 25 KB).

**Widget `aggregate` — "How daily variances add up."** `Book.controls`: sample (select: "TAIEX, 2003–2025" initial,
"TAIEX, 2003 – Oct 2026"); $m$ sessions (1–1,231, step 1, initial 246). `line` chart, `x.type: "log"`, $m$ from 1 to
1,231; y annualized volatility (`pct1`): "overlapping m-day sums" $\sqrt{A\operatorname{VR}(m)}\,s_r$ (1); "independent
days" $\sqrt A\,s_r$ (2, dashed); "iid expectation" $\sqrt{A\,(1-m/T)/(1-1/T)}\,s_r$ (3, dashed); for 2003–2025 a
dashed `hline` at 22.21% "calendar years"; a `vline` at $m$. Readouts: $m$ and $m/A$ years; windows $T-m+1$; $T/m$
disjoint periods; $\operatorname{VR}(m)$; the iid factor; their ratio; the two annual volatilities. $A=246$ on
2003–2025 (LM17's year) and 246.12 on TR23. Nothing is simulated (no `Book.rng`, no `Book.dist`). Data block
`chart-lm19-aggregate`: per sample $T$, $A$, $s_r$ and $\operatorname{VR}(m)$ for $m=1,\dots,1{,}231$ (statistics, not
the series; about 25 KB). Initial state (PDF): 2003–2025, $m=246$: 1.0536, 19.05% against 18.56%, 5,419 windows, 23.0
periods, factor 0.957 [A19-58].

**Examples** (results recomputed from the printed inputs):

- E1 §2 `week` "The tariff week": TR23's returns on 7–11 April 2025 are −9.6997%, −4.0161%, −5.7865%, +9.2512%,
  +2.7842%, the most volatile of its 1,224 ISO weeks ($s=6.72\%$) [A19-14]. Mean −1.493%, median −4.016%, 20% trimmed
  mean −2.339% [A19-15]; growth factor 0.9170 (−8.30%), $R_G=-1.719\%$, $\bar r=-1.734\%$ [A19-16]. Every centre is a
  different question.
- E2 §2 `centres` "Five centres of TAIEX's day": $\bar R=0.0625\%$, $\operatorname{med}=0.0879\%$ ([[LM14]]), 5% trimmed
  mean 0.0832% (292 days dropped at each end), $R_G=0.05518\%$ ([[LM14]]'s 0.055185%), $\bar r=0.05517\%$ [A19-18]. The
  median and the trimmed mean sit above the mean because the largest days are falls (§4); $R_G$ sits below it by the
  drag, 0.7320 bp against $s^2/2=0.7301$ bp (lm14.md:34).
- E3 §3 `weekscale` "The tariff week's spread": $s=6.721\%$, $s_{\mathrm u}=7.515\%$ (×1.118), mean absolute deviation
  6.009%, MAD 5.684% [A19-19]. With five days the divisor matters.
- E4 §3 `robustscale` "A typical day against the standard deviation": TR23's $s=1.2084\%$, $s_{\mathrm u}=1.2085\%$
  [A19-20]; mean absolute deviation 0.836%, 0.692 of $s$ against the normal's 0.798 [A19-21]; $\mathrm{IQR}=1.172\%$,
  MAD 0.589%; normal-equivalent 0.868% and 0.873% [A19-22, A19-23]. Annualized: 18.96% from $s$ against 13.7% and
  13.6% from the robust scales [A19-24]: the typical day of TAIEX moves like a 13.7% volatility, and the large days add
  the rest.
- E5 §4 `divisor` "When the divisor matters": the 23 calendar-year log returns have skewness −0.99 and excess kurtosis
  2.31 with divisor-$T$ moments, −1.06 and 3.22 adjusted [A19-28]; TR23's daily values move only in the fourth digit,
  −0.3384 to −0.3385 and 5.268 to 5.274 [A19-27]. LM4's 8.12 becomes 8.14 at 2,902 days [A19-29].
- E6 §4 `oneday` "One more limit-down day": append a hypothetical −10% day to TR23. The mean falls 2.8%, the median and
  trimmed mean 0.4%, $s$ rises 0.6%, the robust scales move under 0.1%; the skewness goes from −0.338 to −0.425
  (−26%) and the excess kurtosis from 5.27 to 5.88 (+12%), while the quartile skewness moves 1.2% and the octile
  kurtosis 0.05% [A19-31]. A hypothetical; 7 April 2025's real effect is [[LM15]]'s (4.25 → 4.94, lm15.md:399).
- E7 §5 `twoways` "Two ways to correlate a series with its past": for E1's week, (19.5) gives $\hat\rho_1=0.139$ and
  the correlation of its four pairs $(R_t,R_{t+1})$ gives 0.237 [A19-36]. For TR23's log returns they agree:
  0.0393 against 0.0394, and for $\lvert r\rvert$ at lag 20, 0.1224 against 0.1228 ([[LM17]]'s 0.123, lm17.md:392)
  [A19-38, A19-39]. The convention is statsmodels' `acf`, whose values agree with (19.5) to within $10^{-15}$ [A19-43].
- E8 §6 `sumvar` "Two days, and LM16's year": by (19.7) the model's ratio at $m=2$ is $1+\rho_1$; TR23 gives
  $1+\hat\rho_1=1.0393$ and $\operatorname{VR}(2)=1.0392$ [A19-44]. [[LM16]]'s model year (U28's price index, adjacent
  correlation 0.04 assumed) gets 1.0797 from (19.7) as printed (lm16.md:623) [A19-45]; on TR23, lag 1 alone gives
  1.0784, all 245 lags give 1.280 (X6's identity column), and $\operatorname{VR}(246)=1.208$ [A19-45, A19-46].
- E9 §6 `windows` "LM18's five-year windows": the 4,619 windows of 1,231 sessions have a spread of $\ln G$ of 0.283
  about their own mean 0.502, against $\sqrt m\,s_r=0.425$ ([[LM18]]). (19.8) centres the sums at $m\bar r=0.679$
  instead and gives $\operatorname{VR}(1{,}231)=0.619$ [A19-50]. Under iid days it would average 0.790 [A19-47], far
  below 1, because the windows hold only 4.75 disjoint periods [A19-51]. The ratio of the two, about 0.78, says the
  spread grows more slowly than $\sqrt m$ on TR23, but it rests on under five periods; [[LM22]] puts an interval on it.
- E10 §7 `annualvol` "TAIEX's annual volatility, resolved": on 2003–2025, $\sqrt{246}\,s_r=18.563\%$; the overlapping
  one-year sums give $\sqrt{1.0536}\times18.563\%=19.05\%$, and 19.48% after dividing by the iid factor 0.957
  [A19-53, A19-55, A19-47]; the calendar years give 22.207%. Autocorrelation would need a ratio of 1.43 [A19-13]. Cut
  the same 23 years into one-year blocks from each of 246 starting days: 11.89% to 25.04%, 46 grids at or above
  22.207% (X7) [A19-56]. With 2026's 185 sessions added, $\operatorname{VR}(246)=1.208$ [A19-53]; the 73.0% rise of 2026
  (lm17.md:347) moves a long-horizon ratio by itself.

**Problems plan** (12; MC keys C, A, B, A, C, B; the lab solves 7–12). Every stem states its sample (TR23, 3 January
2003 → 8 October 2026, $T=5{,}849$, or 2003–2025), simple or log returns, the divisor, $A$ (246.12, or a year of 246
sessions on 2003–2025), the quantile rule $R_{(\lceil uT\rceil)}$ where a quantile is used, and the rounding; every
answer is descriptive (no standard error, no test; "LM20 gives the standard error" where natural). No problem
simulates.

1. MC: TR23's returns on 16–20 March 2020 are −4.0582%, −2.8622%, −2.3407%, −5.6081%, +6.3683%; the 20% trimmed mean
   (one dropped at each end) is closest to: A −1.700% (the mean: nothing trimmed). B −2.862% (the median: two dropped
   at each end). **C** −3.087% [A19-60].
2. MC: the 23 calendar-year log returns have $s=22.207\%$ (divisor 23); $s_{\mathrm u}$: **A** 22.71%. B 23.22% (the
   factor 23/22 belongs to the variance). C 21.72% (divides instead of multiplies) [A19-61].
3. MC: TR23's MAD is 0.5889%; the normal-equivalent annual volatility with $A=246.12$ and the constant 1.4826: A 9.24%
   (a MAD is not a standard deviation). **B** 13.70%. C 6.23% (divides by 1.4826) [A19-62].
4. MC: quartiles −0.490%, 0.088%, 0.681% ([[LM14]]); the quartile skewness: **A** 0.013. B −0.013 (twice the median
   minus the quartiles: the sign reversed). C 0.163 (median left out) [A19-63].
5. MC: a model with $\rho_1=0.0393$ and no other autocorrelation; the ratio of (19.7) at $m=2$: A 1.0786 (the weight
   $1-k/m=\tfrac12$ forgotten). B 1.0195 (the ratio of volatilities, its square root). **C** 1.0393 [A19-64].
6. MC: iid daily log returns, $T=5{,}849$; the average of $\operatorname{VR}(1{,}231)$ is closest to: A 1.00 (assumes
   an unbiased estimator). **B** 0.79. C 0.21 ($m/T$, the size of the bias) [A19-65].
7. TR23's $s_r=1.2107\%$ (lm17.md:340), $m=246$, and [[LM16]]'s assumption: adjacent correlation 0.04, none other. Find
   the model's ratio of (19.7) and the annual volatility (1.0797; 18.99% → 19.73%) [A19-66]; compare TR23's lag 1
   alone, 1.0784, and $\operatorname{VR}(246)=1.208$, and say what the other lags add.
8. Derive (19.8)'s iid factor from (16.3) and (17.1); evaluate it at $m=246$, $T=5{,}664$ (0.957) and $m=1{,}231$,
   $T=5{,}849$ (0.790); correct 2003–2025's $\operatorname{VR}(246)=1.0536$ (1.101, 19.48%) [A19-47, A19-53, A19-55].
9. 2003–2025 log returns, $r_f=0$: daily Sharpe ratio 0.0400; annual by $\sqrt{246}$, 0.627; by (19.9) with
   $\operatorname{VR}(246)=1.0536$, 0.611; the calendar years' mean over standard deviation, 0.524 [A19-57]. Why the last
   is lower although the means agree (11.634% against 11.646%, lm17.md:347).
10. *(Python)* For the scaled Student $t$ of (15.11), show that $1.4826\,\mathrm{MAD}/\sigma=t_\nu^{-1}(0.75)
    \sqrt{(\nu-2)/\nu}/\Phi^{-1}(0.75)$; evaluate at $\nu=5$ (0.835) and at [[LM15]]'s $\nu=3.065$ (0.667), against
    TR23's 0.723 [A19-67]. Uses `stats.t.ppf` (recorded in SOURCES before Stage 2).
11. *(Python)* $\hat\rho_k$ of TR23's $r$, $\lvert r\rvert$ and $r^2$ for $k\le30$ in NumPy, checked with statsmodels'
    `acf(x, nlags=30, fft=False)`; count the lags outside $\pm1.96/\sqrt T$ with the guard (9, 30, 30) and report lag
    29's margin [A19-38–A19-40].
12. *(Python)* Weekly, monthly and calendar-year log returns of 2003–2025 with Polars (sorted after `group_by`); X1's
    four values; X7's lowest, highest and first-day grids and their median by $\hat F^{-1}(\tfrac12)$ [A19-08–A19-12,
    A19-56].

**Lab parts** (`build/make_lab19.py`; reads only `labs/LM19_lab/data/taiex_tr.csv`, the raw TR23 closes, which
`data/make_lab_data.py` copies from `data/raw/vol3/` as for LM17 and LM18; built locally, never committed): 1 data: TR23
from the closes, `Fraction` checks (distinct, no zero), $T$, years, $A$, the 2003–2025 and regime masks, the Saturday
sessions; 2 location: E1, E2, the trimmed mean by sorting, KC §2; 3 dispersion: E3, E4, X3 with
`np.lib.stride_tricks.sliding_window_view`; 4 shape: E5, E6, X2 with its regime and hypothetical columns, the closed
forms against `bias=False`; 5 autocorrelation: (19.5) in NumPy and statsmodels, X4, E7, KC §5; 6 variance ratios: E8,
X5, X6, E9, experiment $e=1$; 7 annualization: X1 by Polars periods, X7, E10, X8, KC §7; 8 problems 7–12. Extension
(stability check): $\operatorname{VR}(m)$ for $m$ = 5, 20, 60 within each limit regime: 1.070, 1.057, 1.215 before June
2015 and 1.013, 1.000, 0.975 after [A19-68]. Labs write plain "LM20".

**Cross-module tags.**

- (19.1) $s_{\mathrm u}^2:=\frac{T}{T-1}s^2$ (LM20, LM21).
- (19.2) For $R\sim\mathcal N(\mu,\sigma^2)$: $\E\lvert R-\mu\rvert=\sigma\sqrt{2/\pi}$, the median of $\lvert R-\mu\rvert$ is
  $\sigma\Phi^{-1}(0.75)$, the interquartile range $2\sigma\Phi^{-1}(0.75)$; so $\sigma=1.4826\times$ that median
  $=\text{IQR}/1.349$, with the constants rounded (referred to in X2, E4 and Problems 3 and 10; no later user yet).
- (19.3) $\widehat{\operatorname{Skew}}=\frac{\frac1T\sum_t(R_t-\bar R)^3}{s^3}$, $\widehat{\operatorname{Kurt}}=
  \frac{\frac1T\sum_t(R_t-\bar R)^4}{s^4}$ and the adjusted forms, printed as definitions (LM26's standardized
  residuals; LM20 and LM21 cite LM14's printed moments).
- (19.4) $\operatorname{Skew}_{\mathrm Q}$, $\operatorname{Kurt}_{\mathrm O}$, definitions; quantiles by $\hat F^{-1}$ (no
  user yet).
- (19.5) $\hat\gamma_k=\frac1T\sum_{t=k+1}^T(x_t-\bar x)(x_{t-k}-\bar x)$, $\hat\rho_k=\hat\gamma_k/\hat\gamma_0$ (LM20,
  LM22, LM23, LM25, LM26).
- (19.6) $\Var\hat\rho_k\approx1/T$ for iid $x_t$ with finite variance; band $\pm1.96/\sqrt T$ (LM21, LM25, LM26).
- (19.7) $\Var r_t^{(m)}=m\gamma_0+2\sum_{k=1}^{m-1}(m-k)\gamma_k$, so the model's ratio is
  $\Var r_t^{(m)}/(m\gamma_0)=1+2\sum_{k=1}^{m-1}(1-k/m)\rho_k$, for a weakly stationary series (LM20, LM22, LM23,
  LM25, LM26, LM33).
- (19.8) $\operatorname{VR}(m):=\frac{\frac1{T-m+1}\sum_{t=m}^{T}(r_t^{(m)}-m\bar r)^2}{m\,s_r^2}$, with iid factor
  $\approx(1-m/T)/(1-1/T)$; $\operatorname{VR}_{\mathrm n}(m)$ the same ratio on the $\lfloor(T-o)/m\rfloor$ consecutive
  blocks after $o$ skipped returns (LM20, LM22, LM25).
- (19.9) $\mathrm{SR}(m)=\sqrt m\,\mathrm{SR}\big/\sqrt{\Var r_t^{(m)}/(m\gamma_0)}$ for log-return sums with constant
  mean, under (19.7)'s conditions, estimated with $\operatorname{VR}(m)$ in the denominator (LM33).

**Pitfalls to pre-empt.**

- Divisors: $s$ divides by $T$; $s_{\mathrm u}$ only where named; NumPy's `std` defaults to 0 and Polars' to 1 (SOURCES);
  name the divisor for the 23 years (22.207% against 22.706%) and for the five-day week.
- Quantile rule: $\hat F^{-1}(u)=x_{(\lceil un\rceil)}$ everywhere, including the median, MAD, the 246-day windows and
  the median of X7's 246 grids (the 123rd value, 19.13%, not `np.median`'s midpoint 19.15%). Here $T-1=5{,}848$ is a
  multiple of 8, so NumPy's default quantiles agree with the rule at every quartile and octile (as statsmodels' do).
- Return type: §2–§4 on $R$, §5–§7 on $r$; X8 gives $R$ first and $r$ in brackets and says so.
- Samples: TR23, 2003–2025 and the regimes in separate statistics; $A=246.12$ against a year of 246 sessions.
- One variance ratio: $\operatorname{VR}(m)$ is (19.8), centred at $m\bar r$ of the whole sample (the acf's full-sample
  mean); the weighted sum of $\hat\rho_k$ appears only as X6's identity column (and E8's 1.280 from it). LM18's 0.283 is
  about the windows' own mean, so E9 says so and prints no own-mean ratio. Overlapping windows are not independent
  observations.
- The band is iid; lag 29 of $r$ is 0.00002 inside it, so tooltips print five decimals; the counts use the guard.
- Ownership: TR23's median, quartiles, −0.338 and 5.27 are [[LM14]]'s; $s$ and kurtosis by regime and the 7 April
  jump [[LM15]]'s; 18.563%, 11.634% and the pair correlations [[LM17]]'s; 1.0797 [[LM16]]'s on U28 prices. LM19's own
  18.96% and 0.81 are cited by later modules.
- Inference edge: no standard error, interval or test on any TR23 number; the grids' range is not an interval; the
  sentence on the robust band gives no number (0.0205 is LM25's [A19-41]).
- Rounding: every printed value is rounded from its unrounded value, never from a rounded figure;
  `plans/vol-4-anchors.md` flags each one within a tenth of a unit of a boundary. The tight ones: [[LM17]]'s pair
  correlation 0.0394 (0.03935009); X6's 1.047 and 1.140; X2's 0.868%, −0.2768, 0.1055% and the extra day's 1.216%; X7's median 19.13%; 19.05% (the
  printed 1.0536 also gives it); 18.12% (the printed 5.2296% also gives it); the robust annual scales print one decimal
  (13.7%, 13.6%), because the literal 1.349 would change the second.
- Chart text: "sample mean", no hats; "√" is allowed; formula punctuation ("$5\%$", "$m$-day" → "an m-day" in
  words where a hyphen follows math).
- References: the robust shape measures (19.4) and the adjusted moments are printed as definitions, without Kim and
  White (2004), Moors (1988) or Joanes and Gill (1998), until the papers are read; Lo and MacKinlay are not named in
  LM19 (the test is LM25's, attributed after their text is read); Lo (2002) is cited for the annualization caveat only,
  as its abstract supports; the band's normality is *stated without proof* until its source is read.

**Stage 4 for earlier modules** (merged into `plans/vol-4.md`'s list).

- `leads` gain 19 in lm03.md:6 (link at :330), lm04.md:6 (:132) and lm05.md:6 (:367, :745); lm10.md:6, lm14.md:6,
  lm15.md:6, lm16.md:6, lm17.md:6 and lm18.md:6 already list it.
- `build/make_lab17.py:486`: "LM26 treats the autocorrelation convention" → "LM19 defines the autocorrelation
  convention".
- `build/make_lab15.py:443`: "and LM19 the sampling error of such statistics" → "LM19 shows how such statistics vary
  with the sample, and LM20 measures their sampling error".
- lm15.md:263 is reworded with LM20's wording; LM19's E10 agrees that the data do not establish a direction.

**Open before Stage 2** (sources not yet read; until then the text is written as the decisions say):

1. A source for $\Var\hat\rho_k\approx1/T$ and the normal limit of $\hat\rho_k$ (Tsay 2010, or Box, Jenkins, Reinsel
   and Ljung): until it is read, the band's approximate normality is *stated without proof*.
2. The texts of Kim and White (2004), Moors (1988, end page) and Joanes and Gill (1998): until they are read,
   quartile skewness, octile kurtosis and the adjusted moments are printed as definitions, unattributed.

## LM20 Estimation Theory and Maximum Likelihood

Stage 1 brief, revised 2026-10-19 after the cross-check and the independent recomputation. It follows the editor's
decisions (`plans/vol-4.md`, "Editor's decisions on the LM19–LM25 drafts") and the cross-check's findings X1, X2, X5,
X19, X25, X27, X32, X34, X35, X37 and §8, and to the fresh check's findings after them. Each number carries its anchor
ID at its first appearance; `data/vol4_anchors_lm20.py` prints them all (rows in `plans/vol-4-anchors.md`). Numbers
quoted from published modules cite their file:line instead.

**Prereq:** `[1, 2, 4, 5, 7, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]`.

- LM1: (1.12) $\ln G=\sum_tr_t$ (lm01.md:404): the mean log return depends only on the first and last price (§3).
- LM2: (2.1) $1+x\le e^x$ (lm02.md:111), used as $\ln\lambda\le\lambda-1$ in Deep Dive 1.
- LM4: (4.3) $f_q\approx\mu/\sigma^2$ (lm04.md:118) and the quadratic rule $\hat\mu/s^2=5.680$ for 0050 (lm04.md:128);
  the stated $s/\sqrt T$ and 1.96 (lm04.md:541); the band example (lm04.md:543–551: SE 0.0230% a day, interval
  0.042%–0.132%, exact Kelly band 2.7–7.6, quadratic 2.7–8.6); "[[LM20]] and [[LM45]]" (lm04.md:573).
- LM5: the normal model and its density, 0050's fit $\hat\mu=0.0871\%$, $s=1.2385\%$ (lm05.md:449); (5.9) (lm05.md:444);
  the $t$ with $\nu=3$ chosen by eye (lm05.md:497).
- LM7: (7.1) the first-order expansion (lm07.md:105), (7.2) gradient and Hessian $H$ (lm07.md:175), (7.4) the sign of
  $H$ at a maximum (lm07.md:252); 7.36 and 6.09 points (lm07.md:507).
- LM10: (10.2) $\hat\Sigma$ with divisor $T$ (lm10.md:127); (10.4) $\mathbf w^{\top}\hat\Sigma\mathbf w$ (lm10.md:181), the
  delta method's quadratic form; the $T-1$ pitfall and its 1.000114 (lm10.md:166).
- LM11: eigenvalues add up to the trace and multiply to the determinant (lm11.md:92, extended in its Section 3);
  (11.3) (lm11.md:119); the eigenvalue-error pointer (lm11.md:406).
- LM12: (12.8) the Cholesky factor $\hat\Sigma=LL^{\top}$ (lm12.md:407), in Deep Dive 1.
- LM13: (13.13) independent trials, "iid" (lm13.md:394); the 108 falls of 3% or more (lm13.md:33), Hill's main $k$.
- LM14: (14.3) (lm14.md:158), (14.4) (lm14.md:200), (14.5) $\operatorname{Skew}$, $\operatorname{Kurt}$ (lm14.md:208),
  (14.6) $\E Z^4=3$, $\Var(Z^2)=2$ (lm14.md:226); TR23's $\bar R=0.0625\%$, $s=1.2084\%$, skewness −0.34, kurtosis 8.27
  (lm14.md:21, 233, 241); 2008 at −43.07% and 2009 at +83.34% (lm14.md:39).
- LM15: (15.6) $\Phi^{-1}(0.975)=1.9600$ (lm15.md:190, 196); (15.9) the $t$ density (lm15.md:300), (15.10) (lm15.md:319),
  (15.11) (lm15.md:324); (15.13) chords (lm15.md:429) with 2.09–5.03 and 4.17 (lm15.md:438–440); the ML fit $\nu=3.065$,
  location 0.0997%, scale 0.7761%, standard deviation 1.317% (lm15.md:349); the regime table (lm15.md:406–419); the
  annual log returns' 0.11646 and 0.22207 (lm15.md:256); monthly counts' dispersion 3.02 (lm15.md:417).
- LM16: (16.1) (lm16.md:129), (16.2) and $\lvert\rho_{XY}\rvert\le1$ (lm16.md:142–144), (16.3) (lm16.md:197), (16.4)
  (lm16.md:220), (16.7) with the $\mathcal N_N$ density (lm16.md:319–322), (16.8) (lm16.md:339); the pair's
  $\hat\rho=0.5749$ (lm16.md:34, 177).
- LM17: (17.1) (lm17.md:69), (17.2) (lm17.md:99), (17.5) (lm17.md:276); the standard error named (lm17.md:71); 18.563%
  (lm17.md:347).
- LM18: (18.2) (lm18.md:141), (18.3) (lm18.md:147), (18.8) (lm18.md:337); "derives the same $s/\sqrt T$" and
  0.01580% (lm18.md:339, cited there; also lm18.md:345); $s_Y/\sqrt{2n}$ (lm18.md:150); batch standard errors
  (lm18.md:153).
- LM19 (published with LM20): (19.1) $s_{\mathrm u}$, introduced in one paragraph; (19.5) $\hat\rho_k$, (19.7) the
  model's ratio and (19.8) $\operatorname{VR}(m)$, which test the iid assumption the standard errors make; the
  annual-volatility gap it hands over; TR23's point estimates $A\bar R=15.38\%$, $\sqrt A\,s=18.96\%$ and Sharpe ratio
  0.0517 a day, 0.81 a year (LM19 owns them; LM20 owns their standard errors and intervals).

**Leads:** `[21, 22, 23, 24, 25, 26, 30, 32, 33, 45]`: tag users and pointer targets (LM21's interval duality and
tests, LM22's bootstrap against (20.8)–(20.9), LM23's standard errors, LM24's MSE and prior, LM25's maximum likelihood
and delta method ((20.6), (20.8)), LM26's likelihood, LM30's estimation error, LM32's tail models ((20.10), the §8
pointer), LM33's Sharpe ratio, LM45's Kelly sizing).

**Forward links honoured.**

| Earlier text | Promise | Kept in |
|:--|:--|:--|
| lm04.md:541 | derive $s/\sqrt T$, "develops confidence intervals" | §3 (20.2), E2; §4 (20.4), E4 |
| lm04.md:543–551; `make_lab04.py:506` | SE 0.0230%, 0.042%–0.132%, Kelly band 2.7–7.6 ("preview of LM20 and LM45") | §7 E9: LM4's quadratic band is the delta method with the mean's error only; recomputed under LM20's name, the variance adds 2% to the standard error; the exact band is quoted |
| lm04.md:573 | "[[LM20]] and [[LM45]] supply the statistics that must come before any leverage decision" | §7 E9, [[ex:delta]]; LM45 named for sizing |
| lm05.md:449 | $\hat\mu$, $s$ are "the maximum-likelihood choice" | §5 (20.5), E5; LM5's "population standard deviation" is read as the sample one with divisor $T$ (its wording stays: Stage 4 declines a change) |
| lm05.md:497 | "[[LM20]] estimates $\nu$" | §5–§6, E6: $\nu$ with its standard error on TR23 (LM5 used 0050; one main sample here) |
| lm07.md:507 | SE $\approx\sigma/\sqrt{\text{years}}$: 7.36 (0050), 6.09 (00679B) | §3 (20.2), second form, derives it; LM7's values quoted |
| lm10.md:166 | $T-1$ removes a small bias "under assumptions that [[LM20]] states" | §3 (20.3): uncorrelated draws with a common mean and variance |
| lm11.md:406; `make_lab11.py:571` | an eigenvalue's sampling error, "[[LM20]] gives the tools" | §7: the delta method applies to any smooth statistic; one sentence sends the eigenvalue share to LM22's bootstrap; Stage 4 rewords the lab line |
| lm14.md:51 | "[[LM20]] treats estimation" | the module |
| lm14.md:211 | $T$ or $T-1$; "how far such numbers move between samples" | §3 (20.3); §7 pitfall: under the $t$ fit ($\nu<4$) the sample kurtosis has no finite standard error; the adjusted skewness and kurtosis stay LM19's |
| lm15.md:62 | "[[LM20]] and [[LM21]] add standard errors and tests" | §6–§7 standard errors; tests LM21 |
| lm15.md:349 | `t.fit` is maximum likelihood, "which [[LM20]] develops" | §5–§6, E6, [[ex:fits]], [[ex:profile]] |
| lm15.md:419, 615 | the regime table has no standard errors; none "says whether a change exceeds chance" | E6 ($\nu$), E8 ($s$), Problem 7; the test stays LM21's; the kurtosis gets a sentence saying why it has none |
| lm15.md:440 | "[[LM20]] estimates a tail index with its standard error" | §8, E10, [[ex:hill]] |
| lm15.md:263 | "independent days scaled by $\sqrt m$ understate the annual spread ([[LM19]])" | §7 E8 measures the gap against the sampling error of 23 values (1.1 standard errors); Stage 4 rewords the line |
| lm16.md:177 | the error of $\hat\rho=0.5749$ "is [[LM20]]'s subject" | Problem 6 (delta method, normal and plug-in) |
| lm17.md:71 | $s$ in place of $\sigma_X$, "[[LM20]] derives that estimate" | §3: $s$ is consistent, and (17.5) with $s$ stays approximately normal (stated) |
| lm17.md:310 | 9,604 is a model property, "not an interval for a data frequency ([[LM20]])" | Problem 9: TR23's up-day frequency $\hat\theta$ with its interval |
| lm18.md:149 | "[[LM20]] develops standard errors and confidence intervals for data" | §3–§4 |
| lm18.md:339 (the spine's 345; cited as lm18.md:339) | "[[LM20]] derives the same $s/\sqrt T$" | §3 E2: 0.01580% a day |
| lm18.md:150, 527 | $s_Y/\sqrt{2n}$ for near-normal draws; 0.01580% | §6 E7 derives $s/\sqrt{2T}$ from the information; same values |
| plans/vol-3.md:1241 (unpublished plan) | standard errors of $\hat\rho$; maximum likelihood for $\mathcal N_N$ | Problem 6; §5 and Deep Dive 1 |

**Outcomes** ("After this module you should be able to:"):

1. explain an estimator as a random variable with a sampling distribution, and calculate its bias, variance and mean squared error, including the trade-off of a scaled mean
2. derive the standard error $\sigma/\sqrt T$ of a sample mean and the bias of $s^2$, and explain why the standard error of an annualized mean depends on the years of data, not on the sampling frequency
3. construct and interpret confidence intervals for a mean, with the normal approximation and with the $t_{T-1}$ interval of a normal model, and check their coverage by simulation
4. derive the maximum-likelihood estimators of the normal model, and fit a Student-t by maximum likelihood numerically
5. compute standard errors from the observed Fisher information, and state asymptotic normality and the Cramér–Rao bound with their conditions
6. apply the delta method to the annualized volatility, the Kelly fraction and the Sharpe ratio of independent returns
7. estimate a tail index with the Hill estimator and its standard error, and explain how the threshold trades bias against variance
8. compute estimates, standard errors and intervals in Python with explicit divisors and seeded simulations

**Owns.** An estimator as a random variable; its sampling distribution, shown by simulation from models fitted to TR23
([[ex:sampling]]); bias, variance, $\operatorname{MSE}$ and (20.1); a scaled mean $\eta\bar R$ and its best $\eta^*$, the
bridge to LM24; consistency, stated. $\operatorname{SE}(\bar R)=\sigma/\sqrt T$ from (16.3) and (17.1), estimated by
$s/\sqrt T$, and its annual form $\sqrt A\,\sigma/\sqrt\tau$ (20.2); Merton's point and [[ex:merton]]; the bias of
$s^2$ and the unbiased $s_{\mathrm u}^2$ (20.3). Confidence intervals (20.4): the normal approximation by (17.5), the
$t_{T-1}$ interval of a normal model (its law in one line from Blitzstein and Hwang's Ex. 7.5.9, Ex. 10.4.3 and
Def. 10.4.4), coverage ([[ex:coverage]], the widget), the interval against years of data ([[ex:years]]). Likelihood, log-likelihood, the normal MLE (20.5), the MLE of $\mathcal N_N$
stated with Deep Dive 1 (why $\hat\Sigma$ divides by $T$); the Student-t MLE on TR23 with standard errors from the
observed information ([[ex:fits]]) and its profile log-likelihood ([[ex:profile]]); Fisher information, asymptotic
normality (20.6) and Cramér–Rao (20.7), stated, with Deep Dive 2. The delta method (20.8); the standard errors of the
annualized volatility, the plug-in Kelly fraction $\hat f:=\bar R/s^2$ and the Sharpe ratio under iid returns (20.9);
the sampling error of 23 annual values (LM19's gap), by the delta method and by the $\chi^2$ interval of a normal
model. The Hill estimator (20.10) derived as a Pareto MLE, with its standard error, at LM13's and LM15's thresholds.
Values owned (one owner per statistic; cross-check X1): every standard error and interval in [[ex:case]] and
[[ex:delta]]; $\hat f=4.28$ with its standard errors; the standard errors and intervals of [[LM19]]'s 15.38%, 18.96%
and 0.81, whose point estimates LM20 cites; the $t$ fit's standard errors,
profile and regime standard errors; the Hill estimates; the coverage and sampling-distribution simulations; the
standard errors of $\hat\rho$, of the up-day frequency $\hat\theta$ and of the monthly Poisson mean (problems).

**Leaves.** Tests, p-values, the likelihood-ratio test and the two-sample comparison of the regimes (unpooled
variances, X35) → LM21. Quantile standard errors (LM15's regime table's 1% quantile included; none printed here) →
LM32. Bootstrap
standard errors and intervals (Sharpe ratio, Kelly fraction, a variance ratio, LM16's crash correlation, LM11's
eigenvalue share) → LM22. Regression standard errors and HAC → LM23. Priors, posteriors and the prior that fixes
$\eta^*$ → LM24. The autocorrelation-robust standard error of a mean: LM19 measures the dependence, LM23 (HAC) and
LM25 (robust bands) correct for it. GARCH likelihood → LM26 (uses (20.5)–(20.6)). The Sharpe ratio under dependent
returns, PSR and DSR → LM33. Estimation error in portfolio weights → LM30; Kelly sizing under parameter uncertainty →
LM45. Tail-based VaR → LM32. Extreme value theory beyond Hill (block maxima, the
generalized Pareto) → not in the book, one sentence. The adjusted skewness and kurtosis estimators → LM19.

**Uses before taught** (one sentence each in the text):

- §2: "Whether TAIEX's days are independent is a question about data, which [[LM19]] answers; here the model assumes it."
- §2, E1: "The best $\eta$ depends on the unknown $\mu$; [[LM24]] supplies it from a prior."
- §3: "[[LM19]]'s variance ratios measure how far daily variances fail to add up; [[LM23]]'s HAC errors and [[LM22]]'s
  block bootstrap then repair the standard error."
- §4: "An interval that excludes a value is the start of a test, [[LM21]]'s subject; this module runs none."
- §5: "[[LM26]] fits GARCH models with the same machinery."
- §6: "Comparing two maximized log-likelihoods is a likelihood-ratio test ([[LM21]])."
- §7: "For a statistic with no formula, such as [[LM11]]'s eigenvalue share, [[LM22]]'s bootstrap replaces the delta
  method"; "the Sharpe ratio of dependent returns is [[LM33]]'s, and sizing with an uncertain fraction [[LM45]]'s."
- §8: "Value at risk from a tail model is [[LM32]]'s."

**Data role.** Three samples, never mixed in one statistic; every caption names its sample.

- **TR23** (main): `data/processed/vol3_taiex.parquet` (`data/vol3_series.py`; FinMind `TaiwanStockTotalReturnIndex`,
  data_id TAIEX, retrieved 2026-10-18): 5,850 closes, $T=5{,}849$ simple returns $R_t$ from 2003-01-03 to 2026-10-08
  [A20-01]; 8,680 calendar days, $\tau=23.7645$ years, $A=246.12$ [A20-02]. One-day statistics on $R$; sums (Merton's
  $m$-day sums, calendar years) on $r=\ln(1+R)$. $\bar R=0.062505\%$, $s=1.208364\%$ (divisor $T$), $s_{\mathrm u}=1.208468\%$,
  $s_{\mathrm u}/s=1.0000855$ [A20-03] ([[LM14]]'s $\bar R$ and $s$, recomputed). Calendar years 2003–2025, 2003 from
  its first close, only for the 23 annual log returns (mean 0.11646, standard deviation 0.22207 with divisor 23,
  [[LM15]]'s; the daily model refitted to the 5,664 returns of 2003–2025 gives $\sqrt{246}\,s_r=18.563\%$, [[LM17]]'s)
  [A20-06]. Counts use the guard (`R <= -x + 1e-12`, `R > 1e-12`) and are checked with `Fraction` on the two-decimal
  closes. Limit regimes by return date: 3,077 returns to 2015-05-29, 2,772 from 2015-06-01 ([[LM15]]).
- **U28** (Problem 6 only): `data/lm10_series.py` (Volume II, repaired by `data/vol2_series.py`), $T=4{,}382$
  price-index returns 2008-12-02 → 2026-10-08, $A=245.48$; Semiconductor and FinancialInsurance, $\hat\rho=0.5749$
  [A20-04] ([[LM16]]'s, recomputed). Captions say "price indices, no dividends".
- **LM4's 0050 sample** (E9's 0050 row only): `data/processed/etf_daily_returns.parquet`, column `R_0050`, 0050's
  one-session total returns on the 2,902 common dates of 0050 and 00631L, 2014-11-03 → 2026-10-08; $\hat\mu=0.0871\%$,
  $s=1.2385\%$ [A20-05], recomputed under LM20's name as the shared decisions allow (LM4's interval).
- No TX23 and no T5S. No published file carries a daily series (editor's rule, X37): the charts plot standard errors
  by sampling interval, Hill estimates by threshold, model curves and simulated histograms; the widget simulates.
- Seeds (AUTHORING §8; the array shapes are in `plans/vol-4-anchors.md`): experiment 1, [[ex:sampling]] (`default_rng([1,
  20261011])`, 10,000 one-year samples of 246 days, normal draws first, then Student-t draws with LM15's $\nu$);
  experiment 2, [[ex:coverage]] (`[2, 20261011]`, 100,000 samples per cell in chunks of 10,000, normal block then $t_3$
  block for each $T$); experiment 3, Problem 11 (`[3, 20261011]`, 20,000 samples); experiment 4 (`[4, 20261011]`), 20
  further runs of experiment 1's Student-t block, whose spread stands in for the Monte Carlo error that the $t$ block's
  two standard deviations lack (their fourth moments are infinite at $\nu<4$). Simulated quantiles are $\hat F^{-1}(u)$
  (`method="inverted_cdf"`) with [[LM18]]'s batch standard errors (20 batches, divisor 20). Scripts:
  `data/lm20_numbers.py` (every printed value, asserted against `src/lm20.md`; recounts with `Fraction`; flags each
  printed form within a tenth of a unit of a rounding boundary at its printed precision; compares with the anchors),
  `data/lm20_charts.py` ([[ex:sampling]], [[ex:merton]], [[ex:years]], [[ex:profile]], [[ex:hill]], the widget's data
  block); anchors `data/vol4_anchors_lm20.py`.

**Hygiene declaration.** *In-sample:* every estimate, standard error and interval on TR23, U28 and the 0050 sample
([[ex:case]], [[ex:merton]]'s data points, [[ex:fits]], [[ex:profile]], [[ex:delta]], [[ex:hill]], E2–E10). *Model:*
the simulations ([[ex:sampling]] with experiment 4, [[ex:coverage]], the widget, Problem 11), Merton's iid lines and
[[ex:years]]'s band as a function of hypothetical years. *Stability check:* the two limit regimes ($\nu$ and $s$ with
standard errors).
Nothing is *Descriptive* (LM19's) or *Out-of-sample*. Tests run: none (LM21's rule; the text says so). Local note:
"Every TAIEX figure describes the total-return index, 3 January 2003 to 8 October 2026 (5,849 daily returns), except
the 23 calendar years 2003–2025 (2003 from its first close). Every estimate, standard error and interval is
in-sample and assumes independent, identically distributed days unless it says otherwise; none is a forecast.
Simulated samples are models. The two price-limit regimes are a stability check. This module runs no tests
([[LM21]])."

**Notation.** AUTHORING §6 and its Volume IV table. Used: $R$, $r$, $\mu$, $\sigma$, $\bar R$, $s$ (divisor $T$),
$s_{\mathrm u}$ (divisor $T-1$), $\bar r$, $s_r$, $T$ (a count), $t$, $\tau=T/A$ (the span in years), $A$, $f$,
$\hat f:=\bar R/s^2$ (the plug-in Kelly fraction; §6 makes it book-wide from LM20), $\mathrm{SR}$ ($r_f=0$), $\Pr$,
$\E$, $\Var$, $\Cov$, $\operatorname{Skew}$, $\operatorname{Kurt}$, $\varphi$, $\Phi$, $\Phi^{-1}$, $f_R(x;\theta)$ (a
model's density of $R$), $F_Y^{-1}$, $\hat F^{-1}$ (quantiles of simulated values, [[LM14]]'s), $\mathcal N$,
$\mathcal N_N$, $t_\nu$, iid, $X$, $Y$, $Z$, $x$, $\mu_X$, $\sigma_X$, $\theta$, $\hat\theta$ (also Problem 9's up-day
probability and its frequency, X5), $\boldsymbol\theta$, $\operatorname{Bias}$, $\operatorname{MSE}$, $\operatorname{SE}$,
$\mathcal L(\theta)$, $\ell(\theta)$, $\mathcal I(\theta)$, $H$ ([[LM7]]'s Hessian, here of $\ell$), $\nabla$, $\eta$
([[LM5]]'s constant), $n$ (simulated samples), $m$ (days in a sum), $\nu$, $\alpha$ (a tail index, as [[LM15]]),
$\rho$, $\hat\rho$ (Problem 6), $\boldsymbol\mu$, $\Sigma$, $\hat\Sigma$, $\mathbf R_t$, $N$, $\lambda_k$ and $L$ (Deep
Dive 1 only), $\lambda$ (Problem 8's Poisson mean), $\chi^2_N$ (E8's interval, $\chi^2_{22}$), $^{\top}$,
$\operatorname{tr}$, $\det$, $I$. Local:

| Symbol | Meaning | Check |
|:--|:--|:--|
| $\eta$, $\eta^*$ | a constant multiplying $\bar R$; the $\eta$ that minimizes $\operatorname{MSE}(\eta\bar R)$ | LM5's letter; a star marks an optimum |
| $\tau$ | span of the data in years, $T/A$ (23.7645 for TR23) | §6's $\tau$ row: "any span in years when $T$ is a count" |
| $T_m$ | number of non-overlapping $m$-day sums, $\lfloor T/m\rfloor$ | a count of returns, as $T$ |
| $\widehat{\mathrm{SR}}$ | $\bar R/s$, the daily Sharpe ratio's estimate | hatted book-wide symbol |
| $h(\boldsymbol\theta)$ | a smooth function of the parameters in the delta method | §6's generic $h$ |
| $x_0$; $k$; $x_i$ | Hill's threshold, a loss level ([[LM15]]'s $x$); the number of losses at or beyond it; those losses $-R_t$ | $k$ declared (Volume IV table allows it); no lags here |
| $\varepsilon$ | a tolerance in the consistency statement, $\varepsilon>0$ | as [[LM17]]; LM23's residual does not occur |

Formulas write skewness and kurtosis as $\operatorname{Skew}(R)$ and $\operatorname{Kurt}(R)$ (no $m_3$, $m_4$:
[[LM4]]'s $m_k$ are raw moments). The observed information is "$-\ell''(\hat\theta)$", or "$-H$ at $\hat{\boldsymbol\theta}$"
for a vector, never a new letter. The 95% interval writes its level in words or as "95%": $\alpha$ is the tail index.
Charts carry no Greek (AUTHORING §7): "degrees of freedom", "tail index", "sample mean". Not used: $P$, $\kappa$,
$q$ (as a quantile), $p$ for a frequency ($\hat\theta$, X5), $\theta$ as an angle, $\mathcal L$ as a Lagrangian, $I$
for information, $\beta$, $\rho_k$, $\hat f^*$ and $f_{\mathrm B}$ (LM22's and LM24's), $\operatorname{med}$ (the
median is written in words), a star for a simulated draw.

**Motivating case: "What 23.8 years pin down"** (box, about 140 words)

> From 3 January 2003 to 8 October 2026 the TAIEX total-return index, dividends reinvested, had calendar years from
> −43.07% (2008) to +83.34% (2009) [A20-07] ([[LM14]]). Its average day, 0.0625%, is 15.38% a year at $A=246.12$
> sessions; its daily standard deviation, 1.2084%, is 18.96% a year [A20-08] ([[LM19]]). Treat the 5,849 days as
> independent draws from one distribution. The same days then pin the volatility to within about a third of a point
> [A20-10], but leave the mean anywhere from 7.8% to 23.0% a year at 95% [A20-09]. Sampling every five minutes instead
> of daily would not narrow that range; only more years would. Why is the mean so much harder to estimate than the
> volatility, and how far can the Kelly fraction of 4.28 [A20-11] that these numbers suggest be trusted?

Resolved: (a) the mean's precision: §3, (20.2), E2, [[ex:years]] (3.89 points [A20-09]); (b) five-minute sampling:
§3, Merton (1980), [[ex:merton]]; (c) the volatility's precision: §7, (20.8), E8 (0.33 points with the sample
kurtosis, 0.175 for normal days [A20-10]); (d) the Kelly fraction $\hat f$: §7, (20.9), E9 (2.10 to 6.46); the whole
set in [[ex:case]]. The case says "independent" once and the hygiene note says what LM19 checks. The 15.38% and the
18.96% are [[LM19]]'s estimates (its X8), here given their standard errors; the 4.28 is LM20's, with its errors.

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | framing paragraph; case + [[ex:case]]; roadmap; notation and hygiene notes | 380 |
| 2 | Estimators, Bias and Mean Squared Error {1} | a statistic before the data are drawn is a random variable; [[ex:sampling]] (one-year samples from models fitted to TR23; under the $t$ model the volatility's spread is itself erratic, about 4 points, 3.3 to 4.6 over 20 further runs [A20-51]); $\theta$, $\hat\theta$; bias, variance, (20.1) $\operatorname{MSE}=\Var+\operatorname{Bias}^2$; E1: $\eta\bar R$, $\eta^*=T\,\mathrm{SR}^2/(1+T\,\mathrm{SR}^2)$, 0.397 for one year and 0.940 for the sample [A20-12]; consistency stated ((17.2) for $\bar R$); pitfall: unbiased is not best; 中文導讀 | 575 |
| 3 | The Standard Error of a Mean {2} | (20.2) from (16.3) and (17.1), uncorrelated days with a common mean and variance; $s/\sqrt T$ consistent (stated); E2: 0.01580% a day [A20-13] ([[LM18]]'s (18.8)), 3.89 points a year; the annual form $\sqrt A\,\sigma/\sqrt\tau$; (1.12): $A\bar r=\ln(P_T/P_0)/\tau$, so finer sampling leaves the estimate itself unchanged; Merton (1980); [[ex:merton]]; ±1 point at 95% needs 1,381 years [A20-14]; (20.3) by expanding $\sum(X_i-\bar X)^2$; E3: $s_{\mathrm u}/s$ is 1.0000855 on TR23 and 1.0225 on 23 annual values (22/23 = 0.9565 for $\E s^2/\sigma^2$, $s_{\mathrm u}=22.706\%$) [A20-15], LM10's 1.000114 cited; pitfall: annualizing the mean's SE by $\sqrt A$ (0.25 instead of 3.89 points [A20-42]); 中文導讀 | 600 |
| 4 | Confidence Intervals {3} | definition by coverage; (20.4): $\bar R\pm1.96\,s/\sqrt T$ by (17.5) and (15.6); the $t_{T-1}$ interval with $s_{\mathrm u}$ for normal days, its law in one line: by Blitzstein and Hwang's Ex. 7.5.9 $\bar R$ and $s_{\mathrm u}^2$ are independent, by Ex. 10.4.3 $V=(T-1)s_{\mathrm u}^2/\sigma^2\sim\chi^2_{T-1}$, and with $Z=\sqrt T(\bar R-\mu)/\sigma$ Def. 10.4.4 gives $Z/\sqrt{V/(T-1)}=\sqrt T(\bar R-\mu)/s_{\mathrm u}\sim t_{T-1}$ (X32); E4: 7.8% to 23.0% a year; $F_Y^{-1}(0.975)=1.96037$ against 1.95996 at $T-1=5{,}848$ [A20-16]; one year of data, ±37.2 points [A20-18]; [[ex:coverage]] (experiment 2) [A20-17]; [[ex:years]]; widget; pitfall: "95% probability that $\mu$ is inside" ([[LM24]] gives that statement a meaning) | 540 |
| 5 | Maximum Likelihood {4} | $\mathcal L(\theta)=\prod_tf_R(R_t;\theta)$ for iid days (a density keeps its subscript; $f$ is an exposure), $\ell=\ln\mathcal L$; (20.5) the normal MLE derived ($\hat\sigma=s$, divisor $T$); E5 (LM5's 0050 fit is the MLE); $\mathcal N_N$ stated (why (10.2) divides by $T$), Deep Dive 1; E6: the Student-t on TR23 by numerical maximization, $\nu=3.065$, location 0.0997%, scale 0.7761% with standard errors 0.144, 0.0124%, 0.0138% [A20-20]; $\ell$ rises by 561.8 over the normal [A20-19]; the fit's standard deviation 1.317% (SE 0.045) against $s=1.2084\%$ [A20-21]; [[ex:fits]]; pitfall: the $t$ location is not the mean (skewness); 中文導讀 (with §6) | 560 |
| 6 | Fisher Information and the Cramér–Rao Bound {5} | score, $\mathcal I(\theta)$, observed information $-\ell''(\hat\theta)$; (20.6) asymptotic normality, conditions, stated; E7: the normal's information gives $\sigma/\sqrt T$ and $s/\sqrt{2T}=0.0112\%$ [A20-24], [[LM18]]'s $s_Y/\sqrt{2n}$; [[ex:profile]]: the profile log-likelihood of $\nu$ against its parabola (2.80 to 3.37 against 2.78 to 3.35 [A20-23]); $\hat\nu$ and the scale correlate 0.68 [A20-22]; (20.7) Cramér–Rao stated, attained by $\bar R$ in the normal model, Deep Dive 2; the $t$ location's 0.0124% against $\bar R$'s 0.0158% (ratio 0.78 [A20-25]) holds only inside the $t$ model; regimes: $\nu$ 2.990 (SE 0.195) and 3.237 (SE 0.223) [A20-26]; pitfall: an information-based SE assumes the model (Problem 8) | 540 |
| 7 | The Delta Method {6} | (20.8) from (7.1) and (16.4) ((10.4)'s quadratic form); one-parameter case first: $s=\sqrt{s^2}$, $\Var(s^2)\approx(\operatorname{Kurt}-1)\sigma^4/T$ by the sum rule; E8: annual volatility 18.96% ([[LM19]]'s) ± 0.33 (sample skewness −0.34, kurtosis 8.27 [A20-27], [[LM14]]'s) or ± 0.175 (normal); the 23 annual values: 22.207% ± 3.27, interval 15.8% to 28.6%, so LM17's 18.563% (± 0.34) lies 1.1 standard errors below [A20-31]; under a normal model for the years, Ex. 10.4.3's $23s^2/\sigma^2=22s_{\mathrm u}^2/\sigma^2\sim\chi^2_{22}$ gives the interval 17.6% to 32.1% for $\sigma$ (quantiles 10.98 and 36.78) [A20-32]; (20.9) for $\hat f=\bar R/s^2$ and $\bar R/s$; E9: $\hat f=4.28\pm1.11$ (mean only 1.08), interval 2.10 to 6.46 [A20-28]; Sharpe ratio ([[LM19]]'s 0.0517 a day, 0.81 a year) ± 0.0132 a day, ± 0.21 a year, ≈ $1/\sqrt\tau=0.205$ [A20-29]; 0050: 5.68, mean only 1.50 → 2.74 to 8.62 = LM4's 2.7 to 8.6, full 1.53 → 2.68 to 8.68 [A20-30]; [[ex:delta]]; LM11's eigenvalue share and LM22; pitfall: a plug-in SE needs the moments it plugs in (under $\nu<4$ the fourth is infinite); 中文導讀 | 600 |
| 8 | The Hill Estimator of a Tail Index {7} | power tail above $x_0$, conditional (Pareto) density $\alpha x_0^{\alpha}x^{-\alpha-1}$; (20.10) $\hat\alpha=k/\sum\ln(x_i/x_0)$, information $1/\alpha^2$, $\operatorname{SE}=\hat\alpha/\sqrt k$; Hill (1975) takes $x_0$ at an order statistic; E10: at 3%, $k=108$, $\hat\alpha=3.63\pm0.35$, interval 2.9 to 4.3 [A20-33]; at 2%, 4%, 5%: 2.49 (0.16), 4.93 (0.74), 4.76 (1.23) [A20-34]; [[ex:hill]]; LM15's chords (2.09 to 5.03; 4.17) and $\nu=3.065$ beside it; pitfall: the threshold trades bias against variance, and clustered losses make $\hat\alpha/\sqrt k$ too small; 中文導讀 | 420 |
| 9 | Estimation in Python {8} | `ddof` passed explicitly (NumPy 0, Polars 1); `stats.t.fit` and a tighter `minimize(method="Nelder-Mead")`; a central-difference Hessian in NumPy, checked at two step sizes; `stats.t.ppf`; the seed rule; `np.quantile(..., method="inverted_cdf")` for $\hat F^{-1}$; lab box | 180 |
| — | Summary (7) / Problems (12) / Solutions | | 140 / 420 / 520 |
| | **Total** | | **5,475** |

**Elements.** 10 examples (E1 §2; E2, E3 §3; E4 §4; E5, E6 §5; E7 §6; E8, E9 §7; E10 §8). Knowledge checks:

- §2: $\tfrac12\bar R$ has a smaller MSE than $\bar R$ exactly when $\lvert\mu/\sigma\rvert<\sqrt{3/T}$; for one year,
  $\sqrt{3/246}=0.110$ against TR23's daily $\widehat{\mathrm{SR}}=0.0517$ ([[LM19]]'s) [A20-49]: yes, if the model's
  $\mu$ were TR23's.
- §3: three years of daily data with annual volatility 18.96% give an annual-mean SE of 10.9 points; ten years 6.0
  [A20-50]; monthly data over the same years give the same.
- §4: at $T=5{,}849$, does the $t_{T-1}$ quantile change the interval? 1.96037 against 1.95996: not at two decimals
  [A20-16].
- §5: why does the $t$ fit's $\ell$ exceed the normal's by 561.8 [A20-19]? A third parameter, and the normal is the
  $t$ at $\nu\to\infty$; whether a gain exceeds what an extra parameter buys is [[LM21]]'s test.
- §6: with one year of normal days, no unbiased estimator of the annual mean has a standard error below 18.96 points,
  the annual volatility [A20-18].
- §7: the annual Sharpe ratio's standard error after $\tau$ years is about $1/\sqrt\tau$: 0.205 for TR23 [A20-29].
- §8: at 5%, $k=15$ and $\operatorname{SE}=1.23$ [A20-34]: the 95% interval is almost five units wide.
- §9: `pl.col("R").std()` returns 1.208468%, NumPy's `R.std()` 1.208364% [A20-03]: Polars divides by $T-1$.

中文導讀 boxes (terms from `plans/vol-4.md`, English in parentheses at first use in each box): §2 (估計量 (estimator),
抽樣分布 (sampling distribution), 偏誤 (bias), 均方誤差 (mean squared error), 不偏估計量 (unbiased estimator),
一致估計量 (consistent estimator)); §3 (標準誤 (standard error), 樣本變異數 (sample variance); 信賴區間 (confidence
interval) may join here for §4); §5–§6 (概度函數 (likelihood function), 最大概度估計 (maximum likelihood estimation),
費雪訊息 (Fisher information), 觀察訊息矩陣 (observed information matrix), 漸近常態性 (asymptotic normality), 效率
(efficiency), 剖面概度 (profile likelihood), 克萊姆-饒歐下界 (Cramér–Rao lower bound)); §7 (標準誤, delta法 (delta
method)); §8 (希爾估計量 (Hill estimator), 帕累托分布 (Pareto distribution); 尾部指數 (tail index), LM5's and LM15's
printed form, no 樂詞網 entry). Five boxes for eight sections. delta法, 觀察訊息矩陣, 漸近常態性, 效率, 帕累托分布 and
剖面概度 are 樂詞網's statistics forms (SOURCES, "Chinese terms (Volume IV)").

Deep Dives:

- §5, "Maximum likelihood for $\mathcal N_N$" (declares $L$, $\lambda_k$, $M$): for any $\Sigma$,
  $\sum_t(\mathbf R_t-\boldsymbol\mu)^{\top}\Sigma^{-1}(\mathbf R_t-\boldsymbol\mu)=\sum_t(\mathbf R_t-\bar{\mathbf R})^{\top}\Sigma^{-1}(\mathbf R_t-\bar{\mathbf R})+T(\bar{\mathbf R}-\boldsymbol\mu)^{\top}\Sigma^{-1}(\bar{\mathbf R}-\boldsymbol\mu)$,
  so $\hat{\boldsymbol\mu}=\bar{\mathbf R}$. With $\hat\Sigma=LL^{\top}$ ((12.8); needs $\hat\Sigma$ positive definite,
  $T>N$) and $M=L^{\top}\Sigma^{-1}L$, the log-likelihood is
  $-\tfrac T2\big[N\ln2\pi+\ln\det\hat\Sigma+\sum_k(\lambda_k-\ln\lambda_k)\big]$ ($\operatorname{tr}M=\sum\lambda_k$,
  $\det M=\prod\lambda_k$, [[LM11]]); $\lambda-\ln\lambda\ge1$ by (2.1), equality only at 1, so $M=I$ and $\Sigma=\hat\Sigma$,
  divisor $T$. The quadratic-form-as-trace step is one line ($\mathbf x^{\top}M\mathbf x=\operatorname{tr}(M\mathbf x\mathbf x^{\top})$).
- §6, "Why no unbiased estimator beats $1/(T\mathcal I)$": the score has mean 0 (differentiate $\int f_R=1$ under the
  integral, assumed); for unbiased $\hat\theta$, $\Cov(\hat\theta,\ell'(\theta))=1$ (differentiate $\E\hat\theta=\theta$);
  $\lvert\rho\rvert\le1$ ([[LM16]]) gives $1\le\Var(\hat\theta)\,T\mathcal I(\theta)$. Conditions listed (support free of
  $\theta$, differentiation under the integral allowed, $0<\mathcal I<\infty$).

**Exhibits.**

- `case` (table, §1): TR23, daily simple returns, iid. Rows: mean, % a year ($A\bar R$, [[LM19]]'s estimate): 15.38,
  SE 3.89, 7.8 to 23.0, "(20.2)"; volatility, % a year ($\sqrt A\,s$, [[LM19]]'s estimate): 18.96, 0.33, 18.3 to 19.6, "delta method, sample
  kurtosis"; Kelly fraction $\hat f=\bar R/s^2$ (daily): 4.28, 1.11, 2.10 to 6.46, "delta method"; Sharpe ratio a year
  ($r_f=0$, [[LM19]]'s estimate): 0.81, 0.21, 0.40 to 1.22, "delta method, iid"; Student-t degrees of freedom: 3.065,
  0.144, 2.78 to 3.35, "observed information";
  tail index (Hill, the 108 losses of 3% or more): 3.63, 0.35, 2.9 to 4.3, "Pareto information" [A20-08]–[A20-11],
  [A20-20], [A20-23], [A20-28], [A20-29], [A20-33]. Every interval follows from the printed estimate and SE (checked in
  `plans/vol-4-anchors.md`). Note: in-sample; each standard error states its model; Sections 3–8 derive the columns. Source:
  FinMind `TaiwanStockTotalReturnIndex` (TAIEX), retrieved 18 October 2026; Computations: `data/lm20_numbers.py` and
  `LM20_lab.ipynb`.
- `sampling` (two stacked `line` charts with `step` series, §2): experiment 1, 10,000 one-year samples of 246 days from
  a normal model and from a Student-t with LM15's $\nu=3.065$, both with TR23's $\bar R$ and $s$ ((15.11)). Top: x
  annual mean $A\times$(sample mean), bins of 2 points from −60% to +90% (`pct0`), y share per bin; two step series
  "normal model", "Student-t model". Bottom: x annualized volatility $\sqrt A\times$(sample $s$, divisor 246), bins of
  0.25 points from 10% to 40% (`pct1`), the share beyond 40% given in the note. Values: SD of the annual mean 18.9
  (normal, MC SE 0.13) and 18.7 ($t$; 18.6 to 19.2 over experiment 4's 20 further runs), theory 18.96; volatility SD
  0.86 (normal, MC SE 0.006, theory 0.855) and about 4 ($t$; 3.3 to 4.6 over the 20 runs, spread 0.35); 95% ranges
  $\hat F^{-1}(0.025)$ to $\hat F^{-1}(0.975)$: 17.3% to 20.6% (normal) and 14.6% to 26.8% ($t$, median 17.7%)
  [A20-35], [A20-51]. Note: model, not data; seeds and draws printed; batch standard errors of the quantiles 0.01–0.03
  points, 0.3 for the $t$ model's 97.5% point; the $t$ model's two standard deviations get the spread over runs instead
  of a Monte Carlo error, because their fourth moments are infinite. Shows: the mean's spread does not care about the
  tails, the volatility's does.
- `merton` (`line`, `x.type: "log"`, §3): TR23 log returns, non-overlapping $m$-day sums from the first return, $m$ =
  1, 2, 5, 10, 21, 62, 123, 246 sessions as `x.values`; `ticks` [1, 5, 21, 62, 246], `tickLabels` ["1 day", "1 week",
  "1 month", "1 quarter", "1 year"]; y percentage points a year, 0–5 (`n2`). Four series: SE of the annual mean,
  data ($(A/m)\,s_m/\sqrt{T_m}$) and iid model ($\sqrt A\,s_r/\sqrt\tau=3.90$, dashed); SE of the annual volatility,
  data (delta method with each sum's kurtosis) and normal iid model ($\sqrt A\,s_r/\sqrt{2T_m}$, dashed). Values: the
  mean's SE stays between 3.87 and 4.53 at every interval; the volatility's grows from 0.34 (daily) to 4.43 (246-day
  sums), the normal model's from 0.18 to 2.80 [A20-36]. Note: in-sample estimates and model lines; each data point
  rests on one partition (the last $T\bmod m$ returns left out); log returns. Shows Merton's point and the
  syllabus line.
- `years` (`line`, `x.type: "log"`, §4): x years of data $\tau'$ from 1 to 100 (about 50 values), y % a year (`pct1`).
  Band "95% interval" $A\bar R\pm1.96\,\sqrt A\,s/\sqrt{\tau'}$ with TR23's $A\bar R$ and $\sqrt A\,s$ held fixed; line
  "TR23's annual mean, 15.38%"; `hline` 0; dashed `vline` at 23.76 "TR23". Values: −21.8% to 52.5% at one year, 3.6% to
  27.1% at ten, 11.7% to 19.1% at a hundred [A20-37]; 7.8% to 23.0% at 23.76. Note: a model of hypothetical samples
  with TR23's mean and volatility.
- `coverage` (table, §4): experiment 2, 100,000 samples per cell, MC SE 0.07 points at 95%. Rows $T$ = 5, 10, 30,
  100, 246; columns: normal model, $\bar R\pm1.96\,s/\sqrt T$ (simulated; exact $2F_{t_{T-1}}(1.96\sqrt{(T-1)/T})-1$);
  normal model, $t_{T-1}$ interval with $s_{\mathrm u}$; $t_3$ model, both intervals. Values (%, one decimal): 84.5
  (exact 84.6), 95.0, 86.1, 96.4 / 90.4 (90.4), 95.1, 91.5, 96.0 / 93.6 (93.6), 94.9, 94.2, 95.6 / 94.6 (94.6), 95.0,
  94.9, 95.3 / 94.8 (94.8), 95.0, 95.0, 95.2 [A20-17]. Note: model; the exact column uses the $t_{T-1}$ law derived
  in §4 (X32); the $t_3$ draws are built from four normals, as the widget's.
- `fits` (table, §5–§6): TR23 daily returns in %. Rows: normal ($\hat\mu=\bar R$, $\hat\sigma=s$, SEs 0.0158 and 0.0112
  [A20-24]); Student-t, full sample (3.065 (0.144), 0.0997 (0.0124), 0.7761 (0.0138); standard deviation 1.317 (0.045));
  7% limit, 3,077 returns ($\nu$ 2.990 (0.195)); 10% limit, 2,772 returns (3.237 (0.223)) [A20-20], [A20-21], [A20-26];
  log-likelihood gain over the normal, 561.8 [A20-19]; $s$ by regime 1.257 (0.026) and 1.152 (0.035) [A20-39].
  Note: SEs from the observed information (central differences, two step sizes agree); in-sample; regimes a stability
  check; `t.fit` returns $\nu=3.06522$, a tighter search 3.06526 [A20-20], both 3.065; the excess kurtosis gets no
  standard error, because the fitted $\nu<4$ makes the fourth moment infinite.
- `profile` (`line`, §6): x degrees of freedom 2.5–3.8 (step 0.02, `n2`), y log-likelihood minus its maximum
  (`n1`). Series "profile log-likelihood" (location and scale re-maximized at each value) and "quadratic from the
  observed information" (dashed); `hline` −1.92 ($1.96^2/2$, dashed); `point`s at 2.80 and 3.37 (curve) and 2.78 and
  3.35 (parabola) [A20-23]. Shows the curvature as information; the curve is skewed, the parabola symmetric.
- `delta` (table, §7): TR23 and LM4's 0050 sample; standard errors to three decimals (editor's decision, X2), so
  that [[LM22]] can quote them. Rows: annual volatility (TR23: 18.96, SE normal 0.175, plug-in 0.33); Kelly fraction
  $\hat f$ (TR23: 4.28, SE mean only 1.082, normal 1.085, plug-in 1.111, interval 2.10–6.46; 0050: 5.68, 1.50, —,
  1.53, 2.68–8.68; LM4's band 2.74–8.62 from the mean only) [A20-28], [A20-30]; Sharpe ratio (TR23: daily 0.0517, SE
  normal 0.0131, plug-in 0.0132; annual 0.81, SE normal 0.205, plug-in 0.207) [A20-29]. Note: iid; plug-in uses the
  sample's skewness and kurtosis (0050: 0.04 and 11.12); the point estimates 18.96, 0.0517 and 0.81 are [[LM19]]'s;
  LM4's exact band 2.7–7.6 (lm04.md:547) quoted.
- `hill` (`line`, §8): TR23 losses; x threshold $x_0$ from 1.0% to 6.0% in steps of 0.05% (`pct2`), y tail index
  (`n2`). Series "Hill estimate" and band "95% interval" ($\pm1.96\,\hat\alpha/\sqrt k$); dashed `hline` 3.065 "Student-t
  fit"; `point`s at 2%, 3%, 4%, 5% (2.49, 3.63, 4.93, 4.76; $k$ = 252, 108, 44, 15) [A20-33], [A20-34]. Note: $k$ at the four
  marked thresholds (a line chart's tooltip shows no third value), the guard, LM15's chords 2.09–5.03 for comparison; the 7% limit before June 2015 and the 10%
  limit cap the far tail.

Every chart JSON stays far under 300 KB; at most two named series except `merton` (four).

**Widget `coverage` — "How often does a 95% interval cover the mean?"** `Book.controls`: model (select: "Normal",
"Student-t, 3 degrees of freedom"); $T$ (slider 2–250, step 1, initial 10); interval (select: "1.96 with s (divisor
T)", "t quantile with s_u", initial the second); button "Draw again". Each draw: `Book.rng(seed)` (initial seed 1,
plus one per click) generates $n=1{,}000$ samples of $T$ days with TR23's $\bar R=0.0625\%$ and $s=1.2084\%$; a $t_3$
day is $\bar R+s\,Z_0/\sqrt{Z_1^2+Z_2^2+Z_3^2}$ from four normals (variance $s^2$ by (15.10)). Chart (`scatter`): the
first 100 intervals as vertical `lines` (colour 1 when they cover $\bar R$, colour 2 when they miss), `hline` at the true
mean. Readouts: coverage of both intervals over the 1,000 samples with their MC standard error (about 0.7 points); the
$t$ quantile used; for the normal model the exact coverage of the 1.96 interval, $2\,$`Book.dist.tCdf`$(1.96\sqrt{(T-1)/T},T-1)-1$.
Data block `chart-lm20-coverage`: the 97.5% quantiles of $t_{T-1}$ for $T=2,\dots,250$ from SciPy (no `tInv`;
capability D was not approved), checked at $T$ = 5, 10, 20, 30, 100, 250: 2.7764, 2.2622, 2.0930, 2.0452, 1.9842,
1.9695 [A20-38]. Initial state (PDF): normal, $T=10$, $t$ interval, seed 1. The text quotes no widget number.

**Examples** (results recomputed from the printed inputs):

- E1 §2 `scaled`: $\Var(\eta\bar R)=\eta^2\sigma^2/T$, $\operatorname{Bias}=(\eta-1)\mu$; with TR23's $\mu$, $\sigma$ as
  the model's ($\widehat{\mathrm{SR}}=0.0517$, [[LM19]]'s), $\eta^*=0.397$ for one year ($T\mathrm{SR}^2=0.658$) and 0.940 for the
  sample (15.65), and $\operatorname{MSE}(\eta^*\bar R)=\eta^*\sigma^2/T$ [A20-12]. Lesson: a biased estimator can win;
  $\eta^*$ needs $\mu$ (LM24).
- E2 §3 `semean`: $s/\sqrt T=1.2084\%/\sqrt{5{,}849}=0.01580\%$ [A20-13]; $\times A=3.89$ points, the same as
  $18.96\%/\sqrt{23.7645}$ [A20-09]; LM7's 7.36 and 6.09 points follow the same rule (quoted). From five-minute
  returns the estimate $\ln(P_T/P_0)/\tau$ is the same number.
- E3 §3 `divisor`: (20.3); TR23 1.0000855 [A20-03]; 23 annual log returns $s=22.207\%$, $s_{\mathrm u}=22.706\%$,
  factor 1.0225 [A20-15]; U28's 1.000114 (lm10.md:166).
- E4 §4 `interval`: $15.38\%\pm1.96\times3.89$: 7.8% to 23.0%; with $s_{\mathrm u}$ and the $t$ quantile, the same to
  0.01 point [A20-16]; one year: ±37.2 points [A20-18].
- E5 §5 `normalmle`: the derivation; LM5's 0050 $\hat\mu=0.0871\%$, $s=1.2385\%$ (lm05.md:449) are the MLE; TR23's
  $\hat\sigma=1.2084\%$, not 1.2085% ($s_{\mathrm u}$).
- E6 §5 `tmle`: [[ex:fits]]'s Student-t row and regime rows [A20-20], [A20-21], [A20-26]; the gain 561.8 [A20-19].
- E7 §6 `info`: $\mathcal I(\mu)=1/\sigma^2$, $\mathcal I(\sigma)=2/\sigma^2$; SEs 0.0158% and 0.0112% [A20-24]; Cramér–Rao
  attained by $\bar R$; the $t$ location's 0.0124% [A20-25].
- E8 §7 `vol`: $\operatorname{SE}(\sqrt A\,s)=\sqrt A\,s\sqrt{(\operatorname{Kurt}-1)/(4T)}$: 0.33 (Kurt 8.27) and 0.175
  (Kurt 3) [A20-10]; the 23 annual values by the delta method [A20-31] and by the $\chi^2_{22}$ interval of a normal
  model, 17.6% to 32.1% (Blitzstein and Hwang Ex. 10.4.3; SciPy's `stats.chi2.ppf`) [A20-32]; regimes' $s$ 1.257 ± 0.026 and 1.152 ± 0.035 [A20-39] (stability
  check; their difference is LM21's to test).
- E9 §7 `kelly`: (20.9); TR23 and 0050 as in [[ex:delta]] [A20-28]–[A20-30]; the interval is symmetric by
  construction, the true sampling distribution of $\hat f$ need not be ([[LM22]]).
- E10 §8 `hill`: derivation of (20.10) from the conditional density; TR23 at 3% [A20-33] (108 is [[LM13]]'s count);
  2%, 4%, 5% [A20-34].

**Problems plan** (12; MC keys A, C, B, C, B, A; the lab solves 6–11). Stems state the sample (TR23, 3 January 2003 →
8 October 2026, $T=5{,}849$, simple returns unless "log"), the divisor, $A=246.12$, the rounding, the standard-error
method (iid formula, delta method with normal or sample moments, observed information) and, for Problem 11, the seed
and draws. No test, so no null or level beyond "95% interval".

1. MC: ten years of independent daily returns, annual volatility 20%, $A=246.12$; the annual mean's SE from daily
   or from five-minute data (54 a session). **A** 6.32 points either way. B 6.32 daily, 0.86 five-minute (divides by
   $\sqrt{54}$). C 0.40 points ($20\%/\sqrt{2{,}461}$: each day treated as an annual observation) [A20-40].
2. MC: 23 annual log returns; by how much does $s_{\mathrm u}$ exceed $s$? A 4.5% (23/22 − 1, the variance's factor).
   B 0 ("$s$ is unbiased"). **C** 2.2% [A20-41].
3. MC: "7.8% to 23.0% is a 95% interval for TR23's annual mean." A: $\mu$ lies in it with probability 0.95 (a
   posterior statement, LM24). **B**: intervals built this way cover $\mu$ in 95% of samples, if the days are iid.
   C: 95% of future annual returns will fall in it (years vary by about 22 points, [[LM15]]).
4. MC: the MLE of $\sigma$ for the 23 annual log returns under a normal model. A 22.71% ($s_{\mathrm u}$). B 18.56%
   (LM17's daily scaling, another estimator). **C** 22.21% [A20-06], [A20-15].
5. MC: SE of $\sqrt A\,s$ on TR23 for iid normal days (two decimals). A 0.33 (sample kurtosis: not the stated model).
   **B** 0.18. C 0.25 (the 2 forgotten, $\sqrt A\,s/\sqrt T$) [A20-42].
6. Derive $\Var\hat\rho\approx(1-\rho^2)^2/T$ for a normal pair from (16.8) and $\E[X^2Y^2]=1+2\rho^2$; U28 pair
   (price indices, divisor $T$, $T=4{,}382$): $\hat\rho=0.5749$, SE 0.0101, interval 0.555 to 0.595; Python: the
   plug-in delta method ($\operatorname{SE}=\operatorname{sd}(L_t)/\sqrt T$ with
   $L_t=z_{1t}z_{2t}-\tfrac{\hat\rho}2(z_{1t}^2+z_{2t}^2)$, divisor $T$) gives 0.0153 and 0.545 to 0.605, 1.51 times
   wider; why (fat tails, clustering) [A20-43].
7. Python: the Student-t by regime with observed-information SEs (three decimals): 2.990 (0.195), 3.237 (0.223); the
   difference 0.247 has SE 0.296 (independent parts assumed), about 0.8 of its standard errors [A20-44]; why that is
   not yet a test ([[LM21]]).
8. Monthly counts of $\lvert R\rvert\ge3\%$ (guard), 286 calendar months (every month with a session, zero counts
   included): derive the Poisson MLE $\hat\lambda=175/286=0.61189$
   and $\operatorname{SE}=\sqrt{\hat\lambda/286}=0.04625$; the counts' own SD gives 0.0803, $\sqrt{3.0167}=1.737$ times
   larger, [[LM15]]'s overdispersion 3.02 [A20-45]. Lesson: an information-based SE is only as good as the model.
9. TR23's up-day frequency ($R>10^{-12}$): Bernoulli MLE $\hat\theta=3{,}205/5{,}849=0.5480$,
   $\mathcal I(\theta)=1/(\theta(1-\theta))$, SE 0.0065, 95% interval 0.535 to 0.561 (three decimals) [A20-46]; iid
   days assumed (lm17.md:310's promise; LM21 tests $\theta=\tfrac12$ with the same symbol, X5).
10. Hill at 2% and 4% (two decimals): 2.49 (0.16), interval 2.2 to 2.8; 4.93 (0.74), 3.5 to 6.4 [A20-34]; why the
    two intervals barely meet (bias at the low threshold, variance at the high one).
11. Python, experiment 3 (`default_rng([3, 20261011])`, 20,000 normal samples of $T=5$): coverage of $\bar X\pm1.96\,s/\sqrt5$
    (divisor 5) and of the $t_4$ interval: 84.3% (MC SE 0.26) and 94.8% (0.16); exact 84.6% from
    $2F_{t_4}(1.96\sqrt{4/5})-1$ (the $t$ law of §4) [A20-47]; is the gap chance?
12. MC: years of iid data for the annual Sharpe ratio's SE to fall to 0.1 (annual SR 0.5, normal). **A** about 100.
    B 10 (no square). C 384 ($1.96^2/0.1^2$: half-width taken for the SE) [A20-48].

**Lab parts** (`build/make_lab20.py`; reads only `labs/LM20_lab/data/`: `taiex_tr.csv` for TR23;
`0050_daily_raw.csv`, `0050_dividends.csv` and `00631L_daily_raw.csv`, LM4's files, to rebuild the 2,902 common-date
0050 returns as `make_lab04.py` does; `sectors_close_raw.csv` and `sectors_close_repairs.csv`, LM16's, for Problem 6;
`data/make_lab_data.py` builds them from `data/raw/`): 1 data, $T$, $\tau$, $A$, the guard and the `Fraction` check,
`ddof` in NumPy and Polars; 2 [[ex:sampling]] (experiments 1 and 4), E1; 3 E2, E3, [[ex:merton]], [[ex:years]]; 4 E4,
[[ex:coverage]] (experiment 2); 5 E5, E6 with a NumPy central-difference Hessian, [[ex:fits]], [[ex:profile]]; 6 E7–E9,
[[ex:delta]] (0050 rebuilt); 7 E10, [[ex:hill]]; 8 problems 6–11. Extension (stability check): the Kelly fraction and
its delta-method interval in each limit regime. Labs write plain "LM21", never `[[LM21]]`.

**Cross-module tags.**

- (20.1) $\operatorname{MSE}(\hat\theta)=\Var(\hat\theta)+\operatorname{Bias}(\hat\theta)^2$, finite second moment
  (LM24, LM30).
- (20.2) $\operatorname{SE}(\bar R)=\sigma/\sqrt T$, estimated by $s/\sqrt T$; $\operatorname{SE}(A\bar R)=\sqrt A\,\sigma/\sqrt\tau$;
  uncorrelated days with a common mean and variance (LM21, LM22, LM23, LM24, LM30, LM33, LM45).
- (20.3) $\E s^2=\tfrac{T-1}T\sigma^2$, $s_{\mathrm u}^2$ unbiased; same conditions (LM21, LM23).
- (20.4) $\bar R\pm1.96\,s/\sqrt T$ (large $T$, (17.5)); $\bar R\pm F_Y^{-1}(0.975)\,s_{\mathrm u}/\sqrt T$,
  $Y\sim t_{T-1}$, exact for iid normal days (from Blitzstein and Hwang Ex. 7.5.9, Ex. 10.4.3 and Def. 10.4.4, X32)
  (LM21, LM22, LM23, LM24).
- (20.5) normal MLE $\hat\mu=\bar R$, $\hat\sigma=s$; for $\mathcal N_N$, $\bar{\mathbf R}$ and (10.2) when $\hat\Sigma$
  is positive definite (LM23, LM24, LM26, LM30).
- (20.6) $\hat\theta\approx\mathcal N\big(\theta,1/(T\mathcal I(\theta))\big)$; SE from $-\ell''(\hat\theta)$ (or $-H$);
  iid, correct model, interior $\theta$, smooth density, support free of $\theta$, $0<\mathcal I<\infty$ (LM21, LM25,
  LM26).
- (20.7) $\Var\hat\theta\ge1/(T\mathcal I(\theta))$ for unbiased $\hat\theta$, regularity conditions (LM24).
- (20.8) $\Var h(\hat{\boldsymbol\theta})\approx\nabla h^{\top}\Cov(\hat{\boldsymbol\theta})\,\nabla h$; $h$
  differentiable, $\nabla h\ne\mathbf 0$, $\hat{\boldsymbol\theta}$ approximately normal (LM22, LM25, LM26, LM33, LM45).
- (20.9) $T\Var(\hat f)\approx\big[1-2\,\mathrm{SR}\operatorname{Skew}+\mathrm{SR}^2(\operatorname{Kurt}-1)\big]/\sigma^2$,
  $T\Var(\bar R/s)\approx1-\mathrm{SR}\operatorname{Skew}+\tfrac14\mathrm{SR}^2(\operatorname{Kurt}-1)$; iid, finite
  fourth moment (LM22, LM33, LM45).
- (20.10) $\hat\alpha=k/\sum_{i=1}^k\ln(x_i/x_0)$, $\operatorname{SE}=\hat\alpha/\sqrt k$; iid losses with an exact
  power tail beyond $x_0$ (LM32).

**Pitfalls to pre-empt.**

- Conditions every time: iid (or uncorrelated with a common variance), finite moments, the model for an
  information-based SE, regularity for (20.6)–(20.7), a finite fourth moment for any SE of $s$, $\bar R/s^2$ or $\bar R/s$.
- The mean's SE survives volatility clustering when days are uncorrelated ((16.3) with unequal variances still gives
  $\frac1{T^2}\sum\sigma_t^2$); the volatility's does not (fourth moments cluster): say so in E8 and point to LM22.
- Under the $t$ fit ($\nu=3.065<4$) the fourth moment is infinite: the plug-in 0.33 rests on the sample kurtosis and is
  probably too small; the excess kurtosis gets no standard error at all. The same holds for simulation: the $t$
  model's simulated standard deviations get no normal-theory Monte Carlo error, only their spread over experiment 4's
  runs ("about 4").
- Annualizing: the mean's SE scales by $A$ (equivalently $\sqrt A\,\sigma/\sqrt\tau$), not $\sqrt A$; the volatility's and
  the Sharpe ratio's by $\sqrt A$, the latter only with LM19's condition (uncorrelated returns; Lo 2002).
- Return types: the case and the delta method on simple $R$; Merton's sums and the calendar years on log $r$ (3.90
  against 3.89 points for the mean's SE [A20-36], [A20-09]); labelled in every caption.
- Language: "interval", never "significant"; an interval's 95% describes the procedure. No test in this module.
- The $t$ location (0.0997%) is the centre of a symmetric model fitted to skewed data, not the mean (0.0625%); its
  smaller SE is efficiency inside that model only.
- Rounding: print intervals at the precision their printed inputs reproduce (7.8 to 23.0, 18.3 to 19.6, 2.9 to 4.3,
  0.535 to 0.561, 17.6 to 32.1). Every printed form is rounded from the unrounded value and checked at its printed
  precision; the forms within a tenth of a unit of a rounding boundary are flagged in `plans/vol-4-anchors.md` (for
  example 1,381 years, 0.33,
  0.18, 3.63, 0.5480, 23.76).
- `t.fit`'s $\nu$ (3.06522) and a tighter search's (3.06526) differ in the fifth figure; a numerical Hessian is checked at
  two step sizes; scale is not $\sigma$ ((15.11)).
- Mixing samples: TR23 (total return), U28 (price indices, no dividends), LM4's 0050 common dates; never in one statistic.
- Ownership: $\bar R$, $s$, skewness and kurtosis are [[LM14]]'s (and [[LM19]]'s in Volume IV); $A\bar R=15.38\%$,
  $\sqrt A\,s=18.96\%$ and the Sharpe ratio 0.0517 a day, 0.81 a year are [[LM19]]'s (X8); the 23 annual values' 0.22207 [[LM15]]'s; 18.563%
  [[LM17]]'s; the chords [[LM15]]'s; 108 [[LM13]]'s; LM20 owns $\hat f=4.28$, the standard errors, intervals and fits.
- References (SOURCES, sections and theorem numbers only where confirmed): Wasserman (2004) §6.3.1–§6.3.2, §9.3–§9.5,
  §9.7–§9.9 (cited by section only after each is read against the claim, "Open before Stage 2")); Merton (1980), Appendix A
  (read in NBER WP 444; JFE pagination open); Rao (1945, reprint 1992) and Casella and Berger for Cramér–Rao (theorem
  numbers and year unconfirmed: cite the book, not a theorem number, until confirmed); Hill (1975) for the
  conditional-likelihood approach (formula as printed open; the text derives it); Drees, de Haan and Resnick (2000) for
  the Hill plot (author order open); Lo (2002) for the LM33 pointer; [[LM18]] (and its Glasserman 2003, §9.1.2) for
  batch standard errors. Blitzstein and Hwang (2019) as SOURCES records them (X32): Ex. 7.5.9, Ex. 10.4.3 and
  Def. 10.4.4 give (20.4)'s exact form, the coverage table's exact column and Problem 11's exact value through §4's
  one-line derivation (the book does not state the $t_{T-1}$ law of the studentized mean itself, so the text cites the
  three items, not "§10.4"); Ex. 10.4.3 gives E8's $\chi^2_{22}$ interval for $\sigma$ under a normal model of the
  years, whose quantiles come from SciPy (no $\chi^2$ density is needed).
- Notation: $\alpha$ is the tail index, so levels are "95%"; $k$ is Hill's count, not a lag; $\tau$ is years of data;
  no Greek in chart text.

**Stage 4 for earlier modules.**

- `leads` gain 20 in lm01.md:6, lm02.md:6, lm05.md:6, lm07.md:6, lm11.md:6, lm12.md:6 and lm13.md:6, as the plan's
  Stage 4 table lists them with the other modules' additions (lm04, lm10, lm14, lm15, lm16, lm17 and lm18 already list
  20).
- `build/make_lab11.py:571`: the literal `[[LM20]]` becomes the plain text "LM20 and LM22 give the tools; LM22 answers
  it for 2017 and 2020" (plan's Stage 4 list).
- lm15.md:263 ("Independent days scaled by $\sqrt m$ understate the annual spread"): the gap is 1.1 standard errors of
  the 23-value estimate, so "understate" claims a direction the data do not establish. New wording (accepted, plan's
  Stage 4 list): "give a smaller annual spread, a gap that [[LM19]] and [[LM20]] weigh against its sampling error".

**Open before Stage 2** (open in SOURCES; the brief cites only what SOURCES confirms):

- Wasserman §6.3.2, §9.7 and §9.9, read against the claims before the text cites them by section (X34).
- Merton's JFE pagination, Hill's (1975) formula as printed, Casella and Berger's theorem numbers and year, Drees et
  al.'s author order and Rao's 1945 original.

## LM21 Hypothesis Testing and Multiple Testing

Stage 1 brief, revised 2026-10-19 after the cross-check and the independent recomputation. Drafted from the editor's
spine (`plans/vol-4.md` at commit bcfa0d4, "### LM21") and revised to the section "Editor's decisions on the LM19–LM25
drafts (2026-10-19)", the cross-check's findings (X1–X40), the recomputation's items and the fresh check; "Changes in
this revision" lists each. Each number carries its anchor ID at its first appearance; `data/vol4_anchors_lm21.py`
prints all 61 (rows in `plans/vol-4-anchors.md`). Numbers that published modules printed cite their file:line. As
in Volume III's briefs, § counts the Introduction as §1, so §k is the module's Section k−1.

**Prereq:** `[4, 5, 13, 14, 15, 16, 17, 18, 19, 20]`. What each supplies:

- LM4: the 95% interval $\hat\mu\pm1.96$ standard errors, stated without proof, with 1.96 as the 2.5% point of a
  standard normal (lm04.md:541); "Backtests overstate Sharpe ratios ([[LM33]], [[LM34]])" (lm04.md:563).
- LM5: $\varphi$, $\Phi$ (lm05.md:60, 175); (5.5), normal probabilities by standardizing.
- LM13: (13.2) the union bound (lm13.md:97); (13.6) independent events (lm13.md:196); (13.7) "at least once in $n$
  independent trials" (lm13.md:230); the sign table, ex:signs (lm13.md:201–218: 1,226 against 1,195.0, "31 days in
  5,848"); two falls in a row, eg:fallsinarow (lm13.md:161–167: 13 against 2.0); the manager, eg:manager
  (lm13.md:328–336: 8 good months of 12, posterior 13.5%, hypothetical).
- LM14: (14.1) $\E[\mathbf 1_{\mathcal A}]=\Pr(\mathcal A)$ and (14.3) linearity (the expected number of false
  rejections); (14.5) $\operatorname{Skew}$, $\operatorname{Kurt}$ and TR23's printed −0.34 and excess kurtosis 5.27
  (lm14.md:233), for Problem 9 (LM14's printed moments, not LM19's (19.3); cross-check X27).
- LM15: (15.1), (15.2) the binomial; (15.6) $\Phi^{-1}$; (15.9) the $t_\nu$ density; the blocks, eg:updays and the
  pitfall after ex:binom (lm15.md:86–104: variance 4.72 against 4.95 and 5.16, $\rho_1=0.0215$); the limit regimes
  (lm15.md:615).
- LM16: (16.1) the product rule for independent variables; (16.3) the variance of a sum; the $\chi^2_N$ law
  (lm16.md:360–362) and (16.9); ex:pmf and eg:joint (lm16.md:68–88: 347 joint falls, ratio 3.29); eg:outside
  (lm16.md:378–384: 177 days against mean 48.68, SD 6.94); ex:chisq (lm16.md:386–400: S5, 43.8 expected and 291
  found beyond the $\chi^2_5$ 99% quantile); the crash-correlation pitfall (lm16.md:514). All U28 numbers.
- LM17: (17.1); (17.5) the central limit theorem and its conditions; the normal approximation to a binomial count
  with the continuity correction (lm17.md:288–292).
- LM18: (18.2), the standard error of a simulated mean (here of a share); the batch standard error (lm18.md:153) for
  E10's standard deviation; the seed rule and "reproduce against replicate" (lm18.md:70–72).
- LM19 (brief): (19.1) $s_{\mathrm u}$; the sample autocorrelation $\hat\rho_k$ and (19.6), its iid band
  $\pm1.96/\sqrt T$, read here as "$\sqrt T\hat\rho_k$ is approximately standard normal for iid days"; TR23's $\bar R$,
  $s$ and Sharpe ratio, 0.0517 a day and 0.81 a year on $R$ with $r_f=0$, annualized by $\sqrt A$ only for
  uncorrelated returns (Lo 2002), which LM19 owns and LM21 cites; TR23's next-day log returns correlate 0.039
  (lm17.md:392, LM17's figure, LM19's statistic).
- LM20 (brief): (20.2) $\operatorname{SE}(\bar R)=\sigma/\sqrt T$, estimated by $s/\sqrt T$ (0.01580% a day, A20-13);
  (20.3) $s_{\mathrm u}^2$ unbiased; (20.4) the 95% interval, for the annual mean 7.8% to 23.0% a year (A20-09), and
  $t_{T-1}$ for a normal model; (20.6), whose normal information gives the standard error of a sample variance,
  $\sigma^2\sqrt{2/n}$ for nearly normal data (Problem 7; in general it depends on the kurtosis). LM20 owns
  every standard error and interval that LM21 quotes.

**Leads:** `[22, 23, 24, 25, 26, 33, 34]`: the expected tag users and the pointer targets (LM22 bootstraps (21.1)
and (21.2) and sets its regime test beside LM21's 0.041; LM23 applies (21.1) and (21.6)–(21.8) to the 28 alphas; LM24
sets a posterior probability beside (21.2) and cites the t-stat 3.955678; LM25 and LM26 report p-values by (21.2);
LM33 cites (21.4) and (21.9); LM34 cites (21.6) and (21.9)). The cross-check confirmed the list.

**Forward links honoured.** Rechecked by `grep -n "LM21"` over `src/lm*.md`, `src/lm*.js`, `src/pages/*.md`,
`build/make_lab*.py` and `src/syllabus.yaml`: the spine missed none. The syllabus line is added as a promise.

| Earlier text | Promise | Kept in |
|:--|:--|:--|
| lm13.md:59 | "[[LM21]] asks whether a gap is larger than chance" | §5: E6, E7, X4 |
| lm13.md:218 | 1,226 against 1,195.0, "31 days in 5,848": "a question for the tests of [[LM21]]" | §5: E6, $\chi^2=2.69$, $p=0.10$ |
| lm13.md:536 | "Even independent signs would show some gap … [[LM21]] asks whether this one is larger than chance" | §5: E6 (the null law of the gap); E7 |
| `make_lab13.py:463` | shares of falls after big moves, by regime: "LM21 asks whether such gaps exceed chance" | §5: E7 tests the same kind of gap (falls after falls); lab part 4 points back |
| lm15.md:62 | "[[LM20]] and [[LM21]] add standard errors and tests" | throughout; the hygiene note |
| lm15.md:104 | blocks' variance 4.72 against 5.16 and 4.95: "[[LM21]] tests such gaps" | Problem 7: $z=-0.56$ and $-1.03$ |
| lm15.md:615 | the regimes: "no standard error says whether a change exceeds chance ([[LM20]], [[LM21]])" | §3: E4 (the means, two-sample $z=1.08$); one sentence: variance and kurtosis changes need LM20's standard errors, and clustering LM22's blocks |
| lm16.md:62 | "whether gaps could be chance is [[LM21]]'s and [[LM22]]'s question" | §5: the count test of eg:outside with its caveat; the intervals are LM22's |
| lm16.md:88 | the ratio 3.29, "a descriptive ratio, not evidence ([[LM21]])" | Problem 8: $\chi^2=784$ from LM16's printed U28 counts collapsed to 2×2 (recounted on U28, A21-61) |
| lm16.md:369 | "[[LM21]] builds tests on [$\chi^2_N$]" | §5: (21.5) on $\chi^2_1$; LM16's S5 counts read as 4,382 tests on $\chi^2_5$; Problem 9 on $\chi^2_2$ |
| lm16.md:384 | 177 days against 48.68 (SD 6.94): "[[LM21]]'s question" | §5: $z=18.5$ from LM16's printed U28 counts, under a binomial null that assumes independent days; clustering widens the spread by (16.3) |
| lm16.md:430 | 中文導讀: "這個差距是否可能出於偶然，留待 [[LM21]]" | §5 as above |
| lm16.md:514 | 0.788 against 0.860: "for [[LM21]] and [[LM22]]" | §5, one sentence: a test needs the sampling law of a conditional correlation, which LM22's block bootstrap estimates |
| `make_lab16.py:571` | regime correlations 0.6544, 0.5564; 93 and 84 days beyond radius 3: "draw no conclusion about chance from it (LM21, LM22)" | §5 pitfall: a two-proportion test would treat days as independent; LM22 |
| research-hygiene.md:7 | 更完整的處理在 [[LM21]]、[[LM33]] 和 [[LM34]] | §6–§8 |
| research-hygiene.md:29 | "The more versions you try … [[LM21]] and [[LM33]] measure that risk" | §6–§8: FWER, FDR, (21.9) |
| research-hygiene.md:62 | "[[LM21]] covers multiple testing" | §6, §7 |
| syllabus.yaml:62 | "p-values, power, Bonferroni and FDR; the t > 3 hurdle for strategies." | §2–§8 |

**Outcomes** ("After this module you should be able to:"):

1. state a null and an alternative hypothesis, and compute a test statistic, its p-value and the decision at a given level, naming the type I and type II errors
2. apply the one-sample t-test to a mean return and the two-sample test to two periods or groups of days, state their conditions, and relate a test to a confidence interval
3. calculate the power of a test of a mean and the years of data needed to detect a given annual Sharpe ratio
4. test a frequency against a binomial model and the independence of a 2×2 table with the $\chi^2$ test, and explain what dependence between days does to both tests
5. compute the family-wise error rate and the expected number of false rejections in a family of tests, and apply the Bonferroni correction
6. apply Holm's procedure and the Benjamini–Hochberg procedure, and state which error each controls and under which condition
7. explain why the largest t-stat of a search grows with the number of strategies tried, and interpret the t > 3 hurdle
8. run these tests in Python by hand and with SciPy and statsmodels, checking each function's defaults

**Owns.** Null and alternative hypotheses (one- and two-sided, fixed before the data); test statistic, null law,
rejection region, level and size (a discrete test's size below its level), p-value (21.2) and its uniform law under a
continuous null; type I and II errors and power. The one-sample t-test (21.1) with the normal and the $t_{T-1}$
reference, and its duality with LM20's interval. The two-sample statistic with unpooled variances (21.3) (SciPy's
`ttest_ind(..., equal_var=False)`; no paper is cited for it). Power and sample size (21.4): the t-stat as the annual
Sharpe ratio times $\sqrt\tau$, the years for 80% power. Tests of a frequency: exact binomial and normal
approximation, $\theta$ under test. The $\chi^2$ test of a 2×2 table (21.5), $\chi^2=n\hat\rho^2$, with the caveat
that clustered days break its null law. Multiple testing: the family-wise error rate (FWER) and the expected number of
false rejections (21.6); Bonferroni from (13.2); Holm (21.7); the false discovery rate (FDR) and Benjamini–Hochberg
(21.8), independence stated, Benjamini–Yekutieli in one sentence; the largest of $m$ null t-stats (21.9); the t > 3
hurdle. On TR23 it owns: the t-stats of the mean (full sample, 3.955678 with $s_{\mathrm u}$, which LM24 cites; the
regimes) and their two-sample comparison; the up-day test; the $\chi^2$ test of LM13's sign table and the
falls-after-falls test; the calendar family of 17 tests under each rule, its shuffled-date null (*Model*; LM22 adds a
sentence connecting it to permutation and bootstrap tests) and Wednesday's stability check; the search over 10,000
random long–short rules. The rule "report how many tests ran on the same data" (Research hygiene). It quotes and does
not own: $\bar R$, $s$ and the Sharpe ratio ([[LM19]]); $\operatorname{SE}(\bar R)$ and the interval for the mean
([[LM20]]); LM16's U28 counts, from which §5 and Problem 8 compute statistics labelled "from LM16's printed U28
counts".

**Leaves.**

- Bootstrap tests, tests under dependence, the intervals of LM16's count and crash correlation and of LM16's lab's
  regime gaps → LM22.
- Regression t and F tests; the 28 sector alphas under (21.6)–(21.8); HAC standard errors for autocorrelated returns
  → LM23.
- The probability of a hypothesis given the data → LM24.
- The robust autocorrelation and variance-ratio tests, Ljung–Box, the unit-root tests → LM25.
- ARCH tests and models of the clustering that §5 detects → LM26 (which cites E7's 13 against 2.0).
- Tests of a Sharpe ratio under non-iid returns, the Probabilistic and Deflated Sharpe ratios, the minimum track
  record → LM33.
- Backtest overfitting: White's (2000) reality check, Romano and Wolf's (2005) stepwise tests, PBO, testing the best
  rule on later data → LM34 (named in §8).
- Not in the book (a sentence each): the likelihood-ratio test and the Neyman–Pearson lemma; the theory of
  permutation tests (E8's shuffle is used only as a simulated null).

**Uses before taught** (one sentence each in the text):

- §2 pitfall: "A p-value is not the probability that $H_0$ is true; [[LM24]] computes such a probability, as
  [[LM13]] did for the manager."
- §3: "[[LM20]] derives $\operatorname{SE}(\bar R)=\sigma/\sqrt T$, (20.2), and the 95% interval (20.4); this
  section tests the value that interval estimates."
- §3: "Autocorrelated returns change $\Var\bar R$ by (16.3); [[LM19]] measures TR23's autocorrelations, and
  [[LM23]]'s HAC errors correct for them."
- §4: "[[LM19]] annualizes a daily Sharpe ratio by $\sqrt A$, which needs uncorrelated returns (Lo 2002)."
- §4: "[[LM20]] shows that sampling more often does not shrink the standard error of a mean (Merton 1980)."
- §5: "Under independent days $\sqrt T\hat\rho_k$ is approximately standard normal; this is [[LM19]]'s band (19.6)."
- §5: "[[LM22]] resamples blocks of days to measure how clustering widens a count's spread, and gives the interval for
  [[LM16]]'s crash correlation."
- §5: "[[LM26]] models the clustering that makes falls follow falls."
- §7: "[[LM23]] applies these corrections to 28 sector alphas."
- §8: "[[LM33]] deflates a Sharpe ratio for the number of trials, and [[LM34]] tests the best rule of a search on
  later data (White 2000; Romano and Wolf 2005)."
- Problem 7: "[[LM20]]'s standard error of a variance, $\sigma^2\sqrt{2/n}$ for nearly normal data."

**Data role.** TR23 for every test, from `data/processed/vol3_taiex.parquet` (`data/vol3_series.py`; FinMind
`TaiwanStockTotalReturnIndex`, data_id TAIEX, retrieved 2026-10-18): 5,850 closes, 2003-01-02 → 2026-10-08 [A21-01];
$T=5{,}849$ simple returns $R_t=P_t/P_{t-1}-1$ from 2003-01-03 [A21-02]; 8,680 calendar days, 23.7645 years
[A21-03]; $A=246.12$ [A21-04], used only to annualize a Sharpe ratio. Return type: simple daily returns throughout
(no sums over days, so no log returns). Divisors: $s$ with $T$ (the Sharpe ratio, $r_f=0$, and every printed
"standard deviation"), $s_{\mathrm u}$ with $T-1$ (every t-stat); `ddof` passed explicitly. Subsamples, each named in
its caption: the limit regimes by return date, 3,077 returns to 2015-05-29 and 2,772 from 2015-06-01 [A21-05]; LM13's
pair space of 5,848 pairs and LM15's 292 blocks of 20 sessions (the first 5,840 returns) [A21-06]; the calendar
family by the return's date, weekdays Monday 1,151, Tuesday 1,181, Wednesday 1,183, Thursday 1,168, Friday 1,143 and
23 Saturday sessions [A21-07], months from 369 (February) to 532 (March) [A21-08]. The 23 Saturday sessions
(2006-10-14 to 2018-12-22, listed in A21-07) belong to no weekday and to every "rest" (the editor's decision); the text
calls them "Saturday sessions" and says that TWSE's history page states that the market stopped trading on Saturday
make-up workdays from 2019 (SOURCES, "Taiwan facts (Volume IV)"); that the 23 sessions were such days is an
inference, written as one. Cleaning: none
beyond `vol3_series.py`; no return is exactly 0 (`Fraction` on the two-decimal closes: 3,205 up, 2,644 down
[A21-09]). Counts against a threshold use the guard (`R > 1e-12`, `R <= -0.03 + 1e-12`) and are checked exactly with
`Fraction`; constructed p-values are compared with `Fraction`. Seeds (AUTHORING §8): experiment 8 (E8: 10,000
shuffles, each `R[permutation(T)]` placed on TR23's dates in their order, so every month and weekday keeps its dates
and size), 10 (E10 and X7: 10,000 random long–short rules, positions drawn in one call
`integers(0, 2, size=(10000, T), dtype=np.int8)`, processed in 20 chunks of 500), 11 (Problem 11, 10,000 families of
17 normal statistics), each `np.random.default_rng([e, 20261011])` created once. Monte Carlo errors: a share by
(18.2) on indicators, a mean by (18.2), and E10's standard deviation (divisor 10,000) by [[LM18]]'s batch standard
error over the 20 chunks. U28 is loaded only to recount LM16's printed counts (A21-61: 859, 538, 347, 177 and 291
reproduce); no TX23 or T5S data. Scripts: `data/lm21_numbers.py` (after `data/vol3_series.py` and
`data/vol2_series.py`; asserts every printed value and LM16's counts on U28, recounts with `Fraction`, flags values
near a rounding boundary, compares with the anchors), `data/lm21_charts.py` (X2, X3, X5, X6, X7); `build.sh`
`DATA_STEPS` gains both, and `data/make_lab_data.py` gains `"LM21_lab": {**tr23}` (lab file `taiex_tr.csv`). Published
files (the editor's rule on daily series): no chart, widget or other published file carries a daily series. X5 and X6
hold 17 statistics, X7 eleven record points and model curves, X2, X3 and the widget model curves only; the lab's
`taiex_tr.csv` is built locally and never published.

**Hygiene declaration.** *In-sample:* every test on TR23 (E2–E4, E6–E8, the regimes, Problems 7 and 9): each runs
on the data that suggested it. The module runs 29 tests on TR23 [A21-58] and says so beside the calendar family. *Stability check:* the two limit regimes (X1, E4) and Wednesday in each (E8). *Model:* the
null laws (X2), the power curves and years (X3, E5, KC §4), the shuffled-date null (E8), the maximum of $m$ null
statistics and the random rules (X7, E10), the widget, Problem 11, the knowledge checks of §4, §6 and §8.
*Hypothetical:* LM13's manager (E1, Problem 6). *Constructed:* E9's p-values, the knowledge checks of §2, §3, §5, §7
and §9, Problems 1–5. *Quoted:* LM16's U28 counts (descriptive in LM16; §5's $z$ and Problem 8's $\chi^2$ are
in-sample on U28, computed from LM16's printed counts). Local note: "Every test here is in-sample: it runs on TR23,
3 January 2003 to 8 October 2026 (5,849 daily returns), the data that suggested it, and the module runs 29 tests on it
(the lab lists them). Count the tests before you read any single p-value. Comparing the two limit regimes is a
stability check. Null laws, power curves, shuffled dates and simulated searches are model results. The manager is
hypothetical ([[LM13]]); LM16's counts are U28's, as printed. Nothing is tested on later data ([[LM34]])."

**Notation.** AUTHORING §6 with its Volume IV table. Used: $R$, $\mu$, $\sigma$, $\bar R$, $s$, $s_{\mathrm u}$,
$T$, $t$ (date index), $A$, $\tau$ (years of data, $T=A\tau$), $\mathrm{SR}$ (annual, $r_f=0$), $\varphi$, $\Phi$,
$\Phi^{-1}$, $\Pr$, $\E$, $\Var$, $Z$, $X$, $\mathcal N$, $t_\nu$, $\chi^2_N$, $\operatorname{Bin}(n,\theta)$, iid,
$n$, $\mathcal A_i$, $\mathbf 1\{\cdot\}$, $\operatorname{SE}$, $\operatorname{Skew}$, $\operatorname{Kurt}$, $f$,
and the LM21 rows of the Volume IV table: $\theta$ (a binomial probability under test), $H_0$, $H_1$,
$\text{t-stat}$, $\alpha$ (the significance level), $p_i$, $p_{(i)}$, $m$, $q$. Local:

| Symbol | Meaning | Check |
|:--|:--|:--|
| $\theta_0$, $\hat\theta$ | null value of $\theta$; the sample frequency | subscript, hat (LM24's $\alpha_0$, $\beta_0$ are not used) |
| $\mu_{\text{null}}$ | the value of $\mu$ under $H_0$ in (21.1) | $\mu_0$ is LM24's prior mean |
| $\bar R_1$, $\bar R_2$; $s_{\mathrm u,1}$, $s_{\mathrm u,2}$; $T_1$, $T_2$ | the two groups of (21.3) | subscripts |
| $n_{11}$, $n_{12}$, $n_{21}$, $n_{22}$; $n_{1\cdot}$, $n_{\cdot1}$ | cells and margins of a 2×2 table (row 1: yesterday down; column 1: today down) | digit indices |
| $\hat\rho$ | correlation of the table's two indicators over its $n$ pairs ([[LM15]]'s $\rho_1$ for TR23's signs) | sample correlation, §6 |
| $m_0$ | number of true null hypotheses among the $m$ | subscripted count |
| $i$ | test index and rank, $i=1,\dots,m$ | index |
| $i_{\mathrm H}$, $i_{\mathrm{BH}}$ | numbers of hypotheses Holm and Benjamini–Hochberg reject | subscripted |
| $Z_1,\dots,Z_m$ | independent standard normal statistics of a model family, (21.9) | §6's $Z$ |
| $f_{i,t}$ | position of random rule $i$ on day $t$, $\pm1$ (long or short one unit) | §6's $f$, an exposure; not LM20's $\hat f$ |

Clashes avoided: the probability of a type II error is written in words and power as "power" (no $\beta$, which is a
regression slope); critical values are written $\Phi^{-1}(1-\alpha/2)$ (no $z_\alpha$, since $z$ is a value of $Z$);
the phi coefficient is $\hat\rho$ ($\varphi$ is the normal density); no $k$ (a lag in Volume IV); no $p$ without a
subscript (no bets); $V$ and $R$ for the false and total rejections of the FDR are replaced by words; $P$, $R^2$, a
star for anything but an optimum, $\mu_0$ and $\beta$ are not used.

**Motivating case: "The best day to own the TAIEX."** (box, about 125 words)

> From 3 January 2003 to 8 October 2026 the TAIEX total-return index, with dividends reinvested and no costs, gained
> 0.0625% on an average day [A21-10]. Single days varied far more, with a standard deviation of 1.21% [A21-11]. Is the
> mean really positive? It lies 3.96 standard errors above zero [A21-12]: 2.05 before the daily price limit widened
> in June 2015 and 3.68 after it [A21-13]. Now sort the same 5,849 days by calendar month and by weekday, 17 groups in
> all. Wednesdays stand out. They averaged 0.1332%, against 0.0446% on the other days [A21-14], a gap of 2.36 standard
> errors with a p-value of 0.018, well below the usual 5%. Should an investor own the TAIEX only on Wednesdays?

Resolved: (a) the mean: §3, E3 ($p=7.6\times10^{-5}$ [A21-16], past the t > 3 hurdle), E4 (the regimes do not
differ: 1.08 [A21-18]); (b) Wednesday: §6–§7, E8 (one of 17 tests; 0.85 false rejections expected [A21-29], an
adjusted p-value of 0.31 [A21-30]; 2.06 before June 2015 and 1.25 after [A21-33]), X5, X6, E9 (no rule rejects
[A21-32]); (c) why searching finds such days: §8, E10, X7. Wednesday is the extreme of the 17 tests, said in the box's
resolution; February (0.1405% a day) and December (0.1270%) have the highest monthly means [A21-15]. The box's mean
and standard deviation are [[LM19]]'s statistics ($s$, divisor $T$); the t-stats are LM21's.

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | a positive mean, and days that look special; case + X1; roadmap; notation and hygiene notes | 380 |
| 2 | What a Test Decides {1} | small case first: LM13's manager, 8 of 12 under $\theta=\tfrac12$ (E1); $H_0$, $H_1$ fixed in advance, one- or two-sided; statistic, null law, rejection region, level, size; p-value (21.2) and why it is uniform under a continuous null; the 2×2 of decisions and truths: type I and II errors, power; E1's 4% power [A21-46]; E2 (up days, $\theta_0=\tfrac12$, exact binomial (15.1) and normal (17.5)); pitfall: a p-value is not $\Pr(H_0)$, and "not rejected" is not "true" | 600 |
| 3 | Testing a Mean Return {2} | (21.1) with conditions (iid, finite variance, large $T$: approximately $\mathcal N(0,1)$ by (17.5) and LM20; exactly $t_{T-1}$ for iid normal returns, in one line: by Blitzstein and Hwang's Ex. 7.5.9 $\bar R$ and $s_{\mathrm u}^2$ are independent, by Ex. 10.4.3 $V=(T-1)s_{\mathrm u}^2/\sigma^2\sim\chi^2_{T-1}$, so with $Z=\sqrt T(\bar R-\mu)/\sigma$ Def. 10.4.4 makes $Z/\sqrt{V/(T-1)}$, the t-stat at $\mu_{\text{null}}=\mu$, a $t_{T-1}$ variable (as [[LM20]]'s (20.4)); X2; E3 (TR23); duality with LM20's interval (20.4); uncorrelated is enough for $\Var\bar R=\sigma^2/T$ ((16.3)), autocorrelation is not (LM19, LM23); (21.3), the two-sample statistic with unpooled variances, and its conditions; E4 (the regimes); pitfall: significant in one period and not in the other is not a significant difference | 650 |
| 4 | Power and the Years a Sharpe Ratio Needs {3} | power as a function of the true mean; under $H_1$ the t-stat is approximately $\mathcal N(\mathrm{SR}\sqrt\tau,1)$, since $\bar R/s\cdot\sqrt T=\mathrm{SR}\sqrt\tau$; (21.4) from (5.5); X3; E5; TR23's 3.956 as $0.8115\times\sqrt{23.7645}$, with LM19's 0.81 [A21-19]; pitfall: more frequent data do not help (LM20) | 480 |
| 5 | Testing Frequencies and Independence {4} | LM13's sign table (X4); (21.5) with the Deep Dive; the null law $\chi^2_1$ through LM19's (19.6) and LM16's definition (one series on consecutive days; for two series *stated without proof*); E6; E7 (falls after falls); what clustering does: (16.3) with positive covariances widens a count's spread; LM16's 177 days ($z=18.5$ from LM16's printed U28 counts [A21-26]) and its S5 days as 4,382 tests on $\chi^2_5$ at 1% (43.8 rejections expected, 291 found [A21-27]); LM16's crash correlation and lab gaps → LM22; pitfall: two-proportion tests on clustered days | 600 |
| 6 | Many Tests at Once {5} | the calendar family defined before looking (12 months, 5 weekdays, each against the rest); X5; one rejection against $17\times0.05=0.85$ expected ((14.1), (14.3)); FWER $1-0.95^{17}=0.58$ [A21-29] for independent tests ((13.7)); E8 (shuffled dates; Bonferroni and Šidák adjustments; Wednesday by regime); Bonferroni from (13.2), (21.6); the 29 tests of this module | 550 |
| 7 | Holm and the False Discovery Rate {6} | Holm's step-down rule (21.7) and its Deep Dive; FDR defined in words; Benjamini–Hochberg (21.8), independence stated (BH 1995), equal to the FWER when every null is true; Benjamini–Yekutieli in one sentence; E9 (constructed: 1, 3, 5 rejections [A21-47]); X6 (the calendar: none); pitfall: choosing the rule after seeing the p-values | 550 |
| 8 | Searching Many Strategies: the Hurdle of 3 {7} | (21.9) from (16.1); medians of the maximum; X7; E10 (10,000 random rules on TR23, with Monte Carlo errors); Harvey, Liu and Zhu's "t-statistic greater than 3.0"; $\lvert t\rvert=3$ as Bonferroni for about 18.5 tests [A21-34]; LM4's warning; LM33, LM34 (White 2000, Romano and Wolf 2005); widget | 460 |
| 9 | Tests in Python {8} | the t-stat by hand against `stats.t.sf` and `stats.norm.sf`; `stats.binom.sf`, `stats.chi2.sf`; `multipletests` with `method` always given (its default is Holm–Šidák); `stats.false_discovery_control`; SciPy's test functions and their defaults (`ttest_ind`'s `equal_var=True`, `chi2_contingency`'s Yates correction, `jarque_bera`'s divisor-$T$ moments; SOURCES, "SciPy 1.18 (Stage 1 check)"); lab box | 170 |
| — | Summary (7) / Problems (11) / Solutions | | 120 / 380 / 460 |
| | **Total** | | **5,400** |

**Elements.** 10 examples (E1, E2 §2; E3, E4 §3; E5 §4; E6, E7 §5; E8 §6; E9 §7; E10 §8). Knowledge checks:

- §2: 60 up days in 100 sessions under $\theta_0=\tfrac12$: $z=2.00$, two-sided $p=0.0455$ [A21-38]; reject at 5%,
  not at 1%.
- §3: a strategy with mean 0.04% and $s_{\mathrm u}=1\%$ a day over 900 days has t-stat 1.20; the same edge needs
  2,500 days for a t-stat of 2 [A21-39].
- §4: at an annual Sharpe ratio of 0.5, ten years give power 0.35 at the 5% level; a t-stat of 3 needs 9 years at
  $\mathrm{SR}=1$ and 36 at 0.5 [A21-40].
- §5: with $n=10{,}000$ pairs, $\chi^2>3.84$ needs $\lvert\hat\rho\rvert>0.0196$, that is $1.96/\sqrt n$ [A21-41].
- §6: 100 independent tests of true nulls at 5%: 5 false rejections expected; at least one with probability 0.994
  [A21-42].
- §7: p-values 0.004, 0.012, 0.03 at 5%: Bonferroni rejects 2, Holm 3, Benjamini–Hochberg 3 [A21-43].
- §8: how many null rules give an even chance that the best has t > 3? $m=\ln0.5/\ln\Phi(3)=513.1$, so 514 [A21-44].
- §9: a t-stat of 2 with $T=30$: $t_{29}$ gives 0.055, the normal 0.0455 [A21-45]; at $T=5{,}849$ E3's two p-values
  differ by about 1% ($7.6$ and $7.7\times10^{-5}$, A21-16).

中文導讀 in §2 (假設檢定, 虛無假設, 對立假設, 顯著水準, p值, 第一型錯誤, 第二型錯誤; the intuition: a test asks how
surprising the data would be if nothing were there), §4 (檢定力, 標準誤: why 23.8 years are short for a Sharpe ratio
of 0.5), §6 (多重假設檢定 (multiple testing), 族系誤差率, Bonferroni 校正: 17 tries at 5% find something 58% of the
time), §7 (偽發現率: controlling the share of false discoveries instead of any false discovery) and §8 (資料偵伺:
the best of many null rules). Terms from `plans/vol-4.md` "Chinese terms" and the Volume III list (二項分布, 卡方分布,
常態逼近, t 分布, 自由度, 信賴區間, 獨立同分布); English in parentheses at first use in each box. The spacing of
"Bonferroni 校正" follows the editor's choice (SOURCES, Chinese terms (Volume IV), last item). No term outside these
lists is needed.

Deep Dives: §5 "Why the 2×2 $\chi^2$ is $n\hat\rho^2$": with the margins fixed, every cell's observed minus expected
count is $\pm D/n$ with $D=n_{11}n_{22}-n_{12}n_{21}$, and the four $1/\text{expected}$ sum to
$n^3/(n_{1\cdot}n_{2\cdot}n_{\cdot1}n_{\cdot2})$, so $\chi^2=nD^2/(n_{1\cdot}n_{2\cdot}n_{\cdot1}n_{\cdot2})=n\hat\rho^2$
(algebra, checked numerically in A21-23). §7 "Why Holm controls the family-wise error rate": if any true null is
rejected, the first one rejected is reached at a step $j\le m-m_0+1$, so the smallest true-null p-value is at most
$\alpha/m_0$; by (13.2) that event has probability at most $m_0\cdot\alpha/m_0=\alpha$, under any dependence (Holm
1979 for the result).

**Exhibits.**

- X1 `case` (table, §1): TR23's mean and its tests. Rows: all days; before 2015-06-01; from 2015-06-01; Wednesdays
  minus other days. Columns: days; mean (% a day, four decimals); $s_{\mathrm u}$ (% a day, four decimals); t-stat
  (three decimals); p-value (two-sided, normal). Values: 5,849, 0.0625, 1.2085, 3.956, $7.6\times10^{-5}$
  [A21-10–A21-12, A21-16]; 3,077, 0.0464, 1.2572, 2.046, 0.041; 2,772, 0.0804, 1.1519, 3.675, 0.00024 [A21-13];
  1,183 against 4,666, difference 0.0886 (SE 0.0375), 2.363, 0.018 [A21-14]. Note: standard errors are
  $s_{\mathrm u}/\sqrt{\text{days}}$, the iid formula of [[LM20]]'s (20.2): 0.0158, 0.0227 and 0.0219% a day; t-stats
  from unrounded inputs (the four-decimal means and $s_{\mathrm u}$ give 3.955, 2.047, 3.675 [A21-60]); the last row is
  the two-sample statistic (21.3), the others (21.1) with $\mu_{\text{null}}=0$; the mean of all days is [[LM19]]'s;
  29 tests run on TR23 in this module. Source: FinMind `TaiwanStockTotalReturnIndex` (TAIEX), retrieved 2026-10-18;
  Computations: `data/lm21_numbers.py`.
- X2 `nulldist` (`line`, §3): x from −5 to 5 (`fmt: "n2"`, `tfmt: "n0"`); y density 0–0.42 (`n3`). Series: the
  standard normal density "null law of the t-stat"; one band "rejection region, two-sided 5%" with `lo` 0 and `hi`
  $\varphi(x)$ for $\lvert x\rvert\ge1.959964$, `null` between (two runs, one legend entry). `vline`s: ±1.96 (dashed),
  3.96 "all days", 2.05 and 3.68 (dashed) "before / from June 2015". Note: $t_{5848}$'s density differs from
  $\varphi$ by at most $2.3\times10^{-5}$ on $[-5,5]$, and its 97.5% point is 1.9604 against 1.9600 [A21-59], so it
  is not drawn; Model (the null law), the marked statistics in-sample.
- X3 `power` (`line`, §4): x log, years of data $\tau$ from 1 to 200 (`fmt: "n1"`); y power 0–1 (`pct0`). Four
  series on a log grid of about 230 points: $\mathrm{SR}=1$, 0.81 (TR23), 0.5, 0.25, each
  $\Phi(\mathrm{SR}\sqrt\tau-1.959964)+\Phi(-\mathrm{SR}\sqrt\tau-1.959964)$. Dashed `hline` 0.8 "80% power"; dashed
  `vline` 23.76 "TR23's span". `point`s at 80%: 7.85, 11.9, 31.4, 125.6 years [A21-20]; at 23.76 years: 0.998, 0.977,
  0.68, 0.23 [A21-21]. Note: model; iid returns, $\sigma$ known, two-sided 5%; annual SR $=\sqrt A\,\bar R/s$ with
  $A=246.12$ and $r_f=0$; TR23's 0.81 is [[LM19]]'s, in-sample [A21-19].
- X4 `independence` (table, §5): two tests on LM13's 5,848 day pairs. Row 1, down after down: observed 1,226,
  expected 1,194.95 (LM13 printed 1,195.0, lm13.md:212), $\chi^2=2.69$, $p=0.10$ ($\chi^2_1$) [A21-23]. Row 2, a fall
  of 3% or more after a fall: 108 trials, observed 13, expected 2.0, $p=1.2\times10^{-7}$ (exact binomial,
  one-sided) [A21-25]. Note: expected counts keep both days' margins ((13.6)) and are exact fractions; the binomial
  uses $\theta_0=108/5{,}848$; both null laws assume independent days, which row 2 rejects.
- X5 `calendar` (`bar`, §6): 17 categories, Jan–Dec then Mon–Fri; one series, the two-sample statistic (21.3) of
  each group against all other TR23 days (`fmt: "n2"`); y −3.2 to 3.2; `hline`s ±1.96 "5% level, one test" and
  ±2.97 "Bonferroni, 17 tests" [A21-29]. Values [A21-28]: −0.32, 1.33, −1.04, 0.59, 0.51, −0.15, 1.00, −0.50, −1.13,
  −1.10, −0.34, 1.53; −1.05, −0.10, 2.36, −0.63, −0.42. Note: group sizes (A21-07, A21-08); the 23 Saturday sessions
  are in every "rest"; normal p-values; July, August and December lie within a tenth of a unit of a rounding boundary
  at two decimals (flagged in A21-28) and are printed from unrounded values.
- X6 `pvalues` (`scatter`, §7): x rank $i=1,\dots,17$; y $\log_{10}p$ from −3 to 0 with `tickLabels` 0.001, 0.01,
  0.1, 1. Points: the 17 sorted p-values ("calendar family"; labels on Wed 0.018 and Dec 0.127). `lines` (segments
  between ranks): Bonferroni $\alpha/m=0.00294$; Holm $\alpha/(m-i+1)$ (its second threshold, if labelled, is
  0.003125, an exact tie at five decimals); Benjamini–Hochberg $iq/m$ at $q=0.05$ and $q=0.10$ [A21-32]. Note: a
  hypothesis is rejected only if its point lies on or below its rule's line (Holm from the left until the first miss;
  Benjamini–Hochberg at the largest rank on or below); none does, so no rule rejects.
- X7 `maxt` (`line`, §8): x log, number of rules $m$ from 1 to 10,000 (`tickLabels` 1, 10, 100, 1,000, 10,000); y
  t-stat −1.5 to 4.6 (`n2`). Series: band "model, 90% range" (the 5% and 95% quantiles of $\max_iZ_i$,
  $\Phi^{-1}(u^{1/m})$, exact); "model median"; `step` "best of m random rules on TR23" through its 11 record points
  [A21-36]. Dashed `hline` 3 "t = 3". Values: model median 1.75, 2.46, 3.20, 3.81 at $m$ = 17, 100, 1,000, 10,000;
  at 1,000 the range 2.75–3.88 [A21-35]; the search 2.95 at 100 and 1,000, 3.28 at rule 1,022, 3.97 at 10,000
  [A21-36]. Note: experiment 10, `default_rng([10, 20261011])`, one search (a single draw, not an average); the model
  assumes independent standard normal statistics, (21.9).

**Widget `multitest` — "Many tests, three rules."** `Book.controls`: number of tests $m$ (select 17, 50, 100, 200,
500, 1,000; initial 100); share with a real effect (0–50%, step 5%, initial 10%); a real effect's mean t-stat (0–5,
step 0.5, initial 3); level $\alpha=q$ (select 1%, 5%, 10%; initial 5%); button "New draw" (seed +1; initial seed 1).
Each draw: `Book.rng(seed)`, $Z_i$ = `normal()` plus the effect for the first round(share × $m$) tests;
$p_i=2\Phi(-\lvert Z_i\rvert)$ with `Book.dist.Phi`. `scatter`: x rank 1 to $\min(m,40)$, y $\lvert Z\rvert$ 0–6;
points "real effect" and "no effect"; `lines`: Bonferroni $\Phi^{-1}(1-\alpha/(2m))$, Holm
$\Phi^{-1}(1-\alpha/(2(m-i+1)))$ and Benjamini–Hochberg $\Phi^{-1}(1-iq/(2m))$ as segments (`Book.dist.PhiInv`).
Readouts: rejections and false rejections under Bonferroni, Holm and Benjamini–Hochberg; the largest $\lvert Z\rvert$
without an effect; $m\alpha$ times the null share (expected false rejections without correction). No Student $t$ and
no `tInv` (capability D not approved): the statistics are normal by construction. The widget embeds no data. Initial
state (PDF): the values above. The text quotes no widget number (the stream is `Book.rng`'s, not NumPy's).

**Examples** (results recomputed from the printed inputs):

- E1 §2 `manager` (hypothetical, [[LM13]]'s): 8 good months of 12; $H_0:\theta=\tfrac12$ against $H_1:\theta>\tfrac12$.
  $\Pr(X\ge8)=794/4{,}096=0.194$ [A21-46], so the record is not significant. The 5% test rejects only at
  $X\ge10$: $\Pr(X\ge9)=0.073$ is too large, $\Pr(X\ge10)=79/4{,}096=0.0193$ is the size. If the manager is skilled
  ($\theta=0.55$, LM13's value), the test rejects with probability 0.042; a type II error has probability 0.958. Set
  beside LM13's posterior of 13.5% (lm13.md:334): a different question, answered in [[LM24]].
- E2 §2 `updays`: TR23's 3,205 up days of 5,849, $\hat\theta=0.548$; $H_0:\theta=\tfrac12$ (a day as likely to rise
  as to fall), one-sided. $z=(\hat\theta-\tfrac12)/\sqrt{1/(4T)}=7.3$; exact $\Pr(X\ge3{,}205)=1.2\times10^{-13}$
  [A21-22]. Both null laws assume independent days; §5 checks the signs.
- E3 §3 `mean`: $\bar R=0.0625\%$ ([[LM19]]'s) and $s_{\mathrm u}=1.2085\%$ give
  $\operatorname{SE}=s_{\mathrm u}/\sqrt T=0.0158\%$ ([[LM20]]'s (20.2); $s/\sqrt T$ gives the same four decimals) and
  $\text{t-stat}=3.96$ [A21-12]; two-sided $p=7.6\times10^{-5}$ (normal), $7.7\times10^{-5}$ ($t_{5848}$); one-sided
  $3.8\times10^{-5}$ [A21-16]. [[LM20]]'s 95% interval for the annual mean, 7.8% to 23.0% a year [A21-17], excludes
  0: the same decision at 5%. With $s$ in place of $s_{\mathrm u}$ the t-stat is 3.956 (A21-12): the divisor does not
  matter at this $T$.
- E4 §3 `regimes` (stability check): t-stats 2.05 and 3.68 (X1); their two-sample statistic is
  $(0.0804-0.0464)/0.0315=1.08$, $p=0.28$ [A21-18] (SciPy's `ttest_ind(..., equal_var=False)`, which uses a $t$
  reference: 0.280). One period passes 5%, the other passes 1%, and the difference between them is not significant.
- E5 §4 `years`: 80% power at the 5% level needs $\tau=((1.959964+0.841621)/\mathrm{SR})^2$: 7.85, 31.4 and 125.6
  years for $\mathrm{SR}$ = 1, 0.5, 0.25 [A21-20]. TR23's annual Sharpe ratio, [[LM19]]'s
  $\sqrt{246.12}\times0.0625\%/1.2084\%=0.81$ [A21-19], needs 11.9 years; its t-stat is
  $0.8115\times\sqrt{23.7645}=3.956$ (A21-19). Over TR23's span the power is 0.98 at 0.81 and 0.68 at 0.5 [A21-21]
  (model, if that were the true ratio).
- E6 §5 `signs`: LM13's table; expected counts by (13.6) with the margins 2,643, 3,205; 2,644, 3,204: 1,194.95,
  1,448.05, 1,449.05, 1,755.95 (exact fractions). $\chi^2=2.69=5{,}848\times0.02143^2$, $p=0.10$ [A21-23].
  $\hat\rho=0.0214$ is LM15's $\rho_1$ (0.0215 from rounded frequencies, 0.0214 unrounded, lm15.md:100; A21-24).
  SciPy's default (Yates' correction) prints 2.60, $p=0.107$ (A21-23). No evidence against independent signs at 5%.
- E7 §5 `falls`: 108 days after a fall of 3% or more; 13 were falls, against $108\times108/5{,}848=2.0$ under
  independence; with $\theta_0=108/5{,}848$, exact $\Pr(X\ge13)=1.2\times10^{-7}$ [A21-25]. Large moves cluster, so the
  days are not independent: the null laws of E2 and E6 hold only for the signs, approximately.
- E8 §6 `wednesday`: the smallest of 17 p-values is Wednesday's 0.018 [A21-30]; $17\times0.05=0.85$ false rejections
  expected; FWER 0.58 if independent [A21-29]. With TR23's dates shuffled 10,000 times (experiment 8, Model), 0.580 ±
  0.005 of the shuffles have a test at $\lvert z\rvert\ge1.96$, and 0.266 ± 0.004 have one at least as extreme as
  Wednesday's [A21-31], close to Šidák's adjustment $1-(1-p_{(1)})^{17}=0.267$; Bonferroni's adjusted p-value is
  $17\,p_{(1)}=0.31$ [A21-30]. Stability check: Wednesday's statistic is 2.06 before June 2015 and 1.25 after
  [A21-33].
- E9 §7 `holmbh` (constructed): ten p-values 0.002, 0.0054, 0.0061, 0.011, 0.024, 0.031, 0.09, 0.22, 0.47, 0.86 at
  $\alpha=q=5\%$. Bonferroni (0.005) rejects 1; Holm (0.005, 0.00556, 0.00625, then 0.011 > 0.00714) rejects 3;
  Benjamini–Hochberg ($iq/m$ = 0.005, …, 0.035) rejects 5, since 0.024 ≤ 0.025 and every later $p_{(i)}$ misses
  (0.031 > 0.030) [A21-47]. Then the calendar: $p_{(1)}=0.018$ exceeds 0.00294, the first threshold of all three rules
  (0.00588 for $q=0.10$), so none rejects anything [A21-32]; Benjamini–Hochberg's adjusted p-values start at 0.308
  [A21-56].
- E10 §8 `search` (Model on TR23's returns): 10,000 rules, each long or short one unit by a fair coin each day
  (experiment 10). Their t-stats average −0.01 (standard error 0.01) with standard deviation 0.995 (batch standard
  error 0.007); 13 reach 3, against 13.5 expected [A21-37]. The best after 100 rules is 2.95 (rule 90), still 2.95
  after 1,000; rule 1,022 reaches 3.28; the best of 10,000 is 3.97 [A21-36], a single search with no standard error.
  Under (21.9) the best of 1,000 has median 3.20, and exceeds 3 with probability 0.74 [A21-35]. $\lvert t\rvert=3$ has
  $p=0.0027$, Bonferroni's level for 18.5 tests at 5% [A21-34].

**Problems plan** (11; MC keys B, C, A, B, A; the lab solves 6, 7, 9, 10, 11). Stems state the sample (TR23, 3 January
2003 → 8 October 2026, $T=5{,}849$, or the constructed setting), simple returns, the divisor ($s_{\mathrm u}$ in
t-stats), $A=246.12$ where a Sharpe ratio is annualized, two-sided 5% unless stated, the normal reference unless
stated, rounding, and for Problem 11 the seed and the draws.

1. MC: "A test at the 5% level rejects $H_0$. Which is true?" A: $H_0$ has probability below 5% (a p-value is not
   $\Pr(H_0)$). **B**: if $H_0$ were true, a statistic at least this extreme would occur with probability at most 5%.
   C: $H_1$ is true with probability at least 95% (the same error, reversed).
2. MC: 20 independent tests, every null true, each at 5%; the probability of at least one rejection. A 0.05 (one
   test's). B 1.00 ($20\times0.05$, a bound, not a probability). **C** 0.64 [A21-48].
3. MC: years of daily data for 80% power against an annual Sharpe ratio of 0.5, two-sided 5%, iid returns. **A**
   31.4. B 15.4 (drops $\Phi^{-1}(0.8)$: power 50%). C 5.60 (forgets to square) [A21-49].
4. MC: 4,000 day pairs whose indicators correlate $\hat\rho=0.03$; the 2×2 $\chi^2$. A 120 ($n\hat\rho$). **B** 3.60
   ($p=0.058$: not rejected at 5%). C 1.90 ($\sqrt n\hat\rho$, the $z$, not $\chi^2$) [A21-50].
5. MC: p-values 0.003, 0.012, 0.020, 0.030, 0.40 at $q=5\%$; how many does Benjamini–Hochberg reject? **A** 4. B 2
   (Holm's count). C 1 (Bonferroni's) [A21-51].
6. LM13's manager (hypothetical), one-sided 5%: (a) the p-value of 8 good months in 12 under $\theta_0=\tfrac12$,
   0.194; (b) the rejection region and its size, $X\ge10$, 0.0193; (c) the power at $\theta=0.55$, 0.042 [A21-46];
   (d) months for 80% power by the normal approximation,
   $n=\big((1.644854\times0.5+0.841621\sqrt{0.55\times0.45})/0.05\big)^2=616.16$, so 617, 51.4 years; exact at
   $n=617$: reject at $X\ge330$, size 0.0454, power 0.7874 [A21-52].
7. LM15's blocks (lm15.md:86–104): variance 4.72 (divisor 292) against the binomial 4.95 and the dependence-adjusted
   5.16. With [[LM20]]'s standard error of a variance for nearly normal counts, $\sigma^2\sqrt{2/292}$: $z=-0.56$ and
   $-1.03$ from the printed values ($-0.58$, $-1.03$ unrounded), neither significant. Detecting the gap of 0.21 at
   $z=1.96$ against the binomial null needs $n=2(1.959964\times4.95/0.21)^2=4{,}268.7$, so 4,269 blocks: 85,380
   sessions, 347 years [A21-53]. "292 blocks cannot see a dependence this small" made exact.
8. [[LM16]]'s printed U28 counts, collapsed to 2×2 (Semiconductor and FinancialInsurance each at or below −1%: 347
   both, 859 and 538 single, 4,382 days; the script recounts them on U28, A21-61): the table 347, 512, 191, 3,332;
   $\hat\rho=0.423$; $\chi^2=784$ [A21-54]. Why the $\chi^2_1$ law is doubtful (clustered days; §5) and why the
   conclusion stands (any reasonable widening leaves $\chi^2$ far beyond 3.84). The ratio 3.29 recomputes as 3.2902.
9. Jarque–Bera (the editor's decision): the statistic as SciPy's `jarque_bera` computes it,
   $\mathrm{JB}=\frac T6\big(\operatorname{Skew}^2+\tfrac14(\operatorname{Kurt}-3)^2\big)$ with divisor-$T$ moments
   (SOURCES, "SciPy 1.18 (Stage 1 check)"), Jarque and Bera (1980) cited as its origin (bibliographic only); that it is
   approximately $\chi^2_2$ under iid normal returns is stated without proof. From [[LM14]]'s printed −0.34 and 5.27: $\mathrm{JB}=6{,}881$; by (16.9) the tail is
   $e^{-\mathrm{JB}/2}$, about $10^{-1494}$; unrounded moments give 6,875 and $10^{-1493}$ [A21-55]. What the
   rejection says and what it does not (fat tails are known; the test sizes them).
10. Python: the calendar family (12 months, 5 weekdays, each against the rest of TR23) by hand with (21.3), the
    p-values with `stats.norm.sf`; then `multipletests` with `method="holm"` and `"fdr_bh"`, and without a method;
    `stats.false_discovery_control`. All reject nothing; the default is Holm–Šidák; the two smallest adjusted
    p-values are 0.308 and 0.669 [A21-56], [A21-28].
11. Python, Model: 10,000 families of 17 independent standard normal statistics from `default_rng([11,
    20261011])` (`standard_normal((10000, 17))`): the share with a rejection at $\lvert z\rvert\ge1.96$ is 0.590 ±
    0.005 against the exact 0.582; with Bonferroni ($\lvert z\rvert\ge2.974$), 0.051 ± 0.002 against 0.04884
    [A21-57]. Standard errors by (18.2).

**Lab parts** (`build/make_lab21.py`; reads only its `data/taiex_tr.csv`, which `data/make_lab_data.py` copies from
`raw/vol3/TAIEX_TR__2003-01-01__2026-10-08.csv`, as for LM13–LM18): 1 data: TR23 from the closes, $T$, years, $A$,
the guard and the `Fraction` check, weekday and month columns (the weekday convention checked on a known date:
2026-10-08 is a Thursday), the 23 Saturday sessions, the 29 tests listed; 2 E2, E3 by hand and with `stats.norm.sf`
and `stats.t.sf`, X1, X2; 3 (21.3) and E4, X3, E5; 4 the sign table and (21.5) by hand, E6 with and without Yates,
E7, E1 and Problem 6 with `stats.binom`, a pointer to LM13's lab question (make_lab13.py:463); 5 the calendar family,
X5, E8 with experiment 8; 6 Holm and Benjamini–Hochberg by hand, `multipletests`, `false_discovery_control`, X6, E9;
7 experiment 10, X7, E10 with its batch standard error, (21.9); 8 Problems 7, 9, 10, 11. Extension
(stability check): the calendar family in each limit regime (34 tests) under Holm and Benjamini–Hochberg. Labs write
"LM22", never `[[LM22]]`.

**Cross-module tags.**

- (21.1) $\text{t-stat}=(\bar R-\mu_{\text{null}})/(s_{\mathrm u}/\sqrt T)$; under $H_0$ approximately
  $\mathcal N(0,1)$ for iid returns with finite variance and large $T$; exactly $t_{T-1}$ for iid normal returns
  (Blitzstein and Hwang 2019, Ex. 7.5.9, Ex. 10.4.3 and Def. 10.4.4, combined in §3's one line) (LM22, 23, 33).
- (21.2) two-sided p-value $2\Phi(-\lvert\text{t-stat}\rvert)$ (one-sided $\Phi(-\text{t-stat})$); uniform on
  $(0,1)$ under a continuous null (LM22, 23, 24, 25, 26).
- (21.3) $(\bar R_1-\bar R_2)/\sqrt{s_{\mathrm u,1}^2/T_1+s_{\mathrm u,2}^2/T_2}$, the two-sample statistic with
  unpooled variances; two independent groups, iid within each, finite variances, large $T_1$, $T_2$; approximately
  $\mathcal N(0,1)$ under $\mu_1=\mu_2$ (LM33).
- (21.4) power $\approx\Phi\big(\mathrm{SR}\sqrt\tau-\Phi^{-1}(1-\tfrac\alpha2)\big)+\Phi\big(-\mathrm{SR}\sqrt\tau-\Phi^{-1}(1-\tfrac\alpha2)\big)$,
  and, when the second term is negligible,
  $\tau\approx\big((\Phi^{-1}(1-\tfrac\alpha2)+\Phi^{-1}(\text{power}))/\mathrm{SR}\big)^2$; iid returns, $\sigma$
  known, $r_f=0$, annual SR, two-sided level $\alpha$; a `gathered` display (LM33). No letter for the critical value:
  $c$ is LM4's Kelly fraction and $z$ a value of $Z$.
- (21.5) $\chi^2=\sum_{\text{cells}}(\text{observed}-\text{expected})^2/\text{expected}=n\hat\rho^2$ for a 2×2 table;
  approximately $\chi^2_1$ when the $n$ pairs are independent and identically distributed and the two indicators
  independent: for one series on consecutive days from (19.6) and LM16's $\chi^2_N$, for two series *stated without
  proof* (the editor's decision) (in-module; no later user yet).
- (21.6) with each of $m$ tests at level $\alpha/m$, FWER $\le m_0\alpha/m\le\alpha$ under any dependence ((13.2));
  for $m$ independent tests of true nulls at level $\alpha$, FWER $=1-(1-\alpha)^m$; expected false rejections
  $m_0\alpha$ under any dependence ((14.1), (14.3)) (LM23, 33, 34).
- (21.7) Holm: reject $p_{(1)},\dots,p_{(i_{\mathrm H})}$, where $i_{\mathrm H}$ is the number of leading ranks with
  $p_{(i)}\le\alpha/(m-i+1)$; FWER $\le\alpha$ under any dependence (LM23).
- (21.8) Benjamini–Hochberg: $i_{\mathrm{BH}}:=\max\{i:p_{(i)}\le iq/m\}$, reject $p_{(1)},\dots,p_{(i_{\mathrm{BH}})}$;
  FDR $\le q$ for independent statistics (stated without proof) (LM23, 34).
- (21.9) $\Pr(\max_iZ_i\le x)=\Phi(x)^m$ for independent standard normal $Z_1,\dots,Z_m$ (LM33, 34).

**Pitfalls to pre-empt.**

- A p-value is $\Pr(\text{data at least this extreme}\mid H_0)$, not $\Pr(H_0\mid\text{data})$; "not rejected" is not
  "true" (E1's power 4%); "significant" is not "large" (Wednesday's 0.0886% a day).
- Fix one- or two-sided and the family before looking. The calendar family is all 12 months and all 5 weekdays;
  Wednesday was found, not hypothesized.
- Conditions every time: (21.1) needs uncorrelated returns with a CLT, not normality; volatility clustering alone
  leaves $\Var\bar R=\sigma^2/T$ by (16.3), autocorrelation does not (next-day log returns correlate 0.039, lm17.md:392;
  LM23). The tests of §5 assume independent days, which E7 rejects for large moves.
- "Significant in one period, not in the other" is not a difference (E4: 1.08).
- Divisors and defaults: $s_{\mathrm u}$ in t-stats, $s$ in the Sharpe ratio and every printed standard deviation;
  Polars' `std` defaults to `ddof=1`; `multipletests` defaults to Holm–Šidák; SciPy's `chi2_contingency` applies Yates'
  correction to a 2×2 table and `ttest_ind` pools variances unless told otherwise (`equal_var=False`; SOURCES).
- Benjamini–Hochberg's guarantee needs independent statistics; the calendar's 17 are dependent (the months partition
  the days), and the shuffle shows the FWER barely moves (0.580 against 0.582). Benjamini–Yekutieli for any
  dependence.
- Count the tests: 29 on TR23 here. Report each test with its family.
- Samples: LM16's counts are U28's, LM13's pairs are 5,848, LM15's blocks 5,840 returns; the 23 Saturday sessions sit
  in every "rest". $A=246.12$, never 252.
- Numbers near rounding boundaries (flagged in the anchors, each printed from its unrounded value or exact): the
  full-sample t-stat 3.9557 (3.96, or 3.956 in X1), the post-2015 3.67515 (3.68, or 3.675 in X1), December's 1.5255
  and X5's July and August, the years 23.7645 (exact), E6's expected counts (exact fractions), E8's 0.004, the model's
  3.88, Holm's 0.00556 (exact), and LM15's printed 4.95 and 5.16. The up-day $z$ prints 7.3, the normal p of KC §9
  0.0455, Problem 6's 616.16 and Problem 11's exact 0.04884, which avoids four flags; Holm's 0.003125 is an exact tie
  at five decimals and prints in full.
- References (SOURCES, no theorem numbers yet): Holm (1979); Benjamini and Hochberg (1995) for independent
  statistics; Benjamini and Yekutieli (2001) through SciPy's documented use of its Theorem 1.3; Harvey, Liu and Zhu
  (2016), the abstract's sentence only; White (2000) and Romano and Wolf (2005) by their abstracts; Wasserman (2004,
  ch. 10; §10.2 p-values, §10.7 multiple testing, its coverage unconfirmed) and Casella and Berger (2nd ed., ch. 8;
  the year, 2001 or 2002, is open) for the framework; Blitzstein and Hwang (2019) Ex. 7.5.9, Ex. 10.4.3 and
  Def. 10.4.4 for the $t$ law of (21.1) (the book does not state that law itself, so the text shows the one line and
  never cites "§10.4"); no paper for the two-sample statistic (21.3); Jarque and Bera (1980) as the origin of Problem
  9's statistic (bibliographic only), with SciPy's formula; Lo (2002) via LM19; Merton (1980) via LM20.

**Stage 4 for earlier modules.** `leads` gain 21 in lm04.md:6 (LM21 cites lm04.md:541 and 563; cross-check X29),
lm05.md:6 ((5.5)), lm14.md:6 ((14.1), (14.3), (14.5)) and lm18.md:6 ((18.2) and the batch standard error), as in the
plan's Stage 4 table; lm13.md:6, lm15.md:6, lm16.md:6 and lm17.md:6 already list 21. No wording changes: every forward
link above is kept as printed.

**Changes in this revision** (by the cross-check's finding numbers and the recomputation's items).

- Owners (X1, X3, the editor's "Owners"): $\bar R$, $s$ and the Sharpe ratio 0.81 are cited as [[LM19]]'s; the
  standard error and the interval as [[LM20]]'s, E3 now quoting LM20's printed interval 7.8% to 23.0% a year
  (A21-17 changed); LM21 owns the t-stats, 3.955678 with $s_{\mathrm u}$ for LM24.
- Shuffled dates kept as *Model* (X7); statistics from LM16's printed counts labelled, and the counts recounted on U28
  (X8, new A21-61).
- Two-sample statistic named without Welch; SciPy's `equal_var=False` named (X35); script labels changed to match.
- After the fresh check (X32, X34, the editor's decisions): the $t$ law of (21.1) is derived in one line from
  Blitzstein and Hwang's Ex. 7.5.9, Ex. 10.4.3 and Def. 10.4.4; (21.5)'s two-series case stays *stated without proof*;
  Problem 9 stays, with SciPy's formula and Jarque and Bera (1980) as its origin; the SciPy facts are in SOURCES; the
  Saturday sessions follow the "Calendar" decision; (21.5) no longer lists LM25 (its prerequisites cite only (21.2)).
- Tag (19.6) cited for the band (X27); lm04 added to Stage 4 (X29); published files hold no daily series (X37).
- Recomputation 1: E8's permutation is `R[perm]` on fixed dates. 2: E10's standard deviation uses the book's $s$
  (divisor 10,000; 0.9952 → 0.9951, printed 0.995) and now carries a batch standard error, its mean a standard error
  (A21-37 changed). 3: Problem 7's block count is 4,268.7, so 4,269 blocks and 85,380 sessions (was "4,269 = 85,374").
  4: A21-20's label shows the unrounded 0.811509.
- Rounding (recomputation table, the editor's "Rounding"): the script's `chk` checks every printed form at its
  printed precision; new flags in A21-15, A21-23, A21-31, A21-47 and A21-53; the case box prints 0.1332% and 0.0446%
  (0.045% was near a boundary); KC §9 prints 0.0455; Problem 6 prints 1.644854, 616.16, 0.0454 and 0.7874; Problem 11
  prints 0.04884; E2 prints 7.3; E8 writes $17\,p_{(1)}$ and Šidák's 0.267 from the unrounded $p_{(1)}$; the 1.99 of
  A21-25 is no longer listed (only 2.0 prints).

**Open before Stage 2** (open in SOURCES; until they close the text cites as the decisions say): whether Wasserman
§10.7 covers Bonferroni and Benjamini–Hochberg; Casella and Berger's year and theorem numbers; Harvey, Liu and Zhu's
section numbers (only the abstract is cited).

## LM22 Resampling Methods

Stage 1 brief, revised 2026-10-19 after the cross-check and the independent recomputation. Drafted from the editor's
spine (`plans/vol-4.md` at commit bcfa0d4, "### LM22 Resampling Methods") and revised to the editor's decisions on the
drafts (same file) and to the fresh check. Each number carries its anchor ID at its first appearance;
`data/vol4_anchors_lm22.py` prints them all (rows in `plans/vol-4-anchors.md`). Numbers quoted from published modules
cite their file and line.

**Prereq:** `[4, 11, 13, 14, 16, 17, 18, 19, 20, 21]`.

- LM4: the quadratic rule (4.3) $f_q\approx\mu/\sigma^2$ (lm04.md:118); $\bar g(f)$ (4.4) and its derivative (4.5)
  (lm04.md:176, 180), whose root is the exact in-sample optimum; the band example (lm04.md:543–549: SE 0.0230% a day,
  a 26% relative error, interval 0.042%–0.132%, exact Kelly band 2.7–7.6, quadratic 2.7–8.6); fractional Kelly
  (lm04.md:558).
- LM11: the explained share (11.6), $\lambda_1/N$ for a correlation matrix (lm11.md:262); the yearly shares 34.5%
  (2017) and 66.6% (2020) (lm11.md:47, 369); the pitfall's "250 returns" (lm11.md:406).
- LM13: the empirical distribution function $\hat F$ (13.12) (lm13.md:374); independence of $n$ variables and "iid"
  (13.13) (lm13.md:394).
- LM14: $\operatorname{Skew}$ and $\operatorname{Kurt}$ (14.5) (lm14.md:208); the quantile function
  $F_X^{-1}(u):=\min\{x:F_X(x)\ge u\}$ (lm14.md:85–88), applied to the $B$ resampled values; TR23's moments
  (Skew −0.34, Kurt 8.27, LM14's).
- LM16: the variance of a sum (16.3) (lm16.md:197); the conditional correlation (16.10) (lm16.md:444) with
  $\Var(Z\mid\lvert Z\rvert\ge2)=5.7464$ (lm16.md:456); the crash-correlation example (lm16.md:497–507: 223 days, data
  0.788 against the model's 0.860) and its pitfall (lm16.md:514).
- LM17: (17.1) (lm17.md:69) and the CLT (17.5) (lm17.md:276); the lag correlations of $\lvert r\rvert$, 0.161 at lag 1
  and 0.123 at lag 20 (lm17.md:392); the exact in-sample root of (4.5), 4.1381 (lm17.md:239), written $\hat f^*$ here.
- LM18: (18.2) and (18.3), the Monte Carlo standard error and interval (lm18.md:141, 147); the batch standard error
  (lm18.md:153: 20 batches, divisor 20); the seed rule and chunks (lm18.md:70, 419–436); the iid bootstrap and (18.8),
  (18.9) (lm18.md:333–349); what resampling keeps and destroys (lm18.md:375–381); the five-year windows (lm18.md:33,
  366, 373).
- LM19 (same batch): the sample autocorrelation $\hat\rho_k$ (19.5) (full-sample mean, divisor $T$); the variance of an
  $m$-day sum (19.7); $\operatorname{VR}(m)$ (19.8), overlapping sums centred at $m\bar r$; the annualization rule (the
  Sharpe ratio times $\sqrt A$ only for uncorrelated returns; Lo 2002). LM19 owns the estimates the case starts from:
  TR23's Sharpe ratio, 0.0517 a day and 0.81 a year, and its volatility $\sqrt A\,s=18.96\%$, both on $R$ with $r_f=0$;
  $\hat\rho_1(\lvert r\rvert)=0.161$ and $\operatorname{VR}(20)=1.036$.
- LM20 (same batch): (20.2) $\operatorname{SE}(\bar R)$, behind §3's relative error $1/(\widehat{\mathrm{SR}}\sqrt T)$;
  (20.4)'s normal interval, the pattern of the delta-method intervals; $\hat f:=\bar R/s^2=4.28$ and every standard
  error and interval of the delta method, (20.8) and (20.9), as LM20's `delta` table prints them: the Sharpe ratio's SE 0.207 (plug-in skewness and kurtosis) and 0.205
  (normal), interval 0.40 to 1.22; $\hat f$'s SE 1.111 (plug-in), 1.085 (normal) and 1.082 (mean only), interval 2.10
  to 6.46; the volatility's SE 0.33 points (plug-in).
- LM21 (same batch): null and alternative, test statistic, p-value, size; the t-stat (21.1),
  $\bar R/(s_{\mathrm u}/\sqrt T)$, 3.96 on TR23 and 2.05 in the 7% regime, with two-sided normal p-values (21.2), $7.6\times10^{-5}$ and 0.041; the duality of
  a test and an interval; the shuffled-date null (*Model*); the rule that every test reports how many tests ran on the
  same data.

**Leads:** `[23, 25, 26, 30, 33, 34, 45]`: pointer targets in the text (LM23 §4, LM25 §5 and §7, LM26 §5, LM30 §9,
LM34 §3 and §8, LM33 §3, LM45 §3) and tag users (LM33 and LM45 cite (22.1)–(22.3); LM34 cites (22.2) and (22.4)).

**Forward links honoured.** The grep of `src/lm*.md`, `src/pages/*.md` and `build/make_lab*.py` for "LM22" returns
exactly the spine's list; none was missed.

| Earlier text | Promise | Kept in |
|:--|:--|:--|
| lm11.md:406 | an eigenvalue from 250 returns "has sampling error of its own, and this module attaches no confidence intervals ([[LM20]], [[LM22]])" | §7, E8: block-bootstrap intervals for PC1's share in 2017 (246 returns) and 2020 (245) |
| `build/make_lab11.py:571` (Part 12's extension, from :566) | "How much of the movement is sampling noise? [[LM20]] gives the tools to answer" | E8 answers it for the two extreme years; Stage 4 rewords the line |
| lm16.md:62 | "whether gaps could be chance is [[LM21]]'s and [[LM22]]'s question" | §7 E7 (the gap's interval); §8 (a test by duality) |
| lm16.md:514 | 0.788 against 0.860; "whether a gap could be chance is for [[LM21]] and [[LM22]]" | E7: gap −0.071, block interval −0.094 to −0.033, no resample at or above 0 |
| `build/make_lab16.py:571` | regime correlations 0.6544 and 0.5564: "draw no conclusion about chance from it (LM21, LM22)" | lab extension: block-bootstrap intervals for both regimes and their difference (lab only, labelled a stability check) |
| lm18.md:50 | "[[LM22]] resamples blocks" | §5 |
| lm18.md:366 | the windows' "± one standard error": "none here ([[LM22]])" | E9: 4.1% with a block-bootstrap SE of 9.9 points |
| lm18.md:373 | "Their error needs a bootstrap of blocks ([[LM22]])" | E9: the share under water and the SD of $\ln G$ (0.283: interval 0.20 to 0.68) |
| lm18.md:381 | "Resampling blocks of days keeps part of the clustering ([[LM22]])" | §5, X4, X5: $\hat\rho_1(\lvert r\rvert)$ averages 0.156 in block resamples, −0.0001 in iid ones |
| lm18.md:389 | "Reading a range of resamples as an interval for TAIEX is bootstrap inference, left to [[LM22]]" | §2 (the bootstrap principle, (22.1), (22.2)), §3 |
| `build/make_lab04.py:642` | walk-forward Kelly: "LM22 (resampling) and LM45 (Kelly under uncertainty) return to this question" | §3: the in-sample Kelly fraction's interval; one sentence sends the walk-forward test to [[LM34]] and sizing to [[LM45]]; Stage 4 rewords the line |

Consistency kept: LM18's iid answers (5.6% ± 0.2, quantiles 0.97 / 1.94 / 3.94, SD of $\ln G$ 0.424 ± 0.003,
lm18.md:357–361) answer another question (independent five-year paths), so E9 says what its windows statistic is;
lm18.md:379's "resampling destroys the clustering" is E4's starting point; LM7's Sharpe ratios (lm07.md:493) used an
illustrative $r_f=1.5\%$ on 0050, while Volume IV sets $r_f=0$ (one sentence in §3).

**Outcomes** ("After this module you should be able to:"):

1. explain the bootstrap principle, and compute a bootstrap standard error, a percentile interval and a basic interval, stating what BCa adds
2. calculate bootstrap intervals for a Sharpe ratio and a Kelly fraction, and compare them with the delta method's intervals
3. explain why resampling single days fails for dependent returns, and identify the statistics it misjudges
4. apply the moving-block and stationary bootstraps, state what circular blocks change, and explain what each scheme keeps and what it loses
5. choose a block length with the book's rule built on Politis and White's estimate, and check how much a result depends on it
6. compute block-bootstrap intervals for a variance ratio, a conditional correlation, a principal component's share and a window statistic, and choose between the percentile and the basic interval
7. carry out a bootstrap test by resampling under the null hypothesis, and relate it to the interval at the same level
8. implement iid and block bootstraps in NumPy, check them against arch and SciPy, and report the seed, the resamples and the Monte Carlo error

**Owns.** The bootstrap as inference (LM18 owns the mechanics): the plug-in principle ($\hat F$ for $F$), the ideal
bootstrap and its Monte Carlo approximation, the bootstrap standard error (22.1), the percentile and basic intervals
(22.2), BCa stated without proof (SciPy's default; Efron 1987). TR23's bootstrap intervals, iid and block, for the
annualized Sharpe ratio, $\hat f$, the exact in-sample optimum $\hat f^*$ and the annualized volatility, compared with
LM20's delta-method intervals (the estimates are LM19's and LM20's). When the iid bootstrap fails: dependence, shown on
$\hat\rho_1(\lvert r\rvert)$ and $\operatorname{VR}(20)$. The moving-block and stationary bootstraps with their
conditions (22.3), circular blocks in one sentence, and the schemes' agreement on TR23 (X7). The block length:
Politis and White's automatic estimate (arch), the book's rule built on it, and the sensitivity curve. Every printed
interval uses the stationary bootstrap at the book's length, except X7's comparison of schemes. Block-bootstrap
intervals for $\operatorname{VR}(20)$ (LM19's statistic), LM16's crash correlation and its gap to (16.10), LM11's PC1
share in 2017 and 2020, and LM18's windows. Bootstrap tests by resampling under the null (22.4), on TR23's mean, set
beside LM21's normal-reference tests. NumPy implementations that draw arch's indices exactly, and SciPy's `bootstrap`
defaults.

**Leaves.**

- Sizing from a bootstrap distribution, bootstrap Kelly, and LM4's walk-forward question → LM45 (walk-forward testing
  → LM34).
- Resampled portfolios → LM30.
- The reality check, Romano–Wolf and the probability of backtest overfitting, all bootstrap-based → LM34.
- The Sharpe ratio's analytic standard error under dependent returns (Lo 2002), the Probabilistic and Deflated Sharpe
  ratios, and Ledoit and Wolf's (2008) studentized block-bootstrap test of two Sharpe ratios → LM33.
- The long-run variance (HAC), the analytic counterpart of a block bootstrap's variance of a mean → LM23.
- Stationarity defined, the robust autocorrelation band, Ljung–Box and the variance-ratio test → LM25.
- Models of clustering (GARCH) → LM26.
- Not in the book, one sentence each: the parametric bootstrap (Wasserman 2004, §9.11, location only), subsampling
  (Lahiri 2003, §7.3), the bootstrap-t interval, the jackknife beyond BCa's acceleration, the wild bootstrap.

**Uses before taught** (one sentence each in the text):

- §2 BCa: "BCa adjusts the percentile interval for bias and skewness, using a jackknife (the statistic recomputed
  with each day left out once); it is SciPy's default, and this book states it without proof (Efron 1987)."
- §3: "How to size a position from this distribution is [[LM45]]'s subject, and a walk-forward test of the Kelly
  fraction is [[LM34]]'s."
- §3: "The Sharpe ratio's standard error for dependent returns, and the Probabilistic and Deflated Sharpe ratios, are
  [[LM33]]'s."
- §4: "[[LM23]] estimates the same long-run variance directly (HAC); the block bootstrap estimates it by resampling."
- §5 (X28): "Stationarity, a law of the returns that does not change with the date, is defined in [[LM25]]; here it is
  one of the conditions stated without proof."
- §5: "Volatility that depends on yesterday's is modelled in [[LM26]]."
- §7: "[[LM25]] tests a variance ratio with its own robust standard error."
- §8 (X7): "[[LM21]] built its calendar nulls by shuffling the dates, a resampling without replacement that imposes
  'no calendar effect' (*Model*); here centring imposes 'no mean'."
- §8: "Testing many strategies at once with the bootstrap (the reality check) is [[LM34]]'s."
- §9: "Resampled portfolios are [[LM30]]'s."

**Data role.** Two samples, never mixed in one statistic; every caption names its sample.

- **TR23** from `data/processed/vol3_taiex.parquet` (`data/vol3_series.py`; FinMind `TaiwanStockTotalReturnIndex`,
  data_id TAIEX, retrieved 2026-10-18): 5,850 closes 2003-01-02 → 2026-10-08, $T=5{,}849$ simple returns from
  2003-01-03 [A22-01]; 8,680 days, 23.7645 years, $A=246.12$, $\sqrt A=15.69$ [A22-02]. Moments with divisor $T$:
  $\bar R=0.062505\%$, $s=1.2084\%$ [A22-03] (as LM17 and LM18 print them; [[LM19]] owns them); Skew −0.34 and Kurt
  8.27 are [[LM14]]'s, and the delta formulas use the unrounded −0.3384 and 8.2680 [A22-03]. Regimes by return date:
  3,077 returns to 2015-05-29, 2,772 from 2015-06-01 [A22-01]. One-day statistics on $R$; sums and $\lvert r\rvert$ on
  $r=\ln(1+R)$.
- **U28** through `u28()` of `data/lm10_series.py` (closes from `data/processed/vol2_closes.parquet`, built and repaired
  by `data/vol2_series.py`; FinMind `TaiwanStockPrice`, retrieved 2026-10-11, with 524 closes on 38 dates repaired from
  `TaiwanStockEvery5SecondsIndex`, lm16.md:52): $T=4{,}382$ returns 2008-12-02 → 2026-10-08, $A=245.48$ [A22-04].
  Price indices, no dividends: every caption says so. Used for LM16's pair (Semiconductor, FinancialInsurance) and
  LM11's yearly correlation matrices of the 28 sectors (2017: 246 returns, 2020: 245 [A22-31], [A22-32]).
- No new data; no TX23, no T5S. Cleaning: none beyond the two builders'.
- Scripts: `data/vol4_anchors_lm22.py` (the anchors; about three minutes), then `data/lm22_numbers.py` (re-runs every
  experiment, asserts every printed value against `src/lm22.md`, flags values near a rounding boundary) and
  `data/lm22_charts.py` (X2–X6 and the widget's precomputed histograms, experiment 24); both join `DATA_STEPS` in
  module order after `data/vol4_rv.py`.
- Bootstrap conventions. $B=10{,}000$ resamples unless stated, drawn in chunks of 500 rows (only how the draws are
  made). The bootstrap SE divides by $B$ (LM18's choice; Efron and Tibshirani's (6.6) and SciPy's `standard_error`
  divide by $B-1$). Every quantile, of data or of resamples, is $\hat F^{-1}(u)$ (`method="inverted_cdf"`): the
  percentile ends are the order statistics $\lceil0.025B\rceil=250$ and $\lceil0.975B\rceil=9{,}750$ [A22-44]. Monte
  Carlo errors are LM18's batch SEs: 20 batches of $B/20$ consecutive resamples, the statistic on each (an end as the
  batch's order statistic, the 13th and 488th of 500), the SD of the 20 values (divisor 20) over $\sqrt{20}$; a
  bootstrap p-value's is $\sqrt{p(1-p)/B}$.
- Seeds (`default_rng([e, 20261011])`, created once per experiment): 1 E1; 2 iid resamples of TR23 (E2–E5, X1–X4, X7's
  iid row; the SciPy check re-creates stream 2 on purpose); 3 stationary resamples of TR23 at $\ell=145$ (same uses;
  Problem 10 re-creates it); 4 the block-length grid (X6); 5 moving and 6 circular blocks (X7); 7 X5's two paths; 8, 9
  the crash correlation (iid, block); 10–13 PC1's shares (2017 iid, 2017 block, 2020 iid, 2020 block); 14, 15 LM18's
  windows (block, iid); 16–18 the tests (7% regime iid, 7% regime block, full sample block); 19 the §8 knowledge check;
  20 the arch check (§9); 21 Problem 6; 22, 23 Problem 11; 24 the widget's precomputed histograms.
- Block length used for every printed number (the book's rule, §6, as the editor's "Resampling" decision words it:
  one length per sample and statistic family, the largest Politis–White stationary estimate among the squared
  demeaned simple-return series the statistic involves, rounded): $\ell=145$ for every TR23 statistic, whether on $R$
  or on $r$, and its full-sample test; 130 for the U28 pair, 7 (2017) and 18 (2020) for the PC1 shares, 108 in the 7%
  regime, 36 in the 10% regime (Problem 11).
- No full daily series in a published file (the editor's rule, X37): X5 is thinned to every fifth session; the widget
  embeds precomputed histograms, not returns.

**Hygiene declaration.** *In-sample:* every bootstrap interval and test (resamples draw from the sample they
describe, both limit regimes mixed, as lm18.md:389 warns). *Model:* the resampled paths of X5, the widget's
resamples, and the iid resamples read as a world of independent days (E4, the §8 null). *Stability check:* the 7%
regime test (E10), the 10% regime's Kelly interval (Problem 11) and the lab's regime correlations. *Descriptive:*
LM11's yearly shares and LM18's windows as quoted. Nothing is out-of-sample ([[LM34]]). Test count, stated in §8: four
tests, three on TR23 (the mean in the 7% regime and in the full sample, independence of $\lvert r\rvert$ by the iid
null) and one on U28 (the crash gap); E8 compares two years chosen after looking. Local note (draft): "Every interval
here resamples the whole sample it describes, so it is in-sample. A bootstrap interval measures sampling error under
the resampling model; its Monte Carlo error is stated beside it. Resampled paths are a model, not a forecast."

**Notation.** AUTHORING §6 with the Volume IV table: $B$ resamples, $\ell$ (mean) block length, $\hat f=\bar R/s^2$
(LM20's), $\hat f^*$ the exact in-sample root of (4.5), $\theta$, $\hat\theta$, $\operatorname{SE}$,
$\operatorname{Bias}$, $s$ (divisor $T$), $s_{\mathrm u}$ (only in the t-stat), $\text{t-stat}$, $\alpha$ the
significance level (LM22 is one of its two modules), $\hat\rho_k$ (LM19's convention), $\operatorname{VR}(m)$ (LM19's
(19.8)), $\mathrm{SR}$ per day or annualized with $r_f=0$. Also used: $R$, $r$, $\bar R$, $\bar r$, $s_r$, $A$, $T$,
$t$, $m$ (days summed: $\operatorname{VR}(20)$, $m=1{,}231$), $G$, $f$, $f^*$, $\Pr$, $\E$, $\Var$, $\hat F$,
$\hat F^{-1}$, $\E_{\hat F}$, $\Var_{\hat F}$, $\Pr_{\hat F}$, $\bar R_{\text{boot}}$ (LM18's), $\mathcal N$, $\Phi$,
$\Phi^{-1}$, $\rho$, $\hat\rho$ (the pair's correlation, LM16's), $\lambda_1$, $C$, $N$ (LM11's), $U$ a uniform draw,
$\operatorname{Skew}$, $\operatorname{Kurt}$. Local:

| Symbol | Meaning | Check |
|:--|:--|:--|
| $h$ | a statistic as a function of the data, $\hat\theta=h(x_1,\dots,x_T)$ | generic function; $f$, $g$ are taken |
| $\hat\theta_{\text{boot},i}$, $\bar\theta_{\text{boot}}$ | the statistic on resample $i=1,\dots,B$; their mean | no star (§6); LM18's subscript |
| $\hat F_{\text{boot}}$, $\hat F_{\text{boot}}^{-1}(u)$ | empirical distribution of the $B$ values; its quantile, $\hat\theta_{\text{boot},(\lceil uB\rceil)}$ | §6's $\hat F$ with a subscript; never $q$ |
| $\widehat{\mathrm{SR}}$ | $\bar R/s$ per day; annualized $\sqrt A\,\widehat{\mathrm{SR}}$ | hat on the book-wide $\mathrm{SR}$ |
| $\hat\rho_1(\lvert r\rvert)$ | lag-1 sample autocorrelation of $\lvert r_t\rvert$ | LM19's $\hat\rho_k$; unsubscripted $\hat\rho$ stays the pair's |
| $\psi$, $\sigma_\psi$ | Deep Dive (a) only, declared in its first sentence: an increasing function; the standard deviation of $\psi(\hat\theta)$ | §6 allows a Deep Dive's own variables; Volume IV has no constraint functions |
| $i$; $t$; $j$ | resamples; days; ranks and blocks | LM18's indices |

Clashes avoided: no $q$ for a quantile (LM21's level); $1/\ell$, never $p$, for the block-start probability (no bets,
but $p$ is LM21's p-value letter); "the bootstrap p-value" in words (§6: "p-value" in words outside LM21); no $k$ for a
number of standard deviations (LM16's event is written $\lvert R_t-\bar R\rvert\ge2s$; $k$ is a lag); no $c$ in the
Deep Dive (§6's $c$ is the fraction of full Kelly); $T$ for every data sample's size (5, 246, 3,077, 4,382, 5,849), $n$
only for independent draws in a model. Not used: $L$, $P$, $\kappa$, $\beta$, $\mathcal L$, a star for a draw.

**Motivating case: "How wide is a Kelly fraction?"** (box, about 150 words)

> From 3 January 2003 to 8 October 2026 the TAIEX total-return index gave 5,849 daily returns [A22-01], with mean
> 0.062505% and standard deviation 1.2084% [A22-03]. With no risk-free rate its Sharpe ratio is 0.81 a year [A22-05]
> if days are uncorrelated, and its volatility is 18.96% a year [A22-07] ([[LM19]]). Its Kelly fraction
> $\hat f=\bar R/s^2$ is 4.28 [A22-06] ([[LM20]]). Draw the days again at random, 10,000 times, and recompute each
> number. Of the resampled Kelly fractions, 95% lie between 2.2 and 6.5 [A22-10], a range like [[LM4]]'s 2.7 to 7.6
> for 0050. Draw blocks of about 145 days instead [A22-08], which keep calm and turbulent stretches together. The Kelly
> range widens only to 1.8 to 7.1 [A22-13]. The volatility's range, 18.3% to 19.6% from single days [A22-11], becomes
> 16.5% to 21.5% [A22-14], almost four times as wide [A22-15]. Which range is an interval for the TAIEX, and why do
> clusters matter so much more for one number than for the other?

Resolved: (a) a range of resamples as an interval: §2 ((22.1), (22.2), E1, E2) and §3 (E3, X3, against LM20's delta
method); (b) why clusters matter: §4 (iid resamples have none: $\hat\rho_1(\lvert r\rvert)$ 0.161 against an iid range
of −0.025 to 0.026 [A22-22]; the error of a mean of squares depends on the autocorrelation of squares) and §5 (E5,
X5); (c) which block length: §6 (Politis–White gives 3.1 days on $R$ and 144.6 on squared returns [A22-08]; the
book's rule takes 145; X6); (d) the answer: the block intervals of X1, with the caveat that a block keeps no
dependence longer than itself (X6's volatility curve has not levelled off at 400 days). The exact optimum
$\hat f^*=4.14$ ([[LM17]]'s, [A22-06]) gets the same treatment in E3.

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | resampling as inference; case + X1; roadmap; notation and hygiene notes | 380 |
| 2 | The Bootstrap Principle {1} | the sampling distribution of $\hat\theta$ under $F$, approximated by the resamples' under $\hat F$ (13.12); the ideal bootstrap and $B$; (22.1); E1; (22.2) with the basic interval derived from the pivot $\hat\theta-\theta$ and the percentile interval justified in Deep Dive (a); BCa in two sentences; E2; conditions (iid, finite variance, a smooth statistic): stated without proof; pitfall: more resamples shrink Monte Carlo error, not sampling error; 導讀; KC | 620 |
| 3 | Intervals for the Sharpe Ratio and the Kelly Fraction {2} | E3, X2, X3; the iid bootstrap and LM20's delta method agree because both treat days as independent; the exact optimum; LM4's band and the relative error $1/(\widehat{\mathrm{SR}}\sqrt T)$; annualization's condition; $r_f=0$ against LM7's 1.5%; pitfall: an interval for the Kelly fraction is not a sizing rule ([[LM45]], [[LM34]]); KC | 500 |
| 4 | When Resampling Days Fails {3} | iid resamples have independent days by construction; $\Var(\bar x)=\frac{\sigma_x^2}{T}\big(1+2\sum_{k\ge1}(1-\tfrac kT)\rho_k\big)$ from LM19's (19.7): the mean of $R$ carries $R$'s small autocorrelations, the mean of $R^2$ the large autocorrelations of squares; E4, X4; [[LM23]] pointer; KC | 500 |
| 5 | Block Bootstraps {4} | moving blocks (Künsch 1989) and the stationary bootstrap (Politis and Romano 1994), (22.3); circular blocks in one sentence (moving blocks on a circle, so every day is equally likely; Lahiri 2003, §2.7.1); conditions: stationarity ([[LM25]] pointer), dependence that dies out, $\ell\to\infty$ and $\ell/T\to0$ (Künsch's abstract), stated without proof; X5; E5; X7; Deep Dive (b); pitfall: a block keeps no dependence longer than itself; 導讀; KC | 630 |
| 6 | Choosing the Block Length {5} | what Politis and White's estimate targets (the variance of a mean of the series given), stated; on $R$ and on squared returns; the book's rule, never called "the" right length; it is conservative for statistics driven by the mean (their SEs change by 8% and 14% between $\ell=3$ and 145 [A22-26]); E6; X6 (log $x$); the volatility curve that does not level off; KC | 450 |
| 7 | Intervals the Earlier Modules Left Open {6} | X8; E7 (LM16's crash gap); E8 (LM11's shares; percentile against basic under bias); E9 (LM18's windows; the basic interval outside [0, 1]); $\operatorname{VR}(20)$ from E4 in X8; [[LM25]] pointer; 導讀; KC | 620 |
| 8 | Bootstrap Tests {7} | resampling under the null; (22.4); E10 beside LM21's normal-reference p-values; the iid resamples of E4 as a null of independence; LM21's shuffled dates in one sentence; duality with (22.2); the four tests counted; 導讀; KC | 400 |
| 9 | Resampling in Python {8} | the NumPy stationary function (under 80 characters a line); arch draws the same indices from one generator; `optimal_block_length` and its column names; `scipy.stats.bootstrap` (`rng`, `batch`, BCa default, interpolated percentiles, divisor $B-1$); lab box; KC | 260 |
| — | Summary (8) / Problems (11) / Solutions | | 140 / 420 / 520 |
| | **Total** | | **5,440** |

**Elements.** 10 examples (E1, E2 §2; E3 §3; E4 §4; E5 §5; E6 §6; E7, E8, E9 §7; E10 §8). Knowledge checks:

- §2: "Why can more resamples not bring E1's bootstrap SE of the mean below 0.583%?" $B$ governs Monte Carlo error
  only: as $B\to\infty$ the estimate tends to the ideal $s/\sqrt5=0.583\%$ [A22-17]; sampling error falls only with a
  longer sample.
- §3: "TR23's iid Kelly interval has a half-width of about 50% of 4.28, and LM4's band for 0050 one of about 45% of
  5.42 [A22-16]. Why are the relative errors so close?" The relative SE of $\bar R/s^2$ is about
  $\operatorname{SE}(\bar R)/\bar R=1/(\widehat{\mathrm{SR}}\sqrt T)=25.3\%$ [A22-38] here and 26% for 0050
  (lm04.md:547); ±1.96 of them is about ±50%.
- §4: "Why do iid resamples give $\operatorname{VR}(20)$ near 1 whatever the data?" Resampled days are independent
  draws from $\hat F$, so their autocorrelations vanish in expectation and the 20-day sums have variance near
  $20s_r^2$: the resamples average 0.997 [A22-23].
- §5: "How many moving blocks of 145 days does a resample of 5,849 days need, and how many days are cut?"
  $\lceil5{,}849/145\rceil=41$ blocks, 5,945 days, 96 cut [A22-39].
- §6: "Politis and White give 3.1 days on $R$ and 144.6 on squared returns. Why does the Sharpe ratio's interval hardly
  care which is used?" Its error is almost all the error of $\bar R$, which depends on the small autocorrelations of
  $R$: in X6 its SE ratio is 1.05 at $\ell=3$ and 1.13 at 145 [A22-26].
- §7: "The 2017 and 2020 intervals of E8 do not overlap. Does that show that PC1's share changed?" Strong evidence of a
  change between those two years, but they were picked after looking as the extremes of 18 years [A22-40], so the
  comparison is the best of a search ([[LM21]]'s count of tests).
- §8: "Why does E10 resample $R_t-\bar R$ and not $R_t$?" To impose the null $\mu=0$. Resampling $R_t$ gives t-stats
  centred near 3.96, half of them above the observed one [A22-41]: the alternative's distribution, useless as a null.
- §9: "arch gets `seed=5`, or the generator `default_rng([5, 20261011])`: the same resamples?" No: arch turns an
  integer into `default_rng(5)` (`arch/bootstrap/base.py:401–402`), another stream. Pass the experiment's generator.

中文導讀 in §2 (自助重抽法 (bootstrap), 重抽樣 (resampling), 抽樣分布 (sampling distribution), 標準誤 (standard
error), 信賴區間 (confidence interval), 百分位數信賴區間 (percentile confidence interval), 基本信賴區間 (basic
interval), the book's own form (樂詞網 has no entry), and 樂詞網's 偏誤加速校正之自助重抽信賴區間 (BCa); the idea: $\hat F$
stands in for the unknown law, and $B$ only buys simulation accuracy), §5 (區塊自助重抽法 (block bootstrap),
平穩自助重抽法 (stationary bootstrap), 移動區塊 (moving block), 循環區塊 (circular block), 區塊長度 (block length), all
the book's own forms, since 樂詞網 has no entries (SOURCES), printed with their English; 波動群聚現象 (volatility
clustering), 自我相關 (autocorrelation), 波動率 (volatility); the idea: blocks carry calm and turbulent stretches
whole, so the volatility interval widens fourfold while the Kelly interval barely moves), §7 (偏誤 (bias), 變異數比
(variance ratio), 信賴區間; the idea: a skewed or biased bootstrap distribution separates the percentile and basic
intervals, and a bounded statistic needs the percentile one) and §8 (假設檢定 (hypothesis testing), 虛無假設 (null
hypothesis), p值 (p-value), 顯著水準 (significance level); the idea: resample a world where the null holds).

Deep Dives: (a) §2 "When the percentile interval is right". Its first sentence declares $\psi$, an increasing
function, and $\sigma_\psi$, a positive constant. If $\psi(\hat\theta)-\psi(\theta)$ and
$\psi(\hat\theta_{\text{boot}})-\psi(\hat\theta)$ are both $\mathcal N(0,\sigma_\psi^2)$, the percentile interval
equals $\psi^{-1}\big(\psi(\hat\theta)\pm\Phi^{-1}(1-\alpha/2)\,\sigma_\psi\big)$, an exact interval that needs neither
$\psi$ nor $\sigma_\psi$. The Deep Dive derives it; it is attributed to Wasserman (2004, §8.5.2) only after that
section is read (open point). (b) §5 "Every day is equally likely at every position": by induction over positions, a
stationary or circular resample's day at each position is uniform on the $T$ days (a uniform day shifted by one, with
wrap-around, is uniform), so $\E_{\hat F}\bar R_{\text{boot}}=\bar R$ for every $\ell$, as (18.8) for the iid case;
moving blocks cover day $t$ in $\min(t,\ell,T-\ell+1,T-t+1)$ of the $T-\ell+1$ blocks, so their resample mean averages
0.060185%, not $\bar R=0.062505\%$ [A22-49] (Problem 9).

**Exhibits.**

- X1 `case` (table, §1). Rows: Sharpe ratio, annualized; Kelly fraction $\hat f$; volatility, annualized. Columns:
  estimate; iid bootstrap 95% interval; stationary block bootstrap ($\ell=145$) 95% interval; width ratio. Values:
  0.81, 0.41 to 1.21, 0.37 to 1.27, 1.1; 4.28, 2.2 to 6.5, 1.8 to 7.1, 1.2; 18.96%, 18.3% to 19.6%, 16.5% to 21.5%,
  3.9 [A22-05] [A22-06] [A22-07] [A22-09]–[A22-15]. Note: TR23, 5,849 daily simple returns, $r_f=0$, $A=246.12$ (the
  Sharpe ratio annualized as if days were uncorrelated, Lo 2002); estimates [[LM19]]'s and [[LM20]]'s; percentile
  intervals of $B=10{,}000$ resamples, seeds `[2, 20261011]` (iid) and `[3, 20261011]` (stationary, mean block 145
  days); Monte Carlo SEs of the ends at most 0.008 (Sharpe), 0.04 (Kelly) and 0.03 points (volatility) [A22-15]; width
  ratios from unrounded ends. In-sample. Source: FinMind `TaiwanStockTotalReturnIndex` (TAIEX), retrieved 18 October
  2026. Computations: `data/lm22_numbers.py`.
- X2 `srhist` (`line`, §3): x the annualized Sharpe ratio, −0.25 to 1.95 (`fmt: "n2"`); y share of resamples per bin
  of 0.05 (`fmt: "pct1"`). Two `step` series: iid days (color 1), blocks of mean 145 days (color 2); dashed `vline`s
  at the percentile ends 0.41, 1.21 and 0.37, 1.27, a solid `vline` at 0.81. Shows that blocks widen the Sharpe
  ratio's distribution only a little (SE 0.205 against 0.233 [A22-09] [A22-12]).
- X3 `kelly` (`scatter`, forest plot, §3): y rows with `tickLabels` (top to bottom): "Delta method (LM20)", "iid,
  percentile", "iid, basic", "iid, BCa (SciPy)", "blocks, percentile", "blocks, basic", "exact optimum, iid",
  "exact optimum, blocks"; x the Kelly fraction, 0 to 8 (`fmt: "n1"`). Points at 4.28 (rows 1–6) and 4.14 (rows 7–8),
  solid `lines` from each lower to upper end, a dashed line at 4.28. Values: 2.10–6.46 [A22-20]; 2.2–6.5; 2.1–6.4
  [A22-10]; 2.2–6.5 [A22-20]; 1.8–7.1; 1.5–6.7 [A22-13]; 2.1–6.1; 1.8–6.6 [A22-21]. Note: TR23, $B=10{,}000$, seeds as
  X1; SciPy's BCa on experiment 2's own resamples; the delta method is [[LM20]]'s with plug-in skewness and kurtosis.
  Points and rows are one named series ("estimate"), as AUTHORING §7 asks.
- X4 `destroy` (`line`, §4): x $\hat\rho_1(\lvert r\rvert)$, −0.06 to 0.30 (`fmt: "n3"`); y share per bin of 0.005.
  Two `step` series: iid resamples, block resamples ($\ell=145$); a solid `vline` at the estimate 0.161; dashed ends
  −0.025, 0.026 and 0.10, 0.21 [A22-22]. Note: TR23 log returns, LM19's convention; none of the 10,000 iid resamples
  reaches 0.161.
- X5 `rollvol` (`line`, §5): x session 60 to 5,849 (`x.values` shared; thinned to every fifth session plus each
  series' maximum and minimum, about weekly, so no daily series is published); y the annualized 60-day volatility,
  0–50% (`fmt: "pct1"`, `tfmt: "pct0"`). Series: TR23, one iid resample, one block resample ($\ell=145$), both from
  experiment 7. Values: TR23 44.3% (window ending 2008-12-02) and 7.2% (ending 2014-07-29); iid 27.9% and 11.6%; block
  44.3% and 7.2% [A22-27]. Note: a session is the number of the window's last return, on a resampled path a position,
  not a date; the block resample copies whole stretches, its extremes included; the iid one flattens them. Model.
- X6 `ell` (`line`, §6): x mean block length $\ell$, `x.type: "log"`, values 1, 2, 3, 5, 10, 20, 50, 100, 145, 200,
  400; y bootstrap SE ÷ iid SE (`fmt: "n2"`), 0.8–5. Four series: Sharpe ratio, Kelly fraction, volatility,
  $\operatorname{VR}(20)$; `hline` 1; dashed `vline`s at 3.1 ("Politis–White on $R$") and 144.6 ("on squared
  returns"). Values: volatility 1.18, 3.91 and 4.63 at 2, 145 and 400; Sharpe ratio 1.13 at 145 (at most 1.15); Kelly
  1.22 at 145 (at most 1.24); $\operatorname{VR}(20)$ 0.93 at 145 [A22-26]. Note: $\ell=1$ (iid) and 145 from
  experiments 2 and 3 ($B=10{,}000$), the other lengths from experiment 4 ($B=2{,}000$ each); Monte Carlo SE of a
  ratio at most 2% ($B=2{,}000$) and about 1% at 145 [A22-26].
- X7 `methods` (table, §5; the one exhibit that prints moving and circular blocks): rows iid, moving blocks, circular
  blocks, stationary bootstrap (all $\ell=145$); columns volatility SE (points) and 95% interval, Kelly SE and
  interval, Sharpe SE. Values: 0.33, 18.3–19.6, 1.10, 2.2–6.5, 0.205; 1.12, 16.5–21.0, 1.45, 1.6–7.2, 0.247; 1.12,
  16.7–21.1, 1.41, 1.7–7.1, 0.244; 1.30, 16.5–21.5, 1.34, 1.8–7.1, 0.233 [A22-25]. Note: experiments 2, 5, 6 and 3.
- X8 `open` (table, §7): rows with their sample, estimate, method and $\ell$, bootstrap SE, 95% percentile interval:
  U28 pair, correlation on 223 big-move days, 0.788, stationary 130, 0.022, 0.75 to 0.84 [A22-28] [A22-30]; its gap to
  (16.10), −0.071, 0.016, −0.094 to −0.033; U28, PC1's share in 2017, 34.5%, stationary 7, 2.4 points, 30.1% to 39.4%
  [A22-31]; in 2020, 66.6%, stationary 18, 7.1 points, 49.6% to 75.9% (basic 57.3% to 83.7%) [A22-32]; TR23,
  windows under water, 4.1%, stationary 145, 9.9 points, 0.0% to 33.0%; their SD of $\ln G$, 0.283, 0.124, 0.20 to 0.68
  [A22-33] [A22-34]; TR23, $\operatorname{VR}(20)$, 1.036, stationary 145, 0.061, 0.92 to 1.16 [A22-23]. Note: U28
  rows are price indices (no dividends); $B=10{,}000$, seeds 9, 11, 13, 14, 3; in-sample.
- Sizes: X2 and X4 hold under 200 numbers each, X6 44, X5 about 4,700 (every fifth session) or 35 KB; the widget's
  block under 100 KB. Every spec stays far under 300 KB; X3 uses the approved scatter `tickLabels`, X5 the shared
  `x.values`, X6 the log $x$ axis.

**Widget `blockboot` — "Block-bootstrap explorer."** Per the editor's rule on daily series (X37), the widget embeds
precomputed histograms, not TR23's returns. `Book.controls`: statistic (select: Sharpe ratio annualized, Kelly
fraction $\hat f$, volatility annualized, $\hat\rho_1(\lvert r\rvert)$, $\operatorname{VR}(20)$); scheme and length
(slider over X6's grid: 1 means iid days, 2 to 400 the stationary bootstrap's mean block length); replicate (a "new
seed" button that steps through three precomputed replicates). Initial state (the PDF): volatility, $\ell=145$, first
replicate. Chart: a `step` histogram of the 1,000 resampled values (50 bins on a fixed range per statistic), a solid
`vline` at the estimate and dashed ones at the percentile ends; readouts: estimate, bootstrap SE (divisor $B$),
percentile and basic intervals, $\ell$ and the replicate. Data block `chart-lm22-widget`, written by
`data/lm22_charts.py` from experiment 24 (one generator; for each length of the grid in order, three replicates of
$B=1{,}000$ resamples of TR23): 5 statistics × 11 lengths × 3 replicates = 165 histograms with their readouts, under
100 KB, plus the five estimates. The widget draws nothing at run time, needs no `Book.rng`, `tInv` or Student-$t$
sampler, and its numbers are NumPy's, reproducible from the seed; the text quotes none of them.

**Examples** (results recomputed from the printed inputs):

- E1 §2, "The ideal bootstrap of five returns": LM18's Problem 4 returns +1.2%, −0.8%, +0.3%, −2.5%, +0.6%; mean
  −0.24%, $s=1.3032\%$ [A22-17]. All $5^5=3{,}125$ ordered resamples are equally likely: the SE of the mean is
  exactly $s/\sqrt5=0.583\%$ ((18.8)); the median, $\hat F^{-1}(\tfrac12)$ of the five draws, is the third smallest,
  equal to −2.5% or +1.2% with probability 181/3,125 each, −0.8% or +0.6% with 811/3,125, +0.3% with 1,141/3,125, so
  its ideal SE is 0.859% [A22-17]. With $B=1{,}000$ (seed `[1, 20261011]`): 0.59% ± 0.01 and 0.87% ± 0.02 (batch SEs)
  [A22-17], Monte Carlo error only.
- E2 §2, "An interval for TAIEX's Sharpe ratio": iid, $B=10{,}000$, seed 2: SE 0.205 a year, percentile 0.41 to 1.21,
  basic 0.41 to 1.21 [A22-09]; SciPy's BCa on the same resamples 0.42 to 1.22 [A22-19]. [[LM20]]'s delta-method SE is
  0.207 (plug-in skewness and kurtosis), 0.205 under normal returns, interval 0.40 to 1.22 [A22-18]. All agree: the
  daily ratio is small, so its SE is close to $1/\sqrt T=0.0131$ a day [A22-18].
- E3 §3, "The Kelly fraction and the exact optimum": iid, seed 2: $\hat f=4.28$, SE 1.10, percentile 2.2 to 6.5, basic
  2.1 to 6.4 [A22-10], BCa 2.2 to 6.5; [[LM20]]'s delta method: SE 1.111 (plug-in; 1.085 normal, 1.082 mean only),
  interval 2.10 to 6.46 [A22-20]. The exact optimum $\hat f^*=4.14$ (root of (4.5) in every resample): SE 1.03, 2.1 to
  6.1 [A22-21]. With blocks (seed 3, $\ell=145$): $\hat f$ 1.8 to 7.1 [A22-13], $\hat f^*$ 1.8 to 6.6 [A22-21].
  Relative error about $1/(\widehat{\mathrm{SR}}\sqrt T)=25\%$ [A22-38].
- E4 §4, "What resampling days cannot see": $\hat\rho_1(\lvert r\rvert)=0.161$ ([[LM19]]'s; LM17's pair correlation
  prints the same) [A22-22]. iid resamples (seed 2): mean −0.0001, 95% between −0.025 and 0.026, none of 10,000 at
  0.161; block resamples (seed 3): 0.10 to 0.21, mean 0.156 [A22-22]. $\operatorname{VR}(20)=1.036$ ([[LM19]]'s
  (19.8)): iid resamples average 0.997 and span 0.88 to 1.13, centred on independent days; blocks average 1.037 and
  span 0.92 to 1.16; the SE barely moves, 0.065 against 0.061 [A22-23].
- E5 §5, "TAIEX's volatility with blocks": [[LM20]]'s iid formula $\operatorname{SE}(s)\approx
  s\sqrt{(\operatorname{Kurt}-1)/(4T)}$ gives 0.33 points a year, the iid bootstrap 0.33, stationary blocks 1.30:
  3.9 times, a relative SE of 6.84% against 1.75% [A22-24]; interval 16.5% to 21.5% [A22-14]. Moving and circular
  blocks give SEs of 1.12 points (X7) [A22-25].
- E6 §6, "A block length for TR23": `optimal_block_length` gives 3.07 (stationary) and 3.51 (circular) on $R$, 144.59
  and 165.52 on $(R-\bar R)^2$, 144.02 on $(r-\bar r)^2$; its cap is 230 [A22-08]. The book's rule takes the
  stationary estimate on the squared demeaned simple returns, 144.59, rounded: 145 for every TR23 statistic, on $R$ or
  on $r$ (one length per sample, so $\operatorname{VR}(20)$ and $\hat\rho_1(\lvert r\rvert)$ use 145 too). X6: the
  volatility's SE ratio is 1.18 at $\ell=2$, 3.91 at 145 and 4.63 at 400, still rising; the Sharpe ratio's stays at or
  below 1.15 [A22-26].
- E7 §7, "Is the crash correlation below the model's by chance?": U28 pair, 223 days with $\lvert R_t-\bar R\rvert\ge2s$
  for Semiconductor; data 0.788 (each return centred at its event-day mean), (16.10) at LM16's $\hat\rho=0.5749$ gives
  0.860, gap −0.071 [A22-28]. Each resample re-standardizes, reselects its days (182 to 255) and recomputes both.
  Stationary $\ell=130$ (Politis–White 53.3 and 130.0 on the two squared series), seed 9: data correlation 0.75 to
  0.84; gap SE 0.016, −0.094 to −0.033, none of 10,000 at or above 0 [A22-30]. iid (seed 8): gap −0.102 to −0.037
  [A22-29]. The interval excludes 0: at the 5% level the correlation on big-move days is below the normal model's, not
  above it.
- E8 §7, "PC1's share from about 250 returns": 2017, 246 returns, 34.5%: $\ell=7$ (the largest Politis–White estimate
  over the 28 sectors' squares, 6.79), seed 11: SE 2.4 points, 30.1% to 39.4% (iid, seed 10: 30.7% to 38.9%)
  [A22-31]. 2020, 245 returns, 66.6%: $\ell=18$ (18.38), seed 13: SE 7.1 points, percentile 49.6% to 75.9%, basic
  57.3% to 83.7%, resample mean 65.0% (bias −1.7 points); iid (seed 12): 58.6% to 72.8% [A22-32]. The two years'
  intervals do not overlap; in 2020 the percentile and basic intervals part because the resampled shares are skewed and
  biased down.
- E9 §7, "The error of LM18's windows": 191 of 4,619 windows of 1,231 sessions under water (4.1%, counted exactly) and
  their SD of $\ln G$, 0.283, against $\sqrt m\,s_r=0.425$ [A22-33]. Stationary $\ell=145$, seed 14: the share has SE
  9.9 points and percentile interval 0.0% to 33.0%, 3,248 of 10,000 resamples have no window under water, and the basic
  interval runs to −24.7%; the SD of $\ln G$ has SE 0.124, interval 0.20 to 0.68, resample mean 0.386 [A22-34]. iid
  (seed 15): SE 8.4 points; SD interval 0.19 to 0.58 [A22-35]. Blocks of 145 days cannot keep swings that last years,
  which is why the resamples' SD sits above the windows' 0.283 ([[LM19]]'s variance ratios below 1 beyond a year).
- E10 §8, "A bootstrap test of the mean": 7% regime, 3,077 returns, t-stat 2.05 with two-sided p-value 0.041 against
  the standard normal ([[LM21]]'s) [A22-36]. The bootstrap's reference distribution is instead the resampled t-stats
  under the null, two-sided: resampling $R_t-\bar R$ iid (seed 16), 408 of 10,000 at or beyond $\lvert2.05\rvert$,
  0.041 ± 0.002, beside LM21's 0.041; stationary $\ell=108$ (seed 17), 477, 0.048 ± 0.002, its t-stats with SD 1.03
  against 1.01 for iid [A22-36]. Full sample: t-stat 3.96, normal p-value $7.6\times10^{-5}$ ([[LM21]]'s); blocks of
  145 (seed 18): none of 10,000, so below $1/B=0.0001$ at this $B$ [A22-37].

**Problems plan** (11; MC keys A, B, C, B, C; the lab solves 6, 10, 11). Stems state the sample (TR23, 3 January 2003
→ 8 October 2026, $T=5{,}849$; U28 with "price indices"), the divisor ($T$; $B$ for a bootstrap SE), $A=246.12$, the
interval type and level, the resampling scheme and $\ell$, $B$ and the seed, and the rounding.

1. MC: three daily returns +1%, −2%, +4%; the ideal bootstrap SE of their mean (all 27 resamples). **A** 1.414%
   ($s/\sqrt3$, divisor 3). B 1.732% ($s_{\mathrm u}/\sqrt3$: $\hat F$ divides by $T$). C 0.816% ($s/3$, no root)
   [A22-43].
2. MC: $B=10{,}000$; the ranks of a 95% percentile interval's ends. A the 500th and 9,500th (a 90% interval: $\alpha$
   not halved). **B** the 250th and 9,750th. C the estimate ± 1.96 bootstrap SEs (a normal interval, not a percentile
   one) [A22-44].
3. MC: 2020's PC1 share 66.62%, block resamples' percentile interval 49.55% to 75.92%, SE 7.11 points; the basic
   interval is *closest* to: A 49.6% to 75.9% (the percentile interval). B 52.7% to 80.6% (estimate ± 1.96 SE). **C**
   57.3% to 83.7% [A22-45].
4. MC: iid resamples of TR23 give $\hat\rho_1(\lvert r\rvert)$ between −0.025 and 0.026 against the estimate 0.161.
   A the estimate is an outlier of the sample (the resamples cannot see order). **B** the resamples describe
   independent days, so the range is a null distribution that 0.161 rejects. C the bias is −0.161, so the basic
   interval 0.295 to 0.346 corrects it (a bias estimate is meaningless when the resampling destroys what is measured)
   [A22-22].
5. MC: a stationary bootstrap with $\ell=145$ on $T=5{,}849$; the probability that a given position after the first
   starts a new block. A 0.9931 (the probability of continuing). B 0.0248 ($\ell/T$). **C** 0.0069 [A22-46].
6. Stationary bootstrap, $\ell=145$, $T=5{,}849$: (a) the expected number of blocks, $1+5{,}848/145=41.3$; (b) the
   chance that a block runs 60 days or more, $(1-1/145)^{59}=0.665$; (c) the share of adjacent resampled pairs that are
   adjacent in TR23, about $1-1/\ell$, and the predicted mean $\hat\rho_1(\lvert r\rvert)$ of the resamples, about 0.16
   at $\ell=145$ and 0.080 at $\ell=2$, against 0.156 (E4) and 0.078 (seed 21, $B=2{,}000$, batch SE 0.0005) [A22-47].
7. TR23's 7% regime, null: mean zero, two-sided, 5% level, stationary blocks with $\ell=108$, $B=10{,}000$, seed 17.
   The test finds 477 of 10,000 resampled $\lvert\text{t-stat}\rvert$ at or above the observed 2.05: (a)
   the bootstrap p-value and its Monte Carlo SE, 0.0477 ± 0.0021; (b) the decision at the 5% level, and why
   $0.0477+2\times0.0021=0.052$ makes it fragile; (c) the $B$ that brings the Monte Carlo SE to 0.001, about 45,000
   [A22-48].
8. LM18's windows: the block percentile interval for the share under water is 0.0% to 33.0% and the basic interval
   −24.7% to 8.3% [A22-34]. Explain why the basic interval fails here, why a third of the resamples have no window
   under water, and why the resampled SD of $\ln G$ averages 0.386, not 0.283.
9. Prove that every position of a stationary resample is uniform on the $T$ days, so $\E_{\hat F}\bar R_{\text{boot}}=
   \bar R$ for every $\ell$; then count how many of the $T-\ell+1$ moving blocks of 145 days contain day 1 and day 145,
   and evaluate the moving blocks' expected resample mean on TR23, 0.060185% against 0.062505% (−0.23 bp, −3.7%)
   [A22-49].
10. *(Python)* Write the stationary bootstrap's index function; check that arch's `StationaryBootstrap(145, R,
    seed=rng)` draws the same indices from a twin generator (seed `[20, 20261011]`, three resamples) [A22-42]; then
    re-create seed `[3, 20261011]` and reproduce X1's volatility interval 16.5% to 21.5% [A22-14].
11. *(Python, stability check)* TR23's 10% regime (2,772 returns from 1 June 2015): $\hat f=6.06$; the book's rule
    gives $\ell=36$; iid (seed 22) 2.8 to 9.6, blocks (seed 23) 2.6 to 10.1, $B=10{,}000$ [A22-50]. Compare with the
    full sample's 2.2 to 6.5, and say why two regimes' intervals overlap so much.

**Lab parts** (`build/make_lab22.py`; reads only its `data/`: `taiex_tr.csv` for TR23, and `sectors_close_raw.csv` with
`sectors_close_repairs.csv` for U28, rebuilt with LM16's repair cell; `data/make_lab_data.py` gets them as it does for
LM13–LM18 and LM16, `"LM22_lab": {**tr23, **sectors}`): 1 data, $T$, $A$, the moments, the regimes, U28
and the pair; 2 E1 by enumeration and with $B=1{,}000$; 3 iid resamples of TR23 (E2, E3, X2, X3) and the SciPy check
with stream 2 re-created; 4 E4, X4; 5 the three block functions, the arch check, E5, X5, X7; 6 `optimal_block_length`,
the rule, X6 (with $B=2{,}000$ per length); 7 E7, E8, E9 and X8; 8 E10; 9 Problems 6, 10 and 11. Extension (stability
check, `make_lab16.py:571`'s question): the pair's correlation in the two limit regimes of U28 (1,610 and 2,772 returns;
0.6544 and 0.5564 in LM16's lab) with block-bootstrap intervals for each and for their difference; the lab prints its
own numbers and says that two intervals are a stability check, not a test on later data. The lab takes several minutes
(the exact optimum in 10,000 resamples); its first markdown cell says so.

**Cross-module tags.**

- (22.1) $\widehat{\operatorname{SE}}_{\text{boot}}=\big(\frac1B\sum_{i=1}^B(\hat\theta_{\text{boot},i}-
  \bar\theta_{\text{boot}})^2\big)^{1/2}$; the resamples drawn from the resampling model (iid from $\hat F$, or
  blocks); tends to the ideal bootstrap SE as $B\to\infty$ by the strong law (lm18.md:140–143) (LM33, LM45).
- (22.2) the $1-\alpha$ percentile interval $\big[\hat F_{\text{boot}}^{-1}(\tfrac\alpha2),\hat F_{\text{boot}}^{-1}
  (1-\tfrac\alpha2)\big]$ and basic interval $\big[2\hat\theta-\hat F_{\text{boot}}^{-1}(1-\tfrac\alpha2),\,2\hat\theta-
  \hat F_{\text{boot}}^{-1}(\tfrac\alpha2)\big]$, with $\hat F_{\text{boot}}^{-1}(u)=\hat\theta_{\text{boot},(\lceil
  uB\rceil)}$; approximate, under the bootstrap's consistency (stated without proof; its reference waits for a source,
  "Open before Stage 2") (LM33, LM34, LM45).
- (22.3) the stationary bootstrap: a new block at each position after the first with probability $1/\ell$, otherwise
  the next day (day $T$ followed by day 1); $\Pr(\text{a block lasts at least }j\text{ days})=(1-1/\ell)^{j-1}$, mean
  length $\ell$; every position uniform on the $T$ days (LM33, LM45).
- (22.4) the bootstrap p-value of a mean, $\frac1B\#\{i:\lvert\text{t-stat}_{\text{boot},i}\rvert\ge\lvert
  \text{t-stat}\rvert\}$, the resamples drawn from $R_t-\bar R$ (the null imposed) with the scheme stated; its Monte
  Carlo SE $\sqrt{p(1-p)/B}$ written in words (LM34).

**Pitfalls to pre-empt.**

- $B$ against $T$: more resamples shrink Monte Carlo error only (E1, KC §2); print the batch SE beside every
  bootstrap number and keep only the digits it supports (X1's ends: two decimals for the Sharpe ratio, one for the
  Kelly fraction and the volatility).
- The iid bootstrap is a model of independent days: it cannot measure the error of a statistic of dependence
  ($\hat\rho_1(\lvert r\rvert)$, $\operatorname{VR}$), and it understates the error of a statistic of squares fourfold
  on TR23 (E4, E5).
- A block keeps nothing longer than itself: X6's volatility curve still rises at 400 days, and the windows' SD (E9)
  depends on swings of years; say so, and never call 145 "the" right length.
- Percentile against basic: the basic interval reflects the resampled distribution about the estimate and can leave the
  statistic's range (E9's −24.7%); the percentile interval stays inside but inherits bias (E8's 2020).
- SciPy differs from the book in three places: the percentile ends interpolate (`stats.quantile`, `method='linear'`;
  0.4157 against the book's $\hat F^{-1}$ end 0.4147 [A22-19]), `standard_error` divides by $B-1$, and the default is
  BCa with 9,999 resamples. Pass `method="percentile"`, the generator as `rng`, and `batch=500` to draw the book's
  resamples.
- arch's `optimal_block_length` returns columns `stationary` and `circular` in arch 8.0.0
  (`arch/bootstrap/base.py:202`), although its docstring names `b_sb` and `b_cb` (base.py:139); select by position or
  by the real names.
- The 7% regime test and E8's two years are selected comparisons; count them ([[LM21]]).
- Mixing regimes: every resample mixes the 7% and 10% limit regimes (lm18.md:389); Problem 11 and the lab's extension
  are the stability checks.
- Sharpe annualization needs uncorrelated days (Lo 2002); the interval for $\sqrt A\,\widehat{\mathrm{SR}}$ is the daily
  interval times $\sqrt A$, nothing more.
- Divisors: $s$ with $T$ everywhere except the t-stat's $s_{\mathrm u}$; LM18's bootstrap SE with $B$.
- Ownership: TR23's moments are [[LM14]]'s; the Sharpe ratio, the volatility, $\hat\rho_1(\lvert r\rvert)$ and
  $\operatorname{VR}(20)$ [[LM19]]'s; $\hat f$ and the delta-method standard errors and intervals [[LM20]]'s; the
  t-stats and their normal p-values [[LM21]]'s; $\hat f^*$ [[LM17]]'s. LM22's own are the bootstrap intervals, SEs and
  p-values.
- References (SOURCES): Künsch (1989) and Politis and Romano (1994) from their abstracts; Politis and White (2004) with
  Patton, Politis and White (2009) for the automatic length, as arch's docstring cites them; Lahiri (2003) §2.5, §2.7.1,
  §2.7.2, ch. 7 (contents verified); Efron and Tibshirani (1993) ch. 6 (§6.2, (6.6) verified), ch. 13 (chapter title
  verified) and ch. 16 (number inferred), cited by chapter until the sections are read; Efron (1987) for BCa
  (abstract); Ledoit and Wolf (2008), Lo (2002) one sentence each. Wasserman (2004) §8.3 and §8.5.2 are cited only after
  their content is read; until then Deep Dive (a) is derived without attribution and (22.2)'s consistency is stated
  without proof.

**Stage 4 for earlier modules** (in the plan's Stage 4 table).

- Leads gain 22 in lm04.md:6 (LM22 cites (4.3)–(4.5) and the band), lm11.md:6 (lm11.md:406 already links [[LM22]]),
  lm13.md:6 (LM22 cites (13.12)) and lm14.md:6 (LM22 cites (14.5) and the quantile function). lm16.md, lm17.md and
  lm18.md already list 22.
- `build/make_lab11.py:571` ("[[LM20]] gives the tools to answer"): "LM20 and LM22 give the tools; LM22 answers it for
  2017 and 2020", plain text (the literal `[[LM20]]` is already on the Stage 4 list).
- `build/make_lab04.py:642`: "LM22 (bootstrap intervals for the Kelly fraction), LM34 (walk-forward tests) and LM45
  (Kelly under uncertainty) return to this question."
- lm18.md:366 keeps "none here ([[LM22]])": LM22's E9 supplies the value.

**Open before Stage 2** (sources still to read, X34; until then the text follows the decisions): a source for the iid
bootstrap's consistency ((22.2) and §2 say *stated without proof*); the content of Wasserman's §8.3 and §8.5.2 (Deep
Dive (a) is derived without attribution); Efron and Tibshirani's BCa and moving-block sections (cited by chapter);
Politis and Romano (1992), the circular bootstrap's original (Lahiri §2.7.1 cited instead).

## LM23 Linear Regression

Stage 1 brief, revised 2026-10-19 after the cross-check and the independent recomputation. Drafted from the editor's
spine (`plans/vol-4.md` at commit bcfa0d4, "### LM23 Linear Regression"); revised to the editor's decisions
(`plans/vol-4.md`, "Editor's decisions on the LM19–LM25 drafts"), the cross-check's findings X6, X11, X17, X22, X27,
X32, X34, X35, X37, X39, X40 and its §8, the recomputation's items 2a–2h and 3, and the fresh check. Every number
carries its anchor ID at first appearance; `data/vol4_anchors_lm23.py` prints them all (58 rows, `## LM23` of
`plans/vol-4-anchors.md`). Numbers quoted from published modules carry their file:line instead.

**Prereq:** `[2, 6, 8, 9, 10, 11, 12, 15, 16, 17, 18, 19, 20, 21, 22]`. What each supplies:

- LM2: the 00631L-on-0050 slope 1.887 over 2,902 total-return pairs, correlation 0.974, yearly 1.717 (2024) to 1.984
  (2021), unadjusted closes 0.846 (lm02.md:492–496, [[eg:etf]] there); the two halt pairs (lm02.md:494).
- LM6: the risk-free proxy $r_f=2\%$ (lm06.md:585); $q$ as a continuous dividend yield ((6.22), lm06.md:523).
- LM8: the hedged book and its line-by-line P&L, TX at $200F_t$ NT\$ a contract (lm08.md:104–112), the convention E6
  and problem 9 use for contract counts; the promise that LM23 sizes hedges by regression (lm08.md:112).
- LM9: rank and full column rank; the exact square fits that carry no evidence (lm09.md:406–412).
- LM10: $X^{\top}X$ positive definite at full column rank (cited by LM12's proof, lm12.md:101); $\hat\Sigma$ with divisor
  $T$, (10.2).
- LM11: PCA chooses directions, nothing makes PC2 "electronics" (lm11.md:309); PC2 across the halves,
  $\lvert\cos\theta_2\rvert=0.297$ (lm11.md:387); the halves (2,191 returns each).
- LM12: (12.1) normal equations, (12.2) $\Pi$ with $\operatorname{tr}\Pi=N$, (12.3) slopes from covariances and
  $\hat\alpha=\bar y-\bar{\mathbf R}^{\top}\hat{\boldsymbol\beta}$, (12.4) R-squared $=\cos^2\theta$, (12.6) the squared
  condition number (lm12.md:89, 108, 120, 126, 262); the four-point line [[eg:line4]] (lm12.md:130); December 2008, 22
  returns and 29 columns, rank 22 (lm12.md:296–322); the slope 0.4591 and residual SD 0.996% (lm12.md:436); the
  Cholesky slope −0.0709 of 00679B on 0050 (lm12.md:604); R-squared 0.99912 from an accounting identity
  (lm12.md:19–20, 169).
- LM15: the $t_\nu$ density (15.9) (lm15.md:300), for the $t_{T-d}$ law of a t-stat under normal errors.
- LM16: (16.2) covariance, (16.3) the sum rule, (16.4) $\Cov(M\mathbf X+\mathbf b)=M\Sigma M^{\top}$ (lm16.md:220),
  (16.6) the variance split, (16.7) normal linear maps, (16.8) the conditional law and its $\beta=\sigma_{XY}/\sigma_X^2$
  (lm16.md:340–348); the example slope 0.4591 (lm16.md:354–355).
- LM17: (17.1) and (17.5), the reason a slope's error falls like $1/\sqrt T$ and is approximately normal (lm17.md:69,
  276).
- LM18: the batch standard error (lm18.md:153) and its slope of $G$ on $\ln G$, $\hat\beta=2.18$, batch SE 0.01,
  exact 2.1584 (lm18.md:286), on the paths of experiment 3 (lm18.md:155).
- LM19 (brief above): (19.5) $\hat\rho_k$ and its convention (full-sample mean, divisor $T$ in numerator and
  denominator), used for the overlap residuals of §5; (19.7), whose $\Var r_t^{(m)}/m$ tends to the long-run variance
  of §5 as $m$ grows; annualization (a mean times $A$).
- LM20 (brief above): estimator, bias, consistency; (20.2) $\operatorname{SE}$; (20.3) $s_{\mathrm u}$; (20.4)
  intervals; (20.5) the normal MLE divides by $T$.
- LM21 (brief above): $H_0$, $H_1$, size; the one-sample t-test (21.1) and its p-value (21.2); family-wise error and
  Bonferroni (21.6), Holm (21.7), the false discovery rate and Benjamini–Hochberg (21.8); the rule that every test reports how many tests ran on the same data.
- LM22 (brief above): the block bootstrap, named once as the resampling alternative to HAC.

**Leads:** `[25, 26, 27, 30, 33, 34]` (X6: LM24 cites LM23 by a pointer only): LM25 (OLS for AR and Dickey–Fuller
regressions, spurious regression, (23.1)–(23.4), (23.6)), LM26 (auxiliary regressions, the ARCH test and
Mincer–Zarnowitz, (23.1), (23.4), (23.6); HC0, and Newey–West for loss differences, (23.7), with the lag rule), LM27
and LM30 (factor risk, (23.8)), LM33 (HAC for a Sharpe ratio, (23.7)), LM34 (data snooping, pointed to from §7 and the
lab).

**Forward links honoured.**

| Earlier text | Promise | Kept in |
|:--|:--|:--|
| lm02.md:492–496 | 00631L's slope 1.887 "estimates an average daily elasticity ([[LM23]] treats regression)" | §6, E7: SE by three methods, the designed 2 rejected, the yearly spread against its SEs |
| lm08.md:112 | "[[LM23]] sizes hedges by regression" | §6, E6: hedge ratio $=\beta$, variance reduction = R-squared, out of sample on the halves |
| lm09.md:412 | "Fitting over hundreds of days is a regression ([[LM23]])" | §2: the model, $T-d$ degrees of freedom; KC §2 (an exact fit has no error estimate) |
| lm11.md:309 | an economic factor model names its factors in advance and estimates exposures by regression | §8, E9: the electronics excess return named in advance; cosine of the halves' loadings against PC2's 0.297 (lm11.md:387) |
| lm12.md:124 | R-squared "as a statistic" | §3: its sampling behaviour, adjusted R-squared, the F test; it describes, it does not test |
| lm16.md:348, 354–355 | "its standard error is [[LM23]]'s": $\beta=0.4591$, residual SD 0.996% | KC §4 (three SEs, HAC interval); §2 (divisor $T-d$ against $T$) |
| lm18.md:153, 286 | the variance of a slope falls like $1/n$ ("[[LM23]] for a slope"); batch SE 0.01 | §2 ($\sigma_\varepsilon^2/(Ts_x^2)$); §4, E4: classical, White, the model's exact value and the batch value on LM18's own paths |
| lm12.md:19–20, 169, 604 | stay consistent | §2 cites (12.1)–(12.4) and LM12's design $(\mathbf 1\ X)$ as LM23's $X$; §8 the accounting identity; no recomputation of LM12's numbers |

The grep of `src/lm*.md`, `src/pages/*.md` and `build/make_lab*.py` for "LM23" finds exactly the seven lines above
(lm02:492, lm08:112, lm09:412, lm11:309, lm12:124, lm16:348, lm18:153); the spine missed none. lm18.md:286 has no
pointer but holds the number lm18.md:153 promises to explain; it is added here.

**Outcomes** ("After this module you should be able to:"):

1. write the linear regression model in matrix form, compute OLS estimates, residuals and $s_\varepsilon^2=\text{RSS}/(T-d)$, and state the assumptions under which OLS is unbiased and best among linear unbiased estimators
2. compute standard errors, t-stats, confidence intervals and prediction intervals for a regression, identify days with large hat values, and interpret R-squared as a statistic
3. explain why heteroskedastic or autocorrelated errors invalidate the classical standard errors, and compute White and Newey–West standard errors, choosing the lag and checking its effect
4. estimate a market model for a sector index, interpret its beta and intercept, and explain why a raw-return intercept on price indices is not Jensen's alpha
5. size a hedge by regression, and judge a beta's stability across halves, calendar years and rolling windows
6. test 28 sector alphas with Bonferroni, Holm and Benjamini–Hochberg, and explain how correlation across sectors changes the count of false positives
7. estimate a factor model with a factor named in advance, and diagnose the collinearity it brings
8. compute OLS with classical and robust standard errors in NumPy, and check them against statsmodels with every option passed explicitly

**Owns.** The linear model $\mathbf y=X\boldsymbol\beta+\boldsymbol\varepsilon$ and OLS in matrix form (23.1), citing
LM12's projection; the assumptions (linearity, full column rank, $\E[\boldsymbol\varepsilon\mid X]=\mathbf 0$,
$\Var(\boldsymbol\varepsilon\mid X)=\sigma_\varepsilon^2I$, optional normality); unbiasedness and
$\Var(\hat{\boldsymbol\beta}\mid X)=\sigma_\varepsilon^2(X^{\top}X)^{-1}$ (23.2) from (16.4); $s_\varepsilon^2$ (23.3)
and its unbiasedness via $\operatorname{tr}(I-\Pi)=T-d$; Gauss–Markov for linear unbiased estimators only, proved in a
Deep Dive and cited at chapter level (Hayashi §1.3 or Greene ch. 4, X32); t-stats and intervals (23.4), the $t_{T-d}$
law under normal errors *stated without proof* (X32: Blitzstein and Hwang do not state it, and Hayashi and Greene are
unchecked), the normal approximation for large $T$; confidence and prediction intervals for a fitted value and the
hat value (23.5); R-squared as a statistic, adjusted R-squared and the F test in one sentence each; the sandwich (23.6)
and White's estimator (HC0); the long-run variance and Newey–West (23.7) with Bartlett weights, the book's lag rule
(statsmodels' default HAC lag, which is Newey and West's (1994) pilot lag, not their recommended lag; X11) and
`use_correction`; overlapping $m$-day
sums and their MA($m-1$) residuals; a lag curve that does not level off as the signature of a drifting beta; the
market model, beta and alpha; the CAPM's statement; Jensen's alpha and the decomposition (23.8) of a raw-return
intercept on price indices ($r_f$ and dividend yields); U28's 28 betas and alphas with three SE methods; their
stability (halves, years, rolling 250 returns); a hedge ratio by regression, in and out of sample; the 28 alphas under
LM21's corrections, with their correlation across sectors (experiment 1); the factor model with the constructed
electronics factor, collinearity and the variance inflation factor (23.9). Values owned: every A23 anchor except the
recomputed numbers of LM2, LM16 and LM18, which are cited to their modules, and TX23's settlement price (LM25's
sample), one input of E6.

**Leaves.** Regression on nonstationary series and spurious regression, AR estimation by OLS, the Dickey–Fuller
regression → LM25. LM26's auxiliary regressions (ARCH test, Mincer–Zarnowitz) → LM26. Factor risk in portfolios → LM27
(bookkeeping) and LM30 (estimation). The Sharpe ratio's standard error under non-iid returns (HAC, Lo 2002) → LM33.
Data snooping beyond LM21's corrections (reality check) → LM34. Shrinking betas toward 1, a joint test of all 28
alphas, cross-sectional asset-pricing tests (Fama and MacBeth 1973), lagged-market betas for slow sectors → not in the
book, one sentence each. Bootstrap standard errors of a beta → LM22's tools, one sentence.

**Uses before taught** (one sentence each in the text):

- §2 pitfall: "Regressing one trending price series on another can show a strong fit with no relation at all; [[LM25]]
  treats spurious regression, and LM23 regresses returns."
- §4: "Variance that changes from day to day is what [[LM26]] models; White's standard errors need no model of it."
- §5: "Newey–West needs the products $\varepsilon_t\mathbf x_t$ to be stationary with fading dependence; [[LM25]] defines
  stationarity."
- §7: "Searching many sectors, rules or windows and keeping the best is the data snooping that [[LM34]] treats."
- §8: "Factor risk in a portfolio is [[LM27]]'s bookkeeping and [[LM30]]'s estimation problem."

**Data role.**

- **U28** (Volume II): `data/lm10_series.py`'s `u28()` reads `data/processed/vol2_closes.parquet` (built and repaired
  by `data/vol2_series.py`; FinMind `TaiwanStockPrice`, retrieved 11 October 2026, copied closes repaired from the
  13:30:00 values of `TaiwanStockEvery5SecondsIndex`). The 28 leaf sector price indices and the TAIEX price index,
  closes 2008-12-01 → 2026-10-08, $T=4{,}382$ simple daily returns 2008-12-02 → 2026-10-08 [A23-01]; 17.8508 years,
  $A=245.4794$ [A23-02]. Halves (LM11's): 2,191 returns each, 2008-12-02 → 2017-10-06 and 2017-10-11 → 2026-10-08
  [A23-03]. Calendar years: 2008 holds 22 December returns; it is no widget window, and X4's yearly fits fit it on its
  own; 2009–2025 hold 239 to 251 returns, 2025 holds 243 and 2026 185; the last 250 returns run 2025-09-25 → 2026-10-08
  [A23-05]. Price indices, no dividends: every caption says so, and every alpha says that it includes the
  dividend-yield gap (§6).
- **Electronic** (aggregate outside U28, same parquet, same dates, no missing close; *constructed* factor
  $R_{\text{el},t}-R_{\text{mkt},t}$) [A23-06].
- **LM2's sample**: `data/processed/etf_daily_returns.parquet`, 2,902 common-date total-return pairs of 0050 and
  00631L, 2014-11-03 → 2026-10-08 [A23-07], recomputed under LM23's name (`plans/vol-4.md`, "Data", recorded uses of
  earlier samples).
- **TR23 file on U28's dates**: `data/processed/vol3_taiex.parquet`; its price-index return `Rp` equals U28's TAIEX
  return on all 4,382 dates, so $q_{\text{mkt}}=A\cdot\overline{(R-R_p)}=3.46\%$ a year, the TAIEX's dividend yield
  over U28's window (total return 20.23-fold against 10.91-fold) [A23-08]. One statistic of one file, labelled
  "TAIEX total-return and price indices, U28 dates".
- **TX23** (Volume IV, LM25's sample; `data/vol4_series.py` → `data/processed/vol4_tx23.parquet`): one value, the
  settlement price $F_t=49{,}357$ of the contract held from the close of 8 October 2026 (202610), for E6's contract
  count at $200F_t$ NT\$ a contract (LM8's convention) [A23-36].
- **LM18's model paths** (E4): $r_t=\ln(1+R_t)$ of TR23, $\bar r$ and $s_r$ (divisor $T$), $m=1{,}231$, 10,000 paths
  drawn as LM18 drew them, `default_rng([3, 20261011])`, 20 chunks of 500 [A23-25]; LM18's experiment, LM18's seed.
- **Conventions.** One-day regressions on simple returns; 20-day sums on log returns, so labelled. OLS with an intercept;
  $d$ coefficients; $s_\varepsilon^2=\text{RSS}/(T-d)$; descriptive $s$, $s_x$, correlations with divisor $T$
  (`ddof=0`, passed explicitly). Classical SE $s_\varepsilon^2(X^{\top}X)^{-1}$; White's HC0 without a
  degrees-of-freedom factor; Newey–West with Bartlett weights $1-k/(\ell+1)$ and the book's lag rule
  $\ell=\lfloor4(T/100)^{2/9}\rfloor$, which the text calls statsmodels' default HAC lag and Newey and West's (1994)
  pilot lag, not their recommended lag (X11; SOURCES, "LM23 (added)"): 9 at 4,382, 8 at 2,902, 7 at 2,191, 4 for a
  year or 250 returns [A23-04]; no small-sample correction. Normal reference for every t-stat and p-value
  (two-sided), since $T-d\ge241$ ($t_{4380}$ and $t_{241}$ quantiles 1.9605 and 1.9699 against 1.9600 [A23-19]); E1
  alone uses $t_2$. Every t-stat names its method (classical, White or HAC). Sample autocorrelations are LM19's
  $\hat\rho_k$; sample quantiles are $\hat F^{-1}(u)$ (`inverted_cdf`). An intercept prints in bp a day and as $A$
  times that a year.
- **Guard and exact checks.** Counts against a threshold use `x <= c + 1e-12` and `|t| > c + 1e-12`; TAIEX's
  7 April 2025 return is checked to be the exact sample minimum, and the two 2025 days at or below −5% are counted, with
  `Fraction` on the two-decimal closes [A23-23].
- **Seeds.** One LM23 experiment: $e=1$, the correlated null of 28 alpha t-stats, `default_rng([1, 20261011])`,
  100,000 draws [A23-43]; its Monte Carlo SEs are the binomial $\sqrt{p(1-p)/B}$ for a proportion and SD÷$\sqrt B$ for
  the mean count. LM18's paths keep LM18's experiment 3 seed and its batch SE (20 batches, divisor 20). No widget
  simulates.
- **Published files** (plan, X37). No file carries a daily series in date order: X2 stores its 243 points sorted by
  the TAIEX return, without dates (only the labelled 7 April 2025 point is named); X8 is thinned to weekly windows plus
  the cited extremes; the widget embeds per-window statistics only.
- **Scripts.** `data/lm23_numbers.py` (every printed value, asserted against `src/lm23.md`; compares with the anchors;
  flags rounding boundaries), `data/lm23_charts.py` (X2–X4, X6, X8 and the widget block); both after
  `data/vol2_series.py`, `data/vol3_series.py` and `data/lm10_series.py`.

**Hygiene declaration.** *In-sample:* every regression, standard error, t-stat and interval; the 28 alpha tests (one
family of 28, run with three SE methods; the module also tests 28 electronics loadings and one $\beta=1$ hypothesis,
and says so, citing LM21's rule); LM2's and LM16's slopes. *Stability check:* the halves' betas, yearly betas (LM2's
and the widget's), rolling 250-return betas, the 20 starting days of non-overlapping sums, the yearly-fit residuals of
X4. *Out-of-sample:* the hedge ratio estimated on the first half and applied in the second (E6); the lab's walk-forward
hedge, one rule fixed in advance. *Model:* LM18's paths,
the quadrature value of E4, experiment 1. *Descriptive:* growth factors, $q_{\text{mkt}}$, the residual correlations.
Local note: "Every sector figure uses daily price-index returns of U28, 2 December 2008 to 8 October 2026 (4,382
returns): they leave out dividends, so every intercept includes a dividend-yield gap. Fits and tests are in-sample,
and the module runs 28 alpha tests on the same data, which Section 7 corrects for. Halves, years and rolling windows
are stability checks. One hedge is judged out of sample, on the half its ratio did not see."

**Notation.** AUTHORING §6 with the Volume IV table. Used: $R$, $r$, $T$, $t$, $A$, $N=28$, $i$ (a sector), $\mathbf y$,
$X$ ($T\times d$, first column $\mathbf 1$), $d$, $\boldsymbol\beta$, $\hat{\boldsymbol\beta}$, $\hat{\mathbf y}$,
$\boldsymbol\varepsilon$, $\hat{\boldsymbol\varepsilon}$, $\varepsilon_t$, $\hat\varepsilon_t$, $\Pi$, $\alpha$
(intercept; Jensen's alpha $\alpha_{\text{J}}$), $\beta$, $s_\varepsilon$, $s$ (divisor $T$), $\operatorname{SE}$,
$\text{t-stat}(\cdot)$, $H_0$, $H_1$, $\hat\rho$ (a sample correlation), $\hat\rho_k$ (LM19's sample autocorrelation),
$\rho$, $\Sigma$, $C$ (a correlation matrix, E8), $r_f$, $\E$, $\Var$, $\Cov$, $\mathcal N$, $\mathcal N_{28}$, $t_\nu$,
$\Phi$, $\Phi^{-1}$, $\hat F^{-1}$ (E4's terciles), $F_t$ (TX's settlement price, E6), $m$ (days in a sum, $m=20$), $k$
(a lag), $\hat\Sigma$ ((10.2), cited), "R-squared" in words. As LM12 wrote it, the design $(\mathbf 1\ X)$ of LM12 is
LM23's $X$; one sentence says so. Local symbols, accepted by the cross-check (X17, X22) and declared in the notation
note:

| Symbol | Meaning | Check |
|:--|:--|:--|
| $\mathbf x_t$ | the regressors of date $t$, a column; row $t$ of $X$ is $\mathbf x_t^{\top}$ | as §6's $\mathbf R_t$ and $X$ (X22); LM23 names no column of $X$ |
| $R_{i,t}$, $R_{\text{mkt},t}$, $R_{\text{el},t}$ | sector $i$'s, the TAIEX's and Electronic's daily price-index returns | subscripted $R$; not $R_m$ ($m$ counts days) |
| $\sigma_\varepsilon^2$, $\Sigma_\varepsilon$ | error variance under homoskedasticity; $\Var(\boldsymbol\varepsilon\mid X)$ in general | subscripted $\sigma$, $\Sigma$; $\Omega$ stays the sample space |
| $\Gamma_k$, $\hat\Gamma_k$ | $\E[\varepsilon_t\varepsilon_{t-k}\mathbf x_t\mathbf x_{t-k}^{\top}]$ and its sample version (divisor $T$) | matrix version of $\gamma_k$; LM23 writes no scalar $\gamma$ |
| $\ell$ | the Newey–West lag (statsmodels' `maxlags`) | §6's $B$, $\ell$ row: LM22's block length, LM23's lag; neither writes a likelihood (X17); $L$ is 00631L's multiple |
| $\beta_{j,\text{null}}$ | the value of $\beta_j$ under $H_0$ in (23.4) | as LM21's $\mu_{\text{null}}$; clear of LM24's $\beta_0$ (X22) |
| $h_t$, $h_0$ | hat value of date $t$, the $t$th diagonal entry of $\Pi$; of a new point $\mathbf x_0$ | subscripted; $\mathbf h$ (LM8's holdings) not used; "leverage" keeps the book's meaning ($f>1$) |
| $\alpha_{\text{J}}$ | Jensen's alpha, on total excess returns | subscripted $\alpha$ |
| $q_i$, $q_{\text{mkt}}$ | dividend yields a year, continuous as in LM6 | LM23 has no bets; the FDR level is written in words |
| $\text{RSS}$ | residual sum of squares $\lVert\hat{\boldsymbol\varepsilon}\rVert^2$ | upright |
| $s_x$, $\bar x$ | the regressor's standard deviation (divisor $T$) and mean in a simple regression | LM12's $\bar y$ kept for the response |

Not used: $R^2$, $L$ for the lag, $\Omega$, $\theta$ (LM12's angle cited by tag (12.4) only), $\mathbf h$, $q$ as an FDR
level, $p_i$ (p-values in words, LM21's symbols only in a cited sentence), $\beta_{j,0}$, a letter for the F statistic
(written "the F statistic", since $F_t$ is TX's price), a star for a bootstrap draw.

**Motivating case: "Is Semiconductor's alpha real?"** (box, about 150 words)

> From 1 December 2008 to 8 October 2026 the TWSE Semiconductor price index rose 38.1-fold, against 10.9-fold for the
> TAIEX price index [A23-09]. Regress Semiconductor's 4,382 daily returns on the TAIEX's. The slope, the sector's
> beta, is 1.207; the intercept is 2.10 bp a day, 5.16% a year [A23-10], with a classical t-stat of 2.10 [A23-12]. That clears
> the familiar 1.96. Before calling it skill, answer three questions. How sure is the beta? Its standard error is
> 0.0088 by the textbook formula, 0.0129 by White's and 0.0185 by Newey–West's [A23-11], and the beta was 1.089 in the
> first half of the sample and 1.294 in the second [A23-13]. What does the intercept measure, when price indices leave
> out dividends and the regression leaves out interest? And how many sectors were tried? Of 28, one intercept clears
> 1.96; chance alone predicts 1.4 [A23-15].

Resolved: (a) the beta's error: §3–§5, X4 (the HAC error keeps growing with $\ell$ because the beta drifts), X3, X8;
(b) the intercept: §6, (23.8): $r_f=2\%$ moves it by $+0.17$ bp a day, equal dividend yields by $-0.29$ bp [A23-32,
A23-33]; (c) 28 tries: §7, E8 (no correction rejects anything; Semiconductor's classical p-value 0.036 against
Bonferroni's 0.00179 [A23-40]).

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | regression as measurement with an error bar; case + X1; roadmap; notation and hygiene notes | 360 |
| 2 | The Linear Model and Its Assumptions {1} | LM12's design is $X$; (23.1); the four assumptions listed as a theorem's hypotheses; unbiasedness; (23.2) from (16.4); simple regression $\Var\hat\beta=\sigma_\varepsilon^2/(Ts_x^2)$, the $1/T$ rate of lm18.md:153; (23.3) by $\operatorname{tr}(I-\Pi)=T-d$ (12.2); for normal errors the MLE divides by $T$ ([[LM20]]); E1; Gauss–Markov for linear unbiased estimators, Deep Dive (chapter-level reference); pitfall: spurious regression pointer ([[LM25]]); 導讀; KC | 620 |
| 3 | Standard Errors, Intervals and Hat Values {2} | (23.4), $t_{T-d}$ *stated without proof*, normal for large $T$; E2; R-squared as a statistic (adjusted, F test one sentence each; LM12's accounting identity); (23.5): confidence and prediction intervals, the hat value $h_t$ (a point's influence, never called leverage, which stays the book's $f>1$), $\sum_th_t=d$; X2; E3 (7 April 2025, $h=0.171$, 21 times the average); 導讀; KC ($\beta=1$) | 600 |
| 4 | Heteroskedasticity and White's Standard Errors {3} | the sandwich (23.6) from (16.4); White's estimator, conditions stated without proof (White 1980); E4 on LM18's paths; the market model's ratio White/classical 1.19–1.91 [A23-26]; FinancialInsurance's White SE three times the classical in 2025 (E3 cross-reference); KC (LM16's slope) | 440 |
| 5 | Overlapping Returns and Newey–West {3} | overlapping 20-day sums, MA(19) residuals (LM19's $\hat\rho_1=0.953$ against 19/20); long-run variance; (23.7), Bartlett weights, PSD (Newey and West 1987); the book's lag rule, stated as statsmodels' default HAC lag and Newey and West's (1994) pilot lag, not the lag they recommend; E5; X5; X4: the lag curve and the drift diagnosis; pitfall: an SE that grows with $\ell$; one sentence each on [[LM22]]'s block bootstrap and on [[LM33]], which applies the long-run variance to a Sharpe ratio; 導讀 (heteroskedasticity, HAC); KC | 560 |
| 6 | The Market Model: Beta, Alpha and Hedging {4,5} | market model; CAPM stated (Campbell, Lo and MacKinlay ch. 5; Sharpe 1964 and Lintner 1965 as origins); Jensen's alpha (Jensen 1968); (23.8) with sizes; X3 (28 betas, intervals, halves: 25 of 28 move beyond 1.96 HAC SEs); X8 rolling betas; E6 hedge (LM8's promise, contracts at $200F_t$; out of sample); E7 (LM2's slope); 導讀 (beta, alpha, Jensen, 市場模型); KC | 650 |
| 7 | Twenty-Eight Alphas {6} | X6; counts by method (1, 1, 2) against 1.4; Bonferroni, Holm, BH applied (LM21's); correlation across sectors; E8 with experiment 1; the case resolved; one sentence on [[LM34]]; 導讀 (多重假設檢定); KC | 480 |
| 8 | A Factor Named in Advance {7} | two-factor model, the constructed electronics factor; LM11's warning; collinearity, (23.9) VIF, (12.6); reparametrization keeps the fit; X7; E9; Semiconductor sits inside Electronic (partly mechanical loading); halves' cosine 0.807 against PC2's 0.297; Fama–MacBeth one sentence; KC | 420 |
| 9 | Regression in Python {8} | `np.linalg.lstsq`; statsmodels `OLS.fit(cov_type=…, cov_kwds=…)`, HC0 against `get_robustcov_results`' default HC1, `use_correction`, `use_t`; `multipletests(method=…)`; lab box | 200 |
| — | Summary (7) / Problems (12) / Solutions | | 140 / 400 / 520 |
| | **Total** | | **5,390** |

**Elements.** 9 examples (E1 §2; E2, E3 §3; E4 §4; E5 §5; E6, E7 §6; E8 §7; E9 §8). Knowledge checks:

- §2: why LM12's December 2008 fit (22 returns, 29 columns, rank 22; lm12.md:296–322) has no $s_\varepsilon$:
  $\text{RSS}=0$ and $T-\operatorname{rank}=0$, so (23.3) is $0/0$; an exact fit carries no error estimate.
- §3: test $H_0:\beta=1$ for Semiconductor: t-stat 23.6 with the classical SE, 11.2 with HAC; both reject [A23-24].
- §4: LM16's slope $\hat\beta=0.4591$: SEs 0.0099 classical, 0.0165 White, 0.0229 HAC; HAC interval 0.414 to 0.504;
  $s_\varepsilon=0.99626\%$ with divisor $T-2$ against 0.99603% with $T$ (LM12's 0.996%, lm12.md:436) [A23-27].
- §5: under iid days, overlapping 20-day sums correlate $(20-k)/20$ at lag $k$: 0.95 at lag 1, 0.50 at 10, 0 from 20;
  Semiconductor's overlap residuals show $\hat\rho_k$ (LM19's) of 0.953, 0.538, 0.038 [A23-29].
- §6: CommunicationsInternet, $\beta=0.507$, raw intercept $-0.18$ bp (SE 0.99 bp): $r_f=2\%$ lowers it by
  $(1-\beta)r_f/A=0.40$ bp a day, 0.99% a year, to $-0.59$ bp [A23-32].
- §7: Bonferroni's threshold for 28 two-sided tests at the 5% level: p-value below 0.00179, $\lvert\text{t-stat}\rvert>
  3.12$ [A23-40]; the expected count 1.4 needs no independence (linearity of expectation), its spread does (E8).
- §8: the VIF of two regressors with correlation 0.970 is 16.7; with 0.365 it is 1.15 [A23-44].
- §9: `OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 9})` reports normal p-values (`use_t` is False) and no
  small-sample factor (`use_correction=False`); with `use_correction=True` the SE grows by $\sqrt{T/(T-2)}=1.000228$
  [A23-49].

中文導讀 in §2 (迴歸 (regression), 普通最小平方法 (ordinary least squares), 殘差 (residual), 不偏估計量, 高斯-馬可夫定理
(Gauss–Markov theorem), 最佳線性不偏估計量 (best linear unbiased estimator)), §3 (標準誤, 信賴區間, 判定係數
(R-squared)), §5 (變異數非齊一性 (heteroskedasticity), 自我相關 (autocorrelation), 穩健標準誤 (robust standard error),
變異數非齊一與自我相關一致估計量 (HAC)), §6 (beta and alpha kept in English; Jensen's alpha; 殘差; 市場模型 (market
model)), §7 (多重假設檢定 (multiple testing), 族系誤差率, 偽發現率, Bonferroni 校正, 資料偵伺). All but 市場模型 are on
the plan's list (`plans/vol-4.md`, "Chinese terms"); 市場模型 (market model) and 共線性 (collinearity) are 樂詞網's
statistics forms (SOURCES, "Chinese terms (Volume IV)"); collinearity (§8, no box) is written in English in the text.
Deep Dives: §2 "Why OLS is best among linear unbiased estimators" (linear estimators only, X32): any linear
unbiased $M\mathbf y$ has $MX=I$; write $M=(X^{\top}X)^{-1}X^{\top}+K$ with $KX=0$, so
$\Var(M\mathbf y\mid X)=\sigma_\varepsilon^2(X^{\top}X)^{-1}+\sigma_\varepsilon^2KK^{\top}$ by (16.4) ($M$, $K$ as §6's
generic matrices; $C$ stays E8's correlation matrix); reference Hayashi §1.3 or Greene ch. 4 at chapter level. §5
"Why overlapping sums need $\ell\ge m-1$": under iid days the overlap error is a sum of 20 daily errors, so its
autocovariance is $(m-k)\sigma^2$ for $k<m$ and 0 beyond (derived by (16.3)); Bartlett weights keep the estimate
positive semi-definite (*stated without proof*; Newey and West 1987 claim positive semi-definiteness in their abstract;
that their weights are Bartlett's is an open point in SOURCES).

**Exhibits.**

- X1 `case` (table, §1): Semiconductor on the TAIEX, daily simple price returns, 2008-12-02 → 2026-10-08. Rows: beta
  1.207 [A23-10]; SE(beta) 0.0088 / 0.0129 / 0.0185 (classical / White / Newey–West $\ell=9$) [A23-11]; intercept
  2.10 bp a day, 5.16% a year; SE(intercept) 1.00 / 1.00 / 1.01 bp; t-stat 2.10 / 2.10 / 2.09 [A23-12]; R-squared
  0.8112; halves' betas 1.089 and 1.294 [A23-13]; 28 sectors: betas 0.507 (CommunicationsInternet) to 1.207
  [A23-14]; intercept $\lvert\text{t-stat}\rvert>1.96$: 1, 1, 2 by method, 1.4 expected [A23-15]. Note: price indices
  (no dividends); in-sample. Source: FinMind `TaiwanStockPrice`, retrieved 11 October 2026, repaired closes
  (`data/vol2_series.py`); Computations: `data/lm23_numbers.py`.
- X2 `fin2025` (`scatter`, §3): FinancialInsurance against TAIEX, 243 daily returns of 2025 [A23-21], x and y in %
  (`fmt: "n2"`), stored sorted by x without dates (X37); points (named "2025 days"); fitted line (`lines`, solid) and
  the fit without 7 April 2025 (`segments`,
  dashed, $\beta=0.432$); `bands` (approved C3): "95% confidence band" and "95% prediction band" on 60 x values from
  −9.70% to 9.25%; point label "7 Apr 2025" at (−9.70, −9.89). Values cited: $\beta=0.529$ (SE 0.035), at −5% fitted
  −2.64%, confidence −3.01 to −2.28, prediction −4.33 to −0.96 [A23-22]; the full sample's confidence half-width at −5%
  is 0.105 points, about a pixel [A23-22]. Note: in-sample; the 10% limit capped many stocks that day (PITFALLS §7),
  so the point understates the move.
- X3 `betas` (`scatter`, forest plot, §6): y = the 28 sectors sorted by full-sample beta, `ticks` 1–28 with
  `tickLabels` (approved C2); x beta 0.2–1.5 (`fmt: "n3"`). For each sector an unnamed thick `lines` entry for the
  classical 95% interval and an unnamed thin grey one for the HAC interval ($\ell=9$), so the legend shows only the
  point series "full sample", "first half", "second half" (three named series; X39); the note names the two interval
  styles. Values cited: Semiconductor 1.207 (classical 1.190–1.225, HAC 1.171–1.244) [A23-18];
  FinancialInsurance 1.156 → 0.578, Cement 0.982 → 0.463; 25 of 28 halves differ by more than 1.96 HAC SEs; halves'
  betas correlate 0.653 [A23-34]. Note: stability check; HAC $\ell=7$ for the halves.
- X4 `haclag` (`line`, log x, approved C1, §5): x $\ell$ from 1 to 400 (about 60 log-spaced integers; `ticks` 1, 2, 5,
  …, 200); y SE of Semiconductor's daily beta (`fmt: "n4"`). Series "full-sample residuals" and "residuals of yearly
  fits"; dashed `hline`s classical 0.0088 and White 0.0129 (the $\ell=0$ value); dashed `vline` $\ell=9$. Values cited:
  0.0185, 0.0275, 0.0390 at $\ell$ = 9, 50, 200; with yearly residuals 0.0152, 0.0160, 0.0123 [A23-31]. Note: the
  second series removes each calendar year's own line from the residuals (19 fits; 2008's 22 returns form their own);
  it is a diagnostic, not an estimator.
- X5 `overlap` (table, §5): Semiconductor, FinancialInsurance, Food; 20-day log-return sums. Rows: daily log beta (SE);
  overlapping beta (4,363 windows); SE classical / White / NW $\ell=19$ / NW $\ell=38$; non-overlapping beta from the
  first return (219 sums) and its classical SE; range over the 20 starting days. Values: 1.204 (0.0088); 1.157; 0.0089,
  0.0115, 0.0389, 0.0464; 1.106, 0.0406; 1.106–1.189 [A23-28]; FinancialInsurance and Food [A23-30].
- X6 `alphas` (`bar`, §7): 28 sectors sorted by classical t-stat; series "classical" and "Newey–West" (`fmt: "n2"`);
  `hline`s at ±1.96 and ±3.12 ("Bonferroni, 28 tests"). Values cited: Semiconductor 2.10 / 2.09, Optoelectronic
  −1.94 / −1.96 (−1.9647 [A23-15]), Cement −1.53 / −1.56 [A23-39]. Note: price indices; in-sample; 28 tests.
- X7 `factor` (table, §8): ElectronicPartsComponents, ComputerPeripheralEquipment, Semiconductor,
  CommunicationsInternet, FinancialInsurance, Plastics. Columns: one-factor beta, R-squared; two-factor market and
  electronics coefficients with HAC SEs; R-squared [A23-45, A23-46, A23-48]. Note row: Semiconductor on the raw pair
  (TAIEX, Electronic), −0.515 (0.024) and +1.552 (0.021), the same residuals [A23-45]. Note: the
  factor is *constructed*; Semiconductor and the other electronics sectors are inside Electronic.
- X8 `rolling` (`line`, date, shared `x.values`, approved C4, §6): rolling 250-return betas of FinancialInsurance and
  Semiconductor, each with its classical 95% band (`lo`/`hi`, two band series): four series. Thinned to weekly points
  (every fifth window) plus every cited extreme (X37); under 60 KB. Values: FinancialInsurance 1.377 (2010-02-23) to 0.251
  (2026-05-26), last 0.308; Semiconductor 0.914 (2011-05-18) to 1.658 (2020-01-17), last 1.168 [A23-35]; dashed
  `hline`s at the full-sample 0.823 and 1.207. Note: stability check; 4,133 windows, the first ending 2009-11-30.

**Widget `regWindows` — "Betas and alphas by window."** `Book.controls`: window (select: full sample, first half,
second half, 2009, …, 2025, 2026 to 8 October, last 250 returns: 22 options), method (classical, White, Newey–West with
$\ell$ by the rule), sector (select, 28). Chart: X3's forest plot for the chosen window and method (intervals
$\hat\beta\pm\Phi^{-1}(0.975)\operatorname{SE}$, `Book.dist.PhiInv`), the chosen sector in colour 2, sector order fixed
by the full-sample beta so that movement shows. Readouts: beta, SE, interval, intercept in bp a day and ×$A$, its
t-stat, R-squared, $s_\varepsilon$, $T$, $\ell$. Initial state (PDF): full sample, Newey–West, Semiconductor, equal to
X1. Data block `chart-lm23-regWindows`: per window and sector, beta, intercept, three SEs of each, R-squared,
$s_\varepsilon$ (22 × 28 × 10 numbers, about 60 KB), computed by `data/lm23_charts.py`. No simulation, no $t$ quantile
(the kit has none; with $T-d\ge183$ the normal quantile differs from $t$ by at most 0.7%, $t_{183}$'s being 1.973
[A23-19]).

**Examples** (results recomputed from the printed inputs):

- E1 §2 `fourpts`, LM12's four points: $\hat\beta=1.4$, $\hat\alpha=0.9$, $\text{RSS}=4.2$, $T-d=2$,
  $s_\varepsilon^2=2.1$; $\operatorname{SE}(\hat\beta)=\sqrt{2.1/5}=0.648$, $\operatorname{SE}(\hat\alpha)=1.212$,
  t-stat 2.16; the $t_2$ quantile 4.303 gives −1.39 to 4.19, while 1.96 would give 0.13 to 2.67 and exclude 0 [A23-16].
  Few residual degrees of freedom: the normal quantile misleads.
- E2 §3 `semi`, the case by hand: $s_\varepsilon=0.66239\%$ (divisor $T-2$; 0.66224% with $T$), $s_x=1.137\%$, so
  $\operatorname{SE}(\hat\beta)=s_\varepsilon/(\sqrt T s_x)=0.0088$ [A23-17]; interval 1.190–1.225 [A23-18];
  adjusted R-squared 0.81119 against 0.81124; the F statistic $137.20^2=18{,}824$ [A23-20]; the intercept's classical
  t-stat 2.10, p-value 0.036 (normal), stated as one test of 28 (§7).
- E3 §3 `band`, FinancialInsurance in 2025 (X2): $\hat\beta=0.529$, SE 0.0350 classical but 0.106 White [A23-21];
  at a TAIEX return of −5% (beyond all but 2 days of 2025 [A23-23]) the fitted −2.64%, SE of the fit 0.187 points,
  confidence −3.01 to −2.28, prediction −4.33 to −0.96 [A23-22]. 7 April 2025: TAIEX −9.70%, FinancialInsurance −9.89%;
  $h=0.1709$ against the average $d/T=0.0082$, 21 times; without that day $\hat\beta=0.432$; one day moves the year's
  beta by 2.8 classical SEs [A23-23]. White's SE, three times the classical one [A23-21], stays 0.097 without that day
  [A23-23]: the errors are largest on the year's few days of large index moves.
- E4 §4 `lm18slope`, LM18's paths: $\hat\beta=2.1759$; classical SE 0.0067, White 0.0152; the model's exact value,
  by quadrature over the normal law of $\ln G$, is 0.0157 (and the classical formula's model value 0.0067); LM18's
  batch SE 0.0113 [A23-25] is 0.72 of the exact value, inside the about 16% relative error of a spread from 20 batches
  [A23-58]. Residual root mean square (what White's SE uses) by tercile of $\ln G$, cut at $\hat F^{-1}(1/3)$ and
  $\hat F^{-1}(2/3)$ with each cut point in the lower group: 0.260, 0.179, 0.378 [A23-25]: the convex $G=e^{\ln G}$
  leaves the errors largest at both ends, where $\ln G$ also lies farthest from its mean, so the classical formula is
  43% of the truth [A23-58].
- E5 §5 `overlap20`, Semiconductor: overlapping 20-day beta 1.157, classical SE 0.0089, Newey–West ($\ell=19$) 0.0389,
  against the non-overlapping 0.0406 [A23-28]; ratio 4.35 against $\sqrt{20}=4.47$ [A23-53]; the residuals' lag-1
  autocorrelation $\hat\rho_1=0.953$ (LM19's) [A23-29].
- E6 §6 `hedge` (LM8's promise; hypothetical NT\$100 million of FinancialInsurance, hedged with TX at NT\$200 a point):
  the variance-minimizing ratio is the beta, (16.8)'s; full sample 0.8234 (R-squared 0.5916), last 250 returns 0.3085
  (0.1989); a contract is worth $200F_t$ (LM8), and TX's settlement price on 8 October 2026 was $F_t=49{,}357$ (TX23,
  the 202610 contract), so the notional hedge is 10.13 contracts and the beta hedges 8.34 or 3.12, about 3 contracts
  [A23-36]. Out of
  sample:
  the first half's 1.1556 applied in the second half cuts variance by 0.19%, the notional hedge (ratio 1) by 23.09%, the
  second half's own 0.5784 by 49.29% [A23-37]. A regression hedge is only as good as the beta's stability.
- E7 §6 `etf` (LM2's sample recomputed): slope 1.8865, SEs 0.0081 classical, 0.0154 White, 0.0211 HAC ($\ell=8$); the
  designed 2 lies 5.38 HAC SEs away (interval 1.845–1.928); 2021's 1.984 against 2024's 1.717 differ by 2.47 SEs of the
  difference (HAC $\ell=4$) [A23-38]. Measurement says the fund's average exposure is below 2 and moves between years.
- E8 §7 `alphas`: classical t-stats from −1.935 (Optoelectronic) to 2.097 (Semiconductor) [A23-39]; Bonferroni,
  Holm and BH at 5% (false discovery rate 5%) reject none, by any method; Holm's smallest adjusted p-value 1.000, BH's
  0.742 (HAC 0.692) [A23-40]. Residuals correlate across the 378 pairs from −0.430 to 0.462, mean 0.112 [A23-41], so
  under the null the count of $\lvert\text{t-stat}\rvert>1.96$ has mean 1.4 either way but SD 1.458 against 1.153, and
  $\Pr(\text{at least one})=0.696$ (Monte Carlo SE 0.0015) against 0.7622 for independent tests [A23-42, A23-43]
  (experiment 1, `default_rng([1, 20261011])`, 100,000 draws of $\mathcal N_{28}(\mathbf 0,C)$, $C$ the residual
  correlation matrix; 69,645 of the draws had at least one, an exact tie at four decimals, so three are printed).
  Resolution: one passing t-stat is what chance gives; with $r_f$ and dividends Semiconductor's intercept is 1.98 bp
  under equal yields [A23-33], still one draw from 28.
- E9 §8 `factor`: $R_{i,t}=\alpha+\beta_{\text{mkt}}R_{\text{mkt},t}+\beta_{\text{el}}(R_{\text{el},t}-R_{\text{mkt},t})
  +\varepsilon_t$. Semiconductor: 1.037 and +1.552, R-squared 0.8112 → 0.9163 [A23-45]; FinancialInsurance: 0.997 and
  −1.580, 0.5916 → 0.7624 [A23-46]. Raw pair (TAIEX, Electronic): −0.515 and +1.552, the same residuals; correlation
  0.970, VIF 16.7, condition number of the correlation matrix 65, against 0.365, 1.15 and 2.15 [A23-44]. 27 of 28
  loadings have $\lvert\text{t-stat}\rvert>1.96$ by either method (the weakest, CommunicationsInternet: classical
  −1.05, HAC −0.68); the halves' 28 loadings have cosine 0.807, the halves' betas 0.966 [A23-47], against PC2's 0.297
  (lm11.md:387).

**Problems plan** (12; MC keys B, A, C, A, C, B; the lab solves 8, 11, 12). Stems state the sample (U28, daily simple
price returns, 2 December 2008 → 8 October 2026, $T=4{,}382$, $A=245.4794$) or the hypothetical inputs, the divisor
($T-d$ for $s_\varepsilon$, $T$ for $s_x$), the SE method and $\ell$, the normal reference, the level, rounding; problem 12
gives the seed and draws.

1. MC: $T=12$ monthly returns, a constant and one regressor, $\text{RSS}=0.0240$; $s_\varepsilon$. A 4.47% (divisor $T$).
   **B** 4.90%. C 4.67% (divisor $T-1$, LM20's $s_{\mathrm u}$ applied to a regression) [A23-50].
2. MC: $s_\varepsilon=1\%$, $s_x=1.2\%$ (divisor $T$), $T=1{,}000$; $\operatorname{SE}(\hat\beta)$. **A** 0.0264. B 0.833
   (no $\sqrt T$). C 0.000833 (divides by $T$) [A23-51].
3. MC: Semiconductor, $\hat\beta=1.2073$, SEs 0.0088 classical and 0.0185 HAC; the HAC t-stat of $H_0:\beta=1$. A 65.3
   (tests $\beta=0$). B 23.6 (classical SE). **C** 11.2 [A23-52].
4. MC: daily iid returns regressed in overlapping 20-day sums; the honest SE against the classical one is about. **A**
   4.5 times ($\sqrt{20}$; the data give 4.35). B the same (overlap ignored). C 20 times ($m$, not $\sqrt m$) [A23-53].
5. MC: price-index market model, $\beta=0.6$, intercept 1.0 bp a day, $r_f=2\%$ a year, $A=245.48$, equal dividend
   yields aside; Jensen's alpha per day. A 1.326 bp (sign reversed). B 0.185 bp ($r_f/A$ without $1-\beta$). **C** 0.674
   bp [A23-54].
6. MC: five p-values 0.004, 0.011, 0.019, 0.030, 0.20, family-wise level 5%; Holm's rejections. A 1 (Bonferroni's
   count). **B** 2. C 4 (BH's count at a 5% false discovery rate) [A23-55]. The solution adds that statsmodels'
   default `"hs"` (Holm–Šidák) also gives 2 here, and why the default must still be overridden.
7. Derive (23.2) from (16.4), then $\E[\text{RSS}\mid X]=(T-d)\sigma_\varepsilon^2$ from $\operatorname{tr}(I-\Pi)=T-d$.
8. Hat values in a simple regression: show $h_t=\tfrac1T+(x_t-\bar x)^2/(Ts_x^2)$ and $\sum_th_t=2$; for 7 April 2025
   from the printed 2025 inputs (TAIEX mean 0.1062%, $s_x=1.5405\%$ with divisor 243, $x_t=-9.6997\%$), $h=0.1709$
   [A23-56, A23-21]. Python part: recompute the year's hat values.
9. Hedge (hypothetical): NT\$50 million in a sector with $\beta=0.75$ and R-squared 0.5 on the TAIEX, TX settling at
   $F_t=20{,}000$, NT\$200 a point: 9.375 contracts (9), against 12.50 by notional; the hedged SD is $\sqrt{0.5}=0.7071$ of the
   unhedged [A23-57]; why the in-sample R-squared overstates the reduction (E6).
10. Show that regressing on $(R_{\text{mkt}},R_{\text{el}})$ and on $(R_{\text{mkt}},R_{\text{el}}-R_{\text{mkt}})$ gives
    the same fitted values and the same electronics coefficient, with market coefficients related by
    $\beta_{\text{mkt}}^{\text{excess}}=\beta_{\text{mkt}}^{\text{raw}}+\beta_{\text{el}}$; check on Semiconductor
    (−0.515 + 1.552 = 1.037) and compute both VIFs [A23-44, A23-45].
11. Python: FinancialInsurance's market model by NumPy and by statsmodels (`cov_type="nonrobust"`, `"HC0"`, `"HAC"` with
    `cov_kwds={"maxlags": 9}`): $\hat\beta=0.8234$, SEs 0.0103, 0.0183, 0.0288; with `use_correction=True` 0.02885
    [A23-49]; why `get_robustcov_results()` without arguments gives HC1.
12. Python: the 28 intercept t-stats, their p-values and `multipletests` with `method="bonferroni"`, `"holm"`,
    `"fdr_bh"` passed explicitly; then experiment 1 (`default_rng([1, 20261011])`, 100,000 draws): $\Pr(\text{at least one})$
    0.696 (Monte Carlo SE 0.0015) [A23-43].

**Lab parts** (`build/make_lab23.py`; reads only its `data/`: `sectors_close_raw.csv` and `sectors_close_repairs.csv`
(U28 and Electronic, rebuilt with LM16's repair cell), `0050_daily_raw.csv`, `0050_dividends.csv`,
`00631L_daily_raw.csv` (LM2's pairs, built as LM2's lab builds them), `taiex_tr.csv` (TR23, for $q_{\text{mkt}}$ and
LM18's paths)): 1 data, $T$, $A$, halves, the lag rule; 2 OLS by hand, E1, E2, statsmodels with every option; 3 X2,
E3, hat values; 4 E4 (LM18's paths, seed [3, 20261011]), LM16's slope; 5 X4, E5, X5; 6 X3, X8, E6, E7; 7 X6, the three
corrections, E8 (experiment 1); 8 X7, E9; 9 problems 8, 11, 12. E6's contract count takes TX23's $F_t=49{,}357$ as a
printed input (cited to `data/vol4_series.py`), so the lab needs no futures file. Extension (*Out-of-sample*, "one
rule fixed in advance", X40): hedge FinancialInsurance each month with the trailing 250-return beta and compare the
next month's hedged variance with the notional hedge's; a closing sentence says that choosing among many such rules
is LM34's subject. Labs write plain "LM22" and "LM34", never `[[LM22]]`.

**Cross-module tags.**

- (23.1) $\mathbf y=X\boldsymbol\beta+\boldsymbol\varepsilon$, $\hat{\boldsymbol\beta}=(X^{\top}X)^{-1}X^{\top}\mathbf y$; $X$
  of full column rank (LM25, 26, 27, 30).
- (23.2) $\E[\hat{\boldsymbol\beta}\mid X]=\boldsymbol\beta$ when $\E[\boldsymbol\varepsilon\mid X]=\mathbf 0$;
  $\Var(\hat{\boldsymbol\beta}\mid X)=\sigma_\varepsilon^2(X^{\top}X)^{-1}$ when also $\Var(\boldsymbol\varepsilon\mid X)
  =\sigma_\varepsilon^2I$; simple regression $\sigma_\varepsilon^2/(Ts_x^2)$ (LM25).
- (23.3) $s_\varepsilon^2=\text{RSS}/(T-d)$, $\E[s_\varepsilon^2\mid X]=\sigma_\varepsilon^2$ under (23.2)'s conditions
  (LM25).
- (23.4) $\text{t-stat}(\hat\beta_j)=(\hat\beta_j-\beta_{j,\text{null}})/\operatorname{SE}(\hat\beta_j)$; $t_{T-d}$
  under normal errors (*stated without proof*), approximately $\mathcal N(0,1)$ for large $T$; interval
  $\hat\beta_j\pm\Phi^{-1}(0.975)\operatorname{SE}$ (LM25, whose DF t-stat is not $t$; LM26).
- (23.5) $\Var(\mathbf x_0^{\top}\hat{\boldsymbol\beta}\mid X)=\sigma_\varepsilon^2h_0$, $h_0=\mathbf x_0^{\top}(X^{\top}X)^{-1}
  \mathbf x_0$; prediction variance $\sigma_\varepsilon^2(1+h_0)$ (in-module).
- (23.6) $\Var(\hat{\boldsymbol\beta}\mid X)=(X^{\top}X)^{-1}X^{\top}\Sigma_\varepsilon X(X^{\top}X)^{-1}$; White's
  $\sum_t\hat\varepsilon_t^2\mathbf x_t\mathbf x_t^{\top}$ for the middle; independent rows, large $T$ (LM25, 26).
- (23.7) Newey–West: $\hat\Gamma_0+\sum_{k=1}^{\ell}\big(1-\tfrac{k}{\ell+1}\big)(\hat\Gamma_k+\hat\Gamma_k^{\top})$ in
  place of $X^{\top}\Sigma_\varepsilon X/T$; stationary products with fading dependence, $\ell\to\infty$ slower than $T$
  (stated), with the book's lag rule (LM26, LM33).
- (23.8) $\alpha=\alpha_{\text{J}}+(1-\beta)\,r_f/A-(q_i-\beta q_{\text{mkt}})/A$ per day, for a price-index market
  model; $r_f$, $q$ simple a year, spread evenly (LM27, 30, 33).
- (23.9) $\operatorname{VIF}=1/(1-\hat\rho^2)$ for two regressors, the factor by which collinearity multiplies a
  coefficient's variance (LM30).

**Pitfalls to pre-empt.**

- Divisors: $s_\varepsilon$ with $T-d$, descriptive $s$ and $s_x$ with $T$ (every script passes `ddof`); HC0 (White's)
  against HC1 ($T/(T-d)$), which is `get_robustcov_results`' default; statsmodels' `OLS.fit` HAC has `use_correction=False`, while
  `sandwich_covariance.cov_hac_simple` defaults to True; HAC p-values are normal; `multipletests` defaults to Holm–Šidák
  (SOURCES "Python (Volume IV)" and the additions below).
- An SE answers a question about a constant model. A Newey–West SE that keeps growing with $\ell$ (X4) says the beta
  drifts; the full-sample beta is an average, and the halves differ in 25 of 28 sectors.
- Overlapping sums: the classical SE is about $\sqrt m$ too small; use $\ell\ge m-1$ or non-overlapping sums.
- A raw intercept on price indices is not Jensen's alpha: say the $r_f$ and dividend terms of (23.8) every time.
- Counts at a threshold move with the method (Optoelectronic −1.965 under HAC, −1.935 classical): report the method,
  then correct for 28 tests; never call one in 28 a discovery.
- Hat values and limit days: 7 April 2025 has 21 times 2025's average hat value, and its returns were capped by the
  10% limit; robust SEs are themselves noisy when a few days dominate (E3). A point's influence is its hat value,
  never its "leverage" (the book's $f>1$).
- The factor: *constructed*, Electronic contains Semiconductor and the other electronics sectors, so their loadings are
  partly mechanical; the TAIEX contains every sector. Never call LM11's PC2 "electronics".
- LM12's accounting identity: a high R-squared of TAIEX on its sectors is not evidence; R-squared describes.
- Small $T-d$: E1's $t_2$; the normal reference only for large $T-d$.
- Ownership: LM2's, LM16's and LM18's numbers are recomputed and cited to their modules; LM21 owns the corrections, LM23
  applies them; LM22 owns block-bootstrap intervals.
- References (SOURCES; chapter level where theorem numbers are unconfirmed): White (1980), Newey and West (1987), the
  lag rule as statsmodels' default HAC lag and Newey and West's (1994) pilot lag, not their recommended lag (their
  NBER Technical Working Paper 144, p. 7, as SOURCES records it; X11), the CAPM from Campbell, Lo and MacKinlay ch. 5
  with Sharpe (1964) and Lintner (1965) as origins (X35), Jensen (1968) and Fama and MacBeth (1973) (bibliographic,
  SOURCES), Gauss–Markov for linear estimators at chapter level (Hayashi §1.3 or Greene (2018) ch. 4), the $t_{T-d}$
  law *stated without proof* (X32: Blitzstein and Hwang do not state it), Strang (2016) §4.2 via LM12.

**Stage 4 for earlier modules.** `leads` gain 23 in lm02.md:6, lm06.md:6 (the $r_f$ proxy and $q$), lm10.md:6
(positive definiteness of $X^{\top}X$), lm15.md:6 ((15.9) for $t_{T-d}$), lm17.md:6 ((17.1), (17.5)) and lm18.md:6, all
on the plan's Stage 4 list (X25–X29); lm08, lm09, lm11, lm12 and lm16 already list 23. No wording change: lm18.md:286's
"batch standard error 0.01" is a correct report of a noisy estimate, which E4 explains (cross-check §8: no change).

**Open before Stage 2** (open in SOURCES; the text is written as the decisions say):

- The Bartlett weights in Newey and West (1987): the §5 Deep Dive cites the paper only for positive
  semi-definiteness, which its abstract states.
- Theorem numbers in Hayashi and Greene: Gauss–Markov stays at chapter level (Hansen 2022 not cited), and the
  $t_{T-d}$ law of (23.4) stays *stated without proof*.

## LM24 Bayesian Inference and Shrinkage

Stage 1 brief, revised 2026-10-19 after the cross-check and the independent recomputation. Drafted from the editor's
spine (`plans/vol-4.md` at commit bcfa0d4, "### LM24 Bayesian Inference and Shrinkage") and revised to "Editor's
decisions on the LM19–LM25 drafts (2026-10-19)", the cross-check's findings that touch LM24 (X1, X3, X6, X19, X20,
X32, X34, X37 and its §8 answers) and the fresh check. Each number carries its anchor ID at its first appearance
(A24-61, added at the revision, breaks the order); `data/vol4_anchors_lm24.py` prints them all (rows in
`plans/vol-4-anchors.md`). Numbers quoted from published modules cite file:line; numbers owned by
another Volume IV module cite it with [[LMn]].

**Prereq:** `[4, 10, 11, 13, 14, 15, 16, 17, 19, 20, 21]`. LM4: (4.2) the second-order growth $g(f)\approx
f\mu-\tfrac{f^2}{2}(\sigma^2+\mu^2)$ (lm04.md:114); (4.3) the quadratic rule $\mu/\sigma^2$ (lm04.md:118); (4.5) the
exact Kelly condition $\bar g'(f)=0$ (lm04.md:180); (4.15) $cf^*$ keeps $1-(1-c)^2$ of the growth (lm04.md:492); the
band example, which shifts every return by one constant and re-solves the exact Kelly condition (lm04.md:543–551);
fractional Kelly, "a quarter to a half of $f^*$" (lm04.md:558); "size from a haircut estimate" (lm04.md:563). LM10: the
U28 sample, price indices without dividends (lm10.md:41, 46). LM11: the halves, 2,191 returns each (lm11.md:387). LM13:
(13.7) a sequence of independent trials; (13.9) Bayes' rule; (13.10) the odds form; prior and posterior probability
(lm13.md:302); the manager example (lm13.md:328–336: prior 10%, 0.55 against 0.5 a month, 8 good months of 12,
likelihood ratio 1.4064, posterior 13.5%); Practice Problem 8 (16 of 24, posterior 18.02%, lm13.md:497, 530). LM14:
(14.3), (14.4) the mean and variance of $\eta X+\zeta$; TR23's $\bar R=0.0625\%$ and $s=1.2084\%$, divisor $T$
(lm14.md:240–241). LM15: (15.1) the binomial pmf; (15.8) the gamma function (the beta density and the Deep Dive);
$\Phi^{-1}(0.975)=1.96$ (lm15.md:194). LM16: (16.3) the variance of a sum; (16.5), (16.6) the tower property and the
law of total variance; (16.7) linear maps of normal vectors; (16.8) the conditional law in a normal pair, whose slope
becomes the data's weight; the chi-square law (lm16.md:360–361). LM17: (17.1); (17.5), which makes $\bar R$
approximately normal for non-normal days; TR23's exact empirical Kelly leverage, the root of (4.5), written
$\hat f^*=4.1381$ here (lm17.md:239). LM19: TR23's annualized mean 15.38% and volatility 18.96% on simple returns (its
annualization exhibit), cited in words. LM20: $\hat f:=\bar R/s^2$; (20.1) the MSE, and E1's scaled mean $\eta\bar R$
with $\eta^*=0.940$ on TR23; (20.2) $\operatorname{SE}(\bar R)=s/\sqrt T$, 3.89 points a year; (20.4) the 95%
confidence interval, 7.8% to 23.0%; (20.5) the normal MLE $\hat\sigma=s$; (20.7) Cramér–Rao for unbiased estimators;
E9's mean-only standard error of $\hat f$, 1.08. LM21: E3's t-stat 3.96, which divides by $s_{\mathrm u}$; (21.2) its
one-sided p-value; the rule that a module reports how many tests it ran on the same data. [[LM23]] is a pointer only
(the market model as another way to remove the common component, §6; robust errors of a mean, E3), not a
prerequisite (cross-check X6).

**Leads:** `[26, 30, 33, 38, 42, 44, 45]`: tag users (LM30 cites (24.3) and (24.4); LM44 and LM45 cite (24.5)) and
pointer targets (LM26, LM33, LM38, LM42).

**Forward links honoured.**

| Earlier text | Promise | Kept in |
|:--|:--|:--|
| lm04.md:558 | fractional Kelly, "a quarter to a half of $f^*$. [[LM24]] and [[LM44]] formalize it" | §7: (24.5), the Bayes bet is $c\hat f$ inside a stated model; E10 finds the prior that LM4's range needs; LM44 keeps risk aversion |
| lm13.md:336 | "[[LM24]] applies the same rule to an unknown parameter" | §2: (24.1); E1 repeats the manager with a beta prior; Problem 12 repeats lm13.md:497 |
| syllabus.yaml:65 (missed by the spine) | "Priors, posteriors, James–Stein; when fractional Kelly is a Bayesian answer." | §2–§7 |
| LM20 and LM21 briefs (Volume IV drafts, 2026-10-19) | "[[LM24]] supplies it [the best $\eta$] from a prior"; "[[LM24]] gives that statement a meaning"; "[[LM24]] computes such a probability" | §3: averaging (20.1) over the prior gives $\eta=c$ [A24-61]; §4: credible intervals and $\Pr(\mu\le0\mid\text{data})$ |
| lm04.md:563 (consistency) | "size from a haircut estimate, then take a fraction of Kelly" | §7: in the stated model the posterior mean is the haircut estimate, and the two steps are one; PSR and DSR stay [[LM33]]'s |
| lm04.md:543–551 (consistency) | the band of 0050's Kelly leverage by shifting the returns | §7: the exact Bayes fraction uses the same shift (E9) |
| lm07.md:509, lm11.md:480 (consistency) | estimation error and shrinkage of $\hat\Sigma$ belong to [[LM30]], Kelly under uncertainty to [[LM45]] | §5 shrinks means only; Leaves |

**Outcomes** ("After this module you should be able to:"):

1. apply Bayes' rule to an unknown parameter, and compute the beta–binomial posterior of a success probability and the data's weight in it
2. derive the posterior of a normal mean with known variance, and explain why the posterior precision is the prior precision plus the data precision
3. distinguish a credible interval from a confidence interval, and compute both for the TAIEX's mean return
4. state the James–Stein estimator with its conditions, and derive its empirical-Bayes reading as an estimated data's weight
5. evaluate a shrinkage estimator out of sample on two halves of a sample, and explain what correlated estimates do to it
6. derive the Bayes Kelly fraction under log utility in a stated model, and compute the prior that makes fractional Kelly the Bayes bet
7. explain what breaks the Bayes Kelly result, and measure the size of its quadratic approximation on TAIEX data
8. compute posteriors, shrinkage factors and out-of-sample errors in Python, passing every divisor explicitly

**Owns.** Bayes' rule for a parameter, (24.1), with the prior density, the likelihood and the posterior density. The
beta distribution (density through (15.8), mean, variance) and the beta–binomial update (24.2). The data's weight $c$ and
the prior's worth $n_0$ in observations, one idea in all three models. The normal model with known variance (24.3),
derived from (16.8), with precision adding up and (16.6) as a check. Credible against confidence intervals; the
posterior probability of a negative mean against a one-sided p-value. The empirical-Bayes model for many means and the
positive-part James–Stein estimator toward the grand mean (24.4), with its conditions and its empirical-Bayes reading.
U28's split-half test (two noise estimates; the reverse direction as a stability check). The Bayes Kelly fraction (24.5)
in the stated model, the sceptic's priors behind LM4's quarter and half, and what breaks the result (a prior away from
zero, unknown or changing $\sigma$, fat tails, other utilities). Statistics owned: TR23's posteriors (X4, the widget),
their data's weights, credible intervals and $\Pr(\mu\le0\mid\text{data})$; the Bayes fractions $f_{\mathrm B}$ and
their expected growth; U28's James–Stein factors and out-of-sample errors; the manager's beta posteriors; Experiments 1
and 2.

**Leaves.** Covariance shrinkage, Black–Litterman and Jorion's Bayes–Stein portfolio → LM30 (Jorion named only; his
target is an open point). Power utility and fractional Kelly as risk aversion → LM44. Parameter uncertainty in practice,
bootstrap Kelly → LM45. Haircuts for a backtest's Sharpe ratio (PSR, DSR) → LM33. Volatility that changes day to day →
LM26. GBM's exact law → LM38; continuous-time Kelly → LM42. TR23's annualized mean and volatility → LM19 (cited).
$\operatorname{SE}(\bar R)$, the confidence interval for $\mu$, $\hat f$ and its delta-method errors → LM20 (cited,
recomputed in the numbers script). Tests of the mean, the t-stat and its p-value → LM21 (cited). Robust standard errors
of a mean → LM22, LM23. Not in the book, one sentence each: shrinking betas, hierarchical models, Markov chain Monte
Carlo.

**Uses before taught** (one sentence each in the text):

- §1 and §5: "Shrinking a covariance matrix, the subject of [[LM30]], follows the same idea for a whole matrix."
- §7: "Under geometric Brownian motion ([[LM38]]) a fixed fraction grows at exactly $f\mu-\tfrac12f^2\sigma^2$, and
  [[LM42]] derives Kelly in continuous time."
- §7: "Volatility that changes from day to day is modelled in [[LM26]]."
- §7: "Power utility, under which fractional Kelly expresses risk aversion, is [[LM44]]'s subject, and sizing from a
  bootstrap distribution is [[LM45]]'s."
- §7 pitfall: "Haircuts for a backtest's Sharpe ratio are [[LM33]]'s."
- §5: the James–Stein dominance theorem (24.4), *stated without proof*; its source toward the grand mean is an open
  point (below).
- §5 Deep Dive and Problem 8: the $\chi^2_{N-1}$ law of a sum of squared deviations from the sample mean, cited to
  Blitzstein and Hwang's Ex. 10.4.3 (the definition of $\chi^2_N$ is [[LM16]]'s, lm16.md:360–361); the $\chi^2_k$
  density stays *stated without proof*, because only the book's Theorem 10.4.2 ($\chi^2_n$ is
  $\operatorname{Gamma}(n/2,1/2)$) was read, not the Gamma density of its §8.4 (plans/vol-4.md, "Sources").

**Data role.** Two samples, never mixed in one statistic.

- **TR23** from `data/processed/vol3_taiex.parquet` (`data/vol3_series.py`; FinMind `TaiwanStockTotalReturnIndex`,
  data_id TAIEX, retrieved 2026-10-18): 5,850 closes, 2003-01-02 → 2026-10-08 [A24-01]; $T=5{,}849$ simple returns
  from 2003-01-03 [A24-02]; 8,680 calendar days, 23.76 years and $A=246.12$ [A24-03]. $\bar R=0.0625\%$ and
  $s=1.2084\%$ (divisor $T$) [A24-04] are [[LM14]]'s, the annualized 15.38% and 18.96% [[LM19]]'s; the model sets
  $\sigma=s$, the normal MLE (20.5). Used for the posterior of $\mu$ (§3–§4), the widget and the Bayes Kelly fraction
  (§7).
- **U28** from `data/lm10_series.py`'s `u28()` (`data/vol2_series.py` builds and repairs `vol2_closes.parquet`): the
  28 leaf sector *price* indices, no dividends, $T=4{,}382$ returns 2008-12-02 → 2026-10-08, $A=245.4794$ [A24-05];
  [[LM11]]'s halves, 2,191 returns each, 2008-12-02 → 2017-10-06 and 2017-10-11 → 2026-10-08 [A24-06]. Annual
  figures use U28's $A=245.4794$ for both halves. Used for the case, §6, Problem 11 and the lab. Every caption says
  "price indices (no dividends), U28's halves".
- **LM13's manager** (hypothetical, as printed, lm13.md:329): 8 good months of 12, prior share 10% at 0.55 against
  0.5.
- Published files: no exhibit or widget carries a daily series (plans/vol-4.md, X37). X1, X5 and X6 plot statistics of
  the 28 sectors, X2, X3 and X7 model curves, and the widget embeds four TR23 statistics.
- Cleaning: none beyond the two builders. Divisors: $s$ and each sector's $s_i$ divide by the returns used (ddof=0);
  $s_{\mathrm u}$ enters only through LM21's t-stat, cited; the cross-sectional standard deviation of the 28 means
  divides by 28 and says so; James–Stein's sum of squared deviations has no divisor. Every interval uses
  $\Phi^{-1}(0.975)$, printed 1.96. LM24 counts no returns against a threshold; its two counts (KC §6, X5's note)
  compare means and use the book's guard.
- Seeds: Experiment 1 (E6) `default_rng([1, 20261011])`: one 10,000×28 array of true means, then one of noise.
  Experiment 2 (Problem 10) `default_rng([2, 20261011])`: at each spread 0, 1, 3 in turn, 20,000×28 true means drawn
  as spread × standard normal (drawn even at spread 0), then the noise. A Monte Carlo average carries its standard
  error, the standard deviation with divisor $n$ over $\sqrt n$. The widget draws nothing.
- Scripts: `data/lm24_numbers.py` (asserts every printed value, recomputes LM14's, LM17's, LM19's, LM20's and LM21's
  numbers it quotes, computes the beta probabilities exactly with `Fraction`, flags every value within a tenth of a
  unit of a rounding boundary at each precision it is printed), `data/lm24_charts.py` (X1–X3, X5–X7, the widget
  block). Lab files: `taiex_tr.csv`, `sectors_close_raw.csv`, `sectors_close_repairs.csv`.

**Hygiene declaration.** *In-sample:* TR23's posteriors (X3, X4, E3–E5, the widget). *Out-of-sample:* the split-half
test on U28 (X1, X5, X6, E7): estimated on the first half, judged on the second; the split was fixed before any result
(LM11's halves); two noise estimates are reported, both. *Stability check:* the reverse direction (E8) and Problem 11's
third noise estimate. *Model:* the Bayes Kelly result and its expected growth (E9, E10, X7), Experiments 1 and 2.
*Hypothetical:* LM13's manager record. LM24 runs no test. Local note: "TAIEX figures describe the total-return index,
3 January 2003 to 8 October 2026 (5,849 daily returns). Sector figures are price indices without dividends, U28's two
halves (2,191 returns each), estimated on the first half and judged on the second unless stated. Every posterior
depends on a prior that the text states; the Kelly results hold inside the stated model, not as advice."

**Notation.** AUTHORING §6 and its Volume IV table (amended 2026-10-19). Used: $R$, $\bar R$, $s$ (divisor $T$),
$s_{\mathrm u}$ (LM21's t-stat only), $\mu$, $\sigma$, $T$, $A$, $N$, $i$, $f$, $f^*$ (the model's Kelly fraction
$\mu/\sigma^2$), $\hat f:=\bar R/s^2$ (from LM20), $\hat f^*$ (the exact in-sample root of (4.5), LM17's 4.1381),
$f_{\mathrm B}$ (the Bayes fraction; $f_{\mathrm B}=c\hat f$ for a prior centred at zero), $c$ (in LM24 the data's
weight), $g(f)$, $\Pr$, $\E$, $\Var$, $\varphi$, $\Phi$, $\mathcal N$, $\chi^2_N$, $\operatorname{Bin}(n,\cdot)$,
$\Gamma$, $\theta$ (the manager's monthly chance of beating the index, a parameter), $\mathcal L(\theta)$,
$\operatorname{Bias}$, $\operatorname{MSE}$, $\operatorname{SE}$, $\eta$ (LM20's scaled-mean factor, §3), $\alpha_0$,
$\beta_0$, $\mu_0$, $\sigma_0$, $\text{t-stat}$ (LM21's), $\tau$ (a horizon in years, §7), densities $f_\theta$,
$f_{\theta\mid\text{data}}$, $f_\mu$, $f_{\mu\mid\text{data}}$. In §3–§4 and §7, $\mu$ is TR23's unknown daily mean
and $\sigma$ its standard deviation, treated as known. Local (accepted, cross-check X20):

| Symbol | Meaning | Check |
|:--|:--|:--|
| $c$ | the data's weight in a posterior mean: $n/(n+\alpha_0+\beta_0)$ in (24.2), $\sigma_0^2/(\sigma_0^2+\sigma^2/T)$ in (24.3), estimated as $\hat c$ in (24.4); §7 shows that it is also $f_{\mathrm B}/\hat f$, the fraction of the plug-in bet the Bayes bet takes | §6's $c$ row, amended 2026-10-19 |
| $n_0$ | the prior's worth in observations: $\alpha_0+\beta_0$ months, or $\sigma^2/\sigma_0^2$ returns, so that $c=T/(T+n_0)$ | subscripted $n$, accepted |
| $n$, $j$ | months observed and good months among them | Volume III's $n$, $j$ |
| $\mu_i$, $\bar R_i$; $\bar{\bar R}$ | sector $i$'s true and sample daily mean; the grand mean $\frac1N\sum_i\bar R_i$ | $\boldsymbol\mu$, $\bar{\mathbf R}$ as §6; the double bar accepted |
| $\hat c$, $\hat\mu_i^{\mathrm{JS}}$ | James–Stein's estimated data's weight and its estimate of $\mu_i$, (24.4) | hats mark estimates |
| $T$ | the returns in the sample at hand: 5,849 (TR23) or 2,191 (a half of U28) | a count throughout |
| $x$ | a generic value of $\theta$ inside the integral of (24.1) | values are lower case |

The slope $\beta$ of (16.8) is cited by its tag; applied here it is written $c$. Not used: $\beta$ or $\alpha$ alone,
$\hat\theta$ (no estimator of $\theta$ is named), $p$, $q$ (the manager's chance is the parameter $\theta$), $\rho$
(correlations in words), $k$, $m$, $\lambda$, $B$, $L$, $P$.

**Motivating case: "Last decade's winners."** (box, about 150 words)

> Split the 28 TWSE sector price indices of [[LM10]] (U28, no dividends) at [[LM11]]'s midpoint. From December 2008
> to October 2017, Automobile led with 21.65% a year; from October 2017 to October 2026 it ranked 20th, at 3.67%
> [A24-07]. ShippingTransportation went from last, 1.89%, to fifth, 17.57% [A24-08]. Across all 28 sectors the two
> halves' mean returns correlate −0.05 [A24-09]. Predict each sector's second half by its own first-half mean, and the
> typical miss is 9.8 points a year; predict every sector by the first half's average of all 28, 10.49% [A24-10], and
> the miss is 8.5 points [A24-11]. The TAIEX's own total return averaged 15.38% a year over 23.8 years ([[LM19]])
> [A24-12], and its plug-in Kelly leverage is 4.28 ([[LM20]]) [A24-13]. [[LM4]] advised betting a quarter to a half
> of that. Should you believe a past mean, and what would a sceptic have to believe to bet so little?

"Typical miss" is the root mean square over the 28 sectors of the gap between prediction and second-half mean, in
points a year, defined in §6. Resolved: (a) why the grand mean wins: §5–§6, E7, X5, X6 (the spread of 28 means is
smaller than their noise, so James–Stein shrinks all the way); (b) believing a past mean: §3–§4, X3, X4 (the posterior
weighs a mean by its precision); (c) the sceptic: §7, E10, X7 (a prior centred at zero with a standard deviation of
2.25 to 3.89 points a year [A24-14] makes the Bayes bet a quarter to a half of 4.28).

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | parameters as uncertain quantities; case + X1; roadmap; notation and hygiene notes; the [[LM30]] sentence | 380 |
| 2 | Bayes' Rule for a Parameter {1} | from LM13's two types of manager to a continuum of $\theta$; prior density, likelihood $\mathcal L(\theta)\propto\theta^j(1-\theta)^{n-j}$ by (13.7), posterior; (24.1); the beta density via (15.8), mean $\alpha_0/(\alpha_0+\beta_0)$; conjugacy, (24.2), the posterior mean as prior mean plus $c$ times the gap, $c=n/(n+n_0)$; the sceptic's prior Beta(82, 82), chosen so that 10.0% of managers have $\theta\ge0.55$ [A24-15], LM13's share, with integer parameters so that every probability is an exact fraction; E1, E2, X2; pitfall: a flat prior is a choice too; 導讀; KC | 620 |
| 3 | The Normal Mean with Known Variance {2} | iid $\mathcal N(\mu,\sigma^2)$ days: $\sum_t(R_t-\mu)^2=\sum_t(R_t-\bar R)^2+T(\bar R-\mu)^2$, so $\mathcal L(\mu)$ depends on the data only through $\bar R$; $(\mu,\bar R)$ is a normal pair by (16.7), and (16.8) gives (24.3) with slope $c$; precision adds; $c=T/(T+n_0)$; Deep Dive (completing the square); TR23: [[LM19]]'s $A\bar R=15.38\%$ and $\sqrt A\,s=18.96\%$, [[LM20]]'s standard error 3.89 points, (20.2) [A24-12]; $\sigma=s$, the normal MLE (20.5); the posterior mean $c\bar R$ is [[LM20]]'s scaled mean: averaging its MSE (20.1) over the prior replaces $\mu^2$ by $\sigma_0^2$ and gives $\eta=c$, and LM20's $\eta^*=0.940$ is $c$ at a prior SD equal to the mean itself [A24-61]; X3 at $c=\tfrac12$ (prior SD equal to the standard error; posterior 7.69% ± 2.75 [A24-16]); E3, E4; (17.5) for non-normal days; pitfall: a prior SD per day or per year; 導讀; KC | 700 |
| 4 | Credible and Confidence Intervals {3} | posterior mean ± 1.96 posterior SD; the credible interval's probability statement against the confidence interval's coverage of a procedure, (20.4); equal under a flat prior; X4; $\Pr(\mu\le0\mid\text{data})$ against [[LM21]]'s one-sided p-value (21.2): LM21's t-stat 3.96 divides by $s_{\mathrm u}$, LM24's posterior by $s$, and the two agree to the printed $3.8\times10^{-5}$; E5; pitfall: reading a confidence interval as a probability for $\mu$; 導讀; KC | 430 |
| 5 | Shrinking Many Means: James–Stein {4} | many means, one prior: $\mu_i\sim\mathcal N(\mu_0,\sigma_0^2)$, $\bar R_i\mid\mu_i\sim\mathcal N(\mu_i,\sigma^2/T)$ independent; the Bayes estimate shrinks each $\bar R_i$ toward $\mu_0$ by $c$; estimate $\mu_0$ by $\bar{\bar R}$ and $c$ from the spread: (24.4), positive part; the theorem with its conditions (independent normal estimates, a common known noise variance, $N\ge4$, total squared error), *stated without proof*; why it can win: each $\bar R_i$ attains (20.7)'s bound among unbiased estimators, and James–Stein accepts bias, (20.1); Deep Dive (why $N-3$); E6 (Experiment 1); Efron and Morris's batting averages (the Stein rule's squared error under half the raw averages'); pitfall: shrinking toward a target chosen after seeing the data; KC | 700 |
| 6 | Sector Means Out of Sample {5} | U28's halves; the noise of a sector mean against the spread of 28 means; E7: $\hat c=0$; correlated errors: the common part of each sector's noise cancels in the spread but not in $\sigma^2/T$, so the theorem's estimate of the weight is biased toward full shrinkage; remove the cross-sectional mean each day: noise 4.8, $1-\hat c=1.01$, still $\hat c=0$ [A24-17] (a market-model alpha, [[LM23]], is another way); what is lost (no dominance theorem; the residuals still sum to zero and co-move); X5, X6; the second half's larger spread (the means moved); E8 (reverse, a stability check); pitfall: searching for a split that shows shrinkage; 導讀; KC | 680 |
| 7 | Kelly with an Uncertain Mean {6,7} | the model (GBM with known $\sigma$, prior $\mathcal N(0,\sigma_0^2)$, log utility, $r_f=0$); posterior-expected growth $f\,\E[\mu\mid\text{data}]-\tfrac12f^2\sigma^2$ for every horizon $\tau$; (24.5); fractional Kelly equals the data's weight, $f_{\mathrm B}=c\hat f$; Browne and Whitt (1996) for the posterior-mean rule; E9, E10, X7; (4.15) prices the plug-in under the posterior; what breaks: a prior centred away from zero, $\sigma$ unknown (negligible at $T=5{,}849$, Gelman et al. §3.3) or changing ([[LM26]]), fat tails (the quadratic rule's gap against $\hat f^*$, E9), other utilities ([[LM44]]); pitfall: the prior is the decision; 導讀; KC | 720 |
| 8 | Bayesian Inference in Python {8} | `stats.beta`; a posterior function; a James–Stein function with `ddof=0` passed; `optimize.brentq` on shifted returns; lab box | 180 |
| — | Summary (7) / Problems (12) / Solutions | | 140 / 380 / 450 |
| | **Total** | | **5,380** |

**Elements.** 10 examples (E1, E2 §2; E3, E4 §3; E5 §4; E6 §5; E7, E8 §6; E9, E10 §7). Knowledge checks:

- §2: prior Beta(2, 2), 3 good months of 4: posterior Beta(5, 3), mean 0.625, $c=\tfrac12$ [A24-18].
- §3: at $A\sigma_0=10$ points the prior is worth 3.59 years of TAIEX data; $c=0.9$ needs nine times that, 32.3 years
  [A24-19].
- §4: which of two sentences describes a credible interval; and why $\Pr(\mu\le0\mid\text{data})$ under a flat prior,
  $3.8\times10^{-5}$ [A24-20], agrees with [[LM21]]'s one-sided p-value to the printed digits although LM21 divides by
  $s_{\mathrm u}$ (X4's last row).
- §5: four means 1, 2, 3, 6 with noise variance 1: $\hat c=13/14$, estimates 1.14, 2.07, 3.00, 5.79 [A24-21].
- §6: 13 of the 28 sectors lay on the same side of the grand mean in both halves [A24-22]; independent halves predict 14
  (half of 28): no persistence beyond chance.
- §7: a prior centred at 8% a year with $A\sigma_0=3.89$ points: posterior mean 11.69%, Bayes fraction 3.25, which is
  0.76 of $\hat f$, not $c\hat f=2.14$ [A24-23].
- §8: `X.var(axis=0)` divides by $T$ in NumPy, Polars' `var()` by $T-1$; with $T-1$, E7's $1-\hat c$ after removing the
  common component is 1.009 instead of 1.008 [A24-24], and $\hat c$ stays 0.

中文導讀 in §2 (貝氏推論, 事前分布, 事後分布, 概度函數 (likelihood function), 共軛事前分布, 貝他(β)分布 (beta
distribution)), §3 (精確度 (precision), 事後分布), §4 (可靠區間 (credible interval) against 信賴區間, p值), §6 (收縮估計量,
經驗貝氏估計量, James-Stein 估計量, 總平均數 (grand mean)) and §7 (分數凱利 (fractional Kelly), LM4's glossary form,
lm04.md:740). 貝他(β)分布, 精確度, 可靠區間, James-Stein 估計量 and 總平均數 are not on plans/vol-4.md's list; they are
樂詞網's 統計學名詞 forms, recorded in SOURCES ("Chinese terms (Volume IV)"). Deep Dives: §3 "Completing the square":
$-\frac{(\mu-\mu_0)^2}{2\sigma_0^2}-\frac{T(\bar R-\mu)^2}{2\sigma^2}$ is a quadratic in $\mu$ with leading coefficient
$-\tfrac12(1/\sigma_0^2+T/\sigma^2)$, so the posterior is normal with that precision and the mean of (24.3), without
(16.8). §5 "Why $N-3$": under the model of §5 the $\bar R_i$ are iid $\mathcal N(\mu_0,\sigma_0^2+\sigma^2/T)$, so
$\sum_i(\bar R_i-\bar{\bar R})^2/(\sigma_0^2+\sigma^2/T)$ has the law $\chi^2_{N-1}$ (Blitzstein and Hwang Ex. 10.4.3);
with the $\chi^2_k$ density (*stated without proof*) and (15.8), $\E[1/\chi^2_k]=\Gamma(k/2-1)/(2\Gamma(k/2))=1/(k-2)$ for $k>2$, so
$(N-3)(\sigma^2/T)/\sum_i(\bar R_i-\bar{\bar R})^2$ is an unbiased estimate of $1-c$.

**Exhibits.**

- X1 `case` (`scatter`, §1): x first-half annual mean, y second-half annual mean (`fmt: "pct1"`), the 28 sectors; `lines`:
  the 45° line labelled "own mean" and the horizontal line at the first half's grand mean, 10.49%, labelled "grand
  mean"; labelled points Automobile, ShippingTransportation, Semiconductor (16.86% → 29.64%, second both times) and
  ElectronicPartsComponents (12.19%, ninth → 31.08%, first) [A24-25]. Note: price indices (no dividends), U28's
  halves, $A=245.4794$ for both; correlation −0.05; root-mean-square miss 9.8 against 8.5 points; out-of-sample.
  Source: FinMind `TaiwanStockPrice`, sector indices, retrieved 11 October 2026, closes repaired from the 13:30:00
  values as in [[LM10]]; Computations: `data/lm24_numbers.py`.
- X2 `manager` (`line`, §2): x $\theta$ from 0.25 to 0.95 (`fmt: "n3"`, `tfmt: "n2"`); y density (`n1`). Series: the
  sceptic's prior Beta(82, 82), its posterior Beta(90, 86), and the flat prior's posterior Beta(9, 5), which is the
  likelihood scaled to unit area. Dashed `vline`s at 0.5 and 0.55. Note: LM13's hypothetical record, 8 good months of
  12; posterior probabilities of $\theta\ge0.55$: 15.3% [A24-26] and 77.2% [A24-27] (E1, E2); exact with
  `Fraction`.
- X3 `normal` (`line`, §3): x annual mean $A\mu$ from −15% to 35% (`pct1`); y density per point. Series: prior
  $\mathcal N(0,3.89^2)$, likelihood $\mathcal N(15.38,3.89^2)$ scaled to unit area, posterior
  $\mathcal N(7.69,2.75^2)$ [A24-16]. Dashed `vline` at 0. Note: TR23, $c=\tfrac12$, the prior worth exactly the sample
  (23.8 years); in-sample.
- X4 `priors` (table, §4): rows $c=\tfrac14$, $c=\tfrac12$, $A\sigma_0=10$ points, flat prior ($\sigma_0\to\infty$).
  Columns: $A\sigma_0$ (points); prior worth $n_0/A$ (years); $c$; posterior mean (% a year, one decimal); 95% credible
  interval; $\Pr(\mu\le0\mid\text{data})$ (two significant figures); Bayes fraction $c\hat f$. Values: 2.25, 71.3, 0.25,
  3.8, 0.0 to 7.7, 0.024, 1.07 [A24-28]; 3.89, 23.8, 0.50, 7.7, 2.3 to 13.1, 0.0026, 2.14 [A24-29]; 10, 3.59,
  0.869, 13.4, 6.3 to 20.5, 0.00011, 3.72 [A24-30]; ∞, 0, 1, 15.4, 7.8 to 23.0, 0.000038, 4.28 [A24-20]. Note:
  every prior is centred at zero; the flat row's interval equals [[LM20]]'s 95% confidence interval, (20.4), and its
  last probability agrees with [[LM21]]'s one-sided p-value to the printed digits (LM21 divides by $s_{\mathrm u}$);
  intervals use $\Phi^{-1}(0.975)$, printed 1.96 as in lm15.md:194 [A24-31]; in-sample; the Bayes fraction is a model
  result.
- X5 `forest` (`scatter`, §6): rows the 28 sectors sorted by first-half mean (y `ticks` 1–28, `tickLabels` the sector
  ids); first-half mean (points) with its iid 95% interval, $\pm\Phi^{-1}(0.975)\,A s_i/\sqrt{2{,}191}$ by (20.4)
  (`lines`), half-widths from 9 to 19 points [A24-32]; second-half mean (points); dashed `segment` at the grand mean,
  10.49%. Note: every interval contains the first half's grand mean [A24-33]; price indices (no dividends); the
  intervals are iid and ignore the common component; the order of rows is listed.
- X6 `oos` (`line`, §6): x the weight $c$ from 0 to 1 (step 0.02, `n2`); y root-mean-square miss (points a year,
  `n1`). Series: estimated on the first half, judged on the second (out-of-sample); estimated on the second, judged on
  the first (stability check). `point`s at $\hat c$: 0 forward (both noise estimates), 0.25 and 0.59 reverse. Values:
  forward 8.5 at $c=0$ and 9.8 at $c=1$; reverse 4.5, 5.1, 6.9, 9.8 at $c$ = 0, 0.25, 0.59, 1 [A24-34].
- X7 `kelly` (`line`, §7): x $A\sigma_0$ on the approved log axis, 1 to 50 points (ticks 1, 2, 5, 10, 20, 50; `x.fmt:
  "n2"`); y fraction 0–4.5 (`n2`). Series: $c\hat f$ (quadratic) and the exact fraction on shifted returns; dashed
  `hline`s at $\hat f=4.28$ and LM17's $\hat f^*=4.14$ (lm17.md:239); dashed `vline`s at 2.25 ("quarter Kelly"), 3.89
  ("half Kelly") and 10. Values cited: X4's fractions 1.07, 2.14 and 3.72 at the three dashed `vline`s and the exact
  2.11 [A24-35] and 3.62 [A24-36] at the last two (E9). Note: the model of §7; TR23's returns shifted to the
  posterior mean; 61 log-spaced values; the gap between the series is the fat tails' effect on the fraction.

**Widget `posterior` — "Prior, data and the Bayes bet."** `Book.controls`: prior SD $A\sigma_0$ (0.5–30 points, step
0.5, initial 10); years of data (1–100, step 0.01, initial TR23's span from the data block, shown as 23.76; the writer
checks that `Book.controls` keeps an initial value off its step grid, or uses step 0.0001); prior mean $A\mu_0$ (−10
to 20 points, step 1, initial 0). `line` chart, x annual mean −20% to 40%: prior, likelihood (scaled to unit area),
posterior; dashed `vline` at the posterior mean. Readouts: standard error $\sqrt A s/\sqrt{\text{years}}$; $c$;
posterior mean and SD; 95% credible interval; $\Pr(\mu\le0\mid\text{data})$ with `Book.dist.Phi`; the Bayes fraction
$\E[\mu\mid\text{data}]/\sigma^2$ (annual units: posterior mean over $A s^2$) and its ratio to $\hat f$, which equals
$c$ only when the prior mean is 0. Data block `chart-lm24-posterior`: $A\bar R$, $\sqrt A s$, years and $\hat f$
[A24-37]. TR23's mean and volatility stay fixed while the years change: a hypothetical, as the note says. No
simulation, no `Book.rng`. Initial state (PDF): X4's third row, $c=0.869$, posterior 13.4% ± 3.6, interval 6.3% to
20.5%, fraction 3.72 [A24-37].

**Examples** (results recomputed from the printed inputs):

- E1 §2, the manager with the sceptic's prior Beta(82, 82): it gives 10.0% of managers $\theta\ge0.55$, LM13's
  two-point share ($a=81.96$ solves it exactly; the integer keeps every probability an exact fraction); its standard
  deviation is 0.039 [A24-15], and $n_0=164$ months. After 8 good months of 12 the posterior is Beta(90, 86): mean
  $45/88=0.5114$, $c=12/176=3/44=0.068$, $\Pr(\theta\ge0.55\mid\text{record})=15.3\%$ [A24-26], against LM13's
  two-point 13.5% (lm13.md:334). The record moves the mean by 0.0114 because twelve months weigh 6.8% against the
  prior's 164.
- E2 §2, the flat prior Beta(1, 1): posterior Beta(9, 5), mean $9/14=0.643$, $c=6/7$; $\Pr(\theta>0.5)=7{,}099/8{,}192=
  86.7\%$ exactly, $\Pr(\theta\ge0.55)=77.2\%$, 95% interval 0.39 to 0.86 [A24-27]. How long a record convinces the
  sceptic? With two good months in three, $\Pr(\theta\ge0.55)$ first exceeds one half at 72 months, 51.2% (49.4% at 69),
  when $c=0.305$ [A24-38].
- E3 §3, TR23 with $A\sigma_0=10$ points: $c=10^2/(10^2+3.89^2)=0.869$, with [[LM20]]'s standard error 3.89;
  posterior mean $0.869\times15.38=13.4\%$, SD $\sqrt{0.869}\times3.89=3.6$ points [A24-39]; with [[LM19]]'s 18.96%
  the prior is worth $(18.96/10)^2=3.59$ years of data; at $c=\tfrac12$ it is worth the whole sample, 23.8 years, and
  at $c=\tfrac14$ three times it, 71.3 years [A24-40]. (17.5) makes $\bar R$ approximately normal although days are
  not; the iid standard error ignores clustering (robust errors of a mean are [[LM22]]'s and [[LM23]]'s).
- E4 §3, (16.6) at $A\sigma_0=10$: the prior variance, 100 points², splits into $\Var(\E[\mu\mid\bar R])=c\sigma_0^2=86.9$
  and $\E[\Var(\mu\mid\bar R)]=(1-c)\sigma_0^2=13.1$ [A24-41]: before the data, most of the prior's variance is
  variance of the coming posterior mean.
- E5 §4: flat prior, $15.38\%\pm1.96\times3.89$: 7.8% to 23.0%, numerically [[LM20]]'s confidence interval;
  $\Pr(\mu\le0\mid\text{data})=\Phi\big(-\bar R/(s/\sqrt T)\big)=3.8\times10^{-5}$. [[LM21]]'s one-sided p-value, (21.2)
  at its t-stat 3.96, divides by $s_{\mathrm u}$ instead of $s$; the two differ only by that divisor and agree to the
  printed digits [A24-20]. At $A\sigma_0=10$: 6.3% to 20.5% and $1.1\times10^{-4}$; the quarter-Kelly sceptic still
  puts 97.6% on $\mu>0$ [A24-28].
- E6 §5, Experiment 1 (*Model*, `default_rng([1, 20261011])`, 10,000 cross-sections of $N=28$ means, spread $\sigma_0$
  equal to the noise, both 1): average total squared error 28.1 for the raw means, 15.5 for James–Stein and for its
  positive part, 14.0 for the Bayes rule that knows $\mu_0=0$ and $c=\tfrac12$; standard errors 0.04 to 0.08; mean $\hat
  c$ 0.50 [A24-42]. Theory: 28, $28-25/2=15.5$, 14 [A24-43].
- E7 §6, U28, first half: the noise of a sector mean is 7.2 points a year (root of the average $s_i^2/T$, annualized);
  the 28 means spread by 4.5 points (divisor 28); $1-\hat c=25\times\text{noise}^2/\sum(\cdot)^2=2.27$, so $\hat c=0$
  [A24-44]. With the cross-sectional mean removed each day the noise falls to 4.8 points and $1-\hat c=1.01$: $\hat
  c=0$ again, by a hair [A24-17]. Judged on the second half, the grand mean misses by 8.5 points and the own means
  by 9.8; the best weight in hindsight is −0.09 [A24-45]: deviations reversed slightly. The second half's means spread
  by 8.5 points [A24-46], almost twice the first half's: the true means moved, and no first-half estimate could know
  where.
- E8 §6, the reverse (*Stability check*): estimated on the second half, $\hat c=0.25$, or 0.59 with the common component
  removed; judged on the first half, full shrinkage still does best, 4.5 points against 5.1, 6.9 and 9.8 (X6).
- E9 §7, TR23 at $A\sigma_0=10$: $f_{\mathrm B}=0.869\times4.28=3.72$; on returns shifted to the posterior mean the
  exact fraction is 3.62, and maximizing the growth averaged over the posterior gives 3.62 too [A24-36]. The posterior
  SD of the model's full-Kelly fraction $f^*=\mu/\sigma^2$ is 1.01 ([[LM20]]'s mean-only 1.08, shrunk by $\sqrt c$), so
  $f^*$ lies between 1.7 and 5.7 with 95% posterior probability [A24-47]. The quadratic rule's excess over the exact
  fraction is 0.14 at $c=1$ (4.28 against LM17's $\hat f^*=4.14$), 0.10 at $c=0.869$ and 0.03 at $c=\tfrac12$ (2.14
  against 2.11) [A24-35]: the fat tails shave a few per cent off a fraction, the prior shaves 13%. Expected log growth
  in the model: about 25% a year at $f_{\mathrm B}$; the plug-in keeps 97.7% of it, $1-(1-1/0.869)^2$ by (4.15)
  [A24-48].
- E10 §7, LM4's sceptic: $c=\tfrac14$ needs $A\sigma_0=3.89/\sqrt3=2.25$ points, a prior worth 71.3 years; $c=\tfrac12$
  needs 3.89, worth the sample. Both sceptics put high probability on a positive mean, 97.6% and 99.7%, yet bet
  little: size depends on how large the mean is, not only on its sign. Under the half-Kelly sceptic's posterior the
  plug-in bet is twice Kelly and expects zero growth, against 8.2% a year at 2.14; under the quarter-Kelly sceptic's
  it is four times Kelly and expects −16.5% a year, −8 times the Bayes bet's 2.06% [A24-49]. LM4's rule of thumb is
  the Bayes bet of a sceptic whose prior is worth as much as the 23.8 years of data (half Kelly) or three times as much
  (quarter Kelly).

**Problems plan** (12; MC keys B, C, A, B, A, C; the lab solves 9–12). Stems state the sample (TR23, 3 January 2003 →
8 October 2026, $T=5{,}849$, $A=246.12$; or U28's halves, price indices, $A=245.4794$), the divisor ($T$), the prior's
centre and SD on the annual scale, rounding, and for a simulation the seed, the draws and their order. No problem tests
a hypothesis.

1. MC: prior Beta(3, 7), 4 successes in 6 independent trials; posterior mean. A 0.667 (4/6, the data alone). **B**
   0.4375 (7/16). C 0.700 (7/10, $n$ left out of the denominator) [A24-50].
2. MC: prior SD 6 points a year, standard error of the annual mean 4 points; the data's weight. A 0.60 (a ratio of
   standard deviations). B 0.31 (the prior's weight, 16/52). **C** 0.69 (36/52) [A24-51].
3. MC: the posterior SD in Problem 2. **A** 3.33 ($1/\sqrt{1/36+1/16}$). B 7.21 (adds the variances). C 2.40 (combines
   standard deviations as if they were variances, $6\times4/10$) [A24-52].
4. MC: James–Stein with $N=10$ means, noise variance 1, sum of squared deviations 18; $\hat c$. A 0.556 ($N-2$, the
   rule toward a fixed point). **B** 0.611. C 0.389 (reports $1-\hat c$) [A24-53].
5. MC: plug-in fraction 3.0, prior centred at zero, $c=0.4$; the Bayes fraction. **A** 1.20. B 1.90 ($\sqrt c$). C 0.48
   ($c^2$) [A24-54].
6. MC: under a posterior with $c=\tfrac12$, the plug-in bet's expected growth as a share of the Bayes bet's, by (4.15).
   A 75% (half Kelly read the wrong way round). B 50%. **C** 0 (the plug-in is twice Kelly) [A24-55].
7. Derive (24.3) by completing the square, then check (16.6) at $A\sigma_0=10$: 100 = 86.9 + 13.1 (E4).
8. Under §5's model, show that $(N-3)(\sigma^2/T)/\sum_i(\bar R_i-\bar{\bar R})^2$ is unbiased for $1-c$, using the
   $\chi^2_{N-1}$ law (Blitzstein and Hwang Ex. 10.4.3) and $\E[1/\chi^2_k]=1/(k-2)$, derived from the density (stated
   without proof) and (15.8).
9. TR23 with a prior centred at zero, $A\sigma_0=5$ points, from the printed 15.38%, 3.89 and 18.96%: $c=0.623$;
   posterior mean 9.6%, SD 3.1; 95% interval 3.6% to 15.6%; $\Pr(\mu\le0)=0.0009$; Bayes fraction 2.67; prior worth 14.4
   years [A24-56].
10. Python, Experiment 2 (`default_rng([2, 20261011])`, 20,000 cross-sections of 28 means at each spread 0, 1, 3, in
    that order, noise 1; at each spread the true means are drawn as spread × standard normal, even at spread 0, then
    the noise): average squared error of the raw means, James–Stein and its positive part: 28.0, 3.0, 2.1; 28.0, 15.5,
    15.5; 28.0, 25.5, 25.5, standard errors 0.02 to 0.05 [A24-57]; compare $N-(N-3)/(1+\sigma_0^2)$ = 3, 15.5, 25.5,
    and say where the positive part helps.
11. Python, U28: repeat E7 with the TAIEX removed each day instead of the cross-sectional mean: noise 5.0 points,
    $1-\hat c=1.1$, $\hat c=0$; the miss of the grand mean becomes 12.1 points because the sectors' average excess over
    the TAIEX moved from −0.3 to −9.0 points (the TAIEX rose 10.8% then 19.1% a year), while the deviations' miss stays
    8.5 [A24-58]. (*Stability check.*)
12. LM13's Practice Problem 8 with the sceptic's prior: 16 good months of 24 give Beta(98, 90) and
    $\Pr(\theta\ge0.55)=21.6\%$ [A24-59], against the two-point 18.02% (lm13.md:530); explain the difference.

**Lab parts** (`build/make_lab24.py`, reads only its `data/`: `taiex_tr.csv`, `sectors_close_raw.csv`,
`sectors_close_repairs.csv`): 1 data: TR23 from the closes, $T$, years, $A$, $\bar R$, $s$; U28 from the sector files
with [[LM16]]'s repair cell, the halves; 2 the beta–binomial with `stats.beta` and exact `Fraction`s, E1, E2, X2; 3 a
`posterior(c)` function, E3, E4, X3, X4; 4 credible intervals and $\Pr(\mu\le0)$, E5; 5 a `james_stein` function
(`ddof` passed), Experiment 1, E6; 6 U28's halves, E7, E8, X1, X5, X6; 7 the Bayes fraction with `brentq` on shifted
returns, X7, E9, E10; 8 problems 9–12. Extension (*Stability check*): split U28 into thirds of 1,461, 1,461 and 1,460
returns (`np.array_split`) [A24-60], estimate on each third and judge on the next, and say why a second split is
not a new test. Labs write "LM20", never `[[LM20]]`.

**Cross-module tags.**

- (24.1) $f_{\theta\mid\text{data}}(\theta)=\mathcal L(\theta)f_\theta(\theta)/\int\mathcal L(x)f_\theta(x)\,dx$; the
  prior is a density and the integral is finite and positive (LM30, LM45).
- (24.2) a $\operatorname{Beta}(\alpha_0,\beta_0)$ prior and $j$ successes in $n$ independent trials with probability
  $\theta$ give $\operatorname{Beta}(\alpha_0+j,\beta_0+n-j)$; posterior mean $=$ prior mean $+\,c\,(j/n-$prior mean$)$,
  $c=n/(n+\alpha_0+\beta_0)$ (LM45).
- (24.3) iid $\mathcal N(\mu,\sigma^2)$ returns with $\sigma$ known and a prior $\mathcal N(\mu_0,\sigma_0^2)$:
  $\mu\mid\text{data}\sim\mathcal N\big(\mu_0+c(\bar R-\mu_0),\,c\sigma^2/T\big)$, $c=\sigma_0^2/(\sigma_0^2+\sigma^2/T)
  =T/(T+n_0)$, $n_0=\sigma^2/\sigma_0^2$; precisions add (LM30's Black–Litterman, LM44, LM45).
- (24.4) $\hat\mu_i^{\mathrm{JS}}=\bar{\bar R}+\hat c(\bar R_i-\bar{\bar R})$,
  $\hat c=\max\big(0,1-(N-3)(\sigma^2/T)/\sum_i(\bar R_i-\bar{\bar R})^2\big)$; for $N\ge4$ independent normal means with
  a common known variance $\sigma^2/T$, its expected total squared error is below the raw means' for every
  $\boldsymbol\mu$ (stated without proof; the source toward the grand mean is an open point) (LM30).
- (24.5) $f_{\mathrm B}=\E[\mu\mid\text{data}]/\sigma^2=c\hat f$ for a prior centred at zero; GBM with known $\sigma$,
  log utility, $r_f=0$, any horizon; for daily returns, the second-order version of (4.2) without $\mu^2$ (LM44, LM45).

**Pitfalls to pre-empt.**

- Conditions every time: (24.3) needs $\sigma$ known and normal (or, by (17.5), approximately normal) $\bar R$; (24.4)
  needs independent estimates with a common known variance and $N\ge4$; (24.5) needs a prior centred at zero for the
  "fraction" reading.
- Units: $\sigma_0$ is per day in the formulas; the text gives $A\sigma_0$ in points a year. $c$ is a ratio of
  variances, never of standard deviations (Problem 2).
- One owner per statistic: $\bar R$, $s$ are [[LM14]]'s; $A\bar R=15.38\%$ and $\sqrt A\,s=18.96\%$ [[LM19]]'s; the
  standard error 3.89, the confidence interval, $\hat f=4.28$ and its delta-method errors [[LM20]]'s; the t-stat 3.96
  (with $s_{\mathrm u}$) and its p-value [[LM21]]'s; $\hat f^*=4.14$ [[LM17]]'s; the posteriors, the weights, the
  Bayes fractions and the James–Stein factors are LM24's.
- Divisors: `ddof=0` passed everywhere; the cross-sectional SD names its divisor 28; Polars' `var()` divides by
  $T-1$ (KC §8); LM21's t-stat uses $s_{\mathrm u}$, LM24's posterior $s$ (KC §4).
- Rounding: every printed value within a tenth of a unit of a rounding boundary is flagged in its anchor row at each
  precision it is printed (A24-03, 12, 14, 19, 21, 25–28, 30, 37, 42, 47, 49, 53, 57–59), and printed forms are
  rounded from unrounded values. Annual posterior figures print to one decimal, because $0.869\times15.38$ and
  $\sqrt{0.869}\times3.89$ give 13.37 and 3.63 at two decimals against 13.36 and 3.62 unrounded. $A\sigma_0$ for
  $c=\tfrac14$ prints 2.25, which the unrounded 2.24517 and both printed routes ($3.89/\sqrt3$, $3.9/\sqrt3$) give.
  The case's annual sector means print two decimals (21.65% is 21.6499%). Two Monte Carlo averages sit within a tenth
  of a unit of a boundary with a larger standard error (E6's James–Stein 15.542, SE 0.045; Problem 10's raw 28.046, SE
  0.053): the text prints their standard errors and the theory values beside them.
- Hygiene: the split is LM11's, fixed in advance; the reverse is a stability check, not a second test; "James–Stein
  shrank fully" is a statement about these 28 means, not a law; never call the Bayes fraction advice.
- Data traps: price indices without dividends; U28's $A$ for both halves; the TAIEX in the case is the total-return
  index (TR23), never the price index of U28.
- Notation: (16.8)'s $\beta$ becomes $c$; $\theta$ is a parameter (no angle); no $p$ for the manager's chance;
  $\hat f^*$ (LM17's in-sample root of (4.5)) is not $f^*$ (the model's $\mu/\sigma^2$).
- References (SOURCES; open points marked): Bayes' rule for a parameter and the normal model, Gelman et al. (2013),
  §2.5, (2.10) (open: re-read before printing), §3.3 for unknown $\sigma$ (open: only its title is checked); James and
  Stein (1961) (open: end page) and a read source for the dominance theorem toward the grand mean (open); Blitzstein
  and Hwang Ex. 10.4.3 for the chi-square law (its density *stated without proof*); Efron and Morris (1975), read, for the batting
  averages; Efron and Morris (1973), bibliographic only, for the empirical-Bayes view; Browne and Whitt (1996),
  abstract, for the posterior-mean rule; Thorp (2006) §7.3 and MacLean, Thorp and Ziemba (2010) for prudential
  fractional Kelly; Rising and Wyner (2012), abstract, for "reduced estimation error"; Jorion (1986) named only (open:
  target); Chopra and Ziemba (1993) for errors in means.

**Stage 4 for earlier modules.** `leads` gain 24 in lm04.md:6 (already on plans/vol-4.md's list), lm10.md:6,
lm11.md:6, lm14.md:6, lm15.md:6 and lm17.md:6 (lm13.md:6 and lm16.md:6 already list 24), as in the plan's Stage 4
table. No wording changes: lm13.md:336 and lm04.md:558 read correctly once §2 and §7 exist. In Volume IV, LM19's leads
gain 24 and LM23's lose it (cross-check X1, X6).

**The spine's open choices, settled.** The James–Stein variant is the positive-part rule toward the grand mean, with
$N-3$ and one common noise variance, the average of the 28 sectors' $s_i^2/T$, treated as known (2,191 returns make its
own error small); its source equation is an open point (below). Removing the common component (each day's
cross-sectional mean) is the fairer test of the weight and gives the same verdict (E7; accepted, cross-check §8). The
data give no partial-shrinkage example (accepted): E8's reverse direction is a stability check, and E6 (simulated)
and Efron and Morris (1975) show shrinkage working. The derivation's approximation is LM4's second-order growth, exact
under GBM; on TR23 it overstates the fraction by 0.14 at full Kelly and 0.10 at $c=0.869$ (E9).

**Open before Stage 2** (open in SOURCES; until then the text is written as the decisions say):

- (a) A read source for the James–Stein dominance theorem toward the grand mean with $N-3$, $N\ge4$, and the positive
  part (cross-check X34 d): Efron and Morris (1973) is bibliographic only, Efron and Morris (1975) was read for its
  Table 1, Wasserman §12.7 is known from the contents only. Until then (24.4)'s theorem is *stated without proof*.
- (b) The $\chi^2_k$ density: Blitzstein and Hwang's Gamma density (§8.4) is unread, so the density stays *stated
  without proof* (Deep Dive, Problem 8); the $\chi^2_{N-1}$ law itself is cited to Ex. 10.4.3.
- (c) Gelman et al. §3.3 for the posterior under unknown $\sigma$ (X34 e) and (2.10) re-read; James and Stein's (1961)
  end page; Jorion's (1986) target (named only, so it blocks nothing).

## LM25 Time Series I: ARMA, Unit Roots and Cointegration

Stage 1 brief, revised 2026-10-19 after the cross-check and the independent recomputation. Drafted the same day from
the editor's spine (`plans/vol-4.md` at commit bcfa0d4, "### LM25") and revised to the editor's decisions ("Editor's
decisions on the LM19–LM25 drafts") and the fresh check. Each number carries its anchor ID at its first appearance;
`data/vol4_anchors_lm25.py` prints them all (rows in `plans/vol-4-anchors.md`: 72 rows, A25-69 withdrawn). Numbers quoted from published modules carry
their file:line instead. Tags of LM19–LM23 are cited as their Stage 1 briefs number them.

**Prereq:** `[3, 6, 12, 16, 17, 18, 19, 20, 21, 23]`. The spine's draft list plus LM3, LM17 and LM18, which the text
cites for a result (accepted, cross-check §8).

- LM3: $\ln S$ as a random walk (lm03.md:534, the quadratic-variation Deep Dive); LM25 states the model it named.
- LM6: (6.22) $F=Se^{(r_f-q)\tau}$ (lm06.md:523); (6.24) the implied $q\tau$ (lm06.md:537); (6.25) carry − dividends +
  residual (lm06.md:583); realized dividends $q_{\text{real}}\tau$ from the total-return index (lm06.md:564–568); the
  2% proxy (lm06.md:585); $\tau$ in days/365 (lm06.md:658); settlement by rule on thin days (lm06.md:605–607); the
  13:30/13:45 timing pitfall and annualized noise (lm06.md:671–676); the 27 June 2025 extreme (lm06.md:601–603); the
  2025 monthly table and its 83.4-point daily-change SD (lm06.md:611–624); MacKinlay and Ramaswamy (lm06.md:648); the
  promise (lm06.md:650).
- LM12: (12.1) the normal equations and $\hat{\boldsymbol\beta}=(X^{\top}X)^{-1}X^{\top}\mathbf y$ (lm12.md:89); (12.3)
  the slope from covariances (lm12.md:120); (12.4) R-squared (lm12.md:126).
- LM16: (16.1) independence (lm16.md:129); (16.2) covariance and correlation (lm16.md:142); (16.3) the variance of a
  sum (lm16.md:197), used for the random walk, the robust band and the variance ratio.
- LM17: (17.5) the central limit theorem (lm17.md:276), the normal approximation behind every band; its pair
  correlations 0.039 of $r$ and 0.161 of $\lvert r\rvert$ (lm17.md:392), named once beside [[LM19]]'s $\hat\rho_1$.
- LM18: (18.2)–(18.3) the Monte Carlo standard error (lm18.md:141–147); batch standard errors with divisor 20
  (lm18.md:153).
- LM19: (19.5) $\hat\rho_k$ (full-sample mean, divisor $T$); (19.6) the iid band $\pm1.96/\sqrt T$; (19.7) the
  variance of an $m$-day sum and the model's ratio $1+2\sum_{k<m}(1-k/m)\rho_k$ (no symbol); (19.8) the overlapping
  estimator $\operatorname{VR}(m)$; TR23's $\hat\rho_k$ of $r$ and $\lvert r\rvert$ (0.0393 and 0.161 at lag 1).
- LM20: (20.6) asymptotic normality of the MLE, standard errors from $-\ell''$; (20.8) the delta method.
- LM21: (21.2) p-values; the rule that every test reports how many tests ran on the same data.
- LM23: (23.1) OLS and (23.2) its classical variance (the AR and DF regressions, E4's classical SE); (23.3)
  $s_\varepsilon^2=\text{RSS}/(T-d)$; (23.4) t-stats; (23.6) the sandwich and White's HC0 errors; spurious regression
  is left to LM25.

**Leads:** `[26, 33, 34, 36, 39]` (cross-check X26): pointer targets in the text (LM26 models the clustering that
widens the band; LM33 the Sharpe ratio under autocorrelation; LM34 tests on later data, named in the hygiene note;
LM36 Brownian motion, the DF statistic's limit; LM39 the Ornstein–Uhlenbeck process, the continuous-time AR(1)) and the
probable tag users listed under "Cross-module tags".

**Forward links honoured.** A grep of `src/lm*.md`, `src/pages/*.md` and `build/make_lab*.py` for "LM25" finds one
link, lm06.md:650, the spine's. The other rows are the spine's "stay consistent" items and two plan-level mentions.

| Earlier text | Promise | Kept in |
|:--|:--|:--|
| lm06.md:650 | "[[LM25]] models it as a mean-reverting spread" | §7: (6.25)'s residual in log form, tested (X8, E9) and modelled (E10); §4 the AR(1) and its half-life; §6 cointegration with a known vector |
| lm06.md:583–585, 658 | (6.25); the 2% proxy; $\tau$ = days/365 | §7: the fair log basis $r_f\tau-q_{\text{real}}\tau$ and the log residual on the same conventions |
| lm06.md:601–603 | 27 June 2025 the extreme of 146 sessions; −461 average; negative on 131 | cited, not recomputed; LM25's sample-wide view in E9 |
| lm06.md:611–624 | the 2025 monthly table; daily changes SD 83.4 points | §7: X6 averages 2003–2026 by calendar month; E10's 2025 check |
| lm06.md:671–676 | settlement from the last minute before 13:45; annualizing noise | §7: the one-day noise $\sigma_u$ of E10 and the widget; the pitfall cites lm06.md:676 |
| lm06.md:605–607 | settlements set by rule on thin back months | §1, Data role: TX23 holds the near month only (median volume 81,889 [A25-05]) |
| lm15.md:100–103; lm16.md:168; lm17.md:392 | lag-1 values 0.0215 (down-day indicators, TR23), 0.040 (U28 price index), 0.039 and 0.161 (TR23 $r$ and $\lvert r\rvert$) | §3: $\hat\rho_1$ of $r$ (0.0393) and of $\lvert r\rvert$ (0.161) are [[LM19]]'s [A19-38, A19-39], which LM17's pair correlations (lm17.md:392) match; the other two are other statistics or samples and are not compared |
| plans/vol-3.md:321 (LM13's frozen brief) | "Autocorrelation → LM25" | superseded by the Stage 1 decision: LM19 owns $\hat\rho_k$ and $\operatorname{VR}(m)$; LM25 the robust band, Ljung–Box and the variance-ratio test |
| syllabus.yaml:66 | "Stationarity, mean reversion, the futures–spot basis." | §2, §4, §7 |

**Outcomes** ("After this module you should be able to:"):

1. define weak stationarity, white noise and a random walk, and explain why a price level is not stationary while its changes can be
2. test a return series for autocorrelation with the iid and the robust bands, the Ljung–Box test and the variance-ratio test, and explain how volatility clustering changes the verdict
3. derive the autocorrelations and partial autocorrelations of AR(1) and MA(1) models, estimate an AR(1) by least squares and convert its coefficient into a half-life
4. explain why the Dickey–Fuller t-stat does not follow a $t$ distribution, and apply the augmented test with MacKinnon p-values and the KPSS test of the reverse null
5. explain why regressions between independent random walks look significant, and test cointegration with a known vector and with an estimated one
6. decompose the TX–TAIEX log basis into convergence at expiry, roll jumps, the dividend season and one-day noise, and measure how fast it reverts
7. run these tools in Python with statsmodels on NumPy arrays, matching each package result to a calculation by hand

**Owns.** Weak stationarity; white noise against iid noise; the random walk and its variance $t\sigma^2$ (from
(16.3)); AR(1) moments, $\rho_k=\phi_1^k$ and the half-life $\ln\frac12/\ln\phi_1$; MA(1) autocorrelations;
partial autocorrelation as the last coefficient of an AR($k$) regression; ARMA(1,1) named and fitted on the basis at
the likelihood maximum; AR estimation by OLS; the signal-plus-noise reading of ARMA(1,1)
($\sigma_u^2=-\theta_1\sigma_\eta^2/\phi_1$); the robust (HC0-type) standard error of $\hat\rho_k$ (derived in a Deep
Dive) and the robust band; Ljung–Box; the variance-ratio test of LM19's $\operatorname{VR}(m)$ in its iid and robust
forms, a large-sample approximation; the Dickey–Fuller regression and t-stat, its null distribution by simulation, ADF
lags, MacKinnon p-values; KPSS in one paragraph; spurious regression by simulation; cointegration, the known vector
$(1,-1)$ for the basis and Engle–Granger for an estimated one, with the error-correction model in two sentences; the
basis's convergence at expiry, roll jumps and dividend season as a seasonal mean; the four versions of the basis
tested (X8); TR23's robust band counts, Ljung–Box and variance-ratio test statistics; every TX23 statistic printed
here.

**Leaves.**

- Sample autocorrelations of TR23 ($r$, $\lvert r\rvert$, $r^2$), the iid band, $\operatorname{VR}(m)$ (19.8), its
  values beyond $m=20$ and the identity column → LM19 (LM25 recomputes $\hat\rho_k$ and $\operatorname{VR}(m)$,
  $m\le20$, under LM19's tags).
- A block-bootstrap interval for a variance ratio → LM22.
- Regression standard errors, HAC → LM23 (cited); LM25 uses classical and White (HC0) errors only where named.
- Volatility models, ARCH tests, Ljung–Box on squared residuals → LM26 (one sentence: $\lvert r\rvert$'s Ljung–Box
  statistic 1,820 [A25-22]).
- The Sharpe ratio under autocorrelation → LM33. Tests on later data → LM34.
- Ornstein–Uhlenbeck in continuous time → LM39.
- Johansen's test and threshold cointegration → named, one sentence each (Johansen 1988, 1991; Dwyer, Locke and Yu
  1996; Lin, Chen and Hwang 2003 for Taiwan). Pairs trading → not in the book, one sentence. ARMA($p$,$q$) order
  selection, AR(2) and seasonal ARIMA → not in the book (cut for length, as the spine's check asked).

**Uses before taught** (one sentence each in the text):

- §3: "The band uses the normal approximation of [[LM17]]'s (17.5); [[LM19]] defined $\hat\rho_k$ (19.5) and drew the
  iid band (19.6)."
- §3: "The robust standard error is HC0-type, the lag-$k$ version of [[LM23]]'s White errors (23.6)."
- §3: "[[LM19]]'s identity column shows $\operatorname{VR}(m)-1$ close to $2\sum_{k<m}(1-k/m)\hat\rho_k$; the test's
  variance is that sum's, so the test is a large-sample approximation."
- §3, §5: "A test, its null hypothesis and its p-value are [[LM21]]'s (21.2); here every p-value comes with the number
  of tests run on the same data."
- §4: "OLS and its classical standard error are [[LM23]]'s; the estimate is (12.1) with a constant and one lagged
  value."
- §7: "statsmodels fits ARMA(1,1) by maximum likelihood ([[LM20]]); its default optimizer stops short of the maximum
  here, so the fit starts from `method="innovations_mle"` and checks that a restart does not raise $\ell$. Standard
  errors come from the curvature $-\ell''$, (20.6), whose large-sample law for a stationary, invertible ARMA is
  *stated without proof*."
- §5: "The DF statistic's limit is a functional of Brownian motion ([[LM36]]); here it is simulated."
- §7: "In continuous time a mean-reverting spread is an Ornstein–Uhlenbeck process ([[LM39]])."
- §2: "Volatility that changes over time is modelled in [[LM26]]; white noise here only needs a constant variance."

**Data role.**

- **TX23** (`data/processed/vol4_tx23.parquet`, built and checked by `data/vol4_series.py`; FinMind
  `TaiwanFuturesDaily` TX, regular session, monthly contracts, retrieved 2026-10-19; TAIEX price closes
  `TaiwanStockPrice`, retrieved 2026-10-11 and 2026-10-18): 5,850 dates [A25-01], 2003-01-02 → 2026-10-08, 285 rolls,
  286 contracts held; 5,849 daily changes [A25-02]. $F_t$ is the settlement of the near-month contract held from
  that close, rolled at the close of the day before each contract's last trading day (LM2's rule), so no expiry day
  enters; $S_t$ the TAIEX price close (TR23's `price`); $b_t=\ln F_t-\ln S_t$. "Rolled" changes difference the stored
  series; "roll-free" changes are `rF − rS` (one contract). Near-month volume 2,382 to 409,245 contracts, median
  81,889 [A25-05].
- **D** (the dividend sample): the 5,834 TX23 dates [A25-04] whose held contract's last trading day lies in the sample
  (2003-01-02 → 2026-09-14); the last 16 dates hold contract 202610, which expires after 2026-10-08. Realized
  dividends $q_{\text{real}}\tau=\ln(\mathrm{TR}_L/\mathrm{TR}_t)-\ln(S_L/S_t)$, $L$ the last trading day, from TR23's
  total-return index (`tr`); $\tau$ = calendar days to $L$ / 365; $r_f=2\%$. D carries X6, X7, X8 and E9.
- **TR23** log returns $r_t=\ln(1+R_t)$ (`data/processed/vol3_taiex.parquet`, `data/vol3_series.py`): $T=5{,}849$,
  2003-01-03 → 2026-10-08; 8,680 days, 23.764545 years, $A=246.12$ [A25-03]. LM25 annualizes nothing; a simulated
  year has $\operatorname{round}(A)=246$ sessions.
- **Limit regimes** (stability check): TX23 split at 2015-06-01, 3,078 and 2,772 dates [A25-15]. A window's
  statistic uses its own dates only; its changes are differences within the window.
- **Cleaning:** none beyond `vol4_series.py`'s checks; no TX23 date is dropped. Basis statistics in bp ($10^{-4}$ log
  units), divisor $T$ for $s$, $T-d$ for $s_\varepsilon$. Counts against a threshold use the guard ($b_t<-10^{-12}$)
  and `Fraction` on the whole-point settlements and two-decimal closes: $F<S$ on 4,051 of 5,850 dates, $F=S$ on one
  [A25-09]. Medians and quantiles are $\hat F^{-1}(u)$ (`method="inverted_cdf"`).
- **Tests:** two-sided with a normal reference unless named; Dickey–Fuller, ADF and Engle–Granger are one-sided (small
  values reject), KPSS one-sided (large values reject), Ljung–Box the upper tail of $\chi^2_K$; the variance-ratio
  test is two-sided. Each test says so where it appears.
- **Seeds:** `rng = np.random.default_rng([e, 20261011])`, created once per experiment: 1 the Dickey–Fuller null at
  5,850 levels (10,000 walks; X4, E5); 2 spurious regressions at 5,850 sessions (1,000 pairs; the first pair is X5's;
  E7); 3 the DF null at 246 levels (100,000 walks; Problem 10, widget); 4 spurious regressions at 246 sessions (1,000
  pairs; Problem 11). A walk of $n$ levels is $x_t=z_1+\dots+z_t$, $t=1,\dots,n$, with iid standard normal $z_t$;
  walks are drawn in chunks of 500 rows (`standard_normal((500, n))`, cumulated along rows), a pair as
  `standard_normal((2, n))`, $x$ before $y$, one pair at a time. Standard errors: $\sqrt{p(1-p)/n}$ for a share; for a
  quantile or a median, [[LM18]]'s batch SE (20 equal batches, standard deviation with divisor 20, over $\sqrt{20}$).
  Simulated quantiles print the digits their batch SE supports.
- **Scripts:** `data/lm25_numbers.py` (computes and asserts every printed value against these anchors, recounts with
  `Fraction`, flags rounding boundaries) and `data/lm25_charts.py` (X1–X7, the widget block), after
  `data/vol4_series.py` in `DATA_STEPS`. Lab files: below.

**Hygiene declaration.** *In-sample:* every test and fit on TX23 and TR23 (the unit-root, KPSS, Engle–Granger,
Ljung–Box and variance-ratio tests; the AR(1), ARMA(1,1) and error-correction fits). *Descriptive:* X1, X6 and X7,
and the roll jumps. The residual of (6.25) uses dividends that went ex up to each contract's expiry, a look-ahead
that suits a decomposition after the fact (as LM6), never a trading rule. *Stability check:* the limit regimes
(E10, Problem 8). *Model:* the simulated DF null, the spurious regressions, the widget. Tests counted (LM21's rule):
35 on TR23 log returns (30 lags, Ljung–Box, four variance ratios) [A25-25], two on $\lvert r\rvert$ (Ljung–Box and the
lag-1 robust t-stat), and 24 on TX23 [A25-67]; every unit-root verdict lies far from its critical value, so the count
changes no conclusion. Local note: "Every basis figure describes TX23, the TX near-month settlement and the TAIEX
price close on 5,850 dates, 2 January 2003 to 8 October 2026, except where a caption names D (to 14 September 2026,
when realized dividends are used). Autocorrelation tests use TR23's log returns. The fits are in-sample, the regimes a
stability check, the simulations a model. Nothing is tested on later data ([[LM34]])."

**Notation.** AUTHORING §6 with the Volume IV table. Used: $S_t$, $F_t$, $\tau$, $q$ (dividend yield, LM6's; no
bet here), $r_f$, $r$, $R$, $T$ (observations; a simulated walk is described by its number of levels), $t$, $A$, $m$
(the variance ratio's horizon only), $k$ (a lag), $s$, $s_\varepsilon$, $\bar r$, $\rho_k$, $\hat\rho_k$, $\gamma_k$,
$\hat\gamma_k$, $\operatorname{VR}(m)$, $\phi_1$, $\theta_1$, $c$ (AR intercept, as §6's $c$ row allows), $\delta=
\phi_1-1$, $\eta_t$ (white noise), $\varepsilon_t$, $\hat\varepsilon_t$ (regression error and residual), $\beta$,
$\hat\beta$ (cointegrating coefficient), $X$, $d$ (LM23's design and count), $\ell$ (the log-likelihood, written only
in $-\ell''$; LM25 has no block length or HAC lag), $\text{t-stat}$ ("the DF t-stat"), $\operatorname{SE}$, $H_0$,
$H_1$, $\Phi$, $\E$, $\Var$, $\Cov$, $\operatorname{Corr}$, $\mathcal N$, $\chi^2_K$, $n$ (simulated draws), $B_t$
(named in a Deep Dive). Generic series are $x_t$, $y_t$ (no yields here). LM6's $\varepsilon$ of (6.25) is cited by
its tag only ("the residual of (6.25)"). Local symbols, declared (accepted by the editor, X21):

| Symbol | Meaning | Check |
|:--|:--|:--|
| $b_t$ | the log basis $\ln F_t-\ln S_t$, in bp | $b$ is a bet's gain book-wide; LM25 has no bets. LM6 wrote the basis as $F-S$ in points with residual $\varepsilon$; the note says $b_t$ is the log basis |
| $u_t$, $\sigma_u$ | one-day white noise added to a persistent AR(1) (§7); its standard deviation | $u$ is a probability level in Volume III; unused in LM25 |
| $\zeta_t$, $\sigma_\zeta$ | the persistent part's innovation (§7 only) | LM5's $\zeta$ (a constant) does not occur, as for $\eta$ |
| $\sigma_\eta^2$ | variance of the white noise $\eta_t$ | subscripted $\sigma$ |
| $a_j$, $J$ | ADF coefficients of the lagged changes; their number | $a$ is a bet's loss book-wide; LM25 has no bets |
| $\alpha_F$, $\alpha_S$ | error-correction (adjustment) coefficients | LM25 has no significance level $\alpha$; levels are written "the 5% level" |
| $Q_{\text{LB}}(K)$, $K$ | the Ljung–Box statistic over lags $1,\dots,K$ | $Q$ alone is the eigenvector matrix (none here); subscripted |
| $\operatorname{SE}_{\text{iid}}$, $\operatorname{SE}_{\text{rob}}$ | standard errors under iid data and under heteroskedasticity (of $\hat\rho_k$ and of $\operatorname{VR}(m)$) | subscripted SE |
| $\tilde r_t$ | $r_t-\bar r$, the centred log return ((25.4) and its Deep Dive) | a tilde marks centring, as §6 says |

Not used: $\theta$ unsubscripted, $\alpha$ as a level, $\mathcal L$ written, $L$ (no lag operator), $\tau$ for a DF
statistic, $z$ or a star for the VR statistic (written $\text{t-stat}$ with its standard error named), $P$, $p$ for
an order (AR(1), MA(1), ARMA(1,1) only; $q$ stays the dividend yield). Counts: $T$ (observations), $n$ (simulated
walks or pairs, and a walk's levels in the Data role), $K$ (Ljung–Box lags), $J$ (ADF lags), $m$, $k$, $j$.

**Motivating case: "A basis that comes back."** (box, about 140 words)

> From 2 January 2003 to 8 October 2026 the TAIEX price index rose from 4,524.87 to 49,313.44, 10.9 times its start
> [A25-06], and its log never settled around a level. The near-month TX future followed it day by day. Their log
> basis, $b_t=\ln F_t-\ln S_t$, averaged −25.4 bp with a standard deviation of 58.2 bp [A25-07]. It reached −793 bp
> on 27 October 2008, when TX fell by its 7% limit, and +248 bp on 5 May 2009 [A25-08]; the future settled below the
> index on 4,051 of 5,850 days [A25-09]. A day's change in the basis had a standard deviation of 38.9 bp [A25-10], yet
> the basis did not wander off: next-day values correlate 0.776, and a gap halves in about 2.7 sessions [A25-11].
> [[LM6]] split one season's basis into carry, dividends and a residual. Is the basis stationary while the index is
> not, how fast does it return, and how much of a day's move is noise?

Resolved: (a) stationary or not: §5, E6 (ADF on $\ln S$: −0.77, p = 0.97 [A25-12]; on $b_t$: −9.00 with 28 lags,
DF −27.20 [A25-13]); §6 (the known vector); (b) how fast: §4, E4 (2.7 sessions) and §7, E10 (7.0 sessions for the
persistent part, SE 0.56 [A25-68]); (c) noise: §7, E10 (64% of a day's change [A25-55], about 56 index points in 2025
[A25-59]) and the widget.

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | why a level and a spread behave differently; case + X1; roadmap; notation and hygiene notes | 380 |
| 2 | Stationarity, White Noise and the Random Walk {1} | a time series; mean, variance, autocovariance $\gamma_k$ and $\rho_k=\gamma_k/\gamma_0$ of a process; weak stationarity (three conditions); white noise (uncorrelated, mean 0, constant variance) against iid noise ((16.1); clustered returns can be white noise but not iid); the random walk $x_t=x_{t-1}+\eta_t$, $\Var(x_t-x_0)=t\sigma_\eta^2$ by (16.3), not stationary; with drift; LM3's $\ln S$; E1; pitfall: a long sample mean of a level describes the path, not a mean to return to | 520 |
| 3 | Testing for Autocorrelation {2} | LM19's $\hat\rho_k$ and iid band; why clustering widens it; (25.4) $\operatorname{SE}_{\text{rob}}(\hat\rho_k)$, HC0-type, with conditions (Deep Dive); X2, E2; Ljung–Box (25.5) with conditions, upper tail; the variance-ratio test (25.6) of LM19's $\operatorname{VR}(m)$, two-sided, iid and robust variances, a large-sample approximation whose robust form assumes zero cross-lag terms (checked in E3; the attribution to Lo and MacKinlay waits for their text); E3; pitfall: an iid band on clustered data | 670 |
| 4 | Autoregressive and Moving-Average Models {3} | AR(1) (25.1): stationarity $\lvert\phi_1\rvert<1$, mean, variance, $\rho_k=\phi_1^k$ (derived); half-life (25.2); MA(1) (25.3): $\rho_1=\theta_1/(1+\theta_1^2)$, zero beyond; partial autocorrelation as the last OLS coefficient; ACF and PACF signatures; ARMA(1,1) named; AR estimation by OLS ((12.1), [[LM23]]); E4; X3; pitfall: a half-life read from a noisy series is too short | 600 |
| 5 | Unit Roots and the Dickey–Fuller Test {4} | $\Delta x_t=c+\delta x_{t-1}+\eta_t$ (25.7), $H_0:\delta=0$ against $\delta<0$, one-sided; why the t-stat shifts left (Deep Dive, stated); E5, X4; ADF lags (25.8) and statsmodels' AIC choice; MacKinnon p-values; trend for a drifting series; E6; KPSS in one paragraph (reverse null, one-sided, table p-values); pitfall: reading the DF t-stat against $-1.645$ [A25-37] | 620 |
| 6 | Spurious Regression and Cointegration {5} | two independent random walks, E7, X5; why (residuals not stationary); differencing fixes the test but loses the level; cointegration defined; the basis as a known vector $(1,-1)$, so a unit-root test on $b_t$ is a cointegration test (Brenner and Kroner 1995 on the carry); Engle–Granger for an estimated vector, E8; the error-correction model in two sentences; Johansen and threshold cointegration in one sentence each; pitfall: testing $\hat\beta=1$ with the classical standard error | 540 |
| 7 | The TX Basis as a Time Series {6} | convergence at expiry (X7: carry and dividends shrink with $\tau$); roll jumps (−37.5 bp on average, −144.7 in June [A25-49]); the dividend season as a seasonal mean (X6, (6.25) in logs); E9, X8: four versions tested; the signal-plus-noise reading (25.9), E10 with the fit at the likelihood maximum and $-\ell''$ standard errors, the sandwich caveat in one sentence with a pointer to [[LM26]], widget; the 15-minute gap of lm06.md:672 named, with one sentence pointing to [[LM26]], which uses TX's 2025 one-minute bars (X9 is dropped); stability by limit regime; KPSS's verdict read; pitfall: annualizing or ranking a one-day basis (lm06.md:676) | 680 |
| 8 | Time Series in Python {7} | `acf`, `pacf(method="ols")`, `acorr_ljungbox` (DataFrame → `.to_numpy()`), `adfuller` and `kpss` with `result_object=True`, `coint(return_results=True)`, `ARIMA` (`method="innovations_mle"`, a restart, `cov_type="approx"`); matching `adfuller(maxlag=0, autolag=None)` to the hand regression; rolled against roll-free changes; lab box | 230 |
| — | Summary (7) / Problems (12) / Solutions | | 140 / 400 / 520 |
| | **Total** | | **5,300** |

**Elements.** 10 examples (E1 §2; E2, E3 §3; E4 §4; E5, E6 §5; E7, E8 §6; E9, E10 §7). Knowledge checks:

- §2: a random walk with daily standard deviation 1.2%: 6.0% after 25 sessions, 12.0% after 100; an AR(1) with
  $\phi_1=0.9$ and the same innovations stays within a stationary standard deviation of 2.753% [A25-16].
- §3: $\lvert r\rvert$'s lag-1 autocorrelation 0.161 ([[LM19]]'s, [A19-39]) has a robust standard error of 0.0240 and
  a robust t-stat of 6.7 [A25-22]: outside both bands; clustering is dependence of sizes, which [[LM26]] models.
- §4: an MA(1) with $\theta_1=-0.36$ has $\rho_1=-0.319$ and $\rho_2=0$; an AR(1) with $\phi_1=0.5$ has a half-life of
  1 session [A25-27].
- §5: why does adding 28 lagged changes move the basis's statistic from −27.20 to −9.00 while the verdict stays? The
  lagged changes absorb the part of the reversion that the PACF shows at lags 2 and 3 (0.230, 0.109 [A25-30]); both
  lie far below MacKinnon's 1% point, −3.43 [A25-37].
- §6: regressing the differences of X5's pair gives a t-stat of −0.98 [A25-44]: differencing removes the spurious
  fit, but on $\ln F$ and $\ln S$ it would also remove the long-run link that the error-correction term keeps.
- §7: rolls are grouped by the calendar month of the roll date. The June roll, from the June into the July contract,
  lowers the near-month basis by 144.7 bp on average, the July roll by 104.95 bp, rolls in other months by 19.8 bp
  [A25-49]: the new contract's life spans the ex-dividend season.
- §8: `adfuller(b)` reports −9.00 with 28 lags [A25-41]; `maxlag=0, autolag=None` reproduces the hand regression's
  −27.20, and `result_object=True` avoids the FutureWarning (SOURCES).

中文導讀 (each 3–6 sentences, the intuition, not a translation; 樂詞網 terms from plans/vol-4.md and SOURCES
"Chinese terms (Volume IV)" with the English at first use in each box; a term without a 樂詞網 statistics entry prints
the book's form with its English):

- §2: 時間序列 (time series), 平穩 (stationary), 白噪音 (white noise), 隨機漫步 (random walk), 獨立同分布; why a
  price level has no mean to return to and its changes may.
- §3: 自我相關 (autocorrelation), 自我相關函數 (ACF), 變異數比 (variance ratio), 虛無假設 (null hypothesis), 穩健標準誤
  (robust standard error), 波動群聚現象 (volatility clustering); Ljung–Box 檢定 keeps its English name (no 樂詞網
  entry); why clustering widens the band.
- §4: 自我迴歸模型 (AR), 移動平均模型 (MA), 自我迴歸移動平均模型 (ARMA), 偏自我相關函數 (PACF); 半衰期 (half-life),
  the book's form (樂詞網 lists it only outside statistics; SOURCES).
- §5: 單根 (unit root), 單根檢定 (unit root test), 增廣 Dickey-Fuller 檢定 (augmented Dickey–Fuller test), 對立假設
  (alternative hypothesis); why −1.645 is the wrong yardstick.
- §6: 共整合 (cointegration), 誤差修正模型 (error correction model), 迴歸 (regression); 虛假迴歸 (spurious regression),
  樂詞網's statistics form (SOURCES).
- §7: 基差 (basis; LM6's box), 白噪音, 平穩; the basis's three deterministic parts and the noise, tied to LM6's box.

Deep Dives: §3 "Where the robust band comes from": under $H_0$ the centred returns $\tilde r_t$ are a martingale
difference sequence (each has conditional mean 0 given the past) with finite fourth moments, so the products
$\tilde r_t\tilde r_{t-k}$ are uncorrelated across $t$ and (16.3) gives
$\Var\big(\sum_t\tilde r_t\tilde r_{t-k}\big)=\sum_t\E[\tilde r_t^2\tilde r_{t-k}^2]$; dividing by $(\sum_t\tilde
r_t^2)^2$ and replacing expectations by sample values (a large-$T$ approximation) gives (25.4), (23.6)'s White form
for a regression of $\tilde r_t$ on $\tilde r_{t-k}$ under the null (HC0-type); under iid data it reduces to $1/T$. For two lags $j\ne k$ the same argument leaves the cross terms
$\sum_t\E[\tilde r_t^2\tilde r_{t-j}\tilde r_{t-k}]$, which (25.6)'s robust form sets to zero. §5 "Why the DF t-stat
shifts left": under $\delta=0$ the sum $\sum x_{t-1}^2$ grows like $T^2$, not $T$, so $\hat\delta$ settles at rate $T$
and the t-stat converges to a ratio of functionals of Brownian motion ([[LM36]]), not to $\mathcal N(0,1)$; the
constant makes it negative on average (mean −1.54 in experiment 1 [A25-35]). Stated without proof (Hamilton 1994,
ch. 17; MacKinnon 1996 for the tables).

**Exhibits.**

- X1 `case` (two stacked `line` charts in one exhibit, §1, same date range): (a) $S_t$, `y.type: "log"`, `fmt: "n2"`,
  `tfmt: "n0"`; (b) $b_t$ in bp, `fmt: "n1"`; dashed `hline` at the mean −25.4; `point`s at 2008-10-27 (−792.9) and
  2009-05-05 (+247.8). Thinned by the editor's rule (no daily FinMind series at full resolution, X37): the last session
  of each of 1,224 ISO weeks plus the first date and the two extremes, 1,227 dates [A25-70], `x.values` shared, about
  33 KB. Note: TX23, near-month settlement rolled at the close of the day before each last trading day; TAIEX price
  index (no dividends); weekly points (each week's last session) and the two cited extremes. Source: FinMind
  `TaiwanFuturesDaily` (TX, regular session), retrieved 19 October 2026, and `TaiwanStockPrice` (TAIEX), retrieved 11
  and 18 October 2026; Computations: `data/lm25_numbers.py`.
- X2 `robust` (`scatter` with `bands`, §3): x lag $k=1,\dots,30$ (`ticks` 1, 5, 10, 15, 20, 25, 30); y −0.06 to 0.06
  (`fmt: "n4"`, `tfmt: "n2"`). Series "sample autocorrelation of r" (LM19's values, recomputed); bands "robust band"
  $\pm1.96\operatorname{SE}_{\text{rob}}(\hat\rho_k)$ (per lag, 0.0151 to 0.0227 [A25-20]) and "iid band"
  $\pm0.0256$ ($\operatorname{SE}_{\text{iid}}=0.0131$ [A25-18]). Values cited: $\hat\rho_1=0.0393$ [A25-17]; 9 of 30
  lags outside the iid band (1, 4, 6, 8, 13, 14, 18, 20, 26), 2 outside the robust band (8, 14), 1.5 expected [A25-19];
  lag 29 sits just inside the iid band, so the count of 9 rests on a margin of $2\times10^{-5}$ (the text says "9").
  Note: TR23 log returns, $T=5{,}849$; in-sample; 35 tests on these returns.
- X3 `acf` (`line`, §4): x lag 1–20 (`fmt: "n0"`); y −0.1 to 1 (`n3`). Four series: sample ACF of $b_t$ (0.776,
  0.693, 0.633, …, 0.441 at lag 10, 0.360 at 20 [A25-29]); sample PACF, OLS (0.776, 0.230, 0.109, 0.021, 0.072, then
  below 0.07 [A25-30]); AR(1) model $0.7758^k$ (0.602 at 2, 0.281 at 5, 0.079 at 10); ARMA(1,1) model (0.7745, 0.702,
  0.522, 0.319, 0.119 at 1, 2, 5, 10, 20 [A25-32]). Note: TX23; ACF with divisor $T$; PACF the last coefficient of an
  OLS AR($k$) fit; the AR(1) from E4, the ARMA(1,1) from E10. The sample ACF decays more slowly than either model
  beyond lag 5: the mean moves (§7).
- X4 `dfnull` (`line`, §5): x −5.5 to 2.5; y density (`n3`). A `step` histogram (bins 0.1) of 10,000 simulated DF
  t-stats (experiment 1, `default_rng([1, 20261011])`, random walks of 5,850 levels, constant, no lags) and the
  standard normal density; dashed `vline`s at −2.86 (the simulated 5% point, batch SE 0.014, and MacKinnon's [A25-35],
  [A25-37]) and −1.645. Note: 46.7% of the null draws fall below −1.645 (SE 0.5%) [A25-36]; *Model*.
- X5 `spurious` (`line`, §6): x session 1–5,850 (`x.values`), two series $x_t$ and $y_t$, the first independent pair
  of experiment 2 (`default_rng([2, 20261011])`); ends 62.0 and 98.3 [A25-44]. Simulated, not market data, so the
  thinning rule does not apply; about 110 KB. Note: the regression of $y_t$ on $x_t$ has slope 0.61, t-stat 23.5 and
  R-squared 0.086; over 1,000 pairs $\lvert\text{t-stat}\rvert>1.96$ in 96.6% (SE 0.6%), median R-squared 0.18
  [A25-43]; *Model*.
- X6 `season` (`bar`, §7): 12 calendar months; three series in bp (`fmt: "n2"`, axis `n0`): mean $b_t$, mean fair log
  basis $r_f\tau-q_{\text{real}}\tau$, mean residual [A25-53]. Values cited: June −74.80 = −67.43 + (−7.37); July
  −70.17 = −65.88 + (−4.29). Note: D, 5,834 dates, 369–532 a month; $r_f=2\%$, $\tau$ = days/365; dividends counted on
  their ex-dates up to each contract's last trading day (a look-ahead, descriptive); means only, no standard errors,
  because neighbouring days correlate 0.776 and the means describe the sample. Over D the basis averaged −25.57 bp: carry
  +9.73, dividends −17.54, residual −17.76 [A25-52].
- X7 `expiry` (`line`, §7): x = −(sessions to the last trading day), −20 to −2 (`ticks` −20, −15, −10, −5, −2,
  `tickLabels` "20", "15", "10", "5", "2"); band "mean ± one standard deviation" of $b_t$; lines "mean log basis" and
  "mean fair log basis"; dashed `hline` 0. Values cited: at 20 sessions mean −37.95, SD 69.17, fair −14.78; at 2
  sessions −6.56, SD 35.13, fair −1.84 [A25-51] (235–285 dates per point). Note: D; the standard deviation falls
  only to about 35 bp: the noise floor of §7.
- X8 `versions` (table, §7, E9): rows $b_t$; $b_t-r_f\tau$; the residual $b_t-r_f\tau+q_{\text{real}}\tau$; $b_t$ minus
  its calendar-month mean. Columns: mean (bp), $s$ (bp), DF t-stat, ADF t-stat (lags), KPSS (p-value), AR(1)
  $\hat\phi_1$ (half-life), ARMA $\phi_1$, $\theta_1$ (half-life); $\hat\phi_1$ prints four decimals and $\phi_1$ five,
  so that each half-life follows from the printed coefficient by (25.2). Values [A25-54]: −25.6, 58.11, −27.2, −9.03
  (28), 0.62 (0.021), 0.7751 (2.72), 0.90584, −0.355 (7.01); −35.3, 59.11, −27.4, −9.15 (28), 0.62 (0.021), 0.7723
  (2.68), 0.89557, −0.327 (6.28); −17.8, 47.67, −32.3, −7.75 (33), 0.77 (≤0.010, the table's bound), 0.6974 (1.92),
  0.89075, −0.414 (5.99); 0.0, 53.24, −30.3, −8.51 (28), 0.96 (≤0.010), 0.7284 (2.19), 0.87168, −0.323 (5.05). Note: D; ARMA fits
  at the likelihood maximum; MacKinnon's 5% point about −2.86 (A25-37's value is for 5,849 observations); KPSS's 5%
  point 0.463 [A25-40].
- X9 is dropped (fresh check): TX's 2025 one-minute bars and their timestamp check are [[LM26]]'s (its X5), and §7
  says so in one sentence.

**Widget `ar1noise` — "A mean-reverting basis with one-day noise."** `Book.controls`: $\phi_1$ (0 to 1, step 0.01,
initial 0.91); noise $\sigma_u$ (0 to 40 bp, step 1, initial 22); a "new path" button (seed 1, 2, …). Fixed:
$\sigma_\zeta=22.8$ bp, mean −25.5 bp, 246 sessions [A25-60]. `line` chart: the persistent part ($x_t$, `quiet`) and
the observed $b_t=x_t+u_t$, dashed `hline` at the mean. Simulation with `Book.rng(seed).normal()`; the start is drawn
from the stationary law when $\phi_1<1$ and set at the mean at $\phi_1=1$. Readouts: the model half-life
$\ln\frac12/\ln\phi_1$ ("none: a random walk" at 1); $\hat\phi_1$ of an AR(1) fitted to the observed path by OLS and
its half-life; the path's DF t-stat against the 5% point −2.87 for 245 changes (MacKinnon, [A25-38]). Initial state
(PDF): $\phi_1=0.91$, half-life 7.35 sessions [A25-33]. No Student $t$, no `tInv`: normal draws only. The text quotes
only model values (7.35, −2.87). The widget holds no market series.

**Examples** (results recomputed from the printed inputs):

- E1 §2 (stability check, then a model): before 1 June 2015 TX23's mean $S$ was 7,302 and from then 16,042; the
  basis averaged −28.6 bp and −21.8 bp, with standard deviations 65.7 and 48.2 bp [A25-15]. A level's mean depends on
  the window; a spread's moves much less. Model: a random walk's standard deviation after $t$ sessions is
  $\sigma_\eta\sqrt t$ (16.3), so no fixed variance exists.
- E2 §3: TR23's $\hat\rho_1=0.0393$ ([[LM19]]'s value) [A25-17]; $\operatorname{SE}_{\text{iid}}=0.0131$ gives a
  t-stat of 3.01, $\operatorname{SE}_{\text{rob}}=0.0205$ gives 1.92 [A25-18]: below 1.96, so at the 5% level
  (two-sided) the lag-1 correlation is no evidence once clustering is allowed for. Of 30 lags, 9 leave the iid band
  and 2 the robust one (1.5 expected) [A25-19].
- E3 §3: $Q_{\text{LB}}(10)=37.1$, p-value $5.4\times10^{-5}$ from the upper tail of $\chi^2_{10}$ (5% point 18.31)
  [A25-21]. Variance-ratio tests (25.6) on LM19's $\operatorname{VR}(m)$, two-sided: $m=2$: 1.0392, t-stat 3.00
  (iid) and 1.91 (robust); $m=5$: 1.0465, 1.62 and 1.02; $m=10$: 1.0065, 0.15 and 0.09; $m=20$: 1.0359, 0.55 and 0.37
  [A25-23]. Only the iid test at $m=2$ rejects at the 5% level, as the lag-1 test did. The robust form sets the
  cross-lag terms to zero; keeping them widens its standard error by up to 25% and changes no verdict (t-stats 0.90,
  0.08, 0.30 at $m$ = 5, 10, 20 [A25-72]). One sentence: $\lvert r\rvert$'s $Q_{\text{LB}}(10)$ is 1,820 ([[LM26]]).
- E4 §4: AR(1) for $b_t$ by OLS on 5,849 rolled changes: $c=-5.66$ bp, $\hat\phi_1=0.7758$, classical SE 0.00824,
  $s_\varepsilon=36.7$ bp, half-life $\ln\frac12/\ln0.7758=2.73$ sessions, implied mean $c/(1-\hat\phi_1)=-25.25$ bp
  [A25-28]. The classical SE assumes white-noise errors, which the PACF's 0.230 at lag 2 denies, so the half-life gets
  no interval here (E10 gives one). Roll-free changes give 0.7748 and 2.72 [A25-48].
- E5 §5 (experiment 1, *Model*): 10,000 random walks of 5,850 levels; the DF t-stat's 1%, 5%, 10% points are −3.44,
  −2.86 (batch SE 0.014), −2.58, mean −1.54 [A25-35]; MacKinnon's for 5,849 observations −3.43, −2.86, −2.57
  [A25-37]. A true unit root falls below −1.645 in 46.7% of draws (SE 0.5%), below −1.96 in 30.7% [A25-36].
- E6 §5: $\ln S_t$: DF by hand ('c', no lags) 1.19, $\hat\phi_1=1.000392$, p-value 0.996 [A25-39]; ADF with trend
  ('ct', 32 lags by AIC) −0.77, p-value 0.97 [A25-12]; KPSS 10.356, p-value below 0.01 (the table's bound) [A25-40].
  $b_t$: DF −27.20, ADF ('c', 28 lags) −9.00, p-value below $10^{-14}$ [A25-13]; KPSS 0.664, p-value 0.017 (between
  the 2.5% and 1% points) [A25-40]. Both tests reject for the basis: it returns within days to a mean that moves
  across years (yearly means from −80 bp in 2008 to +34 bp in 2026 to date [A25-58]).
- E7 §6 (experiment 2, *Model*): X5's pair: slope 0.61, t-stat 23.5, R-squared 0.086; on differences −0.98 [A25-44];
  1,000 pairs: 96.6% (SE 0.6%) with $\lvert\text{t-stat}\rvert>1.96$, median $\lvert\text{t-stat}\rvert$ 36 (batch SE
  0.9), median R-squared 0.18 (batch SE 0.007) [A25-43]. One year of 246 sessions (experiment 4): 81.7% [A25-45].
- E8 §6: Engle–Granger: $\ln F_t=-0.0283+1.0028\ln S_t+\hat\varepsilon_t$; statsmodels' `coint` gives −9.42 against
  the 5% point −3.34 (one-sided), p-value below $10^{-14}$ [A25-46]. The residual's lag-1 autocorrelation is 0.764
  [A25-50], so the classical SE (0.000154) and the "t-stat" 18 for $\beta=1$ mean nothing; theory fixes the vector at
  $(1,-1)$ and $\hat\beta>1$ is consistent with the basis's mean drifting up with the index level (E6). Error
  correction (roll-free changes on $b_{t-1}$): $\alpha_F=-0.160$ (White HC0 SE 0.055), $\alpha_S=+0.0655$ (White HC0
  SE 0.040) [A25-47]: the futures does most of the correcting; $\alpha_F-\alpha_S=\hat\delta$ of the roll-free DF
  regression.
- E9 §7 (X8, sample D): every version rejects a unit root (DF −27.2 to −32.3, ADF −7.75 to −9.15) and every version
  fails KPSS at the 5% level; the AR(1) half-lives run from 1.92 to 2.72 sessions and the ARMA ones from 5.05 to 7.01
  [A25-54]. Removing carry, dividends or the month's mean changes the speed little: what is removed is slow.
- E10 §7: ARMA(1,1) on $b_t$ in bp at the likelihood maximum (statsmodels' default fit stops short of it; the fit
  starts from `innovations_mle` and a restart does not raise $\ell$): mean −25.5 (SE 3.2), $\phi_1=0.90620$ (SE 0.0071),
  $\theta_1=-0.355$ (SE 0.017), $\sigma_\eta^2=1{,}257.0$ bp², standard errors from $-\ell''$ (20.6) [A25-31]. Read as
  a persistent AR(1) plus one-day noise (25.9): $\sigma_u=22.2$ bp, $\sigma_\zeta=22.8$ bp, persistent standard
  deviation 53.8 bp; the noise is 64% of the variance of a day's change and 14.5% of the level's; the model's
  daily-change SD 39.11 bp against the sample's 38.91 [A25-55]. Half-life of the persistent part 7.04 sessions from
  the printed $\phi_1$ by (25.2), delta-method SE 0.556 by (20.8) from $\operatorname{SE}(\phi_1)=0.007055$ (six
  decimals, so that 0.556 follows), interval 5.95–8.13 [A25-31, A25-68]. These standard errors
  assume the model is right; the basis's volatility changes across years (E1), and the likelihood's sandwich, the
  analogue of [[LM23]]'s (23.6), *stated without proof*, gives $\operatorname{SE}(\phi_1)=0.0146$ and the interval
  4.78–9.30 [A25-71]; [[LM26]] meets the same sandwich as arch's robust standard errors of a GARCH fit. Stability
  check: before and from 1 June 2015, $\phi_1=0.90$ and 0.91, $\sigma_u=25.74$ and 17.45 bp [A25-56]. In 2025 alone
  $\sigma_u=23.4$ bp [A25-57], about 56 index points, and the 242 daily changes within 2025 had a standard deviation
  of 84.5 points [A25-59] (LM6's 83.4 used other months and roll rule, lm06.md:624).

**Problems plan** (12; MC keys A, B, C, B, A; the lab solves 6, 9, 10, 11, 12). Stems state the sample (TX23, 5,850
dates, 2 January 2003 – 8 October 2026, or TR23's 5,849 log returns), units (bp), the divisor ($T$; $T-d$ in a
regression), the test's null and side, the 5% level, the standard-error method (classical, robust, White HC0) and, for
a simulation, the experiment's seed and draws.

1. MC: an AR(1) with $\phi_1=0.8$; its autocorrelation at lag 3. **A** 0.512. B 0.8 (reads $\rho_1$, as if an AR(1)
   correlated only one lag back). C 0 (the partial autocorrelation at lag 3) [A25-61].
2. MC: half-life of an AR(1) with $\phi_1=0.9$, daily. A 5.0 sessions ($0.5/(1-\phi_1)$, a linear decay). **B** 6.58.
   C 10 sessions ($1/(1-\phi_1)$, the mean lag) [A25-61].
3. MC: MA(1) with $\theta_1=0.5$; $\rho_1$. A 0.5 ($\theta_1$ itself). B 0.25 ($\theta_1^2$). **C** 0.40 [A25-61].
4. MC: a DF regression with a constant on 5,849 changes gives −2.50. At the 5% level (one-sided): A reject, since
   −2.50 < −1.645 (the normal one-sided point). **B** do not reject: MacKinnon's 5% point is −2.86. C reject, since
   $\lvert\text{t-stat}\rvert>1.96$ (a two-sided normal test) [A25-62].
5. MC: on TX23 the basis's ADF rejects a unit root and KPSS rejects level stationarity (p-value 0.017). **A** the basis
   returns within days to a mean that itself moves across years. B the basis has a unit root, because KPSS rejects
   (KPSS's alternative is not a unit root alone: a moving mean also fails it). C the tests contradict each other, so
   neither informs (they test different nulls and both can be false).
6. TR23 log returns, $T=5{,}849$; $\hat\rho_1,\dots,\hat\rho_5$ = 0.0393, 0.0000, −0.0031, −0.0323, −0.0173 and robust
   SEs 0.0205, 0.0210, 0.0227, 0.0178, 0.0196 (4 dp): $Q_{\text{LB}}(5)=16.96$ against $\chi^2_5$'s 5% point 11.07,
   reject; the five robust t-stats are 1.92, 0.00, −0.14, −1.81, −0.88, none beyond 1.96 [A25-26] (16.98 from
   unrounded inputs). Why Ljung–Box rejects while no robust t-stat does: its $\chi^2$ law needs iid data, and
   clustering widens each $\hat\rho_k$'s spread; with five tests, say what the count implies.
7. Derive the AR(1)'s mean $c/(1-\phi_1)$, variance $\sigma_\eta^2/(1-\phi_1^2)$ and $\rho_k=\phi_1^k$ from weak
   stationarity, and the half-life (25.2).
8. Derive (25.9) from $b_t=x_t+u_t$; apply it to the regimes' ARMA estimates printed to four decimals (0.9035,
   −0.3606, 1,659.9 bp²; 0.9101, −0.3427, 808.6 bp²): $\sigma_u$ 25.74 and 17.45 bp, persistent SD 60.50 and 44.95 bp,
   noise share of a day's change 65.2% and 62.6% [A25-63]. Stability check: what changed between the regimes.
9. Python: the DF regression by hand on $b_t$ (rolled), −27.20, equal to `adfuller(b, maxlag=0, autolag=None)`; the
   roll-free version −29.66; half-lives 2.73 and 2.72 [A25-64].
10. Python, experiment 3 (`default_rng([3, 20261011])`, 100,000 walks of 246 levels, chunks of 500): the 5% point of
    the DF t-stat −2.87 (batch SE 0.006) against MacKinnon's −2.87 for 245 observations; share below −1.645, 45.7%
    (SE 0.16%) [A25-38].
11. Python, experiment 4 (`default_rng([4, 20261011])`, 1,000 pairs of 246 sessions): share with
    $\lvert\text{t-stat}\rvert>1.96$ 81.7% (SE 1.2%), median R-squared 0.17 (batch SE 0.011) [A25-45].
12. Python: the variance-ratio test at $m=5$ on TR23 log returns, LM19's $\operatorname{VR}(5)$: 1.0465, t-stat 1.62
    (iid) and 1.02 (robust), two-sided [A25-66].

**Lab parts** (`build/make_lab25.py`; reads only its `data/`: `taiex_tr.csv` (TR23's raw closes, as Volume III's
labs), `taiex_price.csv` (TAIEX price closes, `date,close,spread`, from `raw/vol3/TAIEX__2003-01-01__2007-07-01.csv` and
`raw/sectors/TAIEX__*.csv`, cut to TR23's dates) and `tx_daily.csv` (a copy of `raw/vol4/TX__1998-07-21__2026-10-16.csv`)):
1 build TX23 with the roll rule (held contract = first contract whose last trading day is after the next session;
the third Wednesday for contracts open at the file's end), check 5,850 dates and 285 rolls, the `Fraction` count of
$F<S$; TR23's $r$; 2 X1 and the case (weekly points); 3 E1, a simulated random walk against an AR(1); 4 X2, E2, E3,
Problems 6 and 12; 5 X3, E4 by hand and by `statsmodels` OLS, the PACF by regression; 6 E5 and X4 (experiment 1), E6
(`adfuller`, `kpss`), Problems 9 and 10; 7 E7 and X5 (experiment 2), E8 (`coint`, the error-correction regressions
with White HC0 errors), Problem 11; 8 X6, X7, X8 (E9), E10 with `ARIMA` (`method="innovations_mle"`, the restart
check, `cov_type="approx"` against a hand Hessian). Extension (stability check): the AR(1) and ARMA(1,1) half-lives of
$b_t$ year by year. Labs write "LM26", never `[[LM26]]`.

**Cross-module tags** (probable users, as the cross-check confirmed):

- (25.1) AR(1) $x_t=c+\phi_1x_{t-1}+\eta_t$, white-noise $\eta_t$ with variance $\sigma_\eta^2$; stationary iff
  $\lvert\phi_1\rvert<1$, then $\E x_t=c/(1-\phi_1)$, $\Var x_t=\sigma_\eta^2/(1-\phi_1^2)$, $\rho_k=\phi_1^k$ (LM26:
  GARCH's squared returns as an ARMA; LM39: the discrete Ornstein–Uhlenbeck).
- (25.2) half-life $\ln\frac12/\ln\phi_1$, $0<\phi_1<1$ (LM26's GARCH half-life; LM39).
- (25.3) MA(1) $x_t=c+\eta_t+\theta_1\eta_{t-1}$: $\rho_1=\theta_1/(1+\theta_1^2)$, $\rho_k=0$ for $k\ge2$ (LM26: the
  MA(1) autocorrelation of high-frequency returns under its noise model, a hypothesis there).
- (25.4) $\operatorname{SE}_{\text{rob}}(\hat\rho_k)=\sqrt{\sum_{t>k}\tilde r_t^2\tilde r_{t-k}^2}\big/\sum_t\tilde r_t^2$,
  HC0-type; martingale-difference null, finite fourth moments, large $T$ (LM33).
- (25.5) $Q_{\text{LB}}(K)=T(T+2)\sum_{k=1}^K\hat\rho_k^2/(T-k)\approx\chi^2_K$ under iid data, large $T$ (*stated
  without proof*, Ljung and Box 1978); upper tail (LM26).
- (25.6) the variance-ratio t-stat $(\operatorname{VR}(m)-1)/\operatorname{SE}$, $\operatorname{VR}(m)$ LM19's (19.8),
  with $\operatorname{SE}_{\text{iid}}^2=2(2m-1)(m-1)/(3mT)$ or $\operatorname{SE}_{\text{rob}}^2=\sum_{k<m}[2(1-k/m)]^2
  \operatorname{SE}_{\text{rob}}(\hat\rho_k)^2$; two-sided, normal reference, large $T$; the robust form assumes
  $\E[\tilde r_t^2\tilde r_{t-j}\tilde r_{t-k}]=0$ for $j\ne k$ (LM33).
- (25.7) the DF regression $\Delta x_t=c+\delta x_{t-1}+\eta_t$ and its t-stat, $H_0:\delta=0$ against $\delta<0$
  (one-sided), MacKinnon's critical values (LM39 if it tests a spread).
- (25.8) ADF: (25.7) plus $\sum_{j=1}^Ja_j\Delta x_{t-j}$.
- (25.9) $b_t=x_t+u_t$ with $x_t$ an AR(1) and $u_t$ independent white noise has ARMA(1,1) autocorrelations with
  $\sigma_u^2=-\theta_1\sigma_\eta^2/\phi_1$ (LM26: the noise model of realized variance, a hypothesis there).

**Pitfalls to pre-empt.**

- Conditions every time: stationarity of an AR(1) needs $\lvert\phi_1\rvert<1$; Ljung–Box's $\chi^2$ needs iid data;
  the robust band a martingale-difference null and finite fourth moments; the robust VR test also zero cross-lag
  terms; the DF tables a constant (or a trend) as specified and white-noise errors (ADF lags otherwise).
- White noise is not iid: TR23's returns are close to uncorrelated but their sizes are not (0.161, [[LM19]]'s).
- Rolled against roll-free differences; a roll day links two contracts (E4, Problem 9); the June roll moves the basis
  by about 145 bp.
- A half-life from a noisy series is short: 2.7 sessions for the AR(1) against 7.0 for the persistent part.
- statsmodels' default ARMA fit can stop short of the maximum: restart and check $\ell$. Its `cov_type="oim"` is
  Harvey's information formula, not $-\ell''$; `"approx"` is the numerical $-\ell''$ (SOURCES addition). $-\ell''$
  standard errors assume the model is right.
- KPSS's p-values come from a four-point table and stop at 0.01 and 0.10 (SOURCES addition); write "below 0.01".
- Spurious regression: never read a t-stat or R-squared from levels of two random walks; Engle–Granger's classical
  standard error is not a test of $\beta=1$.
- The residual of (6.25) uses realized dividends: a look-ahead, descriptive only; $r_f=2\%$ is LM6's proxy for 23
  years of changing rates, so the residual absorbs rate changes; KPSS's rejection may partly reflect them (not
  measured: FinMind has no Taiwan rate series, SOURCES).
- The 13:30 close against the 13:45 settlement: a one-day basis is mostly noise; never annualize it (lm06.md:676).
- Data traps: $b_t$ on 5,850 dates against D's 5,834; bp of log basis, not index points; $A=246.12$, never 252;
  TX23's $S$ is the price index, TR23's $R$ the total-return index; a regime's or a year's changes stay within it.
- Ownership: $\hat\rho_k$ of TR23, the iid band and $\operatorname{VR}(m)$ are [[LM19]]'s; the robust band,
  Ljung–Box, the VR test and every basis statistic are LM25's; GARCH is [[LM26]]'s.
- Notation: $q$ is the dividend yield, so no ARMA($p$,$q$) orders appear; $\phi_1$, never $\varphi$; $\delta$ is the
  DF coefficient (LM6's dividend fraction $\delta$ of lm06.md:564 is not used); $m$ is only the VR horizon.
- References (SOURCES; chapters, not theorem numbers): Hamilton (1994, ch. 3, 17, 19); Tsay (2010, §2.1–2.7, §8.5–8.6);
  Dickey and Fuller (1979); Said and Dickey (1984); MacKinnon (1994, 1996, 2010); Kwiatkowski et al. (1992); Ljung and
  Box (1978); Engle and Granger (1987); Johansen (1988, 1991); Brenner and Kroner (1995); Dwyer, Locke and Yu (1996);
  Lin, Chen and Hwang (2003); Roope and Zurbruegg (2002); Granger and Newbold (1974, bibliographic only) as the origin
  of spurious regression, with Greene (2018, ch. 21) at chapter level; Hull (2022) and MacKinlay and Ramaswamy (1988)
  as in LM6. Lo and MacKinlay (1988) only after their text is read (X9).

**Stage 4 for earlier modules.** As the plan's Stage 4 list: `leads` gain 25 in lm03.md:6, lm12.md:6, lm16.md:6,
lm17.md:6 and lm18.md:6 (lm06.md:6 already lists 25). No wording changes.

**Open before Stage 2** (a decision applied as written while its source is unread):

- The variance-ratio test is not attributed to Lo and MacKinlay (1988) until their text and robust statistic are
  read (X9).
- The ARMA MLE's large-sample law and the likelihood sandwich are *stated without proof*; the Hamilton chapter that
  treats ARMA likelihoods is not in SOURCES' chapter list, and no source for the sandwich is recorded yet.
- A Chinese form for "mean reversion": 樂詞網 has no statistics entry, and SOURCES leaves the form to the editor;
  until then a box that needs it prints the English.

## LM26 Time Series II: Volatility Models

Stage 1 brief, drafted 2026-10-19 from the editor's spine (`plans/vol-4.md` at commit bcfa0d4, "### LM26 Time Series
II: Volatility Models") under the editor's decisions on the LM19–LM25 drafts, and revised the same day to the
editor's LM26 decisions and the fresh check. Each number carries its anchor ID at its first appearance;
`data/vol4_anchors_lm26.py` prints them all (rows in `plans/vol-4-anchors.md`: 66 rows, A26-01 to A26-66). Numbers quoted from published modules
carry their file:line instead, and numbers from the sibling briefs their anchor IDs (LM19, LM21, LM25 as revised on
2026-10-19). Tags of LM19–LM25 are cited as their Stage 1 briefs number them.

**Prereq:** `[3, 5, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 25]`. The spine's draft list plus LM14 ((14.6) and the
quantile function), LM18 (batch standard errors) and LM25 (the half-life and the noise model), which the text cites for
a result.

- LM3: $\mathrm{RV}=\sum_tR_t^2$ over a holding period, the realized variance (lm03.md:391), and its Glossary term
  實現變異數 (lm03.md:710).
- LM5: the normal model's tails and the forward link at lm05.md:529.
- LM13: the falls-after-falls counts (lm13.md:159).
- LM14: $\E[Z^4]=3$, (14.6) (lm14.md:226), used in Deep Dive 2; the quantile function $F_X^{-1}$ (lm14.md:85).
- LM15: the overdispersed monthly counts, 3.02 times their mean (lm15.md:163); the worst day, −9.6997% on 7 April 2025
  (lm15.md:450).
- LM16: (16.3) the variance of a sum; the sizes of next-day moves on U28 (lm16.md:168).
- LM17: TR23's excess kurtosis of $r$, 5.428 (lm17.md:387); the lag correlations of $\lvert r\rvert$ (lm17.md:392);
  five years $=\operatorname{round}(5A)=1{,}231$ sessions (lm17.md:537).
- LM18: the batch standard error of a median, 20 batches, divisor 20 (lm18.md:153); resampling destroys clustering,
  monthly variance 0.598 against 1.846 (lm18.md:379).
- LM19: (19.3) sample skewness and kurtosis; (19.5) $\hat\rho_k$; (19.6) the iid band; (19.7) the variance of an
  $m$-period sum and its ratio $1+2\sum_{k<m}(1-k/m)\rho_k$; TR23's $\hat\rho_k$ of $r^2$ and $\lvert r\rvert$
  [A19-39, A19-40]; $\sqrt A\,s_r=18.99\%$ [A19-54].
- LM20: (20.5) the normal likelihood; (20.6) standard errors from $-\ell''$; (20.8) the delta method.
- LM21: (21.2) p-values; the rule that every test reports how many tests ran on the same data; E7's falls after falls,
  13 of 108 against 2.0 [A21-25].
- LM23: (23.1) OLS; (23.4) t-stats; (23.6) White's HC0 errors; (23.7) Newey–West with the book's lag rule.
- LM25: (25.1) AR(1); (25.2) the half-life; (25.3) MA(1); (25.5) Ljung–Box; (25.9) signal plus noise; $\lvert r\rvert$'s
  $Q_{\text{LB}}(10)=1{,}820$ [A25-22].

**Leads:** `[30, 31, 32, 34, 39]`: pointer targets in the text (LM30 and LM31 forecast covariances; LM31 targets a
volatility; LM32 turns a variance forecast into a value-at-risk; LM34 tests rules on later data, named in the hygiene
note; LM39 models stochastic volatility in continuous time) and the probable users of the tags below.

**Forward links honoured.** A grep of `src/lm*.md`, `src/pages/*.md` and `build/make_lab*.py` for "LM26" finds nine
lines: lm05.md:529, lm13.md:159, lm15.md:170, lm16.md:170, lm17.md:392, lm18.md:381, `make_lab05.py:529`,
`make_lab13.py:463` and `make_lab17.py:486`. The spine lists all of them except `make_lab17.py:486`, which the plan's
Stage 4 list already gives to LM19. No page in `src/pages/` names LM26.

| Earlier text | Promise | Kept in |
|:--|:--|:--|
| lm05.md:529 | 0050 needs $\sigma=1.859\%$ a day (29.0% a year) for nine −5% days; "Part of that shape comes from volatility that changes over time ([[LM26]])" | §5, E6 on TR23: a normal GARCH implies excess kurtosis 3.51 [A26-25] of the data's 5.428 (lm17.md:387); its standardized residuals keep 2.57 [A26-23]. LM5's 0050 numbers are cited, not recomputed |
| `make_lab05.py:529` | standardize by a trailing 60-day $\sigma$ or an EWMA; "if volatility clustering explained everything" the count at −4.107 would be near 0.058 | §7's rolling 60-day and EWMA forecasts; E6 answers on TR23: 17 days at or below −4.107 standardized by $s$, 9 after GARCH, 0.117 under the normal model [A26-63]; the lab points back |
| lm13.md:159; `make_lab13.py:463` | falls after a fall of 3% or more 12.04%, after a rise 4.48%, overall 1.85%; "[[LM26]] models them" | §5, E7: GARCH expects 7.8 falls after the 108 falls and 5.4 after the 67 rises [A26-29]; the asymmetry is named in words with Hansen and Lunde's (2005) "leverage effect" and left to the lab's extension |
| lm15.md:163, 170 | monthly counts of large moves overdispersed 3.02 times; "[[LM26]] models it" | §5, E7: experiment 1, median ratio 3.15 [A26-30] |
| lm16.md:168, 170 | sizes correlate 0.183; next-day size 1.28% after $\lvert R\rvert\ge2\%$ against 0.75% (U28); "[[LM26]] models how tomorrow's spread depends on today's move" | §4 (26.3) and KC §2; §5, E7 on TR23: 1.27% after such days against 0.80%, GARCH 1.35% and 0.79% [A26-64]. U28's numbers are cited, not recomputed |
| lm17.md:392 | $\lvert r\rvert$ correlates 0.161 at lag 1 and 0.123 at 20; "[[LM26]] models such changing volatility" | §4: persistence 0.98443, half-life 44.2 sessions [A26-20, A26-21]; §5: $Q_{\text{LB}}(10)$ of $\lvert\hat\xi_t\rvert$ 27.6 against $\lvert r\rvert$'s 1,820 [A26-24] |
| lm18.md:379, 381 | resamples give monthly variance 0.598 against 1.846; "volatility that depends on yesterday's is the subject of [[LM26]]" | §4 (26.3); §5, E7: GARCH paths restore the clustering that resampling destroys |
| reviews/lm17.md:36; `make_lab17.py:486` | "the autocorrelation convention stays LM26's" | superseded by the Stage 1 decision: LM19 owns $\hat\rho_k$ (plan, Stage 4) |
| lm03.md:391, 710 | $\mathrm{RV}=\sum_tR_t^2$, Glossary 實現變異數 | §6: $\mathrm{RV}_t(h)$ is the same idea on intraday log returns; the Chinese terms are LM3's 實現變異數 and 實現波動率 (the editor's decision) |
| syllabus.yaml:67 | "EWMA, GARCH, and realized volatility from 5-second TAIEX data." | §3, §4–§5, §6 |

**Outcomes** ("After this module you should be able to:"):

1. explain volatility clustering as dependence between the sizes of returns, and test for it with Engle's ARCH test
2. compute an EWMA variance by hand, with its weights, effective window and RiskMetrics' choice $\lambda=0.94$
3. state the GARCH(1,1) model with its conditions, and derive its unconditional variance, its multi-step forecasts and the half-life of a shock
4. fit GARCH(1,1) by maximum likelihood with normal and Student $t$ innovations, compute the log-likelihood by hand, and check the fit with standardized residuals
5. compute realized variance from intraday data, read a volatility signature plot, and state the hypotheses (microstructure noise, stale prices) that could explain how it moves with the sampling interval
6. evaluate variance forecasts out of sample with MSE and QLIKE against a noisy realized-variance target, and with Mincer–Zarnowitz regressions
7. run these tools in Python with arch and statsmodels on NumPy arrays, matching each package result to a calculation by hand

**Owns.** Volatility clustering as a model's target; the conditional variance $\sigma_t^2$ and the innovation
$\varepsilon_t=\sigma_t\xi_t$; Engle's ARCH test and its results on TR23; EWMA (definition, weights, effective window,
RiskMetrics' $\lambda$, the IGARCH reading); GARCH(1,1) (conditions, unconditional variance, persistence, half-life,
multi-step forecasts, the ARMA(1,1) reading of $\varepsilon_t^2$, the implied kurtosis); its Gaussian likelihood by
hand and arch's fits with normal and $t$ innovations, classic and robust standard errors; standardized-residual
checks; the two simulated experiments; every T5S statistic printed here (the signature by period and by year, the
pooled intraday autocorrelations, the closing auction, the opening return's share, the daily target $V_t$ and its gap to
$r_t^2$); the TX 2025 signature (option E); the out-of-sample comparison of six forecasts (losses, loss differences,
Mincer–Zarnowitz, robustness to the proxy, the window).

**Leaves.**

- TR23's $\hat\rho_k$ of $r$, $\lvert r\rvert$, $r^2$ and the iid band → LM19 (cited); the robust band and Ljung–Box on
  $\lvert r\rvert$ → LM25 (cited, 1,820).
- Value-at-risk from a volatility forecast → LM32. Volatility targeting → LM31. Covariance forecasting → LM30 and LM31,
  one sentence. Stochastic volatility in continuous time → LM39. Tests on later data → LM34.
- Named in one sentence each, not developed: the two-scale estimator of Zhang, Mykland and Aït-Sahalia (2005,
  §1.2.5); asymmetric GARCH (arch's `o=1` term), the lab's extension; jumps and realized kernels, not in the book.
  HAR regressions are not named until Corsi (2009) is in SOURCES (the editor's decision).
- No resampling: every printed standard error is analytic (classic, robust, HC0 or Newey–West), so LM22's block rule
  does not arise.

**Uses before taught** (one sentence each in the text):

- §4: "[[LM31]] scales a position by such a forecast, and [[LM32]] turns it into a value-at-risk."
- §4: "In continuous time a variance that moves at random is [[LM39]]'s stochastic volatility."
- §7: "Forecasting a whole covariance matrix is [[LM30]]'s and [[LM31]]'s subject."
- §7 (hygiene): "A rule judged on the days it was tuned on is in-sample; [[LM34]] tests rules on later data."

**Data role.**

- **TR23** (`data/processed/vol3_taiex.parquet`, `data/vol3_series.py`; FinMind `TaiwanStockTotalReturnIndex`, data_id
  TAIEX, retrieved 2026-10-18): $T=5{,}849$ log returns $r_t=\ln(1+R_t)$, 2003-01-03 → 2026-10-08 (lm17.md:46);
  $A=246.12$ (lm17.md:248) [A26-01, a check row]. Every daily model uses $r_t$ in percent (arch is given $100r_t$), so
  variances are in %² a day; annualized volatilities are $\sqrt{A}$ times a daily one.
- **T5S** (`data/derived/vol4_rv.csv`, built by `data/vol4_rv.py` from FinMind `TaiwanVariousIndicators5Seconds`,
  retrieved 2026-10-19, and the TAIEX closes of FinMind `TaiwanStockPrice`, which give `o2`'s previous close and check
  each day's 09:00:00 and 13:30:00 values; TWSE credited as the original source of both): 5,351 sessions, 2005-01-03 → 2026-10-08, sampled every 60 s (1,503
  days, to 2011-01-14), 15 s (764 days, 2011-01-17 → 2014-02-21), 10 s (214 days, to 2014-12-27) and 5 s (2,870 days,
  from 2014-12-29) [A26-02]; its dates are TR23's from 2005-01-03 [A26-03]. On the window 09:30:00–13:30:00 a day has
  2,880 five-second returns down to 16 fifteen-minute and 8 thirty-minute ones [A26-04]. The opening return
  $r_{\mathrm o,t}$ runs from the previous close to 09:30:00 (the file's `o2` is its square; PITFALLS §3). The daily
  target is $V_t:=r_{\mathrm o,t}^2+\mathrm{RV}_t(15\text{ min})$ in %², the price index's close-to-close day in 17
  squared pieces. TR23's squared log returns and the price index's differ by less than 0.01% in total on these days
  [A26-05], so dividends do not separate the two days at the digits printed.
- **Raw T5S** (`data/raw/intraday/taiex5s/`, not committed): only for statistics that the derived file cannot give
  (the pooled intraday $\hat\rho_1$ of E8, E9, KC §6 and X5's note, the daily autocorrelations of 2025, the closing
  auction). The derived file keeps its approved columns (the editor's decision): X6 plots ratios of adjacent intervals'
  realized variances from the file instead. Each number computed from the raw download says so where it is printed
  ("from the raw download"); `data/lm26_numbers.py` computes them, and the lab's optional part recomputes the 2025 ones
  from the 243 files of 2025. Nothing published carries an intraday value.
- **TX 1-minute bars, 2025** (option E; `data/raw/intraday/tx1m/2025/`, FinMind `TaiwanFuturesKBar`, Sponsor): the
  near-month contract held during day $t$ is TX23's contract on the previous date (`data/processed/vol4_tx23.parquet`).
  A bar's label is the minute it starts: the regular session's first label is 08:45:00 on every day, the last 13:44:00
  on 211 days, 13:45:00 on 30, and 13:40:00 and 13:42:00 on the two limit-locked days, 7 and 10 April 2025 (243 in
  all); the last bar's close equals `TaiwanFuturesDaily`'s close on
  243 of 243 days [A26-39]. So the price at 09:30:00 is the close of the 09:29 bar, and a minute without a bar keeps
  the previous close (only on those two limit-locked days). Text exhibit only; no lab reads it.
- **Out of sample:** the estimation window is $\operatorname{round}(5A)=1{,}231$ returns (lm17.md:537); both GARCH models are
  refitted at the first session of each month on the previous 1,231 returns (226 refits), and forecasts run from
  2008-01-02 to 2026-10-08, 4,609 days [A26-45].
- **Divisors and conventions:** sample moments divide by $T$ (LM19's (19.3)); $\hat\rho_k$ as (19.5), intraday ones
  pooled over a period's days with within-day pairs only; quantiles and medians use [[LM14]]'s quantile function
  (`method="inverted_cdf"`), written in words; counts against a threshold use the guard ($R\le-0.03+10^{-12}$).
- **Tests:** two-sided with a normal reference unless named; the ARCH test and Ljung–Box use the upper tail of
  $\chi^2_K$. Standard errors: classic ($-\ell''$) and robust (sandwich) for the GARCH fits, citing [[LM20]]'s (20.6)
  for the theory and arch's documented `cov_type` options; HC0 for Mincer–Zarnowitz; Newey–West (Bartlett, no
  small-sample correction) for loss differences, with [[LM23]]'s lag rule $\lfloor4(\text{days}/100)^{2/9}\rfloor$:
  9 lags for the 4,609 out-of-sample days.
- **Seeds:** `rng = np.random.default_rng([e, 20261011])`, created once per experiment: 1 the full-sample normal GARCH,
  2 the full-sample $t$ GARCH; 1,000 paths of 5,849 days each, $\sigma_t^2$ started at the unconditional variance, one
  draw per path each day ($t$ draws `rng.standard_t(nu) * sqrt((nu - 2)/nu)`). Medians carry LM18's batch standard
  error (20 batches of 50 paths).
- **Scripts:** `data/lm26_numbers.py` (computes and asserts every printed value against these anchors, flags rounding
  boundaries) and `data/lm26_charts.py` (X2, X4–X6, X8, X9, the widget block), after `data/vol3_series.py`,
  `data/vol4_series.py` and `data/vol4_rv.py` in `DATA_STEPS`. Lab files: below.

**Hygiene declaration.** *In-sample:* the ARCH tests, the full-sample GARCH fits and their residual checks (§2, §5),
X2's GARCH line, E7's expected counts. *Out-of-sample:* §7's forecasts, each made from data up to the day before, with
the 60-day window and $\lambda=0.94$ fixed in advance; the $\lambda$ that would have done best (E3) is chosen on the test
days and is in-sample. *Descriptive:* the signature plots, the intraday autocorrelations, the closing auction, the
opening return's share, X5. *Model:* experiments 1 and 2, the widget, the noise model of §6. *Stability check:* the
windows of 1,000 and 2,461 returns [A26-53] and the years of X8. Tests counted (LM21's rule): three ARCH tests, two
Ljung–Box tests, ten loss differences, six Mincer–Zarnowitz slopes and one test of $V_t$ against $r_t^2$, 22 in all;
the forecast ranking does not hang on any single one. Local note: "Every daily figure describes TR23, 3 January 2003 to
8 October 2026, and every intraday figure the TAIEX price index every 5 to 60 seconds, 3 January 2005 to 8 October
2026. Full-sample fits are in-sample; forecasts are made out of sample from 2 January 2008; simulations are models.
Nothing is tested on later data ([[LM34]])."

**Notation.** AUTHORING §6 with the Volume IV table. Used: $R$, $r$ (in percent in the models), $T$ (5,849, a count),
$t$, $A$, $g$ (the model's mean daily log return, §6's $g=\E[\ln(1+R)]$), $\sigma_t^2$, $\sigma_{t+1\mid t}^2$,
$\sigma_{t+m\mid t}^2$, $\sigma^2$ (the unconditional variance $\omega/(1-\alpha-\beta)$, §6's $\sigma$ of a model),
$\varepsilon_t$, $\hat\varepsilon_t$, $\xi_t$, $\hat\xi_t$, $\eta_t$ (Deep Dive 1 only, LM25's), $\omega$, $\alpha$, $\beta$ (GARCH coefficients; levels are
written "the 5% level"), $\lambda$ (EWMA decay), $\nu$ (Student $t$ degrees of freedom; Volume IV has no constraints),
$\theta$, $\ell(\theta)$, $\mathrm{RV}_t$, $\rho_k$, $\hat\rho_k$, $\operatorname{MSE}$, $\operatorname{SE}$, $H_0$,
$\chi^2_K$, $\Phi$, $\E$, $\Var$, $\Cov$, $\operatorname{Kurt}$, $\operatorname{Skew}$, $m$, $k$, $Q_{\text{LB}}(K)$
(LM25's). No $\operatorname{VR}(m)$: (19.7)'s model ratio, which (26.6) uses, has no symbol (the one-estimator
decision). Local symbols, declared:

| Symbol | Meaning | Check |
|:--|:--|:--|
| $V_t$ | the daily variance target $r_{\mathrm o,t}^2+\mathrm{RV}_t(15\text{ min})$, in %² | §6's $V$ is the SVD's, in modules with an SVD; LM26 has none (LM7 printed $V$ for a mix's variance, lm07.md:416) |
| $r_{\mathrm o,t}$ | the opening return, $\ln$ of the 09:30:00 value over the previous close | a log return, subscripted |
| $\mathrm{RV}_t(h)$, $h$ | realized variance of day $t$ on a grid of interval $h$; the interval in seconds or minutes | §6's $h$ is a generic function where $f$ or $g$ have their meaning; LM26 has no generic function |
| $n$ | intraday returns a day, $14{,}400\text{ s}/h$ | a count; the lag rule writes its day count in words |
| $i$ | the intraday interval index | LM26 has no interest rate or asset index |
| $x_i$, $x_i^{\mathrm e}$, $u_i$, $\sigma_u$, $\sigma_{\mathrm e}$ | observed intraday log index, its efficient part, the noise, their standard deviations (§6, Deep Dive 3) | LM25's $u_t$, $x_t$ (generic series) carried over; LM26 writes no probability level $u$ (quantiles in words) |
| $K$; $a$, $b_j$; $a$, $b$ | lags of the ARCH test; its regression's coefficients; the Mincer–Zarnowitz intercept and slope | §6 gives $a$, $b$ to LM26's auxiliary regressions; $K$ as LM25's $Q_{\text{LB}}(K)$ |
| $m$ | a forecast horizon in sessions | §6's $m$, periods summed |
| $J$ | the number of $h$-intervals in a coarser interval $Jh$, (26.6) and X6 | a count; LM25's $J$ (ADF lags) does not occur here |

Not used: $q$ (no bet or dividend yield: the ARCH order is $K$), $p$ for an order, $L$ for a lag operator, $Z_t$ for an
innovation ($\xi_t$), $R^2$ for R-squared, $\mu$ for the GARCH mean ($g$), a star for an efficient price ($x^{\mathrm
e}$), $\Delta$ for an interval ($h$), $\kappa$ for a fourth moment, $W$ for the estimation window (wealth
book-wide: "the window" in words).

**Motivating case: "The day after the worst day."** (box, about 140 words)

> On Wednesday 2 April 2025, the last session before the Qingming holiday, a GARCH(1,1) model refitted on the previous
> five years forecast a daily standard deviation of 1.72% for the next session, 27.0% a year. An exponentially weighted
> moving average (EWMA) said 1.56% [A26-07]. On Monday 7 April the TAIEX total-return index fell 9.70%, a log return of
> −10.20% [A26-06]: 5.9 of GARCH's standard deviations [A26-07]. That evening the forecasts for 8 April diverged: GARCH
> 3.60%, EWMA 2.92%, and 7 April's own realized variance, read as a forecast, 10.09% [A26-09]. Realized variance from
> 5-second TAIEX data then measured 8 April at 3.39% [A26-09]. Which forecast should a risk manager trust, how fast
> should it fall back, and how can any forecast be judged when a day's true variance is never observed?

7 April 2025 is TR23's largest fall (lm15.md:450), so the box names it as the extreme it is; the multi-day backing is
§7's comparison over 4,609 days and LM13's 108 falls (lm13.md:159). Resolved: (a) which to trust: §7, X7 (GARCH's QLIKE
0.5032 against EWMA's 0.5153 and yesterday's $V$'s 1.1778 [A26-47]; the EWMA gap is 1.83 Newey–West standard errors
[A26-48]); (b) how fast: §4, E4 (half-life 44.2 sessions [A26-21]) and the widget; (c) how to judge: §6 ($V_t$ and its
noise) and §7 (MSE, QLIKE, Patton 2011). The 20 sessions from 7 April had realized volatility 54.3% a year against 19.8%
in the 20 before, and GARCH forecast 48.9% on average over them, EWMA 50.1% [A26-10]: neither forecast wins every
stretch.

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | volatility you can forecast and the day you cannot see; case + X1; roadmap; notation and hygiene notes | 360 |
| 2 | Volatility Clustering and the ARCH Test {1} | the evidence so far, cited (LM13, LM17, LM19's 0.194, LM25's 1,820); conditional variance, $\varepsilon_t=\sigma_t\xi_t$ with its conditions; why uncorrelated returns can have dependent squares; the ARCH test (26.1), $H_0$, upper tail of $\chi^2_K$, *stated without proof* (Engle 1982); E1; KC; pitfall: the test rejects for any change in variance (a calm decade beside a turbulent one), so it names no model | 500 |
| 3 | The Exponentially Weighted Moving Average {2} | the 60-day average and its cliff; EWMA (26.2), weights summing to 1, effective window and weights' half-life, zero mean; RiskMetrics' $\lambda=0.94$ and its criterion (§5.3.2, re-read first); E2 by hand; X2; E3 ($\lambda$ in hindsight, in-sample); EWMA as GARCH with $\omega=0$: a flat forecast; pitfall: a $\lambda$ chosen on the test days | 540 |
| 4 | GARCH(1,1): Model, Forecasts and Half-Life {3} | (26.3) with its four conditions; the recursion as "today's surprise and today's variance"; Deep Dive 1 (the variance as an EWMA of surprises plus a floor; $\varepsilon_t^2$ as an ARMA(1,1) with AR coefficient $\alpha+\beta$, (25.1)); (26.4) derived: unconditional variance, $m$-step forecast, half-life by (25.2); E4; widget; KC; pointers to LM31, LM32, LM39; pitfall: annualizing a one-day forecast by $\sqrt A$ assumes a flat term structure | 620 |
| 5 | Fitting GARCH by Maximum Likelihood {4} | the likelihood as a product of one-day densities; (26.5) for normal $\xi_t$, (20.5) with a changing variance; the start value; E5 (hand $\ell$ = arch's; X3; classic against robust errors, *stated without proof*; the half-life's interval by (20.8) and by mapping $\alpha+\beta$); the $t$ row; E6 (standardized residuals; Deep Dive 2, the implied kurtosis); E7 (what GARCH explains: LM13, LM15, LM16, LM18, LM21); KC; pitfall: a robust standard error does not repair a wrong model | 620 |
| 6 | Realized Variance and the Signature Plot {5} | $\mathrm{RV}_t(h)$ (26.6), the window, $r_{\mathrm o,t}$ and $V_t$; without noise, finer is better (stated, open point); X4; the identity $\E\,\mathrm{RV}(2h)=(1+\rho_1)\E\,\mathrm{RV}(h)$ from (19.7); E8; X6 by year; the noise model (26.7) with (25.3), (25.9) and Deep Dive 3; E9 and X5 (index against TX); the closing auction; the opening return's share; the choice of 15 minutes; pitfall: the finest interval is not the best | 800 |
| 7 | Judging Forecasts Out of Sample {6} | the design (window, refits, six forecasts fixed in advance); MSE and QLIKE (26.8) with units; Patton's robustness, stated; E10, X7; loss differences with (23.7); Mincer–Zarnowitz (26.9) with HC0; robustness to the proxy; X8 by year; X9 (2025); the window check; KC; pitfall: a noisy proxy lowers R-squared, not the ranking | 700 |
| 8 | Volatility Models in Python {7} | `arch_model` on $100r_t$ as a NumPy array, `.params.to_numpy()`, `cov_type="classic"`, `forecast(..., reindex=False).variance.to_numpy()`; the hand likelihood against arch; `het_arch(..., result_object=True)`; `acorr_ljungbox(...).to_numpy()`; `pl.read_csv(..., comment_prefix="#")`; lab box | 220 |
| — | Summary (7) / Problems (12) / Solutions | | 140 / 400 / 500 |
| | **Total** | | **5,400** |

**Elements.** 10 examples (E1 §2; E2, E3 §3; E4 §4; E5–E7 §5; E8, E9 §6; E10 §7). Knowledge checks:

- §2: the ARCH(1) regression gives $a=1.1779$, $b_1=0.1960$ [A26-11]. After a 3% surprise it predicts 2.94 %² for
  tomorrow (1.72%), after a 0.5% one 1.23 %² (1.11%) [A26-55]: today's size moves tomorrow's spread (lm16.md:170).
- §3: with $\lambda=0.97$ the effective window is 33.3 days and the weights' half-life 22.76 days [A26-56].
- §4: $\alpha+\beta=0.98$ gives a half-life of 34.3 sessions; TR23's $t$ fit, 0.99098, gives 76.5 [A26-57].
- §5: why is the robust standard error of $\hat\alpha$ 1.80 times the classic one [A26-62]? The sandwich does not assume
  normal $\xi_t$, and the standardized residuals have excess kurtosis 2.57 [A26-23].
- §6: on the 15-second days $\mathrm{RV}(30\text{ s})/\mathrm{RV}(15\text{ s})=0.7189$, so the pooled $\hat\rho_1$ of
  15-second returns is about −0.281 [A26-61]; the raw download gives −0.2815 [A26-34].
- §7: a forecast half the target scores QLIKE 0.3069, one double the target 0.1931; MSE (target 1 %²) scores 0.25 and
  1 [A26-58]: QLIKE punishes forecasts that are too low, MSE those that are too high.
- §8: arch warns when the residual variance lies outside [0.1, 10,000) (SOURCES, "arch 8.0.0"), so it is given
  $100r_t$; why does `res.params` need `.to_numpy()` before NumPy arithmetic?

中文導讀 (each 3–6 sentences, the intuition, not a translation; 樂詞網 terms from plans/vol-4.md with the English at
first use in each box; the book's own forms and terms not yet looked up print with their English):

- §2: 波動群聚現象 (volatility clustering), 條件變異數 (conditional variance), 自我迴歸條件變異數非齊一模型 (ARCH
  model), 虛無假設 (null hypothesis); why returns can be uncorrelated while their sizes are not.
- §3: 指數加權移動平均模型 (EWMA), 波動率 (volatility); a memory that fades instead of a window that drops days.
- §4: 廣義自我迴歸條件變異數非齊一模型 (GARCH); 半衰期 (half-life), the book's form (樂詞網 lists it only outside
  statistics); a shock that decays toward a long-run level.
- §5: 最大概度估計 (maximum likelihood estimation), 概度函數 (likelihood function), 標準誤 (standard error), 穩健標準誤
  (robust standard error); 標準化殘差 (standardized residual), to look up.
- §6: 實現變異數 (realized variance) and 實現波動率 (realized volatility), LM3's printed form and the book's own (the
  editor's decision), 高頻資料 (high-frequency data), 市場微結構雜訊 (market microstructure noise, named as a
  hypothesis), 自我相關 (autocorrelation); why the finest data are not the best data.
- §7: 均方誤差 (mean squared error); 損失函數 (loss function) and 樣本外 (out-of-sample), to look up; judging a forecast
  against a noisy measurement.

Deep Dives: §4 "The GARCH variance unrolled": iterating (26.3) gives
$\sigma_t^2=\omega/(1-\beta)+\alpha\sum_{j\ge0}\beta^j\varepsilon_{t-1-j}^2$ for $\beta<1$, an EWMA of past surprises
with decay $\beta$ plus a floor; EWMA is the case $\omega=0$, $\alpha=1-\lambda$, $\beta=\lambda$. Writing
$\eta_t:=\varepsilon_t^2-\sigma_t^2$ (conditional mean 0, white noise when the fourth moment is finite; LM25's letter
for an ARMA innovation) turns (26.3) into
$\varepsilon_t^2=\omega+(\alpha+\beta)\varepsilon_{t-1}^2+\eta_t-\beta\eta_{t-1}$, an ARMA(1,1) whose autocorrelations
decay like $(\alpha+\beta)^k$, (25.1). §5 "The kurtosis GARCH implies": squaring (26.3), taking expectations with
$\xi_t$ independent of the past and stationarity gives
$\E\sigma_t^4\,\big(1-(\alpha+\beta)^2-(\E\xi_t^4-1)\alpha^2\big)=\sigma^4\big(1-(\alpha+\beta)^2\big)$, so
$\operatorname{Kurt}(\varepsilon_t)=\E\xi_t^4\,(1-(\alpha+\beta)^2)/\big(1-(\alpha+\beta)^2-(\E\xi_t^4-1)\alpha^2\big)$
when the denominator is positive; $\E\xi_t^4=3$ by (14.6) gives 6.51 at TR23's normal fit, excess 3.51; the $t$ fit's
$\E\xi_t^4=3(\nu-2)/(\nu-4)=6.89$ makes $(\alpha+\beta)^2+(\E\xi_t^4-1)\alpha^2=1.008>1$: no finite fourth moment
[A26-25] (derived, no source needed; checked numerically by the script; no letter for $\E\xi_t^4$, since §6's $\kappa$
is a condition number). §6 "Noise and the variance ratio": $x_i=x_i^{\mathrm
e}+u_i$ with iid efficient returns (variance $\sigma_{\mathrm e}^2$) and iid noise independent of them gives
$\gamma_1=-\sigma_u^2$, $\rho_1=-\sigma_u^2/(\sigma_{\mathrm e}^2+2\sigma_u^2)\in[-\tfrac12,0]$ and
$\E\,\mathrm{RV}(h)=n\sigma_{\mathrm e}^2+2n\sigma_u^2$, linear in $n$; on the 5-second days the rise per extra return
runs from $3.1\times10^{-3}$ to $4.9\times10^{-3}$ of RV(5 min) between neighbouring intervals [A26-65], not constant, so
the noise is not iid (Hansen and Lunde 2006, abstract: noise is time-dependent).

**Exhibits.**

- X1 `case` (table, §1): two rows (forecast made on 2 April for 7 April; made on 7 April for 8 April) × columns GARCH
  (rolling), EWMA 0.94, rolling 60-day, yesterday's $V$, realized $\sqrt{V_t}$, $r_t$; daily %, four decimals.
  Values: 1.7222, 1.5605, 1.3226, 0.7004, realized 10.0859, $r$ −10.2029 [A26-07, A26-08]; 3.6031, 2.9215,
  1.8665, 10.0859, realized 3.3873, $r$ −4.0990 [A26-09]. Note: forecasts out of sample (§7's design); $V_t$ is the
  opening return squared plus the 15-minute realized variance of 09:30–13:30; on 7 April 99.99% of $V_t$ came before
  09:30 (the index opened at its limit) [A26-08]. Source: FinMind `TaiwanStockTotalReturnIndex` (TAIEX), retrieved 18
  October 2026, and `TaiwanVariousIndicators5Seconds` (TWSE's TAIEX), retrieved 19 October 2026; Computations:
  `data/lm26_numbers.py`.
- X2 `vol` (`line`, §3): x date; y annualized volatility, 0–110% (`fmt: "pct1"`). Three series on shared `x.values`,
  each ISO week's last session, 1,224 dates [A26-54]: "GARCH(1,1), in-sample" ($\sqrt A\,\sigma_t$, full-sample normal
  fit), "EWMA 0.94" ($\sqrt A\,\sigma_{t\mid t-1}$), "realized" ($\sqrt{A\cdot\text{week's mean }V_t}$, from 2005, 1,120
  weeks, `null` before); dashed `hline` 19.83% (the unconditional level [A26-20]). Cited: GARCH's maximum 70.41% and
  EWMA's 60.11%, both on 11 April 2025, and the realized week ending 11 April 2025, 100.16% [A26-54]; every cited
  extreme falls on a week's last session, so no date is added. About 40 KB. Note: TR23 log returns; weekly points
  (each week's last session), not the daily series (editor's rule); the GARCH line uses parameters fitted to the whole
  sample. Source: as X1.
- X3 `garchfit` (table, §5): rows $g$ (% a day), $\omega$ (%²), $\alpha$, $\beta$, $\nu$, $\alpha+\beta$, $\sigma^2$
  (%²) and $\sqrt{A\sigma^2}$, half-life (sessions), $\ell$; columns normal (estimate, classic SE, robust SE) and $t$
  (estimate, classic SE, robust SE). Normal: 0.0809 (0.0123, 0.0126); 0.0249 (0.0040, 0.0068); 0.0913 (0.0076,
  0.0137); 0.8932 (0.0086, 0.0151); —; 0.98443; 1.597, 19.83%; 44.2; −8,647.25 [A26-18, A26-20, A26-21]. $t$: 0.0965
  (0.0114, 0.0114); 0.0149 (0.0036, 0.0043); 0.0663 (0.0081, 0.0104); 0.9247 (0.0090, 0.0117); 5.54 (0.41, 0.41);
  0.99098; 1.651, 20.16%; 76.5; −8,463.90 [A26-22]. Note: TR23, 5,849 log returns in percent; arch 8.0.0, constant
  mean, recursion started from arch's backcast (2.78 %² [A26-19]); classic errors from $-\ell''$, robust from the
  sandwich (arch's `cov_type` options; theory in [[LM20]]'s (20.6), stated without proof under dependence);
  $\alpha+\beta$ prints five decimals so that each half-life follows from it by (25.2); in-sample.
- X4 `signature` (`line`, §6): `x.type: "log"`, x the interval in seconds, `x.values` 5, 10, 15, 30, 60, 300, 600, 900,
  1,800 with `ticks` and `tickLabels` "5 s", "10 s", "15 s", "30 s", "1 min", "5 min", "10 min", "15 min", "30 min";
  y log, ratio of the period's mean $\mathrm{RV}(h)$ to its mean $\mathrm{RV}(5\text{ min})$, 0.4–30 (`fmt: "n3"`,
  `tfmt: "n1"`). Four series (`null` where the sampling is coarser than $h$): "2005–2010 (1-minute data)", 1,493 days:
  0.483, 1, 1.164, 1.134, 1.096; "2011–2012 (15-second data)", 487 days from 17 January 2011: 0.699, 0.630, 0.580, 1,
  1.125, 1.106, 1.122; "2015–2026 (5-second data)", 2,867 days: 11.71, 7.248, 5.222, 2.913, 1.730, 1, 0.952, 0.944,
  0.930; "2025", 243 days: 24.26, 14.88, 10.541, 5.602, 2.968, 1, 0.743, 0.642, 0.559 [A26-32] (2025 is inside the
  third series; the note says so). Dashed `hline` 1. Note: TAIEX price index, window 09:30–13:30; ratios of means;
  descriptive; the regime checks in [A26-33]; the 2013–2014 sessions (15- and 10-second data) fall between the second
  and third series and are in X6. Several flagged values (A26-32) print three decimals as listed. Source: FinMind
  `TaiwanVariousIndicators5Seconds` (TWSE's TAIEX), retrieved 19 October 2026; Computations: `data/lm26_numbers.py`.
- X5 `futures` (`line`, §6): `x.type: "log"` as X4 (5 s to 30 min); y log, annualized volatility of the window
  09:30–13:30 in 2025, $\sqrt{A\cdot\text{mean }\mathrm{RV}(h)}$, 8–80% (`fmt: "pct2"`). Series "TAIEX (5-second data)":
  65.27, 51.12, 43.02, 31.36, 22.83, 13.25, 11.42, 10.62, 9.91 [A26-41]; "TX near month (1-minute bars)": 9.26 (1 min),
  9.28, 9.36, 9.17, 9.29 [A26-40]. Note: 243 sessions of 2025; TX's 1-minute returns have $\hat\rho_1=-0.011$, the
  index's −0.421, both from the raw downloads [A26-40, A26-41]; the index's variance is 6.08, 2.04, 1.34 and 1.14 times TX's at 1, 5, 15 and 30
  minutes [A26-41]; two limit-locked days leave TX's ratios unchanged to four decimals [A26-40]. Source: as X4 and
  FinMind `TaiwanFuturesKBar` (TX), retrieved 19 October 2026.
- X6 `byyear` (two stacked `bar` charts, §6; two quantities on different scales): categories 2005–2026, ratios of a
  year's mean realized variances at adjacent intervals, from `vol4_rv.csv` (`fmt: "n3"`). Top, "RV(1 min) ÷ RV(5 min)",
  `hline` 1: from 0.397 (2008) to 2.968 (2025), below 1 in 2005–2012 and 2020, above 1 in every other year [A26-35].
  Bottom, "RV(10 min) ÷ RV(5 min) − 1", `hline` 0: from 0.256 (2007) to −0.257 (2025), below −0.1 only in 2024
  (−0.177) and 2025 [A26-66]. Note: by (26.6) with $J=5$, $\E\,\mathrm{RV}(5\text{ min})/\E\,\mathrm{RV}(1\text{ min})$
  is (19.7)'s model ratio $1+2\sum_{k<5}(1-k/5)\rho_k$ of 1-minute returns, so a top bar below 1 says that 1-minute
  returns within five minutes correlate positively on balance, above 1 negatively; by (26.6) with $J=2$ a bottom bar
  is about $\hat\rho_1$ of 5-minute returns (over all days the ratio and the pooled $\hat\rho_1$ from the raw download
  are both 0.056, A26-34). Neither series is itself a lag-1 autocorrelation; descriptive; price index, window
  09:30–13:30.
- X7 `losses` (table, §7): six rows (rolling 60-day, EWMA 0.94, GARCH normal, GARCH $t$, yesterday's $V$, EWMA of $V$)
  × mean forecast (%²), MSE (%⁴), QLIKE, Mincer–Zarnowitz $b$ (HC0 SE), R-squared, t-stat of the QLIKE difference
  against GARCH normal. Values [A26-47, A26-48]: 1.466, 11.48, 0.5774, 0.763 (0.059), 0.093, 4.82; 1.464, 10.80, 0.5153,
  0.850 (0.083), 0.143, 1.83; 1.411, 10.37, 0.5032, 0.980 (0.114), 0.172, —; 1.394, 10.41, 0.5077, 1.010 (0.118), 0.168,
  1.40; 1.368, 18.18, 1.1778, 0.274 (0.054), 0.075, 11.96; 1.370, 10.78, 0.5209, 0.864 (0.074), 0.143, 1.46. Note: 4,609
  out-of-sample days, 2 January 2008 – 8 October 2026; target $V_t$, mean 1.368 %²; losses (26.8); t-stats Newey–West,
  9 lags; the same QLIKE order with $V_t(5\text{ min})$, $V_t(30\text{ min})$ and $r_t^2$ as targets [A26-49].
- X8 `qlikeyear` (`bar`, §7): categories 2008–2026; series GARCH normal, EWMA 0.94, yesterday's $V$ (`fmt: "n3"`).
  Values [A26-51]; cited: GARCH below EWMA in 12 of 19 years; 2025: 0.611 against 0.733 and 1.866; 2020: 0.666 against
  0.785. Note: out of sample; 2026 to 8 October (185 days).
- X9 `y2025` (`line`, §7): x date, 52 weekly points of 2025 (each week's last session); y annualized volatility
  (`fmt: "pct1"`). Series: "realized" ($\sqrt{A\cdot\text{week's mean }V_t}$), "GARCH normal", "EWMA 0.94", "yesterday's
  V" (each $\sqrt{A\cdot\text{week's mean forecast}}$). Cited: the week of 7 April: 100.16%, 55.86%, 47.22%, 99.52%;
  2025's realized volatility 23.33% [A26-52]. Note: out of sample; weekly means, not the daily series.

**Widget `garchterm` — "How a variance forecast returns to its mean."** `Book.controls`: $\alpha$ (0 to 0.25, step
0.001), $\beta$ (0.60 to 1.00, step 0.001), a select "starting point": "the evening of 7 April 2025"
($\sigma_{t+1\mid t}=3.517\%$) or "8 October 2026" (1.092%) [A26-28]. The initial $\alpha$ and $\beta$ are the
full-sample fit's unrounded 0.091254 and 0.893178, shown as 0.0913 and 0.8932 [A26-18], so that the initial readouts
equal E4's (the rounded 0.0913 and 0.8932 sum to 0.9845, whose half-life is not E4's 44.2); the writer checks that
`Book.controls` keeps an initial value off its step grid, or uses a finer step. The unconditional variance stays at
TR23's fitted 1.5971 %² (19.83% a year), so $\omega=1.5971(1-\alpha-\beta)$; when $\alpha+\beta\ge1$ the widget sets
$\omega=0$ (EWMA, flat at 1; growing above 1) and says "no unconditional variance". `line` chart, x horizon $m$ =
1–250 sessions, y annualized volatility (0–80%): "forecast for day $t+m$" $\sqrt{A\sigma_{t+m\mid t}^2}$ and "average
over the next $m$ days" $\sqrt{A\cdot\frac1m\sum_{j\le m}\sigma_{t+j\mid t}^2}$, dashed `hline` 19.83%, dashed `vline` at
the half-life. Readouts: $\alpha+\beta$ (five decimals, so that the half-life follows from it), the half-life (25.2),
the unconditional volatility, the 20- and 250-day averages. Initial state (PDF): 55.18% at $m=1$, 51.83% over 20 days, 32.57% over 250 [A26-26], half-life 44.2
[A26-21, A26-28]. Model numbers only: no market series, no random draws.

**Examples** (results recomputed from the printed inputs):

- E1 §2: the ARCH test on TR23's $r_t-\bar r$ (percent). $K=1$: $b_1=0.196$, near LM19's $\hat\rho_1(r^2)=0.194$
  [A19-40] because a slope on the lag is about the lag-1 autocorrelation; $(T-1)\cdot$R-squared $=224.8$, p-value
  $8.2\times10^{-51}$ [A26-11]. $K=5$: 696.3 against the 5% point 11.07 of $\chi^2_5$, p-value below $10^{-100}$, the
  five slopes summing to 0.529 [A26-12]. Clustering is beyond doubt; the test does not say which model.
- E2 §3: EWMA by hand. The forecast for 7 April was 1.5605% (2.4351 %²); with $r=-10.2029\%$ the forecast for 8 April
  is $\sqrt{0.94\times2.4351+0.06\times104.0999}=\sqrt{2.2890+6.2460}=2.9215\%$ [A26-16] (both flagged at three
  decimals: print four). The weights $0.06\times0.94^j$ sum to 1; the effective window is 16.7 days, the weights halve
  in 11.2 days, and the last 75 days carry 99.0% of the weight [A26-14] (RiskMetrics' 75 effective days, Table 5.9,
  re-read first). The start, the mean of $r_t^2$ over the first 246 returns (1.84 %²), has weight $8\times10^{-34}$ by
  2008 [A26-15].
- E3 §3: which $\lambda$? Out of sample against $V_t$, QLIKE is 0.5153 at 0.94, 0.5436 at 0.97 and lowest, 0.5087, at
  0.905; GARCH scores 0.5032 [A26-17]. Picking 0.905 uses the test days, so it is an in-sample choice; RiskMetrics fixed
  0.94 across hundreds of series by the root mean squared error of variance forecasts (§5.3.2, re-read first).
- E4 §4 (full-sample normal fit, $\alpha+\beta=0.98443$, $\sigma^2=1.5971$ %²): on the evening of 7 April,
  $\sigma_{t+1\mid t}=3.517\%$ (12.3695 %²); by (26.4) the forecasts fall to 3.42%, 3.10%, 2.66% and 1.35% at $m$ = 5,
  20, 44 and 250 sessions, and the average over the next 20 days is 51.8% a year and over 250 days 32.6% [A26-26],
  toward $\sigma=1.264\%$ a day [A26-20]. On 8 October 2026 the forecast was 1.092%
  (17.13% a year), below the unconditional 19.83%, and rises toward it [A26-27]. arch's `forecast` gives the same
  values (difference $2\times10^{-14}$).
- E5 §5 (X3): the normal GARCH on TR23 by maximum likelihood: $\hat g=0.0809\%$, $\hat\omega=0.0249$ %²,
  $\hat\alpha=0.0913$, $\hat\beta=0.8932$, $\ell=-8{,}647.25$; the NumPy likelihood with arch's backcast equals arch's to
  $10^{-6}$ [A26-18, A26-19]. $\alpha+\beta=0.98443$ and $\sigma^2=1.597$ %², 19.83% a year against the sample's
  18.99% [A19-54] [A26-20]. Half-life 44.2 sessions; the delta method (20.8) with robust errors gives an SE of 16.1
  and an interval of 13 to 76 sessions; mapping the interval for $\alpha+\beta$ (0.97342 to 0.99544, from the
  unrounded estimate and robust SE 0.0056) gives 26 to 152 sessions [A26-21]: near 1 the half-life is poorly
  determined and its interval is lopsided. (Whole sessions, so that each end follows from the printed inputs.) The $t$ row: $\hat\nu=5.54$, $\ell$
  higher by 183.35, half-life 76.5 [A26-22].
- E6 §5: standardized residuals $\hat\xi_t=(r_t-\hat g)/\hat\sigma_t$: excess kurtosis 2.57 against $r_t$'s 5.428
  (lm17.md:387), skewness −0.59 against −0.47 [A26-23]; $Q_{\text{LB}}(10)$ of $\lvert\hat\xi_t\rvert$ 27.6 (p-value
  0.002) against $\lvert r_t\rvert$'s 1,820 ([[LM25]], A25-22) [A26-24]; the ARCH test ($K=5$) on $\hat\xi_t$ gives 14.3,
  p-value 0.014 [A26-13]. GARCH removes most of the dependence of sizes, not all. Deep Dive 2: the normal model implies
  excess kurtosis 3.51, the $t$ model none finite [A26-25]. LM5's lab question on TR23: 17 days lie at or below −4.107
  standardized by $s$, 9 standardized by GARCH, against 0.117 under the normal model [A26-63]; changing volatility
  explains part of the tail, not all.
- E7 §5, what GARCH explains (in-sample; then *Model*): after the 108 falls of 3% or more, 13 next days fell ([[LM21]],
  A21-25; lm13.md:159); GARCH with the residuals' own distribution expects 7.8, against 2.0 for independent days; after
  the 67 rises it expects 5.4 where 3 fell [A26-29]. The model raises the risk after any large move; the data raise it
  more after falls, an asymmetry GARCH(1,1) cannot express, named in words with Hansen and Lunde's (2005, abstract)
  "leverage effect" (their term, quoted; the book's leverage stays $f>1$); the lab's extension fits it. After $\lvert R_t\rvert\ge2\%$ the next day's size averaged
  1.27% against 0.80% after other days; GARCH predicts 1.35% and 0.79% [A26-64] ([[LM16]]'s U28 pattern, on TR23).
  Experiment 1 (`default_rng([1, 20261011])`, 1,000 paths): the variance-to-mean ratio of monthly counts of
  $\lvert R\rvert\ge3\%$ has median 3.15 (batch SE 0.035), 5% to 95% of paths 2.04 to 5.14, against TR23's 3.02
  ([[LM15]]) and resamples' variance 0.598 against the mean 0.612, the value of independent days (lm18.md:379,
  lm15.md:48) [A26-30]. The same paths' excess kurtosis has median only 1.63
  (5.3% reach 5.428); with $t$ innovations (experiment 2) 7.0 [A26-30, A26-31].
- E8 §6: the variance ratio read backwards. On the 5-second days $\mathrm{RV}(10\text{ s})/\mathrm{RV}(5\text{ s})-1=
  -0.381$ from the file against the pooled $\hat\rho_1=-0.380$ from the raw download; on the 15-second days −0.281 and
  −0.2815; at 5 minutes 0.056 both ways [A26-34]. By the noise model (a hypothesis), $\hat\rho_1=-0.386$ in 2025 (raw
  download) means noise supplies 77% of a 5-second return's variance [A26-37]; the year's daily values, from the raw
  download, run from −0.52 to −0.19, the middle half from −0.41 to −0.33 [A26-36]. The spine's 2025 test days
  (`plans/vol-4.md` at commit bcfa0d4, LM26's spine: −0.36 to −0.46; not printed) sit inside that range; the claim is
  made for the 2025 test days only. $\mathrm{RV}(5\text{ s})/\mathrm{RV}(5\text{ min})$ was 24.3 for the year's means
  and 25.2 for the median day, up to 62.6 [A26-32, A26-36].
- E9 §6 (X5): the index against its future, 2025. The TAIEX's 1-minute returns have $\hat\rho_1=-0.421$ (from the raw
  download) and an annualized window volatility of 22.8%; the near-month TX's have −0.011 and 9.26%, flat from 1 to 30
  minutes (ratios 1.00, 1.02, 0.98, 1.00 to 5 minutes) [A26-40, A26-41]. Even at 30 minutes the index's variance is
  1.14 times TX's [A26-41]. Whatever moves the index at high frequency is not in the market's price of the index;
  candidate causes (prices of slow stocks that update late, the bounce of heavy stocks between bid and ask) are named
  as hypotheses, since no source in SOURCES states either for the TAIEX.
- E10 §7 (X7): out of sample against $V_t$, GARCH normal has the lowest QLIKE (0.5032) and MSE (10.37 %⁴); EWMA is
  worse by 0.0121 in QLIKE (Newey–West t-stat 1.83, p-value 0.067) and by 0.428 in MSE (t-stat 2.98); GARCH $t$ differs
  from normal by 1.40 and 0.62 standard errors; yesterday's $V$ is worst (t-stat 11.96 in QLIKE) [A26-47, A26-48].
  Mincer–Zarnowitz for GARCH: $a=-0.015$ (HC0 SE 0.135), $b=0.980$ (0.114), t-stat for $b=1$ −0.18, R-squared 0.172;
  against $r_t^2$ the R-squared falls to 0.119 [A26-50], above Andersen and Bollerslev's (1998) 0.047 and 0.026 for
  currencies and below their "about half" with 5-minute realized volatility, because two thirds of $V_t$ is the single
  squared opening return [A26-43].

**Problems plan** (12; MC keys B, A, C, A, B; the lab solves 10, 11, 12). Stems state the sample (TR23, 3 January 2003 –
8 October 2026, $T=5{,}849$ log returns in percent; T5S, 5,351 sessions from 3 January 2005; 4,609 out-of-sample days
from 2 January 2008), units (%², %⁴), $A=246.12$, the divisor ($T$), the target $V_t$, the standard-error method
(classic, robust, HC0, Newey–West with 9 lags), the test's null and side, and for a simulation the seed and the number
of paths.

1. MC: EWMA with $\lambda=0.97$; its effective window. A 22.76 days (the weights' half-life). **B** 33.3 days. C 32.3
   days ($\lambda/(1-\lambda)$, the mean lag) [A26-56].
2. MC: GARCH(1,1) with $\omega=0.025$ %², $\alpha=0.09$, $\beta=0.89$, $A=246.12$; the unconditional annualized
   volatility. **A** 17.5%. B 7.5% ($\omega/(1-\beta)$: $\alpha$ forgotten). C 1.12% ($\sqrt{1.25}$, a daily value)
   [A26-59].
3. MC: half-life of a shock with $\alpha+\beta=0.98$. A 25 sessions ($0.5/(1-0.98)$, a linear decay). B 50 sessions
   ($1/(1-0.98)$, the mean lag). **C** 34.3 sessions [A26-57].
4. MC: judged against $r_t^2$ instead of $V_t$, TR23's GARCH R-squared falls from 0.172 to 0.119 while the QLIKE order of
   the six forecasts stays the same [A26-49, A26-50]. **A** $r_t^2$ is an unbiased but noisier proxy: the ranking stays
   valid, differences are harder to detect. B $r_t^2$ is biased, so its ranking is invalid (given the past, its mean is the
   conditional variance plus the tiny squared mean). C a low R-squared shows a poor forecast (the proxy's noise caps it).
5. MC: 5-second returns with pooled $\hat\rho_1=-0.40$ and no other autocorrelation; $\mathrm{RV}(10\text{ s})/
   \mathrm{RV}(5\text{ s})$ is about A 1.40 (sign reversed). **B** 0.60. C 0.20 ($1+2\rho_1$, counting each pair twice)
   [A26-60].
6. Derive (26.4) from (26.3); apply it from 7 April 2025 (12.3695 %², $\alpha+\beta=0.984432$, $\sigma^2=1.5971$ %²):
   $\sigma_{t+20\mid t}=3.097\%$, the 20-day average 51.8% a year [A26-20, A26-26].
7. Show that EWMA's weights sum to 1, that its effective window is $1/(1-\lambda)$, and that EWMA is GARCH with
   $\omega=0$, $\alpha=1-\lambda$, $\beta=\lambda$, whose $m$-step forecast is flat (Deep Dive 1).
8. Derive $\E\,\mathrm{RV}(2h)=(1+\rho_1)\E\,\mathrm{RV}(h)$ from (19.7) for a sum of two returns (pooled pairs, the
   day's edge ignored); under the noise model show $\rho_1\ge-\frac12$ and that noise supplies the share
   $2\lvert\rho_1\rvert$ of a return's variance; apply to 2025's −0.386 (from the raw download): 77% [A26-37].
9. Derive the kurtosis of Deep Dive 2 for normal $\xi_t$, evaluate it at X3's normal fit (6.51), and explain why
   experiment 1's paths have a median of only 1.63 [A26-25, A26-30].
10. Python: the normal GARCH log-likelihood by hand in NumPy with arch's backcast; compare with `arch_model(...).fit()`
    (−8,647.25) and report $\hat\sigma_t$ on 7 April 2025, 1.737% [A26-18, A26-26].
11. Python: the out-of-sample EWMA (0.94) and GARCH-normal forecasts with §7's design; QLIKE 0.5153 and 0.5032, the
    Newey–West t-stat of the difference 1.83 with 9 lags [A26-47, A26-48].
12. Python: X4 from `vol4_rv.csv` for 2015–2026, and $\hat\rho_1\approx\mathrm{RV}(10\text{ s})/\mathrm{RV}(5\text{ s})-1
    =-0.381$ [A26-32, A26-34].

**Lab parts** (`build/make_lab26.py`; reads only its `data/`: `taiex_tr.csv`, TR23's raw closes as Volume III's labs,
and `vol4_rv.csv`, a copy of the committed `data/derived/vol4_rv.csv`; `make_lab_data.py` gains `"LM26_lab": {**tr23,
"vol4_rv.csv": <copy of data/derived/vol4_rv.csv>}`, a source outside `data/raw/`): 1 data: TR23's $r_t$ in percent,
$T$, $A$; `vol4_rv.csv` with `comment_prefix="#"`, its regimes, $V_t$; 2 E1 by hand and with `het_arch`; 3 EWMA by hand
(E2), its weights, X2's EWMA line, E3's $\lambda$ grid; 4 the GARCH likelihood by hand, arch's normal and $t$ fits with
both error types (E5, X3), standardized residuals (E6), the term structure (E4, the widget's values); 5 E7 with
experiment 1 (and experiment 2 as an option, its run time stated); 6 X4, X6's by-year ratios and E8's file values;
7 the out-of-sample comparison (X7, X8, X9, E10) with Newey–West and HC0 checked against statsmodels; 8 Problems 10–12.
Optional part (needs the 2025 T5S files, 243 calls), the route to the 2025 numbers printed "from the raw download":
the daily $\hat\rho_1$ of 5-second returns (E8's range), the pooled 5-second $\hat\rho_1$ of 2025 (E8's −0.386) and the
1-minute $\hat\rho_1$ (E9's −0.421); the pooled values over all years need the full download (`data/lm26_numbers.py`).
Extension: arch's asymmetric term (`o=1`), refitted on TR23 and E7's two counts recomputed; does the
model now expect more falls after falls than after rises? Labs write "LM31", never `[[LM31]]`.

**Cross-module tags** (probable users):

- (26.1) ARCH test: OLS of $\hat\varepsilon_t^2$ on a constant and $\hat\varepsilon_{t-1}^2,\dots,
  \hat\varepsilon_{t-K}^2$; under $H_0$ (no ARCH, iid $\varepsilon_t$ with a finite fourth moment) $(T-K)\cdot$R-squared
  is approximately $\chi^2_K$ for large $T$, upper tail (*stated without proof*, Engle 1982) (LM32, LM34).
- (26.2) EWMA $\sigma_{t+1\mid t}^2=\lambda\sigma_{t\mid t-1}^2+(1-\lambda)r_t^2=(1-\lambda)\sum_{j\ge0}\lambda^jr_{t-j}^2$,
  $0<\lambda<1$, zero mean; effective window $1/(1-\lambda)$ (LM30, LM31, LM32).
- (26.3) GARCH(1,1): $r_t=g+\varepsilon_t$, $\varepsilon_t=\sigma_t\xi_t$, $\xi_t$ iid mean 0 variance 1,
  $\sigma_t^2=\omega+\alpha\varepsilon_{t-1}^2+\beta\sigma_{t-1}^2$ with $\omega>0$, $\alpha\ge0$, $\beta\ge0$,
  $\alpha+\beta<1$ (LM31, LM32, LM39).
- (26.4) $\sigma^2=\omega/(1-\alpha-\beta)$; $\sigma_{t+m\mid t}^2=\sigma^2+(\alpha+\beta)^{m-1}(\sigma_{t+1\mid t}^2-
  \sigma^2)$; half-life $\ln\frac12/\ln(\alpha+\beta)$ by (25.2); (26.3)'s conditions (LM31, LM32).
- (26.5) $\ell(\theta)=-\frac12\sum_t\big[\ln2\pi+\ln\sigma_t^2+\varepsilon_t^2/\sigma_t^2\big]$, normal $\xi_t$, given
  a start value $\sigma_1^2$; its maximizer's large-sample normality under dependence is *stated without proof*,
  citing [[LM20]]'s (20.6) for the theory and arch's documented `cov_type` options for the classic and robust errors
  (the editor's decision) (LM32).
- (26.6) $\mathrm{RV}_t(h)=\sum_{i=1}^n(x_i-x_{i-1})^2$, $n=14{,}400\text{ s}/h$; with returns stationary within the day,
  $\E\,\mathrm{RV}(Jh)=\big[1+2\sum_{k=1}^{J-1}(1-k/J)\rho_k\big]\E\,\mathrm{RV}(h)$, (19.7)'s ratio for the
  $h$-returns ($\rho_k$ their lag-$k$ autocorrelation), and $\E\,\mathrm{RV}(2h)=(1+\rho_1)\E\,\mathrm{RV}(h)$ (pooled,
  day edges ignored) (LM30, LM39).
- (26.7) $x_i=x_i^{\mathrm e}+u_i$, iid efficient returns and iid noise independent of them: $\rho_1=-\sigma_u^2/
  (\sigma_{\mathrm e}^2+2\sigma_u^2)\in[-\frac12,0]$ and $\E\,\mathrm{RV}(h)=n\sigma_{\mathrm e}^2+2n\sigma_u^2$ (LM39).
- (26.8) losses for a variance forecast $f$ and proxy $V$: $\operatorname{MSE}=(V-f)^2$, $\text{QLIKE}=V/f-\ln(V/f)-1
  \ge0$; with a conditionally unbiased proxy both rank forecasts as the true variance would (*stated without proof*,
  Patton 2011) (LM31, LM32, LM34).
- (26.9) Mincer–Zarnowitz: OLS of $V_t$ on a constant and $f_t$; an unbiased forecast has $a=0$, $b=1$; HC0 errors,
  (23.6) (LM32, LM34).

**Pitfalls to pre-empt.**

- Conditions every time: (26.3) needs $\omega>0$, $\alpha,\beta\ge0$ and $\alpha+\beta<1$ for an unconditional
  variance; the kurtosis formula a positive denominator; the ARCH test's $\chi^2_K$ iid errors with a fourth moment;
  Patton's robustness a conditionally unbiased proxy.
- The finest interval is not the best: read through the noise model (a hypothesis), noise supplies most of a 5-second
  return's variance; at 5 minutes the 2025 index still carried twice TX's variance (2.04, [A26-41]).
- A realized variance from 09:00:00 contains the overnight gap (PITFALLS §3); $V_t$ keeps it as one squared return,
  which is two thirds of $V_t$ [A26-43] and most of its noise.
- $V_t$ is 0.933 of $r_t^2$ on average (Newey–West t-stat −3.26; 0.918 in 2025, 1.011 in 2008) [A26-44]: the intraday
  pieces miss part of the close-to-close variance, so $V_t$ is not an unbiased proxy for TR23's day; the ranking is
  checked against $r_t^2$ (X7's note).
- Classic and robust standard errors differ by a factor of 1.7–1.8 for $\omega$, $\alpha$, $\beta$ [A26-62]: say which
  one is printed; neither repairs a wrong model.
- A half-life near a unit root: report the interval mapped from $\alpha+\beta$, not the delta method's symmetric one.
- A $\lambda$ or a model chosen on the test days is in-sample (E3).
- QLIKE needs $V_t>0$ and $f_t>0$; MSE in %⁴ is dominated by a few days (yesterday's $V$: mean difference 7.8 %⁴, t-stat
  only 2.54 [A26-48]).
- Data traps: $A=246.12$, never 252; $r_t$ in percent for arch, in decimals in the text's formulas only where said;
  arch's `params` is a pandas Series (`.to_numpy()`); `het_arch` without `result_object=True` warns; the 10-second regime
  has no 15-second grid (NaN); TX bars are labelled by their start; the closing auction freezes the index from the
  first value after 13:25:00 (13:25:00 plus one sampling step) to the last value before 13:30:00, on every day of
  every regime ([A26-42], from the raw download).
- Ownership: $\hat\rho_k$ of TR23 and the iid band are [[LM19]]'s; the robust band and $\lvert r\rvert$'s Ljung–Box are
  [[LM25]]'s; LM26's are the ARCH test, EWMA, GARCH, the T5S statistics and the forecast comparison.
- Notation: $\alpha$ is a GARCH coefficient, so the level is "the 5% level"; $\nu$ the $t$'s degrees of freedom;
  $g$ the model's mean, not $\mu$; $K$ the ARCH lags.
- References (SOURCES; chapters and sections, not pages unless recorded): Engle (1982; end page open); Bollerslev
  (1986; bibliographic only, read its abstract first); *RiskMetrics — Technical Document* (1996, §5.3.2, Table 5.9;
  re-read first); Andersen and Bollerslev (1998); Andersen, Bollerslev, Diebold and Labys (2003; abstract read);
  Zhang, Mykland and Aït-Sahalia (2005, §1.2.5); Hansen and Lunde (2005; 2006, abstracts); Patton (2011; the 2006
  working paper's Section 3); Tsay (2010, ch. 3, §3.6, §7.2) at chapter level, not for the GARCH standard errors,
  which cite [[LM20]]'s (20.6) and arch's documented options; Barndorff-Nielsen and Shephard (2002) only after it is
  read. No signature-plot origin is attributed (open point); Corsi (2009) is not cited, so HAR is not named.

**Stage 4 for earlier modules.** `leads` gain 26 in lm03.md:6 and lm14.md:6 (lm05.md:6 is in the plan's list already;
lm13, lm15–lm18 list 26). The sibling briefs' tag lists of (19.7) and (23.7) now include LM26. lm03.md:710's
實現變異數 stays: LM26 uses LM3's term (the editor's decision), so no wording changes.

**Open before Stage 2** (the editor's LM26 decisions answer the drafter's questions; these sources and records are
still open, and until they close the text is written as the decisions say):

- The ARCH test's $\chi^2_K$ law, the GARCH MLE's large-sample normality and the sandwich are *stated without proof*;
  Engle (1982) is cited at article level (its end page is open), the GARCH standard errors to [[LM20]]'s (20.6) and
  arch's documented `cov_type` options.
- RiskMetrics' $\lambda=0.94$, its criterion and the 75 effective days are printed only after §5.3.2 and Table 5.9 are
  re-read (SOURCES open point).
- QLIKE's normalized form (zero for a perfect forecast) is checked in Patton's text before printing; the MSE and QLIKE
  robustness is cited to the 2006 working paper's Section 3 as SOURCES records it.
- The causes of the signature (stale prices, the bounce of heavy stocks, TWSE's matching rules) stay hypotheses until a
  source in SOURCES states one for the TAIEX. Candidates to verify: TWSE's history of its matching method and its
  tick-size table; Roll (1984) and Lo and MacKinlay (1990), not in SOURCES and unverified.
- Corsi (2009): HAR is named only once it is in SOURCES.
- 樂詞網 lookups for 標準化殘差, 損失函數 and 樣本外 (until then each prints with its English).
