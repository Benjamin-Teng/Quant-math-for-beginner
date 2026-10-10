"""LM6: the TX-TAIEX basis through the 2025 dividend season.

Computes every number about TX futures, TAIEX and dividends quoted in LM6 (Introduction and Sections 7-8) and
writes data/processed/lm06_basis.json.  Run:  uv run python data/lm06_basis.py

Conventions
  F      TX regular-session daily settlement price (volume-weighted price of the last minute before the 13:45 close;
         set by exchange rules when nothing trades then), S = TAIEX close (13:25-13:30 call auction)
  tau    calendar days to expiry / 365 (actual/365, as DBS Taiwan accrues NTD deposits; see LM1); expiry = third
         Wednesday of the delivery month (TAIFEX contract rules)
  r_f    proxy financing rate = CBC discount rate, 2% p.a. throughout 2025 (continuous compounding); R_PROXY below
  q*tau  dividends going ex over the contract's remaining life, as a continuously compounded (log) fraction of the index:
           implied  : r_f*tau - ln(F/S)                      (from F = S exp((r_f-q)tau))
           realized : ln(TR_T/TR_t) - ln(S_T/S_t)            (TWSE total-return index vs price index; ex-dates)
  On an ex-date the ratio TR/S rises by 1/(1-delta), so delta = 1 - exp(-dq) and the index points removed are
  delta * (previous close).
  Basis decomposition (exact):  F - S = carry - dividends + residual
           carry     = S (e^{r_f tau} - 1)
           dividends = S e^{r_f tau} (1 - e^{-q_real tau})   (realized dividend yield applied to the index on the
                                                              pricing date, carried to expiry)
           residual  = F - S e^{(r_f - q_real) tau}           (what perfect-foresight fair value cannot explain)
"""
import datetime as dt
import glob
import json
import math
from decimal import Decimal
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
R_PROXY = 0.02
SNAP = "2025-06-27"                       # term-structure snapshot used in the Introduction
SNAP_DATES = ["2025-04-01", "2025-06-27", "2025-10-31"]


def third_wednesday(y: int, m: int) -> dt.date:
    d = dt.date(y, m, 1)
    return d + dt.timedelta(days=(2 - d.weekday()) % 7 + 14)


def load_index() -> pl.DataFrame:
    """TAIEX price and total-return index for calendar 2025, with integrity checks."""
    price_files = [RAW / "lm06" / "TAIEX__2024-12-31__2025-03-31.csv", RAW / "TAIEX__2025-04-01__2025-10-31.csv",
                   RAW / "lm06" / "TAIEX__2025-11-03__2025-12-31.csv"]
    pr = pl.concat([pl.read_csv(f, schema_overrides={"close": pl.Utf8, "spread": pl.Utf8}) for f in price_files]).sort("date")
    assert pr["date"].is_unique().all()
    c = [Decimal(x) for x in pr["close"]]; s = [Decimal(x) for x in pr["spread"]]
    bad = [pr["date"][i] for i in range(1, len(c)) if abs(c[i] - c[i - 1] - s[i]) > Decimal("0.005")]
    assert not bad, f"spread mismatches {bad}"
    tr = pl.concat([pl.read_csv(f) for f in sorted(glob.glob(str(RAW / "lm06" / "TAIEX_TR__*.csv")))]).sort("date")
    assert tr["date"].is_unique().all()
    idx = (pr.select("date", pl.col("close").cast(pl.Float64).alias("S"))
             .join(tr.select("date", pl.col("price").alias("TR")), on="date", how="full", coalesce=True).sort("date"))
    assert idx.null_count().sum_horizontal().item() == 0, "price and total-return dates differ"
    idx = idx.with_columns(
        (pl.col("TR") / pl.col("TR").shift(1)).log().alias("lTR"),
        (pl.col("S") / pl.col("S").shift(1)).log().alias("lS"),
    ).with_columns((pl.col("lTR") - pl.col("lS")).alias("dq"))
    assert (idx["dq"].drop_nulls() > -1e-6).all(), "total-return index fell behind the price index"
    return idx


