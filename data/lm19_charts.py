"""Chart specs for LM19 (src/data/lm19-*.json), computed from TR23.

Run:  uv run python data/lm19_charts.py      (after data/vol3_series.py; data/lm19_numbers.py checks the text)

Input: data/processed/vol3_taiex.parquet only (TR23, the TAIEX total-return index from FinMind's
TaiwanStockTotalReturnIndex), read through data/lm19_common.py, whose conventions these charts follow: one-day
statistics on simple returns, sums, autocorrelations and variance ratios on log returns; divisors the number of terms;
quantiles F^-1(u) = x_(ceil(un)); rho_k with the full-sample mean and divisor T; VR(m) the overlapping estimator (19.8).
Writes lm19-case (bar), lm19-rollscale (line, thinned to every fifth window plus every cited value), lm19-acf (bar),
lm19-vr (line, log x axis), lm19-grids (line) and lm19-aggregate (the line chart the widget "aggregate" starts from,
with the variance ratios of both samples in its "widget" block). No file carries a daily series: the rolling scales
are statistics of 246-day windows at weekly points, the rest are statistics of the whole sample.
"""
import json
from math import sqrt
from pathlib import Path
from typing import Any

import numpy as np
from lm19_common import (
    EPS,
    M_MAX,
    ROOT,
    TR23,
    YEAR,
    Z75,
    acf,
    blocks,
    iid_factor,
    period_sums,
    vr_all,
)
from numpy.lib.stride_tricks import sliding_window_view

OUT: Path = ROOT / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)


def rd(v: float, n: int) -> float:
    return round(float(v), n)


