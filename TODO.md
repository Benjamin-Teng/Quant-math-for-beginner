# TODO — handoff (2026-10-18)

> 給接手的 Claude Code：先讀 `CLAUDE.md`，再依下列順序執行。每完成一項就 commit 並直接 push 到 `main`，並用繁體中文向 Benjamin 回報。

## Where things stand

- **Volume III Stage 1 is complete (2026-10-18); Stage 2 (writing) is next.** What Stage 1 produced:
  - Data: TR23, the TAIEX total-return index from 2003-01-02 (`data/raw/vol3/`, registered), built and checked against
    the price index on every date by `data/vol3_series.py`; a fresh review tried 40 alterations of the raw files and
    every bad row stops the script. LM13–LM18 lab files in `data/make_lab_data.py` (LM16: U28 only).
  - Site code, owner-approved 2026-10-18 (ROADMAP, "Decided by the owner"): line-chart `step`, band, `quiet` and
    `dash`; `x.tfmt`; format codes `n6`, `sci0–3`, `sig2–4`; shared `Book.controls`, `Book.rng`, `Book.dist`, tested
    against SciPy by `build/qa/test_bookjs_dist.py`; `build.py` checks bands and log axes. Reviewed twice by fresh
    agents: 0 differences on all 12 published pages. AUTHORING §7 documents them.
  - Rules: AUTHORING §6 gains the Probability table (and amendments for $\lambda$, $B$, $u$, $k$, $\mathcal A$,
    $\eta$, $\zeta$); §8 the simulation rule (`np.random.default_rng([e, 20261011])`, the experiment number first).
  - Plans: `plans/vol-3.md` (shared decisions, capability check, the editor's decisions, Stage 4 changes, six
    briefs) and `plans/vol-3-anchors.md` (458 anchors, printed by `data/vol3_anchors_lm13.py` … `lm18.py`). Each
    brief was drafted from the editor's spine, cross-checked (32 findings), revised, checked by fresh agents who
    recomputed every anchor from the raw files (all reproduced), revised again and verified (no major finding left).
  - Sources: `project/SOURCES.md` gains the Volume III books (with verified theorem and section numbers), papers,
    Python facts, Taiwan facts and the 樂詞網 lookups (245 terms; the book writes 分布 from Volume III).
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
- Optional, `book.js`: two options the Volume II writers asked for (bar-label text for LM8's `angles`, ellipses above
  points for LM11's Exhibit 3); the significant-figure codes came with the Volume III kit. The modules work without
  them.

## Next: Volume III (edition 0.4), Stage 2

Follow [`plans/ROADMAP.md`](plans/ROADMAP.md): batch 2 is Volume III (LM13–LM18), then IV, V + VI, VII, VIII and IX.
Each batch repeats Stages 1–4 and bumps the edition (the owner confirmed the process, 2026-10-11). Ask the owner about
code, site, repository and his standing rules, and about the open decisions at the end of the roadmap before the batch
that needs them; content is the editor's call. Volume III's Stage 1 is done (above); its capability check needs nothing
more from the owner.

**Stage 2 done (2026-10-18).** The six drafts are on `main` (not published): 5,480–5,498 words of prose, 29–36
pages at scale 1.0000, numbers scripts with 271–414 checks each and no anchor drift. The editor re-ran every gate on
`main` (numbers, charts regenerate byte for byte, style FAIL 0, 400 px, displays, print width, PDF scale, terms, ruff,
ty, labs without errors) and added the scripts to `build.sh` and `data/README.md`. The writers worked in place in the
main checkout, each on its own module files only, because a worktree lacks the git-ignored `data/raw/`,
`data/processed/` and `build/node_modules/`, and linking them into a worktree risks deleting the originals when the
worktree is removed. Open from the hand-backs, for Stage 3: LM16 is at the 36-page limit; LM18's attribution of the
1/n bias of an estimated control-variate coefficient to Glasserman (2003) §4.1 is not in SOURCES; LM18's tags run
(18.1)–(18.3), (18.9), (18.4)–(18.8); LM18's Exhibit 6 table scrolls inside its box at 400 px; LM16 cites Blitzstein
and Hwang §3.8 and §7.5 by section; LM14's widget shows σ²/2 = 28.13 where its Exhibit 7 prints 28.125; LM15 plots
130 of 5,849 QQ points because `.chart .pt`'s outline whitens a dense scatter (a `book.css` option for the owner).
Preview PDFs keep `file:///` links (`dist/preview/` has no CNAME); the published PDFs, rendered from `docs/`, do not.

The Stage 2 instructions, for later volumes: one writer per module, launched together, each with
AUTHORING (§1, §6 with the Probability table, §7, §8's simulation rule), PITFALLS, the shared part of
`plans/vol-3.md` and its own brief, and its anchors section. Each writer:

- copies its anchor script into `data/lmNN_numbers.py` as the starting point and asserts from the first draft that
  every printed value appears in the text and follows from the printed inputs (a printed string with LaTeX is a raw
  string: `"\times"` holds a tab), with LM10's `anchor(label, got, expected)` comparator reporting drift from
  `plans/vol-3-anchors.md`;
- writes `data/lmNN_charts.py`, `src/lmNN.md`, `src/lmNN.js` (with `Book.controls`, `Book.rng`, `Book.dist`) and
  `build/make_labNN.py` (labs write plain "LMnn");
- keeps first drafts under 5,500 words of prose and runs `style.py`, the build, `overflow.py` and `display_scroll.py`
  at 400 px, `print_width.py`, `pdf_scale.py` and `check_terms.py` before handing back, and scans each 中文導讀 box for
  terms without their English at first use; in a worktree, `ty` needs `--python` pointing at the main checkout's
  `.venv`;
- adds its scripts to `build.sh`'s `DATA_STEPS` and the data README table only through the editor (shared files).

**Stage 3, review.** Per module, in parallel: the independent reviewer (`reviews/REVIEW_PROMPT.md`), the blind solver
(K) and the number auditor (A), plus one cross-module check (X) for the volume; one consolidated list with the
editor's decisions → writer → verifier → closing check with a fresh adversarial second check of every new item → the
editor's fixes → a fresh check.

**Stage 4, publishing.** `status: published`, the edition note, the README status table, prereq and leads consistent
both ways (the list in `plans/vol-3.md`, "Stage 4 changes to earlier modules", including LM5's three 分布 strings,
LM5:60's link to LM13 and Getting Started's seed sentence), `./build.sh --pdf`, and on every page: `overflow.py` at
400 px, `print_width.py`, no dead links, `grep -ac 'file:///' docs/pdf/*.pdf` gives 0, and `git grep --untracked -nE
"uv pip install|python3 |bundled|source \.venv|import requests" -- src labs build data` finds nothing.

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
