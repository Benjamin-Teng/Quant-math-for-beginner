"""Chart specs for LM34 (src/data/lm34-*.json), computed from the through case, TR23 and LM34's grid.

Run:  PYTHONUTF8=1 uv run python data/lm34_charts.py
      (after data/vol3_series.py, data/vol5_series.py and data/vol5_rules.py; data/lm34_numbers.py then checks the
      text against the same computations)

Inputs and conventions: data/lm34_common.py (the anchor script's computations, imported, about a minute). Writes
  lm34-wealth     the eight rules' net wealth at the last session of each ISO week (week keys by ISO year and week),
                  from the first trade's close to 2026-10-08, plus the first and last sessions (every cited value);
                  R1, R2, R4 and R8 named, R3, R5, R6 and R7 as quiet lines (X37: weekly points, no daily series);
  lm34-grossnet   net growth and the gross-minus-net part of the eight rules (stacked bars, totals = gross growth);
  lm34-survivors  the six futures ETFs' growth factors, survivors and delisted as two series, with the two means;
  lm34-rc         experiment 1's 10,000 resampled maxima of the studentized statistic on Experiment 10 as a density in
                  bins of 0.1 (a step line), and (21.9)'s density for the largest of 10,000 independent normals;
  lm34-bumps      the grid's 60 net growth rates by rule, window and frequency, the through case's eight ringed;
  lm34-logits     the 12,870 splits' logits in 18 bins of 0.5 and the noise panels' mean histogram;
  lm34-degrade    the in-sample best's in-sample against out-of-sample Sharpe ratio, every fifth split, annualized,
                  with the OLS line of all 12,870 splits and the means;
  lm34-pboSim     the widget's fallback chart and its "widget" block: experiment 3's 30 mean PBOs, their largest SE,
                  and a synthetic 160 x 5 test matrix (default_rng([7, 20261011]), experiment 7, normal draws, no
                  market data) with its Python PBO and logit histogram.
No published file carries a daily series (plans/vol-5.md, "Charts", X37). The script then runs the widget's CSCV
(src/lm34.js, Book.widgets.pboSim.math) in Node on the test matrix against Python's cscv() and stops on a logit
difference above 1e-12; it also times one widget panel at the initial state (n = 60, ratio 0, seed 1).
"""
import json
import math
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lm34_common as C
import numpy as np
from scipy import stats

ROOT = HERE.parent
OUT = ROOT / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)
K = C.KEEP
RULES = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]


def rd(x: float, n: int = 6) -> float:
    return round(float(x), n)


