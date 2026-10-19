"""Shared data and computations for LM26's scripts (data/lm26_numbers.py and data/lm26_charts.py import it).

Not a script: `uv run python data/lm26_numbers.py` and `uv run python data/lm26_charts.py` run it. Inputs:
- data/processed/vol3_taiex.parquet: TR23, the TAIEX total-return index (columns date, tr, price, R, Rp; R the
  total-return index's simple daily return, Rp the price index's, null on the first row), built and checked by
  data/vol3_series.py;
- data/derived/vol4_rv.csv (data/vol4_rv.py): one row per T5S day, 2005-01-03 .. 2026-10-08, with regime_s, rv_<h>
  and n_<h> on the window 09:30:00-13:30:00 for h = 5s, 10s, 15s, 30s, 1m, 5m, 10m, 15m, 30m (NaN where h is finer
  than the day's sampling), and o2, the squared log change from the previous TAIEX close to 09:30:00;
- data/processed/vol4_tx23.parquet (data/vol4_series.py): TX23's held near-month contract per date;
- the raw 5-second TAIEX files data/raw/intraday/taiex5s/<year>/<date>.csv and the raw TX 1-minute bars of 2025,
  data/raw/intraday/tx1m/2025/<date>.csv (data/fetch_intraday.py), with the TX daily file
  data/raw/vol4/TX__*.csv (TaiwanFuturesDaily). The raw intraday files serve only statistics; when they are missing,
  raw5() and tx25() return None and the scripts say which numbers they could not recompute.

Conventions (plans/vol-4.md, the LM26 brief, and plans/vol-4-anchors.md, "LM26").
- TR23: T = 5,849 daily log returns r_t = ln(1 + R_t), 2003-01-03 .. 2026-10-08; years = calendar days between the
  first and last close / 365.25; A = T / years = 246.12. Every daily model uses y = 100 r_t (percent), so variances are
  in %^2 a day and an annualized volatility is sqrt(A x variance).
- T5S: RV_t(h) = sum of squared log changes on the grid 09:30:00, 09:30:00 + h, ..., 13:30:00; the target
  V_t = 1e4 (o2 + rv_15m) in %^2 (V5 and V30 with rv_5m and rv_30m).
- GARCH(1,1): arch 8.0.0, arch_model(y, mean="Constant", vol="GARCH", p=1, q=1, dist="normal" or "t"),
  fit(disp="off"), convergence asserted; the recursion starts from arch's backcast (the weighted mean of the first 75
  squared residuals about the sample mean, weights 0.94^j normalized; arch/univariate/volatility.py, backcast):
  sigma_1^2 = omega + (alpha + beta) backcast. Classical standard errors invert -l'' (cov_type="classic"), robust ones
  are the sandwich (cov_type="robust", arch's default).
- EWMA: sigma^2_{t+1|t} = 0.94 sigma^2_{t|t-1} + 0.06 y_t^2, zero mean, started at the mean of y^2 over TR23's first
  246 returns.
- Out of sample: W = round(5A) = 1,231. At the first session s of each calendar month with s >= W both GARCH models
  are refitted on y_{s-W} .. y_{s-1}; the recursion restarts at the window's first day from that window's backcast
  and runs with the new parameters through the month's last session; the forecast of day t, made at the close of
  t - 1, is sigma^2_{t|t-1}. Six forecasts: GARCH normal and t (rolling), EWMA 0.94, rolling 60-day (mean of the last
  60 y^2, divisor 60, not demeaned), yesterday's V (V_{t-1}), EWMA of V (f_{t+1} = 0.94 f_t + 0.06 V_t, started with
  f = V on 2005-01-03). Forecast days 2008-01-02 .. 2026-10-08.
- Losses: MSE (V - f)^2 in %^4, QLIKE V/f - ln(V/f) - 1. Newey-West: Bartlett weights 1 - k/(l + 1),
  l = floor(4 (n/100)^(2/9)), divisor n, no small-sample correction. Mincer-Zarnowitz: OLS, HC0.
- Intraday autocorrelations pool within-day pairs only, uncentred: sum over days of sum r_i r_{i-1} over sum over
  days of sum r_i^2.
- TX bars: a bar's label is its first minute (an inference from the labels; SOURCES, TaiwanFuturesKBar); the
  near-month contract held during day t is TX23's contract on the previous TX23 date (TaiwanFuturesDaily); the price
  at 09:30:00 is the close of the 09:29 bar; a minute without a bar keeps the previous close.
- Quantiles and medians: np.quantile(..., method="inverted_cdf"); batch standard error of a median: 20 consecutive
  batches, standard deviation of the batch medians (divisor 20) over sqrt(20) (LM18).
"""
import datetime as dt
import functools
import math
import warnings
from pathlib import Path
from typing import Any, Literal

