"""Chart specs for LM26 (src/data/lm26-*.json), computed from TR23, the per-day realized variances and the 2025 TX bars.

Run:  uv run python data/lm26_charts.py
      (after data/vol3_series.py, data/vol4_series.py and data/vol4_rv.py; data/lm26_numbers.py then checks the text
      and the widget block)

Inputs and conventions: data/lm26_common.py. Writes
  lm26-vol         weekly volatility: GARCH (full-sample normal fit), EWMA 0.94 and realized, at each ISO week's last
                   session (thinned to weeks: no daily series is published, plans/vol-4.md);
  lm26-garchterm   the widget's initial chart and its "widget" block (model parameters only, no market series);
  lm26-signature   mean RV(h) / mean RV(5 min) by period, on a log x axis of the interval in seconds;
  lm26-futures     sqrt(A x mean RV(h)) of the TAIEX and of TX in 2025 (needs the raw TX bars; without them the
                   committed file is kept);
  lm26-byyear1, lm26-byyear5   RV(1 min)/RV(5 min) and RV(10 min)/RV(5 min) - 1 by year;
  lm26-qlikeyear   QLIKE by year for three forecasts, out of sample;
  lm26-y2025       2025 by ISO week: realized volatility and three forecasts, weekly means.
Volatilities are stored as fractions (0.1983 for 19.83%) and printed by the chart formats.
"""
import json
import math
from typing import Any

import lm26_common as C
import numpy as np
from lm26_common import IV, RV, V15, A, T, ann, dates, iso, qlike, rv_dates, ryear

OUT = C.ROOT / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)


def rd(x: float, n: int = 6) -> float:
    return round(float(x), n)


