"""Chart data for LM7 (src/data/lm07-*.json), computed from the verified 0050 / 00679B series.

Run after lm07_series.py and lm07_stats.py:  uv run python data/lm07_charts.py
"""
import json
import math
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import polars as pl


def ms(d):
    """Date string -> epoch milliseconds: book.js converts series dates itself, but not annotation dates."""
    return int(datetime.fromisoformat(d).replace(tzinfo=UTC).timestamp() * 1000)

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)
st = json.loads((HERE / "processed" / "lm07_stats.json").read_text(encoding="utf-8"))
df = pl.read_parquet(HERE / "processed" / "lm07_returns.parquet").sort("date")   # first row = base date (no return)
dates = df["date"].to_list()
R1 = df["R_0050"].to_numpy()[1:]
R2 = df["R_00679B"].to_numpy()[1:]
A = st["sample"]["A"]
IS, OOS, F = st["is"], st["oos"], st["full"]

# ---------------------------------------------------------------- rolling one-year correlation
WIN = 243
rc: list[float | None] = [None] * len(R1)
for i in range(WIN - 1, len(R1)):
    rc[i] = float(np.corrcoef(R1[i - WIN + 1:i + 1], R2[i - WIN + 1:i + 1])[0, 1])
roll = {i: v for i, v in enumerate(rc) if v is not None}     # defined values only
d_ret = dates[1:]
idx = [i for i in range(WIN - 1, len(R1), 5)]
if idx[-1] != len(R1) - 1: idx.append(len(R1) - 1)
# keep the extremes the text quotes in the thinned series: overall, and for windows ending from 2023 on
valid = [i for i in range(len(rc)) if rc[i] is not None]
late_i = [i for i in valid if d_ret[i] >= "2023-01-01"]
for grp in (valid, late_i):
    idx += [min(grp, key=lambda i: roll[i]), max(grp, key=lambda i: roll[i])]
idx = sorted(set(idx))
first_d, last_d = d_ret[idx[0]], d_ret[idx[-1]]
rollcorr = {"alt": "Trailing one-year correlation of daily returns, 0050 and 00679B, 2018 to 2026", "height": 300,
            "x": {"type": "date"}, "y": {"type": "lin", "fmt": "n2", "label": "Correlation of daily returns, trailing 243 trading days", "min": -0.7, "max": 0.4},
            "series": [{"name": "Trailing 243-day correlation", "color": "1", "x": [d_ret[i] for i in idx], "y": [round(roll[i], 4) for i in idx]},
                       {"name": "Full-window correlation (2017–2021, 2022–2026)", "color": "2", "dash": True,
                        "x": [first_d, "2021-12-30", "2021-12-31", "2022-01-03", last_d],
                        "y": [round(IS["rho"], 4), round(IS["rho"], 4), None, round(OOS["rho"], 4), round(OOS["rho"], 4)]}],
            "ann": [{"type": "band", "x0": ms("2022-01-01"), "x1": ms("2022-12-31")}]}

# ---------------------------------------------------------------- volatility curves in and out of sample
ws = [round(k / 100, 2) for k in range(101)]
def vcurve(e):
    return [round(math.sqrt(w * w * e["s1"] ** 2 + (1 - w) ** 2 * e["s2"] ** 2 + 2 * w * (1 - w) * e["cov"]), 5) for w in ws]
wis = st["case"]["w_is"]
volcurve = {"alt": "Portfolio volatility against the weight in 0050, estimated in and out of sample", "height": 320,
            "x": {"type": "num", "fmt": "pct0", "label": "Weight in 0050 (rest in 00679B)", "tipLabel": "w = ", "min": 0, "max": 1},
            "y": {"type": "lin", "fmt": "pct2", "tfmt": "pct0", "label": "Annualized volatility of the mix", "min": 0.08, "max": 0.24},
            "series": [{"name": "Estimated on 2017–2021", "color": "1", "x": ws, "y": vcurve(IS)},
                       {"name": "Realized in 2022–2026", "color": "2", "x": ws, "y": vcurve(OOS)}],
            "ann": [{"type": "point", "x": round(wis, 4), "y": round(IS["s_mv"], 5), "color": "1", "label": "A", "dx": 0, "dy": 20, "anchor": "middle"},
                    {"type": "point", "x": round(OOS["w_mv"], 4), "y": round(OOS["s_mv"], 5), "color": "2", "label": "B", "dx": 0, "dy": -11, "anchor": "middle"},
                    {"type": "point", "x": round(wis, 4), "y": round(st["case"]["realized"], 5), "color": "2", "label": "C", "dx": 0, "dy": -11, "anchor": "middle"}]}

