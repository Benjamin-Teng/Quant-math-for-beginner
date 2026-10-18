"""LM17 anchors (Law of Large Numbers and Central Limit Theorem): every number the Stage 1 brief quotes.

Reads TR23 from data/processed/vol3_taiex.parquet (columns date, tr, price, R, Rp; R is the total-return index's
simple daily return, null on the first row; built and checked by data/vol3_series.py, which must be run first).

Conventions: T = 5,849 returns from 2003-01-03; log returns r = ln(1 + R); moments with divisor T; years = calendar
days between the first and last close / 365.25; A = T / years; a model horizon of tau years is m = round(A * tau)
whole sessions. Counts against a threshold use the book's guard (R > 1e-12 for an up day) and are checked exactly
with Fraction on the two-decimal closes. LM17 simulates nothing, so no random generator is created. Numbers printed
by earlier modules are echoed as printed (file:line in plans/vol-3-anchors.md); numbers owned by LM14 and LM15 are
recomputed here.

Prints one line per anchor, "A17-NN <value>", in ID order, and writes nothing.

Run:  PYTHONUTF8=1 uv run python data/vol3_anchors_lm17.py [repository root]
"""
import sys
from fractions import Fraction
from math import comb, exp, log, sqrt
from pathlib import Path

import numpy as np
import polars as pl
from scipy import optimize, stats

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
EPS = 1e-12
LIMIT_SWITCH = "2015-06-01"
Z95 = float(stats.norm.ppf(0.95))

OUT: list[str] = []


def put(value: str) -> None:
    OUT.append(f"A17-{len(OUT) + 1:02d} {value}")


def kurt_ex(x: np.ndarray) -> float:
    """Excess kurtosis with divisor-n moments (scipy.stats.kurtosis defaults)."""
    xc = x - x.mean()
    return float((xc**4).mean() / (xc**2).mean() ** 2 - 3)


def corr(a: np.ndarray, b: np.ndarray) -> float:
    a = a - a.mean()
    b = b - b.mean()
    return float((a * b).mean() / sqrt(float((a * a).mean() * (b * b).mean())))


def overlap(x: np.ndarray, m: int) -> np.ndarray:
    """All len(x) - m + 1 overlapping m-day sums."""
    c = np.concatenate([[0.0], np.cumsum(x)])
    return c[m:] - c[:-m]


# ---------------------------------------------------------------- data
df = pl.read_parquet(PROC / "vol3_taiex.parquet").sort("date")
dates_all = [str(d) for d in df["date"].to_list()]
tr = df["tr"].to_numpy()
R = df["R"].to_numpy()[1:]
dates = dates_all[1:]
assert df["R"][0] is None and len(set(dates_all)) == len(dates_all)
T = len(R)
r = np.log1p(R)
days = (df["date"][-1] - df["date"][0]).days
years = days / 365.25
A = T / years
Rb, s = float(R.mean()), float(R.std())
rb, sr = float(r.mean()), float(r.std())
G = float(tr[-1] / tr[0])

trf = [Fraction(str(x)) for x in tr]
RF = [trf[i] / trf[i - 1] - 1 for i in range(1, len(trf))]
up_x, dn_x, zero_x = sum(x > 0 for x in RF), sum(x < 0 for x in RF), sum(x == 0 for x in RF)
up_g = int((R > EPS).sum())
assert up_g == up_x and int((R < -EPS).sum()) == dn_x


def gbar(f: float) -> float:
    return float(np.log1p(f * R).mean())


def sdl(f: float) -> float:
    return float(np.log1p(f * R).std())


def gbar_d(f: float) -> float:
    return float((R / (1 + f * R)).mean())


i_min = int(R.argmin())
fmax = 1 / abs(float(R[i_min]))
fstar = float(optimize.brentq(gbar_d, 0.0, fmax - 1e-6))
fzero = float(optimize.brentq(gbar, fstar, fmax - 1e-9))
delta = log(1 + Rb) - rb


