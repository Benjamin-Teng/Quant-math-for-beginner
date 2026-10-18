# Volume III cross-module checks

Round 1's cross-module check (X1–X9) is recorded in the module records (`lm13.md` … `lm18.md`), row by row. Below: verification 1's fresh volume re-check (VX), 2026-10-18, against `1956c57`.

## Verification 1 (VX)

- **Scope:** LM13–LM18 at `1956c57` against the drafts at `dcff66b`, with the round-1 cross-module findings X1–X9 as
  recorded in `reviews/lm13.md` … `lm18.md`. The check was fresh and read-only. Line numbers refer to `1956c57`.
- **Method:**
  - Scripts in `scratch_VX/`:
    - `xref.py` and `tagctx.py` list every `[[LMn]]` link and every cross-module tag citation.
    - `numquote.py` compares numbers quoted with an `[[LMn]]` link against the cited module.
    - `zh.py` and `zhfirst.py` dump the 中文導讀 boxes and the Glossaries.
    - `recompute.py` and `gilpelaez.py` recompute from `data/raw/vol3/TAIEX_TR__2003-01-01__2026-10-08.csv`.
  - Reading: `plans/vol-3.md` (Shared decisions, Stage 4 list, LM18 brief), `plans/vol-3-anchors.md`, AUTHORING §5,
    §6 and §8, and `project/SOURCES.md`.
  - `git status` stayed clean.

### X findings

| X | Modules | Decision | Status | Evidence at `1956c57` |
|:--|:--|:--|:--|:--|
| X1 | LM13 | cite [[LM1]] in the notation note; keep prereq 1 and the Stage 4 lead | verified | lm13.md:52 "total returns as in [[LM1]]"; prereq `[1, 3, 4, 5]`; plans/vol-3.md:263 lm01 gains 13 |
| X2 | LM16 | one box "Independence and the product rule" with (16.1) holding both; Glossary "factorizes, (16.1)" | verified | lm16.md:127–131 (the definition is the first line of (16.1)); lm16.md:646 |
| X2 | LM17 | no change if LM16 moves the definition into (16.1) | verified | lm17.md:61 "independent ((13.13), (16.1))" now points at the definition |
| X2 | LM18 | uniform draws cite [[LM16]]'s definition, or (16.1) once LM16 moved it; (18.1) cites [[LM14]]'s quantile function for 0<u<1 | verified | lm18.md:66 "independent as [[LM16]] defines it". The decision preferred "(16.1)" once LM16 moved the definition; the [[LM16]] form is acceptable, so this is optional. lm18.md:96 cites [[LM14]] for 0<u<1. lm18.md:331 keeps (13.13) for the discrete $\hat F$ |
| X2 | LM13, LM14 | no change | verified | — |
| X3 | LM15 | ([[LM14]]) for the 175 days; "[[LM14]]'s sample median, 0.0879%" | verified | lm15.md:114; lm15.md:349 |
| X3 | LM17 | ([[LM13]]) for 3,205 and 2,644; ([[LM15]]) for the five losing years; Problem 7 keeps five years | verified in the text; the records conflict (VX3) | lm17.md:118 and :345; lm17.md:537 and :563 keep five years. reviews/lm18.md row "7, X3" still says that LM17's record restores the one- and ten-year horizons |
| X3 | LM18 | ([[LM14]]) for the median; ([[LM13]]) for the 15 days | verified | lm18.md:133; lm18.md:375 |
| X4 | LM15 | one [[LM26]] pointer; Solution 2 keeps its sentence without the link | verified | the only [[LM26]] is lm15.md:170; lm15.md:595 has no link |
| X5 | LM13 | §6 box: 累積分布函數（distribution function）, 指示函數（indicator） | verified | lm13.md:408; the residual gloss mismatch with LM14 and LM17 is VX4 |
| X5 | LM16 | 獨立（independent）, 獨立的常態 | verified | lm16.md:426 |
| X5 | LM18 | 累積分布函數（distribution function）, 互斥（disjoint）, 期望值（expectation）; Glossary term | verified | lm18.md:127, :321, :201/:321/:390; Glossary lm18.md:563 "蒙地卡羅估計量" (the 樂詞網 record in SOURCES is still pending, see Observations) |
| X6 | LM13 | 事件（event）, 結果（outcome） in the §3, §4 and §6 boxes | verified | lm13.md:182, :249, :408 |
| X6 | LM15 | 稀有事件（rare event） | verified | lm15.md:176 |
| X6 | LM18 | 事件（event）, 獨立（independent） | verified | lm18.md:321, :390 |
| X7 | LM14 | 樣本平均數…；[[LM3]] 所說的母體變異數（population variance） | verified | lm14.md:186 |
| X8 | LM14 | the 2003 caveat in Exhibits 7 and 8 | verified | lm14.md:441, :448 |
| X8 | LM17 | the 2003 caveat in X6's note | verified | lm17.md:358 (the note is split in two paragraphs, as the hand-back records) |
| X9 | LM18, plans | literal seeds in the stems and notes; the case box points to the examples; plans/vol-3.md:100 | verified | `default_rng([e, 20261011])` printed in lm18.md:156, :186, :214, :267, :301, :340, :352 and :384; case box lm18.md:35 points to [[eg:mcase]] and [[eg:bcase]]; the overview exception is recorded; plans/vol-3.md:100 now says "Different `e`" |

