"""Generate labs/LM33_lab (Polars-first notebook + README) for LM33, The Statistics of the Sharpe Ratio.

Run:  uv run python build/make_lab33.py
Then execute from inside the lab folder:
      cd labs/LM33_lab && uv run jupyter nbconvert --to notebook --execute --inplace LM33_lab.ipynb

The notebook reads only labs/LM33_lab/data/, built by data/make_lab_data.py from data/raw/ (FinMind's licence keeps raw
data out of the repository): rule_wealth_net.csv (the eight rules' net wealth paths of the through case, from
data/vol5_rules.py, on the wealth frame's dates from the first trade) and taiex_tr.csv (TR23, the TAIEX total-return
index). It carries no copy of vol5_rules.py: it reads the rules' wealth, rebuilds every LM33 statistic by hand and
checks it against the module's printed values. This script writes the notebook and the README only.

Exhibit and example numbers are never typed by hand: cells write [[ex:label]] / [[eg:label]], and the generator
resolves them from the labels in src/lm33.md, numbered in document order as build/build.py does.
"""
import re
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "LM33_lab"
LAB.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- exhibit / example numbers from the module's labels
NUM: dict[tuple[str, str], int] = {}
_count = {"exhibit": 0, "example": 0}
for m in re.finditer(r"(?m)^(?:>\s?)+\[!(exhibit|example)\][+-]?\s*(.*)$", (ROOT / "src" / "lm33.md").read_text(encoding="utf-8")):
    _count[m.group(1)] += 1
    lab = re.search(r"\{#([\w-]+)\}\s*$", m.group(2))
    if lab:
        NUM[("ex" if m.group(1) == "exhibit" else "eg", lab.group(1))] = _count[m.group(1)]


def refs(s: str) -> str:
    """Replace [[ex:a]] and [[eg:a]] by 'Exhibit k' and 'Example k'."""
    def rep(m: re.Match[str]) -> str:
        kind, a = m.group(1), m.group(2)
        return f"{'Exhibit' if kind == 'ex' else 'Example'} {NUM[(kind, a)]}"
    out = re.sub(r"\[\[(ex|eg):([\w-]+)\]\]", rep, s)
    assert not re.search(r"\[\[(ex|eg):", out) and "[[LM" not in out, out
    return out


cells: list = []


def md(s: str) -> None:
    cells.append(nbf.v4.new_markdown_cell(refs(s.strip("\n"))))


def code(s: str) -> None:
    cells.append(nbf.v4.new_code_cell(refs(s.strip("\n"))))


md(r"""
# LM33 Lab — The Statistics of the Sharpe Ratio

Companion notebook to **From Calculus to Kelly, LM33**. It rebuilds the module's exhibits and computational examples from the through case's eight net wealth paths and from TR23, solves the computational practice problems, and ends with an extension exercise.

| Part | Rebuilds |
|:--|:--|
| 1 | Data: $R_t$, $x_t$, $T$, $A_{\mathrm w}$, the 90 calendar months and TR23; a check against the module's Sharpe ratios |
| 2 | (20.9) for the eight rules: [[ex:case]] (a), [[ex:forest]], [[eg:r2hand]], [[eg:checkpoint]]; `scipy.stats` with every option passed; the illustrative $r_f$ |
| 3 | (33.1) by hand: [[ex:haclag]], [[eg:hac]], [[eg:tr23]], problem 11 (b) |
| 4 | Lo's correction on 90 months: [[eg:monthly]], the AR(1) check, problem 10 |
| 5 | PSR and MinTRL: [[ex:psrT]], [[eg:mintrl]], Bailey and López de Prado's 2012 example |
| 6 | Ledoit and Wolf's test by hand: experiment 1, [[ex:case]] (b), [[ex:pairs]], [[eg:lw]], problem 12, experiment 3 |
| 7 | The expected maximum (33.4) by quadrature, experiment 2, [[ex:deflate]], [[eg:dsr]], the 2014 example, problem 8 (b) |
| 8 | Haircuts: [[ex:haircut]], [[eg:hsr]], Harvey and Liu's example |
| 9 | Extension: R2's PSR(0) on rolling windows (a stability check) |

**Environment.** From the repository root, `uv sync` installs the locked Python environment (`uv.lock`). Open this notebook with the `.venv` kernel, or run `uv run --with jupyterlab jupyter lab`.

**Data.** The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

On FinMind's free plan, run `uv run python data/fetch_finmind.py --exclude sectors_close/ --exclude vol4_settlement/ --exclude vol6/etf_snapshot` instead, as the book's Getting Started page says. This lab needs none of the excluded files.

`data/` then holds two files, and the notebook reads nothing outside `data/`:

- `rule_wealth_net.csv`: the through case's eight rules (`data/vol5_rules.py`), their net wealth after each day's trade (`rule`, `date`, `wealth`), on every session of E5's wealth frame from the first trade, 4 March 2019, to 8 October 2026.
- `taiex_tr.csv`: TR23, the TAIEX total-return index as FinMind's `TaiwanStockTotalReturnIndex` serves it (`date`, `price`), 2 January 2003 to 8 October 2026. Its dates are the wealth frame's calendar.

**Conventions (as in the module).**

- A rule's daily net return is $R_t=W_t/W_{t-1}-1$ from the session after the first trade, and its excess return $x_t=R_t-r_f/A_{\mathrm w}$, with the illustrative $r_f=1.5\%$ and $A_{\mathrm w}$ the wealth frame's sessions a year (every TR23 session after the base close of 17 January 2017, over the calendar years from it).
- Means, standard deviations, skewness and raw kurtosis divide by $T$ (normal kurtosis 3). Sharpe ratios are per observation in formulas and annualized by $\sqrt{A_{\mathrm w}}$, $\sqrt{12}$ or TR23's $\sqrt A$ for printing.
- The HAC lag is $\lfloor4(T/100)^{2/9}\rfloor$; the bootstrap block size is $b=22$; PSR, MinTRL and DSR use $\sqrt{T-1}$; intervals are $\pm1.959964$ standard errors.
- Experiments create `np.random.default_rng([e, 20261011])` once: $e=1$ the seven Ledoit–Wolf tests, $e=2$ the correlated maximum, $e=3$ the block sizes. Counts against a statistic use the guard `1e-12`; quantiles use `method="inverted_cdf"`.
""")

