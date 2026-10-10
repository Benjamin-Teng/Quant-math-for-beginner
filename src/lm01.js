/* LM1 interactive figure: compounding explorer (stated rate × compounding frequency → EAR → e^r − 1). */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt;
  var FREQS = [
    { n: 1, label: "1", name: "annually" },
    { n: 2, label: "2", name: "semiannually" },
    { n: 4, label: "4", name: "quarterly" },
    { n: 12, label: "12", name: "monthly" },
    { n: 52, label: "52", name: "weekly" },
    { n: 365, label: "365", name: "daily" },
    { n: Infinity, label: "∞", name: "continuously" }
  ];

  function ear(r, n) { return n === Infinity ? Math.expm1(r) : Math.pow(1 + r / n, n) - 1; }

  function pctFmt(span) { return span < 0.0005 ? "pct3" : span < 0.005 ? "pct2" : span < 0.05 ? "pct1" : "pct0"; }

  B.widgets.compound = function (host) {
    var opts = FREQS.map(function (f, i) {
      var txt = f.n === Infinity ? "Continuous (n → ∞)" : f.n + "× a year (" + f.name + ")";
      return '<option value="' + i + '"' + (f.n === 4 ? " selected" : "") + ">" + txt + "</option>";
    }).join("");
    host.innerHTML = '<div class="w-head"><span class="w-title">Compounding explorer</span><span class="w-tag">Interactive</span></div>' +
      '<div class="controls">' +
      '<label for="cw-r">Stated annual rate r <span class="v" id="cw-r-v"></span>' +
      '<input type="range" id="cw-r" min="0" max="1" step="0.0025" value="1"></label>' +
      '<label for="cw-n">Compounding frequency n<select id="cw-n">' + opts + "</select></label></div>" +
      '<div class="cw-path"></div><div class="cw-ear"></div>' +
      '<div class="readout" aria-live="polite"></div>' +
      '<p class="w-note">Upper chart: the value of 1 unit during one year when interest is credited n times (steps), ' +
      "compounded continuously (eʳᵗ) or paid as simple interest (1 + rt). Lower chart: the effective annual rate for each " +
      "frequency; it rises with n and levels off at eʳ − 1. At r = 100% the limit is e − 1: the number e is the year-end " +
      "value of 1 unit at a 100% rate compounded continuously.</p>";
    var sr = host.querySelector("#cw-r"), sn = host.querySelector("#cw-n");
    var cPath = host.querySelector(".cw-path"), cEar = host.querySelector(".cw-ear"), out = host.querySelector(".readout");

    function draw() {
      var r = +sr.value, k = +sn.value, F = FREQS[k], n = F.n;
      host.querySelector("#cw-r-v").textContent = fmt(r, "pct2");

      /* ---- value of 1 unit within the year ---- */
      var xs = [], step = [], cont = [], simp = [], N = 200, i;
      for (i = 0; i <= N; i++) { var t = i / N; xs.push(t); cont.push(Math.exp(r * t)); simp.push(1 + r * t); }
      var sx = [], sy = [];
      if (n === Infinity) { sx = xs.slice(); sy = cont.slice(); }
      else {
        var v = 1;
        for (i = 0; i < n; i++) {
          sx.push(i / n); sy.push(v);
          sx.push((i + 1) / n - 1e-9); sy.push(v);
          v *= 1 + r / n;
        }
        sx.push(1); sy.push(v);
      }
      B.lineChart(cPath, {
        alt: "Value of one unit during one year under the selected compounding", height: 230,
        x: { type: "num", fmt: "n2", label: "Time (years)", tipLabel: "t = ", min: 0, max: 1, ticks: [0, 0.25, 0.5, 0.75, 1] },
        y: { type: "lin", fmt: "n4", tfmt: "n2", label: "Value of 1 unit" },
        series: [
          { name: n === Infinity ? "Compounded continuously" : "Compounded " + n + "× a year", color: "1", x: sx, y: sy },
          { name: "Continuous eʳᵗ", color: "2", dash: true, x: xs, y: cont },
          { name: "Simple interest 1 + rt", color: "var(--muted)", x: xs, y: simp }]
      });

      /* ---- EAR by compounding frequency ---- */
      var ex = [], ey = [];
      FREQS.forEach(function (f, j) { ex.push(j); ey.push(ear(r, f.n)); });
      var lim = Math.expm1(r), span = Math.max(lim - r, 1e-6), pad = span * 0.12;
      var res = B.lineChart(cEar, {
        alt: "Effective annual rate by compounding frequency, converging to e^r − 1", height: 210,
        x: { type: "num", fmt: "n0", label: "Compounding periods per year n", tipLabel: "#", min: -0.25, max: 6.25, ticks: [0, 1, 2, 3, 4, 5, 6] },
        y: { type: "lin", fmt: "pct3", tfmt: pctFmt(span), label: "Effective annual rate (1 + r/n)ⁿ − 1", min: r - pad, max: lim + pad },
        series: [{ name: "Effective annual rate", color: "1", x: ex, y: ey }],
        ann: [{ type: "hline", y: lim, label: "limit eʳ − 1 = " + fmt(lim, "pct2") },
              { type: "point", x: k, y: ey[k], color: "2" }]
      });
      // categorical axis: replace index tick labels 0..6 by the frequencies, and fix the tooltip header
      Array.prototype.forEach.call(res.svg.querySelectorAll("text"), function (t) {
        if (t.getAttribute("text-anchor") === "middle" && !t.getAttribute("class") && /^[0-6]$/.test(t.textContent))
          t.textContent = FREQS[+t.textContent].label;
      });
      res.svg.addEventListener("pointermove", function () {
        var hd = cEar.querySelector(".tip .hd");
        if (!hd) return;
        var j = parseInt(hd.textContent.replace(/[^0-9]/g, ""), 10);
        if (j >= 0 && j < FREQS.length) hd.textContent = "n = " + FREQS[j].label;
      });

      /* ---- readout ---- */
      var R = ear(r, n), gap = R - lim;
      out.innerHTML =
        "<div><span>Quote</span><b>" + fmt(r, "pct2") + ", " + F.name + "</b></div>" +
        "<div><span>Periodic rate i = r/n</span><b>" + (n === Infinity ? "—" : fmt(r / n, "pct3")) + "</b></div>" +
        "<div><span>Effective annual rate</span><b>" + fmt(R, "pct3") + "</b></div>" +
        "<div><span>Continuous limit eʳ − 1</span><b>" + fmt(lim, "pct3") + "</b></div>" +
        "<div><span>EAR − limit</span><b>" + (Math.abs(gap) < 0.01 ? fmt(gap, "bp") : fmt(gap, "pct2") + " pts") + "</b></div>" +
        "<div><span>Continuous rate ln(1 + EAR)</span><b>" + fmt(Math.log1p(R), "pct3") + "</b></div>";
    }
    [sr, sn].forEach(function (c) { c.addEventListener("input", draw); });
    host.__redraw = draw; draw();
  };
})();
