"""Every number quoted in LM11 (Eigen-decomposition and PCA), printed and checked against src/lm11.md.

Run after data/vol2_series.py, data/build_series.py and data/lm07_series.py:
    uv run python data/lm11_numbers.py

Inputs (data/lm11_common.py): data/processed/vol2_closes.parquet (the repaired sector closes),
lm07_returns.parquet (LM7's 0050/00679B total returns, T = 2,363), etf_daily_returns.parquet (LM1's 0050/00631L
total returns, T = 2,902, LM8's sample) and vol2_repairs.json (the count of repaired closes).

Three kinds of checks, all of which stop the script on a mismatch:
  say()  prints a computed value and asserts that its printed form appears in src/lm11.md;
  chk()  recomputes a printed figure from the inputs printed next to it in the module (hand examples use the printed,
         rounded inputs: project/PITFALLS.md section 7) and asserts the printed result; it also refuses a value that sits
         on a rounding tie, where a reader rounding by hand could get the other last digit;
  need() asserts that a literal string (a name, a phrase) appears in the module.
At the end the script lists every number in the module that no check covered, for the writer's and reviewer's eyes.
"""
import json
import math
import re

import numpy as np
from lm11_common import (
    ELEC8,
    HERE,
    PROC,
    S3,
    S5,
    a_factor,
    closes,
    corr,
    cov0,
    eig_desc,
    etf_pair,
    lm07_pair,
    returns,
    sector_names,
    sign_fix,
    spec_norm,
)

MD = HERE.parent / "src" / "lm11.md"


def norm(s: str) -> str:
    """The module text with TeX thousands separators, escaped percent signs and minus signs made plain."""
    s = s.replace("{,}", ",").replace("\\%", "%").replace("\u2212", "-").replace("\\,", "")
    return re.sub(r"\\text\{([^}]*)\}", r"\1", s)


TEXT = norm(MD.read_text(encoding="utf-8")) if MD.exists() else None
COVERED: set[str] = set()
P = print


def need(*parts: str) -> None:
    """Assert that each literal string appears in the module text."""
    for s in parts:
        COVERED.add(s)
        assert TEXT is None or s in TEXT, ("missing text", s)


def say(label: str, value: float, fmt: str) -> str:
    """Print a computed value; assert that its printed form appears in the module text."""
    s = format(value, fmt)
    ok = TEXT is None or s in TEXT
    P(f"{label}: {s}{'' if ok else '   <-- NOT IN src/lm11.md'}")
    need(s)
    return s


def tie(value: float, fmt: str) -> bool:
    """True when value lies on a rounding boundary of fmt (a reader rounding by hand could go either way)."""
    m = re.search(r"\.(\d+)", fmt)
    d = int(m.group(1)) if m else 0
    scaled = abs(value) * 10 ** d * (100 if "%" in fmt else 1)
    return abs(scaled - math.floor(scaled) - 0.5) < 1e-6


def chk(label: str, value: float, fmt: str, printed: str) -> None:
    """A printed figure recomputed from printed inputs; it must equal the printed text and not sit on a tie."""
    got = format(value, fmt)
    P(f"CHECK {label}: {got} (printed {printed}) {'ok' if got == printed else 'MISMATCH'}")
    assert got == printed, (label, got, printed)
    assert not tie(value, fmt), ("rounding tie: print more digits", label, value)
    need(printed)


def deg(rad: float) -> float:
    return math.degrees(rad)


# ====================================================================== sample (Introduction, notation)
df = closes()
ALL30, U28 = sector_names(df)
dates, R = returns(df, U28)
T, N = R.shape
A = a_factor(T, df["date"][0], df["date"][-1])
P(f"U28 sample: T = {T}, first return {dates[0]}, last {dates[-1]}, A = {A:.7f}")
assert (T, N, dates[0], dates[-1]) == (4382, 28, "2008-12-02", "2026-10-08")
say("T", T, ",")
say("A", A, ".2f")                                             # "A=245.48 sessions a year" (LM7's and LM10's wording)
need("A=245.48$ sessions a year on the U28 sample")
rep = json.loads((PROC / "vol2_repairs.json").read_text(encoding="utf-8"))["repairs"]
inside = [r for r in rep if r["series"] in U28 and "2008-12-01" <= r["date"] <= "2026-10-08"]
say("repaired U28 closes in the sample", len(inside), "d")
say("on dates", len({r["date"] for r in inside}), "d")
need("406 distinct entries")                                   # 28 x 29 / 2
assert 28 * 29 // 2 == 406

S = cov0(R)
C = corr(S)
s = np.sqrt(np.diag(S))
lam, Q = eig_desc(C)
lamS, QS = eig_desc(S)
iu = np.triu_indices(N, 1)
off = C[iu]
rbar = float(off.mean())
i_lo, i_hi = int(np.argmin(off)), int(np.argmax(off))
assert (U28[iu[0][i_lo]], U28[iu[1][i_lo]]) == ("BiotechnologyMedicalCare", "OilGasElectricity")
assert (U28[iu[0][i_hi]], U28[iu[1][i_hi]]) == ("ComputerPeripheralEquipment", "ElectronicPartsComponents")
assert off.min() > 0                                         # every pair positively correlated
need("0.217 (BiotechnologyMedicalCare and OilGasElectricity)", "0.755 (ComputerPeripheralEquipment and ElectronicPartsComponents)")

