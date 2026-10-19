"""Every number that LM19 (Descriptive Statistics of Returns) quotes, computed and checked against src/lm19.md.

Run:  uv run python data/lm19_numbers.py      (after data/vol3_series.py has built TR23)

Input: data/processed/vol3_taiex.parquet (TR23: the TAIEX total-return index from FinMind's
TaiwanStockTotalReturnIndex, closes 2003-01-02 .. 2026-10-08), read through data/lm19_common.py. The module text is
src/lm19.md (and its chart files src/data/lm19-*.json, written by data/lm19_charts.py); plans/vol-4-anchors.md holds
the Stage 1 anchors (A19-nn). The script started from data/vol4_anchors_lm19.py: part 1 recomputes every anchor line
with the same definitions and compares it with the anchor table, reporting a difference rather than forcing it.

Conventions (as the module states them; data/lm19_common.py lists them in full): one-day statistics on simple
returns R, sums, autocorrelations and variance ratios on log returns r = ln(1 + R); moments divide by the number of
terms (s_u by T - 1); every quantile and median is F^-1(u) = x_(ceil(un)); rho_k uses the full-sample mean and divisor
T; VR(m) is the overlapping estimator (19.8). A = T / years = 246.12 for TR23, and a year of 2003-2025 is 246 sessions.
Counts on returns use Fraction on the closes; counts on computed statistics use the guard (>= x - 1e-12,
<= x + 1e-12). One simulated experiment, e = 1: np.random.default_rng([1, 20261011]), created once.

Checks (each stops the script on a failure):
  chk(label, value, fmt, printed)  format(value, fmt) equals the printed string, the value does not sit on a rounding
                                   tie of that format, and the printed string is in the module as a whole number.
                                   Hand computations are redone from the printed, rounded inputs (PITFALLS section 7).
  has(label, text)                 a literal string (a table row, a date, a phrase) is in the module.
  near(label, value, fmt)          reports a value within a tenth of a unit of its last printed digit from a
                                   rounding boundary (the anchors' flag), for the writer's and reviewer's eyes.
At the end the script lists the numbers of the module that no check covered and prints "all N checks passed".
"""
import datetime as dt
import json
import math
import re
from fractions import Fraction
from math import ceil, floor, pi, sqrt

import numpy as np
from lm19_common import (
    EPS,
    LIMIT_SWITCH,
    M_MAX,
    ROOT,
    SEED,
    TR23,
    Z75,
    acf,
    blocks,
    exk_adj,
    exkurt,
    exkurt_closed,
    iid_factor,
    mad,
    okurt_normal,
    period_sums,
    qf,
    skew,
    skew_adj,
    skew_closed,
    summary,
    sums,
    trim,
    vr_all,
    vr_n,
    vr_o,
    vr_plug,
)
from numpy.lib.stride_tricks import sliding_window_view
from scipy import stats
from statsmodels.stats.stattools import robust_kurtosis, robust_skewness
from statsmodels.tsa.stattools import acf as sm_acf

MD = ROOT / "src" / "lm19.md"
JS = ROOT / "src" / "lm19.js"
CHARTS = ROOT / "src" / "data"
ANCHORS = ROOT / "plans" / "vol-4-anchors.md"
Check = tuple[float, int]


# ====================================================================== part 1: the anchors
OUT: list[str] = []


def put(value: str, *checks: Check) -> None:
    """One anchor line, as data/vol4_anchors_lm19.py prints it (with its near-boundary flags)."""
    flags = []
    for v, d in checks:
        x = abs(v) * 10**d
        units = abs((x - floor(x)) - 0.5)
        if units < 0.1:
            flags.append(f"{v:.{d + 4}f} at {d} dp, {floor(units * 1e4) / 1e4:.4f} unit from a boundary")
    tail = f" [near boundary: {'; '.join(flags)}]" if flags else ""
    OUT.append(f"A19-{len(OUT) + 1:02d} {value}{tail}")


S = TR23()
R, r, T, A, RF, dates, dates_all = S.R, S.r, S.T, S.A, S.RF, S.dates, S.dates_all
tr, dates_np, in25, r25, T25, pre, ann = S.tr, S.dates_np, S.in25, S.r25, S.T25, S.pre, S.ann
days, years, per_year = S.days, S.years, S.per_year

put(f"{len(dates_all)} closes, {dates_all[0]} -> {dates_all[-1]}")                                   # 01
put(f"{T} returns, {dates[0]} -> {dates[-1]}")                                                       # 02
put(f"{days} days; {years:.7f} years", (years, 4))                                                   # 03
put(f"{A:.6f}", (A, 2))                                                                              # 04
n_distinct = len(set(RF))
n_zero = sum(x == 0 for x in RF)
put(f"distinct returns {n_distinct} of {T}; exact zeros {n_zero} (Fraction on the closes)")         # 05
put(f"{T25} log returns {dates[0]} -> {dates_np[in25][-1]}; sessions per calendar year {min(per_year)}-{max(per_year)},"
    f" mean {T25 / 23:.5f}; returns dated 2026: {T - T25}", (T25 / 23, 2))                           # 06
put(f"before {LIMIT_SWITCH}: {int(pre.sum())}; from it: {int((~pre).sum())}")                        # 07
wk, wk_n = period_sums(S.wk_key, r25)
mo, mo_n = period_sums(S.mo_key, r25)
wpy = len(wk) / 23
put(f"weeks {len(wk)} ({min(wk_n)}-{max(wk_n)} sessions), {wpy:.5f} a year; months {len(mo)} ({min(mo_n)}-{max(mo_n)}"
    f" sessions); years 23 ({min(per_year)}-{max(per_year)} sessions)", (wpy, 2))                    # 08
sr25 = float(r25.std(ddof=0))
v_day = sqrt(246) * sr25
put(f"s_r (divisor {T25}) {100 * sr25:.7f}%; sqrt(246) s_r {100 * v_day:.5f}%",
    (100 * sr25, 5), (100 * v_day, 3), (100 * v_day, 2))                                             # 09
sd_wk, sd_mo = float(wk.std(ddof=0)), float(mo.std(ddof=0))
v_wk = sd_wk * sqrt(wpy)
put(f"weekly s {100 * sd_wk:.6f}% x sqrt({wpy:.5f}) = {100 * v_wk:.5f}%", (100 * sd_wk, 4), (100 * v_wk, 2))  # 10
v_mo = sd_mo * sqrt(12)
put(f"monthly s {100 * sd_mo:.6f}% x sqrt(12) = {100 * v_mo:.5f}%", (100 * sd_mo, 4), (100 * v_mo, 2))  # 11
v_yr = float(ann.std(ddof=0))
m246 = 246 * float(r25.mean())
put(f"calendar years: mean {ann.mean():.7f}, s (divisor 23) {v_yr:.7f}; 246 rbar' {m246:.7f}",
    (100 * float(ann.mean()), 3), (100 * v_yr, 3), (100 * v_yr, 2), (100 * m246, 3))                # 12
vr_need = (v_yr / v_day) ** 2
put(f"(s_year / (sqrt(246) s_r))^2 = {vr_need:.6f}", (vr_need, 2))                                   # 13

wdates = ["2025-04-07", "2025-04-08", "2025-04-09", "2025-04-10", "2025-04-11"]
iw = [dates.index(d) for d in wdates]
wF = [RF[i] for i in iw]
wR = np.array([float(x) for x in wF])
all_wk: dict[tuple[int, int], list[int]] = {}
for i, d in enumerate(dates):
    all_wk.setdefault(dt.date.fromisoformat(d).isocalendar()[:2], []).append(i)
wk_sd = sorted(((float(R[v].std(ddof=0)), k) for k, v in all_wk.items()), reverse=True)
rank = [k for _, k in wk_sd].index(dt.date(2025, 4, 7).isocalendar()[:2]) + 1
w_s = float(wR.std(ddof=0))
put("returns " + ", ".join(f"{100 * float(x):.6f}%" for x in wF)
    + f" (Fraction); week's s {100 * w_s:.5f}%, rank {rank} of {len(all_wk)} ISO weeks by s",
    *[(100 * float(x), 4) for x in wF], (100 * float(wF[0]), 2), (100 * w_s, 2))                     # 14
w_mean, w_med, w_trim = float(wR.mean()), qf(wR, 0.5), trim(wR, 1)
put(f"mean {100 * w_mean:.6f}%; median {100 * w_med:.6f}%; 20% trimmed {100 * w_trim:.6f}%",
    (100 * w_mean, 3), (100 * w_med, 3), (100 * w_trim, 3))                                          # 15
wG = float(np.prod(1 + wR))
w_RG, w_rbar = wG ** 0.2 - 1, float(np.log1p(wR).mean())
put(f"G {wG:.7f} ({100 * (wG - 1):.5f}%); R_G {100 * w_RG:.6f}%; rbar {100 * w_rbar:.6f}%",
    (wG, 4), (100 * (wG - 1), 2), (100 * w_RG, 3), (100 * w_rbar, 3))                                # 16
wR2 = wR.copy()
wR2[0] = wR[0] - 0.10
k_mean, k_med, k_trim = float(wR2.mean()), qf(wR2, 0.5), trim(wR2, 1)
put(f"with {100 * wR2[0]:.4f}% for {100 * wR[0]:.4f}%: mean {100 * k_mean:.6f}%; median {100 * k_med:.6f}%;"
    f" 20% trimmed {100 * k_trim:.6f}%",
    (100 * float(wR2[0]), 2), (100 * k_mean, 3), (100 * k_med, 3), (100 * k_trim, 3))                # 17
full = summary(R)
RG = float((tr[-1] / tr[0]) ** (1 / T) - 1)
rbar = float(r.mean())
i_med = int(np.argsort(R)[ceil(0.5 * T) - 1])
put(f"Rbar {100 * full['mean']:.7f}%; median R_({ceil(0.5 * T)}) {100 * full['median']:.7f}% ({dates[i_med]});"
    f" 5% trimmed (j0 = {floor(0.05 * T)}) {100 * full['trim5']:.7f}%; R_G {100 * RG:.7f}%; rbar {100 * rbar:.7f}%",
    (100 * full["mean"], 4), (100 * full["median"], 4), (100 * full["trim5"], 4), (100 * RG, 5), (100 * RG, 6),
    (100 * rbar, 5))                                                                                 # 18
