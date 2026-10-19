"""Generate labs/LM25_lab (Polars-first notebook + README) for LM25, Time Series I: ARMA, Unit Roots and Cointegration.

Run:  uv run python build/make_lab25.py
Then execute from inside the lab folder:
      cd labs/LM25_lab && uv run jupyter nbconvert --to notebook --execute --inplace LM25_lab.ipynb

The notebook reads only labs/LM25_lab/data/ (built by data/make_lab_data.py from data/raw/; FinMind's licence keeps raw
data out of the repository): taiex_tr.csv (date, price: the TAIEX total-return closes), taiex_price.csv (date, close,
spread: the TAIEX price closes, cut to TR23's dates) and tx_daily.csv (a copy of the regular-session monthly TX rows of
FinMind's TaiwanFuturesDaily). This script writes the notebook and the README only.

Exhibit and example numbers are never typed by hand: cells write [[ex:label]] / [[eg:label]], and the generator
resolves them from the labels in src/lm25.md, numbered in document order as build/build.py does.
"""
import re
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "LM25_lab"
LAB.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- exhibit / example numbers from the module's labels
NUM: dict[str, tuple[str, int]] = {}
_count = {"exhibit": 0, "example": 0}
for m in re.finditer(r"(?m)^(?:>\s?)+\[!(exhibit|example)\][+-]?\s*(.*)$", (ROOT / "src" / "lm25.md").read_text(encoding="utf-8")):
    _count[m.group(1)] += 1
    lab = re.search(r"\{#([\w-]+)\}\s*$", m.group(2))
    if lab:
        NUM[lab.group(1)] = ("Exhibit" if m.group(1) == "exhibit" else "Example", _count[m.group(1)])


def refs(s: str) -> str:
    """Replace [[ex:a]] and [[eg:a]] by 'Exhibit k' and 'Example k', checking the kind."""
    def rep(m: re.Match[str]) -> str:
        kind, a = m.group(1), m.group(2)
        word, k = NUM[a]
        assert word == ("Exhibit" if kind == "ex" else "Example"), (kind, a)
        return f"{word} {k}"
    out = re.sub(r"\[\[(ex|eg):([\w-]+)\]\]", rep, s)
    assert not re.search(r"\[\[(ex|eg):", out) and "[[LM" not in out, out
    return out


cells: list = []


def md(s: str) -> None:
    cells.append(nbf.v4.new_markdown_cell(refs(s.strip("\n"))))


def code(s: str) -> None:
    cells.append(nbf.v4.new_code_cell(refs(s.strip("\n"))))


md(r"""
# LM25 Lab — Time Series I: ARMA, Unit Roots and Cointegration

Companion notebook to **From Calculus to Kelly, LM25**. It builds TX23, the TX near-month future against the TAIEX, from the daily futures file with the module's roll rule, rebuilds the module's exhibits and computational examples, runs the four simulation experiments, solves the computational practice problems, and ends with an extension exercise.

| Part | Rebuilds |
|:--|:--|
| 1 | Data: TX23 with the roll rule (5,850 dates, 285 rolls), the exact count of $F<S$, sample D, TR23's log returns |
| 2 | The case and [[ex:case]] at weekly points |
| 3 | Stationarity: [[eg:regimes]] and a simulated random walk against an AR(1) |
| 4 | AR and MA models: [[eg:ar1]] by hand and with statsmodels, partial autocorrelations by regression, [[ex:acf]] |
| 5 | Tests for autocorrelation: [[eg:lag1]], [[ex:robust]], [[eg:portmanteau]], Problems 6 and 12 |
| 6 | Unit roots: experiment 1 ([[eg:dfsim]], [[ex:dfnull]]), [[eg:adf]], Problems 9 and 10 |
| 7 | Spurious regression and cointegration: experiment 2 ([[eg:spur]], [[ex:spurious]]), [[eg:englegranger]], Problem 11 |
| 8 | The basis: [[ex:expiry]], roll jumps, [[ex:season]], [[ex:versions]] ([[eg:fourversions]]), [[eg:arma]] with a hand Hessian, the regimes and 2025 |
| 9 | The module's Python block, run as printed, and an extension: the half-lives year by year |

**Environment.** From the repository root, `uv sync` installs the locked Python environment (`uv.lock`). Open this notebook with the `.venv` kernel, or run `uv run --with jupyterlab jupyter lab`.

**Data.** The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

`data/` then holds three files: `taiex_tr.csv` (`date`, `price`: the TAIEX total-return closes, FinMind `TaiwanStockTotalReturnIndex`), `taiex_price.csv` (`date`, `close`, `spread`: the TAIEX price closes, FinMind `TaiwanStockPrice`, on the same 5,850 dates) and `tx_daily.csv` (the regular-session rows of the monthly TX contracts, FinMind `TaiwanFuturesDaily`, 1998-07-21 to 2026-10-16). The TX file is free on FinMind; nothing here needs a paid plan. The notebook reads nothing outside `data/`.

**Conventions (as in the module).** The log basis $b_t=\ln F_t-\ln S_t$ is in basis points (bp, $10^{-4}$). A rolled change differences the stored series; a roll-free change uses one contract on both days. $s$ divides by the number of terms (`ddof=0`), a regression's $s_\varepsilon$ by $T-2$. Sample autocorrelations use the full-sample mean and divisor $T$ (LM19's (19.5)); partial autocorrelations come from OLS. Quantiles and medians use `method="inverted_cdf"`; a simulated quantile's standard error is LM18's batch standard error (20 batches, divisor 20). Each simulated experiment $e$ creates `np.random.default_rng([e, 20261011])` once. ARMA fits run at the likelihood maximum with standard errors from $-\ell''$. Every test and fit is in-sample; the limit regimes are a stability check; the simulations are a model; the figures of the case, the regimes' means and the expiry, season and roll figures are descriptive.
""")

