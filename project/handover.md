# 交接：Volume VI（LM32–LM35）Stage 3–4，目標 edition 0.7

> **建立日期**：2026-11-15　|　**上一段做完的事**：Volume VI 的 Stage 2，草稿 LM32–LM35 加上 Stage 2 內的檢查與程式碼審查
> （commit 見第 1 節）。
> **性質**：接手用文件，會過期，每段重寫（歷史交給 git 與 `reviews/`）。
> 為什麼做看 `project/SPEC.md` 與 `plans/ROADMAP.md`，怎麼做看 `CLAUDE.md` 與 `AUTHORING.md`，待辦看 kata（`kata list`）。
> 本檔不放 `docs/`：那裡是 GitHub Pages 的站台輸出，放進去的 .md 會公開上網。

## 0. 三十秒版本

- Volume VI 的四份草稿都在 `main`，在 `main` 上重跑過的每一道 gate 都通過。下一步是 **Stage 3**（kata `cgpp`）：
  審查、修訂到 READY TO PUBLISH，然後 **Stage 4**（`fpst`）：與 Volume V 留下的項目一起以 **edition 0.7** 出版。
- 開工前讀：`plans/vol-5.md` 的「Stage 2 of Volume VI (2026-11-15)」（編輯對 writer 問題的裁決、已排定給 Stage 3
  的修正），以及 `reviews/lm32.md` … `lm35.md`（writer 偏離 brief 之處、Stage 2 檢查的各項與處置）。
- 全書完成後的排版細節是 `d9v8`，選做的是 `jwfw`、`0st8`，Volume VII–IX 是 `kata list` 裡標 `roadmap` 的任務。

## 1. 現在的狀態

- **已上線**：LM1–LM31、Getting Started、Research hygiene；<https://quantmath.fintools.tw>（`main` 的 `docs/`），
  Edition 0.6 (7 November 2026)。這一段沒有動 `docs/`。
- **Volume VI 草稿**（Stage 2 完成）：
  - 草稿 commit `c57f7eb`；程式碼審查後的檢查強化是 `b520775`，複審後 LM34 再改的是 `7bcc00f`（文字沒動，review 紀錄的行號仍然有效）。
  - 每模組的檔案：`src/lm3N.md`、`src/lm3N.js`、`src/data/lm3N-*.json`、`data/lm3N_common.py` / `_charts.py` /
    `_numbers.py`、`build/make_lab3N.py`、`labs/LM3N_lab/`。`build.sh` 的 `DATA_STEPS` 與 `data/README.md` 已列入。
  - 編輯重跑的結果（強化後）：正文 5,678 / 5,498 / 5,498 / 5,497 字；PDF 34 / 34 / 32 / 31 頁，scale 1.0000；
    anchor 差異 0（220 列）；lab 重新產生、執行後與 commit 的輸出逐格相同；`make_lab_data.py --check` 全部 ok。
    numbers script 的檢查數見 `plans/vol-5.md` 的 Stage 2 紀錄。
- **brief 與 anchors**：`plans/vol-6.md`、`plans/vol-6-anchors.md` 維持 Stage 1 的版本。照 Volume V 的慣例，
  writer 的偏離記在 review 紀錄，不回寫 brief；從 Stage 3 起以模組與它的 numbers script 為準。
- **資料**：`data/raw/` 在本機（git-ignored），環境變數有 `FINMIND_TOKEN`。LM32 與 LM35 的 lab 需要 5 秒 TAIEX
  的指定日期（`data/raw/intraday/taiex5s/`，本機已有）。
- **版控**：`main` 與 `origin/main` 同步，工作樹乾淨。

可直接執行的檢查（從 repo 根目錄）：

```bash
PYTHONUTF8=1 uv run python data/lm33_charts.py && PYTHONUTF8=1 uv run python data/lm33_numbers.py   # 每模組先 charts 再 numbers
uv run python build/build.py lm33                          # 草稿建到 dist/preview/（git-ignored）
uv run python build/qa/check_terms.py                      # 必須 clean
npx --yes markdownlint-cli2 reviews/lm33.md                 # 必須 0 issues
```

## 2. 立刻要做：Volume VI Stage 3（kata `cgpp`）

照 `plans/ROADMAP.md`「How a batch runs」的「Stage 3, review」與 Volume V 的流程：

1. round 1：每模組 reviewer、blind solver、number auditor（`reviews/REVIEW_PROMPT.md`），加一位跨模組檢查。
2. 每模組一位合併者，對 critical/major 做對抗式複核並給出精確修法。
3. 編輯裁決，寫進 `reviews/lmNN.md`：每一項與修法都寫全，依 PITFALLS §6。
4. 修訂 1、修訂 2，每輪由 fresh verifier 驗證，最後做跨模組複查。
5. closing check，每一項再做對抗式第二次檢查，然後 closing fixes。
6. fresh final check，判定 READY TO PUBLISH。

