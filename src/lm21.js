/* LM21 interactive figure: three multiple-testing rules on one family of normal statistics.
   Each draw takes m statistics Z_i from Book.rng(seed): a standard normal draw, plus the chosen mean t-stat for the
   first round(share * m) tests (the "real effects"). Two-sided p-values are 2 Phi(-|Z_i|) (21.2). At level alpha = q,
   Bonferroni rejects p_i <= alpha / m (21.6), Holm the leading ranks with p_(i) <= alpha / (m - i + 1) (21.7) and
   Benjamini-Hochberg the ranks up to the largest i with p_(i) <= i q / m (21.8). The chart shows |Z| by rank for the
   first 40 ranks, with each rule's level in |Z| units: Phi^-1(1 - alpha / (2m)), Phi^-1(1 - alpha / (2(m - i + 1)))
   and Phi^-1(1 - i q / (2m)). The widget embeds no data; its generator is not NumPy's, and the text quotes no widget
   value. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt, D = B.dist;
  var MS = [["17", "17"], ["50", "50"], ["100", "100"], ["200", "200"], ["500", "500"], ["1000", "1,000"]];
  var LEVELS = [["0.01", "1%"], ["0.05", "5%"], ["0.1", "10%"]];
  var SHOW = 40;

  function family(m, share, effect, seed) {   // the statistics, sorted by |Z| from the largest (p-value from the smallest)
    var g = B.rng(seed), k = Math.round(share * m), out = [];
    for (var i = 0; i < m; i++) {
      var z = g.normal() + (i < k ? effect : 0), a = Math.abs(z);
      out.push({ a: a, p: 2 * D.Phi(-a), real: i < k });
    }
    out.sort(function (x, y) { return y.a - x.a; });
    return { tests: out, k: k };
  }

  function rules(tests, m, alpha) {   // the number of rejections of each rule; rejected ones are the leading ranks
    var bonf = 0, holm = 0, bh = 0, raw = 0, i;
    for (i = 0; i < m; i++) {
      if (tests[i].p <= alpha / m) bonf++;
      if (tests[i].p <= alpha) raw++;
      if (tests[i].p <= (i + 1) * alpha / m) bh = i + 1;
    }
    for (i = 0; i < m; i++) { if (tests[i].p <= alpha / (m - i)) holm++; else break; }
    return { bonf: bonf, holm: holm, bh: bh, raw: raw };
  }

  function falseAmong(tests, n) {   // tests without an effect among the first n ranks
    var f = 0;
    for (var i = 0; i < n; i++) if (!tests[i].real) f++;
    return f;
  }

  function z(u) { return -D.PhiInv(u); }   // the |Z| whose two-sided tail is 2u

  function segments(n, level, color, label, dash) {   // a level in |Z| units, from rank 1 to rank n, labelled at n
    var out = [];
    if (n === 1) return [{ from: [0.6, level(1)], to: [1.4, level(1)], color: color, label: label, dash: !!dash }];
    for (var i = 1; i < n; i++) {
      var s = { from: [i, level(i)], to: [i + 1, level(i + 1)], color: color, dash: !!dash };
      if (i === n - 1) s.label = label;
      out.push(s);
    }
    return out;
  }

  B.widgets.multitest = function (host) {
    host.innerHTML = '<div class="w-head"><span class="w-title">Many tests, three rules</span>' +
      '<span class="w-tag">Interactive</span></div>';
    var chartBox = document.createElement("div"), out = document.createElement("div"), note = document.createElement("p");
    out.className = "readout"; out.setAttribute("aria-live", "polite"); note.className = "w-note";
    note.textContent = "Each draw gives m standard normal statistics from the book's seeded generator, and adds the " +
      "chosen mean t-stat to the first share of them: those have a real effect, the rest none. The chart shows the " +
      "40 largest |Z| by rank, with each rule's level; a rule rejects the leading ranks (Holm until its first miss, " +
      "Benjamini–Hochberg up to its largest rank on or below its line). New draw moves to the next seed. The " +
      "widget's generator is not NumPy's; the text quotes no widget value.";
    var seed = 1;

    function draw(vals, id) {
      if (id === "mt-new") seed++;
      var m = +vals.m, alpha = +vals.alpha, share = +vals.share, effect = +vals.effect;
      var F = family(m, share, effect, seed), t = F.tests, n = Math.min(m, SHOW), r = rules(t, m, alpha);
      var real = { x: [], y: [] }, none = { x: [], y: [] }, top = 0, i;
      for (i = 0; i < n; i++) {
        var pt = t[i].real ? real : none;
        pt.x.push(i + 1); pt.y.push(t[i].a);
        top = Math.max(top, t[i].a);
      }
      var maxNull = 0;
      for (i = 0; i < m; i++) if (!t[i].real) maxNull = Math.max(maxNull, t[i].a);
      var ymax = Math.max(6, Math.ceil(top + 0.5));
      var lines = segments(n, function () { return z(alpha / (2 * m)); }, "2", "Bonferroni")
        .concat(segments(n, function (k) { return z(alpha / (2 * (m - k + 1))); }, "3", "Holm"))
        .concat(segments(n, function (k) { return z(k * alpha / (2 * m)); }, "4", "BH", true));
      B.chart(chartBox, {
        type: "scatter",
        alt: "Absolute values of the largest test statistics by rank, those with a real effect marked apart, against " +
          "the levels of Bonferroni, Holm and Benjamini-Hochberg",
        height: 300,
        legend: true,
        x: { label: "Rank i (largest |Z| first)", name: "rank", fmt: "n0", min: 0.5, max: n + 0.5 },
        y: { label: "|Z|", name: "|Z|", fmt: "n2", tfmt: "n0", min: 0, max: ymax },
        series: [{ name: "no effect", color: "1", x: none.x, y: none.y },
                 { name: "real effect", color: "2", x: real.x, y: real.y }],
        lines: lines
      });
      function row(label, k) {
        return "<div><span>" + label + "</span><b>" + fmt(k, "n0") + " rejected, " + fmt(falseAmong(t, k), "n0") +
          " false</b></div>";
      }
      out.innerHTML =
        row("Bonferroni", r.bonf) + row("Holm", r.holm) + row("Benjamini–Hochberg", r.bh) +
        row("No correction, p ≤ α", r.raw).replace("</b>", " (" + fmt((m - F.k) * alpha, "n2") + " expected)</b>") +
        "<div><span>Largest |Z| without an effect</span><b>" + (m > F.k ? fmt(maxNull, "n2") : "none") + "</b></div>" +
        "<div><span>Draw (seed)</span><b>" + seed + "</b></div>";
    }

    var ctl = B.controls(host, [
      { type: "select", id: "mt-m", key: "m", label: "Tests m", options: MS, value: "100" },
      { id: "mt-share", key: "share", label: "Share with a real effect", min: 0, max: 0.5, step: 0.05, value: 0.1, fmt: "pct0" },
      { id: "mt-eff", key: "effect", label: "Mean t-stat of a real effect", min: 0, max: 5, step: 0.5, value: 3, fmt: "n1" },
      { type: "select", id: "mt-a", key: "alpha", label: "Level α = q", options: LEVELS, value: "0.05" },
      { type: "button", id: "mt-new", label: "New draw" }
    ], draw);
    host.appendChild(chartBox); host.appendChild(out); host.appendChild(note);
    host.__redraw = ctl.fire;
    ctl.fire();
  };
})();
