/* LM9 interactive figure: 2x2 system explorer. It draws both pictures of a system M x = b: the column picture (the
   two columns, the parallelogram they span, whose area is |det M|, the path x1 m1 + x2 m2 and b) and the row picture
   (one line per equation, meeting at the solution). The presets are the "widget" block of the chart JSON lm09-area,
   inlined in the page by the build (<script type="application/json" id="chart-lm09-area">) and written by
   data/lm09_charts.py. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt;
  var SUP = { "-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹" };

  /* a number for the readout: five significant digits, powers of ten outside 0.001 .. 100,000 */
  function num(v) {
    if (v == null || !isFinite(v)) return "—";
    if (v === 0) return "0";
    var a = Math.abs(v), s;
    if (a >= 0.001 && a < 1e5) {
      s = a.toPrecision(5);
      if (s.indexOf(".") >= 0) s = s.replace(/0+$/, "").replace(/\.$/, "");
    } else {
      var e = Math.floor(Math.log10(a)), m = a / Math.pow(10, e);
      if (+m.toFixed(3) >= 10) { m /= 10; e += 1; }
      s = m.toFixed(3) + " × 10" + String(e).split("").map(function (c) { return SUP[c]; }).join("");
    }
    return (v < 0 ? "−" : "") + s;
  }

  function slider(id, label) {
    return '<label for="' + id + '">' + label + ' <span class="v" id="' + id + '-v"></span>' +
      '<input type="range" id="' + id + '"></label>';
  }

  B.widgets.systemExplorer = function (host) {
    var src = document.getElementById("chart-lm09-area");
    if (!src) { host.innerHTML = '<p class="w-note">The data for this figure are not on the page.</p>'; return; }
    var W = JSON.parse(src.textContent).widget, P = W.presets, TOL = W.tol;
    host.innerHTML = '<div class="w-head"><span class="w-title">A 2×2 system in two pictures: columns, rows and the determinant</span><span class="w-tag">Interactive</span></div>' +
      '<div class="controls"><label for="se-p" style="grid-column:1/-1">System<select id="se-p" style="max-width:100%">' +
      P.map(function (p, i) { return '<option value="' + i + '">' + p.name + "</option>"; }).join("") +
      '<option value="custom">Custom (sliders)</option></select></label>' +
      slider("se-m12", "Column 2, first entry m₁₂") + slider("se-m22", "Column 2, second entry m₂₂") +
      slider("se-b1", "Target, first entry b₁") + slider("se-b2", "Target, second entry b₂") + "</div>" +
      '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:0.4rem 1.2rem">' +
      '<div><div class="kbd-note">Column picture</div><div class="se-col"></div></div>' +
      '<div><div class="kbd-note">Row picture</div><div class="se-row"></div></div></div>' +
      '<div class="readout" aria-live="polite"></div>' +
      '<p class="w-note">Column picture: the columns m₁ (fixed by the system chosen) and m₂ (sliders) span a parallelogram whose area is |det M|; ' +
      "when a solution exists, the dashed path x₁m₁ + x₂m₂ ends at b. Row picture: one line per equation, meeting at the solution. " +
      "As m₂ turns toward m₁ the area shrinks and the mix grows: LM11 measures this sensitivity with the condition number. " +
      "The readout rank M is the number of independent columns (Section 7). " +
      "A determinant within 10⁻⁹ of 0, relative to the product of the column lengths, counts as 0.</p>";
    var sel = host.querySelector("#se-p"), ids = ["se-m12", "se-m22", "se-b1", "se-b2"];
    var inp = ids.map(function (id) { return host.querySelector("#" + id); });
    var colHost = host.querySelector(".se-col"), rowHost = host.querySelector(".se-row"), out = host.querySelector(".readout");
    var cur = P[0];

    function load(p) {
      cur = p;
      var vals = [p.m[0][1], p.m[1][1], p.b[0], p.b[1]], rng = [p.range[0], p.range[0], p.range[1], p.range[1]];
      inp.forEach(function (el, k) {
        el.min = -rng[k]; el.max = rng[k]; el.step = p.step; el.value = vals[k];
      });
    }

    function draw() {
      var dec = cur.step === "any" ? "n5" : "n2";
      var m11 = cur.m[0][0], m21 = cur.m[1][0], m12 = +inp[0].value, m22 = +inp[1].value, b1 = +inp[2].value, b2 = +inp[3].value;
      inp.forEach(function (el, k) { host.querySelector("#" + ids[k] + "-v").textContent = fmt(+el.value, dec); });
      var n1 = Math.hypot(m11, m21), n2 = Math.hypot(m12, m22), nb = Math.hypot(b1, b2);
      var det = m11 * m22 - m12 * m21, x1 = null, x2 = null, rank, verdict, bad = false;
      if (n1 === 0 && n2 === 0) { rank = 0; verdict = nb === 0 ? "every x solves it" : "no solution"; bad = nb !== 0; }
      else if (n1 > 0 && n2 > 0 && Math.abs(det) > TOL * n1 * n2) {
        rank = 2; verdict = "exactly one solution";
        x1 = (b1 * m22 - m12 * b2) / det; x2 = (m11 * b2 - b1 * m21) / det;
      } else {
        rank = 1;
        var u = n1 >= n2 ? [m11, m21] : [m12, m22], nu = Math.max(n1, n2);
        var off = Math.abs(u[0] * b2 - u[1] * b1) > TOL * nu * Math.max(nb, 1e-300);
        verdict = off ? "no solution: the lines are parallel" : "infinitely many: the lines coincide";
        bad = true;
      }
      var theta = n1 > 0 && n2 > 0 ? Math.acos(Math.max(-1, Math.min(1, (m11 * m12 + m21 * m22) / (n1 * n2)))) * 180 / Math.PI : null;

      /* column picture */
      var m1 = [m11, m21], m2 = [m12, m22], s = [m11 + m12, m21 + m22], bv = [b1, b2];
      var vecs = [{ to: m1, color: "1", label: "m_1", width: 2.2 }, { to: m2, color: "2", label: "m_2", width: 2.2 },
                  { to: bv, color: "var(--ink)", label: "b", width: 1.6 }];
      var segs = [{ from: m1, to: s, color: "var(--muted)" }, { from: m2, to: s, color: "var(--muted)" }];
      if (x1 != null && Math.abs(x1) <= 8 && Math.abs(x2) <= 8) {
        var p = [x1 * m11, x1 * m21];
        vecs.push({ to: p, color: "1", dash: true, width: 1.4 }, { from: p, to: bv, color: "2", dash: true, width: 1.4 });
      }
      B.chart(colHost, { type: "vector", alt: "Column picture: the two columns, their parallelogram and the target b", height: 270,
        x: { label: cur.rows[0], fmt: dec, name: cur.rows[0] }, y: { label: cur.rows[1], fmt: dec, name: cur.rows[1] },
        vectors: vecs, segments: segs });

      /* row picture: centred on the solution when there is one, else on the origin */
      var cx = 0, cy = 0, h;
      if (x1 != null && Math.abs(x1) < 1e6 && Math.abs(x2) < 1e6) { cx = x1; cy = x2; h = Math.max(1.5, 0.75 * Math.max(Math.abs(x1), Math.abs(x2))); }
      else {
        h = 1.5;
        [[m11, m12, b1], [m21, m22, b2]].forEach(function (r) { var c = Math.max(Math.abs(r[0]), Math.abs(r[1])); if (c > 0) h = Math.max(h, 1.2 * Math.abs(r[2]) / c); });
      }
      var x0 = cx - h, xe = cx + h, y0 = cy - h, ye = cy + h, lines = [];
      [[m11, m12, b1, cur.rows[0], "1"], [m21, m22, b2, cur.rows[1], "2"]].forEach(function (r) {
        var a = r[0], c = r[1], rhs = r[2], f, t;
        if (a === 0 && c === 0) return;
        if (Math.abs(c) >= Math.abs(a)) { f = [x0, (rhs - a * x0) / c]; t = [xe, (rhs - a * xe) / c]; }
        else { f = [(rhs - c * y0) / a, y0]; t = [(rhs - c * ye) / a, ye]; }
        lines.push({ from: f, to: t, extend: true, color: r[4], width: 2, label: r[3] });
      });
      var pts = x1 != null ? [{ at: [x1, x2], label: "x", color: "var(--ink)" }] : [];
      B.chart(rowHost, { type: "scatter", alt: "Row picture: one line per equation in the plane of the two multiples", height: 270,
        x: { label: cur.axes ? cur.axes[0] : "x_1, multiple of " + cur.cols[0], fmt: "n3", tfmt: "n1", min: x0, max: xe, name: "x_1" },
        y: { label: cur.axes ? cur.axes[1] : "x_2, multiple of " + cur.cols[1], fmt: "n3", tfmt: "n1", min: y0, max: ye, name: "x_2" },
        lines: lines, points: pts });

      out.innerHTML =
        "<div><span>det M = m₁₁m₂₂ − m₁₂m₂₁</span><b>" + num(det) + "</b></div>" +
        "<div><span>Angle between the columns</span><b>" + (theta == null ? "—" : theta.toFixed(2) + "°") + "</b></div>" +
        "<div><span>rank M</span><b>" + rank + "</b></div>" +
        "<div><span>Solutions</span><b" + (bad ? ' class="bad"' : "") + ">" + verdict + "</b></div>" +
        "<div><span>x₁ (" + cur.cols[0] + ")</span><b>" + num(x1) + "</b></div>" +
        "<div><span>x₂ (" + cur.cols[1] + ")</span><b>" + num(x2) + "</b></div>";
    }

    sel.addEventListener("input", function () { if (sel.value !== "custom") { load(P[+sel.value]); } draw(); });
    inp.forEach(function (el) { el.addEventListener("input", function () { sel.value = "custom"; draw(); }); });
    load(P[0]);
    host.__redraw = draw; draw();
  };
})();
