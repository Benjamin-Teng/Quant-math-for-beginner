# Pitfalls — mistakes already made, and the rule that prevents each

Read this before working on the book. Each item says what went wrong and what to do instead. Dates are 2026-10-10
unless stated.

## 1. Owner's rules that were broken once

- **References to a professional-certification curriculum.** The first edition borrowed one's structure and cited it
  (a crosswalk table, header chips, exam-style wording of the outcomes, references and a trademark note). The owner had all of it removed:
  the book is an independent personal-study project. Never add such references, mappings or comparisons, in text,
  code comments, front matter or docs. `uv run python build/qa/check_terms.py` (run by `build.sh`) fails the build if any
  appear. Also never commit third-party course material the owner shares for reference (licensed PDFs marked not for
  distribution).
- **Shioaji for historical data.** The syllabus once planned LM26's realized volatility "from Shioaji ticks". The
  owner's rule: all historical data come from FinMind, which has intraday history too
  (`TaiwanVariousIndicators5Seconds` for TAIEX every 5 seconds, free; minute bars and ticks on paid plans).
- **Raw FinMind data in a public repo.** FinMind's licence (every plan) forbids redistributing raw data, yet the first
  editions committed 63 raw files (`data/raw/`, lab snapshots). On 2026-10-10 they were removed, git history was
  rewritten and force-pushed at the owner's request, and `.gitignore` now excludes `data/raw/` and `labs/*/data/`.
  Commit only the manifest, scripts and derived results (statistics, chart specs, executed notebooks); rebuild raw
  files with `data/fetch_finmind.py`. The old commits stay reachable on GitHub by SHA (and through PR #1) until GitHub Support removes them; see TODO.md.
- **Pull requests.** The owner wants commits pushed straight to `main`. Before pushing, `git fetch` and rebase: the
  owner may change `main` on GitHub (he merged PR #1 there while work continued locally).
- **Asking too late.** The owner interrupted a large batch of agent launches twice to change course. Say what a big
  batch will do before starting it, keep him posted in Traditional Chinese, and push finished work promptly.

## 2. Environment and access

- **The cloud container has no general internet.** FinMind, Yahoo and cdnjs were blocked; only package registries
  and GitHub worked. Market data came through the FinMind MCP server running on the owner's computer. In a session
  without that server, use a FinMind API token instead, and never invent or estimate data.
- **FinMind returns at most 500 rows per query.** Query in windows (about 18 months of daily data for one stock), and
  check every window with `data/check_chunk.py`.
- **The Python environment is uv-managed** (`pyproject.toml` + `uv.lock`, since 2026-10-11): `uv sync`, then
  `uv run python <script>`; add a package with `uv add`, never `pip install`. The old `build/requirements.txt` lacked
  scipy and sympy, which the LM2/4/5/7 scripts import, and only running every step in a fresh environment showed it.
  After any dependency change, run `./build.sh --data --labs --preview` with
  `UV_PROJECT_ENVIRONMENT=<empty folder>` and inspect every change to `src/data/` and to the labs' text outputs: only
  last-digit floating-point noise is expected there (Windows and Linux differ at machine precision even with the same
  locked versions; a chart that plots values near 1e-16 shows it). Notebook images and metadata change whenever
  Matplotlib or the interpreter's patch version does. Installs can time out in a cloud container: run them in the
  background.
- **`gh` GraphQL calls were refused (HTTP 403).** Use REST through `gh api` (for example
  `gh api repos/Benjamin-Teng/Quant-math-for-beginner/pulls/1`).
- **The repo's canonical URL has a capital Q** (`Quant-math-for-beginner`); the lower-case remote works but GitHub
  prints a "repository moved" notice.
- **WebFetch cannot reach some sites** (MacTutor timed out once; law.moj.gov.tw was unreachable from the sandbox).
  Cite an equivalent official page, and say in the reference when a link could not be opened.
- **The Bash tool collapses a double backslash to a single one**, even inside single quotes and quoted heredocs, so a
  Python or regex patch passed inline loses its escapes (a negative lookbehind for a backslash became invalid; a
  JavaScript escaped quote lost its backslash; this very bullet was mangled the first time). Write the patch to a file
  with the file-writing tool, or build backslashes with `chr(92)`, and check the result.
- **The owner's Windows computer changes bytes and encodings.** Git for Windows checks text files out with CRLF
  (`core.autocrlf=true`), so a copy of a file taken from a checkout fails a SHA-256 check that a fresh fetch or
  `git show <commit>:<path>` passes; compare LF bytes. The default Python encoding there is cp950, which broke
  `build.py` reading KaTeX's UTF-8 output: run Python with `PYTHONUTF8=1` (`build.sh` sets it) and give every text
  read, write and subprocess an explicit `encoding="utf-8"` (and `newline="\n"` for data files). In Git Bash, set
  `MSYS_NO_PATHCONV=1` before `git show <rev>:<path>`, or the path is rewritten as a Windows path.

## 3. Data semantics (Taiwan)

- **Ex-dividend days:** FinMind prints `spread = 0.0`, so `close[t] − close[t−1] ≠ spread[t]`. Accept the mismatch only
  on a dividend date whose previous close equals `before_price` in `TaiwanStockDividendResult`.
- **FinMind's labels differ between instruments.** `TaiwanStockDividendResult.stock_or_cache_dividend` is `息` for
  0050 but `除息` for 00679B. The 00679B manifest entry carried 0050's filter `^息$`, so the first real re-fetch kept 0 of
  its 37 rows. Write a filter from the instrument's own records; `fetch_finmind.py --add` now re-fetches the query and
  refuses to register a file it cannot rebuild byte for byte (it needs `FINMIND_TOKEN`).
- **Ex-dates the checksum cannot see:** 00679B went ex on 2019-03-05 and 2025-08-21 with an unchanged close. The dividend
  file, not the checksum, is the authority for ex-dates.
- **Splits:** 0050 split 4-for-1 effective 2025-06-18 after a halt from 11 to 17 June, so that day's return spans six
  sessions; 00631L split 22-for-1 effective 2026-03-31 after its own halt. On a split day FinMind's spread is relative to
  the split-adjusted reference price. Restate the previous price per new share: total return =
  (P_t + D_t)/(P_{t−1}/s) − 1.
- **Aligned samples change the counts.** The 0050/00631L common-date sample has 2,902 returns and A = 243.1 sessions a
  year; TWSE averaged 243.8 a year in 2015–2025 (2,911 exchange sessions in the window: 0050's halt and the 00631L
  alignment remove nine). Say which sample a count or annualization factor comes from.
- **TX futures (`TaiwanFuturesDaily`):** on its last trading day the expiring contract's `settlement_price` prints 0.0
  (use `close` or TAIFEX's published final settlement price); on days a contract does not trade, `close` and `volume`
  print 0 while `settlement_price` is set by the exchange. For expiry, use the official final settlement price from
  `TaiwanFuturesFinalSettlementPrice` (the owner's Sponsor plan includes it). Back months often trade a few lots a day, so their
  settlements are partly exchange-determined: report volume when a result leans on them.
- **Futures vs index timing:** TAIEX closes on a 13:25–13:30 call auction; the TX daily settlement comes from the last
  minute before 13:45. Daily changes in the near-month basis therefore had a standard deviation of about 83 points in 2025, mostly timing noise. Example: on 2025-06-30
  TAIEX fell 1.44% (about 40 points of it ex-dividend) while the July TX settled +0.10%.
- **Final settlement:** TAIFEX averages the published index values from 13:00 (exclusive) to 13:25 (inclusive) plus the
  closing value; at expiry the future converges to that average, not to the 13:30 close.
- **Not in FinMind:** Taiwan's central-bank policy rate (`InterestRate` has the Fed, the ECB and others, not the CBC).
  Cite a dated news report instead (the discount rate was 2%, held for ten consecutive quarters at the 2026-09-17
  meeting).
- **Dividends measured from the total-return index are ex-dates, not payment dates.** Say "ex-dividend" and say which
  quantity a decomposition uses (yield valued at a date versus index points removed).
- **A one-day case can be the sample's extreme.** LM6's 27 June 2025 was the most extreme of 146 days; claims built on
  it failed from the next session. Back a one-day case with a multi-day figure and say where it ranks.
- **2025 TX margins:** no official TAIFEX page was found, only third-party reports; LM2 labels its margin illustrative
  and quotes the official figures effective 2026-08-12.

## 4. Build system and rendering

- **Two module instances.** `build_index.py` imported `build` as a new module, so it saw the default target and wrote
  the artifact index into `docs/`. Fixed with `sys.modules.setdefault("build", …)`; keep that line.
- **Inline math and dollars.** The inline-math pattern used to stop at any `$`, so `\text{NT\$}` inside `$…$` silently
  merged formulas with text (and caused overflow that `overflow.py` did not flag). The pattern now accepts escaped
  characters, but write NT\$ outside math by default.
- **Chart annotations on date axes** needed epoch milliseconds; `book.js` now converts ISO strings too.
- **Missing chart features:** date axes print only year ticks (sub-year charts need labelled vertical lines), and
  `lineChart` has no custom tick labels (widgets relabel ticks themselves). Both are open in TODO.md.
- **Thinned chart series hid the extremes the text quoted** (LM4 Exhibit 8). Keep cited extremes in the plotted data.
- **Mobile overflow:** negative margins on the module band, `white-space: nowrap` on inline math, bare URLs in
  References, and multiple-choice options laid out as grid cells all overflowed at 400 px. Check every page with
  `build/qa/overflow.py <url> 400` and look at screenshots; the overflow script does not catch everything.
- **Uppercase transforms break Greek:** `text-transform: uppercase` turned μ into Μ in a widget readout. Never
  uppercase text that can contain math.
- **The outline (right rail) showed math placeholders** until rendered math was substituted there too.
- **Hand-typed exhibit and example numbers went stale.** Use `[[ex:label]]` / `[[eg:label]]` everywhere; never type the
  numbers, not even in code comments, widget notes or lab cells (the LM1 lab now reads them from the labels).
- **Drafts used to overwrite the published site.** Drafts now build only into `dist/preview/`; only
  `status: published` modules reach `docs/`. Writers and reviewers must not run a full `./build.sh` that rewrites
  `docs/` with their changes, and an agent building one module can still rewrite shared assets, so the editor rebuilds
  everything before publishing.
- **Editing code with `sed` broke an f-string** in `build/qa/shoot.py`, and a greedy regex (DOTALL) once matched to the
  end of `syllabus.yaml`; an assertion stopped the write. Edit with an editor tool or a script that asserts the exact
  number of replacements before writing.

## 5. Python, Polars and notebooks

- The container had **Polars 2.0**; labs must also run on 1.x. Strings passed to expressions are column names
  (`is_between("2021-12-31", …)` failed): wrap literals in `pl.lit(...)`. Avoid `map_elements` when a native expression
  exists. Polars 2.0 raised `DuplicateError` on some print expressions; keep printing simple.
- **Row order after a join is not guaranteed** in Polars 2.0; sort (or pass `maintain_order`) before `shift`, `cum_max`
  or anything order-dependent.
- **A lab must read only its own `data/` folder** (LM7's read a processed parquet that is not shipped).
- **Commit notebooks executed**, after `uv run jupyter nbconvert --to notebook --execute --inplace LMNN_lab.ipynb` from
  inside the lab folder.

## 6. Working with agents

- **One module per writer; shared files belong to the editor** (`build/`, `src/assets/`, `src/syllabus.yaml`,
  `AUTHORING.md`, `README.md`, `build.sh`, `data/README.md`, `reviews/`, `project/`, `TODO.md`, `CLAUDE.md`).
- **Reviews must be independent and read-only**: a fresh agent that did not write the module, recomputing from raw data,
  forbidden to run scripts that write files. Writers' own checks missed 116 findings across five Volume I modules
  (6 critical), and the LM3 review found 34 (including figures 10× too large).
- **A review agent died on an output-filter error**, most likely from quoting long passages from sources. Reviewers and
  writers paraphrase sources and never quote more than a sentence.
- **Agent calls block the main session until the whole batch finishes.** Do the editor's quick work first, then launch
  one batch of parallel agents in a single message.
- **Interrupted agents keep their context**; resume them with a message instead of starting fresh.
- **Give writers the cross-module notation decisions up front.** Six drafts written in parallel clashed on f, L, G, φ,
  g, D, T and q until AUTHORING §6 fixed a book-wide table.

## 7. Content errors the reviews caught (check these before handing a module over)

- Theorem conditions left out: weights in the weighted AM–GM inequality must be non-negative and sum to 1;
  differentiability for "strictly concave ⇒ at most one critical point"; continuous second partials for a second-order
  Taylor error.
- "=" where "≈" belongs, and approximations whose dropped order is not stated.
- Wrong causal story: LM4 blamed the ±10% days for the quadratic Kelly rule's overshoot (the cause is kurtosis); LM7
  blamed fat tails for a gap partly due to a dropped squared mean.
- Statistical terms misused: a raw third moment called skewness.
- Printed numbers that do not recompute from the printed inputs (rounding); tables whose parts do not sum as printed;
  partial years silently omitted.
- Conventions mixed: 365 vs 365.25 days, 243.1 vs 243.8 vs 252 sessions, rates per day vs per year.
- Logic slips: net vs gross exposure; an enumeration of KKT active sets that missed two cases; "bisection halves the
  error" (it halves the bracket); a shadow price read as a total gain.
- Concepts used before they are taught (continuity, the chain rule, covariance, skewness, confidence intervals, the
  Sharpe ratio, matrices) without a short introduction and a pointer.
- Chinese usage: Taiwan terms (最適, not 最優); 斷頭 means forced liquidation, not zero equity; 翻了幾倍 reads as
  "how many-fold" (use 翻了幾番 for doublings).
- Facts to keep straight: TWSE's daily limit widened from 7% to 10% on 2015-06-01; 7 April 2025 was the first session
  after the Qingming holiday and closed at the −10% limit for TX; TAIFEX margins change after sessions, so date them.
- Found by the 2026-10-11 gates (blind solving and full audits) after the first revisions; check these too:
  - The dominant error is still a printed figure computed from unrounded inputs: a reader multiplying the printed
    factors, summing the printed parts or plugging the printed rate gets a different last digit (LM1's six block returns
    compound to 902.18%, not the printed 902.25%; LM6 printed qτ to two decimals while its other columns used six).
    Carry the digit, round the output to what the printed inputs support, or say the figure uses unrounded inputs.
  - A question must state its conventions: which five annualizations, which recovery time, effective or continuous
    rates, a 365-day year, a bracket width or a midpoint error, how a mix is rebalanced. A blind solver who has to
    guess will find a second valid answer.
  - Undiscounted totals are not savings: at the loan's own rate every repayment schedule is worth the principal, so
    "equal principal saves NT$360,064 of interest" teaches the opposite of the time value of money.
  - A sign read backwards: a negative partial derivative g_{f2} means that selling the asset raises growth, so the
    short adds value at the margin. Check the sign of every marginal-value sentence against the formula.
  - Exchange limits make ratios: on 7 April 2025 0050 (−10%) and 00631L (−19.995%) both closed limit-down, so their
    ratio of 2.000 shows the limits, not the fund's leverage. Check limit days before reading a one-day ratio.
  - Averages of annualized rates near expiry are noise: a few days with τ of one or two days dominate a monthly mean
    of daily implied rates. Annualize the averaged components instead, or leave the column out.
  - A chart that plots values near machine precision differs between Windows and Linux; floor it well above 1e-16.
  - Notation peculiar to one certification curriculum's formula sheet (for example "ΔCurve") counts as a reference to
    it: use the module's own symbols.
