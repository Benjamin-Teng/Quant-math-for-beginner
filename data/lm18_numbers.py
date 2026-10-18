"""Every number that LM18 (Monte Carlo Simulation and the Bootstrap) quotes, computed and checked against src/lm18.md.

Run:  uv run python data/lm18_numbers.py      (after data/vol3_series.py)

Inputs (data/lm18_common.py): data/processed/vol3_taiex.parquet (TR23, the TAIEX total-return index), LM12's printed
S5 Cholesky factor and LM5's printed Simpson errors (model parameters typed from those modules), src/lm18.md (the
text the checks compare against).

Checks, each of which stops the script on a mismatch:
  chk(label, value, fmt, printed)  format(value, fmt) must equal `printed`, the string must appear in src/lm18.md as
                                   a whole number, and the value must not sit on a rounding tie of fmt (a reader
                                   rounding by hand could get the other last digit). Hand results are recomputed
                                   from the inputs printed next to them (project/PITFALLS.md section 7).
  has(label, printed)              a literal string (a date, a word, a code line) appears in the text.
  anchor(label, got, expected)     compares with plans/vol-3-anchors.md (LM18 rows); a difference is reported at the
                                   end, not forced.
Simulations follow AUTHORING section 8 (np.random.default_rng([e, 20261011]), e the experiment's number in the text)
and re-run under the NumPy that uv.lock pins; the script asserts that chunked draws equal one call.
It ends by printing "all N checks passed".
"""
import math
import re
from fractions import Fraction

import numpy as np
from lm18_common import (
    CH,
    EPS,
    KK,
    L_PRINTED,
    P_LM5,
    ROOT,
    SEED,
    SIMPSON_LM5,
    X3_SIZES,
    bse,
    lag1,
    load,
    q_inv,
    rng,
    sd_se,
    se,
    x3_runs,
    x7_resamples,
)
from scipy import integrate, stats

MD = ROOT / "src" / "lm18.md"
TEXT = MD.read_text(encoding="utf-8")
NORM = TEXT.replace("{,}", ",").replace("−", "-").replace("\\%", "%")
N_CHECKS = 0
ANCHOR_DIFFS: list[str] = []
COVERED: set[str] = set()


def in_text(printed: str) -> bool:
    """The printed number appears as a whole number (not inside a longer one: 2.15 is not in 2.153)."""
    return re.search(r"(?<![\d.])" + re.escape(printed) + r"(?![\d])", NORM) is not None


def tie(value: float, fmt: str) -> bool:
    """True when value lies on a rounding boundary of fmt."""
    m = re.search(r"\.(\d+)", fmt)
    d = int(m.group(1)) if m else 0
    a = abs(value)
    if "e" in fmt and a > 0:
        a = a / 10 ** math.floor(math.log10(a))
    scaled = a * 10**d
    return abs(scaled - math.floor(scaled) - 0.5) < 1e-6


def chk(label: str, value: float, fmt: str, printed: str) -> None:
    global N_CHECKS
    got = format(value, fmt)
    print(f"CHECK {label}: {got} (printed {printed}) {'ok' if got == printed else 'MISMATCH'}")
    assert got == printed, (label, got, printed)
    assert not tie(value, fmt), ("rounding tie: print more digits", label, value)
    assert in_text(printed), f"{label}: {printed!r} not found in src/lm18.md"
    COVERED.add(printed)
    N_CHECKS += 1


def has(label: str, printed: str) -> None:
    global N_CHECKS
    assert printed in NORM, f"{label}: {printed!r} not found in src/lm18.md"
    print(f"CHECK {label}: '{printed[:60]}' in text ok")
    COVERED.add(printed)
    N_CHECKS += 1


def anchor(label: str, got: str, expected: str) -> None:
    tag = "ok" if got == expected else "DIFFERS"
    print(f"ANCHOR {label}: {got} (anchor {expected}) {tag}")
    if got != expected:
        ANCHOR_DIFFS.append(f"{label}: script {got}, anchor {expected}")


def pct(x: float) -> float:
    return 100 * x


# ====================================================================== TR23 (notation note, case)
d = load()
R, r, T, P, dates, m = d.R, d.r, d.T, d.P, d.dates, d.m
assert (T, dates[0], dates[1], dates[-1]) == (5849, "2003-01-02", "2003-01-03", "2026-10-08")
anchor("A18-03 T", f"{P.size} closes, T = {T}", "5850 closes, T = 5849")
anchor("A18-04", f"{d.days} days; {d.years:.6f} years; A = {d.A:.6f}", "8680 days; 23.764545 years; A = 246.122955")
anchor("A18-06", f"5A = {5 * d.A:.4f}; m = {m}", "5A = 1230.6148; m = 1231")
has("T", "5,849")
chk("years", d.years, ".4f", "23.7645")
chk("A", d.A, ".2f", "246.12")
chk("m = round(5A)", float(m), ",.0f", "1,231")
has("sample dates", "2 January 2003 → 8 October 2026")
has("first return", "3 January 2003")
Rbar, s = float(R.mean()), float(R.std())
rbar, sr = float(r.mean()), float(r.std())
anchor("A18-47", f"Rbar = {pct(Rbar):.7f}%; s = {pct(s):.6f}%", "Rbar = 0.0625051%; s = 1.208364%")
anchor("A18-44", f"rbar = {pct(rbar):.7f}%; s_r = {pct(sr):.6f}%", "rbar = 0.0551696%; s_r = 1.210727%")
chk("Rbar %", pct(Rbar), ".6f", "0.062505")
chk("s %", pct(s), ".4f", "1.2084")
chk("rbar %", pct(rbar), ".5f", "0.05517")
chk("s_r %", pct(sr), ".4f", "1.2107")

# threshold counts with the guard and exactly
Rq = [d.Pq[i + 1] / d.Pq[i] - 1 for i in range(T)]
down5 = R <= -0.05 + EPS
big = (R >= 0.03 - EPS) | (R <= -0.03 + EPS)
assert int(down5.sum()) == sum(1 for x in Rq if x <= Fraction(-5, 100))
assert int(big.sum()) == sum(1 for x in Rq if abs(x) >= Fraction(3, 100))
anchor("A18-05", f"R <= -5%: {int(down5.sum())}; abs(R) >= 3%: {int(big.sum())}", "R <= -5%: 15; abs(R) >= 3%: 175")
chk("days with |R| >= 3%", float(big.sum()), ".0f", "175")
chk("days at or below -5%", float(down5.sum()), ".0f", "15")
iw = int(R.argmin())
assert dates[1 + iw] == "2025-04-07"
chk("worst day %", pct(float(R[iw])), ".4f", "-9.6997")
chk("worst day % (zh, two decimals)", pct(float(R[iw])), ".2f", "-9.70")
has("worst day date", "7 April 2025 (-9.6997%)")
before = sum(1 for x in dates[1:] if x < "2015-06-01")
chk("returns before 2015-06-01", float(before), ",.0f", "3,077")
chk("returns from 2015-06-01", float(T - before), ",.0f", "2,772")
anchor("A18-66", f"{before}; {T - before}", "3077; 2772")

