"""Check Book.dist, Book.rng and the sci/sig/n6 codes of Book.fmt (src/assets/book.js) against SciPy.

book.js runs in Node (a bare `window` and `document` stand in for the browser, so the page code never starts). Every
distribution function is evaluated on a grid and compared with SciPy. Where the two differ by more than the tolerance,
mpmath at 40 digits decides: SciPy is not exact either (its poisson.pmf loses digits for large λ, its norm.cdf in the far
tail), and the error that counts is book.js against mpmath at those points. For the normal distribution the whole grid
is also compared with mpmath. Prints a table of the largest errors; exits with status 1 when a check fails.

    uv run python build/qa/test_bookjs_dist.py
"""
import io
import json
import math
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import mpmath
import numpy as np
from scipy import special, stats

BOOK_JS = Path(__file__).resolve().parents[2] / "src" / "assets" / "book.js"
TINY = 1e-290   # below this a reference counts as underflow: only |got| <= 1e-280 is required there
mpmath.mp.dps = 40
mpf = mpmath.mpf

# reads {"dist": [[name, [args...]], ...], "rng": [...], "fmt": [[value, code], ...]} on stdin, prints the results;
# non-finite numbers travel as the strings "Infinity", "-Infinity", "NaN"
DRIVER = r"""
const vm = require("vm"), fs = require("fs");
const ctx = { window: {}, document: { readyState: "loading", addEventListener() {} }, console };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[1], "utf8"), ctx);
const B = ctx.window.Book, q = JSON.parse(fs.readFileSync(0, "utf8")), out = {};
out.dist = q.dist.map(([f, args]) => args.map(a => B.dist[f](...a)));
out.rng = q.rng.map(([seed, kind, n, arg]) => {
  const r = B.rng(seed), v = [];
  for (let i = 0; i < n; i++) v.push(kind === "int" ? r.int(arg) : r[kind]());
  return v;
});
out.fmt = q.fmt.map(([v, f]) => B.fmt(v, f));
out.seeds = [undefined, null, NaN, Infinity, "abc", "7", 2026.7, -1, 2 ** 40].map(s => {   // what Book.rng(seed) throws
  try { B.rng(s); return "accepted"; } catch (e) { return e.constructor.name; }
});
process.stdout.write(JSON.stringify(out, (k, v) => typeof v === "number" && !isFinite(v) ? String(v) : v));
"""


def run_js(query):
    r = subprocess.run(["node", "-e", DRIVER, str(BOOK_JS)], input=json.dumps(query), capture_output=True,
                       text=True, encoding="utf-8", check=False)
    if r.returncode:
        sys.exit(f"node failed:\n{r.stderr}")
    return json.loads(r.stdout)


def num(a):
    return np.array([float(v) for v in a])


def rel_err(got, ref):
    """Relative error where |ref| >= TINY; where the reference underflows, 0 if |got| <= 1e-280 else inf."""
    got, ref = np.asarray(got, float), np.asarray(ref, float)
    err = np.zeros(len(ref))
    big = np.abs(ref) >= TINY
    with np.errstate(divide="ignore", invalid="ignore"):
        err[big] = np.abs(got[big] - ref[big]) / np.abs(ref[big])
    err[~big] = np.where(np.abs(got[~big]) <= 1e-280, 0.0, np.inf)
    err[got == ref] = 0.0
    return err


def mixed_err(got, ref):
    """|got − ref| / max(1, |ref|): relative for large values, absolute near a zero of the function."""
    got, ref = np.asarray(got, float), np.asarray(ref, float)
    return np.abs(got - ref) / np.maximum(1.0, np.abs(ref))


def t_lower(x, nu):   # Pr(T <= x) in mpmath
    w = mpf(nu) / (mpf(nu) + mpf(x) ** 2)
    tail = mpmath.betainc(mpf(nu) / 2, mpf(1) / 2, 0, w, regularized=True) / 2
    return tail if x < 0 else 1 - tail


def phi_inv(p):   # on the log scale, so that it also works for p below the smallest normal double
    start = float(special.ndtri(p))
    start = start if math.isfinite(start) else -math.sqrt(-2 * math.log(p))
    return mpmath.findroot(lambda x: mpmath.log(mpmath.ncdf(x)) - mpmath.log(mpf(p)), start)


def abs_err(got, ref):
    return np.abs(np.asarray(got, float) - np.asarray(ref, float))


