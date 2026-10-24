"""Batch 4's through case: eight allocation rules on E5, the cost model and the wealth recursion (plans/vol-5.md).

Every module of Volumes V and VI imports its rule numbers from here; none re-implements a rule. The settings were
fixed on 2026-10-24 before any result was computed (plans/vol-5.md, "Through case"):
  - signals at each month's last TR23 session, from the trailing WINDOW rows of E5's estimation frame (vol5_series);
    the first month-end with WINDOW rows is the first signal; the trade is at the close of the next session on which
    every fund trades (the wealth frame); no terminal liquidation;
  - R1 equal weights; R2 the constructed reference mix; R3 long-only minimum variance; R4 long-only maximum Sharpe
    ratio on the window's means in excess of RF (homogenized QP; R3 when no mean exceeds RF/A); R5 R3 with the
    Ledoit-Wolf covariance (scikit-learn, scaled-identity target); R6 equal risk contributions (Newton's method on
    1/2 y'Sy - (1/N) sum ln y); R7 hierarchical risk parity (Lopez de Prado 2016); R8 R6 scaled by
    L = min(CAP, sigma_bar / sigma_ewma), both from R6's new weights applied to the window, cash at RF and borrowing
    at RF + SPREAD;
  - costs: COMMISSION on buys and sells, TAX on sales (0 for the bond ETF), deducted from wealth at the trade: the
    post-trade wealth solves W' = W - cost(W' f - h), so the book is self-financing; interest and returns accrue per
    session of the wealth frame.
Long-only R3, R4 and R5 (min y'Sy subject to a'y = 1, y >= 0) are solved exactly as a non-negative least-squares problem
(min 1/2 z'Sz - a'z, z >= 0, through the Cholesky factor; y = z / a'z), with the KKT conditions checked, then
cross-checked against cvxpy: OSQP (polished) must equal it to OSQP_TOL per weight, CLARABEL's objective to CLARABEL_GAP
relative. R6 is checked against cvxpy's log form, R7's quasi-diagonal order against scipy's leaves_list. Solvers get
annualized inputs. The script stops if any check fails.

The comparison criteria (fixed in advance; summary()): growth = ln(final wealth) / years, from the cash of 1 at the
first trade's close (years = calendar days / 365.25), so the first purchase's cost counts; the Sharpe ratio and the
volatility of the daily returns from the session after the first trade, in excess of RF / A_w, times sqrt(A_w); the
maximum drawdown of the path with the starting 1; turnover = the sum of one-way turnovers 1/2 |f - h/W| (pre-trade W)
after the first purchase, per year; costs = the sum over trades of cost / pre-trade wealth (about ln(gross / net)).

Outputs (git-ignored): data/processed/vol5_rules.parquet (rule, date, wealth, wealth_gross: net and gross wealth after
each day's trade, from the first trade), data/processed/vol5_trades.parquet (rule, signal, trade, the five target
exposures, exposure, turnover, cost: cost / pre-trade wealth) and data/processed/vol5_rules.txt (this report).
Run:  PYTHONUTF8=1 uv run python data/vol5_rules.py     (after data/vol5_series.py)
"""
import sys
from dataclasses import dataclass
from datetime import date
from importlib.metadata import version
from pathlib import Path
from typing import NoReturn

import cvxpy as cp
import numpy as np
import polars as pl
from numpy.typing import NDArray
from scipy.cluster.hierarchy import leaves_list, linkage
from scipy.linalg import cholesky, solve_triangular
from scipy.optimize import nnls
from scipy.spatial.distance import squareform
from sklearn.covariance import LedoitWolf
from vol5_series import Frames, frames

HERE = Path(__file__).resolve().parent
PROC = HERE / "processed"

