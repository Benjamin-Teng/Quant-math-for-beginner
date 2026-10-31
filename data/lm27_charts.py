"""Chart specs for LM27 (src/data/lm27-*.json), computed from E5 and the through case's R1 and R2.

Run:  uv run python data/lm27_charts.py
      (after data/vol5_series.py, data/vol5_rules.py, data/vol2_series.py and data/vol3_series.py; data/lm27_numbers.py
      then checks the text against these files)

Inputs and conventions: data/lm27_common.py. Writes
  lm27-drift      weights of a book bought at 1/N at the close of 2019-03-04 and held to 2026-10-08 (wealth frame),
                  thinned to the last session of each ISO week, the purchase date and every fund's lowest and highest
                  weight (402 dated points: buy-and-hold weights rebuild price ratios, so no daily series is published,
                  plans/vol-5.md, "Charts");
  lm27-freq       correlations of the five pairs at daily, weekly and monthly frequency (estimation frame);
  lm27-shares     money and risk shares of R1 and R2 at the full-sample covariance, stacked;
  lm27-windows    R1's risk shares in the 92 trailing windows, one point per signal;
  lm27-riskSplit  the widget's initial chart and its "widget" block: three annualized 5x5 covariance matrices.
The widget's arithmetic (Book.widgets.riskSplit.math in src/lm27.js) is run in Node against NumPy for R1 and two other
weight vectors under each matrix; the script stops on a mismatch.
Weights and shares are stored as fractions (0.459 for 45.9%) and printed by the chart formats.
"""
import json
import shutil
import subprocess
from typing import Any

import lm27_common as C
import numpy as np
from lm27_common import ROOT, SA, SM, F, J, N, Sn, sch, se, split

OUT = ROOT / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)
COL = {"0050": "1", "00646": "2", "00679B": "3", "00642U": "4", "00635U": "var(--muted)"}


def rd(x: float, n: int = 6) -> float:
    return round(float(x), n)