# ====================================================================== case box and its exhibit
P("\n--- case ---")
say("min correlation", off.min(), ".3f")
say("max correlation", off.max(), ".3f")
say("mean off-diagonal correlation", rbar, ".3f")
say("pairs", len(off), "d")
q1 = Q[:, 0]
assert (q1 > 0).all()
assert U28[int(np.argmin(q1))] == "OilGasElectricity" and U28[int(np.argmax(q1))] == "Other"
say("PC1 smallest loading (OilGasElectricity)", q1.min(), ".3f")
say("PC1 largest loading (Other)", q1.max(), ".3f")
need("with entries from 0.130 to 0.224")                       # the case box: entries of q1, not weights,
assert abs(q1.sum() - math.sqrt(N)) < 0.05                      # since they sum to about sqrt(28), not to 1
share = lam / N
cum = np.cumsum(share)
k80 = int(np.argmax(cum >= 0.80)) + 1
say("PC1 share", share[0], ".1%")
say("components for 80%", k80, "d")
yr = np.array([int(d[:4]) for d in dates])
years = list(range(2009, 2027))
ys = {y: eig_desc(corr(cov0(R[yr == y]))) for y in years}
yshare = {y: float(ys[y][0][0] / N) for y in years}
assert (max(yshare, key=lambda y: yshare[y]), min(yshare, key=lambda y: yshare[y])) == (2020, 2017)
say("highest yearly share (2020)", yshare[2020], ".1%")
say("lowest yearly share (2017)", yshare[2017], ".1%")
need("66.6% in 2020", "34.5% in 2017", "34.5% (2017), 66.6% (2020)")
pos2 = [U28[i] for i in range(N) if Q[i, 1] > 0]
P("PC2 positive:", pos2)
assert len(pos2) == 11 and set(ELEC8) <= set(pos2)
assert set(pos2) - set(ELEC8) == {"BiotechnologyMedicalCare", "Chemical", "ElectricMachinery"}
need("eight electronics sub-industries and on BiotechnologyMedicalCare, Chemical and ElectricMachinery")
say("PC2 negative count", N - len(pos2), "d")
up, dn = (R > 0).all(axis=1), (R < 0).all(axis=1)
assert (int(up.sum() + dn.sum()), int(up.sum()), int(dn.sum())) == (300, 144, 156)
say("same-sign days", int(up.sum() + dn.sum()), "d")
say("same-sign share", float(up.sum() + dn.sum()) / T, ".1%")
need("144; 156")
r7 = R[dates.index("2025-04-07")]
assert (r7 < 0).all()
assert U28[int(np.argmin(r7))] == "Semiconductor" and U28[int(np.argmax(r7))] == "CommunicationsInternet"
say("2025-04-07 smallest fall (CommunicationsInternet)", -r7.max(), ".2%")
say("2025-04-07 largest fall (Semiconductor)", -r7.min(), ".2%")
need("5.90% (CommunicationsInternet) to 9.95% (Semiconductor)")

# halves and the solution of Sigma x = 1
h = T // 2
assert h == 2191 and (dates[h - 1], dates[h]) == ("2017-10-06", "2017-10-11")
need("2,191", "6 October 2017", "11 October 2017")
S1, S2 = cov0(R[:h]), cov0(R[h:])
one = np.ones(N)
x1, x2 = np.linalg.solve(S1, one), np.linalg.solve(S2, one)
iS, iF = U28.index("Semiconductor"), U28.index("FinancialInsurance")
say("x Semiconductor, first half", x1[iS], ",.2f")
say("x Semiconductor, second half", x2[iS], ",.2f")
say("x Financial, first half", x1[iF], ",.2f")
say("x Financial, second half", x2[iF], ",.2f")
rel_u28 = float(np.linalg.norm(x2 - x1) / np.linalg.norm(x2))
say("relative change", rel_u28, ".3f")
need("0.729 of the second half's solution length")             # relative to ||x(2)||, the denominator of (11.9)
P(f"   (relative to the first half's length instead: {np.linalg.norm(x2 - x1) / np.linalg.norm(x1):.4f}; not printed)")
say("cosine of the two solutions", float(x1 @ x2 / np.linalg.norm(x1) / np.linalg.norm(x2)), ".3f")

# ====================================================================== Section 2: E1 (Semiconductor / Financial)
P("\n--- Section 2 ---")
_, RSF = returns(df, S3[:2])
SSF = cov0(RSF)
m11, m22, m12 = (round(float(v) * 1e4, 4) for v in (SSF[0, 0], SSF[1, 1], SSF[0, 1]))
assert (m11, m22, m12) == (2.3234, 1.4817, 1.0666)
need("2.3234", "1.4817", "1.0666")
chk("E1 trace", m11 + m22, ".4f", "3.8051")
chk("E1 half trace", (m11 + m22) / 2, ".5f", "1.90255")
chk("E1 (m11 - m22)^2 / 4", (m11 - m22) ** 2 / 4, ".5f", "0.17711")
chk("E1 m12^2", m12**2, ".5f", "1.13764")
chk("E1 term under the root, from the printed parts", 0.17711 + 1.13764, ".5f", "1.31475")
chk("E1 root", math.sqrt(1.31475), ".5f", "1.14663")
chk("E1 lambda1", 1.90255 + 1.14663, ".4f", "3.0492")
chk("E1 lambda2", 1.90255 - 1.14663, ".4f", "0.7559")
chk("E1 product of the eigenvalues", 3.0492 * 0.7559, ".4f", "2.3049")
chk("E1 determinant from the entries", m11 * m22 - m12**2, ".4f", "2.3049")
chk("E1 sum of the eigenvalues", 3.0492 + 0.7559, ".4f", "3.8051")
wSF, QSF = eig_desc(SSF)
assert abs(wSF[0] * 1e4 - 3.0492) < 5e-5 and abs(wSF[1] * 1e4 - 0.7559) < 5e-5
chk("E1 first row coefficient", 2.3234 - 3.0492, ".4f", "-0.7258")
slope = (3.0492 - 2.3234) / 1.0666
chk("E1 slope", slope, ".4f", "0.6805")
chk("E1 angle of q1", deg(math.atan(0.6805)), ".1f", "34.2")
chk("E1 q1 first entry", math.cos(math.atan(0.6805)), ".3f", "0.827")
chk("E1 q1 second entry", math.sin(math.atan(0.6805)), ".3f", "0.563")
assert np.allclose(QSF[:, 0], [0.827, 0.563], atol=5e-4) and np.allclose(QSF[:, 1], [-0.563, 0.827], atol=5e-4)
chk("angle of M e1", deg(math.atan2(1.0666, 2.3234)), ".1f", "24.7")
chk("pitfall: lambda1 over Semiconductor's variance", 3.0492 / 2.3234, ".2f", "1.31")
chk("correlation from the printed entries", 1.0666 / math.sqrt(2.3234 * 1.4817), ".4f", "0.5749")
# the widget's initial state (src/lm11.js), printed for the reviewer: annualized volatilities and the correlation, to
# the precision of the sliders (steps 0.0001), so that the widget's kappa matches the ladder exhibit's 4.03
P(f"widget inputs: Semiconductor {math.sqrt(A * SSF[0, 0]):.2%}, FinancialInsurance {math.sqrt(A * SSF[1, 1]):.2%}, "
  f"rho {float(corr(SSF)[0, 1]):.4f}")
assert (f"{math.sqrt(A * SSF[0, 0]):.2%}", f"{math.sqrt(A * SSF[1, 1]):.2%}", f"{float(corr(SSF)[0, 1]):.4f}") == \
    ("23.88%", "19.07%", "0.5749")

