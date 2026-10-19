"""Chart specs for LM22 (src/data/lm22-*.json), computed from TR23 and from the module's resampling experiments.

Run:  uv run python data/lm22_charts.py      (after data/vol3_series.py; data/lm22_numbers.py checks the text)

Inputs (data/lm22_common.py): data/processed/vol3_taiex.parquet (TR23). Same conventions and seeds as
data/lm22_numbers.py, each generator created once as np.random.default_rng([e, 20261011]): experiments 2 and 3 (iid and
stationary resamples, B = 10,000), 4 (the block-length grid, B = 2,000 per length), 7 (two resampled paths) and 24
(the widget: for each length of 1, 2, 3, 5, 10, 20, 50, 100, 145, 200, 400 in order, three replicates of 1,000
resamples; length 1 is iid days). SciPy's BCa interval of the Kelly fraction re-creates experiment 2's stream.
Writes lm22-srhist (X2), lm22-kelly (X3, the forest plot), lm22-destroy (X4), lm22-rollvol (X5), lm22-ell (X6) and
lm22-widget (the widget's precomputed histograms and readouts, with its initial state as a chart).
No published file carries a TR23 series in date order at full resolution: X5 is thinned to every fifth session plus
each path's extremes, and the widget holds histograms and statistics, not returns.
"""
import json

import lm22_common as C
import numpy as np
from scipy import stats

OUT = C.ROOT / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)
D, OBS, B = C.D, C.OBS, C.B


