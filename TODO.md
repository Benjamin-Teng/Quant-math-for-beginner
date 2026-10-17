# TODO — handoff (2026-10-17)

> 給接手的 Claude Code：先讀 `CLAUDE.md`，再依下列順序執行。每完成一項就 commit 並直接 push 到 `main`，並用繁體中文向 Benjamin 回報。

## Where things stand

- **Volumes I and II are published (edition 0.3, 2026-10-17).** LM1–LM12 are on the site (`docs/`,
  <https://quantmath.fintools.tw>) with A4 PDFs and executed labs. Volume II went through the four stages below: the
  briefs, data, anchors and tooling; five writers; a review round (reviewer, blind solver, number auditor and a
  cross-module check: 180 items, 2 critical (one defect, LM11 finding 1 = K1), 29 major), two revisions, a verification and a closing check; then
  publication. Each `reviews/lmNN.md` holds the findings, decisions and rounds; `reviews/README.md` lists the findings
  left unfixed and why. `project/PITFALLS.md` holds the lessons.
- **The owner's decisions of 2026-10-11** (in `CLAUDE.md` and `project/SPEC.md`): he oversees code, site and
  repository; every content and editorial decision is the editor's (Claude's), reported with reasons; the process
  is the editor's choice (no SDD or OpenSpec); source authenticity comes first.
- **Writing rules from Volume II** (AUTHORING §1; why: PITFALLS §6): sentences average under 16 words and never
  exceed 30; paragraphs at most 80 words; connectors kept; at most 6,000 words of prose and 36 pages a module. The
  formula-punctuation rule applies to every volume. Volume I keeps its text and its 40-page limit.
