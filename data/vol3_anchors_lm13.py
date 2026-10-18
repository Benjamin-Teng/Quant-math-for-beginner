"""LM13 anchors: every number the Volume III brief for LM13 (plans/vol-3.md) quotes, one line per anchor.

Sample: TR23, the TAIEX total-return index, from data/processed/vol3_taiex.parquet (built and checked by
data/vol3_series.py, which must be run first): 5,850 closes 2003-01-02 .. 2026-10-08, column R the simple daily
return (null on the first row), column Rp the price index's. Conventions:
  - single-day statements use the T = 5,849 returns; statements about two consecutive days use the pair space,
    the 5,848 return dates from 2003-01-06 whose previous return is in the sample ("yesterday" = that return);
  - thresholds are inclusive and counted with the guard (R <= -x + 1e-12, R >= x - 1e-12); every guarded count is
    asserted equal to an exact count with fractions.Fraction from the two-decimal closes;
  - limit regimes by return date: 7% up to 2015-05-29, 10% from 2015-06-01;
  - blocks: consecutive, non-overlapping, from the first return; the last T mod n returns are left out;
  - no simulation, so no random generator.
Values quoted from earlier modules (LM4, LM5) are recomputed or restated and marked in plans/vol-3-anchors.md.

Run from the repository root:
    PYTHONUTF8=1 uv run python data/vol3_anchors_lm13.py [repository root]
(the optional argument is the repository root; without it the script reads processed/ beside itself, data/processed).
It prints "A13-NN <value>" per anchor, in ID order, and writes nothing.
"""
import sys
from collections.abc import Callable
from fractions import Fraction
from itertools import product
from math import log
from pathlib import Path

import numpy as np
import polars as pl
from numpy.typing import NDArray

Bools = NDArray[np.bool_]
EPS = 1e-12
HERE = Path(__file__).resolve().parent
PROC = HERE / "processed"          # data/processed when this script sits in data/


def le(x: NDArray[np.float64], c: float) -> Bools:
    """x <= c with the guard."""
    return x <= c + EPS


def ge(x: NDArray[np.float64], c: float) -> Bools:
    """x >= c with the guard."""
    return x >= c - EPS


def g(x: float) -> str:
    """A float as the script prints it: ten significant digits."""
    return f"{x:.10g}"


def pct(x: float) -> str:
    """A share in percent, ten significant digits."""
    return f"{100 * x:.10g}%"


