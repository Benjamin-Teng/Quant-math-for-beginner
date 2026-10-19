# Authoring guide

How a learning module (LM) is written, checked, reviewed and published. The reference module is
[`src/lm03.md`](src/lm03.md); when this guide and LM3 disagree, follow this guide.

## 1. Reader, voice, length

- **Reader:** a Taiwan-based futures/securities professional reviewing university mathematics on the way to
  quantitative portfolio work. Comfortable with markets; rusty on proofs. Prefers derivations to assertions and
  expects approximations to be called approximations. Reads English as a second language and wants the tools
  learned systematically rather than a lot of material: worked examples, diagrams and formulas carry the content,
  and the prose connects them (owner, 2026-10-11).
- **Language:** English body text. Hard ideas get a **中文導讀** callout (`> [!zh]`) in Traditional Chinese, about one
  per one or two sections, 3–6 sentences, never a translation of the paragraph above it but the intuition behind it.
  Keep English terms in the Chinese text where they help (e.g. 波動拖累 volatility drag). Use Taiwan usage
  (最適, not 最優; 權益歸零 for zero equity, since 斷頭 means forced liquidation). Mathematical terms follow 樂詞網
  (terms.naer.edu.tw), its mathematics or statistics listing (another field's entry, or the common form, when neither
  lists the term), with the English term in parentheses at first use in each box; a row is 列 and a column is 行.
