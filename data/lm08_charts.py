"""Chart specs for LM8 (src/data/lm08-*.json), from the loaders of data/lm08_numbers.py.

Run:  uv run python data/lm08_charts.py

Writes lm08-arrow, lm08-pnl-lines, lm08-balls, lm08-cs-proof, lm08-plane, lm08-angles and lm08-week. Every number is
rounded before it is written, so two runs give identical files.
"""
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path

import lm08_numbers as nb  # data/lm08_numbers.py: Python puts the script's own folder first on sys.path

OUT = Path(__file__).resolve().parent.parent / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)


def r(x: float | Fraction, nd: int = 6) -> float:
    return round(float(x), nd)


def arc(radius: float, deg0: float, deg1: float, n: int = 16) -> list[dict]:
    """A circular arc from deg0 to deg1 as short solid segments (the vector chart has no curve primitive)."""
    pts = [(radius * math.cos(math.radians(deg0 + (deg1 - deg0) * k / n)),
            radius * math.sin(math.radians(deg0 + (deg1 - deg0) * k / n))) for k in range(n + 1)]
    return [{"from": [r(a[0], 4), r(a[1], 4)], "to": [r(b[0], 4), r(b[1], 4)], "dash": False, "color": "var(--muted)",
             "width": 1.2} for a, b in itertools.pairwise(pts)]


def write(name: str, spec: dict) -> None:
    (OUT / f"{name}.json").write_text(json.dumps(spec, ensure_ascii=True, allow_nan=False), encoding="utf-8")
    print("wrote", f"src/data/{name}.json")


