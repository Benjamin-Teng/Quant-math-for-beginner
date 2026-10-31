/* LM29 interactive figure: active sets with two funds and cash, by LM7's enumeration of binding sets.
   Data: the "widget" block of the chart JSON lm29-kktPair, inlined in the page by the build
   (<script type="application/json" id="chart-lm29-kktPair">), written by data/lm29_charts.py: the first window's
   annual excess means e and volatilities s of 0050 and 00646, their correlation rho (unrounded), and the initial
   cap and risk aversion. Model numbers only: no market series and no random draws.
   Problem: maximize f'e - (delta/2) f'Sigma f subject to f1 + f2 <= cap, f1 >= 0, f2 >= 0, the rest in cash at r_f
   (LM28's exposure form). Each of the eight binding sets gives the KKT system
   [delta Sigma, G'; G, 0] [f; nu] = [e; b] for its binding rows G f = b (at most 5 x 5), solved by Gaussian
   elimination with partial pivoting; a pivot below 1e-12 marks the system singular (no candidate). A candidate is
   feasible when G f <= b + 1e-12 and correctly signed when every nu >= -1e-12; the optimum passes both.
   data/lm29_charts.py runs Book.widgets.kktPair.math in Node against the numbers script's pair_kkt. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt;
  var G = [[1, 1], [-1, 0], [0, -1]], NAMES = ["cap", "f₁≥0", "f₂≥0"];

  function solve(M, r) {   // Gaussian elimination with partial pivoting; null when singular
    var n = r.length, A = M.map(function (row, i) { return row.concat([r[i]]); }), i, j, k, p, t;
    for (k = 0; k < n; k++) {
      for (p = k, i = k + 1; i < n; i++) if (Math.abs(A[i][k]) > Math.abs(A[p][k])) p = i;
      if (Math.abs(A[p][k]) < 1e-12) return null;
      t = A[k]; A[k] = A[p]; A[p] = t;
      for (i = k + 1; i < n; i++) for (t = A[i][k] / A[k][k], j = k; j <= n; j++) A[i][j] -= t * A[k][j];
    }
    var x = new Array(n);
    for (i = n - 1; i >= 0; i--) { for (t = A[i][n], j = i + 1; j < n; j++) t -= A[i][j] * x[j]; x[i] = t / A[i][i]; }
    return x;
  }
  function candidates(e, S, delta, cap) {   // the eight binding sets, in the order of itertools.product([0, 1], repeat=3)
    var out = [], b = [cap, 0, 0];
    for (var code = 0; code < 8; code++) {
      var idx = [0, 1, 2].filter(function (k) { return (code >> (2 - k)) & 1; }), n = 2 + idx.length;
      var M = [], r = [e[0], e[1]].concat(idx.map(function (k) { return b[k]; })), i, j;
      for (i = 0; i < n; i++) M.push(new Array(n).fill(0));
      for (i = 0; i < 2; i++) for (j = 0; j < 2; j++) M[i][j] = delta * S[i][j];
      idx.forEach(function (k, c) { M[0][2 + c] = M[2 + c][0] = G[k][0]; M[1][2 + c] = M[2 + c][1] = G[k][1]; });
      var x = solve(M, r), label = idx.map(function (k) { return NAMES[k]; }).join(", ") || "none";
      if (!x) { out.push({ label: label, f: null }); continue; }
      var f = [x[0], x[1]], nu = x.slice(2);
      var feas = G.every(function (g, k) { return g[0] * f[0] + g[1] * f[1] <= b[k] + 1e-12; });
      var signs = nu.every(function (v) { return v >= -1e-12; });
      var u = f[0] * e[0] + f[1] * e[1] - delta / 2 * (f[0] * f[0] * S[0][0] + 2 * f[0] * f[1] * S[0][1] + f[1] * f[1] * S[1][1]);
      out.push({ label: label, f: f, nu: nu, idx: idx, feasible: feas, signs: signs, utility: u });
    }
    return out;
  }

  B.widgets.kktPair = function (host) {
    var src = document.getElementById("chart-lm29-kktPair");
    if (!src) { host.innerHTML = '<p class="w-note">The data for this figure are not on the page.</p>'; return; }
    var W = JSON.parse(src.textContent).widget, e = W.e, s = W.s, rho = W.rho;
    var S = [[s[0] * s[0], rho * s[0] * s[1]], [rho * s[0] * s[1], s[1] * s[1]]];
    host.innerHTML = '<div class="w-head"><span class="w-title">Active sets with two funds and cash</span>' +
      '<span class="w-tag">Interactive</span></div>';
    var ctl = B.controls(host, [
      { id: "kp-cap", key: "cap", label: "Cap on net exposure f₁ + f₂", min: 0.2, max: 2, step: 0.05, value: W.cap, fmt: "n2" },
      { id: "kp-d", key: "delta", label: "Risk aversion δ", min: 1, max: 10, step: 0.5, value: W.delta, fmt: "n1" }
    ], draw);
    var chart = document.createElement("div"), out = document.createElement("div"), note = document.createElement("p");
    out.setAttribute("aria-live", "polite"); note.className = "w-note";
    note.textContent = "Model: maximize f′e − (δ/2) f′Σf for 0050 (f₁) and 00646 (f₂), the rest " +
      "in cash at r_f, subject to f₁ + f₂ ≤ cap, f₁ ≥ 0 and f₂ ≥ 0. Inputs: first window, " +
      "2017-02-13 → 2019-02-27, on its 504 joint dates; in-sample. Excess returns " + fmt(e[0], "pct2") + " and " +
      fmt(e[1], "pct2") + ", volatilities " + fmt(s[0], "pct2") + " and " + fmt(s[1], "pct2") + ", correlation " +
      fmt(rho, "n3") + ". Each binding set solves stationarity with its constraints as equalities; the set with all " +
      "three is singular. Ellipses: contours of the objective about the unconstrained point.";
    host.appendChild(chart); host.appendChild(out); host.appendChild(note);

    function z(x) { return Math.abs(x) < 1e-12 ? 0 : x; }   // an exact zero of a binding row prints as 0.00
    function draw(v) {
      var cands = candidates(e, S, v.delta, v.cap), solv = cands.filter(function (c) { return c.f; });
      var best = solv.filter(function (c) { return c.feasible && c.signs; })[0];
      var fu = solve([[v.delta * S[0][0], v.delta * S[0][1]], [v.delta * S[1][0], v.delta * S[1][1]]], e);
      var d = [best.f[0] - fu[0], best.f[1] - fu[1]];
      var k = Math.sqrt(d[0] * d[0] * S[0][0] + 2 * d[0] * d[1] * S[0][1] + d[1] * d[1] * S[1][1]);
      var det = S[0][0] * S[1][1] - S[0][1] * S[0][1], Si = [[S[1][1] / det, -S[0][1] / det], [-S[0][1] / det, S[0][0] / det]];
      var ells = (k > 1e-9 ? [k, 2 * k] : [0.05, 0.1]).map(function (sc) {
        return { center: fu, cov: Si, scale: sc, color: "var(--muted)" };
      });
      B.chart(chart, {
        type: "scatter", equal: false, height: 340,
        alt: "The plane of exposures to 0050 and 00646 with the feasible triangle, contours of the objective and the " +
          "KKT candidates of the binding sets; the optimum is at (" + fmt(best.f[0], "n2") + ", " + fmt(best.f[1], "n2") + ")",
        x: { label: "f₁, exposure to 0050", fmt: "n2", min: -0.5, max: 2.5, name: "f₁" },
        y: { label: "f₂, exposure to 00646", fmt: "n2", min: -0.5, max: 2.5, name: "f₂" },
        lines: [{ from: [0, 0], to: [v.cap, 0] }, { from: [v.cap, 0], to: [0, v.cap] }, { from: [0, v.cap], to: [0, 0] }],
        ellipses: ells,
        points: solv.filter(function (c) { return c !== best; }).map(function (c) {
          return { at: c.f, color: "var(--muted)", r: 3.5 };
        }).concat([{ at: best.f, color: "1", r: 5.5, label: "optimum: " + best.label }])
      });
      var rows = solv.map(function (c) {
        return "<tr><td>" + c.label + "</td><td>" + fmt(z(c.f[0]), "n2") + "</td><td>" + fmt(z(c.f[1]), "n2") + "</td><td>" +
          (c.nu.length ? c.nu.map(function (x) { return fmt(z(x), "n4"); }).join(", ") : "—") + "</td><td>" +
          (c.feasible ? "yes" : "no") + "</td><td>" + (c.signs ? "yes" : "no") + "</td><td>" + fmt(c.utility, "n4") + "</td></tr>";
      }).join("");
      var nf = solv.filter(function (c) { return c.feasible; }).length, ns = solv.filter(function (c) { return c.signs; }).length;
      out.innerHTML = '<div class="table-wrap"><table><thead><tr><th>Binding</th><th>f₁</th><th>f₂</th>' +
        "<th>Multipliers</th><th>Feasible</th><th>Signs</th><th>Utility</th></tr></thead><tbody>" + rows +
        '</tbody></table></div><p class="w-note">Of ' + solv.length + " solvable binding sets, " + nf +
        " pass feasibility and " + ns + " the signs; only the optimum (" + best.label + " binding, utility " +
        fmt(best.utility, "n4") + ") passes both. Unconstrained point: (" + fmt(fu[0], "n2") + ", " + fmt(fu[1], "n2") + ").</p>";
    }
    host.__redraw = function () { draw(ctl.values()); };
    ctl.fire();
  };
  B.widgets.kktPair.math = { candidates: candidates, solve: solve };
})();
