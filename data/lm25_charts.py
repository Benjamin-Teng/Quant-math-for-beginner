"""Chart specs for LM25 (src/data/lm25-*.json), computed from TX23 and TR23.

Run:  uv run python data/lm25_charts.py      (after data/vol3_series.py and data/vol4_series.py; data/lm25_numbers.py
      checks the text against these files)

Inputs, read through data/lm25_common.py: data/processed/vol4_tx23.parquet (TX23) and data/processed/vol3_taiex.parquet
(TR23). Same conventions as data/lm25_numbers.py. Writes:
  lm25-case-s, lm25-case-b  the TAIEX close and the log basis at weekly points (the last TX23 session of each ISO week,
                            the first date and the two extremes of the basis; no daily series at full resolution);
  lm25-acf                  sample ACF and PACF (OLS) of the basis with the AR(1) and ARMA(1,1) model ACFs, lags 1-20;
  lm25-robust               TR23's sample autocorrelations of log returns, lags 1-30, with the iid and robust bands;
  lm25-dfnull               histogram of experiment 1's 10,000 DF t-stats and the standard normal density;
  lm25-spurious             the first pair of experiment 2 (simulated, not market data);
  lm25-season               means over D of the basis, the fair log basis and the residual by calendar month;
  lm25-expiry               mean and standard deviation of the basis and the mean fair log basis by sessions to expiry;
  lm25-ar1noise             the widget's data block (model constants only, no market series) with a fallback chart.
"""
import datetime as dt
import json
import math
from typing import Any

import numpy as np
from lm25_common import (
    BP,
    ROOT,
    ArmaFit,
    D,
    N,
    S,
    arma_acf,
    b,
    dates,
    df_null,
    df_reg,
    fair,
    mon,
    n_year,
    noise_split,
    quant,
    r,
    resid,
    rho_hat,
    se_rob,
    sess,
    spurious,
)
from scipy import stats
from statsmodels.tsa.stattools import acf, pacf

OUT = ROOT / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)
MAX_BYTES = 300_000


def rd(x: float, n: int) -> float:
    return round(float(x), n)


