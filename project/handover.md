# 交接：Volume VI（LM32–LM35）Stage 2–4，目標 edition 0.7

> **建立日期**：2026-11-07　|　**上一段做完的事**：Volume V（LM27–LM31）完成 Stage 3、4，以 edition 0.6 上線（`66c636e`）。
> **性質**：接手用文件，會過期，每段重寫（歷史交給 git 與 `reviews/`）。
> 為什麼做看 `project/SPEC.md` 與 `plans/ROADMAP.md`，怎麼做看 `CLAUDE.md` 與 `AUTHORING.md`，待辦看 kata（`kata list`）。
> 本檔不放 `docs/`：那裡是 GitHub Pages 的站台輸出，放進去的 .md 會公開上網。

## 0. 三十秒版本

- Volume VI 的 Stage 2（四位 writer 起草 LM32–LM35）**只在 Benjamin 下令後開始**。他希望下一週完成 Volume VI，
  以 **edition 0.7** 出版；同一版要一起套用 Volume V 留下的 Stage 4 項目（第 3 節）。
- 待辦都在 kata：`vtr7`（Benjamin 下令）→ `0n3s`（Stage 2）→ `cgpp`（Stage 3）→ `fpst`（Stage 4 與 0.7 出版）；
  全書完成後的排版細節是 `d9v8`，選做的是 `jwfw`、`0st8`，Volume VII–IX 是 `kata list` 裡標 `roadmap` 的任務。
- 開工前先讀 `plans/ROADMAP.md` 的「How a batch runs」、`plans/vol-5.md` 的共同決策到 Stage 4 清單（1–935 行），以及 `reviews/lm27.md` …
  `lm31.md`：Volume V 在 Stage 3 改過的規則，Volume VI 的 brief 已同步（第 4 節）。

## 1. 現在的狀態

- **已上線**：LM1–LM31、Getting Started、Research hygiene；<https://quantmath.fintools.tw>（`main` 的 `docs/`）。
  首頁顯示 Edition 0.6 (7 November 2026)。
- **Volume VI 的計畫已就緒**（Stage 1 完成，2026-10-31 經整體 fresh check）：
  - brief 在 `plans/vol-6.md`：LM32 13–907 行、LM33 908–1716、LM34 1717–2655、LM35 2656–3653。
  - spine 在 `plans/vol-5.md`：LM32 1148–1193、LM33 1194–1235、LM34 1236–1278、LM35 1279–1324。
  - anchors 在 `plans/vol-6-anchors.md`：LM32 13–165、LM33 166–336、LM34 337–383、LM35 384–545。
    腳本是 `data/vol6_anchors_lm32.py` … `lm35.py`，輸出必須與表格逐字一致。
  - lab 資料：`data/make_lab_data.py` 已寫好 LM32_lab … LM35_lab。processed 檔缺的時候，它會自己先跑 builder。
- **資料**：`data/raw/` 已在本機（git-ignored），環境變數有 `FINMIND_TOKEN`。
- **版控**：`main` 與 `origin/main` 同步。edition 0.6 的 commit 是 `66c636e`，本檔與 `CLAUDE.md`
  的指向在它之後一起 commit；之後工作樹乾淨。

可直接執行的檢查（從 repo 根目錄）：

```bash
PYTHONUTF8=1 uv run python data/vol6_anchors_lm35.py      # 印出 A35-xx；與 plans/vol-6-anchors.md 的 Value 欄比對
uv run python build/build.py --preview                    # 草稿建到 dist/preview/（git-ignored）
uv run python build/qa/check_terms.py                     # 必須 clean
npx --yes markdownlint-cli2 plans/vol-6.md                 # 必須 0 issues
```

## 2. 立刻要做（Benjamin 下令後）：Volume VI Stage 2

照 `plans/ROADMAP.md`「How a batch runs」的「Stage 2, writing」做（kata `0n3s`）：四位 writer 同時在主 checkout 裡各改自己的檔案，編輯在 `main` 上重跑所有
gate 後 commit。Volume V 用過的 workflow 腳本可以當範本，但不能整批把 `vol-5` 換成 `vol-6`：共同決策與
spine 仍在 `plans/vol-5.md`（`plans/vol-6.md` 開頭也這樣說）。要換的只有 brief 檔（`plans/vol-6.md`）、anchors 檔
（`plans/vol-6-anchors.md`）、anchor 腳本前綴（`data/vol6_anchors_lmNN.py`）、各行號範圍、標題，以及
「Volume V, edition 0.6」字樣。範本是：
`C:\Users\ben0315\.claude\projects\D--projects-Quant-math-for-beginner\d93cb476-3aaa-5c28-ac97-5585be9937e7\workflows\scripts\vol5-stage2-writers-wf_0fba92bb-ff1.js`。
其他 Stage 3 用過的腳本（round1、consolidate、revision1/2、closing、final、last、stage4-verify）都在同一資料夾。

Volume VI 特有、要寫進 writer prompt 的事：

