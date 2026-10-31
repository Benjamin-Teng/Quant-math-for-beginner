"""Chart specs for LM29 (src/data/lm29-*.json), computed on E5's estimation frame through data/lm29_common.py.

Run:  PYTHONUTF8=1 uv run python data/lm29_charts.py
      (after data/vol5_series.py and data/vol5_rules.py, whose processed files data/lm29_common.py reads; then
      data/lm29_numbers.py checks the text and these files)

Writes, all in-sample on a window's annual plug-in inputs (no daily series is published, plans/vol-5.md "Charts"):
  lm29-kktR4     R4 at the last signal: each fund's excess return e_i beside beta_ip (mu_p - r_f), % a year, (29.7);
  lm29-limits    maximum-Sharpe weights under four sets of limits on the last window, % (A29-15);
  lm29-frontier  the unconstrained frontier ((28.4), closed form) and the long-only frontier (a QP at each target
                 mean of a grid, by CLARABEL at the book's tolerances, checked against OSQP and, where every weight
                 of the closed form is non-negative, against the closed form), the two capital market lines, the
                 funds, R3, R4 and the tangency, as fractions a year;
  lm29-band      the variance gradient at the cost-penalized R3 of 2025-04-30 (theta = 1) and the band's edges;
  lm29-kktPair   the widget's initial chart and its "widget" block: the first window's e, s (0050, 00646) and rho,
                 unrounded, and the initial cap 1 and delta 4.
The widget's arithmetic (Book.widgets.kktPair.math in src/lm29.js) is run in Node on a grid of caps and risk
aversions and compared with data/lm29_common.py's pair_kkt; the script stops on a mismatch.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import cvxpy as cp
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lm29_common as C  # computes every anchor quantity on import

ROOT = HERE.parent
OUT = ROOT / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)
FUNDS = C.FUNDS


def rd(x: float, n: int = 6) -> float:
    return round(float(x), n)


def write(name: str, spec: dict[str, Any]) -> None:
    assert isinstance(spec.get("alt"), str) and spec["alt"].strip()
    text = json.dumps(spec, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    assert len(text.encode("utf-8")) < 300_000, (name, len(text))
    (OUT / f"{name}.json").write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote src/data/{name}.json ({len(text.encode('utf-8')):,} bytes)")


# ---------------------------------------------------------------- R4's KKT bars (29.7)
e_pct = [rd(100 * v, 3) for v in C.eL]
ask_pct = [rd(100 * v, 3) for v in C.b4 * C.ep]
assert [f"{v:.3f}" for v in e_pct] == ["47.275", "16.437", "-7.276", "19.178", "34.596"], e_pct
assert [f"{v:.3f}" for v in ask_pct] == ["47.275", "21.623", "-0.797", "19.178", "34.596"], ask_pct
write("lm29-kktR4", {
    "type": "bar",
    "alt": "Bars for the five funds at R4 on the last window: each fund's excess return beside its beta to the "
           "portfolio times the portfolio's excess return. The bars are equal for 0050, 00635U and 00642U; 00646 "
           "earns 16.437 points against 21.623 asked, and 00679B -7.276 against -0.797.",
    "height": 300,
    "categories": FUNDS,
    "x": {"label": "Fund"},
    "y": {"fmt": "n3", "tfmt": "n0", "label": "% a year"},
    "series": [{"name": "Excess return e_i", "color": "1", "values": e_pct, "fmt": "n3"},
               {"name": "β_{i,p} × (μ_p − r_f)", "color": "2", "values": ask_pct, "fmt": "n3"}],
    "ann": [{"type": "hline", "y": 0}],
})

# ---------------------------------------------------------------- weights under limits (A29-15)
names = {"unconstrained": "Unconstrained", "gross <= 150%": "Gross ≤ 150%", "long-only (R4)": "Long-only (R4)",
         "long-only, cap 40%": "Long-only, cap 40%"}
series = []
for k, (key, w) in enumerate(C.lims.items()):
    vals = [0.0 if abs(v) < C.ZERO else rd(100 * v, 2) for v in w]
    assert abs(sum(vals) - 100) < 0.005 + 1e-9, (key, sum(vals))
    series.append({"name": names[key], "color": str(k + 1), "values": vals, "fmt": "n2"})
write("lm29-limits", {
    "type": "bar",
    "alt": "Grouped bars of the maximum-Sharpe weights of the five funds on the last window under four sets of "
           "limits: unconstrained (114.24% in 0050, shorts in 00646 and 00679B), gross exposure at most 150%, "
           "long-only (R4: 62.77% in 0050, nothing in 00646 and 00679B) and long-only with a 40% cap.",
    "height": 320,
    "categories": FUNDS,
    "x": {"label": "Fund"},
    "y": {"fmt": "n2", "tfmt": "n0", "label": "Weight (%)"},
    "series": series,
    "ann": [{"type": "hline", "y": 0}],
})

# ---------------------------------------------------------------- frontiers
SL, muL = C.SL, C.muL
lo_m, hi_m = C.lo_m, C.hi_m


def vol(w: np.ndarray) -> float:
    return float(np.sqrt(w @ SL @ w))


def long_only(m: float) -> np.ndarray:
    """The long-only frontier at target mean m: CLARABEL at the book's tolerances, checked against OSQP."""
    w = C.lo_front(m)
    x = cp.Variable(len(FUNDS))
    _, wo = C.solve(cp.quad_form(x, cp.psd_wrap(SL)), [cp.sum(x) == 1, muL @ x == m, x >= 0], cp.OSQP, C.OSQP_OPTS)
    wo = C.must(wo, f"long-only frontier OSQP at {m}")
    # an interior point leaves near-zero weights of a few 1e-6 where a weight sits on its bound (at the ends of the
    # coincidence range), so the cross-check uses the shared conic tolerance 1e-5 (plans/vol-5.md, "Solver output")
    assert np.abs(w - wo).max() < 1e-5, (m, np.abs(w - wo).max())
    if lo_m - 1e-12 <= m <= hi_m + 1e-12:              # where the closed form is long-only, the two coincide
        assert np.abs(w - C.w_front(m)).max() < 1e-5, (m, np.abs(w - C.w_front(m)).max())
    return w


