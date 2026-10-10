/* LM4 interactive figure: growth curve of a binary bet, g(f) = p ln(1 + fb) + q ln(1 − fa) (gain b, loss a per unit staked). */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt;

  function controlsHTML(defs) {
    return '<div class="controls">' + defs.map(function (d) {
      return '<label for="' + d.id + '">' + d.label + ' <span class="v" id="' + d.id + '-v"></span>' +
        '<input type="range" id="' + d.id + '" min="' + d.min + '" max="' + d.max + '" step="' + d.step + '" value="' + d.value + '"></label>';
    }).join("") + "</div>";
  }

  function growth(f, p, b, a) { return p * Math.log1p(f * b) + (1 - p) * Math.log1p(-f * a); }

  /* zero-growth leverage: g(f*) > 0 and g -> -inf as f -> 1/a, so bisection on (f*, 1/a) always works */
  function zeroGrowth(fs, p, b, a) {
    var lo = fs, hi = (1 / a) * (1 - 1e-12);
    for (var i = 0; i < 80; i++) { var m = 0.5 * (lo + hi); if (growth(m, p, b, a) > 0) lo = m; else hi = m; }
    return 0.5 * (lo + hi);
  }

  function lev(v) {
    if (v == null || !isFinite(v)) return "—";
    var a = Math.abs(v);
    return (v < 0 ? "−" : "") + (a < 10 ? a.toFixed(2) : a.toFixed(1)) + "×";
  }
  function gfmt(span) { return span < 0.002 ? "bp" : span < 0.05 ? "pct2" : "pct1"; }

  B.widgets.kelly = function (host) {
    host.innerHTML = '<div class="w-head"><span class="w-title">Binary Kelly bet: growth per trade against position size</span><span class="w-tag">Interactive</span></div>' +
      controlsHTML([
        { id: "kw-p", label: "Win probability p", min: 0.3, max: 0.7, step: 0.005, value: 0.5 },
        { id: "kw-b", label: "Gain if right, b", min: 0.005, max: 0.1, step: 0.001, value: 0.02 },
        { id: "kw-a", label: "Loss if wrong, a", min: 0.005, max: 0.1, step: 0.001, value: 0.01 }
      ]) + '<div class="kw-chart"></div><div class="readout" aria-live="polite"></div>' +
      '<p class="w-note">Solid: exact growth per trade g(f) = p ln(1 + fb) + q ln(1 − fa) for a position of f times equity. ' +
      'Dashed: the quadratic model fμ − f²E[R²]/2. Dots: half Kelly, full Kelly f* = p/a − q/b and the zero-growth point. ' +
      'One loss at f = 1/a wipes out the account.</p>';
    var sp = host.querySelector("#kw-p"), sb = host.querySelector("#kw-b"), sa = host.querySelector("#kw-a");
    var chart = host.querySelector(".kw-chart"), out = host.querySelector(".readout");

    function draw() {
      var p = +sp.value, b = +sb.value, a = +sa.value, q = 1 - p;
      host.querySelector("#kw-p-v").textContent = p.toFixed(3);
      host.querySelector("#kw-b-v").textContent = "+" + fmt(b, "pct1");
      host.querySelector("#kw-a-v").textContent = "−" + fmt(a, "pct1");
      var fs = p / a - q / b, fmax = 1 / a, piBE = a / (a + b);
      var mu = p * b - q * a, m2 = p * b * b + q * a * a;
      var edge = fs > 1e-9, zeroEdge = Math.abs(fs) <= 1e-9, gs = null, f0 = null, xmax;
      if (edge) {
        gs = growth(fs, p, b, a);
        f0 = zeroGrowth(fs, p, b, a);
        xmax = Math.min(fmax, Math.max(1.3 * f0, 1.25 * fs));
      } else {
        xmax = 0.5 * fmax;
      }
      var N = 260, xs = [], ex = [], qd = [];
      for (var i = 0; i <= N; i++) {
        var f = xmax * i / N;
        if (f >= fmax) f = fmax * (1 - 1e-6);
        xs.push(f); ex.push(growth(f, p, b, a)); qd.push(f * mu - f * f * m2 / 2);
      }
      var ymin, ymax;
      if (edge) { ymax = 1.25 * gs; ymin = -0.85 * gs; }
      else { ymin = Math.min(-1e-4, growth(0.6 * xmax, p, b, a)); ymax = -0.15 * ymin; }
      var yf = gfmt(ymax - ymin);
      var ann = [];
      if (edge) {
        ann.push({ type: "vline", x: fs, label: "f* = " + lev(fs), anchor: fs > 0.7 * xmax ? "end" : "start" });
        ann.push({ type: "point", x: fs / 2, y: growth(fs / 2, p, b, a), color: "1", label: "½ Kelly", dx: -8, dy: -9, anchor: "end" });
        ann.push({ type: "point", x: fs, y: gs, color: "1" });
        ann.push({ type: "point", x: f0, y: 0, color: "1", label: "zero growth", dx: -8, dy: 16, anchor: "end" });
      }
      if (xmax >= fmax * 0.999) ann.push({ type: "vline", x: fmax * 0.999, label: "ruin: f = 1/a", anchor: "end", dy: 14 });
      B.lineChart(chart, {
        alt: "Growth per trade of a binary bet against position size", height: 290,
        x: { type: "num", fmt: "x1", label: "Position f (multiple of equity)", tipLabel: "f = ", min: 0, max: xmax },
        y: { type: "lin", fmt: yf, tfmt: yf, label: "Log growth per trade", min: ymin, max: ymax },
        series: [
          { name: "Exact g(f)", color: "1", x: xs, y: ex },
          { name: "Quadratic model", color: "2", dash: true, x: xs, y: qd }],
        ann: ann
      });
      var bet = "<div><span>Bet: p, b, a</span><b>" + p.toFixed(3) + ", +" + fmt(b, "pct1") + ", −" + fmt(a, "pct1") + "</b></div>";
      var ruin = "<div><span>One loss is ruin at f = 1/a</span><b>" + lev(fmax) + "</b></div>";
      if (!edge) {
        out.innerHTML = bet +
          "<div><span>Expected return per unit</span><b" + (zeroEdge ? "" : " class=\"bad\"") + ">" + fmt(mu, "pct2") + "</b></div>" +
          "<div><span>Break-even probability a/(a+b)</span><b>" + piBE.toFixed(3) + "</b></div>" +
          (zeroEdge ? "<div><span>Kelly position</span><b>0× (no edge: g′(0) = 0, an interior optimum)</b></div>"
                    : "<div><span>Kelly position</span><b class=\"bad\">" + lev(fs) + " → long-only corner f = 0</b></div>") + ruin;
        return;
      }
      var half = growth(fs / 2, p, b, a) / gs;
      out.innerHTML = bet +
        "<div><span>Kelly position f*</span><b>" + lev(fs) + " equity</b></div>" +
        "<div><span>Risk per losing trade f*a</span><b" + (fs * a > 0.2 ? ' class="bad"' : "") + ">" + fmt(fs * a, "pct1") + " of equity</b></div>" +
        "<div><span>Growth per trade at f*</span><b>" + fmt(gs, gs < 0.002 ? "bp" : "pct2") + "</b></div>" +
        "<div><span>Half Kelly keeps</span><b>" + fmt(half, "pct1") + " of it</b></div>" +
        "<div><span>Zero growth at</span><b>" + lev(f0) + " (" + (f0 / fs).toFixed(2) + " f*)</b></div>" +
        "<div><span>Break-even probability</span><b>" + piBE.toFixed(3) + "</b></div>" + ruin;
    }
    [sp, sb, sa].forEach(function (c) { c.addEventListener("input", draw); });
    host.__redraw = draw; draw();
  };
})();
