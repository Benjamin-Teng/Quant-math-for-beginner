"""Chart specs for LM32 (src/data/lm32-*.json), computed from TR23, LM26's forecasts and the through case.

Run:  uv run python data/lm32_charts.py
      (after data/vol3_series.py, data/vol5_series.py and data/vol5_rules.py; data/lm32_numbers.py then checks the
      text and the widget block)

Inputs and conventions: data/lm32_common.py (the anchor script's computations: TR23 and LM26's forecasts through
data/lm26_common.py, the through case through vol5_rules). Writes
  lm32-tail       the 293 worst of TR23's 5,849 returns as a histogram of losses (bins of 0.25 points, a post-step
                  line), with the historical and normal 99% VaR and ES as vertical lines;
  lm32-rollvar    minus the 99% VaR forecasts of HS, GARCH-t and the normal model, 2 January 2008 to 8 October 2026,
                  at each ISO week's last forecast day plus 7 April 2025; the returns of HS's and GARCH-t's
                  exceedance days only, as points (133 dated values);
  lm32-zones      the six models' exceedance counts (bars), with the expected count and the zone thresholds;
  lm32-underwater minus the drawdown of R1, R3, R6 and R8 at each ISO week's last session plus every cited peak,
                  trough and recovery, from 4 March 2019 to 8 October 2026;
  lm32-mddboot    a forest plot of the eight rules' realized MDD against the permutation and the stationary bootstrap
                  (5-95% ranges and medians);
  lm32-varlevel   the widget's initial chart and its "widget" block: each rule's 186 worst returns sorted, without
                  dates; its mean and s (divisor T); its maximum-likelihood t fit; its grid of t quantiles.
No published file carries a daily series in date order at full resolution (plans/vol-5.md, "Charts", X37): every dated
series is thinned to weekly points plus cited days, and no file has more than 1,172 dated points of a series. The
script then runs the widget's functions (src/lm32.js, Book.widgets.varLevel.math) in Node against the Python
estimators on every rule and every tail probability of the slider, and stops on a difference above 1e-9.
"""
import json
import shutil
import subprocess
from typing import Any

import lm32_common as K
import numpy as np

ROOT = K.HERE.parent
OUT = ROOT / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)
MAXPTS = 1172


def rd(x: float, n: int = 6) -> float:
    return round(float(x), n)


