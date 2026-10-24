# Reviews

One record per module: the independent reviewer's findings, the editor's decisions, each revision round, its
verification and the editor's gates. A module is published only when every finding is verified fixed or its non-fix
is explained (AUTHORING §11). Templates for reviewer, writer and verifier prompts: [`REVIEW_PROMPT.md`](REVIEW_PROMPT.md).

Finding IDs: the review's own numbers (1, 2, …; LM6's review numbers them by severity, C1/M1/m1), V1… for a
verifier's new findings, and K1… (key check against a blind solution) and A1… (full number audit) for the editor's
gates. Volume II adds X1… (round 1's cross-module check), VX1… (verification 1's Volume II re-check), and C1… and
CX1… (the closing check's new module and volume findings). From Volume III, U1… are the number auditor's unclear
definitions, and round 1 may number its items by severity (C1, M1, m1). Volume IV adds N1… and F1…, a verifier's new
findings after revisions 1 and 2. After revision 2, LM21, LM23 and LM25 write N, V and m instead; LM24's
consolidation and LM26's final check also use N. XB1… are the editor's cross-module decisions, and the Stage 1 brief
cross-check's items are X1–X40 (`plans/vol-4.md`). In Stage 3 a bare X1–X11 is a round-1 item. The later volume
checks are named X2–X6, and their items are cited by number ("X3 item 6").

## Status (2026-10-11): Volume I published in edition 0.2

| Module | Review | Round 1 | Gates | Stage |
|:--|:--|:--|:--|:--|
| [LM1](lm01.md) Exponentials, Logarithms and Compounding | 21 (2 critical, 4 major) | all 21 verified; V1–V5 | K1–K10, A1–A14 (3 major) | **published** in 0.2; closed, merged `7129c5a`; V12 withdrawn on the owner's clarification and the GIPS citation restored (2026-10-11) |
| [LM2](lm02.md) Limits and Derivatives | 19 (5 major) | all 19 verified; V1–V8 | K1–K7 (2 major), A1–A10 (1 major) | **published** in 0.2; closed, merged `8ac0f31` |
| [LM3](lm03.md) Taylor Series and Approximation | 34 (edition 0.1, all fixed) | — | K1–K16 (3 major), A1–A27 (4 major) | **published** in 0.2; closed, merged `c85df84` |
| [LM4](lm04.md) Optimization in One Variable | 24 (1 critical, 8 major) and length | 23 verified, 12 reopened; V1–V5 | K1–K6, A1–A11 | **published** in 0.2; closed, merged `bca9443` |
| [LM5](lm05.md) Integration | 21 (5 major) | fixes verified; V1–V7 (V5 raised to major) | K1–K6 (1 major), A1–A11 (2 major) | **published** in 0.2; closed, merged `53bf10c` |
| [LM6](lm06.md) Sequences, Series and the Time Value of Money | 29 (2 critical, 5 major) | all 29 verified; V1–V10 (2 major) | K1–K8 (2 major), A1–A14 (1 major) | **published** in 0.2; closed, merged `e528863` |
| [LM7](lm07.md) Multivariable Calculus and Lagrange Multipliers | 23 (1 critical, 5 major) and 2 editor items | 22 and both items verified, 1 reopened; V1–V5 (1 major) | K1–K9 (1 critical = finding 1, 1 major), A1–A15 (1 major) | **published** in 0.2; closed, merged `2681d71` |

LM3's 34 findings of edition 0.1 were fixed before the first push; its record starts with the gates on that text.

## Status (2026-10-20): Volume IV published in edition 0.5

| Module | Round 1 | Revisions 1–3 | Closing check | Stage |
|:--|:--|:--|:--|:--|
| [LM19](lm19.md) Descriptive Statistics of Returns | 29 items (1 critical, 2 major) | Rev. 1: 0 reopened; N1–N2 (minor). Rev. 2: none new | 5 items (minor), all confirmed | final check ready; published in 0.5 |
| [LM20](lm20.md) Estimation Theory and Maximum Likelihood | 29 items (4 major) | Rev. 1: 0 reopened; N1–N3 (minor). Rev. 2: F1–F5 (minor) | 4 items (minor), all confirmed | final check ready; published in 0.5 |
| [LM21](lm21.md) Hypothesis Testing and Multiple Testing | 21 items (1 critical; 1 major, in LM20's text) | Rev. 1: 0 reopened; none new. Rev. 2: N1–N2 (minor) | 3 items (minor), all confirmed | final check: 1 minor item, fixed; published in 0.5 |
| [LM22](lm22.md) Resampling Methods | 29 items (1 critical, 4 major) | Rev. 1: 0 reopened; N1 (major), N2–N4 (minor). Rev. 2: F1–F5 (minor) | 6 items (minor or trivial), 3 confirmed, 3 refuted | final check ready; published in 0.5 |
| [LM23](lm23.md) Linear Regression | 27 items (1 critical, 3 major) | Rev. 1: 0 reopened; N1–N3 (minor). Rev. 2: V1–V4 (minor) | 8 items (1 major), all confirmed | final check: 2 minor items, fixed; published in 0.5 |
| [LM24](lm24.md) Bayesian Inference and Shrinkage | 23 items (5 major) | Rev. 1: 0 reopened; N-1 to N-4 (minor). Rev. 2: F1–F2 (minor) | 6 items (minor), 5 confirmed, 1 refuted | final check: 1 minor item, fixed; published in 0.5 |
| [LM25](lm25.md) Time Series I: ARMA, Unit Roots and Cointegration | 25 items (4 major) | Rev. 1: 0 reopened; N1–N2 (minor). Rev. 2: m1–m4 (minor) | 9 items (1 major), 8 confirmed, 1 settled | final check ready; published in 0.5 |
| [LM26](lm26.md) Time Series II: Volatility Models | 34 items (6 major) | Rev. 1: 0 reopened; N1–N3 (minor). Rev. 2: F1–F5 (minor) | 5 items (1 major), all confirmed | final check: 4 minor items, fixed; published in 0.5 |

Round 1 (2026-10-19) ran fresh, read-only checks on each draft (`157461e`). They were the independent reviewer, the
blind solver (K), the number auditor (A, U) and a Volume IV cross-module check (X). A fresh agent per module merged
the module checkers' findings into 217 items and re-checked every critical and major item adversarially. Four items were critical
(LM19, LM21, LM22 and LM23) and 29 were major. The editor confirmed each decision. The cross-module check found 11
items (X1–X11), none major. Three revisions followed. Revisions 1 and 2 (`692799a`, `15b0071`) were each verified by
fresh agents and a volume re-check (X2, X3). Verification 1 reopened nothing and found 21 new items, one major (LM22
N1: a bootstrap theorem was implied to cover data without its moments). Verification 2 found 27 new minor items. X2
found 9 volume items (2 major) and X3 found 8 (none major). Revision 3 applied the minor items of verification 2 and
X3; LM19 needed no change. The editor's cross-module decisions are XB1–XB11 in `vol4_cross.md`.

The closing check (2026-10-20) ran one fresh reviewer per module and a volume check (X4). It found 46 module items and
9 volume items. Only three were major, all in modules. LM23's out-of-sample result for the first-half hedge ratio
rested on one selected sector. LM25 stated a half-life as a fact of the data. LM26's "15-second days" were not the
sample it defines. A fresh adversarial second check confirmed 41 module items, refuted 4 and left 1 to an earlier
decision. The final check verified the fixes. It found LM21, LM23, LM24 and LM26 not ready, for 8 minor items in all,
and raised 5 volume items (X5). Every module then ended READY TO PUBLISH, and a last check found the front matter
consistent (X6). Edition 0.5 was published on 2026-10-20 (`bc4930c`). Not copied back into the briefs or the
anchors, by the preface of `plans/vol-4.md`: values and wording that a revision changed. From Stage 3 the modules and
their numbers scripts are authoritative.

The records cite the agents' working reports under `scratch/`, which were never committed. They state every finding
and decision, with one gap. For the closing check's minor items and the fixes its second check changed, they give
counts and verdicts only. The text of those items is lost; the published modules carry the result. From Volume V a
record states every item and its fix itself (PITFALLS §6).

## Status (2026-10-18): Volume III published in edition 0.4

| Module | Round 1 | Verification 1 | Closing check | Stage |
|:--|:--|:--|:--|:--|
| [LM13](lm13.md) Probability Foundations and Bayes | 31 items (3 major) | 0 reopened; V1–V4 (minor) | 8 items (minor), 7 fixed, C5 not a defect | published in 0.4 |
| [LM14](lm14.md) Random Variables, Expectation and Jensen's Inequality | 31 items (5 major) | 0 reopened; V1–V4 (minor) | 10 items (minor), all fixed or decided | published in 0.4 |
| [LM15](lm15.md) Distributions in Finance | 34 items (6 major) | 1 reopened (minor); V1–V2 | 10 items (minor), all fixed or decided | published in 0.4 |
| [LM16](lm16.md) Joint Distributions and Dependence | 30 items (5 major) | 0 reopened; V1 (minor) | 8 items (1 major), all fixed | published in 0.4 |
| [LM17](lm17.md) Law of Large Numbers and Central Limit Theorem | 29 items (5 major) | 0 reopened; V1–V3 (minor) | 7 items (minor), all fixed | published in 0.4 |
| [LM18](lm18.md) Monte Carlo Simulation and the Bootstrap | 37 items (1 major) | 1 reopened (minor); V1–V3 | 9 items (minor), all fixed | published in 0.4 |

Round 1 (2026-10-18) ran the independent reviewer, the blind solver (K), the number auditor (A) and a Volume III
cross-module check (X) on each draft (`dcff66b`), all fresh and read-only. No item is critical; the blind solvers agreed
with every answer key, and the auditors reproduced every printed number from the raw data. A fresh agent per module
merged the reports, re-checked every major item adversarially and proposed the decisions, which the editor confirmed.
Two revisions followed, each verified by fresh agents (verification 1 and a volume re-check VX, in
`vol3_cross.md`). The closing check (one fresh verifier per module and a volume check CX) found 52 module items and
9 volume items, one major (LM16: the multivariate normal for a singular covariance matrix, now cited to Durrett
§3.10); a fresh adversarial second check confirmed or amended each and gave the final text, and a fresh final check
found the volume ready to publish. Not copied back into the brief or the anchors, by the brief's preface: values,
tags and wording that a revision changed (for example A16-39, A16-42, A17-71 and LM18's tags).

## Status (2026-10-17): Volume II published in edition 0.3

| Module | Round 1 | Verification 1 | Closing check | Stage |
|:--|:--|:--|:--|:--|
| [LM8](lm08.md) Vectors and Matrices | 26 findings (8 major), all verified | V1–V3 (minor): V1 and V2 fixed in revision 2, V3 by the editor in the brief | 3 items verified; C1 not a defect (the brief keeps the plan); CX8 fixed | **published** in 0.3 |
| [LM9](lm09.md) Linear Systems, Inverses and Rank | 29 findings (2 major), all verified | V1–V4, VX5, VX7; X26 reopened for LM12 | 7 items verified; CX8 fixed; CX3 not a defect | **published** in 0.3 |
| [LM10](lm10.md) Quadratic Forms and Covariance Matrices | 42 findings (9 major) | 10, K6 and A7 reopened; V1–V6, VX3, VX8 | 11 items verified; C1, C2 and CX6 fixed; CX5 added to ROADMAP; CX1 not a defect | **published** in 0.3 |
| [LM11](lm11.md) Eigen-decomposition and PCA | 41 findings (2 critical, 4 major) | V1–V6, VX3, VX4, VX9 | 9 items verified; C1 (as amended), C2 and CX6 fixed; CX3 not a defect | **published** in 0.3 |
| [LM12](lm12.md) Cholesky, SVD and Least Squares | 42 findings (6 major) | V1, VX1, VX2, VX6; X26 reopened | 5 items verified; C1 and CX7 fixed; CX2 not a defect | **published** in 0.3 |

Round 1 ran the independent reviewer, the blind solver (K), the number auditor (A) and a Volume II cross-module check (X) on each draft; the IDs in each record follow that order. The closing check (2026-10-17) ran one fresh verifier per module and a Volume II re-check (CX); every new item then had a fresh adversarial second check. It reopened nothing and found 6 module items and 8 volume items, all minor. Six are not defects: LM8 C1 and CX1–CX3 ask the brief to copy back what the modules wrote after the plan, in their drafts or revisions, which its preface rules out; CX4 asks to drop Golub and Van Loan §8.3, a pointer inside the cited ch. 8; CX5 asks for a ROADMAP line, added anyway. The editor's fixes are `decb0a6` (before the check) and `e55dba4`.

Findings left unfixed in Volume II, each by a recorded decision: LM8 11 and X25 (s_i stays the standard deviation; AUTHORING §6 was amended instead), LM9 V4 (上三角矩陣 is the volume's settled term), LM11 21 (two departures from the brief confirmed by the editor), the items above judged not defects (LM8 C1 and CX1–CX4), and two of LM11 V6's five brief edits ('separate movements', ρ = 0.5749), which the brief's preface also leaves out. Every other "no change" row in the records points to a fix made in another file or to a part that does not apply to that module.
