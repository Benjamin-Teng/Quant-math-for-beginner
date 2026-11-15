/* LM33 interactive figure: how long must a record be? The minimum track record after n trials, (33.5), and the
   deflated Sharpe ratio, (33.4), for one of the eight rules' moments or for constructed inputs.
   Data: the "widget" block of the chart JSON lm33-mintrack, inlined in the page by the build
   (<script type="application/json" id="chart-lm33-mintrack">), written by data/lm33_charts.py: for R1 to R8 the daily
   Sharpe ratio of the excess returns (per observation), the skewness and the raw kurtosis (divisor T), T = 1,851, and
   A_w and tau = T / A_w of the wealth frame, all unrounded. Model numbers only: no market series and no random draws.
   Formulas: V = 1 - SR Skew + (Kurt - 1) SR^2 / 4, (20.9); E Z_(n) by Simpson's rule on (33.4)'s two integrals over
   [-10, 0] and [0, 10] with 2,000 steps each (Book.dist.Phi); Bailey and Lopez de Prado's approximation
   (1 - g) PhiInv(1 - 1/n) + g PhiInv(1 - 1/(n e)), g = 0.5772156649 (Book.dist.PhiInv); MinTRL after n trials
   1 + ((PhiInv(c) sqrt(V) + E Z_(n)) / SR)^2 observations, (33.5), for SR > 0; PSR(0) and DSR at the through case's
   record of tau years, that is tau x (observations a year) observations (years of sessions at 243.57):
   Phi((SR sqrt(T - 1) - E Z_(n)) / sqrt(V)), (33.2) and (33.4). The readouts say "years of sessions" at 243.57
   observations a year and "years of observations" at 12 or 52. The chart draws DSR against the record in years of observations (observations over
   the observations a year; 0.5 to 20, log scale), dashed at the confidence and at MinTRL.
   The first drawing uses the data block's exact values for R2. Choosing a rule in the first select sets the three
   sliders to its values (shown at the nearest step) and uses its exact values, which are daily: while they are in
   use, the "Observations a year" select is fixed at 243.57 (A_w) and disabled. Once one of the three sliders moves,
   every input is a slider value (constructed), the first select shows "Constructed inputs" (an option the reader
   cannot choose, so that choosing any rule again is a change and fires), and 12 and 52 observations a year become
   available, the sliders then giving that period's moments. data/lm33_charts.py runs Book.widgets.minTrack.math in
   Node against Python on the eight rules at several n, confidence levels and frequencies, and drives the widget
   itself on a minimal DOM through a slider move, a frequency, a rule chosen again and a trial count. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt, D = B.dist, EULER = 0.5772156649015329;

  function simpson(g, a, b, m) {   // m even
    var h = (b - a) / m, s = g(a) + g(b), i;
    for (i = 1; i < m; i++) s += (i % 2 ? 4 : 2) * g(a + i * h);
    return s * h / 3;
  }
  function emax(n) {               // (33.4): E Z_(n) for n iid standard normals
    if (n === 1) return 0;
    var up = simpson(function (z) { return 1 - Math.pow(D.Phi(z), n); }, 0, 10, 2000);
    var lo = simpson(function (z) { return Math.pow(D.Phi(z), n); }, -10, 0, 2000);
    return up - lo;
  }
  function approx(n) {             // Bailey and Lopez de Prado (2014); -Infinity at n = 1, so none
    if (n < 2) return null;
    return (1 - EULER) * D.PhiInv(1 - 1 / n) + EULER * D.PhiInv(1 - 1 / (n * Math.E));
  }
  function vsr(sr, sk, ku) { return 1 - sr * sk + (ku - 1) / 4 * sr * sr; }   // (20.9)
  function mintrl(sr, sk, ku, ez, conf) {                                      // (33.5), in observations
    if (!(sr > 0)) return null;
    var q = (D.PhiInv(conf) * Math.sqrt(vsr(sr, sk, ku)) + ez) / sr;
    return 1 + q * q;
  }
  function dsr(sr, sk, ku, ez, T) {                                            // (33.4); PSR(0) when ez = 0
    return D.Phi((sr * Math.sqrt(T - 1) - ez) / Math.sqrt(vsr(sr, sk, ku)));
  }

  B.widgets.minTrack = function (host) {
    var src = document.getElementById("chart-lm33-mintrack");
    if (!src) { host.innerHTML = '<p class="w-note">The data for this figure are not on the page.</p>'; return; }
    var W = JSON.parse(src.textContent).widget, rule = W.rules.indexOf("R2");
    function near(x, step, d) { return (Math.round(x / step) * step).toFixed(d); }
    function annual(j) { return W.sr[j] * Math.sqrt(W.Aw); }
    host.innerHTML = '<div class="w-head"><span class="w-title">How long must a record be?</span>' +
      '<span class="w-tag">Interactive</span></div>';
    var SL = [["mt-sr", function (j) { return annual(j); }, 0.0001, 4, "n4"],
              ["mt-sk", function (j) { return W.skew[j]; }, 0.0001, 4, "n4"],
              ["mt-ku", function (j) { return W.kurt[j]; }, 0.001, 3, "n3"]];
    var defs = [
      { type: "select", id: "mt-rule", key: "rule", label: "Start from", value: "R2",
        options: W.rules.map(function (r) { return [r, r + "'s moments"]; }) },
      { id: "mt-sr", key: "sr", label: "Annual Sharpe ratio", min: 0.2, max: 2.5, step: 0.0001,
        value: near(annual(rule), 0.0001, 4), fmt: "n4" },
      { id: "mt-sk", key: "sk", label: "Skewness", min: -2, max: 1, step: 0.0001,
        value: near(W.skew[rule], 0.0001, 4), fmt: "n4" },
      { id: "mt-ku", key: "ku", label: "Raw kurtosis", min: 3, max: 25, step: 0.001,
        value: near(W.kurt[rule], 0.001, 3), fmt: "n3" },
      { type: "select", id: "mt-n", key: "n", label: "Trials n", value: "8",
        options: [["1", "1"], ["2", "2"], ["3", "3"], ["5", "5"], ["8", "8"], ["10", "10"], ["20", "20"], ["50", "50"],
                  ["100", "100"], ["1000", "1,000"]] },
      { type: "select", id: "mt-a", key: "a", label: "Observations a year", value: "daily",
        options: [["12", "12"], ["52", "52"], ["daily", "243.57"]] },
      { type: "select", id: "mt-c", key: "c", label: "Confidence", value: "0.95",
        options: [["0.9", "90%"], ["0.95", "95%"], ["0.99", "99%"]] }
    ];
    var ctl = B.controls(host, defs, draw);
    var chart = document.createElement("div"), out = document.createElement("div"), note = document.createElement("p");
    out.className = "readout"; out.setAttribute("aria-live", "polite"); note.className = "w-note";
    note.innerHTML = "Starting point (out-of-sample): R2's unrounded daily Sharpe ratio, skewness and raw kurtosis " +
      "over the 1,851 sessions from 5 March 2019, 243.57 observations a year, n = 8 trials and 95%. Choosing a rule " +
      "restores its exact values, which are daily, so the frequency stays at 243.57 observations a year. Once a " +
      "slider moves, the inputs are constructed, and 12 or 52 observations a year read the sliders as that period's " +
      "moments. " +
      "E Z<sub>(n)</sub> by quadrature of (33.4); MinTRL by (33.5); PSR(0) and DSR at the record of 7.60 years, " +
      "that is 7.60 times the observations a year (years of sessions at 243.57). A record's years are its observations over the " +
      "observations a year. Model: independent trials with true ratio zero, and the estimate held fixed as the " +
      "record lengthens.";
    host.appendChild(chart); host.appendChild(out); host.appendChild(note);
    var ruleSel = host.querySelector("#mt-rule"), aSel = host.querySelector("#mt-a");
    var cons = document.createElement("option");   // shown once a slider moves; the reader cannot choose it
    cons.value = "constructed"; cons.textContent = "Constructed inputs"; cons.disabled = true;
    ruleSel.appendChild(cons);

    function draw(v, id) {
      if (id === "mt-rule" && W.rules.indexOf(v.rule) >= 0) {   // the sliders take the rule's values, no input events
        rule = W.rules.indexOf(v.rule);
        SL.forEach(function (s) {
          var el = host.querySelector("#" + s[0]);
          el.value = near(s[1](rule), s[2], s[3]);
          host.querySelector("#" + s[0] + "-v").textContent = fmt(+el.value, s[4]);
        });
      } else if (id === "mt-sr" || id === "mt-sk" || id === "mt-ku") { rule = -1; ruleSel.value = "constructed"; }
      var ex = rule >= 0;
      if (ex) aSel.value = "daily";   // a rule's moments are daily: 243.57 observations a year while they are in use
      aSel.disabled = ex;
      aSel.title = ex ? "A rule's moments are daily. Move a slider to choose 12 or 52." : "";
      var A = ex || v.a === "daily" ? W.Aw : +v.a, n = +v.n, conf = +v.c;
      var sr = ex ? W.sr[rule] : v.sr / Math.sqrt(A);
      var sk = ex ? W.skew[rule] : v.sk, ku = ex ? W.kurt[rule] : v.ku;
      var ez = emax(n), ap = approx(n), T = W.tau * A;
      var mt = mintrl(sr, sk, ku, ez, conf), d = dsr(sr, sk, ku, ez, T), p0 = dsr(sr, sk, ku, 0, T);
      var xs = [], ys = [], k, yr;
      for (k = 0; k <= 120; k++) { yr = 0.5 * Math.pow(40, k / 120); xs.push(yr); ys.push(dsr(sr, sk, ku, ez, yr * A)); }
      var ann = [{ type: "hline", y: conf, dash: true, label: fmt(conf, "pct0") }];
      if (mt != null && mt / A >= 0.5 && mt / A <= 20) ann.push({ type: "vline", x: mt / A, dash: true, label: "MinTRL" });
      B.chart(chart, {
        alt: "DSR against the record's length in years, on a log scale, for the chosen moments and number of trials, " +
          "with the confidence level and MinTRL dashed",
        height: 260,
        x: { type: "log", fmt: "n2", tfmt: "n1", label: "Record, years of observations (log scale)", min: 0.5, max: 20,
             ticks: [0.5, 1, 2, 5, 10, 20] },
        y: { type: "lin", fmt: "n3", tfmt: "n2", label: "DSR", min: 0, max: 1, ticks: [0, 0.25, 0.5, 0.75, 1] },
        series: [{ name: "DSR, n = " + n, color: "1", x: xs, y: ys }],
        ann: ann
      });
      function item(lbl, val) { return "<div><span>" + lbl + "</span><b>" + val + "</b></div>"; }
      var yrs = A === W.Aw ? " years of sessions" : " years of observations";   // sessions only at 243.57 a year
      out.innerHTML =
        item("E Z<sub>(n)</sub>, exact; approximation", fmt(ez, "n4") + "; " + (ap == null ? "—" : fmt(ap, "n4"))) +
        item("MinTRL after n trials", mt == null ? "none: the ratio is not positive" :
          fmt(mt, "n0") + " observations, " + fmt(mt / A, "n2") + yrs) +
        item("PSR(0) at 7.60" + yrs, fmt(p0, "n3")) +
        item("DSR at 7.60" + yrs, fmt(d, "n3"));
    }
    host.__redraw = function () { draw(ctl.values(), null); };
    ctl.fire();
  };
  B.widgets.minTrack.math = { emax: emax, approx: approx, vsr: vsr, mintrl: mintrl, dsr: dsr };
})();
