"""Chart data for LM3 (src/data/lm03-*.json), computed from the verified return series.

Run after data/build_series.py:  uv run python data/lm03_charts.py
"""

import json
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "src" / "data"


def price(y, c=0.02, n=10, face=100.0):
    """Price per 100 face of an annual-coupon bond at yield y (the 10-year 2% bond by default)."""
    return sum(c * face / (1 + y) ** t for t in range(1, n + 1)) + face / (1 + y) ** n


def main():
    df = pl.read_parquet(HERE / "processed" / "etf_daily_returns.parquet")
    R, RL, d = df["R_0050"].to_numpy(), df["R_00631L"].to_numpy(), df["date"].to_list()
    dates = ["2014-10-31", *d]                                     # base date: last close before the first return
    W0 = np.concatenate([[1.0], np.cumprod(1 + R)])                # 0050 total return
    WL = np.concatenate([[1.0], np.cumprod(1 + RL)])               # 00631L
    W2 = np.concatenate([[1.0], np.cumprod(1 + 2 * R)])            # exact daily 2x of 0050
    WT = np.concatenate([[1.0], (np.cumprod(1 + R) ** 2) * np.exp(-np.cumsum(R**2))])   # Taylor (3.11)
    gap_act = np.concatenate([[0.0], np.cumsum(np.log1p(RL) - 2 * np.log1p(R))])
    gap_ex = np.concatenate([[0.0], np.cumsum(np.log1p(2 * R) - 2 * np.log1p(R))])
    gap_t2 = np.concatenate([[0.0], -np.cumsum(R**2)])
    idx = list(range(0, len(dates), 5))                            # weekly thinning keeps the page light
    if idx[-1] != len(dates) - 1:
        idx.append(len(dates) - 1)

    def pick(a, k=4):
        return [round(float(a[i]), k) for i in idx]

    xs = [dates[i] for i in idx]
    # the legend carries each curve's end value: the exact and Taylor curves end 0.003 apart, too close for end labels;
    # five decimals keep the two-decimal end labels and tooltips equal to the values quoted in the text
    wealth = {
        "alt": "Growth of 1 unit, log scale, Nov 2014 to Oct 2026", "height": 340, "endLabels": True,
        "endValue": True, "x": {"type": "date"},
        "y": {"type": "log", "fmt": "x2", "tfmt": "x1", "label": "Growth of 1 unit (log scale)"},
        "series": [
            {"name": f"00631L (market price), end {WL[-1]:.2f}", "endLabel": "00631L", "color": "2", "fmt": "n2",
             "x": xs, "y": pick(WL, 5)},
            {"name": f"Exact daily 2× of 0050, end {W2[-1]:.3f}", "endLabel": "Daily 2×", "color": "1", "fmt": "n3",
             "x": xs, "y": pick(W2, 5)},
            {"name": f"Taylor: G² · e^(−ΣR²), end {WT[-1]:.3f}", "endLabel": "Taylor", "color": "4", "dash": True,
             "fmt": "n3", "x": xs, "y": pick(WT, 5)},
            {"name": f"0050 total return, end {W0[-1]:.2f}", "endLabel": "0050", "color": "3", "fmt": "n2",
             "x": xs, "y": pick(W0, 5)}],
        "endMargin": 150}
    gap = {
        "alt": "Cumulative log-point gap versus twice 0050, Nov 2014 to Oct 2026", "height": 320, "endLabels": True,
        "x": {"type": "date"},
        "y": {"type": "lin", "fmt": "n2", "label": "Cumulative gap vs 2 × log growth of 0050 (log points)"},
        "series": [
            {"name": "00631L actual gap", "endLabel": "00631L", "color": "2", "x": xs, "y": pick(gap_act)},
            {"name": "Exact daily-rebalancing effect", "endLabel": "Exact", "color": "1", "x": xs, "y": pick(gap_ex)},
            {"name": "Taylor: −ΣR²", "endLabel": "−ΣR²", "color": "4", "dash": True, "x": xs, "y": pick(gap_t2)}],
        "ann": [{"type": "hline", "y": 0}], "endMargin": 120}

    y0 = 0.02
    P0 = price(y0)
    dP = -sum(t * 2 / (1 + y0) ** (t + 1) for t in range(1, 11)) - 10 * 100 / (1 + y0) ** 11
    d2P = sum(t * (t + 1) * 2 / (1 + y0) ** (t + 2) for t in range(1, 11)) + 110 * 100 / (1 + y0) ** 12
    Dm, C = -dP / P0, d2P / P0                                     # 8.98259 and 93.9955, analytic
    ys = [round(k * 0.0025, 4) for k in range(25)]
    bond = {
        "alt": "Bond price versus yield with first- and second-order approximations", "height": 300,
        "endLabels": True,
        "x": {"type": "num", "fmt": "pct1", "label": "Yield to maturity", "tipLabel": "yield "},
        "y": {"type": "lin", "fmt": "n1", "label": "Price per 100 face (10-year, 2% annual coupon)"},
        "series": [
            {"name": "Exact price", "endLabel": "Exact", "color": "1", "x": ys, "y": [round(price(y), 3) for y in ys]},
            {"name": "Duration only (1st order)", "endLabel": "1st order", "color": "2", "x": ys,
             "y": [round(P0 * (1 - Dm * (y - y0)), 3) for y in ys]},
            {"name": "Duration + convexity (2nd order)", "endLabel": "2nd order", "color": "3", "dash": True, "x": ys,
             "y": [round(P0 * (1 - Dm * (y - y0) + 0.5 * C * (y - y0) ** 2), 3) for y in ys]}],
        "ann": [{"type": "point", "x": 0.02, "y": 100.0, "label": "expansion point y₀ = 2%", "color": "1", "dx": 8,
                 "dy": -10}],
        "endMargin": 130}

    for name, spec in (("lm03-wealth", wealth), ("lm03-gap", gap), ("lm03-bond", bond)):
        (OUT / f"{name}.json").write_text(json.dumps(spec, ensure_ascii=True), encoding="utf-8")
        print("wrote", f"src/data/{name}.json")
    print(f"end values: 00631L {WL[-1]:.4f}, exact 2x {W2[-1]:.5f}, Taylor {WT[-1]:.5f}, 0050 {W0[-1]:.4f}; "
          f"Dmod {Dm:.6f}, C {C:.6f}")


if __name__ == "__main__":
    main()