# ====================================================================== Section 3: E2 (LM7's Sigma) and E3 (S3)
P("\n--- Section 3 ---")
r50, r679, A7 = lm07_pair()
assert len(r50) == 2363
say("LM7 T", len(r50), ",")
say("LM7 A (E2: Sigma = A Sigma-hat on LM7's sample; the daily ellipse of the chart does not need it)", A7, ".4f")
S7 = cov0(np.column_stack([r50, r679])) * A7
a11, a22, a12 = (round(float(v), 6) for v in (S7[0, 0], S7[1, 1], S7[0, 1]))
assert (a11, a22, a12) == (0.040425, 0.018214, -0.002866)          # LM7's printed Sigma
need("0.040425", "0.018214", "0.002866")
chk("E2 trace", a11 + a22, ".6f", "0.058639")
d7 = math.sqrt((a11 - a22) ** 2 / 4 + a12**2)
chk("E2 lambda1 from the printed entries", (a11 + a22) / 2 + d7, ".6f", "0.040789")
chk("E2 lambda2 from the printed entries", (a11 + a22) / 2 - d7, ".6f", "0.017850")
chk("E2 slope", (0.040789 - 0.040425) / -0.002866, ".4f", "-0.1270")
chk("E2 tilt", deg(math.atan(-0.1270)), ".2f", "-7.24")
chk("E2 q1 first", math.cos(math.atan(-0.1270)), ".3f", "0.992")
chk("E2 q1 second", math.sin(math.atan(-0.1270)), ".3f", "-0.126")
chk("E2 axis volatility 1", math.sqrt(0.040789), ".2%", "20.20%")
chk("E2 axis volatility 2", math.sqrt(0.017850), ".2%", "13.36%")
chk("E2 0050 volatility", math.sqrt(0.040425), ".2%", "20.11%")
chk("E2 00679B volatility", math.sqrt(0.018214), ".2%", "13.50%")
w7, Q7 = eig_desc(S7)
assert abs(w7[0] - 0.040789) < 5e-7 and abs(w7[1] - 0.017850) < 5e-7
assert abs(deg(math.atan2(Q7[1, 0], Q7[0, 0])) + 7.24) < 0.005
chk("E2 correlation from the printed entries", -0.002866 / math.sqrt(0.040425 * 0.018214), ".3f", "-0.106")
say("LM7 correlation", float(corr(S7)[0, 1]), ".3f")
need("18 January 2017")

_, R3 = returns(df, S3)
S3h = cov0(R3) * 1e4
w3, Q3 = eig_desc(S3h)
P("E3 S3 x 1e4:", S3h.round(4).tolist())
for i in range(3):
    for j in range(i, 3):
        need(f"{S3h[i, j]:.4f}")
for k in range(3):
    say(f"E3 lambda{k + 1}", w3[k], ".4f")
w3r, Q3r = np.round(w3, 4), np.round(Q3, 4)
P("E3 Q (4 decimals):", Q3r.tolist())
for k in range(3):
    for i in range(3):
        need(f"{Q3r[i, k]:.4f}")
# rank-one pieces lambda_k q_k q_k' (x 1e4), printed to 3 decimals as a reader computes them from the printed
# eigenpairs; each lies within rounding of the unrounded piece, and the three add up to the printed matrix to within
# 0.001, which the text says
pieces = [w3[k] * np.outer(Q3[:, k], Q3[:, k]) for k in range(3)]
pr = [np.round(w3r[k] * np.outer(Q3r[:, k], Q3r[:, k]), 3) for k in range(3)]
for k in range(3):
    assert np.abs(pr[k] - pieces[k]).max() < 0.001, k
    P(f"E3 piece {k + 1}:", pr[k].tolist())
    for i in range(3):
        for j in range(i, 3):
            need(f"{pr[k][i, j]:.3f}")
gap3 = float(np.abs(pr[0] + pr[1] + pr[2] - np.round(S3h, 4)).max())
P(f"E3 largest gap between the summed printed pieces and the printed matrix: {gap3:.4f}")
assert gap3 <= 0.001 + 1e-9
need("within 0.001")
chk("E3 printed trace", 2.3234 + 1.4817 + 1.1550, ".4f", "4.9601")
chk("E3 eigenvalues add up to the trace", 3.4728 + 0.9944 + 0.4929, ".4f", "4.9601")
chk("E3 first share", 3.4728 / 4.9601, ".1%", "70.0%")

# ====================================================================== Section 4: Rayleigh quotient, condition numbers
P("\n--- Section 4 ---")
th = np.radians(np.arange(0, 180.0001, 0.01))
U = np.vstack([np.cos(th), np.sin(th)])
hu = np.einsum("in,ij,jn->n", U, SSF * 1e4, U)
P(f"X4: max h = {hu.max():.4f} at {np.degrees(th[int(np.argmax(hu))]):.2f} deg; "
  f"min {hu.min():.4f} at {np.degrees(th[int(np.argmin(hu))]):.2f} deg")
assert abs(hu.max() - 3.0492) < 5e-5 and abs(np.degrees(th[int(np.argmax(hu))]) - 34.23) < 0.02
chk("X4 angle of the minimum", 34.2 + 90, ".1f", "124.2")
r0050, r631 = etf_pair()
assert len(r0050) == 2902
rho_etf = float(np.corrcoef(r0050, r631)[0, 1])
say("0050/00631L correlation", rho_etf, ".6f")
say("0050/00631L T", len(r0050), ",")
chk("kappa 0050/00631L from the printed rho", (1 + 0.974365) / (1 - 0.974365), ".1f", "77.0")
chk("kappa 0050/00631L, problem 9", (1 + 0.974365) / (1 - 0.974365), ".2f", "77.02")
chk("problem 9 numerator", 1 + 0.974365, ".6f", "1.974365")
chk("problem 9 denominator", 1 - 0.974365, ".6f", "0.025635")
ladder = []
for lab, sig in (("0050/00679B (LM7)", cov0(np.column_stack([r50, r679]))),
                 ("0050/00631L (LM8)", cov0(np.column_stack([r0050, r631])))):
    ladder.append((lab, 2, *(eig_desc(m)[0] for m in (corr(sig), sig))))
for lab, cols in (("Semiconductor/FinancialInsurance", S3[:2]), ("S3", S3), ("S5", S5), ("U28", U28),
                  ("Electronic + eight", ["Electronic", *ELEC8]), ("All 30", ALL30)):
    sig = cov0(returns(df, cols)[1])
    ladder.append((lab, len(cols), *(eig_desc(m)[0] for m in (corr(sig), sig))))
    assert abs(np.linalg.cond(sig) / (ladder[-1][3][0] / ladder[-1][3][-1]) - 1) < 1e-9   # cond = l1/lN (SPD)
