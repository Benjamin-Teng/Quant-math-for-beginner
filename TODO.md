# TODO — handoff (2026-10-11)

> 給接手的 Claude Code：先讀 `CLAUDE.md`，再依下列順序執行。每完成一項就 commit 並直接 push 到 `main`，並用繁體中文向 Benjamin 回報。

## Where things stand

- **Volume I is published (edition 0.2, 2026-10-11).** LM1–LM7 are on the site (`docs/`) with A4 PDFs and executed
  labs. Each module went through an independent review, a verifier, the editor's gates (a blind solve of every
  question with a key check, and a full audit of its numbers from `data/raw/`), revision rounds and a closing
  verification. Every finding in [`reviews/`](reviews/README.md) is verified fixed, except LM1's V12, withdrawn on the
  owner's clarification of 2026-10-11. The records hold the decisions; `project/PITFALLS.md` holds the lessons.
- **The owner's decisions of 2026-10-11** (in `CLAUDE.md` and `project/SPEC.md`): he oversees code, site and
  repository; every content and editorial decision is the editor's (Claude's), reported with reasons; the process
  is the editor's choice (no SDD or OpenSpec); source authenticity comes first; Volume II is published on its own
  as edition 0.3, and Volume III becomes the next batch.
- **Writing rules from Volume II** (AUTHORING §1; why: PITFALLS §6): sentences average under 16 words and never
  exceed 30; paragraphs at most 80 words; connectors kept; at most 6,000 words of prose and 36 pages a module. The
  formula-punctuation rule applies to every volume. Volume I keeps its text and its 40-page limit.
- Reviews and verifications use fresh Opus subagents, never Codex (the owner's instruction, 2026-10-10). The editor
  (main session) recomputes every major finding before accepting it and passes no agent claim through unchecked.
- The local branches `rev/lm01` … `rev/lm07` and their worktrees are merged (squash) and can be deleted.

## Owner action (not for Claude Code)

- Deferred by the owner (2026-10-10): ask GitHub Support (<https://support.github.com/request>, "Remove sensitive
  data") to remove cached views and pull-request references for commits purged on 2026-10-10 because they contained
  raw FinMind data: PR #1 head `e3ed88b`, and the old `main` commits `cfc45f0`, `a9de9cf`, `44d199c`, `8ec5034`,
  `f959c26`, `49b0748`, `5b56679`.

## Volume II (edition 0.3)

The owner approved the tooling, the data pipeline and the repository process on 2026-10-11. Scope and module plan:
`plans/ROADMAP.md` and, once written, `plans/vol-2.md`.

**Stage 1, before any writer starts.**

1. **Data.** `TaiwanStockPrice` daily closes of TAIEX and the 30 TWSE sector indices (ROADMAP, "Daily sector indices
   need no intraday download"), from 2007-07-02 (2005-01-03 where a series starts then) to 2026-10-08, in windows under
   500 rows under `data/raw/sectors/`, each checked with `data/check_chunk.py` and registered with
   `data/fetch_finmind.py --add`; `data/README.md` updated.
2. **Anchor numbers.** An editor's script computes the facts the briefs rely on (the common sample and its $A$,
   sector correlations and PCA, condition numbers, the `Electronic` index against its eight sub-industries, TAIEX
   against the sector returns, LM8's P&L case); a second agent recomputes every quoted one with independent code.
3. **Notation.** Extend AUTHORING §6 for vectors and matrices before the briefs: bold column vectors, matrices as plain
   capitals, $^{\top}$ only, a generic matrix that is not $A$ (the annualization factor), a Cholesky factor that is not
   $L$ (leverage), eigenvalues $\lambda_k$ always subscripted, $\hat\Sigma$ dividing by $T$ (`ddof=0`), checked against
   every Volume I notation note.
4. **Tooling** (owner-approved): bar, heatmap, scatter and vector-diagram charts in `src/assets/book.js`;
   `build/qa/style.py` for the AUTHORING §1 counts and formula punctuation (then name it in §10 item 7); a 400 px
   check for display formulas that scroll (today's `overflow.py` skips scrolling boxes); `data/make_lab_data.py` for
   several series; a vector/matrix row in the front page's notation table. A fresh Opus agent reviews each piece.
5. **Volume I punctuation.** Rewrite the 15 spots where a hyphen or a fullwidth `；` `：` follows an inline formula
   (hyphens: lm01:79, lm03:22, lm03:396, lm05:335; `；`: lm01:279, lm05:191 twice, lm05:430; `：`: lm01:578, lm02:511,
   lm05:271, lm05:372, lm05:532, lm07:133, lm07:572) by AUTHORING §1's formula-punctuation rule; `style.py` finds none
   left; a fresh check; rebuild `docs/` and the PDFs.
6. **Briefs.** `plans/vol-2.md` in the format of `plans/vol-1.md`, plus per module: notation, concepts used before
   they are taught (with pointers), verified anchor numbers with their scripts, exhibits and chart types, a problems
   plan, lab parts and cross-module tags. A fresh Opus agent checks the briefs.

**Stage 2, writing.** Five writers in parallel, one module each on its own worktree branch (`vol2/lmNN`), with
AUTHORING (§1, §6), PITFALLS and the brief up front. First drafts stay under 5,500 words of prose; numbers scripts
assert from the start that every printed value appears in the text and follows from the printed inputs. Writers run
`style.py`, the build, `overflow.py` at 400 px, `print_width.py`, `pdf_scale.py` and `check_terms.py` before handing
back. At each hand-back the editor rebases the branch, fast-forwards `main` and pushes (drafts never reach `docs/`
without `status: published`), so review records cite commits on `main`.

**Stage 3, review.** Per module, in parallel in round 1: the independent reviewer (`reviews/REVIEW_PROMPT.md`), the
blind solver (K) and the number auditor (A, exact arithmetic from `data/raw/`); one consolidated list with the
editor's decisions → writer → verifier (fixes, changed lines, `style.py`) → closing pass → the editor's fixes → a
fresh check.

**Stage 4, publishing 0.3.** `status: published` for LM8–LM12; the 0.3 edition note; the README status table; prereq
and leads consistent both ways (Volume I modules gain leads to the Volume II modules that build on them, e.g. LM7 →
8, 9, 11; check the chips at 400 px), with a fresh check; `./build.sh --pdf`; AUTHORING §10 on every page,
`build/qa/overflow.py` at 400 px and `build/qa/print_width.py` on every page, no dead links, and
`git grep --untracked -nE "uv pip install|python3 |bundled|source \.venv|import requests" -- src labs build data`
finds nothing (options before the pattern).

## Optional

- Refresh the private claude.ai artifact preview (needs a Claude session with the artifact tool); update the project
  progress note on claude.ai.
- LM6's Solution with "Stage 1: $D_1,\dots,D_5=11.20,\ 12.544,…$" is one unbreakable inline formula that overflows a
  320 px screen (the gate is 400 px); split it at the commas, then a fresh check.

## Then: the remaining volumes

Follow [`plans/ROADMAP.md`](plans/ROADMAP.md): batch 2 is Volume III (LM13–LM18), then IV + V, VI + VII, VIII and IX.
Each batch repeats Stages 1–4 and bumps the edition. Ask the owner about code, site, repository and his standing
rules, and about the open decisions at the end of the roadmap before the batch that needs them; content is the
editor's call.