def pr_above(m: int, f: float = 1.0) -> tuple[float, float]:
    d = log(1 + f * Rb) - gbar(f)
    z = sqrt(m) * d / sdl(f)
    return z, float(stats.norm.sf(z))


def row(m: int) -> tuple[float, ...]:
    med = exp(m * rb)
    lo = exp(m * rb - Z95 * sr * sqrt(m))
    hi = exp(m * rb + Z95 * sr * sqrt(m))
    p_loss = float(stats.norm.cdf(-rb * sqrt(m) / sr))
    return med, (1 + Rb) ** m, lo, hi, p_loss, pr_above(m)[1]


m1, m5, m10, m40 = round(A), round(5 * A), round(10 * A), round(40 * A)

# ---------------------------------------------------------------- data role, notation, case
put(f"{len(dates_all)}")                                                       # 01 closes
put(f"{T}")                                                                    # 02 T
put(f"{days}")                                                                 # 03 days
put(f"{years:.6f}")                                                            # 04 years
put(f"{A:.6f}")                                                                # 05 A
put(f"up {up_x}; down {dn_x}; zero {zero_x} (guard count {up_g})")             # 06 signs
put(f"{m5} (5A = {5 * A:.4f})")                                                # 07 five years
put(f"{G:.4f}")                                                                # 08 G
put(f"{Rb:.10%}")                                                              # 09 R bar
put(f"from 0.06251%: {1.0006251**T:.4f}; unrounded: {(1 + Rb) ** T:.4f}")     # 10 mean path
put(f"from 0.06251%: {(1 + 4 * 0.0006251) ** T:.6g}; unrounded: {(1 + 4 * Rb) ** T:.6g}")  # 11
put(f"f* {fstar:.6f}; exp(T gbar(f*)) {exp(T * gbar(fstar)):.2f}")             # 12
put(f"{fzero:.6f}")                                                            # 13 zero growth
put(f"{1.000625**T:.4f}")                                                      # 14 0.0625%
put(f"{1e4 * delta:.5f} bp")                                                   # 15 daily gap (LM14 E10)
put(f"T*delta {T * delta:.5f}; exp {exp(T * delta):.5f}")                      # 16
z1, p1 = pr_above(T)
zs, ps = pr_above(T, fstar)
put(f"f=1: {p1:.5f}; f*: {ps:.5f}")                                            # 17
# ---------------------------------------------------------------- sections
put("averages 2%, 0.5%, 0.5%, -1%; mean 0.5%; variance "
    f"{np.var([2.0, 0.5, 0.5, -1.0]):.4f} %^2; one trade {np.var([2.0, -1.0]):.4f} %^2")  # 18


def coin_tail(n: int) -> float:
    """Exact Pr(|j/n - 1/2| >= 0.1) for Bin(n, 1/2), compared in integers: |10j - 5n| >= n."""
    return float(Fraction(sum(comb(n, j) for j in range(n + 1) if abs(10 * j - 5 * n) >= n), 2**n))


