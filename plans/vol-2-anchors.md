# Volume II — anchor numbers

Every number the Volume II briefs (`plans/vol-2.md`) quote, with the definition that reproduces it. The values come
from the editor's exploratory scripts; an independent recomputation on 2026-10-11 checked them, and the status line
of each module records the result. Each module's own `data/lmNN_numbers.py` must print and assert every
value it uses (AUTHORING §8). Sample conventions: `plans/vol-2.md`, "Universe and sample".

## LM8

**Status.** Recomputed independently on 2026-10-11: 111 of 113 values matched; the two U28 correlations below are
corrected, and the definitions the check found ambiguous are now stated.

Case: TX = `raw/TX__2025-04-01__2025-10-31.csv`, `contract_date` 202504, `settlement_price`; 0050, 00679B = `close`
from their raw chunks; dates 2025-04-02, 07, 08, 09, 10, 11; exact decimals; $\mathbf h=(-1,24000,100000)$, TX price
$=200F$, $W_0=10^7$.

- TX settlement 21,296 / 19,167 / 18,169 / 17,184 / 18,902 / 19,543; volume 66,423 / 2,736 / 152,423 / 176,779 /
  2,382 / 132,834. 0050 176.00 / 158.40 / 153.25 / 146.20 / 160.80 / 164.55. 00679B 29.88 / 30.42 / 29.33 / 28.10 /
  28.91 / 27.88.
- 7 Apr returns: TX −9.997183%, 0050 −10.000000%, 00679B +1.807229%; TAIEX −9.699731% (anchors 456).
- Line P&L 7 Apr $h_i\Delta P_i$: +425,800; −422,400; +54,000; total +57,400 (0.574% of $W_0$).
- Daily book P&L $Y\mathbf h$: +57,400; −33,000; −95,200; +87,800; −141,200; week −124,200 $=\mathbf h^{\top}(\mathbf P_{11}
  -\mathbf P_{2})$.
- Values on 2 Apr $h_iP_i$: −4,259,200; 4,224,000; 2,988,000; net 2,952,800; gross 11,471,200. $\mathbf f=(-0.42592,
  0.4224, 0.2988)$; $\mathbf 1^{\top}\mathbf f=0.29528$; $\lVert\mathbf f\rVert_1=1.14712$; $\mathbf f^{\top}\mathbf R_{7\,
  \text{Apr}}=0.00574$ exactly.
- Drift: true 8 Apr return $\Delta W_{8}/(W_0+57{,}400)=-0.328117\%$; $\mathbf f^{\top}\mathbf R_{8\,\text{Apr}}=
  -0.226276\%$.
- $X\mathbf w$ (0050, 00679B weights): 60/40 daily −5.2771, −3.3840, −4.4377, +7.1448, −0.0259%; sum −5.9798%;
  compounded $\prod(1+R)-1=-6.3194\%$. 50/50 sum −6.0915%, compounded −6.3284%. 100% 0050 sum −5.5332%, comp −6.5057%.
- Week correlations (five returns, centred cosine): TX/0050 0.9912 (7.63°); 0050/00679B 0.2526 (75.37°), uncentred
  0.2930; TX/00679B 0.2802 (73.73°).
