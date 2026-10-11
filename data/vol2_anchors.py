"""Volume II anchors: the facts the Volume II (Linear Algebra for Portfolios, LM8-LM12) briefs will rely on.

This is the editor's exploration for the Volume II briefs, not a published module's script. It computes, from
data/processed/vol2_closes.parquet (TAIEX, 28 leaf sector indices, 2 aggregate indices: the FinMind chunks in
raw/sectors/ with the wrongly served closes repaired and every row validated by data/vol2_series.py, which must be
run first) and from Volume I's raw ETF and TX files:

  (a) the common sample of TAIEX + the 28 leaf sectors (dates, T, years, A) and every series' missing days;
  (b) PCA of the correlation and covariance matrices of S15 and of all 28 leaves (eigenvalues, shares,
      first three loadings, condition numbers, extreme pairs);
  (c) Electronic against its eight sub-industries (OLS, per calendar year; 9x9 correlation spectrum);
  (d) TAIEX against the 28 leaves (OLS: full sample, per calendar year, last 250 returns);
  (e) the first eigenvalue share of S15's correlation matrix per calendar year;
  (f) estimation error: Sigma_hat x = 1 solved in two half samples (S15 and 5 sectors);
  (g) Cholesky factor of the 5-sector Sigma_hat and a simulation check (default_rng(20261011));
  (h) LM8's P&L case, 2025-04-07 (0050 and the front-month TX), q^T dP;
  (i) pairwise deletion against the common sample for S15 + 0050 + 00631L + 00679B.

Conventions: daily simple returns R_t = close_t / close_{t-1} - 1 between consecutive trading dates of the
TAIEX calendar; sample covariance divides by T (ddof=0); years = calendar days between the first and last
date / 365.25; A = number of returns / years. Sector indices are price indices.

Run:  PYTHONUTF8=1 uv run python data/vol2_series.py && PYTHONUTF8=1 uv run python data/vol2_anchors.py
Writes data/processed/vol2_anchors.txt (git-ignored) and prints the same report.
"""
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np
import polars as pl
from numpy.typing import NDArray

Mat = NDArray[np.float64]

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
SECT = RAW / "sectors"
CLOSES = HERE / "processed" / "vol2_closes.parquet"
REPAIRS = HERE / "processed" / "vol2_repairs.json"
OUT = HERE / "processed" / "vol2_anchors.txt"

AGGREGATES = ["Electronic", "ChemicalBiotechnologyMedicalCare"]
S15 = ["Semiconductor", "ComputerPeripheralEquipment", "Optoelectronic", "CommunicationsInternet",
       "ElectronicPartsComponents", "FinancialInsurance", "ShippingTransportation", "Plastics", "IronSteel",
       "Cement", "Food", "Textiles", "BuildingMaterialConstruction", "OilGasElectricity",
       "BiotechnologyMedicalCare"]
S5 = ["Semiconductor", "FinancialInsurance", "Plastics", "ShippingTransportation", "Food"]
ELEC8 = ["Semiconductor", "ComputerPeripheralEquipment", "Optoelectronic", "CommunicationsInternet",
         "ElectronicPartsComponents", "ElectronicProductsDistribution", "InformationService", "OtherElectronic"]
ETFS = ["0050", "00631L", "00679B"]
SPLITS = {"0050": "2025-06-18", "00631L": "2026-03-31"}   # effective dates (data/README.md, PITFALLS 3)
SEED = 20261011
M_TX = 200            # NT$ per index point

LINES: list[str] = []


def out(s: str = "") -> None:
    LINES.append(s)
    print(s)


def g(x: float | np.floating, n: int = 7) -> str:
    return f"{float(x):.{n}g}"


def section(title: str) -> None:
    out()
    out("=" * 100)
    out(title)
    out("=" * 100)


# ------------------------------------------------------------------ loading
def load_chunks(folder: Path, name: str) -> pl.DataFrame:
    files = sorted(folder.glob(f"{name}__*.csv"))
    assert files, f"no files for {name}"
    df = pl.concat([pl.read_csv(f, schema_overrides={"spread": pl.Float64, "close": pl.Float64}) for f in files])
    assert df["date"].n_unique() == df.height, f"{name}: duplicate dates across chunks"
    return df.sort("date")