def load_tx(idx: pl.DataFrame) -> pl.DataFrame:
    tx = pl.read_csv(RAW / "TX__2025-04-01__2025-10-31.csv").with_columns(pl.col("contract_date").cast(pl.Utf8).alias("c"))
    assert tx.group_by("date").len()["len"].unique().to_list() == [6]
    exp = {c: third_wednesday(int(c[:4]), int(c[4:])).isoformat() for c in tx["c"].unique().to_list()}
    # the expiring contract shows settlement 0.0 on its expiry day (final settlement is not in the file)
    zero = tx.filter(pl.col("settlement_price") == 0)
    assert all(exp[c] == d for c, d in zip(zero["c"], zero["date"])), "settlement 0 off an expiry day"
    d = (tx.filter(pl.col("settlement_price") > 0)
           .with_columns(pl.col("c").replace_strict(exp).alias("expiry"))
           .join(idx.select("date", "S", "TR"), on="date", how="left"))
    assert d["S"].null_count() == 0
    d = d.with_columns(((pl.col("expiry").str.to_date() - pl.col("date").str.to_date()).dt.total_days()).alias("days"))
    d = d.with_columns((pl.col("days") / 365.0).alias("tau"), pl.col("settlement_price").alias("F"))
    d = d.join(idx.select(pl.col("date").alias("expiry"), pl.col("S").alias("S_T"), pl.col("TR").alias("TR_T")),
               on="expiry", how="left")
    r = R_PROXY
    d = d.with_columns(
        (pl.col("F") - pl.col("S")).alias("basis"),
        (r * pl.col("tau") - (pl.col("F") / pl.col("S")).log()).alias("qtau_imp"),
        (1 - pl.col("F") / pl.col("S") * (-r * pl.col("tau")).exp()).alias("pvdiv_imp"),
        ((pl.col("TR_T") / pl.col("TR")).log() - (pl.col("S_T") / pl.col("S")).log()).alias("qtau_real"),
    ).with_columns(
        (pl.col("S") * ((r * pl.col("tau")).exp() - 1)).alias("carry"),
        (pl.col("S") * (r * pl.col("tau")).exp() * (1 - (-pl.col("qtau_real")).exp())).alias("div_fv"),
        (pl.col("S") * ((r * pl.col("tau") - pl.col("qtau_real")).exp() - 1)).alias("fair_basis"),
    ).with_columns(
        (pl.col("basis") - pl.col("fair_basis")).alias("residual"),
        ((pl.col("qtau_real") + (pl.col("F") / pl.col("S")).log()) / pl.col("tau")).alias("r_implied"),
    )
    return d.sort(["date", "days"])


def near_month(d: pl.DataFrame) -> pl.DataFrame:
    return d.group_by("date", maintain_order=True).first()


def rnd(x, k=6):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else round(float(x), k)


