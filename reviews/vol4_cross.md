# Volume IV cross-module checks

## Round 1 (X), 2026-10-19

A fresh, read-only agent checked the eight drafts at `157461e` as one volume and against LM1–LM18; no critical or major item.

I read the drafts, plans/vol-4.md (shared decisions, editor's decisions, Stage 4 list and the briefs' prereq, leads and tag-user lines), AUTHORING §6, SOURCES "Chinese terms (Volume IV)", the ROADMAP boundary table and reviews/vol3_cross.md. The scratch scripts are in scratch/stage3/X:

- xref.py, tagctx.py and fm.py check tags, links and front matter.
- numshared.py and numquote.py compare numbers across modules.
- jsonscan.py scans the chart and widget JSON.
- zh.py dumps the 中文導讀 boxes and Glossaries.
- spot.py spot-checks values against data/raw.

Nothing in the repository was changed. No critical or major item was found.

## Findings

**X1 (minor). Ownership of TR23's autocorrelations and moments.** In Volume IV, LM19 owns the sample autocorrelations of $r$, $\lvert r\rvert$ and $r^2$ (plans/vol-4.md:110, :254). LM22 follows the decision ("([[LM19]]; [[LM17]]'s pair correlation prints the same)", lm22.md:163), and so does LM25 (lm25.md:69, :149, :203). Three places do not:

- lm21.md:135: "TR23's next-day log returns correlate 0.039 ([[LM17]])". LM19 prints 0.0393 (lm19.md:253).
- lm26.md:56: "correlate only 0.039, but their sizes correlate 0.161 ([[LM17]])". LM26 itself cites [[LM19]] for 0.194 at lm26.md:29, so it uses two attributions for one family of statistics.
- lm26.md:240: "skewness −0.59 against −0.47". No owner prints TR23's log-return skewness −0.47: LM19's summary table holds simple-return moments only, and LM17 prints 5.428 but not −0.47.

Fix: LM21 and LM26 cite [[LM19]] (0.0393, 0.161). For −0.47, either LM26 says it computes the value itself, or LM19 adds the log-return skewness and kurtosis to its summary. **Modules: LM21, LM26 (LM19 optional).**

**X2 (minor). Prerequisites with no citation in the text, and the Stage 4 leads built on them.** fm.py finds four prerequisites that the text never cites, by link or by tag:

- LM23 lists 9 and 15 (lm23.md:5). Its brief gives LM9 for rank and exact fits, and LM15's (15.9) for the $t_{T-d}$ law. The draft cites [[LM10]] for rank and [[LM20]] for $t_{T-d}$ (lm23.md:126).
- LM24 lists 14 (lm24.md:5). Its brief gives (14.3), (14.4) and TR23's moments, but the draft takes them from LM19 and LM20.
- LM25 lists 18 (lm25.md:5). It prints batch standard errors (lm25.md:220, :266, :459, :488) but never names [[LM18]].

The Stage 4 list adds lm15 → 23, lm14 → 24 and lm18 → 25 (plans/vol-4.md:423–425) on these prerequisites alone. Either add the citations (for example [[LM18]] at the first batch SE, lm25.md:220; (15.9) at lm23.md:126; [[LM14]] in LM24), or drop them from prereq and from the Stage 4 list. **Modules: LM23, LM24, LM25 (plan).**

**X3 (minor). Pointers to LM22 that LM22 does not honour.**

- lm21.md:231 says "[[LM22]] resamples blocks of days to measure the widening" of count tests. lm21.md:238 says LM22 replaces the two-proportion test on shares of extreme days. LM22 resamples no count and no share of extreme days. Its only share is "five-year windows under water", and its regime work is LM16's correlation, in the lab.
- lm19.md:334 says "[[LM22]] puts an interval on it", meaning VR(1,231) and its ratio to the iid factor. LM22 bootstraps a different statistic: the windows' spread about their own mean, 0.283 (0.20 to 0.68, lm22.md:304), plus VR(20). This one is borderline.

Fix: reword the pointers ("[[LM22]]'s block bootstrap is the tool for this", "an interval on the windows' spread"), or add one LM22 problem that block-bootstraps a count, for example the 13 falls after 108 falls. **Modules: LM21, LM19 (or LM22).**

