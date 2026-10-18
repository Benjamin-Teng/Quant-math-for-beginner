"""Chart specs for LM17 (src/data/lm17-*.json), computed from TR23.

Run:  uv run python data/lm17_charts.py      (after data/vol3_series.py; data/lm17_numbers.py checks the text)

Input: data/processed/vol3_taiex.parquet only (TR23, the TAIEX total-return index from FinMind's
TaiwanStockTotalReturnIndex). Same conventions as data/lm17_numbers.py: T = 5,849 simple daily returns from
2003-01-03, log returns for sums, moments with divisor T, A = T / years (calendar days / 365.25).
Writes lm17-case, lm17-upfreq, lm17-leverage, lm17-binom, lm17-kurtm, lm17-runkurt and lm17-wealth (the line chart
that the widget "wealth" starts from, with the grid of gbar(f) and s_r(f) in its "widget" block).
"""
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl
from numpy.typing import NDArray
from scipy import optimize, stats

Vec = NDArray[np.float64]

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)
EPS = 1e-12

df = pl.read_parquet(HERE / "processed" / "vol3_taiex.parquet").sort("date")
dates_all = [str(d) for d in df["date"].to_list()]
tr = df["tr"].to_numpy().astype(np.float64)
R = df["R"].to_numpy()[1:].astype(np.float64)
dates = dates_all[1:]
T = len(R)
r = np.log1p(R)
years = (df["date"][-1] - df["date"][0]).days / 365.25
A = T / years
Rb, rb, sr = float(R.mean()), float(r.mean()), float(r.std())
assert T == 5849 and abs(A - 246.122955) < 1e-6
Z95 = float(stats.norm.ppf(0.95))


def rd(v: float, n: int) -> float:
    return round(float(v), n)


def write(name: str, spec: dict[str, Any]) -> None:
    assert isinstance(spec.get("alt"), str) and spec["alt"].strip()
    (OUT / f"{name}.json").write_text(json.dumps(spec, ensure_ascii=False, separators=(",", ":"), allow_nan=False),
                                      encoding="utf-8", newline="\n")
    print("wrote", f"src/data/{name}.json")


def gbar(f: float) -> float:
    return float(np.log1p(f * R).mean())


def sdl(f: float) -> float:
    return float(np.log1p(f * R).std())


# ------------------------------------------------------------------ case: wealth, mean path, median path (log scale)
t_idx = np.arange(len(tr))
W = tr / tr[0]
mean_path = (1 + Rb) ** t_idx
median_path = np.exp(t_idx * rb)
keep = sorted(set(range(0, len(tr), 5)) | {len(tr) - 1, int(W.argmin()), int(W.argmax())})
keep_m = sorted(set(range(0, len(tr), 25)) | {len(tr) - 1})   # the model paths are smooth
case = {
    "alt": "TAIEX total-return wealth from January 2003 to October 2026 on a log scale, with the mean path of the "
           "average day compounded, which ends at 38.66, and the median path, which ends with the index at 25.20",
    "height": 320,
    "x": {"type": "date"},
    "y": {"type": "log", "fmt": "x2", "tfmt": "x0", "label": "Growth of 1 unit (log scale)", "min": 0.6, "max": 45,
          "ticks": [1, 2, 5, 10, 20, 40]},
    "series": [
        {"name": "TAIEX total return", "endLabel": "TAIEX", "color": "1",
         "x": [dates_all[i] for i in keep], "y": [rd(W[i], 4) for i in keep]},
        {"name": "Mean path: average day compounded", "endLabel": "Mean", "color": "2", "dash": True,
         "x": [dates_all[i] for i in keep_m], "y": [rd(mean_path[i], 4) for i in keep_m]},
        {"name": "Median path: mean log return", "endLabel": "Median", "color": "3", "dash": True,
         "x": [dates_all[i] for i in keep_m], "y": [rd(median_path[i], 4) for i in keep_m]},
    ],
    "endLabels": True, "endValue": True, "endMargin": 140,
}
assert (f"{W[-1]:.2f}", f"{mean_path[-1]:.2f}", f"{median_path[-1]:.2f}") == ("25.20", "38.66", "25.20")
write("lm17-case", case)