No X finding is reopened.

### Cross-module checks that passed

- **Tags.**
  - Every cross-module tag citation in LM13–LM18 names a tag that exists with the cited content: 13.4–13.8, 13.11–13.13; 14.1, 14.3–14.8, 14.10, 14.12; 15.1, 15.2, 15.6, 15.7, 15.9; 16.1, 16.3, 16.7; 17.1, 17.4–17.6.
  - LM18's internal citations (18.1)–(18.9) match the renumbered displays: lm18.md:102–570, the Glossary, `lm18.js`, `lm18_numbers.py`, `lm18_charts.py` and `make_lab18.py`.
  - No other module or earlier volume cites an (18.x) tag.
  - LM18's "(17.4) with μ=R̄" (lm18.md:345, :492, :527) stays as LM18's record decides (M2 declined). LM17's Glossary cites (17.4) for the mean path.
- **Front matter.**
  - Prereq and leads agree both ways within LM13–LM18.
  - Every earlier module cited for a result is in the citing module's prereq.
  - Each Stage 4 addition (plans/vol-3.md:263–264) matches a Volume III prereq, and no Volume III prereq is missing from it: lm01 gains 13–18, lm02 15 and 18, lm03 13, 15, 16 and 17 (14 is already there), lm04 13, 14 and 17, lm05 13 and 16, lm07 16, lm09 16.
  - The links the revision added ([[LM1]] in LM13; [[LM16]] in LM14, LM15 and LM18; [[LM3]], [[LM13]] and [[LM15]] in LM17; [[LM21]] in LM16) all fall within the front matter.
- **Numbers quoted across modules.** Each reproduces from the raw closes and equals the source module's printed value:
  - T 5,849 (3 Jan 2003 – 8 Oct 2026); 3,205 up and 2,644 down; 175, 108 and 15 threshold days; the median 0.0879%.
  - Skew −0.34, excess kurtosis 5.27, kurtosis 8.27; the running excess kurtosis 4.25 → 4.94 on 7 April 2025.
  - 8,680 days, 23.7645 years, A = 246.12 (the same wording in LM14, LM15, LM17 and LM18).
  - r̄ 0.055170%, s_r 1.2107%, R̄ 0.062505%, s 1.2084%.
  - The 2003–2025 refit: 0.047292%, 1.18352%, 11.634%, 18.563% and 26.54% by (17.6). LM15 prints 0.1163 and 0.1856.
  - Five years 5.49%; lag-1 correlation of |r| 0.161 and of r 0.039.
  - Monthly counts: mean 0.612, variance 1.846, 286 months.
  - 5 losing years; μ_X 0.11646, σ_X 0.22207; 30.0%.
  - LM14's 0.7316 bp, 13.58% and δ(2) = 2.936 bp as quoted in LM17.
- **Ownership ("Return type", C1).**
  - Every TR23 statistic quoted outside its owner now carries the owner's pointer.
  - LM17's kurtosis jump cites [[LM15]] (lm17.md:435).
  - LM15's lab extension now uses five-session log returns and points to LM17 (make_lab15.py:441–453).
- **Notation (AUTHORING §6).**
  - No module uses P, E, \hat\mu, \kappa or \theta in a way the table forbids.
  - LM18's v is gone.
  - $\mathcal A$ is used in the annualizing modules and A, B only in LM13.
  - k, m, n, λ, ν, L, B, η, ζ and d² each keep their table meaning across the six modules.
