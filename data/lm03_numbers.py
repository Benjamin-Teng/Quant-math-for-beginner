import numpy as np, polars as pl, json, math
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))  # paths below are relative to data/
from math import log, exp, log1p, expm1, sqrt
P = lambda *a: print(*a)
# ---- Example 1: ln(1.05), e^0.05
x=0.05
ln_ex=log1p(x); T=[x, x-x**2/2, x-x**2/2+x**3/3]
P("Ex1 ln1.05", f"{ln_ex:.7f}", [f"{t:.7f}" for t in T], [f"{ln_ex-t:+.7f}" for t in T])
e_ex=exp(x); E=[1+x, 1+x+x**2/2, 1+x+x**2/2+x**3/6]
P("Ex1 e^.05", f"{e_ex:.7f}", [f"{t:.7f}" for t in E], [f"{e_ex-t:+.7f}" for t in E])
# ---- Example 2: real rate
i,pi=0.01725,0.018
P("Ex2 real exact", f"{(1+i)/(1+pi)-1:.6%}", "approx", f"{i-pi:.6%}", "2nd", f"{(i-pi)-pi*(i-pi):.6%}")
# ---- remainder table
P("Remainder table x, ln, T2, err, bound")
for x in [-0.20,-0.10,-0.05,-0.01,0.01,0.05,0.10,0.20,0.50]:
    ex=log1p(x); t2=x-x*x/2; err=ex-t2
    bound = x**3/3 if x>=0 else abs(x)**3/(3*(1+x)**3)
    P(f"{x:+.2f} {ex:+.6f} {t2:+.6f} {err:+.6f} {bound:.6f} ratio={abs(err)/bound:.3f}")
# ---- big days
for d,x in [("2024-08-05",-0.0913),("2025-04-07",-0.1)]:
    pass
df = pl.read_parquet("processed/etf_daily_returns.parquet")
for d in ["2024-08-05","2025-04-07","2025-04-10"]:
    x = df.filter(pl.col("date")==d)["R_0050"][0]
    ex=log1p(x); t1=x; t2=x-x*x/2; t3=t2+x**3/3
    b2 = abs(x)**3/(3*(1+x)**3) if x<0 else x**3/3
    P("BIG", d, f"R={x:.6f} ln={ex:.6f} T1err={(t1-ex)*1e4:.2f}bp T2err={(t2-ex)*1e4:.2f}bp T3err={(t3-ex)*1e4:.3f}bp bound2={b2*1e4:.2f}bp")
# ---- rule of 72
for R in [0.02,0.04,0.06,0.08,0.10,0.12,0.20]:
    exact=log(2)/log1p(R); a1=log(2)/R; a2=log(2)/R+log(2)/2; r72=72/(100*R)
    P(f"R={R:.2f} exact={exact:.3f} ln2/R={a1:.3f} +0.347={a2:.3f} 72rule={r72:.3f}")
# ---- R vs r table
P("R vs r")
for R in [-0.5,-0.2,-0.1,-0.01,0.01,0.1,0.2,0.5,1.0]:
    r=log1p(R); P(f"{R:+.0%} r={r:+.4%} gap={R-r:.4%} R^2/2={R*R/2:.4%}")
# ---- Example 5 (+2%/-1%)
a,b=0.02,-0.01; mu=(a+b)/2; s2=((a-mu)**2+(b-mu)**2)/2
geo=sqrt((1+a)*(1+b))-1; g=(log1p(a)+log1p(b))/2
P("Ex5", f"mu={mu:.5%} s2={s2:.8f} geo={geo:.5%} g={g:.5%} mu-s2/2={mu-s2/2:.5%} mu-(s2+mu2)/2={mu-(s2+mu*mu)/2:.5%}")
# ---- +100/-50 and +60/-40
for a,b in [(1.0,-0.5),(0.6,-0.4)]:
    mu=(a+b)/2; s2=((a-mu)**2+(b-mu)**2)/2; geo=sqrt((1+a)*(1+b))-1
    P("pitfall", a,b, f"mu={mu:.2%} s={sqrt(s2):.2%} geo={geo:.3%} approx={mu-s2/2:.3%}")
