"""Chart specs for LM35 (src/data/lm35-*.json), computed from E5, TR23 and the through case's books.

Run:  uv run python data/lm35_charts.py
      (after data/vol3_series.py, data/vol4_series.py, data/build_series.py, data/vol5_series.py and
      data/vol5_rules.py; data/lm35_numbers.py then checks the text and the widget block)

Inputs and conventions: data/lm35_common.py (the anchor script's computations; E5 through vol5_series, the books
through vol5_rules' files, TR23 through vol3_taiex.parquet). Writes
  lm35-windows   the five scenario windows on TR23: worst day, worst 5 and 20 sessions, peak to trough (bars);
  lm35-replay    R1's, R3's, R6's and R8's frozen losses in the 2020, 2024 and 2025 windows (bars);
  lm35-attrib    the parts f_i R_i of R1, R3, R6 and R8 on 7 April 2025 (stacked bars; 00635U in the muted colour);
  lm35-reverse   the reverse stress shocks of R1 and R8 (35.4), R2's with 0050's limit, and the worst day of each fund;
  lm35-ruin      1 + L R for R6's book in three replays and for 0050 to the open of 8 April 2025 (straight lines);
  lm35-builder   the widget's initial chart and its "widget" block (the eight current books, the presets, for each
                 window preset every rule's lowest unit-book value on the window's dates, the mean, covariance and
                 inverse covariance of the 2,362 joint dates, and their sorted distances, no dates).
No published file carries a daily series: every chart is per scenario, per fund or a straight line (plans/vol-5.md,
"Charts", X37); the widget's distances are sorted and carry no dates, and a window's lowest value is one number per
rule. The script then runs the widget's functions (src/lm35.js, Book.widgets.scenarioBuilder.math) in Node against
NumPy for every rule and preset at L = 0, 0.5, 1, 2.5 and 10 and at each rule's own total exposure, and on 200 custom
shocks drawn with np.random.default_rng([2, 20261011]) (experiment 2), and stops on a difference above 1e-12 (a
distance count must agree exactly). It prints no statistic of the draws.
"""
import json
import shutil
import subprocess
from typing import Any

import lm35_common as K
import numpy as np

ROOT = K.HERE.parent
OUT = ROOT / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)
FUNDS = K.FUNDS                                    # 0050, 00646, 00679B, 00635U, 00642U
COLOR = {"0050": "1", "00646": "2", "00679B": "3", "00635U": "var(--muted)", "00642U": "4"}   # Volume V's
SCEN = ["2008", "2015", "2020", "2024-08-05", "2025-04-07"]
SHORT = {"2008": "2008", "2015": "2015", "2020": "2020", "2024-08-05": "2024", "2025-04-07": "2025"}


def rd(x: float, n: int = 10) -> float:
    return round(float(x), n)


