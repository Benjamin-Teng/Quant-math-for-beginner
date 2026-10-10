# Volume I — Calculus for Finance: module briefs

Scope boundaries matter: each brief lists what the module owns and what it leaves to others. LM3 (Taylor series,
volatility drag, leveraged ETFs, duration–convexity) is written; do not repeat its results, link to them with [[LM3]].

Shared data already verified in the repo: `data/raw/0050__*.csv`, `00631L__*.csv`, `0050_dividends.csv`
(2014-10-31 → 2026-10-08) and `data/processed/etf_daily_returns.parquet` (run `uv run python data/build_series.py`).
New data for this volume: `data/raw/00679B__*.csv` (+ dividends) for LM7; TX futures and TAIEX around the 2025
dividend season for LM6.

---

## LM1 Exponentials, Logarithms and Compounding

**Prereq:** none. **Leads:** 3, 6, 19, 29.
**Owns:** laws of exponents/logs; change of base; log scale charts; compounding frequency, EAR, the limit
$(1+r/n)^n\to e^r$ and the definition of $e$; holding-period and annualized returns; continuously compounded
returns and their additivity over time; time-to-goal and rate-to-goal problems; drawdown recovery arithmetic.
**Leaves:** series expansions and error bounds (LM3), arithmetic vs geometric mean and volatility drag (LM3/LM19),
present values (LM6).
**Motivating case:** one investment, three numbers — 0050 from 2014-10-31 to 2026-10-08: total return +902%,
annualized (geometric) 21.3%, continuously compounded 19.3% a year (log growth 2.305). Which one should you quote, and
how do they convert? Resolve by the end of section 4.
**Sections (suggested):** 1 Introduction · 2 Exponents and logarithms (laws, change of base, why log-scale charts:
0050 on linear vs log axis) · 3 Compounding frequency and the number e (periodic rate, EAR, continuous limit,
derivation of e as a limit, EAR $=e^{r}-1$) · 4 Holding-period, annualized and continuously compounded returns
(conversions, annualizing across different horizons, 252 vs 365 conventions) · 5 Adding returns across time and
across assets (aggregation rules; why averaging log returns across assets is wrong) · 6 Solving growth equations
with logarithms (doubling, target wealth, required CAGR, drawdown recovery: −50% needs +100%; use 0050's
2024-08-05 and 2025-04-07 drawdowns and the days to recover) · 7 In Python (Polars return pipeline).
**Widget:** compounding explorer (rate slider, frequency 1/2/4/12/52/365/∞) showing EAR converging to $e^r-1$.
**Examples (ideas):** Taiwan bank deposit APR vs EAR; credit-card revolving rate with daily compounding; converting a
90-day return to annual; 0050 three-number case; required CAGR for a retirement target; recovery time from a
drawdown.
**Lab:** return conversions and annualization on 0050; compounding table; drawdown and recovery statistics.

## LM2 Limits and Derivatives

**Prereq:** 1. **Leads:** 3, 4, 7, 31.
**Owns:** limits and continuity (including the derivative as a limit and $\lim (1+1/n)^n$ revisited briefly),
differentiation rules (power, exponential, logarithmic, product, quotient, chain), derivatives as marginal rates,
sensitivities and elasticities, differentials and the linear approximation, numerical differentiation.
**Leaves:** second-order approximations and convexity (LM3), optimization (LM4).
**Motivating case:** "Why does a 1% move in TAIEX move a futures account by 5–8%?" — equity elasticity of a TX
position equals its leverage $f$. Use real TX settlement levels (from the LM6 data) and an *illustrative* margin
that is clearly labelled as illustrative (TAIFEX margins change; do not state current values as fact).
**Sections (suggested):** 1 Introduction · 2 Limits and continuity · 3 The derivative (definition, rules, proofs of
the rules that matter: $d e^x$, $d\ln x$, chain rule) · 4 Derivatives as sensitivities (delta of a futures position
NT\$200 per point; modified duration as $-P'/P$ for a bond — first order only, link [[LM3]] for convexity; PV
sensitivity to rate) · 5 Elasticity and leverage (elasticity of equity to the index = $f$; FX-hedged vs unhedged
return of a TWD investor in a USD asset via chain rule) · 6 Differentials and when linear approximation fails
(preview; link LM3) · 7 Numerical derivatives (forward/central differences, step-size trade-off, rounding error) ·
8 In Python (finite differences, sympy check).
**Widget:** secant-to-tangent explorer (h slider) for a chosen function, showing the difference quotient converging.
**Lab:** finite-difference experiments (error vs h on a log–log plot), duration by bumping yields, elasticity of a
levered position from 0050 data.