**X4 (minor). Pointers that contradict the module they cite.**

- lm19.md:157: "How far a sample skewness moves between samples is measured by its standard error ([[LM20]])". The note at lm19.md:194 also points to [[LM20]]. But lm20.md:406 says "the skewness and the kurtosis get no standard error at all". LM19 should say that LM20 explains why they get none.
- lm20.md:280 (knowledge check): the gain of 561.8 "needs a test ([[LM21]])". But lm20.md:311 calls the likelihood-ratio test "outside this book", and lm21.md:85 says it is not in the book either. Reword the answer to match.

**Modules: LM19, LM20.**

**X5 (minor). Chinese terms that differ between boxes.** None of these is in SOURCES "Chinese terms (Volume IV)":

- Sharpe ratio: 夏普比率（Sharpe ratio） in lm19.md:391 and lm20.md:409, but untranslated "Sharpe ratio" in LM21's box, lm21.md:187.
- t-statistic: LM22 writes t 統計量（t-statistic） (lm22.md:345), LM25 writes t 值 (lm25.md:200, :250, :296), and LM21 and LM23 keep "t-stat".
- Sandwich: LM23 writes White 的三明治公式 (lm23.md:260), and LM26 writes 夾層估計量（sandwich estimator） (lm26.md:265).

Choose one form for each and record it in SOURCES. **Modules: LM21, LM22, LM25, LM23/LM26.**

**X6 (minor). A book-coined term printed without its English.** The book's own forms are printed with their English in every box that uses them (plans/vol-4.md:159–161; SOURCES). The box at lm26.md:401 uses 實現變異數 with no "(realized variance)". **Module: LM26.**

**X7 (minor). Glossary conventions for terms without a 樂詞網 entry.**

- LM22 (lm22.md:518, :519, :528) and LM26 (lm26.md:535, :537, :539, :544, :546, :548) print a Chinese description in parentheses. LM23 prints "—" (lm23.md:549, :554, :556).
- Inside LM26, the boxes use 有效窗口（effective window） (lm26.md:128) and 無條件變異數（unconditional variance） (lm26.md:187) as terms, while its Glossary shows them as parenthesised descriptions.
- Spacing: LM24's Glossary writes James-Stein估計量 (lm24.md:522), but its box writes James-Stein 估計量 (lm24.md:311), and other modules write Bonferroni 校正 with a space. SOURCES asks for one style.

**Modules: LM22, LM23, LM24, LM26.**

**X8 (trivial). A tag-shaped citation of an outside source.** lm22.md:72 and lm22.md:533 write Efron and Tibshirani's equation as "their (6.6)". That is the book's tag form, and it collides with LM6's (6.6), the annuity future value. Write "their equation 6.6". **Module: LM22.**

**X9 (trivial). One work cited in two forms.**

- Lo (2002) reads "The Statistics of Sharpe Ratios." *Financial Analysts Journal* 58 (4): 36–52 at lm19.md:564, lm20.md:631 and lm21.md:531.
- LM22 writes "The statistics of Sharpe ratios. … 58(4): 36–52, doi" (lm22.md:537), and its whole reference list uses sentence-case titles without quotes.

The VX9 precedent is one form per work. **Module: LM22.**

**X10 (trivial). Notation details against AUTHORING §6.**

- lm26.md:197 writes the parameter vector as a plain $\theta=(g,\omega,\alpha,\beta)$. §6 and LM20 write a vector as $\boldsymbol\theta$.
- lm23.md:356 draws $\mathbf Z\sim\mathcal N_{28}(\mathbf 0,C)$, but §6 reserves $\mathbf Z$ for a standard normal vector.
- LM24 uses $k$ both for a grid index ($x_k$, lm24.md:60) and for the degrees of freedom of $\chi^2_k$ (lm24.md:250, :468), and does not declare it.
- The same derivation of the $t_{T-1}$ law names its variables differently: LM20 writes $Y\sim t_{T-1}$ and $V\sim\chi^2$ (lm20.md:54), while LM21 writes $Y\sim\chi^2_{T-1}$ (lm21.md:118).

**Modules: LM26, LM23, LM24, LM20/LM21.**

