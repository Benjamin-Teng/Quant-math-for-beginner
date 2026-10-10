"""LM6: every time-value-of-money number quoted in the module (Sections 2-7, examples, knowledge checks, practice
problems and solutions) that does not come from the TX/TAIEX data.  The 0050 Gordon-model inputs are read from the
verified raw FinMind files.  Run:  uv run python data/lm06_numbers.py
Rates labelled "illustrative" in the module are assumptions chosen for teaching, not market quotes."""
import glob
import math
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
P = print


# ------------------------------------------------------------------ core TVM functions (derived in Sections 2-6)
def geo_sum(a, x, n):
    """a + a x + ... + a x^(n-1), eq. (6.2)."""
    return n * a if x == 1 else a * (1 - x**n) / (1 - x)


def annuity_pv(pmt, i, n, due=False):
    """PV of n level payments PMT at periodic rate i (ordinary: end of period), eq. (6.5); due: times (1+i), eq. (6.7)."""
    pv = pmt * n if i == 0 else pmt * (1 - (1 + i) ** -n) / i
    return pv * (1 + i) if due else pv


def annuity_fv(pmt, i, n, due=False):
    fv = pmt * n if i == 0 else pmt * ((1 + i) ** n - 1) / i
    return fv * (1 + i) if due else fv


def growing_annuity_pv(pmt1, i, g, n):
    """PV of PMT1, PMT1(1+gamma), ..., n payments, eq. (6.9) (gamma = growth rate per period)."""
    return n * pmt1 / (1 + i) if abs(i - g) < 1e-15 else pmt1 / (i - g) * (1 - ((1 + g) / (1 + i)) ** n)


def bond_price(y, c, n, M=100.0, freq=1):
    """Price of an n-year bond with face value M, coupon rate c (annual), yield y (annual), freq payments a year, eq. (6.14)."""
    i, C = y / freq, c * M / freq
    return annuity_pv(C, i, n * freq) + M * (1 + i) ** -(n * freq)


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
    pmt = amort_payment(L, i, n - grace) if method == "annuity" else 0.0
    P_eq = L / (n - grace)
    for k in range(1, n + 1):
        I = B * i
        if k <= grace: prin = 0.0
        elif method == "annuity": prin = pmt - I
        else: prin = P_eq
        B = B - prin
        rows.append((k, I + prin, I, prin, B))
    return rows


def balance(L, i, n, k):
    """Outstanding balance after k payments of a level-payment loan: retrospective form of (6.17)."""
    pmt = amort_payment(L, i, n)
    return L * (1 + i) ** k - pmt * ((1 + i) ** k - 1) / i


def pv_payments(rows, j):
    """Present value at monthly rate j of a schedule's payments (rows from amort_schedule)."""
    return sum(pay * (1 + j) ** -k for k, pay, *_ in rows)


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
# printed chain (A4): unrounded D5 to 6 decimals, D6 to 5, P5 to 3 decimals; each step must reproduce from the page
D6p = round(divs[-1] * 1.04, 5); P5p = round(D6p / 0.05, 3)
assert round(P5p / 1.09 ** 5, 4) == round(pv2, 4) and round(54.2831 + round(pv2, 4), 2) == round(pv1_brute + pv2, 2)
P(f"   printed chain: D5 {divs[-1]:.6f} (unrounded); D6 = D5 x 1.04 = {D6p:.5f}; P5 = {D6p:.5f}/0.05 = {P5p:.3f};"
  f" {P5p:.3f}/1.09^5 = {P5p/1.09**5:.4f}; P0 = 54.2831 + {round(pv2, 4)} = {54.2831 + round(pv2, 4):.2f}")
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
a52 = round(annuity_pv(1, 0.02, 5), 5)   # printed a_{5,2%} (A5): five decimals so the printed products reproduce
assert round(3 * a52 + round(zero, 4), 4) == round(coup, 4) and round(a52, 4) == round(coup - 100, 4)
assert round(round(Aam, 4) * a52, 3) == round(amort, 3)
P(f"   printed: a_5,2% = {a52:.5f};  3 x {a52:.5f} + {zero:.4f} = {3*a52 + round(zero, 4):.5f};"
  f"  {Aam:.4f} x {a52:.5f} = {round(Aam, 4)*a52:.5f} -> {round(Aam, 4)*a52:.3f} (true {amort:.5f})")
# YTM by bisection: 10y, 1.5% annual coupon, price 97.20
price0 = 97.20
log = []
ytm, k = bisect(lambda yy: bond_price(yy, 0.015, 10) - price0, 0.0, 0.05, tol=1e-8, log=log)
P(f"YTM 10y 1.5% @97.20: {ytm:.6%} after {k} iterations; check price {bond_price(ytm,0.015,10):.6f}")
for row in log[:8]:
    P("   k={:2d} a={:.6%} b={:.6%} mid={:.6%} P(mid)-price={:+.4f}".format(*row))