- **LM34** 的 `data/lm34_numbers.py` 要把 60 個設定的每日淨報酬寫到 `data/processed/lm34_grid.parquet`。
  寫出之前，`make_lab_data.py` 每次都會印出 `skipped labs/LM34_lab/data/lm34_grid.csv …`；寫出後才會產生
  `lm34_grid.csv`，再由編輯跑一次 `uv run python data/make_lab_data.py`（只有編輯能跑，writer 同時跑會互相碰撞）。
- **Volume V 已出版**：Volume VI 引用 LM27–LM31 的數字時，以已出版的 `src/lm27.md` … `lm31.md` 為準。
  anchors 表是計畫，Stage 3 之後以模組與它們的 numbers script 為準。
- **LM35**：週報酬在 wealth frame 上複利，並剔除 0050 停牌跨越的 2025-W24、W25（498 週）。brief 與 A35-25
  已改；writer 不要回到 estimation frame。
- **LM34**：TR23 的兩個規則（日比例縮放、Kelly walk-forward）在**下一個收盤**交易
  （A34-16 15.08%、A34-17 22.27%）。在訊號當天的收盤交易是 E5 的錯誤，不能拿來當可交易版本。

判讀 checklist（Volume V 的正常值）：

| 看什麼 | 正常值 | 偏離時 |
|:--|:--|:--|
| style.py 的 prose words（初稿） | 5,4xx–5,499，0 FAIL | 超過 5,500：要 writer 先刪，不要等審查 |
| numbers script | 初稿 282–429 項全過、anchor differences 0 | 有差異：寫 anchor 列與原因，不要硬改 |
| PDF | 初稿 30–31 頁（出版時 31–33）、scale 1.0000 | scale < 1：用 `print_width.py` 找太寬的元素 |
| lab | 0 個 error output | 有錯：看是否缺 `labs/LMNN_lab/data/` 的檔 |
| overflow / display_scroll（400 px） | 無輸出 / 0 scroll | 公式拆行（`aligned`、`gathered`） |
| `git status docs` | 草稿階段不得有變動 | 有變動就 `git checkout -- docs`（見第 4 節） |

做完要回寫：`build.sh` 的 `DATA_STEPS`、`data/README.md` 的腳本表、`plans/vol-5.md` 的 Stage 2 紀錄、
`reviews/lm32.md` … `lm35.md`（開頭記草稿 commit 與 writer 偏離 brief 之處）、kata 任務（結案或留言），以及本檔。

## 3. 接著要做：Volume VI Stage 3 與 Stage 4（edition 0.7）

- **Stage 3** 照 Volume V 的流程：
  1. round 1：每模組 reviewer、blind solver、number auditor（`reviews/REVIEW_PROMPT.md`），加一位跨模組檢查。
  2. 每模組一位合併者，對 critical/major 做對抗式複核並給出精確修法。
  3. 編輯裁決，寫進 `reviews/lmNN.md`：每一項與修法都寫全，依 PITFALLS §6。
  4. 修訂 1、修訂 2，每輪由 fresh verifier 驗證，最後做跨模組複查。
  5. closing check，每一項再做對抗式第二次檢查，然後 closing fixes。
  6. fresh final check，判定 READY TO PUBLISH。
- **Stage 4** 要一起套用的項目（`plans/vol-5.md` 的「Stage 4 changes to earlier modules」標為 Waits for 0.7）：
  - leads +32…+35，依 decision G：lm01 +32 +35、lm02 +35、lm04 +33 +34、lm05 +32、lm10 +32、lm11 +34、lm18 +33、
    lm20 +34、lm21 +32、lm22 +32、lm23 +35、lm26 +35。LM27–LM31 的 front matter 已列出 32–35，出版時檢查兩個方向
    是否一致（LM32–LM35 的 prereq 對上 leads）。
  - lm19.md:359（Lo 的 65% 是他例子中的避險基金，LM33 的措辭）、lm21.md:373（LM34 的措辭）。
  - `build/make_lab04.py` 的 walk-forward：改成下一個收盤才交易。
  - lm04.md 的 MDD 正負號（選做）。
  - **LM3 的 TQQQ 例子**：Volume I 已出版的缺陷。QQQ 的還原收盤價（back-adjusted closes）每次重抓都會變，
    `data/lm03_numbers.py:313–314` 對水準值做精確 assert，所以全新 checkout 跑 `build.sh --data` 會失敗。
    修法寫在 Stage 4 清單裡；編輯計畫依 AUTHORING §11 另派獨立審查（改的是已出版內容）。
  - 各 Volume VI brief 自己的「Stage 4 for earlier modules」。
- **出版檢查**（Volume V 用過）：
  - `./build.sh --data --pdf`：src/data 與 data/derived 應該 0 變動。
  - 每頁 `overflow.py` 400 px 與 `print_width.py`。首頁安裝區塊 755 px 是已知項目，全書完成後才處理。
  - 站內連結 0 斷連；`grep -ac 'file:///' docs/pdf/*.pdf` 每份 0。
  - ROADMAP「Stage 4, publishing」列出的禁用字串 `git grep` 為空。
  - 兩位 fresh agent 分別驗證出版文字與 `docs/`。
  - commit 前 `git add -A docs`：新頁面、資產與 PDF 是 untracked，漏加的話 README 的連結會斷。