**X11 (trivial). A forward link answered on another sample.** lm26.md:242 answers make_lab05.py:529 ("Part of that shape comes from volatility that changes over time"). LM5's question is about 0050, with a normal count of 0.058 over twelve years. LM26 answers on TR23, with 0.117, and does not say that the sample changed. Add "(LM5 asked it for 0050; on TR23 …)". **Module: LM26.**

## Observations (no change requested)

- **Weekly series near the old cap.** lm25-case-s.json publishes 1,227 weekly TAIEX closes. lm26-vol.json has 1,224 weekly points and lm19-rollscale.json 1,126. All are thinned to weekly or every fifth session, as decision X37 allows, but the first exceeds the "1,172 dated points" precedent quoted at plans/vol-4.md:316–317.
- **LM26 states the opening-return share three ways:** "two thirds" (lm26.md:23), 66% (lm26.md:325) and 68% (lm26.md:365). The samples probably differ (5,351 days against the 4,609 out-of-sample days) but are not named. This is inside one module.
- **Glossary coinages not recorded in SOURCES:** 常態等效尺度, 獨立同分布區間, 獨立同分布因子 (LM19) and 資料權重 (LM24). Some box terms are missing there too: 創新項, 損失函數, 標準化殘差, 持有成本.

## Checks that passed

- **Tags.**
  - Every cross-module tag cited in LM19–LM26 exists, and its content matches what the citing text uses. Volume IV tags: 19.1, 19.3, 19.5–19.8, 20.1, 20.2, 20.4–20.8, 21.1, 21.2, 21.6–21.8, 23.1–23.4, 23.6, 23.7, 25.1–25.3 and 25.5. Earlier tags include 1.9, 1.12, 2.1, 3.9, 4.2, 4.5, 4.15, 6.22, 6.25, 7.1, 10.2, 10.4, 11.6, 12.1–12.4, 12.6, 12.8, 13.2, 13.6–13.9, 13.12, 14.1, 14.3–14.6, 14.12, 15.1, 15.2, 15.6, 15.8–15.11, 16.1–16.10, 17.1, 17.2, 17.5, 18.1, 18.2, 18.6 and 18.8.
  - Every module's own tag citations are defined.
  - All `[[ex:]]` and `[[eg:]]` references resolve.
- **Labels.** No module gives one label to both an exhibit and an example, and there are no duplicate labels. The rendered previews are newer than the sources.
- **Front matter.**
  - prereq and leads equal the briefs in all eight modules.
  - Leads within the volume agree with the later modules' prereqs and with the forward links: LM24 to LM22 and LM23 are pointers only, as decided in X6.
  - The future leads LM20 → 30 and LM25 → 33 rest on the briefs' tag users.
  - The Stage 4 lead additions match the drafts' prereqs exactly, apart from X2.
- **Numbers across modules agree to the printed digits and cite the owner.**
  - LM19's 15.38%, 18.96% (18.99% on log returns), 0.0517 and 0.81.
  - LM20's 4.28, 3.89, 0.33, 1.11 (1.111, 1.085, 1.082), 0.21 (0.207, 0.205), 7.8–23.0, 2.10–6.46 and 0.40–1.22.
  - LM21's t-stat 3.96 (3.955678), $7.6\times10^{-5}$, the one-sided $3.8\times10^{-5}$ and the regime p-value 0.041.
  - The variance ratios 1.039 (1.0392), 1.047 (1.0465), 1.036 (1.0359), 1.208, 0.619 and the iid factor 0.997.
  - $\hat\rho_1$ = 0.0393, the iid band ±0.0256 and its outside lags; 0.194; the robust SE 0.0205.
  - The crash correlation 0.788/0.7884 against 0.860/0.8598, and $\hat\rho$ = 0.5749.
  - GARCH and EWMA appear only in LM26, and the block length 145 only in LM22.
  - 23.7645, 246.12, 245.4794, 4,382, 2,191, 1,224 ISO weeks, 524 repaired closes on 38 dates, and LM17's $\hat f^*$ = 4.14.
  - From data/raw: TX settled at 49,357 on 8 October 2026; the TAIEX price index rose 10.91-fold from 1 December 2008 and 10.90-fold from 2 January 2003; both indices returned −9.6997% on 7 April 2025.