w_su = float(wR.std(ddof=1))
w_mad = mad(wR)
w_mad_mean = float(np.abs(wR - w_mean).mean())
put(f"week: s {100 * w_s:.6f}%; s_u {100 * w_su:.6f}%; ratio {w_su / w_s:.6f}; mean abs dev "
    f"{100 * w_mad_mean:.6f}%; MAD {100 * w_mad:.6f}%",
    (100 * w_s, 3), (100 * w_su, 3), (w_su / w_s, 3), (100 * w_mad_mean, 3), (100 * w_mad, 3))       # 19
put(f"s {100 * full['s']:.7f}%; s_u {100 * full['s_u']:.7f}%; ratio {full['s_u'] / full['s']:.9f}",
    (100 * full["s"], 4), (100 * full["s_u"], 4), (full["s_u"] / full["s"], 7),
    (100 * full["s"], 3), (100 * full["s_u"], 3))                                                    # 20
put(f"mean abs dev {100 * full['meanAD']:.7f}%; / s {full['meanAD'] / full['s']:.6f}; sqrt(2/pi) {sqrt(2 / pi):.7f}",
    (100 * full["meanAD"], 3), (full["meanAD"] / full["s"], 3), (sqrt(2 / pi), 3))                   # 21
put(f"Phi^-1(0.75) {Z75:.7f}; 1/Phi^-1(0.75) {1 / Z75:.7f}; 2 Phi^-1(0.75) {2 * Z75:.7f}",
    (Z75, 4), (1 / Z75, 4), (2 * Z75, 3))                                                            # 22
q1, q3, mad_full = qf(R, 0.25), qf(R, 0.75), mad(R)
put(f"R_({ceil(0.25 * T)}) {100 * q1:.6f}%; R_({ceil(0.75 * T)}) {100 * q3:.6f}%; IQR {100 * (q3 - q1):.6f}%;"
    f" IQR/(2 Phi^-1(0.75)) {100 * full['IQR/1.349']:.7f}%; MAD {100 * mad_full:.7f}%; MAD/Phi^-1(0.75) "
    f"{100 * full['1.4826MAD']:.7f}%",
    (100 * q1, 3), (100 * q3, 3), (100 * (q3 - q1), 3), (100 * full["IQR/1.349"], 3), (100 * mad_full, 3),
    (100 * mad_full, 4), (100 * full["1.4826MAD"], 3))                                               # 23
an_s, an_m, an_i = sqrt(A) * full["s"], sqrt(A) * full["1.4826MAD"], sqrt(A) * full["IQR/1.349"]
put(f"sqrt(A) s {100 * an_s:.5f}%; sqrt(A) 1.4826 MAD {100 * an_m:.5f}%; sqrt(A) IQR/1.349 {100 * an_i:.5f}%;"
    f" s over each {an_s / an_m:.5f}, {an_s / an_i:.5f}",
    (100 * an_s, 2), (100 * an_m, 1), (100 * an_i, 1), (an_s / an_m, 2), (an_s / an_i, 2))           # 24
W = sliding_window_view(R, 246)
srt = np.sort(W, axis=1)
med_w = srt[:, 122]
madw = np.sort(np.abs(W - med_w[:, None]), axis=1)[:, 122]
roll = {"s": sqrt(A) * W.std(axis=1, ddof=0), "MAD": sqrt(A) * madw / Z75,
        "IQR": sqrt(A) * (srt[:, 184] - srt[:, 61]) / (2 * Z75)}
ends = dates_np[245:]
txt = []
roll_checks: list[Check] = []
for k, v in roll.items():
    txt.append(f"{k} max {100 * v.max():.4f}% ({ends[v.argmax()]}) min {100 * v.min():.4f}% ({ends[v.argmin()]})"
               f" end {100 * v[-1]:.4f}%")
    roll_checks += [(100 * float(v.max()), 1), (100 * float(v.min()), 1), (100 * float(v[-1]), 1)]
ratio_w = roll["s"] / roll["MAD"]
put(f"{len(W)} windows ending {ends[0]} -> {ends[-1]}: " + "; ".join(txt)
    + f"; s / (1.4826 MAD) max {ratio_w.max():.5f} ({ends[ratio_w.argmax()]}) min {ratio_w.min():.5f}"
    f" ({ends[ratio_w.argmin()]})", *roll_checks, (float(ratio_w.max()), 2), (float(ratio_w.min()), 2))  # 25
medF = sorted(RF)[ceil(0.5 * T) - 1]
devF = sorted(abs(x - medF) for x in RF)
madF = devF[ceil(0.5 * T) - 1]
n_in = sum(abs(x - medF) <= madF for x in RF)
put(f"days with |R - median| <= MAD: {n_in} (Fraction); ties among |R - median|: {len(devF) - len(set(devF))};"
    f" exact and float MAD agree within 1e-15: {abs(float(madF) - mad_full) < 1e-15}")              # 26
sk_b, ek_b = float(stats.skew(R, bias=False)), float(stats.kurtosis(R, bias=False))
put(f"skew {full['skew']:.7f}, adjusted {full['skew_adj']:.7f}; excess kurtosis {full['exkurt']:.7f}, adjusted "
    f"{full['exkurt_adj']:.7f}; closed forms agree with SciPy bias=False within 1e-13: "
    f"{abs(full['skew_adj'] - sk_b) < 1e-13}, {abs(full['exkurt_adj'] - ek_b) < 1e-13}",
    (full["skew"], 3), (full["skew"], 4), (full["skew_adj"], 4), (full["exkurt"], 2), (full["exkurt"], 3),
    (full["exkurt_adj"], 3))                                                                         # 27
sk23, ek23 = skew(ann), exkurt(ann)
put(f"23 calendar-year log returns: skew {sk23:.6f}, adjusted {skew_adj(ann):.6f}; excess kurtosis "
    f"{ek23:.6f}, adjusted {exk_adj(ann):.6f}",
    (sk23, 2), (skew_adj(ann), 2), (ek23, 2), (exk_adj(ann), 2))                                     # 28
n50 = 2902
k50 = (n50 - 1) / ((n50 - 2) * (n50 - 3)) * ((n50 + 1) * 8.12 + 6)
put(f"LM4's 0050 8.12 (lm04.md:132) adjusted at T = {n50}: {k50:.5f}", (k50, 2))                     # 29
okn = okurt_normal()
sk_sm = robust_skewness(R)[1]
kr_sm = robust_kurtosis(R)[1]
put(f"quartile skewness {full['qskew']:.7f}; octile kurtosis {full['okurt']:.7f}, normal {okn:.7f}, excess "
    f"{full['okurt'] - okn:.7f}; statsmodels sk2 {float(sk_sm):.7f}, kr2 (excess) {float(kr_sm):.7f}",
    (full["qskew"], 3), (full["qskew"], 4), (full["okurt"], 3), (okn, 3), (full["okurt"] - okn, 3))  # 30
X2_DEC = {"mean": 4, "median": 4, "trim5": 4, "s": 3, "s_u": 3, "meanAD": 3, "1.4826MAD": 3, "IQR/1.349": 3,
          "skew": 4, "skew_adj": 4, "qskew": 3, "exkurt": 3, "exkurt_adj": 3, "okurt": 3}
PCT = ("mean", "median", "trim5", "s", "s_u", "meanAD", "1.4826MAD", "IQR/1.349")


def fmt_summary(d: dict[str, float]) -> str:
    return "; ".join(f"{k} {100 * v:.6f}%" if k in PCT else f"{k} {v:.6f}" for k, v in d.items())


def x2_checks(d: dict[str, float]) -> list[Check]:
    return [(100 * v if k in PCT else v, X2_DEC[k]) for k, v in d.items()]


plus = summary(np.append(R, -0.10))
rel = {k: (plus[k] - full[k]) / abs(full[k]) for k in full}
REL_DEC = {"mean": 1, "median": 1, "trim5": 1, "s": 1, "1.4826MAD": 2, "IQR/1.349": 2, "skew": 0, "exkurt": 0,
           "qskew": 1, "okurt": 2}
put("one more -10% day (T+1): " + fmt_summary(plus) + "; relative changes "
    + ", ".join(f"{k} {100 * v:+.5f}%" for k, v in rel.items()),
    *x2_checks(plus), (plus["skew"], 3), (plus["exkurt"], 2),
    *[(100 * rel[k], d) for k, d in REL_DEC.items()])                                                # 31
reg7, reg10 = summary(R[pre]), summary(R[~pre])
put("7% regime: " + fmt_summary(reg7), *x2_checks(reg7), (reg7["exkurt"], 2))                         # 32
put("10% regime: " + fmt_summary(reg10), *x2_checks(reg10), (reg10["exkurt"], 2))                     # 33
put(f"normal with TR23's mean and s: mean = median = trimmed {100 * full['mean']:.6f}%; mean abs dev "
    f"{100 * sqrt(2 / pi) * full['s']:.6f}%; robust scales = s {100 * full['s']:.6f}%; skewness 0; quartile "
    f"skewness 0; excess kurtosis 0; octile kurtosis {okn:.7f}",
    (100 * full["mean"], 4), (100 * sqrt(2 / pi) * full["s"], 3), (100 * full["s"], 3), (okn, 3))    # 34
alt = np.array([1.0, -1.0, 1.0, -1.0, 1.0, -1.0])
a1 = float(acf(alt, 1)[0])
put(f"alternating six: rho_1 {a1:.7f} = {Fraction(-5, 6)}", (a1, 3))                                  # 35
w_rho, w_pair = float(acf(wR, 1)[0]), float(np.corrcoef(wR[:-1], wR[1:])[0, 1])
put(f"tariff week R: rho_1 {w_rho:.6f}; correlation of the 4 pairs (R_t, R_t+1) {w_pair:.6f}",
    (w_rho, 3), (w_pair, 3))                                                                          # 36
band, band25 = 1.96 / sqrt(T), 1.96 / sqrt(T25)
put(f"1.96/sqrt(T) {band:.7f}; on 2003-2025 {band25:.7f}", (band, 4), (band, 5), (band25, 4))         # 37
rho_r, rho_a, rho_q = acf(r, M_MAX - 1), acf(np.abs(r), 30), acf(r**2, 30)


def corr_pairs(a: np.ndarray, b: np.ndarray) -> float:
    a, b = a - a.mean(), b - b.mean()
    return float((a * b).mean() / sqrt(float((a * a).mean() * (b * b).mean())))


