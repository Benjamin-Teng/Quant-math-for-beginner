# Volume II — Linear Algebra for Portfolios: module briefs

Volume II turns the two-asset calculus of LM7 into the linear algebra of $N$ assets. A portfolio is a vector, a book
of returns is a matrix, risk is a quadratic form, and the structure of a covariance matrix is its eigenvectors. The
volume teaches the tools; portfolio theory built on them waits for Volume V (ROADMAP, "Module boundaries").

The reader reads English as a second language and wants the tools learned systematically, not a lot of material
(SPEC §2). So worked examples, diagrams and formulas carry each module, and the prose connects them. Each brief lists
what its module owns and what it leaves to others; LM7 is written, so link to its two-asset results with [[LM7]]
instead of repeating them.

## Shared decisions

- **Length and voice.** AUTHORING §1: at most 6,000 words of prose and 36 pages; first drafts under 5,500 words;
  sentences average under 16 words and never exceed 30; paragraphs at most 80 words; connectors kept.
  `uv run python build/qa/style.py src/lmNN.md` must show no FAIL before a draft is handed back.
- **Section pattern.** A small numeric case (2×2 or 3×3) or a diagram first, then the definition or theorem with all
  its conditions, a short derivation, a worked example, at most one pitfall, the 中文導讀 and the knowledge check.
- **Matrices on the page.** Matrices go in displays, never inline beyond a pair of entries. An $N\times N$ matrix is
  written with $\cdots$ or by blocks, and a display wider than the page is broken with `aligned` (PITFALLS §4).
  Numerical matrices larger than 3×3 go in exhibit tables or heatmaps.
- **Notation.** AUTHORING §6, including its table for vectors and matrices; every local symbol in the notation note.
- **Python.** NumPy for linear algebra: `@`, `np.linalg.solve` (never `inv` to solve a system), `eigh` for symmetric
  matrices, `cholesky`, `svd`, `lstsq`, `matrix_rank`, `cond`; `np.cov(..., rowvar=False, ddof=0)` or
  `Xc.T @ Xc / T`; Polars for data; print shapes when they matter.
- **Python facts** (checked 2026-10-11 on the NumPy 2.5, Polars and SciPy references; `project/SOURCES.md`). `np.cov`
  treats rows as variables and divides by $T-1$ unless `ddof=0`; `np.var` and `np.std` divide by $T$; Polars' `var`,
  `std` and `pl.cov` divide by $T-1$ unless `ddof=0`, `pl.corr` has no `ddof`, and Polars has no `DataFrame.cov`.
  `eigh` returns eigenvalues in ascending order; `svd` returns singular values in descending order and $V^{\top}$ as
  `Vh`; `np.linalg.cholesky` returns the lower factor, `scipy.linalg.cholesky` the upper one. `matrix_rank` and `lstsq`
  treat singular values below about $s_1\max(M,N)\,\varepsilon$ as zero; `pinv` uses $10^{-15}s_1$. `solve` calls
  LAPACK's `gesv` (LU with partial pivoting, per LAPACK's DGESV documentation); it raises `LinAlgError` when a pivot is exactly zero or the matrix is not
  square, so a matrix that is singular only in exact arithmetic can pass (LM9).
- **References.** Cite the entries verified in `project/SOURCES.md` ("Papers and books"): Strang 2016 for the core
  results; Golub and Van Loan 2013 and Higham 2002a for numerical methods; Horn and Johnson 2013, ch. 7, for tests of
  positive (semi)definiteness; Higham 2002b and Rousseeuw and Molenberghs 1993 for repairing an indefinite correlation
  matrix; Strang and Herman 2016 (OpenStax *Calculus Volume 3*, free online), §4.7, Theorem 4.18, for the extreme
  value theorem. A section or theorem number that SOURCES.md
  does not list is checked before it is printed.
- **Chinese terms.** AUTHORING §1: the 中文導讀 use 樂詞網's terms (terms.naer.edu.tw), mathematics or statistics
  listing, with the English term in parentheses at first use in each box. Volume II's terms: 特徵值、特徵向量
  (統計學名詞; the mathematics listing has 固有值、固有向量), 二次形式, 正定, 半正定, 主子式, 行列式, 秩, 條件數,
  高斯消去法, 克拉瑪法則, 奇異值分解, 主成分分析, 最小平方法, Cholesky 分解, 正交投影, 擬反矩陣 (Moore–Penrose 反矩陣),
  譜分解, 內積, Cauchy–Schwarz 不等式. Settled in review (2026-10-11): pivot 樞軸元 (LM9's term), upper and lower
  triangular matrix 上三角矩陣, 下三角矩陣, out-of-sample test 樣本外檢定, Euclidean norm 歐氏範數, dot product 內積,
  Hessian 海森矩陣 (LM7's form). 樂詞網 has no mathematics or statistics entry for column space, whitening,
  projection matrix or pairwise deletion, and lists null space as 零核空間 in mathematics and 零空間 in engineering:
  write 行空間, 白化, 投影矩陣, 按配對刪除 (its sociology entry) and 零空間, each with its English term. A row is 列 and a column is 行.
- **Data.** Daily closes of TAIEX and the TWSE sector indices from `data/vol2_series.py` (repaired from the 13:30:00
  closes, see `data/README.md`), 2007-07-02 → 2026-10-08, and Volume I's 0050, 00631L, 00679B and TX files. Sector
  indices are price indices; `Electronic` covers its eight electronics sub-industries; TradingConsumersGoods is complete
  only from 2008-12-01. Every number comes from the module's scripts, which assert from the first draft that each
  printed value appears in the text and follows from the printed inputs.
- **Universe and sample.** Sector analyses use **U28**, the 28 leaf indices among the 30 TWSE sector indices that FinMind serves
  daily (all except the aggregates `Electronic` and `ChemicalBiotechnologyMedicalCare`; TWSE's four sector indices of
  30 June 2023 have no daily series there, so from July 2023 some TAIEX members lie outside U28), on one common sample of daily simple returns from
  2008-12-01 to 2026-10-08; using every leaf avoids choosing sectors by hand. Hand-sized examples use **S3**
  (Semiconductor, FinancialInsurance, Food) and **S5** (S3 plus Plastics and ShippingTransportation) on the same
  sample. Year-by-year results use the full calendar years 2009–2025 and 2026 to date. Never mix samples within a
  module: $A$, $T$ and every moment come from the sample the text names.
- **Research hygiene.** The site's Research hygiene page (TODO, Stage 1 item 7) and each module's declaration below.
  A full-sample covariance matrix describes the past; it is not a forecast. Comparing two halves of the sample is a
  stability check, not an out-of-sample test.
- **Charts.** `line`, `bar`, `heatmap`, `scatter` and `vector` (AUTHORING §7); at most four series; every value the
  text cites is plotted or printed in a cell.
- **Labs.** One per module, generated by `build/make_labNN.py`, reading only its own `data/` folder, which
  `data/make_lab_data.py` builds (LM8–LM12 are registered there).
  - *Sector files* (every Volume II lab). `sectors_close_raw.csv`: `date`, then `TAIEX` and the 30 sector ids, the
    closes FinMind serves, empty where a series has no close. `sectors_close_repairs.csv`: `id`, `date`, `close_1330`,
    one row for each of the 561 closes that `data/vol2_series.py` repairs (listed from the manifest), with the 13:30:00
    value. Read both with `infer_schema_length=None` and `schema_overrides={"close_1330": pl.Float64}`, because
    `close_1330` can be entirely empty.
  - *Repair cell.* It replaces each listed close with `close_1330` and prints the rule, how many listed closes it
    replaced and how many it dropped (561 and 0 on a paid plan, 0 and 561 on the free plan), and how many fall in the
    module's sample (U28 from 2008-12-01: 524 closes on 38 dates). With every value present, the result equals
    `vol2_closes.parquet` cell for cell. On FinMind's free plan `close_1330` is empty, because
    `data/raw/sectors_close/` comes from a paid dataset, and the cell drops those closes. Returns stay between
    consecutive TAIEX-calendar dates, so a dropped close removes the returns into and out of its date: U28's sample
    then keeps $T=4{,}307$ of 4,382 returns ($A=241.28$). Only numbers computed inside a window without a listed
    close keep their values: 7–10 April 2025, December 2008, the last 250 returns and the calendar years 2014, 2023,
    2024 and 2026. A number that also uses the full sample ($A$, or the full-sample eigenvectors behind LM11's per-year
    cosines and plane measure) changes with it. The
    lab says which of its printed numbers change (Getting Started, "Fetch the data").
  - *ETF files* (LM8, LM10, LM11). `0050_daily_raw.csv`, `00631L_daily_raw.csv` and `00679B_daily_raw.csv` (`date`,
    `close`, `spread`); `0050_dividends.csv` and `00679B_dividends.csv` (`date`, `before_price`, `after_price`,
    `cash_dividend`, from `TaiwanStockDividendResult`; 0050's first row, 2014-10-24, precedes its first close). A total
    return is $R_t=(P_t+D_t)/(P_{t-1}/s_t)-1$: $D_t$ is the cash dividend of every row of the dividends file, including
    00679B's 2019-03-05 and 2025-08-21, whose close did not change, and $s_t$ is 4 for 0050 on 2025-06-18, 22 for
    00631L on 2026-03-31 and 1 otherwise. LM1's frame (0050 and 00631L on their common dates, $T=2{,}902$, as
    `etf_daily_returns.parquet`) and LM7's frame (each fund's total-return index on its own dates, returns between consecutive common dates from
    2017-01-17, $T=2{,}363$, as `lm07_returns.parquet`) are rebuilt as the LM1 and LM7 labs do, and serve only statistics of the pair they join
    (PITFALLS §3). Where an ETF meets sector returns (LM10), it uses one-session returns: between consecutive
    TAIEX-calendar dates on which it has both closes, so a return that spans a halt drops out.
  - *TX file* (LM8). `TX__2025-04-01__2025-10-31.csv`: `date`, `contract_date` (yyyymm, an integer), `close`,
    `settlement_price`, `volume`, `open_interest`, one row per listed contract month (six a day). Keep
    `contract_date == 202504`, whose `settlement_price` prints 0.0 on its last day, 2025-04-16 (PITFALLS §3).

## Editor's decisions on the drafts (2026-10-11)

The module briefs below were drafted from two alternative designs per module; these decisions settle the points the
drafts left open. Every number they quote is listed, with its definition, in `plans/vol-2-anchors.md`.

- **Notation.** A vector of a book-wide capital quantity keeps its letter in bold capitals: $\mathbf R_t$ (returns)
  and $\mathbf P_t$ (prices) (AUTHORING §6). Column $j$ of a matrix $M$ is $\mathbf m_j$, so LM8 writes the columns of
  $X$ as $\mathbf x_j$; LM9, whose unknown is $\mathbf x$, does not use them. Perturbations are $\Delta M$ and
  $\Delta\mathbf x$ (LM11); $\delta$ is LM12's rank tolerance. The spectral norm is $\lVert M\rVert_2$. The SVD of
  data is taken of $\tilde X/\sqrt T$, so that $\lambda_k=s_k^2$; LM11 cites LM12 that way. LM9's null vectors keep the
  echelon scaling (free variable 1); the sign rule of AUTHORING §6 is for eigenvectors.
- **LM8.** One `angles` exhibit, whose note gives each bar's return type and sample. LM7's line 57 gains [[LM8]] when
  Volume II is published (TODO, Stage 4).
- **LM9.** The case shows four exact fits that disagree (7–9 April and the other triples). Electronic is the one named
  exception outside U28 (§7). TX and MTX stay a contract-terms example with illustrative point moves.
- **LM10.** Problem 6 asks for pivots only. The real pairwise-deletion case keeps the three ETFs, the only series that
  start on different dates, with one sentence on price versus total returns. Its pairwise correlation matrix is
  positive definite, but its pairwise covariance matrix is not positive semidefinite (smallest eigenvalue −6.56e-06):
  each variance uses a series' whole sample, each covariance with an ETF only the ETF's dates. §6 shows this real
  failure next to E9's constructed one.
- **LM11.** 0050/00631L's $\kappa(C)=77.0$ is the real near-collinear pair, on LM8's sample: LM1's total returns on
  their 2,902 common dates ($\rho=0.974365$). The plane measure is a formula in cosines of orthonormal vectors, not
  LM12's projection; it places the compared period's $\mathbf q_2$ against the reference period's $\mathbf q_2$ and
  $\mathbf q_3$ (the first half; the full sample for a year). It is one-sided: it shows where $\mathbf q_2$ went, not
  that the plane holds. In U28's halves the two planes lie 21.9° and 64.2° apart, the second half's $\mathbf q_2$ is
  mostly the first half's $\mathbf q_3$ (0.879), and the components beyond the first change places (review of
  2026-10-11, reviews/lm11.md, finding 1).
- **LM12.** Electronic stays in §5 and in the `cond` exhibit; December 2008 stays as the rank-deficient sub-sample.
- **Before any draft** (done 2026-10-11). An independent recomputation checked every number in
  `plans/vol-2-anchors.md` (each module's status line there records its result and the corrections), and a second
  recomputation confirmed every corrected or added number. All 640 comparisons with the 13:30:00 values match, including GlassCeramic's largest moves (so its high
  volatility is not a copying artefact) and S5's returns on 2026-07-31 and 2026-07-17. The facts once marked "to
  verify" were checked on official pages, software references and bibliographic records (`project/SOURCES.md`).

## LM8 Vectors and Matrices

**Prereq** `[1, 2, 3, 7]`: LM1 (simple returns add across assets, (1.13); log returns do not, (1.14)); LM2 (TX at
NT\$200 a point, futures P&L); LM3 (sample moments, divisor $T$); LM7 (vectors, $^{\top}$, two-asset correlation;
Cauchy–Schwarz "without proof; [[LM8]]", line 75). **Leads** `[9, 10, 11, 12, 16, 23, 27, 31, 35]`.

