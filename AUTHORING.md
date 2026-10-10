# Authoring guide

How a learning module (LM) is written, checked, reviewed and published. The reference module is
[`src/lm03.md`](src/lm03.md); when this guide and LM3 disagree, follow this guide.

## 1. Reader, voice, length

- **Reader:** a Taiwan-based futures/securities professional reviewing university mathematics on the way to
  quantitative portfolio work. Comfortable with markets; rusty on proofs. Prefers derivations to assertions and
  expects approximations to be called approximations.
- **Language:** English body text. Hard ideas get a **中文導讀** callout (`> [!zh]`) in Traditional Chinese, about one
  per one or two sections, 3–6 sentences, never a translation of the paragraph above it but the intuition behind it.
  Keep English terms in the Chinese text where they help (e.g. 波動拖累 volatility drag). Use Taiwan usage
  (最適, not 最優; 權益歸零 for zero equity, since 斷頭 means forced liquidation).
- **Voice:** textbook register, concise. Sentences under 25 words; paragraphs of at most four sentences.
  Active voice, concrete numbers, no filler ("it is worth noting", "in today's world"), no emoji, no questions as
  headings.
- **Length:** 30–40 A4 pages when printed (roughly 8,000–11,000 words including examples, problems and solutions).

## 2. File layout for module NN

| File | Content |
|:--|:--|
| `src/lmNN.md` | the module (front matter + Markdown) |
| `src/lmNN.js` | optional interactive figures (`Book.widgets.<name> = function (host) {…}`) |
| `src/data/lmNN-*.json` | chart specs, written by a script, never by hand |
| `data/lmNN_*.py` | scripts that compute every number quoted in the module (add them to `DATA_STEPS` in `build.sh`) |
| `data/raw/…` | verified raw data, git-ignored and registered in `data/raw_manifest.json` (see §8) |
| `build/make_labNN.py` | generates `labs/LMNN_lab/LMNN_lab.ipynb` |
| `labs/LMNN_lab/` | notebook (saved with outputs), `README.md`; its `data/` is built locally by `data/make_lab_data.py` |

## 3. Front matter

```yaml
---
lm: 1
title: Exponentials, Logarithms and Compounding        # must match src/syllabus.yaml
subtitle: "One line that states the module's point."
prereq: []                 # module numbers this one builds on (every module it cites for a result)
leads: [3, 19, 29]         # module numbers that build on this one
time: "≈ 2 h + lab"
js: [lm01.js]              # only if the module has widgets
outcomes:                  # 6–8; each completes "After this module you should be able to:"
  - "convert between periodic, effective annual and continuously compounded rates"
overview:                  # 6–8 bullets stating results, with numbers where possible
  - "…"
---
```

Outcomes start with an action verb (calculate, derive, explain, interpret, apply, compare), lower case, no final
period. YAML strings with backslashes need double escaping inside double quotes (`"$\\ln x$"`).

## 4. Module structure

1. `## Introduction` (unnumbered LO): one framing paragraph, then a `> [!case]` **Motivating Case** built on real,
   verified data that the module resolves later, then an exhibit with the case numbers, then a short roadmap.
   A `> [!note]` on notation lists the module's local symbols (see §6).
2. Numbered sections `## Title {lo=2,3}`: each maps to one or more outcomes. Inside: intuition → definition →
   derivation → exhibit → worked example → pitfall → 導讀 → knowledge check. Not every section needs every element.
3. Unnumbered closing sections, in this order: `## Summary {-}`, `## Practice Problems {-}`, `## Solutions {-}`,
   `## Glossary {-}`, `## References {-}`.

## 5. Markdown dialect

