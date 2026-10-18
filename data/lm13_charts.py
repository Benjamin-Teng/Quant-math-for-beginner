"""Chart specs for LM13 (src/data/lm13-*.json), computed from TR23.

Run:  uv run python data/lm13_charts.py      (after data/vol3_series.py; data/lm13_numbers.py checks the text)

Input: data/processed/vol3_taiex.parquet only, through data/lm13_common.py (same sample and guard as the numbers
script: T = 5,849 simple daily returns 2003-01-03 .. 2026-10-08; the pair space is the 5,848 return dates with a
previous return; thresholds inclusive, counted with the guard and checked against exact fractions).
Writes lm13-venn (two events on the pair space), lm13-buckets (a fall by yesterday's return), lm13-ecdf (the
empirical distribution function), lm13-bins (the pmf of the 1% bin) and lm13-bayes (the case's four counts as a bar
chart, with the widget's data in its "widget" block).
"""
import json
from pathlib import Path

import numpy as np
from lm13_common import (
    BIN_NAMES,
    BINS,
    BUCKET_NAMES,
    BUCKETS,
    at_least,
    at_most,
    bucket,
    load,
)

OUT = Path(__file__).resolve().parent.parent / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)


def write(name: str, spec: dict) -> None:
    (OUT / f"{name}.json").write_text(json.dumps(spec, ensure_ascii=False, separators=(",", ":"), allow_nan=False),
                                      encoding="utf-8", newline="\n")
    print("wrote", f"src/data/{name}.json")


tr = load()
T, R = tr.T, tr.R
assert T == 5849
nP = T - 1

# ------------------------------------------------------------------ venn: falls of 2% or more today and yesterday
f2 = at_most(tr, -2)
today, yest = f2[1:], f2[:-1]
n_t, n_y, n_b = int(today.sum()), int(yest.sum()), int((today & yest).sum())
n_neither = nP - int((today | yest).sum())
assert (n_t, n_y, n_b, n_neither) == (252, 252, 38, 5382)
x0, x1, y0, y1 = 0.3, 11.7, 0.3, 7.0
hidden = {"color": "transparent", "dx": -8, "dy": 12, "anchor": "middle"}
venn = {
    "type": "vector", "alt": "Two overlapping circles inside a rectangle of the 5,848 days of the pair space: 214 days "
    "fell 2% or more today only, 214 only yesterday, 38 on both days, and 5,382 on neither",
    "height": 300,
    "x": {"min": 0, "max": 12, "ticks": [], "name": "position", "fmt": "n1"},
    "y": {"min": 0, "max": 7.3, "ticks": [], "name": "position", "fmt": "n1"},
    "lines": [{"from": a, "to": b, "color": "var(--ink-2)"} for a, b in
              (([x0, y0], [x1, y0]), ([x1, y0], [x1, y1]), ([x1, y1], [x0, y1]), ([x0, y1], [x0, y0]))],
    "ellipses": [{"center": [4.6, 3.6], "cov": [[6.25, 0], [0, 6.25]], "color": "1", "fill": True},
                 {"center": [7.4, 3.6], "cov": [[6.25, 0], [0, 6.25]], "color": "2", "fill": True}],
    "points": [{"at": [3.3, 3.4], "label": f"{n_t - n_b}", **hidden},
               {"at": [6.0, 3.4], "label": f"{n_b}", **hidden},
               {"at": [8.7, 3.4], "label": f"{n_y - n_b}", **hidden},
               {"at": [0.6, 6.45], "label": "A (today)", "color": "transparent", "dx": -8, "dy": 12,
                "anchor": "start"},
               {"at": [11.4, 6.45], "label": "B (yesterday)", "color": "transparent", "dx": -8, "dy": 12,
                "anchor": "end"},
               {"at": [6.0, 0.85], "label": f"{n_neither:,} days in neither", **hidden}],
}
write("lm13-venn", venn)

# ------------------------------------------------------------------ buckets: a fall today by yesterday's return
fall = at_most(tr, -3)
A = fall[1:]
yR = R[:-1]
shares, days, falls = [], [], []
for lo, hi in BUCKETS:
    m = bucket(yR, None if lo is None else lo / 100, None if hi is None else hi / 100)
    days.append(int(m.sum()))
    falls.append(int((m & A).sum()))
    shares.append(round(falls[-1] / days[-1], 10))
