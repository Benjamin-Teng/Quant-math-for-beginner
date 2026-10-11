"""Numbers for LM8 (Vectors and Matrices): every value src/lm08.md quotes, recomputed and checked.

Run:  uv run python data/lm08_numbers.py

Inputs: data/raw/ (TX__2025-04-01__2025-10-31.csv, the 0050 and 00679B close chunks, both dividend files and the
sectors_close/ file names) and data/processed/: vol2_closes.parquet (the repaired sector closes, data/vol2_series.py),
lm07_returns.parquet (data/lm07_series.py) and etf_daily_returns.parquet (data/build_series.py). The case is computed
in exact arithmetic (Decimal prices, Fraction returns).

Every quoted value passes two checks (project/PITFALLS.md section 7): its formatted value equals the printed text, and
the printed text appears in src/lm08.md. A hand calculation is recomputed from the inputs printed next to it, not
from unrounded ones. The script also checks the price changes that src/lm08.js embeds and the output that the Python
box of Section 7 prints. data/lm08_charts.py imports the loaders below.
"""
from __future__ import annotations

import contextlib
import csv
import io
import json
import math
import re
import runpy
import tempfile
from datetime import date
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RAW, PROC = HERE / "raw", HERE / "processed"

CASE_DATES = ["2025-04-02", "2025-04-07", "2025-04-08", "2025-04-09", "2025-04-10", "2025-04-11"]
INSTRUMENTS = ["TX", "0050", "00679B"]
H = (Decimal(-1), Decimal(24_000), Decimal(100_000))      # the case book: TX contracts, 0050 and 00679B shares
H_B = (Decimal(-1), Decimal(20_000), Decimal(100_000))    # the second trader's book (Example 1, knowledge checks)
H_P2 = (Decimal(2), Decimal(0), Decimal(200_000))         # Practice Problems 2 and 3
W0 = Decimal(10_000_000)
TX_MULT = Decimal(200)                                    # NT$ per index point per TX contract (TAIFEX)
AGG = ("Electronic", "ChemicalBiotechnologyMedicalCare")  # aggregate sector indices, not in U28
U28_FIRST, LAST = "2008-12-01", "2026-10-08"
LM7_BASE = "2017-01-17"
PAIRS = [   # the bars of the `angles` exhibit, left to right: (id, label in the chart, series 1, series 2)
    ("etf", "0050/00631L", "0050", "00631L"),
    ("u28", "Parts/Computer", "ElectronicPartsComponents", "ComputerPeripheralEquipment"),
    ("u28", "Semi/Financial", "Semiconductor", "FinancialInsurance"),
    ("u28", "Semi/Food", "Semiconductor", "Food"),
    ("u28", "Biotech/OilGas", "BiotechnologyMedicalCare", "OilGasElectricity"),
    ("lm7", "0050/00679B", "0050", "00679B"),
]


# ---------------------------------------------------------------------------------------------------- loaders
def read_chunks(pattern: str) -> dict[str, list[str]]:
    """Merge raw `date,close,spread` chunks: one row per date, exact duplicates allowed, conflicts refused."""
    rows: dict[str, list[str]] = {}
    for f in sorted(RAW.glob(pattern)):
        with open(f, newline="", encoding="utf-8") as fh:
            body = list(csv.reader(fh))[1:]
        for r in body:
            if r[0] in rows and rows[r[0]] != r:
                raise SystemExit(f"conflicting rows for {r[0]} in data/raw/{pattern}")
            rows[r[0]] = r
    if not rows:
        raise SystemExit(f"missing data/raw/{pattern}: run uv run python data/fetch_finmind.py")
    return dict(sorted(rows.items()))


def dividend_dates(name: str) -> list[str]:
    with open(RAW / name, newline="", encoding="utf-8") as fh:
        return [r["date"] for r in csv.DictReader(fh)]


def taiex_calendar() -> list[str]:
    return pl.read_parquet(PROC / "vol2_closes.parquet").sort("date")["date"].to_list()


