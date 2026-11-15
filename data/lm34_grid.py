"""LM34's declared grid (Backtesting Without Fooling Yourself): the 60 configurations' net returns, written to
data/processed/lm34_grid.parquet (git-ignored), from which data/make_lab_data.py writes labs/LM34_lab/data/lm34_grid.csv.

Run:  PYTHONUTF8=1 uv run python data/lm34_grid.py
      (after data/vol5_series.py and data/vol5_rules.py; data/make_lab_data.py runs it when the parquet is missing,
      and data/lm34_numbers.py asserts that the file equals the table it builds from the full computation)

Inputs: E5's frames through vol5_series.frames("E5") (data/processed/vol5_frames.parquet) and vol5_rules.py, through
data/lm34_common.py's grid_paths() and grid_frame(); no rule is re-implemented. It reads no ETF snapshot, no TR23 and
no file under data/raw/vol6/, so it runs on FinMind's free plan. It also checks that the eight configurations the
through case trades (R1 and R2 monthly, R3-R8 monthly at the 504-date window) give exactly the net wealth that
data/processed/vol5_rules.parquet holds.

The table: a column `date`, then one column per configuration in the declared grid order (R1_1m, R1_3m, R1_6m, R2_1m,
..., R3_126_1m, R3_126_3m, ..., R8_504_6m). Its first row, 2019-03-04, is the first purchase from the cash of 1
(wealth after it minus 1, so minus the cost share); the 1,851 rows from 2019-03-05 to 2026-10-08 are the daily net
returns that CSCV and the reality check use, and the product of one plus every row is the final wealth.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lm34_common as C
import numpy as np
import polars as pl
import vol5_rules as V
from vol5_series import frames

OUT = C.PROC / "lm34_grid.parquet"
RULES_PATH = C.PROC / "vol5_rules.parquet"


def main() -> None:
    if not RULES_PATH.exists():
        sys.exit("lm34_grid: run data/vol5_rules.py first (it writes data/processed/vol5_rules.parquet)")
    fr = frames("E5")
    gp = C.grid_paths(fr, V.signals(fr, []))
    ref = pl.read_parquet(RULES_PATH)
    for k in V.RULES:                                  # the through case's own configuration of each rule
        p = gp.paths[gp.conf.index((k, 0 if k in ("R1", "R2") else 504, 1))]
        r = ref.filter(pl.col("rule") == k)
        assert r["date"].to_list() == p.dates, k
        assert np.array_equal(r["wealth"].to_numpy(), p.wealth), k
    df = C.grid_frame(gp)
    assert df.height == 1852 and df.width == 61, df.shape
    assert (df["date"][0], df["date"][1], df["date"][-1]) == ("2019-03-04", "2019-03-05", "2026-10-08")
    assert df.columns[1:4] == ["R1_1m", "R1_3m", "R1_6m"] and df.columns[-1] == "R8_504_6m"
    OUT.parent.mkdir(exist_ok=True)
    df.write_parquet(OUT)
    print(f"wrote data/processed/lm34_grid.parquet ({df.height} rows, {df.width} columns: date and 60 configurations; "
          "the first row is the first purchase); the eight through-case configurations equal "
          "data/processed/vol5_rules.parquet's net wealth")


if __name__ == "__main__":
    main()