def compute(proc: Path) -> dict[str, str]:
    df = pl.read_parquet(proc / "vol3_taiex.parquet")
    dates = [d.isoformat() for d in df["date"].to_list()]
    tr = df["tr"].to_numpy()
    assert df["R"][0] is None and df["R"].null_count() == 1
    R = df["R"].to_numpy()[1:]
    Rp = df["Rp"].to_numpy()[1:]
    rd = dates[1:]
    T = len(R)

    # exact returns from the two-decimal closes; the float column must be the same numbers
    TF = [Fraction(f"{x:.2f}") for x in tr]
    assert all(float(a) == x for a, x in zip(TF, tr, strict=True))
    RF = [TF[i] / TF[i - 1] - 1 for i in range(1, len(TF))]
    assert np.allclose(R, [float(r) for r in RF], rtol=0, atol=1e-15)

    def exact_le(c: Fraction) -> Bools:
        return np.array([r <= c for r in RF])

    def exact_ge(c: Fraction) -> Bools:
        return np.array([r >= c for r in RF])

    def fall(pc: int) -> Bools:            # R <= -pc %, guarded, checked against the exact count
        m = le(R, -pc / 100)
        assert (m == exact_le(Fraction(-pc, 100))).all()
        return m

    def rise(pc: int) -> Bools:            # R >= +pc %
        m = ge(R, pc / 100)
        assert (m == exact_ge(Fraction(pc, 100))).all()
        return m

    V: dict[str, str] = {}

    # ---- earlier modules' printed values
    fstar = 0.5 / 0.01 - 0.5 / 0.02
    gstar = 0.5 * log(1.5) + 0.5 * log(0.75)
    V["lm04"] = f"f* {g(fstar)}; g* {g(gstar)} (printed 25 and 5.889% in lm04.md:345)"
    V["limit"] = "7% to 10% on 2015-06-01 (printed in lm05.md:364)"
    V["gh"] = "16%; 46% and 50% (quoted: Gigerenzer and Hoffrage 1995, Study 1)"

    # ---- sample
    V["sample"] = f"closes {len(tr)}; T {T}; returns {rd[0]} .. {rd[-1]}"
    V["pairs"] = f"{T - 1} pairs; first pair date {rd[1]}"
    V["first"] = f"{pct(R[0])} on {rd[0]}"
    i_min, i_max = int(R.argmin()), int(R.argmax())
    V["extremes"] = f"min {pct(R[i_min])} on {rd[i_min]}; max {pct(R[i_max])} on {rd[i_max]}"
    ties = {c: sum(1 for r in RF if r == Fraction(c, 100)) for c in (0, -1, 1, -2, 2, -3, 3, -4, 4, -5, 5)}
    V["ties"] = f"exact returns at 0, -1, +1, ..., -5, +5 %: {list(ties.values())}; distinct returns {len(set(RF))}"

    # ---- regimes
    rda = np.array(rd)
    reg7, reg10 = rda <= "2015-05-29", rda >= "2015-06-01"
    assert (reg7 ^ reg10).all()
    n7, n10 = int(reg7.sum()), int(reg10.sum())
    V["regimes"] = f"7%: {n7} returns {rda[reg7][0]} .. {rda[reg7][-1]}; 10%: {n10} returns {rda[reg10][0]} .. {rda[reg10][-1]}"

    # ---- the case: A = fall of 3% or more today, B = |R| >= 2% yesterday, on the pair space
    crash = fall(3)
    big = rise(2) | fall(2)
    nP = T - 1
    A, Byest = crash[1:], big[:-1]
    nA, nB = int(A.sum()), int(Byest.sum())
    nAB = int((A & Byest).sum())
    V["crash"] = f"{int(crash.sum())} of {T}: {pct(crash.mean())}"
    V["bigB"] = f"{nB} of {nP}"
    joint = (nAB, nA - nAB, nB - nAB, nP - nA - nB + nAB, nP - nA, nP - nB)
    V["joint"] = "A&B, A&Bc, Ac&B, neither, Ac, Bc: " + ", ".join(map(str, joint))
    hit, fa = nAB / nA, (nB - nAB) / (nP - nA)
    pA_pairs = nA / nP
    V["hit"] = f"{nAB}/{nA} = {pct(hit)}"
    V["fa"] = f"{nB - nAB}/{nP - nA} = {pct(fa)}"
    V["pAB"] = f"{nAB}/{nB} = {pct(nAB / nB)}; days per crash {g(nB / nAB)}"
    V["ratio"] = f"Pr(A given B)/Pr(A), Pr(A) = {nA}/{nP}: {g((nAB / nB) / pA_pairs)}"
    V["inv"] = f"Pr(B given A)/Pr(A given B) = {g(hit / (nAB / nB))}"

    # ---- knowledge checks
    V["kc2"] = f"{g(0.9 + 0.9 - 1)}"
    down = R < 0
    up = R > 0
    yD, tD = down[:-1], down[1:]
    nDD, nDU = int((yD & tD).sum()), int((yD & ~tD).sum())
    nUD, nUU = int((~yD & tD).sum()), int((~yD & ~tD).sum())
    V["kc3"] = f"{nDD}/{nDD + nDU} = {g(nDD / (nDD + nDU))}; {nDD}/{nDD + nUD} = {g(nDD / (nDD + nUD))}"
    V["kc4"] = (f"Pr(up) {int(up.sum())}/{T} = {g(up.mean())}, Pr(down) {int(down.sum())}/{T} = {g(down.mean())}; "
                f"product of the printed 0.5480 x 0.4520 = {g(0.5480 * 0.4520)}; exact {g(up.mean() * down.mean())}")
    lr = hit / fa
    V["kc5"] = f"LR = Pr(B given A)/Pr(B given Ac) = {g(lr)}; base rate with Pr(A given B) = 1/2: 1/(1 + LR) = {pct(1 / (1 + lr))}"
    V["dd2"] = f"2^3 - 3 - 1 = {2 ** 3 - 3 - 1}"
    n_m1, n_p1 = int(fall(1).sum()), int(le(R, 0.01).sum())
    assert (le(R, 0.01) == exact_le(Fraction(1, 100))).all()
    V["kc6"] = (f"Fhat(0) = {int(le(R, 0.0).sum())}/{T} = {g(le(R, 0.0).mean())}; "
                f"Pr(-1% < R <= 1%) = ({n_p1} - {n_m1})/{T} = {n_p1 - n_m1}/{T} = {g((n_p1 - n_m1) / T)}")

    # ---- X1 shares
    V["x1"] = (f"Pr(A given Bc) {nA - nAB}/{nP - nB} = {pct((nA - nAB) / (nP - nB))}; Pr(A) {nA}/{nP} = {pct(pA_pairs)}; "
               f"Pr(B) {nB}/{nP} = {pct(nB / nP)}")

    # ---- X2 / E2: falls of 2% or more yesterday and today
    f2 = fall(2)
    y2, t2 = f2[:-1], f2[1:]
    ny, nt, nb2, nu2 = int(y2.sum()), int(t2.sum()), int((y2 & t2).sum()), int((y2 | t2).sum())
    assert nu2 == ny + nt - nb2
    V["venn"] = (f"yesterday {ny}, today {nt}, both {nb2}, either {nu2}; regions {ny - nb2}, {nb2}, {nt - nb2}, "
                 f"{nP - nu2}")

    # ---- X3: crash share by yesterday's return, buckets (lo, hi] in %
    yR = R[:-1]
    edges = [(None, -3), (-3, -2), (-2, -1), (-1, 0), (0, 1), (1, 2), (2, 3), (3, None)]
    rows = []
    tot_days = tot_crash = 0
    for lo, hi in edges:
        m = np.ones(nP, dtype=bool)
        if lo is not None:
            m &= ~le(yR, lo / 100)
        if hi is not None:
            m &= le(yR, hi / 100)
        d, c = int(m.sum()), int((m & A).sum())
        tot_days, tot_crash = tot_days + d, tot_crash + c
        rows.append(f"{d}/{c} {pct(c / d)}")
    assert (tot_days, tot_crash) == (nP, nA)
    V["x3"] = "; ".join(rows)

    # ---- X4: signs of consecutive days
    assert not (R == 0).any()
    V["x4"] = (f"DD {nDD}, DU {nDU}, UD {nUD}, UU {nUU}; rows {nDD + nDU}, {nUD + nUU}; columns {nDD + nUD}, "
               f"{nDU + nUU}; Pr(D given D) {g(nDD / (nDD + nDU))}, Pr(D given U) {g(nUD / (nUD + nUU))}, "
               f"Pr(D today) {g((nDD + nUD) / nP)}")
    ind = [(nDD + nDU) * (nDD + nUD) / nP, (nDD + nDU) * (nDU + nUU) / nP,
           (nUD + nUU) * (nDD + nUD) / nP, (nUD + nUU) * (nDU + nUU) / nP]
    V["x4ind"] = "if independent DD, DU, UD, UU: " + ", ".join(g(x) for x in ind) + f"; sum {g(sum(ind))}"

    # ---- X5: the two limit regimes (single days; pairs with both days inside a regime)
    parts = []
    for name, m in (("7%", reg7), ("10%", reg10)):
        mp = m[1:] & m[:-1]
        a_in, b_in, ab_in = int((A & mp).sum()), int((Byest & mp).sum()), int((A & Byest & mp).sum())
        c_r = int((crash & m).sum())
        parts.append(f"{name}: days {int(m.sum())} ({pct(m.mean())}), falls {c_r} ({pct(c_r / m.sum())}); "
                     f"pairs inside {int(mp.sum())}, after a big move {ab_in}/{b_in} = {pct(ab_in / b_in)}, "
                     f"hit {ab_in}/{a_in} = {pct(ab_in / a_in)}")
    i_s = rd.index("2015-05-29")
    parts.append(f"straddling pair {rd[i_s]} ({pct(R[i_s])}) -> {rd[i_s + 1]} ({pct(R[i_s + 1])}): "
                 f"crash {bool(crash[i_s + 1])}, big {bool(big[i_s])}")
    V["x5"] = "; ".join(parts)

    # ---- X6: the empirical distribution function at three points
    V["x6"] = "; ".join(f"Fhat({c:+d}%) = {int(le(R, c / 100).sum())}/{T} = {g(le(R, c / 100).mean())}"
                        for c in (-3, 0, 3))

    # ---- X7: 1% bins (lo, hi], tails pooled
    bins = [(None, -5)] + [(k, k + 1) for k in range(-5, 5)] + [(5, None)]
    counts = []
    for lo, hi in bins:
        m = np.ones(T, dtype=bool)
        if lo is not None:
            m &= ~le(R, lo / 100)
        if hi is not None:
            m &= le(R, hi / 100)
        counts.append(int(m.sum()))
    assert sum(counts) == T
    V["x7"] = ("counts " + ", ".join(map(str, counts)) + "; shares " + ", ".join(pct(c / T) for c in counts)
               + f"; shares rounded to 0.01 points sum to {sum(round(100 * c / T, 2) for c in counts):.2f}%")

    # ---- widget: odds and the 1,000-day picture
    prior_odds, post_odds = nA / (nP - nA), nAB / (nB - nAB)
    V["odds"] = (f"prior odds {nA}/{nP - nA} = {g(prior_odds)}; LR = {g(lr)}; posterior odds {nAB}/{nB - nAB} = "
                 f"{g(post_odds)}; printed 0.018815 x 3.7215 = {g(0.018815 * 3.7215)}; "
                 f"0.07002/1.07002 = {pct(0.07002 / 1.07002)}")
    cells = [nAB, nA - nAB, nB - nAB, nP - nA - nB + nAB]          # hits, misses, false alarms, rest
    per = [1000 * c / nP for c in cells]
    sq = [int(x) for x in per]
    for i in sorted(range(4), key=lambda i: per[i] - sq[i], reverse=True)[: 1000 - sum(sq)]:
        sq[i] += 1
    V["squares"] = (f"per 1,000: {', '.join(g(x) for x in per)}; squares {sq}; picture share {sq[0]}/{sq[0] + sq[2]} "
                    f"= {pct(sq[0] / (sq[0] + sq[2]))}")
    V["widget"] = (f"Pr(B) {pct(nB / nP)}; Pr(A given B) {pct(nAB / nB)}; Pr(A given Bc) {pct((nA - nAB) / (nP - nB))}; "
                   f"ratio {g((nAB / nB) / pA_pairs)}; from the printed 0.01847, 0.2963, 0.07962: Pr(B) "
                   f"{pct(0.01847 * 0.2963 + 0.98153 * 0.07962)}")

    # ---- E1, E5: two fair trades, exact
    om = list(product("+-", repeat=2))

    def pr(ev: Callable[[tuple[str, ...]], bool]) -> Fraction:
        return Fraction(sum(1 for w in om if ev(w)), len(om))

    V["e1"] = (f"Pr(B) = {pr(lambda w: '-' in w)}; Pr(A and B) = {pr(lambda w: w[0] == '+' and '-' in w)}; "
               f"wealth below start only on --: {[''.join(w) for w in om if (1.5 if w[0] == '+' else 0.75) * (1.5 if w[1] == '+' else 0.75) < 1]}")
    pa = pr(lambda w: w[0] == "+")
    pb = pr(lambda w: w[1] == "+")
    pc = pr(lambda w: w[0] == w[1])
    pairs3 = [pr(lambda w: w[0] == "+" and w[1] == "+"), pr(lambda w: w[0] == "+" and w[0] == w[1]),
              pr(lambda w: w[1] == "+" and w[0] == w[1])]
    V["e5"] = (f"each {pa}, {pb}, {pc}; pairs {', '.join(map(str, pairs3))}; all three "
               f"{pr(lambda w: w[0] == '+' and w[1] == '+')} against {pa * pb * pc}")

    # ---- E2 numbers
    V["e2"] = (f"union {nu2}/{nP} = {pct(nu2 / nP)}; sum {ny + nt}/{nP} = {pct((ny + nt) / nP)}; "
               f"Pr(today) {nt}/{nP} = {pct(nt / nP)}; independent both {nP}*0.0431^2 = {g(nP * 0.0431 ** 2)}, "
               f"exact {g(nP * (ny / nP) * (nt / nP))}")

    # ---- E3: crash after crash
    yA = crash[:-1]
    ncc = int((yA & A).sum())
    V["e3"] = (f"{ncc} of {int(yA.sum())} = {pct(ncc / yA.sum())}; both {ncc}/{nP} = {pct(ncc / nP)}; "
               f"ratio to base rate {g((ncc / yA.sum()) / pA_pairs)} (printed 12.04/1.85 = {g(12.04 / 1.85)}); "
               f"pairs if independent {g(nP * (int(yA.sum()) / nP) * pA_pairs)}")

    # ---- E4: inside the tail
    n4, n5 = int(fall(4).sum()), int(fall(5).sum())
    nc = int(crash.sum())
    V["e4"] = (f"Pr(R<=-5% given R<=-3%) {n5}/{nc} = {pct(n5 / nc)}; Pr(R<=-4% given R<=-3%) {n4}/{nc} = {pct(n4 / nc)}; "
               f"mean R of the {nc} days {pct(R[crash].mean())}")

    # ---- E6 and P6: at least one crash in a block
    p1 = nc / T

    def blocks(n: int) -> tuple[int, int, int]:
        nb = T // n
        has = crash[: nb * n].reshape(nb, n).any(axis=1)
        return nb, T - nb * n, int(has.sum())

    nb20, left20, hit20 = blocks(20)
    V["e6"] = (f"Pr(A) = {nc}/{T} = {pct(p1)}; model 1-(1-108/5849)^20 = {pct(1 - (1 - p1) ** 20)}; "
               f"from the printed 1.8465%: {pct(1 - (1 - 0.018465) ** 20)}; blocks {nb20}, left out {left20}, "
               f"with a crash {hit20} ({pct(hit20 / nb20)}); model blocks {g(nb20 * (1 - (1 - p1) ** 20))}, "
               f"from the printed 31.1%: {g(nb20 * 0.311)}")

    # ---- E7: total probability and Bayes across the regimes
    c7, c10 = int((crash & reg7).sum()), int((crash & reg10).sum())
    w7, w10 = n7 / T, n10 / T
    q7, q10 = c7 / n7, c10 / n10
    trap = 0.0130 * 0.4739 / (0.0234 * 0.5261 + 0.0130 * 0.4739)
    V["e7"] = (f"Pr(A given 7%) {c7}/{n7} = {pct(q7)}; Pr(A given 10%) {c10}/{n10} = {pct(q10)}; weights {pct(w7)}, {pct(w10)}; "
               f"total {pct(q7 * w7 + q10 * w10)}; Pr(10% given A) {c10}/{c7 + c10} = {pct(q10 * w10 / (q7 * w7 + q10 * w10))}; "
               f"from the printed 2.34%, 1.30%, 0.5261, 0.4739: {pct(trap)}")

    # ---- E8: the case by Bayes' rule
    def bayes(b: float, h: float, f_: float) -> float:
        return b * h / (b * h + (1 - b) * f_)

    V["e8"] = (f"inputs {pct(pA_pairs)}, {pct(hit)}, {pct(fa)}; (13.9) with 0.01847, 0.2963, 0.07962: "
               f"{pct(bayes(0.01847, 0.2963, 0.07962))}; with the case's 0.0185, 0.296, 0.0796: "
               f"{pct(bayes(0.0185, 0.296, 0.0796))}; LR from the printed 29.63%, 7.962%: {g(0.2963 / 0.07962)}")

    # ---- E9 and P8: the manager
    def lr_mgr(wins: int, losses: int) -> float:
        return 0.55 ** wins * 0.45 ** losses / 0.5 ** (wins + losses)

    lr8 = lr_mgr(8, 4)
    po8 = (0.1 / 0.9) * lr8
    po8p = (0.1 / 0.9) * 1.4064
    V["e9"] = (f"LR {g(lr8)}; posterior odds {g(po8)}; posterior {pct(po8 / (1 + po8))}; from the printed 1.4064: "
               f"odds {g(po8p)}, posterior {pct(po8p / (1 + po8p))}")
    lr16 = lr_mgr(16, 8)
    po16 = (0.1 / 0.9) * lr16
    po16p = (0.1 / 0.9) * 1.9780
    V["p8"] = (f"LR {g(lr16)} (1.4064^2 = {g(1.4064 ** 2)}); posterior {pct(po16 / (1 + po16))}, from the printed "
               f"1.9780 {pct(po16p / (1 + po16p))}; prior giving 1/2 after 8 of 12: {pct(1 / (1 + lr8))}, "
               f"from the printed 1.4064 {pct(1 / (1 + 1.4064))}")

    # ---- E10 and P9: wealth multiples at f = 25 (1 + 25 x 2% = 1.5, 1 - 25 x 1% = 0.75)
    up_m, dn_m = 1 + fstar * 0.02, 1 - fstar * 0.01
    vals2 = {"++": up_m ** 2, "+-": up_m * dn_m, "--": dn_m ** 2}
    V["e10"] = (f"X = {', '.join(g(v) for v in vals2.values())}; pmf 1/4, 1/2, 1/4; F_X(1) = 1/4; "
                f"half-logs {', '.join(pct(log(v) / 2) for v in vals2.values())}")
    v3: dict[float, int] = {}
    for seq in product((up_m, dn_m), repeat=3):
        v = round(seq[0] * seq[1] * seq[2], 9)
        v3[v] = v3.get(v, 0) + 1
    below = sum(c for v, c in v3.items() if v < 1)
    V["p9"] = "; ".join(f"{g(v)}: {c}/8" for v, c in sorted(v3.items(), reverse=True)) + f"; Pr(W3 < W0) = {Fraction(below, 8)}"

    # ---- P1
    n_dn2, n_up2 = int(f2.sum()), int(rise(2).sum())
    a1, b1 = 0.0431, 0.0405
    V["p1"] = (f"Pr(R<=-2%) {n_dn2}/{T} = {pct(n_dn2 / T)}; Pr(R>=2%) {n_up2}/{T} = {pct(n_up2 / T)}; "
               f"Pr(abs(R)>=2%) {n_dn2 + n_up2}/{T} = {pct((n_dn2 + n_up2) / T)}; printed sum {pct(a1 + b1)}, "
               f"product {pct(a1 * b1)}, 1-(1-a)(1-b) {pct(1 - (1 - a1) * (1 - b1))}")

    # ---- P2: the case inside the 10% regime
    mp = reg10[1:] & reg10[:-1]
    n2, a2, b2, ab2 = int(mp.sum()), int((A & mp).sum()), int((Byest & mp).sum()), int((A & Byest & mp).sum())
    V["p2"] = (f"pairs {n2}; base {a2}/{n2} = {pct(a2 / n2)}; hit {ab2}/{a2} = {pct(ab2 / a2)}; false alarms "
               f"{b2 - ab2}/{n2 - a2} = {pct((b2 - ab2) / (n2 - a2))}; (13.9) from the printed 1.299%, 41.67%, "
               f"6.252%: {pct(bayes(0.01299, 0.4167, 0.06252))}; exact {ab2}/{b2} = {pct(ab2 / b2)}")

    # ---- P4: falls of 2% or more on three consecutive days (5,847 triples)
    e0, e1, e2 = f2[:-2], f2[1:-1], f2[2:]
    n3 = len(e0)
    un3 = int((e0 | e1 | e2).sum())
    s3 = int(e0.sum() + e1.sum() + e2.sum())
    V["p4"] = (f"triples {n3}; singles {int(e0.sum())}, {int(e1.sum())}, {int(e2.sum())}; pairs 1-2 "
               f"{int((e0 & e1).sum())}, 1-3 {int((e0 & e2).sum())}, 2-3 {int((e1 & e2).sum())}; all three "
               f"{int((e0 & e1 & e2).sum())}; union {un3} ({pct(un3 / n3)}); bound {s3} ({pct(s3 / n3)})")

    # ---- P5: three down days in a row
    d0, d1, d2 = down[:-2], down[1:-1], down[2:]
    c0, c01, c012 = int(d0.sum()), int((d0 & d1).sum()), int((d0 & d1 & d2).sum())
    V["p5"] = (f"{c0}/{n3} = {g(c0 / n3)}, {c01}/{c0} = {g(c01 / c0)}, {c012}/{c01} = {g(c012 / c01)}; product of "
               f"the printed 0.4519 x 0.4637 x 0.4424 = {pct(0.4519 * 0.4637 * 0.4424)}; exact {c012}/{n3} = "
               f"{pct(c012 / n3)}; independence ({int(down.sum())}/{T})^3 = {pct(down.mean() ** 3)}, from 0.45204 "
               f"{pct(0.45204 ** 3)}, from 0.4520 {pct(0.4520 ** 3)}")

    # ---- P6: the fifty-fifty horizon
    nb38, left38, hit38 = blocks(38)
    V["p6"] = (f"n = ln 0.5/ln(1 - 108/5849) = {g(log(0.5) / log(1 - p1))}; at 37 {pct(1 - (1 - p1) ** 37)}, at 38 "
               f"{pct(1 - (1 - p1) ** 38)}; blocks of 38: {nb38}, left out {left38}, with a crash {hit38} "
               f"({pct(hit38 / nb38)})")

    # ---- P7: falls of 5% or more by regime
    f5 = fall(5)
    c57, c510 = int((f5 & reg7).sum()), int((f5 & reg10).sum())
    s7, s10 = c57 / n7, c510 / n10
    lrp = (0.002525 / 0.002600)
    po7 = (n10 / n7) * 0.971
    V["p7"] = (f"{c57}/{n7} = {pct(s7)}; {c510}/{n10} = {pct(s10)}; LR {g(s10 / s7)}, from the printed "
               f"{g(lrp)}; Pr(10% given R<=-5%) {c510}/{c57 + c510} = {pct(c510 / (c57 + c510))}; via the printed LR 0.971: "
               f"{pct(po7 / (1 + po7))}; prior {pct(w10)}")

    # ---- P10: indicators of down yesterday and down today
    V["p10"] = (f"Pr(X=1,Y=1) {nDD}/{nP} = {g(nDD / nP)}; Pr(X=1) {nDD + nDU}/{nP} = {g((nDD + nDU) / nP)}, "
                f"Pr(Y=1) {nDD + nUD}/{nP} = {g((nDD + nUD) / nP)}; product exact {g((nDD + nDU) * (nDD + nUD) / nP ** 2)}, "
                f"of the printed 0.4519 x 0.4521 = {g(0.4519 * 0.4521)}")

    # ---- P12: losing trades in two independent trades, win probability 0.55
    p_, q_ = 0.55, 0.45
    V["p12"] = f"1 - q^2 = {g(1 - q_ ** 2)}; 2pq = {g(2 * p_ * q_)}; 1 - p^2 = {g(1 - p_ ** 2)}"

    # ---- lab: a big move in the previous five sessions
    absR = np.abs(R)
    idx = np.arange(5, T)
    prev = np.array([ge(absR[i - 5:i], 0.02).any() for i in idx])
    cw = crash[idx]
    V["lab5"] = (f"days {len(idx)}; crashes with abs(R) >= 2% in the previous five sessions {int((prev & cw).sum())}/"
                 f"{int(cw.sum())} = {pct((prev & cw).sum() / cw.sum())}")

    # ---- data trap: total minus price return
    gap = R - Rp
    j = int(gap.argmax())
    V["gap"] = f"max R - Rp = {g(gap[j] * 1e4)} bp on {rd[j]}"

    return V


ORDER = [
    "lm04", "limit", "sample", "pairs", "first", "ties", "regimes", "crash", "hit", "fa", "bigB", "pAB", "ratio",
    "inv", "joint", "dd2", "kc2", "kc3", "kc4", "kc5", "kc6", "gh", "x1", "venn", "x3", "x4", "x4ind", "x5", "x6",
    "extremes", "x7", "widget", "odds", "squares", "e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8", "e9", "e10", "p1",
    "p2", "p4", "p5", "p6", "p7", "p8", "p9", "p10", "p12", "lab5", "gap",
]


def main() -> int:
    proc = Path(sys.argv[1]).resolve() / "data" / "processed" if len(sys.argv) > 1 else PROC
    V = compute(proc)
    assert sorted(ORDER) == sorted(V), (set(V) ^ set(ORDER))
    for i, name in enumerate(ORDER, start=1):
        print(f"A13-{i:02d} {V[name]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