# ------------------------------------------------------------------ upfreq: running share of up days, log n axis
n_all = np.arange(1, T + 1)
run_up = np.cumsum(R > EPS) / n_all
p_hat = float(run_up[-1])
ns = sorted({round(20 * 1.006**k) for k in range(1000)} | {246, 1231, T})
ns = [n for n in ns if 20 <= n <= T]
half = [2 * math.sqrt(p_hat * (1 - p_hat) / n) for n in ns]
tick_n = [20, 50, 100, 250, 1000, 2500, T]
upfreq = {
    "alt": "Running share of TAIEX up days among the first n daily returns, n from 20 to 5,849 on a logarithmic axis, "
           "settling near 0.548 inside a band of two model standard errors that narrows as n grows",
    "height": 300,
    "x": {"type": "num", "fmt": "n3", "label": "Number of daily returns n (log scale)", "tipLabel": "log10 of n = ",
          "min": rd(math.log10(20), 4), "max": rd(math.log10(T), 4),
          "ticks": [rd(math.log10(v), 6) for v in tick_n], "tickLabels": [f"{v:,}" for v in tick_n]},
    "y": {"type": "lin", "fmt": "n4", "tfmt": "n2", "label": "Share of up days", "min": 0.40, "max": 0.65,
          "ticks": [0.40, 0.45, 0.50, 0.55, 0.60, 0.65]},
    "series": [
        {"name": "iid model band: whole-sample share ± 2 standard errors", "color": "2",
         "x": [rd(math.log10(n), 5) for n in ns], "lo": [rd(p_hat - h, 5) for h in half],
         "hi": [rd(p_hat + h, 5) for h in half]},
        {"name": "Running share of up days", "color": "1",
         "x": [rd(math.log10(n), 5) for n in ns], "y": [rd(run_up[n - 1], 5) for n in ns]},
    ],
    "ann": [{"type": "hline", "y": rd(p_hat, 5), "dash": True, "label": f"whole sample {p_hat:.4f}"}],
}
assert [f"{run_up[n - 1]:.4f}" for n in (246, 1231)] == ["0.5163", "0.5378"]
write("lm17-upfreq", upfreq)

# ------------------------------------------------------------------ leverage: annual log growth against f
i_min = int(R.argmin())
fmax = 1 / abs(float(R[i_min]))
fstar = float(optimize.brentq(lambda f: float((R / (1 + f * R)).mean()), 0.0, fmax - 1e-6))
fzero = float(optimize.brentq(gbar, fstar, fmax - 1e-9))
fs = sorted(set(np.round(np.arange(0, 10.30 + 1e-9, 0.02), 2).tolist()) | {1.0, round(fstar, 4), round(fzero, 4), 10.305, 10.309, 10.3095, 10.30958})
real, meanp = [], []
for f in fs:
    v = A * gbar(f)
    real.append(rd(v, 5) if v >= -1.2 else None)
    meanp.append(rd(A * math.log(1 + f * Rb), 5))
leverage = {
    "alt": "Annual log growth of TAIEX total return at constant leverage f from 0 to 10.31: the realized curve peaks at "
           "32.28% at f = 4.14 and crosses zero at 8.04, while the mean path's rate rises with every f",
    "height": 320,
    "x": {"type": "num", "fmt": "n2", "tfmt": "n0", "label": "Leverage f", "tipLabel": "f = ", "min": 0, "max": 10.4,
          "ticks": [0, 2, 4, 6, 8, 10]},
    "y": {"type": "lin", "fmt": "pct2", "tfmt": "pct0", "label": "Annual log growth (A = 246.12)", "min": -1.0,
          "max": 1.6, "ticks": [-1.0, -0.5, 0, 0.5, 1.0, 1.5]},
    "series": [
        {"name": "Realized: A × mean of ln(1 + f R)", "color": "1", "x": fs, "y": real},
        {"name": "Mean path: A × ln(1 + f × average day)", "color": "2", "dash": True, "x": fs, "y": meanp},
    ],
    "ann": [
        {"type": "point", "x": 1, "y": rd(A * gbar(1), 5), "label": "f = 1: 13.58%", "color": "1", "dx": 8, "dy": 34},
        {"type": "point", "x": 1, "y": rd(A * math.log(1 + Rb), 5), "label": "15.38%", "color": "2", "dx": -8, "dy": -8,
         "anchor": "end"},
        {"type": "point", "x": rd(fstar, 4), "y": rd(A * gbar(fstar), 5), "label": "f* = 4.14: 32.28%", "color": "1",
         "dx": 8, "dy": 18},
        {"type": "point", "x": rd(fzero, 4), "y": 0, "label": "zero growth at 8.04", "color": "1", "dx": -8, "dy": 18,
         "anchor": "end"},
        {"type": "vline", "x": rd(fmax, 4), "dash": True, "label": "ruin at 10.31", "anchor": "end", "dy": 100},
    ],
}
assert f"{fstar:.2f}" == "4.14" and f"{fzero:.2f}" == "8.04" and f"{fmax:.2f}" == "10.31"
write("lm17-leverage", leverage)