code(r"""
import datetime as dt
import math
import warnings
from fractions import Fraction
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import acf, adfuller, coint, kpss, pacf

DATA = Path("data")
SEED = 20261011
BP = 1e4
RF = 0.02            # LM6's financing-rate proxy, continuously compounded
EPS = 1e-12
plt.rcParams.update({"figure.figsize": (9, 4.2), "axes.grid": True, "grid.alpha": 0.3,
                     "axes.spines.top": False, "axes.spines.right": False})
pl.Config.set_tbl_rows(30)     # print the 12 months and the 24 years in full


def show(label, value, fmt, printed):
    # print a value next to the module's printed value and assert that they agree
    got = format(value, fmt)
    print(f"{label}: {got}   [book: {printed}]")
    assert got == printed, (label, got, printed)
""")

md(r"""
## Part 1 — Data: TX23 with the roll rule

A monthly contract's last trading day is its last row in the file; for a contract still trading at the file's end, it is the TAIFEX rule's third Wednesday of the month. On each date the position holds the first contract whose last trading day comes after the next session, so the roll happens at the close of the day before a contract's last trading day and no expiry day enters (FinMind prints the expiring contract's settlement as 0 on that day from December 2008). $F_t$ is the held contract's settlement price, $S_t$ the TAIEX price close.
""")

code(r"""
tr = pl.read_csv(DATA / "taiex_tr.csv", schema_overrides={"price": pl.String}).sort("date")
px = pl.read_csv(DATA / "taiex_price.csv", schema_overrides={"close": pl.String}).sort("date")
tx = pl.read_csv(DATA / "tx_daily.csv", schema_overrides={"contract_date": pl.String,
                                                          "settlement_price": pl.String}).sort("date", "contract_date")
dates = tr["date"].to_list()
assert px["date"].to_list() == dates and len(dates) == 5850

rows = tx.select("date", "contract_date", "settlement_price", "volume").rows()
settle = {(d, c): s for d, c, s, _ in rows}
volume = {(d, c): v for d, c, _, v in rows}
listed: dict[str, list[str]] = {}
last_row: dict[str, str] = {}
for d, c, _, _ in rows:
    listed.setdefault(d, []).append(c)
    last_row[c] = max(last_row.get(c, d), d)
all_dates = sorted(listed)
file_end = all_dates[-1]
next_session = dict(zip(all_dates[:-1], all_dates[1:]))


def third_wednesday(month):
    d = dt.date(int(month[:4]), int(month[4:]), 1)
    return d + dt.timedelta(days=(2 - d.weekday()) % 7 + 14)


last_day = {c: (third_wednesday(c) if e == file_end else dt.date.fromisoformat(e)) for c, e in last_row.items()}

recs = []
held_prev = None
for d in dates:
    nd = dt.date.fromisoformat(next_session[d])
    c = min(k for k in listed[d] if last_day[k] > nd)              # the near month held from this close
    recs.append({"date": d, "contract": c, "F_str": settle[(d, c)], "F_held_str": settle[(d, held_prev)] if held_prev else None,
                 "last_day": last_day[c], "roll": held_prev is not None and c != held_prev, "volume": volume[(d, c)]})
    held_prev = c
tx23 = (pl.DataFrame(recs).with_columns(pl.Series("S_str", px["close"].to_list()), pl.Series("TR", tr["price"].cast(pl.Float64)))
        .with_columns(pl.col("F_str").cast(pl.Float64).alias("F"), pl.col("S_str").cast(pl.Float64).alias("S"),
                      pl.col("F_held_str").cast(pl.Float64).alias("F_held")))
F = tx23["F"].to_numpy()
S = tx23["S"].to_numpy()
TRI = tx23["TR"].to_numpy()
roll = tx23["roll"].to_numpy()
b = np.log(F / S)                                      # the log basis
rF = np.log(tx23["F_held"].to_numpy()[1:] / F[:-1])    # roll-free daily log change of the position
rS = np.diff(np.log(S))
db = np.diff(b)                                        # rolled changes
db_free = rF - rS                                      # roll-free changes
N = len(dates)
show("TX23 dates", N, ",", "5,850")
print("rolls:", int(roll.sum()), "| contracts held:", tx23["contract"].n_unique())
assert int(roll.sum()) == 285
assert all(F > 0) and all(tx23["last_day"].to_numpy() > np.array([np.datetime64(d) for d in dates]))

# F < S counted exactly on the whole-point settlements and the two-decimal closes; the guard agrees
n_neg = sum(Fraction(f) < Fraction(s) for f, s in zip(tx23["F_str"], tx23["S_str"]))
assert n_neg == int((b < -EPS).sum())
show("F < S", n_neg, ",", "4,051")
""")

code(r"""
# sample D: the dates whose held contract's last trading day lies in the sample; realized dividends to that day
idx = {d: i for i, d in enumerate(dates)}
ld = [x.isoformat() for x in tx23["last_day"].to_list()]
qt = np.array([math.log(TRI[idx[l]] / TRI[i]) - math.log(S[idx[l]] / S[i]) if l in idx else np.nan
               for i, l in enumerate(ld)])
sess = np.array([idx[l] - i if l in idx else -1 for i, l in enumerate(ld)])
days = np.array([(dt.date.fromisoformat(l) - dt.date.fromisoformat(d)).days for d, l in zip(dates, ld)])
tau = days / 365.0
D = ~np.isnan(qt)
fair = RF * tau - qt                 # fair log basis: carry minus realized dividends
resid = b - fair                     # the residual of (6.25) in log form
mon = np.array([int(d[5:7]) for d in dates])
yr = np.array([int(d[:4]) for d in dates])
pre = np.array([d < "2015-06-01" for d in dates])
show("D dates", int(D.sum()), ",", "5,834")
iD_last = int(np.flatnonzero(D)[-1])
print("D ends on", dates[iD_last], "holding", tx23["contract"][iD_last], "which expires on", ld[iD_last])

# TR23: log returns of the total-return index
r = np.diff(np.log(TRI))
T = len(r)
show("TR23 returns T", T, ",", "5,849")
""")

md(r"""
## Part 2 — The case at weekly points

The module publishes no daily FinMind series at full resolution: [[ex:case]] plots the last session of each ISO week, the first date and the two extremes of the basis. Here the full daily series is available, so the statistics use every date.
""")

