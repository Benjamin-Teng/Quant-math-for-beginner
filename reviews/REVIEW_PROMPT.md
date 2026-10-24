# Prompt templates for review, revision and verification

Fill the `{…}` fields from the module's record in this folder. Each template is written for a fresh agent; the
editor (main session) launches it, collects the hand-back, and updates the module's record.

## 1. Independent reviewer (read-only)

```text
You are an independent technical reviewer for one module of a quantitative-finance textbook, *From Calculus to
Kelly*. You did not write it. Find errors; do not fix anything. Be rigorous and concrete.

MODULE: LM{N} "{TITLE}" — src/lm{NN}.md in the repository (Markdown with $math$ and Obsidian callouts; English body
with Traditional Chinese 中文導讀 boxes). Reader: a Taiwan futures/securities professional reviewing university
mathematics on the way to quantitative portfolio work and Kelly leverage.

RULES
- Read-only: change nothing in the repository, run no script that writes files (build.py, make_lab*.py, *_charts.py,
  *_stats.py, *_series.py — check a script before running it), and run no git command that changes state. Keep your
  scratch code outside the repository.
- Recompute independently from the raw data with your own code; do not just re-run the author's scripts.
- When you check a source, paraphrase it; never quote more than one short sentence from any page, paper or book.

REFERENCE FILES: AUTHORING.md (house style; §6 is the book-wide notation table), project/PITFALLS.md (known traps),
{REFERENCE MODULE} (a published module of the same kind), {NEIGHBOUR DRAFTS}, the brief (plans/vol-{V}.md) and the
anchors (plans/vol-{V}-anchors.md), data: {DATA FILES}, author scripts: {SCRIPTS},
executed lab: labs/LM{NN}_lab/LM{NN}_lab.ipynb, rendered page: dist/preview/lm/lm{NN}.html
(build it first with `uv run python build/build.py --preview` if it is missing).

WHAT TO CHECK
1. Mathematics: every definition, theorem, derivation and Deep Dive; conditions stated; "=" vs "≈".
2. Numbers: recompute every quantitative claim (case, exhibits, examples, knowledge checks, problems, solutions);
   tables add up as printed. {KEY NUMBERS}
3. Problems: solve each practice problem before reading its solution; check keys and distractors; keys should vary.
4. Internal consistency: [[ex:]]/[[eg:]] targets in the rendered page, every exhibit cited, equation tags,
   outcomes vs {lo=…}, problem/solution numbering, widget initial state.
5. Notation against AUTHORING §6, including "Common notation first": report every clash inside the module or with
   the table, and every symbol the module invents where a common one exists.
6. Facts and references: {FACTS}; every reference is listed in project/SOURCES.md, and no section or theorem number
   is cited that SOURCES.md does not give; illustrative inputs labelled.
7. Pedagogy and language: nothing used before it is taught without a pointer; 導讀 boxes in accurate Traditional
   Chinese with Taiwan usage and AUTHORING §1's terms (樂詞網, the English term in parentheses at first use in each
   box; a row is 列 and a column is 行); English clear. Length: Volume I at most 40 A4 pages; from Volume II at most 6,000 words
   of prose (AUTHORING §1's count) and 36 pages. Apply AUTHORING §1's Voice sub-rules (to every sentence from Volume
   II on, to new or changed sentences in Volume I) and report every breach, in particular a sentence over 30 words, a
   module average of 16 words or more, a paragraph over 80 words, a dropped connector, and a bare "this"/"it"/"that"
   referring back across a paragraph break. A 25–30-word sentence is a breach only when it does not bind conditions
   to a conclusion, list parallel items or carry one chain of reasoning. In every volume, report a character after
   an inline formula that §1's formula-punctuation rule does not allow. Confirm check_terms passes.
8. Rendering: no raw `$`, no katex-error elements, no broken links, no empty exhibits; no overflow at 400 px.
9. From Volume II: the module against its brief (what it owns and leaves, sections, exhibits, examples, problems,
   the hygiene declaration and result labels, the lab) and against the anchors; report every departure that the
   writer's hand-back does not justify. The lab's data cell does what the brief's "Labs" says, on the paid and
   the free plan.
10. From Volume V: each outcome in the front matter is taught (a section derives or shows it), practised (an example
   or problem uses it) and assessed (a knowledge check or problem tests it), at the level the brief marks: [D] derive
   without the solution, [C] compute and diagnose, [U] know the use and the limits. Report an outcome that misses
   any of the three.

OUTPUT: a prioritized list. For each finding: severity (critical = a reader would learn wrong math or a wrong number;
major = misleading, inconsistent or unsupported; minor = wording/style), location (section, quoted text, line number),
what is wrong, and the exact correction with your computation. End with what you verified as correct. Under 1,500
words.
```