**Owns.** Vectors with a shape, a unit per entry and an index (asset order; a date for $\mathbf P_t$, $\mathbf R_t$), as
arrows and as lists; addition, scalar multiples, linear combinations. The dot product as P&L, $\Delta W=\mathbf h^{\top}
\Delta\mathbf P$, and as portfolio return, $R_p=\mathbf w^{\top}\mathbf R$ (simple returns only); the one-period identity
$\mathbf h^{\top}\Delta\mathbf P=W_0\mathbf f^{\top}\mathbf R$. Norm, distance, unit vectors; 1-norm as gross exposure,
$\mathbf 1^{\top}\mathbf f$ as net. Angle; Cauchy–Schwarz **with proof** and equality case, also in LM7's sum form;
triangle inequality; orthogonality. Sample correlation as the cosine of centred vectors; two vectors drawn exactly in
their own plane; standardized distance $2T(1-\rho)$; $s_p\le\sum_iw_is_i$ for $w_i\ge0$. Matrices as data: $X$, rows,
columns, $X\mathbf w$ (row view first, in LM7 line 483's words, then column view), $Y\mathbf h$; transpose; matrix
product, associativity, $MK\ne KM$, $(MK)^{\top}=K^{\top}M^{\top}$; $I$. Sample facts only.

**Leaves.** Span, rank, $M\mathbf x=\mathbf b$, inverse, Cramer (LM9) · $\tilde X$ as an object, $\hat\Sigma$,
$\mathbf w^{\top}\hat\Sigma\mathbf w$, $C$, positive semidefiniteness (LM10) · eigenvectors, condition number (LM11) ·
projections, least squares, SVD, Cholesky (LM12) · population correlation (LM16) · a correlation's sampling error
(LM19–LM20) · regression hedge ratios (LM23) · trades, risk decomposition (LM27) · clustering (LM31) · shocks (LM35).

**Uses before taught** (one sentence and a pointer each). Covariance matrix, §7: "The dot products of all centred
columns form a square table $\tilde X^{\top}\tilde X$; [[LM10]] divides it by $T$ and calls it the sample covariance
matrix." Inverse, §7: "$I$ plays the role of 1; dividing by a matrix means multiplying by its inverse, which exists only
sometimes ([[LM9]])." Projection, §4: the minimizing $a\mathbf y$ "is the projection of $\mathbf x$ on $\mathbf y$
([[LM12]])." Hedge ratio, §2: by notional here; by regression in [[LM12]], [[LM23]]. Population correlation, §5:
orthogonal centred vectors describe these dates, not "no relation" ([[LM16]]). Price limits and daily settlement, §2:
one sentence each, citing TAIFEX and TWSE. TX's limit is ±10% of the previous regular session's daily settlement price
and its tick is one point; 21,296 × 0.9 = 19,166.4 is off the tick, and TX traded and settled at 19,167, a rounding
that the data show and TAIFEX's pages do not state. The daily settlement is the volume-weighted price of the last
minute's trades; TAIFEX has no special rule for a locked market. Daily rebalancing, §6: LM3 and LM7 assumed it; $X\mathbf w$ shows it.

**Data role.** (1) Case: TX 202504 `settlement_price` (`raw/TX__2025-04-01__2025-10-31.csv`, expiry 16 Apr, no roll),
0050 and 00679B unadjusted closes, sessions 2, 7, 8, 9, 10, 11 April 2025. No ex-date in the window (0050: 2025-01-17,
2025-07-21; 00679B: 2025-02-21, 2025-05-22) and 0050's split (2025-06-18) is later, so price changes are total changes.
(2) ETF pairs, total returns, LM7 and Volume I samples: 0050/00679B (`processed/lm07_returns.parquet`, $T=2{,}363$,
2017-01-18 → 2026-10-08), 0050/00631L (`processed/etf_daily_returns.parquet`, $T=2{,}902$, from 2014-11-03).
(3) Sector pairs on **U28** (the 30 TWSE sector ids minus `Electronic` and `ChemicalBiotechnologyMedicalCare`), closes
2008-12-01 → 2026-10-08 from `processed/vol2_closes.parquet` (repaired; run `data/vol2_series.py` if missing), simple
price returns, $T=4{,}382$, no gaps; S3 (Semiconductor, FinancialInsurance, Food) for hand work. No per-year results;
no cleaning beyond the builders.

**Hygiene declaration.** The case is exact accounting. Every angle and correlation is **Descriptive** (whole stated
sample); five-session cosines are called noise beside full-sample values. The `angles` note gives each bar's return type
and sample. No fit, stability check or out-of-sample claim.

**Notation** (local; checked against AUTHORING §6). $\mathbf h$ holdings (shares; TX contracts): bold, and LM8 has no
generic function $h$; not $\mathbf q$ (eigenvectors). $\mathbf P_t$ prices in NT\$ per unit (TX: $200F_t$),
$\Delta\mathbf P_t:=\mathbf P_t-\mathbf P_{t-1}$; $F_t$ TX settlement in points; $W_0$, $\Delta W_t$ equity, P&L of date
$t$. $Y$ the $T\times N$ price-change matrix, row $t$ equal to $\Delta\mathbf P_t^{\top}$ (LM8 has no yields or
regressions). $\mathbf x_j$ column $j$ of $X$; $\mathbf x,\mathbf y$ generic vectors ($\mathbf y$ is a response only from
LM12); $a$ a generic scalar (no bets in LM8; not $\alpha$, which LM23 takes). $\tilde{\mathbf x}:=\mathbf x-\bar
x\mathbf 1$, $\bar x$ mean of entries; $\lVert\mathbf x\rVert_1:=\sum_k\lvert x_k\rvert$; $\mathbf u$ unit vector;
$\rho$, $s$, $s_p$ sample correlation, standard deviation (divisor $T$), that of $X\mathbf w$. No $\mathbf v$ ($v$
discounts): values are $W_0f_i$. Counts: $N$ assets, $T$ returns (never a horizon), $m$ portfolios; $i,j$ assets, $t$
dates, $k$ entries. The rest ($\mathbf w$, $\mathbf f$, $X$, $\mathbf e_i$, $\theta$, …) as in §6; $\mathbf x\cdot\mathbf y$
is said once to equal $\mathbf x^{\top}\mathbf y$. No eigenvectors, so no sign rule.

**Motivating case — "7 April 2025: two limit-downs and a bond that rose"** (box ≤ 130 words). At the 2 April close a
trader holds $\mathbf h=(-1,\ 24{,}000,\ 100{,}000)^{\top}$ (short one TX April contract; 0050; 00679B), $W_0=$ NT\$10m;
the short future roughly offsets the 0050 notional. Taiwan reopened Monday 7 April after Qingming; TX and 0050 closed
limit-down, 00679B rose. Asks: (1) the day's P&L and which line made it (§2); (2) why the "hedged" book still lost
NT\$124,200 over the week (§7); (3) how alike the series are, on the week and over a decade (§5). Anchors
(`vol2_anchors.txt` 447–456, 4, 465): TX 21,296 → 19,167 (volume 66,423 → 2,736), 0050 176.00 → 158.40, −9.997183% and
−10.000000%, TAIEX −9.699731%, the sample's largest move. New: 00679B 29.88 → 30.42; lines +425,800, −422,400, +54,000.

**Sections** (prose words; total 5,300).

| # | Title | Words | Content |
|:--|:--|--:|:--|
| — | Introduction | 330 | framing; `[!case]`; `case`; roadmap; notation note |
| 1 | Vectors: Holdings, Prices, Weights and Returns | 470 | `arrow` first; shape, units, index; columns; addition needs same order, units, date; linear combination, $\sum_jw_j\mathbf x_j$. Ex 1. Pitfall: different asset order or dates (inner join). KC |
| 2 | The Dot Product: P&L and Portfolio Return | 620 | (8.1); (8.2) with units; (8.3) from LM1 (1.13), not log returns; (8.4); symmetry, linearity. Ex 2–3 resolve Q1. Pitfall: on a limit-down day sell orders queue while buy orders fill at once, so the short TX line could close at 19,167 but the long 0050 line could not be sold at 158.40: the book's P&L is a valuation, not cash. 中文導讀. KC |
| 3 | Length, Distance and Exposure | 400 | (8.5), distance, unit vectors, 1-norm; net vs gross. Ex 4. Pitfall: net ≠ gross (PITFALLS §7). KC |
| 4 | Angles, the Cauchy–Schwarz Inequality and Orthogonality | 580 | (8.6) with equality case; proof as a display chain, $\lVert\mathbf x-a\mathbf y\rVert^2\ge0$ at $a=\mathbf x^{\top}\mathbf y/\lVert\mathbf y\rVert^2$ ($\mathbf y=\mathbf 0$ separate); LM7's sum form; (8.7); (8.8) in two lines; dollar-neutral ⟂ $\mathbf 1$. Ex 5. 中文導讀. KC |
| 5 | Correlation as a Cosine | 580 | centring; (8.9); divisor and annualization cancel; own plane, lengths $\sqrt T s$ (`plane`); (8.10); (8.11), equality only at $\theta=0$. Ex 6–7. Pitfall: uncentred cosine ≠ correlation. Resolves Q3 (`angles`). KC |
| 6 | Matrices as Data | 500 | $X$, $x_{tj}$, rows $\mathbf R_t^{\top}$, columns; transpose; (8.12) row then column view; $X\mathbf w$ rebalances daily; (8.13) $Y\mathbf h$ a fixed book. Ex 8. Pitfall: exposures of a fixed book drift. 中文導讀. KC |
| 7 | Matrix Multiplication, Transpose and Identity | 480 | shape rule; (8.14); $XK$; associativity, $MK\ne KM$, (8.15) proved; $I$; $\mathbf 1^{\top}Y\mathbf h$ exact, $\mathbf 1^{\top}X\mathbf w$ no period return. Ex 9 resolves Q2. Python box (`@`, `.T`, shapes). KC |
| — | Summary / Problems / Solutions | 150 / 420 / 770 | eight bullets; 11 problems; short solutions |

**Exhibits** (9). `case` (Intro, table): instrument, unit, $h_i$, prices 2 and 7 Apr, $\Delta P_i$, $h_i\Delta P_i$,
total, TX volume. `arrow` (§1, vector): $\mathbf w=(0.6,0.4)^{\top}$ with $\mathbf e_1$, $\mathbf e_2$ and dashed
components. `pnl-lines` (§2, bar, three series, hline 0): daily P&L per line, 7–11 Apr. `balls` (§3, vector): unit circle
(ellipse, cov $I$), 1-norm diamond (segments), point $(f_{\text{TX}},f_{0050})$. `cs-proof` (§4, vector): $\mathbf x$,
$\mathbf y$, $a^*\mathbf y$, dashed $\mathbf x-a^*\mathbf y$, $\theta$. `angles` (§5, bar, hline 90°, $\rho$ as labels):
0050/00631L 13.0°, ElectronicPartsComponents/ComputerPeripheralEquipment 41.0° (U28 maximum of 378 pairs),
Semiconductor/FinancialInsurance 54.9°, Semiconductor/Food 66.2°, BiotechnologyMedicalCare/OilGasElectricity 77.4° (U28
minimum), 0050/00679B 96.1°. `plane` (§5, vector): centred 0050 and 00679B as arrows of length $s\sqrt A$ (20.11%,
13.50%) at 96.06°, the 42.3/57.7 mix (10.91%, with $w=0.423$ as printed), parallelogram dashed. `week` (§6, heatmap, dates × instruments, pct1,
±0.10): the $5\times3$ $X$; note says row 1 spans 3–6 April. `xk` (§7, table): $XK$ for 100% 0050, 60/40 and 50/50
0050/00679B, sums and compounded week.

**Widget `bookPnl`.** Sliders: TX −3…+3; 0050 0…60,000 (step 1,000); 00679B 0…300,000 (step 10,000). Bar chart of
$Y\mathbf h$ (colour by sign); prints 7 Apr P&L, $\mathbf 1^{\top}Y\mathbf h$, net and gross exposure on 2 Apr. Embeds
the 15 derived price changes. Initial state the case book (+57,400, −124,200).

**Examples** (9). (1) Shapes, units, index of $\mathbf h$, $\mathbf P$, $\mathbf f$, $\mathbf R$; a combined book as a
linear combination. (2) 7 Apr P&L by line, +57,400. (3) Same via $W_0\mathbf f^{\top}\mathbf R$, 0.574%. (4) Net 0.29528,
gross 1.14712; distance 0.1414 between 60/40 and 50/50. (5) Angle and Cauchy–Schwarz on two small vectors; a
dollar-neutral pair ⟂ $\mathbf 1$. (6) Week correlation 0050/00679B by hand, +0.2526 (75.4°), uncentred 0.2930, against
−0.1056 (96.1°) in full. (7) (8.11) with LM7's mix: 10.91% against 16.29%. (8) $X\mathbf w$ for 60/40 over the week:
sum −5.98%, compounded −6.32%. (9) $Y\mathbf h$, $\mathbf 1^{\top}Y\mathbf h=-124{,}200$, $XK$ for three portfolios.

**Problems** (11; MC keys B, C, A; one Python). 1 MC **B** (§1–2): valid portfolio return — A $\mathbf w^{\top}\mathbf r$
(log), **B** $\mathbf w^{\top}\mathbf R$ (simple), C $\mathbf h+\mathbf w$. 2 (§2): 8 Apr P&L of $(+2,0,200{,}000)$.
3 (§2–3): exposures, net, gross; check (8.4) on 7 Apr. 4 (§3): norms and relative distance of two weight vectors.
5 proof (§4): triangle inequality and its equality case. 6 (§4): angle of two 3-vectors; $a$ with
$\mathbf x-a\mathbf y\perp\mathbf y$. 7 (§5): 4-observation correlation as a cosine; divisor cancels. 8 MC **C** (§5):
$\rho=-0.106$, angle closest to A 84°, B 90°, **C** 96°. 9 (§5): U28 maximum and minimum pairs ($\rho=0.7547$,
$0.2175$): angles and $\sqrt{2(1-\rho)}$. 10 MC **A** (§6–7): exact over the week — **A** summed daily P&Ls of a fixed
book, B summed returns, C $X\mathbf f$. 11 Python (§6–7): join April 2025, $X$, $X\mathbf w$, cosine vs `np.corrcoef`.

**Lab parts** (`labs/LM08_lab/`). 1 inner-join the three instruments; shapes, units. 2 $\mathbf h^{\top}\Delta\mathbf P$
with `Decimal` and float (the −10% tie); simple vs log across assets. 3 net, gross, distances. 4 Cauchy–Schwarz and
angles on data columns (no random numbers). 5 the six `angles` pairs vs `np.corrcoef`, `ddof` invariance, $2T(1-\rho)$,
S3 equal-weight bound (1.0527% vs 1.2721% a day); U28 from the repair cell (rule and counts, "Labs"); the lab reads
nothing outside `data/`. 6 $X$, $Y$, $X\mathbf w$, $Y\mathbf h$, exposure drift. 7 $XK$, $(MK)^{\top}$, $I$, $MK\ne KM$.
8 extension: 00631L against $2\times$0050 (uncentred RMS distance 0.558% a day, norm ratio 1.94).

**Cross-module tags.** (8.1) $\mathbf x^{\top}\mathbf y=\sum_kx_ky_k$: all of Vol II · (8.2)
$\Delta W=\mathbf h^{\top}\Delta\mathbf P$: LM27, LM35 · (8.3) $R_p=\mathbf w^{\top}\mathbf R$: LM10, LM27, LM28 · (8.4)
exposure identity: LM27, LM43 · (8.5) norm, (8.7) $\cos\theta$: LM11, LM12 · (8.6) Cauchy–Schwarz: LM10, LM16 · (8.8)
triangle: LM10, LM27 · (8.9) $\rho=\cos\theta$: LM10, LM16, LM19 · (8.10) $2T(1-\rho)$: LM31 · (8.11) $s_p$ bound: LM27,
LM28 · (8.12) $X\mathbf w$: LM9, LM10, LM12, LM23 · (8.13) $Y\mathbf h$: LM27, LM35 · (8.14), (8.15): LM9–LM12.

**Pitfalls to pre-empt.** Math: $\mathbf y\ne\mathbf 0$ in the proof; equality iff one is a scalar multiple of the other;
angles need non-zero vectors, correlations non-constant series. The uncentred gap hides on long samples
(Semiconductor/FinancialInsurance 0.5758 vs 0.5749), so Ex 6 uses the week. (8.11) needs $w_i\ge0$, else
$\sum_i\lvert w_i\rvert s_i$. $X\mathbf f$ on 8 Apr gives −0.226%, the fixed book −0.328%. NumPy 1-D arrays have no
orientation. Boundary creep ($\tilde X^{\top}\tilde X/T$, projection, "orthogonal = independent"): one sentence and a
link. Data: 176.00 → 158.40 is exactly −10% (`158.4/176.0 - 1` prints −0.09999999999999998,
`(158.4 - 176.0)/176.0` prints −0.09999999999999996): `Decimal`. Limit-locked marks are not
"realized" (TX volume 2,736 on 7 Apr, 2,382 on 10 Apr). Row 1 spans five calendar days. Contract 202504 only to 16 Apr.
Price vs total returns (0050/00679B: −0.1050 from price returns on their own common dates, split day
excluded, $T=2{,}362$, anchors 477; −0.1056 from LM7's total returns): total, as LM7. 0050 after 2025-06-18: new shares.

## LM9 Linear Systems, Inverses and Rank

One system, read four ways (rows, columns, determinant, elimination): which multiples of three sector indices reproduce
TAIEX on chosen days? An exact fit is not an estimate. **Prereq** `[2, 6, 7, 8]` (LM2 §7, TX multiplier; LM6; LM7's
Cramer and $\Sigma^{-1}$ promises; LM8 (8.12)). **Leads** `[10, 11, 12, 23, 27, 28, 43]`. "≈ 2.5 h + lab".

**Owns.** (1) $M\mathbf x=\mathbf b$ by rows (lines, planes) and by columns. (2) Determinant: signed area and volume,
cofactor expansion, row-operation rules, triangular, product rule (stated), $\det M=0$ exactly when columns are
dependent. (3) Cramer for 2×2 and 3×3, from column linearity, and its cost. (4) Gaussian elimination, back
substitution, row swaps, $\det$ from pivots. (5) Inverse: definition, 2×2 formula, Gauss–Jordan, product and transpose
rules, equivalences; solve first in code. (6) Exact rank: independence, column and null space, pivots, row rank =
column rank (Deep Dive), rank–nullity. (7) None, one or infinitely many solutions, $\mathbf x_p+\operatorname{null}M$.
(8) Perfect collinearity: $\operatorname{rank}X<N$ exactly when a non-zero combination of columns is zero on every date.

**Leaves.** Condition number, sensitivity, $\det$ = product of eigenvalues → LM11. Numerical rank, SVD, pseudoinverse,
least squares (four days), the minimum-norm point of a line, Cholesky → LM12. $\hat\Sigma$, its singularity,
semidefiniteness → LM10. Fits over many days, dummy trap → LM23. Bookkeeping → LM27. $\Sigma^{-1}\mathbf 1$ → LM28.
Kelly $\Sigma^{-1}(\boldsymbol\mu-r_f\mathbf 1)$ → LM43. LU by name: not owned (one sentence: `solve` stores it).

**Uses before taught.** *Least squares* (§6): "With more days than sectors there is usually no exact solution;
[[LM12]] finds the multiples that miss by the least." *Regression* (§6): "Fitting over hundreds of days is a regression,
[[LM23]]." *Condition number* (§7, name only): "how strongly a nearly singular matrix magnifies small errors; [[LM11]]."
*Cap-weighted index* (§7): "a sector index weights each stock by its market value, so its weights drift with prices
([[LM27]])." *Floating point* (§7, [[LM2]] §7): "about 16 significant digits, so a determinant that is exactly zero can print as about $10^{-14}$."
*Futures multiplier* (§6, [[LM2]]): TX pays NT\$200 per TAIEX point, MTX NT\$50, on the same index (TAIFEX contract specifications).

**Data role.** Running example: percent returns of TAIEX ($\mathbf b$) and S3 = Semiconductor, FinancialInsurance,
Food (columns) on 7–10 April 2025, from `vol2_closes.parquet`, $100(P_t/P_{t-1}-1)$ on the TAIEX calendar, rounded to
0.01; the rounded values are the inputs and every printed solution is exact for them (no repair on these dates; no input
near a rounding tie). §7: common sample 2008-12-01 → 2026-10-08 ($T=4382$): Semiconductor, Financial and two 50/50 mixes;
the U28 matrix; Electronic with its eight sub-industries, the aggregate U28 leaves out. LM7's printed $\Sigma$ and excess
returns. No new FinMind data. Scripts `data/lm09_numbers.py` (exact rationals), `data/lm09_charts.py`.

**Hygiene declaration.** Square fits are an **in-sample exact fit**: when $\det M\ne0$ they always succeed, so they carry
no evidence. Comparing the four triples is a **stability check**; the 7–9 multiples applied to 10 April are one
illustration, not an out-of-sample test. §7's ranks are **descriptive**. `> [!note] Research hygiene` in §6.

**Notation** (AUTHORING §6). Book-wide: $M\mathbf x=\mathbf b$ (no bets in LM9), $M$, $K$, $m_{ij}$, $^{\top}$,
$M^{-1}$, $\det$, $\operatorname{rank}$, $I_n$, $\mathbf 0$, $\mathbf 1$, $\mathbf e_j$ (LM7's $\mathbf e$ never named;
write $\boldsymbol\mu-r_f\mathbf 1$), $\theta$, $R$; $X$, $T$, $N$ in §7 only; $\Sigma,\sigma_1^2,\sigma_{12},r_f$ in
E6 only. Local: $\mathbf x=(x_1,x_2,x_3)^{\top}$, the **replicating mix** (Semiconductor, Financial, Food), not weights
(they need not sum to 1); $\mathbf m_j$ column $j$ of $M$; $[M\mid\mathbf b]$; $\operatorname{col}M$,
$\operatorname{null}M$, $\dim$; $M_j(\mathbf b)$ (column $j$ replaced, Cramer); $M^{(ij)}$ (row $i$, column $j$
deleted); $\operatorname{adj}M$ (Deep Dive); $\mathbf x_p$ particular solution, $\mathbf x_h$ null-space vector with
free variable 1. Counts: $M$ is $m\times n$; $i,j$ row, column; $k$ elimination step. Never: $\mathbf x_j$ for columns
(LM8), $t$ as a parameter, $\mathbf q$, $\mathbf h$, $\mathbf z$, $s$, $L$, $U$, $C$, $A$, $^T$, $r$ for rank,
$\mathbf y$, $\hat{\boldsymbol\beta}$, $\kappa$, $\lambda$; $n$ never counts periods (problem 8 writes $v_1,v_2,v_3$).

**Motivating case** `> [!case] Three sectors, three days`. After the 2025 Qingming holiday TAIEX moved −9.70%, −4.02%,
−5.79% and +9.25% on 7, 8, 9 and 10 April. Is there one mix of Semiconductor, Financial and Food whose returns
reproduce TAIEX's on each day? Two days: infinitely many. 7–9 April: exactly one, $(0.334,\,1.447,\,-0.916)$, sum
0.865. 8–10 April: $(-0.018,\,2.069,\,-1.376)$. All four days: none, and the 7–9 multiples give +10.17% on 10 April,
not +9.25%. Why does a perfect fit say so little? Anchor: TAIEX −9.699731% (`vol2_anchors.txt` block (h)); the rest is
printed by `lm09_numbers.py`. Resolved in §4 (the solution), §6 (regimes, triples), §7 (the singular mix).

| § | Title | Words | Content | Ex. | KC |
|:--|:--|--:|:--|:--|:--|
| — | Introduction | 350 | framing, case, `days`, roadmap, notation note | — | — |
| 1 | Two Pictures of a Linear System | 520 | rows: each day a line (3D a plane); columns (9.1); 2×2 lines meet, are parallel or coincide | E1 | which picture shows "no solution" |
| 2 | The Determinant | 600 | signed area (9.2); cofactors, volume; row-operation rules; triangular; (9.3) stated; $\det=0\iff$ dependent; small ≠ nearly singular | E2, E3 | sign after swapping two days |
| 3 | Cramer's Rule | 400 | (9.4) from column linearity; (7.12) recast; cost $n!$ terms per determinant vs $\tfrac23n^3$ | E4 | products for $n=4$ |
| 4 | Gaussian Elimination | 580 | row operations keep solutions; triangular form; back substitution; swaps; det from pivots; `solve` is this (LU, partial pivoting) | E5 | one elimination step |
| 5 | The Inverse | 500 | definition; (9.5); Gauss–Jordan; rules; (9.6); `solve(M, b)` first, `inv` for concepts or many right-hand sides | E6 | why `inv(M) @ b` is the wrong habit |
| 6 | Rank and the Number of Solutions | 680 | independence, col/null space, pivots, (9.7), (9.8); case: 2/3/4 days, four triples; hygiene note; pitfall TX/MTX | E7, E8 | classify three augmented matrices |
| 7 | Perfect Collinearity in Returns, and Python | 480 | (9.9); rebalanced mix exact, buy-and-hold not; Electronic (full rank, nearly dependent → LM11/12); float output; Python | E9 | which mix is collinear |
| — | Summary · Problems · Solutions | 170·420·600 | eight bullets with the case's numbers; 11 problems | — | — |

Total 5,300 words. 中文導讀 (four): after §1 (一列一個方程是「線相交」，一欄一個工具是「組合湊出目標」); after §3
(行列式＝面積或體積的倍率；Cramer 漂亮但 $n$ 大時算不動); after §5 (消去法就是電腦的 `solve`；反矩陣是概念，不是解題
步驟); after §7 (三天三個未知數一定解得出來，所以剛好擬合不代表組合有意義；完全共線＝某個組合每天報酬為 0). Deep Dives:
row rank = column rank; $M^{-1}=\operatorname{adj}M/\det M$; the product rule via elementary matrices (Strang 2016, 5th ed.).

**Exhibits** (12). `days` (Intro, table; note: 7 April runs from the 2 April close, limit-down day). `rowpic` (§1,
`scatter`, E1's two lines meeting). `colpic` (§1, `vector`, E1's scaled columns adding to $\mathbf b$). `three` (§1,
`scatter`, crossing, parallel, coincident pairs). `area` (§2, `vector`, E1's parallelogram 24.753 beside the 1.52° pair,
2.781). `cost` (§3, `line`, log y, $(n+1)!$ vs $\tfrac23n^3$, $n=2,\dots,20$). `elim` (§4, table, each step with
multipliers and pivots). `inverse` (§5, `heatmap`, fmt `n3`, min/max from the matrix). `regimes` (§6, table: days →
ranks, count, $\mathbf x$). `triples` (§6, `bar`, three sectors × four triples). `wline` (§6, `scatter`, the 7–8 April
line in $(x_1,x_2)$ with the 7–8–9 and 7–8–10 solutions on it: a third day picks one point). `drift` (§7, `line`,
buy-and-hold weight in Semiconductor vs the rebalanced 0.5, 2008-12-01 → 2026-10-08).

**Widget** `systemExplorer`: a 2×2 system; presets "8 and 9 April" (E1; initial and PDF state), "7 and 9 April,
Semiconductor and Food" (1.52°), "a collinear pair", "LM7's $\Sigma$"; sliders for column 2 and $\mathbf b$. Linked
`vector` (parallelogram, area $\det M$) and `scatter` (two lines); readout $\det M$, rank, verdict, $\mathbf x$, which
grows as the columns align (note points to [[LM11]]). Spec from `lm09_charts.py`; singularity by a stated tolerance.

**Examples** (9). E1 8–9 April, Semiconductor and Financial: both pictures, $\mathbf x=(1.0351,\,0.2074)$. E2 E1's
signed area 24.753; the 7–9 April Semiconductor–Food pair (1.52°): area 2.781, $\mathbf x=(-3.48,\,5.12)$. E3
$\det M=-71.591922$ (7–9 April) by cofactors. E4 Cramer: $x_3=65.586258/(-71.591922)=-0.916113$; (7.12) as Cramer. E5
elimination, 7–9 April: pivots −9.95, 4.495940, 1.600370; $\mathbf x=(0.334105,\,1.446834,\,-0.916113)$. E6 LM7's
$\Sigma^{-1}$, $\Sigma^{-1}(\boldsymbol\mu-r_f\mathbf 1)=(5.59,\,-0.52)$, $\Sigma\Sigma^{-1}=I$. E7 7–8 April, three
unknowns: $x_1=1.003671+0.730877\,x_3$, $x_2=-0.028971-1.610943\,x_3$. E8 four days: ranks 3 and 4
($\det[M\mid\mathbf b]=65.603260$), no solution. E9 mix column $(\mathbf m_1+\mathbf m_2)/2$, 7–9 April: rank 2,
$\mathbf x_h=(-\tfrac12,-\tfrac12,1)^{\top}$, no solution; common sample `matrix_rank` 2 (rebalanced) vs 3 (buy-and-hold).

**Problems** (11: 3 MC, 6 computational, 2 Python). 1 MC swap two rows, double a third: $\det$ times **C** (−2). 2 MC
four days, $\operatorname{rank}[M\mid\mathbf b]=4$: **A** (none). 3 MC which 50/50 mix makes a three-column return
matrix singular on every sample: **B** (daily rebalanced). 4 7 and 10 April, Semiconductor and Food, by Cramer and
(9.5): $\det=28.9066$, $\mathbf x=(0.85174,\,0.14147)$. 5 elimination on 8–10 April vs E5. 6 $\det$ of 7–8–10 by
cofactors and by pivots (22.568247). 7 rank, column space, $\mathbf x_h$ of an integer 3×4 augmented matrix with a
parameter. 8 three discount factors from three illustrative coupon bonds, forward substitution, [[LM6]]. 9 TX and MTX
per TAIEX point (200, 50) on two illustrative days: singular, reachable targets, $\mathbf x_h=(-\tfrac14,1)^{\top}$. 10
Python: `solve` vs `inv @ b`; `solve` on four days raises `LinAlgError`; `matrix_rank`. 11 Python: the two mixes, ranks
2 and 3, the drift.

**Lab.** 1 Data (four days; common-sample S3; repair cell with rule and count). 2 Both pictures. 3 Cofactor determinant
with `Fraction` vs `np.linalg.det`. 4 Cramer timed against `solve`, $n=2,\dots,9$. 5 Elimination with swaps vs `solve`.
6 Gauss–Jordan; LM7's $\Sigma^{-1}$. 7 `regimes`, E7, the triples. 8 Mixes; U28 rank 28; Electronic + eight, rank 9. 9
Problems 4–11. Extension: $N$ U28 sectors on exactly $N$ days, $N=3,\dots,10$ (in-sample).

**Tags.** (9.1) $M\mathbf x=x_1\mathbf m_1+\dots+x_n\mathbf m_n$ (LM12, LM27). (9.2) 2×2 $\det$ = signed area (LM11).
(9.3) $\det(MK)=\det M\det K$, $\det M^{\top}=\det M$, $\det M^{-1}=1/\det M$ (LM10, LM11). (9.4) Cramer
$x_j=\det M_j(\mathbf b)/\det M$ (LM7, LM28). (9.5) 2×2 inverse (LM10, LM28, LM43). (9.6) invertible $\iff\det M\ne0
\iff\operatorname{rank}M=n\iff\operatorname{null}M=\{\mathbf 0\}$ (LM10–12). (9.7) rank–nullity (LM11, LM12). (9.8)
solvable $\iff$ equal ranks; $\mathbf x_p+\operatorname{null}M$ (LM12, LM29). (9.9) $\operatorname{rank}X<N\iff
X\mathbf x=\mathbf 0$, $\mathbf x\ne\mathbf 0$ (LM10, LM23, LM30).

**Pitfalls to pre-empt.** (a) The multiples need not sum to 1: a replicating mix, not portfolio weights. (b) A square fit
always succeeds when $\det M\ne0$; Financial's multiple runs from −1.479 to 2.069 over the four triples, so no triple
estimates sector weights. (c) 7 April runs from the 2 April close (holiday, weekend) and was limit-down: its row
$(-9.95,-9.89,-8.66)$ lies 3.6° from $-\mathbf 1$, nearly a multiple of $\mathbf 1$ (PITFALLS §7). (d) A small determinant is not "nearly
singular": $\det(0.1\,I_9)=10^{-9}$; compare with column lengths (E2); LM11 measures it. (e) For the exactly singular
mix matrix `det` prints about $10^{-14}$ and `solve` may return entries of order $10^{15}$ instead of raising
(machine-dependent: print no digits; assert "exception or $\max\lvert x_j\rvert>10^{10}$"); `matrix_rank` uses a
tolerance (LM12). (f) Only the daily rebalanced mix is collinear; buy-and-hold drifts from 0.50 to 0.858 in
Semiconductor. (g) One instrument twice: the TX column is four times the MTX column, so MTX adds no direction and a
TX + MTX hedge is a line of answers, not a better hedge; a fact of the contract terms, not of settlement data. (h)
Cramer's cost exactly: one cofactor expansion of an $n\times n$ determinant has $n!$ terms, each a product of $n$ entries. (i) Boundary: no fit
over many days, no singular value, condition number, R-squared or $N\times N$ $\hat\Sigma$.

## LM10 Quadratic Forms and Covariance Matrices

**Prereq:** LM7 (two-asset variance, Hessian, the $2\times2$ test (7.4), expansion (7.2)), LM8 ($X$, $X\mathbf w$ (8.12), $R_p=\mathbf w^{\top}\mathbf R$ (8.3), Cauchy–Schwarz (8.6), triangle inequality (8.8), $\rho=\cos\theta$ (8.9)), LM9 (rank, (9.8) $\operatorname{rank}X<N\iff X\mathbf w=\mathbf 0$ for some $\mathbf w\ne\mathbf 0$, $3\times3$ determinants by cofactors, (9.4)); LM3 for the divisor-$T$ convention. **Leads:** LM11, 12, 16, 19, 20, 27, 28, 29, 30, 31, 43.

**LM7 forward references honoured:** line 57 ($N$-asset matrix notation: $\mathbf w^{\top}\hat\Sigma\mathbf w$ as a sample quantity; bookkeeping stays LM27); line 169 ($H=2\Sigma$: Hessian of $\mathbf w^{\top}M\mathbf w$ is $M+M^{\top}$, derived for $N$ assets); line 254 ($h_{xx}>0$, $\det H>0$ extended: leading principal minors, pivots, all principal minors for PSD); line 268 (PSD ⇒ convex, proved for quadratic functions only); line 75 (covariance: sample matrix here, population LM16). Keep LM7's glossary terms and Chinese: Covariance 共變異數, Positive definite 正定, Convex function 凸函數, Hessian 海森矩陣.

**Owns.** Quadratic forms $h(\mathbf x)=\mathbf x^{\top}M\mathbf x$; only $M_{\text{sym}}=(M+M^{\top})/2$ enters. The centred data matrix $\tilde X$; $\hat\Sigma=\tilde X^{\top}\tilde X/T$ and its outer-product form; annualized $A\hat\Sigma$; $C$ and the way back. $s_p^2=\mathbf w^{\top}\hat\Sigma\mathbf w$ as exactly the divisor-$T$ variance of the daily-rebalanced series $X\mathbf w$; the equal-weight identity (10.6). PSD/PD for $N\times N$ symmetric matrices: definition, diagonal entries, leading principal minors (PD), all principal minors (PSD) with the counterexample, pivots, congruence ($K^{\top}MK$ stays PSD, so $C$ PSD ⇔ $\hat\Sigma$ PSD). Why $\hat\Sigma$ is PSD (10.5); PD ⇔ $\tilde X$ has full column rank; the rank bound (10.7). Pairwise deletion and how it breaks PSD. Matrix calculus: $\nabla(\mathbf a^{\top}\mathbf w)$, $\nabla(\mathbf w^{\top}M\mathbf w)$, Hessian $2M$, the exact expansion (10.9); PSD ⇔ convex and PD ⇔ strictly convex for quadratic functions.

**Leaves.** Population covariance, random vectors, multivariate normal → LM16. Descriptive statistics, $T$ vs $T-1$ as a bias question → LM19, LM20. Eigenvalues, the eigenvalue test of PSD, condition numbers, statistical factors → LM11. Cholesky (pivots become $LL^{\top}$), numerical rank and tolerances, SVD, least squares → LM12. Portfolio bookkeeping in matrix form, covariance of an asset with the portfolio, risk decomposition → LM27. Euler risk contributions → LM31 (with LM27). Minimum variance, frontier, tangency (no solving $\nabla s_p^2\propto\mathbf 1$) → LM28. General convexity, convex programs, KKT in $N$ dimensions → LM29. Estimation error in $\hat\Sigma$, shrinkage, nearest-correlation repair, 1/N as a portfolio choice → LM30. EWMA/GARCH covariance → LM26. Economic factors → LM23.

**Uses before taught.**

- Population covariance: "$\hat\Sigma$ summarizes the sample; the covariance matrix of a random vector, which $\hat\Sigma$ estimates, is defined in [[LM16]]." (§3, once.)
- Divisor $T-1$: "Dividing by $T-1$ removes a small bias under assumptions that [[LM20]] states; with $T=4{,}382$ it multiplies a volatility by about 1.00011." (§3 pitfall.)
- Eigenvalues: "A third test, through the eigenvalues of $M$, arrives in [[LM11]], which also measures how close to singular $\hat\Sigma$ is." (§5, §6.)
- Cholesky: "The pivots of Section 5 are the squares of the diagonal of the Cholesky factor of [[LM12]]." (§5.)
- Numerical rank: "`matrix_rank` decides rank with a tolerance; [[LM12]] explains it." (§6, §8.)
- Adjugate: "$\operatorname{adj}M$, the transposed matrix of cofactors, satisfies $M\operatorname{adj}M=(\det M)I$ ([[LM9]], Deep Dive)." (§6 widget note, Problem 7.)
- General convexity: "For functions that are not quadratic, the same conclusion needs the argument of [[LM29]]." (§7.)
- Risk contributions: "Splitting $s_p^2$ into one share per asset is the subject of [[LM27]] and [[LM31]]; this module stops at the gradient." (§4 and §7.)

**Data role.** Daily closes of U28, the 28 leaf TWSE sector indices (the 30 sector ids of `data/raw/sectors` without the aggregates Electronic and ChemicalBiotechnologyMedicalCare), from `data/processed/vol2_closes.parquet` (`data/vol2_series.py`: repaired from the 13:30:00 values, 524 U28 closes on 38 dates inside the sample). One common sample: closes 2008-12-01 → 2026-10-08, $T=4{,}382$ simple returns from 2008-12-02, 17.85078713 years, $A=245.4793712$ (= `vol2_anchors.txt` sample (a)); no gaps. Price indices (no dividends). Hand-sized blocks on the same sample: S3 = Semiconductor, FinancialInsurance, Food; S5 = S3 + Plastics, ShippingTransportation. TAIEX on the same dates, one number (context). 0050, 00631L and 00679B one-session total returns, built from their raw closes and dividends ("Labs"; 0050 and 00631L from 2014-11-03, 00679B from 2017-01-18), only for the pairwise-deletion examples; never put an ETF and a sector in one $\hat\Sigma$ without saying that sectors are price returns and ETFs total returns. Scripts: `data/lm10_numbers.py` (asserts every printed value), `data/lm10_charts.py`. No new FinMind data.

**Hygiene declaration.** Descriptive. Every $\hat\Sigma$, $C$ and $s_p^2$ summarizes 2008-12-02 → 2026-10-08 and is not a forecast. The weight switch of §7 reports what it would have done to the sample variance. No half-sample or rolling comparison in the text (LM11, LM30); the lab's per-year extension is labelled a stability check. E9 is constructed: real returns, missing years chosen by the author, labelled in the example title, exhibit note and widget note. Local note: "Every matrix in this module describes 2008–2026. It is not a forecast, and no result here is tested on later data ([[LM11]] compares periods; [[LM30]] treats estimation error)."

**Notation** (book-wide symbols with their §6 meaning: $\mathbf R_t$, $X$, $\tilde X$, $\bar{\mathbf R}$, $\hat\Sigma$, $\mathbf s$, $C$, $s_p^2$, $\sigma_p^2$ only when pointing to LM16, $\mathbf w$, $\mathbf 1$, $\mathbf 0$, $\mathbf e_i$, $I_N$, $^{\top}$, $\det$, $\operatorname{rank}$, $\operatorname{diag}$, $N$, $i$, $j$, $T$ a count of returns, never a horizon, $t$, $A$, $H$, $\boldsymbol\Delta$ a step as in LM7). Local, each checked against §6:

- $M$, $K$ generic matrices, $m_{ij}$ entries (table). $h(\mathbf x)=\mathbf x^{\top}M\mathbf x$ a quadratic form ($q$ is book-wide; $h$ is the allowed generic function).
- $\mathbf x$, $\mathbf y$ generic vectors in purely mathematical passages; in §6 $\mathbf x$ is positions in standard-deviation units. Declared; LM10 has no least squares and no yields.
- $M_{\text{sym}}$; $M_k$ leading $k\times k$ block, $\det M_k$ its leading principal minor; $\delta_k=\det M_k/\det M_{k-1}$ the $k$th pivot ($\det M_0:=1$); $k$ is only a block size.
- $\hat\sigma_{ij}$ entries of $\hat\Sigma$, $\hat\sigma_{ii}=s_i^2$ (subscripted, distinct from $\sigma$). $\mathbf a$ coefficient vector of $\mathbf a^{\top}\mathbf w$ (module without bets). $\alpha\in[0,1]$ mixing weight. $\overline{\operatorname{var}}$, $\overline{\operatorname{cov}}$ averages of the $N$ diagonal and $N(N-1)$ off-diagonal entries of $\hat\Sigma$. $\mathcal T_{ij}$, $T_{ij}$ dates on which $i$ and $j$ both have returns, and their number. $\operatorname{adj}M$ adjugate.
- Not used: $\lambda_k$, $\mathbf q_k$, $Q$, $\Lambda$, $\kappa$ (LM11), $L$ (LM12); LM10 prints no eigenvalue or eigenvector.

**Motivating case: "Twenty-eight volatilities, one number."** A desk holds the 28 sector indices of U28 in equal weights, rebalanced daily. Over 2 December 2008 → 8 October 2026 (4,382 daily returns) the sectors' annualized volatilities run from 13.67% (CommunicationsInternet) to 35.31% (GlassCeramic), 21.94% on average. The book's volatility was 15.75%, below every sector but one and below TAIEX's 17.82%. The 28 variances alone give 4.22%. The case asks which numbers make the rest (406 distinct entries of a $28\times28$ matrix), why the answer can never fall below zero, and how a risk system can still print a negative variance. Resolved: §4 (E5: identity (10.6), off-diagonal terms 92.8% of $s_p^2$, a split of the quadratic form, not of assets), §5 ((10.5)), §6 (E9). Anchors printed by `data/lm10_numbers.py`; all provisional (see Numbers to verify).

**Sections** (prose words, AUTHORING §1 count):

| § | Title {lo} | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | framing; case + X1; roadmap; notation and hygiene notes | 400 |
| 2 | Quadratic Forms and Symmetric Matrices {1} | opens with the S3 matrix $A\hat\Sigma_3$ (%²) evaluated at $(0.5,0.3,0.2)$, $\mathbf e_1$ and $(1,-1,0)$; definition, double sum; (10.1); level sets (X2); $h(\mathbf e_i)=m_{ii}$; (7.4) as $N=2$; E1 | 560 |
| 3 | The Sample Covariance Matrix {2} | E2 table first; $X$, $\bar{\mathbf R}$, $\tilde X$, (10.2) both forms; shapes (X3); (10.3) and back, annualizing (E3); U28 heatmap (X4); pitfall: divisor and orientation (`np.cov` defaults) | 620 |
| 4 | Portfolio Variance as a Quadratic Form {3} | (10.4) derived in two lines, constant weights only; E4 with grid X5 (total only); $s_p\le\mathbf w^{\top}\mathbf s$ by (8.8); (10.6); E5 resolves case part 1 | 560 |
| 5 | Positive Semidefinite and Positive Definite Matrices {4} | opens with $C_3$ (E6); definitions; (10.5); PD ⇔ full column rank ((9.8)); tests: diagonal, leading minors (proof by completing squares in a Deep Dive), pivots, all principal minors for PSD (E7), congruence; X6; pointers LM11, LM12 | 660 |
| 6 | When $\hat\Sigma$ Fails: Singularity and Pairwise Deletion {5} | (10.7) via deviations summing to $\mathbf 0$; E8 + X7; exact collinearity (S5 + its equal-weight series); pitfall: rounding and floating point; pairwise deletion: the real case (U28 + the three ETFs: $C$ PD, the pairwise $\hat\Sigma$ not PSD), E9 + X8 + widget, case part 3 | 640 |
| 7 | Matrix Calculus: Gradients, the Hessian and Convexity {6, 7} | (10.8) componentwise; (10.9) exact (LM7's (7.2) with no remainder); zero-sum trades, only differences of gradient entries matter; E10; X9; Hessian $2\hat\Sigma$; (10.10) ⇒ PSD ⇔ convex (converse in a Deep Dive); boundary sentences to LM27/28/31 | 600 |
| 8 | Quadratic Forms and Covariance in Python {8} | `Xc.T @ Xc / T` vs `np.cov(X, rowvar=False, ddof=0)`; `X @ w` check; minors and pivots; PSD check with a tolerance; pairwise masks; X10; lab box | 260 |
| — | Summary (7 bullets) / Practice Problems (11) / Solutions | | 140 / 360 / 500 |
| | **Total** | | **5,300** |

Elements: 10 examples, 7 knowledge checks (§2–§8), 5 中文導讀 (§2–3, §4, §5, §6, §7), at most one pitfall per section, 2 Deep Dives (leading minors by completing squares; convex ⇒ PSD: $0=h(\mathbf 0)\le\frac12h(\mathbf x)+\frac12h(-\mathbf x)=h(\mathbf x)$).

**Exhibits.** X1 `bar` §1: 28 annualized volatilities sorted, `hline`s 21.94% (mean), 15.75% (book), 4.22% (variances only); TAIEX 17.82% in the note; Source line (FinMind `TaiwanStockPrice`, repaired from `TaiwanStockEvery5SecondsIndex`, retrieval date). X2 `vector` §2: level sets $h=1$ of a PD form (`ellipses`, cov $M^{-1}$), a PSD singular form (two `lines`), an indefinite form (hyperbola from short `lines`). X3 table §3: $X$ ($4382\times28$) → $\bar{\mathbf R}$ → $\tilde X$ → $\hat\Sigma$ ($28\times28$, 406 distinct entries): shape and meaning. X4 `heatmap` §3: U28 $C$ ($28\times28$, n2, −1…1); labels drop on a phone above ~25 rows, so the note lists the row order (X1's order); run `print_width.py`. X5 table §4: the nine cells $Aw_iw_j\hat\sigma_{ij}$ (%²) for $(0.5,0.3,0.2)$ on S3 and their total only, no row sums (LM27/LM31). X6 table §5: definition / diagonal / leading minors / all principal minors / pivots / (eigenvalues → LM11) / (Cholesky → LM12): what each proves, cost, value on $C_3$. X7 `bar` §6: $\operatorname{rank}\hat\Sigma$ on the latest $T=20,\dots,35$ returns, `hline` at $N=28$. X8 §6 table (years kept per ETF, the three pair correlations with $T_{ij}$) + `vector` (admissible ellipse in the $(\rho_{13},\rho_{23})$ plane for $\rho_{12}=0.982$: `ellipses` cov $\begin{pmatrix}1&0.982\\0.982&1\end{pmatrix}$, scale 1, from $\det C\ge0$; 2018 common-sample point inside, constructed point outside). X9 `vector` §7: level ellipses of $A\hat\Sigma$ on Semiconductor/Food with arrows $2M\mathbf x$ at three points, each perpendicular to its ellipse. X10 table §8: `np.cov`, `Xc.T @ Xc / T`, Polars `pl.cov`/`pl.corr`, `matrix_rank`: orientation, default divisor, null handling, what to pass (checked 2026-10-11, "Python facts" above; Polars documents no null rule, so the table reports what the lab observes and says so).

**Widget `corr3` — "Can these three correlations coexist?"** Sliders $\rho_{12},\rho_{13},\rho_{23}\in[-1,1]$, step 0.001. Shows the three $2\times2$ principal minors, $\det C$, the verdict (PD / PSD singular / not PSD, by all principal minors) and, when not PSD, a witness $\mathbf x=\operatorname{adj}(C)\mathbf e_j$ with $\mathbf x^{\top}C\mathbf x=\det C\cdot\operatorname{adj}(C)_{jj}<0$ ($j$ with a positive $2\times2$ minor; proof is Problem 7). A `vector` chart draws X8's ellipse for the current $\rho_{12}$ and the current point. Initial state: E9's constructed values (0.982, 0.199, −0.444), so the PDF shows the failure; the note says "constructed". No eigenvalues.

**Examples.**

- E1 §2 The cross term decides: $M=\begin{pmatrix}1&4\\0&1\end{pmatrix}$ has $m_{11}>0$, $\det M=1$, yet $h(1,-1)=-2$; $M_{\text{sym}}$ has $\det=-3$.
- E2 §3 A covariance matrix by hand: Semiconductor, FinancialInsurance on 7, 8, 9 April 2025 (previous date 2 April): −9.95, −3.99, −4.47 and −9.89, +0.53, −5.61 (%); from the printed values $\hat\Sigma$ and $\rho=0.851$.
- E3 §3 From $\hat\Sigma$ to $C$ and back: S3 $A\hat\Sigma_3$ (%²) 570.3, 261.8, 162.3 / 363.7, 191.3 / 283.5 → 23.88%, 19.07%, 16.84%; 0.575, 0.403, 0.596.
- E4 §4 A three-sector mix: $(0.5,0.3,0.2)$ on S3: 17.91% against a weighted-average volatility of 21.03%.
- E5 §4 Equal weights on U28: $\overline{\operatorname{var}}$, $\overline{\operatorname{cov}}$, (10.6) → 15.75%; limit $\sqrt{A\,\overline{\operatorname{cov}}}=15.45\%$ as $N\to\infty$ with both averages held fixed (a thought experiment, labelled).
- E6 §5 Three tests on one matrix: $C_3$ to 3 decimals: leading minors 1, 0.669375, 0.427966; pivots 1, 0.6694, 0.6394; PD.
- E7 §5 When leading minors mislead: $\operatorname{diag}(0,-1)$; Semiconductor, FinancialInsurance and their 50/50 daily mix, third row built from E3's printed entries (416.05, 312.75, 364.4): principal minors ≥ 0, $\det=0$ exactly, PSD not PD.
- E8 §6 Twenty-eight sectors, twenty-eight days: rank 27 on the latest 28 returns (from 2026-08-28), 28 on 29.
- E9 §6 A risk system that prints a negative variance (constructed): 0050 kept for 2018 and 2023, 00631L for 2018 and 2019, 00679B for 2019 and 2023; $\rho$ = 0.982 (2018), 0.199 (2023), −0.444 (2019); no common date; $\det C=-0.374592$; $\mathbf x=(-1,1,1)$ gives $-0.25$.
- E10 §7 Selling one sector into another: EW U28, $\boldsymbol\Delta=\tfrac1{28}(\mathbf e_{\text{CommunicationsInternet}}-\mathbf e_{\text{GlassCeramic}})$; gradient entries 0.07230, 0.02764; linear −0.001595, quadratic +0.000136; variance 0.024803 → 0.023345; volatility 15.75% → 15.28%; exact.

**Problems plan** (11; MC keys B, C, A; Python: 11; lab repeats 4, 5, 6, 9, 11). 1 MC which symmetric $3\times3$ is PD (one negative leading minor, one PSD singular): **B**. 2 MC $\mathbf x^{\top}\begin{pmatrix}2&6\\0&3\end{pmatrix}\mathbf x$ is PD / PSD / indefinite: **C** ($\det M_{\text{sym}}=-3$). 3 MC 20 returns on U28: $\operatorname{rank}\hat\Sigma$ at most 19 / 20 / 28: **A**. 4 Rebuild $A\hat\Sigma_3$ from printed $C_3$ and volatilities; volatility of $(0.2,0.3,0.5)$: 15.74%. 5 (10.6) with S5's averages (16.73%, limit 14.92%) and U28's (15.75%, 15.45%). 6 Leading minors and pivots of printed $A\hat\Sigma_3$: pivots 570.3, 243.52, 181.29; PD. 7 Prove the adjugate witness identity; apply to E9 ($j=1,2,3$: −0.3007, −0.3598, −0.0134). 8 Gradient of $\mathbf a^{\top}\mathbf w-\frac12\mathbf w^{\top}M\mathbf w$ at a given point (no optimum: LM28, LM43). 9 Exact expansion for a 5-point switch Semiconductor → Food on E4's mix, from the printed $A\hat\Sigma_3$: linear −0.002009, quadratic +0.000132, variance 0.032060 → 0.030184, 17.91% → 17.37%; the solution says that the printed matrix gives 320.60 %² where X5's unrounded one gives 320.62. 10 Prove convexity from (10.10) for PSD $M$; find $\mathbf x,\mathbf y$ violating it for E1's $M$. 11 Python: S5 $\hat\Sigma$ three ways; `np.var(X @ w)` against `w @ S @ w`; the `ddof=1` difference. Each question states divisor $T$, $A$ and its sample, daily rebalancing, rounding (PITFALLS §7).

**Lab parts** (`build/make_lab10.py`): 1 data: U28 closes, the repair cell (rule and its count, 524), returns, $T$, $A$; 2 forms: symmetric part, level sets; 3 $\hat\Sigma$ three ways, $C$, heatmap, E2, E3; 4 `X @ w` vs `w @ S @ w`, grid, (10.6), case; 5 minors, pivots, all principal minors, congruence check; 6 rank vs $T$, collinear sixth column (residue printed as "below 1e-15"), pairwise masks on the ETFs, the real U28 + ETF case; 7 finite-difference gradient vs $2\hat\Sigma\mathbf w$, E10, (10.10) numerically; 8 problems 4, 5, 6, 9, 11. Extension (stability check, pointer to LM11, no conclusions): EW volatility ÷ mean sector volatility per calendar year 2009–2025 and 2026 to date.

**Cross-module tags.** (10.1) $\mathbf x^{\top}M\mathbf x=\mathbf x^{\top}M_{\text{sym}}\mathbf x$ (LM11, 29). (10.2) $\hat\Sigma=\tilde X^{\top}\tilde X/T=\frac1T\sum_t(\mathbf R_t-\bar{\mathbf R})(\mathbf R_t-\bar{\mathbf R})^{\top}$ (LM11, 12, 16, 19, 27, 30). (10.3) $C=\operatorname{diag}(\mathbf s)^{-1}\hat\Sigma\operatorname{diag}(\mathbf s)^{-1}$ (LM11, 16, 30). (10.4) $s_p^2=\mathbf w^{\top}\hat\Sigma\mathbf w$ = divisor-$T$ variance of $X\mathbf w$ (LM27, 28, 31, 32). (10.5) $\mathbf w^{\top}\hat\Sigma\mathbf w=\lVert\tilde X\mathbf w\rVert^2/T\ge0$ (LM11, 12). (10.6) $s_p^2=\overline{\operatorname{var}}/N+(1-1/N)\overline{\operatorname{cov}}$ (LM27, 30). (10.7) $\operatorname{rank}\hat\Sigma\le\min(N,T-1)$ (LM11, 12, 30). (10.8) $\nabla(\mathbf a^{\top}\mathbf w)=\mathbf a$, $\nabla(\mathbf w^{\top}M\mathbf w)=(M+M^{\top})\mathbf w$, $H=2M$ (LM28, 29, 31, 43). (10.9) $h(\mathbf w+\boldsymbol\Delta)=h(\mathbf w)+2\boldsymbol\Delta^{\top}M\mathbf w+\boldsymbol\Delta^{\top}M\boldsymbol\Delta$, $M$ symmetric (LM27, 29). (10.10) $h(\alpha\mathbf x+(1-\alpha)\mathbf y)=\alpha h(\mathbf x)+(1-\alpha)h(\mathbf y)-\alpha(1-\alpha)h(\mathbf x-\mathbf y)$ (LM29).

**Pitfalls to pre-empt.**

- Leading minors ≥ 0 do not give PSD ($\operatorname{diag}(0,-1)$); PSD needs all principal minors. Sylvester needs a symmetric matrix (E1).
- Centring makes the deviations sum to $\mathbf 0$: the bound is $T-1$, so $\hat\Sigma$ is singular when $T\le N$ (Problem 3's key).
- (10.4) holds for constant (daily-rebalanced) weights only; buy-and-hold weights drift. Say "rebalanced daily" in the case and at (10.4).
- A gradient step changes total weight: only zero-sum trades count, only differences of gradient entries matter. Never call $2(\hat\Sigma\mathbf w)_i$, a row of X5 or the diagonal/off-diagonal split a contribution of an asset (LM27, LM31); never set the gradient proportional to $\mathbf 1$ (LM28).
- (10.9) is exact (`=`); the 15.45% limit holds under a stated hypothesis (both averages fixed), not in the data.
- Rounding can break PSD: E7's matrix with each computed entry rounded to 0.1 has $\det=-13{,}888.91$. Build printed matrices from printed inputs (E7 from E3's entries) and print floating-point residues as "below $10^{-15}$", never their value (they differ across machines).
- `np.cov` treats rows as variables and divides by $T-1$ by default; pass `rowvar=False, ddof=0`. `matrix_rank` uses a tolerance; X7 must match (10.7), asserted.
- $\mathbf x^{\top}C\mathbf x$ in E9 is the number a risk system would report, not a variance of any sample; $C$ needs every $s_i>0$.
- Data: only repaired closes from `vol2_series.py` (a raw read puts 2009-06-05 at the level of 29 June 2026); one sample, one $A$ (245.4793712, never S15's 245.78); sectors are price indices, ETFs total returns; E2 computed from the two-decimal printed returns; E9's year triple is a choice (362 of the 720 assignments with distinct years fail) and the script prints the per-year table so the choice is visible.

## LM11 Eigen-decomposition and PCA

**Prereq** LM7 (Lagrange multipliers; $m$, $M$, $\kappa$ of line 615), LM8 (dot product, norm, angle), LM9 (inverse, determinant, exact rank, solving systems), LM10 ($\hat\Sigma$, $C$, positive semidefiniteness). Front matter `prereq: [7, 8, 9, 10]`. **Leads** LM12, LM16, LM23, LM27, LM28, LM30, LM43, LM45. Time "≈ 3 h + lab". Syllabus line: "Principal components of Taiwan sector returns; condition numbers and why Σ⁻¹ amplifies error."

**Outcomes (7).** (1) eigenpairs of a 2×2 symmetric matrix by hand and of an $N\times N$ one with `eigh`; (2) the spectral theorem with its conditions, $\hat\Sigma=Q\Lambda Q^{\top}=\sum_k\lambda_k\mathbf q_k\mathbf q_k^{\top}$; (3) the first principal component as a variance-maximizing unit vector whose multiplier is the eigenvalue; (4) shares, loadings, scores, covariance versus correlation PCA; (5) the sign convention and why near-equal eigenvalues give unstable eigenvectors; (6) stability across years and halves, labelled a stability check; (7) $\kappa=\lambda_1/\lambda_N$ and why solving with $\hat\Sigma^{-1}$ amplifies estimation error.

**Owns.** Eigenvalue, eigenvector, characteristic equation, the 2×2 formula, trace = sum and det = product; the spectral theorem for real symmetric matrices (2×2 proof in the text, $N\times N$ by repeated maximization in a Deep Dive); rank-one sum; PD/PSD ⇔ all $\lambda_k>0$ ($\ge0$) (LM10's third test); the Rayleigh quotient and its bounds; the condition number of a positive definite matrix and the spectral norm; PCA (Lagrangian derivation, successive components, shares, scree, scores, covariance vs correlation); sign indeterminacy and the book's convention; repeated and near-equal eigenvalues; stability across calendar years and halves; $\hat\Sigma^{-1}=Q\Lambda^{-1}Q^{\top}$; the perturbation bound; `eigh`, ordering, sign fixing, `cond`, `solve`.

**Leaves.** SVD, PCA from $\tilde X$, numerical rank, pseudoinverse, Cholesky → LM12. Ellipses as probability contours, the multivariate normal → LM16. Sampling error and confidence intervals of eigenvalues, bootstrap of loadings → LM20, LM22. Economic factor labels, factor regressions → LM23. Risk contributions → LM27. Minimum-variance and tangency weights → LM28. Covariance shrinkage, eigenvalue cleaning, eigenvalue bias → LM30. HRP → LM31. Out-of-sample tests → LM34. $\Sigma^{-1}(\boldsymbol\mu-r_f\mathbf 1)$ and its estimation error → LM43, LM45.

**Uses before taught.**

- Extreme value theorem in several variables: "A continuous function on a closed and bounded set, such as the unit sphere, attains a largest value (stated without proof)." → Strang and Herman 2016, *Calculus Volume 3* (OpenStax), §4.7, Theorem 4.18 (two variables; the text states the $N$-variable case without proof).
- Rotation matrices: "A rotation of the plane by an angle other than 0° or 180° has no real eigenvector; symmetry is what excludes this." (one sentence, no complex numbers) → Strang 2016, §6.1 (the 90° rotation).
- Eigenvalue algorithms: "`eigh` does not solve the characteristic polynomial; it uses an iterative method (stated without proof)." → Golub and Van Loan 2013, ch. 8.
- Sampling error of an eigenvalue: "An eigenvalue estimated from 250 returns has sampling error of its own; this module compares periods but attaches no confidence intervals." → [[LM20]], [[LM22]].
- Factor model: "An economic factor model names its factors in advance and estimates exposures by regression; PCA lets the data choose the directions." → [[LM23]].
- Shrinkage: "Pulling the small sample eigenvalues up lowers $\kappa$; it is the subject of [[LM30]]."
- Minimum variance: "Rescaled to sum to 1, the solution of $\hat\Sigma\mathbf x=\mathbf 1$ is the minimum-variance portfolio of [[LM28]]; here it is only a linear system." → [[LM28]].
- SVD: "The same components come from the singular value decomposition of $\tilde X$, the route software prefers." → [[LM12]].
- Out-of-sample test: "A test fits on earlier data and judges on later data the fit never used; two halves compared side by side are not one." → Research hygiene page, [[LM34]].

**Data role.** Universe **U28**: the 28 leaf TWSE sector price indices (all 30 sector series of `data/raw/sectors` except `Electronic` and `ChemicalBiotechnologyMedicalCare`), one common sample: closes 2008-12-01 → 2026-10-08 from `data/processed/vol2_closes.parquet` (repaired closes; no missing value in U28 on this sample), daily simple returns between consecutive TAIEX-calendar dates, $T=4{,}382$ (first return 2008-12-02), $A=245.4794$, divisor $T$. Hand-sized subsets on the same sample: the pair Semiconductor/FinancialInsurance, **S3** = Semiconductor, FinancialInsurance, Food, **S5** = S3 + Plastics, ShippingTransportation. Overlap examples only (Section 6): Electronic with its eight sub-industries, and all 30 series, same sample. LM7's pair (0050/00679B daily total returns, own sample, $T=2{,}363$, $A=243.0543$) for Section 3; the 0050/00631L correlation (total returns on their 2,902 common dates, `etf_daily_returns.parquet`, LM8's sample) for one $\kappa$ line. Per-year results: full calendar years 2009–2025 plus "2026 to 8 October" (185 returns); the 22 returns of December 2008 enter only full-sample and half-sample results. Halves: the first $T/2=2{,}191$ returns (2008-12-02 → 2017-10-06) and the rest (2017-10-11 → 2026-10-08). The data illustrate a dominant first direction, a long flat tail of small eigenvalues, unstable minor directions, and an inverse that moves more than its matrix. They do not give tradable portfolios: indices are price indices with today's industry classification, so a principal direction is a **direction in the data**; the text does not use the phrase "eigen-portfolio" (if a reader meets it elsewhere, one sentence defines it this way). The lab repeats the close repair in one cell, with the rule and the counts that "Labs" names.

**Hygiene declaration.** Full-sample $\hat\Sigma$, $C$, eigenvalues, shares, loadings, $\kappa$: **descriptive**. Per-year shares and cosines, half-sample PCA and half-sample $\hat\Sigma\mathbf x=\mathbf 1$: **stability check**, never called out-of-sample. No claim about the future. Local note (≈ 70 words): universe and sample fixed before any result; halves split by time; full-sample loadings could not have been known inside the sample; a low cosine cannot tell noise from change.

**Notation** (book-wide symbols with their §6 meaning: $\hat\Sigma$, $C$, $\mathbf s$, $\tilde X$, $\mathbf R_t$, $\bar{\mathbf R}$, $N$, $T$, $t$, $i$, $j$, $\lambda_k$, $\mathbf q_k$, $Q$, $\Lambda$, $\kappa$, $M$, $m_{ij}$, $I$, $\mathbf 1$, $\mathbf e_i$ (no excess-return vector in LM11), $\lVert\cdot\rVert$, $\theta$, $A$, $\rho$, unsubscripted $\lambda$ = multiplier, $\mathcal L$, $M\mathbf x=\mathbf b$, generic $h$). Local: $\mathbf u$ unit vector (bold; plain $u$ stays a generic function); $h(\mathbf u)=\mathbf u^{\top}M\mathbf u/\mathbf u^{\top}\mathbf u$ the Rayleigh quotient; $\xi_{k,t}$ score of component $k$ on date $t$ ($\mathbf q_k^{\top}\operatorname{diag}(\mathbf s)^{-1}(\mathbf R_t-\bar{\mathbf R})$ for correlation PCA; not $\mathbf z_t$, LM12's whitened vector); $\bar\rho$ mean of the $N(N-1)$ off-diagonal entries of $C$; superscripts $^{(1)}$, $^{(2)}$ for halves (never powers); $\Delta M$, $\Delta\mathbf x$ changes of a matrix and a vector (LM12's $\delta$ is a rank tolerance, so not $\delta$); $\lVert M\rVert_2=\max_{\lVert\mathbf u\rVert=1}\lVert M\mathbf u\rVert$ spectral norm (largest $\lvert$eigenvalue$\rvert$ for symmetric $M$; never the Frobenius norm); $\varepsilon$ scalar off-diagonal perturbation in (11.7) (not LM12's $\hat{\boldsymbol\varepsilon}$); counts $k=1,\dots,N$ component index (no required return here). Not used: $g_k$ (eigengap in words), $c_k$ ($c$ is the Kelly fraction). Sign rule: the entry largest in absolute value is positive; on a tie, the first tied entry is positive (2×2 correlation: $\mathbf q_2=(1,-1)^{\top}/\sqrt2$). "R-squared" never appears as a symbol; the term is "explained share".

**Motivating case — "Twenty-eight sectors, how many movements?"** (≈ 180 words, table X1). Over 2008-12-02 → 2026-10-08 the daily returns of the 28 leaf sectors are all positively correlated, from 0.217 (BiotechnologyMedicalCare/OilGasElectricity) to 0.755 (ComputerPeripheralEquipment/ElectronicPartsComponents). One direction with loadings 0.130–0.224 carries 52.6% of the total variance of standardized returns, yet 12 directions are needed to pass 80%. The share was 66.6% in 2020 and 34.5% in 2017. A second direction is positive on the eight electronics sub-industries and three others, negative on
17. Solving $\hat\Sigma\mathbf x=\mathbf 1$ on each half: Semiconductor's entry goes from +430.84 to −587.60, FinancialInsurance's from −2,547.30 to +2,216.20; $\lVert\mathbf x^{(2)}-\mathbf x^{(1)}\rVert/\lVert\mathbf x^{(2)}\rVert=0.729$. Extreme-day line: on 2025-04-07 all 28 fell, by 5.90% (CommunicationsInternet) to 9.95% (Semiconductor); over the sample all 28 moved the same strict sign on only 300 of 4,382 days (6.8%). Questions: how many independent movements, do they hold over time, why does the solution move so much more than the matrix? Resolved in Sections 5, 7, 8.

**Sections** (prose words, `style.py` count; total ≈ 5,300; first draft under 5,500; 中文導讀 after 3, 4, 5, 7, 8)

| # | Section {lo} | Words | Content (one pitfall each) | Examples | KC |
|:--|:--|--:|:--|:--|:--|
| — | Introduction, notation note, hygiene note | 380+90+70 | case box, X1, roadmap in 3 sentences | — | — |
| 2 | Directions a Matrix Only Stretches {1} | 520 | circle → ellipse first; (11.1); characteristic equation; (11.2); trace/det; rotation sentence. Pitfall: an eigenvalue of $\hat\Sigma$ is not any sector's variance | E1 | eigenvalues from trace and det |
| 3 | Symmetric Matrices: the Spectral Theorem {2} | 560 | statement with conditions; 2×2 proof (discriminant $\tfrac14(m_{11}-m_{22})^2+m_{12}^2\ge0$, orthogonality from $\mathbf x_1^{\top}M\mathbf x_2$ read two ways); (11.3); PSD ⇔ $\lambda_k\ge0$; sign rule; repeated eigenvalue ⇒ only the eigenspace is determined. Pitfall: comparing eigenvectors entry by entry across periods | E2, E3 | is $-\mathbf q_k$ an eigenvector? |
| 4 | Variance in a Direction: the Rayleigh Quotient and the Condition Number {3,7} | 480 | $h(\mathbf u)$; (11.4) proved in $Q$ coordinates, closing LM7 line 615; $\kappa$ as largest over smallest directional variance; 2×2 correlation $\kappa=(1+\lvert\rho\rvert)/(1-\lvert\rho\rvert)$ (LM7 line 285 points here), 0050/00631L 77.0; X6 ladder; Deep Dive (≈ 100 words): LM7's $(\kappa-1)/(\kappa+1)=0.391$ on a quadratic. Pitfall: $\kappa$ of $C$ and of $\hat\Sigma$ differ (70.6 vs 108.1) | E4 | $\kappa$ of a 2×2 $C$ with $\rho=0.9$ |
| 5 | Principal Component Analysis {3,4} | 680 | variance of $\mathbf u^{\top}(\mathbf R_t-\bar{\mathbf R})$ is $\mathbf u^{\top}\hat\Sigma\mathbf u$; why $\mathbf u^{\top}\mathbf u=1$, not $\mathbf 1^{\top}\mathbf u=1$; (11.5): every eigenpair is stationary, the maximum is chosen by value; successive components; Deep Dive "PCA proves the spectral theorem" (≈ 150); (11.6); scree; scores, $\operatorname{Var}\xi_k=\lambda_k$, uncorrelated; covariance vs correlation; no labels; case Q1 resolved. Pitfall: naming components | E5, E6 | which PCA is unchanged by rescaling |
| 6 | Overlapping Indices and Near-Zero Eigenvalues {4,7} | 300 | a tiny $\lambda_N$'s eigenvector is a near-exact linear relation; why the book uses leaves only; links [[LM9]] exact rank, [[LM12]] numerical rank. Pitfall: an aggregate and its members in one matrix | E7 | read $\mathbf q_9$ |
| 7 | Eigenvalue Gaps and the Stability of Components {5,6} | 520 | (11.7); equicorrelation as the limit case; per-year shares and $\lvert\cos\theta\rvert$; halves; sign flips; plane measure $\sqrt{\cos^2\theta_2+\cos^2\theta_3}$ (cosines with $\mathbf q_2$, $\mathbf q_3$ of the other period); case Q2 resolved. Pitfall: a stability check is not an out-of-sample test | E8 | why PC1 is stable and PC4 is not |
| 8 | The Inverse of $\hat\Sigma$ and Error Amplification {7} | 550 | (11.8): small $\lambda_k$ get weight $1/\lambda_k$; spectral norm; (11.9) with its 3-line proof; worst case vs realized; case Q3 resolved. Pitfall: reading a large $\kappa$ as "the answer is wrong", or as a ranking of realized change | E9, E10 | where does most of $\hat\Sigma^{-1}\mathbf 1$ come from? |
| 9 | Eigen-decomposition in Python {1,6} | 150 | `eigh` (ascending: reverse), sign function with tie-break, `cond` (2-norm), `solve` never `inv`; one block ≤ 80 columns | — | what `eigh` returns first |
| — | Summary (6 bullets) / Problems / Solutions / lab box | 130/330/480/60 | | | |

**Exhibits.** X1 case anchors (table, Intro). X2 circle → ellipse under the Semis/Fin $\hat\Sigma$ (×10⁴), eigenvectors as arrows (`vector`; `ellipses` with `cov` $=M^2$, `axes`; S2). X3 LM7's 2,363 daily returns with the one-standard-deviation ellipse $\mathbf x^{\top}\Sigma^{-1}\mathbf x=1$ and axes, descriptive (`scatter` + `ellipses`; S3). X4 directional variance $h(\mathbf u)$ against the angle of $\mathbf u$, 0–180°, Semis/Fin, `hline` at $\lambda_1$, $\lambda_2$ (`line`; S4). X5 $\kappa$ ladder, columns $\kappa(C)$ and $\kappa(\hat\Sigma)$, rows LM7 pair, Semis/Fin, S3, S5, U28, Electronic + eight, all 30 (table; S4; note: a tendency with $N$, the last two rungs are overlap artefacts). X6 U28 scree, shares by $k$ (`bar`; S5). X7 U28 PC1 and PC2 loadings, 28 categories ordered by PC2 (`bar`, two series; S5). X8 covariance vs correlation PCA: share 1, share 2, $\lvert\cos\rvert$ of the two PC1, largest PC2 entry (table; S5). X9 overlap: smallest eigenvalues and largest entries of their eigenvectors, Electronic + eight and all 30 (table; S6). X10 PC1 share by year, 2009–2026, `hline` at 52.6%, 2026 bar "to Oct" (`bar`; S7). X11 per year: $\lvert\cos\theta_2\rvert$ and the plane measure against the full sample (`bar`, two series; S7). X12 two halves of U28: $\lambda_1..\lambda_5$, PC1 share, $\lvert\cos\theta_k\rvert$, $k=1..5$ (table; S7). X13 $\hat\Sigma\mathbf x=\mathbf 1$ in two halves: S5 entries, and U28 summary rows (relative change, cosine, bound) (table; S8). X14 share of $\lVert\mathbf x^{(h)}\rVert^2$ from each component, $(\mathbf q_k^{\top}\mathbf 1/\lambda_k)^2/\lVert\mathbf x\rVert^2$, $k=1..28$, two halves (`bar`; S8). No 28×28 heatmap.

**Widget `pca2`** (`src/lm11.js`). Sliders $\sigma_1$, $\sigma_2$ (annualized 5–60%), $\rho$ (−0.99 to 0.99); toggles covariance/correlation and right-hand side $\mathbf b=\mathbf 1$ or $\mathbf e_1$. Draws the one-standard-deviation ellipse with its axes (`vector`); prints $\lambda_1$, $\lambda_2$, PC1 share, $\kappa$, angle of $\mathbf q_1$, and the solution of $M\mathbf x=\mathbf b$ before and after $\rho+0.01$ with the relative change and the bound (11.9). Initial and PDF state: Semis/Fin, $\sigma_1=23.88\%$, $\sigma_2=19.07\%$, $\rho=0.575$, covariance, $\mathbf b=\mathbf e_1$. With equal $\sigma$ and $\mathbf b=\mathbf 1$ the solution barely moves ($\mathbf 1$ is then $\mathbf q_1$), which the note explains.

**Examples.**

- E1 Semis/Fin $\hat\Sigma=10^{-4}\begin{pmatrix}2.3234&1.0666\\1.0666&1.4817\end{pmatrix}$ (daily) by (11.2): $\lambda=3.0492$, 0.7559; $\mathbf q_1=(0.827,0.563)^{\top}$ at 34.2°; $\kappa=4.03$.
- E2 LM7's $\Sigma$ rebuilt: $\lambda_1=0.04079$, $\lambda_2=0.01785$, $\mathbf q_1=(0.992,-0.126)^{\top}$, tilt −7.24°, axis volatilities 20.20%, 13.36%.
- E3 S3 $\hat\Sigma$ as three rank-one pieces (3×3 displays): $\lambda=3.4728$, 0.9944, 0.4929 (×10⁻⁴), first share 70.0%.
- E4 Equicorrelation $C=(1-\rho)I+\rho\mathbf 1\mathbf 1^{\top}$: $1+(N-1)\rho$ once, $1-\rho$ $N-1$ times; Rayleigh with $\mathbf 1/\sqrt N$ on U28: $1+27\bar\rho=14.561\le\lambda_1=14.721$.
- E5 U28 shares: 52.58%, cumulative 80.93% at $k=12$.
- E6 units: Semiconductor in percent, FinancialInsurance in decimals: covariance PC1 becomes $(1.0000,0.0046)^{\top}$ with share 99.996%; correlation PCA unchanged.
- E7 Electronic + eight: $\lambda_9=0.0073$, $\mathbf q_9$ entries 0.828 (Electronic), −0.529 (Semiconductor), the rest $\le0.104$ in size; $\kappa(C)=836$.
- E8 (11.7) on U28's $\lambda_2,\lambda_3=1.4837,1.1469$ with $\varepsilon=0.05$: exact 8.27°, linearized 8.51°; on $\lambda_7,\lambda_8=0.5803,0.5444$: exact 35.1°, linearized 80.0° (fails when $\varepsilon$ is not small next to the gap).
- E9 2×2 $C$, $\rho=0.95\to0.96$, $\mathbf b=\mathbf e_1$: $\mathbf x=(10.256,-9.744)^{\top}\to(12.755,-12.245)^{\top}$; relative change 0.19996 against the bound $39\times0.005128=0.2000$ (nearly attained).
- E10 U28 halves through (11.8): PC1 gives 1.8% and 1.0% of $\lVert\mathbf x^{(h)}\rVert^2$, the 14 smallest components 72.0% and 80.5%; realized 0.729 against the bound $126.05\times0.2454=30.93$.

**Problems (12; MC keys 1 B, 2 C, 3 A, 4 A; Python 11, 12).** 1 MC: which matrix is guaranteed real eigenvalues and orthogonal eigenvectors (A positive entries; B real symmetric; C invertible). 2 MC: U28 $\lambda_1=14.721$, share closest to A 14.7%, B 37.4%, C 52.6%. 3 MC: one sector restated in percent; what changes (A covariance-PCA loadings; B correlation-PCA eigenvalues; C correlation-PCA loadings). 4 MC: halves, PC2 $\lvert\cos\rvert=0.297$, plane measure 0.927 (one-sided), reverse measure 0.514; best reading (A beyond the first, the components changed places; B the plane of PC2 and PC3 holds; C the sign rule failed): key A. 5 Plastics/Food $\hat\Sigma=10^{-4}\begin{pmatrix}2.5228&0.7180\\0.7180&1.1550\end{pmatrix}$: eigenpairs from the printed entries ($\lambda=2.8305$, 0.8473), share 77.0%, $\kappa=3.34$. 6 Equicorrelation $N=5$, $\rho=0.5$ (3, 0.5 four times; 60%; $\kappa=6$) vs S5's $C$ ($\lambda_1=2.863$, $\bar\rho=0.462$, $\kappa=8.52$). 7 rebuild a 2×2 from $\lambda_1,\lambda_2,\theta$ and check trace and det. 8 (11.7) exact vs linearized on an illustrative 2×2. 9 $\rho$ giving $\kappa=100$ ($99/101$); 0050/00631L $\kappa=77.02$ (LM8's sample). 10 S5 halves: bound $10.86\times0.4423=4.81$ vs realized 0.910, cosine 0.419; compare with U28 (worst case, not a ranking). 11 Python: S5 correlation PCA, eigenvalues 2.863, 0.667, 0.590, 0.544, 0.336, signed loadings, $\operatorname{Var}\xi_k=\lambda_k$. 12 Python: U28 per year, $\lvert\cos\rvert$ of PC1 and PC2 and the plane measure; the year with the smallest $\lambda_2-\lambda_3$ (2022, 0.029).

**Lab** (`build/make_lab11.py` → `labs/LM11_lab/`). 1 Data: `sectors_close_raw.csv` and the repair cell (rule, counts), returns, U28 sample, $T$, $A$. 2 LM7's pair: $\Sigma$, eigenpairs, tilt, X3. 3 E1 by hand vs `eigh`; trace, det. 4 S3 rank-one pieces, $Q^{\top}Q=I$, sign function with tie-break. 5 Rayleigh around the circle (X4), random unit vectors never beat $\lambda_1$, $\kappa$ ladder, LM7 gradient factor 0.391. 6 PCA of U28: scree, loadings, scores, covariance vs correlation, units test. 7 Overlap: Electronic + eight, all 30. 8 Stability: per year (X10, X11), halves (X12). 9 $\hat\Sigma^{-1}$: halves with `solve`, (11.8) shares (X14), bound (11.9) in the spectral norm. 10 Problems 5–12. 11 Extension: rolling 250-day PC1 share (descriptive, not in the text).

**Cross-module tags.** (11.1) $M\mathbf x=\lambda_k\mathbf x$, $\det(M-\lambda_kI)=0$ → LM12, LM16. (11.2) $\lambda_{1,2}=\tfrac12\operatorname{tr}M\pm\sqrt{\tfrac14(\operatorname{tr}M)^2-\det M}$ → LM16, LM27. (11.3) $\hat\Sigma=Q\Lambda Q^{\top}=\sum_k\lambda_k\mathbf q_k\mathbf q_k^{\top}$ → LM12, LM16, LM23, LM30, LM31. (11.4) $\lambda_N\le\mathbf u^{\top}\hat\Sigma\mathbf u\le\lambda_1$, $\lVert\mathbf u\rVert=1$ → LM27, LM28, LM30. (11.5) $\max_{\mathbf u^{\top}\mathbf u=1}\mathbf u^{\top}\hat\Sigma\mathbf u=\lambda_1$ via $\mathcal L$ → LM23. (11.6) share $\lambda_k/\operatorname{tr}\hat\Sigma$ ($=\lambda_k/N$ for $C$) → LM23, LM30. (11.8) $\hat\Sigma^{-1}\mathbf b=\sum_k(\mathbf q_k^{\top}\mathbf b/\lambda_k)\mathbf q_k$ → LM28, LM30, LM43, LM45. (11.9) $\lVert\Delta\mathbf x\rVert/\lVert\mathbf x+\Delta\mathbf x\rVert\le\kappa\lVert\Delta M\rVert_2/\lVert M\rVert_2$ for $(M+\Delta M)(\mathbf x+\Delta\mathbf x)=M\mathbf x=\mathbf b$, $M$ positive definite → LM12, LM29, LM30, LM45. (11.7) $\tan2\theta=2m_{12}/(m_{11}-m_{22})$; $\theta\approx\varepsilon/(\lambda_1-\lambda_2)$, dropped terms of order $(\varepsilon/(\lambda_1-\lambda_2))^3$ → LM23, LM30.

**Pitfalls to pre-empt.** Math: (a) "orthonormal eigenvectors can be chosen" for repeated eigenvalues, not "are orthogonal"; (b) the Lagrangian's stationary points are all eigenpairs, the maximum is picked by value, existence needs the extreme value theorem; with $\mathbf 1^{\top}\mathbf u=1$ the variance is unbounded; (c) $\kappa$ only for positive definite matrices ("infinite" if $\lambda_N=0$); `cond` equals $\lambda_1/\lambda_N$ only for symmetric PD input; (d) (11.9) holds in the spectral norm with denominator $\lVert\mathbf x+\Delta\mathbf x\rVert$; $\Delta M$ is indefinite, so $\lVert\Delta M\rVert_2$ is its largest $\lvert$eigenvalue$\rvert$, not its $\lambda_1$; (e) $\kappa$ is a worst case (S5: $\kappa$ 10.9, realized 0.910; U28: 126, realized 0.729); (f) "=" for the exact angle, "≈" with the dropped order for the linearization; (g) the ellipse is descriptive, no fraction of points inside (LM16); (h) a covariance-PCA share is a share of the sum of the sectors' variances, not of a portfolio's variance; (i) the eigenvalue bias of sample covariance matrices is left to LM30. Data: (j) $\kappa(C)\ne\kappa(\hat\Sigma)$; LM7's pair and 0050/00631L use other samples, said in X5's note; (k) partial 2026 and the excluded December 2008 are said; (l) compare eigenvectors across periods only by $\lvert\cos\theta\rvert$ (U28 halves: PC2's largest entry is OilGasElectricity in the first, ElectronicPartsComponents in the second, signed cosine −0.297); (m) never mix an aggregate with its members outside Section 6; (n) limit days (2025-04-07) are extreme, hence the 6.8% line; (o) hand examples use the printed 4-digit inputs, loadings three decimals, no "−0.000"; (p) price indices: say nothing about dividends' effect on the spectrum.

## LM12 Cholesky, SVD and Least Squares

**Prereq:** 7, 8, 9, 10, 11. **Leads:** 16, 18, 23, 27, 30, 32. Every number below is **provisional** until
`data/lm12_numbers.py` recomputes it and a second agent checks it (block "Numbers to verify").

**Owns.** Least squares as a projection (column space, normal equations, $\Pi$ symmetric and idempotent with trace =
columns, orthogonal residuals, intercept by centring, R-squared as $\cos^2\theta$); rank deficiency
($\hat{\boldsymbol\beta}+\operatorname{null}X$, minimum norm). Thin SVD via $M^{\top}M$; $\lambda_k=s_k^2$;
$\kappa(M)=s_1/s_N$, $\kappa(\tilde X^{\top}\tilde X)=\kappa(\tilde X)^2$; numerical rank at a stated tolerance;
pseudoinverse; `lstsq`, `pinv`, `matrix_rank`. Cholesky (conditions, uniqueness, recursion, failure when singular,
sequential least squares, triangular solves). Whitening and colouring real returns; mean $\lVert\mathbf z_t\rVert^2=N$.

**Leaves.** Standard errors, HAC, $t$/$F$ tests, adjusted R-squared, CAPM beta → LM23 · multivariate normal, chi-square
law of $\lVert\mathbf z_t\rVert^2$, unusual-day probabilities → LM16 · random generation, colouring draws, Monte Carlo
error → LM18 · Monte Carlo VaR → LM32 · reading components → LM11 · $T$ vs $T-1$ → LM20 · residual statistics → LM19 ·
shrinkage, ridge → LM24, LM30 · replicating portfolios, risk decomposition → LM27, LM29 · QR → none (named once).

**Uses before taught.** *R-squared:* "the share of the centred response's squared length the fit reproduces"
([[LM23]]) · *index arithmetic:* a market-value-weighted index's return is a weighted average of its members' returns,
weights set at the previous close, while members and shares stay fixed ([[LM8]]'s $\mathbf w^{\top}\mathbf R$; TWSE's
IndexS03: total market value over a base value, times the base level) · *machine precision:* about 16 significant digits, so a computed zero prints near $10^{-16}$ · *cyclic
trace* $\operatorname{tr}(KM)=\operatorname{tr}(MK)$, proved in one line in §2 · *standard normal draw* (§6 preview
only; [[LM16]], [[LM18]]) · *price limit ±10%*: re-cite Volume I (PITFALLS §7).

**Data role.** Repaired closes `data/processed/vol2_closes.parquet` (`data/vol2_series.py`), one common sample
2008-12-01 → 2026-10-08: $T=4{,}382$ daily simple returns from 2008-12-02. **U28** = the 28 leaf sector indices (30
TWSE sector ids minus Electronic and ChemicalBiotechnologyMedicalCare), regressed against TAIEX. Sub-samples: last 250
returns (2025-09-25 → 2026-10-08); calendar years 2009–2025 and 2026 to date (185); December 2008 (22 returns).
**S3** = Semiconductor, FinancialInsurance, Food; **S5** = S3 + Plastics, ShippingTransportation, in that order. §5
adds Electronic and its eight sub-industries (why aggregates leave U28); one problem uses LM7's printed 0050/00679B
moments. Price indices; nothing dropped or estimated; the lab repeats the repair cell.

**Hygiene declaration.** Every fit is **in-sample** (R-squared near 1 from an accounting identity, not a forecast);
per-year fits are a **stability check**, not out-of-sample; SVD, $L$, $\mathbf z_t$ use the full-sample $\hat\Sigma$:
**descriptive** ("most unusual day" is judged with later data). U28, S3, S5 were fixed by the editor before LM12 (say so).

**Notation** (local only; $\Pi$, $U,S,V,s_k$, $L$, $\mathbf z_t$, $\kappa$, $\theta$, $\mathbf y$, $\hat{\boldsymbol\beta}$ as AUTHORING §6).

| Symbol | Meaning | Check against §6 |
|:--|:--|:--|
| $T$; $k$; $m$ | number of returns (a count, never a horizon); index of $s_k$, $\lambda_k$; summation index in (12.8) | §6 lets a module pick the count; no $m_{ij}$ is written |
| $\hat\alpha$; $(\mathbf 1\ X)$; $\tilde{\mathbf y}$ | intercept $\bar y-\bar{\mathbf R}^{\top}\hat{\boldsymbol\beta}$; design with intercept, $T\times(N+1)$; $\mathbf y-\bar y\mathbf 1$ | not book-wide; declare |
| $\mathbf u_k$, $\mathbf v_k$ | columns of $U$, $V$; sign rule (largest $\lvert\cdot\rvert$ positive, first of ties) on $\mathbf v_k$, then $\mathbf u_k=M\mathbf v_k/s_k$ | bold; distinct from $u$, $v$ |
| $M^{+}$, $S^{+}$; $\kappa(M)$ | pseudoinverse ($S^{+}$ inverts the non-zero $s_k$); $s_1/s_N$ at full column rank, = LM11's $\lambda_1/\lambda_N$ on a PD matrix | new / extends §6; declare |
| $\delta$; $\operatorname{col}X$, $\operatorname{null}X$ | rank tolerance (count of $s_k>\delta s_1$); column space, null space (LM9's term) | new; never cite LM11's $\delta M$ |

Avoid "$R^2$" (clash with $R$; write "R-squared"; formulas use $\cos^2\theta$), $c$ for a covariance vector, $\epsilon$
for machine precision, $P$ or $H$ for the projection, $D$ for a diagonal matrix, "kernel", the set name "S15".

**Motivating case: "Can you rebuild TAIEX from its sectors?"** A desk analyst wants TAIEX's semiconductor content
without a weight file. Fit TAIEX's last 250 daily returns (25 September 2025 → 8 October 2026) on the U28 returns with
an intercept: R-squared 0.99912; Semiconductor 0.542, Electronic Parts 0.098, Financial 0.084, Computer Peripherals
0.054; the 28 sum to 0.990. On December 2008's 22 returns the same fit is exact, and stays exact with Semiconductor
removed. Which fit tells more, and why is the perfect one worthless? Resolved in §3 (coefficients = the weights that best
reproduce TAIEX's daily moves in the window) and §5 (rank). Scripts: `data/vol2_anchors.py` (d), `data/lm12_numbers.py`.

**Sections** (prose words; total 5,280).

| § | Title | Content | Words |
|:--|:--|:--|--:|
| 1 | Introduction | framing; case; `case` exhibit; roadmap; notation note (exempt); hygiene note | 420 |
| 2 | Least Squares as a Projection | E1 diagram first; column space; orthogonality ⇒ (12.1), LM10's gradient as a one-line second route; $\Pi$ (12.2), cyclic trace; centring (12.3); R-squared $=\cos^2\theta$ (12.4); pitfall: without an intercept R-squared is another number; E2; KC: why orthogonal to every column, not only to $\hat{\mathbf y}$? | 820 |
| 3 | Reading TAIEX from Its Sectors | the index identity and its conditions; coefficients as the best-reproducing weights in the window, never "the sector weights"; E3, E4; full-sample R-squared below every year's; small negatives are fitting noise; widget; 中文導讀 (§2–3); KC: why can a coefficient be slightly negative? | 650 |
| 4 | The Singular Value Decomposition | 2×2 picture; derivation from $M^{\top}M$ (LM11's spectral theorem); thin SVD; PCA link (12.5); conditioning (12.6), `cond` exhibit; why `lstsq` works on $\tilde X$; E5, E6; KC: $\kappa$ and $\lvert\det M\rvert$ from $s_1,s_2$ | 780 |
| 5 | Rank Deficiency, Numerical Rank and the Pseudoinverse | December 2008: 22×29, rank 22, null space of dimension 7; $\hat{\boldsymbol\beta}+\operatorname{null}X$; minimum-norm $X^{+}\mathbf y$ (12.7), Deep Dive: it is orthogonal to $\operatorname{null}X$; tolerance $\delta$; pitfall: `matrix_rank` "full" ≠ well determined; E7, E8; 中文導讀 (§4–5); KC: how many exact solutions has a 22×29 design of rank 22, and which does `lstsq` return? | 720 |
| 6 | Cholesky, Whitening and Colouring | 2×2 first: LM7's test ($h_{xx}>0$, $\det H>0$) is the existence condition; theorem (symmetric PD ⇒ unique lower-triangular $L$, positive diagonal; induction in a Deep Dive); (12.8); LM10's pivots are $l_{jj}^2$; sequential least squares; failure on December 2008's rank-21 $\hat\Sigma$; two triangular solves; whitening (12.9), mean $\lVert\mathbf z_t\rVert^2=N$ via $\mathbf z^{\top}\mathbf z=\operatorname{tr}(\mathbf z\mathbf z^{\top})$, order dependence; E9, E10; limit-day caveat; preview paragraph ([[LM16]], [[LM18]]); 中文導讀; KC: mean of $\lVert\mathbf z_t\rVert^2$ for 28 sectors, and why exactly | 760 |
| — | Summary | B's table "one return matrix, three factorizations" (question, factorization, result, NumPy call) + 5 bullets | 170 |
| — | Problems / Solutions | 12 problems | 360 / 600 |

**Exhibits.** `case` table (full / last 250 / December 2008: $T$, columns, rank, R-squared, sum; six largest last-250
coefficients) · `proj` vector (E1) · `coef` bar (28 last-250 coefficients, sorted, hline 0) · `drift` line, numeric year
axis 2009–2026 (Semiconductor, Financial, Electronic Parts, Computer Peripherals; 2026 partial) · `svd` vector (E5:
circle, ellipse `cov` $MM^{\top}$, $\mathbf v_k$, $s_k\mathbf u_k$) · `cond` table ($\kappa(\tilde X)$,
$\kappa(\tilde X^{\top}\tilde X)$, order of the gap between `lstsq` and the normal equations, response the centred TAIEX returns: S3, S5, U28
full, last 250, U28 + Electronic 2016)
· `rank` line, $k=1..9$, log y (standardized $s_k/s_1$, Electronic + eight, full vs 2016, hline $\delta=0.01$) · `dec08`
table (minimum-norm fit vs exact fit without Semiconductor) · `chol` table (S5's $L$, % a day) · `white` scatter, two
charts (Semiconductor vs Financial centred returns, $\hat\Sigma$ ellipse; $z_1$ vs $z_2$, unit circle; 7 April 2025
marked) · `apr7` table (S5 returns, $\mathbf z$ in two orders, $\lVert\mathbf z\rVert^2$, top-5 days).

**Widget** `taiexWeights`: two selectors (2009 … 2026, "last 250", "full sample") over a bar chart of the 28
coefficients, with R-squared and sum; `src/data/lm12-weights.json` from `data/lm12_charts.py`; initial state 2009, 2026.

**Examples.**

- E1 (§2) $\mathbf y=(1,3)^{\top}$ on $\mathbf x=(2,1)^{\top}$: $\hat{\mathbf y}=(2,1)^{\top}$, $\hat{\boldsymbol\varepsilon}=(-1,2)^{\top}$, $\mathbf x^{\top}\hat{\boldsymbol\varepsilon}=0$.
- E2 (§2) $x=(0,1,2,3)$, $y=(1,3,2,6)$: $\hat\beta=1.4$, $\hat\alpha=0.9$, residuals $(0.1,0.7,-1.7,0.9)$, R-squared $0.7=\cos^2\theta$.
- E3 (§3) case resolved: R-squared 0.99912, six largest coefficients, sum 0.990, 7 negatives (smallest −0.0081); without Semiconductor 0.856.
- E4 (§3) stability: Semiconductor 0.189 (2009) → 0.554 (2026), Financial 0.133 → 0.080; yearly R-squared ≥ 0.99800 vs full 0.98333.
- E5 (§4) $M=\begin{pmatrix}4&4\\-2&4\end{pmatrix}$: $M^{\top}M$ eigenvalues 36, 16; $\mathbf v_1=(1,2)^{\top}/\sqrt5$, $\mathbf v_2=(2,-1)^{\top}/\sqrt5$, $\mathbf u_1=(2,1)^{\top}/\sqrt5$, $\mathbf u_2=(1,-2)^{\top}/\sqrt5$; $\lvert\det M\rvert=24=6\cdot4$.
- E6 (§4) U28 by SVD: $s_1=0.05424$, $s_{28}=0.005218$, $\kappa(\tilde X)=10.40$, $\kappa(\hat\Sigma)=108.09$; last 250: 17.04, 290.2.
- E7 (§5) December 2008: rank 22 of 29; minimum-norm fit (Semiconductor 0.145, norm 0.285) vs exact fit without Semiconductor (Financial 0.218, norm 0.401).
- E8 (§5) Electronic + eight, standardized $s_9/s_1$: 0.0346 full, 0.00277 in 2016; rank 9 vs 8 at $\delta=0.01$, 8 and 8 at 0.1; `matrix_rank` default 9 every year.
- E9 (§6) Semiconductor–Financial: $l_{11}=0.015243$, $l_{21}=0.006998$, $l_{22}=0.009960$; $l_{21}/l_{11}=0.45908$ = slope; S3's $l_{33}=0.008594$ = Food's residual s.d. on the other two.
- E10 (§6) 7 April 2025, S5: returns −9.95, −9.89, −8.66, −9.90, −9.73%; $\lVert\mathbf z\rVert^2=89.30$ in both orders, largest of 4,382; mean exactly 5.

**Problems** (12; MC keys B, C, A). 1 MC false claim about $\Pi$ (**B** "$\Pi$ is invertible") · 2 MC meaning of
R-squared = 1 in December 2008 (**C** rank deficiency) · 3 MC which 2×2 has a Cholesky factor (**A** PD; others PSD
singular, indefinite) · 4 four-point line, residual checks · 5 $\Pi$ for $(1,1,0)^{\top}$, $\Pi^2=\Pi$, trace · 6 SVD of
an integer 2×2 without sign ties · 7 rank-one system, minimum-norm solution · 8 S5's printed $s_k$ → eigenvalues,
$\kappa(\tilde X)=3.481$, $\kappa(\hat\Sigma)=12.12$ · 9 Cholesky of LM7's $\Sigma$ from 20.1%, 13.5%, −0.11 (slope
−0.0739) · 10 whiten a 2-vector with 9's $L$ in both orders · 11 **Python** last-250 fit three ways, gap, $\kappa$ ·
12 **Python** per-year fits, Electronic + eight's rank at $\delta=0.01$. Numeric problems state divisor, units, order.

**Lab** (`build/make_lab12.py`). 0 data, repair cell (rule, count) · 1 projection, $\Pi^2=\Pi$, orthogonality,
$\cos^2\theta$ · 2 rebuild TAIEX: full, last 250, per year; widget JSON · 3 SVD: E5 vs `np.linalg.svd` (`Vh`);
$\lambda_k=s_k^2$; `cond` · 4 December 2008: rank, `pinv`, fit without Semiconductor; three tolerances · 5 Cholesky
recursion vs `np.linalg.cholesky`, sequential slopes, `LinAlgError` · 6 whitening, colouring, ranking, order ·
7 extension: colour `default_rng(20261011)` draws with S5's $L$ (Frobenius gap 0.0250); its size → [[LM18]].

**Cross-module tags.** (12.1) $X^{\top}X\hat{\boldsymbol\beta}=X^{\top}\mathbf y$, $X^{\top}\hat{\boldsymbol\varepsilon}=\mathbf 0$
→ LM23 · (12.2) $\Pi^{\top}=\Pi=\Pi^2$, $\operatorname{tr}\Pi$ = columns → LM23 · (12.3)
$\hat\Sigma\hat{\boldsymbol\beta}=\tilde X^{\top}\tilde{\mathbf y}/T$, $\hat\alpha=\bar y-\bar{\mathbf R}^{\top}\hat{\boldsymbol\beta}$
→ LM23, LM27 · (12.4) R-squared $=\cos^2\theta=\lVert\hat{\mathbf y}-\bar y\mathbf 1\rVert^2/\lVert\tilde{\mathbf y}\rVert^2$
→ LM23 · (12.5) $\tilde X/\sqrt T=USV^{\top}\Rightarrow\hat\Sigma=VS^2V^{\top}$ → LM11, LM30 · (12.6) $\kappa(\tilde X^{\top}\tilde X)=\kappa(\tilde X)^2$
→ LM23, LM29, LM30 · (12.7) $M^{+}=VS^{+}U^{\top}$, $X^{+}\mathbf y$ → LM30 · (12.8) $l_{jj}=(\hat\sigma_{jj}-\sum_{m<j}l_{jm}^2)^{1/2}$,
$l_{ij}=(\hat\sigma_{ij}-\sum_{m<j}l_{im}l_{jm})/l_{jj}$ → LM16, LM18 · (12.9) $\mathbf z_t=L^{-1}(\mathbf R_t-\bar{\mathbf R})$,
$\tfrac1T\sum_t\mathbf z_t\mathbf z_t^{\top}=I_N$, $\lVert\mathbf z_t\rVert^2=(\mathbf R_t-\bar{\mathbf R})^{\top}\hat\Sigma^{-1}(\mathbf R_t-\bar{\mathbf R})$ → LM16, LM18, LM32.

**Pitfalls to pre-empt.**

- Coefficients ≠ market-value weights (unverified; the identity needs fixed members and shares); never "replicating
  portfolio". The 0.990 sum and the −0.013%-a-day intercept are **unexplained**: no causal story (PITFALLS §7).
- R-squared $=\cos^2\theta$ only with an intercept. December 2008's 1 is rank, not fit: residual "zero to machine precision".
- A second exact fit from an `svd` null vector is not reproducible (null space of dimension 7, any basis): use the two unique fits.
- $\kappa$ squaring is real but harmless here: `lstsq` and normal equations agree to about $10^{-15}$ (U28) and
  to between $10^{-12}$ and $10^{-11}$ (U28 + Electronic, 2016); the gap depends on the machine, so print its order. Say digits lost ≈ $\log_{10}\kappa^2$; never claim the normal equations fail on these data.
- Scale and $\delta$ change numerical rank ($s_9/s_1$ 0.0346 standardized, 0.0329 covariance scale): state both.
- `eigh` sorts ascending, `svd` descending and returns $V^{\top}$; `scipy.linalg.cholesky` gives the upper factor.
- $\mathbf z_t$ depends on asset order, $\lVert\mathbf z_t\rVert^2$ does not. 7 April 2025 is a limit-down day: capped
  returns make the squared length understate the shock. Check 2026-07-31 and 2026-07-17 (2nd, 5th) before a top-5 table.
