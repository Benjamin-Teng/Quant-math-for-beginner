# CLAUDE.md — From Calculus to Kelly

A self-study quantitative-finance textbook (static website + A4 PDFs + Jupyter labs) that runs from first-year
calculus, statistics and linear algebra to Kelly leverage, GBM and Itô's lemma. Owner: Benjamin. MIT License.
An independent personal-study project.

## Read first, in this order

1. [`TODO.md`](TODO.md) — the current work queue and its order; [`plans/ROADMAP.md`](plans/ROADMAP.md) for the volumes after Volume I.
2. [`project/SPEC.md`](project/SPEC.md) — what the owner decided (format, language, rigor, hosting, rules).
3. [`project/PITFALLS.md`](project/PITFALLS.md) — mistakes already made and the rule that prevents each. Do not repeat them.
4. [`AUTHORING.md`](AUTHORING.md) — how a module is written, checked, reviewed and published; §6 is the book-wide notation table.
5. [`reviews/`](reviews/README.md) — review findings and their status per module.
6. [`project/SOURCES.md`](project/SOURCES.md) — where facts and data were checked.

## Owner's standing rules

- Talk to Benjamin in **Traditional Chinese**; the book itself is English with 中文導讀 boxes.
- **Commit and push directly to `main`**; no pull requests. `git fetch` and rebase before every push.
- **No references to any professional-certification curriculum or exam body**, anywhere. `build/qa/check_terms.py`
  must pass (`build.sh` runs it).
- **Historical market data come only from FinMind** (daily and intraday); never Shioaji for history. He has a
  **Sponsor plan** (6,000 calls an hour; minute bars, ticks, final settlement prices…), licensed for non-commercial
  use: never redistribute raw FinMind data, and cite FinMind.
- Never commit third-party course material he shares for reference.
- Publish a module only after an independent review and verified fixes (AUTHORING §11).

## Commands

```bash
uv pip install -r build/requirements.txt          # Python deps (pip: add --break-system-packages in containers)
(cd build && npm ci)                              # KaTeX + self-hosted fonts
python3 build/build.py                            # published site -> docs/
python3 build/build.py --preview                  # every module incl. drafts -> dist/preview/ (git-ignored)
python3 build/build.py lm04                       # one module (a draft goes to dist/preview/)
./build.sh [--data] [--labs] [--pdf] [--preview]  # full pipeline; --pdf needs `playwright install chromium`
python3 build/qa/overflow.py file://$PWD/dist/preview/lm/lm04.html 400   # horizontal overflow check
python3 build/qa/check_terms.py                   # banned-terms check
python3 data/check_chunk.py data/raw/<file>.csv   # verify a raw FinMind chunk against its spread column
FINMIND_TOKEN=... python3 data/fetch_finmind.py  # rebuild data/raw/ (git-ignored) from FinMind; --verify checks offline
python3 data/make_lab_data.py                     # build every lab's data/ folder from data/raw/
```

## Layout

`src/` module sources (`lmNN.md`, `lmNN.js`, `data/*.json`, `assets/`, `syllabus.yaml`) · `build/` builders and QA ·
`data/` the raw-data manifest, fetch script and the scripts that compute every number · `labs/` executed notebooks (data built locally) ·
`docs/` the published site (GitHub Pages, `main` `/docs`) · `plans/` module briefs · `reviews/` review records ·
`project/` spec, pitfalls, sources.

## Working with agents

- One writer agent per module; it edits only that module's files. The main session is the editor and alone edits
  shared files (`build/`, `src/assets/`, `src/syllabus.yaml`, `AUTHORING.md`, `README.md`, `build.sh`,
  `data/README.md`, `reviews/`, `project/`, `TODO.md`, `CLAUDE.md`).
- Reviewers and verifiers are fresh, read-only agents that recompute from raw data; use `reviews/REVIEW_PROMPT.md`.
- Launch independent agents together in one message; do the editor's quick work before launching a batch.
- Data: raw FinMind files are never committed (licence); `data/raw_manifest.json` lists them and `fetch_finmind.py`
  rebuilds them. New data come from FinMind (MCP server or API token), in windows under 500 rows, each checked with
  `data/check_chunk.py` and registered with `fetch_finmind.py --add`; never invent or estimate data.
