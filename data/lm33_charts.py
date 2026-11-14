"""Chart specs for LM33 (src/data/lm33-*.json), computed from the through case's eight rules and from model curves.

Run:  uv run python data/lm33_charts.py
      (after data/vol5_series.py, data/vol5_rules.py and data/vol3_series.py; data/lm33_numbers.py then checks the
      text and the widget block)

Inputs and conventions: data/lm33_common.py (the anchor script's computations; E5 through vol5_series, the rules
through vol5_rules). Writes
  lm33-forest     the eight rules' annual Sharpe ratios with their 95% intervals by (20.9) and by (33.1), lag 7
                  (a scatter forest plot, R1 at the top);
  lm33-haclag     (33.1) a year at lags 0 to 60 for R1, R2 and R4 (line);
  lm33-psrT       PSR(0) of normal returns at annual Sharpe ratios 0.5, 1.0 and 1.5 against the record in years of
                  sessions, 0.5 to 15 (log x; model);
  lm33-pairs      R2 .. R8 against R1: Ledoit and Wolf's difference with its HAC and bootstrap intervals (scatter);
  lm33-deflate    the deflated benchmark E Z_(n) / sqrt(T - 1) a year against n, 1 to 10,000, exact and approximate
                  (log x; model);
  lm33-haircut    the eight rules' Sharpe ratios and their haircut ratios, independent tests and Holm (bars);
  lm33-mintrack   the widget's initial chart (R2's DSR against the record, n = 8) and its "widget" block: per rule
                  the daily Sharpe ratio, skewness, raw kurtosis and T, with A_w and tau (all unrounded).
No published file carries a daily series (plans/vol-5.md, "Charts", X37): only per-rule statistics and model curves.
The script then runs the widget's functions (src/lm33.js, Book.widgets.minTrack.math) in Node against Python on the
eight rules at ten trial counts, three confidence levels and three observation frequencies, and stops on a relative
difference above 1e-6 in E Z_(n) or MinTRL, or above 1e-9 in DSR; it checks the widget's initial readouts.
"""
import json
import math
import shutil
import subprocess
from typing import Any

import lm33_common as K
import numpy as np
from scipy import stats

ROOT = K.HERE.parent
OUT = ROOT / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)
RULES = K.RULES
sqA = K.sqA


def rd(x: float, n: int = 6) -> float:
    return round(float(x), n)


