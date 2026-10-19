/* LM23 interactive figure "regWindows": betas and intercepts of the 28 U28 market models by window and method.
   Data: the "widget" block of the chart JSON lm23-regWindows, inlined in the page by the build
   (<script type="application/json" id="chart-lm23-regWindows">), written by data/lm23_charts.py from
   data/lm23_common.py. For each of 22 windows (full sample, the two halves, the calendar years 2009-2025, 2026 to
   8 October, the last 250 returns) and each sector, in the order of the full-sample beta, it holds ten statistics of
   the OLS fit of the sector's daily price returns on the TAIEX's: beta; its classical, White (HC0) and Newey-West
   standard errors; the intercept and the same three standard errors; R-squared; s_eps (divisor T - 2). Newey-West uses
   Bartlett weights and the lag floor(4 (T/100)^(2/9)) of the window's T. Intervals are estimate +/- PhiInv(0.975) SE
   (normal reference); t-stats are the intercept over its standard error. Nothing is simulated or refitted here. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt;
  var METHODS = [["n", "Newey–West"], ["w", "White"], ["c", "Classical"]];
  var COL = { c: 1, w: 2, n: 3 };   // standard-error columns of beta; the intercept's are 4 further on

  B.widgets.regWindows = function (host) {
    var src = document.getElementById("chart-lm23-regWindows");
    if (!src) { host.innerHTML = '<p class="w-note">The data for this figure are not on the page.</p>'; return; }
    var W = JSON.parse(src.textContent).widget, names = W.names, A = W.A, z = B.dist.PhiInv(0.975), byKey = {};
    W.windows.forEach(function (w) { byKey[w.key] = w; });

    host.innerHTML = '<div class="w-head"><span class="w-title">Betas and alphas by window</span>' +
      '<span class="w-tag">Interactive</span></div>';
    var ctl = B.controls(host, [
      { type: "select", id: "rw-win", key: "win", label: "Window", value: W.init.window,
        options: W.windows.map(function (w) { return [w.key, w.label]; }) },
      { type: "select", id: "rw-meth", key: "meth", label: "Standard error", value: W.init.method, options: METHODS },
      { type: "select", id: "rw-sec", key: "sec", label: "Sector", value: W.init.sector,
        options: names.slice().sort() }
    ], draw);
    var chart = document.createElement("div"), out = document.createElement("div"), note = document.createElement("p");
    out.className = "readout"; out.setAttribute("aria-live", "polite"); note.className = "w-note";
    host.appendChild(chart); host.appendChild(out); host.appendChild(note);
    note.textContent = "Daily price returns of the 28 U28 sector indices on the TAIEX price index (no dividends), " +
      "in-sample. Rows keep the order of the full-sample beta, so a sector that moves shows it. Intervals are the " +
      "estimate ± 1.96 standard errors with the method chosen; Newey–West uses the book's lag for the window's size. " +
      "Every number was computed in advance by data/lm23_charts.py.";

    function draw(v) {
      var win = byKey[v.win], rows = W.rows[v.win], k = COL[v.meth], ri = names.indexOf(v.sec);
      var xs = [], ys = [], lines = [];
      rows.forEach(function (r, j) {
        var b = r[0], se = r[k];
        lines.push({ from: [b - z * se, j + 1], to: [b + z * se, j + 1], color: j === ri ? "2" : "var(--ink-2)",
                     width: j === ri ? 4 : 1.6 });
        if (j !== ri) { xs.push(b); ys.push(j + 1); }
      });
      var mname = METHODS.filter(function (m) { return m[0] === v.meth; })[0][1];
      B.chart(chart, {
        type: "scatter", equal: false, height: 600,
        alt: "Betas of the 28 U28 market models with " + mname + " 95% intervals, " + win.label + ", " + v.sec +
          " highlighted",
        x: { label: "Beta on the TAIEX", fmt: "n3", tfmt: "n1", name: "beta", min: W.xmin, max: W.xmax,
             ticks: [-0.5, 0, 0.5, 1.0, 1.5, 2.0] },
        y: { fmt: "n0", name: "sector", min: 0.4, max: 28.6, ticks: names.map(function (n, j) { return j + 1; }),
             tickLabels: names },
        series: [
          { name: "28 sectors", color: "1", r: 3.6, x: xs, y: ys },
          { name: v.sec, color: "2", r: 5, x: [rows[ri][0]], y: [ri + 1] }
        ],
        lines: lines
      });
      var r = rows[ri], b = r[0], se = r[k], a = r[4], sea = r[4 + k];
      out.innerHTML =
        "<div><span>Beta · " + mname + " SE</span><b>" + fmt(b, "n3") + " · " + fmt(se, "n4") + "</b></div>" +
        "<div><span>95% interval for beta</span><b>" + fmt(b - z * se, "n3") + " to " + fmt(b + z * se, "n3") + "</b></div>" +
        "<div><span>Intercept: bp a day · % a year</span><b>" + fmt(1e4 * a, "n2") + " · " + fmt(100 * A * a, "n2") + "%</b></div>" +
        "<div><span>t-stat of the intercept</span><b>" + fmt(a / sea, "n2") + "</b></div>" +
        "<div><span>R-squared · residual SD (% a day)</span><b>" + fmt(r[8], "n4") + " · " + fmt(100 * r[9], "n3") + "</b></div>" +
        "<div><span>Returns T · Newey–West lag</span><b>" + win.T.toLocaleString("en-US") + " · " + win.lag + "</b></div>";
    }
    host.__redraw = function () { draw(ctl.values()); };
    ctl.fire();
  };
})();