out_r = [(k + 1, rho_r[k]) for k in range(30) if abs(rho_r[k]) >= band - EPS]
marg = np.abs(np.abs(rho_r[:30]) - band)
k_close = int(marg.argmin())
pr1 = corr_pairs(r[:-1], r[1:])
put(f"r: rho_1 {rho_r[0]:.7f} (pairs {pr1:.8f}); outside the band {len(out_r)} of 30: "
    + ", ".join(f"{k} {v:.6f}" for k, v in out_r)
    + f"; closest to the band: lag {k_close + 1} {rho_r[k_close]:.7f} (margin {marg[k_close]:.1e}); X4 tooltips: all"
    " 30 lags checked at 5 dp",
    (float(rho_r[0]), 4), (pr1, 4), (float(rho_r[0]), 3), (pr1, 3), *[(float(v), 5) for v in rho_r[:30]])  # 38
ar = np.abs(r)
pa20 = corr_pairs(ar[:-20], ar[20:])
put(f"|r|: rho_1 {rho_a[0]:.7f}; rho_20 {rho_a[19]:.7f} (pairs {pa20:.7f}); min over 1-30 "
    f"{rho_a.min():.6f} (lag {int(rho_a.argmin()) + 1}); max {rho_a.max():.6f} (lag {int(rho_a.argmax()) + 1}); "
    f"outside the band {int((np.abs(rho_a) >= band - EPS).sum())} of 30; X4 tooltips: all 30 lags checked at 5 dp",
    (float(rho_a[0]), 3), (float(rho_a[19]), 4), (pa20, 4), (pa20, 3), (float(rho_a.min()), 3),
    (float(rho_a.max()), 3), *[(float(v), 5) for v in rho_a])                                        # 39
x2c = r**2 - (r**2).mean()
p3 = x2c[3:] * x2c[:-3]
i10 = dates.index("2025-04-10")
xa = ar - ar.mean()
pa3 = xa[3:] * xa[:-3]
sh_q, sh_a = float(p3[i10 - 3] / p3.sum()), float(pa3[i10 - 3] / pa3.sum())
put(f"r^2: rho_1..3 {rho_q[0]:.6f}, {rho_q[1]:.6f}, {rho_q[2]:.6f}; min over 1-30 {rho_q.min():.6f} (lag "
    f"{int(rho_q.argmin()) + 1}); outside the band {int((np.abs(rho_q) >= band - EPS).sum())} of 30; share of the lag-3 "
    f"sum from 2025-04-10 x 2025-04-07 {100 * sh_q:.5f}%; |r| rho_3 {rho_a[2]:.6f}, that pair's share "
    f"{100 * sh_a:.5f}%",
    (float(rho_q[0]), 3), (float(rho_q[1]), 3), (float(rho_q[2]), 3), (float(rho_q.min()), 3), (100 * sh_q, 1),
    (float(rho_a[2]), 3), (100 * sh_a, 1))                                                           # 40
xr = r - r.mean()
se_rob = sqrt(float(((xr[1:] * xr[:-1]) ** 2).sum())) / float((xr * xr).sum())
put(f"rho_1(r) standard errors: iid 1/sqrt(T) {1 / sqrt(T):.6f}; HC0-type robust {se_rob:.6f} (LM25's; not printed"
    " in LM19)", (1 / sqrt(T), 4))                                                                   # 41
reg = []
reg_checks: list[Check] = []
reg_rho: dict[str, tuple[float, float]] = {}
for lab, msk in (("7%", pre), ("10%", ~pre)):
    a_r, a_a = float(acf(r[msk], 1)[0]), float(acf(np.abs(r[msk]), 1)[0])
    reg_rho[lab] = (a_r, a_a)
    reg.append(f"{lab}: rho_1(r) {a_r:.6f}, rho_1(|r|) {a_a:.6f}")
    reg_checks += [(a_r, 3), (a_a, 3)]
put("; ".join(reg), *reg_checks)                                                                      # 42
dmax = max(float(np.abs(sm_acf(x, nlags=30, fft=False)[1:] - acf(x, 30)).max()) for x in (r, ar, r**2))
put(f"statsmodels acf(x, nlags=30, fft=False) and the book's rho_k agree within 1e-15 for r, |r|, r^2: {dmax < 1e-15}")  # 43
put(f"VR(2): 1 + rho_1 {1 + rho_r[0]:.7f}; overlapping {vr_o(r, 2):.7f}", (1 + float(rho_r[0]), 4), (vr_o(r, 2), 4))  # 44
f16, f1 = 1 + 2 * 0.04 * 244 / 245, 1 + 2 * float(rho_r[0]) * 245 / 246
put(f"LM16's factor (lm16.md:623) 1 + 2(0.04)(244/245) = {f16:.7f}; TR23 lag 1 only at m = 246: "
    f"1 + 2 rho_1 (245/246) = {f1:.7f}", (f16, 4), (f1, 4))                                          # 45
offs246 = [vr_n(r, 246, o) for o in range(246)]
vo246, vp246 = vr_o(r, 246), vr_plug(rho_r, 246)
put(f"m = 246, TR23: identity column {vp246:.7f}; overlapping {vo246:.7f}; non-overlapping from the first "
    f"return {vr_n(r, 246):.7f} ({T // 246} blocks), over the 246 first returns {min(offs246):.6f} to {max(offs246):.6f}",
    (vp246, 3), (vo246, 3))                                                                          # 46
put(f"iid factor (1 - m/T)/(1 - 1/T): m = 246, T = {T}: {iid_factor(T, 246):.7f}; m = 1231: {iid_factor(T, 1231):.7f};"
    f" m = 246, T = {T25}: {iid_factor(T25, 246):.7f}",
    (iid_factor(T, 246), 3), (iid_factor(T, 1231), 3), (iid_factor(T25, 246), 3))                    # 47
# experiment e = 1: the iid expectation of the overlapping estimator (the generator is created once, here)
rng = np.random.default_rng([1, SEED])
n_sim = 10_000
sim = np.empty((n_sim, 2))
for j in range(n_sim):
    z = rng.standard_normal(T)
    sim[j] = vr_o(z, 246), vr_o(z, 1231)
mc = sim.mean(axis=0)
mcse = sim.std(axis=0, ddof=0) / sqrt(n_sim)
put(f"e = 1, {n_sim} iid normal samples of T = {T}: mean VR(246) {mc[0]:.6f} +- {mcse[0]:.6f}, formula "
    f"{iid_factor(T, 246):.6f}; mean VR(1231) {mc[1]:.6f} +- {mcse[1]:.6f}, formula {iid_factor(T, 1231):.6f}",
    (float(mc[0]), 3), (float(mcse[0]), 3), (float(mc[1]), 3), (float(mcse[1]), 3))                  # 48
X6_M = (2, 5, 20, 60, 246, 1231)
x6: dict[int, tuple[float, ...]] = {}
rows = []
x6_checks: list[Check] = []
for m in X6_M:
    o = [vr_n(r, m, k) for k in range(m)]
    vals = (vr_o(r, m), vr_plug(rho_r, m), vr_n(r, m), min(o), max(o), iid_factor(T, m))
    x6[m] = vals
    rows.append(f"m={m}: windows {T - m + 1}, blocks {T // m}, T/m {T / m:.4f}, overlapping {vals[0]:.6f}, identity "
                f"column {vals[1]:.6f}, non-overlapping first {vals[2]:.6f}, range {vals[3]:.6f}-{vals[4]:.6f}, "
                f"iid factor {vals[5]:.6f}")
    x6_checks += [(T / m, 2)] + [(v, 3) for v in vals]
put("; ".join(rows), *x6_checks)                                                                      # 49
s1231 = sums(r, 1231)
own = float(s1231.var(ddof=0)) / (1231 * float(r.var(ddof=0)))
cen = vr_o(r, 1231)
wts = np.convolve(np.ones(T - 1231 + 1), np.ones(1231)) / (T - 1231 + 1)
own_factor = (1231 - float((wts**2).sum())) / (1231 * (1 - 1 / T))
sd_own, sqm = float(s1231.std(ddof=0)), sqrt(1231) * float(r.std(ddof=0))
put(f"LM18's windows: sd of ln G about its own mean {sd_own:.6f}; sqrt(m) s_r {sqm:.6f}; own-mean ratio {own:.6f}"
    f" (iid factor {own_factor:.6f}; neither printed); VR(1231) {cen:.6f} (iid factor {iid_factor(T, 1231):.6f},"
    f" ratio {cen / iid_factor(T, 1231):.6f}); mean ln G {float(s1231.mean()):.6f} vs m rbar {1231 * rbar:.6f}",
    (sd_own, 3), (sqm, 3), (cen, 3), (cen / iid_factor(T, 1231), 2), (float(s1231.mean()), 3), (1231 * rbar, 3))  # 50
put(f"iid correlation of consecutive overlapping 246-day sums (m-1)/m {245 / 246:.6f}; T/m at 246 {T / 246:.4f},"
    f" at 1231 {T / 1231:.4f}", (245 / 246, 3), (T / 246, 1), (T / 1231, 2))                          # 51
VR_TR = vr_all(r, M_MAX)          # VR(1) .. VR(1231)
VR_25 = vr_all(r25, M_MAX)
vr_tr2, vr_252 = VR_TR[1:], VR_25[1:]
mm = np.arange(2, M_MAX + 1)
v492, v25_492, v25_1231 = vr_o(r, 492), vr_o(r25, 492), vr_o(r25, 1231)
assert abs(VR_TR[491] - v492) < 1e-12 and abs(VR_25[1230] - v25_1231) < 1e-12
put(f"TR23 VR(m), m = 2..1231: max {vr_tr2.max():.6f} at m = {int(mm[vr_tr2.argmax()])}; at 492 {v492:.6f};"
    f" min {vr_tr2.min():.6f} at m = {int(mm[vr_tr2.argmin()])}; first m below 1: {int(mm[np.argmax(vr_tr2 < 1)])};"
    f" 2003-2025 VR at 492 {v25_492:.6f}, at 1231 {v25_1231:.6f}, max {vr_252.max():.6f} at m ="
    f" {int(mm[vr_252.argmax()])} (not printed)",
    (float(vr_tr2.max()), 3), (v492, 3), (float(vr_tr2.min()), 3), (v25_492, 3), (v25_1231, 3))      # 52
rho25 = acf(r25, 245)
v25 = vr_o(r25, 246)
vp25 = vr_plug(rho25, 246)
put(f"2003-2025, m = 246: VR {v25:.7f}; identity column {vp25:.7f}; divided by the iid factor "
    f"{v25 / iid_factor(T25, 246):.6f}; TR23 VR {vo246:.7f}",
    (v25, 4), (v25, 3), (vp25, 3), (v25 / iid_factor(T25, 246), 3), (vo246, 3))                      # 53
