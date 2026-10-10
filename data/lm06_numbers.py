"""LM6: every time-value-of-money number quoted in the module (Sections 2-7, examples, knowledge checks, practice
problems and solutions) that does not come from the TX/TAIEX data.  The 0050 Gordon-model inputs are read from the
verified raw FinMind files.  Run:  python3 data/lm06_numbers.py
Rates labelled "illustrative" in the module are assumptions chosen for teaching, not market quotes."""
import glob
import math
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
P = print


# ------------------------------------------------------------------ core TVM functions (derived in Sections 2-6)
def geo_sum(a, x, n):
    """a + a x + ... + a x^(n-1), eq. (6.1)."""
    return n * a if x == 1 else a * (1 - x**n) / (1 - x)


def annuity_pv(A, i, n, due=False):
    """PV of n level payments A at periodic rate i (ordinary: end of period), eq. (6.4); due: times (1+i)."""
    pv = A * n if i == 0 else A * (1 - (1 + i) ** -n) / i
    return pv * (1 + i) if due else pv


def annuity_fv(A, i, n, due=False):
    fv = A * n if i == 0 else A * ((1 + i) ** n - 1) / i
    return fv * (1 + i) if due else fv


def growing_annuity_pv(A1, i, g, n):
    """PV of A1, A1(1+g), ..., n payments, eq. (6.8)."""
    return n * A1 / (1 + i) if abs(i - g) < 1e-15 else A1 / (i - g) * (1 - ((1 + g) / (1 + i)) ** n)


def bond_price(y, c, n, F=100.0, freq=1):
    """Price of an n-period bond, coupon rate c (annual), yield y (annual), freq payments per year."""
    i, C = y / freq, c * F / freq
    return annuity_pv(C, i, n * freq) + F * (1 + i) ** -(n * freq)


def npv(rate, flows):
    """flows: list of (t, cash flow); t in periods."""
    return sum(cf * (1 + rate) ** -t for t, cf in flows)


def bisect(f, a, b, tol=1e-10, maxit=200, log=None):
    fa = f(a)
    assert fa * f(b) < 0, "root not bracketed"
    for k in range(1, maxit + 1):
        m = 0.5 * (a + b); fm = f(m)
        if log is not None: log.append((k, a, b, m, fm))
        if fm == 0 or (b - a) / 2 < tol: return m, k
        if fa * fm < 0: b = m
        else: a, fa = m, fm
    return 0.5 * (a + b), maxit


def amort_payment(L, i, n):
    return L * i / (1 - (1 + i) ** -n)


def amort_schedule(L, i, n, grace=0, method="annuity"):
    """List of (k, payment, interest, principal, balance). grace: interest-only months first."""
    rows, B = [], L
    A = amort_payment(L, i, n - grace) if method == "annuity" else None
    P_eq = L / (n - grace)
    for k in range(1, n + 1):
        I = B * i
        if k <= grace: prin = 0.0
        elif method == "annuity": prin = A - I
        else: prin = P_eq
        B = B - prin
        rows.append((k, I + prin, I, prin, B))
    return rows


def balance(L, i, n, k):
    """Outstanding balance after k payments of a level-payment loan: retrospective form (6.13)."""
    A = amort_payment(L, i, n)
    return L * (1 + i) ** k - A * ((1 + i) ** k - 1) / i


