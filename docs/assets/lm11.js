/* LM11 interactive figure: a 2x2 covariance or correlation matrix, its one-standard-deviation ellipse and eigenvectors,
   and how far the solution of M x = b moves when the correlation rises by 0.01. The initial state is Semiconductor and
   FinancialInsurance on the U28 sample (annualized volatilities and correlation printed by data/lm11_numbers.py). */
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

  // the book's sign rule: the entry largest in absolute value is positive; on a tie, the first entry
  function signRule(v) {
    var a = Math.abs(v[0]), b = Math.abs(v[1]);
    var i = a >= b * (1 - 1e-12) ? 0 : 1;
    return v[i] < 0 ? [-v[0], -v[1]] : v;
  }

  // eigenpairs of the symmetric 2x2 matrix [[a, c], [c, d]], largest first
  function eig2(a, c, d) {
    var mid = (a + d) / 2, rad = Math.sqrt((a - d) * (a - d) / 4 + c * c);
    var th = 0.5 * Math.atan2(2 * c, a - d);
    return { l1: mid + rad, l2: mid - rad, q1: signRule([Math.cos(th), Math.sin(th)]), q2: signRule([-Math.sin(th), Math.cos(th)]) };
  }

  function solve2(a, c, d, b) {            // [[a, c], [c, d]] x = b by Cramer's rule (LM9)
    var det = a * d - c * c;
    if (Math.abs(det) < 1e-14 * Math.max(1, a * d)) return null;
    return [(d * b[0] - c * b[1]) / det, (a * b[1] - c * b[0]) / det];
  }

  function matrix(mode, s1, s2, rho) {
    return mode === "corr" ? [1, rho, 1] : [s1 * s1, rho * s1 * s2, s2 * s2];
  }

  B.widgets.pca2 = function (host) {
    host.innerHTML = '<div class="w-head"><span class="w-title">Two assets: eigenvectors, condition number and a moving solution</span><span class="w-tag">Interactive</span></div>' +
      controlsHTML([
        { type: "select", id: "pc-m", label: "Matrix", options: [["cov", "Covariance (annualized)"], ["corr", "Correlation"]] },
        { type: "select", id: "pc-b", label: "Right-hand side b", options: [["e1", "e₁ = (1, 0)"], ["one", "1 = (1, 1)"]] },
        { id: "pc-s1", label: "Volatility σ₁ (asset 1)", min: 0.05, max: 0.6, step: 0.0001, value: 0.2388 },
        { id: "pc-s2", label: "Volatility σ₂ (asset 2)", min: 0.05, max: 0.6, step: 0.0001, value: 0.1907 },
        { id: "pc-r", label: "Correlation ρ", min: -0.99, max: 0.99, step: 0.0001, value: 0.5749 }
      ]) + '<div class="pc-chart"></div><div class="readout" aria-live="polite"></div>' +
      '<p class="w-note">The ellipse is the set of points x with x<sup>T</sup>M<sup>−1</sup>x = 1; its half-axes, √λ₁ and √λ₂, lie along the eigenvectors q₁ and q₂ (signed by the book\'s rule). ' +
      'The last rows solve Mx = b, then raise ρ by 0.01 and solve again. The relative change of the solution never exceeds the bound (11.9): κ times the change of the matrix relative to its spectral norm. ' +
      'Initial state: Semiconductor (asset 1) and FinancialInsurance (asset 2), 2008–2026. With equal volatilities and b = 1 = (1, 1), the vector 1 is an eigenvector. For ρ &gt; 0 it is q₁, and the solution barely moves (relative change 0.01/(1 + ρ)). For ρ &lt; 0 it is q₂, the direction of the small eigenvalue, and the change reaches the bound.</p>';
    var sm = host.querySelector("#pc-m"), sb = host.querySelector("#pc-b");
    var i1 = host.querySelector("#pc-s1"), i2 = host.querySelector("#pc-s2"), ir = host.querySelector("#pc-r");
    var chart = host.querySelector(".pc-chart"), out = host.querySelector(".readout");

    function draw() {
      var mode = sm.value, s1 = +i1.value, s2 = +i2.value, rho = +ir.value;
      host.querySelector("#pc-s1-v").textContent = fmt(s1, "pct2");
      host.querySelector("#pc-s2-v").textContent = fmt(s2, "pct2");
      host.querySelector("#pc-r-v").textContent = fmt(rho, "n4");
      i1.disabled = i2.disabled = mode === "corr";
      var m = matrix(mode, s1, s2, rho), e = eig2(m[0], m[1], m[2]);
      var f = mode === "corr" ? "n2" : "pct0", tf = mode === "corr" ? "n1" : "pct0";
      var a1 = Math.sqrt(e.l1), a2 = Math.sqrt(Math.max(e.l2, 0));
      B.chart(chart, {
        type: "vector", alt: "One-standard-deviation ellipse of the chosen 2x2 matrix with its two eigenvectors", height: 300,
        x: { label: mode === "corr" ? "Asset 1, standardized" : "Asset 1, annualized", fmt: f, tfmt: tf, name: "asset 1" },
        y: { fmt: f, tfmt: tf, name: "asset 2" },
        ellipses: [{ center: [0, 0], cov: [[m[0], m[1]], [m[1], m[2]]], color: "1", fill: true, axes: true }],
        vectors: [{ to: [a1 * e.q1[0], a1 * e.q1[1]], label: "q_1", color: "1" },
                  { to: [a2 * e.q2[0], a2 * e.q2[1]], label: "q_2", color: "2" }]
      });
      var b = sb.value === "one" ? [1, 1] : [1, 0], x = solve2(m[0], m[1], m[2], b);
      var rho2 = rho + 0.01, m2 = matrix(mode, s1, s2, rho2), x2 = rho2 < 1 ? solve2(m2[0], m2[1], m2[2], b) : null;
      var kappa = e.l1 / e.l2, dM = mode === "corr" ? 0.01 : 0.01 * s1 * s2, bound = kappa * dM / e.l1;
      var lf = mode === "corr" ? "n3" : "n4", vec = function (v) { return v ? "(" + fmt(v[0], "n2") + ", " + fmt(v[1], "n2") + ")" : "—"; };
      var rel = x && x2 ? Math.hypot(x2[0] - x[0], x2[1] - x[1]) / Math.hypot(x2[0], x2[1]) : null;
      var ang = Math.atan2(e.q1[1], e.q1[0]) * 180 / Math.PI;
      out.innerHTML =
        "<div><span>Eigenvalues λ₁ · λ₂</span><b>" + fmt(e.l1, lf) + " · " + fmt(e.l2, lf) + "</b></div>" +
        "<div><span>Share of the first component</span><b>" + fmt(e.l1 / (e.l1 + e.l2), "pct1") + "</b></div>" +
        "<div><span>Condition number κ = λ₁/λ₂</span><b>" + fmt(kappa, "n2") + "</b></div>" +
        "<div><span>Angle of q₁ from axis 1</span><b>" + fmt(ang, "n1") + "°</b></div>" +
        "<div><span>Solution x of Mx = b</span><b>" + vec(x) + "</b></div>" +
        "<div><span>After ρ + 0.01</span><b>" + (rho2 < 1 ? vec(x2) : "singular: ρ would be 1") + "</b></div>" +
        "<div><span>Relative change of x</span><b>" + (rel == null ? "—" : fmt(rel, "n4")) + "</b></div>" +
        "<div><span>Bound (11.9)</span><b>" + fmt(bound, "n4") + "</b></div>";
    }
    [sm, sb, i1, i2, ir].forEach(function (el) { el.addEventListener("input", draw); });
    host.__redraw = draw; draw();
  };
})();