code(r"""
show("S first", S[0], ",.2f", "4,524.87")
show("S last", S[-1], ",.2f", "49,313.44")
show("growth", S[-1] / S[0], ".1f", "10.9")
show("mean basis (bp)", BP * b.mean(), ".1f", "-25.4")
show("s of the basis (bp)", BP * b.std(), ".1f", "58.2")
i_lo, i_hi = int(b.argmin()), int(b.argmax())
print("extremes:", dates[i_lo], round(BP * b[i_lo], 1), "|", dates[i_hi], round(BP * b[i_hi], 1))
show("s of rolled changes (bp)", BP * db.std(), ".1f", "38.9")


def rho_hat(x, k):
    c = x - x.mean()
    return float(c[k:] @ c[:-k] / (c @ c))


show("next-day correlation", rho_hat(b, 1), ".3f", "0.776")

iso = [dt.date.fromisoformat(d).isocalendar()[:2] for d in dates]
last_of_week = {w: i for i, w in enumerate(iso)}
keep = sorted(set(last_of_week.values()) | {0, i_lo, i_hi, N - 1})
show("weekly points", len(keep), ",", "1,227")
t_axis = [dt.date.fromisoformat(dates[i]) for i in keep]
fig, ax = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
ax[0].semilogy(t_axis, S[keep])
ax[0].set_ylabel("TAIEX close (log)")
ax[1].plot(t_axis, BP * b[keep], color="C1")
ax[1].axhline(BP * b.mean(), ls="--", color="grey")
ax[1].set_ylabel("log basis (bp)")
ax[0].set_title("[[ex:case]]: weekly points")
plt.show()
""")

md(r"""
## Part 3 — Stationarity

[[eg:regimes]] splits TX23 at 1 June 2015, when TWSE's daily price limit widened from 7% to 10%. A window's statistics use its own dates only. Then a simulated random walk and a stationary AR(1) with the same innovations show why a level has no fixed variance (seed `[101, 20261011]`, an illustration that the module does not print).
""")

code(r"""
for name, msk in (("before", pre), ("from", ~pre)):
    print(f"{name} 1 June 2015: {int(msk.sum())} dates, mean S {S[msk].mean():,.0f}, "
          f"mean b {BP * b[msk].mean():.1f} bp, s(b) {BP * b[msk].std():.1f} bp")
show("mean S before", S[pre].mean(), ",.0f", "7,302")
show("mean S from", S[~pre].mean(), ",.0f", "16,042")
show("s(b) before", BP * b[pre].std(), ".1f", "65.7")
show("s(b) from", BP * b[~pre].std(), ".1f", "48.2")

rng = np.random.default_rng([101, SEED])
eta = rng.standard_normal(2000)
walk = np.cumsum(eta)
ar = np.zeros(2000)
for t in range(1, 2000):
    ar[t] = 0.9 * ar[t - 1] + eta[t]
plt.plot(walk, label="random walk")
plt.plot(ar, label="AR(1), phi1 = 0.9")
plt.legend(); plt.title("Same innovations: a level that wanders and one that returns"); plt.show()
show("KC: AR(1) stationary sd (%)", 1.2 / math.sqrt(1 - 0.81), ".3f", "2.753")
""")

md(r"""
## Part 4 — AR and MA models

[[eg:ar1]] regresses $b_t$ on a constant and $b_{t-1}$: first by hand from the normal equations, then with statsmodels' OLS. The partial autocorrelation at lag $k$ is the last coefficient of an OLS regression on lags 1 to $k$; `pacf(method="ols")` gives the same numbers ([[ex:acf]]).
""")

code(r"""
def ols(X, y):
    beta = np.linalg.solve(X.T @ X, X.T @ y)
    e = y - X @ beta
    s2 = float(e @ e) / (len(y) - X.shape[1])
    return beta, np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X))), e


bb = BP * b
X = np.column_stack([np.ones(N - 1), bb[:-1]])
beta, se, e = ols(X, bb[1:])
c_hat, phi_hat = beta
half = math.log(0.5) / math.log(phi_hat)
show("c (bp)", c_hat, ".2f", "-5.66")
show("phi_hat", phi_hat, ".4f", "0.7758")
show("classical SE", se[1], ".5f", "0.00824")
show("s_eps (bp)", math.sqrt(float(e @ e) / (N - 1 - 2)), ".1f", "36.7")
show("half-life", half, ".2f", "2.73")
show("implied mean (bp)", c_hat / (1 - phi_hat), ".2f", "-25.25")

import statsmodels.api as sm
fit = sm.OLS(bb[1:], X).fit()
print("statsmodels:", fit.params, fit.bse)
assert np.allclose(fit.params, beta) and np.allclose(fit.bse, se)

# partial autocorrelations by regression, against pacf(method="ols")
pac_hand = []
for k in range(1, 21):
    Xk = np.column_stack([np.ones(N - k)] + [b[k - j:N - j] for j in range(1, k + 1)])
    pac_hand.append(ols(Xk, b[k:])[0][-1])
pac = pacf(b, nlags=20, method="ols")[1:]
assert np.allclose(pac_hand, pac)
acf_b = acf(b, nlags=20, fft=False)[1:]
print("ACF :", np.round(acf_b[:5], 3), "... lag 10", round(acf_b[9], 3), "lag 20", round(acf_b[19], 3))
print("PACF:", np.round(pac[:5], 3), "max beyond lag 5", round(float(np.abs(pac[5:]).max()), 3))
show("PACF lag 2", pac[1], ".3f", "0.230")
show("PACF lag 3", pac[2], ".3f", "0.109")
""")

md(r"""
## Part 5 — Tests for autocorrelation

[[eg:lag1]] compares the iid band with the robust standard error (25.4); [[ex:robust]] does it for 30 lags. [[eg:portmanteau]] adds Ljung–Box (25.5) and the variance-ratio test (25.6) on LM19's overlapping $\operatorname{VR}(m)$. Problems 6 and 12 redo the arithmetic from the printed, rounded inputs.
""")

