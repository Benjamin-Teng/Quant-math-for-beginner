# Sources consulted

Every website and data service used while building edition 0.1 and the Volume I drafts (2026-10-10), extracted from
the session logs of the editor and all writer, reviewer and data agents. Each module's own References section is the
authoritative citation list; this file shows where facts were checked, so the next session can go straight to the
right page. Pages consulted for edition 0.1 that no current text cites are left out.

## Market data

| Service | Used for |
|:--|:--|
| FinMind `TaiwanStockPrice` | 0050, 00631L, 00679B daily closes and spreads; TAIEX daily closes; 2330 and 2317 around 30 June 2025 |
| FinMind `TaiwanStockDividendResult` | 0050 and 00679B ex-dates, before/after prices, cash dividends |
| FinMind `TaiwanFuturesDaily` | TX (and MTX for a cross-check), every contract month, April–October 2025 |
| FinMind `TaiwanStockTotalReturnIndex` | TAIEX total-return index (LM6 dividend measurement) |
| FinMind `USStockPrice` | QQQ and TQQQ, calendar 2022 (LM3) |
| FinMind `InterestRate` | tried for Taiwan's policy rate: not available (Fed, ECB and others only) |
| FinMind `TaiwanVariousIndicators5Seconds` | tried for TAIEX intraday on 2025-06-30; from Volume II, TAIEX's official 13:30:00 close on the 52 dates whose spread prints 0.0 |
| FinMind `TaiwanStockEvery5SecondsIndex` | the official 13:30:00 close of a TWSE sector index, one date per request; the 561 closes that repair FinMind's copied sector values (Volume II) |
| FinMind `TaiwanStockInfo` | which index ids FinMind serves: none for the four sector indices TWSE launched on 30 June 2023 (`DigitalCloudServices` has no id and no `TaiwanStockPrice` rows; MCP query, 2026-10-12) |
| TWSE `rwd/zh/TAIEX/MI_5MINS_HIST` (JSON) | TAIEX daily high/low around 27–30 June 2025 |
| FinMind `TaiwanFuturesDaily`, TX, whole history | TX23 (LM25's basis): every TX row from 1998-07-21 in one call; sessions, expiry-day zeros and the `spread` rule below (2026-10-19) |
| FinMind `TaiwanFuturesFinalSettlementPrice` | an optional cross-check of TX expiries (Backer); whole years missing, below |
| FinMind `TaiwanVariousIndicators5Seconds` | T5S (LM26's realized variance): the TAIEX every 5 seconds (earlier every minute, 15 and 10 seconds), 2005-01-03 → 2026-10-08, one day per request; regimes and the closing-auction freeze below |
| FinMind `TaiwanFuturesKBar` | option E: TX 1-minute bars for 2025 (Sponsor); night-session dating below |
| FinMind `TaiwanStockTradingDate` | the calendar check of TX23: 1999-01-05 → 2026-12-31, including 52 future dates and the 1999–2000 Saturday sessions, so filter it to dates on or before the retrieval date |
| FinMind `InterestRate`, `GovernmentBondsYield` | tried again 2026-10-19 for a Taiwan rate: `CBC` returns 0 rows (`FED` 222 rows, 1990-07-13 → 2026-06-17); `GovernmentBondsYield` with `data_id` "Taiwan 10-Year" returns 0 rows; `list_datasets` names no Taiwan policy, interbank or government bond rate. Volume IV's Sharpe ratios take a zero risk-free rate |
| FinMind `TaiwanStockPrice`, E5 and the checkpoint funds (`vol5/`, Free) | 0050, 00646, 00679B, 00635U and 00642U (E5, batch 4's through case) and 0056, 00662 and 00720B (LM35's checkpoint): `date, open, max, min, close, spread, volume` (`volume` is `Trading_Volume`), 2016-12-01 → 2026-10-08, one file a fund, retrieved 2026-10-24; `data/vol5_series.py` checks them (spreads against closes in exact arithmetic, ex-dates, splits, copied rows) and builds E5's estimation and wealth frames, which `data/vol5_rules.py` and the scripts of LM27–LM35 read |
| FinMind `TaiwanStockDividendResult`, the funds' distributions (`vol5/`, `vol6/`, Free) | 0050 and 0056 (label filter `^息$`) and 00679B and 00720B (`^除息$`): `date, before_price, after_price, cash_dividend` (from `stock_and_cache_dividend`), 2016-12-01 → 2026-10-08; 0050's two distributions of 2007-07-02 → 2008-12-31 for LM35's 2008 replay. 00646, 00635U and 00642U have no rows (survey and fresh check, `plans/vol-5.md`). FinMind's label differs by fund, so the filter of one entry copied to another keeps no row (PITFALLS §3) |
| FinMind `TaiwanStockSplitPrice` (`vol5/splits__2016-12-01__2026-10-08.csv`, Free) | every event of the dataset in the window, one query without `data_id`: 35 rows, 4 splits (分割), 6 reverse splits (反分割), 24 par-value changes (面額變更) and 00631L's 2026 split, whose `type` is empty; columns `date, stock_id, type, before_price, after_price`. `vol5_series.py` takes the events of E5 and the checkpoint funds from it (0050's four-for-one of 2025-06-18 among them) and stops unless the ratio is an integer. 00662's five-for-one split (trading suspended 2026-11-11 → 11-16, resuming 2026-11-17) falls after the window (Fubon and TWSE rows below) |
| FinMind `TaiwanStockPrice`, survivorship and replay files (`vol6/`) | LM34's survivorship example (§5): 00672L, 00673R, 00674R and 00677U over `vol5/`'s window and columns (00635U and 00642U come from `vol5/`); 00673R reverse-split one for four on 2025-10-22 and 00674R one for five on 2026-04-22 (the split file above), and 00674R prints a close of 0 on days without a trade (`data/README.md`); one-day snapshots of every ETF on 2017-01-17 and 2026-10-08, requested without `data_id` (FinMind serves that only above the Free plan; columns `date, stock_id, close, volume`; kept ids `^00\d{2,4}[A-Z]?$`; they hold TPEx-listed funds as well as TWSE-listed ones, 00679B in both and 00720B in 2026; a Free account fetches the rest with `--exclude vol6/etf_snapshot`, and LM34's A34-18 then prints a note instead of its value). LM35's 2008 replay: 0050's `date, close, spread` for 2007-07-02 → 2008-12-31. Retrieved 2026-10-24 |
| FinMind `TaiwanStockDelisting` (`vol6/delisting__2000-01-01__2026-10-08.csv`, Free) | `date, stock_id, stock_name` for ids beginning "00" (63 rows): which ETFs vanished, and the names of 00672L and 00677U; LM34 §5. Retrieved 2026-10-24 |
| FinMind `TaiwanStockInfo` (queried 2026-10-24 by LM34's drafter; no extract is registered, the editor's decision of 2026-10-25) | the query of 2026-10-24 gave the names of the six funds of LM34 §5 (its open item O12), which `data/vol6_anchors_lm34.py` fixes by code (`FUTURES6`): 00635U 期元大S&P黃金, 00642U 期元大S&P石油, 00672L 元大S&P原油正2, 00673R 期元大S&P原油反1, 00674R 期元大S&P黃金反1, 00677U 期富邦VIX. The script asserts the names of 00672L and 00677U against the registered delisting file; TWSE's ISIN page gives the other four the same short names (listing-markets row under "Taiwan exchanges"), and the second source hunt (2026-10-24) confirmed each fund's futures index and which three are daily leveraged or inverse on the issuers' and TWSE's pages (Taiwan facts, "LM34's six survivorship funds") |
| FinMind `USStockPrice` (`vol6/`, Free): SPY, TLT, GLD, USO, DBO | `date, adj_close, close`, 2007-07-02 → 2026-10-08, retrieved 2026-10-24: the US proxies of LM35's hypothetical 2008 and 2015 replays, for 00646, 00679B, 00635U and 00642U (none traded in 2008; in the 2015 window, 2015-04-27 → 08-24, only 00635U did, from 2015-04-15, and GLD stands in for it too). All five are registered with `--adjusted adj_close` (paragraph below). FinMind's US `Close` is already split-adjusted: USO's 1-for-8 reverse split of 2020-04-28 (USCF's page, under "Banks, issuers and firms") shows no jump in either column, and USO and GLD register no ex-dates (`data/raw_manifest.json`; `data/README.md`). The owner approved DBO on 2026-10-24 as a second oil proxy besides USO (`plans/vol-5.md`, capability check) |
| FinMind `TaiwanExchangeRate`, `data_id` USD (`vol6/USD_TWD__2007-07-02__2026-10-08.csv`, Free) | `date, spot_buy, spot_sell`, 2007-07-02 → 2026-10-08; FinMind's −1 rows (no quote) are filtered out at registration (`spot_buy` must start with 1–9). The USD/TWD leg of LM35's proxies, paired as the capability check fixed: the New York close of date D takes the first FX row dated after D |
| FinMind `TaiwanStockTotalReturnIndex`, TR23 (`vol3/`, retrieved 2026-10-18) | the TAIEX total-return index, 2003-01-02 → 2026-10-08 (Volume III's file, no new retrieval): the long sample of LM32–LM35 (VaR backtests, the Sharpe-ratio statistics, the reality check, scenario windows and the replays' calendar); `data/vol3_series.py` tests it against the price index |
| FinMind `TaiwanVariousIndicators5Seconds` and `TaiwanFuturesDaily` (T5S and TX23, Volume IV's files, no new retrieval) | LM35's five named days, through per-day statistics only (the raw day files are never published), and TX23's settlement moves; LM32's lab reads three raw T5S days |
| FinMind `TaiwanStockPriceAdj` (tried, not registered) | rebuilt backward from the latest day at every retrieval, like `Adj_Close` (PITFALLS §3), so LM34 builds its own adjusted 0050 series from the registered closes, distributions and split and prints no FinMind adjusted level |
| FinMind `TaiwanStockPriceLimit` (tried, not used) | wrong for ETFs: on the limit-down lock day of 2025-04-07 its limit for 0050 did not equal the price at which 0050 traded all day at exactly −10% (survey, `plans/vol-5.md` "Limits and locks"); the limits come instead from TWSE's Art. 8 for the TWSE-listed funds and from TPEx's ETF rules, Art. 7, for the TPEx-listed 00679B and 00720B (Taiwan sections below) |
| FinMind `InterestRate` (tried again, 2026-10-24) | the Volume V survey again found no Taiwan policy rate: it lists 12 central banks, not the CBC (`plans/vol-5.md`, "Risk-free rate"), so batch 4 keeps Volume IV's zero rate and, in the through case and where a riskless asset is part of the problem, an illustrative 1.5% a year |
| FinMind `TaiwanStockMarketValueWeight` (considered, not fetched) | Backer; it holds TAIEX weights as dated snapshots from 2024-10-30 only (`plans/ROADMAP.md`, tier check of 2026-10-11), and no market-value weights of E5's funds exist, so R2 is a constructed reference |
| FinMind [Pricing](https://finmind.github.io/Pricing/) and [Disclaimer](https://finmind.github.io/Disclaimer/) pages | hourly quotas per plan; the terms on redistribution and attribution that govern what Volume IV commits (below) |

Every registered FinMind file is fetched, and re-checked byte for byte, through the FinMind API with `data/fetch_finmind.py`;
intraday files, one request a day, with `data/fetch_intraday.py` and its own manifest (Volume IV).

Back-adjusted columns. FinMind rebuilds `USStockPrice`'s `Adj_Close` (and `TaiwanStockPriceAdj`) backward from the
latest day at every retrieval (PITFALLS §3, "Back-adjusted prices change at every retrieval", 2026-10-24), so a
re-fetch is not byte for byte the registered file. `data/fetch_finmind.py --add ... --adjusted adj_close` registers
such a file (the QQQ and TQQQ files of LM3 and the five US proxies of `vol6/`): every other field must match
exactly; the adjusted column must follow `close` day by day within three of that day's own cent-rounding allowances
(`0.005 (1/a[t-1] + 1/a[t] + 1/c[t-1] + 1/c[t])` on the log change, with a the adjusted and c the plain close) off
the registered ex-dates; and the window's distribution yield must agree within the rounding of its two end values.
The manifest keeps only the ex-dates, the yield and a SHA-256 of the other fields, never a price
(`fetch_finmind.py`, `adjusted_parts`, `adjusted_summary`, `adjusted_match`; `ADJ_K = 3`). A re-fetch that passes is
accepted and listed at the end of the run. A figure computed from an adjusted column is printed only to digits that
a cent per value cannot move, and its levels carry their retrieval date.

### TaiwanFuturesDaily, TX (TX23)

- Tier Free with a `data_id` (per `list_datasets`, the FinMind plugin's knowledge base). One call returns the whole
  history: 18.5 MB of JSON, 77,347 rows on 7,009 dates, 1998-07-21 → 2026-10-16 (survey); the fresh check's call,
  ending 2026-10-08, returned 77,221 rows on 7,004 dates (its saved file, read again in Stage 1). One year (2024) is
  1.57 MB.
- Columns: `date, futures_id, contract_date, open, max, min, close, spread, spread_per, volume, settlement_price,
  open_interest, trading_session`.
- Sessions: `trading_session` is `position` (regular session) or `after_market` (night session). `after_market` rows
  start 2017-05-16, and their settlement price and open interest are always 0. The `after_market` row dated D is the
  night session that began at 15:00 on the previous trading day (checked against the 1-minute bars: the row dated
  2025-06-30 opens at the 2025-06-27 15:00 bar and closes at the 2025-06-28 04:59 bar; after long holidays the gap is
  wider, the row dated 2018-02-21 being the night of 2018-02-12). Night prices do not enter `position` rows: on
  2025-06-27 the `position` open and close equal the 08:45 open and the 13:44 close. No `after_market` rows on
  2017-06-05, 2017-10-02, 2018-04-02, 2018-07-11 and 2018-12-24; cause unverified.
- Contracts: calendar spreads appear as `contract_date` "YYYYMM/YYYYMM" from 2007-10-08; monthly contracts per date
  are 2–5 in 1998–2000 (back months missing on days they did not trade), 5 from 2001-01 to 2018-06-29, and 6 from
  2018-07-02; no weekly contracts appear.
- Calendar: the regular-session dates equal `TaiwanStockTradingDate` for 1999-01-05 → 2026-10-16 and the TAIEX
  calendar for 2003-01-02 → 2026-10-08 (survey); the fresh check found the 5,850 regular-session dates equal to TR23's
  5,850, with no difference either way.
- Expiry-day zeros: from 2008-12-17 the expiring contract's settlement price prints 0 on its expiry day (214
  contracts, 6 of them on holiday-shifted dates); before that the expiry row carries a settlement price. TX23 therefore
  takes each monthly contract's last trading day from its last regular-session row and rolls at the close of the day
  before (plans/vol-4.md, "Data").
- Last close is not the final settlement: in the 189 months with both values, the expiring contract's last close equals
  TAIFEX's final settlement price in only 105 (for example 200906: close 6204 against 6203), and differs by up to 4
  points in the rest; `data/README.md` says so (corrected in Stage 1, 2026-10-19).
- `spread` is close minus the previous day's settlement price, not minus the previous close: it holds for 34,571 of
  34,773 same-contract pairs. The 202 exceptions: 197 in 1998–2000, where back-month rows are missing; 2001-03-07 (2
  contracts); 2007-03-12 (5 contracts, spread 0.0), the five inside TR23's window.
- Other oddities: 11 `position` rows (1998–2008, back months) with volume above 0 and open interest 0; 1,334
  `position` rows with close 0 and volume 0. No duplicate rows, no identical consecutive near-month rows and no copied
  whole days in the full history. Times are local Taipei time with no zone marker (inferred from the sessions).

### TaiwanFuturesFinalSettlementPrice (gaps)

- Tier Backer (per `list_datasets`; the Pricing page lists 期貨/選擇權最後結算價 under Backer). One call: 219 KB, 721
  rows (survey; 720 TX rows in the fresh check's call): 277 monthly rows, 199809 → 202609, and 444 rows coded
  "YYYYMMWn" from 2013-08-07 (443 in the fresh check). Which product the weekly codes belong to is unverified; they are
  not in `TaiwanFuturesDaily` TX, so filter to 6-character months.
- Columns: `date, contract_month, futures_type, futures_id, futures_name, settlement_price, underlying_code,
  notional_value`; `underlying_code` is empty and `notional_value` is 0 on every row.
- Gaps: every monthly contract of 2000, 2006, 2008, 2014 and 2020 is missing, 60 monthly prices in all (48 of them in
  TR23's window); a request for 2020 alone, and one for 2008 alone, returned no rows.
- Dates: for 200301–200712 the final-settlement date is one day after the contract's last regular-session row in
  `TaiwanFuturesDaily` (the third Wednesday plus one day); from 200901 they match. Six later dates are holiday-shifted:
  2010-02-22, 2010-06-17, 2013-08-22, 2015-02-24, 2023-01-30, 2026-02-23.

### TaiwanVariousIndicators5Seconds (T5S)

- Tier Free, no `data_id`. One day per request: a request with `end_date` returns HTTP 400, "the dataset
  TaiwanVariousIndicators5Seconds size is too large, we only send one day data, so end_date parameter need be none."
  (the survey's saved reply, read again in Stage 1).
- Columns: `date` ("YYYY-MM-DD HH:MM:SS", local time) and `TAIEX`. Data start on 2005-01-03; 2004-12-31 returns no
  rows.
- Regimes, by rows a day (09:00:00 to 13:30:00 inclusive): 271 (one value a minute, about 12.7 KB) to 2011-01-14;
  1,081 (15 seconds) from 2011-01-17; 1,621 (10 seconds) from 2014-02-24; 3,241 (5 seconds, about 152 KB) from
  2014-12-29. The 15-second to 10-second switch lies between the adjacent sessions 2014-02-21 (1,081 rows) and
  2014-02-24 (1,621); the 10-second regime ends on Saturday 2014-12-27 (1,621 rows, a re-review's fetch), the session
  before 2014-12-29. `data/fetch_intraday.py --check` prints every regime's first and last day from the download.
- On every one of the 8 days the fresh check sampled (2005–2025), timestamps increase strictly and the 13:30:00 value
  equals the `TaiwanStockPrice` close (for example 6426.39, 8606.37, 22470.1).
- The closing call auction freezes the index, on every day of every regime (A26-42; checked again 2026-10-19 with our
  own script over all 5,351 files of `data/raw/intraday/taiex5s/`):
  - The freeze starts at the first value after 13:25:00: 13:26:00, 13:25:15, 13:25:10 or 13:25:05, by regime. Every
    value from there to the last one before 13:30:00 is equal: on 1,503 of 1,503 one-minute days, 764 of 764
    fifteen-second, 214 of 214 ten-second and 2,870 of 2,870 five-second days. On 2025-06-27, for example, 59 equal
    values run from 13:25:05 to 13:29:55.
  - The 13:25:00 value is not part of the freeze: it differs from the frozen value on 365, 124, 28 and 1,115 of those
    days.
  - The 13:30:00 value (the close) differs from the frozen value on every day.
  - TWSE's trading-system page, already under "Taiwan exchanges, regulators and official pages", gives the closing
    call auction from 13:25. The data show the freeze in every regime, but which auction rules applied in the earlier
    regimes was not checked.
- `TaiwanStockEvery5SecondsIndex` (Backer, 291 KB a day) gave the same 3,241 values on 2025-06-27, with 0 differences.

### TaiwanFuturesKBar (night-session dating)

- Tier Sponsor; `data_id` required (per `list_datasets`); one day per request (a range returns the HTTP 400 above).
  Data start on 2011-01-03 (2010-12-31 is empty). Columns: `date, futures_id, contract_date, minute, open, high, low,
  close, volume`. Every listed month and the spread combinations, with no (contract, minute) duplicates.
- Night session from 2017-05-15 15:00. Rows are filed by calendar date: date D holds 00:00–04:59 of the night that began
  on D − 1 and 15:00–23:59 of the night that begins on D. So one night is split across two minute-bar dates and filed
  under a third date in `TaiwanFuturesDaily`, and a full download needs calls on Saturdays and post-holiday days
  (Saturday 2025-06-28 has 336 rows).
- Bars are labelled by their start minute. This is an inference from the 2025 labels; FinMind's page was not read on
  it. The near month's first regular-session label is 08:45:00 on all 243 trading days, night labels run
  15:00:00–04:59:00, and a bar labelled with the closing minute itself (13:45:00, or 05:00:00 at night) appears only
  on some days, with 2–16 contracts at 13:45:00 and 2–36 at 05:00:00. Labels that mark a bar's first minute fit all
  three.
- 2025, near month (TX23's contract on the previous date, A26-39), checked 2026-10-19 with our own script over
  `data/raw/intraday/tx1m/2025/` and `data/raw/vol4/TX__1998-07-21__2026-10-16.csv`:
  - The last regular-session label is 13:44:00 on 211 of 243 days, or 13:45:00 on 30. The 13:45:00 bar has a tiny
    volume (2–10 contracts; the median near-month bar from 08:45:00 to 13:44:00 has 276), and its close equals the
    daily close (`TaiwanFuturesDaily` `close`) on all 30.
  - The other two days are the limit-locked 2025-04-07 (last label 13:40:00, 103 bars) and 2025-04-10 (13:42:00,
    90 bars).
  - The last bar's close equals the daily close on 243 of 243 days.
  - Over all monthly contracts, 31 dates have a 13:45:00 bar (32 bars, volume 2–16, each close equal to that
    contract's daily close). The night session has a 05:00:00 bar on 5 of the 297 dates.
- The survey's test days of other years: bars to 13:44 in 2020, and a 13:45 bar in 2011 and 2017. Only 2025 is
  downloaded.
- Summed regular-session minute volume is not the daily volume: the ratio ran from 0.54 to 2.00 on 4 days, about 2 for
  the near month and below 1 for the next month in roll weeks. Cause unverified (consistent with minute bars counting
  both sides and leaving out spread legs).

### FinMind's terms (Pricing and Disclaimer)

- [方案與價格](https://finmind.github.io/Pricing/) (Pricing), retrieved 2026-10-19. Quoted by the fresh check: the
  licence table marks "再散布原始資料、建立鏡像 API" as not allowed on any plan; quotas
  "免費 | 300 次／小時（註冊會員 600 次／小時）", Backer 1,600, Sponsor 6,000 and Sponsor Pro 20,000 calls an hour.
- [免責聲明與資料授權](https://finmind.github.io/Disclaimer/) (Disclaimer), retrieved 2026-10-19. Quoted by the fresh
  check: §3.2 "本服務之授權不包含將本服務提供之資料對外再散布、轉售"; §3.3, whoever publishes the data must obtain the
  "原資料來源機關" licences; §2, credit the original providing agency.
- The fresh check's quotes came through a summarizer; they were re-read in the pages' HTML (next item). Its URL for
  the Disclaimer is the Pricing page's link `../Disclaimer/`.
- Read again in Stage 1 (raw HTML fetched with curl, tags stripped, 2026-10-19): each quoted phrase appears verbatim. The
  Disclaimer is dated 版本日期：2026-07-12 (re-read 2026-10-31: 版本日期 2026-10-30, the quoted items unchanged; it adds a restriction on broker-branch data, which the registered files do not include); its sections are numbered 一 to 五, and §3.2 and §3.3 are items 2 and 3 of
  the numbered list under 三、使用者之授權範圍. Item 2 continues "，或建置實質等同於本服務之鏡像服務。"; item 3 asks users
  who publish or redistribute the data to "自行確認並取得原資料來源機關所要求之相應授權". Section 二、來源標示 asks users
  who put the data to external use to "以適當方式標示原資料提供機關". On the Pricing page the Free row's quota cell reads
  "300 次／小時（註冊會員 600 次／小時）" (the "免費 |" of the quote is the price column); Free, Backer and Sponsor are
  "非商業用途"; every plan "需標示資料來源「FinMind」"; and "將即時資料直接呈現於 web、App 等對外介面" is not allowed on
  any plan.

## Taiwan exchanges, regulators and official pages

| Page | Used for |
|:--|:--|
| [TAIFEX TX](https://www.taifex.com.tw/cht/2/tX), [MTX](https://www.taifex.com.tw/cht/2/mTX), [TMF](https://www.taifex.com.tw/cht/2/tMF) contract specifications | multipliers NT$200/50/10, ticks, ±10% limit, session hours, expiry, settlement |
| [TAIFEX index margins](https://www.taifex.com.tw/cht/5/indexMarging) (also `indexMargingDetail`, `indexMargingDown`; English [indexMargining](https://www.taifex.com.tw/enl/eng5/indexMargining), [marginAdj](https://www.taifex.com.tw/enl/eng5/marginAdj)) | margins effective 2026-08-12; how margins are adjusted |
| TAIFEX [announcements](https://www.taifex.com.tw/cht/11/announcement) and [press releases](https://www.taifex.com.tw/cht/11/pressRelease) | search for 2025 margin changes (none found officially) |
| TAIFEX [final settlement price formula](https://www.taifex.com.tw/cht/5/formulaIndex) and its training PDF (最後結算價計算方式) | final settlement as an average of index values 13:00–13:25 plus the close |
| TAIFEX [daily settlement price](https://www.taifex.com.tw/cht/5/futSetPrice) and the TX trading rules ([trade_1_1.doc](https://www.taifex.com.tw/chinese/6/trade/trade_1_1.doc), Arts. 6, 11, 12); [trading safeguards](https://www.taifex.com.tw/cht/4/tradingSafeguard) | daily settlement = volume-weighted price of the last minute's trades, with fallbacks; no rule for a locked market; TX limit ±10% of the previous regular session's daily settlement price; tick one point; the rounding of a limit price to the tick is not stated (read 2026-10-11) |
| TAIFEX 114年期貨集中交易市場開（休）市日期表 ([PDF](https://www.taifex.com.tw/file/taifex/CHINESE/11/attach/114%E5%B9%B4%E6%9C%9F%E8%B2%A8%E9%9B%86%E4%B8%AD%E5%B8%82%E5%A0%B4%E9%96%8B%E4%BC%91%E5%B8%82%E6%97%A5%E6%9C%9F.pdf)) | futures market closed on 3 and 4 April 2025 (read 2026-10-11) |
| [TWSE trading system](https://www.twse.com.tw/zh/products/system/trading.html) | 09:00–13:30 session, closing call auction from 13:25 |
| TWSE index compilation rules: [IndexS02.pdf](https://www.twse.com.tw/downloads/zh/products/indices/IndexS02.pdf) (TAIEX), [IndexS03.pdf](https://www.twse.com.tw/downloads/zh/products/indices/IndexS03.pdf) (the sector series), IndexS07.pdf | TAIEX, sector and total-return index methodology |
| TWSE IndexS03.pdf (2023.06) and [IndexS02.pdf](https://www.twse.com.tw/downloads/zh/products/indices/IndexS02.pdf) (2023.04), read again for Volume II | the sector indices are market-value-weighted price indices (a separate return-index series adds cash dividends; Appendix 2 lists the sector price indices); a price index's base is not adjusted for cash dividends (read 2026-10-11) |
| TWSE news of 2007-06-27 ([newsDetail id=606](https://www.twse.com.tw/rwd/zh/news/newsDetail?id=606&response=json)); Taiwan Index Co. [index list](https://taiwanindex.com.tw/en/indexes/multiple) (secondary) | from 2007-07-02, 29 industry categories, electronics split into eight sub-industries; their indices start on that date |
| TWSE MI_INDEX price-index table of 2025-10-08 (JSON `twse.com.tw/rwd/zh/afterTrading/MI_INDEX?date=20251008&type=IND&response=json`) | official Chinese names of the 28 leaf sector indices (…類指數); every close that day equals FinMind's (read 2026-10-11) |
| TWSE English notice on 0050's split ([PDF, 2025-05-14](https://www.twse.com.tw/staticFiles/news/news/tsecnews/8a8216d696b406fc0196ce290acb0065.pdf)); the issuer's notice on [ETFortune](https://www.twse.com.tw/zh/ETFortune/announcement?company=A00005&date=20250509&seq=1&fund=0050&type=all) | 0050 split four for one; trading suspended 11–17 June 2025, new units from 18 June (read 2026-10-11) |
| TWSE [company history](https://www.twse.com.tw/en/about/company/history.html) and 60th-anniversary book, [p. 181](https://www.twse.com.tw/staticFiles/product/publication/twse60/html/181/) (also pp. 256, 429) | daily limit widened from 7% to 10% on 2015-06-01 |
| [TPEx fluctuation limits](https://www.tpex.org.tw/zh-tw/mainboard/trading/rules/fluctuation-limit.html) | cross-check of the 10% limit |
| TWSE Rules Governing Trading of Beneficial Certificates (受益憑證買賣辦法), Art. 8: [EN](https://twse-regulation.twse.com.tw/EN/law/DAT0201.aspx?FLCODE=FL007114), [ZH](https://twse-regulation.twse.com.tw/TW/law/DAT0201.aspx?FLCODE=FL007114), [Art. 8 alone](https://twse-regulation.twse.com.tw/TW/law/DOC01.aspx?FLCODE=FL007114&FLNO=8), [amendment history](https://twse-regulation.twse.com.tw/TW/law/DAT01.aspx?FLCODE=FL007114), versions at `DAT06.aspx?FLCODE=FL007114&FLDATE=20241231&LSER=001` (also `20240223`, `20160603`) | ¶1: the listed-stock limit applies (準用上市股票之有關規定), except four kinds of certificate with no daily limit: (1) index ETFs with foreign constituent securities and their attached listings (加掛), (2) futures-trust ETFs tracking a foreign futures index, (3) offshore ETFs (境外指數股票型基金), (4) active ETFs with foreign constituent securities. ¶2: a leveraged or inverse ETF on an index whose constituents are all domestic has a limit of 10% times its multiple; if any constituent is foreign, none (00631L's −19.995% and +19.968% limit closes of April 2025 fit 20%). **Dates:** Art. 8 itself was last amended on 2024-12-31 (臺證上二字第1131705681號, effective at once; it added item (4) and reworded item (1) from "及其加掛 ETF 受益憑證" to "及其加掛指數股票型基金受益憑證"); items (1)–(3) and ¶2 read the same in the versions of 2016-06-03 (臺證交字第1050009905號) and 2024-02-23, and the history page names Art. 8 in no other amendment since 2016-06-03, so the rule for index and futures ETFs has stood since 2016-06-03 (versions before 2016-06-03 not read). The version date the pages print, **2025-09-30** (公告 臺證交字第1140205581號, effective at once), is the rules' version date: that amendment changed Arts. 14, 5-1 and 5-2, not Art. 8. Arts. 5-1 (SITC ETFs) and 5-2 (futures-trust ETFs), added by it, let the issuer apply to suspend trading during the closure of the foreign market on the same conditions as TPEx's Arts. 4-2 and 4-3 (TPEx ETF rules row below): five or more consecutive business days on which the foreign market is closed and TWSE trades (連續五個營業日（含）以上), and a NAV of at most NT$3 billion or a premium or discount of 3% or more on each of the two business days before the application, filed four business days before the closure; in force from 2025-09-30, so inside the data window, which ends 2026-10-08. Read 2026-10-11 (¶2, version date) and 2026-10-24 (¶1, the dates and the three versions; the source check, and every page re-opened for this entry: HTTP 200, text in the HTML). TWSE's rules govern TWSE-listed certificates; 00679B and 00720B trade on TPEx (listing-markets row below), and their limit is TPEx's ETF rules, Art. 7 (TPEx rows below). TWSE's Art. 2-1 ¶1 item 一(二)2 (added 2024-12-31) defines a foreign-constituent bond index ETF (「…標的指數成分證券全部為債券者，且成分證券含一種以上國外債券者」), and the 2016-06-03 and 2024-02-23 texts (Art. 2 item 二(一)2) define a foreign-constituent index ETF by 「含一種以上國外有價證券」, so Art. 8 item (1) covers foreign bonds; none of the TWSE-listed funds used is a bond ETF (TWSE's classes, e添富 row below). The Operating Rules (營業細則) Art. 63 have no ETF clause |
| TWSE Holiday Schedule 2025 (JSON endpoint `twse.com.tw/rwd/en/holidaySchedule/holidaySchedule?response=json&date=20250101`; the page is rendered by JavaScript) | the English JSON labels 3 April "Adjusted Holiday" and 4 April "Children’s Day & Tomb-sweeping Day" (read 2026-10-11; the same labels on 2026-10-25); the Chinese JSON (`rwd/zh/holidaySchedule`, `date=20250101`, read 2026-10-24 by the second source hunt) names both days 兒童節及民族掃墓節 and says of 3 April 「兒童節與民族掃墓節為4月4日（星期五），依規定於前一日4月3日（星期四）放假。」 So 3 April is the observed holiday for the two holidays of Friday 4 April |
| TWSE 中華民國109年有價證券集中交易市場開（休）市日期表 (the 2020 holiday schedule), [Wayback Machine capture of 2020-06-04](https://web.archive.org/web/20200604104858/https://www.twse.com.tw/zh/holidaySchedule/holidaySchedule) of `twse.com.tw/zh/holidaySchedule/holidaySchedule` | the last session before the Lunar New Year was 1月20日, with 「1月21日及1月22日市場無交易，僅辦理結算交割作業」; 1月23日 調整放假; 1月24日 除夕; 1月25日–29日 春節; 1月30日 農曆春節後開始交易. So the market was closed 2020-01-21 → 01-29, and 2020-01-30 comes ten calendar days after the previous session (LM35, A35-06 and A35-10). TWSE's own JSON returns no rows for 2018–2020 (Volume IV's check, and again on 2026-10-24), hence the archived copy. Read 2026-10-24 by the second source hunt; for this entry, the archive's index gives this capture's timestamp, and its digest matches the hunt's copy |
| 全國法規資料庫: [Banking Act Art. 47-1](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=G0380001&flno=47-1), 信用卡業務機構管理辦法 [Art. 48](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=G0380055&flno=48) | 15% cap on card revolving interest from 2015-09-01; no compounding of revolving interest (Art. 48 item 1, read 2026-10-11) |
| TWSE [ETF 專區, 交易規則](https://www.twse.com.tw/zh/products/securities/etf/overview/rules.html) (the ETF rules page) | one table for NT$ ETFs and the attached RMB and USD listings: tick 0.01 below NT$50 and 0.05 from NT$50 ("較一般股票小"); daily limit "同一般股票(10%)，但含海外股票之ETF價格無漲跌幅限制" (narrower than Art. 8, which the text cites for the limits); trading time as for stocks; tax "證交稅：ETF賣方課徵0.1% (債券ETF免徵證交稅10年至2026年)". The page prints no date (the footer reads ©2023); the server's `Last-Modified` was Thu, 22 Oct 2026 06:38:26 GMT; read 2026-10-24 by the source check and again for this entry (HTTP 200, 13,030 bytes, byte-identical to the check's copy; static HTML, no JavaScript needed); re-read 2026-10-31: `Last-Modified` Wed, 28 Oct 2026 06:12:16 GMT, 13,103 bytes, the tick, limit and tax rows as quoted |
| TWSE [ETF 總覽](https://www.twse.com.tw/zh/products/securities/etf/overview/introduction.html) (the ETF overview page) | the three legal types of listed ETF (證信託ETF, 期貨ETF and 境外ETF) and seven asset classes, among them 原型期貨ETF, whose index constituents are all commodities such as crude oil, precious metals, currencies and soybeans (原油、貴重金屬、貨幣及黃豆等大宗商品). Under 「三、期信託ETF另外須考慮之其他投資風險」 the roll cost reads: 「期貨轉倉成本：期信託ETF追蹤的是期貨指數，基金經理人將會依據標的指數規則定期轉倉，當近遠期期貨之間為正價差(遠期期貨較近期期貨貴)時，基金經理人即須買高(遠期期貨)賣低(近期期貨)，期貨轉倉可能產生之損失無法避免。」: the losses the roll *may* produce (可能產生), so the text keeps the "may". A futures-trust ETF on a foreign futures index is valued on Europe and US futures, so the time difference is a risk. Under §四 the multiple of a leveraged or inverse ETF holds 「僅限於單日，在每日複利計算下，ETF之長期報酬率會偏離…」 (00672L, 00673R and 00674R). The page does not call futures ETFs unsuited to long holding (LM34's O13; the issuers say so of four funds, Taiwan facts below). `Last-Modified` Thu, 22 Oct 2026 06:38:26 GMT (Wed, 28 Oct 2026 06:12:16 GMT on 2026-10-31, the quoted sentences unchanged); footer ©2023; read 2026-10-24 by LM34's reviser, for this entry and by the second source hunt (HTTP 200, static; the hunt's copy is byte-identical to this entry's) |
| TWSE ETF e添富 fund pages, `https://www.twse.com.tw/zh/ETFortune-institute/etfInfo/<code>` (added for this entry; the briefs of LM27, LM34 and LM35 cite them) | the exchange's own classification (證券類別) and index (標的指數) of each fund, read 2026-10-24 (HTTP 200, static): 0050 台股ETF, 富時臺灣證券交易所臺灣50指數; 0056 台股ETF, 臺灣高股息指數 (證券簡稱 元大高股息); 00646 國外股票ETF, 標普指數(S&P 500R); 00662 國外股票ETF, NASDAQ-100指數 (證券簡稱 富邦NASDAQ; both short names read in the copies re-fetched on 2026-10-25; issuer 富邦投信; with Fubon's own page below, this closes the part of LM35's open item 3 that asked for 00662's index); 00635U 期貨ETF, 標普高盛黃金ER指數(S&P GSCI Gold Excess Return Index); 00642U 期貨ETF, 標普高盛原油ER指數(S&P GSCI Crude Oil Enhanced Excess Return); 00631L 股票槓反ETF, 臺灣50指數. For LM34 the second source hunt also read 00673R and 00674R: 期貨槓反ETF, 標普高盛原油日報酬反向一倍ER指數(S&P GSCI Crude Oil 1x Inverse Index ER) and 標普高盛黃金日報酬反向一倍ER指數(S&P GSCI Gold 1x Inverse Index ER). 00679B and 00720B are TPEx-listed (listing-markets row below), and for them, as for the delisted 00672L and 00677U, the same URL pattern returned the e添富 home page instead of a fund page; TPEx's product pages (row below) classify the two bond funds. The e添富 split table (分割/反分割預告表; this entry's first draft saw the same notice on the 00662 page, the second hunt read the table) lists a split of 00662: 停止買賣日期 2026-11-11, 恢復買賣日期 2026-11-17, ratio 5.00 (units after over units before), so no trading 2026-11-11 → 11-16, after the data window of 2026-10-08 |
| TWSE ETF e添富 announcements (重大消息) on LM34's delisted funds: 00672L of [2020-07-07](https://www.twse.com.tw/zh/ETFortune/announcement?company=A00005&date=20200707&seq=1&fund=00672L&type=all) and [2020-10-12](https://www.twse.com.tw/zh/ETFortune/announcement?company=A00005&date=20201012&seq=1&fund=00672L&type=all), 00677U of [2021-04-29](https://www.twse.com.tw/zh/ETFortune/announcement?company=A00010&date=20210429&seq=1&fund=00677U&type=all) | 00672L, 元大標普高盛原油ER單日正向2倍指數股票型期貨信託基金 ("證券代號：00672L"): on 2020-07-07 the issuer explains that it had moved the fund's holdings from the index's near-month constituent to the December 2020 WTI contract (「故將指數成分期貨契約轉至2020年12月份西德州輕原油期貨契約」), the cause of its tracking error (from the start of 2020 to 2020-06-30 the index fell 97.84% and the NAV 95.23%), and that it would roll back to the index's near-month contracts from 2020-07-08 (「自7月8日起轉倉至近月份指數成分期貨契約」); on 2020-10-12, its termination: the average NAV per unit over the last thirty business days had fallen 90% from its initial value; FSC approval 2020-10-07 (金管證期字第1090370507號); last trading day 2020-11-12, delisted from 2020-11-13, contract terminated 2020-11-16, liquidation reference date 2020-11-24. 00677U (富邦標普500波動率短期期貨ER指數股票型期貨信託基金): last trading day 2021-06-02, delisted from 2021-06-03, contract terminated 2021-06-04. Read 2026-10-24 by the second source hunt; the three URLs answered HTTP 200 as static pages on 2026-10-25 (this entry's verifier, and again for its first repair) |
| TWSE Operating Rules (營業細則), version 115.09.24: [mobile page FL007304](https://twse-regulation.twse.com.tw/m/LawContent.aspx?FID=FL007304) | Art. 94: the commission is charged after a trade, at a rate that TWSE reports to the authority for approval; a broker may set its own rate by the value traded, with discounts and a minimum per order, filed with TWSE for the record, and must notify a client before the order, and keep a record, when the rate exceeds 千分之一點四二五 (1.425‰), so 0.1425% is a reference, not a cap. Art. 3: the market's trading time is 09:00–13:30 (上午九時至下午一時三十分). Art. 63: the daily limit is 10% for stocks and 5% for bonds, with no ETF clause. These rules are TWSE's, for the TWSE-listed funds; the TPEx-listed 00679B and 00720B follow TPEx's Business Rules (row below). Read 2026-10-24 by LM34's drafter and again for this entry (HTTP 200; the page's 法規名稱 line carries the version, 「臺灣證券交易所股份有限公司營業細則（115.09.24）」; on 2026-10-31 the page carries 115.10.19, and Arts. 3, 63 and 94 still contain the phrases quoted above) |
| TPEx 指數股票型基金及主動式交易所交易基金受益憑證買賣辦法 (the ETF rules; English title "Taipei Exchange Rules Governing Trading of Passive Exchange-Traded Fund and Active Exchange-traded Fund Beneficial Certificates"; named 「…指數股票型基金受益憑證買賣辦法」 before 2024-12-31): [selaw LW10845400](https://www.selaw.com.tw/Chinese/RegulatoryInformationResult?sysNumber=LW10845400), tabs 所有條文, 法規沿革, 歷史法規 and 附件下載, and its English version. TPEx's [ETF rules page](https://www.tpex.org.tw/zh-tw/product/etf/regulations/rules.html) lists the rules by name and refers to that database (「相關法規請至「證券暨期貨法令判解查詢系統」網站查詢」; selaw.com.tw, run by 證券暨期貨市場發展基金會) | the rules of the TPEx-listed 00679B and 00720B, issued under the Business Rules Art. 39-7 (Art. 1). **Limit, Art. 7:** the TPEx-stock limit applies (準用上櫃股票之有關規定), but none (採無升降幅度限制) for ¶1 item 一, 國外成分證券 index ETFs and foreign-constituent active ETFs with their 加掛 listings, and item 二, futures-trust ETFs tracking a foreign futures index; ¶2: 10% times the multiple for a leveraged or inverse ETF on an all-domestic index, none if a constituent is foreign. Art. 2-1 ¶1 item 二(二) defines a foreign-constituent bond ETF as one whose index holds only bonds, at least one of them foreign (「…標的指數成分證券全部為債券者，且成分證券含一種以上國外債券者」; Art. 2-1 added 2024-12-31, its 2025-09-30 amendment only adding item 三), so foreign bonds are covered expressly. **Session, Art. 4 ¶2:** trading time, matching method and order-size limits follow the Business Rules for TPEx stocks (準用本中心業務規則有關上櫃股票之規定; the same sentence stands in the texts before 2010 and 2017; a proviso added 2010-11-29, 「但債券成分之指數股票型基金之交易時間由本中心另行公告之」, was deleted by the amendment of 2016-01-30, before E5's span). **Commission, Art. 15 ¶1:** the broker's commission and TPEx's service fee follow the rates for TPEx stocks (準用上櫃股票規定之費率辦理), i.e. the Business Rules Art. 64 (next row); the texts before 2019-04-24 and before 2023-09-15 read 「…準用上櫃股票交易規定之費率辦理」 (the amendment of 2019-04-24, in force 2019-05-01, added 「除第二項另有規定外」 and ¶2's exception for the service fee on repo trades; the history names Art. 15 in no amendment from 2017-01-17 until then), so the rule stood through E5's span. **Dates:** the current version is 2025-09-30 (證櫃交字第11400735781號; Arts. 2-1 and 13 amended, 4-2 and 4-3 added). The 法規沿革 lists 26 entries: the issuance of 2007-11-08 and 25 amendments. Art. 7 was amended 2017-02-13 (證櫃交字第10600023611號, in force 2017-03-01), 2018-08-09 (證櫃交字第10700215501號), 2023-09-15 (證櫃債字第11200696191號) and 2024-12-31 (證櫃債字第11300812731號, which renamed the rules), and by none since. The texts before each change (歷史法規) carry the exception throughout: to 2017-02-28 for an index whose 成分股 (constituent shares) include foreign securities, from 2017-03-01 成分證券 (constituent securities), from 2018-08-09 the item list, with 國外成分證券 defined in Art. 2. Under the 成分股 text TPEx's listing notice still gave 00679B no limit (notices row below), and 00679B's largest close-to-close move from 2017-01-17 to 02-28 is −1.84% (repository data), so no number turns on that wording. **Locks:** Art. 4-1 lets such ETFs keep trading while the foreign market is closed; Arts. 4-2 (SITC ETFs) and 4-3 (futures-trust ETFs), added 2025-09-30, let the issuer apply to suspend trading during a foreign closure of five or more consecutive business days (連續五個營業日(含)以上) when the NAV is at most NT$3 billion or the premium or discount reached 3% on each of the two business days before the application. Read 2026-10-25 by the TPEx source check and its verifier (anonymous requests; the verifier's re-fetch matched word for word) |
| TPEx 證券商營業處所買賣有價證券業務規則 (the Business Rules; English title "Taipei Exchange Rules Governing Securities Trading on the TPEx"): [selaw LW10812069](https://www.selaw.com.tw/Chinese/RegulatoryInformationResult?sysNumber=LW10812069), current version 2026-10-21 (證櫃交字第11500775601號: Arts. 45-4 and 46 amended, 46-11 added) | **Art. 64**, the counterpart of TWSE's Art. 94, applied to ETFs by the ETF rules' Art. 15 ¶1: the broker charges the commission after the trade (¶1); TPEx drafts the rate and the authority approves it (¶2); a broker may set its own schedule by value traded, with discounts and a minimum per order, filed with TPEx for the record, and must notify the client before applying, and keep a record, a rate above 千分之一點四二五 of the value traded (¶3; the English version: "exceeds 0.1425 percent"), so 0.1425% is a reference, not a cap. ¶1–¶3 are unchanged since 2008-02-12 (證櫃交字第0970002700號); the article was last amended 2011-12-16 (證櫃交字第1000033483號), in ¶4 and ¶5 only (item 二 added to ¶4's exceptions to the ban on paying fees to introducers; ¶5 now refers to item 一); the hunt compared the 89 old texts that contain Art. 64. **Art. 40** item 一: the trading time is 09:00–13:30 for stocks on the 等價成交系統 (上午九時至下午一時三十分); last amended 2014-09-23 (in force 2014-12-29), in item 二 only, so the hour held over E5's span; ETFs reach it through the ETF rules' Art. 4 ¶2. **Art. 35 ¶3:** the closing price is the price of the call auction before the close, or else the day's last trade (the text before 2020 states the same rule). **Continuous trading** began on 2020-03-23: the 法規沿革's entry 53, the amendment of 2018-12-28 (證櫃交字第10700539481號; Arts. 35, 35-11, 36, 62, 63 and 72 amended, 35-12 added), 「自109年3月23日起實施」. Read 2026-10-25 by the TPEx source check and its verifier |
| TPEx [交易系統簡介](https://www.tpex.org.tw/zh-tw/mainboard/trading/rules/system.html) and [逐筆交易](https://www.tpex.org.tw/zh-tw/mainboard/trading/rules/continuous.html) pages (`Last-Modified` Thu, 26 Mar 2026 07:55:10 GMT, both) | 「委託時間8:30至13:30，撮合成交時間為9:00至13:30」; a delayed close moves to 13:33 (「達到暫緩收盤標準之有價證券，將延後至13:33分收盤」); the first match (the 09:00 open) is a call auction, continuous matching follows to 13:25, and 13:25 to the 13:30 close is a call auction. The 逐筆交易 page says 「13:25至收巿仍維持採集合交易撮合」, so the closing call was kept, not introduced, with continuous trading; for the start date it reports only the FSC's announcement of 2018-09-03 that continuous trading was 預訂 for 2020-03-23 (the date in force is in the row above). The 交易系統簡介 page lists 國外成分證券ETF(及其加掛ETF) and 追蹤國外商品期貨指數之ETF under 無漲跌幅, and domestic-constituent ETFs under 「以漲或跌至當日參考價格10%為限」. Read 2026-10-25 by the TPEx source check (static HTML; its verifier's re-fetch matched) |
| TPEx listing notices 證櫃債字第10600009612號 (2017-01-13, 00679B) and 證櫃債字第10700020421號 (2018-01-25, 00720B, with 00719B and 00721B); TPEx ETF product pages, `https://www.tpex.org.tw/zh-tw/product/etf/product/detail.html?type=bond&code=<code>`, for [00679B](https://www.tpex.org.tw/zh-tw/product/etf/product/detail.html?type=bond&code=00679B) and [00720B](https://www.tpex.org.tw/zh-tw/product/etf/product/detail.html?type=bond&code=00720B) (data from TPEx's `/www/zh-tw/ETF/detail`) | the notices: 00679B 「於本(106)年1月17日起在證券商營業處所開始櫃檯買賣」 and 00720B from 2018-02-01, each with 「每日漲跌幅限制：無漲跌幅度限制」. The product pages: 00679B 元大美債20年, ETF類別 被動式國外債券及固定收益ETF, 上櫃日期 2017/01/17, 標的指數 ICE美國政府20+年期債券指數; 00720B 元大投資級公司債 (TPEx's short name, its field ETF簡稱; the fund 元大20年期以上BBB級美元公司債券ETF證券投資信託基金, of the 元大多元債券ETF傘型 umbrella), the same class, 上櫃日期 2018/02/01, 標的指數 彭博美國20+年期BBB公司債流動性指數. For both: 升降幅度 「無漲跌幅度限制」, 交易時間 「同上櫃證券」, 證券交易稅 「依證券交易稅條例第2條之1規定」, and ticks of 1 分 below NT$50 and 5 分 from NT$50. Read 2026-10-25 by the TPEx source check (its verifier re-fetched them) |
| Listing markets: TPEx's ETF list (`info.tpex.org.tw/api/etfFilter`, 118 ETFs) and OpenAPI [`tpex_mainboard_daily_close_quotes`](https://www.tpex.org.tw/openapi/v1/tpex_mainboard_daily_close_quotes) (13,032 rows dated 1151022, i.e. 2026-10-22); TWSE's OpenAPI [`STOCK_DAY_ALL`](https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL) (dated 1151022) and ISIN pages for [上市](https://isin.twse.com.tw/isin/C_public.jsp?strMode=2) and [上櫃](https://isin.twse.com.tw/isin/C_public.jsp?strMode=4) securities | 00679B 元大美債20年 and 00720B 元大投資級公司債 are TPEx-listed (上櫃 from 2017-01-17 and 2018-02-01: ISIN page and etfFilter `listingDate`) and absent from `STOCK_DAY_ALL`. TWSE-listed (上市), in `STOCK_DAY_ALL` and in neither TPEx list, with the ISIN page's short names and listing dates: 0050 元大台灣50 (2003-06-30), 0056 元大高股息 (2007-12-26), 00635U 期元大S&P黃金 (2015-04-15), 00642U 期元大S&P石油 (2015-09-07), 00646 元大S&P500 (2015-12-14), 00662 富邦NASDAQ (2016-06-24), 00673R 期元大S&P原油反1 and 00674R 期元大S&P黃金反1 (both 2016-10-07); the delisted 00672L and 00677U have their delisting announcements on TWSE's e添富 (row above). TPEx's quotes give 00679B and 00720B `NextLimitUp` 9999.95 and `NextLimitDown` 0.01, the no-limit placeholders, against 46.36 and 37.94 (±10% of the close 42.15) for the domestic 006201 元大富櫃50. Read 2026-10-25 by the TPEx source check; its verifier re-fetched them, and every linked URL of this row answered anonymously again for this entry's first repair |
| 全國法規資料庫, [證券交易稅條例](https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=G0340078) (修正日期 民國114年01月02日), with its 沿革 (history) and 授權子法 pages | Art. 2: the tax is charged to the seller at the trade price: item 1, 千分之三 on the shares of a company; item 2, 千分之一 on corporate bonds "及其他經政府核准之有價證券" (other securities approved by the government); Art. 2 last amended 1993-01-30 (82年1月30日 華總（一）義字第0401號令). Art. 2-1 ¶2: from 民國106年1月1日 to 115年12月31日 (2017-01-01 to 2026-12-31) the tax is suspended on sales of the listed and OTC-listed (上市及上櫃) bond ETFs of securities investment trust enterprises, so on TWSE and TPEx alike (00679B and 00720B are on TPEx); leveraged and inverse bond ETFs are excluded; ¶3 limits such funds' investments to domestic and foreign government bonds, corporate bonds, financial bonds, bond repos, bank deposits and bond futures. Art. 2-1 was added 2009-12-30 and last amended 2016-12-30 (華總一義字第10500165221號令; the history's later entries amend other articles only). Art. 1 ¶2 counts "經政府核准得公開募銷之其他有價證券" as securities. The Act was last amended 2025-01-02 (華總一經字第11300128651號令), and that amendment changed Arts. 2-2 and 12 only. The Act names no ETF; the Ministry of Finance's rulings (next row) place fund certificates, futures-trust ones among them, under Art. 2 item 2. No 施行細則 exists: the 授權子法 page lists only the rule on warrant-hedge accounts (權證避險專戶…稅率辦法, 112-08-14). Read 2026-10-24 by LM34's drafter, for this entry and by the second source hunt (HTTP 200); Art. 2-1's three paragraphs ([Art. 2-1 alone](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=G0340078&flno=2-1)) and the history read again 2026-10-25 by the TPEx source check |
| 財政部 法令彙編函釋檢索系統 (the Ministry of Finance's ruling database): [ruling 97/08/11 台財稅字第09700161260號函](https://ttc.mof.gov.tw/FB/FB120/139155), filed under 證券交易稅條例, 一一四年版, 第二條（稅率）, 釋示函令 5, 「期貨信託事業發行受益憑證募集期貨信託基金之課稅規定」 | the direct official statement of the futures-ETF rate. For the certificates of a futures-trust fund (期貨信託基金): 「2.受益憑證之轉讓，應依證券交易稅條例第2條第2款規定，按每次交易成交價格1‰課徵證券交易稅。」 Issuing them is not a trade and a redemption that cancels them is not a securities transaction, so neither is taxed (items 1 and 3). So 00635U and 00642U pay 0.1% on sales, under Art. 2 item 2. Corroborating copy: the Ministry's earlier ruling system (ttc.gov.tw, an Internet Archive capture of 2023-06-04, Big5, ‰ printed as "?") lists this ruling as [N5] under Art. 2, beside [N2] 79/01/08 台財稅第791182786號函 (certificates of securities investment trusts are government-approved securities, taxed at 1‰ under Art. 2 item 2) and [N6] 財政部賦稅署 98/04/16 台稅一發字第09804022810號函 on Taiwan–Hong Kong cross-listed ETFs (臺港指數股票型基金相互掛牌交易: a domestic SITC feeder ETF and a directly cross-listed Hong Kong ETF traded on TWSE pay 1‰ under Art. 2). Read 2026-10-24 by the second source hunt; the page answered HTTP 200 again for this entry |
| 財政部統計處 [財政統計通報 第21號](https://service.mof.gov.tw/public/Data/statistic/bulletin/113/%E7%AC%AC21%E8%99%9F_ETF%E8%AD%89%E4%BA%A4%E7%A8%85.pdf) (113年11月14日; "113年1-9月ETF交易金額已超越歷年全年水準，貢獻證交稅約50億元") | para. 1 ends with the ETF tax rate, 千分之1, being below the rate on ordinary stocks (so the tax is 2.2% of the total); para. 2: bond and fixed-income ETFs have the tax suspended from 民國106 to 115 (2017–2026); the table "113年1-9月ETF成交狀況－按投資標的分" has a 原型期貨 (plain futures ETF) column with turnover, tax collected and their shares, and a 槓桿及反向 column whose footnote says it includes leveraged and inverse futures ETFs. The notice prints no rate per column; the 0.1% for 00635U and 00642U is the Ministry's ruling (row above), which the notice supports (it shows tax collected on 原型期貨 ETFs and gives the ETF rate as 千分之1). The PDF is byte-identical in the source check's, this entry's and the second hunt's copies (521,424 bytes; `Last-Modified` Wed, 13 Nov 2024 05:23:55 GMT); its text layer loses the Chinese glyphs, so it was read as a page image on 2026-10-24 (source check and this entry). Source: MOF; HTTP 200 anonymous |
| [Bank of Taiwan rates](https://rate.bot.com.tw/twd) | one-year 定期儲蓄存款 1.725% and 定期存款 1.700%, posted 2026-10-10 |

## Banks, issuers and firms

| Page | Used for |
|:--|:--|
| COTA Bank revolving-credit disclosure (cotabank.com.tw, card_pdf_revolvingCredit.pdf) | revolving interest = balance × rate × days/365 |
| DBS Taiwan NTD deposit terms (dbs.com.tw, DBS_NTD_Deposit.pdf; 新台幣存款計息方式, updated 2024-04-10; read by local text extraction, 2026-10-11) | 整存整付 compounds monthly; 存本取息 accrues daily; actual days over 365, leap years included |
| Bank of Taiwan 存戶須知重要內容說明書 (version 2017-01-26, hosted on gov.tw) | whole months credited monthly, part months by day; 整存整付 compounded, 存本取息 simple: not the same convention as DBS |
| [Yuanta 00679B fund page](https://www.yuantaetfs.com/product/detail/00679B/Basic_information) and holdings ratio page | tracked index (ICE US Treasury 20+ Year), set-up 2017-01-11, listing 2017-01-17, no currency hedge |
| Yuanta fund pages, `https://www.yuantaetfs.com/product/detail/<code>/Basic_information` for [0050](https://www.yuantaetfs.com/product/detail/0050/Basic_information), [00646](https://www.yuantaetfs.com/product/detail/00646/Basic_information), [00635U](https://www.yuantaetfs.com/product/detail/00635U/Basic_information), [00642U](https://www.yuantaetfs.com/product/detail/00642U/Basic_information), [00720B](https://www.yuantaetfs.com/product/detail/00720B/Basic_information) and [0056](https://www.yuantaetfs.com/product/detail/0056/Basic_information) | tracked index, set-up date and listing date, read 2026-10-24 by LM27's drafter (0050, 00646, 00635U, 00642U) and LM35's (00720B), and again for this entry (HTTP 200 for all six; the fields are in the server-rendered HTML): 0050 臺灣50指數, FTSE TWSE Taiwan 50 Index, TWSE and FTSE, 50 constituents, listed 2003-06-30; 00646 標普500指數, S&P500 Index, compiled by S&P指數公司, listed 2015-12-14; 00635U 標普高盛黃金超額回報指數, S&P GSCI Gold Excess Return Index, "紐約商品交易所(COMEX) 黃金期貨契約", no distribution, listed 2015-04-15; 00642U 標普高盛原油增強超額回報指數, S&P GSCI Crude Oil Enhanced Excess Return, "紐約商業交易所(NYMEX)西德州輕原油期貨契約", no distribution, listed 2015-09-07 (the page also prints the index's roll rule); 00720B 彭博美國 20+ 年期 BBB 公司債流動性指數, Bloomberg US 20+ Year BBB Corporate Bond liquid index, a customized index, listed 2018-02-01; 0056 臺灣高股息指數, FTSE TWSE Taiwan Dividend+ Index, 50 constituents, listed 2007-12-26 (not cited by a brief; the page does not itself say that all constituents are domestic). The visible text of none of the six pages mentions a currency hedge, an exchange rate or a fund currency (searched for 避險, 匯率, 幣別 and 計價幣; the pages' other tabs were not read); the book's text says nothing about hedging. The 0050 page's management fee carries a data date of 2026-10-22, so a later read can differ. The second source hunt reread 00635U and 00642U on 2026-10-24 with the same fields |
| Yuanta, LM34's futures funds: the fund pages of [00673R](https://www.yuantaetfs.com/product/detail/00673R/Basic_information) and [00674R](https://www.yuantaetfs.com/product/detail/00674R/Basic_information) (the URL pattern of the row above; HTTP 200 with their fields again on 2026-10-25; 00672L's page answers 查無此商品) and the prospectus of the umbrella fund 元大標普油金傘型期貨信託基金 (PDF, `Last-Modified` 2026-10-08) | 00673R (TWSE's short name 期元大S&P原油反1), index 標普高盛原油日報酬反向一倍ER指數 (S&P GSCI Crude Oil 1x Inverse Index ER), NYMEX WTI futures, listed 2016-10-07; 00674R (期元大S&P黃金反1), index 標普高盛黃金日報酬反向一倍ER指數 (S&P GSCI Gold 1x Inverse Index ER), COMEX gold futures, listed 2016-10-07. The prospectus cover says of each of 00672L (S&P GSCI crude oil ER, daily +2×), 00673R and 00674R 「本子基金為策略交易型產品，不適合長期持有」, and gives 00672L's FSC approval of 2020-10-07 (金管證期字第1090370507號) and its liquidation reference date, 2020-11-24. Read 2026-10-24 by the second source hunt |
| Fubon Financial press releases (fubon.com, 新聞中心) of 2016-12-06 and 2021-05-03 on 富邦標普500波動率短期期貨ER指數股票型期貨信託基金 (00677U) | 2016-12-06 (the offering): the index is 標普500波動率短期期貨ER指數, a VIX futures index and not the VIX itself; the fund holds near- and next-month VIX futures and rolls daily as the index does; 「該ETF不適合長期作為買方」. The release's risk notice gives the index's English title: 本基金之標的指數為「S&P 500 VIX Short-term Futures Index Excess Return」(標普 500 波動率短期期貨超額回報指數). 2021-05-03: 「期富邦VIX ETF(證券代號：00677U)」 was approved for delisting by TWSE on 2021-04-29, delisted from 2021-06-03, contract terminated 2021-06-04. Read 2026-10-24 by the second source hunt |
| [Fubon NASDAQ 00662 page](https://www.fubon.com/asset-management/ph/NASDAQ00662/index.html) | the fund table (an image titled 富邦Nasdaq-100基金; data date 2026.08) prints 證券簡稱 富邦NASDAQ, 證券代號 00662, 基金類型 跨國指數股票型(ETF), 追蹤標的指數 Nasdaq-100指數 and 成立日 2016.06.03; the page text gives the full name, 富邦NASDAQ-100證券投資信託基金 (in its 基金警語), and says 「本基金之標的指數為 Nasdaq-100指數」, so the issuer's own page gives the Nasdaq-100, as TWSE's fund page does. The five-for-one split comes after the data window: TWSE suspends trading 2026-11-11 → 11-16 and trading resumes 2026-11-17 (e添富 row above); Fubon's schedule gives 2026-11-10 as the planned last trading day (預計; 「實際時程可視情況調整」); a series extended past that date meets it. HTTP 200 on 2026-10-24; read by the second source hunt (LM35's drafter had found the page under maintenance, and this entry's first draft read only its marketing text) |
| USCF [USO page](https://www.uscfinvestments.com/uso) | the benchmark is the NYMEX light sweet crude futures contract that is the near month to expire, changing "over a five-day period" into the next month at the beginning of each month; operations began 2006-04-10; "On April 28, 2020, there was a 1-for-8 reverse share split", with historical NAV per share adjusted retroactively. Read 2026-10-24 by LM35's drafter and again for this entry (HTTP 200) |
| Invesco [DB Oil Fund (DBO) page](https://www.invesco.com/us/en/financial-products/etfs/invesco-db-oil-fund.html) (the old product-detail URL redirects here) | the fund seeks to track the DBIQ Optimum Yield Crude Oil Index Excess Return™ (Bloomberg DBCMOCLE; provider DBIQ) plus the interest income of its US Treasury and money-market holdings, less expenses; the index is "a rules-based index composed of futures contracts on light sweet crude oil (WTI)", and "The Fund and the Index are rebalanced and reconstituted annually in November"; inception 01/05/2007, NYSE Arca. **No roll rule is stated** beyond the name "Optimum Yield", so LM35 describes DBO by its data only and states no roll rule. The page adds: "Effective November 10, 2025, the Fund’s underlying index methodology has been updated", among other changes "the Optimum Yield approach was adjusted to remove contracts with limited liquidity": after the replayed years of 2008 and 2015. The fact sheet was not obtained (HTML or HTTP 406 to plain requests). HTTP 200 on 2026-10-24 for this entry (LM35's drafter reported that the page did not load; the description sits in the page's embedded data, not in its visible text) and read headless by the second source hunt the same day |
| NYSE, [Holidays & Trading Hours](https://www.nyse.com/markets/hours-calendars) | NYSE and NYSE Arca equities: core trading session 9:30 a.m. to 4:00 p.m. ET (the page also lists pre-opening, early and late sessions, and 1:00 p.m. early closes on 2025-07-03, 2025-11-28, 2025-12-24, 2026-11-27, 2026-12-24 and 2027-11-26); all times Eastern Time. LM27 §4 uses the 4:00 p.m. close; the page says nothing about Taipei time or daylight saving. Read 2026-10-24 by LM27's drafter and again for this entry (HTTP 200, static) |
| Yahoo Taiwan quote profile for 00679B (tw.stock.yahoo.com) | quoted in TWD |
| ProShares UltraPro QQQ (TQQQ) summary prospectus, 1 October 2022 (SEC EDGAR, f23121d1.htm) | expense ratio 0.98% gross, 0.86% net; objective three times the daily Nasdaq-100 return, index Bloomberg ticker NDX (read 2026-10-11) |
| Nasdaq, "NDX Index Versions" (indexes.nasdaq.com/docs/NDX%20Versions.pdf) | NDX is the price-return index (dividends excluded), XNDX the total-return version (read 2026-10-11) |
| Federal Reserve, open market operations page; FRED series FEDFUNDS | 2022 target-range moves (0–0.25% to 4.25–4.50%); 2022 monthly effective rate averaging 1.68% (read 2026-10-11) |
| Lee and Li newsletter 5323 (leeandli.com) | Banking Act Art. 47-1 cap |
| 法律百科 (legis-pedia.com, consumer-loan article) | card-rate rules (secondary) |
| 6laws.net | unofficial statute mirror; replaced by 全國法規資料庫 |

## News (Taiwan)

| Source | Used for |
|:--|:--|
| White House fact sheet, 2 April 2025 (whitehouse.gov; official, US) | the reciprocal tariffs behind the April 2025 sell-off: a 10% baseline from 5 April, higher country rates from 9 April (read 2026-10-11) |
| TechNews [2026-05-26 weight gap](https://finance.technews.tw/2026/05/26/weight-gap/) and SETN news 1844764 (2026-05-27) | 00631L replication: TAIEX futures 160.87%, TSMC 39.63%; TSMC weight 43.7% in TAIEX vs 60.9% in Taiwan 50 (as of 2026-05-19) |
| TechNews 2025-04-07 (black Monday records), Taiwan News zh/news/6078269 | 7 April 2025 tariff sell-off; TechNews reports 936 listed stocks (1,702 with the OTC market) closing limit-down that day (re-read 2026-10-18 for LM13–LM15: by Atkinson, 「台股黑色星期一創多項新紀錄，外資抄底轉買超 168.21 億元」, 936 listed and 766 OTC stocks, 1,702 in all). LM13 and LM14 cite it in one References form, "Atkinson (7 April 2025)" with the title and the TechNews link; LM15 points to LM14 for the cap (closing check, 2026-10-18) |
| TechNews 2022-12-30 (TWD depreciation), 2025-05-05 (TWD surge); FTV News 2025505W0BEA | USD/TWD 30.708 at end-2022; 31.064 on 2 May 2025; 30.145 on 5 May 2025 |
| TechNews 2025-06-10 (0050 one-into-four) | 0050 split timing |
| TechNews 2025-02-04, ctee.com.tw exchange/792949 and 20250204700571 | bond ETF background (LM7) |
| [money.udn.com story 9194923](https://money.udn.com/money/story/5607/9194923) (also 9006502) | TSMC ex-dividend effect on TAIEX, 40.34 points on 11 Dec 2025 |
| [旺得富 2026-09-17](https://wantrich.chinatimes.com/news/20260917900492-420501) | central-bank discount rate 2%, ten quarters unchanged |
| [NOWnews 6766337](https://www.nownews.com/news/6766337) | discount rate 2% through 2025 |
| PTS news 298694 and 743164 | 2015 limit change (superseded by TWSE's own pages) |
| ctee.com.tw 20250520701689, 20250617701663; hao.cnyes.com posts 141707, 177118 | third-party reports of 2025 TX margins |
| newtalk 2025-07-01/979200 | 30 June 2025 market close |
| acnnewswire (TWSE press release) | 2015 limit change |

## Standards, software and references

| Page | Used for |
|:--|:--|
| GIPS 2020 advertising guidelines comparison (gipsstandards.org PDF) | provision 8.A.4: periods under one year are not annualized |
| Spaulding Group, "Why don't we annualize returns of less than one year" | background for the same rule |
| [Microsoft Support: LOG function](https://support.microsoft.com/en-us/excel/functions/log-function) | Excel LOG defaults to base 10 |
| SciPy docs: [`integrate.quad`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.quad.html), [SLSQP](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-slsqp.html), [1.16.0 release notes](https://docs.scipy.org/doc/scipy/release/1.16.0-notes.html) | QUADPACK description; SLSQP returns multipliers |
| MacTutor, [History of e](https://mathshistory.st-andrews.ac.uk/HistTopics/e/); Britannica; Wikipedia (e, Mills ratio, Descartes' rule of signs, William Karush) | history and secondary checks |
| NumPy 2.5 reference: [`linalg.solve`](https://numpy.org/doc/2.5/reference/generated/numpy.linalg.solve.html), `lstsq`, `matrix_rank`, `pinv`, `cholesky`, `svd`, `eigh`, `cond`, `cov`, `corrcoef`, `var`, `std` (same URL pattern) | orders, defaults, tolerances and errors quoted in `plans/vol-2.md`, "Python facts"; checked against NumPy 2.5.3 (2026-10-11) |
| Polars API reference: [`polars.cov`](https://docs.pola.rs/api/python/dev/reference/expressions/api/polars.cov.html), `polars.corr`, `DataFrame.corr`, `DataFrame.var` | `ddof=1` defaults; `corr` has no `ddof`; no null rule is documented: in Polars 2.0.0 `pl.cov` and `pl.corr` drop nulls pair by pair, while `DataFrame.corr` returns NaN when a column has a null |
| LAPACK [`dgesv.f`](https://www.netlib.org/lapack/double/dgesv.f) (netlib) | "The LU decomposition with partial pivoting and row interchanges is used to factor A"; INFO = i when U(i,i) is exactly zero (read 2026-10-11) |
| NumPy 2.5 [`linalg.inv`](https://numpy.org/doc/2.5/reference/generated/numpy.linalg.inv.html) and [`linalg.det`](https://numpy.org/doc/2.5/reference/generated/numpy.linalg.det.html) | the inverse and the determinant, cited by LM9 and LM12 |
| SciPy [`linalg.solve_triangular`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.solve_triangular.html) (v1.18) | triangular solves with `lower=True`, cited by LM12 |
| SciPy [`linalg.cholesky`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.cholesky.html) (v1.18) | returns the upper factor by default |
| 樂詞網, [terms.naer.edu.tw](https://terms.naer.edu.tw/) (國家教育研究院) | Chinese terms of the 中文導讀 (AUTHORING §1); Volume II's list is in `plans/vol-2.md`, "Chinese terms" (searched 2026-10-11 and 12) |

## Papers and books (where bibliographic details were verified)

- Kelly (1956), *BSTJ* 35(4): 917–926 — archive.org `bstj35-4-917`.
- Breiman (1961), Fourth Berkeley Symposium, Vol. 1: 65–78; Kuhn & Tucker (1951), Second Berkeley Symposium: 481–492 — projecteuclid.org.
- Thorp (2006), *Handbook of Asset and Liability Management*, Vol. 1: 385–428 — PDF on gwern.net, sites.oxy.edu; Elsevier catalogue.
- MacLean, Thorp & Ziemba (2010), *Quantitative Finance* 10(7): 681–687, and the 2011 World Scientific volume — ideas.repec.org, arXiv 1112.0829.
- Almgren & Chriss (2000), *Journal of Risk* 3(2): 5–39 — risk.net, ideas.repec.org.
- Gopikrishnan et al. (1999), *PRE* 60: 5305–5316 — arXiv cond-mat/9905305, amaral.northwestern.edu; Gabaix et al. (2003), *Nature* 423: 267–270; Mandelbrot (1963), *J. Business* 36(4): 394–419 (PDF via williams.edu); Cont (2001), *QF* 1(2): 223–236 — ideas.repec.org.
- Gordon (1941), *Ann. Math. Stat.* 12(3): 364–366 — projecteuclid.org; Rosenlicht (1972), *AMM* 79: 963–972 (math.ucr.edu notes); Dowd et al. (2008), *JPM* 34(4): 76–80 — research.aston.ac.uk.
- Gordon (1959), *RES* 41(2): 99–105 — JSTOR 1927792; MacKinlay & Ramaswamy (1988), *RFS* 1(2): 137–158 — academic.oup.com, ideas.repec.org; Wang (2004), *AMM* 111(6): 525.
- Markowitz (1952), *JF* 7(1): 77–91; Merton (1972), *JFQA* 7(4): 1851–1872 — ideas.repec.org; Kjeldsen (2000), *Historia Mathematica* 27: 331–361 (PDF via u-szeged.hu); Chopra & Ziemba (1993), *JPM* 19 — pm-research.com; Boyd & Vandenberghe (2004) — Stanford PDF; Kraft (1988).
- Press et al., *Numerical Recipes* 3rd ed., §5.7 — PDF via drexel.edu; Burden, Faires & Burden, *Numerical Analysis* 10th ed.; Brent (1973); Stewart (Clegg, Watson), *Calculus: Early Transcendentals* 9th ed.; Simon & Blume (1994); Cover & Thomas (2006); Hull, *Options, Futures, and Other Derivatives* 11th ed. — publisher and library catalogues (Cengage, Pearson, Wiley, Elsevier, abebooks, university libraries) and course notes (NYCU, NTU, Villanova, UCSC, ETSU) for editions, ISBNs and chapter titles.
- Virtanen et al. (2020), "SciPy 1.0", *Nature Methods* 17(3): 261–272.
- Stewart, Clegg & Watson, *Calculus: Early Transcendentals*, 9th ed., Cengage, ISBN 9781337613927: the publisher's
  product page gives copyright 2021 (released 2020-01-09); every module cites it with these fields (Stewart, Clegg and
  Watson; 2021; 9th ed.; Cengage) in its own reference style (checked 2026-10-11).
- Spivak, *Calculus*, 4th ed., Publish or Perish, 2008, ISBN 978-0-914098-91-1 — the publisher's page
  (mathpop.com) and bookseller listings. Hull, *Options, Futures, and Other Derivatives*, 11th ed. (Global Edition),
  Pearson, print ISBN 9781292410654 — Pearson's catalogue gives copyright 2022 (published 5 July 2021). Modules cite
  them as Spivak (2008) and Hull (2022) (checked 2026-10-11).
- Volume II (checked 2026-10-11). Strang, *Introduction to Linear Algebra*, 5th ed., Wellesley-Cambridge Press, 2016, ISBN 978-0-9802327-7-6 — author's page math.mit.edu/~gs/linearalgebra/ila5/ (projections §4.2, Gram–Schmidt §4.4, positive definite matrices §6.5, SVD ch. 7 with PCA §7.3). Golub & Van Loan, *Matrix Computations*, 4th ed., Johns Hopkins University Press, 2013, ISBN 9781421407944 (symmetric eigenproblem ch. 8, symmetric QR algorithm §8.3). Higham, *Accuracy and Stability of Numerical Algorithms*, 2nd ed., SIAM, 2002, ISBN 0-89871-521-0, ch. 14 "Matrix Inversion", DOI 10.1137/1.9780898718027.ch14 (cited as Higham 2002a). Higham, "Computing the nearest correlation matrix — a problem from finance", *IMA J. Numer. Anal.* 22(3): 329–343, 2002, DOI 10.1093/imanum/22.3.329 (Higham 2002b). Rousseeuw & Molenberghs, "Transformation of non positive semidefinite correlation matrices", *Comm. Stat. Theory Methods* 22(4): 965–984, 1993, DOI 10.1080/03610928308831068 — Crossref. Horn & Johnson, *Matrix Analysis*, 2nd ed., Cambridge University Press, ISBN 9780521839402 (CUP lists October 2012, the copyright page 2013: cite 2013); ch. 7 covers positive definite and semidefinite matrices, and its theorem numbers were not checked against the 2nd edition. Strang's §6.1 sample chapter (author's page): Example 5 is the
  90° rotation. Strang & Herman, *Calculus Volume 3*, OpenStax, Houston, 2016 (published 30 March 2016; CC BY-NC-SA
  4.0, free online at openstax.org): §4.7 "Maxima/Minima Problems", Theorem 4.18 "Extreme Value Theorem" for two
  variables (read 2026-10-11). Golub & Van Loan's ch. 8 and §8.3 come from tables of contents (a 4th-edition summary
  and Cornell's GVL page), not from the book itself; §3.4 "Pivoting" comes from the 4th edition's table of contents
  on the distributor's page
  (woodslane.com.au/products/9781421407944, read 2026-10-12). TWSE's IndexS03 (2023.06), Appendix 1, lists the four
  sector indices launched with base date 2023-06-30 (綠能環保類, 數位雲端類, 運動休閒類, 居家生活類); IndexS02 (2023.04)
  gives TAIEX as total market value over the base value, times 100 (both re-read 2026-10-12).
- Volume III, books (read 2026-10-18). Blitzstein & Hwang, *Introduction to Probability*, 2nd ed., Chapman &
  Hall/CRC (CRC Press, Boca Raton, FL; Chapman & Hall/CRC Texts in Statistical Science), copyright 2019, 634 pp.,
  hardcover ISBN 978-1-138-36991-7, eBook ISBN 978-0-429-42835-7, DOI
  [10.1201/9780429428357](https://doi.org/10.1201/9780429428357) (Taylor & Francis datePublished 2019-02-08) — the
  [Routledge product page](https://www.routledge.com/Introduction-to-Probability-Second-Edition/Blitzstein-Hwang/p/book/9781138369917),
  the [Taylor & Francis eBook page](https://www.taylorfrancis.com/books/mono/10.1201/9780429428357) and Hitotsubashi
  University OPAC record 8000089761 ("Boca Raton, FL: CRC Press, [2019]"). Partly verified: the record is confirmed,
  the section numbers are *inferred* from the order of Routledge's unnumbered contents list and must be checked in the
  book before they are printed (§1.6 "Non-naive definition of probability"; §2.2 conditional probability, "Definition
  and intuition"; §2.3 "Bayes' rule and the law of total probability"; §2.5 "Independence of events"; §3.8
  "Independence of rvs"; §4.5 LOTUS, 2D LOTUS in §7.2; §4.7 "Poisson" and §4.8 "Connections between Poisson and
  Binomial"; §5.3 "Universality of the Uniform"; §7.5 "Multivariate Normal"; §10.1 "Inequalities", subsections not
  shown; §10.2 "Law of large numbers"; §10.3 "Central limit theorem"; §10.4 "Chi-Square and Student-t"). Not checked:
  whether §10.2 states both the weak and the strong law, and the theorem numbers. The free edition
  (probabilitybook.net redirects to a Google Drive file whose owner disabled downloads) could not be read;
  stat110.net and projects.iq.harvard.edu/stat110 returned 403 to automated requests.
- Grinstead & Snell, *Introduction to Probability: Second Revised Edition*, American Mathematical Society,
  Providence, RI, 1997, 510 pp., hardcover ISBN 978-0-8218-0749-1, softcover ISBN 978-0-8218-9414-9 (product code
  IPROB.S) — [AMS bookstore](https://bookstore.ams.org/IPROB); Open Library (secondary) gives LCCN 97008126 and
  xi + 510 pp. Verified and read in the free CHANCE Project edition ([prob.pdf](https://math.dartmouth.edu/~prob/prob/prob.pdf),
  version of 4 July 2006, Copyright (C) 2006 Peter G. Doyle, GNU Free Documentation License, 518 pp.), whose title
  page calls it a version of the AMS 2nd edition "Copyright (C) 2003 Charles M. Grinstead and J. Laurie Snell": its
  2003 differs from AMS's 1997. The AMS print pagination was not compared with the free PDF, so cite section and
  theorem numbers, not pages. Locations: no axioms as such (§1.2: Definition 1.2, the distribution function; Theorem 1.1,
  the properties of P); conditional probability §4.1 (continuous case §4.2); Bayes' formula §4.1; independence §4.1, Definitions 4.1–4.2
  (random variables Definitions 4.3–4.5; continuous case Definitions 4.6–4.8 and Theorems 4.2–4.3 in §4.2); LOTUS,
  without that name, §6.1 Theorem 6.1 (discrete) and §6.3 Theorem 6.11 (continuous); Chebyshev
  §8.1 Theorem 8.1 and §8.2 Theorem 8.3; Markov only as §8.2 Exercise 17; the "Weak Law of Large Numbers" §8.1
  Theorem 8.2 and §8.2 Theorem 8.4; the strong law stated, not proved (§2.1; §8.1 Exercise 15, with Exercise 16's
  sequence that satisfies the weak law but not the strong); Poisson approximation to the binomial §5.1 with Table 5.1;
  change of variables §5.2 Theorem 5.1 and the inverse transform as its Corollary 5.2, for F strictly increasing
  where 0 < F < 1 (pp. 210–212 of the CHANCE PDF, read again 2026-10-18 for LM18's review); independence of
  continuous random variables §4.2, Definition 4.7 and Theorem 4.2 (joint density the product of the marginals);
  central limit theorem §9.1 Theorems 9.1–9.2, §9.2 Theorems 9.4–9.5, §9.3
  Theorem 9.6. Not in the book (text search): Jensen's inequality and the multivariate normal. The old CHANCE book
  page (dartmouth.edu/~chance/) returns 404.
- Wasserman, *All of Statistics: A Concise Course in Statistical Inference*, Springer Texts in Statistics, Springer,
  New York, copyright 2004, xx + 442 pp., hardcover ISBN 978-0-387-40272-7 (published 4 December 2003), softcover ISBN
  978-1-4419-2322-6, eBook ISBN 978-0-387-21736-9, DOI
  [10.1007/978-0-387-21736-9](https://doi.org/10.1007/978-0-387-21736-9) — Springer's page and its
  [front matter PDF](https://link.springer.com/content/pdf/bfm:978-0-387-21736-9/1). Verified; the sections come from
  the table of contents: probability §1.3, independent events §1.5, conditional probability §1.6, Bayes' theorem §1.7,
  two important multivariate distributions §2.10, expectation §3.1, probability inequalities §4.1, inequalities for
  expectations §4.2, law of large numbers §5.3, central limit theorem §5.4, the bootstrap ch. 8 (§8.2 "Bootstrap
  Variance Estimation"). Not checked: what each section contains (for example Jensen in §4.2, the multivariate normal
  in §2.10) and the theorem numbers.
- Glasserman, *Monte Carlo Methods in Financial Engineering*, Springer, New York, 2003, Applications of Mathematics 53
  (Springer now lists the series as Stochastic Modelling and Applied Probability, vol. 53), xiii + 596 pp., hardcover
  ISBN 978-0-387-00451-8 (published 7 August 2003), softcover reprint ISBN 978-1-4419-1822-2, eBook ISBN
  978-0-387-21617-1, DOI [10.1007/978-0-387-21617-1](https://doi.org/10.1007/978-0-387-21617-1) — Springer's page and
  its [front matter PDF](https://link.springer.com/content/pdf/bfm:978-0-387-21617-1/1) with the full table of
  contents. Verified, sections and pages from that table of contents: inverse transform §2.2.1 (p. 54),
  acceptance-rejection §2.2.2 (p. 58), generating multivariate normals §2.3.3 (p. 71), control variates §4.1 (p. 185),
  antithetic variates §4.2 (p. 205), stratified sampling §4.3 (p. 209), importance sampling §4.6 (p. 255); ch. 4
  "Variance Reduction Techniques", pp. 185–280.
- Efron & Tibshirani, *An Introduction to the Bootstrap*, Monographs on Statistics and Applied Probability 57, Chapman
  & Hall, New York, 1993, xvi + 436 pp., ISBN 0-412-04231-2 — Open Library's record from the LC MARC (secondary; LCCN
  93004489). The publisher's current
  [Routledge page](https://www.routledge.com/An-Introduction-to-the-Bootstrap/Efron-Tibshirani/p/book/9780412042317)
  gives "Copyright 1994", 456 pages, ISBN 9780412042317, and the Taylor & Francis eBook (DOI
  [10.1201/9780429246593](https://doi.org/10.1201/9780429246593)) datePublished 1994-05-15: the 1994 dates belong to
  later printings and the reissue, so cite 1993. Partly verified: the chapters come from Routledge's ordered list of 26
  (ch. 4 "The Empirical Distribution Function and the Plug-In Principle", ch. 5 "Standard Errors and Estimated
  Standard Errors", ch. 6 "The Bootstrap Estimate of Standard Error", ch. 7 "Bootstrap Standard Errors: Some
  Examples", ch. 13 "Confidence Intervals Based on Bootstrap Percentiles"). §6.2 "The bootstrap estimate of standard
  error" was seen only in a secondary copy of the contents (Scribd), not in the book; Algorithm 6.1 and the equation
  number of the bootstrap standard error were not found. Cite "ch. 6" unless §6.2 is confirmed.
- Feller, *An Introduction to Probability Theory and Its Applications*, Vol. 1, 3rd ed., Wiley, New York, ISBN
  978-0-471-25708-0, hardcover, 528 pp. — [Wiley's page](https://www.wiley.com/en-us/An+Introduction+to+Probability+Theory+and+Its+Applications%2C+Volume+1%2C+3rd+Edition-p-9780471257080).
  Partly verified: Wiley shows "January 1991", a catalogue date, while Open Library (secondary) gives 1968 for the 3rd
  edition; the copyright page was not seen; cite Feller (1968). Wiley's contents list has no chapter numbers, so
  chapter and section numbers (for example a section on the Poisson approximation) were not checked.
- Volume III, papers (read 2026-10-18). Longin & Solnik, "Extreme Correlation of International Equity Markets", *JF*
  56(2): 649–676, April 2001, DOI [10.1111/0022-1082.00340](https://doi.org/10.1111/0022-1082.00340) — Crossref record
  and abstract. Verified: with extreme value theory for the tails they reject multivariate normality for the negative
  tail but not the positive; correlation is linked to the market trend, not to volatility as such, rising in bear
  markets but not in bull markets.
- Forbes & Rigobon, "No Contagion, Only Interdependence: Measuring Stock Market Comovements" (the full title includes
  the subtitle), *JF* 57(5): 2223–2261, October 2002, DOI [10.1111/0022-1082.00494](https://doi.org/10.1111/0022-1082.00494)
  — Crossref abstract. Verified: correlation coefficients are conditional on market volatility, so heteroskedasticity
  biases correlation-based contagion tests upward in crises; after the adjustment, unconditional correlations barely
  rose in the 1997 Asian crisis, the 1994 Mexican devaluation and the 1987 US crash, and the high comovement in all
  periods is what they call "interdependence".
- Boyer, Gibson & Loretan, "Pitfalls in Tests for Changes in Correlations", Board of Governors of the Federal Reserve
  System, *International Finance Discussion Papers* No. 597 — [index page](https://www.federalreserve.gov/pubs/ifdp/1997/597/default.htm)
  and [PDF](https://www.federalreserve.gov/pubs/ifdp/1997/597/ifdp597.pdf). Verified (read): the PDF's title page says
  first version December 1997, revised March 1999, while the Fed's index files it under 1997; cite 1999, the revised
  version, with "IFDP 597". Theorem 1 (§2.1, eq. 1): for bivariate normal x, y with constant correlation ρ,
  conditional on x ∈ A, ρ_A = ρ [ρ² + (1 − ρ²) Var(x)/Var(x | x ∈ A)]^(−1/2), so |ρ_A| > |ρ| when Var(x | A) > Var(x)
  and smaller otherwise; splitting a sample by large or small realizations produces an apparent correlation breakdown
  in i.i.d. data. The conditional correlation depends on the conditioning variable's conditional variance, not on
  "high or low" as such: conditioning on large |x| raises it, on a narrow band lowers it.
- Ang & Chen, "Asymmetric correlations of equity portfolios", *JFE* 63(3): 443–494, March 2002, DOI
  [10.1016/S0304-405X(02)00068-5](https://doi.org/10.1016/S0304-405X(02)00068-5) — abstract on
  [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0304405X02000685) and the
  [Columbia Business School page](https://business.columbia.edu/faculty/research/asymmetric-correlations-equity-portfolios);
  Crossref record. Verified: correlations between US stocks and the US market are much greater for downside moves,
  especially extreme ones, than for upside moves; conditional on the downside they differ from those implied by a
  normal distribution by 11.6%; small, value and past-loser stocks show more asymmetry; the asymmetries reject
  multivariate normality at daily, weekly and monthly frequencies, and regime-switching models capture them better.
- Ang & Chen (2002), definition read 2026-10-18 for LM16's closing check in the authors' working paper hosted by
  Columbia Business School
  ([corr.pdf](https://drupalgsb-test.paas.cc.columbia.edu/sites/default/files-efs/pubfiles/1516/corr.pdf), a
  test-server URL; its abstract is the published one, with the 11.6%, and it thanks a referee; journal pagination and
  equation numbers not compared): §3.1 "Upside and downside correlations", eq. (10), p. 7, defines the exceedance
  correlation at level ϑ, which it calls "the Longin and Solnik (2001) exceedance correlation": the correlation of two
  standardized returns when both lie more than ϑ standard deviations above their means (ϑ ≥ 0) or both below
  (ϑ ≤ 0); the empirical version uses cut-offs in standard deviations from the observed means. Longin & Solnik's own
  text was not read (CEPR DP 2538 and HEC's copy refused automated requests), so their part of LM16's attribution rests
  on Ang and Chen's.
- Gigerenzer & Hoffrage, "How to improve Bayesian reasoning without instruction: Frequency formats", *Psychological
  Review* 102(4): 684–704, 1995, DOI [10.1037/0033-295X.102.4.684](https://doi.org/10.1037/0033-295X.102.4.684) —
  Crossref record; abstract and text read in an author-posted copy marked "not the copy of record"
  ([pages.ucsd.edu](https://pages.ucsd.edu/~scoulson/203/GG_How_1995.pdf)). Corrected: the paper does not use the term
  "natural frequencies" (a text search finds none); its terms are "frequency formats" and "natural sampling", with
  "standard" and "short" menus. Study 1: 46% (standard menu) and 50% (short menu) Bayesian answers in frequency
  formats, against 16% and 28% in probability formats, so from 16% to 46% with the standard menu and from 28% to 50%
  with the short menu (each comparison within one menu). A text that says "natural frequencies" must attribute the term
  to later work, which was not checked.
- O'Neill, "PCG: A Family of Simple Fast Space-Efficient Statistically Good Algorithms for Random Number Generation",
  Technical Report HMC-CS-2014-0905, Harvey Mudd College Computer Science Department, Claremont, CA, issued
  5 September 2014, 58 pp. — [pcg-random.org/paper.html](https://www.pcg-random.org/paper.html) and the
  [report PDF](https://www.cs.hmc.edu/tr/hmc-cs-2014-0905.pdf). Verified (title page read): submitted to ACM TOMS; the
  author distributes the technical report, and no journal version is stated. NumPy's `PCG64` page cites it as
  reference [2]; NumPy uses the member "PCG XSL RR 128/64", of the family the report names PCG-XSL-RR.
- Peters, "The ergodicity problem in economics", *Nature Physics* 15(12): 1216–1221, a Perspective published online
  2 December 2019 (received 29 September 2018, accepted 28 October 2019), DOI
  [10.1038/s41567-019-0732-0](https://doi.org/10.1038/s41567-019-0732-0), paywalled — the
  [article page](https://www.nature.com/articles/s41567-019-0732-0) metadata and the
  [Fig. 2 caption](https://www.nature.com/articles/s41567-019-0732-0/figures/2); full text read in a third-party
  annotated copy (cyclostationarity.com). Related: Author Correction, *Nat. Phys.* 16(1): 111, DOI
  10.1038/s41567-019-0769-0 (online 6 December 2019); Matters Arising by Doctor, Wakker & Wang, "Economists' views on
  the ergodicity problem", *Nat. Phys.* 16: 1168 (2020), DOI 10.1038/s41567-020-01106-x, which criticizes the
  Perspective. Verified: eq. (2) defines the gamble Δx = +0.5x or −0.4x, each with probability 1/2; ⟨Δx⟩ = +0.05x per
  round, while the expected change in log wealth is ½ ln 0.9 = −0.0527 per round (a typical factor √0.9 ≈ 0.949);
  Fig. 2 shows 150 trajectories of 1,000 rounds, the ensemble average growing while the time-average growth rate gives
  the decay of a typical trajectory.
- Hill, "A Simple General Approach to Inference About the Tail of a Distribution", *Ann. Statist.* 3(5): 1163–1174,
  September 1975, DOI [10.1214/aos/1176343247](https://doi.org/10.1214/aos/1176343247) — Crossref record and abstract
  (the Project Euclid page could not be fetched: bot challenge). Verified: inference uses only the tail behaviour,
  notably for Zipf-type tails 1 − G(y) = C y^(−α), through the conditional likelihood given the extreme order
  statistics. Not checked: the estimator's formula in the paper's text.
- Durrett, *Probability: Theory and Examples*, 5th ed., Cambridge Series in Statistical and Probabilistic Mathematics
  49, Cambridge University Press, 2019 (online 5 April, print 18 April 2019), 430 pp., hardback ISBN
  978-1-108-47368-2, eBook ISBN 978-1-108-59103-4, DOI [10.1017/9781108591034](https://doi.org/10.1017/9781108591034)
  — Crossref record and the [CUP page](https://www.cambridge.org/core/books/probability/DD9A1907F810BB14CCFF022CDFC5677A).
  Verified (read 2026-10-18) in the author's free PDF ([PTE5_011119.pdf](https://sites.math.duke.edu/~rtd/PTE/PTE5_011119.pdf),
  "Version 5 January 11, 2019", from [his page](https://sites.math.duke.edu/~rtd/PTE/pte.html)) and in Google Books'
  snippets of the CUP edition, which use the same numbers. §2.4, Theorem 2.4.1 (Etemadi): pairwise independent,
  identically distributed, E|Xᵢ| < ∞ ⇒ Sₙ/n → EXᵢ a.s. (print p. 65); §2.5, Theorem 2.5.10: the same for iid (print
  p. 74); Theorem 2.3.8: E|Xᵢ| = ∞ ⇒ P(|Xₙ| ≥ n i.o.) = 1, so E|Xᵢ| < ∞ is necessary; Theorem 2.2.14: the weak law
  for iid with E|Xᵢ| < ∞. The PDF's pages differ from print: cite theorem numbers. Also read in the PDF (2026-10-18;
  this number not compared with the print edition): §2.1.4 "Constructing Independent Random Variables" asks whether
  independent random variables exist and builds an infinite sequence X₁, X₂, … with given distribution functions on
  ℝ^ℕ by Theorem 2.1.21 (Kolmogorov's extension theorem): consistent probability measures μₙ on (ℝⁿ, ℛⁿ) have a unique
  extension P to (ℝ^ℕ, ℛ^ℕ). LM13 cites it for the existence of infinitely many independent trades, with "numbered as
  in the author's free PDF" (closing check CX6; the print number stays unchecked: Google Books answered with a
  CAPTCHA on 2026-10-18).
- Blitzstein & Hwang, section numbers now verified (read 2026-10-18) in the authors' free edition. probabilitybook.net
  redirects to [Google Drive](https://drive.google.com/file/d/1VmkAAGOYCTORq1wxSQqy255qLJjTNvBI/view): file "Blitzstein
  Hwang Probability.pdf", shared from the first author's account, downloads disabled, read through the viewer's page
  images. Its title page reads "Second Edition ... © 2019 by Taylor & Francis Group, LLC". Its printed contents
  (pp. vii–ix) confirm every section number above, and Recap, R and Exercises are numbered sections. Read in the text:
  Theorem 4.5.1 LOTUS (discrete); Theorem 5.3.1 universality of the Uniform (F continuous, strictly increasing);
  §10.1.1 Cauchy–Schwarz (Theorem 10.1.1), §10.1.2 Jensen (Theorem 10.1.5, equality iff g(X) = a + bX with
  probability 1), §10.1.3 Markov (Theorem 10.1.10, P(|X| ≥ a) ≤ E|X|/a), Chebyshev (10.1.11), Chernoff (10.1.12);
  §10.2 assumes iid with finite mean and **finite variance** and states the strong law (Theorem 10.2.1) and the weak
  law (Theorem 10.2.2, proved by Chebyshev), plus item 10.2.4 on the gambler's fallacy; §10.3, Theorem 10.3.1 (CLT,
  proved assuming an MGF; the MGF-to-CDF step is omitted). Not compared: the free edition's pages against the print.
- Efron & Tibshirani, section and algorithm verified (read 2026-10-18) in Google Books' snippet view of the Chapman &
  Hall/CRC printing ([gLlpIUxRntoC](https://books.google.com/books?id=gLlpIUxRntoC)). CIP "QA276.8.E3745 1993 ...
  93-4489", ISBN 0-412-04231-2, preface dated June 1993. §6.2 "The bootstrap estimate of standard error" (p. 45);
  Algorithm 6.1 "The bootstrap algorithm for estimating standard errors" (p. 47); (6.6) se_B = {Σ_b [θ̂*(b) −
  θ̂*(·)]²/(B − 1)}^{1/2}, θ̂*(·) = Σ_b θ̂*(b)/B; (6.7) se_B → the ideal bootstrap estimate se_F̂(θ̂*) as B → ∞;
  Figure 6.1 (p. 48). Wasserman's (8.1) (§8.2, p. 109) divides by B instead.
- Wasserman, locations verified (read 2026-10-18) in Google Books snippets of ISBN 978-0-387-40272-7
  ([th3fbFI1DaMC](https://books.google.com/books?id=th3fbFI1DaMC)): the three axioms in §1.3 (p. 5), Definition 1.5,
  whose third axiom is additivity over a sequence of disjoint events (countable additivity; read for LM13's
  verification); Theorem 1.8,
  continuity of probabilities (p. 7, before §1.4's heading); §2.10 (pp. 39–40), the N(μ, Σ) density (2.10) for Σ
  symmetric positive definite and Theorem 2.43 (X = μ + Σ^{1/2}Z ~ N(μ, Σ), and conversely); Chebyshev Theorem 4.2
  (p. 64); Jensen Theorem 4.9 (p. 66); WLLN Theorem 5.6 (§5.3, p. 76, proof assumes σ < ∞); CLT Theorem 5.8 (§5.4,
  p. 77); **strong law Theorem 5.18** (§5.7.1, p. 81): iid with E|X₁| < ∞ ⇒ X̄ₙ → μ a.s.; bootstrap variance (8.1)
  (§8.2, p. 109, divisor B).
- Grinstead & Snell, further locations (CHANCE PDF, read 2026-10-18): §6.3 Theorem 6.10 (for real-valued random
  variables with densities, E(X + Y) = E(X) + E(Y) and E(cX) = cE(X); "The proof is very similar to the proof of
  Theorem 6.2, and we omit it"; no independence is assumed), which LM14 cites for (14.3) with densities;
  §4.1 Theorem 4.1 (independence iff product),
  Exercise 7 (pairwise but not mutually independent), Exercise 17 (complements of independent events), Exercise 33;
  §8.2 Example 8.8 (the average of n standard Cauchy variables is standard Cauchy; also §7.2 Example 7.6 and §10.3 by
  characteristic functions); §10.3 "Sketch of the Proof of the Central Limit Theorem" (bounded continuous variables,
  mgf convergence; the step to distributions not proved).
- Glasserman (2003), §2.2.1, pp. 54–55: the inverse transform for a general distribution function, with the
  generalized inverse (2.14) and Figure 2.6; §4.1.3 "Small-Sample Issues", p. 200: the bias from estimating the
  control-variate coefficient is typically of order 1/n, against a standard error of order 1/√n (Google Books search
  within [e9GWUsQkPNMC](https://books.google.com/books?id=e9GWUsQkPNMC), read 2026-10-18 for LM18's review).
- Durrett (2019), Theorem 1.7.2: Fubini's theorem, for f ≥ 0 or ∫|f| < ∞ (read in the author's free PDF,
  2026-10-18, for LM16's verification; numbered as in that PDF).
- Durrett (2019), §3.10 "Limit Theorems in R^d", read 2026-10-18 for Volume III's closing check in the author's free
  PDF (numbered and paged as in that PDF, not compared with the print edition): Theorem 3.10.4 (p. 199), the
  inversion formula for characteristic functions on R^d; Theorem 3.10.7 (pp. 200–201), the central limit theorem in
  R^d, whose limit is multivariate normal with mean 0 and covariance Γ, that is with characteristic function
  exp(−θΓθᵀ/2). The text that follows (pp. 201–202) shows that a covariance matrix Γ is symmetric and nonnegative
  definite and, for every such Γ (degenerate allowed), builds the law as YA from independent standard normal Y,
  showing that each linear combination is normal; it gives the density (2π)^(−d/2)(det Γ)^(−1/2)exp(−yΓ⁻¹yᵀ/2) only
  when Γ has rank d and reduces degenerate cases to that one by a linear map. Exercise 3.10.7 (p. 202): the entries of
  a multivariate normal vector are independent if and only if they are uncorrelated. Exercise 3.10.8 (p. 203): a
  vector is multivariate normal with mean vector θ and covariance Γ if and only if every linear combination c·X is
  normal with mean cθᵀ and variance cΓcᵀ. The two are exercises, stated with the proof left to the reader. LM16 cites
  §3.10 and Exercise 3.10.8 for its two stated facts (independent normals are jointly normal; μ and Σ fix the law),
  for every positive semidefinite Σ, and keeps Wasserman for the density.
- Durrett (2019), Theorem 2.2.3: the L² weak law for uncorrelated random variables with a common mean and bounded
  variances (read in the author's free PDF, 2026-10-18, for LM17's review; numbered as in that PDF, and LM17's
  References say so since the closing check, CX6; a web search did not find the print number).
- Glasserman (2003), §4.2, p. 207 (Google Books snippet, [e9GWUsQkPNMC](https://books.google.com/books?id=e9GWUsQkPNMC),
  read 2026-10-18): antithetic sampling reduces variance when Cov(Yᵢ, Ỹᵢ) < 0 (4.29); "A simple sufficient condition
  ensuring this is monotonicity of the mapping from inputs to outputs".
- Glasserman (2003), §9.1.2 "Calculating VAR" (from p. 484, table of contents): on p. 491 the asymptotic interval for
  a quantile estimate needs the density at the quantile, and "to avoid this step, one may divide the sample of n
  observations into batches, compute an estimate … from each batch, and form a confidence interval based on the sample
  standard deviation of the estimates across batches"; the central limit theorem for quantile estimation is (9.7)
  (so named on p. 500; the index places it at p. 490). Google Books search within
  [e9GWUsQkPNMC](https://books.google.com/books?id=e9GWUsQkPNMC), read 2026-10-18 for LM18's closing check; LM18 cites
  §9.1.2 for a quantile's 1/n variance and its batch standard error.
- Glasserman (2003), §4.6.1 "Principles and First Examples" (from p. 255): p. 256, the second moment of an
  importance-sampling estimator against plain sampling ("depending on the choice of g it might even be infinitely
  larger or smaller"); Example 4.6.1, p. 260, "Normal distribution: change of mean", with its likelihood ratio (4.83).
  The closed form of the shifted normal's second moment for a tail was not found in the snippets, so LM18 cites §4.6
  for the method only and derives the formula itself (same search, read 2026-10-18 for LM18's closing check).

## Papers and books (Volume IV)

Checked 2026-10-19 by the Stage 1 survey. Bibliographic data come from Crossref unless another source is named;
Stage 1 read the Crossref record of every DOI below again (2026-10-19): volume, issue, pages and year agree with the
survey everywhere Crossref holds them, and the titles of the LM23–LM26 entries, which the survey recorded without
titles, are Crossref's. For several JSTOR DOIs Crossref holds only the first page; the end page's source is then
named, or marked "end page not in Crossref". "Abstract" marks a claim read only in an abstract: for LM19–LM22, in
OpenAlex's copy, not compared with the publisher's page; for LM23–LM26, in the copy named, or in one the survey did
not name. "Bibliographic data only" means nothing in the text was read.

### LM19 and LM20

- Lo & MacKinlay, "Stock Market Prices Do Not Follow Random Walks: Evidence from a Simple Specification Test", *RFS*
  1(1): 41–66, January 1988, DOI [10.1093/rfs/1.1.41](https://doi.org/10.1093/rfs/1.1.41). Abstract: tests the random
  walk on weekly returns by comparing variance estimators at different sampling frequencies; strongly rejected for
  1962–1985; largely due to small stocks, but not fully explained by infrequent trading or time-varying volatility. The
  equation numbers for VR(q), z(q) and z\*(q) are unconfirmed (text not read).
- Lo, "The Statistics of Sharpe Ratios", *FAJ* 58(4): 36–52, 2002, DOI
  [10.2469/faj.v58.n4.2453](https://doi.org/10.2469/faj.v58.n4.2453). Abstract: monthly Sharpe ratios "cannot be
  annualized by multiplying by √12 except under very special circumstances"; in an illustrative example of mutual
  funds and hedge funds, "the annual Sharpe ratio for a hedge fund can be overstated by as much as 65 percent"
  because of serial correlation (LM19's annualization rule; LM33). The abstract was confirmed on the journal's own
  article page and the text read for LM33: see "Entries already in this list: Volume VI locations".
- Campbell, Lo & MacKinlay, *The Econometrics of Financial Markets*, Princeton University Press, ©1997 (published
  29 December 1996), 632 pp., ISBN 978-0-691-04301-2 — Princeton UP's page; section numbers unconfirmed (its contents
  are images only). Chapters from Project MUSE (titles as the survey shortened them): ch. 5 CAPM,
  pp. 181–218; ch. 6 Multifactor, pp. 219–252; ch. 12 Nonlinearities, pp. 467–526.
- Merton, "On estimating the expected return on the market: An exploratory investigation", *JFE* 8(4): 323–361,
  December 1980, DOI [10.1016/0304-405X(80)90007-0](https://doi.org/10.1016/0304-405X(80)90007-0) (Crossref's title
  omits the subtitle). Read in NBER Working Paper 444 (February 1980), Appendix A, "Estimating the Variance Rate From
  Time Series of Realized Returns": with n = h/Δ observations, Var[μ̂] = σ²/h (A.3), and "nothing is gained in terms
  of accuracy of the expected return estimate by choosing finer observation intervals"; the variance estimator's
  accuracy depends on n, (A.4)–(A.5); annual data give a standard deviation of the variance estimate "approximately
  nineteen times larger" than daily data (p. A4). The journal's pages and equation numbers were not compared.
- Rao, "Information and the Accuracy Attainable in the Estimation of Statistical Parameters", reprinted in
  *Breakthroughs in Statistics*, Springer Series in Statistics, Springer, 1992, pp. 235–247, DOI
  [10.1007/978-1-4612-0919-5_16](https://doi.org/10.1007/978-1-4612-0919-5_16) — the reprint is verified; the original
  (*Bull. Calcutta Math. Soc.*, 1945) is **unverified**.
- Embrechts, Klüppelberg & Mikosch, *Modelling Extremal Events for Insurance and Finance*, Springer, Berlin Heidelberg,
  1997, Applications of Mathematics 33 (now Stochastic Modelling and Applied Probability 33), softcover ISBN
  978-3-642-08242-9, eBook ISBN 978-3-642-33483-2, DOI
  [10.1007/978-3-642-33483-2](https://doi.org/10.1007/978-3-642-33483-2) — front-matter PDF (4th corrected and 9th
  printing, 2012): §6.4.2 "Estimating the Shape Parameter ξ", p. 327. That the Hill estimator sits in §6.4.2 is
  **unconfirmed**.
- Drees, de Haan & Resnick, "How to make a Hill plot", *Ann. Statist.* 28(1): 254–274, February 2000, DOI
  [10.1214/aos/1016120372](https://doi.org/10.1214/aos/1016120372). Crossref lists the authors as Drees, Resnick, de
  Haan; check the order on the title page.
- Bibliographic data only: Lo & MacKinlay, "The size and power of the variance ratio test in finite samples",
  *J. Econometrics* 40(2): 203–238, 1989, DOI
  [10.1016/0304-4076(89)90083-3](https://doi.org/10.1016/0304-4076(89)90083-3); Fisher, "Theory of Statistical
  Estimation", *Proc. Camb. Phil. Soc.* 22(5): 700–725, 1925, DOI
  [10.1017/S0305004100009580](https://doi.org/10.1017/S0305004100009580); Cramér, *Mathematical Methods of Statistics*
  (PMS-9), Princeton University Press, 1946, DOI [10.1515/9781400883868](https://doi.org/10.1515/9781400883868).

### LM21

- Harvey, Liu & Zhu, "… and the Cross-Section of Expected Returns" (the title starts with the ellipsis), *RFS* 29(1):
  5–68, January 2016 (online 9 October 2015), DOI [10.1093/rfs/hhv059](https://doi.org/10.1093/rfs/hhv059). Abstract:
  "A new factor needs to clear a much higher hurdle, with a t-statistic greater than 3.0"; "most claimed research
  findings in financial economics are likely false". Section numbers unconfirmed (the PDF returned 403).
- White, "A Reality Check for Data Snooping", *Econometrica* 68(5): 1097–1126, September 2000, DOI
  [10.1111/1468-0262.00152](https://doi.org/10.1111/1468-0262.00152). Abstract: tests the null that the best model
  found in a specification search has no predictive superiority over a benchmark.
- Sullivan, Timmermann & White, "Data-Snooping, Technical Trading Rule Performance, and the Bootstrap", *JF* 54(5):
  1647–1691, 1999, DOI [10.1111/0022-1082.00163](https://doi.org/10.1111/0022-1082.00163). Abstract: applies the
  Reality Check to technical rules on 100 years of daily DJIA data, expanding Brock et al.'s 26 rules.
- Romano & Wolf, "Stepwise Multiple Testing as Formalized Data Snooping", *Econometrica* 73(4): 1237–1282, 2005, DOI
  [10.1111/j.1468-0262.2005.00615.x](https://doi.org/10.1111/j.1468-0262.2005.00615.x). Abstract: a stepwise procedure
  that asymptotically controls the FWER; more powerful than single-step methods; studentization advocated; set in
  strategies against a benchmark.
- Holm, "A Simple Sequentially Rejective Multiple Test Procedure", *Scand. J. Statist.* 6(2): 65–70, 1979, JSTOR
  4615733; **no registered DOI** (doi.org returns 404 for 10.2307/4615733, which OpenAlex lists; Crossref also returned
  404, read again in Stage 1). First page read in a JSTOR copy (ime.usp.br): "Scand J Statist 6: 65-70, 1979"; the
  procedure gives a prescribed level of protection against errors of the first kind for any combination of true
  hypotheses.
- Benjamini & Hochberg, "Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing",
  *JRSS B* 57(1): 289–300, 1995, DOI
  [10.1111/j.2517-6161.1995.tb02031.x](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x). Abstract: the FDR equals
  the FWER when all nulls are true and is smaller otherwise; the procedure is proved for **independent** test
  statistics.
- Benjamini & Yekutieli, "The control of the false discovery rate in multiple testing under dependency", *Ann.
  Statist.* 29(4): 1165–1188, 2001, DOI [10.1214/aos/1013699998](https://doi.org/10.1214/aos/1013699998) — Crossref
  record; SciPy's `false_discovery_control` cites its Theorem 1.3 for `'by'`.
- Harvey & Liu, "Backtesting", *JPM* 42(1): 13–28, 2015 (Crossref: print and online 31 October 2015), DOI
  [10.3905/jpm.2015.42.1.013](https://doi.org/10.3905/jpm.2015.42.1.013). Read for LM33 by the source check and the
  LM33 drafter in the JPM layout hosted at Duke; its headings re-read by Stage 1's fresh check (2026-10-31) in the
  copy on Harvey's Duke pages (people.duke.edu/~charvey/Research/Published_Papers/P120_Backtesting.PDF; its footers
  name the layout file "JPM-HARVEY.indd"). **Cited by section and equation, not by page:** that copy's running heads
  number its 17 pages 12–28 (its first page prints 12, "Fall 2015"), while Crossref, whose issue listing places the
  article after two editorials on pp. 1–4 and 5–6 and lists nothing on pp. 7–12, gives 13–28, and the journal's own
  pages were not compared; the copy's page labels below, as the source check recorded them, only locate the passages
  in that copy. Its headings in order, with the copy page on which each starts (sections set in capitals, subsections
  in mixed case): an untitled introduction (p. 12); METHOD (p. 13); MULTIPLE TESTING FRAMEWORK (p. 14), with "Type I
  Error" (p. 15), "P-value Adjustment under FWER" (p. 15), "P-value Adjustment under FDR" (p. 16), "Multiple Testing
  and Cross-Validation" (p. 17) and "In-Sample Multiple Testing versus Out-of-Sample Validation" (p. 17);
  APPLICATIONS (p. 18), with "Three Strategies" (p. 18), "Sharpe Ratio Adjustment for a New Strategy" (p. 19) and
  "Minimum Profitability for Proposed Trading Strategies" (p. 21); CONCLUSIONS (p. 22); PROGRAMS (p. 23), with
  "Haircut Sharpe Ratios" (p. 23), "Profit Hurdles" (p. 23) and "Correlation Adjustment" (p. 24), the material the
  text calls "the appendix" (no heading in the copy's text says "Appendix"); ENDNOTES (p. 25); REFERENCES (p. 26).
  METHOD holds the t-statistic `μ̂/(σ̂/√T)` with `T − 1` degrees of freedom, (1); the Sharpe ratio, (2); the
  single-test p-value, (3); `p^M = 1 − (1 − p^S)^N` for `N` independent tests, (4); the haircut Sharpe ratio, solving
  (5); the haircut `(SR − HSR)/SR`, worked as `(0.75 − 0.32)/0.75` (copy pp. 13–14; in words in the introduction,
  p. 12); and the example (240 months, Sharpe ratio 0.75: `p^S = 0.0008`; with `N = 200`, `p^M = 0.15`, HSR 0.32, a
  haircut of about 60%), reproduced with the normal reference (A33-55). MULTIPLE TESTING FRAMEWORK holds the FWER
  and the FDR ("Type I Error", copy p. 15); Bonferroni and Holm ("P-value Adjustment under FWER", copy p. 15, Holm's
  comparison with Bonferroni ending on p. 16); BHY ("P-value Adjustment under FDR", copy p. 16); and, in that
  subsection, the model of 300-plus factors of Harvey, Liu & Zhu that gives Holm and BHY the other p-values (copy
  p. 16). LM33 uses Bonferroni and the independent-tests form directly, labels Holm on the eight rules' own p-values
  as the book's adaptation, and cites the equations (1)–(5) and the sections of the methods it uses. LM34 cites the
  paper by pointer.
- Hansen, P. R., "A Test for Superior Predictive Ability", *JBES* 23(4): 365–380, October 2005, DOI
  [10.1198/073500105000000063](https://doi.org/10.1198/073500105000000063). Read for LM34 by the source check in the
  University of North Carolina repository's postprint, which carries the journal's layout without page numbers; its
  16 pages are counted from 365 (the journal's range has 16 pages). The loss differences `d_k,t` (the benchmark's
  loss minus model `k`'s) and the null `μ ≤ 0`, eq. (1), p. 367; the statistic, the largest studentized mean
  difference floored at 0, p. 368; the consistent version recentres only the models whose t-statistic is at or above
  `−√(2 log log n)` (his `n` is the number of returns), p. 368, and in the bootstrap form, §3, p. 372; the
  logarithm comes from the law of the iterated logarithm (p. 370), so it is natural; the lower and upper versions give
  bounds (Theorem 2, p. 371), and only the recentred one a consistent p-value (Corollary 2); the stationary
  bootstrap, a recommended kernel estimate of each variance and validity of the test without it, pp. 371–372; the
  p-value counts resamples strictly above the statistic over `B`, with no "+1", p. 372. LM34's A34-25 follows him
  except for the iid standard deviation and the count "at or above", which gives the same 0.277; E7 says both.
- Bibliographic data only: Harvey, "Presidential Address: The Scientific Outlook in Financial Economics", *JF* 72(4):
  1399–1440, 2017, DOI [10.1111/jofi.12530](https://doi.org/10.1111/jofi.12530); Romano & Wolf, "Exact and
  Approximate Stepdown Methods for Multiple Hypothesis Testing", *JASA* 100(469): 94–108, 2005, DOI
  [10.1198/016214504000000539](https://doi.org/10.1198/016214504000000539); Neyman & Pearson, "On the problem of the
  most efficient tests of statistical hypotheses", *Phil. Trans. R. Soc. A* 231: 289–337, 1933, DOI
  [10.1098/rsta.1933.0009](https://doi.org/10.1098/rsta.1933.0009); Wasserstein & Lazar, "The ASA Statement on
  p-Values: Context, Process, and Purpose", *Am. Stat.* 70(2): 129–133, 2016, DOI
  [10.1080/00031305.2016.1154108](https://doi.org/10.1080/00031305.2016.1154108).

### LM22

- Künsch, "The Jackknife and the Bootstrap for General Stationary Observations", *Ann. Statist.* 17(3): 1217–1241,
  1989, DOI [10.1214/aos/1176347265](https://doi.org/10.1214/aos/1176347265) (Crossref spells the name "Kunsch").
  Abstract (the IMS abstract Crossref holds, re-read 2026-10-19), in order: the jackknife and the bootstrap extended to
  general stationary sequences; the jackknife omits each block of l consecutive data once; for the mean, that is a
  weighted covariance estimate of the spectral density at zero; "Under appropriate conditions consistency is obtained
  if l = l(n) → ∞ and l(n)/n → 0"; general statistics approximated by a mean; only then the bootstrap, which selects
  blocks of length l with replacement. The consistency sentence names no method and precedes the bootstrap, so the
  abstract ties the conditions to the jackknife and states no bootstrap consistency result. The paper's theorems were
  not read (Project Euclid blocked the requests). For block-bootstrap consistency cite Lahiri (2003), below.
- Politis & Romano, "The Stationary Bootstrap", *JASA* 89(428): 1303–1313, 1994, DOI
  [10.1080/01621459.1994.10476870](https://doi.org/10.1080/01621459.1994.10476870). Abstract: blocks of random length
  with a geometric distribution; the pseudo-series is stationary conditional on the data. Re-read 2026-10-19 on Taylor &
  Francis's page (OpenAlex's copy is identical): weakly dependent stationary observations; the article develops
  "fundamental consistency and weak convergence properties" of the scheme. Theorem numbers and conditions not read.
- Politis & White, "Automatic Block-Length Selection for the Dependent Bootstrap", *Econometric Reviews* 23(1): 53–70,
  2004, DOI [10.1081/ETC-120028836](https://doi.org/10.1081/ETC-120028836). Abstract: optimal block-size estimators
  built on flat-top lag-window spectral estimation. With the next entry, the reference of arch's
  `optimal_block_length` ("Python (Volume IV)").
- Patton, Politis & White, "Correction to 'Automatic Block-Length Selection for the Dependent Bootstrap' by D. Politis
  and H. White", *Econometric Reviews* 28(4): 372–375, 2009, DOI
  [10.1080/07474930802459016](https://doi.org/10.1080/07474930802459016). Abstract: corrects the block-size algorithms
  after Nordman's correction of Lahiri (1999).
- Efron, "Better Bootstrap Confidence Intervals", *JASA* 82(397): 171–185, 1987, DOI
  [10.1080/01621459.1987.10478410](https://doi.org/10.1080/01621459.1987.10478410). Abstract: the new intervals are
  second-order correct (the origin of BCa).
- Ledoit & Wolf, "Robust performance hypothesis testing with the Sharpe ratio", *J. Empirical Finance* 15(5): 850–859,
  December 2008, DOI [10.1016/j.jempfin.2008.03.002](https://doi.org/10.1016/j.jempfin.2008.03.002) (Crossref spells
  the first author "Oliver"). Read first, for LM22, in IEW Working Paper 320 (January 2008): Jobson–Korkie, as
  corrected by Memmel (2003), is invalid under heavy tails or time-series data; they propose a studentized time-series
  bootstrap interval for the difference of two Sharpe ratios. Read in the journal text by the Volume VI source check
  (2026-10-24; the published article hosted at UZH, running pages 850–859; received 7 May 2007, accepted 18 March 2008,
  online 26 March 2008, p. 850), whose numbers replace the working paper's: the parameter is a function of the means
  and uncentred second moments, (1)–(2), with the delta method (4) and the standard error (5), §3, pp. 851–852; finite
  fourth moments for iid data, and `4 + δ` moments with a mixing condition for time series, p. 852; HAC inference
  (§3.1, pp. 852–853) with a kernel estimate and a `T/(T − 4)` degrees-of-freedom factor, Bartlett named as the
  `q = 1` kernel, the p-value `2Φ(−|Δ̂|/s(Δ̂))` and the interval `Δ̂ ± z s(Δ̂)` (p. 853, unnumbered); the bootstrap test
  inverts a symmetric studentized interval, (6)–(7), resampling the observed data (§3.2, p. 853); §3.2.2, p. 854: the
  circular block bootstrap of Politis & Romano (1992) on blocks of return pairs with a fixed block size `b`, footnote
  7 on circular rather than moving blocks (edge effects; the working paper's footnote 5), footnote 8 on a prewhitened
  Parzen kernel, and the original-data standard error by Andrews & Monahan's (1992) prewhitened quadratic-spectral
  kernel; the Götze–Künsch standard error in each resample on the `⌊T/b⌋` complete blocks (the journal prints `n`
  for `T`), the resample centred at its own estimates, (8), with footnote 9 (`b = 1` is the iid case); Algorithm 3.1,
  pp. 854–855, calibrates `b` on a fitted model (grid {1, 2, 4, 6, 8, 10} for `T = 120`); Remark 3.2, eq. (9), p. 855,
  the p-value `(#{d̃* ≥ d} + 1)/(M + 1)` (the journal omits the "#"), with `M = 499` and `T = 120` in the simulations
  (§4). The paper does not say how a resample is cut when `T` is not a multiple of `b`. LM33 prints the bootstrap test
  beside the HAC one and labels three settings as the book's (Bartlett with `ℓ = 7`; `b` by LM22's rule; the
  resample length when `T` is not a multiple of `b`).
- Jobson & Korkie, "Performance Hypothesis Testing with the Sharpe and Treynor Measures", *JF* 36(4): 889–908, 1981,
  DOI [10.1111/j.1540-6261.1981.tb04891.x](https://doi.org/10.1111/j.1540-6261.1981.tb04891.x) — bibliographic data
  only. Memmel (2003) is **unverified**.
- Lahiri, *Resampling Methods for Dependent Data*, Springer Series in Statistics, Springer, New York, ©2003, DOI
  [10.1007/978-1-4757-3803-2](https://doi.org/10.1007/978-1-4757-3803-2); the reprint's front matter gives softcover
  ISBN 978-1-4419-1848-2, eBook ISBN 978-1-4757-3803-2, LCCN 2003045455; the original hardcover ISBN was not seen.
  Contents (front-matter PDF): §2.5 the moving block bootstrap, p. 25; §2.7.1 circular, p. 33; §2.7.2 stationary,
  p. 34; §3.3 the stationary bootstrap for the sample mean, p. 57; ch. 5 comparison of block methods, p. 115; ch. 7
  "Empirical Choice of the Block Size", p. 175 (§7.3 subsampling, p. 182; §7.4 nonparametric plug-in, p. 186). Read
  2026-10-19 in Google Books' preview (id e4f8sqm439UC; pp. 49, 55, 58, 64 as page images); the CIP data on p. iv give
  ISBN 0-387-00928-0, © 2003 Springer-Verlag New York. Chapter 3, "Properties of Block Bootstrap Methods for the
  Sample Mean": $\{X_i\}$ stationary and strongly mixing with coefficient $\alpha(\cdot)$, $T_n=\sqrt n(\bar X_n-\mu)$;
  $j=1,2,3,4$ the moving, non-overlapping, circular and stationary block bootstraps.
  - Theorem 3.1 (p. 49): $E\lVert X_1\rVert^{2+\delta}<\infty$ and $\sum\alpha(n)^{\delta/(2+\delta)}<\infty$ for some
    $\delta>0$, with $\ell^{-1}+n^{-1}\ell=o(1)$, give $\Var_*(T^*_n(j))\to_p\Sigma_\infty$ for $j=1,2,3$.
  - Theorem 3.2 (p. 55): the same conditions and a nonsingular $\Sigma_\infty$ give the bootstrap distribution's
    uniform consistency for $j=1,2,3$; the text adds that the conditions on $\ell$ are also necessary.
  - Theorem 3.3 (p. 58), "a stronger set of conditions": $E\lVert X_1\rVert^{4+\delta}<\infty$,
    $\sum n^3\alpha(n)^{\delta/(4+\delta)}<\infty$ and $p+(n^{1/2}p)^{-1}\to0$ ($1/p$ the mean block length) give the
    stationary bootstrap's variance consistency; Theorem 3.4 (p. 64) its distribution result under
    $6+\delta$ moments. These are sufficient conditions; TR23's tails (LM15's $\nu=3.065$) do not meet the moment
    condition of Theorem 3.3, while Theorem 3.1's holds for small $\delta$.
- Bibliographic data only: Hall, Horowitz & Jing, "On blocking rules for the bootstrap with dependent data",
  *Biometrika* 82(3): 561–574, 1995, DOI [10.1093/biomet/82.3.561](https://doi.org/10.1093/biomet/82.3.561); Efron,
  "Bootstrap Methods: Another Look at the Jackknife", *Ann. Statist.* 7(1): 1–26, 1979, DOI
  [10.1214/aos/1176344552](https://doi.org/10.1214/aos/1176344552); DiCiccio & Efron, "Bootstrap confidence
  intervals", *Stat. Sci.* 11(3): 189–228, 1996, DOI [10.1214/ss/1032280214](https://doi.org/10.1214/ss/1032280214).

### LM23

- White, "A Heteroskedasticity-Consistent Covariance Matrix Estimator and a Direct Test for Heteroskedasticity",
  *Econometrica* 48(4): 817–838, 1980, DOI [10.2307/1912934](https://doi.org/10.2307/1912934); pages also on the
  Econometric Society's page (Crossref gives the first page only). Abstract: a covariance estimator that stays
  consistent under heteroskedasticity, plus a direct test.
- Newey & West, "A Simple, Positive Semi-Definite, Heteroskedasticity and Autocorrelation Consistent Covariance
  Matrix", *Econometrica* 55(3): 703–708, 1987, DOI [10.2307/1913610](https://doi.org/10.2307/1913610); end page not in
  Crossref; 703–708 on RePEc, NBER's page and the Econometric Society's page. Abstract: positive semi-definite by
  construction and consistent. The weights are read in the working paper (Stage 3, round 1, below); the journal text
  was not reached. The Society's web page lists West first; Crossref has Newey, West.
- Andrews, "Heteroskedasticity and Autocorrelation Consistent Covariance Matrix Estimation", *Econometrica* 59(3):
  817–858, 1991, DOI [10.2307/2938229](https://doi.org/10.2307/2938229); end page not in Crossref (RePEc gives 817–858,
  and the issue's next article starts at p. 859). Abstract: optimal
  kernel and bandwidth, and data-dependent automatic bandwidths. The plug-in constants (for example 1.1447) are
  unconfirmed.
- Lintner, "The Valuation of Risk Assets and the Selection of Risky Investments in Stock Portfolios and Capital
  Budgets", *REStat* 47(1): 13–37, 1965, DOI [10.2307/1924119](https://doi.org/10.2307/1924119). The end page came
  from JSTOR's citation string as carried by OpenAlex, which on 2026-10-19 gave 13–13; Crossref's issue listing starts
  the next article at p. 38, which is consistent with 37. Bibliographic data only.
- Hansen, B. E., "A Modern Gauss–Markov Theorem", *Econometrica* 90(3): 1283–1294, 2022, DOI
  [10.3982/ECTA19255](https://doi.org/10.3982/ECTA19255); Pötscher & Preinerstorfer's comment, *Econometrica* 92(3):
  913–924 (2024 in Crossref), DOI [10.3982/ECTA20819](https://doi.org/10.3982/ECTA20819), with Hansen's reply at
  925–928 (its DOI not recorded). Bibliographic data only: read them before LM23 states Gauss–Markov for anything
  beyond linear estimators.
- Hayashi, *Econometrics*, Princeton University Press, 712 pp., ISBN 978-0-691-01018-2; the publisher's page says
  published 19 November 2000, copyright 2001 (the copyright page was not seen). Contents from a bookseller (Eyrolles,
  secondary): §1.3 "Finite-Sample Properties of OLS", p. 27 (Gauss–Markov is not named in the contents); ch. 6 "Serial
  Correlation", p. 365, with "Using Kernels to Estimate S", p. 408; ch. 9 "Unit-Root Econometrics", p. 557 (Dickey–Fuller
  tests §9.3, ADF §9.4); ch. 10 "Cointegration", p. 623. Theorem and equation numbers unconfirmed.
- Greene, *Econometric Analysis*, 8th ed., Pearson, ©2018 (published 29 March 2017), ISBN 978-0-13-446136-6.
  Pearson's contents: ch. 3 Least Squares; ch. 4 Estimating the Regression Model by Least Squares; ch. 9 Generalized
  Regression and Heteroscedasticity; ch. 16 Bayesian (title as the survey shortened it); ch. 20 Serial Correlation;
  ch. 21 Nonstationary Data. Theorem numbers unconfirmed.
- Wooldridge, *Introductory Econometrics*, 8th ed., Cengage, c2025, xxi + 916 pp., ISBN 978-0-357-90016-1 (CiNii).
  Chapters not checked.
- Bibliographic data only: Newey & West, "Automatic Lag Selection in Covariance Matrix Estimation", *RES* 61(4):
  631–653, 1994, DOI [10.2307/2297912](https://doi.org/10.2307/2297912); Sharpe, "Capital Asset Prices: A Theory of
  Market Equilibrium under Conditions of Risk", *JF* 19(3): 425–442, 1964, DOI
  [10.1111/j.1540-6261.1964.tb02865.x](https://doi.org/10.1111/j.1540-6261.1964.tb02865.x); Fama & French, "Common
  risk factors in the returns on stocks and bonds", *JFE* 33(1): 3–56, 1993, DOI
  [10.1016/0304-405X(93)90023-5](https://doi.org/10.1016/0304-405X(93)90023-5).

### LM24

- James & Stein, "Estimation with Quadratic Loss" (title from the reprint's Crossref record), Fourth Berkeley
  Symposium, Vol. 1: 361–379. The end page is unresolved: two library records give 379, one set of course notes 380.
  Project Euclid's page and PDF are blocked from here. The reprint in *Breakthroughs in Statistics* (1992), pp.
  443–460, DOI [10.1007/978-1-4612-0919-5_30](https://doi.org/10.1007/978-1-4612-0919-5_30), is verified. BDA3 cites
  the paper as "James and Stein (1960)". Breiman (1961), already in this list, is in the same volume.
- Efron & Morris, "Data Analysis Using Stein's Estimator and its Generalizations", *JASA* 70(350): 311–319, 1975, DOI
  [10.1080/01621459.1975.10479864](https://doi.org/10.1080/01621459.1975.10479864). Read in the Taylor & Francis PDF (a
  course-site copy): Table 1 gives 18 players' averages after their first 45 at-bats of 1970; the Stein rule's mean
  squared error is less than half that of the sample mean.
- Efron & Morris, "Stein's Paradox in Statistics", *Scientific American* 236(5): 119–127, 1977, DOI
  [10.1038/scientificamerican0577-119](https://doi.org/10.1038/scientificamerican0577-119). Content not seen.
- Efron & Morris, "Stein's Estimation Rule and its Competitors—An Empirical Bayes Approach", *JASA* 68(341): 117–130,
  1973, DOI [10.1080/01621459.1973.10481350](https://doi.org/10.1080/01621459.1973.10481350) (the empirical Bayes view).
  Bibliographic data only.
- Jorion, "Bayes-Stein Estimation for Portfolio Analysis", *JFQA* 21(3): 279–292, 1986, DOI
  [10.2307/2331042](https://doi.org/10.2307/2331042); the end page comes from the RePEc handle (Crossref gives the
  first page only). Abstract: an empirical Bayes estimator should outperform the sample mean in a portfolio setting.
  The shrinkage target (the minimum-variance portfolio's mean) is confirmed only by secondary sources. **Warning:**
  10.1017/S0022109000012138 is the issue's front matter (Crossref: "JFQ volume 21 issue 3 Cover and Front matter"),
  not this article.
- Gelman et al., *Bayesian Data Analysis*, 3rd ed., Chapman & Hall/CRC Texts in Statistical Science, ©2013, 675 pp.,
  ISBN 978-1-4398-4095-5. The authors offer a free PDF for non-commercial use (errata fixed to 20 February 2025; its
  pages may differ from print), at <https://sites.stat.columbia.edu/gelman/book/BDA3.pdf>; re-read in Stage 3, round 1
  (below). The survey confirmed in that PDF: §2.5 "Normal distribution
  with known variance", p. 39; eq. (2.10), p. 40: "the posterior precision equals the prior precision plus the data
  precision"; §3.3 normal data with a conjugate prior, p. 67; §5.5 the eight schools, p. 119; §5.8 the bibliographic
  note on Stein.
- MacLean, Thorp & Ziemba (2010), already in this list (with Kelly 1956) without a DOI: its DOI is
  [10.1080/14697688.2010.506108](https://doi.org/10.1080/14697688.2010.506108), title "Long-term capital growth: the
  good and bad properties of the Kelly and fractional Kelly capital growth criteria" (Crossref).

### Fractional Kelly and parameter uncertainty (LM24)

What each source claims; no source found derives fractional Kelly as *the* Bayesian answer, which fits ROADMAP's
"only inside a stated model". LM24 cites Browne and Whitt (1996) for the posterior-mean rule under log utility.

- Browne & Whitt, "Portfolio choice and the Bayesian Kelly criterion", *Adv. Appl. Prob.* 28(4): 1145–1176, 1996, DOI
  [10.2307/1428168](https://doi.org/10.2307/1428168). Abstract: with log utility and unknown parameters the optimal
  bet is "a linear function of the posterior mean increment", a generalisation of Kelly; it is not fractional Kelly.
- MacLean, Ziemba & Blazenko, "Growth Versus Security in Dynamic Investment Analysis", *Mgmt Sci.* 38(11): 1562–1585,
  1992, DOI [10.1287/mnsc.38.11.1562](https://doi.org/10.1287/mnsc.38.11.1562). Abstract: fractional Kelly trades
  growth against security; the abstract does not mention parameter uncertainty.
- Thorp (2006), already in this list: §7.3 "The case for 'fractional Kelly'", read in the PDF on gwern.net. Prudential,
  not derived: overbetting costs more than underbetting; if mₑ is uncertain, choose f < fₑ; half Kelly keeps 3/4 of the
  growth rate.
- MacLean, Thorp & Ziemba (2010): wagers should be reduced because E log is so sensitive to errors in the mean.
  Prudential; read in the January 2010 working version only.
- Kan & Zhou, "Optimal Portfolio Choice with Parameter Uncertainty", *JFQA* 42(3): 621–656, 2007, DOI
  [10.1017/S0022109000004129](https://doi.org/10.1017/S0022109000004129). Abstract: the plug-in portfolio does poorly;
  under uncertainty, the riskless asset plus the sample tangency portfolio is never optimal; a three-fund rule.
  Mean–variance, not log utility.
- Rising & Wyner, "Partial Kelly portfolios and shrinkage estimators", 2012 IEEE International Symposium on
  Information Theory Proceedings: 1618–1622, DOI [10.1109/ISIT.2012.6283549](https://doi.org/10.1109/ISIT.2012.6283549).
  Abstract (OpenAlex): fractional Kelly works "not because of reduced risk, but because of reduced estimation error".
- Baker & McHale, "Optimal Betting Under Parameter Uncertainty: Improving the Kelly Criterion", *Decision Analysis*
  10(3): 189–199, 2013, DOI [10.1287/deca.2013.0271](https://doi.org/10.1287/deca.2013.0271). Abstract: shrink the
  bet to improve out-of-sample performance.
- Chu, Wu & Swartz, "Modified Kelly criteria", *JQAS* 14(1): 1–11, 2018, DOI
  [10.1515/jqas-2017-0122](https://doi.org/10.1515/jqas-2017-0122). Abstract: decision-theoretic; the modified
  fractions are smaller than Kelly in the cases studied and depend on the loss function.
- Han, Yu & Mathew, "Shrinkage estimation of Kelly portfolios", *QF* 19(2): 277–287 (2019 in Crossref; the survey
  gave no year), DOI [10.1080/14697688.2018.1483583](https://doi.org/10.1080/14697688.2018.1483583). Abstract: plug-in
  Kelly weights are biased; proposes a shrinkage estimator.

### LM25

- Said & Dickey, "Testing for unit roots in autoregressive-moving average models of unknown order", *Biometrika*
  71(3): 599–607, 1984, DOI [10.1093/biomet/71.3.599](https://doi.org/10.1093/biomet/71.3.599). Abstract: the test
  approximates the ARMA by an autoregression.
- Dickey & Fuller, "Distribution of the Estimators for Autoregressive Time Series with a Unit Root", *JASA* 74(366a):
  427–431, 1979, DOI [10.1080/01621459.1979.10482531](https://doi.org/10.1080/01621459.1979.10482531). Abstract read
  (its content not recorded by the survey).
- Kwiatkowski, Phillips, Schmidt & Shin (KPSS), "Testing the null hypothesis of stationarity against the alternative of
  a unit root", *J. Econometrics* 54(1–3): 159–178, 1992, DOI
  [10.1016/0304-4076(92)90104-Y](https://doi.org/10.1016/0304-4076(92)90104-Y) (authors from Crossref). Abstract not
  seen; the limit law is read in the working paper (revision 2, below).
- MacKinnon, "Numerical distribution functions for unit root and cointegration tests", *JAE* 11(6): 601–618, 1996, DOI
  [`10.1002/(SICI)1099-1255(199611)11:6<601::AID-JAE417>3.0.CO;2-T`](https://doi.org/10.1002/(SICI)1099-1255(199611)11:6%3C601::AID-JAE417%3E3.0.CO;2-T).
  Abstract: response surfaces giving finite-sample and asymptotic critical values and p-values.
- MacKinnon, "Critical Values for Cointegration Tests", Queen's Economics Department Working Paper 1227, 2010 — the
  IDEAS abstract says a new appendix is "more accurate" and covers more cases; Queen's own page failed its TLS
  certificate check. statsmodels takes its critical values from it ("Python (Volume IV)").
- Ljung & Box, "On a measure of lack of fit in time series models", *Biometrika* 65(2): 297–303, 1978, DOI
  [10.1093/biomet/65.2.297](https://doi.org/10.1093/biomet/65.2.297); it modifies Box & Pierce, "Distribution of
  Residual Autocorrelations in Autoregressive-Integrated Moving Average Time Series Models", *JASA* 65(332): 1509–1526,
  1970, DOI [10.1080/01621459.1970.10481180](https://doi.org/10.1080/01621459.1970.10481180).
- Hamilton, *Time Series Analysis*, Princeton University Press, 1994, ISBN 978-0-691-04289-3, 816 pp. Chapters from
  Project MUSE (titles as the survey shortened them): 3 Stationary ARMA, pp. 43–71; 10 Covariance-Stationary Vector
  Processes, pp. 257–290; 17 Unit Roots, pp. 475–543; 19 Cointegration, pp. 571–629; 20 FIML for cointegrated
  systems, pp. 630–656; 21 Heteroskedasticity, pp. 657–676. Newey–West: §10.5, [10.5.15], pp. 281–283, and p. 220;
  unit roots with drift: §17.4, Cases 3 and 4, pp. 495–497 (Stage 3, round 1, below). Other theorem and equation
  numbers unconfirmed.
- Box, Jenkins, Reinsel & Ljung, *Time Series Analysis: Forecasting and Control* (title from Open Library's ISBN
  record, secondary, read again in Stage 1), 5th ed., Wiley, 720 pp., ISBN 978-1-118-67502-1. Wiley says June 2015;
  library catalogues say 2016. Chapters not checked.
- Tsay, *Analysis of Financial Time Series* (title from Open Library's ISBN record, secondary, read again in Stage 1),
  3rd ed., Wiley, August 2010, 720 pp., ISBN 978-0-470-41435-4. Sections from Kinokuniya's contents (secondary):
  §2.1–2.7 (pp. 30–71) stationarity, the ACF, white noise, AR, MA, ARMA and unit roots; §2.10 consistent covariance
  matrix estimation, p. 97; ch. 3 conditional heteroscedastic models, p. 109 (IGARCH §3.6, p. 140); §7.2 RiskMetrics,
  p. 328; §8.5–8.6 cointegration, pp. 428–432; §8.8 pairs trading, p. 446; §10.1 exponentially weighted estimate,
  p. 506.
- Futures–spot basis: Brenner & Kroner, "Arbitrage, Cointegration, and Testing the Unbiasedness Hypothesis in
  Financial Markets", *JFQA* 30(1): 23–42, 1995, DOI [10.2307/2331251](https://doi.org/10.2307/2331251) (end page not
  in Crossref) — RePEc abstract: whether spot and futures prices are cointegrated depends on the time-series properties
  of the cost of carry. Dwyer, Locke & Yu, "Index Arbitrage and Nonlinear Dynamics Between the S&P 500 Futures and
  Cash", *RFS* 9(1): 301–332, 1996, DOI [10.1093/rfs/9.1.301](https://doi.org/10.1093/rfs/9.1.301) — abstract:
  threshold error correction, minute-by-minute S&P 500 data. Martens, Kofman & Vorst (1998), *JAE* 13(3): 245–263 —
  abstract read; the title and DOI were not recorded by the survey. Lin, Chen & Hwang, "An Application of Threshold
  Cointegration to Taiwan Stock Index Futures and Spot Markets", *Rev. Pacific Basin Fin. Mkts. Policies* 6(3):
  291–304, 2003, DOI [10.1142/S0219091503001109](https://doi.org/10.1142/S0219091503001109) — abstract: Taiwan index
  futures, 5-minute data, threshold cointegration. Roope & Zurbruegg, "The intra-day price discovery process between
  the Singapore Exchange and Taiwan Futures Exchange", *JFM* 22(3): 219–240, 2002, DOI
  [10.1002/fut.2215](https://doi.org/10.1002/fut.2215) — abstract: SGX and TAIFEX Taiwan index futures share a common
  stochastic trend with the index.
- Bibliographic data only: Engle & Granger, "Co-Integration and Error Correction: Representation, Estimation, and
  Testing", *Econometrica* 55(2): 251–276, 1987, DOI [10.2307/1913236](https://doi.org/10.2307/1913236) (end page not
  in Crossref); Johansen, "Statistical analysis of cointegration vectors", *JEDC* 12(2–3): 231–254, 1988, DOI
  [10.1016/0165-1889(88)90041-3](https://doi.org/10.1016/0165-1889(88)90041-3); Johansen, "Estimation and Hypothesis
  Testing of Cointegration Vectors in Gaussian Vector Autoregressive Models", *Econometrica* 59(6): 1551–1580, 1991,
  DOI [10.2307/2938278](https://doi.org/10.2307/2938278) (end page not in Crossref); MacKinnon, "Approximate
  Asymptotic Distribution Functions for Unit-Root and Cointegration Tests", *JBES* 12(2): 167–176, 1994, DOI
  [10.1080/07350015.1994.10510005](https://doi.org/10.1080/07350015.1994.10510005) (statsmodels' p-values); Wahab &
  Lashgari, "Price dynamics and error correction in stock index and stock index futures markets: A cointegration
  approach", *JFM* 13(7): 711–742, 1993, DOI [10.1002/fut.3990130702](https://doi.org/10.1002/fut.3990130702).

### LM26

- *RiskMetrics — Technical Document*, 4th ed., J.P. Morgan/Reuters, New York, 17 December 1996 (PDF hosted by MSCI at
  <https://www.msci.com/documents/10199/5915b101-4206-4ba0-aee2-3449d5c7e95a>, file "td4e.pdf"; re-read in Stage 3,
  round 1, below). The survey confirmed: §5.3.2 "Choosing the decay factor", p. 97: λ = 0.94 for the daily
  data set and 0.97 for the monthly; the criterion is the root mean squared error of the variance forecast, Eq. [5.30]
  in §5.3.2.1; the single λ is a weighted average across 480+ series, Eqs. [5.32]–[5.35]; Table 5.9, p. 100: 550 days
  used in production, 75 effective at 0.94; Eq. [5.23]: σ²ₜ₊₁|ₜ = 0.94σ²ₜ|ₜ₋₁ + 0.06r²ₜ.
- Engle, "Autoregressive Conditional Heteroscedasticity with Estimates of the Variance of United Kingdom Inflation",
  *Econometrica* 50(4): 987–1007, 1982, DOI [10.2307/1912773](https://doi.org/10.2307/1912773). JSTOR's cover page
  ("Vol. 50, No. 4 (Jul., 1982), pp. 987-1007", read 2026-10-19 in a JSTOR-downloaded copy on a university site) and
  RePEc give 987–1007; the Econometric Society's page gives 987–1008 (the next article starts at p. 1009); Crossref
  gives the first page only.
- Andersen & Bollerslev, "Answering the Skeptics: Yes, Standard Volatility Models do Provide Accurate Forecasts",
  *IER* 39(4): 885–905, 1998, DOI [10.2307/2527343](https://doi.org/10.2307/2527343) (end page not in Crossref). Read
  in a JSTOR copy: the out-of-sample R-squared of GARCH(1,1) against squared returns is 0.047 (DM–$) and 0.026 (¥–$);
  against 5-minute realized volatility the models explain "about half"; there is a theoretical upper bound on
  R-squared under conditional normality, but its value is garbled in the copy read.
- Andersen, Bollerslev, Diebold & Labys, "Modeling and Forecasting Realized Volatility", *Econometrica* 71(2): 579–625,
  2003, DOI [10.1111/1468-0262.00418](https://doi.org/10.1111/1468-0262.00418). Abstract read (its content not recorded
  by the survey).
- Andersen, Bollerslev, Diebold & Labys, "Great Realisations", *Risk*, 2000, issue (3): 105–108 (Kellogg listing).
  Volume 13 is unverified. That this article introduced the signature plot is **unconfirmed**. Hansen and Lunde's 2004
  working paper (below) says the plots "were introduced by" Andersen, Bollerslev, Diebold and Labys (2000) and cites
  "Great realizations", *Risk* 13(3): 105–108: a secondary source for both points.
- Zhang, Mykland & Aït-Sahalia (Lan Zhang, Per A. Mykland, Yacine Aït-Sahalia; Crossref writes "Per A"), "A Tale of Two Time
  Scales", *JASA* 100(472): 1394–1411, 2005, DOI
  [10.1198/016214505000000169](https://doi.org/10.1198/016214505000000169); the subtitle "Determining Integrated
  Volatility With Noisy High-Frequency Data" is printed on p. 1394 (Crossref omits it). Read in the published PDF
  (<https://www.princeton.edu/~yacine/twoscales.pdf>, re-read 2026-10-19): the five estimators, §1.2; §1.2.5 "The
  First-Best Approach: Subsampling and Averaging, and Bias-Correction", p. 1396: `TSRV = [Y,Y]^avg −
  (n̄/n)[Y,Y]^all`, over "the two time scales"; Section 4, p. 1402, the theory; the small-sample adjustment, eq. (64), §4.2;
  K = c·n^(2/3), with rate n^(−1/6).
- Patton, "Volatility forecast comparison using imperfect volatility proxies", *J. Econometrics* 160(1): 246–256,
  2011, DOI [10.1016/j.jeconom.2010.03.034](https://doi.org/10.1016/j.jeconom.2010.03.034). Abstract read on Duke's
  page. MSE and QLIKE as members of a robust family are confirmed in the 2006 working version (Section 3); the
  published text was not seen. Working paper: Quantitative Finance Research Centre, University of Technology Sydney,
  Research Paper 175, April 2006 (RePEc uts:rpaper:175; title page "This version: 13 April, 2006"), read 2026-10-19 at
  <https://www.uts.edu.au/sites/default/files/qfr-archive-02/QFR-rp175.pdf>: Definition 1, p. 4, a loss is robust if
  it ranks forecasts by expected loss as the true conditional variance would, with "some conditionally unbiased
  volatility proxy"; Section 3, p. 13, assumption A1 $E_{t-1}[\hat\sigma_t^2]=\sigma_t^2$; Propositions 2–3, p. 14 (MSE
  the only robust loss in the forecast error, QLIKE the only one in the standardized error); QLIKE, eq. (6), p. 6:
  $\log h_t+\hat\sigma_t^2/h_t$.
- Hansen & Lunde, "A forecast comparison of volatility models: does anything beat a GARCH(1,1)?", *JAE* 20(7):
  873–889, 2005, DOI [10.1002/jae.800](https://doi.org/10.1002/jae.800). Abstract: 330 ARCH-type models compared; for
  DM–$ no evidence that GARCH(1,1) is beaten; for IBM, GARCH(1,1) is inferior to models with a leverage effect.
- Hansen & Lunde, "Realized Variance and Market Microstructure Noise", *JBES* 24(2): 127–161, 2006, DOI
  [10.1198/073500106000000071](https://doi.org/10.1198/073500106000000071). Abstract (OpenAlex's copy, read 2026-10-19;
  the publisher's page was blocked): in the Dow Jones Industrial Average stocks, microstructure noise is
  time-dependent and correlated with increments in the efficient price. The September 2004 working paper (NYU Stern
  copy) says the same of the 30 stocks and means serial dependence of the noise (p. 2 and the conclusion).
- Bibliographic data only: Bollerslev, "Generalized autoregressive conditional heteroskedasticity", *J. Econometrics*
  31(3): 307–327, 1986, DOI [10.1016/0304-4076(86)90063-1](https://doi.org/10.1016/0304-4076(86)90063-1);
  Barndorff-Nielsen & Shephard, "Econometric Analysis of Realized Volatility and its Use in Estimating Stochastic
  Volatility Models", *JRSS B* 64(2): 253–280, 2002, DOI
  [10.1111/1467-9868.00336](https://doi.org/10.1111/1467-9868.00336).

### Stage 1 additions to the papers (2026-10-19, after the briefs)

Bibliographic data come from Crossref (`api.crossref.org/works/<doi>`, read 2026-10-19) unless another source is named.

#### The t and χ² laws of normal samples (X32)

- Blitzstein & Hwang (2019). Read 2026-10-19 in the authors' free edition, the Google Drive file recorded above. Its page images were fetched headless through the viewer. Page numbers are as printed on the images; the print edition was not compared.
  - §7.5, Theorem 7.5.7 (pp. 339–341): "Within an MVN random vector, uncorrelated implies independent."
  - Example 7.5.9, "Independence of sample mean and sample variance" (p. 342). For X₁,…,Xₙ iid 𝒩(μ,σ²), n ≥ 2, with S²ₙ = Σ(Xⱼ − X̄ₙ)²/(n − 1): "Show that X̄ₙ and S²ₙ are independent by applying MVN ideas to (X̄ₙ, X₁ − X̄ₙ, …, Xₙ − X̄ₙ)". The text solves it.
  - §10.4, "Chi-Square and Student-t" (p. 477). Definition 10.4.1 defines χ²ₙ as a sum of n squared iid 𝒩(0,1). Theorem 10.4.2: "The χ²ₙ distribution is the Gamma(n/2, 1/2) distribution."
  - Example 10.4.3, "Distribution of sample variance" (pp. 478–479): "Show that (n − 1)S²ₙ/σ² ∼ χ²ₙ₋₁". It is solved with Example 7.5.9 and MGFs, and the text adds that E(S²ₙ) = σ² (its Theorem 6.3.4).
  - Definition 10.4.4, Student-t (p. 479): T = Z/√(V/n), with Z ∼ 𝒩(0,1), V ∼ χ²ₙ and Z independent of V. The tₙ density is printed "though we will not prove this". Theorem 10.4.5 (pp. 479–480) gives symmetry, t₁ = Cauchy, and convergence to the normal.
  - **Not stated in the book:** the tₙ₋₁ law of √n(X̄ₙ − μ)/Sₙ. On p. 479 the text says "we do not introduce the details of t-tests here since they are better left for a course on statistical inference". The exercises seen (19–37, pp. 491–494) do not state it either. It follows in one line from Ex. 7.5.9, Ex. 10.4.3 and Def. 10.4.4, taking Z = √n(X̄−μ)/σ and V = (n−1)S²/σ². A module can cite those three items and show that line.
  - LM24's χ² density: only Theorem 10.4.2 (Gamma(n/2, 1/2)) was read. The Gamma density itself (§8.4) was not read.
- Casella & Berger and Wasserman were not reached. No legitimate free copy was found, and the Google Books API answered 429 (daily quota). Their theorem numbers stay open.

#### LM19 (added)

- Kim & White, "On more robust estimation of skewness and kurtosis", *Finance Research Letters* 1(1): 56–73, March 2004, DOI [10.1016/S1544-6123(03)00003-5](https://doi.org/10.1016/S1544-6123(03)00003-5).
  - Text not read: no free copy was found, and IDEAS lists access as restricted.
  - Secondary source: statsmodels 0.15.0's `robust_skewness` and `robust_kurtosis` pages cite it. They print SK₂ = [(q.75 − q.5) − (q.5 − q.25)]/(q.75 − q.25) and KR₂ = [(q.875 − q.625) + (q.375 − q.125)]/(q.75 − q.25).
- Moors, "A Quantile Alternative for Kurtosis", *The Statistician* 37(1): 25–?, 1988, DOI [10.2307/2348376](https://doi.org/10.2307/2348376).
  - **End page unresolved.** Crossref and OpenAlex give only the first page, and JSTOR answered with a bot challenge.
  - Read instead in the 1987 discussion paper, Tilburg *Ter discussie FEW* 87.08 ([Tilburg repository PDF](https://repository.tilburguniversity.edu/bitstreams/56d6c0a6-9d7b-4d6a-b194-0a19231563ca/download), an OCR of a scan):
    - octiles Eᵢ, (2.1);
    - T = [(E₇ − E₅) + (E₃ − E₁)]/(E₆ − E₂), (2.3);
    - its table gives the normal's T = 1.233 (E₅ = 0.3186, E₆ = 0.6745, E₇ = 1.1503).
  - The journal text was not compared.
- Joanes & Gill, "Comparing measures of sample skewness and kurtosis", *JRSS D (The Statistician)* 47(1): 183–189, March 1998, DOI [10.1111/1467-9884.00122](https://doi.org/10.1111/1467-9884.00122). Bibliographic data only. A BibTeX index gives 10.2307/2988433, which doi.org and Crossref answer with 404: do not use it.

#### LM21 (added)

- Jarque & Bera, "Efficient tests for normality, homoscedasticity and serial independence of regression residuals", *Economics Letters* 6(3): 255–259, 1980, DOI [10.1016/0165-1765(80)90024-5](https://doi.org/10.1016/0165-1765(80)90024-5). This is the reference on SciPy's `jarque_bera` page, which prints it as "6 Econometric Letters 255-259". Bibliographic data only: the paper's own formula was not read. The formula SciPy computes is recorded under "Python" below.
- Jarque & Bera, "A Test for Normality of Observations and Regression Residuals", *International Statistical Review* 55(2): 163–172, August 1987, DOI [10.2307/1403192](https://doi.org/10.2307/1403192). Crossref gives only the first page; the end page 172 comes from Semantic Scholar (secondary). Bibliographic data only.

#### LM23 (added)

- Jensen, "The Performance of Mutual Funds in the Period 1945–1964" (Crossref prints the title in capitals), *JF* 23(2): 389–416, May 1968, DOI [10.1111/j.1540-6261.1968.tb00815.x](https://doi.org/10.1111/j.1540-6261.1968.tb00815.x). Bibliographic data only.
- Fama & MacBeth, "Risk, Return, and Equilibrium: Empirical Tests", *JPE* 81(3): 607–636, May 1973, DOI [10.1086/260061](https://doi.org/10.1086/260061). Bibliographic data only.
- Newey & West (1994), already listed. Read in [NBER Technical Working Paper 144](https://www.nber.org/papers/t0144), "Automatic Lag Selection in Covariance Matrix Estimation", September 1993. The cover lists Kenneth D. West first, then Whitney K. Newey. The PDF is a scan; its pages were extracted locally.
  - p. 7, (2-2), "For clarity, assume that the Bartlett kernel is used". The **lag selection parameter** n = [4(T/100)^{2/9}] truncates the sums ŝ⁽¹⁾ = 2Σⱼ₌₁ⁿ jσ̂ⱼ and ŝ⁽⁰⁾ = σ̂₀ + 2Σⱼ₌₁ⁿ σ̂ⱼ.
  - Then γ̂ = 1.1447{(ŝ⁽¹⁾/ŝ⁽⁰⁾)²}^{1/3}, and the HAC truncation lag is "m = [γ̂T^{1/3}]" ("We recommend initially setting"). The recommended procedure first prewhitens with a VAR(1) (p. 6).
  - So **⌊4(T/100)^{2/9}⌋ is Newey and West's pilot lag, not the HAC lag they recommend.** As a HAC lag it is statsmodels' default (see "Python" below), which closes the open point on the lag rule's source.
  - The definition of the brackets was not seen. The journal version (*RES* 61(4): 631–653) was not read.
  - The 1.1447 here is Newey and West's Bartlett constant, which arch also uses. It does not settle the open point on Andrews' (1991) constants.

#### LM25 (added)

- Granger & Newbold, "Spurious regressions in econometrics", *J. Econometrics* 2(2): 111–120, July 1974, DOI [10.1016/0304-4076(74)90034-7](https://doi.org/10.1016/0304-4076(74)90034-7). Bibliographic data only.
- Dimson (1979) is not added, because no brief uses it.

### Entries already in this list: Volume IV locations

- Wasserman (2004), from the contents in Springer's front-matter PDF (2026-10-19): §6.3.1 Point Estimation, p. 90;
  §6.3.2 Confidence Sets, p. 92; §6.3.3 Hypothesis Testing, p. 94; ch. 7, the EDF, p. 97; §8.3 Bootstrap Confidence
  Intervals, p. 110; §8.5.2 "Justification For The Percentile Interval", p. 116; §9.3 Maximum Likelihood, p. 122; §9.4
  Properties of MLEs, p. 124; §9.5 Consistency of MLEs, p. 126; §9.7 Asymptotic Normality, p. 128; §9.8 Optimality,
  p. 130; §9.9 Delta Method, p. 131; §9.11 Parametric Bootstrap, p. 134; ch. 10, Hypothesis Testing and p-values,
  p. 149, with §10.1 Wald, p. 152, §10.2 p-values, p. 156, §10.6 the likelihood ratio test, p. 164, §10.7 Multiple
  Testing, p. 165, and §10.10.1 Neyman–Pearson, p. 170; ch. 11 Bayesian Inference (§11.2, p. 176); §12.7 "Stein's
  Paradox", p. 204; ch. 13 Linear and Logistic Regression (§13.2, §13.5; chapter 13's page numbers are garbled in the
  PDF text). Unconfirmed: theorem numbers, and whether §10.7 covers Bonferroni and BH.
- Efron & Tibshirani (1993): Routledge's ordered contents list gives ch. 8 "More Complicated Data Structures", ch. 12
  "Confidence Intervals Based on Bootstrap 'Tables'", ch. 14 "Better Bootstrap Confidence Intervals" and ch. 16
  "Hypothesis Testing with the Bootstrap" (ch. 13 as above); the numbers are inferred from the order. The BCa section
  number and the moving-blocks section are **unconfirmed** (Google Books answered with a CAPTCHA).
- Casella & Berger, *Statistical Inference*, 2nd ed. (new). Publication data (secondary): Duxbury/Thomson Learning,
  Pacific Grove, CA, 2002, xxviii + 660 pp., ISBN 0-534-24312-6, LCCN 2001025794, from Open Library's copy of the LC
  MARC record. Reprint: Chapman & Hall/CRC (Texts in Statistical Science), ©2024, 565 pp., DOI
  [10.1201/9781003456285](https://doi.org/10.1201/9781003456285); Routledge's page says: "a reprint of the second
  edition originally published by Cengage Learning, Inc. in 2001". Chapters 7 Point Estimation, 8 Hypothesis Testing,
  9 Interval Estimation, 10 Asymptotic Evaluations. **Theorem 7.3.9 (Cramér–Rao), Corollary 7.3.10 (iid case), Lemma
  7.3.11, Corollary 7.3.15 (attainment): unconfirmed** — they appear only in a UMich BIOS 602 handout (Kang, 2013)
  that does not name the book; Google Books answered with a CAPTCHA and archive.org search was refused. The reprint's
  page count differs from the original's: cite theorem numbers, not pages. Which year to cite (2001 or 2002) is open.
- Hill (1975): the estimator's formula is still not checked (Project Euclid answered with a bot challenge again).
- Already listed, named by the survey for Volume IV, no new checks: Cont (2001), Mandelbrot (1963) and
  Gopikrishnan et al. (1999) (LM19, LM26); Kelly (1956), Breiman (1961), Thorp (2006), Markowitz (1952), Merton (1972),
  Chopra & Ziemba (1993) (LM24); Hull (2022) (LM25); Strang (2016) §4.2 (LM23); Forbes & Rigobon (2002) (LM26); the
  Volume III entries for Durrett, Glasserman, Grinstead & Snell and Blitzstein & Hwang (LM19, LM20, LM22).

#### Stage 3, round 1 (2026-10-19)

- Brockwell & Davis (Peter J. Brockwell, Richard A. Davis, in Crossref), *Time Series: Theory and Methods*, 2nd ed.,
  Springer Series in Statistics, Springer-Verlag, New
  York, 1991, DOI [10.1007/978-1-4419-0320-4](https://doi.org/10.1007/978-1-4419-0320-4) (Crossref gives the 2009
  reprint's ISBNs 978-1-4419-0319-8 and 978-1-4419-0320-4; the 1991 copyright page gives 0-387-97429-6). Read
  2026-10-19 in Google Books' preview (id ZW_ThhYQiXIC): p. 222 as a page image; pp. 220–223 and 308 in snippets.
  §7.2: $\hat\rho(h)=\hat\gamma(h)/\hat\gamma(0)$ with mean-corrected $\hat\gamma$ and divisor $n$, (7.2.1)–(7.2.2).
  Theorem 7.2.1 (p. 221) assumes a linear process driven by IID(0, σ²) noise with a finite fourth moment; Theorem
  7.2.2 (p. 222) relaxes the fourth moment. Example 7.2.1, "Independent White Noise" (pp. 222–223): for IID(0, σ²)
  noise $\hat\rho(1),\dots,\hat\rho(h)$ are approximately iid normal with mean 0 and variance $1/n$. The source of
  LM19's (19.6): iid with a finite variance (for $r_t^2$ that means a finite fourth moment of $r_t$).
- Brockwell & Davis, *Introduction to Time Series and Forecasting*, 3rd ed., Springer Texts in Statistics, Springer
  International Publishing, 2016, DOI [10.1007/978-3-319-29854-2](https://doi.org/10.1007/978-3-319-29854-2), ISBN
  978-3-319-29852-8. §2.4, Example 2.4.2 "iid Noise", p. 53 (page image): the same result; §1.6(a), p. 30 (snippet):
  iid with finite variance, bounds $\pm1.96/\sqrt n$.
- Tsay (2010), §2.2, p. 31 (snippets): for an iid sequence with $E(r_t^2)<\infty$, $\hat\rho_\ell$ is asymptotically
  normal with mean 0 and variance $1/T$ for each fixed lag, citing Brockwell and Davis (1991), Theorem 7.2.2.
- Shumway & Stoffer, *Time Series Analysis and Its Applications*, 4th ed., Springer, 2017, DOI
  [10.1007/978-3-319-52452-8](https://doi.org/10.1007/978-3-319-52452-8): Property 1.2, p. 28, under iid with a finite
  fourth moment (a stronger sufficient condition). Hyndman & Athanasopoulos, *Forecasting: principles and practice*,
  3rd ed., OTexts, 2021, §2.9: the ±1.96/√T rule for white noise, without a moment condition.

Batch B (LM23–LM26), read 2026-10-19:

- Newey & West (1987), working-paper version: NBER Technical Working Paper 55, April 1986 ("Revised, February 1986"),
  <https://www.nber.org/papers/t0055>, a 14-page scan read page by page. Eq. (5), p. 3:
  $\hat S_T=\hat\Omega_0+\sum_{j=1}^m w(j,m)[\hat\Omega_j+\hat\Omega_j']$ with $w(j,m)=1-j/(m+1)$, "the modified
  Bartlett weights"; Theorem 1, p. 4: $\hat S_T$ is positive semi-definite; Theorem 2, pp. 5–6: consistency under mixing
  and moment bounds when $m(T)\to\infty$ and $m(T)/T^{1/4}\to0$ (for an MA(∞) with iid innovations, slower than
  $T^{1/2}$ suffices). The journal text was not reached (JSTOR's bot check), so the journal's equation numbers are not
  cited. Hamilton (1994) states the same rate on p. 282 and attributes [10.5.15] to Newey and West (1987).
- Hamilton (1994), Google Books snippets of the 2020 reissue (ISBN 978-0-691-21863-2; its pages match the 1994
  contents): §10.5, "Newey-West Estimator", [10.5.15], pp. 281–283; p. 220 (ch. 8). §17.4, Case 3, pp. 495–497: with a
  constant and no trend in the regression and a random walk with drift as the true process, "both estimated
  coefficients are asymptotically Gaussian" and the usual t and F statistics apply. Case 4, p. 497: with a constant and
  a trend, the true drift "turns out not to matter" (the Dickey–Fuller law).
- West, "Asymptotic Normality, When Regressors Have a Unit Root", *Econometrica* 56(6): 1397–1417, 1988, DOI
  [10.2307/1913104](https://doi.org/10.2307/1913104) (end page from RePEc and Hamilton's reference list; the issue's
  next article starts at p. 1419). RePEc abstract: OLS estimators are asymptotically normal when the nonstationary
  regressors share a unit root and their first differences have a nonzero mean. An alternative source for Case 3.
- Gelman et al. (2013), BDA3, re-read in the authors' PDF (printed page = PDF page − 10; every page reads "This
  electronic edition is for non-commercial purposes only"): (2.10), p. 40, $1/\tau_1^2=1/\tau_0^2+1/\sigma^2$, and the
  sentence after it on precisions; (2.12), p. 42, with $n$ observations and "the data precision, $n/\sigma^2$". §3.3,
  p. 67: the conjugate prior $\mu\mid\sigma^2\sim\mathrm N(\mu_0,\sigma^2/\kappa_0)$, $\sigma^2\sim\text{Inv-}\chi^2(\nu_0,\sigma_0^2)$;
  (3.7)–(3.9), p. 68; p. 69, "Analytic form of the marginal posterior distribution of μ": $t_{\nu_n}(\mu\mid\mu_n,
  \sigma_n^2/\kappa_n)$. §3.3's $t$ holds under this prior, whose variance for $\mu$ scales with $\sigma^2$; §3.2, p. 66, gives
  $t_{n-1}(\bar y,s^2/n)$ under the noninformative prior; BDA3 states no $t$ for a prior SD fixed apart from $\sigma$. The authors'
  contents file titles §2.5 "Estimating a normal mean with known variance"; print pagination unconfirmed.
- Wasserman (2004), Springer's front matter and the chapter page: ch. 11 "Bayesian Inference", pp. 175–192, DOI
  [10.1007/978-0-387-21736-9_11](https://doi.org/10.1007/978-0-387-21736-9_11); §11.2 "The Bayesian Method", p. 176.
  The page-one preview (pp. 175–176) shows §11.2's three steps (prior, model, posterior); the rest was not reached.
- Efron & Hastie (Bradley Efron, Trevor Hastie, in Crossref), *Computer Age Statistical Inference: Algorithms,
  Evidence, and Data Science*, Cambridge University
  Press, 2016, DOI [10.1017/CBO9781316576533](https://doi.org/10.1017/CBO9781316576533) (Crossref). Read in the authors'
  free PDF (<https://hastie.su.domains/CASI/>, "for personal use only", corrected 5 March 2021): §7.1, (7.12)–(7.13),
  pp. 92–93, the James–Stein estimator toward the grand mean, $\hat M+\hat B(x_i-\hat M)$ with $\hat B=1-(N-3)/S$,
  unbiased "as long as $N>3$"; (7.14), p. 93, its risk $NB+3(1-B)$ under (7.7), which with unit noise variance
  and $B=\sigma_0^2/(1+\sigma_0^2)$ equals LM24's $N-(N-3)/(1+\sigma_0^2)$ (proof in endnote 2, pp. 105–106); the James–Stein Theorem, (7.15)–(7.16), p. 93: for $N\ge4$ the expected total squared error is below
  $N$ for every $\mu$; §7.5, pp. 104–105, the positive part $\max(\hat B,0)$; endnote 1, (7.49)–(7.50), p. 105:
  $E[1/\chi^2_\nu]=1/(\nu-2)$. The source of LM24's (24.4).
- Efron & Morris (1975), re-read: (1.4), p. 311, shrinking toward "any initial guess"; (1.12), p. 312, the positive
  part for a fixed target; (2.3), p. 312, the grand-mean rule with $k-3$, credited to Lindley; (2.4), p. 312, its risk
  bound. Their reference [13] gives James and Stein (1961) as pp. 361–79 (a secondary source for the end page).
  Efron & Morris (1973): OpenAlex's abstract covers $k\ge3$, a fixed target and the positive part only.
- *RiskMetrics — Technical Document* (1996), re-read: §5.3.2 "Choosing the decay factor" starts on p. 97 (the chapter
  contents, p. 75, say 96); p. 97: "over 480 time series", and "across 450 time series" later on that page. §5.3.2.2,
  "How RiskMetrics chooses its optimal decay factor", pp. 99–100: each of 480 series has the λ minimizing the RMSE of
  Eq. [5.30] (§5.3.2.1, p. 98); λ = 0.94 is "a weighted average of individual optimal decay factors where the weights
  are a measure of individual forecast accuracy". §5.3.1.2 "Volatility and correlation", p. 93: effective days
  $K=\ln\Gamma_L/\ln\lambda$ at a tolerance level $\Gamma_L$, Eqs. [5.25]–[5.26]. Table 5.7, p. 94: 74 days at λ = 0.94
  and 1% (151 at 0.97); Table 3.1, p. 39, the same. Table 5.9, p. 100, "Summary of RiskMetrics volatility and
  correlation forecasts": 0.94, 550 days in production, 75 effective, with no tolerance level named; footnote: the
  sample mean of daily returns is set to zero.
- End pages confirmed from RePEc and Crossref's issue listings (the next article's first page): White (1980)
  817–838; Engle & Granger (1987) 251–276; Johansen (1991) 1551–1580; Brenner & Kroner (1995) 23–42; Andersen &
  Bollerslev (1998) 885–905; Andrews (1991) 817–858. Newey & West (1987) 703–708 from RePEc, NBER and the Society's
  page (Crossref does not bound it: the next issue starts at p. 749); Engle (1982) 987–1007 (its row).

Revision 2 (LM25), read 2026-10-19:

- KPSS, working-paper version: Kwiatkowski, Phillips & Schmidt, "Testing the Null Hypothesis of Stationarity Against
  the Alternative of a Unit Root: How Sure Are We That Economic Time Series Have a Unit Root?", Cowles Foundation
  Discussion Paper No. 979, May 1991, <https://cowles.yale.edu/sites/default/files/2022-08/d0979.pdf> (a scan; pp. 1,
  3, 7–12 and Table 1 read as page images). §3.a, p. 11, (10)–(12): the level statistic's limit is
  $\int_0^1V(r)^2\,dr$, with $V(r)=W(r)-rW(1)$ a standard Brownian bridge; p. 12: Table 1 by direct simulation (sample
  size 2,000, 50,000 replications); Table 1: .347, .463, .574, .739. The journal text was not reached, so no journal
  equation number is cited.
- Csörgő & Faraway, "The Exact and Asymptotic Distributions of Cramér–von Mises Statistics", *JRSS B* 58(1): 221–234,
  1996, DOI [10.1111/j.2517-6161.1996.tb02077.x](https://doi.org/10.1111/j.2517-6161.1996.tb02077.x) (Crossref). Read in
  the Deep Blue copy (<https://hdl.handle.net/2027.42/146839>), p. 222: the limit distribution function's second
  formula in (1.3) is Anderson and Darling's (1952), who identified it as the law of $\omega^2=\int_0^1B^2(s)\,ds$ for a
  Brownian bridge. SciPy 1.18.1's private `_cdf_cvm_inf` (`stats/_hypotests.py`, l. 479–515) implements that formula
  and cites the paper. Its points 0.347, 0.461, 0.581 and 0.743 match KPSS's table to 0.007; the 0.05/24 point is
  1.0309 (a simulation of 20,000 bridges gives 0.00215 above it). Anderson & Darling (1952), *Ann. Math. Statist.*
  23(2): 193–212, DOI [10.1214/aoms/1177729437](https://doi.org/10.1214/aoms/1177729437): bibliographic data only.

### Open points (Volume IV)

Each of these must be settled before what depends on it is printed. Until then the briefs print the result *stated
without proof*, name the work without the missing detail, or label a mechanism a hypothesis.

- **Bibliographic details:**
  - end pages: James and Stein (1961; two secondary sources give 379); Moors (1988); Jarque and Bera (1987), from a
    primary source;
  - the *Risk* volume of "Great Realisations" (a secondary source gives 13);
  - Casella and Berger's year;
  - the JFE pagination of Merton's Appendix A;
  - the author order of Drees et al.;
  - the DOI of Hansen's (2024) reply;
  - Lahiri's hardcover ISBN;
  - the title and DOI of Martens, Kofman and Vorst (1998);
- **Texts, sections and numbers still to read:**
  - Casella and Berger's theorem numbers, the section contents of Casella and Berger, and Wasserman's §11.2 after
    p. 176;
  - Lo and MacKinlay's (1988) equation numbers;
  - Hill's (1975) formula as printed, and where Embrechts et al. treat the Hill estimator;
  - Harvey, Liu and Zhu's section numbers;
  - Efron and Tibshirani's BCa and moving-blocks sections;
  - the originals of Bonferroni (1936), Rao (1945), Memmel (2003) and Politis and Romano (1992, the circular block
    bootstrap, a book chapter);
  - Jorion's (1986) shrinkage target;
  - Andrews' (1991) plug-in constants;
  - the journal text of Newey and West (1987) (its weights and theorems are read in the 1986 working paper), and the
    journal version of Newey and West (1994);
  - every theorem or equation number in Greene and Hayashi, and Hamilton's beyond §10.5 and §17.4;
  - the Kim & White and Joanes & Gill texts.
- **Sources for results the briefs state without proof:**
  - the $\chi^2_1$ law of (21.5) for two series (LM21);
  - the consistency of the iid bootstrap (LM22, (22.2));
  - the regression's $t_{T-d}$ law (LM23): Blitzstein and Hwang do not state it (above), and Hayashi and Greene are
    unchecked;
  - the ARMA likelihood sandwich and the MLE's large-sample law (LM25).
- **LM26's sources:**
  - the origin of the volatility signature plot (Hansen and Lunde's 2004 working paper credits Andersen, Bollerslev,
    Diebold and Labys 2000, a secondary source);
  - the causes of the signature (stale prices, the bounce of heavy stocks, TWSE's matching rules), which stay
    hypotheses until a source states them for the TAIEX;
  - Roll (1984) and Lo and MacKinlay (1990), which the LM26 brief names for bid–ask bounce and nonsynchronous trading;
    neither is in this file, and their details are unverified;
  - TWSE's history of its matching method (periodic call auctions, continuous trading) and of its tick-size table;
  - Glosten, Jagannathan and Runkle, for the asymmetry term (arch's `o=1`). The text names the asymmetry with Hansen
    and Lunde's (2005) "leverage effect" instead (plans/vol-4.md, the LM26 decisions);
  - Corsi (2009), which must be checked in Crossref before HAR is named.
- **Taiwan:** a TAIFEX page on Saturday sessions.
- **Chinese terms (樂詞網):** 標準化殘差 (standardized residual), 損失函數 (loss function) and 樣本外 (out of sample),
  for LM26; 均值回歸 (mean reversion), marked "editor" in the terms table, for LM25.

Closed in Stage 1 (2026-10-19): the $t$ and $\chi^2$ laws of normal samples (Blitzstein and Hwang Ex. 7.5.9,
Ex. 10.4.3 and Def. 10.4.4; the $t_{n-1}$ law of the studentized mean follows from them in one line, which a module
shows); the source of the lag rule $\lfloor4(T/100)^{2/9}\rfloor$ (statsmodels' default HAC lag, and Newey and
West's (1994) pilot lag, not their recommended HAC lag); the Saturday sessions (TWSE's history page).

Closed in Stage 3, round 1 (2026-10-19): the source of LM19's (19.6) (Brockwell and Davis 1991, Theorem 7.2.2 and
Example 7.2.1); the James–Stein theorem toward the grand mean (Efron and Hastie 2016); BDA3's
(2.10) and §3.3; the Bartlett weights (Newey and West's 1986 working paper); where Hamilton treats Newey–West; the
end pages of Engle (1982), Newey and West (1987), Andrews (1991), Engle and Granger (1987), Johansen (1991) and
Brenner and Kroner (1995); RiskMetrics §5.3.2 and its effective days; the URLs of the RiskMetrics and BDA3 PDFs.

## Papers and books (Volume V)

Checked 2026-10-24 from the Stage 1 briefs of LM27–LM31 and the source check (decision F), whose readings override the
briefs where the two differ, and brought up to a second source hunt of the same day (two fresh agents, anonymous
requests), which read Agrawal et al. (2018), Maillard, Roncalli & Teïletche (2010), López de Prado (2016) and Harvey et
al. (2018) in the versions named; the Crossref record of every DOI below was then read again by the editor's agent
(anonymous requests, no contact data sent). Bibliographic data come from Crossref unless another source is named.
Volume, issue, pages and year agree with the briefs everywhere Crossref holds them; the differences in these fields,
titles and author order are named in their entries, and where the records themselves give different dates (for example
Litterman, Ledoit & Wolf (2004, *J. Multivariate Analysis*), DeMiguel et al., Roncalli's book and Raffinot) the entry
gives each. For the JSTOR DOIs of Merton (1972) and Tobin (1958) Crossref holds only the first page: the end page's
source is named. Titles are in title case, except that Cederburg et al., DeMiguel et al. and López de Prado (2016) keep
Crossref's form and Griveau-Billion et al. arXiv's. Section, equation and page numbers are those of the version named in
the entry. "Abstract" marks a claim read only in an abstract (Crossref's or OpenAlex's copy, as named, not compared with
the publisher's page); "Text not read" means that only the citation or the abstract was seen; "Bibliographic data only"
means nothing in the text was read; "unverified" marks a field or claim that no record checked.

### LM27

- Maillard, Roncalli & Teïletche, "The Properties of Equally Weighted Risk Contribution Portfolios", *JPM* 36(4):
  60–70, 2010 (Crossref: print and online 31 July 2010), DOI
  [10.3905/jpm.2010.36.4.060](https://doi.org/10.3905/jpm.2010.36.4.060). Abstract (OpenAlex's copy, re-read): the
  portfolio that makes every component's risk contribution equal resembles a minimum-variance portfolio with a
  diversification constraint on the weights, and its volatility lies between those of the minimum-variance and the
  equally weighted portfolios. The journal text was not read: no open copy exists (second hunt: OpenAlex marks the
  article closed with no repository copy, SSRN 1271972 answered "Content Blocked", and Roncalli's site hosts only the
  working paper and slides). Read in the working paper "On the properties of equally-weighted risk contributions
  portfolios" (first version June 2008, this version May 2009; thierry-roncalli.com/download/erc.pdf, 23 pages, server
  Last-Modified 2009-06-03; the title differs from the journal's), by the LM27 drafter (local text extraction) and by
  the second hunt: §2.1, p. 4, defines the marginal risk contribution as `∂σ(x)/∂x_i` and the total contribution as
  `σ_i(x) = x_i ∂σ(x)/∂x_i`, with `σ(x) = Σ σ_i(x)`; footnote 1 on p. 4 (the second note so numbered) obtains the sum
  from Euler's theorem for a function homogeneous of degree 1. Used for (27.6) and the Deep Dive; page and equation
  numbers are the working paper's, so LM27 cites the journal article at article level. LM31's uses are under "Entries
  already in this list: Volume V locations".
- Qian, "On the Financial Interpretation of Risk Contribution: Risk Budgets Do Add Up", *Journal of Investment
  Management* 4(4): 41–51, Fourth Quarter 2006; no DOI. joim.com's 2006 listing places the article in Vol. 4, No. 4,
  Fourth Quarter 2006 (re-read; the listing prints no pages and the text needs a login). The pages 41–51 are printed
  on the first page of PanAgora's copy (read by the LM27 drafter, by local text extraction) and, a secondary source,
  in the reference list of Haugh, Iyengar & Song, *J. Computational Finance* 21(2): 29–60 and DOI 10.21314/JCF.2017.329
  as the copy at columbia.edu prints them (re-read for this list); that DOI is not registered (Crossref and doi.org: not
  found, 2026-10-25). Fact used, from PanAgora's copy: under normality a component's expected share of a portfolio loss
  is its percentage risk contribution plus a term that shrinks as the loss grows (his equation (3) and the paragraph
  after it), for the standard deviation and, with a Cornish–Fisher expansion, for VaR. The working paper is SSRN 684221,
  DOI [10.2139/ssrn.684221](https://doi.org/10.2139/ssrn.684221) (Crossref: posted content, preprint, issued 2005, same
  title); its Crossref abstract says that a risk contribution defined through the standard deviation or VaR is closely
  linked to the expected contribution to losses. Used in §6 and in the Leaves sentence on VaR contributions.
- Choueifaty & Coignard, "Toward Maximum Diversification", *JPM* 35(1): 40–51, Fall 2008, DOI
  [10.3905/jpm.2008.35.1.40](https://doi.org/10.3905/jpm.2008.35.1.40). Read by the source check in the JPM layout
  (hosted by TOBAM). Equation (1), p. 41: `D(P) = P′Σ/√(P′VP)`, where *their* Σ is the vector of volatilities, not a
  covariance matrix. The sentence below it reads "The diversification ratio is the ratio of the weighted average of volatilities divided by the portfolio volatility" (quoted; the book does not reuse it unquoted). Also on
  p. 41: a long-only portfolio has `D > 1` unless it is equivalent to a single asset (then `D = 1`); and if the
  expected excess returns are proportional to the volatilities, the Most-Diversified Portfolio is the tangency
  portfolio. LM27 writes the ratio (27.7) in the book's notation, derived from (8.11) and not copied from their Σ,
  and "the ratio exceeds 1" carries their condition (a long-only portfolio not equivalent to a single asset). The
  brief's earlier fallback (abstract only, no citation) is superseded.
- Burns, Engle & Mezrich, "Correlations and Volatilities of Asynchronous Data", *J. Derivatives* 5(4): 7–18, 1998, DOI
  [10.3905/jod.1998.408000](https://doi.org/10.3905/jod.1998.408000). Abstract (OpenAlex's copy, re-read): when
  markets close at different times the returns look predictable and the correlations are understated; the authors
  synchronize the returns by estimating asset values while markets are closed. Text not read; used for that one
  sentence in §4 only.
- Bibliographic data only (checked, not used): Litterman, "Hot Spots™ and Hedges" (Crossref's title carries the ™),
  *JPM* 23(5): 52–75, DOI [10.3905/jpm.1996.052](https://doi.org/10.3905/jpm.1996.052) — Crossref issues it on
  1996-12-31 online and dates the print issue 1997-08-31 (cite 1997); Scholes & Williams, "Estimating Betas
  from Nonsynchronous Data", *JFE* 5(3): 309–327, December 1977, DOI
  [10.1016/0304-405X(77)90041-1](https://doi.org/10.1016/0304-405X(77)90041-1). Sharpe (1963): entry under LM30.

### LM28

- Tobin, "Liquidity Preference as Behavior Towards Risk", *RES* 25(2): 65–86, February 1958, DOI
  [10.2307/2296205](https://doi.org/10.2307/2296205). Crossref holds the first page only; the end page 86 comes from
  the RePEc handle (re-read) and fits Crossref's issue listing, whose next article starts at p. 87. The RES text is
  on JSTOR only and was not compared. Read by the source check: Cowles Foundation Discussion Paper No. 14, dated 17
  July 1956 (an image-only typescript, cowles.yale.edu/sites/default/files/2022-08/d0014.pdf; RePEc lists it as
  Cowles Foundation Discussion Papers 14, 1956). §3.6 "Multiple alternatives to cash" (typescript pp. 31–36): with
  cash riskless, the dominant combinations of the non-cash assets lie on one ray from the origin (pp. 34–35); so the
  proportionate mix of the non-cash assets does not depend on their total share, and the investor behaves as if
  there were one composite asset (pp. 35–36); the opportunity locus is a line, (3.25); the result holds only while
  cash is riskless (p. 36). Limits: the riskless asset is cash at zero yield; no borrowing (the total stays at most
  the investor's balance); non-negativity is assumed but not treated as binding (the proof solves the linear system
  (3.22)); the mix depends on the investor's own estimates. The equation numbers are the typescript's. LM28 cites
  "read in Cowles Foundation Discussion Paper No. 14 (1956), §3.6" and prints no RES page or section number.
- Sharpe, "Capital Asset Prices with and without Negative Holdings", Nobel Lecture, 7 December 1990 (the date on
  nobelprize.org's lecture page, re-read); published in *JF* 46(2): 489–509, June 1991, DOI
  [10.1111/j.1540-6261.1991.tb02671.x](https://doi.org/10.1111/j.1540-6261.1991.tb02671.x). Read by the survey in its
  text copy of the nobelprize.org PDF: the section "The Two-fund Separation Theorem" calls two-fund separation
  "following Tobin" and says that with a riskless asset every investor holds it and the market portfolio; "Fund
  Separation" says that non-negativity makes the frontier piecewise linear (citing Markowitz 1959), so two-fund
  separation need not hold (no brief of Volumes V–VI cites this section). The lecture's reference list misdates Tobin as 1969 with 25: 65–86, which is
  the 1958 paper. Not cited by LM28's text after the revision (Tobin is cited directly, above). Markowitz (1959) is
  named only inside the lecture and was not checked: **unverified**.
- Best & Grauer, "On the Sensitivity of Mean-Variance-Efficient Portfolios to Changes in Asset Means: Some Analytical
  and Computational Results", *RFS* 4(2): 315–342, 1991, DOI
  [10.1093/rfs/4.2.315](https://doi.org/10.1093/rfs/4.2.315). Abstract (OpenAlex's copy, re-read): with only a budget
  constraint a mean-variance-efficient portfolio's weights, mean and variance can be extremely sensitive to changes in
  asset means; with non-negativity added the weights stay extremely sensitive but the portfolio's return and standard
  deviation barely move; a surprisingly small rise in the mean of one asset drives half the securities out. Text not
  read; used in §5 (one sentence).
- Boyd & Vandenberghe (2004), §4.4.1 (the Markowitz example, p. 155) and §4.7.6 (pp. 185–186): already in this list;
  its data and pages are under "Entries already in this list: Volume V locations".

### LM29

- Diamond & Boyd, "CVXPY: A Python-Embedded Modeling Language for Convex Optimization", *J. Machine Learning
  Research* 17(83): 1–5, 2016; no DOI. The JMLR page (jmlr.org/papers/v17/15-408.html, re-read): authors Steven
  Diamond, Stephen Boyd; abstract: a domain-specific language for convex optimization embedded in Python that lets
  the user write problems in a natural syntax instead of the standard form solvers require. That its solver list
  (CVXOPT, ECOS, SCS) is outdated is the survey's finding; the text names the solvers from A29-22, not from the
  paper. Text not read.
- Agrawal, Verschueren, Diamond & Boyd, "A Rewriting System for Convex Optimization Problems", *Journal of Control
  and Decision* 5(1): 42–60, 2018 (Crossref: issued 2018-01-02, online 2018-01-19; Crossref's title is in lower
  case), DOI [10.1080/23307706.2017.1397554](https://doi.org/10.1080/23307706.2017.1397554). Read by the survey and,
  in full, by the second hunt in arXiv:1709.04494v2 (v1 13 September 2017, v2 22 January 2019, journal reference
  "J.Control.Decis. 5 (2018) 42-60"; its first page reads "Updated January 23, 2019; originally published September
  15, 2017"); page numbers are arXiv v2's, and the journal's pages were not compared. The paper describes CVXPY 1.0.
  Abstract, p. 1: two phases, analysis, which looks for a suitable solver, and canonicalization, which rewrites the
  problem in the selected solver's standard form; §1.3, pp. 4–5: on `solve`, CVXPY canonicalizes a problem to a solver's
  standard form, and problems written in CVX, Convex.jl and CVXPY are canonicalized to conic form automatically; §4,
  p. 15: an analyzer finds the most specific class the problem belongs to by checking which back ends accept it, and the
  problem is solved through a chain of reductions, a solver call and the retrieval of the solution (a problem reducible
  to a quadratic program goes to a QP solver when one is installed); §3.3, p. 11: these languages canonicalize to a form
  for cone program solvers, in general (the paper does not treat a volatility limit); p. 3: CVXPY detects convexity
  through the disciplined convex programming rules. LM29 §8 cites the paper for cvxpy's canonicalization (abstract, §1.3
  and §4), with no journal page; the solver names, defaults and the cone route in cvxpy 1.9.3 rest on the installed
  environment (A29-22).
- Stellato, Banjac, Goulart, Bemporad & Boyd, "OSQP: An Operator Splitting Solver for Quadratic Programs",
  *Mathematical Programming Computation* 12(4): 637–672, 2020 (Crossref: online 2020-02-20, print December 2020), DOI
  [10.1007/s12532-020-00179-2](https://doi.org/10.1007/s12532-020-00179-2). Cited only for the method's name, which
  the title states. Text not read.
- Goulart & Chen, "Clarabel: An Interior-Point Solver for Conic Programs with Quadratic Objectives", arXiv:2405.12762
  (v1, 21 May 2024; the arXiv API record and abstract, re-read): a general-purpose interior-point solver for conic
  problems, based on a homogeneous embedding, specialized to quadratic objectives, "distributed as a standard solver
  for the Python CVXPY optimization suite". A preprint; no journal version was checked. Cited for the method's name.
- Boyd, Busseti, Diamond, Kahn, Koh, Nystrup & Speth, "Multi-Period Trading via Convex Optimization", *Foundations
  and Trends in Optimization* 3(1): 1–76, August 2017, DOI
  [10.1561/2400000023](https://doi.org/10.1561/2400000023). **Author order:** Crossref lists the seven authors as
  Boyd, Diamond, Koh, Nystrup, Busseti, Kahn, Speth; Boyd's page (web.stanford.edu/~boyd/papers/cvx_portfolio.html)
  and arXiv:1705.00109 (both re-read) give the order printed here, which is the one to cite. Abstract (all three
  agree): in single-period optimization the trades are found by solving a convex problem that trades off expected
  return, risk, transaction cost and holding cost, such as the cost of borrowing to short. Text not read; used for
  that one sentence.
- Lawson & Hanson, *Solving Least Squares Problems*, SIAM, 1995, DOI
  [10.1137/1.9781611971217](https://doi.org/10.1137/1.9781611971217). Crossref: monograph issued 1995-01-01, print
  ISBN 978-0-89871-356-5, online ISBN 978-1-61197-121-7. The series Classics in Applied Mathematics is **unverified**
  (Crossref does not record it; SIAM's page answered 403) and is not printed. Cited through SciPy 1.18.1's
  `scipy.optimize.nnls` docstring (re-read in the project environment), which cites the book as "SIAM, 1995" and says
  the function uses an active-set method that solves the KKT conditions of non-negative least squares. The book was not
  read.
- Bibliographic data only (checked, not relied on): Nocedal & Wright, *Numerical Optimization*, 2nd ed., Springer
  Series in Operations Research and Financial Engineering, Springer New York, 2006, DOI
  [10.1007/978-0-387-40065-5](https://doi.org/10.1007/978-0-387-40065-5) (Crossref: print ISBN 978-0-387-30303-1,
  online ISBN 978-0-387-40065-5; the edition number is LM7's, lm07.md:784) — LM7's source for the necessity of the
  KKT conditions (Theorem 12.1, text not read); Cornuéjols, Peña & Tütüncü, *Optimization Methods in Finance*, 2nd
  ed., Cambridge University Press, 2018 (Crossref: online 2018-07-27, print 2018-08-09), DOI
  [10.1017/9781107297340](https://doi.org/10.1017/9781107297340); Kolm, Tütüncü & Fabozzi, "60 Years of Portfolio
  Optimization: Practical Challenges and Current Trends", *European J. Operational Research* 234(2): 356–371, 2014
  (Crossref: April 2014), DOI [10.1016/j.ejor.2013.10.060](https://doi.org/10.1016/j.ejor.2013.10.060). The last two
  are further reading only, if Stage 2 wants them.
- Pointer: Boyd & Vandenberghe (2004), LM29's text on convex functions, KKT conditions and quadratic programs, is
  already in this list; its data and the pages LM28 and LM29 use are under "Entries already in this list: Volume V
  locations".

### LM30

- Ledoit & Wolf, "A Well-Conditioned Estimator for Large-Dimensional Covariance Matrices", *J. Multivariate
  Analysis* 88(2): 365–411, February 2004, DOI
  [10.1016/S0047-259X(03)00096-4](https://doi.org/10.1016/S0047-259X(03)00096-4) (Crossref's issue date is February
  2004; OpenAlex dates the article 2003, the online year). Read in the authors' working paper of February 2001 (the
  survey's saved copy from ledoit.net; its title page re-read): §2 (the oracle, Lemma 2.1 and Theorem 2.1, mean-zero
  data, finite fourth moments); §3 (Assumptions 1–3: `p/n` bounded, bounded eighth moments, a condition on products;
  Lemmas 3.2–3.5; the estimator (14); Theorem 3.2, consistency; Theorem 3.4, asymptotic optimality; Theorem 3.5, a
  bounded condition number). Lemma and theorem numbers are the working paper's: cite them as such, or at section
  level. The journal text was not compared.
- Ledoit & Wolf, "Improved Estimation of the Covariance Matrix of Stock Returns with an Application to Portfolio
  Selection", *J. Empirical Finance* 10(5): 603–621, December 2003, DOI
  [10.1016/S0927-5398(03)00007-0](https://doi.org/10.1016/S0927-5398(03)00007-0). The single-index target: from the
  survey's reading of the working paper (abstract and §1), not re-read; the abstract of the working paper of
  October 2001 (title page re-read) says the estimator is an optimally weighted average of the sample covariance
  matrix and the single-index covariance matrix. One sentence only.
- Ledoit & Wolf, "Honey, I Shrunk the Sample Covariance Matrix", *JPM* 30(4): 110–119, 2004, DOI
  [10.3905/jpm.2004.110](https://doi.org/10.3905/jpm.2004.110). The constant-correlation target: from the survey's
  reading of the working paper dated November 2003 (§3.2, not re-read). Abstract (OpenAlex's copy, re-read): no one
  should use the sample covariance matrix for portfolio optimization; shrinkage pulls the most extreme coefficients
  toward the centre; the challenge is the optimal shrinkage intensity. One sentence only.
- DeMiguel, Garlappi & Uppal, "Optimal Versus Naive Diversification: How Inefficient is the 1/N Portfolio
  Strategy?", *RFS* 22(5): 1915–1953, May 2009 (online 3 December 2007; cite 2009), DOI
  [10.1093/rfs/hhm075](https://doi.org/10.1093/rfs/hhm075). Crossref's title is in title case with "is" in lower case
  and the N in italics. Read by the source check: the published RFS article (the copy on Garlappi's site). Abstract: 14
  models, seven datasets, none consistently better than 1/N in Sharpe ratio, certainty-equivalent return or turnover;
  with parameters calibrated to the US equity market, around 3,000 months for 25 assets and 6,000 for 50. "3,000 months"
  appears in four places: the abstract ("around 3000"), p. 1919, §4 p. 1941 (Figure 1, panel E: "more than 3000" for 25
  assets, more than 6000 for 50) and the Conclusions, p. 1947. The criterion (§4, pp. 1937–1938) is the expected
  mean-variance utility loss (the certainty equivalent), eqs. (18)–(22), Proposition 1, for the sample-based
  mean-variance rule under i.i.d. normal returns. Panel E is calibrated to US stocks: tangency Sharpe ratio 0.15 and
  1/N's 0.12, both monthly (p. 1939). Table 6 (p. 1943), monthly values: 1/N earns 0.1356, 0.1447 and 0.1466 for N = 10,
  25, 50, against 0.1477 for the true mean-variance policy (p-values 0.00, 0.03, 0.15); the paper says panel E's 0.12
  comes from Table 6, yet Table 6's 1/N values are 0.1356–0.1466 — quote one of the two, labelled. Conditions under
  which optimizing wins (p. 1919): a long estimation window, an ex ante mean-variance Sharpe ratio substantially above
  1/N's, and few assets. **"1/N lies close to the tangency portfolio" is not in the paper:** it is not to be printed.
- Jagannathan & Ma, "Risk Reduction in Large Portfolios: Why Imposing the Wrong Constraints Helps", *JF* 58(4):
  1651–1683, August 2003 (online 15 July 2003), DOI
  [10.1111/1540-6261.00580](https://doi.org/10.1111/1540-6261.00580). Abstract (Crossref's copy, re-read):
  constraining the weights to be non-negative can reduce the risk of estimated optimal portfolios even when the
  constraints are wrong; with no-short-sale constraints the sample covariance matrix performs as well as estimates
  from factor models, shrinkage and daily data. Proposition 1 read in NBER Working Paper 8922 (May 2002; the
  survey's copy, title page re-read): with only the non-negativity constraint the adjusted matrix is
  `S − (λ1ᵀ + 1λᵀ)` in their letters, symmetric and positive semidefinite, and the constrained portfolio is one of
  its minimum-variance portfolios. Cite both: Jagannathan, Ma & Zhang, "A Note on 'Risk Reduction in Large
  Portfolios: Why Imposing the Wrong Constraints Helps'", *JF* 74(5): 2689–2696, October 2019 (online 2 July 2019),
  DOI [10.1111/jofi.12824](https://doi.org/10.1111/jofi.12824). Its Crossref abstract: it corrects an error in the
  proof of Proposition 2, not Proposition 1 (the abstract quotes the title with "Constraint" in the singular). The
  note's text (re-read) places Proposition 1 on p. 1655 of the 2003 article.
- Black & Litterman, "Global Portfolio Optimization", *FAJ* 48(5): 28–43, 1992, DOI
  [10.2469/faj.v48.n5.28](https://doi.org/10.2469/faj.v48.n5.28) (Idzorek's reference list prints "September/October").
  Text not read (image-only scan); cited as the model's origin only, with no claim of its own.
- He & Litterman, "The Intuition Behind Black-Litterman Model Portfolios", Goldman Sachs Investment Management
  Research, December 1999 (the date and series as Idzorek's reference list prints them, re-read), SSRN 334304, DOI
  [10.2139/ssrn.334304](https://doi.org/10.2139/ssrn.334304) (Crossref: posted content, preprint, issued 2002; SSRN's
  page answered 403, so the 1999 date is single-sourced). Abstract (Crossref): the unconstrained optimal portfolio of
  the Black–Litterman model is the scaled market equilibrium portfolio plus a weighted sum of portfolios that
  represent the investor's views. Text not read; §6 derives the statement for one view and cites the note for the
  general case.
- Idzorek, "A Step-by-Step Guide to the Black-Litterman Model", in S. Satchell (ed.), *Forecasting Expected Returns
  in the Financial Markets*, Elsevier (Academic Press), 2007, pp. 17–38, ISBN 978-0-7506-8321-0, DOI
  [10.1016/B978-075068321-0.50003-0](https://doi.org/10.1016/B978-075068321-0.50003-0). Crossref: book chapter,
  2007, pp. 17–38, ISBN 9780750683210, no editor recorded; "edited by Stephen Satchell", Elsevier/AP, 2007, 286 pp.,
  from Open Library's record of the book. Read in the author's draft (subtitle "Incorporating user-specified
  confidence levels"; original draft 1 January 2002, "This Draft: July 20, 2004"; the survey's copy, re-read):
  reverse optimization, Formula (1); the posterior mean, (3); the scarce guidance on the scalar (values near zero,
  0.01–0.05, 1, and about one over the number of observations, each attributed there to other authors). Formula
  numbers are the draft's.
- Michaud, "The Markowitz Optimization Enigma: Is 'Optimized' Optimal?", *FAJ* 45(1): 31–42, 1989, DOI
  [10.2469/faj.v45.n1.31](https://doi.org/10.2469/faj.v45.n1.31). Abstract (the journal's own article page, saved
  by the LM30 drafter and re-read; OpenAlex holds only a conference note): the major problem with mean-variance
  optimization is its tendency to maximize the effects of errors in the inputs; unconstrained optimization can give
  results inferior to simple equal weighting. Text not read (403). LM30 cites it at this level only.
- Michaud & Michaud, "Estimation Error and Portfolio Optimization: A Resampling Solution", *Journal of Investment
  Management* 6(1), First Quarter 2008; no DOI. joim.com's 2008 listing places the article in Vol. 6, No. 1, First
  Quarter 2008 (re-read; no pages shown, the text needs a login): the pages are **unverified**. Read by the source
  check: the New Frontier Advisors pre-publication copy (©2007, "Publication forthcoming in the Journal of
  Investment Management", marked "not to be quoted or reproduced without the authors' permission", so paraphrase
  only); its page numbers are the copy's. Resampled Efficiency was first proposed in Michaud (1998), chs. 6–7 (p. 3).
  The steps (p. 5): draw a mean vector and covariance matrix centred at the point estimates (resampled from an
  assumed distribution, or bootstrapped); compute the efficient frontier for that draw; repeat; average the weights
  of "properly associated" efficient portfolios — for example all minimum-variance portfolios, all maximum-return
  portfolios, or portfolios matched by utility (pp. 5–7); optionally apply constraints. Their illustration uses 120
  simulated monthly returns and long-only weights (footnote 14, p. 5; 51 portfolios per frontier, Figure 1, p. 6).
  The method is trademarked and, by footnote 3, protected by U.S. and Israeli patents, with patents pending
  worldwide. An SSRN posting of the same title (SSRN 2658657, Crossref: posted content, preprint, 2015) was not read.
  LM30's experiment 4 averages maximum-Sharpe portfolios, a variant of this method.
- Michaud (1998) is cited only as Michaud & Michaud (2008) describe it: *Efficient Asset Management*, Harvard
  Business School Press, 1998 — publisher and year as the reference list of the pre-publication copy prints them;
  Open Library's record of the 1998 edition: "a practical guide to stock portfolio optimization and asset
  allocation", Boston, 152 pp., ISBN 0-87584-743-9, LCCN 98005193. The book was not read. The second edition
  (R. Michaud & R. Michaud, Oxford University Press, 2008, ISBN 978-0-19-533191-2; Crossref's chapter records and
  Open Library agree) is not cited.
- Sharpe, "A Simplified Model for Portfolio Analysis", *Management Science* 9(2): 277–293, January 1963, DOI
  [10.1287/mnsc.9.2.277](https://doi.org/10.1287/mnsc.9.2.277). Abstract (Crossref's copy, re-read): a model with few
  parameters for the Markowitz analysis, 2,000 securities analysed at a small fraction of the cost, and very nearly
  the same results as with far larger sets of relationships. The single-index model's origin; text not read. (LM27's
  brief also lists it, as checked and not used.)
- Chen, Wiesel, Eldar & Hero, "Shrinkage Algorithms for MMSE Covariance Estimation", *IEEE Transactions on Signal
  Processing* 58(10): 5016–5029, October 2010, DOI
  [10.1109/TSP.2010.2053029](https://doi.org/10.1109/TSP.2010.2053029). Abstract (OpenAlex's copy, re-read):
  Gaussian samples; an estimator that improves on Ledoit–Wolf by conditioning on a sufficient statistic (RBLW), and an
  iterative approximation of the clairvoyant shrinkage estimator whose limit is the oracle approximating shrinkage
  (OAS) estimator. Named in §8 as OAS's source; text not read.
- Pointer: Best & Grauer (1991) is under LM28; LM30 does not cite it.

### LM31

- Bruder & Roncalli, "Managing Risk Exposures Using the Risk Budgeting Approach", SSRN working paper 2009778, 2012,
  DOI [10.2139/ssrn.2009778](https://doi.org/10.2139/ssrn.2009778) (Crossref: posted content, 2012; the title page
  writes "using" in lower case). Read by the LM31 drafter in the author-hosted copy (thierry-roncalli.com,
  `download/risk-budgeting.pdf`) and by the source check in the version whose title page reads "First version: January
  2012 – This version: March 2012" (the source check's report calls it the SSRN version; its saved file bears the
  author-hosted copy's name, `risk-budgeting.pdf`): Definition (3), p. 5 (weights in [0, 1]ⁿ; budgets strictly positive,
  summing to 1); §2.2, pp. 4–5 (a zero budget can give several solutions: budgets (50%, 50%, 0%) admit more than one, hence `b_i > 0`; the two
  weight vectors first recorded here do not both sum to 1 and wait for a re-read); eq. (7), p. 9 (weights proportional to `b_i/β_i`); §2.3.3, pp. 9–10
  (existence and uniqueness for a positive definite covariance from the log-barrier program (9), footnote 13 on
  `b_i > 0` — a short argument, not a formal theorem); §2.3.4, p. 10 (`σ_mv ≤ σ_rb ≤ σ_wb`, proved in Appendix A.3).
  Page and equation numbers are that version's. LM31's source for unequal budgets (the shared "References" decision
  asked for one beyond Maillard et al.); because §2.3.3 is a sketch, LM31 derives (31.2) in full. Whether a journal
  version exists was not checked.
- Griveau-Billion, Richard & Roncalli, "A Fast Algorithm for Computing High-dimensional Risk Parity Portfolios",
  arXiv:1311.4057 (v1, 16 November 2013; the arXiv API record, re-read; the brief notes that the PDF is dated September
  2013), also SSRN 2325255, DOI [10.2139/ssrn.2325255](https://doi.org/10.2139/ssrn.2325255). Crossref types the SSRN
  record as a journal article in "SSRN Electronic Journal", 2013, writes "High-Dimensional" and misspells the first
  author's given name ("Thhophile"; arXiv: Théophile). Read by the LM31 drafter in the arXiv version: the budget
  definition (citing Roncalli 2013), the CCD update, eq. (4), convergence by Tseng (2001, Theorem 5.1; their Remark 2),
  positive budgets (Remark 3), and the appendix's account of Chaves et al.'s fixed point and Newton method and of
  Spinu's Newton method. A preprint; no journal version was checked. Used for the CCD algorithm and its widget, and as
  the route to Chaves et al. and Tseng.
- Chaves, Hsu, Li & Shakernia, "Efficient Algorithms for Computing Risk Parity Portfolio Weights", *J. Investing*
  21(3): 150–163, 2012 (Crossref: print and online 31 August 2012; Crossref's title runs "RiskParity" together), DOI
  [10.3905/joi.2012.21.3.150](https://doi.org/10.3905/joi.2012.21.3.150). Text not read: the fixed point is described
  as Griveau-Billion et al. describe it.
- Tseng, "Convergence of a Block Coordinate Descent Method for Nondifferentiable Minimization", *J. Optimization
  Theory and Applications* 109(3): 475–494, June 2001, DOI
  [10.1023/A:1017501703105](https://doi.org/10.1023/A:1017501703105). Text not read: cited as Griveau-Billion et al.
  cite it (Theorem 5.1), so the convergence of CCD is *stated without proof*.
- López de Prado, "Building Diversified Portfolios that Outperform Out of Sample", *JPM* 42(4): 59–69, 2016
  (Crossref: print 31 May 2016, online 31 July 2016), DOI
  [10.3905/jpm.2016.42.4.059](https://doi.org/10.3905/jpm.2016.42.4.059). Abstract (OpenAlex's copy, re-read): HRP
  addresses the instability, concentration and underperformance of quadratic optimizers, needs no invertible
  covariance matrix, and in Monte Carlo experiments gives lower out-of-sample variance than the critical line
  algorithm. The JPM body was not read (the publisher's page redirects to a login; OpenAlex lists SSRN as the only
  open location). Read by the LM31 drafter and by the second hunt in SSRN 2708678, "This version: May 23, 2016"
  (Crossref: DOI [10.2139/ssrn.2708678](https://doi.org/10.2139/ssrn.2708678), posted content dated 2019, title
  "… Out-of-Sample"). SSRN blocks automated access (403, "Content Blocked"), so the file read is SSRN's own PDF, with
  SSRN's stamp on every page, obtained from a third-party mirror (smallake.kr; byte-identical to the drafter's copy);
  SSRN's abstract page, as the Internet Archive holds it (capture 2019-04-04), shows "Date Written: May 23, 2016" and
  "Journal of Portfolio Management, 2016, Forthcoming". Also read: the author's `HRP.py` (header dated 2015-12-27),
  which his site quantresearch.org links. Locations, the SSRN version's: no inverse of the covariance needed, the
  abstract (p. 2) and p. 5; the distance `√(½(1 − ρ))`, Stage 1, p. 5, a metric by Appendix A.1, p. 13; the Euclidean
  distance between the columns of the distance matrix, p. 5, so that Example 1's correlations give Example 2's
  0.5659, 0.9747 and 1.1225, which the script and SciPy on the square matrix reproduce [A31-46]; single linkage (the
  "nearest point algorithm"), Example 4, p. 6; quasi-diagonalization, Stage 2, p. 7; recursive bisection of the
  ordered list, Stage 3, p. 8 (the first half takes `int(½|L_i|)` items with the order preserved, each half's
  variance uses inverse-variance weights, and the first half receives `1 − V_1/(V_1 + V_2)`); inverse-variance
  weights optimal for a diagonal covariance, Appendix A.2, pp. 13–14; p. 11: stage 3 could instead split top-down
  along the stage-1 clusters, the source for leaving tree-following splits out; the Monte Carlo design, p. 10 (10
  series of 520 Gaussian observations, a 260-observation window, re-estimated and rebalanced every 22 observations,
  10,000 runs); Appendix A.3's code, `dist=correlDist(corr); link=sch.linkage(dist,'single')`, the same as `HRP.py`
  lines 90–91, which reads the square distance matrix as observations. LM31 prints no JPM page or equation number.
- Moreira & Muir, "Volatility-Managed Portfolios", *JF* 72(4): 1611–1644, August 2017 (online 15 May 2017), DOI
  [10.1111/jofi.12513](https://doi.org/10.1111/jofi.12513). Abstract (Crossref's copy, re-read): managed portfolios
  that take less risk when volatility is high raise Sharpe ratios, because changes in volatility are not offset by
  proportional changes in expected returns. The JF text was not read (Wiley answers every client with a challenge
  page; source check). Read: NBER Working Paper 22208, by the LM31 drafter (April 2016) and by the source check (the
  revision of June 2016), DOI [10.3386/w22208](https://doi.org/10.3386/w22208) (Crossref: report, April 2016, title
  "Volatility Managed Portfolios", without the hyphen); and, by the source check, the authors' draft of 25 October
  2016, which thanks the editor and two referees. The two agree on every design fact: eq. (1) scales the factor's
  next-month return by `c` over the previous month's realized variance, which eq. (2) computes from the month's daily
  returns (22 days); `c` makes the managed portfolio's unconditional standard deviation equal buy-and-hold's, is
  computed on the full sample and does not change the Sharpe ratio (footnote 5); samples (Table I's note) 1926–2015 for
  the market, SMB, HML and momentum, 1963–2015 for RMW and CMA, 1967–2015 for ROE and IA, 1983–2015 for the FX carry
  factor; leverage caps of 1 and 1.5 appear only as robustness checks. Equation, footnote and table numbers are those
  versions'. LM31 cites the JF article, names the two versions read and prints no JF page or equation number.
- Harvey, Hoyle, Korgaonkar, Rattray, Sargaison & Van Hemert, "The Impact of Volatility Targeting", *JPM* 45(1):
  14–33, 2018 (Crossref: print 31 October 2018, online 1 November 2018; Crossref lists the last author as "Hemert,
  Otto Van"), DOI [10.3905/jpm.2018.45.1.014](https://doi.org/10.3905/jpm.2018.45.1.014). Read by the second hunt in
  the journal reprint, complete (cover and pp. 14–33; its footer says it was downloaded from the JPM site by Campbell
  Harvey on 1 November 2018), at people.duke.edu/~charvey (Last-Modified 2018-11-01); the exhibits were read from
  rendered pages because their text layer is garbled (probably the copy the LM31 drafter found damaged). Journal
  pages: "more than 60 assets, with daily data beginning as early as 1926", p. 14 ("our 60+ assets", pp. 14 and 31),
  which LM31 may print; the volatility, a zero-mean exponentially weighted standard deviation of daily returns
  (footnote 8, p. 16), with a 20-day half-life by default throughout; half-lives of 10, 20, 40, 60 and 90 days
  compared for US equities in Exhibit 5, p. 20, 90 days the slowest (footnote 8; Exhibit 20, p. 31); returns scaled
  by `σ_target/σ̂`, with `σ̂` from returns up to `t − 2`, a 10% target and a constant near 1 chosen so that the
  target is realized ex post over the full sample, p. 16; US equities daily from 1 July 1926 (p. 15), with statistics
  for 1927–2017 (Exhibits 1 and 5); US bond yields from 1962 (p. 15; Exhibit 1), bond statistics 1963–2017 (Exhibits
  9 and 11); 50 futures and forwards (19 commodities, 9 currencies, 10 equity indexes, 9 bonds and 3 rate contracts,
  p. 16) and credit, for 1988–2017 in the results exhibits (Exhibits 15 and 18–20; Exhibit 1 says 1988–2018); the
  Sharpe ratio "improves slightly for equity indexes and credit" and is similar for other assets (p. 25), the effect
  negligible for fixed income, currencies and commodities (p. 31; the opening section, p. 14, names bonds, currencies
  and commodities); the vol of vol and the mean shortfall (the left tail) improve materially for almost all of the
  futures, forwards and credit (p. 25), but for US 10-year Treasury futures the vol of vol is much lower while the
  Sharpe ratio and the left tail are similar (p. 25; Exhibit 13, p. 26); for a 60–40 portfolio scaled at the asset and
  portfolio levels, 1988–2017, both the cumulative return and the vol of vol improve, and so do the Sharpe ratio and
  the expected shortfall (pp. 27–28, Exhibits 16–17); footnote 7, p. 16: Moreira and Muir scaled by variance for most
  of their analysis, and volatility scaling did as well in a robustness check (for LM31's knowledge check §6(b)).
  LM31's wording follows these locations; the paper's Sharpe ratios stay out, and nothing is said of its results holding
  for E5's funds.
- Checked, not used:
  - Roncalli, *Introduction to Risk Parity and Budgeting*, Chapman & Hall/CRC, DOI
    [10.1201/b15151](https://doi.org/10.1201/b15151). Crossref: book, e-book ISBN 978-0-429-17130-7, issued 19 April
    2016 (the e-book record); Routledge's page (read 2026-10-24): 1st edition, Chapman & Hall, "Copyright 2014",
    440 pp., hardback ISBN 978-1-4822-0715-6; the Library of Congress MARC record (LCCN 2013026141; the copy Open
    Library names as its source, read 2026-10-25): Boca Raton, Taylor & Francis, "[2014]", xxiii + 410 pp.,
    Chapman & Hall/CRC financial mathematics series; Open Library's own date is 2013, a value it held before the LC
    record was added. The records differ (Open Library 2013, LC [2014], the publisher ©2014, Crossref's e-book 2016;
    cite 2014, the publisher's ©). Not read; Griveau-Billion et al. cite it as Roncalli (2013) for the budget
    definition.
  - Spinu, "An Algorithm for Computing Risk Parity Weights", SSRN 2297383, DOI
    [10.2139/ssrn.2297383](https://doi.org/10.2139/ssrn.2297383) (Crossref: posted content, 2013). Crossref's abstract:
    a Newton's-method algorithm for risk parity and risk budget weights, provably convergent. Text not read.
  - Raffinot, "Hierarchical Clustering-Based Asset Allocation", *JPM* 44(2): 89–99, DOI
    [10.3905/jpm.2018.44.2.089](https://doi.org/10.3905/jpm.2018.44.2.089). Crossref: online 22 December 2017, print
    31 December 2017; OpenAlex dates the work 2016; the DOI string carries 2018, which no record checked gives (cite
    2017, Crossref's online and print year). Not read.
  - Cederburg, O'Doherty, Wang & Yan, "On the performance of volatility-managed portfolios", *JFE* 138(1): 95–117,
    October 2020, DOI [10.1016/j.jfineco.2020.04.015](https://doi.org/10.1016/j.jfineco.2020.04.015). Bibliographic
    data only; its findings are **unverified** and stay out of the text (decision F).
- Pointers: LM31's uses of Maillard, Roncalli & Teïletche (2010, under LM27), of Boyd & Vandenberghe (2004) and of the
  RiskMetrics document are under "Entries already in this list: Volume V locations".

### Entries already in this list: Volume V locations

- Markowitz (1952), "Papers and books (where bibliographic details were verified)": LM28 cites it for the origin of
  mean–variance only. Crossref, re-read: *JF* 7(1): 77–91, March 1952, DOI
  [10.1111/j.1540-6261.1952.tb01525.x](https://doi.org/10.1111/j.1540-6261.1952.tb01525.x).
- Merton (1972), same list: LM28 uses it for the closed-form frontier and two-fund separation (his notation is not
  used). Crossref, re-read: *JFQA* 7(4), first page 1851 only, DOI
  [10.2307/2329621](https://doi.org/10.2307/2329621); 1851–1872 on RePEc (abstract, re-read: explicit frontiers for
  more than three assets, the separation theorem stated and proved as a mutual-fund theorem, the graphical method
  incorrect under some conditions), which fits Crossref's issue listing (the next article starts at p. 1873). The
  Cambridge-style DOI 10.1017/S0022109000017798 is not registered (Crossref and doi.org both returned 404): cite
  10.2307/2329621.
- Chopra & Ziemba (1993), same list: LM28 and LM30 cite it as lm07.md:509 does, with no ratio printed. Crossref,
  re-read: *JPM* 19(2): 6–11, 1993, DOI 10.3905/jpm.1993.409440 (Crossref's record for that DOI, read 2026-10-31: the
  title, both authors, volume, issue and pages match).
- Boyd & Vandenberghe (2004), same list ("Stanford PDF"): LM28, LM29 and LM31. *Convex Optimization*, Cambridge
  University Press, 2004, DOI [10.1017/CBO9780511804441](https://doi.org/10.1017/CBO9780511804441). Crossref:
  monograph issued 2004-03-08, print ISBN 978-0-521-83378-3, online ISBN 978-0-511-80444-1. Read by the LM29 drafter
  in the authors' PDF (web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf; the copyright page reads "First published
  2004", "Seventh printing with corrections 2009", ISBN 0 521 83378 7). Pages as the drafters recorded them,
  re-checked for this list in a fresh download of the same PDF and in the survey's text copy (every page below
  agrees): first-order conditions §3.1.3, p. 69; second-order conditions §3.1.4, p. 71; pointwise maximum §3.2.3,
  p. 80; local and global optima §4.2.2, p. 138; linear-fractional programs and their change of variables §4.3.2,
  p. 151; the QP form (4.34) §4.4, p. 152; §4.4.1 "Examples", subsection "Markowitz portfolio optimization", p. 155,
  and its linear transaction costs with buy and sell variables, p. 156; the refined Slater condition (5.27), §5.2.3,
  p. 226, which reduces to feasibility for linear constraints (p. 227); KKT conditions sufficient for convex problems, and
  necessary and sufficient under Slater's condition, §5.5.3, p. 244; the global inequality (5.57), §5.6.2, p. 250;
  local sensitivity §5.6.3, p. 251; and, for LM28, §4.7.6 "Examples", subsection "Risk-return trade-off in portfolio
  optimization", pp. 185–186 (§4.7.6 itself is titled "Examples"). LM28 uses §4.4.1 and §4.7.6; LM31 cites the book
  through LM29, with no section of its own.
- Sharpe (1964) and Lintner (1965), the "LM23" section; Campbell, Lo & MacKinlay (1997), ch. 5, the "LM19 and LM20"
  entry: LM28 cites LM23's statement of the CAPM by line (lm23.md:285) for the equation only. The LM23 entry for Sharpe
  (1964) is bibliographic data only, so LM28 does not cite it as the source of the term "capital market line".
- Jorion (1986), the "LM24" section: LM30 §6 states only the abstract's claim, that an empirical Bayes estimator of
  the means should outperform the sample mean in a portfolio; the shrinkage target stays unconfirmed there.
- Kan & Zhou (2007), "Fractional Kelly and parameter uncertainty (LM24)": one sentence in LM30. Crossref's abstract,
  re-read: the plug-in portfolio can perform very poorly out of sample, and a portfolio that optimally combines the
  riskless asset, the sample tangency portfolio and the sample global minimum-variance portfolio dominates a portfolio
  of the riskless asset and the sample tangency portfolio alone.
- Higham (2002b) and Rousseeuw & Molenberghs (1993), the "Volume II" bullet of the first papers list: LM30 §7 attributes
  only their abstracts (OpenAlex's copies, re-read). Higham: the nearest correlation matrix in two weighted Frobenius
  norms, by modified alternating projections for the more common weighting. Rousseeuw & Molenberghs: methods based on
  shrinking, a method based on eigenvalues, and a new geometric method. Crossref, re-read, agrees with the listed
  data (*IMA J. Numer. Anal.* 22(3): 329–343, 2002; *Comm. Stat. Theory Methods* 22(4): 965–984, 1993).
- Kuhn & Tucker (1951) and Kjeldsen (2000), the first papers list: LM29 cites them, and Karush (1939), through LM7's
  reference list (lm07.md:780–782) by pointer, with no new claim. Karush's M.Sc. thesis is **not** in this list (only
  the Wikipedia check on William Karush is), and Nocedal & Wright (2006), which LM7 cites, is entered under LM29.
- Maillard, Roncalli & Teïletche (2010), under LM27: LM31, from the working paper of May 2009 (read by the survey and
  rechecked by the LM31 drafter and by the second hunt): Euler's split (§2.1, p. 4, as under LM27); the ERC
  conditions `x_i(Σx)_i = x_j(Σx)_j` with `x ∈ [0, 1]ⁿ`, (1)–(2), pp. 4–5 (long-only called "voluntary"); the
  two-asset solution, inverse volatilities whatever the correlation, §3.1, p. 5; inverse-volatility weights under a
  constant correlation, eq. (3), §3.2, p. 5 (footnote 3 uses `ρ ≥ −1/(n − 1)`; LM31's strict bounds are the book's
  positive definite case); uniqueness for a positive definite covariance from formulation (7), §3.3, p. 7, an
  informal argument (LM31 derives (31.2) in full); minimum variance equalizes the marginal contributions and ERC the
  total contributions, §3.4, p. 8; `σ_mv ≤ σ_erc ≤ σ_1/n`, stated p. 9 and proved in Appendix A.3, p. 22, where the
  minimum-variance portfolio is the long-only one (program (8), `1ᵀx = 1`, `x ≥ 0`), which LM31 states. LM31 cites
  the JPM article at article level with these locations, labelled as the working paper's, and prints no JPM page or
  equation number.
- *RiskMetrics — Technical Document* (1996), the "LM26" section: LM31's EWMA with λ = 0.94, through LM26.

## Papers and books (Volume VI)

Checked 2026-10-24 from the Stage 1 briefs of LM32–LM35 and the source check (decision F), whose readings override the
briefs where the two differ; the Crossref record of every DOI below was then read again for this list (anonymous
requests, no contact data sent). Bibliographic data come from Crossref unless another source is named. Volume, issue,
pages and year agree with the briefs everywhere Crossref holds them; the differences are named in their entries (for
example the page numbers of Harvey & Liu's hosted copy). Where Crossref holds only the first page or no pages (the JSTOR
DOIs, the PBO article, the *Notices* article), the source of the missing fields is named. The Basel Committee's
documents are entered from their BIS pages, re-read. Section, equation and page numbers are those of the version named
in the entry. The source check read Ledoit & Wolf (2008), Hansen (2005), Romano & Wolf (2005), Bailey & López de Prado
(2012, 2014), Bailey et al. (2017) and Harvey & Liu (2015) in the versions named; it could obtain neither Kupiec (1995)
nor Christoffersen (1998), which a second source hunt of the same day (two fresh agents, anonymous requests) read in a
working paper and an author's manuscript, together with Lo (2002), the pages of Andrews & Monahan (1992), BCBS d450 and
Breuer et al. (2009), in the versions named. Works already in this list keep their entries: their Volume VI uses are
under "Entries already in this list: Volume VI locations", and the three entries that the new readings make wrong
(Ledoit & Wolf's, LM21's bibliographic list and Lo's) are rewritten. "Abstract" marks a claim read only in an abstract
(the copy named); "Text not read" means that only the citation or the abstract was seen; "Bibliographic data only" means
nothing in the text was read; "unverified" marks a field or claim that no record checked.

### LM32

- Artzner, Delbaen, Eber & Heath, "Coherent Measures of Risk", *Mathematical Finance* 9(3): 203–228, July 1999 (online
  25 December 2001), DOI [10.1111/1467-9965.00068](https://doi.org/10.1111/1467-9965.00068). Read by the survey and the
  LM32 drafter in the authors' ETH preprint of 22 July 1998: the four axioms that define coherence (translation
  invariance, subadditivity, positive homogeneity, monotonicity; relevance is a separate axiom); the survey located
  Definition 2.4, Axiom R, Proposition 4.1 and §3.3 there. The journal's numbering was not compared, so LM32 cites the
  paper for the definition only and prints no axiom or theorem number.
- Acerbi & Tasche, "On the coherence of expected shortfall", *J. Banking & Finance* 26(7): 1487–1503, July 2002, DOI
  [10.1016/S0378-4266(02)00283-2](https://doi.org/10.1016/S0378-4266(02)00283-2). Read by the LM32 drafter in arXiv
  cond-mat/0104295v5 (2 May 2002; arXiv's record, re-read, gives the journal reference "Journal of Banking & Finance
  26, 2002, pp. 1487-1503"): Definition 2.6 (the tail mean and ES, the form of (32.2)); Corollary 4.3 (independence of
  the quantile convention, by its statement there); Proposition 3.1 (coherence); the survey adds Example 5.4 (tail
  conditional expectation not subadditive). The journal's numbering was not compared, so the text cites the paper
  without numbers. Source of the book's historical ES (32.2) in every module (decision D).
- Acerbi & Tasche, "Expected Shortfall: A Natural Coherent Alternative to Value at Risk", *Economic Notes* 31(2):
  379–388, July 2002 (online 2 December 2003), DOI [10.1111/1468-0300.00091](https://doi.org/10.1111/1468-0300.00091).
  A different paper from the previous one (survey). Read by the LM32 drafter in arXiv cond-mat/0105191v1 (9 May 2001;
  arXiv's journal reference "Economic notes, 31(2), 379-388, 2002"): the sample estimator that averages the `⌊nu⌋`
  worst outcomes; used only for E1's third reading.
- Rockafellar & Uryasev, "Optimization of conditional value-at-risk", *J. Risk* 2(3): 21–41, 2000 (Crossref gives the
  year only), DOI [10.21314/jor.2000.038](https://doi.org/10.21314/jor.2000.038). Read by the survey and the LM32
  drafter in the working paper of 5 September 1999: the function `F_α(x, ζ)`, eq. (4); Theorem 1 (the minimum formula,
  with VaR the left end of the set of minimizers); Theorem 2 (joint minimization). The paper assumes a density, so the
  Deep Dive derives the empirical-distribution case itself. Equation and theorem numbers are the working paper's.
- Rockafellar & Uryasev, "Conditional value-at-risk for general loss distributions", *J. Banking & Finance* 26(7):
  1443–1471, July 2002, DOI [10.1016/S0378-4266(02)00271-6](https://doi.org/10.1016/S0378-4266(02)00271-6).
  Bibliographic data only: not relied on, and not cited unless Stage 2 reads it.
- Kupiec, "Techniques for Verifying the Accuracy of Risk Measurement Models", *J. Derivatives* 3(2): 73–84, 1995
  (Crossref: issued 30 November 1995), DOI [10.3905/jod.1995.407942](https://doi.org/10.3905/jod.1995.407942). The
  journal text was not read (pm-research.com is paywalled). Read by the second hunt in the working-paper version,
  Finance and Economics Discussion Series 95-24, Board of Governors of the Federal Reserve System (May 1995 on the
  cover, April 1995 on the title page; 47 pp.), in the official scan on FRASER, item 717921
  ([feds_1995-024.pdf](https://fraser.stlouisfed.org/files/docs/publications/bog_feds/feds_1995-024.pdf); the
  federalreserve.gov addresses answer 404). §IV, subsection "Tests Based on the Number of Failures" (from p. 18): the
  likelihood ratio of the proportion of failures, eq. (6), p. 19,
  `−2 log[(1 − p*)^(n−x) (p*)^x] + 2 log[(1 − x/n)^(n−x) (x/n)^x]`, with `n` the sample size, `x` the number of
  failures and `p*` the failure probability under the null, χ²(1) under the null; also §IV, "Verification Tests Based
  on Daily Monitoring" (from p. 10): the time-until-first-failure ratio, eq. (2), p. 11, χ²(1) with the 5% critical
  value 3.841, the χ² law asymptotic (footnote 12), and a two-sided test: its acceptance region (Table 1) has two
  bounds, and footnote 13 reads a first failure after day 438 as p < 0.01; §V, "Verification Test for Infrequent
  Monitoring Schemes": the statistic of eq. (6) for a fixed audit sample, eq. (8), p. 23 (the binomial coefficient of
  (7) cancels). Independence is assumed, not tested (p. 7, footnote 9). Equation and page numbers are the working paper's. Table 1's 5% row reproduces; Table 2 reproduces in
  14 of its 16 printed cells (two differ from eq. (6) at 3.841, and four cells are blank where eq. (6) rejects), so it
  is not used as a check. The label "POF" and tables for fixed samples such as 255, 510 or 1,000 days are not in this
  version, and nothing is taken from the journal's tables or equation numbers. LM32 §7 names the paper at section
  level with this version and prints no journal page or equation number; the lab computes the statistic beside LM21's
  exact tests (decision E). The survey's own likelihood-ratio ranges are not Kupiec's table.
- Christoffersen, "Evaluating Interval Forecasts", *International Economic Review* 39(4): 841–862, November 1998, DOI
  [10.2307/2527341](https://doi.org/10.2307/2527341). Crossref holds the first page only; the end page 862 comes from
  the RePEc record that the journal maintains (re-read: "vol. 39(4), pages 841-862, November") and fits Crossref's
  issue listing, whose next article starts at p. 863. The journal text was not read (JSTOR refused automated access;
  ResearchGate answered 403). Read by the second hunt in the author's final manuscript: 28 pp., thanking "two
  referees", with a disclaimer that it does not represent the views of the International Monetary Fund, its PDF dated
  7 July 1998; posted on his McGill homepage (`…/profs/christop/research/Pac1.pdf`, as CiteSeerX's record
  10.1.1.41.8009 names its source) and read in CiteSeerX's cached copy through the Internet Archive. Page numbers are
  the manuscript's. §2.1, Definition 1, p. 4: `I_t = 1` when the outcome lies inside the interval forecast and 0
  otherwise, `p` the coverage; a VaR is the one-sided interval `(L, +∞)`, p. 5; Lemma 1, p. 5: correct conditional
  coverage is equivalent to iid Bernoulli(`p`) indicators. §3.1, p. 6: `LR_uc = −2 log[L(p)/L(π̂)]` with
  `π̂ = n1/(n0 + n1)`, asymptotically χ²(1) (footnote 6 names Kupiec (1995) among similar tests of unconditional
  coverage). §3.2, pp. 7–8: `LR_ind` against a two-state first-order Markov chain, conditioning on the first
  observation, asymptotically χ²(1) and free of the true coverage. §3.3, p. 9: `LR_cc = −2 log[L(p)/L(Π̂₁)]`,
  asymptotically χ²(2) (a proposition proved in the appendix); ignoring the first observation, `LR_cc = LR_uc + LR_ind`.
  In this paper a VaR exceedance is `I_t = 0`; the three statistics are unchanged when 0 and 1 are swapped and `p`
  becomes `1 − p`. LM32 §7 names the paper at section level with this version; LM32's lab codes exceedances as 1,
  says the statistics are unchanged and computes the three statistics for the six models; LM21's exact-count independence
  check stays the book's own.
- Magdon-Ismail, Atiya, Pratap & Abu-Mostafa, "On the maximum drawdown of a Brownian motion", *J. Applied Probability*
  41(1): 147–161, March 2004, DOI [10.1239/jap/1077134674](https://doi.org/10.1239/jap/1077134674). Read by the LM32
  drafter in the authors' preprint dated 1 September 2003: with zero drift the expected maximum drawdown is
  `2γσ√T` with `γ = √(π/8) ≈ 0.6267`, eq. (16), which the preprint takes from Bond (2003); the journal's equation number
  was not compared, so the text cites the paper without it. Bond (2003) is **unverified**. Not the two-author *Risk*
  article "Maximum drawdown" (survey).
- Basle Committee on Banking Supervision (1996a), *Supervisory framework for the use of "backtesting" in conjunction
  with the internal models approach to market risk capital requirements* (BCBS 22). The BIS page (re-read; it prints
  'backtesting' in single quotes; the old address [bcbs22.htm](https://www.bis.org/publ/bcbs22.htm) now redirects to
  a new address under bis.org/publications/): Date Published 04 January 1996, Status Superseded, PDF 15 pages; a
  technical note in the three-part package that amended the 1988 Accord for market risks. Read by the survey and the
  LM32 drafter in the BIS PDF: §III's three zones; Table 2 (250 observations, 99% VaR): green 0–4 exceptions, yellow
  5–9, red 10 or more, with the cumulative probabilities 8.11% … 99.99%, all reproduced (A32-30); yellow starts where
  the cumulative probability reaches 95%, red where it reaches 99.99%.
- Basle Committee on Banking Supervision (1996b), *Amendment to the Capital Accord to incorporate market risks*
  (BCBS 24). The BIS page (re-read; title in lower case there; the old address bcbs24.htm now redirects to a
  [new address](https://www.bis.org/publications/199601-standards-amendment-capital-accord-incorporate-market-risks)):
  Date Published 04 January 1996, Status Superseded, PDF 56 pages; the page names the "Modifications to the market
  risk amendment" of 19 September 1997 as the subsequent version. Read by the survey and the LM32 drafter in the
  BIS PDF: Part B.4 "Quantitative standards", (a)–(d): daily VaR; a 99th percentile, one-tailed; a ten-day holding
  period, with square-root-of-time scaling allowed; at least one year of observations. The 1996 documents spell the
  committee "Basle".
- Basel Committee on Banking Supervision (2019), *Minimum capital requirements for market risk* (d457). The BIS page
  (re-read; the old address d457.htm now redirects to a
  [new address](https://www.bis.org/publications/201901-standards-minimum-capital-requirements-market-risk)): Date
  Published 14 January 2019; a corrected version was published on 25 February 2019 (typos, with an errata list); status
  "Consolidated" (integrated into the Basel Framework); it replaces the standard of January 2016; PDF 136 pages. The
  PDF's cover reads "January 2019 (rev. February 2019)" (the survey's text copy, re-read). MAR33.3, ES at a 97.5th
  percentile, one-tailed: read by the LM32 drafter in the BIS PDF; the paragraph (33.3 under MAR33) and its wording
  confirmed for this list in the survey's text copy.
- Checked, not cited:
  - Chekhlov, Uryasev & Zabarankin, "Drawdown measure in portfolio optimization" (Crossref's title is in capitals),
    *Int. J. Theoretical and Applied Finance* 8(1): 13–58, January 2005, DOI
    [10.1142/S0219024905002767](https://doi.org/10.1142/S0219024905002767). The survey read the January 2003 working
    paper ("Portfolio optimization with drawdown constraints"); the journal text was not read.
  - Jorion, *Value at Risk: The New Benchmark for Managing Financial Risk*, 3rd ed., McGraw-Hill, ISBN
    978-0-07-146495-6. Open Library's record (from Amazon, secondary): 19 October 2006, 600 pp.; the survey found
    © 2007 on the publisher's page. The year to cite is **unverified**. Not read.
  - McNeil, Frey & Embrechts, *Quantitative Risk Management: Concepts, Techniques and Tools*, revised edition,
    Princeton Series in Finance, Princeton University Press, 2015, xix + 699 pp., ISBN 978-0-691-16627-8, LCCN
    2015934589 (Open Library's copy of the LC MARC record; Princeton's page answered 403). The survey recorded 720 pp.
    and 26 May 2015 from the publisher's page. Not read.

### LM33

- Bailey & López de Prado, "The Sharpe Ratio Efficient Frontier" (Crossref: "The Sharpe ratio efficient frontier"),
  *J. Risk* 15(2): 3–44, December 2012 (Crossref: online December 2012, no print date), DOI
  [10.21314/jor.2012.255](https://doi.org/10.21314/jor.2012.255); SSRN 1821643, DOI
  [10.2139/ssrn.1821643](https://doi.org/10.2139/ssrn.1821643) (Crossref: posted content, 2011). Read in the authors'
  version of July 2012 (the survey, the LM33 drafter and the source check): the estimate's asymptotic distribution,
  (8), from Mertens, and the `n − 1` (Bessel's correction) in its standard deviation, §2.5, p. 8; PSR, eq. (11), p. 9,
  with `√(n − 1)` and raw kurtosis; MinTRL, eqs. (12)–(13), pp. 10–11, counted in observations, not years, with its
  "1 +" term; the examples, pp. 10–11 (p. 10: PSR(0) 0.982 under normality, 0.913 with the fund's skewness and
  kurtosis, 0.953 with three years; p. 11: MinTRL 2.73, 2.83 and 3.24 years for daily, weekly and monthly returns,
  and 4.99 years with skewness −0.72 and kurtosis 5.78); the code of Appendix A.3, p. 20, with those inputs (monthly
  mean 2, standard deviation √12, reference `1/√12`) and 59.895 months (the drafter, rechecked by the reviser in the
  source check's copy). LM33 reproduces 3.24 and 4.99 years (A33-30). Equation and page numbers are the authors'
  version's; the journal's were not compared.
- Bailey & López de Prado, "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and
  Non-Normality", *JPM* 40(5): 94–107, 2014 (Crossref: print and online 30 September 2014), DOI
  [10.3905/jpm.2014.40.5.094](https://doi.org/10.3905/jpm.2014.40.5.094); SSRN 2460551, DOI
  [10.2139/ssrn.2460551](https://doi.org/10.2139/ssrn.2460551) (Crossref: posted content, 2019, title without the
  comma before "and"). Read in the authors' version of 31 July 2014 (the survey, the LM33 drafter and the source
  check): the expected maximum Sharpe ratio of `N` independent trials with the Euler–Mascheroni constant, eq. (1),
  p. 7, derived in Appendix A.1, eqs. (3)–(6), p. 12; DSR, eq. (2), p. 8, a PSR at that threshold with `√(T − 1)` and
  raw kurtosis, its threshold eq. (1) without the mean term (eq. (1) scales by the standard deviation of the trials'
  estimated Sharpe ratios, the example's `V`; LM33's DSR uses `1/√(T − 1)` instead and says so); the worked example, pp. 9–10 (`N = 100`, `V = 1/2`,
  `T = 1250`, skewness −3, kurtosis 10: threshold ≈ 0.1132 and DSR ≈ 0.9004; 0.9505 at `N = 46`; with normal
  returns 0.9505 at `N = 88`; reproduced, A33-51); eq. (9), Appendix A.3, p. 14, the implied number of independent
  trials `N̂ = ρ̂ + (1 − ρ̂)M` with `ρ̂` the average correlation of eq. (8) — not the expected maximum. LM33 prints
  2.25 (A33-48), cited "eq. (9) of the authors' 31 July 2014 version". The journal's equation numbers were not
  compared. LM34 cites the paper by pointer.
- Götze & Künsch, "Second-order correctness of the blockwise bootstrap for stationary observations", *Ann. Statist.*
  24(5): 1914–1933, October 1996, DOI [10.1214/aos/1069362303](https://doi.org/10.1214/aos/1069362303). Bibliographic
  data only: named as Ledoit and Wolf's source for the resample's standard error.
- Andrews & Monahan, "An Improved Heteroskedasticity and Autocorrelation Consistent Covariance Matrix Estimator",
  *Econometrica* 60(4): 953–966, July 1992, DOI [10.2307/2951574](https://doi.org/10.2307/2951574). Crossref holds the
  first page only; the end page 966 comes from the Econometric Society's article page
  (econometricsociety.org/publications/econometrica/1992/07/01/notes-and-comments-improved-heteroskedasticity-and:
  "Volume 60, Issue 4 … p. 953-966", under the section label "Notes and Comments") and from RePEc's record of the
  Society's series ("vol. 60(4), pages 953-966, July"; read for this list and by the second hunt), and fits
  Crossref's issue listing, whose next article starts at p. 967 (this closes the LM33 brief's open item 3). The
  journal text was not read (JSTOR refused automated access). Abstract (RePEc's copy, which it says is borrowed from
  another version): prewhitened kernel estimators with vector autoregressions in the prewhitening stage. Read by the
  second hunt in Cowles Foundation Discussion Paper 942 (March 1990, a scan; the abstract and pp. 1–3 only;
  cowles.yale.edu/sites/default/files/2022-08/d0942.pdf): §1, p. 3, eq. (1.1), fit a vector autoregression, apply a
  kernel estimator to its residuals and undo the filter, "the VAR prewhitened kernel HAC estimator". The paper's
  treatment of the quadratic-spectral kernel was not checked. LM33 names the paper once, through Ledoit and Wolf's
  prewhitened quadratic-spectral kernel (that choice is theirs), cites pp. 953–966 and relies on nothing else in it.
- Opdyke, "Comparing Sharpe ratios: So where are the p-values?", *J. Asset Management* 8(5): 308–336, 2007
  (Crossref: online 30 November 2007, print December 2007), DOI
  [10.1057/palgrave.jam.2250084](https://doi.org/10.1057/palgrave.jam.2250084). Abstract (RePEc's, as the survey
  read it): an asymptotic formula valid for stationary ergodic returns. Bailey & López de Prado (2012) say Opdyke
  proved Mertens' variance identical to Christie's GMM expression (the survey's copy, re-read). Not cited unless the
  text needs it.
- Mertens (2002), not cited and not otherwise in this list: both Bailey & López de Prado papers print it as
  "Variance of the IID estimator in Lo (2002)", working paper, University of Basel, 2002 (their reference lists in
  the survey's copies, re-read). No copy was found (survey), and a Crossref search found no record: its content is
  **unverified**. LM20 derives (20.9) without it.
- Lo (2002), Ledoit & Wolf (2008) and Harvey & Liu (2015) are already in this list: see "Entries already in this list:
  Volume VI locations" and their rewritten entries under LM19 and LM20 (Lo), LM21 (Harvey & Liu) and LM22 (Ledoit &
  Wolf).

### LM34

- Bailey, Borwein, López de Prado & Zhu, "The probability of backtest overfitting", *J. Computational Finance* 20(4):
  39–69, April 2017 (first published online 19 September 2016; cite 2017), DOI
  [10.21314/JCF.2016.322](https://doi.org/10.21314/JCF.2016.322). Crossref holds no volume, issue or pages (online
  September 2016); they come from the publisher's article page at risk.net (read by the source check and again for
  this list: "Volume 20, Number 4 (April 2017)", "Pages: 39-69", "First published: 19 September 2016"; the page names
  four authors, though its citation tags list three). Read by the source check: Algorithm 2.3 (CSCV) in the authors'
  Lawrence Berkeley National Laboratory manuscript of 27 February 2015 (eScholarship, escholarship.org/uc/item/4w1110bb,
  which lists the article as *J. Computational Finance* 20(4), 2017); the JCF text was not compared. The steps: the
  `T × N` matrix of the trials' synchronous performance; `S` equal blocks of rows, `S` even; all `C(S, S/2)`
  combinations, eq. (2.3); for each, the chosen blocks in sample and the rest out of sample, each kept in time order,
  the in-sample best's out-of-sample rank over `N + 1` and its logit; their relative frequency, eq. (2.4). PBO is the
  mass of logits at or below 0 (§3.1); §3.2 adds the degradation regression and the probability of loss. The manuscript
  prints 12,780 for `C(16, 8) = 12,870`, and its step c) calls the in-sample set the testing set and step f) drops the
  bars: §7 states the steps in the book's own words, citing the manuscript. Dropping the earliest rows to make 16 equal
  blocks is the book's convention. Used for (34.4) and §7.
- Elton, Gruber & Blake, "Survivor Bias and Mutual Fund Performance", *RFS* 9(4): 1097–1120, October 1996, DOI
  [10.1093/rfs/9.4.1097](https://doi.org/10.1093/rfs/9.4.1097). Abstract (OpenAlex's copy, re-read): funds that
  disappear tend to do so after poor performance; the study tracks every fund that existed at the end of 1976 and
  follows mergers. Text not read; one sentence in §5.
- Brown, Goetzmann, Ibbotson & Ross, "Survivorship Bias in Performance Studies", *RFS* 5(4): 553–580, October 1992,
  DOI [10.1093/rfs/5.4.553](https://doi.org/10.1093/rfs/5.4.553). Bibliographic data only: the abstract OpenAlex holds
  (re-read) describes a presentation at a conference of March 1994, not this article, so no claim rests on it.
  Optional.
- Bailey, Borwein, López de Prado & Zhu, "Pseudo-Mathematics and Financial Charlatanism: The Effects of Backtest
  Overfitting on Out-of-Sample Performance", *Notices of the AMS* 61(5): 458–471, May 2014, DOI
  [10.1090/noti1105](https://doi.org/10.1090/noti1105). Crossref holds the first page only; the end page 471 comes from
  the running heads of the AMS PDF (read for this list; the survey read the first and last pages too). The survey read
  Theorem 2, the minimum backtest length, p. 462. Not relied on by LM34.
- Hansen (2005), Romano & Wolf (2005), White (2000) and Sullivan et al. (1999) are already in this list: see "Entries
  already in this list: Volume VI locations".

### LM35

- Basel Committee on Banking Supervision (2018), *Stress testing principles* (d450), October 2018, ISBN
  978-92-9259-207-3 (the PDF). The old addresses bcbs/publ/d450.htm and d450.pdf now redirect to a
  [new address](https://www.bis.org/publications/201810-guidelines-stress-testing-principles) (second hunt). That
  page (re-read for this list): Guidelines, Date Published 17 October 2018, Status Current, PDF 15 pages; the
  principles replace the *Principles for sound stress testing practices and supervision* of May 2009 (dated 20 May
  2009 there, status Superseded). Read by the second hunt in the BIS
  [PDF](https://www.bis.org/publications/201810-guidelines-stress-testing-principles.pdf): the title and the date
  (cover); the update of the 2009 principles, Introduction, p. 1, whose footnote 3 lists reverse stress testing among
  the methods; also p. 1: the principles are Guidelines, not Standards; Principle 4, p. 6 (PDF p. 10): "the scenarios
  should be sufficiently severe but plausible"; p. 6: reverse stress tests "explore scenarios that could potentially
  lead banks to fail" and so help banks identify their core vulnerabilities, and consideration should be given to
  historical events and hypothetical future events. LM35 §9 may print "severe but plausible" and the
  reverse-stress-test sentence (Principle 4, p. 6).
- Breuer, Jandačka, Rheinberger & Summer, "How to Find Plausible, Severe, and Useful Stress Scenarios", *International
  Journal of Central Banking* 5(3): 205–224, September 2009; no DOI (Crossref searches, run for this list and by the
  second hunt, find no record of the IJCB article, only SSRN working papers by the same authors). The journal's page
  (read 2026-10-24; the old address ijcb.org/journal/ijcb09q3a7.htm now redirects to
  [ijcb.org/journal/v5n3/…](https://www.ijcb.org/journal/v5n3/how-find-plausible-severe-and-useful-stress-scenarios)):
  title, the four authors, JEL codes G28, G32, G20 and C15, Volume 5, Issue 3, September 2009, a PDF of 20 pages.
  Read by the second hunt in the journal PDF linked there (ijcb.org/sites/default/files/journal/v5n3/, file
  `ijcb-v5n3-how-find-plausible-severe-and-useful-stress-scenarios.pdf`), pp. 205–224 from its first and last
  pages. The abstract: an operational definition of three Basel requirements for stress tests (plausibility,
  severity, suggestiveness of risk-reducing actions); a region of plausibility defined from the risk-factor
  distribution and searched systematically for the scenario with the worst portfolio loss; a plausibility measure
  free of the dimensional dependence of maximum loss; and setting the non-stressed risk factors to their conditional
  expected values given the stressed ones maximizes plausibility among the approaches in the literature. §2.1,
  p. 209: plausibility measured by the Mahalanobis distance `Maha(r) = √((r − μ)ᵀ Cov⁻¹ (r − μ))`, the square-root form,
  as LM35's `d`, a high value meaning low plausibility; §2.2, p. 210, Proposition 1: for an elliptical distribution
  whose density decreases in Maha, setting the non-stressed factors to their conditional expectation gives the most
  plausible scenario among those that agree on the fixed factors (the four options compared are attributed to Kupiec
  1998); §2.3, p. 211: the worst loss over the ellipsoid `Ell_k = {r : Maha(r) ≤ k}`. LM35 may print the Mahalanobis
  plausibility (§2.1, p. 209) and the worst loss within `d ≤ k`, which is the paper's construction, not the book's own
  (§2.3, p. 211); Proposition 1 may support (35.3)'s conditional choice under ellipticity. The survey also lists the
  paper as OeNB Working Paper 150: **unverified**.
- Kupiec, "Stress Testing in a Value at Risk Framework", *J. Derivatives* 6(1): 7–24, 1998 (Crossref: 31 August 1998),
  DOI [10.3905/jod.1998.408008](https://doi.org/10.3905/jod.1998.408008). Text not read (the publisher's page needs a
  login; OpenAlex holds no abstract). Cited only as Breuer et al. (2009, §2.2, p. 210) describe it: they attribute to
  it the four options they compare for the non-stressed risk factors. (35.3) is derived from (16.8).

### Entries already in this list: Volume VI locations

- Lo (2002), "LM19 and LM20": LM33. Read by the second hunt in the journal's layout (page headers "Financial Analysts
  Journal", "July/August 2002", "©2002, AIMR"; pp. 36–52), a copy posted by a UC Berkeley student organization
  (traders.studentorg.berkeley.edu), neither the author's nor the publisher's, of unknown licence: no author-hosted or
  official open copy exists (OpenAlex and Semantic Scholar list the paper as closed, the journal's own article page
  keeps it for members, and Lo's MIT page has no file). The abstract was confirmed word for word on the journal's own
  article [page](https://rpc.cfainstitute.org/research/financial-analysts-journal/2002/the-statistics-of-sharpe-ratios).
  Crossref, re-read: July 2002 (online 2 January 2019). Equations and tables checked on rendered pages: eq. (8),
  `V_IID = 1 + SR²/2`, and eq. (9), the standard error `√((1 + SR²/2)/T)`, p. 38; Lo's label is "IID", his
  `Var(σ̂²) ≈ 2σ⁴/T` (eqs. (5)–(6)) is the normal value, and (A33), p. 50, reduces his general variance to `V_IID` for
  normal returns, so LM33 writes "Lo's IID formula (9)"; the scale factor `η(q)` for `q`-period sums, eq. (20),
  p. 40, derived ignoring compounding (so it fits sums of log returns); the AR(1) form, eq. (22), and Table 2, "Scale
  Factors for Time-Aggregated Sharpe Ratios When Returns Follow an AR(1) Process …", p. 41, whose `q = 12` entries are
  3.46 at a first-order autocorrelation of 0 and 2.88 at 20%, as the text beside it states (the same paragraph gives
  4.17 at −20%); the GMM standard error, eqs. (14)–(15), pp. 39–40, with Newey and West's weights `1 − j/(m + 1)` and
  the divisor `T`, (A12)–(A14), p. 47, the weights and divisor of the book's (23.7) (Table 4's note, p. 44: lags 3
  and 6); the abstract's "as much as 65 percent", p. 36, is the annual Sharpe ratio "for a hedge fund" in an
  illustrative example of mutual funds and hedge funds, and LM33 keeps that scope (so does its LM19 and LM20 entry,
  rewritten). LM33 recomputes 2.88 and 3.46 (A33-24).
- Harvey & Liu (2015) and Hansen (2005), formerly in the LM21 "Bibliographic data only" bullet: both texts were read for
  LM33 and LM34, so they now have entries of their own in the LM21 section.
- Romano & Wolf (2005, *Econometrica*), "LM21": LM34. Read by the source check in the published article (the copy
  hosted at UZH, running pages 1237–1282; Crossref, re-read: July 2005). The setting: strategies relabelled from the
  largest statistic to the smallest, region (7) with a common critical value, a stepdown method (footnote 12),
  p. 1245. Algorithm 3.1, p. 1247: reject each remaining hypothesis whose statistic exceeds the bootstrap `1 − α`
  quantile, (9), of the maximum of the centred statistics over the hypotheses not yet rejected; repeat until nothing
  new is rejected. Algorithm 3.2, p. 1251, with at least 1,000 bootstrap data matrices; Remark 3.4: for a linear
  statistic and the Efron, circular or stationary bootstrap, the sample value may replace the centring parameter. The
  studentized form, §4.1, pp. 1252–1253: (10), Algorithm 4.1, and Algorithm 4.2 with each resample's own standard
  error; footnote 22: the original sample's standard error inside the resamples, Hansen's choice, is first-order
  consistent, though the resample's own is preferred; for block bootstraps they suggest the Götze–Künsch variance,
  p. 1254. LM34's E7 names the first step with footnote 22's variant and Remark 3.4's centring; the lab codes
  Algorithms 4.1 and 4.2.
- White (2000), "LM21": LM34's (34.3) and §6's Deep Dive. Read by the LM34 drafter (2026-10-24) in a copy of the
  published article in the journal's layout (30 pages, running pages 1097–1126; where the copy came from was not
  recorded), re-read for this list in the drafter's saved file: the statistic is the maximum over models of `√n`
  times the mean performance against the benchmark, its bootstrap counterpart the maximum of the recentred resampled
  means (Corollary 2.4, p. 1105), and the p-value one minus the observed statistic's rank among the sorted resampled
  ones over their number (§3, p. 1110); the resamples use Politis and Romano's stationary bootstrap. The corollary's
  hypotheses were read by Stage 1's fresh check (2026-10-31) in the published article on Bruce Hansen's course page
  at the University of Wisconsin (users.ssc.wisc.edu/~bhansen/718/White2000.pdf: the journal's layout, 30 pages,
  running pages 1097–1126, so its numbering is the published one). Corollary 2.4 (p. 1105) holds "under the
  conditions of Theorem 2.3": either (i) Assumptions A and B, with no estimated parameters; or (ii) Assumptions A–C
  and either (a) `F = 0` and `q_n = c n^(−γ)`, `c > 0`, `0 < γ < 1`, with `(n^(γ+ε)/R) log log R → 0` for some
  `ε > 0`, or (b) `(n/R) log log R → 0`, as `T → ∞` (p. 1105). Its conclusion: as `T → ∞`, the distance between the
  law of `V*_l = max_k n^(1/2)(f̄*_k − f̄_k)` given the data and that of `max_k n^(1/2)(f̄_k − E(f*_k))`, in any metric
  of convergence in distribution, tends to 0 in probability; likewise for the minimum `W*_l`. White's `n` counts the
  predictions `t = R, …, T`, `T = R + n − 1`, and `l` the models; the data are a stationary strong (α-) mixing
  sequence (§2.a, p. 1099); the stationary bootstrap's `q = 1/b = q_n` has `0 < q_n ≤ 1`, `q_n → 0` and `n q_n → ∞`
  (p. 1104). Assumption A, West's (1996), in the Mathematical Appendix (p. 1117): A.1, `f_t(β)` measurable and twice
  continuously differentiable near `β*`, its second derivatives bounded by `m_t` with `E m_t < D < ∞`; A.2,
  `β̂_t − β* = B(t)H(t)` with `B(t) → B` a.s. of rank `k` and `H(t)` the mean of orthogonality conditions `h_s(β*)` of
  mean 0; A.3, for the vector stacking `vec(f*_tβ)`, `f*_t` and `h_t`: (a) its norm has a finite moment of order
  `4d`, uniformly in `t`, for some `d > 1`, (b) it is strong mixing (centred) with coefficients of size `−3d/(d − 1)`,
  (c) it is covariance stationary, (d) the long-run covariance `S_ff` of `f*_t` is positive definite; A.4,
  `R, n → ∞` and `n/R → π`, `0 ≤ π ≤ ∞`; A.5, `π = 0` or `F = 0`, or a joint matrix `S` positive definite.
  Assumption B (p. 1119): the conditions of Theorem A.2, his version of Politis and Romano's (1994a) Theorem 2, for
  each element of `f*_t`: strict stationarity, `E|X_1|^(6+ε) < ∞` for some `ε > 0`, and α-mixing with
  `α(k) = O(k^(−r))` for some `r > 3(6 + ε)/ε`. Assumption C (p. 1104): a law of the iterated logarithm for `β̂_T`.
  With no estimated parameters `F` "plays no role" (p. 1101). The number of models is fixed: the theory treats "a
  finite number of specifications", and `l` growing with `T` gets heuristics only, a rigorous treatment being "beyond
  our present scope" (pp. 1110–1111); §5 lists it among open topics (p. 1115). A singular `Ω` keeps the corollary
  (pp. 1105–1106). The simple p-value `P_RC = 1 − M/N`, with `V*_(M) ≤ V_l < V*_(M+1)`, counts the resampled values
  strictly above `V_l` (p. 1110). Crossref, re-read: 68(5): 1097–1126, September 2000.
- Sullivan, Timmermann & White (1999), "LM21": one sentence in LM34's §6 (the reality check on technical trading
  rules). Crossref, re-read: *JF* 54(5): 1647–1691, October 1999.
- Ledoit & Wolf (2008), "LM22": LM33's two-Sharpe test, now read in the JEF text (its LM22 entry, rewritten).
- Jobson & Korkie (1981), "LM22": LM33 names it once; bibliographic data only. Memmel (2003) stays **unverified**,
  and LM33 does not cite it. Crossref, re-read: *JF* 36(4): 889–908, September 1981.
- Politis & Romano (1994), "LM22": LM32's block bootstrap of the drawdown (LM22's draw order) and the stationary
  bootstrap behind White's and Hansen's resamples (LM34). Crossref, re-read: 89(428): 1303–1313, December 1994.
- Politis & White (2004) with Patton, Politis & White (2009), "LM22": the block lengths by LM22's rule in LM32, LM33
  (`b = 22`) and LM34 (`ℓ = 75`), through arch's `optimal_block_length`. Crossref, re-read: 23(1): 53–70; 28(4):
  372–375.
- Lahiri (2003), "LM22": §2.7.1, the circular block bootstrap, p. 33, for LM33's circular resamples; Politis and
  Romano's 1992 original stays unread.
- Newey & West (1987), "LM23": LM33's Bartlett HAC with `ℓ = 7` and LM23's lag rule. Crossref, re-read: first page 703
  only.
- Glasserman (2003), §9.1.2 and (9.7), in the first papers list (LM18's closing check): LM32's (32.6), the quantile
  estimate's variance through the density at the quantile.
- Hill (1975), the first papers list: LM32's tail estimates, through LM20. The estimator's formula as printed is still
  not checked. Crossref, re-read: 3(5): 1163–1174, September 1975.
- *RiskMetrics — Technical Document* (1996) and the GARCH sources of the "LM26" section (Engle 1982; Bollerslev 1986,
  bibliographic data only): LM32's EWMA and GARCH VaR forecasts.
- Boyer, Gibson & Loretan (1999), Theorem 1, and Wasserman (2004), the Volume III entries: LM35's (16.10) and the
  distance `d²` of (16.7), through LM16.
- Jagannathan & Ma (2003), Proposition 1, under LM30 (Volume V): LM35, through LM30's (30.4).
- Bailey & López de Prado (2014), under LM33 above, and Harvey & Liu (2015): LM34 cites both by pointer.

## Python (Volume III)

Read 2026-10-18 in the NumPy v2.5 docs (`numpy.org/doc/stable`) and the SciPy v1.18.0 docs (`docs.scipy.org/doc/scipy`);
every numeric check ran in the project's venv (NumPy 2.5.3, SciPy 1.18.1).

- [`scipy.stats.lognorm`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.lognorm.html): pdf
  f(x, s) = exp(−log²x / (2s²)) / (s x √(2π)) for x > 0; if X is normal with mean mu and standard deviation sigma,
  Y = exp(X) is lognormal "with s = sigma and scale = exp(mu)". Checked with s = 0.5, scale = e^0.3: mean
  exp(μ + σ²/2), median e^μ.
- [`scipy.stats.t`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.t.html): the page gives the
  standardized pdf and `t.pdf(x, df, loc, scale) = t.pdf(y, df)/scale` with `y = (x − loc)/scale`. It does not print
  the variance: Var = scale²·df/(df − 2) follows from Y = loc + scale·T and was verified by computation, not read on the
  page: `t(5, scale=2).var()` = 6.6667 = 4·5/3; `t(2).var()` and `t(1.5).var()` are inf; `t(1).var()` and
  `t(0.5).var()` are nan. So the formula holds for df > 2, the variance is infinite for 1 < df ≤ 2 and undefined for
  df ≤ 1.
- [`rv_continuous.fit`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.rv_continuous.fit.html): the
  default method is MLE (minimizes the negative log-likelihood); `method="MM"` minimizes the L2 norm of the relative
  errors between the first k raw data moments and the distribution's, k being the number of non-fixed parameters.
  `f0…fn` (or `fa`, `fix_a`), `floc` and `fscale` fix parameters, so a two-parameter lognormal needs `floc=0`. Neither
  method is guaranteed to reach a global optimum, and data with nan or inf raise a RuntimeError.
- [`scipy.stats.kurtosis`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kurtosis.html):
  `kurtosis(a, axis=0, fisher=True, bias=True, nan_policy='propagate', *, keepdims=False)`; the fourth central moment
  over the squared variance, minus 3.0 when `fisher=True` (a normal gives 0); `bias=False` uses k statistics; the
  default `bias=True` uses central moments with divisor N (written out on the `skew` page). Checked: the default equals
  mean((x − x̄)⁴)/var(x, ddof=0)² − 3.
- [`scipy.stats.skew`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.skew.html):
  `skew(a, axis=0, bias=True, nan_policy='propagate', *, keepdims=False)`; the default is g₁ = m₃/m₂^(3/2) with
  m_i = (1/N) Σ (x − x̄)^i; `bias=False` gives G₁ = √(N(N−1))/(N−2) · g₁.
- NumPy [`default_rng`](https://numpy.org/doc/stable/reference/random/generator.html),
  [`PCG64`](https://numpy.org/doc/stable/reference/random/bit_generators/pcg64.html), the
  [random guide](https://numpy.org/doc/stable/reference/random/index.html) and
  [compatibility policy](https://numpy.org/doc/stable/reference/random/compatibility.html): `default_rng(seed=None)`
  builds a Generator on PCG64 (checked: `type(default_rng(20261011).bit_generator).__name__ == 'PCG64'`); integer seeds
  must be non-negative and go to `SeedSequence`; `None` pulls fresh OS entropy; no global instance is managed. The guide
  recommends "very large, unique numbers" as seeds and suggests `secrets.randbits(128)`. PCG64 is "PCG XSL RR 128/64",
  period 2^128, 2^127 streams, and a fixed seed always gives the same integer stream. Caveat: the Generator's streams
  are promised identical only for the same seed, the same calls with the same arguments, and the same NumPy build,
  environment and machine; stream-breaking changes are allowed in X.Y releases; five calls of `rng.random()` need not
  equal `rng.random(5)`; `multivariate_normal` may differ across builds (LAPACK). Reproducing printed simulation numbers
  therefore needs the NumPy version pinned (uv.lock).
- [`Generator.choice`](https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.choice.html):
  `choice(a, size=None, replace=True, p=None, axis=0, shuffle=True)`, with replacement by default.
  [`Generator.integers`](https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.integers.html):
  `integers(low, high=None, size=None, dtype=np.int64, endpoint=False)`, sampling [low, high) by default and
  [low, high] with `endpoint=True`; with `high=None` the results run from 0 to `low`.
- [`Generator.multivariate_normal`](https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.multivariate_normal.html):
  `multivariate_normal(mean, cov, size=None, check_valid='warn', tol=1e-8, *, method='svd')`; it computes A with
  A @ A.T = cov, by `'svd'` (default, slowest), `'eigh'` or `'cholesky'` (fastest, "less robust"); cov must be positive
  semidefinite or the behaviour is undefined; results may differ across builds, notably with repeated singular values
  under `'svd'`; `check_valid` (`'warn'`, `'raise'`, `'ignore'`) and `tol` govern a non-PSD cov. Checked: `'warn'`
  gives the RuntimeWarning "covariance is not symmetric positive-semidefinite.", `'raise'` a ValueError.
- [`scipy.stats.poisson`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.poisson.html): f(k) =
  exp(−μ) μ^k / k! for k ≥ 0, μ ≥ 0, only `loc` shifts it.
  [`scipy.stats.chi2`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2.html): f(x, k) =
  x^(k/2−1) e^(−x/2) / (2^(k/2) Γ(k/2)) for x > 0, a gamma with a = df/2, loc = 0, scale = 2.
  [`scipy.special.gammaln`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.gammaln.html): ln|Γ(x)|,
  "the same function as the Python standard library function math.lgamma". Checked: poisson(3) mean = var = 3;
  chi2(4) mean 4, var 8; gammaln(5) = ln 24.
- NumPy seeding ([Random Generator](https://numpy.org/doc/stable/reference/random/generator.html),
  [SeedSequence](https://numpy.org/doc/stable/reference/random/bit_generators/generated/numpy.random.SeedSequence.html),
  [Parallel Random Number Generation](https://numpy.org/doc/stable/reference/random/parallel.html), read 2026-10-18).
  `default_rng` accepts "array_like[ints]" (non-negative), passed to `SeedSequence`, whose entropy may be a
  "sequence[int]". Seeds that differ in one ID give streams that are independent "with very high probability"
  (collision probability about n²·2⁻¹²⁸). NumPy recommends "the varying IDs before the unvarying root seed": the form
  `[worker_id, root_seed]` is "Good", while `[root_seed, worker_id]` "will *work*, but it's less flexible", because
  `spawn` appends after the user's seed. Checked in NumPy 2.5.3: `default_rng([20261011, 1])` does not coincide with
  `SeedSequence(20261011).spawn(2)[1]`.
- NumPy [`Generator.random`](https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.random.html):
  "Return random floats in the half-open interval [0.0, 1.0)" (0 possible).
  [`standard_normal`](https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.standard_normal.html):
  mean 0, standard deviation 1.
  [`numpy.quantile`](https://numpy.org/doc/stable/reference/generated/numpy.quantile.html): default `method='linear'`
  (Hyndman & Fan 7); `'inverted_cdf'` (H&F 1, discontinuous) returns order statistic ⌈qn⌉ (checked for LM14's nine
  levels at T = 5,849 and for qn integer).
  [`median`](https://numpy.org/doc/stable/reference/generated/numpy.median.html) averages the two middle values when
  N is even; [`std`](https://numpy.org/doc/stable/reference/generated/numpy.std.html) `ddof=0` by default;
  [`cov`](https://numpy.org/doc/stable/reference/generated/numpy.cov.html) divides by N − 1 by default (`bias=True`
  for N); [`log1p`](https://numpy.org/doc/stable/reference/generated/numpy.log1p.html) gives nan below −1.
- SciPy v1.18.0: [`norm`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html) `ppf` = inverse
  cdf, `sf` = 1 − cdf ("sometimes more accurate"), `moment` = non-central moment;
  [`rv_continuous.expect`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.rv_continuous.expect.html)
  integrates numerically with `quad` and cannot check that the integral exists;
  [`rv_continuous.stats`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.rv_continuous.stats.html)
  `'k'` = Fisher's (excess) kurtosis;
  [`rv_discrete`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.rv_discrete.html)
  `values=(xk, pk)` with integer, unique `xk`, and a discrete `ppf` is the smallest x_k with F(x_k) ≥ q
  ([tutorial](https://docs.scipy.org/doc/scipy/tutorial/stats/discrete.html));
  [`binom`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binom.html) shapes n, p;
  [`optimize.brentq`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.brentq.html) needs a sign
  change on [a, b]. `norm.fit` returning the divisor-T standard deviation was computed, not read.
- Python 3.13 [`fractions.Fraction`](https://docs.python.org/3.13/library/fractions.html): a string such as
  `'1.414213'` parses exactly (`Fraction(1414213, 1000000)`), unlike a float. Checked: `Fraction('4524.92')` =
  113123/25.
- Polars 2.0 [`Expr.shift`](https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.shift.html)
  leaves nulls in the vacated rows unless given `fill_value`;
  [`Expr.std`](https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.std.html) defaults to
  `ddof=1` (divisor N − 1).

## Python (Volume IV)

Checked 2026-10-19 by the Stage 1 survey and the fresh check in the source of the statsmodels 0.15.0 and arch 8.0.0
wheels (cp313, win_amd64; sha256 checked against PyPI); file:line references are inside the unpacked wheels. The
documentation pages below returned HTTP 200 and carry these versions (page titles "statsmodels 0.15.0" and "arch
8.0.0"; status and titles read again in Stage 1); their text was not compared line by line with the source. A
line marked "read again in Stage 1" was read in the same wheel source in Stage 1, not by the survey. Prefixes:
statsmodels pages are under `https://www.statsmodels.org/stable/generated/`, arch pages under
`https://bashtage.github.io/arch/`; "stable" was 0.15.0 on that date.

### The packages

- statsmodels 0.15.0, released 2026-08-27
  ([release notes](https://www.statsmodels.org/stable/release/version0.15.0.html)), BSD-3-Clause; arch 8.0.0,
  released 2025-10-21, NCSA, the latest on PyPI ([changelog](https://bashtage.github.io/arch/changes.html)); dates and
  licences from PyPI's JSON ([statsmodels](https://pypi.org/pypi/statsmodels/json),
  [arch](https://pypi.org/pypi/arch/json)).
- Requirements: arch requires `statsmodels>=0.13.0`, so the two are one decision. statsmodels requires
  `numpy<3,>=1.23.5`, `scipy!=1.9.2,>=1.8`, `pandas!=2.1.0,>=1.4`, `patsy>=0.5.6`, `packaging>=21.3` and, new in 0.15,
  `formulaic>=1.1.0`; arch requires `numpy<3,>=1.22.3`, `pandas>=1.4.0`, `scipy>=1.8` and `packaging` (numba only in
  its `dev` extra). New packages: pandas 3.0.6, patsy 1.0.3, formulaic 1.2.2, narwhals 2.27.1, wrapt 2.5.1,
  interface-meta 2.0.1 and tzdata 2026.5; about 81.5 MB unpacked in all (the wheels were read, not installed). The
  working tree's `uv.lock` pins statsmodels 0.15.0, arch 8.0.0 and pandas 3.0.6 beside NumPy 2.5.3 and SciPy 1.18.1
  (read again in Stage 1).
- arch 8.0.0 predates pandas 3.0.0 (2026-01-21) and statsmodels 0.15.0; every statsmodels symbol arch imports exists
  in 0.15.0 (static check). The smoke test of 2026-10-19 in an empty `UV_PROJECT_ENVIRONMENT` (plans/vol-4.md,
  capability A) ran them together without error: `./build.sh --data --labs --preview` reproduced every tracked chart
  file byte for byte and every lab's text output, and `arch_model` (normal and $t$), the three block bootstraps with a
  NumPy `Generator` as `seed` (identical on a rerun), `optimal_block_length`, `adfuller`, `kpss`, `coint`,
  `acorr_ljungbox`, OLS with HAC (equal to a NumPy Newey–West to 2e-15), `multipletests` and `ARIMA` ran on TR23.
- Both packages import pandas when the modules the book uses load (statsmodels: `base/model.py:10`, `tsatools.py:9`,
  `_stattools.py:13`, `diagnostic.py:35`, `multitest` through `stats/_knockoff.py:26`; arch: `univariate/mean.py:12`).
  Importing OLS also loads patsy and formulaic. Book code passes NumPy arrays and ends with `.to_numpy()`. statsmodels
  accepts a Polars frame but converts it with `.to_pandas()` (`tools/data.py:205-206`); whether that needs pyarrow is
  unverified.
- numba is not needed: arch's Windows wheel ships compiled `recursions.cp313-win_amd64.pyd` and
  `_samplers.cp313-win_amd64.pyd`; its kernel covariance falls back to pure Python silently
  (`covariance/kernel.py:148-151`).

### statsmodels 0.15.0

- [`OLS.fit`](https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.OLS.fit.html) and
  [`get_robustcov_results`](https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.RegressionResults.get_robustcov_results.html):
  `fit(method="pinv", cov_type="nonrobust", cov_kwds=None, use_t=None, **kwargs)`; with `cov_type="HAC"`,
  `cov_kwds={"maxlags": L}` is required, the kernel defaults to Bartlett with weights 1 − j/(L + 1), j = 0, …, L
  (`sandwich_covariance.py:543`), and `use_correction` defaults to False (`linear_model.py:2884`); with it the
  covariance is multiplied by n/(n − k) (`sandwich_covariance.py:976-978`). `use_t=None` means t for `nonrobust` and
  the normal distribution for every robust type, so HAC p-values are normal (docstring, `linear_model.py:2645-2647`;
  code `linear_model.py:1868-1888` and `base/model.py:1546`, fresh check). This default is statsmodels', not arch's:
  arch 8.0.0 has no `use_t`.
- [`adfuller`](https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.adfuller.html):
  `adfuller(x, maxlag=None, regression="c", autolag="AIC", store=False, regresults=False, *, result_object=None)`
  (`_stattools.py:233-242`). The default maximum lag is 12(nobs/100)^(1/4); the code rounds it up
  (`int(np.ceil(...))`, `_stattools.py:373`, read again in Stage 1). The p-value is "MacKinnon's approximate p-value
  based on MacKinnon (1994, 2010)" and the critical values follow MacKinnon (2010) (`_stattools.py:184-192`;
  `adfvalues.py:256-258, 447-452`). `result_object=None` returns the old tuple with a FutureWarning; pass
  `result_object=True`. The docstring says the default changes "In release 0.16.0 or after July 2027, whichever is
  later" (`_stattools.py:279-289`, read again in Stage 1).
- [`kpss`](https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.kpss.html):
  `kpss(x, regression="c", nlags="auto", store=False, *, result_object=None)`, `regression` "c" or "ct", `nlags`
  "auto", "legacy" or an integer (`_stattools.py:3051-3062`); `nlags=None` now raises an error; `result_object` as
  for `adfuller`. The page cites Hobijn et al. as vol. 52; Crossref gives 58(4): 483–502.
- [`coint`](https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.coint.html):
  `coint(y0, y1, trend="c", method="aeg", maxlag=None, autolag="aic", return_results=None)`
  (`_stattools.py:2571-2579`): it takes `return_results`, not `result_object`; MacKinnon's approximate p-value
  (1994, 2010).
- [`acf`](https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.acf.html):
  `acf(x, adjusted=False, nlags=None, qstat=False, fft=True, alpha=None, bartlett_confint=True, missing="none", *,
  result_object=None)` (`_stattools.py:847-858`); it warns (FutureWarning) when only one of `qstat` and `alpha` is
  requested (`:909-919`). Its convention, read again in Stage 1: `acf` calls `acovf` with `demean=True`
  (`_stattools.py:1012`), which subtracts the full-sample mean (`:564`) and divides every lag by n when
  `adjusted=False` ("If True, then denominators is n-k, otherwise n", `:488-498`).
  [`pacf`](https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.pacf.html):
  `pacf(x, nlags=None, method=…)` (`:1315`).
- [`acorr_ljungbox`](https://www.statsmodels.org/stable/generated/statsmodels.stats.diagnostic.acorr_ljungbox.html):
  `acorr_ljungbox(x, lags=None, boxpierce=False, model_df=0, period=None, return_df=True, auto_lag=False)`
  (`diagnostic.py:596-604`); it always returns a DataFrame, `return_df` being "retained for backward compatibility"
  (`:635-645`).
- [`multipletests`](https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html):
  `multipletests(pvals, alpha=0.05, method="hs", maxiter=1, is_sorted=False, returnsorted=False)`
  (`multitest.py:99-101`): the default is Holm–Šidák, **not** Holm; `"bonferroni"`, `"holm"`, `"fdr_bh"` and
  `"fdr_by"` are available (`:203, 233, 269`).
- [`ARIMA`](https://www.statsmodels.org/stable/generated/statsmodels.tsa.arima.model.ARIMA.html):
  `ARIMA(endog, exog=None, order=(p, d, q), …)` (`tsa/arima/model.py:26, 145`).
- [`coint_johansen`](https://www.statsmodels.org/stable/generated/statsmodels.tsa.vector_ar.vecm.coint_johansen.html):
  `coint_johansen(endog, det_order, k_ar_diff)`, giving `lr1`, `lr2`, `cvt`, `cvm`, `eig` and `evec`
  (`vecm.py:594, 763-803`).

### arch 8.0.0

- [`arch_model`](https://bashtage.github.io/arch/univariate/introduction.html#arch.univariate.arch_model):
  `arch_model(y, x=None, mean="Constant", lags=0, vol="GARCH", p=1, o=0, q=1, power=2.0, dist="normal",
  hold_back=None, rescale=None)`; `mean` includes "Zero", `dist` includes "t" (`univariate/mean.py:1887-1911`). The
  survey's link (`univariate/mean.html#arch.univariate.arch_model`) opens a page without that anchor; the function is
  documented on the introduction page above (read again in Stage 1).
- [`ARCHModel.fit`](https://bashtage.github.io/arch/univariate/generated/generated/arch.univariate.base.ARCHModel.fit.html):
  `fit(update_freq=1, disp="final", starting_values=None, cov_type="robust", show_warning=True, first_obs=None,
  last_obs=None, tol=None, options=None, backcast=None)`; SciPy's SLSQP with bounds and constraints
  (`univariate/base.py:617-629, 807-815`). Results: `params`, `pvalues` and `std_err` are pandas Series
  (`base.py:1320, 2027, 2035`); `resid` and `conditional_volatility` stay ndarrays for NumPy input
  (`base.py:1335-1338, 1352-1355`).
- [`ARCHModelResult.forecast`](https://bashtage.github.io/arch/univariate/generated/generated/arch.univariate.base.ARCHModelResult.forecast.html):
  `forecast(params=None, horizon=1, start=None, align="origin", method="analytic", simulations=1000, rng=None,
  random_state=None, *, reindex=False, x=None)`; `.variance` is a DataFrame (`base.py:1444-1456, 2224`).
- Scale warning: when the residual variance lies outside [0.1, 10000), arch warns and suggests rescaling
  (`base.py:309-322`); daily decimal returns trigger it, so Volume IV fits returns in percent (or passes `rescale`).
- [`StationaryBootstrap`](https://bashtage.github.io/arch/bootstrap/generated/arch.bootstrap.StationaryBootstrap.html),
  [`CircularBlockBootstrap`](https://bashtage.github.io/arch/bootstrap/generated/arch.bootstrap.CircularBlockBootstrap.html),
  [`MovingBlockBootstrap`](https://bashtage.github.io/arch/bootstrap/generated/arch.bootstrap.MovingBlockBootstrap.html):
  `(block_size, *args, seed=None, **kwargs)` (`bootstrap/base.py:1511/1586, 1367/1442, 1609/1686`); `seed` accepts
  `int | Generator | RandomState` (`base.py:391`), so the experiment's NumPy generator can be passed.
- [`optimal_block_length`](https://bashtage.github.io/arch/bootstrap/generated/arch.bootstrap.optimal_block_length.html) (corrected in Stage 1, 2026-10-19):
  - `optimal_block_length(x) -> pd.DataFrame` (`bootstrap/base.py:126`) returns columns **`stationary`** and **`circular`**.
    - Code: `base.py:202`. Running it on 500 normals gave `['stationary', 'circular']`.
    - The docstring (`base.py:139–141`) and the doc page both say `b_sb` and `b_cb`. Those are the internal variable names (`base.py:119–123`).
  - Each estimate is capped at ⌈min(3√n, n/3)⌉ (`base.py:91`, applied at `:121–122`); the page does not mention the cap.
  - It implements Politis & White (2004) with Patton, Politis & White's (2009) correction (docstring, `base.py:185–190`).
- [`ADF`](https://bashtage.github.io/arch/unitroot/generated/arch.unitroot.ADF.html) (also
  [`KPSS`](https://bashtage.github.io/arch/unitroot/generated/arch.unitroot.KPSS.html),
  [`PhillipsPerron`](https://bashtage.github.io/arch/unitroot/generated/arch.unitroot.PhillipsPerron.html)):
  `ADF(y, lags, trend, max_lags, method, low_memory)` (`unitroot/unitroot.py:664, 754-762, 1004, 1207`).
  [`engle_granger`](https://bashtage.github.io/arch/unitroot/generated/arch.unitroot.cointegration.engle_granger.html):
  `engle_granger(y, x, trend="c", *, lags, max_lags, method="bic")` (`unitroot/_engle_granger.py:25-33`); its critical
  values come from arch's own tables (`critical_values/engle_granger.py`), whose source is unverified.

### SciPy 1.18 (locked 1.18.1)

- [`scipy.stats.bootstrap`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html) (v1.18.0
  docs): defaults `method='BCa'`, `n_resamples=9999`, `confidence_level=0.95`; iid resampling only, no block scheme;
  cites Efron & Tibshirani (1993).
- [`scipy.stats.false_discovery_control`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.false_discovery_control.html):
  `false_discovery_control(ps, *, axis=0, method='bh')`, methods `'bh'` and `'by'`; `'by'` controls the FDR under
  dependence, citing Benjamini & Yekutieli (2001), Theorem 1.3 (checked in the locked 1.18.1).

### Stage 1 additions to the Python facts (2026-10-19, after the briefs)

- **Documentation pages:**
  - SciPy's `stable` pages are titled "SciPy v1.18.0 Manual"; `docs.scipy.org/doc/scipy-1.18.1/` returns 404.
  - NumPy pages are under `numpy.org/doc/2.5/`.
  - statsmodels pages are under `https://www.statsmodels.org/v0.15.0/generated/`, titled "statsmodels 0.15.0".
  - arch pages are titled "arch 8.0.0".
- **Source lines** are in the project venv's `.venv/Lib/site-packages`: SciPy 1.18.1, NumPy 2.5.3, statsmodels 0.15.0, arch 8.0.0.

#### arch 8.0.0 (Stage 1 check)

- `seed` of the block bootstraps. The page says: "If an int, passes the value to value to np.random.default_rng" (sic).
  - Code (`base.py:399–404`): a Generator or RandomState is used as given; an int becomes `np.random.default_rng(int(seed))`; `None` becomes `default_rng()`.
- [`kernel.Bartlett`](https://bashtage.github.io/arch/covariance/generated/arch.covariance.kernel.Bartlett.html): `kernel_const` 1.1447 and `rate` 2/9 (`covariance/kernel.py:440–451`).
  - The pilot lag in `_alpha_q` is n = ⌈4(nobs/100)^{2/9}⌉ (`kernel.py:337`). arch rounds up, Newey and West print [·], and statsmodels takes the floor.
  - The bandwidth is 1.1447(α̂T)^{1/3}, capped at nobs − 1 (`:362–374`).
  - So arch's default Bartlett lag is **not** the book's rule.
- `cov_type` of [`ARCHModel.fit`](https://bashtage.github.io/arch/univariate/generated/generated/arch.univariate.base.ARCHModel.fit.html), for LM26. Read 2026-10-19 after the fresh check, on the page (titled "arch 8.0.0", HTML fetched with curl) and in the venv source; run in the venv.
  - The page: `cov_type: 'robust' | 'classic' = 'robust'`. "Supported options are 'robust', which does not assume the Information Matrix Equality holds and 'classic' which does. In the ARCH literature, 'robust' corresponds to Bollerslev-Wooldridge covariance estimator." The docstring is the same (`univariate/base.py:644–648`). The page names Bollerslev and Wooldridge without a year or title; no brief cites them, so the article is not looked up.
  - Code (`univariate/base.py:941–988`): both use numerical derivatives of the negative log-likelihood (`_loglikelihood` returns the "Negative of model loglikelihood", `:460–481`). With H = `approx_hess(…)`/nobs, "classic" is H⁻¹/nobs. "robust" is H⁻¹SH⁻¹/nobs, where S is `np.cov` of the per-observation scores from `approx_fprime` (centred, divisor nobs − 1).
  - The result uses the robust form only when `cov_type == "robust"`, and the classic form for any other value (`:1989–1992`). The argument is not validated, so a misspelling silently gives classic errors. Checked: on a simulated GARCH(1,1) series, `cov_type="Classic"` gave the classic standard errors, and the parameters are the same under both options.

#### SciPy 1.18 (Stage 1 check)

- [`ttest_1samp`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_1samp.html): `(a, popmean, axis=0, nan_policy='propagate', alternative='two-sided', *, keepdims=False)`.
- [`ttest_ind`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html): `(a, b, *, axis=0, equal_var=True, nan_policy='propagate', alternative='two-sided', trim=0, method=None, keepdims=False)`. `equal_var`: "If True (default), perform a standard independent 2 sample test that assumes equal population variances"; `False` is Welch's test.
- [`chi2_contingency`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html): `(observed, correction=True, lambda_=None, *, method=None)`. `correction`: "If True, and the degrees of freedom is 1, apply Yates' correction for continuity". It is therefore on by default for a 2×2 table.
- [`binomtest`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html): `(k, n, p=0.5, alternative='two-sided')`.
- [`jarque_bera`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.jarque_bera.html): `(x, *, axis=None, nan_policy='propagate', keepdims=False)`.
  - The page says the test "only works for a large enough number of data samples (>2000)", with an asymptotic χ²₂ law, and prints no formula.
  - Code (`stats/_stats_py.py:1931–1939`): statistic = n/6·(s² + k²/4), where s and k are `skew` and Fisher `kurtosis` at their defaults (divisor n, `bias=True`); the p-value is the χ²₂ upper tail.
- [`bootstrap`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html): `(data, statistic, *, n_resamples=9999, batch=None, vectorized=None, paired=False, axis=0, confidence_level=0.95, alternative='two-sided', method='BCa', bootstrap_result=None, rng=None)`. The page also shows `random_state=None`.
  - `rng` passed by keyword: a Generator is used as given; other values go to `default_rng`. Passed positionally or as `random_state`, it takes the legacy RandomState behaviour.
  - `batch`: "Default is None, in which case batch = n_resamples (or batch = max(n_resamples, n) for method='BCa')".
  - `method`: 'percentile', 'basic' ("AKA 'reverse'") or 'BCa'.
  - `standard_error`: "the sample standard deviation of the bootstrap distribution". The page's example checks it against `np.std(…, ddof=1)`, i.e. divisor B − 1 (code `_resampling.py:684`).
  - Code:
    - resamples are `rng_integers(rng, 0, n, (n_resamples, n))` (`:80`);
    - the interval ends are `stats.quantile(theta_hat_b, …)` (`:663`), whose default is `method='linear'` (`_quantile.py:161`);
    - the basic interval is 2θ̂ minus the ends (`:675–677`).
  - **The ends are not the book's `inverted_cdf`, and the page does not name the method.**
- [`t`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.t.html), [`chi2`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2.html), [`norm`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html), [`beta`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.beta.html):
  - Methods: `ppf(q, df, loc=0, scale=1)` ("Percent point function (inverse of cdf — percentiles)") and `logpdf(x, df, loc=0, scale=1)`. `norm` takes no `df`; `beta` takes `a, b`.
  - beta's density: f(x, a, b) = Γ(a+b)x^{a−1}(1−x)^{b−1}/(Γ(a)Γ(b)) for 0 ≤ x ≤ 1, a, b > 0.
- [`minimize(method='Nelder-Mead')`](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-neldermead.html):
  - The page says `maxiter` and `maxfev` "Will default to N*200 … if neither maxiter or maxfev is set".
  - `xatol` and `fatol` are documented, but the page prints no defaults.
  - Code `optimize/_optimize.py:701–704`: `xatol=1e-4`, `fatol=1e-4`, `adaptive=False`.
- [`kurtosis`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kurtosis.html) with `bias=False`.
  - The page says it is "calculated using k statistics to eliminate bias coming from biased moment estimators".
  - Code `_stats_py.py:1431–1435`, for n > 3: [(n²−1)m₄/m₂² − 3(n−1)²]/((n−2)(n−3)). By algebra this equals `(n−1)[(n+1)g₂ + 6]/((n−2)(n−3))`.
- [`brentq`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.brentq.html): `(f, a, b, args=(), xtol=2e-12, rtol=8.881784197001252e-16, maxiter=100, full_output=False, disp=True)`. "f(a) and f(b) must have opposite signs".
- NumPy [`Generator.standard_t`](https://numpy.org/doc/2.5/reference/random/generated/numpy.random.Generator.standard_t.html): `(df, size=None)`, with df "must be > 0".

#### statsmodels 0.15.0 (Stage 1 check)

- `robust_skewness(y, axis=0)` and `robust_kurtosis(y, axis=0, ab=(5.0, 50.0), dg=(2.5, 25.0), excess=True)`. The pages give SK₂ and KR₂ as above and cite Kim & White.
  - Quantiles come from `np.percentile` at NumPy's default, linear (`stats/stattools.py:198, 376`). **They are not `inverted_cdf`.**
  - `kr1 = stats.kurtosis(y, axis, False)`, which is `fisher=False` (`:382`); `kr2` is at `:383`.
  - `excess=True` subtracts `expected_robust_kurtosis()`, whose KR₂ entry for the normal is 1.23309512 (computed).
- `HC0_se` page: "White's (1980) heteroskedasticity robust standard errors". `HC1_se` page: "MacKinnon and White's (1985) … Defined as sqrt(diag(n/(n-p)*HC_0)". Code: `regression/linear_model.py:2222–2236`.
  - `get_robustcov_results(cov_type='HC1', use_t=None, **kwargs)` (page; `:2634`) defaults to HC1. The book's HC0 must be requested explicitly.
- [`cov_hac`](https://www.statsmodels.org/v0.15.0/generated/statsmodels.stats.sandwich_covariance.cov_hac.html) is the alias of `cov_hac_simple`, whose v0.15.0 page returns 404. Signature: `(results, nlags=None, weights_func=weights_bartlett, use_correction=True)`.
  - `nlags`: "If None, then nlags = floor[4(T/100)^(2/9)] is used".
  - `use_correction`: "If true (default), then a small sample correction factor is used". The Notes add: "just guessing on correction factor, need reference".
  - Code:
    - the lag rule is `int(np.floor(4 * (n_periods / 100.0) ** (2.0 / 9.0)))` (`stats/sandwich_covariance.py:606–607`);
    - the correction multiplies by nobs/(nobs − k) (`:976–978`);
    - a module comment reads "Reference: xtscc paper, Newey-West" (`:72–73`).
  - `OLS.fit(cov_type="HAC")` still requires `maxlags` (already recorded), so this default lag applies only through `cov_hac`, `cov_hac_simple` and `S_hac_simple`.
- `acorr_ljungbox`. The page says: "If lags is None, then the default maxlag is min(10, nobs // 5)"; "The data is demeaned before the test statistic is computed".
  - Code: the lags are at `stats/diagnostic.py:736–738`; Q = nobs(nobs+2)Σρ̂ₖ²/(nobs − k) is computed with `acf(fft=False)` (`:746–749`).
- `kpss`. The page says: "a boundary point is returned if the test statistic is outside the table of critical values, that is, if the p-value is outside the interval (0.01, 0.1)".
  - Code: the critical values are 0.347, 0.463, 0.574 and 0.739 for "c" and 0.119, 0.146, 0.176 and 0.216 for "ct" (`tsa/stattools/_stattools.py:3182–3187`).
  - p = `np.interp(stat, crit, [0.10, 0.05, 0.025, 0.01])` (`:3211–3217`), so p is clipped to [0.01, 0.10], with an `InterpolationWarning` (`:3219–3235`).
- `pacf(x, nlags=None, method='ywadjusted', alpha=None, *, result_object=None)` (page; `:1315–1337`). The page describes the default as "Yule-Walker with sample-size adjustment in denominator for acovf"; `"ols"` is "regression of time series on lags of it and on constant".
- `ARIMA`, trend: "Default is 'c' for models without integration, and no trend for models with integration" (page; `tsa/arima/model.py:152–159`).
  - Trends enter as "regression with ARIMA errors": Yₜ − δ₀ − … = εₜ, with εₜ ARMA (page, Notes).
  - Reading that equation: with d = 0, `const` is the process mean.
- `ARIMA.fit(…, method=None, …, cov_type=None, …)`.
  - Methods: 'statespace', 'innovations_mle', 'hannan_rissanen', 'burg', 'innovations', 'yule_walker'. `None` means "statespace" (`model.py:326–335`).
  - With `"innovations_mle"` the estimates come from `innovations_mle` (`:454–455`), and the results are rebuilt by `smooth(…, cov_type=cov_type)` (`:501`).
- `MLEModel.fit(…, cov_type=None, cov_kwds=None, method='lbfgs', maxiter=50, …)`.
  - The `cov_type` options are 'opg'; 'oim' ("observed information matrix estimator, calculated using the method of Harvey (1989)"); 'approx' ("… numerical approximation of the Hessian matrix"); 'robust', 'robust_approx' and 'none'.
  - "Default is 'opg' unless memory conservation is used …, in which case the default is 'approx'". The code agrees (`tsa/statespace/mlemodel.py:2800–2801`).
  - The ARIMA.fit page says 'oim' for the memory-conservation case. It disagrees with the code.
- [`het_arch`](https://www.statsmodels.org/v0.15.0/generated/statsmodels.stats.diagnostic.het_arch.html), for LM26. Read 2026-10-19 after the fresh check, on the page (titled "statsmodels 0.15.0", HTML fetched with curl) and in the venv source; run in the venv.
  - Signature: `het_arch(resid, nlags=None, store=False, ddof=0, *, result_object=None)` (page; `stats/diagnostic.py:936–938`).
  - The page says `result_object` returns "an LMTestResult NamedTuple instead of a plain tuple". With `store=False`, "the legacy four-element tuple is returned by default and a FutureWarning is issued". "In release 0.16.0 or after July 2027, whichever is later, the default will change to always return an LMTestResult." The fields are `lm`, `lmpval`, `fval`, `fpval` and `res_store`. Notes: "verified against R:FinTS::ArchTest".
  - Code: it returns `acorr_lm(resid**2, …)` (`:997–999`), squaring `resid` as given, with no demeaning. `acorr_lm` regresses the squares on a constant and `nlags` lags, dropping the first `nlags` rows (`:892–894`). It sets LM = (nobs − ddof)·R², where nobs is the number of rows kept, and takes the χ² upper tail with `nlags` degrees of freedom (`:905–906`). The default lag is min(10, nobs // 5) (`:888`).
  - Run on 2,000 simulated normals with `nlags=5`: `result_object=True` returned an `LMTestResult` with no warning, and the default returned a four-element tuple with a FutureWarning. A NumPy regression gave the same LM and p-value (difference 0.0).

#### NumPy 2.5 and Polars 2.0 (Stage 1 check)

- [`polynomial.hermite_e.hermegauss`](https://numpy.org/doc/2.5/reference/generated/numpy.polynomial.hermite_e.hermegauss.html), for LM24. Read 2026-10-19 after the fresh check, on the page (titled "NumPy v2.5 Manual", HTML fetched with curl) and in the venv source (NumPy 2.5.3); run in the venv.
  - `hermegauss(deg)` returns the sample points and the weights. They "will correctly integrate polynomials of degree 2*deg - 1 or less over the interval [-inf, inf] with the weight function f(x) = exp(-x^2/2)" (quoted without the page's TeX markup).
  - `deg` "must be >= 1"; deg 0 raises a ValueError. Notes: "The results have only been tested up to degree 100".
  - The weights are scaled so that they integrate 1 against exp(−x²/2), so they sum to √(2π) (`polynomial/hermite_e.py:1619`). A standard-normal expectation is therefore Σ wₖ g(xₖ)/√(2π).
  - Checked with `hermegauss(5)`: the weights sum to 2.50663 = √(2π). E Z⁴ = 3 and E Z⁸ = 105 come out to within 2e-13, but E Z¹⁰ gives 825 against 945, because degree 10 exceeds 2·5 − 1 = 9.
- [`read_csv`](https://docs.pola.rs/api/python/stable/reference/api/polars.read_csv.html), for LM26 and `data/derived/vol4_rv.csv`. Read 2026-10-19 after the fresh check, on the page (HTML fetched with curl) and in the venv source (Polars 2.0.0); run in the venv.
  - The docs' version switcher labels `stable` "2 (stable)" and names no minor version.
  - `comment_prefix: str | None = None`: "A string used to indicate the start of a comment line. Comment lines are skipped during parsing. Common examples of comment prefixes are # and //." The installed docstring is the same (`io/csv/functions.py:154–156`; `read_csv` starts at `:74`, the parameter at `:91`).
  - Run: `pl.read_csv("data/derived/vol4_rv.csv", comment_prefix="#")` gives 5,351 rows and 21 columns. Without it, Polars raises a `ComputeError` ("found more fields than defined in 'Schema'").

#### Stage 3, round 1: Python facts (2026-10-19)

- `scipy.stats.bootstrap` (SciPy 1.18.1, `stats/_resampling.py`, read 2026-10-19): default `method='BCa'` (l. 302);
  `_bca_interval` (l. 110–166) follows Efron & Tibshirani (1993) §14.3 and §15.4 by its own comment. Bias correction
  (l. 114–119): $\hat z_0=\Phi^{-1}$(share of resamples below $\hat\theta$, ties counted half). Acceleration (l. 121–156):
  $\hat a=\sum U_i^3/\big(6(\sum U_i^2)^{3/2}\big)$ over the leave-one-out jackknife values. The interval's ends are read
  off the bootstrap distribution by `stats.quantile` with its default `method='linear'` (l. 663). Resampling is iid
  for every method. Recomputed (n = 250, B = 4,999): the closed forms agree to about 1e-16. The documentation page gives
  no formula.

## Python (Volumes V and VI)

Checked 2026-10-24 for the Stage 1 briefs of batch 4 in the project environment (`.venv/Lib/site-packages`, cp313
win_amd64, as `uv.lock` pins it); file:line references are inside those installed packages. Three kinds of statement
follow, each marked: **(brief)** a fact a brief or `data/vol5_rules.py` relies on, with the check the brief names;
**(read)** the same fact read again in the installed source on 2026-10-24 for this entry; **(run)** the same fact
re-run on toy data on 2026-10-24 (random matrices, no book data, `python -I` in the project venv), so that no data
value is printed here. A fact marked only (brief) was not reproduced for this entry. Release dates and licences are
from PyPI's JSON for each version (`https://pypi.org/pypi/<name>/<version>/json`, anonymous requests, HTTP 200 for all
twelve); a release date is the upload date of the version's files.

### The packages (Volumes V and VI)

cvxpy 1.9.3 and scikit-learn 1.9.1 were approved by the owner on 2026-10-11 and added on 2026-10-24 (commit `40e1876`,
`uv add`): twelve packages in all, no existing pin changed (NumPy 2.5.3, SciPy 1.18.1 and Polars 2.0.0 stay), and
`./build.sh --data` ran every data step with exit 0 and left `src/data` and `docs` unchanged (commit message). Every
one of the twelve has in `uv.lock` a Windows wheel that installs on CPython 3.13 (cp313 `win_amd64`, or clarabel's
`cp39-abi3-win_amd64`) or a pure-Python wheel (read). The installed versions equal `uv.lock`'s (run,
`importlib.metadata`).

| Package | Version | Released | Licence (PyPI) | Role in Volumes V and VI |
|:--|:--|:--|:--|:--|
| cvxpy | 1.9.3 | 2026-09-19 | Apache-2.0 | modelling layer of the solver cross-checks in `vol5_rules.py` and of the optimization problems of LM28–LM32 and LM35; requires Python 3.11+, `osqp>=1.0.0`, `clarabel>=0.5.0`, `scs>=3.2.4.post1`, `highspy>=1.14.0`, `qdldl>=0.1.7.post0`, `sparsediffpy<0.7.0,>=0.6.0`, NumPy 2+, SciPy 1.13+ |
| scikit-learn | 1.9.1 | 2026-09-10 | BSD-3-Clause | `sklearn.covariance.LedoitWolf`, the covariance of R5 (LM30); requires `joblib>=1.4.0`, `narwhals>=2.0.1`, `threadpoolctl>=3.5.0`, NumPy 1.24.1+, SciPy 1.10+ |
| OSQP | 1.1.3 | 2026-06-12 | Apache-2.0 | cvxpy's default QP solver; the polished OSQP is the book's QP check |
| CLARABEL | 0.11.1 | 2025-06-11 | Apache-2.0 | cvxpy's default LP and cone solver; the book's main solver at set tolerances |
| SCS | 3.3.1 | 2026-09-05 | MIT | one cross-check only (LM29's problem 11) |
| HiGHS (`highspy`) | 1.15.1 | 2026-07-02 | MIT | one cross-check only (LM32's Problem 12, `cp.HIGHS`) |
| qdldl | 0.1.9.post1 | 2026-02-19 | Apache 2.0 | a cvxpy requirement; no brief names it |
| sparsediffpy | 0.6.1 | 2026-07-13 | Apache-2.0 | a cvxpy requirement; no brief names it |
| joblib | 1.6.0 | 2026-08-31 | BSD-3-Clause | requirement of scikit-learn and OSQP |
| threadpoolctl | 3.7.0 | 2026-09-15 | BSD-3-Clause | requirement of scikit-learn |
| cloudpickle | 3.1.2 | 2025-11-03 | BSD-3-Clause | requirement of joblib (`cloudpickle>=3.0`) |
| setuptools | 84.2.1 | 2026-10-20 | MIT | requirement of OSQP |

- Solvers installed beside cvxpy: `cvxpy.installed_solvers()` returns CLARABEL, SCS, SCIPY, HIGHS and OSQP (run); no
  commercial solver. cvxpy tries a commercial solver first when one is installed (`cvxpy/settings.py:121-123`,
  `DEFAULT_TO_COMMERCIAL_SOLVERS`; `reductions/solvers/defines.py:115-117` lists MOSEK, GUROBI, CPLEX, COPT, XPRESS, NAG
  and KNITRO; `problems/problem_form.py:356-360`), so on a machine that has one the default solver differs. The
  book's scripts therefore name their solver in every call (shared decision "Solver output").
- Python 3.13 is the project's minor version (`pyproject.toml`); scikit-learn 1.9.1 and cvxpy 1.9.3 require 3.11 or
  later (PyPI).

### cvxpy 1.9.3

- **What cvxpy does with a problem** (LM29 §8 and its open item 2; read by the second source hunt on 2026-10-24 in
  arXiv:1709.04494v2, the version of Agrawal, Verschueren, Diamond and Boyd (2018) that it read in full; page numbers
  are that version's). The abstract (p. 1) describes an analysis phase that finds a suitable solver and a
  canonicalization phase "in which we rewrite the problem in the selected solver's standard form", implemented "in
  version 1.0 of CVXPY"; §1.3 (pp. 4–5) and §4 (p. 15) say the same of CVXPY's solve method. The paper describes
  CVXPY 1.0, so the solver names, defaults and routes of 1.9.3 below rest on the installed source and runs (A29-22),
  not on it. Its bibliographic entry is under Papers (LM29).
- **Default solver by problem class** (brief: LM29's A29-22, by `Problem.solver_stats.solver_name` with no solver given;
  recomputed independently, 34 of 34 anchors reproduced; read; run). A linear program goes to CLARABEL, a quadratic
  program to OSQP, a semidefinite program to SCS, and everything else (second-order cone, exponential cone) to CLARABEL
  (`problems/problem_form.py:373-387`, after the commercial-solver step above). The brief's four cases: R3's QP OSQP, a
  volatility limit (SOCP) CLARABEL, the cost-penalized QP OSQP, an LP CLARABEL. Run on three toy problems: LP CLARABEL,
  QP OSQP, SOCP CLARABEL; `solver=cp.HIGHS` solved a toy LP with `solver_name` HIGHS.
- **OSQP defaults as cvxpy sets them** (brief: A29-22, parsed from the installed `osqp_qpif.py`; read). `eps_abs` and
  `eps_rel` 1e-5 and `max_iter` 10,000, in place of OSQP's own 1e-3 and 4,000 (comment and code,
  `reductions/solvers/qp_solvers/osqp_qpif.py:111-114`); polishing is on for a fresh solve (`:147-148`) and, on a warm
  re-solve, only when the matrices changed (`:142-143`). Options pass straight to `OSQP.setup` (`:150-151`); the book's
  `OSQP_OPTS` (`data/vol5_rules.py:64`) is `eps_abs` = `eps_rel` = 1e-10, `max_iter` 400,000, `polishing` True.
- **CLARABEL settings** (brief: A29-22, `clarabel.DefaultSettings()`; run). The installed 0.11.1 defaults are
  `tol_gap_abs` = `tol_gap_rel` = `tol_feas` = `tol_infeas_abs` = `tol_infeas_rel` = 1e-8 and `max_iter` = 200. cvxpy
  sets each keyword as an attribute of the settings object and raises `TypeError` ("unrecognized solver setting") for
  a name CLARABEL does not know (`reductions/solvers/conic_solvers/clarabel_conif.py:183-189`, read). The book's
  `CLARABEL_OPTS` (`vol5_rules.py:65`) is 1e-12 for the three tolerances; `ERC_OPTS` (`:70`) is 1e-10.
- **Why 1e-10 for cone programs** (brief: shared decision "Solver output" and `vol5_rules.py:70-71`, the editor's runs
  on the book's matrices, not re-run for this entry): at 1e-12 CLARABEL stops at `optimal_inaccurate` for the
  log-barrier (exponential-cone) form of R6 and for LM29's problem 11 (a second-order cone program, A29-31). Run on toy
  data: thirty random 5×5 problems of the log-barrier form returned `optimal_inaccurate` four times at 1e-12 and
  `optimal` thirty times at 1e-10, the same direction; the rate depends on the matrix, so the book's choice rests on
  its own runs.
- **SCS** (brief: LM29's problem 11 passes `{"eps": 1e-9, "max_iters": 200000}`, `SCS_OPTS` in
  `data/vol5_anchors_lm29.py`; read).
  With SCS 3 or later cvxpy turns `eps` into `eps_abs` and `eps_rel` (`conic_solvers/scs_conif.py:206-209`) and, when
  neither is given, defaults both to 1e-5 (`:210-212`).
- **Statuses** (brief: A29-18; run on a toy). A 15% cap on five funds gave `infeasible` (objective `inf`, variable value
  `None`); maximizing a mean under the budget alone gave `unbounded` (objective `inf`); a lower bound on a quadratic
  form (`quad_form(...) >= c`) raised `DCPError` at `solve()` (the `Problem` builds, and `is_dcp()` is False).
  `optimal_inaccurate` is a status to be reported, not a pass (shared decision).
- **Dual signs** (brief: LM28's E9, A28-33, and LM29's A29-26, both run on the book's first and last windows with the
  duals printed as cvxpy reports them; run). For `minimize w'Sw` subject to `1'w = 1` the equality's `dual_value` is the
  negative of the multiplier λ = 2w'Sw in LM7's convention, and for `w >= b` the inequality dual is ν ≥ 0 with
  stationarity 2Sw + (equality dual)·1 − ν = 0 (a toy two-asset problem, residual below 1e-13 with CLARABEL at 1e-12).
  cvxpy's own page (`https://www.cvxpy.org/tutorial/advanced/`, HTTP 200, "Advanced Features", the site's latest
  documentation, not pinned to 1.9.3) says each constraint's `dual_value` holds its optimal dual variable (Lagrange
  multiplier) and shows an inequality dual of 2: by complementarity the constraint is active (x − y = 1), and the
  non-zero dual means that tightening it raises the optimal value; it prints no sign convention for equalities. So
  the text reports the installed behaviour and tells the reader to check the sign against a closed form (LM28's
  decision), as the brief says.
- **`psd_wrap`** (read; no brief states a check). `psd_wrap(P)` asserts that a square matrix is PSD and does not test it
  (`atoms/affine/wraps.py:83-96`, `is_psd` returns True); `quad_form(x, P, assume_PSD=True)` wraps `P` with it
  (`atoms/quad_form.py:290-314`). Every `quad_form` of the rules passes a covariance that the script has made positive
  definite or has built as one, so the assertion is the script's, not cvxpy's.
- **The rules' cross-check constants** (brief: `data/vol5_rules.py:66-72` and the editor's runs, not re-run here):
  polished OSQP must equal the exact non-negative-least-squares solution to `OSQP_TOL` = 1e-9 per weight and
  CLARABEL's objective to `CLARABEL_GAP` = 1e-9 relative; R6 against cvxpy's log form to `ERC_CHECK_TOL` = 1e-5; the
  comments record that at 1e-10 tolerances CLARABEL's objective gap reached 1.2e-8 on U28 and at 1e-12 stayed below
  1.5e-10.

### scikit-learn 1.9.1

- **`LedoitWolf(assume_centered=False)`** (brief: LM30, "installed source read 2026-10-24"; the formula of
  `ledoit_wolf_shrinkage` matches (30.3) term by term and the hand computation agrees to rounding error (below 1e-15), A30-13, reproduced
  independently in its first version and revised since; read; run). `fit` subtracts the column means
  (`covariance/_shrunk_covariance.py:603-606`) and calls `_ledoit_wolf(..., assume_centered=True)` (`:607-609`),
  whose empirical covariance divides by the number of rows (`_empirical_covariance.py:104-105`): the divisor is T.
  The result is (1 − shrinkage)·S + shrinkage·μ·I with μ = tr(S)/N (`_shrunk_covariance.py:38-41`; docstring
  `:538-542`), so the only target is a scaled identity.
  `shrinkage_` is the target's weight (docstring `:506-508`, set at `:610`): it is 1 − ĉ in the book's (30.1) and
  (30.3). `block_size` "is purely a memory optimization and does not affect results" (`:489-492`). The class docstring
  cites Ledoit and Wolf, *Journal of Multivariate Analysis* 88(2): 365–411 (February 2004), as the source of the formula
  (`:470-474`, `:546-548`).
- **The shrinkage formula, term by term** (read; re-derived for this entry). In `ledoit_wolf_shrinkage` (`:297-400`),
  `delta_` is the sum of the squared entries of S (`:367-385`, divided by T² at `:385`), `beta_` the sum of the
  entries of X²′X² (`:366-388`), `delta = (delta_ − 2μ·tr(S) + N·μ²)/N`, which is `‖S − μI‖_F²/N` (`:392-393`), and
  `beta = (beta_/T − delta_)/(N·T)` (`:390`), which is the book's noise estimate
  `T⁻² Σ_t ‖x_t x_t′ − S‖_F²` divided by N; then `beta = min(beta, delta)` and `shrinkage = beta/delta`
  (`:394-399`). Both terms carry the same factor 1/N, so the ratio is the book's
  `min(σ̂², ‖S − μI‖_F²) / ‖S − μI‖_F²`. Run on 120×5 toy data (divisor-T covariance): `shrinkage_` equals
  the book's form to 7e-17 and `covariance_` equals (1 − s)·S + s·μ·I to 4e-16; multiplying the data by √243 changed
  `shrinkage_` by 8e-17 (scale-free; A30-13 finds daily and annual units equal to rounding error, below 1e-15, on E5's first window).
- **`OAS`** (brief: LM30, "its source comment, read in the installed 1.9.1"; read; run). `_oas`
  (`_shrunk_covariance.py:46-94`) computes min((tr(S²) + tr(S)²)/((n + 1)(tr(S²) − tr(S)²/p)), 1) and the comment says
  "The factor 2 / p is omitted since it does not impact the value of the estimator for large p" and cites Eq. 23 of
  Chen, Wiesel, Eldar and Hero (2010) (`:66-71`). Run on the toy data: `OAS().shrinkage_` equals that formula without
  the 2/p factor to 4e-17. The paper's own Eq. 23 was not read here (its bibliographic entry is under Papers).

### SciPy 1.18.1 (what `vol5_rules.py` and LM31 rely on)

- **`scipy.optimize.nnls`** (brief: LM29, docstring "read in the project environment"; read). The docstring calls the
  code "the classical algorithm of [1]", an active-set method that "solves the KKT (Karush-Kuhn-Tucker) conditions for
  the non-negative least squares problem", citing Lawson and Hanson, *Solving Least Squares Problems*, SIAM, 1995,
  doi 10.1137/1.9781611971217 (`optimize/_nnls.py:38-46`); `maxiter` defaults to 3·n (`:86-87`), and the rules pass
  `maxiter=1000` (`vol5_rules.py:96`).
- **`scipy.cluster.hierarchy.linkage`** (brief: LM31, docs v1.18.0 read and the installed 1.18.1 run on 2026-10-24;
  read; run). A 1-D `y` is a condensed distance matrix and a 2-D `y` an array of observation vectors
  (`cluster/hierarchy/_hierarchy_impl.py:727-731`); a square, symmetric, non-negative, hollow 2-D input is read as
  observations and raises `ClusterWarning` ("looks suspiciously like an uncondensed distance matrix", `:934-944`);
  `method="single"` is the nearest-point rule (`:773-780`) computed from a minimum spanning tree (`:960-961`).
- **`scipy.spatial.distance.squareform`** (brief: shared decision "Python" and LM31 §8; read; run). With `checks=True`
  it calls `is_valid_dm(X, throw=True)` at tolerance 0 (`spatial/distance.py:2283-2284`), which requires exact symmetry
  and an exactly zero diagonal (`:2399-2409`). Run on 200 toy correlation matrices (5 to 28 variables): `np.corrcoef`
  was asymmetric in all 200; `squareform` rejected the raw distance matrix in 199, the symmetrized one in 190, and the
  symmetrized one with its diagonal set to 0 in none. The shared decision's "191 of 200" is the fresh check's own draws.

### Not checked here

- cvxpy's "Solver Features" page, quoted by the survey: not relied on.
- The OSQP and Clarabel papers are cited for the solvers' names only, and Diamond and Boyd (2016) at its abstract
  (LM29's entries under Papers).

## Taiwan facts (Volume III)

- TAIEX total-return index (發行量加權股價報酬指數), read 2026-10-18. Dividend rule verified: TWSE
  [IndexS02.pdf](https://www.twse.com.tw/downloads/zh/products/indices/IndexS02.pdf) (2023.04 修訂), §四(一)2 and
  §五(六): the 報酬指數 is adjusted for cash dividends, and on an ex-dividend date only its base changes, 當日基值 =
  前一日基值 × [(前一日收盤後調整之總發行市值 − 當日發放現金股利總值) / 前一日收盤總發行市值]; Taiwan Index Plus's English
  methodology ([The TAIEX Methodology](https://backend.taiwanindex.com.tw/api/downloadFile/IndexFiles/992/en), amended
  April 2023) says the TR index "reflect[s] the return including reinvesting the cash dividend". Base date from Taiwan
  Index Plus (TWSE's wholly owned subsidiary), [IR0001](https://taiwanindex.com.tw/indexes/IR0001) (also
  [EN](https://taiwanindex.com.tw/en/indexes/IR0001) and the list page): 基期 2002.12.31, 發布日 2003.01.02, 基期指數 100.
  Start level: TWSE's own series (`rwd/zh/TAIEX/MFI94U`) starts on 2003-01-02 at 4,524.92 and rejects queries before
  92年1月; TAIEX closed at 4,452.45 on 2002-12-31 and 4,524.87 on 2003-01-02 (`MI_5MINS_HIST`). So the published level
  starts from TAIEX's level at the base date, not from 100: an inference from the data, since IndexS02 does not print
  the base value; say "set equal to TAIEX on 2002-12-31" or give the base date only. Launch date not found: no TWSE
  notice of first publication was found, 發布日 2003.01.02 is the first value date, TWSE's `MI_INDEX` (type IND) shows a
  報酬指數 table on 2009-01-05 (5,862.14) but returns empty tables for 2005–2008, and the
  [index-series page](https://www.twse.com.tw/zh/indices/indices/series.html) has no separate row for it. (IndexS02
  §四(五): TAIEX's own base is the 1966 annual average = 100, published 1970-11; Taiwan Index Plus gives launch
  1970.11.02.)
- Daily price limit 7% → 10% on 2015-06-01: verified again on 2026-10-18 on the two TWSE pages listed under "Taiwan
  exchanges, regulators and official pages" ([company history](https://www.twse.com.tw/en/about/company/history.html):
  "Jun 1: The daily price fluctuation limit is raised from 7% to 10%."; 60th-anniversary book
  [p. 181](https://www.twse.com.tw/staticFiles/product/publication/twse60/html/181/): "104 年 6 月 1 日起，我國市場之漲跌幅度由
  7% 放寬為 10%"). The formal notice itself was not looked up.

## Taiwan facts (Volume IV)

- TWSE [company history (zh)](https://www.twse.com.tw/zh/about/company/history.html), read 2026-10-19: "108年 01.01 施行週末補行上班日，證券市場不交易亦不交割". The [English page](https://www.twse.com.tw/en/about/company/history.html) says: "2019 Jan 1 The TWSE forgoes Saturday trading and settlement, even with the presence of work."
- TWSE [市場開休市日期](https://www.twse.com.tw/zh/trading/holiday.html), read through its JSON (`rwd/zh/holidaySchedule`):
  - 2024: "於2月17日（星期六）補行上班，但不交易亦不交割";
  - 2025: the same wording for 2月8日;
  - 2018–2020 return no rows.
- Inference, not stated on either page: before 2019 the market traded on Saturday make-up workdays, which would explain TR23's 23 Saturday sessions (2006–2018).
- Not checked: whether those 23 dates match the government's make-up workdays.
- TAIFEX: no official page was found; only news covers it.

## Taiwan facts (Volumes V and VI)

- **Art. 8's amendment history** (TWSE regulation database, history page `DAT01`, 2026-10-24 and, by this entry's
  verifier, 2026-10-25; full text of the versions of 2024-12-31, 2024-02-23 and 2016-06-03 compared for this entry).
  The page numbers 41 entries: the issuance of 1987-12-18 and 40 amendment entries (42 amendments, as entries 27
  and 35, of 2017-02-08 and 2021-10-08, each hold two notices). Each names the articles it changes, except 1993-05-01
  (修正發布, no articles named) and two full-text revisions, 2003-05-16 (名稱及全文 14 條) and 2016-03-08
  (臺證交字第1050002539號, 修正全文24條), which restate every article, Art. 8 included. From 2009 on, Art. 8 is
  named in: 2009-06-09 (the list 2, 3, 5–9, 11–13), 2011-01-12 (8, 9), 2014-07-04 (the list 2, 3, 4-1, 6–8, 11–13),
  2014-09-10 (2, 3, 4-1, 7, 8, 11, 12), 2016-06-03 (2–4, 8, 17) and 2024-12-31 (2, the range 3–10-1, 11–15, 19, 20,
  plus the new 2-1); no amendment between those two dates names it.
  The text of Art. 8 differs between 2024-02-23 and 2024-12-31 in item (4), added, and in the wording of item (1)
  ("加掛 ETF 受益憑證" became "加掛指數股票型基金受益憑證"); the 2016-06-03 and 2024-02-23 texts are the same. The
  only amendment after 2024-12-31 is 2025-09-30 (Arts. 14, 5-1, 5-2). The pages' footer "資料最新修訂日期" is a date
  the database updates daily (115.10.23 on 2026-10-24, 115.10.24 on 2026-10-25).
- **Fund by fund, which market's rule applies** (the shared decision "Limits and locks" and LM35's brief state the
  application; this entry adds what the pages read show). On TWSE, Art. 8: TWSE's classification is 台股ETF for 0050
  and 0056 (10% limit), 國外股票ETF for 00646 and 00662 (item 1, no limit), 期貨ETF for 00635U and 00642U (item 2, no
  limit; their Yuanta pages give a COMEX gold and a NYMEX WTI futures index) and 股票槓反ETF for 00631L (¶2, 10% times
  2). On TPEx, the ETF rules' Art. 7 ¶1 item 一: 00679B and 00720B are TPEx-listed (TPEx's ETF list and quotes, TWSE's
  ISIN page; neither is in TWSE's `STOCK_DAY_ALL`), TPEx classes both 被動式國外債券及固定收益ETF, and Art. 2-1 ¶1
  item 二(二) counts an index of bonds with at least one foreign bond as foreign-constituent, so neither has a limit;
  the 成分證券 text has stood since 2017-03-01, and TPEx's listing notices (00679B 2017-01-13, 00720B 2018-01-25) and
  product pages print 無漲跌幅度限制. TPEx's quotes carry the no-limit placeholders 9999.95 and 0.01 for both, and
  00720B closed −11.25% on 2020-03-19 (repository data, no ex-date that day), beyond any 10% limit. That the 0056
  index holds only domestic stocks is not stated on the Yuanta page read.
- **Short names of LM35's checkpoint funds** (LM35 prints them; `plans/vol-5.md`, "Decisions on the third
  revision"). 0056 元大高股息 and 00662 富邦NASDAQ: TWSE's e添富 fund pages (證券簡稱) and TWSE's ISIN page for
  上市 securities; Fubon's fund table also prints 證券簡稱 富邦NASDAQ. 00720B 元大投資級公司債, TPEx's short name:
  TPEx's product page (ETF簡稱) and ETF list (`stockName`), and TWSE's ISIN page for 上櫃 securities. Read
  2026-10-25, Fubon's table 2026-10-24 (the e添富, product-page, listing-markets and Fubon rows above).
- **Cost model** (shared decision "Cost model"; official sources read 2026-10-24, the TPEx ones 2026-10-25).
  Commission: TWSE's Operating Rules Art. 94 for the TWSE-listed funds and, for the TPEx-listed 00679B and 00720B,
  TPEx's Business Rules Art. 64, applied to ETFs by TPEx's ETF rules, Art. 15 ¶1 (¶1–¶3 unchanged since 2008-02-12;
  the article last amended 2011-12-16, in ¶4 and ¶5 only): each imposes a notice duty above 1.425‰, so 0.1425% is a
  posted reference on both exchanges and brokers' discounts are not modelled. Tax on sales: 0.1% for ETFs under
  Securities Transaction Tax Act Art. 2 item 2, 千分之一 on other securities approved by the government (Art. 2 last
  amended 1993-01-30; the Act last amended 2025-01-02, Arts. 2-2 and 12 only); Art. 2-1 ¶2 (last amended 2016-12-30)
  suspends it from 2017-01-01 to 2026-12-31 for the listed and OTC-listed (上市及上櫃) bond ETFs of securities investment
  trust enterprises, leveraged and inverse ones excluded: 00679B was exempt throughout E5's span and 00720B from its
  listing on 2018-02-01. The futures ETFs 00635U and 00642U pay the same 0.1%, as the Ministry of Finance's ruling
  97/08/11 台財稅字第09700161260號函 states directly of futures-trust fund certificates:
  「受益憑證之轉讓，應依證券交易稅條例第2條第2款規定，按每次交易成交價格1‰課徵證券交易稅。」 TWSE's ETF rules page (0.1% on
  every ETF sale, bond ETFs exempt to 2026) and 財政統計通報 No. 21 (the ETF rate 千分之1, and tax collected on 原型期貨
  ETFs) support it; for the two TPEx funds, TPEx's product pages give 「證券交易稅：依證券交易稅條例第2條之1規定」. The
  source check's own arithmetic, not the notice's statement: 0.3% of NT$7.4 trillion at 0.1% is about 0.22億 (NT$22
  million), against the table's 0.2億 for 原型期貨, which fits 0.1%.
- **LM34's six survivorship funds** (§5, open item O12; read by the second source hunt on 2026-10-24 in the rows
  above). All six are futures-trust ETFs on futures indices, and three of them are daily leveraged or inverse, so part
  of their decay is daily compounding and the survivorship gap mixes product types. 00635U (期貨ETF; S&P GSCI Gold
  Excess Return Index, COMEX gold; listed 2015-04-15) and 00642U (期貨ETF; S&P GSCI Crude Oil Enhanced Excess Return,
  NYMEX WTI; listed 2015-09-07): Yuanta's and TWSE's pages. 00672L (S&P GSCI crude oil ER, daily +2×; the index's
  title is not printed in the documents read; a WTI-futures fund that held the December 2020 contract instead of the
  index's near-month one until 2020-07-08; last trade 2020-11-12, delisted from 2020-11-13): TWSE's announcements and
  Yuanta's prospectus. 00673R (期貨槓反ETF; S&P GSCI Crude Oil 1x Inverse Index ER, NYMEX WTI) and 00674R (期貨槓反ETF;
  S&P GSCI Gold 1x Inverse Index ER, COMEX gold), both listed 2016-10-07: Yuanta's and TWSE's pages. 00677U (Fubon;
  標普500波動率短期期貨ER指數, S&P 500 VIX Short-term Futures Index Excess Return, near- and next-month VIX futures
  rolled daily by the index; last trade 2021-06-02, delisted from 2021-06-03): Fubon's releases and TWSE's
  announcement. All six are TWSE-listed (TWSE's ISIN page and announcements), so their cost and limit rules are
  TWSE's. The two delisting dates match A34-19's last trades. "Unsuitable for long holding" is the issuers' wording,
  for four funds (Yuanta's prospectus for 00672L, 00673R and 00674R; Fubon for 00677U), and in none of the other
  documents read: not on TWSE's pages read, and the 00635U and 00642U prospectuses were not read. TWSE's overview page
  says only that the roll may produce losses (可能產生).
- **Timing of E5's foreign funds** (LM27 §4). 0050, 00646, 00635U and 00642U trade on TWSE and 00679B on TPEx, both
  matching from 09:00 to 13:30: TWSE's Operating Rules Art. 3 for TWSE, and for TPEx its Business Rules Art. 40 item
  一, applied to ETFs by its ETF rules' Art. 4 ¶2; on TPEx a closing call auction runs from 13:25 and a delayed close
  can move to 13:33 (TPEx's 交易系統簡介 page), as TWSE's closing call runs from 13:25 (the "TWSE trading system" row).
  TWSE's ETF overview page warns that, when Taiwan has closed, an event abroad reaches a foreign-constituent or offshore
  ETF late and that a futures-trust ETF on a foreign futures index is valued on Europe and US futures. The NYSE core
  session ends 4:00 p.m. ET. The offsets are not on the NYSE page: from the IANA time-zone data (Python `zoneinfo`,
  tzdata 2026.5, run 2026-10-24) Taipei is UTC+8 with no daylight saving and 16:00 in New York is 04:00 in Taipei in
  US summer time and 05:00 otherwise (checked for dates in 2008, 2025 and 2026). On the page's early-close days (1:00
  p.m. ET) the session ends at 01:00 or 02:00 Taipei time.
- **Not read, so not asserted:** TWSE's rule in force before 2016-06-03, so the replays of 2008 and 2015 keep "under each
  market's current rules" (the source check's advice, with each fund's own market by the "Listing markets" decision); DBO's roll rule (Invesco's page states none beyond the name "Optimum
  Yield", and its fact sheet was not obtained); the index title of 00672L; the 證券交易稅條例實施注意事項 that the Ministry's ruling
  cites. For TPEx: no official reason for the 2017 change of Art. 7's 成分股 to 成分證券 was found (selaw's 附件下載 lists five
  undated files: a 修正總說明 and a 修正條文對照表 whose titles name 主動式交易所交易基金, which the rules' name took on 2024-12-31, so
  neither is 2017's, and three forms; the 2017 notice's attachments returned nothing); TPEx's suspension records before
  2026 (its `tpex_spendi_history` holds 2026 only and lists neither bond fund). For TWSE: its suspension records under
  Arts. 5-1 and 5-2 (the rule itself is in the Art. 8 row). The 2008 TWSE trading rules and tax rates behind the 0050
  replay are not in this entry (Art. 2's text has stood since 1993-01-30).

## Chinese terms (Volume III)

- 樂詞網, [terms.naer.edu.tw](https://terms.naer.edu.tw/) (國家教育研究院), searched 2026-10-18 for Volume III's list
  (`plans/vol-3.md`, "Chinese terms"): 108 English terms (46 on the brief's list, 38 further terms, 24 printed terms and
  their neighbours), 245 query strings, each run three times (all listings, 統計學名詞 only, 數學名詞 only), 735 result
  pages. Search field 中英文名詞, 模糊檢索, 100 rows a page:
  `https://terms.naer.edu.tw/search/?query_term=<q>&query_field=title&query_op=&match_type=phrase&page_size=100`,
  plus `&filter_bool=and&filter_term=%27%E7%B5%B1%E8%A8%88%E5%AD%B8%E5%90%8D%E8%A9%9E%27&filter_field=subcategory_1.raw&filter_op=term&tabaction=browse`
  for statistics (`filter_term=%27%E6%95%B8%E5%AD%B8%E5%90%8D%E8%A9%9E%27` for mathematics); the empty `query_op=` is
  required, or a filtered search ignores the query and browses the whole listing. Found later (2026-10-18, LM18's
  revision): 蒙地卡羅估計量 (Monte Carlo estimator, 數學名詞; a re-run of the search lists it there, not in 統計學名詞).
  Pseudo-random number generator: 擬隨機數產生器 (電子工程名詞); the statistics and mathematics listings have only
  隨機數產生器 (random number generator, 統計學名詞) and 擬隨機數 (pseudo-random number, 數學名詞) (re-checked
  2026-10-18, LM18's closing check). Random number: 隨機數；亂數, in that order (數學名詞 and 數學名詞-兩岸數學名詞,
  same date); Volume III prints 隨機數, and LM12 keeps the 亂數 it printed (lm12.md:527). Entry pages (`/detail/<hash>/`)
  depend on the search session and are not cited. 分布 and 分配: the statistics listing writes 分布 in every Volume III
  compound (常態分布, 二項分布, 聯合分布, 條件分布, 累積分布函數, 依分布收斂, 經驗分布函數) and its bare
  distribution and distribution function entries give 分布 first, 分配 second; the mathematics listing pairs "分布；分配" in most compounds but has 分布
  alone for distribution function, conditional distribution and convergence in distribution; 條件分配 and 分配收斂
  appear only in the economics and psychology listings; 高中以下數學名詞 lists both forms. LM5 printed 分配 three times
  (累積分配函數, 常態分配函數, 常態分配; 累積分配函數 and 常態分配 are listed mathematics forms); Stage 4 (2026-10-18)
  changed them to 累積分布函數, 常態分布函數 and 常態分布, so the book has one form. Quantile-quantile (Q-Q) plot:
  分位數-分位數點圖 (統計學名詞; found by the queries `QQ plot`, `Q-Q plot` and `Q-Q`, rechecked 2026-10-18). Independent
  identically distributed (iid): 獨立同分布[的] (數學名詞); 統計學名詞 has only the noun phrase 獨立且相同分布隨機變數.
  Gambler's fallacy: 賭者謬誤 (統計學名詞, query `fallacy`). Log–log plot: 雙對數圖 (統計學名詞, listed as "double
  logarithmic chart", beside 雙對數尺度 for "double logarithmic scale"; queries `雙對數` and `double logarithmic`,
  2026-10-18, LM15's closing check); the query `log-log` shows only 雙對數坐標圖 (電機工程名詞) for "log-log plot" and
  雙對數圖尺；雙對數尺度 (數學名詞) for "log-log scale". LM15 prints 雙對數圖. Not in 樂詞網, composed from listed parts:
  檢察官謬誤, 標準化動差, 全變異數法則, 條件相關係數, 超越相關係數, 放回重抽樣; the law of the unconscious statistician has
  no entry and keeps its English name; the printed 尾部指數 and 超額峰態 are not in 樂詞網 either.

## Chinese terms (Volume IV)

- 樂詞網, [terms.naer.edu.tw](https://terms.naer.edu.tw/) (國家教育研究院), searched 2026-10-19 for Volume IV's list
  (`plans/vol-4.md`, "Chinese terms") with the URL pattern of the Volume III entry: 75 query strings for LM19–LM22 and
  67 for LM23–LM26, each run in all listings, in 統計學名詞 and in 數學名詞 (426 result pages). Python's ssl rejected
  the site's certificate ("Missing Subject Key Identifier"), so the pages were fetched with curl. Entry pages are not
  cited. "—" means the listing has no entry for that English form; "not recorded" means the survey did not report that
  listing.
- Decided (plans/vol-4.md): **波動率** for volatility (統計學名詞 gives 波動；波動率 and lists "volatility index (VIX)"
  as 波動率指數; the plan also cites TAIFEX's 臺指選擇權波動率指數, whose page is not yet in this file); the five printed
  波動度 (lm05.md:191, lm07.md:354, lm07.md:512, lm10.md:228, lm10.md:449) become 波動率 at Stage 4. **時間序列** for
  time series (數學名詞; 統計學名詞 writes 時間數列).
- Already printed and consistent: 標準誤 (lm18.md:566) and 自助重抽法 (lm18.md:573), both 統計學名詞 forms.

| English | 統計學名詞 | 數學名詞 | Book |
|:--|:--|:--|:--|
| descriptive statistics | 敘述統計量；描述統計量；敘述統計（學）；描述統計（學） | 敘述統計[學] | 敘述統計 |
| sample variance | 樣本變異數 | 樣本變異數 | 樣本變異數 |
| estimator | 估計量；估計式 | 估計量；估計式 | 估計量 |
| unbiased estimator | 不偏估計量 | — | 不偏估計量 |
| bias | 偏誤；偏差 | — (compounds only, e.g. 不偏性) | 偏誤 |
| mean squared error | 均方誤差 ("mean squared error (MSE)" and "mean square error (MSE)") | 均方誤差 ("mean square error (MSE)") | 均方誤差 |
| consistent estimator | 一致估計量 (consistency 一致性) | — (consistency 相容性；一致性；無矛盾性) | 一致估計量 |
| standard error | 標準誤 | 標準誤[差] | 標準誤 |
| sampling distribution | 抽樣分布 | — | 抽樣分布 |
| confidence interval | 信賴區間 | 信賴區間 | 信賴區間 |
| likelihood function | 概度函數 | 概度函數 | 概度函數 |
| maximum likelihood estimation | 最大概度估計 (estimator 最大概度估計量) | estimate 最大概度估計; method 最大概度法 | 最大概度估計 |
| Fisher information | 費雪訊息 (matrix 費雪訊息矩陣) | — | 費雪訊息 |
| Cramér–Rao lower bound | 克萊姆-饒歐下界 (inequality 克萊姆-饒歐不等式; information inequality 訊息不等式) | — | 克萊姆-饒歐下界 |
| Hill estimator | 希爾估計量 | — | 希爾估計量 |
| tail index | — | — | none (Volume III printed 尾部指數, not in 樂詞網) |
| hypothesis testing | 假設檢定 | 假設檢定 | 假設檢定 |
| null hypothesis | 虛無假設 | 虛無假設 | 虛無假設 |
| alternative hypothesis | 對立假設 | 備擇假設；對立假設 | 對立假設 |
| significance level | 顯著水準 (also "level of significance") | 顯著水準; "level of significance" 顯著性水準 | 顯著水準 |
| p-value | p值(顯著機率值) | — | p值 |
| power | 檢定力；檢力；乘冪; "power of a test" 檢定力；檢力 | "power of test" 檢定力 | 檢定力 |
| type I error | 第一型誤差；第一型錯誤 | "error of the first kind" 第一類誤差 | 第一型錯誤 |
| type II error | 第二型誤差；第二型錯誤 | 第二類誤差 | 第二型錯誤 |
| multiple testing | no entry for "multiple testing" or "multiple test"; multiple comparisons 多重比較; multiple hypothesis test 多重假設檢定 | — | 多重假設檢定 (multiple testing) |
| family-wise error rate | familywise error rate 族系誤差率 (experimentwise error rate 實驗誤差率) | — | 族系誤差率 |
| false discovery rate | 偽發現率 | — | 偽發現率 |
| Bonferroni correction, inequality | Bonferroni校正, Bonferroni不等式 | — | Bonferroni 校正 |
| data snooping | 資料偵伺 | — | 資料偵伺 |
| resampling | 重抽樣 | 再抽樣 | 重抽樣 |
| bootstrap | 自助重抽法；靴拔重抽法 | not recorded | 自助重抽法 |
| block bootstrap | not listed in any listing (block: 集區；區塊) | — | 區塊自助重抽法 (book's own) |
| stationary bootstrap | not listed (stationary time series 平穩時間數列; stationary process 平穩過程) | stationary 平穩；定常 | 平穩自助重抽法 (book's own) |
| percentile interval | "percentile interval" and "percentile method" not listed; percentile confidence interval 百分位數信賴區間; BCa 偏誤加速校正之自助重抽信賴區間 | — | 百分位數信賴區間 |
| variance ratio | 變異數比 (test 變異數比檢定) | variance-ratio transformation 變異數比變換 | 變異數比 |
| autocorrelation | 自我相關; serial correlation 序列相關 | compounds only, with 自相關; serial correlation 序列相關 | 自我相關 |
| ACF, PACF | 自我相關函數, 偏自我相關函數 | 自相關函數, — | 自我相關函數, 偏自我相關函數 |
| regression | 迴歸 | 迴歸 | 迴歸 |
| least squares | method of least squares 最小平方法 (bare term not listed) | 最小平方法; 最小平方估計 | — |
| ordinary least squares | ordinary least squares (OLS) method 普通最小平方法 | — | 普通最小平方法 |
| residual | 殘差 | 剩餘；殘差 | 殘差 |
| coefficient of determination | 判定係數；決定係數 | 決定係數 | 判定係數 |
| Gauss–Markov theorem | 高斯-馬可夫定理 | not recorded | 高斯-馬可夫定理 |
| best linear unbiased estimator | 最佳線性不偏估計量 | not recorded | 最佳線性不偏估計量 |
| heteroscedasticity | 變異數非齊一性 (same entry for the -sk- spelling) | 異方差性；不等變異性 | 變異數非齊一性 |
| robust standard error | 穩健標準誤 | not recorded | 穩健標準誤 |
| HAC estimator | 變異數非齊一與自我相關一致估計量 | — | 變異數非齊一與自我相關一致估計量 (HAC) |
| Bayesian inference | 貝氏推論 | — | 貝氏推論 |
| prior distribution | 事前分布 | 事前分布；事前分配 | 事前分布 |
| posterior distribution | "posterior distributions" 事後分布 | none (兩岸數學名詞 has 事後分布；事後分配) | 事後分布 |
| conjugate prior | 共軛事前分布 | — | 共軛事前分布 |
| shrinkage estimator | 收縮估計量; James-Stein估計量 | — | 收縮估計量 |
| empirical Bayes estimator | 經驗貝氏估計量 | empirical Bayes method 經驗Bayes法 | 經驗貝氏估計量 |
| precision | 精確度 | 精確；精[密]度 | 精確度 (LM24) |
| stationary | bare term none; stationarity 平穩性；定態性; 平穩過程; 平穩時間數列; 共變異數平穩過程；共變異數定態過程 | 平穩；定常; 平穩過程; 平穩時間序列 | 平穩 |
| white noise | 白雜訊；白噪音 | 白噪音 | 白噪音 |
| random walk | 隨機漫步 | 隨機漫步 | 隨機漫步 |
| autoregressive model | autoregressive (AR) model 自我迴歸模型; 自我迴歸過程 | 自迴歸 compounds | 自我迴歸模型 |
| moving average model | moving average (MA) 移動平均; MA model 移動平均模型; MA process 移動平均數過程 | 移動平均數 | 移動平均模型 |
| ARMA | 自我迴歸移動平均模型; 自我迴歸移動平均過程 | — | 自我迴歸移動平均模型 |
| unit root | bare term none (經濟學名詞 has 單根); unit root test 單根檢定 | — | 單根, 單根檢定 |
| Dickey–Fuller test, augmented | Dickey-Fuller檢定; 增廣Dickey-Fuller檢定 | not recorded | 增廣 Dickey-Fuller 檢定 |
| Box–Pierce test | 柏克斯-皮爾斯檢定 | not recorded | — |
| portmanteau test | 便利的檢定 | not recorded | — |
| Ljung–Box test | no entry | not recorded | Ljung–Box 檢定 (LM25) |
| cointegration | 共整合；共積 | — | 共整合 |
| threshold cointegration | 門檻共積；門檻共整合 | not recorded | — |
| error correction model | 誤差修正模型 | not recorded | 誤差修正模型 |
| volatility | 波動；波動率 | — | 波動率 |
| volatility clustering | 波動群聚現象 | — | 波動群聚現象 |
| conditional variance | 條件變異數 (conditional heteroscedasticity: bare term none) | 條件變異數 | 條件變異數 |
| ARCH model | 自我迴歸條件變異數非齊一模型 | — | the listed form (LM26) |
| GARCH | 廣義自我迴歸條件變異數非齊一模型; IGARCH 整合廣義自我迴歸條件變異數非齊一模型 | — | 廣義自我迴歸條件變異數非齊一模型 (GARCH) |
| EWMA | EWMA model 指數加權移動平均模型; exponential smoothing 指數平滑 | — | 指數加權移動平均模型 |
| realized volatility, realized variance | no entry in any listing (integrated variance: none) | — | 實現波動率, 實現變異數 (book's own; 實現變異數 as LM3 printed it, lm03.md:710) |
| microstructure noise | no entry; noise 雜訊；噪音; high-frequency data 高頻資料 | 雜訊 | 市場微結構雜訊 (book's own); 高頻資料 |

- The rows from Gauss–Markov to error correction that the survey reported without a listing are all 統計學名詞 entries
  in its saved results (read again in Stage 1).
- The book's own forms have no 樂詞網 entry and are printed with their English in every box that uses them:
  區塊自助重抽法 (block bootstrap), 平穩自助重抽法 (stationary bootstrap), 實現變異數 (realized variance, LM3's printed
  form, lm03.md:710), 實現波動率 (realized volatility), 市場微結構雜訊 (market microstructure noise).
- Forms that differ from the listing only by spacing: the listing writes Bonferroni校正 and 增廣Dickey-Fuller檢定 with no
  space between Latin letters and Chinese; plans/vol-4.md writes "Bonferroni 校正" and "增廣 Dickey-Fuller 檢定". The
  book should choose one style.

### Stage 1 additions to the terms (2026-10-19, after the briefs)

- 樂詞網, searched 2026-10-19 with curl, using the Volume III URL pattern: 67 query strings, each in all listings, in 統計學名詞 and in 數學名詞 (201 pages).
- "—" means no entry. The Book column holds proposals for the editor.

| English | 統計學名詞 | 數學名詞 | Book (proposed) |
|:--|:--|:--|:--|
| delta method | delta法；δ法 | — | delta 法 (X7's spacing) |
| observed information | only "observed information matrix" 觀察訊息矩陣 | — | 觀察訊息(矩陣) |
| asymptotic normality | 漸近常態性 | 漸近正規性；漸近常態性 | 漸近常態性 |
| efficiency | 效率；有效性; efficient estimator 有效估計量; relative efficiency 相對效率；相對有效性 | 效率; 有效估計量; 相對效率 | 效率 |
| Pareto distribution | 帕累托分布 | — | 帕累托分布 |
| profile likelihood | 剖面概度 | — | 剖面概度 |
| basic interval | — ("basic bootstrap", "reverse percentile": —) | — | book's own |
| moving block; circular block (bootstrap) | — (other listings: engineering senses only) | — | book's own |
| block length, block size | — | block length 分組長度 (coding sense) | book's own |
| half-life | — (半衰期 in physics, astronomy and other listings) | — | 半衰期 |
| spurious regression | 虛擬迴歸；虛假迴歸 (偽迴歸: —) | — | 虛假迴歸 |
| spurious correlation | 虛擬相關；虛假相關 | 偽相關；虛假相關 | — |
| mean reversion | — (管理學名詞 平均數復歸; 均值回歸, 均值復歸, 回歸均值: —) | — | editor |
| rollover (轉倉) | — (no futures sense; 管理學名詞 rollover credit 展期信用) | — | 轉倉 (market usage) |
| collinearity; multicollinearity | 共線性; 多元共線性 | —; 多重共線性 | 共線性 |
| market model | 市場模型 | — | 市場模型 |
| credible interval | "credible intervals" 可靠區間; credible region 可靠區域 | — | 可靠區間 |
| beta distribution | 貝他(β)分布; beta-binomial 貝他(β)-二項分布 | β分布；β分配 | 貝他(β)分布 |
| grand mean | 總平均數 | — | 總平均數 |
| hyperparameter | 超參數 | — | 超參數 |
| sufficient statistic | 充分統計量 | 充分統計量 | 充分統計量 |
| shrinkage; Stein's paradox | 收縮 (收縮估計); Stein詭論 | — | 收縮 |
| trimmed mean | 截尾平均數 | — | 截尾平均數 |
| interquartile range | 四分位距；四分位數間距 (IQR) | 四分位[數間]距 | 四分位距 |
| median absolute deviation | 中位數絕對離差 (MAD) | — | 中位數絕對離差 |
| mean absolute deviation | — | 平均絕對偏差 | 平均絕對偏差 |
| robust statistics; robustness; robust estimation | 穩健統計; 穩健性; 穩健估計 | —; 穩健; — | 穩健統計 |
| quartile; octile | 四分位數; 八分位數 | 四分位數; — | 四分位數, 八分位數 |
| measure of location, dispersion | 位置量數, 離勢量數 | — | — |
| sensitivity curve | 敏感度曲線 | — | 敏感度曲線 |

### Stage 3, round 1 additions (2026-10-19)

樂詞網 searched 2026-10-19 with curl (Volume III URL pattern; 82 query strings in all listings, 統計學名詞 and 數學名詞).

| English | 樂詞網 | Book |
|:--|:--|:--|
| autocovariance | 自我共變異數 (統計學名詞; function 自我共變異函數) | 自我共變異數 |
| t-statistic | t統計量 (統計學名詞, headword "t-statistics") | t 統計量 (space as the book writes Latin names) |
| Sharpe ratio | 夏普比率 (統計學名詞); Sharpe比率 (管理學名詞) | 夏普比率 |
| sandwich estimator | 夾層估計量 (統計學名詞); 三明治 has no 統計 or 數學 entry | 夾層估計量 |
| bootstrap test | 自助重抽檢定 (統計學名詞) | 自助重抽檢定 |
| standardized residual | 標準化殘差 (統計學名詞) | 標準化殘差 |
| loss function | 損失函數 (統計學名詞, 數學名詞) | 損失函數 |
| out-of-sample | compounds only: out-of-sample forecasting 樣本外預測 (統計學名詞) | 樣本外 |
| cost of carry | none in 統計 or 數學; holding cost 持有成本 (管理學名詞) | 持有成本 |
| innovation (time series) | 新息 (數學名詞); 創新項 has no entry | 新息 |
| effective window, unconditional variance, realized variance | no entry | the book's own forms 有效視窗 (XB11, from 視窗), 無條件變異數, 實現變異數 (LM3's) |
| normal-equivalent scale, iid band, iid factor, data weight | no entry | the book's own forms 常態等效尺度, 獨立同分布區間, 獨立同分布因子, 資料權重 |

Batch B (LM23–LM26), 樂詞網 searched 2026-10-19 with curl (21 query strings, 統計學名詞 and 數學名詞):

| English | 樂詞網 | Book |
|:--|:--|:--|
| homoscedasticity (the -sk- spelling has no entry) | 變異數齊一性 (統計學名詞); 同方差性 (數學名詞) | 變異數齊一性 |
| homoscedastic | 變異數齊一的 (統計學名詞); homoscedastic model 變異數齊一模型 | 變異數齊一 (as in 誤差若變異數齊一) |
| lag | 落階；落期；遲延期數 (統計學名詞); lag operator 落後運算子; 數學名詞 compounds only | 落期 (decision XB2) |
| lagged variable or value | no 統計 or 數學 entry (經濟學名詞 落遲變數) | described: 落後一期的值 |
| 同質變異, 落後項, 落後變數, 滯後 | no entry in 統計 or 數學 | not used |
| partial autocorrelation | 偏自我相關 (統計學名詞; coefficient 偏自我相關係數) | 偏自我相關 |

Revision 1 (LM19–LM26), 樂詞網 searched 2026-10-19 with curl (46 query strings, all listings, 統計學名詞 and 數學名詞).
The book's own forms are recorded here and printed in the modules without a tag (decision XB9).

| English | 樂詞網 | Book |
|:--|:--|:--|
| drift | 漂移項 (統計學名詞; also 參數漂移, Pitman漂移); 數學名詞 only zero drift 零點漂移 | 漂移項 |
| log-likelihood | 對數概度；對數概似 (統計學名詞) | 對數概度 |
| ARCH test | 自我迴歸條件變異數非齊一檢定 (統計學名詞) | the listed form |
| Lagrange multiplier test | 拉格朗日乘數檢定 (統計學名詞) | not printed |
| opening return | no entry (opening price 開盤價格, 管理學名詞) | 開盤報酬, the book's own form |
| basic (bootstrap) interval | no entry | 基本信賴區間, the book's own form |
| moving block, circular block (bootstrap) | no entry in 統計 or 數學 | 移動區塊, 循環區塊, the book's own forms |
| block length | no entry in 統計; 數學名詞 分組長度 is the coding sense | 區塊長度, the book's own form |
| effective sample size | 有效樣本數 (統計學名詞); effective observations or days: no entry | not printed |

Revision 2 (LM19–LM26): the glosses revision 2 added to the boxes, from the verifiers' and a fresh checker's curl
lookups (2026-10-19, the Volume III URL pattern); forms already recorded above are not repeated. Decision XB11
(`reviews/vol4_cross.md`) settles the forms marked "XB11".

| English | 樂詞網 | Book |
|:--|:--|:--|
| statistic | 統計量 (統計學名詞, 數學名詞) | 統計量 |
| numerator, denominator | 分子, 分母 (數學名詞) | 分子, 分母 |
| annualized | compounds only (季節調整年化率, 統計學名詞) | 年化; 年化平均報酬, 年化夏普比率 composed |
| uncorrelated; correlated | compounds only (不相關隨機變數); 統計學名詞 compounds only | 互不相關 (LM16's Glossary form; XB11); 彼此相關 |
| mean; variance; covariance | 平均數; 變異數; 共變異數；共變異 (統計學名詞) | as listed |
| standard deviation, estimate, dependence | 標準差, 估計值, 相依性 (統計學名詞) | as listed |
| dispersion; deviation | 離勢；離散 (統計學名詞); 離差；偏差 (數學名詞) | 離散程度; 離差 |
| sampling; sampling error; error | 抽樣；取樣; 抽樣誤差; 誤差；錯誤 (統計學名詞) | 抽樣 (XB11); 抽樣誤差; 誤差 |
| sampling interval | 抽樣區間 (統計學名詞) | 抽樣區間 (XB11) |
| sampling frequency | 抽樣次數 (統計學名詞); sampling rate 抽樣率 (統計學名詞) | 抽樣頻率, another field's form (電子計算機名詞): LM20 means observations per unit of time, and 抽樣次數 reads as a count of draws, 抽樣率 as a fraction |
| numerical method | 數值法 (數學名詞) | 數值方法, LM5's form (XB11) |
| normal model | 正規模型 (數學名詞 only) | 常態模型, as the book writes 常態 |
| parameter, unbiased, significant figure, parabola, smooth function, diagonal entries, threshold, inverse matrix, linear combination | listed (統計學名詞 or 數學名詞) | as listed (門檻 of 閾值；門檻) |
| probability, test, factor, independent | 機率, 檢定, 因子 (統計學名詞); 獨立 (數學名詞-兩岸數學名詞 and 高中以下數學名詞; 統計學名詞 independence 獨立性) | as listed |
| significant | compounds only (顯著差異, 顯著域; significance 顯著性, 統計學名詞) | 顯著 |
| dimension | 維度；維數；維 (統計學名詞) | 維度 |
| forecast; target; weight | 預測 (統計學名詞); no entry; 權數 (統計學名詞) | 預測值 for a forecast value (樣本外預測 for forecasting); 目標值; 權重 (LM18's and LM24's form) |
| vector, weighted average, repeated sampling, fit, interval | 向量 (數學名詞); 加權平均(數), 重複抽樣, 配適 (in 最佳配適), 區間 (統計學名詞) | as listed |
| coefficient, intercept, slope, projection, fitted value, prediction interval, influence | listed (統計學名詞, 數學名詞) | as listed (配適值, 預測區間, 影響力) |
| window | 視域；視窗 (統計學名詞) | 視窗; 有效視窗 for the effective window (XB11) |
| parameter drift; drift | 參數漂移; 漂移項 (統計學名詞) | 參數漂移 (LM23), 漂移項 (LM25) (XB11) |
| dividend yield | dividend yield ratio 股利收益率 (管理學名詞) | 股利殖利率, LM6's form (XB11) |
| shock, one-sided test, critical value | 衝擊項, 單邊檢定, 臨界值 (統計學名詞) | as listed |
| heavy tail, conditional expectation | 重尾；厚尾, 條件期望值 (統計學名詞) | 厚尾, 條件期望值 |
| recursion, normal density, conditionally unbiased | 遞迴[式] (數學名詞); 常態密度函數; 條件不偏估計量 | 遞迴 (LM18's form), 常態密度, 條件不偏 |
| price index, risk-free rate, total excess return | 物價指數；價格指數; 無風險利率 (管理學名詞); 超額報酬 | 價格指數, 無風險利率, 超額報酬 |
| sceptical prior | 懷疑性事前分布 (統計學名詞) | 懷疑性事前分布 (XB11) |
| backtest; long; short | 回溯測試 (管理學名詞); 作多 (經濟學名詞); 放空: no entry (賣空；融券) | 回測 (the common form); 作多 (LM8's 做多 changes at Stage 4); 放空 (LM1–LM14's form) |
| false rejection | 錯誤拒絕 (engineering listings only) | 錯誤拒絕 |
| tails, adjusted, first principal component | compounds only | 尾部, 調整後, 第一主成分 |
| no entry in 統計 or 數學: log return, simple return, sample autocorrelation, shoulders, quartile skewness, joint density, second derivative, first-order expansion, fourth moment, Kelly fraction, fractional Kelly, mean return, Monte Carlo error, price limit, hedge ratio, binomial data, posterior mean, prior SD, cross-sectional mean, expected log growth, Bayes bet, common component, classical standard error, efficient price, bid and ask, basis (基差 in 經濟學名詞, 管理學名詞) | no entry | the book's forms 對數報酬, 簡單報酬, 樣本自我相關, 肩部, 四分位數偏態, 聯合密度, 二階導數, 一階展開, 四階動差, 凱利比例, 分數凱利, 平均報酬, 模擬誤差, 漲跌幅限制, 避險比例, 二項資料, 事後平均數, 事前標準差, 橫斷面平均, 期望對數成長, 貝氏下注, 共同成分, 古典標準誤, 有效價格, 買賣價, 基差 |

The Book cells above that read "—" are now filled where a module prints the term: precision 精確度 (LM24), ARCH model
自我迴歸條件變異數非齊一模型 (LM26) and Ljung–Box test Ljung–Box 檢定 (LM25).

Final check (2026-10-20), 樂詞網 searched with curl (40 query strings, all listings, 統計學名詞 and 數學名詞):

| English | 樂詞網 | Book |
|:--|:--|:--|
| log basis | no entry (basis 基差 in 經濟學名詞 and 管理學名詞 only) | 對數基差, the book's own form (LM25) |
| octile kurtosis | no entry (octile 八分位數 and kurtosis 峰態, 統計學名詞) | 八分位數峰態, the book's own form (LM19), as 四分位數偏態 |
| absolute log return | no entry (absolute value 絕對值, 數學名詞) | 對數報酬絕對值, the book's own form (LM19); not 絕對報酬, which reads as the investment term |
| third power, fourth power | 三次方；立方 (數學名詞); fourth power no entry | 三次方、四次方 (LM19) |

## Chinese terms (Volumes V and VI)

- 樂詞網, [terms.naer.edu.tw](https://terms.naer.edu.tw/) (國家教育研究院), searched 2026-10-24 for Volumes V and VI
  (`plans/vol-5.md`, shared decision "Chinese terms", and the "Chinese terms" of the nine briefs: LM27–LM31 in
  `plans/vol-5.md`, LM32–LM35 in `plans/vol-6.md`) with the URL pattern of the Volume III entry: 481 query strings
  (288 English forms with their hyphenated and unhyphenated variants, 193 Chinese forms), each run in all listings,
  in 統計學名詞 and in 數學名詞, and 374 of them also in 管理學名詞 (the other 107, terms of mathematics, statistics
  and optimization, were not): 1,817 searches and 1,903 result pages. Every filtered search was read to its last
  page, and every all-listings search to its end or to at least its first 300 rows (26 broad queries, such as
  `weight` with 2,085 rows, were read in part). Python's ssl rejected the site's certificate, so the pages were
  fetched with curl, anonymously (no cookie, no personal data), at about one request a second or less. The search
  is a phrase match on the words as written: `value at risk` does not find the management listing's
  "value-at-risk {=VaR}", nor `two-fund` its "two fund monetary separation", so both spellings were queried.
  管理學名詞-會計學, 會計學 and 經濟學 are listings of their own, separate from 管理學名詞; they and other fields are
  named in parentheses where they add an entry. Entry pages are not cited. "—" means the listing has no entry for
  that English form; "not run" means 管理學名詞 was not searched on its own for that form, and the all-listings
  search for it, read to its end for every such form but `coordinate` (and the Chinese `坐標`, `座標`), shows a
  management entry only where the cell names one.
- Decided (`plans/vol-5.md`, shared decision "Chinese terms"): the listed forms 投資組合, 效率前緣, 最小變異數投資組合,
  資本市場線, 風險規避, 二次規劃, 凸規劃 (with 凸函數, 凸集), 拉格朗日乘數, 收縮, 收縮估計量, 共變異數矩陣, 估計誤差,
  條件數, 風險平價, 風險預算, 層次叢集法, 樹形圖, 風險值, 夏普比率, 過度配適, 交易成本, 週轉率, 壓力測試, 情境分析,
  敏感度分析, 無風險利率, 資產配置, 槓桿, 限制條件, 目標函數, 對偶問題, 交叉確認, 資料偵伺, 選擇偏誤, 歷史模擬法,
  保證金追繳, 條件風險值 (CVaR, named once) and 劣可加性 (數學名詞); the book's own forms, printed with their English
  in every box that uses them: 切點投資組合 (LM7's Glossary, lm07.md:771), KKT 條件, 預期短缺 (LM5's, lm05.md:785),
  回撤, 最大回撤, 回測, 波動率目標, 層次風險平價, 前視偏誤, 存活者偏誤, 滾動前進測試, 尾部風險 and 一致性風險量數.
- Decided after this pass (`plans/vol-5.md`, "Decisions on the second recomputation and cross-check", "Chinese
  terms"): 單邊檢定 for one-sided test (LM33, as lm25.md:264); 漲跌幅限制 for price limit (LM35, as the five
  published modules; 管理學名詞's 漲跌停限制 is not used); a space between a Latin name and the Chinese after it
  (Mahalanobis 距離, as LM16 prints it at lm16.md:429 and 660, and Euler 常數), while studentized takes
  統計學名詞's form where that listing has one (Student化信賴區間); 指數加權移動平均模型 for EWMA (LM31, as
  lm26.md:132); 對偶變量 with "dual variable" at first use (LM29; LM18's 對偶變數, lm18.md:323 and 570, is
  antithetic variates); 排列檢定 for permutation test (LM32); 風險預算, which LM31's 導讀 says once is a budget per
  asset (LM7's, lm07.md:354, is a volatility limit); 秩, which LM34's 導讀 glosses as 名次 (the book's earlier
  秩 is a matrix's rank: lm09.md:473, 592; lm10.md:303, 391; lm11.md:166; lm12.md:381–382, 624); 有效限制 for an
  active constraint (LM7's Glossary prints 緊限制式（有效限制）, lm07.md:769); 權益歸零 for ruin in LM35's captions and
  §8, not 破產 (AUTHORING §1 keeps 權益歸零 for zero equity, AUTHORING.md:16; printed at lm02.md:566); and the
  Stage 4 change 切點組合 → 切點投資組合 covers lm07.md:511–512 (line 512 prints 切點組合 twice).
- Already printed and consistent (each claim of the briefs opened at its line): 再平衡 (lm08.md:403; also lm03.md:487,
  lm09.md:473, lm10.md:228, 391), 買進持有 and 漂移 (lm09.md:473), 等權重 (lm10.md:228, 391), 市場模型 (lm23.md:339–340,
  Glossary lm23.md:578), 殘差 (lm23.md:116), 最小變異數投資組合 and 切點投資組合 (lm07.md:770, 771), 樣本內／樣本外
  (lm07.md:773), 影子價格 (lm04.md:734, lm07.md:766), KKT 條件 (lm07.md:768), 緊, 鬆弛 and 互補鬆弛性
  (lm07.md:571–572), 半正定 and 正定 (LM10, lm10.md:302), 收縮估計量 (lm24.md:315, 524), 樣本外檢定 (lm11.md:409),
  超額報酬 (lm23.md:340), 特徵值 (LM11), Frobenius 範數 (lm18.md:568), 事前分布 and 事後分布 (LM24), 重抽樣 and
  自助重抽法 (LM22), 相關矩陣 (LM10, LM11), 牛頓法 (lm04.md:469–470, 742), 座標 (lm01.md:151–152, 764; lm11.md:233;
  lm12.md:382), 曝險 (lm07.md:572; lm08.md:597), 預期短缺 (lm05.md:785), 回撤 (lm01.md:152, 577–578, 779), 標準誤
  (lm18.md:566), 順序統計量 (lm14.md:603), 二項分布 (LM15, LM17), 重要抽樣 (LM18), 自我相關 (LM19),
  變異數非齊一與自我相關一致估計量 (lm23.md:269, 575), delta 法 (lm20.md:412–413, 627), 檢定力, 多重假設檢定, 族系誤差率
  and 資料偵伺 (LM21), 循環區塊, 區塊自助重抽法 and 平穩自助重抽法 (lm22.md:236, 537–540), 回測 (lm21.md:189, 380;
  research-hygiene.md:7).

Two "already printed" claims of the briefs were wrong. LM33's brief gave 單尾檢定 as LM25's form, but lm25.md:264
prints 單邊檢定（one-sided test）, `src/` has no 單尾檢定, and the Volume IV entry (Revision 2) records 單邊檢定.
LM31's brief gave LM26's form as the bare 指數加權移動平均, but lm26.md:132 prints 指數加權移動平均模型（EWMA）, and
LM26's Glossary row is 指數加權移動平均模型 (lm26.md:550), the form the Volume IV table records.
An earlier LM29 brief said interior-point method appears only as 經濟學's 內在點法; 統計學名詞 lists 內點法, which
the book uses (AUTHORING §1 takes the mathematics or statistics listing).

The shared list (`plans/vol-5.md`, "Chinese terms"):

| English | 統計學名詞 | 數學名詞 | 管理學名詞 | Book |
|:--|:--|:--|:--|:--|
| portfolio | 投資組合 | — | 投資組合 (管理學名詞-會計學: [投資]組合) | 投資組合 |
| efficient frontier | — | — | 效率前緣 | 效率前緣 |
| minimum-variance portfolio | — (minimum variance 最小變異數) | — | 最小變異數投資組合 (hyphenated headword; 經濟學 "Minimum variance portfolio" 最低變異數資產組合) | 最小變異數投資組合 (lm07.md:770) |
| capital market line | — | — | 資本市場線 (headword "capital market line、 CML"; also 經濟學) | 資本市場線 |
| risk aversion | — | — | 風險規避 (經濟學 風險袪避) | 風險規避 |
| quadratic programming | 二次規劃 | 二次型規劃 | — | 二次規劃 |
| convex programming; convex optimization | 凸規劃; — | 凸規劃; — | not run (convex optimization: 電子工程名詞 凸形最佳化 only) | 凸規劃 |
| Lagrange multiplier | compounds only (拉格朗日乘數檢定, 增廣拉格朗日乘數法) | Lagrange乘數；Lagrange乘子 | — (拉格朗日乘數 in 電子計算機名詞, 土木工程名詞 and other engineering listings) | 拉格朗日乘數 (lm04.md:282, lm07.md:353, lm11.md:312) |
| shrinkage; shrinkage estimator | 收縮; 收縮估計量 | — (contraction 縮距；收縮；縮約) | — | 收縮, 收縮估計量 (LM24) |
| covariance matrix | 共變異數矩陣 | 共變異方陣 | — | 共變異數矩陣 |
| estimation error | "error of estimation" and "estimate error" 估計誤差 ("estimation error" 估計誤差: 海洋地質學 only) | — | — | 估計誤差 |
| condition number | 條件數 | 條件數 | — | 條件數 |
| risk parity | only "risk-parity portfolio" 風險平價投資組合 | — | — | 風險平價 |
| risk budget; risk budgeting | —; — | —; — | —; — (電子工程名詞 and 電機工程名詞 "risk budget" 風險預算) | 風險預算, another field's entry; LM31's is a budget per asset, LM7's a volatility limit (lm07.md:354) |
| hierarchical clustering | 層次叢集法 (also "hierarchical cluster method") | — | — | 層次叢集法 |
| dendrogram | 樹形圖 | — (tree diagram 樹形圖) | not run | 樹形圖 |
| value at risk | 風險值 (headword "value at risk (VaR)") | — | 風險值 (headword "value-at-risk {=VaR}"; also 管理學名詞-會計學) | 風險值 |
| conditional value at risk | 條件風險值 | — | 條件風險值 ("conditional value-at-risk") | 條件風險值, named once |
| expected shortfall | 期望損失 (also the entry for "expected loss") | — | 預期損失 | 預期短缺 (lm05.md:785) |
| Sharpe ratio | 夏普比率 | — | Sharpe比率 | 夏普比率 |
| overfitting | 過度配適 | — | — | 過度配適 |
| transaction cost | — | — | 交易成本 (also 經濟學, 管理學名詞-會計學) | 交易成本 |
| turnover; turnover rate | —; — | —; — | 離職；週轉; 周轉率 (會計學 and 電子計算機名詞 週轉率) | 週轉率 |
| stress testing; stress test | —; — | —; — | 壓力測試; — (管理學名詞-會計學 壓力測試; 經濟學 壓力檢定) | 壓力測試 |
| scenario analysis | 情境分析 | — | 情境分析 | 情境分析 |
| sensitivity analysis | 敏感度分析 | 敏感度分析 | 敏感度分析 | 敏感度分析 |
| risk-free rate | — | — | 無風險利率 ("risk-free rate of interest", "risk-free interest rate、 RFR") | 無風險利率 (lm23.md:340) |
| asset allocation | — | — | 資產配置 | 資產配置 |
| leverage | 槓桿；槓桿作用 | — | — (compounds only) | 槓桿 |
| constraint | 限制條件；限制 | 制限；約束 | 限制 | 限制條件 (LM7 also prints 限制式, lm07.md:353) |
| objective function | 目標函數 | 目標函數 | 目標方程式；目標函數 | 目標函數 |
| dual problem | 對偶問題 | — (compounds only) | — | 對偶問題 |
| cross-validation | 交叉確認 | — | — (經濟學 交叉驗證) | 交叉確認 |
| data snooping | 資料偵伺 | — | — | 資料偵伺 (LM21) |
| selection bias | 選擇偏誤；選擇偏差 | — | 選擇偏差 | 選擇偏誤 |
| historical simulation method | — | — | 歷史模擬法 | 歷史模擬法 |
| margin call | — | — | 保證金追繳 | 保證金追繳 |
| subadditivity; finite subadditivity | —; — | 劣可加性; 有限[的]次加性；有限[的]劣加性 | not run (經濟學 次加性) | 劣可加性 |
| risk measure; coherent risk measure | 風險量數; — | —; — | —; — | 一致性風險量數, the book's own |
| backtesting; backtest | —; — | —; — | 回溯測試; — | 回測 (lm21.md:189) |

No listing has an entry for tangency portfolio, KKT conditions (only 經濟學's "Kuhn-Tucker conditions" 肯塔克條件),
drawdown (only other senses: 洩降, a water-level term, in earth-science, engineering and environmental listings; a
pressure or production decline in 礦冶工程名詞; 紡織科技's "draw-down" 紡絲拉伸比), maximum drawdown, volatility
targeting or target, hierarchical risk parity, look-ahead bias, survivorship bias (only "survivorship curve" 存活曲線
(動物學名詞: 生存曲線), in life-science, ecology, marine and environmental listings), walk-forward test or tail risk;
回測 itself is only 測量學's "set back".

LM27 and LM28 (new terms):

| English | 統計學名詞 | 數學名詞 | 管理學名詞 | Book |
|:--|:--|:--|:--|:--|
| rebalancing; rebalance | —; — | —; — | —; — (管理學名詞-會計學 "rebalancing" 重新平衡; "rebalance" 再平衡 in 電子計算機名詞, 再平衡；重新平衡 in 一般性常見術語) | 再平衡 (lm08.md:403) |
| buy-and-hold | — | — | — | 買進持有 (lm09.md:473) |
| systematic risk | 系統性風險 | — | 系統風險 | 系統性風險 |
| idiosyncratic risk; unsystematic risk | —; — | —; — | 特質風險; 非系統風險 | not used (殘差) |
| single index model | 單一指標模型 | — | — | 單一指標模型 |
| factor model | 因子模型 | — | 因子模型 (經濟學 要素模型) | 因子模型 |
| variance decomposition | 變異數分解 (headword "variance decomposition (VDC)") | — | — | 變異數分解 |
| homogeneous function; positively homogeneous | —; — | 齊性函數; 正齊次的 | — | 一次齊性函數, composed |
| Euler's theorem | — | — (the listing writes Euler數, Euler常數) | — (歐拉定理 in 測量學, 測繪學辭典, 地理學名詞-測繪學名詞, 海洋地質學, 電子計算機名詞) | Euler 定理 |
| diversification | 多樣化 | — | 多角化; "limit of diversification" 風險分散極限原則; "well-diversified portfolio" 充分分散風險的投資組合 (經濟學 風險分化) | 風險分散 |
| risk contribution; marginal contribution; risk decomposition; risk attribution | — (contribution rate 貢獻率；提撥率) | — | — | 風險貢獻, 邊際風險貢獻, the book's own |
| commission | — | — | 佣金 (also 管理學名詞-會計學; 會計學 傭金，手續費) | 手續費 |
| securities transaction tax | — | — | 證券交易稅 (also for "securities exchange tax", "stock transaction tax", "transfer tax on stock"; 會計學 證券交易稅; 經濟學 "transaction tax" 交易稅) | 證券交易稅 |
| exchange traded fund | 指數股票型基金 ("exchange traded fund (ETF)") | — | 指數股票型基金 ("exchange traded fund, ETF") | 指數股票型基金 |
| self-financing | — | — | 自籌資金 (also "self-financing project" 自籌資金計畫) | 自我融資, composed (LM27's brief reads 自籌資金 as a firm's own funds, another sense) |
| asynchronous | — | 非同步的；異步的 | — | 非同步 |
| hedge | — | — | 避險 ("hedge"; "hedge、 hedging") | 避險 |
| weight | 權數 | 重量；權[重]函數 | — | 權重 (Volume IV) |
| correlation coefficient | 相關係數 | 相關係數 | 相關係數 (headword spelt "correlation coeffeicient", found by the query `相關係數`; also 經濟學) | 相關係數 |
| closing price | — | — | 收盤價 | 收盤 |
| efficient portfolio | — | — | 效率投資組合 | 效率投資組合 |
| risk-free asset | — | — | 無風險資產 (also 經濟學, with "riskless asset") | 無風險資產 |
| separation theorem | 分離定理 | — | — (經濟學 分離定理) | 分離定理 |
| two-fund separation | — | — | — ("two fund monetary separation" 兩基金的貨幣分離) | 兩基金分離, composed |
| parabola; hyperbola; asymptote | —; —; 漸近線 | 拋物線; 雙曲線; 漸近線 (headword "asymptote ; asymptotic line") | not run | 拋物線, 雙曲線, 漸近線 |
| mean–variance | — | — | compounds only: "mean-variance analysis" 平均數-變異數分析, "mean-variance criterion" 平均數-變異數準則 | 平均數-變異數 |
| sensitivity | 敏感度 | 敏感度 | — | 敏感度 |
| Jacobian matrix | — | Jacobi矩陣 (Jacobian: Jacobi行列式) | not run | not in a box |
| in-sample; out-of-sample | compounds only: in-sample observation 樣本內觀察值; out-of-sample forecasting 樣本外預測 | — | — | 樣本內／樣本外 (lm07.md:773) |

LM29, LM30 and LM31 (new terms):

| English | 統計學名詞 | 數學名詞 | 管理學名詞 | Book |
|:--|:--|:--|:--|:--|
| convex set | 凸集 | 凸集 | not run (工業工程名詞 凸集合) | 凸集 |
| convex function; strictly convex function | 凸函數; 嚴格凸函數；狹義凸函數 | 凸函數; 嚴格凸函數 | not run | 凸函數, 嚴格凸函數 |
| convex combination | 凸組合 | 凸組合 | not run | 凸組合 |
| half space; hyperplane; convex polyhedron | —; —; — | 半空間; 超平面; 凸多面體 | not run | 半空間, 超平面, 凸多面體 |
| linear programming | 線性規劃 | 線性規劃 | not run (the all-listings search shows 線性規劃) | 線性規劃 |
| feasible region | — | 可行解區域 | not run (工業工程名詞 可行區域) | 可行解區域 |
| complementary slackness | — | 互補鬆弛性 | not run | 互補鬆弛性 (lm07.md:572) |
| shadow price | — | 影子價格 | not run (also 經濟學) | 影子價格 (lm07.md:766) |
| constraint qualification | — | 約束規範 | not run | 約束規範 |
| sufficient condition; necessary condition | —; — | 充分條件; 必要條件 | not run (the all-listings searches show "Sufficient Condition" 充分條件 and "Necessary Conditions" 必要條件) | 充分條件, 必要條件 |
| positive semidefinite | — | 半正定 | not run | 半正定 (lm10.md:302) |
| penalty function | — | 懲罰函數 | not run | 懲罰函數 |
| dual variable | — | 對偶變量 | not run | 對偶變量, with "dual variable" at first use (LM29) |
| antithetic variables, variates | 對偶變數 ("antithetic variables") | 對偶變數 ("antithetic variates") | — | 對偶變數 (lm18.md:570) |
| multiplier | — | 乘數；乘式；乘子 | — | 乘數 (LM7) |
| active set; active constraint | —; — | —; 起作用的約束 | not run; — (經濟學 有效限制; 工業工程名詞 作用限制條件) | "active set" in English; 有效限制, as LM7's Glossary 緊限制式（有效限制） (lm07.md:769) |
| interior-point method | 內點法 | — (interior point 內點) | not run (經濟學 "Interior point method" 內在點法) | 內點法 (統計學名詞), only where a box names the method |
| slack | — | — (slack variable 鬆弛變量；附加變數) | not run | 鬆弛 (lm07.md:572) |
| no-trade band; operator splitting; solver | — | — (solver: compounds such as Riemann solver) | not run | English |
| mean squared error | 均方誤差 ("mean squared error (MSE)", "mean square error (MSE)") | 均方誤差 ("mean square error (MSE)") | — | 均方誤差 |
| bias–variance tradeoff | 偏誤及變異數之抵換 (tradeoff 抵換；互償) | — | — | 偏誤及變異數之抵換 |
| sampling error | 抽樣誤差 | 抽樣誤差 | 抽樣誤差 | 抽樣誤差 |
| Monte Carlo simulation | 蒙地卡羅模擬 | — | 蒙地卡羅模擬 | 蒙地卡羅模擬 |
| plug-in principle | 代入原則 | — | — | 代入原則; 代入投資組合, the book's own |
| excess return | 超額報酬 | — | — ("abnormal return" 超額報酬; 經濟學 "Excess returns" 超額報酬) | 超額報酬 (lm23.md:340) |
| eigenvalue | 特徵值；固有值 | 固有值 ("characteristic value ; proper value" 特徵值) | not run | 特徵值 (LM11) |
| Frobenius norm | — | Frobenius範數 | not run | Frobenius 範數 (lm18.md:568) |
| ill-conditioned matrix | 病態矩陣 | 病態矩陣 | not run | 病態矩陣 |
| correlation matrix | 相關矩陣 | 相關矩陣 | — | 相關矩陣 (LM10, LM11) |
| nonnegativity condition | — | 非負性條件 | not run | 非負性條件 |
| weighted average | 加權平均(數) | 加權平均[值]；加權平均數 (headword "weighted average ; weighted mean") | — | 加權平均 |
| equilibrium; market equilibrium | 均衡；平衡; — | 平衡；平衡點; — | 均衡; 市場均衡 | 均衡 |
| implied volatility | — | — | 隱含波動度 | not used; 隱含超額報酬, the book's own |
| equally weighted index | — | — | 等權指數 | 等權重 (lm10.md:228, 391) |
| reference portfolio; view | —; — | —; — | —; — | 參考投資組合, 觀點, the book's own |
| James–Stein estimator | James-Stein估計量 | — | — | James–Stein 估計量 |
| Black–Litterman; Ledoit–Wolf | — | — | — | English |
| single linkage clustering | 單一連接叢集法；最近連接叢集法 | — | — | 單一連接叢集法 |
| Euclidean distance | 歐氏距離 | 歐氏距離 | not run | 歐氏距離 |
| uniqueness | 唯一性 | 唯一性 | not run (the all-listings search shows 獨特性) | 唯一性 |
| positive definite; positive definite matrix | 正定的; — | 正定的; 正定方陣 | not run; — | 正定 (lm10.md:302) |
| Newton's method | — | 牛頓法 (headword "method of Newton ; Newton's method") | not run | 牛頓法 (LM4) |
| fixed point | — | 不動點；定點 | not run | 不動點 |
| coordinate; descent method; coordinate descent | —; —; — | 坐標; 下降法; — | not run | 座標下降法, composed with the book's 座標 |
| EWMA | "EWMA model" 指數加權移動平均模型 | — | 指數加權移動平均數; "EWMA model" 指數加權移動平均模型 | 指數加權移動平均模型 (lm26.md:132, 550; LM31) |
| exposure | — (compounds: exposure at default 違約曝險額; exposure ratio 暴露比；暴險比) | — | — (管理學名詞-會計學 "risk exposure" 暴險) | 曝險 (lm08.md:597) |
| bisection; recursive bisection | dichotomy 二分法; — | bisection method 二分法; — | not run | 遞迴二分, composed |
| reestimation | 再估計 | — | — | 定期再估計, composed |
| periodic | — | — | — (動物學名詞 周期性；定期的; 國防部新編國軍簡明美華軍語辭典 定期，週期的) | 定期 |
| trigger | — | — | — (compound "trigger price" 觸發價格; 一般性常見術語 觸發；觸發點) | 風險觸發, composed |
| threshold | compounds only | 閾值；門檻 | — | 門檻 |

No listing has an entry for no-trade band, operator splitting, risk contribution, marginal contribution, coordinate
descent, inverse variance or volatility, quasi-diagonalization, equal risk contribution, recursive bisection,
volatility targeting, reference portfolio, Black–Litterman or Ledoit–Wolf. LM31's composed forms, printed with their
English in every box that uses them: 等風險貢獻 (equal risk contribution, ERC), 反波動率權重 (inverse-volatility weights)
and 準對角化 (quasi-diagonalization); the other forms are in the rows above and in the list of the book's own forms.

Volume VI, LM32–LM35 (new terms):

| English | 統計學名詞 | 數學名詞 | 管理學名詞 | Book |
|:--|:--|:--|:--|:--|
| tail value at risk | 尾端風險值 | — | — | not used |
| order statistic | 順序統計量；有序統計量 (headword "order statistics") | 順序統計量 | not run | 順序統計量 (lm14.md:603) |
| quantile; sample quantile | 分位數; — | 分位數; 樣本分位數 | —; — | 分位數, 樣本分位數 |
| binomial distribution; binomial test | 二項分布; — | 二項分布；二項分配; 二項檢驗 | —; not run | 二項分布 (LM15, LM17); the test not named |
| test of independence | 獨立性檢定 ("test of independence", "test for independence") | 獨立性檢定 ("independence test") | — | 獨立性檢定 |
| permutation test | 排列檢定 | 置換檢驗 | not run | 排列檢定 (LM32) |
| importance sampling | 重要抽樣 | 重要性抽樣 | 重要性抽樣法 | 重要抽樣 (LM18) |
| fat tail; heavy tail | compounds only; 重尾；厚尾 | — | 厚尾 (headword "fat tail、 heavy-tailed distributions") | 厚尾 |
| skewness | 偏態 | 偏斜度 | — | 偏態 |
| kurtosis | 峰態 | 峰度 | — | 峰態 |
| studentized confidence interval | Student化信賴區間 | — | not run | Student化信賴區間, 統計學名詞's form |
| serial correlation | 序列相關 | 序列相關 | — | 自我相關 (LM19's) instead |
| Euler's constant | Euler常數 ("Euler's constant") | Euler常數 ("Euler constant") | not run | Euler 常數 |
| one-sided test; one-tailed test | 單邊檢定 (also "single-sided test"); 單尾檢定 (also "single tail test") | 單側檢定; — | — | 單邊檢定 (lm25.md:264) |
| delta method | delta法；δ法 | — | — | delta 法 (LM20) |
| familywise error rate | 族系誤差率 (no entry for the hyphenated form) | — | — | 族系誤差率 (LM21) |
| logit | 對數勝算；邏輯式 | — | not run (經濟學 羅吉特機率) | 對數勝算 |
| rank | 秩 | 秩 | not run | 秩, glossed as 名次 in LM34's 導讀 (名次 has no 統計學名詞, 數學名詞 or 管理學名詞 entry) |
| bootstrap; stationary bootstrap | 自助重抽法；靴拔重抽法; — | — | — | 自助重抽法; 平穩自助重抽法 (LM22) |
| delisting | — | — | — (電子計算機名詞 刪除表列; 下市 only in 下市交易, "going-private transaction", 管理學名詞-會計學) | 下市 |
| benchmark | 基準 | — | 比較基準 (headword "Benchmarks", found by the query `基準`) | 基準 |
| contango | — | — | 正向市場 (會計學 延期交割費) | 正價差, TWSE's word (LM34 §5) |
| Mahalanobis distance | Mahalanobis距離 | Mahalanobis距離 | — | Mahalanobis 距離 (lm16.md:429, 660) |
| conditional expectation | 條件期望值 | 條件期望值 | — | 條件期望值 |
| price limit | — | — | 漲跌停限制 | 漲跌幅限制 (lm04.md:212, lm12.md:527, lm13.md:342, lm17.md:450, lm22.md:355; no listing has it) |
| worst-case scenario | — | — | — (新聞傳播學名詞 最差情況；最糟情境) | not printed in a box (LM35's brief) |
| what-if scenario | — | — | — (土木工程名詞 假設情境) | 假設情境 (hypothetical scenario) |
| overnight | — (overnight interbank call loan rate 隔夜拆款利率) | — | — | 隔夜 |
| proxy | — | — | 委託書 (管理學名詞-會計學 參考值；替代; 會計學 代理，委託; 電子計算機名詞 代理伺服器) | 代理資產, composed |
| exchange rate | 匯率 | — | 匯率 | 匯率 |
| ruin | — (gambler's ruin 賭者破產; ruin problems 破產問題; ruin theory 破產理論) | — | — | 權益歸零 in LM35's captions and §8, not 破產 (AUTHORING §1) |

Besides drawdown, coherent risk measure and tail risk (above), no listing has an entry for positive homogeneity,
translation invariance, long-run variance, expected maximum, haircut, circular block, walk-forward test, reverse
stress test or testing, stress scenario (壓力情境 is only 心理學名詞's "stressful situation"), historical scenario,
hypothetical scenario, gap risk, proxy variable, zero equity or price gap. Exceedance, deflated (Sharpe ratio), track
record and effective number (of trials) appear only in other senses in other fields, such as 統計學名詞's
"exceedance life test" 超值壽命試驗 and the electronics listings' "track record" 軌跡紀錄. The book's own forms for
them, printed with their English in every box that uses them: 回撤, 最大回撤, 一致性風險量數, 尾部風險, 長期變異數,
循環區塊 (LM22), 滾動前進測試, 反向壓力測試, 壓力情境, 歷史情境, 跳空, 鎖跌停 (limit-down lock, LM35's brief; searched
in Chinese only), 代理資產 and 權益歸零; "exceedance" is glossed 超過 VaR 的日子, and PSR, DSR, MinTRL and haircut stay
in English.

## Writing style (AUTHORING §1, checked 2026-10-11)

Read for the Volume II style rules; each statement below was checked against the source by a second agent or by the
editor.

- GOV.UK [A to Z style guide](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/style-guides/a-to-z-style-guide/),
  "Sentence length": check sentences of more than 25 words to see whether a split makes them clearer. Inside GOV.UK,
  ["Sentence length: why 25 words is our limit"](https://insidegovuk.blog.gov.uk/2014/08/04/sentence-length-why-25-words-is-our-limit/)
  (Sara Vincent, 2014-08-04): break such sentences up or condense them, and otherwise keep them plain.
- European Commission, Directorate-General for Translation, *How to write clearly* (2011, ISBN 978-92-79-16957-1; read
  in a third-party copy of the official PDF): 20 words a sentence on average, and keep link words such as "but", "so"
  and "however" when splitting.
- Plain English Campaign, *How to write in plain English* (`howto.pdf`, linked from plainenglish.co.uk/free-guides): an
  average sentence length of 15 to 20 words.
- PLAIN, Federal Plain Language Guidelines, "Write short paragraphs"
  ([archived source](https://raw.githubusercontent.com/GSA/plainlanguage.gov/main/_pages/guidelines/concise/write-short-paragraphs.md)):
  paragraphs of no more than 150 words in three to eight sentences.
- Halmos, "How to Write Mathematics", *L'Enseignement Mathématique* 16 (1970): a theorem statement is one sentence
  whenever possible; never start a sentence with a symbol.
- Knuth, Larrabee and Roberts, *Mathematical Writing*, MAA Notes 14 (1989): symbols in different formulas are separated
  by words (§1); M.-C. van Leunen's class (§35): averages under 20 words a sentence, with varied lengths.
- Krantz, *A Primer of Mathematical Writing*, 2nd ed. ([arXiv:1612.04888](https://arxiv.org/abs/1612.04888), 2016):
  short declarative sentences and short paragraphs, each with one point.
- Blau, "The Effect of Syntax on Readability for ESL Students in Puerto Rico", *TESOL Quarterly* 16(4) (1982),
  [doi:10.2307/3586469](https://doi.org/10.2307/3586469) (abstract read in an OpenAlex copy): complex sentences with
  the clues to their relationships left intact scored highest, above short simple sentences, so material at a lower
  readability-formula level did not help these second-language readers understand.
- Yano, Long and Ross, "The Effects of Simplified and Elaborated Texts on Foreign Language Reading Comprehension",
  *Language Learning* 44(2) (1994), [doi:10.1111/j.1467-1770.1994.tb01100.x](https://doi.org/10.1111/j.1467-1770.1994.tb01100.x)
  (Crossref abstract): comprehension of the simplified and the elaborated versions did not differ significantly.
- Crossley, Allen and McNamara, "Text readability and intuitive simplification: A comparison of readability
  formulas", *Reading in a Foreign Language* 23(1): 86–101 (2011),
  [ScholarSpace record](https://scholarspace.manoa.hawaii.edu/items/fc754b04-a1ef-4176-885e-e4389a3a27e0/full): an index
  built on cognitive measures sorted intuitively simplified texts into beginning, intermediate and advanced levels
  significantly better than traditional readability formulas built on sentence and word length.
- Nielsen Norman Group: Nielsen, ["How Users Read on the Web"](https://www.nngroup.com/articles/how-users-read-on-the-web/)
  (1997), one idea per paragraph; Moran, ["Reading Content on Mobile Devices"](https://www.nngroup.com/articles/mobile-content/)
  (2016), no practical difference in comprehension between phones and desktops.
