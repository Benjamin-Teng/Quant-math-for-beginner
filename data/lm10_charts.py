"""Chart specs for LM10 (src/data/lm10-*.json), computed from the repaired sector closes and the ETF files.

Run after data/vol2_series.py:  uv run python data/lm10_charts.py

Writes lm10-vols (bar), lm10-levels (vector), lm10-corr (heatmap), lm10-rank (bar), lm10-admissible (vector) and
lm10-gradient (vector). Values are rounded before they are written, so two runs write identical files.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lm10_series import ETFS, S3, cov0, one_session, u28

OUT = Path(__file__).resolve().parents[1] / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)


def r(x: float, d: int = 6) -> float:
    v = round(float(x), d)
    return 0.0 if v == 0 else v                                          # never -0.0


smp = u28()
X, names, T, A = smp.X, smp.names, smp.X.shape[0], smp.A
S = cov0(X)
s = np.sqrt(np.diag(S))
vol = s * math.sqrt(A)
order = [int(k) for k in np.argsort(vol)]
w = np.full(28, 1 / 28)
book = math.sqrt(A * float(w @ S @ w))
var_only = math.sqrt(A * float(np.sum(w**2 * s**2)))
specs: dict[str, dict] = {}

# ------------------------------------------------------------------ lm10-vols: the case
specs["lm10-vols"] = {
    "type": "bar", "height": 340,
    "alt": f"Annualized volatility of the 28 sector indices of U28, 2008 to 2026, sorted from {vol[order[0]]:.2%} to "
           f"{vol[order[-1]]:.2%}, with lines at their mean {vol.mean():.2%}, the equal-weight book {book:.2%} and its "
           f"variance terms alone {var_only:.2%}",
    "categories": [names[k] for k in order],
    "x": {"label": "Sector index, from the least to the most volatile"},
    "y": {"fmt": "pct2", "tfmt": "pct0", "label": "Annualized volatility of daily price returns, 2008-12-02 to 2026-10-08",
          "min": 0, "max": 0.4, "ticks": [0, 0.1, 0.2, 0.3, 0.4]},
    "series": [{"name": "Annualized volatility", "color": "1", "values": [r(vol[k]) for k in order]}],
    "ann": [{"type": "hline", "y": r(vol.mean()), "label": f"mean of the 28: {vol.mean():.2%}"},
            {"type": "hline", "y": r(book), "label": f"equal-weight book: {book:.2%}"},
            {"type": "hline", "y": r(var_only), "label": f"its variance terms alone: {var_only:.2%}"}],
}

# ------------------------------------------------------------------ lm10-levels: three level sets h(x) = 1
lv_lines = [{"from": [-3.5, 4.5], "to": [4.5, -3.5], "extend": True, "color": "2", "width": 2,
             "label": "off-diagonal 1: two lines"},
            {"from": [-4.5, 3.5], "to": [3.5, -4.5], "extend": True, "color": "2", "width": 2}]
# hyperbola x1^2 + 4 x1 x2 + x2^2 = 1: with u = (x1 + x2)/sqrt2, v = (x1 - x2)/sqrt2 it reads 3u^2 - v^2 = 1
vs = np.linspace(-4.0, 4.0, 81)
for sign in (1, -1):
    pts = [((sign * math.sqrt((1 + v * v) / 3) + v) / math.sqrt(2), (sign * math.sqrt((1 + v * v) / 3) - v) / math.sqrt(2))
           for v in vs]
    for k in range(len(pts) - 1):
        seg = {"from": [r(pts[k][0], 4), r(pts[k][1], 4)], "to": [r(pts[k + 1][0], 4), r(pts[k + 1][1], 4)], "color": "3",
               "width": 2}
        if sign == 1 and k == 60:
            seg["label"] = "off-diagonal 2: hyperbola"
        lv_lines.append(seg)
pd_inv = np.linalg.inv(np.array([[1.0, 0.5], [0.5, 1.0]]))               # the contour x'K^-1 x = 1 with K = M^-1
for x1, x2 in ((1.0, 0.0), (0.0, 1.0)):                                    # sanity: points on each level set
    assert abs(x1 * x1 + x1 * x2 + x2 * x2 - 1) < 1e-12
specs["lm10-levels"] = {
    "type": "vector", "height": 380,
    "alt": "Level curves h(x) = 1 of three quadratic forms with diagonal entries 1: an ellipse for off-diagonal 0.5, "
           "two parallel lines for off-diagonal 1 and a hyperbola for off-diagonal 2",
    "x": {"label": "x_1", "fmt": "n2", "min": -2.5, "max": 2.5, "name": "x_1"},
    "y": {"label": "x_2", "fmt": "n2", "min": -2.5, "max": 2.5, "name": "x_2"},
    "ellipses": [{"center": [0, 0], "cov": [[r(pd_inv[0, 0]), r(pd_inv[0, 1])], [r(pd_inv[1, 0]), r(pd_inv[1, 1])]],
                  "scale": 1, "color": "1", "label": "off-diagonal 0.5: ellipse"}],
    "lines": lv_lines,
}

# ------------------------------------------------------------------ lm10-corr: the U28 correlation matrix
C = S / np.outer(s, s)
offd = ~np.eye(28, dtype=bool)
specs["lm10-corr"] = {
    "type": "heatmap",
    "alt": "Correlation matrix of the 28 sector indices, ordered from the least to the most volatile; every "
           f"correlation is positive, from {C[offd].min():.3f} to {C[offd].max():.3f}",
    "labels": [names[k] for k in order],
    "matrix": [[r(C[i, j], 2) for j in order] for i in order],
    "fmt": "n2", "min": -1, "max": 1, "valueName": "correlation",
}

# ------------------------------------------------------------------ lm10-rank: rank against the number of returns
ranks = [int(np.linalg.matrix_rank(cov0(X[-t:]))) for t in range(20, 36)]
assert ranks == [min(t - 1, 28) for t in range(20, 36)]
specs["lm10-rank"] = {
    "type": "bar", "height": 300, "valueLabels": True,
    "alt": "Rank of the 28 by 28 sample covariance matrix on the latest T returns, T from 20 to 35: T minus 1 up to "
           "T = 29, then 28",
    "categories": [str(t) for t in range(20, 36)],
    "x": {"label": "Number of latest returns T"},
    "y": {"fmt": "n0", "label": "Rank of the 28 × 28 sample covariance matrix", "min": 0, "max": 32,
          "ticks": [0, 5, 10, 15, 20, 25, 30]},
    "series": [{"name": "Rank", "color": "1", "values": ranks}],
    "ann": [{"type": "hline", "y": 28}],                                   # N = 28, named in the exhibit note
}

# ------------------------------------------------------------------ lm10-admissible: the constructed example
etf = {e: one_session(e, smp.calendar) for e in ETFS}
d18 = [d for d in sorted(set(etf["0050"]) & set(etf["00631L"]) & set(etf["00679B"])) if d.startswith("2018")]
C18 = np.corrcoef(np.array([[etf[e][d] for e in ETFS] for d in d18]).T)
p18 = [r(C18[0, 2], 3), r(C18[1, 2], 3)]
assert p18 == [-0.394, -0.395]
rho12 = 0.982
square = [[[-1, -1], [1, -1]], [[1, -1], [1, 1]], [[1, 1], [-1, 1]], [[-1, 1], [-1, -1]]]
specs["lm10-admissible"] = {
    "type": "vector", "height": 360,
    "alt": "The pairs of correlations rho13 and rho23 for which the pairwise 3 by 3 correlation matrix with "
           "rho12 = 0.982 is positive semidefinite fill a thin ellipse along the diagonal; the 2018 common-sample "
           "point lies inside, the constructed point outside",
    "x": {"label": "ρ_{13}, 0050 / 00679B", "fmt": "n3", "min": -1.1, "max": 1.1, "name": "ρ_{13}"},
    "y": {"label": "ρ_{23}, 00631L / 00679B", "fmt": "n3", "min": -1.1, "max": 1.1, "name": "ρ_{23}"},
    "ellipses": [{"center": [0, 0], "cov": [[1, rho12], [rho12, 1]], "scale": 1, "color": "1", "fill": True,
                  "label": "det C_{pw} ≥ 0 when ρ_{12} = 0.982"}],
    "segments": [{"from": a, "to": b, "color": "var(--muted)", "width": 1} for a, b in square],
    "points": [{"at": p18, "label": "2018, common dates", "color": "1"},
               {"at": [0.199, -0.444], "label": "constructed", "color": "2"}],
}

# ------------------------------------------------------------------ lm10-gradient: gradients and level sets
i3 = [names.index(n) for n in S3]
AS3 = 1e4 * A * S[np.ix_(i3, i3)]
P3 = np.round(AS3, 2)                                                      # the matrix as printed in Section 2
M = np.array([[P3[0, 0], P3[0, 2]], [P3[0, 2], P3[2, 2]]]) / 1e4            # Semiconductor and Food, decimal units
Minv = np.linalg.inv(M)
SCALE = 4                                                                   # arrows drawn at four times 2Mw
pts = [np.array([0.15 / math.sqrt(M[0, 0]), 0.0]), np.array([0.0, 0.15 / math.sqrt(M[1, 1])])]
dvec = np.array([1.0, 1.0])
pts.append(dvec * 0.15 / math.sqrt(float(dvec @ M @ dvec)))
vectors, segments, points = [], [], []
for k, p in enumerate(pts):
    assert abs(math.sqrt(float(p @ M @ p)) - 0.15) < 1e-12               # on the 15% ellipse
    g = 2 * M @ p
    tip = p + SCALE * g
    tan = np.array([-g[1], g[0]]) / np.linalg.norm(g)
    assert abs(float(tan @ g)) < 1e-15                                    # tangent is perpendicular to the gradient
    vectors.append({"from": [r(p[0], 4), r(p[1], 4)], "to": [r(tip[0], 4), r(tip[1], 4)], "color": "2",
                    **({"label": "2Mw"} if k == 2 else {})})
    segments.append({"from": [r(p[0] - 0.3 * tan[0], 4), r(p[1] - 0.3 * tan[1], 4)],
                     "to": [r(p[0] + 0.3 * tan[0], 4), r(p[1] + 0.3 * tan[1], 4)], "color": "var(--ink-2)", "width": 1.5})
    points.append({"at": [r(p[0], 4), r(p[1], 4)], "color": "var(--ink)", "r": 3.5})
specs["lm10-gradient"] = {
    "type": "vector", "height": 380,
    "alt": "Two level ellipses of portfolio variance for Semiconductor and Food, at 10% and 15% volatility, with "
           "gradient arrows at three points on the outer ellipse, each perpendicular to it",
    "x": {"label": "w_1, weight in Semiconductor", "fmt": "n2", "name": "w_1"},
    "y": {"label": "w_2, weight in Food", "fmt": "n2", "name": "w_2"},
    "ellipses": [{"center": [0, 0], "cov": [[r(Minv[0, 0]), r(Minv[0, 1])], [r(Minv[1, 0]), r(Minv[1, 1])]],
                  "scale": 0.10, "color": "3", "label": "volatility 10%"},
                 {"center": [0, 0], "cov": [[r(Minv[0, 0]), r(Minv[0, 1])], [r(Minv[1, 0]), r(Minv[1, 1])]],
                  "scale": 0.15, "color": "1", "label": "volatility 15%", "dx": -70}],
    "segments": segments,
    "vectors": vectors,
    "points": points,
}

for name, spec in specs.items():
    (OUT / f"{name}.json").write_text(json.dumps(spec, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8",
                                      newline="\n")
    print("wrote", f"src/data/{name}.json")
print(f"vols: {vol[order[0]]:.4%} .. {vol[order[-1]]:.4%}; book {book:.4%}; variances only {var_only:.4%}")
print("ranks", dict(zip(range(20, 36), ranks)))
print("gradient points", [p.round(4).tolist() for p in pts])
