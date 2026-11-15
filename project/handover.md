# 交接：Batch 5（Volume VII 隨機微積分，edition 0.8）

> **建立日期**：2026-11-15　|　**上一段做完的事**：Volume VI（LM32–LM35）的 Stage 3–4，以 edition 0.7 出版。
> **性質**：接手用文件，會過期，每段重寫（歷史交給 git 與 `reviews/`）。
> 為什麼做看 `project/SPEC.md` 與 `plans/ROADMAP.md`，怎麼做看 `CLAUDE.md` 與 `AUTHORING.md`，待辦看 kata（`kata list`）。
> 本檔不放 `docs/`：那裡是 GitHub Pages 的站台輸出，放進去的 .md 會公開上網。

## 0. 三十秒版本

- Edition 0.7 已上線：<https://quantmath.fintools.tw> 現在有 LM1–LM35。下一段是 **batch 5，Volume VII 隨機微積分
  （LM36–LM40），edition 0.8**（kata `9cpm`）。開工前先處理 `plans/ROADMAP.md` 末尾「Open decisions for the owner」，
  新套件、新資料集要先經 owner 的 capability check 核准。
- Codex 額度 2026-11-17 恢復。這一段的程式碼審查都改派 fresh opus（全域規則的備援），恢復後 diff 審查回到 Codex。
- 這一段每個步驟的紀錄：`reviews/lm32.md` … `lm35.md`（Stage 3 各輪、程式碼審查、final check）、`reviews/lm03.md`
  與 `lm04.md`（edition 0.7 的已出版內容修正）、`plans/vol-5.md` 的「Stage 3 of Volume VI」與 Stage 4 清單。

## 1. 現在的狀態

- **已上線**：LM1–LM35、Getting Started、Research hygiene；`main` 的 `docs/`，Edition 0.7（15 November 2026）。
- **Edition 0.7 帶的已出版內容修改**（都經獨立審查，紀錄如上）：
  - LM3 的 TQQQ 例子：位數改成重抓 FinMind adjusted close 也不會變；`data/lm03_numbers.py` 有帶 seed 的重抓穩定性
    檢查（每格誤差上限一分）。
  - LM4：MDD 印成正數；Lab 4 的 walk-forward 改在下一個收盤交易。
  - Volumes I–V 的 leads 補上 +32…+35（decision G，14 筆）；lm19.md 的 Lo 65%、lm21.md 的 LM34 句、lm23.md 的長期變異數；
    AUTHORING §9 的 5 秒 TAIEX 句型；Getting Started 的盤中日期與「兩個計數」；Research hygiene 的 look-ahead 標籤；
    Lab 31 的一句說明。
- **共用程式（owner 2026-11-15 核准）**：`data/make_lab_data.py` 的 `t5s_days` 只複製找得到的 5 秒日期、缺的印下載指令；
  `data/lm34_grid.py`（新）寫 `processed/lm34_grid.parquet`，只需要 E5 的 frames 與 `vol5_rules.py`，免費方案也能跑；
  它登記在 `make_lab_data.py` 的 `BUILDERS`，缺檔時會先跑它，`lm34_numbers.py` 只讀這個檔來比對。
- **資料**：`data/raw/` 在本機（git-ignored），環境變數有 `FINMIND_TOKEN`；LM32、LM35 的 lab 需要的 5 秒 TAIEX 日期在
  `data/raw/intraday/taiex5s/`。
- **版控**：見 `git log`；這一段的 commit 從 `9d9678e`（Stage 3）起。

可直接執行的檢查（從 repo 根目錄）：

```bash
bash build.sh --data --pdf                         # 出版建置：src/data 與 data/derived 應 0 變動
uv run python data/make_lab_data.py --check        # 每個 lab 的 data/ 應 "all identical"
uv run python build/qa/check_terms.py              # 必須 clean
npx --yes markdownlint-cli2 reviews/lm35.md         # 必須 0 issues
```

