# TODO — handoff (2026-10-11)

> 給接手的 Claude Code：先讀 `CLAUDE.md`，再依下列順序執行。每完成一項就 commit 並直接 push 到 `main`，並用繁體中文向 Benjamin 回報。

## Where things stand

- `main` is pushed. The site (`docs/`) has edition 0.1: roadmap, contents and the published module LM3. Since the
  handoff of 2026-10-10: the raw data were rebuilt on the owner's computer and verified byte for byte (`aab55c4`);
  short date axes get month ticks (`6ddde98`); the Python environment is uv-managed (`38131a2`: `uv sync`, then
  `uv run python …`); the round-1 review results and the editor's notation decisions are recorded (`b4b8cf6`,
  `bc3db65`).
- Reviews and verifications use fresh Opus subagents, never Codex (the owner's instruction, 2026-10-10). The editor
  (main session) recomputes every major finding before accepting it and must not pass agent claims through unchecked.
- **Volume I is in revision round 2.** The work happens on local branches `rev/lm01` … `rev/lm07` in the owner's
  repository (not pushed), one per module; each round is committed on its branch. A module is squash-merged into
  `main` only after it closes (below). Each module's record in [`reviews/`](reviews/README.md) lists every finding,
  its status and the editor's decisions.
- The per-module cycle: writer → fresh verifier → the editor's gates (a blind solver answers every knowledge check,
  example and problem from a copy with all answers removed, a fresh agent checks the keys against it, and a full
  audit recomputes every number from `data/raw/`) → writer → verifier → closed.

| Module | Round 1 | Gates | Round 2 (2026-10-11) |
|:--|:--|:--|:--|
| LM1 | 21 fixes verified | 31 questions, 628 claims: V1–V5, K1–K10, A1–A14 | writer + verifier running |
| LM2 | 19 fixes verified | 33 questions, 503 claims: V1–V8, K1–K7, A1–A10 | writer + verifier running |
| LM3 | published in 0.1 | blind solve and audit running | then a pass for its gate findings and the items in task 4 |
| LM4 | 24 fixes, 23 verified (12 reopened) | 28 questions, 656 claims: V1–V5, K1–K6, A1–A11 | writer + verifier running |
| LM5 | review: 21 findings (5 major) | after round 1 | round-1 writer + verifier running |
| LM6 | 29 fixes verified | 28 questions, 753 claims: V1–V10, K1–K8, A1–A14 | writer + verifier running |
| LM7 | 23 fixes, 22 verified (1 reopened) | 27 questions, 695 claims: V1–V5, K1–K9, A1–A15 | writer + verifier running |

## Owner action (not for Claude Code)

- Deferred by the owner (2026-10-10): ask GitHub Support (<https://support.github.com/request>, "Remove sensitive
  data") to remove cached views and pull-request references for commits purged on 2026-10-10 because they contained
  raw FinMind data: PR #1 head `e3ed88b`, and the old `main` commits `cfc45f0`, `a9de9cf`, `44d199c`, `8ec5034`,
  `f959c26`, `49b0748`, `5b56679`.

## Tasks, in order

1. **Close each module.** A module closes when every finding in its record is verified fixed or declined with a reason
   the verifier accepted; the gates have run on its current text (rerun the blind solve and the audit on any module
   whose round changed many numbers); `ruff` and `ty` are clean on its scripts; its lab executes from a clean kernel;
   it builds without KaTeX errors and overflow at 400 px; and it is within 40 A4 pages and 11,000 words. Reopened or new
   findings go back to a writer (`reviews/REVIEW_PROMPT.md` §2) and a fresh verifier (§3). Squash-merge the branch
   into `main`, update the record's statuses, push.
2. **LM5:** after its round-1 revision is verified, run the gates on it, then round 2 as above.
3. **LM3:** after its gates, a writer pass for the gate findings plus the task-4 items for LM3, then verification.
   LM3 is published, so build it with `uv run python build/build.py --preview` (building it alone writes `docs/`).
4. **Cross-module pass** (editor): every Volume I module against AUTHORING §6 (including the rules added on
   2026-10-10/11); "about 243" wording (A = 243.1 for the aligned sample; TWSE 243.8); prereq and leads consistent
   across front matter, no cycles (LM3's leads add 5); every `[[LMn]]` link resolves; LM7 cites LM4's envelope theorem
   as (4.16): check it after LM4 closes; Stewart cited as Stewart, Clegg and Watson (2021) everywhere
   (`project/SOURCES.md`); the site's notation table (`build/build_index.py`) matches §6; LM3's lab and companion box
   use the AUTHORING §9 wording; `uv run python build/qa/check_terms.py`.
5. **Publish Volume I** (AUTHORING §11): add `status: published` to LM1, LM2, LM4–LM7 in `src/syllabus.yaml`; add an
   edition note ("0.2", date, "Volume I complete: LM1–LM7 with labs"); update the status table in `README.md` and
   `reviews/README.md`; run `./build.sh --pdf` (needs `uv run playwright install chromium`); check every page at 400 px
   with `build/qa/overflow.py`, look at light and dark screenshots (`build/qa/shoot.py`), and confirm no KaTeX errors
   and no dead links in `docs/`; confirm that
   `git grep -nE "uv pip install|python3 |bundled|source \.venv|import requests" --untracked -- src labs build data`
   finds nothing; commit `src/`, `data/`, `labs/` and `docs/` together and push to `main`.
6. **Report to Benjamin** (in Traditional Chinese): a table with, for each chapter, the findings by severity
   (critical / major / minor) from the review, the verifications and the gates, how many were fixed, and the reason
   for each one not fixed. Source: `reviews/README.md` and the module records — update them first.
7. **Optional:** refresh the private claude.ai artifact preview (needs a Claude session with the artifact tool);
   update the project progress note on claude.ai.

## Then: the remaining volumes

Follow [`plans/ROADMAP.md`](plans/ROADMAP.md): batch 1 is Volumes II and III (LM8–LM18), then IV + V, VI + VII,
VIII and IX. For each batch, write the briefs (`plans/vol-N.md`, same format as `plans/vol-1.md`), collect and verify
the data (historical data from FinMind only), give writers AUTHORING §6 and `project/PITFALLS.md` up front, then
write → review → revise → verify → gates → publish as above, bumping the edition. Ask the owner about the open
decisions listed at the end of the roadmap before the batch that needs them.