def write(name: str, spec: dict[str, Any]) -> None:
    assert isinstance(spec.get("alt"), str) and spec["alt"].strip()
    text = json.dumps(spec, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    assert len(text.encode("utf-8")) < 300_000, (name, len(text))
    (OUT / f"{name}.json").write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote src/data/{name}.json ({len(text.encode('utf-8')):,} bytes)")


# ---------------------------------------------------------------- X2: forest plot of the eight Sharpe ratios
yr = {k: 8 - i for i, k in enumerate(RULES)}                   # R1 at the top
lines: list[dict[str, Any]] = []
for k in RULES:
    lo9, hi9 = K.CI9[k]
    loh, hih = K.CIH[k]
    lines += [{"from": [rd(lo9), yr[k]], "to": [rd(hi9), yr[k]], "color": "1", "width": 3.5},
              {"from": [rd(loh), yr[k] + 0.2], "to": [rd(hih), yr[k] + 0.2], "color": "var(--muted)", "width": 1.5}]
lines.append({"from": [0, 0.5], "to": [0, 8.6], "dash": True, "color": "var(--muted)", "width": 1})
assert f"{K.CI9['R2'][0]:.2f} {K.CI9['R2'][1]:.2f}" == "0.42 1.86"
write("lm33-forest", {
    "type": "scatter", "equal": False, "height": 320,
    "alt": "The eight rules' annual Sharpe ratios out of sample, from 0.63 for R4 to 1.14 for R2, each with a 95% "
           "interval about 0.73 wide on either side by (20.9) and a nearly equal one by the HAC standard error; every "
           "interval but R4's lies above 0",
    "x": {"label": "Sharpe ratio a year", "fmt": "n3", "tfmt": "n1", "min": -0.2, "max": 2.0,
          "ticks": [-0.2, 0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0], "name": "Sharpe ratio"},
    "y": {"label": "", "fmt": "n0", "min": 0.5, "max": 8.6, "ticks": list(range(1, 9)),
          "tickLabels": [RULES[8 - t] for t in range(1, 9)], "name": "rule"},
    "series": [{"name": "Estimate", "color": "1", "x": [rd(K.SR[k] * sqA) for k in RULES],
                "y": [yr[k] for k in RULES], "r": 4}],
    "lines": lines,
})

# ---------------------------------------------------------------- X3: the HAC standard error by lag
lc = K.LAGCURVE
lo_ = min(min(v) for v in lc.values())
hi_ = max(max(v) for v in lc.values())
assert 0.28 < lo_ and hi_ < 0.42, (lo_, hi_)
for k, want in (("R1", "0.370 0.363 0.359 0.367"), ("R2", "0.367 0.382 0.393 0.389"), ("R4", "0.368 0.340 0.316 0.300")):
    assert " ".join(f"{lc[k][lg]:.3f}" for lg in (0, 7, 20, 60)) == want, k
write("lm33-haclag", {
    "alt": "The annual Sharpe ratio's HAC standard error against the lag from 0 to 60 for R1, R2 and R4: R2's rises "
           "from 0.367 to about 0.39, R4's falls from 0.368 to 0.300, R1's stays near 0.36",
    "height": 280,
    "x": {"type": "num", "fmt": "n0", "label": "HAC lag (sessions)", "min": 0, "max": 60,
          "ticks": [0, 7, 10, 20, 30, 40, 50, 60], "values": K.LAGS},
    "y": {"type": "lin", "fmt": "n3", "tfmt": "n2", "label": "Standard error a year", "min": 0.28, "max": 0.42,
          "ticks": [0.28, 0.30, 0.32, 0.34, 0.36, 0.38, 0.40, 0.42]},
    "series": [{"name": k, "color": c, "y": [rd(v) for v in lc[k]]} for k, c in (("R1", "1"), ("R2", "2"), ("R4", "3"))],
    "ann": [{"type": "hline", "y": 0.363, "dash": True, "label": "normal 0.363"},
            {"type": "vline", "x": 7, "dash": True, "label": "book's lag 7"}],
})

# ---------------------------------------------------------------- X4: PSR(0) against the record's length (model)
assert [f"{K.X4_MIN[a]:.2f}" for a in K.X4_SR] == ["10.83", "2.72", "1.21"]
assert [f"{K.X4_AT[a]:.3f}" for a in K.X4_SR] == ["0.916", "0.997", "1.000"]
write("lm33-psrT", {
    "alt": "PSR(0) of normal returns against the record in years of sessions on a log scale, for annual Sharpe ratios "
           "0.5, 1.0 and 1.5: each curve crosses 0.95 at its minimum track record, 10.83, 2.72 and 1.21 years",
    "height": 300,
    "x": {"type": "log", "fmt": "n2", "tfmt": "n1", "label": "Record, years of sessions (log scale)", "min": 0.5,
          "max": 15, "ticks": [0.5, 1, 2, 5, 10], "values": [rd(t) for t in K.X4_TAU]},
    "y": {"type": "lin", "fmt": "n3", "tfmt": "n1", "label": "PSR(0)", "min": 0.5, "max": 1.0,
          "ticks": [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]},
    "series": [{"name": f"annual SR {a:.1f}", "color": c, "y": [rd(v) for v in K.X4_PSR[a]]}
               for a, c in zip(K.X4_SR, ("1", "2", "3"), strict=True)],
    "ann": [{"type": "hline", "y": 0.95, "dash": True},
            {"type": "vline", "x": rd(K.tau), "dash": True, "label": "E5's record 7.60"}]
           + [{"type": "point", "x": rd(K.X4_MIN[a]), "y": 0.95, "label": f"{K.X4_MIN[a]:.2f}"} for a in K.X4_SR],
})

# ---------------------------------------------------------------- X5: each rule against R1
py = {k: 8 - i for i, k in enumerate(RULES[1:], start=1)}     # R2 - R1 at the top (7)
plines: list[dict[str, Any]] = []
for k in RULES[1:]:
    p = K.PAIR[k]
    plines += [{"from": [rd(p["hac_lo"]), py[k]], "to": [rd(p["hac_hi"]), py[k]], "color": "1", "width": 3.5},
               {"from": [rd(p["boot_lo"]), py[k] + 0.2], "to": [rd(p["boot_hi"]), py[k] + 0.2],
                "color": "var(--muted)", "width": 1.5}]
plines.append({"from": [0, 0.5], "to": [0, 7.6], "dash": True, "color": "var(--muted)", "width": 1})
assert f"{K.PAIR['R4']['boot_lo']:+.2f} {K.PAIR['R4']['boot_hi']:+.2f}" == "-0.95 +0.25"
write("lm33-pairs", {
    "type": "scatter", "equal": False, "height": 300,
    "alt": "Each rule's Sharpe ratio minus R1's, a year, with Ledoit and Wolf's HAC and bootstrap 95% intervals: R2's "
           "lead of 0.16 and every other gap lie well inside intervals that contain 0",
    "x": {"label": "Difference from R1, Sharpe ratio a year", "fmt": "n3", "tfmt": "n1", "min": -1.0, "max": 0.8,
          "ticks": [-1.0, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8], "name": "difference"},
    "y": {"label": "", "fmt": "n0", "min": 0.5, "max": 7.6, "ticks": list(range(1, 8)),
          "tickLabels": [f"{RULES[8 - t]} − R1" for t in range(1, 8)], "name": "pair"},
    "series": [{"name": "Difference", "color": "1", "x": [rd(K.PAIR[k]["d"]) for k in RULES[1:]],
                "y": [py[k] for k in RULES[1:]], "r": 4}],
    "lines": plines,
})

# ---------------------------------------------------------------- X6: the deflated benchmark against n (model)
xn = [rd(n, 6) for n in K.X6_N]
ex_vals = {n: v for n, v in zip(K.X6_N, K.X6_EXACT, strict=True)}
want6 = {1.0: "0.00", 2.0: "0.20", 8.0: "0.52", 10.0: "0.56", 100.0: "0.91", 1000.0: "1.18", 10000.0: "1.40"}
for n, w in want6.items():
    assert f"{ex_vals[n]:.2f}" == w, (n, ex_vals[n])
ap_x = [rd(n, 6) for n, v in zip(K.X6_N, K.X6_APPROX, strict=True) if v is not None]
ap_y = [rd(v) for v in K.X6_APPROX if v is not None]
assert f"{K.PASS_LINE:.2f}" == "0.53"
write("lm33-deflate", {
    "alt": "The deflated benchmark Sharpe ratio a year against the number of trials on a log scale, from 0 at one "
           "trial through 0.52 at eight to 1.40 at 10,000; the approximation lies just above the exact curve, and "
           "the benchmark reaches 0.53, where R2's PSR is 0.95, just past eight trials",
    "height": 300,
    "x": {"type": "log", "fmt": "n2", "tfmt": "n0", "label": "Number of trials (log scale)", "min": 1, "max": 10000,
          "ticks": [1, 10, 100, 1000, 10000], "tickLabels": ["1", "10", "100", "1,000", "10,000"]},
    "y": {"type": "lin", "fmt": "n3", "tfmt": "n2", "label": "Deflated benchmark, a year", "min": 0, "max": 1.5,
          "ticks": [0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5]},
    "series": [{"name": "exact, (33.4)", "color": "1", "x": xn, "y": [rd(v) for v in K.X6_EXACT]},
               {"name": "approximation", "color": "2", "dash": True, "x": ap_x, "y": ap_y}],
    "ann": [{"type": "hline", "y": rd(K.PASS_LINE), "dash": True, "label": "R2's PSR 0.95 at 0.53"},
            {"type": "vline", "x": 8, "dash": True, "label": "n = 8"},
            {"type": "vline", "x": rd(K.neff), "dash": True, "label": "effective 2.07"}],
})

# ---------------------------------------------------------------- X7: Sharpe ratios and haircuts
sr_y = [rd(K.SR[k] * sqA) for k in RULES]
assert (f"{sr_y[1]:.2f}", f"{K.HSR_IND['R2']:.2f}", f"{K.HSR_HOLM['R2']:.2f}") == ("1.14", "0.90", "0.89")
write("lm33-haircut", {
    "type": "bar", "valueLabels": True, "height": 300,
    "alt": "The eight rules' annual Sharpe ratios beside their haircut ratios for eight independent tests and by "
           "Holm: R2 goes from 1.14 to 0.90 and 0.89, R4 to 0.24 with independent tests but keeps 0.63 under Holm",
    "categories": RULES, "x": {"label": ""},
    "y": {"fmt": "n2", "tfmt": "n1", "label": "Sharpe ratio a year", "min": 0, "max": 1.2,
          "ticks": [0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2]},
    "series": [{"name": "Sharpe ratio", "color": "1", "values": sr_y, "fmt": "n2"},
               {"name": "HSR, independent tests", "color": "2", "values": [rd(K.HSR_IND[k]) for k in RULES], "fmt": "n2"},
               {"name": "HSR, Holm", "color": "3", "values": [rd(K.HSR_HOLM[k]) for k in RULES], "fmt": "n2"}],
})

# ---------------------------------------------------------------- widget: minimum track record and DSR
j2 = RULES.index("R2")
sr2, sk2, ku2 = K.SR["R2"], K.mom["R2"][2], K.mom["R2"][3]
ez8 = K.emax(8)
v2 = K.v209(sr2, sk2, ku2)
mt8 = 1 + ((stats.norm.ppf(0.95) * math.sqrt(v2) + ez8) / sr2) ** 2
gx = [0.5 * 40 ** (k / 120) for k in range(121)]
gy = [float(stats.norm.cdf((sr2 * math.sqrt(t * K.Aw - 1) - ez8) / math.sqrt(v2))) for t in gx]
write("lm33-mintrack", {
    "alt": "R2's deflated Sharpe ratio for eight trials against the record's length in years of sessions on a log "
           "scale: it crosses 0.95 at the minimum track record of 7.37 years of sessions",
    "height": 260,
    "x": {"type": "log", "fmt": "n2", "tfmt": "n1", "label": "Record, years of observations (log scale)", "min": 0.5,
          "max": 20, "ticks": [0.5, 1, 2, 5, 10, 20]},
    "y": {"type": "lin", "fmt": "n3", "tfmt": "n2", "label": "DSR", "min": 0, "max": 1, "ticks": [0, 0.25, 0.5, 0.75, 1]},
    "series": [{"name": "DSR, n = 8", "color": "1", "x": [rd(x) for x in gx], "y": [rd(y) for y in gy]}],
    "ann": [{"type": "hline", "y": 0.95, "dash": True, "label": "95%"},
            {"type": "vline", "x": rd(mt8 / K.Aw), "dash": True, "label": "MinTRL"}],
    "widget": {"rules": RULES, "sr": [float(x) for x in K.W_SR], "skew": [float(x) for x in K.W_SKEW],
               "kurt": [float(x) for x in K.W_KURT], "T": [K.T] * 8, "Aw": float(K.Aw), "tau": float(K.tau)},
})

# ---------------------------------------------------------------- the widget's arithmetic in Node against Python
DRIVER = r"""
const vm = require("vm"), fs = require("fs");
const ctx = { window: {}, document: { readyState: "loading", addEventListener() {} }, console };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[1], "utf8"), ctx);
vm.runInContext(fs.readFileSync(process.argv[2], "utf8"), ctx);
const M = ctx.window.Book.widgets.minTrack.math, F = ctx.window.Book.fmt, q = JSON.parse(fs.readFileSync(0, "utf8"));
const ez = {};
q.ns.forEach(n => { ez[n] = M.emax(n); });
const cases = q.cases.map(([sr, sk, ku, n, conf, T]) => ({
  mt: M.mintrl(sr, sk, ku, ez[n], conf), dsr: M.dsr(sr, sk, ku, ez[n], T), psr: M.dsr(sr, sk, ku, 0, T) }));
const ap = q.ns.map(n => M.approx(n));
const init = q.init;
const mt8 = M.mintrl(init.sr, init.sk, init.ku, ez[8], 0.95), mt1 = M.mintrl(init.sr, init.sk, init.ku, 0, 0.95);
process.stdout.write(JSON.stringify({ ez: q.ns.map(n => ez[n]), ap, cases,
  readouts: [F(mt8, "n0"), F(mt8 / init.A, "n2"), F(M.dsr(init.sr, init.sk, init.ku, ez[8], init.T), "n3"),
             F(mt1 / init.A, "n2"), F(ez[8], "n4"), F(M.dsr(init.sr, init.sk, init.ku, 0, init.T), "n3")] }));
"""
node_exe = shutil.which("node")
assert node_exe, "Node is needed to check the widget (it is needed to build the site too)"
NS = [1, 2, 3, 5, 8, 10, 20, 50, 100, 1000]
cases: list[list[float]] = []
for k in RULES:
    j = RULES.index(k)
    for A in (12.0, 52.0, K.Aw):
        sr = K.W_SR[j] * sqA / math.sqrt(A)
        for n in NS:
            for conf in (0.9, 0.95, 0.99):
                cases.append([sr, K.W_SKEW[j], K.W_KURT[j], n, conf, K.tau * A])
init = {"sr": sr2, "sk": sk2, "ku": ku2, "A": K.Aw, "T": K.tau * K.Aw}
out = subprocess.run([node_exe, "-e", DRIVER, str(ROOT / "src" / "assets" / "book.js"), str(ROOT / "src" / "lm33.js")],
                     input=json.dumps({"ns": NS, "cases": cases, "init": init}), capture_output=True, text=True,
                     encoding="utf-8", check=True)
got = json.loads(out.stdout)
ez_py = [K.emax(n) for n in NS]
worst_ez = max(abs(a - b) for a, b in zip(got["ez"], ez_py, strict=True))
assert worst_ez < 1e-6, worst_ez
for n, a in zip(NS, got["ap"], strict=True):
    assert (a is None) == (n == 1) and (a is None or abs(a - K.emax_bldp(n)) < 1e-9), (n, a)
worst_mt = worst_d = 0.0
for (sr, sk, ku, n, conf, T), g in zip(cases, got["cases"], strict=True):
    ez = ez_py[NS.index(int(n))]
    v = K.v209(sr, sk, ku)
    mt = 1 + ((stats.norm.ppf(conf) * math.sqrt(v) + ez) / sr) ** 2
    d = float(stats.norm.cdf((sr * math.sqrt(T - 1) - ez) / math.sqrt(v)))
    p0 = float(stats.norm.cdf(sr * math.sqrt(T - 1) / math.sqrt(v)))
    worst_mt = max(worst_mt, abs(g["mt"] / mt - 1))
    worst_d = max(worst_d, abs(g["dsr"] - d), abs(g["psr"] - p0))
assert worst_mt < 1e-6 and worst_d < 1e-9, (worst_mt, worst_d)
assert got["readouts"] == ["1,796", "7.37", "0.955", "2.15", "1.4236", "0.999"], got["readouts"]
assert abs(K.psr(sr2, ez8 * K.s0, K.T, sk2, ku2) - float(stats.norm.cdf((sr2 * math.sqrt(K.T - 1) - ez8)
                                                                      / math.sqrt(v2)))) < 1e-12
assert np.isclose(K.tau * K.Aw, K.T)
print(f"widget arithmetic against Python over {len(cases)} cases: largest difference in E Z_(n) {worst_ez:.1e}, "
      f"relative in MinTRL {worst_mt:.1e}, in DSR and PSR(0) {worst_d:.1e}; initial readouts "
      f"{', '.join(got['readouts'])}")
