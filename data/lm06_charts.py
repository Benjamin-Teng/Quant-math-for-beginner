"""Chart data for LM6 (src/data/lm06-*.json), computed from the verified raw files.
Run:  uv run python data/lm06_charts.py   (imports the analysis in lm06_basis.py)"""
import datetime as dt
import json
from pathlib import Path
from typing import Any

import polars as pl
from lm06_basis import build

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "src" / "data"


def ms(d: str) -> int:
    """Date string -> milliseconds since epoch (for annotations)."""
    y, m, dd = map(int, d.split("-"))
    return int(dt.datetime(y, m, dd, tzinfo=dt.UTC).timestamp() * 1000)


out, d, idx = build()

# ---- 1. cumulative 2025 dividends by ex-date, from the total-return index
cum = out["dividends2025"]["cum"]
divs: dict[str, Any] = {"alt": "Cumulative TAIEX cash dividends by ex-date in 2025, as a share of the index", "height": 300,
        "x": {"type": "date"},
        "y": {"type": "lin", "fmt": "pct2", "tfmt": "pct1", "label": "Cumulative dividends, ln(TR/TR₀) − ln(S/S₀)", "min": 0},
        "series": [{"name": "Dividends gone ex since 31 Dec 2024", "color": "1", "area": True,
                    "x": cum["date"], "y": [round(v, 6) for v in cum["cum"]]}],
        "ann": [{"type": "band", "x0": ms("2025-06-01"), "x1": ms("2025-09-30")}]}   # month ticks come from book.js

# ---- 2. December 2025 contract: actual vs perfect-foresight fair basis, plus the near month
dec = pl.DataFrame(out["dec_series"])
near = d.group_by("date", maintain_order=True).first().sort("date")
decspec: dict[str, Any] = {"alt": "TX December 2025 contract: actual basis and fair basis, April to October 2025", "height": 330,
           "x": {"type": "date"},
           "y": {"type": "lin", "fmt": "n0", "label": "Basis F − S (index points)"},
           "series": [
               {"name": "December contract: actual basis", "color": "1", "x": dec["date"].to_list(),
                "y": [round(v, 2) for v in dec["basis"].to_list()]},
               {"name": "December contract: fair basis (2% financing rate, dividends that went ex)", "color": "2", "dash": True,
                "x": dec["date"].to_list(), "y": [round(v, 2) for v in dec["fair_basis"].to_list()]},
               {"name": "Near-month contract: actual basis", "color": "var(--muted)", "width": 1.2,
                "x": near["date"].to_list(), "y": [round(v, 2) for v in near["basis"].to_list()]}]}   # month ticks from book.js

# ---- 3. term structures on three dates (basis as % of TAIEX vs days to expiry)
names = {"2025-04-01": ("1 April 2025", "3"), "2025-06-27": ("27 June 2025", "2"), "2025-10-31": ("31 October 2025", "1")}
curves: dict[str, Any] = {"alt": "TX basis as a percentage of TAIEX against days to expiry on three dates in 2025", "height": 300,
          "x": {"type": "num", "fmt": "n0", "label": "Days to expiry", "tipLabel": "days to expiry: ", "min": 0, "max": 360},
          "y": {"type": "lin", "fmt": "pct2", "tfmt": "pct1", "label": "Basis (F − S)/S"},
          "series": [{"name": names[k][0], "color": names[k][1], "x": [x["days"] for x in v],
                      "y": [round(x["basis"] / x["S"], 6) for x in v]} for k, v in out["curves"].items()],
          "ann": [{"type": "hline", "y": 0}]}

# ---- 4. pull to par: 10-year annual-coupon bonds at a constant 2% yield, clean price monthly
def clean_price(t, c, y=0.02, n=10, F=100.0):
    """Clean price at time t (years since issue): full price of remaining flows minus accrued coupon."""
    if t >= n: return F
    full = sum((c * F + (F if j == n else 0.0)) * (1 + y) ** -(j - t) for j in range(1, n + 1) if j > t + 1e-12)
    accrued = c * F * (t - int(t + 1e-12))
    return full - accrued

ts = [k / 12 for k in range(121)]
pull: dict[str, Any] = {"alt": "Clean prices of three 10-year bonds at a constant 2% yield, converging to 100", "height": 300,
        "x": {"type": "num", "fmt": "n0", "label": "Years since issue", "tipLabel": "year ", "min": 0, "max": 10,
              "ticks": [0, 2, 4, 6, 8, 10]},
        "y": {"type": "lin", "fmt": "n2", "tfmt": "n0", "label": "Clean price per 100 face"},
        "series": [{"name": f"{lab} coupon", "color": col, "x": [round(t, 4) for t in ts],
                    "y": [round(clean_price(t, c), 4) for t in ts]}
                   for c, lab, col in ((0.04, "4% (premium)", "1"), (0.02, "2% (par)", "3"), (0.005, "0.5% (discount)", "2"))]}

for name, spec in (("lm06-divs", divs), ("lm06-dec", decspec), ("lm06-curves", curves), ("lm06-pull", pull)):
    (OUT / f"{name}.json").write_text(json.dumps(spec, ensure_ascii=True), encoding="utf-8")
    print("wrote", f"src/data/{name}.json", "points:", sum(len(s["x"]) for s in spec["series"]))
print("pull checks: P0(4%)", pull["series"][0]["y"][0], "P5(4%)", pull["series"][0]["y"][60],
      "P0(0.5%)", pull["series"][2]["y"][0], "P5(0.5%)", pull["series"][2]["y"][60])
par_fine = min(clean_price(k / 1000, 0.02) for k in range(10001))
print(f"par bond: 100 on coupon dates; lowest clean price {min(pull['series'][1]['y']):.4f} (monthly), {par_fine:.4f} (fine grid)")
