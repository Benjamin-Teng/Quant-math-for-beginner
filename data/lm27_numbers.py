"""Every number that LM27 (Portfolio Return and Risk) prints, computed and checked against src/lm27.md.

Run:  uv run python data/lm27_numbers.py
      (after data/vol5_series.py, data/vol5_rules.py, data/vol2_series.py and data/vol3_series.py; and after
      data/lm27_charts.py, whose chart files and widget block this script checks)

Inputs and conventions: data/lm27_common.py (E5's two frames and the through case's R1 and R2 through the shared
builders vol5_series and vol5_rules; U28 through lm10_series). It reads nothing else and writes nothing. The module
text is src/lm27.md; plans/vol-5-anchors.md, "LM27", holds the Stage 1 anchors A27-01 .. A27-50, which
data/vol5_anchors_lm27.py prints and this script started from.

Part 1 rebuilds every anchor line exactly as data/vol5_anchors_lm27.py prints it and compares it with the anchor
table's Value column: a difference is reported, never forced.

Part 2 checks the text (each check stops the script on a failure):
  chk(label, value, fmt, printed)  format(value, fmt) equals the printed string, the value is not a rounding tie of
                                   that format, and the printed string is in the module as a whole number. Figures
                                   printed beside their inputs are recomputed from the printed, rounded inputs too.
  has(label, text)                 a literal string (a date, a phrase, a table row) is in the module.
At the end the script lists the numbers of the module that no check covered and prints "all N checks passed".
"""
import json
import math
import re
import sys
from collections.abc import Iterable
from datetime import date, datetime
from math import floor, sqrt
from zoneinfo import ZoneInfo

import numpy as np
from lm27_common import (
    A7,
    C3,
    ROOT,
    S3,
    SA,
    SH,
    SH2,
    SM,
    A,
    A_week,
    Afreq,
    Au,
    B,
    Cd,
    Ck,
    F,
    G_span,
    J,
    N,
    P,
    Sn,
    T,
    Tu,
    W_first,
    W_post,
    W_pre,
    Wq,
    a9,
    ap_q,
    approx,
    b1,
    b2,
    b9,
    beta,
    bn,
    bp,
    c50,
    c_before,
    c_last,
    com_i,
    covp,
    days,
    days_wk,
    dbh,
    dlt,
    dm_list,
    drift,
    eq_span,
    ex3,
    first_rows,
    fr,
    frq,
    g0,
    g_hi,
    g_lo,
    g_n,
    g_p,
    gap,
    gap_2dp,
    gap_m,
    gap_wm,
    ge,
    gw,
    halted,
    hi_p,
    k6,
    k_d,
    k_hi,
    k_m,
    k_m70,
    k_m79,
    k_s,
    kg,
    km,
    kmin,
    kneg_last,
    ko,
    kp,
    ku_hi,
    ku_lo,
    kurt,
    kw,
    kw_all,
    lam,
    last_wk,
    lin,
    lin3,
    lo_p,
    log_avg,
    log_sum,
    m1,
    m3,
    m70,
    m79,
    m_n,
    m_p,
    mkt,
    mn,
    mu,
    mu3,
    n_cal_weeks,
    n_week,
    names,
    neg,
    neg_1bp,
    only_w,
    over,
    p1,
    pairs,
    pre,
    pts,
    r1_span,
    r2_book,
    r_m,
    r_split,
    r_st,
    ratio,
    rc1,
    rc2,
    rc3,
    rc_res,
    rc_sys,
    rc_u,
    reb,
    res_pairs,
    rho5,
    rho7,
    rho_b,
    s,
    sch,
    se,
    se_m,
    sh1,
    sh2,
    sh3,
    shm,
    shn,
    slopes,
    sp1,
    sp2,
    sp3,
    span_n,
    split,
    spm,
    spn,
    spu,
    stand,
    sw,
    sw3,
    t0,
    tax_i,
    tax_q,
    tb,
    ten,
    to_q,
    v_diag,
    v_new,
    v_res,
    v_sys,
    var_pr,
    var_terms,
    vm,
    vn2,
    vol,
    vol7,
    volu,
    vp,
    vt_u,
    vterm,
    vterm_pr,
    w1,
    w2,
    w3,
    w_span,
    wbh,
    wk_first,
    wk_last,
    wsf,
    x_tr,
    years_wk,
)
from vol5_rules import COMMISSION, TAX, WINDOW, cov0

MD = ROOT / "src" / "lm27.md"
ANCHORS = ROOT / "plans" / "vol-5-anchors.md"
CHARTS = ROOT / "src" / "data"

# ====================================================================== part 1: the anchor lines
OUT: list[str] = []
NEAR: list[str] = []


def put(value: str) -> None:
    """One anchor line; values that f() found near a rounding boundary are listed at its end."""
    tail = f" [NEAR a rounding boundary: {'; '.join(NEAR)}]" if NEAR else ""
    OUT.append(f"A27-{len(OUT) + 1:02d} {value}{tail}")
    NEAR.clear()


def f(x: float, *ks: int, plus: bool = False) -> str:
    """x with max(ks) + 3 decimals; flagged for each printed precision k within 0.1 of a last-digit unit of a boundary."""
    x = float(x)
    for k in ks:
        u = abs(x) * 10**k
        if abs(u - floor(u) - 0.5) < 0.1:
            NEAR.append(f"{x:.{k + 3}f} at {k} dp")
    return f"{x:{'+' if plus else ''}.{max(ks) + 3}f}"


def fl(xs: Iterable[float], *ks: int) -> str:
    return ", ".join(f(float(x), *ks) for x in xs)


put(f"E5 funds {', '.join(F)}; base close {fr.base}; last close {fr.wealth_dates[-1]}; {days} calendar days; "
    f"years {f(fr.years, 4)}")                                                                               # 01
put(f"estimation frame T {T}, {fr.est_dates[0]} .. {fr.est_dates[-1]}; A = T / years = {T} x 365.25 / {days} "
    f"{f(A, 2, 3)}")                                                                                       # 02
put(f"wealth frame {len(fr.wealth_dates)} sessions, {fr.wealth_dates[0]} .. {fr.wealth_dates[-1]}; A_w = "
    f"{len(fr.wealth_dates)} x 365.25 / {days} {f(fr.A_wealth, 2, 3)}; dates in the wealth frame only: "
    f"{', '.join(only_w)} ({len(only_w)}); halted fund-days {len(halted)} ({', '.join(sorted({s for s, _ in halted}))})"
    )                                                                                                      # 03
put(f"0050: close {float(c50['2025-06-10']):.2f} on 2025-06-10, {float(c50['2025-06-18']):.2f} on 2025-06-18 after "
    f"the 4-for-1 split; total return 4 x {float(c50['2025-06-18']):.2f} / {float(c50['2025-06-10']):.2f} - 1 = "
    f"{f(100 * float(r_split), 2, 3)}% (exact fraction {r_split}); flat on the 5 halted sessions")       # 04
put("2025-06-10 -> 2025-06-18 (6 sessions of the wealth frame): fund returns "
    + ", ".join(f"{s_} {f(100 * (float(g) - 1), 2, 3, plus=True)}%" for s_, g in zip(F, G_span, strict=True))
    + f"; 1/N bought at the 06-10 close {f(100 * eq_span, 2, 3)}%; exp(mean log) - 1 {f(100 * log_avg, 2, 4)}% "
    f"(mean log {f(log_sum, 4, 5)}; exp(0.02524) - 1 = {f(100 * (np.exp(0.02524) - 1), 2, 3)}%); R1 (wealth path) "
    f"{f(100 * r1_span, 2, 1)}%")                                                                          # 05
put("growth factor, wealth frame vs estimation frame: "
    + "; ".join(f"{s_} {f(float(a), 3, 4)} vs {f(float(b), 3, 4)}" for s_, a, b in zip(F, gw, ge, strict=True))
    + f"; 0050 total return {f(100 * (gw[0] - 1), 1)}% (lm07.md:36 prints +767.3%)")                      # 06
put(f"LM7's pair: {len(P)} returns between common closes, A {f(A7, 4)} (lm07.md:45: 2,363; lm08.md:284: A = "
    f"243.0543); corr {f(rho7, 4, 2)} (lm08.md:284: -0.1056; lm07.md:50: -0.11); vols {fl(100 * vol7, 2, 1)}% "
    f"(lm08.md:284: 20.11%, 13.50%); E5 estimation frame corr {f(rho5, 4, 3)} on {T} returns, without "
    f"2025-06-18")                                                                                         # 07
put(f"annualized volatilities (divisor T, A {f(A, 2)}) {fl(100 * vol, 2, 1)}%; annualized means A x mean "
    f"{fl(100 * mu, 2)}%")                                                                                 # 08
put("daily correlations " + "; ".join(f"{F[a]}-{F[b]} {f(Cd[a, b], 2, 3, 4)}" for a in range(N)
                                      for b in range(a + 1, N)))                                         # 09
put(f"weekly: {len(kw)} ISO weeks {kw[0]} .. {kw[-1]}; monthly: {len(km)} calendar months {km[0]} .. {km[-1]} (the "
    f"first and last period, in which the sample starts and ends, dropped); keeping the last week ({kw_all[-1]}: "
    f"{last_wk[0]} .. {last_wk[-1]}, {len(last_wk)} sessions) would give {len(kw) + 1} weeks and weekly correlations "
    f"0050-00646 {f(Ck[0, J['00646']], 3)}, 0050-00679B {f(Ck[0, J['00679B']], 3)}")                  # 10
rows = []
for a, b in pairs[:4]:
    cells = [f"{nm} {f(se[a, b, nm][0], 3, 2)} (SE {f(se[a, b, nm][1], 3)} normal, {f(se[a, b, nm][2], 3)} plug-in)"
             for nm in frq]
    rows.append(f"{F[a]}-{F[b]}: " + ", ".join(cells))
