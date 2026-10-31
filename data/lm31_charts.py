"""Chart specs for LM31 (src/data/lm31-*.json), computed from E5's first window and through case and from U28.

Run:  uv run python data/lm31_charts.py
      (after data/vol5_series.py, data/vol5_rules.py and data/vol2_series.py; data/lm31_numbers.py then checks the text
      and the widget block)

Inputs and conventions: data/lm31_common.py (the anchor script's computations; E5 through vol5_series, the through
case through vol5_rules, U28 through lm10_series). Writes
  lm31-shares     weights and ex-ante risk shares RC_i / sigma_p of R1, inverse volatility, R6 and R7 on the first
                  window (stacked bars; five funds, 00635U in the muted colour);
  lm31-u28corr    U28's full-sample correlation matrix in HRP's order (heatmap);
  lm31-u28tree    U28's single-linkage tree on the column distance (scatter lines, three per merge), leaves in HRP's
                  order from the top;
  lm31-exposure   R8's exposure L_t at its 92 trades (a post-step line to the last date, 92 values; no daily series);
  lm31-target     realized RMS over sigma_bar for R6 and R8 at the starts of the 91 complete holding months (log y);
  lm31-ercthree   the widget's initial chart and its "widget" block (three volatilities and three correlations of
                  the first window, unrounded, and b1 = 1/3).
No published file carries a daily series (plans/vol-5.md, "Charts", X37). The script then runs the widget's functions
(src/lm31.js, Book.widgets.ercThree.math) in Node against Python's CCD and vol5_rules.erc on the initial state and on
500 random positive definite 3 x 3 matrices drawn with np.random.default_rng([1, 20261011]) (experiment 1), and stops
on a weight difference above 1e-9. It prints no statistic of the draws.
"""
import json
import shutil
import subprocess
from typing import Any

import lm31_common as K
import numpy as np

ROOT = K.HERE.parent
OUT = ROOT / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)
FUNDS = K.funds                                  # 0050, 00646, 00679B, 00635U, 00642U
COLOR = {"0050": "1", "00646": "2", "00679B": "3", "00635U": "var(--muted)", "00642U": "4"}


def rd(x: float, n: int = 6) -> float:
    return round(float(x), n)