def write(name: str, spec: dict[str, Any]) -> None:
    assert isinstance(spec.get("alt"), str) and spec["alt"].strip()
    text = json.dumps(spec, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    assert len(text.encode("utf-8")) < 300_000, (name, len(text.encode("utf-8")))
    (OUT / f"{name}.json").write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote src/data/{name}.json ({len(text.encode('utf-8')):,} bytes)")


S = TR23()
R, r, T, A, dates_np = S.R, S.r, S.T, S.A, S.dates_np
r25, T25 = S.r25, S.T25
assert T == 5849 and T25 == 5664 and abs(A - 246.122955) < 1e-6

# ------------------------------------------------------------------ case: four annual standard deviations, 2003-2025
wk, _ = period_sums(S.wk_key, r25)
mo, _ = period_sums(S.mo_key, r25)
wpy = len(wk) / 23
case_vals = [sqrt(YEAR) * float(r25.std(ddof=0)), sqrt(wpy) * float(wk.std(ddof=0)), sqrt(12) * float(mo.std(ddof=0)),
             float(S.ann.std(ddof=0))]
assert [f"{100 * v:.2f}" for v in case_vals] == ["18.56", "18.09", "18.12", "22.21"]
write("lm19-case", {
    "type": "bar",
    "alt": "Annual standard deviation of TAIEX total-return log returns, 2003 to 2025, measured four ways: daily "
           "returns times the square root of 246 give 18.56%, weekly 18.09%, monthly 18.12%, while the 23 calendar "
           "years give 22.21%",
    "height": 300, "valueLabels": True,
    "categories": ["Days × √246", "Weeks × √51.52", "Months × √12", "Calendar years"],
    "x": {"label": "Log-return sums over each period, scaled to a year"},
    "y": {"fmt": "pct2", "tfmt": "pct0", "label": "Standard deviation a year", "min": 0, "max": 0.25,
          "ticks": [0, 0.05, 0.10, 0.15, 0.20, 0.25]},
    "series": [{"name": "TAIEX log returns, 2003–2025", "color": "1", "fmt": "pct2",
                "values": [rd(v, 7) for v in case_vals]}],
})

# ------------------------------------------------------------------ rollscale: three scales over 246-day windows
W = sliding_window_view(R, YEAR)
srt = np.sort(W, axis=1)
med_w = srt[:, 122]                                         # R_(123) of each window
madw = np.sort(np.abs(W - med_w[:, None]), axis=1)[:, 122]
roll = [sqrt(A) * W.std(axis=1, ddof=0), sqrt(A) * madw / Z75, sqrt(A) * (srt[:, 184] - srt[:, 61]) / (2 * Z75)]
ends = [str(d) for d in dates_np[YEAR - 1:]]
nw = len(ends)
ratio = roll[0] / roll[1]
keep = set(range(0, nw, 5)) | {nw - 1, int(ratio.argmax()), int(ratio.argmin())}
for v in roll:
    keep |= {int(v.argmax()), int(v.argmin())}
keep_l = sorted(keep)
cited = {"2009-06-15": 0.352, "2008-12-15": 0.310, "2017-11-10": 0.082, "2017-11-29": 0.076}
assert ends[int(roll[0].argmax())] == "2009-06-15" and ends[int(roll[1].argmax())] == "2008-12-15"
assert ends[int(roll[0].argmin())] == "2017-11-10" and ends[int(roll[1].argmin())] == "2017-11-29"
assert ends[int(ratio.argmax())] == "2020-03-30" and ends[int(ratio.argmin())] == "2008-10-17"
write("lm19-rollscale", {
    "alt": "Annualized scale of TAIEX daily total returns over rolling windows of 246 sessions, December 2003 to "
           "October 2026: the standard deviation peaks at 35.2% in June 2009 and bottoms at 8.2% in November 2017, "
           "and the two robust scales, 1.4826 MAD and IQR/1.349, run below it, most of all after single large days",
    "height": 320,
    "x": {"type": "date", "values": [ends[i] for i in keep_l]},
    "y": {"type": "lin", "fmt": "pct1", "tfmt": "pct0", "label": "Scale a year (× √246.12), window of 246 returns",
          "min": 0, "max": 0.40, "ticks": [0, 0.10, 0.20, 0.30, 0.40]},
    "series": [
        {"name": "Standard deviation", "color": "1", "y": [rd(roll[0][i], 5) for i in keep_l]},
        {"name": "1.4826 × MAD", "color": "2", "y": [rd(roll[1][i], 5) for i in keep_l]},
        {"name": "IQR / 1.349", "color": "3", "dash": True, "y": [rd(roll[2][i], 5) for i in keep_l]},
    ],
    "ann": [
        {"type": "point", "x": "2009-06-15", "y": rd(roll[0].max(), 5), "label": "35.2% (15 Jun 2009)", "color": "1",
         "dx": 8, "dy": -6},
        {"type": "point", "x": "2008-12-15", "y": rd(roll[1].max(), 5), "label": "31.0% (15 Dec 2008)", "color": "2",
         "anchor": "end", "dx": -8, "dy": -6},
        {"type": "point", "x": "2017-11-10", "y": rd(roll[0].min(), 5), "label": "8.2% (10 Nov 2017)", "color": "1",
         "anchor": "end", "dx": -8, "dy": 22},
        {"type": "point", "x": "2017-11-29", "y": rd(roll[1].min(), 5), "label": "7.6% (29 Nov 2017)", "color": "2",
         "dx": 8, "dy": 22},
    ],
})
for d, v in cited.items():
    assert d in [ends[i] for i in keep_l]
    i = ends.index(d)
    assert min(abs(roll[0][i] - v), abs(roll[1][i] - v)) < 0.0005, d

# ------------------------------------------------------------------ acf: r and |r|, lags 1-30, iid band
rho_r, rho_a = acf(r, 30), acf(np.abs(r), 30)
band = 1.96 / sqrt(T)
assert sum(abs(v) >= band - EPS for v in rho_r) == 9 and sum(abs(v) >= band - EPS for v in rho_a) == 30
write("lm19-acf", {
    "type": "bar",
    "alt": "Sample autocorrelations of TAIEX daily log returns and of their absolute values at lags 1 to 30, with "
           "the iid band of plus and minus 0.02563: the returns stay near the band, 9 of 30 lags just outside it, "
           "while the absolute returns lie between 0.096 and 0.217 at every lag",
    "height": 300,
    "categories": [str(k) for k in range(1, 31)],
    "x": {"label": "Lag k (sessions)"},
    "y": {"fmt": "n5", "tfmt": "n2", "label": "Sample autocorrelation", "min": -0.05, "max": 0.25,
          "ticks": [-0.05, 0, 0.05, 0.10, 0.15, 0.20, 0.25]},
    "series": [
        {"name": "r (log return)", "color": "1", "fmt": "n5", "values": [rd(v, 9) for v in rho_r]},
        {"name": "|r|", "color": "2", "fmt": "n5", "values": [rd(v, 9) for v in rho_a]},
    ],
    "ann": [{"type": "hline", "y": rd(band, 9), "label": "iid band ±1.96/√T = ±0.02563"},
            {"type": "hline", "y": rd(-band, 9)}],
})

# ------------------------------------------------------------------ vr: VR(m) on a log m axis
VR_TR = vr_all(r, M_MAX)
VR_25 = vr_all(r25, M_MAX)
ms = list(range(2, M_MAX + 1))
iid = [iid_factor(T, m) for m in ms]
ticks = [2, 5, 10, 20, 50, 100, 246, 500, 1231]
write("lm19-vr", {
    "alt": "Variance ratio VR(m) of TAIEX log returns for sums of m = 2 to 1,231 days on a logarithmic axis: the "
           "full sample rises to 1.267 at m = 127, reads 1.208 at 246 and falls to 0.619 at 1,231; 2003 to 2025 "
           "reads 1.054 at 246; the dashed curve is the iid expectation, 0.790 at 1,231",
    "height": 320,
    "x": {"type": "log", "fmt": "n0", "label": "Days in each sum, m (log scale)", "tipLabel": "m = ",
          "min": 2, "max": 1231, "ticks": ticks, "tickLabels": [f"{t:,}" for t in ticks], "values": ms},
    "y": {"type": "lin", "fmt": "n4", "tfmt": "n1", "label": "VR(m), overlapping sums of log returns", "min": 0.2,
          "max": 1.4, "ticks": [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4]},
    "series": [
        {"name": "TR23, Jan 2003 – Oct 2026", "color": "1", "y": [rd(v, 6) for v in VR_TR[1:]]},
        {"name": "2003–2025", "color": "2", "y": [rd(v, 6) for v in VR_25[1:]]},
        {"name": "iid expectation, T = 5,849", "color": "3", "dash": True, "y": [rd(v, 6) for v in iid]},
    ],
    "ann": [
        {"type": "hline", "y": 1},
        {"type": "vline", "x": 246, "dash": True},
        {"type": "vline", "x": 1231, "dash": True},
        {"type": "point", "x": 246, "y": rd(VR_TR[245], 6), "label": "1.208", "color": "1", "dx": 8, "dy": -8},
        {"type": "point", "x": 246, "y": rd(VR_25[245], 6), "color": "2"},
        {"type": "point", "x": 1231, "y": rd(VR_TR[1230], 6), "label": "0.619", "color": "1", "dx": -8, "dy": -8,
         "anchor": "end"},
    ],
})
assert [f"{VR_TR[245]:.3f}", f"{VR_25[245]:.3f}", f"{VR_TR[1230]:.3f}"] == ["1.208", "1.054", "0.619"]

# ------------------------------------------------------------------ grids: one-year block standard deviations
sd_day = sqrt(YEAR) * float(r25.std(ddof=0))
sd_ovl = sqrt(VR_25[YEAR - 1]) * sd_day
sd_cal = float(S.ann.std(ddof=0))
gv = [float(blocks(r25, YEAR, o).std(ddof=0)) for o in range(YEAR)]
xs = list(range(YEAR))
write("lm19-grids", {
    "alt": "Standard deviation of one-year log-return sums of TAIEX, 2003 to 2025, cut into consecutive blocks of 246 "
           "sessions after skipping 0 to 245 returns: it ranges from 11.89% to 25.04%, against 22.21% for the "
           "calendar years, 19.05% for overlapping one-year sums and 18.56% for days times the square root of 246",
    "height": 320,
    "x": {"type": "num", "fmt": "n0", "label": "Returns skipped before the first block, o", "tipLabel": "o = ",
          "min": 0, "max": 245, "ticks": [0, 50, 100, 150, 200, 245]},
    "y": {"type": "lin", "fmt": "pct2", "tfmt": "pct0", "label": "Standard deviation of the one-year block sums",
          "min": 0.10, "max": 0.26, "ticks": [0.10, 0.14, 0.18, 0.22, 0.26]},
    "series": [
        {"name": "246-day blocks from return o", "color": "1", "x": xs, "y": [rd(v, 7) for v in gv]},
        {"name": "Calendar years, 22.21%", "color": "2", "dash": True, "x": [0, 245], "y": [rd(sd_cal, 7)] * 2},
        {"name": "Overlapping one-year sums, 19.05%", "color": "3", "dash": True, "x": [0, 245],
         "y": [rd(sd_ovl, 7)] * 2},
        {"name": "Days × √246, 18.56%", "color": "4", "dash": True, "x": [0, 245], "y": [rd(sd_day, 7)] * 2},
    ],
    "ann": [
        {"type": "point", "x": 171, "y": rd(gv[171], 7), "label": "11.89% (o = 171)", "color": "1", "dx": 8, "dy": 16},
        {"type": "point", "x": 212, "y": rd(gv[212], 7), "label": "25.04% (o = 212)", "color": "1", "anchor": "end",
         "dx": -8, "dy": -6},
        {"type": "point", "x": 0, "y": rd(gv[0], 7), "label": "20.18% (o = 0)", "color": "1", "dx": 8, "dy": 40},
    ],
})
assert int(np.argmin(gv)) == 171 and int(np.argmax(gv)) == 212
assert [f"{100 * v:.2f}" for v in (gv[171], gv[212], gv[0], sd_cal, sd_ovl, sd_day)] == \
    ["11.89", "25.04", "20.18", "22.21", "19.05", "18.56"]

# ------------------------------------------------------------------ aggregate: the widget's initial chart and data
samples = {
    "2025": {"label": "TAIEX, 2003–2025", "T": T25, "A": YEAR, "sr": rd(float(r25.std(ddof=0)), 12),
             "cal": rd(sd_cal, 7), "vr": [rd(v, 7) for v in VR_25]},
    "all": {"label": "TAIEX, 2003 – Oct 2026", "T": T, "A": rd(A, 6), "sr": rd(float(r.std(ddof=0)), 12),
            "cal": None, "vr": [rd(v, 7) for v in VR_TR]},
}
mx = sorted({round(10 ** (k / 60)) for k in range(186)} | {YEAR, M_MAX})
mx = [m for m in mx if 1 <= m <= M_MAX]
sr0, vr0, a0, t0 = rd(float(r25.std(ddof=0)), 12), [rd(v, 7) for v in VR_25], float(YEAR), T25   # the initial sample
agg_ticks = [1, 2, 5, 10, 20, 50, 100, 246, 500, 1231]
write("lm19-aggregate", {
    "alt": "Annual volatility of TAIEX log returns, 2003 to 2025, from overlapping sums of m days, m from 1 to 1,231 "
           "on a logarithmic axis, against independent days and the iid expectation, with the calendar years' 22.21% "
           "and m = 246 marked",
    "height": 320,
    "x": {"type": "log", "fmt": "n0", "label": "Days in each sum, m (log scale)", "tipLabel": "m = ", "min": 1,
          "max": M_MAX, "ticks": agg_ticks, "tickLabels": [f"{t:,}" for t in agg_ticks], "values": mx},
    "y": {"type": "lin", "fmt": "pct2", "tfmt": "pct0", "label": "Annual volatility, √(A · VR(m)) × daily s_r",
          "min": 0.08, "max": 0.25, "ticks": [0.10, 0.15, 0.20, 0.25]},
    "series": [
        {"name": "Overlapping m-day sums", "color": "1", "y": [rd(sqrt(a0 * vr0[m - 1]) * sr0, 6) for m in mx]},
        {"name": "Independent days", "color": "2", "dash": True, "y": [rd(sqrt(a0) * sr0, 6)] * len(mx)},
        {"name": "iid expectation", "color": "3", "dash": True,
         "y": [rd(sqrt(a0 * iid_factor(t0, m)) * sr0, 6) for m in mx]},
    ],
    "ann": [{"type": "hline", "y": rd(sd_cal, 6), "dash": True, "label": "calendar years 22.21%"},
            {"type": "vline", "x": YEAR, "dash": True, "label": "m = 246"}],
    "widget": {"init": {"sample": "2025", "m": YEAR}, "mMax": M_MAX, "samples": samples},
})
v246 = vr0[YEAR - 1]
assert (f"{v246:.4f}", f"{100 * sqrt(a0 * v246) * sr0:.2f}", f"{100 * sqrt(a0) * sr0:.2f}", t0 - YEAR + 1,
        f"{t0 / YEAR:.1f}", f"{iid_factor(t0, YEAR):.3f}") == ("1.0536", "19.05", "18.56", 5419, "23.0", "0.957")
