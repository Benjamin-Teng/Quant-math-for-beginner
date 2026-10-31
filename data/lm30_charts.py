"""Chart specs for LM30 (src/data/lm30-*.json), computed from E5's first window, the through case and U28.

Run:  uv run python data/lm30_charts.py
      (after data/vol5_series.py, data/vol5_rules.py and data/vol2_series.py; data/lm30_numbers.py then checks the
      text, these files and the widget block)

Inputs and conventions: data/lm30_common.py (the computations of data/vol5_anchors_lm30.py, same names). Writes
  lm30-scatter     experiment 1's first 1,000 samples: the plug-in exposures to 00646 and 00679B, in percent, with
                   means and covariances estimated and with the covariances alone (Model; simulated, no dates);
  lm30-years       experiment 2: the mean true Sharpe ratio against years of sessions T / A (Model);
  lm30-spectrum    U28's annual eigenvalues: the last 60 returns of the first half, that matrix shrunk with its
                   Ledoit-Wolf c, and the whole first half (price indices; In-sample);
  lm30-chat        Ledoit and Wolf's c_hat at the 92 signals of the through case (R5's windows; In-sample);
  lm30-bl          Black-Litterman exposures on the first window at c = 0, 0.5 and 1, and the plug-in (In-sample);
  lm30-shrinkPath  the widget's initial chart and its "widget" block: per window of U28's first half (30, 60 and 250
                   returns and the whole half) the 28 annual eigenvalues, their eigenvectors and c_hat; the second
                   half's annual matrix; the sector names (derived statistics, no return series and no dates).
No file carries a daily market series in date order (plans/vol-5.md, "Charts", decision X6). The widget's arithmetic
(Book.widgets.shrinkPath.math in src/lm30.js) is run in Node against NumPy and against A30-20's values; the script stops
on a mismatch.
"""
import json
import shutil
import subprocess
from typing import Any

import lm30_common as C
import numpy as np

ROOT = C.HERE.parent
OUT = ROOT / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)


def rd(x: float, n: int = 6) -> float:
    return round(float(x), n)


def sig(x: float, n: int = 10) -> float:
    """x to n significant digits (the widget's eigenvalues span six orders of magnitude)."""
    return float(f"{float(x):.{n}g}")