def build():
    idx = load_index()
    d = load_tx(idx)
    nm = near_month(d)
    out = {"r": R_PROXY}

    # ---- dividends in calendar 2025 from the total-return index
    q2025 = math.log(idx["TR"][-1] / idx["TR"][0]) - math.log(idx["S"][-1] / idx["S"][0])
    m = idx.drop_nulls("dq").with_columns(pl.col("date").str.slice(5, 2).cast(pl.Int32).alias("m"))
    by_month = m.group_by("m").agg(pl.col("dq").sum()).sort("m")
    jun_sep = float(by_month.filter(pl.col("m").is_between(6, 9))["dq"].sum())
    jul_aug = by_month.filter(pl.col("m").is_between(7, 8))["dq"].sum()
    dec11 = idx.filter(pl.col("date") == "2025-12-11")
    s_prev = idx.filter(pl.col("date") == "2025-12-10")["S"][0]
    # TR/S rises by 1/(1-delta) on an ex-date: delta = 1 - e^{-dq}, points removed = delta * previous close
    dec11_delta = -math.expm1(-dec11["dq"][0])
    tsmc_pts = s_prev * dec11_delta
    big_days = m.filter(pl.col("dq") > 10e-4).select("date", (pl.col("dq") * 1e4).alias("bp"))
    out["dividends2025"] = {"q_total": q2025, "jun_sep": jun_sep, "jul_aug": jul_aug, "share_jun_sep": jun_sep / q2025,
                            "by_month": dict(zip(by_month["m"].to_list(), by_month["dq"].to_list())),
                            "dec11_bp": dec11["dq"][0] * 1e4, "dec11_delta_bp": dec11_delta * 1e4,
                            "dec11_prev_close": s_prev, "dec11_points": tsmc_pts,
                            "days_over_10bp": big_days.to_dicts(),
                            "n_div_days": m.filter(pl.col("dq") > 1e-6).height}
    # cumulative series for the chart
    cum = m.select("date", pl.col("dq").cum_sum().alias("cum"))
    out["dividends2025"]["cum"] = {"date": ["2024-12-31"] + cum["date"].to_list(), "cum": [0.0] + cum["cum"].to_list()}

    # ---- the curve on the snapshot date
    snap = d.filter(pl.col("date") == SNAP)
    out["snap"] = snap.select("c", "expiry", "days", "tau", "S", "F", "volume", "close", "basis", "qtau_imp", "pvdiv_imp",
                              "qtau_real", "carry", "div_fv", "fair_basis", "residual", "r_implied").to_dicts()
    # implied forward dividends between consecutive expiries (calendar spreads; no index timing mismatch)
    sn = snap.sort("days")
    fwd = []
    for a, b in zip(sn.iter_rows(named=True), list(sn.iter_rows(named=True))[1:]):
        dtau = b["tau"] - a["tau"]
        imp = R_PROXY * dtau - math.log(b["F"] / a["F"])
        real = None
        if b["TR_T"] is not None and a["TR_T"] is not None:
            real = math.log(b["TR_T"] / a["TR_T"]) - math.log(b["S_T"] / a["S_T"])
        fwd.append({"from": a["c"], "to": b["c"], "dtau": dtau, "spread": b["F"] - a["F"], "q_imp": imp, "q_real": real})
    out["snap_forward"] = fwd

    # ---- robustness: average of 23-27 June for the same contracts
    wk = d.filter(pl.col("date").is_between(pl.lit("2025-06-23"), pl.lit("2025-06-27")) & pl.col("c").is_in(snap["c"].to_list()))
    out["week"] = (wk.group_by("c").agg(pl.len().alias("n"), pl.col("basis").mean(), pl.col("qtau_imp").mean(),
                                        pl.col("qtau_real").mean(), pl.col("residual").mean(), pl.col("r_implied").mean())
                     .sort("c").to_dicts())

    # ---- sensitivity of the implied dividend yield to r (December contract on the snapshot date)
    dec = snap.filter(pl.col("c") == "202512").row(0, named=True)
    sens = []
    for r in (0.0, 0.01, 0.015, 0.02, 0.025, 0.03):
        qt = r * dec["tau"] - math.log(dec["F"] / dec["S"])
        fair = dec["S"] * math.exp(r * dec["tau"] - dec["qtau_real"])
        sens.append({"r": r, "qtau": qt, "q_ann": qt / dec["tau"], "pvdiv": 1 - dec["F"] / dec["S"] * math.exp(-r * dec["tau"]),
                     "residual": dec["F"] - fair})
    out["sens_dec"] = sens

    # ---- near month by calendar month
    nmm = nm.with_columns(pl.col("date").str.slice(5, 2).cast(pl.Int32).alias("m"))
    out["near_by_month"] = (nmm.group_by("m").agg(
        pl.len().alias("n"), pl.col("basis").mean().alias("basis"), pl.col("basis").min().alias("bmin"),
        pl.col("basis").max().alias("bmax"), (pl.col("basis") / pl.col("S")).mean().alias("basis_pct"),
        pl.col("carry").mean(), pl.col("div_fv").mean(), pl.col("residual").mean(),
        pl.col("qtau_imp").mean(), pl.col("qtau_real").mean(), pl.col("days").mean().alias("days"))
        .sort("m").to_dicts())
    # day-to-day noise of the near-month basis (same contract on consecutive trading days)
    nmc = nm.with_columns(pl.col("basis").diff().alias("db"), (pl.col("c") == pl.col("c").shift(1)).alias("same"))
    db = nmc.filter(pl.col("same"))["db"].to_numpy()
    out["noise"] = {"sd_daily_change": float(np.std(db, ddof=1)), "n": len(db)}
    j30 = d.filter((pl.col("date").is_in(["2025-06-27", "2025-06-30"])) & (pl.col("c") == "202507")).sort("date")
    out["jun30"] = {"S": j30["S"].to_list(), "F": j30["F"].to_list(), "basis": j30["basis"].to_list()}
    ohlc = pl.read_csv(RAW / "lm06" / "TAIEX_OHLC__2025-06-26__2025-07-01.csv")
    out["ohlc"] = ohlc.to_dicts()
    # the most extreme near-month annualized implied yields (pitfall: annualizing close to expiry)
    nmq = nm.with_columns((pl.col("qtau_imp") / pl.col("tau")).alias("q_ann"))
    out["near_extreme"] = nmq.sort("q_ann", descending=True).head(3).select("date", "c", "days", "basis", "q_ann").to_dicts()
    out["near_min_q"] = nmq.sort("q_ann").head(2).select("date", "c", "days", "basis", "q_ann").to_dicts()

    # ---- December 2025 contract through time (for the chart) and by month
    dc = d.filter(pl.col("c") == "202512").sort("date")
    out["dec_series"] = dc.select("date", "S", "F", "basis", "fair_basis", "residual", "qtau_imp", "qtau_real",
                                  "r_implied", "days").to_dicts()
    dcm = dc.with_columns(pl.col("date").str.slice(5, 2).cast(pl.Int32).alias("m"))
    out["dec_by_month"] = (dcm.group_by("m").agg(pl.col("basis").mean(), pl.col("fair_basis").mean(),
                                                 pl.col("residual").mean(), pl.col("r_implied").mean(),
                                                 (pl.col("residual") / pl.col("S")).mean().alias("res_pct"))
                              .sort("m").to_dicts())
    # ---- term structures on three dates
    out["curves"] = {dd: d.filter(pl.col("date") == dd).select("c", "days", "basis", "S", "F").to_dicts() for dd in SNAP_DATES}
    # ---- PP12: the September 2025 contract (202509) by month over its life (no implied financing rate: a mean of
    #      daily annualized rates is dominated by the last sessions before expiry)
    sep = d.filter(pl.col("c") == "202509").with_columns(pl.col("date").str.slice(5, 2).cast(pl.Int32).alias("m"))
    out["sep_by_month"] = (sep.group_by("m").agg(pl.len().alias("n"), pl.col("basis").mean(), pl.col("carry").mean(),
                                                 pl.col("div_fv").mean(), pl.col("residual").mean(),
                                                 pl.col("date").min().alias("first"), pl.col("date").max().alias("last"))
                              .sort("m").to_dicts())
    sep_raw = pl.read_csv(RAW / "TX__2025-04-01__2025-10-31.csv").filter(pl.col("contract_date").cast(pl.Utf8) == pl.lit("202509"))
    out["sep_expiry_row"] = sep_raw.filter(pl.col("date") == pl.lit("2025-09-17")).select("date", "settlement_price").to_dicts()
    # ---- whole-window facts
    out["window"] = {"first": d["date"].min(), "last": d["date"].max(), "n_days": d["date"].n_unique(),
                     "S_first": idx.filter(pl.col("date") == "2025-04-01")["S"][0],
                     "S_last": idx.filter(pl.col("date") == "2025-10-31")["S"][0]}

    # ---- is 27 June typical? ranks over the whole window and multi-day figures (December contract)
    def rank_of(frame, col, day, ascending=True):
        s = frame.sort(col, descending=not ascending)["date"].to_list()
        return s.index(day) + 1, frame.height
    dec_d = d.filter(pl.col("c") == "202512").sort("date")
    centred = dec_d.filter(pl.col("date").is_between(pl.lit("2025-06-23"), pl.lit("2025-07-03")))
    jj = dec_d.filter(pl.col("date").is_between(pl.lit("2025-06-01"), pl.lit("2025-07-31"))).with_columns(
        (-(pl.col("F") / pl.col("S")).log()).alias("qtau_r0"),                       # implied q*tau at r_f = 0
        (pl.col("F") - pl.col("S") * (-pl.col("qtau_real")).exp()).alias("resid_r0"))   # residual at r_f = 0
    d30 = dec_d.filter(pl.col("date") == "2025-06-30").row(0, named=True)
    out["robust"] = {
        "dec_basis_rank": rank_of(dec_d, "basis", SNAP), "dec_resid_rank": rank_of(dec_d, "residual", SNAP),
        "dec_rimp_rank": rank_of(dec_d, "r_implied", SNAP), "near_resid_rank": rank_of(nm, "residual", SNAP),
        "near_resid_min": nm.sort("residual").select("date", "c", "residual").head(2).to_dicts(),
        "dec_resid_neg_days": int((dec_d["residual"] < 0).sum()), "dec_days": dec_d.height,
        "centred_days": centred["date"].to_list(), "centred_resid": centred["residual"].mean(),
        "centred_basis": centred["basis"].mean(), "centred_qtau_imp": centred["qtau_imp"].mean(),
        "dec_jun30": {"residual": d30["residual"], "r_implied": d30["r_implied"],
                      "qtau_r0": -math.log(d30["F"] / d30["S"])},
        "junjul_days": jj.height, "q2025": q2025,
        "junjul_qtau_r0_above_q2025": int((jj["qtau_r0"] > q2025).sum()),
        "junjul_last_day_above": jj.filter(pl.col("qtau_r0") > q2025)["date"].max(),
        "junjul_resid_r0_neg": int((jj["resid_r0"] < 0).sum()),
        "junjul_resid_r0_nonneg_days": jj.filter(pl.col("resid_r0") >= 0)["date"].to_list(),
        "S_T_over_S_dec": dec_d.filter(pl.col("date") == SNAP)["S_T"][0] / dec_d.filter(pl.col("date") == SNAP)["S"][0],
    }

    # ---- 30 June: index timing versus the ex-dividend part of the fall (July contract)
    i27, i30, i01 = (idx.filter(pl.col("date") == x).row(0, named=True) for x in ("2025-06-27", "2025-06-30", "2025-07-01"))
    delta30 = -math.expm1(-i30["dq"])
    jul = d.filter((pl.col("c") == "202507") & pl.col("date").is_in(["2025-06-27", "2025-06-30"])).sort("date")
    out["jun30_detail"] = {
        "S_change": i30["S"] - i27["S"], "S_ret": i30["S"] / i27["S"] - 1, "TR_ret": i30["TR"] / i27["TR"] - 1,
        "exdiv_bp": delta30 * 1e4, "exdiv_points": delta30 * i27["S"],
        "F_change": jul["F"][1] - jul["F"][0], "F_ret": jul["F"][1] / jul["F"][0] - 1,
        "basis": jul["basis"].to_list(), "basis_change": jul["basis"][1] - jul["basis"][0],
        "residual": jul["residual"].to_list(),
        "timing_points": (jul["basis"][1] - jul["basis"][0]) - delta30 * i27["S"],
        "S_change_jul1": i01["S"] - i30["S"]}

    # ---- trading volume: back months trade thinly (settlement partly set by exchange rules)
    vol = d.filter(pl.col("date") == SNAP).select("c", "volume", "close", "F").sort("c")
    out["volume_snap"] = vol.with_columns((pl.col("close") - pl.col("F")).alias("last_minus_settle")).to_dicts()
    traded = dec_d.filter(pl.col("volume") > 0).with_columns((pl.col("close") - pl.col("F")).alias("gap"))
    gmax = traded.sort(pl.col("gap").abs(), descending=True).row(0, named=True)
    j26 = d.filter((pl.col("c") == "202606") & (pl.col("date") == "2025-06-30")).row(0, named=True)
    out["volume_dec"] = {"median": dec_d["volume"].median(), "zero_days": int((dec_d["volume"] == 0).sum()),
                         "zero_dates": dec_d.filter(pl.col("volume") == 0)["date"].to_list(),
                         "max_gap": gmax["gap"], "max_gap_date": gmax["date"], "max_gap_volume": gmax["volume"],
                         "jun26_on_jun30": {"volume": j26["volume"], "settlement": j26["F"]},
                         "near_median": nm["volume"].median()}
    out["volume_by_contract"] = (d.group_by("c").agg(pl.len().alias("n"), pl.col("volume").median().alias("median"),
                                                     (pl.col("volume") == 0).sum().alias("zero_days"))
                                  .sort("c").to_dicts())
    # by position on the curve each day (1 = nearest contract with a settlement price)
    pos = d.sort(["date", "days"]).with_columns(pl.col("days").rank("ordinal").over("date").alias("pos"))
    out["volume_by_position"] = (pos.group_by("pos").agg(pl.col("volume").median().alias("median"),
                                                         pl.col("volume").max().alias("max")).sort("pos").to_dicts())

    # ---- M4: index points actually removed on the ex-dates between the snapshot and each expiry (yield measure
    #      in (6.25) applies the realized yield to the snapshot index level instead)
    ix = idx.with_columns(pl.col("S").shift(1).alias("S_prev"), (-(-pl.col("dq")).exp() + 1).alias("delta"))
    pts = []
    for x in snap.sort("days").iter_rows(named=True):
        if x["TR_T"] is None:
            continue
        w = ix.filter((pl.col("date") > SNAP) & (pl.col("date") <= x["expiry"])).with_columns(
            (pl.col("delta") * pl.col("S_prev")).alias("pts"),
            ((pl.lit(x["expiry"]).str.to_date() - pl.col("date").str.to_date()).dt.total_days() / 365.0).alias("t_left"))
        fv = (w["pts"] * (R_PROXY * w["t_left"]).exp()).sum()
        pts.append({"c": x["c"], "points": w["pts"].sum(), "points_fv": fv, "div_fv": x["div_fv"],
                    "residual_points": x["basis"] - x["carry"] + fv, "residual": x["residual"]})
    out["exdiv_points"] = pts
    return out, d, idx