# ====================================================================== the case: five-year windows (exhibit windows)
nwin = P.size - m
Gw = P[m:] / P[:-m]
uw = np.flatnonzero(Gw < 1)
assert uw.size == sum(1 for i in range(nwin) if d.Pq[i + m] < d.Pq[i])
anchor("A18-07", f"{nwin} windows; {uw.size} under water; {pct(uw.size / nwin):.4f}%",
       "4619 windows; 191 under water; 4.1351%")
chk("windows", float(nwin), ",.0f", "4,619")
chk("windows under water", float(uw.size), ".0f", "191")
chk("share under water %", pct(uw.size / nwin), ".1f", "4.1")
assert dates[nwin - 1] == "2021-09-10"
has("last window start", "2 January 2003 → 10 September 2021 (4,619 windows)")
episodes = np.split(uw, np.flatnonzero(np.diff(uw) > 250) + 1)
assert len(episodes) == 2
(e1, e2) = episodes
assert (dates[e1[0]], dates[e1[-1]], dates[e2[0]], dates[e2[-1]]) == ("2003-11-03", "2004-04-21", "2007-06-15",
                                                                      "2007-12-07")
assert (e1[-1] - e1[0] + 1, e1.size, e2[-1] - e2[0] + 1, e2.size) == (116, 111, 122, 80)
has("episode 1", "3 November 2003 → 21 April 2004 (116 starts, 111 under water)")
has("episode 2", "15 June → 7 December 2007 (122, 80)")
has("case: episodes", "between November 2003 and April 2004 or between June and December 2007")
i0, i1 = int(Gw.argmin()), int(Gw.argmax())
assert (dates[i0], dates[i0 + m], dates[i1], dates[i1 + m]) == ("2004-03-09", "2009-02-24", "2021-05-17", "2026-06-09")
chk("worst window", float(Gw[i0]), ".2f", "0.78")
chk("best window", float(Gw[i1]), ".2f", "3.43")
has("worst window dates", "0.78 (2004-03-09 → 2009-02-24)")
has("best window dates", "3.43 (2021-05-17 → 2026-06-09)")
chk("disjoint five-year periods", d.years / 5, ".2f", "4.75")
assert d.years / 5 < 5
qw = q_inv(Gw, [0.05, 0.5, 0.95])
anchor("A18-33", " / ".join(f"{x:.4f}" for x in qw), "1.0227 / 1.6089 / 2.5290")
assert np.allclose(np.round(np.quantile(Gw, [0.05, 0.5, 0.95]), 2), np.round(qw, 2))
has("window quantiles", "1.02 / 1.61 / 2.53")
lw = np.log(Gw)
chk("sd of window ln G", float(lw.std()), ".3f", "0.283")
chk("mean of window ln G", float(lw.mean()), ".3f", "0.502")
chk("m rbar (three decimals)", m * rbar, ".3f", "0.679")

# ====================================================================== the model (E3's formula, X6)
z0 = -math.sqrt(m) * rbar / sr
p_ln = float(stats.norm.cdf(z0))
v = m * sr**2
EG = math.exp(m * (rbar + sr**2 / 2))
anchor("A18-10", f"z = {z0:.6f}; Pr = {p_ln:.6f}", "z = -1.598758; Pr = 0.054937")
chk("model Pr(G<1) %", pct(p_ln), ".2f", "5.49")
chk("model Pr(G<1), four decimals", p_ln, ".4f", "0.0549")
gp, sp = 0.0005517, 0.012107                       # the printed g and sigma_r
zp = -math.sqrt(m) * gp / sp
chk("z from printed g, sigma_r", zp, ".4f", "-1.5988")
chk("Phi(-1.5988) %", pct(float(stats.norm.cdf(-1.5988))), ".2f", "5.49")
chk("E G", EG, ".4f", "2.1584")
chk("E G from printed g, sigma_r", math.exp(m * (gp + sp**2 / 2)), ".4f", "2.1584")
chk("m sigma_r^2", v, ".4f", "0.1804")
chk("m sigma_r^2 from printed", m * sp**2, ".4f", "0.1804")
chk("m g", m * rbar, ".4f", "0.6791")
chk("m g from printed", m * gp, ".4f", "0.6791")
qln = np.exp(m * rbar + math.sqrt(v) * stats.norm.ppf([0.05, 0.5, 0.95]))
anchor("A18-27", " / ".join(f"{x:.4f}" for x in qln), "0.9806 / 1.9722 / 3.9664")
has("model quantiles", "0.98 / 1.97 / 3.97")
chk("sqrt(m) s_r", math.sqrt(v), ".3f", "0.425")
chk("sqrt(m) s_r from printed", math.sqrt(m) * sp, ".3f", "0.425")

# ====================================================================== E1 (experiments 1 and 16): same seed, same answer
n1 = 10_000
hits = [int((rng(e).standard_normal(n1) <= -2).sum()) for e in (1, 1, 16)]
anchor("A18-39", f"{hits[0]}, rerun {hits[1]}; {hits[2]}", "249, rerun 249; 214")
assert hits[0] == hits[1]
chk("E1 hits", float(hits[0]), ".0f", "249")
chk("E1 second stream", float(hits[2]), ".0f", "214")
p2 = float(stats.norm.cdf(-2))
chk("Phi(-2)", p2, ".5f", "0.02275")
chk("expected hits", n1 * p2, ".1f", "227.5")
chk("expected hits from printed Phi(-2)", n1 * 0.02275, ".1f", "227.5")
sdc = math.sqrt(n1 * p2 * (1 - p2))
chk("sd of the count", sdc, ".1f", "14.9")
chk("sd of the count from printed", math.sqrt(n1 * 0.02275 * 0.97725), ".1f", "14.9")
assert max(abs(h - n1 * p2) for h in hits) / sdc < 1.5
has("within 1.5 sd", "within 1.5 standard deviations of 227.5")

# ====================================================================== E2 (experiment 2): inverse transform
u3 = rng(2).random(3)
anchor("A18-40", ", ".join(f"{u:.8f}" for u in u3), "0.13969646, 0.46349849, 0.17408344")
for u, p in zip(u3, ("0.1396965", "0.4634985", "0.1740834"), strict=True):
    chk(f"E2 u {p}", float(u), ".7f", p)