assert sum(days) == nP and sum(falls) == int(A.sum()) == 108
buckets = {
    "type": "bar", "alt": "Share of days that fell 3% or more, by yesterday's return in eight buckets: highest after a "
    "fall of 3% or more (12.04%) and raised in both tails, against 1.85% for all days",
    "height": 300, "categories": BUCKET_NAMES, "valueLabels": True,
    "x": {"label": "Yesterday's return (%), each bucket including its upper end"},
    "y": {"fmt": "pct2", "tfmt": "pct0", "label": "Share of days that fell 3% or more today", "min": 0, "max": 0.14,
          "ticks": [0, 0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.14]},
    "series": [{"name": "Fell 3% or more today", "color": "1", "values": shares}],
    "ann": [{"type": "hline", "y": round(108 / nP, 10), "label": "all days, 1.85%", "dash": True}],
}
write("lm13-buckets", buckets)

# ------------------------------------------------------------------ ecdf: the empirical distribution function
rs = np.sort(R)
assert rs[0] > -0.10 and rs[-1] < 0.10
xs = [-0.10] + [round(float(v), 10) for v in rs] + [0.10]
ys = [0.0] + [round((k + 1) / T, 8) for k in range(T)] + [1.0]
pts = {c: int(at_most(tr, c).sum()) for c in (-3, 0, 3)}
assert pts == {-3: 108, 0: 2644, 3: 5782}
ecdf = {
    "alt": "The empirical distribution function of TR23's 5,849 daily returns, a step function rising from 0 to 1 "
    "between −9.70% and +9.25%: 0.0185 at −3%, 0.4520 at 0 and 0.9885 at +3%",
    "height": 320,
    "x": {"type": "num", "fmt": "pct2", "tfmt": "pct0", "label": "Daily return x", "tipLabel": "x = ",
          "min": -0.10, "max": 0.10, "ticks": [-0.10, -0.05, -0.03, 0, 0.03, 0.05, 0.10]},
    "y": {"type": "lin", "fmt": "n4", "tfmt": "n1", "label": "Share of days at or below x", "min": 0, "max": 1,
          "ticks": [0, 0.2, 0.4, 0.6, 0.8, 1]},
    "series": [{"name": "Empirical distribution function", "color": "1", "step": True, "x": xs, "y": ys}],
    "ann": [{"type": "point", "x": -0.03, "y": round(pts[-3] / T, 10), "label": "−3%: 0.0185", "color": "2"},
            {"type": "point", "x": 0, "y": round(pts[0] / T, 10), "label": "0: 0.4520", "color": "2",
             "anchor": "end", "dx": -8, "dy": -6},
            {"type": "point", "x": 0.03, "y": round(pts[3] / T, 10), "label": "+3%: 0.9885", "color": "2",
             "dy": 16}],
}
write("lm13-ecdf", ecdf)

# ------------------------------------------------------------------ bins: the pmf of the 1% bin of R
counts = [int(bucket(R, None if lo is None else lo / 100, None if hi is None else hi / 100).sum()) for lo, hi in BINS]
assert sum(counts) == T and counts[:3] == [15, 29, 64] and sum(counts[:3]) == 108
bins = {
    "type": "bar", "alt": "Probability mass function of the 1% bin of a TR23 daily return, twelve bins from 5% or "
    "below to above 5%, highest for the bins from −1% to 0 (32.07%) and from 0 to 1% (38.84%)",
    "height": 300, "categories": BIN_NAMES, "valueLabels": True,
    "x": {"label": "Bin of the daily return (%), each bin including its upper end"},
    "y": {"fmt": "pct2", "tfmt": "pct0", "label": "Probability", "min": 0, "max": 0.45,
          "ticks": [0, 0.1, 0.2, 0.3, 0.4]},
    "series": [{"name": "Share of the 5,849 days", "color": "1", "values": [round(c / T, 10) for c in counts]}],
}
write("lm13-bins", bins)

# ------------------------------------------------------------------ bayes: the case's counts and the widget's data
big = (at_least(tr, 2) | at_most(tr, -2))[:-1]
nA, nB, nAB = int(A.sum()), int(big.sum()), int((A & big).sum())
cells = [nAB, nA - nAB, nB - nAB, nP - nA - nB + nAB]
assert cells == [32, 76, 457, 5283]
bayes = {
    "type": "bar", "alt": "The 5,848 days of the pair space by yesterday's move and today's fall: 32 falls and 457 "
    "other days after a big move, 76 falls and 5,283 other days after a smaller move",
    "height": 260,
    "categories": ["Fall after a big move", "Fall after a smaller move", "Big move, no fall", "Neither"],
    "valueLabels": True, "x": {"label": "Day of the pair space"}, "y": {"fmt": "n0", "label": "Days"},
    "series": [{"name": "Days", "color": "1", "values": cells}],
    "widget": {"N": nP, "A": nA, "B": nB, "AB": nAB},
}
write("lm13-bayes", bayes)
print(f"buckets {list(zip(days, falls, strict=True))}; bins {counts}; case cells {cells}")
