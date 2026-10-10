"""Print LM7's data exhibits as Markdown table rows, rounded exactly as displayed in src/lm07.md.

Run after lm07_stats.py:  python3 data/lm07_tables.py
Each table also checks that printed parts add up to printed totals where the text implies a sum.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
st = json.loads((HERE / "processed" / "lm07_stats.json").read_text(encoding="utf-8"))
F, IS, OOS = st["full"], st["is"], st["oos"]
m = lambda v: f"{v:.{0}f}"


def pct(v, d=1, sign=False):
    s = f"{abs(v) * 100:,.{d}f}%"
    return ("+" if v > 0 and sign else "−" if v < 0 else "") + s


def num(v, d=2, sign=False):
    s = f"{abs(v):,.{d}f}"
    return ("+" if v > 0 and sign else "−" if v < 0 and round(abs(v), d) > 0 else "") + s


print("### Exhibit: case (periods)")
oo = st["oos_table"]
rows = [
    ("Trading days (daily returns)", f"{F['n']:,}", f"{IS['n']:,}", f"{OOS['n']:,}"),
    ("0050 total return", pct(F["g1"], 1, True), pct(IS["g1"], 1, True), pct(OOS["g1"], 1, True)),
    ("00679B total return", pct(F["g2"], 1, True), pct(IS["g2"], 1, True), pct(OOS["g2"], 1, True)),
    ("0050 annualized volatility", pct(F["s1"]), pct(IS["s1"]), pct(OOS["s1"])),
    ("00679B annualized volatility", pct(F["s2"]), pct(IS["s2"]), pct(OOS["s2"])),
    ("Correlation of daily returns", num(F["rho"]), num(IS["rho"]), num(OOS["rho"])),
    ("Minimum-variance weight in 0050, estimated in the window", pct(F["w_mv"]), pct(IS["w_mv"]), pct(OOS["w_mv"])),
    ("Lowest attainable volatility in the window", pct(F["s_mv"], 2), pct(IS["s_mv"], 2), pct(OOS["s_mv"], 2)),
    (f"Volatility of the {IS['w_mv']:.1%} / {1-IS['w_mv']:.1%} mix", pct(st["case"]["vol_full"], 2), pct(oo["IS min-var"]["vol_is"], 2), pct(oo["IS min-var"]["vol_oos"], 2)),
]
for r in rows:
    print("> | " + " | ".join(r) + " |")
print(f"check days: {IS['n']}+{OOS['n']}={IS['n']+OOS['n']} vs {F['n']}")

print("\n### Exhibit: attribution (%^2)")
at, ap = st["attrib"], st["attrib_partials"]
d = at["d"]
f = at["first"]
r1 = [("σ₁: " + pct(IS["s1"], 2) + " → " + pct(OOS["s1"], 2), f"{ap['dV_ds1']:.4f}", num(f["s1"] * 1e4, 2, True)),
      ("σ₂: " + pct(IS["s2"], 2) + " → " + pct(OOS["s2"], 2), f"{ap['dV_ds2']:.4f}", num(f["s2"] * 1e4, 2, True)),
      ("ρ: " + num(IS["rho"], 3) + " → " + num(OOS["rho"], 3), f"{ap['dV_drho']:.4f}", num(f["rho"] * 1e4, 2, True))]
for r in r1:
    print("> | " + " | ".join(r) + " |")
tot1 = round(f["s1"] * 1e4, 2) + round(f["s2"] * 1e4, 2) + round(f["rho"] * 1e4, 2)
print(f"first-order total printed {at['first_total']*1e4:.2f}; sum of printed parts {tot1:.2f}")
print(f"second-order approx {(at['first_total']+at['second_total'])*1e4:.2f}; exact {at['dV']*1e4:.2f}; V0 {at['V0']*1e4:.1f} V1 {at['V1']*1e4:.1f} "
      f"diff of printed {round(at['V1']*1e4,1)-round(at['V0']*1e4,1):.1f}; s1s1 {at['second']['s1s1']*1e4:.2f} s1rho {at['second']['s1rho']*1e4:.2f} third {at['third']*1e4:.2f}")
print(f"shares: s1 {f['s1']/at['dV']:.0%}, rho {f['rho']/at['dV']:.0%}, first {at['first_total']/at['dV']:.0%}, second {at['second_total']/at['dV']:.0%}")
print(f"d2V/ds1^2={ap['d2V_ds1']:.4f} d2V/ds1drho={ap['d2V_ds1drho']:.4f}; dsigma1={d['s1']*100:.2f}pp drho={d['rho']:.3f}")

print("\n### Exhibit: Taylor accuracy of the growth model")
for t in st["taylor"]:
    ge, gq = round(t["exact"] * 100, 4), round(t["quad"] * 100, 4)
    err = t["err"] * 1e4
    print(f"> | {t['name']} | {num(t['f1'],2)} | {num(t['f2'],2)} | {num(t['exact']*100,4)}% | {num(t['quad']*100,4)}% | {num(err,1,True)} bp |"
          f"   [printed diff {(gq-ge)*100:+.1f} bp; raw err {err:+.3f}; err2 {t['err2']*1e4:+.1f}]")

print("\n### Exhibit: years")
for y in st["years"]:
    print(f"> | {y['year']}{'*' if y['year']==2026 else ''} | {y['n']} | {pct(y['r1'],1,True)} | {pct(y['r2'],1,True)} | {pct(y['s1'])} | {pct(y['s2'])} | {num(y['rho'],2,True)} | {pct(y['w_mv'])} |")
fr = st["freq"]
print(f"weekly corr IS {fr['1w']['IS']:.2f} OOS {fr['1w']['OOS']:+.2f}; monthly IS {fr['1mo']['IS']:.2f} OOS {fr['1mo']['OOS']:+.2f}; lags {fr['lag']}")

print("\n### Exhibit: Kelly by window (r_f = 1.5%)")
for lab, e in (("2017–2021", IS), ("2022–2026", OOS), ("2017–2026", F)):
    print(f"> | {lab} | {pct(e['e1'],1)} | {pct(e['e2'],1,True)} | {pct(e['s1'])} | {pct(e['s2'])} | {num(e['rho'],2)} | {num(e['f1'],2)} | {num(e['f2'],2,True)} | {num(e['lev'],2)} | {pct(e['wT1'],1)} / {pct(e['wT2'],1,True)} | {num(e['sr_star'],2)} |"
          f"   [check f1+f2: {round(e['f1'],2)+round(e['f2'],2):.2f}; wT sum {round(e['wT1']*100,1)+round(e['wT2']*100,1):.1f}; SR1 {e['sr1']:.2f} SR2 {e['sr2']:.2f}]")

print("\n### Exhibit: KKT candidates (full sample, cap 2)")
for c in st["kkt_cap"]["full_cap2"]:
    print(f"> | {c['case']} | ({num(c['f1'],2)}, {num(c['f2'],2,True)}) | {c['mult']} | {c['ok']} | {pct(c['g'],2)} |")

print("\n### Exhibit: numerical optimization")
no = st["numopt"]
for r in no["newton"][:5]:
    print(f"Newton k={r['k']} f=({r['f1']:.4f}, {r['f2']:.4f}) gap={r['gap']:.1e}")
for r in no["ga"]:
    print(f"GA k={r['k']} f=({r['f1']:.4f}, {r['f2']:.4f}) gap={r['gap']:.1e}")
print(f"eig {no['eig'][0]:.4f} {no['eig'][1]:.4f} kappa {no['kappa']:.2f} alpha {no['alpha']:.1f} rate {no['rate']:.2f}; GA k(1e-6)={no['ga_k_1e6']} k(1e-10)={no['ga_k_1e10']}; Newton {no['nt_k_1e6']} {no['nt_k_1e10']}")
