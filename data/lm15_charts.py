"""Chart specs for LM15 (src/data/lm15-*.json), computed from TR23, the TAIEX total-return index.

Run:  uv run python data/lm15_charts.py      (after data/vol3_series.py; data/lm15_numbers.py checks the text)

Input: data/processed/vol3_taiex.parquet (closes 2003-01-02 .. 2026-10-08 and the simple daily returns R, T = 5,849).
Conventions as in data/lm15_numbers.py: moments divide by T, counts against a threshold use the guard
R <= -x + 1e-12, the normal has the sample mean and standard deviation, the kurtosis fit has nu = 4 + 6 / (excess
kurtosis) with the data's mean and standard deviation, and the maximum-likelihood fit is scipy.stats.t.fit(R).
Writes lm15-binom, lm15-poisson, lm15-qq, lm15-lognormal, lm15-tailchart (with the "widget" block that src/lm15.js
reads) and lm15-loglog.

The widget's own arithmetic (Book.dist in src/assets/book.js and the 1% quantile found by bisection in src/lm15.js) is
checked here against SciPy in Node, as build/qa/test_bookjs_dist.py checks Book.dist; the script stops on a mismatch.
"""
import json
import math
import shutil
import subprocess
from pathlib import Path

import numpy as np
import polars as pl
from numpy.typing import NDArray
from scipy import stats

Vec = NDArray[np.float64]

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)
TR23 = HERE / "processed" / "vol3_taiex.parquet"
EPS = 1e-12

df = pl.read_parquet(TR23).sort("date")
closes: Vec = np.asarray(df["tr"].to_numpy(), dtype=np.float64)
dates_c = [d.isoformat() for d in df["date"].to_list()]
R: Vec = np.asarray(df["R"].to_numpy()[1:], dtype=np.float64)
dates = dates_c[1:]
T = len(R)
assert T == 5849 and dates[0] == "2003-01-03" and dates[-1] == "2026-10-08"
Rbar, s = float(R.mean()), float(R.std())
exk = float(stats.kurtosis(R))
nu_k = 4 + 6 / exk
sc_k = s * math.sqrt((nu_k - 2) / nu_k)
nu_m, loc_m, sc_m = (float(v) for v in stats.t.fit(R))


def r(v: float, n: int) -> float:
    return round(float(v), n)


def write(name: str, spec: dict) -> None:
    (OUT / f"{name}.json").write_text(json.dumps(spec, ensure_ascii=False, separators=(",", ":"), allow_nan=False),
                                      encoding="utf-8", newline="\n")
    print("wrote", f"src/data/{name}.json", f"({(OUT / f'{name}.json').stat().st_size:,} bytes)")


def e_norm(x: float) -> float:
    return T * float(stats.norm.cdf((x - Rbar) / s))


def e_ml(x: float) -> float:
    return T * float(stats.t.cdf(x, nu_m, loc_m, sc_m))


def e_k(x: float) -> float:
    return T * float(stats.t.cdf((x - Rbar) / sc_k, nu_k))


# ------------------------------------------------------------------ binom: up days in 292 blocks of 20
NB = T // 20
up = (R > 0).astype(float)
assert int((R == 0).sum()) == 0
blocks = up[: NB * 20].reshape(NB, 20).sum(axis=1)
p_hat = float(up[: NB * 20].mean())
js = list(range(4, 18))
binom = {
    "type": "bar", "alt": "Number of 20-session blocks by their count of up days, 292 blocks of TAIEX returns, beside "
    "the counts a binomial with p = 3,200/5,840 expects; the two agree closely", "height": 270,
    "categories": [str(j) for j in js], "x": {"label": "Up days in a block of 20 sessions"},
    "y": {"fmt": "n2", "tfmt": "n0", "label": "Blocks (of 292)"},
    "series": [{"name": "Blocks observed", "color": "2", "fmt": "n0",
                "values": [int((blocks == j).sum()) for j in js]},
               {"name": "Binomial, p = 3,200/5,840: expected blocks", "color": "1", "fmt": "n2",
                "values": [r(NB * float(stats.binom.pmf(j, 20, p_hat)), 6) for j in js]}],
}
write("lm15-binom", binom)

