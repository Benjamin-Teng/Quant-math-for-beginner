/* LM17 interactive figure: mean path, median path and the 5%-95% range of wealth in the iid model of TAIEX days.
   Data: the "widget" block of the chart JSON lm17-wealth, inlined in the page by the build
   (<script type="application/json" id="chart-lm17-wealth">), written by data/lm17_charts.py: the sample's mean daily
   return, A, the 95% normal quantile and the grid of (f, gbar(f), s_r(f)) for f = 0.25, 0.5, ..., 8, where gbar(f) and
   s_r(f) are the mean and standard deviation (divisor T) of ln(1 + f R_t) over TR23's 5,849 daily returns.
   Formulas: mean path (1 + f Rbar)^m, the exact iid mean; median exp(m gbar); quantiles exp(m gbar -/+ z95 s_r sqrt m);
   Pr(W_m < W_0) ~ Phi(-gbar sqrt m / s_r); Pr(W_m > E W_m) ~ Phi(-sqrt m delta / s_r), delta = ln(1 + f Rbar) - gbar
   (the lognormal approximation, (17.6)). Nothing is simulated. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt;

  function fmtW(v) {   // wealth per unit: 25.20, 115.6, 2,147, 2.20e6
    if (v == null || !isFinite(v)) return "—";
    if (v >= 1e6 || v < 0.01) return fmt(v, "sig3");
    if (v >= 1000) return fmt(v, "n0");
    if (v >= 100) return fmt(v, "n1");
    return fmt(v, "n2");
  }
  function fmtP(p) { return p < 1e-4 ? fmt(p, "sci1") : fmt(p, "pct2"); }
  function clip(v) { return v >= 1e-3 && v <= 1e7 ? v : null; }

  B.widgets.wealth = function (host) {
    var src = document.getElementById("chart-lm17-wealth");
    if (!src) { host.innerHTML = '<p class="w-note">The data for this figure are not on the page.</p>'; return; }
    var W = JSON.parse(src.textContent).widget, A = W.A, Rb = W.Rbar, z95 = W.z95, Phi = B.dist.Phi, byF = {};
    W.grid.forEach(function (g) { byF[g[0].toFixed(2)] = { g: g[1], s: g[2] }; });

    host.innerHTML = '<div class="w-head"><span class="w-title">Mean, median and the range of wealth</span>' +
      '<span class="w-tag">Interactive</span></div>';
    var ctl = B.controls(host, [
      { id: "wl-f", key: "f", label: "Leverage f", min: 0.25, max: 8, step: 0.25, value: W.init.f,
        fmt: function (v) { return v.toFixed(2) + "×"; } },
      { id: "wl-m", key: "m", label: "Horizon m (sessions)", min: 1, max: W.mMax, step: 1, value: W.init.m,
        fmt: function (v) { return v.toLocaleString("en-US") + " (" + (v / A).toFixed(2) + " years)"; } }
    ], draw);
    var chart = document.createElement("div"), out = document.createElement("div"), note = document.createElement("p");
    out.className = "readout"; out.setAttribute("aria-live", "polite"); note.className = "w-note";
    host.appendChild(chart); host.appendChild(out); host.appendChild(note);
    var c1 = W.check.f1, c8 = W.check.f8;
    note.textContent = "Model: days drawn independently from TAIEX's " + W.T.toLocaleString("en-US") +
      " daily total returns, in-sample, not a forecast; leverage is hypothetical (daily rebalancing, free borrowing, " +
      "no costs). The median, the 5% to 95% band and both chances use the lognormal approximation (17.6) with the " +
      "mean and standard deviation of ln(1 + f R) at that leverage. The mean path is the exact iid mean, (1 + f × " +
      "average day)^m; the lognormal mean would give " + fmtW(c1.lognormal) + " instead of " + fmtW(c1.iid) +
      " over the sample at f = 1, and " + fmtW(c8.lognormal) + " instead of " + fmtW(c8.iid) + " at f = 8.";

    function draw(v) {
      var f = v.f, m = Math.round(v.m), p = byF[f.toFixed(2)], g = p.g, s = p.s;
      var d = Math.log(1 + f * Rb) - g, xs = [], mean = [], med = [], lo = [], hi = [], ks = [];
      for (var k = 0; k <= 240; k++) ks.push(Math.round(k * W.mMax / 240));
      ks.push(m);
      ks.sort(function (a, b) { return a - b; });
      ks.forEach(function (mk, i) {
        if (i > 0 && mk === ks[i - 1]) return;
        xs.push(mk / A);
        mean.push(clip(Math.pow(1 + f * Rb, mk)));
        med.push(clip(Math.exp(mk * g)));
        lo.push(clip(Math.exp(mk * g - z95 * s * Math.sqrt(mk))));
        hi.push(clip(Math.exp(mk * g + z95 * s * Math.sqrt(mk))));
      });
      B.chart(chart, {
        alt: "Wealth per unit invested at leverage " + f.toFixed(2) + " over 0 to 40 years: mean path, median path and " +
          "the 5% to 95% band, log scale, horizon " + (m / A).toFixed(2) + " years",
        height: 320,
        x: { type: "num", fmt: "n2", tfmt: "n0", label: "Horizon in years (m / A sessions)", tipLabel: "years: ",
             min: 0, max: 40, ticks: [0, 5, 10, 15, 20, 25, 30, 35, 40] },
        y: { type: "log", fmt: "sig4", tfmt: "sci0", label: "Wealth per unit invested (log scale)", min: 0.01, max: 1e6,
             ticks: [0.01, 1, 100, 1e4, 1e6] },
        series: [
          { name: "5% to 95% quantile", color: "3", x: xs, lo: lo, hi: hi },
          { name: "Mean path", color: "2", dash: true, x: xs, y: mean },
          { name: "Median path", color: "1", x: xs, y: med }
        ],
        ann: [{ type: "hline", y: 1 }, { type: "vline", x: m / A, dash: true, label: (m / A).toFixed(2) + " years" }]
      });
      var sm = Math.sqrt(m);
      out.innerHTML =
        "<div><span>Mean path, exact iid mean</span><b>" + fmtW(Math.pow(1 + f * Rb, m)) + "</b></div>" +
        "<div><span>Median path</span><b>" + fmtW(Math.exp(m * g)) + "</b></div>" +
        "<div><span>5% and 95% quantiles</span><b>" + fmtW(Math.exp(m * g - z95 * s * sm)) + " · " +
          fmtW(Math.exp(m * g + z95 * s * sm)) + "</b></div>" +
        "<div><span>Chance of ending below the start</span><b>" + fmtP(Phi(-g * sm / s)) + "</b></div>" +
        "<div><span>Chance of ending above the mean path</span><b>" + fmtP(Phi(-sm * d / s)) + "</b></div>" +
        "<div><span>Horizon: sessions · years</span><b>" + m.toLocaleString("en-US") + " · " + (m / A).toFixed(2) + "</b></div>";
    }
    host.__redraw = function () { draw(ctl.values()); };
    ctl.fire();
  };
})();
