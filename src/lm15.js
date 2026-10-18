/* LM15 interactive figure: Student-t explorer, TAIEX's histogram beside the fitted normal and a Student-t.
   Data: the "widget" block of the chart JSON lm15-tailchart, inlined in the page by the build
   (<script type="application/json" id="chart-lm15-tailchart">), written by data/lm15_charts.py: the sample's size,
   mean and standard deviation (divisor T), the maximum-likelihood Student-t, the kurtosis fit's nu, a histogram in
   0.5-point bins, the sorted returns at or below -0.95% (ten decimals) and SciPy's values for a check on load.
   Distribution functions come from Book.dist; the 1% quantile of a Student-t is found here by bisection on tCdf.
   data/lm15_charts.py runs the functions in Book.widgets.tdist.math in Node against SciPy. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt, D = B.dist;

  /* quantile of the standard Student-t at level u (0 < u < 1/2) by bisection on Book.dist.tCdf */
  function tq(u, nu) {
    var lo = -1, hi = 0;
    while (D.tCdf(lo, nu) > u) { hi = lo; lo *= 2; }
    for (var i = 0; i < 200 && hi - lo > 1e-14 * Math.abs(lo); i++) {
      var mid = (lo + hi) / 2;
      if (D.tCdf(mid, nu) > u) hi = mid; else lo = mid;
    }
    return (lo + hi) / 2;
  }
  function tDays(x, nu, loc, sc, n) { return n * D.tCdf((x - loc) / sc, nu); }
  function normDays(x, mu, sd, n) { return n * D.Phi((x - mu) / sd); }
  function days(v) { return v == null || !isFinite(v) ? "—" : v >= 0.001 ? fmt(v, "sig3") : fmt(v, "sci1"); }

  B.widgets.tdist = function (host) {
    var src = document.getElementById("chart-lm15-tailchart");
    if (!src) { host.innerHTML = '<p class="w-note">The data for this figure are not on the page.</p>'; return; }
    var W = JSON.parse(src.textContent).widget, n = W.T, mu = W.Rbar, s = W.s;
    var edges = W.counts.map(function (_, i) { return W.edges0 + i * W.bin; }).concat([W.edges0 + W.counts.length * W.bin]);
    var dens = W.counts.map(function (c) { return c / (n * W.bin * 100); });    /* probability per percentage point */

    /* SciPy's values for the initial state, compared once: a mismatch is shown, not hidden */
    var C = W.check, bad = [];
    function near(a, b, what) { if (!(Math.abs(a - b) <= 1e-6 * Math.abs(b))) bad.push(what); }
    near(normDays(-C.x, mu, s, n), C.normDays, "normal days");
    near(tDays(-C.x, W.ml.nu, W.ml.loc, W.ml.scale, n), C.mlDays, "Student-t days");
    near(tDays(-C.x, W.nuK, mu, s * Math.sqrt((W.nuK - 2) / W.nuK), n), C.kDays, "kurtosis-fit days");
    near(W.ml.loc + W.ml.scale * tq(0.01, W.ml.nu), C.mlQ01, "Student-t 1% quantile");
    C.tq01.forEach(function (p) { near(tq(0.01, p[0]), p[1], "t quantile at nu = " + p[0]); });

    host.innerHTML = '<div class="w-head"><span class="w-title">Student-t explorer: TAIEX histogram, normal and Student-t</span><span class="w-tag">Interactive</span></div>';
    var ctl = B.controls(host, [
      { type: "select", id: "td-fit", label: "Student-t", value: "ml",
        options: [["ml", "Maximum likelihood (ν = 3.065)"], ["match", "Data's mean and σ, choose ν"]] },
      { id: "td-nu", label: "Degrees of freedom ν", min: 2.05, max: 30, step: 0.01, value: 5.14,
        fmt: function (v) { return v.toFixed(2); } },
      { id: "td-x", label: "Loss level x", min: 1, max: 10, step: 0.1, value: 5,
        fmt: function (v) { return v.toFixed(1) + "%"; } },
      { type: "select", id: "td-ax", label: "Density axis", value: "log",
        options: [["log", "Log scale (shows the tails)"], ["lin", "Linear scale"]] }
    ], draw);
    var chart = document.createElement("div"); chart.className = "td-chart"; host.appendChild(chart);
    var out = document.createElement("div"); out.className = "readout"; out.setAttribute("aria-live", "polite"); host.appendChild(out);
    var note = document.createElement("p"); note.className = "w-note"; host.appendChild(note);
    note.textContent = "Histogram: TAIEX's " + n.toLocaleString("en-US") + " daily total returns (" + W.first + " to " + W.last +
      ") in 0.5-point bins, scaled to total area 1. Dashed: the normal with the data's mean and standard deviation. " +
      "Solid: the Student-t, either the maximum-likelihood fit or one with the data's mean and standard deviation and the " +
      "chosen ν. Shaded: R ≤ −x. Every fit is in-sample; TAIEX's days are counted with the guard R ≤ −x + 10⁻¹²." +
      (bad.length ? " Check against SciPy failed: " + bad.join(", ") + "." : "");
    if (bad.length && window.console) console.error("lm15 tdist: check against SciPy failed: " + bad.join(", "));
    var nuEl = host.querySelector("#td-nu"), nuV = host.querySelector("#td-nu-v");

    function actual(x) { var c = 0; for (var i = 0; i < W.lower.length; i++) if (W.lower[i] <= -x + 1e-12) c++; return c; }

    function draw(v) {
      var ml = v["td-fit"] === "ml", nu = ml ? W.ml.nu : v["td-nu"];
      var loc = ml ? W.ml.loc : mu, sc = ml ? W.ml.scale : s * Math.sqrt((nu - 2) / nu);
      var x = v["td-x"] / 100, log = v["td-ax"] === "log", base = log ? 1e-5 : 0;
      nuEl.disabled = ml;
      nuV.textContent = ml ? "3.065 (fitted)" : nu.toFixed(2);
      var lo = -0.11, hi = 0.11, mx = [], ny = [], ty = [];
      for (var j = 0; j <= 440; j++) {
        var xx = lo + (hi - lo) * j / 440, a = D.phi((xx - mu) / s) / (s * 100), b = D.tPdf((xx - loc) / sc, nu) / (sc * 100);
        mx.push(xx); ny.push(log && a < base ? null : a); ty.push(log && b < base ? null : b);
      }
      var hy = dens.map(function (d) { return d > 0 ? d : base; }).concat([base]);
      var tName = ml ? "Student-t, maximum likelihood, ν = 3.065" : "Student-t, same mean and σ, ν = " + nu.toFixed(2);
      var ch = B.lineChart(chart, {
        alt: "Histogram of TAIEX daily returns with the fitted normal and a Student-t density; the area at or below the loss level is shaded",
        height: 300,
        x: { type: "num", fmt: "pct2", tfmt: "pct0", label: "Daily total return", tipLabel: "R = ", min: lo, max: hi },
        y: log ? { type: "log", fmt: "sig3", tfmt: "num", label: "Density, probability per 1 pp of return (log scale)", min: base, max: 1, ticks: [1e-5, 1e-4, 1e-3, 0.01, 0.1, 1] }
               : { type: "lin", fmt: "sig3", tfmt: "n1", label: "Density, probability per 1 pp of return", min: 0 },
        series: [
          { name: "TAIEX daily returns (histogram)", color: "2", step: true, x: edges, y: hy },
          { name: "Normal, fitted", color: "1", dash: true, x: mx, y: ny },
          { name: tName, color: "3", x: mx, y: ty }],
        ann: [{ type: "vline", x: -x, label: "−x = " + fmt(-x, "pct1"), anchor: x > 6 / 100 ? "start" : "end", dash: true }]
      });
      /* shaded areas at or below -x, drawn under the lines and clipped like them */
      var NS = "http://www.w3.org/2000/svg", svg = ch.svg, sg = svg.querySelector("g.series");
      var clip = sg ? sg.getAttribute("clip-path") : null, top = log ? 1 : 1e9;
      var yb = function (q) { return ch.Y(Math.max(base, Math.min(q, top))); };
      function poly(pts, color, op) {
        var p = document.createElementNS(NS, "path");
        p.setAttribute("d", "M" + pts.map(function (q) { return ch.X(q[0]).toFixed(1) + "," + yb(q[1]).toFixed(1); }).join("L") + "Z");
        p.setAttribute("style", "fill:" + color + ";fill-opacity:" + op + ";stroke:none");
        if (clip) p.setAttribute("clip-path", clip);
        svg.insertBefore(p, sg);
      }
      var hp = [[edges[0], base]], k;
      for (k = 0; k < dens.length && edges[k] < -x; k++) {
        var dv = dens[k] > 0 ? dens[k] : base, right = Math.min(edges[k + 1], -x);
        hp.push([edges[k], dv], [right, dv]);
      }
      hp.push([Math.min(-x, edges[k]), base]);
      poly(hp, "var(--series-2)", 0.28);
      var tp = [[lo, base]];
      for (var q = 0; q <= 300; q++) { var xq = lo + (-x - lo) * q / 300; tp.push([xq, D.tPdf((xq - loc) / sc, nu) / (sc * 100)]); }
      tp.push([-x, base]);
      poly(tp, "var(--series-3)", 0.3);

      var eN = normDays(-x, mu, s, n), eT = tDays(-x, nu, loc, sc, n), a = actual(x);
      var sig = ml ? sc * Math.sqrt(nu / (nu - 2)) : s, q01 = loc + sc * tq(0.01, nu);
      out.innerHTML =
        "<div><span>Standardized loss level z = (−x − mean) / s</span><b>" + fmt((-x - mu) / s, "n3") + "</b></div>" +
        "<div><span>Normal: expected days with R ≤ −x</span><b>" + days(eN) + "</b></div>" +
        "<div><span>Student-t: expected days with R ≤ −x</span><b>" + days(eT) + "</b></div>" +
        "<div><span>TAIEX: days with R ≤ −x</span><b>" + a + "</b></div>" +
        "<div><span>TAIEX ÷ Student-t</span><b>" + (eT > 0 ? fmt(a / eT, "x2") : "—") + "</b></div>" +
        "<div><span>Student-t: σ · kurtosis</span><b>" + fmt(sig, "pct3") + " · " + (nu > 4 ? fmt(3 + 6 / (nu - 4), "n2") : "infinite") + "</b></div>" +
        "<div><span>Student-t: 1% quantile (TAIEX " + fmt(W.q01, "pct3") + ")</span><b>" + fmt(q01, "pct3") + "</b></div>";
    }
    host.__redraw = function () { ctl.fire(); };
    ctl.fire();
  };
  B.widgets.tdist.math = { tq: tq, tDays: tDays, normDays: normDays };
})();