s_r = float(r.std(ddof=0))
sr_R, sr_r = full["mean"] / full["s"], rbar / s_r
put(f"TR23: A Rbar {100 * A * full['mean']:.5f}%; A rbar {100 * A * rbar:.5f}%; A s^2 {A * full['s'] ** 2:.7f};"
    f" A s_r^2 {A * s_r**2:.7f}; s_r {100 * s_r:.6f}%; sqrt(A) s {100 * an_s:.5f}%; sqrt(A) s_r {100 * sqrt(A) * s_r:.5f}%;"
    f" SR(R) per day {sr_R:.7f}, x sqrt(A) {sqrt(A) * sr_R:.6f}; SR(r) per day {sr_r:.7f}, x sqrt(A) "
    f"{sqrt(A) * sr_r:.6f}, / sqrt(VR(246)) {sqrt(A) * sr_r / sqrt(vo246):.6f}",
    (100 * A * full["mean"], 2), (100 * A * rbar, 2), (A * full["s"] ** 2, 4), (A * s_r**2, 4), (100 * s_r, 4),
    (100 * an_s, 2), (100 * sqrt(A) * s_r, 2), (sr_R, 4), (sqrt(A) * sr_R, 2), (sr_r, 4), (sqrt(A) * sr_r, 3),
    (sqrt(A) * sr_r / sqrt(vo246), 3))                                                               # 54
v_ovl, v_bias = sqrt(v25) * v_day, sqrt(v25 / iid_factor(T25, 246)) * v_day
put(f"2003-2025 annual volatility: iid {100 * v_day:.5f}%; overlapping sqrt(VR) {100 * v_ovl:.5f}%;"
    f" bias-corrected {100 * v_bias:.5f}%; calendar years {100 * v_yr:.5f}%",
    (100 * v_day, 3), (100 * v_day, 2), (100 * v_ovl, 2), (100 * v_bias, 2), (100 * v_yr, 3), (100 * v_yr, 2))  # 55
grid = [(float(blocks(r25, 246, o).std(ddof=0)), len(blocks(r25, 246, o)), o) for o in range(246)]
gv = np.array([g[0] for g in grid])
lo_g, hi_g = grid[int(gv.argmin())], grid[int(gv.argmax())]
g_med = qf(gv, 0.5)
n_hi = int((gv >= v_yr - EPS).sum())
n_lo = int((gv <= v_day + EPS).sum())
mrg = min(float(np.abs(gv - v_yr).min()), float(np.abs(gv - v_day).min()))
put(f"246 grids of 246-day blocks on 2003-2025: min {100 * lo_g[0]:.5f}% (first return {lo_g[2]}, {lo_g[1]} blocks); max "
    f"{100 * hi_g[0]:.5f}% (first return {hi_g[2]}, {hi_g[1]} blocks); first return 0: {100 * grid[0][0]:.5f}% ({grid[0][1]}"
    f" blocks); median F^-1(1/2) = grid {ceil(0.5 * 246)} of 246 sorted, {100 * g_med:.5f}%; at or above the calendar"
    f" years' value {n_hi} ({100 * n_hi / 246:.4f}%); at or below the iid value {n_lo} ({100 * n_lo / 246:.4f}%);"
    f" smallest margin {mrg:.1e}; grids with 23 blocks: first returns "
    f"{min(g[2] for g in grid if g[1] == 23)}-{max(g[2] for g in grid if g[1] == 23)}",
    (100 * lo_g[0], 2), (100 * hi_g[0], 2), (100 * grid[0][0], 2), (100 * g_med, 2), (100 * n_hi / 246, 1),
    (100 * n_lo / 246, 1))                                                                           # 56
sh25 = float(r25.mean()) / sr25
cal_sr = float(ann.mean()) / v_yr
put(f"2003-2025 log returns: SR per day {sh25:.7f}; x sqrt(246) {sqrt(246) * sh25:.6f}; / sqrt(VR(246)) "
    f"{sqrt(246) * sh25 / sqrt(v25):.6f}; calendar years mean / s {cal_sr:.6f}",
    (sh25, 4), (sqrt(246) * sh25, 3), (sqrt(246) * sh25 / sqrt(v25), 3), (cal_sr, 3))                # 57
put(f"initial state (2003-2025, m = 246): VR {v25:.6f}; annual {100 * v_ovl:.5f}%; iid {100 * v_day:.5f}%;"
    f" windows {T25 - 246 + 1}; T/m {T25 / 246:.4f}; iid factor {iid_factor(T25, 246):.6f}",
    (v25, 4), (100 * v_ovl, 2), (100 * v_day, 2), (T25 / 246, 1), (iid_factor(T25, 246), 3))         # 58
kc6 = 1 + 2 * (2 / 3) * 0.04
put(f"KC section 6: m = 3, rho_1 = 0.04, rho_2 = 0: 1 + 2(2/3)(0.04) = {kc6:.7f}", (kc6, 4))           # 59
p1d = ["2020-03-16", "2020-03-17", "2020-03-18", "2020-03-19", "2020-03-20"]
p1 = np.array([float(RF[dates.index(d)]) for d in p1d])
p1_mean, p1_med, p1_trim = float(p1.mean()), qf(p1, 0.5), trim(p1, 1)
put("Problem 1 (2020-03-16..20): " + ", ".join(f"{100 * x:.6f}%" for x in p1) + f"; mean {100 * p1_mean:.6f}%;"
    f" median {100 * p1_med:.6f}%; 20% trimmed {100 * p1_trim:.6f}%",
    *[(100 * float(x), 4) for x in p1], (100 * p1_mean, 3), (100 * p1_med, 3), (100 * p1_trim, 3))  # 60
su23 = 100 * float(ann.std(ddof=1))
p2 = (22.207 * sqrt(23 / 22), 22.207 * 23 / 22, 22.207 * sqrt(22 / 23))
put(f"Problem 2: 22.207% x sqrt(23/22) = {p2[0]:.5f}%; x 23/22 = {p2[1]:.5f}%; x sqrt(22/23) = {p2[2]:.5f}%;"
    f" unrounded s_u {su23:.5f}%", *[(v, 2) for v in p2], (su23, 3))                                  # 61
p3v = (0.5889 * 1.4826 * sqrt(246.12), 0.5889 * sqrt(246.12), 0.5889 / 1.4826 * sqrt(246.12))
put(f"Problem 3: 0.5889% x 1.4826 x sqrt(246.12) = {p3v[0]:.5f}%; 0.5889% x sqrt(246.12) = {p3v[1]:.5f}%;"
    f" 0.5889% / 1.4826 x sqrt(246.12) = {p3v[2]:.5f}%", *[(v, 2) for v in p3v])                     # 62
p4 = (0.681 - 0.490 - 2 * 0.088) / (0.681 + 0.490)
p4c = (0.681 - 0.490) / (0.681 + 0.490)
put(f"Problem 4 (printed quartiles -0.490, 0.088, 0.681): {p4:.6f}; sign reversed {-p4:.6f}; without the median "
    f"{p4c:.6f}", (p4, 3), (p4c, 3))                                                                  # 63
p5 = sqrt(1.0393)
put(f"Problem 5: 1 + 0.0393 = 1.0393; 1 + 2(0.0393) = {1 + 2 * 0.0393:.4f}; sqrt(1.0393) = {p5:.6f}", (p5, 4))  # 64
put(f"Problem 6: iid factor {iid_factor(5849, 1231):.6f}; m/T {1231 / 5849:.6f}",
    (iid_factor(5849, 1231), 2), (1231 / 5849, 2))                                                  # 65
vr7 = 1 + 2 * 0.04 * 245 / 246
p7a = sqrt(246) * 1.2107
put(f"Problem 7: model ratio 1 + 2(0.04)(245/246) = {vr7:.7f}; sqrt(246) x 1.2107% = {p7a:.5f}%; x sqrt(ratio) = "
    f"{p7a * sqrt(vr7):.5f}%", (vr7, 4), (p7a, 2), (p7a * sqrt(vr7), 2))                             # 66
t_rows = []
t_checks: list[Check] = []
t_vals: dict[float, tuple[float, float]] = {}
for nu in (5.0, 3.065):
    tq = float(stats.t.ppf(0.75, nu))
    ratio_t = tq * sqrt((nu - 2) / nu) / Z75
    t_vals[nu] = (tq, ratio_t)
    t_rows.append(f"nu = {nu}: t quantile {tq:.6f}, 1.4826 MAD / sigma {ratio_t:.6f}")
    t_checks += [(tq, 4), (ratio_t, 3)]
tr_ratio = full["1.4826MAD"] / full["s"]
put("Problem 10: " + "; ".join(t_rows) + f"; TR23 {tr_ratio:.6f}", *t_checks, (tr_ratio, 3))          # 67
ext = []
ext_checks: list[Check] = []
ext_vals: dict[str, list[float]] = {}
for lab, msk in (("7%", pre), ("10%", ~pre)):
    xx = r[msk]
    v3 = [vr_o(xx, m) for m in (5, 20, 60)]
    ext_vals[lab] = v3
    ext.append(f"{lab}: " + ", ".join(f"VR({m}) {v:.6f}" for m, v in zip((5, 20, 60), v3)))
    ext_checks += [(v, 3) for v in v3]
put("; ".join(ext), *ext_checks)                                                                     # 68
dd = [dt.date.fromisoformat(d) for d in dates]
sat = [d for d in dd if d.weekday() == 5]
wk25: dict[tuple[int, int], list] = {}
for d in S.d25:
    wk25.setdefault(d.isocalendar()[:2], []).append(d)
sat_wk = [v for v in wk25.values() if any(x.weekday() == 5 for x in v)]
six = [v for v in wk25.values() if len(v) == 6]
put(f"Saturday sessions in TR23: {len(sat)} ({sat[0]} -> {sat[-1]}), {sum(d.year <= 2025 for d in sat)} of them in"
    f" 2003-2025; ISO weeks of 2003-2025 holding one: {len(sat_wk)} ({min(map(len, sat_wk))}-{max(map(len, sat_wk))}"
    f" sessions); weeks of 6 sessions: {len(six)}, each holding a Saturday: {all(any(x.weekday() == 5 for x in v) for v in six)};"
    f" Sunday sessions: {sum(d.weekday() == 6 for d in dd)}")                                          # 69


def _anchor_values() -> dict[str, str]:
    rows_: dict[str, str] = {}
    sec = ANCHORS.read_text(encoding="utf-8").split("\n## LM19", 1)[1].split("\n## ", 1)[0]
    for line in sec.splitlines():
        if line.startswith("| A19-"):
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
            rows_[cells[0]] = cells[3].strip("`").replace("\\|", "|")
    return rows_


