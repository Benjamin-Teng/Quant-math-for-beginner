/* LM24 interactive figure: prior, likelihood and posterior of TAIEX's annual mean, and the Bayes Kelly bet.
   Data: the "widget" block of the chart JSON lm24-posterior, inlined in the page by the build
   (<script type="application/json" id="chart-lm24-posterior">), written by data/lm24_charts.py: TR23's annual mean
   A Rbar, its annualized volatility sqrt(A) s, its span in years, the plug-in fraction fhat = Rbar / s^2 and
   Phi^{-1}(0.975). Model (24.3) on the annual scale: the standard error of the annual mean is sqrt(A) s / sqrt(years);
   the data's weight c = (A sigma0)^2 / ((A sigma0)^2 + SE^2); the posterior mean A mu0 + c (A Rbar - A mu0); the
   posterior SD sqrt(c) SE; Pr(mu <= 0 | data) = Phi(-mean / SD); the Bayes fraction (24.5) = posterior mean / (A s^2),
   and its ratio to fhat = posterior mean / (A Rbar). TAIEX's mean and volatility stay fixed while the years change: a
   hypothetical sample. Nothing is simulated. The initial state is the third row of the module's table of priors. */
(function () {
  "use strict";
  var B = window.Book, fmt = B.fmt, D = B.dist;

  function pts(v) { return fmt(v * 100, "n2"); }          // a fraction of 1 as percentage points, 3.89
  function prob(p) { return p < 1e-3 ? fmt(p, "sci1") : fmt(p, "n4"); }

  B.widgets.posterior = function (host) {
    var src = document.getElementById("chart-lm24-posterior");
    if (!src) { host.innerHTML = '<p class="w-note">The data for this figure are not on the page.</p>'; return; }
    var W = JSON.parse(src.textContent).widget, z = W.z975;
    var xs = [];
    for (var k = 0; k <= 240; k++) xs.push(-0.20 + 0.0025 * k);

    host.innerHTML = '<div class="w-head"><span class="w-title">Prior, data and the Bayes bet</span>' +
      '<span class="w-tag">Interactive</span></div>';
    var ctl = B.controls(host, [
      { id: "po-s0", key: "s0", label: "Prior SD of the annual mean (points)", min: 0.5, max: 30, step: 0.5,
        value: W.init.s0, fmt: function (v) { return v.toFixed(1); } },
      { id: "po-mu0", key: "mu0", label: "Prior mean (% a year)", min: -10, max: 20, step: 1, value: W.init.mu0,
        fmt: function (v) { return (v > 0 ? "+" : "") + v.toFixed(0) + "%"; } },
      { id: "po-yr", key: "years", label: "Years of data", min: 1, max: 100, step: "any", value: W.init.years,
        fmt: function (v) { return v.toFixed(2); } }
    ], draw);
    var chart = document.createElement("div"), out = document.createElement("div"), note = document.createElement("p");
    out.className = "readout"; out.setAttribute("aria-live", "polite"); note.className = "w-note";
    host.appendChild(chart); host.appendChild(out); host.appendChild(note);
    note.textContent = "Model (24.3) on the annual scale, with TAIEX's annual mean " + fmt(W.ARbar, "pct2") +
      " and volatility " + fmt(W.vol, "pct2") + " (total-return index, " + W.years.toFixed(2) + " years) held fixed " +
      "while the years change: a hypothetical sample. The likelihood is drawn with unit area. The Bayes fraction is " +
      "(24.5)'s posterior mean divided by A s²; it equals c times the plug-in " + fmt(W.fhat, "n2") +
      " only when the prior mean is 0. In-sample model results, not advice.";

    function dens(x, m, sd) { return 0.01 * D.phi((x - m) / sd) / sd; }   // per percentage point

    function draw(v) {
      var s0 = v.s0 / 100, mu0 = v.mu0 / 100, yrs = v.years;
      var se = W.vol / Math.sqrt(yrs), c = s0 * s0 / (s0 * s0 + se * se);
      var pm = mu0 + c * (W.ARbar - mu0), psd = Math.sqrt(c) * se;
      var prior = [], like = [], post = [], top = 0;
      xs.forEach(function (x) {
        var a = dens(x, mu0, s0), b = dens(x, W.ARbar, se), p = dens(x, pm, psd);
        prior.push(a); like.push(b); post.push(p);
        top = Math.max(top, a, b, p);
      });
      var ymax = Math.ceil(top * 1.1 * 50) / 50;
      B.chart(chart, {
        alt: "Prior, likelihood and posterior of TAIEX's annual mean for a prior SD of " + v.s0.toFixed(1) +
          " points centred at " + v.mu0.toFixed(0) + "% and " + yrs.toFixed(2) + " years of data: posterior mean " +
          fmt(pm, "pct1"),
        height: 300,
        x: { type: "num", fmt: "pct2", tfmt: "pct0", label: "Annual mean return (TAIEX total-return index)", tipLabel: "",
             min: -0.20, max: 0.40, ticks: [-0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4], values: xs },
        y: { type: "lin", fmt: "n4", tfmt: "n2", label: "Density per percentage point", min: 0, max: ymax },
        series: [
          { name: "Prior", color: "3", dash: true, y: prior },
          { name: "Likelihood (unit area)", color: "2", y: like },
          { name: "Posterior", color: "1", y: post }
        ],
        ann: [{ type: "vline", x: pm, dash: true, label: "posterior mean " + fmt(pm, "pct1") }]
      });
      var fb = pm / (W.vol * W.vol);
      out.innerHTML =
        "<div><span>Standard error of the annual mean (points)</span><b>" + pts(se) + "</b></div>" +
        "<div><span>Data's weight c</span><b>" + fmt(c, "n3") + "</b></div>" +
        "<div><span>Posterior mean ± SD</span><b>" + fmt(pm, "pct1") + " ± " + fmt(psd * 100, "n1") + "</b></div>" +
        "<div><span>95% credible interval</span><b>" + fmt(pm - z * psd, "pct1") + " to " + fmt(pm + z * psd, "pct1") + "</b></div>" +
        "<div><span>Pr(μ ≤ 0 | data)</span><b>" + prob(D.Phi(-pm / psd)) + "</b></div>" +
        "<div><span>Bayes fraction · ratio to the plug-in " + fmt(W.fhat, "n2") + "</span><b>" + fmt(fb, "n2") +
          " · " + fmt(pm / W.ARbar, "n3") + "</b></div>";
    }
    host.__redraw = function () { draw(ctl.values()); };
    ctl.fire();
  };
})();
