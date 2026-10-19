# Quant-math-for-beginner · From Calculus to Kelly

從大一的微積分、統計學與線性代數開始，一路推進到**自建統計模型、投資組合統計最佳化、計算真正的風險報酬，以及在估計誤差下求最適凱利槓桿**。全書 9 卷 50 個 Learning Modules，每章依「Learning Outcomes → 編號章節 → Example／Exhibit → Practice Problems → Solutions」編排。內文以英文為主，難懂之處附「中文導讀」；每章附 Jupyter Lab，用台股與美股真實資料重現書中每個數字。這是個人學習用的專案。

*A nine-volume quantitative curriculum that starts from first-year calculus, statistics and linear algebra and ends with statistical models, optimized portfolios and growth-optimal (Kelly) leverage. English text with Traditional Chinese reading guides; every module ships with a lab notebook on real Taiwan and US market data. A personal study project.*

## Status — Edition 0.5 (2026-10-20)

| Module | State | HTML | PDF | Lab |
|:--|:--|:--|:--|:--|
| Roadmap, contents, notation | published | [`docs/index.html`](docs/index.html) | — | — |
| LM1 Exponentials, Logarithms and Compounding | published | [`docs/lm/lm01.html`](docs/lm/lm01.html) | [`docs/pdf/LM01_…pdf`](docs/pdf/LM01_Exponentials_Logarithms_and_Compounding.pdf) | [`labs/LM01_lab`](labs/LM01_lab) |
| LM2 Limits and Derivatives | published | [`docs/lm/lm02.html`](docs/lm/lm02.html) | [`docs/pdf/LM02_…pdf`](docs/pdf/LM02_Limits_and_Derivatives.pdf) | [`labs/LM02_lab`](labs/LM02_lab) |
| LM3 Taylor Series and Approximation | published | [`docs/lm/lm03.html`](docs/lm/lm03.html) | [`docs/pdf/LM03_…pdf`](docs/pdf/LM03_Taylor_Series_and_Approximation.pdf) | [`labs/LM03_lab`](labs/LM03_lab) |
| LM4 Optimization in One Variable | published | [`docs/lm/lm04.html`](docs/lm/lm04.html) | [`docs/pdf/LM04_…pdf`](docs/pdf/LM04_Optimization_in_One_Variable.pdf) | [`labs/LM04_lab`](labs/LM04_lab) |
| LM5 Integration | published | [`docs/lm/lm05.html`](docs/lm/lm05.html) | [`docs/pdf/LM05_…pdf`](docs/pdf/LM05_Integration.pdf) | [`labs/LM05_lab`](labs/LM05_lab) |
| LM6 Sequences, Series and the Time Value of Money | published | [`docs/lm/lm06.html`](docs/lm/lm06.html) | [`docs/pdf/LM06_…pdf`](docs/pdf/LM06_Sequences_Series_and_the_Time_Value_of_Money.pdf) | [`labs/LM06_lab`](labs/LM06_lab) |
| LM7 Multivariable Calculus and Lagrange Multipliers | published | [`docs/lm/lm07.html`](docs/lm/lm07.html) | [`docs/pdf/LM07_…pdf`](docs/pdf/LM07_Multivariable_Calculus_and_Lagrange_Multipliers.pdf) | [`labs/LM07_lab`](labs/LM07_lab) |
| LM8 Vectors and Matrices | published | [`docs/lm/lm08.html`](docs/lm/lm08.html) | [`docs/pdf/LM08_…pdf`](docs/pdf/LM08_Vectors_and_Matrices.pdf) | [`labs/LM08_lab`](labs/LM08_lab) |
| LM9 Linear Systems, Inverses and Rank | published | [`docs/lm/lm09.html`](docs/lm/lm09.html) | [`docs/pdf/LM09_…pdf`](docs/pdf/LM09_Linear_Systems_Inverses_and_Rank.pdf) | [`labs/LM09_lab`](labs/LM09_lab) |
| LM10 Quadratic Forms and Covariance Matrices | published | [`docs/lm/lm10.html`](docs/lm/lm10.html) | [`docs/pdf/LM10_…pdf`](docs/pdf/LM10_Quadratic_Forms_and_Covariance_Matrices.pdf) | [`labs/LM10_lab`](labs/LM10_lab) |
| LM11 Eigen-decomposition and PCA | published | [`docs/lm/lm11.html`](docs/lm/lm11.html) | [`docs/pdf/LM11_…pdf`](docs/pdf/LM11_Eigen_decomposition_and_PCA.pdf) | [`labs/LM11_lab`](labs/LM11_lab) |
| LM12 Cholesky, SVD and Least Squares | published | [`docs/lm/lm12.html`](docs/lm/lm12.html) | [`docs/pdf/LM12_…pdf`](docs/pdf/LM12_Cholesky_SVD_and_Least_Squares.pdf) | [`labs/LM12_lab`](labs/LM12_lab) |
| LM13 Probability Foundations and Bayes | published | [`docs/lm/lm13.html`](docs/lm/lm13.html) | [`docs/pdf/LM13_…pdf`](docs/pdf/LM13_Probability_Foundations_and_Bayes.pdf) | [`labs/LM13_lab`](labs/LM13_lab) |
| LM14 Random Variables, Expectation and Jensen's Inequality | published | [`docs/lm/lm14.html`](docs/lm/lm14.html) | [`docs/pdf/LM14_…pdf`](docs/pdf/LM14_Random_Variables_Expectation_and_Jensen_s_Inequality.pdf) | [`labs/LM14_lab`](labs/LM14_lab) |
| LM15 Distributions in Finance | published | [`docs/lm/lm15.html`](docs/lm/lm15.html) | [`docs/pdf/LM15_…pdf`](docs/pdf/LM15_Distributions_in_Finance.pdf) | [`labs/LM15_lab`](labs/LM15_lab) |
| LM16 Joint Distributions and Dependence | published | [`docs/lm/lm16.html`](docs/lm/lm16.html) | [`docs/pdf/LM16_…pdf`](docs/pdf/LM16_Joint_Distributions_and_Dependence.pdf) | [`labs/LM16_lab`](labs/LM16_lab) |
| LM17 Law of Large Numbers and Central Limit Theorem | published | [`docs/lm/lm17.html`](docs/lm/lm17.html) | [`docs/pdf/LM17_…pdf`](docs/pdf/LM17_Law_of_Large_Numbers_and_Central_Limit_Theorem.pdf) | [`labs/LM17_lab`](labs/LM17_lab) |
| LM18 Monte Carlo Simulation and the Bootstrap | published | [`docs/lm/lm18.html`](docs/lm/lm18.html) | [`docs/pdf/LM18_…pdf`](docs/pdf/LM18_Monte_Carlo_Simulation_and_the_Bootstrap.pdf) | [`labs/LM18_lab`](labs/LM18_lab) |
| LM19 Descriptive Statistics of Returns | published | [`docs/lm/lm19.html`](docs/lm/lm19.html) | [`docs/pdf/LM19_…pdf`](docs/pdf/LM19_Descriptive_Statistics_of_Returns.pdf) | [`labs/LM19_lab`](labs/LM19_lab) |
| LM20 Estimation Theory and Maximum Likelihood | published | [`docs/lm/lm20.html`](docs/lm/lm20.html) | [`docs/pdf/LM20_…pdf`](docs/pdf/LM20_Estimation_Theory_and_Maximum_Likelihood.pdf) | [`labs/LM20_lab`](labs/LM20_lab) |
| LM21 Hypothesis Testing and Multiple Testing | published | [`docs/lm/lm21.html`](docs/lm/lm21.html) | [`docs/pdf/LM21_…pdf`](docs/pdf/LM21_Hypothesis_Testing_and_Multiple_Testing.pdf) | [`labs/LM21_lab`](labs/LM21_lab) |
| LM22 Resampling Methods | published | [`docs/lm/lm22.html`](docs/lm/lm22.html) | [`docs/pdf/LM22_…pdf`](docs/pdf/LM22_Resampling_Methods.pdf) | [`labs/LM22_lab`](labs/LM22_lab) |
| LM23 Linear Regression | published | [`docs/lm/lm23.html`](docs/lm/lm23.html) | [`docs/pdf/LM23_…pdf`](docs/pdf/LM23_Linear_Regression.pdf) | [`labs/LM23_lab`](labs/LM23_lab) |
| LM24 Bayesian Inference and Shrinkage | published | [`docs/lm/lm24.html`](docs/lm/lm24.html) | [`docs/pdf/LM24_…pdf`](docs/pdf/LM24_Bayesian_Inference_and_Shrinkage.pdf) | [`labs/LM24_lab`](labs/LM24_lab) |
| LM25 Time Series I: ARMA, Unit Roots and Cointegration | published | [`docs/lm/lm25.html`](docs/lm/lm25.html) | [`docs/pdf/LM25_…pdf`](docs/pdf/LM25_Time_Series_I_ARMA_Unit_Roots_and_Cointegration.pdf) | [`labs/LM25_lab`](labs/LM25_lab) |
| LM26 Time Series II: Volatility Models | published | [`docs/lm/lm26.html`](docs/lm/lm26.html) | [`docs/pdf/LM26_…pdf`](docs/pdf/LM26_Time_Series_II_Volatility_Models.pdf) | [`labs/LM26_lab`](labs/LM26_lab) |