c79 = [f(se[a9, b9, nm][0], 3, 2) for nm in frq]
s79 = [f"{f(se[a9, b9, nm][1], 3)}, {f(se[a9, b9, nm][2], 3)}" for nm in frq]
put("; ".join(rows) + f"; 00679B-00642U daily, weekly, monthly {', '.join(c79)} (SE normal, plug-in: "
    f"{'; '.join(s79)}); daily plug-in over normal-theory SE, five pairs: {f(ratio[lo_p], 1, 2)} "
    f"({F[lo_p[0]]}-{F[lo_p[1]]}) to {f(ratio[hi_p], 1, 2)} ({F[hi_p[0]]}-{F[hi_p[1]]}); of the five pairs, largest "
    f"daily-weekly gap {F[kg[0]]}-{F[kg[1]]} {f(gap[kg], 3)} = {f(g_n[kg], 1)} weekly normal-theory SEs, "
    f"{f(g_p[kg], 1)} plug-in SEs (of the five pairs, no daily-weekly gap reaches 2 weekly SEs of either kind); "
    f"daily-monthly gaps in monthly normal-theory and plug-in SEs: {dm_list}; of the five pairs, at 2 or more "
    f"normal-theory SEs only {F[a9]}-{F[b9]}: gap {f(gap_m[a9, b9], 4)} from the unrounded correlations (the "
    f"two-decimal ones give {gap_2dp:.2f}) = {f(m_n[a9, b9], 1)} normal-theory SEs ({f(se[a9, b9, 'monthly'][1], 4)}),"
    f" {f(m_p[a9, b9], 1)} plug-in SEs ({f(se[a9, b9, 'monthly'][2], 4)}); its weekly-monthly gap "
    f"{gap_wm[a9, b9]:.6f} = {gap_wm[a9, b9] / se[a9, b9, 'monthly'][1]:.4f} and "
    f"{gap_wm[a9, b9] / se[a9, b9, 'monthly'][2]:.4f}; largest monthly plug-in SE "
    f"{f(se[kp[0], kp[1], 'monthly'][2], 2)} ({F[kp[0]]}-{F[kp[1]]}); " + ten)                           # 11
cells = []
fsp: dict[str, tuple[float, np.ndarray]] = {}
for nm, x in frq.items():
    sp_, _, _, _, sh_ = split(cov0(x), w1)
    fsp[nm] = (sp_ * sqrt(Afreq[nm]), sh_)
    cells.append(f"{nm} vol {f(100 * sp_ * sqrt(Afreq[nm]), 2)}%, 00642U share {f(100 * sh_[J['00642U']], 1)}%, "
                 f"0050 share {f(100 * sh_[0], 1)}%")
    if nm == "weekly":
        cells[-1] += f" (vol {f(100 * sp_ * sqrt(365.25 / 7), 2)}% with A = 365.25 / 7)"
put(f"R1's weights by frequency (A = {f(A, 2)}, {f(A_week, 2)}, 12; weekly A = {len(kw)} weeks with a session over "
    f"{f(years_wk, 4)} years from the close of {c_before}, before the first weekly return, to that of {c_last} "
    f"({days_wk} days, the span of the {n_cal_weeks} calendar weeks {wk_first} .. {wk_last}) = {len(kw)} x 365.25 / "
    f"{days_wk}): " + "; ".join(cells))                                                                    # 12
put(f"R1 weights 1/5: s_p {f(100 * sp1, 1, 2, 3)}%; w's {f(100 * sw, 2)}%; ratio w's / s_p {f(sw / sp1, 3, 2)}; "
    f"variance terms {f(100 * var_terms, 1)}% of the variance, covariance terms {f(100 * (1 - var_terms), 1)}%")  # 13
put(f"R1 Cov(R_i, R_p) x A {fl(1e4 * covp, 2)} (%^2); beta_(i,p) {fl(b1, 3)}; sum w_i beta_(i,p) "
    f"{float(w1 @ b1):.15f}")                                                                              # 14
put(f"R1 MRC {fl(100 * m1, 2)}% ; RC {fl(100 * rc1, 2)}% (sum {f(100 * rc1.sum(), 2)}%); shares {fl(100 * sh1, 1)}%"
    f" (sum {f(100 * sh1.sum(), 1)}%)")                                                                   # 15
put(f"R1 other splits: stand-alone w_i s_i / w's {fl(100 * stand, 1)}%; variance terms w_i^2 s_i^2 / s_p^2 "
    f"{fl(100 * vterm, 1, 3)}% (sum {f(100 * vterm.sum(), 1, 3)}%; the three-decimal parts sum to "
    f"{sum(round(100 * float(v), 3) for v in vterm):.3f}); from the printed volatilities (two decimals) and "
    f"{var_pr:.2f}: {fl(vterm_pr, 3)}% (sum {f(float(vterm_pr.sum()), 3)}%)")                                # 16
put(f"R2 weights {fl(100 * w2, 0)}%: s_p {f(100 * sp2, 2)}%; w's {f(100 * float(w2 @ vol), 2)}%; ratio "
    f"{f(float(w2 @ vol) / sp2, 3, 2)}; beta_(i,p) {fl(b2, 3)}; RC {fl(100 * rc2, 2)}%; shares {fl(100 * sh2, 1)}%")  # 17
put(f"OLS slope of w_i R_i on R_p (R1, full sample) minus w_i beta_(i,p): max |diff| "
    f"{np.abs(slopes - sh1).max():.1e}; sum of slopes {slopes.sum():.15f}")                                # 18
put(f"R1, 5 points from 00642U to 00679B: linear change (MRC difference x 0.05) {f(100 * lin, 2, 3)} points; exact "
    f"by (10.9) {f(100 * (sqrt(v_new) - sp1), 2, 3)} points; s_p {f(100 * sp1, 2)}% -> {f(100 * sqrt(v_new), 2)}%; "
    f"variance {f(1e4 * sp1**2, 2)} -> {f(1e4 * v_new, 2)} (%^2), linear term {f(1e4 * 2 * float(dlt @ SA @ w1), 2)}, "
    f"quadratic {f(1e4 * float(dlt @ SA @ dlt), 2)}")                                                     # 19
put(f"{len(sch)} windows of {WINDOW} rows (signals {sch[0][0]} .. {sch[-1][0]}); R1's 00642U share "
    f"{f(100 * SH[:, k6].min(), 1)}% ({sch[int(SH[:, k6].argmin())][0]}) to {f(100 * SH[:, k6].max(), 1)}% "
    f"({sch[int(SH[:, k6].argmax())][0]}); 0050 {f(100 * SH[:, 0].min(), 1)}% to {f(100 * SH[:, 0].max(), 1)}%; "
    f"00679B negative in {len(neg)} windows ({neg[0]} .. {neg[-1]}), lowest {f(100 * SH[:, J['00679B']].min(), 2)}% "
    f"({sch[int(SH[:, J['00679B']].argmin())][0]}), highest {f(100 * SH[:, J['00679B']].max(), 1)}%; "
    f"{span_n} windows from {neg[0]} to {neg[-1]}, the last negative share {f(100 * SH[kneg_last, J['00679B']], 4)}%; "
    f"below -0.01% in {len(neg_1bp)} windows, the last {neg_1bp[-1]}; counted with the guard 1e-12, smallest "
    f"|00679B share| {f(100 * m79, 4)}% ({sch[k_m79][0]})")                                                # 20
put(f"first window {fr.est_dates[first_rows - WINDOW]} .. {fr.est_dates[first_rows - 1]}: R1 shares "
    f"{fl(100 * SH[0], 1)}%")                                                                              # 21
put(f"window through {sch[kmin][0]} ({fr.est_dates[sch[kmin][2] - WINDOW]} .. {fr.est_dates[sch[kmin][2] - 1]}): "
    f"R1 s_p {f(100 * spn, 2)}%; 00679B corr with the book {f(rho_b, 3)}, beta_(i,p) {f(bn[J['00679B']], 3, 4)}, MRC "
    f"{f(100 * mn[J['00679B']], 2)}%, share {f(100 * shn[J['00679B']], 2)}%; 00642U share "
    f"{f(100 * shn[k6], 1)}%; 5 points from 00642U to 00679B: s_p -> {f(100 * vn2, 2)}%; MRC by fund "
    f"{fl(100 * mn, 2)}% (every fund but 00679B positive)")                                              # 22
put(f"first purchase {t0.trade} (signal {t0.signal}): from cash 1, TO {f(t0.turnover, 2)}, W_post = 1 / (1 + 0.001425) "
    f"{f(W_first, 6)}, cost {f(100 * t0.cost, 4, 2)}% of W_pre; the same for R2")                             # 23
put(f"R1's trade on {tb.trade} (signal {tb.signal}; the largest one-way turnover of {len(reb)} rebalances): "
    f"W_pre {f(W_pre, 6)}, drift weights {fl(100 * drift, 2, 3)}%, TO {f(100 * tb.turnover, 2, 3)}%, W_post "
    f"{f(W_post, 6)}, "
    f"cost {f(100 * tb.cost, 4, 5)}% of W_pre ({f(1e6 * tb.cost, 0)} NT$ per NT$1 million); approximation "
    f"2 x 0.1425% x TO + tax on sales {f(100 * approx, 4, 5)}%")                                          # 24
put(f"cost per unit of turnover, a rebalance of weights summing to 1 (approximation): 2 x 0.1425% = "
    f"{f(200 * COMMISSION, 3)}% with no taxed sale, up to {f(200 * COMMISSION + 0.1, 3)}% when every sale is taxed")  # 25
ext = "; ".join(f"{s_} {f(100 * wbh[:, j].min(), 1)}% ({dbh[int(wbh[:, j].argmin())]}) to "
                f"{f(100 * wbh[:, j].max(), 1)}% ({dbh[int(wbh[:, j].argmax())]})" for j, s_ in enumerate(F))
put(f"buy-and-hold from 1/N at the close of {t0.trade}: weights on {dbh[-1]} {fl(100 * wbh[-1], 1, 3)}% (the "
    f"three-decimal weights sum to {sum(round(100 * float(x), 3) for x in wbh[-1]):.3f}); range {ext}; "
    f"{len(dbh) + 1} dates with the purchase date; thinned for X2 to {len(pts)} points ({n_week} last sessions of ISO "
    f"weeks, the purchase date and the extremes); from 1/N at the base close {fr.base}: {fl(100 * g0 / g0.sum(), 1)}%")  # 26