code(r"""
import math
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from arch.bootstrap import optimal_block_length
from scipy import integrate, optimize, stats

DATA = Path("data")
RULES = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]
RF, SEED, EULER = 0.015, 20261011, 0.5772156649015329
Z95, Z975 = float(stats.norm.ppf(0.95)), 1.959964
plt.rcParams.update({"figure.figsize": (9, 4.5), "axes.grid": True, "grid.alpha": 0.3,
                     "axes.spines.top": False, "axes.spines.right": False})


def show(label, value, fmt, printed):
    # print a value next to the module's printed value and assert that they agree
    got = format(value, fmt)
    print(f"{label}: {got}   [book: {printed}]")
    assert got == printed, (label, got, printed)


def show_row(label, got, printed):
    # a table row of the module, rebuilt; the module writes minus signs as U+2212
    got = got.replace("-", "−")
    print(f"{label}: {got}")
    assert got == printed, (label, got, printed)


def moments(x):
    # mean, s, sample skewness and raw kurtosis, all with divisor T, (19.3)
    m, s = float(x.mean()), float(x.std(ddof=0))
    c = x - m
    return m, s, float((c**3).mean() / s**3), float((c**4).mean() / s**4)


def v209(sr, sk, ku):
    # (20.9): T Var(SR hat) for iid returns
    return 1 - sr * sk + (ku - 1) / 4 * sr**2


def lag_rule(n):
    return math.floor(4 * (n / 100) ** (2 / 9))


def lrv(V, lag):
    # (23.7)'s Bartlett estimate of the long-run covariance of the centred rows of V, divisor T
    n = V.shape[0]
    S = V.T @ V / n
    for k in range(1, lag + 1):
        G = V[k:].T @ V[:-k] / n
        S = S + (1 - k / (lag + 1)) * (G + G.T)
    return S


def se_sr_hac(x, lag):
    # (33.1): the delta method with the long-run covariance of (x - mean, (x - mean)^2 - s^2)
    m, s, _, _ = moments(x)
    c = x - m
    g = np.array([1 / s, -m / (2 * s**3)])
    return float(np.sqrt(g @ lrv(np.column_stack([c, c**2 - s**2]), lag) @ g / len(x)))


def se_mean_hac(x, lag):
    c = (x - x.mean())[:, None]
    return float(np.sqrt(lrv(c, lag)[0, 0] / len(x)))


def se_vol_hac(x, lag):
    # the SE of s: (x - mean)^2 has a long-run variance; ds / d(s^2) = 1 / (2 s)
    m, s, _, _ = moments(x)
    c = ((x - m) ** 2 - s**2)[:, None]
    return float(np.sqrt(lrv(c, lag)[0, 0] / len(x)) / (2 * s))


def psr(sr, sr0, n_obs, sk, ku):
    # (33.2), with sqrt(T - 1)
    return float(stats.norm.cdf((sr - sr0) * math.sqrt(n_obs - 1) / math.sqrt(v209(sr, sk, ku))))


def mintrl(sr, sr0, sk, ku, conf=0.95):
    # (33.3), in observations
    return 1 + v209(sr, sk, ku) * (stats.norm.ppf(conf) / (sr - sr0)) ** 2


def emax(n):
    # (33.4): E Z_(n) by quadrature of the two integrals
    if n == 1:
        return 0.0
    up = integrate.quad(lambda z: 1 - stats.norm.cdf(z) ** n, 0, 12, limit=200, epsabs=1e-13, epsrel=1e-13)[0]
    lo = integrate.quad(lambda z: stats.norm.cdf(z) ** n, -12, 0, limit=200, epsabs=1e-13, epsrel=1e-13)[0]
    return up - lo


def emax_bldp(n):
    # Bailey and Lopez de Prado's (2014) approximation of E Z_(n)
    return float((1 - EULER) * stats.norm.ppf(1 - 1 / n) + EULER * stats.norm.ppf(1 - 1 / (n * math.e)))


def holm(p):
    # (21.7)'s adjusted p-values, in the input order
    order = sorted(range(len(p)), key=lambda i: p[i])
    adj, run = [0.0] * len(p), 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (len(p) - r) * p[i]))
        adj[i] = run
    return adj


def two_sided(t):
    return float(2 * stats.norm.sf(abs(t)))


def rho1(y):
    # (19.5)'s lag-1 autocorrelation, divisor T in both sums
    c = y - y.mean()
    return float(c[1:] @ c[:-1] / (c @ c))
""")

md(r"""
## Part 1 — Data: the rules' returns, the months and TR23

The rules' wealth paths lie on the wealth frame's dates, every session. $A_{\mathrm w}$ comes from that frame's calendar, which is TR23's.
""")

code(r"""
wl = pl.read_csv(DATA / "rule_wealth_net.csv", schema_overrides={"rule": pl.Utf8, "date": pl.Utf8})
Wd = wl.pivot(on="rule", index="date", values="wealth").sort("date").select("date", *RULES)
dates = Wd["date"].to_list()
WM = Wd.select(RULES).to_numpy()
tr = pl.read_csv(DATA / "taiex_tr.csv", schema_overrides={"date": pl.Utf8}).sort("date")
tr_dates = tr["date"].to_list()
assert dates == [d for d in tr_dates if dates[0] <= d <= dates[-1]], "the paths lie on every session"
frame = [d for d in tr_dates if "2017-01-17" < d <= "2026-10-08"]
years_w = (date(2026, 10, 8) - date(2017, 1, 17)).days / 365.25
Aw = len(frame) / years_w
R = WM[1:] / WM[:-1] - 1
assert (1 + R > 0).all(), "no rule is ruined, so every log below is defined"
X = R - RF / Aw
T = len(R)
sqA = math.sqrt(Aw)
tau = T / Aw
cal = (date.fromisoformat(dates[-1]) - date.fromisoformat(dates[0])).days / 365.25
L = lag_rule(T)
print(f"{T} daily net returns {dates[1]} .. {dates[-1]} (first trade {dates[0]})")
show("T", T, ",d", "1,851")
show("wealth frame sessions", len(frame), ",d", "2,368")
show("A_w", Aw, ".2f", "243.57")
show("years of sessions T / A_w", tau, ".4f", "7.5995")
show("calendar years from the first trade's close", cal, ".4f", "7.5975")
show("HAC lag", L, "d", "7")

ym = [d[:7] for d in dates]
ends = [i for i in range(len(dates)) if i == len(dates) - 1 or ym[i] != ym[i + 1]]
full = np.array([i for i in ends if "2019-03" <= ym[i] <= "2026-09"])
nsess = np.diff(full)
print(f"{len(full) - 1} calendar months {ym[full[1]]} .. {ym[full[-1]]}, {nsess.min()} to {nsess.max()} sessions; "
      f"excluded: {sum(d[:7] == '2019-03' for d in dates[1:])} returns of March 2019 and "
      f"{sum(d[:7] == '2026-10' for d in dates[1:])} of October 2026")

P = tr["price"].to_numpy().astype(float)
Rt = P[1:] / P[:-1] - 1                                  # TR23's simple returns, r_f = 0
Tt = len(Rt)
At = Tt / ((date.fromisoformat(tr_dates[-1]) - date.fromisoformat(tr_dates[0])).days / 365.25)
show("TR23 T", Tt, ",d", "5,849")
show("TR23 A", At, ".2f", "246.12")

mom = {k: moments(X[:, j]) for j, k in enumerate(RULES)}
SR = {k: mom[k][0] / mom[k][1] for k in RULES}
for k, p in zip(RULES, ["0.976", "1.138", "0.775", "0.629", "0.843", "0.955", "0.918", "0.935"]):
    show(f"{k}'s Sharpe ratio a year", SR[k] * sqA, ".3f", p)
""")