def write(name: str, spec: dict[str, Any]) -> None:
    assert isinstance(spec.get("alt"), str) and spec["alt"].strip()
    text = json.dumps(spec, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    assert len(text.encode("utf-8")) < 300_000, (name, len(text))
    (OUT / f"{name}.json").write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote src/data/{name}.json ({len(text.encode('utf-8')):,} bytes)")


F5 = C.F5
i646, i679 = F5.index("00646"), F5.index("00679B")

# ---------------------------------------------------------------- X2: experiment 1's plug-in exposures
n_show = 1000
fb = 100 * C.fb_all[:n_show]
fs = 100 * C.fs_all[:n_show]
assert -150 < fb[:, i646].min() and fb[:, i646].max() < 350 and -200 < fb[:, i679].min() and fb[:, i679].max() < 300
truth = (100 * float(C.w_tan[i646]), 100 * float(C.w_tan[i679]))
write("lm30-scatter", {
    "type": "scatter",
    "alt": "Experiment 1, first 1,000 of 10,000 simulated samples of 504 days: plug-in exposures to 00646 and 00679B "
           "in percent. With means and covariances estimated they scatter over hundreds of points (SDs 67.1 and 80.7); "
           "with the covariances alone they stay within a few points of the truth, 62.6 and 37.8 (SDs 4.73 and 4.79)",
    "height": 340,
    "x": {"label": "Exposure to 00646 (%)", "fmt": "n1", "tfmt": "n0", "min": -150, "max": 350,
          "ticks": [-100, 0, 100, 200, 300], "name": "00646"},
    "y": {"label": "Exposure to 00679B (%)", "fmt": "n1", "tfmt": "n0", "min": -200, "max": 300,
          "ticks": [-200, -100, 0, 100, 200, 300], "name": "00679B"},
    "series": [
        {"name": "means and covariances estimated", "color": "1", "r": 2,
         "x": [rd(v, 1) for v in fb[:, i646]], "y": [rd(v, 1) for v in fb[:, i679]]},
        {"name": "covariances only (means known)", "color": "2", "r": 2,
         "x": [rd(v, 1) for v in fs[:, i646]], "y": [rd(v, 1) for v in fs[:, i679]]},
    ],
    "points": [{"at": [rd(truth[0], 1), rd(truth[1], 1)], "label": "truth (62.6, 37.8)", "color": "var(--ink)",
                "r": 5, "dx": 10, "dy": -10}],
})

# ---------------------------------------------------------------- X3: experiment 2 by length
yrs = [T / C.A for T, *_ in C.EXP2]
both = [rd(m, 6) for _, m, _, _, _ in C.EXP2]
covo = [rd(m, 6) for _, _, _, m, _ in C.EXP2]
assert [f"{v:.3f}" for v in both] == ["0.230", "0.322", "0.422", "0.546", "0.672", "0.759", "0.816"]
write("lm30-years", {
    "alt": "Experiment 2: mean true Sharpe ratio of the plug-in portfolio against the sample's length in years of "
           "sessions, log scale. With means and covariances estimated it rises from 0.230 at 0.52 years to 0.816 at "
           "33.2, about equal to equal weights' 0.327 at 1.04 years; with the covariances alone it is 0.8660 already "
           "at 0.52 years, near the best 0.880",
    "height": 300,
    "x": {"type": "log", "fmt": "n2", "label": "Years of sessions T / A (log scale)", "tipLabel": "years: ",
          "values": [rd(v, 5) for v in yrs], "min": 0.5, "max": 35, "ticks": [0.5, 1, 2, 5, 10, 20],
          "tickLabels": ["0.5", "1", "2", "5", "10", "20"]},
    "y": {"type": "lin", "fmt": "n3", "tfmt": "n1", "label": "Mean true Sharpe ratio (annual)", "min": 0, "max": 1,
          "ticks": [0, 0.2, 0.4, 0.6, 0.8, 1.0]},
    "series": [
        {"name": "means and covariances estimated", "color": "1", "y": both},
        {"name": "covariances only", "color": "2", "y": covo},
    ],
    "ann": [{"type": "hline", "y": rd(C.sr_star, 6), "dash": True, "label": "best 0.880"},
            {"type": "hline", "y": rd(C.sr_1n, 6), "dash": True, "label": "equal weights 0.327"}],
})

# ---------------------------------------------------------------- X4: U28's spectrum, sample and shrunk
x60 = C.X1[-60:]
S60 = C.cov0(x60)
c60 = C.c_lw(x60)
ev60 = np.sort(np.linalg.eigvalsh(C.AU * S60))[::-1]
lam60 = float(ev60.mean())
evs60 = c60 * ev60 + (1 - c60) * lam60
evh = np.sort(np.linalg.eigvalsh(C.AU * C.S1))[::-1]
assert f"{ev60[0] / ev60[-1]:.0f}" == "438" and f"{evs60[0] / evs60[-1]:.1f}" == "68.1"
assert f"{evh[0] / evh[-1]:.2f}" == "126.05" and f"{c60:.3f}" == "0.874"
ks = list(range(1, C.NU + 1))
write("lm30-spectrum", {
    "alt": "Annual eigenvalues of U28's covariance matrix, largest first, log scale: the last 60 returns of the first "
           "half (condition number 438), the same matrix shrunk with Ledoit and Wolf's c = 0.874 (68.1), and the whole "
           "first half of 2,191 returns (126.05)",
    "height": 300,
    "x": {"type": "num", "fmt": "n0", "label": "Eigenvalue index k", "tipLabel": "k = ", "min": 1, "max": 28,
          "ticks": [1, 7, 14, 21, 28]},
    "y": {"type": "log", "fmt": "sig3", "tfmt": "sci0", "label": "Annual eigenvalue, log scale", "min": 1e-4,
          "max": 1},
    "series": [
        {"name": "sample, last 60 returns of the first half", "color": "1", "x": ks, "y": [sig(v) for v in ev60]},
        {"name": "shrunk (Ledoit–Wolf, c = 0.874)", "color": "2", "x": ks, "y": [sig(v) for v in evs60]},
        {"name": "sample, whole first half", "color": "3", "x": ks, "y": [sig(v) for v in evh]},
    ],
})

# ---------------------------------------------------------------- X6: c_hat at the 92 signals
sig_dates = [d for d, _, _ in C.sch]
imin = int(np.argmin(C.cs))
assert sig_dates[imin] == "2026-03-31" and f"{C.cs[imin]:.3f}" == "0.781"
write("lm30-chat", {
    "alt": "Ledoit and Wolf's estimate of the data's weight c in R5's 92 windows of 504 daily returns, at each month-end "
           "signal from February 2019 to September 2026: first 0.968, median 0.962, highest 0.979 on 2024-04-30, "
           "lowest 0.781 on 2026-03-31; 19 signals lie below 0.9, the first on 2020-03-31",
    "height": 280,
    "x": {"type": "date", "values": sig_dates},
    "y": {"type": "lin", "fmt": "n3", "tfmt": "n2", "label": "Data's weight c (Ledoit–Wolf)", "min": 0.75, "max": 1.0,
          "ticks": [0.75, 0.8, 0.85, 0.9, 0.95, 1.0]},
    "series": [{"name": "c at each signal", "color": "1", "y": [rd(v, 6) for v in C.cs]}],
    "ann": [{"type": "hline", "y": 0.9, "dash": True},
            {"type": "point", "x": "2026-03-31", "y": rd(float(C.cs[imin]), 6), "color": "2",
             "label": "2026-03-31: 0.781", "anchor": "end", "dx": -8, "dy": 4}],
})

# ---------------------------------------------------------------- X7: Black-Litterman exposures
def f_bl(c: float) -> np.ndarray:
    return C.wref + C.K * c * (C.b - C.kq) / (C.dl * C.KSK)


bl = {c: f_bl(c) for c in (0.0, 0.5, 1.0)}
assert [f"{100 * v:.1f}" for v in bl[0.5]][:2] == ["22.5", "37.5"]
assert [f"{100 * v:.1f}" for v in C.fp] == ["13.6", "72.4", "43.8", "3.0", "-17.1"]
write("lm30-bl", {
    "type": "bar",
    "alt": "Black–Litterman exposures to the five funds on the first window, with one view that 00646 beats 0050: R2's "
           "40/20/30/10/0% at c = 0, 22.5/37.5/30/10/0% at c = 0.5 and 4.9/55.1/30/10/0% at c = 1; the plug-in at the "
           "same risk aversion holds 13.6/72.4/43.8/3.0/−17.1%",
    "height": 300,
    "categories": F5, "x": {"label": "Fund"},
    "y": {"fmt": "pct1", "tfmt": "pct0", "label": "Exposure", "min": -0.2, "max": 0.8,
          "ticks": [-0.2, 0, 0.2, 0.4, 0.6, 0.8]},
    "series": [
        {"name": "R2 (c = 0)", "color": "1", "values": [rd(v) for v in bl[0.0]], "fmt": "pct1"},
        {"name": "c = 0.5", "color": "2", "values": [rd(v) for v in bl[0.5]], "fmt": "pct1"},
        {"name": "c = 1", "color": "3", "values": [rd(v) for v in bl[1.0]], "fmt": "pct1"},
        {"name": "plug-in", "color": "4", "values": [rd(v) for v in C.fp], "fmt": "pct1"},
    ],
    "ann": [{"type": "hline", "y": 0}],
})

# ---------------------------------------------------------------- the widget: shrinkage path on U28's first half
WIN = [(30, "the last 30 returns"), (60, "the last 60 returns"), (250, "the last 250 returns"),
       (C.H, "the whole first half (2,191 returns)")]
S2a = C.AU * C.S2
wins: list[dict[str, Any]] = []
for T, label in WIN:
    x = C.X1[-T:]
    lam, Q = np.linalg.eigh(C.AU * C.cov0(x))
    order = np.argsort(lam)[::-1]
    lam, Q = lam[order], Q[:, order]
    for k in range(C.NU):                      # AUTHORING section 6: the entry largest in absolute value is positive
        j = int(np.argmax(np.abs(Q[:, k])))
        if Q[j, k] < 0:
            Q[:, k] = -Q[:, k]
    wins.append({"T": T, "label": label, "chat": float(C.c_lw(x)), "lam": [sig(v) for v in lam],
                 "q": [[rd(v, 9) for v in Q[:, k]] for k in range(C.NU)]})
widget = {"windows": wins, "S2": [[sig(v) for v in row] for row in S2a], "names": C.s.names,
          "secondHalf": f"{C.s.dates[C.H]} to {C.s.dates[-1]}", "ymin": 1e-6, "ymax": 1, "init": {"win": "1"}}


def py_solve(win: dict[str, Any], c: float) -> tuple[np.ndarray, float, float]:
    lam = np.array(win["lam"])
    Q = np.array(win["q"]).T
    d = c * lam + (1 - c) * lam.mean()
    x = Q @ ((Q.T @ np.ones(len(lam))) / d)
    return x / x.sum(), 1 / x.sum(), float(d[0] / d[-1])


# A30-20's realized volatilities and kappa_c at each window's c_hat, from the stored (rounded) block
want = {30: ("59.8966", "12.45993"), 60: ("68.0635", "12.04281"), 250: ("59.3402", "11.16885"),
        C.H: ("121.3769", "11.78068")}
S2w = np.array(widget["S2"])
for win in wins:
    w, pv, kc = py_solve(win, win["chat"])
    kap, rv = want[win["T"]]
    assert f"{kc:.{len(kap.split('.')[1])}f}" == kap, (win["T"], kc)
    assert f"{100 * np.sqrt(w @ S2w @ w):.5f}" == rv, (win["T"], 100 * np.sqrt(w @ S2w @ w))
w0, _, _ = py_solve(wins[1], 0.0)
assert np.abs(w0 - 1 / C.NU).max() < 1e-7 and f"{100 * np.sqrt(w0 @ S2w @ w0):.2f}" == "15.51"

DRIVER = r"""
const vm = require("vm"), fs = require("fs");
const ctx = { window: {}, document: { readyState: "loading", addEventListener() {} }, console };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[1], "utf8"), ctx);
vm.runInContext(fs.readFileSync(process.argv[2], "utf8"), ctx);
const M = ctx.window.Book.widgets.shrinkPath.math, q = JSON.parse(fs.readFileSync(0, "utf8"));
process.stdout.write(JSON.stringify(q.cases.map(([k, c]) => {
  const r = M.solve(q.W.windows[k], c);
  return [r.w, r.pvar, r.kappa, M.quad(r.w, q.W.S2)];
})));
"""
node = shutil.which("node")
assert node, "Node is needed to check the widget (it is needed to build the site too)"
cases = [[k, c] for k in range(len(wins)) for c in (0.0, 0.25, 0.5, 0.75, 0.99, wins[k]["chat"])]
res = subprocess.run([node, "-e", DRIVER, str(ROOT / "src" / "assets" / "book.js"), str(ROOT / "src" / "lm30.js")],
                     input=json.dumps({"cases": cases, "W": widget}), capture_output=True, text=True,
                     encoding="utf-8", check=True)
got = json.loads(res.stdout)
worst = 0.0
for (k, c), (wj, pvj, kj, rvj) in zip(cases, got, strict=True):
    w, pv, kc = py_solve(wins[int(k)], c)
    worst = max(worst, float(np.abs(np.array(wj) - w).max()), abs(pvj - pv) / pv, abs(kj - kc) / kc,
                abs(rvj - float(w @ S2w @ w)) / float(w @ S2w @ w))
assert worst < 1e-10, worst
print(f"widget arithmetic in Node against NumPy: largest difference {worst:.1e} ({len(cases)} cases)")

w_init = wins[1]
wi, pvi, kci = py_solve(w_init, w_init["chat"])
write("lm30-shrinkPath", {
    "alt": "Annual eigenvalues of U28's sample covariance matrix on the last 60 returns of the first half, largest "
           "first, and of the matrix shrunk with Ledoit and Wolf's c = 0.874, log scale; condition number 438 falls to "
           "68.1",
    "height": 280,
    "x": {"type": "num", "fmt": "n0", "label": "Eigenvalue index k", "tipLabel": "k = ", "min": 1, "max": 28,
          "ticks": [1, 7, 14, 21, 28]},
    "y": {"type": "log", "fmt": "sig3", "tfmt": "sci0", "label": "Annual eigenvalue, log scale", "min": 1e-6, "max": 1},
    "series": [
        {"name": "Sample", "color": "1", "x": ks, "y": w_init["lam"]},
        {"name": "Shrunk", "color": "2", "x": ks,
         "y": [sig(w_init["chat"] * v + (1 - w_init["chat"]) * float(np.mean(w_init["lam"]))) for v in w_init["lam"]]},
    ],
    "widget": widget,
})
print(f"widget initial state: c {w_init['chat']:.3f}, kappa_c {kci:.1f}, realized "
      f"{100 * np.sqrt(wi @ S2w @ wi):.2f}%, predicted {100 * np.sqrt(pvi):.2f}%")
