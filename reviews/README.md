# Reviews

One record per module: the independent reviewer's findings, the editor's decisions, each revision round, its
verification and the editor's gates. A module is published only when every finding is verified fixed or its non-fix
is explained (AUTHORING §11). Templates for reviewer, writer and verifier prompts: [`REVIEW_PROMPT.md`](REVIEW_PROMPT.md).

Finding IDs: the review's own numbers (1, 2, …; LM6's review numbers them by severity, C1/M1/m1), V1… for a
verifier's new findings, and K1… (key check against a blind solution) and A1… (full number audit) for the editor's
gates. Volume II adds X1… (round 1's cross-module check), VX1… (verification 1's Volume II re-check), and C1… and
CX1… (the closing check's new module and volume findings).

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
