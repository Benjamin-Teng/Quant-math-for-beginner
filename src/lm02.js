/* LM2 interactive figure: secant-to-tangent explorer with a live error-versus-step panel. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt;

  /* scientific notation with Unicode superscripts, e.g. −1.8×10⁻⁶ */
  var SUP = { "-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹" };
  function sci(v, d) {
    if (v == null || !isFinite(v)) return "—";
    if (v === 0) return "0";
    var a = Math.abs(v);
    if (a >= 1e-3 && a < 1e5) return fmt(v, d === 4 ? "n4" : "n5");
    var e = Math.floor(Math.log10(a)), m = a / Math.pow(10, e);
    if (m >= 9.95) { m /= 10; e += 1; }
    return (v < 0 ? "−" : "") + m.toFixed(1) + "×10" + String(e).split("").map(function (c) { return SUP[c]; }).join("");
  }
  function ladder(hi, lo) {           /* 1-2-5 sequence from hi down to lo */
    var out = [], base = [5, 2, 1];
    for (var e = Math.ceil(Math.log10(hi)) + 1; e >= Math.floor(Math.log10(lo)) - 1; e--)
      for (var i = 0; i < 3; i++) { var v = base[i] * Math.pow(10, e); if (v <= hi * 1.0001 && v >= lo * 0.9999) out.push(+v.toPrecision(6)); }
    return out;
  }

  /* 10-year bond with a 2% annual coupon (the bond used throughout the module) */
  function bondP(y) { var s = 0; for (var t = 1; t <= 10; t++) s += 2 / Math.pow(1 + y, t); return s + 100 / Math.pow(1 + y, 10); }
  function bondD(y) { var s = 0; for (var t = 1; t <= 10; t++) s -= t * 2 / Math.pow(1 + y, t + 1); return s - 1000 / Math.pow(1 + y, 11); }
  /* account A of the motivating case: one TX contract, NT$600,000 of equity when F = 22,116 */
  function levF(F) { var E = 600000 + 200 * (F - 22116); return E > 0 ? 200 * F / E : NaN; }
  function levD(F) { var v = levF(F); return -v * (v - 1) / F; }

  var FUN = {
    exp: { name: "eˣ", f: Math.exp, d: function () { return 1; }, x0: 0, lo: -1.6, hi: 1.6, ylo: -0.4, yhi: 5,
      hs: ladder(1, 0.001), h0: 0.5, elo: -16, xfmt: "n1", yfmt: "n2", hfmt: function (h) { return String(h); }, dd: 5,
      note: "x₀ = 0, so the exact derivative is e⁰ = 1." },
    ln: { name: "ln x", f: Math.log, d: function (x) { return 1 / x; }, x0: 1, lo: 0.08, hi: 2.6, ylo: -2.6, yhi: 1.2,
      hs: ladder(0.5, 0.001), h0: 0.5, elo: -16, xfmt: "n1", yfmt: "n2", hfmt: function (h) { return String(h); }, dd: 5,
      note: "x₀ = 1, so the exact derivative is 1/1 = 1." },
    bond: { name: "Bond price P(y)", f: bondP, d: bondD, x0: 0.02, lo: 0, hi: 0.06, ylo: 64, yhi: 126,
      hs: ladder(0.02, 0.0001), h0: 0.01, elo: -16, xfmt: "pct1", yfmt: "n2", dd: 4,
      hfmt: function (h) { return +(h * 1e4).toPrecision(3) + " bp"; },
      note: "10-year bond, 2% annual coupon, at y₀ = 2%: P′(y₀) = −898.2585 per 100 face per unit of yield." },
    lev: { name: "Leverage f(F), account A", f: levF, d: levD, x0: 22116, lo: 19250, hi: 25500, ylo: 0, yhi: 30,
      hs: ladder(2000, 1), h0: 1000, elo: -10, xfmt: "n0", yfmt: "n2", dd: 5,
      hfmt: function (h) { return h.toLocaleString("en-US") + " points"; },
      note: "One TX contract on NT$600,000 at F₀ = 22,116: f′(F₀) = −f(f−1)/F = −0.0021240 per point. Equity hits zero at F = 19,116." },
    call: { name: "Call payoff max(x − 1, 0)", f: function (x) { return Math.max(x - 1, 0); }, d: null, x0: 1, lo: 0, hi: 2,
      ylo: -0.2, yhi: 1.1, hs: ladder(0.5, 0.001), h0: 0.5, elo: -16, xfmt: "n1", yfmt: "n2", dd: 5,
      hfmt: function (h) { return String(h); },
      note: "At the strike the left slope is 0 and the right slope is 1: no tangent exists, and the central quotient is 0.5 for every Δx." }
  };

  function controlsHTML() {
    return '<div class="controls">' +
      '<label for="sw-f">Function<select id="sw-f">' +
      '<option value="exp">eˣ at x₀ = 0</option><option value="ln">ln x at x₀ = 1</option>' +
      '<option value="bond">Bond price P(y) at y₀ = 2%</option><option value="lev">Leverage f(F) of account A</option>' +
      '<option value="call">Call payoff at the strike</option></select></label>' +
      '<label for="sw-m">Difference quotient<select id="sw-m"><option value="fwd">Forward [h(x₀+Δx) − h(x₀)]/Δx</option>' +
      '<option value="bwd">Backward [h(x₀) − h(x₀−Δx)]/Δx</option><option value="cen">Central [h(x₀+Δx) − h(x₀−Δx)]/(2Δx)</option></select></label>' +
      '<label for="sw-h">Step Δx, slide right to shrink <span class="v" id="sw-h-v"></span>' +
      '<input type="range" id="sw-h" min="0" max="9" step="1" value="1"></label></div>';
  }

  function quotient(F, m, h) {
    var x = F.x0;
    if (m === "fwd") return (F.f(x + h) - F.f(x)) / h;
    if (m === "bwd") return (F.f(x) - F.f(x - h)) / h;
    return (F.f(x + h) - F.f(x - h)) / (2 * h);
  }

  B.widgets.secant = function (host) {
    host.innerHTML = '<div class="w-head"><span class="w-title">From secant to tangent</span><span class="w-tag">Interactive</span></div>' +
      controlsHTML() + '<div class="sw-chart"></div><div class="sw-err"></div><div class="readout" aria-live="polite"></div>' +
      '<p class="w-note sw-note"></p>' +
      '<p class="w-note">Upper panel — grey: the function; dashed: the tangent at x₀, whose slope is the derivative (when one exists); solid: the secant, whose slope is the difference quotient. ' +
      'Lower panel — error of the quotient against the step Δx on log–log axes, computed live in double precision: slope 1 means first order, slope 2 second order, and the rise on the left is rounding error.</p>';
    var sf = host.querySelector("#sw-f"), sm = host.querySelector("#sw-m"), sh = host.querySelector("#sw-h");
    var chart = host.querySelector(".sw-chart"), errc = host.querySelector(".sw-err"), out = host.querySelector(".readout");
    var cur = null;
    function setFun() {
      var F = FUN[sf.value];
      sh.max = String(F.hs.length - 1);
      sh.value = String(Math.max(0, F.hs.indexOf(F.h0)));
      cur = sf.value;
    }
    function draw() {
      if (cur !== sf.value) setFun();
      var F = FUN[sf.value], m = sm.value, h = F.hs[+sh.value], x0 = F.x0, y0 = F.f(x0);
      host.querySelector("#sw-h-v").textContent = F.hfmt(h);
      var xa = m === "fwd" ? x0 : x0 - h, xb = m === "bwd" ? x0 : x0 + h;
      var q = quotient(F, m, h), d = F.d ? F.d(x0) : null;
      var xs = [], fy = [], ty = [], sy = [], N = 240;
      for (var i = 0; i <= N; i++) {
        var x = F.lo + (F.hi - F.lo) * i / N, v = F.f(x);
        xs.push(x); fy.push(isFinite(v) ? v : null);
        ty.push(d == null ? null : y0 + d * (x - x0));
        sy.push(F.f(xa) + q * (x - xa));
      }
      var series = [{ name: F.name, color: "var(--muted)", x: xs, y: fy }];
      if (d != null) series.push({ name: "Tangent at x₀", color: "2", dash: true, x: xs, y: ty });
      series.push({ name: "Secant", color: "1", x: xs, y: sy });
      var clampY = function (v) { return Math.min(Math.max(v, F.ylo), F.yhi); };
      B.lineChart(chart, {
        alt: "Function with its tangent line and a secant line", height: 270,
        x: { type: "num", fmt: F.xfmt, tipLabel: "x = " },
        y: { type: "lin", fmt: F.yfmt, min: F.ylo, max: F.yhi },
        series: series,
        ann: [{ type: "point", x: xa, y: clampY(F.f(xa)), color: "1" }, { type: "point", x: xb, y: clampY(F.f(xb)), color: "1" },
              { type: "point", x: x0, y: clampY(y0), color: "var(--muted)" }]
      });
      /* error panel */
      if (d == null) {
        errc.innerHTML = "";
      } else {
        var other = m === "cen" ? "fwd" : "cen", ks = [], e1 = [], e2 = [];
        var khi = Math.log10(F.hs[0]);
        for (var k = F.elo; k <= khi + 1e-9; k += 0.1) {
          var hh = Math.pow(10, k);
          var r1 = Math.abs(quotient(F, m, hh) - d) / Math.abs(d), r2 = Math.abs(quotient(F, other, hh) - d) / Math.abs(d);
          ks.push(+k.toFixed(2)); e1.push(r1 > 0 && isFinite(r1) ? Math.log10(r1) : null); e2.push(r2 > 0 && isFinite(r2) ? Math.log10(r2) : null);
        }
        var rc = Math.abs(q - d) / Math.abs(d);
        var nm = { fwd: "Forward", bwd: "Backward", cen: "Central" };
        var st = khi - F.elo > 10 ? 4 : 2, xt = [];
        for (var t = Math.ceil(F.elo / st) * st; t <= khi + 1e-9; t += st) xt.push(t);
        B.lineChart(errc, {
          alt: "Relative error of the difference quotient against step size, log-log", height: 210,
          x: { type: "num", fmt: "n0", label: "log₁₀ Δx", tipLabel: "log₁₀ Δx = ", min: F.elo, max: khi, ticks: xt },
          y: { type: "lin", fmt: "n1", tfmt: "n0", label: "log₁₀ relative error", min: -16, max: 1, ticks: [-16, -12, -8, -4, 0] },
          series: [{ name: nm[m] + " (selected)", color: "1", x: ks, y: e1 }, { name: nm[other], color: "var(--muted)", dash: true, x: ks, y: e2 }],
          ann: rc > 0 ? [{ type: "point", x: Math.log10(h), y: Math.max(-16, Math.log10(rc)), color: "1" }] : []
        });
      }
      var err = d == null ? null : q - d, ord = m === "cen" ? 2 : 1;
      out.innerHTML =
        "<div><span>Difference quotient</span><b>" + (Math.abs(q) < 1e5 ? fmt(q, F.dd === 4 ? "n4" : "n5") : sci(q)) + "</b></div>" +
        "<div><span>Derivative h′(x₀)</span><b>" + (d == null ? "none (kink)" : fmt(d, F.dd === 4 ? "n4" : "n5")) + "</b></div>" +
        "<div><span>Error</span><b" + (err != null && Math.abs(err) > 0.01 * Math.abs(d) ? ' class="bad"' : "") + ">" + (err == null ? "—" : sci(err, F.dd)) + "</b></div>" +
        "<div><span>" + (ord === 1 ? "Error ÷ Δx" : "Error ÷ Δx²") + "</span><b>" + (err == null ? "—" : sci(err / Math.pow(h, ord), F.dd)) + "</b></div>";
      host.querySelector(".sw-note").textContent = F.note;
    }
    [sf, sm, sh].forEach(function (c) { c.addEventListener("input", draw); });
    host.__redraw = draw; draw();
  };
})();