def write(name: str, spec: dict[str, Any]) -> None:
    assert isinstance(spec.get("alt"), str) and spec["alt"].strip()
    text = json.dumps(spec, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    assert len(text.encode("utf-8")) < 300_000, (name, len(text))
    (OUT / f"{name}.json").write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote src/data/{name}.json ({len(text.encode('utf-8')):,} bytes)")


# ---------------------------------------------------------------- X2: the five windows
LV, RT, TPOS = K.LV, K.RT, K.TPOS
cols: dict[str, list[float]] = {"Worst day": [], "Worst 5 sessions": [], "Worst 20 sessions": [], "Peak to trough": []}
for n in SCEN:
    p, t, nd = K.WIN[n]
    cols["Worst day"].append(rd(RT[TPOS[nd]]))
    cols["Worst 5 sessions"].append(rd(K.WORST[n][5][0]))
    cols["Worst 20 sessions"].append(rd(K.WORST[n][20][0]))
    cols["Peak to trough"].append(rd(LV[TPOS[t]] / LV[TPOS[p]] - 1))
assert f"{100 * cols['Peak to trough'][0]:.2f}" == "-56.02" and f"{100 * cols['Worst day'][4]:.2f}" == "-9.70"
write("lm35-windows", {
    "type": "bar", "valueLabels": False, "height": 300,
    "alt": "Losses of TR23, the TAIEX total-return index, in five scenario windows: worst day, worst 5 and 20 sessions "
           "and peak to trough, from 18.31% (2024) to 56.02% (2008) peak to trough",
    "categories": [SHORT[n] for n in SCEN], "x": {"label": ""},
    "y": {"fmt": "pct2", "tfmt": "pct0", "label": "TR23 return", "min": -0.6, "max": 0,
          "ticks": [-0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0]},
    "series": [{"name": k, "color": str(i + 1), "values": v, "fmt": "pct2"} for i, (k, v) in enumerate(cols.items())],
})

# ---------------------------------------------------------------- X3: frozen replays of four rules
REPLAY = ["2020", "2024-08-05", "2025-04-07"]
write("lm35-replay", {
    "type": "bar", "valueLabels": False, "height": 280,
    "alt": "Frozen replays of R1, R3, R6 and R8 over the 2020, 2024 and 2025 windows: R1 lost 19.84% in 2020, R3 gained "
           "0.11% in 2024, R8 lost 10.15% in 2025",
    "categories": [SHORT[n] for n in REPLAY], "x": {"label": ""},
    "y": {"fmt": "pct2", "tfmt": "pct0", "label": "Frozen book's return", "min": -0.2, "max": 0.02,
          "ticks": [-0.2, -0.15, -0.1, -0.05, 0]},
    "series": [{"name": k, "color": str(i + 1), "values": [rd(K.FROZEN[n][k]) for n in REPLAY], "fmt": "pct2"}
               for i, k in enumerate(("R1", "R3", "R6", "R8"))],
})

# ---------------------------------------------------------------- X4: attribution on 7 April 2025
i7 = K.i7
order = ["0050", "00646", "00679B", "00642U", "00635U"]          # colours 1-4, then the muted 00635U
parts = {k: K.expo(k, "2025-04-02") * K.fr.W[i7] for k in ("R1", "R3", "R6", "R8")}
write("lm35-attrib", {
    "type": "bar", "stack": True, "valueLabels": True, "height": 300,
    "alt": "Each fund's part of the loss of R1, R3, R6 and R8 on 7 April 2025, stacked: 00646 and 00642U supply the "
           "largest parts, 00679B the only gain; totals 7.70%, 5.40%, 5.96% and 7.94%",
    "categories": ["R1", "R3", "R6", "R8"], "x": {"label": ""},
    "y": {"fmt": "pct2", "tfmt": "pct0", "label": "Part of the day's return", "min": -0.1, "max": 0.02,
          "ticks": [-0.1, -0.08, -0.06, -0.04, -0.02, 0, 0.02]},
    "series": [{"name": s, "color": COLOR[s], "values": [rd(parts[k][FUNDS.index(s)]) for k in parts], "fmt": "pct2"}
               for s in order],
})

# ---------------------------------------------------------------- X6: reverse stress shocks
xb2, db2, _ = K.bounded(K.CUR["R2"])
rev = [("R1, (35.4)", K.XSTAR["R1"]), ("R8, (35.4)", K.XSTAR["R8"]), ("R2, 0050 ≥ −10%", xb2),
       ("Worst day of each fund", K.woe)]
write("lm35-reverse", {
    "type": "bar", "valueLabels": False, "height": 300,
    "alt": "Least unusual one-day shocks that cost R1, R8 and R2 (with 0050's limit) 10%, beside each fund's worst day: "
           "R1's shock puts 00642U at -23.00% and 0050 below its limit",
    "categories": FUNDS, "x": {"label": ""},
    "y": {"fmt": "pct2", "tfmt": "pct0", "label": "Shock", "min": -0.25, "max": 0, "ticks": [-0.25, -0.2, -0.15, -0.1,
                                                                                           -0.05, 0]},
    "series": [{"name": nm, "color": str(i + 1), "values": [rd(v) for v in x], "fmt": "pct2"}
               for i, (nm, x) in enumerate(rev)],
})

# ---------------------------------------------------------------- X7: the ruin lines (35.2)
eve = {n: K.WD[K.WIDX[K.WIN[n][2]] - 1] for n in REPLAY}
lines = [("R6, 2020 window", float(K.expo("R6", K.WIN["2020"][0]) @ K.growth(*K.WIN["2020"][:2]))),
         ("R6, 2025 window", float(K.expo("R6", K.WIN["2025-04-07"][0]) @ K.growth(*K.WIN["2025-04-07"][:2]))),
         ("R6, 7 April 2025", float(K.expo("R6", eve["2025-04-07"]) @ K.fr.W[K.WIDX["2025-04-07"]])),
         ("0050 to the open of 8 April", float(K.xo))]
LMAX = 20.0
series = []
pts = []
for i, (nm, r) in enumerate(lines):
    lr = -1 / r
    xs = [0.0, rd(lr), LMAX]
    series.append({"name": nm, "color": str(i + 1), "x": xs, "y": [1.0, 0.0, rd(1 + LMAX * r)]})
    pts.append({"type": "point", "x": rd(lr), "y": 0, "color": str(i + 1), "label": f"{lr:.2f}",
                **({"dy": 14} if i % 2 else {})})
umax = float(K.ratio.max())
write("lm35-ruin", {
    "height": 320,
    "alt": "Wealth after a scenario, 1 + L R, against total exposure L for R6's book in three replays and for 0050 to "
           "the next open of 8 April 2025: the lines cross zero, ruin, at 7.10, 7.67, 9.90 and 16.77, far right of R8's "
           "cap of 1.5 and its largest uncapped ratio, 2.14",
    "x": {"type": "num", "fmt": "n2", "tfmt": "n0", "label": "Total exposure L", "min": 0, "max": LMAX,
          "ticks": [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20]},
    "y": {"type": "lin", "fmt": "pct0", "label": "Wealth after the scenario", "min": -2, "max": 1,
          "ticks": [-2, -1.5, -1, -0.5, 0, 0.5, 1]},
    "series": series,
    "ann": [{"type": "hline", "y": 0, "label": "ruin"},
            {"type": "vline", "x": 1.5, "dash": True},
            {"type": "vline", "x": rd(umax), "dash": True, "label": f"R8: cap 1.5, ratio {umax:.2f}"}] + pts,
})

# ---------------------------------------------------------------- widget: the scenario builder
xr_mu = K.MU
presets: dict[str, dict[str, Any]] = {}
for key, (label, vec) in K.PRESETS.items():
    kind = "window" if key.startswith("win") else "day"
    presets[key] = {"label": label, "kind": kind, "x": [float(v) for v in vec]}
# (35.2) over a window applies on every date (Section 8): each rule's unit book, at its current exposures, gets its
# lowest value on the window's dates, which the widget's ruin readout uses
WIN_KEY = {"win2020": "2020", "win2024": "2024-08-05", "win2025": "2025-04-07"}
LOW: dict[str, dict[str, float]] = {}
for key, name in WIN_KEY.items():
    a, b, _ = K.WIN[name]
    path = np.cumprod(1 + K.fr.W[K.WIDX[a] + 1:K.WIDX[b] + 1], axis=0) - 1
    assert np.abs(path[-1] - np.array(presets[key]["x"])).max() < 1e-14, key
    LOW[key] = {k: float((path @ (K.CUR[k] / K.CUR[k].sum())).min()) for k in K.RULES}
    presets[key]["low"] = LOW[key]
assert f"{-1 / LOW['win2024']['R3']:.2f}" == "89.54" and f"{-1 / LOW['win2024']['R5']:.2f}" == "62.09"
presets["reverse"] = {"label": "Reverse stress, 10% loss", "kind": "reverse", "x": None}
presets["custom"] = {"label": "Custom (sliders)", "kind": "custom", "x": None}
order_p = ["day0407", "win2020", "win2024", "win2025", "factor", "break", "worst", "reverse", "custom"]
wblock = {
    "funds": FUNDS, "rules": list(K.RULES), "books": {k: [float(v) for v in K.CUR[k]] for k in K.RULES},
    "presets": presets, "order": order_p, "loss": K.LOSS,
    "mu": [float(v) for v in xr_mu], "S": [[float(v) for v in row] for row in K.S],
    "Si": [[float(v) for v in row] for row in K.SI], "dist": [round(float(v), 9) for v in np.sort(K.dt)],
    "init": {"rule": "R1", "preset": "day0407", "L": 1.0},
}
g0 = K.CUR["R1"] / K.CUR["R1"].sum()
p0 = g0 * K.w7
write("lm35-builder", {
    "type": "bar", "stack": True, "height": 260,
    "alt": "R1's book of 8 October 2026 under the returns of 7 April 2025 at total exposure 1: a loss of 7.78%, split "
           "by fund",
    "categories": ["R1 at L = 1.00"], "x": {"label": ""},
    "y": {"fmt": "pct2", "tfmt": "pct0", "label": "Part of the return"},
    "series": [{"name": s, "color": COLOR[s], "values": [rd(p0[j])], "fmt": "pct2"} for j, s in enumerate(FUNDS)],
    "widget": wblock,
})


# ---------------------------------------------------------------- the widget's arithmetic in Node against NumPy
def py_eval(rule: str, preset: str, L: float, custom: list[float]) -> dict[str, Any] | None:
    f = K.CUR[rule]
    u = f / f.sum()
    g = L * u
    p = presets[preset]
    if preset == "custom":
        x = np.array(custom)
    elif p["kind"] == "reverse":
        if not L > 0:
            return None
        Sg = K.S @ g
        x = K.MU - (K.LOSS + g @ K.MU) / float(g @ Sg) * Sg
    else:
        x = np.array(p["x"])
    ru = float(u @ x)
    win = preset != "custom" and p["kind"] == "window"
    low = LOW[preset][rule] if win else None
    worst = low if low is not None else ru
    d = None if win else K.maha(x)
    far = None if d is None else int((np.array(wblock["dist"]) > d + 1e-6).sum())
    return {"x": x.tolist(), "ret": L * ru, "wealth": 1 + L * ru, "low": low,
            "lowWealth": None if low is None else 1 + L * low, "ruin": -1 / worst if worst < 0 else None, "d": d,
            "farther": far}


DRIVER = r"""
const vm = require("vm"), fs = require("fs");
const ctx = { window: {}, document: { readyState: "loading", addEventListener() {} }, console };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[1], "utf8"), ctx);
vm.runInContext(fs.readFileSync(process.argv[2], "utf8"), ctx);
const M = ctx.window.Book.widgets.scenarioBuilder.math, q = JSON.parse(fs.readFileSync(0, "utf8"));
process.stdout.write(JSON.stringify(q.cases.map(([r, p, L, c]) => M.evaluate(q.W, r, p, L, c))));
"""
node_exe = shutil.which("node")
assert node_exe, "Node is needed to check the widget (it is needed to build the site too)"
rng = np.random.default_rng([2, 20261011])                 # experiment 2, created once
cases: list[tuple[str, str, float, list[float]]] = [("R1", "day0407", 1.0, [0.0] * 5)]
for rule in K.RULES:
    for preset in order_p:
        for L in (0.0, 0.5, 1.0, 2.5, 10.0):
            cases.append((rule, preset, L, [float(v) for v in rng.uniform(-0.5, 0.5, 5)] if preset == "custom"
                          else [0.0] * 5))
N_OWN = len(cases)
for rule in K.RULES:                                       # each rule's own book, L = 1'f (the widget's default)
    for preset in order_p:
        cases.append((rule, preset, float(K.CUR[rule].sum()), [0.0] * 5))
while len(cases) < 361 + 72 + 200:
    cases.append((str(rng.choice(K.RULES)), "custom", float(rng.uniform(0, 20)), [float(v) for v in
                                                                                  rng.uniform(-0.5, 0.5, 5)]))
run = subprocess.run([node_exe, "-e", DRIVER, str(ROOT / "src" / "assets" / "book.js"), str(ROOT / "src" / "lm35.js")],
                     input=json.dumps({"W": wblock, "cases": cases}), capture_output=True, text=True,
                     encoding="utf-8", check=True)
got = json.loads(run.stdout)
worst = 0.0
for (rule, preset, L, c), js in zip(cases, got, strict=True):
    py = py_eval(rule, preset, L, c)
    if py is None or js is None:
        assert py is None and js is None, (rule, preset, L)
        continue
    worst = max(worst, float(np.abs(np.array(js["x"]) - np.array(py["x"])).max()), abs(js["ret"] - py["ret"]),
                abs(js["wealth"] - py["wealth"]))
    assert (js["low"] is None) == (py["low"] is None), (rule, preset, L)
    if py["low"] is not None:
        worst = max(worst, abs(js["low"] - py["low"]), abs(js["lowWealth"] - py["lowWealth"]))
    assert (js["ruin"] is None) == (py["ruin"] is None), (rule, preset, L)
    if py["ruin"] is not None:
        worst = max(worst, abs(js["ruin"] - py["ruin"]) / py["ruin"])
    assert (js["d"] is None) == (py["d"] is None) and js["farther"] == py["farther"], (rule, preset, L)
    if py["d"] is not None:
        worst = max(worst, abs(js["d"] - py["d"]))
first = got[0]
assert f"{-100 * first['ret']:.2f}" == "7.78" and f"{first['ruin']:.2f}" == "12.85" and f"{first['d']:.2f}" == "12.94"
assert first["farther"] == 2
own = {(r, p): js for (r, p, L, _), js in zip(cases[N_OWN:N_OWN + 72], got[N_OWN:N_OWN + 72], strict=True)}
assert f"{own[('R8', 'reverse')]['d']:.2f}" == "12.27", "R8's own book reproduces the reverse stress test's d*"
assert f"{own[('R1', 'reverse')]['d']:.2f}" == "13.52"
assert f"{own[('R3', 'win2024')]['ruin']:.2f}" == "89.54" and own[("R3", "win2024")]["ret"] > 0, "lowest value, not end"
worst = max(worst, abs(own[("R8", "reverse")]["ret"] + K.LOSS))
assert worst < 1e-12, worst
print(f"widget arithmetic against NumPy: largest difference {worst:.1e} over {len(cases)} cases (every rule and preset "
      f"at five L and at the rule's own L, and custom shocks of experiment 2); R8's own book under the reverse preset: "
      f"d {own[('R8', 'reverse')]['d']:.2f}; R3's 2024 window: ruin leverage {own[('R3', 'win2024')]['ruin']:.2f} at its "
      f"lowest value; initial state R1, 7 April 2025, L = 1: loss "
      f"{-100 * first['ret']:.2f}%, ruin leverage {first['ruin']:.2f}, d {first['d']:.2f}, {first['farther']} days "
      "farther")
