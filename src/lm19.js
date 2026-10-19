/* LM19 interactive figure: how daily variances add up into the annual volatility of TAIEX log returns.
   Data: the "widget" block of the chart JSON lm19-aggregate, inlined in the page by the build
   (<script type="application/json" id="chart-lm19-aggregate">), written by data/lm19_charts.py. For each sample
   (2003-2025, and TR23 to October 2026) it holds T, A (246 sessions a year on 2003-2025, 246.12 on TR23), s_r (the
   standard deviation of the daily log returns, divisor T), the calendar years' standard deviation (2003-2025 only)
   and VR(m) of (19.8) for m = 1, ..., 1,231: statistics of the series, not the series.
   Curves, annualized: overlapping sums sqrt(A VR(m)) s_r; independent days sqrt(A) s_r; the iid expectation
   sqrt(A (1 - m/T)/(1 - 1/T)) s_r. Nothing is simulated. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt;
  var TICKS = [1, 2, 5, 10, 20, 50, 100, 246, 500, 1231];

  function grid(mMax, m) {   // about 60 m values a decade, the endpoints and the chosen m
    var seen = {}, out = [];
    for (var k = 0; k <= 186; k++) {
      var v = Math.round(Math.pow(10, k / 60));
      if (v >= 1 && v <= mMax) seen[v] = 1;
    }
    seen[mMax] = 1; seen[246] = 1; seen[m] = 1;
    for (var x in seen) out.push(+x);
    return out.sort(function (a, b) { return a - b; });
  }

  B.widgets.aggregate = function (host) {
    var src = document.getElementById("chart-lm19-aggregate");
    if (!src) { host.innerHTML = '<p class="w-note">The data for this figure are not on the page.</p>'; return; }
    var W = JSON.parse(src.textContent).widget, S = W.samples;

    host.innerHTML = '<div class="w-head"><span class="w-title">How daily variances add up</span>' +
      '<span class="w-tag">Interactive</span></div>';
    var ctl = B.controls(host, [
      { type: "select", id: "ag-s", key: "sample", label: "Sample ",
        options: [["2025", S["2025"].label], ["all", S.all.label]], value: W.init.sample },
      { id: "ag-m", key: "m", label: "Days in each sum, m", min: 1, max: W.mMax, step: 1, value: W.init.m,
        fmt: function (v) { return v.toLocaleString("en-US"); } }
    ], draw);
    var chart = document.createElement("div"), out = document.createElement("div"), note = document.createElement("p");
    out.className = "readout"; out.setAttribute("aria-live", "polite"); note.className = "w-note";
    host.appendChild(chart); host.appendChild(out); host.appendChild(note);
    note.textContent = "TAIEX total-return log returns; descriptive. VR(m) is (19.8): every window of m consecutive " +
      "days, centred at m times the mean. The iid expectation is the average of VR(m) for independent days, " +
      "(1 - m/T)/(1 - 1/T). Overlapping windows are not independent: the sample holds only T/m disjoint periods.";

    function draw(v) {
      var key = v.sample, d = S[key], m = Math.round(v.m), A = d.A, sr = d.sr, T = d.T;
      var vr = d.vr[m - 1], iid = (1 - m / T) / (1 - 1 / T), xs = grid(W.mMax, m);
      var ovl = [], ind = [], exp = [], base = Math.sqrt(A) * sr;
      xs.forEach(function (x) {
        ovl.push(Math.sqrt(A * d.vr[x - 1]) * sr);
        ind.push(base);
        exp.push(Math.sqrt(A * (1 - x / T) / (1 - 1 / T)) * sr);
      });
      var ann = [{ type: "vline", x: m, dash: true, label: "m = " + m.toLocaleString("en-US") }];
      if (d.cal != null) ann.unshift({ type: "hline", y: d.cal, dash: true, label: "calendar years " + fmt(d.cal, "pct2") });
      B.chart(chart, {
        alt: "Annual volatility of TAIEX log returns, " + d.label + ", from overlapping sums of m days, m from 1 to " +
          "1,231 on a logarithmic axis, against independent days and the iid expectation; m = " + m + " is marked",
        height: 320,
        x: { type: "log", fmt: "n0", label: "Days in each sum, m (log scale)", tipLabel: "m = ", min: 1, max: W.mMax,
             ticks: TICKS, tickLabels: TICKS.map(function (t) { return t.toLocaleString("en-US"); }), values: xs },
        y: { type: "lin", fmt: "pct2", tfmt: "pct0", label: "Annual volatility, √(A · VR(m)) × daily s_r",
             min: 0.08, max: 0.25, ticks: [0.10, 0.15, 0.20, 0.25] },
        series: [
          { name: "Overlapping m-day sums", color: "1", y: ovl },
          { name: "Independent days", color: "2", dash: true, y: ind },
          { name: "iid expectation", color: "3", dash: true, y: exp }
        ],
        ann: ann
      });
      out.innerHTML =
        "<div><span>m · years (m / A)</span><b>" + m.toLocaleString("en-US") + " · " + (m / A).toFixed(2) + "</b></div>" +
        "<div><span>Windows T − m + 1 · disjoint periods T / m</span><b>" + (T - m + 1).toLocaleString("en-US") +
          " · " + (T / m).toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + "</b></div>" +
        "<div><span>VR(m) · iid factor · their ratio</span><b>" + vr.toFixed(4) + " · " + iid.toFixed(3) + " · " +
          (vr / iid).toFixed(3) + "</b></div>" +
        "<div><span>Annual volatility: overlapping sums · independent days</span><b>" +
          fmt(Math.sqrt(A * vr) * sr, "pct2") + " · " + fmt(base, "pct2") + "</b></div>";
    }
    host.__redraw = function () { draw(ctl.values()); };
    ctl.fire();
  };
})();