- **Simulation and data rules.**
  - Only LM18 simulates; no rng appears in LM13–LM17, their labs, scripts or widgets.
  - Every LM18 experiment prints its literal seed or points to the example that does. The lab and scripts use `default_rng([e, 20261011])` with the same e as the text.
  - LM12's `default_rng(20261011)` is kept as recorded.
  - LM16 alone uses U28, and LM18 loads no U28 data.
  - Every Source line names `TaiwanStockTotalReturnIndex`, retrieved 18 October 2026, or LM16's `TaiwanStockPrice`, retrieved 11 October 2026.
  - The revision added no raw data files.

### New findings

| # | Severity | Modules, lines | Finding | Correction |
|:--|:--|:--|:--|:--|
| VX1 | minor (records) | plans/vol-3.md:238, 1949–1950, 1958–1959, 1978–1982, 2035, 2047, 2074–2092, 2125, 2185–2301; plans/vol-3-anchors.md:637 (A18-13), :645 (A18-21) | LM18's tag renumbering was not carried into the plans, although reviews/lm18.md item 1 assigns it to the editor; `1956c57` changes only plans/vol-3.md:100, 534 and 2099. The brief's tag-user map now names the wrong displays. For example, line 1949 says that LM20 and LM22 cite (18.7) for the bootstrap moments, which is now importance sampling; LM30's (18.9) is now $\E_{\hat F}G_{\text{boot}}$; LM45's (18.8) is now the bootstrap mean. Later volumes' briefs are told to honour these forward links. | Map old to new as (18.4)→(18.5), (18.5)→(18.6), (18.6)→(18.7), (18.7)→(18.8), (18.8)→(18.9) and (18.9)→(18.4). Line 1949–1950 becomes "LM20, LM22 cite (18.2), (18.3), (18.8); LM22 also (18.1), (18.9); LM30 (18.4); LM32 (18.1)–(18.3), (18.5)–(18.7); LM36, LM38 (18.2); LM39 (18.1); LM45 (18.9)". Renumber the tag list (2274–2301), the sections table, the E- and X-lines and the anchors' labels the same way |
| VX2 | minor | LM15:22 (overview), :263 (E6 solution), :274 (§5 box) | LM15 prints 26.5% as what "a model of independent days gives" ("虧損年機率降為 26.5%"). That value is the normal approximation (17.6): LM17 now writes "gives, by (17.6), 26.54%" (lm17.md:345). The model's exact value is 26.38% (Gil-Pelaez inversion here; reviews/lm17.md M4: 26.383%), which prints 26.4%. LM17's record M4 left "whether it says so" to LM15's record, which has no decision on it (AUTHORING §6: "≈" with the size of what was dropped). | Write "by [[LM17]]'s normal approximation, 26.5%" at :263, "about 26.5%" at :22, and 「以常態逼近約為 26.5%」 at :274; or print the exact 26.4% and say so. Decision C2's sentence stays |
| VX3 | minor (records) | reviews/lm18.md row "7, X3"; reviews/lm17.md row "m14 + X3"; lm17.md:537, :563 | The two records decide X3's five-year item in opposite directions. LM18's says that "LM17's record restores its brief's one- and ten-year horizons". LM17's keeps five years and declines the restoration, and the text follows LM17's record. | Amend LM18's row: "LM17 keeps five years (reviews/lm17.md, m14 + X3); LM18's formula row derives from (17.6), so no pointer is needed" |
| VX4 | minor | lm14.md:331, lm17.md:316 against lm13.md:408; lm15.md:472 against lm17.md:450 | The same Chinese term carries different English glosses. 指示函數 is glossed "(indicator)" in LM13, as X5 decided to match the Glossaries (lm13.md:581, lm14.md:606 "Indicator"), but "(indicator function)" in LM14's §5 box and LM17's §5 box; the English text never says "indicator function". 樣本峰態 is glossed "(sample kurtosis)" in LM17 (m13) but "(kurtosis)" in LM15's §8 box. | Use 指示函數（indicator） in LM14 and LM17, and 樣本峰態（sample kurtosis） in LM15 |
| VX5 | minor | LM15 boxes lm15.md:176, 233, 274, 381, 472 (nine uses of 台股); LM13 boxes lm13.md:128, 249 ("TR23"); lm18.md:201 | The Chinese name of TR23 differs by module. LM14's item 18 replaced 台股 with 加權股價報酬指數 (LM17's form), but LM15's boxes still call the total-return index 台股. LM13's boxes use the English label TR23 with no Chinese name. | Write 加權股價報酬指數 at first use in each LM15 box and 加權股價報酬指數（TR23） in LM13's first box. LM18's 「不是對台股的信賴區間」 may stay generic or name the index |
| VX6 | minor | lm15.md:274, :381; lm16.md:298; lm17.md:254, :368; lm18.md:390 | Some terms still lack their English at first use in a box (AUTHORING §1), after X6: 對數報酬 (log return) in LM15's §5 box and LM17's §4 and §6 boxes; 密度 (density) in LM15's §6 box; 平均數 (mean) in LM16's §5 box and LM18's §7 box. LM14 glosses all three. | Add （log return）, （density） and （mean） at those first uses |
| VX7 | minor | lm15.md:462, :466 ([[ex:choice]]) | The row "A calendar year's growth" prints year-based evidence (6.90 against 5 losing years, +15.16% against 14.97%), but the note lacks the 2003 caveat that X8 applied elsewhere (plans/vol-3.md:77–78: every exhibit with years says so). | Note: "…calendar years 2003–2025, 2003 from its first close" |
| VX8 | minor | LM13–LM15 data exhibits; LM16–LM18 | After LM17's m11 and LM18's item 5, LM16–LM18 give each data exhibit a Source line (LM16: "Source: as [[ex:case]]"). LM13 (7 exhibits), LM14 (9) and LM15 (11) carry one only on the case exhibit, as Volumes I–II do. The volume now follows two conventions. | Either add "Source: as [[ex:case]]." to LM13–LM15's data exhibits, or record that a case exhibit's Source line covers the module (the editor's choice) |
| VX9 | minor | References: lm13.md:587, lm14.md:622, lm15.md:643–644, lm16.md:664–665, lm17.md:601, :605, lm18.md:579 | The same book is cited in three forms. Grinstead and Snell is "2nd rev. ed. Providence, RI: American Mathematical Society" in LM13, LM14, LM16 and LM17; "2nd revised ed. Providence: American Mathematical Society" in LM15; and "2nd revised ed. American Mathematical Society" in LM18. Blitzstein and Hwang is "Boca Raton: CRC Press (Chapman & Hall/CRC)" in LM15, "Boca Raton: Chapman & Hall/CRC" in LM16 and "Boca Raton, FL: CRC Press" in LM17. | One form per book, e.g. LM13's for Grinstead and Snell and LM17's for Blitzstein and Hwang |
| VX10 | minor | lm18.md:47 against lm17.md:48, :197 | LM18's notation note justifies $Y_i^-$ with "a tilde marks centred data", while LM17, two modules earlier, writes $\tilde f$ for a second position. AUTHORING §6 reserves only $\tilde X$. | LM18: "(not $\tilde Y_i$, which recalls [[LM10]]'s centred $\tilde X$)", or drop the clause |