def write(name: str, spec: dict[str, Any]) -> None:
    assert isinstance(spec.get("alt"), str) and spec["alt"].strip()
    text = json.dumps(spec, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    assert len(text.encode("utf-8")) < 300_000, (name, len(text))
    (OUT / f"{name}.json").write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote src/data/{name}.json ({len(text.encode('utf-8')):,} bytes)")


# ---------------------------------------------------------------- X2: buy-and-hold drift (thinned, decision X37)
pts = sorted(C.pts)
assert len(pts) == 402 and pts[0] == 0
wts = [np.full(N, 1 / N) if i == 0 else C.wbh[i - 1] for i in pts]
dts = [C.d_all[i] for i in pts]
# every cited extreme and the end weights are plotted
for j in range(N):
    assert rd(C.wbh[:, j].min()) in [rd(w[j]) for w in wts] and rd(C.wbh[:, j].max()) in [rd(w[j]) for w in wts]
assert dts[-1] == "2026-10-08"
order = ["0050", "00646", "00679B", "00642U", "00635U"]
write("lm27-drift", {
    "alt": "Weights of a book bought at a fifth in each E5 fund at the close of 4 March 2019 and held without trades to "
           "8 October 2026: 0050 rises from 19.1% in August 2019 to 48.6% at the end, 00679B falls from 28.0% in March "
           "2020 to 5.4%, and 00642U ends at 11.7%",
    "height": 320,
    "x": {"type": "date", "values": dts},
    "y": {"type": "lin", "fmt": "pct1", "tfmt": "pct0", "label": "Weight in the book", "min": 0, "max": 0.5,
          "ticks": [0, 0.1, 0.2, 0.3, 0.4, 0.5]},
    "series": [{"name": s, "color": COL[s], "y": [rd(w[J[s]]) for w in wts]} for s in order],
    "ann": [{"type": "hline", "y": 0.2, "dash": True}],
})

# ---------------------------------------------------------------- X4: correlations by frequency
pair_names = [f"{F[a]}–{F[b]}" for a, b in C.pairs]
write("lm27-freq", {
    "type": "bar",
    "alt": "Correlations of daily, weekly and monthly simple returns for five pairs of E5 funds: 0050 with 00646 0.599, "
           "0.588, 0.552; 0050 with 00679B -0.105, -0.023, -0.013; 0050 with 00635U 0.180, 0.228, 0.187; 0050 with "
           "00642U 0.092, 0.073, 0.014; 00679B with 00642U -0.18, -0.20, -0.36",
    "height": 280, "categories": pair_names, "x": {"label": "Pair"},
    "y": {"fmt": "n3", "tfmt": "n1", "label": "Correlation", "min": -0.4, "max": 0.7,
          "ticks": [-0.4, -0.2, 0, 0.2, 0.4, 0.6]},
    "series": [{"name": nm, "color": str(k + 1), "fmt": "n3", "values": [rd(se[a, b, nm][0]) for a, b in C.pairs]}
               for k, nm in enumerate(("daily", "weekly", "monthly"))],
    "ann": [{"type": "hline", "y": 0}],
})

# ---------------------------------------------------------------- X6: money against risk, stacked
cats = ["R1 money", "R1 risk", "R2 money", "R2 risk"]
write("lm27-shares", {
    "type": "bar", "stack": True,
    "alt": "Money weights and risk shares of R1 and R2 at the full-sample covariance matrix: R1 puts a fifth of the "
           "money in each fund, but 45.9% of its risk is in 00642U and 2.6% in 00679B; R2 puts 40% of the money and "
           "63.5% of the risk in 0050",
    "height": 300, "categories": cats, "x": {"label": "Book"},
    "y": {"fmt": "pct1", "tfmt": "pct0", "label": "Share of the book", "min": 0, "max": 1,
          "ticks": [0, 0.2, 0.4, 0.6, 0.8, 1.0]},
    "series": [{"name": s, "color": COL[s], "fmt": "pct1",
                "values": [rd(C.w1[J[s]]), rd(C.sh1[J[s]]), rd(C.w2[J[s]]), rd(C.sh2[J[s]])]} for s in F],
})

# ---------------------------------------------------------------- X7: R1's shares in the 92 windows
assert len(sch) == 92
write("lm27-windows", {
    "alt": "R1's risk shares in the 92 trailing two-year windows, one point per month-end signal from February 2019 to "
           "September 2026: 00642U's share runs from 32.7% to 54.3%, and 00679B's is negative in 22 windows, lowest "
           "-1.89% in the window through 27 February 2020",
    "height": 320,
    "x": {"type": "date", "values": [d for d, _, _ in sch]},
    "y": {"type": "lin", "fmt": "pct2", "tfmt": "pct0", "label": "Share of R1's risk", "min": -0.05, "max": 0.6,
          "ticks": [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]},
    "series": [{"name": s, "color": COL[s], "y": [rd(C.SH[k, J[s]]) for k in range(len(sch))]} for s in order],
    "ann": [{"type": "hline", "y": 0, "dash": True}, {"type": "hline", "y": 0.2, "dash": True}],
})

# ---------------------------------------------------------------- widget: weights against risk shares
mats = {"daily": SA, "monthly": SM, "window": Sn}
mats10 = {k: [[round(float(M[a, b]), 10) for b in range(N)] for a in range(N)] for k, M in mats.items()}
for k, M in mats10.items():
    Mx = np.array(M)
    assert np.allclose(Mx, Mx.T, rtol=0, atol=0) and np.linalg.eigvalsh(Mx).min() > 0, k
w0 = [0.2, 0.2, 0.2, 0.2]
sp0, *_, sh0 = split(np.array(mats10["daily"]), C.w1)
write("lm27-riskSplit", {
    "type": "bar",
    "alt": "Money weights against risk shares of the equal-weight book under the daily full-sample covariance matrix: "
           "a fifth of the money in each fund, risk shares 21.2%, 17.7%, 2.6%, 12.6% and 45.9%",
    "height": 260, "categories": F, "x": {"label": "Fund"},
    "y": {"fmt": "pct1", "tfmt": "pct0", "label": "Share of the book"},
    "series": [{"name": "money", "color": "1", "values": [rd(x) for x in C.w1]},
               {"name": "risk", "color": "2", "values": [rd(x) for x in sh0]}],
    "ann": [{"type": "hline", "y": 0}],
    "widget": {"funds": F, "mats": mats10, "init": {"mat": "daily", "w": w0},
               "options": [["daily", "daily, 2017–2026"], ["monthly", "monthly, 2017–2026"],
                           ["window", "daily, window to 27 Feb 2020"]]},
})

# ---------------------------------------------------------------- the widget's arithmetic in Node against NumPy
DRIVER = r"""
const vm = require("vm"), fs = require("fs");
const ctx = { window: {}, document: { readyState: "loading", addEventListener() {} }, console };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[1], "utf8"), ctx);
vm.runInContext(fs.readFileSync(process.argv[2], "utf8"), ctx);
const M = ctx.window.Book.widgets.riskSplit.math, q = JSON.parse(fs.readFileSync(0, "utf8"));
process.stdout.write(JSON.stringify(q.cases.map(([k, w]) => M.split(q.mats[k], w))));
"""
node = shutil.which("node")
assert node, "Node is needed to check the widget (it is needed to build the site too)"
vecs: list[list[float]] = [C.w1.tolist(), [0.4, 0.2, 0.3, 0.1, 0.0], [0.5, 0.3, -0.2, 0.2, 0.2]]
cases: list[tuple[str, list[float]]] = [(k, w) for k in mats10 for w in vecs]
out = subprocess.run([node, "-e", DRIVER, str(ROOT / "src" / "assets" / "book.js"), str(ROOT / "src" / "lm27.js")],
                     input=json.dumps({"mats": mats10, "cases": cases}), capture_output=True, text=True,
                     encoding="utf-8", check=True)
got = json.loads(out.stdout)
worst = 0.0
for (k, w), g in zip(cases, got, strict=True):
    wv = np.array(w)
    sp, _, _, _, sh = split(mats[k], wv)                     # the unrounded matrix
    avg = float(np.abs(wv) @ np.sqrt(np.diag(mats[k])))
    worst = max(worst, abs(g["sp"] - sp) / sp, float(np.abs(np.array(g["shares"]) - sh).max()),
                abs(g["avg"] - avg) / avg, abs(g["sum"] - 1))
    assert g["shortSold"] == bool((wv < 0).any())
assert worst < 1e-8, worst
# the initial state (the PDF): R1 under the daily matrix, as the module prints it
g0 = got[0]
assert f"{100 * g0['sp']:.2f}" == "11.49" and [f"{100 * x:.1f}" for x in g0["shares"]] == \
    ["21.2", "17.7", "2.6", "12.6", "45.9"] and f"{g0['ratio']:.2f}" == "1.81"
print(f"widget arithmetic against NumPy: largest error {worst:.1e} ({len(cases)} cases, three matrices)")
