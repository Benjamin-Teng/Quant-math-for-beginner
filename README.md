# From Calculus to Kelly

**English** | [繁體中文](README.zh-TW.md)

A personal self-study project that builds from first-year calculus, statistics and linear algebra toward statistical modeling, portfolio optimization and Kelly position sizing under uncertainty. The planned curriculum spans **9 volumes and 50 Learning Modules**; **Volumes I–IV (LM1–LM26) are published**.

The textbook is written in English with Traditional Chinese reading guides. Published modules include a web chapter, an A4 PDF and a Jupyter lab with saved outputs. Examples combine Taiwan and US market data with explicitly labeled models, simulations and constructed cases.

**[Read online](https://quantmath.fintools.tw)** · [Getting Started](https://quantmath.fintools.tw/getting-started.html) · [Research hygiene](https://quantmath.fintools.tw/research-hygiene.html)

## Current progress

README updated: **2026-10-23**. Latest textbook edition: **0.5 (2026-10-20)**, as recorded in [the syllabus](src/syllabus.yaml).

| Volume | Topic | Modules | Status |
|:--|:--|:--|:--|
| I | Calculus for Finance | LM1–LM7 | Published |
| II | Linear Algebra for Portfolios | LM8–LM12 | Published |
| III | Probability | LM13–LM18 | Published |
| IV | Statistical Inference and Econometrics | LM19–LM26 | Published |
| V | Portfolio Optimization | LM27–LM31 | Planned |
| VI | Measuring True Risk and Return | LM32–LM35 | Planned |
| VII | Stochastic Calculus | LM36–LM40 | Planned |
| VIII | The Kelly Criterion and Optimal Leverage | LM41–LM46 | Planned |
| IX | Capstone | LM47–LM50 | Planned |

Edition 0.5 adds statistical inference, regression, Bayesian shrinkage and time-series models, including volatility modeling. The remaining portfolio, risk, stochastic-calculus, advanced Kelly and capstone modules are roadmap items, not published chapters.

See [TODO.md](TODO.md) for the current queue and [the roadmap](plans/ROADMAP.md) for future volumes.

## Start learning

1. Read **Getting Started** for prerequisites, notation and the lab workflow.
2. Follow the module order, or use each chapter's prerequisite links.
3. Work through the learning outcomes, examples and practice problems before checking the solutions.
4. Reproduce the lab results and compare their assumptions with the **Research hygiene** guidance.

The language switch above changes the README only. The textbook keeps its English text and 中文導讀 boxes.

## Published modules

The following links point to the repository's built chapters, PDFs and lab folders. Use the online site above to read rendered HTML.

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

A module is published only after independent review and verified fixes under [AUTHORING.md](AUTHORING.md). The syllabus controls which modules appear in the published build; unpublished entries appear only in the preview.

## Build locally

Prerequisites: Python 3.13 managed by `uv`, Node.js/npm, and Bash for `build.sh` (for example, Git Bash or WSL on Windows). Python dependencies are defined in [pyproject.toml](pyproject.toml) and pinned in [uv.lock](uv.lock).

```bash
uv sync                           # create the Python environment
(cd build && npm ci)              # install KaTeX and self-hosted fonts
./build.sh                        # build docs/ and dist/artifact/
./build.sh --preview              # also build drafts into dist/preview/
uv run playwright install chromium  # required before PDF rendering
./build.sh --pdf                  # also render A4 PDFs into docs/pdf/
```

Optional data and lab rebuilds require local source data:

```bash
./build.sh --fetch                # fetch raw data and rebuild lab data; needs FINMIND_TOKEN
./build.sh --data                 # recompute derived data and chart specifications
./build.sh --labs                 # regenerate and execute lab notebooks
```

Volume IV intraday downloads use `data/fetch_intraday.py` separately; `--fetch` does not fetch that entire history. Follow [data/README.md](data/README.md) for access requirements, reconstruction steps and verification. These commands may make substantial data requests or take time to execute.

For an HTML-only build, run `uv run python build/build.py` after installing dependencies. Formulas are rendered with KaTeX at build time; interactive charts use JavaScript.

## Repository layout

| Path | Purpose |
|:--|:--|
| `src/` | Module sources, standalone pages, figures, assets and publication syllabus |
| `docs/` | Built website, published chapters and A4 PDFs |
| `labs/` | Jupyter notebooks with saved outputs; input data are rebuilt locally |
| `data/` | Data-fetching, validation, calculation and chart-generation scripts |
| `build/` | HTML/PDF builders, notebook generators and QA tools |
| `plans/` | Roadmap and module briefs |
| `reviews/` | Independent review findings and verification records |
| `project/` | Specification, pitfalls and source records |
| `AUTHORING.md` | Writing, notation, review and publication rules |
| `TODO.md` | Current work queue and handoff |

## Authoring and checks

See [AUTHORING.md](AUTHORING.md) for the chapter format, notation and publication gates, [project/SPEC.md](project/SPEC.md) for agreed requirements, and [reviews/README.md](reviews/README.md) for review status. Sources use Markdown with YAML front matter, math, callouts and cross-references; they also serve as an Obsidian vault.

For changes to these README files:

```bash
markdownlint-cli2 README.md README.zh-TW.md
uv run python build/qa/check_terms.py
```

Module publication additionally requires the content, numerical, lab, layout and PDF checks defined in the authoring guide.

## Hosting

The published site is configured for **[quantmath.fintools.tw](https://quantmath.fintools.tw)** using GitHub Pages from `main` → `/docs`. The build produces static files and `docs/CNAME`; another static host can serve the `docs/` directory. Adjust the domain configuration for your own deployment. See [CLAUDE.md](CLAUDE.md) for repository maintenance instructions.

## Data and license

Historical market data come from **FinMind**. The project uses Taiwan stock, index, dividend and futures data, plus US stock data. Validation and adjustments are documented in [data/README.md](data/README.md), the source manifest and the calculation scripts; [project/SOURCES.md](project/SOURCES.md) records references.

Text, code and notebooks use the [MIT License](LICENSE). This license does **not** grant rights to FinMind data. Raw market data and lab input-data folders are not redistributed; rebuild them using your own token and appropriate data access. Only derived results are committed. Derived statistics in `data/derived/` also remain subject to FinMind's non-commercial-use and attribution terms; they are not covered by the MIT License. The project's FinMind access is for non-commercial use.

## Disclaimer

A personal study project for education. Nothing here is investment advice.
