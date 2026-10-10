/* LM3 interactive figures: Taylor explorer and volatility-drag explorer. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt;

  function controlsHTML(defs) {
    return '<div class="controls">' + defs.map(function (d) {
      if (d.type === "select")
        return '<label for="' + d.id + '">' + d.label + '<select id="' + d.id + '">' +
          d.options.map(function (o) { return '<option value="' + o[0] + '">' + o[1] + "</option>"; }).join("") + "</select></label>";
      return '<label for="' + d.id + '">' + d.label + ' <span class="v" id="' + d.id + '-v"></span>' +
        '<input type="range" id="' + d.id + '" min="' + d.min + '" max="' + d.max + '" step="' + d.step + '" value="' + d.value + '"></label>';
    }).join("") + "</div>";
  }

  /* ---------------- Taylor explorer ---------------- */
  var FUN = {
    ln: { name: "ln(1+x)", lo: -0.95, hi: 1.6, ylo: -3, yhi: 1.6,
      f: function (x) { return Math.log1p(x); },
      T: function (x, n) { var s = 0, p = 1; for (var k = 1; k <= n; k++) { p *= x; s += (k % 2 ? 1 : -1) * p / k; } return s; },
      bound: function (x, n) { var base = x >= 0 ? 1 : 1 + x; return Math.pow(Math.abs(x), n + 1) / ((n + 1) * Math.pow(base, n + 1)); },
      ann: [{ type: "vline", x: 1, label: "radius of convergence: x = 1", anchor: "end" }] },
    exp: { name: "eˣ", lo: -3, hi: 3, ylo: -3, yhi: 21,
      f: Math.exp,
      T: function (x, n) { var s = 1, p = 1; for (var k = 1; k <= n; k++) { p *= x / k; s += p; } return s; },
      bound: function (x, n) { var fct = 1; for (var k = 2; k <= n + 1; k++) fct *= k; return Math.exp(Math.max(0, x)) * Math.pow(Math.abs(x), n + 1) / fct; },
      ann: [] },
    sqrt: { name: "√(1+x)", lo: -0.95, hi: 1.6, ylo: -0.6, yhi: 2,
      f: function (x) { return Math.sqrt(1 + x); },
      T: function (x, n) { var s = 1, c = 1, p = 1; for (var k = 1; k <= n; k++) { c *= (0.5 - (k - 1)) / k; p *= x; s += c * p; } return s; },
      bound: null,
      ann: [{ type: "vline", x: 1, label: "radius of convergence: x = 1", anchor: "end" }] }
  };

  B.widgets.taylor = function (host) {
    host.innerHTML = '<div class="w-head"><span class="w-title">Taylor polynomial explorer</span><span class="w-tag">Interactive</span></div>' +
      controlsHTML([
        { type: "select", id: "tw-f", label: "Function", options: [["ln", "ln(1 + x)"], ["exp", "eˣ"], ["sqrt", "√(1 + x)"]] },
        { id: "tw-n", label: "Order n", min: 1, max: 10, step: 1, value: 2 },
        { id: "tw-x", label: "Evaluate at x", min: -0.9, max: 1.5, step: 0.01, value: -0.1 }
      ]) + '<div class="tw-chart"></div><div class="readout" aria-live="polite"></div>' +
      '<p class="w-note">Grey curve: the function. Coloured curve: its order-n Taylor polynomial about 0. Raise n and watch the fit improve inside the radius of convergence and fail outside it.</p>';
    var sel = host.querySelector("#tw-f"), sn = host.querySelector("#tw-n"), sx = host.querySelector("#tw-x");
    var chart = host.querySelector(".tw-chart"), out = host.querySelector(".readout");
    function draw() {
      var F = FUN[sel.value], n = +sn.value;
      if (sel.value === "exp") { sx.min = -3; sx.max = 3; } else { sx.min = -0.9; sx.max = 1.5; }
      var x0 = Math.min(Math.max(+sx.value, +sx.min), +sx.max);
      host.querySelector("#tw-n-v").textContent = n;
      host.querySelector("#tw-x-v").textContent = x0.toFixed(2);
      var xs = [], fy = [], ty = [], N = 160;
      for (var i = 0; i <= N; i++) { var x = F.lo + (F.hi - F.lo) * i / N; xs.push(x); fy.push(F.f(x)); var t = F.T(x, n); ty.push(t > F.yhi * 3 || t < F.ylo * 3 ? null : t); }
      var fx = F.f(x0), tx = F.T(x0, n);
      B.lineChart(chart, {
        alt: "Function and Taylor polynomial", height: 280,
        x: { type: "num", fmt: "n1", label: "x", tipLabel: "x = " },
        y: { type: "lin", fmt: "n3", tfmt: "n1", min: F.ylo, max: F.yhi },
        series: [{ name: F.name, color: "var(--muted)", x: xs, y: fy }, { name: "T" + n + "(x), order " + n, color: "1", x: xs, y: ty }],
        ann: F.ann.concat([{ type: "point", x: x0, y: Math.min(Math.max(tx, F.ylo), F.yhi), color: "1" }, { type: "point", x: x0, y: fx, color: "var(--muted)" }])
      });
      var err = fx - tx, bd = F.bound ? F.bound(x0, n) : null;
      out.innerHTML =
        "<div><span>f(x)</span><b>" + fmt(fx, "n5") + "</b></div>" +
        "<div><span>T" + n + "(x)</span><b>" + fmt(tx, "n5") + "</b></div>" +
        "<div><span>Error f − T</span><b" + (Math.abs(err) > 0.01 ? ' class="bad"' : "") + ">" + fmt(err, "n5") + "</b></div>" +
        "<div><span>Lagrange bound</span><b>" + (bd == null ? "—" : fmt(bd, "n5")) + "</b></div>";
    }
    [sel, sn, sx].forEach(function (c) { c.addEventListener("input", draw); });
    host.__redraw = draw; draw();
  };

  /* ---------------- Volatility-drag explorer ---------------- */
  B.widgets.drag = function (host) {
    host.innerHTML = '<div class="w-head"><span class="w-title">Volatility drag in a two-outcome world</span><span class="w-tag">Interactive</span></div>' +
      controlsHTML([
        { id: "dw-mu", label: "Arithmetic mean μ per period", min: -0.05, max: 0.15, step: 0.0025, value: 0.08 },
        { id: "dw-s", label: "Volatility σ per period", min: 0, max: 0.8, step: 0.01, value: 0.2 },
        { id: "dw-n", label: "Periods T", min: 2, max: 60, step: 2, value: 20 }
      ]) + '<div class="dw-chart"></div><div class="readout" aria-live="polite"></div>' +
      '<p class="w-note">Each period the return is μ + σ or μ − σ with equal probability, so σ is exactly the standard deviation. The exact geometric return is √((1+μ)² − σ²) − 1.</p>';
    var smu = host.querySelector("#dw-mu"), ss = host.querySelector("#dw-s"), sn = host.querySelector("#dw-n");
    var chart = host.querySelector(".dw-chart"), out = host.querySelector(".readout");
    function geo(mu, s) { var q = (1 + mu) * (1 + mu) - s * s; return q > 0 ? Math.sqrt(q) - 1 : null; }
    function draw() {
      var mu = +smu.value, s = +ss.value, N = +sn.value;
      host.querySelector("#dw-mu-v").textContent = fmt(mu, "pct2");
      host.querySelector("#dw-s-v").textContent = fmt(s, "pct0");
      host.querySelector("#dw-n-v").textContent = N;
      var smax = Math.min(0.8, 1 + mu - 1e-3), xs = [], ex = [], ap = [], ar = [];
      for (var i = 0; i <= 120; i++) { var v = smax * i / 120; xs.push(v); ex.push(geo(mu, v)); ap.push(mu - v * v / 2); ar.push(mu); }
      var gx = geo(mu, s);
      B.lineChart(chart, {
        alt: "Geometric return versus volatility", height: 270,
        x: { type: "num", fmt: "pct0", label: "Volatility σ per period", tipLabel: "σ = ", min: 0, max: smax },
        y: { type: "lin", fmt: "pct0" },
        series: [
          { name: "Arithmetic mean μ", color: "var(--muted)", x: xs, y: ar, dash: true },
          { name: "Exact geometric return", color: "1", x: xs, y: ex },
          { name: "Approximation μ − σ²/2", color: "2", x: xs, y: ap }],
        ann: gx == null ? [] : [{ type: "point", x: s, y: gx, color: "1" }]
      });
      var ruin = mu - s <= -1;
      var g = ruin ? null : 0.5 * (Math.log1p(mu + s) + Math.log1p(mu - s));
      var a1 = mu - s * s / 2, a2 = mu - (s * s + mu * mu) / 2;
      out.innerHTML = ruin
        ? '<div><span>Outcome</span><b class="bad">A −100% outcome is possible: log wealth is −∞ (ruin)</b></div>'
        : "<div><span>Exact geometric</span><b>" + fmt(gx, "pct3") + "</b></div>" +
          "<div><span>μ − σ²/2</span><b>" + fmt(a1, "pct3") + "</b></div>" +
          "<div><span>Approx. error</span><b" + (Math.abs(a1 - gx) > 0.0025 ? ' class="bad"' : "") + ">" + fmt(a1 - gx, "bp") + "</b></div>" +
          "<div><span>Log growth g</span><b>" + fmt(g, "pct3") + "</b></div>" +
          "<div><span>Mean wealth after T periods</span><b>" + fmt(Math.pow(1 + mu, N), "x2") + "</b></div>" +
          "<div><span>Median wealth after T periods</span><b>" + fmt(Math.exp(g * N), "x2") + "</b></div>";
    }
    [smu, ss, sn].forEach(function (c) { c.addEventListener("input", draw); });
    host.__redraw = draw; draw();
  };
})();