u7 = [round(float(u), 7) for u in u3]
ranks = [math.ceil(T * u) for u in u3]
assert ranks == [math.ceil(T * u) for u in u7] == [818, 2712, 1019]
assert [math.ceil(T * round(float(u), 6)) for u in u3][1] == 2711, "six decimals no longer give another rank"
chk("T u, second", T * 0.4634985, ",.3f", "2,711.003")
for j, p in zip(ranks, ("818", "2,712", "1,019"), strict=True):
    chk(f"rank {p}", float(j), ",.0f", p)
lam = int(big.sum()) / T
chk("lambda", lam, ".5f", "0.02992")
waits = [-math.log(1 - u) / lam for u in u3]
waits_p = [-math.log(1 - u) / 0.02992 for u in u7]
for w, wp, p in zip(waits, waits_p, ("5.03", "20.81", "6.39"), strict=True):
    chk(f"wait {p}", w, ".2f", p)
    chk(f"wait {p} from printed u, lambda", wp, ".2f", p)
chk("mean wait", 1 / lam, ".2f", "33.42")
chk("mean wait from printed lambda", 1 / 0.02992, ".2f", "33.42")
chk("median wait", math.log(2) / lam, ".2f", "23.17")
chk("median wait from printed lambda", math.log(2) / 0.02992, ".2f", "23.17")
Rs = np.sort(R)
for j, p, dt in zip(ranks, ("-0.9468", "+0.0247", "-0.7785"), ("2021-12-14", "2007-02-01", "2005-09-23"), strict=True):
    x = Rs[j - 1]
    assert int((R == x).sum()) == 1
    assert dates[1 + int(np.flatnonzero(R == x)[0])] == dt
    chk(f"R_({j})", pct(float(x)), "+.4f", p)
    has(f"R_({j}) date", f"({dt})")
# KC section 3: u = 0.5
chk("KC3 T u", 0.5 * T, ",.1f", "2,924.5")
j5 = math.ceil(0.5 * T)
chk("KC3 rank", float(j5), ",.0f", "2,925")
chk("KC3 median %", pct(float(Rs[j5 - 1])), "+.4f", "+0.0879")
assert Rs[j5 - 1] == np.median(R)

# ====================================================================== E3 (experiment 3): the case by simulation
g3 = rng(3)
S3 = np.empty(10_000)
for c in range(0, 10_000, CH):
    S3[c:c + CH] = (rbar + sr * g3.standard_normal((CH, m))).sum(axis=1)
Y3 = (S3 < 0).astype(float)
p3, se3 = float(Y3.mean()), se(Y3)
G3 = np.exp(S3)
anchor("A18-11", f"{int(Y3.sum())}; {p3:.6f} +- {se3:.6f}", "530; 0.053000 +- 0.002240")
chk("E3 paths under water", float(Y3.sum()), ".0f", "530")
chk("E3 p hat", p3, ".4f", "0.0530")
chk("E3 SE", se3, ".4f", "0.0022")
chk("E3 SE from printed p hat", math.sqrt(0.0530 * 0.9470 / 1e4), ".4f", "0.0022")
chk("E3 1 - p hat", 1 - p3, ".4f", "0.9470")
chk("E3 interval low %", pct(0.0530 - 1.96 * 0.0022), ".1f", "4.9")
chk("E3 interval high %", pct(0.0530 + 1.96 * 0.0022), ".1f", "5.7")
assert f"{pct(p3 - 1.96 * se3):.1f}" == "4.9" and f"{pct(p3 + 1.96 * se3):.1f}" == "5.7"
assert abs(p3 - p_ln) <= 1.96 * se3
chk("E3 printed %", pct(p3), ".1f", "5.3")
chk("E3 printed +- points", pct(se3), ".1f", "0.2")
has("digits rule", "0.0530\\pm0.0022$ prints as 5.3% ± 0.2 points")
# the printed code of section 8 (rounded inputs) gives the same paths count
rng_c = np.random.default_rng([3, SEED])
lnG_c = np.empty(10_000)
for c in range(0, 10_000, 500):
    zc = rng_c.standard_normal((500, m))
    lnG_c[c:c + 500] = (gp + sp * zc).sum(axis=1)
yc = (lnG_c < 0).astype(float)
assert str(yc.mean()) == "0.053" and str(yc.std() / np.sqrt(yc.size)).startswith("0.00224")
assert str(stats.norm.cdf(-gp * np.sqrt(m) / sp)).startswith("0.0549")
has("code output 1", "# 0.053 0.00224...")
has("code output 2", "# 0.0549...")
# standard_normal in 20 chunks equals one call (asserted, NumPy does not promise it)
g_a, g_b = rng(3), rng(3)
assert np.array_equal(np.concatenate([g_a.standard_normal((CH, m)) for _ in range(20)]),
                      g_b.standard_normal((10_000, m))), "chunked standard_normal differs from one call"
# KC section 4
n_kc =0.0549 * 0.9451 / 1e-6
assert 51_500 < n_kc < 52_500 and 51_500 < p_ln * (1 - p_ln) / 1e-6 < 52_500
has("KC4 about 52,000", "about 52,000 paths")
assert round(n_kc / 1e4) == 5
anchor("A18-15", f"{p_ln * (1 - p_ln) / 1e-6:.0f}; {n_kc:.0f}", "51919; 51886")

# ====================================================================== E4 and X3: LM12's colouring gap, (18.4)
L = L_PRINTED
Sig = L @ L.T
n4 = 4382
sim = np.random.default_rng(SEED).standard_normal((n4, 5)) @ L.T
Ssim = np.cov(sim, rowvar=False, ddof=0)
gap4 = float(np.linalg.norm(Ssim - Sig) / np.linalg.norm(Sig))
anchor("A18-02", f"{gap4:.6f}", "0.025026")
chk("E4 gap", gap4, ".4f", "0.0250")
semi = float(Ssim[0, 0] / Sig[0, 0] - 1)
chk("E4 Semiconductor variance high %", pct(semi), ".2f", "4.18")
chk("E4 sqrt(2/n) %", pct(math.sqrt(2 / n4)), ".2f", "2.14")
assert 1.5 < semi / math.sqrt(2 / n4) < 2.5 and 1.5 < 4.18 / 2.14 < 2.5
has("about two standard errors", "about two standard errors")
F2, tr = float(np.linalg.norm(Sig) ** 2), float(np.trace(Sig))
chk("tr^2 / F^2", tr**2 / F2, ".4f", "2.6509")
cst = math.sqrt(1 + tr**2 / F2)
chk("sqrt(1 + .)", cst, ".3f", "1.911")
chk("sqrt(1 + printed 2.6509)", math.sqrt(1 + 2.6509), ".3f", "1.911")
chk("(18.4) at 4,382", cst / math.sqrt(n4), ".4f", "0.0289")
chk("(18.4) at 4,382 from printed 1.911", 1.911 / math.sqrt(n4), ".4f", "0.0289")
chk("(18.4) at 50,000", cst / math.sqrt(50_000), ".4f", "0.0085")
chk("(18.4) at 50,000 from printed 1.911", 1.911 / math.sqrt(50_000), ".4f", "0.0085")
has("50,000 draws", "0.0085 at 50,000")