TRUTH: dict[str, Callable[..., Any]] = {   # the same functions in mpmath, for the points where SciPy and book.js disagree
    "phi": lambda z: mpmath.npdf(mpf(z)),
    "Phi": lambda z: mpmath.ncdf(mpf(z)),
    "PhiInv": lambda p: -phi_inv(1 - p) if p > 0.5 else phi_inv(p),
    "lgamma": lambda x: mpmath.loggamma(mpf(x)),
    "tPdf": lambda x, nu: mpmath.exp(mpmath.loggamma((mpf(nu) + 1) / 2) - mpmath.loggamma(mpf(nu) / 2))
    / mpmath.sqrt(mpf(nu) * mpmath.pi) * (1 + mpf(x) ** 2 / nu) ** (-(mpf(nu) + 1) / 2),
    "tCdf": t_lower,
    "poissonPmf": lambda k, lam: mpmath.exp(k * mpmath.log(mpf(lam)) - lam - mpmath.loggamma(k + 1)),
    "poissonCdf": lambda k, lam: mpmath.gammainc(k + 1, mpf(lam), mpmath.inf, regularized=True),
    "binomPmf": lambda k, n, p: mpmath.binomial(n, k) * mpf(p) ** k * (1 - mpf(p)) ** (n - k),
    "chi2Cdf": lambda x, k: mpmath.gammainc(mpf(k) / 2, 0, mpf(x) / 2, regularized=True),
}

# ---------------------------------------------------------------- the grids and their SciPy references
z_all = np.concatenate([np.linspace(-37, 37, 4001), [-4.1074386, -0.67448975, 0.67448975, -5.656854249492381,
                                                       -5.6568542494923815, 0.0, 1e-300, -1e-10, -36.99]])
p_inv = np.concatenate([np.logspace(-300, np.log10(0.5), 3001), 1 - np.logspace(-16, np.log10(0.5), 1001),
                        0.5 + np.logspace(-16, -1, 151), 0.5 - np.logspace(-16, -1, 151), [0.5, 0.02425, 0.97575]])
p_sub = np.concatenate([np.logspace(-323.3, np.log10(2.2e-308), 60), [5e-324, 2e-308]])   # below the smallest normal
x_lg = np.concatenate([np.logspace(-12, 12, 2001), np.linspace(0.5, 3, 501), [0.5, 1.0, 1.5, 2.0]])
near = np.logspace(-14, -1, 80)
x_lz = np.concatenate([1 - near, 1 + near, 2 - near, 2 + near, [1.0, 2.0]])   # where log Γ crosses 0
x_t = np.concatenate([-np.logspace(-6, 6, 241), [0.0], np.logspace(-6, 6, 121)])
LAMS = [1e-3, 0.1, 0.5, 1, 2.5, 7, 20, 100, 1000, 1e4]
NS, PS = [1, 2, 5, 10, 50, 250, 1000, 5000], [1e-4, 0.01, 0.1, 0.3, 0.5, 0.73, 0.99, 0.9999]
KS_CHI = [0.5, 1, 2, 3, 4, 5, 10, 30, 100, 1000, 1e4]


def cols(rows):
    return [list(c) for c in zip(*rows, strict=True)]


cases = []   # (function, domain, args, SciPy values, error function, metric, tolerance)
cases.append(("phi", "z in [−37, 37]", [[z] for z in z_all], stats.norm.pdf(z_all), rel_err, "rel", 1e-12))
cases.append(("Phi", "z in [−37, 37]", [[z] for z in z_all], special.ndtr(z_all), rel_err, "rel", 1e-12))
cases.append(("PhiInv", "p in [1e−300, 1 − 1.1e−16]", [[p] for p in p_inv], special.ndtri(p_inv), rel_err, "rel", 1e-12))
cases.append(("PhiInv", "p in [5e−324, 2.2e−308): Acklam only", [[p] for p in p_sub], special.ndtri(p_sub), rel_err, "rel", 2e-9))
cases.append(("lgamma", "x in [1e−12, 1e12]", [[x] for x in x_lg], special.gammaln(x_lg), mixed_err, "mixed", 1e-13))
cases.append(("lgamma", "x within 0.1 of 1 and 2 (log Γ near 0)", [[x] for x in x_lz], special.gammaln(x_lz), abs_err, "abs", 5e-15))
# tCdf: the continued fraction loses accuracy about in proportion to ν, and above ν = 1e8 the normal approximation of
# A&S 26.7.8 takes over, whose error is largest just above the switch, in the far tail (about 1e-8 at x = −37)
T_GROUPS = (([0.1, 0.5, 1, 1.5, 2, 3, 4.5, 10, 30, 100, 1e3, 1e4], 1e-12, 1e-12), ([1e5, 1e6], 1e-12, 1e-10),
            ([1e8, 1.01e8, 2e8, 1e9, 1e10, 1e12, 1e14, 1e15, 1e16, 1e17], 1e-12, 2e-8))