code(r"""
def se_rob(x, k):
    c = x - x.mean()
    return math.sqrt(float((c[k:] ** 2 * c[:-k] ** 2).sum())) / float(c @ c)


rho = np.array([rho_hat(r, k) for k in range(1, 31)])
rob = np.array([se_rob(r, k) for k in range(1, 31)])
assert np.allclose(rho, acf(r, nlags=30, fft=False)[1:])
se_iid = 1 / math.sqrt(T)
show("rho_1", rho[0], ".4f", "0.0393")
show("iid SE", se_iid, ".6f", "0.013076")
show("robust SE lag 1", rob[0], ".4f", "0.0205")
show("iid t-stat", rho[0] / se_iid, ".2f", "3.01")
show("robust t-stat", rho[0] / rob[0], ".2f", "1.92")
out_iid = [k for k in range(1, 31) if abs(rho[k - 1]) > 1.96 * se_iid]
out_rob = [k for k in range(1, 31) if abs(rho[k - 1]) > 1.96 * rob[k - 1]]
print("outside the iid band:", out_iid, "| outside the robust band:", out_rob)
assert len(out_iid) == 9 and out_rob == [8, 14]

lags = np.arange(1, 31)
plt.fill_between(lags, -1.96 * rob, 1.96 * rob, alpha=0.2, label="robust band")
plt.fill_between(lags, -1.96 * se_iid, 1.96 * se_iid, alpha=0.3, label="iid band")
plt.scatter(lags, rho, s=14, label="sample autocorrelation of r")
plt.legend(); plt.title("[[ex:robust]]"); plt.show()
""")

code(r"""
lb = acorr_ljungbox(r, lags=[10]).to_numpy()          # a DataFrame: [[Q, p-value]]
q_hand = T * (T + 2) * sum(rho[k] ** 2 / (T - k - 1) for k in range(10))
assert abs(q_hand - lb[0, 0]) < 1e-8
show("Q_LB(10)", lb[0, 0], ".1f", "37.1")
print(f"p-value {lb[0, 1]:.1e}; chi2_10 5% point {stats.chi2.isf(0.05, 10):.2f}")
show("|r|: Q_LB(10)", acorr_ljungbox(np.abs(r), lags=[10]).to_numpy()[0, 0], ",.0f", "1,820")


def vr(x, m):     # LM19's (19.8): overlapping m-day sums centred at m * mean
    cs = np.concatenate([[0.0], np.cumsum(x)])
    sums = cs[m:] - cs[:-m]
    return float(((sums - m * x.mean()) ** 2).mean()) / (m * float(((x - x.mean()) ** 2).mean()))


for m in (2, 5, 10, 20):
    w = 2 * (1 - np.arange(1, m) / m)
    se_i = math.sqrt(2 * (2 * m - 1) * (m - 1) / (3 * m * T))
    se_r = math.sqrt(float((w ** 2) @ (rob[: m - 1] ** 2)))
    v = vr(r, m)
    print(f"m = {m:2d}: VR {v:.4f}, t iid {(v - 1) / se_i:.2f}, t robust {(v - 1) / se_r:.2f}")
show("VR(2) t iid", (vr(r, 2) - 1) / math.sqrt(2 * 3 * 1 / (3 * 2 * T)), ".2f", "3.00")
""")

code(r"""
# Problem 6: Ljung-Box and robust t-stats from the printed four-decimal inputs
rho4 = [0.0393, 0.0000, -0.0031, -0.0323, -0.0173]
rob4 = [0.0205, 0.0210, 0.0227, 0.0178, 0.0196]
assert rho4 == [round(x, 4) + 0.0 for x in rho[:5]] and rob4 == [round(x, 4) for x in rob[:5]]
q5 = T * (T + 2) * sum(rho4[k] ** 2 / (T - k - 1) for k in range(5))
show("P6 Q_LB(5) from printed inputs", q5, ".2f", "16.96")
show("P6 Q_LB(5) unrounded", acorr_ljungbox(r, lags=[5]).to_numpy()[0, 0], ".2f", "16.98")
print("P6 robust t-stats:", [f"{a / c:.2f}" for a, c in zip(rho4, rob4)], "| chi2_5 5% point",
      f"{stats.chi2.isf(0.05, 5):.2f}")

# Problem 12: VR(5), iid and robust t-stats (robust SEs of Problem 6)
v5 = vr(r, 5)
se_i5 = math.sqrt(72 / (15 * 5849))
se_r5 = math.sqrt(sum((2 * (1 - k / 5)) ** 2 * rob4[k - 1] ** 2 for k in range(1, 5)))
show("P12 VR(5)", v5, ".4f", "1.0465")
show("P12 iid SE", se_i5, ".5f", "0.02865")
show("P12 t iid", (v5 - 1) / se_i5, ".2f", "1.62")
show("P12 robust SE", se_r5, ".5f", "0.04573")
show("P12 t robust", (v5 - 1) / se_r5, ".2f", "1.02")
""")

md(r"""
## Part 6 — Unit roots

Experiment 1 simulates the Dickey–Fuller null ([[eg:dfsim]], [[ex:dfnull]]): random walks $x_t=z_1+\dots+z_t$ of 5,850 levels, drawn in chunks of 500, each with the DF t-stat of (25.7) (constant, no lags, classical standard error). [[eg:adf]] then runs `adfuller` and `kpss` on $\ln S_t$ and $b_t$. MacKinnon's constant-only points and p-values assume no drift: for the drifting $\ln S_t$ the no-lag p-value does not apply, and the module tests the index with a trend. Problem 10 repeats experiment 1's idea on one year of 246 levels.
""")