WINDOW = 504
RF = 0.015
SPREAD = 0.02
CAP = 1.5
LAM = 0.94
COMMISSION = 0.001425
TAX = {"0050": 0.001, "00646": 0.001, "00679B": 0.0, "00635U": 0.001, "00642U": 0.001}
R2 = {"0050": 0.40, "00646": 0.20, "00679B": 0.30, "00635U": 0.10, "00642U": 0.0}
RULES = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]
OSQP_OPTS = {"eps_abs": 1e-10, "eps_rel": 1e-10, "max_iter": 400000, "polishing": True}
CLARABEL_OPTS = {"tol_gap_abs": 1e-12, "tol_gap_rel": 1e-12, "tol_feas": 1e-12}
OSQP_TOL = 1e-9           # polished OSQP against the exact solution, per weight
CLARABEL_GAP = 1e-9       # CLARABEL's objective against the exact one, relative (an interior point leaves near-zero
                          # weights off at the 1e-6 level, so its weights are not compared; at 1e-10 tolerances its
                          # objective gap reached 1.2e-8 on U28, at 1e-12 below 1.5e-10)
ERC_OPTS = {"tol_gap_abs": 1e-10, "tol_gap_rel": 1e-10, "tol_feas": 1e-10}   # the exponential cone stops
                          # at "optimal_inaccurate" at 1e-12
ERC_CHECK_TOL = 1e-5      # Newton's ERC against cvxpy's exponential-cone form (its own accuracy is about 1e-6);
                          # Newton's solution itself is checked to 1e-10 by its equal risk shares

Vec = NDArray[np.float64]
Mat = NDArray[np.float64]


def fail(msg: str) -> NoReturn:
    sys.exit(f"vol5_rules: FAILED: {msg}")


def cov0(x: Mat) -> Mat:
    """Sample covariance, divisor T (AUTHORING section 6)."""
    xc = x - x.mean(axis=0)
    return xc.T @ xc / x.shape[0]


def qp_simplex(S: Mat, a: Vec, label: str) -> Vec | None:
    """min y'Sy subject to a'y = 1, y >= 0 (S positive definite), or None when no a_i > 0. Solved exactly as
    min 1/2 z'Sz - a'z, z >= 0: with S = R'R this is the non-negative least-squares problem |Rz - R^-T a|, and
    y = z / a'z. Checked: the KKT conditions of the original problem to 1e-10 relative to |lambda| max|a|."""
    if a.max() <= 0:
        return None
    R = cholesky(S, lower=False)
    z, _ = nnls(R, solve_triangular(R, a, trans="T"), maxiter=1000)
    den = float(a @ z)
    if den <= 0:
        fail(f"{label}: NNLS found no solution with a'z > 0")
    y = z / den
    lam = 2.0 / den                                       # multiplier of a'y = 1
    nu = 2 * S @ y - lam * a                              # multipliers of y >= 0
    scale = abs(lam) * float(np.abs(a).max())
    if nu.min() < -1e-10 * scale or float(np.abs(nu[y > 0]).max(initial=0.0)) > 1e-10 * scale:
        fail(f"{label}: KKT conditions fail (smallest multiplier {nu.min():.2e})")
    return y


def minvar(S: Mat, label: str) -> Vec:
    y = qp_simplex(S, np.ones(S.shape[0]), label)
    assert y is not None
    return y / y.sum()


def maxsharpe(S: Mat, e: Vec, label: str) -> Vec | None:
    """Long-only maximum Sharpe weights for excess means e, or None when no e_i > 0."""
    y = qp_simplex(S, e, label)
    return None if y is None else y / y.sum()


