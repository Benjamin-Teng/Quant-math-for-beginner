# CLAUDE.md — From Calculus to Kelly

A self-study quantitative-finance textbook (static website + A4 PDFs + Jupyter labs) that runs from first-year
calculus, statistics and linear algebra to Kelly leverage, GBM and Itô's lemma. Owner: Benjamin. MIT License.
An independent personal-study project. `AGENTS.md` lets Codex take over the project by pointing to this file; keep
every project instruction here, not there.

## Read first, in this order

1. [`TODO.md`](TODO.md) — the current work queue and its order; [`plans/ROADMAP.md`](plans/ROADMAP.md) for the volumes after Volume I.
2. [`project/SPEC.md`](project/SPEC.md) — what the owner decided (format, language, rigor, hosting, rules).
3. [`project/PITFALLS.md`](project/PITFALLS.md) — mistakes already made and the rule that prevents each. Do not repeat them.
4. [`AUTHORING.md`](AUTHORING.md) — how a module is written, checked, reviewed and published; §6 is the book-wide notation table.
5. [`reviews/`](reviews/README.md) — review findings and their status per module.
6. [`project/SOURCES.md`](project/SOURCES.md) — where facts and data were checked.

## Owner's standing rules

- Talk to Benjamin in **Traditional Chinese**; the book itself is English with 中文導讀 boxes.
- **Division of responsibility** (owner, 2026-10-11): Benjamin oversees the code architecture, the website and
  repository maintenance; propose changes there and wait for his approval. Every content and editorial decision
  (scope, depth, length, style, notation, examples, cases) is delegated to Claude as the editor: decide on evidence,
  report the reasons, accept his veto. The numbers in `AUTHORING.md` are editorial choices, revisable with evidence;
  the owner's decisions are those `project/SPEC.md` attributes to him.
- **Process is the editor's choice** (owner, 2026-10-11): this is a learning-content project, not a software
  project. No SDD, OpenSpec or other process skill is required; decide per task whether any process helps. The
  default is the project's own cycle: briefs in `plans/`, the queue in `TODO.md`, the gates of AUTHORING §10–§11.
- **Source authenticity comes first** (owner, 2026-10-11): textbooks, papers, official documents, FinMind data and
  Claude's own knowledge are all acceptable sources, but every citation is checked to exist as cited, and no data,
  reference or quotation is ever invented.
- **Commit and push directly to `main`**; no pull requests. `git fetch` and rebase before every push.
- **Infringe no one's intellectual property** (owner, 2026-10-10; clarified 2026-10-11). In particular, never copy or
  adapt a professional-certification curriculum's material (its readings, outcome wording or problems). What an exam
  body publishes publicly may be cited like any source. `build/qa/check_terms.py` must pass (`build.sh` runs it).
- **Historical market data come only from FinMind** (daily and intraday); never Shioaji for history. He has a
  **Sponsor plan** (6,000 calls an hour; minute bars, ticks, final settlement prices…), licensed for non-commercial
  use: never redistribute raw FinMind data, and cite FinMind.
- Never commit third-party course material he shares for reference.
- Publish a module only after an independent review and verified fixes (AUTHORING §11).

## Commands

```bash
uv sync                                           # Python env (.venv) from pyproject.toml + uv.lock; uv add <pkg> to add one
(cd build && npm ci)                              # KaTeX + self-hosted fonts
uv run python build/build.py                      # published site -> docs/
uv run python build/build.py --preview            # every module incl. drafts -> dist/preview/ (git-ignored)
uv run python build/build.py lm04                 # one module (a draft goes to dist/preview/)
./build.sh [--data] [--labs] [--pdf] [--preview]  # full pipeline; --pdf needs `uv run playwright install chromium`
uv run python build/qa/overflow.py dist/preview/lm/lm04.html 400   # horizontal overflow check (path or URL)
uv run python build/qa/check_terms.py             # banned-terms check
uv run python build/qa/print_width.py <html>      # what is wider than the A4 text width in print
uv run python build/qa/pdf_scale.py <pdf>         # fail if Chromium shrank a PDF (its page count would be too low)
uv run python data/check_chunk.py data/raw/<file>.csv  # verify a raw FinMind chunk against its spread column
FINMIND_TOKEN=... uv run python data/fetch_finmind.py  # rebuild data/raw/ (git-ignored) from FinMind; --verify: offline
uv run python data/make_lab_data.py               # build every lab's data/ folder from data/raw/
uv run ruff check <files> && uv run ty check <files>   # Python gates (dev group); markdownlint-cli2 "**/*.md" for docs
```

## Layout

`src/` module sources (`lmNN.md`, `lmNN.js`, `data/*.json`, `assets/`, `syllabus.yaml`) and standalone pages
(`pages/`: Getting Started, Research hygiene) · `build/` builders and QA (`qa/style.py` checks AUTHORING §1) ·
`data/` the raw-data manifest, fetch script and the scripts that compute every number · `labs/` executed notebooks (data built locally) ·
`docs/` the published site (GitHub Pages, `main` `/docs`, at <https://quantmath.fintools.tw>) · `plans/` module briefs · `reviews/` review records ·
`project/` spec, pitfalls, sources.

## Working with agents

- One writer agent per module; it edits only that module's files. The main session is the editor and alone edits
  shared files (`build/`, `src/assets/`, `src/syllabus.yaml`, `AUTHORING.md`, `README.md`, `build.sh`,
  `data/README.md`, `reviews/`, `project/`, `TODO.md`, `CLAUDE.md`).
- Reviewers and verifiers are fresh, read-only agents that recompute from raw data; use `reviews/REVIEW_PROMPT.md`.
- Reviews of diffs and code also go to fresh Opus subagents, never to Codex (the owner's instruction, 2026-10-10):
  do not run `codex-companion` or enable the Codex review gate in this repository.
- Launch independent agents together in one message; do the editor's quick work before launching a batch.
- Data: raw FinMind files are never committed (licence); `data/raw_manifest.json` lists them and `fetch_finmind.py`
  rebuilds them. New data come from FinMind (MCP server or API token), in windows under 500 rows, each checked with
  `data/check_chunk.py` and registered with `fetch_finmind.py --add`; never invent or estimate data.