for nus, tol_pdf, tol_cdf in T_GROUPS:
    t_args = [(x, nu) for nu in nus for x in x_t]
    xs, ns = cols(t_args)
    dom = f"ν {nus[0]:g}..{nus[-1]:g}, |x| 1e−6..1e6"
    cases.append(("tPdf", dom, [list(a) for a in t_args], stats.t.pdf(xs, ns), rel_err, "rel", tol_pdf))
    cases.append(("tCdf", dom, [list(a) for a in t_args], special.stdtr(ns, xs), rel_err, "rel", tol_cdf))
# Poisson and binomial: far in a tail the probability is e^−(a few hundred), and its relative error is about k ulps
# (the rounding of k/λ inside Loader's bd0, multiplied by k): 2e-12 covers k up to 1e4
pois = [(k, lam) for lam in LAMS for k in range(int(lam + 12 * math.sqrt(lam) + 25))]
ks, ls = cols(pois)
cases.append(("poissonPmf", "λ 1e−3..1e4, k 0..λ + 12√λ + 25", [list(a) for a in pois], stats.poisson.pmf(ks, ls),
              rel_err, "rel", 2e-12))
cases.append(("poissonCdf", "the same grid", [list(a) for a in pois], stats.poisson.cdf(ks, ls), rel_err, "rel", 2e-12))
binom = [(k, n, p) for n in NS for p in PS for k in range(n + 1)]
kb, nb, pb = cols(binom)
cases.append(("binomPmf", "n 1..5000, p 1e−4..0.9999, all k", [list(a) for a in binom], stats.binom.pmf(kb, nb, pb),
              rel_err, "rel", 2e-12))
chi = [(x, k) for k in KS_CHI for x in np.concatenate([[1e-10], k * np.logspace(-3, 1.5, 200)])]
xc, kc = cols(chi)
cases.append(("chi2Cdf", "k 0.5..1e4, x/k 1e−3..30", [list(a) for a in chi], stats.chi2.cdf(xc, kc), rel_err, "rel", 1e-12))

# ---------------------------------------------------------------- the random numbers and the format codes
SEED = 2026
rng_q = [[SEED, "uniform", 200000, None], [SEED, "uniform", 200000, None], [SEED, "normal", 200000, None],
         [SEED, "normal", 200000, None], [SEED, "int", 70000, 7], [7, "uniform", 5, None], [2**32 + 7, "uniform", 5, None],
         [SEED, "int", 20000, 2**32], [SEED, "uniform", 3, None], [SEED, "normal", 3, None]]
# the first numbers for seed 2026, pinned: a change to the generator shows here before it changes a widget
PINNED_U = [0.17210804602121343, 0.12454267537089636, 0.5156590064802732]
PINNED_N = [-0.07261409412934218, -0.0831477966486868, 0.49182617315333926]
FMT = [(2.000355e-5, "sci2", "2.00e−5"), (-2.000355e-5, "sci1", "−2.0e−5"), (9.996e-5, "sci2", "1.00e−4"),
       (12345.0, "sci1", "1.2e4"), (1.0, "sci3", "1.000e0"), (0.0, "sci2", "0"), (3e-7, "sci0", "3e−7"),
       (-123456.789, "sig3", "−123,000"), (0.000123456, "sig2", "0.00012"), (1.5, "sig3", "1.50"),
       (1.2, "sig3", "1.20"), (0.0009995, "sig3", "0.00100"), (1234.5678, "sig4", "1,235"), (0.0, "sig2", "0.0"),
       (0.0, "sig3", "0.00"), (999999.7, "sig3", "1.00e6"), (1234567.0, "sig3", "1.23e6"), (999499.0, "sig3", "999,000"),
       (0.00009996, "sig3", "0.000100"), (0.0000123, "sig2", "1.2e−5"), (-3.21e-9, "sig2", "−3.2e−9"),
       (0.1234567, "n6", "0.123457")]
SEEDS = ["TypeError", "TypeError", "RangeError", "RangeError", "TypeError", "TypeError", "RangeError", "accepted", "accepted"]

res = run_js({"dist": [[c[0], c[2]] for c in cases], "rng": rng_q, "fmt": [[v, f] for v, f, _ in FMT]})

# ---------------------------------------------------------------- report
if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")   # the table has − and ν; a Windows console defaults to cp950
failed = []
print("Largest error of book.js against SciPy, and arbitrated: where the two differ by more than 1/100 of the tolerance,\n"
      "the error of book.js against mpmath (40 digits) counts instead; 'mpmath' is the number of such points\n")