code(r"""
def df_tstats(e, length, n):
    rng = np.random.default_rng([e, SEED])
    out = np.empty(n)
    for c0 in range(0, n, 500):
        x = np.cumsum(rng.standard_normal((500, length)), axis=1)
        dy, xl = np.diff(x, axis=1), x[:, :-1]
        xm, ym = xl - xl.mean(axis=1, keepdims=True), dy - dy.mean(axis=1, keepdims=True)
        sxx = (xm * xm).sum(axis=1)
        d = (xm * ym).sum(axis=1) / sxx
        s2 = ((ym - d[:, None] * xm) ** 2).sum(axis=1) / (length - 3)
        out[c0:c0 + 500] = d / np.sqrt(s2 / sxx)
    return out


def batch_se(x, fn):
    vals = np.array([fn(p) for p in np.split(x, 20)])
    return float(vals.std(ddof=0) / math.sqrt(20))


def q05(x):
    return float(np.quantile(x, 0.05, method="inverted_cdf"))


t1 = df_tstats(1, 5850, 10_000)
print("1%, 5%, 10% points:", np.round(np.quantile(t1, [0.01, 0.05, 0.10], method="inverted_cdf"), 2))
show("exp 1: 5% point", q05(t1), ".2f", "-2.86")
show("exp 1: batch SE", batch_se(t1, q05), ".3f", "0.014")
show("exp 1: mean", t1.mean(), ".2f", "-1.54")
show("exp 1: share below -1.645 (%)", 100 * (t1 < -1.645).mean(), ".1f", "46.7")
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    a0 = adfuller(b, maxlag=0, autolag=None, result_object=True)
print("MacKinnon for 5,849 observations:", {k: round(v, 2) for k, v in a0.critical_values.items()})
edges = np.arange(-55, 26) / 10
plt.hist(t1, bins=edges, density=True, alpha=0.5, label="simulated DF t-stat")
z = np.linspace(-5.5, 2.5, 200)
plt.plot(z, stats.norm.pdf(z), label="standard normal")
plt.axvline(q05(t1), ls="--", color="grey"); plt.axvline(-1.645, ls=":", color="grey")
plt.legend(); plt.title("[[ex:dfnull]]"); plt.show()
""")

code(r"""
lnS = np.log(S)
X1 = np.column_stack([np.ones(N - 1), lnS[:-1]])
beta_s, se_s, _ = ols(X1, np.diff(lnS))
show("ln S: DF t by hand", beta_s[1] / se_s[1], ".2f", "1.19")
show("ln S: phi_hat", 1 + beta_s[1], ".6f", "1.000392")
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    a_s = adfuller(lnS, regression="ct", autolag="AIC", result_object=True)
    k_s = kpss(lnS, regression="c", nlags="auto", result_object=True)
    a_b = adfuller(b, regression="c", autolag="AIC", result_object=True)
    k_b = kpss(b, regression="c", nlags="auto", result_object=True)
show("ln S: ADF 'ct'", a_s.statistic, ".2f", "-0.77")
print("ln S: ADF p-value", round(a_s.pvalue, 2), "with", a_s.lags, "lags; KPSS", round(k_s.statistic, 3),
      "p", "below 0.01 (the table's bound)" if k_s.pvalue <= 0.01 else round(k_s.pvalue, 3))
show("b: ADF 'c'", a_b.statistic, ".2f", "-9.00")
print("b: ADF lags", a_b.lags, "p-value", f"{a_b.pvalue:.1e}")
show("b: KPSS", k_b.statistic, ".3f", "0.664")
show("b: KPSS p-value", k_b.pvalue, ".3f", "0.017")

# Problem 9: the DF regression by hand, rolled and roll-free
Xb = np.column_stack([np.ones(N - 1), b[:-1]])
beta_r, se_r, _ = ols(Xb, db)
beta_f, se_f, _ = ols(Xb, db_free)
show("P9 rolled t", beta_r[1] / se_r[1], ".2f", "-27.20")
show("P9 adfuller(maxlag=0)", a0.statistic, ".2f", "-27.20")
show("P9 roll-free t", beta_f[1] / se_f[1], ".2f", "-29.66")
show("P9 half-life rolled", math.log(0.5) / math.log(1 + beta_r[1]), ".2f", "2.73")
show("P9 half-life roll-free", math.log(0.5) / math.log(1 + beta_f[1]), ".2f", "2.72")
""")

code(r"""
# Problem 10: experiment 3, one year of 246 levels, 100,000 walks
t3 = df_tstats(3, 246, 100_000)
show("P10 5% point", q05(t3), ".2f", "-2.87")
show("P10 batch SE", batch_se(t3, q05), ".3f", "0.006")
p3 = (t3 < -1.645).mean()
show("P10 share below -1.645 (%)", 100 * p3, ".1f", "45.7")
show("P10 its SE (%)", 100 * math.sqrt(p3 * (1 - p3) / 1e5), ".2f", "0.16")
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    crit245 = adfuller(np.log(S[:246]), maxlag=0, autolag=None,       # any 246 levels: the points depend on nobs
                       result_object=True).critical_values["5%"]
show("P10 MacKinnon 5% for 245 observations", crit245, ".2f", "-2.87")
""")

md(r"""
## Part 7 — Spurious regression and cointegration

Experiment 2 regresses one random walk on an independent one, 1,000 times ([[eg:spur]]); its first pair is [[ex:spurious]]. [[eg:englegranger]] estimates the cointegrating regression of $\ln F_t$ on $\ln S_t$, tests it with `coint`, and fits the error-correction regressions of the roll-free changes with White (HC0) standard errors. Problem 11 repeats experiment 2 on 246 sessions.
""")

code(r"""
def spurious(e, length, n):
    rng = np.random.default_rng([e, SEED])
    tt, r2, first = np.empty(n), np.empty(n), None
    for i in range(n):
        xy = np.cumsum(rng.standard_normal((2, length)), axis=1)     # x first, then y
        Xs = np.column_stack([np.ones(length), xy[0]])
        beta_, se_, e_ = ols(Xs, xy[1])
        tt[i] = beta_[1] / se_[1]
        r2[i] = 1 - float(e_ @ e_) / float(((xy[1] - xy[1].mean()) ** 2).sum())
        if i == 0:
            bd, sd, _ = ols(np.column_stack([np.ones(length - 1), np.diff(xy[0])]), np.diff(xy[1]))
            first = (beta_[1], tt[0], r2[0], bd[1] / sd[1], xy)
    return tt, r2, first


def med(x):
    return float(np.quantile(x, 0.5, method="inverted_cdf"))


tt2, r22, first = spurious(2, 5850, 1000)
show("first pair: slope", first[0], ".2f", "0.61")
show("first pair: t-stat", first[1], ".1f", "23.5")
show("first pair: R-squared", first[2], ".3f", "0.086")
show("first pair: t-stat on differences", first[3], ".2f", "-0.98")
show("share |t| > 1.96 (%)", 100 * (np.abs(tt2) > 1.96).mean(), ".1f", "96.6")
show("median |t|", med(np.abs(tt2)), ".0f", "36")
show("median R-squared", med(r22), ".2f", "0.18")
plt.plot(first[4][0], label="x_t"); plt.plot(first[4][1], label="y_t")
plt.legend(); plt.title("[[ex:spurious]]"); plt.show()

tt4, r24, _ = spurious(4, 246, 1000)
p4 = (np.abs(tt4) > 1.96).mean()
show("P11 share (%)", 100 * p4, ".1f", "81.7")
show("P11 its SE (%)", 100 * math.sqrt(p4 * (1 - p4) / 1000), ".1f", "1.2")
show("P11 median R-squared", med(r24), ".2f", "0.17")
show("P11 batch SE", batch_se(r24, med), ".3f", "0.011")
""")

