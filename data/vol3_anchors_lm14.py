"""LM14 anchors: every number the LM14 brief (plans/vol-3.md) quotes, as "A14-NN <value>", in ID order.

Sample TR23: data/processed/vol3_taiex.parquet (built and checked by data/vol3_series.py, which must run first),
columns date, tr, price, R, Rp; R is TR23's simple daily return tr_t / tr_{t-1} - 1, null on the first row
(2003-01-02), so T = 5,849 returns from 2003-01-03 to 2026-10-08. Conventions (plans/vol-3.md, Shared decisions):
divisor T for every moment (the moments of the empirical law, mass 1/T on each return); years = calendar days from
the first to the last close / 365.25; A = T / years; counts against a threshold use the guard (<= -x + 1e-12,
>= x - 1e-12), and the -3% count is confirmed with exact fractions of the two-decimal closes. Calendar years
2003-2025 run from the last close of the previous year to the last close of the year, 2003 from its first close
(2003-01-02); 2026 is partial and left out. The small laws (the +2%/-1% bet, LM13's two trades, the four-day bet,
LM4's +1%/-5% trade and its Kelly factor 1 + 8R, 2008/2009 from the printed returns, +100%/-50%) are exact
arithmetic. No simulation, so the seed rule default_rng([e, 20261011]) has nothing to seed.

Run from the repository root (the optional argument is the repository root; default: this file's parent's parent):
    PYTHONUTF8=1 uv run python data/vol3_anchors_lm14.py
It prints one line per anchor and writes nothing.
"""
import sys
from fractions import Fraction
from itertools import pairwise, product
from math import ceil, comb
from pathlib import Path

import numpy as np
import polars as pl
from numpy.typing import NDArray
from scipy import stats

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
HERE = ROOT / "data"
PROC = HERE / "processed"
EPS = 1e-12

Vec = NDArray[np.float64]
VALUES: dict[str, str] = {}


def g(x: float | np.floating, n: int = 10) -> str:
    """A float to n significant digits."""
    return f"{float(x):.{n}g}"


def put(key: str, *parts: str) -> None:
    if key in VALUES:
        raise SystemExit(f"duplicate anchor key {key}")
    VALUES[key] = "; ".join(parts)


def law(x: Vec, p: Vec) -> dict[str, float]:
    """Moments and drag quantities of a law with values x and probabilities p (R > -1)."""
    mu = float((p * x).sum())
    var = float((p * (x - mu) ** 2).sum())
    sd = var**0.5
    gg = float((p * np.log1p(x)).sum())
    y = (x - mu) / (1 + mu)
    t2, t3, t4 = (float((p * y**k).sum()) * (-1) ** k / k for k in (2, 3, 4))
    return {
        "mu": mu, "sd": sd, "var": var, "g": gg, "RG": float(np.expm1(gg)),
        "drag": float(np.log1p(mu)) - gg, "t2": t2, "t3": t3, "t4": t4,
        "skew": float((p * (x - mu) ** 3).sum()) / sd**3 if sd > 0 else 0.0,
        "kurt": float((p * (x - mu) ** 4).sum()) / sd**4 if sd > 0 else 0.0,
    }