def write(name: str, spec: dict[str, Any]) -> None:
    assert isinstance(spec.get("alt"), str) and spec["alt"].strip()
    text = json.dumps(spec, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    assert len(text.encode("utf-8")) < 300_000, (name, len(text))
    (OUT / f"{name}.json").write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote src/data/{name}.json ({len(text.encode('utf-8')):,} bytes)")


# ---------------------------------------------------------------- X2: net wealth, weekly points
case = K["case"]
dates: list[str] = case.paths["R1"].dates
keep = [i for i in range(len(dates))
        if i == 0 or i == len(dates) - 1
        or date.fromisoformat(dates[i]).isocalendar()[:2] != date.fromisoformat(dates[i + 1]).isocalendar()[:2]]
assert keep[0] == 0 and dates[keep[-1]] == "2026-10-08" and len(keep) < 1172
COLOR = {"R1": "1", "R2": "2", "R4": "3", "R8": "4"}
NAME = {"R1": "R1 equal weights", "R2": "R2 reference mix", "R4": "R4 maximum Sharpe", "R8": "R8 volatility target"}
series: list[dict[str, Any]] = []
for k in RULES:
    w = case.paths[k].wealth
    s: dict[str, Any] = {"name": NAME.get(k, k), "y": [rd(w[i], 5) for i in keep]}
    if k in COLOR:
        s.update(color=COLOR[k], endLabel=f"{k} {w[-1]:.3f}")
    else:
        s["quiet"] = True
    series.append(s)
finals = {k: f"{case.paths[k].wealth[-1]:.3f}" for k in RULES}
assert list(finals.values()) == ["2.662", "3.008", "1.937", "2.221", "2.040", "2.272", "2.183", "2.412"]
write("lm34-wealth", {
    "alt": "Net wealth of the eight rules from the cash of 1 on 4 March 2019 to 8 October 2026, weekly: R2 ends at "
           "3.008, R1 at 2.662, R8 at 2.412 and R4 at 2.221; the four other rules, in grey, end between 1.937 and "
           "2.272",
    "height": 320, "endLabels": True,
    "x": {"type": "date", "values": [dates[i] for i in keep]},
    "y": {"type": "lin", "fmt": "n3", "tfmt": "n1", "label": "Net wealth", "min": 0.6, "max": 3.4,
          "ticks": [1, 1.5, 2, 2.5, 3]},
    "series": series,
    "ann": [{"type": "hline", "y": 1, "dash": True}],
})

# ---------------------------------------------------------------- X3: gross against net growth
net = [float(K["summ"][k]["growth"]) for k in RULES]
gross = [float(K["gsum"][k]["growth"]) for k in RULES]
assert [f"{100 * g:.2f}" for g in gross] == ["12.99", "14.58", "8.85", "11.06", "9.52", "10.91", "10.44", "11.99"]
write("lm34-grossnet", {
    "type": "bar", "stack": True, "valueLabels": True, "height": 300,
    "alt": "Gross growth of the eight rules split into net growth and the part that commission and tax remove: "
           "from 0.08 points a year for R2 to 0.56 for R4 and 0.40 for R8",
    "categories": RULES, "x": {"label": ""},
    "y": {"fmt": "pct2", "tfmt": "pct0", "label": "Log growth a year", "min": 0, "max": 0.16,
          "ticks": [0, 0.04, 0.08, 0.12, 0.16]},
    "series": [{"name": "net growth", "color": "1", "values": [rd(x, 8) for x in net], "fmt": "pct2"},
               {"name": "commission and tax", "color": "2", "values": [rd(g - x, 8) for g, x in zip(gross, net,
                                                                                                    strict=True)],
                "fmt": "pct2"}],
})

# ---------------------------------------------------------------- X5: survivorship
g6, dld = K["g6"], K["dld"]
F6 = list(C.FUTURES6)
assert F6 == ["00635U", "00642U", "00672L", "00673R", "00674R", "00677U"]
fac = {s: float(g6[s][0]) for s in F6}
assert [f"{fac[s]:.3f}" for s in F6] == ["2.198", "1.593", "0.038", "0.140", "0.285", "0.086"]
write("lm34-survivors", {
    "type": "bar", "valueLabels": True, "height": 300,
    "alt": "Growth factors of the six gold, oil and VIX futures ETFs of January 2017 to October 2026: 00635U 2.198, "
           "00642U 1.593, 00673R 0.140 and 00674R 0.285 survived; 00672L (0.038) and 00677U (0.086) were delisted; "
           "the mean of all six is 0.723 and of the survivors 1.054",
    "categories": F6, "x": {"label": ""},
    "y": {"fmt": "n3", "tfmt": "n1", "label": "Growth factor", "min": 0, "max": 2.4, "ticks": [0, 0.5, 1, 1.5, 2]},
    "series": [{"name": "survivors", "color": "1", "values": [None if s in dld else rd(fac[s], 6) for s in F6],
                "fmt": "n3"},
               {"name": "delisted", "color": "2", "values": [rd(fac[s], 6) if s in dld else None for s in F6],
                "fmt": "n3"}],
    "ann": [{"type": "hline", "y": rd(K["all6"], 6), "label": f"all six {K['all6']:.3f}"},
            {"type": "hline", "y": rd(K["sur6"], 6), "label": f"survivors {K['sur6']:.3f}"}],
})

# ---------------------------------------------------------------- X6: the reality check on Experiment 10
rc = K["rc10"]
mt = np.asarray(rc["mt"], dtype=float)
lo, hi = math.floor(mt.min() * 10) / 10, math.ceil(mt.max() * 10) / 10
edges = np.round(np.arange(lo, hi + 0.05, 0.1), 10)
cnt = np.histogram(mt, bins=edges)[0]
assert int(cnt.sum()) == len(mt) == 10_000
dens = cnt / (len(mt) * 0.1)
xs = np.round(np.arange(float(edges[0]), float(edges[-1]) + 1e-9, 0.02), 10)   # the axis spans every bin
d219 = 10_000 * stats.norm.pdf(xs) * stats.norm.cdf(xs) ** (10_000 - 1)
t_best = float(rc["tt"][rc["best"]])
assert (f"{t_best:.2f}", f"{rc['q95']:.2f}", f"{rc['q95_219']:.2f}") == ("3.97", "4.77", "4.41")
write("lm34-rc", {
    "alt": "Density of the 10,000 resampled maxima of the studentized statistic on Experiment 10, as steps, against "
           "the density of the largest of 10,000 independent normals; the observed best t-stat 3.97 lies below both "
           "95% points, 4.77 and 4.41",
    "height": 300,
    "x": {"type": "num", "fmt": "n2", "tfmt": "n0", "label": "Largest t-stat", "min": float(edges[0]),
          "max": float(edges[-1]), "ticks": list(range(math.ceil(edges[0]), math.floor(edges[-1]) + 1))},
    "y": {"type": "lin", "fmt": "n3", "tfmt": "n1", "label": "Density", "min": 0},
    "series": [{"name": "bootstrap maxima", "color": "1", "step": True, "x": [float(e) for e in edges],
                "y": [rd(v, 6) for v in dens]},
               {"name": "(21.9), independent normals", "color": "2", "x": [float(x) for x in xs],
                "y": [rd(v, 6) for v in d219]}],
    "ann": [{"type": "vline", "x": rd(t_best, 4), "dash": True, "label": "3.97"},
            {"type": "vline", "x": rd(rc["q95"], 4), "dash": True, "label": "4.77"},
            {"type": "vline", "x": rd(rc["q95_219"], 4), "dash": True, "label": "4.41"}],
})

# ---------------------------------------------------------------- X7: the highest bump
G = K["grid"]
conf, growth = G["conf"], G["growth"]
WIN = {126: 0, 252: 1, 504: 2}
FREQ = {1: 0, 3: 1, 6: 2}
FNAME = {1: "monthly", 3: "every 3 month-ends", 6: "every 6 month-ends"}


def xpos(rule: str, w: int, q: int) -> float:
    r = RULES.index(rule) + 1
    if w == 0:
        return r + (FREQ[q] - 1) * 0.08
    return r + (WIN[w] - 1) * 0.25 + (FREQ[q] - 1) * 0.07


pts = {q: ([], []) for q in (1, 3, 6)}
for (k, w, q), g in zip(conf, growth, strict=True):
    pts[q][0].append(rd(xpos(k, w, q), 4))
    pts[q][1].append(rd(g, 6))
marked = []
for k in RULES:
    i = G["tcase"][RULES.index(k)]
    kk, w, q = conf[i]
    marked.append({"at": [rd(xpos(kk, w, q), 4), rd(growth[i], 6)], "r": 7})
med = float(G["med"])
assert (f"{100 * max(growth):.2f}", f"{100 * med:.2f}", f"{100 * min(growth):.2f}") == ("18.62", "10.96", "7.60")
write("lm34-bumps", {
    "type": "scatter", "equal": False, "height": 320,
    "alt": "Net growth of the grid's 60 configurations by rule: R4's nine run from 10.51% to 18.62%, the best, while "
           "R1's three lie between 12.85% and 12.96%; the median is 10.96% and the worst 7.60% (R7)",
    "x": {"label": "Rule (within each: 126, 252, 504 dates)", "fmt": "n2", "min": 0.5, "max": 8.7,
          "ticks": [1, 2, 3, 4, 5, 6, 7, 8], "tickLabels": RULES, "name": "position"},
    "y": {"label": "Net growth a year", "fmt": "pct2", "tfmt": "pct0", "min": 0.06, "max": 0.2,
          "ticks": [0.06, 0.1, 0.14, 0.18], "name": "growth"},
    "series": [{"name": FNAME[q], "color": str(c), "x": pts[q][0], "y": pts[q][1], "r": 3.5}
               for c, q in zip((1, 2, 3), (1, 3, 6), strict=True)],
    "points": marked,
    "lines": [{"from": [0.5, rd(med, 6)], "to": [8.7, rd(med, 6)], "dash": True, "label": "median 10.96%"}],
})

# ---------------------------------------------------------------- X8: the logits
hist = [int(h) for h in G["hist"]]
assert hist == [797, 0, 276, 1016, 1758, 1161, 823, 1171, 1528, 1174, 889, 859, 818, 418, 161, 21, 0, 0]
centres = [f"{c:+.2f}".replace("-", "−").replace("+", "") for c in np.arange(-4.25, 4.26, 0.5)]
noise_hist = [rd(h, 3) for h in K["noise"]["hist"]]
write("lm34-logits", {
    "type": "bar", "valueLabels": False, "height": 300,
    "alt": "Histogram of the 12,870 splits' logits on the declared grid, mostly below 0 (PBO 0.663), against the "
           "mean histogram of 200 panels of skill-free strategies, centred near 0",
    "categories": centres, "x": {"label": "Logit, bin centre"},
    "y": {"fmt": "n0", "tfmt": "n0", "label": "Splits", "min": 0, "ticks": [0, 500, 1000, 1500, 2000]},
    "series": [{"name": "the grid", "color": "1", "values": hist, "fmt": "n0"},
               {"name": "noise, mean of 200 panels", "color": "2", "values": noise_hist, "fmt": "n0"}],
})

# ---------------------------------------------------------------- X9: performance degradation
aw = case.fr.A_wealth
is_ = np.asarray(G["is"]) * math.sqrt(aw)
oos = np.asarray(G["oos"]) * math.sqrt(aw)
sel = np.arange(0, len(is_), 5)
assert len(sel) == 2574
sl, ic = float(G["slope"]), float(G["icept"])
x0, x1 = float(is_.min()), float(is_.max())
assert (f"{sl:.2f}", f"{ic:.2f}", f"{is_.mean():.2f}", f"{oos.mean():.2f}") == ("-0.86", "1.93", "1.31", "0.80")
write("lm34-degrade", {
    "type": "scatter", "equal": False, "height": 320,
    "alt": "In-sample against out-of-sample annualized Sharpe ratio of the in-sample best, every fifth of 12,870 "
           "splits: the OLS line falls with slope −0.86, and the means are 1.31 in sample and 0.80 out of sample",
    "x": {"label": "In-sample Sharpe ratio (annualized)", "fmt": "n2", "tfmt": "n1", "name": "in sample"},
    "y": {"label": "Out-of-sample Sharpe ratio", "fmt": "n2", "tfmt": "n1", "name": "out of sample"},
    "series": [{"name": "splits", "color": "1", "x": [rd(v, 4) for v in is_[sel]], "y": [rd(v, 4) for v in oos[sel]],
                "r": 1.6}],
    "curves": [{"x": [rd(x0, 4), rd(x1, 4)], "y": [rd(ic + sl * x0, 4), rd(ic + sl * x1, 4)], "dash": True,
                "label": "slope −0.86"}],
    "points": [{"at": [rd(is_.mean(), 4), rd(oos.mean(), 4)], "label": "means 1.31, 0.80", "r": 6, "color": "2"}],
})

# ---------------------------------------------------------------- widget: PBO simulator
NS = [2, 5, 10, 20, 60, 100]
SRS = [0.0, 0.5, 1.0, 1.5, 2.0]
wg = K["widget"]
means = {str(n): [rd(wg[(n, s)][0], 6) for s in SRS] for n in NS}
se_max = max(v[1] for v in wg.values())
assert f"{se_max:.3f}" == "0.051"
gt = np.random.default_rng([7, C.SEED])                 # experiment 7: the widget's test matrix, created once
test = gt.standard_normal((160, 5)) * 0.01
lg_test = C.cscv(test, 0.0)[0]
pbo_test = float((lg_test <= C.EPS).mean())
hist_test = [int(h) for h in np.histogram(np.clip(lg_test, -4.5 + 1e-9, 4.5 - 1e-9), bins=np.linspace(-4.5, 4.5,
                                                                                                    19))[0]]
wblock = {"n": NS, "sr": SRS, "means": means, "seMax": rd(se_max, 6), "days": int(G["Tg"]), "blocks": C.BLOCKS,
          "Aw": rd(aw, 8), "panels": C.N_STATE,
          "test": {"x": [[rd(v, 12) for v in row] for row in test], "pbo": rd(pbo_test, 10), "hist": hist_test}}
write("lm34-pboSim", {
    "type": "bar", "valueLabels": False, "height": 280,
    "alt": "Mean PBO of 40 simulated panels by the number of strategies: near one half when no strategy has skill, "
           "falling as strategy 1's true Sharpe ratio rises to 2",
    "categories": [str(n) for n in NS], "x": {"label": "Strategies n"},
    "y": {"fmt": "n2", "tfmt": "n1", "label": "Mean PBO", "min": 0, "max": 0.8, "ticks": [0, 0.2, 0.4, 0.6, 0.8]},
    "series": [{"name": f"true ratio {s:g}", "color": str(c), "values": [means[str(n)][SRS.index(s)] for n in NS],
                "fmt": "n2"} for c, s in zip((1, 2, 3), (0.0, 1.0, 2.0), strict=True)],
    "widget": wblock,
})

# ---------------------------------------------------------------- the widget's CSCV in Node against Python
DRIVER = r"""
const vm = require("vm"), fs = require("fs");
const ctx = { window: {}, document: { readyState: "loading", addEventListener() {} }, console, Float64Array, Math };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[1], "utf8"), ctx);
vm.runInContext(fs.readFileSync(process.argv[2], "utf8"), ctx);
const M = ctx.window.Book.widgets.pboSim.math, q = JSON.parse(fs.readFileSync(0, "utf8"));
const x = new Float64Array(q.x.length * q.x[0].length);
q.x.forEach((row, t) => row.forEach((v, k) => { x[t * row.length + k] = v; }));
const lg = M.cscv(x, q.x.length, q.x[0].length, 16);
const t0 = Date.now(), p = M.panel(60, 0, 1, q.days, q.Aw);
process.stdout.write(JSON.stringify({ logits: Array.from(lg), pbo: M.pbo(lg), panelPbo: p.pbo,
                                      panelMs: Date.now() - t0, splits: p.logits.length }));
"""
node_exe = shutil.which("node")
assert node_exe, "Node is needed to check the widget (it is needed to build the site too)"
out = subprocess.run([node_exe, "-e", DRIVER, str(ROOT / "src" / "assets" / "book.js"), str(ROOT / "src" / "lm34.js")],
                     input=json.dumps({"x": wblock["test"]["x"], "days": int(G["Tg"]), "Aw": aw}),
                     capture_output=True, text=True, encoding="utf-8", check=True)
got = json.loads(out.stdout)
lg_py = C.cscv(np.asarray(wblock["test"]["x"], dtype=float), 0.0)[0]
diff = float(np.abs(np.asarray(got["logits"]) - lg_py).max())
assert len(got["logits"]) == 12_870 and diff < 1e-12, diff
assert abs(got["pbo"] - pbo_test) < 1e-15 and got["splits"] == 12_870
print(f"widget CSCV against Python on the 160 x 5 test matrix: largest logit difference {diff:.1e}, PBO "
      f"{got['pbo']:.4f} both; one initial-state panel (n = 60, ratio 0, seed 1) took {got['panelMs']} ms in Node")