- Reviews and verifications use fresh Opus subagents, never Codex (the owner's instruction, 2026-10-10). The editor
  (main session) recomputes every major finding before accepting it and passes no agent claim through unchecked.
- **Publishing deploys the site.** GitHub Pages serves `docs/` from `main` (README, "Hosting"), so a push that
  carries a rebuilt `docs/` goes live; nothing is built on GitHub. Run `./build.sh --pdf` and commit `docs/` with
  `src/`, `data/` and `labs/` (AUTHORING §11).
- **PDF links** (owner-approved, 2026-10-17): `build/render_pdf.py` sends a link to another page of the book to the
  live site (the domain in `docs/CNAME`) and keeps same-page anchors as internal PDF links; before, Chromium printed
  them as `file:///` paths on the author's disk. After `./build.sh --pdf`, `grep -ac 'file:///' docs/pdf/*.pdf`
  gives 0 for every file.
- The brief and anchors keep the plan and the corrected facts (preface of `plans/vol-2.md`); values and wording that
  a revision changes in a module are not copied back. Four of the closing check's six refuted items (LM8 C1, CX1–CX3) rest on this rule; reviews/README.md gives the
  reasons for CX4 and CX5.

## Owner action (not for Claude Code)

- Deferred by the owner (2026-10-10): ask GitHub Support (<https://support.github.com/request>, "Remove sensitive
  data") to remove cached views and pull-request references for commits purged on 2026-10-10 because they contained
  raw FinMind data: PR #1 head `e3ed88b`, and the old `main` commits `cfc45f0`, `a9de9cf`, `44d199c`, `8ec5034`,
  `f959c26`, `49b0748`, `5b56679`.
- Optional, site code: the front page's install block (`build/build_index.py`, the `git clone … cd …` line) is
  755 px wide in print against the 680 px text width (`build/qa/print_width.py docs/index.html`). It was so in 0.2;
  on screen it scrolls inside its box, and the front page has no PDF.
- Optional, `book.js`: the options the Volume II writers asked for (bar-label text for LM8's `angles`, ellipses above
  points for LM11's Exhibit 3, a significant-figure `Book.fmt` code); the modules work without them.

## Next: Volume III (edition 0.4)

Follow [`plans/ROADMAP.md`](plans/ROADMAP.md): batch 2 is Volume III (LM13–LM18), then IV, V + VI, VII, VIII and IX.
Each batch repeats Stages 1–4 and bumps the edition (the owner confirmed the process, 2026-10-11). Ask the owner about
code, site, repository and his standing rules, and about the open decisions at the end of the roadmap before the batch
that needs them; content is the editor's call.

**Stage 1, before any writer starts**, in this order:

1. Briefs (`plans/vol-3.md`) within ROADMAP's module boundaries, with notation that follows AUTHORING §6 ("Common
   notation first"). Volume II's forward links name what Volume III owes: LM16 (population covariance and joint
   distributions, uncorrelated against independent, the multivariate normal and the squared Mahalanobis distance,
   colouring), LM18 (random generation and Monte Carlo error); scan `src/lm*.md` for `[[LM13]]`
   … `[[LM18]]` and honour each.
2. **Capability check.** List every exhibit, widget, dataset and Python package the briefs need; check each against
   `src/assets/book.js`, `build/qa/`, `data/` and `pyproject.toml`; send the owner one list of what is missing (site
   code, data pipeline, new packages) and build what he approves before any writer starts.
3. Data: fetch through the API, check every new series as PITFALLS §3 says, and register it in the manifest.
4. Anchors (`plans/vol-3-anchors.md`): every number the briefs quote, with its definition, recomputed by independent
   code; facts checked on official sources (`project/SOURCES.md`).
5. Lab data: `data/make_lab_data.py` writes each lab's files, and the briefs name them.
6. A fresh check of the whole of Stage 1, then commit and push.

**Stage 2, writing.** One writer per module on its own worktree branch (`vol3/lmNN`), with AUTHORING (§1, §6),
PITFALLS and the brief up front. First drafts stay under 5,500 words of prose; numbers scripts assert from the start
that every printed value appears in the text and follows from the printed inputs (a printed string with LaTeX is a
raw string: `"\times"` holds a tab). Writers run `style.py`, the build, `overflow.py` and `display_scroll.py` at
400 px, `print_width.py`, `pdf_scale.py` and `check_terms.py` before handing back, and scan each 中文導讀 box for terms
without their English at first use (the most frequent minor finding in Volume II). In a worktree, `ty` needs
`--python` pointing at the main checkout's `.venv`.

**Stage 3, review.** Per module, in parallel: the independent reviewer (`reviews/REVIEW_PROMPT.md`), the blind solver
(K) and the number auditor (A), plus one cross-module check (X) for the volume; one consolidated list with the
editor's decisions → writer → verifier → closing check with a fresh adversarial second check of every new item → the
editor's fixes → a fresh check.

**Stage 4, publishing.** `status: published`, the edition note, the README status table, prereq and leads consistent
both ways (earlier modules gain leads to the new ones), `./build.sh --pdf`, and on every page: `overflow.py` at
400 px, `print_width.py`, no dead links, and `git grep --untracked -nE "uv pip install|python3 |bundled|source
\.venv|import requests" -- src labs build data` finds nothing.

## Optional

- Refresh the private claude.ai artifact preview (`dist/artifact/`, needs a Claude session with the artifact tool);
  update the project progress note on claude.ai.
- LM6's Solution with "Stage 1: $D_1,\dots,D_5=11.20,\ 12.544,…$" is one unbreakable inline formula that overflows a
  320 px screen (the gate is 400 px); split it at the commas, then a fresh check.
- Volume I has 92 display formulas that scroll inside their own box at 400 px (`build/qa/display_scroll.py`; LM1–LM7:
  8, 15, 14, 10, 19, 9, 17). AUTHORING §10 item 8 applies from Volume II; break the worst with `aligned` if time allows.
- `uv run ruff check data` reports I001 in `data/build_series.py` and `data/check_chunk.py` and B023 in
  `build_series.py` (a lambda that reads the loop's `divd`; it runs inside the same iteration, so the result is
  right). Tidy them when those files next change.