# ------------------------------------------------------------------ poisson: months by their number of large moves
months = sorted({d[:7] for d in dates})
big = np.abs(R) >= 0.03 - EPS
mon_idx = np.array([months.index(d[:7]) for d in dates])
cnt_m = np.bincount(mon_idx, weights=big.astype(float), minlength=len(months))
lam = float(cnt_m.mean())
poisson = {
    "type": "bar", "alt": "Number of calendar months by their count of days with a move of 3% or more, 286 months of "
    "TAIEX, beside a Poisson with the same mean: the data have far more calm months and more turbulent ones",
    "height": 270,
    "categories": [str(j) for j in range(9)], "x": {"label": "Days with a move of 3% or more in the month"},
    "y": {"fmt": "n1", "tfmt": "n0", "label": "Months (of 286)"},
    "series": [{"name": "Months observed", "color": "2", "fmt": "n0",
                "values": [int((cnt_m == j).sum()) for j in range(9)]},
               {"name": "Poisson, mean 175/286: expected months", "color": "1", "fmt": "sig4",
                "values": [float(f"{len(months) * float(stats.poisson.pmf(j, lam)):.6g}") for j in range(9)]}],
}
write("lm15-poisson", poisson)

# ------------------------------------------------------------------ qq: TAIEX against the fitted normal
srt = np.sort(R)
pp = (np.arange(1, T + 1) - 0.5) / T
qq = np.asarray(stats.norm.ppf(pp), dtype=np.float64)
zs = (srt - Rbar) / s
# thinned by spacing, so that the points stay apart on the page: rank 1, then each rank at least 0.05 to the right of
# the last plotted point or 0.2 above it; rank 59 (the 1% quantile) and rank T (the best day) are always plotted
keep = [0]
for j in range(1, T):
    if j in (58, T - 1) or qq[j] - qq[keep[-1]] >= 0.05 or zs[j] - zs[keep[-1]] >= 0.2:
        keep.append(j)
sel = np.zeros(T, dtype=bool)
sel[keep] = True
assert int(sel.sum()) == 130 and sel[58]
qq_spec = {
    "type": "scatter", "alt": "QQ plot of TAIEX's 5,849 daily returns against the fitted normal: the points follow the "
    "45-degree line in the middle and bend away from it in both tails, down to 7 April 2025 and up to 10 April 2025",
    "height": 370, "equal": False,
    "x": {"label": "Normal quantile", "fmt": "n3", "tfmt": "n0", "name": "normal quantile", "min": -4.2, "max": 4.2},
    "y": {"label": "Standardized return (R − mean) / s", "fmt": "n3", "tfmt": "n0", "name": "standardized return",
          "min": -8.6, "max": 8.2},
    "series": [{"name": "TAIEX daily returns (130 of 5,849 plotted)", "color": "1", "r": 2.2,
                "x": [r(v, 4) for v in qq[sel]], "y": [r(v, 4) for v in zs[sel]]}],
    "lines": [{"from": [-4, -4], "to": [4, 4], "extend": True, "color": "var(--muted)", "label": "line y = x"}],
    "points": [{"at": [r(qq[0], 3), r(zs[0], 3)], "label": "7 Apr 2025", "color": "2", "dx": 8, "dy": 4},
               {"at": [r(qq[-1], 3), r(zs[-1], 3)], "label": "10 Apr 2025", "color": "2", "anchor": "end",
                "dx": -8, "dy": 4},
               {"at": [r(qq[58], 3), r(zs[58], 3)], "label": "rank 59: 1% quantile", "color": "3", "r": 3.5,
                "dx": 8, "dy": 12}],
}
write("lm15-qq", qq_spec)

# ------------------------------------------------------------------ lognormal: 23 calendar-year growth factors
last: dict[int, float] = {}
for d, c in zip(dates_c, closes, strict=True):
    last[int(d[:4])] = float(c)
yrs = list(range(2003, 2026))
G = np.array([last[y] / (float(closes[0]) if y == 2003 else last[y - 1]) for y in yrs])
muX, sX = float(np.log(G).mean()), float(np.log(G).std())
gx = [r(0.5 + 0.005 * k, 3) for k in range(281)]
gs = np.sort(G)
lognormal = {
    "alt": "Distribution function of a lognormal fitted to TAIEX's 23 calendar-year growth factors, 2003 to 2025, with "
    "the step function of the 23 factors themselves; the model's median 1.1235 and mean 1.1516 are marked",
    "height": 280,
    "x": {"type": "num", "fmt": "n4", "tfmt": "n1", "label": "Growth factor G of a calendar year", "tipLabel": "G = ",
          "min": 0.5, "max": 1.9},
    "y": {"type": "lin", "fmt": "n3", "tfmt": "n1", "label": "Cumulative probability, Pr(G ≤ y)", "min": 0, "max": 1},
    "series": [{"name": "Lognormal, μ_X = 0.11646, σ_X = 0.22207", "color": "1",
                "x": gx, "y": [r(float(stats.norm.cdf((math.log(g) - muX) / sX)), 6) for g in gx]},
               {"name": "TAIEX, 23 calendar years", "color": "2", "step": True,
                "x": [0.5, *[r(g, 6) for g in gs], 1.9],
                "y": [0.0, *[r((i + 1) / 23, 6) for i in range(23)], 1.0]}],
    "ann": [{"type": "vline", "x": r(math.exp(muX), 4), "label": "median 1.1235", "anchor": "end", "dash": True},
            {"type": "vline", "x": r(math.exp(muX + sX**2 / 2), 4), "label": "mean 1.1516", "dy": 14, "dash": True}],
}
write("lm15-lognormal", lognormal)