## 2. 下一步（待辦在 kata）

- `9cpm`：batch 5，Volume VII（LM36–LM40）的 Stage 1–4，照 `plans/ROADMAP.md`「How a batch runs」。
- `d9v8`：全書完成後一起處理的排版項目。`0st8`、`jwfw` 選做。`z2cz` 等 owner 決定（標 `human`）。
- `a305`（batch 6）已記一筆：LM35 原本把融資（margin loans）指給 LM46，Stage 3 收窄了指標，batch 6 決定 LM46 要不要教。

判讀 checklist（Volume VI 的正常值，batch 5 可對照）：

| 看什麼 | 正常值 | 偏離時 |
|:--|:--|:--|
| style.py 的 prose words | Stage 2 草稿 ≤ 5,500，Stage 3 後 5,632–5,890；上限 6,000 | 超過：先刪不影響 brief 元素的句子 |
| numbers script | 全過、anchor differences 0；未涵蓋的數字等於 allowlist | 新數字未涵蓋：補檢查或寫進 allowlist 並附理由 |
| PDF | 33–35 頁、scale 1.0000（上限 36） | scale < 1：用 `print_width.py` 找太寬的元素 |
| lab | 0 個 error output；notebook 0 個 CR 位元組 | 有 CR：nbconvert 在 Windows 寫 CRLF，轉回 LF |
| Stage 3 round 1 | 每模組 30–35 項，major 2–4 | 明顯偏多或偏少：先查 prompt 給的行號範圍對不對 |
| `git status docs` | 草稿階段不得有變動 | 有變動就 `git checkout -- docs` |

## 3. 這一段踩過的坑（不要再推導一次）

- **不會報錯的錯誤**
  - PowerShell 的 `Measure-Object -Line` 不算空行，拿它算的行號範圍會短一截：LM35 的 brief 少給了 230 行。正解：用
    Grep 的行號，或 `[System.IO.File]::ReadAllLines(path).Count`（memory 有記）。
  - 對 workflow 裡正在跑的 agent 用 `SendMessage` 不會送到它，而是從 transcript 另開一個副本；workflow 的那個實例照舊
    用錯的 prompt。正解：發現 prompt 錯就停掉重跑（`resumeFromRunId`），或跑完後做補充輪（memory 有記）。
  - 帶 seed 的穩定性檢查只在自己的 seed 上通過不算證據：LM3 第一版的模擬模型超出物理上限，換 seed 就失敗。正解：
    模擬重抓時每格誤差限在一分內，並換幾個 seed 跑（memory 有記）。
  - numbers script 只檢查「字串出現在某處」時，打錯其中一處照樣全過；兩個數字在同一句互換也會過。正解：位置比對、
    帶號比對、確切次數，修訂改到的含兩個以上計算數字的句子加整句 phrase check；選擇題的答案鍵也要綁（LM32 的程式碼
    審查抓到過）。
  - Verifier 若在共用檔 agent 之前跑，會把「等共用檔修」的項目標成 reopened。正解：共用檔改完再驗，或在紀錄裡註明
    「由同輪共用檔修改關閉」。
- **環境（Windows）**
  - Bash 工具會吃掉反斜線：腳本一律用 Write 工具寫成檔再執行。
  - PowerShell 的 here-string 沒辦法用 `git commit -F -` 從 stdin 讀：訊息會被當成 pathspec。正解：訊息寫成檔案，
    `git commit -F <file>`。
  - nbconvert 在 Windows 寫出 CRLF：執行完 lab 要轉回 LF，並檢查 CR 位元組為 0。
  - 用量上限或登入失效會讓 workflow 的 agent 中途停下。正解：prompt 加上「從 scratch 的進度檔接續」，再用
    `resumeFromRunId` 重跑。
