# TODO — handoff (2026-10-10)

> 給接手的 Claude Code：先讀 `CLAUDE.md`，再依下列順序執行。每完成一項就 commit 並直接 push 到 `main`，並用繁體中文向 Benjamin 回報。

## Where things stand

- `main` is pushed and clean. The site (`docs/`) has edition 0.1: roadmap, contents and the published module LM3.
- Volume I drafts LM1, LM2, LM4, LM5, LM6, LM7 are committed with executed labs but are **not published**
  (`status: published` is set only for LM3 in `src/syllabus.yaml`). Preview them with `python3 build/build.py --preview`.
- Independent reviews: LM1, LM2, LM4, LM6, LM7 done (116 findings, 6 critical); LM5 still to review.
  LM1 and LM2 are revised (writer-reported, unverified). LM4, LM6, LM7 revisions have not started.
  Records with every finding and the editor's decisions: [`reviews/`](reviews/README.md).

## Tasks, in order

0. **Rebuild the raw data on the owner's computer.** Raw FinMind files are no longer in the repo. Run
   `export FINMIND_TOKEN=…; ./build.sh --fetch` once: it downloads every file listed in `data/raw_manifest.json`,
   checks each byte for byte, and builds the labs' `data/` folders. The download code could not be tested from the
   cloud container (no route to FinMind); its parsing was tested against real FinMind rows. Fix any problem before
   task 1, and never commit `data/raw/` or `labs/*/data/`.
1. **Verify LM1 and LM2.** Run the verifier template (`reviews/REVIEW_PROMPT.md` §3) on each, with the reviewed commit
   `44d199c`. Update the status column in `reviews/lm01.md` and `reviews/lm02.md`. Reopened findings go back to a
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
   `python3 build/qa/check_terms.py`.
7. **Publish Volume I** (AUTHORING §11): add `status: published` to LM1, LM2, LM4–LM7 in `src/syllabus.yaml`; add an
   edition note ("0.2", date, "Volume I complete: LM1–LM7 with labs"); update the status table in `README.md`; run
   `./build.sh --pdf` (needs `playwright install chromium`); check every page at 400 px with `build/qa/overflow.py`,
   look at light and dark screenshots (`build/qa/shoot.py`), and confirm no KaTeX errors and no dead links in `docs/`;
   commit `src/`, `data/`, `labs/` and `docs/` together and push to `main`.
8. **Report to Benjamin** (in Traditional Chinese): a table with, for each chapter, the review findings by severity
   (critical / major / minor), how many were fixed, and the reason for each one not fixed. Source: `reviews/README.md`
   and the module records — update them first.
9. **Optional:** add sub-year date ticks to `Book.lineChart` and an `x.tickLabels` option (requested by the LM1 and LM6
   writers); refresh the private claude.ai artifact preview (needs a Claude session with the artifact tool);
   update the project progress note on claude.ai.

## Then: the remaining volumes

Follow [`plans/ROADMAP.md`](plans/ROADMAP.md): batch 1 is Volumes II and III (LM8–LM18), then IV + V, VI + VII,
VIII and IX. For each batch, write the briefs (`plans/vol-N.md`, same format as `plans/vol-1.md`), collect and verify
the data (historical data from FinMind only), give writers AUTHORING §6 and `project/PITFALLS.md` up front, then
write → review → revise → verify → publish as above, bumping the edition. Ask the owner about the open decisions
listed at the end of the roadmap before the batch that needs them.
