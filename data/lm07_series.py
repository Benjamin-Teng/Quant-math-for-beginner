"""LM7 data: verified daily total-return series for 0050 and 00679B on common trading dates.

Run:  python3 data/lm07_series.py
Writes data/processed/lm07_returns.parquet (and .csv) with columns
    date, R_0050, R_00679B, I_0050, I_00679B
where R are simple total returns between consecutive common trading dates and I are total-return
indices (1.0 on the base date 2017-01-17, the first 00679B close).

Verification (same rules as build_series.py):
  * every close is checked against FinMind's `spread` column with exact decimal arithmetic,
    across chunk boundaries;
  * a mismatch is accepted only on an ex-dividend date listed in the dividend file (where the previous
    close must equal FinMind's `before_price`) or on 0050's split date (4-for-1, 2025-06-18);
  * every ex-dividend date in the window must be a trading date whose previous close equals `before_price`,
    including the ex-dates on which the close did not change and which therefore show no mismatch
    (00679B: 2019-03-05 and 2025-08-21). Dividends are applied on every ex-date from the dividend file.
Each fund's total-return index is built on its own trading calendar; returns are then taken between
consecutive common dates (0050 was halted 2025-06-11..17 for its split while 00679B traded).
"""
import glob
from decimal import Decimal
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
RAW, OUT = HERE / "raw", HERE / "processed"
OUT.mkdir(exist_ok=True)
BASE = "2017-01-17"                       # first 00679B close in the raw files
SPLITS = {"0050": ("2025-06-18", 4)}       # effective date, ratio (new units per old unit)
SYMS = ["0050", "00679B"]


def load(sym):
    files = sorted(glob.glob(str(RAW / f"{sym}__*.csv")))
    df = pl.concat([pl.read_csv(f, schema_overrides={"close": pl.Utf8, "spread": pl.Utf8}) for f in files]).sort("date")
    assert df["date"].is_unique().all(), f"{sym}: duplicate dates"
    c = [Decimal(x) for x in df["close"]]
    s = [Decimal(x) for x in df["spread"]]
    d = df["date"].to_list()
    bad = [(d[i], c[i - 1], c[i], s[i]) for i in range(1, len(c)) if abs(c[i] - c[i - 1] - s[i]) > Decimal("0.005")]
    return df, bad


def verify_and_index(sym):
    df, bad = load(sym)
    div = pl.read_csv(RAW / f"{sym}_dividends.csv", schema_overrides={"before_price": pl.Utf8, "cash_dividend": pl.Utf8})
    dates = df["date"].to_list()
    first = dates[0]
    div = div.filter(pl.col("date") > first)                     # ex-dates inside the price window
    D = {r["date"]: Decimal(r["cash_dividend"]) for r in div.iter_rows(named=True)}
    BEF = {r["date"]: Decimal(r["before_price"]) for r in div.iter_rows(named=True)}
    sdate, sfac = SPLITS.get(sym, (None, 1))
    pos = {x: i for i, x in enumerate(dates)}
    close = [Decimal(x) for x in df["close"]]
    # 1) every mismatch is explained
    expl = []
    for d, p, cl, sp in bad:
        if d in D:
            assert p == BEF[d], (sym, d, p, BEF[d]); expl.append((d, "dividend"))
        elif d == sdate:
            expl.append((d, "split"))
        else:
            raise SystemExit(f"{sym}: UNEXPLAINED spread mismatch on {d}: prev {p} close {cl} spread {sp}")
    # 2) every ex-date is a trading date whose previous close equals before_price
    silent = []
    for d in D:
        assert d in pos, (sym, "ex-date not a trading date", d)
        i = pos[d]
        assert close[i - 1] == BEF[d], (sym, d, close[i - 1], BEF[d])
        if d not in {x for x, _ in expl}:
            silent.append(d)
    n_div = sum(1 for w in expl if w[1] == "dividend")
    print(f"{sym}: rows {df.height}, {dates[0]} -> {dates[-1]}, ex-dates in window {len(D)}, "
          f"dividend mismatches {n_div}, split mismatches {sum(1 for w in expl if w[1] == 'split')}, "
          f"ex-dates without a mismatch (unchanged close) {sorted(silent)}")
    # 3) total-return index on the fund's own calendar
    I, idx = [1.0], []
    for i in range(1, len(dates)):
        k = sfac if dates[i] == sdate else 1
        g = (float(close[i]) + float(D.get(dates[i], 0))) / (float(close[i - 1]) / k)
        I.append(I[-1] * g)
    return pl.DataFrame({"date": dates, f"P_{sym}": [float(x) for x in close], f"I_{sym}": I})


frames = {s: verify_and_index(s) for s in SYMS}
a, b = frames["0050"], frames["00679B"]
only_a = sorted(set(a["date"]) - set(b["date"]))
only_b = sorted(set(b["date"]) - set(a["date"]))
print("dates only in 0050 (from base):", [d for d in only_a if d >= BASE])
print("dates only in 00679B:", only_b)
m = a.join(b, on="date", how="inner").filter(pl.col("date") >= BASE).sort("date")
assert m["date"][0] == BASE
m = m.with_columns(
    (pl.col("I_0050") / pl.col("I_0050").first()).alias("I_0050"),
    (pl.col("I_00679B") / pl.col("I_00679B").first()).alias("I_00679B"),
)
ret = m.with_columns(
    (pl.col("I_0050") / pl.col("I_0050").shift(1) - 1).alias("R_0050"),
    (pl.col("I_00679B") / pl.col("I_00679B").shift(1) - 1).alias("R_00679B"),
)
# the return that spans 0050's split halt (2025-06-10 -> 2025-06-18) for both funds
span = ret.filter(pl.col("date") == "2025-06-18").select("date", "R_0050", "R_00679B")
print("return spanning the 0050 halt:", span.to_dicts())
ret.select("date", "R_0050", "R_00679B", "I_0050", "I_00679B").write_parquet(OUT / "lm07_returns.parquet")
ret.select("date", "R_0050", "R_00679B", "I_0050", "I_00679B").write_csv(OUT / "lm07_returns.csv")
r = ret.drop_nulls("R_0050")
for sym in SYMS:
    dv = pl.read_csv(RAW / f"{sym}_dividends.csv")
    k = dv.filter((pl.col("date") > BASE) & (pl.col("date") <= r["date"][-1])).height
    print(f"{sym}: ex-dates inside the return window {BASE} .. {r['date'][-1]}: {k}")
print(f"returns: {r.height}, {r['date'][0]} -> {r['date'][-1]}; growth 0050 x{r['I_0050'][-1]:.4f}, 00679B x{r['I_00679B'][-1]:.4f}")

# cross-check 0050 against the shared LM3 series (0050/00631L calendar) on intervals that both series share,
# i.e. dates whose previous common date is the same in both (00631L's split halt merges 2026-03-25..31 there)
shared = OUT / "etf_daily_returns.parquet"
if shared.exists():
    s = (pl.read_parquet(shared).select("date", "R_0050").sort("date")
         .with_columns(pl.col("date").shift(1).alias("prev")).rename({"R_0050": "R_lm03"}))
    mine = r.select("date", "R_0050").sort("date").with_columns(pl.col("date").shift(1).alias("prev"))
    j = mine.join(s, on=["date", "prev"], how="inner")
    diff = (j["R_0050"] - j["R_lm03"]).abs().max()
    print(f"cross-check vs etf_daily_returns.parquet on {j.height} shared intervals: max |diff| = {diff:.1e}")
    assert diff < 1e-12