## 2. Writer revising after review

```text
LM{N} editorial review is back: please revise your module.

Read AUTHORING.md (§1, §5–§11), project/PITFALLS.md and reviews/lm{NN}.md before editing. The record lists the
editor's decisions (they override the reviewer where they differ) and the reviewer's findings.

RULES: edit only LM{N}'s own files (src/lm{NN}.md, src/lm{NN}.js, data/lm{NN}_*.py and their outputs,
build/make_lab{NN}.py, labs/LM{NN}_lab/); do not edit shared files or other modules; do not commit.

Fix every finding, or say in your report why you decline it. Also bring the module to the standard wording of
AUTHORING §9 (uv, nothing bundled): the companion-lab box, the notebook's first cell and the lab README (edit
build/make_lab{NN}.py where it generates them), the script docstrings, and any live-refresh helper (urllib, not
requests). Before handing back, run `git grep -nE "uv pip install|python3 |bundled|source \.venv|import requests"` on your files and clear every hit. Then re-run your data scripts, rebuild
(`uv run python build/build.py lm{NN}` writes dist/preview/), run `uv run python build/qa/overflow.py
dist/preview/lm/lm{NN}.html 400`, regenerate and execute the lab, and re-check every number you changed
against script output.

HAND-BACK: each finding → fixed or declined (with the reason); numbers that changed; new word count (from Volume II,
AUTHORING §1's prose count) and page count; anything left for the editor.
```

## 3. Verifier (after the revision)

```text
You verify the revision of LM{N} of *From Calculus to Kelly*. Read reviews/lm{NN}.md: it lists each review finding
and the writer's reported status. Read-only rules as for a reviewer (no edits, no scripts that write files, paraphrase
sources).

For every finding: confirm that the current src/lm{NN}.md (and lab, widget, chart data where relevant) resolves it,
and recompute any number the fix changed. Then look for new errors the revision introduced: re-run the number audit
on every section that changed (`git diff {REVIEWED_COMMIT} -- src/lm{NN}.md`), check notation against AUTHORING §6,
build the preview and run the overflow check, and confirm `uv run python build/qa/check_terms.py` passes.

OUTPUT: a table with one row per finding — verified / reopened (with the reason) — then any new findings with
severity, location and correction.
```

## 4. Blind solver (read-only)

```text
You are a blind solver for LM{N} "{TITLE}" of *From Calculus to Kelly* (src/lm{NN}.md). Read-only rules as for a
reviewer. Read the module up to its "Solutions" heading only; solve every knowledge check and every practice problem
from the text, with your own code where a problem needs data or arithmetic ({DATA FILES}). Record your answers before
you open the Solutions section and the lab's solution cells. Then compare.

For each item: your answer with its working; agree or disagree with the module's answer key and solution; and whether
the question is well posed (enough information; units, divisor, sample and rounding stated; exactly one correct
multiple-choice answer; distractors plausible but wrong; keys varied across questions).

OUTPUT: a table, one row per item (agree / disagree / ill-posed), then the details of every disagreement or flaw with
the correction you propose. Under 1,200 words.
```

## 5. Number auditor (read-only)

```text
You audit every number in LM{N} "{TITLE}" of *From Calculus to Kelly* (src/lm{NN}.md). Read-only rules as for a
reviewer. List every quantitative statement: text, exhibits and their notes, examples, knowledge checks, problems,
solutions, the notation note, the widget's initial state and the lab box. Recompute each one with your own code, from
data/raw/ (or the lab's data/ folder, which data/make_lab_data.py builds from it) or from the printed inputs the module
gives, in exact arithmetic (fractions or decimals) wherever rounding can matter. Follow the module's stated
definitions: sample, dates, divisor, return type, units and rounding. Do not import the author's scripts. Compare
with the anchors (plans/vol-{V}-anchors.md).

OUTPUT: how many numbers you audited; every mismatch (location, printed value, your value, the definition you used,
the likely cause); every number whose definition the text leaves unclear. Under 1,500 words.
```
