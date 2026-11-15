/* LM35 interactive figure: a scenario builder for the through case's current books.
   Data: the "widget" block of the chart JSON lm35-builder, inlined in the page by the build
   (<script type="application/json" id="chart-lm35-builder">), written by data/lm35_charts.py: the five funds, the eight
   rules' exposures at the close of 8 October 2026, the presets' shock vectors (exact, decimals), for each window preset
   every rule's lowest unit-book value on the window's dates, the 2,362 joint dates' mean, covariance and inverse
   covariance (divisor T) and their sorted Mahalanobis distances (no dates).
   Formulas: the chosen book f is the rule's own (L = 1'f) or its unit book scaled to the slider's total exposure L,
   g = L f / (1'f). Its return under a shock x is g'x and the wealth after it 1 + g'x (ruin at or below 0, reported,
   never floored). The ruin leverage of (35.2) is -1/(u'x) with u = f / (1'f); over a window it uses the unit book's
   lowest value on the window's dates, as Section 8 states, and the readout gives the lowest wealth too. For a one-day
   shock the distance is d = sqrt((x - mu)' Sigma^-1 (x - mu)), with the count of historical days farther than
   d + 1e-6 (a count, not a probability); a window gets no daily distance. The reverse preset is (35.4) in closed form
   for g and a loss of 10%: x = mu - (0.10 + g'mu) Sigma g / (g'Sigma g). Custom uses the five sliders; moving a shock
   slider selects Custom, and moving the L slider selects "Total exposure L". The first drawing uses the data block's
   exact values. data/lm35_charts.py runs Book.widgets.scenarioBuilder.math in Node against NumPy for every rule and
   preset at several L (each rule's own included) and on custom shocks. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt;
  var COLORS = ["1", "2", "3", "var(--muted)", "4"];   // 0050, 00646, 00679B, 00635U (grey), 00642U

  function dot(a, b) { var s = 0; for (var i = 0; i < a.length; i++) s += a[i] * b[i]; return s; }
  function mv(M, v) { return M.map(function (row) { return dot(row, v); }); }
  function total(f) { return f.reduce(function (s, x) { return s + x; }, 0); }
  function dist(W, x) { var z = x.map(function (v, i) { return v - W.mu[i]; }); return Math.sqrt(dot(z, mv(W.Si, z))); }
  function farther(W, d) { var n = 0; for (var i = 0; i < W.dist.length; i++) if (W.dist[i] > d + 1e-6) n++; return n; }
  function reverse(W, g, loss) {   // (35.4): the least unusual shock with g'x = -loss
    var Sg = mv(W.S, g), k = (loss + dot(g, W.mu)) / dot(g, Sg);
    return W.mu.map(function (m, i) { return m - k * Sg[i]; });
  }
  function evaluate(W, rule, preset, L, custom) {   // null when no shock is defined (the reverse preset at L = 0)
    var f = W.books[rule], u = f.map(function (x) { return x / total(f); }), g = u.map(function (x) { return L * x; });
    var p = W.presets[preset], x, win = preset !== "custom" && p.kind === "window";
    if (preset === "custom") x = custom;
    else if (p.kind === "reverse") { if (!(L > 0)) return null; x = reverse(W, g, W.loss); }
    else x = p.x;
    var ru = dot(u, x), low = win ? p.low[rule] : null, worst = win ? low : ru, d = win ? null : dist(W, x);
    return { x: x, parts: g.map(function (gi, i) { return gi * x[i]; }), ret: L * ru, wealth: 1 + L * ru,
             low: low, lowWealth: win ? 1 + L * low : null, ruin: worst < 0 ? -1 / worst : null, d: d,
             farther: d === null ? null : farther(W, d) };
  }

  B.widgets.scenarioBuilder = function (host) {
    var src = document.getElementById("chart-lm35-builder");
    if (!src) { host.innerHTML = '<p class="w-note">The data for this figure are not on the page.</p>'; return; }
    var W = JSON.parse(src.textContent).widget, exact = true;
    host.innerHTML = '<div class="w-head"><span class="w-title">Build a shock, see the loss</span>' +
      '<span class="w-tag">Interactive</span></div>';
    var x0 = W.presets[W.init.preset].x;
    var defs = [
      { type: "select", id: "sb-rule", key: "rule", label: "Book", options: W.rules, value: W.init.rule },
      { type: "select", id: "sb-preset", key: "preset", label: "Shock",
        options: W.order.map(function (k) { return [k, W.presets[k].label]; }), value: W.init.preset },
      { type: "select", id: "sb-scale", key: "scale", label: "Exposure",
        options: [["own", "The rule's own book"], ["L", "Total exposure L (slider)"]], value: "own" },
      { id: "sb-L", key: "L", label: "Total exposure L", min: 0, max: 20, step: 0.1, value: W.init.L.toFixed(1),
        fmt: "n1" }
    ].concat(W.funds.map(function (s, i) {
      return { id: "sb-x" + i, key: "x" + i, label: "Custom shock, " + s, min: -50, max: 50, step: 0.1,
               value: (Math.round(1000 * x0[i]) / 10).toFixed(1), fmt: function (v) { return fmt(v / 100, "pct1"); } };
    }));
    var ctl = B.controls(host, defs, draw);
    var chart = document.createElement("div"), out = document.createElement("div"), note = document.createElement("p");
    out.className = "readout"; out.setAttribute("aria-live", "polite"); note.className = "w-note";
    note.innerHTML = "Hypothetical: each rule's book at the close of 8 October 2026 under a past or a built shock, " +
      "holdings fixed, no interest. The book is the rule's own (R8's holds total exposure " +
      fmt(total(W.books.R8), "n2") + ", the others 1) or its unit book scaled to the slider's L. The presets are the " +
      "exact shocks of Sections 3 to 6. A window is a frozen replay over several sessions: it gets no daily distance, " +
      "and its ruin leverage, (35.2), uses the book's lowest value on the window's dates. Reverse stress: (35.4) for a " +
      "loss of 10% on the chosen book. Distances use the mean and covariance of the 2,362 joint dates (in-sample). " +
      "Ruin at wealth 0 or below.";
    host.appendChild(chart); host.appendChild(out); host.appendChild(note);

    function item(lbl, val) { return "<div><span>" + lbl + "</span><b>" + val + "</b></div>"; }
    function wealthText(w) { return w <= 0 ? "ruined: " + fmt(w, "pct2") + " of the start" : fmt(w, "pct2") + " of the start"; }
    function draw(v, id) {
      if (id != null) exact = false;
      if (id && id.indexOf("sb-x") === 0 && v.preset !== "custom") {
        document.getElementById("sb-preset").value = "custom"; v.preset = "custom";
      }
      if (id === "sb-L" && v.scale !== "L") { document.getElementById("sb-scale").value = "L"; v.scale = "L"; }
      var rule = exact ? W.init.rule : v.rule, preset = exact ? W.init.preset : v.preset;
      var L = exact ? W.init.L : v.scale === "own" ? total(W.books[rule]) : v.L;
      var custom = W.funds.map(function (_, i) { return v["x" + i] / 100; });
      var r = evaluate(W, rule, preset, L, custom);
      if (!r) {
        chart.innerHTML = ""; out.innerHTML = item("Reverse stress", "no shock: at L = 0 the book cannot lose"); return;
      }
      B.chart(chart, {
        type: "bar", stack: true, height: 260,
        alt: "Each fund's part L times exposure times shock of the chosen book's return under the chosen shock, " +
          "stacked into the book's return",
        categories: [rule + " at L = " + fmt(L, "n2")], x: { label: "" },
        y: { fmt: "pct2", tfmt: "pct0", label: "Part of the return" },
        series: W.funds.map(function (s, i) { return { name: s, color: COLORS[i], values: [r.parts[i]], fmt: "pct2" }; })
      });
      var win = r.low !== null;
      out.innerHTML =
        item("Shock, " + W.funds.join(", "), r.x.map(function (x) { return fmt(x, "pct2"); }).join(", ")) +
        item("Book's return", fmt(r.ret, "pct2")) +
        item(win ? "Wealth at the window's last close" : "Wealth after", wealthText(r.wealth)) +
        (win ? item("Lowest wealth in the window", wealthText(r.lowWealth)) : "") +
        item(win ? "Ruin leverage, (35.2), at the lowest value" : "Ruin leverage, (35.2)",
             r.ruin === null ? (win ? "none: the book never loses in the window" : "none: the shock is a gain") :
             fmt(r.ruin, "n2")) +
        item("Mahalanobis distance", r.d === null ? "a window, not a day: no daily distance" :
             fmt(r.d, "n2") + " (" + r.farther + " of " + W.dist.length.toLocaleString("en-US") +
             " days farther: a count, not a probability)");
    }
    host.__redraw = function () { draw(ctl.values(), null); };
    ctl.fire();
  };
  B.widgets.scenarioBuilder.math = { evaluate: evaluate, reverse: reverse, dist: dist, farther: farther };
})();