ANCHOR_ROWS = _anchor_values()
assert len(ANCHOR_ROWS) == 69 == len(OUT), (len(ANCHOR_ROWS), len(OUT))
ANCHOR_DIFFS: list[str] = []
for line in OUT:
    aid, got = line.split(" ", 1)
    if got != ANCHOR_ROWS[aid]:
        ANCHOR_DIFFS.append(f"{aid}: script {got} | anchor {ANCHOR_ROWS[aid]}")
print(f"part 1: {len(OUT)} anchor lines recomputed, {len(OUT) - len(ANCHOR_DIFFS)} identical to the anchor table")


# ====================================================================== part 2: the module's text
def norm_text(s: str) -> str:
    """Module text with TeX thousands separators, escaped percent signs, \\text{} and minus signs made plain."""
    s = s.replace("{,}", ",").replace("\\%", "%").replace("\u2212", "-").replace("\\,", "")
    return re.sub(r"\\text\{\s*([^}]*)\}", r" \1", s)


MD_RAW = MD.read_text(encoding="utf-8") if MD.exists() else ""
CHART_TEXT = ""
for p in sorted(CHARTS.glob("lm19-*.json")):
    spec = json.loads(p.read_text(encoding="utf-8"))
    CHART_TEXT += "\n" + json.dumps(spec, ensure_ascii=False)
TEXT = norm_text(MD_RAW) + "\n" + CHART_TEXT
N_CHECKS = 0
COVERED: set[str] = set()
NEAR: list[str] = []


def in_text(printed: str, text: str = TEXT) -> bool:
    """The printed number appears as a whole number (2.323 is not inside 2.3235, 0.32 not inside 10.32)."""
    return re.search(r"(?<![\d.])" + re.escape(printed) + r"(?![\d])", text) is not None


def tie(value: float, fmt: str) -> bool:
    """True when value lies on a rounding boundary of fmt (a reader rounding by hand could go either way)."""
    m = re.search(r"\.(\d+)", fmt)
    d = int(m.group(1)) if m else 0
    if fmt.endswith(("e", "g")):
        return False
    scaled = abs(value) * 10**d * (100 if "%" in fmt else 1)
    return abs(scaled - math.floor(scaled) - 0.5) < 1e-6


def chk(label: str, value: float, fmt: str, printed: str) -> None:
    global N_CHECKS
    got = format(value, fmt)
    if got.startswith("-"):
        got = got.replace("-", "-", 1)
    ok = got == printed and in_text(printed) and not tie(value, fmt)
    print(f"CHECK {label}: {got} (printed {printed}) {'ok' if ok else 'MISMATCH'}")
    assert got == printed, (label, got, printed)
    assert not tie(value, fmt), ("rounding tie: print more digits", label, value)
    assert in_text(printed), f"{label}: {printed!r} not found in src/lm19.md or its charts"
    COVERED.add(printed.lstrip("-+"))
    N_CHECKS += 1


def has(label: str, text: str) -> None:
    global N_CHECKS
    assert text in TEXT, f"{label}: {text!r} not found in src/lm19.md or its charts"
    print(f"CHECK {label}: '{text}' in text ok")
    for num in re.findall(r"\d[\d,]*\.?\d*", text):
        COVERED.add(num.rstrip(".,"))
    N_CHECKS += 1


def same(label: str, got: str, printed: str, in_md: bool = True) -> None:
    """A value produced as a string (a fraction, a date) equals the printed one; in_md: it appears in the text."""
    global N_CHECKS
    assert got == printed, (label, got, printed)
    assert not in_md or printed in TEXT, f"{label}: {printed!r} not found in src/lm19.md"
    print(f"CHECK {label}: {got} ok")
    COVERED.add(printed)
    N_CHECKS += 1


def near(label: str, value: float, d: int) -> None:
    """Flag a printed value within a tenth of a unit of its last digit from a rounding boundary (the anchors' rule)."""
    x = abs(value) * 10**d
    units = abs((x - floor(x)) - 0.5)
    if units < 0.1:
        NEAR.append(f"{label}: {value:.{d + 4}f} at {d} dp, {floor(units * 1e4) / 1e4:.4f} unit from a boundary")


def pc(label: str, value: float, d: int, printed: str, sign: bool = False) -> None:
    """A percentage printed with d decimals (value is a fraction)."""
    chk(label, 100 * value, f"{'+' if sign else ''}.{d}f", printed)
    near(label, 100 * value, d)


def nm(label: str, value: float, d: int, printed: str, sign: bool = False) -> None:
    """A plain number printed with d decimals."""
    chk(label, value, f"{'+' if sign else ''}.{d}f", printed)
    near(label, value, d)


def ct(label: str, value: int, printed: str) -> None:
    """A count, with a thousands separator when it has one."""
    chk(label, value, "," if "," in printed else "d", printed)


def cell(v: float, d: int, pct: bool = False) -> str:
    return f"{100 * v if pct else v:.{d}f}"


assert MD_RAW, "src/lm19.md is missing"

# ====================================================================== front matter, case and X1
pc("case: s_r 2003-2025 (LM17's)", sr25, 5, "1.18352")
pc("case: sqrt(246) s_r", v_day, 2, "18.56")
nm("case: sqrt(246) x printed 1.18352%", sqrt(246) * 1.18352, 2, "18.56")
pc("case: weeks", v_wk, 2, "18.09")
pc("case: months", v_mo, 2, "18.12")
pc("case: calendar years", v_yr, 2, "22.21")
nm("case: needed ratio", vr_need, 2, "1.43")
nm("case: needed ratio from printed 22.21/18.56", (22.21 / 18.56) ** 2, 2, "1.43")
ct("T 2003-2025", T25, "5,664")
ct("weeks", len(wk), "1,185")
ct("months", len(mo), "276")
assert (min(wk_n), max(wk_n)) == (1, 6)
has("weeks of one to six sessions", "1,185 ISO weeks of one to six sessions, 276 months and 23 years")
nm("weeks a year", wpy, 2, "51.52")
has("weeks a year, in the note", "1,185/23 = 51.52 weeks or 12 months")
assert (len(sat), sat[0].isoformat(), sat[-1].isoformat(), len(six)) == (23, "2006-10-14", "2018-12-22", 17)
assert all(any(x.weekday() == 5 for x in v) for v in six) and sum(d.year <= 2025 for d in sat) == 23
has("Saturday sessions", "23 Saturday sessions (14 October 2006 to 22 December 2018), one in each of the 17 six-session weeks")
has("retrieval", "retrieved 18 October 2026")
has("first return", "3 January 2003")
has("last close", "8 October 2026")
ct("T", T, "5,849")
nm("years", years, 4, "23.7645")
nm("A", A, 2, "246.12")
has("subtitle range", "anything from 11.89% to 25.04%")

# ====================================================================== section 2
assert rank == 1 and len(all_wk) == 1224
for i, (x, pr) in enumerate(zip(wF, ("-9.6997", "-4.0161", "-5.7865", "+9.2512", "+2.7842"))):
    chk(f"E1: return {i + 1}", 100 * float(x), "+.4f", pr)
pc("E1: week's s", w_s, 2, "6.72")
ct("E1: ISO weeks of TR23", len(all_wk), "1,224")
nm("E1: sum", 100 * float(wR.sum()), 4, "-7.4669")
nm("E1: sum of the printed returns", -9.6997 - 4.0161 - 5.7865 + 9.2512 + 2.7842, 4, "-7.4669")
pc("E1: mean", w_mean, 3, "-1.493")
nm("E1: mean from the printed sum", -7.4669 / 5, 3, "-1.493")
pc("E1: median", w_med, 3, "-4.016")
pc("E1: 20% trimmed mean", w_trim, 3, "-2.339")
nm("E1: trimmed mean from printed returns", (-5.7865 - 4.0161 + 2.7842) / 3, 3, "-2.339")
has("E1: sorted", "−9.6997%, −5.7865%, −4.0161%, +2.7842% and +9.2512%".replace("−", "-"))
nm("E1: growth factor", wG, 5, "0.91697")
pc("E1: loss", 1 - wG, 3, "8.303")
pc("E1: R_G", w_RG, 3, "-1.719")
nm("E1: R_G from printed 0.91697", 100 * (0.91697**0.2 - 1), 3, "-1.719")
pc("E1: rbar", w_rbar, 3, "-1.734")
nm("E1: rbar from printed 0.91697", 100 * math.log(0.91697) / 5, 3, "-1.734")
assert abs(w_rbar - math.log(wG) / 5) < 1e-15
pc("E2: Rbar, six decimals", full["mean"], 6, "0.062505")
pc("E2: Rbar", full["mean"], 4, "0.0625")
ct("E2: median rank", ceil(0.5 * T), "2,925")
pc("E2: median (LM14's)", full["median"], 4, "0.0879")
ct("E2: j0", floor(0.05 * T), "292")
pc("E2: 5% trimmed mean", full["trim5"], 4, "0.0832")
pc("E2: rbar", rbar, 6, "0.055170")
pc("E2: R_G (LM14's)", RG, 6, "0.055185")
assert abs(RG - math.expm1(rbar)) < 1e-15
nm("E2: drag in bp", 1e4 * (full["mean"] - RG), 4, "0.7320")
nm("E2: drag from printed inputs", 100 * (0.062505 - 0.055185), 4, "0.7320")
nm("E2: s^2/2 in bp", 1e4 * full["s"] ** 2 / 2, 4, "0.7301")
nm("E2: s^2/2 from printed s", 1.2084**2 / 2, 4, "0.7301")
pc("E2: s", full["s"], 4, "1.2084")
has("KC 2: changed return", "from −9.6997% to −19.6997%".replace("−", "-"))
pc("KC 2: mean", k_mean, 3, "-3.493")
assert abs(k_mean - (w_mean - 0.02)) < 1e-15 and k_med == w_med and k_trim == w_trim

# ====================================================================== section 3
nm("LM10's factor at 4,382 days", sqrt(4382 / 4381), 6, "1.000114")
nm("Phi^-1(0.75)", Z75, 4, "0.6745")
nm("1/Phi^-1(0.75)", 1 / Z75, 4, "1.4826")
nm("2 Phi^-1(0.75)", 2 * Z75, 3, "1.349")
dw = 100 * (wR - wR.mean())
pc("E3: mean, four decimals", w_mean, 4, "-1.4934")
for i, (x, pr) in enumerate(zip(dw, ("-8.2063", "-2.5227", "-4.2931", "+10.7446", "+4.2776"))):
    chk(f"E3: deviation {i + 1}", float(x), "+.4f", pr)