md(r"""
## Part 2 — The checkpoint: (20.9) for eight rules

[[ex:case]] (a), [[ex:forest]], [[eg:r2hand]] and [[eg:checkpoint]]. SciPy's `skew` and `kurtosis` are called with every option that changes the number.
""")

code(r"""
SE9 = {k: math.sqrt(v209(SR[k], mom[k][2], mom[k][3]) / T) for k in RULES}
SEN = {k: math.sqrt((1 + SR[k] ** 2 / 2) / T) for k in RULES}
SEH = {k: se_sr_hac(X[:, j], L) for j, k in enumerate(RULES)}
PSR0 = {k: psr(SR[k], 0, T, mom[k][2], mom[k][3]) for k in RULES}
CI9 = {k: ((SR[k] - Z975 * SE9[k]) * sqA, (SR[k] + Z975 * SE9[k]) * sqA) for k in RULES}
CIH = {k: ((SR[k] - Z975 * SEH[k]) * sqA, (SR[k] + Z975 * SEH[k]) * sqA) for k in RULES}
X1A = {
    "R1": "| R1 | 0.976 | 0.370 | 0.363 | 0.26 to 1.69 | 0.996 |",
    "R2": "| R2 | 1.138 | 0.367 | 0.382 | 0.39 to 1.89 | 0.999 |",
    "R3": "| R3 | 0.775 | 0.370 | 0.373 | 0.04 to 1.51 | 0.982 |",
    "R4": "| R4 | 0.629 | 0.368 | 0.340 | −0.04 to 1.30 | 0.956 |",
    "R5": "| R5 | 0.843 | 0.370 | 0.374 | 0.11 to 1.58 | 0.989 |",
    "R6": "| R6 | 0.955 | 0.371 | 0.370 | 0.23 to 1.68 | 0.995 |",
    "R7": "| R7 | 0.918 | 0.370 | 0.368 | 0.20 to 1.64 | 0.993 |",
    "R8": "| R8 | 0.935 | 0.371 | 0.368 | 0.21 to 1.66 | 0.994 |",
}
for k in RULES:
    got = (f"| {k} | {SR[k] * sqA:.3f} | {SE9[k] * sqA:.3f} | {SEH[k] * sqA:.3f} | {CIH[k][0]:.2f} to "
           f"{CIH[k][1]:.2f} | {PSR0[k]:.3f} |")
    show_row(f"[[ex:case]] (a), {k}", got, X1A[k])
print("normal SE a year:", sorted({f"{SEN[k] * sqA:.3f}" for k in RULES}))

fig, ax = plt.subplots(figsize=(8, 4.5))
y = np.arange(8, 0, -1)
ax.errorbar([SR[k] * sqA for k in RULES], y, xerr=[[SR[k] * sqA - CI9[k][0] for k in RULES],
            [CI9[k][1] - SR[k] * sqA for k in RULES]], fmt="o", capsize=0, lw=3, label="(20.9)")
ax.errorbar([SR[k] * sqA for k in RULES], y + 0.2, xerr=[[SR[k] * sqA - CIH[k][0] for k in RULES],
            [CIH[k][1] - SR[k] * sqA for k in RULES]], fmt="none", color="grey", lw=1.2, label="(33.1), lag 7")
ax.axvline(0, ls="--", color="grey")
ax.set_yticks(y, RULES)
ax.set_xlabel("Sharpe ratio a year")
ax.set_title("[[ex:forest]]: eight Sharpe ratios with two intervals")
ax.legend()
plt.show()
""")

code(r"""
x2 = X[:, RULES.index("R2")]
m2, s2, sk2, ku2 = mom["R2"]
show("[[eg:r2hand]]: mean excess (%)", 100 * m2, ".4f", "0.0564")
show("s (%)", 100 * s2, ".3f", "0.774")
show("skewness", sk2, ".3f", "-0.112")
show("raw kurtosis", ku2, ".2f", "13.58")
show("daily ratio", SR["R2"], ".4f", "0.0729")
show("skewness term", -SR["R2"] * sk2, ".4f", "0.0082")
show("kurtosis term", (ku2 - 1) / 4 * SR["R2"] ** 2, ".4f", "0.0167")
show("V", v209(SR["R2"], sk2, ku2), ".4f", "1.0249")
show("SE a day", SE9["R2"], ".4f", "0.0235")
show("SE a year", SE9["R2"] * sqA, ".3f", "0.367")
show("t-stat SR sqrt(T)", SR["R2"] * math.sqrt(T), ".2f", "3.14")

# SciPy with every option passed: bias=True is the divisor T of (19.3); fisher=False is the raw kurtosis
assert abs(stats.skew(x2, bias=True) - sk2) < 1e-12
assert abs(stats.kurtosis(x2, fisher=False, bias=True) - ku2) < 1e-10
show("scipy.stats.kurtosis with its defaults (excess)", float(stats.kurtosis(x2)), ".2f", "10.58")

rows = []
for k in RULES:
    m, s, sk, ku = mom[k]
    se_m, se_v = s / math.sqrt(T) * Aw, s * math.sqrt((ku - 1) / (4 * T)) * sqA
    rows.append(f"| {k} | {100 * m * Aw:.2f} ({100 * se_m:.2f}) | {100 * s * sqA:.2f} ({100 * se_v:.2f}) | "
                f"{sk:.2f} | {ku:.1f} |")
for r in rows:
    print(r.replace("-", "−"))
show_row("[[eg:checkpoint]], R4", rows[3], "| R4 | 10.40 (6.00) | 16.53 (0.59) | −0.66 | 10.3 |")
show_row("[[eg:checkpoint]], R8", rows[7], "| R8 | 10.77 (4.18) | 11.52 (0.63) | −0.42 | 23.0 |")

show("R4's (20.9) interval, low", CI9["R4"][0], ".2f", "-0.09")
show("R4's (20.9) interval, high", CI9["R4"][1], ".2f", "1.35")
show("R4's PSR(0)", PSR0["R4"], ".3f", "0.956")
hp = holm([1 - PSR0[k] for k in RULES])
print("Holm on the eight one-sided p-values: rejections", sum(a <= 0.05 + 1e-12 for a in hp))
show("largest adjusted p-value", max(hp), ".3f", "0.044")

for rate, lo_, hi_ in ((0.0, "0.09", "0.15"), (0.02, "0.03", "0.05")):
    mo = {k: moments(R[:, j] - rate / Aw) for j, k in enumerate(RULES)}
    chg = [abs(mo[k][0] / mo[k][1] - SR[k]) * sqA for k in RULES]
    show(f"r_f {rate:.0%}: smallest change", min(chg), ".2f", lo_)
    show(f"r_f {rate:.0%}: largest change", max(chg), ".2f", hi_)
    p1 = {k: psr(mo[k][0] / mo[k][1], 0, T, mo[k][2], mo[k][3]) for k in RULES}
    print(f"   best {max(p1, key=lambda k: mo[k][0] / mo[k][1])}, worst {min(RULES, key=lambda k: mo[k][0] / mo[k][1])}, "
          f"Holm rejections {sum(a <= 0.05 + 1e-12 for a in holm([1 - p1[k] for k in RULES]))}")
    if rate == 0.02:
        show("r_f 2%: R4's PSR(0)", p1["R4"], ".3f", "0.948")
""")

