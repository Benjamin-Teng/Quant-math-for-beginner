"""Chart data for LM9 (src/data/lm09-*.json), and the presets of the systemExplorer widget (src/lm09.js).

Run after data/vol2_series.py:  uv run python data/lm09_charts.py

Reads data/processed/vol2_closes.parquet only. The hand-sized systems use the percent returns of 7-10 April 2025
rounded to 0.01, solved in exact rational arithmetic as in data/lm09_numbers.py; the drift chart uses the Volume II
sector sample, closes 2008-12-01 .. 2026-10-08. Writing the same data twice gives byte-identical files.
"""
import json
import math
from decimal import ROUND_HALF_EVEN, Decimal
from fractions import Fraction as Fr
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)
cl = pl.read_parquet(HERE / "processed" / "vol2_closes.parquet").sort("date")

Mat = list[list[Fr]]


def r6(x: Fr | float, d: int = 6) -> float:
    """A number rounded to d decimals for the JSON (exact rationals are rounded half-even from their exact value)."""
    if isinstance(x, Fr):
        q = Decimal(x.numerator) / Decimal(x.denominator)
        return float(q.quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_EVEN))
    return round(float(x), d)


def det2(m: Mat) -> Fr:
    return m[0][0] * m[1][1] - m[0][1] * m[1][0]


def det3(m: Mat) -> Fr:
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def solve(m: Mat, b: list[Fr]) -> list[Fr]:
    """Cramer's rule, exact (2x2 or 3x3)."""
    d = det2(m) if len(m) == 2 else det3(m)
    out = []
    for j in range(len(m)):
        mj = [row[:j] + [bi] + row[j + 1:] for row, bi in zip(m, b)]
        out.append((det2(mj) if len(m) == 2 else det3(mj)) / d)
    return out


def inverse3(m: Mat) -> Mat:
    d = det3(m)
    cof = [[(-1) ** (i + j) * det2([r[:j] + r[j + 1:] for k, r in enumerate(m) if k != i]) for j in range(3)] for i in range(3)]
    return [[cof[j][i] / d for j in range(3)] for i in range(3)]


# ---------------------------------------------------------------- the four days, rounded percent returns
DAYS = ["2025-04-07", "2025-04-08", "2025-04-09", "2025-04-10"]
dates = cl["date"].to_list()
i0 = dates.index(DAYS[0])
assert dates[i0 - 1] == "2025-04-02" and dates[i0:i0 + 4] == DAYS
win = cl.slice(i0 - 1, 5)


def pct(series: str) -> list[Fr]:
    """100 (P_t / P_{t-1} - 1) from the two-decimal closes, exact, rounded to 0.01 (no input lies near a tie)."""
    p = [Fr(Decimal(str(round(v, 2)))) for v in win[series].to_list()]
    out = []
    for k in range(4):
        v = 100 * (p[k + 1] / p[k] - 1)
        q = (Decimal(v.numerator) / Decimal(v.denominator)).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
        out.append(Fr(q))
    return out


TAIEX, SEMI, FIN, FOOD = pct("TAIEX"), pct("Semiconductor"), pct("FinancialInsurance"), pct("Food")
assert [str(float(v)) for v in TAIEX] == ["-9.7", "-4.02", "-5.79", "9.25"]
MF = [[SEMI[k], FIN[k], FOOD[k]] for k in range(4)]


def fl(v: list[Fr]) -> list[float]:
    return [float(x) for x in v]


specs: dict[str, dict] = {}

# ---------------------------------------------------------------- rowpic: the 8-9 April system, row picture
M1 = [[SEMI[1], FIN[1]], [SEMI[2], FIN[2]]]
b1 = [TAIEX[1], TAIEX[2]]
x1 = solve(M1, b1)


def line_pts(a: Fr, c: Fr, rhs: Fr, lo: float, hi: float) -> tuple[list[float], list[float]]:
    """Two points of the line a x1 + c x2 = rhs, spread along its steeper coordinate."""
    if abs(c) >= abs(a):
        return [lo, r6(rhs / c - a / c * Fr(lo))], [hi, r6(rhs / c - a / c * Fr(hi))]
    return [r6(rhs / a - c / a * Fr(lo)), lo], [r6(rhs / a - c / a * Fr(hi)), hi]


