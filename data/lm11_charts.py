"""Chart specs for LM11 (src/data/lm11-*.json), computed from the repaired sector closes and LM7's ETF returns.

Run after data/vol2_series.py and data/lm07_series.py:  uv run python data/lm11_charts.py
Conventions as in data/lm11_common.py; the numbers the text quotes are printed and checked by data/lm11_numbers.py.
Values are rounded before they are written, so two runs write identical files.
"""
import json
import math

import numpy as np
from lm11_common import (
    ELEC8,
    HERE,
    closes,
    corr,
    cov0,
    eig_desc,
    lm07_pair,
    returns,
    sector_names,
)

OUT = HERE.parent / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)


def r(v: float, n: int = 6) -> float:
    """Round for the JSON (no -0.0)."""
    x = round(float(v), n)
    return 0.0 if x == 0 else x


df = closes()
ALL30, U28 = sector_names(df)
assert "Electronic" in ALL30 and all(e in U28 for e in ELEC8)
dates, R = returns(df, U28)
T, N = R.shape
S = cov0(R)
C = corr(S)
lam, Q = eig_desc(C)
specs: dict[str, dict] = {}

# ---------------------------------------------------------------- the unit circle and its image (Semiconductor, Fin.)
_, RSF = returns(df, ["Semiconductor", "FinancialInsurance"])
M = cov0(RSF) * 1e4
wM, QM = eig_desc(M)
Me1 = M @ np.array([1.0, 0.0])
specs["lm11-stretch"] = {
    "type": "vector", "alt": "The unit circle and the ellipse it becomes under the covariance matrix of Semiconductor "
    "and FinancialInsurance, with the two eigenvectors that keep their direction",
    "height": 340,
    "x": {"label": "Semiconductor axis (units of 10⁻⁴)", "fmt": "n2", "tfmt": "n0", "name": "x"},
    "y": {"fmt": "n2", "tfmt": "n0", "name": "y"},
    "ellipses": [
        {"center": [0, 0], "cov": [[1, 0], [0, 1]], "color": "var(--muted)", "label": "unit circle"},
        {"center": [0, 0], "cov": [[r(v, 6) for v in row] for row in (M @ M)], "color": "1", "fill": True,
         "axes": True},
    ],
    "vectors": [
        {"to": [r(wM[0] * QM[0, 0], 4), r(wM[0] * QM[1, 0], 4)], "label": f"Mq_1 = {wM[0]:.4f} q_1", "color": "1"},
        {"to": [r(wM[1] * QM[0, 1], 4), r(wM[1] * QM[1, 1], 4)], "label": f"Mq_2 = {wM[1]:.4f} q_2", "color": "2"},
        {"to": [1, 0], "label": "e_1", "color": "var(--muted)", "width": 1.5},
        {"to": [r(Me1[0], 4), r(Me1[1], 4)], "label": "Me_1", "color": "4", "width": 1.5, "dash": True},
    ],
}

# ---------------------------------------------------------------- LM7's daily returns and the one-sd ellipse
r50, r679, _ = lm07_pair()
S7 = cov0(np.column_stack([r50, r679]))
w7, Q7 = eig_desc(S7)
# Equal scales, so that the two axes of the ellipse look perpendicular. The window holds the ellipse and most days;
# days with larger moves (such as 7 April 2025) fall outside it and are not drawn (the exhibit note says so).
# book.js draws an `ellipses` entry under the points, where 2,363 points hide it, so the outline and the two axes are
# also drawn as a second series of closely spaced points, on top of the cloud.
mu = np.array([r50.mean(), r679.mean()])
half = Q7 @ np.diag(np.sqrt(w7))                               # columns: the two half-axes sqrt(lambda_k) q_k
ring = [mu + half @ np.array([math.cos(t), math.sin(t)]) for t in np.linspace(0, 2 * math.pi, 151)[:-1]]
ticks = np.linspace(-1, 1, 25)
axes_pts = [mu + s_ * half[:, k] for k in range(2) for s_ in ticks]
outline = ring + axes_pts
specs["lm11-lm7cloud"] = {
    "type": "scatter", "equal": True, "alt": "Scatter of the daily total returns of 0050 against 00679B with the "
    "one-standard-deviation ellipse of their sample covariance matrix and its two axes",
    "height": 300,
    "x": {"label": "0050 daily total return", "fmt": "pct2", "tfmt": "pct0", "name": "0050", "min": -0.04, "max": 0.04},
    "y": {"fmt": "pct2", "tfmt": "pct0", "name": "00679B", "label": "00679B daily total return", "min": -0.02,
          "max": 0.02},
    "series": [{"name": "Daily returns, 2017–2026", "color": "var(--muted)", "r": 1.3,
                "x": [r(v, 5) for v in r50], "y": [r(v, 5) for v in r679]},
               {"name": "One-standard-deviation ellipse and its axes", "color": "1", "r": 2.2,
                "x": [r(p[0], 6) for p in outline], "y": [r(p[1], 6) for p in outline]}],
    "ellipses": [{"center": [r(mu[0], 6), r(mu[1], 6)], "cov": [[r(v, 9) for v in row] for row in S7],
                  "color": "1", "fill": True}],
}
outside = int(((np.abs(r50) > 0.04) | (np.abs(r679) > 0.02)).sum())