# ------------------------------------------------------------------ tailchart: days with R <= x, and the widget block
FLOOR = 1e-3
xs = [r(-0.105 + k * 0.0005, 4) for k in range(round((0.105 - 0.010) / 0.0005) + 1)]
x_floor = r(Rbar + s * float(stats.norm.ppf(FLOOR / T)), 6)
nx = sorted({*xs, x_floor})
ny = [FLOOR if x == x_floor else (r(e_norm(x), 6) if e_norm(x) >= FLOOR else None) for x in nx]
low = srt[srt <= -0.010 + EPS]
emp_x = [r(v, 10) for v in low] + [-0.010]
emp_y = [k + 1 for k in range(len(low))] + [len(low)]
assert len(low) == int((R <= -0.01 + EPS).sum())
edges = np.round(np.arange(-0.1075, 0.1076, 0.005), 4)
counts, _ = np.histogram(R, bins=edges)
assert int(counts.sum()) == T
lower = [r(v, 10) for v in srt[srt <= -0.0095 + EPS]]
q01_emp = float(srt[math.ceil(0.01 * T) - 1])
check_nus = [2.05, 2.5, nu_m, 4.0, nu_k, 10.0, 30.0]
tailchart = {
    "alt": "Number of TAIEX days at or below each return from -10.5% to -1%, against the expected days of "
    "the fitted normal and of two Student-t fits, log scale",
    "height": 300,
    "x": {"type": "num", "fmt": "pct2", "tfmt": "pct0", "label": "Daily total return", "tipLabel": "R ≤ ",
          "min": -0.105, "max": -0.010},
    "y": {"type": "log", "fmt": "sig3", "tfmt": "num", "label": "Days at or below this return, of 5,849 (log scale)", "min": FLOOR,
          "max": 1000, "ticks": [0.001, 0.01, 0.1, 1, 10, 100, 1000]},
    "series": [{"name": "TAIEX (actual days)", "color": "2", "step": True, "fmt": "n0", "x": emp_x, "y": emp_y},
               {"name": "Normal (expected)", "color": "1", "x": nx, "y": ny},
               {"name": "Student-t, maximum likelihood, ν = 3.065", "color": "3", "x": xs,
                "y": [r(e_ml(x), 6) for x in xs]},
               {"name": "Student-t, kurtosis fit, ν = 5.139", "color": "4", "dash": True, "x": xs,
                "y": [r(e_k(x), 6) for x in xs]}],
    "ann": [{"type": "vline", "x": -0.05, "label": "x = −5%", "anchor": "start", "dash": True},
            {"type": "hline", "y": 1, "label": "1 day", "dash": True}],
    "widget": {
        "T": T, "first": dates[0], "last": dates[-1], "Rbar": r(Rbar, 12), "s": r(s, 12),
        "ml": {"nu": r(nu_m, 9), "loc": r(loc_m, 12), "scale": r(sc_m, 12)}, "nuK": r(nu_k, 9),
        "bin": 0.005, "edges0": float(edges[0]), "counts": [int(c) for c in counts], "lower": lower,
        "q01": r(q01_emp, 10),
        # SciPy's values for the initial state and the 1% quantile of t at several nu: the widget compares its own
        "check": {"x": 0.05, "normDays": r(e_norm(-0.05), 9), "mlDays": r(e_ml(-0.05), 9),
                  "kDays": r(e_k(-0.05), 9), "mlQ01": r(float(stats.t.ppf(0.01, nu_m, loc_m, sc_m)), 12),
                  "tq01": [[r(v, 9), r(float(stats.t.ppf(0.01, r(v, 9))), 12)] for v in check_nus]},
    },
}
write("lm15-tailchart", tailchart)