put(f"U28 T {len(mkt)} ({s.dates[0]} .. {s.dates[-1]}), A {f(s.A, 4)}; Semiconductor's weight in a 50/50 "
    f"buy-and-hold mix with FinancialInsurance: {f(wsf[-1], 3)} on {s.dates[-1]}, low {f(wsf.min(), 3)} "
    f"({s.dates[int(wsf.argmin())]}), high {f(wsf.max(), 3)} ({s.dates[int(wsf.argmax())]}) (lm09.md:437)")  # 27
put(f"U28 equal-weight book: s_p {f(100 * sqrt(Au * vp), 2)}% (lm10.md:36: 15.75%); TAIEX {f(100 * sqrt(Au * vm), 2)}% "
    f"(lm10.md:41: 17.82%); market betas {f(beta.min(), 3)} ({names[int(beta.argmin())]}) to {f(beta.max(), 3)} "
    f"({names[int(beta.argmax())]}); book beta w'beta {f(bp, 4, 3)}; systematic {f(100 * v_sys / vp, 1, 3)}% of the "
    f"variance (R-squared of the book on TAIEX {f(100 * r2_book, 1, 3)}%), residual {f(100 * v_res / vp, 1, 3)}%: "
    f"diagonal {f(100 * v_diag / vp, 1, 3)}%, off-diagonal {f(100 * (v_res - v_diag) / vp, 1, 3)}%")       # 28
put(f"U28 book volatilities: systematic part {f(100 * sqrt(Au * v_sys), 1, 2)}%, residual part "
    f"{f(100 * sqrt(Au * v_res), 1, 2)}%; with the residual covariances set to 0 "
    f"{f(100 * sqrt(Au * (v_sys + v_diag)), 2)}% against {f(100 * sqrt(Au * vp), 2)}%")                   # 29
put(f"U28 shares (RC / s_p): Semiconductor {f(100 * rc_u[k_s] / spu, 2)}% = systematic "
    f"{f(100 * rc_sys[k_s] / spu, 2)}% + residual {f(100 * rc_res[k_s] / spu, 2)}%; largest {names[ku_hi]} "
    f"{f(100 * rc_u[ku_hi] / spu, 2)}%, smallest {names[ku_lo]} {f(100 * rc_u[ku_lo] / spu, 2)}% "
    f"(1/28 = {f(100 / 28, 2)}%); negative residual parts: {int((rc_res < 0).sum())} of 28")              # 30
put(f"U28 mean of the 28 volatilities {f(100 * volu.mean(), 2)}% (lm10.md:41: 21.94%); ratio w's / s_p "
    f"{f(volu.mean() / sqrt(Au * vp), 3)}; E5's R1 {f(sw / sp1, 3)}; U28 variance terms {f(100 * vt_u / vp, 1)}% of "
    f"the variance, covariance terms {f(100 * (1 - vt_u / vp), 1)}%, variance terms alone a volatility of "
    f"{f(100 * sqrt(Au * vt_u), 2)}% (lm10.md:220: 92.8%, 7.2%, 4.22%)")                                   # 31
put(f"(11.4) for R1 on E5 (annualized S): eigenvalues {fl(1e4 * lam[::-1], 2)} (%^2); |w|^2 = 1/5, so "
    f"{f(1e4 * lam[0] / N, 2)} <= s_p^2 = {f(1e4 * sp1**2, 2)} <= {f(1e4 * lam[-1] / N, 2)} (%^2)")       # 32
put("widget matrix A S (daily, full sample, decimals): "
    + "; ".join(" ".join(f"{SA[a, b]:.10f}" for b in range(N)) for a in range(N))
    + f"; initial state R1: s_p {f(100 * sp1, 2)}%, shares {fl(100 * sh1, 1)}%")                          # 33
put(f"np.cov's default divisor T - 1: volatility ratio sqrt(T/(T-1)) = {f(sqrt(Tu / (Tu - 1)), 6)} at T = {Tu}; "
    f"R1's s_p {f(100 * sp1, 3, 4)}% -> {f(100 * sp1 * sqrt(Tu / (Tu - 1)), 3, 4)}%")                      # 34
put(f"P1: 50/50, returns +10% and -5%: R_p {f(2.5, 2)}%; drifted weight 0.55 / 1.025 = {f(0.55 / 1.025, 3, 4)}")  # 35
put(f"P2: E5's taxes, pre-trade weights {fl(pre, 2)}, target 1/N: TO {f(to_q, 2)}; approximation "
    f"{f(100 * ap_q, 4)}% of W; exact {f(100 * (1 - Wq), 4)}%; distractors {f(100 * 2 * COMMISSION * to_q, 4)}% "
    f"(no tax), {f(100 * (4 * COMMISSION * to_q + tax_q), 4)}% (commission on twice the trades)")           # 36
put(f"P3: 50/50 bought and held, growth factors {g_hi} and {g_lo}: R_p {f(100 * (0.5 * g_hi + 0.5 * g_lo - 1), 2)}%; "
    f"exp(mean log) - 1 {f(100 * (sqrt(g_hi * g_lo) - 1), 2)}%; mean log {f(100 * 0.5 * np.log(g_hi * g_lo), 2)}%")  # 37
sd3 = np.sqrt(np.diag(S3))
put(f"P4: sigma (20%, 10%, 30%), rho12 0.2, rho13 0.6, rho23 -0.2, w (0.4, 0.4, 0.2): sigma_p {f(100 * sp3, 2)}%; "
    f"MRC {fl(100 * m3, 2)}%; RC {fl(100 * rc3, 2)}%; shares {fl(100 * sh3, 1)}%; stand-alone shares "
    f"{fl(100 * w3 * sd3 / float(w3 @ sd3), 1)}%; variance-term shares {fl(100 * w3**2 * sd3**2 / sp3**2, 1)}%")  # 38
put(f"P10: same inputs, with annual means (8%, 4%, 10%): mu_p {f(100 * float(w3 @ mu3), 2)}%; w's {f(100 * sw3, 2)}%; "
    f"ratio w's / sigma_p {f(sw3 / sp3, 2)} (the printed 18 / 13.30 = {f(18 / 13.30, 2, 4)}); 5 points from asset 3 "
    f"to asset 2: linear {f(100 * lin3, 2, 3)} points, exact {f(100 * ex3, 2, 3)} points; sigma_p -> "
    f"{f(100 * (sp3 + ex3), 2)}%")                                                                         # 39
put(f"P6: 0050-00646 monthly rho {f(r_m, 3, 4)} on T = {len(km)}; the stem's rho {r_st:.4f}: normal-theory SE "
    f"(1 - rho^2) / sqrt(T) {f((1 - r_st**2) / sqrt(len(km)), 4)} (from the unrounded rho {f(se_m, 4)}); distractors "
    f"1 / sqrt(T) {f(1 / sqrt(len(km)), 4)}, (1 - rho^2) / T {f((1 - r_st**2) / len(km), 4)}")             # 40
put(f"detail of A27-24, per fund ({', '.join(F)}), % of W_pre: target {fl(100 * tb.target, 2)}; trade "
    f"{fl(100 * x_tr, 4)}; commission {fl(100 * com_i, 5)}; tax {fl(100 * tax_i, 5)}; totals commission "
    f"{f(100 * com_i.sum(), 5)}, tax {f(100 * tax_i.sum(), 5)}, cost {f(100 * (com_i.sum() + tax_i.sum()), 4)}")  # 41
put(f"1/N at the close of 2025-06-10, weights at the close of 2025-06-18 without a trade: {fl(100 * w_span, 2)}%")  # 42
put(f"switching NT$1,000,000 (approximation, no cost on the cost): 00679B -> 0050 "
    f"{f(2 * COMMISSION * 1e6, 0)} NT$; 0050 -> 00679B {f(2 * COMMISSION * 1e6 + TAX['0050'] * 1e6, 0)} NT$")  # 43
put(f"A27-24's trade on a book of NT$10,000,000 before the trade: holdings {fl(B * drift, 0)}; trades "
    f"{fl(B * x_tr, 0)}; commission by fund {fl(B * com_i, 0)}, tax by fund {fl(B * tax_i, 0)}; commission "
    f"{f(B * com_i.sum(), 0)}, tax {f(B * tax_i.sum(), 0)}, cost "
    f"{f(B * tb.cost, 0)} NT$; after the trade {f(B * W_post / W_pre, 0)} NT$, {f(B * W_post / W_pre / 5, 0)} in "
    f"each fund (whole NT$ in X3)")                                                                        # 44
put("R2's shares in the 92 windows: "
    + "; ".join(f"{s_} {f(100 * SH2[:, j].min(), 1)}% ({sch[int(SH2[:, j].argmin())][0]}) to "
                f"{f(100 * SH2[:, j].max(), 1)}% ({sch[int(SH2[:, j].argmax())][0]})" for j, s_ in enumerate(F[:4]))
    + f"; 00642U 0 (weight 0); 0050 above 70% in {len(over)} windows ({over[0]} .. {over[-1]}), counted with the "
    f"guard 1e-12, smallest |0050 share - 70%| {f(100 * m70, 3)} points ({sch[k_m70][0]})")                 # 45
put("withdrawn (it checked the shared decision's note on its first figures, which the decisions on the third "
    "revision dropped; the ID is kept so that later IDs do not move)")                                    # 46
put(f"mu_p = w'mu (A x mean, estimation frame): R1 {f(100 * float(w1 @ mu), 2)}%, R2 {f(100 * float(w2 @ mu), 2)}%")  # 47
put(f"widget matrix 12 S (monthly, {len(km)} calendar months, decimals): "
    + "; ".join(" ".join(f"{SM[a, b]:.10f}" for b in range(N)) for a in range(N))
    + f"; R1: s_p {f(100 * spm, 2)}%, shares {fl(100 * shm, 1)}%")                                        # 48
