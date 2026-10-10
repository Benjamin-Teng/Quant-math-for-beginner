"""LM2 motivating case: the equity elasticity of a TX futures account equals its leverage.

Inputs (verified FinMind files, regular session only):
  raw/TX__2025-04-01__2025-10-31.csv     date,contract_date,close,settlement_price,volume,open_interest
  raw/TAIEX__2025-04-01__2025-10-31.csv  date,close,spread
Output: processed/lm02_case.json and a printed report of every number quoted in LM2 from these files.
Run:  python3 data/lm02_case.py
"""
import json
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
TX_FILE = HERE / "raw" / "TX__2025-04-01__2025-10-31.csv"
TAIEX_FILE = HERE / "raw" / "TAIEX__2025-04-01__2025-10-31.csv"
M_TX = 200            # NT$ per index point (TAIFEX contract specification, TX)
EQ_A, EQ_B = 600_000, 900_000      # equity of the two case accounts (NT$)
IM_ILLUS = 350_000    # ILLUSTRATIVE initial margin per TX contract (not a TAIFEX figure)


def load():
    tx = pl.read_csv(TX_FILE)
    ta = pl.read_csv(TAIEX_FILE)
    assert tx.group_by("date").len()["len"].unique().to_list() == [6], "expected 6 contracts per day"
    assert sorted(tx["date"].unique().to_list()) == ta["date"].to_list(), "date sets differ"
    return tx, ta


def held_series(tx, ta):
    """Near-month contract held at each close, rolled at the close of the day before expiry.

    On an expiry day the expiring contract's settlement_price is printed as 0.0 (its final settlement is not in
    the file), so a position must leave it one session earlier. Closing the old and opening the new contract at
    their settlement prices on the roll day is P&L-neutral under daily mark-to-market."""
    dates = ta["date"].to_list()
    expiry = sorted(tx.filter(pl.col("settlement_price") == 0)["date"].to_list())
    exp_of = {int(d[:4] + d[5:7]): d for d in expiry}
    px = {(r["date"], r["contract_date"]): r["settlement_price"] for r in tx.iter_rows(named=True)}
    held = []
    for i, d in enumerate(dates):
        nxt = dates[i + 1] if i + 1 < len(dates) else d     # last day: any contract not expiring in the file
        months = sorted(tx.filter(pl.col("date") == d)["contract_date"].to_list())
        held.append(next(c for c in months if exp_of.get(c, "9999-12-31") > nxt))
    rows = []
    S = ta["close"].to_list()
    for i in range(1, len(dates)):
        c = held[i - 1]
        f0, f1 = px[(dates[i - 1], c)], px[(dates[i], c)]
        assert f0 > 0 and f1 > 0, (dates[i], c)
        rows.append({"date": dates[i], "contract": c, "F0": f0, "F1": f1, "S0": S[i - 1], "S1": S[i],
                     "held_next": held[i]})
    df = pl.DataFrame(rows).with_columns(
        (pl.col("F1") / pl.col("F0") - 1).alias("RF"),
        (pl.col("S1") / pl.col("S0") - 1).alias("RS"))
    # settlement of the contract held from this close onwards (differs from F1 only on roll days)
    nxt = tx.select("date", pl.col("contract_date").alias("held_next"), pl.col("settlement_price").alias("F_next"))
    df = df.join(nxt, on=["date", "held_next"], how="left").sort("date")
    assert df["F_next"].null_count() == 0 and (df["F_next"] > 0).all()
    return df, expiry


def account_path(df, start_date, E0, n=1):
    """Equity and leverage of an account holding n contracts from the close of start_date (inclusive)."""
    sub = df.filter(pl.col("date") > start_date)
    first = df.filter(pl.col("date") == start_date)
    F_open = first["F_next"][0] if first.height else None
    E, out = float(E0), []
    out.append({"date": start_date, "F": F_open, "E": E, "f": n * M_TX * F_open / E})
    for r in sub.iter_rows(named=True):
        E += n * M_TX * (r["F1"] - r["F0"])
        f = n * M_TX * r["F_next"] / E if E > 0 else float("nan")
        out.append({"date": r["date"], "F": r["F_next"], "E": E, "f": f, "pnl": n * M_TX * (r["F1"] - r["F0"])})
    return out