code(r"""
lnF = np.log(F)
beta_eg, se_eg, e_eg = ols(np.column_stack([np.ones(N), lnS]), lnF)
show("EG intercept", beta_eg[0], ".4f", "-0.0283")
show("EG slope", beta_eg[1], ".4f", "1.0028")
show("EG residual rho_1", rho_hat(e_eg, 1), ".3f", "0.764")
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    cg = coint(lnF, lnS, trend="c", return_results=True)
show("coint t", cg.coint_t, ".2f", "-9.42")
print("coint p-value", f"{cg.pvalue:.1e}", "| 5% point", round(cg.critical_values[1], 2))


def hc0(X, e):
    xtxi = np.linalg.inv(X.T @ X)
    return np.sqrt(np.diag(xtxi @ ((X * e[:, None] ** 2).T @ X) @ xtxi))


bF, _, eF = ols(Xb, rF)
bS, _, eS = ols(Xb, rS)
show("alpha_F", bF[1], ".4f", "-0.1597")
show("alpha_F White SE", hc0(Xb, eF)[1], ".3f", "0.055")
show("alpha_F t-stat (HC0)", bF[1] / hc0(Xb, eF)[1], ".1f", "-2.9")
print(f"its two-sided p-value {2 * stats.norm.sf(abs(bF[1] / hc0(Xb, eF)[1])):.4f}; Bonferroni's level for 24 tests "
      f"{0.05 / 24:.5f}")
show("alpha_S", bS[1], "+.4f", "+0.0655")
show("alpha_S White SE", hc0(Xb, eS)[1], ".3f", "0.040")
show("alpha_F - alpha_S = roll-free delta", bF[1] - bS[1], ".4f", "-0.2252")
""")

md(r"""
## Part 8 — The basis as a time series

On sample D: convergence at expiry ([[ex:expiry]]), roll jumps, the dividend season ([[ex:season]]) and the four versions of [[ex:versions]]. Then [[eg:arma]]: the ARMA(1,1) at the likelihood maximum, its standard errors from $-\ell''$ checked against a central-difference Hessian, the delta-method half-life, the sandwich, the regimes and 2025.
""")

code(r"""
for k in (20, 10, 2):
    m_ = D & (sess == k)
    print(f"{k:2d} sessions before ({int(m_.sum())} dates): mean b {BP * b[m_].mean():.2f}, "
          f"s {BP * b[m_].std():.2f}, mean fair {BP * fair[m_].mean():.2f} bp")
show("20 sessions: mean", BP * b[D & (sess == 20)].mean(), ".2f", "-37.95")
show("2 sessions: s", BP * b[D & (sess == 2)].std(), ".2f", "35.13")
ks = np.arange(20, 1, -1)
mb = np.array([BP * b[D & (sess == k)].mean() for k in ks])
sb = np.array([BP * b[D & (sess == k)].std() for k in ks])
mf = np.array([BP * fair[D & (sess == k)].mean() for k in ks])
plt.fill_between(-ks, mb - sb, mb + sb, alpha=0.2, label="mean +- one sd")
plt.plot(-ks, mb, label="mean log basis"); plt.plot(-ks, mf, "--", label="mean fair log basis")
plt.legend(); plt.title("[[ex:expiry]] (x: minus sessions to expiry)"); plt.show()

jump = (db - db_free)[roll[1:]]
rmon = mon[1:][roll[1:]]
show("roll jumps: mean", BP * jump.mean(), ".1f", "-37.5")
show("June roll", BP * jump[rmon == 6].mean(), ".1f", "-144.7")
show("July roll", BP * jump[rmon == 7].mean(), ".2f", "-104.95")
# the share of a calendar year's dividends (TR - price log gap from the previous year's last close) that went ex in the
# life of the contract entered at the June and the July roll, 2003-2025
for mm, printed in ((6, "45"), (7, "39")):
    sh = []
    for y in range(2003, 2026):
        yi = np.flatnonzero(yr == y)
        j0 = max(int(yi[0]) - 1, 0)
        gap = math.log(TRI[yi[-1]] / TRI[j0]) - math.log(S[yi[-1]] / S[j0])
        i_roll = next(int(i) for i in yi if roll[i] and mon[i] == mm)
        sh.append(qt[i_roll] / gap)
    show(f"roll in month {mm}: mean share of the year's dividends (%)", 100 * np.mean(sh), ".0f", printed)

season = pl.DataFrame({"month": mon[D], "b": BP * b[D], "fair": BP * fair[D], "resid": BP * resid[D]})
by_month = season.group_by("month").agg(pl.col("b", "fair", "resid").mean(), pl.len()).sort("month")
print(by_month)
show("June mean b", by_month.filter(pl.col("month") == 6)["b"][0], ".2f", "-74.80")
show("June fair", by_month.filter(pl.col("month") == 6)["fair"][0], ".2f", "-67.43")
show("D: carry", BP * (RF * tau[D]).mean(), "+.2f", "+9.73")
show("D: dividends", -BP * qt[D].mean(), ".2f", "-17.54")
show("D: residual", BP * resid[D].mean(), ".2f", "-17.76")
""")