f8, t8 = line_pts(M1[0][0], M1[0][1], b1[0], -2.0, 2.0)
f9, t9 = line_pts(M1[1][0], M1[1][1], b1[1], -1.0, 3.0)
specs["lm09-rowpic"] = {
    "type": "scatter", "alt": "Row picture: the 8 April and 9 April equations as two lines in the plane of the two multiples, crossing at one point",
    "height": 320,
    "x": {"label": "x_1, multiple of Semiconductor", "fmt": "n3", "tfmt": "n1", "min": 0.0, "max": 2.0, "name": "x_1"},
    "y": {"label": "x_2, multiple of FinancialInsurance", "fmt": "n3", "tfmt": "n1", "min": -1.0, "max": 1.5, "name": "x_2"},
    "lines": [{"from": f8, "to": t8, "extend": True, "color": "1", "width": 2, "label": "8 April: −3.99x_1 + 0.53x_2 = −4.02"},
              {"from": f9, "to": t9, "extend": True, "color": "2", "width": 2, "label": "9 April: −4.47x_1 − 5.61x_2 = −5.79"}],
    "points": [{"at": [r6(x1[0]), r6(x1[1])], "label": "x = (1.035, 0.207)", "color": "var(--ink)", "dx": 10, "dy": -8}],
}

# ---------------------------------------------------------------- colpic: the same system, column picture
m1, m2 = [M1[0][0], M1[1][0]], [M1[0][1], M1[1][1]]
s1 = [x1[0] * v for v in m1]
specs["lm09-colpic"] = {
    "type": "vector", "alt": "Column picture: 1.035 times the Semiconductor column plus 0.207 times the FinancialInsurance column ends at TAIEX's returns",
    "height": 340,
    "x": {"label": "8 April return (%)", "fmt": "n2", "name": "8 April"},
    "y": {"label": "9 April return (%)", "fmt": "n2", "name": "9 April"},
    "vectors": [{"to": fl(m2), "color": "2", "width": 1.5, "dash": True, "label": "m_2"},
                {"to": [r6(v) for v in s1], "color": "1", "width": 2.5, "label": "1.035 m_1", "dx": -6, "dy": -6, "anchor": "end"},
                {"from": [r6(v) for v in s1], "to": fl(b1), "color": "2", "width": 2.5, "label": "0.207 m_2", "dx": -12, "dy": 2,
                 "anchor": "end"},
                {"to": fl(b1), "color": "var(--ink)", "width": 1.5, "label": "b (TAIEX)", "dx": 12, "dy": -2, "anchor": "start"}],
}

# ---------------------------------------------------------------- three: one, none or infinitely many solutions
specs["lm09-three"] = {
    "type": "scatter", "alt": "Three partner lines for the line x1 + x2 = 2: one crosses it, one is parallel, one coincides with it",
    "height": 320,
    "x": {"label": "x_1", "fmt": "n1", "min": -0.5, "max": 3.5, "name": "x_1"},
    "y": {"label": "x_2", "fmt": "n1", "min": -0.5, "max": 3.5, "name": "x_2"},
    "series": [{"name": "x_1 + x_2 = 2", "color": "var(--ink)", "x": [], "y": []},
               {"name": "x_1 − x_2 = 0: crosses it at (1, 1)", "color": "1", "x": [1], "y": [1], "r": 5},
               {"name": "x_1 + x_2 = 3: parallel, no common point", "color": "2", "x": [], "y": []},
               {"name": "2x_1 + 2x_2 = 4: the same line (dashed)", "color": "3", "x": [], "y": []}],
    "lines": [{"from": [0, 2], "to": [2, 0], "extend": True, "color": "var(--ink)", "width": 3},
              {"from": [0, 0], "to": [1, 1], "extend": True, "color": "1", "width": 2},
              {"from": [0, 3], "to": [3, 0], "extend": True, "color": "2", "width": 2},
              {"from": [0, 2], "to": [2, 0], "extend": True, "color": "3", "width": 2, "dash": True}],
}

