# TODO — handoff (2026-10-25)

> 給接手的 Claude Code：先讀 `CLAUDE.md`，再依下列順序執行。每完成一項就 commit 並直接 push 到 `main`，並用繁體中文向 Benjamin 回報。

課綱建議見 [plans/curriculum-guidance.md](plans/curriculum-guidance.md)（2026-10-21）：保留現有卷序，補強跨卷能力驗收與決策整合。
它是建議，不是規範；每卷 brief 的共同決策記錄採用、調整或暫不採用的理由（編輯決定）。

## Where things stand

- **Volumes I–IV are published (edition 0.5, 2026-10-20).** LM19–LM26 joined the site with A4 PDFs and executed
  labs; their record is under "Volume IV (edition 0.5)" below. `README.md` was refreshed and `README.zh-TW.md` added
  on 2026-10-23 (`d0ebe25`).
- **Volume III (edition 0.4, 2026-10-18).** LM13–LM18 joined the site with A4 PDFs and executed labs. Volume III's
  record, in order:
  - Stage 1: TR23 (the TAIEX total-return index from 2003, `data/vol3_series.py`, checked against the price index on
    every date); the owner-approved chart kit (`step`, bands, `quiet`, `dash`, `x.tfmt`, `n6`/`sci`/`sig`,
    `Book.controls`/`Book.rng`/`Book.dist`, tested by `build/qa/test_bookjs_dist.py`); AUTHORING §6's Probability
    table and §8's simulation rule (`default_rng([e, 20261011])`); `plans/vol-3.md` and `plans/vol-3-anchors.md`
    (458 anchors, recomputed independently twice); SOURCES and 樂詞網 (分布 from Volume III).
  - Stage 2: six writers in place in the main checkout, each on its own files (a worktree lacks the git-ignored
    `data/raw/`, `data/processed/` and `build/node_modules/`, and linking them risks deleting the originals).
  - Stage 3: round 1 (reviewer, blind solver, number auditor, cross-module check; 192 items, 25 major after an
    adversarial re-check, none critical); revisions 1 and 2, each verified by fresh agents; a closing check (52
    module and 9 volume items, one major: LM16's multivariate normal for a singular Σ, now cited to Durrett §3.10)
    with a fresh adversarial second check of every item; a fresh final check. Records: `reviews/lm13.md` … `lm18.md`,
    `reviews/vol3_cross.md`, `reviews/README.md`.
  - Stage 4: Volumes I–II gained leads to the Volume III modules that cite them; LM5 links random variables to LM13
    and writes 分布; Getting Started states the seed rule; the Research hygiene page defines the model,
    hypothetical and constructed labels.
- **Volume I was published in edition 0.2 (2026-10-11) and Volume II in edition 0.3 (2026-10-17).** LM1–LM12 are on
  the site (`docs/`, <https://quantmath.fintools.tw>) with A4 PDFs and executed labs. Volume II went through the four
  stages below: the briefs, data, anchors and tooling; five writers; a review round (reviewer, blind solver, number
  auditor and a cross-module check: 180 items, 2 critical (one defect, LM11 finding 1 = K1), 29 major), two
  revisions, a verification and a closing check; then publication. Each `reviews/lmNN.md` holds the findings,
  decisions and rounds; `reviews/README.md` lists the findings left unfixed and why. `project/PITFALLS.md` holds the
  lessons.
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
  `src/`, `data/` and `labs/` (AUTHORING §11). Only build output belongs in `docs/`. GitHub Pages serves every
  committed file there as is (`docs/.nojekyll`). The build removes only stale pages and PDFs (`remove_unpublished()`
  in `build/build.py`), so a hand-written file of another kind, such as a `.md`, stays public.
- **PDF links** (owner-approved, 2026-10-17): `build/render_pdf.py` sends a link to another page of the book to the
  live site (the domain in `docs/CNAME`) and keeps same-page anchors as internal PDF links; before, Chromium printed
  them as `file:///` paths on the author's disk. After `./build.sh --pdf`, `grep -ac 'file:///' docs/pdf/*.pdf`
  gives 0 for every file.
- **Mobile Contents drawer and Start or Resume reading** (owner-requested, `3c3f4c5`): checked by the owner on
  2026-10-19. The reading record (`ftck-last-read`, localStorage) keeps its rule: opening a module records it.
- The brief and anchors keep the plan and the corrected facts (preface of `plans/vol-2.md`); values and wording that
  a revision changes in a module are not copied back. Four of the closing check's six refuted items (LM8 C1, CX1–CX3) rest on this rule; reviews/README.md gives the
  reasons for CX4 and CX5.

## Batch 4: Volumes V and VI (edition 0.6) — in progress

The owner (2026-10-24): run batch 4 from Stage 1 to publication, as before. Only technical questions go to him. The
textbook content follows the plan and is the editor's call, and the editor reviews it independently before anything
is published. The decisions `CLAUDE.md` reserves to him still go to him (for example the intellectual-property scope,
and changes to code, site and repository). Volume V is LM27–LM31 (Portfolio Optimization), Volume VI is
LM32–LM35 (Measuring True Risk and Return); the two can be written in parallel (ROADMAP). The Volume V packages
`cvxpy` and `scikit-learn` are approved (ROADMAP, "Decided by the owner").

- [ ] Stage 1: survey, spines and shared decisions (`plans/vol-5.md`, `plans/vol-6.md`), capability check (owner),
  data, briefs and anchors (`plans/vol-5-anchors.md`, `plans/vol-6-anchors.md`), a fresh check of the whole.
  - [x] Survey (eight surveyors and a critic, 2026-10-24); spines and shared decisions in `plans/vol-5.md`, revised
    after a fresh adversarial check; `ROADMAP.md` and `reviews/REVIEW_PROMPT.md` (item 10) amended.
  - [x] Capability check: every item approved by the owner on 2026-10-24 (`plans/vol-5.md`, ROADMAP "Decided by
    the owner"). Built and reviewed by fresh agents: cvxpy and scikit-learn (`40e1876`); `fetch_finmind.py
    --adjusted` (LM3's QQQ defect; re-reviewed after a failed first design); the E5 and checkpoint raw files
    (`data/raw/vol5/`); `data/vol5_series.py` and `data/vol5_rules.py` (independently recomputed: every target,
    wealth path and criterion); the chart kit's stacked bars, curves and colour check (published pages pixel- and
    byte-identical); AUTHORING §6 (portfolio notation) and §7.
  - [x] US proxies for LM35 (capability B5) and delisted ETFs for LM34 (B4), registered (`6b02e71`).
  - [x] Briefs LM27–LM35 and their anchor scripts (`data/vol5_anchors_lm27.py` … `data/vol6_anchors_lm35.py`,
    assembled into `plans/vol-5.md`, `plans/vol-6.md` and the two anchors files): drafted; recomputed independently
    (all 423 anchors, then the 185 a revision changed, then each later change); two cross-module checks; revised
    three times plus a last pass, each verified by a fresh agent. Every decision is in `plans/vol-5.md` ("Editor's
    decisions on the briefs" and the sections on the first, second and third revisions).
  - [x] Sources: two source hunts read every cited original that could be had (Kupiec 1995 and Christoffersen 1998 in
    their working versions; TPEx's rules for the TPEx-listed 00679B and 00720B); SOURCES gained the Volume V and VI
    papers, data, Python, Taiwan facts and 樂詞網 sections (each fragment verified by fresh agents).
  - [ ] **Next (the owner paused the work here for usage on 2026-10-25):** a fresh check of the whole of Stage 1
    (the nine briefs and anchors as assembled, the decisions, SOURCES), then the editor's fixes. Give it the minor
    items the last verifiers left (reports in the session scratch, summarized here):
    - LM28: the closed list's "LM30's E2 alone" (LM29's widget and LM31's E1 also print A28-06 to two decimals);
      A28-06's Printed-as should record those two; LM31 cites A28-06 where its anchors name A31-07.
    - LM29: the cost-model pointer reads as if the articles fixed the rate (they let brokers set it, with notice above
      1.425‰); the Used list lacks the widget's $\sigma_i$ and $\rho$.
    - LM30: the anchors Status omits A30-04's Printed-as change; X3's note "years of sessions are sessions over $A$"
      should read "years are sessions over $A$".
    - LM31: the Pitfalls line counts credit among Harvey et al.'s 50 futures and forwards (their 50 exclude credit).
    - LM32: the hygiene note's first sentence has 31 words.
    - LM33: E2's "the rules' own paths keep 1.5%" can be read as R8 borrowing at 1.5% (it borrows at 3.5%).
    - LM34: A34-17's half-Kelly 23.56% does not follow from the printed root 4.14 (23.57%).
    - LM35: the suspension wording against the SOURCES rows; "under TWSE's current rules" for the hypothetical
      replays, which hold 00679B's proxy (TPEx); the read dates of the short names.
  - [ ] Before Stage 2's labs: `data/make_lab_data.py` writes what the shared "Labs" decision lists (both E5 frames,
    the rules' targets and wealth paths, LM34's grid, the T5S days, the checkpoint and proxy frames).
- [ ] Stage 2: drafts of LM27–LM35.
- [ ] Stage 3: review rounds, closing check, final check.
- [ ] Stage 4: publish edition 0.6.

## How a batch runs

Follow [`plans/ROADMAP.md`](plans/ROADMAP.md): batches 0–3 (Volumes I–IV) are published; batch 4 is Volumes V and
VI, then VII, VIII and IX. Each batch repeats Stages 1–4 and bumps the edition. Ask the owner about code, site,
repository and his standing rules, and about the open decisions at the end of the roadmap before the batch that needs
them; content is the editor's call.

**Stage 1, before any writer starts**, as Volumes III and IV did (`plans/vol-4.md` is the model):

1. A spine per module in `plans/vol-N.md` within ROADMAP's module boundaries, with shared decisions (samples, return
   types, notation that follows AUTHORING §6, ownership of each statistic, which recommendations of
   `plans/curriculum-guidance.md` apply). Scan `src/lm*.md`, `src/pages/*.md` and `build/make_lab*.py` for the
   batch's forward links (`[[LM27]]` … `[[LM35]]` for batch 4, and plain "LM34" mentions in the labs) and honour
   each; take over what earlier briefs leave to the batch.
2. Capability check: list every exhibit, widget, dataset and package the spines need; check each against
   `src/assets/book.js`, `build/qa/`, `data/` and `pyproject.toml`; send the owner one list of what is missing and
   build what he approves before any writer starts, each piece reviewed by a fresh agent (0 differences on the
   published pages).
3. Data through the FinMind API (intraday by a logged script), each new series checked as PITFALLS §3 says (and, for
   a series without a spread column, against an independent series, as `data/vol3_series.py` does), registered in
   the manifest.
4. Briefs drafted from the spines by one agent per module, cross-checked by a fresh agent, decided by the editor and
   revised; anchors (`plans/vol-N-anchors.md`) printed by one script per module and recomputed independently by
   fresh agents from the raw files; facts and references checked on official sources (SOURCES, 樂詞網).
5. Lab data in `data/make_lab_data.py`; the briefs name the files.
6. A fresh check of the whole of Stage 1, then commit and push.

**Stage 2, writing.** One writer per module, launched together, each in place in the main checkout on its own files
only, with AUTHORING, PITFALLS, the shared part of the brief, its own brief and anchors. Each writer starts its
`data/lmNN_numbers.py` from its anchor script and asserts from the first draft that every printed value appears in
the text and follows from the printed inputs (a printed string with LaTeX is a raw string); writes its charts script,
module, widget and lab generator; keeps the first draft under 5,500 words of prose; runs style.py, the build,
overflow.py and display_scroll.py at 400 px, print_width.py, the PDF with pdf_scale.py, check_terms.py, ruff and ty,
and the lab; and asks the editor for shared-file changes (`build.sh`'s `DATA_STEPS`, `data/README.md`). The editor
re-runs every gate on `main` and commits the drafts.

**Stage 3, review.** Per module, in parallel: the independent reviewer (`reviews/REVIEW_PROMPT.md`), the blind solver
(K) and the number auditor (A), plus one cross-module check (X) for the volume; a fresh agent per module merges the
reports and re-checks every major item adversarially; the editor decides and records (`reviews/lmNN.md`, stating
every item and its fix in the record itself, PITFALLS §6) → writers
revise → fresh verifiers and a volume re-check → a second revision if needed → closing check with a fresh adversarial
second check of every new item → closing fixes → a fresh final check.

**Stage 4, publishing.** `status: published`, the edition note, the README status table (`README.md` and
`README.zh-TW.md`), prereq and leads consistent both ways (earlier modules gain leads to the new ones),
`./build.sh --pdf`, and on every page: `overflow.py` at 400 px, `print_width.py`, no dead links,
`grep -ac 'file:///' docs/pdf/*.pdf` gives 0, and
`git grep --untracked -nE "uv pip install|python3 |bundled|source \.venv|import requests" -- src labs build data`
finds nothing.

## Volume IV (edition 0.5) — published

**Status (2026-10-20): Volume IV is published (edition 0.5); Stages 1–4 are complete.** Stage 3's record, in
order, is in `reviews/lm19.md` … `lm26.md` and `reviews/vol4_cross.md`: round 1 (reviewer, blind solver, number
auditor, consolidation with an adversarial re-check, cross-module check X1–X11), revisions 1–3 each verified by fresh
agents (volume re-checks X2 and X3; the editor's cross-module decisions are XB1–XB11), the closing check with an
adversarial second check of every item (three majors, all fixed), the closing fixes, a fresh final check per module
and for the volume (LM21, LM23, LM24 and LM26 not ready, for 8 minor items; X5), and the last fixes, verified (every
module READY TO PUBLISH; front matter consistent, X6). The editor's decisions were each checked by a fresh
agent before the writers applied them. Stage 4 applied `plans/vol-4.md`'s "Stage 4 changes to earlier modules", rebuilt every number, chart, page and PDF with `./build.sh --data --pdf`, and passed a fresh verification (links, leads both ways, rendering, PDFs). The
owner approved (2026-10-19) that a blank line in an exhibit caption starts a new paragraph (`build/build.py`); LM17's
two split captions changed at this publication. Stage 1's material is in
[`plans/vol-4.md`](plans/vol-4.md) (shared decisions, the capability check and the owner's answers, the editor's
decisions on the survey and the drafts, the eight briefs) and [`plans/vol-4-anchors.md`](plans/vol-4-anchors.md) (488
anchors, printed by `data/vol4_anchors_lm19.py` … `lm26.py`). The record, in order:

- Survey of the published book's promises to LM19–LM26, the notation, the data, the packages, the sources and the
  chart kit; spines; a fresh adversarial check of the spines.
- Capability check: the owner approved A (statsmodels 0.15.0 and arch 8.0.0; smoke-tested in an empty environment,
  every tracked output reproduced), B (TX23 by `data/vol4_series.py`; T5S, the 5-second TAIEX 2005–2026, by
  `data/fetch_intraday.py` with its own manifest; `data/vol4_rv.py`), B′ (per-day realized variances committed in
  `data/derived/vol4_rv.csv`), C (log $x$, `x.values`, scatter `tickLabels` and bands, chart and page size checks) and
  E (TX 1-minute bars for 2025); not D. Each piece was built, reviewed by a fresh agent, fixed and re-reviewed
  (published pages pixel- and byte-identical). The download: 5,351 T5S days and 297 TX requests (243 trading days and 54 night-session tails), every day checked.
- Briefs: seven drafters (LM19–LM25), a cross-check (X1–X40), an independent recomputation of the drafts' 415 anchors (all
  reproduced), the editor's decisions, seven revisers (the rows they added or changed recomputed independently
  afterwards); LM26 drafted on the full download; a fresh check of the whole
  (no critical finding; LM26's 66 anchors recomputed, all reproduced) and its fixes, verified by a fresh agent.
- Shared files: AUTHORING §6 (the Volume IV statistics table and amendments), §7–§9; PITFALLS §3 (futures spreads
  against settlement; an intraday index opens at the previous close); SOURCES (Volume IV: papers, Python facts, data
  sets, FinMind's terms, 樂詞網, Taiwan facts); ROADMAP's owner decisions; `data/make_lab_data.py` (LM19–LM26 entries).
- Stage 2's shared-file changes were made by the editor: `build.sh` `DATA_STEPS` for `data/lm19_numbers.py` …
  `lm26_charts.py`, `data/README.md` rows, and the Stage 4 list in `plans/vol-4.md`.

## After the whole course (owner, 2026-10-24)

These layout details wait until the whole course is published (owner, 2026-10-24); then they are done together:

- Site code: the front page's install block (`build/build_index.py`, the `git clone … cd …` line) is 755 px wide in
  print against the 680 px text width (`build/qa/print_width.py docs/index.html`). It was so in 0.2; on screen it
  scrolls inside its box, and the front page has no PDF.
- `book.js`: two minor items the last review left (each tested in a scratch copy): relock directly in the drawer's
  ResizeObserver callback (one frame of the wrong page behind the backdrop on a reflow), and add
  `main [data-widget] > *` to the drawer's scroll anchors (a widget filling the reading line can miss the place by up
  to a window).
- `book.js`: two options the Volume II writers asked for (bar-label text for LM8's `angles`, ellipses above points
  for LM11's Exhibit 3); the significant-figure codes came with the Volume III kit. The modules work without them.
- LM6's Solution with "Stage 1: $D_1,\dots,D_5=11.20,\ 12.544,…$" is one unbreakable inline formula that overflows a
  320 px screen (the gate is 400 px); split it at the commas, then a fresh check.
- Volume I has 92 display formulas that scroll inside their own box at 400 px (`build/qa/display_scroll.py`; LM1–LM7:
  8, 15, 14, 10, 19, 9, 17). AUTHORING §10 item 8 applies from Volume II; break the worst with `aligned`.

## Optional

- Refresh the private claude.ai artifact preview (`dist/artifact/`, needs a Claude session with the artifact tool);
  update the project progress note on claude.ai.
- `uv run ruff check data` reports I001 in `data/build_series.py` and `data/check_chunk.py` and B023 in
  `build_series.py` (a lambda that reads the loop's `divd`; it runs inside the same iteration, so the result is
  right). Tidy them when those files next change.
