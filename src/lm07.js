/* LM7 interactive figure: two-asset volatility explorer (correlation and weight sliders,
   volatility curve with the minimum-variance point). Presets are the sample estimates printed by
   data/lm07_stats.py (population moments, annualized with A = 243.05 trading days a year). */
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

  // sigma_0050, sigma_00679B, rho (from data/lm07_stats.py)
  var PRESETS = {
    is:   { s1: 0.163706, s2: 0.135475, rho: -0.221314 },
    oos:  { s1: 0.234031, s2: 0.134335, rho: -0.021900 },
    full: { s1: 0.201060, s2: 0.134959, rho: -0.105632 }
  };

  function vol(w, s1, s2, rho) {
    var v = w * w * s1 * s1 + (1 - w) * (1 - w) * s2 * s2 + 2 * w * (1 - w) * rho * s1 * s2;
    return Math.sqrt(Math.max(v, 0));
  }

  B.widgets.twoasset = function (host) {
    host.innerHTML = '<div class="w-head"><span class="w-title">Two-asset explorer: weight, correlation and the minimum-variance point</span><span class="w-tag">Interactive</span></div>' +
      controlsHTML([
        { type: "select", id: "ta-p", label: "Inputs", options: [["is", "0050 / 00679B, 2017–2021"], ["oos", "0050 / 00679B, 2022–2026"], ["full", "0050 / 00679B, 2017–2026"], ["custom", "Custom (sliders)"]] },
        { id: "ta-rho", label: "Correlation ρ", min: -1, max: 1, step: "any", value: -0.221314 },
        { id: "ta-w", label: "Weight w in asset 1 (0050)", min: -0.25, max: 1.25, step: 0.01, value: 0.6 },
        { id: "ta-s1", label: "Volatility σ₁ (0050)", min: 0.05, max: 0.4, step: "any", value: 0.163706 },
        { id: "ta-s2", label: "Volatility σ₂ (00679B)", min: 0.05, max: 0.4, step: "any", value: 0.135475 }
      ]) + '<div class="ta-chart"></div><div class="readout" aria-live="polite"></div>' +
      '<p class="w-note">The portfolio holds w in asset 1 and 1 − w in asset 2, rebalanced to these weights. Coloured curve: σ<sub>p</sub>(w) at the chosen ρ; dashed curves: the same two assets at ρ = +1, 0 and −1. The shaded band is the long-only region 0 ≤ w ≤ 1; when the minimum lies outside it, the long-only optimum is the nearest corner (Section 7).</p>';
    var sp = host.querySelector("#ta-p"), sr = host.querySelector("#ta-rho"), sw = host.querySelector("#ta-w");
    var s1i = host.querySelector("#ta-s1"), s2i = host.querySelector("#ta-s2");
    var chart = host.querySelector(".ta-chart"), out = host.querySelector(".readout");

    function applyPreset() {
      var p = PRESETS[sp.value];
      if (!p) return;
      sr.value = p.rho; s1i.value = p.s1; s2i.value = p.s2;
    }
    function draw() {
      var rho = +sr.value, w = +sw.value, s1 = +s1i.value, s2 = +s2i.value;
      host.querySelector("#ta-rho-v").textContent = fmt(rho, "n2");
      host.querySelector("#ta-w-v").textContent = fmt(w, "pct0");
      host.querySelector("#ta-s1-v").textContent = fmt(s1, "pct1");
      host.querySelector("#ta-s2-v").textContent = fmt(s2, "pct1");
      var lo = -0.25, hi = 1.25, N = 150, xs = [], cur = [], pos = [], zer = [], neg = [];
      for (var i = 0; i <= N; i++) {
        var x = lo + (hi - lo) * i / N; xs.push(x);
        cur.push(vol(x, s1, s2, rho)); pos.push(vol(x, s1, s2, 1)); zer.push(vol(x, s1, s2, 0)); neg.push(vol(x, s1, s2, -1));
      }
      var c = rho * s1 * s2, den = s1 * s1 + s2 * s2 - 2 * c;
      var wstar = den > 1e-12 ? (s2 * s2 - c) / den : null;
      var vmin = den > 1e-12 ? (s1 * s1 * s2 * s2 - c * c) / den : null;
      var smin = vmin == null ? null : Math.sqrt(Math.max(vmin, 0));
      var sw0 = vol(w, s1, s2, rho);
      var ann = [{ type: "band", x0: 0, x1: 1 }, { type: "point", x: w, y: sw0, color: "1" }];
      if (wstar != null && wstar >= lo && wstar <= hi)
        ann.push({ type: "point", x: wstar, y: smin, color: "var(--ink)", label: "minimum", dx: 8, dy: 16 });
      B.lineChart(chart, {
        alt: "Portfolio volatility against the weight in asset 1", height: 290,
        x: { type: "num", fmt: "pct0", label: "Weight w in asset 1 (rest in asset 2)", tipLabel: "w = ", min: lo, max: hi },
        y: { type: "lin", fmt: "pct2", tfmt: "pct0", min: 0, max: Math.max(s1, s2) * 1.32 },
        series: [
          { name: "σp(w) at ρ = " + fmt(rho, "n2"), color: "1", x: xs, y: cur, width: 2.6 },
          { name: "ρ = +1", color: "var(--muted)", dash: true, x: xs, y: pos },
          { name: "ρ = 0", color: "3", dash: true, x: xs, y: zer },
          { name: "ρ = −1", color: "4", dash: true, x: xs, y: neg }],
        ann: ann
      });
      // long-only KKT: min V(w) s.t. 0 <= w <= 1; at a corner the multiplier is |V'(corner)|
      var avg = w * s1 + (1 - w) * s2, lam = vmin == null ? null : 2 * vmin, lo_txt;
      if (wstar == null) lo_txt = "not unique (σ₁ = σ₂, ρ = 1)";
      else if (wstar < 0) lo_txt = "corner w = 0, ν = " + fmt(2 * (c - s2 * s2), "n4");
      else if (wstar > 1) lo_txt = "corner w = 1, ν = " + fmt(2 * (c - s1 * s1), "n4");
      else lo_txt = "interior, slack";
      out.innerHTML =
        "<div><span>Inputs σ₁ · σ₂ · ρ</span><b>" + fmt(s1, "pct1") + " · " + fmt(s2, "pct1") + " · " + fmt(rho, "n2") + "</b></div>" +
        "<div><span>σp at w = " + fmt(w, "pct0") + "</span><b>" + fmt(sw0, "pct2") + "</b></div>" +
        "<div><span>Weighted average of σ</span><b>" + fmt(Math.abs(avg), "pct2") + "</b></div>" +
        "<div><span>Minimum-variance w*</span><b" + (wstar != null && (wstar < 0 || wstar > 1) ? ' class="bad"' : "") + ">" + (wstar == null ? "—" : fmt(wstar, "pct1")) + "</b></div>" +
        "<div><span>Minimum σp</span><b>" + (smin == null ? "—" : fmt(smin, "pct2")) + "</b></div>" +
        "<div><span>Multiplier λ = 2σ²min</span><b>" + (lam == null ? "—" : fmt(lam, "n4")) + "</b></div>" +
        "<div><span>Long-only optimum</span><b>" + lo_txt + "</b></div>";
    }
    sp.addEventListener("input", function () { applyPreset(); draw(); });
    [sr, s1i, s2i].forEach(function (el) { el.addEventListener("input", function () { sp.value = "custom"; draw(); }); });
    sw.addEventListener("input", draw);
    applyPreset();
    host.__redraw = draw; draw();
  };
})();