# ---------------------------------------------------------------- area: E1's parallelogram beside the 1.52-degree pair
M2 = [[SEMI[0], FOOD[0]], [SEMI[2], FOOD[2]]]
b2 = [TAIEX[0], TAIEX[2]]
x2 = solve(M2, b2)
p1, q1 = [M1[0][0], M1[1][0]], [M1[0][1], M1[1][1]]
p2, q2 = [M2[0][0], M2[1][0]], [M2[0][1], M2[1][1]]
s_1 = [p1[0] + q1[0], p1[1] + q1[1]]
s_2 = [p2[0] + q2[0], p2[1] + q2[1]]


def ang(u: list[Fr], v: list[Fr]) -> float:
    fu, fv = np.array(fl(u)), np.array(fl(v))
    return math.degrees(math.acos(float(fu @ fv) / float(np.linalg.norm(fu) * np.linalg.norm(fv))))


specs["lm09-area"] = {
    "type": "vector",
    "alt": "Two parallelograms spanned by pairs of return columns: a wide one of area 24.753 and a thin sliver of area 2.7813 whose columns are 1.52 degrees apart",
    "height": 330,
    "x": {"label": "return on the first day of the pair (%)", "fmt": "n2", "name": "first day"},
    "y": {"label": "return on the second day (%)", "fmt": "n2", "name": "second day"},
    "series": [{"name": "8 and 9 April: m_1 Semiconductor, m_2 FinancialInsurance (θ = 47.15°)", "color": "1",
                "x": [r6((s_1[0]) / 2, 4)], "y": [r6((s_1[1]) / 2, 4)], "r": 2.5},
               {"name": "7 and 9 April: m_1 Semiconductor, m_2 Food (θ = 1.52°)", "color": "2",
                "x": [r6((s_2[0]) / 2, 4)], "y": [r6((s_2[1]) / 2, 4)], "r": 2.5}],
    "points": [{"at": [r6(s_1[0], 4), r6(s_1[1], 4)], "label": "area 24.753", "color": "1", "r": 2.5, "dx": -4, "dy": 24, "anchor": "end"},
               {"at": [r6(s_2[0], 4), r6(s_2[1], 4)], "label": "area 2.7813", "color": "2", "r": 2.5, "dx": -2, "dy": 24}],
    "vectors": [{"to": fl(p1), "color": "1", "label": "m_1"}, {"to": fl(q1), "color": "1", "label": "m_2"},
                {"to": fl(p2), "color": "2", "label": "m_1", "dx": -6, "dy": -10}, {"to": fl(q2), "color": "2", "label": "m_2", "dx": 4, "dy": 16}],
    "segments": [{"from": fl(p1), "to": fl(s_1), "color": "1"}, {"from": fl(q1), "to": fl(s_1), "color": "1"},
                 {"from": fl(p2), "to": fl(s_2), "color": "2"}, {"from": fl(q2), "to": fl(s_2), "color": "2"}],
}
assert det2(M1) == Fr("24.753") and det2(M2) == Fr("2.7813")
assert f"{ang(p1, q1):.2f}" == "47.15" and f"{ang(p2, q2):.2f}" == "1.52"

# the widget's presets (src/lm09.js reads them from this chart's JSON)
sig = [[Fr("0.040425"), Fr("-0.002866")], [Fr("-0.002866"), Fr("0.018214")]]
exc = [Fr("0.22751"), Fr("-0.02547")]
presets = [
    {"id": "e1", "name": "8 and 9 April: Semiconductor, FinancialInsurance", "m": [fl(r) for r in M1], "b": fl(b1),
     "rows": ["8 April", "9 April"], "cols": ["Semiconductor", "FinancialInsurance"], "unit": "%", "range": [12, 12], "step": "0.01",
     "x": [r6(v) for v in x1]},
    {"id": "e2", "name": "7 and 9 April: Semiconductor, Food (1.52°)", "m": [fl(r) for r in M2], "b": fl(b2),
     "rows": ["7 April", "9 April"], "cols": ["Semiconductor", "Food"], "unit": "%", "range": [12, 12], "step": "0.01",
     "x": [r6(v) for v in x2]},
    {"id": "col", "name": "Collinear: Semiconductor and a 2× fund (illustrative)",
     "m": [[float(M1[0][0]), float(2 * M1[0][0])], [float(M1[1][0]), float(2 * M1[1][0])]], "b": fl(b1),
     "rows": ["8 April", "9 April"], "cols": ["Semiconductor", "2× fund"], "unit": "%", "range": [20, 12], "step": "0.01", "x": None},
    {"id": "lm7", "name": "LM7's Σ and excess returns", "m": [fl(r) for r in sig], "b": fl(exc),
     "rows": ["equation 1", "equation 2"], "cols": ["0050", "00679B"],
     "axes": ["f_1, Kelly fraction of 0050", "f_2, Kelly fraction of 00679B"], "unit": "", "range": [0.06, 0.3],
     "step": "any", "x": [r6(v, 4) for v in solve(sig, exc)]},
]
specs["lm09-area"]["widget"] = {"tol": 1e-9, "presets": presets}