nm("E3: sum of squared deviations", float((dw**2).sum()), 2, "225.88")
dw4 = np.array([-8.2063, -2.5227, -4.2931, 10.7446, 4.2776])
nm("E3: sum of squares of the printed deviations", float((dw4**2).sum()), 2, "225.88")
pc("E3: s", w_s, 3, "6.721")
nm("E3: s from printed 225.88", sqrt(225.88 / 5), 3, "6.721")
pc("E3: s_u", w_su, 3, "7.515")
nm("E3: s_u from printed 225.88", sqrt(225.88 / 4), 3, "7.515")
nm("E3: s_u / s", w_su / w_s, 3, "1.118")
pc("E3: mean absolute deviation", w_mad_mean, 3, "6.009")
nm("E3: mean absolute deviation from printed deviations", float(np.abs(dw4).mean()), 3, "6.009")
pc("E3: median", w_med, 3, "-4.016")
dmed = 100 * np.abs(wR - w_med)
for i, (x, pr) in enumerate(zip(dmed, ("5.684", "0.000", "1.770", "13.267", "6.800"))):
    if pr != "0.000":
        chk(f"E3: deviation from the median {i + 1}", float(x), ".3f", pr)
for i, x in enumerate((-9.6997, -4.0161, -5.7865, 9.2512, 2.7842)):
    assert f"{abs(x + 4.0161):.3f}" == f"{dmed[i]:.3f}", i
has("E3: deviations from the median", "5.684, 0, 1.770, 13.267 and 6.800 points")
pc("E3: MAD", w_mad, 3, "5.684")
pc("E4: s", full["s"], 4, "1.2084")
pc("E4: s_u", full["s_u"], 4, "1.2085")
pc("E4: mean absolute deviation", full["meanAD"], 3, "0.836")
nm("E4: mean absolute deviation / s", full["meanAD"] / full["s"], 3, "0.692")
nm("E4: from printed 0.836/1.2084", 0.836 / 1.2084, 3, "0.692")
nm("E4: sqrt(2/pi)", sqrt(2 / pi), 3, "0.798")
pc("E4: lower quartile", q1, 4, "-0.4904")
pc("E4: upper quartile", q3, 4, "0.6812")
pc("E4: IQR", q3 - q1, 4, "1.1716")
nm("E4: IQR from the printed quartiles", 0.6812 + 0.4904, 4, "1.1716")
pc("E4: MAD", mad_full, 4, "0.5889")
assert n_in == 2925 == ceil(T / 2) and len(devF) == len(set(devF))
has("E4: half the days", "exactly half the days, 2,925, lie within 0.5889% of the median")
pc("E4: 1.4826 MAD", full["1.4826MAD"], 3, "0.873")
nm("E4: 1.4826 x printed 0.5889", 1.4826 * 0.5889, 3, "0.873")
pc("E4: IQR/1.349", full["IQR/1.349"], 3, "0.868")
nm("E4: printed 1.1716 / 1.349", 1.1716 / 1.349, 3, "0.868")
pc("E4: annual, 1.4826 MAD", an_m, 1, "13.7")
nm("E4: annual from printed 0.873", 0.873 * sqrt(246.12), 1, "13.7")
pc("E4: annual, IQR/1.349", an_i, 1, "13.6")
nm("E4: annual from printed 0.868", 0.868 * sqrt(246.12), 1, "13.6")
pc("E4: annual, s", an_s, 2, "18.96")
nm("E4: annual from printed 1.2084", 1.2084 * sqrt(246.12), 2, "18.96")
ct("X3: windows", len(W), "5,604")
same("X3: first window end", str(ends[0]), "2003-12-29", in_md=False)
has("X3: first window end in words", "29 December 2003 to 8 October 2026")
has("X3: window quantiles", "$R_{(123)}$, $R_{(62)}$ and $R_{(185)}$")
assert (ceil(0.5 * 246), ceil(0.25 * 246), ceil(0.75 * 246)) == (123, 62, 185)
nm("X3: ratio min", float(ratio_w.min()), 2, "1.01")
nm("X3: ratio max", float(ratio_w.max()), 2, "1.72")
same("X3: ratio min date", str(ends[ratio_w.argmin()]), "2008-10-17", in_md=False)
same("X3: ratio max date", str(ends[ratio_w.argmax()]), "2020-03-30", in_md=False)
has("X3: ratio dates", "1.01 (window ending 17 October 2008) to 1.72 (30 March 2020)")
# "s stands furthest above the other two" in the same window: s / (IQR/1.349) peaks within a week of 30 March 2020
# (it falls below 1 in some windows, so the text claims only where the gap is widest, not that s always exceeds it)
ratio_iqr = roll["s"] / roll["IQR"]
assert abs(int(ratio_iqr.argmax()) - int(ratio_w.argmax())) <= 5, (ends[ratio_iqr.argmax()], ends[ratio_w.argmax()])
has("X3: where the gap is widest", "$s$ stands furthest above the other two when a few extreme days fall into a calm year")
pc("X3: last s", float(roll["s"][-1]), 1, "26.7")
pc("X3: last MAD", float(roll["MAD"][-1]), 1, "21.9")
pc("X3: last IQR", float(roll["IQR"][-1]), 1, "22.2")
has("X3: last window", "26.7%, 21.9% and 22.2%")
for k, lab, fn, d in (("s", "35.2% (15 Jun 2009)", np.argmax, "2009-06-15"), ("MAD", "31.0% (15 Dec 2008)", np.argmax,
                      "2008-12-15"), ("s", "8.2% (10 Nov 2017)", np.argmin, "2017-11-10"),
                      ("MAD", "7.6% (29 Nov 2017)", np.argmin, "2017-11-29")):
    i = int(fn(roll[k]))
    assert str(ends[i]) == d and f"{100 * roll[k][i]:.1f}%" == lab.split()[0], (k, lab)
    has(f"X3 point label {lab}", lab)
nm("KC 3: five days", sqrt(5 / 4), 3, "1.118")
nm("KC 3: TR23", sqrt(T / (T - 1)), 7, "1.0000855")

# ====================================================================== section 4
nm("E5: 23 years, skewness", sk23, 2, "-0.99")
nm("E5: 23 years, excess kurtosis", ek23, 2, "2.31")
nm("E5: 23 years, adjusted skewness", skew_adj(ann), 2, "-1.06")
nm("E5: 23 years, adjusted excess kurtosis", exk_adj(ann), 2, "3.22")
nm("E5: skewness factor", sqrt(23 * 22) / 21, 3, "1.071")
nm("E5: adjusted skewness from printed", -0.99 * 1.071, 2, "-1.06")
nm("E5: adjusted kurtosis from printed 2.31", 22 / (21 * 20) * (24 * 2.31 + 6), 2, "3.22")
assert abs(skew_closed(R) - full["skew"]) < 1e-13 and abs(exkurt_closed(R) - full["exkurt"]) < 1e-12
assert abs(full["skew_adj"] - sk_b) < 1e-13 and abs(full["exkurt_adj"] - ek_b) < 1e-13
nm("E5: TR23 skewness", full["skew"], 4, "-0.3384")
nm("E5: TR23 adjusted skewness", full["skew_adj"], 4, "-0.3385")
nm("E5: TR23 excess kurtosis", full["exkurt"], 3, "5.268")
nm("E5: TR23 adjusted excess kurtosis", full["exkurt_adj"], 3, "5.274")
nm("E5: LM4's 8.12 adjusted", k50, 2, "8.14")
ct("E5: 0050's days", n50, "2,902")
nm("octile kurtosis of a normal law", okn, 3, "1.233")
# X2, row by row (the minus sign is normalized to '-')
COLS = (full, reg7, reg10, None, plus)
NORMAL = {"mean": full["mean"], "median": full["mean"], "trim5": full["mean"], "s": full["s"], "s_u": None,
          "meanAD": sqrt(2 / pi) * full["s"], "1.4826MAD": full["s"], "IQR/1.349": full["s"], "skew": 0.0,
          "skew_adj": None, "qskew": 0.0, "exkurt": 0.0, "exkurt_adj": None, "okurt": okn}
ROWS = (("Mean (%)", "mean"), ("Median (%)", "median"), ("5% trimmed mean (%)", "trim5"), ("$s$ (%)", "s"),
        ("$s_{\\mathrm u}$ (%)", "s_u"), ("Mean absolute deviation (%)", "meanAD"), ("1.4826 MAD (%)", "1.4826MAD"),
        ("IQR/1.349 (%)", "IQR/1.349"), ("Skewness", "skew"), ("Adjusted skewness", "skew_adj"),
        ("Quartile skewness", "qskew"), ("Excess kurtosis", "exkurt"), ("Adjusted excess kurtosis", "exkurt_adj"),
        ("Octile kurtosis", "okurt"))
assert len(R[pre]) == 3077 and len(R[~pre]) == 2772
has("X2: returns row", "| Returns | 5,849 | 3,077 | 2,772 | — | 5,850 |")
for lab, key in ROWS:
    d = X2_DEC[key]
    pct = key in PCT
    vals = []
    for col in COLS:
        v = NORMAL[key] if col is None else col[key]
        if v is None:
            vals.append("—")
        elif col is None and key in ("skew", "qskew", "exkurt"):
            vals.append("0")
        else:
            vals.append(cell(v, d, pct))
            near(f"X2 {key}", 100 * v if pct else v, d)
    has(f"X2 row {key}", f"| {lab} | " + " | ".join(vals) + " |")
    for v in vals:
        COVERED.add(v.lstrip("-"))
