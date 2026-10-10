# Reviews

One record per module: the independent reviewer's findings, the editor's decisions, the writer's revision and the
verification. A module is published only when every finding is verified fixed or its non-fix is explained
(AUTHORING §11). Templates for reviewer, writer and verifier prompts: [`REVIEW_PROMPT.md`](REVIEW_PROMPT.md).

## Status (2026-10-10)

| Module | Critical | Major | Minor | Total | Fixed | Open | Not fixed (reason) | Stage |
|:--|--:|--:|--:|--:|--:|--:|:--|:--|
| [LM1](lm01.md) Exponentials, Logarithms and Compounding | 2 | 4 | 15 | 21 | 21 (writer-reported) | 0 | — | fixed, awaiting verification |
| [LM2](lm02.md) Limits and Derivatives | 0 | 5 | 14 | 19 | 19 (writer-reported) | 0 | — | fixed, awaiting verification |
| LM3 Taylor Series and Approximation | — | — | — | 34 | 34 | 0 | — | published (reviewed in edition 0.1) |
| [LM4](lm04.md) Optimization in One Variable | 1 | 8 | 15 | 24 | 1 (rendering, via preview build) | 23 | — | revision not started; length cuts also pending |
| [LM5](lm05.md) Integration | — | — | — | — | — | — | — | review to be rerun |
| [LM6](lm06.md) Sequences, Series and the Time Value of Money | 2 | 5 | 22 | 29 | 1 (rendering, via preview build) | 28 | — | revision not started |
| [LM7](lm07.md) Multivariable Calculus and Lagrange Multipliers | 1 | 5 | 17 | 23 | 0 | 23 | — | revision not started |

LM3's 34 findings (edition 0.1) were fixed before the first push; they have no separate record. "Writer-reported"
becomes "verified" once a verifier confirms each row.

When everything is done, report this table to the owner with the final counts and the reason for every finding
left unfixed.