# ---------------------------------------------------------------- cost: Cramer's (n+1)! terms against (2/3) n^3
ns = list(range(2, 21))
specs["lm09-cost"] = {
    "alt": "The number of terms of Cramer's rule with cofactor expansions against the operations of elimination, log scale, n from 2 to 20",
    "height": 300,
    "x": {"type": "num", "fmt": "n0", "label": "Number of unknowns n", "tipLabel": "n = ", "min": 2, "max": 20, "ticks": [2, 5, 10, 15, 20]},
    "y": {"type": "lin", "fmt": "n1", "tfmt": "n0", "label": "log₁₀ of the count (5 means 10⁵)", "min": 0, "max": 20, "ticks": [0, 5, 10, 15, 20]},
    "series": [{"name": "Cramer's rule: (n+1)! terms", "color": "2", "x": ns, "y": [round(math.log10(math.factorial(n + 1)), 4) for n in ns]},
               {"name": "Elimination: 2n^3/3 operations", "color": "1", "x": ns, "y": [round(math.log10(2 * n**3 / 3), 4) for n in ns]}],
}

# ---------------------------------------------------------------- inverse: the 7-9 April matrix
M3 = [MF[0], MF[1], MF[2]]
Minv = inverse3(M3)
flat = [r6(v) for r in Minv for v in r]
specs["lm09-inverse"] = {
    "type": "heatmap", "alt": "Heatmap of the inverse of the 7 to 9 April matrix: rows are the three multiples, columns the three days",
    "rows": ["x_1", "x_2", "x_3"], "cols": ["7 April", "8 April", "9 April"],
    "matrix": [[r6(v) for v in r] for r in Minv], "fmt": "n3", "min": math.floor(min(flat) * 1000) / 1000,
    "max": math.ceil(max(flat) * 1000) / 1000, "scaleFmt": "n2", "valueName": "change in x_i per point of TAIEX on the day",
}

# ---------------------------------------------------------------- triples: the exact mix on each triple of days
TRI = {"7, 8, 9 Apr": [0, 1, 2], "7, 8, 10 Apr": [0, 1, 3], "7, 9, 10 Apr": [0, 2, 3], "8, 9, 10 Apr": [1, 2, 3]}
sols = {k: solve([MF[r] for r in v], [TAIEX[r] for r in v]) for k, v in TRI.items()}
specs["lm09-triples"] = {
    "type": "bar", "alt": "The exact replicating mix for each of the four triples of days: the multiples of Semiconductor, FinancialInsurance and Food",
    "height": 300, "categories": list(TRI), "valueLabels": True,
    "x": {"label": "Days used"},
    "y": {"fmt": "n3", "tfmt": "n1", "label": "Multiple in the exact mix"},
    "series": [{"name": "Semiconductor x_1", "color": "1", "values": [r6(s[0]) for s in sols.values()]},
               {"name": "FinancialInsurance x_2", "color": "2", "values": [r6(s[1]) for s in sols.values()]},
               {"name": "Food x_3", "color": "3", "values": [r6(s[2]) for s in sols.values()]}],
}

# ---------------------------------------------------------------- wline: the 7-8 April line of mixes
# reduced echelon form of the first two rows: x1 = p1 + h1 x3, x2 = p2 + h2 x3
a, b_, c = MF[0], MF[1], [TAIEX[0], TAIEX[1]]
d12 = a[0] * b_[1] - a[1] * b_[0]
p_1 = (c[0] * b_[1] - a[1] * c[1]) / d12
p_2 = (a[0] * c[1] - c[0] * b_[0]) / d12
h_1 = -(a[2] * b_[1] - a[1] * b_[2]) / d12
h_2 = -(a[0] * b_[2] - a[2] * b_[0]) / d12
for k in ("7, 8, 9 Apr", "7, 8, 10 Apr"):
    s = sols[k]
    assert s[0] == p_1 + h_1 * s[2] and s[1] == p_2 + h_2 * s[2]