# ---------------------------------------------------------------- convergence of gradient ascent vs Newton
# Shortfalls far below the floor approach the rounding error of g itself (about 1e-16) and change from machine to
# machine, so each series stops at its first iterate below the floor, drawn on the floor itself (the bottom edge).
# lm07_stats.py computes the shortfall without cancelling two ~64% rates, so the values above the floor are reproducible.
no = st["numopt"]
FLOOR = no["floor"]
LF = round(math.log10(FLOOR))


def to_floor(path):
    xs, ys = [], []
    for k, gap in path:
        xs.append(k)
        if gap < FLOOR:
            ys.append(LF); break
        ys.append(round(math.log10(gap), 2))
    return xs, ys


xg, yg = to_floor(no["ga_path"]); xn, yn = to_floor(no["nt_path"])
conv = {"alt": "Shortfall from the maximum growth rate by iteration, gradient ascent versus Newton's method", "height": 280,
        "x": {"type": "num", "fmt": "n0", "label": "Iteration k", "tipLabel": "k = ", "min": 0, "max": xg[-1]},
        "y": {"type": "lin", "fmt": "n1", "tfmt": "n0", "label": "Growth shortfall g* − g(f_k), log₁₀ scale (−6 means 10⁻⁶)", "min": LF, "max": 0,
              "ticks": [-10, -8, -6, -4, -2, 0]},
        "series": [{"name": "Gradient ascent, fixed step", "color": "2", "x": xg, "y": yg},
                   {"name": "Newton's method", "color": "1", "x": xn, "y": yn}]}

# ---------------------------------------------------------------- level curves of V(w1, w2) and the budget line (IS estimates)
S = np.array([[IS["s1"] ** 2, IS["cov"]], [IS["cov"], IS["s2"] ** 2]])
lam_, Q = np.linalg.eigh(S)
def ellipse(sig, n=240):
    th = np.linspace(0, 2 * np.pi, n + 1)
    pts = Q @ np.diag(sig / np.sqrt(lam_)) @ np.vstack([np.cos(th), np.sin(th)])
    return [round(float(v), 4) for v in pts[0]], [round(float(v), 4) for v in pts[1]]
lv_series = []
for sig, col, nm in ((IS["s_mv"], "1", f"σp = {IS['s_mv']:.2%} (touches the budget line)"), (0.12, "3", "σp = 12%"), (0.15, "4", "σp = 15%")):
    ex, ey = ellipse(sig)
    lv_series.append({"name": nm, "color": col, "x": ex, "y": ey})
lv_series.append({"name": "Budget line w₁ + w₂ = 1", "color": "var(--muted)", "dash": True, "x": [-0.25, 1.25], "y": [1.25, -0.25]})
levels = {"alt": "Level curves of portfolio variance in the plane of the two weights, with the budget line", "height": 400,
          "x": {"type": "num", "fmt": "pct0", "label": "Weight w₁ in 0050", "tipLabel": "w₁ = ", "min": -1.25, "max": 1.25,
                "ticks": [-1.0, -0.5, 0.0, 0.5, 1.0]},
          "y": {"type": "lin", "fmt": "pct0", "label": "Weight w₂ in 00679B (2017–2021 estimates)", "min": -1.25, "max": 1.25,
                "ticks": [-1.0, -0.5, 0.0, 0.5, 1.0]},
          "series": lv_series,
          "ann": [{"type": "point", "x": round(wis, 4), "y": round(1 - wis, 4), "color": "1", "label": "minimum variance: ∇V = λ∇ψ", "dx": 10, "dy": -10},
                  {"type": "point", "x": 0, "y": 0, "color": "var(--muted)", "label": "all cash", "dx": 8, "dy": 16}]}

for name, spec in (("lm07-levels", levels), ("lm07-rollcorr", rollcorr), ("lm07-volcurve", volcurve), ("lm07-converge", conv)):
    (OUT / f"{name}.json").write_text(json.dumps(spec, ensure_ascii=True), encoding="utf-8")
    print("wrote", f"src/data/{name}.json")
print("rolling corr range:", min(v for v in rc if v is not None), max(v for v in rc if v is not None),
      "min date", d_ret[int(np.nanargmin([v if v is not None else np.nan for v in rc]))], "max date", d_ret[int(np.nanargmax([v if v is not None else np.nan for v in rc]))])
late = [(d_ret[i], rc[i]) for i in range(len(rc)) if rc[i] is not None and d_ret[i] >= "2023-01-01"]
lo_, hi_ = min(late, key=lambda t: t[1]), max(late, key=lambda t: t[1])
plotted = {d_ret[i] for i in idx}
print(f"trailing corr, windows ending 2023-01-01 .. {late[-1][0]}: min {lo_[1]:+.4f} on {lo_[0]} (plotted: {lo_[0] in plotted}), "
      f"max {hi_[1]:+.4f} on {hi_[0]} (plotted: {hi_[0] in plotted})")
print("convergence chart:", {"GA": list(zip(xg, yg))[-3:], "Newton": list(zip(xn, yn))})
