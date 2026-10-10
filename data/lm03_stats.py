import polars as pl, numpy as np, json
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))  # paths below are relative to data/
df = pl.read_parquet("processed/etf_daily_returns.parquet").with_columns(pl.col("date").str.to_date())
R = df["R_0050"].to_numpy(); RL = df["R_00631L"].to_numpy()
dates = df["date"].to_list()
res = {}
def block(R, RL, label):
    n = len(R); G0 = np.prod(1+R); G2 = np.prod(1+RL)
    L0 = np.log1p(R).sum(); L2 = np.log1p(RL).sum(); D = L2 - 2*L0
    E = (np.log1p(2*R) - 2*np.log1p(R)).sum()
    S2, S3, S4 = (R**2).sum(), (R**3).sum(), (R**4).sum()
    return dict(label=label, n=n, ret0050=G0-1, ret00631L=G2-1, twice0050=2*(G0-1), log0050=L0, log00631L=L2,
                gap_log=D, exact_rebal=E, T2=-S2, T3=-S2+2*S3, T4=-S2+2*S3-3.5*S4, residual=D-E, RV=S2)
d0, d1 = dates[0], dates[-1]
yrs = (d1 - d0).days/365.25
full = block(R, RL, "full"); full["years"] = yrs
full["cagr0050"] = (1+full["ret0050"])**(1/yrs)-1; full["cagr00631L"] = (1+full["ret00631L"])**(1/yrs)-1
full["residual_per_year"] = full["residual"]/yrs; full["T2_per_year"] = full["T2"]/yrs
full["ann_vol_0050"] = np.sqrt(R.var()*len(R)/yrs); full["ann_vol_00631L"] = np.sqrt(RL.var()*len(RL)/yrs)
res["full"] = full
# per year
yr = np.array([d.year for d in dates]); rows = []
for y in sorted(set(yr)):
    m = yr == y
    b = block(R[m], RL[m], str(y)); rows.append(b)
res["years"] = rows
# simple vs log daily
r = np.log1p(R)
res["daily"] = dict(meanR=R.mean(), meanr=r.mean(), diff=R.mean()-r.mean(), half_var=R.var()/2, half_m2=(R**2).mean()/2,
                    sd=R.std(), skew=float(((R-R.mean())**3).mean()/R.std()**3), exkurt=float(((R-R.mean())**4).mean()/R.std()**4-3))
# frequency study on 0050 TR wealth index
w = np.cumprod(1+R); wdf = pl.DataFrame({"date": dates, "w": w})
def agg(every):
    if every == "1d": ww = w
    else:
        ww = wdf.group_by_dynamic("date", every=every).agg(pl.col("w").last())["w"].to_numpy()
    ww = np.concatenate([[1.0], ww]); Rk = ww[1:]/ww[:-1]-1
    if every == "1y": Rk = Rk[1:-1]  # drop partial 2014 & 2026
    mu = Rk.mean(); var = Rk.var(); g = np.log1p(Rk).mean()
    return dict(freq=every, n=len(Rk), mu=mu, sd=np.sqrt(var), g_log=g, approx1=mu-var/2, approx2=mu-(var+mu**2)/2,
                err1=(mu-var/2)-g, err2=(mu-(var+mu**2)/2)-g, geo=np.expm1(g))
res["freq"] = [agg(e) for e in ["1d","1w","1mo","1q","1y"]]
# big days
big = []
for dd in ["2015-08-24","2018-10-11","2020-03-19","2024-08-05","2025-04-07","2025-04-09","2025-04-10"]:
    i = [k for k,x in enumerate(dates) if str(x)==dd]
    if i:
        i=i[0]; x=R[i]; xl=RL[i]
        big.append(dict(date=dd, R0050=x, R00631L=xl, ratio=xl/x, log=np.log1p(x), t1=x, t2=x-x**2/2, t3=x-x**2/2+x**3/3))
res["big"] = big
# QQQ/TQQQ 2022
q = pl.read_csv("raw/QQQ__us_2022.csv"); t = pl.read_csv("raw/TQQQ__us_2022.csv")
qt = q.join(t, on="date", suffix="_t").sort("date")
qa = qt["adj_close"].to_numpy(); ta = qt["adj_close_t"].to_numpy(); qd = qt["date"].to_list()
# returns within calendar 2022: from 2021-12-31 close to 2022-12-30 close
i0 = qd.index("2021-12-31"); i1 = qd.index("2022-12-30")
rq = qa[i0+1:i1+1]/qa[i0:i1]-1; rt = ta[i0+1:i1+1]/ta[i0:i1]-1
res["qqq2022"] = dict(n=len(rq), QQQ=qa[i1]/qa[i0]-1, TQQQ=ta[i1]/ta[i0]-1, thrice=3*(qa[i1]/qa[i0]-1),
    logQ=np.log1p(rq).sum(), logT=np.log1p(rt).sum(), gap=np.log1p(rt).sum()-3*np.log1p(rq).sum(),
    exact=(np.log1p(3*rq)-3*np.log1p(rq)).sum(), T2=-3*(rq**2).sum(), T3=-3*(rq**2).sum()+8*(rq**3).sum(),
    ann_vol=rq.std()*np.sqrt(252), RV=(rq**2).sum(), minq=rq.min(), mint=rt.min())
def conv(o):
    if isinstance(o, dict): return {k: conv(v) for k,v in o.items()}
    if isinstance(o, list): return [conv(v) for v in o]
    if isinstance(o, (np.floating,)): return float(o)
    if isinstance(o, (np.integer,)): return int(o)
    return o
json.dump(conv(res), open("processed/lm03_stats.json","w"), indent=1)
f = res["full"]
print(f"FULL {d0}->{d1} yrs={yrs:.2f} n={f['n']}")
for k in ["ret0050","ret00631L","twice0050","cagr0050","cagr00631L","log0050","log00631L","gap_log","exact_rebal","T2","T3","T4","residual","residual_per_year","T2_per_year","ann_vol_0050","ann_vol_00631L"]:
    print(f"  {k:18s} {f[k]: .5f}")
print("YEAR   n   r0050    r631L   2x0050   gaplog  exact    T2     T3    resid  RV")
for b in rows:
    print(f"{b['label']} {b['n']:4d} {b['ret0050']:8.4f} {b['ret00631L']:8.4f} {b['twice0050']:8.4f} {b['gap_log']:7.4f} {b['exact_rebal']:7.4f} {b['T2']:7.4f} {b['T3']:7.4f} {b['residual']:7.4f} {b['RV']:.4f}")
print("DAILY", {k: round(v,7) for k,v in res['daily'].items()})
print("FREQ"); [print("  ", {k:(round(v,6) if isinstance(v,float) else v) for k,v in x.items()}) for x in res['freq']]
print("BIG"); [print("  ", {k:(round(v,5) if isinstance(v,float) else v) for k,v in x.items()}) for x in big]
print("QQQ2022", {k:(round(v,5) if isinstance(v,float) else v) for k,v in res['qqq2022'].items()})
