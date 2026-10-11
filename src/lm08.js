/* LM8 interactive figure: the daily P&L of a fixed book over 7-11 April 2025, Y h, with sliders for the holdings.
   DP holds the price changes per unit in NT$, one row per session: TX per contract (200 x the change in its daily
   settlement price), then 0050 and 00679B per share. P0 holds the prices of 2 April in the same units.
   data/lm08_numbers.py checks both arrays against the raw FinMind files. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt;

  var DAYS = ["7 Apr", "8 Apr", "9 Apr", "10 Apr", "11 Apr"];
  var DP = [[-425800.0, -17.6, 0.54], [-199600.0, -5.15, -1.09], [-197000.0, -7.05, -1.23],
            [343600.0, 14.6, 0.81], [128200.0, 3.75, -1.03]];
  var P0 = [4259200.0, 176.0, 29.88];
  var W0 = 10000000;   // equity, NT$

  function controlsHTML(defs) {
    return '<div class="controls">' + defs.map(function (d) {
      return '<label for="' + d.id + '">' + d.label + ' <span class="v" id="' + d.id + '-v"></span>' +
        '<input type="range" id="' + d.id + '" min="' + d.min + '" max="' + d.max + '" step="' + d.step + '" value="' + d.value + '"></label>';
    }).join("") + "</div>";
  }
  function signed(v) { return (v > 0 ? "+" : "") + fmt(v, "n0"); }

  B.widgets.bookPnl = function (host) {
    host.innerHTML = '<div class="w-head"><span class="w-title">A fixed book over 7–11 April 2025: the daily P&amp;L Y h</span>' +
      '<span class="w-tag">Interactive</span></div>' +
      controlsHTML([
        { id: "bp-tx", label: "TX contracts (negative: short)", min: -3, max: 3, step: 1, value: -1 },
        { id: "bp-50", label: "0050 shares", min: 0, max: 60000, step: 1000, value: 24000 },
        { id: "bp-679", label: "00679B shares", min: 0, max: 300000, step: 10000, value: 100000 }
      ]) + '<div class="bp-chart"></div><div class="readout" aria-live="polite"></div>' +
      '<p class="w-note">The holdings stay fixed all week, so each bar is one entry of Y h: the session\'s price changes ' +
      'times the holdings, summed over the three lines. Bars above zero are gains and bars below zero losses. TX moves ' +
      'NT$200 a point per contract. Exposures are position values at the close of 2 April, also shown as a multiple of ' +
      'equity of NT$10 million.</p>';
    var tx = host.querySelector("#bp-tx"), s50 = host.querySelector("#bp-50"), s679 = host.querySelector("#bp-679");
    var chart = host.querySelector(".bp-chart"), out = host.querySelector(".readout");

    function draw() {
      var h = [+tx.value, +s50.value, +s679.value];
      host.querySelector("#bp-tx-v").textContent = h[0] > 0 ? "+" + h[0] : String(h[0]).replace("-", "−");
      host.querySelector("#bp-50-v").textContent = fmt(h[1], "n0");
      host.querySelector("#bp-679-v").textContent = fmt(h[2], "n0");
      var pnl = DP.map(function (r) { return Math.round(r[0] * h[0] + r[1] * h[1] + r[2] * h[2]); });
      var week = pnl.reduce(function (a, b) { return a + b; }, 0);
      var vals = P0.map(function (p, i) { return p * h[i]; });
      var net = vals[0] + vals[1] + vals[2], gross = Math.abs(vals[0]) + Math.abs(vals[1]) + Math.abs(vals[2]);
      B.chart(chart, {
        type: "bar", alt: "Daily P&L of the chosen fixed book on the five sessions from 7 to 11 April 2025", height: 250,
        categories: DAYS, valueLabels: true,
        y: { fmt: "n0", label: "Daily P&L of the book, NT$" },
        series: [{ name: "Daily P&L", color: "1", values: pnl }]
      });
      // colour by sign; the chart draws the bars in order and skips a bar of height zero
      var bars = chart.querySelectorAll("rect.bar"), k = 0;
      pnl.forEach(function (v) {
        if (v === 0) return;
        if (bars[k]) bars[k].style.fill = v < 0 ? "var(--series-2)" : "var(--series-1)";
        k++;
      });
      out.innerHTML =
        "<div><span>P&amp;L on 7 April</span><b>NT$" + signed(pnl[0]) + "</b></div>" +
        "<div><span>Week, the sum of the bars</span><b>NT$" + signed(week) + "</b></div>" +
        "<div><span>Net exposure, 2 April</span><b>NT$" + fmt(net, "n0") + "</b><span>" + fmt(net / W0, "n3") + " × equity</span></div>" +
        "<div><span>Gross exposure, 2 April</span><b>NT$" + fmt(gross, "n0") + "</b><span>" + fmt(gross / W0, "n3") + " × equity</span></div>";
    }
    [tx, s50, s679].forEach(function (el) { el.addEventListener("input", draw); });
    host.__redraw = draw; draw();
  };
})();