def case() -> dict:
    """The case week: TX 202504 daily settlement, 0050 and 00679B closes, as exact decimals (NT$ per unit)."""
    tx: dict[str, dict[str, str]] = {}
    with open(RAW / "TX__2025-04-01__2025-10-31.csv", newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["contract_date"] == "202504":
                tx[r["date"]] = r
    p50, p679 = read_chunks("0050__*.csv"), read_chunks("00679B__*.csv")
    F = [Decimal(tx[d]["settlement_price"]) for d in CASE_DATES]
    P = [[TX_MULT * F[k], Decimal(p50[d][1]), Decimal(p679[d][1])] for k, d in enumerate(CASE_DATES)]
    # the six dates are consecutive TAIEX sessions, and 202504 is still trading after them (expiry 2025-04-16)
    cal = taiex_calendar()
    i0 = cal.index(CASE_DATES[0])
    assert cal[i0:i0 + 6] == CASE_DATES, cal[i0:i0 + 6]
    expiry = [d for d, r in tx.items() if Decimal(r["settlement_price"]) == 0]
    assert expiry == ["2025-04-16"], expiry
    # no ex-dividend date in (2 April, 11 April]; 0050's split (2025-06-18) comes later: price changes are total changes
    for name in ("0050_dividends.csv", "00679B_dividends.csv"):
        assert not [d for d in dividend_dates(name) if CASE_DATES[0] < d <= CASE_DATES[-1]], name
    return {"F": F, "volume": [int(tx[d]["volume"]) for d in CASE_DATES], "P": P, "p50": p50, "p679": p679}


def week_returns(c: dict) -> list[list[Fraction]]:
    """Exact simple returns, 5 sessions x (TX, 0050, 00679B); TX from its daily settlement price."""
    P = c["P"]
    return [[(Fraction(P[k][i]) - Fraction(P[k - 1][i])) / Fraction(P[k - 1][i]) for i in range(3)]
            for k in range(1, 6)]


def lm7_pair() -> tuple[np.ndarray, np.ndarray, list[str]]:
    """LM7's frame: 0050 and 00679B total returns between consecutive common dates from 2017-01-17 (T = 2,363)."""
    df = pl.read_parquet(PROC / "lm07_returns.parquet").sort("date").drop_nulls("R_0050")
    return df["R_0050"].to_numpy(), df["R_00679B"].to_numpy(), df["date"].to_list()


def lm1_pair() -> tuple[np.ndarray, np.ndarray, list[str]]:
    """LM1's frame: 0050 and 00631L total returns on their common dates (T = 2,902)."""
    df = pl.read_parquet(PROC / "etf_daily_returns.parquet").sort("date")
    return df["R_0050"].to_numpy(), df["R_00631L"].to_numpy(), df["date"].to_list()


def u28() -> tuple[list[str], np.ndarray, list[str]]:
    """U28: the 28 leaf sector indices, simple price returns between consecutive closes from 2008-12-01 (T = 4,382)."""
    cl = pl.read_parquet(PROC / "vol2_closes.parquet").sort("date")
    names = [c for c in cl.columns if c not in ("date", "TAIEX", *AGG)]
    smp = cl.filter(pl.col("date") >= pl.lit(U28_FIRST))
    P = smp.select(names).to_numpy()
    assert len(names) == 28 and not np.isnan(P).any()
    return names, P[1:] / P[:-1] - 1, smp["date"].to_list()


def corr(x: np.ndarray, y: np.ndarray) -> float:
    return float(np.corrcoef(x, y)[0, 1])


def cos_uncentred(x: np.ndarray, y: np.ndarray) -> float:
    return float(x @ y / np.linalg.norm(x) / np.linalg.norm(y))


def angle(c: float) -> float:
    return math.degrees(math.acos(c))


def angles_pairs() -> list[dict]:
    """The six pairs of the `angles` exhibit: correlation of the centred daily return vectors and its angle."""
    names, X, _ = u28()
    ix = {n: i for i, n in enumerate(names)}
    lm1, lm7 = lm1_pair(), lm7_pair()
    out = []
    for src, label, a, b in PAIRS:
        if src == "u28":
            rho = corr(X[:, ix[a]], X[:, ix[b]])
        else:
            rho = corr(*(lm1 if src == "etf" else lm7)[:2])
        out.append({"label": label, "a": a, "b": b, "rho": rho, "deg": angle(rho)})
    return out


def lm7_vols() -> dict:
    """Annualized volatilities (divisor T) of LM7's frame, A = T / years (years = calendar days / 365.25)."""
    a, b, d = lm7_pair()
    years = (date.fromisoformat(d[-1]) - date.fromisoformat(LM7_BASE)).days / 365.25
    A = len(a) / years
    return {"T": len(a), "A": A, "s1": float(a.std() * math.sqrt(A)), "s2": float(b.std() * math.sqrt(A)),
            "rho": corr(a, b), "a": a, "b": b}


# ---------------------------------------------------------------------------------------------------- checks
TEXT = (ROOT / "src" / "lm08.md").read_text(encoding="utf-8")
FAILS: list[str] = []


def forms(s: str) -> set[str]:
    """The ways a printed number appears in the source: prose (U+2212 minus, 1,000) or math (-, 1{,}000, \\%, ^\\circ)."""
    out = {s, s.replace(",", "{,}")}
    out |= {"−" + t[1:] for t in out if t.startswith("-")} | {t[1:] for t in out if t.startswith("+")}
    return out | {t.replace("%", "\\%").replace("°", "^\\circ") for t in out}


def chk(label: str, value: float | Fraction | Decimal, fmt: str, printed: str, *, suffix: str = "",
        in_text: bool = True) -> None:
    """Assert format(value, fmt) + suffix == printed, and that printed appears in src/lm08.md."""
    got = format(float(value) if isinstance(value, Fraction) else value, fmt) + suffix
    ok_txt = (not in_text) or any(f in TEXT for f in forms(printed))
    ok = got == printed and ok_txt
    print(f"{'ok  ' if ok else 'FAIL'} {label}: {got} (printed {printed}){'' if ok_txt else '  <- not in src/lm08.md'}")
    if not ok:
        FAILS.append(label)


def in_text(*needles: str) -> None:
    """Assert that each exact string appears in src/lm08.md (formulas and table rows quoted as written)."""
    for s in needles:
        ok = s in TEXT
        print(f"{'ok  ' if ok else 'FAIL'} text contains: {s}")
        if not ok:
            FAILS.append(s)


def rnd(x: float | Fraction, nd: int) -> Fraction:
    """Round half away from zero to nd decimals, exactly (the printed value as a number)."""
    q = Fraction(x) * 10**nd
    n = math.floor(abs(q) + Fraction(1, 2))
    return Fraction(n if q >= 0 else -n, 10**nd)


def main() -> None:
    P_ = print
    # ================================================================================ case (Introduction, Section 2)
    c = case()
    P, F = c["P"], c["F"]
    P_("TX 202504 settlement:", [str(x) for x in F], "volume:", c["volume"])
    P_("0050:", [str(p[1]) for p in P], " 00679B:", [str(p[2]) for p in P])
    chk("TX 2 Apr", F[0], ",.0f", "21,296")
    chk("TX 7 Apr", F[1], ",.0f", "19,167")
    chk("TX change 7 Apr (points)", F[1] - F[0], ",.0f", "-2,129")
    chk("0050 2 Apr", P[0][1], ".2f", "176.00")
    chk("0050 7 Apr", P[1][1], ".2f", "158.40")
    chk("0050 change 7 Apr", P[1][1] - P[0][1], ".2f", "-17.60")
    chk("00679B 2 Apr", P[0][2], ".2f", "29.88")
    chk("00679B 7 Apr", P[1][2], ".2f", "30.42")
    chk("00679B change 7 Apr", P[1][2] - P[0][2], "+.2f", "+0.54")
    chk("TX volume 2 Apr", c["volume"][0], ",d", "66,423")
    chk("TX volume 7 Apr", c["volume"][1], ",d", "2,736")
    X = week_returns(c)
    chk("R TX 7 Apr", X[0][0], "+.4%", "-9.9972%")
    chk("R 0050 7 Apr", X[0][1], "+.4%", "-10.0000%")
    chk("R 00679B 7 Apr", X[0][2], "+.4%", "+1.8072%")
    assert X[0][1] == Fraction(-1, 10)                     # 176.00 -> 158.40 is exactly -10%
    chk("R TX 7 Apr (vector)", X[0][0], ".7f", "-0.0999718")
    chk("R 0050 7 Apr (vector)", X[0][1], ".7f", "-0.1000000")
    chk("R 00679B 7 Apr (vector)", X[0][2], ".7f", "0.0180723")
    P_(f"   floats: 158.4/176.0 - 1 = {158.4 / 176.0 - 1!r}; (158.4 - 176.0)/176.0 = {(158.4 - 176.0) / 176.0!r}")
    lines7 = [H[i] * (P[1][i] - P[0][i]) for i in range(3)]
    chk("TX line 7 Apr", lines7[0], "+,.0f", "+425,800")
    chk("0050 line 7 Apr", lines7[1], "+,.0f", "-422,400")
    chk("00679B line 7 Apr", lines7[2], "+,.0f", "+54,000")
    chk("book 7 Apr", sum(lines7), "+,.0f", "+57,400")
    chk("hedge pair 7 Apr (TX + 0050 lines)", lines7[0] + lines7[1], ",.0f", "3,400")
    chk("TX per-contract change 7 Apr", P[1][0] - P[0][0], ",.0f", "-425,800")
    in_text("425{,}800-422{,}400+54{,}000\\\\&=57{,}400", "200\\times(19{,}167-21{,}296)=-425{,}800")
    # TAIEX on 7 April: the largest absolute daily move of the whole calendar 2007-07-02 .. 2026-10-08
    tx_idx = pl.read_parquet(PROC / "vol2_closes.parquet").sort("date").select("date", "TAIEX")
    ti = tx_idx["TAIEX"].to_numpy()
    rt = ti[1:] / ti[:-1] - 1
    k = int(np.argmax(np.abs(rt)))
    assert tx_idx["date"][k + 1] == "2025-04-07" and tx_idx["date"][0] == "2007-07-02" and tx_idx["date"][-1] == LAST
    chk("TAIEX fall on 7 Apr (largest |move| 2007-07 .. 2026-10)", -rt[k], ".4%", "9.6997%")
    # the notionals of the case box and the exposures (Example 3, Section 3)
    vals = [H[i] * P[0][i] for i in range(3)]
    chk("TX notional (millions)", -vals[0] / Decimal(10**6), ".2f", "4.26")
    chk("0050 notional (millions)", vals[1] / Decimal(10**6), ".2f", "4.22")
    chk("value TX", vals[0], ",.0f", "-4,259,200")
    chk("value 0050", vals[1], ",.0f", "4,224,000")
    chk("value 00679B", vals[2], ",.0f", "2,988,000")
    f = [v / W0 for v in vals]
    chk("f TX", f[0], ".5f", "-0.42592")
    chk("f 0050", f[1], ".4f", "0.4224")
    chk("f 00679B", f[2], ".4f", "0.2988")
    prods = [Fraction(f[i]) * X[0][i] for i in range(3)]
    assert all(prods[i] * Fraction(W0) == Fraction(lines7[i]) for i in range(3))      # f_i R_i = h_i dP_i / W0, exactly
    chk("f R TX", prods[0], ".6f", "0.042580")
    chk("f R 0050", prods[1], ".6f", "-0.042240")
    chk("f R 00679B", prods[2], ".6f", "0.005400")
    chk("f'R", sum(prods), ".6f", "0.005740")
    chk("f'R in percent", sum(prods), ".3%", "0.574%")
    net, gross = sum(f), sum(abs(x) for x in f)
    chk("net exposure", net, ".5f", "0.29528")
    chk("gross exposure", gross, ".5f", "1.14712")
    chk("net exposure (3 dp)", net, ".3f", "0.295")
    chk("gross exposure (3 dp)", gross, ".3f", "1.147")
    chk("net NT$", sum(vals), ",.0f", "2,952,800")
    chk("gross NT$", sum(abs(v) for v in vals), ",.0f", "11,471,200")
    in_text("-0.42592+0.4224+0.2988=0.29528", "0.42592+0.4224+0.2988=1.14712")
    # Example 1 and the knowledge checks of Sections 1, 2 and 7: the second trader's book
    in_text("(-2,\\ 44{,}000,\\ 200{,}000)^{\\top}", "4{,}000\\,\\mathbf e_2", "(-2,\\ 48{,}000,\\ 200{,}000)^{\\top}")
    assert [H[i] + H_B[i] for i in range(3)] == [-2, 44_000, 200_000] and [H[i] - H_B[i] for i in range(3)] == [0, 4_000, 0]
    lines_b = [H_B[i] * (P[1][i] - P[0][i]) for i in range(3)]
    chk("variant 0050 line 7 Apr", lines_b[1], ",.0f", "-352,000")
    chk("variant P&L 7 Apr", sum(lines_b), ",.0f", "127,800")
    chk("variant: 0050 line saved", lines_b[1] - lines7[1], ",.0f", "70,400")
    wk_b = sum(H_B[i] * (P[5][i] - P[0][i]) for i in range(3))
    chk("variant week P&L", wk_b, ",.0f", "-78,400")
    in_text("350{,}600-229{,}000-200{,}000\\\\&=-78{,}400")
    # ================================================================================ Section 2 pitfall: limits
    assert P[0][1] * Decimal("0.9") == P[1][1]                      # 0050 closed exactly at -10% (TWSE's limit)
    lim = F[0] * Decimal("0.9")
    chk("TX limit 0.9 x 21,296", lim, ",.1f", "19,166.4")
    assert F[1] == lim.to_integral_value(rounding="ROUND_CEILING")  # settled at the first tick inside the limit
    in_text("0.9\\times21{,}296=19{,}166.4")
    assert F[4] == (F[3] * Decimal("1.1")).to_integral_value(rounding="ROUND_FLOOR")   # 10 April: at the +10% limit
    chk("TX volume 10 Apr (limit-up)", c["volume"][4], ",d", "2,382")
    # ================================================================================ the week: Y h, X, X w, X K
    Yh = []
    for kk in range(1, 6):
        Yh.append(sum(H[i] * (P[kk][i] - P[kk - 1][i]) for i in range(3)))
    for lab, v, pr in zip(CASE_DATES[1:], Yh, ("+57,400", "-33,000", "-95,200", "+87,800", "-141,200")):
        chk(f"Y h {lab}", v, "+,.0f", pr)
    in_text("57{,}400\\\\-33{,}000\\\\-95{,}200\\\\87{,}800\\\\-141{,}200", "\\mathbf 1^{\\top}Y\\mathbf h=-124{,}200")
    week = [P[5][i] - P[0][i] for i in range(3)]
    wl = [H[i] * week[i] for i in range(3)]
    chk("week TX line", wl[0], ",.0f", "350,600")
    chk("week 0050 line", wl[1], ",.0f", "-274,800")
    chk("week 00679B line", wl[2], ",.0f", "-200,000")
    chk("1'Y h", sum(Yh), ",.0f", "-124,200")
    assert sum(Yh) == sum(wl)                                     # telescoping
    chk("hedge pair week", wl[0] + wl[1], ",.0f", "75,800")
    chk("TX week move", -(F[5] - F[0]) / F[0], ".1%", "8.2%")
    chk("0050 week move", -(P[5][1] - P[0][1]) / P[0][1], ".1%", "6.5%")
    chk("TX week points", F[5] - F[0], ",.0f", "-1,753")
    in_text("350{,}600-274{,}800-200{,}000", "(19{,}543-21{,}296)", "(164.55-176.00)", "(27.88-29.88)")
    # drift (Section 6 pitfall, Problem 10)
    W7 = W0 + sum(lines7)
    f7 = [H[i] * P[1][i] / W7 for i in range(3)]
    R8 = X[1]
    true8 = Fraction(Yh[1]) / Fraction(W7)
    fR8 = sum(Fraction(f[i]) * R8[i] for i in range(3))
    chk("TX exposure 2 Apr (3 dp)", f[0], ".3f", "-0.426")
    chk("TX exposure 7 Apr", f7[0], ".3f", "-0.381")
    chk("0050 exposure 2 Apr (3 dp)", f[1], ".3f", "0.422")
    chk("0050 exposure 7 Apr", f7[1], ".3f", "0.378")
    chk("true 8 Apr return of the fixed book", true8, ".3%", "-0.328%")
    chk("f(2 Apr)'R(8 Apr)", fR8, ".3%", "-0.226%")
    P_(f"   precise: {float(true8):.6%} and {float(fR8):.6%} (anchors -0.328117%, -0.226276%)")
    # X w, X K (Example 8, the `xk` exhibit)
    K = {"100% 0050": (0, 1, 0), "60/40": (0, Fraction(6, 10), Fraction(4, 10)), "50/50": (0, Fraction(1, 2), Fraction(1, 2))}
    xk = {}
    for name, w in K.items():
        days = [sum(w[i] * X[kk][i] for i in range(3)) for kk in range(5)]
        comp = math.prod(1 + d for d in days) - 1
        xk[name] = (days, sum(days), comp)
        shown = [rnd(100 * d, 3) for d in days]
        assert rnd(100 * sum(days), 3) == sum(shown), (name, "printed parts do not add up")    # the sum row adds up
        comp_shown = math.prod(1 + s / 100 for s in shown) - 1
        P_(f"   {name}: daily {[f'{float(100 * d):+.4f}' for d in days]} sum {float(100 * sum(days)):+.4f} "
           f"compounded {float(100 * comp):+.4f} (from the printed entries {float(100 * comp_shown):+.4f})")
    rows_xk = []
    for kk, lab in enumerate(("7 Apr", "8 Apr", "9 Apr", "10 Apr", "11 Apr")):
        cells = []
        for name in K:
            v = 100 * xk[name][0][kk]
            cells.append(f"{float(v):+.3f}%" if not (lab == "7 Apr" and name == "100% 0050") else f"{float(v):.3f}%")
        rows_xk.append(f"| {lab} | " + " | ".join(cells) + " |")
    rows_xk.append("| Sum of daily returns | " + " | ".join(f"{float(100 * xk[n][1]):.3f}%" for n in K) + " |")
    rows_xk.append("| Compounded week | " + " | ".join(f"{float(100 * xk[n][2]):.3f}%" for n in K) + " |")
    in_text(*[r.replace("-", "−") for r in rows_xk])
    d6040 = xk["60/40"][0]
    chk("60/40 row 1 from printed inputs", 0.6 * -10.000 + 0.4 * 1.807, ".3f", "-5.277")
    chk("0050 7 Apr (3 dp)", 100 * X[0][1], ".3f", "-10.000")
    chk("00679B 7 Apr (3 dp)", 100 * X[0][2], ".3f", "1.807")
    in_text("-5.277\\\\-3.384\\\\-4.438\\\\7.145\\\\-0.026")
    assert [f"{float(100 * d):.3f}" for d in d6040] == ["-5.277", "-3.384", "-4.438", "7.145", "-0.026"]
    shown6040 = [rnd(100 * d, 3) for d in d6040]
    chk("60/40 sum (from printed)", sum(shown6040), ".2f", "-5.98%", suffix="%", in_text=False)
    chk("60/40 sum", 100 * xk["60/40"][1], ".2f", "-5.98%", suffix="%")
    chk("60/40 compounded (from printed)", 100 * (math.prod(1 + s / 100 for s in shown6040) - 1), ".2f", "-6.32%",
        suffix="%", in_text=False)
    chk("60/40 compounded", 100 * xk["60/40"][2], ".2f", "-6.32%", suffix="%")
    chk("100% 0050 compounded", 100 * xk["100% 0050"][2], ".3f", "-6.506%", suffix="%")
    order_sum = sorted(K, key=lambda n: -xk[n][1])
    order_comp = sorted(K, key=lambda n: -xk[n][2])
    assert order_sum[0] == "100% 0050" and order_comp[-1] == "100% 0050", (order_sum, order_comp)
    # week correlations (Example 6): by hand from the printed four-decimal percent returns
    x5 = [rnd(100 * X[kk][1], 4) for kk in range(5)]
    y5 = [rnd(100 * X[kk][2], 4) for kk in range(5)]
    for lab, a, b in zip(("7 Apr", "8 Apr", "9 Apr", "10 Apr", "11 Apr"), x5, y5):
        in_text(f"| {lab} | {float(a):.4f} | {float(b):.4f} |".replace("-", "−"))
    assert [f"{float(v):.4f}" for v in x5] == ["-10.0000", "-3.2513", "-4.6003", "9.9863", "2.3321"]
    assert [f"{float(v):.4f}" for v in y5] == ["1.8072", "-3.5832", "-4.1937", "2.8826", "-3.5628"]
    xb, yb = sum(x5) / 5, sum(y5) / 5
    chk("mean 0050 (5 dp)", xb, ".5f", "-1.10664")
    chk("mean 00679B (5 dp)", yb, ".5f", "-1.32998")
    xbp, ybp = rnd(xb, 5), rnd(yb, 5)                     # the printed means
    xc = [rnd(v - xbp, 4) for v in x5]
    yc = [rnd(v - ybp, 4) for v in y5]
    pr = [rnd(a * b, 4) for a, b in zip(xc, yc)]
    for lab, a, b, p in zip(("7 Apr", "8 Apr", "9 Apr", "10 Apr", "11 Apr"), xc, yc, pr):
        in_text(f"| {lab} | {float(a):.4f} | {float(b):.4f} | {float(p):.4f} |".replace("-", "−"))
    sxy, sxx, syy = sum(pr), sum(a * a for a in xc), sum(b * b for b in yc)
    in_text(f"| Sum | | | {float(sxy):.4f} |")
    chk("sum of products (printed parts)", sxy, ".4f", "25.9890")
    chk("|x~|^2", sxx, ".3f", "230.775")
    chk("|y~|^2", syy, ".3f", "45.851")
    rho_hand = 25.989 / math.sqrt(230.775 * 45.851)
    chk("rho by hand", rho_hand, ".3f", "0.253")
    chk("angle by hand", angle(rho_hand), ".1f", "75.4°", suffix="°")
    sxy_u, sxx_u, syy_u = (sum(a * b for a, b in zip(x5, y5)), sum(a * a for a in x5), sum(b * b for b in y5))
    chk("x'y uncentred", sxy_u, ".3f", "33.348")
    chk("|x|^2", sxx_u, ".3f", "236.899")
    chk("|y|^2", syy_u, ".3f", "54.695")
    chk("uncentred cosine by hand", 33.348 / math.sqrt(236.899 * 54.695), ".3f", "0.293")
    Xf = np.array([[float(v) for v in row] for row in X])
    wk_rho = corr(Xf[:, 1], Xf[:, 2])
    chk("week rho 0050/00679B (exact inputs)", wk_rho, ".4f", "0.2526")
    chk("week rho (3 dp)", wk_rho, ".3f", "0.253")
    chk("week uncentred (3 dp)", cos_uncentred(Xf[:, 1], Xf[:, 2]), ".3f", "0.293")
    chk("week angle 0050/00679B", angle(wk_rho), ".0f", "75°", suffix="°")
    P_(f"   week, five returns: TX/0050 {corr(Xf[:, 0], Xf[:, 1]):.4f} ({angle(corr(Xf[:, 0], Xf[:, 1])):.2f} deg); "
       f"0050/00679B {wk_rho:.4f} ({angle(wk_rho):.2f} deg), uncentred {cos_uncentred(Xf[:, 1], Xf[:, 2]):.4f}; "
       f"TX/00679B {corr(Xf[:, 0], Xf[:, 2]):.4f} ({angle(corr(Xf[:, 0], Xf[:, 2])):.2f} deg)")
    # ================================================================================ Sections 3 and 4: small vectors
    chk("|(0.6, 0.4)|", math.hypot(0.6, 0.4), ".4f", "0.7211")
    chk("distance 60/40 - 50/50", math.hypot(0.1, 0.1), ".4f", "0.1414")
    fe = np.array([float(f[0]), float(f[1])])
    chk("balls: Euclidean norm", np.linalg.norm(fe), ".3f", "0.600")
    chk("balls: 1-norm", np.abs(fe).sum(), ".3f", "0.848")
    chk("balls: net", fe.sum(), ".3f", "-0.004")
    chk("balls: f_TX", fe[0], ".3f", "-0.426")
    chk("balls: f_0050", fe[1], ".3f", "0.422")
    chk("KC 3: norm of (0.5, -0.5)", math.hypot(0.5, 0.5), ".4f", "0.7071")
    # cs-proof
    xv, yv = np.array([1.5, 2.5]), np.array([3.0, 1.0])
    a_star = Fraction(7, 10)
    assert Fraction(xv @ yv).limit_denominator(100) == 7 and Fraction(yv @ yv).limit_denominator(100) == 10
    res = [Fraction(3, 2) - a_star * 3, Fraction(5, 2) - a_star * 1]
    assert res == [Fraction(-3, 5), Fraction(9, 5)] and res[0] * 3 + res[1] * 1 == 0
    chk("cs-proof angle", angle(float(xv @ yv / np.linalg.norm(xv) / np.linalg.norm(yv))), ".2f", "40.60°", suffix="°")
    # Example 5
    x5a, y5a = np.array([0.6, 0.4]), np.array([0.5, 0.5])
    chk("Ex5 |x|", np.linalg.norm(x5a), ".5f", "0.72111")
    chk("Ex5 |y|", np.linalg.norm(y5a), ".5f", "0.70711")
    chk("Ex5 product of printed norms", 0.72111 * 0.70711, ".5f", "0.50990")
    chk("Ex5 cos from printed", 0.50 / 0.50990, ".5f", "0.98058")
    chk("Ex5 cos exact", float(x5a @ y5a) / np.linalg.norm(x5a) / np.linalg.norm(y5a), ".5f", "0.98058", in_text=False)
    chk("Ex5 angle", angle(0.98058), ".2f", "11.31°", suffix="°")
    chk("Ex5b net of equity lines", fe.sum(), ".5f", "-0.00352")
    chk("Ex5b |f_eq|", np.linalg.norm(fe), ".5f", "0.59986")
    chk("Ex5b sqrt 2", math.sqrt(2), ".5f", "1.41421")
    chk("Ex5b product of printed lengths", 0.59986 * 1.41421, ".5f", "0.84833")
    chk("Ex5b cos from printed", -0.00352 / 0.84833, ".5f", "-0.00415")
    chk("Ex5b angle", angle(-0.00352 / 0.84833), ".2f", "90.24°", suffix="°")
    chk("Ex5b angle exact", angle(float(fe.sum() / np.linalg.norm(fe) / math.sqrt(2))), ".2f", "90.24°", suffix="°")
    # ================================================================================ Section 5: correlation as a cosine
    v = lm7_vols()
    chk("LM7 T", v["T"], ",d", "2,363")
    chk("LM7 A", v["A"], ".4f", "243.0543")
    chk("0050 vol (2 dp)", v["s1"], ".2%", "20.11%")
    chk("00679B vol (2 dp)", v["s2"], ".2%", "13.50%")
    chk("0050 vol (3 dp)", v["s1"], ".3%", "20.106%")
    chk("00679B vol (3 dp)", v["s2"], ".3%", "13.496%")
    chk("LM7 rho (4 dp)", v["rho"], ".4f", "-0.1056")
    chk("LM7 angle (2 dp)", angle(v["rho"]), ".2f", "96.06°", suffix="°")
    chk("LM7 angle (1 dp)", angle(v["rho"]), ".1f", "96.1°", suffix="°")
    mix = 0.423 * v["a"] + 0.577 * v["b"]
    sp = float(mix.std() * math.sqrt(v["A"]))
    chk("mix vol w = 0.423 (2 dp)", sp, ".2%", "10.91%")
    chk("mix vol w = 0.423 (3 dp)", sp, ".3%", "10.908%")
    bound = 0.423 * v["s1"] + 0.577 * v["s2"]
    chk("bound (2 dp)", bound, ".2%", "16.29%")
    chk("bound from printed inputs", 0.423 * 20.106 + 0.577 * 13.496, ".3f", "16.292%", suffix="%")
    var_p = 0.423**2 * 20.106**2 + 0.577**2 * 13.496**2 + 2 * 0.423 * 0.577 * -0.1056 * 20.106 * 13.496
    chk("mix variance from printed inputs (%^2)", var_p, ".2f", "118.99")
    chk("mix vol from printed variance", math.sqrt(118.99), ".3f", "10.908%", suffix="%")
    in_text("w^2(20.106)^2+(1-w)^2(13.496)^2", "2w(1-w)(-0.1056)\\\\&\\quad\\times(20.106)(13.496)=118.99",
            "With $w=0.423$")
    # the plane picture: the mix vector's length in the plane equals the mix's volatility
    th = math.radians(angle(v["rho"]))
    m2 = (0.423 * v["s1"] + 0.577 * v["s2"] * math.cos(th), 0.577 * v["s2"] * math.sin(th))
    assert abs(math.hypot(*m2) - sp) < 1e-12
    # (8.10) and U28
    names, XS, d28 = u28()
    T28 = XS.shape[0]
    chk("U28 T", T28, ",d", "4,382")
    assert d28[0] == U28_FIRST and d28[1] == "2008-12-02" and d28[-1] == LAST
    ix = {n: i for i, n in enumerate(names)}
    C = np.corrcoef(XS, rowvar=False)
    iu = np.triu_indices(28, 1)
    cv = C[iu]
    chk("U28 pairs", len(cv), "d", "378")
    kmax, kmin = int(np.argmax(cv)), int(np.argmin(cv))
    assert {names[iu[0][kmax]], names[iu[1][kmax]]} == {"ElectronicPartsComponents", "ComputerPeripheralEquipment"}
    assert {names[iu[0][kmin]], names[iu[1][kmin]]} == {"BiotechnologyMedicalCare", "OilGasElectricity"}
    chk("U28 max rho (4 dp)", cv[kmax], ".4f", "0.7547")
    chk("U28 min rho (4 dp)", cv[kmin], ".4f", "0.2175")
    chk("U28 max angle", angle(cv[kmax]), ".1f", "41.0°", suffix="°")
    chk("U28 min angle", angle(cv[kmin]), ".1f", "77.4°", suffix="°")
    P_(f"   U28 median correlation {np.median(cv):.4f}, mean {cv.mean():.5f}")
    sf = XS[:, [ix["Semiconductor"], ix["FinancialInsurance"]]]
    rho_sf = corr(sf[:, 0], sf[:, 1])
    chk("Semi/Fin rho", rho_sf, ".4f", "0.5749")
    chk("Semi/Fin uncentred cosine", cos_uncentred(sf[:, 0], sf[:, 1]), ".4f", "0.5758")
    zx = (sf[:, 0] - sf[:, 0].mean()) / sf[:, 0].std()
    zy = (sf[:, 1] - sf[:, 1].mean()) / sf[:, 1].std()
    d2 = float(np.sum((zx - zy) ** 2))
    assert abs(d2 - 2 * T28 * (1 - rho_sf)) < 1e-8 and abs(np.sum(zx**2) - T28) < 1e-8      # (8.10) on real data
    P_(f"   (8.10) Semi/Fin: squared distance {d2:.2f} = 2T(1-rho) {2 * T28 * (1 - rho_sf):.2f} (lab anchor 3,725.94)")
    s3 = XS[:, [ix[n] for n in ("Semiconductor", "FinancialInsurance", "Food")]]
    s_ew, s_avg = float(s3.mean(axis=1).std()), float(s3.std(axis=0).mean())
    assert s_ew <= s_avg                                                                         # (8.11) on real data
    P_(f"   (8.11) S3 equal weights: s_p {s_ew:.4%} a day <= sum w_i s_i {s_avg:.4%} (lab anchors 1.0527%, 1.2721%)")
    # the `angles` exhibit
    ap = angles_pairs()
    for p_, (r_pr, d_pr) in zip(ap, (("0.974", "13.0"), ("0.755", "41.0"), ("0.575", "54.9"), ("0.403", "66.2"),
                                     ("0.217", "77.4"), ("-0.106", "96.1"))):
        chk(f"angles {p_['label']} rho", p_["rho"], ".3f", r_pr)
        chk(f"angles {p_['label']} angle", p_["deg"], ".1f", d_pr + "°", suffix="°")
        assert abs(angle(float(r_pr)) - p_["deg"]) < 0.1                          # the printed rho gives the printed angle
    a1, b1, dd1 = lm1_pair()
    chk("LM1 T", len(a1), ",d", "2,902")
    assert dd1[0] == "2014-11-03" and dd1[-1] == LAST
    _, _, dd7 = lm7_pair()
    assert dd7[0] == "2017-01-18" and dd7[-1] == LAST
    rho_lm1 = corr(a1, b1)
    P_(f"   0050/00631L rho {rho_lm1:.6f}, angle {angle(rho_lm1):.3f}, sqrt(2(1-rho)) {math.sqrt(2 * (1 - rho_lm1)):.4f}")
    # sector closes repaired in the U28 sample (one raw/sectors_close/ file per repaired close)
    reps = [p.stem.split("__") for p in (RAW / "sectors_close").glob("*.csv")]
    rep28 = [(s, d) for s, d in reps if s in ix and U28_FIRST <= d <= LAST]
    chk("repaired U28 closes in the sample", len(rep28), "d", "524")
    P_(f"   on {len({d for _, d in rep28})} dates (anchor 38); all repaired closes: {len(reps)}")
    # price returns of 0050 and 00679B on their own common dates, split day excluded (the brief's price-vs-total check)
    cal = taiex_calendar()
    p50, p679 = c["p50"], c["p679"]

    def price_returns(rows: dict[str, list[str]], skip: str | None = None) -> dict[str, float]:
        return {cal[i]: float(rows[cal[i]][1]) / float(rows[cal[i - 1]][1]) - 1 for i in range(1, len(cal))
                if cal[i] in rows and cal[i - 1] in rows and cal[i] != skip}

    r50, r679 = price_returns(p50, "2025-06-18"), price_returns(p679)
    common = sorted(set(r50) & set(r679))
    P_(f"   0050/00679B price returns, own common dates, split day excluded: T = {len(common)} (anchor 2,362), "
       f"rho = {corr(np.array([r50[d] for d in common]), np.array([r679[d] for d in common])):.6f} (anchor -0.104998)")
    # Section 1 pitfall: the dates the two funds share, and 0050's halt
    both = sorted(set(p50) & set(p679))
    chk("common dates of 0050 and 00679B", len(both), ",d", "2,364")
    assert both[0] == LM7_BASE and len(both) - 1 == v["T"]
    halt = sorted(set(p679) - set(p50))
    assert halt == ["2025-06-11", "2025-06-12", "2025-06-13", "2025-06-16", "2025-06-17"], halt
    # ================================================================================ practice problems
    p2 = [H_P2[i] * (P[2][i] - P[1][i]) for i in range(3)]
    chk("P2 TX line", p2[0], ",.0f", "-399,200")
    chk("P2 00679B line", p2[2], ",.0f", "-218,000")
    chk("P2 total", -sum(p2), ",.0f", "617,200")
    chk("P2 inputs: TX 8 Apr", F[2], ",.0f", "18,169")
    chk("P2 inputs: 00679B 8 Apr", P[2][2], ".2f", "29.33")
    v3 = [H_P2[i] * P[0][i] for i in range(3)]
    chk("P3 value TX", v3[0], ",.0f", "8,518,400")
    chk("P3 value 00679B", v3[2], ",.0f", "5,976,000")
    f3 = [x / W0 for x in v3]
    chk("P3 f TX", f3[0], ".5f", "0.85184")
    chk("P3 f 00679B", f3[2], ".4f", "0.5976")
    chk("P3 net = gross", sum(f3), ".5f", "1.44944")
    pr3 = [Fraction(f3[i]) * X[0][i] for i in range(3)]
    chk("P3 f R TX", pr3[0], ".6f", "-0.085160")
    chk("P3 f R 00679B", pr3[2], ".6f", "0.010800")
    chk("P3 f'R", sum(pr3), ".6f", "-0.074360")
    chk("P3 W0 f'R", sum(pr3) * Fraction(W0), ",.0f", "-743,600")
    assert sum(pr3) * Fraction(W0) == sum(H_P2[i] * (P[1][i] - P[0][i]) for i in range(3))
    wa, wb = np.array([0.5, 0.3, 0.2]), np.array([0.4, 0.3, 0.3])
    chk("P4 |wa|", np.linalg.norm(wa), ".4f", "0.6164")
    chk("P4 |wb|", np.linalg.norm(wb), ".4f", "0.5831")
    chk("P4 distance", np.linalg.norm(wb - wa), ".4f", "0.1414")
    chk("P4 relative distance from printed", 0.1414 / 0.6164, ".4f", "0.2294")
    chk("P4 1-norm", np.abs(wb - wa).sum(), ".1f", "0.2")
    chk("P6 angle", angle(8 / 9), ".2f", "27.27°", suffix="°")
    x7, y7 = np.array([2, 4, 0, 2.0]), np.array([1, 3, 1, 3.0])
    chk("P7 rho", corr(x7, y7), ".4f", "0.7071")
    assert abs(np.cov(x7, y7, ddof=0)[0, 1] - 1) < 1e-12 and abs(np.cov(x7, y7, ddof=1)[0, 1] - 4 / 3) < 1e-12
    chk("P8 arccos(-0.106)", angle(-0.106), ".1f", "96.1°", suffix="°")
    chk("P8 distractor arccos(0.106)", angle(0.106), ".1f", "83.9°", suffix="°")
    chk("P9 max angle", angle(0.7547), ".2f", "41.00°", suffix="°")
    chk("P9 max sqrt(2(1-rho))", math.sqrt(2 * (1 - 0.7547)), ".4f", "0.7004")
    chk("P9 min angle", angle(0.2175), ".2f", "77.44°", suffix="°")
    chk("P9 min sqrt(2(1-rho))", math.sqrt(2 * (1 - 0.2175)), ".4f", "1.2510")
    # ================================================================================ the Python box of Section 7
    m = re.search(r"\[!python\] Shapes and products in NumPy\n(.*?)\n(?!>)", TEXT, re.DOTALL)
    assert m is not None
    block = re.search(r"```python\n(.*?)```", re.sub(r"(?m)^> ?", "", m.group(1)), re.DOTALL)
    assert block is not None
    out = io.StringIO()
    with tempfile.TemporaryDirectory() as tmp:                   # run the module's own code, as printed
        script = Path(tmp) / "python_box.py"
        script.write_text(block.group(1), encoding="utf-8")
        with contextlib.redirect_stdout(out):
            runpy.run_path(str(script))
    got = out.getvalue().splitlines()
    want = ["(5, 3) (3, 3) (5, 3)", "(3,) (3,)", "True", "[  57400.  -33000.  -95200.   87800. -141200.] -124200.0"]
    P_(f"{'ok  ' if got == want else 'FAIL'} Python box prints {got}")
    if got != want:
        FAILS.append("python box")
    for line in want:
        in_text(line if line.startswith("[") else line.split(" (")[0])
    # ================================================================================ the widget's embedded data
    js = (ROOT / "src" / "lm08.js").read_text(encoding="utf-8")
    mdp, mp0 = re.search(r"var DP = (\[.*?\]);", js, re.DOTALL), re.search(r"var P0 = (\[.*?\]);", js)
    assert mdp is not None and mp0 is not None, "src/lm08.js: DP and P0 not found"
    dp_js, p0_js = json.loads(mdp.group(1)), json.loads(mp0.group(1))
    dp = [[float(P[kk][i] - P[kk - 1][i]) for i in range(3)] for kk in range(1, 6)]
    ok_js = dp_js == dp and p0_js == [float(x) for x in P[0]]
    P_(f"{'ok  ' if ok_js else 'FAIL'} src/lm08.js embeds the 15 price changes and the prices of 2 April")
    if not ok_js:
        FAILS.append("lm08.js data")
    # ================================================================================ result
    print(f"\n{len(FAILS)} failed check(s)" + (": " + ", ".join(FAILS) if FAILS else ""))
    assert not FAILS, FAILS


if __name__ == "__main__":
    main()