put(f"widget matrix A S (daily, window {fr.est_dates[sch[kmin][2] - WINDOW]} .. {fr.est_dates[sch[kmin][2] - 1]}, "
    f"A = {f(A, 2)}, decimals): " + "; ".join(" ".join(f"{Sn[a, b]:.10f}" for b in range(N)) for a in range(N))
    + f"; R1: s_p {f(100 * spn, 2)}%, shares {fl(100 * shn, 1)}%")                                        # 49
put("raw kurtosis (19.3), divisor T, estimation frame: "
    + "; ".join(f"{nm} " + ", ".join(f"{F[j]} {kurt[nm][j]:.4f}" for j in range(N)) for nm in frq)
    + f"; largest daily and monthly 00642U ({f(float(k_d[J['00642U']]), 1)}, {f(float(k_m[J['00642U']]), 1)}), "
    f"largest weekly {k_hi['weekly']}; the other four daily {f(float(k_d[ko].min()), 1)} to "
    f"{f(float(k_d[ko].max()), 1)}, monthly {f(float(k_m[ko].min()), 1)} to {f(float(k_m[ko].max()), 1)}")  # 50


def anchor_rows() -> dict[str, str]:
    rows_: dict[str, str] = {}
    sec = ANCHORS.read_text(encoding="utf-8").split("\n## LM27", 1)[1].split("\n## ", 1)[0]
    for line in sec.splitlines():
        if line.startswith("| A27-"):
            c = [x.strip() for x in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
            rows_[c[0]] = c[3].strip("`").replace("\\|", "|")
    return rows_


AN = anchor_rows()
assert len(AN) == 50 and len(OUT) == 50, (len(AN), len(OUT))
ANCHOR_DIFFS = []
for line in OUT:
    aid, val = line.split(" ", 1)
    if AN[aid] != val:
        ANCHOR_DIFFS.append(f"{aid}:\n      script {val}\n      anchor {AN[aid]}")
print(f"part 1: {len(OUT)} anchor lines rebuilt, {len(OUT) - len(ANCHOR_DIFFS)} equal to the anchor table")


# ====================================================================== part 2: the text
def norm_text(t: str) -> str:
    """The module text with TeX thousands separators, escaped percent and dollar signs, \\text{} and minus signs made
    plain."""
    t = t.replace("{,}", ",").replace("\\%", "%").replace("\\$", "$").replace("\u2212", "-").replace("\\,", "")
    return re.sub(r"\\text\{\s*([^}]*)\}", r" \1", t)


RAW = MD.read_text(encoding="utf-8")
TEXT = norm_text(RAW)
N_CHECKS = 0
COVERED: set[str] = set()
FLAGS: list[str] = []


def in_text(printed: str) -> bool:
    """The printed number appears as a whole number (2.323 is not inside 2.3235, 0.32 not inside 10.32)."""
    return re.search(r"(?<![\d.])" + re.escape(printed) + r"(?![\d])", TEXT) is not None


def tie(value: float, fmt: str) -> bool:
    m = re.search(r"\.(\d+)", fmt)
    d = int(m.group(1)) if m else 0
    scaled = abs(value) * 10**d
    return abs(scaled - math.floor(scaled) - 0.5) < 1e-6


def chk(label: str, value: float, fmt: str, printed: str, in_md: bool = True) -> None:
    global N_CHECKS
    got = format(value, fmt)
    print(f"CHECK {label}: {got} (printed {printed})")
    assert got == printed, (label, got, printed)
    assert not tie(value, fmt), ("rounding tie: print more digits", label, value)
    assert not in_md or in_text(printed), f"{label}: {printed!r} not found in src/lm27.md"
    COVERED.add(printed.lstrip("-+"))
    N_CHECKS += 1
    flag(label, value, fmt)


def flag(label: str, value: float, fmt: str) -> None:
    m = re.search(r"\.(\d+)", fmt)
    d = int(m.group(1)) if m else 0
    y = abs(value) * 10**d
    if abs(y - math.floor(y) - 0.5) < 0.1:
        FLAGS.append(f"{label}: {value:.{d + 3}f} lies within a tenth of a unit of a boundary at {d} decimals")


def has(label: str, text: str) -> None:
    global N_CHECKS
    assert text in TEXT, f"{label}: {text!r} not found in src/lm27.md"
    print(f"CHECK {label}: '{text[:80]}' in text")
    for num in re.findall(r"\d[\d,]*\.?\d*", text):
        COVERED.add(num.rstrip(".,"))
    N_CHECKS += 1


MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


def dlong(d: str) -> str:
    """2025-06-18 -> '18 June 2025'."""
    x = date.fromisoformat(d)
    return f"{x.day} {MONTHS[x.month - 1]} {x.year}"


# ---------------------------------------------------------------- front matter and case
i0050, i46, i79, i35, i42 = (J[s_] for s_ in F)
end_w = wbh[-1]
chk("overview/case: 0050's end weight", 100 * end_w[i0050], ".1f", "48.6")
chk("overview/case: R1's largest one-way turnover", 100 * tb.turnover, ".2f", "8.06")
chk("overview/case: its cost", 100 * tb.cost, ".3f", "0.031")
chk("overview: NT$3,100", B * tb.cost, ",.0f", "3,100")
chk("overview: 2,362 joint dates", T, ",d", "2,362")
chk("overview: 2,368 sessions", len(fr.wealth_dates), ",d", "2,368")
chk("overview: 0050-00679B daily", se[0, i79, "daily"][0], ".3f", "-0.105")
chk("overview: 0050-00679B monthly", se[0, i79, "monthly"][0], ".3f", "-0.013")
chk("overview/case: 00642U's share", 100 * sh1[i42], ".1f", "45.9")
chk("overview/case: 00679B's share", 100 * sh1[i79], ".1f", "2.6")
chk("overview: negative windows", len(neg), "d", "22")
chk("overview: 92 windows", len(sch), "d", "92")
chk("overview: U28 systematic share", 100 * v_sys / vp, ".1f", "83.4")
has("overview: residual covariances dominate", "most of the residual part comes from residual covariances")
assert v_res - v_diag > v_diag
has("overview: 0.285", "about 0.285% of its one-way turnover")
chk("case: lowest volatility", 100 * vol.min(), ".2f", "13.49")
chk("case: highest volatility", 100 * vol.max(), ".2f", "37.43")
assert F[int(vol.argmax())] == "00642U" and F[int(vol.argmin())] == "00679B"
chk("case: R1's volatility", 100 * sp1, ".2f", "11.49")
chk("case: 91 resets", len(reb), "d", "91")
assert reb[int(np.argmax([t.turnover for t in reb]))].trade == "2026-04-01"
has("case: the date of the largest reset", "on 1 April 2026, traded 8.06% of the book")
assert tb.trade == "2026-04-01" and tb.signal == "2026-03-31" and t0.trade == "2019-03-04"
has("case: the purchase date", "Bought on 4 March 2019 and held, 0050 grew to 48.6% of the book by 8 October 2026")

# X1: the table rows, built from the values
idx_names = {"0050": "FTSE TWSE Taiwan 50", "00646": "S&P 500", "00679B": "ICE US Treasury 20+ Year",
             "00635U": "S&P GSCI Gold Excess Return", "00642U": "S&P GSCI Crude Oil Enhanced Excess Return"}
for j, s_ in enumerate(F):
    sh2_txt = "0" if w2[j] == 0 else f"{100 * sh2[j]:.1f}%"
    row = (f"| {s_} | {idx_names[s_]} | {100 * vol[j]:.2f}% | {100 * w1[j]:.0f}% | {100 * sh1[j]:.1f}% | "
           f"{100 * w2[j]:.0f}% | {sh2_txt} |")
    has(f"X1 row {s_}", row)
    chk(f"X1 {s_} volatility", 100 * vol[j], ".2f", f"{100 * vol[j]:.2f}")
    chk(f"X1 {s_} R1 share", 100 * sh1[j], ".1f", f"{100 * sh1[j]:.1f}")
    if w2[j]:
        chk(f"X1 {s_} R2 share", 100 * sh2[j], ".1f", f"{100 * sh2[j]:.1f}")
assert abs(sh2[i42]) < 1e-15
has("X1 book volatility", f"| The book's volatility | | | | {100 * sp1:.2f}% | | {100 * sp2:.2f}% |")
has("X1 weighted average", f"| Weighted average volatility | | | | {100 * sw:.2f}% | | {100 * float(w2 @ vol):.2f}% |")
has("X1 ratio", f"| Their ratio, (27.7) | | | | {sw / sp1:.2f} | | {float(w2 @ vol) / sp2:.2f} |")
chk("X1 R2 volatility", 100 * sp2, ".2f", "11.17")
chk("X1 R1 weighted average", 100 * sw, ".2f", "20.75")
chk("X1 R2 weighted average", 100 * float(w2 @ vol), ".2f", "16.97")
chk("X1 R1 ratio", sw / sp1, ".2f", "1.81")
chk("X1 R2 ratio", float(w2 @ vol) / sp2, ".2f", "1.52")
chk("A, estimation frame", A, ".3f", "242.951")
assert sum(round(100 * float(x), 1) for x in sh1) == 100.0
assert abs(sum(round(100 * float(x), 1) for x in sh2) - 100.0) < 1e-9

# ---------------------------------------------------------------- section 2
chk("LM9's drift, end", wsf[-1], ".3f", "0.858")
has("LM9's drift", "drifted from 0.50 to 0.858")
for j, s_ in enumerate(F):
    chk(f"X2 end weight {s_}", 100 * end_w[j], ".3f", f"{100 * end_w[j]:.3f}")
assert abs(sum(round(100 * float(x), 3) for x in end_w) - 100.0) < 1e-9          # sums to 100.000 as printed
has("X2 end weights in order", "it had 48.619%, 19.734%, 5.422%, 14.513% and 11.712% in the five funds")


def ext_of(j: int, kind: str) -> tuple[float, str]:
    k = int(wbh[:, j].argmax() if kind == "max" else wbh[:, j].argmin())
    return 100 * float(wbh[k, j]), dbh[k]


for (s_, kind, printed, when) in [("0050", "min", "19.1", "15 August 2019"), ("0050", "max", "49.1", "1 July 2026"),
                                  ("00642U", "max", "21.3", "23 April 2019"), ("00642U", "min", "7.0", "2 November 2020"),
                                  ("00679B", "max", "28.0", "23 March 2020")]:
    v_, d_ = ext_of(J[s_], kind)
    chk(f"X2 {s_} {kind}", v_, ".1f", printed)
    assert dlong(d_) == when, (s_, kind, d_)
    has(f"X2 {s_} {kind} date", when)
chk("X2 points", len(pts), "d", "402")
# the chart carries every cited extreme and the end weights (AUTHORING section 7)
X2 = json.loads((CHARTS / "lm27-drift.json").read_text(encoding="utf-8"))
assert len(X2["x"]["values"]) == 402 and X2["x"]["values"][-1] == "2026-10-08"
for sr in X2["series"]:
    j = J[sr["name"]]
    assert round(max(sr["y"]), 6) == round(float(wbh[:, j].max()), 6) and round(min(sr["y"]), 6) == round(
        float(wbh[:, j].min()), 6) and round(sr["y"][-1], 6) == round(float(end_w[j]), 6), sr["name"]
# E1
span_pr = [f"{100 * (float(g) - 1):+.3f}" for g in G_span]
assert span_pr == ["+0.864", "-1.689", "-0.792", "+2.226", "+12.816"], span_pr
has("E1 returns", "returned +0.864%, -1.689%, -0.792%, +2.226% and +12.816%")
for j in range(N):
    chk(f"E1 return {F[j]}", 100 * (float(G_span[j]) - 1), "+.3f", span_pr[j])
chk("E1 1/N over the span", 100 * eq_span, ".3f", "2.685")
chk("E1 1/N from the printed returns", sum(float(x) for x in span_pr) / 5, ".3f", "2.685")
chk("E1 mean log", log_sum, ".5f", "0.02524")
chk("E1 exp(mean log) - 1, from the printed 0.02524", 100 * (math.exp(0.02524) - 1), ".2f", "2.56")
chk("E1 exp(mean log) - 1, unrounded", 100 * log_avg, ".2f", "2.56", in_md=False)
chk("E1 R1 over the span", 100 * r1_span, ".2f", "2.73")
last_before = max(t.trade for t in p1.trades if t.trade <= "2025-06-10")
assert last_before == "2025-06-02", last_before
has("E1 R1's last trade", "since its trade of 2 June")
has("domain", "every fund's return exceeds -100%")
assert (fr.W > -1).all()
# KC 2
chk("KC2 book's growth", float(G_span.mean()), ".5f", "1.02685")
chk("KC2 00642U's growth", float(G_span[i42]), ".5f", "1.12816")
chk("KC2 00642U's weight", 100 * w_span[i42], ".2f", "21.97")
chk("KC2 weight from the printed factors", 100 * 0.2 * 1.12816 / 1.02685, ".2f", "21.97", in_md=False)

# ---------------------------------------------------------------- section 3
has("R2's weights", "40% 0050, 20% 00646, 30% 00679B and 10% 00635U")
assert [round(x, 2) for x in w2] == [0.4, 0.2, 0.3, 0.1, 0.0]
has("13:30", "known only after 13:30")
chk("commission", 100 * COMMISSION, ".4f", "0.1425")
chk("tax", 100 * TAX["0050"], ".1f", "0.1")
assert TAX["00679B"] == 0 and all(TAX[s_] == 0.001 for s_ in F if s_ != "00679B")
factor = (COMMISSION + max(TAX.values())) * 1.5
assert factor < 0.004
has("factor below 0.4%", "For E5's rules the factor is below 0.4%.")
chk("cost per unit of turnover, no tax", 200 * COMMISSION, ".3f", "0.285")
chk("cost per unit of turnover, all taxed", 200 * COMMISSION + 0.1, ".3f", "0.385")
# E2
has("E2 equation", "W_t=1-0.001425W_t")
has("E2 root", "W_t=1/1.001425=0.998577")
chk("E2 W after the purchase", W_first, ".6f", "0.998577")
chk("E2 cost", 100 * t0.cost, ".4f", "0.1423")
chk("E2 turnover", t0.turnover, ".1f", "0.5")
assert abs(p1.trades[0].cost - 1 / 1.001425 * 0.001425) < 1e-15
# E3 and X3
for j in range(N):
    chk(f"E3 drift weight {F[j]}", 100 * drift[j], ".3f", f"{100 * drift[j]:.3f}")
has("E3 drift weights", "17.954%, 18.611%, 18.697%, 16.680% and 28.058%")
assert abs(sum(round(100 * float(x), 3) for x in drift) - 100.0) < 1e-9
chk("E3 turnover", 100 * tb.turnover, ".3f", "8.058")
dpr = np.round(100 * drift, 3)
chk("E3 turnover from the printed weights", 0.5 * float(np.abs(dpr - 20).sum()), ".3f", "8.058", in_md=False)
chk("E3 00642U's sale", 100 * (drift[i42] - 0.2), ".3f", "8.058")
assert (drift[:4] < 0.2).all() and drift[i42] > 0.2                                     # only 00642U is sold
chk("E3 approximation", 100 * approx, ".5f", "0.03102")
chk("E3 approximation from the printed inputs", 0.285 * 8.058 / 100 + 0.1 * 8.058 / 100, ".5f", "0.03102", in_md=False)
has("E3 approximation formula", "0.285%\\times8.058%+0.1%\\times8.058%=0.03102%")
chk("E3 exact cost", 100 * tb.cost, ".5f", "0.03100")
chk("E3 NT$ cost", B * tb.cost, ",.0f", "3,100")
has("E3 book", "NT$3,100 on a book of NT$10,000,000")
hold = np.round(B * drift)
trade = np.round(B * x_tr)
after = np.round(B * W_post / W_pre * tb.target)
comm = np.round(B * com_i)
taxs = np.round(B * tax_i)
for j, s_ in enumerate(F):
    row = (f"| {s_} | {hold[j]:,.0f} | {'+' if trade[j] > 0 else '-'}{abs(trade[j]):,.0f} | {after[j]:,.0f} | "
           f"{comm[j]:,.0f} | {taxs[j]:,.0f} |")
    has(f"X3 row {s_}", row)
    assert hold[j] + trade[j] == after[j], s_                                            # each row adds up as printed
    for v_, nm in ((B * drift[j], "holding"), (B * x_tr[j], "trade"), (B * com_i[j], "commission")):
        chk(f"X3 {s_} {nm}", abs(v_), ",.0f", f"{abs(v_):,.0f}")
assert hold.sum() == 1e7 and trade.sum() == -3100 and after.sum() == 9996900 and comm.sum() == 2294 and taxs.sum() == 806
has("X3 total", "| Total | 10,000,000 | -3,100 | 9,996,900 | 2,294 | 806 |")
chk("X3 after the trade", B * W_post / W_pre, ",.0f", "9,996,900")
chk("X3 each fund after", B * W_post / W_pre / 5, ",.0f", "1,999,380")
chk("X3 commission total", B * com_i.sum(), ",.0f", "2,294")
chk("X3 tax", B * tax_i.sum(), ",.0f", "806")
chk("X3 cost", B * (com_i.sum() + tax_i.sum()), ",.0f", "3,100")
chk("X3 note turnover", 100 * tb.turnover, ".2f", "8.06")
chk("rf", 100 * 0.015, ".1f", "1.5")
# KC 3
chk("KC3 switch 00679B -> 0050", 2 * COMMISSION * 1e6, ",.0f", "2,850")
chk("KC3 switch 0050 -> 00679B", 2 * COMMISSION * 1e6 + TAX["0050"] * 1e6, ",.0f", "3,850")
chk("KC3 tax", TAX["0050"] * 1e6, ",.0f", "1,000")
has("KC3 book", "Switching NT$1,000,000 from 00679B to 0050")

# ---------------------------------------------------------------- section 4
has("base close", "base close of 17 January 2017")
assert fr.base == "2017-01-17"
chk("days", days, ",d", "3,551")
chk("years", fr.years, ".4f", "9.7221")
has("A formula", "A=2,362\\times365.25/3,551=242.951")
chk("A_w", fr.A_wealth, ".3f", "243.569")
assert only_w == ["2025-06-11", "2025-06-12", "2025-06-13", "2025-06-16", "2025-06-17", "2025-06-18"]
assert len(halted) == 5 and {x for x, _ in halted} == {"0050"}
has("E4 six dates", "The six dates 11 to 18 June 2025 are in the wealth frame only")
has("E4 split return", "4\\times47.57/188.65-1=0.864%")
assert float(c50["2025-06-10"]) == 188.65 and float(c50["2025-06-18"]) == 47.57
chk("E4 split-day return", 100 * float(r_split), ".3f", "0.864")
chk("E4 00642U wealth frame", float(gw[i42]), ".3f", "1.593")
chk("E4 00642U estimation frame", float(ge[i42]), ".3f", "1.412")
chk("KC4 LM7's pair", len(P), ",d", "2,363")
chk("KC4 LM7's correlation", rho7, ".4f", "-0.1056")
chk("KC4 E5's correlation", rho5, ".3f", "-0.105")
# timing: TWSE and TPEx close at 13:30 Taipei; New York's 4:00 p.m. in Taipei time (IANA data)
for day_, want in (("2025-07-15", 4), ("2025-12-15", 5), ("2026-07-15", 4), ("2026-01-15", 5)):
    ny = datetime.fromisoformat(f"{day_}T16:00").replace(tzinfo=ZoneInfo("America/New_York"))
    assert ny.astimezone(ZoneInfo("Asia/Taipei")).hour == want, day_
has("sessions", "Both markets match orders from 09:00 to 13:30 with a closing call auction from 13:25")
has("NYSE close", "New York's core session ends at 4:00 p.m. (NYSE): 04:00 Taipei time in US summer time, 05:00 otherwise")
chk("weeks", len(kw), "d", "500")
chk("weekly years", years_wk, ".4f", "9.6975")
assert c_before == "2017-01-20" and c_last == "2026-10-02"
has("weekly span", "from the close of 20 January 2017 to that of 2 October 2026")
chk("weekly days", days_wk, ",d", "3,542")
chk("weekly A", A_week, ".2f", "51.56")
chk("weekly A from its formula", 500 * 365.25 / 3542, ".2f", "51.56", in_md=False)
chk("months", len(km), "d", "116")
# X4 note and its chart
X4 = json.loads((CHARTS / "lm27-freq.json").read_text(encoding="utf-8"))
for k, sr in enumerate(X4["series"]):
    nm = sr["name"]
    assert [round(v_, 6) for v_ in sr["values"]] == [round(se[a, b, nm][0], 6) for a, b in pairs], nm
near0 = [k_ for k_ in pairs if abs(se[k_[0], k_[1], "daily"][0]) < 0.15]
assert near0 == [(0, i79), (0, i42)]
for nm, printed in (("daily", "0.02"), ("weekly", "0.045"), ("monthly", "0.09")):
    d = len(printed) - 2
    for a, b in near0:
        assert abs(se[a, b, nm][1] - float(printed)) < 10 ** -d, (nm, a, b)      # "about": within a last-digit unit
has("X4 SEs near zero", "normal-theory standard errors are about 0.02, 0.045 and 0.09")
for nm, pn, pp in (("daily", "0.020", "0.040"), ("weekly", "0.045", "0.053"), ("monthly", "0.093", "0.095")):
    chk(f"X4 0050-00679B normal SE {nm}", se[0, i79, nm][1], ".3f", pn)
    chk(f"X4 0050-00679B plug-in SE {nm}", se[0, i79, nm][2], ".3f", pp)
has("X4 0050-00679B SEs", "(0050–00679B: 0.020, 0.045, 0.093)")
has("X4 0050-00679B plug-in SEs", "(0050–00679B: 0.040, 0.053, 0.095)")
chk("X4 ratio low", ratio[lo_p], ".1f", "1.4")
chk("X4 ratio high", ratio[hi_p], ".1f", "2.4")
# E5
for (a, b), printed in (((0, i79), ("-0.105", "-0.023", "-0.013")), ((0, i46), ("0.599", "0.588", "0.552")),
                        ((0, i35), ("0.180", "0.228", "0.187"))):
    for nm, pr_ in zip(("daily", "weekly", "monthly"), printed, strict=True):
        chk(f"E5 {F[a]}-{F[b]} {nm}", se[a, b, nm][0], ".3f", pr_)
for nm, pr_ in zip(("daily", "weekly", "monthly"), ("-0.18", "-0.20", "-0.36"), strict=True):
    chk(f"E5 00679B-00642U {nm}", se[i79, i42, nm][0], ".2f", pr_)
has("E5 correlations", "0050 correlates -0.105, -0.023 and -0.013 with 00679B, 0.599, 0.588 and 0.552 with 00646, "
                       "and 0.180, 0.228 and 0.187 with 00635U. 00679B–00642U gives -0.18, -0.20 and -0.36.")
chk("E5 00642U daily kurtosis", float(k_d[i42]), ".1f", "26.6")
chk("E5 00642U monthly kurtosis", float(k_m[i42]), ".1f", "12.3")
chk("E5 others daily, low", float(k_d[ko].min()), ".1f", "11.2")
chk("E5 others daily, high", float(k_d[ko].max()), ".1f", "21.0")
chk("E5 others monthly, low", float(k_m[ko].min()), ".1f", "4.3")
chk("E5 others monthly, high", float(k_m[ko].max()), ".1f", "5.7")
assert k_hi["daily"] == k_hi["monthly"] == "00642U"
chk("E5 largest daily-weekly gap", gap[kg], ".3f", "0.082")
assert kg == (0, i79)
chk("E5 that gap in weekly normal SEs", g_n[kg], ".1f", "1.8")
assert all(g_n[k_] < 2 and g_p[k_] < 2 for k_ in pairs)
higher = {k_ for k_ in pairs if se[k_[0], k_[1], "daily"][0] > se[k_[0], k_[1], "weekly"][0]}
assert higher == {(0, i46), (0, i42), (i79, i42)}, higher
has("E5 higher/lower", "The daily figure is higher for 0050–00646, 0050–00642U and 00679B–00642U, and lower for the "
                       "other two")
chk("E5 daily-monthly gap", gap_m[a9, b9], ".4f", "0.1815")
assert round(gap_2dp, 2) == 0.18                                                       # hence "from the unrounded"
has("E5 unrounded", "0.1815 (from the unrounded correlations)")
chk("E5 monthly normal SE", se[a9, b9, "monthly"][1], ".4f", "0.0806")
chk("E5 monthly plug-in SE", se[a9, b9, "monthly"][2], ".4f", "0.0888")
chk("E5 gap in normal SEs", m_n[a9, b9], ".1f", "2.3")
chk("E5 gap in plug-in SEs", m_p[a9, b9], ".1f", "2.0")
chk("E5 multiples from the printed gap and SEs (normal)", 0.1815 / 0.0806, ".1f", "2.3", in_md=False)
chk("E5 multiples from the printed gap and SEs (plug-in)", 0.1815 / 0.0888, ".1f", "2.0", in_md=False)
assert [k_ for k_ in pairs if m_n[k_] >= 2] == [(a9, b9)]
chk("E5 largest monthly plug-in SE", se[kp[0], kp[1], "monthly"][2], ".2f", "0.16")
for nm, pv, ps in (("daily", "11.49", "45.9"), ("weekly", "10.55", "41.9"), ("monthly", "10.02", "45.0")):
    chk(f"E5 R1 vol {nm}", 100 * fsp[nm][0], ".2f", pv)
    chk(f"E5 R1 00642U share {nm}", 100 * fsp[nm][1][i42], ".1f", ps)

# ---------------------------------------------------------------- section 5
for j in range(N):
    chk(f"X5 mean {F[j]}", 100 * mu[j], ".2f", f"{100 * mu[j]:.2f}")
has("X5 means", "| Mean, a year | 24.16% | 14.87% | -0.97% | 9.26% | 10.53% |")
has("X5 volatilities", "| Volatility, a year | 20.10% | 16.12% | 13.49% | 16.60% | 37.43% |")
for a in range(N):
    cells_ = " | ".join("1" if a == b else f"{Cd[a, b]:.2f}" for b in range(N))
    has(f"X5 correlation row {F[a]}", f"| {F[a]} | {cells_} |")
chk("E6 R1 mean", 100 * float(w1 @ mu), ".2f", "11.57")
chk("E6 R1 mean from the printed means", (24.16 + 14.87 - 0.97 + 9.26 + 10.53) / 5, ".2f", "11.57", in_md=False)
chk("E6 R1 variance terms", 100 * var_terms, ".1f", "76.4")
chk("E6 R1 covariance terms", 100 * (1 - var_terms), ".1f", "23.6")
chk("E6 U28 variance terms", 100 * vt_u / vp, ".1f", "7.2")
chk("E6 U28 covariance terms", 100 * (1 - vt_u / vp), ".1f", "92.8")
chk("E6 R1 ratio from the printed volatilities", 20.75 / 11.49, ".2f", "1.81", in_md=False)
chk("E6 R2 mean", 100 * float(w2 @ mu), ".2f", "13.27")
chk("E6 R2 mean from the printed means", 0.4 * 24.16 + 0.2 * 14.87 + 0.3 * -0.97 + 0.1 * 9.26, ".2f", "13.27",
    in_md=False)
has("E6 R2 formula", "0.4\\times24.16%+0.2\\times14.87%")
chk("E6 R2 ratio from the printed volatilities", 16.97 / 11.17, ".2f", "1.52", in_md=False)
chk("E6 U28 mean volatility", 100 * volu.mean(), ".2f", "21.94")
chk("E6 U28 book", 100 * sqrt(Au * vp), ".2f", "15.75")
chk("E6 U28 ratio", volu.mean() / sqrt(Au * vp), ".3f", "1.393")
chk("E6 U28 ratio from the printed volatilities", 21.94 / 15.75, ".3f", "1.393", in_md=False)
# KC 5
chk("KC5 lambda_5", 1e4 * lam[0], ".2f", "118.05")
chk("KC5 lambda_1", 1e4 * lam[-1], ",.2f", "1,429.89")
chk("KC5 lower bound", 1e4 * lam[0] / 5, ".2f", "23.61")
chk("KC5 upper bound", 1e4 * lam[-1] / 5, ".2f", "285.98")
chk("KC5 bounds from the printed eigenvalues", 1429.89 / 5, ".2f", "285.98", in_md=False)
chk("KC5 s_p^2", 1e4 * sp1**2, ".2f", "132.09")
chk("KC5 11.493", 100 * sp1, ".3f", "11.493")
chk("KC5 11.493 squared", 11.493**2, ".2f", "132.09", in_md=False)

# ---------------------------------------------------------------- section 6
cov_pr = [f"{1e4 * float(x):.2f}" for x in covp]
assert cov_pr == ["139.80", "117.05", "17.22", "83.25", "303.13"], cov_pr
has("E7 covariances", "is 139.80, 117.05, 17.22, 83.25 and 303.13 (%²)")
for j in range(N):
    chk(f"E7 covariance {F[j]}", 1e4 * covp[j], ".2f", cov_pr[j])
    chk(f"E7 beta {F[j]}", b1[j], ".3f", f"{b1[j]:.3f}")
    chk(f"E7 beta {F[j]} from the printed covariance", float(cov_pr[j]) / 132.09, ".3f", f"{b1[j]:.3f}", in_md=False)
    chk(f"E7 share {F[j]} from the printed beta", 0.2 * round(float(b1[j]), 3) * 100, ".1f", f"{100 * sh1[j]:.1f}",
        in_md=False)
    chk(f"E7 MRC {F[j]}", 100 * m1[j], ".2f", f"{100 * m1[j]:.2f}")
    chk(f"E7 RC {F[j]}", 100 * rc1[j], ".2f", f"{100 * rc1[j]:.2f}")
has("E7 betas", "1.058, 0.886, 0.130, 0.630 and 2.295")
has("E7 shares", "21.2%, 17.7%, 2.6%, 12.6% and 45.9%")
has("E7 MRC", "12.16%, 10.18%, 1.50%, 7.24% and 26.37%")
has("E7 RC", "2.43, 2.04, 0.30, 1.45 and 5.27 points, summing to 11.49")
assert abs(sum(round(100 * float(x), 2) for x in rc1) - 11.49) < 1e-9              # the printed RCs sum to 11.49
# "from unrounded inputs": the printed covariances over the printed 11.49 move some MRCs
assert any(f"{float(c) / 11.49:.2f}" != f"{100 * m:.2f}" for c, m in zip(cov_pr, m1, strict=True))
for lab_, vals, d, tot in (("Euler", sh1, 1, "100.0"), ("Stand-alone", stand, 1, "100.0"), ("Variance terms", vterm, 3,
                                                                                               "76.400")):
    cells_ = " | ".join(f"{100 * float(x):.{d}f}%" for x in vals)
    assert f"| {cells_} | {tot}% |" in TEXT, lab_
    assert f"{sum(round(100 * float(x), d) for x in vals):.{d}f}" == tot, lab_          # the parts sum as printed
    for x in vals:
        COVERED.add(f"{100 * float(x):.{d}f}")
    COVERED.add(tot)
print("CHECK E7 table: three rows, parts sum as printed")
assert any(f"{x:.3f}" != f"{100 * float(v_):.3f}" for x, v_ in zip(vterm_pr, vterm, strict=True))  # unrounded inputs
chk("E7 weighted average", 100 * sw, ".2f", "20.75")
assert float(np.abs(slopes - sh1).max()) < 1e-15
has("E7 slopes", "equal the shares to about $10^{-16}$, machine precision")
X6 = json.loads((CHARTS / "lm27-shares.json").read_text(encoding="utf-8"))
for sr in X6["series"]:
    j = J[sr["name"]]
    assert [round(v_, 6) for v_ in sr["values"]] == [round(float(x), 6) for x in (w1[j], sh1[j], w2[j], sh2[j])]
# E8
chk("E8 linear prediction", 100 * lin, ".2f", "-1.24")
chk("E8 linear from the printed MRCs", 0.05 * (1.50 - 26.37), ".2f", "-1.24", in_md=False)
lin_term = 1e4 * 2 * float(dlt @ SA @ w1)
quad = 1e4 * float(dlt @ SA @ dlt)
chk("E8 linear term", -lin_term, ".2f", "28.59")
chk("E8 quadratic term", quad, ".2f", "4.42")
chk("E8 new variance", 1e4 * v_new, ".2f", "107.92")
has("E8 sum", "132.09-28.59+4.42=107.92")
assert round(132.09 - 28.59 + 4.42, 2) == 107.92
chk("E8 new volatility", 100 * sqrt(v_new), ".2f", "10.39")
chk("E8 new volatility from the printed variance", sqrt(107.92), ".2f", "10.39", in_md=False)
chk("E8 exact change", 100 * (sp1 - sqrt(v_new)), ".2f", "1.10")
has("E8 path", "falls from 11.49% to 10.39%, by 1.10 points")
# widget block (charts script ran the JavaScript against NumPy): the first draw is R1 at the daily matrix
WJ = json.loads((CHARTS / "lm27-riskSplit.json").read_text(encoding="utf-8"))
Wd = np.array(WJ["widget"]["mats"]["daily"])
assert WJ["widget"]["init"] == {"mat": "daily", "w": [0.2, 0.2, 0.2, 0.2]}
spw, _, _, _, shw = split(Wd, w1)
assert f"{100 * spw:.2f}" == "11.49" and [f"{100 * x:.1f}" for x in shw] == ["21.2", "17.7", "2.6", "12.6", "45.9"]
assert np.allclose(np.array(WJ["widget"]["mats"]["monthly"]), SM, atol=1e-10)
assert np.allclose(np.array(WJ["widget"]["mats"]["window"]), Sn, atol=1e-10)
print("CHECK widget: three matrices to 1e-10; its first draw is R1 at the daily matrix (11.49%, 45.9%)")
# KC 6
chk("KC6 0050's beta in R2", b2[0], ".3f", "1.587")
chk("KC6 0050's share in R2", 100 * sh2[0], ".1f", "63.5")
chk("KC6 share from the printed beta", 0.4 * 1.587 * 100, ".1f", "63.5", in_md=False)

# ---------------------------------------------------------------- section 7
assert sch[kmin][0] == "2020-02-27" and fr.est_dates[sch[kmin][2] - WINDOW] == "2018-01-29"
has("E9 window", "504 joint dates from 29 January 2018 to 27 February 2020")
chk("E9 s_p", 100 * spn, ".2f", "8.13")
chk("E9 correlation", rho_b, ".3f", "-0.067")
chk("E9 beta", bn[i79], ".4f", "-0.0944")
chk("E9 MRC", 100 * mn[i79], ".2f", "-0.77")
chk("E9 MRC from the printed inputs", -0.0944 * 8.13, ".2f", "-0.77", in_md=False)
chk("E9 share", 100 * shn[i79], ".2f", "-1.89")
chk("E9 share from the printed beta", 0.2 * -0.0944 * 100, ".2f", "-1.89", in_md=False)
chk("E9 00642U's share", 100 * shn[i42], ".1f", "54.3")
chk("E9 after the switch", 100 * vn2, ".2f", "7.07")
assert len(neg) == 22 and span_n == 36 and neg[0] == "2019-05-31" and neg[-1] == "2022-04-29"
has("E9 negative windows", "negative in 22 of the 36 windows from May 2019 to April 2022")
chk("E9 36 windows", span_n, "d", "36")
chk("E9 last negative share", 100 * SH[kneg_last, i79], ".4f", "-0.0023")
has("E9 last window", "through 29 April 2022, was -0.0023%")
assert m79 > 1e-12                                                                      # the count's margin
chk("windows: 00642U low", 100 * SH[:, k6].min(), ".1f", "32.7")
chk("windows: 00642U high", 100 * SH[:, k6].max(), ".1f", "54.3")
chk("windows: 0050 low", 100 * SH[:, 0].min(), ".1f", "16.8")
chk("windows: 0050 high", 100 * SH[:, 0].max(), ".1f", "28.6")
assert sch[int(SH[:, k6].argmin())][0] == "2026-02-26" and sch[int(SH[:, k6].argmax())][0] == "2020-02-27"
has("X7 lowest window", "00642U's lowest share is in the window through 26 February 2026")
assert sch[0][0] == "2019-02-27" and fr.est_dates[first_rows - WINDOW] == "2017-02-13"
has("X7 first signal", "one point per month-end signal from 27 February 2019")
has("X7 first window", "The first window, from 13 February 2017, gives 21.7%, 19.3%, 1.1%, 7.7% and 50.2%")
for j in range(N):
    chk(f"X7 first window {F[j]}", 100 * SH[0, j], ".1f", f"{100 * SH[0, j]:.1f}")
X7 = json.loads((CHARTS / "lm27-windows.json").read_text(encoding="utf-8"))
for sr in X7["series"]:
    assert [round(v_, 6) for v_ in sr["y"]] == [round(float(x), 6) for x in SH[:, J[sr["name"]]]]
assert all(mn[j] > 0 for j in range(N) if j != i79)
has("KC7 MRCs", "Its MRC is -0.77% there and the other four MRCs are positive")

# ---------------------------------------------------------------- section 8
chk("E10 lowest beta", beta.min(), ".3f", "0.507")
chk("E10 highest beta", beta.max(), ".3f", "1.207")
chk("E10 book beta", bp, ".3f", "0.807")
for v_, printed in ((v_sys, "83.426"), (v_res, "16.574"), (v_diag, "4.037"), (v_res - v_diag, "12.537")):
    chk(f"E10 share {printed}", 100 * v_ / vp, ".3f", printed)
assert abs(round(100 * v_sys / vp, 3) + round(100 * v_res / vp, 3) - 100) < 1e-9
assert abs(round(100 * v_diag / vp, 3) + round(100 * (v_res - v_diag) / vp, 3) - round(100 * v_res / vp, 3)) < 1e-9
assert abs(r2_book - v_sys / vp) < 1e-12                                                # the R-squared
chk("E10 TAIEX volatility", 100 * sqrt(Au * vm), ".2f", "17.82")
chk("E10 83.4 from the printed inputs", 100 * 0.807**2 * 17.82**2 / 15.75**2, ".1f", "83.4", in_md=False)
chk("E10 diagonal residuals only", 100 * sqrt(Au * (v_sys + v_diag)), ".2f", "14.73")
chk("E10 mean residual correlation", float(res_pairs.mean()), ".3f", "0.112")
assert len(res_pairs) == 378 and v_res - v_diag > 0
assert names[k_s] == "Semiconductor" and rc_res[k_s] < 0 and int((rc_res < 0).sum()) == 1
chk("E10 Semiconductor share", 100 * rc_u[k_s] / spu, ".2f", "3.82")
chk("E10 Semiconductor systematic", 100 * rc_sys[k_s] / spu, ".2f", "4.46")
chk("E10 Semiconductor residual", 100 * rc_res[k_s] / spu, ".2f", "-0.64")
assert round(4.46 - 0.64, 2) == 3.82
has("E10 Semiconductor", "4.46%-0.64%=3.82%")
has("X8 Semiconductor", "| 4.46% - 0.64% = 3.82% |")
chk("X8 systematic volatility", 100 * sqrt(Au * v_sys), ".1f", "14.4")
chk("X8 residual volatility", 100 * sqrt(Au * v_res), ".1f", "6.4")
chk("X8 systematic volatility from the printed", sqrt(0.83426) * 15.75, ".1f", "14.4", in_md=False)
chk("X8 residual volatility from the printed", sqrt(0.16574) * 15.75, ".1f", "6.4", in_md=False)
assert names[ku_hi] == "GlassCeramic" and names[ku_lo] == "CommunicationsInternet"
chk("X8 largest share", 100 * rc_u[ku_hi] / spu, ".2f", "5.21")
chk("X8 smallest share", 100 * rc_u[ku_lo] / spu, ".2f", "1.99")
chk("X8 1/28", 100 / 28, ".2f", "3.57")
chk("X8 U28 T", len(mkt), ",d", "4,382")
chk("X8 U28 A", Au, ".4f", "245.4794")
assert s.dates[0] == "2008-12-02" and s.dates[-1] == "2026-10-08"
has("X8 span", "2 December 2008 to 8 October 2026")
for lab_, val in (("The book's volatility", "15.75%"), ("TAIEX price index's volatility", "17.82%"),
                  ("Systematic share of the variance (= R-squared)", "83.426%"),
                  ("Residual share of the variance", "16.574%"), ("from the residual variances", "4.037%"),
                  ("from the residual covariances", "12.537%"),
                  ("Systematic and residual parts as volatilities", "14.4%, 6.4%"),
                  ("Volatility with residual covariances set to 0", "14.73%"),
                  ("Largest risk share: GlassCeramic", "5.21%"),
                  ("Smallest risk share: CommunicationsInternet", "1.99%"), ("Equal share, 1/28", "3.57%")):
    has(f"X8 row {lab_}", f"| {lab_} | {val} |")

# ---------------------------------------------------------------- section 9, summary, problems
chk("code: A", A, ".3f", "242.951")
chk("code: s_p", sp1, ".5f", "0.11493")
chk("KC9 factor", sqrt(Tu / (Tu - 1)), ".6f", "1.000212")
chk("KC9 new volatility", 100 * sp1 * sqrt(Tu / (Tu - 1)), ".3f", "11.495")
chk("KC9 from the printed inputs", 11.493 * 1.000212, ".3f", "11.495", in_md=False)
# P1
chk("P1 key", 0.55 / 1.025, ".3f", "0.537")
has("P1 options", "**A.** 0.55")
has("P1 option C", "**C.** 0.50")
chk("S1 1.025", 0.5 * 1.1 + 0.5 * 0.95, ".3f", "1.025")
chk("S1 0.475", 0.5 * 0.95, ".3f", "0.475")
# P2
chk("P2 key", 100 * ap_q, ".4f", "0.0385")
chk("P2 exact", 100 * (1 - Wq), ".4f", "0.0385")
chk("P2 no tax", 100 * 2 * COMMISSION * to_q, ".4f", "0.0285")
chk("P2 twice the commission", 100 * (4 * COMMISSION * to_q + tax_q), ".4f", "0.0670")
chk("P2 turnover", to_q, ".2f", "0.10")
has("P2 weights", "0.30, 0.20, 0.15, 0.15 and 0.20 in E5's order")
assert [round(x, 2) for x in pre] == [0.3, 0.2, 0.15, 0.15, 0.2]
# P3
chk("P3 key", 100 * (0.5 * g_hi + 0.5 * g_lo - 1), ".2f", "10.00")
chk("P3 averaged logs", 100 * (sqrt(g_hi * g_lo) - 1), ".2f", "5.83")
chk("P3 mean log", 100 * 0.5 * np.log(g_hi * g_lo), ".2f", "5.67")
chk("S3 mean log as a number", 0.5 * float(np.log(g_hi * g_lo)), ".4f", "0.0567")
chk("S3 growth factor", 0.5 * g_hi + 0.5 * g_lo, ".2f", "1.10")
# P4 and P10
assert np.allclose(C3, [[1, 0.2, 0.6], [0.2, 1, -0.2], [0.6, -0.2, 1]]) and list(w3) == [0.4, 0.4, 0.2]
chk("P4 key", 100 * sh3[0], ".1f", "56.1")
chk("P4 variance term", 100 * w3[0] ** 2 * S3[0, 0] / sp3**2, ".1f", "36.2")
chk("P4 stand-alone", 100 * w3[0] * sd3[0] / float(w3 @ sd3), ".1f", "44.4")
Sw3 = S3 @ w3
chk("S4 (Sigma w)_1", Sw3[0], ".4f", "0.0248")
chk("S4 (Sigma w)_2", Sw3[1], ".4f", "0.0044")
chk("S4 (Sigma w)_3", Sw3[2], ".2f", "0.03")
chk("S4 variance", sp3**2, ".5f", "0.01768")
has("S4 terms", "(\\Sigma\\mathbf w)_1=0.016+0.0016+0.0072=0.0248")
has("S4 stand-alone", "0.08/0.18=44.4%")
chk("P10 mu_p", 100 * float(w3 @ mu3), ".2f", "6.80")
chk("P10 sigma_p", 100 * sp3, ".2f", "13.30")
chk("P10 w's", 100 * sw3, ".0f", "18")
chk("P10 ratio", sw3 / sp3, ".2f", "1.35")
chk("P10 ratio from the printed", 18 / 13.30, ".2f", "1.35", in_md=False)
for j, printed in enumerate(("56.1", "10.0", "33.9")):
    chk(f"P10 share {j + 1}", 100 * sh3[j], ".1f", printed)
assert f"{sum(round(100 * float(x), 1) for x in sh3):.1f}" == "100.0"
for j, printed in enumerate(("18.65", "3.31", "22.56")):
    chk(f"P10 MRC {j + 1}", 100 * m3[j], ".2f", printed)
chk("P10 linear", 100 * lin3, ".2f", "-0.96")
chk("P10 linear from the printed MRCs", 0.05 * (3.31 - 22.56), ".2f", "-0.96", in_md=False)
chk("P10 exact", -100 * ex3, ".2f", "0.89")
chk("P10 new sigma_p", 100 * (sp3 + ex3), ".2f", "12.41")
assert round(13.30 - 0.89, 2) == 12.41
# P6
chk("P6 stem rho", r_m, ".4f", "0.5521")
chk("P6 key", (1 - r_st**2) / sqrt(116), ".4f", "0.0645")
chk("P6 1/sqrt(T)", 1 / sqrt(116), ".4f", "0.0928")
chk("P6 divided by T", (1 - r_st**2) / 116, ".4f", "0.0060")
chk("S6 1 - rho^2", 1 - r_st**2, ".4f", "0.6952")
chk("S6 sqrt(116)", sqrt(116), ".3f", "10.770")
chk("S6 plug-in", se[0, i46, "monthly"][2], ".3f", "0.081")
# P8 and S8
chk("P8 exact", 100 * tb.cost, ".7f", "0.0310028")
chk("P8 approximation", 100 * approx, ".7f", "0.0310231")
chk("S8 gap", 100 * (approx - tb.cost), ".7f", "0.0000203")
chk("S8 bound", 100 * tb.cost * (COMMISSION + 0.001) * float(np.abs(tb.target).sum()), ".7f", "0.0000752")
chk("S8 0.2425", 100 * (COMMISSION + 0.001), ".4f", "0.2425")
assert approx - tb.cost <= tb.cost * (COMMISSION + 0.001) * float(np.abs(tb.target).sum())
chk("S8 bound from the printed", 0.0310028 * 0.2425 / 100, ".7f", "0.0000752", in_md=False)
# P12 / S12: the lab's recursion against the shared path (the lab prints it); S9's figures are E10's
# stated inputs and labels that are not results
has("P3 stem", "Their growth factors over the period are 1.40 and 0.80")
has("P4 stem", "$\\rho_{12}=0.2$, $\\rho_{13}=0.6$ and $\\rho_{23}=-0.2$")
has("E8 switch", "With $\\boldsymbol\\Delta$ holding +0.05 and -0.05")
has("E8 linear", "$0.05(\\mathrm{MRC}_{00679B}-\\mathrm{MRC}_{00642U})=-1.24$")
has("E6 formula", "0.3\\times(-0.97%)")
has("time", "time: \"≈ 2.5 h + lab\"")
has("Maillard's section", "(§2.1, p. 4, and its footnote)")

# ---------------------------------------------------------------- structure: labels, tags and citations
ex_labels = re.findall(r"\[!exhibit\][^\n]*\{#([\w-]+)\}", RAW)
eg_labels = re.findall(r"\[!example\][^\n]*\{#([\w-]+)\}", RAW)
assert ex_labels == ["case", "drift", "trade", "freq", "cov", "shares", "windows", "factor"], ex_labels
assert len(eg_labels) == 10, eg_labels
assert len(set(ex_labels) | set(eg_labels)) == len(ex_labels) + len(eg_labels), "a label is used twice"
for lab_ in ex_labels:
    assert f"[[ex:{lab_}]]" in RAW, f"exhibit {lab_} is never cited"
for kind, lab_ in re.findall(r"\[\[(ex|eg):([\w-]+)\]\]", RAW):
    assert lab_ in (ex_labels if kind == "ex" else eg_labels), (kind, lab_)
tags = re.findall(r"\\tag\{(27\.\d+)\}", RAW)
assert tags == [f"27.{k}" for k in (1, 2, 3, 4, 7, 5, 6, 8)], tags
for name in re.findall(r'data-chart="(lm27-[\w-]+)"', RAW):
    assert (CHARTS / f"{name}.json").exists(), name
assert "κ" not in RAW and "\\kappa" not in RAW and "\\mathcal B" not in RAW
print(f"labels: {len(ex_labels)} exhibits, {len(eg_labels)} examples, tags (27.1)-(27.8), every exhibit cited")

# ====================================================================== report
body = TEXT.split("\n## Glossary", 1)[0]
nums = set(re.findall(r"(?<![\w.])\d+\.\d+|(?<![\w.,])\d{1,3}(?:,\d{3})+", body))
COVERED |= set(re.findall(r"\((\d{1,2}\.\d{1,2})\)", body))          # equation references, (1.12) .. (27.8)
COVERED |= {n.split(".")[0] for n in COVERED if re.fullmatch(r"\d{1,3}(,\d{3})+\.\d+", n)}   # 1,429 of 1,429.89
left = sorted(n for n in nums if n not in COVERED)
print(f"\nnumbers with a decimal point or thousands separator not covered by a check ({len(left)}):")
print("   " + " ".join(left))
print(f"\nvalues near a rounding boundary at their printed precision ({len(FLAGS)}):")
for fl_ in FLAGS:
    print("   ", fl_)
print(f"anchor differences ({len(ANCHOR_DIFFS)}):")
for a_ in ANCHOR_DIFFS:
    print("   ", a_)
print(f"\nall {N_CHECKS} checks passed")
sys.exit(0)