| Syntax | Use |
|:--|:--|
| `$…$`, `$$ … \tag{N.k} $$` | inline and display math; number only equations that are referred to, as `(N.k)` with N = module number |
| `> [!definition] Term` | precise English definition |
| `> [!theorem]`, `> [!proposition]`, `> [!result]` | statements; a proof follows or sits in a Deep Dive |
| `> [!example] Title {#label}` + nested `> > [!solution]` | worked example (8–10 per module) |
| `> [!exhibit] Title {#label}` | numbered table or chart; a final `Note:` or `Source:` line becomes the caption |
| `> [!pitfall] Title` | a common mistake and its fix |
| `> [!zh] 標題` | 中文導讀 |
| `> [!deepdive]- Title` | optional rigorous proof, collapsed |
| `> [!kc]` + nested `> > [!answer]-` | knowledge check (one per numbered section) |
| `> [!case] Title`, `> [!note] Title`, `> [!python] Title` | motivating case, side note, pointer to code/lab |
| `[[LM14]]`, `[[LM14|text]]` | link to another module (rendered as "coming" until it is published) |
| `[[ex:label]]`, `[[eg:label]]` | "Exhibit k" / "Example k" with automatic numbering; never type exhibit or example numbers by hand, not even in code comments or widget notes |
| `<div data-chart="lmNN-name"></div>` | chart from `src/data/lmNN-name.json` (inside an exhibit) |
| `<div class="widget" data-widget="name"></div>` | interactive figure defined in `src/lmNN.js` |
| ` ```python ` | code block with copy button |

- Write `NT\$` for New Taiwan dollars: an unescaped `$` starts math. Inside math, `\text{NT\$}` works.
- Every exhibit is cited in the prose at least once.
- In References, give every URL link text (`[site, page](https://…)`); bare URLs are hard to read in print.

Practice problems are an ordered list; multiple-choice options are a nested list `- **A.** …` (three options, A–C,
"*closest* to" for numeric answers; vary which letter is correct). Solutions are an ordered list with the same
numbering; multiple-choice solutions start with "**B** is correct." and explain why the distractors are wrong when
that teaches something.

## 6. Mathematics and notation

**One symbol, one meaning.** Within a module a symbol has exactly one meaning. The book-wide symbols below keep their
meaning in every module; a module may add local symbols in its notation note but may not reuse a book-wide symbol
for something else.

| Symbol | Book-wide meaning |
|:--|:--|
| $R$, $r$ | simple return per period; $r:=\ln(1+R)$ the log return. A continuously compounded rate is also an $r$: $r_f$, $r(t)$ |
| $\mu$, $\sigma$ | mean and standard deviation of $R$ in a model; $\bar R$ (or $\hat\mu$) and $s$ are the sample mean and standard deviation (say whether $s$ divides by $T$ or $T-1$) |
| $g$, $G$ | log growth rate per unit time ($g(f)$: growth as a function of exposure); growth factor, end value ÷ start value |
| $\mathrm{RV}$ | $\sum_t R_t^2$, realized variance |
| $A$ | periods per year used to annualize, e.g. $A=243.1$ trading sessions; always say which sample it comes from |
| $T$, $t$, $\tau$, $n$ | either a sample size (number of returns) or a horizon or maturity in years: a module uses one of the two and says which; time index; time to maturity or expiry, or any span in years when $T$ is a count; number of compounding or payment periods |
| $P$, $W$, $D$, $\mathrm{DD}$ | price; wealth; cash dividend ($D_1$ the next dividend); drawdown |
| $f$, $f^*$, $c$ | exposure ÷ equity of a position ($f>1$ is leverage); its growth-maximizing (Kelly) value; $c:=f/f^*$, the fraction of full Kelly |
| $L$ | a leveraged fund's fixed daily multiple (00631L: $L=2$); for a portfolio, total exposure $\sum_i f_i$ |
| $p$, $q$, $b$, $a$ | binary bet: win probability, $q=1-p$, gain $b$ and loss $a$ per unit staked, so $f^*=p/a-q/b$. In futures pricing $q$ is instead the continuous dividend yield; a module uses one of the two |
| $r_f$ | risk-free or financing rate (state the compounding) |
| $w$, $\mathbf w$, $\mathbf f$, $\Sigma$, $\rho$ | portfolio weights summing to 1; vector of exposures; covariance matrix; correlation |
| $\varphi$, $\Phi$ | standard normal density and distribution function |
| $y$, $i$, $v$, $k$, $\gamma$ | yield to maturity or IRR; periodic interest rate; discount factor $1/(1+i)$; required return; growth rate of dividends or cash flows (simple, per period) |
| $\lambda$, $\nu$, $\mathcal L$ | multiplier of an equality constraint; multipliers of inequality constraints (KKT); Lagrangian |
| $h$, $u$; $\psi$ | generic functions in modules where $f$ or $g$ already have their book-wide meaning ($f$, $g$, $h$ are fine in purely mathematical modules); constraint functions, $\psi(x)=b$ or $\psi_i(x)\le b_i$ |

- Subscripted standard symbols are distinct symbols and may sit beside the table: $D_{\text{mod}}$, $D_{\text{Mac}}$,
  $D_{\mathrm{KL}}$, $a_{n,i}$, $s_{n,i}$, $T_1(x)$.
- `=` only for exact statements; `≈` comes with the order or size of what was dropped; `:=` for definitions.
- State the conditions of every theorem (differentiability, convexity, sign or sum constraints on weights).
- Every formula the reader is asked to use is either derived or explicitly labelled *stated without proof* with a
  reference. Rigorous proofs go in Deep Dives.
- Use only what earlier modules teach. When a later idea is needed (skewness, kurtosis, confidence intervals,
  covariance, matrices), introduce it in a sentence or two and point to the module that develops it.
- Check every derivation numerically in the module's script before writing it down.

## 7. Exhibits, charts and widgets

- Exhibits are numbered automatically in order of appearance; reference them only with `[[ex:label]]`.
- Tables: right-align numbers (`--:`), give units in headers, round consistently, and make sure printed values add up
  as printed (if a sum is shown, its parts must sum to it at the displayed precision). Say when partial years or
  sub-samples are excluded.
- A chart must show every value the text cites from it (do not thin a series past the extremes you quote).
- Chart spec (`src/data/*.json`, produced by `data/lmNN_charts.py`):
  `{"alt", "height", "x": {"type": "date"|"num", "fmt", "label", "tipLabel", "min", "max"},
  "y": {"type": "lin"|"log", "fmt", "tfmt", "label", "min", "max"}, "series": [{"name", "endLabel", "color": "1".."4"
  or a CSS colour, "dash", "area", "x": [...], "y": [...]}], "ann": [{"type": "vline"|"hline"|"point"|"band", ...}],
  "endLabels", "endValue", "endMargin"}`.
  On a date axis, series and annotation dates may be ISO strings or epoch milliseconds.
  Format codes: `pct0..pct3`, `bp`, `x0..x2` (multiples), `n0..n5`. At most four series; legend is automatic.
- Widgets use `Book.lineChart(host, spec)` and `Book.fmt(v, code)` from `src/assets/book.js`; they must render a
  meaningful initial state (it is what the PDF shows) and must not depend on external libraries.

## 8. Data

- Real Taiwan and US data, and for historical data FinMind only (`TaiwanStockPrice`, `TaiwanStockDividendResult`,
  `TaiwanFuturesDaily`, `TaiwanStockTotalReturnIndex`, `USStockPrice`, …), fetched through the FinMind MCP tool in
  windows of fewer than 500 rows. Intraday history (`TaiwanVariousIndicators5Seconds`, minute bars, ticks) is too large
  for those windows: download it with a FinMind API token and a logged script (see `plans/ROADMAP.md`).
- Store raw files in `data/raw/` exactly as returned (`date,close,spread` for prices) and register each one in
  `data/raw_manifest.json` with `python3 data/fetch_finmind.py --add …`. `data/raw/` is git-ignored: FinMind's licence
  forbids redistributing raw data, so the repository keeps only the manifest and the scripts. Verify every close against
  FinMind's `spread` column with `data/check_chunk.py`; accept mismatches only on ex-dividend days (spread printed as
  0.0) and split days, and handle those explicitly in the script that builds returns. Around a split, restate the
  previous price per new share.