code(r"""
def arma_fit(x, strict=True):
    # ARMA(1,1) at the likelihood maximum: innovations MLE, then a restart that must not raise the log-likelihood
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = ARIMA(x, order=(1, 0, 1))
        f0 = model.fit(method="innovations_mle")
        f1 = model.fit(start_params=f0.params, cov_type="approx")
        default = model.fit()
    if strict:
        assert f1.llf - f0.llf < 1e-6 and f1.llf >= default.llf - 1e-9
    return model, f1, default


def half_life(phi):
    return math.log(0.5) / math.log(phi)


mb_month = {mm: b[D & (mon == mm)].mean() for mm in range(1, 13)}
versions = {"b": b[D], "b - carry": (b - RF * tau)[D], "residual": resid[D],
            "b - month mean": (b - np.array([mb_month[mm] for mm in mon]))[D]}
for name, x in versions.items():
    xb = BP * x
    Xv = np.column_stack([np.ones(len(x) - 1), x[:-1]])
    bv, sv, _ = ols(Xv, np.diff(x))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        av = adfuller(x, regression="c", autolag="AIC", result_object=True)
        kv = kpss(x, regression="c", nlags="auto", result_object=True)
    _, fv, _ = arma_fit(xb)
    mean_txt = f"{xb.mean():6.1f}".replace("-0.0", " 0.0")          # the month-mean version averages 0 exactly
    kp_txt = f"p {kv.pvalue:.3f}" if kv.pvalue > 0.01 else "p <0.01, the table's bound"
    print(f"{name:15s} mean {mean_txt}  s {xb.std():6.2f}  DF {bv[1] / sv[1]:6.1f}  ADF {av.statistic:6.2f} "
          f"({av.lags})  KPSS {kv.statistic:.2f} ({kp_txt})  AR {1 + bv[1]:.4f} "
          f"({half_life(1 + bv[1]):.2f})  ARMA {fv.params[1]:.5f}, {fv.params[2]:.3f} ({half_life(fv.params[1]):.2f})")
""")

code(r"""
model, fit_b, default = arma_fit(BP * b)
p, se_p = fit_b.params, fit_b.bse
show("llf gap of the default fit", fit_b.llf - default.llf, ".3f", "0.006")
show("mean", p[0], ".1f", "-25.5")
show("phi1", p[1], ".5f", "0.90620")
show("SE(phi1), -l''", se_p[1], ".6f", "0.007055")
show("theta1", p[2], ".4f", "-0.3553")
show("sigma2 (bp^2)", p[3], ",.1f", "1,257.0")

# -l'' by hand: a central-difference Hessian of the log-likelihood
h = 1e-5 * np.maximum(1.0, np.abs(p))
H = np.empty((4, 4))
for i in range(4):
    for j in range(4):
        def ll(si, sj):
            q = p.copy(); q[i] += si * h[i]; q[j] += sj * h[j]
            return float(model.loglike(q))
        H[i, j] = (ll(1, 1) - ll(1, -1) - ll(-1, 1) + ll(-1, -1)) / (4 * h[i] * h[j])
se_hand = np.sqrt(np.diag(np.linalg.inv(-H)))
print("SEs, statsmodels approx:", np.round(se_p, 6), "| by hand:", np.round(se_hand, 6))
assert np.allclose(se_hand, se_p, rtol=1e-3)

# (25.9): a persistent AR(1) plus one-day noise
phi, theta, s2 = p[1], p[2], p[3]
su2 = -theta * s2 / phi
sz2 = (1 + theta ** 2) * s2 - (1 + phi ** 2) * su2
sx2 = sz2 / (1 - phi ** 2)
var_change = 2 * sx2 * (1 - phi) + 2 * su2
show("sigma_u (bp)", math.sqrt(su2), ".1f", "22.2")
show("sigma_zeta (bp)", math.sqrt(sz2), ".1f", "22.8")
show("persistent sd (bp)", math.sqrt(sx2), ".1f", "53.8")
show("noise share of the variance of a day's change (%)", 100 * 2 * su2 / var_change, ".0f", "64")
show("model sd of a change (bp)", math.sqrt(var_change), ".2f", "39.11")

hl = half_life(phi)
hl_se = abs(math.log(0.5) / (phi * math.log(phi) ** 2)) * se_p[1]
show("half-life", hl, ".2f", "7.04")
show("delta-method SE", hl_se, ".3f", "0.556")
print(f"95% interval {hl - 1.96 * hl_se:.2f} to {hl + 1.96 * hl_se:.2f}")
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    se_sand = model.smooth(p, cov_type="robust_approx").bse
    se_opg = model.smooth(p, cov_type="opg").bse
    se_oim = model.smooth(p, cov_type="oim").bse
show("sandwich SE(phi1)", se_sand[1], ".5f", "0.01462")
show("'opg' SE(phi1)", se_opg[1], ".5f", "0.00385")
show("'oim' SE(phi1)", se_oim[1], ".4f", "0.0068")
hs = abs(math.log(0.5) / (phi * math.log(phi) ** 2)) * se_sand[1]
print(f"sandwich interval {hl - 1.96 * hs:.2f} to {hl + 1.96 * hs:.2f}")
""")