A module goes on the site only after an independent review has recomputed its numbers and checked its mathematics; drafts are kept in `src/` and `labs/` but are not linked from the site. The full syllabus lives in [`src/syllabus.yaml`](src/syllabus.yaml).

## Repository layout

```text
docs/            built static site, published modules only — upload as-is to any host (GitHub Pages: main /docs)
  index.html       roadmap and contents
  lm/              one page per learning module
  pdf/             A4 print editions
  assets/          CSS, JS, self-hosted fonts and KaTeX
src/             sources (Obsidian-compatible Markdown)
  syllabus.yaml    volumes, modules, publish status, edition notes
  lmNN.md          module text: $math$, > [!callouts], exhibits, problems
  lmNN.js          the module's interactive figures
  data/            chart specs (generated by data/lmNN_charts.py)
  assets/          book.css, book.js, favicon
build/           build.py (Markdown → HTML, KaTeX at build time), build_index.py, render_pdf.py,
                 make_labNN.py, katex_render.js, package.json, qa/ (screenshots, overflow check)
data/            scripts that compute every number, table and chart; raw_manifest.json + fetch_finmind.py rebuild raw/
labs/            LMNN_lab/ notebooks (saved with outputs); their data/ is built by data/make_lab_data.py
plans/           module briefs
reviews/         independent review records: findings, decisions, fix status, prompt templates
project/         SPEC.md (agreed decisions), PITFALLS.md (mistakes not to repeat), SOURCES.md (sites consulted)
AUTHORING.md     how a module is written, checked, reviewed and published
TODO.md          the current work queue (handoff)
CLAUDE.md        orientation for Claude Code sessions
build.sh         one-shot build
pyproject.toml   the Python environment, managed by uv (uv.lock pins every version)
```

