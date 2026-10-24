# From Calculus to Kelly｜從微積分到凱利準則

[English](README.md) | **繁體中文**

這是個人自學量化金融的專案，從大一微積分、統計學與線性代數出發，逐步走向統計建模、投資組合最佳化，以及考量估計誤差的凱利部位配置。完整課程規劃為 **9 卷、50 個 Learning Modules**；目前已發布 **第 I–IV 卷（LM1–LM26）**。

教材以英文撰寫，搭配繁體中文導讀。已發布的每個模組均有網頁章節、A4 PDF，以及保留執行輸出的 Jupyter Lab。範例結合台股與美股市場資料，並明確標示模型、模擬及建構案例。

**[線上閱讀](https://quantmath.fintools.tw)** · [開始學習](https://quantmath.fintools.tw/getting-started.html) · [研究可信度與資料使用原則](https://quantmath.fintools.tw/research-hygiene.html)

## 目前進度

README 更新日期：**2026-10-24**。教材最新版本：**Edition 0.5（2026-10-20）**，以[課程目錄](src/syllabus.yaml)的版本紀錄為準。

| 卷 | 主題 | 模組 | 狀態 |
|:--|:--|:--|:--|
| I | 金融微積分 | LM1–LM7 | 已發布 |
| II | 投資組合線性代數 | LM8–LM12 | 已發布 |
| III | 機率 | LM13–LM18 | 已發布 |
| IV | 統計推論與計量經濟學 | LM19–LM26 | 已發布 |
| V | 投資組合最佳化 | LM27–LM31 | 規劃中 |
| VI | 衡量真實風險與報酬 | LM32–LM35 | 規劃中 |
| VII | 隨機微積分 | LM36–LM40 | 規劃中 |
| VIII | 凱利準則與最適槓桿 | LM41–LM46 | 規劃中 |
| IX | 整合專題 | LM47–LM50 | 規劃中 |

Edition 0.5 新增統計推論、迴歸、貝氏收縮與時間序列模型，涵蓋波動率建模。後續投資組合、風險、隨機微積分、進階凱利與整合專題仍屬規劃，尚未發布。

目前工作順序見 [TODO.md](TODO.md)，後續卷別見[課程路線圖](plans/ROADMAP.md)。

## 如何開始

1. 先讀 **Getting Started**，了解先備知識、符號與 Lab 操作方式。
2. 依模組順序學習，或沿各章的先修連結補足基礎。
3. 先完成學習目標、範例與練習題，再對照解答。
4. 重現 Lab 結果，並依 **Research hygiene** 檢視資料與模型假設。

上方語言切換僅適用於 README；教材正文維持英文搭配「中文導讀」。下表保留英文原章名，方便對照教材。

## 已發布模組

下列連結指向儲存庫內的網頁產物、PDF 與 Lab 資料夾。閱讀網頁請使用上方的線上網站。

| 模組 | 狀態 | HTML | PDF | Lab |
|:--|:--|:--|:--|:--|
| 課程路線圖、目錄與符號 | 已發布 | [`docs/index.html`](docs/index.html) | — | — |
| LM1 Exponentials, Logarithms and Compounding | 已發布 | [`docs/lm/lm01.html`](docs/lm/lm01.html) | [`docs/pdf/LM01_…pdf`](docs/pdf/LM01_Exponentials_Logarithms_and_Compounding.pdf) | [`labs/LM01_lab`](labs/LM01_lab) |
| LM2 Limits and Derivatives | 已發布 | [`docs/lm/lm02.html`](docs/lm/lm02.html) | [`docs/pdf/LM02_…pdf`](docs/pdf/LM02_Limits_and_Derivatives.pdf) | [`labs/LM02_lab`](labs/LM02_lab) |
| LM3 Taylor Series and Approximation | 已發布 | [`docs/lm/lm03.html`](docs/lm/lm03.html) | [`docs/pdf/LM03_…pdf`](docs/pdf/LM03_Taylor_Series_and_Approximation.pdf) | [`labs/LM03_lab`](labs/LM03_lab) |
| LM4 Optimization in One Variable | 已發布 | [`docs/lm/lm04.html`](docs/lm/lm04.html) | [`docs/pdf/LM04_…pdf`](docs/pdf/LM04_Optimization_in_One_Variable.pdf) | [`labs/LM04_lab`](labs/LM04_lab) |
| LM5 Integration | 已發布 | [`docs/lm/lm05.html`](docs/lm/lm05.html) | [`docs/pdf/LM05_…pdf`](docs/pdf/LM05_Integration.pdf) | [`labs/LM05_lab`](labs/LM05_lab) |
| LM6 Sequences, Series and the Time Value of Money | 已發布 | [`docs/lm/lm06.html`](docs/lm/lm06.html) | [`docs/pdf/LM06_…pdf`](docs/pdf/LM06_Sequences_Series_and_the_Time_Value_of_Money.pdf) | [`labs/LM06_lab`](labs/LM06_lab) |
| LM7 Multivariable Calculus and Lagrange Multipliers | 已發布 | [`docs/lm/lm07.html`](docs/lm/lm07.html) | [`docs/pdf/LM07_…pdf`](docs/pdf/LM07_Multivariable_Calculus_and_Lagrange_Multipliers.pdf) | [`labs/LM07_lab`](labs/LM07_lab) |
| LM8 Vectors and Matrices | 已發布 | [`docs/lm/lm08.html`](docs/lm/lm08.html) | [`docs/pdf/LM08_…pdf`](docs/pdf/LM08_Vectors_and_Matrices.pdf) | [`labs/LM08_lab`](labs/LM08_lab) |
| LM9 Linear Systems, Inverses and Rank | 已發布 | [`docs/lm/lm09.html`](docs/lm/lm09.html) | [`docs/pdf/LM09_…pdf`](docs/pdf/LM09_Linear_Systems_Inverses_and_Rank.pdf) | [`labs/LM09_lab`](labs/LM09_lab) |
| LM10 Quadratic Forms and Covariance Matrices | 已發布 | [`docs/lm/lm10.html`](docs/lm/lm10.html) | [`docs/pdf/LM10_…pdf`](docs/pdf/LM10_Quadratic_Forms_and_Covariance_Matrices.pdf) | [`labs/LM10_lab`](labs/LM10_lab) |
| LM11 Eigen-decomposition and PCA | 已發布 | [`docs/lm/lm11.html`](docs/lm/lm11.html) | [`docs/pdf/LM11_…pdf`](docs/pdf/LM11_Eigen_decomposition_and_PCA.pdf) | [`labs/LM11_lab`](labs/LM11_lab) |
| LM12 Cholesky, SVD and Least Squares | 已發布 | [`docs/lm/lm12.html`](docs/lm/lm12.html) | [`docs/pdf/LM12_…pdf`](docs/pdf/LM12_Cholesky_SVD_and_Least_Squares.pdf) | [`labs/LM12_lab`](labs/LM12_lab) |
| LM13 Probability Foundations and Bayes | 已發布 | [`docs/lm/lm13.html`](docs/lm/lm13.html) | [`docs/pdf/LM13_…pdf`](docs/pdf/LM13_Probability_Foundations_and_Bayes.pdf) | [`labs/LM13_lab`](labs/LM13_lab) |
| LM14 Random Variables, Expectation and Jensen's Inequality | 已發布 | [`docs/lm/lm14.html`](docs/lm/lm14.html) | [`docs/pdf/LM14_…pdf`](docs/pdf/LM14_Random_Variables_Expectation_and_Jensen_s_Inequality.pdf) | [`labs/LM14_lab`](labs/LM14_lab) |
| LM15 Distributions in Finance | 已發布 | [`docs/lm/lm15.html`](docs/lm/lm15.html) | [`docs/pdf/LM15_…pdf`](docs/pdf/LM15_Distributions_in_Finance.pdf) | [`labs/LM15_lab`](labs/LM15_lab) |
| LM16 Joint Distributions and Dependence | 已發布 | [`docs/lm/lm16.html`](docs/lm/lm16.html) | [`docs/pdf/LM16_…pdf`](docs/pdf/LM16_Joint_Distributions_and_Dependence.pdf) | [`labs/LM16_lab`](labs/LM16_lab) |
| LM17 Law of Large Numbers and Central Limit Theorem | 已發布 | [`docs/lm/lm17.html`](docs/lm/lm17.html) | [`docs/pdf/LM17_…pdf`](docs/pdf/LM17_Law_of_Large_Numbers_and_Central_Limit_Theorem.pdf) | [`labs/LM17_lab`](labs/LM17_lab) |
| LM18 Monte Carlo Simulation and the Bootstrap | 已發布 | [`docs/lm/lm18.html`](docs/lm/lm18.html) | [`docs/pdf/LM18_…pdf`](docs/pdf/LM18_Monte_Carlo_Simulation_and_the_Bootstrap.pdf) | [`labs/LM18_lab`](labs/LM18_lab) |
| LM19 Descriptive Statistics of Returns | 已發布 | [`docs/lm/lm19.html`](docs/lm/lm19.html) | [`docs/pdf/LM19_…pdf`](docs/pdf/LM19_Descriptive_Statistics_of_Returns.pdf) | [`labs/LM19_lab`](labs/LM19_lab) |
| LM20 Estimation Theory and Maximum Likelihood | 已發布 | [`docs/lm/lm20.html`](docs/lm/lm20.html) | [`docs/pdf/LM20_…pdf`](docs/pdf/LM20_Estimation_Theory_and_Maximum_Likelihood.pdf) | [`labs/LM20_lab`](labs/LM20_lab) |
| LM21 Hypothesis Testing and Multiple Testing | 已發布 | [`docs/lm/lm21.html`](docs/lm/lm21.html) | [`docs/pdf/LM21_…pdf`](docs/pdf/LM21_Hypothesis_Testing_and_Multiple_Testing.pdf) | [`labs/LM21_lab`](labs/LM21_lab) |
| LM22 Resampling Methods | 已發布 | [`docs/lm/lm22.html`](docs/lm/lm22.html) | [`docs/pdf/LM22_…pdf`](docs/pdf/LM22_Resampling_Methods.pdf) | [`labs/LM22_lab`](labs/LM22_lab) |
| LM23 Linear Regression | 已發布 | [`docs/lm/lm23.html`](docs/lm/lm23.html) | [`docs/pdf/LM23_…pdf`](docs/pdf/LM23_Linear_Regression.pdf) | [`labs/LM23_lab`](labs/LM23_lab) |
| LM24 Bayesian Inference and Shrinkage | 已發布 | [`docs/lm/lm24.html`](docs/lm/lm24.html) | [`docs/pdf/LM24_…pdf`](docs/pdf/LM24_Bayesian_Inference_and_Shrinkage.pdf) | [`labs/LM24_lab`](labs/LM24_lab) |
| LM25 Time Series I: ARMA, Unit Roots and Cointegration | 已發布 | [`docs/lm/lm25.html`](docs/lm/lm25.html) | [`docs/pdf/LM25_…pdf`](docs/pdf/LM25_Time_Series_I_ARMA_Unit_Roots_and_Cointegration.pdf) | [`labs/LM25_lab`](labs/LM25_lab) |
| LM26 Time Series II: Volatility Models | 已發布 | [`docs/lm/lm26.html`](docs/lm/lm26.html) | [`docs/pdf/LM26_…pdf`](docs/pdf/LM26_Time_Series_II_Volatility_Models.pdf) | [`labs/LM26_lab`](labs/LM26_lab) |

模組須依 [AUTHORING.md](AUTHORING.md)完成獨立審查與修正驗證，才能發布。課程目錄控制正式建置納入的模組；未發布的項目只會出現在預覽版。

## 本機建置

需要透過 `uv` 管理的 Python 3.13、Node.js/npm，以及執行 `build.sh` 的 Bash（Windows 可使用 Git Bash 或 WSL）。Python 相依套件定義於 [pyproject.toml](pyproject.toml)，版本鎖定於 [uv.lock](uv.lock)。

```bash
uv sync                           # 建立 Python 環境
(cd build && npm ci)              # 安裝 KaTeX 與自託管字型
./build.sh                        # 建置 docs/ 與 dist/artifact/
./build.sh --preview              # 另外將草稿建置至 dist/preview/
uv run playwright install chromium  # 產生 PDF 前須先安裝
./build.sh --pdf                  # 另外產生 docs/pdf/ 的 A4 PDF
```

重新產生資料與 Lab 時，需要本機原始資料：

```bash
./build.sh --fetch                # 下載原始資料並重建 Lab 資料；需要 FINMIND_TOKEN
./build.sh --data                 # 重算衍生資料與圖表規格
./build.sh --labs                 # 重新產生並執行 Lab notebooks
```

第 IV 卷的日內資料須另以 `data/fetch_intraday.py` 下載；`--fetch` 不會下載這整段日內歷史。資料權限、重建步驟與驗證方式見 [data/README.md](data/README.md)。這些指令可能需要大量資料請求或較長執行時間。

只建置 HTML 時，可在安裝相依套件後執行 `uv run python build/build.py`。公式透過 KaTeX 在建置時轉為 HTML；互動圖表則使用 JavaScript。

## 專案結構

| 路徑 | 用途 |
|:--|:--|
| `src/` | 模組原稿、獨立頁面、圖表、資源與發布目錄 |
| `docs/` | 已建置網站、正式章節與 A4 PDF |
| `labs/` | 保留執行輸出的 Jupyter notebooks；輸入資料須於本機重建 |
| `data/` | 資料下載、驗證、計算與圖表產生程式 |
| `build/` | HTML／PDF 建置器、Notebook 產生器與 QA 工具 |
| `plans/` | 課程路線圖與模組寫作規劃 |
| `reviews/` | 獨立審查意見與修正驗證紀錄 |
| `project/` | 規格、已知陷阱與來源紀錄 |
| `AUTHORING.md` | 寫作、符號、審查與發布規範 |
| `TODO.md` | 目前待辦與交接狀態 |

## 寫作與檢查

章節格式、符號及發布關卡見 [AUTHORING.md](AUTHORING.md)，已確定的需求見 [project/SPEC.md](project/SPEC.md)，審查狀態見 [reviews/README.md](reviews/README.md)。原稿採用含 YAML front matter、數學公式、提示框與交叉引用的 Markdown，也可作為 Obsidian 筆記庫使用。

修改這兩份 README 時，可執行：

```bash
markdownlint-cli2 README.md README.zh-TW.md
uv run python build/qa/check_terms.py
```

發布教材模組還須完成寫作規範要求的內容、數值、Lab、版面及 PDF 檢查。

## 網站託管

網站設定於 **[quantmath.fintools.tw](https://quantmath.fintools.tw)**，由 GitHub Pages 的 `main` → `/docs` 提供內容。建置會產生靜態檔案與 `docs/CNAME`；其他靜態主機也可直接提供 `docs/` 內容。自行部署時須調整網域設定。儲存庫維護指引見 [CLAUDE.md](CLAUDE.md)。

## 資料與授權

歷史市場資料來自 **FinMind**，涵蓋台灣股票、指數、股利、期貨及美股資料。資料驗證與調整方法記錄於 [data/README.md](data/README.md)、來源清單及計算程式；參考來源見 [project/SOURCES.md](project/SOURCES.md)。

教材文字、程式與 notebooks 採用 [MIT License](LICENSE)，此授權**不包含 FinMind 資料的使用權利**。原始市場資料與 Lab 輸入資料夾不隨專案散布，須以自己的 token 與適當資料權限重建；儲存庫只提交衍生結果。`data/derived/` 中的衍生統計同樣受 FinMind 的非商業使用與來源標示條款約束，不適用 MIT 授權。本專案的 FinMind 使用權限限於非商業用途。

## 免責聲明

本專案供個人學習與教育使用，內容不構成投資建議。