# ================================================================== SECTION 2: sequences and series
P("=== S2 ===")
P("52-week challenge NT$100 steps:", sum(100 * k for k in range(1, 53)), "= 100*52*53/2 =", 100 * 52 * 53 // 2)
for i in (0.02, 0.05, 0.08):
    P(f"perpetuity share paid within n years at i={i:.0%}:", {n: round(1 - (1 + i) ** -n, 4) for n in (10, 30, 50)},
      " PV of 1/yr forever:", round(1 / i, 2))
# geometric tail of a decaying series (KC): 1 + 0.5 + 0.25 + ...
P("tail check: sum 0.9^k k=0..19 =", round(geo_sum(1, 0.9, 20), 4), " infinite =", round(1 / (1 - 0.9), 4))

# ================================================================== SECTION 3: PV, FV, annuities
P("=== S3 ===")
# Example: saving a down payment
FV, i, n = 3_000_000, 0.024 / 12, 8 * 12
pmt = FV * i / ((1 + i) ** n - 1)
P(f"down payment: monthly deposit = {pmt:,.2f}  total deposited {pmt*n:,.0f}  interest earned {FV-pmt*n:,.0f}")
P(f"   annuity-due deposit (start of month) = {pmt/(1+i):,.2f}")
# how long does a pot last
PV, A, i = 10_000_000, 60_000, 0.03 / 12
nmon = -math.log(1 - PV * i / A) / math.log(1 + i)
P(f"pot lasts n = {nmon:.2f} months = {nmon/12:.2f} years;  at 0%: {PV/A:.1f} months = {PV/A/12:.2f} years")
A_max = PV * i  # perpetual withdrawal
P(f"   perpetual monthly withdrawal = {A_max:,.0f}")
# Example: rent paid in advance (annuity due) vs annual lump sum
rent, i = 30_000, 0.02 / 12
pv_due = annuity_pv(rent, i, 12, due=True); pv_ord = annuity_pv(rent, i, 12)
P(f"rent: PV due = {pv_due:,.0f}  PV ordinary = {pv_ord:,.0f}  ratio {pv_due/pv_ord:.6f} = 1+i {1+i:.6f}")
lump = 350_000
im, kk = bisect(lambda x: annuity_pv(rent, x, 12, due=True) - lump, 1e-6, 0.05)
P(f"   lump sum {lump:,}: saving vs PV at 2% = {pv_due-lump:,.0f};  implied monthly rate {im:.5%}, nominal annual {12*im:.3%}, EAR {(1+im)**12-1:.3%}")
# KC: ordinary vs due
P("KC S3: 1,000/yr for 10 yrs at 3%: PV ord", round(annuity_pv(1000, 0.03, 10), 2), " due", round(annuity_pv(1000, 0.03, 10, True), 2),
  " FV ord", round(annuity_fv(1000, 0.03, 10), 2), " FV due", round(annuity_fv(1000, 0.03, 10, True), 2))

# ================================================================== SECTION 4: perpetuities, growth, Gordon
P("=== S4 ===")
P("preferred: 2.4/0.04 =", 2.4 / 0.04, "; deferred 5 yrs:", round(2.4 / 0.04 / 1.04 ** 5, 2), "; perpetuity due:", round(2.4 / 0.04 * 1.04, 2))
# growing annuity check: g = i limit
P("growing annuity A1=1 i=5% g=3% n=20:", round(growing_annuity_pv(1, 0.05, 0.03, 20), 4),
  "; brute:", round(sum(1.03 ** (t - 1) / 1.05 ** t for t in range(1, 21)), 4), "; g=i:", round(growing_annuity_pv(1, 0.05, 0.05, 20), 4))
# Example: two-stage DDM (illustrative)
D0, g1, g2, r, N = 10.0, 0.12, 0.04, 0.09, 5
divs = [D0 * (1 + g1) ** t for t in range(1, N + 1)]
pv1_brute = sum(d / (1 + r) ** t for t, d in enumerate(divs, 1))
pv1_formula = growing_annuity_pv(D0 * (1 + g1), r, g1, N)
D6 = divs[-1] * (1 + g2); PN = D6 / (r - g2); pv2 = PN / (1 + r) ** N
P(f"two-stage: D1..D5 {[round(d,4) for d in divs]}  PV stage1 {pv1_brute:.4f} (formula {pv1_formula:.4f})")
P(f"   D6 {D6:.4f}  P5 {PN:.4f}  PV(P5) {pv2:.4f}  P0 {pv1_brute+pv2:.4f}  share terminal {pv2/(pv1_brute+pv2):.3f}")
P(f"   single-stage at 4%: {D0*1.04/(0.09-0.04):.2f};  at 12%: undefined (g>r)")
P(f"   justified forward P/E if payout 40% and EPS1 such that D1=E1*0.4:  P0/E1 = 0.4/(r-g) = {0.4/(0.09-0.04):.1f}")

# 0050 from raw files: close on 2016-10-07 and 2026-10-08, TTM dividends (split 4:1 on 2025-06-18)
px = pl.concat([pl.read_csv(f) for f in sorted(glob.glob(str(HERE / "raw" / "0050__*.csv")))]).sort("date")
div = pl.read_csv(HERE / "raw" / "0050_dividends.csv")
def close_on(d): return px.filter(pl.col("date") == d)["close"][0]
def ttm(end, start):
    x = div.filter((pl.col("date") > start) & (pl.col("date") <= end))
    adj = [c / 4 if d < "2025-06-18" else c for d, c in zip(x["date"], x["cash_dividend"])]
    return sum(adj), list(zip(x["date"].to_list(), x["cash_dividend"].to_list()))
P0, P0_old = close_on("2026-10-08"), close_on("2016-10-07") / 4
D0, dl = ttm("2026-10-08", "2025-10-08"); D0_old, dl_old = ttm("2016-10-07", "2015-10-07")
yrs = 10.0
g_div = (D0 / D0_old) ** (1 / yrs) - 1; g_px = (P0 / P0_old) ** (1 / yrs) - 1
r_imp = D0 * (1 + g_div) / P0 + g_div
P(f"0050: P0 {P0} (2026-10-08)  TTM D0 {D0} from {dl};  2016-10-07: P {P0_old:.4f} (split-adj)  D {D0_old:.4f} from {dl_old}")
P(f"   yield now {D0/P0:.4%}  yield 2016 {D0_old/P0_old:.4%}  10y dividend CAGR {g_div:.4%}  price CAGR {g_px:.4%}")
P(f"   implied r (g = div CAGR) = D1/P0 + g = {D0*(1+g_div)/P0:.4%} + {g_div:.4%} = {r_imp:.4%}")
for rr in (0.07, 0.08, 0.09, 0.10):
    P(f"   implied g at r={rr:.0%}: now {(rr*P0-D0)/(P0+D0):.4%}   2016 {(rr*P0_old-D0_old)/(P0_old+D0_old):.4%}")
for gg in (0.04, 0.06, g_div):
    P(f"   implied r at g={gg:.4%}: {D0*(1+gg)/P0+gg:.4%}")
share30 = ((1 + g_div) / (1 + r_imp)) ** 30
P(f"   share of Gordon value after year 30 at (r_imp, g_div): {share30:.4f};   at (9%,4%): {(1.04/1.09)**30:.4f}")
# sensitivity: price if r - g changes
P(f"   Gordon price at r_imp - 0.5pt: {D0*(1+g_div)/(r_imp-0.005-g_div):.2f}; +0.5pt: {D0*(1+g_div)/(r_imp+0.005-g_div):.2f}; base {D0*(1+g_div)/(r_imp-g_div):.2f}")

# ================================================================== SECTION 5: bonds and YTM
P("=== S5 ===")
y = 0.02
zero = 100 / (1 + y) ** 5
coup = bond_price(y, 0.03, 5)
Aam = amort_payment(100, 0.03, 5); amort = annuity_pv(Aam, y, 5)
P(f"5y at 2%: zero {zero:.4f}  3% coupon {coup:.4f}  amortizing payment {Aam:.4f} price {amort:.4f}")
P(f"   coupon bond as zeros: {sum(3/(1.02)**t for t in range(1,6)) + 100/1.02**5:.4f};  premium identity (C-yF)a_n = {(3-2)*annuity_pv(1,0.02,5):.4f} = P-F {coup-100:.4f}")
# YTM by bisection: 10y, 1.5% annual coupon, price 97.20
price0 = 97.20
log = []
ytm, k = bisect(lambda yy: bond_price(yy, 0.015, 10) - price0, 0.0, 0.05, tol=1e-8, log=log)
P(f"YTM 10y 1.5% @97.20: {ytm:.6%} after {k} iterations; check price {bond_price(ytm,0.015,10):.6f}")
for row in log[:8]:
    P("   k={:2d} a={:.6%} b={:.6%} mid={:.6%} P(mid)-price={:+.4f}".format(*row))
P(f"   last: k={log[-1][0]} mid={log[-1][3]:.6%}  bracket width {(log[-1][2]-log[-1][1]):.2e}")
P(f"   P(0)={bond_price(0,0.015,10):.2f}  P(5%)={bond_price(0.05,0.015,10):.4f}")
# Example: savings insurance IRR (illustrative): pay 100,000 at t=0..5, receive 700,000 at t=10
flows = [(t, -100_000) for t in range(6)] + [(10, 700_000)]
lg = []
irr, k = bisect(lambda x: npv(x, flows), 0.0, 0.10, tol=1e-8, log=lg)
P(f"insurance IRR = {irr:.4%} ({k} iterations)  NPV@1.7% = {npv(0.017, flows):,.0f}  NPV@2.5% = {npv(0.025, flows):,.0f}")
for row in lg[:5]:
    P("   k={:2d} a={:.4%} b={:.4%} mid={:.4%} NPV={:+,.0f}".format(*row))
P(f"   FV at 1.7% of the premiums at t=10: {sum(100_000*1.017**(10-t) for t in range(6)):,.0f}")
# pull to par: 10y bonds at a constant 2% yield, coupons 4%, 2%, 0.5%
for c in (0.04, 0.02, 0.005):
    P(f"pull to par c={c:.1%}: P0 {bond_price(0.02,c,10):.4f}  after 5y {bond_price(0.02,c,5):.4f}  after 9y {bond_price(0.02,c,1):.4f}")
# semiannual check
P(f"semiannual 10y 1.5% at 1.8%: {bond_price(0.018, 0.015, 10, freq=2):.4f}")

# ================================================================== SECTION 6: loans
P("=== S6 ===")
L, i, n = 10_000_000, 0.022 / 12, 360
A = amort_payment(L, i, n)
sch = amort_schedule(L, i, n)
tot_int = sum(r_[2] for r_ in sch)
P(f"mortgage: payment {A:,.2f}  total paid {A*n:,.0f}  total interest {tot_int:,.0f} (= nA - L {A*n-L:,.0f})")
for k in (1, 2, 12, 60, 120, 180, 240, 300, 359, 360):
    kk_, pay, I, prin, B = sch[k - 1]
    P(f"   k={k:3d} pay {pay:,.2f}  interest {I:,.2f}  principal {prin:,.2f}  balance {B:,.2f}")
B60 = balance(L, i, n, 60)
P(f"   balance after 60 (6.13) {B60:,.2f};  prospective PV of 300 remaining {annuity_pv(A, i, 300):,.2f}")
P(f"   principal ratio check: P2/P1 {sch[1][3]/sch[0][3]:.6f} = 1+i {1+i:.6f};  first principal A v^n {A*(1+i)**-n:,.2f}")
P(f"   interest share of payment 1: {sch[0][2]/A:.4%};  month when principal first exceeds 50% of payment:",
  next(r_[0] for r_ in sch if r_[3] > r_[2]))
P(f"   interest paid in first 5 years {sum(r_[2] for r_ in sch[:60]):,.0f}; principal repaid {L-B60:,.0f}")
# equal principal
sch2 = amort_schedule(L, i, n, method="equal")
tot2 = sum(r_[2] for r_ in sch2)
P(f"equal principal: first {sch2[0][1]:,.2f}  last {sch2[-1][1]:,.2f}  step {sch2[0][1]-sch2[1][1]:,.4f}  total interest {tot2:,.2f} (formula {i*L*(n+1)/2:,.2f})")
P(f"   saving vs annuity {tot_int-tot2:,.0f};  month where equal-principal payment falls below annuity payment:",
  next(r_[0] for r_ in sch2 if r_[1] < A))
P(f"   payment 37 (equal principal) {sch2[36][1]:,.2f};  first payment ratio {sch2[0][1]/A:.4f};  60 payments {60*A:,.0f}")
# grace period 3 years
sch3 = amort_schedule(L, i, n, grace=36)
tot3 = sum(r_[2] for r_ in sch3)
P(f"grace 36m: interest-only {sch3[0][1]:,.2f}  then {sch3[36][1]:,.2f}  total interest {tot3:,.0f}  extra vs none {tot3-tot_int:,.0f}")
# KC: balance after 10 years of a NT$5m 20y loan at 2.4%
L2, i2, n2 = 5_000_000, 0.024 / 12, 240
P(f"KC loan 5m 20y 2.4%: payment {amort_payment(L2,i2,n2):,.2f}  balance after 120 {balance(L2,i2,n2,120):,.0f}  ({balance(L2,i2,n2,120)/L2:.2%} of principal)")

# ================================================================== SECTION 7: forwards
P("=== S7 ===")
z = {1: 0.015, 2: 0.017, 3: 0.0185, 4: 0.0195, 5: 0.0205}  # illustrative annual-compounding spot rates
for t in range(2, 6):
    f = (1 + z[t]) ** t / (1 + z[t - 1]) ** (t - 1) - 1
    P(f"   f({t-1},1) = {f:.4%}")
f23 = ((1 + z[5]) ** 5 / (1 + z[2]) ** 2) ** (1 / 3) - 1
P(f"   f(2,3) = {f23:.4%};  approx (5 z5 - 2 z2)/3 = {(5*z[5]-2*z[2])/3:.4%}")
P(f"   check: (1.017)^2 (1+f23)^3 = {(1.017**2)*(1+f23)**3:.6f} vs 1.0205^5 = {1.0205**5:.6f}")
P(f"   discount factors: {[round((1+z[t])**-t, 6) for t in range(1,6)]}")
# 5y 3% coupon bond priced off the spot curve (cash-flow additivity) and its YTM
pz = sum(3 / (1 + z[t]) ** t for t in range(1, 6)) + 100 / (1 + z[5]) ** 5
yz, _ = bisect(lambda yy: bond_price(yy, 0.03, 5) - pz, 0.0, 0.1)
P(f"   5y 3% bond off spot curve: {pz:.4f}  YTM {yz:.4%}")
# forward FX (illustrative): USD/TWD
S, iT, iU = 30.00, 0.016, 0.040
Ffx = S * (1 + iT) / (1 + iU)
P(f"FX: 1y forward {Ffx:.4f}  points {Ffx-S:+.4f}  approx S(1+iT-iU) {S*(1+iT-iU):.4f}  err {S*(1+iT-iU)-Ffx:+.4f}")
P(f"   continuous version S e^(rT-rU): {S*math.exp(math.log(1+iT)-math.log(1+iU)):.4f}")
# 3-month version with simple money-market rates ACT/360-free (T=0.25)
F3 = S * (1 + iT * 0.25) / (1 + iU * 0.25)
P(f"   3m forward {F3:.4f}  points {F3-S:+.4f}")
# arbitrage if the quoted forward is 29.50
Fq = 29.50
P(f"   if quoted forward {Fq}: borrow USD? profit per USD 1 face at T: {(Fq - Ffx) * (1 + iU):.4f} TWD...")
# index futures fair value, toy numbers for the formula section
S0, r, q, T = 20_000, 0.02, 0.03, 0.25
P(f"toy F = S e^((r-q)T) = {S0*math.exp((r-q)*T):.2f}; basis {S0*math.exp((r-q)*T)-S0:.2f}; first-order {S0*(r-q)*T:.2f}")
# discrete dividends version: dividend 300 points paid at t=0.1
Dd, td = 300, 0.1
Fdisc = (S0 - Dd * math.exp(-r * td)) * math.exp(r * T)
P(f"toy discrete: F = (S - PV(D)) e^(rT) = {Fdisc:.2f} = S e^(rT) - D e^(r(T-td)) = {S0*math.exp(r*T) - Dd*math.exp(r*(T-td)):.2f}")

# ================================================================== extra facts used in the text
P("=== TEXT EXTRAS ===")
for apr in (0.022, 0.05):
    im = apr / 12; dbl = math.log(2) / math.log(1 + im)
    cross = max(1, math.floor(360 + 1 - dbl) + 1)
    P(f"crossover APR {apr:.1%}: doubling time {dbl:.1f} months; principal > interest from payment {cross}"
      f"  (check: payment {cross} principal share {(1+im)**-(360-cross+1):.4f})")
P(f"EAR of 2.2% APR monthly: {(1+0.022/12)**12-1:.4%}")
# knowledge checks
P("KC S2: 0.95 forever from 100:", 100 / (1 - 0.95))
P("KC S4: k = 3/62.5 =", 3 / 62.5, "; with 1% growth:", round(3 / (3 / 62.5 - 0.01), 2))
P("KC S5: 3y 2% coupon at 2.5%:", round(bond_price(0.025, 0.02, 3), 4))
P("KC S7: F = 25000 e^((0.02-0.012)*0.25) =", round(25000 * math.exp(0.02 * 0.25 - 0.003), 2),
  " basis", round(25000 * math.exp(0.02 * 0.25 - 0.003) - 25000, 2), "; no-dividend basis", round(25000 * (math.exp(0.005) - 1), 2))

# ================================================================== practice problems
P("=== PRACTICE PROBLEMS ===")
P("PP1 sum 0.9^k k<20:", round(geo_sum(1, 0.9, 20), 4))
fv2 = annuity_fv(5000, 0.0015, 120); P(f"PP2 FV {fv2:,.2f}  deposited {5000*120:,}  interest {fv2-600000:,.2f}  PV {annuity_pv(5000,0.0015,120):,.2f}")
pv3d = annuity_pv(2000, 0.025, 15, True); pv3o = annuity_pv(2000, 0.025, 15)
P(f"PP3 annuity due {pv3d:,.2f}  ordinary {pv3o:,.2f}  undiscounted {2000*15:,}")
n4 = -math.log(1 - 6_000_000 * 0.002 / 40_000) / math.log(1.002)
P(f"PP4 months {n4:.2f} = {n4/12:.2f} years; perpetual withdrawal {6_000_000*0.002:,.0f}")
P(f"PP5 1.8/0.045 = {1.8/0.045:.2f}; 1.8/0.05 = {1.8/0.05:.2f}; due {1.8/0.045*1.045:.2f}")
g6 = (0.08 * 80 - 3.2) / (80 + 3.2); k6 = 3.2 * 1.04 / 80 + 0.04
P(f"PP6 implied g {g6:.4%}; implied k at g=4% {k6:.4%}; check Gordon at g6: {3.2*(1+g6)/(0.08-g6):.4f}")
P(f"PP7 forward P/E {0.6/(0.09-0.05):.2f}; trailing {0.6*1.05/(0.09-0.05):.2f}; 0.6/0.05 {0.6/0.05:.2f}")
D0, g1, g2, k, N = 2.0, 0.10, 0.03, 0.08, 3
dv = [D0 * (1 + g1) ** t for t in range(1, N + 1)]
pv_s1 = sum(d / (1 + k) ** t for t, d in enumerate(dv, 1)); PN = dv[-1] * (1 + g2) / (k - g2)
P(f"PP8 divs {[round(x,4) for x in dv]} PV1 {pv_s1:.4f} P3 {PN:.4f} PV(P3) {PN/(1+k)**N:.4f} P0 {pv_s1+PN/(1+k)**N:.4f}")
p9 = bond_price(0.0175, 0.0125, 7)
P(f"PP9 7y 1.25% at 1.75%: {p9:.4f};  at 1.25%: {bond_price(0.0125,0.0125,7):.4f};  coupon at y=1.25 discounted at 1.75 without face? ")
lg10 = []
y10, k10 = bisect(lambda yy: bond_price(yy, 0.02, 3) - 98.0, 0.02, 0.04, tol=1e-9, log=lg10)
for row in lg10[:3]:
    P("PP10 k={:d} a={:.4%} b={:.4%} mid={:.4%} P(mid)-98={:+.4f}".format(*row))
P(f"PP10 YTM {y10:.4%} ({k10} it)  check {bond_price(y10,0.02,3):.6f}")
L11, i11, n11 = 8_000_000, 0.021 / 12, 240
A11 = amort_payment(L11, i11, n11); B96 = balance(L11, i11, n11, 96)
I97 = B96 * i11
P(f"PP11 payment {A11:,.2f}  balance after 96 {B96:,.2f}  payment 97: interest {I97:,.2f} principal {A11-I97:,.2f}"
  f"  (A v^(n-96) = {A11*(1+i11)**-(n11-96):,.2f})  total interest {A11*n11-L11:,.0f}")
s12 = amort_schedule(L11, i11, n11, method="equal")
P(f"PP12 equal principal first {s12[0][1]:,.2f} last {s12[-1][1]:,.2f} total interest {sum(r_[2] for r_ in s12):,.2f}"
  f" (formula {i11*L11*(n11+1)/2:,.2f}); level-payment total {A11*n11-L11:,.2f}; difference {A11*n11-L11-i11*L11*(n11+1)/2:,.2f}")
P(f"PP13 f(1,1) = {1.019**2/1.016-1:.4%}")
S14, iT, iU, T = 31.20, 0.015, 0.042, 0.25
F14 = S14 * (1 + iT * T) / (1 + iU * T)
P(f"PP14 3m forward {F14:.4f}  points {F14-S14:+.4f}  approx {S14*(1+(iT-iU)*T):.4f}")
S15, tau, r, qt = 23_000, 0.2, 0.02, 0.012
Ff = S15 * math.exp(r * tau - qt); F15 = 22_600
P(f"PP15 fair {Ff:.2f} basis {Ff-S15:.2f}; at F=22600: implied qtau {r*tau-math.log(F15/S15):.4%} residual {F15-Ff:.2f}"
  f" implied financing rate {(qt+math.log(F15/S15))/tau:.4%}")

# ================================================================== intermediate values shown in worked solutions
P("=== INTERMEDIATES ===")
P(f"S2 compound 100*1.02^2 = {100*1.02**2:.2f}")
P(f"Ex2(b) PV i/A = {10_000_000*0.0025/60_000:.5f}; 1 - that = {1-10_000_000*0.0025/60_000:.5f}; ln(1.0025) = {math.log(1.0025):.7f}")
P(f"Ex3 monthly rate 0.02/12 = {0.02/12:.5%}")
P(f"Ex5 (0.08*114.95 - 1.60) = {0.08*114.95-1.60:.3f}; 114.95 + 1.60 = {114.95+1.60:.2f}; 1.0843/1.0994 = {1.0843/1.0994:.6f}; ^30 = {(1.0843/1.0994)**30:.4f}")
P(f"KC5 (2-2.5)*a_3(2.5%) = {(2-2.5)*annuity_pv(1,0.025,3):.4f}")
P(f"Ex8 monthly rate {0.022/12:.7f} = {0.022/12:.5%}; principal L/n {10_000_000/360:,.2f}")
P(f"Ex9(b) 30*1.04 forward delivery {1.04*29.50:.2f}; repay 30*1.016 = {30*1.016:.2f}")
P(f"Ex7 premiums shortfall {700_000 - sum(100_000*1.017**(10-t) for t in range(6)):,.0f}")
tau = 173 / 365
P(f"Ex10 r*tau = {0.02*tau:.6f}; -ln(21700/22580.08) = {-math.log(21700/22580.08):.5f}; tau = {tau:.5f}")
P(f"KC8 Sep->Dec: r*dtau = {0.02*91/365:.5f}; -ln(21700/21834) = {-math.log(21700/21834):.5f}")
P(f"PP6 0.08*80-3.20 = {0.08*80-3.2:.2f}; 80+3.20 = {80+3.2:.2f}; 1+g = {1+(0.08*80-3.2)/(80+3.2):.5f}; D1/P0 at 4% = {3.2*1.04/80:.2%}")
P(f"PP9 (1.25-1.75)*a_7(1.75%) = {(1.25-1.75)*annuity_pv(1,0.0175,7):.2f}; option C = {100-(1.25-1.75)*annuity_pv(1,0.0175,7):.2f}")
P(f"PP11/12 monthly rate {0.021/12:.3%}; L/n = {8_000_000/240:,.2f}; first interest {8_000_000*0.021/12:,.2f}; 1+i = {1+0.021/12:.5f}")
P(f"PP2 1+i = {1.0015}; PP3 a_15(2.5%) = {annuity_pv(1,0.025,15):.4f}")