P(f"   last: k={log[-1][0]} mid={log[-1][3]:.6%}  bracket width {(log[-1][2]-log[-1][1]):.2e}  (= 0.05/2^{log[-1][0]-1})")
P("   |midpoint - yield| by step (pp):", [(row[0], round(abs(row[3] - ytm) * 100, 4)) for row in log[:6]],
  "-> the error rises from step 3 to step 4; the bracket halves every step")
P(f"   halvings needed for |mid - y| <= 1e-8 from a 0.05 bracket: j = {next(j for j in range(60) if 0.05 / 2 ** (j + 1) <= 1e-8)}"
  f" (2^22 = {2**22:,} < 0.05/1e-8 = {0.05/1e-8:,.0f} <= 2^23 = {2**23:,})")
P(f"   P(0)={bond_price(0,0.015,10):.2f}  P(5%)={bond_price(0.05,0.015,10):.4f}")
# Example: savings insurance IRR (illustrative): pay 100,000 at t=0..5, receive 700,000 at t=10
flows = [(t, -100_000) for t in range(6)] + [(10, 700_000)]
lg = []
irr, k = bisect(lambda x: npv(x, flows), 0.0, 0.10, tol=1e-8, log=lg)
P(f"insurance IRR = {irr:.4%} ({k} iterations)  NPV@1.7% = {npv(0.017, flows):,.0f}  NPV@2.5% = {npv(0.025, flows):,.0f}")
P(f"   midpoint {k} lies within 0.1/2^{k} = {0.1/2**k:.2e} <= 1e-8 of the IRR; midpoint {k-1} only within 0.1/2^{k-1} = {0.1/2**(k-1):.2e}")
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
pmt = amort_payment(L, i, n)
sch = amort_schedule(L, i, n)
tot_int = sum(r_[2] for r_ in sch)
P(f"mortgage: payment {pmt:,.2f} (unrounded {pmt:.6f})  total paid {pmt*n:,.0f}  total interest {tot_int:,.2f} (= n PMT - B0 {pmt*n-L:,.2f})")
for k in (1, 2, 12, 60, 120, 180, 240, 300, 359, 360):
    kk_, pay, I, prin, B = sch[k - 1]
    P(f"   k={k:3d} pay {pay:,.2f}  interest {I:,.2f}  principal {prin:,.2f}  balance {B:,.2f}")
B60 = balance(L, i, n, 60)
P(f"   balance after 60 (6.17) {B60:,.2f};  prospective PV of 300 remaining {annuity_pv(pmt, i, 300):,.2f}")
pmt6 = round(pmt, 6)   # the payment as printed unrounded (A2): both forms of (6.17) must agree from it
assert round(L * (1 + i) ** 60 - pmt6 * ((1 + i) ** 60 - 1) / i, 2) == round(annuity_pv(pmt6, i, 300), 2) == round(B60, 2)
assert round(360 * pmt6 - L, 2) == round(tot_int, 2)
P(f"   from PMT = {pmt6:.6f}: retrospective {L*(1+i)**60 - pmt6*((1+i)**60-1)/i:,.2f}, prospective {annuity_pv(pmt6, i, 300):,.2f},"
  f" 360 PMT - B0 = {360*pmt6 - L:,.2f}")
P(f"   principal ratio check: P2/P1 {sch[1][3]/sch[0][3]:.6f} = 1+i {1+i:.6f};  first principal PMT v^n {pmt*(1+i)**-n:,.2f}")
P(f"   interest share of payment 1: {sch[0][2]/pmt:.4%};  month when principal first exceeds 50% of payment:",
  next(r_[0] for r_ in sch if r_[3] > r_[2]))
P(f"   interest paid in first 5 years {sum(r_[2] for r_ in sch[:60]):,.0f}; principal repaid {L-B60:,.0f}")
# equal principal
sch2 = amort_schedule(L, i, n, method="equal")
tot2 = sum(r_[2] for r_ in sch2)
P(f"equal principal: first {sch2[0][1]:,.2f}  last {sch2[-1][1]:,.2f} (= (B0/n)(1+i) {L/n*(1+i):,.2f})  step {sch2[0][1]-sch2[1][1]:,.4f}"
  f"  total interest {tot2:,.2f} (formula {i*L*(n+1)/2:,.2f})")
P(f"   less interest than level payment {tot_int-tot2:,.2f} (undiscounted);  month where equal-principal payment falls below the level payment:",
  next(r_[0] for r_ in sch2 if r_[1] < pmt))