def rms_centred(n: int) -> float:
    """Exact RMS relative gap of np.cov(ddof=0) for n iid N(0, Sigma) draws (Wishart moments)."""
    return math.sqrt(((n - 1) / n**2) * (F2 + tr**2) + F2 / n**2) / math.sqrt(F2)


changes = [1 - rms_centred(n) / (cst / math.sqrt(n)) for n in (100, 200, 500, 1000, 4382, 10**5)]
assert all(0 < c < 0.004 for c in changes) and changes == sorted(changes, reverse=True)
has("centring under 0.4%", "under 0.4% for $n\\ge100$")
runs = x3_runs(L)
rms = {n: math.sqrt(float((g**2).mean())) for n, g in runs.items()}
rms_b = {n: bse(lambda a: math.sqrt(float((a**2).mean())), g) for n, g in runs.items()}
anchor("A18-21 RMS", ", ".join(f"{rms[n]:.4f}" for n in X3_SIZES), "0.1889, 0.0872, 0.0614, 0.0301, 0.0195, 0.0084")
anchor("A18-21 batch SE", ", ".join(f"{rms_b[n]:.4f}" for n in X3_SIZES), "0.0050, 0.0020, 0.0015, 0.0007, 0.0004, 0.0002")
chk("X3 RMS at 4,382", rms[4382], ".4f", "0.0301")
chk("X3 batch SE at 4,382", rms_b[4382], ".4f", "0.0007")
rel = max(rms_b[n] / rms[n] for n in X3_SIZES)
assert 2.6 < pct(rel) < 2.7, pct(rel)
has("X3 relative batch SE below 2.7%", "relative standard errors below 2.7%")
below = int((runs[4382] <= gap4).sum())
sh = below / 200
chk("X3 runs at or below 0.0250", float(below), ".0f", "82")
chk("X3 share %", pct(sh), ".0f", "41")
chk("X3 share SE %", pct(math.sqrt(sh * (1 - sh) / 200)), ".0f", "3")
anchor("A18-21 share", f"{below} of 200, {sh:.3f} +- {math.sqrt(sh * (1 - sh) / 200):.3f}", "82 of 200, 0.410 +- 0.035")
has("X3 82 of 200", "82 of 200 runs (41%)")
has("X3 200 runs", "200 runs at each $n$ (experiment 12,")
has("X3 batches", "20 batches of 10 runs")

# ====================================================================== E5 (experiment 5) and X4: against quadrature
pk = float(stats.norm.cdf(-KK))
anchor("A18-01", f"{pk:.7e}; quad {abs(integrate.quad(stats.norm.pdf, -np.inf, -KK)[0] / pk - 1):.1e}",
       "2.0003554e-05; quad 6.7e-11")
chk("Phi(-4.1074386) mantissa", pk * 1e5, ".6f", "2.000355")
z5 = rng(5).standard_normal(1_000_000)
h5 = int((z5 <= -KK).sum())
p5 = h5 / 1e6
se5 = math.sqrt(p5 * (1 - p5) / 1e6)
anchor("A18-24", f"{h5} hits; {p5:.3e} +- {se5:.3e}", "18 hits; 1.800e-05 +- 4.243e-06")
chk("E5 hits", float(h5), ".0f", "18")
chk("E5 expected hits", 1e6 * pk, ".1f", "20.0")
chk("E5 estimate x1e5", p5 * 1e5, ".1f", "1.8")
chk("E5 SE x1e5", se5 * 1e5, ".1f", "0.4")
assert abs(p5 - pk) <= 1.96 * se5
rel_plain = math.sqrt((1 - pk) / pk)
chk("plain relative SE per draw", rel_plain, ".1f", "223.6")
chk("E5 relative SE %", pct(rel_plain / 1e3), ".0f", "22")
n_1pct = (1.96 / 0.01) ** 2 * (1 - pk) / pk
chk("draws for +-1% (x1e9)", n_1pct / 1e9, ".2f", "1.92")
chk("draws for +-1% from printed 223.6 (x1e9)", (1.96 / 0.01) ** 2 * 223.6**2 / 1e9, ".2f", "1.92")
n_simp = (1 / 1.23e-6) ** 2 * (1 - pk) / pk
chk("draws for relative SE 1.23e-6 (x1e16)", n_simp / 1e16, ".1f", "3.3")
chk("same from printed 223.6 (x1e16)", (223.6 / 1.23e-6) ** 2 / 1e16, ".1f", "3.3")
simp_rel = {n + 1: e / P_LM5 for n, e in SIMPSON_LM5.items()}
anchor("A18-22", ", ".join(f"{k}: {v:.4e}" for k, v in simp_rel.items()),
       "9: 4.8441e-01, 17: 6.1489e-02, 33: 4.7342e-03, 65: 3.1144e-04, 129: 1.9697e-05, 257: 1.2348e-06, "
       "513: 7.7486e-08, 1025: 4.8341e-09")
chk("Simpson relative at 9", simp_rel[9], ".3f", "0.484")
chk("Simpson relative at 257 (x1e6)", simp_rel[257] * 1e6, ".2f", "1.23")
chk("Simpson relative at 1,025 (x1e9)", simp_rel[1025] * 1e9, ".2f", "4.83")
has("257 evaluations", "with 257 evaluations of $\\varphi$")
var_is = math.exp(KK**2) * float(stats.norm.cdf(-2 * KK)) - pk**2
chk("IS relative SE per draw", math.sqrt(var_is) / pk, ".3f", "2.153")
chk("IS relative SE per draw (pitfall)", math.sqrt(var_is) / pk, ".2f", "2.15")
anchor("A18-23", f"{rel_plain:.2f}; {math.sqrt(var_is) / pk:.4f}", "223.58; 2.1529")
two_digits = len(str(2**1231))
chk("digits of 2^1231", float(two_digits), ".0f", "371")
# zero hits (pitfall, KC section 5)
chk("expected hits in 10,000", 1e4 * pk, ".1f", "0.2")
chk("(1-p)^10000", (1 - pk) ** 10_000, ".4f", "0.8187")
chk("zero-hit share %", pct((1 - pk) ** 10_000), ".0f", "82")
chk("(1-p)^100000", (1 - pk) ** 100_000, ".3f", "0.135")
chk("expected hits in 1e5", 1e5 * pk, ".1f", "2.0")
assert 6.5 < 1 / (1 - pk) ** 100_000 < 7.5
has("one run in seven", "About one run in seven")

# ====================================================================== E6 (experiment 6): antithetic paths
g6 = rng(6)
Sa, Sb = np.empty(5000), np.empty(5000)
for c in range(0, 5000, CH):
    Z6 = g6.standard_normal((CH, m))
    Sa[c:c + CH] = (rbar + sr * Z6).sum(axis=1)
    Sb[c:c + CH] = (rbar - sr * Z6).sum(axis=1)