- Every number in the text, tables, examples, knowledge checks, problems and solutions must be produced by a script
  in `data/` or by the lab, and re-checked after the last edit.
- Conventions: a horizon in years is calendar days ÷ 365.25 unless an instrument has its own day count (actual/365
  for NTD deposits); quote the annualization factor $A$ of the sample in use.
- A motivating case built on one day says whether that day is typical or the extreme of the sample, and backs the
  claim with a multi-day figure.
- Futures: TAIEX closes on a 13:25–13:30 call auction while the TX daily settlement is set from the last minute of
  trading to 13:45, so daily basis changes are noisy. Back months trade thinly; report volume when it matters, and
  remember that an untraded contract's settlement price is set by exchange rules.
- Cite the dataset and retrieval date in the exhibit's `Source:` line.

## 9. Labs

Polars-first notebooks (NumPy/SciPy at the numerical edge, Matplotlib for plots) that run on Polars 1.x and 2.x:
pass literals to expressions with `pl.lit(...)` (strings are column names), avoid `map_elements` when a native
expression exists, and never rely on row order after a join (pass `maintain_order` or sort). A lab rebuilds the
module's exhibits and computational examples, solves the computational practice problems, and ends with one
extension exercise. It reads only files in its own `data/` folder, which is git-ignored and built from `data/raw/` by
`data/make_lab_data.py` (add the lab's files there). Commit it executed (`./build.sh --labs` or
`jupyter nbconvert --execute`).

## 10. Checks before a module goes to review

1. `python3 build/build.py lmNN` runs without KaTeX errors (a draft builds into `dist/preview/`).
2. No horizontal overflow at 400 px: `python3 build/qa/overflow.py file://$PWD/dist/preview/lm/lmNN.html 400`.
3. Screenshots in light and dark mode look right (`build/qa/shoot.py`).
4. Every number reproduced by the scripts; every `[[ex:…]]`/`[[eg:…]]` points where the prose intends.
5. The lab executes from a clean kernel.

## 11. Review and publishing

1. **Draft.** The writer delivers the files in §2. Drafts are committed to `main` but stay off the site: only
   modules whose entry in `src/syllabus.yaml` has `status: published` are built into `docs/`. Preview the whole site,
   drafts included, with `python3 build/build.py --preview` and open `dist/preview/index.html`.
2. **Independent review.** Someone who did not write the module recomputes every number from the raw data, solves
   every problem, checks the mathematics, facts, notation (§6) and Chinese, and reports findings by severity.
3. **Fixes.** The writer fixes every finding or explains in writing why not, then re-runs §10.
4. **Publish.** Add `status: published` to the module's syllabus entry, add an edition note, update the status table
   in `README.md`, run `./build.sh --pdf`, and commit `src/`, `data/`, `labs/` and `docs/` together.
