# Project spec — From Calculus to Kelly

What the owner (Benjamin) and Claude agreed for this book. Change any item here only with the owner's approval,
and record the change with its date. How modules are written is in [`../AUTHORING.md`](../AUTHORING.md); what is
left to do is in [`../TODO.md`](../TODO.md).

## 1. Purpose

- Review university mathematics from first-year **calculus, statistics and linear algebra**, and carry it through to
  the **Kelly criterion, Kelly leverage, geometric Brownian motion (GBM) and Itô's lemma**, with the linear algebra
  and statistics they need.
- By the end the reader can: **build their own statistical models**; **optimize portfolios statistically**;
  **measure true risk and return** (geometric growth, honest uncertainty, costs and biases removed); and
  **optimize Kelly leverage**, including under estimation error.
- A personal study project. It is independent of any professional-certification curriculum and must not reference
  one (owner, 2026-10-10). Released under the MIT License (owner, 2026-10-10).

## 2. Reader

A Taiwan-based futures and securities professional: fluent in markets, rusty on proofs, prefers derivations to
assertions, wants real Taiwan and US market cases, and expects approximations to be called approximations.

## 3. Decisions

| Topic | Decision | Source |
|:--|:--|:--|
| Format | an online textbook website (multi-page HTML), plus one A4 PDF per module, plus Markdown sources that open as an Obsidian vault | owner's choice |
| Language | English body text with technical terms in English; hard ideas get a Traditional Chinese 中文導讀 box | owner's choice |
| Rigor | derivations complete; optional rigorous proofs in collapsed Deep Dive boxes | owner's choice |
| Code | short Python snippets in the text, plus one Jupyter lab per module; Polars first | owner's choice |
| Length | no limit for the whole book; each module 30–40 A4 pages | original brief; AUTHORING §1 |
| Presentation | clear heading hierarchy; diagrams, charts and worked examples; concise prose; real market situations as cases | original brief |
| Data | real Taiwan and US market data (FinMind), verified against FinMind's own checksums; every printed number reproduced by a script | agreed while building LM3 |
| Historical data source | FinMind only, including intraday history (5-second TAIEX, minute bars, ticks); Shioaji is not used for historical data | owner, 2026-10-10 |
| FinMind plan | Sponsor: 6,000 API calls an hour and every Free, Backer and Sponsor dataset; non-commercial licence that forbids redistributing raw data and requires citing FinMind | owner, 2026-10-10 |
| Remaining volumes | five batches after Volume I: II + III, IV + V, VI + VII, VIII, IX (`plans/ROADMAP.md`) | agreed 2026-10-10 |
| Hosting | GitHub repo [Benjamin-Teng/Quant-math-for-beginner](https://github.com/Benjamin-Teng/Quant-math-for-beginner) (public); the built site in `docs/` is served by GitHub Pages from `main` `/docs`, and will move to the owner's own domain via `docs/CNAME` | owner, 2026-10-10 |
| Git | commit and push directly to `main`; no pull requests | owner, 2026-10-10 |
| License | MIT (`LICENSE`); FinMind data remain subject to FinMind's terms | owner, 2026-10-10 |
| Independence | no references to any professional-certification curriculum or exam body, anywhere in the repo; `build/qa/check_terms.py` enforces it | owner, 2026-10-10 |
| Quality gate | a module is published (linked from the site, PDF built) only after an independent review and its fixes | editor's process, AUTHORING §11 |
| Unclear brief | raise it with the owner rather than guess | original brief |
| Conversation | the owner reads and writes Traditional Chinese; reply to him in Traditional Chinese | owner's preference |

## 4. Structure

Nine volumes, fifty learning modules; the authoritative list (titles, one-line descriptions, publish status) is
[`../src/syllabus.yaml`](../src/syllabus.yaml).

| Volume | Title | Modules |
|:--|:--|:--|
| I | Calculus for Finance | LM1–LM7 |
| II | Linear Algebra for Portfolios | LM8–LM12 |
| III | Probability | LM13–LM18 |
| IV | Statistical Inference and Econometrics | LM19–LM26 |
| V | Stochastic Calculus | LM27–LM31 |
| VI | Portfolio Optimization | LM32–LM36 |
| VII | Measuring True Risk and Return | LM37–LM40 |
| VIII | The Kelly Criterion and Optimal Leverage | LM41–LM46 |
| IX | Capstone | LM47–LM50 |

Every module has the same architecture: Learning Outcomes (with tick boxes) → Learning Module Overview → Motivating
Case on verified data → numbered sections (intuition, definition, derivation, exhibit, worked example, pitfall,
中文導讀, knowledge check) → Summary → Practice Problems → Solutions → Glossary (English–中文) → References, plus a
lab notebook that reproduces every number. Details: AUTHORING §4–§5.

## 5. Design system

- **Type:** Source Serif 4 (body), Archivo (headings and interface), IBM Plex Mono (code), self-hosted as woff2 from
  npm Fontsource; Noto Sans TC (Chinese) from Google Fonts.
- **Colour tokens** (`src/assets/book.css`, light and dark): paper `#f8f9fa`, ink `#15181c`, accent `#1c5aa6`,
  seal `#b8360f` (中文導讀), amber (pitfalls, draft chip), grey panel (examples).
- **Chart palette:** light `#2a78d6`, `#eb6834`, `#1baf7a`, `#6250d6`; dark `#3987e5`, `#d95926`, `#199e70`, `#9085e9`.
- **Math:** KaTeX 0.16.11 rendered at build time, so formulas need no client-side JavaScript.
- **Charts and widgets:** the dependency-free `src/assets/book.js` (line charts with hover tooltips, log/linear axes,
  light/dark aware; widgets registered as `Book.widgets.<name>`). Charts are specified in `src/data/*.json`.
- **Layout:** left rail (book contents), centre page, right outline; no horizontal overflow at 400 px.
- **Print/PDF:** Playwright/Chromium, A4, margins 16/18/15 mm, every `<details>` opened, footer
  "From Calculus to Kelly · LMn Title · page/total".

## 6. Build outputs

| Target | Command | Output |
|:--|:--|:--|
| Published site | `python3 build/build.py` (or `./build.sh`) | `docs/` (published modules only) |
| Preview with drafts | `python3 build/build.py --preview` | `dist/preview/` (git-ignored) |
| claude.ai artifact bundle | `python3 build/build.py --target artifact` | `dist/artifact/` (content-only index; git-ignored) |
| PDFs | `./build.sh --pdf` | `docs/pdf/LMnn_Title.pdf` |

A private claude.ai artifact preview of the site exists; updating it needs a Claude session with the artifact tool and
is optional.