def erc(S: Mat) -> Vec:
    """Equal risk contributions: minimize 1/2 y'Sy - (1/N) sum ln y by Newton's method, w = y / sum y."""
    n = S.shape[0]
    y = 1 / np.sqrt(np.diag(S))
    y *= np.sqrt(1 / (n * (y @ S @ y)))

    def f(v: Vec) -> float:
        return 0.5 * float(v @ S @ v) - float(np.log(v).sum()) / n

    for _ in range(100):
        g = S @ y - 1 / (n * y)
        if np.abs(g * y).max() < 1e-13:              # y_i (Sy)_i = 1/N to 1e-13 (quadratic convergence)
            break
        H = S + np.diag(1 / (n * y**2))
        step = np.linalg.solve(H, -g)
        t = 1.0
        far = np.abs(g * y).max() > 1e-6               # near the optimum f's decrease drowns in rounding: full steps
        while (y + t * step).min() <= 0 or (far and f(y + t * step) > f(y) + 1e-4 * t * float(g @ step)):
            t /= 2
            if t < 1e-12:
                fail("ERC line search failed")
        y = y + t * step
    else:
        fail(f"ERC Newton iteration did not converge: largest |y_i (Sy)_i - 1/N| = {np.abs(g * y).max():.2e}")
    w = y / y.sum()
    rc = w * (S @ w) / float(w @ S @ w)
    if np.abs(rc - 1 / n).max() > 1e-10:
        fail(f"ERC risk shares not equal: {rc}")
    return w


def quasi_diag(Z: NDArray[np.float64], n: int) -> list[int]:
    """Lopez de Prado's getQuasiDiag: replace each cluster by its two members, from the root down."""
    order = [int(Z[-1, 0]), int(Z[-1, 1])]
    while max(order) >= n:
        out: list[int] = []
        for c in order:
            out += [int(Z[c - n, 0]), int(Z[c - n, 1])] if c >= n else [c]
        order = out
    return order


