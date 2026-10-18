/* LM5 interactive figure: tail-probability explorer (normal model vs 0050 daily returns).
   Data: the "widget" block of the chart JSON lm05-tail, inlined in the page by the build
   (<script type="application/json" id="chart-lm05-tail">), written by data/lm05_charts.py. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt;

  /* complementary error function, fractional error < 1.2e-7 everywhere (Numerical Recipes, erfcc) */
  function erfc(x) {
    var z = Math.abs(x), t = 1 / (1 + 0.5 * z);
    var r = t * Math.exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + t * (-0.18628806 +
      t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))));
    return x >= 0 ? r : 2 - r;
  }
  function Phi(z) { return 0.5 * erfc(-z / Math.SQRT2); }
  function phi(z) { return Math.exp(-0.5 * z * z) / Math.sqrt(2 * Math.PI); }
  /* Student-t with 3 degrees of freedom: closed-form density and distribution function */
  function t3pdf(t) { return 6 * Math.sqrt(3) / (Math.PI * Math.pow(3 + t * t, 2)); }
  function t3cdf(t) { var u = t / Math.sqrt(3); return 0.5 + (u / (1 + u * u) + Math.atan(u)) / Math.PI; }

  var SUP = { "-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹" };
  function sci(v, d) {
    if (v == null || !isFinite(v)) return "—";
    if (v === 0) return "0";
    if (v >= 0.001 && v < 1e5) return v < 1 ? v.toPrecision(d || 3) : fmt(v, v < 10 ? "n2" : v < 1000 ? "n1" : "n0");
    var e = Math.floor(Math.log10(v)), m = v / Math.pow(10, e);
    if (+m.toFixed((d || 3) - 1) >= 10) { m /= 10; e += 1; }
    return m.toFixed((d || 3) - 1) + " × 10" + String(e).split("").map(function (c) { return SUP[c]; }).join("");
  }
  function years(v) {
    if (!isFinite(v)) return "never in the sample";
    if (v < 100) return v.toFixed(v < 10 ? 2 : 1) + " years";
    if (v < 1e6) return Math.round(v).toLocaleString("en-US") + " years";
    return sci(v, 2) + " years";
  }

  B.widgets.tails = function (host) {
    var src = document.getElementById("chart-lm05-tail");
    if (!src) { host.innerHTML = '<p class="w-note">The data for this figure are not on the page.</p>'; return; }
    var W = JSON.parse(src.textContent).widget;
    var n = W.n, mu = W.mu, s = W.s, perYear = n / W.years, nu = 3, sc = s * Math.sqrt((nu - 2) / nu);
    var edges = W.counts.map(function (_, i) { return W.edges0 + i * W.bin; }).concat([W.edges0 + W.counts.length * W.bin]);
    var dens = W.counts.map(function (c) { return c / (n * W.bin * 100); });        /* probability per percentage point */

    host.innerHTML = '<div class="w-head"><span class="w-title">Tail-probability explorer: model area versus 0050 data</span><span class="w-tag">Interactive</span></div>' +
      '<div class="controls">' +
      '<label for="tl-k">Threshold κ <span class="v" id="tl-k-v"></span><input type="range" id="tl-k" min="-0.10" max="-0.01" step="0.001" value="-0.05"></label>' +
      '<label for="tl-m">Model<select id="tl-m"><option value="n">Normal, fitted mean and σ</option><option value="t">Student-t, ν = 3, same σ (illustrative)</option></select></label>' +
      '<label for="tl-s">Density axis<select id="tl-s"><option value="log">Log scale (shows the tails)</option><option value="lin">Linear scale</option></select></label>' +
      '</div><div class="tl-chart"></div><div class="readout" aria-live="polite"></div>' +
      '<p class="w-note">Bars: histogram of 0050\'s ' + n.toLocaleString("en-US") + ' daily total returns (' + W.first + ' to ' + W.last +
      '), in 0.5-point bins, scaled so that their total area is 1. Curve: the model density with the same mean and standard deviation. ' +
      'Shaded: the area left of κ, which is the probability of a day at or below κ. On the log axis an empty bin drops to the floor.</p>';
    var sk = host.querySelector("#tl-k"), sm = host.querySelector("#tl-m"), ss = host.querySelector("#tl-s");
    var chart = host.querySelector(".tl-chart"), out = host.querySelector(".readout");

    function modelPdf(x, m) { return m === "t" ? t3pdf((x - mu) / sc) / (sc * 100) : phi((x - mu) / s) / (s * 100); }
    function modelCdf(x, m) { return m === "t" ? t3cdf((x - mu) / sc) : Phi((x - mu) / s); }
    function actual(k) { var c = 0; for (var i = 0; i < W.lower.length; i++) if (W.lower[i] <= k + 1e-12) c++; return c; }

    function draw() {
      var k = +sk.value, m = sm.value, log = ss.value === "log";
      host.querySelector("#tl-k-v").textContent = fmt(k, "pct1");
      var lo = -0.11, hi = 0.11, base = log ? 1e-5 : 0, top = log ? 1 : null;
      /* histogram outline as a step line; on the log axis empty bins sit on the floor */
      var hx = [edges[0]], hy = [base];
      for (var i = 0; i < dens.length; i++) {
        var d = dens[i] > 0 ? dens[i] : base;
        hx.push(edges[i], edges[i + 1]); hy.push(d, d);
      }
      hx.push(edges[edges.length - 1]); hy.push(base);
      var mx = [], my = [];
      for (var j = 0; j <= 440; j++) {
        var x = lo + (hi - lo) * j / 440, v = modelPdf(x, m);
        mx.push(x); my.push(log && v < base ? null : v);
      }
      var name = m === "t" ? "Student-t density, ν = 3 (illustrative)" : "Normal density, fitted";
      var spec = {
        alt: "Histogram of 0050 daily returns and a model density, with the tail left of the threshold shaded", height: 300,
        x: { type: "num", fmt: "pct1", label: "Daily total return", tipLabel: "R = ", min: lo, max: hi },
        y: log ? { type: "log", fmt: "dens", label: "Density, probability per 1 pp of return (log scale)", min: base, max: top, ticks: [1e-5, 1e-4, 1e-3, 0.01, 0.1, 1] }
               : { type: "lin", fmt: "n2", label: "Density, probability per 1 pp of return", min: 0 },
        series: [
          { name: "0050 daily returns (histogram)", color: "2", x: hx, y: hy },
          { name: name, color: m === "t" ? "3" : "1", dash: m === "t", x: mx, y: my }],
        ann: [{ type: "vline", x: k, label: "κ = " + fmt(k, "pct1"), anchor: k < -0.06 ? "start" : "end" }]
      };
      var ch = B.lineChart(chart, spec);
      /* shaded tail areas, drawn under the lines and clipped like them */
      var NS = "http://www.w3.org/2000/svg", svg = ch.svg, sg = svg.querySelector("g.series");
      var clip = sg ? sg.getAttribute("clip-path") : null;
      var yb = function (v) { return ch.Y(Math.max(log ? base : 0, Math.min(v, log ? top : 1e9))); };
      function poly(pts, color, op) {
        var p = document.createElementNS(NS, "path");
        p.setAttribute("d", "M" + pts.map(function (q) { return ch.X(q[0]).toFixed(1) + "," + yb(q[1]).toFixed(1); }).join("L") + "Z");
        p.setAttribute("style", "fill:" + color + ";fill-opacity:" + op + ";stroke:none");
        if (clip) p.setAttribute("clip-path", clip);
        svg.insertBefore(p, sg);
      }
      var hp = [[edges[0], base]];
      for (var b = 0; b < dens.length && edges[b] < k; b++) {
        var dv = dens[b] > 0 ? dens[b] : base, right = Math.min(edges[b + 1], k);
        hp.push([edges[b], dv], [right, dv]);
      }
      hp.push([Math.min(k, edges[b]), base]);
      poly(hp, "var(--series-2)", 0.28);
      var mp = [[lo, base]];
      for (var q = 0; q <= 400; q++) { var xx = lo + (k - lo) * q / 400; mp.push([xx, modelPdf(xx, m)]); }
      mp.push([k, base]);
      poly(mp, m === "t" ? "var(--series-3)" : "var(--series-1)", 0.32);

      var z = (k - mu) / s, p = modelCdf(k, m), e = n * p, a = actual(k);
      var ratio = e > 0 ? a / e : Infinity;
      out.innerHTML =
        "<div><span>Standardized threshold z</span><b>" + fmt(z, "n3") + "</b></div>" +
        "<div><span>Model Pr(R ≤ κ): shaded area</span><b>" + sci(p) + "</b></div>" +
        "<div><span>Model: expected days of " + n.toLocaleString("en-US") + "</span><b>" + sci(e) + "</b></div>" +
        "<div><span>0050: actual days</span><b>" + a + "</b></div>" +
        "<div><span>Actual ÷ expected</span><b" + (ratio > 3 || ratio < 1 / 3 ? ' class="bad"' : "") + ">" +
          (a === 0 ? "—" : ratio < 1000 ? fmt(ratio, ratio < 10 ? "x2" : "x0") : sci(ratio, 2) + "×") + "</b></div>" +
        "<div><span>Model: one such day every</span><b>" + years(1 / (p * perYear)) + "</b></div>" +
        "<div><span>0050: one such day every</span><b>" + (a ? years(W.years / a) : "never in the sample") + "</b></div>";
    }
    [sk, sm, ss].forEach(function (c) { c.addEventListener("input", draw); });
    host.__redraw = draw; draw();
  };
})();
