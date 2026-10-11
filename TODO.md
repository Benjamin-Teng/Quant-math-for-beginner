# TODO — handoff (2026-10-11)

> 給接手的 Claude Code：先讀 `CLAUDE.md`，再依下列順序執行。每完成一項就 commit 並直接 push 到 `main`，並用繁體中文向 Benjamin 回報。

## Where things stand

- **Volume I is published (edition 0.2, 2026-10-11).** LM1–LM7 are on the site (`docs/`) with A4 PDFs and executed
  labs. Edition 0.2.1 adds the reordered Volumes V–VII, Volume I's punctuation fixes, and the Getting Started and
  Research hygiene pages. Each module went through an independent review, a verifier, the editor's gates (a blind solve of every
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

**Stage 1, before any writer starts.** Done on 2026-10-11; every item had a fresh Opus check and the editor's
re-check of each fix.

1. **Data.** 403 files under `data/raw/sectors/` (TAIEX and the 30 TWSE sector indices, 2007-07-02 → 2026-10-08).
   FinMind serves copied values in that series (PITFALLS §3), so 561 closes under `data/raw/sectors_close/` (the
   13:30:00 value of `TaiwanStockEvery5SecondsIndex`) replace them and 52 files under `data/raw/taiex_close/` confirm
   TAIEX; `data/vol2_series.py` builds `data/processed/vol2_closes.parquet` and stops on anything it cannot explain.
   A free-plan reader skips `sectors_close/` with `fetch_finmind.py --exclude`. An independent check compared 640
   closes on extreme days with the 13:30:00 values: all match, and GlassCeramic's high volatility is real.
2. **Anchor numbers.** `plans/vol-2-anchors.md`, recomputed by independent code; its corrections are applied and each
   module's status line records them.
3. **Notation.** AUTHORING §6 has the vectors-and-matrices table and the $L$ and $\lambda$ rows.
4. **Tooling.** Bar, heatmap, scatter and vector charts in `src/assets/book.js`, with build gates; `build/qa/style.py`
   (AUTHORING §1 counts and formula punctuation) and `build/qa/display_scroll.py` (§10 items 7 and 8); the notation
   row on the front page. **Left for Stage 2:** `data/make_lab_data.py` must export the sector closes (and the repair
   rule's inputs) to each Volume II lab's `data/` folder, and run without `sectors_close/`; `book.js` measures chart
   labels before the web fonts load (a label's width can be off by up to about 13 px, enough to cross an edge), so
   redraw the charts on `document.fonts.ready` before the first Volume II scatter or vector chart is published.
5. **Volume I punctuation.** The 15 spots are rewritten; `style.py` finds none left.
6. **Briefs.** `plans/vol-2.md`, from two designs per module and the editor's decisions. Its facts were checked on
   official pages, software references and bibliographic records (`project/SOURCES.md`), and its Chinese terms come
   from 樂詞網 (AUTHORING §1).
7. **Renumbering and two new pages.** Volumes V–VII reordered and LM27–LM40 renumbered (edition 0.2.1): syllabus,
   front-page map, Volume I's references and leads, the LM7 lab, AUTHORING, SPEC, `plans/vol-1.md`. The **Getting
   Started** and **Research hygiene** pages are published; every Volume II module that estimates, selects or
   backtests carries a short note pointing to the second.

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
- Volume I has 92 display formulas that scroll inside their own box at 400 px (`build/qa/display_scroll.py`; LM1–LM7:
  8, 15, 14, 10, 19, 9, 17). AUTHORING §10 item 8 applies from Volume II; break the worst with `aligned` if time allows.
- For the owner (site code): after a click in a long outline, the keyboard's Page Down, Space and End scroll the
  outline panel, not the page: Chromium scrolls the box that was clicked last, although the link loses the focus on
  the jump (the behaviour predates 0.2.1). Moving the focus to the target heading (`tabindex="-1"`,
  `focus({preventScroll: true})`) fixes it in a test: Page Down then scrolls the page.
- `uv run ruff check data` reports I001 in `data/build_series.py` and `data/check_chunk.py` and B023 in
  `build_series.py` (a lambda that reads the loop's `divd`; it runs inside the same iteration, so the result is
  right). Tidy them when those files next change.

## Then: the remaining volumes

Follow [`plans/ROADMAP.md`](plans/ROADMAP.md): batch 2 is Volume III (LM13–LM18), then IV, V + VI, VII, VIII and IX.
Each batch repeats Stages 1–4 and bumps the edition. Ask the owner about code, site, repository and his standing
rules, and about the open decisions at the end of the roadmap before the batch that needs them; content is the
editor's call.