import numpy as np
import polars as pl
from arch import arch_model
from numpy.typing import NDArray

Vec = NDArray[np.float64]
Mask = NDArray[np.bool_]
Dist = Literal["normal", "t"]
DISTS: tuple[Dist, Dist] = ("normal", "t")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PROC = HERE / "processed"
RV_FILE = HERE / "derived" / "vol4_rv.csv"
RAW5 = HERE / "raw" / "intraday" / "taiex5s"
RAWTX = HERE / "raw" / "intraday" / "tx1m" / "2025"
RAWTXD = HERE / "raw" / "vol4"
SEED = 20261011
EPS = 1e-12
LAM = 0.94
IV = [("5s", 5), ("10s", 10), ("15s", 15), ("30s", 30), ("1m", 60), ("5m", 300), ("10m", 600), ("15m", 900),
      ("30m", 1800)]
START_S, AUCT_S, CLOSE_S = 9 * 3600 + 30 * 60, 13 * 3600 + 25 * 60, 13 * 3600 + 30 * 60


# ---------------------------------------------------------------- helpers
def qinv(x: Vec, u: float) -> float:
    """F_hat^{-1}(u), LM14's quantile function (inverted_cdf)."""
    return float(np.quantile(x, u, method="inverted_cdf"))


def batch_se_median(x: Vec) -> float:
    meds = np.array([qinv(b, 0.5) for b in np.split(x, 20)])
    return float(meds.std() / math.sqrt(20))


def nw_se(d: Vec, lags: int) -> float:
    """Newey-West standard error of a mean: Bartlett weights, divisor n, no small-sample correction."""
    c = d - d.mean()
    n = len(c)
    s = float(c @ c) / n
    for k in range(1, lags + 1):
        s += 2 * (1 - k / (lags + 1)) * float(c[k:] @ c[:-k]) / n
    return math.sqrt(s / n)


def nw_lags(n: int) -> int:
    """The book's lag rule, floor(4 (n/100)^(2/9)) (LM23)."""
    return math.floor(4 * (n / 100) ** (2 / 9))


def ols_hc0(X: Vec, yv: Vec) -> tuple[Vec, Vec, float]:
    """OLS coefficients, HC0 standard errors, R-squared."""
    b, *_ = np.linalg.lstsq(X, yv, rcond=None)
    e = yv - X @ b
    xtxi = np.linalg.inv(X.T @ X)
    meat = (X * e[:, None] ** 2).T @ X
    se = np.sqrt(np.diag(xtxi @ meat @ xtxi))
    yc = yv - yv.mean()
    return b, se, 1 - float(e @ e) / float(yc @ yc)


def backcast(e: Vec) -> float:
    """arch's backcast: weights 0.94^j on the first 75 squared residuals, normalized to 1."""
    w = 0.94 ** np.arange(min(75, len(e)))
    return float(np.sum(e[: len(w)] ** 2 * w / w.sum()))


def garch_filter(om: float, al: float, be: float, e: Vec, bc: float) -> Vec:
    """sigma^2_t for t = 0..len(e) (the last is the forecast after e ends), started from the backcast."""
    s2 = np.empty(len(e) + 1)
    s2[0] = om + (al + be) * bc
    for t in range(len(e)):
        s2[t + 1] = om + al * e[t] ** 2 + be * s2[t]
    return s2