def hrp(x: Mat, S: Mat) -> Vec:
    """Hierarchical risk parity (Lopez de Prado 2016): distance sqrt((1 - rho)/2), Euclidean distance between its
    columns, single linkage, quasi-diagonal order, recursive bisection with inverse-variance weights in each cluster.
    Checked against the paper's SSRN version (abstract 2708678) and the author's HRP.py (2026-10-24 review)."""
    n = S.shape[0]
    C = np.corrcoef(x, rowvar=False)
    C = (C + C.T) / 2
    np.fill_diagonal(C, 1.0)
    D = np.sqrt(np.clip((1 - C) / 2, 0.0, None))
    np.fill_diagonal(D, 0.0)
    D2 = np.sqrt(((D[:, :, None] - D[:, None, :]) ** 2).sum(axis=0))
    D2 = (D2 + D2.T) / 2
    np.fill_diagonal(D2, 0.0)
    Z = linkage(squareform(D2, checks=False), method="single")
    order = quasi_diag(Z, n)
    if order != [int(i) for i in leaves_list(Z)]:
        fail(f"quasi-diagonal order {order} differs from scipy's leaves_list {list(leaves_list(Z))}")
    w = np.ones(n)
    clusters = [order]
    while clusters:
        clusters = [c[a:b] for c in clusters for a, b in ((0, len(c) // 2), (len(c) // 2, len(c))) if len(c) > 1]
        for left, right in zip(clusters[::2], clusters[1::2], strict=True):
            v = []
            for c in (left, right):
                sub = S[np.ix_(c, c)]
                ivp = 1 / np.diag(sub)
                ivp /= ivp.sum()
                v.append(float(ivp @ sub @ ivp))
            alpha = 1 - v[0] / (v[0] + v[1])
            w[left] *= alpha
            w[right] *= 1 - alpha
    return w


def cvx_check(S: Mat, a: Vec, exact: Vec, label: str) -> tuple[float, float]:
    """min y'Sy, a'y = 1, y >= 0 by OSQP (weights) and CLARABEL (objective) against the exact weights `exact`
    (normalized to sum 1). Returns (OSQP's largest weight gap, CLARABEL's relative objective gap)."""
    y_exact = exact / float(a @ exact)
    obj = float(y_exact @ S @ y_exact)
    out = []
    for solver, opts in ((cp.OSQP, OSQP_OPTS), (cp.CLARABEL, CLARABEL_OPTS)):
        y = cp.Variable(len(a))
        prob = cp.Problem(cp.Minimize(cp.quad_form(y, cp.psd_wrap(S))), [a @ y == 1, y >= 0])
        prob.solve(solver=solver, **opts)
        if prob.status != "optimal":
            fail(f"{label}: {solver} status {prob.status}")
        v = y.value
        assert v is not None
        yv = np.asarray(v, dtype=float)
        out.append(float(np.abs(yv / yv.sum() - exact).max()) if solver == cp.OSQP
                   else abs(float(yv @ S @ yv) - obj) / obj)
    if out[0] > OSQP_TOL or out[1] > CLARABEL_GAP:
        fail(f"{label}: OSQP weight gap {out[0]:.1e}, CLARABEL objective gap {out[1]:.1e}")
    return out[0], out[1]


def cvx_erc(S: Mat) -> Vec:
    n = S.shape[0]
    y = cp.Variable(n)
    prob = cp.Problem(cp.Minimize(0.5 * cp.quad_form(y, cp.psd_wrap(S)) - cp.sum(cp.log(y)) / n))
    prob.solve(solver=cp.CLARABEL, **ERC_OPTS)
    if prob.status != "optimal":
        fail(f"ERC cross-check: status {prob.status}")
    v = y.value
    assert v is not None
    w = np.asarray(v, dtype=float)
    return w / w.sum()


@dataclass
class Signal:
    signal: str
    trade: str
    targets: dict[str, Vec]     # rule -> exposures to the five funds (sum 1, except R8: sum L)


def schedule(fr: Frames) -> list[tuple[str, str, int]]:
    """(signal date, trade date, number of estimation rows through the signal) for every month-end with WINDOW rows."""
    wd, est = fr.wealth_dates, fr.est_dates
    out = []
    for i, d in enumerate(wd[:-1]):
        if d[:7] == wd[i + 1][:7]:
            continue                                   # not the month's last session
        rows = sum(1 for x in est if x <= d)
        if rows < WINDOW:
            continue
        j = next((k for k in range(i + 1, len(wd)) if fr.traded[k].all()), None)
        if j is None:
            continue
        out.append((d, wd[j], rows))
    return out


def signals(fr: Frames, log: list[str]) -> list[Signal]:
    A, n = fr.A, len(fr.funds)
    r2 = np.array([R2[s] for s in fr.funds])
    out = []
    gaps = {"R3 OSQP": 0.0, "R3 CLARABEL": 0.0, "R4 OSQP": 0.0, "R4 CLARABEL": 0.0, "R5 OSQP": 0.0,
            "R5 CLARABEL": 0.0, "R6": 0.0}
    fallback = 0
    for sig, trade, rows in schedule(fr):
        x = fr.X[rows - WINDOW:rows]
        S = A * cov0(x)                                   # annualized inputs (solver scaling)
        e = A * x.mean(axis=0) - RF
        t: dict[str, Vec] = {"R1": np.full(n, 1 / n), "R2": r2}
        t["R3"] = minvar(S, f"R3 {sig}")
        g = cvx_check(S, np.ones(n), t["R3"], f"R3 {sig}")
        gaps["R3 OSQP"], gaps["R3 CLARABEL"] = max(gaps["R3 OSQP"], g[0]), max(gaps["R3 CLARABEL"], g[1])
        w4 = maxsharpe(S, e, f"R4 {sig}")
        if w4 is None:
            fallback += 1
            t["R4"] = t["R3"]
        else:
            t["R4"] = w4
            g = cvx_check(S, e, w4, f"R4 {sig}")
            gaps["R4 OSQP"], gaps["R4 CLARABEL"] = max(gaps["R4 OSQP"], g[0]), max(gaps["R4 CLARABEL"], g[1])
        S5 = A * np.asarray(LedoitWolf(assume_centered=False).fit(x).covariance_, dtype=float)
        t["R5"] = minvar(S5, f"R5 {sig}")
        g = cvx_check(S5, np.ones(n), t["R5"], f"R5 {sig}")
        gaps["R5 OSQP"], gaps["R5 CLARABEL"] = max(gaps["R5 OSQP"], g[0]), max(gaps["R5 CLARABEL"], g[1])
        t["R6"] = erc(S)
        gaps["R6"] = max(gaps["R6"], float(np.abs(cvx_erc(S) - t["R6"]).max()))
        if gaps["R6"] > ERC_CHECK_TOL:
            fail(f"R6 {sig}: cvxpy differs from Newton by {gaps['R6']:.2e}")
        t["R7"] = hrp(x, S)
        p = x @ t["R6"]                                   # R6's new weights on the window
        sbar2 = float(np.mean(p**2))
        s2 = sbar2
        for r in p:
            s2 = LAM * s2 + (1 - LAM) * r * r
        L = min(CAP, float(np.sqrt(sbar2 / s2)))
        t["R8"] = L * t["R6"]
        for k in RULES[:7]:
            if abs(t[k].sum() - 1) > 1e-12 or t[k].min() < 0:
                fail(f"{k} {sig}: weights {t[k]} do not sum to 1 or are negative")
        out.append(Signal(sig, trade, t))
    log.append(f"signals: {len(out)} month-ends, first {out[0].signal} (trade {out[0].trade}), last {out[-1].signal} "
               f"(trade {out[-1].trade}); window {WINDOW} estimation rows; R4 fell back to R3 {fallback} times")
    log.append(f"solvers: cvxpy {version('cvxpy')}, OSQP {version('osqp')} {OSQP_OPTS}, CLARABEL "
               f"{version('clarabel')} {CLARABEL_OPTS}, scikit-learn {version('scikit-learn')}, SciPy {version('scipy')}")
    log.append("largest gap to the exact (NNLS) solution, OSQP per weight and CLARABEL's relative objective; R6 "
               "Newton against cvxpy per weight: " + ", ".join(f"{k} {v:.1e}" for k, v in gaps.items()))
    return out


@dataclass
class Trade:
    signal: str
    trade: str
    target: Vec       # exposures to the five funds
    exposure: float   # their sum (1, or R8's L)
    turnover: float   # one-way, 1/2 |target - pre-trade weights|
    cost: float       # cost / pre-trade wealth


@dataclass
class WealthPath:
    rule: str
    dates: list[str]  # wealth-frame dates from the first trade
    wealth: Vec       # wealth after each day's trade (the first purchase's cost included); 1 before it
    trades: list[Trade]
    ruin: str | None  # the first date with wealth <= 0, if any (no trade after it)


def wealth_path(fr: Frames, sigs: list[Signal], rule: str, cost_mult: float = 1.0,
                spread: float = SPREAD) -> WealthPath:
    wd = fr.wealth_dates
    by_trade = {s.trade: s for s in sigs}
    if len(by_trade) != len(sigs):
        fail("two signals trade on the same date")
    tax = np.array([TAX[s] for s in fr.funds]) * cost_mult
    comm = COMMISSION * cost_mult
    i0 = wd.index(sigs[0].trade)
    h = np.zeros(len(fr.funds))
    c = 1.0
    wealth: list[float] = []
    trades: list[Trade] = []
    ruin = None
    for i in range(i0, len(wd)):
        if i > i0:
            h = h * (1 + fr.W[i])
            c *= 1 + ((RF if c >= 0 else RF + spread) / fr.A_wealth)
        W = float(h.sum() + c)
        if W <= 0 and ruin is None:
            ruin = wd[i]
        s = by_trade.get(wd[i])
        if s is not None and ruin is None:
            f = s.targets[rule]
            drift = h / W
            Wn, cost = W, 0.0
            for _ in range(100):
                delta = Wn * f - h
                cost = comm * float(np.abs(delta).sum()) + float(tax @ np.clip(-delta, 0, None))
                new = W - cost
                if abs(new - Wn) < 1e-15 * W:
                    break
                Wn = new
            else:
                fail(f"{rule} {wd[i]}: the post-cost wealth did not converge")
            h = Wn * f
            c = Wn * (1 - float(f.sum()))
            trades.append(Trade(s.signal, s.trade, f, float(f.sum()), 0.5 * float(np.abs(f - drift).sum()), cost / W))
            W = Wn
        if abs(W - float(h.sum() + c)) > 1e-12 * max(1.0, abs(W)):
            fail(f"{rule} {wd[i]}: wealth identity broken")
        wealth.append(W)
    return WealthPath(rule, wd[i0:], np.array(wealth), trades, ruin)


def summary(fr: Frames, p: WealthPath) -> dict[str, float | str]:
    """The comparison criteria (module docstring); a path that reaches wealth <= 0 reports its ruin date instead."""
    if p.ruin:
        return {"ruin": p.ruin}
    years = (date.fromisoformat(p.dates[-1]) - date.fromisoformat(p.dates[0])).days / 365.25
    r = p.wealth[1:] / p.wealth[:-1] - 1
    ex = r - RF / fr.A_wealth
    path = np.concatenate([[1.0], p.wealth])
    peak = np.maximum.accumulate(path)
    return {"growth": float(np.log(p.wealth[-1]) / years),
            "sharpe": float(ex.mean() / ex.std() * np.sqrt(fr.A_wealth)),
            "vol": float(r.std() * np.sqrt(fr.A_wealth)),
            "mdd": float((1 - path / peak).max()),
            "turnover": float(sum(t.turnover for t in p.trades[1:]) / years),
            "costs": float(sum(t.cost for t in p.trades))}


def fmt_summary(m: dict[str, float | str], keys: tuple[str, ...]) -> str:
    if "ruin" in m:
        return f"RUIN on {m['ruin']}"
    return " ".join(f"{k} {m[k]:.6f}" for k in keys)


def main() -> None:
    fr = frames("E5")
    log = [(f"E5 ({', '.join(fr.funds)}): estimation frame T = {len(fr.est_dates)}, A = {fr.A:.6f}; wealth frame "
            f"{len(fr.wealth_dates)} dates, A_w = {fr.A_wealth:.6f}")]
    sigs = signals(fr, log)
    rows, trows = [], []
    log.append("net of costs, from the first trade (2019-03 onward): annual log growth, Sharpe ratio (excess of RF, "
               "sqrt A_w), volatility, maximum drawdown, one-way turnover a year (after the first purchase), "
               "costs (sum of cost / pre-trade wealth)")
    every = ("growth", "sharpe", "vol", "mdd", "turnover", "costs")
    for k in RULES:
        p = wealth_path(fr, sigs, k)
        g = wealth_path(fr, sigs, k, cost_mult=0.0)
        log.append(f"{k}: {fmt_summary(summary(fr, p), every)}")
        rows += [(k, d, float(w), float(wg)) for d, w, wg in zip(p.dates, p.wealth, g.wealth, strict=True)]
        trows += [(k, t.signal, t.trade, *map(float, t.target), t.exposure, t.turnover, t.cost) for t in p.trades]
    for spread in (0.0, 0.05):
        m = summary(fr, wealth_path(fr, sigs, "R8", spread=spread))
        log.append(f"R8 with a borrowing spread of {spread:.2f}: {fmt_summary(m, ('growth', 'sharpe'))}")
    for k in RULES:
        m = summary(fr, wealth_path(fr, sigs, k, cost_mult=2.0))
        log.append(f"{k} at twice the costs: {fmt_summary(m, ('growth', 'sharpe'))}")
    PROC.mkdir(exist_ok=True)
    pl.DataFrame(rows, schema=["rule", "date", "wealth", "wealth_gross"], orient="row").write_parquet(
        PROC / "vol5_rules.parquet")
    pl.DataFrame(trows, schema=["rule", "signal", "trade", *fr.funds, "exposure", "turnover", "cost"],
                 orient="row").write_parquet(PROC / "vol5_trades.parquet")
    text = "\n".join(log) + "\n"
    (PROC / "vol5_rules.txt").write_text(text, encoding="utf-8", newline="\n")
    print(text, end="")


if __name__ == "__main__":
    main()
