"""Merge verified FinMind chunks into total-return daily series for 0050 and 00631L."""
import glob, polars as pl
from pathlib import Path
from decimal import Decimal
HERE = Path(__file__).resolve().parent
RAW = str(HERE / "raw"); OUT = str(HERE / "processed")
Path(OUT).mkdir(exist_ok=True)
SPLITS = {"0050": ("2025-06-18", 4), "00631L": ("2026-03-31", 22)}

def load(sym):
    files = sorted(glob.glob(f"{RAW}/{sym}__*.csv"))
    df = pl.concat([pl.read_csv(f, schema_overrides={"close": pl.Utf8, "spread": pl.Utf8}) for f in files]).sort("date")
    assert df["date"].is_unique().all(), "duplicate dates"
    # boundary + global checksum (Decimal exact)
    c = [Decimal(x) for x in df["close"]]; s = [Decimal(x) for x in df["spread"]]
    bad = [(df["date"][i], str(c[i-1]), str(c[i]), str(s[i])) for i in range(1, len(c)) if abs(c[i]-c[i-1]-s[i]) > Decimal("0.005")]
    return df.with_columns(pl.col("close").cast(pl.Float64)), bad

div = pl.read_csv(f"{RAW}/0050_dividends.csv")
out = {}
for sym in ["0050", "00631L"]:
    df, bad = load(sym)
    divd = dict(zip(div["date"], div["cash_dividend"])) if sym == "0050" else {}
    befd = dict(zip(div["date"], div["before_price"])) if sym == "0050" else {}
    sdate, sfac = SPLITS[sym]
    expl = []
    for d, p, cl, sp in bad:
        why = "dividend" if d in divd else ("split" if d == sdate else "UNEXPLAINED")
        if why == "dividend":
            assert abs(float(p) - befd[d]) < 1e-9, (sym, d, p, befd[d])
        expl.append((d, why))
    print(sym, "rows", df.height, df["date"][0], "->", df["date"][-1], "| mismatches:", expl)
    assert all(w != "UNEXPLAINED" for _, w in expl)
    out[sym] = df.select("date", "close").with_columns(
        pl.col("date").map_elements(lambda d: divd.get(d, 0.0), return_dtype=pl.Float64).alias("div"),
        pl.when(pl.col("date") == sdate).then(sfac).otherwise(1).cast(pl.Float64).alias("split"))

# align on common dates; returns between consecutive common dates
a = out["0050"].rename({"close": "p0050", "div": "d0050", "split": "s0050"})
b = out["00631L"].rename({"close": "p00631L", "div": "d00631L", "split": "s00631L"})
only_a = set(a["date"]) - set(b["date"]); only_b = set(b["date"]) - set(a["date"])
print("dates only in 0050:", sorted(only_a)); print("dates only in 00631L:", sorted(only_b))
# fold split/dividend flags of non-common days into next common day (none expected except halts)
m = a.join(b, on="date", how="full", coalesce=True).sort("date")
m.write_csv(f"{OUT}/raw_merged_full.csv")
common = a.join(b, on="date", how="inner").sort("date")
# carry corporate actions that occurred on dates missing in the other series: none of the split dates are missing
for sym, (sd, f) in SPLITS.items():
    assert sd in set(common["date"]), sd
common = common.with_columns(
    ((pl.col("p0050") + pl.col("d0050")) / (pl.col("p0050").shift(1) / pl.col("s0050")) - 1).alias("R_0050"),
    ((pl.col("p00631L") + pl.col("d00631L")) / (pl.col("p00631L").shift(1) / pl.col("s00631L")) - 1).alias("R_00631L"),
).drop_nulls("R_0050")
common.write_csv(f"{OUT}/etf_daily_returns.csv")
common.write_parquet(f"{OUT}/etf_daily_returns.parquet")
print(common.height, common["date"][0], common["date"][-1])
