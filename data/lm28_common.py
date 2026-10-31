"""Shared inputs and closed forms for LM28's scripts (data/lm28_numbers.py and data/lm28_charts.py import it).

Not a script: `uv run python data/lm28_numbers.py` and `uv run python data/lm28_charts.py` run it. It reads only
data/processed/*.parquet, through the shared builders (run them first; this module runs neither):
  * E5 (plans/vol-5.md, "Data"): data/vol5_series.py's frames("E5"): the estimation frame (dates on which every fund
    has a one-session total return; T = 2,362, A = T / years) and the wealth frame (every TR23 session after the base
    close 2017-01-17; a halted fund earns 0 and books its spanning return when it trades again; A_w = sessions /
    years). The funds, in this order: 0050, 00646, 00679B, 00635U, 00642U.
  * The through case's schedule: data/vol5_rules.py's schedule(), WINDOW (504) and RF (1.5% a year). The first window
    is the 504 estimation rows through the first signal; the test period is every wealth-frame session after that
    signal's trade (2019-03-04), to 2026-10-08. No rule of R1-R8 is recomputed here (shared decision "Through case").
  * U28 (Volume II): data/lm10_series.py's u28() (28 TWSE sector price indices, T = 4,382, halves of 2,191).

Conventions (the LM28 brief, plans/vol-5.md, and plans/vol-5-anchors.md, "LM28", whose definitions this module
implements as data/vol5_anchors_lm28.py does): mu = A * (window mean) and Sigma = A * cov0 (divisor T), annual, treated
as known; e = mu - r_f 1 with r_f = 1.5% a year. Every linear system is solved with numpy.linalg.solve, never with an
explicit inverse. Held portfolios keep constant weights (rebalanced every session, no costs) and earn w'R_t on the
wealth frame; joint statistics of the test period use the estimation frame's test rows.
"""
import sys
from datetime import date
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from lm10_series import u28
from vol5_rules import CLARABEL_OPTS, OSQP_OPTS, RF, WINDOW, cov0, minvar, schedule
from vol5_series import frames

Vec = NDArray[np.float64]
Mat = NDArray[np.float64]

__all__ = ["CLARABEL_OPTS", "OSQP_OPTS", "RF", "WINDOW", "cov0", "frames", "minvar", "schedule", "u28"]


def years(a: str, b: str) -> float:
    """Calendar days from a to b over 365.25 (AUTHORING section 8)."""
    return (date.fromisoformat(b) - date.fromisoformat(a)).days / 365.25


def kurt(r: Vec) -> float:
    """The raw sample kurtosis (divisor T)."""
    c = r - r.mean()
    return float((c**4).mean() / (c**2).mean() ** 2)


class Opt:
    """The closed forms of LM28 for annualized mu and Sigma (Sigma positive definite)."""

    def __init__(self, mu: Vec, S: Mat, rf: float = RF) -> None:
        n = len(mu)
        self.mu, self.S, self.rf = mu, S, rf
        self.one = np.ones(n)
        x = np.linalg.solve(S, self.one)                       # Sigma^-1 1
        self.s2min = 1 / float(x.sum())                        # (28.2)
        self.wmv = x * self.s2min
        self.mumv = float(mu @ self.wmv)
        d = mu - self.mumv * self.one
        self.dir = np.linalg.solve(S, d)                       # Sigma^-1 (mu - mu_mv 1)
        self.srinf2 = float(d @ self.dir)                      # SR_inf^2, (28.5)
        self.e = mu - rf * self.one
        self.y = np.linalg.solve(S, self.e)                    # Sigma^-1 e
        self.den = float(self.y.sum())                         # 1' Sigma^-1 e
        self.sr2 = float(self.e @ self.y)                      # SR*^2, (28.6)
        self.wtan = self.y / self.den

    def front_var(self, mp: float) -> float:
        return self.s2min + (mp - self.mumv) ** 2 / self.srinf2      # (28.5)

    def front_w(self, mp: float) -> Vec:
        return self.wmv + (mp - self.mumv) / self.srinf2 * self.dir  # (28.4)


def lemma(S: Mat, K: Mat, b: Vec) -> tuple[Vec, float, Vec]:
    """(28.1): min w'Sw subject to Kw = b; returns (w*, value, multipliers lambda, LM7's signs: 2Sw = K'lambda)."""
    Si_Kt = np.linalg.solve(S, K.T)
    G = K @ Si_Kt
    lam = 2 * np.linalg.solve(G, b)
    w = Si_Kt @ lam / 2
    return w, float(b @ np.linalg.solve(G, b)), lam


def smin(S_: Mat) -> float:
    """(28.2)'s sigma_min, by solving against 1."""
    return 1 / float(np.sqrt(np.linalg.solve(S_, np.ones(len(S_))).sum()))


# ---------------------------------------------------------------- E5, the first window and the test period
fr = frames("E5")
F = fr.funds
A, Aw = fr.A, fr.A_wealth
sch = schedule(fr)
sig, trade, rows = sch[0]
x = fr.X[rows - WINDOW:rows]                                   # the first window, 504 x 5
w0, w1 = fr.est_dates[rows - WINDOW], fr.est_dates[rows - 1]
assert w1 == sig
assert fr.wealth_dates.index(w0) > 0
b0w = fr.wealth_dates[fr.wealth_dates.index(w0) - 1]           # the close before the window's first return
wd = fr.wealth_dates
i0 = wd.index(trade)
Wt = fr.W[i0 + 1:]                                             # wealth-frame test returns (1,851 x 5)
ed = fr.est_dates
j0 = next(k for k, d in enumerate(ed) if d > trade)
Xt = fr.X[j0:]                                                 # estimation-frame test rows (1,845 x 5)
missing = sorted(set(wd[i0 + 1:]) - set(ed[j0:]))
yt = years(trade, wd[-1])

mu = A * x.mean(axis=0)
S = A * cov0(x)
sd = np.sqrt(np.diag(S))
C = S / np.outer(sd, sd)
St = A * cov0(Xt)
sdt = np.sqrt(np.diag(St))
Ct = St / np.outer(sdt, sdt)
o = Opt(mu, S)
ot = Opt(A * Xt.mean(axis=0), St)
assert np.linalg.eigvalsh(S).min() > 0