# ---- Example 4: 0050 calendar returns 2020-2024 & 2015-2025
st=json.load(open("processed/lm03_stats.json"))
yrs={y["label"]:y for y in st["years"]}
def cal(years):
    Rs=np.array([yrs[str(y)]["ret0050"] for y in years])
    mu=Rs.mean(); s2=Rs.var(); geo=np.prod(1+Rs)**(1/len(Rs))-1; g=np.log1p(Rs).mean()
    return Rs, mu, s2, geo, g
for years in [range(2020,2025), range(2015,2026)]:
    Rs,mu,s2,geo,g=cal(years)
    P("CAL", list(years)[0], list(years)[-1], [f"{r:.2%}" for r in Rs], f"mu={mu:.3%} s={sqrt(s2):.3%} geo={geo:.3%} approx={mu-s2/2:.3%} g={g:.3%} gapprox={mu-(s2+mu*mu)/2:.3%} s2samp={Rs.var(ddof=1):.5f}")
# ---- frequency table (R_G vs approx, g vs approx)
P("FREQ")
for f in st["freq"]:
    mu=f["mu"]; s2=f["sd"]**2; g=f["g_log"]; geo=f["geo"]
    P(f"{f['freq']:>4} n={f['n']:5d} mu={mu:.4%} sd={f['sd']:.4%} geo={geo:.4%} mu-s2/2={mu-s2/2:.4%} err={(mu-s2/2-geo)*1e4:+.2f}bp | g={g:.4%} mu-(s2+mu2)/2={mu-(s2+mu*mu)/2:.4%} err={(mu-(s2+mu*mu)/2-g)*1e4:+.2f}bp")
# ---- Practice 3
x=-0.08; ex=log1p(x); t2=x-x*x/2; P("PP3", f"ln0.92={ex:.7f} T2={t2:.7f} err={ex-t2:.7f} bound={abs(x)**3/(3*(1+x)**3):.7f}")
# ---- PP4
Rs=np.array([0.30,-0.20,0.10]); mu=Rs.mean(); s2=Rs.var(); geo=np.prod(1+Rs)**(1/3)-1
P("PP4", f"mu={mu:.4%} s2={s2:.5f} geo={geo:.4%} approx={mu-s2/2:.4%}")
# ---- PP7
P("PP7", 1.2*0.8-1, 1.1*0.9-1, (1.1*0.9)**2, (1.1*0.9)**2*exp(-(0.1**2+0.1**2)))
# ---- PP8
G=1.2; RV=0.09; P("PP8", G**3*exp(-3*RV)-1, 3*0.2, G**3-1)
# ---- PP10
P("PP10", -7.5*0.015+0.5*70*0.015**2)
# ---- PP12
R=0.06; P("PP12", log(2)/log1p(R), log(2)/R+log(2)/2, 72/6)
# ---- PP14
i,pi=0.03,0.025; P("PP14", (1+i)/(1+pi)-1, i-pi, (i-pi)-pi*(i-pi))
# ---- bond example 7: 10y annual coupon 2% priced at 2%
def price(y, c=0.02, n=10, F=100):
    return sum(c*F/(1+y)**t for t in range(1,n+1)) + F/(1+y)**n
y0=0.02; P0=price(y0); h=1e-5
dP=(price(y0+h)-price(y0-h))/(2*h); d2P=(price(y0+h)-2*P0+price(y0-h))/h**2
Dmod=-dP/P0; C=d2P/P0
P("BOND", f"P0={P0:.4f} Dmod={Dmod:.4f} C={C:.4f}")
for dy in [0.01,-0.01,0.03]:
    ex=price(y0+dy)/P0-1; a1=-Dmod*dy; a2=a1+0.5*C*dy*dy
    P(f"  dy={dy:+.2%} exact={ex:.4%} dur={a1:.4%} dur+conv={a2:.4%}")
# Macaulay duration check
mac=sum(t*(0.02*100)/(1.02)**t for t in range(1,11))/P0 + 10*100/1.02**10/P0
P("Macaulay", mac, "Dmod=mac/1.02", mac/1.02)
