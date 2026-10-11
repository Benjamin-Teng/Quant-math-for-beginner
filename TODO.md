# TODO — handoff (2026-10-11)

> 給接手的 Claude Code：先讀 `CLAUDE.md`，再依下列順序執行。每完成一項就 commit 並直接 push 到 `main`，並用繁體中文向 Benjamin 回報。

## Where things stand

- **Volume I is published (edition 0.2, 2026-10-11).** LM1–LM7 are on the site (`docs/`) with A4 PDFs and executed
  labs. Each module went through an independent review, a verifier, the editor's gates (a blind solve of every
  question with a key check, and a full audit of its numbers from `data/raw/`), revision rounds and a closing
  verification; the editor's fixes after closing passed fresh checks. Every finding in [`reviews/`](reviews/README.md)
  is verified fixed, except LM1's V12, withdrawn on the owner's clarification of 2026-10-11 (the GIPS citation is
  restored). The records hold the decisions; `project/PITFALLS.md` holds the lessons.
- Reviews and verifications use fresh Opus subagents, never Codex (the owner's instruction, 2026-10-10). The editor
  (main session) recomputes every major finding before accepting it and passes no agent claim through unchecked.
- Shared changes made while closing Volume I: inline formulas keep their punctuation and equation tags never print
  over formulas (`58c148c`); wide tables are not clipped on paper (`fc976e9`); `build.sh --pdf` fails on a PDF that
  Chromium shrank to fit (`build/qa/pdf_scale.py`; `build/qa/print_width.py` finds the cause). LM1, LM2, LM5 and LM6 are
  at the 40-page limit and LM4 and LM6 at or near 11,000 words: any addition needs a cut.
- The local branches `rev/lm01` … `rev/lm07` and their worktrees are merged (squash) and can be deleted.

## Owner action (not for Claude Code)

- Deferred by the owner (2026-10-10): ask GitHub Support (<https://support.github.com/request>, "Remove sensitive
  data") to remove cached views and pull-request references for commits purged on 2026-10-10 because they contained
  raw FinMind data: PR #1 head `e3ed88b`, and the old `main` commits `cfc45f0`, `a9de9cf`, `44d199c`, `8ec5034`,
  `f959c26`, `49b0748`, `5b56679`.
- Decisions asked of the owner in the 0.2 report: (1) AUTHORING §1's limits (sentences under 25 words, paragraphs of
  at most four sentences) were enforced on text the reviews touched, not swept through every older paragraph; sweep
  Volume I, or apply them from Volume II on? (2) Fullwidth `；` `：`, `-`, `%` and the en dash after an inline formula
  can still start a line at some screen widths (the renderer cannot hold them); accept, or rewrite those spots?

## Tasks, in order

1. **Optional:** refresh the private claude.ai artifact preview (needs a Claude session with the artifact tool);
   update the project progress note on claude.ai.
2. **Volumes II and III** (below), after the owner's answers to the two decisions above.
3. **Optional:** LM6's Solution with "Stage 1: $D_1,\dots,D_5=11.20,\ 12.544,…$" is one unbreakable inline formula
   that overflows a 320 px screen (the gate is 400 px); split it at the commas, then a fresh check.

## Then: the remaining volumes

Follow [`plans/ROADMAP.md`](plans/ROADMAP.md): batch 1 is Volumes II and III (LM8–LM18), then IV + V, VI + VII,
VIII and IX. For each batch, write the briefs (`plans/vol-N.md`, same format as `plans/vol-1.md`), collect and verify
the data (historical data from FinMind only), give writers AUTHORING §6 and `project/PITFALLS.md` up front, then
write → review → revise → verify → gates → publish as Volume I did, bumping the edition. Ask the owner about the open
decisions listed at the end of the roadmap before the batch that needs them.

The cycle that closed Volume I, per module on its own branch and worktree: writer → fresh verifier → the editor's
gates → writer → verifier → closing pass (writer + a verifier scoped to the fixes and the changed lines) → the
editor's small fixes → a fresh check → squash-merge. Before publishing: AUTHORING §10 (including the unshrunk PDF of
at most 40 pages), `build/qa/overflow.py` at 400 px and `build/qa/print_width.py` on every page, no dead links, and
`git grep --untracked -nE "uv pip install|python3 |bundled|source \.venv|import requests" -- src labs build data`
finds nothing (options before the pattern).
