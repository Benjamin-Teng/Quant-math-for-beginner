/* LM18 interactive figure: three estimators of the tail probability Pr(Z <= -k) on one stream of draws.
   Each run draws 1,000,000 uniforms from Book.rng(run) (a draw of exactly 0 is redrawn) and turns them into standard
   normal draws Z = Book.dist.PhiInv(U), cached for the current run. Plain sampling averages 1{Z <= -k}; antithetic
   sampling averages (1{Z <= -k} + 1{-Z <= -k}) / 2 over the first n/2 draws, so n evaluations in n/2 pairs; importance
   sampling, (18.7) with a = k, averages 1{Z <= 0} exp(kZ - k^2/2), the shifted draw Z - k in the tail weighted back.
   The chart shows each running estimate divided by the exact Phi(-k) at 41 log-spaced checkpoints up to n (values
   above 3 are drawn at 3); the readouts describe the selected method at n. The widget's generator is not NumPy's,
   and the text quotes no widget value. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt, D = B.dist;
  var NMAX = 1000000, YMAX = 3;
  var KS = [["1", "1"], ["2", "2"], ["3", "3"], ["4.1074386", "4.1074386 (LM5's −5% day)"], ["5", "5"]];
  var METHODS = [["plain", "Plain"], ["anti", "Antithetic"], ["is", "Importance sampling, a = k"]];
  var NAMES = { plain: "Plain", anti: "Antithetic", is: "Importance sampling" };

  // checkpoints: 41 on the chart (log10 n = 2, 2.1, ..., 6) and the slider's quarter decades
  var CHART = [], CPS = [];
  (function () {
    var seen = {}, i, n;
    for (i = 0; i <= 40; i++) { n = Math.round(Math.pow(10, 2 + i / 10)); CHART.push(n); seen[n] = 1; }
    for (i = 0; i <= 16; i++) { n = Math.round(Math.pow(10, 2 + i / 4)); seen[n] = 1; }
    for (n in seen) CPS.push(+n);
    CPS.sort(function (a, b) { return a - b; });
  })();

  var zRun = null, zData = null, statKey = null, stat = null;
  function stream(run) {
    if (zRun === run) return zData;
    var g = B.rng(run), z = new Float64Array(NMAX), u;
    for (var i = 0; i < NMAX; i++) {
      do u = g.uniform(); while (u === 0);
      z[i] = D.PhiInv(u);
    }
    zRun = run; zData = z; statKey = null;
    return z;
  }

  // running sums at every checkpoint: plain and importance sampling over n draws, antithetic over floor(n/2) pairs
  function stats(run, k) {
    var key = run + "|" + k;
    if (statKey === key) return stat;
    var z = stream(run), w = Math.exp(-k * k / 2), half = NMAX / 2;
    var sp = 0, si = 0, si2 = 0, ti = 0, sa = 0, sa2 = 0, ta = 0, ci = 0, ca = 0;
    var res = { plain: {}, is: {}, anti: {} };
    for (var i = 0; i < NMAX; i++) {
      var x = z[i];
      if (x <= -k) sp++;
      if (x <= 0) { var y = Math.exp(k * x) * w; si += y; si2 += y * y; ti++; }
      if (i < half) {
        var hits = (x <= -k ? 1 : 0) + (x >= k ? 1 : 0);
        sa += hits / 2; sa2 += hits * hits / 4; ta += hits;
        while (ca < CPS.length && Math.floor(CPS[ca] / 2) === i + 1) {
          res.anti[CPS[ca]] = { n: i + 1, s: sa, s2: sa2, tail: ta }; ca++;
        }
      }
      while (ci < CPS.length && CPS[ci] === i + 1) {
        res.plain[CPS[ci]] = { n: i + 1, s: sp, s2: sp, tail: sp };
        res.is[CPS[ci]] = { n: i + 1, s: si, s2: si2, tail: ti };
        ci++;
      }
    }
    statKey = key; stat = res;
    return res;
  }

  function est(r) {   // mean and standard error (divisor n) of the averaged values
    var mean = r.s / r.n, v = Math.max(0, r.s2 / r.n - mean * mean);
    return { mean: mean, se: Math.sqrt(v / r.n) };
  }

  B.widgets.mcTail = function (host) {
    host.innerHTML = '<div class="w-head"><span class="w-title">Three ways to estimate a tail probability</span>' +
      '<span class="w-tag">Interactive</span></div>';
    var chartBox = document.createElement("div"), out = document.createElement("div"), note = document.createElement("p");
    out.className = "readout"; out.setAttribute("aria-live", "polite"); note.className = "w-note";
    note.textContent = "Each run draws 1,000,000 uniform numbers from the book's seeded generator (seed = run) and " +
      "turns them into standard normal draws Z. All three methods use the same draws: Z for plain sampling, Z and −Z " +
      "for antithetic pairs (n/2 pairs), and Z − k weighted by (18.7) for importance sampling. Values above 3 times " +
      "the exact value are drawn at 3. The widget's generator is not NumPy's; the text quotes no widget value.";

    function draw(vals) {
      var k = +vals.k, run = vals.run, n = Math.round(Math.pow(10, vals.n)), meth = vals.method;
      var S = stats(run, k), p = D.Phi(-k), clipped = false;
      var shown = CHART.filter(function (c) { return c <= n; });
      var series = ["plain", "anti", "is"].map(function (mk, j) {
        return {
          name: NAMES[mk], color: String(j + 1), width: mk === meth ? 2.6 : 1.3,
          x: shown.map(function (c) { return Math.log(c) / Math.LN10; }),
          y: shown.map(function (c) {
            var v = est(S[mk][c]).mean / p;
            if (v > YMAX) { clipped = true; return YMAX; }
            return v;
          })
        };
      });
      B.chart(chartBox, {
        alt: "Running estimates of the tail probability divided by the exact value, for plain, antithetic and " +
          "importance sampling, against the number of draws on a log scale",
        height: 300,
        x: { type: "num", fmt: "n2", tipLabel: "log10 n = ", label: "Draws n (log scale)", min: 2, max: 6,
             ticks: [2, 3, 4, 5, 6], tickLabels: ["100", "1,000", "10,000", "100,000", "1,000,000"] },
        y: { type: "lin", fmt: "n3", tfmt: "n1", label: "Estimate ÷ exact value", min: 0, max: YMAX,
             ticks: [0, 0.5, 1, 1.5, 2, 2.5, 3] },
        series: series,
        ann: [{ type: "hline", y: 1, dash: true, label: "exact" }]
      });
      var r = S[meth][n], e = est(r), covers = Math.abs(e.mean - p) <= 1.96 * e.se;
      var rho = -p / (1 - p), varIs = Math.exp(k * k) * D.Phi(-2 * k) - p * p;
      var equiv = meth === "plain" ? n : meth === "anti" ? n / (1 + rho) : n * p * (1 - p) / varIs;
      var tailLabel = meth === "plain" ? "Draws in the tail" : meth === "anti" ? "Hits in the pairs" : "Shifted draws in the tail";
      out.innerHTML =
        "<div><span>" + NAMES[meth] + " estimate ± standard error</span><b>" + fmt(e.mean, "sci2") + " ± " + fmt(e.se, "sci1") + "</b></div>" +
        "<div><span>Exact Φ(−k)</span><b>" + fmt(p, "sci3") + "</b></div>" +
        "<div><span>Estimate ÷ exact</span><b>" + fmt(e.mean / p, "n3") + (clipped ? " (chart cut at 3)" : "") + "</b></div>" +
        "<div><span>95% Monte Carlo interval</span><b>" + (covers ? "covers the exact value" : "misses the exact value") + "</b></div>" +
        "<div><span>" + tailLabel + "</span><b>" + fmt(r.tail, "n0") + "</b></div>" +
        "<div><span>Equivalent plain draws</span><b>" + fmt(equiv, "sig3") + "</b></div>";
    }

    var ctl = B.controls(host, [
      { type: "select", id: "mc-k", key: "k", label: "Threshold k", options: KS, value: "4.1074386" },
      { id: "mc-n", key: "n", label: "Draws n", min: 2, max: 6, step: 0.25, value: 6,
        fmt: function (v) { return fmt(Math.round(Math.pow(10, v)), "n0"); } },
      { id: "mc-run", key: "run", label: "Run (seed)", min: 1, max: 5, step: 1, value: 1 },
      { type: "select", id: "mc-m", key: "method", label: "Method", options: METHODS, value: "is" }
    ], draw);
    host.appendChild(chartBox); host.appendChild(out); host.appendChild(note);
    host.__redraw = ctl.fire;
    ctl.fire();
  };
})();
