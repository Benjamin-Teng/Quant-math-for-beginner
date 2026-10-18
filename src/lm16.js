/* LM16 interactive figure: what a normal model says about correlation in a crash.
   Data: the "widget" block of the chart JSON lm16-widget, inlined in the page by the build
   (<script type="application/json" id="chart-lm16-widget">), written by data/lm16_charts.py:
     corr[i][j], prob[i][j]  the correlation and probability of joint falls of a standard normal pair at least
                             k = 0.05 i standard deviations, correlation 0.01 j (j = 0 .. 95), by numerical integration;
                             joint rises take the same values by symmetry;
     vtwo[i], vlow[i]        Var(Z | |Z| >= k) and Var(Z | Z <= -k) for the one-variable events, used in (16.10);
     data[event]             the U28 pair's days and correlation for each k (null below 30 days).
   The model's correlation is interpolated in the correlation by four-point Lagrange through the four nearest nodes,
   clamped at the ends, as the script checks; one-variable probabilities come from Book.dist.Phi. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt;

  function lag4(row, x, h) {          // four-point Lagrange on the nodes 0, h, 2h, ..., clamped at the ends
    var i0 = Math.min(Math.max(Math.floor(x / h + 1e-9) - 1, 0), row.length - 4), t = x / h - i0, out = 0;
    for (var a = 0; a < 4; a++) {
      var la = 1;
      for (var b = 0; b < 4; b++) if (b !== a) la *= (t - b) / (a - b);
      out += la * row[i0 + a];
    }
    return out;
  }
  function bgl(r, v) { return r / Math.sqrt(r * r + (1 - r * r) / v); }   // (16.10) with Var(X) = 1

  B.widgets.exceed = function (host) {
    var src = document.getElementById("chart-lm16-widget");
    if (!src) { host.innerHTML = '<p class="w-note">The data for this figure are not on the page.</p>'; return; }
    var W = JSON.parse(src.textContent).widget, nk = W.vtwo.length;
    var ks = []; for (var i = 0; i < nk; i++) ks.push(Math.round(i * W.kStep * 100) / 100);
    var LABEL = { fall2: "both fall", rise2: "both rise", two: "Semiconductor moves either way", fall1: "Semiconductor falls" };

    host.innerHTML = '<div class="w-head"><span class="w-title">What a normal model says about correlation in a crash</span><span class="w-tag">Interactive</span></div>';
    var ctl = B.controls(host, [
      { type: "select", id: "ex-ev", key: "ev", label: "Event, k or more", value: "fall2",
        options: [["fall2", "Both fall"], ["rise2", "Both rise"], ["two", "Semiconductor, either way"],
                  ["fall1", "Semiconductor falls"]] },
      { id: "ex-r", key: "r", label: "Correlation of the model", min: 0, max: 0.95, step: 0.0001, value: 0.5749, fmt: "n4" },
      { id: "ex-k", key: "k", label: "k, standard deviations", min: 0, max: 2.5, step: 0.05, value: 2, fmt: "n2" }
    ], draw);
    var chart = document.createElement("div"); host.appendChild(chart);
    var out = document.createElement("div"); out.className = "readout"; out.setAttribute("aria-live", "polite"); host.appendChild(out);
    var note = document.createElement("p"); note.className = "w-note";
    note.innerHTML = "The model is a normal pair with the chosen correlation; at 0.5749 it is fitted to the same days as the data (in-sample). " +
      "Joint events are interpolated from a precomputed grid, one-variable events use (16.10). " +
      "The pair's correlation is shown where at least 30 of its 4,382 days fall in the event.";
    host.appendChild(note);

    function model(ev, r, i) {          // {c: correlation, p: probability} of the event at k = ks[i]
      var k = ks[i];
      if (ev === "fall2" || ev === "rise2") return { c: lag4(W.corr[i], r, W.rhoStep), p: lag4(W.prob[i], r, W.rhoStep) };
      if (ev === "two") return { c: bgl(r, W.vtwo[i]), p: 2 * B.dist.Phi(-k) };
      return { c: bgl(r, W.vlow[i]), p: B.dist.Phi(-k) };
    }

    function draw(v) {
      var ev = v.ev, r = v.r, i = Math.round(v.k / W.kStep), k = ks[i];
      var curve = ks.map(function (_, j) { return model(ev, r, j).c; });
      var d = W.data[ev];
      B.chart(chart, {
        alt: "Correlation given the event " + LABEL[ev] + ": the normal model at correlation " + fmt(r, "n4") + " and the U28 pair, against k",
        height: 280,
        x: { type: "num", fmt: "n2", tfmt: "n1", label: "k standard deviations", tipLabel: "k = ", min: 0, max: 2.5, ticks: [0, 0.5, 1, 1.5, 2, 2.5] },
        y: { type: "lin", fmt: "n3", tfmt: "n1", label: "Correlation given the event", min: 0, max: 1, ticks: [0, 0.2, 0.4, 0.6, 0.8, 1] },
        series: [{ name: "Normal model", color: "2", dash: true, x: ks, y: curve },
                 { name: "U28 pair (at least 30 days)", color: "1", x: ks, y: d.corr }],
        ann: [{ type: "vline", x: k, label: "k = " + fmt(k, "n2") },
              { type: "hline", y: W.rhoHat, dash: true, label: "full sample: " + fmt(W.rhoHat, "n4") }]
      });
      var m = model(ev, r, i), days = d.days[i];
      out.innerHTML =
        "<div><span>Model correlation</span><b>" + fmt(m.c, "n3") + "</b></div>" +
        "<div><span>Model probability · expected days in " + W.T.toLocaleString("en-US") + "</span><b>" + fmt(m.p, "n4") + " · " + fmt(W.T * m.p, "n1") + "</b></div>" +
        "<div><span>U28 pair: correlation · days</span><b>" + (d.corr[i] == null ? "fewer than 30 days (" + days + ")" : fmt(d.corr[i], "n3") + " · " + days) + "</b></div>" +
        "<div><span>Full-sample correlation of the pair</span><b>" + fmt(W.rhoHat, "n4") + "</b></div>";
    }
    host.__redraw = ctl.fire; ctl.fire();
  };
})();
