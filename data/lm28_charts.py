"""Chart specs for LM28 (src/data/lm28-*.json), computed from E5's first window, its test period and U28.

Run:  uv run python data/lm28_charts.py
      (after data/vol5_series.py, data/vol5_rules.py and data/vol2_series.py; data/lm28_numbers.py then checks the
      text, these files and the widget block)

Inputs and conventions: data/lm28_common.py. No file carries a dated series (shared decision "Charts", rule X37):
the charts hold curves, points and weights only. Writes
  lm28-frontier     the first window's frontier (efficient branch solid, lower branch dashed), the capital market line
                    from r_f through the tangency portfolio, the five funds, w_mv, w_tan, equal weights and the two
                    frontier portfolios of the equal-weight example; % a year;
  lm28-sensitivity  exact change of w_tan (points) for a 1-point rise in each mean, a heatmap;
  lm28-heldout      the window's efficient branch, the test period's ex-post efficient branch, and arrows from
                    predicted to realized (volatility, mean) for the two held portfolios;
  lm28-u28mv        U28's 28 minimum-variance weights, sorted, a bar chart;
  lm28-frontierLab  the widget's first drawing (lm28-frontier's layout) and its "widget" block: the first window's
                    annual mu (5), Sigma (5 x 5) and r_f, 31 numbers at full precision, and the fund names.
The widget's own arithmetic (Book.widgets.frontierLab.math.solve in src/lm28.js: a Cholesky factor that tests positive
definiteness, two triangular solves, (28.2), (28.5) and (28.6)) is run in Node on the initial state, the all-rounded
state and five slider settings (both failures of positive definiteness and one with r_f >= mu_mv) and compared with
NumPy; the script stops on a mismatch.
"""
import json
import math
import shutil
import subprocess
from typing import Any

import lm28_common as CM
import numpy as np
from lm28_common import RF, F, Opt, S, Vec, Wt, cov0, mu, o, ot, sd, u28

OUT = CM.ROOT / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)


def rd(x: float, n: int = 6) -> float:
    return round(float(x), n)