def conv(o):
    if isinstance(o, dict): return {str(k): conv(v) for k, v in o.items()}
    if isinstance(o, list): return [conv(v) for v in o]
    if isinstance(o, (np.floating,)): return float(o)
    if isinstance(o, (np.integer,)): return int(o)
    return o


if __name__ == "__main__":
    out, d, idx = build()
    (HERE / "processed").mkdir(exist_ok=True)
    (HERE / "processed" / "lm06_basis.json").write_text(json.dumps(conv(out), indent=1), encoding="utf-8")
    P = print
    dv = out["dividends2025"]
    P(f"DIVIDENDS 2025 (TR vs price, log): total {dv['q_total']:.4%}  Jun-Sep {dv['jun_sep']:.4%} ({dv['share_jun_sep']:.1%})"
      f"  Jul-Aug {dv['jul_aug']:.4%}  ex-div days {dv['n_div_days']}")
    P("  by month (%):", {k: round(v * 100, 3) for k, v in dv["by_month"].items()})
    P(f"  2025-12-11: TR/S up {dv['dec11_bp']:.2f} bp (log), dq = {dv['dec11_bp']/1e4:.8f}; delta = 1 - e^-dq = {dv['dec11_delta_bp']:.3f} bp of the"
      f" 10 Dec close {dv['dec11_prev_close']:,.2f} = {dv['dec11_points']:.2f} index points (press estimate: 40.34)")
    P("  days > 10 bp:", [(x["date"], round(x["bp"], 2)) for x in dv["days_over_10bp"]])
    P(f"SNAPSHOT {SNAP}: S = {out['snap'][0]['S']:.2f}")
    P("  c       days  tau      F        basis   bas%    qtau_imp pvdiv_imp qtau_real  carry   div_fv  fair   resid   r_impl")
    for x in out["snap"]:
        P(f"  {x['c']} {x['days']:4d} {x['tau']:.5f} {x['F']:8.0f} {x['basis']:8.2f} {x['basis']/x['S']:7.3%} {x['qtau_imp']:8.4%} "
          f"{x['pvdiv_imp']:8.4%} {(x['qtau_real'] if x['qtau_real'] is not None else float('nan')):8.4%} "
          f"{x['carry']:7.1f} {(x['div_fv'] or float('nan')):7.1f} {(x['fair_basis'] or float('nan')):7.1f} "
          f"{(x['residual'] or float('nan')):7.1f} {(x['r_implied'] or float('nan')):7.2%}")
    P("  forward (calendar-spread) dividends:")
    for f in out["snap_forward"]:
        P(f"   {f['from']}->{f['to']} dtau={f['dtau']:.5f} spread={f['spread']:.0f} q_imp={f['q_imp']:.4%} "
          f"q_real={(f['q_real'] if f['q_real'] is not None else float('nan')):.4%}")
    P("  week 23-27 June averages:")
    for w in out["week"]:
        P(f"   {w['c']} n={w['n']} basis={w['basis']:.1f} qimp={w['qtau_imp']:.4%} qreal={w['qtau_real'] if w['qtau_real'] is None else round(w['qtau_real']*100,4)} "
          f"resid={w['residual'] if w['residual'] is None else round(w['residual'],1)} rimp={w['r_implied'] if w['r_implied'] is None else round(w['r_implied']*100,2)}")
    P("SENSITIVITY (Dec contract on snapshot):")
    for s in out["sens_dec"]:
        P(f"   r={s['r']:.1%} qtau={s['qtau']:.4%} q_ann={s['q_ann']:.3%} pvdiv={s['pvdiv']:.4%} residual={s['residual']:.1f}")
    P("NEAR MONTH BY MONTH:")
    P("   m  n  basis   min    max   bas%    carry  div_fv  resid  qimp    qreal   days")
    for x in out["near_by_month"]:
        P(f"   {x['m']:2d} {x['n']:2d} {x['basis']:7.1f} {x['bmin']:7.1f} {x['bmax']:6.1f} {x['basis_pct']:7.3%} {x['carry']:6.1f} "
          f"{x['div_fv']:6.1f} {x['residual']:7.1f} {x['qtau_imp']:7.3%} {x['qtau_real']:7.3%} {x['days']:5.1f}")
    P(f"NOISE: sd of daily change in near-month basis = {out['noise']['sd_daily_change']:.1f} points (n={out['noise']['n']})")
    P("JUN30:", out["jun30"])
    P("OHLC:", out["ohlc"])
    P("NEAR EXTREME q_ann:", [(x["date"], x["c"], x["days"], round(x["basis"], 2), round(x["q_ann"] * 100, 1)) for x in out["near_extreme"]])
    P("NEAR MIN q_ann:", [(x["date"], x["c"], x["days"], round(x["basis"], 2), round(x["q_ann"] * 100, 1)) for x in out["near_min_q"]])
    P("DEC BY MONTH:")
    for x in out["dec_by_month"]:
        P(f"   {x['m']:2d} basis={x['basis']:.1f} fair={x['fair_basis']:.1f} resid={x['residual']:.1f} ({x['res_pct']:.3%}) r_impl={x['r_implied']:.2%}")
    for dd, cv in out["curves"].items():
        P("CURVE", dd, [(x["c"], x["days"], round(x["basis"], 2)) for x in cv])
    P("WINDOW", out["window"])
    P("BALANCED TABLES (1 decimal; residual = basis - carry + dividends as displayed):")
    def bal(b, c, dv, res):
        br, cr, dr = round(b, 1), round(c, 1), round(dv, 1)
        rd = round(br - cr + dr, 1)
        assert abs(rd - res) <= 0.1 + 1e-9, (b, c, dv, res)
        return br, cr, dr, rd, round(res, 1)
    for x in out["snap"][:4]:
        P("   SNAP", x["c"], bal(x["basis"], x["carry"], x["div_fv"], x["residual"]),
          f"qimp {x['qtau_imp']:.2%} qreal {x['qtau_real']:.2%} rimp {x['r_implied']:.2%} fairF {x['S']+x['fair_basis']:.1f}")
    for x in out["near_by_month"]:
        P("   NEAR", x["m"], x["n"], round(x["days"], 1), bal(x["basis"], x["carry"], x["div_fv"], x["residual"]),
          f"qimp {x['qtau_imp']:.3%} qreal {x['qtau_real']:.3%}")
    for x in out["sep_by_month"]:
        P("   SEP", x["m"], x["n"], x["first"], x["last"], bal(x["basis"], x["carry"], x["div_fv"], x["residual"]))
    P("   SEP expiry-day row in the raw file (dropped):", out["sep_expiry_row"])
    P("EXHIBIT TABLES AT DISPLAYED PRECISION (each row: basis = carry - dividends + residual exactly as printed)")
    for x in out["snap"]:
        P(f"   EX1 {x['c']} {x['expiry']} {x['days']} vol {x['volume']:,} {x['F']:,.0f} {x['basis']:,.2f} {x['basis']/x['S']:.2%} {x['qtau_imp']:.2%}")
    for x in out["snap"][:4]:
        v = [round(x[k], 2) for k in ("basis", "carry", "div_fv", "residual")]
        assert abs(v[1] - v[2] + v[3] - v[0]) < 1e-9
        P(f"   EX11 {x['c']} " + " ".join(f"{u:.2f}" for u in v) + f" {x['qtau_imp']:.2%} {x['qtau_real']:.5%} {x['r_implied']:.2%}")
        # A1: the printed inputs (S, F, days from the first exhibit; realized q tau to 0.00001%) reproduce every printed column
        tau_p, qr_p = x["days"] / 365.0, round(x["qtau_real"] * 100, 5) / 100
        carry_p = x["S"] * (math.exp(R_PROXY * tau_p) - 1)
        div_p = x["S"] * math.exp(R_PROXY * tau_p) * (1 - math.exp(-qr_p))
        res_p = x["F"] - x["S"] * math.exp(R_PROXY * tau_p - qr_p)
        rimp_p = (qr_p + math.log(x["F"] / x["S"])) / tau_p
        printed = [round(carry_p, 2), round(div_p, 2), round(res_p, 2), round(rimp_p, 4)]
        assert printed == [v[1], v[2], v[3], round(x["r_implied"], 4)], (x["c"], carry_p, div_p, res_p, rimp_p)
    for x in out["near_by_month"]:
        v = [round(x[k]) for k in ("basis", "carry", "div_fv", "residual")]
        assert v[1] - v[2] + v[3] == v[0]
        P(f"   EX12 month {x['m']:2d} days {x['n']} dte {x['days']:.1f} " + " ".join(f"{u:+d}" for u in v) + f" {x['qtau_imp']:.3%} {x['qtau_real']:.3%}")
    for x in out["sep_by_month"]:
        v = [round(x[k]) for k in ("basis", "carry", "div_fv", "residual")]
        assert v[1] - v[2] + v[3] == v[0]
        P(f"   PP12 month {x['m']} sessions {x['n']} ({x['first']}..{x['last']}) " + " ".join(f"{u:+d}" for u in v))
    for w in out["week"][:4]:
        P(f"   WEEK {w['c']} residual {w['residual']:.0f}")
    P("   curve 1 Apr: spring avg {:.0f}, Sep+ avg {:.0f}, gap {:.0f}".format(
        sum(x["basis"] for x in out["curves"]["2025-04-01"][:3]) / 3, sum(x["basis"] for x in out["curves"]["2025-04-01"][3:]) / 3,
        sum(x["basis"] for x in out["curves"]["2025-04-01"][3:]) / 3 - sum(x["basis"] for x in out["curves"]["2025-04-01"][:3]) / 3))
    sn = out["snap"]; P(f"   S on snap {sn[0]['S']:.2f}; Dec PV implied dividends {sn[3]['pvdiv_imp']*sn[3]['S']:.1f} points;"
                        f" residual/S {sn[3]['residual']/sn[3]['S']:.3%}; q_ann {sn[3]['qtau_imp']/sn[3]['tau']:.3%}")
    dec = [x for x in out["dec_series"]]
    P("DEC first/last:", (dec[0]["date"], round(dec[0]["basis"], 2), round(dec[0]["fair_basis"], 1)), (dec[-1]["date"], round(dec[-1]["basis"], 2), round(dec[-1]["fair_basis"], 1)))
    mn = min(dec, key=lambda x: x["basis"]); P("DEC min basis:", mn["date"], round(mn["basis"], 2), round(mn["residual"], 1))
    rb = out["robust"]
    P("ROBUSTNESS OF 27 JUNE (rank 1 = most negative):")
    P(f"   Dec basis rank {rb['dec_basis_rank']}, residual rank {rb['dec_resid_rank']}, r_implied rank {rb['dec_rimp_rank']};"
      f" near-month residual rank {rb['near_resid_rank']}; near-month lowest residuals "
      + str([(x['date'], x['c'], round(x['residual'], 1)) for x in rb['near_resid_min']]))
    P(f"   Dec residual negative on {rb['dec_resid_neg_days']} of {rb['dec_days']} sessions")
    P(f"   centred window {rb['centred_days'][0]}..{rb['centred_days'][-1]} ({len(rb['centred_days'])} sessions): mean residual"
      f" {rb['centred_resid']:.1f}, mean basis {rb['centred_basis']:.1f}, mean implied qtau {rb['centred_qtau_imp']:.2%}")
    P(f"   Dec on 30 June: residual {rb['dec_jun30']['residual']:.1f}, implied financing {rb['dec_jun30']['r_implied']:.2%},"
      f" implied qtau at r_f=0 {rb['dec_jun30']['qtau_r0']:.2%}")
    P(f"   June-July ({rb['junjul_days']} sessions): qtau(r_f=0) > 2025 total {rb['q2025']:.2%} on {rb['junjul_qtau_r0_above_q2025']}"
      f" (last {rb['junjul_last_day_above']}); residual at r_f=0 negative on {rb['junjul_resid_r0_neg']}"
      f" (exceptions {rb['junjul_resid_r0_nonneg_days']})")
    P(f"   TAIEX 17 Dec / 27 Jun = {rb['S_T_over_S_dec']:.4f}")
    j = out["jun30_detail"]
    P(f"30 JUNE: TAIEX {j['S_change']:+.2f} ({j['S_ret']:+.3%}), total-return index {j['TR_ret']:+.3%}; ex-dividend"
      f" {j['exdiv_bp']:.2f} bp = {j['exdiv_points']:.2f} points; July TX {j['F_change']:+.0f} ({j['F_ret']:+.3%});"
      f" basis {j['basis'][0]:.2f} -> {j['basis'][1]:.2f} ({j['basis_change']:+.2f}); residual {j['residual'][0]:.2f} ->"
      f" {j['residual'][1]:.2f}; basis jump net of ex-dividend {j['timing_points']:.1f}; TAIEX 1 Jul {j['S_change_jul1']:+.2f}")
    P("VOLUME on 27 June (lots; last trade - settlement):",
      [(v["c"], v["volume"], v["last_minus_settle"]) for v in out["volume_snap"]])
    vd = out["volume_dec"]
    P(f"   Dec contract: median {vd['median']} lots/day, no trades on {vd['zero_days']} days {vd['zero_dates']};"
      f" largest |last trade - settlement| {vd['max_gap']:+.0f} on {vd['max_gap_date']} ({vd['max_gap_volume']} lot(s));"
      f" Jun 2026 on 30 June: volume {vd['jun26_on_jun30']['volume']}, settlement {vd['jun26_on_jun30']['settlement']:.0f};"
      f" near-month median {vd['near_median']:.0f} lots/day")
    P("   by contract:", [(v["c"], v["n"], v["median"], v["zero_days"]) for v in out["volume_by_contract"]])
    P("   median (max) lots a day by position on the curve:",
      [(v["pos"], v["median"], v["max"]) for v in out["volume_by_position"]])
    P("EX-DIVIDEND INDEX POINTS from 28 June to expiry (vs the yield measure in (6.25)):")
    for x in out["exdiv_points"]:
        P(f"   {x['c']}: points {x['points']:.2f}, carried to expiry {x['points_fv']:.2f}; (6.25) dividends {x['div_fv']:.2f};"
          f" residual with points {x['residual_points']:.2f} vs {x['residual']:.2f}")
