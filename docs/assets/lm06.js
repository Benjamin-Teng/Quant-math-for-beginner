/* LM6 interactive figure: loan amortization explorer (level payment, equal principal, grace period). */
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

  /* Monthly schedule for a loan of B0. Level payment PMT: eq. (6.16), principal PMT v^(n-t+1) as in (6.18).
     Equal principal: Q = B0/(n-m) a month plus interest. Grace: m interest-only months first. */
  function schedule(B0, apr, years, graceYears, method) {
    var i = apr / 12, n = Math.round(years * 12);
    var m = Math.min(Math.round(graceYears * 12), n - 12);
    var N = n - m, PMT = i === 0 ? B0 / N : B0 * i / (1 - Math.pow(1 + i, -N)), Q = B0 / N;
    var rows = [], bal = B0;
    for (var k = 1; k <= n; k++) {
      var I = bal * i, prin;
      if (k <= m) prin = 0;
      else if (k === n) prin = bal;
      else prin = method === "level" ? PMT - I : Q;
      bal -= prin;
      rows.push({ k: k, pay: I + prin, I: I, P: prin, bal: Math.abs(bal) < 1e-6 ? 0 : bal });
    }
    return { rows: rows, m: m, n: n, i: i };
  }

  B.widgets.amort = function (host) {
    host.innerHTML = '<div class="w-head"><span class="w-title">Loan amortization explorer</span><span class="w-tag">Interactive</span></div>' +
      controlsHTML([
        { id: "am-L", label: "Loan (NT$ million)", min: 1, max: 30, step: 0.5, value: 10 },
        { id: "am-r", label: "Annual rate (nominal)", min: 0.005, max: 0.08, step: 0.0005, value: 0.022 },
        { id: "am-y", label: "Term (years)", min: 5, max: 40, step: 1, value: 30 },
        { id: "am-g", label: "Grace period, interest only (years)", min: 0, max: 5, step: 1, value: 0 },
        { type: "select", id: "am-m", label: "Repayment method", options: [["level", "Level payment (本息平均攤還)"], ["equal", "Equal principal (本金平均攤還)"]] }
      ]) + '<div class="am-chart"></div><div class="readout" aria-live="polite"></div>' +
      '<p class="w-note">Monthly rate = annual rate ÷ 12. Level payment: every payment is equal and its principal part grows by the factor 1 + i each month (6.18). Equal principal: the same principal every month, so payments fall in a straight line (6.19). Initial setting: the illustrative NT$10 million, 30-year, 2.2% mortgage of the worked example below.</p>';
    var sL = host.querySelector("#am-L"), sr = host.querySelector("#am-r"), sy = host.querySelector("#am-y"),
        sg = host.querySelector("#am-g"), sm = host.querySelector("#am-m");
    var chart = host.querySelector(".am-chart"), out = host.querySelector(".readout");
    function draw() {
      var B0 = +sL.value * 1e6, apr = +sr.value, yrs = +sy.value, g = +sg.value, method = sm.value;
      host.querySelector("#am-L-v").textContent = fmt(+sL.value, "n1");
      host.querySelector("#am-r-v").textContent = fmt(apr, "pct2");
      host.querySelector("#am-y-v").textContent = yrs;
      host.querySelector("#am-g-v").textContent = g;
      var S = schedule(B0, apr, yrs, g, method), rows = S.rows;
      var xs = [], pay = [], ints = [], prin = [];
      rows.forEach(function (r) { xs.push(r.k / 12); pay.push(r.pay); ints.push(r.I); prin.push(r.P); });
      var ann = S.m > 0 ? [{ type: "vline", x: S.m / 12, label: "grace ends" }] : [];
      var maxPay = rows.reduce(function (s, r) { return Math.max(s, r.pay); }, 0);
      B.lineChart(chart, {
        alt: "Monthly payment split into interest and principal", height: 280,
        x: { type: "num", fmt: "n0", label: "Years since the loan started", tipLabel: "year ", min: 0, max: yrs },
        y: { type: "lin", fmt: "n0", min: 0, max: maxPay * 1.1, label: "NT$ per month" },
        series: [
          { name: "Payment", color: "1", x: xs, y: pay },
          { name: "Interest", color: "2", area: true, x: xs, y: ints },
          { name: "Principal", color: "3", x: xs, y: prin }],
        ann: ann
      });
      var totI = rows.reduce(function (s, r) { return s + r.I; }, 0);
      var cross = null;
      for (var j = 0; j < rows.length; j++) if (rows[j].P > rows[j].I) { cross = rows[j].k; break; }
      var bal5 = rows.length >= 60 ? rows[59].bal : 0;
      out.innerHTML =
        "<div><span>First payment</span><b>" + fmt(rows[0].pay, "n0") + "</b></div>" +
        "<div><span>Largest payment</span><b>" + fmt(maxPay, "n0") + "</b></div>" +
        "<div><span>Last payment</span><b>" + fmt(rows[rows.length - 1].pay, "n0") + "</b></div>" +
        "<div><span>Total interest</span><b>" + fmt(totI, "n0") + "</b></div>" +
        "<div><span>Interest ÷ loan</span><b>" + fmt(totI / B0, "pct1") + "</b></div>" +
        "<div><span>Balance after 5 years</span><b>" + fmt(bal5, "n0") + "</b></div>" +
        "<div><span>Principal &gt; interest from</span><b>" + (cross ? "month " + cross : "—") + "</b></div>" +
        "<div><span>Effective annual rate</span><b>" + fmt(Math.pow(1 + S.i, 12) - 1, "pct3") + "</b></div>";
    }
    [sL, sr, sy, sg, sm].forEach(function (c) { c.addEventListener("input", draw); });
    host.__redraw = draw; draw();
  };
})();
