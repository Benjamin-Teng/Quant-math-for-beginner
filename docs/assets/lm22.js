/* LM22 interactive figure: block-bootstrap explorer.
   Data: the "widget" block of the chart JSON lm22-widget, inlined in the page by the build
   (<script type="application/json" id="chart-lm22-widget">), written by data/lm22_charts.py from experiment 24: one NumPy
   generator, default_rng([24, 20261011]), drew three replicates of 1,000 resamples of TR23's 5,849 daily returns at
   each mean block length 1, 2, 3, 5, 10, 20, 50, 100, 145, 200, 400, in that order (length 1 is iid days, the others
   the stationary bootstrap). For each statistic, length and replicate it holds the counts on 50 fixed bins, the
   standard deviation of the 1,000 values (divisor 1,000), their mean and the percentile ends (the 25th and 975th
   order statistics). The widget draws nothing at random: it shows these histograms and computes the basic interval
   (2 x estimate minus the ends) and the normal interval (estimate +- PhiInv(0.975) x standard error). The text quotes
   no widget value. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt, D = B.dist;
  var TICKS = { SR: "n1", Kelly: "n0", vol: "pct0", acf: "n2", VR20: "n2" };

  B.widgets.blockboot = function (host) {
    var src = document.getElementById("chart-lm22-widget");
    if (!src) { host.innerHTML = '<p class="w-note">The data for this figure are not on the page.</p>'; return; }
    var W = JSON.parse(src.textContent).widget, byKey = {}, rep = W.init.rep, z = D.PhiInv(0.975);
    W.stats.forEach(function (s) { byKey[s.key] = s; });

    host.innerHTML = '<div class="w-head"><span class="w-title">Block-bootstrap explorer</span>' +
      '<span class="w-tag">Interactive</span></div>';
    var ctl = B.controls(host, [
      { type: "select", id: "bb-stat", key: "stat", label: "Statistic",
        options: W.stats.map(function (s) { return [s.key, s.name]; }), value: W.init.stat },
      { id: "bb-ell", key: "li", label: "Mean block length", min: 0, max: W.ells.length - 1, step: 1,
        value: W.ells.indexOf(W.init.ell),
        fmt: function (v) { var e = W.ells[v]; return e === 1 ? "1 day (iid days)" : e + " days"; } },
      { type: "button", id: "bb-seed", label: "Next replicate" }
    ], draw);
    var chart = document.createElement("div"), out = document.createElement("div"), note = document.createElement("p");
    out.className = "readout"; out.setAttribute("aria-live", "polite"); note.className = "w-note";
    host.appendChild(chart); host.appendChild(out); host.appendChild(note);
    note.textContent = "Each histogram holds " + W.B.toLocaleString("en-US") + " resamples of TR23's daily returns, " +
      "drawn in NumPy by one generator, " + W.seed + " (experiment 24), " + W.reps + " replicates at each length; " +
      "length 1 resamples single days, the others use the stationary bootstrap. Nothing is drawn in the browser. " +
      "Solid line: the estimate on TR23; dashed lines: the percentile ends. The replicates differ by Monte Carlo " +
      "error, larger than in the text's 10,000 resamples. In-sample; the text quotes no value from this figure.";

    function draw(v, id) {
      if (id === "bb-seed") rep = (rep + 1) % W.reps;
      var s = byKey[v.stat], li = Math.round(v.li), ell = W.ells[li], d = W.data[s.key][li][rep];
      var edges = [], ys = [];
      for (var i = 0; i <= W.nbins; i++) edges.push(s.lo + i * s.width);
      d.c.forEach(function (c) { ys.push(c / W.B); });
      var scheme = ell === 1 ? "iid days" : "stationary blocks of mean length " + ell;
      B.chart(chart, {
        alt: "Histogram of " + W.B + " resampled values of the " + s.name.toLowerCase() + " of TR23, " + scheme +
          ", replicate " + (rep + 1) + ", with the estimate and the percentile ends",
        height: 280,
        x: { type: "num", fmt: s.fmt, tfmt: TICKS[s.key], tipLabel: "from ", label: s.name,
             min: edges[0], max: edges[edges.length - 1] },
        y: { type: "lin", fmt: "pct1", tfmt: "pct0", label: "Share of the " + W.B.toLocaleString("en-US") +
             " resamples per bin", min: 0 },
        series: [{ name: "resamples", color: ell === 1 ? "1" : "2", step: true, x: edges, y: ys }],
        ann: [{ type: "vline", x: s.est, label: "estimate" },
              { type: "vline", x: d.lo, dash: true }, { type: "vline", x: d.hi, dash: true }]
      });
      var f = function (x) { return fmt(x, s.fmt); };
      // a volatility's standard error is in percentage points, as the text writes it
      var fse = s.key === "vol" ? function (x) { return fmt(100 * x, "n2") + " points"; } : f;
      out.innerHTML =
        "<div><span>Estimate on TR23</span><b>" + f(s.est) + "</b></div>" +
        "<div><span>Bootstrap standard error (divisor " + W.B.toLocaleString("en-US") + ")</span><b>" + fse(d.se) + "</b></div>" +
        "<div><span>95% percentile interval</span><b>" + f(d.lo) + " to " + f(d.hi) + "</b></div>" +
        "<div><span>95% basic interval</span><b>" + f(2 * s.est - d.hi) + " to " + f(2 * s.est - d.lo) + "</b></div>" +
        "<div><span>Normal interval, estimate ± " + z.toFixed(2) + " standard errors</span><b>" + f(s.est - z * d.se) +
          " to " + f(s.est + z * d.se) + "</b></div>" +
        "<div><span>Mean of the resamples</span><b>" + f(d.mean) + "</b></div>" +
        "<div><span>Scheme · replicate</span><b>" + scheme + " · " + (rep + 1) + " of " + W.reps + "</b></div>";
    }
    host.__redraw = function () { draw(ctl.values(), null); };
    ctl.fire();
  };
})();