- **Forward links.** All 71 links from LM1–LM18, the pages and the labs to LM19–LM26 are honoured. The exceptions are the items already on the Stage 4 list (make_lab04.py:642, make_lab11.py:571, make_lab15.py:443, make_lab17.py:486, lm15.md:263) and X11.
- **Volume-wide decisions, checked in every module.**
  - No src/data/lm19-*… lm26-* JSON file and no widget carries a daily FinMind series in date order. Dated arrays are weekly or every fifth session; widgets hold statistics, models or the 243 undated 2025 pairs.
  - Every quantile helper uses inverted_cdf; np.median appears only as the labelled contrast.
  - HC0 throughout; Newey–West lags of 9, 8, 7 and 4 follow ⌊4(T/100)^{2/9}⌋ with no correction. LM23's ℓ = 19 and 38 for overlapping sums are argued in the text.
  - Printed bootstrap numbers use the stationary bootstrap.
  - Tests use a normal reference and two tails; DF and KPSS are stated as one-sided, and Ljung–Box and ARCH use the upper tail.
  - The 23 Saturday sessions are treated as LM21 treats them.
  - The volume writes 實現變異數, never 已實現; "hat value" is LM23's; "leverage" keeps the book's meaning.
- **Notation.**
  - α, β, θ, ℓ, k, m, c, q, $L$, $K$, $h$ and $u$ each keep one meaning per module, as their notation notes declare and §6 allows, apart from X10.
  - No $R^2$, $P$ or $^T$ appears for the uses §6 forbids.
- **Boundaries.**
  - Each ROADMAP boundary holds: LM12/LM23, LM18/LM22/LM45, LM24/LM30 and LM25–LM26/LM39.
  - The promises the plan assigned are each kept: LM16's crash correlation and LM11's eigenvalue share in LM22; the factor model in LM23; the MLE of $\mathcal N_N$ in LM20.
  - Nothing is taught twice beyond the editor-approved one-line $t_{T-1}$ derivation in both LM20 and LM21.
- **Chinese terms.** Every SOURCES "Book" term, and each Glossary English–Chinese pair, is used consistently across the eight modules, apart from X5–X7. 波動率 and 時間序列 throughout; no 波動度 or 時間數列.

## Editor's decisions on X1–X11 (2026-10-19)

- **X1:** accepted. LM21 and LM26 cite [[LM19]] for 0.0393 and 0.161; LM26 says that it computes the log-return
  skewness −0.47 itself (LM19's summary table stays on simple returns).
- **X2:** accepted. LM25 cites [[LM18]] at its first batch standard error, so lm18 → 25 stays. LM23 drops 9 and 15 from
  its prerequisites (rank and the $t_{T-d}$ law come from [[LM10]] and [[LM20]]) and LM24 drops 14 (its moments come
  from LM19 and LM20); the Stage 4 list loses lm15 → 23 and lm14 → 24.
- **X3:** accepted: reword the pointers (LM21 lines 231 and 238: "[[LM22]]'s block bootstrap is the tool for this";
  LM19 line 334: "an interval on the windows' spread"). No new LM22 problem.
- **X4:** accepted: LM19 says that [[LM20]] explains why a sample skewness gets no standard error; LM20's line 280 as
  its record decides.
- **X5:** decided: 夏普比率（Sharpe ratio） in every box; t 統計量（t-statistic）; 夾層估計量（sandwich estimator）, the
  statistics listing's form (the source check of 2026-10-19 found no 三明治 entry), in LM23 and LM26. The forms are in
  SOURCES, "Chinese terms (Volume IV)", Stage 3 round 1 additions; LM26's innovation is 新息.
- **X6:** accepted: 實現變異數（realized variance） at its first use in each box.
- **X7:** decided: a Glossary prints the Chinese form a box uses, the book's own form when 樂詞網 has none (marked so in
  SOURCES), never a description in parentheses and never "—" for a term the module uses in Chinese; a Latin name is
  separated from the Chinese by a space (James-Stein 估計量, Bonferroni 校正).
- **X8, X9:** accepted ("their equation 6.6"; one form per work, the house form).
- **X10:** accepted: LM26 $\boldsymbol\theta$; LM23 names its non-standard normal vector with another letter; LM24
  declares $k$; LM20 and LM21 align the variable names of the $t_{T-1}$ derivation.
