/* LM13 interactive figure: from a hit rate to a conditional probability, Bayes' rule drawn as one square per day.
   Data: the "widget" block of the chart JSON lm13-bayes, inlined in the page by the build
   (<script type="application/json" id="chart-lm13-bayes">), written by data/lm13_charts.py: the 5,848 days of TR23's
   pair space, the falls of 3% or more (A), the days after a move of 2% or more either way (B) and the days with both.
   The preset "TR23 counts" uses the exact fractions of those counts; the sliders move in steps of 0.01 percentage
   points. Away from the preset, each square count is the number of days times its probability, rounded to whole
   days by largest remainder. No randomness. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt, NS = "http://www.w3.org/2000/svg";
  var UNDEF = "— (undefined)";

  function ok(v) { return v != null && isFinite(v); }
  function pct(v) { return ok(v) ? fmt(v, "pct2") : UNDEF; }
  function sig(v, k) {   // k significant digits, trailing zeros kept; whole numbers from 100,000
    if (!ok(v)) return UNDEF;
    return v >= 1e5 ? fmt(v, "n0") : Number(v).toPrecision(k);
  }
  function counts(n, p) {   // largest remainder: whole days that sum to n, for probabilities p that sum to 1
    var raw = p.map(function (x) { return n * x; }), fl = raw.map(Math.floor), left = n;
    fl.forEach(function (x) { left -= x; });
    var order = raw.map(function (x, i) { return i; }).sort(function (a, b) { return (raw[b] - fl[b]) - (raw[a] - fl[a]) || a - b; });
    for (var i = 0; i < left; i++) fl[order[i % order.length]] += 1;
    return fl;
  }

  B.widgets.bayes = function (host) {
    var src = document.getElementById("chart-lm13-bayes");
    if (!src) { host.innerHTML = '<p class="w-note">The data for this figure are not on the page.</p>'; return; }
    var W = JSON.parse(src.textContent).widget;
    var exact = { base: W.A / W.N, hit: W.AB / W.A, fa: (W.B - W.AB) / (W.N - W.A) };
    var snapped = { base: 0.0185, hit: 0.2963, fa: 0.0796 };
    var preset = true;
    // the live value beside a slider: the exact fraction to four significant digits in the preset, else the slider
    function label(key) { return function (v) { return preset ? (100 * exact[key]).toPrecision(4) + "%" : fmt(v, "pct2"); }; }
    // categories in the order the squares are laid out: the days after a big move first
    var CATS = [
      { name: "Fall after a big move", style: "fill:var(--series-1)" },
      { name: "Big move, no fall", style: "fill:var(--series-1);fill-opacity:0.5" },
      { name: "Fall after a smaller move", style: "fill:var(--series-2)" },
      { name: "Neither", style: "fill:var(--rule)" }];

    host.innerHTML = '<div class="w-head"><span class="w-title">From a hit rate to a conditional probability</span>' +
      '<span class="w-tag">Interactive</span></div>';
    var ctl = B.controls(host, [
      { id: "by-base", key: "base", label: "Base rate Pr(A): fall today", min: 0.001, max: 0.5, step: 0.0001, value: snapped.base, fmt: label("base") },
      { id: "by-hit", key: "hit", label: "Hit rate Pr(B | A)", min: 0, max: 1, step: 0.0001, value: snapped.hit, fmt: label("hit") },
      { id: "by-fa", key: "fa", label: "False-alarm rate Pr(B | not A)", min: 0, max: 1, step: 0.0001, value: snapped.fa, fmt: label("fa") },
      { type: "select", id: "by-days", key: "days", label: "Days in the picture",
        options: [["5848", "The sample's 5,848 days"], ["1000", "1,000 days"]], value: "5848" },
      { type: "button", id: "by-reset", label: "TR23 counts" }
    ], draw);
    var pic = document.createElement("div"), key = document.createElement("div"), out = document.createElement("div"), note = document.createElement("p");
    pic.className = "by-pic"; key.className = "w-note by-key"; out.className = "readout"; out.setAttribute("aria-live", "polite"); note.className = "w-note";
    host.appendChild(pic); host.appendChild(key); host.appendChild(out); host.appendChild(note);

    function setSlider(id, v) { host.querySelector("#" + id).value = v; }
    function picture(n, sq) {
      var cols = n === 5848 ? 86 : 40, rows = Math.ceil(n / cols), s = 0.8, d = CATS.map(function () { return ""; }), k = 0;
      sq.forEach(function (c, ci) {
        for (var j = 0; j < c; j++, k++) d[ci] += "M" + (k % cols) + " " + Math.floor(k / cols) + "h" + s + "v" + s + "h-" + s + "z";
      });
      var svg = '<svg xmlns="' + NS + '" viewBox="-0.1 -0.1 ' + (cols + 0.1) + " " + (rows + 0.1) + '" role="img" aria-label="' +
        n.toLocaleString("en-US") + " squares, one per day: " + CATS.map(function (c, i) { return c.name.toLowerCase() + " " + sq[i]; }).join(", ") +
        '" style="display:block;width:100%;max-width:' + (n === 5848 ? 520 : 480) + 'px;height:auto;margin:0.3rem 0">';
      d.forEach(function (p, i) { if (p) svg += '<path d="' + p + '" style="' + CATS[i].style + '"></path>'; });
      pic.innerHTML = svg + "</svg>";
      key.innerHTML = CATS.map(function (c, i) {
        return '<span style="display:inline-block;margin-right:1rem;white-space:nowrap"><svg width="11" height="11" viewBox="0 0 1 1" ' +
          'style="vertical-align:-1px;margin-right:0.3rem"><rect width="1" height="1" style="' + c.style + '"></rect></svg>' +
          c.name + ": " + sq[i].toLocaleString("en-US") + "</span>";
      }).join("");
    }

    function draw(v, id) {
      if (id === "by-reset") { preset = true; setSlider("by-base", snapped.base); setSlider("by-hit", snapped.hit); setSlider("by-fa", snapped.fa); }
      else if (id === "by-base" || id === "by-hit" || id === "by-fa") preset = false;
      ["base", "hit", "fa"].forEach(function (k) { host.querySelector("#by-" + k + "-v").textContent = label(k)(v[k]); });
      var b = preset ? exact.base : v.base, h = preset ? exact.hit : v.hit, a = preset ? exact.fa : v.fa, n = +v.days;
      var pAB = b * h, pAnotB = b * (1 - h), pBnotA = (1 - b) * a, pNeither = (1 - b) * (1 - a);
      var pB = pAB + pBnotA, pNotB = pAnotB + pNeither;
      var postA = pB > 0 ? pAB / pB : NaN, postNotB = pNotB > 0 ? pAnotB / pNotB : NaN;
      var lr = a > 0 ? h / a : NaN, prior = b / (1 - b), post = a > 0 ? prior * lr : NaN;
      // squares in the layout order: fall after a big move, big move without a fall, fall after a smaller move, neither
      var sq = preset && n === W.N ? [W.AB, W.B - W.AB, W.A - W.AB, W.N - W.A - W.B + W.AB]
                                   : counts(n, [pAB, pBnotA, pAnotB, pNeither]);
      picture(n, sq);
      var inB = sq[0] + sq[1];
      out.innerHTML =
        "<div><span>Pr(B): big move yesterday</span><b>" + pct(pB) + "</b></div>" +
        "<div><span>Pr(A | B): fall after a big move</span><b>" + pct(postA) + "</b></div>" +
        "<div><span>Pr(A | not B): fall after a smaller move</span><b>" + pct(postNotB) + "</b></div>" +
        "<div><span>Pr(A | B) ÷ " + (preset ? "108/5,848" : "Pr(A)") + "</span><b>" + (ok(postA) ? fmt(postA / b, "n2") : UNDEF) + "</b></div>" +
        "<div><span>Likelihood ratio, hit ÷ false alarm</span><b>" + sig(lr, 5) + "</b></div>" +
        "<div><span>Prior odds × ratio = posterior odds</span><b>" + sig(prior, 5) + " × " + sig(lr, 5) + " = " + sig(post, 4) + "</b></div>" +
        "<div><span>In the picture: falls among the big-move days</span><b>" + sq[0] + " of " + inB.toLocaleString("en-US") +
          (inB > 0 ? ", " + fmt(sq[0] / inB, "pct1") : "") + "</b></div>";
      note.textContent = (preset ? "Preset: TR23's exact rates 108/5,848, 32/108 and 457/5,740 on the pair space (descriptive). " :
        "Hypothetical rates; a slider moves in steps of 0.01 percentage points. ") +
        (n === W.N && preset ? "The squares are the sample's days. " : "The squares are whole days, rounded by largest remainder, so their share can differ from the readout. ") +
        "A readout whose denominator is 0 is undefined.";
    }
    host.__redraw = function () { ctl.fire(); };
    ctl.fire();
  };
})();