print(f"{'function':<11} {'domain':<35} {'points':>6} {'metric':>6} {'vs SciPy':>10} {'arbitrated':>11} "
      f"{'tolerance':>9} {'mpmath':>6}  worst point")
for (name, dom, args, ref, errf, metric, tol), got in zip(cases, res["dist"], strict=True):
    got = num(got)
    err = errf(got, ref)
    final = err.copy()
    hard = np.flatnonzero(err > tol / 100)   # SciPy and book.js disagree: book.js against mpmath counts there
    for j in hard:
        final[j] = errf([got[j]], [float(TRUTH[name](*args[j]))])[0]
    i = int(np.argmax(final))
    ok = bool(final[i] <= tol)
    if not ok:
        failed.append(name)
    worst = ", ".join(f"{float(a):.6g}" for a in args[i])
    print(f"{name:<11} {dom:<35} {len(args):>6} {metric:>6} {err.max():>10.2e} {final[i]:>11.2e} {tol:>9.0e} {len(hard):>6}  "
          f"({worst}){'' if ok else '   FAIL'}")

print("\nThe normal distribution against mpmath on the whole grid (largest relative error):")
lo_half = p_inv[p_inv <= 0.5]
normal = (("phi", z_all, num(res["dist"][0]), stats.norm.pdf(z_all)), ("Phi", z_all, num(res["dist"][1]), special.ndtr(z_all)),
          ("PhiInv", lo_half, num(res["dist"][2])[p_inv <= 0.5], special.ndtri(lo_half)))
for name, grid, got, sp in normal:
    mp = np.array([float(TRUTH[name](v)) for v in grid])
    e_js, e_sp = rel_err(got, mp).max(), rel_err(sp, mp).max()
    print(f"  {name:<7} book.js {e_js:.2e}   SciPy {e_sp:.2e}")
    if e_js > 1e-12:
        failed.append(name + " vs mpmath")
lm5 = num(res["dist"][1])[list(z_all).index(-4.1074386)]
print(f"\nPhi(−4.1074386) = {lm5:.7e} (LM5 quotes 2.000355e-5)")
if f"{lm5:.6e}" != "2.000355e-05":
    failed.append("Phi LM5 value")

u1, u2, n1, n2, ints, s7, s7b, big, u3, n3 = (np.array(v, dtype=float) for v in res["rng"])
checks = [
    ("same seed, same uniforms", bool(np.array_equal(u1, u2))),
    ("same seed, same normals", bool(np.array_equal(n1, n2))),
    ("first numbers for seed 2026 as pinned", bool(list(u3) == PINNED_U and list(n3) == PINNED_N)),
    ("seed taken modulo 2^32", bool(np.array_equal(s7, s7b))),
    ("uniform in [0, 1)", bool(u1.min() >= 0 and u1.max() < 1)),
    ("uniform: Kolmogorov-Smirnov p > 0.001", bool(stats.kstest(u1, "uniform").pvalue > 1e-3)),
    ("normal: Kolmogorov-Smirnov p > 0.001", bool(stats.kstest(n1, "norm").pvalue > 1e-3)),
    ("normal: mean and variance within 4 standard errors", bool(abs(n1.mean()) < 4 / math.sqrt(len(n1))
                                                                and abs(n1.var() - 1) < 4 * math.sqrt(2 / len(n1)))),
    ("int(7) covers 0..6 evenly (chi-square p > 0.001)", bool(set(np.unique(ints)) == set(range(7)) and
                                                             stats.chisquare(np.bincount(ints.astype(int))).pvalue > 1e-3)),
    ("int(2^32) in 0..2^32 − 1, whole numbers", bool(big.min() >= 0 and big.max() <= 2**32 - 1 and np.all(big == np.floor(big)))),
    ("seed undefined, null, NaN, Infinity, 'abc', '7', 2026.7 throw; −1 and 2^40 accepted", res["seeds"] == SEEDS),
]
print(f"\nBook.rng (seed {SEED}):")
for label, ok in checks:
    print(f"  {'ok  ' if ok else 'FAIL'} {label}")
    if not ok:
        failed.append("rng: " + label)
print("\nBook.fmt:")
for (v, f, want), got in zip(FMT, res["fmt"], strict=True):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'} fmt({v!r}, {f!r}) = {got!r}" + ("" if ok else f", want {want!r}"))
    if not ok:
        failed.append(f"fmt {f}")

if failed:
    sys.exit("\nFAILED: " + ", ".join(failed))
print("\nall checks passed")