has("X2: regime date", "before 1 June 2015 and from it")
nm("regimes: s 7% (LM15's)", 100 * reg7["s"], 3, "1.257")
nm("regimes: s 10% (LM15's)", 100 * reg10["s"], 3, "1.152")
nm("regimes: excess kurtosis 7% (LM15's)", reg7["exkurt"], 2, "3.39")
nm("regimes: excess kurtosis 10% (LM15's)", reg10["exkurt"], 2, "8.07")
nm("regimes: octile kurtosis 7%", reg7["okurt"], 3, "1.534")
nm("regimes: octile kurtosis 10%", reg10["okurt"], 3, "1.420")
c1, c2, c3, c4 = (np.cumsum(R**k) for k in (1, 2, 3, 4))
nn = np.arange(1, T + 1)
mu_run = c1 / nn
m2_run = c2 / nn - mu_run**2
m4_run = c4 / nn - 4 * mu_run * c3 / nn + 6 * mu_run**2 * c2 / nn - 3 * mu_run**4
i_a2, i_a7 = dates.index("2025-04-02"), dates.index("2025-04-07")
nm("LM15's running excess kurtosis on 2 April 2025", float(m4_run[i_a2] / m2_run[i_a2] ** 2 - 3), 2, "4.25")
nm("LM15's running excess kurtosis on 7 April 2025", float(m4_run[i_a7] / m2_run[i_a7] ** 2 - 3), 2, "4.94")
ct("E6: T + 1", T + 1, "5,850")
pc("E6: mean, relative", -rel["mean"], 1, "2.8")
pc("E6: median, relative", -rel["median"], 1, "0.4")
pc("E6: trimmed mean, relative", -rel["trim5"], 1, "0.4")
pc("E6: s, relative", rel["s"], 1, "0.6")
assert abs(rel["1.4826MAD"]) < 0.001 and abs(rel["IQR/1.349"]) < 0.001
has("E6: robust scales", "move by less than 0.1%")
nm("E6: skewness before", full["skew"], 3, "-0.338")
nm("E6: skewness after", plus["skew"], 3, "-0.425")
pc("E6: skewness, relative", rel["skew"], 0, "-26")
nm("E6: excess kurtosis before", full["exkurt"], 2, "5.27")
nm("E6: excess kurtosis after", plus["exkurt"], 2, "5.88")
pc("E6: excess kurtosis, relative", rel["exkurt"], 0, "+12", sign=True)
nm("E6: skewness change from printed", 100 * (-0.425 + 0.338) / 0.338, 0, "-26")
nm("E6: kurtosis change from printed", 100 * (5.88 - 5.27) / 5.27, 0, "12")
pc("E6: quartile skewness, relative", rel["qskew"], 1, "1.2")
pc("E6: octile kurtosis, relative", -rel["okurt"], 2, "0.05")
x4 = (R - R.mean()) ** 4
pc("LM15's top-ten share of fourth powers", float(np.sort(x4)[-10:].sum() / x4.sum()), 1, "35.0")
nm("KC 4: quartile skewness", full["qskew"], 3, "0.013")
assert (q3 - full["median"]) > (full["median"] - q1)

# ====================================================================== section 5
nm("E7: sum of products of neighbours", float((dw[1:] * dw[:-1]).sum()), 2, "31.37")
nm("E7: from the printed deviations", float((dw4[1:] * dw4[:-1]).sum()), 2, "31.37")
nm("E7: rho_1 of the week", w_rho, 3, "0.139")
nm("E7: rho_1 from printed 31.37/225.88", 31.37 / 225.88, 3, "0.139")
nm("E7: pairs of the week", w_pair, 3, "0.237")
nm("E7: TR23 rho_1", float(rho_r[0]), 4, "0.0393")
nm("E7: TR23 pairs", pr1, 4, "0.0394")
nm("E7: |r| lag 20", float(rho_a[19]), 4, "0.1224")
nm("E7: |r| lag 20 pairs", pa20, 4, "0.1228")
nm("E7: LM17's 0.123", pa20, 3, "0.123")
assert dmax < 1e-15
has("E7: statsmodels", "to within $10^{-15}$")
nm("band", band, 4, "0.0256")
nm("band, X4", band, 5, "0.02563")
has("band, chart label", "iid band ±1.96/√T = ±0.02563")
assert [k for k, _ in out_r] == [1, 4, 6, 8, 13, 14, 18, 20, 26]
has("X4: lags outside", "9 of 30 lags lie outside the band: 1, 4, 6, 8, 13, 14, 18, 20 and 26")
nm("X4: lag 29", float(rho_r[28]), 5, "-0.02561")
assert k_close == 28 and abs(rho_r[28]) < band - EPS
nm("X4: |r| lag 1", float(rho_a[0]), 3, "0.161")
nm("X4: |r| min", float(rho_a.min()), 3, "0.096")
nm("X4: |r| max", float(rho_a.max()), 3, "0.217")
assert (int(rho_a.argmin()) + 1, int(rho_a.argmax()) + 1) == (19, 3)
has("X4: |r| range", "from 0.096 (lag 19) to 0.217 (lag 3), all outside")
assert int((np.abs(rho_a) >= band - EPS).sum()) == 30 == int((np.abs(rho_q) >= band - EPS).sum())
nm("X4: r^2 lag 1", float(rho_q[0]), 3, "0.194")
nm("X4: r^2 lag 2", float(rho_q[1]), 3, "0.213")
nm("X4: r^2 lag 3", float(rho_q[2]), 3, "0.271")
nm("X4: r^2 min", float(rho_q.min()), 3, "0.046")
for lab in ("7%", "10%"):
    nm(f"regime {lab}: rho_1(r)", reg_rho[lab][0], 3, {"7%": "0.055", "10%": "0.018"}[lab])
    nm(f"regime {lab}: rho_1(|r|)", reg_rho[lab][1], 3, {"7%": "0.113", "10%": "0.217"}[lab])
pc("lag-3 share, r^2", sh_q, 1, "31.5")
pc("lag-3 share, |r|", sh_a, 1, "7.7")
nm("pitfall 5: thirty looks", 30 * 0.05, 1, "1.5")
same("KC 5: alternating six", str(Fraction(a1).limit_denominator(100)), "-5/6", in_md=False)
has("KC 5: -5/6", "-5/6=-0.833")
nm("KC 5: value", a1, 3, "-0.833")

# ====================================================================== section 6
nm("E8: 1 + rho_1", 1 + float(rho_r[0]), 4, "1.0393")
nm("E8: VR(2)", vr_o(r, 2), 4, "1.0392")
nm("E8: LM16's factor", f16, 4, "1.0797")
nm("E8: rho_1, six decimals", float(rho_r[0]), 6, "0.039337")
nm("E8: lag 1 alone", f1, 4, "1.0784")
nm("E8: lag 1 alone from printed 0.039337", 1 + 2 * 0.039337 * 245 / 246, 4, "1.0784")
nm("E8: identity column", vp246, 3, "1.280")
nm("E8: VR(246)", vo246, 3, "1.208")
ct("e = 1: samples", n_sim, "10,000")
nm("e = 1: mean VR(246)", float(mc[0]), 3, "0.960")
nm("e = 1: its standard error", float(mcse[0]), 3, "0.002")
nm("e = 1: mean VR(1231)", float(mc[1]), 3, "0.791")
nm("e = 1: its standard error", float(mcse[1]), 3, "0.005")
nm("iid factor, m = 246, T = 5,849", iid_factor(T, 246), 3, "0.958")
nm("iid factor, m = 1,231, T = 5,849", iid_factor(T, 1231), 3, "0.790")
has("e = 1: seed", "`default_rng([1, 20261011])`")
nm("overlap: (m-1)/m", 245 / 246, 3, "0.996")
nm("overlap: T/246", T / 246, 1, "23.8")
ct("overlap: windows of 1,231", T - 1231 + 1, "4,619")
nm("overlap: T/1231", T / 1231, 2, "4.75")
nm("X5: max", float(vr_tr2.max()), 3, "1.267")
ct("X5: argmax", int(mm[vr_tr2.argmax()]), "127")
ct("X5: first m below 1", int(mm[np.argmax(vr_tr2 < 1)]), "340")
assert bool((vr_tr2[mm < 340] >= 1).all()) and bool((vr_tr2[mm >= 340] < 1).all()), "VR crosses 1 more than once"
ct("X5 text: every sum of up to 339 days has VR(m) >= 1", int(mm[np.argmax(vr_tr2 < 1)]) - 1, "339")
nm("X5: at 492", v492, 3, "0.783")
nm("X5: min", float(vr_tr2.min()), 3, "0.508")
ct("X5: argmin", int(mm[vr_tr2.argmin()]), "980")
nm("X5: 2003-2025 at 246", v25, 3, "1.054")
nm("X5: 2003-2025 at 492", v25_492, 3, "0.692")
nm("X5: 2003-2025 at 1,231", v25_1231, 3, "0.468")
assert float(vr_252.min()) > 0.2   # inside the chart's y range
for m in X6_M:
    vals6 = x6[m]
    row = (f"| {m:,} | {T - m + 1:,} | {T / m:,.2f} | {vals6[0]:.3f} | {vals6[1]:.3f} | {vals6[2]:.3f} | "
           f"{vals6[3]:.3f}–{vals6[4]:.3f} | {vals6[5]:.3f} |")
    has(f"X6 row m = {m}", row)
    for v in vals6:
        near(f"X6 m={m}", v, 3)
nm("E9: sd of ln G (LM18's)", sd_own, 3, "0.283")
nm("E9: mean ln G (LM18's)", float(s1231.mean()), 3, "0.502")
nm("E9: sqrt(m) s_r (LM18's)", sqm, 3, "0.425")
nm("E9: m rbar", 1231 * rbar, 3, "0.679")
nm("E9: VR(1231)", cen, 3, "0.619")
nm("E9: ratio", cen / iid_factor(T, 1231), 2, "0.78")
nm("E9: ratio from printed", 0.619 / 0.790, 2, "0.78")
nm("KC 6", kc6, 4, "1.0533")