- **Voice:** textbook register, concise. Active voice, concrete numbers, no filler ("it is worth noting", "in
  today's world"), no emoji, no questions as headings. For a reader of English as a second language, clarity comes
  before brevity. The sub-rules below are for English text: all of it from Volume II on, and new or changed
  sentences in Volume I (why: `project/PITFALLS.md` §6, "Hard sentence caps"). A 中文導讀 follows the Language rule,
  the first two sentences of this item and the formula-punctuation rule.
  - A sentence ends at `.`, `?` or `!` (a semicolon does not end it) and makes one main point; a definition, theorem
    or result may state linked conclusions in one sentence.
  - Put the main clause early: a condition may come first ("If …, then …"; "When …, …"), a chain of clauses may not.
    Keep the logical connectors (because, so, hence, but): a shorter sentence that has lost its "because" is worse.
  - Sentences average under 16 words in a module, and none exceeds 30. A sentence of 25–30 words stays only when it
    binds conditions to a conclusion, lists parallel items or carries one chain of reasoning; otherwise split it.
  - One idea per paragraph, at most 80 words. Each list item, each lettered part of a solution and each text block of
    a box is a paragraph; a sentence that continues after a display stays one sentence of its paragraph.
  - A bare "this", "it" or "that" never refers back across a paragraph break; after a display, name what you refer to
    ("this equation", "(10.3)").
  - A theorem with more than two hypotheses lists them (a hypothesis is a clause with its own verb; standing
    assumptions may go in a "Let …" sentence before it).
  - One term per concept: the term in the module's Glossary, which keeps an earlier module's term for the same
    concept; no synonyms for variety. Plain verbs rather than idioms or phrasal verbs ("exclude", not "rule out").
  - Avoid noun stacks (at most two nouns before the head noun), stacked negatives and more than one colon in a
    sentence. An inline formula longer than about 15 symbols goes in a display.
  - Never start a sentence with a symbol, that is anything in math mode: "The variance is $V=…$", not "$V=…$ is …".
    A ticker or a number (even in math mode) may start a sentence, an entry of a notation note may start with the
    symbol it defines, and a part label such as (a) is not part of the sentence. Separate two formulas by words.
  - Counting: split on white space after replacing each inline formula and each `[[…]]` reference by one token.
    Exempt from the sentence and paragraph limits: the symbol lists of a notation note, the Source and Computations
    sentences of an exhibit note, tables, code and displayed math.
- **Formula punctuation (every volume):** after an inline formula put a space, an opening bracket or a character the
  renderer keeps on the formula's line (`GLUE` in `build/build.py`: `. , ; : ! ? ) ] ’ ” " '` and `，。、」』）】》！？`).
  Anything else, such as a hyphen, a dash, a letter, `%` or a fullwidth `；` or `：`, can start the next line
  (`project/PITFALLS.md` §4): write `$k\text{th}$` or "step $k$", "$5\%$", "from $k$ to $m$", and recast the Chinese
  clause.
- **Length:** from Volume II, at most 6,000 words of prose and 36 A4 pages, examples, problems and solutions
  included; first drafts stay under 5,500 words so that revisions have room. Prose is counted as in Voice over the
  English text after the front matter, without displays, tables, code, headings, box titles, the Glossary and the
  References (Volume I modules have 6,300–8,300 such words and run 33–40 pages; Volume I keeps its 40-page limit and
  has no word limit).

## 2. File layout for module NN

| File | Content |
|:--|:--|
| `src/lmNN.md` | the module (front matter + Markdown) |
| `src/lmNN.js` | optional interactive figures (`Book.widgets.<name> = function (host) {…}`) |
| `src/data/lmNN-*.json` | chart specs, written by a script, never by hand |
| `data/lmNN_*.py` | scripts that compute every number quoted in the module (add them to `DATA_STEPS` in `build.sh`) |
| `data/raw/…` | verified raw data, git-ignored and registered in `data/raw_manifest.json` (see §8) |
| `build/make_labNN.py` | generates `labs/LMNN_lab/LMNN_lab.ipynb` |
| `labs/LMNN_lab/` | notebook (saved with outputs), `README.md`; its `data/` is built locally by `data/make_lab_data.py` |

A standalone page (Getting Started, Research hygiene) is `src/pages/<slug>.md`, listed under `pages:` in
`src/syllabus.yaml` with its `slug`, a `title` equal to the page's own, and `status: published` once it may reach
`docs/`. Its front matter holds only `title` and `description`; it takes the Markdown, callouts, formulas and `[[LMn]]`
links of a module, but no `js:`, no attributes on headings (`{lo=…}`, `{-}`) and no PDF. The builder stops on any of
these.

## 3. Front matter

```yaml
---
lm: 1
title: Exponentials, Logarithms and Compounding        # must match src/syllabus.yaml
subtitle: "One line that states the module's point."
prereq: []                 # module numbers this one builds on (every module it cites for a result)
leads: [3, 19, 38]         # module numbers that build on this one
time: "≈ 2 h + lab"
js: [lm01.js]              # only if the module has widgets
outcomes:                  # 6–8; each completes "After this module you should be able to:"
  - "convert between periodic, effective annual and continuously compounded rates"
overview:                  # 6–8 bullets stating results, with numbers where possible
  - "…"
---
```

Outcomes start with an action verb (calculate, derive, explain, interpret, apply, compare), lower case, no final
period. YAML strings with backslashes need double escaping inside double quotes (`"$\\ln x$"`).

## 4. Module structure

1. `## Introduction` (unnumbered LO): one framing paragraph, then a `> [!case]` **Motivating Case** built on real,
   verified data that the module resolves later, then an exhibit with the case numbers, then a short roadmap.
   A `> [!note]` on notation lists the module's local symbols (see §6).
2. Numbered sections `## Title {lo=2,3}`: each maps to one or more outcomes. Inside: intuition → definition →
   derivation → exhibit → worked example → pitfall → 導讀 → knowledge check. Not every section needs every element.
3. Unnumbered closing sections, in this order: `## Summary {-}`, `## Practice Problems {-}`, `## Solutions {-}`,
   `## Glossary {-}`, `## References {-}`.

## 5. Markdown dialect

| Syntax | Use |
|:--|:--|
| `$…$`, `$$ … \tag{N.k} $$` | inline and display math; number only equations that are referred to, as `(N.k)` with N = module number |
| `> [!definition] Term` | precise English definition |
| `> [!theorem]`, `> [!proposition]`, `> [!result]` | statements; a proof follows or sits in a Deep Dive |
| `> [!example] Title {#label}` + nested `> > [!solution]` | worked example (8–10 per module) |
| `> [!exhibit] Title {#label}` | numbered table or chart; a final `Note:` or `Source:` line becomes the caption |
| `> [!pitfall] Title` | a common mistake and its fix |
| `> [!zh] 標題` | 中文導讀 |
| `> [!deepdive]- Title` | optional rigorous proof, collapsed |
| `> [!kc]` + nested `> > [!answer]-` | knowledge check (one per numbered section) |
| `> [!case] Title`, `> [!note] Title`, `> [!python] Title` | motivating case, side note, pointer to code/lab |
| `[[LM14]]`, `[[LM14\|text]]` | link to another module (rendered as "coming" until it is published) |
| `[[ex:label]]`, `[[eg:label]]` | "Exhibit k" / "Example k" with automatic numbering; never type exhibit or example numbers by hand, not even in code comments or widget notes |
| `<div data-chart="lmNN-name"></div>` | chart from `src/data/lmNN-name.json` (inside an exhibit) |
| `<div class="widget" data-widget="name"></div>` | interactive figure defined in `src/lmNN.js` |
| ` ```python ` | code block with copy button |

- Write `NT\$` for New Taiwan dollars: an unescaped `$` starts math. Inside math, `\text{NT\$}` works.
- Every exhibit is cited in the prose at least once.
- In References, give every URL link text (`[site, page](https://…)`); bare URLs are hard to read in print.
- Every book in References gives its year, the publisher's copyright year of the edition cited, and names that
  edition unless it is the first (Stewart 2021, 9th ed.; Spivak 2008, 4th ed.; Hull 2022, 11th ed.);
  `project/SOURCES.md` records the check.

Practice problems are an ordered list; multiple-choice options are a nested list `- **A.** …` (three options, A–C,
"*closest* to" for numeric answers; vary which letter is correct). Solutions are an ordered list with the same
numbering; multiple-choice solutions start with "**B** is correct." and explain why the distractors are wrong when
that teaches something.

## 6. Mathematics and notation

**One symbol, one meaning.** Within a module a symbol has exactly one meaning. The book-wide symbols below keep their
meaning in every module; a module may add local symbols in its notation note but may not reuse a book-wide symbol
for something else, except where a row below scopes the reuse to named modules or to a kind of module (for example LM25's $b_t$, $a_j$,
$u_t$, $\zeta_t$, $K$; LM23's $h_t$; LM26's $u_i$, $h$, $K$): the module then does not use the book-wide meaning,
and its notation note declares the local one.

**Common notation first** (owner, 2026-10-11). Use the symbols a reader meets in standard textbooks and in practice
($\sigma$ for a volatility, $\rho$ for a correlation, $\Sigma$ for a covariance matrix, $\beta$ for a regression slope,
$\Delta$ for a change), so that the book never asks the reader to learn private symbols. A module introduces a new
symbol only where no common one exists or the common one would clash with a book-wide symbol below, and its notation
note says why.

| Symbol | Book-wide meaning |
|:--|:--|
| $R$, $r$ | simple return per period; $r:=\ln(1+R)$ the log return. A continuously compounded rate is also an $r$: $r_f$, $r(t)$ |
| $\mu$, $\sigma$ | mean and standard deviation of $R$ in a model; $\bar R$ (or $\hat\mu$) and $s$ are the sample mean and standard deviation, $s$ with divisor $T$ (from Volume IV, $s_{\mathrm u}$ divides by $T-1$) |
| $g$, $G$ | log growth rate per unit time ($g(f)$: growth as a function of exposure); growth factor, end value ÷ start value |
| $\mathrm{RV}$ | $\sum_t R_t^2$, realized variance |
| $A$ | periods per year used to annualize, e.g. $A=243.1$ trading sessions; always say which sample it comes from |
| $T$, $t$, $\tau$, $n$ | either a sample size (number of returns) or a horizon or maturity in years: a module uses one of the two and says which; time index; time to maturity or expiry, or any span in years when $T$ is a count; number of compounding or payment periods |
| $P$, $W$, $D$, $\mathrm{DD}$ | price; wealth; cash dividend ($D_1$ the next dividend); drawdown |
| $f$, $f^*$, $c$ | exposure ÷ equity of a position ($f>1$ is leverage); its growth-maximizing (Kelly) value; $c:=f/f^*$, the fraction of full Kelly (LM25, without Kelly, writes $c$ for an AR intercept; in LM24, $c$ is the data's weight in a posterior, which is the Kelly fraction its Bayes bet takes) |
| $L$ | a leveraged fund's fixed daily multiple (00631L: $L=2$); for a portfolio, total exposure $\sum_i f_i$; in a module without leverage, a Cholesky factor, declared (table below) |
| $p$, $q$, $b$, $a$ | binary bet: win probability, $q=1-p$, gain $b$ and loss $a$ per unit staked, so $f^*=p/a-q/b$. In futures pricing $q$ is instead the continuous dividend yield; a module uses one of the two. LM21, without bets, writes $p_i$ for p-values and $q$ for a false-discovery level; LM26's auxiliary regressions write their coefficients $a$, $b$ |
| $r_f$ | risk-free or financing rate (state the compounding) |
| $\mathrm{SR}$ | Sharpe ratio $(\mu-r_f)/\sigma$ of a return; say the period (per day, or annualized) |
| $w$, $\mathbf w$, $\mathbf f$, $\Sigma$, $\rho$ | portfolio weights summing to 1; vector of exposures; covariance matrix; correlation |
| $\varphi$, $\Phi$ | standard normal density and distribution function |
| $B_t$ | standard Brownian motion ($W$ stays wealth, so $dW_t=W_t(\mu\,dt+\sigma\,dB_t)$ reads unambiguously); a module without Brownian motion may use $B$ for a balance, or (LM18) the number of bootstrap resamples, declared in its notation note |
| $y$, $i$, $v$, $k$, $\gamma$ | yield to maturity or IRR; periodic interest rate; discount factor $1/(1+i)$; required return; growth rate of dividends or cash flows (simple, per period) |
| $\lambda$, $\nu$, $\mathcal L$ | multiplier of an equality constraint (with a subscript, $\lambda_k$ is an eigenvalue: table below); multipliers of inequality constraints (KKT), or in a module about distributions a Student $t$'s degrees of freedom (a module uses one of the two); Lagrangian. In a module about distributions without constraints, $\lambda$ is a Poisson mean or an exponential rate. Volume IV has no constraints: there $\mathcal L(\theta)$ is a likelihood, and LM26's $\lambda$ is the EWMA decay |
| $h$, $u$; $\psi$ | generic functions in modules where $f$ or $g$ already have their book-wide meaning ($f$, $g$, $h$ are fine in purely mathematical modules; from Volume III $u$ is instead a probability level or a uniform draw, table below); constraint functions, $\psi(x)=b$ or $\psi_i(x)\le b_i$ (there $b$ is a constraint level, not a bet's gain: a module uses one of the two) |

**Vectors and matrices** (from Volume II; LM7 already writes vectors, transposes and $\Sigma$ this way):

| Symbol | Book-wide meaning |
|:--|:--|
| $\mathbf x$, $\boldsymbol\mu$ | a vector is bold lower case (bold Greek with `\boldsymbol`) and a column; a vector of a book-wide capital quantity keeps its letter in bold capitals ($\mathbf R_t$ returns, $\mathbf P_t$ prices); column $j$ of a matrix $M$ is $\mathbf m_j$; inline, a column is written $(x_1,\dots,x_N)^{\top}$; a displayed vector or matrix uses `pmatrix` |
| $M$, $K$; $m_{ij}$ | a matrix is a plain capital; a generic matrix is $M$ (a second one $K$), never $A$, which annualizes; $m_{ij}$ is the entry in row $i$ and column $j$ |
| $^{\top}$, $M^{-1}$, $\det M$, $\operatorname{rank}M$, $\operatorname{tr}M$ | transpose (never $^T$, since $T$ is a count, and never a prime, which is a derivative); inverse; determinant; rank; trace |
| $I$, $\mathbf 0$, $\mathbf 1$, $\mathbf e_i$ | identity ($I_N$ when the size matters); zero vector; vector of ones; $i$th standard basis vector, in a module that does not use LM7's excess-return vector $\mathbf e$ |
| $\lVert\mathbf x\rVert$, $\lVert M\rVert_2$, $\mathbf x^{\top}\mathbf y$, $\theta$ | Euclidean norm; spectral norm, $\max_{\lVert\mathbf u\rVert=1}\lVert M\mathbf u\rVert$ (the largest absolute eigenvalue of a symmetric $M$); dot product (LM8 also writes $\mathbf x\cdot\mathbf y$); angle between two vectors ($\varphi$ stays the normal density); from Volume IV, in a module without angles, $\theta$ is a parameter (statistics table below) |
| $N$, $i$, $j$; $T$, $t$ | number of assets and asset indices; number of returns and the date index |
| $\mathbf R_t$, $X$, $\tilde X$, $\bar{\mathbf R}$ | vector of the $N$ simple returns on date $t$; the $T\times N$ matrix whose row $t$ is $\mathbf R_t^{\top}$ (date first, asset second), so its entry $x_{tj}$ is $R_{j,t}$, the return of asset $j$ on date $t$ (asset first); its centred version $X-\mathbf 1\bar{\mathbf R}^{\top}$; vector of sample means |
| $\hat\Sigma$, $\mathbf s$, $C$ | sample covariance matrix $\tilde X^{\top}\tilde X/T$ (divisor $T$; in NumPy `ddof=0`, `rowvar=False`); vector of sample standard deviations; correlation matrix $\operatorname{diag}(\mathbf s)^{-1}\hat\Sigma\operatorname{diag}(\mathbf s)^{-1}$ |
| $\sigma_p^2$, $s_p^2$ | portfolio variance $\mathbf w^{\top}\Sigma\mathbf w$ in a model; $\mathbf w^{\top}\hat\Sigma\mathbf w$ in a sample |
| $\lambda_k$, $\mathbf q_k$, $Q$, $\Lambda$, $\kappa$ | eigenvalues $\lambda_1\ge\dots\ge\lambda_N$, always subscripted (the multiplier of the variance-maximizing unit vector is one, LM11); unit eigenvectors, each signed so that its entry largest in absolute value is positive (on a tie, the first of the tied entries); $Q=(\mathbf q_1\ \cdots\ \mathbf q_N)$; $\Lambda=\operatorname{diag}(\lambda_1,\dots,\lambda_N)$; condition number, $\lambda_1/\lambda_N$ for a positive definite matrix (LM7's $M/m$) |
| $L$, $\mathbf z_t$ | Cholesky factor, $\hat\Sigma=LL^{\top}$ with $L$ lower triangular, in a module without leverage, declared; whitened vector $L^{-1}(\mathbf R_t-\bar{\mathbf R})$ |
| $U$, $S$, $V$, $s_k$ | singular value decomposition $M=USV^{\top}$; singular values $s_1\ge s_2\ge\dots\ge0$ on the diagonal of $S$, in a module with an SVD (elsewhere $s_i$, the entries of $\mathbf s$, are the assets' sample standard deviations); for data the book decomposes $\tilde X/\sqrt T$, so that $\lambda_k=s_k^2$ |
| $\mathbf y$, $\hat{\boldsymbol\beta}$, $\hat{\mathbf y}$, $\hat{\boldsymbol\varepsilon}$, $\Pi$ | least squares: response (in a module without yields), coefficients, fitted values, residuals, projection matrix $X(X^{\top}X)^{-1}X^{\top}$ ($P$ stays the price and $H$ the Hessian); the share of variance a fit explains is written "R-squared" in words, never $R^2$, which is a squared return, and a formula may use $\cos^2\theta$ |
| $M\mathbf x=\mathbf b$ | a linear system; $\mathbf b$ is a vector, in a module without bets |

**Probability** (from Volume III; LM5 already writes $\Pr$, $X\sim\mathcal N(\mu,\sigma^2)$ and $Z$ this way):

| Symbol | Book-wide meaning |
|:--|:--|
| $\Omega$, $\omega$ | sample space; an outcome (sequences of trades or days as $+$/$-$ strings); LM26, without a sample space, writes $\omega$ for a GARCH constant |
| $\Pr(\cdot)$, $\Pr(B\mid A)$ | probability and conditional probability (`\mid`), never $P$, the price. Events are sets, $\{R\le-3\%\}$; capital letters $A$, $B$ for events only in a module that does not annualize (LM13), with $A^c$ the complement |
| $\mathcal A$, $\mathcal B$ | an event in a general statement, in a module that annualizes, where $A$ is the annualization factor; LM13, which does not annualize, writes $A$, $B$ |
| $\mathbf 1_{\mathcal A}$, $\mathbf 1\{\cdot\}$ | indicator of an event, always with a subscript or braces (bold $\mathbf 1$ alone is the vector of ones); $\E[\mathbf 1_{\mathcal A}]=\Pr(\mathcal A)$ is (14.1) |
| $X$, $Y$, $Z$; $x$, $y$, $z$ | random variables and their values; $Z$ a standard normal; $R$ and $r$ are random returns. A module that writes random variables does not use the data matrix $X$ |
| $\mathbf X$, $\mathbf Z$ | random vectors; $\mathbf Z$ a standard normal vector ($\mathbf z_t$ stays LM12's whitened data) |
| $p_X$, $f_X$, $F_X$, $F_X^{-1}$; $\hat F$, $\hat F^{-1}$, $\E_{\hat F}$ (also $\Var_{\hat F}$, $\Pr_{\hat F}$, LM22) | pmf, density, distribution function and quantile function $F_X^{-1}(u):=\min\{x:F_X(x)\ge u\}$, always subscripted ($f$ is an exposure, $p$ a win probability); empirical distribution function of a sample, mass $1/T$ on each observation, its quantile function (order statistics) and expectation under it |
| $u$, $U$ | a probability level in $F^{-1}(u)$; a value of a uniform random variable $U\sim\operatorname{Unif}(0,1)$ |
| $\E$, $\Var$, $\Cov$, $\operatorname{Corr}$; $\operatorname{Skew}$, $\operatorname{Kurt}$ | expectation, variance, covariance, correlation (macros `\E`, `\Var`, `\Cov`); standardized third and fourth moments, excess kurtosis $\operatorname{Kurt}-3$ |
| $\mu_X$, $\sigma_X$, $\sigma_{XY}$, $\rho_{XY}$ | moments of random variables; unsubscripted $\mu$, $\sigma$, $\rho$ stay the return's. A population correlation is $\rho$, a sample one $\hat\rho$ in a module with both |
| $\bar R$, $s$; $\bar r$, $s_r$; $g$, $\sigma_r$ | sample mean and standard deviation of $R$ and of $r$ (divisor $T$; $s_{\mathrm u}$ divides by $T-1$); model mean log return per day $g=\E[\ln(1+R)]$ and its standard deviation |
| $\mathcal N$, $\mathcal N_N$, $t_\nu$, $\chi^2_N$, $\operatorname{Bin}(n,p)$, $\operatorname{Poisson}(\lambda)$, $\operatorname{Exp}(\lambda)$ | distributions; "iid" independent and identically distributed |
| $n$, $\bar X_n$, $S_n$; $m$ | number of independent draws or trials, their mean and sum ($T$ stays the number of returns in a data sample); number of days summed or compounded in a model, whole sessions ($m=\operatorname{round}(A\tau)$) |
| $j$, $R_{(j)}$; $k$ | the value of a count in a pmf, the $j$th smallest return; a number of standard deviations, $k\ge0$, in a module without a required return; in Volume IV a lag (statistics table), and in LM20 the Hill estimator's tail count, declared |
| $\eta$, $\zeta$ | constants in $\Var(\eta X+\zeta)$ (LM5's letters; $a$, $b$ are a bet's) |
| $d^2$ | squared Mahalanobis distance $(\mathbf x-\boldsymbol\mu)^{\top}\Sigma^{-1}(\mathbf x-\boldsymbol\mu)$ |

**Statistics and time series** (from Volume IV, `plans/vol-4.md`; one meaning per module, declared in its notation
note):

| Symbol | Book-wide meaning |
|:--|:--|
| $\theta$, $\hat\theta$, $\boldsymbol\theta$ | a parameter, its estimator, a parameter vector, in a module without angles; in LM21 also a binomial probability under test |
| $\operatorname{Bias}$, $\operatorname{MSE}$, $\operatorname{SE}$ | bias, mean squared error and standard error of an estimator, upright: $\operatorname{SE}(\bar R)$ |
| $s_{\mathrm u}$, $s_\varepsilon$ | standard deviation with divisor $T-1$, $s_{\mathrm u}^2=\frac{T}{T-1}s^2$; a regression's residual standard deviation, $s_\varepsilon^2=\text{RSS}/(T-d)$. A script passes `ddof` explicitly (NumPy defaults to 0, Polars to 1) |
| $\mathcal L(\theta)$, $\ell(\theta)$, $\mathcal I(\theta)$ | likelihood, log-likelihood $\ln\mathcal L$, Fisher information ($I$ stays the identity) |
| $H_0$, $H_1$; $\text{t-stat}$ | null and alternative hypotheses; a t-statistic, upright, with its estimate when needed, $\text{t-stat}(\hat\beta)$ ($t$ stays the date index and $t_\nu$ the distribution); the Dickey–Fuller statistic is "the DF t-stat" |
| $p_i$, $p_{(i)}$; $m$; $q$ | in LM21: the p-values of $m$ tests and their ordered values; the number of tests; the false-discovery level. Elsewhere "p-value" is written in words |
| $\alpha$ | one meaning per module: a significance level (LM21, LM22); a regression intercept and Jensen's alpha (LM23); a GARCH coefficient (LM26); a tail index (LM15, LM20). A module whose $\alpha$ is not the level writes the level as a percentage ("the 5% level") |
| $\beta$, $\hat{\boldsymbol\beta}$; $\alpha_0$, $\beta_0$ | regression or cointegrating coefficients (LM23, LM25), a GARCH coefficient (LM26); the parameters of a $\operatorname{Beta}(\alpha_0,\beta_0)$ prior (LM24) |
| $\mu_0$, $\sigma_0$ | prior mean and standard deviation of a mean parameter (LM24); a parameter's density is an $f$ with a subscript |
| $\varepsilon_t$, $\hat\varepsilon_t$; $\eta_t$; $\xi_t$ | a regression's error and residual (LM23), LM26's innovation $\varepsilon_t=\sigma_t\xi_t$; white noise of an AR or MA model (LM25); an iid standardized innovation, mean 0, variance 1, normal or scaled Student $t$ (LM26; $Z$ stays a standard normal) |
| $X$, $d$ | LM23's $T\times d$ design matrix, first column $\mathbf 1$, and its number of coefficients (LM23 writes no random variable $X$) |
| $\rho_k$, $\hat\rho_k$, $\gamma_k$, $\hat\gamma_k$ | autocorrelation and autocovariance at lag $k$, model and sample; $\hat\rho_k$ uses the full-sample mean and divisor $T$ in numerator and denominator (LM19). $\gamma$ without a lag keeps its meaning above |
| $\operatorname{VR}(m)$ | variance ratio: the variance of overlapping $m$-day log-return sums, centred at $m\bar r$, over $m$ times the daily variance (LM19's (19.8); LM22, LM25; LM26 writes (19.7)'s ratio without the symbol) |
| $\phi_j$, $\theta_j$; $\delta$ | AR and MA coefficients, always subscripted ($\phi_1$ even in an AR(1); $\varphi$ stays the normal density); the Dickey–Fuller coefficient $\delta=\phi_1-1$ (LM25) |
| $F_t$, $S_t$ | TX settlement price and TAIEX close (LM23 in E6's contract count, $200F_t$ a contract; LM25; LM6 writes $F$, $S$; $F_X$ keeps its subscript) |
| $b_t$, $a_j$, $u_t$, $\zeta_t$, $K$; $h_t$; $u_i$, $h$ | LM25's log basis, ADF lag coefficients, one-day white noise, the persistent part's innovation and the Ljung–Box lag count; LM23's hat values; LM26's intraday noise and sampling interval (and its lag count $K$) — local, declared; each displaces a book-wide meaning its module does not use ($b$, $a$ a bet's; $u$ a probability level; $\zeta$ LM5's constant; $K$ a second matrix; $h$ a generic function) |
| $\sigma_t^2$, $\sigma^2_{t+1\mid t}$ | conditional variance of day $t$; its forecast made on day $t$ (LM26) |
| $\mathrm{RV}_t$ | realized variance of day $t$, the sum of squared intraday log returns at a stated interval (LM26; the table's $\mathrm{RV}$ is the same idea on simple returns) |
| $B$, $\ell$ | number of bootstrap resamples; block length or mean block length (LM22), Newey–West lag (LM23); neither module writes a likelihood |
| $\hat f$, $\hat f^*$, $f_{\mathrm B}$ | $\bar R/s^2$, the plug-in Kelly fraction (from LM20); the exact in-sample root of (4.5) (LM22, LM24); LM24's Bayes fraction, $f_{\mathrm B}=c\hat f$ |
| $\operatorname{med}$ | a sample median, $\hat F^{-1}(\tfrac12)$, upright (LM19); a tilde means centred ($\tilde X$, $\tilde r_t$) |

Words with one meaning each: "unconditional variance" is GARCH's $\omega/(1-\alpha-\beta)$ (LM26) and "long-run
variance" the HAC target (LM23); "leverage" is $f>1$ (a regression point's influence is its hat value, LM23; LM26 quotes Hansen and Lunde's
"leverage effect" as their term). Not used: $R^2$ for R-squared, a star for a bootstrap draw ($\bar R_{\text{boot}}$),
$L$ for a lag operator (write $x_{t-1}$), $\tau$ for a Dickey–Fuller statistic, $Z_t$ for a non-normal innovation.

- Subscripted standard symbols are distinct symbols and may sit beside the table: $D_{\text{mod}}$, $D_{\text{Mac}}$,
  $D_{\mathrm{KL}}$, $a_{n,i}$, $s_{n,i}$, $T_1(x)$.
- A Deep Dive may use the standard variables of its argument even if the table gives them another meaning (for
  example $\rho,\theta$ as polar coordinates), provided it declares them in its first sentence; the main text may not.
- A star marks an optimum or a solution ($f^*$, $x^*$, $\Delta x^*$); do not use it for other special values.
- Integer indices and counts ($i$, $j$, $k$, $m$, $n$ as a summation index, a step number, an order or a count) are
  not book-wide symbols, but each still has one meaning in a module, and a module that also uses the letter's table
  meaning ($k$ a required return or a number of standard deviations, $m$ a number of days, $n$ a number of periods or
  draws, $i$ a periodic rate) picks another letter for the index.
  The notation note lists the counts a module uses.
- In a module without bets, $a$ and $b$ may be generic constants (an expansion point, the ends of an interval),
  declared in the notation note.
- In a purely mathematical passage $x$ and $y$ may be generic coordinates, declared in the notation note and
  instantiated per example, as $f$, $g$, $h$ may be generic functions; a module that also uses $y$ as a yield picks
  other letters.
- `=` only for exact statements; `≈` comes with the order or size of what was dropped; `:=` for definitions.
- State the conditions of every theorem (differentiability, convexity, sign or sum constraints on weights).
- Every formula the reader is asked to use is either derived or explicitly labelled *stated without proof* with a
  reference. Rigorous proofs go in Deep Dives.
- Use only what earlier modules teach. When a later idea is needed (skewness, kurtosis, confidence intervals,
  covariance, matrices), introduce it in a sentence or two and point to the module that develops it.
- Check every derivation numerically in the module's script before writing it down.

## 7. Exhibits, charts and widgets

- Exhibits are numbered automatically in order of appearance; reference them only with `[[ex:label]]`.
- Tables: right-align numbers (`--:`), give units in headers, round consistently, and make sure printed values add up
  as printed (if a sum is shown, its parts must sum to it at the displayed precision). Say when partial years or
  sub-samples are excluded.
- A chart must show every value the text cites from it (do not thin a series past the extremes you quote).
- Chart spec (`src/data/*.json`, produced by `data/lmNN_charts.py`):
  `{"alt", "height", "x": {"type": "date"|"num"|"log", "fmt", "label", "tipLabel", "min", "max", "ticks",
  "tickLabels", "values"}, "y": {"type": "lin"|"log", "fmt", "tfmt", "label", "min", "max", "ticks"}, "series":
  [{"name", "endLabel", "color": "1".."4" or a CSS colour, "dash", "area", "x": [...], "y": [...]}], "ann":
  [{"type": "vline"|"hline"|"point"|"band", ...}], "endLabels", "endValue", "endMargin"}`.
  On a date axis, series and annotation dates may be ISO strings or epoch milliseconds; ticks fall on year starts when
  at least three are in range, otherwise on month starts (every 1, 2, 3 or 6 months, labelled "Jan 2026", "Apr", …).
  On a numeric axis, `ticks` fixes the tick values and `tickLabels` (one string per tick) replaces their text;
  `x.tfmt` formats the ticks only (the tooltip keeps `x.fmt`), as `y.tfmt` does.
  Format codes: `pct0..pct3`, `bp`, `x0..x2` (multiples), `n0..n6`, `sci0..sci3` (scientific, "2.00e−5") and
  `sig2..sig4` (significant figures with trailing zeros kept, "1.20"; scientific outside 1e−4 to 1e6). The sig codes are
  for tooltips and readouts: an axis ticks with an n or sci `tfmt` (a narrow sci axis can show a single tick: use
  more digits). At most four named series; legend is
  automatic.
  From Volume III, series options: `step: true` draws a post-step line (`y[i]` holds from `x[i]` to `x[i+1]`), for
  histograms on bin edges and distribution functions; a series with `lo` and `hi` arrays instead of `y` is a band, the
  filled region between them (with a legend entry; `build.py` refuses lengths that differ from `x`); `quiet: true` is
  a thin translucent line with no legend entry, tooltip row, hover dot or end label, for dozens of simulated paths
  (`opacity`, `width` override). Bands are drawn first, then quiet lines, then the rest. `hline` and `vline`
  annotations take `dash: true`. A log axis ignores values at or below zero. From Volume IV: `x.type: "log"` is a
  log $x$ axis, ticked like a log $y$ axis (1, 2 and 5 times powers of ten, only the powers of ten when that gives
  more than eight ticks); `ticks` and `tickLabels` work as on a numeric axis, and the tooltip header prints the
  value itself in `x.fmt`. `build.py` refuses a log $x$ axis where any $x$ (in a series, `x.values`, `x.min`,
  `x.max`, `x.ticks` or an annotation) is not a number above zero. `x.values` is one $x$ array for every series
  without its own `x` (dates as ISO strings or epoch milliseconds, as in a series), so several series on the same
  days carry their dates once. `build.py` refuses a series whose `y`, or a band whose `lo` and `hi`, is not as long
  as its $x$ (its own `x`, else `x.values`), and a band with `lo` above `hi`; a `step` series may instead have one
  `y` fewer than its $x$ (bin edges and the heights between them).
- Other chart types: add `"type"` to the spec (`"line"` is the default, and the spec above is a line chart). All types
  need `alt`, share the legend, tooltip, colour tokens and format codes, and are drawn by `Book.chart(host, spec)`.
  - `"bar"`: `categories` (one text each), `valueLabels`, `x: {label}`, `y: {fmt, tfmt, label, min, max, ticks}`,
    `series: [{name, color, values, fmt}]`, `ann: [{"type": "hline", y, label}]`. Bars start at zero, several series
    stand side by side. Category labels that do not fit tilt by 40 degrees (long ones are cut with an ellipsis); with
    very many categories only every k-th is labelled, and the tooltip names every one. Value labels drop out when they
    would not fit. Keep to about 30 categories on screen.
  - `"heatmap"`: `labels` (rows and columns alike) or `rows` and `cols`; `matrix` (one array per row; `null` is a
    blank cell); `fmt` (cell text, default `n2`), `min` and `max` (default -1 and 1), `scale: false` to hide the colour
    bar, `scaleFmt`, `valueName` (tooltip). The scale is diverging and centred at 0 (series 1 above, series 2 below).
    Labels are cut to 16 and 18 characters, to 7 when the cells would be under 10 px, and dropped below that: a matrix
    larger than about 25 rows loses its labels on a phone, so list the order of rows in the exhibit note.
  - `"scatter"` and `"vector"` share one drawing routine; a vector diagram has equal scales on both axes (`equal`,
    default true; `equal: true` widens an author's own `x`/`y` `min`/`max` until the scales match) and dashed
    `segments`, a scatter plot has free scales and solid `lines`. Keys: `x`, `y` (`label`, `fmt`, `tfmt`, `min`, `max`,
    `ticks`, `tickLabels`, `name` for the tooltip), `series: [{name, color, x, y, labels, r}]` (points), `points:
    [{at, label, color, r, dx, dy}]`, `lines` and `segments: [{from, to, extend, dash, color, width, label}]`,
    `vectors: [{from, to, label, color, width, dash, dx, dy}]` (arrows; `from` defaults to the origin), `ellipses:
    [{center, cov, scale, color, fill, axes, label}]` (the contour x'S^-1 x = scale^2 of a positive semi-definite
    2x2 `cov`; anything else fails).
    From Volume IV: `bands: [{x, lo, hi, color, opacity, name}]` fills the region between `lo` and `hi` (`opacity`
    0.18 unless given, `color` the ink grey unless given) under everything else, and counts in the axis range; a
    `null` in `lo` or `hi` leaves a gap. A band's `name` is a legend entry, and as with series the legend shows only
    with two or more entries (series and named bands) or `legend: true`; name the points' series
    too, or the legend shows an entry without text. `build.py` refuses arrays of unequal
    length, an $x$ that is not a finite number and `lo` above `hi`. `tickLabels` (one string per tick, with
    `ticks`; `null` keeps the number) replaces the tick text on either axis. Long $y$ labels widen the left margin
    up to 40% of the chart's width and are cut with an ellipsis beyond that (about 20 characters on a phone); the
    tooltip of a point on a labelled $y$ tick prints the whole label.
- Series names, categories and labels may mark `a_1` and `x_{ij}` as subscripts and `A^T` and `x^{2}` as superscripts:
  in legends and tooltips of every chart type, in the text drawn on bar, heatmap, scatter and vector charts, and in
  line-chart end labels (not in a line chart's axis titles or annotations). A `^` or `_` followed by anything but a
  letter, digit or `{...}` (as in `e^(-2t)`) stays as typed.
- `build.py` refuses a chart spec without a non-empty `alt` string, or one that is not strict JSON: write a missing
  point as `null`, never `NaN`. On any axis of any chart type it refuses `tickLabels` that is not an array as long
  as that axis's `ticks` (a missing label would shift every later one to the wrong tick). It refuses a chart or
  widget JSON over 300,000 bytes as inlined (compact JSON in UTF-8), and warns when a built page is over 2,000,000
  bytes (the largest, LM7, was 1,500,849 in edition 0.4); the warning gives the page's size, the total of its
  inline charts and its three largest charts. A spec the browser cannot draw leaves a one-line note and the other
  charts alone.
- Chart text (legends, labels, end labels) uses no combining marks: the chart font has no Greek, so a hat drifts off
  its letter (write "sample mean", or keep μ̂ for the exhibit note, which renders in the body font).
- Code blocks keep lines to 80 characters: longer lines are cut off at A4 print width.
- Widgets use `Book.chart(host, spec)` (or `Book.lineChart`) and `Book.fmt(v, code)` from `src/assets/book.js`; they must render a
  meaningful initial state (it is what the PDF shows) and must not depend on external libraries. Shared helpers (from
  Volume III): `Book.controls(host, defs, onChange)` builds sliders, selects and buttons (`defs`: `id`, `label`,
  `min`, `max`, `step`, `value`, `fmt`, `options`, `type`) and calls `onChange(values, id)` at most once a frame;
  `Book.rng(seed)` is a seeded generator (`uniform()`, `normal()`, `int(n)`; an integer seed, the same stream in every
  browser, not NumPy's); `Book.dist` has `phi`, `Phi`, `PhiInv`, `lgamma`, `tPdf`, `tCdf`, `poissonPmf`, `poissonCdf`,
  `binomPmf` and `chi2Cdf`, checked against SciPy by `build/qa/test_bookjs_dist.py`. Use them instead of copying local
  versions.

## 8. Data

- Real Taiwan and US data, and for historical data FinMind only (`TaiwanStockPrice`, `TaiwanStockDividendResult`,
  `TaiwanFuturesDaily`, `TaiwanStockTotalReturnIndex`, `USStockPrice`, …), fetched through the FinMind API with
  `data/fetch_finmind.py` and a token, a whole series per query where the dataset allows it. Intraday history
  (`TaiwanVariousIndicators5Seconds`, minute bars, ticks) is large and answers one day per request: download it with
  `data/fetch_intraday.py` into `data/raw/intraday/<series>/<year>/`. That script keeps its own manifest
  (`data/raw_intraday_manifest.json`, one entry per day), logs every request, stops cleanly at the hourly quota,
  retries an empty answer on a trading day instead of listing it, and checks every day (`--check`);
  `fetch_finmind.py --verify` does not need it. A day that fails a check for a reason you have confirmed goes into the
  script's `EXCEPTIONS` with that reason, as `drop` (left out downstream), `grid` (kept) or `steps` (a real move
  above the step bound, kept).
- Store raw files in `data/raw/` exactly as returned (`date,close,spread` for prices) and register each one in
  `data/raw_manifest.json` with `uv run python data/fetch_finmind.py --add …`. `data/raw/` is git-ignored: FinMind's licence
  forbids redistributing raw data, so the repository keeps only the manifest and the scripts. Verify every close against
  FinMind's `spread` column with `data/check_chunk.py`; accept mismatches only on ex-dividend days (spread printed as
  0.0) and split days, and handle those explicitly in the script that builds returns. Around a split, restate the
  previous price per new share. Futures files (`TaiwanFuturesDaily`) differ: the spread is against the contract's
  previous *settlement*, an untraded contract prints a close of 0, and from 2008-12-17 the expiring contract's
  settlement prints 0 on its last day, so `check_chunk.py` does not apply and the series script checks them per
  contract (`data/vol4_series.py`). The last day's close is not the final settlement price, which TAIFEX publishes
  (`TaiwanFuturesFinalSettlementPrice`).
- Per-day statistics of raw data that a reader could rebuild only with a long intraday download are committed in
  `data/derived/` (owner, 2026-10-19: per-day statistics only, never intraday prices or returns). Each file starts
  with a `#` line crediting FinMind and the original source, and `data/README.md` gives its licence (FinMind's terms,
  not the MIT licence). Its builder rebuilds it only from a complete download that passes every check, and otherwise
  keeps the committed file. `data/derived/vol4_rv.csv` holds realized variances on the window 09:30:00–13:30:00 (the
  5-second TAIEX prints the previous close at 09:00:00) and, as its own column, the squared log change from the
  previous close to 09:30:00 (the overnight gap and the first half hour); it holds no
  signed return and no price level. The `Source:` line of an exhibit built on such a file names FinMind, the dataset
  and TWSE.
- Every number in the text, tables, examples, knowledge checks, problems and solutions must be produced by a script
  in `data/` or by the lab, and re-checked after the last edit.
- Conventions: a horizon in years is calendar days ÷ 365.25 unless an instrument has its own day count, which is the
  issuer's: name the bank or issuer whose terms you quote (DBS Taiwan accrues NTD deposits on actual/365; Bank of
  Taiwan credits whole months and only part months by day). Quote the annualization factor $A$ of the sample in use.
- A motivating case built on one day says whether that day is typical or the extreme of the sample, and backs the
  claim with a multi-day figure.
- Futures: TAIEX closes on a 13:25–13:30 call auction while the TX daily settlement is set from the last minute of
  trading to 13:45, so daily basis changes are noisy. Back months trade thinly; report volume when it matters, and
  remember that an untraded contract's settlement price is set by exchange rules.
- Cite the dataset and retrieval date in the exhibit's `Source:` line.
- Simulation (from Volume III): each simulated experiment (an example, a problem, an exhibit, a lab part) creates its
  generator once, at its start, as `np.random.default_rng([e, 20261011])` with `e` the experiment's stated number
  first, as NumPy recommends (varying IDs before the root seed), and never reseeds it; the stem or note prints the
  seed. A printed Monte Carlo or bootstrap result states the number of
  draws, the seed and its standard error, and keeps only the digits its standard error supports. The numbers script
  re-runs it under the NumPy that `uv.lock` pins. Widgets simulate with `Book.rng(seed)` from a fixed initial state.

## 9. Labs

Polars-first notebooks (NumPy/SciPy at the numerical edge, Matplotlib for plots) that run on Polars 1.x and 2.x:
pass literals to expressions with `pl.lit(...)` (strings are column names), avoid `map_elements` when a native
expression exists, and never rely on row order after a join (pass `maintain_order` or sort). A lab rebuilds the
module's exhibits and computational examples, solves the computational practice problems, and ends with one
extension exercise. It reads only files in its own `data/` folder, which is git-ignored and built from `data/raw/`
(and, for committed per-day statistics, `data/derived/`) by `data/make_lab_data.py` (add the lab's files there).
Commit it executed (`./build.sh --labs` or
`uv run jupyter nbconvert --to notebook --execute --inplace LMNN_lab.ipynb` inside the lab folder). Use only packages in `pyproject.toml` (the standard library's `urllib` for an
optional live refresh, not `requests`); add a new one with `uv add` after asking the owner.

Standard wording, the same in every module (FinMind's licence forbids redistributing its data, so no FinMind data are
bundled):

- The module's companion-lab box keeps the sentence that says what the notebook rebuilds, minus any claim about bundled
  data or a snapshot, and then, in a paragraph of its own (four sentences), says: "The notebook reads FinMind files that you download once with your own token. From the repository root, run
  `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow
  the book to redistribute the data. After that, the notebook runs offline." LM26's box adds a fifth sentence: "The
  realized variances come with the repository (`data/derived/vol4_rv.csv`); rebuilding them needs the 5-second TAIEX
  download, `uv run python data/fetch_intraday.py --series taiex5s` (5,351 requests, about nine hours on a free
  FinMind account, re-run after each hourly stop)."
- The notebook's first cell: "**Environment.** From the repository root, `uv sync` installs the locked Python
  environment (`uv.lock`). Open this notebook with the `.venv` kernel, or run `uv run --with jupyterlab jupyter lab`."
- The lab's README runs `uv sync` and `uv run --with jupyterlab jupyter lab labs/LMNN_lab/LMNN_lab.ipynb` from the
  repository root, re-executes with `uv run jupyter nbconvert --to notebook --execute --inplace LMNN_lab.ipynb` inside the lab folder,
  and builds `data/` with the two commands above.
- `build/make_labNN.py` writes the notebook, including its first cell, and for some labs the README: change the
  generator and regenerate, because `./build.sh --labs` overwrites edits made to the generated files.
- Script docstrings show how to run the script: `uv run python data/lmNN_x.py`.

## 10. Checks before a module goes to review

1. `uv run python build/build.py lmNN` runs without KaTeX errors (a draft builds into `dist/preview/`).
2. No horizontal overflow at 400 px: `uv run python build/qa/overflow.py dist/preview/lm/lmNN.html 400`.
3. Screenshots in light and dark mode look right (`build/qa/shoot.py`).
4. Every number reproduced by the scripts; every `[[ex:…]]`/`[[eg:…]]` points where the prose intends.
5. The lab executes from a clean kernel.
6. The PDF (`build/render_pdf.py`) has at most 40 pages (Volume I) or 36 pages (from Volume II, §1) and is not
   shrunk: `uv run python build/qa/pdf_scale.py
   <pdf>`. Chromium shrinks the whole document when anything is wider than the A4 text width, so a page count from a
   shrunk PDF is too low; `build/qa/print_width.py <html>` lists what sticks out.
7. From Volume II, the §1 counts hold: at most 6,000 words of prose, no sentence over 30 words, an average under 16,
   no paragraph over 80 words; in every volume, nothing after an inline formula that §1's formula-punctuation rule
   does not allow. `uv run python build/qa/style.py src/lmNN.md` checks all of this and lists the 25–30-word
   sentences for a second look.
8. From Volume II, no display formula needs sideways scrolling on a phone: `uv run python build/qa/display_scroll.py
   dist/preview/lm/lmNN.html 400` (`overflow.py` cannot see a display that scrolls inside its own box). Volume I's
   displays that scroll inside their own box (92 at 400 px) are accepted; TODO lists their clean-up as optional.

## 11. Review and publishing

1. **Draft.** The writer delivers the files in §2. Drafts are committed to `main` but stay off the site: only
   modules whose entry in `src/syllabus.yaml` has `status: published` are built into `docs/`. Preview the whole site,
   drafts included, with `uv run python build/build.py --preview` and open `dist/preview/index.html`.
2. **Independent review.** Someone who did not write the module recomputes every number from the raw data, solves
   every problem, checks the mathematics, facts, notation (§6) and Chinese, and reports findings by severity.
3. **Fixes.** The writer fixes every finding or explains in writing why not, then re-runs §10.
4. **Publish.** Add `status: published` to the module's syllabus entry, add an edition note, update the status table
   in `README.md`, run `./build.sh --pdf`, and commit `src/`, `data/`, `labs/` and `docs/` together.
