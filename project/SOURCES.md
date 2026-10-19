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
| FinMind [Pricing](https://finmind.github.io/Pricing/) and [Disclaimer](https://finmind.github.io/Disclaimer/) pages | hourly quotas per plan; the terms on redistribution and attribution that govern what Volume IV commits (below) |

Every registered FinMind file is fetched, and re-checked byte for byte, through the FinMind API with `data/fetch_finmind.py`;
intraday files, one request a day, with `data/fetch_intraday.py` and its own manifest (Volume IV).

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
  Disclaimer is dated 版本日期：2026-07-12; its sections are numbered 一 to 五, and §3.2 and §3.3 are items 2 and 3 of
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
| TWSE Rules Governing Trading of Beneficial Certificates (受益憑證買賣辦法), Art. 8 ¶2, [EN](https://twse-regulation.twse.com.tw/EN/law/DAT0201.aspx?FLCODE=FL007114), [ZH](https://twse-regulation.twse.com.tw/TW/law/DAT0201.aspx?FLCODE=FL007114) | a leveraged or inverse ETF on a domestic index has a daily limit of 10% times its multiple (version amended 2025-09-30, read 2026-10-11; 00631L's −19.995% and +19.968% limit closes of April 2025 fit 20%); the Operating Rules (營業細則) Art. 63 have no ETF clause |
| TWSE Holiday Schedule 2025 (JSON endpoint `twse.com.tw/rwd/en/holidaySchedule/holidaySchedule?response=json&date=20250101`; the page is rendered by JavaScript) | 3 April 2025 adjusted holiday; 4 April Children's Day and Tomb-sweeping Day (read 2026-10-11) |
| 全國法規資料庫: [Banking Act Art. 47-1](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=G0380001&flno=47-1), 信用卡業務機構管理辦法 [Art. 48](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=G0380055&flno=48) | 15% cap on card revolving interest from 2015-09-01; no compounding of revolving interest (Art. 48 item 1, read 2026-10-11) |
| [Bank of Taiwan rates](https://rate.bot.com.tw/twd) | one-year 定期儲蓄存款 1.725% and 定期存款 1.700%, posted 2026-10-10 |

## Banks, issuers and firms

| Page | Used for |
|:--|:--|
| COTA Bank revolving-credit disclosure (cotabank.com.tw, card_pdf_revolvingCredit.pdf) | revolving interest = balance × rate × days/365 |
| DBS Taiwan NTD deposit terms (dbs.com.tw, DBS_NTD_Deposit.pdf; 新台幣存款計息方式, updated 2024-04-10; read by local text extraction, 2026-10-11) | 整存整付 compounds monthly; 存本取息 accrues daily; actual days over 365, leap years included |
| Bank of Taiwan 存戶須知重要內容說明書 (version 2017-01-26, hosted on gov.tw) | whole months credited monthly, part months by day; 整存整付 compounded, 存本取息 simple: not the same convention as DBS |
| [Yuanta 00679B fund page](https://www.yuantaetfs.com/product/detail/00679B/Basic_information) and holdings ratio page | tracked index (ICE US Treasury 20+ Year), set-up 2017-01-11, listing 2017-01-17, no currency hedge |
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
  annualized by multiplying by √12 except under very special circumstances"; serial correlation can overstate the
  annual ratio by "as much as 65 percent" (LM19's annualization rule; LM33).
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
- Bibliographic data only: Harvey, "Presidential Address: The Scientific Outlook in Financial Economics", *JF* 72(4):
  1399–1440, 2017, DOI [10.1111/jofi.12530](https://doi.org/10.1111/jofi.12530); Harvey & Liu, "Backtesting", *JPM*
  42(1): 13–28, 2015, DOI [10.3905/jpm.2015.42.1.013](https://doi.org/10.3905/jpm.2015.42.1.013); Romano & Wolf,
  "Exact and Approximate Stepdown Methods for Multiple Hypothesis Testing", *JASA* 100(469): 94–108, 2005, DOI
  [10.1198/016214504000000539](https://doi.org/10.1198/016214504000000539); Hansen, P. R., "A Test for Superior
  Predictive Ability", *JBES* 23(4): 365–380, 2005, DOI
  [10.1198/073500105000000063](https://doi.org/10.1198/073500105000000063); Neyman & Pearson, "On the problem of the
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
  December 2008, DOI [10.1016/j.jempfin.2008.03.002](https://doi.org/10.1016/j.jempfin.2008.03.002). Read in IEW
  Working Paper 320 (January 2008): Jobson–Korkie, as corrected by Memmel (2003), is invalid under heavy tails or
  time-series data; they propose a studentized time-series bootstrap interval for the difference of two Sharpe ratios.
  §3.1 HAC inference; §3.2.2 the circular block bootstrap of Politis & Romano (1992); footnote 5 explains why circular
  rather than Künsch's moving blocks (edge effects); Algorithm 3.1 chooses the block size. These numbers come from the
  working paper and were not compared with the journal.
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
  seen.
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
| precision | 精確度 | 精確；精[密]度 | — |
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
| Ljung–Box test | no entry | not recorded | — |
| cointegration | 共整合；共積 | — | 共整合 |
| threshold cointegration | 門檻共積；門檻共整合 | not recorded | — |
| error correction model | 誤差修正模型 | not recorded | 誤差修正模型 |
| volatility | 波動；波動率 | — | 波動率 |
| volatility clustering | 波動群聚現象 | — | 波動群聚現象 |
| conditional variance | 條件變異數 (conditional heteroscedasticity: bare term none) | 條件變異數 | 條件變異數 |
| ARCH model | 自我迴歸條件變異數非齊一模型 | — | — |
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
| effective window, unconditional variance, realized variance | no entry | the book's own forms 有效窗口, 無條件變異數, 實現變異數 (LM3's) |
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