## LM4 Optimization in One Variable

**Prereq:** 2, 3. **Leads:** 7, 20, 41, 42.
**Owns:** critical points, first- and second-order conditions, concavity/convexity and global optima, corner
solutions on intervals (leverage caps, long-only), root finding (bisection, Newton) for equations without closed
form, sensitivity of optima (flat tops; envelope theorem in one variable), the binary Kelly bet derived as a
one-variable optimization.
**Leaves:** continuous-time Kelly and Itô (LM42), multi-asset (LM43), estimation error in $\mu$ (LM20, LM45).
**Motivating case:** "In-sample, full Kelly on 0050 says about 5–6× leverage." Maximize the sample mean of
$\ln(1+fR_t)$ over 0050's daily returns (compute it; the quadratic approximation is $f\approx\mu/\sigma^2$). Show the
growth curve, the half-Kelly point (≈ 75% of maximal growth at half the volatility) and why the number must not be
used as is (sampling error in $\mu$, forward references to [[LM20]] and [[LM45]]). Keep the "Sharpe 3 → full Kelly"
warning.
**Sections (suggested):** 1 Introduction · 2 First- and second-order conditions · 3 Concavity, convexity and global
optima · 4 Constraints on an interval: corners (margin cap, long-only) · 5 The binary Kelly bet ($f^*=p/L-q/G$,
position size vs risk size, sensitivity to $p$) · 6 Root finding: bisection and Newton (IRR/YTM, empirical Kelly
first-order condition $\mathbb{E}[R/(1+fR)]=0$, convergence rates) · 7 How sensitive is the optimum? (flat tops,
growth lost at $f=\lambda f^*$ is $(1-(1-\lambda)^2)$ of the maximum in the quadratic case) · 8 In Python
(`scipy.optimize`).
**Widget:** binary Kelly growth curve $g(f)$ with sliders $p$, $G$, $L$; marks $f^*$, half-Kelly and the zero-growth
point.
**Lab:** empirical Kelly on 0050 (full sample and rolling windows), Newton vs bisection iteration counts, YTM solver.

## LM5 Integration

**Prereq:** 1, 2. **Leads:** 14, 15, 17, 18.
**Owns:** definite integral as accumulation and area, Riemann sums, fundamental theorem of calculus, substitution,
integration by parts, improper integrals and convergence, the Gaussian integral, continuous discounting and the PV of
continuous cash flows, numerical integration (trapezoid, Simpson) with error orders, expectation as an integral of a
density (preview of LM14 — define only what is needed).
**Leaves:** probability axioms and random variables (LM13–14), distributions in depth (LM15), Monte Carlo (LM18).
**Motivating case:** "How often should a −5% day happen?" A normal model fitted to 0050's daily returns gives
$P(R\le-5\%)$ as an integral of the density (≈ $\Phi(-4.1)$, a fraction of a day in 12 years); the data contain
several such days (count them exactly, list the dates). The gap is the integral of the tail — and the reason tails
need their own models ([[LM15]]).
**Sections (suggested):** 1 Introduction · 2 Accumulation and area (Riemann sums) · 3 The fundamental theorem of
calculus · 4 Techniques: substitution and integration by parts · 5 Improper integrals and the Gaussian integral
(with polar-coordinates proof in a Deep Dive; tails that make moments infinite) · 6 Continuous discounting and
continuous cash flows · 7 Densities and expectations as integrals (normal tail probability vs empirical frequency)
· 8 Numerical integration (trapezoid $O(h^2)$, Simpson $O(h^4)$) · 9 In Python (`scipy.integrate`).
**Widget:** tail-probability explorer: threshold slider; normal tail area vs empirical frequency of 0050 daily
returns, with a shaded density.
**Lab:** Riemann/trapezoid/Simpson convergence, normal fit vs empirical tails on 0050, continuous annuity PV.