# ------------------------------------------------------------------ binom: Bin(100, 1/2) and the normal density
js = list(range(25, 76))
pmf = [float(stats.binom.pmf(j, 100, 0.5)) for j in js]
edges = [j - 0.5 for j in js] + [75.5]
xs = [rd(25 + 0.25 * k, 2) for k in range(201)]
binom = {
    "alt": "Probabilities of 25 to 75 wins in 100 trades of a fair bet, drawn as a histogram, with the normal density of "
           "mean 50 and standard deviation 5; the region of 41 or fewer wins, where the full-Kelly bettor is behind, "
           "is shaded",
    "height": 300,
    "x": {"type": "num", "fmt": "n1", "tfmt": "n0", "label": "Wins j in 100 trades", "tipLabel": "x = ", "min": 25,
          "max": 75, "ticks": [25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75]},
    "y": {"type": "lin", "fmt": "n4", "tfmt": "n2", "label": "Probability (bars) and density", "min": 0, "max": 0.09,
          "ticks": [0, 0.02, 0.04, 0.06, 0.08]},
    "series": [
        {"name": "Bin(100, 1/2), Pr(j)", "color": "1", "step": True, "x": edges, "y": [rd(v, 6) for v in pmf] + [rd(pmf[-1], 6)]},
        {"name": "Normal density, mean 50, sd 5", "color": "2", "x": xs,
         "y": [rd(float(stats.norm.pdf((x - 50) / 5)) / 5, 6) for x in xs]},
    ],
    "ann": [{"type": "band", "x0": 25, "x1": 41.5},
            {"type": "vline", "x": 41.5, "dash": True, "label": "j ≤ 41: loss at f* = 25", "anchor": "end"}],
}
write("lm17-binom", binom)

# ------------------------------------------------------------------ kurtm: kurtosis of m-day sums against iid


def kurt_ex(x: Vec) -> float:
    xc = x - x.mean()
    return float((xc**4).mean() / (xc**2).mean() ** 2 - 3)


def window_sums(x: Vec, m: int) -> Vec:
    c = np.concatenate([[0.0], np.cumsum(x)])
    return c[m:] - c[:-m]


ms = [1, 2, 5, 10, 20, 60]
km = [kurt_ex(window_sums(r, m)) for m in ms]
kurtm = {
    "type": "bar",
    "alt": "Excess kurtosis of TAIEX log-return sums over 1, 2, 5, 10, 20 and 60 days, overlapping windows, against "
           "the iid prediction 5.428 divided by m: the data fall from 5.43 to 2.29 at 20 days and 3.20 at 60, the "
           "prediction to 0.27 and 0.090",
    "height": 300, "valueLabels": True,
    "categories": [str(m) for m in ms], "x": {"label": "Days in each sum, m"},
    "y": {"fmt": "n2", "tfmt": "n0", "label": "Excess kurtosis", "min": 0, "max": 6, "ticks": [0, 1, 2, 3, 4, 5, 6]},
    "series": [
        {"name": "TAIEX, overlapping sums of m daily log returns", "color": "1", "fmt": "n2",
         "values": [rd(v, 4) for v in km]},
        {"name": "iid sums: 5.428 / m", "color": "2", "fmt": "n3", "values": [rd(5.428 / m, 5) for m in ms]},
    ],
}
assert [f"{v:.2f}" for v in km] == ["5.43", "5.04", "3.63", "3.02", "2.29", "3.20"]
write("lm17-kurtm", kurtm)

# ------------------------------------------------------------------ runkurt: running excess kurtosis of R
c1, c2, c3, c4 = (np.cumsum(R**k) for k in (1, 2, 3, 4))
mu = c1 / n_all
m2 = c2 / n_all - mu**2
m4 = c4 / n_all - 4 * mu * c3 / n_all + 6 * mu**2 * c2 / n_all - 3 * mu**4
with np.errstate(divide="ignore", invalid="ignore"):   # the first day has no variance
    k_run = m4 / m2**2 - 3
i0 = 245
i_apr2, i_apr7 = dates.index("2025-04-02"), dates.index("2025-04-07")
for i in (i0, i_apr2, i_apr7, T - 1):
    xc = R[: i + 1] - R[: i + 1].mean()
    assert abs(k_run[i] - ((xc**4).mean() / (xc**2).mean() ** 2 - 3)) < 1e-8