# ---------------------------------------------------------------- variance in every direction (Semiconductor, Fin.)
deg = list(range(181))
hu = []
for d in deg:
    u = np.array([math.cos(math.radians(d)), math.sin(math.radians(d))])
    hu.append(r(u @ M @ u, 5))
th1 = math.degrees(math.atan2(QM[1, 0], QM[0, 0]))
specs["lm11-rayleigh"] = {
    "alt": "Variance of the Semiconductor and FinancialInsurance mix in direction theta, from 0 to 180 degrees, with "
    "its maximum and minimum at the two eigenvalues", "height": 260,
    "x": {"type": "num", "fmt": "n0", "label": "Angle θ of u from the Semiconductor axis (degrees)", "tipLabel": "θ = ",
          "min": 0, "max": 180, "ticks": [0, 30, 60, 90, 120, 150, 180]},
    "y": {"type": "lin", "fmt": "n4", "tfmt": "n1", "label": "h(u), variance in direction u (units of 10⁻⁴)",
          "min": 0, "max": 3.5},
    "series": [{"name": "h(u)", "color": "1", "x": deg, "y": hu}],
    "ann": [{"type": "hline", "y": r(wM[0], 4), "label": f"λ₁ = {wM[0]:.4f}"},
            {"type": "hline", "y": r(wM[1], 4), "label": f"λ₂ = {wM[1]:.4f}"},
            {"type": "point", "x": r(th1, 2), "y": r(wM[0], 4), "color": "1", "label": f"{th1:.1f}°", "dx": 8,
             "dy": 16},
            {"type": "point", "x": r(th1 + 90, 2), "y": r(wM[1], 4), "color": "2", "label": f"{th1 + 90:.1f}°",
             "dx": 8, "dy": -8}],
}

# ---------------------------------------------------------------- scree and loadings (U28, correlation PCA)
specs["lm11-scree"] = {
    "type": "bar", "alt": "Explained shares of the 28 principal components of the U28 correlation matrix",
    "height": 250, "categories": [str(k) for k in range(1, N + 1)],
    "x": {"label": "Component k"},
    "y": {"fmt": "pct2", "tfmt": "pct0", "label": "Explained share λ_k / 28", "min": 0, "max": 0.55},
    "series": [{"name": "Explained share", "color": "1", "values": [r(v / N, 6) for v in lam]}],
    "ann": [{"type": "hline", "y": r(1 / N, 6), "label": "1/28 = 3.57%"}],
}
order = np.argsort(-Q[:, 1], kind="stable")
specs["lm11-loadings"] = {
    "type": "bar", "alt": "Loadings of the first two principal components of U28 for the 28 sectors, sorted by the "
    "second component's loading",
    "height": 300, "categories": [U28[i] for i in order],
    "y": {"fmt": "n3", "tfmt": "n1", "label": "Loading (entry of q_1 or q_2)"},
    "series": [{"name": "PC1 loading", "color": "1", "values": [r(Q[i, 0], 4) for i in order]},
               {"name": "PC2 loading", "color": "2", "values": [r(Q[i, 1], 4) for i in order]}],
}