## Build

Python is managed with [uv](https://docs.astral.sh/uv/): `uv sync` creates `.venv` from `uv.lock` (Python 3.13), and every
script runs as `uv run python <script>`.

```bash
uv sync                           # locked Python environment in .venv
(cd build && npm ci)              # KaTeX + self-hosted fonts
./build.sh                        # docs/ (web) and dist/artifact/ (claude.ai artifact bundle)
./build.sh --preview              # also dist/preview/: the whole site with drafts, for local review
./build.sh --pdf                  # also render docs/pdf/ (first: uv run playwright install chromium)
./build.sh --fetch                # rebuild data/raw/ and the labs' data/ from FinMind (needs FINMIND_TOKEN)
./build.sh --data                 # rebuild data/processed and src/data/*.json from data/raw
./build.sh --labs                 # regenerate and execute the lab notebooks
```

Math is rendered to HTML at build time, so the pages need no JavaScript to show formulas; charts and the interactive figures use a small dependency-free script (`src/assets/book.js`).

## Hosting on your own domain

Every link in `docs/` is relative, so the site works at a domain root or under a sub-path.

- **GitHub Pages:** Settings → Pages → *Deploy from a branch* → `main` / `/docs`; the site is live at <https://quantmath.fintools.tw>. `build/build.py` writes `docs/CNAME` with that domain, and a DNS `CNAME` record points `quantmath.fintools.tw` at `benjamin-teng.github.io`.
- **Any static host** (Cloudflare Pages, Netlify, your own server): publish the `docs/` folder; no build step is needed on the host.

## Writing a module

See [`AUTHORING.md`](AUTHORING.md). In short, `src/lmNN.md` starts with YAML front matter (`lm`, `title`, `subtitle`, `prereq`, `leads`, `time`, `js`, `outcomes`, `overview`) followed by Markdown:

| Syntax | Renders as |
|:--|:--|
| `$x$`, `$$…\tag{3.1}$$` | KaTeX inline / numbered display math |
| `## Title {lo=2,3}` · `## Summary {-}` | numbered section mapped to outcomes 2 and 3 · unnumbered section |
| `> [!definition] Term` · `theorem` · `pitfall` · `zh` · `kc` · `case` · `note` | callout boxes (`zh` = 中文導讀) |
| `> [!example] Title {#label}` with a nested `> > [!solution]` | numbered example with its solution |
| `> [!exhibit] Title {#label}` | numbered table or chart; a final `Note:` / `Source:` line becomes the caption |
| `> [!deepdive]- Title`, `> > [!answer]-` | collapsed proof / answer |
| `[[LM14]]`, `[[ex:label]]`, `[[eg:label]]` | links to modules, exhibits, examples (numbered automatically) |
| `<div data-chart="id"></div>` | chart from `src/data/id.json` (hover tooltips, light/dark aware) |

The same files open cleanly in Obsidian, so the sources double as a notes vault.

## Data

Taiwan prices, dividends, index and futures data come from FinMind (`TaiwanStockPrice`, `TaiwanStockDividendResult`, `TaiwanStockTotalReturnIndex`, `TaiwanFuturesDaily`, and for Volume II the 13:30:00 index values of `TaiwanStockEvery5SecondsIndex` and `TaiwanVariousIndicators5Seconds`); US prices come from FinMind `USStockPrice`. The files were retrieved on 2026-10-10, except Volume II's `sectors/`, `sectors_close/` and `taiex_close/` files (2026-10-11). Every daily close in `data/raw/` was checked against FinMind's own `spread` column (close − previous close). In Volume I's files the only mismatches are ex-dividend days and the two share splits (0050 4-for-1 on 2025-06-18, 00631L 22-for-1 on 2026-03-31), which the pipeline handles explicitly. In Volume II's sector-index series FinMind copies some closes from other dates or series: `data/vol2_series.py` replaces the 561 wrong closes with their 13:30:00 values and accepts 1,528 stale spreads whose closes agree with their neighbours. TAIEX's spread prints 0.0 on 52 dates, and each of those closes equals its 13:30:00 value. Volume III's main sample is the TAIEX total-return index (`TaiwanStockTotalReturnIndex`, retrieved 2026-10-18), 2003-01-02 to 2026-10-08, which FinMind serves from 2003-01-02; it has no spread column, so `data/vol3_series.py` checks every row against the TAIEX price index (the same 5,850 dates, each price close against its spread, and the daily dividend gap within rounding and 1%). Volume IV adds TX's daily history (`TaiwanFuturesDaily`, retrieved 2026-10-19) and, through `data/fetch_intraday.py`, the intraday TAIEX (`TaiwanVariousIndicators5Seconds`, every trading day from 2005-01-03 to 2026-10-08, sampled every minute to 2011 and every 5 seconds from 2014-12-29) and 2025's TX one-minute bars (`TaiwanFuturesKBar`); of these only per-day realized variances (`data/derived/vol4_rv.csv`) are committed. See [`data/README.md`](data/README.md).

## License

Text, code and notebooks are released under the [MIT License](LICENSE). Market data come from FinMind and are not redistributed here: `data/raw/` and the labs' `data/` folders are rebuilt with your own FinMind token (`./build.sh --fetch`), and only derived results are committed.

## Disclaimer

A personal study project. Educational material only; nothing here is investment advice.