- **X11:** accepted: LM26 says that LM5 asked it for 0050 and answers on TR23.
- **Observations:** weekly series are allowed by decision X37 (no change); LM26 names the samples behind 66% and 68%;
  the Glossary coinages go into SOURCES with the source check.

## Round 1, batch B additions (2026-10-19)

The consolidations of LM23–LM26 found items that also fall on other modules. Decided by the editor:

- **XB1 (dividend datasets):** LM23's m11 applies to LM20 too. The manifest holds dividend files for 0050 and 00679B
  only, so lm20.md:401 and :636 print "`TaiwanStockPrice` (0050, 00631L) and `TaiwanStockDividendResult` (0050)" as
  LM23 does.
- **XB2 (lag):** 樂詞網's statistics listing gives 落階；落期；遲延期數 for "lag" (SOURCES, Chinese terms (Volume IV),
  batch B). The noun is 落期（lag） at its first use in each box: LM19 (line 263) and LM23 (line 260, both occurrences)
  change 落後期. LM26's 落後項 (line 81) means lagged values, which 樂詞網 does not list: it becomes
  「…對自己前幾期的值（lagged values）做迴歸」. A plain phrase such as 落後 1 期 or 落後一期的值 stays.
- **XB3 (homoskedastic):** 樂詞網 gives 變異數齊一性 (homoscedasticity) and 變異數齊一的 (homoscedastic). LM23's box reads
  「誤差若變異數齊一（homoskedastic）且彼此不相關」; a Glossary row, if any, prints 變異數齊一性.
- **XB4 (本模組):** a box calls its module 本模組, as LM1 and LM18 do: lm23.md:331 and lm26.md:333 change 本章.
- **XB5 (covariance citations):** (16.3) is the variance of a sum and (16.4) the covariance of $M\mathbf X+\mathbf b$.
  LM23 (m3), LM24 (m5) and LM25 (m4) cite (16.4) for covariances. LM19–LM22's citations of (16.3) are for variances
  of sums and stay.
- **XB6 (documentation links):** every statsmodels link in Volume IV points to v0.15.0, the locked version, as LM25
  does (LM19 line 569, LM21 line 537, LM23 line 575, LM26 line 562; the v0.15.0 pages return HTTP 200). SciPy links
  keep the unversioned form of the published modules.
- **X10, refined (LM24 m3):** LM24 declares $k$ once, as Section 2's cell index, and writes a chi-square law's degrees
  of freedom as $\nu$, as AUTHORING §6 does for $t_\nu$.
- **Briefs and anchors:** from Stage 3 the modules and their numbers scripts are authoritative (plans/vol-4.md
  preface). The departures the records list (LM23 C1, M2, m16; LM24 A1, m11; LM25 M1, M3, m16, A2; LM26 m4) are recorded
  in the module records, not copied back.

## Revision 1 re-check (X2), 2026-10-19

A fresh, read-only agent checked the eight revised modules as one volume (`scratch/rev1/X2.md`). Every X and XB
decision is applied where it falls; every tag, label and cross-module number agrees. Its findings, with the editor's
decisions after a fresh adversarial re-check of the major items (`scratch/rev1/chk/`):