- $\lVert(0.6,0.4)-(0.5,0.5)\rVert=0.141421$.
- 0050/00679B, `lm07_returns.parquet` `R_0050`, `R_00679B`, rows with both, $T=2{,}363$: $\rho=-0.105632$, 96.064°,
  uncentred cosine −0.105699; $s\sqrt A$ with $A=243.0543$, divisor $T$: 20.106%, 13.496%; 42.3/57.7 daily-rebalanced
  mix with $w=0.423$ as printed $s_p\sqrt A=10.908\%$, bound 16.292% (LM7's unrounded $w^*$ gives 10.909%, 16.293%); 50/50 11.501% vs 16.801%.
- 0050/00631L, `etf_daily_returns.parquet` `R_0050`, `R_00631L`, $T=2{,}902$: $\rho=0.974365$, 13.001°,
  $\sqrt{2(1-\rho)}=0.2264$; $\mathbf x_{00631L}-2\mathbf x_{0050}$ RMS 0.5577% a day; norm ratio 1.9357 (both uncentred; centred 0.5575%, 1.9362).
- U28 on `vol2_closes.parquet` closes 2008-12-01 → 2026-10-08 (4,383 closes, $T=4{,}382$ simple price returns,
  `np.corrcoef`): 378 pairs; max ElectronicPartsComponents/ComputerPeripheralEquipment 0.754715 (40.999°,
  $\sqrt{2(1-\rho)}=0.7004$); min BiotechnologyMedicalCare/OilGasElectricity 0.217481 (77.439°, 1.2510); median
  0.5015. Semiconductor/FinancialInsurance 0.574858 (54.91°; uncentred 0.575796); Semiconductor/Food 0.403495
  (66.20°); FinancialInsurance/Food 0.59584 (53.43°).
- S3 equal-weight daily-rebalanced mix, U28 sample: $s$ (divisor $T$) 1.0527% a day; $\sum_iw_is_i=1.2721\%$
  (Semiconductor 1.5243%, FinancialInsurance 1.2173%, Food 1.0747%).
- Identity check, Semiconductor/FinancialInsurance, each centred and divided by its $s$ (divisor $T$): squared distance
  of the two standardized vectors $=2T(1-\rho)=3{,}725.94$.
- Variant book $(-1, 20000, 100000)$: 7 Apr P&L +127,800; week $\mathbf h^{\top}(\mathbf P_{11}-\mathbf P_{2})=-78{,}400$.
- Checked in the recomputation and quoted by the brief: Problem 2's book $(+2, 0, 200{,}000)$ on 8 Apr gives
  $2\times200\times(18{,}169-19{,}167)+200{,}000\times(29.33-30.42)=-617{,}200$; ex-dates 0050 2025-01-17 and 2025-07-21,
  00679B 2025-02-21 and 2025-05-22; 0050's split on 2025-06-18 (raw close 188.65 on 2025-06-10, 47.57 on 2025-06-18);
  TX 202504 expires 2025-04-16; 7 April 2025 is a Monday after the 3–4 April holidays; TAIEX's −9.699731% is the
  largest absolute daily return of 2007-07-02 → 2026-10-08; 0050/00679B price returns on their own common dates, split
  day excluded: $\rho=-0.104998$, $T=2{,}362$; `158.4/176.0 - 1` prints −0.09999999999999998 and
  `(158.4 - 176.0)/176.0` prints −0.09999999999999996.

## LM9

**Status.** Recomputed independently on 2026-10-11: 25 of 27 rows matched; row 3 is corrected and row 17 reworded.

Inputs: `data/processed/vol2_closes.parquet` (built by `data/vol2_series.py`); returns on the TAIEX calendar,
$100(P_t/P_{t-1}-1)$, rounded to 2 decimals; systems use the rounded values in exact rational arithmetic; columns in
order Semiconductor, FinancialInsurance, Food; $\mathbf b$ = TAIEX.

| # | Number | Definition | Value |
|--:|:--|:--|:--|
| 1 | four-day returns, % (TAIEX, Semi, Fin, Food) | 7 Apr (from 2 Apr close) / 8 / 9 / 10 Apr 2025 | −9.70, −9.95, −9.89, −8.66 / −4.02, −3.99, 0.53, 3.77 / −5.79, −4.47, −5.61, −4.17 / 9.25, 9.91, 8.36, 5.72 |
| 2 | TAIEX 7 Apr unrounded | 19232.35/21298.22 − 1 | −9.699731% (anchor, block (h)) |
| 3 | nearest rounding tie | min distance of an unrounded % return from a .xx5 value | Food 8 Apr 3.774862 (0.000138 away; next Semiconductor 8 Apr −3.994467, 0.000533); half-up and half-even rounding agree on all 16 inputs; no repair on these dates in `vol2_repairs.json` |
| 4 | E1 (8–9 Apr; Semi, Fin) | $\det$, $\mathbf x$, angle between columns | 24.753 exactly; (1.035062, 0.207357); 47.15° |
| 5 | nearly parallel pair (7, 9 Apr; Semi, Food) | $\det$, $\mathbf x$, angle | 2.7813 exactly; (−3.48485, 5.12404); 1.52° |
| 6 | 7–9 Apr system | $\det M$ | −71.591922 (= −35795961/500000) |
| 7 | 7–9 Apr elimination | multipliers $l_{21},l_{31},l_{32}$; rows after step 1; final row 3 | 0.401005, 0.449246, −0.259557; (0, 4.495940, 7.242704 ∣ −0.130251), (0, −1.166955, −0.279528 ∣ −1.432312); (0, 0, 1.600370 ∣ −1.466119) |
| 8 | 7–9 Apr pivots | diagonal after elimination (no swap needed; partial pivoting picks the same) | −9.95, 4.495940, 1.600370; product −71.591922 |
| 9 | 7–9 Apr solution | $\mathbf x$, sum | (0.334105, 1.446834, −0.916113); 0.864827 |
| 10 | Cramer numerators, 7–9 Apr | $\det M_j(\mathbf b)$, $j=1,2,3$ | −23.919201, −103.581657, 65.586258 |
| 11 | $M^{-1}$, 7–9 Apr | rows | (−0.264549, −0.102544, 0.456693), (0.467793, −0.038849, −1.006607), (−0.345751, 0.162186, 0.624855); float $\max\lvert MM^{-1}-I\rvert$ about $10^{-16}$ (not printed) |
| 12 | other triples | $\det$, $\mathbf x$ | 7–8–10: 22.568247, (1.66166, −1.47925, 0.90027); 7–9–10: −29.587887, (0.10674, 1.36070, −0.55651); 8–9–10: 49.300524, (−0.01793, 2.06932, −1.37620) |
| 13 | Financial's range over triples | min/max of $x_2$ over the four triples | −1.47925 to 2.06932 |
| 14 | 7–9 multiples applied to 10 Apr | $(9.91, 8.36, 5.72)\cdot\mathbf x$ vs 9.25 | 10.16635 (+10.17%) |
| 15 | 7–8 Apr line | reduced echelon form | $x_1=1.003671+0.730877x_3$, $x_2=-0.028971-1.610943x_3$; $\mathbf x_h=(0.730877,-1.610943,1)$ |
| 16 | four days | ranks; $\det[M\mid\mathbf b]$ (4×4) | 3 and 4; 65.603260 (= 65.60326017) |
| 17 | mix column, 7–9 Apr | $(\mathbf m_1+\mathbf m_2)/2$; rank $M$, rank $[M\mid\mathbf b]$; $\mathbf x_h$ | (−9.92, −1.73, −5.04); 2, 3; $(-\tfrac12,-\tfrac12,1)$; float det 3.97e-14 and `solve` entries of order $10^{15}$ (largest 1.65e15) on this machine (NumPy 2.5.3), not to print |
| 18 | problem 4 (7, 10 Apr; Semi, Food) | $\det$, $\mathbf x$ | 28.9066; (0.85174, 0.14147) |
| 19 | LM7 inverse | from $\sigma_1^2=0.040425$, $\sigma_2^2=0.018214$, $\sigma_{12}=-0.002866$, excess (0.22751, −0.02547) | $\det\Sigma=7.28087\times10^{-4}$; $\Sigma^{-1}$ = ((25.0162, 3.9363), (3.9363, 55.5222)); $\mathbf f^*=(5.5912,-0.5186)$ = LM7's (5.59, −0.52) |
| 20 | common sample | dates and returns, 2008-12-01 → 2026-10-08 | 4383 dates, $T=4382$, first return 2008-12-02 |
| 21 | 50/50 mixes, Semi + Fin | `matrix_rank` of [R_S, R_F, mix] | daily rebalanced 2; buy-and-hold (start 2008-12-01) 3 |
| 22 | buy-and-hold weight in Semi | $0.5\,(P_{S,t}/P_{S,0})/V_t$, $V_t$ the mix value | 0.50 → 0.8580 at 2026-10-08; max 0.8833 (2026-05-25), min 0.4571 (2011-08-04) |
| 23 | largest daily gap | $\max_t\lvert R^{\text{reb}}_t-R^{\text{bh}}_t\rvert$ | 2.5675 percentage points |
| 24 | U28 rank | `matrix_rank` of the $4382\times28$ return matrix | 28 (no nulls) |
| 25 | Electronic + 8 | `matrix_rank` of $4382\times9$; corr(Semi, Electronic) | 9; 0.952591 |
| 26 | cost chart | $n!$, $(n+1)!$, $\tfrac23n^3$ | $n=3$: 6, 24, 18; $n=20$: $21!=51{,}090{,}942{,}171{,}709{,}440{,}000$, 5,333 |
| 27 | MTX vs TX | multipliers; null vector per contract | 50 and 200 NT\$ per point (TAIFEX contract specifications); $\mathbf x_h=(-\tfrac14,1)$ |

Facts checked on official sources (2026-10-11, `project/SOURCES.md`): MTX pays NT\$50 per TAIEX point and TX
NT\$200, on the same index with the same final settlement (TAIFEX contract specifications); `Electronic` covers the
eight electronics sub-industries created on 2007-07-02, and the sector indices are market-value-weighted price indices
(TWSE news of 2007-06-27; IndexS03.pdf); `numpy.linalg.solve` calls LAPACK `_gesv`, an LU factorization with partial
pivoting (LAPACK's DGESV documentation), and refuses non-square input (error text: "Last 2 dimensions of the array must be square"); solving through
the inverse costs more and has weaker error bounds (Higham 2002a, ch. 14); Strang 2016, 5th ed.

## LM10

**Status.** Recomputed independently on 2026-10-11: all 36 rows reproduced; row 30 now separates $C$ from $\hat\Sigma$,
and rows 5, 13, 17 and 35 state their definitions. Row 30 then moved to one-session ETF returns (an ETF column of a
two-fund frame inherits the other fund's halts, PITFALLS §3), and rows 25 and 29 follow it; the editor and an
independent check agree on all three.

U28 sample: closes of the 28 leaf sectors from `vol2_closes.parquet`, dates 2008-12-01..2026-10-08; $R_t=P_t/P_{t-1}-1$ on consecutive rows; $\hat\Sigma$ with `ddof=0`; $A=T/\text{years}$, years = (2026-10-08 − 2008-12-01 in days)/365.25. Annualized volatility $=s\sqrt A$.

| # | Number | Definition | Value |
|--:|:--|:--|--:|
| 1 | $T$, first return, years, $A$ | U28 sample | 4,382; 2008-12-02; 17.85078713; 245.4793712 |
| 2 | repaired U28 closes | entries of `vol2_repairs.json` "repairs" with series in U28 and date in [2008-12-01, 2026-10-08]; distinct dates | 524; 38 |
| 3 | min / max sector volatility | $s_i\sqrt A$ | 13.67% CommunicationsInternet; 35.31% GlassCeramic |
| 4 | mean of 28 volatilities | $\frac1{28}\sum_is_i\sqrt A$ | 21.94% |
| 5 | EW book volatility | $\sqrt{A\,\mathbf w^{\top}\hat\Sigma\mathbf w}$, $\mathbf w=\mathbf 1/28$ (= $\sqrt A\cdot$ std(`X @ w`, ddof=0); the difference is below 1e-15 and never printed) | 15.75% |
| 6 | sectors below the book | count of $s_i\sqrt A<15.75\%$ | 1 |
| 7 | TAIEX volatility | TAIEX closes, same dates | 17.82% |
| 8 | variances-only volatility | $\sqrt{A\sum_iw_i^2s_i^2}$ | 4.22% |
| 9 | off-diagonal share | $\sum_{i\ne j}w_iw_j\hat\sigma_{ij}/\mathbf w^{\top}\hat\Sigma\mathbf w$ | 92.8% |
| 10 | $\overline{\operatorname{var}}$, $\overline{\operatorname{cov}}$ (daily) | mean diagonal; mean of 756 off-diagonal entries | 2.0328e-4; 9.7254e-5 |
| 11 | limit | $\sqrt{A\,\overline{\operatorname{cov}}}$ | 15.45% |
| 12 | mean off-diagonal correlation | mean of 756 off-diagonal entries of $C$ | 0.502 (context only) |
| 13 | divisor effect | factor $\sqrt{T/(T-1)}$ on a volatility | 1.000114 (a relative change of 0.0114%, not percentage points) |
| 14 | S3 $A\hat\Sigma_3$ (%²) | $10^4A\hat\Sigma$ for (Semiconductor, FinancialInsurance, Food), to 0.1 | 570.3, 261.8, 162.3; 363.7, 191.3; 283.5 |
| 15 | S3 volatilities; correlations | $\sqrt{A\hat\sigma_{ii}}$; $C_{12},C_{13},C_{23}$ | 23.88, 19.07, 16.84%; 0.575, 0.403, 0.596 |
| 16 | $C_3$ leading minors, pivots | from the 3-decimal entries | 1, 0.669375, 0.427966; 1, 0.6694, 0.6394 |
| 17 | mix $(0.5,0.3,0.2)$ | computed $\hat\Sigma_3$: $\sqrt{A\mathbf w^{\top}\hat\Sigma_3\mathbf w}$; $\mathbf w^{\top}(\text{vols})$; grid total in %² | 17.91%; 21.03%; 320.62 |
| 18 | X5 cells (%²) | $10^4Aw_iw_j\hat\sigma_{ij}$, to 0.01 | 142.58, 39.27, 16.23; 32.74, 11.48; 11.34 (sum of all nine 320.62) |
| 19 | E2 returns | Semiconductor, FinancialInsurance on 2025-04-07/08/09 vs previous close (2025-04-02), % to 0.01 | −9.95, −3.99, −4.47; −9.89, +0.53, −5.61 |
| 20 | E2 from printed | means; $\hat\Sigma$ ($\times10^{-4}$, $T=3$); $\rho$ | −6.1367%, −4.99%; 7.3092, 9.8339, 18.2883; 0.851 |
| 21 | E7 matrix | E3 block + third row $(0.5(570.3+261.8),\ 0.5(261.8+363.7),\ 0.25\cdot570.3+0.5\cdot261.8+0.25\cdot363.7)$; $2\times2$ minors; det | 416.05, 312.75, 364.4; 138,878.87, 34,719.7175, 34,719.7175; 0 |
| 22 | E7 rounded | det of the computed 50/50 matrix with entries rounded to 0.1 (416.1, 312.8, 364.4) | −13,888.91 |
| 23 | rank windows | `matrix_rank(np.cov(X[-T:], rowvar=False, ddof=0))` for $T=20..35$, asserted $=\min(T-1,28)$; first dates | $T=28$: 27 from 2026-08-28; $T=29$: 28 from 2026-08-27 |
| 24 | collinear | S5 + its EW series: rank; $\lvert\mathbf v^{\top}\hat\Sigma\mathbf v\rvert$, $\mathbf v=(\frac15,\dots,\frac15,-1)$ | 5; below 1e-15 |
| 25 | E9 correlations | one-session total returns (row 30), per calendar year, each pair on its common dates: 0050/00631L 2018; 0050/00679B 2023; 00631L/00679B 2019; $T_{ij}$ | 0.982 (247); 0.199 (239); −0.444 (242) |
| 26 | E9 det, form | from the 3-decimal entries; $\mathbf x=(-1,1,1)$ | −0.374592; −0.25 |
| 27 | witnesses | $\det C\cdot\operatorname{adj}(C)_{jj}$, $j=1,2,3$ | −0.3007, −0.3598, −0.0134 |
| 28 | 2018 common triple | all three ETFs on 2018 common dates ($T=247$); det of 3-decimal matrix | 0.982, −0.394, −0.395; 0.0301 |
| 29 | failing assignments | ordered triples of distinct years 2017–2026 for the three pairs with $\det<0$, on row 25's one-session returns (full-precision or 3-decimal correlations alike) | 362 of 720 |
| 30 | real pairwise case | U28 + one-session total returns of 0050, 00631L and 00679B (between consecutive TAIEX-calendar dates on which the fund has both closes, from its raw closes and dividends; halt-spanning returns drop out) on U28 dates: common $T$ and dates; pairwise $T$ range; smallest eigenvalue of the pairwise $C$ (each pair standardized on its common dates), of the pairwise $\hat\Sigma$ (each variance on the series' own returns, each covariance on the pair's common dates with that pair's means, divisor the pair's count), of the common-sample $C$ and $\hat\Sigma$; largest entries of the eigenvector of the negative eigenvalue (sign rule); U28 plus one ETF; Semiconductor's variance on its own sample and on 00631L's dates; largest entry change of $C$ | 2,357, 2017-01-18..2026-10-08; 2,362..4,382; 0.01380; −6.56e-06 (not PSD); 0.01337, 3.55e-06; Semiconductor 0.656, 00631L −0.454, 0050 −0.362; +0050 −2.35e-06, +00631L −4.85e-06, +00679B +2.72e-05; 2.3234e-4 vs 2.5076e-4 (00631L's 2,906 dates); 0.144 ElectronicProductsDistribution/TradingConsumersGoods (0.465 vs 0.321) |
| 31 | E10 | $\mathbf g=2A\hat\Sigma\mathbf w$ EW U28: entries GlassCeramic, CommunicationsInternet (also the max and min of $\mathbf g$); $\boldsymbol\Delta^{\top}\mathbf g$; $A\boldsymbol\Delta^{\top}\hat\Sigma\boldsymbol\Delta$; variance; volatility | 0.07230, 0.02764; −0.001595; +0.000136; 0.024803 → 0.023345; 15.75% → 15.28% |
| 32 | Problem 4 | $(0.2,0.3,0.5)$ from 3-decimal $C_3$ and 2-decimal volatilities | 15.74% |
| 33 | Problem 5 | S5 $\overline{\operatorname{var}}$, $\overline{\operatorname{cov}}$; EW S5 volatility; limit | 2.0740e-4, 9.0696e-5; 16.73%; 14.92% |
| 34 | Problem 6 | printed $A\hat\Sigma_3$: leading minors; pivots | 570.3, 138,878.87, ≈25,178,038; 570.3, 243.52, 181.29 |
| 35 | Problem 9 | printed $A\hat\Sigma_3$, $\boldsymbol\Delta=(-0.05,0,0.05)$: $2A\hat\Sigma\mathbf w$; linear; quadratic; variance; volatility | 0.0792, 0.0557, 0.0390; −0.002009; +0.000132; 0.032060 → 0.030184 (the printed matrix gives 320.60 %², row 17's computed one 320.62); 17.91% → 17.37% |
| 36 | lab extension | per calendar year (2009–2025, 2026 to 2026-10-08, $T_y=185$): EW volatility ÷ mean sector volatility | 0.563 (2017) … 0.809 (2020) |

## LM11

**Status.** Recomputed independently on 2026-10-11: 23 of 25 rows matched; rows 21 and 24 are corrected, and row 25
moved to LM8's sample of 0050/00631L (the price-return value 59.04 is dropped).

Common definitions. **U28 sample**: `vol2_closes.parquet`, rows with date ≥ 2008-12-01, the 28 leaf columns; $R_{i,t}=P_{i,t}/P_{i,t-1}-1$ between consecutive rows; $T=4{,}382$; $\hat\Sigma=\tilde X^{\top}\tilde X/T$; $C$ from $\hat\Sigma$; eigenvalues descending; sign rule with tie-break. **Halves**: first 2,191 returns and the last 2,191. **Year** $y$: returns dated in $y$. $\kappa$ = $\lambda_1/\lambda_N$ (= `np.linalg.cond`).

| # | Number(s) | Definition | Value |
|:--|:--|:--|:--|
| 1 | $T$, first/last return, $A$ | U28 sample; $A=T/$(days from 2008-12-01 to 2026-10-08 / 365.25) | 4,382; 2008-12-02, 2026-10-08; 245.4794 |
| 2 | min/max pairwise correlation, $\bar\rho$ | off-diagonal of U28 $C$ | 0.2175 Biotech/OilGas; 0.7547 Computer/Parts; 0.50227 |
| 3 | $\lambda_1$, shares | U28 $C$; $\lambda_k/28$; first $k$ with cumulative ≥ 0.80 | 14.7214; 52.58%; $k=12$, 80.93% |
| 4 | PC1 range; PC2 signs | entries of $\mathbf q_1$, $\mathbf q_2$ of U28 $C$ | 0.1302 OilGas to 0.2238 Other; 11 positive (8 electronics + Biotech, Chemical, ElectricMachinery), 17 negative |
| 5 | yearly share extremes | $\lambda_1/28$ of each year's $C$, 2009–2026 | max 2020 66.62%, min 2017 34.52% |
| 6 | 2025-04-07 | U28 returns that day | all negative; min −9.953% Semiconductor, max −5.898% CommunicationsInternet |
| 7 | same-sign days | dates with all 28 $R>0$ or all $<0$ (zero breaks) | 300 (144 up, 156 down), 6.85%; 415 dates have a zero |
| 8 | halves $\mathbf x$ | `solve`($\hat\Sigma^{(h)}$, $\mathbf 1$), daily units | Semi 430.84 → −587.60; Fin −2,547.30 → 2,216.20 |
| 9 | halves change | $\lVert\mathbf x^{(2)}-\mathbf x^{(1)}\rVert/\lVert\mathbf x^{(2)}\rVert$; cosine | 0.7286; 0.6902 |
| 10 | bound U28 | $\kappa(\hat\Sigma^{(1)})$; $\lVert\hat\Sigma^{(2)}-\hat\Sigma^{(1)}\rVert_2/\lVert\hat\Sigma^{(1)}\rVert_2$; product | 126.05; 0.24536; 30.93 ($\kappa(\hat\Sigma^{(2)})=119.40$) |
| 11 | (11.7) shares | $(\mathbf q_k^{\top}\mathbf 1/\lambda_k)^2/\lVert\mathbf x\rVert^2$ with $\hat\Sigma^{(h)}$'s eigenpairs; $k=1$; $k=15..28$ | 1.80%, 1.02%; 72.03%, 80.48% |
| 12 | halves PCA | U28 $C^{(h)}$: $\lambda_1$, share; $\lvert\mathbf q_k^{(1)\top}\mathbf q_k^{(2)}\rvert$, $k=1..5$ | 16.116/13.787, 57.56%/49.24%; 0.9971, 0.2966, 0.1206, 0.0431, 0.4279 |
| 13 | plane measure | $\lVert[\mathbf q_2^{(1)}\ \mathbf q_3^{(1)}]^{\top}\mathbf q_2^{(2)}\rVert$; PC2 largest entries per half | 0.9274; OilGasElectricity / ElectronicPartsComponents, signed cos −0.2966 |
| 14 | per year | $\lvert\cos\rvert$ of year's $\mathbf q_1$, $\mathbf q_2$ with full sample; plane measure (the year's $\mathbf q_2$ on the full sample's $\mathbf q_2$, $\mathbf q_3$ plane, as row 13); $\lambda_2-\lambda_3$ | PC1 ≥ 0.981 (2026), PC2 0.119 (2016) to 0.946 (2025); plane 0.690 (2020) to 0.959 (2024); min gap 2022 0.029 |
| 15 | $\kappa$ ladder | $\kappa(C)$, $\kappa(\hat\Sigma)$ | LM7 1.2362, 2.2851; Semis/Fin 3.7043, 4.0337; S3 5.8823, 7.0449; S5 8.5162, 12.1177; U28 70.637, 108.085; Elec+8 836.3, 925.3; all 30 2,265.7, 2,410.7 |
| 16 | E1 | Semis/Fin $\hat\Sigma\times10^4$ entries $(\hat\sigma_{11},\hat\sigma_{22},\hat\sigma_{12})$; (11.2) on 4-digit inputs; $\mathbf q_1$ angle; ann. vol; $\rho$ | 2.3234, 1.4817, 1.0666; 3.0492, 0.7559; 34.23°; 23.88%, 19.07%; 0.5749 |
| 17 | E2 | LM7: `lm07_returns.parquet` R_0050, R_00679B (nulls dropped), $\Sigma=243.0543\,\hat\Sigma$ | $T=2{,}363$; 0.040789, 0.017850; $\mathbf q_1=(0.9920,-0.1260)$; −7.236°; 20.196%, 13.360%; factor 0.3912; $\rho=-0.1056$ |
| 18 | E3 | S3 $\hat\Sigma\times10^4$ eigenvalues; $\lambda_1/\operatorname{tr}$ | 3.4728, 0.9944, 0.4929; 70.01% |
| 19 | E4 | $1+27\bar\rho$ vs $\lambda_1$ | 14.5613 ≤ 14.7214 |
| 20 | E6 / X8 | covariance PCA U28: shares 1, 2; $\lvert\cos\rvert$ cov-PC1/corr-PC1; largest cov-PC2 entry; Semis×100 test | 51.70%, 5.88%; 0.9791; GlassCeramic 0.667 (ann. vol 35.31%, the highest); $(0.99999,0.00459)$, 99.996% |
| 21 | E7, X9 | Elec+8 $C$ $\lambda_9$, $\mathbf q_9$; all-30 two smallest eigenvalues and top entries | 0.0073 (0.007298), 0.828/−0.529; 0.00711 (Electronic 0.826, Semi −0.530), 0.01517 (ChemBio 0.771, Chemical −0.473, Biotech −0.425) |
| 22 | E8 | $\tfrac12\arctan(2\varepsilon/\text{gap})$ and $\varepsilon/\text{gap}$, $\varepsilon=0.05$ | gap 0.33676: 8.269°, 8.507°; gap 0.035826: 35.145°, 79.963° |
| 23 | E9 | $C(\rho)^{-1}\mathbf e_1$; $\lVert\Delta\mathbf x\rVert/\lVert\mathbf x+\Delta\mathbf x\rVert$; $\kappa\cdot0.01/1.95$ | (10.2564, −9.7436), (12.7551, −12.2449); 0.199958; 0.2 |
| 24 | P4, P5, P6, P11 | as in Problems; Plastics/Food $\hat\Sigma\times10^4$ | P5 from the printed $(\hat\sigma_{11},\hat\sigma_{22},\hat\sigma_{12})=(2.5228,1.1550,0.7180)$: 2.8305, 0.8473, $\mathbf q_1=(0.919,0.394)$, 76.96%, 3.3405 (full precision 0.8474, 3.3404); S5 $C$ 2.8633, 0.6674, 0.5895, 0.5436, 0.3362, $\bar\rho=0.46216$ |
| 25 | P9, P10 | $(1+\rho)/(1-\rho)$, $\rho=0.974365$ (0050/00631L total returns, `etf_daily_returns.parquet`, $T=2{,}902$, LM8's sample); S5 halves as rows 9–10 | 77.018; 10.863 × 0.44235 = 4.805, realized 0.9105, cosine 0.4187 |

## LM12

**Status.** Recomputed independently on 2026-10-11: 29 of 31 rows matched; rows 13 and 16 now state machine
precision instead of a digit, row 30 states its centring, and rows 32–33 were added for the `cond` and `chol` tables.

Common definitions: closes from `data/processed/vol2_closes.parquet`, dates 2008-12-01 … 2026-10-08; $R_t=P_t/P_{t-1}-1$;
$T=4{,}382$ (first return 2008-12-02). "Fit" = least squares of TAIEX's $R_t$ on the U28 returns with an intercept
(`lstsq` on $(\mathbf 1\ X)$); R-squared $=1-\lVert\hat{\boldsymbol\varepsilon}\rVert^2/\lVert\tilde{\mathbf y}\rVert^2$;
$\hat\Sigma$ with divisor $T$; $\tilde X$ centred. Years by calendar year of the return date.

| # | Number | Definition | Value |
|--:|:--|:--|:--|
| 1 | last-250 window | last 250 returns of the sample | 2025-09-25 → 2026-10-08 |
| 2 | last-250 R-squared ($=\cos^2\theta$) | fit on the last 250 | 0.99912119 |
| 3 | last-250 coefficients | Semiconductor, ElectronicPartsComponents, FinancialInsurance, ComputerPeripheralEquipment, OtherElectronic, CommunicationsInternet | 0.542284, 0.097593, 0.083770, 0.054491, 0.046945, 0.038280 |
| 4 | last-250 sum of slopes; intercept | sum of the 28 slopes; $\hat\alpha$ | 0.99033451; −1.290574e-4 |
| 5 | last-250 negatives | count of slopes < 0; smallest (InformationService) | 7; −0.008120 |
| 6 | last-250 without Semiconductor | R-squared of the fit on the other 27 | 0.856353 |
| 7 | full-sample fit | R-squared; sum of slopes; Semiconductor | 0.98332561; 1.009356; 0.337425 |
| 8 | per-year Semiconductor | fit per calendar year: 2009; 2026 (185 returns) | 0.1892; 0.5538 |
| 9 | per-year Financial | same: 2009; 2026 | 0.1329; 0.0798 |
| 10 | smallest yearly R-squared | min over 2009–2026 (2021) | 0.99800344 |
| 11 | December 2008 | returns 2008-12-02 … 2008-12-31; design $(\mathbf 1\ X)$ shape; `matrix_rank`; null-space dimension; R-squared | 22; 22×29; 22; 7; 1.0000000000 |
| 12 | December 2008 minimum-norm fit | `pinv(D) @ y`: Semiconductor; FinancialInsurance; Euclidean norm of all 29 coefficients | 0.1450; 0.1653; 0.2849 |
| 13 | December 2008 fit without Semiconductor | minimum-norm fit on the 22×28 design without that column (rank 22, residual zero to machine precision: largest absolute residual 2.0e-15, below 1e-13): Financial; norm | 0.2178; 0.4006 |
| 14 | December 2008 $\hat\Sigma$ | 28×28, divisor 22: `matrix_rank`; `np.linalg.cholesky` | 21; LinAlgError |
| 15 | U28 singular values | $\tilde X/\sqrt T$, full sample: $s_1$; $s_{28}$; $\kappa(\tilde X)$; $\kappa(\hat\Sigma)$ (anchors L214) | 0.054245; 0.005218; 10.3964; 108.0852 |
| 16 | last-250 conditioning | centred 250×28 $\tilde X$: $\kappa(\tilde X)$; `cond`$(\tilde X^{\top}\tilde X)$; max gap between `lstsq`$(\tilde X,\tilde{\mathbf y})$ and `solve`$(\tilde X^{\top}\tilde X,\tilde X^{\top}\tilde{\mathbf y})$, $\tilde{\mathbf y}$ the centred TAIEX returns | 17.0354; 290.2065; about 1e-15 (1.1e-15 and 1.6e-15 on two runs; print the order only) |
| 17 | U28 + Electronic | centred 29 columns (Electronic first), TAIEX response: $\kappa(\tilde X)$ full / 2016 / last 250; $\kappa(\tilde X^{\top}\tilde X)$ the same; max gap 2016 as in row 16 | 48.3 / 642.0 / 316.6; 2,336 / 412,167 / 100,209; between 1e-12 and 1e-11 (3.5e-12 and 7.0e-12 on two runs) |
| 18 | Electronic + eight | 9 columns standardized (divisor $T$), singular values of $Z/\sqrt T$: $s_9/s_1$ full; 2016; covariance scale full; rank at $\delta=0.1,0.01,0.001$ full and 2016 | 0.03458; 0.00277; 0.03287; 8,9,9 and 8,8,9 |
| 19 | Electronic on eight, full sample | fit: Semiconductor; sum; R-squared | 0.53735; 1.014412; 0.98938888 |
| 20 | S3 $\hat\Sigma$ | Semiconductor, Financial, Food | entries printed by the script (e.g. $\hat\sigma_{11}=2.323354\text{e-}4$) |
| 21 | S3 Cholesky | $l_{11}$, $l_{21}$, $l_{22}$, $l_{33}$; slope of Financial on Semiconductor; residual s.d. ($T$) of Food on the other two | 0.015243, 0.006998, 0.009960, 0.008594; 0.45908; 0.0085939 |
| 22 | S3, S5 conditioning | $\kappa(\tilde X)$, $\kappa(\hat\Sigma)$ | S3 2.654, 7.045; S5 3.481, 12.118 |
| 23 | S5 singular values | $\tilde X/\sqrt T$ | 0.024240, 0.013487, 0.011470, 0.009351, 0.006964 |
| 24 | S5 $l_{55}$ | = residual s.d. ($T$) of Shipping on the other four | 0.0143584 |
| 25 | 7 April 2025, S5 | raw returns (%); $\lVert\mathbf z\rVert^2$; rank among 4,382; mean of $\lVert\mathbf z_t\rVert^2$ | −9.95, −9.89, −8.66, −9.90, −9.73; 89.30; 1; 5 (exact) |
| 26 | 7 April 2025 $\mathbf z$ | given order; reversed order (Shipping, Plastics, Food, Financial, Semiconductor) | (−6.59, −5.35, −3.82, −1.32, −0.98); (−5.75, −4.52, −5.11, −2.71, −1.54) |
| 27 | top-5 $\lVert\mathbf z_t\rVert^2$, S5 | dates and values | 2025-04-07 89.30; 2026-07-31 74.13; 2025-04-10 65.98; 2020-07-27 61.28; 2026-07-17 55.58 |
| 28 | S3 on 7 April 2025 | $\lVert\mathbf z\rVert^2$; rank | 86.60; 1 |
| 29 | LM7 problem | $\Sigma$ from 20.1%, 13.5%, −0.11: $l_{11}$, $l_{21}$, $l_{22}$; slope $\rho\sigma_2/\sigma_1$ | 0.20100, −0.01485, 0.13418; −0.0739 |
| 30 | lab extension | `default_rng(20261011).standard_normal((4382,5)) @ L.T`, S5; $\hat\Sigma_{\text{sim}}$ centred, divisor $T$; $\lVert\hat\Sigma_{\text{sim}}-\hat\Sigma\rVert_F/\lVert\hat\Sigma\rVert_F$ | 0.025024 |
| 31 | hand examples | E1, E2, E5 (exact integers; check by hand) | as listed |
| 32 | `cond` table gaps | as in row 16, for S3, S5 and the U28 full sample | all below 1e-14 (5.0e-16, 2.9e-16, 6.5e-16 on one run) |
| 33 | `chol` table | S5's $L$ (divisor $T$) in % a day: diagonal | 1.5243, 0.9960, 0.8594, 1.3034, 1.4358 |