put("; ".join(f"n={n}: {coin_tail(n):.6g} vs {25 / n:g}" for n in (10, 100, 1000)))  # 19
put("1.2130; 1.2358 (printed in lm05.md:521)")                                 # 20
put("5.84 -> 7.63 (lm05.md:367); 62.8%; 14.1% (lm05.md:369)")                  # 21
xc = R - Rb
top = np.argsort(-(xc**4))[:10]
put(f"{(xc[top] ** 4).sum() / (xc**4).sum():.4%}; {(xc[top] ** 2).sum() / (xc**2).sum():.4%}")  # 22
# ---------------------------------------------------------------- knowledge checks
put(f"{1.2 / sqrt(4):.1f}%; {1.2:.1f}%")                                       # 23
put(f"{sqrt(100) / 2:g}, {sqrt(10000) / 2:g}; {0.5 / sqrt(100):g}, {0.5 / sqrt(10000):g}")  # 24
put(f"{1.005**1000:.4f}; {exp(1000 * 0.0048761):.4f}")                         # 25
put(f"{0.5 * log(1.02) + 0.5 * log(0.99):.7%} (printed 0.48761%, lm03.md:363)")  # 26
put(f"exact {float(stats.binom.sf(59, 100, 0.5)):.6f}; cc {float(stats.norm.sf(1.9)):.6f}")  # 27
put(f"gbar(2) {gbar(2):.6%}; s_r(2) {sdl(2):.5%}")                             # 28
put(f"{m1} (A = {A:.4f})")                                                     # 29
z2 = gbar(2) * sqrt(m1) / sdl(2)
z2p = 0.00095571 * sqrt(m1) / 0.024288
put(f"z {z2:.5f}, Pr {float(stats.norm.cdf(-z2)):.5f}; printed inputs z {z2p:.5f}, Pr {float(stats.norm.cdf(-z2p)):.5f}")  # 30
put(f"{row(m1)[4]:.6f}")                                                       # 31
put(f"{kurt_ex(r):.5f}")                                                       # 32
put(f"{next(m for m in range(1, 100) if 5.428 / m < 0.5)}")                    # 33
put(f"{kurt_ex(overlap(r, 10)):.4f}")                                          # 34
n2 = dates.index("2025-04-02") + 1
n7 = dates.index("2025-04-07") + 1
put(f"{kurt_ex(R[:n2]):.4f} ({n2} returns) -> {kurt_ex(R[:n7]):.4f} ({n7} returns)")  # 35
# ---------------------------------------------------------------- exhibits
put(f"{G:.4f}; {(1 + Rb) ** T:.4f}; {exp(T * rb):.4f}")                        # 36 X1
put(f"0.062505%: {1.00062505**T:.4f}; 0.06251%: {1.0006251**T:.4f}")           # 37
run = np.cumsum(R > EPS) / np.arange(1, T + 1)
put("; ".join(f"n={n}: {run[n - 1]:.5f}" for n in (246, m5, T)))              # 38
p_hat = up_x / T
put(f"{2 * sqrt(p_hat * (1 - p_hat) / T):.6f}")                               # 39
n_rounds = 10
ew10 = 1.25**n_rounds
contrib = sum(Fraction(comb(n_rounds, j), 2**n_rounds) * Fraction(2) ** (2 * j - n_rounds) for j in range(7, 11))
put(f"paths {2**n_rounds}; E W10 {ew10:.5f}; Pr(j>=7) {Fraction(sum(comb(10, j) for j in range(7, 11)), 1024)}"
    f" = {176 / 1024:.6f}; contribution {float(contrib):.4f} = {float(contrib) / ew10:.4%}")  # 40
put(f"A gbar(1) {A * gbar(1):.4%}; A ln(1+Rbar) {A * log(1 + Rb):.4%}; f* {fstar:.4f}, "
    f"A gbar(f*) {A * gbar(fstar):.4%}; zero growth {fzero:.4f}")              # 41
put(f"1/abs(R_min) {fmax:.4f}; R_min {R[i_min]:.4%} on {dates[i_min]}")           # 42
put("f* = 25, g* = 5.889% (printed in lm04.md:345)")                           # 43
gs = 0.5 * log(1.5) + 0.5 * log(0.75)
sg = log(2) / 2
thr = log(4 / 3) / log(2)


def coin(n: int) -> tuple[float, float, float, float]:
    jmax = int(np.ceil(thr * n)) - 1
    z = -gs * sqrt(n) / sg
    return (float(stats.binom.cdf(jmax, n, 0.5)), float(stats.norm.cdf(z)),
            float(stats.norm.cdf((jmax + 0.5 - n / 2) / (sqrt(n) / 2))), z)