## 4. 這一段踩過的坑（不要再推導一次）

- **不會報錯的錯誤**
  - 在只保留共同交易日的 estimation frame 上複利週、月報酬，2025 年 6 月會少掉 0050 停牌的六個交易日。
    所有 gate 都會通過，數字卻是錯的。正解：用 wealth frame，並剔除停牌跨越的週。
    memory 也有記：joined frames keep the partner's dates。
  - 訊號在收盤 t 算出、又從收盤 t 起持有，就是 look-ahead；anchor script 照樣「重現」錯的時點。
    memory：signal close = trade close is look-ahead。
  - 只手改 anchors 表的 Value 欄、不改腳本，表格和腳本輸出就會不一致（A28-39 的例子）。
    正解：改腳本、重跑，把輸出逐字貼回。
  - 預覽版 PDF 裡有 `file:///` 連結：`dist/preview/` 沒有 `CNAME`，這是預期的；從 `docs/` 產生的正式 PDF 沒有。
- **站台**
  - 草稿階段重建 `docs/` 時，首頁會把草稿標成「In review」，push 就直接上線了。
    正解：`git checkout -- docs/index.html`，`docs/` 只在出版時改。
- **環境（Windows）**
  - Bash 工具會吃掉反斜線，Python one-liner 或 heredoc 裡的 LaTeX 會壞掉。
    正解：腳本一律用 Write 工具寫成檔再執行。
  - 用腳本產生 `reviews/` 紀錄時，要在 code span 以外跳脫 `<`、`*`、`_`。編號清單到 10 以上縮排會錯，
    改用無序清單；最後去掉行尾空白再跑 markdownlint。
  - 用量上限或登入失效會讓 workflow 的 agent 中途停下。正解：prompt 加上「從 scratch 的進度檔接續」，
    再用 `resumeFromRunId` 重跑；已完成的 agent 會直接取快取。
- **資料**
  - 免費方案有三組付費檔：`sectors_close/`、`vol4_settlement/`、`vol6/etf_snapshot__…`。
    指令是 `uv run python data/fetch_finmind.py --exclude sectors_close/ --exclude vol4_settlement/ --exclude vol6/etf_snapshot`。
  - 多位 writer 同時跑 `make_lab_data.py` 會互相碰撞：只由編輯跑。
- **流程**
  - 多位 agent 同時改同一個 plans 檔時，用 Edit 做小範圍精確替換沒問題。共享檔一律由一位 agent（或編輯）處理，
    模組 writer 只列出請求。
  - 樂詞網：查詢要匿名（通用 User-Agent，不帶 e-mail）；詞條頁沒有 session 會回 302，只讀得到搜尋頁。

## 5. 已定但未執行的決策

| 決策 | 狀態 |
|:--|:--|
| Volume VI 以 edition 0.7 出版 | 已定（owner，2026-11-07）；ROADMAP 的 VII、VIII 隨之順延為 0.8、0.9，IX 維持 1.0 |
| 0050 的 2007–2008 收盤價與配息（LM35 的 2008 重演） | owner 已核准（2026-10-31） |
| `make_lab_data.py` 缺 processed 檔時自己跑 builder | owner 已核准，已實作 |
| 2015 重演用 GLD 代替 00635U（兩個假設年份用同一組 proxy） | 已定（Stage 1 fresh check） |
| LM3 TQQQ 修正延到 0.7 | 已定（編輯），未執行；修正後另派獨立審查是編輯的計畫（AUTHORING §11） |
| 首頁安裝區塊 755 px、`book.js` 的兩個小項、LM6 的長公式、Volume I 的 92 個捲動公式 | 全書完成後一起處理（owner，2026-10-24） |
| LM31 widget 的 b₁ 保留 Unicode 下標（slider 標籤是純文字） | 決定不改 |
| LM31 的 column distance 用組合詞「行向量距離」，不用數學名詞的「行距離」（多半是編碼理論的術語，未驗證；又會被讀成「行距」） | 決定不改，SOURCES 有記錄 |
| `fetch_finmind.py`、Getting Started、首頁套件清單、Volume II lab 指令的小修正（Stage 3 發現，`5516bb4`、`66c636e`） | 已做；2026-11-07 在對話中向 owner 回報，他若不同意再改回 |

## 6. 之後的路

Volume VI 出版後是 batch 5（Volume VII 隨機微積分，0.8）、batch 6（Volume VIII 凱利與最佳槓桿，0.9）、
batch 7（Volume IX Capstone，1.0）。每個 batch 開始前，先處理 `plans/ROADMAP.md` 末尾的 owner 待決事項；
新套件與新資料集要先經 owner 的 capability check 核准。

## 版本紀錄

| 版本 | 日期 | 變更 |
|:--|:--|:--|
| 1 | 2026-11-07 | 首版：Volume V 出版後，交接 Volume VI |
| 2 | 2026-11-14 | 待辦改由 kata 管理：`TODO.md` 刪除，流程說明移到 `plans/ROADMAP.md`「How a batch runs」 |