m_min, m_max = float(muL.min()), float(muL.max())
grid_lo = sorted(set([round(v, 6) for v in np.linspace(m_min + 0.002, m_max - 0.002, 60)] +
                     [round(lo_m, 6), round(hi_m, 6), 0.40, round(C.mgmv, 6), round(float(C.w4L @ muL), 6)]))
lo_x = [rd(vol(long_only(m))) for m in grid_lo]
lo_y = [rd(m) for m in grid_lo]
# the ends of the long-only frontier are single funds: 00679B (lowest mean) and 0050 (highest)
i_lo, i_hi = int(np.argmin(muL)), int(np.argmax(muL))
lo_x = [rd(C.volL[i_lo])] + lo_x + [rd(C.volL[i_hi])]
lo_y = [rd(muL[i_lo])] + lo_y + [rd(muL[i_hi])]
un_grid = np.linspace(-0.10, 0.76, 87)
un_x = [rd(vol(C.w_front(float(m)))) for m in un_grid]
un_y = [rd(float(m)) for m in un_grid]
# the cited values are plotted: the coincidence range, the 40% target, the end at 0050
v40u, v40l = vol(C.w30u), vol(C.w30l)
assert f"{100 * v40u:.2f}" == "18.29" and f"{100 * v40l:.2f}" == "18.32"
assert rd(v40l) in lo_x and 0.4 in lo_y
srT, srR = C.sr(C.wtL, SL, C.eL), C.sr(C.w4L, SL, C.eL)
x_end = 0.36
write("lm29-frontier", {
    "type": "scatter",
    "alt": "Mean against volatility on the last window: the unconstrained frontier (dashed) and the long-only "
           "frontier (solid) coincide for target means from 4.12% to 30.44%; above that the long-only frontier lies "
           "to the right and ends at 0050. Two capital market lines from 1.5% touch the tangency (71.13%, 31.94%) "
           "and R4 (41.22%, 18.85%); R3 is the global minimum (8.46%, 10.10%).",
    "height": 380,
    "x": {"label": "Volatility, % a year", "fmt": "pct2", "tfmt": "pct0", "min": 0, "max": 0.52,
          "ticks": [0, 0.1, 0.2, 0.3, 0.4, 0.5], "name": "volatility"},
    "y": {"label": "Mean, % a year", "fmt": "pct2", "tfmt": "pct0", "min": -0.1, "max": 0.8,
          "ticks": [-0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8], "name": "mean"},
    "series": [{"name": "Funds", "color": "3", "x": [rd(v) for v in C.volL], "y": [rd(v) for v in muL],
                "labels": FUNDS}],
    "curves": [
        {"x": un_x, "y": un_y, "color": "1", "dash": True, "label": "unconstrained"},
        {"x": lo_x, "y": lo_y, "color": "2", "label": "long-only"},
        {"x": [0, x_end], "y": [C.RF, rd(C.RF + srT * x_end)], "color": "1", "dash": True, "width": 1},
        {"x": [0, x_end], "y": [C.RF, rd(C.RF + srR * x_end)], "color": "2", "dash": True, "width": 1},
    ],
    "points": [
        {"at": [rd(vol(C.w3L)), rd(C.mgmv)], "label": "R3", "color": "4"},
        {"at": [rd(vol(C.w4L)), rd(float(C.w4L @ muL))], "label": "R4", "color": "2"},
        {"at": [rd(vol(C.wtL)), rd(float(C.wtL @ muL))], "label": "tangency", "color": "1"},
    ],
})

