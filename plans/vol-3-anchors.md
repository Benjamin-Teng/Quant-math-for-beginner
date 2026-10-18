# Volume III — anchors

Every number the Volume III briefs (`plans/vol-3.md`) quote, with the definition that reproduces it. Each module's
`data/vol3_anchors_lmNN.py` prints its rows (`PYTHONUTF8=1 uv run python data/vol3_anchors_lm13.py`), after
`data/vol3_series.py` has built TR23. IDs are global (A13-01 … A18-nn) and are cited the same way in the briefs, the
reviews and the numbers scripts; each module's `data/lmNN_numbers.py` compares its values with these rows and reports a
difference rather than forcing it. From Stage 3 the module sources are authoritative (preface of `plans/vol-3.md`).

## LM13

**Status.** Computed by the reviser on 2026-10-18 with data/vol3_anchors_lm13.py; not yet recomputed independently.

**Common definitions.** Sample: TR23, `data/processed/vol3_taiex.parquet` as built and checked by
`data/vol3_series.py`: 5,850 closes, 2003-01-02 → 2026-10-08. $R$ is its column `R`, the simple return
$P_t/P_{t-1}-1$ of consecutive closes (null on the first row), so $T=5{,}849$ returns, 2003-01-03 → 2026-10-08; `Rp`
is the price index's return. The pair space is the 5,848 return dates from 2003-01-06; "yesterday" is the previous
return; triples run over 5,847 dates. Divisor: a share divides a count by the days of its space (5,849, 5,848 or
5,847, or a regime's days); the one average (E4) divides by its 108 days; LM13 has no variance. Guard: $R\le c$ is
`R <= c + 1e-12`, $R\ge c$ is `R >= c - 1e-12`, and a bucket $(lo,hi]$ is "not $\le lo$ and $\le hi$"; every guarded
count is asserted equal to an exact `Fraction` count from the two-decimal closes. Down is $R<0$ (no return is 0).
Regimes by return date: 7% to 2015-05-29, 10% from 2015-06-01. Blocks: consecutive, non-overlapping, from the first
return, the last $T \bmod n$ returns left out. $A=246.12$ (5,849 returns ÷ 23.7645 years, Shared decisions) is not
used: in LM13 $A$ and $B$ are events (in the case, $R_t\le-3\%$ and $\lvert R_{t-1}\rvert\ge2\%$). Seeds: none; LM13
has no simulation. The Value column is the script's line after its ID, verbatim.

| ID | Number | Definition (enough to reproduce it) | Value (unrounded, as the script prints) | Printed as |
|:--|:--|:--|:--|:--|
| A13-01 | LM4's bet: $f^*$, $g^*$ | printed in lm04.md:345 (the +2%/−1% bet, $p=1/2$); the script recomputes $f^*=0.5/0.01-0.5/0.02$ and $g^*=0.5\ln1.5+0.5\ln0.75$ | `f* 25; g* 0.05889151783 (printed 25 and 5.889% in lm04.md:345)` | 25; 5.889% |
| A13-02 | Price limit | printed in lm05.md:364 (TWSE; sources.md item 25); the script prints the fact | `7% to 10% on 2015-06-01 (printed in lm05.md:364)` | 7% to 10% on 1 June 2015 |
| A13-03 | TR23 sample | rows of the parquet; returns are the rows after the first; first and last return dates | `closes 5850; T 5849; returns 2003-01-03 .. 2026-10-08` | 5,850 closes; $T=5{,}849$; 3 January 2003 to 8 October 2026 |
| A13-04 | Pair space | returns with a previous return in the sample ($T-1$); the first such date | `5848 pairs; first pair date 2003-01-06` | 5,848; 6 January 2003 |
| A13-05 | First return | $R$ on 2003-01-03 | `2.24180759% on 2003-01-03` | +2.24% |
| A13-06 | Ties, distinct returns | number of returns exactly equal (`Fraction`) to 0, −1%, +1%, …, −5%, +5%; number of distinct `Fraction` returns | `exact returns at 0, -1, +1, ..., -5, +5 %: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]; distinct returns 5849` | none; 5,849 |
| A13-07 | Limit regimes | returns dated ≤ 2015-05-29 and ≥ 2015-06-01 | `7%: 3077 returns 2003-01-03 .. 2015-05-29; 10%: 2772 returns 2015-06-01 .. 2026-10-08` | 3,077 days; 2,772 days |
| A13-08 | Falls of 3% or more | # $R\le-3\%$ (guard) among the $T$ returns; share of $T$ | `108 of 5849: 1.846469482%` | 108; 1.85%; 1.8465% (E6) |
| A13-09 | Hit rate $\Pr(B\mid A)$ | pair space: # ($R_t\le-3\%$ and $\lvert R_{t-1}\rvert\ge2\%$) ÷ # ($R_t\le-3\%$) | `32/108 = 29.62962963%` | 32 (29.6%); 29.63% |
| A13-10 | False-alarm rate $\Pr(B\mid A^c)$ | pair space: # ($\lvert R_{t-1}\rvert\ge2\%$ and not $R_t\le-3\%$) ÷ # (not $R_t\le-3\%$) | `457/5740 = 7.961672474%` | 7.96%; 7.962% |
| A13-11 | Big move yesterday | pair space: # $\lvert R_{t-1}\rvert\ge2\%$ (guard on each side) | `489 of 5848` | 489 |
| A13-12 | $\Pr(A\mid B)$ | pair space: 32/489; and 489/32, the days per fall | `32/489 = 6.54396728%; days per crash 15.28125` | 6.54%; under one day in fifteen |
| A13-13 | Ratio to the base rate | $\Pr(A\mid B)$ ÷ (108/5,848) | `Pr(A given B)/Pr(A), Pr(A) = 108/5848: 3.543437098` | 3.5 (case); 3.54 (widget) |
| A13-14 | Inversion factor | $\Pr(B\mid A)/\Pr(A\mid B)$ | `Pr(B given A)/Pr(A given B) = 4.527777778` | 4.53; 4.5 (KC §3) |
| A13-15 | Joint counts | pair space: $A\cap B$, $A\cap B^c$, $A^c\cap B$, neither, $A^c$, $B^c$ | `A&B, A&Bc, Ac&B, neither, Ac, Bc: 32, 76, 457, 5283, 5740, 5359` | 32, 76, 457, 5,283, 5,740, 5,359 |
| A13-16 | Product conditions | $2^m-m-1$ at $m=3$ (Deep Dive 2) | `2^3 - 3 - 1 = 4` | 4 |
| A13-17 | KC §2 | smallest $\Pr(A\cap B)=0.9+0.9-1$ | `0.8` | 0.8 |
| A13-18 | KC §3 | X4's DD/(DD + DU) and DD/(DD + UD) | `1226/2643 = 0.463866818; 1226/2644 = 0.4636913767` | 0.4639; 0.4637 |
| A13-19 | KC §4 | $\Pr(\text{up})$, $\Pr(\text{down})$ on $T$; product of the printed 0.5480 and 0.4520 | `Pr(up) 3205/5849 = 0.5479569157, Pr(down) 2644/5849 = 0.4520430843; product of the printed 0.5480 x 0.4520 = 0.247696; exact 0.2477001342` | 0.5480, 0.4520; 0.2477 |
| A13-20 | Likelihood ratio; KC §5 | LR = A13-09 ÷ A13-10; base rate $1/(1+\text{LR})$ that makes $\Pr(A\mid B)=1/2$ | `LR = Pr(B given A)/Pr(B given Ac) = 3.72153335; base rate with Pr(A given B) = 1/2: 1/(1 + LR) = 21.17956024%` | 3.7215; 21.18% |
| A13-21 | KC §6 | $\hat F(0)=\#(R\le0)/T$; $\#(-1\%<R\le1\%)/T$, guard at both ends | `Fhat(0) = 2644/5849 = 0.4520430843; Pr(-1% < R <= 1%) = (4916 - 768)/5849 = 4148/5849 = 0.7091810566` | 0.4520; 4,148/5,849 = 0.7092 |
| A13-22 | Frequency formats | quoted from Gigerenzer and Hoffrage (1995), Study 1 (sources.md item 11): 16% Bayesian answers in the standard probability format, 46% and 50% with frequency formats; the script prints the quotation | `16%; 46% and 50% (quoted: Gigerenzer and Hoffrage 1995, Study 1)` | from 16% to as much as 50% |
| A13-23 | X1 shares | $\Pr(A\mid B^c)=76/5{,}359$; $\Pr(A)=108/5{,}848$; $\Pr(B)=489/5{,}848$ | `Pr(A given Bc) 76/5359 = 1.418175033%; Pr(A) 108/5848 = 1.846785226%; Pr(B) 489/5848 = 8.361833105%` | 1.42%; 1.85%, 1.847%; 8.36% |
| A13-24 | X2, E2 counts | pair space: # $R_{t-1}\le-2\%$, # $R_t\le-2\%$, both, either; regions only yesterday, both, only today, neither | `yesterday 252, today 252, both 38, either 466; regions 214, 38, 214, 5382` | 252, 252, 38, 466; 214, 38, 214, 5,382 |
| A13-25 | X3 buckets | pair space, yesterday's $R$ in $(lo,hi]$ %: days/falls of 3% or more today, and the share | `108/13 12.03703704%; 144/8 5.555555556%; 516/15 2.906976744%; 1875/30 1.6%; 2272/23 1.012323944%; 696/8 1.149425287%; 170/8 4.705882353%; 67/3 4.47761194%` | counts as listed; 12.04, 5.56, 2.91, 1.60, 1.01, 1.15, 4.71, 4.48 (%) |
| A13-26 | X4 signs | pair space, down = $R<0$: DD, DU, UD, UU (yesterday, today); margins; $\Pr(\text{down today})$ given down, given up, overall | `DD 1226, DU 1417, UD 1418, UU 1787; rows 2643, 3205; columns 2644, 3204; Pr(D given D) 0.463866818, Pr(D given U) 0.4424336973, Pr(D today) 0.452120383` | counts as listed; 0.4639, 0.4424, 0.4521 |
| A13-27 | X4 if independent | row total × column total ÷ 5,848 | `if independent DD, DU, UD, UU: 1194.954172, 1448.045828, 1449.045828, 1755.954172; sum 5848` | 1,195.0, 1,448.0, 1,449.0, 1,756.0; 5,848.0 |
| A13-28 | X5 regimes | per regime: days and share of $T$; falls of 3% or more and their share; pairs with both days inside; falls/days after $\lvert R_{t-1}\rvert\ge2\%$; hit rate; the pair straddling the change | `7%: days 3077 (52.6072833%), falls 72 (2.339941501%); pairs inside 3076, after a big move 17/303 = 5.610561056%, hit 17/72 = 23.61111111%; 10%: days 2772 (47.3927167%), falls 36 (1.298701299%); pairs inside 2771, after a big move 15/186 = 8.064516129%, hit 15/36 = 41.66666667%; straddling pair 2015-05-29 (-0.1212243319%) -> 2015-06-01 (-0.7727700109%): crash False, big False` | 52.61%, 47.39%; 72, 36; 2.34%, 1.30%; 3,076, 2,771; 17/303 (5.61%), 15/186 (8.06%); 23.61%, 41.67%; −0.12%, −0.77% |
| A13-29 | X6 points | $\hat F(x)=\#(R\le x)/T$ at −3%, 0, +3% | `Fhat(-3%) = 108/5849 = 0.01846469482; Fhat(+0%) = 2644/5849 = 0.4520430843; Fhat(+3%) = 5782/5849 = 0.9885450504` | 0.0185, 0.4520, 0.9885 |
| A13-30 | Extremes | minimum and maximum $R$, with dates | `min -9.69969699% on 2025-04-07; max 9.251191375% on 2025-04-10` | −9.70% (7 April 2025); +9.25% (10 April 2025) |
| A13-31 | X7 bins | counts and shares of $T$ in $(-\infty,-5]$, $(-5,-4]$, …, $(4,5]$, $(5,\infty)$ %; sum of the two-decimal shares | `counts 15, 29, 64, 144, 516, 1876, 2272, 696, 170, 37, 17, 13; shares 0.2564540947%, 0.4958112498%, 1.094204137%, 2.461959309%, 8.822020858%, 32.07385878%, 38.84424688%, 11.89946999%, 2.90647974%, 0.632586767%, 0.290647974%, 0.2222602154%; shares rounded to 0.01 points sum to 99.99%` | counts as listed; 0.26, 0.50, 1.09, 2.46, 8.82, 32.07, 38.84, 11.90, 2.91, 0.63, 0.29, 0.22 (%); 99.99% |
| A13-32 | Widget readouts | $\Pr(B)=489/5{,}848$; $\Pr(A\mid B)$; $\Pr(A\mid B^c)$; $\Pr(A\mid B)$ ÷ (108/5,848); $\Pr(B)$ from the printed inputs | `Pr(B) 8.361833105%; Pr(A given B) 6.54396728%; Pr(A given Bc) 1.418175033%; ratio 3.543437098; from the printed 0.01847, 0.2963, 0.07962: Pr(B) 8.36220796%` | 8.36%, 6.54%, 1.42%, 3.54 |
| A13-33 | Odds (widget, E8) | prior odds 108/5,740; LR (A13-20); posterior odds 32/457; the printed 0.018815 × 3.7215; 0.07002/1.07002 | `prior odds 108/5740 = 0.01881533101; LR = 3.72153335; posterior odds 32/457 = 0.07002188184; printed 0.018815 x 3.7215 = 0.0700200225; 0.07002/1.07002 = 6.54380292%` | 0.018815; 3.7215; 0.07002; 6.54% |
| A13-34 | 1,000-day picture | 1,000 × the four joint counts ÷ 5,848, floored, the remaining squares to the largest remainders; share $A\cap B$ ÷ ($A\cap B$ + $A^c\cap B$) | `per 1,000: 5.471956224, 12.99589603, 78.14637483, 903.3857729; squares [6, 13, 78, 903]; picture share 6/84 = 7.142857143%` | 6, 13, 78, 903; 6 of 84, 7.1% |
| A13-35 | E1 | enumeration of $\{++,+-,-+,--\}$, equally likely; wealth multiple 1.5 or 0.75 a trade at $f=25$ | `Pr(B) = 3/4; Pr(A and B) = 1/4; wealth below start only on --: ['--']` | 3/4; 1/4; $--$ only |
| A13-36 | E2 | 466/5,848; 504/5,848; 252/5,848; 5,848 × 0.0431² (printed input) and exact | `union 466/5848 = 7.968536252%; sum 504/5848 = 8.618331053%; Pr(today) 252/5848 = 4.309165527%; independent both 5848*0.0431^2 = 10.86330328, exact 10.85909713` | 7.97%; 8.62%; 0.0431; 10.9 |
| A13-37 | E3 | pair space: falls today after a fall yesterday ÷ falls yesterday; both ÷ 5,848; ratio to 108/5,848 (and printed 12.04/1.85); 108²/5,848 | `13 of 108 = 12.03703704%; both 13/5848 = 0.2222982216%; ratio to base rate 6.517832647 (printed 12.04/1.85 = 6.508108108); pairs if independent 1.994528044` | 13, 12.04%; 0.222%; 6.5; 2.0 |
| A13-38 | E4 | $\#(R\le-5\%)$ and $\#(R\le-4\%)$ ÷ $\#(R\le-3\%)$ on $T$; mean $R$ of the 108 days (divisor 108) | `Pr(R<=-5% given R<=-3%) 15/108 = 13.88888889%; Pr(R<=-4% given R<=-3%) 44/108 = 40.74074074%; mean R of the 108 days -4.062685051%` | 13.9%; 40.7%; −4.06% |
| A13-39 | E5, Problem 3 | two fair trades: $\Pr$ of $A_1$, $A_2$, $A_3$; of each pair; of all three, against the product | `each 1/2, 1/2, 1/2; pairs 1/4, 1/4, 1/4; all three 1/4 against 1/8` | 1/2; 1/4; 1/4, not 1/8 |
| A13-40 | E6 | $p=108/5{,}849$; $1-(1-p)^{20}$, exact and from the printed 1.8465%; blocks of 20 from the first return: number, returns left out, blocks with a fall of 3% or more; 292 × model, and 292 × 0.311 | `Pr(A) = 108/5849 = 1.846469482%; model 1-(1-108/5849)^20 = 31.11597589%; from the printed 1.8465%: 31.11640424%; blocks 292, left out 9, with a crash 61 (20.89041096%); model blocks 90.85864959, from the printed 31.1%: 90.812` | 1.8465%; 31.1%; 292, 9, 61 (20.9%); about 91 |
| A13-41 | E7 | 72/3,077, 36/2,772; weights 3,077/5,849, 2,772/5,849; total; 36/108; (13.9) from the printed 2.34%, 1.30%, 0.5261, 0.4739 | `Pr(A given 7%) 72/3077 = 2.339941501%; Pr(A given 10%) 36/2772 = 1.298701299%; weights 52.6072833%, 47.3927167%; total 1.846469482%; Pr(10% given A) 36/108 = 33.33333333%; from the printed 2.34%, 1.30%, 0.5261, 0.4739: 33.35257024%` | 2.34%, 1.30%; 52.6%, 47.4%; 1.85%; 33.3%; 33.4% (rounding trap) |
| A13-42 | E8 | the inputs 108/5,848, 32/108, 457/5,740; (13.9) with the printed four-digit inputs; with the case's 1.85%, 29.6%, 7.96%; the ratio of the printed 29.63% and 7.962% | `inputs 1.846785226%, 29.62962963%, 7.961672474%; (13.9) with 0.01847, 0.2963, 0.07962: 6.544516743%; with the case's 0.0185, 0.296, 0.0796: 6.549972848%; LR from the printed 29.63%, 7.962%: 3.721426777` | 1.847%, 29.63%, 7.962%; 6.54%; 6.55% (rounding trap); 3.7214 not printed (why E8(c) uses counts) |
| A13-43 | E9 | $0.55^8\,0.45^4/0.5^{12}$; $(0.1/0.9)\times$LR; odds ÷ (1 + odds); also from the printed 1.4064 | `LR 1.406408618; posterior odds 0.1562676242; posterior 13.51483177%; from the printed 1.4064: odds 0.1562666667, posterior 13.51476015%` | 1.4064; 0.15627; 13.5% |
| A13-44 | E10 | $1.5^2$, $1.5\times0.75$, $0.75^2$ ($1+25\times2\%$, $1-25\times1\%$); ½ ln of each | `X = 2.25, 1.125, 0.5625; pmf 1/4, 1/2, 1/4; F_X(1) = 1/4; half-logs 40.54651081%, 5.889151783%, -28.76820725%` | 2.25, 1.125, 0.5625; 40.55%, 5.889%, −28.77% |
| A13-45 | Problem 1 | 252/5,849, 237/5,849, 489/5,849; from the printed 4.31% and 4.05%: sum, product, $1-(1-a)(1-b)$ | `Pr(R<=-2%) 252/5849 = 4.308428791%; Pr(R>=2%) 237/5849 = 4.051974697%; Pr(abs(R)>=2%) 489/5849 = 8.360403488%; printed sum 8.36%, product 0.174555%, 1-(1-a)(1-b) 8.185445%` | 4.31%, 4.05%; 8.36%; 0.17%; 8.19% |
| A13-46 | Problem 2 | pairs with both days ≥ 2015-06-01; base rate 36/2,771; hit rate 15/36; false alarms 171/2,735; (13.9) from the printed inputs; 15/186 | `pairs 2771; base 36/2771 = 1.299169975%; hit 15/36 = 41.66666667%; false alarms 171/2735 = 6.252285192%; (13.9) from the printed 1.299%, 41.67%, 6.252%: 8.064464585%; exact 15/186 = 8.064516129%` | 2,771; 1.299%, 1.30%; 41.67%, 41.7%; 6.252%; 8.06% |
| A13-47 | Problem 4 | 5,847 triples: # $R\le-2\%$ on day 1, 2, 3; on days 1–2, 1–3, 2–3; on all three; union; sum | `triples 5847; singles 252, 252, 252; pairs 1-2 38, 1-3 34, 2-3 38; all three 8; union 654 (11.18522319%); bound 756 (12.92970754%)` | 252 three times; 38, 34, 38; 8; 654 (11.19%); 756 (12.93%) |
| A13-48 | Problem 5 | triples: # down on day 1, days 1–2, days 1–3; chain factors; product of the printed factors; 542/5,847; $(2{,}644/5{,}849)^3$, from 0.45204, from 0.4520 | `2642/5847 = 0.4518556525, 1225/2642 = 0.463663891, 542/1225 = 0.4424489796; product of the printed 0.4519 x 0.4637 x 0.4424 = 9.270316367%; exact 542/5847 = 9.269710963%; independence (2644/5849)^3 = 9.237181739%, from 0.45204 9.236992665%, from 0.4520 9.2345408%` | 0.4519, 0.4637, 0.4424; 9.27%; 0.45204; 9.24%; 9.23% (rounding trap) |
| A13-49 | Problem 6 | $\ln0.5/\ln(1-108/5{,}849)$; model at 37 and 38; blocks of 38 from the first return: number, left out, with a fall of 3% or more | `n = ln 0.5/ln(1 - 108/5849) = 37.19140413; at 37 49.82131872%, at 38 50.74785276%; blocks of 38: 153, left out 35, with a crash 50 (32.67973856%)` | 38; 49.82%, 50.75%; 153, 35, 50 (32.68%) |
| A13-50 | Problem 7 | # $R\le-5\%$ per regime ÷ its days; LR, exact and from the printed shares; 7/15; via the printed LR 0.971; prior 2,772/5,849 | `8/3077 = 0.2599935002%; 7/2772 = 0.2525252525%; LR 0.9712752525, from the printed 0.9711538462; Pr(10% given R<=-5%) 7/15 = 46.66666667%; via the printed LR 0.971: 46.6596124%; prior 47.3927167%` | 8, 7; 0.2600%, 0.2525%; 0.971; 46.7%; 47.4% |
| A13-51 | Problem 8 | $0.55^{16}\,0.45^{8}/0.5^{24}$; posterior at prior 10%; prior $1/(1+1.4064)$; also from the printed ratios | `LR 1.977985201 (1.4064^2 = 1.97796096); posterior 18.01774338%, from the printed 1.9780 18.01785389%; prior giving 1/2 after 8 of 12: 41.55570224%, from the printed 1.4064 41.55585106%` | 1.9780; 18.02%; 41.56% |
| A13-52 | Problem 9 | $W_3/W_0$ over the 8 equally likely sequences; $\Pr(W_3<W_0)$ | `3.375: 1/8; 1.6875: 3/8; 0.84375: 3/8; 0.421875: 1/8; Pr(W3 < W0) = 1/2` | 3.375, 1.6875, 0.84375, 0.421875; 1/8, 3/8, 3/8, 1/8; 1/2 |
| A13-53 | Problem 10 | pair space: DD/5,848; (DD + DU)/5,848; (DD + UD)/5,848; their product, exact and from the printed 0.4519 and 0.4521 | `Pr(X=1,Y=1) 1226/5848 = 0.2096443228; Pr(X=1) 2643/5848 = 0.4519493844, Pr(Y=1) 2644/5848 = 0.452120383; product exact 0.2043355288, of the printed 0.4519 x 0.4521 = 0.20430399` | 0.2096; 0.4519; 0.4521; 0.2043 |
| A13-54 | Problem 12 | $p=0.55$, $q=0.45$: $1-q^2$, $2pq$, $1-p^2$ | `1 - q^2 = 0.7975; 2pq = 0.495; 1 - p^2 = 0.6975` | 0.7975; 0.4950; 0.6975 |
| A13-55 | Lab extension | returns from the sixth (5,844 days): falls of 3% or more with some $\lvert R\rvert\ge2\%$ among the previous five returns ÷ all those falls | `days 5844; crashes with abs(R) >= 2% in the previous five sessions 76/108 = 70.37037037%` | 70.4%; 5,844 |
| A13-56 | Dividend gap | maximum over days of $R-R_p$ (TR23 minus the price index, column `Rp`), in bp, with its date | `max R - Rp = 83.93463079 bp on 2016-06-27` | 84 bp |

**Facts checked on official sources.**

- The daily price limit rose from 7% to 10% on 1 June 2015 (A13-02): sources.md item 25 (TWSE company history; TWSE
  60th-anniversary book, p. 181), as printed in lm05.md:364.
- The TAIEX total-return index reinvests cash dividends (the case's "dividends reinvested", X1's Source line):
  sources.md item 24 (TWSE IndexS02, §四(一)2 and §五(六); Taiwan Index Plus, "The TAIEX Methodology").
- Gigerenzer and Hoffrage (1995), Study 1 (A13-22): sources.md item 11, status corrected; the paper says "frequency
  formats" and "natural sampling", not "natural frequencies".

## LM14

**Status.** Computed by the reviser on 2026-10-18 with data/vol3_anchors_lm14.py; not yet recomputed independently.

**Common definitions.** Sample TR23: column `R` of `data/processed/vol3_taiex.parquet` (built and checked by
`data/vol3_series.py`), the simple daily return $R_t=\mathrm{tr}_t/\mathrm{tr}_{t-1}-1$ of the TAIEX total-return
index, null on the first row (2003-01-02), so $T=5{,}849$ returns from 2003-01-03 to 2026-10-08. The empirical law
$\hat F$ puts mass $1/T$ on each return, so every mean, variance, skewness and kurtosis divides by $T$ (`ddof=0`,
`bias=True`). Years: calendar days from 2003-01-02 to 2026-10-08 ÷ 365.25; $A=T/\text{years}$. Calendar years
2003–2025 run from the last close of the previous year (2003 from 2003-01-02); 2026 is partial and left out.
$z=(R-\bar R)/s$. Counts use the guard (`<= -x + 1e-12`, `>= x - 1e-12`); the −3% count is confirmed with exact
fractions of the two-decimal closes. The small laws are exact arithmetic; "from printed" means recomputed from the
inputs at the precision the brief prints them. Seeds: none (LM14 has no simulation). The script prints percentages in
percent and gaps in bp or log points, as each row says.

| ID | Number | Definition (enough to reproduce it) | Value (unrounded, as the script prints) | Printed as |
|:--|:--|:--|:--|:--|
| A14-01 | $T$ | number of TR23 returns (non-null `R`); first and last return dates | 5849; first return 2003-01-03; last 2026-10-08 | 5,849 |
| A14-02 | calendar days; years | 2026-10-08 − 2003-01-02 in days; ÷ 365.25 | 8680 calendar days; 23.76454483 | 8,680; 23.7645 |
| A14-03 | $A$ | $T$ ÷ years | 246.1229551 | 246.12 |
| A14-04 | arithmetic mean of the years | mean of the 23 calendar-year returns 2003–2025: last `tr` of the year ÷ last `tr` of the previous year − 1, 2003 from the first close (2003-01-02); 2026 left out | 23 years 2003-2025; 14.97485882% | 14.97% |
| A14-05 | compound annual rate | (product of the 23 growth factors)$^{1/23}-1$; the product | 12.35149765%; growth factor 14.56511496 | 12.35% |
| A14-06 | 2008, 2009 | calendar-year returns as in A14-04 | 2008 -43.06878444%; 2009 83.34488375% | −43.07%, +83.34% |
| A14-07 | average of 2008 and 2009 | $(R_{2008}+R_{2009})/2$; from the printed −43.07%, +83.34% | unrounded 20.13804966%; from printed 20.135% | +20.1% (20.135 is a two-decimal tie) |
| A14-08 | two years together | $(1+R_{2008})(1+R_{2009})-1$; from the printed returns | unrounded 4.380470992%; from printed 4.375462% | +4.4% |
| A14-09 | $\bar R$ | mean of `R` | 0.06250506219% | 0.0625%; 0.062505% (X1 note) |
| A14-10 | compound daily rate $R_G$; $\bar r$ | $e^{\bar r}-1$, $\bar r$ the mean of $\ln(1+R)$ | 0.05518484246%; r_bar 0.05516962122% | 0.0552%; 0.055185% (X1 note) |
| A14-11 | $\bar R-R_G$ | A14-09 − A14-10 in bp; the same from the four-decimal rates | 0.7320219732 bp; from the four-decimal rates 0.73 bp | 0.7320 bp; 0.73 bp |
| A14-12 | distance to $s^2/2$ | A14-11 − A14-13 | 0.001949782118 bp | within 0.002 bp |
| A14-13 | $s^2/2$ daily | $s^2=\frac1T\sum(R_t-\bar R)^2$, halved, in bp | 0.7300721911 bp | 0.7301 bp |
| A14-14 | $s$; $s^2$ | divisor-$T$ standard deviation of `R` | 1.208364342%; s^2 0.0001460144382 | 1.2084%; 1.208364% (X1 note) |
| A14-15 | the die (KC §2, X9) | fair die: mean, variance, set of medians, `np.median`, `rv_discrete(values=...).median()` | E 3.5; Var 2.916666667 = 35/12 2.916666667; medians [3, 4]; np.median 3.5; rv_discrete median 3 | every $m\in[3,4]$; 3.5; 3 |
| A14-16 | ±10% day | $\tfrac12\ln1.1+\tfrac12\ln0.9=\tfrac12\ln0.99$ | -0.5025167927%; 0.5 ln 0.99 = -0.5025167927% | −0.5025% |
| A14-17 | TR23 at $f=2$ (KC §4) | $2s$; $2\times$ the printed 1.2084%; $4\E[R^2]$ | 2s 2.416728683%; from printed 2 x 1.2084 = 2.4168%; E(2R)^2 0.000585620506 | 2.417% (not 2.4167, since 2 × 1.2084 = 2.4168); $5.856\times10^{-4}$ |
| A14-18 | X6, KC §5, Problem 11 | $z=(R-\bar R)/s$; days with $\lvert z\rvert\ge k$ (guard `>= k - 1e-12`) and with $z\le-k$ (guard `<= -k + 1e-12`), shares of $T$; $1/k^2$; $1/(1+k^2)$; $k=1,\dots,6$ | k=1: two-sided 1313 (22.44828176%), Chebyshev 100% / lower 665 (11.36946487%), Cantelli 50%; k=2: two-sided 319 (5.453923748%), Chebyshev 25% / lower 188 (3.214224654%), Cantelli 20%; k=3: two-sided 99 (1.692597025%), Chebyshev 11.11111111% / lower 61 (1.042913319%), Cantelli 10%; k=4: two-sided 30 (0.5129081894%), Chebyshev 6.25% / lower 17 (0.290647974%), Cantelli 5.882352941%; k=5: two-sided 11 (0.1880663361%), Chebyshev 4% / lower 6 (0.1025816379%), Cantelli 3.846153846%; k=6: two-sided 4 (0.06838775859%), Chebyshev 2.777777778% / lower 2 (0.0341938793%), Cantelli 2.702702703% | $k=1,\dots,6$: 1,313, 665; 319, 188; 99, 61; 30, 17; 11, 6; 4, 2 (two-sided, lower); shares to two decimals of a percent; 25% and 20% at $k=2$ |
| A14-19 | $\ln(1+\bar R)-\bar r$ | exact daily drag in log points, bp; check $(1+\bar R)(1-e^{-J})=\bar R-R_G$, also from the printed 0.0625% and 0.7316 bp | 0.7315914689 bp; check (1+mu)(1-exp(-J)) 0.7320219732 bp; from printed (1.000625)(1-exp(-0.7316 bp)) 0.732030472 bp | 0.7316 bp; 0.7320 bp (E10) |
| A14-20 | gap at $f=2$ (KC §7) | $\ln(1+2\bar R)-\frac1T\sum\ln(1+2R_t)$ in bp; $4\times$ A14-19; $4\times0.7316$ | 2.936068384 bp; 4 x J 2.926365876 bp; from printed 4 x 0.7316 = 2.9264 | 2.936 bp; 2.926 |
| A14-21 | X3, E2, KC §8, Problem 11 | $\hat F^{-1}(u)=R_{(j)}$, $j=\lceil uT\rceil$ (asserted equal to `np.quantile(R, u, method="inverted_cdf")`) and `np.quantile(R, u)` (default `"linear"`) | u=0.001: j=6 -6.312532736% / linear -5.866488419%; u=0.01: j=59 -3.567140254% / linear -3.566784606%; u=0.05: j=293 -1.86205837% / linear -1.856947206%; u=0.25: j=1463 -0.4904071481% / linear -0.4904071481%; u=0.5: j=2925 0.08786964504% / linear 0.08786964504%; u=0.75: j=4387 0.6811683611% / linear 0.6811683611%; u=0.95: j=5557 1.832865508% / linear 1.832228495%; u=0.99: j=5791 3.125229484% / linear 3.119770843%; u=0.999: j=5844 5.822750878% / linear 5.665597896% | three decimals of a percent (−6.313, −5.866, −3.567, 3.125, 5.823, …) |
| A14-22 | E1's $X$ (LM13's E10) | $X=W_2/W_0$ at $f=25$ on $\{++,+-,-+,--\}$, factors 1.5 and 0.75, each outcome ¼: values, $p_X$, $F_X$ | 0.5625: 0.25, 1.125: 0.5, 2.25: 0.25; F_X 0.25, 0.75, 1 | 0.5625, 1.125, 2.25; ¼, ½, ¼; ¼, ¾, 1 |
| A14-23 | (3.7) row of X4; E7's $\E[R^2]$ | mean of $R^2$; $s^2$; $\bar R^2$; their sum; the sum from four-figure and from five-figure printed inputs | E R^2 0.0001464051265; s^2 0.0001460144382; Rbar^2 3.906882799e-07; s^2 + Rbar^2 0.0001464051265; from four-figure inputs 0.0001463907; from five-figure inputs 0.00014640069 | $1.464\times10^{-4}$, $1.460\times10^{-4}$, $3.907\times10^{-7}$; at five figures 1.4601 + 0.0039 gives 1.4640, not 1.4641 |
| A14-24 | 0050's excess kurtosis; $m_4$ ratio | printed in lm04.md:132 (8.12 also lm05.md:366); not recomputed | printed in lm04.md:132: 0050 excess kurtosis 8.12, m4 3.7 times the normal's | 8.12; 3.7 |
| A14-25 | X5 | $T/(1+k^2)$ at $k=1,4,8$; smallest $z$, its date and return | Cantelli days T/(1+k^2) at k=1,4,8: 2924.5, 344.0588235, 89.98461538; min z -8.078856447 on 2025-04-07 (R -9.69969699%) | 2,924.5, 344.1, 90.0; $k=8.08$, 7 April 2025, −9.6997% |
| A14-26 | days at $k=4$ | days with $z\le-4$ (guard); share of $T$ | 17; 0.290647974% | 17; 0.29% |
| A14-27 | X7 | per calendar year 2003–2025 (2003 from 2003-01-03), from that year's daily returns: mean minus compound rate against half their variance (divisor: the year's count), bp; the extremes; largest absolute and relative gaps | min drag 2017 0.1442227499 bp (s^2/2 0.1442387824); max 2008 2.250101527 bp (s^2/2 2.246978118); largest absolute gap 2024 0.009727008643 bp; largest relative 2024 1.133056112% | 2.25 bp (2008), 0.14 bp (2017); 0.0097 bp (2024); 1.13% |
| A14-28 | daily (14.13) terms | $\frac1T\sum_t(-1)^jy_t^j/j$ for $j=2,3,4$, $y_t=(R_t-\bar R)/(1+\bar R)$, in bp; their sum | 0.7291603819, 0.00198675989, 0.0004395903755 bp; sum 0.7315867322 | 0.7292, 0.0020, 0.0004; 0.7316 |
| A14-29 | annual $\sigma$, Skew, Kurt (X8, Problem 10) | divisor-23 moments of A14-04's returns; their mean log; $\ln(1+\text{mean})$ | 23.6984248%; skew 0.1855797901; kurt 5.023379734; g 11.64621428%; ln(1+mu) 13.95432995% | 23.70%; 0.19; 5.02 |
| A14-30 | annual row of X8 | law of the 23 returns, equal weights: $\ln(1+\mu)-g$, second-order term, through the fourth order, $\mu-R_G$, $\sigma^2/2$ (log or percentage points) | ln(1+mu)-g 2.308115673; 2nd 2.124238103; through 4th 2.296742417; mu-R_G 2.623361168; sigma^2/2 2.808076691 | 2.31, 2.12, 2.30, 2.62, 2.81 |
| A14-31 | 2008/2009 law (X8 pair row, widget) | two-point law on the printed −43.07%, +83.34%, ½ each | mu 20.135%; sigma 63.205%; g 2.141221176%; R_G 2.164309815%; ln(1+mu) 18.34459245%; ln(1+mu)-g 16.20337127; mu-R_G 17.97069018; sigma^2/2 19.97436013; 2nd-order 13.83992607; through 4th 15.75536161; (3.9) 0.160639875% | 20.1%, 63.2% (20.135%, 63.205%: two-decimal ties), 2.14%, 2.16%, 18.34%, 16.20, 17.97, 19.97, 13.84, 15.76, 0.16% |
| A14-32 | +100%/−50% row of X8 | two-point law, ½ each | mu 25%; sigma 75%; mu-R_G 25; sigma^2/2 28.125; ln(1+mu)-g 22.31435513; 2nd 18; through 4th 21.24 | 25%, 75%, 25.00, 28.125 (exact; two decimals would tie), 22.31, 18.00, 21.24 |
| A14-33 | LM4's Kelly bet | $f^*=p/a-q/b$; $g^*=\tfrac12\ln1.5+\tfrac12\ln0.75$; printed in lm04.md:345 | f_star = 0.5/0.01 - 0.5/0.02 = 25; g_star 5.889151783%; printed in lm04.md:345: 25, 5.889% | 25×; 5.889% |
| A14-34 | $\E[\tfrac12\ln X]$ | LOTUS on E1's $X$, equal to $\tfrac12\ln1.125$ (LM4's $g^*$) | 5.889151783%; 0.5 ln 1.125 = 5.889151783% | 5.889% |
| A14-35 | $\ln\E[X]$; $\tfrac12\ln\E[X]$ | $\ln1.265625$; half of it, which is also $\E[\ln X]=\ln1.125$ (Problem 9) | ln E X 23.55660713%; 0.5 ln E X 11.77830357% | 23.557%; 11.778% |
| A14-36 | E1's quantile and median | $\min\{x:F_X(x)\ge u\}$ at $u=0.1$; the median and its two probabilities | F^-1(0.1) 0.5625; median 1.125 (Pr(X<=m) 0.75, Pr(X>=m) 0.75) | 0.5625; 1.125 |
| A14-37 | $\hat F(0)$ | days with $R\le0$ (guard) ÷ $T$; days with $R=0$ | 2644/5849 = 0.4520430843; R == 0 on 0 days | 2,644/5,849 = 0.4520; none |
| A14-38 | up days | days with $R>0$; share | 3205; 54.79569157% | 3,205; 54.8% |
| A14-39 | median of $\hat F$ | 2,925th smallest return ($T$ odd); `np.median` agrees | 0.08786964504%; order 2925; np.median 0.08786964504% | 0.0879% |
| A14-40 | days above the mean | days with $R>\bar R$; share | 3020; 51.63275774% | 3,020; 51.6% |
| A14-41 | $\E[X]$ | both sums of E3 | 1.265625; 1.125^2 = 1.265625 | 1.265625 $=1.125^2$ |
| A14-42 | $\tfrac12\ln X$ | at 0.5625, 1.125, 2.25; the weighted sum from LM13's two-decimal values (−28.77, 5.889, 40.55) | -28.76820725%, 5.889151783%, 40.54651081%; weighted sum from two-decimal logs 5.8895% | −28.7682%, 5.8892%, 40.5465%; 5.8895 (a tie) |
| A14-43 | $\bar r=\bar g(1)$ | mean of $\ln(1+R)$, bp | 5.516962122 bp | 5.5170 bp |
| A14-44 | $A\bar r$ | and $\ln G$ ÷ years, equal by (1.12) | A r_bar 13.57851021%; ln G / years 13.57851021% | 13.58% |
| A14-45 | $G$ over the sample | last `tr` ÷ first `tr` | 25.20068421 | 25.2007 |
| A14-46 | +2%/−1% bet (E5) | two-point law, ½ each: $\mu$, $\sigma$, $\E[R^2]$, $\E[R^3]$, $\mu^3+3\mu\sigma^2$, Skew, Kurt | mu 0.005; sigma 0.015; E R^2 0.00025; E R^3 3.5e-06; mu^3+3mu sigma^2 3.5e-06; Skew 0; Kurt 1 | 0.5%, 1.5%, 0.00025, $3.5\times10^{-6}$, 0, 1 |
| A14-47 | Skew of $\hat F$ | `stats.skew(R)` (divisor $T$) | -0.3384441792 | −0.34 (E6); −0.338 (X4) |
| A14-48 | Kurt; excess kurtosis | `stats.kurtosis(R) + 3`; `stats.kurtosis(R)` | Kurt 8.268030077; excess 5.268030077 | 8.27; 5.27 |
| A14-49 | $\E[R^3]$ | mean of $R^3$ | -3.231028625e-07 | $-3.231\times10^{-7}$ |
| A14-50 | normal $\E[X^3]$ | $\mu^3+3\mu\sigma^2$ at $\mu=\bar R$, $\sigma=s$; from the six-decimal inputs | 2.740434462e-07; from six-decimal inputs 2.740430182e-07 | $2.740\times10^{-7}$ |
| A14-51 | $\E[R^4]$ | mean of $R^4$ | 1.751256313e-07 | $1.751\times10^{-7}$ |
| A14-52 | ratio of fourth moments | A14-51 ÷ A14-53 | 2.723440882 | 2.72 |
| A14-53 | normal $\E[X^4]$ | $\mu^4+6\mu^2\sigma^2+3\sigma^4$ at $\bar R$, $s$; from four- and six-decimal inputs | 6.430307792e-08; from four-decimal inputs 6.431059278e-08; from six-decimal inputs 6.430300471e-08 | $6.430\times10^{-8}$ (four decimals would give 6.431) |
| A14-54 | $(\bar R/s)^2$ | the relative size of LM4's dropped terms | 0.00267568252 | 0.0027 |
| A14-55 | LM4's approximations | $3\mu\sigma^2$, $3\sigma^4$ at $\bar R$, $s$; from four- and six-decimal inputs | 3 mu sigma^2 2.737992462e-07; 3 sigma^4 6.396064851e-08; from four-decimal inputs 2.7379323e-07, 6.396819865e-08; from six-decimal inputs 2.73798819e-07, 6.396057617e-08 | $2.738\times10^{-7}$; $6.396\times10^{-8}$ (four decimals: 6.397) |
| A14-56 | $\E\lvert R\rvert$ | mean of $\lvert R\rvert$ | 0.8401635878% | 0.8402% |
| A14-57 | Markov on $\lvert R\rvert$ at 3% | A14-56 ÷ 3%; from the printed 0.8402% | unrounded 28.00545293%; from printed 28.00666667% | 28.0% |
| A14-58 | Markov on $R^2$ at 3% | $\E[R^2]/0.03^2$; from the printed $1.464\times10^{-4}$ | unrounded 16.26723628%; from printed 16.26666667% | 16.27% |
| A14-59 | days with $\lvert R\rvert\ge3\%$ | guard `>= 0.03 - 1e-12`; share | 175; 2.991964438% | 175; 2.99% |
| A14-60 | Cantelli at −3% | $k=(\bar R+3\%)/s$, $1/(1+k^2)$; from the printed 0.0625%, 1.2084% | k 2.53442191 -> 13.47110789%; from printed k 2.534342933 -> 13.47183439% | $k=2.534$; 13.47% |
| A14-61 | days with $R\le-3\%$ | guard; share; recount with exact fractions of the two-decimal closes | 108; 1.846469482%; exact-fraction recount 108 | 108; 1.85% |
| A14-62 | Cantelli at $k=4$ | $1/17$ | 1/17 = 5.882352941% | 5.88% |
| A14-63 | $\Phi(-4)$ | `stats.norm.cdf(-4)`; printed in lm05.md:749 | 3.167124183e-05 | $3.17\times10^{-5}$ |
| A14-64 | normal expected days at $k=4$ | $T\Phi(-4)$ (also from the printed $3.17\times10^{-5}$); $2T\Phi(-4)$ | T Phi(-4) 0.1852450935; from printed 0.1854133; 2 T Phi(-4) 0.370490187 | 0.185; 0.37 |
| A14-65 | $\bar R-4s$ | also from the printed 0.0625%, 1.2084% | -4.770952304%; from printed -4.7711% | −4.771% |
| A14-66 | 17 days against the normal and the bound | A14-26 ÷ A14-64 (also from the printed 0.185); the share ÷ $1/17$ | 91.77031186; from printed 91.89189189; share / bound 0.04941015558 | 92 times; a twentieth |
| A14-67 | two-sided days at $k=4$ | $\lvert z\rvert\ge4$ (guard); share; $1/16$ | 30; 0.5129081894%; Chebyshev 6.25% | 30; 0.51%; 6.25% |
| A14-68 | E9, the 23 years | $1+$A14-04; $1+$A14-05 | 1 + mean 1.149748588; geometric mean 1.123514976 | 1.1497 ≥ 1.1235 |
| A14-69 | E9, the pair | from the printed returns: $\tfrac12(0.5693+1.8334)$; $\sqrt{0.5693\times1.8334}$ | AM 1.20135; GM 1.021643098 | 1.20135 ≥ 1.02164 |
| A14-70 | lognormal form | $s_r^2/2$ in bp, $s_r$ the divisor-$T$ standard deviation of $\ln(1+R)$ | s_r^2/2 0.7329297619 bp; s_r 1.210726858% | 0.7329 bp; 1.2107% |
| A14-71 | four-day bet (Problem 1) | $1.02^j0.99^{4-j}$ with probability $\binom4j/16$; $F_G$; the mean | 0.96059601: 1/16, 0.98970498: 1/4, 1.01969604: 3/8, 1.05059592: 1/4, 1.08243216: 1/16; F 1/16, 5/16, 11/16, 15/16, 1; mean 1.020150501 | 0.960596, 0.989705, 1.019696, 1.050596, 1.082432; 1.020151 |
| A14-72 | Problem 2 | $\E[G]$; one day's $\E\ln(1+R)$; $\E[\ln G]$; $\ln\E[G]$; the gap | E G 1.020150501 (1.005^4 1.020150501); E ln(1+R) one day 0.4876145721%; E ln G 1.950458289%; ln E G 1.995016604%; gap 4.455831588 bp | 1.02015 $=1.005^4$; 0.487615%; 1.95046%; 1.99502%; 4.456 bp |
| A14-73 | Pareto mean (Problem 3) | $\alpha/(\alpha-1)$ at $\alpha=1.5$ | mean 1.5/0.5 = 3 | 3 |
| A14-74 | Problem 4 | +1% with probability 0.9, −5% otherwise (lm04.md:719): $\mu$, $\sigma$, $\E[R^2]$, $\E[R^3]$, Skew, Kurt, excess; $\mu$, $\sigma$ at $f=8$ | mu 0.4%; sigma 1.8%; E R^2 0.00034; E R^3 -1.16e-05; Skew -2.666666667 (-8/3); Kurt 8.111111111 (73/9), excess 5.111111111; f=8: mu 3.2%, sigma 14.4% | 0.4%, 1.8%, $3.4\times10^{-4}$, $-1.16\times10^{-5}$, −8/3 = −2.67, 73/9 = 8.11, 5.11; 3.2%, 14.4% |
| A14-75 | Problem 5 | $\E[Z^6]$, $\Var(Z^3)$; (14.6) at $\mathcal N(0.05,0.2^2)$ and SciPy's `moment` | E Z^6 15; Var Z^3 = E Z^6 - (E Z^3)^2 15; E X^3 0.006125 (scipy 0.006125); E X^4 0.00540625 (scipy 0.00540625) | 15; 15; 0.006125; 0.00540625 |
| A14-76 | Problem 6 | $k=(0.0625+5)/1.2084$ (printed inputs); $1/(1+k^2)$; $1/k^2$; days with $R\le-5\%$ (guard), share | k from printed 4.189424032; Cantelli 5.390465448%; Chebyshev 5.697592187%; days R <= -5%: 15 (0.2564540947%); unrounded k 4.189551849 | 4.1894; 5.39%; 5.70%; 15, 0.26% |
| A14-77 | Problem 7's distractors | $1/9$; the Pareto tail $\Pr(X\ge x)=x^{-1.5}$, positive for every $x\ge1$ (value at $x=4$) | 1/9 11.11111111%; Pareto tail Pr(X >= x) = x^-1.5, e.g. at x = 4: 0.125 | 11.1%; 0 (distractor C) |
| A14-78 | LM1's counterexample | $\ln(1.5e^{0.10}-0.5e^{0.20})$; $\sum_jw_jr_j$; printed in lm01.md:435 | ln(1.5e^0.10 - 0.5e^0.20) 0.04598145967; 1.5 x 0.10 - 0.5 x 0.20 = 0.05; printed in lm01.md:435: 0.0460, 0.0500 | 0.0460 < 0.0500 |
| A14-79 | Problem 9 | on E1's $X$: $\E\sqrt X$, $\sqrt{\E X}$, $\E[1/X]$, $1/\E X$ | E sqrt X 1.092830086; sqrt E X 1.125; E[1/X] 1; 1/E X 0.7901234568 | 1.0928, 1.125, 1, 0.7901 |
| A14-80 | Problem 10; a pitfall | from the printed 14.97%, 23.70%, 0.19, 5.02: (3.9); the three (14.13) terms; their sum; $R_G=e^{\ln1.1497-\text{sum}}-1$; (3.9) from unrounded inputs | (3.9) printed 12.16155%; terms 2.124700077, -0.05547838246, 0.2266203909; sum 2.295842085; R_G 12.36053952%; (3.9) unrounded 12.16678213% | 12.16%; 2.1247, −0.0555, 0.2266; 2.2958; 12.36%; 12.17% |
| A14-81 | limit regimes (lab) | returns dated to 2015-05-29 and from 2015-06-01 | T 3077 (to 2015-05-29); T 2772 (from 2015-06-01) | 3,077; 2,772 |
| A14-82 | LM5's $A$ | printed in lm05.md:521 (0050); not recomputed | printed in lm05.md:521: A = 243.1 (0050) | 243.1 |
| A14-83 | the pair from unrounded returns | as A14-31 with A14-06's unrounded returns: $\sigma^2/2$, $R_G$, $\ln(1+\mu)$ | sigma^2/2 19.97551938; R_G 2.166761225%; ln(1+mu) 18.34713094% | 19.98; 2.17%; 18.35% |

**Facts checked on official sources.** Each fact, where the brief uses it, and its source:

- The daily price limit, 7% until 29 May 2015 and 10% from 1 June 2015 (X5's note, the lab's regimes): sources.md
  item 25 (TWSE company history; TWSE 60th-anniversary book, p. 181), verified.
- TR23 reinvests cash dividends (X1's note, the case): sources.md item 24 (TWSE IndexS02 §四(一)2 and §五(六); the
  Taiwan Index Plus methodology), verified for the dividend rule.
- `scipy.stats.kurtosis` returns excess kurtosis from divisor-$T$ moments by default, and `scipy.stats.skew` uses
  `bias=True` (X9, E6): sources.md items 18 and 19, verified.
- LOTUS for densities, cited as Grinstead and Snell (1997), §6.3, Theorem 6.11: sources.md item 2, verified (read; the
  section and theorem numbers are the free edition's).
- Not in sources.md; checked by the reviser on 2026-10-18 on the NumPy v2.5 and SciPy v1.18.0 manuals (X9):
  `numpy.quantile(a, q, ..., method='linear', ...)` defaults to `'linear'` (Hyndman and Fan's estimator 7) and lists
  `'inverted_cdf'` as estimator 1, a method based on the empirical distribution function
  (<https://numpy.org/doc/stable/reference/generated/numpy.quantile.html>); `numpy.median` averages the two middle
  values when the count is even (<https://numpy.org/doc/stable/reference/generated/numpy.median.html>);
  `scipy.stats.rv_discrete(values=(xk, pk))` takes integer `xk`, its `median` is the median, `ppf` the inverse of the
  cdf, `moment` the non-central moment and `expect` a numerical sum
  (<https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.rv_discrete.html>); `scipy.stats.norm`'s `moment`
  is the non-central moment and `expect` the expected value of a function
  (<https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html>). Observed with NumPy 2.5.3 and SciPy
  1.18.1 (the project's lock): the die's `median()` and `ppf(0.5)` return 3, and `norm(...).expect(np.log1p)` returns
  `nan` with RuntimeWarnings.

## LM15

**Status.** Computed by the reviser on 2026-10-18 with data/vol3_anchors_lm15.py; not yet recomputed independently.

**Common definitions.** Sample: TR23, `data/processed/vol3_taiex.parquet` (built and checked by `data/vol3_series.py`; FinMind `TaiwanStockTotalReturnIndex`, TAIEX, retrieved 2026-10-18), closes 2003-01-02 → 2026-10-08. Return: $R_t=P_t/P_{t-1}-1$ (column `R`), $T=5{,}849$ from 2003-01-03; $r=\ln(1+R)$. Divisor $T$ for every moment (`ddof=0`; `stats.kurtosis` and `stats.skew` with their defaults). Years = calendar days ÷ 365.25 = 23.764545; $A=T/\text{years}=246.122955$. Counts against a threshold use the guard `R <= -x + 1e-12`, `R >= x - 1e-12` and equal an exact recount with `fractions.Fraction` from the two-decimal closes (asserted for $x=1\%,\dots,10\%$ and $\lvert R\rvert\ge3\%$). Empirical quantile: $\hat F^{-1}(u)=R_{(\lceil uT\rceil)}$. Limit regimes: returns dated before 2015-06-01 and from 2015-06-01. Calendar years 2003–2025, 2003 from its first close (2003-01-02). Seeds: none; LM15 simulates nothing. Every printed derived value is asserted from its printed inputs where the brief says so (PITFALLS §7).

| ID | Number | Definition (enough to reproduce it) | Value (unrounded, as the script prints) | Printed as |
|:--|:--|:--|:--|:--|
| A15-01 | large moves | days with $\lvert R\rvert\ge3\%$ (guard `abs(R) >= 0.03 - 1e-12`, equal to the `Fraction` recount), split into $R\le-3\%$ and $R\ge+3\%$; $p$ = count ÷ $T$ | 175 days with \|R\| >= 3% (108 with R <= -3%, 67 with R >= +3%); p = 175/5849 = 0.02991964 | 175; 108 against 67; $p=175/5{,}849=0.02992$ |
| A15-02 | TR23's skewness (LM14's) | `stats.skew(R)` (divisor-$T$ moments) | -0.338444 | −0.34 |
| A15-03 | $T$ | simple returns $R$ of the TR23 closes (parquet column `R`), first return 2003-01-03 | 5849 returns 2003-01-03 .. 2026-10-08; 5850 closes from 2003-01-02 | 5,849; 5,850 closes |
| A15-04 | days, years, $A$ | 2026-10-08 minus 2003-01-02 in days; ÷ 365.25; $T$ ÷ years | 8680 calendar days; 23.764545 years; A = 246.122955 | 8,680; 23.7645; 246.12 |
| A15-05 | blocks | consecutive blocks of 20 returns from the first return; the returns left over | 292 blocks of 20 from 2003-01-03; 9 returns left out, 2026-09-24 .. 2026-10-08 | 292; the last 9 (24 September – 8 October 2026) |
| A15-06 | months | calendar months of the return dates; sessions per month | 286 months 2003-01 .. 2026-10; sessions a month: mean 20.451049, min 6, max 24; 2003-01 has 18, 2026-10 has 6 | 286; January 2003 18 sessions, October 2026 6; about 20 a month; 6 to 24 |
| A15-07 | limit regimes (X9) | returns dated before 2015-06-01 and from it, and the full sample: $T$; $s$; `stats.kurtosis`; $4+6/\text{excess}$; `stats.t.fit` $\nu$; $\hat F^{-1}(0.01)=R_{(\lceil 0.01n\rceil)}$ of the part ($n$ its size); guarded count of $R\le-3\%$, per 1,000 | full: T 5849 (2003-01-03 .. 2026-10-08), s 1.2084%, excess kurtosis 5.2680, nu by kurtosis 5.1389, ML nu 3.0652, 1% quantile -3.5671%, <= -3% 108 (18.4647 per 1,000); 7% limit: T 3077 (2003-01-03 .. 2015-05-29), s 1.2570%, excess kurtosis 3.3926, nu by kurtosis 5.7685, ML nu 2.9898, 1% quantile -3.6206%, <= -3% 72 (23.3994 per 1,000); 10% limit: T 2772 (2015-06-01 .. 2026-10-08), s 1.1517%, excess kurtosis 8.0723, nu by kurtosis 4.7433, ML nu 3.2370, 1% quantile -3.4672%, <= -3% 36 (12.9870 per 1,000) | 3,077, 2,772; X9: 1.208 / 1.257 / 1.152; 5.27 / 3.39 / 8.07; 5.14 / 5.77 / 4.74; 3.065 / 2.990 / 3.237; −3.567 / −3.621 / −3.467; 18.5 / 23.4 / 13.0 |
| A15-08 | extremes | minimum and maximum of $R$ | min -9.6997% (2025-04-07); max 9.2512% (2025-04-10) | −9.6997% (7 April 2025); +9.2512% (10 April 2025) |
| A15-09 | $\bar R$ | mean of $R$ | 0.06250506% | 0.0625% |
| A15-10 | $s$ | standard deviation of $R$, divisor $T$ | 1.20836434% | 1.2084% (prose, E4, P5); 1.20836% (exhibit notes); 1.208 (X9) |
| A15-11 | normal days at −5% | $T\,\Phi\big((-0.05-\bar R)/s\big)$; from the printed 0.0625%, 1.20836%; with $s=1.2084\%$ | 0.081742; from the printed 0.0625% and 1.20836%: 0.081738; with s = 1.2084%: 0.081788 | 0.08 (case); 0.0817; 0.0818 with 1.2084% |
| A15-12 | TAIEX days at −5% | guarded count of $R\le-0.05$ | 15 | 15 |
| A15-13 | maximum-likelihood Student-t | `stats.t.fit(R)` → (df, loc, scale); Nelder–Mead on the negative log-likelihood from four starts agrees ($\lvert\Delta\nu\rvert<0.001$, no lower minimum) | nu 3.065223; loc 0.099725%; scale 0.776115% | $\nu=3.065$; location 0.0997%; scale 0.7761% |
| A15-14 | maximum-likelihood days at −5% | $T\,F_t(-0.05)$ under A15-13; from the printed parameters; with $\nu=3.07$ | 19.613844; from the printed 3.065, 0.0997%, 0.7761%: 19.617497; with nu 3.07: 19.517876 | 19.6; 19.5 with $\nu=3.07$ |
| A15-15 | $\hat\lambda$ | large-move days ÷ months | 175/286 = 0.61188811 | 175/286; 0.612 |
| A15-16 | monthly variance | variance of the 286 monthly counts of $\lvert R\rvert\ge3\%$, divisor 286 | 1.84587266 (divisor 286); divisor 285: 1.852349 | 1.846 |
| A15-17 | variance ÷ mean | A15-16 ÷ A15-15; from the printed 1.846 and 0.612; inverted (P3's A) | 3.016683; from the printed 1.846/0.612: 3.016340; 0.612/1.846 = 0.331528 | 3.02 ("three times"); 0.33 |
| A15-18 | months with eight | months whose count is 8, the maximum; 2008-12's count | 3 months with eight: 2008-09, 2008-10, 2020-03; 2008-12 has 6 | September and October 2008, March 2020; 2008-12 had six |
| A15-19 | 0050's normal verdict | printed in lm05.md:35 (0.058) and lm05.md:53 (9) | printed in lm05.md:35 (0.058 days expected) and lm05.md:53 (9 days actual) | 0.058 days expected at −5%, 9 actual |
| A15-20 | 1.96 | printed in lm04.md:541 | printed in lm04.md:541: 1.96, the value a standard normal variable exceeds with probability 2.5% | 1.96 |
| A15-21 | binomial mean and variance | $np$, $np(1-p)$ with $n=20$, $p=\hat p$ (A15-22); from the printed 0.548; standard deviation; $n/4$ | np = 10.958904; np(1-p) = 4.954025; from the printed 0.548: 4.953920; sd 2.225764; n/4 = 5 | 10.96; 4.95; 2.23 (P1's C); 5 |
| A15-22 | $\hat p$ | up days ($R>0$; no return is 0) among the first 5,840 returns ÷ 5,840 | 3200/5840 = 0.54794521 | 3,200/5,840; 0.548 |
| A15-23 | $\sigma$ for 15 days at −5% | $(-0.05-\bar R)/\Phi^{-1}(15/T)$; then $T\,\Phi\big((-0.02-\bar R)/\sigma\big)$, also from the printed 1.809% | Phi^-1(15/T) -2.798813; sigma 1.808804%; then days <= -2%: 743.3450; from the printed 1.809%: 743.4987 | 1.809%; 743 |
| A15-24 | TAIEX days at −2% … −10% | guarded counts of $R\le-x$, $x=2\%,\dots,10\%$ | 252, 108, 44, 15, 6, 2, 2, 1, 0 | 252, 108, 44, 15, 6, 2, 2, 1, 0 |
| A15-25 | normal on annual returns | $\Phi(-\text{mean}/\text{sd})$ of the 23 growth factors $G_y$ (A15-62), divisor 23; asserted from the printed 1.1497 and 0.2370 | Pr(G<0) = Phi(-1.149749/0.236984) = 6.1240e-07 | $6.1\times10^{-7}$ |
| A15-26 | kurtosis-matched Student-t | $\nu=4+6/\text{A15-49}$; scale $s\sqrt{(\nu-2)/\nu}$ (also from the printed 5.14 and 1.2084%); from the printed 5.27; P9's distractors $6/5.27$ and $4+6/8.27$ | nu 5.138946; scale 0.944393%; from the printed 5.27: 5.138520; 6/5.27 = 1.138520; 4 + 6/8.27 = 4.725514 | 5.14 (5.139 in exhibit notes); 0.944%; 1.14; 4.73 |
| A15-27 | maximum-likelihood days at −2% … −10% | $T\,F_t(-x)$ under A15-13; equal at the printed precision from the printed parameters | 209.826, 79.011, 36.643, 19.6138, 11.6145, 7.40591, 4.99527, 3.52077, 2.57063 | 210, 79.0, 36.6, 19.6, 11.6, 7.41, 5.00, 3.52, 2.57 |
| A15-28 | Student-t moments | $\nu/(\nu-2)$ and $3+6/(\nu-4)$ at $\nu=3,4,5,6$ (checked by `quad` at 5 and 6); SciPy's `t(5).stats(moments="k")`; LM5's value printed in lm05.md:343 | nu=3: variance 3.000000, kurtosis infinite; nu=4: variance 2.000000, kurtosis infinite; nu=5: variance 1.666667, kurtosis 9.000000; nu=6: variance 1.500000, kurtosis 6.000000; SciPy t(5).stats(moments='k') 6.0; LM5 prints 9 for t_5 (lm05.md:343) | 3, infinite; 2; 5/3, 9; 3/2, 6; 6 (SciPy) against 9 (LM5) |
| A15-29 | LM13's sign frequencies | $\Pr(R<0)$ over the $T$ days; over the 5,848 day-pairs $\Pr(R_t<0)$ and $\Pr(R_t<0\mid R_{t-1}<0)$ | Pr(R<0) 2644/5849 = 0.452043; on the 5848 day-pairs: Pr(R_t<0) = 0.452120, Pr(R_t<0 \| R_t-1<0) = 0.463867 | 0.4521; 0.4639 |
| A15-30 | block variance under sign dependence | $\rho_1$ = lag-1 correlation of the up-day indicators of the 5,840 block returns; $20\hat p(1-\hat p)\big(1+2\cdot\tfrac{19}{20}\rho_1\big)$ (LM16's variance of a sum) | lag-1 correlation of up-day indicators 0.020998; 20 p(1-p) (1 + 2 (19/20) rho1) = 5.151672 | 5.15 |
| A15-31 | block mean and variance | mean and variance (divisor 292) of up days per block | mean 10.958904; variance 4.717489 (divisor 292; divisor 291: 4.733701) | 10.96; 4.72 |
| A15-32 | Poisson expected months | $286\,p_X(j)$ under $\operatorname{Poisson}(\hat\lambda)$, $j=0,\dots,8$; $286\Pr(X\ge5)$; $286\Pr(X\ge8)$ | 155.1052, 94.9070, 29.0362, 5.9223, 0.9059, 0.111, 0.0113, 0.000988, 7.56e-05; five or more 0.123244 (observed 9); eight or more 8.1065e-05 | 155.1, 94.9, 29.0, 5.92, 0.906, 0.111, 0.0113, $9.9\times10^{-4}$, $7.6\times10^{-5}$; 0.123; $8.1\times10^{-5}$ |
| A15-33 | $\bar r$, $s_r$ | mean and standard deviation (divisor $T$) of $r=\ln(1+R)$ | rbar 0.05516962%; s_r 1.21072686% | 0.05517%; 1.2107% |
| A15-34 | daily lognormal at −5% | $T\,\Phi\big((\ln0.95-\bar r)/s_r\big)$; from the printed inputs | 0.054134; from the printed 0.05517%, 1.2107%: 0.054111 | 0.0541 |
| A15-35 | normal days at −2% … −10% | $T\,\Phi\big((-x-\bar R)/s\big)$; equal at the printed precision from 0.0625% and 1.20836% | 256.913, 32.9395, 2.26309, 0.0817415, 0.00153398, 1.48429e-05, 7.3673e-08, 1.86904e-10, 2.4172e-13 | 257, 32.9, 2.26, 0.0817, 0.00153, $1.5\times10^{-5}$, $7.4\times10^{-8}$, $1.9\times10^{-10}$, $2.4\times10^{-13}$ |
| A15-36 | observed blocks | blocks with $j$ up days, $j=4,\dots,17$ | 0, 2, 4, 13, 21, 38, 34, 59, 46, 39, 26, 7, 3, 0 | as the value |
| A15-37 | binomial expected blocks | $292\binom{20}{j}\hat p^j(1-\hat p)^{20-j}$, $j=4,\dots,17$; their sum | 0.3879, 1.5045, 4.5589, 11.0520, 21.7691, 35.1823, 46.9098, 51.6912, 46.9920, 35.0523, 21.2438, 10.3000, 3.9015, 1.1127; sum over 4..17: 291.6582 | 0.39, 1.50, 4.56, 11.05, 21.77, 35.18, 46.91, 51.69, 46.99, 35.05, 21.24, 10.30, 3.90, 1.11; 291.7 |
| A15-38 | observed months | months with $j$ days of $\lvert R\rvert\ge3\%$, $j=0,\dots,8$ | 210, 38, 9, 16, 4, 5, 1, 0, 3 | as the value |
| A15-39 | QQ points | $\big(\Phi^{-1}((j-\tfrac12)/T),(R_{(j)}-\bar R)/s\big)$ at ranks 1, $T$, 59; plotted: $\lvert x\rvert>2$ or rank 1, 11, 21, …, plus both ends | rank 1 (-3.758450, -8.078856); rank 5849 (3.758450, 7.604235); rank 59 (-2.326284, -3.003767); 824 points plotted, 266 with \|x\| > 2 | $(-3.758,-8.079)$; $(3.758,7.604)$; $(-2.326,-3.004)$; 824; 266 |
| A15-40 | $\mu_X$, $\sigma_X$ | mean and standard deviation (divisor 23) of $\ln G_y$ (A15-62) | mu_X 0.11646214; sigma_X 0.22207066 (divisor 23; divisor 22: 0.227062) | 0.11646; 0.22207; 0.222 |
| A15-41 | lognormal median, mean, sd | $e^{\mu_X}$, $e^{\mu_X+\sigma_X^2/2}$, $\sqrt{(e^{\sigma_X^2}-1)e^{2\mu_X+\sigma_X^2}}$, each also from the printed 0.11646, 0.22207; the median from 0.1165 | median 1.123515; mean 1.151563; sd 0.258914; from 0.1165: median 1.123558 | 1.1235; 1.1516 (+15.16%); 0.2589; 1.1236 |
| A15-42 | lognormal 5% and 95% | $e^{\mu_X\pm1.644854\,\sigma_X}$ (from the printed inputs too); $G$ of 2008 and 2009; 10% of 23 | 5% 0.779727; 95% 1.618882; outside: 2008 0.569312, 2009 1.833449; 10% of 23 = 2.3 | 0.7797; 1.6189; 0.5693; 1.8334; 2.3 |
| A15-43 | empirical median of $G$ | 12th of the 23 sorted factors | 1.151412 (2013) | 1.1514 (2013) |
| A15-44 | X6's $z$ | $(-x-\bar R)/s$, $x=2\%,\dots,10\%$ (equal at three decimals from 0.0625%, 1.20836%) | -1.706857, -2.534422, -3.361987, -4.189552, -5.017117, -5.844682, -6.672247, -7.499812, -8.327377 | three decimals in X6 |
| A15-45 | kurtosis-fit days at −2% … −10% | $T\,F_{t_\nu}\big((-x-\bar R)/\text{scale}\big)$ with A15-26; equal at the printed precision from $\nu=5.139$, 0.0625%, 1.20836% | 231.738, 64.3154, 21.1746, 8.17451, 3.59299, 1.75071, 0.926166, 0.523645, 0.312662 | 232, 64.3, 21.2, 8.17, 3.59, 1.75, 0.926, 0.524, 0.313 |
| A15-46 | tail index in the literature | printed in lm05.md:350 | printed in lm05.md:350: tail index of most return series between 2 and 5 (Cont 2001); alpha about 3 for index returns (Gopikrishnan et al. 1999) | 2–5; $\alpha\approx3$ (X8's slope −3) |
| A15-47 | chords (15.13) | $\ln[N(x_1)/N(x_2)]/\ln(x_2/x_1)$ with the guarded counts $N$ | counts at 2%..6%: 252, 108, 44, 15, 6; 2%->4% 2.517848; 3%->6% 4.169925; 4%->6% 4.913937; 2%->6% 3.402174 | 252, 108, 44, 15, 6; 2.52, 4.17, 4.91, 3.40 |
| A15-48 | overdispersion by regime | variance ÷ mean of the monthly counts, months 2003-01 … 2015-05 (149) and 2015-06 … 2026-10 (137) | months 149 / 137: variance / mean 2.954198 / 3.013761 | 2.95; 3.01 |
| A15-49 | excess kurtosis | `stats.kurtosis(R)` = mean$((R-\bar R)^4)/s^4-3$ | 5.268030 | 5.27 |
| A15-50 | empirical quantiles | $\hat F^{-1}(u)=R_{(\lceil uT\rceil)}$, equal to `np.quantile(R, u, method="inverted_cdf")` | 0.001: #6 -6.3125%; 0.01: #59 -3.5671%; 0.025: #147 -2.6480%; 0.05: #293 -1.8621%; 0.5: #2925 0.0879%; 0.95: #5557 1.8329%; 0.99: #5791 3.1252%; #6 is 2018-10-11; linear default at 0.01: -3.5668% | −6.313% (rank 6, 11 October 2018); −3.567% (59); −2.648% (147); −1.862% (293); +3.125% (5,791) |
| A15-51 | normal quantiles | $\bar R+s\,\Phi^{-1}(u)$ (also from 0.0625%, 1.2084% and four-decimal $\Phi^{-1}$) | 0.001: -3.6716%; 0.01: -2.7486%; 0.025: -2.3058%; 0.05: -1.9251%; 0.99: 2.8736% | −3.672%; −2.749%; −2.306%; −1.925%; +2.874% |
| A15-52 | maximum-likelihood 1% quantile | `stats.t.ppf(0.01, ν, loc, scale)`; from the printed parameters | 1%: -3.3651% (from the printed parameters -3.3653%); 5%: -1.7110% | −3.365% |
| A15-53 | annual means | mean of $G_y$ minus 1; $\exp(\text{mean}\ln G_y)-1$ | arithmetic 14.9749%; compound 12.3515% | 14.97%; 12.35% |
| A15-54 | `norm.fit` | `stats.norm.fit(R)` minus $(\bar R,s)$ | norm.fit - (Rbar, s): 0.000e+00, 0.000e+00 | returns $\bar R$ and $s$ exactly |
| A15-55 | maximum-likelihood $\sigma$ | scale $\times\sqrt{\nu/(\nu-2)}$ (also from the printed parameters); ÷ $s$ | 1.316548%; / s = 1.089529 | 1.317%; 9% above $s$ |
| A15-56 | binomial tails (E1) | $\operatorname{Bin}(20,0.548)$: $\Pr(X\le5)$, $\Pr(X\ge16)$, × 292 (also from the printed probabilities); observed; with the unrounded $\hat p$ | Pr(X<=5) 0.006768 -> 1.9762 blocks (observed 2); Pr(X>=16) 0.018068 -> 5.2757 (observed 3); from the unrounded p: 1.9789, 5.2695; 292 x 0.0181 = 5.2852 | 0.00677, 1.98 (2); 0.01807, 5.28 (3); 5.27; 0.0181 would give 5.29 |
| A15-57 | rare binomial against Poisson | pmfs of $\operatorname{Bin}(20,0.02992)$ and $\operatorname{Poisson}(0.5984)$ at $j=0,1,2$ | j=0: Bin(20, 0.02992) 0.544692 against Poisson(0.5984) 0.549690; j=1: Bin(20, 0.02992) 0.335997 against Poisson(0.5984) 0.328935; j=2: Bin(20, 0.02992) 0.098449 against Poisson(0.5984) 0.098417 | 0.5447 / 0.5497; 0.3360 / 0.3289; 0.09845 / 0.09842 |
| A15-58 | $(1-0.612/n)^n$ | $n=20$, 250, 10,000; $e^{-0.612}$ | n=20: 0.537106; n=250: 0.541859; n=10000: 0.542255; e^-0.612 = 0.542265 | 0.53711, 0.54186, 0.54226; 0.54227 |
| A15-59 | $\operatorname{Poisson}(0.612)$ | $\Pr(X=0)$, $\Pr(X\ge5)$, × 286 | Pr(X=0) 0.542265; Pr(X>=5) 0.00043128; x286: 155.0879, 0.123345 | 0.5423; 0.000431; 155.1; 0.123 |
| A15-60 | unequal months | $\bar n\,p(1-p)+p^2\operatorname{var}(n)$, $n$ the sessions of each of the 286 months (divisor 286), $p=175/5{,}849$ | 0.599092 (mean sessions 20.4510, variance 6.1567, p = 175/5849) | 0.60 |
| A15-61 | $\Phi^{-1}$ | `stats.norm.ppf` at 0.95, 0.975, 0.99, 0.999 | 0.95: 1.644854; 0.975: 1.959964; 0.99: 2.326348; 0.999: 3.090232 | 1.6449, 1.9600, 2.3263, 3.0902 |
| A15-62 | 23 calendar-year returns | $G_y-1$, $G_y$ = last close of year $y$ ÷ last close of $y-1$; 2003 from the close of 2 January 2003 | 2003 33.0757%, 2004 7.5932%, 2005 10.9417%, 2006 24.4410%, 2007 12.4964%, 2008 -43.0688%, 2009 83.3449%, 2010 13.5736%, 2011 -17.9789%, 2012 12.9415%, 2013 15.1412%, 2014 11.3898%, 2015 -6.8712%, 2016 15.5898%, 2017 19.5234%, 2018 -4.8270%, 2019 28.9193%, 2020 27.1215%, 2021 27.0631%, 2022 -18.6772%, 2023 31.4827%, 2024 31.7330%, 2025 29.4731% | the 23 factors of X5 (lab) |
| A15-63 | lognormal losing year | $\Phi(-\mu_X/\sigma_X)$ (from the printed inputs too); $\Phi(+\mu_X/\sigma_X)$; × 23; losing years | Phi(-0.524437) = 0.299987; Phi(+0.524437) = 0.700013; x 23 = 6.8997; losing years 5 (2008, 2011, 2015, 2018, 2022) = 0.217391 | $\Phi(-0.5244)=30.0\%$; 70.0%; 6.90; 5 (2008, 2011, 2015, 2018, 2022), 21.7% |
| A15-64 | LM17's daily model, one year | $m=\operatorname{round}(A)=246$; $\Phi(-\bar r\sqrt m/s_r)$; $s_r\sqrt m$ | m = 246: Phi(-rbar sqrt(m)/s_r) = 0.237398; s_r sqrt(m) = 0.189895 | 23.7%; 0.190 |
| A15-65 | $\Gamma$ | `special.gamma` at 1/2, 3/2, 2, 5/2 | Gamma(1/2) 1.772454 (sqrt(pi) 1.772454); Gamma(3/2) 0.886227; Gamma(2) 1.000000; Gamma(5/2) 1.329340 | 1.772454, 0.886227, 1, 1.329340 |
| A15-66 | (15.9)'s constant | $\Gamma((\nu+1)/2)/\big(\sqrt{\nu\pi}\,\Gamma(\nu/2)\big)$ at $\nu=1,3,4,30,1000$; $1/\sqrt{2\pi}$; the density integrates to 1 (`quad`) at both fitted $\nu$ | nu=1: 0.318310; nu=3: 0.367553; nu=4: 0.375000; nu=30: 0.395632; nu=1000: 0.398843; 1/sqrt(2 pi) 0.398942; 2/(pi sqrt 3) 0.367553 | 0.3183; 0.3676; 3/8; 0.3956; 0.3988; 0.3989 |
| A15-67 | sample median | $R_{(2925)}$ | #2925 0.0879% | 0.0879% |
| A15-68 | model chords 3%→6% | (15.13) on model probabilities: normal, maximum likelihood, kurtosis fit | 3%->6%: normal 14.390254; ML t 2.766121; kurtosis-fit t 4.161908 | 14.4; 2.77; 4.16 |
| A15-69 | 7 April 2025 | returns to 2025-04-02 (5,478) and to 2025-04-07 (5,479): `stats.kurtosis`, $\hat F^{-1}(0.01)$, guarded count of $R\le-3\%$; whole sample without that day | returns to 2025-04-02 (5478) then to 2025-04-07 (5479): excess kurtosis 4.2464 -> 4.9386; 1% quantile -3.5382% -> -3.5430%; <= -3% 96 -> 97; whole sample without 2025-04-07: 4.7110 | 4.25 → 4.94; −3.538% → −3.543%; 96 → 97; 4.71 |
| A15-70 | without the four largest moves | `stats.kurtosis` without the four largest $\lvert R-\bar R\rvert$ | without the four largest \|R - Rbar\| (2025-04-07, 2025-04-10, 2024-08-05, 2026-07-31): 3.7351 | 3.74 (7 and 10 April 2025, 5 August 2024, 31 July 2026) |
| A15-71 | top-ten shares | the ten largest $(R-\bar R)^4$: their share of $\sum(R-\bar R)^4$ and of $\sum(R-\bar R)^2$ | 34.9933% of sum (R - Rbar)^4; 6.6648% of sum (R - Rbar)^2 | 35.0%; 6.7% |
| A15-72 | 0050's kurtosis path | printed in lm05.md:367 | printed in lm05.md:367: 8.12; 7.05 without 7 April 2025; 3.85 without the four largest moves; 5.84 -> 7.63 | 8.12, 7.05, 3.85, 5.84 → 7.63 |
| A15-73 | 0050's top-ten shares | printed in lm05.md:369 | printed in lm05.md:369: 62.8% of sum (R - mu)^4, 14.1% of sum (R - mu)^2 | 62.8%; 14.1% |
| A15-74 | tail means at −5% | mean of the guarded $R\le-5\%$; (5.11) with $\bar R$, $s$; $\int_{-\infty}^{-0.05}x f_t\,dx/F_t(-0.05)$ under A15-13 (`quad`) | data -6.2635%; normal (5.11) -5.2623%; ML t -7.5738% | −6.26%; −5.26%; −7.57% |
| A15-75 | P5's gaps | $-2.749-(-3.567)$; $3.125-2.874$ (printed values) | from the printed quantiles: 1% 0.818; 99% 0.251 percentage points | 0.82; 0.25 |
| A15-76 | upper tail | guarded counts of $R\ge3\%$, $5\%$; $T(1-\Phi)$ and $T(1-F_t)$ (also from the printed parameters) | +3%: 67, normal 44.0387, ML 94.1855; +5%: 13, normal 0.128295, ML 22.0154 | 67, 13; 44.0, 0.128; 94.2, 22.0 |
| A15-77 | 7%-regime extremes | minimum and maximum of $R$ before 2015-06-01 | before 2015-06-01: min -6.6789% (2004-03-22), max 6.7420% (2009-04-30) | −6.6789% (22 March 2004); +6.7420% (30 April 2009) |

**Facts checked on official sources** (items of `v3briefs/sources.md`, all read on 2026-10-18).

- TWSE daily price limit raised from 7% to 10% on 1 June 2015 (item 25, verified; TWSE company history and 60th-anniversary book, both in `project/SOURCES.md`): Data role, X9, §7 pitfall.
- The TAIEX total-return index reinvests cash dividends (item 24, dividend rule verified; TWSE IndexS02 and Taiwan Index Plus): Data role. Its base value and launch date are not used.
- SciPy 1.18: `lognorm(s, scale)` with `s` $=\sigma_X$, `scale` $=e^{\mu_X}$ (item 15, verified); `t(df, loc, scale)` gives the standardized pdf (15.9) and `t.pdf(y, df)/scale`, variance `scale²·df/(df−2)` for `df > 2` by computation (item 16); `fit` is maximum likelihood by default (item 17, verified); `kurtosis` defaults `fisher=True`, `bias=True`, excess kurtosis with divisor-$N$ moments (item 18, verified); `poisson(mu)` pmf $e^{-\mu}\mu^k/k!$ (item 23, verified). Computed, not read on a reference page: `t(5).stats(moments="k")` returns 6.0 (A15-28); `norm.fit` returns $(\bar R,s)$ (A15-54); `np.quantile(..., method="inverted_cdf")` equals $R_{(\lceil uT\rceil)}$ (A15-50).
- Reference: Grinstead and Snell, *Introduction to Probability*, 2nd revised ed. (AMS), §5.1, subsection "Poisson Distribution", Table 5.1 "Poisson approximation to the binomial distribution" (item 2, verified, read): §3's further reading.

## LM16

**Status.** Computed by the reviser on 2026-10-18 with data/vol3_anchors_lm16.py; not yet recomputed independently.

**Common definitions.** Sample U28: `data/processed/vol2_closes.parquet` (built and repaired by `data/vol2_series.py`),
the 28 TWSE sector indices other than Electronic and ChemicalBiotechnologyMedicalCare and the TAIEX price index, closes
2008-12-01 → 2026-10-08, loaded as `data/lm10_series.py` does. Returns $R_t=P_t/P_{t-1}-1$ between consecutive rows
(price returns, no dividends), $T=4{,}382$ from 2008-12-02; log returns $r=\ln(1+R)$ only for §4's sum. Means, standard
deviations, covariances and $\hat\Sigma$ divide by $T$ (a bin's statistics by its days); $\hat\rho$ is (8.9).
Years = calendar days ÷ 365.25; $A=T/\text{years}$, printed 245.48. Standardized thresholds use the full-sample mean and
divisor-$T$ standard deviation. Counts use the guard (`<= -x + 1e-12`, `>= x - 1e-12`; inside $d_t^2\le k^2+10^{-12}$)
and counts on returns are recounted exactly with `Fraction` on the two-decimal closes. $d_t^2$ by `np.linalg.cholesky`
and `solve_triangular`. Seeds: none; LM16 draws no random numbers. "From printed inputs" means the inputs at the
precision the brief prints them. Values are in the units of the Number column (% or %² where stated). LM16 reads no
TR23 data.

| ID | Number | Definition (enough to reproduce it) | Value (unrounded, as the script prints) | Printed as |
|:--|:--|:--|:--|:--|
| A16-01 | $T$; first, last return | returns between consecutive U28 closes, 2008-12-01 … 2026-10-08 | 4382; 2008-12-02; 2026-10-08 | 4,382; 2008-12-02; 2026-10-08 |
| A16-02 | calendar days; years | 2026-10-08 minus 2008-12-01 in days; ÷ 365.25 | 6520; 17.8507871321 | 6,520; 17.8508 |
| A16-03 | $A$ | $T$ ÷ years; printed 245.48 in lm10.md:41 | 245.479371166 | 245.4794; 245.48 |
| A16-04 | repaired closes | `vol2_repairs.json` entries of a U28 series dated 2008-12-01 … 2026-10-08; their distinct dates (printed in lm12.md:54) | 524; 38 | 524; 38 |
| A16-05 | repairs on key dates | entries (U28 or TAIEX) dated 2025-04-07 … 2025-04-10, 2024-08-05, 2009-05-05 or the close before each | 0 | none |
| A16-06 | $\hat\rho$ of the pair | Semiconductor, FinancialInsurance, (8.9) on all $T$ returns; printed in lm08.md:345 | 0.5748584673 | 0.5749 |
| A16-07 | three-day $\hat\rho$ | (8.9) on LM10's printed returns −9.95, −3.99, −4.47 and −9.89, 0.53, −5.61 (lm10.md:107–109); printed in lm10.md:122 | 0.8505589922 | 0.851 |
| A16-08 | 7 April 2025 returns (%) | Semiconductor, FinancialInsurance, from the 2025-04-02 closes; printed in lm10.md:107 | -9.952905846; -9.889390915 | −9.95; −9.89 ("about 9.9%") |
| A16-09 | pair $d^2$ on 7 April; rank | $(\mathbf R_t-\bar{\mathbf R})^{\top}\hat\Sigma^{-1}(\mathbf R_t-\bar{\mathbf R})$, pair, divisor $T$; rank among $T$ days | 72.04702712; 1 | 72.05; 1 ("most extreme") |
| A16-10 | days outside radius 3 | pair days without $d_t^2\le9+10^{-12}$ | 177 | 177 |
| A16-11 | model count: mean; variance; SD | $Tp$, $Tp(1-p)$, $\sqrt{Tp(1-p)}$, $p=e^{-4.5}$ | 48.67962283; 48.13884107; 6.938215986 | 48.68 (48.7; "about 49"); 48.14; 6.94 |
| A16-12 | $\bar r$; $s_r$ (%) | $\ln(1+R)$ of the TAIEX price index on U28 dates; mean, SD divisor $T$ | 0.05454203725; 1.139215684 | 0.05454; 1.1392 |
| A16-13 | $m$ | $\operatorname{round}(A)$, sessions in a model year | 245 | 245 |
| A16-14 | year's log return: mean; SD (%) | $m\bar r$, $\sqrt m\,s_r$ unrounded; then $245\times0.05454$, $\sqrt{245}\times1.1392$ (printed inputs) | 13.36279913; 17.83154597; 13.3623; 17.83130048 | 13.36; 17.83 |
| A16-15 | equal-weight mean of bin means (%) | mean of the printed −0.9505, 0.0730, 0.8458 | -0.01056666667 | −0.0106 |
| A16-16 | $\ell$ at $k=2$ | $\varphi(2)/\Phi(-2)$; LM5 printed $\E[Z\mid Z\le-2]=-2.3732$ (lm05.md:759) | 2.373215533 | 2.3732 |
| A16-17 | KC §2 | 20/538 | 0.03717472119 | 0.0372 |
| A16-18 | KC §4 | $4+9$; $4/\sqrt{4\cdot13}$ | 13; 0.5547001962 | 13; 0.555 |
| A16-19 | U28 $d_t^2$: 7 April; rank; maximum; date | 28-dimensional $d_t^2$ with U28's means and $\hat\Sigma$ (divisor $T$) | 132.2895003; 15; 209.5521326; 2009-05-05 | 132.29; 15th; 209.55; 2009-05-05 |
| A16-20 | 7 April share along $\mathbf q_1$; 5 May 2009 lowest, highest sector return; TAIEX price index (%) | $(\mathbf q_1^{\top}\mathbf x)^2/\mathbf x^{\top}\mathbf x$, $\mathbf x=\mathbf R_t-\bar{\mathbf R}$, $\mathbf q_1$ the top eigenvector of U28's $\hat\Sigma$ | 0.9714643806; -3.71049949; 6.059395392; 0.7825729812 | 97.1%; −3.71; +6.06; 0.78 |
| A16-21 | $\Var(Z\mid\lvert Z\rvert\ge k)$; $\Var(Z\mid Z\le-k)$, $k=1,2,2.5$ | $1+k\varphi(k)/\Phi(-k)$; $1+k\ell-\ell^2$, $\ell=\varphi(k)/\Phi(-k)$ | 2.525135276, 5.746431066, 8.056861994; 0.1990976656, 0.1142791004, 0.08897380142 | 2.5251, 5.7464, 8.0569; 0.1991, 0.1143, 0.0890 |
| A16-22 | KC §7 | (16.10) with the printed 0.5749 and 2.5251 | 0.7449015895 | 0.745 |
| A16-23 | $\Pr(d^2>9)$ under $\mathcal N_2$ | $e^{-4.5}$ | 0.01110899654 | 0.011109; 1.11% |
| A16-24 | X2 cells | rows Semiconductor, columns FinancialInsurance; bins $R\le-0.01+10^{-12}$, between, $R\ge0.01-10^{-12}$; the `Fraction` recount is equal | 347, 478, 34 / 171, 2100, 248 / 20, 654, 330 | 347, 478, 34 / 171, 2,100, 248 / 20, 654, 330 |
| A16-25 | X2 margins | row totals; column totals | 859, 2519, 1004; 538, 3232, 612 | 859, 2,519, 1,004; 538, 3,232, 612 |
| A16-26 | returns of exactly ±1% | exact returns (`Fraction`) of either index equal to ±1/100 | 0 | none |
| A16-27 | pairs; $\hat\rho(R_t,R_{t+1})$; $\hat\rho(\lvert R_t\rvert,\lvert R_{t+1}\rvert)$ | TAIEX price index, U28 dates, $t=1,\dots,T-1$ | 4381; 0.04028528512; 0.1831384229 | 4,381; 0.040; 0.183 |
| A16-28 | days with $\lvert R_t\rvert\ge2\%$; mean $\lvert R_{t+1}\rvert$ after them, after the others, overall (%) | guard $\ge0.02-10^{-12}$, `Fraction` recount equal; $t\le T-1$ | 306; 1.282259859; 0.7536877631; 0.7906069736 | 306; 1.28; 0.75; 0.79 |
| A16-29 | X3: days; mean $R_t$; mean $R_{t+1}$; mean $\lvert R_{t+1}\rvert$ (%) | bins $(\text{lower},\text{upper}]$ at −3 … 3%, guard $R_t>\text{lower}+10^{-12}$, $R_t\le\text{upper}+10^{-12}$; `Fraction` recount equal | 60, 95, 389, 1433, 1770, 483, 112, 39; -4.1416, -2.4494, -1.3877, -0.4033, 0.4305, 1.3867, 2.4174, 4.2277; -0.0614, 0.2245, 0.0037, 0.0039, 0.0730, 0.1366, 0.2877, 0.4881; 2.0152, 1.2027, 0.9057, 0.8043, 0.6960, 0.6925, 0.9259, 1.3718 | 60, 95, 389, 1,433, 1,770, 483, 112, 39; −4.1416, −2.4494, −1.3877, −0.4033, 0.4305, 1.3867, 2.4174, 4.2277; −0.0614, 0.2245, 0.0037, 0.0039, 0.0730, 0.1366, 0.2877, 0.4881; 2.0152, 1.2027, 0.9057, 0.8043, 0.6960, 0.6925, 0.9259, 1.3718 |
| A16-30 | FinancialInsurance mean; SD by Semiconductor's bin (%) | X2's row bins; divisor the bin's days | -0.95045364, 0.073010791, 0.84583083; 1.4122139, 0.84256067, 1.2200756 | −0.9505, 0.0730, 0.8458; 1.4122, 0.8426, 1.2201 |
| A16-31 | within; between; total (%²); share (%) | $\sum(\text{days}/T)\,\text{var}$; $\sum(\text{days}/T)(\text{mean}-\bar R_2)^2$; variance of FinancialInsurance | 1.140105709; 0.3416230248; 1.481728733; 23.05570629 | 1.140; 0.342; 1.482; 23.1 |
| A16-32 | the same from X4's printed values; weighted mean (%) | weights 859, 2,519, 1,004 over 4,382 | 1.140149772; 0.3416296576; 1.481779429; 23.05536511; 0.04942736194 | 1.140; 0.342; 1.482; 23.1; 0.0494 |
| A16-33 | daily means (%) | Semiconductor; FinancialInsurance | 0.09470490744; 0.0494497173 | 0.0947; 0.0494 |
| A16-34 | $\hat\rho^2$ | square of A16-06 | 0.3304622575 | 0.3305 |
| A16-35 | $\hat\Sigma$ entries (%², daily) | $\hat\sigma_{11}$, $\hat\sigma_{21}$, $\hat\sigma_{22}$ × 10⁴; printed in lm12.md:431 as ×10⁻⁴ | 2.323354; 1.066603; 1.481729 | 2.323354; 1.066603; 1.481729 |
| A16-36 | share inside, $k=1,2,3$: model; data (%) | $1-e^{-k^2/2}$; share of days with $d_t^2\le k^2+10^{-12}$ | 39.34693403; 86.46647168; 98.88910035; 56.16157006; 87.95070744; 95.96074852 | 39.35, 86.47, 98.89; 56.16, 87.95, 95.96 |
| A16-37 | pair, $k=1,\dots,5$: model share outside (%); expected; actual | $e^{-k^2/2}$; $Te^{-k^2/2}$; days without $d_t^2\le k^2+10^{-12}$ | 60.6531, 13.5335, 1.1109, 0.0335463, 0.000372665; 2657.82, 593.039, 48.6796, 1.47, 0.0163302; 1921, 528, 177, 61, 25 | 60.65, 13.53, 1.11, 0.0335, 0.00037; 2,657.8, 593.0, 48.7, 1.47, 0.016; 1,921, 528, 177, 61, 25 |
| A16-38 | S5: $\chi^2_5$ quantiles; expected beyond; actual beyond | `stats.chi2.ppf(q, 5)`, $q=0.5,0.9,0.99,0.999$; $T(1-q)$; S5 days without $d_t^2\le c+10^{-12}$ | 4.35146, 9.23636, 15.0863, 20.515; 2191, 438.2, 43.82, 4.382; 1411, 613, 291, 184 | 4.35, 9.24, 15.09, 20.52; 2,191, 438.2, 43.8, 4.4; 1,411, 613, 291, 184 |
| A16-39 | benchmark correlation, $k=0,1,2$ | standard normal pair, $\rho=$ A16-06 unrounded, given both $\le-k$: moments by `quad` over $x\le-k$ of the truncated-normal moments of $Y$ given $X=x$ | 0.3323344912; 0.2288472697; 0.156000637 | 0.332, 0.229, 0.156 |
| A16-40 | joint falls: days, $\hat\rho$, $k=0,1,2$ | both $(R_{j,t}-\bar R_j)/s_j\le-k+10^{-12}$ | 1509 0.5752018373; 228 0.4645378; 44 0.6689681893 | 1,509, 0.575; 228, 0.465; 44, 0.669 |
| A16-41 | joint rises: days, $\hat\rho$ | both $(R_{j,t}-\bar R_j)/s_j\ge k-10^{-12}$ | 1523 0.4296914637; 170 0.4517984494; 32 0.5414590214 | 1,523, 0.430; 170, 0.452; 32, 0.541 |
| A16-42 | model probability (expected days), $k=0,1,2$ | as A16-39; × $T$ | 0.3474714477 (1522.619884); 0.06989208099 (306.2670989); 0.00510199255 (22.35693136) | 0.3475 (1,522.6); 0.0699 (306.3); 0.0051 (22.4) |
| A16-43 | $\lvert$Semiconductor$\rvert\ge k$ sd, $k=1,2,2.5$: days; data; model | standardized $\lvert\cdot\rvert\ge k-10^{-12}$; (16.10) with A16-06 unrounded and A16-21 | 1088, 223, 111; 0.6916236859, 0.7884464211, 0.8110685472; 0.7448681252, 0.8598424221, 0.8939015054 | 1,088, 223, 111; 0.692, 0.788, 0.811; 0.745, 0.860, 0.894 |
| A16-44 | Semiconductor $\le-k$ sd: days; data; model | standardized $\le-k+10^{-12}$ | 550, 105, 47; 0.4740481686, 0.488211645, 0.4851603668; 0.2991247039, 0.2310690026, 0.2051029882 | 550, 105, 47; 0.474, 0.488, 0.485; 0.299, 0.231, 0.205 |
| A16-45 | Semiconductor $\ge k$ sd: days; data | standardized $\ge k-10^{-12}$ | 538, 118, 64; 0.3671363792, 0.428688774, 0.3816362751 | 538, 118, 64; 0.367, 0.429, 0.382 |
| A16-46 | widget interpolation error | max over $k=0,0.05,\dots,2.5$ of the error of linear interpolation between $\rho=0.57$ and 0.58 at 0.5749 (joint falls); the script also asserts the initial state prints 0.156, 0.0051, 22.4 | 2.565e-05 | below $3\times10^{-5}$ |
| A16-47 | 347/T; 859/T; 538/T; product; ratio; ratio of printed 0.0792/0.0241 | X2's counts | 0.07918758558; 0.1960292104; 0.1227749886; 0.02406748407; 3.290231141; 3.286307054 | 0.0792; 0.1960; 0.1228; 0.0241; 3.29; 3.29 |
| A16-48 | conditionals | 347/859; 20/1,004 | 0.4039580908; 0.01992031873 | 0.404; 0.0199 |
| A16-49 | E2 (exact) | integrals over $[0,1]^2$ of $x+y$: total; $\E X$; $\E X^2$; $\Var X$; $\E[XY]$; Cov; ρ; $\Pr(X,Y\le\tfrac12)$; $\E[Y\mid X=0]$, $\E[Y\mid X=1]$ | 1; 7/12; 5/12; 11/144; 1/3; -1/144; -0.006944444444; -1/11; -0.09090909091; 1/8; 2/3; 5/9 | 1; 7/12; 5/12; 11/144; 1/3 = 0.3333; −1/144 = −0.0069; −1/11 = −0.0909; 1/8; 2/3; 5/9 |
| A16-50 | E3 (exact) | $\Cov(X,X^2)$, $X$ uniform on $\{-1,0,1\}$; $\Pr(X^2=0)$ | 0; 1/3 | 0; 1/3 |
| A16-51 | LM10's $A\hat\Sigma_3$ entries (%²) | printed in lm10.md:61 | 570.34; 261.83; 363.73 (printed in lm10.md:61) | 570.34, 261.83, 363.73 |
| A16-52 | $\sigma_p^2$; $\sigma_p$; $\Cov(R_1,R_p)$; $\Var(R_1-R_2)$; root | from A16-51: $0.25a_{11}+0.5a_{12}+0.25a_{22}$; $0.5a_{11}+0.5a_{12}$; $a_{11}+a_{22}-2a_{12}$ (the last pair printed in lm10.md:63) | 364.4325; 19.09011524; 416.085; 410.41; 20.25857843 | 364.43; 19.09%; 416.085; 410.41; 20.26% |
| A16-53 | daily SDs (%) | Semiconductor; FinancialInsurance; divisor $T$ | 1.524255234; 1.217262804 | 1.5243; 1.2173 |
| A16-54 | $\beta$; $\E[Y\mid X=-5\%]$; SD; $z$; probability | printed inputs 0.0947, 0.0494, 1.5243, 1.2173, 0.5749; $\beta$ and 0.996 printed in lm12.md:436 | 0.4591128846; -2.289642413; 0.9960236853; -0.7131934685; 0.2378630237 | 0.4591; −2.29%; 0.996%; −0.713; 0.238 |
| A16-55 | the same from unrounded moments | $\beta$; mean (%); SD (%) | 0.4590791713; -2.28942319; 0.9960287703 | 0.4591; −2.29; 0.996 |
| A16-56 | days; FinancialInsurance mean, SD (%); days $\le-3\%$ | Semiconductor in $[-0.055-10^{-12},-0.045+10^{-12}]$ | 17; -2.86025369; 1.99648776; 6 | 17; −2.86; 2.00; 6 |
| A16-57 | S5 $d^2$ on 7 April; rank | printed 89.30 in lm12.md:483 | 89.29919741; 1; 89.30 (printed in lm12.md:483) | 89.30; 1 |
| A16-58 | $\Pr(\chi^2_5\ge89.30)$; years per occurrence | `stats.chi2.sf(89.30, 5)`; $1/(p\times245.48)$ | 9.42658e-18; 4.32145e+14 | $9.4\times10^{-18}$; about $4\times10^{14}$ |
| A16-59 | Semiconductor 7–9 April (sd) | $(r-0.0947)/1.5243$, $r$ = −9.95, −3.99, −4.47 | -6.589713311; -2.67972184; -2.994620482 | −6.59; −2.68; −2.99 |
| A16-60 | P1 distractors C; A | 347/538; 347/4,382 to three decimals | 0.6449814126; 0.07918758558 | 0.645; 0.079 |
| A16-61 | P4 (constructed) | $\sigma_1=0.20$, $\sigma_2=0.15$, $\rho=0.5$, weights 0.6, 0.4: $\sqrt{\Var(R_1-R_2)}$; $\Cov(R_1,R_p)$; $\sigma_p$; Corr; $\lvert\sigma_1-\sigma_2\rvert$; $\sqrt{\sigma_1^2+\sigma_2^2}$ | 0.1802775638; 0.03; 0.1587450787; 0.9449111825; 0.05; 0.25 | 18.03%; 0.0300; 15.87%; 0.945; 5%; 25% |
| A16-62 | P5: factor; SD (%) | $1+2(0.04)(m-1)/m$; $\sqrt m\times1.1392\times\sqrt{\text{factor}}$ | 1.079673469; 18.52802949 | 1.0797; 18.53 |
| A16-63 | P5 wrong routes (%) | $m\times1.1392$; $17.83\times$factor; unrounded $\sqrt m\times1.1392\times$factor | 279.104; 19.25057796; 19.25198205 | 279.1; 19.25; 19.25 |
| A16-64 | P6 inputs: days; means; SDs (%) | TAIEX price index $R_{t+1}$ after $\lvert R_t\rvert\ge2\%$ and after the others; divisor each group's days | 306; 4075; 0.2251416352; 0.0496074729; 1.888862723; 1.056986426 | 306; 4,075; 0.2251; 0.0496; 1.8889; 1.0570 |
| A16-65 | P6 key | from the printed inputs, weights days/4,381: mean (%); within; between; total (%²); share (%); then the unrounded mean and variance | 0.06185816024; 1.288422802; 0.002001044629; 1.290423847; 0.1550687887; 0.06186801927; 1.290388098 | 0.0619; 1.288; 0.002; 1.290; 0.16; 0.0619; 1.290 |
| A16-66 | SD ratio; equal-weight mean (%) | 1.8889/1.0570; (0.2251 + 0.0496)/2, exact and as a float | 1.787038789; 2747/20000; 0.13735 | 1.79; 0.13735 |
| A16-67 | P7 key and distractors | printed inputs at $X=-3\%$: mean (%); $z$; probability; probability with SD 1.2173; mean with slope 0.5749 (%) | -1.371416644; -0.6310927795; 0.263989931; 0.3027962419; -1.72974303 | −1.37; −0.631; 0.264; 0.303; −1.73 |
| A16-68 | 5 August 2024 returns (%) | Semiconductor; FinancialInsurance | -9.483723161; -6.931030288 | −9.48; −6.93 |
| A16-69 | LM12's $L$ for the pair (% a day) | printed in lm12.md:441–442 | 1.5243; 0.6998; 0.9960 (printed in lm12.md:441-442) | 1.5243, 0.6998, 0.9960 |
| A16-70 | $z_1$; $z_2$; $d^2$; unrounded $d^2$ | $z_1=(-9.48-0.0947)/1.5243$, $z_2=(-6.93-0.0494-0.6998z_1)/0.9960$; then the unrounded pair $d_t^2$ on 2024-08-05 | -6.281375057; -2.594070015; 46.18487185; 46.21508321 | −6.281; −2.594; 46.18; 46.22 |
| A16-71 | $d^2/2$; $e^{-d^2/2}$; × $T$ | from A16-70's 46.18… | 23.09243593; 9.35583e-11; 4.09973e-07 | 23.09; $9.4\times10^{-11}$; about $4\times10^{-7}$ |
| A16-72 | P10 | (16.10) at 0.5749 with 5.7464; with 0.1143 | 0.8598660008; 0.2311126084 | 0.860; 0.231 |
| A16-73 | Python outputs | `1 - stats.chi2.cdf(89.30, 5)`; `stats.chi2.sf(89.30, 5)`; `stats.chi2.sf(9, 2)`; × $T$ | 0.0; 9.426575482464327e-18; 0.01110899654; 48.67962283 | 0.0; 9.4e-18; 0.011109; 48.68 |
| A16-74 | free-plan $T$ | printed in build/make_lab12.py:167 | 4,307 (printed in build/make_lab12.py:167) | 4,307 |
| A16-75 | regimes: $T$; $\hat\rho$; days $d_t^2>9$ | 2008-12-02 … 2015-05-29 and 2015-06-01 … 2026-10-08; full-sample $d_t^2$ | 1610; 2772; 0.6544413016; 0.5563822138; 93; 84 | 1,610, 2,772; 0.6544, 0.5564; 93, 84 |
| A16-76 | three-day $\hat\rho$, unrounded returns | (8.9) on the 7–9 April returns from the closes | 0.8504341292 | 0.850 |
| A16-77 | 2022: falls; daily correlation | printed in lm07.md:418 | 21-22%; -0.06 (printed in lm07.md:418) | 21–22%; −0.06 |
| A16-78 | days all 28 fell; rose | every U28 return $<0$; $>0$ (printed in lm11.md:48) | 156; 144; (printed in lm11.md:48) | 156; 144 |

**Facts checked on official sources** (items of `sources.md`):

- The daily price limit, 7% until 29 May 2015 and 10% from 1 June 2015 (sources.md item 25, verified; PITFALLS §7):
  the lab extension's two regimes and the 7 April 2025 caveat.
- References (sources.md): Wasserman (2004), ch. 2 (item 3, verified; section numbers checked in the book before
  printing); Longin and Solnik (2001), *Journal of Finance* 56(2): 649–676 (item 7, verified); Forbes and Rigobon
  (2002), *Journal of Finance* 57(5): 2223–2261 (item 8, verified); Boyer, Gibson and Loretan (1999), Federal Reserve
  Board IFDP 597, Theorem 1 (item 9, verified); Ang and Chen (2002), *Journal of Financial Economics* 63(3): 443–494
  (item 10, verified).
- `scipy.stats.chi2(df)` and its `sf`, `ppf` (sources.md item 23, verified).

## LM17

**Status.** Computed by the reviser on 2026-10-18 with data/vol3_anchors_lm17.py; not yet recomputed independently.

**Common definitions.** Sample TR23: `data/processed/vol3_taiex.parquet` (built and checked by
`data/vol3_series.py`; FinMind `TaiwanStockTotalReturnIndex`, data_id TAIEX, retrieved 2026-10-18), 5,850 closes
2003-01-02 → 2026-10-08, $T=5{,}849$ simple returns $R_t=P_t/P_{t-1}-1$ (the parquet's `R`) from 2003-01-03; log
returns $r_t=\ln(1+R_t)$. Means, variances, standard deviations, correlations and kurtosis divide by $T$ (or by the
number of terms or windows used); excess kurtosis is $\operatorname{Kurt}-3$ (`stats.kurtosis` defaults). Years =
calendar days between the first and last close ÷ 365.25 = 23.7645; $A=T/\text{years}=246.12$. A model horizon of
$\tau$ years is $m=\operatorname{round}(A\tau)$ sessions. The iid model draws days independently from TR23's
empirical law, so $\mu=\bar R$, $g=\bar r$, $\sigma_r=s_r$; $\bar g(f)$ and $s_r(f)$ are the mean and standard
deviation of $\ln(1+fR_t)$. Counts use the guard `R > 1e-12` and are checked with `Fraction` on the two-decimal
closes. Seeds: none (LM17 simulates nothing). Earlier modules' printed numbers are echoed with their file:line;
LM14's and LM15's numbers are recomputed here and cited to their owners in the text.

| ID | Number | Definition (enough to reproduce it) | Value (unrounded, as the script prints) | Printed as |
|:--|:--|:--|:--|:--|
| A17-01 | closes | rows of `vol3_taiex.parquet`, 2003-01-02 → 2026-10-08 | `5850` | 5,850 |
| A17-02 | $T$ | non-null `R`, 2003-01-03 → 2026-10-08 | `5849` | 5,849 |
| A17-03 | days | 2026-10-08 minus 2003-01-02 | `8680` | 8,680 |
| A17-04 | years | days ÷ 365.25 | `23.764545` | 23.7645 (23.76, 23.8) |
| A17-05 | $A$ | $T$ ÷ years | `246.122955` | 246.12 |
| A17-06 | signs | up $R>0$, down, zero, by `Fraction` on the closes; the guard `R > 1e-12` agrees | `up 3205; down 2644; zero 0 (guard count 3205)` | 3,205; 2,644; none |
| A17-07 | five years | $m=\operatorname{round}(5A)$ | `1231 (5A = 1230.6148)` | 1,231 |
| A17-08 | $G$ | last close ÷ first close | `25.2007` | 25.2 |
| A17-09 | $\bar R$ | mean of $R_t$ | `0.0625050622%` | 0.06251% |
| A17-10 | mean path, case | $(1.0006251)^T$; with the unrounded $\bar R$ | `from 0.06251%: 38.6701; unrounded: 38.6590` | 38.7 |
| A17-11 | case, $f=4$ | $(1+4\times0.0006251)^T$; unrounded | `from 0.06251%: 2.20577e+06; unrounded: 2.20323e+06` | 2.2 million |
| A17-12 | $f^*$ and its wealth | root of $\frac1T\sum R_t/(1+fR_t)$ (`brentq` on $[0,1/\lvert R_{\min}\rvert)$); $e^{T\bar g(f^*)}$ | `f* 4.138091; exp(T gbar(f*)) 2146.83` | 4.14; 2,147 |
| A17-13 | zero growth | root of $\bar g(f)=0$ above $f^*$ | `8.039046` | 8.04 |
| A17-14 | 0.0625% | $(1.000625)^T$ | `38.6475` | 38.65 |
| A17-15 | $\delta$ (LM14's E10, recomputed) | $\ln(1+\bar R)-\bar r$, in bp | `0.73159 bp` | 0.7316 bp |
| A17-16 | gap over the sample | $T\delta$; $e^{T\delta}$ | `T*delta 0.42791; exp 1.53404` | 0.4279; 1.534 |
| A17-17 | $\Pr(W_m>\E W_m)$, $m=T$ | $\Phi(-\sqrt T\,\delta(f)/s_r(f))$ at $f=1$ and $f^*$ | `f=1: 0.32199; f*: 0.02776` | 0.32; 0.028 |
| A17-18 | two trades of LM3's bet | the four equally likely averages of two +2%/−1% trades; their mean; variance (divisor 4, %²); one trade's variance | `averages 2%, 0.5%, 0.5%, -1%; mean 0.5%; variance 1.1250 %^2; one trade 2.2500 %^2` | 2%, 0.5%, 0.5%, −1%; 0.5%; 1.125; 2.25 |
| A17-19 | fair coin | exact $\Pr(\lvert 10j-5n\rvert\ge n)$ for $\operatorname{Bin}(n,\tfrac12)$, $n$ = 10, 100, 1,000 (integers); Chebyshev $0.25/(0.01n)=25/n$ | `n=10: 0.753906 vs 2.5; n=100: 0.0568879 vs 0.25; n=1000: 2.72846e-10 vs 0.025` | 0.7539, 0.05689, $2.7\times10^{-10}$; 2.5, 0.25, 0.025 |
| A17-20 | 0050 lognormal | printed in lm05.md:521 | `1.2130; 1.2358 (printed in lm05.md:521)` | 1.2130; 1.2358 |
| A17-21 | 0050 kurtosis | printed in lm05.md:367 and lm05.md:369 | `5.84 -> 7.63 (lm05.md:367); 62.8%; 14.1% (lm05.md:369)` | 5.84 → 7.63; 62.8%; 14.1% |
| A17-22 | top-ten shares (LM15's E10, recomputed) | ten largest $(R_t-\bar R)^4$ ÷ $\sum(R_t-\bar R)^4$; the same days' $(R_t-\bar R)^2$ ÷ $\sum(R_t-\bar R)^2$ | `34.9933%; 6.6648%` | 35.0%; 6.7% |
| A17-23 | KC §2 | $1.2\%/\sqrt4$; four identical copies | `0.6%; 1.2%` | 0.6%; 1.2% |
| A17-24 | KC §3 | $\sqrt n/2$ at $n$ = 100, 10,000; $0.5/\sqrt n$ | `5, 50; 0.05, 0.005` | 5, 50; 0.05, 0.005 |
| A17-25 | KC §4 | $1.005^{1000}$; $e^{1000\times0.0048761}$ | `146.5756; 131.1183` | 146.58; 131.12 |
| A17-26 | LM3's $g$ | printed in lm03.md:363; recomputed $\tfrac12(\ln1.02+\ln0.99)$ | `0.4876146% (printed 0.48761%, lm03.md:363)` | 0.48761% |
| A17-27 | KC §5 | $\Pr(j\ge60)$, $\operatorname{Bin}(100,\tfrac12)$; $\Phi(-(59.5-50)/5)$ | `exact 0.028444; cc 0.028717` | 2.84%; 2.87% |
| A17-28 | $f=2$ inputs | mean and sd (divisor $T$) of $\ln(1+2R_t)$ | `gbar(2) 0.095571%; s_r(2) 2.42884%` | 0.095571%; 2.4288% |
| A17-29 | one year | $m=\operatorname{round}(A)$ | `246 (A = 246.1230)` | 246 |
| A17-30 | KC §6 | $z=\bar g(2)\sqrt{246}/s_r(2)$, $\Phi(-z)$; from the printed inputs | `z 0.61716, Pr 0.26857; printed inputs z 0.61717, Pr 0.26856` | 0.6172; 26.86% |
| A17-31 | one-year loss, $f=1$ | $\Phi(-\bar r\sqrt{246}/s_r)$ | `0.237398` | 23.74% |
| A17-32 | daily kurtosis of $r$ | excess kurtosis of $r_t$, divisor $T$ (`stats.kurtosis` defaults) | `5.42776` | 5.428 (5.43) |
| A17-33 | KC §7 | smallest $m$ with $5.428/m<0.5$ | `11` | 11 |
| A17-34 | 10-day sums | excess kurtosis of the 5,840 overlapping 10-day sums of $r_t$ | `3.0229` | 3.02 |
| A17-35 | 7 April 2025 (LM15's E10, recomputed) | excess kurtosis of $R_t$ through 2025-04-02 and through 2025-04-07 | `4.2464 (5478 returns) -> 4.9386 (5479 returns)` | 4.25 → 4.94 |
| A17-36 | X1 end labels | $G$; $(1+\bar R)^T$; $e^{T\bar r}$ | `25.2007; 38.6590; 25.2007` | 25.20; 38.66; 25.20 |
| A17-37 | 38.66 from a printed $\bar R$ | $(1.00062505)^T$; $(1.0006251)^T$ | `0.062505%: 38.6588; 0.06251%: 38.6701` | 38.66; 38.67 |
| A17-38 | running up-frequency | share of $R_t>10^{-12}$ among the first $n$ returns, $n$ = 246, 1,231, 5,849 | `n=246: 0.51626; n=1231: 0.53777; n=5849: 0.54796` | 0.5163; 0.5378; 0.5480 |
| A17-39 | X2 band at $T$ | $2\sqrt{\hat p(1-\hat p)/T}$ | `0.013015` | 0.0130 |
| A17-40 | X3 | ten rounds of +100%/−50%: $2^{10}$; $1.25^{10}$; $\Pr(j\ge7)$; $\sum_{j\ge7}\Pr(j)\,2^{2j-10}$ and its share | `paths 1024; E W10 9.31323; Pr(j>=7) 11/64 = 0.171875; contribution 8.1875 = 87.9126%` | 1,024; 9.3132; 0.1719; 8.1875, 87.9% |
| A17-41 | X4 points | $A\bar g(1)$ (LM14's); $A\ln(1+\bar R)$; $f^*$, $A\bar g(f^*)$; zero growth | `A gbar(1) 13.5785%; A ln(1+Rbar) 15.3791%; f* 4.1381, A gbar(f*) 32.2823%; zero growth 8.0390` | 13.58%; 15.38%; 4.14, 32.28%; 8.04 |
| A17-42 | domain edge | $1/\lvert R_{\min}\rvert$; $R_{\min}$ and its date | `1/abs(R_min) 10.3096; R_min -9.6997% on 2025-04-07` | 10.31; −9.6997% |
| A17-43 | LM4's Kelly bet | printed in lm04.md:345 | `f* = 25, g* = 5.889% (printed in lm04.md:345)` | 25; 5.889% |
| A17-44 | X5 | $\Pr(j\le41)$, $\operatorname{Bin}(100,\tfrac12)$; $\Phi(-g^*\sqrt{100}/\sigma)$; $\Phi((41.5-50)/5)$ | `exact 0.044313; normal 0.0446360; cc 0.044565` | 0.04431; 0.04464; 0.04457 |
| A17-45 | ten years | $m=\operatorname{round}(10A)$ | `2461 (10A = 2461.2296)` | 2,461 |
| A17-46 | $\Phi^{-1}(0.95)$ | `stats.norm.ppf(0.95)` | `1.644854` | 1.645 |
| A17-47 | X6, one year | $m=246$: $e^{m\bar r}$; $(1+\bar R)^m$; $e^{m\bar r\mp\Phi^{-1}(0.95)s_r\sqrt m}$; $\Phi(-\bar r\sqrt m/s_r)$; $\Phi(-\sqrt m\,\delta/s_r)$ | `median 1.14536; mean path 1.16616; 5% 0.83809; 95% 1.56528; Pr(W<W0) 0.237398; Pr(W>EW) 0.46225` | 1.1454; 1.1662; 0.8381; 1.5653; 23.74%; 46.2% |
| A17-48 | X6, ten years | the same at $m=2{,}461$ | `median 3.88734; mean path 4.65420; 5% 1.44743; 95% 10.44018; Pr(W<W0) 0.011894; Pr(W>EW) 0.38218` | 3.89; 4.65; 1.45; 10.44; 1.19%; 38.2% |
| A17-49 | X6, sample | the same at $m=5{,}849$ | `median 25.20068; mean path 38.65898; 5% 5.49490; 95% 115.57520; Pr(W<W0) 0.000246; Pr(W>EW) 0.32199` | 25.20; 38.66; 5.49; 115.6; 0.02%; 32.2% |
| A17-50 | loss years | calendar years 2003–2025 whose last close is below the previous year's last close (2003 against 2003-01-02), `Fraction` | `5 of 23: 2008 -43.07%, 2011 -17.98%, 2015 -6.87%, 2018 -4.83%, 2022 -18.68%` | 5 (2008, 2011, 2015, 2018, 2022) |
| A17-51 | expected loss years | 23 × the one-year loss probability; 23 × 0.2374 | `23 x 0.237398 = 5.4602; 23 x 0.2374 = 5.4602` | 5.46 |
| A17-52 | printed model inputs | $\bar r$, $s_r$; quantiles from 0.055170%, 1.2107% and 1.645 (ten-year 5%, sample 5% and 95%) | `rbar 0.055170%, s_r 1.21073%; from 0.055170%, 1.2107%, 1.645: ten-year 5% 1.4473, sample 5% 5.4945, sample 95% 115.59` | 0.055170%, 1.2107%; 1.4473, 5.4945, 115.59 |
| A17-53 | X7, TR23 | excess kurtosis of all $T-m+1$ overlapping $m$-day sums of $r_t$, divisor the number of windows | `m=1: 5.42776, m=2: 5.04496, m=5: 3.62979, m=10: 3.02290, m=20: 2.28573, m=60: 3.20225` | 5.428, 5.04, 3.63, 3.02, 2.29, 3.20 |
| A17-54 | X7, iid | $5.428/m$; $5.43/2$ | `5.4280, 2.7140, 1.0856, 0.5428, 0.2714, 0.0905; 5.43/2 = 2.7150` | 5.43, 2.71, 1.09, 0.54, 0.27, 0.09; 2.72 |
| A17-55 | daily kurtosis of $R$ (LM14's E6, LM15) | excess kurtosis of $R_t$, divisor $T$ | `5.2680` | 5.27 |
| A17-56 | non-overlapping 20-day | from the first return ($\lfloor T/20\rfloor$ windows); minimum and maximum over the 20 starting offsets | `first return 2.3968 (292 windows); offsets 0-19 0.6931 to 4.4869` | 2.40 (292); 0.69–4.49 |
| A17-57 | limit regimes | daily and 20-day overlapping excess kurtosis of $r_t$ before 2015-06-01 (3,077 returns) and from it (2,772); 3.44/20, 8.41/20 | `before 2015-06-01 (3077): daily 3.4366, 20-day 1.9649; from 2015-06-01 (2772): daily 8.4101, 20-day 2.6592; iid 3.44/20 = 0.1720, 8.41/20 = 0.4205` | 3.44, 1.96; 8.41, 2.66; 0.17, 0.42 |
| A17-58 | X9 note | $A\times$ running variance of $R$ (divisor $n$), $n\ge246$: minimum, maximum, end | `min 0.032616 (2024-04-12); max 0.058011 (2004-06-23); end 0.035938` | 0.0326; 0.0580; 0.0359 |
| A17-59 | widget range | $m=\operatorname{round}(40A)$ | `9845 (40A = 9844.9182)` | 9,845 |
| A17-60 | five-year loss | $\Phi(-\bar r\sqrt{1231}/s_r)$ | `0.054937` | 5.49% |
| A17-61 | widget grid | $(\bar g(f),s_r(f))$ at $f$ = 1, 2 | `f=1: 0.00055170, 0.01210727; f=2: 0.00095571, 0.02428841` | as the value |
| A17-62 | lognormal against iid mean | $e^{T(\bar g(f)+s_r(f)^2/2)}$ and $(1+f\bar R)^T$ at $f$ = 1, 8 | `f=1: lognormal 38.6892, iid 38.6590; f=8: lognormal 2.1944e+13, iid 4.6808e+12` | 38.69, 38.66; $2.19\times10^{13}$, $4.68\times10^{12}$ |
| A17-63 | E1 | $1.5\%/\sqrt n$ at $n$ = 100, 10,000; smallest $n$ with $1.5/\sqrt n\le0.25$; LM3's mean (lm03.md:363) | `0.15%, 0.015%; n = 36; edge 0.5% (lm03.md:363)` | 0.15%, 0.015%; 36; 0.5% |
| A17-64 | E2 | $0.25/(0.01^2\times0.05)$ | `50000` | 50,000 |
| A17-65 | E3, ten rounds | $1.25^{10}$; $\Pr(j=5)$; $\Pr(j\ge7)$; share of the mean; $\Pr(j\le4)$ | `E W10 9.31323; Pr(W=1) 63/256 = 0.2461; Pr(W>EW) 11/64 = 0.1719; share 87.9126%; Pr(W<1) 193/512 = 0.3770` | 9.3132; 63/256 = 0.2461; 11/64 = 0.1719; 87.9%; 193/512 = 0.3770 |
| A17-66 | E3, 100 rounds | $1.25^{100}$; $\Pr(j\ge67)$ (smallest $j$ with $2^{2j-100}>1.25^{100}$); $\Pr(j\le49)$ | `E W 4.9091e+09; Pr(j>=67) 4.3686e-04; Pr(j<=49) 0.4602` | $4.91\times10^9$; 0.00044; 0.4602 |
| A17-67 | Peters' coin | expected factor per round; $\tfrac12\ln0.9$; $\sqrt{0.9}$ | `1.05; -0.05268; 0.94868` | 1.05; −0.0527; 0.949 |
| A17-68 | seven figures | $\bar R$, $\bar r$; $\delta$ from 0.06250506% and 0.05516962%; from 0.062505% and 0.055170% | `Rbar 0.06250506%, rbar 0.05516962%; gap from 7 s.f. 0.73159 bp; from 0.062505%, 0.055170%: 0.73155 bp` | 0.06250506%, 0.05516962%; 0.7316 (0.7315 fails) |
| A17-69 | days for 5% | $(\Phi^{-1}(0.95)s_r/\delta)^2$ and ÷ $A$; from 1.645, 1.2107%, 0.7316 bp | `74099 days = 301.06 years; from 1.645, 1.2107%, 0.7316 bp: 74107 days = 301.10 years` | about 74,000 days, about 300 years |
| A17-70 | Chebyshev, $f=1$ | $s_r^2/(T\delta^2)$; from the printed inputs | `4.6825; from printed 4.6821` | 4.68 |
| A17-71 | E5 rows | $W_T=e^{T\bar g(f)}$; $A\bar g(f)$, and $\ln W_T/\text{years}$ from the printed $W_T$; $(1+f\bar R)^T$ unrounded and from 0.062505% | `f=1: W 25.2007, A gbar 13.5785% (ln of printed W / years 13.5784%), mean path 3.8659e+01 (from 0.062505% 3.8659e+01); f=2: W 267.727, A gbar 23.5223% (ln of printed W / years 23.5219%), mean path 1.4911e+03 (from 0.062505% 1.4911e+03); f=4: W 2127.85, A gbar 32.2450% (ln of printed W / years 32.2453%), mean path 2.2032e+06 (from 0.062505% 2.2032e+06); f=6: W 405.589, A gbar 25.2702% (ln of printed W / years 25.2703%), mean path 3.2260e+09 (from 0.062505% 3.2259e+09); f=8: W 1.17536, A gbar 0.6799% (ln of printed W / years 0.6786%), mean path 4.6808e+12 (from 0.062505% 4.6807e+12)` | 25.20, 267.7, 2,128, 405.6, 1.175; 13.58%, 23.52%, 32.25%, 25.27%, 0.68%; 38.66, 1,491, $2.20\times10^6$, $3.23\times10^9$, $4.68\times10^{12}$ |
| A17-72 | E5, $f^*$ | $f^*$; $A\bar g(f^*)$; $e^{T\bar g(f^*)}$; ÷ $G$; zero growth; ÷ $f^*$ | `f* 4.138091; A gbar(f*) 32.2823%; W 2146.83; /G 85.189; zero growth 8.039046; /f* 1.9427` | 4.1381; 32.28%; 2,147; 85; 8.04; 1.94 |
| A17-73 | E5, $z$ at $f^*$ | $\delta(f^*)$, $s_r(f^*)$, $z=\sqrt T\,\delta(f^*)/s_r(f^*)$, $\Phi(-z)$ | `delta(f*) 12.7154 bp; s_r(f*) 5.07869%; z 1.91478; Pr 0.02776` | 1.915; 0.028 |
| A17-74 | drawdown at $f^*$ | largest fall of $\prod_{t\le n}(1+f^*R_t)$ from its running peak; date of the trough | `98.4816% at 2008-11-20` | 98.5%; 20 November 2008 |
| A17-75 | coin threshold | $\ln(4/3)/\ln2$; printed in lm04.md:366 | `0.4150375 (printed 0.41504, lm04.md:366)` | 0.4150375; 0.41504 |
| A17-76 | E6 | $g^*=\tfrac12\ln1.5+\tfrac12\ln0.75$; $\sigma=\ln2/2$; $z=-g^*\sqrt{100}/\sigma$; exact, normal, corrected at $n=100$; normal minus the boundary 0.0446355; the same three at $n=10$ | `g* 0.0588915; sigma 0.3465736; z -1.699250; n=100 exact 0.044313, normal 0.0446360, cc 0.044565; normal minus 0.0446355 5.43e-07; n=10 exact 0.376953, normal 0.295513, cc 0.375915` | 0.0588915; 0.3465736; −1.69925; 0.04431, 0.04464, 0.04457; $5\times10^{-7}$; 0.37695, 0.29551, 0.37591 |
| A17-77 | E7 | $1.96^2\times0.25/0.01^2$ | `9604.00` | 9,604 |
| A17-78 | 1.96 | printed in lm04.md:541 | `1.96 (printed in lm04.md:541)` | 1.96 |
| A17-79 | E8 $z$ | $\bar r\sqrt m/s_r$ at $m$ = 246, 2,461; from the printed inputs | `one year z 0.71470; ten years z 2.26053; from printed inputs 0.71472, 2.26059` | 0.7147; 2.261 |
| A17-80 | LM15's annual fit (E6, recomputed) | mean and sd (divisor 23) of the 23 calendar-year log returns; $\Phi(-\text{mean}/\text{sd})$; $s_r\sqrt{246}$ | `annual log returns mean 0.11646, sd 0.22207; Pr(G<1) 0.29999; s_r sqrt(246) 0.18990` | 22.21% (sd); 30.0%; 18.99% |
| A17-81 | lag correlations | Pearson correlation of the pairs $(r_t,r_{t+1})$; $(\lvert r_t\rvert,\lvert r_{t+1}\rvert)$; $(\lvert r_t\rvert,\lvert r_{t+20}\rvert)$ | `r lag 1 0.0394; abs(r) lag 1 0.1606; abs(r) lag 20 0.1228` | 0.039; 0.161; 0.123 |
| A17-82 | E10 | $2\Phi(-\sqrt n)$ at $n$ = 1, 4, 25 | `n=1: 0.3173, n=4: 0.0455, n=25: 5.733e-07` | 0.317, 0.0455, $5.7\times10^{-7}$ |
| A17-83 | Problem 1 | $1.2\%/\sqrt{400}$; $1.2\%/400$; $1.2\%\times\sqrt{400}$ | `0.06%; 0.003%; 24%` | 0.06%; 0.003%; 24% |
| A17-84 | Problem 2 | $2\Phi(-0.02/(0.5/\sqrt{2500}))$; $\sqrt{0.25}/(\sqrt{2500}\times0.02)$; $0.25/(2500\times0.02^2)$ | `0.0455; 0.5; 0.25` | 0.0455; 0.5; 0.25 |
| A17-85 | Problem 3 | $1.25^4$; $\Pr(j=4)$, $\Pr(j\ge3)$, $\Pr(j\ge2)$ for $\operatorname{Bin}(4,\tfrac12)$ | `E W4 2.4414; Pr(j=4) 1/16; Pr(j>=3) 5/16; Pr(j>=2) 11/16` | 2.4414; 1/16, 5/16, 11/16 |
| A17-86 | Problem 5 | $5.43/\sqrt{20}$; $5.43/20$ | `1.2142; 0.2715` | 1.21; 0.27 |
| A17-87 | Problem 6 | $n=400$: $\Pr(j\le166)$; $z=-g^*\sqrt{400}/\sigma$, $\Phi(z)$; $\Phi((166.5-200)/10)$; relative error of $\Phi(z)$ at $n$ = 400, 100 | `exact 0.000394; z -3.3985, normal 0.000339; cc 0.000404; relative errors n=400 -13.94%, n=100 +0.73%` | 0.000394; −3.3985, 0.000339; 0.000404; 14% low, 0.7% high |
| A17-88 | $\delta(2)$ (LM14's KC §7, recomputed) | $\ln(1+2\bar R)-\bar g(2)$, bp | `2.9361 bp` | 2.936 bp |
| A17-89 | Problem 8 | $0.024288^2/(T\times(2.936\text{ bp})^2)$; $z=\sqrt T\times2.936\text{ bp}/2.4288\%$; $\Phi(-z)$ | `bound 1.1700; z 0.9245; Pr 0.1776` | 1.17; 0.9245; 0.178 |
| A17-90 | Problem 9 | excess kurtosis of $\operatorname{Bin}(20,\tfrac12)$ | `-0.1000` | −0.1 |
| A17-91 | lab part 3 | $A\times$ running mean of $r_t$: at $n=246$; minimum for $n\ge246$ and its date; end | `n=246 27.1212%; min 2.0269% (2008-11-20); end 13.5785%` | 27.12%; 2.03% (20 November 2008); 13.58% |
| A17-92 | level spread | $s_r\sqrt T$; $e^{s_r\sqrt T}$ | `0.925949; exp 2.5243` | 0.9259; 2.52 |

**Facts checked on official sources.** Each item names its entry in `sources.md` or the reviser's own check.

- The daily price limit, 7% until 29 May 2015 and 10% from 1 June 2015 (`sources.md` item 25, verified: TWSE
  company history; TWSE 60th-anniversary book, p. 181): the 7 April 2025 cap and the two limit regimes of X7.
- The TAIEX total-return index reinvests cash dividends (`sources.md` item 24, verified: TWSE IndexS02).
- `scipy.stats.kurtosis` defaults `fisher=True, bias=True` give divisor-$T$ excess kurtosis (`sources.md` item 18).
- Grinstead and Snell (`sources.md` item 2, verified; AMS 1997, free 2006 edition), read by the reviser on
  2026-10-18 in the free edition's text: §8.1 Theorem 8.2 (weak law, iid with finite mean and variance) and
  Exercise 15 (strong law, stated for coin tossing only); §8.2 Example 8.8 (the average of $n$ standard Cauchy draws
  has the Cauchy density for every $n$, so the law of large numbers fails); §9.3 Theorem 9.6 (CLT); ch. 10, §10.3
  "Sketch of the Proof of the Central Limit Theorem" through moment generating functions, its last step stated
  without proof. §8.1, §8.2 and §9.3 are verified in `sources.md`; Example 8.8 and ch. 10 are this check's.
- Peters (2019), *Nature Physics* 15(12): 1216–1221 (`sources.md` item 13, verified): the +50%/−40% coin, expected
  change +0.05 per round, $\tfrac12\ln0.9=-0.0527$, typical factor $\sqrt{0.9}\approx0.949$.
- Wasserman (2004), §5.3 "The law of large numbers" and §5.4 "The central limit theorem" (`sources.md` item 3,
  verified from the contents only). No checked source states the strong law for general iid draws with
  $\E\lvert X\rvert<\infty$; the brief prints that form only after one is checked.

## LM18

**Status.** Computed by the reviser on 2026-10-18 with data/vol3_anchors_lm18.py; not yet recomputed independently.

**Common definitions.** Sample TR23: `data/processed/vol3_taiex.parquet` (from `data/vol3_series.py`), closes `tr`
2003-01-02 → 2026-10-08, $T=5{,}849$ simple returns $R_t=P_t/P_{t-1}-1$ from 2003-01-03 and log returns
$r_t=\ln(1+R_t)$. Moments divide by $T$ (sample standard deviations `std()` with `ddof=0`; covariances `np.cov(...,
ddof=0)`); a simulation's standard error is the standard deviation of its draws (divisor $n$) over $\sqrt n$. Years =
calendar days ÷ 365.25, $A=T/\text{years}=246.12$; five years is $m=\operatorname{round}(5A)=1{,}231$ sessions.
Threshold counts use the guard `<= -x + 1e-12`, `>= x - 1e-12` and agree with an exact `Fraction` recount on the
two-decimal closes. Seeds: each experiment creates its generator once, `np.random.default_rng([20261011, k])`, with
stream $k$: E1 1 (and `[20261012, 1]` for its second seed), E2 2 (also lab part 3 and the `multivariate_normal`
check), E3 3 (E7 reuses its paths), E5 5, E6 6, E8 8, E9 9, E10 10 (Problem 12 and the chunking check), common random
numbers 11, X3 12, coverage 13, X7 14, the $t$ extension 15; E4 reproduces LM12's lab with
`np.random.default_rng(20261011)`. Model parameters for E4 and X3: LM12's printed S5 Cholesky factor (lm12.md:441–445,
% a day ÷ 100); no U28 data are loaded. NumPy 2.5.3, SciPy 1.18.1 (`uv.lock`).

| ID | Number | Definition (enough to reproduce it) | Value (unrounded, as the script prints) | Printed as |
|:--|:--|:--|:--|:--|
| A18-01 | LM5's tail and `quad` check | `stats.norm.cdf(-4.1074386)`; relative difference of `integrate.quad(norm.pdf, -inf, -4.1074386)`. Printed in lm05.md:223 ($z$), 581 and 599 ($2.000355\times10^{-5}$), 603 ($7\times10^{-11}$) | Phi(-4.1074386) = 2.0003554e-05; quad relative difference 6.7e-11 | $\Phi(-4.1074386)$; $2.000355\times10^{-5}$ |
| A18-02 | LM12's colouring gap | `default_rng(20261011).standard_normal((4382, 5)) @ L.T` with LM12's printed $L$ (lm12.md:441–445, ÷100); `np.cov(ddof=0)`; $\lVert\hat\Sigma_{\text{sim}}-\Sigma\rVert_F/\lVert\Sigma\rVert_F$, $\Sigma=LL^{\top}$. LM12's lab prints 0.0250 (build/make_lab12.py:577–579, from U28's unrounded $L$) | 0.025026 | 0.0250; 0.025026 |
| A18-03 | $T$ | rows of `vol3_taiex.parquet`; $R_t=P_t/P_{t-1}-1$ on `tr` | 5850 closes 2003-01-02 -> 2026-10-08; T = 5849 returns from 2003-01-03 | 5,849 |
| A18-04 | days, years, $A$ | (2026-10-08 − 2003-01-02) in days; ÷ 365.25; $A=T$/years | 8680 days; 23.764545 years; A = 246.122955 | 8,680; 23.7645; 246.12 |
| A18-05 | threshold counts | guard (`<= -x + 1e-12`, `>= x - 1e-12`), recounted with `Fraction` on the two-decimal closes; LM15 owns them | R <= -3%: 108; R <= -5%: 15; abs(R) >= 3%: 175; guard = Fraction recount; returns exactly at +-3% or +-5%: 0 | 108; 15; 175 |
| A18-06 | $m$ | round(5$A$) | 5A = 1230.6148; m = 1231 | 1,231 |
| A18-07 | windows under water | start closes $i=0,\dots,4{,}618$; $G=P_{i+1231}/P_i<1$ (also exact with `Fraction`) | 4619 windows; 191 under water; 4.1351%; last start 2021-09-10 -> 2026-10-08 | 4,619; 191; 4.1%; 2003-01-02 → 2021-09-10 |
| A18-08 | episodes | under-water starts split where consecutive starts are more than 250 sessions apart | starts 2003-11-03 -> 2004-04-21 (111 windows), ends 2008-10-20 -> 2009-04-08; starts 2007-06-15 -> 2007-12-07 (80 windows), ends 2012-05-25 -> 2012-11-14 | November 2003 – April 2004 (2003-11-03 → 2004-04-21); June – December 2007 (2007-06-15 → 2007-12-07) |
| A18-09 | disjoint periods | years ÷ 5 | years / 5 = 4.753 | fewer than five; 4.75 |
| A18-10 | model answer | $z=-\sqrt m\,\bar r/s_r$; $\Phi(z)$, iid $\mathcal N(\bar r,s_r^2)$ daily log returns ((17.6), exact under the model) | z = -1.598758; Pr(G<1) = 0.054937 | 5.49%; −1.5988 |
| A18-11 | E3 | stream 3; 10 chunks of `standard_normal((1000, m))`; $\ln G=\sum(\bar r+s_rZ)$; count $\ln G<0$; SE = sd (divisor $n$)/$\sqrt n$; interval ±1.96 SE | 544 of 10000; 0.054400 +- 0.002268; interval 0.049955 - 0.058845; covers True | 544; 0.0544 ± 0.0023; 5.4% ± 0.2; about 5.0% to 5.9% |
| A18-12 | E10 | stream 10; 20 chunks of `integers(0, T, size=(500, m))`; $\ln G=\sum r$, $G=\prod(1+R)$; `np.quantile` default; sd divisor $B$ | 538 of 10000; 0.053800 +- 0.002256; quantiles 0.9828 / 1.9758 / 3.9680; sd ln G 0.4221 | 538; 0.0538 ± 0.0023; 5.4% ± 0.2; 0.98 / 1.98 / 3.97; 0.422 |
| A18-13 | (18.9) for S5 | $\Sigma=LL^{\top}$ from LM12's printed $L$; relative RMS gap $\sqrt{(1+(\operatorname{tr}\Sigma)^2/\lVert\Sigma\rVert_F^2)/n}$; centred (`np.cov`, divisor $n$) exact value $\sqrt{((n-1)/n^2)(\lVert\Sigma\rVert_F^2+(\operatorname{tr}\Sigma)^2)+\lVert\Sigma\rVert_F^2/n^2}/\lVert\Sigma\rVert_F$; its change at $n=100$ | centring changes the RMS gap at n = 100 by 0.364%; tr(Sigma)^2 / Frobenius(Sigma)^2 = 2.6509; sqrt(1 + .) = 1.9107; n = 4382: 0.02886 (centred 0.02886); n = 50000: 0.00855 (centred 0.00854) | under 0.4%; 1.911; 0.0289; 0.0085 |
| A18-14 | KC §3 | rank $\lceil0.5T\rceil$ of the sorted returns | u = 0.5 -> rank 2925 -> 0.0879%; np.median 0.0879% | 2,925; +0.0879% |
| A18-15 | KC §4 | $n=p(1-p)/0.001^2$ at $p=0.054937$; at 0.0549 | p(1-p)/0.001^2 = 51919; from 5.49%: 51886 | about 52,000 |
| A18-16 | zero hits | $(1-\Phi(-4.1074386))^n$, $n=10^5$ and $10^4$ | (1-p)^100000 = 0.1353; (1-p)^10000 = 0.8187 | 0.135; 0.8187 (82%) |
| A18-17 | antithetic tail | $\operatorname{Corr}(\mathbf 1\{Z\le-k\},\mathbf 1\{-Z\le-k\})=-p/(1-p)$; $1/(1+\rho_-)$ | corr -p/(1-p) = -2.0004e-05; variance ratio 1.000020 | $-2.0\times10^{-5}$; 1.00002 |
| A18-18 | KC §7 | $(1-1/T)^T$ and its complement | (1-1/T)^T = 0.367848; complement 0.632152 | 0.368; about 63% |
| A18-19 | memory, chunking | $10{,}000\times m\times8$ bytes; stream 10 as 20 calls of $(500,m)$ against one $(10{,}000,m)$ | memory of 10000 x 1231 float64: 98.48 MB; 20 chunks of 500 == one call of 10000: True | 98.5 MB; identical |
| A18-20 | window extremes | min and max of the window $G$, with start and end dates | worst 0.7754 (2004-03-09 -> 2009-02-24); best 3.4349 (2021-05-17 -> 2026-06-09) | 0.78; 3.43 |
| A18-21 | X3 | stream 12; for each $n$, 200 runs of `standard_normal((n, 5)) @ L.T`, relative Frobenius gap of `np.cov(ddof=0)`; RMS over runs; (18.9) uncentred; 5–95% (`np.quantile`) at 4,382 | RMS of 200 runs 0.1927, 0.0868, 0.0591, 0.0283, 0.0194, 0.0085; (18.9) 0.1911, 0.0855, 0.0604, 0.0289, 0.0191, 0.0085; 5-95% of runs at 4382: 0.0156-0.0432 | 0.0283; 0.0156–0.0432; series (`n3`) |
| A18-22 | X4 Simpson | LM5's printed Simpson errors (lm05.md:590–597) ÷ $2.000355\times10^{-5}$ at $N+1$ evaluations; LM5 prints “within a relative $1.2\times10^{-6}$” at 256 panels (lm05.md:585) | 9: 4.8441e-01, 17: 6.1489e-02, 33: 4.7342e-03, 65: 3.1144e-04, 129: 1.9697e-05, 257: 1.2348e-06, 513: 7.7486e-08, 1025: 4.8341e-09 | 0.484 … $1.23\times10^{-6}$ at 257 … $4.83\times10^{-9}$; $1.2\times10^{-6}$ |
| A18-23 | X4 Monte Carlo | per-draw relative SE $\sqrt{(1-p)/p}$ (plain), $\sqrt{e^{k^2}\Phi(-2k)-p^2}/p$ (importance sampling), $k=4.1074386$ | plain sqrt((1-p)/p) = 223.58; IS 2.1529 | 223.6; 2.153 (2.15) |
| A18-24 | E5 | stream 5; `standard_normal(10**6)`; hits $\le-4.1074386$; SE $\sqrt{\hat p(1-\hat p)/n}$; exact relative SE $\sqrt{(1-p)/(np)}$; $n=(1.96/0.01)^2(1-p)/p$; $n=(1/1.2\times10^{-6})^2(1-p)/p$ | 19 hits; 1.900e-05 +- 4.359e-06; expected 20.00; relative SE exact 0.2236, run 0.2294; n for 1.96 SE = 1%: 1.9204e+09; n for relative SE 1.2e-6: 3.4715e+16 | 19; $1.9\times10^{-5}\pm0.4\times10^{-5}$; 20.0; 22%; $1.92\times10^9$; about $3.5\times10^{16}$ |
| A18-25 | E8 | stream 8; $x=-k+Z$, 10,000 draws; $Y=\mathbf 1\{x\le-k\}e^{kx+k^2/2}$; mean ± SE | 4993 draws in the tail; 2.01062e-05 +- 4.3435e-07; relative SE 0.0216; covers True | 4,993; $2.011\times10^{-5}\pm0.043\times10^{-5}$; 2.2% |
| A18-26 | E8 variances | $e^{k^2}\Phi(-2k)-p^2$ and $p(1-p)$; their ratio; the ratio from three significant digits; $10^4\times$ ratio | per-draw variance IS 1.85457e-09; plain 2.00032e-05; ratio 10785.9; from 3 significant digits 10810.8; plain draws for 10,000 1.0786e+08 | $1.8546\times10^{-9}$; $2.0003\times10^{-5}$; 10,786; 10,811; $1.08\times10^8$ |
| A18-27 | model's $G$ | $e^{m(\bar r+s_r^2/2)}$; quantiles $e^{m\bar r+\sqrt m\,s_r\Phi^{-1}(q)}$; $\sqrt m\,s_r$; $ms_r^2$; $m\bar r$ | E G = 2.158388; quantiles 0.9806 / 1.9722 / 3.9664; sqrt(m) s_r = 0.4248; m s_r^2 = 0.180447; m rbar = 0.679138 | 2.1584; 0.98 / 1.97 / 3.97; 0.425; 0.1804; 0.6791 |
| A18-28 | E3's mean $G$ | mean of $e^{\ln G}$ over E3's paths ± SE | mean G 2.159622 +- 0.009643 | 2.160 ± 0.010; 0.0096 |
| A18-29 | E6 | stream 6; `standard_normal((5000, m))`; paths from $\mathbf Z$ and $-\mathbf Z$; mean of $(G+G^-)/2$ ± SE over pairs; run correlation; $-e^{-ms_r^2}$; $1/(1+\rho_-)$ | 2.155478 +- 0.003704; run corr -0.8467; exact rho -0.8349; exact ratio 6.0568 | 2.156 ± 0.004; −0.847; −0.835; 6.06 |
| A18-30 | E7 | E3's paths; control $\ln G$, $\mu_X=m\bar r$; $\hat\beta$ = covariance ÷ variance (`ddof=0`); controlled mean ± SE; $\sqrt{v/(e^v-1)}$, $v=ms_r^2$; $1/(1-\rho^2)$ | beta_hat 2.1581; rho_hat 0.9533; controlled 2.159319 +- 0.002912; exact rho 0.9552; exact ratio 11.4270; from rho 0.955: 11.3669 | 2.158; 0.953; 2.159 ± 0.003; 0.955; 11.4 |
| A18-31 | E6, $\Pr(G<1)$ | E6's pairs, indicators of $\ln G<0$; exact $-p/(1-p)$; $1/(1+\rho_-)$ | 0.055100 +- 0.002214; run corr -0.0583; exact rho -0.0581; exact ratio 1.0617 | 0.0551 ± 0.0022 (0.055, 0.002); −0.058; 1.06 |
| A18-32 | E7, $\Pr(G<1)$ | E3's paths, $Y=\mathbf 1\{\ln G<0\}$, control $\ln G$; exact $-\varphi(z)/\sqrt{p(1-p)}$; $1/(1-\rho^2)$; controlled mean ± SE | exact rho -0.4878; run rho -0.4864; exact ratio 1.3122; controlled 0.054436 +- 0.001982 | −0.488; −0.486; 1.31; 0.0544 ± 0.0020 (0.054, 0.002) |
| A18-33 | window quantiles | `np.quantile` (default) of the 4,619 window $G$ at 0.05, 0.5, 0.95 | 1.0228 / 1.6089 / 2.5281 | 1.02 / 1.61 / 2.53 |
| A18-34 | window spread | sd (divisor 4,619) and mean of the window $\ln G$; $m\bar r$ | sd ln G (divisor 4619) 0.2831; mean ln G 0.5018; m rbar 0.6791 | 0.283; 0.502; 0.679 |
| A18-35 | monthly counts | days with $\lvert R\rvert\ge3\%$ per calendar month of the return dates, 286 months (first and last partial); months by count; mean; variance (divisor 286); LM15 owns them | months by count 0..8: 210, 38, 9, 16, 4, 5, 1, 0, 3; 286 months 2003-01 -> 2026-10; mean 0.6119; variance 1.8459; max 8 in 2008-09, 2008-10, 2020-03 | 210, 38, 9, 16, 4, 5, 1, 0, 3; 286; 1.846; September 2008, October 2008, March 2020 |
| A18-36 | X7 resamples | stream 14; 1,000 resamples `integers(0, T, size=T)` placed on TR23's return dates; average months by count; monthly variance (mean, highest); resamples with a month of 8 or more | expected months by count 0..8: 154.300, 96.175, 29.027, 5.605, 0.786, 0.097, 0.010, 0.000, 0.000; variance: mean 0.5971, highest 0.8662; resamples with a month of 8 or more: 0 | 154.3, 96.2, 29.0, 5.6, 0.8, 0.1, 0.0, 0.0, 0.0; 0.597; 0.866; none |
| A18-37 | lag-1 $\lvert r\rvert$ | `np.corrcoef` of $\lvert r_t\rvert$, $\lvert r_{t+1}\rvert$; LM17 owns it (its A17-51) | corr(abs(r_t), abs(r_t+1)) = 0.1606 | 0.161 |
| A18-38 | X7 resample lag-1 | the same in each of X7's resamples: mean, sd | mean -0.00046; sd 0.01314 | −0.0005; 0.013 |
| A18-39 | E1 | hits $Z\le-2$ in `default_rng([s, 1]).standard_normal(10000)`, $s$ = 20261011 (twice), 20261012; $10{,}000\,\Phi(-2)$ | [20261011, 1]: 229, rerun 229; [20261012, 1]: 234; Phi(-2) = 0.022750; expected 227.50 | 229; 234; 0.02275; 227.5 |
| A18-40 | E2 uniforms | `default_rng([20261011, 2]).random(3)` | 0.91296814, 0.06612141, 0.84264153 | 0.912968, 0.066121, 0.842642 |
| A18-41 | $\lambda$ | 175 ÷ 5,849 | 175/5849 = 0.029920 | 0.02992 |
| A18-42 | E2 waits | $-\ln(1-u)/\lambda$; the same from $u$ to 6 decimals and 0.02992; $1/\lambda$; $\ln2/\lambda$ (unrounded and from 0.02992) | waits 81.6013, 2.2864, 61.8065; from u to 6 dp and 0.02992: 81.6002, 2.2864, 61.8059; 1/lambda = 33.4229 (33.4225); ln2/lambda = 23.1670 (23.1667) | 81.60, 2.29, 61.81; 33.42 (33.4); 23.17 |
| A18-43 | E2 empirical draws | $j=\lceil Tu\rceil$ (also from $u$ to 6 decimals); $R_{(j)}$ of the sorted returns (each value occurs once); its date | 5340 -> 1.4489% (2025-07-23); 387 -> -1.6133% (2010-08-31); 4929 -> 1.0114% (2016-12-28) | 5,340, 387, 4,929; +1.4489% (2025-07-23), −1.6133% (2010-08-31), +1.0114% (2016-12-28) |
| A18-44 | $\bar r$, $s_r$ | mean and sd (divisor $T$) of $r=\ln(1+R)$ | rbar = 0.0551696%; s_r = 1.210727% | 0.05517%; 1.2107%; 0.055170% |
| A18-45 | model from printed inputs | $z$, $\Phi(z)$, $\E G$, $m\sigma_r^2$, $mg$ from $g=0.05517\%$, $\sigma_r=1.2107\%$ | from g = 0.05517%, sigma_r = 1.2107%: z = -1.598805; Phi(z) = 0.054932; E G = 2.158390; m sigma_r^2 = 0.180439; m g = 0.679143 | −1.5988; 5.49%; 2.1584; 0.1804; 0.6791 |
| A18-46 | E4 entry | LM12's draw (A18-02): Semiconductor's simulated ÷ model variance − 1; $\sqrt{2/4{,}382}$ | Semiconductor simulated / model variance - 1 = 4.184%; sqrt(2/4382) = 2.136% | 4.18%; 2.14% |
| A18-47 | $\bar R$, $s$ | mean and sd (divisor $T$) of $R$ | Rbar = 0.0625051%; s = 1.208364% | 0.06251%; 1.2084%; 0.062505% |
| A18-48 | E9 | stream 9; 20 chunks of `integers(0, T, size=(500, T))`; mean and sd (divisor $B$) of the resample means; $s/\sqrt T$ (also from 1.2084%); means $\le0$ | mean of resample means 0.0624649%; sd 0.0158417%; s/sqrt(T) 0.0158000%, from 1.2084%: 0.0158005%; means <= 0: 0 | 0.06246%; 0.01584%; 0.01580%; none |
| A18-49 | E10's mean | $(1+\bar R)^m$ unrounded, from 0.062505% and from 0.0625%; E10's mean $G$ ± SE; with control $\ln G$ (mean $m\bar r$) | (1+Rbar)^m = 2.158033; from 0.062505%: 2.158031; from 0.0625%: 2.157898; estimate 2.150060 +- 0.009482; controlled 2.155970 +- 0.002748 | 2.1580; 2.1579; 2.150 ± 0.009; 2.156 ± 0.003 |
| A18-50 | Problem 2 | $\Phi(-3)$; $\sqrt{p(1-p)/10^6}$; $p(1-p)/10^6$; $\sqrt{p(1-p)}$ | Phi(-3) = 1.349898e-03; SE 3.6716e-05; variance 1.3481e-09; without n 0.0367 | 0.001350; $3.67\times10^{-5}$; $1.35\times10^{-9}$; 0.0367 |
| A18-51 | Problem 3 | the mean of $-\lambda\ln(1-U)$ is $\lambda$; $1-e^{-\lambda}$ bounds $1-e^{-\lambda U}$ | -lambda ln(1-U) has mean lambda = 0.02992 sessions; 1 - exp(-0.02992) = 0.0295 | 0.03; 0.0295 |
| A18-52 | Problem 4 | ranks $\lceil5u\rceil$ of the five sorted returns | sorted -2.5, -0.8, +0.3, +0.6, +1.2; ceil(5u) for u = 0.37, 0.95, 0.18: 2, 5, 1 | 2, 5, 1 |
| A18-53 | Problem 5 | $0.0096\sqrt{1+\rho_-}$ at $\rho_-=-0.835$ and $-0.058$ (0.0096 is A18-28) | 0.0096 sqrt(1 - 0.835) = 0.00390; 0.0096 sqrt(1 - 0.058) = 0.00932 | 0.0039; 0.0093 |
| A18-54 | Problem 6 | $1/(1-\rho^2)$, $1/(1-\rho)$, $1/\rho^2$ at $\rho=0.95$ | 1/(1-0.95^2) = 10.2564; 1/(1-0.95) = 20.0000; 1/0.95^2 = 1.1080 | 10.3; 20; 1.11 |
| A18-55 | Problem 7 | $k=3$: $\Phi(-3)$; $e^9\Phi(-6)$; importance variance $e^9\Phi(-6)-\Phi(-3)^2$; plain $\Phi(-3)(1-\Phi(-3))$; ratio | Phi(-3) = 1.34990e-03; e^9 Phi(-6) = 7.99440e-06; IS variance 6.17218e-06; plain 1.34808e-03; ratio 218.41 | $1.3499\times10^{-3}$; $7.994\times10^{-6}$; $6.17\times10^{-6}$; $1.348\times10^{-3}$; 218 |
| A18-56 | median path | $e^{m\bar r}$ unrounded and from 0.055170% | exp(m rbar) = 1.972177; from 0.055170%: 1.972186 | 1.9722 |
| A18-57 | Problem 10 | $4/m<1/2$ | n^(-4/m) falls faster than n^(-1/2) iff m < 8; Monte Carlo's order is better iff m > 8 | $m>8$ |
| A18-58 | Problem 11 | $\Phi(-2.01)$, $\Phi(-1.99)$; difference unrounded, from 7 and from 6 decimals; SE of the central difference ($\Delta k=0.01$, $n=100{,}000$): independent $\sqrt{\sum p(1-p)/n}/0.02$, common $\sqrt{d(1-d)/n}/0.02$; $-\varphi(2)$ | Phi(-2.01) = 0.022215594; Phi(-1.99) = 0.023295468; difference 0.001079873; from 7 decimals 0.0010799; from 6 decimals 0.001079; SE independent 0.03334; SE common 0.00519; -phi(2) = -0.053991 | 0.0222156; 0.0232955; 0.001080 (0.001079); 0.0333; 0.0052; −0.0540 |
| A18-59 | lab part 2 | stream 11; 200 repetitions of two `standard_normal(100000)` arrays; central difference with the two arrays and with the first twice; sd over repetitions | sd over 200 repetitions: independent 0.03254; common 0.00470 | 0.033; 0.005 |
| A18-60 | lab part 3 | `norm.ppf` of A18-40's uniforms; `default_rng([20261011, 2]).standard_normal(3)` | norm.ppf(u) 1.3593, -1.5053, 1.0054; standard_normal(3) -0.3144, 0.5177, 0.5719 | 1.3593, −1.5053, 1.0054; −0.3144, 0.5177, 0.5719 |
| A18-61 | lab part 4 coverage | stream 13; 1,000 runs of `standard_normal(1000)`, $\ln G=m\bar r+\sqrt m\,s_rZ$; interval $\hat p\pm1.96$ SE covers 0.054937; expected hits $1{,}000p$ | 940 of 1000; expected hits a run 54.9 | 940 of 1,000; about 55 |
| A18-62 | $t$ fit | `stats.t.fit(R)` (maximum likelihood; LM15 owns the fit) | nu 3.0652; loc 0.09972%; scale 0.77611% | 3.065; 0.0997%; 0.7761% |
| A18-63 | $t$ model | stream 15; 10 chunks of `loc + scale * standard_t(nu, size=(1000, m))`; a path with a day $\le-100\%$ counts as under water; otherwise $\ln G=\sum\ln(1+R)$ | Pr(G<1) 0.00970 +- 0.00098; paths with a day <= -100%: 7 | 1.0% ± 0.1; 7 |
| A18-64 | proposal shifts | per-draw relative SE $\sqrt{e^{a^2}\Phi(-k-a)-p^2}/p$ for proposal $\mathcal N(-a,1)$, $a=k/2$ and $2k$ ($a=k$ is A18-23) | per-draw relative SE at shift k/2 7.7623; at 2k 132.08 | 7.76; 132 |
| A18-65 | calendar windows | end = last close on or before the start date five calendar years later (29 February → 28 February); under water exactly; window lengths | 185 of 4637; 3.9896%; 1213-1250 sessions | 185 of 4,637; 3.99% |
| A18-66 | limit regimes | returns dated before 2015-06-01, and from it | before 2015-06-01: 3077; from 2015-06-01: 2772 | 3,077; 2,772 |
| A18-67 | worst day | minimum $R$ and its date | 2025-04-07; R = -9.6997% | −9.6997% (7 April 2025) |
| A18-68 | method dependence | `default_rng([20261011, 2]).multivariate_normal(0, Sigma, size=3)` against `standard_normal((3, 5)) @ L.T` from a fresh stream 2 | multivariate_normal and z @ L.T differ: True | other draws |

**Facts checked on official sources.** Each item names its sources.md entry.

- NumPy random (sources.md item 20, verified): `default_rng(seed)` builds a `Generator` on `PCG64`; integer seeds and
  sequences go to `SeedSequence`; PCG64 ("PCG XSL RR 128/64") has period $2^{128}$; identical streams are promised only
  for the same seed, calls, NumPy version and build, and `rng.random()` five times need not equal `rng.random(5)` (so
  the chunking check A18-19 is asserted, not assumed).
- `Generator.choice` defaults to `replace=True`; `Generator.integers` samples $[\text{low},\text{high})$ (item 21,
  verified). `Generator.multivariate_normal` defaults to `method='svd'` (item 22, verified).
- O'Neill (2014), PCG, HMC-CS-2014-0905 (item 12, verified); Glasserman (2003) §2.2.1, §2.3.3, §4.1, §4.2, §4.6 (item
  4, verified from the table of contents); Wasserman (2004) ch. 8, §8.2 (item 3, verified); Grinstead and Snell §5.2,
  Theorem 5.1 (item 2, verified).
- Installed docstrings, NumPy 2.5.3 and SciPy 1.18.1, read 2026-10-18 (not in sources.md; the editor adds them to
  SOURCES): `Generator.random` "Return random floats in the half-open interval [0.0, 1.0)"; `scipy.stats.norm.ppf`
  "Percent point function (inverse of `cdf`)"; `SeedSequence` seeds "independent and very probably non-overlapping
  BitGenerators".
- Not used: Efron and Tibshirani (1993) and Blitzstein and Hwang (2019), both "partly verified" in sources.md.