keep_k = sorted(set(range(i0, T, 5)) | {i0, i_apr2, i_apr7, T - 1, i0 + int(k_run[i0:].argmax()), i0 + int(k_run[i0:].argmin())})
runkurt = {
    "alt": "Running excess kurtosis of TAIEX daily total returns from the end of 2003 to October 2026: it climbs in "
           "jumps on extreme days, from 4.25 to 4.94 on 7 April 2025, and ends at 5.27",
    "height": 300,
    "x": {"type": "date"},
    "y": {"type": "lin", "fmt": "n2", "tfmt": "n0", "label": "Excess kurtosis of daily returns so far", "min": 0,
          "max": 6, "ticks": [0, 1, 2, 3, 4, 5, 6]},
    "series": [{"name": "Running excess kurtosis", "color": "1", "x": [dates[i] for i in keep_k],
                "y": [rd(k_run[i], 4) for i in keep_k]}],
    "ann": [{"type": "hline", "y": rd(k_run[-1], 4), "dash": True, "label": "full sample 5.27"},
            {"type": "point", "x": "2025-04-02", "y": rd(k_run[i_apr2], 4), "label": "4.25 (2 Apr 2025)", "color": "2",
             "anchor": "end", "dx": -8, "dy": 26},
            {"type": "point", "x": "2025-04-07", "y": rd(k_run[i_apr7], 4), "label": "4.94 (7 Apr 2025)", "color": "2",
             "anchor": "end", "dx": -8, "dy": 4}],
}
assert (f"{k_run[i_apr2]:.2f}", f"{k_run[i_apr7]:.2f}", f"{k_run[-1]:.2f}") == ("4.25", "4.94", "5.27")
write("lm17-runkurt", runkurt)

# ------------------------------------------------------------------ wealth: the widget's initial chart and its grid
grid_f = [round(0.25 * k, 2) for k in range(1, 33)]
grid = [[f, rd(gbar(f), 10), rd(sdl(f), 10)] for f in grid_f]
assert f"{grid[3][1]:.8f}, {grid[3][2]:.8f}" == "0.00055170, 0.01210727"
assert f"{grid[7][1]:.8f}, {grid[7][2]:.8f}" == "0.00095571, 0.02428841"
m_max = round(40 * A)
m0 = T
ms_w = sorted(set(np.linspace(0, m_max, 241).round().astype(int).tolist()) | {m0})
x_years = [rd(m / A, 4) for m in ms_w]
f0, g0, s0 = 1.0, gbar(1.0), sdl(1.0)


def clip(v: float) -> float | None:
    return rd(v, 8) if 1e-3 <= v <= 1e7 else None


wealth = {
    "alt": "Wealth of one unit invested in the iid model of TAIEX total-return days at leverage 1 over 0 to 40 years: "
           "the mean path, the median path and the band from the 5% to the 95% quantile on a log scale, with the "
           "horizon of 5,849 sessions marked",
    "height": 320,
    "x": {"type": "num", "fmt": "n2", "tfmt": "n0", "label": "Horizon in years (m / A sessions)", "tipLabel": "years: ",
          "min": 0, "max": 40, "ticks": [0, 5, 10, 15, 20, 25, 30, 35, 40]},
    "y": {"type": "log", "fmt": "sig4", "tfmt": "sci0", "label": "Wealth per unit invested (log scale)", "min": 0.01,
          "max": 1e6, "ticks": [0.01, 1, 100, 1e4, 1e6]},
    "series": [
        {"name": "5% to 95% quantile", "color": "3", "x": x_years,
         "lo": [clip(math.exp(m * g0 - Z95 * s0 * math.sqrt(m))) for m in ms_w],
         "hi": [clip(math.exp(m * g0 + Z95 * s0 * math.sqrt(m))) for m in ms_w]},
        {"name": "Mean path", "color": "2", "dash": True, "x": x_years, "y": [clip((1 + f0 * Rb) ** m) for m in ms_w]},
        {"name": "Median path", "color": "1", "x": x_years, "y": [clip(math.exp(m * g0)) for m in ms_w]},
    ],
    "ann": [{"type": "hline", "y": 1}, {"type": "vline", "x": rd(m0 / A, 4), "dash": True, "label": "23.76 years"}],
    "widget": {
        "Rbar": rd(Rb, 12), "A": rd(A, 6), "T": T, "z95": rd(Z95, 7), "mMax": m_max, "init": {"f": 1, "m": m0},
        "grid": grid,
        "check": {"f1": {"lognormal": rd(math.exp(T * (gbar(1) + sdl(1) ** 2 / 2)), 4), "iid": rd((1 + Rb) ** T, 4)},
                  "f8": {"lognormal": float(f"{math.exp(T * (gbar(8) + sdl(8) ** 2 / 2)):.4e}"),
                         "iid": float(f"{(1 + 8 * Rb) ** T:.4e}")}},
    },
}
row_t = (math.exp(T * g0), (1 + Rb) ** T, math.exp(T * g0 - Z95 * s0 * math.sqrt(T)), math.exp(T * g0 + Z95 * s0 * math.sqrt(T)))
assert [f"{v:.2f}" for v in row_t[:3]] + [f"{row_t[3]:.1f}"] == ["25.20", "38.66", "5.49", "115.6"]
assert f"{100 * stats.norm.cdf(-g0 * math.sqrt(1231) / s0):.2f}" == "5.49" and m_max == 9845
write("lm17-wealth", wealth)