for lab, n_, wc, ws in ladder:
    P(f"X5 {lab:34s} N={n_:2d} kappa(C)={wc[0] / wc[-1]:10.4f} kappa(Sigma)={ws[0] / ws[-1]:10.4f}")
    say(f"X5 {lab} kappa(C)", wc[0] / wc[-1], ",.2f")
    say(f"X5 {lab} kappa(Sigma)", ws[0] / ws[-1], ",.2f")
k_u28_c, k_u28_s = ladder[5][2][0] / ladder[5][2][-1], ladder[5][3][0] / ladder[5][3][-1]
say("U28 kappa(C), one decimal", k_u28_c, ".1f")
say("U28 kappa(Sigma), one decimal", k_u28_s, ".1f")
chk("LM7 pair kappa(C) from its printed correlation", (1 + 0.106) / (1 - 0.106), ".2f", "1.24")
say("rho bar", rbar, ".5f")
say("756 off-diagonal entries", N * (N - 1), "d")
chk("E4 1 + 27 rho bar", 1 + 27 * 0.50227, ".3f", "14.561")
say("lambda1 U28", lam[0], ".3f")
assert 1 + 27 * rbar <= lam[0]
chk("KC kappa for rho 0.9", 1.9 / 0.1, ".0f", "19")
# Deep Dive: gradient ascent on LM7's quadratic model contracts by (kappa - 1)/(kappa + 1)
chk("Deep Dive factor from the printed eigenvalues", (0.040789 - 0.017850) / (0.040789 + 0.017850), ".3f", "0.391")
chk("Deep Dive step 2/(l1 + lN)", 2 / (0.040789 + 0.017850), ".1f", "34.1")
chk("LM7's kappa from the printed eigenvalues", 0.040789 / 0.017850, ".2f", "2.29")

# ====================================================================== Section 5: PCA
P("\n--- Section 5 ---")
say("lambda1 U28 (4 decimals)", lam[0], ".4f")
say("lambda2 U28", lam[1], ".4f")
chk("E5 share 1 from the printed lambda1", 14.7214 / 28, ".2%", "52.58%")
chk("E5 share 2 from the printed lambda2", 1.4837 / 28, ".2%", "5.30%")
say("U28 PC1 share (2 decimals)", share[0], ".2%")
say("U28 PC2 share", share[1], ".2%")
say("cumulative share at k = 11", cum[10], ".2%")
say("cumulative share at k = 12", cum[11], ".2%")
chk("problem 2: share from the printed lambda1", 14.721 / 28, ".1%", "52.6%")
chk("X6 equal share 1/28", 1 / 28, ".2%", "3.57%")
chk("X7 equal loading 1/sqrt(28)", 1 / math.sqrt(28), ".3f", "0.189")
sharesS = lamS / lamS.sum()
say("covariance PCA share 1", sharesS[0], ".2%")
say("covariance PCA share 2", sharesS[1], ".2%")
say("|cos| of the two PC1", abs(float(QS[:, 0] @ Q[:, 0])), ".4f")
iG = int(np.argmax(np.abs(QS[:, 1])))
assert U28[iG] == "GlassCeramic" and QS[iG, 1] > 0
say("covariance PC2 largest loading (GlassCeramic)", QS[iG, 1], ".3f")
vols = np.sqrt(A * np.diag(S))
assert U28[int(np.argmax(vols))] == "GlassCeramic"
say("GlassCeramic volatility", vols.max(), ".2%")
iE = int(np.argmax(np.abs(Q[:, 1])))
assert U28[iE] == "ElectronicPartsComponents" and Q[iE, 1] > 0
say("correlation PC2 largest loading (ElectronicPartsComponents)", Q[iE, 1], ".3f")
# scores: variance lambda_k (divisor T) and uncorrelated
XI = ((R - R.mean(axis=0)) / s) @ Q
cxi = XI.T @ XI / T
assert np.allclose(np.diag(cxi), lam, rtol=1e-10) and np.abs(cxi - np.diag(np.diag(cxi))).max() < 1e-10
P(f"scores: max |Var xi_k - lambda_k| = {np.abs(np.diag(cxi) - lam).max():.1e}; largest |covariance| of two scores "
  f"{np.abs(cxi - np.diag(np.diag(cxi))).max():.1e} (machine precision, not printed)")
# E6: Semiconductor in percent, FinancialInsurance in decimals
RSFp = RSF * np.array([100.0, 1.0])
w6, Q6 = eig_desc(cov0(RSFp))
P(f"E6: covariance PC1 {Q6[:, 0]}, share {w6[0] / w6.sum():.6%}")
say("E6 covariance PC1 first entry", Q6[0, 0], ".4f")
say("E6 covariance PC1 second entry", Q6[1, 0], ".4f")
say("E6 covariance share", w6[0] / w6.sum(), ".3%")
wc6, Qc6 = eig_desc(corr(cov0(RSFp)))
assert np.allclose(wc6, eig_desc(corr(SSF))[0]) and np.allclose(Qc6[:, 0], [2**-0.5, 2**-0.5])
chk("E6 correlation eigenvalue 1 from the printed rho", 1 + 0.5749, ".4f", "1.5749")
chk("E6 correlation eigenvalue 2 from the printed rho", 1 - 0.5749, ".4f", "0.4251")
say("E6 correlation eigenvalue 1", wc6[0], ".4f")

# ====================================================================== Section 6: overlap
P("\n--- Section 6 ---")
cols9 = ["Electronic", *ELEC8]
w9, Q9 = eig_desc(corr(cov0(returns(df, cols9)[1])))
q9 = Q9[:, -1]
P("E7 lambda:", w9.round(5).tolist())
P("E7 q9:", dict(zip(cols9, q9.round(3).tolist())))
assert int(np.argmax(np.abs(q9))) == 0 and q9[0] > 0
say("E7 lambda9", w9[-1], ".4f")
say("E7 lambda1", w9[0], ".3f")
say("E7 q9 Electronic", q9[0], ".3f")
say("E7 q9 Semiconductor", q9[1], ".3f")
assert cols9[2 + int(np.argmax(np.abs(q9[2:])))] == "ElectronicPartsComponents"
say("E7 largest other entry", np.abs(q9[2:]).max(), ".3f")
chk("E7 ratio Semiconductor / Electronic", 0.529 / 0.828, ".2f", "0.64")
say("E7 kappa(C)", w9[0] / w9[-1], ".0f")
chk("E7 kappa(C) from the printed eigenvalues", 6.104 / 0.0073, ".0f", "836")
w30, Q30 = eig_desc(corr(cov0(returns(df, ALL30)[1])))
v1, v2 = Q30[:, -1], Q30[:, -2]
for k_, v in ((-1, v1), (-2, v2)):
    o = np.argsort(-np.abs(v))[:3]
    P(f"X9 all 30: lambda = {w30[k_]:.5f}:", [(ALL30[i], round(float(v[i]), 3)) for i in o])
