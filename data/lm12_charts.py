"""Chart specs for LM12 (src/data/lm12-*.json), computed from the repaired sector closes.

Run:  uv run python data/lm12_charts.py      (after data/vol2_series.py; data/lm12_numbers.py checks the text)

Inputs: data/processed/vol2_closes.parquet only. Same sample and conventions as data/lm12_numbers.py: closes
2008-12-01 .. 2026-10-08, daily simple returns between consecutive TAIEX-calendar dates (T = 4,382), U28 = the 28
sector indices without the aggregates, fits with an intercept by np.linalg.lstsq, moments with divisor T.
Writes lm12-proj, lm12-coef, lm12-drift, lm12-svd, lm12-rank, lm12-white-raw, lm12-white-z and lm12-weights (the
bar chart that the widget taiexWeights starts from, with every sample's coefficients in its "widget" block).
"""
import json
import math
from pathlib import Path

import numpy as np
import polars as pl
from numpy.typing import NDArray

Vec = NDArray[np.float64]
Mat = NDArray[np.float64]

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)
CLOSES = HERE / "processed" / "vol2_closes.parquet"
AGGREGATES = ["Electronic", "ChemicalBiotechnologyMedicalCare"]
ELEC8 = ["Semiconductor", "ComputerPeripheralEquipment", "Optoelectronic", "CommunicationsInternet",
         "ElectronicPartsComponents", "ElectronicProductsDistribution", "InformationService", "OtherElectronic"]
FIRST_CLOSE, LAST_CLOSE = "2008-12-01", "2026-10-08"

cdf = pl.read_parquet(CLOSES).sort("date").filter(pl.col("date").is_between(pl.lit(FIRST_CLOSE), pl.lit(LAST_CLOSE)))
series_ids = [c for c in cdf.columns if c != "date"]
U28 = [c for c in series_ids if c not in ("TAIEX", *AGGREGATES)]
ret = cdf.with_columns([(pl.col(c) / pl.col(c).shift(1) - 1).alias(c) for c in series_ids]).slice(1)
ret = ret.filter(pl.all_horizontal([pl.col(c).is_not_null() for c in ["TAIEX", *U28]]))
T = ret.height
assert T == 4382 and len(U28) == 28
dates = ret["date"].to_list()
X = np.asarray(ret.select(U28).to_numpy(), dtype=np.float64)
y = ret["TAIEX"].to_numpy().astype(np.float64)
year = np.array([int(d[:4]) for d in dates])
col = {c: i for i, c in enumerate(U28)}


def fit(mask: NDArray[np.bool_]) -> tuple[Vec, float]:
    """Least squares of TAIEX on U28 with an intercept on the dates in mask: coefficients and R-squared."""
    ym, xm = y[mask], X[mask]
    design = np.column_stack([np.ones(len(ym)), xm])
    b = np.linalg.lstsq(design, ym, rcond=None)[0]
    e = ym - design @ b
    yc = ym - ym.mean()
    return b, float(1 - e @ e / (yc @ yc))


def r(v: float, n: int) -> float:
    return round(float(v), n)


def write(name: str, spec: dict) -> None:
    (OUT / f"{name}.json").write_text(json.dumps(spec, ensure_ascii=False, separators=(",", ":"), allow_nan=False),
                                      encoding="utf-8", newline="\n")
    print("wrote", f"src/data/{name}.json")