md(r"""
## Part 3 — The HAC standard error (33.1)

[[ex:haclag]], [[eg:hac]] and [[eg:tr23]]; problem 11 (b). At lag 0, (33.1) equals (20.9).
""")

code(r"""
for j, k in enumerate(RULES):
    assert abs(se_sr_hac(X[:, j], 0) - SE9[k]) < 1e-15
lags = range(61)
curve = {k: [se_sr_hac(X[:, RULES.index(k)], lg) * sqA for lg in lags] for k in ("R1", "R2", "R4")}
for k in ("R1", "R2", "R4"):
    print(k, [f"{curve[k][lg]:.3f}" for lg in (0, 7, 20, 60)])
for lg, p in zip((0, 7, 20, 60), ("0.367", "0.382", "0.393", "0.389")):
    show(f"problem 11 (b): R2 at lag {lg}", curve["R2"][lg], ".3f", p)
ratio = {k: SEH[k] / SE9[k] for k in RULES}
show("HAC over (20.9), lowest (R4)", min(ratio.values()), ".2f", "0.92")
show("HAC over (20.9), highest (R2)", max(ratio.values()), ".2f", "1.04")
print("rho_1 of the daily excess returns:", {k: round(rho1(X[:, j]), 3) for j, k in enumerate(RULES)})
x1 = X[:, 0]
show("rho_1 of R1's squared deviations", rho1((x1 - x1.mean()) ** 2), ".3f", "0.246")
vr = {k: se_vol_hac(X[:, j], L) / (mom[k][1] * math.sqrt((mom[k][3] - 1) / (4 * T))) for j, k in enumerate(RULES)}
show("volatility: HAC over iid, lowest", min(vr.values()), ".2f", "1.51")
show("volatility: HAC over iid, highest", max(vr.values()), ".2f", "1.60")
show("R1's volatility SE, iid (%)", 100 * mom["R1"][1] * math.sqrt((mom["R1"][3] - 1) / (4 * T)) * sqA, ".3f", "0.576")
for lg, p in zip((7, 20, 60), ("0.872", "1.026", "1.156")):
    show(f"R1's volatility SE, lag {lg} (%)", 100 * se_vol_hac(x1, lg) * sqA, ".3f", p)
show("R1's mean: HAC over iid", se_mean_hac(x1, L) / (mom["R1"][1] / math.sqrt(T)), ".2f", "0.94")

fig, ax = plt.subplots()
for k in ("R1", "R2", "R4"):
    ax.plot(list(lags), curve[k], label=k)
ax.axhline(0.363, ls="--", color="grey")
ax.axvline(7, ls="--", color="grey")
ax.set_xlabel("HAC lag")
ax.set_ylabel("standard error a year")
ax.set_title("[[ex:haclag]]")
ax.legend()
plt.show()

mt, st, skt, kut = moments(Rt)
srt = mt / st
show("TR23 daily ratio", srt, ".5f", "0.05173")
show("TR23 a year", srt * math.sqrt(At), ".2f", "0.81")
show("TR23 skewness", skt, ".2f", "-0.34")
show("TR23 raw kurtosis", kut, ".2f", "8.27")
show("TR23 (20.9) a year", math.sqrt(v209(srt, skt, kut) / Tt) * math.sqrt(At), ".3f", "0.207")
show("TR23 (33.1), lag 9", se_sr_hac(Rt, lag_rule(Tt)) * math.sqrt(At), ".3f", "0.213")
show("TR23 (33.1), lag 145", se_sr_hac(Rt, 145) * math.sqrt(At), ".3f", "0.243")
""")

md(r"""
## Part 4 — Lo's correction on 90 calendar months

[[eg:monthly]] and problem 10: monthly log excess returns, (19.9) with $\hat\rho_1,\dots,\hat\rho_{11}$, and the robust standard error of the ratio by (25.6) with (25.4).
""")

code(r"""
lo_rows = {}
for j, k in enumerate(RULES):
    w = WM[full, j]
    xm = np.log(w[1:] / w[:-1]) - nsess * np.log(1 + RF / Aw)
    c = xm - xm.mean()
    rho = [float(c[i:] @ c[:-i] / (c @ c)) for i in range(1, 12)]
    ratio12 = 1 + 2 * sum((1 - i / 12) * rho[i - 1] for i in range(1, 12))
    se_rob = math.sqrt(sum((2 * (1 - i / 12)) ** 2 * float(np.sum(c[i:] ** 2 * c[:-i] ** 2)) / float(c @ c) ** 2
                           for i in range(1, 12)))
    srm = float(xm.mean() / xm.std(ddof=0))
    lo_rows[k] = (srm, srm * math.sqrt(12), srm * math.sqrt(12 / ratio12), ratio12, se_rob, math.sqrt(12 / ratio12))
print(pl.DataFrame({"rule": RULES, "monthly SR": [round(lo_rows[k][0], 3) for k in RULES],
                    "x sqrt(12)": [round(lo_rows[k][1], 2) for k in RULES],
                    "(19.9)": [round(lo_rows[k][2], 2) for k in RULES],
                    "ratio": [round(lo_rows[k][3], 3) for k in RULES],
                    "robust SE": [round(lo_rows[k][4], 2) for k in RULES]}))
srm, a12, alo, rat, srob, _ = lo_rows["R1"]
show("problem 10: R1's monthly ratio", srm, ".3f", "0.305")
show("by sqrt(12)", a12, ".2f", "1.06")
show("by (19.9)", alo, ".2f", "0.92")
show("the ratio", rat, ".2f", "1.31")
show("its robust SE", srob, ".2f", "0.38")
se_iid = math.sqrt(2 * 23 * 11 / (3 * 12 * 90))
show("(25.6)'s iid SE", se_iid, ".3f", "0.395")
show("the excess over 1 in iid SEs", (rat - 1) / se_iid, ".2f", "0.78")
sf = [lo_rows[k][5] for k in RULES]
show("scale factors, lowest", min(sf), ".2f", "2.74")
show("scale factors, highest", max(sf), ".2f", "3.33")
ar = 12 / math.sqrt(12 + 2 * sum((12 - i) * 0.2**i for i in range(1, 12)))
show("AR(1) with rho_1 = 0.2: the scale factor", ar, ".3f", "2.879")
show("sqrt(12) over it", math.sqrt(12) / ar, ".3f", "1.203")
dl = {k: (np.log(1 + R[:, j]) - np.log(1 + RF / Aw)) for j, k in enumerate(RULES)}
dlr = {k: dl[k].mean() / dl[k].std(ddof=0) * sqA for k in RULES}
show("daily log ratios, lowest (R4)", min(dlr.values()), ".2f", "0.54")
show("daily log ratios, highest (R2)", max(dlr.values()), ".2f", "1.08")
""")

