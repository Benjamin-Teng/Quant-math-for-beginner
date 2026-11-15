/* LM32 interactive figure: VaR and ES of a rule at any tail probability, by three models.
   Data: the "widget" block of the chart JSON lm32-varlevel, inlined in the page by the build
   (<script type="application/json" id="chart-lm32-varlevel">), written by data/lm32_charts.py: for each rule R1-R8,
   its 186 worst out-of-sample net returns sorted (no dates), the mean and s (divisor T = 1,851) of its returns, its
   maximum-likelihood Student-t fit on returns in percent (nu, location, scale; in-sample), and the t quantiles
   F_Y^-1(u) at u = 0.001, 0.002, ..., 0.100 for its nu (Book.dist has no t quantile function).
   Formulas: u = k / 1000 for the slider's k; j = ceil(uT); historical VaR -R_(j) and ES (32.2); normal VaR and ES
   (32.3) with Book.dist.PhiInv and Book.dist.phi; Student-t VaR and ES (32.4) with the grid's q and Book.dist.tPdf.
   No simulation, no optimizer. The first drawing is R1 at u = 1%. data/lm32_charts.py runs
   Book.widgets.varLevel.math in Node against the Python estimators on every rule and every k. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt;

  function measures(W, rule, k) {   // k = 1..100, u = k/1000
    var T = W.T, u = k / 1000, j = Math.ceil(k * T / 1000), x = W.worst[rule], i, sum = 0;
    for (i = 0; i < j - 1; i++) sum += x[i];
    var hv = -x[j - 1], he = -(sum / T + x[j - 1] * (u - (j - 1) / T)) / u;
    var mu = W.mean[rule], s = W.s[rule], z = B.dist.PhiInv(u);
    var nv = -(mu + s * z), ne = -mu + s * B.dist.phi(z) / u;
    var t = W.t[rule], nu = t[0], loc = t[1], sc = t[2], q = W.q[rule][k - 1];
    var tv = -(loc + sc * q) / 100, te = (-loc + sc * (nu + q * q) * B.dist.tPdf(q, nu) / ((nu - 1) * u)) / 100;
    return { j: j, worst: x[j - 1], hv: hv, he: he, nv: nv, ne: ne, tv: tv, te: te, nu: nu };
  }

  B.widgets.varLevel = function (host) {
    var src = document.getElementById("chart-lm32-varlevel");
    if (!src) { host.innerHTML = '<p class="w-note">The data for this figure are not on the page.</p>'; return; }
    var W = JSON.parse(src.textContent).widget;
    host.innerHTML = '<div class="w-head"><span class="w-title">VaR and ES of a rule at any level</span>' +
      '<span class="w-tag">Interactive</span></div>';
    var defs = [
      { id: "vl-rule", key: "rule", label: "Rule", type: "select", value: "R1", options: W.rules.slice() },
      { id: "vl-u", key: "k", label: "Tail probability u", min: 1, max: W.kmax, step: 1, value: 10,
        fmt: function (v) { return fmt(v / 1000, "pct1"); } }
    ];
    var ctl = B.controls(host, defs, draw);
    var chart = document.createElement("div"), out = document.createElement("div"), note = document.createElement("p");
    out.className = "readout"; out.setAttribute("aria-live", "polite"); note.className = "w-note";
    note.innerHTML = "Each rule's 1,851 net daily returns, 5 March 2019 to 8 October 2026 (out-of-sample, fixed in " +
      "advance). Historical: the <i>j</i>th worst return and (32.2), <i>j</i> = ⌈1851<i>u</i>⌉. Normal: (32.3) with " +
      "the rule's mean and <i>s</i> (divisor 1,851; in-sample). Student t: (32.4) with the rule's maximum-likelihood fit " +
      "(in-sample). Starting point: R1 at <i>u</i> = 1%.";
    host.appendChild(chart); host.appendChild(out); host.appendChild(note);

    function draw(v) {
      var rule = v.rule || "R1", k = Math.round(+v.k), m = measures(W, rule, k);
      B.chart(chart, {
        type: "bar", height: 260, valueLabels: true,
        alt: "One-day VaR and ES of " + rule + " at u = " + fmt(k / 1000, "pct1") + " by historical simulation, " +
          "the normal model and the Student t",
        categories: ["historical", "normal", "Student t"], x: { label: "" },
        y: { fmt: "pct2", tfmt: "pct1", label: "Loss", min: 0 },
        series: [{ name: "VaR", color: "1", values: [m.hv, m.nv, m.tv], fmt: "pct2" },
                 { name: "ES", color: "2", values: [m.he, m.ne, m.te], fmt: "pct2" }]
      });
      function item(lbl, val) { return "<div><span>" + lbl + "</span><b>" + val + "</b></div>"; }
      out.innerHTML =
        item("Rank <i>j</i> and the <i>j</i>th worst return", m.j + ", " + fmt(m.worst, "pct2")) +
        item("ES ÷ VaR: historical, normal, t", [m.he / m.hv, m.ne / m.nv, m.te / m.tv].map(function (r) {
          return fmt(r, "n2"); }).join(", ")) +
        item("Fitted ν of the t", fmt(m.nu, "n2"));
    }
    host.__redraw = function () { draw(ctl.values()); };
    ctl.fire();
  };
  B.widgets.varLevel.math = { measures: measures };
})();
