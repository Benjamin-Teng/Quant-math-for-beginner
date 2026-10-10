"""LM3 statistics from the verified FinMind series; writes data/processed/lm03_stats.json.

Run after data/build_series.py:  uv run python data/lm03_stats.py

The 0050 and 00631L figures use processed/etf_daily_returns.parquet: total returns on the 2,902 dates on which
both funds traded. Each fund's split halt removes a few sessions from the other fund's series, so the returns dated
2025-06-18 and 2026-03-31 span several sessions. 0050's own calendar is used only to check the worst-day claims of
the module. QQQ and TQQQ use FinMind's adjusted closes for calendar 2022.
"""

import json
from datetime import date
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
PROC = HERE / "processed"
BASE = date(2014, 10, 31)  # last close before the first daily return
SPLITS = {"0050": ("2025-06-18", 4), "00631L": ("2026-03-31", 22)}


def decomposition(R, RF, L):
    """Log growth of an L-times daily fund: power, exact rebalancing effect, Taylor terms and residual."""
    s2, s3, s4 = (R**2).sum(), (R**3).sum(), (R**4).sum()
    power = L * np.log1p(R).sum()
    exact = (np.log1p(L * R) - L * np.log1p(R)).sum()
    t2 = -L * (L - 1) / 2 * s2
    t3 = t2 + (L**3 - L) / 3 * s3
    t4 = t3 - (L**4 - L) / 4 * s4
    actual = np.log1p(RF).sum()
    return {"power": power, "exact": exact, "T2": t2, "T3": t3, "T4": t4, "term3": t3 - t2, "term4": t4 - t3,
            "residual": actual - power - exact, "actual": actual, "RV": s2}


def block(R, RL, label):
    """Calendar-period decomposition of 00631L against twice 0050."""
    G0, GL, G2 = np.prod(1 + R), np.prod(1 + RL), np.prod(1 + 2 * R)
    d = decomposition(R, RL, 2)
    return {"label": label, "n": len(R), "ret0050": G0 - 1, "ret00631L": GL - 1, "twice0050": 2 * (G0 - 1),
            "exact2x": G2 - 1, "taylor2x": G0**2 * np.exp(-d["RV"]) - 1, **d, "gap": d["exact"] - d["T2"]}


def own_returns(sym):
    """A fund's daily total returns on its own trading calendar (dividends and split restated)."""
    files = sorted(RAW.glob(f"{sym}__*.csv"))
    px = pl.concat([pl.read_csv(f) for f in files]).unique("date").sort("date")
    div = pl.read_csv(RAW / "0050_dividends.csv") if sym == "0050" else None
    dmap = dict(zip(div["date"], div["cash_dividend"], strict=True)) if div is not None else {}
    sdate, k = SPLITS[sym]
    p, dates = px["close"].to_numpy(), px["date"].to_list()
    out = []
    for i in range(1, len(p)):
        prev = p[i - 1] / (k if dates[i] == sdate else 1)
        out.append((dates[i], (p[i] + dmap.get(dates[i], 0.0)) / prev - 1))
    return out