def write(name: str, spec: dict[str, Any]) -> None:
    assert isinstance(spec.get("alt"), str) and spec["alt"].strip()
    text = json.dumps(spec, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    assert len(text.encode("utf-8")) < 300_000, (name, len(text))
    (OUT / f"{name}.json").write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote src/data/{name}.json ({len(text.encode('utf-8')):,} bytes)")


FF = C.full_fits()
FO = C.forecasts()
FC, oos = FO["FC"], FO["oos"]
ew = C.ewma_path()
cvn, pn, pers, uvar = FF["cvn"], FF["pn"], FF["pers"], FF["uvar"]

# ---------------------------------------------------------------- X2: weekly volatility
weeks: dict[tuple[int, int], list[int]] = {}
for i, w in enumerate(iso):
    weeks.setdefault(w, []).append(i)
ends = [ids[-1] for ids in weeks.values()]
assert len(ends) == 1224
real = [rd(math.sqrt(A * float(np.mean(V15[ids]))) / 100) if dates[ids[0]] >= "2005-01-03" else None
        for ids in weeks.values()]
g_ser = [rd(math.sqrt(A) * float(cvn[i]) / 100) for i in ends]
e_ser = [rd(math.sqrt(A * float(ew[i])) / 100) for i in ends]
assert max(g_ser) == rd(math.sqrt(A) * float(cvn.max()) / 100) and max(e_ser) == rd(math.sqrt(A * float(ew[:T].max())) / 100)
assert f"{100 * max(g_ser):.2f}" == "70.41" and f"{100 * max(e_ser):.2f}" == "60.11"
assert f"{100 * max(x for x in real if x is not None):.2f}" == "100.16"
write("lm26-vol", {
    "alt": "TAIEX annualized volatility by week from January 2003 to October 2026: the in-sample GARCH conditional "
           "volatility, the EWMA forecast and realized volatility from 2005; all three peak in the week ending 11 April "
           "2025, at 70.41%, 60.11% and 100.16%",
    "height": 320,
    "x": {"type": "date", "values": [dates[i] for i in ends]},
    "y": {"type": "lin", "fmt": "pct2", "tfmt": "pct0", "label": "Annualized volatility", "min": 0, "max": 1.1,
          "ticks": [0, 0.2, 0.4, 0.6, 0.8, 1.0]},
    "series": [
        {"name": "Realized, weekly", "color": "3", "y": real},
        {"name": "EWMA 0.94", "color": "2", "y": e_ser},
        {"name": "GARCH(1,1), in-sample", "color": "1", "y": g_ser},
    ],
    "ann": [{"type": "hline", "y": rd(ann(uvar) / 100), "dash": True, "label": "unconditional 19.83%"}],
})

# ---------------------------------------------------------------- widget: the term structure of a GARCH forecast
s2_7 = float(FF["s2"][C.pos["2025-04-07"] + 1])
s2_T = float(FF["s2"][T])
W_A, W_AL, W_BE, W_U = rd(A), rd(pn[2]), rd(pn[3]), rd(uvar)
W_S = {"apr": rd(s2_7), "oct": rd(s2_T)}
mm = np.arange(1, 251)
ps_w = W_AL + W_BE
path_w = W_U + ps_w ** (mm - 1) * (W_S["apr"] - W_U)
fore = [rd(math.sqrt(W_A * x) / 100) for x in path_w]
avg = [rd(math.sqrt(W_A * float(path_w[:m].mean())) / 100) for m in mm]
hl_w = math.log(0.5) / math.log(ps_w)
write("lm26-garchterm", {
    "alt": "GARCH(1,1) variance forecasts from the evening of 7 April 2025 for 1 to 250 sessions ahead, annualized: the "
           "forecast for day t+m falls from 55.18% toward the unconditional 19.83%, and the average over the next m days "
           "from 55.18% to 32.57% at 250 sessions; half-life 44.2 sessions",
    "height": 300,
    "x": {"type": "num", "fmt": "n0", "label": "Horizon m (sessions)", "tipLabel": "m = ", "min": 1, "max": 250,
          "ticks": [1, 50, 100, 150, 200, 250]},
    "y": {"type": "lin", "fmt": "pct2", "tfmt": "pct0", "label": "Annualized volatility", "min": 0, "max": 0.8,
          "ticks": [0, 0.2, 0.4, 0.6, 0.8]},
    "series": [
        {"name": "Forecast for day t+m", "color": "1", "x": mm.tolist(), "y": fore},
        {"name": "Average over the next m days", "color": "2", "x": mm.tolist(), "y": avg},
    ],
    "ann": [{"type": "hline", "y": rd(math.sqrt(W_A * W_U) / 100), "dash": True},
            {"type": "vline", "x": rd(hl_w, 3), "dash": True, "label": f"half-life {hl_w:.1f}"}],
    "widget": {"A": W_A, "alpha": W_AL, "beta": W_BE, "uvar": W_U, "start": W_S, "mMax": 250,
               "init": {"start": "apr"}},
})

# ---------------------------------------------------------------- X4: the signature by period
d_arr = np.array(rv_dates)
periods = [
    ("2005–2010 (1-minute data)", (d_arr >= "2005-01-01") & (d_arr <= "2010-12-31")),
    ("2011–2012 (15-second data)", (d_arr >= "2011-01-17") & (d_arr <= "2012-12-31")),
    ("2015–2026 (5-second data)", d_arr >= "2015-01-01"),
    ("2025", ryear == "2025"),
]
xs = [h for _, h in IV]
# every interval is a tick, but only five are labelled, so that the labels do not collide at 400 px
labels = ["5 s", "", "15 s", "", "1 min", "5 min", "", "", "30 min"]
sig_series = []
for (pname, msk), col in zip(periods, ("4", "2", "1", "3")):
    m5 = float(np.mean(RV["5m"][msk]))
    vals = [None if np.isnan(RV[name][msk]).any() else rd(float(np.mean(RV[name][msk])) / m5) for name, _ in IV]
    sig_series.append({"name": pname, "color": col, "y": vals})
write("lm26-signature", {
    "alt": "Volatility signature of the TAIEX: mean realized variance at intervals from 5 seconds to 30 minutes over its "
           "mean at 5 minutes, log scales; on 5-second data it rises steeply as the interval shrinks (11.71 at 5 seconds "
           "in 2015-2026, 24.26 in 2025), while on 1-minute data of 2005-2010 it falls (0.483 at 1 minute)",
    "height": 320,
    "x": {"type": "log", "fmt": "n0", "label": "Sampling interval h (log scale)", "tipLabel": "h (seconds): ",
          "values": xs, "ticks": xs, "tickLabels": labels},
    "y": {"type": "log", "fmt": "n3", "tfmt": "n1", "label": "Mean RV(h) / mean RV(5 min), log scale", "min": 0.4,
          "max": 30, "ticks": [0.5, 1, 2, 5, 10, 20]},
    "series": sig_series,
    "ann": [{"type": "hline", "y": 1, "dash": True}],
})

# ---------------------------------------------------------------- X5: index against TX, 2025
TX = C.tx25()
m25 = ryear == "2025"
if TX is not None:
    TXA = TX["RV"]
    idx = [rd(math.sqrt(A * float(np.mean(RV[name][m25])))) for name, _ in IV]      # RV in decimals: a fraction
    txm = {"1m": 1, "5m": 5, "10m": 10, "15m": 15, "30m": 30}      # interval name -> TX bar count
    tx_ser = [rd(math.sqrt(A * float(TXA[txm[name]].mean()))) if name in txm else None for name, _ in IV]
    # the values the alt text and E9 cite (A26-40, A26-41), in percent
    assert [f"{100 * idx[0]:.2f}", f"{100 * idx[4]:.1f}", f"{100 * idx[-1]:.2f}"] == ["65.27", "22.8", "9.91"]
    assert f"{100 * (tx_ser[4] or 0):.2f}" == "9.26"
    write("lm26-futures", {
        "alt": "Annualized volatility of the window 09:30-13:30 in 2025 against the sampling interval, log scales: the "
               "TAIEX falls from 65.27% at 5 seconds to 9.91% at 30 minutes, while the near-month TX future stays near "
               "9.3% from 1 to 30 minutes",
        "height": 300,
        "x": {"type": "log", "fmt": "n0", "label": "Sampling interval h (log scale)", "tipLabel": "h (seconds): ",
              "values": xs, "ticks": xs, "tickLabels": labels},
        "y": {"type": "log", "fmt": "pct2", "tfmt": "pct0", "label": "Annualized volatility, log scale", "min": 0.08,
              "max": 0.8, "ticks": [0.1, 0.2, 0.5]},
        "series": [
            {"name": "TAIEX (5-second data)", "color": "1", "y": idx},
            {"name": "TX near month (1-minute bars)", "color": "2", "y": tx_ser},
        ],
    })
else:
    assert (OUT / "lm26-futures.json").exists(), "no TX bars and no committed lm26-futures.json"
    print("kept src/data/lm26-futures.json (the raw TX 1-minute bars are missing)")

# ---------------------------------------------------------------- X6: ratios by year
years = sorted(set(ryear))
top = [rd(float(np.mean(RV["1m"][ryear == yy]) / np.mean(RV["5m"][ryear == yy]))) for yy in years]
bot = [rd(float(np.mean(RV["10m"][ryear == yy]) / np.mean(RV["5m"][ryear == yy]) - 1)) for yy in years]
write("lm26-byyear1", {
    "type": "bar",
    "alt": "RV(1 min) over RV(5 min) of the TAIEX by year, 2005 to 2026: below 1 in 2005-2012 and 2020, from 0.397 in "
           "2008 to 2.968 in 2025",
    "height": 240, "categories": years, "x": {"label": "Year"},
    "y": {"fmt": "n3", "tfmt": "n1", "label": "RV(1 min) ÷ RV(5 min)", "min": 0, "max": 3.2,
          "ticks": [0, 0.5, 1, 1.5, 2, 2.5, 3]},
    "series": [{"name": "RV(1 min) ÷ RV(5 min)", "color": "1", "values": top, "fmt": "n3"}],
    "ann": [{"type": "hline", "y": 1}],
})
write("lm26-byyear5", {
    "type": "bar",
    "alt": "RV(10 min) over RV(5 min), minus 1, of the TAIEX by year, 2005 to 2026: from 0.256 in 2007 to -0.257 in 2025",
    "height": 240, "categories": years, "x": {"label": "Year"},
    "y": {"fmt": "n3", "tfmt": "n1", "label": "RV(10 min) ÷ RV(5 min) − 1", "min": -0.3, "max": 0.3,
          "ticks": [-0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3]},
    "series": [{"name": "RV(10 min) ÷ RV(5 min) − 1", "color": "2", "values": bot, "fmt": "n3"}],
    "ann": [{"type": "hline", "y": 0}],
})

# ---------------------------------------------------------------- X8: QLIKE by year
oy = np.array([dates[i][:4] for i in oos])
oyears = sorted(set(oy))
hV = V15[oos]
qy = {k: [rd(float(qlike(hV[oy == yy], FC[k][oos][oy == yy]).mean())) for yy in oyears] for k in ("garch_n", "ewma",
                                                                                                    "v_prev")}
write("lm26-qlikeyear", {
    "type": "bar",
    "alt": "Mean QLIKE by year, 2008 to 2026, of the out-of-sample GARCH normal, EWMA 0.94 and yesterday's realized "
           "variance forecasts against the target V; GARCH is below EWMA in 12 of 19 years, and yesterday's V is worst "
           "in every year",
    "height": 280, "categories": oyears, "x": {"label": "Year (2026 to 8 October)"},
    "y": {"fmt": "n3", "tfmt": "n1", "label": "Mean QLIKE", "min": 0, "max": 2,
          "ticks": [0, 0.5, 1, 1.5, 2]},
    "series": [
        {"name": "GARCH normal", "color": "1", "values": qy["garch_n"], "fmt": "n3"},
        {"name": "EWMA 0.94", "color": "2", "values": qy["ewma"], "fmt": "n3"},
        {"name": "Yesterday's V", "color": "3", "values": qy["v_prev"], "fmt": "n3"},
    ],
})

# ---------------------------------------------------------------- X9: 2025 by week
w25 = sorted({iso[i] for i in oos if dates[i].startswith("2025")})
wk = [[i for i in oos if iso[i] == w and dates[i].startswith("2025")] for w in w25]
assert len(wk) == 52 and sum(len(ids) for ids in wk) == 243


def wmean(arr: np.ndarray) -> list[float]:
    return [rd(math.sqrt(A * float(np.mean(arr[ids]))) / 100) for ids in wk]


ids25 = [i for ids in wk for i in ids]
real25 = math.sqrt(A * float(np.mean(V15[ids25]))) / 100
write("lm26-y2025", {
    "alt": "Annualized volatility in 2025 by ISO week, out of sample: realized volatility from 5-second data against the "
           "weekly mean forecasts of GARCH normal, EWMA 0.94 and yesterday's realized variance; in the week of 7 April "
           "realized volatility was 100.16%, GARCH 55.86%, EWMA 47.22% and yesterday's V 99.52%",
    "height": 300,
    "x": {"type": "date", "values": [dates[ids[-1]] for ids in wk]},
    "y": {"type": "lin", "fmt": "pct2", "tfmt": "pct0", "label": "Annualized volatility", "min": 0, "max": 1.1,
          "ticks": [0, 0.2, 0.4, 0.6, 0.8, 1.0]},
    "series": [
        {"name": "Realized", "color": "3", "y": wmean(V15)},
        {"name": "Yesterday's V", "color": "4", "y": wmean(FC["v_prev"])},
        {"name": "EWMA 0.94", "color": "2", "y": wmean(FC["ewma"])},
        {"name": "GARCH normal", "color": "1", "y": wmean(FC["garch_n"])},
    ],
    "ann": [{"type": "hline", "y": rd(real25), "dash": True, "label": f"2025 realized {100 * real25:.2f}%"}],
})