# ---------------------------------------------------------------- the no-trade band (2025-04-30, theta = 1)
g = [rd(v, 6) for v in C.gp1]
buy, sell, sell0 = C.lam_b - C.COMMISSION, C.lam_b + C.COMMISSION + 0.001, C.lam_b + C.COMMISSION
assert [f"{v:.6f}" for v in g] == ["0.017684", "0.019085", "0.015235", "0.015235", "0.019085"], g
write("lm29-band", {
    "type": "bar",
    "alt": "Bars of the variance gradient of each fund at the cost-penalized R3 of 30 April 2025 (theta 1): the two "
           "bought funds sit on the buy edge 0.015235, the two sold funds on their sell edges, 0050 inside the band.",
    "height": 300,
    "categories": FUNDS,
    "x": {"label": "Fund"},
    "y": {"fmt": "n6", "tfmt": "n3", "label": "Gradient (2Σw)_i", "min": 0.014, "max": 0.0195,
          "ticks": [0.014, 0.015, 0.016, 0.017, 0.018, 0.019]},
    "series": [{"name": "Gradient at θ = 1", "color": "1", "values": g, "fmt": "n6"}],
    "ann": [{"type": "hline", "y": rd(buy), "label": "buy edge 0.015235"},
            {"type": "hline", "y": rd(sell0), "label": "00679B's sell edge 0.018085"},
            {"type": "hline", "y": rd(sell), "label": "sell edge 0.019085"}],
})