# ====================================================================== section 7
has("Lo (2002)", "as much as 65%")
pc("X8: Rbar", full["mean"], 4, "0.0625")
pc("X8: A Rbar", A * full["mean"], 2, "15.38")
nm("X8: A Rbar from printed", 246.12 * 0.0625, 2, "15.38")
pc("X8: rbar", rbar, 5, "0.05517")
pc("X8: A rbar", A * rbar, 2, "13.58")
nm("X8: A rbar from printed", 246.12 * 0.05517, 2, "13.58")
nm("X8: A s^2", A * full["s"] ** 2, 4, "0.0359")
nm("X8: A s_r^2", A * s_r**2, 4, "0.0361")
nm("X8: A s^2 from printed s", 246.12 * 1.2084**2 / 1e4, 4, "0.0359")
nm("X8: A s_r^2 from printed s_r", 246.12 * 1.2107**2 / 1e4, 4, "0.0361")
pc("X8: s_r", s_r, 4, "1.2107")
pc("X8: sqrt(A) s_r", sqrt(A) * s_r, 2, "18.99")
nm("X8: sqrt(A) s_r from printed", sqrt(246.12) * 1.2107, 2, "18.99")
nm("X8: SR(R) per day", sr_R, 4, "0.0517")
nm("X8: SR(R) a year", sqrt(A) * sr_R, 2, "0.81")
nm("X8: SR(r) per day", sr_r, 4, "0.0456")
nm("X8: SR(r) a year", sqrt(A) * sr_r, 3, "0.715")
nm("X8: SR(r) by (19.9)", sqrt(A) * sr_r / sqrt(vo246), 3, "0.650")
ann_simple = float(np.expm1(ann).mean())
pc("LM14's 14.97%", ann_simple, 2, "14.97")
pc("E10: sqrt(246) s_r", v_day, 3, "18.563")
nm("E10: VR(246), 2003-2025", v25, 4, "1.0536")
pc("E10: overlapping", v_ovl, 2, "19.05")
nm("E10: overlapping from printed", sqrt(1.0536) * 18.563, 2, "19.05")
pc("E10: bias-corrected", v_bias, 2, "19.48")
nm("E10: bias-corrected from printed", sqrt(1.0536 / 0.957) * 18.563, 2, "19.48")
nm("E10: iid factor at T = 5,664", iid_factor(T25, 246), 3, "0.957")
pc("E10: calendar years", v_yr, 3, "22.207")
assert [g[2] for g in grid if g[1] == 23] == list(range(7))
pc("E10: lowest grid", lo_g[0], 2, "11.89")
pc("E10: highest grid", hi_g[0], 2, "25.04")
assert (lo_g[2], hi_g[2]) == (171, 212)
pc("E10: median grid", g_med, 2, "19.13")
assert g_med == float(np.sort(gv)[122])
ct("E10: grids at or above 22.207%", n_hi, "46")
ct("E10: grids at or below 18.563%", n_lo, "113")
pc("X7: share above", n_hi / 246, 1, "18.7")
pc("X7: share below", n_lo / 246, 1, "45.9")
has("X7: median rule", "Median 19.13%, the 123rd of the 246 sorted values")
pc("P12: first grid", grid[0][0], 2, "20.18")
pc("P12: np.median of the grids", float(np.median(gv)), 2, "19.15")
ct("2026 sessions", T - T25, "185")
i_end25 = int(np.where(in25)[0][-1]) + 1   # index of 2025's last close in the closes
pc("LM17's 73.0% rise in 2026", float(tr[-1] / tr[i_end25] - 1), 1, "73.0")
ct("widget: windows", T25 - 246 + 1, "5,419")
nm("widget: T/m", T25 / 246, 1, "23.0")
pc("widget: independent days", v_day, 2, "18.56")
nm("KC 7: SR(r) per day", sr_r, 6, "0.045567")
nm("KC 7: VR(246)", vo246, 4, "1.2080")
nm("KC 7: annual", 0.045567 * sqrt(246.12), 4, "0.7149")
nm("KC 7: annual, unrounded", sqrt(A) * sr_r, 3, "0.715")
nm("KC 7: by (19.9)", 0.7149 / sqrt(1.2080), 3, "0.650")

# ====================================================================== section 8 and its code
pc("KC 8: Polars' std on the 23 years", float(ann.std(ddof=1)), 3, "22.706")
nm("KC 8: sqrt(23/22)", sqrt(23 / 22), 4, "1.0225")
nm("KC 8: 22.207 x 1.0225", 22.207 * 1.0225, 2, "22.71")
nm("code: 0.22207", v_yr, 5, "0.22207")
for c in ("# T = 5,849 simple returns", "# R_(2925)", "# 292 dropped at each end", "# -0.3384, 5.268",
          "# 5.274, adjusted", "# 0.0393, 0.0393", "# 1.208", "# 0.22207, divisor 23"):
    has(f"code comment {c}", c)
code = re.search(r"```python\n(.*?)```", MD_RAW, re.DOTALL)
assert code is not None
assert max(len(line) for line in code.group(1).splitlines()) <= 80
LAB_CSV = ROOT / "labs" / "LM19_lab" / "data" / "taiex_tr.csv"
if LAB_CSV.exists():   # run the printed code where the lab runs it, and compare what it prints
    import contextlib
    import io
    import os
    buf = io.StringIO()
    here = os.getcwd()
    os.chdir(LAB_CSV.parent.parent)
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(code.group(1), "lm19.md code", "exec"), {})  # noqa: S102 - the module's own code block
    finally:
        os.chdir(here)
    got = [float(t) for t in buf.getvalue().split()]
    want = [full["skew"], full["exkurt"], full["exkurt_adj"], float(rho_r[0]), float(rho_r[0]), vo246, v_yr]
    assert len(got) == len(want) and all(abs(a - b) < 1e-12 for a, b in zip(got, want)), (got, want)
    print(f"CHECK code block: runs and prints {len(got)} values as the module's comments say ok")
    N_CHECKS += 1
else:
    print("code block not run: labs/LM19_lab/data/taiex_tr.csv is missing (data/make_lab_data.py builds it)")

# ====================================================================== problems and solutions
for i, (x, pr) in enumerate(zip(p1, ("-4.0582", "-2.8622", "-2.3407", "-5.6081", "+6.3683"))):
    chk(f"P1: return {i + 1}", 100 * float(x), "+.4f", pr)
pc("P1: A, mean", p1_mean, 3, "-1.700")
pc("P1: B, median", p1_med, 3, "-2.862")
pc("P1: C, trimmed", p1_trim, 3, "-3.087")
nm("P1: C from printed", (-4.0582 - 2.8622 - 2.3407) / 3, 3, "-3.087")
nm("P1: A from printed", (-4.0582 - 2.8622 - 2.3407 - 5.6081 + 6.3683) / 5, 3, "-1.700")
nm("P2: A", p2[0], 2, "22.71")
nm("P2: B", p2[1], 2, "23.22")
nm("P2: C", p2[2], 2, "21.72")
nm("P3: B", p3v[0], 2, "13.70")
nm("P3: A", p3v[1], 2, "9.24")
nm("P3: C", p3v[2], 2, "6.23")
nm("P4: A", p4, 3, "0.013")
nm("P4: B", -p4, 3, "-0.013")
nm("P4: C", p4c, 3, "0.163")
nm("P4: numerator", 0.681 - 0.490 - 2 * 0.088, 3, "0.015")
nm("P4: IQR", 0.681 + 0.490, 3, "1.171")
nm("P5: C", 1 + 0.0393, 4, "1.0393")
nm("P5: A", 1 + 2 * 0.0393, 4, "1.0786")
nm("P5: B", p5, 4, "1.0195")
nm("P6: B", iid_factor(5849, 1231), 2, "0.79")
nm("P6: C", 1231 / 5849, 2, "0.21")
nm("P7: ratio", vr7, 4, "1.0797")
nm("P7: without", p7a, 2, "18.99")
nm("P7: with", p7a * sqrt(vr7), 2, "19.73")
nm("P7: with, from printed", 18.99 * sqrt(1.0797), 2, "19.73")
nm("P8: factor at T = 5,664", iid_factor(T25, 246), 3, "0.957")
nm("P8: corrected ratio", 1.0536 / iid_factor(T25, 246), 3, "1.101")
nm("P8: corrected ratio from printed", 1.0536 / 0.957, 3, "1.101")
nm("P8: annual from printed", sqrt(1.101) * 18.563, 2, "19.48")
nm("P9: SR per day", sh25, 4, "0.0400")
nm("P9: by sqrt(246)", sqrt(246) * sh25, 3, "0.627")
nm("P9: by sqrt(246), from printed", 0.0400 * sqrt(246), 3, "0.627")
nm("P9: by (19.9)", sqrt(246) * sh25 / sqrt(v25), 3, "0.611")
nm("P9: by (19.9), from printed", 0.627 / sqrt(1.0536), 3, "0.611")
pc("P9: calendar mean (LM15's)", float(ann.mean()), 3, "11.646")
nm("P9: calendar ratio", cal_sr, 3, "0.524")
nm("P9: calendar ratio from printed", 11.646 / 22.207, 3, "0.524")
pc("P9: 246 rbar (LM17's)", m246, 3, "11.634")
tq5, rt5 = t_vals[5.0]
tq3, rt3 = t_vals[3.065]
nm("P10: t5 quantile", tq5, 4, "0.7267")
nm("P10: ratio at 5", rt5, 3, "0.835")
nm("P10: ratio at 5 from printed", 0.7267 * sqrt(0.6) / 0.6745, 3, "0.835")
nm("P10: t quantile at 3.065", tq3, 4, "0.7628")
nm("P10: ratio at 3.065", rt3, 3, "0.667")
nm("P10: ratio at 3.065 from printed", 0.7628 * sqrt(1.065 / 3.065) / 0.6745, 3, "0.667")
nm("P10: TR23", tr_ratio, 3, "0.723")
nm("P11: lag 29 margin", band - abs(float(rho_r[28])), 5, "0.00002")

# ====================================================================== structure: labels and citations
ex_labels = re.findall(r"\[!exhibit\][^\n]*\{#([\w-]+)\}", MD_RAW)
eg_labels = re.findall(r"\[!example\][^\n]*\{#([\w-]+)\}", MD_RAW)
assert len(ex_labels) == 8 and len(eg_labels) == 10, (ex_labels, eg_labels)
for lab in ex_labels:
    assert f"[[ex:{lab}]]" in MD_RAW, f"exhibit {lab} is never cited"
for kind, lab in re.findall(r"\[\[(ex|eg):([\w-]+)\]\]", MD_RAW):
    assert lab in (ex_labels if kind == "ex" else eg_labels), (kind, lab)
for tag in range(1, 10):
    assert MD_RAW.count(f"\\tag{{19.{tag}}}") == 1, tag
assert "\t" not in MD_RAW
print(f"labels: {len(ex_labels)} exhibits, {len(eg_labels)} examples, tags (19.1)-(19.9), every exhibit cited")

# ====================================================================== report
body = TEXT.split("\n## Glossary", 1)[0]
nums = set(re.findall(r"(?<![\w.])\d+\.\d+|(?<![\w.,])\d{1,3}(?:,\d{3})+", body))
left = sorted(n for n in nums if n not in COVERED)
print(f"\nnumbers with a decimal point or thousands separator not covered by a check ({len(left)}):")
print("   " + " ".join(left))
print(f"\nprinted values within a tenth of a unit of a rounding boundary ({len(NEAR)}):")
for n in NEAR:
    print("   ", n)
print(f"\nanchor differences ({len(ANCHOR_DIFFS)}):")
for a in ANCHOR_DIFFS:
    print("   ", a)
print(f"\nall {N_CHECKS} checks passed")