md(r"""
## Part 5 — PSR and the minimum track record

[[ex:psrT]] and [[eg:mintrl]], with Bailey and López de Prado's (2012) example from their appendix code's inputs.
""")

code(r"""
mt_rows = (("R2", "523", "2.15", "2.10"), ("R1", "720", "2.96", "2.85"),
           ("R4", "1,717", "7.05", "6.85"))
for k, n0, y0, yn in mt_rows:
    _, _, sk, ku = mom[k]
    n_ = mintrl(SR[k], 0, sk, ku)
    show(f"{k}: MinTRL against zero (sessions)", n_, ",.0f", n0)
    show(f"{k}: in years of sessions", n_ / Aw, ".2f", y0)
    show(f"{k}: with normal moments", mintrl(SR[k], 0, 0, 3) / Aw, ".2f", yn)
z1 = SR["R2"] * math.sqrt(T - 1) / math.sqrt(v209(SR["R2"], sk2, ku2))
show("R2's z with sqrt(T - 1)", z1, ".3f", "3.097")
show("with sqrt(T)", z1 * math.sqrt(T / (T - 1)), ".3f", "3.098")
show("TR23's PSR(0)", psr(srt, 0, Tt, skt, kut), ".5f", "0.99995")
n_tr = mintrl(srt, 0, skt, kut)
show("TR23's MinTRL (sessions)", n_tr, ",.0f", "1,035")
show("in years of sessions", n_tr / At, ".2f", "4.20")
show("TR23 with normal moments, years of sessions", mintrl(srt, 0, 0, 3) / At, ".2f", "4.12")
show("(21.4) one-sided at power 1/2", (Z95 / (srt * math.sqrt(At))) ** 2, ".2f", "4.11")
n12 = mintrl(2 / math.sqrt(12), 1 / math.sqrt(12), -0.72, 5.78)
n12n = mintrl(2 / math.sqrt(12), 1 / math.sqrt(12), 0, 3)
show("Bailey and Lopez de Prado (2012): months", n12, ".1f", "59.9")
show("normal months", n12n, ".1f", "38.9")
show("years", n12 / 12, ".2f", "4.99")
show("normal years", n12n / 12, ".2f", "3.24")

tg = np.geomspace(0.5, 15, 200)
fig, ax = plt.subplots()
for a in (0.5, 1.0, 1.5):
    ax.plot(tg, [psr(a / sqA, 0, t * Aw, 0, 3) for t in tg], label=f"annual SR {a}")
    print(f"annual SR {a}: MinTRL {mintrl(a / sqA, 0, 0, 3) / Aw:.2f} years of sessions; "
          f"PSR(0) at 7.60 years of sessions {psr(a / sqA, 0, T, 0, 3):.3f}")
ax.axhline(0.95, ls="--", color="grey")
ax.axvline(tau, ls="--", color="grey")
ax.set_xscale("log")
ax.set_xlabel("record, years of sessions")
ax.set_ylabel("PSR(0)")
ax.set_title("[[ex:psrT]] (model: normal returns)")
ax.legend()
plt.show()
""")

md(r"""
## Part 6 — Ledoit and Wolf's test by hand

(33.6) with (23.7) at lag 7, and their studentized circular block bootstrap with the book's settings: $b=22$ (the largest stationary estimate of `optimal_block_length` over the eight rules' squared demeaned returns), 85 block starts per resample cut to 1,851 rows, moments centred at the resample's own means, the block covariance from the 84 complete blocks. Experiment 1 shares one set of block starts among the seven pairs, so problem 12's pair R4 − R1 is one column of it.
""")