def write(name: str, spec: dict[str, Any]) -> None:
    assert isinstance(spec.get("alt"), str) and spec["alt"].strip()
    text = json.dumps(spec, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    assert len(text.encode("utf-8")) < 300_000, (name, len(text))
    (OUT / f"{name}.json").write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote src/data/{name}.json ({len(text.encode('utf-8')):,} bytes)")


# ---------------------------------------------------------------- X2: the tail of TR23 as a histogram of losses
v1, e1 = 100 * K.var_h(K.R, K.U), 100 * K.es_h(K.R, K.U)
vn, en = 100 * K.var_n(K.mu, K.s, K.U), 100 * K.es_n(K.mu, K.s, K.U)
assert (f"{v1:.2f}", f"{e1:.2f}", f"{vn:.2f}", f"{en:.2f}") == ("3.57", "4.69", "2.75", "3.16")
write("lm32-tail", {
    "alt": "Histogram of the 293 worst daily losses of the TAIEX total-return index, 2003 to 2026, in bins of 0.25 "
           "points: most lie between 1.86% and 3%, a few reach beyond 6%, the worst 9.70%; the historical 99% VaR "
           "3.57% and ES 4.69% lie right of the normal model's 2.75% and 3.16%",
    "height": 300,
    "x": {"type": "num", "fmt": "n2", "tfmt": "n0", "label": "Loss (%)", "tipLabel": "loss from (%)", "min": 1.75,
          "max": 10, "ticks": [2, 3, 4, 5, 6, 7, 8, 9, 10]},
    "y": {"type": "lin", "fmt": "n0", "tfmt": "n0", "label": "Days", "min": 0},
    "series": [{"name": "days in the bin", "color": "1", "step": True, "area": True,
                "x": [float(x) for x in K.EDGES], "y": [int(c) for c in K.HIST]}],
    "ann": [{"type": "vline", "x": rd(vn, 4), "dash": True, "label": "normal VaR 2.75"},
            {"type": "vline", "x": rd(en, 4), "dash": True, "label": "normal ES 3.16", "dy": 15},
            {"type": "vline", "x": rd(v1, 4), "label": "historical VaR 3.57", "dy": 30},
            {"type": "vline", "x": rd(e1, 4), "label": "historical ES 4.69", "dy": 45}],
})

# ---------------------------------------------------------------- X4: rolling 99% VaR and the exceedances
oos = [int(i) for i in K.oos]
fdates = [K.dates[i] for i in oos]
keep = sorted(set(K.weekly_last(fdates)) | {K.k7})
assert len(keep) <= MAXPTS
series = []
for m, col, nm in (("HS", "1", "historical"), ("GARCH-t", "2", "GARCH-t"), ("N", "3", "normal")):
    series.append({"name": f"minus VaR, {nm}", "color": col, "y": [rd(-K.VAR[m][j], 6) for j in keep]})
pts: list[dict[str, Any]] = []
n_pts = 0
for m, col in (("HS", "1"), ("GARCH-t", "2")):
    for j in np.flatnonzero(K.HIT[m]):
        pts.append({"type": "point", "x": fdates[int(j)], "y": rd(K.Ro[int(j)], 6), "color": col})
        n_pts += 1
assert n_pts == 56 + 77 <= MAXPTS
pts.append({"type": "point", "x": "2025-04-07", "y": rd(K.R[K.i7], 6), "label": "7 Apr 2025 −9.70%", "anchor": "end",
            "dx": -8})
write("lm32-rollvar", {
    "alt": "Minus the one-day 99% value at risk of the TAIEX total-return index forecast by historical simulation, "
           "GARCH with t innovations and the normal model, January 2008 to October 2026, with the returns of the "
           "exceedance days of the first two as points: the forecasts widen after each crash, and on 7 April 2025 "
           "the index fell 9.70% against forecasts of 3.53%, 4.14% and 2.66%",
    "height": 320,
    "x": {"type": "date", "values": [fdates[j] for j in keep]},
    "y": {"type": "lin", "fmt": "pct2", "tfmt": "pct0", "label": "Return; minus VaR", "min": -0.1, "max": 0,
          "ticks": [-0.1, -0.08, -0.06, -0.04, -0.02, 0]},
    "series": series,
    "ann": pts,
})

# ---------------------------------------------------------------- X5: exceedance counts against Basel's zones
cnt = [int(K.BT[m]["x"]) for m in K.MODELS]
assert cnt == [56, 110, 69, 103, 102, 77]
write("lm32-zones", {
    "type": "bar", "height": 280, "valueLabels": True,
    "alt": "Exceedances of the six models' 99% VaR forecasts over 4,609 days: historical simulation 56, normal 110, "
           "Student t 69, EWMA 103, GARCH-n 102, GARCH-t 77, against 46.09 expected; Basel's 1996 probabilities "
           "applied to 4,609 days put yellow from 57 and red from 73",
    "categories": ["HS", "N", "t", "EWMA", "GARCH-n", "GARCH-t"], "x": {"label": ""},
    "y": {"fmt": "n0", "tfmt": "n0", "label": "Exceedances", "min": 0, "max": 120, "ticks": [0, 20, 40, 60, 80, 100, 120]},
    "series": [{"name": "exceedances", "color": "1", "values": cnt, "fmt": "n0"}],
    "ann": [{"type": "hline", "y": 46.09, "label": "expected 46.09", "dash": True},
            {"type": "hline", "y": int(K.yN), "label": "yellow from 57"},
            {"type": "hline", "y": int(K.rN), "label": "red from 73"}],
})

# ---------------------------------------------------------------- X7: underwater chart of R1, R3, R6 and R8
p1 = K.paths["R1"]
wd = list(p1.dates)
cited: set[str] = set()
for k in ("R1", "R3", "R6", "R8"):
    sp = K.SP[k]
    cited |= {sp.peak, sp.trough, sp.long_peak, sp.long_end, sp.dd0_date, *( [sp.rec] if sp.rec else [])}
cited -= {"start", "open"}
assert all(k_ in wd for k_ in cited)
keepw = sorted(set(K.weekly_last(wd)) | {wd.index(d) for d in cited} | {0})
assert len(keepw) <= MAXPTS
uw_series = []
for k, col in (("R1", "1"), ("R3", "2"), ("R6", "3"), ("R8", "4")):
    assert K.paths[k].dates == wd
    uw_series.append({"name": k, "color": col, "y": [rd(-K.DDP[k][j], 6) for j in keepw]})
troughs = []
for k, col in (("R1", "1"), ("R3", "2"), ("R6", "3"), ("R8", "4")):
    sp = K.SP[k]
    place = {"R3": {"anchor": "end", "dx": -8, "dy": 16}, "R6": {"anchor": "end", "dx": -8}}.get(k, {})
    troughs.append({"type": "point", "x": sp.trough, "y": rd(-sp.mdd, 6), "color": col,
                    "label": f"{k} −{100 * sp.mdd:.2f}%", **place})
write("lm32-underwater", {
    "alt": "Underwater chart, minus the drawdown from the running peak, of R1, R3, R6 and R8 from March 2019 to "
           "October 2026: R1 falls 23.19% into 19 March 2020; R3, R6 and R8 fall 19.11%, 18.90% and 18.42% into 21 "
           "October 2022; only R1 crosses the hypothetical 20% limit among the four",
    "height": 320,
    "x": {"type": "date", "values": [wd[j] for j in keepw]},
    "y": {"type": "lin", "fmt": "pct2", "tfmt": "pct0", "label": "Minus drawdown", "min": -0.25, "max": 0,
          "ticks": [-0.25, -0.2, -0.15, -0.1, -0.05, 0]},
    "series": uw_series,
    "ann": [{"type": "hline", "y": -0.2, "dash": True, "label": "hypothetical 20% limit"}] + troughs,
})

# ---------------------------------------------------------------- X9: realized MDD against two resampling schemes
def q(v: np.ndarray, u: float) -> float:
    return float(np.quantile(v, u, method="inverted_cdf"))


ys = {k: 8 - i for i, k in enumerate(K.RULES)}        # R1 at the top
lines = []
real_x, perm_x, boot_x, yy = [], [], [], []
for k in K.RULES:
    y0 = ys[k]
    mp, mb = K.MP[k], K.MB[k]
    lines.append({"from": [rd(100 * q(mp, 0.05), 3), y0 + 0.15], "to": [rd(100 * q(mp, 0.95), 3), y0 + 0.15],
                  "color": "var(--muted)", "width": 1.5})
    lines.append({"from": [rd(100 * q(mb, 0.05), 3), y0 - 0.15], "to": [rd(100 * q(mb, 0.95), 3), y0 - 0.15],
                  "color": "var(--muted)", "width": 5})
    real_x.append(rd(100 * K.SP[k].mdd, 3))
    perm_x.append(rd(100 * q(mp, 0.5), 3))
    boot_x.append(rd(100 * q(mb, 0.5), 3))
    yy.append(y0)
assert f"{perm_x[0]:.1f}" == "17.2" and f"{boot_x[0]:.1f}" == "20.7" and f"{real_x[0]:.2f}" == "23.19"
write("lm32-mddboot", {
    "type": "scatter", "equal": False, "height": 360, "legend": True,
    "alt": "Forest plot of the eight rules' maximum drawdowns: for each rule the realized MDD, the median and 5-95% "
           "range of 10,000 permutations of its returns (thin) and of 10,000 stationary-bootstrap resamples (thick); "
           "every realized MDD lies inside both ranges, R1's 23.19% against medians of 17.2% and 20.7%",
    "x": {"label": "Maximum drawdown (%)", "fmt": "n1", "tfmt": "n0", "min": 8, "max": 40,
          "ticks": [10, 15, 20, 25, 30, 35, 40], "name": "MDD (%)"},
    "y": {"label": "", "fmt": "n0", "min": 0.4, "max": 8.6, "ticks": list(range(1, 9)),
          "tickLabels": [f"R{9 - t}" for t in range(1, 9)], "name": "rule"},
    "series": [{"name": "realized MDD", "color": "1", "x": real_x, "y": yy, "r": 4},
               {"name": "permutation median", "color": "2", "x": perm_x, "y": [y + 0.15 for y in yy], "r": 3},
               {"name": "bootstrap median", "color": "3", "x": boot_x, "y": [y - 0.15 for y in yy], "r": 3}],
    "lines": lines,
})

# ---------------------------------------------------------------- widget: VaR and ES of a rule at any level
nR = K.nR
wblock = {"T": nR, "rules": list(K.RULES), "kmax": len(K.ugrid),
          "worst": {k: [round(float(x), 10) for x in K.WORST[k]] for k in K.RULES},
          "mean": {k: K.NMOM[k][0] for k in K.RULES}, "s": {k: K.NMOM[k][1] for k in K.RULES},
          "t": {k: list(K.TFIT[k]) for k in K.RULES},
          "q": {k: [round(float(x), 12) for x in K.QGRID[k]] for k in K.RULES}}
assert all(len(wblock["worst"][k]) == 186 for k in K.RULES) and K.ntail == 186
w1 = K.WORST["R1"]
assert np.array_equal(np.array(wblock["worst"]["R1"]), np.round(w1, 10))
m1, s1 = K.NMOM["R1"]
nu1, lo1, sc1 = K.TFIT["R1"]
init = [100 * K.var_h(K.ret["R1"], K.U), 100 * K.var_n(m1, s1, K.U), K.var_t(nu1, lo1, sc1, K.U)]
init_es = [100 * K.es_h(K.ret["R1"], K.U), 100 * K.es_n(m1, s1, K.U), K.es_t(nu1, lo1, sc1, K.U)]
assert [f"{x:.2f}" for x in init + init_es] == ["2.10", "1.80", "2.05", "3.38", "2.08", "3.07"]
write("lm32-varlevel", {
    "type": "bar", "height": 260, "valueLabels": True,
    "alt": "R1's one-day 99% VaR and ES by historical simulation (2.10% and 3.38%), the normal model (1.80% and 2.08%) "
           "and the Student t (2.05% and 3.07%), from its 1,851 out-of-sample net returns",
    "categories": ["historical", "normal", "Student t"], "x": {"label": ""},
    "y": {"fmt": "pct2", "tfmt": "pct1", "label": "Loss", "min": 0},
    "series": [{"name": "VaR", "color": "1", "values": [rd(x / 100, 8) for x in init], "fmt": "pct2"},
               {"name": "ES", "color": "2", "values": [rd(x / 100, 8) for x in init_es], "fmt": "pct2"}],
    "widget": wblock,
})

# ---------------------------------------------------------------- the widget's arithmetic in Node against Python
DRIVER = r"""
const vm = require("vm"), fs = require("fs");
const ctx = { window: {}, document: { readyState: "loading", addEventListener() {} }, console };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[1], "utf8"), ctx);
vm.runInContext(fs.readFileSync(process.argv[2], "utf8"), ctx);
const M = ctx.window.Book.widgets.varLevel.math;
const W = JSON.parse(fs.readFileSync(process.argv[3], "utf8")).widget, out = {};
W.rules.forEach(function (r) {
  out[r] = [];
  for (let k = 1; k <= W.kmax; k++) out[r].push(M.measures(W, r, k));
});
process.stdout.write(JSON.stringify(out));
"""
node_exe = shutil.which("node")
assert node_exe, "Node is needed to check the widget (it is needed to build the site too)"
res = subprocess.run([node_exe, "-e", DRIVER, str(ROOT / "src" / "assets" / "book.js"), str(ROOT / "src" / "lm32.js"),
                      str(OUT / "lm32-varlevel.json")], capture_output=True, text=True, encoding="utf-8", check=True)
got = json.loads(res.stdout)
worst_d = 0.0
for k in K.RULES:
    x = K.ret[k]
    mk, sk = K.NMOM[k]
    nuk, lok, sck = K.TFIT[k]
    for i, u in enumerate(K.ugrid):
        u = float(u)
        g = got[k][i]
        assert g["j"] == K.jrank(u, nR), (k, u, g["j"])
        py = [K.var_h(x, u), K.es_h(x, u), K.var_n(mk, sk, u), K.es_n(mk, sk, u), K.var_t(nuk, lok, sck, u) / 100,
              K.es_t(nuk, lok, sck, u) / 100]
        js = [g["hv"], g["he"], g["nv"], g["ne"], g["tv"], g["te"]]
        worst_d = max(worst_d, max(abs(a - b) for a, b in zip(py, js, strict=True)))
assert worst_d < 1e-9, worst_d
print(f"widget arithmetic against Python: largest difference {worst_d:.1e} over 8 rules x {len(K.ugrid)} tail "
      f"probabilities (historical, normal and t VaR and ES)")