# ------------------------------------------------------------------ proj: one column, Example "The closest multiple"
proj = {
    "type": "vector", "alt": "The vector y projected on the line of multiples of x: the fitted vector, the orthogonal "
    "residual and a farther candidate",
    "x": {"min": -0.5, "max": 3.6, "label": "first coordinate"}, "y": {"min": -0.5, "max": 3.4},
    "lines": [{"from": [0, 0], "to": [2, 1], "extend": True, "color": "var(--muted)", "label": "multiples of x"}],
    "segments": [{"from": [2, 1], "to": [1, 3], "color": "2"},
                 {"from": [3, 1.5], "to": [1, 3], "color": "var(--muted)"}],
    "vectors": [{"to": [1, 3], "label": "y = (1, 3)", "color": "1"},
                {"to": [2, 1], "label": "x = fitted vector (2, 1)", "color": "3", "dy": 16}],
    "points": [{"at": [1.5, 2], "label": "residual", "color": "2", "r": 3, "dx": 9, "dy": 4},
               {"at": [3, 1.5], "label": "1.5x: distance 2.5", "color": "var(--muted)", "dx": 8, "dy": 14}],
}
write("lm12-proj", proj)

# ------------------------------------------------------------------ coef: last 250, sorted
LAST = np.arange(T) >= T - 250
b_last, r2_last = fit(LAST)
order = [U28[i] for i in np.argsort(-b_last[1:], kind="stable")]
coef = {
    "type": "bar", "alt": "Least-squares coefficients of TAIEX's daily returns on the 28 sector returns, last 250 "
    "returns, sorted from largest to smallest; seven are slightly negative", "height": 320,
    "categories": order, "x": {"label": "Sector index (U28)"},
    "y": {"fmt": "n4", "tfmt": "n1", "label": "Coefficient", "ticks": [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]},
    "series": [{"name": "Coefficient, 25 Sep 2025 to 8 Oct 2026", "color": "1",
                "values": [r(b_last[1 + col[c]], 6) for c in order]}],
    "ann": [{"type": "hline", "y": 0}],
}
write("lm12-coef", coef)

# ------------------------------------------------------------------ drift: four coefficients by calendar year
YEARS = list(range(2009, 2027))
yearly = {yr: fit(year == yr) for yr in YEARS}
four = [("Semiconductor", "Semiconductor", "1"), ("FinancialInsurance", "FinancialInsurance", "2"),
        ("ElectronicPartsComponents", "ElectronicPartsComponents", "3"),
        ("ComputerPeripheralEquipment", "ComputerPeripheralEquipment", "4")]
drift = {
    "alt": "Coefficients of Semiconductor, FinancialInsurance, ElectronicPartsComponents and ComputerPeripheralEquipment "
    "in yearly fits of TAIEX on the 28 sectors, 2009 to 2026", "height": 300,
    "x": {"type": "num", "label": "Calendar year (2026 to 8 October)", "tipLabel": "", "min": 2009, "max": 2026,
          "ticks": [2009, 2011, 2013, 2015, 2017, 2019, 2021, 2023, 2026],
          "tickLabels": ["2009", "2011", "2013", "2015", "2017", "2019", "2021", "2023", "2026"]},
    "y": {"type": "lin", "fmt": "n3", "tfmt": "n1", "label": "Coefficient in the yearly fit", "min": 0, "max": 0.6,
          "ticks": [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]},
    "series": [{"name": nm, "color": c, "x": YEARS, "y": [r(yearly[yr][0][1 + col[sid]], 6) for yr in YEARS]}
               for sid, nm, c in four],
}
write("lm12-drift", drift)

# ------------------------------------------------------------------ svd: the unit circle and its image under M
M = np.array([[4.0, 4.0], [-2.0, 4.0]])
s5 = math.sqrt(5)
v1, v2 = np.array([1.0, 2.0]) / s5, np.array([2.0, -1.0]) / s5
u1, u2 = M @ v1 / 6, M @ v2 / 4
assert np.allclose(u1, np.array([2, 1]) / s5) and np.allclose(u2, np.array([1, -2]) / s5)
mmt = M @ M.T
svd = {
    "type": "vector", "alt": "The unit circle and its image under M, an ellipse with semi-axes 6 and 4; the right "
    "singular vectors v1 and v2 map to the axes s1 u1 and s2 u2", "height": 400,
    "x": {"min": -6.5, "max": 6.5}, "y": {"min": -6.5, "max": 6.5},
    "ellipses": [{"center": [0, 0], "cov": [[1, 0], [0, 1]], "color": "var(--muted)", "label": "unit circle"},
                 {"center": [0, 0], "cov": [[float(mmt[0, 0]), float(mmt[0, 1])], [float(mmt[1, 0]), float(mmt[1, 1])]],
                  "color": "3", "label": "image of the circle"}],
    "vectors": [{"to": [r(v1[0], 4), r(v1[1], 4)], "label": "v_1", "color": "1"},
                {"to": [r(v2[0], 4), r(v2[1], 4)], "label": "v_2", "color": "1", "dy": 14},
                {"to": [r(6 * u1[0], 4), r(6 * u1[1], 4)], "label": "s_1 u_1", "color": "2"},
                {"to": [r(4 * u2[0], 4), r(4 * u2[1], 4)], "label": "s_2 u_2", "color": "2"}],
}
write("lm12-svd", svd)