assert ALL30[int(np.argmax(np.abs(v1)))] == "Electronic" and ALL30[int(np.argmax(np.abs(v2)))] == "ChemicalBiotechnologyMedicalCare"
say("X9 all-30 smallest", w30[-1], ".5f")
say("X9 all-30 second smallest", w30[-2], ".5f")
for nm, v in (("Electronic", v1), ("Semiconductor", v1), ("ChemicalBiotechnologyMedicalCare", v2), ("Chemical", v2),
              ("BiotechnologyMedicalCare", v2)):
    say(f"X9 entry {nm}", v[ALL30.index(nm)], ".3f")
say("X9 U28 smallest", lam[-1], ".4f")

# ====================================================================== Section 7: gaps and stability
P("\n--- Section 7 ---")
eps = 0.05
for a_, b_ in ((1, 2), (6, 7)):
    say(f"E8 lambda{a_ + 1}", lam[a_], ".5f")
    say(f"E8 lambda{b_ + 1}", lam[b_], ".5f")
chk("E8 gap 2-3 from the printed eigenvalues", 1.48370 - 1.14694, ".5f", "0.33676")
chk("E8 gap 7-8 from the printed eigenvalues", 0.58028 - 0.54445, ".5f", "0.03583")
P(f"E8 unrounded gaps: {lam[1] - lam[2]:.6f}, {lam[6] - lam[7]:.6f}")
chk("E8 ratio eps/gap (2-3)", eps / 0.33676, ".4f", "0.1485")
chk("E8 exact, gap 0.33676", deg(0.5 * math.atan(2 * eps / 0.33676)), ".2f", "8.27")
chk("E8 first order, gap 0.33676", deg(eps / 0.33676), ".2f", "8.51")
chk("E8 first order from the printed radians 0.1485", deg(0.1485), ".2f", "8.51")
chk("E8 ratio eps/gap (7-8)", eps / 0.03583, ".4f", "1.3955")
chk("E8 exact, gap 0.03583", deg(0.5 * math.atan(2 * eps / 0.03583)), ".1f", "35.1")
chk("E8 first order, gap 0.03583", deg(eps / 0.03583), ".1f", "80.0")
chk("E8 first order from the printed radians 1.3955", deg(1.3955), ".1f", "80.0")
need("0.1/0.33676")
for a_, b_ in ((1, 2), (6, 7)):                                # unrounded gaps give the same printed angles
    g_ = float(lam[a_] - lam[b_])
    assert format(deg(0.5 * math.atan(2 * eps / g_)), ".2f" if a_ == 1 else ".1f") == ("8.27" if a_ == 1 else "35.1")
say("KC gap 1-2", lam[0] - lam[1], ".2f")
say("KC gap 3-4", lam[2] - lam[3], ".3f")
say("KC gap 4-5", lam[3] - lam[4], ".3f")
chk("KC: (11.7) turns q4 against q3, from the printed gap 0.193", deg(0.5 * math.atan(2 * eps / 0.193)), ".1f", "13.7")
assert format(deg(0.5 * math.atan(2 * eps / float(lam[2] - lam[3]))), ".1f") == "13.7"     # unrounded gap: same
assert deg(0.5 * math.atan(2 * eps / float(lam[3] - lam[4]))) > 10                           # "more than ten degrees"
need("more than ten degrees")
# per year
ycos1 = {y: abs(float(ys[y][1][:, 0] @ Q[:, 0])) for y in years}
ycos2 = {y: abs(float(ys[y][1][:, 1] @ Q[:, 1])) for y in years}
yplane = {y: math.hypot(float(Q[:, 1] @ ys[y][1][:, 1]), float(Q[:, 2] @ ys[y][1][:, 1])) for y in years}
ygap = {y: float(ys[y][0][1] - ys[y][0][2]) for y in years}
for y in years:
    P(f"{y} T={int((yr == y).sum()):3d} share {yshare[y]:.4f} |cos1| {ycos1[y]:.4f} |cos2| {ycos2[y]:.4f} "
      f"plane {yplane[y]:.4f} gap23 {ygap[y]:.4f}")
assert int((yr == 2026).sum()) == 185 and int((yr == 2008).sum()) == 22
say("returns in 2026", int((yr == 2026).sum()), "d")
say("returns in December 2008", int((yr == 2008).sum()), "d")
assert min(years, key=lambda y: ycos1[y]) == 2026
say("smallest yearly |cos| PC1 (2026)", ycos1[2026], ".3f")
# the printed lower bound must hold at full precision: 0.98, not the minimum rounded up (0.981 > 0.980974)
assert min(ycos1.values()) >= 0.98 and min(ycos1.values()) < 0.981
need("at least 0.98 every year", "lowest in 2026, at 0.981", "2026 has the lowest, 0.981")
assert (min(years, key=lambda y: ycos2[y]), max(years, key=lambda y: ycos2[y])) == (2016, 2025)
say("smallest yearly |cos| PC2 (2016)", ycos2[2016], ".3f")
say("largest yearly |cos| PC2 (2025)", ycos2[2025], ".3f")
assert (min(years, key=lambda y: yplane[y]), max(years, key=lambda y: yplane[y])) == (2020, 2024)
say("smallest yearly plane measure (2020)", yplane[2020], ".3f")
say("largest yearly plane measure (2024)", yplane[2024], ".3f")
assert min(years, key=lambda y: ygap[y]) == 2022
say("smallest yearly lambda2 - lambda3 (2022)", ygap[2022], ".3f")
need("0.119 (2016) to 0.946 (2025)", "0.690 (2020) to 0.959 (2024)")
# halves, correlation PCA
wa, Qa = eig_desc(corr(S1))
wb, Qb = eig_desc(corr(S2))
for k in range(5):
    say(f"X12 first half lambda{k + 1}", wa[k], ".3f")
    say(f"X12 second half lambda{k + 1}", wb[k], ".3f")
say("X12 first half share", wa[0] / N, ".1%")
say("X12 second half share", wb[0] / N, ".1%")
hc = [float(Qa[:, k] @ Qb[:, k]) for k in range(5)]
for k in range(5):
    say(f"X12 |cos| PC{k + 1}", abs(hc[k]), ".3f")
