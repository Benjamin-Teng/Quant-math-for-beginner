/* LM25 interactive figure "ar1noise": a mean-reverting basis with one-day noise.
   Model, (25.9) of the module: b_t = x_t + u_t, with x_t - mean = phi1 (x_{t-1} - mean) + zeta_t, zeta_t normal with
   standard deviation sigma_zeta, u_t normal with standard deviation sigma_u, all independent, t = 1..n (n = 246).
   Fixed: sigma_zeta, the mean and n, from the "widget" block of the chart JSON lm25-ar1noise (inlined in the page by
   the build as <script type="application/json" id="chart-lm25-ar1noise">, written by data/lm25_charts.py from the
   ARMA(1,1) fit of TX23's log basis); the 5% point is MacKinnon's for n - 1 = 245 changes (statsmodels). The start
   x_1 is drawn from the stationary law, standard deviation sigma_zeta / sqrt(1 - phi1^2), when phi1 < 1 and set at
   the mean when phi1 = 1. Draws come from Book.rng(path).normal(): n for x (the start, then the innovations), then n
   for u. For one path the draws stay the same whatever phi1 and sigma_u, so a slider changes the model, not the luck.
   Readouts: the model half-life (25.2); phi1 of an AR(1) fitted to the observed path by OLS (b_t on a constant and
   b_{t-1}) and its half-life; the path's DF t-stat (25.7), constant and no lags, classical standard error, against
   the 5% point. Book.rng is not NumPy's generator, and the text quotes no simulated widget value. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt;

  function halfLife(phi) { return Math.log(0.5) / Math.log(phi); }
  function hlText(phi) {
    if (!(phi > 0)) return "none: no memory";
    if (phi >= 1) return "none: a random walk";
    return fmt(halfLife(phi), "n2") + " sessions";
  }

  // OLS of b_t on a constant and b_{t-1}, t = 2..n: phi_hat, and the DF t-stat of delta = phi_hat - 1
  function fitAR1(bv) {
    var n = bv.length - 1, mx = 0, my = 0, i;
    for (i = 0; i < n; i++) { mx += bv[i]; my += bv[i + 1]; }
    mx /= n; my /= n;
    var sxx = 0, sxy = 0;
    for (i = 0; i < n; i++) { sxx += (bv[i] - mx) * (bv[i] - mx); sxy += (bv[i] - mx) * (bv[i + 1] - my); }
    var phi = sxy / sxx, c = my - phi * mx, rss = 0;
    for (i = 0; i < n; i++) { var e = bv[i + 1] - c - phi * bv[i]; rss += e * e; }
    var se = Math.sqrt(rss / (n - 2) / sxx);
    return { phi: phi, t: (phi - 1) / se };
  }

  B.widgets.ar1noise = function (host) {
    var src = document.getElementById("chart-lm25-ar1noise");
    if (!src) { host.innerHTML = '<p class="w-note">The data for this figure are not on the page.</p>'; return; }
    var W = JSON.parse(src.textContent).widget, n = W.n, mean = W.mean, sz = W.sigmaZeta, crit = W.crit5;
    var path = W.seed0, draws = null;

    function stream(seed) {   // n normals for x, then n for u, cached for the current path
      if (draws && draws.seed === seed) return draws;
      var g = B.rng(seed), zx = new Float64Array(n), zu = new Float64Array(n), i;
      for (i = 0; i < n; i++) zx[i] = g.normal();
      for (i = 0; i < n; i++) zu[i] = g.normal();
      draws = { seed: seed, zx: zx, zu: zu };
      return draws;
    }

    host.innerHTML = '<div class="w-head"><span class="w-title">A mean-reverting basis with one-day noise</span>' +
      '<span class="w-tag">Interactive</span></div>';
    var chart = document.createElement("div"), out = document.createElement("div"), note = document.createElement("p");
    out.className = "readout"; out.setAttribute("aria-live", "polite"); note.className = "w-note";
    note.textContent = "Model, not market data: a persistent AR(1) with innovations of " + fmt(sz, "n1") +
      " bp around a mean of " + fmt(mean, "n1") + " bp (dashed), plus independent one-day noise, over " + n +
      " sessions. Normal draws from the book's seeded generator (seed = path number); " +
      "a new path changes the draws, the sliders change only the model. The DF t-stat uses a constant and no lags, " +
      "and its 5% point is MacKinnon's for " + (n - 1) + " changes, " + fmt(crit, "n2") + ".";

    function draw(v, id) {
      if (id === "an-new") path += 1;
      var phi = v.phi, su = v.su, d = stream(path), xs = [], xv = [], bv = [], i;
      var sx = phi < 1 ? sz / Math.sqrt(1 - phi * phi) : 0;
      var x = mean + sx * d.zx[0];
      for (i = 0; i < n; i++) {
        if (i > 0) x = mean + phi * (x - mean) + sz * d.zx[i];
        xs.push(i + 1); xv.push(x); bv.push(x + su * d.zu[i]);
      }
      var f = fitAR1(bv), rejects = f.t < crit;
      B.chart(chart, {
        alt: "One simulated path of " + n + " sessions: the persistent part and the observed basis with one-day noise, " +
          "phi1 " + fmt(phi, "n2") + ", noise " + su + " bp, path " + path,
        height: 300,
        x: { type: "num", fmt: "n0", label: "Session", tipLabel: "session ", min: 1, max: n,
             ticks: [1, 50, 100, 150, 200, n] },
        y: { type: "lin", fmt: "n1", tfmt: "n0", label: "Basis (bp)" },
        series: [   // the persistent part first, so the thinner observed path stays visible on top of it
          { name: "Persistent part", color: "2", width: 2.2, x: xs, y: xv },
          { name: "Observed basis", color: "1", width: 1, x: xs, y: bv }
        ],
        ann: [{ type: "hline", y: mean, dash: true }]
      });
      out.innerHTML =
        "<div><span>Model half-life of the persistent part</span><b>" + hlText(phi) + "</b></div>" +
        "<div><span>AR(1) fitted to the observed path</span><b>" + fmt(f.phi, "n3") + " · half-life " + hlText(f.phi) + "</b></div>" +
        "<div><span>DF t-stat against " + fmt(crit, "n2") + "</span><b>" + fmt(f.t, "n2") +
          (rejects ? " · rejects a unit root" : " · no rejection") + "</b></div>" +
        "<div><span>Path (seed)</span><b>" + path + "</b></div>";
    }

    var ctl = B.controls(host, [
      { id: "an-phi", key: "phi", label: "Persistence φ₁", min: 0, max: 1, step: 0.01, value: W.phi0, fmt: "n2" },
      { id: "an-su", key: "su", label: "One-day noise", min: 0, max: 40, step: 1, value: W.sigmaU0,
        fmt: function (val) { return val + " bp"; } },
      { type: "button", id: "an-new", label: "New path" }
    ], draw);
    host.appendChild(chart); host.appendChild(out); host.appendChild(note);
    host.__redraw = function () { draw(ctl.values(), null); };
    ctl.fire();
  };
})();