c100 = coin(100)
put(f"exact {c100[0]:.6f}; normal {c100[1]:.7f}; cc {c100[2]:.6f}")            # 44
put(f"{m10} (10A = {10 * A:.4f})")                                             # 45
put(f"{Z95:.6f}")                                                              # 46
fmt_row = "median {:.5f}; mean path {:.5f}; 5% {:.5f}; 95% {:.5f}; Pr(W<W0) {:.6f}; Pr(W>EW) {:.5f}"
put(fmt_row.format(*row(m1)))                                                  # 47
put(fmt_row.format(*row(m10)))                                                 # 48
put(fmt_row.format(*row(T)))                                                   # 49
year_end: dict[str, int] = {}
for i, d in enumerate(dates_all):
    year_end[d[:4]] = i
losses = []
for y in range(2003, 2026):
    base = 0 if y == 2003 else year_end[str(y - 1)]
    ret = trf[year_end[str(y)]] / trf[base] - 1
    if ret < 0:
        losses.append(f"{y} {float(ret):.2%}")
put(f"{len(losses)} of 23: " + ", ".join(losses))                               # 50
put(f"23 x {row(m1)[4]:.6f} = {23 * row(m1)[4]:.4f}; 23 x 0.2374 = {23 * 0.2374:.4f}")  # 51
gp, sp = 0.00055170, 0.012107
qs = (exp(m10 * gp - 1.645 * sp * sqrt(m10)), exp(T * gp - 1.645 * sp * sqrt(T)), exp(T * gp + 1.645 * sp * sqrt(T)))
put(f"rbar {rb:.6%}, s_r {sr:.5%}; from 0.055170%, 1.2107%, 1.645: ten-year 5% {qs[0]:.4f}, "
    f"sample 5% {qs[1]:.4f}, sample 95% {qs[2]:.2f}")                         # 52