# ------------------------------------------------------------------ rank: standardized singular values, Electronic + eight
e9 = np.asarray(ret.select(["Electronic", *ELEC8]).to_numpy(), dtype=np.float64)


def std_ratios(mask: NDArray[np.bool_]) -> Vec:
    z = e9[mask] - e9[mask].mean(axis=0)
    z = z / z.std(axis=0)
    s = np.linalg.svd(z / math.sqrt(int(mask.sum())), compute_uv=False)
    return s / s[0]


full_r, y2016_r = std_ratios(np.ones(T, dtype=bool)), std_ratios(year == 2016)
ks = list(range(1, 10))
rank_spec = {
    "alt": "Singular values of the standardized returns of Electronic and its eight sub-industries relative to the "
    "largest, full sample and 2016, on a log scale, with the tolerance 0.01", "height": 300,
    "x": {"type": "num", "label": "k", "tipLabel": "k = ", "min": 1, "max": 9, "ticks": ks},
    "y": {"type": "log", "label": "s_k / s_1 (log scale)", "min": 0.002, "max": 1, "ticks": [0.002, 0.01, 0.1, 1]},
    "series": [{"name": "Full sample, 2008–2026", "color": "1", "x": ks, "y": [r(v, 6) for v in full_r], "fmt": "n5"},
               {"name": "Calendar 2016", "color": "2", "x": ks, "y": [r(v, 6) for v in y2016_r], "fmt": "n5"}],
    "ann": [{"type": "hline", "y": 0.01, "label": "tolerance δ = 0.01"}],
}
write("lm12-rank", rank_spec)