specs["lm09-wline"] = {
    "type": "scatter", "alt": "The line of mixes that reproduce TAIEX on 7 and 8 April, seen in the plane of the first two multiples, with the two points that a third day picks",
    "height": 320,
    "x": {"label": "x_1, multiple of Semiconductor", "fmt": "n3", "tfmt": "n1", "min": -0.6, "max": 2.6, "name": "x_1"},
    "y": {"label": "x_2, multiple of FinancialInsurance", "fmt": "n3", "tfmt": "n1", "min": -3.4, "max": 3.4, "name": "x_2"},
    "lines": [{"from": [r6(p_1 - 2 * h_1), r6(p_2 - 2 * h_2)], "to": [r6(p_1 + 2 * h_1), r6(p_2 + 2 * h_2)], "color": "var(--ink-2)",
               "width": 2}],
    "series": [{"name": "with 9 April (x_3 = −0.916)", "color": "1", "x": [r6(sols["7, 8, 9 Apr"][0])], "y": [r6(sols["7, 8, 9 Apr"][1])], "r": 5},
               {"name": "with 10 April (x_3 = 0.900)", "color": "2", "x": [r6(sols["7, 8, 10 Apr"][0])], "y": [r6(sols["7, 8, 10 Apr"][1])], "r": 5}],
    "points": [{"at": [r6(p_1), r6(p_2)], "label": "x_p (x_3 = 0)", "color": "var(--muted)", "r": 3.5}],
}

# ---------------------------------------------------------------- drift: buy-and-hold weight in Semiconductor
cs = cl.filter(pl.col("date") >= pl.lit("2008-12-01")).sort("date")
cd = cs["date"].to_list()
PS, PF = cs["Semiconductor"].to_numpy(), cs["FinancialInsurance"].to_numpy()
V = 0.5 * PS / PS[0] + 0.5 * PF / PF[0]
wS = 0.5 * (PS / PS[0]) / V
imax, imin = int(np.argmax(wS)), int(np.argmin(wS))
keep = sorted(set(range(0, len(cd), 5)) | {imax, imin, len(cd) - 1})
specs["lm09-drift"] = {
    "alt": "Semiconductor's weight in a 50/50 mix with FinancialInsurance: constant at 0.5 when rebalanced daily, drifting to 0.858 when bought and held, December 2008 to October 2026",
    "height": 300,
    "x": {"type": "date"},
    "y": {"type": "lin", "fmt": "n3", "tfmt": "n1", "label": "Weight of Semiconductor in the 50/50 mix", "min": 0.4, "max": 0.9},
    "series": [{"name": "Bought on 1 December 2008 and held", "color": "1", "x": [cd[i] for i in keep], "y": [round(float(wS[i]), 4) for i in keep]},
               {"name": "Rebalanced to 50/50 every day", "color": "2", "dash": True, "x": [cd[0], cd[-1]], "y": [0.5, 0.5]}],
    "ann": [{"type": "point", "x": cd[imax], "y": round(float(wS[imax]), 4), "color": "1", "label": f"{wS[imax]:.3f}", "dx": -8, "dy": -8, "anchor": "end"},
            {"type": "point", "x": cd[imin], "y": round(float(wS[imin]), 4), "color": "1", "label": f"{wS[imin]:.3f}", "dx": 0, "dy": 16, "anchor": "middle"},
            {"type": "point", "x": cd[-1], "y": round(float(wS[-1]), 4), "color": "1", "label": f"{wS[-1]:.3f}", "dx": -6, "dy": 18, "anchor": "end"}],
}

for name, spec in specs.items():
    (OUT / f"{name}.json").write_text(json.dumps(spec, ensure_ascii=True, sort_keys=False), encoding="utf-8", newline="\n")
    print("wrote", f"src/data/{name}.json")
print(f"rowpic x = {x1[0]} {x1[1]}; area x2 = {[r6(v) for v in x2]}; drift max {wS[imax]:.4f} {cd[imax]}, min {wS[imin]:.4f} {cd[imin]}, "
      f"end {wS[-1]:.4f} {cd[-1]}; points plotted {len(keep)}")