pairG = (np.exp(Sa) + np.exp(Sb)) / 2
rho_m = -math.exp(-v)
anchor("A18-29", f"{pairG.mean():.6f} +- {se(pairG):.6f}; rho {rho_m:.4f}; ratio {1 / (1 + rho_m):.4f}",
       "2.155069 +- 0.003969; rho -0.8349; ratio 6.0568")
chk("E6 estimate", float(pairG.mean()), ".3f", "2.155")
chk("E6 SE", se(pairG), ".3f", "0.004")
chk("E3 mean G", float(G3.mean()), ".3f", "2.165")
chk("E3 mean G SE", se(G3), ".3f", "0.010")
chk("E3 mean G SE, four decimals (Problem 5)", se(G3), ".4f", "0.0097")
anchor("A18-28", f"{G3.mean():.6f} +- {se(G3):.6f}", "2.165165 +- 0.009702")
chk("rho- for G", rho_m, ".3f", "-0.835")
chk("rho- for G from printed 0.1804", -math.exp(-0.1804), ".3f", "-0.835")
chk("antithetic factor for G", 1 / (1 + rho_m), ".2f", "6.06")
chk("antithetic factor from printed -0.835", 1 / (1 - 0.835), ".2f", "6.06")
pairI = ((Sa < 0).astype(float) + (Sb < 0).astype(float)) / 2
assert not ((Sa < 0) & (Sb < 0)).any()
rho_i = -p_ln / (1 - p_ln)
anchor("A18-31", f"{pairI.mean():.6f} +- {se(pairI):.6f}; rho {rho_i:.4f}", "0.052800 +- 0.002173; rho -0.0581")
chk("E6 Pr", float(pairI.mean()), ".4f", "0.0528")
chk("E6 Pr SE", se(pairI), ".4f", "0.0022")
chk("rho- for the indicator", rho_i, ".3f", "-0.058")
chk("rho- for the indicator from printed 0.0549", -0.0549 / 0.9451, ".3f", "-0.058")
chk("antithetic factor for the indicator", 1 / (1 + rho_i), ".2f", "1.06")
chk("antithetic factor from printed -0.058", 1 / (1 - 0.058), ".2f", "1.06")
chk("X5 antithetic Pr, three decimals", float(pairI.mean()), ".3f", "0.053")
chk("X5 antithetic Pr SE", se(pairI), ".3f", "0.002")
chk("X5 plain Pr", p3, ".3f", "0.053")
chk("X5 plain Pr SE", se3, ".3f", "0.002")

# ====================================================================== E7: control variate on E3's paths


def slope(y: np.ndarray, x: np.ndarray) -> float:
    c = np.cov(y, x, ddof=0)
    return float(c[0, 1] / c[1, 1])


b7 = slope(G3, S3)
b7_se = bse(slope, G3, S3)
rho_x = math.sqrt(v / (math.exp(v) - 1))
Gc = G3 - b7 * (S3 - m * rbar)
anchor("A18-30", f"beta {b7:.4f} +- {b7_se:.4f}; controlled {Gc.mean():.6f} +- {se(Gc):.6f}; rho {rho_x:.4f}",
       "beta 2.1759 +- 0.0113; controlled 2.160503 +- 0.002841; rho 0.9552")
chk("E7 beta hat", b7, ".2f", "2.18")
chk("E7 beta batch SE", b7_se, ".2f", "0.01")
assert abs(float(np.cov(G3, S3, ddof=0)[0, 1]) / v / G3.mean() - 1) < 0.05   # Cov(G, ln G) = m sigma^2 E G
chk("E7 controlled", float(Gc.mean()), ".3f", "2.161")
chk("E7 controlled SE", se(Gc), ".3f", "0.003")
chk("E7 rho", rho_x, ".3f", "0.955")
chk("E7 rho from printed 0.1804", math.sqrt(0.1804 / (math.exp(0.1804) - 1)), ".3f", "0.955")
chk("E7 factor", 1 / (1 - rho_x**2), ".1f", "11.4")
chk("E7 factor from printed 0.955", 1 / (1 - 0.955**2), ".1f", "11.4")
bi = slope(Y3, S3)
Yc = Y3 - bi * (S3 - m * rbar)
rho_xi = -float(stats.norm.pdf(z0)) / math.sqrt(p_ln * (1 - p_ln))
chk("E7 indicator rho", rho_xi, ".3f", "-0.488")
chk("E7 indicator rho from printed", -float(stats.norm.pdf(1.5988)) / math.sqrt(0.0549 * 0.9451), ".3f", "-0.488")
chk("E7 indicator factor", 1 / (1 - rho_xi**2), ".2f", "1.31")
chk("E7 indicator factor from printed -0.488", 1 / (1 - 0.488**2), ".2f", "1.31")
chk("E7 indicator controlled", float(Yc.mean()), ".4f", "0.0535")
chk("E7 indicator controlled SE", se(Yc), ".4f", "0.0020")
chk("X5 control Pr", float(Yc.mean()), ".3f", "0.054")
chk("X5 control Pr SE", se(Yc), ".3f", "0.002")
anchor("A18-32", f"rho {rho_xi:.4f}; controlled {Yc.mean():.6f} +- {se(Yc):.6f}",
       "rho -0.4878; controlled 0.053534 +- 0.001972")

# ====================================================================== E8 (experiment 8): importance sampling
x8 = -KK + rng(8).standard_normal(10_000)
y8 = (x8 <= -KK) * np.exp(KK * x8 + KK**2 / 2)
p8, se8 = float(y8.mean()), se(y8)
tail8 = int((x8 <= -KK).sum())
anchor("A18-25", f"{tail8}; {p8:.5e} +- {se8:.4e}", "5043; 2.04745e-05 +- 4.3658e-07")
chk("E8 draws in the tail", float(tail8), ",.0f", "5,043")
chk("E8 estimate x1e5", p8 * 1e5, ".3f", "2.047")
chk("E8 SE x1e5", se8 * 1e5, ".3f", "0.044")
chk("E8 relative SE %", pct(se8 / p8), ".1f", "2.1")
chk("E8 relative SE % from printed", pct(0.044 / 2.047), ".1f", "2.1")
assert abs(p8 - pk) <= 1.96 * se8
chk("IS per-draw variance x1e9", var_is * 1e9, ".4f", "1.8546")
chk("plain per-draw variance x1e5", pk * (1 - pk) * 1e5, ".4f", "2.0003")
chk("IS factor", pk * (1 - pk) / var_is, ",.0f", "10,786")
chk("IS factor from printed five digits", 2.0003e-5 / 1.8546e-9, ",.0f", "10,786")
chk("IS factor from three digits", 2.00e-5 / 1.85e-9, ",.0f", "10,811")
chk("plain draws equivalent x1e8", 1e4 * pk * (1 - pk) / var_is / 1e8, ".2f", "1.08")
anchor("A18-26", f"{var_is:.5e}; ratio {pk * (1 - pk) / var_is:.1f}", "1.85457e-09; ratio 10785.9")
shift = [math.sqrt(math.exp(a**2) * float(stats.norm.cdf(-KK - a)) - pk**2) / pk for a in (KK / 2, 2 * KK)]
chk("relative SE per draw at k/2", shift[0], ".2f", "7.76")
chk("relative SE per draw at 2k", shift[1], ".0f", "132")
anchor("A18-64", f"{shift[0]:.4f}; {shift[1]:.2f}", "7.7623; 132.08")
anti_tail = -pk / (1 - pk)
chk("antithetic tail rho x1e5", anti_tail * 1e5, ".1f", "-2.0")
chk("antithetic tail factor", 1 / (1 + anti_tail), ".5f", "1.00002")

