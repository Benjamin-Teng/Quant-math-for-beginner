"""Chart data for LM2 (src/data/lm02-*.json).

  lm02-leverage : leverage of one TX contract held from 10 June to 31 October 2025 (accounts A and B)
  lm02-fderror  : relative error of forward and central differences for the bond's P'(2%) versus step size

Run:  python3 data/lm02_charts.py
"""
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import sympy as sp

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "src" / "data"
sys.path.insert(0, str(HERE))
import lm02_case as case                      # noqa: E402  (same folder)


def bond_price(y, c=0.02, n=10, face=100.0):
    """10-year bond with a 2% annual coupon (same function as lm02_numbers.py)."""
    return sum(c * face / (1 + y) ** t for t in range(1, n + 1)) + face / (1 + y) ** n


def bond_derivs(y0):
    """Price and first three derivatives at y0, exact (symbolic)."""
    y = sp.Symbol("y")
    Ps = sum(sp.Rational(2) / (1 + y) ** t for t in range(1, 11)) + 100 / (1 + y) ** 10
    y0r = sp.nsimplify(y0)
    return tuple(float(sp.diff(Ps, y, k).subs(y, y0r)) for k in range(4))

# ---------------------------------------------------------------- leverage path
tx, ta = case.load()
df, _ = case.held_series(tx, ta)
pa = case.account_path(df, "2025-06-10", case.EQ_A)
pb = case.account_path(df, "2025-06-10", case.EQ_B)
assert [p["date"] for p in pa] == [p["date"] for p in pb]
xs = [p["date"] for p in pa]
ts0 = int(datetime(*map(int, xs[0].split("-")), tzinfo=timezone.utc).timestamp() * 1000)   # date axis: ms since epoch
leverage = {
    "alt": "Leverage of one TX contract held from 10 June to 31 October 2025 in two accounts", "height": 300,
    "endLabels": True, "endValue": False, "endMargin": 90,
    "x": {"type": "date"},
    "y": {"type": "lin", "fmt": "n2", "tfmt": "n0", "label": "Leverage f = notional ÷ equity", "min": 0, "max": 8.5},
    "series": [
        {"name": "Account A: NT$600,000 on 10 June", "endLabel": f"A {pa[-1]['f']:.2f}", "color": "2", "x": xs, "y": [round(p["f"], 4) for p in pa]},
        {"name": "Account B: NT$900,000 on 10 June", "endLabel": f"B {pb[-1]['f']:.2f}", "color": "1", "x": xs, "y": [round(p["f"], 4) for p in pb]}],
    "ann": [{"type": "point", "x": ts0, "y": round(pa[0]["f"], 4), "color": "2", "label": f"{pa[0]['f']:.2f}", "dx": 9, "dy": -8},
            {"type": "point", "x": ts0, "y": round(pb[0]["f"], 4), "color": "1", "label": f"{pb[0]['f']:.2f}", "dx": 9, "dy": 16}],
}

# ---------------------------------------------------------------- finite-difference error
EPS = np.finfo(float).eps
y0 = 0.02
P0, d1, d2, d3 = bond_derivs(y0)
ks = [round(-16 + 0.25 * i, 2) for i in range(0, 61)]          # log10 h from -16 to -1
fw, ce, fw_m, ce_m = [], [], [], []
for k in ks:
    h = 10.0 ** k
    efw = abs((bond_price(y0 + h) - P0) / h - d1) / abs(d1)
    ece = abs((bond_price(y0 + h) - bond_price(y0 - h)) / (2 * h) - d1) / abs(d1)
    fw.append(round(math.log10(efw), 3) if efw > 0 else None)
    ce.append(round(math.log10(ece), 3) if ece > 0 else None)
    fw_m.append(round(math.log10((abs(d2) / 2 * h + 2 * EPS * P0 / h) / abs(d1)), 3))
    ce_m.append(round(math.log10((abs(d3) / 6 * h * h + EPS * P0 / h) / abs(d1)), 3))
fderror = {
    "alt": "Relative error of forward and central difference estimates of a bond price derivative versus step size, log-log",
    "height": 320,
    "x": {"type": "num", "fmt": "n0", "label": "log₁₀ h  (step in units of yield)", "tipLabel": "log₁₀ h = ",
          "min": -16, "max": -1, "ticks": [-16, -14, -12, -10, -8, -6, -4, -2]},
    "y": {"type": "lin", "fmt": "n1", "tfmt": "n0", "label": "log₁₀ of relative error in P′(2%)", "min": -12, "max": 0,
          "ticks": [-12, -10, -8, -6, -4, -2, 0]},
    "series": [
        {"name": "Forward difference", "color": "2", "x": ks, "y": fw},
        {"name": "Central difference", "color": "1", "x": ks, "y": ce},
        {"name": "Model: ½|P″|h + 2ε|P|/h", "color": "2", "dash": True, "x": ks, "y": fw_m},
        {"name": "Model: |P‴|h²/6 + ε|P|/h", "color": "1", "dash": True, "x": ks, "y": ce_m}],
}

for name, spec in (("lm02-leverage", leverage), ("lm02-fderror", fderror)):
    (OUT / f"{name}.json").write_text(json.dumps(spec, ensure_ascii=True), encoding="utf-8")
    print("wrote", f"src/data/{name}.json")
jmin = int(np.nanargmin([v if v is not None else np.nan for v in ce]))
imin = int(np.nanargmin([v if v is not None else np.nan for v in fw]))
print(f"leverage: A {pa[0]['f']:.3f} -> {pa[-1]['f']:.3f}; B {pb[0]['f']:.3f} -> {pb[-1]['f']:.3f}; points {len(xs)}")
print(f"fderror: forward min log10 rel err {fw[imin]} at log10 h = {ks[imin]}; central min {ce[jmin]} at {ks[jmin]}")