say("signed cos PC2", hc[1], ".3f")
plane_h = math.hypot(float(Qa[:, 1] @ Qb[:, 1]), float(Qa[:, 2] @ Qb[:, 1]))
say("plane measure, halves", plane_h, ".3f")
c22_4, c23_4 = round(abs(hc[1]), 4), round(abs(float(Qa[:, 2] @ Qb[:, 1])), 4)
say("|cos| PC2, 4 decimals", c22_4, ".4f")
say("cos of the second half's PC2 with the first half's PC3, 4 decimals", c23_4, ".4f")
chk("plane measure from the printed 4-decimal cosines", math.hypot(c22_4, c23_4), ".4f", f"{plane_h:.4f}")
chk("angle of q2(2) from the plane", deg(math.acos(0.9274)), ".0f", "22")
ia, ib = int(np.argmax(np.abs(Qa[:, 1]))), int(np.argmax(np.abs(Qb[:, 1])))
assert (U28[ia], U28[ib]) == ("OilGasElectricity", "ElectronicPartsComponents")
say("PC2 first half, OilGasElectricity loading", Qa[ia, 1], ".3f")
say("PC2 second half, ElectronicPartsComponents loading", Qb[ib, 1], ".3f")
# The plane measure is one-sided (review of 2026-10-11, finding 1): it says where the second half's q2 went, not that
# the plane of q2 and q3 holds. The reverse check, the cross cosines and the second half's q3 show that it does not.
say("|cos| of the second half's q2 with the first half's q3", abs(float(Qa[:, 2] @ Qb[:, 1])), ".3f")
c32_4 = round(abs(float(Qb[:, 2] @ Qa[:, 1])), 4)                # second half's q3 . first half's q2
say("cos of the first half's q2 with the second half's q3, 4 decimals", c32_4, ".4f")
rev = math.hypot(float(Qa[:, 1] @ Qb[:, 1]), float(Qa[:, 1] @ Qb[:, 2]))
say("reverse measure: first half's q2 against the second half's plane", rev, ".3f")
chk("reverse measure from the printed 4-decimal cosines", math.hypot(c22_4, c32_4), ".3f", "0.514")
need("0.2966^2+0.4196^2")
assert TEXT is None or "reverse check" not in TEXT              # one term per concept: the reverse measure
cos24 = [abs(float(Qa[:, 1] @ Qb[:, k])) for k in range(N)]
assert int(np.argmax(cos24)) == 3                              # the first half's q2 is closest to the second half's q4
say("|cos| of the first half's q2 with the second half's q4", cos24[3], ".3f")
cos32 = [abs(float(Qa[:, k] @ Qb[:, 1])) for k in range(N)]
assert int(np.argmax(cos32)) == 2                              # the second half's q2 is closest to the first half's q3
need("the first half's third direction ranks second in the second half (0.879), and its second ranks fourth (0.776)")
# Solution 4 cites 0.879 from Section 7: the printed 0.927 and 0.297 would give 0.878 (PITFALLS section 7)
assert format(math.sqrt(0.927**2 - 0.297**2), ".3f") == "0.878"
need("(cosine 0.879 in Section 7)")
plane_q3 = math.hypot(float(Qa[:, 1] @ Qb[:, 2]), float(Qa[:, 2] @ Qb[:, 2]))
say("plane measure of the second half's q3 against the first half's plane", plane_q3, ".3f")
chk("its angle, from the printed 0.437", deg(math.acos(0.437)), ".0f", "64")
assert format(deg(math.acos(plane_q3)), ".0f") == "64"
say("second half: lambda3 - lambda4", wb[2] - wb[3], ".3f")
pa = np.degrees(np.arccos(np.clip(np.linalg.svd(Qa[:, 1:3].T @ Qb[:, 1:3], compute_uv=False), -1, 1)))
P(f"for the editor (not printed in the module): principal angles between the two halves' planes of q2 and q3: "
  f"{pa[0]:.2f} and {pa[1]:.2f} degrees")
need("one-sided")

# ====================================================================== Section 8: the inverse
P("\n--- Section 8 ---")
xa_, xb_ = np.array([1, -0.95]) / (1 - 0.95**2), np.array([1, -0.96]) / (1 - 0.96**2)
for v in (*xa_, *xb_):
    say("E9 entry", v, ".3f")
chk("E9 delta x entry 1", 12.755 - 10.256, ".3f", "2.499")
chk("E9 delta x entry 2", -12.245 + 9.744, ".3f", "-2.501")
chk("E9 relative change from the printed x", math.hypot(2.499, -2.501) / math.hypot(12.755, -12.245), ".5f", "0.19996")
chk("E9 relative change (unrounded)", float(np.linalg.norm(xb_ - xa_) / np.linalg.norm(xb_)), ".5f", "0.19996")
chk("E9 kappa", 1.95 / 0.05, ".0f", "39")
chk("E9 norm ratio", 0.01 / 1.95, ".6f", "0.005128")
chk("E9 bound from the printed factors", 39 * 0.005128, ".4f", "0.2000")
assert abs(39 * 0.01 / 1.95 - 0.2) < 1e-15
# E10 and X14: shares of ||x||^2 by component, through (11.8)
for lab, Sh, xh in (("first", S1, x1), ("second", S2, x2)):
    wh, Qh = eig_desc(Sh)
    cs = (Qh.T @ one / wh) ** 2 / float(xh @ xh)
    assert abs(cs.sum() - 1) < 1e-9 and np.allclose(Qh @ (Qh.T @ one / wh), xh)
    say(f"E10 {lab} half, PC1 share of ||x||^2", cs[0], ".1%")
    say(f"E10 {lab} half, the 14 smallest components", cs[14:].sum(), ".1%")
    P(f"   {lab}: shares by k {np.round(cs * 100, 2).tolist()}")
    # "they also lie close together": every gap between neighbours among the 14 smallest eigenvalues is under 1% of
    # the gap between lambda_1 and lambda_2 (review finding 2)
    gaps = -np.diff(wh[14:])
    assert gaps.max() < 0.01 * (wh[0] - wh[1]), (lab, gaps.max() / (wh[0] - wh[1]))
    P(f"   {lab}: largest neighbouring gap among the 14 smallest eigenvalues {gaps.max():.2e}, "
      f"{gaps.max() / (wh[0] - wh[1]):.2%} of lambda_1 - lambda_2")
