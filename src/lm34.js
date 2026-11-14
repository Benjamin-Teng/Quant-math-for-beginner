/* LM34 interactive figure: how often does the best backtest disappoint? CSCV on simulated strategies.
   Data: the "widget" block of the chart JSON lm34-pboSim, inlined in the page by the build
   (<script type="application/json" id="chart-lm34-pboSim">), written by data/lm34_charts.py: experiment 3's mean PBO
   of 40 panels for each state (n strategies = 2, 5, 10, 20, 60, 100; strategy 1's true annual Sharpe ratio 0, 0.5, 1,
   1.5, 2), their largest standard error, the number of days (1,851) and blocks (16), A_w, and a synthetic test
   matrix with its Python PBO.
   Model only: the widget draws its own panel with Book.rng(seed), days in rows: each return is 1% times a standard
   normal, plus strategy 1's drift SR / sqrt(A_w) x 1%. These are not NumPy's draws, so a panel's PBO differs from
   experiment 3's panels; the readout gives experiment 3's 40-panel mean for the chosen state.
   CSCV as the module's (34.4): 16 equal blocks, the earliest rows that do not fill a block dropped; every choice of 8
   blocks in lexicographic order (as itertools.combinations); the in-sample best by the Sharpe ratio of the in-sample
   days (population moments; the first on a tie); its out-of-sample rank j among the n (1 = the worst);
   logit ln(w / (1 - w)), w = j / (n + 1); PBO the share of logits at or below 0 (guard 1e-12).
   data/lm34_charts.py runs Book.widgets.pboSim.math.cscv in Node on the test matrix against Python's cscv(). */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt, EDGES = [];
  for (var e = -4.5; e <= 4.5 + 1e-9; e += 0.5) EDGES.push(e);

  function combos(S) {            // every S/2-subset of 0..S-1, in lexicographic order
    var out = [], c = [];
    (function rec(start) {
      if (c.length === S / 2) { out.push(c.slice()); return; }
      for (var i = start; i < S; i++) { c.push(i); rec(i + 1); c.pop(); }
    })(0);
    return out;
  }
  function cscv(x, T, n, S) {     // x: T rows of n returns, row-major; returns the logits of the C(S, S/2) splits
    var m = Math.floor(T / S), drop = T - m * S, h = m * S / 2, s1 = new Float64Array(S * n), s2 = new Float64Array(S * n);
    var b, r, k, v, C = combos(S), out = new Float64Array(C.length), t1 = new Float64Array(n), t2 = new Float64Array(n);
    for (b = 0; b < S; b++) for (r = 0; r < m; r++) for (k = 0; k < n; k++) {
      v = x[(drop + b * m + r) * n + k]; s1[b * n + k] += v; s2[b * n + k] += v * v;
    }
    for (k = 0; k < n; k++) for (b = 0; b < S; b++) { t1[k] += s1[b * n + k]; t2[k] += s2[b * n + k]; }
    var i1 = new Float64Array(n), i2 = new Float64Array(n), so = new Float64Array(n);
    C.forEach(function (c, ci) {
      var best = 0, bestSr = -Infinity, j = 1, a, mu;
      for (k = 0; k < n; k++) {
        i1[k] = 0; i2[k] = 0;
        for (a = 0; a < c.length; a++) { i1[k] += s1[c[a] * n + k]; i2[k] += s2[c[a] * n + k]; }
        mu = i1[k] / h; v = mu / Math.sqrt(i2[k] / h - mu * mu);
        if (v > bestSr) { bestSr = v; best = k; }
        mu = (t1[k] - i1[k]) / h; so[k] = mu / Math.sqrt((t2[k] - i2[k]) / h - mu * mu);
      }
      for (k = 0; k < n; k++) if (so[k] < so[best]) j++;
      v = j / (n + 1); out[ci] = Math.log(v / (1 - v));
    });
    return out;
  }
  function pbo(lg) { var c = 0; for (var i = 0; i < lg.length; i++) if (lg[i] <= 1e-12) c++; return c / lg.length; }
  function panel(n, sr, seed, T, Aw) {   // one simulated panel and its CSCV
    var g = B.rng(seed), x = new Float64Array(T * n), drift = sr / Math.sqrt(Aw) * 0.01;
    for (var t = 0; t < T; t++) for (var k = 0; k < n; k++) x[t * n + k] = 0.01 * g.normal() + (k === 0 ? drift : 0);
    var lg = cscv(x, T, n, 16);
    return { logits: lg, pbo: pbo(lg) };
  }
  function hist(lg) {
    var h = EDGES.slice(1).map(function () { return 0; });
    for (var i = 0; i < lg.length; i++) {
      var v = Math.min(Math.max(lg[i], -4.5 + 1e-9), 4.5 - 1e-9);
      h[Math.min(h.length - 1, Math.floor((v + 4.5) / 0.5))]++;
    }
    return h;
  }

  B.widgets.pboSim = function (host) {
    var src = document.getElementById("chart-lm34-pboSim");
    if (!src) { host.innerHTML = '<p class="w-note">The data for this figure are not on the page.</p>'; return; }
    var W = JSON.parse(src.textContent).widget, seed = 1;
    host.innerHTML = '<div class="w-head"><span class="w-title">How often does the best backtest disappoint?</span>' +
      '<span class="w-tag">Interactive</span></div>';
    var ctl = B.controls(host, [
      { id: "pbo-n", key: "n", type: "select", label: "Strategies n", value: "60",
        options: W.n.map(function (v) { return [String(v), String(v)]; }) },
      { id: "pbo-sr", key: "sr", type: "select", label: "True Sharpe ratio of strategy 1", value: "0",
        options: W.sr.map(function (v) { return [String(v), String(v)]; }) },
      { id: "pbo-new", type: "button", label: "New draw" }
    ], draw);
    var chart = document.createElement("div"), out = document.createElement("div"), note = document.createElement("p");
    out.className = "readout"; out.setAttribute("aria-live", "polite"); note.className = "w-note";
    note.innerHTML = "Model: " + fmt(W.days, "n0") + " days of n strategies with daily SD 1% and zero true Sharpe ratio, except " +
      "strategy 1, drawn with the page's own generator (Book.rng, starting at seed 1); CSCV with " + W.blocks +
      " blocks as (34.4). The mean PBO of " + W.panels + " panels comes from the module's experiment 3 " +
      "(largest SE " + fmt(W.seMax, "n3") + "). For odd n the middle rank has a logit of exactly 0, which PBO " +
      "counts, so with no skill the expected PBO is (n + 1)/(2n): 0.6 at n = 5.";
    host.appendChild(chart); host.appendChild(out); host.appendChild(note);

    function draw(v, id) {
      if (id === "pbo-new") seed += 1;
      var n = +v.n, sr = +v.sr, p = panel(n, sr, seed, W.days, W.Aw), h = hist(p.logits);
      var mean = W.means[String(n)][W.sr.indexOf(sr)];
      B.chart(chart, {
        type: "bar", valueLabels: false, height: 260,
        alt: "Histogram of this panel's 12,870 CSCV logits; logits at or below 0 count toward PBO",
        categories: EDGES.slice(1).map(function (e) { return fmt(e - 0.25, "n2"); }),
        x: { label: "Logit, bin centre" }, y: { fmt: "n0", tfmt: "n0", label: "Splits", min: 0 },
        series: [{ name: "this panel", color: "1", values: h, fmt: "n0" }]
      });
      function item(lbl, val) { return "<div><span>" + lbl + "</span><b>" + val + "</b></div>"; }
      out.innerHTML = item("This panel's PBO", fmt(p.pbo, "n3")) +
        item("Mean PBO of " + W.panels + " panels (experiment 3)", fmt(mean, "n2")) +
        item("Strategies; strategy 1's true Sharpe ratio", n + "; " + sr) + item("Seed", String(seed));
    }
    host.__redraw = function () { draw(ctl.values(), null); };
    ctl.fire();
  };
  B.widgets.pboSim.math = { combos: combos, cscv: cscv, pbo: pbo, panel: panel, hist: hist };
})();