def spread_mismatches(df: pl.DataFrame) -> int:
    """Rows whose close minus previous close differs from the spread column by more than 0.011."""
    d = df.with_columns((pl.col("close") - pl.col("close").shift(1) - pl.col("spread")).abs().alias("gap"))
    return int(d.filter(pl.col("gap") > 0.011).height)


def to_mat(df: pl.DataFrame, cols: list[str]) -> Mat:
    return np.asarray(df.select(cols).to_numpy(), dtype=np.float64)


def cov0(x: Mat) -> Mat:
    xc = x - x.mean(axis=0)
    return xc.T @ xc / x.shape[0]


def corr_of(c: Mat) -> Mat:
    d = np.sqrt(np.diag(c))
    return c / np.outer(d, d)


def eig_desc(a: Mat) -> tuple[NDArray[np.float64], Mat]:
    w, v = np.linalg.eigh(a)
    idx = np.argsort(w)[::-1]
    return w[idx], v[:, idx]


def sign_fix(v: NDArray[np.float64]) -> NDArray[np.float64]:
    return v * np.sign(v[int(np.argmax(np.abs(v)))])


@dataclass
class Fit:
    beta: NDArray[np.float64]
    r2: float
    sd0: float
    sd_dof: float
    adj_r2: float
    T: int
    k: int


def ols(y: NDArray[np.float64], x: Mat) -> Fit:
    t, k = x.shape
    design = np.column_stack([np.ones(t), x])
    beta, *_ = np.linalg.lstsq(design, y, rcond=None)
    resid = y - design @ beta
    rss = float(resid @ resid)
    tss = float(((y - y.mean()) ** 2).sum())
    return Fit(beta=beta, r2=1 - rss / tss, sd0=float(np.sqrt(rss / t)),
               sd_dof=float(np.sqrt(rss / (t - k - 1))) if t > k + 1 else float("nan"),
               adj_r2=1 - (rss / (t - k - 1)) / (tss / (t - 1)) if t > k + 1 else float("nan"), T=t, k=k)


def build() -> tuple[pl.DataFrame, pl.DataFrame, list[str], list[str]]:
    names = sorted({p.name.split("__")[0] for p in SECT.glob("*.csv")})
    assert "TAIEX" in names
    sectors = [n for n in names if n != "TAIEX"]
    leaves = [n for n in sectors if n not in AGGREGATES]
    assert len(sectors) == 30 and len(leaves) == 28, (len(sectors), len(leaves))
    assert all(a in sectors for a in AGGREGATES)
    assert all(s in leaves for s in S15)

    # The sector closes come from data/vol2_series.py, which repairs the closes FinMind served wrongly (13:30:00 value of
    # TaiwanStockEvery5SecondsIndex, raw/sectors_close/) and validates every row.
    assert CLOSES.exists() and REPAIRS.exists(), "run data/vol2_series.py first"
    cdf = pl.read_parquet(CLOSES).sort("date")
    assert sorted(cdf.columns[1:]) == names, "vol2_closes.parquet does not hold the series of raw/sectors/"
    cdf = cdf.select("date", *names)
    master = cdf.select("date")
    wide = cdf
    dts = wide["date"].to_list()
    rep = json.loads(REPAIRS.read_text(encoding="utf-8"))
    out(f"[data] sector closes: {len(names)} series incl. TAIEX from data/processed/vol2_closes.parquet (built by "
        f"data/vol2_series.py); master calendar = TAIEX {master.height} dates {dts[0]}..{dts[-1]}")
    n_dates = len({r["date"] for r in rep["repairs"]})
    out(f"[data] {len(rep['repairs'])} served closes replaced by the 13:30:00 value of TaiwanStockEvery5SecondsIndex on "
        f"{n_dates} dates ({rep['confirmed_total']} further 13:30:00 values, recorded when fetched, confirmed the served close); "
        "no close is dropped or estimated")
    c_cl = to_mat(cdf, sectors)
    r_cl = c_cl[1:] / c_cl[:-1] - 1
    out(f"[data] largest |daily return| over the 30 sector series: {np.nanmax(np.abs(r_cl)):.4%}; "
        f"count above 10.5%: {int((np.nan_to_num(np.abs(r_cl)) > 0.105).sum())}")
    tr = to_mat(wide, ["TAIEX"])[:, 0]
    out(f"[data] TAIEX largest |daily return| = {np.nanmax(np.abs(tr[1:] / tr[:-1] - 1)):.4%}")

    mism = {}
    for e in ETFS:
        etf = load_chunks(RAW, e)
        mism[e] = spread_mismatches(etf)
        off = sorted(set(etf["date"].to_list()) - set(master["date"].to_list()))
        out(f"[data] {e}: {etf.height} closes {etf['date'][0]}..{etf['date'][-1]}; dates outside the TAIEX calendar: {len(off)} {off[:5]}")
        cdf = cdf.join(etf.select("date", pl.col("close").alias(e)), on="date", how="left")
    cdf = cdf.sort("date")
    out(f"[data] ETF rows where close - previous close differs from `spread`: {mism} (ex-dividend days, where FinMind "
        "prints spread 0.0, and split days)")

    ret = cdf.with_columns([(pl.col(c) / pl.col(c).shift(1) - 1).alias(c) for c in cdf.columns if c != "date"])
    for e, sd in SPLITS.items():                       # the return that spans a split is not a price return
        ret = ret.with_columns(pl.when(pl.col("date") == sd).then(None).otherwise(pl.col(e)).alias(e))
    ret = ret.with_columns(pl.col("date").shift(1).alias("prev_date"),
                           pl.col("date").str.slice(0, 4).cast(pl.Int32).alias("year"))
    return cdf, ret, leaves, names