code(r"""
# stability check by limit regime, then 2025 alone (each window's changes within the window)
for name, msk in (("before 1 June 2015", pre), ("from 1 June 2015", ~pre), ("2025", yr == 2025)):
    x = b[msk]
    _, f_, _ = arma_fit(BP * x)
    ph, th, s2_ = f_.params[1], f_.params[2], f_.params[3]
    su = math.sqrt(-th * s2_ / ph)
    Xw = np.column_stack([np.ones(len(x) - 1), x[:-1]])
    bw, sw, _ = ols(Xw, np.diff(x))
    print(f"{name}: {len(x)} dates, DF t {bw[1] / sw[1]:.2f}, ARMA phi {ph:.4f} theta {th:.4f} sigma2 {s2_:.1f}, "
          f"sigma_u {su:.2f} bp")
m25 = yr == 2025
_, f25, _ = arma_fit(BP * b[m25])
su25 = math.sqrt(-f25.params[2] * f25.params[3] / f25.params[1])
show("2025 sigma_u (bp)", su25, ".1f", "23.4")
show("2025 sigma_u in index points (a conversion at the mean close)", su25 / BP * S[m25].mean(), ".0f", "56")
# measured in points: the changes of F - S within 2025, rolled and roll-free (the contract held over the day)
F_held = tx23["F_held"].to_numpy()
i25 = np.flatnonzero(m25)[1:]                  # both days in 2025
pts_rolled = (F[i25] - S[i25]) - (F[i25 - 1] - S[i25 - 1])
pts_free = (F_held[i25] - F[i25 - 1]) - (S[i25] - S[i25 - 1])
print("changes within 2025:", len(i25), "| rolls among them:", int(roll[i25].sum()))
show("2025 sd of rolled changes of F - S (points)", pts_rolled.std(), ".1f", "81.4")
show("2025 sd of roll-free changes of F - S (points)", pts_free.std(), ".1f", "76.7")

# Problem 8: (25.9) from the regimes' estimates printed to four decimals
for ph, th, s2_ in ((0.9035, -0.3606, 1659.9), (0.9101, -0.3427, 808.6)):
    su2_ = -th * s2_ / ph
    sx2_ = ((1 + th ** 2) * s2_ - (1 + ph ** 2) * su2_) / (1 - ph ** 2)
    print(f"phi {ph}: sigma_u {math.sqrt(su2_):.2f} bp, persistent sd {math.sqrt(sx2_):.2f} bp, noise share of the "
          f"variance of a day's change {100 * 2 * su2_ / (2 * sx2_ * (1 - ph) + 2 * su2_):.1f}%")
""")

md(r"""
## Part 9 — The module's Python block, and an extension

The block below is Section 8's code as printed, run on this notebook's arrays (`b`, `F`, `S`, `r`).
""")

code(r"""
import numpy as np
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import acf, adfuller, coint, kpss, pacf

rho = acf(r, nlags=30, fft=False)[1:]        # (19.5), divisor T
pac = pacf(b, nlags=20, method="ols")[1:]    # the default is "ywadjusted"
lb = acorr_ljungbox(r, lags=[10]).to_numpy() # [[Q_LB(10), p-value]]
a = adfuller(b, regression="c", autolag="AIC", result_object=True)
a0 = adfuller(b, maxlag=0, autolag=None, result_object=True)
k = kpss(b, regression="c", nlags="auto", result_object=True)
eg = coint(np.log(F), np.log(S), trend="c", return_results=True)
model = ARIMA(1e4 * b, order=(1, 0, 1))      # basis in bp; const = mean
f0 = model.fit(method="innovations_mle")
f = model.fit(start_params=f0.params, cov_type="approx")  # restart, -l''
print(a.statistic, a.lags, a0.statistic, f.params, f.bse)
""")

md(r"""
### Extension: the basis's half-lives year by year (stability check)

Fit the AR(1) by OLS and the ARMA(1,1) at the likelihood maximum to each calendar year's log basis, with changes within the year only. Does the persistent part's half-life drift with the years, and does the noise (25.9) follow the limit regimes? A year has about 246 sessions, so expect wide intervals; a year-by-year table is a stability check, not a test (LM34 tests on later data).
""")

code(r"""
rows_y = []
for y in range(2003, 2027):
    x = BP * b[yr == y]
    Xy = np.column_stack([np.ones(len(x) - 1), x[:-1]])
    phi_y = ols(Xy, x[1:])[0][1]
    _, fy, _ = arma_fit(x, strict=False)
    rows_y.append({"year": y, "dates": len(x), "AR(1) phi": round(phi_y, 3),
                   "AR(1) half-life": round(half_life(phi_y), 2) if 0 < phi_y < 1 else None,
                   "ARMA phi": round(float(fy.params[1]), 3),
                   "ARMA half-life": round(half_life(fy.params[1]), 2) if 0 < fy.params[1] < 1 else None})
print(pl.DataFrame(rows_y))
# your code: add sigma_u by (25.9) to each row and plot it against the year
""")

nb = nbf.v4.new_notebook()
nb["cells"] = cells
nb["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                  "language_info": {"name": "python"}}
nbf.write(nb, LAB / "LM25_lab.ipynb")

(LAB / "README.md").write_text("""# LM25 Lab — Time Series I: ARMA, Unit Roots and Cointegration

Companion to *From Calculus to Kelly*, Learning Module 25. The notebook builds TX23 (the TX near-month future against the TAIEX) from the daily futures file with the module's roll rule, rebuilds the module's exhibits and computational examples (stationarity, AR and MA models, tests for autocorrelation, unit-root tests, spurious regression and cointegration, the basis as a time series), runs the four simulation experiments and works the computational practice problems.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM25_lab/LM25_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM25_lab.ipynb
```

`build/make_lab25.py` generates the notebook and this README: edit the generator, not the generated files.

## Data (FinMind; not in the repository)

The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

The same steps in a shell (`data/raw/` and this folder's `data/` are git-ignored):

```bash
export FINMIND_TOKEN=...               # your FinMind API token
uv run python data/fetch_finmind.py    # rebuilds and verifies data/raw/
uv run python data/make_lab_data.py    # writes every lab's data/ folder
```

`fetch_finmind.py` checks every file against `data/raw_manifest.json`. The notebook reads only the files in its own `data/` folder, all from FinMind's free datasets:

| File | Content |
|:--|:--|
| `data/taiex_tr.csv` | `date`, `price`: the daily closes of the TAIEX total-return index (FinMind `TaiwanStockTotalReturnIndex`, data_id TAIEX), 2003-01-02 → 2026-10-08 |
| `data/taiex_price.csv` | `date`, `close`, `spread`: the TAIEX price closes (FinMind `TaiwanStockPrice`), on the same 5,850 dates |
| `data/tx_daily.csv` | `date`, `contract_date`, `close`, `spread`, `settlement_price`, `volume`, `open_interest`: the regular-session rows of the monthly TX contracts (FinMind `TaiwanFuturesDaily`, data_id TX), 1998-07-21 → 2026-10-16 |
""", encoding="utf-8", newline="\n")
print("wrote", LAB / "LM25_lab.ipynb", "and README.md | labels:", {k: ("X" if w == "Exhibit" else "E") + str(n) for k, (w, n) in NUM.items()})