# ---------------------------------------------------------------- per calendar year
yr = np.array([int(d[:4]) for d in dates])
years = list(range(2009, 2027))
ycats = [str(y) if y < 2026 else "2026 to Oct" for y in years]
ysh, yc1, yc2, ypl = [], [], [], []
for y in years:
    wy, Qy = eig_desc(corr(cov0(R[yr == y])))
    ysh.append(r(wy[0] / N, 6))
    yc1.append(r(abs(float(Qy[:, 0] @ Q[:, 0])), 4))
    yc2.append(r(abs(float(Qy[:, 1] @ Q[:, 1])), 4))
    ypl.append(r(math.hypot(Q[:, 1] @ Qy[:, 1], Q[:, 2] @ Qy[:, 1]), 4))
specs["lm11-yshare"] = {
    "type": "bar", "alt": "Share of the first principal component of each calendar year's U28 correlation matrix, "
    "2009 to 2026", "height": 260, "categories": ycats, "valueLabels": True,
    "y": {"fmt": "pct1", "tfmt": "pct0", "label": "First component's share λ_1 / 28", "min": 0, "max": 0.75},
    "series": [{"name": "Share of PC1", "color": "1", "values": ysh}],
    "ann": [{"type": "hline", "y": r(lam[0] / N, 6), "label": f"{lam[0] / N:.1%}"}],
}
specs["lm11-ycos"] = {
    "type": "bar", "alt": "For each calendar year, the absolute cosine of the year's first and second principal "
    "components with the full sample's, and the plane measure of the second", "height": 270, "categories": ycats,
    "y": {"fmt": "n3", "tfmt": "n1", "label": "Absolute cosine with the full sample", "min": 0, "max": 1},
    "series": [{"name": "|cos θ_1|", "color": "1", "values": yc1},
               {"name": "|cos θ_2|", "color": "2", "values": yc2},
               {"name": "plane measure of q_2", "color": "3", "values": ypl}],
}

# ---------------------------------------------------------------- shares of ||x||^2 by component, two halves
h = T // 2
xs_series = []
for name, col, part in (("First half", "1", R[:h]), ("Second half", "2", R[h:])):
    Sh = cov0(part)
    wh, Qh = eig_desc(Sh)
    xh = np.linalg.solve(Sh, np.ones(N))
    cs = (Qh.T @ np.ones(N) / wh) ** 2 / float(xh @ xh)
    assert abs(cs.sum() - 1) < 1e-9
    xs_series.append({"name": name, "color": col, "values": [r(v, 6) for v in cs]})
specs["lm11-xshares"] = {
    "type": "bar", "alt": "Share of the squared length of the solution of Sigma x = 1 contributed by each of the 28 "
    "components, in the two halves of the sample", "height": 260,
    "categories": [str(k) for k in range(1, N + 1)], "x": {"label": "Component k (1 = largest eigenvalue)"},
    "y": {"fmt": "pct1", "tfmt": "pct0", "label": "Share of the squared length of x"},
    "series": xs_series,
}

for name, spec in specs.items():
    (OUT / f"{name}.json").write_text(json.dumps(spec, ensure_ascii=True, allow_nan=False), encoding="utf-8",
                                      newline="\n")
    print("wrote", f"src/data/{name}.json")
print(f"stretch: lambda {wM.round(4).tolist()}, angle of q1 {th1:.2f} deg, M e1 {Me1.round(4).tolist()}")
print(f"lm7cloud: {len(r50)} points; x range {r50.min():.4f}..{r50.max():.4f}, y range {r679.min():.4f}..{r679.max():.4f}; "
      f"daily half-axes {math.sqrt(w7[0]):.5f}, {math.sqrt(w7[1]):.5f}; days outside the 4% x 2% window: {outside} "
      "(a wide screen shows a wider 0050 range)")
print(f"yshare min {min(ysh):.4f} max {max(ysh):.4f}; ycos PC1 min {min(yc1):.4f}; PC2 {min(yc2):.4f}..{max(yc2):.4f}; "
      f"plane {min(ypl):.4f}..{max(ypl):.4f}")
print("xshares PC1:", [s_["values"][0] for s_ in xs_series])