def fit(x: Vec, dist: Dist, cov: Literal["robust", "classic"] = "robust") -> Any:
    """arch 8.0.0's GARCH(1,1) with a constant mean; convergence asserted."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        res = arch_model(x, mean="Constant", vol="GARCH", p=1, q=1, dist=dist).fit(disp="off", cov_type=cov)
    assert res.convergence_flag == 0, "arch did not converge"
    return res


def qlike(h: Vec, f: Vec) -> Vec:
    return h / f - np.log(h / f) - 1


def half_life(ps: float) -> float:
    """(25.2) with phi_1 = alpha + beta."""
    return math.log(0.5) / math.log(ps)


# ---------------------------------------------------------------- TR23
_tr = pl.read_parquet(PROC / "vol3_taiex.parquet").sort("date")
dates_all = [str(d) for d in _tr["date"].to_list()]
dates = dates_all[1:]
R = _tr["R"].to_numpy()[1:].astype(np.float64)
Rp = _tr["Rp"].to_numpy()[1:].astype(np.float64)
r = np.log1p(R)
rp = np.log1p(Rp)
y = 100 * r
T = len(y)
days_span = (dt.date.fromisoformat(dates_all[-1]) - dt.date.fromisoformat(dates_all[0])).days
years = days_span / 365.25
A = T / years
pos = {d: i for i, d in enumerate(dates)}
month = [d[:7] for d in dates]
starts = [i for i in range(T) if i == 0 or month[i] != month[i - 1]]
iso = [dt.date.fromisoformat(d).isocalendar()[:2] for d in dates]
assert T == 5849 and abs(A - 246.122955) < 1e-6


def ann(var_pct2: float) -> float:
    """Annualized volatility in percent from a daily variance in %^2."""
    return math.sqrt(A * var_pct2)


# ---------------------------------------------------------------- T5S per-day file
rvf = pl.read_csv(RV_FILE, comment_prefix="#").sort("date")
rv_dates: list[str] = rvf["date"].to_list()
reg = rvf["regime_s"].to_numpy()
RV = {name: rvf[f"rv_{name}"].to_numpy().astype(np.float64) for name, _ in IV}
NN = {name: rvf[f"n_{name}"].to_numpy().astype(np.float64) for name, _ in IV}
O2 = rvf["o2"].to_numpy().astype(np.float64)
ryear = np.array([d[:4] for d in rv_dates])
Vt = {name: 1e4 * (O2 + RV[name]) for name in ("5m", "15m", "30m")}
Vmap = {name: dict(zip(rv_dates, Vt[name].tolist())) for name in Vt}
i05 = pos["2005-01-03"]
assert [d for d in dates if d >= "2005-01-03"] == rv_dates
V15 = np.array([Vmap["15m"].get(d, np.nan) for d in dates])        # TR23's dates; NaN before 2005


# ---------------------------------------------------------------- full-sample fits
@functools.cache
def full_fits() -> dict[str, Any]:
    gn = fit(y, "normal")
    gn_c = fit(y, "normal", "classic")
    gt = fit(y, "t")
    gt_c = fit(y, "t", "classic")
    pn = gn.params.to_numpy()
    pt = gt.params.to_numpy()
    cvn = np.asarray(gn.conditional_volatility)
    cvt = np.asarray(gt.conditional_volatility)
    bc = backcast(y - y.mean())
    s2 = garch_filter(pn[1], pn[2], pn[3], y - pn[0], bc)       # s2[t] = sigma^2 of day t; s2[T] the next day's
    ll = -0.5 * float(np.sum(np.log(2 * np.pi) + np.log(s2[:T]) + (y - pn[0]) ** 2 / s2[:T]))
    assert abs(ll - gn.loglikelihood) < 1e-6, (ll, gn.loglikelihood)
    assert np.max(np.abs(s2[:T] - cvn**2)) < 1e-9
    pers = float(pn[2] + pn[3])
    uvar = float(pn[1] / (1 - pers))
    return {"gn": gn, "gn_c": gn_c, "gt": gt, "gt_c": gt_c, "pn": pn, "pt": pt, "cvn": cvn, "cvt": cvt, "bc": bc,
            "s2": s2, "ll_hand": ll, "pers": pers, "uvar": uvar,
            "xin": (y - pn[0]) / cvn, "xit": (y - pt[0]) / cvt}


def term(s2next: float, pers: float, uvar: float, m_max: int = 250) -> Vec:
    """(26.4): sigma^2_{t+m|t} for m = 1..m_max."""
    mm = np.arange(1, m_max + 1, dtype=np.float64)
    return np.asarray(uvar + pers ** (mm - 1) * (s2next - uvar), dtype=np.float64)


# ---------------------------------------------------------------- forecasts
def rolling_garch(window: int, refits: dict[str, list[tuple[str, Vec]]] | None = None) -> dict[str, Vec]:
    """Monthly refits on the previous `window` returns; sigma^2_{t|t-1} for every day from the first refit."""
    out = {"normal": np.full(T, np.nan), "t": np.full(T, np.nan)}
    f0 = next(i for i in starts if i >= window)
    for k, s in enumerate(starts):
        if s < f0:
            continue
        e_end = starts[k + 1] if k + 1 < len(starts) else T
        win = y[s - window : s]
        bc = backcast(win - win.mean())
        for dist in DISTS:
            res = fit(win, dist)
            p = res.params.to_numpy()
            if refits is not None:
                refits[dist].append((dates[s], p))
            s2 = garch_filter(p[1], p[2], p[3], y[s - window : e_end] - p[0], bc)
            if refits is not None and s == f0:
                assert np.max(np.abs(s2[:window] - np.asarray(res.conditional_volatility) ** 2)) < 1e-9
            out[dist][s:e_end] = s2[window : window + (e_end - s)]
    return out


@functools.cache
def ewma_path(lam: float = LAM) -> Vec:
    """sigma^2_{t|t-1} of (26.2) for t = 0..T (index T: the forecast after the last day)."""
    ew = np.empty(T + 1)
    ew[0] = float(np.mean(y[:246] ** 2))
    for t in range(T):
        ew[t + 1] = lam * ew[t] + (1 - lam) * y[t] ** 2
    return ew


NAMES = {"roll60": "rolling 60-day", "ewma": "EWMA 0.94", "garch_n": "GARCH normal", "garch_t": "GARCH t",
         "v_prev": "yesterday's V", "ewma_v": "EWMA of V"}


@functools.cache
def forecasts() -> dict[str, Any]:
    W = round(5 * A)
    assert W == 1231
    first = next(i for i in starts if i >= W)
    refits: dict[str, list[tuple[str, Vec]]] = {"normal": [], "t": []}
    rg = rolling_garch(W, refits)
    FC: dict[str, Vec] = {k: np.full(T, np.nan) for k in NAMES}
    FC["garch_n"], FC["garch_t"] = rg["normal"], rg["t"]
    ew = ewma_path()
    FC["ewma"][first:] = ew[first:T]
    c2 = np.concatenate([[0.0], np.cumsum(y**2)])
    ewv = np.full(T + 1, np.nan)
    ewv[i05] = V15[i05]
    for t in range(i05, T):
        ewv[t + 1] = LAM * ewv[t] + (1 - LAM) * V15[t]
    for t in range(first, T):
        FC["roll60"][t] = (c2[t] - c2[t - 60]) / 60
        FC["v_prev"][t] = V15[t - 1]
        FC["ewma_v"][t] = ewv[t]
    oos = np.arange(first, T)
    assert not any(np.isnan(FC[k][oos]).any() for k in FC)
    return {"W": W, "first": first, "oos": oos, "FC": FC, "refits": refits}


# ---------------------------------------------------------------- raw 5-second TAIEX (statistics only)
def raw5_available() -> bool:
    return RAW5.is_dir() and len(list(RAW5.glob("*/*.csv"))) == len(rv_dates)


@functools.cache
def raw5() -> dict[str, Vec] | None:
    """Per-day sums from the raw files: at the day's own interval (f), 1 and 5 minutes (m1, m5): sum of squares,
    sum of lag-1 products, sum, first and last return; each day's own-mean lag-1 autocorrelation of its finest
    returns; the closing auction's freeze and squared change. None when the download is missing."""
    if not raw5_available():
        return None
    files = {f.stem: f for f in RAW5.glob("*/*.csv")}
    assert sorted(files) == rv_dates
    P: dict[str, list[float]] = {k: [] for k in ("f_ss", "f_p1", "f_s", "f_n", "m1_ss", "m1_p1", "m1_s", "m5_ss",
                                                  "m5_p1", "m5_s", "auct2", "frozen_all", "rho1_day", "f_s_head",
                                                  "f_s_tail", "m1_head", "m1_tail", "m5_head", "m5_tail")}
    for d in rv_dates:
        x = pl.read_csv(files[d], schema_overrides={"date": pl.String, "TAIEX": pl.Float64})
        tt = x["date"].str.slice(11, 8).to_list()
        secs = np.array([int(a[:2]) * 3600 + int(a[3:5]) * 60 + int(a[6:8]) for a in tt])
        lv = np.log(x["TAIEX"].to_numpy())
        rg_s = int(np.bincount(np.diff(secs)).argmax())
        at = {int(s): j for j, s in enumerate(secs)}
        for key, h in (("f", rg_s), ("m1", 60), ("m5", 300)):
            rr = np.diff(lv[[at[s] for s in range(START_S, CLOSE_S + 1, h)]])
            P[f"{key}_ss"].append(float(rr @ rr))
            P[f"{key}_p1"].append(float(rr[1:] @ rr[:-1]))
            P[f"{key}_s"].append(float(rr.sum()))
            hk = "f_s" if key == "f" else key
            P[f"{hk}_head"].append(float(rr[0]))
            P[f"{hk}_tail"].append(float(rr[-1]))
            if key == "f":
                P["f_n"].append(len(rr))
                rc = rr - rr.mean()
                P["rho1_day"].append(float(rc[1:] @ rc[:-1]) / float(rc @ rc))
        inside = [at[s] for s in range(AUCT_S + rg_s, CLOSE_S, rg_s)]   # 13:25:00 + one step .. 13:30:00 - one step
        P["frozen_all"].append(float(np.all(lv[inside] == lv[inside[0]])))
        P["auct2"].append(float((lv[at[CLOSE_S]] - lv[at[AUCT_S]]) ** 2))
    return {k: np.array(val) for k, val in P.items()}