| # | Severity | Finding | Decision |
|:--|:--|:--|:--|
| 1 | major | LM22 (L34, L47, L139) and LM21 (L172) describe the annual Sharpe ratio on simple returns as holding for uncorrelated days, against LM19's [[ex:rules]] and the plan's "Sharpe ratio" decision. The re-check confirmed it and found two more sentences in LM20 (L153, L407). | XB8 below; the wording is in the module records. |
| 2 | major | LM26's E1 prints $\chi^2$ p-values for the ARCH test without the fourth-moment caveat that LM19 and LM20 apply. Confirmed; the re-check refuted in part X2's "exceeds every draw" (a $t_{3.065}$ law reaches 224.8 about twice in 10,000) and "reject whatever the reference law", and found a permutation reference that needs no moment. The same-root scan found the caveat missing in LM20, LM22, LM23, LM25 and LM26. | XB7 below; LM26 adds a permutation experiment. |
| 3 | minor | The Stage 4 list lacks lm15 → 22. | Added (plans/vol-4.md). |
| 4 | minor | The iid band has three Chinese forms. | 獨立同分布區間（iid band） in LM19's §4 box and LM25's §5 box. |
| 5 | minor | Basic terms are glossed in some boxes only. | XB10 below. |
| 6 | minor | LM21 L282 points to LM22 for a statement LM22 does not make. | Reworded (LM21's record). |
| 7 | minor | LM22 alone tags its own forms in the Glossary. | XB9 below. |
| 8 | trivial | Two attributions (LM26 L251, LM22 L163). | Fixed as proposed. |
| 9 | trivial | Reference forms (journal "&", Patton's initials, NumPy's pinned page, "equation 5"). | Fixed as proposed. |

Decided by the editor:

- **XB7 (fourth moment):** a test, p-value, standard error or interval whose reference law needs a finite fourth
  moment of returns is flagged at its first use in each module (nominal, approximate, or resting on practice), in one
  sentence that cites [[LM19]] or [[LM15]]'s $\nu=3.065$ fit (LM20: its own Section 7). Where a reference without
  that moment exists and is cheap (LM26's permutation), the module adds it. Places: LM20 L47 and L410; LM22 L89 and
  L196; LM23 L131; LM25 after L170; LM26 E1 and after L387.
- **XB8 (√A):** $\sqrt A$ annualization of a Sharpe ratio or a volatility is exact only for log returns on uncorrelated
  days and a convention on simple returns ([[LM19]]; Lo 2002); no sentence says that uncorrelated days suffice.
  Places: LM20 L153 and L407; LM21 L172; LM22 L34, L47 and L139.
- **XB9 (own forms):** a module prints the book's own Chinese forms without a tag, as LM1–LM18 do; SOURCES records
  them ("Chinese terms (Volume IV)", revision 1). LM22 drops its tags and its prose remark; LM26 drops its remark on
  半衰期.
- **XB10 (glosses):** every Chinese technical term gets its English at its first use in each box, basic terms
  included (變異數, 平均數, 標準差, 殘差, 迴歸, 估計量, 標準誤, 對數報酬, 波動率, 條件變異數 and the like), as AUTHORING §1 asks and LM20
  and LM23 already do. Places as X2 lists them, in the module records.

## Revision 2 re-check (X3), 2026-10-19

A fresh, read-only agent checked the eight modules after revision 2 (`scratch/rev2/X3.md`): no critical or major
item. XB7–XB10 are applied; X1–X11 and XB1–XB6 still hold; tags, labels, prereq and leads, and the numbers one
module cites from another all agree; the revision added no contradiction. Its minor items and the editor's decisions:

| # | Finding | Decision |
|:--|:--|:--|
| 1 | XB7 gaps in LM22 (the stationary test of the mean; $\hat\rho_1(\lvert r\rvert)$; Section 7's correlations and shares). | Fixed as proposed (LM22's record). |
| 2 | XB7 gap in LM20 (Problem 6(c)'s plug-in error). | Fixed as proposed (LM20's record). |
| 3 | LM26's permutation maxima depend on the seed and carry no standard error. | "No shuffle reaches" instead (LM26's record). |
| 4 | LM26 alone has no roadmap. | Restored (LM26's record). |
| 5 | One concept, two forms: drift, sampling, classical standard error, window, dividend yield, uncorrelated, heavy tail, 數值方法. | XB11 below. |
| 6 | XB10: first uses still unglossed. | Applied with the module lists (records); XB10's scope below. |
| 7 | SOURCES lacks rows for revision 2's glosses, and three Book cells are stale. | The editor adds a revision-2 table and fills the cells. |
| 8 | LM25's XB7 wording and Glossary row. | Fixed as proposed (LM25's record). |

Decided by the editor:

- **XB11 (one form per concept):** 參數漂移（parameter drift） for a moving coefficient (LM23), 漂移項（drift） for a
  drift term (LM25); 抽樣 for sampling and 抽樣區間（sampling interval） (LM21, LM26); "classical standard error" in
  English and 古典標準誤 in Chinese (LM26 joins LM23 and LM25); 視窗 for window and 有效視窗 for the effective window
  (LM26, SOURCES); 股利殖利率（dividend yield） (LM23, as LM6); 互不相關（uncorrelated） (LM16's Glossary form; LM23,
  LM25, LM26); 懷疑性事前分布（sceptical prior） (LM24, 樂詞網). Two are declined: "fat tails" and "heavy tails" stay
  English synonyms, as in LM4, LM5, LM14, LM15 and LM17; 數值方法 stays, LM5's form.
- **XB10's scope, from here:** the module lists above close it. A later check reports an unglossed first use in a box
  only for a term in the module's own Glossary or a term the module defines; ordinary words of the book's prose are
  not reopened.
- **XB11, after a fresh check (2026-10-20):** the English headword variants a checker listed (stationary and
  stationarity for 平穩 and 平穩性, likelihood and likelihood function, hypothesis test and hypothesis testing,
  percentile interval and percentile confidence interval, out-of-sample forecast and forecasting) are Glossary
  headword variants and stay, except where a box glosses a noun with an adjective (LM25 L262: 平穩性（stationarity）).
  LM8's 只做多 becomes 作多, 樂詞網's form, at Stage 4 (plans/vol-4.md).

## Volume closing check (X4), 2026-10-20

A fresh, read-only agent checked the eight modules after revision 3 as one volume (`scratch/rev3/X4.md`), beside
the closing checks C19–C26 and their second checks S19–S26: no critical or major item. Every X and XB decision holds;
tags, labels, cross-module numbers, conventions and notation agree. Its items and the editor's decisions:

| # | Finding | Decision |
|:--|:--|:--|
| 1 | Pointer-only citations follow two rules (lm07 → 22 kept; LM24's pointers dropped). | One rule: a pointer or an illustrative value creates no prereq or lead (stated exactly in X5 below). The Stage 4 list drops lm07 → 22; LM23's prereq drops 22. |
| 2 | LM25 names no divisor and compares 81.4 with LM6's 83.4 across divisors. | Fixed (LM25's record). |
| 3 | LM23's test count leaves out tests it reads at 1.96. | Fixed (LM23's record). |
| 4 | LM26 prints R-squared and sample moments with neither a standard error nor a reason. | Fixed (LM26's record). |
| 5 | Five data exhibits lack a Source line (LM21, LM22, LM24). | Fixed (the records). |
| 6 | LM25 points to LM26 for a gap LM26 does not measure. | Fixed (LM25's record). |
| 7 | LM22 says Volume IV sets $r_f=0$; LM23 and LM25 use 2%. | Fixed (LM22's record). |
| 8 | "out of sample" and "out-of-sample". | Fixed (LM23's record). |
| 9 | LM18 prints 波動的群聚 against Volume IV's 波動群聚現象. | Stage 4 list (plans/vol-4.md). |

## Final check (X5), 2026-10-20

A fresh agent checked the volume after the closing fixes (`scratch/fix/X5.md`) beside the eight module final checks
(`scratch/fix/F19.md` … `F26.md`). Its items and the editor's decisions:

| # | Finding | Decision |
|:--|:--|:--|
| 1 | `src/syllabus.yaml` still describes LM26 as using 5-second data. | "intraday TAIEX data" (done). |
| 2 | X4's rule applied only to the cases it was decided on: LM21's prereq 4, LM23's 6 and LM25's 3 rest on a backward pointer or an illustrative value; the rule's wording does not say that forward pointers make leads. | Rule: a backward pointer or an illustrative value creates no prereq or lead; a forward [[LMn]] makes n a lead (plans/vol-4.md, shared decisions). LM21 drops 4, LM23 6, LM25 3; the Stage 4 list drops lm03 → 25, lm04 → 21 and lm06 → 23. LM20's [[LM13]] (a count LM20 cites from LM13) and LM19's [[LM10]] (LM10's factor) cite results and stay. |
| 3 | The Stage 4 list's lab wordings for `make_lab11.py:571` and `make_lab15.py:443` say more than LM20 gives, and the committed notebooks hold the same lines. | Reworded; labs 04, 11, 15 and 17 are regenerated at Stage 4 (plans/vol-4.md). |
| 4 | LM23's new median uses `np.median`, against the quantile rule. | `inverted_cdf` (LM23's record); the printed 87% holds. |
| 5 | SOURCES lacks four box forms (對數基差, 八分位數峰態, 對數報酬絕對值, 三次方、四次方). | Added after a 樂詞網 lookup. |