def write(name: str, spec: dict[str, Any]) -> None:
    assert isinstance(spec.get("alt"), str) and spec["alt"].strip()
    blob = json.dumps(spec, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    assert len(blob.encode("utf-8")) < MAX_BYTES, (name, len(blob.encode("utf-8")))
    (OUT / f"{name}.json").write_text(blob, encoding="utf-8", newline="\n")
    print(f"wrote src/data/{name}.json ({len(blob.encode('utf-8')):,} bytes)")


# ------------------------------------------------------------------ X1: the case, weekly points
iso = [dt.date.fromisoformat(d).isocalendar() for d in dates]
week_last: dict[tuple[int, int], int] = {}
for i, c in enumerate(iso):
    week_last[(c[0], c[1])] = i
i_lo, i_hi = int(b.argmin()), int(b.argmax())
keep = sorted(set(week_last.values()) | {0, i_lo, i_hi, N - 1})
assert len(keep) == 1227
xs = [dates[i] for i in keep]
bk = [rd(BP * b[i], 1) for i in keep]
assert -792.9 in bk and 247.8 in bk
write("lm25-case-s", {
    "alt": "The TAIEX price close from January 2003 to October 2026 on a log scale, rising from 4,524.87 to 49,313.44, "
           "at weekly points",
    "height": 220,
    "x": {"type": "date", "values": xs},   # xs holds the first and last dates: both charts share the range
    "y": {"type": "log", "fmt": "n2", "tfmt": "n0", "label": "TAIEX price close (log scale)", "min": 3500,
          "max": 56000, "ticks": [5000, 10000, 20000, 40000]},
    "series": [{"name": "TAIEX", "color": "1", "y": [rd(S[i], 2) for i in keep]}],
})
write("lm25-case-b", {
    "alt": "The TX-TAIEX log basis in basis points from January 2003 to October 2026 at weekly points, around its "
           "mean of -25.4 bp, with its low of -792.9 bp on 27 October 2008 and its high of +247.8 bp on 5 May 2009",
    "height": 240,
    "x": {"type": "date", "values": xs},   # xs holds the first and last dates: both charts share the range
    "y": {"type": "lin", "fmt": "n1", "tfmt": "n0", "label": "Log basis (bp)", "min": -820, "max": 280,
          "ticks": [-800, -600, -400, -200, 0, 200]},
    "series": [{"name": "Log basis", "color": "2", "y": bk}],
    "ann": [{"type": "hline", "y": rd(BP * b.mean(), 1), "dash": True},
            {"type": "point", "x": dates[i_lo], "y": rd(BP * b[i_lo], 1), "color": "2", "label": "−792.9 (27 Oct 2008)",
             "dx": 10, "dy": 4},
            {"type": "point", "x": dates[i_hi], "y": rd(BP * b[i_hi], 1), "color": "2", "label": "+247.8 (5 May 2009)",
             "dx": 10, "dy": 4}],
})

# ------------------------------------------------------------------ X3: ACF and PACF of the basis
lags20 = list(range(1, 21))
acf_b = acf(b, nlags=20, fft=False)[1:]
pacf_b = np.asarray(pacf(b, nlags=20, method="ols"), dtype=float)[1:]
_, d_b, _, _, _ = df_reg(b)
phi_ar = 1 + d_b
fit_b = ArmaFit(BP * b)
p_b = fit_b.params
write("lm25-acf", {
    "alt": "Sample autocorrelations of the log basis falling from 0.776 at lag 1 to 0.360 at lag 20, partial "
           "autocorrelations 0.776, 0.230 and 0.109 at lags 1 to 3 and small beyond, the AR(1) model 0.7758 to the "
           "power k and the ARMA(1,1) model",
    "height": 280,
    "x": {"type": "num", "fmt": "n0", "label": "Lag k (sessions)", "tipLabel": "lag ", "min": 1, "max": 20,
          "ticks": [1, 5, 10, 15, 20]},
    "y": {"type": "lin", "fmt": "n3", "tfmt": "n1", "label": "Autocorrelation", "min": -0.1, "max": 1,
          "ticks": [0, 0.2, 0.4, 0.6, 0.8, 1]},
    "series": [
        {"name": "Sample ACF", "color": "1", "x": lags20, "y": [rd(x, 5) for x in acf_b]},
        {"name": "Sample PACF (OLS)", "color": "2", "x": lags20, "y": [rd(x, 5) for x in pacf_b]},
        {"name": "AR(1) model", "color": "3", "dash": True, "x": lags20, "y": [rd(phi_ar**k, 5) for k in lags20]},
        {"name": "ARMA(1,1) model", "color": "4", "dash": True, "x": lags20,
         "y": [rd(arma_acf(p_b[1], p_b[2], k), 5) for k in lags20]},
    ],
})

# ------------------------------------------------------------------ X2: robust band
K = 30
T = len(r)
lags30 = list(range(1, K + 1))
rho = [rho_hat(r, k) for k in lags30]
rob = [se_rob(r, k) for k in lags30]
band_iid = 1.96 / math.sqrt(T)
write("lm25-robust", {
    "type": "scatter",
    "alt": f"Sample autocorrelations of TAIEX log returns at lags 1 to 30, between {min(rho):.3f} and {max(rho):.3f}, "
           "against the iid band of plus or minus 0.0256 and the wider robust band; nine lags leave the iid band and "
           "two, lags 8 and 14, the robust band",
    "height": 280,
    "x": {"label": "Lag k (sessions)", "fmt": "n0", "min": 0, "max": 31, "ticks": [1, 5, 10, 15, 20, 25, 30],
          "name": "lag"},
    "y": {"label": "Autocorrelation", "fmt": "n4", "tfmt": "n2", "min": -0.06, "max": 0.06,
          "ticks": [-0.06, -0.04, -0.02, 0, 0.02, 0.04, 0.06], "name": "value"},
    "bands": [
        {"x": lags30, "lo": [rd(-1.96 * s, 5) for s in rob], "hi": [rd(1.96 * s, 5) for s in rob], "color": "2",
         "opacity": 0.16, "name": "Robust band"},
        {"x": lags30, "lo": [rd(-band_iid, 5)] * K, "hi": [rd(band_iid, 5)] * K, "color": "3", "opacity": 0.22,
         "name": "iid band"},
    ],
    "series": [{"name": "Sample autocorrelation of r", "color": "1", "x": lags30, "y": [rd(x, 5) for x in rho]}],
})

# ------------------------------------------------------------------ X4: the DF null
t1, _ = df_null(1, N, 10_000)
edges = np.round(np.arange(-55, 26) / 10, 1)
assert t1.min() > edges[0] and t1.max() < edges[-1]
counts, _ = np.histogram(t1, bins=edges)
dens = counts / (len(t1) * 0.1)
zx = np.round(np.arange(-55, 26) / 10, 1)
q05 = quant(t1, 0.05)
YMAX = math.ceil(10 * max(float(dens.max()), float(stats.norm.pdf(0)))) / 10
write("lm25-dfnull", {
    "alt": "Histogram of 10,000 simulated Dickey-Fuller t-stats under a unit root, centred near -1.5 and shifted left "
           "of the standard normal density; the simulated 5% point is -2.86 against the normal's -1.645",
    "height": 280,
    "x": {"type": "num", "fmt": "n2", "tfmt": "n0", "label": "DF t-stat", "tipLabel": "t-stat ", "min": -5.5,
          "max": 2.5, "ticks": [-5, -4, -3, -2, -1, 0, 1, 2]},
    "y": {"type": "lin", "fmt": "n3", "tfmt": "n1", "label": "Density", "min": 0, "max": YMAX,
          "ticks": [round(0.1 * i, 1) for i in range(round(YMAX * 10) + 1)]},
    "series": [
        {"name": "Simulated DF t-stat", "color": "1", "step": True, "area": True, "x": [float(e) for e in edges],
         "y": [rd(x, 4) for x in dens]},
        {"name": "Standard normal", "color": "2", "x": [float(z) for z in zx],
         "y": [rd(stats.norm.pdf(z), 4) for z in zx]},
    ],
    "ann": [{"type": "vline", "x": rd(q05, 4), "dash": True, "label": "5% point −2.86", "anchor": "end"},
            {"type": "vline", "x": -1.645, "dash": True, "label": "−1.645"}],
})

# ------------------------------------------------------------------ X5: spurious regression, first pair of experiment 2
_, _, first2, paths2 = spurious(2, N, 1)
assert f"{paths2[0, -1]:.1f}" == "62.0" and f"{paths2[1, -1]:.1f}" == "98.3"
SP_LO, SP_HI = 25 * math.floor(float(paths2.min()) / 25), 25 * math.ceil(float(paths2.max()) / 25)
write("lm25-spurious", {
    "alt": "Two independent simulated random walks of 5,850 sessions that drift apart and together by chance, ending "
           "at 62.0 and 98.3; their regression shows a t-stat of 23.5",
    "height": 260,
    "x": {"type": "num", "fmt": "n0", "label": "Session", "tipLabel": "session ", "min": 1, "max": N,
          "values": list(range(1, N + 1)), "ticks": [1, 1000, 2000, 3000, 4000, 5000, 5850]},
    "y": {"type": "lin", "fmt": "n1", "tfmt": "n0", "label": "Level", "min": SP_LO, "max": SP_HI,
          "ticks": [v for v in range(SP_LO, SP_HI + 1, 25) if v % 50 == 0]},
    "series": [{"name": "x_t", "color": "1", "y": [rd(x, 1) for x in paths2[0]]},
               {"name": "y_t", "color": "2", "y": [rd(x, 1) for x in paths2[1]]}],
})

# ------------------------------------------------------------------ X6: dividend season
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
sb, sf, sr = [], [], []
for mm in range(1, 13):
    msk = D & (mon == mm)
    sb.append(rd(BP * b[msk].mean(), 2))
    sf.append(rd(BP * fair[msk].mean(), 2))
    sr.append(rd(BP * resid[msk].mean(), 2))
assert (sb[5], sf[5], sr[5], sb[6], sf[6], sr[6]) == (-74.80, -67.43, -7.37, -70.17, -65.88, -4.29)
write("lm25-season", {
    "type": "bar",
    "alt": f"Mean log basis by calendar month over 2003-2026: -74.80 bp in June and -70.17 bp in July, between "
           f"{min(sb[:5] + sb[7:]):.2f} and {max(sb[:5] + sb[7:]):.2f} bp in the other months, each split into the "
           "fair log basis (carry minus realized dividends) and the residual",
    "height": 300,
    "categories": months,
    "x": {"label": "Calendar month"},
    "y": {"fmt": "n2", "tfmt": "n0", "label": "bp", "min": -80, "max": 20, "ticks": [-80, -60, -40, -20, 0, 20]},
    "valueLabels": False,
    "series": [{"name": "Mean log basis", "color": "1", "values": sb},
               {"name": "Fair log basis", "color": "2", "values": sf},
               {"name": "Residual", "color": "3", "values": sr}],
})

# ------------------------------------------------------------------ X7: convergence at expiry
ks = list(range(20, 1, -1))
mb, lo, hi, mf = [], [], [], []
for k in ks:
    msk = D & (sess == k)
    m_, s_ = BP * float(b[msk].mean()), BP * float(b[msk].std())
    mb.append(rd(m_, 2))
    lo.append(rd(m_ - s_, 2))
    hi.append(rd(m_ + s_, 2))
    mf.append(rd(BP * float(fair[msk].mean()), 2))
assert (mb[0], mf[0], mb[-1], mf[-1]) == (-37.95, -14.78, -6.56, -1.84)
Y_LO, Y_HI = 40 * math.floor(min(lo) / 40), 40 * math.ceil(max(hi) / 40)
write("lm25-expiry", {
    "alt": "Mean log basis by sessions to the last trading day, rising from -37.95 bp at 20 sessions to -6.56 bp at 2, "
           "with a band of one standard deviation narrowing from 69.17 to 35.13 bp, and the mean fair log basis "
           "rising from -14.78 to -1.84 bp",
    "height": 280,
    "x": {"type": "num", "fmt": "n0", "label": "Sessions to the last trading day", "tipLabel": "minus sessions: ",
          "min": -20, "max": -2, "ticks": [-20, -15, -10, -5, -2], "tickLabels": ["20", "15", "10", "5", "2"],
          "values": [-k for k in ks]},
    "y": {"type": "lin", "fmt": "n2", "tfmt": "n0", "label": "bp", "min": Y_LO, "max": Y_HI,
          "ticks": list(range(Y_LO, Y_HI + 1, 40))},
    "series": [{"name": "Mean ± one standard deviation", "color": "1", "lo": lo, "hi": hi},
               {"name": "Mean log basis", "color": "1", "y": mb},
               {"name": "Mean fair log basis", "color": "2", "dash": True, "y": mf}],
    "ann": [{"type": "hline", "y": 0, "dash": True}],
})

# ------------------------------------------------------------------ widget: a persistent AR(1) plus one-day noise
su2, sz2, sx2, _ = noise_split(p_b[1], p_b[2], p_b[3])
_, crit245 = df_null(3, n_year, 500)       # MacKinnon's 5% point for 245 observations (statsmodels' adfuller)
phi0, su0 = 0.91, 22
sx0 = math.sqrt(sz2 / (1 - phi0**2))
lag_k = list(range(21))
write("lm25-ar1noise", {
    "alt": "Model autocorrelations at the widget's initial state: a persistent AR(1) with coefficient 0.91 and, below "
           "it, the same series observed with one-day noise of 22 bp",
    "height": 280,
    "x": {"type": "num", "fmt": "n0", "label": "Lag (sessions)", "min": 0, "max": 20, "ticks": [0, 5, 10, 15, 20]},
    "y": {"type": "lin", "fmt": "n3", "tfmt": "n1", "label": "Autocorrelation", "min": 0, "max": 1},
    "series": [{"name": "Persistent part", "color": "2", "x": lag_k, "y": [rd(phi0**k, 4) for k in lag_k]},
               {"name": "Observed basis", "color": "1", "x": lag_k,
                "y": [1.0] + [rd(phi0**k * sx0**2 / (sx0**2 + su0**2), 4) for k in lag_k[1:]]}],
    "widget": {"phi0": phi0, "sigmaU0": su0, "sigmaZeta": rd(math.sqrt(sz2), 3), "mean": rd(p_b[0], 3),
               "n": n_year, "crit5": rd(crit245, 4), "seed0": 1},
})
assert math.isclose(rd(crit245, 4), -2.8734) and n_year == 246