def main():
    tx, ta = load()
    df, expiry = held_series(tx, ta)
    res = {"expiry_days": expiry, "n_returns": df.height}
    print(f"TX expiry days in file: {expiry}")
    print(f"daily returns: {df.height}  ({df['date'][0]} -> {df['date'][-1]})")

    # ---- the two case days
    case = {}
    for d in ("2025-06-11", "2025-04-07"):
        r = df.filter(pl.col("date") == d).row(0, named=True)
        pnl = M_TX * (r["F1"] - r["F0"])
        notional0 = M_TX * r["F0"]
        row = dict(date=d, contract=r["contract"], S0=r["S0"], S1=r["S1"], RS=r["RS"], F0=r["F0"], F1=r["F1"],
                   RF=r["RF"], points=r["F1"] - r["F0"], pnl=pnl, notional0=notional0,
                   fA=notional0 / EQ_A, fB=notional0 / EQ_B, RA=pnl / EQ_A, RB=pnl / EQ_B,
                   ratioA=(pnl / EQ_A) / r["RS"], ratioB=(pnl / EQ_B) / r["RS"], eps_FS=r["RF"] / r["RS"],
                   limit_down=round(r["F0"] * 0.9, 1))
        case[d] = row
        print(f"\nCASE {d}: contract {r['contract']}")
        print(f"  TAIEX {r['S0']:,.2f} -> {r['S1']:,.2f}  RS = {r['RS']:+.4%}")
        print(f"  TX    {r['F0']:,.0f} -> {r['F1']:,.0f}  ({r['F1']-r['F0']:+,.0f} pts)  RF = {r['RF']:+.4%}  "
              f"limit price 0.9*F0 = {r['F0']*0.9:,.1f}")
        print(f"  P&L per contract NT$ {pnl:+,.0f}; notional at previous settlement NT$ {notional0:,.0f}")
        print(f"  f_A = {notional0/EQ_A:.4f}  R_A = {pnl/EQ_A:+.4%}  R_A/RS = {(pnl/EQ_A)/r['RS']:.3f}")
        print(f"  f_B = {notional0/EQ_B:.4f}  R_B = {pnl/EQ_B:+.4%}  R_B/RS = {(pnl/EQ_B)/r['RS']:.3f}")
        print(f"  check f_A*RF = {notional0/EQ_A*r['RF']:+.4%}   measured eps(F,S) = RF/RS = {r['RF']/r['RS']:.4f}")
        print(f"  max leverage at illustrative IM {IM_ILLUS:,}: {notional0/IM_ILLUS:.2f}")
    res["case"] = case

    # ---- typical day and futures-vs-index statistics over the window
    RS, RF = df["RS"].to_numpy(), df["RF"].to_numpy()
    beta = np.polyfit(RS, RF, 1)[0]
    stats = dict(med_abs_RS=float(np.median(np.abs(RS))), med_abs_RF=float(np.median(np.abs(RF))),
                 corr=float(np.corrcoef(RS, RF)[0, 1]), slope_RF_on_RS=float(beta),
                 sd_RS=float(RS.std(ddof=1)), sd_RF=float(RF.std(ddof=1)),
                 n_roll_days=int((df["contract"] != df["held_next"]).sum()))
    near1 = df.filter(pl.col("RS").abs().is_between(0.009, 0.011))
    stats["n_near_1pct"] = near1.height
    stats["near1_ratio_RF_RS_min"] = float((near1["RF"] / near1["RS"]).min())
    stats["near1_ratio_RF_RS_max"] = float((near1["RF"] / near1["RS"]).max())
    res["stats"] = stats
    print(f"\nWINDOW: median |RS| = {stats['med_abs_RS']:.3%}, median |RF| = {stats['med_abs_RF']:.3%}, "
          f"corr = {stats['corr']:.3f}, OLS slope RF on RS = {beta:.3f}, sd RS = {stats['sd_RS']:.3%}, sd RF = {stats['sd_RF']:.3%}")
    print(f"  days with 0.9% <= |RS| <= 1.1%: {near1.height}; RF/RS on those days from "
          f"{stats['near1_ratio_RF_RS_min']:.3f} to {stats['near1_ratio_RF_RS_max']:.3f}")
    print(f"  roll days: {stats['n_roll_days']}")
    # roll gains: settlement of the new contract minus the old one at each roll close (negative = new is cheaper)
    rolls = df.filter(pl.col("contract") != pl.col("held_next")).select(
        "date", "contract", "held_next", "F1", "F_next", (pl.col("F_next") - pl.col("F1")).alias("new_minus_old"))
    print(rolls)
    res["rolls"] = rolls.to_dicts()

    # ---- leverage path from the case day to the end of the window (Section 6 chart)
    paths = {}
    for lab, E0 in (("A", EQ_A), ("B", EQ_B)):
        p = account_path(df, "2025-06-10", E0)
        paths[lab] = p
        last = p[-1]
        fmin = min(x["f"] for x in p); fmax = max(x["f"] for x in p)
        print(f"\nPATH {lab}: start 2025-06-10 E0={E0:,} f0={p[0]['f']:.3f}; 2025-06-11 E={p[1]['E']:,.0f} f={p[1]['f']:.3f}; "
              f"end {last['date']} F={last['F']:,.0f} E={last['E']:,.0f} f={last['f']:.3f}; f range {fmin:.3f}-{fmax:.3f}")
    res["paths"] = paths
    # first-order check of eps(f,F) = 1 - f on the case day for account A
    a0, a1 = paths["A"][0], paths["A"][1]
    dlnF = np.log(case["2025-06-11"]["F1"] / case["2025-06-11"]["F0"])
    pred = a0["f"] * np.exp((1 - a0["f"]) * dlnF)
    lev_after = M_TX * case["2025-06-11"]["F1"] / a1["E"]
    print(f"  eps(f,F)=1-f check (A, 11 Jun): f0={a0['f']:.4f} -> exact {lev_after:.4f}; log-linear prediction {pred:.4f}; "
          f"linear prediction {a0['f']*(1+(1-a0['f'])*case['2025-06-11']['RF']):.4f}")
    res["lev_check_0611"] = dict(f0=a0["f"], f1=lev_after, pred_log=float(pred),
                                 pred_lin=a0["f"] * (1 + (1 - a0["f"]) * case["2025-06-11"]["RF"]))
    # cumulative: account A from 10 Jun to 31 Oct
    pa = paths["A"]; pb = paths["B"]
    gainA = pa[-1]["E"] - EQ_A
    print(f"  A: equity gain {gainA:,.0f} (= {gainA/M_TX:,.0f} points) ; B: {pb[-1]['E']-EQ_B:,.0f}")
    S_06_10 = df.filter(pl.col("date") == "2025-06-11")["S0"][0]; S_end = df["S1"][-1]
    print(f"  TAIEX 2025-06-10 {S_06_10:,.2f} -> 2025-10-31 {S_end:,.2f}: {S_end/S_06_10-1:+.2%}; "
          f"account A {pa[-1]['E']/EQ_A-1:+.2%}, B {pb[-1]['E']/EQ_B-1:+.2%}; f0*index = {pa[0]['f']*(S_end/S_06_10-1):+.2%}")
    roll_after = rolls.filter(pl.col("date") > "2025-06-10")["new_minus_old"].sum()
    F_first = pa[0]["F"]; F_last = pa[-1]["F"]
    pts = gainA / M_TX
    print(f"  near-month price {F_first:,.0f} -> {F_last:,.0f} ({F_last-F_first:+,.0f} pts); roll adjustments {roll_after:+,.0f} pts; "
          f"held-contract points {pts:+,.0f} = {pts/F_first:.2%} of F0; f0 x that = {pa[0]['f']*pts/F_first:.2%}; "
          f"TAIEX points {S_end-S_06_10:+,.2f}")
    b0, b1 = F_first - S_06_10, F_last - S_end
    print(f"  basis (near-month settlement - TAIEX close): 2025-06-10 {b0:+.2f}, 2025-10-31 {b1:+.2f}; change {b1-b0:+.2f}; "
          f"excess of futures points over TAIEX points {pts-(S_end-S_06_10):+.2f} = basis change {b1-b0:+.2f} + rolls {-roll_after:+.0f}")
    res["cum"] = dict(S0=S_06_10, S1=S_end, RS=S_end / S_06_10 - 1, RA=pa[-1]["E"] / EQ_A - 1, RB=pb[-1]["E"] / EQ_B - 1,
                      gainA=gainA, gainB=pb[-1]["E"] - EQ_B, roll_pts=roll_after, pts=pts, F_first=F_first, F_last=F_last,
                      basis0=b0, basis1=b1)

    # ---- April 2025: leverage near wipe-out (Section 7)
    crash = {}
    for lab, E0 in (("A", EQ_A), ("B", EQ_B)):
        p = account_path(df, "2025-04-02", E0)[:5]
        crash[lab] = p
        print(f"\nAPRIL {lab} (E0={E0:,}):")
        for x in p:
            print(f"  {x['date']}  F={x['F']:,.0f}  E={x['E']:>12,.0f}  f={x['f']:.3f}")
    res["crash"] = crash
    F0 = crash["B"][0]["F"]; f0 = crash["B"][0]["f"]
    print(f"  wipe-out level A: {F0 - EQ_A/M_TX:,.0f}; B: {F0 - EQ_B/M_TX:,.0f}")
    lin = []
    for x in crash["B"][1:5]:
        dF = x["F"] - F0
        df_lin = -f0 * (f0 - 1) / F0 * dF
        lin.append(dict(date=x["date"], F=x["F"], move=x["F"] / F0 - 1, f_exact=x["f"], f_lin=f0 + df_lin))
        print(f"  B first-order from 2 Apr: {x['date']} cum move {x['F']/F0-1:+.2%}  f exact {x['f']:.3f}  f linear {f0+df_lin:.3f}")
    # a hypothetical 1% fall from 2 April for comparison
    F1 = F0 * 0.99; E1 = EQ_B + M_TX * (F1 - F0); f1 = M_TX * F1 / E1
    lin1 = f0 + (-f0 * (f0 - 1) / F0) * (F1 - F0)
    print(f"  B hypothetical -1% from 2 Apr: f exact {f1:.4f}, linear {lin1:.4f}, error {f1-lin1:.4f}")
    res["crash_lin"] = lin
    res["crash_1pct"] = dict(f_exact=f1, f_lin=lin1)

    def conv(o):
        if isinstance(o, dict): return {k: conv(v) for k, v in o.items()}
        if isinstance(o, list): return [conv(v) for v in o]
        if isinstance(o, (np.floating,)): return float(o)
        if isinstance(o, (np.integer,)): return int(o)
        return o
    (HERE / "processed").mkdir(exist_ok=True)
    (HERE / "processed" / "lm02_case.json").write_text(json.dumps(conv(res), indent=1))
    print("\nwrote data/processed/lm02_case.json")


if __name__ == "__main__":
    main()
