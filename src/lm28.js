/* LM28 interactive figure: the frontier, the tangency portfolio and one correlation, (28.2), (28.5) and (28.6).
   Data: the "widget" block of the chart JSON lm28-frontierLab, inlined in the page by the build
   (<script type="application/json" id="chart-lm28-frontierLab">), written by data/lm28_charts.py: the first window's
   annual means mu, covariance matrix S and r_f at full precision (31 numbers), the fund names and the sliders'
   rounded starting values. No market series and no random draws.
   First drawing: the data block's exact mu and S, so the figure (and the PDF) equals the frontier exhibit. Each slider
   starts at a rounded value (00646's mean 10.0%, 00635U's 0.8%, corr(0050, 00646) 0.54), and its value replaces the
   window's exact entry only once that slider has moved; a moved correlation sets S[0][1] = S[1][0] = rho s_0 s_1, the
   other entries staying the window's.
   Math (module-local, Book.widgets.frontierLab.math.solve): a Cholesky factor of S, which exists exactly when S is
   positive definite (LM12); two triangular solves for S^-1 1 and S^-1 mu; then (28.2), (28.5) and (28.6), with the
   tangency portfolio only when 1'S^-1 e > 0 (r_f < mu_mv). data/lm28_charts.py runs it in Node against NumPy. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt, Y0 = -0.02, Y1 = 0.12, XMAX = 0.25;

  function solve(mu, S, rf) {   // null when S is not positive definite
    var n = mu.length, L = [], i, j, k, s;
    for (i = 0; i < n; i++) {   // Cholesky, S = L L': the positive-definiteness test
      L.push([]);
      for (j = 0; j <= i; j++) {
        for (s = S[i][j], k = 0; k < j; k++) s -= L[i][k] * L[j][k];
        if (i === j) { if (!(s > 0)) return null; L[i][i] = Math.sqrt(s); } else L[i][j] = s / L[j][j];
      }
    }
    function sol(b) {   // S^-1 b by forward and backward substitution
      var y = [], x = [];
      for (i = 0; i < n; i++) { for (s = b[i], k = 0; k < i; k++) s -= L[i][k] * y[k]; y.push(s / L[i][i]); }
      for (i = n - 1; i >= 0; i--) { for (s = y[i], k = i + 1; k < n; k++) s -= L[k][i] * x[k]; x[i] = s / L[i][i]; }
      return x;
    }
    function dot(a, b) { var t = 0; for (var q = 0; q < n; q++) t += a[q] * b[q]; return t; }
    var one = mu.map(function () { return 1; }), a = sol(one), m = sol(mu), A1 = dot(one, a);
    var wmv = a.map(function (v) { return v / A1; }), mumv = dot(mu, wmv);
    var y = m.map(function (v, q) { return v - rf * a[q]; }), den = dot(one, y);   // S^-1 e and 1'S^-1 e
    return { wmv: wmv, s2min: 1 / A1, mumv: mumv, srinf2: dot(mu, m) - mumv * mumv * A1, den: den,
             sr: Math.sqrt(dot(mu, y) - rf * den), wtan: den > 0 ? y.map(function (v) { return v / den; }) : null };
  }

  function r4(v) { return Math.round(v * 1e4) / 1e4; }
  function vec(w) { return "(" + w.map(function (x) { return fmt(100 * x, "n1"); }).join(", ") + ")%"; }

  B.widgets.frontierLab = function (host) {
    var src = document.getElementById("chart-lm28-frontierLab");
    if (!src) { host.innerHTML = '<p class="w-note">The data for this figure are not on the page.</p>'; return; }
    var W = JSON.parse(src.textContent).widget, F = W.funds;
    var sd = W.S.map(function (row, i) { return Math.sqrt(row[i]); }), base = solve(W.mu, W.S, W.rf), moved = {};

    host.innerHTML = '<div class="w-head"><span class="w-title">Frontier, tangency and one correlation</span>' +
      '<span class="w-tag">Interactive</span></div>';
    var ctl = B.controls(host, [
      { id: "fl-m1", key: "mu646", label: "Mean of 00646 (% a year)", min: 0, max: 20, step: 0.1, value: W.sliders.mu646, fmt: "n1" },
      { id: "fl-m3", key: "mu635", label: "Mean of 00635U (% a year)", min: -5, max: 10, step: 0.1, value: W.sliders.mu635, fmt: "n1" },
      { id: "fl-r", key: "rho", label: "Correlation of 0050 and 00646", min: -0.95, max: 0.99, step: 0.01, value: W.sliders.rho, fmt: "n2" }
    ], draw);
    var msg = document.createElement("p"), c1 = document.createElement("div"), c2 = document.createElement("div");
    var out = document.createElement("div"), note = document.createElement("p");
    msg.className = "w-note"; out.className = "readout"; out.setAttribute("aria-live", "polite"); note.className = "w-note";
    note.textContent = "In-sample: the first window's plug-in moments, a riskless rate of 1.5% a year. Solid: the " +
      "efficient frontier; dashed: its lower half and, from 1.5%, the capital market line. The first drawing uses the " +
      "window's exact inputs. The sliders move in rounded steps: once moved, a slider's value replaces the window's " +
      "exact entry, so moving it back leaves the readouts slightly off the exhibit's values. Bars: tangency weights, " +
      "the window's against the sliders'.";
    host.appendChild(msg); host.appendChild(c1); host.appendChild(c2); host.appendChild(out); host.appendChild(note);

    function draw(v, id) {
      if (id) moved[id] = true;
      var mu = W.mu.slice(), S = W.S.map(function (row) { return row.slice(); });
      if (moved["fl-m1"]) mu[1] = v.mu646 / 100;
      if (moved["fl-m3"]) mu[3] = v.mu635 / 100;
      if (moved["fl-r"]) S[0][1] = S[1][0] = v.rho * sd[0] * sd[1];
      var r = solve(mu, S, W.rf), curves = [], pts = [], k, m, ex = [], ey = [], ix = [], iy = [];
      if (r) {
        for (k = 0; k <= 120; k++) {   // (28.5): efficient branch up to 12%, lower branch down to -2%
          m = r.mumv + (Y1 - r.mumv) * k / 120;
          if (m >= r.mumv) { ex.push(r4(100 * Math.sqrt(r.s2min + Math.pow(m - r.mumv, 2) / r.srinf2))); ey.push(r4(100 * m)); }
          m = Y0 + (r.mumv - Y0) * k / 120;
          if (m <= r.mumv) { ix.push(r4(100 * Math.sqrt(r.s2min + Math.pow(m - r.mumv, 2) / r.srinf2))); iy.push(r4(100 * m)); }
        }
        curves.push({ x: ex, y: ey, color: "2", width: 2 }, { x: ix, y: iy, color: "2", dash: true });
        pts.push({ at: [100 * Math.sqrt(r.s2min), 100 * r.mumv], label: "minimum variance", color: "4", dx: 6, dy: 8 });
        if (r.wtan) {
          curves.push({ x: [0, 100 * (Y1 - W.rf) / r.sr], y: [100 * W.rf, 100 * Y1], color: "3", dash: true });
          var mt = 0, vt = 0, i, j;
          for (i = 0; i < 5; i++) { mt += r.wtan[i] * mu[i]; for (j = 0; j < 5; j++) vt += r.wtan[i] * S[i][j] * r.wtan[j]; }
          pts.push({ at: [100 * Math.sqrt(vt), 100 * mt], label: "tangency", color: "4", dx: -8, dy: -8 });
        }
      }
      msg.innerHTML = !r ? "<b>Σ is not positive definite: no frontier.</b>" :
        !r.wtan ? "<b>r<sub>f</sub> ≥ μ<sub>mv</sub>: no tangency portfolio.</b> The frontier is still drawn." : "";
      B.chart(c1, {
        type: "scatter", height: 330,
        alt: "Frontier explorer: the five funds, the efficient frontier, the capital market line and the minimum-variance " +
          "and tangency portfolios for the current means and correlation, % a year",
        x: { label: "Volatility (% a year)", fmt: "n2", tfmt: "n0", min: 0, max: 100 * XMAX, ticks: [0, 5, 10, 15, 20, 25], name: "volatility" },
        y: { label: "Mean (% a year)", fmt: "n2", tfmt: "n0", min: 100 * Y0, max: 100 * Y1, ticks: [-2, 0, 2, 4, 6, 8, 10, 12], name: "mean" },
        series: [{ name: "funds", color: "1", x: sd.map(function (s) { return 100 * s; }), y: mu.map(function (x) { return 100 * x; }), labels: F }],
        curves: curves, points: pts
      });
      B.chart(c2, {
        type: "bar", height: 220,
        alt: "Tangency weights of the five funds: the first window's against the current sliders'",
        categories: F, x: { label: "Fund" },
        y: { fmt: "pct1", tfmt: "pct0", label: "Tangency weight", min: -0.4, max: 1, ticks: [-0.4, 0, 0.4, 0.8] },
        series: [{ name: "first window", color: "2", values: base.wtan, fmt: "pct1" },
                 { name: "with the sliders", color: "1", values: r && r.wtan ? r.wtan : F.map(function () { return null; }), fmt: "pct1" }],
        ann: [{ type: "hline", y: 0 }]
      });
      var g = 0;
      if (r && r.wtan) r.wtan.forEach(function (x) { g += Math.abs(x); });
      out.innerHTML = !r ? "<div><span>Frontier</span><b>none (Σ not positive definite)</b></div>" :
        "<div><span>w<sup>mv</sup></span><b>" + vec(r.wmv) + "</b></div>" +
        "<div><span>σ<sub>min</sub>, a year</span><b>" + fmt(Math.sqrt(r.s2min), "pct2") + "</b></div>" +
        "<div><span>μ<sub>mv</sub>, a year</span><b>" + fmt(r.mumv, "pct2") + "</b></div>" +
        "<div><span>w<sup>tan</sup></span><b>" + (r.wtan ? vec(r.wtan) : "none (r<sub>f</sub> ≥ μ<sub>mv</sub>)") + "</b></div>" +
        "<div><span>SR*</span><b>" + (r.wtan ? fmt(r.sr, "n3") : "—") + "</b></div>" +
        "<div><span>Gross exposure of w<sup>tan</sup></span><b>" + (r.wtan ? fmt(g, "n2") : "—") + "</b></div>";
    }
    host.__redraw = function () { draw(ctl.values(), null); };
    ctl.fire();
  };
  B.widgets.frontierLab.math = { solve: solve };
})();
