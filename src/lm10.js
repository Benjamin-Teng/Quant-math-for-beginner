/* LM10 interactive figure: can three correlations coexist? Sliders set rho12, rho13 and rho23 of a 3 x 3 pairwise
   correlation matrix C_pw. The readout shows the three 2 x 2 principal minors, det C_pw and the verdict by all
   principal minors (test 4 of Section 5); when C_pw is not PSD it also shows a witness x = adj(C_pw) e_j, for which
   x'C_pw x = det C_pw * adj(C_pw)_jj < 0 (Practice Problem 7).
   The chart draws the set det C_pw >= 0 in the (rho13, rho23) plane for the current rho12, and the current point.
   Initial state: the constructed example of Section 6 (0.982, 0.199, -0.444, printed by data/lm10_numbers.py), so the
   printed page shows the failure. No eigenvalues are used. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt;
  var INIT = { r12: 0.982, r13: 0.199, r23: -0.444 };
  var TOL = 1e-12;
  var CPW = "C<sub>pw</sub>";

  function slider(id, label, value) {
    return '<label for="' + id + '">' + label + ' <span class="v" id="' + id + '-v"></span>' +
      '<input type="range" id="' + id + '" min="-1" max="1" step="0.001" value="' + value + '"></label>';
  }

  // d decimals; a non-zero value that would round to zero at d decimals gets three significant figures instead,
  // so a small negative determinant never prints as "−0" beside the verdict "not PSD"
  function num(v, d) {
    if (v !== 0 && Math.abs(v) < 0.5 * Math.pow(10, -d)) {
      var p = Math.abs(v).toExponential(2).split("e");
      return (v < 0 ? "−" : "") + p[0] + " × 10<sup>" + String(+p[1]).replace("-", "−") + "</sup>";
    }
    return (v < 0 ? "−" : "") + Math.abs(v).toFixed(d);
  }

  // adjugate of the symmetric matrix [[1,a,b],[a,1,c],[b,c,1]]: the transposed matrix of cofactors
  function adjugate(a, b, c) {
    return [[1 - c * c, b * c - a, a * c - b],
            [b * c - a, 1 - b * b, a * b - c],
            [a * c - b, a * b - c, 1 - a * a]];
  }
  function form(x, a, b, c) {   // x'C_pw x
    return x[0] * x[0] + x[1] * x[1] + x[2] * x[2] + 2 * (a * x[0] * x[1] + b * x[0] * x[2] + c * x[1] * x[2]);
  }
  function vec(x) { return "(" + x.map(function (v) { return num(v, 3); }).join(", ") + ")"; }

  B.widgets.corr3 = function (host) {
    host.innerHTML = '<div class="w-head"><span class="w-title">Can these three correlations coexist?</span><span class="w-tag">Interactive</span></div>' +
      '<div class="controls">' +
      slider("c3-12", "ρ₁₂ (0050 / 00631L)", INIT.r12) +
      slider("c3-13", "ρ₁₃ (0050 / 00679B)", INIT.r13) +
      slider("c3-23", "ρ₂₃ (00631L / 00679B)", INIT.r23) +
      '</div><div class="c3-chart"></div><div class="readout" aria-live="polite"></div>' +
      '<p class="w-note">The sliders set the three correlations of a pairwise matrix ' + CPW + '. The starting values are the constructed example of Section 6: three correlations from three different years (2018, 2023 and 2019), which no single sample can produce. ' +
      'The shaded ellipse is the set where det ' + CPW + ' ≥ 0 for the current ρ₁₂, inside the square of correlations between −1 and 1; the dot is the current (ρ₁₃, ρ₂₃). ' +
      'The verdict checks all seven principal minors. When ' + CPW + ' is not PSD, the witness is the column x = adj(' + CPW + ')e<sub>j</sub> of the adjugate with the largest 2 × 2 minor, and xᵀ' + CPW + 'x = det ' + CPW + ' · adj(' + CPW + ')<sub>jj</sub> (Practice Problem 7). ' +
      'Values too small for the decimals shown appear with three significant figures.</p>';
    var s12 = host.querySelector("#c3-12"), s13 = host.querySelector("#c3-13"), s23 = host.querySelector("#c3-23");
    var chart = host.querySelector(".c3-chart"), out = host.querySelector(".readout");

    function draw() {
      var a = +s12.value, b = +s13.value, c = +s23.value;
      host.querySelector("#c3-12-v").textContent = fmt(a, "n3");
      host.querySelector("#c3-13-v").textContent = fmt(b, "n3");
      host.querySelector("#c3-23-v").textContent = fmt(c, "n3");
      var adj = adjugate(a, b, c);
      var minors = [adj[0][0], adj[1][1], adj[2][2]];            // the 2 x 2 principal minors without row j
      var det = 1 + 2 * a * b * c - a * a - b * b - c * c;
      var pd = minors[2] > TOL && det > TOL;                       // leading minors 1, 1 - rho12^2, det C_pw
      var psd = det >= -TOL && minors.every(function (m) { return m >= -TOL; });
      var verdict = pd ? "positive definite" : psd ? "PSD, singular" : "not PSD";
      var wx = "none", wq = "≥ 0 for every x";
      if (!psd) {
        var j = minors.indexOf(Math.max.apply(null, minors));
        var x = [adj[0][j], adj[1][j], adj[2][j]];
        if (minors[j] > TOL) {
          wx = vec(x); wq = num(form(x, a, b, c), 4);
        } else {                                                   // a corner: every 2 x 2 minor is 0
          var best = null, bv = 0;
          [[1, 1, -1], [1, -1, 1], [-1, 1, 1], [1, 1, 1]].forEach(function (y) {
            var v = form(y, a, b, c); if (v < bv) { bv = v; best = y; }
          });
          if (best) { wx = vec(best); wq = num(bv, 4); }
        }
      }
      var labels = ["1 − ρ₂₃²", "1 − ρ₁₃²", "1 − ρ₁₂²"];
      out.innerHTML = minors.map(function (m, k) {
          return "<div><span>" + labels[k] + "</span><b>" + num(m, 4) + "</b></div>";
        }).join("") +
        "<div><span>det " + CPW + "</span><b" + (det < -TOL ? ' class="bad"' : "") + ">" + num(det, 6) + "</b></div>" +
        "<div><span>Verdict</span><b" + (psd ? "" : ' class="bad"') + ">" + verdict + "</b></div>" +
        '<div style="grid-column: span 2"><span>Witness x = adj(' + CPW + ')e<sub>j</sub></span><b>' + wx + "</b></div>" +
        "<div><span>xᵀ" + CPW + "x</span><b" + (psd ? "" : ' class="bad"') + ">" + wq + "</b></div>";
      var sq = [[[-1, -1], [1, -1]], [[1, -1], [1, 1]], [[1, 1], [-1, 1]], [[-1, 1], [-1, -1]]];
      B.chart(chart, {
        type: "vector", height: 320,
        alt: "The set of (rho13, rho23) with det C_pw >= 0 for the current rho12, and the current point",
        x: { label: "ρ_{13}", fmt: "n3", min: -1.1, max: 1.1, name: "ρ_{13}" },
        y: { label: "ρ_{23}", fmt: "n3", min: -1.1, max: 1.1, name: "ρ_{23}" },
        ellipses: [{ center: [0, 0], cov: [[1, a], [a, 1]], scale: 1, color: "1", fill: true }],
        segments: sq.map(function (s) { return { from: s[0], to: s[1], color: "var(--muted)", width: 1 }; }),
        points: [{ at: [b, c], color: psd ? "1" : "2", label: psd ? "consistent" : "not PSD" }]
      });
    }
    [s12, s13, s23].forEach(function (el) { el.addEventListener("input", draw); });
    host.__redraw = draw; draw();
  };
})();
