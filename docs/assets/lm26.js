/* LM26 interactive figure: how a GARCH(1,1) variance forecast returns to its mean, (26.4).
   Data: the "widget" block of the chart JSON lm26-garchterm, inlined in the page by the build
   (<script type="application/json" id="chart-lm26-garchterm">), written by data/lm26_charts.py: A (sessions a year),
   the full-sample normal fit's alpha and beta (six decimals), its unconditional variance in %^2, and the next day's
   variance forecast in %^2 on the evening of 7 April 2025 ("apr") and on 8 October 2026 ("oct"). Model numbers only:
   no market series and no random draws.
   Formulas: the unconditional variance stays fixed, so omega = uvar (1 - alpha - beta); the forecast m sessions ahead
   is uvar + (alpha + beta)^(m - 1) (start - uvar), and the average over the next m days is its mean over 1..m. When
   alpha + beta >= 1 there is no unconditional variance: omega = 0 (EWMA when the sum is 1), and the forecast is
   start (alpha + beta)^(m - 1), flat at 1 and growing above 1. Half-life ln(1/2)/ln(alpha + beta), (25.2).
   Annualized volatilities are sqrt(A x variance). data/lm26_numbers.py checks the initial readouts against the text. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt, MMAX = 250, YMAX = 0.8;

  B.widgets.garchterm = function (host) {
    var src = document.getElementById("chart-lm26-garchterm");
    if (!src) { host.innerHTML = '<p class="w-note">The data for this figure are not on the page.</p>'; return; }
    var W = JSON.parse(src.textContent).widget, A = W.A, U = W.uvar;
    var STARTS = [["apr", "After 7 April 2025"], ["oct", "After 8 October 2026"]];

    host.innerHTML = '<div class="w-head"><span class="w-title">How a variance forecast returns to its mean</span>' +
      '<span class="w-tag">Interactive</span></div>';
    var ctl = B.controls(host, [
      { id: "gt-a", key: "alpha", label: "α", min: 0, max: 0.25, step: 0.000001, value: W.alpha, fmt: "n4" },
      { id: "gt-b", key: "beta", label: "β", min: 0.6, max: 1, step: 0.000001, value: W.beta, fmt: "n4" },
      { type: "select", id: "gt-s", key: "start", label: "Starting point", options: STARTS, value: W.init.start }
    ], draw);
    var chart = document.createElement("div"), out = document.createElement("div"), note = document.createElement("p");
    out.className = "readout"; out.setAttribute("aria-live", "polite"); note.className = "w-note";
    note.textContent = "Model: GARCH(1,1) forecasts by (26.4), starting from the next day's forecast of the " +
      "full-sample normal fit to TR23 (" + fmt(Math.sqrt(W.start.apr), "n3") + "% a day after 7 April 2025, " +
      fmt(Math.sqrt(W.start.oct), "n3") + "% after 8 October 2026). The unconditional variance stays at " +
      fmt(U, "n4") + " %² a day (" + fmt(Math.sqrt(A * U) / 100, "pct2") + " a year, dashed), so ω = " + fmt(U, "n4") +
      " × (1 − α − β). When α + β ≥ 1 there is no unconditional variance: ω is set to 0, the forecast stays flat " +
      "(EWMA) or grows. Values above 80% a year are not drawn.";
    host.appendChild(chart); host.appendChild(out); host.appendChild(note);

    function vol(v) { return Math.sqrt(A * v) / 100; }
    function cap(v) { return v <= YMAX ? v : null; }

    function draw(v) {
      var a = v.alpha, b = v.beta, s = W.start[v.start], p = a + b, stat = p < 1;
      var xs = [], fore = [], avg = [], sum = 0, f, m;
      for (m = 1; m <= MMAX; m++) {
        f = stat ? U + Math.pow(p, m - 1) * (s - U) : s * Math.pow(p, m - 1);
        sum += f;
        xs.push(m); fore.push(cap(vol(f))); avg.push(cap(vol(sum / m)));
      }
      var hl = stat && p > 0 ? Math.log(0.5) / Math.log(p) : null, ann = [];
      if (stat) ann.push({ type: "hline", y: vol(U), dash: true });
      if (hl != null && hl >= 1 && hl <= MMAX) ann.push({ type: "vline", x: hl, dash: true, label: "half-life " + fmt(hl, "n1") });
      B.chart(chart, {
        alt: "GARCH(1,1) variance forecasts for 1 to 250 sessions ahead, annualized, with alpha " + fmt(a, "n4") +
          " and beta " + fmt(b, "n4") + ": the forecast for each day and the average over the next m days",
        height: 300,
        x: { type: "num", fmt: "n0", label: "Horizon m (sessions)", tipLabel: "m = ", min: 1, max: MMAX,
             ticks: [1, 50, 100, 150, 200, 250] },
        y: { type: "lin", fmt: "pct2", tfmt: "pct0", label: "Annualized volatility", min: 0, max: YMAX,
             ticks: [0, 0.2, 0.4, 0.6, 0.8] },
        series: [
          { name: "Forecast for day t+m", color: "1", x: xs, y: fore },
          { name: "Average over the next m days", color: "2", x: xs, y: avg }
        ],
        ann: ann
      });
      var f20 = 0, f250 = 0;
      for (m = 1; m <= MMAX; m++) {
        f = stat ? U + Math.pow(p, m - 1) * (s - U) : s * Math.pow(p, m - 1);
        if (m <= 20) f20 += f;
        f250 += f;
      }
      out.innerHTML =
        "<div><span>α + β</span><b>" + fmt(p, "n5") + "</b></div>" +
        "<div><span>Half-life (sessions)</span><b>" + (hl == null ? "none (α + β ≥ 1)" : fmt(hl, "n1")) + "</b></div>" +
        "<div><span>Unconditional volatility, a year</span><b>" + (stat ? fmt(vol(U), "pct2") : "none (α + β ≥ 1)") + "</b></div>" +
        "<div><span>Forecast for tomorrow, a year</span><b>" + fmt(vol(s), "pct2") + "</b></div>" +
        "<div><span>Average over the next 20 days</span><b>" + fmt(vol(f20 / 20), "pct2") + "</b></div>" +
        "<div><span>Average over the next 250 days</span><b>" + fmt(vol(f250 / MMAX), "pct2") + "</b></div>";
    }
    host.__redraw = function () { draw(ctl.values()); };
    ctl.fire();
  };
})();