# ------------------------------------------------------------------ white: Semiconductor and FinancialInsurance, raw and whitened
pair = ["Semiconductor", "FinancialInsurance"]
xp = X[:, [col[c] for c in pair]]
xpc = xp - xp.mean(axis=0)
sig2 = xpc.T @ xpc / T
L2 = np.linalg.cholesky(sig2)
z2 = np.linalg.solve(L2, xpc.T).T
S5 = ["Semiconductor", "FinancialInsurance", "Food", "Plastics", "ShippingTransportation"]
i5 = [col[c] for c in S5]
x5c = X[:, i5] - X[:, i5].mean(axis=0)
z5 = np.linalg.solve(np.linalg.cholesky(x5c.T @ x5c / T), x5c.T).T
assert np.allclose(z5[:, :2], z2, atol=1e-10), "the pair's z is not the first two entries of S5's z"
i7 = dates.index("2025-04-07")
pct = 100 * xpc
white_raw = {
    "type": "scatter", "equal": True, "alt": "Centred daily returns of Semiconductor against FinancialInsurance, "
    "4,382 days, with the tilted ellipse on which the squared whitened length is 9; 7 April 2025 lies far outside",
    "height": 440,
    "x": {"label": "Semiconductor, centred (% a day)", "fmt": "n2", "tfmt": "n0", "name": "Semiconductor",
          "min": -11, "max": 11},
    "y": {"label": "FinancialInsurance, centred (% a day)", "fmt": "n2", "tfmt": "n0", "name": "FinancialInsurance",
          "min": -11, "max": 9},
    "series": [{"name": "Daily returns, centred", "color": "1", "r": 1.6,
                "x": [r(v, 2) for v in pct[:, 0]], "y": [r(v, 2) for v in pct[:, 1]]}],
    "ellipses": [{"center": [0, 0], "cov": [[r(1e4 * sig2[0, 0], 6), r(1e4 * sig2[0, 1], 6)],
                                            [r(1e4 * sig2[1, 0], 6), r(1e4 * sig2[1, 1], 6)]],
                  "scale": 3, "color": "2", "label": "squared whitened length 9"}],
    "points": [{"at": [r(pct[i7, 0], 3), r(pct[i7, 1], 3)], "label": "7 Apr 2025", "color": "2", "dx": 8, "dy": -6}],
}
write("lm12-white-raw", white_raw)
white_z = {
    "type": "scatter", "equal": True, "alt": "Whitened returns of the same two sectors: an uncorrelated round cloud "
    "with the circle of radius 3; 7 April 2025 lies far outside", "height": 440,
    "x": {"label": "z_1 (whitened Semiconductor)", "fmt": "n2", "tfmt": "n0", "name": "z_1", "min": -8, "max": 8},
    "y": {"label": "z_2 (whitened FinancialInsurance)", "fmt": "n2", "tfmt": "n0", "name": "z_2", "min": -7, "max": 7},
    "series": [{"name": "Whitened returns", "color": "1", "r": 1.6,
                "x": [r(v, 2) for v in z2[:, 0]], "y": [r(v, 2) for v in z2[:, 1]]}],
    "ellipses": [{"center": [0, 0], "cov": [[1, 0], [0, 1]], "scale": 3, "color": "2", "label": "circle of radius 3"}],
    "points": [{"at": [r(z2[i7, 0], 3), r(z2[i7, 1], 3)], "label": "7 Apr 2025", "color": "2", "dx": 8, "dy": -6}],
}
write("lm12-white-z", white_z)

# ------------------------------------------------------------------ weights: the widget's data and its initial chart
samples: dict[str, tuple[NDArray[np.bool_], str]] = {str(yr): (year == yr, str(yr) if yr < 2026 else "2026 (to 8 Oct)")
                                                     for yr in YEARS}
samples["last250"] = (LAST, "Last 250 returns")
samples["full"] = (np.ones(T, dtype=bool), "Full sample, 2008–2026")
block = {"order": order, "samples": {}}
for key, (mask, label) in samples.items():
    b, r2 = fit(mask)
    block["samples"][key] = {"label": label, "T": int(mask.sum()), "first": dates[int(np.flatnonzero(mask)[0])],
                             "last": dates[int(np.flatnonzero(mask)[-1])], "r2": r(r2, 8), "sum": r(b[1:].sum(), 6),
                             "alpha": r(b[0], 8), "coef": [r(b[1 + col[c]], 6) for c in order]}
weights = {
    "type": "bar", "alt": "The 28 coefficients of TAIEX's yearly fits on the sector returns in two samples, 2009 and "
    "2026, side by side", "height": 330,
    "categories": order, "x": {"label": "Sector index (U28), in the order of the last-250 fit"},
    "y": {"fmt": "n4", "tfmt": "n1", "label": "Coefficient"},
    "series": [{"name": block["samples"][k]["label"], "color": c, "values": block["samples"][k]["coef"]}
               for k, c in (("2009", "1"), ("2026", "2"))],
    "ann": [{"type": "hline", "y": 0}],
    "widget": block,
}
write("lm12-weights", weights)
print(f"coef: R-squared {r2_last:.5f}, {sum(1 for v in coef['series'][0]['values'] if v < 0)} negative; "
      f"rank chart: full s9/s1 {full_r[-1]:.5f}, 2016 {y2016_r[-1]:.5f}; 7 April 2025 z = ({z2[i7, 0]:.3f}, {z2[i7, 1]:.3f})")
