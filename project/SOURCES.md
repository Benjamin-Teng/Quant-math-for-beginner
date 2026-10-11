# Sources consulted

Every website and data service used while building edition 0.1 and the Volume I drafts (2026-10-10), extracted from
the session logs of the editor and all writer, reviewer and data agents. Each module's own References section is the
authoritative citation list; this file shows where facts were checked, so the next session can go straight to the
right page. Four pages about a professional-certification curriculum, consulted for edition 0.1, are left out: the
owner had that edition's crosswalk and curriculum references removed on 2026-10-10, and no current text cites them.
Pages an exam body publishes publicly are listed like any other source when a module uses them (PITFALLS §1).

## Market data

| Service | Used for |
|:--|:--|
| FinMind `TaiwanStockPrice` | 0050, 00631L, 00679B daily closes and spreads; TAIEX daily closes; 2330 and 2317 around 30 June 2025 |
| FinMind `TaiwanStockDividendResult` | 0050 and 00679B ex-dates, before/after prices, cash dividends |
| FinMind `TaiwanFuturesDaily` | TX (and MTX for a cross-check), every contract month, April–October 2025 |
| FinMind `TaiwanStockTotalReturnIndex` | TAIEX total-return index (LM6 dividend measurement) |
| FinMind `USStockPrice` | QQQ and TQQQ, calendar 2022 (LM3) |
| FinMind `InterestRate` | tried for Taiwan's policy rate: not available (Fed, ECB and others only) |
| FinMind `TaiwanVariousIndicators5Seconds` | tried for TAIEX intraday on 2025-06-30 |
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
| TWSE [index compilation rules IndexS03.pdf](https://www.twse.com.tw/downloads/zh/products/indices/IndexS03.pdf), IndexS07.pdf | TAIEX and total-return index methodology |
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
| TechNews 2025-04-07 (black Monday records), Taiwan News zh/news/6078269 | 7 April 2025 tariff sell-off |
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
| SciPy [`linalg.cholesky`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.cholesky.html) (v1.18) | returns the upper factor by default |
| 樂詞網, [terms.naer.edu.tw](https://terms.naer.edu.tw/) (國家教育研究院) | Chinese terms of the 中文導讀 (AUTHORING §1); Volume II's list is in `plans/vol-2.md`, "Chinese terms" (searched 2026-10-11) |

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
  and Cornell's GVL page), not from the book itself.

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