Volume V 的 Stage 3 腳本（round1、consolidate、revision1/2、closing、final、last、stage4-verify）在
`C:\Users\ben0315\.claude\projects\D--projects-Quant-math-for-beginner\d93cb476-3aaa-5c28-ac97-5585be9937e7\workflows\scripts\`；
Volume VI 的 Stage 2 腳本（lessons digest、writers）在本 session 的
`C:\Users\ben0315\.claude\projects\D--projects-Quant-math-for-beginner\3131c0c8-9c9d-4c42-90ad-4b8c01f01710\workflows\scripts\`。
換 vol-6 時只換 brief 檔、anchors 檔、行號、標題；共同決策與 spine 仍在 `plans/vol-5.md`。

Stage 2 已排定給 Stage 3 的修正（`plans/vol-5.md` 的 Stage 2 紀錄；修訂時一起做）：

- LM32 §7（`src/lm32.md:381`）改成「what each lost on 7 April 2025 is [[LM35]]'s」；LM35 沒有印 R7 在 2020-03-19 的損失。
- LM32 與 LM35 的 lab 方塊在標準四句之後加一句，比照 LM26，給 `fetch_intraday.py --series taiex5s --dates …` 指令。
- LM32 是 5,678 字：先做不刪內容的縮減（例如四句「not in this book」合成一句）。
- LM35 的 References 可以印 Kupiec 的縮寫 P. H.（Crossref，SOURCES 已記）。
- **修訂時的規則**：同一句裡兩個計算數字互換，numbers script 抓不到（次數不變；複審重現過）。所以修訂寫到或改到
  含兩個以上計算數字的句子時，要在 numbers script 加一條用計算值組出的 `has()` 整句檢查（PITFALLS §5）。

Stage 2 留下、交給審查判斷的：每份 review 紀錄的「Lessons not met」與「Off the regular path」。

判讀 checklist（Volume VI Stage 2 的正常值）：

| 看什麼 | 正常值 | 偏離時 |
|:--|:--|:--|
| style.py 的 prose words | 5,497–5,678，0 FAIL；Stage 3 的上限 6,000 | 超過 6,000：先刪不影響 brief 元素的句子 |
| numbers script | 全過、anchor differences 0；未涵蓋的數字等於 allowlist | 新數字未涵蓋：補檢查或寫進 allowlist 並附理由 |
| PDF | 31–34 頁、scale 1.0000（上限 36） | scale < 1：用 `print_width.py` 找太寬的元素 |
| lab | 0 個 error output | 有錯：看是否缺 `labs/LMNN_lab/data/` 的檔 |
| overflow / display_scroll（400 px） | 無輸出 / 0 scroll | 公式拆行（`aligned`、`gathered`） |
| `git status docs` | 草稿階段不得有變動 | 有變動就 `git checkout -- docs` |

## 3. 接著要做：Stage 4 與 edition 0.7（kata `fpst`）

- **Stage 4** 要一起套用的項目（`plans/vol-5.md` 的「Stage 4 changes to earlier modules」標為 Waits for 0.7）：
  - leads +32…+35，依 decision G：lm01 +32 +35、lm02 +35、lm04 +33 +34、lm05 +32、lm10 +32、lm11 +34、lm18 +33、
    lm20 +34、lm21 +32、lm22 +32、lm23 +35、lm26 +35。出版時檢查兩個方向是否一致（LM32–LM35 的 prereq 對上 leads）。
  - lm19.md:359（Lo 的 65% 是他例子中的避險基金，LM33 的措辭）、lm21.md:373（LM34 的措辭）。
  - `build/make_lab04.py` 的 walk-forward：改成下一個收盤才交易。
  - lm04.md 的 MDD 正負號（選做）。
  - **LM3 的 TQQQ 例子**：QQQ 的還原收盤價每次重抓都會變，`data/lm03_numbers.py:313–314` 對水準值做精確 assert，
    全新 checkout 跑 `build.sh --data` 會失敗。修法在 Stage 4 清單；改的是已出版內容，依 AUTHORING §11 另派獨立審查。
  - 各 Volume VI brief 自己的「Stage 4 for earlier modules」。
  - Stage 2 新增：AUTHORING §9 記下 LM32、LM35 lab 方塊多的那一句，Getting Started 給指定日期的下載指令；
    `make_lab_data.py` 的 LM35_lab 可拿掉 notebook 沒讀的 `0050_daily_raw.csv`、`0050_dividends.csv`（選做）。
- **出版檢查**（Volume V 用過）：
  - `./build.sh --data --pdf`：src/data 與 data/derived 應該 0 變動。
  - 每頁 `overflow.py` 400 px 與 `print_width.py`。首頁安裝區塊 755 px 是已知項目，全書完成後才處理。
  - 站內連結 0 斷連；`grep -ac 'file:///' docs/pdf/*.pdf` 每份 0。
  - ROADMAP「Stage 4, publishing」列出的禁用字串 `git grep` 為空。
  - 兩位 fresh agent 分別驗證出版文字與 `docs/`。
  - commit 前 `git add -A docs`：新頁面、資產與 PDF 是 untracked，漏加的話 README 的連結會斷。

## 4. 這一段踩過的坑（不要再推導一次）

- **不會報錯的錯誤**
  - numbers script 只檢查「印出的字串出現在文中某處」時，同一數字印兩次、改錯其中一處照樣全過；短整數會被頁碼或
    日期滿足，無號的值會被帶號的滿足。四支腳本已強化（帶號比對、重複字串給確切次數、未涵蓋的數字等於 allowlist），
    PITFALLS §5 與 memory 都有記。正解：改完文字就跑 numbers script，新數字要補檢查；懷疑腳本時做突變測試。
  - 在只保留共同交易日的 estimation frame 上複利週、月報酬，會少掉 0050 停牌的交易日（memory：joined frames
    keep the partner's dates）；訊號在收盤 t 算出又從收盤 t 起持有就是 look-ahead（memory 有記）。
  - 只手改 anchors 表的 Value 欄、不改腳本，表格和腳本輸出就會不一致。正解：改腳本、重跑，把輸出逐字貼回。
  - 預覽版 PDF 裡有 `file:///` 連結是預期的；從 `docs/` 產生的正式 PDF 沒有。
- **審查路由**
  - Codex 額度用完時（這一段遇到，恢復時間是 2026-11-17），照全域規則改派 fresh `opus` subagent 找碴審 diff，
    通過視同 Codex 通過。companion script 的 `adversarial-review` 會把 `--help` 當成 focus 文字，直接開始審查。
  - 這個 repo 的 stop review gate 沒開（`codex-companion.mjs setup --json` 的 `reviewGateEnabled: false`）。
- **站台**
  - 草稿階段重建 `docs/` 時首頁會把草稿標成「In review」，push 就直接上線。正解：`git checkout -- docs`。
- **環境（Windows）**
  - Bash 工具會吃掉反斜線：腳本一律用 Write 工具寫成檔再執行。
  - 用腳本產生 `reviews/` 紀錄時，在 code span 以外跳脫 `<`、`*`、`_`（反斜線也要加倍）；用無序清單；去掉行尾空白。
    Stage 2 的產生腳本是 scratch 的 `stage2/mkreviews.py`（scratch 會被清掉，要用就照它的做法重寫）。
  - 用量上限或登入失效會讓 workflow 的 agent 中途停下。正解：prompt 加上「從 scratch 的進度檔接續」，
    再用 `resumeFromRunId` 重跑。
- **資料**
  - 多位 writer 同時跑 `make_lab_data.py` 會互相碰撞：只由編輯跑。`lm34_numbers.py` 寫 `processed/lm34_grid.parquet`，
    `make_lab_data.py` 要在它之後跑。
  - 免費方案有三組付費檔：`sectors_close/`、`vol4_settlement/`、`vol6/etf_snapshot__…`。
- **流程**
  - Stage 2 內加一道 fresh 檢查（brief 覆蓋、數字覆蓋、45 項 Volume V 教訓）再讓 writer 補正，四模組共抓到 114 項
    （2 critical、13 major）。Volume VII 照做。
  - 樂詞網：查詢要匿名（通用 User-Agent，不帶 e-mail），約一秒一次；結果寫進 SOURCES 的 Volume VI 術語表。

## 5. 已定但未執行的決策

| 決策 | 狀態 |
|:--|:--|
| Volume VI 以 edition 0.7 出版 | 已定（owner，2026-11-07）；ROADMAP 的 VII、VIII 隨之順延為 0.8、0.9，IX 維持 1.0 |
| LM3 TQQQ 修正延到 0.7 | 已定（編輯），未執行；修正後另派獨立審查（AUTHORING §11） |
| 首頁安裝區塊 755 px、`book.js` 的兩個小項、LM6 的長公式、Volume I 的 92 個捲動公式 | 全書完成後一起處理（owner，2026-10-24） |
| LM31 widget 的 b₁ 保留 Unicode 下標；LM31 的「行向量距離」 | 決定不改，SOURCES 有記錄 |
| Stage 2 對 writer 問題的裁決（字數、表格、無 anchor 的數字、種子、標籤、術語等） | 已定（編輯，2026-11-15），見 `plans/vol-5.md` 的 Stage 2 紀錄 |

## 6. 之後的路

Volume VI 出版後是 batch 5（Volume VII 隨機微積分，0.8）、batch 6（Volume VIII 凱利與最佳槓桿，0.9）、
batch 7（Volume IX Capstone，1.0）。每個 batch 開始前，先處理 `plans/ROADMAP.md` 末尾的 owner 待決事項；
新套件與新資料集要先經 owner 的 capability check 核准。

## 版本紀錄

| 版本 | 日期 | 變更 |
|:--|:--|:--|
| 1 | 2026-11-07 | 首版：Volume V 出版後，交接 Volume VI |
| 2 | 2026-11-14 | 待辦改由 kata 管理：`TODO.md` 刪除，流程說明移到 `plans/ROADMAP.md`「How a batch runs」 |
| 3 | 2026-11-15 | Volume VI Stage 2 完成，交接 Stage 3–4 |
