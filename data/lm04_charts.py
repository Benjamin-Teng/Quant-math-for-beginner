"""Chart data for LM4 (src/data/lm04-*.json), computed from the verified return series.
Run after build_series.py:  python3 data/lm04_charts.py"""
import json
from datetime import date
from pathlib import Path

import numpy as np
import polars as pl
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "src" / "data"
df = pl.read_parquet(HERE / "processed" / "etf_daily_returns.parquet").with_columns(pl.col("date").str.to_date())
R = df["R_0050"].to_numpy()
dates = df["date"].to_list()
T = len(R)
A = T / ((dates[-1] - date(2014, 10, 31)).days / 365.25)      # 243.1 trading days a year

gbar = lambda f, r=R: float(np.log1p(f * r).mean())
dg = lambda f, r=R: float((r / (1 + f * r)).mean())


def kelly(r, xtol=1e-12):
    lo, hi = -1 / r.max(), 1 / -r.min()
    return brentq(lambda f: dg(f, r), lo * (1 - 1e-12), hi * (1 - 1e-12), xtol=xtol)


fs = kelly(R)
f0 = brentq(gbar, fs, 10 * (1 - 1e-12), xtol=1e-12)
mu, m2 = R.mean(), (R**2).mean()

# ---------------------------------------------------------------- growth curve (Exhibit 3)
fx = [round(0.05 * k, 2) for k in range(0, 200)] + [9.97, 9.99]
growth = {"alt": "Annual log growth of constant-leverage 0050 versus leverage, 2014 to 2026", "height": 330,
  "x": {"type": "num", "fmt": "x1", "label": "Leverage f (units of 0050 per unit of equity, rebalanced daily)", "tipLabel": "f = ", "min": 0, "max": 10},
  "y": {"type": "lin", "fmt": "pct1", "tfmt": "pct0", "label": "Annual log growth rate", "min": -0.3, "max": 0.72},
  "series": [
    {"name": "Exact: mean of ln(1 + fR)", "color": "1", "x": fx, "y": [round(gbar(f) * A, 5) for f in fx]},
    {"name": "Quadratic model: fμ − f²E[R²]/2", "color": "2", "dash": True, "x": fx, "y": [round((f * mu - f * f * m2 / 2) * A, 5) for f in fx]}],
  "ann": [
    {"type": "vline", "x": round(fs, 4), "label": f"f* = {fs:.2f}", "anchor": "start"},
    {"type": "vline", "x": 10, "label": "ruin at 10×", "anchor": "end", "dy": 14},
    {"type": "point", "x": 1, "y": round(gbar(1) * A, 5), "color": "1", "label": "0050", "dx": 6, "dy": 14},
    {"type": "point", "x": round(fs / 2, 4), "y": round(gbar(fs / 2) * A, 5), "color": "1", "label": "½ Kelly", "dx": -8, "dy": -10, "anchor": "end"},
    {"type": "point", "x": round(fs, 4), "y": round(gbar(fs) * A, 5), "color": "1"},
    {"type": "point", "x": round(f0, 4), "y": 0.0, "color": "1", "label": f"zero growth {f0:.2f}", "dx": -8, "dy": 16, "anchor": "end"}]}

# ---------------------------------------------------------------- growth retained at a fraction of Kelly (Exhibit 7)
lam = [round(0.02 * k, 2) for k in range(0, 111)]
gs = gbar(fs)
lam_max = 10 / fs                                              # 1.8445: the -10% day wipes out the account beyond this
lam_0050 = [l for l in lam if l * fs < 10 * (1 - 1e-9)]
lam_0050 += [round(lam_max * (1 - e), 6) for e in (2e-3, 1e-3, 4e-4, 1e-4, 1e-5)]   # the plunge to -inf at 10x
share_0050 = [round(gbar(l * fs) / gs, 5) for l in lam_0050]
pB, GB, LB = 0.5, 0.02, 0.01
gb = lambda f: pB * np.log1p(f * GB) + (1 - pB) * np.log1p(-f * LB)
fB = pB / LB - (1 - pB) / GB
share_bet = [round(float(gb(l * fB) / gb(fB)), 5) for l in lam]
share = {"alt": "Share of maximal growth kept at a fraction of the Kelly leverage", "height": 320,
  "x": {"type": "num", "fmt": "n2", "label": "Fraction of Kelly leverage λ = f / f*", "tipLabel": "λ = ", "min": 0, "max": 2.2},
  "y": {"type": "lin", "fmt": "pct1", "tfmt": "pct0", "label": "Growth kept, g(λf*) / g(f*)", "min": -0.6, "max": 1.12},
  "series": [
    {"name": "Quadratic model: 1 − (1 − λ)²", "color": "var(--muted)", "dash": True, "x": lam, "y": [round(1 - (1 - l) ** 2, 5) for l in lam]},
    {"name": "0050 in-sample (exact)", "color": "1", "x": lam_0050, "y": share_0050},
    {"name": "+2% / −1% bet, p = 0.5 (exact)", "color": "2", "x": lam, "y": share_bet}],
  "ann": [
    {"type": "vline", "x": 1, "label": "full Kelly", "anchor": "start"},
    {"type": "vline", "x": 0.5, "label": "half Kelly", "anchor": "end"},
    {"type": "point", "x": 0.5, "y": 0.75, "color": "var(--muted)"},
    {"type": "point", "x": round(f0 / fs, 4), "y": 0.0, "color": "1", "label": f"0050: zero at {f0 / fs:.2f}", "dx": -8, "dy": 16, "anchor": "end"}]}

# ---------------------------------------------------------------- rolling three-year empirical Kelly (Exhibit 8)
W = 729
ends = list(range(W, T + 1))
rk = [kelly(R[e - W:e], xtol=1e-10) for e in ends]
rq = [float(R[e - W:e].mean() / R[e - W:e].var()) for e in ends]
idx = list(range(0, len(ends), 5))
if idx[-1] != len(ends) - 1: idx.append(len(ends) - 1)
xs = [str(dates[ends[i] - 1]) for i in idx]
rolling = {"alt": "Empirical Kelly leverage of 0050 over trailing three-year windows", "height": 300,
  "x": {"type": "date"},
  "y": {"type": "lin", "fmt": "n2", "tfmt": "n0", "label": "Empirical Kelly leverage f* (× equity), trailing 729 trading days", "min": 0, "max": 10},
  "series": [
    {"name": "Exact empirical Kelly", "color": "1", "x": xs, "y": [round(rk[i], 3) for i in idx]},
    {"name": "Quadratic rule μ/s² (same window)", "color": "2", "dash": True, "x": xs, "y": [round(rq[i], 3) for i in idx]}],
  "ann": [{"type": "hline", "y": round(fs, 4)}]}

for name, spec in (("lm04-growth", growth), ("lm04-share", share), ("lm04-rolling", rolling)):
    (OUT / f"{name}.json").write_text(json.dumps(spec, ensure_ascii=True), encoding="utf-8")
    print("wrote", f"src/data/{name}.json")
print(f"f*={fs:.4f} f0={f0:.4f} lam_max={lam_max:.4f} rolling min={min(rk):.3f} max={max(rk):.3f} last={rk[-1]:.3f}")