P(f"   payment 37 (equal principal) {sch2[36][1]:,.2f};  first payment ratio {sch2[0][1]/pmt:.4f};  60 payments {60*pmt:,.0f}")
# grace period 3 years
sch3 = amort_schedule(L, i, n, grace=36)
tot3 = sum(r_[2] for r_ in sch3)
P(f"grace 36m: interest-only {sch3[0][1]:,.2f}  then {sch3[36][1]:,.2f}  total interest {tot3:,.2f}  more than level payment {tot3-tot_int:,.2f}")
assert round(round(tot_int, 2) - round(tot2, 2)) == round(tot_int - tot2) and round(round(tot3, 2) - round(tot_int, 2)) == round(tot3 - tot_int)
# K1: at the loan's own rate every schedule is worth the principal; at another discount rate the ranking depends on it
for lab, j in (("loan rate 2.2%", i), ("1.7% (deposit, illustrative)", 0.017 / 12), ("3%", 0.03 / 12)):
    v1, v2, v3 = (pv_payments(x, j) for x in (sch, sch2, sch3))
    P(f"   PV of payments at {lab}, monthly {j:.6f}: level {v1:,.2f}  equal principal {v2:,.2f} ({v2-v1:+,.2f})"
      f"  grace {v3:,.2f} ({v3-v1:+,.2f})")
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

# ================================================================== practice problems (numbering of the 2026-10 revision)
P("=== PRACTICE PROBLEMS ===")
P("PP1 sum 0.9^k k<20:", round(geo_sum(1, 0.9, 20), 4), "; infinite", round(1 / (1 - 0.9), 4), "; 20 terms that do not shrink: 20")
fv2 = annuity_fv(5000, 0.0015, 120); P(f"PP2 FV {fv2:,.2f}  deposited {5000*120:,}  interest {fv2-600000:,.2f}  PV {annuity_pv(5000,0.0015,120):,.2f}")
pv3d = annuity_pv(2000, 0.025, 15, True); pv3o = annuity_pv(2000, 0.025, 15)
P(f"PP3 annuity due {pv3d:,.2f}  ordinary {pv3o:,.2f}  undiscounted {2000*15:,}")
g4 = (0.08 * 80 - 3.2) / (80 + 3.2); k4 = 3.2 * 1.04 / 80 + 0.04
P(f"PP4 implied g {g4:.4%}; implied k at g=4% {k4:.4%}; check Gordon at g4: {3.2*(1+g4)/(0.08-g4):.4f}")
P(f"PP5 forward P/E {0.6/(0.09-0.05):.2f} (option B); trailing {0.6*1.05/(0.09-0.05):.2f} (C); 0.6/0.05 {0.6/0.05:.2f} (A)")
p6 = bond_price(0.0175, 0.0225, 7)
P(f"PP6 7y 2.25% at 1.75%: {p6:.4f} (option C);  reversed sign 100 - (2.25-1.75) a_7 = {100-(2.25-1.75)*annuity_pv(1,0.0175,7):.2f} (A);"
  f"  at 1.75%: {bond_price(0.0175,0.0175,7):.4f} (B)")
lg7 = []
y7, k7 = bisect(lambda yy: bond_price(yy, 0.02, 3) - 98.0, 0.02, 0.04, tol=1e-9, log=lg7)
for row in lg7[:3]:
    P("PP7 k={:d} a={:.4%} b={:.4%} mid={:.4%} P(mid)-98={:+.4f}".format(*row))
P(f"PP7 YTM {y7:.4%} ({k7} it)  check {bond_price(y7,0.02,3):.6f}")
L8, i8, n8 = 8_000_000, 0.021 / 12, 240
pmt8 = amort_payment(L8, i8, n8); B96 = balance(L8, i8, n8, 96)
I97 = B96 * i8
P(f"PP8 payment {pmt8:,.2f} (unrounded {pmt8:.6f})  balance after 96 {B96:,.2f}  payment 97: interest {I97:,.2f} principal {pmt8-I97:,.2f}"
  f"  (PMT v^(n-96) = {pmt8*(1+i8)**-(n8-96):,.2f})  total interest {pmt8*n8-L8:,.2f}")
pmt8r = round(pmt8, 6)   # A2: the printed unrounded payment reproduces B96 and the total interest to the cent
assert round(annuity_pv(pmt8r, i8, 144), 2) == round(B96, 2) and round(240 * pmt8r - L8, 2) == round(pmt8 * n8 - L8, 2)
s9 = amort_schedule(L8, i8, n8, method="equal")
P(f"PP9 equal principal first {s9[0][1]:,.2f} last {s9[-1][1]:,.2f} (= (8,000,000/240) x 1.00175 = {8_000_000/240*1.00175:,.2f})"
  f" total interest {sum(r_[2] for r_ in s9):,.2f} (formula {i8*L8*(n8+1)/2:,.2f}); level-payment total {pmt8*n8-L8:,.2f};"
  f" difference {pmt8*n8-L8-i8*L8*(n8+1)/2:,.2f}")
