/* LM31 interactive figure: equal risk, or a risk budget, for three funds by cyclical coordinate descent, (31.4).
   Data: the "widget" block of the chart JSON lm31-ercthree, inlined in the page by the build
   (<script type="application/json" id="chart-lm31-ercthree">), written by data/lm31_charts.py: the first window's
   annualized volatilities of 0050, 00679B and 00642U and their three correlations, unrounded, and the first budget
   1/3. Model numbers only once a slider moves: no market series and no random draws.
   Formulas: Sigma has entries rho_ij sigma_i sigma_j; a Cholesky factorization checks that it is positive definite (a
   failure shows a note and no solution). Budgets b = (b1, (1 - b1)/2, (1 - b1)/2). CCD (31.4) starts at
   y_i = 1/sigma_i and sweeps i = 1, 2, 3 until max_i |y_i (Sigma y)_i - b_i| < 1e-12, at most 1,000 sweeps; the
   weights are y / sum(y). Risk shares w_i (Sigma w)_i / w'Sigma w; volatility sqrt(w'Sigma w).
   The first drawing uses the data block's exact values; the sliders show the nearest step, and once one moves every
   input is a slider value. data/lm31_charts.py runs Book.widgets.ercThree.math in Node against Python's CCD and
   vol5_rules.erc on the initial state and on 500 random positive definite matrices. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt, NAMES = ["0050", "00679B", "00642U"], COLORS = ["1", "3", "4"];

  function cov(v, r) {            // v: volatilities; r: [rho12, rho13, rho23]
    var c = [[1, r[0], r[1]], [r[0], 1, r[2]], [r[1], r[2], 1]];
    return c.map(function (row, i) { return row.map(function (x, j) { return x * v[i] * v[j]; }); });
  }
  function pd(S) {                // Cholesky: true when every pivot is positive
    var L = [[0, 0, 0], [0, 0, 0], [0, 0, 0]], i, j, k, s;
    for (i = 0; i < 3; i++) for (j = 0; j <= i; j++) {
      for (s = S[i][j], k = 0; k < j; k++) s -= L[i][k] * L[j][k];
      if (i === j) { if (!(s > 1e-14)) return false; L[i][i] = Math.sqrt(s); } else L[i][j] = s / L[j][j];
    }
    return true;
  }
  function Sy(S, y, i) { return S[i][0] * y[0] + S[i][1] * y[1] + S[i][2] * y[2]; }
  function ccd(S, b) {            // (31.4); returns {w, sweeps}, or null after 1,000 sweeps
    var y = [0, 1, 2].map(function (i) { return 1 / Math.sqrt(S[i][i]); }), n, i, r, gap;
    for (n = 1; n <= 1000; n++) {
      for (i = 0; i < 3; i++) {
        r = Sy(S, y, i) - S[i][i] * y[i];
        y[i] = (Math.sqrt(r * r + 4 * S[i][i] * b[i]) - r) / (2 * S[i][i]);
      }
      for (gap = 0, i = 0; i < 3; i++) gap = Math.max(gap, Math.abs(y[i] * Sy(S, y, i) - b[i]));
      if (gap < 1e-12) { var t = y[0] + y[1] + y[2]; return { w: y.map(function (x) { return x / t; }), sweeps: n }; }
    }
    return null;
  }
  function variance(S, w) { return w[0] * Sy(S, w, 0) + w[1] * Sy(S, w, 1) + w[2] * Sy(S, w, 2); }
  function shares(S, w) { var v = variance(S, w); return w.map(function (x, i) { return x * Sy(S, w, i) / v; }); }
  function inverseVol(S) {
    var u = [0, 1, 2].map(function (i) { return 1 / Math.sqrt(S[i][i]); }), t = u[0] + u[1] + u[2];
    return u.map(function (x) { return x / t; });
  }

  B.widgets.ercThree = function (host) {
    var src = document.getElementById("chart-lm31-ercthree");
    if (!src) { host.innerHTML = '<p class="w-note">The data for this figure are not on the page.</p>'; return; }
    var W = JSON.parse(src.textContent).widget, exact = true;
    function near(x, step) { return Math.round(x / step) * step; }
    host.innerHTML = '<div class="w-head"><span class="w-title">Equal risk, or a budget, for three funds</span>' +
      '<span class="w-tag">Interactive</span></div>';
    var defs = NAMES.map(function (nm, i) {
      return { id: "erc-v" + i, key: "v" + i, label: "σ " + nm, min: 2, max: 40, step: 0.1,
               value: near(100 * W.vols[i], 0.1).toFixed(1), fmt: function (x) { return fmt(x / 100, "pct1"); } };
    }).concat([["ρ 0050–00679B", 0], ["ρ 0050–00642U", 1], ["ρ 00679B–00642U", 2]].map(function (p) {
      return { id: "erc-r" + p[1], key: "r" + p[1], label: p[0], min: -0.9, max: 0.9, step: 0.01,
               value: near(W.corr[p[1]], 0.01).toFixed(2), fmt: "n2" };
    })).concat([{ id: "erc-b", key: "b1", label: "Budget b₁ of 0050", min: 0.1, max: 0.8, step: 0.01,
                  value: near(W.b1, 0.01).toFixed(2), fmt: "n2" }]);
    var ctl = B.controls(host, defs, draw);
    var chart = document.createElement("div"), out = document.createElement("div"), note = document.createElement("p");
    out.className = "readout"; out.setAttribute("aria-live", "polite"); note.className = "w-note";
    note.textContent = "Starting point: the first window's 0050, 00679B and 00642U (13 February 2017 to 27 February " +
      "2019), with their unrounded volatilities and correlations and b₁ = 1/3, so the budget portfolio is ERC. Once a " +
      "slider moves, every input is a slider value (constructed). The other two funds share 1 − b₁ equally. Weights " +
      "by CCD (31.4) to 1e-12; risk shares RC_i/σ_p; volatilities a year.";
    host.appendChild(chart); host.appendChild(out); host.appendChild(note);

    function draw(v, id) {
      if (id != null) exact = false;
      var vols = exact ? W.vols : [v.v0 / 100, v.v1 / 100, v.v2 / 100];
      var rho = exact ? W.corr : [v.r0, v.r1, v.r2], b1 = exact ? W.b1 : v.b1;
      var S = cov(vols, rho), b = [b1, (1 - b1) / 2, (1 - b1) / 2];
      if (!pd(S)) {
        chart.innerHTML = ""; out.innerHTML = '<div><span>Covariance matrix</span><b>not positive definite: ' +
          'no solution</b></div>'; return;
      }
      var sol = ccd(S, b);
      if (!sol) { chart.innerHTML = ""; out.innerHTML = "<div><span>CCD</span><b>no convergence</b></div>"; return; }
      var books = [["1/N", [1 / 3, 1 / 3, 1 / 3]], ["IV", inverseVol(S)], ["Budget", sol.w]];
      var cats = [], vals = [[], [], []];
      books.forEach(function (bk) {
        var sh = shares(S, bk[1]);
        cats.push(bk[0] + " weights", bk[0] + " risk");
        for (var i = 0; i < 3; i++) { vals[i].push(bk[1][i]); vals[i].push(sh[i]); }
      });
      B.chart(chart, {
        type: "bar", stack: true, valueLabels: false, height: 280,
        alt: "Weights and risk shares of 1/N, inverse volatility and the budget portfolio for three funds, stacked " +
          "to 100% in each bar",
        categories: cats, x: { label: "" }, y: { fmt: "pct1", tfmt: "pct0", label: "Share", min: 0, max: 1,
                                                    ticks: [0, 0.25, 0.5, 0.75, 1] },
        series: NAMES.map(function (nm, i) { return { name: nm, color: COLORS[i], values: vals[i], fmt: "pct1" }; })
      });
      function list(xs, code) { return xs.map(function (x) { return fmt(x, code); }).join(", "); }
      function item(lbl, val) { return "<div><span>" + lbl + "</span><b>" + val + "</b></div>"; }
      out.innerHTML =
        item("Budget weights", list(sol.w, "n4")) +
        item("Budget risk shares", list(shares(S, sol.w), "pct1")) +
        item("Inverse volatility's risk shares", list(shares(S, books[1][1]), "pct1")) +
        item("1/N's risk shares", list(shares(S, books[0][1]), "pct1")) +
        item("Volatility a year: 1/N, IV, budget", list(books.map(function (bk) {
          return Math.sqrt(variance(S, bk[1])); }), "pct2")) +
        item("CCD sweeps", String(sol.sweeps));
    }
    host.__redraw = function () { draw(ctl.values(), null); };
    ctl.fire();
  };
  B.widgets.ercThree.math = { cov: cov, pd: pd, ccd: ccd, shares: shares, inverseVol: inverseVol, variance: variance };
})();