ms = (1, 2, 5, 10, 20, 60)
put(", ".join(f"m={m}: {kurt_ex(overlap(r, m)):.5f}" for m in ms))              # 53
put(", ".join(f"{5.428 / m:.4f}" for m in ms) + f"; 5.43/2 = {5.43 / 2:.4f}")  # 54
put(f"{kurt_ex(R):.4f}")                                                       # 55
nw = T // 20
k_first = kurt_ex(r[: nw * 20].reshape(nw, 20).sum(axis=1))
k_off = [kurt_ex(r[o : o + (T - o) // 20 * 20].reshape(-1, 20).sum(axis=1)) for o in range(20)]
put(f"first return {k_first:.4f} ({nw} windows); offsets 0-19 {min(k_off):.4f} to {max(k_off):.4f}")  # 56
pre = np.array([d < LIMIT_SWITCH for d in dates])
reg = []
for lab, x in (("before", r[pre]), ("from", r[~pre])):
    reg.append(f"{lab} 2015-06-01 ({len(x)}): daily {kurt_ex(x):.4f}, 20-day {kurt_ex(overlap(x, 20)):.4f}")
put("; ".join(reg) + f"; iid 3.44/20 = {3.44 / 20:.4f}, 8.41/20 = {8.41 / 20:.4f}")  # 57
n_ = np.arange(1, T + 1)
va = A * (np.cumsum(R**2) / n_ - (np.cumsum(R) / n_) ** 2)
lo_i, hi_i = 245 + int(va[245:].argmin()), 245 + int(va[245:].argmax())
put(f"min {va[lo_i]:.6f} ({dates[lo_i]}); max {va[hi_i]:.6f} ({dates[hi_i]}); end {va[-1]:.6f}")  # 58
# ---------------------------------------------------------------- widget
put(f"{m40} (40A = {40 * A:.4f})")                                             # 59
put(f"{float(stats.norm.cdf(-rb * sqrt(m5) / sr)):.6f}")                       # 60
put(f"f=1: {gbar(1):.8f}, {sdl(1):.8f}; f=2: {gbar(2):.8f}, {sdl(2):.8f}")    # 61
put(f"f=1: lognormal {exp(T * (gbar(1) + sdl(1) ** 2 / 2)):.4f}, iid {(1 + Rb) ** T:.4f}; "
    f"f=8: lognormal {exp(T * (gbar(8) + sdl(8) ** 2 / 2)):.4e}, iid {(1 + 8 * Rb) ** T:.4e}")  # 62
# ---------------------------------------------------------------- examples
put(f"{1.5 / sqrt(100):g}%, {1.5 / sqrt(10000):g}%; n = {int(np.ceil((1.5 / 0.25) ** 2))}; edge 0.5% (lm03.md:363)")  # 63
put(f"{0.25 / (0.01**2 * 0.05):.0f}")                                          # 64
put(f"E W10 {ew10:.5f}; Pr(W=1) {Fraction(comb(10, 5), 1024)} = {comb(10, 5) / 1024:.4f}; Pr(W>EW) 11/64 = "
    f"{11 / 64:.4f}; share {float(contrib) / ew10:.4%}; Pr(W<1) {Fraction(sum(comb(10, j) for j in range(5)), 1024)}"
    f" = {sum(comb(10, j) for j in range(5)) / 1024:.4f}")                     # 65
j100 = int(np.floor((100 * log(1.25) / log(2) + 100) / 2)) + 1
put(f"E W {1.25**100:.4e}; Pr(j>={j100}) {float(stats.binom.sf(j100 - 1, 100, 0.5)):.4e}; "
    f"Pr(j<=49) {float(stats.binom.cdf(49, 100, 0.5)):.4f}")                  # 66
put(f"1.05; {0.5 * log(0.9):.5f}; {sqrt(0.9):.5f}")                            # 67
put(f"Rbar {Rb:.8%}, rbar {rb:.8%}; gap from 7 s.f. {1e4 * (log(1.0006250506) - 0.0005516962):.5f} bp; "
    f"from 0.062505%, 0.055170%: {1e4 * (log(1.00062505) - 0.00055170):.5f} bp")  # 68
need = (Z95 * sr / delta) ** 2
need_p = (1.645 * 0.012107 / 0.7316e-4) ** 2
put(f"{need:.0f} days = {need / A:.2f} years; from 1.645, 1.2107%, 0.7316 bp: {need_p:.0f} days = {need_p / 246.12:.2f} years")  # 69
put(f"{sr**2 / (T * delta**2):.4f}; from printed {0.012107**2 / (T * 0.7316e-4**2):.4f}")  # 70
lev = []
for f in (1, 2, 4, 6, 8):
    w = exp(T * gbar(f))
    lev.append(f"f={f}: W {w:.6g}, A gbar {A * gbar(f):.4%} (ln of printed W / years "
               f"{log(float(f'{w:.4g}')) / years:.4%}), mean path {(1 + f * Rb) ** T:.4e}"
               f" (from 0.062505% {(1 + f * 0.00062505) ** T:.4e})")
put("; ".join(lev))                                                            # 71
w_star = exp(T * gbar(fstar))
put(f"f* {fstar:.6f}; A gbar(f*) {A * gbar(fstar):.4%}; W {w_star:.2f}; /G {w_star / G:.3f}; "
    f"zero growth {fzero:.6f}; /f* {fzero / fstar:.4f}")                      # 72
d_star = log(1 + fstar * Rb) - gbar(fstar)
put(f"delta(f*) {1e4 * d_star:.4f} bp; s_r(f*) {sdl(fstar):.5%}; z {zs:.5f}; Pr {ps:.5f}")  # 73
w = np.concatenate([[1.0], np.exp(np.cumsum(np.log1p(fstar * R)))])
dd = 1 - w / np.maximum.accumulate(w)
put(f"{dd.max():.4%} at {dates_all[int(dd.argmax())]}")                       # 74
put(f"{thr:.7f} (printed 0.41504, lm04.md:366)")                               # 75
c10 = coin(10)
put(f"g* {gs:.7f}; sigma {sg:.7f}; z {c100[3]:.6f}; n=100 exact {c100[0]:.6f}, normal {c100[1]:.7f}, "
    f"cc {c100[2]:.6f}; normal minus 0.0446355 {c100[1] - 0.0446355:.2e}; n=10 exact {c10[0]:.6f}, "
    f"normal {c10[1]:.6f}, cc {c10[2]:.6f}")                                   # 76
put(f"{1.96**2 * 0.25 / 0.01**2:.2f}")                                         # 77
put("1.96 (printed in lm04.md:541)")                                           # 78
put(f"one year z {rb * sqrt(m1) / sr:.5f}; ten years z {rb * sqrt(m10) / sr:.5f}; "
    f"from printed inputs {gp * sqrt(m1) / sp:.5f}, {gp * sqrt(m10) / sp:.5f}")  # 79
ann = []
for y in range(2003, 2026):
    base = 0 if y == 2003 else year_end[str(y - 1)]
    ann.append(log(float(trf[year_end[str(y)]] / trf[base])))
la = np.array(ann)
put(f"annual log returns mean {la.mean():.5f}, sd {la.std():.5f}; Pr(G<1) {float(stats.norm.cdf(-la.mean() / la.std())):.5f}; "
    f"s_r sqrt(246) {sr * sqrt(m1):.5f}")                                     # 80
ar = np.abs(r)
put(f"r lag 1 {corr(r[:-1], r[1:]):.4f}; abs(r) lag 1 {corr(ar[:-1], ar[1:]):.4f}; abs(r) lag 20 {corr(ar[:-20], ar[20:]):.4f}")  # 81
put(", ".join(f"n={n}: {2 * float(stats.norm.sf(sqrt(n))):.4g}" for n in (1, 4, 25)))  # 82
# ---------------------------------------------------------------- problems, lab, pitfalls
put(f"{1.2 / sqrt(400):g}%; {1.2 / 400:g}%; {1.2 * sqrt(400):g}%")             # 83
put(f"{2 * float(stats.norm.sf(0.02 / (0.5 / sqrt(2500)))):.4f}; {sqrt(0.25) / (sqrt(2500) * 0.02):g}; "
    f"{0.25 / (2500 * 0.02**2):g}")                                            # 84
put(f"E W4 {1.25**4:.4f}; Pr(j=4) 1/16; Pr(j>=3) 5/16; Pr(j>=2) 11/16")        # 85
put(f"{5.43 / sqrt(20):.4f}; {5.43 / 20:.4f}")                                 # 86
c400 = coin(400)
put(f"exact {c400[0]:.6f}; z {c400[3]:.4f}, normal {c400[1]:.6f}; cc {c400[2]:.6f}; "
    f"relative errors n=400 {c400[1] / c400[0] - 1:+.2%}, n=100 {c100[1] / c100[0] - 1:+.2%}")  # 87
put(f"{1e4 * (log(1 + 2 * Rb) - gbar(2)):.4f} bp")                              # 88
zp8 = sqrt(T) * 2.936e-4 / 0.024288
put(f"bound {0.024288**2 / (T * 2.936e-4**2):.4f}; z {zp8:.4f}; Pr {float(stats.norm.sf(zp8)):.4f}")  # 89
put(f"{float(stats.binom.stats(20, 0.5, moments='k')):.4f}")                   # 90
rm = A * np.cumsum(r) / n_
lo_r = 245 + int(rm[245:].argmin())
put(f"n=246 {rm[245]:.4%}; min {rm[lo_r]:.4%} ({dates[lo_r]}); end {rm[-1]:.4%}")  # 91
put(f"{sr * sqrt(T):.6f}; exp {exp(sr * sqrt(T)):.4f}")                         # 92

print("\n".join(OUT))