# "poorly determined": |cos theta| between the halves' covariance eigenvectors, component by component
wc1, Qc1 = eig_desc(S1)
wc2, Qc2 = eig_desc(S2)
ccov = np.abs(np.sum(Qc1 * Qc2, axis=0))
P("covariance PCA, |cos| between the halves, k = 1..28:", np.round(ccov, 3).tolist())
assert int(np.argmax(ccov)) == 0                               # PC1, the most stable direction
n_small = int((ccov[14:] < 0.25).sum())
assert n_small == 12 and np.all(np.abs(ccov[14:] - 0.25) > 0.005)    # no value near the 0.25 edge
say("eigenvectors of the 14 smallest eigenvalues with |cos| below 0.25", n_small, "d")
need("12 of the 14 eigenvectors of the smallest eigenvalues have", "below 0.25")
k1 = float(np.linalg.cond(S1))
dn_ = spec_norm(S2 - S1) / spec_norm(S1)
say("kappa(Sigma^(1))", k1, ".2f")
say("||dS||/||S||", dn_, ".5f")
say("||dS||/||S|| in percent", dn_, ".1%")
chk("E10 bound from the printed factors", 126.05 * 0.24536, ".2f", "30.93")
P(f"bound U28 (unrounded): {k1 * dn_:.4f}; kappa(Sigma^(2)) = {np.linalg.cond(S2):.2f}")
ev_d = np.linalg.eigvalsh(S2 - S1)
assert ev_d.min() < 0 < ev_d.max()                            # Delta Sigma is indefinite
P(f"Delta Sigma eigenvalues from {ev_d.min():.3e} to {ev_d.max():.3e}: indefinite")
# X13: S5 halves
R5 = returns(df, S5)[1]
S5a, S5b = cov0(R5[:h]), cov0(R5[h:])
x5a, x5b = np.linalg.solve(S5a, np.ones(5)), np.linalg.solve(S5b, np.ones(5))
for v in (*x5a, *x5b):
    say("X13 S5 entry", v, ",.2f")
rel5 = float(np.linalg.norm(x5b - x5a) / np.linalg.norm(x5b))
say("S5 relative change", rel5, ".3f")
say("S5 cosine", float(x5a @ x5b / np.linalg.norm(x5a) / np.linalg.norm(x5b)), ".3f")
k5 = float(np.linalg.cond(S5a))
dn5 = spec_norm(S5b - S5a) / spec_norm(S5a)
say("S5 kappa(Sigma^(1))", k5, ".3f")
say("S5 ||dS||/||S||", dn5, ".5f")
chk("S5 bound from the printed factors", 10.863 * 0.44235, ".3f", "4.805")
assert format(k5 * dn5, ".3f") == "4.805"
chk("pitfall: S5 kappa, one decimal", 10.863, ".1f", "10.9")
chk("pitfall: U28 kappa, whole", 126.05, ".0f", "126")
need(r"S5 has $\kappa(\hat\Sigma^{(1)})=10.9$", r"U28 has $\kappa(\hat\Sigma^{(1)})=126$")   # the pitfall names the matrix
chk("problem 10: S5 realized over bound", 0.910 / 4.805, ".2f", "0.19")
chk("problem 10: U28 realized over bound", 0.729 / 30.93, ".3f", "0.024")
chk("problem 10: ratio of the two kappas", 126.05 / 10.863, ".1f", "11.6")

# ====================================================================== Problems
P("\n--- Problems ---")
chk("P2 distractor A: lambda1 read as a percentage", 14.721 / 100, ".1%", "14.7%")
need("80%", "1.95/0.05", "0.01/1.95", "0.96")                 # the threshold and E9's inputs
chk("P2 distractor: sum of all entries of C from the printed rho bar", 28 + 756 * 0.50227, ".1f", "407.7")
chk("P2 distractor: lambda1 over that sum", 14.721 / 407.7, ".1%", "3.6%")
assert abs(float(C.sum()) - (28 + 756 * rbar)) < 1e-9
say("sum of all entries of C", float(C.sum()), ".1f")
need("784 entries")
# P5: Plastics / Food from the printed entries
SPF = cov0(returns(df, ["Plastics", "Food"])[1]) * 1e4
p11, p22, p12 = (round(float(v), 4) for v in (SPF[0, 0], SPF[1, 1], SPF[0, 1]))
assert (p11, p22, p12) == (2.5228, 1.1550, 0.7180)
need("2.5228", "1.1550", "0.7180")
chk("P5 trace", p11 + p22, ".4f", "3.6778")
chk("P5 half trace", (p11 + p22) / 2, ".4f", "1.8389")
chk("P5 m11 - m22", p11 - p22, ".4f", "1.3678")
chk("P5 (m11 - m22)^2 / 4", 1.3678**2 / 4, ".5f", "0.46772")
chk("P5 m12^2", p12**2, ".5f", "0.51552")
chk("P5 term under the root", 0.46772 + 0.51552, ".5f", "0.98324")
chk("P5 root", math.sqrt(0.98324), ".5f", "0.99158")
chk("P5 lambda1", 1.8389 + 0.99158, ".4f", "2.8305")
chk("P5 lambda2", 1.8389 - 0.99158, ".4f", "0.8473")
chk("P5 slope", (2.8305 - 2.5228) / 0.7180, ".4f", "0.4286")
chk("P5 angle", deg(math.atan(0.4286)), ".1f", "23.2")
chk("P5 q1 first", math.cos(math.atan(0.4286)), ".3f", "0.919")
chk("P5 q1 second", math.sin(math.atan(0.4286)), ".3f", "0.394")
chk("P5 share", 2.8305 / 3.6778, ".1%", "77.0%")
chk("P5 kappa", 2.8305 / 0.8473, ".2f", "3.34")
wPF = eig_desc(SPF)[0]
assert abs(wPF[0] - 2.8305) < 1e-4 and abs(wPF[1] - 0.8473) < 2e-4
# P6: equicorrelation N = 5, rho = 0.5, against S5's C
chk("P6 lambda1", 1 + 4 * 0.5, ".0f", "3")
chk("P6 share", 3 / 5, ".0%", "60%")
chk("P6 kappa", 3 / 0.5, ".0f", "6")
C5 = corr(cov0(R5))
w5, Q5 = eig_desc(C5)
for k in range(5):
    say(f"P6/P11 S5 lambda{k + 1}", w5[k], ".4f")