# ------------------------------------------------------------------ loglog: days with R <= -x on log-log axes
pcts = [1, 2, 3, 5, 7, 10]
lg = [r(k / 200, 4) for k in range(201)]                   # log10 of x in %, from 0 (1%) to 1 (10%)
xl = [10 ** v / 100 for v in lg]
losses = np.sort(-R[R <= -0.01 + EPS])                       # loss levels at or above 1%, ascending
n1 = len(losses)
ll_x = [0.0] + [r(math.log10(100 * v), 6) for v in losses]
ll_y = [n1] + [n1 - (i + 1) for i in range(n1)]
ll_y = [v if v > 0 else None for v in ll_y]
x_fl = -x_floor
lg_n = sorted({*lg, r(math.log10(100 * x_fl), 6)})
nl = []
for v in lg_n:
    x = 10 ** v / 100
    e = e_norm(-x)
    nl.append(FLOOR if abs(x - x_fl) < 1e-9 else (r(e, 6) if e >= FLOOR else None))
c3 = int((R <= -0.03 + EPS).sum())
assert c3 == 108
loglog = {
    "alt": "Days with a return at or below -x against x from 1% to 10%, both axes logarithmic: TAIEX steepens with the "
    "loss level, the Student-t fit runs almost straight, the normal falls away, and a dashed line of slope -3 passes "
    "through 108 days at 3%",
    "height": 300,
    "x": {"type": "num", "fmt": "n3", "label": "Loss level x (log scale)", "tipLabel": "log10 of x in % = ",
          "min": 0, "max": 1, "ticks": [r(math.log10(p), 6) for p in pcts], "tickLabels": [f"{p}%" for p in pcts]},
    "y": {"type": "log", "fmt": "sig3", "tfmt": "num", "label": "Days with R ≤ −x, of 5,849 (log scale)", "min": FLOOR,
          "max": 5000, "ticks": [0.001, 0.01, 0.1, 1, 10, 100, 1000]},
    "series": [{"name": "TAIEX (actual days)", "color": "2", "step": True, "fmt": "n0", "x": ll_x, "y": ll_y},
               {"name": "Normal (expected)", "color": "1", "x": lg_n, "y": nl},
               {"name": "Student-t, maximum likelihood", "color": "3", "x": lg, "y": [r(e_ml(-x), 6) for x in xl]},
               {"name": "Slope −3 through 108 days at 3%", "color": "4", "dash": True, "x": lg,
                "y": [r(c3 * (x / 0.03) ** -3, 6) for x in xl]}],
}
write("lm15-loglog", loglog)

# ------------------------------------------------------------------ the widget's arithmetic in Node against SciPy
DRIVER = r"""
const vm = require("vm"), fs = require("fs");
const ctx = { window: {}, document: { readyState: "loading", addEventListener() {} }, console };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[1], "utf8"), ctx);
vm.runInContext(fs.readFileSync(process.argv[2], "utf8"), ctx);
const M = ctx.window.Book.widgets.tdist.math, q = JSON.parse(fs.readFileSync(0, "utf8"));
process.stdout.write(JSON.stringify({
  tq: q.nus.map(nu => M.tq(0.01, nu)),
  days: q.cases.map(([nu, loc, sc, x]) => M.tDays(-x, nu, loc, sc, q.T)),
  norm: q.norm.map(([x]) => M.normDays(-x, q.mu, q.sd, q.T))
}));
"""
node = shutil.which("node")
assert node, "Node is needed to check the widget (it is needed to build the site too)"
nus = [0.5 + 0.25 * k for k in range(7, 120)] + [nu_m, nu_k]
cases = [[nu_m, loc_m, sc_m, x / 100] for x in (1, 2, 3, 5, 7, 10)] + \
        [[nu, Rbar, s * math.sqrt((nu - 2) / nu), 0.05] for nu in (2.05, 3, 5.14, 30)]
out = subprocess.run([node, "-e", DRIVER, str(ROOT / "src" / "assets" / "book.js"), str(ROOT / "src" / "lm15.js")],
                     input=json.dumps({"nus": nus, "cases": cases, "norm": [[0.02], [0.05], [0.1]], "T": T,
                                       "mu": Rbar, "sd": s}),
                     capture_output=True, text=True, encoding="utf-8", check=True)
got = json.loads(out.stdout)
worst = 0.0
for nu, g in zip(nus, got["tq"], strict=True):
    ref = float(stats.t.ppf(0.01, nu))
    worst = max(worst, abs(g - ref) / abs(ref))
for (nu, loc, sc, x), g in zip(cases, got["days"], strict=True):
    ref = T * float(stats.t.cdf((-x - loc) / sc, nu))
    worst = max(worst, abs(g - ref) / ref)
for (x,), g in zip([[0.02], [0.05], [0.1]], got["norm"], strict=True):
    ref = e_norm(-x)
    worst = max(worst, abs(g - ref) / ref)
assert worst < 1e-8, worst
print(f"widget arithmetic against SciPy: largest relative error {worst:.1e} "
      f"({len(nus)} quantiles, {len(cases) + 3} expected counts)")
