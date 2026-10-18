/* LM14 interactive figure: Jensen's chord on a two-point return.
   A return is +b with probability p and −a otherwise. The figure draws ln(1 + x), the chord between the two outcomes,
   and, above the mean μ, the average of the logs g (on the chord) and the log of the average ln(1 + μ) (on the
   curve). Presets: the "widget" block of the chart JSON lm14-jensen, inlined in the page by the build
   (<script type="application/json" id="chart-lm14-jensen">), written by data/lm14_charts.py; the initial state is its
   first preset, TAIEX's 2008 and 2009 returns as printed in the module. No random numbers. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt;

  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }

  // moments, drag and Jensen gap of the law +b with probability p, −a otherwise
  function law(b, a, p) {
    var q = 1 - p, mu = p * b - q * a, sd = Math.sqrt(p * q) * (a + b);
    var g = p * Math.log1p(b) + q * Math.log1p(-a), lnmu = Math.log1p(mu), RG = Math.expm1(g);
    return { mu: mu, sd: sd, g: g, lnmu: lnmu, RG: RG, jensen: lnmu - g, drag: mu - RG, half: sd * sd / 2,
             second: sd * sd / (2 * (1 + mu) * (1 + mu)) };
  }

  B.widgets.jensen = function (host) {
    var src = document.getElementById("chart-lm14-jensen");
    if (!src) { host.innerHTML = '<p class="w-note">The data for this figure are not on the page.</p>'; return; }
    var P = JSON.parse(src.textContent).widget.presets, first = P[0];
    host.innerHTML = '<div class="w-head"><span class="w-title">Jensen\'s chord on a two-point return</span>' +
      '<span class="w-tag">Interactive</span></div>';
    var ctl = B.controls(host, [
      { type: "select", id: "jn-pre", key: "pre", label: "Law",
        options: P.map(function (o) { return [o.key, esc(o.label)]; }).concat([["custom", "Custom (sliders)"]]), value: first.key },
      { id: "jn-b", key: "b", label: "Gain b", min: 0, max: 1, step: 0.0001, value: first.b, fmt: "pct2" },
      { id: "jn-a", key: "a", label: "Loss a", min: 0, max: 0.9, step: 0.0001, value: first.a, fmt: "pct2" },
      { id: "jn-p", key: "p", label: "Probability of the gain p", min: 0.05, max: 0.95, step: 0.01, value: first.p, fmt: "n2" }
    ], update);
    var chart = document.createElement("div"); host.appendChild(chart);
    var out = document.createElement("div"); out.className = "readout"; out.setAttribute("aria-live", "polite"); host.appendChild(out);
    var note = document.createElement("p"); note.className = "w-note";
    note.innerHTML = "The return is +b with probability p and −a otherwise. The logarithm is concave, so the chord " +
      "lies below the curve: above the mean μ, the chord gives the average of the logs, g, and the curve the log of " +
      "the average, ln(1 + μ). Their difference is the Jensen gap; the volatility drag is μ − R<sub>G</sub> with " +
      "R<sub>G</sub> = e<sup>g</sup> − 1. Gaps are in percentage or log points.";
    host.appendChild(note);
    var sel = host.querySelector("#jn-pre");

    function setSlider(id, v, f) {   // move a slider without an input event, and show its value
      host.querySelector("#" + id).value = v;
      host.querySelector("#" + id + "-v").textContent = fmt(v, f);
    }
    function update(v, id) {
      if (id === "jn-pre" && v.pre !== "custom") {
        var o = P.filter(function (x) { return x.key === v.pre; })[0];
        setSlider("jn-b", o.b, "pct2"); setSlider("jn-a", o.a, "pct2"); setSlider("jn-p", o.p, "n2");
        v = ctl.values();
      } else if (id && id !== "jn-pre") sel.value = "custom";
      draw(v.b, v.a, v.p);
    }
    function draw(b, a, p) {
      var L = law(b, a, p), xs = [], ys = [], cx = [], cy = [], i;
      for (i = 0; i <= 200; i++) { var x = -0.9 + 1.9 * i / 200; xs.push(x); ys.push(Math.log1p(x)); }
      var l0 = Math.log1p(-a), l1 = Math.log1p(b);
      for (i = 0; i <= 60; i++) { var t = -a + (a + b) * i / 60; cx.push(t); cy.push(a + b > 0 ? l0 + (l1 - l0) * (t + a) / (a + b) : l0); }
      B.chart(chart, {
        height: 320,
        alt: "The curve ln(1 + x) with the chord between −" + fmt(a, "pct2").replace("−", "") + " and +" + fmt(b, "pct2") +
          ": above the mean " + fmt(L.mu, "pct1") + " the chord gives the average of the logs, " + fmt(L.g, "pct3") +
          ", and the curve the log of the average, " + fmt(L.lnmu, "pct3"),
        x: { type: "num", fmt: "pct2", tfmt: "pct0", label: "Return x", tipLabel: "x = ", min: -0.9, max: 1.0 },
        y: { type: "lin", fmt: "n4", tfmt: "n1", label: "ln(1 + x)", min: -2.4, max: 0.8 },
        series: [
          { name: "chord between the two outcomes", color: "2", dash: true, x: cx, y: cy },
          { name: "ln(1 + x)", color: "1", x: xs, y: ys }
        ],
        ann: [
          { type: "vline", x: L.mu, dash: true },
          { type: "point", x: L.mu, y: L.lnmu, color: "1", label: "log of the average", anchor: "end", dx: -8, dy: -8 },
          { type: "point", x: L.mu, y: L.g, color: "2", label: "average of the logs", dx: 8, dy: 16 }
        ]
      });
      function pts(v) { return fmt(v * 100, "n2"); }
      out.innerHTML =
        "<div><span>Mean μ · standard deviation σ</span><b>" + fmt(L.mu, "pct1") + " · " + fmt(L.sd, "pct1") + "</b></div>" +
        "<div><span>Average of the logs g · log of the average ln(1 + μ)</span><b>" + fmt(L.g, "pct3") + " · " + fmt(L.lnmu, "pct3") + "</b></div>" +
        "<div><span>Compound rate R<sub>G</sub> · (3.9)'s μ − σ²/2</span><b>" + fmt(L.RG, "pct2") + " · " + fmt(L.mu - L.half, "pct2") + "</b></div>" +
        "<div><span>Jensen gap ln(1 + μ) − g · drag μ − R<sub>G</sub> (points)</span><b>" + pts(L.jensen) + " · " + pts(L.drag) + "</b></div>" +
        "<div><span>σ²/2 · second order σ²/(2(1 + μ)²) (points)</span><b>" + pts(L.half) + " · " + pts(L.second) + "</b></div>";
    }
    host.__redraw = function () { draw.apply(null, [ctl.values().b, ctl.values().a, ctl.values().p]); };
    draw(first.b, first.a, first.p);
  };
})();
