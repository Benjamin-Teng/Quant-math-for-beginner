# TODO — handoff (2026-10-10)

> 給接手的 Claude Code：先讀 `CLAUDE.md`，再依下列順序執行。每完成一項就 commit 並直接 push 到 `main`，並用繁體中文向 Benjamin 回報。

## Where things stand

- `main` is pushed and clean. The site (`docs/`) has edition 0.1: roadmap, contents and the published module LM3.
- Volume I drafts LM1, LM2, LM4, LM5, LM6, LM7 are committed with executed labs but are **not published**
  (`status: published` is set only for LM3 in `src/syllabus.yaml`). Preview them with `uv run python build/build.py --preview`.
- Independent reviews: LM1, LM2, LM4, LM6, LM7 done (116 findings, 6 critical); LM5 still to review.
  LM1 and LM2 are revised (writer-reported, unverified). LM4, LM6, LM7 revisions have not started.
  Records with every finding and the editor's decisions: [`reviews/`](reviews/README.md).

## Owner action (not for Claude Code)

- Ask GitHub Support (<https://support.github.com/request>, "Remove sensitive data") to remove cached views and
  pull-request references for commits purged on 2026-10-10 because they contained raw FinMind data: PR #1 head
  `e3ed88b`, and the old `main` commits `cfc45f0`, `a9de9cf`, `44d199c`, `8ec5034`, `f959c26`, `49b0748`, `5b56679`.
  They are no longer in any branch but GitHub still serves them by SHA.

## Tasks, in order

0. ~~Rebuild the raw data on the owner's computer.~~ **Done 2026-10-10** on the owner's Windows computer: a clean
   checkout fetched all 34 manifest files from FinMind and matched each byte for byte, and the 28 lab data files built
   from them match. One fix: the `00679B_dividends.csv` filter (FinMind labels that ETF's cash dividends `除息`, not
   `息`); `fetch_finmind.py --add` now test-fetches before registering. Never commit `data/raw/` or `labs/*/data/`.
   **uv (2026-10-11):** the Python environment is now uv-managed (`pyproject.toml`, `uv.lock`, Python 3.13; run
   `uv sync`, then `uv run python …`). Shared files are converted. Every module gets a writer pass in round 2, reopened findings or not,
   and that pass also switches its companion-lab box, notebook Environment cell, lab README, script docstrings and any
   live-refresh helper to the standard wording of AUTHORING §9 (LM3: the editor, in the cross-module pass); until then
   they still show the old `uv pip install` setup.
1. **Verify LM1 and LM2.** Run the verifier template (`reviews/REVIEW_PROMPT.md` §3) on each, with the reviewed commit
   `390c790` (the 2026-10-10 history rewrite renamed every commit; `44d199c` is the same tree). Update the status column in `reviews/lm01.md` and `reviews/lm02.md`. Reopened findings go back to a
   writer (template §2), then verify again.
2. **Revise LM4** from `reviews/lm04.md`: the critical skewness error, the eight major findings, the notation renaming
   (binary bet gain b / loss a, fractional Kelly c, Π, r_f, y; widget labels in `src/lm04.js`), the exact 95% band
   2.7×–7.6×, and the length cuts (PDF ≤ 40 pages). Then verify.
3. **Revise LM6** from `reviews/lm06.md`: the 40.34-point conversion, the bisection wording, the extreme-day case
   (multi-day figure), the 30 June pitfall, thin back months with volumes, the dividend-term labelling, the notation
   renaming, front-matter prereq/leads, and trimming to ≤ 11,000 words. Then verify.
4. **Revise LM7** from `reviews/lm07.md`: net vs gross exposure cap and ν₂, the two missing KKT rows (also in the lab),
   the quadratic budget constraint, the 202 bp attribution, the notation renaming (h objective, ψ constraints, J(c),
   r_f/A with A defined, w^tan, det H), the covariance derivations, the lab reading only its own data, and trimming to
   ≤ 11,000 words. Then verify.
5. **Review LM5** with the reviewer template (§1) and the inputs in `reviews/lm05.md`; record the findings there; revise
   (include the known items listed in the record); verify.
6. **Cross-module pass** (editor): every Volume I module against AUTHORING §6; "about 243" wording in LM3 l.259 and LM5
   (A = 243.1 for the aligned sample; TWSE 243.8); LM5's stale remark that r(t) is used "because φ is taken"; prereq
   and leads consistent across front matter (no cycles); every `[[LMn]]` link resolves in the preview; run
   `uv run python build/qa/check_terms.py`; LM3's lab, companion box and front-matter leads (add 5) get the
   AUTHORING §9 wording and the LM5 record's finding 19.
7. **Publish Volume I** (AUTHORING §11): add `status: published` to LM1, LM2, LM4–LM7 in `src/syllabus.yaml`; add an
   edition note ("0.2", date, "Volume I complete: LM1–LM7 with labs"); update the status table in `README.md`; run
   `./build.sh --pdf` (needs `uv run playwright install chromium`); check every page at 400 px with `build/qa/overflow.py`,
   look at light and dark screenshots (`build/qa/shoot.py`), and confirm no KaTeX errors and no dead links in `docs/`;
   confirm that `git grep -nE "uv pip install|python3 |bundled|source \.venv|import requests" --untracked -- src labs build data`
   finds nothing; commit `src/`, `data/`, `labs/` and `docs/` together and push to `main`.
8. **Report to Benjamin** (in Traditional Chinese): a table with, for each chapter, the review findings by severity
   (critical / major / minor), how many were fixed, and the reason for each one not fixed. Source: `reviews/README.md`
   and the module records — update them first.
9. **Optional:** ~~sub-year date ticks and `x.tickLabels` in `Book.lineChart`~~ (done 2026-10-11, `6ddde98`); refresh the private claude.ai artifact preview (needs a Claude session with the artifact tool);
   update the project progress note on claude.ai.

## Then: the remaining volumes

Follow [`plans/ROADMAP.md`](plans/ROADMAP.md): batch 1 is Volumes II and III (LM8–LM18), then IV + V, VI + VII,
VIII and IX. For each batch, write the briefs (`plans/vol-N.md`, same format as `plans/vol-1.md`), collect and verify
the data (historical data from FinMind only), give writers AUTHORING §6 and `project/PITFALLS.md` up front, then
write → review → revise → verify → publish as above, bumping the edition. Ask the owner about the open decisions
listed at the end of the roadmap before the batch that needs them.