def write(name: str, spec: dict[str, Any]) -> None:
    assert isinstance(spec.get("alt"), str) and spec["alt"].strip()
    text = json.dumps(spec, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    assert len(text.encode("utf-8")) < 300_000, (name, len(text))
    (OUT / f"{name}.json").write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote src/data/{name}.json ({len(text.encode('utf-8')):,} bytes)")


# ---------------------------------------------------------------- X2: weights and risk shares on the first window
books = [("R1", K.w1), ("IV", K.iv0), ("R6", K.w6), ("R7", K.w7)]
cats: list[str] = []
vals: dict[str, list[float]] = {f: [] for f in FUNDS}
for nm, w in books:
    sh = K.shares(w, K.S0)
    cats += [f"{nm} weights", f"{nm} risk"]
    for i, f in enumerate(FUNDS):
        vals[f] += [rd(w[i]), rd(sh[i])]
assert f"{100 * vals['00642U'][1]:.1f}" == "50.2"
write("lm31-shares", {
    "type": "bar", "stack": True, "valueLabels": False, "height": 300,
    "alt": "Weights and ex-ante risk shares on the first window for equal weights, inverse volatility, R6 and R7, "
           "stacked to 100% in each bar: R1's 20% in the oil-futures fund carries 50.2% of its risk, R6's shares are "
           "20% each",
    "categories": cats, "x": {"label": ""},
    "y": {"fmt": "pct1", "tfmt": "pct0", "label": "Share", "min": 0, "max": 1, "ticks": [0, 0.25, 0.5, 0.75, 1]},
    "series": [{"name": f, "color": COLOR[f], "values": vals[f], "fmt": "pct1"} for f in FUNDS],
})

# ---------------------------------------------------------------- X3: U28's correlations in HRP's order
ou = [int(i) for i in K.ou]
names = [K.nm[i] for i in ou]
Cu = K.Cu
write("lm31-u28corr", {
    "type": "heatmap",
    "alt": "Correlations of U28's 28 sector price indices, rows and columns in HRP's order: all positive, from 0.217 "
           "to 0.755, with the electronics sectors in one block near the middle",
    "labels": names, "matrix": [[rd(Cu[i, j], 3) for j in ou] for i in ou],
    "fmt": "n2", "min": 0, "max": 1, "valueName": "correlation",
})

# ---------------------------------------------------------------- X4: U28's tree (three lines per merge)
Zu = K.Zu
X0 = 0.45
pos = {leaf: 28 - p for p, leaf in enumerate(ou)}          # the first leaf of the order at the top
node: dict[int, tuple[float, float]] = {leaf: (X0, float(pos[leaf])) for leaf in range(28)}
lines: list[dict[str, Any]] = []
mx: list[float] = []
my: list[float] = []
for k in range(len(Zu)):
    a, b, h = int(Zu[k, 0]), int(Zu[k, 1]), float(Zu[k, 2])
    (xa, ya), (xb, yb) = node[a], node[b]
    lines += [{"from": [rd(xa), ya], "to": [rd(h), ya]}, {"from": [rd(xb), yb], "to": [rd(h), yb]},
              {"from": [rd(h), ya], "to": [rd(h), yb]}]
    node[28 + k] = (h, (ya + yb) / 2)
    mx.append(rd(h))
    my.append((ya + yb) / 2)
assert f"{Zu[0, 2]:.4f}" == "0.5012" and f"{Zu[-1, 2]:.4f}" == "0.7426"
write("lm31-u28tree", {
    "type": "scatter", "equal": False, "height": 440,
    "alt": "Single-linkage tree of U28's 28 sector indices on the column distance, sectors in HRP's order from the "
           "top: the first merge, ComputerPeripheralEquipment with ElectronicPartsComponents, at 0.5012 and the root "
           "at 0.7426",
    "x": {"label": "Column distance at the merge", "fmt": "n4", "tfmt": "n2", "min": X0, "max": 0.76,
          "ticks": [0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75], "name": "distance"},
    "y": {"label": "", "fmt": "n0", "min": 0.5, "max": 28.5, "ticks": list(range(1, 29)),
          "tickLabels": [names[28 - t] for t in range(1, 29)], "name": "position"},
    "series": [{"name": "Merge", "color": "1", "x": mx, "y": my, "r": 2.5}],
    "lines": [{**ln, "width": 1.4} for ln in lines],
    "points": [{"at": [mx[0], my[0]], "label": "first merge 0.5012", "dx": 6},
               {"at": [mx[-1], my[-1]], "label": "root 0.7426", "dx": -6, "anchor": "end"}],
})

# ---------------------------------------------------------------- X7: R8's exposure at its 92 trades
Lp = [rd(x) for x in K.L]
trade_dates = list(K.trades)
assert len(Lp) == 92 and len(trade_dates) == 92
mark = {"2019-03-04": "0.85", "2020-04-01": "0.295 (lowest)", "2025-04-01": "1.33"}
write("lm31-exposure", {
    "alt": "R8's exposure at its 92 monthly trades from March 2019 to October 2026, a step line between 0.295 (1 "
           "April 2020) and the cap of 1.5, which it reached at 14 trades; 1.33 on 1 April 2025",
    "height": 300,
    "x": {"type": "date"},
    "y": {"type": "lin", "fmt": "n3", "tfmt": "n1", "label": "Exposure L_t", "min": 0, "max": 1.7,
          "ticks": [0, 0.5, 1, 1.5]},
    "series": [{"name": "R8's exposure", "color": "1", "step": True, "x": trade_dates + [K.p8.dates[-1]],
                "y": Lp}],
    "ann": [{"type": "hline", "y": 1, "dash": True}, {"type": "hline", "y": 1.5, "dash": True, "label": "cap 1.5"}]
           + [{"type": "point", "x": d, "y": Lp[trade_dates.index(d)], "label": lab,
               **({"anchor": "end", "dx": -8} if d == "2025-04-01" else {})} for d, lab in mark.items()],
})

# ---------------------------------------------------------------- X8: realized over target, 91 holding months
starts = [K.p8.dates[K.idx[m] + 1] for m in range(len(K.idx) - 1)]
r6, r8 = (list(map(rd, K.ratio[k])) for k in ("R6", "R8"))
assert len(starts) == 91 and starts[0] == "2019-03-05"
i20, i25 = starts.index("2020-03-03"), starts.index("2025-04-02")
assert (f"{r6[i20]:.2f}", f"{r8[i20]:.2f}", f"{r6[i25]:.2f}", f"{r8[i25]:.2f}") == ("5.60", "4.90", "4.25", "5.78")
write("lm31-target", {
    "alt": "Realized over target volatility for R6 and R8 in the 91 holding months from March 2019, on a log scale: "
           "medians 0.83 and 0.98, the largest 5.60 for R6 from 3 March 2020 and 5.78 for R8 from 2 April 2025",
    "height": 300,
    "x": {"type": "date", "values": starts},
    "y": {"type": "log", "fmt": "n2", "tfmt": "n1", "label": "Realized ÷ target (log scale)", "min": 0.3, "max": 8},
    "series": [{"name": "R6", "color": "1", "y": r6}, {"name": "R8", "color": "2", "y": r8}],
    "ann": [{"type": "hline", "y": 1, "dash": True},
            {"type": "point", "x": "2020-03-03", "y": r6[i20], "color": "1", "label": "R6 5.60, R8 4.90"},
            {"type": "point", "x": "2025-04-02", "y": r8[i25], "color": "2", "label": "R6 4.25, R8 5.78",
             "anchor": "end", "dx": -8}],
})

# ---------------------------------------------------------------- widget: ERC for three funds
Sw, vw, Cw = K.Sw, K.vw, K.Cw
vols0 = [float(x) for x in vw]
corr0 = [float(Cw[0, 1]), float(Cw[0, 2]), float(Cw[1, 2])]
wblock = {"vols": vols0, "corr": corr0, "b1": 1 / 3}
b3 = np.array([1 / 3, 1 / 3, 1 / 3])
erc3, _ = K.ccd(Sw, b3)
init = [("1/N", b3), ("IV", K.ivw), ("Budget", erc3)]
wc: list[str] = []
wv: list[list[float]] = [[], [], []]
for nm, w in init:
    sh = K.shares(w, Sw)
    wc += [f"{nm} weights", f"{nm} risk"]
    for i in range(3):
        wv[i] += [rd(w[i]), rd(sh[i])]
write("lm31-ercthree", {
    "type": "bar", "stack": True, "valueLabels": False, "height": 280,
    "alt": "Weights and risk shares of 1/N, inverse volatility and ERC for 0050, 00679B and 00642U on the first "
           "window: ERC holds 0.3061, 0.5400 and 0.1539",
    "categories": wc, "x": {"label": ""},
    "y": {"fmt": "pct1", "tfmt": "pct0", "label": "Share", "min": 0, "max": 1, "ticks": [0, 0.25, 0.5, 0.75, 1]},
    "series": [{"name": f, "color": c, "values": wv[i], "fmt": "pct1"}
               for i, (f, c) in enumerate(zip(("0050", "00679B", "00642U"), ("1", "3", "4"), strict=True))],
    "widget": wblock,
})

# ---------------------------------------------------------------- the widget's arithmetic in Node against Python
DRIVER = r"""
const vm = require("vm"), fs = require("fs");
const ctx = { window: {}, document: { readyState: "loading", addEventListener() {} }, console };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[1], "utf8"), ctx);
vm.runInContext(fs.readFileSync(process.argv[2], "utf8"), ctx);
const M = ctx.window.Book.widgets.ercThree.math, q = JSON.parse(fs.readFileSync(0, "utf8"));
process.stdout.write(JSON.stringify(q.map(([v, r, b1]) => {
  const S = M.cov(v, r), b = [b1, (1 - b1) / 2, (1 - b1) / 2];
  if (!M.pd(S)) return null;
  const s = M.ccd(S, b), iv = M.inverseVol(S);
  return s ? { w: s.w, sweeps: s.sweeps, sh: M.shares(S, s.w), iv: iv, ivsh: M.shares(S, iv) } : null;
})));
"""
node_exe = shutil.which("node")
assert node_exe, "Node is needed to check the widget (it is needed to build the site too)"
rng = np.random.default_rng([1, 20261011])                # experiment 1, created once
cases: list[tuple[list[float], list[float], float]] = [(vols0, corr0, 1 / 3)]
while len(cases) < 501:
    v = rng.uniform(0.02, 0.40, 3)
    g = rng.normal(size=(3, 5))
    m = g @ g.T
    c = m / np.sqrt(np.outer(np.diag(m), np.diag(m)))
    cases.append(([float(x) for x in v], [float(c[0, 1]), float(c[0, 2]), float(c[1, 2])],
                  float(rng.uniform(0.1, 0.8))))
out = subprocess.run([node_exe, "-e", DRIVER, str(ROOT / "src" / "assets" / "book.js"), str(ROOT / "src" / "lm31.js")],
                     input=json.dumps(cases), capture_output=True, text=True, encoding="utf-8", check=True)
got = json.loads(out.stdout)
worst = 0.0
for (v, r, b1), g_ in zip(cases, got, strict=True):
    assert g_ is not None, (v, r, b1)
    vv = np.array(v)
    cc = np.array([[1, r[0], r[1]], [r[0], 1, r[2]], [r[1], r[2], 1]])
    S = cc * np.outer(vv, vv)
    b = np.array([b1, (1 - b1) / 2, (1 - b1) / 2])
    w_py, _ = K.ccd(S, b)
    worst = max(worst, float(np.abs(np.array(g_["w"]) - w_py).max()),
                float(np.abs(np.array(g_["sh"]) - K.shares(w_py, S)).max()))
    iv = (1 / vv) / float((1 / vv).sum())
    worst = max(worst, float(np.abs(np.array(g_["iv"]) - iv).max()))
first = got[0]
assert float(np.abs(np.array(first["w"]) - K.erc(Sw)).max()) < 1e-9 and first["sweeps"] == K.itw
assert worst < 1e-9, worst
print(f"widget arithmetic against Python: largest difference {worst:.1e} over {len(cases)} cases (the initial state "
      f"and 500 random positive definite matrices, experiment 1); initial state {first['sweeps']} sweeps, equal to "
      f"vol5_rules.erc to 1e-9")