# ====================================================================== E9 (experiment 9): bootstrap of the mean day
g9 = rng(9)
means = np.empty(10_000)
for c in range(0, 10_000, CH):
    means[c:c + CH] = R[g9.integers(0, T, size=(CH, T))].mean(axis=1)
sd9 = float(means.std())
ex9 = s / math.sqrt(T)
anchor("A18-48", f"{pct(float(means.mean())):.7f}% +- {pct(se(means)):.7f}%; sd {pct(sd9):.7f}% +- "
       f"{pct(sd_se(means)):.7f}%", "0.0627206% +- 0.0001563%; sd 0.0156299% +- 0.0001105%")
chk("E9 mean of means %", pct(float(means.mean())), ".5f", "0.06272")
chk("E9 SE %", pct(se(means)), ".5f", "0.00016")
chk("E9 sd %", pct(sd9), ".5f", "0.01563")
chk("E9 sd SE %", pct(sd_se(means)), ".5f", "0.00011")
chk("E9 exact s/sqrt(T) %", pct(ex9), ".5f", "0.01580")
chk("E9 exact from printed s", 1.2084 / math.sqrt(T), ".5f", "0.01580")
chk("E9 distance in SE", abs(sd9 - ex9) / sd_se(means), ".1f", "1.5")
chk("E9 distance from printed", (0.01580 - 0.01563) / 0.00011, ".1f", "1.5")
assert f"{pct(float(means.std(ddof=1))):.5f}" == "0.01563"   # (6.6)'s divisor B - 1 changes no printed digit
has("E9 B", "$B=10,000$ resamples of 5,849 days")

# ====================================================================== E10 (experiment 10): the case by bootstrap
g10 = rng(10)
S10, G10 = np.empty(10_000), np.empty(10_000)
for c in range(0, 10_000, CH):
    idx = g10.integers(0, T, size=(CH, m))
    S10[c:c + CH] = r[idx].sum(axis=1)
    G10[c:c + CH] = np.prod(1 + R[idx], axis=1)
Y10 = (S10 < 0).astype(float)
p10, se10 = float(Y10.mean()), se(Y10)
q10 = q_inv(G10, [0.05, 0.5, 0.95])
q10se = [bse(lambda a, u=u: float(q_inv(a, [u])[0]), G10) for u in (0.05, 0.5, 0.95)]
anchor("A18-12", f"{int(Y10.sum())}; {p10:.6f} +- {se10:.6f}; " + " / ".join(f"{x:.4f}" for x in q10) + "; "
       + " / ".join(f"{x:.4f}" for x in q10se), "561; 0.056100 +- 0.002301; 0.9717 / 1.9400 / 3.9445; "
       "0.0079 / 0.0104 / 0.0335")
chk("E10 under water", float(Y10.sum()), ".0f", "561")
chk("E10 p hat", p10, ".4f", "0.0561")
chk("E10 SE", se10, ".4f", "0.0023")
chk("E10 printed %", pct(p10), ".1f", "5.6")
chk("E10 printed points", pct(se10), ".1f", "0.2")
has("bootstrap quantiles", "0.97 / 1.94 / 3.94")
for x, p in zip(q10, ("0.97", "1.94", "3.94"), strict=True):
    assert f"{x:.2f}" == p and not tie(float(x), ".2f")
for x, p in zip(q10se, ("0.008", "0.010", "0.034"), strict=True):
    assert f"{x:.3f}" == p and not tie(x, ".3f"), (x, p)
has("bootstrap quantile SEs", "0.008, 0.010 and 0.034")
has("X6 quantile SEs", "(± 0.008, 0.010, 0.034)")
chk("E10 sd ln G", float(S10.std()), ".3f", "0.424")
chk("E10 sd ln G SE", sd_se(S10), ".3f", "0.003")
dist = (float(S10.mean()) - m * rbar) / se(S10)
chk("E10 mean ln G below m rbar, in SE", -dist, ".1f", "2.4")
assert (1.9722 - 1.9400) / 0.0104 > 2.5
has("several standard errors", "several standard errors below 1.97")
EGb = (1 + Rbar) ** m
chk("(1+Rbar)^m", EGb, ".4f", "2.1580")
chk("(1+Rbar)^m from printed 0.062505%", 1.00062505**m, ".4f", "2.1580")
assert f"{1.000625**m:.4f}" == "2.1579"                       # why the text prints 0.062505%
has("(18.9) printed", "1.00062505^{1231}=2.1580")
chk("E10 mean G", float(G10.mean()), ".3f", "2.136")
chk("E10 mean G SE", se(G10), ".3f", "0.009")
chk("E10 interval low from printed", 2.136 - 1.96 * 0.009, ".3f", "2.118")
chk("E10 interval high from printed", 2.136 + 1.96 * 0.009, ".3f", "2.154")
assert not (float(G10.mean()) - 1.96 * se(G10) <= EGb <= float(G10.mean()) + 1.96 * se(G10))
C10 = np.cov(G10, S10, ddof=0)
Gc10 = G10 - C10[0, 1] / C10[1, 1] * (S10 - m * rbar)
chk("E10 controlled", float(Gc10.mean()), ".3f", "2.158")
chk("E10 controlled SE", se(Gc10), ".3f", "0.003")
anchor("A18-49", f"{EGb:.6f}; {G10.mean():.6f} +- {se(G10):.6f}; controlled {Gc10.mean():.6f} +- {se(Gc10):.6f}",
       "2.158033; 2.136106 +- 0.009483; controlled 2.157598 +- 0.002762")