s8 = amort_schedule(L8, i8, n8)
for lab, j in (("loan rate 2.1%", i8), ("1.7%", 0.017 / 12), ("3%", 0.03 / 12)):
    P(f"   PP9 PV of payments at {lab}: level {pv_payments(s8, j):,.2f}  equal principal {pv_payments(s9, j):,.2f}"
      f"  ({pv_payments(s9, j) - pv_payments(s8, j):+,.2f})")
S10, iT, iU, T = 31.20, 0.015, 0.042, 0.25
F10 = S10 * (1 + iT * T) / (1 + iU * T)
P(f"PP10 3m forward {F10:.4f}  points {F10-S10:+.4f}  approx {S10*(1+(iT-iU)*T):.4f}")
S11, tau, r, qt = 23_000, 0.2, 0.02, 0.012
Ff = S11 * math.exp(r * tau - qt); F11 = 22_600
P(f"PP11 fair {Ff:.2f} basis {Ff-S11:.2f}; at F=22600: implied qtau {r*tau-math.log(F11/S11):.4%} residual {F11-Ff:.2f}"
  f" implied financing rate {(qt+math.log(F11/S11))/tau:.4%}")
P("PP12: from data/lm06_basis.py (SEP rows)")

# ================================================================== intermediate values shown in worked solutions
P("=== INTERMEDIATES ===")
P(f"S2 compound 100*1.02^2 = {100*1.02**2:.2f}")
P(f"Savings example (b): PV i/A = {10_000_000*0.0025/60_000:.5f}; 1 - that = {1-10_000_000*0.0025/60_000:.5f}; ln(1.0025) = {math.log(1.0025):.7f}")
P(f"0050 example: (0.08*114.95 - 1.60) = {0.08*114.95-1.60:.3f}; 114.95 + 1.60 = {114.95+1.60:.2f}; 1.0843/1.0994 = {1.0843/1.0994:.6f}; ^30 = {(1.0843/1.0994)**30:.4f}")
P(f"KC5 (2-2.5)*a_3(2.5%) = {(2-2.5)*annuity_pv(1,0.025,3):.4f}")
P(f"Mortgage example: i = 0.022/12; first interest 10,000,000*0.022/12 = {10_000_000*0.022/12:,.2f}; equal-principal interest"
  f" (0.022/12)*10,000,000*361/2 = {0.022/12*10_000_000*361/2:,.2f}; principal B0/n {10_000_000/360:,.2f}")
P(f"FX example (b) 30*1.04 forward delivery {1.04*29.50:.2f}; repay 30*1.016 = {30*1.016:.2f}")
P(f"Insurance example: premiums shortfall {700_000 - sum(100_000*1.017**(10-t) for t in range(6)):,.0f}")
tau = 173 / 365
P(f"December example: r*tau = {0.02*tau:.7f}; -ln(21700/22580.08) = {-math.log(21700/22580.08):.5f}; tau = {tau:.5f}")
P(f"KC Section 8, Sep->Dec: r*dtau = {0.02*91/365:.6f}; -ln(21700/21834) = {-math.log(21700/21834):.6f};"
  f" printed sum {round(0.02*91/365, 6) + round(-math.log(21700/21834), 6):.6f}")
P(f"PP4 0.08*80-3.20 = {0.08*80-3.2:.2f}; 80+3.20 = {80+3.2:.2f}; 1+g = {1+(0.08*80-3.2)/(80+3.2):.5f}; D1/P0 at 4% = {3.2*1.04/80:.2%}")
P(f"PP6 (2.25-1.75)*a_7(1.75%) = {(2.25-1.75)*annuity_pv(1,0.0175,7):+.2f}; option A = {100-(2.25-1.75)*annuity_pv(1,0.0175,7):.2f}")
P(f"PP8/9 monthly rate {0.021/12:.3%}; L/n = {8_000_000/240:,.2f}; first interest {8_000_000*0.021/12:,.2f}; 1+i = {1+0.021/12:.5f}")
P(f"PP2 1+i = {1.0015}; PP3 a_15(2.5%) = {annuity_pv(1,0.025,15):.4f}")
P(f"Section 6 text: doubling time at 2.2% {math.log(2)/math.log(1+0.022/12):.1f} months; at 5% {math.log(2)/math.log(1+0.05/12):.1f} months")