def write(name: str, spec: dict) -> None:
    assert spec.get("alt"), name
    blob = json.dumps(spec, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    assert len(blob.encode("utf-8")) < 300_000, (name, len(blob))
    (OUT / f"{name}.json").write_text(blob, encoding="utf-8", newline="\n")
    print(f"wrote src/data/{name}.json ({len(blob.encode('utf-8')):,} bytes)")


def rd(v: float, n: int) -> float:
    return round(float(v), n)


def hist(v: np.ndarray, lo: float, width: float, nbins: int) -> tuple[list[float], list[int]]:
    """Counts on nbins bins [lo + k width, lo + (k + 1) width); every value must fall inside."""
    edges = [round(lo + width * i, 6) for i in range(nbins + 1)]
    assert v.min() >= edges[0] and v.max() < edges[-1], (v.min(), v.max(), edges[0], edges[-1])
    k = np.floor((v - lo) / width).astype(int)
    counts = np.bincount(k, minlength=nbins)
    assert counts.size == nbins and counts.sum() == v.size
    return edges, [int(c) for c in counts]


IID = C.exp_tr(2, "iid", 1)
SB = C.exp_tr(3, "sb", C.ELL)
S = {k: (C.summ(IID[k], OBS[k]), C.summ(SB[k], OBS[k])) for k in ("SR", "Kelly", "acf", "fx", "vol", "VR20")}

# ------------------------------------------------------------------ X2 srhist: resampled Sharpe ratios
edges, ci_ = hist(IID["SR"], -0.25, 0.05, 44)
_, cb_ = hist(SB["SR"], -0.25, 0.05, 44)
si, sb = S["SR"]
srhist = {
    "alt": "Histograms of TR23's annual Sharpe ratio on 10,000 resamples of iid days and on 10,000 stationary-block "
    "resamples of mean length 145: both centred near the estimate 0.81, the block histogram slightly wider, with "
    "percentile intervals 0.41 to 1.21 and 0.37 to 1.27",
    "height": 300,
    "x": {"type": "num", "fmt": "n2", "tipLabel": "Sharpe ratio from ", "label": "Annual Sharpe ratio of a resample",
          "min": -0.25, "max": 1.95, "ticks": [0, 0.5, 1, 1.5]},
    "y": {"type": "lin", "fmt": "pct1", "tfmt": "pct0", "label": "Share of resamples per bin of 0.05", "min": 0},
    "series": [{"name": "iid days", "color": "1", "step": True, "x": edges, "y": [rd(c / B, 4) for c in ci_]},
               {"name": "Blocks of mean length 145", "color": "2", "step": True, "x": edges,
                "y": [rd(c / B, 4) for c in cb_]}],
    "ann": [{"type": "vline", "x": rd(OBS["SR"], 4), "label": "0.81"}]
    + [{"type": "vline", "x": rd(v, 4), "dash": True} for v in (si.lo, si.hi, sb.lo, sb.hi)],
}
write("lm22-srhist", srhist)

# ------------------------------------------------------------------ X3 kelly: the forest plot
z975 = float(stats.norm.ppf(0.975))
SR, skew, kurt = D.Rb / D.s, D.skew, D.kurt
se_k = (1 - 2 * SR * skew + SR**2 * (kurt - 1)) ** 0.5 / (D.s * D.T**0.5)
bca = stats.bootstrap((D.R,), lambda x, axis=-1: x.mean(axis=axis) / x.var(axis=axis), n_resamples=B,
                      batch=C.CHUNK, vectorized=True, method="BCa", rng=C.gen(2))
assert np.allclose(bca.bootstrap_distribution, IID["Kelly"], rtol=0, atol=1e-12)
ki, kb = S["Kelly"]
fi, fb = S["fx"]
KEL, FX = OBS["Kelly"], OBS["fx"]
rows = [  # top to bottom: label, estimate, low, high, colour (3 delta, 1 iid, 2 blocks), printed digits
    ("Delta method (LM20)", KEL, KEL - z975 * se_k, KEL + z975 * se_k, "3", 2),
    ("iid, percentile", KEL, ki.lo, ki.hi, "1", 1),
    ("iid, basic", KEL, ki.blo, ki.bhi, "1", 1),
    ("iid, BCa (SciPy)", KEL, float(bca.confidence_interval.low), float(bca.confidence_interval.high), "1", 1),
    ("blocks, percentile", KEL, kb.lo, kb.hi, "2", 1),
    ("blocks, basic", KEL, kb.blo, kb.bhi, "2", 1),
    ("exact optimum, iid", FX, fi.lo, fi.hi, "1", 1),
    ("exact optimum, blocks", FX, fb.lo, fb.hi, "2", 1),
]
ys = list(range(len(rows), 0, -1))
kelly = {
    "type": "scatter",
    "alt": "Forest plot of 95% intervals for TR23's Kelly fraction 4.28: the delta method 2.10 to 6.46; iid resamples, "
    "percentile 2.2 to 6.5, basic 2.1 to 6.4, BCa 2.2 to 6.5; stationary blocks of mean length 145, percentile 1.8 to "
    "7.1, basic 1.5 to 6.7; and for the exact optimum 4.14, 2.1 to 6.1 (iid) and 1.8 to 6.6 (blocks)",
    "height": 330,
    "x": {"label": "Kelly fraction", "fmt": "n2", "tfmt": "n0", "min": 0, "max": 8, "ticks": [0, 2, 4, 6, 8],
          "name": "estimate"},
    "y": {"min": 0.4, "max": len(rows) + 0.6, "ticks": ys[::-1], "tickLabels": [r[0] for r in rows][::-1],
          "fmt": "n0", "name": "interval"},
    "series": [{"name": "estimate", "color": "var(--ink)", "x": [rd(r[1], 4) for r in rows], "y": ys}],
    "lines": [{"from": [rd(r[2], 4), y], "to": [rd(r[3], 4), y], "color": r[4], "width": 2.5,
               "label": f"{r[2]:.{r[5]}f} to {r[3]:.{r[5]}f}"} for r, y in zip(rows, ys, strict=True)]
    + [{"from": [rd(KEL, 4), 0.4], "to": [rd(KEL, 4), len(rows) + 0.6], "dash": True}],
}
printed = ["2.10 to 6.46", "2.2 to 6.5", "2.1 to 6.4", "2.2 to 6.5", "1.8 to 7.1", "1.5 to 6.7", "2.1 to 6.1",
           "1.8 to 6.6"]
assert [ln["label"] for ln in kelly["lines"][:-1]] == printed
write("lm22-kelly", kelly)

# ------------------------------------------------------------------ X4 destroy: the lag-1 autocorrelation of |r|
edges, ci_ = hist(IID["acf"], -0.06, 0.005, 72)
_, cb_ = hist(SB["acf"], -0.06, 0.005, 72)
ai, ab = S["acf"]
destroy = {
    "alt": "Histograms of the lag-1 autocorrelation of absolute log returns on 10,000 iid resamples, centred at 0 "
    "between -0.025 and 0.026, and on 10,000 stationary-block resamples of mean length 145, between 0.10 and 0.21; "
    "TR23's own value, 0.161, lies far outside the iid histogram",
    "height": 300,
    "x": {"type": "num", "fmt": "n3", "tipLabel": "autocorrelation from ", "label": "Lag-1 autocorrelation of |r|",
          "min": -0.06, "max": 0.3, "ticks": [-0.05, 0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3]},
    "y": {"type": "lin", "fmt": "pct1", "tfmt": "pct0", "label": "Share of resamples per bin of 0.005", "min": 0},
    "series": [{"name": "iid days", "color": "1", "step": True, "x": edges, "y": [rd(c / B, 4) for c in ci_]},
               {"name": "Blocks of mean length 145", "color": "2", "step": True, "x": edges,
                "y": [rd(c / B, 4) for c in cb_]}],
    "ann": [{"type": "vline", "x": rd(OBS["acf"], 4), "label": "TR23: 0.161"}]
    + [{"type": "vline", "x": rd(v, 4), "dash": True} for v in (ai.lo, ai.hi, ab.lo, ab.hi)],
}
write("lm22-destroy", destroy)

# ------------------------------------------------------------------ X5 rollvol: one path of each kind (experiment 7)
pi_, ps_ = C.exp7()
paths = [("TR23", C.roll_vol(D.R)), ("iid resample", C.roll_vol(D.R[pi_])),
         ("block resample, mean 145", C.roll_vol(D.R[ps_]))]
n = paths[0][1].size
keep = set(range(0, n, 5)) | {n - 1}
for _, v in paths:
    keep |= {int(v.argmax()), int(v.argmin())}
idx = sorted(keep)
assert len(idx) < n / 4
ycols = [[rd(v[i], 5) for i in idx] for _, v in paths]
for yc, (_, v) in zip(ycols, paths, strict=True):
    assert f"{max(yc):.3%}" == f"{v.max():.3%}" and f"{min(yc):.3%}" == f"{v.min():.3%}"
rollvol = {
    "alt": "Annualized 60-day volatility along TR23 and along one iid and one stationary-block resample of its days: "
    "TR23 swings between 7.2% and 44.3%, the iid path stays between 11.6% and 27.9%, and the block path copies "
    "whole calm and turbulent stretches, from 7.2% to 44.3%",
    "height": 320,
    "x": {"type": "num", "fmt": "n0", "tipLabel": "session ", "label": "Session (last return of the 60-day window)",
          "min": 60, "max": D.T, "ticks": [60, 1000, 2000, 3000, 4000, 5000],
          "values": [i + C.W60 for i in idx]},
    "y": {"type": "lin", "fmt": "pct1", "tfmt": "pct0", "label": "Annualized 60-day volatility", "min": 0, "max": 0.5,
          "ticks": [0, 0.1, 0.2, 0.3, 0.4, 0.5]},
    "series": [{"name": nm, "color": str(j + 1), "width": 1.2 if j else 1.6, "y": yc}
               for j, ((nm, _), yc) in enumerate(zip(paths, ycols, strict=True))],
}
write("lm22-rollvol", rollvol)

# ------------------------------------------------------------------ X6 ell: standard error against block length
G4 = C.exp4()
grid = {1: IID, C.ELL: SB, **G4}
ells = sorted(grid)
assert ells == list(C.WIDGET_ELLS)
names = {"SR": "Sharpe ratio", "Kelly": "Kelly fraction", "vol": "Volatility", "VR20": "VR(20)"}
pw_r, pw_r2 = C.pw(D.R)[0], C.pw((D.R - D.Rb) ** 2)[0]
ell = {
    "alt": "Bootstrap standard error over the iid one against the mean block length, 1 to 400 days on a log scale: "
    "the volatility's ratio rises from 1.18 at 2 days to 3.91 at 145 and 4.63 at 400, while the Sharpe ratio's and "
    "the Kelly fraction's peak at 1.15 and 1.24, between 50 and 100 days, and VR(20)'s is 0.93 at 145",
    "height": 320,
    "x": {"type": "log", "fmt": "n0", "tipLabel": "mean block length ", "label": "Mean block length (days, log scale)",
          "min": 1, "max": 400, "ticks": [1, 3, 10, 30, 145, 400], "values": ells},
    "y": {"type": "lin", "fmt": "n2", "tfmt": "n0", "label": "Standard error ÷ iid standard error", "min": 0.8,
          "max": 5, "ticks": [1, 2, 3, 4, 5]},
    "series": [{"name": names[k], "color": str(j + 1),
                "y": [rd(float(grid[e][k].std() / IID[k].std()), 4) for e in ells]}
               for j, k in enumerate(("SR", "Kelly", "vol", "VR20"))],
    "ann": [{"type": "hline", "y": 1, "dash": True},
            {"type": "vline", "x": rd(pw_r, 2), "dash": True, "label": "3.1 on R"},
            {"type": "vline", "x": rd(pw_r2, 2), "dash": True, "label": "144.6 on squares", "anchor": "end"}],
}
write("lm22-ell", ell)

# ------------------------------------------------------------------ the widget (experiment 24)
W = C.exp24()
RANGES = {"SR": (-0.25, 0.05), "Kelly": (-1.0, 0.25), "vol": (0.13, 0.0025), "acf": (-0.075, 0.0075),
          "VR20": (0.7, 0.015)}
NB = 50
LABELS = {"SR": ("Sharpe ratio, annualized", "n2"), "Kelly": ("Kelly fraction", "n2"),
          "vol": ("Volatility, annualized", "pct2"), "acf": ("Lag-1 autocorrelation of |r|", "n3"),
          "VR20": ("VR(20)", "n3")}
wstats, wdata = [], {}
for k in C.KEYS5:
    lo, width = RANGES[k]
    wstats.append({"key": k, "name": LABELS[k][0], "fmt": LABELS[k][1], "est": rd(OBS[k], 6), "lo": lo,
                   "width": width})
    wdata[k] = []
    for e in C.WIDGET_ELLS:
        reps = []
        for rep in range(C.WIDGET_REPS):
            v = W[f"{e}_{rep}_{k}"]
            assert v.size == C.B_WIDGET
            _, counts = hist(v, lo, width, NB)
            q = np.quantile(v, [0.025, 0.975], method="inverted_cdf")
            reps.append({"c": counts, "se": float(f"{v.std():.6g}"), "lo": float(f"{q[0]:.6g}"),
                         "hi": float(f"{q[1]:.6g}"), "mean": float(f"{v.mean():.6g}")})
        wdata[k].append(reps)
init = {"stat": "vol", "ell": C.ELL, "rep": 0}
iv0 = wdata["vol"][list(C.WIDGET_ELLS).index(C.ELL)][0]
lo0, w0 = RANGES["vol"]
edges0 = [rd(lo0 + w0 * i, 6) for i in range(NB + 1)]
widget = {
    "alt": "Histogram of 1,000 resampled annual volatilities of TR23 from stationary blocks of mean length 145 "
    "(the widget's first replicate), with the estimate 18.96% and the percentile ends",
    "height": 280,
    "x": {"type": "num", "fmt": "pct2", "tfmt": "pct0", "tipLabel": "from ", "label": "Volatility, annualized",
          "min": edges0[0], "max": edges0[-1]},
    "y": {"type": "lin", "fmt": "pct1", "tfmt": "pct0", "label": "Share of the 1,000 resamples per bin", "min": 0},
    "series": [{"name": "resamples", "color": "2", "step": True, "x": edges0,
                "y": [rd(c / C.B_WIDGET, 4) for c in iv0["c"]]}],
    "ann": [{"type": "vline", "x": rd(OBS["vol"], 6), "label": "estimate"},
            {"type": "vline", "x": iv0["lo"], "dash": True}, {"type": "vline", "x": iv0["hi"], "dash": True}],
    "widget": {"B": C.B_WIDGET, "nbins": NB, "ells": list(C.WIDGET_ELLS), "reps": C.WIDGET_REPS, "init": init,
               "seed": f"default_rng([24, {C.SEED}])", "stats": wstats, "data": wdata},
}
write("lm22-widget", widget)
for k in C.KEYS5:                                     # the widget's length 145 and 1 sit close to experiments 3 and 2
    print(f"widget {k}: SE at 145, three replicates "
          + ", ".join(f"{r_['se']:.4g}" for r_ in wdata[k][list(C.WIDGET_ELLS).index(C.ELL)])
          + f" (experiment 3: {SB[k].std():.4g}); iid " + ", ".join(f"{r_['se']:.4g}" for r_ in wdata[k][0])
          + f" (experiment 2: {IID[k].std():.4g})")
