# Reviews

One record per module: the independent reviewer's findings, the editor's decisions, each revision round, its
verification and the editor's gates. A module is published only when every finding is verified fixed or its non-fix
is explained (AUTHORING §11). Templates for reviewer, writer and verifier prompts: [`REVIEW_PROMPT.md`](REVIEW_PROMPT.md).

Finding IDs: the review's own numbers (1, 2, … or C1/M1/m1), V1… for a verifier's new findings, and K1… (key check
against a blind solution) and A1… (full number audit) for the editor's gates.

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

## Status (2026-10-12): Volume II in Stage 3

| Module | Review | Round 1 | Gates | Stage |
|:--|:--|:--|:--|:--|
| [LM8](lm08.md) Vectors and Matrices | round 1: 26 findings (8 major) | revision | — | draft on `main` |
| [LM9](lm09.md) Linear Systems, Inverses and Rank | round 1: 29 findings (2 major) | revision | — | draft on `main` |
| [LM10](lm10.md) Quadratic Forms and Covariance Matrices | round 1: 42 findings (9 major) | revision | — | draft on `main` |
| [LM11](lm11.md) Eigen-decomposition and PCA | round 1: 41 findings (2 critical, 4 major) | revision | — | draft on `main` |
| [LM12](lm12.md) Cholesky, SVD and Least Squares | round 1: 42 findings (6 major) | revision | — | draft on `main` |

Round 1 ran the independent reviewer, the blind solver (K), the number auditor (A) and a Volume II cross-module check (X) on each draft; the IDs in each record follow that order.

When everything is done, report this table to the owner with the final counts and the reason for every finding
left unfixed.