def pooled(PA: dict[str, Vec], mask: Mask, key: str, centred: bool = False) -> float:
    """Pooled lag-1 autocorrelation of within-day pairs (uncentred, or centred at the group's mean return)."""
    ss, p1, s = PA[f"{key}_ss"][mask], PA[f"{key}_p1"][mask], PA[f"{key}_s"][mask]
    if not centred:
        return float(p1.sum() / ss.sum())
    hk = "f_s" if key == "f" else key
    n = PA["f_n"][mask] if key == "f" else np.full(int(mask.sum()), 240.0 if key == "m1" else 48.0)
    mu = float(s.sum() / n.sum())
    a = s - PA[f"{hk}_head"][mask]     # sum over i >= 2
    b = s - PA[f"{hk}_tail"][mask]     # sum over i <= n - 1
    num = p1 - mu * (a + b) + (n - 1) * mu * mu
    den = ss - 2 * mu * s + n * mu * mu
    return float(num.sum() / den.sum())


# ---------------------------------------------------------------- raw TX 1-minute bars, 2025
def tx25_available() -> bool:
    return RAWTX.is_dir() and any(RAWTXD.glob("TX__*.csv"))


@functools.cache
def tx25() -> dict[str, Any] | None:
    """The near month's 2025 minute bars on the grid 09:30:00..13:30:00: RV at 1, 5, 10, 15 and 30 minutes per day,
    pooled lag-1 sums of 1-minute returns, and the label checks. None when the bars are missing."""
    if not tx25_available():
        return None
    tx23 = pl.read_parquet(PROC / "vol4_tx23.parquet").sort("date")
    txd = [str(d) for d in tx23["date"].to_list()]
    held = dict(zip(txd, tx23["contract"].to_list()))
    daily = pl.read_csv(min(RAWTXD.glob("TX__*.csv")), infer_schema_length=0)
    daily25 = daily.filter(pl.col("date").str.starts_with("2025"))
    dclose = {(a, b): float(c) for a, b, c in zip(daily25["date"].to_list(), daily25["contract_date"].to_list(),
                                                    daily25["close"].to_list())}
    tx_days = [d for d in txd if d.startswith("2025")]
    first_lab: set[str] = set()
    last_lab: dict[str, int] = {}
    nbar: dict[int, int] = {}
    miss_days: dict[str, int] = {}
    eq = 0
    TXRV: dict[int, list[float]] = {h: [] for h in (1, 5, 10, 15, 30)}
    tx_p1, tx_ss = [], []
    for d in tx_days:
        c = str(held[txd[txd.index(d) - 1]])
        x = pl.read_csv(RAWTX / f"{d}.csv", infer_schema_length=0)
        x = x.filter((pl.col("contract_date") == c) & (pl.col("minute") >= "08:45:00") & (pl.col("minute") <= "13:45:00"))
        x = x.sort("minute")
        mins = x["minute"].to_list()
        first_lab.add(mins[0])
        last_lab[mins[-1]] = last_lab.get(mins[-1], 0) + 1
        nbar[len(mins)] = nbar.get(len(mins), 0) + 1
        cl = dict(zip(mins, [float(z) for z in x["close"].to_list()]))
        eq += int(dclose[(d, c)] == cl[mins[-1]])
        before = [m_ for m_ in mins if m_ <= "09:29:00"]
        last = cl[before[-1]]
        grid = []
        for t in range(9 * 60 + 29, 13 * 60 + 30):
            lab = f"{t // 60:02d}:{t % 60:02d}:00"
            if lab in cl:
                last = cl[lab]
            else:
                miss_days[d] = miss_days.get(d, 0) + 1
            grid.append(last)
        lp = np.log(np.array(grid))
        for h, acc in TXRV.items():
            rr = np.diff(lp[::h])
            acc.append(float(rr @ rr))
        r1 = np.diff(lp)
        tx_p1.append(float(r1[1:] @ r1[:-1]))
        tx_ss.append(float(r1 @ r1))
    return {"days": tx_days, "first_lab": first_lab, "last_lab": last_lab, "nbar": nbar, "eq": eq,
            "miss_days": miss_days, "RV": {h: np.array(val) for h, val in TXRV.items()},
            "rho1": sum(tx_p1) / sum(tx_ss)}