code(r"""
obl = [optimal_block_length((X[:, j] - X[:, j].mean()) ** 2) for j in range(8)]
stat_est = [float(o["stationary"].iloc[0]) for o in obl]
circ_est = [float(o["circular"].iloc[0]) for o in obl]
b = round(max(stat_est))
print(f"stationary estimates {min(stat_est):.2f} to {max(stat_est):.2f}, circular {min(circ_est):.2f} to "
      f"{max(circ_est):.2f}: b = {b}; T = {T} = {T // b} x {b} + {T % b}")


def lw_parts(xj, x1, lag):
    # (Delta hat, SE) per observation: (33.6) with (23.7)'s long-run covariance
    a, b_, c, d = xj.mean(), x1.mean(), (xj**2).mean(), (x1**2).mean()
    V = np.column_stack([xj - a, x1 - b_, xj**2 - c, x1**2 - d])
    grad = np.array([c / (c - a**2) ** 1.5, -d / (d - b_**2) ** 1.5, -0.5 * a / (c - a**2) ** 1.5,
                     0.5 * b_ / (d - b_**2) ** 1.5])
    return float(a / math.sqrt(c - a**2) - b_ / math.sqrt(d - b_**2)), float(np.sqrt(grad @ lrv(V, lag) @ grad / len(xj)))


def lw_boot(XA, pairs, blk, n_boot, rng):
    # centred studentized statistics |Delta_boot - Delta| / SE(Delta_boot), circular blocks
    n = XA.shape[0]
    nb, lb = -(-n // blk), n // blk
    base = [lw_parts(XA[:, j], XA[:, o], 0)[0] for j, o in pairs]
    out = np.empty((n_boot, len(pairs)))
    for i in range(n_boot):
        idx = ((rng.integers(0, n, size=nb)[:, None] + np.arange(blk)) % n).ravel()[:n]
        Xs = XA[idx]
        mu, ga = Xs.mean(axis=0), (Xs**2).mean(axis=0)
        V = np.concatenate([Xs - mu, Xs**2 - ga], axis=1)[: lb * blk]
        Z = V.reshape(lb, blk, -1).sum(axis=1) / math.sqrt(blk)
        Pb = Z.T @ Z / lb
        for jj, (j, o) in enumerate(pairs):
            a, b_, c, d = mu[j], mu[o], ga[j], ga[o]
            grad = np.array([c / (c - a**2) ** 1.5, -d / (d - b_**2) ** 1.5, -0.5 * a / (c - a**2) ** 1.5,
                             0.5 * b_ / (d - b_**2) ** 1.5])
            ix = [j, o, XA.shape[1] + j, XA.shape[1] + o]
            se = math.sqrt(float(grad @ Pb[np.ix_(ix, ix)] @ grad) / n)
            out[i, jj] = abs(a / math.sqrt(c - a**2) - b_ / math.sqrt(d - b_**2) - base[jj]) / se
    return out


B = 9999
pairs = [(j, 0) for j in range(1, 8)]
rng1 = np.random.default_rng([1, SEED])                  # experiment 1, created once
dstar = lw_boot(X, pairs, b, B, rng1)
res = {}
for jj, (j, _) in enumerate(pairs):
    k = RULES[j]
    dlt, sd = lw_parts(X[:, j], X[:, 0], L)
    t = dlt / sd
    pb = (int(np.sum(dstar[:, jj] >= abs(t) - 1e-12)) + 1) / (B + 1)
    q = float(np.quantile(dstar[:, jj], 0.95, method="inverted_cdf"))
    qse = float(np.quantile(dstar[:, jj].reshape(99, 101), 0.95, axis=1, method="inverted_cdf").std(ddof=1) / math.sqrt(99))
    res[k] = {"d": dlt * sqA, "se": sd * sqA, "t": t, "p_hac": two_sided(t), "p_boot": pb, "q": q, "q_se": qse}
hh, hb = holm([res[k]["p_hac"] for k in RULES[1:]]), holm([res[k]["p_boot"] for k in RULES[1:]])
X1B = {"R2": "+0.162 0.253 0.52 0.52", "R3": "-0.201 0.243 0.41 0.41", "R4": "-0.347 0.285 0.22 0.25",
       "R5": "-0.134 0.229 0.56 0.56", "R6": "-0.022 0.137 0.87 0.88", "R7": "-0.058 0.207 0.78 0.78",
       "R8": "-0.041 0.163 0.80 0.81"}
for k, a1, a2 in zip(RULES[1:], hh, hb):
    r = res[k]
    got = f"{r['d']:+.3f} {r['se']:.3f} {r['p_hac']:.2f} {r['p_boot']:.2f}"
    print(f"[[ex:case]] (b), {k} - R1: {got}; Holm {a1:.2f}, {a2:.2f}   [book: {X1B[k]}, 1.00]")
    assert got == X1B[k] and f"{a1:.2f}" == f"{a2:.2f}" == "1.00"
r = res["R2"]
show("[[eg:lw]]: t-stat", r["t"], "+.2f", "+0.64")
show("HAC interval, low", r["d"] - Z975 * r["se"], "+.2f", "-0.33")
show("HAC interval, high", r["d"] + Z975 * r["se"], "+.2f", "+0.66")
show("bootstrap p-value's Monte Carlo SE", math.sqrt(r["p_boot"] * (1 - r["p_boot"]) / B), ".3f", "0.005")
show("the bootstrap quantile", r["q"], ".1f", "2.0")
show("its Monte Carlo SE (batch means)", r["q_se"], ".2f", "0.02")
show("bootstrap interval, low", r["d"] - r["q"] * r["se"], "+.2f", "-0.34")
show("bootstrap interval, high", r["d"] + r["q"] * r["se"], "+.2f", "+0.67")
r = res["R4"]
show("problem 12: bootstrap p-value", r["p_boot"], ".2f", "0.25")
show("its Monte Carlo SE", math.sqrt(r["p_boot"] * (1 - r["p_boot"]) / B), ".3f", "0.004")
show("the bootstrap quantile", r["q"], ".1f", "2.1")
show("bootstrap interval, low", r["d"] - r["q"] * r["se"], "+.2f", "-0.95")
show("bootstrap interval, high", r["d"] + r["q"] * r["se"], "+.2f", "+0.25")
show("HAC interval, low", r["d"] - Z975 * r["se"], "+.2f", "-0.91")
show("HAC interval, high", r["d"] + Z975 * r["se"], "+.2f", "+0.21")
""")

code(r"""
x1, x2 = X[:, 0], X[:, 1]
naive = math.sqrt(SE9["R2"] ** 2 + SE9["R1"] ** 2)
show("independent-samples SE a year", naive * sqA, ".3f", "0.521")
show("correlation R2-R1", float(np.corrcoef(x2, x1)[0, 1]), ".2f", "0.70")
for lg, p in zip((0, 7, 22, 60), ("0.280", "0.253", "0.250", "0.243")):
    show(f"SE of R2 - R1 at lag {lg}", lw_parts(x2, x1, lg)[1] * sqA, ".3f", p)
rng3 = np.random.default_rng([3, SEED])                  # experiment 3, created once
t21 = abs(lw_parts(x2, x1, L)[0] / lw_parts(x2, x1, L)[1])
p_b = {}
for blk in (1, 5, 10, 26, 50, 100):
    ds = lw_boot(X[:, [1, 0]], [(0, 1)], blk, B, rng3)[:, 0]
    p_b[blk] = (int(np.sum(ds >= t21 - 1e-12)) + 1) / (B + 1)
print("experiment 3, bootstrap p-values by block size:", {k: round(v, 2) for k, v in p_b.items()})
show("lowest", min(p_b.values()), ".2f", "0.53")
show("highest", max(p_b.values()), ".2f", "0.56")
show("largest Monte Carlo SE", max(math.sqrt(p * (1 - p) / B) for p in p_b.values()), ".3f", "0.005")
c = res["R2"]["se"] * math.sqrt(tau)
z80 = float(stats.norm.ppf(0.975) + stats.norm.ppf(0.8))
show("years of sessions for 80% power", (z80 * c / res["R2"]["d"]) ** 2, ".0f", "146")
show("one-sided at power 1/2", (Z95 * c / res["R2"]["d"]) ** 2, ".0f", "50")

fig, ax = plt.subplots(figsize=(8, 4))
y = np.arange(7, 0, -1)
for yy, k in zip(y, RULES[1:]):
    r = res[k]
    ax.plot([r["d"] - Z975 * r["se"], r["d"] + Z975 * r["se"]], [yy, yy], lw=3, color="C0")
    ax.plot([r["d"] - r["q"] * r["se"], r["d"] + r["q"] * r["se"]], [yy + 0.2, yy + 0.2], lw=1.2, color="grey")
    ax.plot(r["d"], yy, "o", color="C0")
ax.axvline(0, ls="--", color="grey")
ax.set_yticks(y, [f"{k} - R1" for k in RULES[1:]])
ax.set_xlabel("difference from R1, Sharpe ratio a year")
ax.set_title("[[ex:pairs]]: HAC (thick) and bootstrap (thin) 95% intervals")
plt.show()
""")