No critical or major item is new.

### Observations outside the X scope (shared-file actions decided in round 1, not in `1956c57`)

- **project/SOURCES.md.**
  - Durrett (2019), Theorem 1.7.2 is not recorded. LM16 now cites it (lm16.md:99, :666); LM16 item 10 assigns the record to the editor.
  - Blitzstein and Hwang §3.8 and §7.5 are recorded only as contents entries, while LM16 cites both for statements (lm16.md:130, :312, :664). LM16 item 3 makes reading and recording them a condition for keeping either citation (the owner's source rule).
  - The TechNews 2025-04-07 row (SOURCES line 70) is not extended with the 936 limit-down count (LM13 A3).
  - The 樂詞網 entry 蒙地卡羅估計量 is not recorded (LM18 hand-back).
- **plans/vol-3-anchors.md and the brief.**
  - A14-24 still cites lm05.md:366; A14-54 still prints 0.07% and 0.53%.
  - A16-39 and A16-42 still use the unrounded ρ.
  - A17-71 still prints 2,128 and 32.25%, and so does the brief's E5.
  - A18-21 and the brief's X3 still print ± 4%.
  - The brief's LM17 Leads line (plans/vol-3.md:1580–1581) says that LM18 cites (17.2); LM18 cites (17.1), (17.4), (17.5) and (17.6).