# Problem 12's printed code (concatenated chunks; one call of 10,000 rows gives identical indices)
g12a = np.random.default_rng([10, 20261011])
idx12 = np.concatenate([g12a.integers(0, T, size=(500, m)) for _ in range(20)])
one = np.random.default_rng([10, 20261011])
assert bool((idx12 == one.integers(0, T, size=(10_000, m))).all()), "chunked integers differ from one call"
G12 = np.prod(1 + R[idx12], axis=1)
y12 = (G12 < 1).astype(float)
assert np.array_equal(y12, (r[idx12].sum(axis=1) < 0).astype(float))   # G < 1 and ln G < 0 agree here
assert str(y12.mean()) == "0.0561" and str(y12.std() / 100).startswith("0.0023")
assert str(G12.mean()).startswith("2.136") and str(G12.std() / 100).startswith("0.0094")
has("P12 code output 1", "# 0.0561 0.0023...")
has("P12 code output 2", "# 2.136... 0.0094...")
del idx12
mem = 10_000 * m * 8 / 1e6
chk("memory MB", mem, ".1f", "98.5")
chk("chunk memory MB", 500 * m * 8 / 1e6, ".1f", "4.9")
anchor("A18-19", f"{mem:.2f} MB", "98.48 MB")

# ====================================================================== X6 and the knowledge check of section 7
chk("X6 windows %", pct(uw.size / nwin), ".1f", "4.1")
chk("KC7 absent", (1 - 1 / T) ** T, ".3f", "0.368")
chk("KC7 appear %", pct(1 - (1 - 1 / T) ** T), ".0f", "63")
anchor("A18-18", f"{(1 - 1 / T) ** T:.6f}", "0.367848")

# ====================================================================== X7 (experiment 14): what resampling destroys
x7 = x7_resamples(d)
data_pmf = np.bincount(np.minimum(x7.counts, 8), minlength=9)
anchor("A18-35", ", ".join(str(int(x)) for x in data_pmf), "210, 38, 9, 16, 4, 5, 1, 0, 3")
chk("months", float(len(x7.months)), ".0f", "286")
assert (x7.nmon[0], x7.nmon[-1]) == (18, 6)
has("partial months", "partial (18 and 6 returns)")
top = [x7.months[i] for i in np.flatnonzero(x7.counts == x7.counts.max())]
assert int(x7.counts.max()) == 8 and top == ["2008-09", "2008-10", "2020-03"]
has("months with eight", "three months with eight (September 2008, October 2008 and March 2020)")
chk("monthly variance, data", float(x7.counts.var()), ".3f", "1.846")
chk("monthly variance, resamples", float(x7.variances.mean()), ".3f", "0.598")
chk("monthly variance SE", se(x7.variances), ".3f", "0.002")
lam_m = int(big.sum()) / T
ev = float(x7.nmon.mean() * lam_m * (1 - lam_m) * (1 - 1 / len(x7.months)) + lam_m**2 * x7.nmon.var())
chk("monthly variance, independent days", ev, ".3f", "0.597")
pmf_avg, pmf_se = x7.pmf.mean(axis=0), x7.pmf.std(axis=0) / math.sqrt(x7.pmf.shape[0])
anchor("A18-36", ", ".join(f"{x:.1f}" for x in pmf_avg), "154.3, 96.3, 28.8, 5.7, 0.8, 0.1, 0.0, 0.0, 0.0")
assert pmf_se.max() <= 0.3
has("SE at most 0.3", "standard errors at most 0.3")
chk("lag-1 |r|, data", lag1(np.abs(r)), ".3f", "0.161")
chk("lag-1 |r|, resamples", float(x7.lag1s.mean()), ".4f", "0.0006")
chk("lag-1 |r| SE", se(x7.lag1s), ".4f", "0.0004")
chk("X7 resamples", 1000.0, ",.0f", "1,000")

# ====================================================================== the other examples' and problems' numbers
# Problem 2
p3_ = float(stats.norm.cdf(-3))
chk("P2 Phi(-3)", p3_, ".6f", "0.001350")
chk("P2 1 - p", 1 - 0.001350, ".6f", "0.998650")
chk("P2 SE x1e5 from printed", math.sqrt(0.001350 * 0.998650 / 1e6) * 1e5, ".2f", "3.67")
chk("P2 SE x1e5", math.sqrt(p3_ * (1 - p3_) / 1e6) * 1e5, ".2f", "3.67")
chk("P2 distractor A", math.sqrt(p3_ * (1 - p3_)), ".4f", "0.0367")
chk("P2 distractor B x1e9", p3_ * (1 - p3_) / 1e6 * 1e9, ".2f", "1.35")
# Problem 1, 3
chk("P1 sqrt(10)", math.sqrt(10), ".2f", "3.16")
chk("P3 mean of B", 0.02992, ".2f", "0.03")
chk("P3 1/lambda", 1 / 0.02992, ".1f", "33.4")
chk("P3 bound of C", 1 - math.exp(-0.02992), ".4f", "0.0295")
# Problem 4
ret5 = sorted([1.2, -0.8, 0.3, -2.5, 0.6])
draws4 = [ret5[math.ceil(5 * u) - 1] for u in (0.37, 0.95, 0.18)]
assert [math.ceil(5 * u) for u in (0.37, 0.95, 0.18)] == [2, 5, 1] and draws4 == [-0.8, 1.2, -2.5]
has("P4 ranks", "$\\lceil1.85\\rceil=2$, $\\lceil4.75\\rceil=5$ and $\\lceil0.9\\rceil=1$")
# Problem 5
chk("P5 E G", 0.0097 * math.sqrt(1 - 0.835), ".4f", "0.0039")
chk("P5 Pr", 0.0022 * math.sqrt(1 - 0.058), ".4f", "0.0021")
anchor("A18-53", f"{0.0097 * math.sqrt(1 - 0.835):.5f}; {0.0022 * math.sqrt(1 - 0.058):.5f}", "0.00394; 0.00214")
# Problem 6
chk("P6 1 - rho^2", 1 - 0.95**2, ".4f", "0.0975")
chk("P6 factor", 1 / (1 - 0.95**2), ".1f", "10.3")
chk("P6 factor from printed 0.0975", 1 / 0.0975, ".1f", "10.3")
chk("P6 A", 1 / 0.95**2, ".2f", "1.11")
chk("P6 C", 1 / (1 - 0.95), ".0f", "20")
# Problem 7
v3 = math.exp(9) * float(stats.norm.cdf(-6))
chk("P7 Phi(-3) x1e3", p3_ * 1e3, ".4f", "1.3499")
chk("P7 e^9 Phi(-6) x1e6", v3 * 1e6, ".3f", "7.994")
chk("P7 IS variance x1e6", (v3 - p3_**2) * 1e6, ".2f", "6.17")
chk("P7 IS variance from printed x1e6", (7.994e-6 - 1.3499e-3**2) * 1e6, ".2f", "6.17")
chk("P7 plain variance x1e3", p3_ * (1 - p3_) * 1e3, ".3f", "1.348")
chk("P7 plain variance from printed x1e3", 1.3499e-3 * (1 - 1.3499e-3) * 1e3, ".3f", "1.348")
chk("P7 ratio", p3_ * (1 - p3_) / (v3 - p3_**2), ".0f", "218")
chk("P7 ratio from printed", 1.348e-3 / 6.17e-6, ".0f", "218")
# Problem 9
chk("P9 median path", math.exp(m * rbar), ".4f", "1.9722")
chk("P9 median path from printed 0.05517%", math.exp(m * 0.0005517), ".4f", "1.9722")
anchor("A18-56", f"{math.exp(m * rbar):.6f}", "1.972177")
# Problem 10
assert all((4 / N < 0.5) == (N > 8) for N in range(1, 40))
# Problem 11 and the pitfall of section 2
pa, pb = float(stats.norm.cdf(-2.01)), float(stats.norm.cdf(-1.99))
chk("P11 Phi(-2.01)", pa, ".7f", "0.0222156")
chk("P11 Phi(-1.99)", pb, ".7f", "0.0232955")
chk("P11 difference", 0.0232955 - 0.0222156, ".7f", "0.0010799")
chk("P11 1 - difference", 1 - (0.0232955 - 0.0222156), ".7f", "0.9989201")
chk("P11 1 - Phi(-2.01)", 1 - 0.0222156, ".7f", "0.9777844")
chk("P11 1 - Phi(-1.99)", 1 - 0.0232955, ".7f", "0.9767045")
chk("P11 central difference", (0.0222156 - 0.0232955) / 0.02, ".4f", "-0.0540")
chk("P11 -phi(2)", -float(stats.norm.pdf(2)), ".4f", "-0.0540")
vsum = 0.0222156 * 0.9777844 + 0.0232955 * 0.9767045
chk("P11 sum of variances", vsum, ".6f", "0.044475")
chk("P11 SE independent", math.sqrt(0.044475 / 1e5) / 0.02, ".4f", "0.0333")
chk("P11 SE independent, unrounded", math.sqrt((pa * (1 - pa) + pb * (1 - pb)) / 1e5) / 0.02, ".4f", "0.0333")
chk("P11 variance of the common indicator", 0.0010799 * 0.9989201, ".7f", "0.0010787")
chk("P11 SE common", math.sqrt(0.0010787 / 1e5) / 0.02, ".4f", "0.0052")
chk("P11 SE common, unrounded", math.sqrt((pb - pa) * (1 - (pb - pa)) / 1e5) / 0.02, ".4f", "0.0052")
anchor("A18-58", f"{math.sqrt((pa * (1 - pa) + pb * (1 - pb)) / 1e5) / 0.02:.5f}; "
       f"{math.sqrt((pb - pa) * (1 - (pb - pa)) / 1e5) / 0.02:.5f}", "0.03334; 0.00519")