def main() -> None:
    df = pl.read_parquet(PROC / "vol3_taiex.parquet").sort("date")
    dates = df["date"].to_list()
    tr = df["tr"].to_numpy().astype(np.float64)
    R = df["R"].drop_nulls().to_numpy().astype(np.float64)
    rdates = dates[1:]
    T = R.size
    days = (dates[-1] - dates[0]).days
    years = days / 365.25
    A = T / years
    r = np.log1p(R)
    Rbar, rbar = float(R.mean()), float(r.mean())
    s, s_r = float(R.std()), float(r.std())
    RG = float(np.expm1(rbar))
    z = (R - Rbar) / s

    # ---- sample
    put("T", f"{T}", f"first return {rdates[0]}", f"last {rdates[-1]}")
    put("yrs", f"{days} calendar days", g(years))
    put("A", g(A))

    # ---- calendar years 2003-2025 (2003 from its first close)
    yr = pl.DataFrame({"date": dates, "tr": tr}).with_columns(pl.col("date").dt.year().alias("y"))
    last = yr.group_by("y").agg(pl.col("tr").last()).sort("y")
    prev = float(tr[0])
    ys: list[int] = []
    ry: list[float] = []
    for y, p in last.iter_rows():
        if y == 2026:
            continue
        ys.append(int(y))
        ry.append(float(p) / prev - 1)
        prev = float(p)
    Ry = np.array(ry)
    n_y = Ry.size
    ann = law(Ry, np.full(n_y, 1 / n_y))
    cagr = float(np.prod(1 + Ry) ** (1 / n_y) - 1)
    r08, r09 = Ry[ys.index(2008)], Ry[ys.index(2009)]
    put("ann_mean", f"{n_y} years {ys[0]}-{ys[-1]}", f"{g(ann['mu'] * 100)}%")
    put("ann_cagr", f"{g(cagr * 100)}%", f"growth factor {g(np.prod(1 + Ry))}")
    put("y0809", f"2008 {g(r08 * 100)}%", f"2009 {g(r09 * 100)}%")
    put("pair_avg", f"unrounded {g((r08 + r09) / 2 * 100)}%", f"from printed {g((-0.4307 + 0.8334) / 2 * 100)}%")
    put("pair_two", f"unrounded {g(((1 + r08) * (1 + r09) - 1) * 100)}%",
        f"from printed {g((0.5693 * 1.8334 - 1) * 100)}%")

    # ---- daily case
    put("Rbar", f"{g(Rbar * 100)}%")
    put("RG", f"{g(RG * 100)}%", f"r_bar {g(rbar * 100)}%")
    put("gapRG", f"{g((Rbar - RG) * 1e4)} bp", f"from the four-decimal rates {g((0.0625 - 0.0552) * 100)} bp")
    put("s2h", f"{g(s**2 / 2 * 1e4)} bp")
    put("gapdiff", f"{g((Rbar - RG - s**2 / 2) * 1e4)} bp")
    put("s", f"{g(s * 100)}%", f"s^2 {g(s**2)}")

    # ---- E1, E3 (LM13's two trades at f = 25) and P9
    X = np.array([0.5625, 1.125, 2.25])
    pX = np.array([0.25, 0.5, 0.25])
    two = {}
    for w in product((1.5, 0.75), repeat=2):
        v = w[0] * w[1]
        two[v] = two.get(v, 0) + 0.25
    put("e1_X", ", ".join(f"{g(v)}: {g(p)}" for v, p in sorted(two.items())),
        f"F_X {', '.join(g(c) for c in np.cumsum(pX))}")
    xmed = float(X[np.searchsorted(np.cumsum(pX), 0.5)])
    put("e1_q", f"F^-1(0.1) {g(X[np.searchsorted(np.cumsum(pX), 0.1)])}",
        f"median {g(xmed)} (Pr(X<={g(xmed)}) {g(pX[X <= xmed].sum())}, Pr(X>={g(xmed)}) {g(pX[X >= xmed].sum())})")
    half = 0.5 * np.log(X)
    put("e1_half", ", ".join(f"{g(v * 100)}%" for v in half),
        f"weighted sum from two-decimal logs {g(0.25 * -28.77 + 0.5 * 5.889 + 0.25 * 40.55)}%")
    EX = float((pX * X).sum())
    put("e1_EX", g(EX), f"1.125^2 = {g(1.125**2)}")
    put("e1_Ehalf", f"{g((pX * half).sum() * 100)}%", f"0.5 ln 1.125 = {g(0.5 * np.log(1.125) * 100)}%")
    put("e1_lnEX", f"ln E X {g(np.log(EX) * 100)}%", f"0.5 ln E X {g(0.5 * np.log(EX) * 100)}%")

    # ---- quoted from Volumes I-II (printed values; 0050 is cited, never recomputed)
    put("lm4coin", f"f_star = 0.5/0.01 - 0.5/0.02 = {g(0.5 / 0.01 - 0.5 / 0.02)}",
        f"g_star {g((0.5 * np.log(1.5) + 0.5 * np.log(0.75)) * 100)}%", "printed in lm04.md:345: 25, 5.889%")
    put("lm0050", "printed in lm04.md:132: 0050 excess kurtosis 8.12, m4 3.7 times the normal's")
    put("lm5A", "printed in lm05.md:521: A = 243.1 (0050)")

    # ---- E2, X3: the empirical law of TR23
    n_le0 = int((R <= 0 + EPS).sum())
    put("F0", f"{n_le0}/{T} = {g(n_le0 / T)}", f"R == 0 on {int((R == 0).sum())} days")
    n_pos = int((R > 0).sum())
    put("pos", f"{n_pos}", f"{g(n_pos / T * 100)}%")
    Rs = np.sort(R)
    put("med", f"{g(Rs[(T + 1) // 2 - 1] * 100)}%", f"order {(T + 1) // 2}", f"np.median {g(np.median(R) * 100)}%")
    n_above = int((R > Rbar).sum())
    put("above", f"{n_above}", f"{g(n_above / T * 100)}%")
    us = (0.001, 0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99, 0.999)
    rows = []
    for u in us:
        j = ceil(u * T - 1e-9)
        inv = float(np.quantile(R, u, method="inverted_cdf"))
        assert inv == Rs[j - 1]
        rows.append(f"u={u}: j={j} {g(inv * 100)}% / linear {g(np.quantile(R, u) * 100)}%")
    put("x3", *rows)

    # ---- KC: die; +-10% day
    die = stats.rv_discrete(values=(np.arange(1, 7), np.full(6, 1 / 6)))
    put("die", f"E {g(die.mean())}", f"Var {g(die.var())} = 35/12 {g(35 / 12)}",
        "medians [3, 4]", f"np.median {g(np.median(np.arange(1, 7)))}", f"rv_discrete median {g(die.median())}")
    put("pm10", f"{g((0.5 * np.log(1.1) + 0.5 * np.log(0.9)) * 100)}%",
        f"0.5 ln 0.99 = {g(0.5 * np.log(0.99) * 100)}%")

    # ---- E4
    G = float(tr[-1] / tr[0])
    put("rbar_bp", f"{g(rbar * 1e4)} bp")
    put("Ar", f"A r_bar {g(A * rbar * 100)}%", f"ln G / years {g(np.log(G) / years * 100)}%",
        f"compound rate exp(A r_bar) - 1 = G^(1/years) - 1 {g(np.expm1(A * rbar) * 100)}%",
        f"from printed 25.2007^(1/23.7645) - 1 = {g((25.2007 ** (1 / 23.7645) - 1) * 100)}%"
        f" (from the printed 13.58%: exp(0.1358) - 1 = {g(np.expm1(0.1358) * 100)}%)")
    put("Gfull", g(G))

    # ---- E5: the +2%/-1% bet
    bet = law(np.array([0.02, -0.01]), np.array([0.5, 0.5]))
    put("bet", f"mu {g(bet['mu'])}", f"sigma {g(bet['sd'])}", f"E R^2 {g(bet['var'] + bet['mu'] ** 2)}",
        f"E R^3 {g(0.5 * 0.02**3 + 0.5 * (-0.01) ** 3)}",
        f"mu^3+3mu sigma^2 {g(bet['mu'] ** 3 + 3 * bet['mu'] * bet['var'])}",
        f"Skew {g(bet['skew'])}", f"Kurt {g(bet['kurt'])}")

    # ---- E6, X4: moments of TR23 against the normal with mu = Rbar, sigma = s
    m2, m3, m4 = float((R**2).mean()), float((R**3).mean()), float((R**4).mean())
    put("m2", f"E R^2 {g(m2)}", f"s^2 {g(s**2)}", f"Rbar^2 {g(Rbar**2)}", f"s^2 + Rbar^2 {g(s**2 + Rbar**2)}",
        f"from four-figure inputs {g(1.460e-4 + 3.907e-7)}", f"from five-figure inputs {g(1.4601e-4 + 3.9069e-7)}")
    put("skew", g(stats.skew(R)))
    put("kurt", f"Kurt {g(stats.kurtosis(R) + 3)}", f"excess {g(stats.kurtosis(R))}")
    put("m3", g(m3))
    n3 = Rbar**3 + 3 * Rbar * s**2
    n4 = Rbar**4 + 6 * Rbar**2 * s**2 + 3 * s**4
    put("nm3", g(n3), f"from six-decimal inputs {g(0.00062505**3 + 3 * 0.00062505 * 0.01208364**2)}")
    put("m4", g(m4))
    put("ratio4", g(m4 / n4))
    m4p, s4p = 0.000625, 0.012084
    put("nm4", g(n4), f"from four-decimal inputs {g(m4p**4 + 6 * m4p**2 * s4p**2 + 3 * s4p**4)}",
        f"from six-decimal inputs {g(0.00062505**4 + 6 * 0.00062505**2 * 0.01208364**2 + 3 * 0.01208364**4)}")
    q2 = (Rbar / s) ** 2
    put("musig", f"(Rbar/s)^2 {g(q2)}",
        f"third: (Rbar/s)^2/3 {g(q2 / 3 * 100)}% (check n3/(3 Rbar s^2) - 1 {g((n3 / (3 * Rbar * s**2) - 1) * 100)}%)",
        f"fourth: 2(Rbar/s)^2 + (Rbar/s)^4/3 {g((2 * q2 + q2**2 / 3) * 100)}%"
        f" (check n4/(3 s^4) - 1 {g((n4 / (3 * s**4) - 1) * 100)}%)",
        f"from the printed four-figure moments 2.740/2.738 - 1 {g((2.740 / 2.738 - 1) * 100)}%,"
        f" 6.430/6.396 - 1 {g((6.430 / 6.396 - 1) * 100)}%")
    put("approx", f"3 mu sigma^2 {g(3 * Rbar * s**2)}", f"3 sigma^4 {g(3 * s**4)}",
        f"from four-decimal inputs {g(3 * m4p * s4p**2)}, {g(3 * s4p**4)}",
        f"from six-decimal inputs {g(3 * 0.00062505 * 0.01208364**2)}, {g(3 * 0.01208364**4)}")
    put("f2mom", f"2s {g(2 * s * 100)}%", f"from printed 2 x 1.2084 = {g(2 * 1.2084)}%", f"E(2R)^2 {g(4 * m2)}")

    # ---- E7, E8, X5, X6: tail bounds
    absR = np.abs(R)
    put("absR", f"{g(absR.mean() * 100)}%")
    put("mk1", f"unrounded {g(absR.mean() / 0.03 * 100)}%", f"from printed {g(0.8402 / 3 * 100)}%")
    put("mk2", f"unrounded {g(m2 / 0.03**2 * 100)}%", f"from printed {g(1.464e-4 / 9e-4 * 100)}%")
    n3a = int((absR >= 0.03 - EPS).sum())
    put("n3abs", f"{n3a}", f"{g(n3a / T * 100)}%")
    k3 = (Rbar + 0.03) / s
    k3p = (0.0625 + 3) / 1.2084
    put("cant3", f"k {g(k3)} -> {g(1 / (1 + k3**2) * 100)}%",
        f"from printed k {g(k3p)} -> {g(1 / (1 + k3p**2) * 100)}%")
    n3d = int((R <= -0.03 + EPS).sum())
    closes = [Fraction(repr(float(v))) for v in tr]
    n3x = sum(1 for a, b in pairwise(closes) if b / a - 1 <= Fraction(-3, 100))
    put("n3", f"{n3d}", f"{g(n3d / T * 100)}%", f"exact-fraction recount {n3x}")
    put("c17", f"1/17 = {g(1 / 17 * 100)}%")
    put("phi4", g(stats.norm.cdf(-4)))
    put("nd4", f"T Phi(-4) {g(T * stats.norm.cdf(-4))}", f"from printed {g(T * 3.17e-5)}",
        f"2 T Phi(-4) {g(2 * T * stats.norm.cdf(-4))}")
    put("th4", f"{g((Rbar - 4 * s) * 100)}%", f"from printed {g(0.0625 - 4 * 1.2084)}%")
    n4 = int((z <= -4 + EPS).sum())
    put("n4", f"{n4}", f"{g(n4 / T * 100)}%")
    put("r92", f"{g(n4 / (T * stats.norm.cdf(-4)))}", f"from printed {g(17 / 0.185)}",
        f"share / bound {g(n4 / T * 17)}")
    n4t = int((np.abs(z) >= 4 - EPS).sum())
    put("n4two", f"{n4t}", f"{g(n4t / T * 100)}%", f"Chebyshev {g(100 / 16)}%")
    imin = int(R.argmin())
    put("x5", f"Cantelli days T/(1+k^2) at k=1,4,8: {g(T / 2)}, {g(T / 17)}, {g(T / 65)}",
        f"min z {g(z[imin])} on {rdates[imin]} (R {g(R[imin] * 100)}%)")
    rows = []
    for k in range(1, 7):
        nt = int((np.abs(z) >= k - EPS).sum())
        nl = int((z <= -k + EPS).sum())
        rows.append(f"k={k}: two-sided {nt} ({g(nt / T * 100)}%), Chebyshev {g(100 / k**2)}%"
                    f" / lower {nl} ({g(nl / T * 100)}%), Cantelli {g(100 / (1 + k**2))}%")
    put("x6", *rows)

    # ---- E9: AM-GM
    put("amgm", f"1 + mean {g(1 + ann['mu'])}", f"geometric mean {g(1 + cagr)}")
    put("pair_amgm", f"AM {g((0.5693 + 1.8334) / 2)}", f"GM {g(np.sqrt(0.5693 * 1.8334))}")

    # ---- widget initial state and X8's pair row: 2008/2009 from the printed returns
    pr = law(np.array([-0.4307, 0.8334]), np.array([0.5, 0.5]))
    put("wid", f"mu {g(pr['mu'] * 100)}%", f"sigma {g(pr['sd'] * 100)}%", f"g {g(pr['g'] * 100)}%",
        f"R_G {g(pr['RG'] * 100)}%", f"ln(1+mu) {g(np.log1p(pr['mu']) * 100)}%",
        f"ln(1+mu)-g {g(pr['drag'] * 100)}", f"mu-R_G {g((pr['mu'] - pr['RG']) * 100)}",
        f"sigma^2/2 {g(pr['var'] / 2 * 100)}", f"2nd-order {g(pr['t2'] * 100)}",
        f"through 4th {g((pr['t2'] + pr['t3'] + pr['t4']) * 100)}", f"(3.9) {g((pr['mu'] - pr['var'] / 2) * 100)}%")
    un = law(np.array([r08, r09]), np.array([0.5, 0.5]))
    put("wid_unr", f"sigma^2/2 {g(un['var'] / 2 * 100)}", f"R_G {g(un['RG'] * 100)}%",
        f"ln(1+mu) {g(np.log1p(un['mu']) * 100)}%")

    # ---- E10, X8: the gap exactly
    tr23 = law(R, np.full(T, 1 / T))
    put("J", f"{g(tr23['drag'] * 1e4)} bp",
        f"check (1+mu)(1-exp(-J)) {g((1 + Rbar) * -np.expm1(-tr23['drag']) * 1e4)} bp",
        f"from printed (1.000625)(1-exp(-0.7316 bp)) {g(1.000625 * -np.expm1(-0.7316e-4) * 1e4)} bp")
    put("terms", f"{g(tr23['t2'] * 1e4)}, {g(tr23['t3'] * 1e4)}, {g(tr23['t4'] * 1e4)} bp",
        f"sum {g((tr23['t2'] + tr23['t3'] + tr23['t4']) * 1e4)}")
    put("ann_drag", f"ln(1+mu)-g {g(ann['drag'] * 100)}", f"2nd {g(ann['t2'] * 100)}",
        f"through 4th {g((ann['t2'] + ann['t3'] + ann['t4']) * 100)}", f"mu-R_G {g((ann['mu'] - ann['RG']) * 100)}",
        f"sigma^2/2 {g(ann['var'] / 2 * 100)}")
    put("lognorm", f"s_r^2/2 {g(s_r**2 / 2 * 1e4)} bp", f"s_r {g(s_r * 100)}%")
    put("ann_sd", f"{g(ann['sd'] * 100)}%", f"skew {g(ann['skew'])}", f"kurt {g(ann['kurt'])}",
        f"g {g(ann['g'] * 100)}%", f"ln(1+mu) {g(np.log1p(ann['mu']) * 100)}%")
    hm = law(np.array([1.0, -0.5]), np.array([0.5, 0.5]))
    put("x8_hm", f"mu {g(hm['mu'] * 100)}%", f"sigma {g(hm['sd'] * 100)}%", f"mu-R_G {g((hm['mu'] - hm['RG']) * 100)}",
        f"sigma^2/2 {g(hm['var'] / 2 * 100)}", f"ln(1+mu)-g {g(hm['drag'] * 100)}", f"2nd {g(hm['t2'] * 100)}",
        f"through 4th {g((hm['t2'] + hm['t3'] + hm['t4']) * 100)}")

    # ---- X7: each calendar year's daily drag against its s^2/2 (2003 from 2003-01-03)
    ryear = np.array([d.year for d in rdates])
    pts = []
    for y in ys:
        x = R[ryear == y]
        mb, rg = float(x.mean()), float(np.expm1(np.log1p(x).mean()))
        pts.append((y, (mb - rg) * 1e4, float(x.var()) / 2 * 1e4))
    gaps = [(abs(a - b), y) for y, a, b in pts]
    rels = [(abs(a / b - 1), y) for y, a, b in pts]
    lo = min(pts, key=lambda t: t[1])
    hi = max(pts, key=lambda t: t[1])
    gmax, rmax = max(gaps), max(rels)
    put("x7", f"min drag {lo[0]} {g(lo[1])} bp (s^2/2 {g(lo[2])})", f"max {hi[0]} {g(hi[1])} bp (s^2/2 {g(hi[2])})",
        f"largest absolute gap {gmax[1]} {g(gmax[0])} bp",
        f"largest gap relative to half the variance {rmax[1]} {g(rmax[0] * 100)}%")

    put("f2drag", f"{g((np.log1p(2 * Rbar) - np.log1p(2 * R).mean()) * 1e4)} bp",
        f"4 x J {g(4 * tr23['drag'] * 1e4)} bp", f"from printed 4 x 0.7316 = {g(4 * 0.7316)}")

    # ---- problems
    four: dict[float, Fraction] = {}
    for j in range(5):
        four[1.02**j * 0.99 ** (4 - j)] = Fraction(comb(4, j), 16)
    put("four", ", ".join(f"{g(v)}: {p}" for v, p in sorted(four.items())),
        f"F {', '.join(str(sum(p for v, p in four.items() if v <= x)) for x in sorted(four))}",
        f"mean {g(sum(v * float(p) for v, p in four.items()))}")
    e_ln1 = 0.5 * np.log(1.02) + 0.5 * np.log(0.99)
    eln4 = sum(np.log(v) * float(p) for v, p in four.items())
    eg4 = sum(v * float(p) for v, p in four.items())
    put("p2", f"E G {g(eg4)} (1.005^4 {g(1.005**4)})", f"E ln(1+R) one day {g(e_ln1 * 100)}%",
        f"E ln G {g(eln4 * 100)}%", f"ln E G {g(np.log(eg4) * 100)}%", f"gap {g((np.log(eg4) - eln4) * 1e4)} bp")
    put("pareto", f"mean 1.5/0.5 = {g(1.5 / 0.5)}")
    tr5 = law(np.array([0.01, -0.05]), np.array([0.9, 0.1]))
    put("p4", f"mu {g(tr5['mu'] * 100)}%", f"sigma {g(tr5['sd'] * 100)}%",
        f"E R^2 {g(tr5['var'] + tr5['mu'] ** 2)}", f"E R^3 {g(0.9 * 0.01**3 + 0.1 * (-0.05) ** 3)}",
        f"Skew {g(tr5['skew'])} (-8/3)", f"Kurt {g(tr5['kurt'])} (73/9), excess {g(tr5['kurt'] - 3)}",
        f"f=8: mu {g(8 * tr5['mu'] * 100)}%, sigma {g(8 * tr5['sd'] * 100)}%")
    nz = stats.norm(0.05, 0.2)
    put("p5", f"E Z^6 {g(stats.norm.moment(6))}",
        f"Var Z^3 = E Z^6 - (E Z^3)^2 {g(stats.norm.moment(6) - stats.norm.moment(3) ** 2)}",
        f"E X^3 {g(0.05**3 + 3 * 0.05 * 0.04)} (scipy {g(nz.moment(3))})",
        f"E X^4 {g(0.05**4 + 6 * 0.05**2 * 0.04 + 3 * 0.04**2)} (scipy {g(nz.moment(4))})")
    k5 = (0.0625 + 5) / 1.2084
    n5 = int((R <= -0.05 + EPS).sum())
    put("p6", f"k from printed {g(k5)}", f"Cantelli {g(1 / (1 + k5**2) * 100)}%", f"Chebyshev {g(1 / k5**2 * 100)}%",
        f"days R <= -5%: {n5} ({g(n5 / T * 100)}%)", f"unrounded k {g((Rbar + 0.05) / s)}")
    put("p7", f"Chebyshev 1/3^2 {g(100 / 9)}%", f"Cantelli 1/(1+3^2) {g(100 / (1 + 3**2))}%")
    put("lm1", f"ln(1.5e^0.10 - 0.5e^0.20) {g(np.log(1.5 * np.exp(0.10) - 0.5 * np.exp(0.20)))}",
        f"1.5 x 0.10 - 0.5 x 0.20 = {g(1.5 * 0.10 - 0.5 * 0.20)}", "printed in lm01.md:435: 0.0460, 0.0500")
    # P9: Problem 4's trade at its Kelly exposure f* = p/a - q/b = 8 (lm04.md:718), X = 1 + 8R
    f4 = 0.9 / 0.05 - 0.1 / 0.01
    X9 = 1 + f4 * np.array([0.01, -0.05])
    p9 = np.array([0.9, 0.1])
    EX9 = float((p9 * X9).sum())
    put("p9", f"f* = 0.9/0.05 - 0.1/0.01 = {g(f4)}; X in {{{g(X9[0])}, {g(X9[1])}}}, E X {g(EX9)}",
        f"E ln X {g((p9 * np.log(X9)).sum() * 100)}%", f"ln E X {g(np.log(EX9) * 100)}%",
        f"E[1/X] {g((p9 / X9).sum())}", f"1/E X {g(1 / EX9)}",
        f"E sqrt X {g((p9 * np.sqrt(X9)).sum())}", f"sqrt E X {g(np.sqrt(EX9))}")
    mp, sp, skp, kup = 0.1497, 0.2370, 0.19, 5.02
    j2 = sp**2 / (2 * (1 + mp) ** 2)
    j3 = -skp * sp**3 / (3 * (1 + mp) ** 3)
    j4 = kup * sp**4 / (4 * (1 + mp) ** 4)
    put("p10", f"(3.9) printed {g((mp - sp**2 / 2) * 100)}%", f"terms {g(j2 * 100)}, {g(j3 * 100)}, {g(j4 * 100)}",
        f"sum {g((j2 + j3 + j4) * 100)}", f"R_G {g(np.expm1(np.log1p(mp) - (j2 + j3 + j4)) * 100)}%",
        f"(3.9) unrounded {g((ann['mu'] - ann['var'] / 2) * 100)}%")

    # ---- lab extension: the limit regimes
    cut = np.array([d.isoformat() <= "2015-05-29" for d in rdates])
    put("regimes", f"T {int(cut.sum())} (to 2015-05-29)", f"T {int((~cut).sum())} (from 2015-06-01)")

    order = ORDER
    missing = [k for k in VALUES if k not in order]
    unknown = [k for k in order if k not in VALUES]
    if missing or unknown:
        raise SystemExit(f"anchor order mismatch: missing {missing}, unknown {unknown}")
    for i, key in enumerate(order, start=1):
        print(f"A14-{i:02d} {VALUES[key]}")


# anchor keys in the order of their first appearance in the brief: A14-01, A14-02, ...
ORDER: list[str] = [
    "T", "yrs", "A", "ann_mean", "ann_cagr", "y0809", "pair_avg", "pair_two", "Rbar", "RG", "gapRG", "gapdiff",
    "s2h", "s", "die", "pm10", "f2mom", "x6", "J", "f2drag", "x3", "e1_X", "m2", "lm0050", "x5", "n4", "x7",
    "terms", "ann_sd", "ann_drag", "wid", "x8_hm", "lm4coin", "e1_Ehalf", "e1_lnEX", "e1_q", "F0", "pos", "med",
    "above", "e1_EX", "e1_half", "rbar_bp", "Ar", "Gfull", "bet", "skew", "kurt", "m3", "nm3", "m4", "ratio4",
    "nm4", "musig", "approx", "absR", "mk1", "mk2", "n3abs", "cant3", "n3", "c17", "phi4", "nd4", "th4", "r92",
    "n4two", "amgm", "pair_amgm", "lognorm", "four", "p2", "pareto", "p4", "p5", "p6", "p7", "lm1", "p9", "p10",
    "regimes", "lm5A", "wid_unr",
]

if __name__ == "__main__":
    main()