def main():
    df = pl.read_parquet(PROC / "etf_daily_returns.parquet").with_columns(pl.col("date").str.to_date())
    R, RL = df["R_0050"].to_numpy(), df["R_00631L"].to_numpy()
    dates = df["date"].to_list()
    n = len(R)
    days = (dates[-1] - BASE).days
    yrs = days / 365.25
    res = {}

    # ---- full sample (Exhibits paradox, decomp; Sections 5 and 7)
    full = block(R, RL, "full")
    mu, var = R.mean(), R.var()
    cen = R - mu
    full.update({
        "base": str(BASE), "first": str(dates[0]), "last": str(dates[-1]), "days": days, "years": yrs, "A": n / yrs,
        "cagr0050": (1 + full["ret0050"]) ** (1 / yrs) - 1, "cagr00631L": (1 + full["ret00631L"]) ** (1 / yrs) - 1,
        "log0050": np.log1p(R).sum(), "G0": np.prod(1 + R), "GL": np.prod(1 + RL),
        "drag_per_year": -full["T2"] / yrs, "exact_per_year": -full["exact"] / yrs,
        "residual_per_year": full["residual"] / yrs, "s2A": var * n / yrs, "mu2A": mu**2 * n / yrs,
        # 2*sum R^3 = 2*sum (R-mu)^3 + 2*(3*mu*sum (R-mu)^2 + n*mu^3): asymmetry part and trend part
        "term3_central": 2 * (cen**3).sum(), "term3_trend": 2 * (3 * mu * (cen**2).sum() + n * mu**3),
        "end_exact2x": np.prod(1 + 2 * R), "end_taylor": np.prod(1 + R) ** 2 * np.exp(-(R**2).sum()),
    })
    gap_path = np.cumsum(np.log1p(2 * R) - 2 * np.log1p(R)) + np.cumsum(R**2)
    i = int(np.argmax(np.abs(gap_path)))
    full["path_gap_max"], full["path_gap_date"] = gap_path[i], str(dates[i])
    res["full"] = full

    # ---- calendar periods: the 2014 stub, the full years 2015-2025 and 2026 to date
    yr = np.array([d.year for d in dates])
    res["years"] = [block(R[yr == y], RL[yr == y], str(y)) for y in sorted(set(yr.tolist()))]

    # ---- daily simple vs log returns (Section 5)
    r = np.log1p(R)
    res["daily"] = {"meanR": mu, "meanr": r.mean(), "diff": mu - r.mean(), "half_var": var / 2,
                    "half_m2": (R**2).mean() / 2, "sd": np.sqrt(var), "skew": (cen**3).mean() / var**1.5,
                    "exkurt": (cen**4).mean() / var**2 - 3, "max": R.max(), "max_date": str(dates[int(np.argmax(R))]),
                    "min": R.min(), "min_date": str(dates[int(np.argmin(R))])}

    # ---- sampling frequency (Exhibit freq): calendar periods of the 0050 total-return index on the common dates
    w = np.cumprod(1 + R)
    wdf = pl.DataFrame({"date": dates, "w": w})
    freq = []
    for every in ("1d", "1w", "1mo", "1q", "1y"):
        ww = w if every == "1d" else wdf.group_by_dynamic("date", every=every).agg(pl.col("w").last())["w"].to_numpy()
        ww = np.concatenate([[1.0], ww])
        Rk = ww[1:] / ww[:-1] - 1
        if every == "1y":
            Rk = Rk[1:-1]  # full calendar years 2015-2025 only
        m, v = Rk.mean(), Rk.var()
        g = np.log1p(Rk).mean()
        freq.append({"freq": every, "n": len(Rk), "mu": m, "sd": np.sqrt(v), "geo": np.expm1(g), "g_log": g,
                     "approx1": m - v / 2, "approx2": m - (v + m * m) / 2, "err1": m - v / 2 - np.expm1(g),
                     "err2": m - (v + m * m) / 2 - g, "max": Rk.max(), "min": Rk.min()})
    res["freq"] = freq

    # ---- crash days (aligned sample) and 0050's own calendar
    big = []
    for dd in ("2018-10-11", "2024-08-05", "2025-04-07", "2025-04-10"):
        k = next(j for j, x in enumerate(dates) if str(x) == dd)
        x = R[k]
        big.append({"date": dd, "R": x, "log": np.log1p(x), "T1": x, "T2": x - x * x / 2,
                    "bound2": abs(x) ** 3 / (3 * (1 + min(x, 0.0)) ** 3), "R00631L": RL[k]})
    res["big"] = big
    own = own_returns("0050")
    worst = sorted(own, key=lambda t: t[1])[:3]
    res["own0050"] = {"n": len(own), "worst": [{"date": d, "R": x} for d, x in worst]}
    # sessions spanned by the two halt-spanning returns: the other fund traded in between
    s0050 = {d for d, _ in own}
    s631 = {d for d, _ in own_returns("00631L")}
    span = {}
    for d0, d1, other in (("2025-06-10", "2025-06-18", s631), ("2026-03-24", "2026-03-31", s0050)):
        span[d1] = 1 + sum(d0 < d < d1 for d in other)
    res["span_sessions"] = span

    # ---- QQQ and TQQQ in 2022 (Example tqqq): adjusted closes from 2021-12-31 to 2022-12-30. TQQQ targets three
    # times the Nasdaq-100 price index (NDX), which leaves dividends out, so the residual is also measured against
    # QQQ's unadjusted close; the adjusted close adds QQQ's 2022 dividends.
    qt = (pl.read_csv(RAW / "QQQ__us_2022.csv").join(pl.read_csv(RAW / "TQQQ__us_2022.csv"), on="date", suffix="_t")
          .sort("date").filter(pl.col("date").is_between(pl.lit("2021-12-31"), pl.lit("2022-12-30"))))
    qa, ta, qc = qt["adj_close"].to_numpy(), qt["adj_close_t"].to_numpy(), qt["close"].to_numpy()
    rq, rt = qa[1:] / qa[:-1] - 1, ta[1:] / ta[:-1] - 1
    d3 = decomposition(rq, rt, 3)
    du = decomposition(qc[1:] / qc[:-1] - 1, rt, 3)
    G, Gu = qa[-1] / qa[0], qc[-1] / qc[0]
    res["qqq2022"] = {"n": len(rq), "first": qt["date"][0], "last": qt["date"][-1], "G": G, "lnG": np.log(G),
                      "QQQ": G - 1, "TQQQ": ta[-1] / ta[0] - 1, "thrice": 3 * (G - 1), "tqqq_first": ta[0],
                      "tqqq_last": ta[-1], "sqrtRV": np.sqrt(d3["RV"]), **d3,
                      "residual_vs_T2": d3["actual"] - d3["power"] - d3["T2"],
                      "taylor_value": G**3 * np.exp(d3["T2"]), "exact_value": G**3 * np.exp(d3["exact"]),
                      "div_qqq": np.log(G) - np.log(qc[-1] / qc[0]), "qqq_close_first": qc[0],
                      "qqq_close_last": qc[-1], "power_unadj": du["power"], "exact_unadj": du["exact"],
                      "residual_unadj": du["residual"], "G_unadj": Gu, "RV_unadj": du["RV"],
                      # the benchmark G^3 e^(-3 RV) on the unadjusted (price-only) closes
                      "taylor_value_unadj": Gu**3 * np.exp(du["T2"]), "exact_value_unadj": Gu**3 * np.exp(du["exact"])}

    (PROC / "lm03_stats.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")

    f = res["full"]
    print(f"FULL {f['first']}..{f['last']} n={f['n']} days={f['days']} years={f['years']:.4f} A={f['A']:.3f}")
    for k in ("ret0050", "ret00631L", "twice0050", "cagr0050", "cagr00631L", "log0050", "power", "exact", "T2", "T3",
              "T4", "term3", "term4", "term3_trend", "term3_central", "gap", "residual", "actual", "drag_per_year",
              "exact_per_year", "residual_per_year", "s2A", "mu2A", "end_exact2x", "end_taylor", "path_gap_max"):
        print(f"  {k:18s} {f[k]: .6f}")
    print("  path_gap_date     ", f["path_gap_date"])
    print("YEAR     n   0050%      631L%     2x%      exact2x%  T2       exact    T3       gap      resid")
    for b in res["years"]:
        print(f"{b['label']} {b['n']:4d} {100 * b['ret0050']:9.4f} {100 * b['ret00631L']:9.4f} "
              f"{100 * b['twice0050']:9.4f} {100 * b['exact2x']:9.4f} {b['T2']:8.5f} {b['exact']:8.5f} "
              f"{b['T3']:8.5f} {b['gap']:+8.5f} {b['residual']:+8.5f}")
    print("DAILY", {k: (round(v, 7) if isinstance(v, float) else v) for k, v in res["daily"].items()})
    for x in res["freq"]:
        print("FREQ", {k: (round(float(v), 7) if not isinstance(v, str) else v) for k, v in x.items()})
    for x in res["big"]:
        print("BIG", {k: (round(float(v), 6) if not isinstance(v, str) else v) for k, v in x.items()})
    print("OWN0050", res["own0050"], "SPAN", res["span_sessions"])
    print("QQQ2022", {k: (round(float(v), 6) if not isinstance(v, str) else v) for k, v in res["qqq2022"].items()})


if __name__ == "__main__":
    main()