## LM6 Sequences, Series and the Time Value of Money

**Prereq:** 1. **Leads:** 3, 7, 25, 31.
**Owns:** arithmetic and geometric sequences, finite and infinite geometric sums, PV/FV, annuities (ordinary and due),
perpetuities, growing annuities and perpetuities, loan amortization, bond pricing and YTM (numerically — link
[[LM4]] for Newton), dividend discount and Gordon growth models with implied required return and implied growth,
cash-flow additivity and no-arbitrage: implied forward rates, forward FX, and index futures fair value
$F=Se^{(r-q)T}$.
**Leaves:** duration and convexity (LM2/LM3), term-structure modelling, options (LM31).
**Motivating case:** "Why does TX trade below TAIEX every summer?" — use near-month TX settlement vs TAIEX close in
May–September 2025; the discount (逆價差) widens before the ex-dividend season. Fair value $F=Se^{(r-q)T}$ turns
the basis into an implied dividend yield; compare it with a plausible range. Connects directly to futures–spot
basis trading.
**Sections (suggested):** 1 Introduction · 2 Sequences and geometric series · 3 Present value, future value and
annuities · 4 Perpetuities and growth (Gordon model, 0050's implied required return from its dividends) · 5 Bond
pricing and yield to maturity · 6 Loans and amortization (Taiwan mortgage example; clearly labelled illustrative
rate) · 7 Cash-flow additivity and no-arbitrage (implied forwards, forward FX, index futures fair value and the TX
basis) · 8 In Python.
**Widget:** loan/annuity explorer (rate, years, principal) with an amortization chart of interest vs principal, or a
basis explorer (r, q, T) — choose one.
**Lab:** TVM functions, bond price–yield and YTM solver, Gordon implied return for 0050, TX basis and implied
dividend yield through the 2025 season.

## LM7 Multivariable Calculus and Lagrange Multipliers

**Prereq:** 2, 3, 4. **Leads:** 10, 32, 33, 43.
**Owns:** functions of several variables, partial derivatives, gradient, Hessian, multivariate Taylor to second
order, unconstrained optima and the 2×2 definiteness test, Lagrange multipliers and the multiplier as shadow price,
KKT conditions for simple inequality constraints, gradient-based numerical optimization; two-asset minimum-variance
weights, two-asset tangency weights and the two-asset Kelly fraction by calculus.
**Leaves:** matrix notation and $N$ assets (Vol II and LM32–33), estimation error (LM35).
**Motivating case:** "0050 plus a US Treasury ETF: how much bond minimizes risk?" — 00679B (元大美債20年, TWD) and
0050 daily total returns since 2017: volatilities, correlation (and its regime change in 2022, when both fell), the
calculus-derived minimum-variance weight, its in-sample vs out-of-sample volatility. State clearly that 00679B returns
include USD/TWD moves.
**Sections (suggested):** 1 Introduction · 2 Functions of several variables and partial derivatives · 3 Gradient,
Hessian and the multivariate Taylor expansion · 4 Unconstrained optimization in two variables · 5 Equality
constraints: Lagrange multipliers · 6 Two-asset portfolios by calculus (min variance, tangency, Kelly fraction
$f^*=\Sigma^{-1}(\mu-r_f\mathbf 1)$ in the 2×2 case) · 7 Inequality constraints: KKT for long-only and leverage caps ·
8 In Python (numerical gradients, `scipy.optimize.minimize`).
**Widget:** two-asset explorer: correlation and weight sliders; portfolio volatility curve with the minimum-variance
point.
**Lab:** 0050/00679B statistics by year, rolling correlation, min-variance weights in and out of sample, a
Lagrangian solved symbolically and numerically.