md(r"""
## Part 7 — The best of eight: (33.4), experiment 2 and DSR

[[ex:deflate]], [[eg:dsr]], Bailey and López de Prado's (2014) example and problem 8 (b).
""")

code(r"""
for n in (2, 5, 8, 100):
    print(f"n = {n}: exact {emax(n):.4f}, approximation {emax_bldp(n):.4f}, (21.9)'s median "
          f"{stats.norm.ppf(0.5 ** (1 / n)):.4f}")
ez8 = emax(8)
show("E Z_(8)", ez8, ".4f", "1.4236")
show("problem 4: E Z_(5)", emax(5), ".3f", "1.163")
s0 = 1 / math.sqrt(T - 1)
show("the deflated benchmark at n = 8, a year", ez8 * s0 * sqA, ".3f", "0.517")
show("DSR at n = 8", psr(SR["R2"], ez8 * s0, T, sk2, ku2), ".3f", "0.955")
show("with the approximation", psr(SR["R2"], emax_bldp(8) * s0, T, sk2, ku2), ".3f", "0.951")
show("with R2's HAC SE", float(stats.norm.cdf((SR["R2"] - ez8 * s0) / SEH["R2"])), ".3f", "0.948")
nstar = optimize.brentq(lambda n: psr(SR["R2"], emax(n) * s0, T, sk2, ku2) - 0.95, 2, 100, xtol=1e-10)
show("DSR = 0.95 at n", nstar, ".1f", "8.8")

C = np.corrcoef(X, rowvar=False)
off = C[~np.eye(8, dtype=bool)]
show("mean correlation", float(off.mean()), ".3f", "0.821")
rng2 = np.random.default_rng([2, SEED])                  # experiment 2, created once
mx = (rng2.standard_normal((1_000_000, 8)) @ np.linalg.cholesky(C).T).max(axis=1)
emc, emc_se = float(mx.mean()), float(mx.std() / 1000)
show("E max of N_8(0, C)", emc, ".3f", "0.588")
show("its Monte Carlo SE", emc_se, ".4f", "0.0009")
neff = optimize.brentq(lambda n: emax(n) - emc, 1.000001, 8, xtol=1e-12)
show("n_eff", neff, ".2f", "2.07")
show("DSR at n_eff", psr(SR["R2"], emc * s0, T, sk2, ku2), ".3f", "0.994")
show("eq. (9) of Bailey and Lopez de Prado", float(off.mean()) + (1 - float(off.mean())) * 8, ".2f", "2.25")
cs = float(np.array([SR[k] for k in RULES]).std())
show("SD of the eight estimates, a year", cs * sqA, ".3f", "0.141")
show("expected under equal true ratios", math.sqrt((1 - C.sum() / 64) / T) * sqA, ".3f", "0.144")


def mintrl_n(ez):
    # (33.5) for R2 at 95%
    return 1 + ((Z95 * math.sqrt(v209(SR["R2"], sk2, ku2)) + ez) / SR["R2"]) ** 2


show("MinTRL at n = 8 (sessions)", mintrl_n(ez8), ",.0f", "1,796")
show("in years of sessions", mintrl_n(ez8) / Aw, ".2f", "7.37")
show("at n_eff", mintrl_n(emc) / Aw, ".1f", "3.9")
show("at n = 100", mintrl_n(emax(100)) / Aw, ".1f", "13.5")
sr14, v14 = 2.5 / math.sqrt(250), 0.5 / 250
show("2014 example: threshold a day", math.sqrt(v14) * emax_bldp(100), ".4f", "0.1132")
show("DSR at 100", psr(sr14, math.sqrt(v14) * emax_bldp(100), 1250, -3, 10), ".4f", "0.9004")
show("at 46", psr(sr14, math.sqrt(v14) * emax_bldp(46), 1250, -3, 10), ".4f", "0.9505")
show("normal returns at 88", psr(sr14, math.sqrt(v14) * emax_bldp(88), 1250, 0, 3), ".4f", "0.9505")
n05 = optimize.brentq(lambda n: emax(n) - math.sqrt(0.5 / math.pi), 1.000001, 2, xtol=1e-12)
show("problem 8 (b): the n with E Z_(n) = sqrt(0.5 / pi)", n05, ".3f", "1.608")

ng = np.geomspace(1, 10000, 60)
fig, ax = plt.subplots()
ax.plot(ng, [emax(n) * s0 * sqA for n in ng], label="exact, (33.4)")
ax.plot(ng[1:], [emax_bldp(n) * s0 * sqA for n in ng[1:]], ls="--", label="approximation")
ax.axhline((SR["R2"] - Z95 * math.sqrt(v209(SR["R2"], sk2, ku2) / (T - 1))) * sqA, ls="--", color="grey")
ax.axvline(8, ls="--", color="grey")
ax.axvline(neff, ls=":", color="grey")
ax.set_xscale("log")
ax.set_xlabel("number of trials n")
ax.set_ylabel("deflated benchmark, a year")
ax.set_title("[[ex:deflate]] (model)")
ax.legend()
plt.show()
""")

md(r"""
## Part 8 — Haircuts

[[ex:haircut]] and [[eg:hsr]]: (33.7) with $n=8$ on the two-sided normal p-value of $\widehat{\mathrm{SR}}\sqrt T$, and Harvey and Liu's example with the normal and the $t_{239}$ reference.
""")