def smp(ret: pl.DataFrame, cols: list[str]) -> pl.DataFrame:
    """The common sample of the series used: returns between consecutive TAIEX-calendar dates, both closes present."""
    return ret.filter(pl.all_horizontal([pl.col(c).is_not_null() for c in cols]))


def sample_line(label: str, rr: pl.DataFrame) -> None:
    ds = sorted(set(rr["date"].to_list()) | set(rr["prev_date"].to_list()))
    yrs = (date.fromisoformat(ds[-1]) - date.fromisoformat(ds[0])).days / 365.25
    out(f"sample for {label}: {len(ds)} dates {ds[0]}..{ds[-1]}; T = {rr.height} returns "
        f"(first return {rr['date'][0]}); years = {g(yrs, 10)}; A = T/years = {g(rr.height / yrs, 10)}")


def main() -> None:
    wide, ret, leaves, names = build()
    close_cols = ["TAIEX", *leaves]

    # -------------------------------------------------------------- (a)
    section("(a) Common sample of TAIEX + the 28 leaf sectors")
    for n in names:
        miss = wide.filter(pl.col(n).is_null())["date"].to_list()
        if miss:
            out(f"series {n}: {len(miss)} master dates without a close, first {miss[0]}, last {miss[-1]}")
    out("missing dates of TradingConsumersGoods (it has only 2007-11-08, 2008-01-25 and 2008-09-05 before its "
        "contiguous run from 2008-12-01; the three stray closes give no one-day return):")
    miss = wide.filter(pl.col("TradingConsumersGoods").is_null())["date"].to_list()
    tcg = [d for d in miss if d < "2008-12-01"]
    for i in range(0, len(tcg), 10):
        out("    " + " ".join(tcg[i:i + 10]))
    out(f"  ({len(tcg)} dates before 2008-12-01; {len(miss) - len(tcg)} missing dates from 2008-12-01 on)")
    rr = smp(ret, close_cols)
    sample_line("TAIEX + 28 leaves (the (a) sample)", rr)
    ds_ = sorted(set(rr["date"].to_list()) | set(rr["prev_date"].to_list()))
    cal = [d for d in wide["date"].to_list() if d >= ds_[0]]
    out(f"master-calendar dates from {ds_[0]}: {len(cal)}; dates in the sample: {len(ds_)}; returns lost to missing "
        f"closes (no valid close on t or t-1): {len(cal) - 1 - rr.height}")
    out("for comparison: S15 alone (own sample) " + "; ".join(
        [f"T = {smp(ret, S15).height} from {smp(ret, S15)['prev_date'][0]}"]))
    out("all analyses use one-day returns only; each analysis uses the common sample of the series it uses "
        "(its own sample_line is printed)")
    t = rr.height
    xall = to_mat(rr, leaves)
    ytx = to_mat(rr, ["TAIEX"])[:, 0]
    dates = rr["date"].to_list()
    years_col = rr["year"].to_numpy()
    r15 = smp(ret, S15)
    xs15 = to_mat(r15, S15)
    years15 = r15["year"].to_numpy()
    r5 = smp(ret, S5)
    x5 = to_mat(r5, S5)
    relec = smp(ret, ["Electronic", *ELEC8])

    # -------------------------------------------------------------- (b)
    section("(b) PCA of the correlation and covariance matrices")

    def pca_block(label: str, cols: list[str], x: Mat) -> None:
        out()
        out(f"--- {label}: {len(cols)} series, T = {x.shape[0]} ---")
        c = cov0(x)
        r = corr_of(c)
        for mname, m in (("correlation", r), ("covariance (daily, ddof=0)", c)):
            w, v = eig_desc(m)
            out(f"{mname} matrix eigenvalues (descending), explained share, cumulative share:")
            cum = 0.0
            tot = float(w.sum())
            for i in range(len(w)):
                wi = float(w[i])
                cum += wi / tot
                fmt = g(wi, 8) if mname == "correlation" else f"{wi:.8e}"
                out(f"  {i + 1:2d}  {fmt:>16s}  {g(wi / tot, 8):>12s}  {g(cum, 8):>12s}")
            out(f"  trace = {g(float(w.sum()), 10)}; condition number lambda_max/lambda_min = {g(float(w[0] / w[-1]), 8)} "
                f"(np.linalg.cond = {g(float(np.linalg.cond(m)), 8)})")
            if mname == "correlation":
                out("first three eigenvectors of the correlation matrix (sign: largest |entry| positive), loadings by sector:")
                vecs = [sign_fix(v[:, k]) for k in range(3)]
                out(f"  {'sector':32s}{'PC1':>12s}{'PC2':>12s}{'PC3':>12s}")
                for i, nme in enumerate(cols):
                    out(f"  {nme:32s}" + "".join(f"{vecs[k][i]:12.6f}" for k in range(3)))
        pairs = sorted(((r[i, j], cols[i], cols[j]) for i in range(len(cols)) for j in range(i)), reverse=True)
        out("three most correlated pairs:")
        for rho, a, b in pairs[:3]:
            out(f"  {g(float(rho), 8)}  {a} / {b}")
        out("three least correlated pairs:")
        for rho, a, b in pairs[::-1][:3]:
            out(f"  {g(float(rho), 8)}  {a} / {b}")

    sample_line("S15 (own sample)", r15)
    pca_block("S15 on its own sample", S15, xs15)
    sample_line("all 28 leaves ((a) sample)", rr)
    pca_block("all 28 leaves", leaves, xall)
    out()
    out("--- extra: S15 on the (a) sample (the 28-leaf dates), top of the spectrum only ---")
    xs15a = to_mat(rr, S15)
    ca = cov0(xs15a)
    wr, _ = eig_desc(corr_of(ca))
    wc_, _ = eig_desc(ca)
    out(f"T = {xs15a.shape[0]}; correlation eigenvalues 1-3: {' '.join(g(float(v), 8) for v in wr[:3])}; "
        f"shares 1-3: {' '.join(g(float(v / 15), 8) for v in wr[:3])}; lambda_min = {g(float(wr[-1]), 8)}; "
        f"cond = {g(float(wr[0] / wr[-1]), 8)}; covariance cond = {g(float(wc_[0] / wc_[-1]), 8)}")

    # -------------------------------------------------------------- (c)
    section("(c) Electronic against its eight electronics sub-industries (OLS with intercept)")
    sample_line("Electronic + its eight sub-industries (own sample)", relec)
    ye = to_mat(relec, ["Electronic"])[:, 0]
    x8 = to_mat(relec, ELEC8)
    tc_ = relec.height
    yc = relec["year"].to_numpy()
    short = [s[:9] for s in ELEC8]
    out("regressors (in order): " + ", ".join(ELEC8))

    def reg_row(label: str, mask: NDArray[np.bool_]) -> None:
        f = ols(ye[mask], x8[mask])
        b = f.beta
        out(f"{label:>10s} T={f.T:5d} a={g(float(b[0]), 5):>11s} " + " ".join(f"{float(v):8.5f}" for v in b[1:])
            + f" | sum={float(b[1:].sum()):.6f} R2={f.r2:.8f} sd_resid(ddof0)={g(f.sd0, 6)}"
              f" sd_resid(T-9)={g(f.sd_dof, 6)}")

    out(f"{'':>10s} {'':7s} {'':>13s}" + " ".join(f"{s:>8s}" for s in short))
    reg_row("full", np.ones(tc_, dtype=bool))
    for y in sorted(set(yc.tolist())):
        reg_row(str(y), yc == y)
    out("note: 2007 holds only the returns from 2007-07-03; 2026 is to 2026-10-08.")
    c9 = np.column_stack([ye, x8])
    r9 = corr_of(cov0(c9))
    w9, _ = eig_desc(r9)
    out("9x9 correlation matrix (Electronic + eight) eigenvalues, descending: " + " ".join(g(float(v), 8) for v in w9))
    out(f"condition number lambda_max/lambda_min = {g(float(w9[0] / w9[-1]), 8)}")
    out("correlation of Electronic with each sub-industry: " + ", ".join(f"{n}={r9[0, i + 1]:.5f}" for i, n in enumerate(ELEC8)))

    # -------------------------------------------------------------- (d)
    section("(d) TAIEX's returns on the 28 leaves' returns (OLS with intercept)")
    sample_line("TAIEX + 28 leaves ((a) sample)", rr)
    out(f"{'sample':>14s} {'T':>6s} {'R2':>12s} {'adj R2':>12s} {'sd_resid(ddof0)':>16s} {'sd_resid(T-29)':>16s}")

    def reg_d(label: str, mask: NDArray[np.bool_]) -> Fit:
        f = ols(ytx[mask], xall[mask])
        out(f"{label:>14s} {f.T:6d} {f.r2:12.8f} {f.adj_r2:12.8f} "
            f"{g(f.sd0, 6):>16s} {g(f.sd_dof, 6):>16s}" + ("   (T < 3 x 29: nearly saturated, do not use)" if f.T < 87 else ""))
        return f

    reg_d("full", np.ones(t, dtype=bool))
    for y in sorted(set(years_col.tolist())):
        reg_d(str(y), years_col == y)
    last = np.zeros(t, dtype=bool)
    last[-250:] = True
    f250 = reg_d("last 250", last)
    out(f"last 250 returns: {dates[-250]} .. {dates[-1]}")
    b250 = f250.beta
    out(f"intercept = {g(float(b250[0]), 6)}; sum of the 28 slope coefficients = {float(b250[1:].sum()):.8f}")
    out("coefficients (last 250):")
    for nme, bv in zip(leaves, b250[1:]):
        out(f"  {nme:32s}{float(bv):12.6f}")
    out("note: per-year fits with 29 parameters are nearly saturated when T is small; "
        "returns per year: " + ", ".join(f"{int(y)}:{int(k)}" for y, k in zip(*np.unique(years_col, return_counts=True))))

    # -------------------------------------------------------------- (e)
    section("(e) First eigenvalue share of S15's correlation matrix, per calendar year")
    out(f"{'year':>6s} {'T':>5s} {'lambda_1':>12s} {'share':>12s}")
    sample_line("S15 (own sample)", r15)
    for y in range(2008, 2027):
        m = years15 == y
        w, _ = eig_desc(corr_of(cov0(xs15[m])))
        out(f"{y:>6d} {int(m.sum()):5d} {float(w[0]):12.6f} {float(w[0] / 15):12.8f}" + ("   (to date)" if y == 2026 else ""))
    w, _ = eig_desc(corr_of(cov0(xs15)))
    out(f"{'full':>6s} {len(xs15):5d} {float(w[0]):12.6f} {float(w[0] / 15):12.8f}")

    # -------------------------------------------------------------- (f)
    section("(f) Estimation error: Sigma_hat x = 1 in two half samples")
    out("each set is run on its own common sample (the samples differ in length) and, as a check, on the (a) sample; "
        "halves: first T // 2 returns and the rest")

    def half_test(label: str, cols: list[str], frame: pl.DataFrame) -> None:
        x = to_mat(frame, cols)
        h = x.shape[0] // 2
        dd = frame["date"].to_list()
        out()
        out(f"halves of {label}: T = {x.shape[0]}; first {h} returns {dd[0]}..{dd[h - 1]}; second {x.shape[0] - h} returns {dd[h]}..{dd[-1]}")
        s1, s2 = cov0(x[:h]), cov0(x[h:])
        one = np.ones(len(cols))
        x1, x2 = np.linalg.solve(s1, one), np.linalg.solve(s2, one)
        w1 = x1 / x1.sum()
        w2 = x2 / x2.sum()
        out(f"--- {label} ({len(cols)} sectors) ---")
        out(f"||x1 - x2|| / ||x1||           = {g(float(np.linalg.norm(x1 - x2) / np.linalg.norm(x1)), 8)}")
        out(f"||S1 - S2||_F / ||S1||_F       = {g(float(np.linalg.norm(s1 - s2) / np.linalg.norm(s1)), 8)}")
        out(f"cond(S1) = {g(float(np.linalg.cond(s1)), 8)}; cond(S2) = {g(float(np.linalg.cond(s2)), 8)}; "
            f"cond(S full) = {g(float(np.linalg.cond(cov0(x))), 8)}")
        out(f"extra: normalised to sum 1 (minimum-variance weights): ||w1 - w2|| / ||w1|| = "
            f"{g(float(np.linalg.norm(w1 - w2) / np.linalg.norm(w1)), 8)}")
        out(f"{'sector':32s}{'x1':>16s}{'x2':>16s}{'w1':>12s}{'w2':>12s}")
        for i, nme in enumerate(cols):
            out(f"{nme:32s}{float(x1[i]):16.6f}{float(x2[i]):16.6f}{float(w1[i]):12.6f}{float(w2[i]):12.6f}")

    half_test("S15, own sample", S15, r15)
    half_test("S15, (a) sample", S15, rr)
    half_test("5 sectors, own sample", S5, r5)
    half_test("5 sectors, (a) sample", S5, rr)

    # -------------------------------------------------------------- (g)
    section("(g) Cholesky factor of the 5-sector Sigma_hat and a simulation check")
    sample_line("5 sectors (own sample)", r5)
    t5 = x5.shape[0]
    s5 = cov0(x5)
    lo = np.linalg.cholesky(s5)
    out("sectors: " + ", ".join(S5))
    out("Sigma_hat (full own sample, ddof=0):")
    for row in s5:
        out("  " + " ".join(f"{float(v):15.8e}" for v in row))
    out("lower-triangular Cholesky factor L (Sigma_hat = L L^T):")
    for row in lo:
        out("  " + " ".join(f"{float(v):15.8e}" for v in row))
    out(f"check L L^T - Sigma_hat: max abs = {g(float(np.abs(lo @ lo.T - s5).max()), 4)}")
    rng = np.random.default_rng(SEED)
    z = rng.standard_normal((t5, 5))
    sim = z @ lo.T                                     # row i = L z_i, covariance L L^T in expectation
    ssim = cov0(sim)
    diff = np.abs(ssim - s5)
    rel = diff / np.abs(s5)
    out(f"draws: default_rng({SEED}).standard_normal(({t5}, 5)); simulated returns = z @ L^T; sample covariance ddof=0")
    out(f"largest absolute difference = {g(float(diff.max()), 8)}  (at entry {tuple(int(v) for v in np.unravel_index(int(np.argmax(diff)), diff.shape))}; "
        f"largest |Sigma_hat| entry = {g(float(np.abs(s5).max()), 8)})")
    out(f"largest relative difference (elementwise |diff| / |Sigma_hat_ij|) = {g(float(rel.max()), 8)} "
        f"(at entry {tuple(int(v) for v in np.unravel_index(int(np.argmax(rel)), rel.shape))})")
    out(f"Frobenius relative difference = {g(float(np.linalg.norm(ssim - s5) / np.linalg.norm(s5)), 8)}")

    # -------------------------------------------------------------- (h)
    section("(h) LM8 P&L case, 2025-04-07: 0050 and the front-month TX, q^T dP")
    tx = pl.read_csv(RAW / "TX__2025-04-01__2025-10-31.csv")
    e50 = load_chunks(RAW, "0050").filter(pl.col("date").is_between(pl.lit("2025-03-01"), pl.lit("2025-04-30")))
    d_to = "2025-04-07"
    tx_dates = sorted(tx["date"].unique().to_list())
    e_dates = e50["date"].to_list()
    d_from = max(d for d in e_dates if d < d_to)
    assert d_from in tx_dates and d_to in tx_dates, "TX file lacks one of the days"
    out(f"trading day before {d_to} (in the 0050 file and the TX file): {d_from}")
    expiry = {int(r["date"][:4] + r["date"][5:7]): r["date"]
              for r in tx.filter(pl.col("settlement_price") == 0).iter_rows(named=True)}
    out("expiry dates seen in the TX file (days on which settlement_price prints 0.0): "
        + ", ".join(f"{k}:{v}" for k, v in sorted(expiry.items())))

    def front(day: str) -> int:
        cands = [c for c in sorted(tx.filter(pl.col("date") == day)["contract_date"].to_list())
                 if expiry.get(c, "9999-12-31") > day]
        return cands[0]

    c_from, c_to = front(d_from), front(d_to)
    out(f"front month on {d_from}: {c_from}; on {d_to}: {c_to} (nearest contract_date whose expiry date is after the day)")
    assert c_from == c_to, "front month changes between the two days"
    out(f"contract used for both days: {c_to}, expiry {expiry[c_to]}; no roll between the two days, so dF is one "
        "contract's own settlement change.")
    px = {r["date"]: r for r in tx.filter(pl.col("contract_date") == c_to).iter_rows(named=True)}
    ep = {r["date"]: r for r in e50.iter_rows(named=True)}
    for dd in (d_from, d_to):
        r = px[dd]
        out(f"  {dd}: TX {c_to} settlement {r['settlement_price']:.1f}, close {r['close']:.1f}, volume {r['volume']}, "
            f"open interest {r['open_interest']}; 0050 close {ep[dd]['close']:.2f} (spread {ep[dd]['spread']})")
    div = pl.read_csv(RAW / "0050_dividends.csv")
    inwin = div.filter(pl.col("date").is_between(pl.lit(d_from), pl.lit(d_to)))["date"].to_list()
    out(f"0050 ex-dividend dates between {d_from} and {d_to}: {inwin if inwin else 'none'}; split date 2025-06-18 not in window")
    dfut = px[d_to]["settlement_price"] - px[d_from]["settlement_price"]
    ds = ep[d_to]["close"] - ep[d_from]["close"]
    out(f"dP = (dF, dS) = ({dfut:.1f} points, {ds:.2f} NT$ per share)")
    out(f"returns: TX settlement {px[d_to]['settlement_price'] / px[d_from]['settlement_price'] - 1:.6%}; "
        f"0050 {ep[d_to]['close'] / ep[d_from]['close'] - 1:.6%}")
    ta = pl.read_csv(RAW / "TAIEX__2025-04-01__2025-10-31.csv")
    tc = {r["date"]: r["close"] for r in ta.iter_rows(named=True)}
    if d_from in tc and d_to in tc:
        out(f"context: TAIEX close {tc[d_from]:.2f} -> {tc[d_to]:.2f} ({tc[d_to] / tc[d_from] - 1:.6%})")
    for label, q in (("q = (+1 TX contract at NT$200/point, +10,000 shares of 0050)", (1 * M_TX, 10_000)),
                     ("q = (-1 TX contract, +50,000 shares of 0050)", (-1 * M_TX, 50_000))):
        a, b = q[0] * dfut, q[1] * ds
        out(f"{label}: q in NT$ per unit = ({q[0]}, {q[1]}); q^T dP = {q[0]} x {dfut:.1f} + {q[1]} x {ds:.2f} "
            f"= {a:,.2f} + {b:,.2f} = {a + b:,.2f} NT$")

    # -------------------------------------------------------------- (i)
    section("(i) Pairwise deletion: S15 + 0050 + 00631L + 00679B (18 series)")
    cols18 = [*S15, *ETFS]
    for e, sd in SPLITS.items():
        out(f"{e}: return on split date {sd} excluded (set to missing); returns need a close on the previous TAIEX-calendar date, "
            "so the halt days around each split also drop out. ETF returns are price returns (no dividend added), "
            "like the sector price indices.")
    r18 = to_mat(ret, cols18)
    for e in ETFS:
        col = ret[e].drop_nulls().to_numpy()
        out(f"  {e}: {len(col)} returns, first {ret.filter(pl.col(e).is_not_null())['date'][0]}, "
            f"max |R| = {float(np.abs(col).max()):.4%}")
    n = len(cols18)
    rp = np.eye(n)
    cnt = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(n):
            m = ~np.isnan(r18[:, i]) & ~np.isnan(r18[:, j])
            cnt[i, j] = int(m.sum())
            if i < j:
                rp[i, j] = rp[j, i] = float(np.corrcoef(r18[m, i], r18[m, j])[0, 1])
    allm = ~np.isnan(r18).any(axis=1)
    rc = np.corrcoef(r18[allm].T)
    cd = ret.filter(pl.Series(allm))["date"].to_list()
    out(f"common sample of all 18: T = {int(allm.sum())}, {cd[0]}..{cd[-1]}")
    off = cnt[np.triu_indices(n, 1)]
    out(f"pairwise sample sizes: min {int(off.min())}, max {int(off.max())}; "
        f"pairs among the 3 ETFs: " + ", ".join(f"{ETFS[a]}/{ETFS[b]} T={cnt[15 + a, 15 + b]}"
                                                for a in range(3) for b in range(a + 1, 3)))
    wp, _ = eig_desc(rp)
    wc, _ = eig_desc(rc)
    out("pairwise-deleted 18x18 matrix: eigenvalues descending: " + " ".join(g(float(v), 8) for v in wp))
    out(f"  smallest eigenvalue = {g(float(wp[-1]), 10)}; negative eigenvalues: {int((wp < 0).sum())}; "
        f"condition number (positive-definite only) = {g(float(wp[0] / wp[-1]), 8) if wp[-1] > 0 else 'n/a (not positive definite)'}")
    out("common-sample 18x18 matrix: eigenvalues descending: " + " ".join(g(float(v), 8) for v in wc))
    out(f"  smallest eigenvalue = {g(float(wc[-1]), 10)}; condition number = {g(float(wc[0] / wc[-1]), 8)}")
    dm = np.abs(rp - rc)
    k = np.unravel_index(int(np.argmax(dm)), dm.shape)
    out(f"largest entrywise |pairwise - common| = {g(float(dm.max()), 6)} at {cols18[k[0]]} / {cols18[k[1]]}; "
        f"Frobenius ||pairwise - common||_F = {g(float(np.linalg.norm(rp - rc)), 6)}")
    # the ETF block alone shows where the inconsistency can come from
    out("pairwise correlations among the ETFs (own common dates) vs the common-sample value:")
    for a in range(3):
        for b in range(a + 1, 3):
            out(f"  {ETFS[a]}/{ETFS[b]}: pairwise {rp[15 + a, 15 + b]:.6f} (T={cnt[15 + a, 15 + b]}), common {rc[15 + a, 15 + b]:.6f}")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(LINES) + "\n")
    print(f"\nwritten {OUT}")


if __name__ == "__main__":
    main()