def write(name: str, spec: dict[str, Any]) -> None:
    assert isinstance(spec.get("alt"), str) and spec["alt"].strip()
    text = json.dumps(spec, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    assert len(text.encode("utf-8")) < 300_000, (name, len(text))
    (OUT / f"{name}.json").write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote src/data/{name}.json ({len(text.encode('utf-8')):,} bytes)")


def branch(op: Opt, lo: float, hi: float, n: int = 120) -> tuple[list[float], list[float]]:
    """(volatility, mean) in percent along (28.5) for means from lo to hi (fractions)."""
    ms = np.linspace(lo, hi, n)
    return [rd(100 * math.sqrt(op.front_var(float(m))), 4) for m in ms], [rd(100 * float(m), 4) for m in ms]


Y0, Y1 = -2.0, 12.0
sr = math.sqrt(o.sr2)
st = math.sqrt(float(o.wtan @ S @ o.wtan))
mtan = float(mu @ o.wtan)
wN = np.full(5, 0.2)
mN, sN = float(mu @ wN), math.sqrt(float(wN @ S @ wN))
me = o.mumv + math.sqrt(o.srinf2 * (sN**2 - o.s2min))
ex, ey = branch(o, o.mumv, Y1 / 100)
ix, iy = branch(o, Y0 / 100, o.mumv)
cml_end = (Y1 / 100 - RF) / sr
frontier_spec: dict[str, Any] = {
    "type": "scatter",
    "alt": "The first window's mean-variance frontier in volatility and mean, % a year: the efficient branch rises from "
           "the minimum-variance portfolio at 5.02% and 4.34%; the capital market line runs from 1.5% through the "
           "tangency portfolio at 7.81% and 8.38%; equal weights lie inside the frontier at 7.38% and 3.91%",
    "height": 330,
    "x": {"label": "Volatility (% a year)", "fmt": "n2", "tfmt": "n0", "min": 0, "max": 25, "ticks": [0, 5, 10, 15, 20, 25],
          "name": "volatility"},
    "y": {"label": "Mean (% a year)", "fmt": "n2", "tfmt": "n0", "min": Y0, "max": Y1, "ticks": [-2, 0, 2, 4, 6, 8, 10, 12],
          "name": "mean"},
    "series": [{"name": "funds", "color": "1", "x": [rd(100 * v, 4) for v in sd], "y": [rd(100 * m, 4) for m in mu],
                "labels": list(F)}],
    "curves": [
        {"x": ex, "y": ey, "color": "2", "width": 2},
        {"x": ix, "y": iy, "color": "2", "dash": True},
        {"x": [0, rd(100 * cml_end, 4)], "y": [rd(100 * RF, 4), Y1], "color": "3", "dash": True},
    ],
    "points": [
        {"at": [rd(100 * math.sqrt(o.s2min), 4), rd(100 * o.mumv, 4)], "label": "minimum variance", "color": "4",
         "dx": 6, "dy": -6},
        {"at": [rd(100 * st, 4), rd(100 * mtan, 4)], "label": "tangency", "color": "4", "dx": -8, "dy": -8},
        {"at": [rd(100 * sN, 4), rd(100 * mN, 4)], "label": "equal weights", "color": "var(--muted)", "dx": 6, "dy": 8},
        {"at": [rd(100 * math.sqrt(o.front_var(mN)), 4), rd(100 * mN, 4)], "color": "var(--muted)", "r": 2.5},
        {"at": [rd(100 * sN, 4), rd(100 * me, 4)], "color": "var(--muted)", "r": 2.5},
    ],
}
assert f"{100 * math.sqrt(o.front_var(mN)):.2f}" == "5.05" and f"{100 * me:.2f}" == "7.99"
write("lm28-frontier", frontier_spec)

# ---------------------------------------------------------------- X3: exact sensitivity of w_tan
dW = np.zeros((5, 5))
for i in range(5):
    m2 = mu.copy()
    m2[i] += 0.01
    dW[:, i] = Opt(m2, S).wtan - o.wtan
assert [f"{100 * dW[i, i]:+.1f}" for i in range(5)] == ["+6.6", "+4.7", "+7.6", "+10.3", "+1.9"]
write("lm28-sensitivity", {
    "type": "heatmap",
    "alt": "Exact change of the first window's tangency weights, in points, when one fund's mean rises by 1 point: "
           "gold's own weight rises 10.3 points, 0050's 6.6, 00679B's 7.6, 00646's 4.7 and oil's 1.9",
    "rows": [f"{s} weight" for s in F],
    "cols": [f"{s} mean" for s in F],
    "matrix": [[rd(100 * dW[i, j], 4) for j in range(5)] for i in range(5)],
    "fmt": "n1", "min": -12, "max": 12, "scaleFmt": "n0", "valueName": "change, points",
})

# ---------------------------------------------------------------- X4: predicted against realized
held = {}
for name, w in (("mv", o.wmv), ("tan", o.wtan)):
    r = Wt @ w
    held[name] = (100 * float(r.std(ddof=0)) * math.sqrt(CM.Aw), 100 * float(r.mean()) * CM.Aw,
                  100 * math.sqrt(float(w @ S @ w)), 100 * float(mu @ w))
H1 = 16.0
wx, wy = branch(o, o.mumv, H1 / 100)
tx, ty = branch(ot, ot.mumv, H1 / 100)
write("lm28-heldout", {
    "type": "scatter",
    "alt": "Predicted against realized volatility and mean of the first window's two portfolios held from March 2019 to "
           "October 2026, % a year: minimum variance moved from 5.02% and 4.34% to 10.05% and 9.14%, the tangency "
           "portfolio from 7.81% and 8.38% to 14.15% and 10.79%; the test period's own frontier starts at 9.63% and 8.22%",
    "height": 330,
    "x": {"label": "Volatility (% a year)", "fmt": "n2", "tfmt": "n0", "min": 0, "max": 20, "ticks": [0, 4, 8, 12, 16, 20],
          "name": "volatility"},
    "y": {"label": "Mean (% a year)", "fmt": "n2", "tfmt": "n0", "min": 0, "max": H1, "ticks": [0, 4, 8, 12, 16],
          "name": "mean"},
    "curves": [
        {"x": wx, "y": wy, "color": "2", "width": 2, "label": "first window"},
        {"x": tx, "y": ty, "color": "4", "dash": True, "label": "test period"},
    ],
    "vectors": [
        {"from": [rd(held["mv"][2], 4), rd(held["mv"][3], 4)], "to": [rd(held["mv"][0], 4), rd(held["mv"][1], 4)],
         "label": "minimum variance", "color": "1"},
        {"from": [rd(held["tan"][2], 4), rd(held["tan"][3], 4)], "to": [rd(held["tan"][0], 4), rd(held["tan"][1], 4)],
         "label": "tangency", "color": "3"},
    ],
    "points": [{"at": [rd(100 * math.sqrt(ot.s2min), 4), rd(100 * ot.mumv, 4)], "label": "test-period minimum",
                "color": "4", "dx": 6, "dy": 14}],
})
assert [f"{v:.2f}" for v in held["mv"]] == ["10.05", "9.14", "5.02", "4.34"]
assert [f"{v:.2f}" for v in held["tan"]] == ["14.15", "10.79", "7.81", "8.38"]

# ---------------------------------------------------------------- X5: U28's minimum-variance weights
u = u28()
ou = Opt(u.A * u.X.mean(axis=0), u.A * cov0(u.X))
order = np.argsort(-ou.wmv)
write("lm28-u28mv", {
    "type": "bar",
    "alt": "U28's 28 minimum-variance weights, sorted, on the full sample of sector price indices: CommunicationsInternet "
           "takes 53.6%, 12 sectors are shorted, the largest short being Optoelectronic at -10.8%; gross exposure 2.24",
    "height": 300,
    "categories": [u.names[int(k)] for k in order],
    "x": {"label": "Sector price index"},
    "y": {"fmt": "pct1", "tfmt": "pct0", "label": "Weight", "min": -0.2, "max": 0.6, "ticks": [-0.2, 0, 0.2, 0.4, 0.6]},
    "series": [{"name": "minimum-variance weight", "color": "1", "values": [rd(float(ou.wmv[int(k)])) for k in order],
                "fmt": "pct1"}],
    "ann": [{"type": "hline", "y": 0}],
})
assert int((ou.wmv < -1e-6).sum()) == 12

# ---------------------------------------------------------------- the widget: data block and its arithmetic in Node
widget_spec = dict(frontier_spec)
widget_spec["alt"] = ("Frontier explorer: " + frontier_spec["alt"] + "; sliders move 00646's mean, 00635U's mean and the "
                      "correlation of 0050 and 00646")
widget_spec["widget"] = {"funds": list(F), "mu": [float(v) for v in mu], "S": [[float(v) for v in row] for row in S],
                         "rf": RF,
                         "sliders": {"mu646": 10.0, "mu635": 0.8, "rho": 0.54}}
assert len(widget_spec["widget"]["mu"]) + 25 + 1 == 31
write("lm28-frontierLab", widget_spec)

DRIVER = r"""
const vm = require("vm"), fs = require("fs");
const ctx = { window: {}, document: { readyState: "loading", addEventListener() {} }, console };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[1], "utf8"), ctx);
vm.runInContext(fs.readFileSync(process.argv[2], "utf8"), ctx);
const M = ctx.window.Book.widgets.frontierLab.math, q = JSON.parse(fs.readFileSync(0, "utf8"));
process.stdout.write(JSON.stringify(q.map(c => M.solve(c.mu, c.S, c.rf))));
"""


def with_corr(S_: np.ndarray, r_: float) -> np.ndarray:
    S2 = S_.copy()
    S2[0, 1] = S2[1, 0] = r_ * sd[0] * sd[1]
    return S2


def case(mu646: float | None, mu635: float | None, rho: float | None) -> tuple[Vec, np.ndarray]:
    m = mu.copy()
    if mu646 is not None:
        m[1] = mu646 / 100
    if mu635 is not None:
        m[3] = mu635 / 100
    return m, (S if rho is None else with_corr(S, rho))


cases = [case(None, None, None), case(10.0, 0.8, 0.54), case(None, None, -0.74), case(None, None, 0.97),
         case(0.0, -5.0, None), case(20.0, 10.0, 0.99 - 0.03), case(5.0, 3.0, -0.73), case(15.0, -2.0, 0.2)]
node = shutil.which("node")
assert node, "Node is needed to check the widget (it is needed to build the site too)"
payload = [{"mu": [float(v) for v in m], "S": [[float(v) for v in row] for row in S_], "rf": RF} for m, S_ in cases]
res = subprocess.run([node, "-e", DRIVER, str(CM.ROOT / "src" / "assets" / "book.js"), str(CM.ROOT / "src" / "lm28.js")],
                     input=json.dumps(payload), capture_output=True, text=True, encoding="utf-8", check=True)
got = json.loads(res.stdout)
worst = 0.0
seen = {"pd_fail": 0, "no_tan": 0, "ok": 0}
for (m, S_), g in zip(cases, got, strict=True):
    pd = bool(np.linalg.eigvalsh(S_).min() > 0)
    if not pd:
        assert g is None, ("the widget drew a frontier for a matrix that is not positive definite", g)
        seen["pd_fail"] += 1
        continue
    assert g is not None
    ref = Opt(m, S_)
    worst = max(worst, float(np.abs(np.array(g["wmv"]) - ref.wmv).max()), abs(g["s2min"] - ref.s2min),
                abs(g["mumv"] - ref.mumv), abs(g["srinf2"] - ref.srinf2), abs(g["den"] - ref.den),
                abs(g["sr"] - math.sqrt(ref.sr2)))
    if ref.den > 0:
        assert g["wtan"] is not None
        worst = max(worst, float(np.abs(np.array(g["wtan"]) - ref.wtan).max()))
        seen["ok"] += 1
    else:
        assert g["wtan"] is None
        seen["no_tan"] += 1
assert worst < 1e-10, worst
assert seen["pd_fail"] == 2 and seen["no_tan"] >= 1, seen
g0, g1 = got[0], got[1]
assert [f"{100 * v:.1f}" for v in g0["wtan"]] == ["11.8", "62.6", "37.8", "2.6", "-14.7"]
assert f"{g0['sr']:.3f}" == "0.880" and f"{100 * g0['mumv']:.2f}" == "4.34"
assert [f"{100 * v:.1f}" for v in g1["wtan"]] == ["11.8", "62.4", "37.8", "2.7", "-14.7"]
assert f"{g1['sr']:.3f}" == "0.878" and f"{100 * g1['mumv']:.2f}" == "4.33"
print(f"widget arithmetic against NumPy: largest gap {worst:.1e} over {len(cases)} settings ({seen})")