chk("P11 printed eigenvalues add up to the trace", float(np.round(w5, 4).sum()), ".4f", "5.0000")
say("S5 rho bar", float(C5[np.triu_indices(5, 1)].mean()), ".3f")
chk("P6 1 + 4 rho bar from the printed rho bar", 1 + 4 * 0.462, ".3f", "2.848")
chk("P6 S5 kappa from the printed eigenvalues", 2.8633 / 0.3362, ".2f", "8.52")
chk("P6 S5 share from the printed lambda1", 2.8633 / 5, ".1%", "57.3%")
P("P11 S5 loadings (correlation PCA, 3 decimals, order Semiconductor, FinancialInsurance, Food, Plastics, Shipping):",
  np.round(Q5, 3).tolist())
need(", ".join(f"{v:.3f}" for v in Q5[:4, 0]) + f" and {Q5[4, 0]:.3f}")
# P7: rebuild from lambda1 = 4, lambda2 = 1, theta = 30 degrees
c30, s30 = math.cos(math.radians(30)), math.sin(math.radians(30))
M7 = 4 * np.outer([c30, s30], [c30, s30]) + np.outer([-s30, c30], [-s30, c30])
chk("P7 m11", M7[0, 0], ".2f", "3.25")
chk("P7 m22", M7[1, 1], ".2f", "1.75")
chk("P7 m12", M7[0, 1], ".4f", "1.2990")
chk("P7 m12 squared", 27 / 16, ".4f", "1.6875")
chk("P7 determinant", 3.25 * 1.75 - 1.6875, ".4f", "4.0000")
assert abs(M7[0, 0] + M7[1, 1] - 5) < 1e-12 and abs(np.linalg.det(M7) - 4) < 1e-12
# P8: rows (2, eps) and (eps, 1)
chk("P8 exact, eps = 0.1", deg(0.5 * math.atan(0.2)), ".2f", "5.65")
chk("P8 first order, eps = 0.1", deg(0.1), ".2f", "5.73")
chk("P8 exact, eps = 0.5", deg(0.5 * math.atan(1.0)), ".2f", "22.50")
chk("P8 first order, eps = 0.5", deg(0.5), ".2f", "28.65")
chk("P8 overshoot", 28.65 / 22.50 - 1, ".0%", "27%")
# P9
chk("P9 rho for kappa 100", 99 / 101, ".4f", "0.9802")

# ====================================================================== widget initial state (for the reviewer)
P("\n--- widget pca2, initial state (Semiconductor / FinancialInsurance, covariance, b = e1) ---")
s1w, s2w, rw = 0.2388, 0.1907, 0.5749                          # src/lm11.js: slider values (steps 0.0001)


def wmat(rho_: float, s1_: float = s1w, s2_: float = s2w) -> np.ndarray:
    return np.array([[s1_**2, rho_ * s1_ * s2_], [rho_ * s1_ * s2_, s2_**2]])


def rel_bound(m0: np.ndarray, m1: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    """The widget's relative change ||dx|| / ||x + dx|| and its bound (11.9), kappa ||dM||_2 / ||M||_2."""
    xa_w, xb_w = np.linalg.solve(m0, b), np.linalg.solve(m1, b)
    w0 = eig_desc(m0)[0]
    return (float(np.linalg.norm(xb_w - xa_w) / np.linalg.norm(xb_w)),
            float(w0[0] / w0[1] * spec_norm(m1 - m0) / w0[0]))


ww, qw = eig_desc(wmat(rw))
xw, xw2 = np.linalg.solve(wmat(rw), [1.0, 0.0]), np.linalg.solve(wmat(rw + 0.01), [1.0, 0.0])
P(f"lambda {ww.round(6).tolist()}, share {ww[0] / ww.sum():.4f}, kappa {ww[0] / ww[1]:.3f}, angle of q1 "
  f"{deg(math.atan2(qw[1, 0], qw[0, 0])):.2f} deg, x {xw.round(3).tolist()} -> {xw2.round(3).tolist()}, relative "
  f"change {np.linalg.norm(xw2 - xw) / np.linalg.norm(xw2):.4f}, bound "
  f"{ww[0] / ww[1] * spec_norm(wmat(rw + 0.01) - wmat(rw)) / ww[0]:.4f}")
# the widget's kappa reads like the ladder exhibit's kappa(Sigma) for the same pair (review findings 7 and A4)
assert format(ww[0] / ww[1], ".2f") == format(ladder[2][3][0] / ladder[2][3][-1], ".2f") == "4.03"
# the note: equal volatilities and b = 1; for rho > 0, 1 is q1 and the change is 0.01/(1 + rho), below the bound; for
# rho < 0, 1 is q2 and the change equals the bound (review findings 8 and A1)
for rho_ in (0.5, 0.9, -0.5, -0.9):
    m0, m1 = wmat(rho_, 0.2, 0.2), wmat(rho_ + 0.01, 0.2, 0.2)
    q_one = eig_desc(m0)[1][:, 0 if rho_ > 0 else 1]
    assert np.allclose(q_one, np.array([1.0, 1.0]) / math.sqrt(2))
    rc, bd = rel_bound(m0, m1, np.ones(2))
    assert abs(rc - 0.01 / (1 + rho_)) < 1e-12 and (rc < bd - 1e-6 if rho_ > 0 else abs(rc - bd) < 1e-12), (rho_, rc, bd)
    P(f"equal volatilities, b = 1, rho {rho_:+.1f}: relative change {rc:.4f}, bound {bd:.4f}")
JS = (HERE.parent / "src" / "lm11.js").read_text(encoding="utf-8")   # the note's formula sits in the widget
assert "0.01/(1 + ρ)" in JS and "Bound (11.9)" in JS and "bound (11.9)" in JS and "value: 0.5749" in JS
assert np.allclose(sign_fix(np.array([-1.0, 1.0]) / math.sqrt(2)), np.array([1.0, -1.0]) / math.sqrt(2))

# ====================================================================== numbers in the text that no check covered
if TEXT is not None:
    body = re.sub(r"(?s)^---\n.*?\n---\n", "", TEXT)
    body = re.sub(r"(?s)```.*?```", "", body)
    body = body.split("## Glossary")[0]
    toks = set(re.findall(r"(?<![\w.$])-?\d[\d,]*\.\d+%?|(?<![\w.$])\d{1,3}(?:,\d{3})+|(?<![\w.$])\d+%", body))
    known = " ".join(COVERED)
    left = sorted(t for t in toks if t not in known and t.lstrip("-") not in known
                  and not re.fullmatch(r"(7|9|10|11|12)\.\d+", t)       # equation tags
                  and t not in {"4.7", "4.18", "6.1", "6.5", "7.3", "13:30"})   # sections of the references
    P("\nnumbers in src/lm11.md that no check covered:", left if left else "none")
P("\nall checks passed" if TEXT is not None else "\nsrc/lm11.md not found: values printed, text not checked")