# ---------------------------------------------------------------- the widget: two funds and cash
pS, pE = C.pairS, C.pairE
s1, s2 = float(np.sqrt(pS[0, 0])), float(np.sqrt(pS[1, 1]))
rho = float(pS[0, 1] / (s1 * s2))
block = {"e": [float(pE[0]), float(pE[1])], "s": [s1, s2], "rho": rho, "cap": 1.0, "delta": 4.0}
DRIVER = r"""
const vm = require("vm"), fs = require("fs");
const ctx = { window: {}, document: { readyState: "loading", addEventListener() {} }, console };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[1], "utf8"), ctx);
vm.runInContext(fs.readFileSync(process.argv[2], "utf8"), ctx);
const M = ctx.window.Book.widgets.kktPair.math, q = JSON.parse(fs.readFileSync(0, "utf8"));
const S = [[q.s[0] * q.s[0], q.rho * q.s[0] * q.s[1]], [q.rho * q.s[0] * q.s[1], q.s[1] * q.s[1]]];
process.stdout.write(JSON.stringify(q.cases.map(([d, c]) => M.candidates(q.e, S, d, c))));
"""
node = shutil.which("node")
assert node, "Node is needed to check the widget (it is needed to build the site too)"
cases = [[d, c] for d in (1.0, 2.5, 4.0, 7.0, 10.0) for c in (0.2, 0.5, 1.0, 1.5, 2.0)]
res = subprocess.run([node, "-e", DRIVER, str(ROOT / "src" / "assets" / "book.js"), str(ROOT / "src" / "lm29.js")],
                     input=json.dumps({**block, "cases": cases}), capture_output=True, text=True, encoding="utf-8",
                     check=True)
got = json.loads(res.stdout)
worst = 0.0
S_js = np.array([[s1 * s1, rho * s1 * s2], [rho * s1 * s2, s2 * s2]])
for (d, c), js in zip(cases, got, strict=True):
    py = C.pair_kkt(S_js, np.array(block["e"]), d, c)
    assert len(js) == len(py) == 8
    for a, b in zip(js, py, strict=True):
        assert (a["f"] is None) == (b[1] is None), (d, c, a["label"], b[0])
        if b[1] is None:
            continue
        assert a["feasible"] == b[3] and a["signs"] == b[4], (d, c, b[0])
        worst = max(worst, float(np.abs(np.array(a["f"]) - b[1]).max()),
                    float(np.abs(np.array(a["nu"]) - b[2]).max(initial=0.0)), abs(a["utility"] - b[5]))
    assert sum(1 for a in js if a["f"] is not None and a["feasible"] and a["signs"]) == 1, (d, c)
assert worst < 1e-10, worst
print(f"widget arithmetic against pair_kkt: largest difference {worst:.1e} ({len(cases)} settings x 8 binding sets)")

init = got[cases.index([4.0, 1.0])]
best = next(a for a in init if a["f"] is not None and a["feasible"] and a["signs"])
fu = np.linalg.solve(4.0 * S_js, np.array(block["e"]))
dd = np.array(best["f"]) - fu
k = float(np.sqrt(dd @ S_js @ dd))
Si = np.linalg.inv(S_js)
cov_i = [[rd(Si[0, 0], 4), rd(Si[0, 1], 4)], [rd(Si[1, 0], 4), rd(Si[1, 1], 4)]]
pts = [{"at": [rd(a["f"][0]), rd(a["f"][1])], "color": "var(--muted)", "r": 3.5}
       for a in init if a["f"] is not None and a is not best]
pts.append({"at": [rd(best["f"][0]), rd(best["f"][1])], "color": "1", "r": 5.5, "label": "optimum: " + best["label"]})
write("lm29-kktPair", {
    "type": "scatter", "equal": False, "height": 340,
    "alt": "The plane of exposures to 0050 and 00646 with the feasible triangle for a cap of 1, contours of the "
           "objective at delta 4, and the KKT candidates of the binding sets; the optimum is at (0.00, 1.00)",
    "x": {"label": "f₁, exposure to 0050", "fmt": "n2", "min": -0.5, "max": 2.5, "name": "f₁"},
    "y": {"label": "f₂, exposure to 00646", "fmt": "n2", "min": -0.5, "max": 2.5, "name": "f₂"},
    "lines": [{"from": [0, 0], "to": [1, 0]}, {"from": [1, 0], "to": [0, 1]}, {"from": [0, 1], "to": [0, 0]}],
    "ellipses": [{"center": [rd(fu[0]), rd(fu[1])], "cov": cov_i, "scale": rd(sc), "color": "var(--muted)"}
                 for sc in (k, 2 * k)],
    "points": pts,
    "widget": block,
})
