/* LM20 interactive figure: how often a 95% interval covers the mean, in simulated samples.
   Data: the "widget" block of the chart JSON lm20-coverage, inlined in the page by the build
   (<script type="application/json" id="chart-lm20-coverage">), written by data/lm20_charts.py: the 97.5% quantiles of
   t_{T-1} for T = 2 ... 250 from SciPy (tq[T - 2]), TR23's mean daily return Rbar and its standard deviation s
   (divisor T), the number of samples per draw (n = 1,000), the number of intervals drawn (100) and the initial state.
   Each draw creates Book.rng(seed) once (seed 1 at first, plus one per click of "Draw again") and draws n samples of
   T days, in order: a normal day is Rbar + s Z; a Student-t day with 3 degrees of freedom is
   Rbar + s Z0 / sqrt(Z1^2 + Z2^2 + Z3^2), which has variance s^2 by (15.10). The intervals are
   mean +- 1.96 s / sqrt(T) (s with divisor T) and mean +- tq s_u / sqrt(T) (s_u with divisor T - 1). Coverage is the
   share of the n intervals that contain Rbar, with Monte Carlo standard error sqrt(c (1 - c) / n). For the normal model
   the exact coverage of the first interval is 2 F_{t_{T-1}}(1.96 sqrt((T - 1) / T)) - 1 (Book.dist.tCdf). The widget's
   generator is not NumPy's, and the text quotes no widget number. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt, D = B.dist;

  function pct(v, d) { return (100 * v).toFixed(d) + "%"; }

  B.widgets.coverage = function (host) {
    var src = document.getElementById("chart-lm20-coverage");
    if (!src) { host.innerHTML = '<p class="w-note">The data for this figure are not on the page.</p>'; return; }
    var W = JSON.parse(src.textContent).widget, Rb = W.Rbar, s = W.s, N = W.n, SHOW = W.shown;
    var seed = W.init.seed;

    host.innerHTML = '<div class="w-head"><span class="w-title">How often does a 95% interval cover the mean?</span>' +
      '<span class="w-tag">Interactive</span></div>';
    var chartBox = document.createElement("div"), out = document.createElement("div"), note = document.createElement("p");
    out.className = "readout"; out.setAttribute("aria-live", "polite"); note.className = "w-note";
    note.textContent = "A model, not data: each draw makes " + N.toLocaleString("en-US") + " samples of T independent " +
      "days with TAIEX's mean, " + pct(Rb, 4) + " a day, and standard deviation, " + pct(s, 4) + ", either normal or " +
      "Student-t with 3 degrees of freedom (four normal draws per day, scaled to the same variance). The chart shows " +
      "the first " + SHOW + " intervals of the chosen kind around their sample means. The generator is the book's " +
      "seeded one, not NumPy's, so its numbers differ from the module's table; the text quotes none of them.";

    function simulate(model, T, sd) {
      var g = B.rng(sd), q = W.tq[T - 2], res = { hz: 0, ht: 0, rows: [] };
      for (var i = 0; i < N; i++) {
        var sum = 0, sum2 = 0;
        for (var t = 0; t < T; t++) {
          var x;
          if (model === "t3") {
            var z0 = g.normal(), z1 = g.normal(), z2 = g.normal(), z3 = g.normal();
            x = Rb + s * z0 / Math.sqrt(z1 * z1 + z2 * z2 + z3 * z3);
          } else {
            x = Rb + s * g.normal();
          }
          sum += x; sum2 += x * x;
        }
        var m = sum / T, ss = Math.max(0, sum2 - T * m * m);
        var sT = Math.sqrt(ss / T), su = Math.sqrt(ss / (T - 1));
        var hz = 1.96 * sT / Math.sqrt(T), ht = q * su / Math.sqrt(T);
        var cz = Math.abs(m - Rb) <= hz, ct = Math.abs(m - Rb) <= ht;
        if (cz) res.hz++;
        if (ct) res.ht++;
        if (i < SHOW) res.rows.push({ m: m, hz: hz, ht: ht, cz: cz, ct: ct });
      }
      return res;
    }

    function draw(v) {
      var model = v.model, T = Math.round(v.T), useT = v.interval === "t";
      var r = simulate(model, T, seed), q = W.tq[T - 2];
      var inX = [], inY = [], outX = [], outY = [], lines = [];
      r.rows.forEach(function (row, i) {
        var h = useT ? row.ht : row.hz, ok = useT ? row.ct : row.cz;
        (ok ? inX : outX).push(i + 1);
        (ok ? inY : outY).push(row.m);
        lines.push({ from: [i + 1, row.m - h], to: [i + 1, row.m + h], color: ok ? "1" : "2", width: ok ? 1.2 : 2 });
      });
      lines.push({ from: [0, Rb], to: [1, Rb], extend: true, dash: true, color: "var(--ink)",
                   label: "true mean " + pct(Rb, 4) });
      B.chart(chartBox, {
        type: "scatter", height: 320, legend: true,
        alt: "The first " + SHOW + " of " + N + " simulated 95% intervals for the mean daily return, " +
          (model === "t3" ? "Student-t" : "normal") + " model, " + T + " days per sample, " +
          (useT ? "t quantile with s_u" : "1.96 with s") + "; intervals that miss the true mean are marked",
        x: { label: "Sample (the first " + SHOW + " of " + N.toLocaleString("en-US") + ")", fmt: "n0", min: 0,
             max: SHOW + 1, ticks: [1, 25, 50, 75, 100], name: "sample" },
        y: { label: "Mean daily return and its 95% interval", fmt: "pct3", tfmt: "pct1", name: "sample mean" },
        series: [
          { name: "Interval covers the mean", color: "1", x: inX, y: inY, r: 2.4 },
          { name: "Interval misses the mean", color: "2", x: outX, y: outY, r: 3.2 }
        ],
        lines: lines
      });
      var cz = r.hz / N, ct = r.ht / N;
      function se(c) { return Math.sqrt(c * (1 - c) / N); }
      var exact = model === "normal" ? 2 * D.tCdf(1.96 * Math.sqrt((T - 1) / T), T - 1) - 1 : null;
      out.innerHTML =
        "<div><span>Coverage, 1.96 with s (divisor T)</span><b>" + pct(cz, 1) + " ± " + (100 * se(cz)).toFixed(1) +
          "</b></div>" +
        "<div><span>Coverage, t quantile with s<sub>u</sub></span><b>" + pct(ct, 1) + " ± " +
          (100 * se(ct)).toFixed(1) + "</b></div>" +
        "<div><span>t quantile, " + (T - 1) + " degrees of freedom</span><b>" + fmt(q, "n4") + "</b></div>" +
        "<div><span>Exact coverage of 1.96 with s</span><b>" +
          (exact === null ? "no formula (Student-t days)" : pct(exact, 1)) + "</b></div>" +
        "<div><span>Samples · seed</span><b>" + N.toLocaleString("en-US") + " · " + seed + "</b></div>";
    }

    var ctl = B.controls(host, [
      { type: "select", id: "cv-model", key: "model", label: "Model",
        options: [["normal", "Normal"], ["t3", "Student-t, 3 degrees of freedom"]], value: W.init.model },
      { id: "cv-T", key: "T", label: "Days per sample, T", min: W.Tmin, max: W.Tmax, step: 1, value: W.init.T,
        fmt: "n0" },
      { type: "select", id: "cv-int", key: "interval", label: "Interval",
        options: [["z", "1.96 with s (divisor T)"], ["t", "t quantile with s_u"]], value: W.init.interval },
      { type: "button", id: "cv-draw", label: "Draw again" }
    ], function (v, id) {
      if (id === "cv-draw") seed += 1;
      draw(v);
    });
    host.appendChild(chartBox); host.appendChild(out); host.appendChild(note);
    host.__redraw = function () { draw(ctl.values()); };
    ctl.fire();
  };
})();