- **對外查詢**：User-Agent 不可帶專案名稱（Volume V/VI 的 prompt 寫了 `quantmath-sourcecheck/1.0`，之後改成
  `Mozilla/5.0`）；樂詞網一秒約一次、匿名（memory 有記）。
- **資料**
  - 多位 writer 同時跑 `make_lab_data.py` 會互相碰撞：只由編輯跑。
  - 免費方案有三組付費檔：`sectors_close/`、`vol4_settlement/`、`vol6/etf_snapshot__…`。
- **紀錄**
  - Agent 依全域語言規則常用中文回報，但 `reviews/` 一律英文：寫進紀錄前要改寫成英文。
  - 產生紀錄的腳本要跳脫 code span 以外的 `\ < * _ [ ]`、把裸網址包進 code span、去掉 code span 內前後空白、各輪小標題
    不重名、用無序清單、去掉行尾空白。這一段的腳本在 scratch 的 `tools/mk_r1.py`、`mk_rev.py`、`mk_close.py`、
    `mk_final.py`（scratch 會被清掉，要用就照它們的做法重寫）。
- **站台**：草稿階段重建 `docs/` 時首頁會把草稿標成「In review」，push 就直接上線。正解：草稿階段不碰 `docs/`。
- **流程**：Stage 2 內加一道 fresh 檢查（brief 覆蓋、數字覆蓋、教訓清單）再讓 writer 補正，Volume VI 四模組共抓到
  114 項；Stage 3 仍抓到 11 項 major，兩道都值得。Volume VII 照做。

## 4. 已定的決策

| 決策 | 狀態 |
|:--|:--|
| Volume VI 以 edition 0.7 出版 | 已執行（2026-11-15） |
| `t5s_days` 跳過缺的日期；LM34 grid 由 `BUILDERS` 建 | owner 核准（2026-11-15），已執行 |
| 後出的 Glossary 列重用前面模組的詞、意思不同時，加 "Here, …" 限定 | 已定（編輯，Stage 3） |
| 規則的圖表配色各圖自訂、以圖例為準；LM35 的基金配色沿用 Volume V | 已定（編輯，Stage 3） |
| lm25→34、lm32→33、lm32→34 三個只靠前向指標的 lead 保留 | 已定（decision C9），記在 Stage 4 清單 |
| LM35_lab 不讀的兩個 0050 檔（`make_lab_data.py`）不拿掉 | 決定不做：只多兩個檔，拿掉要改共用程式 |
| 首頁安裝區塊 755 px、`book.js` 的小項、LM6 的長公式、Volume I 的 92 個捲動公式 | 全書完成後一起處理（kata `d9v8`） |
| `build.sh --data` 的 `fetch_finmind.py --verify` 在免費方案會因缺付費檔失敗 | 已知、未處理：屬 fetch_finmind 的架構，owner 的決定 |
| LM31 widget 的 b₁ 保留 Unicode 下標；LM31 的「行向量距離」 | 決定不改，SOURCES 有記錄 |

## 5. 之後的路

Batch 5（Volume VII 隨機微積分，0.8）→ batch 6（Volume VIII 凱利準則與最佳槓桿，0.9）→ batch 7（Volume IX
Capstone，1.0）。Volume VII 的 Stage 1 照 Volume V/VI 的做法：spine、capability check、資料、brief 與 anchors、
lab data、Stage 1 的 fresh 檢查。

## 版本紀錄

| 版本 | 日期 | 變更 |
|:--|:--|:--|
| 1 | 2026-11-07 | 首版：Volume V 出版後，交接 Volume VI |
| 2 | 2026-11-14 | 待辦改由 kata 管理：`TODO.md` 刪除，流程說明移到 `plans/ROADMAP.md`「How a batch runs」 |
| 3 | 2026-11-15 | Volume VI Stage 2 完成，交接 Stage 3–4 |
| 4 | 2026-11-15 | Volume VI 以 edition 0.7 出版，交接 batch 5 |
