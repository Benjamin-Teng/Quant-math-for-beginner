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

Every registered FinMind file is fetched, and re-checked byte for byte, through the FinMind API with `data/fetch_finmind.py`.

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
