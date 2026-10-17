/* LM12 interactive figure: TAIEX's least-squares coefficients on the 28 sector returns (U28), two samples side by side.
   Data: the "widget" block of the chart JSON lm12-weights, inlined in the page by the build
   (<script type="application/json" id="chart-lm12-weights">), written by data/lm12_charts.py: for each sample (a
   calendar year 2009-2026, the last 250 returns, the full sample) the 28 slopes in the order of the last-250 fit,
   R-squared, the sum of the slopes, the intercept and the number of returns. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt;

  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }

  B.widgets.taiexWeights = function (host) {
    var src = document.getElementById("chart-lm12-weights");
    if (!src) { host.innerHTML = '<p class="w-note">The data for this figure are not on the page.</p>'; return; }
    var W = JSON.parse(src.textContent).widget, keys = Object.keys(W.samples), semi = W.order.indexOf("Semiconductor");

    function options(sel) {
      return keys.map(function (k) {
        return '<option value="' + k + '"' + (k === sel ? " selected" : "") + ">" + esc(W.samples[k].label) + "</option>";
      }).join("");
    }
    host.innerHTML = '<div class="w-head"><span class="w-title">Rebuilding TAIEX from its sectors: the 28 coefficients in two samples</span><span class="w-tag">Interactive</span></div>' +
      '<div class="controls">' +
      '<label for="tw-a">Sample A<select id="tw-a">' + options("2009") + "</select></label>" +
      '<label for="tw-b">Sample B<select id="tw-b">' + options("2026") + "</select></label>" +
      '</div><div class="tw-chart"></div><div class="readout" aria-live="polite"></div>' +
      '<p class="w-note">Each sample has its own least-squares fit of TAIEX\'s daily returns on the 28 sector returns, ' +
      "with an intercept. The sectors keep the order of the last-250 fit. Every fit is in-sample, and comparing two years " +
      "is a stability check, not a forecast; 2026 holds the returns to 8 October.</p>";
    var sa = host.querySelector("#tw-a"), sb = host.querySelector("#tw-b");
    var chart = host.querySelector(".tw-chart"), out = host.querySelector(".readout");

    function negatives(s) { return s.coef.filter(function (v) { return v < 0; }).length; }
    function draw() {
      var a = W.samples[sa.value], b = W.samples[sb.value];
      B.chart(chart, {
        type: "bar", alt: "Coefficients of the 28 sectors in two samples: " + a.label + " and " + b.label, height: 330,
        categories: W.order, x: { label: "Sector index (U28)" },
        y: { fmt: "n4", tfmt: "n1", label: "Coefficient" },
        series: [{ name: "A: " + a.label, color: "1", values: a.coef }, { name: "B: " + b.label, color: "2", values: b.coef }],
        ann: [{ type: "hline", y: 0 }]
      });
      var big = 0;
      for (var i = 1; i < W.order.length; i++) if (Math.abs(b.coef[i] - a.coef[i]) > Math.abs(b.coef[big] - a.coef[big])) big = i;
      var d = b.coef[big] - a.coef[big];
      out.innerHTML =
        "<div><span>A: returns · R-squared · sum of slopes</span><b>" + a.T + " · " + fmt(a.r2, "n5") + " · " + fmt(a.sum, "n3") + "</b></div>" +
        "<div><span>B: returns · R-squared · sum of slopes</span><b>" + b.T + " · " + fmt(b.r2, "n5") + " · " + fmt(b.sum, "n3") + "</b></div>" +
        "<div><span>Semiconductor, A → B</span><b>" + fmt(a.coef[semi], "n3") + " → " + fmt(b.coef[semi], "n3") + "</b></div>" +
        "<div><span>Largest change, B − A</span><b>" + esc(W.order[big]) + " " + (d >= 0 ? "+" : "") + fmt(d, "n3") + "</b></div>" +
        "<div><span>Negative coefficients, A · B</span><b>" + negatives(a) + " · " + negatives(b) + "</b></div>";
    }
    sa.addEventListener("input", draw);
    sb.addEventListener("input", draw);
    host.__redraw = draw; draw();
  };
})();
