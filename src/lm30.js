/* LM30 interactive figure: shrinkage from equal weights to minimum variance, (30.1) with (11.8).
   Data: the "widget" block of the chart JSON lm30-shrinkPath, inlined in the page by the build
   (<script type="application/json" id="chart-lm30-shrinkPath">), written by data/lm30_charts.py: for four windows of
   U28's first half (the last 30, 60 and 250 returns, and the whole half of 2,191) the 28 annual eigenvalues of the
   sample matrix (largest first), their unit eigenvectors q_k and Ledoit and Wolf's c_hat; the second half's annual
   covariance matrix; the 28 sector names. Derived statistics of price indices only: no return series, no dates.
   Formulas: by (30.1) the shrunk matrix has the sample's eigenvectors and eigenvalues d_k = c lambda_k + (1 - c) lam_bar,
   lam_bar the mean eigenvalue; by (11.8) its minimum-variance weights are w = x / 1'x with
   x = sum_k q_k (q_k'1) / d_k, its predicted variance 1 / 1'x and kappa_c = d_1 / d_N. The realized volatility is
   sqrt(w' S2 w) with the second half's matrix. No optimizer, no simulation (plans/vol-5.md, "Widgets").
   The first draw, a change of window and the reset button use the window's exact c_hat; only the slider moves c.
   data/lm30_charts.py runs Book.widgets.shrinkPath.math in Node against NumPy. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt;

  function solve(win, c) {           // (30.1) and (11.8): weights, predicted variance and kappa of the shrunk matrix
    var n = win.lam.length, lb = 0, k, i, d = [], x = [], s = 0;
    for (k = 0; k < n; k++) lb += win.lam[k] / n;
    for (k = 0; k < n; k++) d.push(c * win.lam[k] + (1 - c) * lb);
    for (i = 0; i < n; i++) x.push(0);
    for (k = 0; k < n; k++) {
      var q = win.q[k], q1 = 0;
      for (i = 0; i < n; i++) q1 += q[i];
      for (i = 0; i < n; i++) x[i] += q[i] * q1 / d[k];
    }
    for (i = 0; i < n; i++) s += x[i];
    return { w: x.map(function (v) { return v / s; }), pvar: 1 / s, kappa: d[0] / d[n - 1], d: d };
  }
  function quad(w, M) {               // w'M w
    var t = 0, i, j;
    for (i = 0; i < w.length; i++) for (j = 0; j < w.length; j++) t += w[i] * M[i][j] * w[j];
    return t;
  }

  B.widgets.shrinkPath = function (host) {
    var src = document.getElementById("chart-lm30-shrinkPath");
    if (!src) { host.innerHTML = '<p class="w-note">The data for this figure are not on the page.</p>'; return; }
    var SP = JSON.parse(src.textContent), W = SP.widget, cur = null;
    var WINS = W.windows.map(function (w, i) { return [String(i), w.label]; });

    host.innerHTML = '<div class="w-head"><span class="w-title">Shrinkage from equal weights to minimum variance</span>' +
      '<span class="w-tag">Interactive</span></div>';
    var ctl = B.controls(host, [
      { type: "select", id: "sp-w", key: "win", label: "Window of U28's first half", options: WINS, value: W.init.win },
      { id: "sp-c", key: "c", label: "Data's weight c", min: 0, max: 1, step: 0.01,
        value: W.windows[+W.init.win].chat, fmt: "n2" },
      { type: "button", id: "sp-r", label: "Reset c to Ledoit–Wolf's estimate" }
    ], draw);
    var chart = document.createElement("div"), out = document.createElement("div"), note = document.createElement("p");
    out.className = "readout"; out.setAttribute("aria-live", "polite"); note.className = "w-note";
    note.textContent = "Price indices, no dividends. The weights come from (11.8) with the shrunk eigenvalues of " +
      "(30.1); no optimizer runs. Predicted volatility uses the shrunk matrix of the chosen window, realized " +
      "volatility the second half (" + W.secondHalf + "), so the c that minimizes it is hindsight. At c = 0 the " +
      "portfolio is 1/N.";
    host.appendChild(chart); host.appendChild(out); host.appendChild(note);
    var slider = host.querySelector("#sp-c"), label = slider.parentNode.querySelector(".v");

    function draw(v, id) {
      var win = W.windows[+v.win];
      if (id === "sp-c") cur = v.c;
      else if (id !== "redraw" || cur === null) {   // first draw, a new window or the reset: the exact c_hat
        cur = win.chat; slider.value = String(win.chat); label.textContent = fmt(+slider.value, "n2");
      }
      var r = solve(win, cur), big = 0, gross = 0, i;
      for (i = 0; i < r.w.length; i++) { gross += Math.abs(r.w[i]); if (Math.abs(r.w[i]) > Math.abs(r.w[big])) big = i; }
      var ks = win.lam.map(function (_, k) { return k + 1; });
      B.chart(chart, {
        alt: "Annual eigenvalues of U28's sample covariance matrix on " + win.label + ", largest first, and of the " +
          "matrix shrunk with c = " + fmt(cur, "n3") + ", log scale: shrinkage keeps the eigenvectors and pulls every " +
          "eigenvalue toward their mean",
        height: 280,
        x: { type: "num", fmt: "n0", label: "Eigenvalue index k", tipLabel: "k = ", min: 1, max: ks.length,
             ticks: [1, 7, 14, 21, 28] },
        y: { type: "log", fmt: "sig3", tfmt: "sci0", label: "Annual eigenvalue, log scale", min: W.ymin, max: W.ymax },
        series: [
          { name: "Sample", color: "1", x: ks, y: win.lam },
          { name: "Shrunk", color: "2", x: ks, y: r.d }
        ]
      });
      out.innerHTML =
        "<div><span>Ledoit–Wolf c (this window)</span><b>" + fmt(win.chat, "n3") + "</b></div>" +
        "<div><span>c used</span><b>" + fmt(cur, "n3") + "</b></div>" +
        "<div><span>Condition number κ<sub>c</sub></span><b>" + fmt(r.kappa, "n1") + "</b></div>" +
        "<div><span>Predicted volatility</span><b>" + fmt(Math.sqrt(r.pvar), "pct2") + "</b></div>" +
        "<div><span>Realized, second half</span><b>" + fmt(Math.sqrt(quad(r.w, W.S2)), "pct2") + "</b></div>" +
        "<div><span>Gross exposure (sum of |w|)</span><b>" + fmt(gross, "n2") + "</b></div>" +
        "<div><span>Largest weight</span><b>" + fmt(r.w[big], "pct1") + " " + W.names[big] + "</b></div>";
    }
    host.__redraw = function () { draw(ctl.values(), "redraw"); };
    ctl.fire();
  };
  B.widgets.shrinkPath.math = { solve: solve, quad: quad };
})();