code(r"""
pS = {k: two_sided(SR[k] * math.sqrt(T)) for k in RULES}
hol = dict(zip(RULES, holm([pS[k] for k in RULES])))


def hsr(p_adj):
    return 0.0 if p_adj >= 1 else float(stats.norm.isf(p_adj / 2) / math.sqrt(T) * sqA)


hc = pl.DataFrame({"rule": RULES, "SR": [round(SR[k] * sqA, 2) for k in RULES],
                   "HSR independent": [round(hsr(1 - (1 - pS[k]) ** 8), 2) for k in RULES],
                   "HSR Bonferroni": [round(hsr(min(1, 8 * pS[k])), 2) for k in RULES],
                   "HSR Holm": [round(hsr(hol[k]), 2) for k in RULES]})
print(hc)
show("[[eg:hsr]]: R2's t-stat", SR["R2"] * math.sqrt(T), ".3f", "3.137")
show("its p-value", pS["R2"], ".5f", "0.00171")
show("adjusted, independent tests", 1 - (1 - pS["R2"]) ** 8, ".4f", "0.0136")
show("adjusted, Bonferroni", 8 * pS["R2"], ".4f", "0.0137")
show("t-stat adjusted", float(stats.norm.isf((1 - (1 - pS["R2"]) ** 8) / 2)), ".2f", "2.47")
show("HSR", hsr(1 - (1 - pS["R2"]) ** 8), ".2f", "0.90")
show("haircut (%)", 100 * (1 - hsr(1 - (1 - pS["R2"]) ** 8) / (SR["R2"] * sqA)), ".0f", "21")
show("Bonferroni's HSR", hsr(8 * pS["R2"]), ".2f", "0.89")
show("Bonferroni's haircut (%)", 100 * (1 - hsr(8 * pS["R2"]) / (SR["R2"] * sqA)), ".0f", "21")
show("Holm's HSR of R2", hsr(hol["R2"]), ".2f", "0.89")
show("Holm's HSR of R6", hsr(hol["R6"]), ".2f", "0.71")
show("Bonferroni's haircut of R4 (%)", 100 * (1 - hsr(min(1, 8 * pS["R4"])) / (SR["R4"] * sqA)), ".0f", "75")
t240 = 0.75 / math.sqrt(12) * math.sqrt(240)
pn = two_sided(t240)
show("Harvey and Liu: single p-value, normal", pn, ".4f", "0.0008")
show("adjusted for 200 tests", 1 - (1 - pn) ** 200, ".2f", "0.15")
show("HSR, normal", float(stats.norm.isf((1 - (1 - pn) ** 200) / 2)) / math.sqrt(240) * math.sqrt(12), ".2f", "0.32")
pt = float(2 * stats.t.sf(t240, 239))
show("HSR with t_239", float(stats.t.isf((1 - (1 - pt) ** 200) / 2, 239)) / math.sqrt(240) * math.sqrt(12), ".2f", "0.31")

fig, ax = plt.subplots()
xx = np.arange(8)
ax.bar(xx - 0.27, hc["SR"], 0.27, label="Sharpe ratio")
ax.bar(xx, hc["HSR independent"], 0.27, label="HSR, independent tests")
ax.bar(xx + 0.27, hc["HSR Holm"], 0.27, label="HSR, Holm")
ax.set_xticks(xx, RULES)
ax.set_ylabel("Sharpe ratio a year")
ax.set_title("[[ex:haircut]]")
ax.legend()
plt.show()
""")

md(r"""
## Part 9 — Extension: R2's PSR(0) on rolling windows

A **stability check**, not a result: compute R2's PSR(0) by (33.2) on every window of 730 consecutive sessions (about three years of sessions), and plot it against the window's last date. How often does it fall below 0.95, and when?

Picking a window after seeing this curve would be one more trial on the same data, the kind of search that LM34 corrects.
""")

code(r"""
win = 730
ends_w = list(range(win, T + 1))
roll = []
for e in ends_w:
    _, s_, sk_, ku_ = moments(x2[e - win:e])
    roll.append(psr(x2[e - win:e].mean() / s_, 0, win, sk_, ku_))
roll = np.array(roll)
print(f"{len(roll)} windows of {win} sessions; PSR(0) from {roll.min():.3f} to {roll.max():.3f}; "
      f"below 0.95 in {int((roll < 0.95 - 1e-12).sum())} windows")
fig, ax = plt.subplots()
ax.plot([date.fromisoformat(dates[e]) for e in ends_w], roll)
ax.axhline(0.95, ls="--", color="grey")
ax.set_ylabel("PSR(0), 730 sessions")
ax.set_title("R2's PSR(0) on rolling windows (a stability check)")
plt.show()
""")

nb = nbf.v4.new_notebook()
nb["cells"] = cells
nb["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                  "language_info": {"name": "python"}}
nbf.write(nb, LAB / "LM33_lab.ipynb")

(LAB / "README.md").write_text("""# LM33 Lab — The Statistics of the Sharpe Ratio

Companion to *From Calculus to Kelly*, Learning Module 33. The notebook rebuilds the module's exhibits and computational examples:

- the eight rules' Sharpe ratios with (20.9)'s standard errors, the checkpoint table and the illustrative risk-free rate;
- the HAC standard error (33.1) by hand, its lag curve and TR23's long record;
- Lo's correction on 90 calendar months, with the noise of the correction;
- the probabilistic Sharpe ratio and the minimum track record, with Bailey and López de Prado's 2012 example;
- Ledoit and Wolf's test of each rule against R1, by HAC and by their circular block bootstrap (experiments 1 and 3);
- the expected maximum of $n$ trials, the effective number of trials (experiment 2) and the deflated Sharpe ratio;
- Harvey and Liu's haircuts.

It also works the computational practice problems and ends with R2's PSR(0) on rolling windows, a stability check.

## Run

From the repository root, install the locked Python environment (`uv.lock`) and open the notebook:

```bash
uv sync
uv run --with jupyterlab jupyter lab labs/LM33_lab/LM33_lab.ipynb
```

The notebook is saved with its outputs, so you can read it before running it. To re-execute it, from inside this folder:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace LM33_lab.ipynb
```

`build/make_lab33.py` generates the notebook and this README: edit the generator, not the generated files.

## Data (FinMind; not in the repository)

The notebook reads FinMind files that you download once with your own token. From the repository root, run `uv run python data/fetch_finmind.py`, then `uv run python data/make_lab_data.py`. FinMind's licence does not allow the book to redistribute the data. After that, the notebook runs offline.

On FinMind's free plan, run `uv run python data/fetch_finmind.py --exclude sectors_close/ --exclude vol4_settlement/ --exclude vol6/etf_snapshot` instead, as the book's Getting Started page says. This lab needs none of the excluded files.

The same steps in a shell (`data/raw/` and this folder's `data/` are git-ignored):

```bash
export FINMIND_TOKEN=...               # your FinMind API token
uv run python data/fetch_finmind.py    # rebuilds and verifies data/raw/
uv run python data/make_lab_data.py    # writes every lab's data/ folder
```

`fetch_finmind.py` checks every file against `data/raw_manifest.json`. The notebook reads only the files in its own `data/` folder:

| File | Content |
|:--|:--|
| `data/rule_wealth_net.csv` | the through case's eight rules (`data/vol5_rules.py`): `rule`, `date`, `wealth`, the net wealth after each day's trade on every session of E5's wealth frame from the first trade, 4 March 2019, to 8 October 2026 (FinMind `TaiwanStockPrice`, `TaiwanStockDividendResult`, `TaiwanStockSplitPrice`) |
| `data/taiex_tr.csv` | TR23, the TAIEX total-return index (`date`, `price`; FinMind `TaiwanStockTotalReturnIndex`, data_id TAIEX), 2 January 2003 to 8 October 2026 |
""", encoding="utf-8", newline="\n")
print("wrote", LAB / "LM33_lab.ipynb", "and README.md | labels:",
      {f"{k}:{a}": n for (k, a), n in sorted(NUM.items(), key=lambda kv: (kv[0][0], kv[1]))})