has("P11 100,000", "100,000 draws on each side")
has("pitfall 100,000", "100,000 draws a side")
# the method pitfall of section 8: stream 2 re-created
ppf3 = stats.norm.ppf(u3)
sn3 = rng(2).standard_normal(3)
for x, p in zip(ppf3, ("-1.0817", "-0.0916", "-0.9382"), strict=True):
    chk(f"norm.ppf(u) {p}", float(x), ".4f", p)
for x, p in zip(sn3, ("0.1679", "0.2891", "0.7095"), strict=True):
    chk(f"standard_normal(3) {p}", float(x), ".4f", p)
mvn = rng(2).multivariate_normal(np.zeros(5), Sig, size=3)
col = rng(2).standard_normal((3, 5)) @ L.T
assert np.abs(mvn - col).max() > 1e-12, "multivariate_normal now gives the coloured draws"

# ====================================================================== literal phrases: seeds, sizes, dates
for lit in ("`default_rng([1, 20261011])`", "`default_rng([16, 20261011])`", "`default_rng([2, 20261011])`",
            "`default_rng([e, 20261011])`", "`standard_normal(10**6)`", "`standard_normal(10_000)`",
            "`integers(0, T, size=(500, T))`", "`integers(0, T, size=(500, m))`", "`standard_normal((500, m))` ten",
            "`standard_normal((500, m))` twenty", "`standard_normal((4382, 5))`", "`default_rng(20261011)`",
            "retrieved 18 October 2026", "(experiment 14, `default_rng([14, 20261011])`; in-sample model)",
            "(experiment 12, `default_rng([12, 20261011])`)", "Experiment 3", "Experiment 5",
            "Experiment 6", "Experiment 8", "Experiment 9", "Experiment 10", "Experiment 2",
            "`default_rng([3, 20261011])`", "`default_rng([5, 20261011])`", "`default_rng([6, 20261011])`",
            "`default_rng([8, 20261011])`", "`default_rng([9, 20261011])`", "`default_rng([10, 20261011])`",
            "`default_rng([12, 20261011])`", "`default_rng([14, 20261011])`", "y = (G < 1).astype(float)",
            "import numpy as np\n\n    T, m = 5849, 1231",
            "6 (antithetic), seeded `default_rng([e, 20261011])` with `e` the experiment's number",
            "From `default_rng([2, 20261011])`, `norm.ppf(rng.random(3))`"):
    has(f"literal {lit}", lit)
has("LM12's draws", "4,382 standard normal draws")
has("1,025 evaluations", "$4.83\\times10^{-9}$ at 1,025")
has("LM5's threshold", "$p=\\Pr(Z\\le-4.1074386)=2.000355\\times10^{-5}$")
has("code inputs", "m, g, sr = 1231, 0.0005517, 0.012107")
has("ranks in math", "$R_{(818)}$, $R_{(2712)}$ and $R_{(1019)}$")
has("5,000 pairs", "5,000 pairs")
has("10,000 paths", "10,000 paths")
has("seed in the code", "rng = np.random.default_rng([3, 20261011])")

# numbers in the text that no check above covers (printed for the writer's and the reviewer's eyes; section numbers,
# equation tags, years in references and the like are expected here)
body = NORM.split("## Glossary")[0]
body = re.sub(r"\(\d{1,2}\.\d{1,2}\)|\\tag\{[^}]*\}|\[\[[^\]]*\]\]|\{#[\w-]+\}|lm=[\d,]+|https?://\S+", " ", body)
nums = sorted({x.rstrip(".,") for x in re.findall(r"(?<![\w.])\d[\d,]*(?:\.\d+)?", body)} - {""})
uncovered = [x for x in nums if not any(re.search(r"(?<![\d.])" + re.escape(x) + r"(?!\d)", c) for c in COVERED)]
print("numbers in the text not covered by a check:", ", ".join(uncovered))

print()
if ANCHOR_DIFFS:
    print("anchors that differ (reported, not forced):")
    for s_ in ANCHOR_DIFFS:
        print("  ", s_)
print(f"\nall {N_CHECKS} checks passed")