def main() -> None:
    c = nb.case()
    X = nb.week_returns(c)
    P, H = c["P"], nb.H
    days = ["7 Apr", "8 Apr", "9 Apr", "10 Apr", "11 Apr"]

    # ---------------------------------------------------------------- arrow (Section 1)
    write("lm08-arrow", {
        "type": "vector", "height": 380,
        "alt": "The weight vector w = (0.6, 0.4) drawn as an arrow from the origin, with the basis vectors e1 and e2 "
               "and the components 0.6 e1 and 0.4 e2",
        "x": {"label": "First entry: weight in 0050", "fmt": "n1", "min": -0.12, "max": 1.2, "name": "0050"},
        "y": {"label": "Second entry: weight in 00679B", "fmt": "n1", "min": -0.12, "max": 1.12, "name": "00679B"},
        "segments": [{"from": [0.6, 0], "to": [0.6, 0.4]}, {"from": [0, 0.4], "to": [0.6, 0.4]}],
        "vectors": [
            {"to": [1, 0], "label": "e_1", "color": "var(--muted)", "width": 1.6},
            {"to": [0, 1], "label": "e_2", "color": "var(--muted)", "width": 1.6},
            {"to": [0.6, 0], "label": "0.6 e_1", "color": "2", "dash": True, "dx": -30, "dy": 16},
            {"to": [0, 0.4], "label": "0.4 e_2", "color": "2", "dash": True, "dx": -6},
            {"to": [0.6, 0.4], "label": "w = (0.6, 0.4)", "color": "1", "width": 2.8}]})

    # ---------------------------------------------------------------- pnl-lines (Section 2)
    lines = [[H[i] * (P[k][i] - P[k - 1][i]) for k in range(1, 6)] for i in range(3)]
    write("lm08-pnl-lines", {
        "type": "bar", "height": 300,
        "alt": "Daily P&L of the three lines of the case book from 7 to 11 April 2025: the short TX contract, "
               "24,000 shares of 0050 and 100,000 shares of 00679B",
        "categories": days, "x": {"label": "Session, April 2025"},
        "y": {"fmt": "n0", "label": "Daily P&L of each line, NT$"},
        "series": [{"name": "TX, 1 contract short", "color": "1", "values": [int(v) for v in lines[0]]},
                   {"name": "0050, 24,000 shares", "color": "2", "values": [int(v) for v in lines[1]]},
                   {"name": "00679B, 100,000 shares", "color": "3", "values": [int(v) for v in lines[2]]}],
        "ann": [{"type": "hline", "y": 0}]})

    # ---------------------------------------------------------------- balls (Section 3)
    f = [float(H[i] * P[0][i] / nb.W0) for i in range(2)]
    diamond = [[1, 0], [0, 1], [-1, 0], [0, -1], [1, 0]]
    write("lm08-balls", {
        "type": "vector", "height": 360,
        "alt": "The unit circle of the Euclidean norm, the diamond of the 1-norm and the case's exposures to TX "
               "and 0050, close to the line of zero net exposure",
        "x": {"label": "Exposure to TX, f_{TX} (multiple of equity)", "fmt": "n2", "tfmt": "n1", "min": -1.3,
              "max": 1.3, "name": "f_{TX}"},
        "y": {"label": "Exposure to 0050, f_{0050} (multiple of equity)", "fmt": "n2", "tfmt": "n1", "min": -1.3,
              "max": 1.3, "name": "f_{0050}"},
        "series": [{"name": "Euclidean norm 1 (circle)", "color": "1", "x": [], "y": []},
                   {"name": "1-norm 1 (diamond)", "color": "2", "x": [], "y": []}],
        "ellipses": [{"center": [0, 0], "cov": [[1, 0], [0, 1]], "scale": 1, "color": "1"}],
        "lines": [{"from": a, "to": b, "color": "2", "width": 1.8} for a, b in itertools.pairwise(diamond)],
        "segments": [{"from": [-1.25, 1.25], "to": [1.25, -1.25], "color": "var(--muted)", "label": "net exposure 0"}],
        "points": [{"at": [r(f[0], 5), r(f[1], 5)], "label": "case: (−0.426, 0.422)", "color": "var(--ink)",
                    "dx": -150, "dy": -10}]})

    # ---------------------------------------------------------------- cs-proof (Section 4)
    x, y, a = (1.5, 2.5), (3.0, 1.0), 0.7
    ay = (a * y[0], a * y[1])
    uy, ur = (y[0] / math.hypot(*y), y[1] / math.hypot(*y)), (-0.6 / math.hypot(0.6, 1.8), 1.8 / math.hypot(0.6, 1.8))
    s = 0.16                                                    # the right-angle mark at a*y
    q1 = (ay[0] - s * uy[0], ay[1] - s * uy[1])
    q2 = (q1[0] + s * ur[0], q1[1] + s * ur[1])
    q3 = (ay[0] + s * ur[0], ay[1] + s * ur[1])
    th_x, th_y = math.degrees(math.atan2(x[1], x[0])), math.degrees(math.atan2(y[1], y[0]))
    mid = math.radians((th_x + th_y) / 2)
    write("lm08-cs-proof", {
        "type": "vector", "height": 320,
        "alt": "The vectors x = (1.5, 2.5) and y = (3, 1), the multiple a*y = (2.1, 0.7) closest to x, and the dashed "
               "leftover x - a*y, perpendicular to y",
        "x": {"fmt": "n1", "tfmt": "n1", "min": -0.3, "max": 3.5}, "y": {"fmt": "n1", "tfmt": "n1", "min": -0.3, "max": 2.9},
        "segments": [{"from": [r(ay[0], 4), r(ay[1], 4)], "to": list(x), "color": "3"}]
                    + [{"from": [r(p[0], 4), r(p[1], 4)], "to": [r(q[0], 4), r(q[1], 4)], "dash": False,
                        "color": "var(--muted)", "width": 1.2} for p, q in ((q1, q2), (q2, q3))]
                    + arc(0.75, th_y, th_x),
        "vectors": [{"to": list(x), "label": "x", "color": "1", "width": 2.6},
                    {"to": list(y), "label": "y", "color": "2", "width": 2.6},
                    {"to": [r(ay[0], 4), r(ay[1], 4)], "label": "a*y", "color": "4", "width": 3.4, "dy": 16}],
        "points": [{"at": [r(1.02 * math.cos(mid), 4), r(1.02 * math.sin(mid), 4)], "label": "θ", "r": 0.01,
                    "color": "var(--muted)", "dx": -2, "dy": 5},
                   {"at": [r((ay[0] + x[0]) / 2, 4), r((ay[1] + x[1]) / 2, 4)], "label": "x − a*y", "r": 0.01,
                    "color": "3", "dx": 8, "dy": 4}]})

    # ---------------------------------------------------------------- plane (Section 5)
    v = nb.lm7_vols()
    s1, s2, deg = 100 * v["s1"], 100 * v["s2"], nb.angle(v["rho"])
    v1 = (s1, 0.0)
    v2 = (s2 * math.cos(math.radians(deg)), s2 * math.sin(math.radians(deg)))
    w = 0.423
    a1, a2 = (w * v1[0], w * v1[1]), ((1 - w) * v2[0], (1 - w) * v2[1])
    mx = (a1[0] + a2[0], a1[1] + a2[1])
    write("lm08-plane", {
        "type": "vector", "height": 340,
        "alt": "The centred daily return vectors of 0050 and 00679B drawn in their own plane, of lengths 20.11% and "
               "13.50% at 96.06 degrees, and the 42.3/57.7 mix as the diagonal of a parallelogram, of length 10.91%",
        "x": {"label": "Along centred 0050, % a year", "fmt": "n2", "tfmt": "n0", "min": -3.5, "max": 23},
        "y": {"label": "Perpendicular to it, in the plane of the two vectors, % a year", "fmt": "n2", "tfmt": "n0",
              "min": -1.5, "max": 15.5},
        "segments": [{"from": [r(a1[0], 4), r(a1[1], 4)], "to": [r(mx[0], 4), r(mx[1], 4)]},
                     {"from": [r(a2[0], 4), r(a2[1], 4)], "to": [r(mx[0], 4), r(mx[1], 4)]}] + arc(4.5, 0, deg, 24),
        "vectors": [{"to": [r(v1[0], 4), r(v1[1], 4)], "label": f"0050: {s1:.2f}%", "color": "1", "width": 2.6},
                    {"to": [r(v2[0], 4), r(v2[1], 4)], "label": f"00679B: {s2:.2f}%", "color": "2", "width": 2.6},
                    {"to": [r(a1[0], 4), r(a1[1], 4)], "color": "1", "dash": True, "width": 1.4},
                    {"to": [r(a2[0], 4), r(a2[1], 4)], "color": "2", "dash": True, "width": 1.4},
                    {"to": [r(mx[0], 4), r(mx[1], 4)], "label": f"42.3/57.7 mix: {math.hypot(*mx):.2f}%",
                     "color": "3", "width": 3}],
        "points": [{"at": [r(5.3 * math.cos(math.radians(74)), 4), r(5.3 * math.sin(math.radians(74)), 4)],
                    "label": f"{deg:.2f}°", "r": 0.01, "color": "var(--muted)", "dx": 2, "dy": 2}]})

    # ---------------------------------------------------------------- angles (Section 5)
    ap = nb.angles_pairs()
    write("lm08-angles", {
        "type": "bar", "height": 300, "valueLabels": True,
        "alt": "Angles between centred vectors of daily returns for six pairs, from 13.0 degrees for 0050 and 00631L "
               "to 96.1 degrees for 0050 and 00679B, against a line at 90 degrees",
        "categories": [p["label"] for p in ap], "x": {"label": "Pair of daily return series"},
        "y": {"fmt": "n1", "tfmt": "n0", "label": "Angle between the centred return vectors, degrees", "min": 0,
              "max": 120, "ticks": [0, 30, 60, 90, 120]},
        "series": [{"name": "Angle θ = arccos ρ", "color": "1", "values": [r(p["deg"], 3) for p in ap]}],
        "ann": [{"type": "hline", "y": 90}]})

    # ---------------------------------------------------------------- week (Section 6)
    write("lm08-week", {
        "type": "heatmap", "fmt": "pct1", "min": -0.1, "max": 0.1, "scaleFmt": "pct0", "valueName": "daily return",
        "alt": "Daily returns of TX, 0050 and 00679B on the five sessions from 7 to 11 April 2025, as a 5 by 3 matrix "
               "with a row per session",
        "rows": days, "cols": nb.INSTRUMENTS,
        "matrix": [[r(v, 8) for v in row] for row in X]})


if __name__ == "__main__":
    main()
