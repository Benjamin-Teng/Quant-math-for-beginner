/* LM27 interactive figure: weights against risk shares, (27.5)-(27.7).
   Data: the "widget" block of the chart JSON lm27-riskSplit, inlined in the page by the build
   (<script type="application/json" id="chart-lm27-riskSplit">), written by data/lm27_charts.py: the five funds and
   three annualized 5x5 covariance matrices of E5 in decimals, ten decimals each (daily on the 2,362 joint dates, A =
   242.951; monthly on 116 calendar months, A = 12; daily on the window 29 January 2018 to 27 February 2020, A of the
   full sample). Matrices only: no market series.
   Formulas: Sigma w, s_p = sqrt(w'Sigma w), shares w_i (Sigma w)_i / s_p^2, which sum to 1 by (27.5); the weighted
   average volatility sum_i w_i s_i and the ratio (27.7) while every weight is >= 0, else sum_i |w_i| s_i, the bound of
   (8.11) with a short. The matrices are positive semidefinite by (10.5), so only s_p > 0 is checked. No optimizer.
   data/lm27_charts.py runs Book.widgets.riskSplit.math in Node against NumPy. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt;

  function split(S, w) {   // s_p, shares, the weighted (or absolute) average volatility and the ratio
    var n = w.length, Sw = [], v = 0, avg = 0, shortSold = false, i, j;
    for (i = 0; i < n; i++) {
      Sw.push(0);
      for (j = 0; j < n; j++) Sw[i] += S[i][j] * w[j];
      v += w[i] * Sw[i];
      avg += Math.abs(w[i]) * Math.sqrt(S[i][i]);
      if (w[i] < 0) shortSold = true;
    }
    if (!(v > 0)) return null;
    var sp = Math.sqrt(v), shares = [], sum = 0;
    for (i = 0; i < n; i++) { shares.push(w[i] * Sw[i] / v); sum += shares[i]; }
    return { sp: sp, shares: shares, sum: sum, avg: avg, ratio: avg / sp, shortSold: shortSold };
  }

  B.widgets.riskSplit = function (host) {
    var src = document.getElementById("chart-lm27-riskSplit");
    if (!src) { host.innerHTML = '<p class="w-note">The data for this figure are not on the page.</p>'; return; }
    var W = JSON.parse(src.textContent).widget, F = W.funds;
    host.innerHTML = '<div class="w-head"><span class="w-title">Weights against risk shares</span>' +
      '<span class="w-tag">Interactive</span></div>';
    var defs = F.slice(0, 4).map(function (s, i) {
      return { id: "rs-" + i, key: "w" + i, label: s, min: -0.2, max: 1, step: 0.01, value: W.init.w[i], fmt: "pct0" };
    });
    defs.push({ type: "select", id: "rs-m", key: "mat", label: "Covariance matrix", options: W.options, value: W.init.mat });
    var ctl = B.controls(host, defs, draw);
    var chart = document.createElement("div"), out = document.createElement("div"), note = document.createElement("p");
    out.className = "readout"; out.setAttribute("aria-live", "polite"); note.className = "w-note";
    note.textContent = "Descriptive: E5's daily total returns, annualized, divisor T. " + F[4] + " takes the rest of " +
      "the money. A risk share is w_i (Σw)_i / s_p², so the shares always add up to 100%; a negative share means " +
      "that the fund lowers the book's volatility at the margin.";
    host.appendChild(chart); host.appendChild(out); host.appendChild(note);

    function draw(v) {
      var w = [v.w0, v.w1, v.w2, v.w3], i;
      w.push(1 - w[0] - w[1] - w[2] - w[3]);
      w = w.map(function (x) { return Math.round(x * 1e10) / 1e10; });   // 0.2 + 0.2 + ... is not exactly 1 in floats
      var r = split(W.mats[v.mat], w);
      if (!r) { out.innerHTML = "<div><span>s_p</span><b>0: no split</b></div>"; return; }
      B.chart(chart, {
        type: "bar", height: 260,
        alt: "Money weights against risk shares of the five funds under the " + v.mat + " covariance matrix",
        categories: F, x: { label: "Fund" }, y: { fmt: "pct1", tfmt: "pct0", label: "Share of the book" },
        series: [{ name: "money", color: "1", values: w }, { name: "risk", color: "2", values: r.shares }],
        ann: [{ type: "hline", y: 0 }]
      });
      var html = "<div><span>Book's volatility, a year</span><b>" + fmt(r.sp, "pct2") + "</b></div>";
      html += r.shortSold
        ? "<div><span>Σ|w_i| s_i, (8.11) with a short</span><b>" + fmt(r.avg, "pct2") + "</b></div>" +
          "<div><span>Its ratio to s_p</span><b>" + fmt(r.ratio, "n2") + "</b></div>"
        : "<div><span>Weighted average volatility</span><b>" + fmt(r.avg, "pct2") + "</b></div>" +
          "<div><span>Ratio (27.7)</span><b>" + fmt(r.ratio, "n2") + "</b></div>";
      html += "<div><span>Sum of the risk shares</span><b>" + fmt(r.sum, "pct1") + "</b></div>";
      for (i = 0; i < F.length; i++) html += "<div><span>" + F[i] + ": money, risk</span><b>" + fmt(w[i], "pct1") +
        ", " + fmt(r.shares[i], "pct1") + "</b></div>";
      if (w[4] < 0) html += "<div><span>" + F[4] + ' is sold short</span><b class="bad">' + fmt(w[4], "pct0") + "</b></div>";
      out.innerHTML = html;
    }
    host.__redraw = function () { draw(ctl.values()); };
    ctl.fire();
  };
  B.widgets.riskSplit.math = { split: split };
})();
