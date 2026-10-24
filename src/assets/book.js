/* From Calculus to Kelly — shared page behaviour + a small SVG chart kit.
   No dependencies. Every chart reads its colours from CSS tokens. */
(function () {
  "use strict";
  var Book = (window.Book = window.Book || {});
  Book.widgets = Book.widgets || {};

  /* ---------------- storage (per viewer, best effort) ---------------- */
  var store = {
    get: function (k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { window.localStorage.setItem(k, v); } catch (e) {} }
  };
  Book.store = store;

  /* ---------------- theme (dark / light) ---------------- */
  // The script in <head> sets data-theme before the first paint (the reader's saved choice, else the system's) and
  // runs the switch until this file has loaded. A click saves an explicit choice; without one the page follows the
  // system. The theme changes at once: the switch's own animation shows the change (a whole-page cross-fade froze
  // the KaTeX-heavy module pages and swallowed quick second clicks).
  var THEME_KEY = "ftck-theme", root = document.documentElement, chosen = null;   // chosen: if storage is blocked
  function mq(q) { return window.matchMedia ? window.matchMedia(q) : null; }
  function systemTheme() { var m = mq("(prefers-color-scheme: dark)"); return m && m.matches ? "dark" : "light"; }
  function savedTheme() { var s = chosen || store.get(THEME_KEY); return s === "light" || s === "dark" ? s : null; }
  function theme() { return root.getAttribute("data-theme") || savedTheme() || systemTheme(); }
  function syncToggles() {
    var light = theme() === "light";
    document.querySelectorAll(".theme-toggle").forEach(function (b) {
      b.setAttribute("aria-checked", light ? "true" : "false");
      b.title = light ? "Switch to the dark theme" : "Switch to the light theme";
    });
  }
  function setTheme(t) {
    if (root.getAttribute("data-theme") !== t) root.setAttribute("data-theme", t);
    syncToggles();
  }
  function initTheme() {
    window.__ftckTheme = true;                       // the head script's early click handler steps aside
    var early = window.__ftckEarly;                  // a choice clicked before this file loaded
    if ((early === "light" || early === "dark") && store.get(THEME_KEY) !== early) chosen = early;
    if (!root.hasAttribute("data-theme")) root.setAttribute("data-theme", savedTheme() || systemTheme());
    syncToggles();
    document.querySelectorAll(".theme-toggle").forEach(function (b) {
      b.addEventListener("click", function () {
        var t = theme() === "light" ? "dark" : "light";
        store.set(THEME_KEY, t);
        chosen = store.get(THEME_KEY) === t ? null : t;   // memory only when storage refuses the write
        setTheme(t);
      });
    });
    var resync = function () { setTheme(savedTheme() || systemTheme()); };
    var sys = mq("(prefers-color-scheme: dark)");
    if (sys) {
      var follow = function () { if (!savedTheme()) setTheme(systemTheme()); };
      if (sys.addEventListener) sys.addEventListener("change", follow); else if (sys.addListener) sys.addListener(follow);
    }
    // Back/Forward restores a page with its old theme, and another tab may change the choice meanwhile
    window.addEventListener("pageshow", function (e) { if (e.persisted) resync(); });
    window.addEventListener("storage", function (e) { if (e.key === THEME_KEY || e.key === null) { chosen = null; resync(); } });
  }
  Book.setTheme = setTheme;

  /* ---------------- number formatting ---------------- */
  function fmt(v, f) {
    if (v == null || !isFinite(v)) return "—";
    var neg = v < 0, a = Math.abs(v), s;
    switch (f) {
      case "pct0": s = (a * 100).toFixed(0) + "%"; break;
      case "pct1": s = (a * 100).toFixed(1) + "%"; break;
      case "pct2": s = (a * 100).toFixed(2) + "%"; break;
      case "pct3": s = (a * 100).toFixed(3) + "%"; break;
      case "bp": s = (a * 10000).toFixed(1) + " bp"; break;
      case "x0": s = a.toFixed(0) + "×"; break;
      case "x1": s = a.toFixed(a < 10 ? 1 : 0) + "×"; break;
      case "x2": s = a.toFixed(2) + "×"; break;
      case "n0": s = a.toLocaleString("en-US", { maximumFractionDigits: 0 }); break;
      case "n1": s = a.toFixed(1); break;
      case "n2": s = a.toFixed(2); break;
      case "n3": s = a.toFixed(3); break;
      case "n4": s = a.toFixed(4); break;
      case "n5": s = a.toFixed(5); break;
      case "n6": s = a.toFixed(6); break;
      // 2.00e−5: the chart font (Archivo, latin subset) has ¹ ² ³ but not ⁰ ⁴–⁹ ⁻, so no superscript exponents
      case "sci0": case "sci1": case "sci2": case "sci3": s = a === 0 ? "0" : expo(a, +f.charAt(3)); break;
      // k significant figures, trailing zeros kept as by printf's %#g (1.20, 0.00100, 0.0) and thousands separated as
      // by n0; outside 1e−4 <= |v| < 1e6, after rounding, the same digits in the sci form (1.23e6)
      case "sig2": case "sig3": case "sig4":
        var k = +f.charAt(3), e = a === 0 ? 0 : +a.toExponential(k - 1).split("e")[1];
        s = e >= -4 && e < 6 ? a.toLocaleString("en-US", { minimumSignificantDigits: k, maximumSignificantDigits: k }) : expo(a, k - 1);
        break;
      default: s = String(Math.round(a * 1e6) / 1e6);
    }
    return (neg ? "−" : "") + s;
  }
  function expo(a, d) { return a.toExponential(d).replace("e+", "e").replace("e-", "e−"); }   // 2.00e−5, 1.2e6
  Book.fmt = fmt;
  var MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  function fmtDate(t, mode) {
    var d = new Date(t);
    if (mode === "year") return String(d.getUTCFullYear());
    if (mode === "month") return MONTHS[d.getUTCMonth()];
    if (mode === "monthyear") return MONTHS[d.getUTCMonth()] + " " + d.getUTCFullYear();
    var m = String(d.getUTCMonth() + 1).padStart(2, "0"), dd = String(d.getUTCDate()).padStart(2, "0");
    return d.getUTCFullYear() + "-" + m + "-" + dd;
  }

  /* ---------------- scales & ticks ---------------- */
  // the finest step each tick format can print; 2.5 units of it, or a finer step, would print rounded labels
  // (0.025 in pct0 as "3%"), so niceStep takes 2 units, or the format's own unit, instead
  var RES = { pct0: 1e-2, pct1: 1e-3, pct2: 1e-4, pct3: 1e-5, bp: 1e-5, x0: 1, x1: 0.1, x2: 1e-2,
              n0: 1, n1: 0.1, n2: 1e-2, n3: 1e-3, n4: 1e-4, n5: 1e-5, n6: 1e-6 };
  // sci and sig print digits relative to the size of the number: the coarsest is that of the largest tick, |big|.
  // On a range narrow for those digits, or one that straddles a decade (9.6e−6 to 1.04e−5 in sci1), the ticks can
  // collapse to a single label: give such an axis more digits or a tfmt.
  function tickRes(f, big) {
    var k = /^(sci|sig)(\d)$/.exec(f || "");
    if (!k) return RES[f];
    return big > 0 && isFinite(big) ? Math.pow(10, Math.floor(Math.log10(big)) - +k[2] + (k[1] === "sig" ? 1 : 0)) : undefined;
  }
  function niceStep(span, n, res) {
    var raw = span / Math.max(1, n), p = Math.pow(10, Math.floor(Math.log10(raw))), r = raw / p;
    var st = (r <= 1 ? 1 : r <= 2 ? 2 : r <= 2.5 ? 2.5 : r <= 5 ? 5 : 10) * p;
    if (res && Math.abs(st / res - Math.round(st / res)) > 1e-6) st = 2 * p;
    if (res && st < res * (1 - 1e-9)) st = res;
    return st;
  }
  function linTicks(lo, hi, n, f) {
    var big = Math.max(Math.abs(lo), Math.abs(hi)), res = f === "x1" && big >= 10 ? 1 : tickRes(f, big);   // x1 prints whole numbers from 10
    var st = niceStep(hi - lo, n, res), t = [], v = Math.ceil(lo / st - 1e-9) * st;
    for (; v <= hi + st * 1e-9; v += st) t.push(Math.abs(v) < st * 1e-9 ? 0 : v);
    return t;
  }
  function logTicks(lo, hi) {
    var t = [], base = [1, 2, 5];
    if (!(lo > 0 && hi < Infinity)) return t;   // a log axis needs a positive, finite range (else the loop never ends)
    for (var e = Math.floor(Math.log10(lo)) - 1; e <= Math.ceil(Math.log10(hi)) + 1; e++)
      for (var i = 0; i < 3; i++) { var v = base[i] * Math.pow(10, e); if (v >= lo * 0.999 && v <= hi * 1.001) t.push(v); }
    if (t.length > 8) t = t.filter(function (v) { return Math.abs(Math.log10(v) - Math.round(Math.log10(v))) < 1e-9; });
    return t;
  }
  function yearTicks(lo, hi, maxN) {
    var a = new Date(lo).getUTCFullYear(), b = new Date(hi).getUTCFullYear(), t = [];
    var step = Math.max(1, Math.ceil((b - a + 1) / maxN));
    for (var y = a; y <= b + 1; y += step) { var ts = Date.UTC(y, 0, 1); if (ts >= lo && ts <= hi) t.push(ts); }
    return t;
  }
  function monthTicks(lo, hi, maxN) {   // first days of months, every 1, 2, 3 or 6 months, aligned to January
    var d = new Date(lo), y = d.getUTCFullYear(), mo = d.getUTCMonth(), all = [];
    for (var ts = Date.UTC(y, mo, 1); ts <= hi; ts = Date.UTC(y, ++mo, 1)) if (ts >= lo) all.push(ts);
    var steps = [1, 2, 3, 6], t = all;
    for (var i = 0; i < steps.length; i++) {
      t = all.filter(function (v) { return new Date(v).getUTCMonth() % steps[i] === 0; });
      if (t.length <= maxN) break;
    }
    return t;
  }
  // a date axis shows years when at least three year starts fall inside it, else month starts, else its two ends
  function dateTicks(lo, hi, narrow) {
    var starts = 0;
    for (var y = new Date(lo).getUTCFullYear(); Date.UTC(y, 0, 1) <= hi; y++) if (Date.UTC(y, 0, 1) >= lo) starts++;
    if (starts >= 3) return { t: yearTicks(lo, hi, narrow ? 5 : 12), mode: "year" };
    var t = monthTicks(lo, hi, narrow ? 4 : 8);
    if (t.length >= 2) return { t: t, mode: "month" };
    return { t: [lo, hi], mode: "day" };
  }

  var NS = "http://www.w3.org/2000/svg";
  function el(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) if (attrs[k] != null) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function color(c) { return /^\d$/.test(String(c)) ? "var(--series-" + c + ")" : c; }

  /* ---------------- line chart ---------------- */
  // spec: {x:{type:'num'|'date'|'log',label,fmt,tfmt,min,max,ticks,tickLabels,values}, y:{type:'lin'|'log',label,fmt,tfmt,min,max,ticks},
  //        series:[{name,color,dash,area,width,fmt,step,quiet,opacity,x:[],y:[]}], ann:[{type:'vline'|'hline'|'point'|'band',dash,...}], height}
  // x.values: one x array for every series without its own x. A log x axis, like a log y axis, ignores x <= 0.
  // step: a post-step line, y[i] holding from x[i] to x[i+1] (histograms on bin edges, distribution functions).
  // A band series has lo and hi instead of y: the region between them is filled (opacity 0.18) under every line.
  // quiet: a thin translucent line (opacity 0.35) with no legend entry, tooltip row, hover dot or end label, for dozens
  // of simulated paths. Bands are drawn first, then quiet lines, then the other lines, each group in the given order.
  function isBand(s) { return !!(s.lo && s.hi); }
  // one closed outline per run of points where x, lo and hi all exist: along hi, back along lo (line and scatter bands);
  // xok, when given, leaves out the x it rejects
  function bandOutline(xa, lo, hi, pt, xok) {
    var d = "", run = [], fin = function (v) { return v != null && isFinite(v); };
    for (var i = 0; i <= xa.length; i++) {
      if (i < xa.length && fin(xa[i]) && (!xok || xok(xa[i])) && fin(lo[i]) && fin(hi[i])) { run.push(i); continue; }
      if (run.length > 1) d += "M" + run.map(function (j) { return pt(xa[j], hi[j]); }).join("L") + "L" + run.reverse().map(function (j) { return pt(xa[j], lo[j]); }).join("L") + "Z";
      run = [];
    }
    return d;
  }
  Book.lineChart = function (host, spec) {
    host.innerHTML = "";
    host.classList.add("chart");
    var xs0 = spec.x.values, series = (spec.series || []).map(function (s) { return s.x || !xs0 ? s : Object.assign({}, s, { x: xs0 }); });
    var keyed = series.filter(function (s) { return !s.quiet; });   // the series with a legend entry and a tooltip row
    if (keyed.length > 1 || spec.legend) {
      var lg = document.createElement("div"); lg.className = "legend";
      keyed.forEach(function (s) {
        var k = document.createElement("span"); k.className = "key";
        var sw = document.createElement("i"); sw.className = "sw" + (isBand(s) ? " band" : s.dash ? " dash" : "");
        sw.style.background = color(s.color); sw.style.color = color(s.color);
        if (isBand(s)) sw.style.opacity = Math.min(1, 1.6 * (s.opacity != null ? s.opacity : 0.18));   // a small swatch needs more ink than a wide band
        var nm = document.createElement("span"); nm.innerHTML = rich(s.name == null ? "" : s.name);   // a_1 / A^T as sub- and superscripts, as in the other chart types
        k.appendChild(sw); k.appendChild(nm); lg.appendChild(k);
      });
      host.appendChild(lg);
    }
    var wrap = document.createElement("div"); wrap.style.position = "relative"; host.appendChild(wrap);
    var tip = document.createElement("div"); tip.className = "tip"; tip.hidden = true; wrap.appendChild(tip);
    var W = Math.max(280, Math.round(host.clientWidth || 640)), H = spec.height || Math.round(Math.min(360, Math.max(220, W * 0.52)));
    var narrow = W < 460;
    var m = { l: narrow ? 46 : 58, r: spec.endLabels && !narrow ? (spec.endMargin || 96) : 16, t: 12, b: spec.x.label ? 44 : 30 };
    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, role: "img", "aria-label": spec.alt || spec.title || null }, wrap);
    // data range, in a loop (Math.min.apply fails on very long argument lists, such as dozens of quiet paths). A step
    // also reaches x[i+1]; on a log axis a value <= 0 does not count towards the y range (it would give no decades)
    var isLog = spec.y.type === "log", xLog = spec.x.type === "log";
    var xok = function (v) { return !xLog || v > 0; };
    var xmn = Infinity, xmx = -Infinity, ymn = Infinity, ymx = -Infinity;
    series.forEach(function (s) {
      var band = isBand(s), lo = band ? s.lo : s.y, hi = band ? s.hi : s.y, n = s.x.length;
      for (var i = 0; i < n; i++) {
        var a = lo[i], b = hi[i];
        if (a == null || !isFinite(a) || b == null || !isFinite(b) || !xok(s.x[i])) continue;
        xmn = Math.min(xmn, s.x[i]); xmx = Math.max(xmx, s.x[i]);
        if (s.step && i + 1 < n) { xmn = Math.min(xmn, s.x[i + 1]); xmx = Math.max(xmx, s.x[i + 1]); }
        if (!isLog || a > 0) { ymn = Math.min(ymn, a); ymx = Math.max(ymx, a); }
        if (!isLog || b > 0) { ymn = Math.min(ymn, b); ymx = Math.max(ymx, b); }
      }
    });
    var x0 = spec.x.min != null ? spec.x.min : xmn, x1 = spec.x.max != null ? spec.x.max : xmx;
    if (xLog) { if (!(x0 > 0)) x0 = xmn; if (!(x1 > x0)) x1 = Math.max(xmx, x0); }   // a log x axis needs 0 < x0 <= x1
    var y0 = spec.y.min != null ? spec.y.min : ymn, y1 = spec.y.max != null ? spec.y.max : ymx;
    if (!isLog && spec.y.min == null) { var pad = (y1 - y0) * 0.06 || 1; y0 -= pad; if (spec.y.max == null) y1 += pad; }
    if (isLog) { y0 = y0 * 0.9; y1 = y1 * 1.1; }
    var X = xLog
      ? function (v) { return m.l + (Math.log(v) - Math.log(x0)) / (Math.log(x1) - Math.log(x0) || 1) * (W - m.l - m.r); }
      : function (v) { return m.l + (v - x0) / (x1 - x0 || 1) * (W - m.l - m.r); };
    var Y = isLog
      ? function (v) { return H - m.b - (Math.log(v) - Math.log(y0)) / (Math.log(y1) - Math.log(y0)) * (H - m.t - m.b); }
      : function (v) { return H - m.b - (v - y0) / (y1 - y0 || 1) * (H - m.t - m.b); };
    // bands
    (spec.ann || []).forEach(function (a) {
      if (a.type === "band") el("rect", { class: "band", x: X(a.x0), y: m.t, width: Math.max(0, X(a.x1) - X(a.x0)), height: H - m.t - m.b }, svg);
    });
    // grid + y ticks
    var g = el("g", { class: "grid" }, svg), ax = el("g", { class: "axis" }, svg);
    var yt = spec.y.ticks || (isLog ? logTicks(y0, y1) : linTicks(y0, y1, narrow ? 4 : 6, spec.y.tfmt || spec.y.fmt));
    yt.forEach(function (v) {
      if (v < y0 || v > y1) return;
      el("line", { x1: m.l, x2: W - m.r, y1: Y(v), y2: Y(v) }, g);
      var t = el("text", { x: m.l - 8, y: Y(v) + 3.5, "text-anchor": "end" }, svg); t.textContent = fmt(v, spec.y.tfmt || spec.y.fmt);
    });
    if (!isLog && y0 < 0 && y1 > 0) el("line", { class: "zero", x1: m.l, x2: W - m.r, y1: Y(0), y2: Y(0) }, svg);
    var dt = spec.x.type === "date" ? dateTicks(x0, x1, narrow) : null;
    var xtf = spec.x.tfmt || spec.x.fmt;   // tick labels; the tooltip header keeps x.fmt
    var xt = dt ? dt.t : (spec.x.ticks || (xLog ? logTicks(x0, x1) : linTicks(x0, x1, narrow ? 4 : 7, xtf)));
    var xl = !dt && spec.x.ticks && spec.x.tickLabels;   // optional text for each of x.ticks
    el("line", { x1: m.l, x2: W - m.r, y1: H - m.b, y2: H - m.b }, ax);
    xt.forEach(function (v, i) {
      el("line", { x1: X(v), x2: X(v), y1: H - m.b, y2: H - m.b + 4 }, ax);
      var t = el("text", { x: X(v), y: H - m.b + 16, "text-anchor": "middle" }, svg);
      if (dt && dt.mode === "month") t.textContent = fmtDate(v, i === 0 || new Date(v).getUTCMonth() === 0 ? "monthyear" : "month");
      else if (dt) t.textContent = fmtDate(v, dt.mode === "year" ? "year" : null);
      else t.textContent = xl && xl[i] != null ? xl[i] : fmt(v, xtf);
      // on a log axis (often ticked at its right end) the last label moves left until it ends at the svg's right edge
      // (6.2 px a character); ending it at its tick instead would run it into the label before on a phone
      if (xLog && i === xt.length - 1 && v <= x1 * 1.001) t.setAttribute("x", Math.min(X(v), W - t.textContent.length * 3.1));
    });
    if (spec.x.label) { var tx = el("text", { class: "ttl-y", x: m.l + (W - m.l - m.r) / 2, y: H - 6, "text-anchor": "middle" }, svg); setText(tx, spec.x.label); }
    if (spec.y.label) { var ty = el("text", { class: "ttl-y", x: m.l, y: m.t - 2 + 0, "text-anchor": "start" }, svg); ty.textContent = ""; host.setAttribute("data-ylabel", spec.y.label); }
    // series
    var sg = el("g", { class: "series" }, svg);
    var cy = function (v) { return Y(Math.min(Math.max(v, isLog ? y0 : y0 - (y1 - y0)), y1 + (y1 - y0))).toFixed(1); };
    var ok = function (v) { return v != null && isFinite(v) && !(isLog && v <= 0); };
    // a step series turns into vertices (x0,y0) (x1,y0) (x1,y1) (x2,y1) ...: a missing y[i+1] still ends step i at x[i+1].
    // It is not cut at the x range (the clip path does that), so a step that crosses the edge reaches it.
    function verts(xa, ya, step) {
      if (!step) return { x: xa, y: ya };
      var vx = [], vy = [];
      for (var i = 0; i < xa.length; i++) { vx.push(xa[i]); vy.push(ya[i]); if (i + 1 < xa.length) { vx.push(xa[i + 1]); vy.push(ya[i]); } }
      return { x: vx, y: vy };
    }
    // on a log y axis a value <= 0 is drawn at the floor of the axis (cy clamps it there), so a band from 0 keeps its shape
    function bandPath(s) {
      var l = verts(s.x, s.lo, s.step), h = verts(s.x, s.hi, s.step);
      return bandOutline(l.x, l.y, h.y, function (x, y) { return X(x).toFixed(1) + "," + cy(y); }, xok);
    }
    var order = series.filter(isBand)
      .concat(series.filter(function (s) { return s.quiet && !isBand(s); }), series.filter(function (s) { return !s.quiet && !isBand(s); }));
    order.forEach(function (s) {
      if (isBand(s)) {
        el("path", { class: "bandfill", d: bandPath(s), style: "fill:" + color(s.color) + ";fill-opacity:" + (s.opacity != null ? s.opacity : 0.18) }, sg);
        return;
      }
      var v = verts(s.x, s.y, s.step), d = "", pen = false, xa = null, xb = null;   // xa, xb: the first and last x drawn
      for (var i = 0; i < v.x.length; i++) {
        var yv = v.y[i];
        if (!ok(yv) || !xok(v.x[i]) || (!s.step && (v.x[i] < x0 || v.x[i] > x1))) { pen = false; continue; }
        d += (pen ? "L" : "M") + X(v.x[i]).toFixed(1) + "," + cy(yv);
        pen = true; if (xa == null) xa = v.x[i]; xb = v.x[i];
      }
      if (s.area && !isLog && xa != null) {
        var base = Y(Math.max(y0, Math.min(0, y1)));
        el("path", { class: "area", d: d + "L" + X(xb).toFixed(1) + "," + base + "L" + X(xa).toFixed(1) + "," + base + "Z", style: "fill:" + color(s.color) }, sg);
      }
      el("path", { class: s.quiet ? "line quiet" : "line", d: d, style: "stroke:" + color(s.quiet ? s.color || "var(--muted)" : s.color) +
        (s.dash ? ";stroke-dasharray:5 4" : "") + (s.width || s.quiet ? ";stroke-width:" + (s.width || 0.8) : "") +
        (s.quiet ? ";stroke-opacity:" + (s.opacity != null ? s.opacity : 0.35) : "") }, sg);
    });
    // clip region line overflow: simple rect mask
    var cid = "c" + Math.random().toString(36).slice(2, 8);
    var defs = el("defs", {}, svg); var cp = el("clipPath", { id: cid }, defs);
    el("rect", { x: m.l, y: m.t - 2, width: W - m.l - m.r, height: H - m.t - m.b + 4 }, cp);
    sg.setAttribute("clip-path", "url(#" + cid + ")");
    // annotations
    var ag = el("g", { class: "ann" }, svg);
    (spec.ann || []).forEach(function (a) {
      if (a.type === "vline") {
        el("line", { x1: X(a.x), x2: X(a.x), y1: m.t, y2: H - m.b, "stroke-dasharray": a.dash ? "4 3" : null }, ag);
        if (a.label) { var t = el("text", { x: X(a.x) + (a.anchor === "end" ? -5 : 5), y: m.t + 11 + (a.dy || 0), "text-anchor": a.anchor || "start" }, ag); setText(t, a.label); }
      } else if (a.type === "hline") {
        el("line", { x1: m.l, x2: W - m.r, y1: Y(a.y), y2: Y(a.y), "stroke-dasharray": a.dash ? "4 3" : null }, ag);
        if (a.label) { var t2 = el("text", { x: W - m.r - 4, y: Y(a.y) - 5, "text-anchor": "end" }, ag); setText(t2, a.label); }
      } else if (a.type === "point") {
        el("circle", { class: "dot", cx: X(a.x), cy: Y(a.y), r: 4.5, style: "fill:" + color(a.color || "1") }, ag);
        if (a.label) { var t3 = el("text", { x: X(a.x) + (a.dx || 8), y: Y(a.y) + (a.dy || -8), "text-anchor": a.anchor || "start" }, ag); setText(t3, a.label); }
      }
    });
    // end labels (skip if they would collide)
    if (spec.endLabels && !narrow) {
      var ends = series.map(function (s) {
        if (s.quiet || isBand(s)) return null;
        for (var i = s.x.length - 1; i >= 0; i--) if (s.y[i] != null && isFinite(s.y[i])) return { s: s, y: Y(s.y[i]), v: s.y[i] };
        return null;
      }).filter(Boolean).sort(function (a, b) { return a.y - b.y; });
      var groups = [];
      ends.forEach(function (e) {
        var g0 = groups[groups.length - 1];
        if (g0 && e.y - g0.y1 < 14) { g0.items.push(e); g0.y1 = e.y; } else groups.push({ items: [e], y0: e.y, y1: e.y });
      });
      var lastY = -Infinity;
      groups.forEach(function (gp) {
        var y = Math.max((gp.y0 + gp.y1) / 2, lastY + 14); lastY = y;
        var t = el("text", { class: "lab", x: W - m.r + 6, y: y + 4 }, svg);
        setText(t, gp.items.map(function (e) { return e.s.endLabel || e.s.name; }).join(" · ") +
          (spec.endValue ? " " + fmt(gp.items[0].v, spec.y.fmt) : ""));
      });
    }
    // crosshair + tooltip
    var cross = el("line", { class: "cross", y1: m.t, y2: H - m.b, x1: -10, x2: -10, visibility: "hidden" }, svg);
    var dots = series.map(function (s) { return s.quiet || isBand(s) ? null : el("circle", { class: "dot", r: 4, style: "fill:" + color(s.color), visibility: "hidden" }, svg); });
    var hit = el("rect", { x: m.l, y: m.t, width: W - m.l - m.r, height: H - m.t - m.b, fill: "transparent", style: "cursor:crosshair" }, svg);
    var xd = xLog ? Math.log : Number;   // nearest on the screen: on a log axis, by ratio
    function nearest(arr, v) { var lo = 0, hi = arr.length - 1; while (hi - lo > 1) { var mid = (lo + hi) >> 1; if (arr[mid] < v) lo = mid; else hi = mid; } return Math.abs(xd(arr[lo]) - xd(v)) <= Math.abs(xd(arr[hi]) - xd(v)) ? lo : hi; }
    function stepAt(arr, v) {   // the step holding at v: the last i with arr[i] <= v; -1 outside arr[0] .. arr[n-1]
      if (!(v >= arr[0] && v <= arr[arr.length - 1])) return -1;
      var lo = 0, hi = arr.length - 1;
      while (lo < hi) { var mid = (lo + hi + 1) >> 1; if (arr[mid] <= v) lo = mid; else hi = mid - 1; }
      return lo;
    }
    function move(ev) {
      var r = svg.getBoundingClientRect(), sx = (ev.clientX - r.left) * W / r.width;
      var fr = (sx - m.l) / (W - m.l - m.r), xv = xLog ? x0 * Math.pow(x1 / x0, fr) : x0 + fr * (x1 - x0);
      var rows = [], px = null, at = [], snap = xv;
      // lines and bands report their point nearest the pointer; the last one with a value places the crosshair
      series.forEach(function (s, k) {
        if (s.quiet || s.step) return;
        var i = nearest(s.x, xv), lo = isBand(s) ? s.lo[i] : s.y[i], hi = isBand(s) ? s.hi[i] : lo;
        if (lo == null || !isFinite(lo) || hi == null || !isFinite(hi) || !xok(s.x[i])) return;
        at[k] = i; px = X(s.x[i]); snap = s.x[i];
      });
      // step series report the step under the crosshair (under the pointer when no other series has a value there)
      series.forEach(function (s, k) {
        if (s.quiet) return;
        var i = s.step ? stepAt(s.x, snap) : at[k], band = isBand(s);
        var yv = i == null || i < 0 ? null : band ? s.lo[i] : s.y[i], hv = band && yv != null ? s.hi[i] : yv;
        if (yv == null || !isFinite(yv) || hv == null || !isFinite(hv)) { if (dots[k]) dots[k].setAttribute("visibility", "hidden"); return; }
        var xi = s.step ? snap : s.x[i];
        if (px == null) px = X(xi);
        if (dots[k]) { dots[k].setAttribute("cx", X(xi)); dots[k].setAttribute("cy", Y(yv)); dots[k].setAttribute("visibility", "visible"); }
        rows.push({ s: s, v: yv, hi: hv, xv: xi });
      });
      if (px == null) { leave(); return; }   // no series has a value here: no stale tooltip from the last point
      cross.setAttribute("x1", px); cross.setAttribute("x2", px); cross.setAttribute("visibility", "visible");
      var head = spec.x.type === "date" ? fmtDate(rows[0].xv) : (spec.x.tipLabel || "") + fmt(rows[0].xv, spec.x.fmt);
      tip.innerHTML = '<div class="hd">' + head + "</div>" + rows.map(function (rw) {
        var f = rw.s.fmt || spec.y.fmt, band = isBand(rw.s);   // a band's row: "lo – hi" beside a square swatch
        return '<div class="tk"><i style="background:' + color(rw.s.color) + (band ? ";height:0.6rem;border-radius:2px;opacity:0.45" : "") + '"></i><span>' +
          rich(rw.s.name) + "</span><b>" + (band ? fmt(rw.v, f) + " – " + fmt(rw.hi, f) : fmt(rw.v, f)) + "</b></div>";
      }).join("");
      tip.hidden = false;
      var wr = wrap.getBoundingClientRect(), left = px * r.width / W + (r.left - wr.left) + 12;
      if (left + tip.offsetWidth > wr.width) left = px * r.width / W + (r.left - wr.left) - tip.offsetWidth - 12;
      tip.style.left = Math.max(0, left) + "px"; tip.style.top = "8px";
    }
    function leave() { tip.hidden = true; cross.setAttribute("visibility", "hidden"); dots.forEach(function (d) { if (d) d.setAttribute("visibility", "hidden"); }); }
    hit.addEventListener("pointermove", move); hit.addEventListener("pointerdown", move); hit.addEventListener("pointerleave", leave);
    if (spec.y.label) {
      var cap = document.createElement("div"); cap.className = "kbd-note"; cap.style.margin = "0 0 0.2rem"; cap.innerHTML = rich(spec.y.label);
      host.insertBefore(cap, wrap);
    }
    return { X: X, Y: Y, svg: svg };
  };

  /* ---------------- more chart types: bars, heatmap, scatter, vector diagram ---------------- */
  // They share the line chart's frame: a legend for several series, a tooltip, an SVG that follows its container's
  // width, and colours read from CSS tokens (so a theme change needs no redraw). Book.chart picks one by spec.type.
  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
  var SCRIPT_RE = /([_^](?:\{[^}]*\}|\w))/, TOKEN_RE = /^([_^])(?:\{([^}]*)\}|(\w))$/;
  function rich(s) {   // tooltip HTML: "v_1" -> v<sub>1</sub>, "x_{ij}", "A^T" -> A<sup>T</sup>
    return esc(s).split(SCRIPT_RE).map(function (p) {
      var m = TOKEN_RE.exec(p);
      return m ? "<" + (m[1] === "_" ? "sub" : "sup") + ">" + (m[2] != null ? m[2] : m[3]) + "</" + (m[1] === "_" ? "sub" : "sup") + ">" : p;
    }).join("");
  }
  function setText(t, s) {   // SVG text with the same subscript / superscript marks as rich()
    s = String(s);
    if (!SCRIPT_RE.test(s)) { t.textContent = s; return t; }
    var shift = 0;
    s.split(SCRIPT_RE).forEach(function (p) {
      if (!p) return;
      var m = TOKEN_RE.exec(p), d = m ? (m[1] === "_" ? 3 : -4) : 0;
      var sp = el("tspan", { dy: d - shift || null, "font-size": m ? "0.75em" : null }, t);
      sp.textContent = m ? (m[2] != null ? m[2] : m[3]) : p;
      shift = d;
    });
    return t;
  }
  function txt(parent, x, y, s, cls, anchor) {
    return setText(el("text", { x: x, y: y, class: cls || null, "text-anchor": anchor || null }, parent), s);
  }
  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
  function legend(host, items, shape) {
    var lg = document.createElement("div"); lg.className = "legend";
    items.forEach(function (s) {
      var k = document.createElement("span"); k.className = "key";
      var sw = document.createElement("i"); sw.className = "sw " + (s.shape || shape);
      sw.style.background = color(s.color);
      if (s.opacity != null) sw.style.opacity = s.opacity;
      var nm = document.createElement("span"); nm.innerHTML = rich(s.name == null ? "" : s.name);   // rich() escapes, and sets a_1 as a subscript
      k.appendChild(sw); k.appendChild(nm); lg.appendChild(k);
    });
    host.appendChild(lg);
  }
  // legend (several series), the y label as a caption, the positioned wrapper and the tooltip; the svg comes later
  function begin(host, spec, items, shape) {
    host.innerHTML = ""; host.classList.add("chart");
    if (items.length > 1 || spec.legend) legend(host, items, shape);
    if (spec.y && spec.y.label) {
      var cap = document.createElement("div"); cap.className = "kbd-note"; cap.style.margin = "0 0 0.2rem"; cap.innerHTML = rich(spec.y.label); host.appendChild(cap);
    }
    var wrap = document.createElement("div"); wrap.style.position = "relative"; host.appendChild(wrap);
    var tip = document.createElement("div"); tip.className = "tip"; tip.hidden = true; wrap.appendChild(tip);
    return { wrap: wrap, tip: tip, W: Math.max(280, Math.round(host.clientWidth || 640)) };
  }
  function makeSvg(c, H, spec) {
    c.H = H;
    var alt = spec.alt || spec.title || null;   // build.py refuses a spec without alt; here, no empty aria-label on a role="img"
    if (!alt && window.console) console.warn("chart without alt text");
    c.svg = el("svg", { viewBox: "0 0 " + c.W + " " + H, role: "img", "aria-label": alt }, c.wrap);
    return c.svg;
  }
  function clipTo(svg, g, x, y, w, h) {   // clip group g to a rectangle
    var cid = "c" + Math.random().toString(36).slice(2, 8), cp = el("clipPath", { id: cid }, el("defs", {}, svg));
    el("rect", { x: x, y: y, width: Math.max(0, w), height: Math.max(0, h) }, cp);
    g.setAttribute("clip-path", "url(#" + cid + ")");
  }
  // show html in the tooltip beside the svg point (px, py), above it when there is room
  function showTip(c, html, px, py) {
    c.tip.innerHTML = html; c.tip.hidden = false;
    var r = c.svg.getBoundingClientRect(), wr = c.wrap.getBoundingClientRect(), k = r.width / c.W;
    var cx = px * k + (r.left - wr.left), cy = py * k + (r.top - wr.top);
    var left = cx + 12; if (left + c.tip.offsetWidth > wr.width) left = cx - c.tip.offsetWidth - 12;
    var top = cy - c.tip.offsetHeight - 10; if (top < 0) top = cy + 14;
    var mt = wr.height - c.tip.offsetHeight; if (top > mt) top = Math.max(0, mt);   // a tall tip below its point stays inside the box, which scrolls and would cut it
    c.tip.style.left = Math.max(0, left) + "px"; c.tip.style.top = top + "px";
  }
  function tipRow(col, name, val, sq) {
    return '<div class="tk"><i style="background:' + color(col) + (sq ? ";height:0.6rem;border-radius:2px" : "") + '"></i><span>' + rich(name) + "</span><b>" + val + "</b></div>";
  }
  function svgPoint(c, ev) { var r = c.svg.getBoundingClientRect(); return { x: (ev.clientX - r.left) * c.W / r.width, y: (ev.clientY - r.top) * c.W / r.width, k: r.width / c.W }; }
  function maxLen(a) { return a.reduce(function (m, s) { return Math.max(m, String(s).replace(/[_^](\{[^}]*\}|\w)/g, "x").length); }, 0); }
  // cut a label to at most n visible characters, ending in an ellipsis; a_1 / x_{ij} / A^T count as one character each
  // and are never cut in the middle. The full text stays in the tooltip.
  function ellipsize(s, n) {
    s = String(s);
    if (maxLen([s]) <= n) return s;
    var out = "", k = 0, re = /[_^](?:\{[^}]*\}|\w)|[\s\S]/g, m;
    while (k < n - 1 && (m = re.exec(s))) { out += m[0]; k++; }
    return out + "…";
  }
  function ticksWithStep(lo, hi, st) {
    var t = [], v = Math.ceil(lo / st - 1e-9) * st;
    for (; v <= hi + st * 1e-9; v += st) t.push(Math.abs(v) < st * 1e-9 ? 0 : v);
    return t;
  }

  /* ---------------- bar chart ---------------- */
  // spec: {type:'bar', alt, height, legend, categories:[text], valueLabels, stack,
  //        x:{label}, y:{fmt,tfmt,label,min,max,ticks},
  //        series:[{name,color,values:[],fmt}], ann:[{type:'hline',y,label}]}
  // Bars start at zero (up for positive values, down for negative ones); with several series the bars of one
  // category stand side by side, never wider together than 78% of their slot. With stack:true each category has one
  // bar: its positive values stack upward from zero and its negative values downward, in series order; the value
  // label and the tooltip give the category's total. Category labels that do not fit tilt by
  // 40 degrees; when even tilted ones would touch, every k-th is shown (the tooltip names every category).
  // Value labels are dropped when they would not fit under the bars.
  Book.barChart = function (host, spec) {
    var series = spec.series || [], cats = spec.categories || [], nc = cats.length, ns = series.length, ys = spec.y || {}, xs = spec.x || {};
    var c = begin(host, spec, series.map(function (s, i) { return { name: s.name, color: s.color || String(i + 1) }; }), "sq");
    var W = c.W, narrow = W < 460, yf = ys.tfmt || ys.fmt;
    var stack = !!spec.stack, nb = stack ? 1 : ns, ok = function (v) { return v != null && isFinite(v); };
    var sums = cats.map(function (cat, i) {   // [positive sum, negative sum, total, values] of each category (stacked)
      var p = 0, n = 0, k = 0;
      series.forEach(function (s) { var v = s.values[i]; if (ok(v)) { k++; if (v >= 0) p += v; else n += v; } });
      var t = p + n;
      if (Math.abs(t) <= 1e-12 * (p - n)) t = 0;   // a category that cancels prints 0, not -0.0
      return [p, n, t, k];
    });
    var totFmt = ys.fmt || (series[0] && series[0].fmt);   // the total's format: the axis's, else the first series'
    var vals = [];
    if (stack) sums.forEach(function (pn) { vals.push(pn[0], pn[1]); });
    else series.forEach(function (s) { s.values.forEach(function (v) { if (ok(v)) vals.push(v); }); });
    var y0 = ys.min != null ? ys.min : Math.min(0, Math.min.apply(null, vals)), y1 = ys.max != null ? ys.max : Math.max(0, Math.max.apply(null, vals));
    if (!(y1 > y0)) y1 = y0 + 1;
    var room = (y1 - y0) * (spec.valueLabels ? 0.1 : 0.03);
    if (ys.max == null && y1 > 0) y1 += room;
    if (ys.min == null && y0 < 0) y0 -= room;
    var yt = ys.ticks || linTicks(y0, y1, narrow ? 4 : 6, yf);
    var m = { l: narrow ? 46 : 58, r: 16, t: 12, b: 30 };
    var pw = W - m.l - m.r, slot = pw / Math.max(1, nc);
    var catPx = maxLen(cats) * 6.2 + 6, tilt = slot < catPx, shown = cats;   // labels that do not fit tilt by 40 degrees
    if (tilt) {   // tilted labels hang down and to the left of their tick: keep them to 20 characters and widen the left margin
      shown = cats.map(function (s) { return ellipsize(s, 20); });
      catPx = maxLen(shown) * 6.2 + 6; tilt = slot < catPx;
      if (tilt) {
        var ml = clamp(catPx * 0.766 - slot / 2 + 4, m.l, Math.max(m.l, W * 0.22));
        if (ml > m.l) { m.l = ml; pw = W - m.l - m.r; slot = pw / Math.max(1, nc); }
        var fit = Math.floor(((m.l + slot / 2 - 4) / 0.766 - 6) / 6.2);   // characters whose tilted label still ends inside the svg
        if (fit < 20) { shown = cats.map(function (s) { return ellipsize(s, Math.max(4, fit)); }); catPx = maxLen(shown) * 6.2 + 6; }
      }
    }
    var extra = tilt ? Math.min(80, catPx * 0.65 - 18) : 0;   // room for the tilted labels
    m.b = 30 + extra + (xs.label ? 14 : 0);
    var svg = makeSvg(c, (spec.height || Math.round(Math.min(360, Math.max(220, W * 0.52)))) + extra, spec), H = c.H;
    var ph = H - m.t - m.b, Y = function (v) { return m.t + ph - (v - y0) / (y1 - y0) * ph; };
    var base = Y(clamp(0, y0, y1));
    var hov = el("rect", { class: "hov", y: m.t, height: ph, width: slot, visibility: "hidden" }, svg);
    var g = el("g", { class: "grid" }, svg), ax = el("g", { class: "axis" }, svg);
    yt.forEach(function (v) {
      if (v < y0 || v > y1) return;
      el("line", { x1: m.l, x2: W - m.r, y1: Y(v), y2: Y(v) }, g);
      txt(svg, m.l - 8, Y(v) + 3.5, fmt(v, yf), null, "end");
    });
    if (y0 < 0 && y1 > 0) el("line", { class: "zero", x1: m.l, x2: W - m.r, y1: Y(0), y2: Y(0) }, svg);
    el("line", { x1: m.l, x2: W - m.r, y1: H - m.b, y2: H - m.b }, ax);
    // bars
    var per = slot * 0.78 / Math.max(1, nb), gap = nb > 1 && per >= 4 ? 2 : 0, bw = Math.min(64, per - gap), group = nb * (bw + gap) - gap;   // group <= 0.78 slot: neighbours never interleave
    var labStep = tilt ? Math.max(1, Math.ceil(12 / (slot * 0.643))) : 1;   // tilted by 40 degrees, labels sit slot*sin40 apart: show every k-th so that they are 12 px apart
    var bars = el("g", { class: "bars" }, svg); clipTo(svg, bars, m.l, m.t - 2, pw, ph + 4);
    var labels = [];
    cats.forEach(function (cat, i) {
      var cx = m.l + (i + 0.5) * slot;
      if (stack) {
        var up = 0, down = 0, bx0 = cx - bw / 2;
        series.forEach(function (s, k) {
          var v = s.values[i]; if (!ok(v) || v === 0) return;
          var lo = v > 0 ? up : down + v, hi = v > 0 ? up + v : down;
          if (v > 0) up = hi; else down = lo;
          var top = Y(hi), h = Y(lo) - Y(hi);
          if (h > 0) el("rect", { class: "bar", x: bx0, y: top, width: bw, height: h, style: "fill:" + color(s.color || String(k + 1)) }, bars);
        });
        var tot = sums[i][2];
        if (sums[i][3]) labels.push({ x: cx, y: tot >= 0 ? Y(sums[i][0]) - 4 : Y(sums[i][1]) + 12, t: fmt(tot, totFmt) });
      } else series.forEach(function (s, k) {
        var v = s.values[i]; if (!ok(v)) return;
        var bx = cx - group / 2 + k * (bw + gap), top = Math.min(Y(v), base), h = Math.abs(Y(v) - base);
        if (h > 0) el("rect", { class: "bar", x: bx, y: top, width: bw, height: h, style: "fill:" + color(s.color || String(k + 1)) }, bars);
        labels.push({ x: bx + bw / 2, y: v >= 0 ? Y(v) - 4 : Y(v) + 12, t: fmt(v, s.fmt || ys.fmt) });
      });
      el("line", { x1: cx, x2: cx, y1: H - m.b, y2: H - m.b + 4 }, ax);
      if (i % labStep) return;
      var lab = txt(svg, tilt ? cx + 3 : cx, H - m.b + (tilt ? 12 : 16), shown[i], null, tilt ? "end" : "middle");
      if (tilt) lab.setAttribute("transform", "rotate(-40 " + (cx + 3) + " " + (H - m.b + 12) + ")");
    });
    (spec.ann || []).forEach(function (a) {   // over the bars but under the value labels, so the labels and their halo stay readable
      if (a.type !== "hline") return;
      var ag = el("g", { class: "ann" }, svg);
      el("line", { x1: m.l, x2: W - m.r, y1: Y(a.y), y2: Y(a.y), "stroke-dasharray": "4 3" }, ag);
      if (a.label) txt(ag, W - m.r - 4, Y(a.y) - 5, a.label, null, "end");
    });
    if (spec.valueLabels && labels.length) {   // 10.5 px, else 9 px, else none: the longest label must fit one bar's pitch
      var longest = maxLen(labels.map(function (l) { return l.t; })), pitch = nb > 1 ? bw + gap : slot * 0.9;
      var fs = longest * 6.1 <= pitch ? 10.5 : longest * 5.2 <= pitch ? 9 : 0;
      if (fs) labels.forEach(function (l) { el("text", { class: "bv", x: l.x, y: l.y, "text-anchor": "middle", style: "font-size:" + fs + "px" }, svg).textContent = l.t; });
    }
    if (xs.label) txt(svg, m.l + pw / 2, H - 6, xs.label, "ttl-y", "middle");
    // hover: one hit column per category
    var cross = function (i) { hov.setAttribute("x", m.l + i * slot); hov.setAttribute("visibility", "visible"); };
    cats.forEach(function (cat, i) {
      var hit = el("rect", { x: m.l + i * slot, y: m.t, width: slot, height: ph, fill: "transparent" }, svg);
      var show = function () {
        cross(i);
        var tops = [], rows = series.map(function (s, k) {
          var v = s.values[i]; if (!ok(v)) return "";
          tops.push(Y(stack ? sums[i][0] : v));
          return tipRow(s.color || String(k + 1), s.name, fmt(v, s.fmt || ys.fmt), true);
        }).join("");
        if (stack && sums[i][3]) rows += tipRow("transparent", "Total", fmt(sums[i][2], totFmt), true);   // no swatch
        showTip(c, '<div class="hd">' + rich(cat) + "</div>" + rows, m.l + (i + 0.5) * slot, tops.length ? Math.min.apply(null, tops) : m.t);
      };
      hit.addEventListener("pointermove", show); hit.addEventListener("pointerdown", show);
      hit.addEventListener("pointerleave", function () { c.tip.hidden = true; hov.setAttribute("visibility", "hidden"); });
    });
    return { Y: Y, svg: svg };
  };

  /* ---------------- heatmap ---------------- */
  // spec: {type:'heatmap', alt, labels:[text] (rows and columns alike) or rows:[text], cols:[text],
  //        matrix:[[number]] (one inner array per row), fmt (cell labels, default 'n2'), min, max (default -1 and 1),
  //        scale (false hides the colour bar), scaleFmt, valueName (tooltip, default 'value')}
  // The scale is diverging and centred at 0: series-1 for positive values, series-2 for negative ones, the surface
  // colour at 0, each side reaching full strength at max and min. Cells are square and carry their value.
  // Row and column labels are cut to 16 and 18 characters; when cells would then be under 10 px they are cut to 7, and
  // when that is not enough either, dropped (hover or touch names every cell). The chart never exceeds its container.
  Book.heatmap = function (host, spec) {
    var fullRows = spec.rows || spec.labels || [], fullCols = spec.cols || spec.labels || [], M = spec.matrix || [];
    var nr = fullRows.length, nc = fullCols.length, f = spec.fmt || "n2";
    var lo = spec.min != null ? spec.min : -1, hi = spec.max != null ? spec.max : 1;
    var negLim = lo < 0 ? -lo : 1, posLim = hi > 0 ? hi : 1, showScale = spec.scale !== false;
    var c = begin(host, spec, [], "sq"), W = c.W;
    // Layout. The labels are cut to a length (the tooltip header has the full text) and the cells take what is left of
    // the width. Cells below LABEL_MIN px cannot carry readable labels: first try short labels, then none at all
    // (every cell still names its row and column in the tooltip), so the chart never grows wider than its container.
    var LABEL_MIN = 10;
    function plan(rc, cc) {
      var rl = fullRows.map(function (s) { return ellipsize(s, rc); }), cl = fullCols.map(function (s) { return ellipsize(s, cc); });
      var labW = Math.min(110, 14 + maxLen(rl) * 6.4), colPx = maxLen(cl) * 6.2 + 4;
      var cell0 = Math.min(72, (W - labW - 8) / Math.max(1, nc)), tilt = colPx > cell0;
      var mr = tilt ? Math.min(W * 0.3, Math.max(8, colPx * 0.72 - cell0 / 2 + 4)) : 8;
      return { rows: rl, cols: cl, labW: labW, colPx: colPx, tilt: tilt, mr: mr, cell: Math.min(72, (W - labW - mr) / Math.max(1, nc)), labels: true };
    }
    var P = plan(16, 18);
    if (P.cell < LABEL_MIN) { var Q = plan(7, 7); if (Q.cell >= LABEL_MIN) P = Q; }
    if (P.cell < LABEL_MIN) P = { rows: [], cols: [], labW: 8, colPx: 0, tilt: false, mr: 8, cell: Math.max(1, Math.min(72, (W - 16) / Math.max(1, nc))), labels: false };
    var rows = P.rows, cols = P.cols, labW = P.labW, colPx = P.colPx, tilt = P.tilt, mr = P.mr, cell = P.cell;
    var rowStep = Math.max(1, Math.ceil(12 / cell)), colStep = tilt ? Math.max(1, Math.ceil(15.6 / cell)) : 1;   // 11 px labels need 12 px of pitch; tilted by 45 degrees, a cell of 15.6 px
    var top = P.labels ? (tilt ? Math.min(90, 12 + colPx * 0.72) : 24) : 8, left = labW + Math.max(0, (W - labW - mr - cell * nc) / 2);
    var H = Math.round(top + cell * nr + (showScale ? 44 : 6));
    var svg = makeSvg(c, H, spec);
    function tone(v) {
      if (v == null || !isFinite(v)) return { cls: "cell none", a: 0 };
      return v >= 0 ? { cls: "cell pos", a: Math.min(1, v / posLim) } : { cls: "cell neg", a: Math.min(1, -v / negLim) };
    }
    var chars = 0;
    M.forEach(function (r) { r.forEach(function (v) { chars = Math.max(chars, fmt(v, f).length); }); });
    var fs = Math.min(11.5, (cell - 6) / Math.max(1, chars * 0.62));   // below 7.5 px the values stay in the tooltip
    fullRows.forEach(function (_, i) {
      if (P.labels && i % rowStep === 0) txt(svg, left - 7, top + (i + 0.5) * cell + 4, rows[i], null, "end");
      fullCols.forEach(function (_, j) {
        var v = (M[i] || [])[j], t = tone(v);
        el("rect", { class: t.cls, x: left + j * cell, y: top + i * cell, width: cell, height: cell, style: "--a:" + t.a.toFixed(3) }, svg);
        if (fs >= 7.5 && v != null && isFinite(v)) {
          el("text", { class: "cv", x: left + (j + 0.5) * cell, y: top + (i + 0.5) * cell + fs * 0.35, "text-anchor": "middle", style: "font-size:" + fs.toFixed(1) + "px" }, svg).textContent = fmt(v, f);
        }
      });
    });
    if (P.labels) cols.forEach(function (cl, j) {
      if (j % colStep) return;
      var x = left + (j + 0.5) * cell;
      if (!tilt) txt(svg, x, top - 7, cl, null, "middle");
      else { var t = txt(svg, x - 2, top - 6, cl, null, "start"); t.setAttribute("transform", "rotate(-45 " + (x - 2) + " " + (top - 6) + ")"); }
    });
    if (showScale) {   // colour bar: 21 steps from min to max, with min, 0 and max printed under it
      var n = 21, bw = Math.min(240, cell * nc), sw = bw / n, by = top + nr * cell + 14, sf = spec.scaleFmt;
      for (var k = 0; k < n; k++) {
        var v = lo + (k + 0.5) / n * (hi - lo), t = tone(v);
        el("rect", { class: t.cls.replace("cell", "cell bar-step"), x: left + k * sw, y: by, width: sw + 0.5, height: 10, style: "--a:" + t.a.toFixed(3) }, svg);
      }
      txt(svg, left, by + 23, fmt(lo, sf), null, "start");
      txt(svg, left + bw, by + 23, fmt(hi, sf), null, "end");
      if (lo < 0 && hi > 0) txt(svg, left + (0 - lo) / (hi - lo) * bw, by + 23, fmt(0, sf), null, "middle");
    }
    // hover: an outline on the cell under the pointer
    var ring = el("rect", { class: "hl", width: cell, height: cell, visibility: "hidden" }, svg);
    var hit = el("rect", { x: left, y: top, width: cell * nc, height: cell * nr, fill: "transparent" }, svg);
    function show(ev) {
      var p = svgPoint(c, ev), j = Math.floor((p.x - left) / cell), i = Math.floor((p.y - top) / cell);
      if (i < 0 || j < 0 || i >= nr || j >= nc) { leave(); return; }
      var v = (M[i] || [])[j];
      ring.setAttribute("x", left + j * cell); ring.setAttribute("y", top + i * cell); ring.setAttribute("visibility", "visible");
      showTip(c, '<div class="hd">' + rich(fullRows[i]) + " × " + rich(fullCols[j]) + "</div>" +
        '<div class="tk"><i style="background:transparent"></i><span>' + esc(spec.valueName || "value") + "</span><b>" + fmt(v, f) + "</b></div>",
        left + (j + 0.5) * cell, top + i * cell);
    }
    function leave() { c.tip.hidden = true; ring.setAttribute("visibility", "hidden"); }
    hit.addEventListener("pointermove", show); hit.addEventListener("pointerdown", show); hit.addEventListener("pointerleave", leave);
    return { svg: svg };
  };

  /* ---------------- scatter and vector diagram ---------------- */
  // Both draw the same kinds of things on numeric axes; they differ in defaults: a vector diagram has equal scales on
  // the two axes (spec.equal, default true) and its `segments` are dashed; a scatter plot has free scales and its `lines`
  // are solid. Any of the keys below may appear in either.
  // spec: {type:'scatter'|'vector', alt, height, legend, equal,
  //        x:{label,fmt,tfmt,min,max,ticks,tickLabels,name}, y:{...},             tickLabels: text for each of ticks
  //        series:[{name,color,x:[],y:[],labels:[text],r}],                       points (up to four series)
  //        bands:[{x:[],lo:[],hi:[],color,opacity,name}],                         filled between lo and hi, under everything
  //        lines:[{from:[x,y],to:[x,y],extend,dash,color,width,label}],          straight lines; extend runs the line to the edges
  //        segments:[...same keys...],                                            dashed by default (projections)
  //        curves:[{x:[],y:[],color,dash,width,label}],                           polylines, one path each (a dash runs along
  //                                                                               the whole curve); null breaks the curve
  //        ellipses:[{center:[x,y],cov:[[a,b],[b,c]],scale,color,fill,axes,label}],   the contour x'S^-1 x = scale^2
  //        vectors:[{from:[0,0],to:[x,y],label,color,width,dash,dx,dy}],           arrows
  //        points:[{at:[x,y],label,color,r,dx,dy}]}                                single marked points
  function clipSeg(ax, ay, bx, by, x0, x1, y0, y1, extend) {   // Liang-Barsky; extend lets the line run past both ends
    var dx = bx - ax, dy = by - ay;
    if (dx === 0 && dy === 0) return null;
    var t0 = extend ? -Infinity : 0, t1 = extend ? Infinity : 1, p = [-dx, dx, -dy, dy], q = [ax - x0, x1 - ax, ay - y0, y1 - ay];
    for (var i = 0; i < 4; i++) {
      if (p[i] === 0) { if (q[i] < 0) return null; continue; }
      var r = q[i] / p[i];
      if (p[i] < 0) { if (r > t0) t0 = r; } else if (r < t1) t1 = r;
    }
    return t0 > t1 ? null : [ax + t0 * dx, ay + t0 * dy, ax + t1 * dx, ay + t1 * dy];
  }
  function ellipseShape(ctr, cov, k) {   // principal axes of a 2x2 covariance matrix, scaled by k standard deviations
    var a = cov[0][0], b = (cov[0][1] + cov[1][0]) / 2, d = cov[1][1], h = (a - d) / 2, r = Math.sqrt(h * h + b * b), mid = (a + d) / 2;
    if (!(mid - r >= -1e-12 * Math.abs(mid))) throw new Error("ellipse cov is not positive semi-definite");   // also catches NaN
    var s1 = k * Math.sqrt(Math.max(0, mid + r)), s2 = k * Math.sqrt(Math.max(0, mid - r)), th = 0.5 * Math.atan2(2 * b, a - d);
    var u = [Math.cos(th), Math.sin(th)], v = [-Math.sin(th), Math.cos(th)], pts = [];
    for (var i = 0; i < 120; i++) {
      var t = i / 120 * 2 * Math.PI, p = s1 * Math.cos(t), q = s2 * Math.sin(t);
      pts.push([ctr[0] + p * u[0] + q * v[0], ctr[1] + p * u[1] + q * v[1]]);
    }
    return { pts: pts, hx: Math.sqrt(Math.pow(s1 * u[0], 2) + Math.pow(s2 * v[0], 2)), hy: Math.sqrt(Math.pow(s1 * u[1], 2) + Math.pow(s2 * v[1], 2)),
             a1: [ctr[0] - s1 * u[0], ctr[1] - s1 * u[1], ctr[0] + s1 * u[0], ctr[1] + s1 * u[1]],
             a2: [ctr[0] - s2 * v[0], ctr[1] - s2 * v[1], ctr[0] + s2 * v[0], ctr[1] + s2 * v[1]] };
  }
  function xyPlot(host, spec, vectorDefaults) {
    var series = spec.series || [], vectors = spec.vectors || [], pts = spec.points || [], xs = spec.x || {}, ys = spec.y || {};
    var equal = spec.equal != null ? !!spec.equal : vectorDefaults;
    var lines = (spec.lines || []).map(function (l) { return { l: l, dash: l.dash === true }; })
      .concat((spec.segments || []).map(function (l) { return { l: l, dash: l.dash !== false }; }));
    var ells = (spec.ellipses || []).map(function (e) { return { e: e, s: ellipseShape(e.center, e.cov, e.scale || 1) }; });
    var bands = spec.bands || [], bop = function (b) { return b.opacity != null ? b.opacity : 0.18; }, curves = spec.curves || [];
    var c = begin(host, spec, series.map(function (s, i) { return { name: s.name, color: s.color || String(i + 1) }; })
      .concat(bands.filter(function (b) { return b.name != null; })
        .map(function (b) { return { name: b.name, color: b.color || "var(--ink-2)", shape: "band", opacity: Math.min(1, 1.6 * bop(b)) }; })), "dot");
    var W = c.W, narrow = W < 460, bx = [], by = [];
    function add(x, y) { if (x != null && y != null && isFinite(x) && isFinite(y)) { bx.push(x); by.push(y); } }
    series.forEach(function (s) { s.x.forEach(function (v, i) { add(v, s.y[i]); }); });
    bands.forEach(function (b) { b.x.forEach(function (v, i) { add(v, b.lo[i]); add(v, b.hi[i]); }); });
    vectors.forEach(function (v) { var f = v.from || [0, 0]; add(f[0], f[1]); add(v.to[0], v.to[1]); });
    pts.forEach(function (p) { add(p.at[0], p.at[1]); });
    lines.forEach(function (o) { add(o.l.from[0], o.l.from[1]); add(o.l.to[0], o.l.to[1]); });
    curves.forEach(function (cv) { cv.x.forEach(function (v, i) { add(v, cv.y[i]); }); });
    ells.forEach(function (o) { add(o.e.center[0] - o.s.hx, o.e.center[1] - o.s.hy); add(o.e.center[0] + o.s.hx, o.e.center[1] + o.s.hy); });
    if (!bx.length) { bx = [-1, 1]; by = [-1, 1]; }
    var x0 = Math.min.apply(null, bx), x1 = Math.max.apply(null, bx), y0 = Math.min.apply(null, by), y1 = Math.max.apply(null, by);
    if (x1 === x0) { x0 -= 1; x1 += 1; }
    if (y1 === y0) { y0 -= 1; y1 += 1; }
    var pad = vectorDefaults ? 0.1 : 0.06, px = (x1 - x0) * pad, py = (y1 - y0) * pad;
    x0 = xs.min != null ? xs.min : x0 - px; x1 = xs.max != null ? xs.max : x1 + px;
    y0 = ys.min != null ? ys.min : y0 - py; y1 = ys.max != null ? ys.max : y1 + py;
    var m = { l: narrow ? 46 : 58, r: 16, t: 12, b: xs.label ? 44 : 30 }, pw = W - m.l - m.r, ph;
    var xl = xs.ticks && xs.tickLabels, yl = ys.ticks && ys.tickLabels;   // text for each of the ticks
    if (yl) {   // the left margin grows to fit the longest y label, up to 40% of the width; longer ones are cut with an ellipsis
      var room = Math.max(m.l, W * 0.4);
      yl = yl.map(function (s) { return s == null ? s : ellipsize(s, Math.floor((room - 14) / 6.2)); });
      m.l = clamp(maxLen(yl.filter(function (s) { return s != null; })) * 6.2 + 14, m.l, room); pw = W - m.l - m.r;
    }
    if (spec.height) ph = spec.height - m.t - m.b;
    else if (equal) ph = clamp(pw * (y1 - y0) / (x1 - x0), 190, 460);
    else ph = Math.round(Math.min(360, Math.max(220, W * 0.52))) - m.t - m.b;
    if (equal) {   // the same number of pixels per unit on both axes: widen the shorter range around its middle
      var k = Math.min(pw / (x1 - x0), ph / (y1 - y0)), ex = pw / k - (x1 - x0), ey = ph / k - (y1 - y0);
      x0 -= ex / 2; x1 += ex / 2; y0 -= ey / 2; y1 += ey / 2;
    }
    var H = ph + m.t + m.b, svg = makeSvg(c, H, spec);
    var X = function (v) { return m.l + (v - x0) / (x1 - x0) * pw; }, Y = function (v) { return m.t + ph - (v - y0) / (y1 - y0) * ph; };
    // grid, tick labels, the lines x = 0 and y = 0
    var xt, yt;
    if (equal && !xs.ticks && !ys.ticks) {   // one tick step for both axes, so equal distances look equal
      var st = niceStep(Math.max(x1 - x0, y1 - y0), narrow ? 5 : 8, tickRes(xs.tfmt || xs.fmt, Math.max(Math.abs(x0), Math.abs(x1), Math.abs(y0), Math.abs(y1))));
      xt = ticksWithStep(x0, x1, st); yt = ticksWithStep(y0, y1, st);
    } else {
      xt = xs.ticks || linTicks(x0, x1, narrow ? 4 : 7, xs.tfmt || xs.fmt);
      yt = ys.ticks || linTicks(y0, y1, narrow ? 4 : 6, ys.tfmt || ys.fmt);
    }
    var g = el("g", { class: "grid" }, svg), ax = el("g", { class: "axis" }, svg);
    yt.forEach(function (v, i) {
      if (v < y0 || v > y1) return;
      el("line", { x1: m.l, x2: W - m.r, y1: Y(v), y2: Y(v) }, g);
      txt(svg, m.l - 8, Y(v) + 3.5, yl && yl[i] != null ? yl[i] : fmt(v, ys.tfmt || ys.fmt), null, "end");
    });
    el("line", { x1: m.l, x2: m.l, y1: m.t, y2: H - m.b }, ax);
    el("line", { x1: m.l, x2: W - m.r, y1: H - m.b, y2: H - m.b }, ax);
    xt.forEach(function (v, i) {
      if (v < x0 || v > x1) return;
      el("line", { x1: X(v), x2: X(v), y1: m.t, y2: H - m.b }, g);
      el("line", { x1: X(v), x2: X(v), y1: H - m.b, y2: H - m.b + 4 }, ax);
      txt(svg, X(v), H - m.b + 16, xl && xl[i] != null ? xl[i] : fmt(v, xs.tfmt || xs.fmt), null, "middle");
    });
    if (y0 < 0 && y1 > 0) el("line", { class: "zero", x1: m.l, x2: W - m.r, y1: Y(0), y2: Y(0) }, svg);
    if (x0 < 0 && x1 > 0) el("line", { class: "zero", x1: X(0), x2: X(0), y1: m.t, y2: H - m.b }, svg);
    if (xs.label) txt(svg, m.l + pw / 2, H - 6, xs.label, "ttl-y", "middle");
    var geo = el("g", { class: "geo" }, svg); clipTo(svg, geo, m.l, m.t, pw, ph);
    var inside = function (x, y) { return x >= x0 && x <= x1 && y >= y0 && y <= y1; };
    var tags = [];
    function tag(x, y, s, anchor, o, uy) { tags.push({ x: x + (o.dx || 0), y: y + (o.dy || 0), s: s, a: o.anchor || anchor, uy: uy, moved: o.dx != null || o.dy != null || o.anchor != null }); }
    function drawTags() {   // labels go on top of everything; one that would leave the plot sideways turns to the other side
      var boxes = [];       // boxes of the labels already placed; a label that would overlap one moves down 12 px (then up, then down 24)
      function box(q, w) { var x = q.a === "end" ? q.x - w : q.a === "middle" ? q.x - w / 2 : q.x, y = Math.max(10, q.y); return { x0: x, x1: x + w, y0: y - 11, y1: y + 3 }; }
      function hits(b) { return boxes.some(function (o) { return b.x0 < o.x1 && b.x1 > o.x0 && b.y0 < o.y1 && b.y1 > o.y0; }); }
      tags.forEach(function (q) {
        var t = txt(svg, q.x, Math.max(10, q.y), q.s, "tl", q.a), w = 0;     // drawn first, so that its real width is measured, not guessed
        try { w = t.getComputedTextLength(); } catch (err) { w = 0; }
        if (!(w > 0)) w = maxLen([q.s]) * 6.4;                               // not rendered (hidden, or no layout yet): estimate
        if (!q.moved) {
          var flipped = false;
          if (q.a === "start" && q.x + w > W - 2) { q.a = "end"; q.x = Math.max(q.x - 16, w + 2); flipped = true; }   // a flipped label is clamped too, so a long one is not cut off at the other edge
          else if (q.a === "end" && q.x - w < 2) { q.a = "start"; q.x = Math.min(q.x + 16, W - w - 2); flipped = true; }
          else if (q.a === "middle") q.x = clamp(q.x, w / 2 + 2, W - w / 2 - 2);
          if (flipped && q.uy != null) {   // a vector's label now lies on the shaft's side of the tip: step off the shaft (up if the arrow points up, else down)
            var off = q.uy < 0 ? -12 : 12;
            if (q.y + off < 10 || q.y + off > H - m.b - 2) off = -off;
            q.y += off;
          }
          if (hits(box(q, w))) {
            var y = q.y, steps = [12, -12, 24];
            for (var i = 0; i < steps.length; i++) { q.y = y + steps[i]; if (q.y >= 10 && q.y <= H - m.b - 2 && !hits(box(q, w))) break; q.y = y; }
          }
        }
        boxes.push(box(q, w));
        t.setAttribute("x", q.x); t.setAttribute("y", Math.max(10, q.y)); t.setAttribute("text-anchor", q.a);
      });
    }
    // bands, under everything else in the plot
    bands.forEach(function (b) {
      el("path", { class: "bandfill", d: bandOutline(b.x, b.lo, b.hi, function (x, y) { return X(x).toFixed(1) + "," + Y(y).toFixed(1); }),
                   style: "fill:" + color(b.color || "var(--ink-2)") + ";fill-opacity:" + bop(b) }, geo);
    });
    // ellipses
    ells.forEach(function (o, i) {
      var e = o.e, col = color(e.color || "var(--ink-2)"), d = "";
      o.s.pts.forEach(function (p, j) { d += (j ? "L" : "M") + X(p[0]).toFixed(1) + "," + Y(p[1]).toFixed(1); });
      el("path", { class: "ell", d: d + "Z", style: "stroke:" + col + ";fill:" + (e.fill ? col : "none"), "fill-opacity": e.fill ? 0.1 : null }, geo);
      if (e.axes) [o.s.a1, o.s.a2].forEach(function (a) {
        el("line", { class: "ln", x1: X(a[0]), y1: Y(a[1]), x2: X(a[2]), y2: Y(a[3]), style: "stroke:" + col + ";stroke-dasharray:3 3;stroke-width:1" }, geo);
      });
      if (e.label) {   // above the topmost point of the contour
        var top = o.s.pts.reduce(function (b, p) { return p[1] > b[1] ? p : b; }, o.s.pts[0]);
        tag(X(top[0]), Math.max(m.t + 10, Y(top[1]) - 6), e.label, "middle", e);
      }
    });
    // lines and segments
    lines.forEach(function (o) {
      var l = o.l, col = color(l.color || "var(--ink-2)");
      var s = clipSeg(l.from[0], l.from[1], l.to[0], l.to[1], x0, x1, y0, y1, !!l.extend);
      if (!s) return;
      el("line", { class: "ln", x1: X(s[0]), y1: Y(s[1]), x2: X(s[2]), y2: Y(s[3]),
                   style: "stroke:" + col + (o.dash ? ";stroke-dasharray:5 4" : "") + (l.width ? ";stroke-width:" + l.width : "") }, geo);
      if (l.label) {   // at the end with the larger x (the upper end of a vertical line), set back from the edge
        var vert = Math.abs(s[2] - s[0]) < 1e-9 * (x1 - x0), e = (vert ? s[3] >= s[1] : s[2] >= s[0]) ? [s[2], s[3]] : [s[0], s[1]];
        tag(clamp(X(e[0]), m.l + 4, W - m.r - 4), clamp(Y(e[1]), m.t + 12, H - m.b - 4) - 5, l.label, "end", l);
      }
    });
    // vectors: a shaft and a filled head, both in the vector's colour
    vectors.forEach(function (v, i) {
      var f = v.from || [0, 0], col = color(v.color || String(i % 4 + 1)), w = v.width || 2;
      var x1p = X(f[0]), y1p = Y(f[1]), x2p = X(v.to[0]), y2p = Y(v.to[1]), L = Math.hypot(x2p - x1p, y2p - y1p);
      if (L < 1) return;
      var ux = (x2p - x1p) / L, uy = (y2p - y1p) / L, hl = Math.min(11, L * 0.6), hw = hl * 0.4, bxp = x2p - ux * hl, byp = y2p - uy * hl;
      el("line", { class: "vsh", x1: x1p, y1: y1p, x2: bxp + ux * 1, y2: byp + uy * 1, style: "stroke:" + col + ";stroke-width:" + w + (v.dash ? ";stroke-dasharray:5 4" : "") }, geo);
      el("polygon", { class: "vhd", points: x2p + "," + y2p + " " + (bxp - uy * hw) + "," + (byp + ux * hw) + " " + (bxp + uy * hw) + "," + (byp - ux * hw), style: "fill:" + col }, geo);
      if (v.label) {   // beyond the tip, on the side the arrow points to
        var anchor = ux > 0.35 ? "start" : ux < -0.35 ? "end" : "middle";
        tag(x2p + ux * 9, y2p + uy * 9 + (uy > 0.35 ? 11 : uy < -0.35 ? -1 : 4), v.label, anchor, v, uy);
      }
    });
    // data points
    var n = 0; series.forEach(function (s) { n += s.x.length; });
    series.forEach(function (s, i) {
      var r = s.r || (n > 150 ? 2.6 : n > 40 ? 3.4 : 4.5), col = color(s.color || String(i + 1));
      s.x.forEach(function (xv, j) {
        var yv = s.y[j]; if (yv == null || !isFinite(xv) || !isFinite(yv) || !inside(xv, yv)) return;
        el("circle", { class: "pt", cx: X(xv), cy: Y(yv), r: r, style: "fill:" + col, "fill-opacity": n > 150 ? 0.75 : null }, svg);
        if (s.labels && s.labels[j]) tag(X(xv) + 7, Y(yv) - 7, s.labels[j], "start", {});
      });
    });
    // curves: one path per curve, so that a dash pattern runs along the whole curve; over the cloud of points (a
    // frontier through simulated portfolios) and under the marked points and labels, in their own clipped group
    var cg = curves.length ? el("g", { class: "geo" }, svg) : null;
    if (cg) clipTo(svg, cg, m.l, m.t, pw, ph);
    curves.forEach(function (cv) {
      var col = color(cv.color || "var(--ink-2)"), d = "", pen = false, last = null;
      cv.x.forEach(function (xv, j) {
        var yv = cv.y[j];
        if (xv == null || yv == null || !isFinite(xv) || !isFinite(yv)) { pen = false; return; }
        d += (pen ? "L" : "M") + X(xv).toFixed(1) + "," + Y(yv).toFixed(1); pen = true;
        if (inside(xv, yv) && (!last || xv >= last[0])) last = [xv, yv];
      });
      if (!d) return;
      el("path", { class: "ln", d: d, style: "fill:none;stroke:" + col + (cv.dash ? ";stroke-dasharray:5 4" : "") + (cv.width ? ";stroke-width:" + cv.width : "") }, cg);
      if (cv.label && last) tag(clamp(X(last[0]), m.l + 4, W - m.r - 4), clamp(Y(last[1]), m.t + 12, H - m.b - 4) - 5, cv.label, "end", cv);
    });
    pts.forEach(function (p) {
      if (!inside(p.at[0], p.at[1])) return;
      el("circle", { class: "pt", cx: X(p.at[0]), cy: Y(p.at[1]), r: p.r || 4.5, style: "fill:" + color(p.color || "var(--ink)") }, svg);
      if (p.label) tag(X(p.at[0]) + 8, Y(p.at[1]) - 8, p.label, "start", p);
    });
    drawTags();
    // hover: the nearest series point, vector tip or marked point within 18 px
    var cand = [];
    function addCand(col, head, xv, yv) { if (yv != null && isFinite(xv) && isFinite(yv) && inside(xv, yv)) cand.push({ x: X(xv), y: Y(yv), col: col, head: head, xv: xv, yv: yv }); }
    series.forEach(function (s, i) { s.x.forEach(function (xv, j) { addCand(s.color || String(i + 1), (s.name || "") + (s.labels && s.labels[j] ? " · " + s.labels[j] : ""), xv, s.y[j]); }); });
    vectors.forEach(function (v, i) { addCand(v.color || String(i % 4 + 1), v.label || "vector", v.to[0], v.to[1]); });
    pts.forEach(function (p) { addCand(p.color || "var(--ink)", p.label || "point", p.at[0], p.at[1]); });
    var ring = el("circle", { class: "hl", r: 8, visibility: "hidden" }, svg);
    var hit = el("rect", { x: m.l, y: m.t, width: pw, height: ph, fill: "transparent" }, svg);
    function leave() { c.tip.hidden = true; ring.setAttribute("visibility", "hidden"); }
    function move(ev) {
      var p = svgPoint(c, ev), best = null, bd = 18 / p.k;
      cand.forEach(function (q) { var d = Math.hypot(q.x - p.x, q.y - p.y); if (d < bd) { bd = d; best = q; } });
      if (!best) { leave(); return; }
      ring.setAttribute("cx", best.x); ring.setAttribute("cy", best.y); ring.setAttribute("visibility", "visible");
      var yi = yl ? ys.ticks.indexOf(best.yv) : -1;   // a point on a labelled tick (a forest plot's row): the label in full
      showTip(c, '<div class="hd">' + rich(best.head) + "</div>" + tipRow(best.col, xs.name || "x", fmt(best.xv, xs.fmt)) + tipRow(best.col, ys.name || "y", yi >= 0 && ys.tickLabels[yi] != null ? rich(ys.tickLabels[yi]) : fmt(best.yv, ys.fmt)), best.x, best.y);
    }
    hit.addEventListener("pointermove", move); hit.addEventListener("pointerdown", move); hit.addEventListener("pointerleave", leave);
    return { X: X, Y: Y, svg: svg };
  }
  Book.scatter = function (host, spec) { return xyPlot(host, spec, false); };
  Book.vectorDiagram = function (host, spec) { return xyPlot(host, spec, true); };

  /* the chart types by their spec.type; a spec without one is a line chart */
  var CHART_TYPES = { line: "lineChart", bar: "barChart", heatmap: "heatmap", scatter: "scatter", vector: "vectorDiagram" };
  Book.chart = function (host, spec) {
    var f = Book[CHART_TYPES[spec.type || "line"]];
    if (!f) throw new Error("unknown chart type: " + spec.type);
    return f(host, spec);
  };

  /* ---------------- probability distributions (Book.dist) ---------------- */
  // For widgets. build/qa/test_bookjs_dist.py checks every function against SciPy: run it after any change here.
  var SQRT2PI = 2.5066282746310002, LN_SQRT_2PI = 0.9189385332046728, LN_SQRT_PI = 0.5723649429247001, EPS = 2.220446049250313e-16;
  function expHalfSq(z) {   // exp(−z²/2), with z² split so that its rounding error does not grow with z (Cody)
    var h = Math.trunc(z * 16) / 16;
    return Math.exp(-h * h / 2) * Math.exp(-(z - h) * (z + h) / 2);
  }
  function phi(z) { return z === Infinity || z === -Infinity ? 0 : expHalfSq(z) / SQRT2PI; }
  // Phi: W. J. Cody's rational approximations (Math. Comp. 1969), as in R's pnorm; relative error near 1e-15 in both tails
  var CA = [2.2352520354606839287, 161.02823106855587881, 1067.6894854603709582, 18154.981253343561249, 0.065682337918207449113],
      CB = [47.20258190468824187, 976.09855173777669322, 10260.932208618978205, 45507.789335026729956],
      CC = [0.39894151208813466764, 8.8831497943883759412, 93.506656132177855979, 597.27027639480026226, 2494.5375852903726711,
            6848.1904505362823326, 11602.651437647350124, 9842.7148383839780218, 1.0765576773720192317e-8],
      CD = [22.266688044328115691, 235.38790178262499861, 1519.377599407554805, 6485.558298266760755, 18615.571640885098091,
            34900.952721145977266, 38912.003286093271411, 19685.429676859990727],
      CP = [0.21589853405795699, 0.1274011611602473639, 0.022235277870649807, 0.001421619193227893466, 2.9112874951168792e-5,
            0.02307344176494017303],
      CQ = [1.28426009614491121, 0.468238212480865118, 0.0659881378689285515, 0.00378239633202758244, 7.29751555083966205e-5];
  function PhiHalf(z) {   // Phi(z) − 1/2 for |z| <= 0.67448975, without the cancellation of Phi(z) − 0.5
    var zz = z * z, num = CA[4] * zz, den = zz;
    for (var i = 0; i < 3; i++) { num = (num + CA[i]) * zz; den = (den + CB[i]) * zz; }
    return z * (num + CA[3]) / (den + CB[3]);
  }
  function Phi(z) {
    if (isNaN(z)) return NaN;
    var y = Math.abs(z), t, i, num, den;
    if (y <= 0.67448975) return 0.5 + PhiHalf(z);
    if (y <= 5.656854249492381) {   // up to √32
      num = CC[8] * y; den = y;
      for (i = 0; i < 7; i++) { num = (num + CC[i]) * y; den = (den + CD[i]) * y; }
      t = (num + CC[7]) / (den + CD[7]);
    } else if (y < 37.5193) {       // beyond, the lower tail is below the smallest normal double
      var r = 1 / (z * z); num = CP[5] * r; den = r;
      for (i = 0; i < 4; i++) { num = (num + CP[i]) * r; den = (den + CQ[i]) * r; }
      t = (0.3989422804014327 - r * (num + CP[4]) / (den + CQ[4])) / y;
    } else return z > 0 ? 1 : 0;
    var tail = expHalfSq(y) * t;    // Pr(Z > |z|)
    return z > 0 ? 1 - tail : tail;
  }
  // PhiInv: P. J. Acklam's rational approximation (relative error 1.15e-9) and one Halley step. Above 1/2 it works on
  // 1 − p, which is exact there; near 1/2 the step compares Phi(x) − 1/2 with p − 1/2, both free of cancellation.
  var AA = [-39.69683028665376, 220.9460984245205, -275.9285104469687, 138.3577518672690, -30.66479806614716, 2.506628277459239],
      AB = [-54.47609879822406, 161.5858368580409, -155.6989798598866, 66.80131188771972, -13.28068155288572],
      AC = [-0.007784894002430293, -0.3223964580411365, -2.400758277161838, -2.549732539343734, 4.374664141464968, 2.938163982698783],
      AD = [0.007784695709041462, 0.3224671290700398, 2.445134137142996, 3.754408661907416];
  function PhiInv(p) {
    if (!(p >= 0 && p <= 1)) return NaN;
    if (p === 0) return -Infinity;
    if (p === 1) return Infinity;
    if (p > 0.5) return -PhiInv(1 - p);
    var x, q, r;
    if (p < 0.02425) {
      q = Math.sqrt(-2 * Math.log(p));
      x = (((((AC[0] * q + AC[1]) * q + AC[2]) * q + AC[3]) * q + AC[4]) * q + AC[5]) / ((((AD[0] * q + AD[1]) * q + AD[2]) * q + AD[3]) * q + 1);
    } else {
      q = p - 0.5; r = q * q;
      x = (((((AA[0] * r + AA[1]) * r + AA[2]) * r + AA[3]) * r + AA[4]) * r + AA[5]) * q /
          (((((AB[0] * r + AB[1]) * r + AB[2]) * r + AB[3]) * r + AB[4]) * r + 1);
    }
    if (x <= -37.5193) return x;   // p below the smallest normal double, where Phi underflows: Acklam's value stands
    var u = (Math.abs(x) <= 0.67448975 ? PhiHalf(x) - (p - 0.5) : Phi(x) - p) / phi(x);
    return x - u / (1 + x * u / 2);
  }
  // log Γ(x), x > 0: Lanczos (g = 7, nine terms): Γ(z) = √(2π) t^(z − 1/2) e^(−t) A(z), t = z + 6.5, for z >= 1/2.
  // The error is relative (about 1e-15) except where log Γ is near 0, around x = 1 and x = 2: there it is absolute,
  // a few 1e-15 (the sum of terms of size 1 to 10 that cancel), so the relative error there is unbounded.
  var LG = [0.99999999999980993, 676.5203681218851, -1259.1392167224028, 771.32342877765313, -176.61502916214059,
            12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7];
  function lanczosA(z) { var a = LG[0]; for (var k = 1; k < 9; k++) a += LG[k] / (z - 1 + k); return a; }
  function lgamma(x) {
    if (!(x > 0)) return NaN;
    if (x === Infinity) return Infinity;
    if (x < 0.5) return lgamma(x + 1) - Math.log(x);
    var t = x + 6.5;
    return LN_SQRT_2PI + (x - 0.5) * Math.log(t) - t + Math.log(lanczosA(x));
  }
  // log Γ(z + h) − log Γ(z) from the Lanczos terms, without subtracting two large logarithms (Student-t for large ν)
  function lgammaDiff(z, h) {
    if (z < 0.5) return lgamma(z + h) - lgamma(z);
    var t = z + 6.5;
    return (z - 0.5) * Math.log1p(h / t) + h * (Math.log(t + h) - 1) + Math.log(lanczosA(z + h) / lanczosA(z));
  }
  // continued fraction of the regularized incomplete beta function (Numerical Recipes, modified Lentz)
  function betacf(x, a, b) {
    var TINY = 1e-300, c = 1, d = 1 - (a + b) * x / (a + 1);
    d = 1 / (Math.abs(d) < TINY ? TINY : d);
    var h = d;
    for (var m = 1; m <= 20000; m++) {
      var m2 = 2 * m, aa = m * (b - m) * x / ((a - 1 + m2) * (a + m2));
      d = 1 + aa * d; d = 1 / (Math.abs(d) < TINY ? TINY : d);
      c = 1 + aa / c; if (Math.abs(c) < TINY) c = TINY;
      h *= d * c;
      aa = -(a + m) * (a + b + m) * x / ((a + m2) * (a + 1 + m2));
      d = 1 + aa * d; d = 1 / (Math.abs(d) < TINY ? TINY : d);
      c = 1 + aa / c; if (Math.abs(c) < TINY) c = TINY;
      var del = d * c; h *= del;
      if (Math.abs(del - 1) <= EPS) break;
    }
    return h;
  }
  function tPdf(x, nu) {
    if (isNaN(x) || !(nu > 0)) return NaN;
    if (nu === Infinity) return phi(x);
    var u = Math.abs(x / Math.sqrt(nu)), l1 = u > 1e150 ? 2 * Math.log(u) : Math.log1p(u * u);   // log(1 + x²/ν)
    return Math.exp(lgammaDiff(nu / 2, 0.5) - 0.5 * Math.log(nu * Math.PI) - (nu + 1) / 2 * l1);
  }
  // 2 Pr(T <= −|x|) = I_w(ν/2, 1/2) with w = ν/(ν + x²) = 1/(1 + s), s = x²/ν; 1 − w = s/(1 + s) is formed directly.
  // Relative error about 1e-12 up to ν = 1e4; beyond, the continued fraction cancels near w = 1 and its error grows
  // about in proportion to ν (4e-11 at ν = 1e6, 2e-9 at 1e8). Above ν = 1e8 the normal approximation of A&S 26.7.8
  // takes over: its error falls as 1/ν² and grows with |x| (1e-8 just above 1e8 at x = −37, 1e-10 at ν = 1e9, and from
  // ν = 1e10 on below the 2e-13 that Phi's own rounding leaves in the far tail).
  function tCdf(x, nu) {
    if (isNaN(x) || !(nu > 0)) return NaN;
    if (nu === Infinity) return Phi(x);
    if (x === 0) return 0.5;
    if (!isFinite(x)) return x > 0 ? 1 : 0;
    if (nu > 1e8) {   // Abramowitz & Stegun 26.7.8 (R's pt used it for large ν up to version 2.6.0): Phi(x (1 − g) / √(1 + 2x²g)), g = 1/(4ν)
      var g = 1 / (4 * nu), xx = x * x;
      return Phi(isFinite(xx) ? x * (1 - g) / Math.sqrt(1 + 2 * xx * g) : (x > 0 ? 1 : -1) * (1 - g) / Math.sqrt(2 * g));
    }
    var a = nu / 2, u = Math.abs(x / Math.sqrt(nu)), big = u > 1e150, s = u * u;
    var w = big ? 0 : 1 / (1 + s), v = big ? 1 : s / (1 + s);
    var lw = big ? -2 * Math.log(u) : -Math.log1p(s), lv = big ? 0 : Math.log(s) - Math.log1p(s);
    var front = Math.exp(a * lw + 0.5 * lv - (LN_SQRT_PI - lgammaDiff(a, 0.5)));   // w^a (1 − w)^(1/2) / B(ν/2, 1/2)
    var p = w < (a + 1) / (a + 2.5) ? 0.5 * front * betacf(w, a, 0.5) / a : 0.5 - front * betacf(v, 0.5, a);
    return x < 0 ? p : 1 - p;
  }
  // C. Loader's saddle-point form of λ^x e^−λ / x! (as in R's dpois_raw and dbinom_raw): accurate to rounding for any
  // size of x and λ, where a difference of log-gammas such as k log λ − λ − log k! loses digits
  function stirlerr(n) {   // log n! − log(√(2πn) (n/e)^n), n > 0
    if (n <= 15) return lgamma(n + 1) - (n + 0.5) * Math.log(n) + n - LN_SQRT_2PI;
    var nn = n * n;
    if (n > 500) return (1 / 12 - 1 / 360 / nn) / n;
    if (n > 80) return (1 / 12 - (1 / 360 - 1 / 1260 / nn) / nn) / n;
    if (n > 35) return (1 / 12 - (1 / 360 - (1 / 1260 - 1 / 1680 / nn) / nn) / nn) / n;
    return (1 / 12 - (1 / 360 - (1 / 1260 - (1 / 1680 - 1 / 1188 / nn) / nn) / nn) / nn) / n;
  }
  function bd0(x, np) {   // x log(x/np) + np − x, by a series when x is near np
    if (Math.abs(x - np) < 0.1 * (x + np)) {
      var v = (x - np) / (x + np), s = (x - np) * v, ej = 2 * x * v;
      v *= v;
      for (var j = 1; j < 1000; j++) { ej *= v; var s1 = s + ej / (2 * j + 1); if (s1 === s) return s1; s = s1; }
    }
    return x * Math.log(x / np) + np - x;
  }
  function dpois(x, lam) { return Math.exp(-stirlerr(x) - bd0(x, lam)) / Math.sqrt(2 * Math.PI * x); }   // x > 0, λ > 0
  // regularized incomplete gamma P(a, x), or Q(a, x) = 1 − P when upper: the series below x = a + 1, the continued
  // fraction above it (Numerical Recipes), so that whichever of P and Q is small keeps its relative accuracy
  function incGamma(a, x, upper) {
    if (!(x > 0)) return upper ? 1 : 0;
    if (x === Infinity) return upper ? 0 : 1;
    var f = a * dpois(a, x), r, i;   // x^a e^−x / Γ(a)
    if (x < a + 1) {
      var del = 1 / a, sum = del;
      for (i = 1; i < 100000 && Math.abs(del) > Math.abs(sum) * EPS; i++) { del *= x / (a + i); sum += del; }
      r = sum * f;
      return upper ? 1 - r : r;
    }
    var b = x + 1 - a, c = 1e300, d = 1 / b, h = d;
    for (i = 1; i < 100000; i++) {
      var an = -i * (i - a); b += 2;
      d = an * d + b; d = 1 / (Math.abs(d) < 1e-300 ? 1e-300 : d);
      c = b + an / c; if (Math.abs(c) < 1e-300) c = 1e-300;
      var dl = d * c; h *= dl;
      if (Math.abs(dl - 1) <= EPS) break;
    }
    r = f * h;
    return upper ? r : 1 - r;
  }
  function isCount(k) { return k >= 0 && k === Math.floor(k) && isFinite(k); }
  function poissonPmf(k, lam) {
    if (!(lam >= 0)) return NaN;
    if (!isCount(k)) return 0;
    if (lam === 0 || k === 0) return k === 0 ? Math.exp(-lam) : 0;
    return dpois(k, lam);
  }
  function poissonCdf(k, lam) {   // Pr(N <= k) = Q(floor(k) + 1, λ)
    if (!(lam >= 0) || isNaN(k)) return NaN;
    if (k < 0) return 0;
    if (lam === 0 || k === Infinity) return 1;
    return incGamma(Math.floor(k) + 1, lam, true);
  }
  function binomPmf(k, n, p) {
    if (!isCount(n) || !(p >= 0 && p <= 1)) return NaN;
    if (!isCount(k) || k > n) return 0;
    if (p === 0 || p === 1) return k === (p === 0 ? 0 : n) ? 1 : 0;
    if (k === 0) return Math.exp(n * Math.log1p(-p));
    if (k === n) return Math.exp(n * Math.log(p));
    var q = 1 - p, lc = stirlerr(n) - stirlerr(k) - stirlerr(n - k) - bd0(k, n * p) - bd0(n - k, n * q);   // Loader, as dbinom_raw
    return Math.exp(lc - 0.5 * (Math.log(2 * Math.PI) + Math.log(k) + Math.log1p(-k / n)));
  }
  function chi2Cdf(x, k) { return isNaN(x) || !(k > 0) ? NaN : incGamma(k / 2, x / 2, false); }
  Book.dist = { phi: phi, Phi: Phi, PhiInv: PhiInv, lgamma: lgamma, tPdf: tPdf, tCdf: tCdf,
                poissonPmf: poissonPmf, poissonCdf: poissonCdf, binomPmf: binomPmf, chi2Cdf: chi2Cdf };

  /* ---------------- seeded random numbers (Book.rng) ---------------- */
  // Book.rng(seed): sfc32 (C. Doty-Humphrey's small fast counting generator, from PractRand), its four words filled
  // from the seed, a whole number taken modulo 2^32 (anything else throws), by splitmix32. The same seed gives the
  // same numbers in every browser:
  // uniform() and int() use integer arithmetic only, and normal() takes its logarithm from lnDet below instead of
  // Math.log, whose last bit may differ between JavaScript engines. It does not reproduce NumPy's streams: a widget
  // and a lab given the same seed draw different numbers.
  function lnDet(x) {   // ln x for 0 < x <= 1 from +, −, ×, ÷ only: x = m 2^e, m in [√½, √2), ln m = 2 atanh((m − 1)/(m + 1))
    var e = 0;
    while (x < 0.7071067811865476) { x *= 2; e--; }   // exact: doubling only changes the exponent
    var z = (x - 1) / (x + 1), z2 = z * z, t = z, s = 0;
    for (var k = 1; k <= 25; k += 2) { s += t / k; t *= z2; }   // |z| < 0.172: thirteen terms reach 1e-17
    return e * 0.6931471803691238 + (e * 1.9082149292705877e-10 + 2 * s);   // ln 2 in two parts (fdlibm)
  }
  Book.rng = function (seed) {
    if (typeof seed !== "number") throw new TypeError("Book.rng(seed): the seed must be a number");
    if (!isFinite(seed) || seed !== Math.floor(seed)) throw new RangeError("Book.rng(seed): the seed must be a whole number");
    var w = seed >>> 0;
    function sm() {   // splitmix32: a Weyl sequence through a 32-bit integer hash
      w = w + 0x9e3779b9 | 0;
      var t = Math.imul(w ^ w >>> 16, 0x21f0aaad);
      t = Math.imul(t ^ t >>> 15, 0x735a2d97);
      return (t ^ t >>> 15) >>> 0;
    }
    var a = sm(), b = sm(), c = sm(), d = sm(), spare = null;
    function next() {   // one 32-bit output of sfc32; d is its counter
      var t = (a + b | 0) + d | 0;
      d = d + 1 | 0; a = b ^ b >>> 9; b = c + (c << 3) | 0; c = (c << 21 | c >>> 11) + t | 0;
      return t >>> 0;
    }
    for (var i = 0; i < 12; i++) next();   // mix the seed through the state before the first output
    function uniform() { return ((next() >>> 5) * 67108864 + (next() >>> 6)) / 9007199254740992; }   // 53 bits, [0, 1)
    return {
      uniform: uniform,
      normal: function () {   // Marsaglia's polar method; the second variate of each pair is kept for the next call
        if (spare !== null) { var z = spare; spare = null; return z; }
        var x, y, s;
        do { x = 2 * uniform() - 1; y = 2 * uniform() - 1; s = x * x + y * y; } while (s >= 1 || s === 0);
        var f = Math.sqrt(-2 * lnDet(s) / s);
        spare = y * f;
        return x * f;
      },
      int: function (n) {   // 0 .. n − 1, all equally likely: draws past the last whole multiple of n are redrawn
        if (!(n >= 1 && n <= 4294967296 && n === Math.floor(n))) throw new RangeError("rng.int(n): n must be an integer from 1 to 2^32");
        var lim = 4294967296 - 4294967296 % n, r;
        do r = next(); while (r >= lim);
        return r % n;
      }
    };
  };

  /* ---------------- widget controls (Book.controls) ---------------- */
  // Book.controls(host, defs, onChange) appends a <div class="controls"> to host, in the markup of the modules' own
  // controlsHTML copies. defs: [{type: 'range' (default) | 'select' | 'button', id, key, label, ...}]
  //   range:  min, max, step, value; fmt (a Book.fmt code, or a function of the value) for the live value by the label
  //   select: options [[value, text], ...] (or plain strings), value (the option selected at first)
  //   button: label only
  // onChange(values, id): values is {key or id: value}, a number for a slider and a string for a select; id names the
  // control that changed (null from fire()). Slider and select input is coalesced to one call per animation frame, so
  // a slow redraw never queues up; when several controls change within one frame, id names the last of them (values
  // holds every current value). A button click calls at once. Returns {el, values(), fire()}: fire() calls onChange
  // now, for the first drawing (Book.controls does not) and for host.__redraw.
  Book.controls = function (host, defs, onChange) {
    var box = document.createElement("div"); box.className = "controls";
    box.innerHTML = defs.map(function (d) {
      if (d.type === "button") return '<button type="button" id="' + d.id + '">' + d.label + "</button>";
      if (d.type === "select")
        return '<label for="' + d.id + '">' + d.label + '<select id="' + d.id + '">' + d.options.map(function (o) {
          var v = Array.isArray(o) ? o[0] : o;
          return '<option value="' + v + '"' + (d.value != null && String(d.value) === String(v) ? " selected" : "") + ">" + (Array.isArray(o) ? o[1] : o) + "</option>";
        }).join("") + "</select></label>";
      return '<label for="' + d.id + '">' + d.label + ' <span class="v" id="' + d.id + '-v"></span>' +
        '<input type="range" id="' + d.id + '" min="' + d.min + '" max="' + d.max + '" step="' + d.step + '" value="' + d.value + '"></label>';
    }).join("");
    host.appendChild(box);
    var els = defs.map(function (d, i) { var c = box.children[i]; return d.type === "button" ? c : c.querySelector(d.type === "select" ? "select" : "input"); });
    function values() {
      var o = {};
      defs.forEach(function (d, i) { if (d.type !== "button") o[d.key || d.id] = d.type === "select" ? els[i].value : +els[i].value; });
      return o;
    }
    function show(i) {   // a slider's live value
      var d = defs[i], v = +els[i].value;
      box.children[i].querySelector(".v").textContent = typeof d.fmt === "function" ? d.fmt(v) : d.fmt ? fmt(v, d.fmt) : String(v);
    }
    var queued = false, last = null;
    defs.forEach(function (d, i) {
      if (d.type === "button") { els[i].addEventListener("click", function () { onChange(values(), d.id); }); return; }
      if (d.type !== "select") show(i);
      els[i].addEventListener("input", function () {
        if (d.type !== "select") show(i);
        last = d.id;
        if (!queued) { queued = true; requestAnimationFrame(function () { queued = false; onChange(values(), last); }); }
      });
    });
    return { el: box, values: values, fire: function () { onChange(values(), null); } };
  };

  /* render every data chart on the page; re-render on width change */
  function renderCharts() {
    document.querySelectorAll("[data-chart]").forEach(function (h) {
      var src = document.getElementById("chart-" + h.getAttribute("data-chart"));
      if (!src) return;
      try {   // everything per chart is inside the try, so one bad spec leaves the other charts on the page alone
        var spec = JSON.parse(src.textContent);
        if (spec.x && spec.x.type === "date") {   // dates may be ISO strings or epoch milliseconds, in series and annotations alike
          var toT = function (d) { return typeof d === "number" ? d : Date.parse(d + "T00:00:00Z"); };
          if (spec.x.values) spec.x.values = spec.x.values.map(toT);   // the shared x
          spec.series.forEach(function (s) { if (s.x) s.x = s.x.map(toT); });
          (spec.ann || []).forEach(function (a) { ["x", "x0", "x1"].forEach(function (k) { if (a[k] != null) a[k] = toT(a[k]); }); });
        }
        Book.chart(h, spec);
      } catch (e) { h.innerHTML = '<p class="w-note">This chart could not be drawn.</p>'; if (window.console) console.error("chart " + h.getAttribute("data-chart") + ": " + e.message); }
    });
  }
  Book.renderCharts = renderCharts;

  /* KaTeX pins an equation tag to the right edge of its display. When the centred formula and the tag do not both
     fit, the tag would print over the formula, so it moves to a line of its own below, as in amsmath. width: the
     main column's width to lay out for (the A4 text width when printing); default, the current one. */
  var A4_TEXT_WIDTH = 680.3, PRINT_FONT_PX = 13.8667;   // 180 mm at 96 px/in; the body's 10.4 pt in print (book.css)
  function layoutTags(width) {
    var page = document.querySelector(".page"), dw = width && page ? width - page.clientWidth : 0;
    // from the screen layout (beforeprint fires before print styles apply), formulas shrink to the print font
    var k = width && !printing() ? PRINT_FONT_PX / parseFloat(getComputedStyle(document.body).fontSize) : 1;
    document.querySelectorAll(".katex-display").forEach(function (d) {
      var tag = d.querySelector(".katex-html > .tag"), bases = tag ? tag.parentElement.querySelectorAll(":scope > .base") : [];
      if (!bases.length) return;
      if (!d.clientWidth) { d.classList.add("tag-below"); return; }   // hidden: below until shown; toggle re-decides
      d.classList.remove("tag-below");
      var f = bases[bases.length - 1].getBoundingClientRect().right - bases[0].getBoundingClientRect().left;
      var gap = 0.5 * parseFloat(getComputedStyle(tag).fontSize);
      if (k * (f + 2 * (tag.getBoundingClientRect().width + gap)) > d.clientWidth + dw) d.classList.add("tag-below");
    });
  }
  Book.layoutTags = layoutTags;
  Book.A4_TEXT_WIDTH = A4_TEXT_WIDTH;
  function printing() { var m = mq("print"); return !!(m && m.matches); }

  function initWidgets() {
    document.querySelectorAll("[data-widget]").forEach(function (h) {
      var f = Book.widgets[h.getAttribute("data-widget")];
      if (f && !h.__init) { h.__init = true; try { f(h); } catch (e) { h.insertAdjacentHTML("beforeend", '<p class="w-note">This interactive figure could not start in this browser.</p>'); } }
    });
  }

  /* ---------------- page chrome ---------------- */
  function chrome() {
    drawer(); trackReading();
    // learning-outcome mastery boxes
    var lm = document.body.getAttribute("data-lm");
    document.querySelectorAll(".lo input[type=checkbox]").forEach(function (cb) {
      var key = "ftck-lo-" + lm + "-" + cb.id;
      if (store.get(key) === "1") cb.checked = true;
      cb.addEventListener("change", function () { store.set(key, cb.checked ? "1" : "0"); });
    });
    // copy buttons
    document.querySelectorAll(".code").forEach(function (blk) {
      var b = blk.querySelector("button.copy"), pre = blk.querySelector("pre");
      if (!b || !pre) return;
      b.addEventListener("click", function () {
        var txt = pre.innerText;
        var done = function () { b.textContent = "Copied"; setTimeout(function () { b.textContent = "Copy"; }, 1400); };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(txt).then(done, function () { selectPre(pre); b.textContent = "Selected — press Ctrl+C"; });
        } else { selectPre(pre); b.textContent = "Selected — press Ctrl+C"; }
      });
    });
    // outline scroll-spy. The active entry is readingHead()'s. An observer that waits for a heading to cross a band
    // misses jumps: a clicked sub-heading lands above the band and never crosses it. A clicked entry stays active until
    // the reader scrolls again, so a short section at the end of the page still lights up. A hash that is not an
    // outline entry (browser back, the address bar, an in-text link) releases that hold and the entry is recomputed
    // from the scroll position. The outline panel scrolls itself (its own scrollTop, never scrollIntoView) to keep the
    // active entry in view.
    var links = Array.prototype.slice.call(document.querySelectorAll(".outline a"));
    if (links.length) {
      var heads = outlineTargets();
      var current = null, pinned = false, queued = false;
      var keepVisible = function (a) {
        var o = a.closest(".outline");
        if (!o || o.clientHeight === 0 || o.scrollHeight <= o.clientHeight) return;
        var r = a.getBoundingClientRect(), orr = o.getBoundingClientRect();
        var top = Math.max(orr.top, 0) + 24, bottom = Math.min(orr.bottom, window.innerHeight) - 24;
        if (r.bottom > bottom) o.scrollTop += r.bottom - bottom;
        else if (r.top < top) o.scrollTop -= top - r.top;
      };
      var setActive = function (a) {
        if (a !== current) {
          if (current) current.classList.remove("active");
          current = a;
          if (a) a.classList.add("active");
        }
        if (a) keepVisible(a);
      };
      var spy = function () {
        queued = false;
        if (pinned) return;
        var k = readingHead(heads);
        setActive(k < 0 ? null : links[k]);
      };
      var pinTo = function (hash) {
        for (var i = 0; i < links.length; i++) if (links[i].getAttribute("href") === hash) { pinned = true; setActive(links[i]); return true; }
        return false;
      };
      window.addEventListener("scroll", function () { if (!queued) { queued = true; requestAnimationFrame(spy); } }, { passive: true });
      // After the jump, the keyboard must scroll the page, not the outline panel that was clicked: Chromium scrolls the
      // box clicked last, so the focus moves to the target (a section or a heading). The target is made focusable for
      // that (data-jump: no focus ring, book.css) until a click lands inside it, which then focuses as it always did,
      // so a wide display in that section still scrolls with the arrow keys.
      var jumped = [];
      var focusTarget = function (hash) {
        var t = document.getElementById(decodeURIComponent(hash.slice(1)));
        if (!t) return;
        if (!t.hasAttribute("tabindex")) { t.setAttribute("tabindex", "-1"); t.setAttribute("data-jump", ""); jumped.push(t); }
        t.focus({ preventScroll: true });
      };
      window.addEventListener("mousedown", function (e) {
        jumped = jumped.filter(function (t) {
          if (!t.contains(e.target)) return true;
          t.removeAttribute("tabindex"); t.removeAttribute("data-jump");
          return false;
        });
      }, { passive: true, capture: true });
      links.forEach(function (a) {
        a.addEventListener("click", function (e) {
          if (e.button !== 0 || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;   // a new tab or window: no jump here
          var h = a.getAttribute("href");
          pinTo(h);
          setTimeout(function () { if (location.hash === h) focusTarget(h); }, 0);   // after the browser's own jump
        });
      });
      window.addEventListener("hashchange", function () {
        var h = location.hash;
        if (pinTo(h)) setTimeout(function () { focusTarget(h); }, 0);   // Back and Forward land on an entry: same as a click
        else { pinned = false; requestAnimationFrame(spy); }   // after the browser has restored the scroll position
      });
      ["wheel", "touchstart", "keydown", "mousedown"].forEach(function (ev) {
        window.addEventListener(ev, function () { if (pinned) { pinned = false; } }, { passive: true, capture: true });
      });
      if (!(location.hash && pinTo(location.hash))) spy();
    }
  }
  function selectPre(pre) { var r = document.createRange(); r.selectNodeContents(pre); var s = window.getSelection(); s.removeAllRanges(); s.addRange(r); }

  /* On narrow screens (book.css, 920 px) the contents rail is a drawer over the page. The page behind it is fixed at
     its scroll offset while the drawer is open (body top = -offset; overflow: hidden does not stop iOS Safari once
     its toolbar has collapsed), so window.pageYOffset reads 0 until it closes and the offset is restored. Fixing and
     releasing the body lays out the whole page again (about 200 ms on the largest module at a phone's speed), so it
     waits for the first frame of the slide, which the compositor then finishes. Closes on the toggle, Escape, the
     backdrop, a link in the drawer, focus moving into the page, Back or Forward, the page being left or hidden, or the
     window widening past the breakpoint. */
  function drawer() {
    var tg = document.querySelector(".rail-toggle"), rail = document.getElementById("rail"), bar = document.querySelector(".topbar");
    if (!tg || !rail) return;
    var body = document.body, narrow = mq("(max-width: 920px)"), x0 = 0, y0 = 0, locked = false, pending = 0, shut = 0;
    var scrim = document.createElement("div");
    scrim.className = "rail-backdrop";
    rail.parentNode.insertBefore(scrim, rail.nextSibling);
    var later = function (f) { var id = ++pending; requestAnimationFrame(function () { setTimeout(function () { if (id === pending) f(); }, 0); }); };
    // The text can reflow while the page is fixed (the phone turned, a font arrived), and the old offset would then land
    // screens away: the first block at the reading line (a paragraph, list item, table row, figure…; a list or a table can
    // fill the window) goes back to where it was, with the same point of it on the line, as a tall paragraph gets shorter.
    var anchor = null, a0 = 0, f0 = 0, line = 0;
    var lock = function () {
      if (locked) return;
      locked = true; x0 = window.pageXOffset; y0 = window.pageYOffset; anchor = null;
      var els = document.querySelectorAll("main p, main li, main tr, main h2, main h3, main figure, main pre, main summary");
      line = parseFloat(getComputedStyle(root).scrollPaddingTop) || 0;
      for (var i = 0; i < els.length; i++) {
        var r = els[i].getBoundingClientRect();
        if (r.height && r.bottom > line) { anchor = els[i]; a0 = r.top; f0 = r.top < line ? (line - r.top) / r.height : 0; break; }
      }
      body.style.top = -y0 + "px"; root.classList.add("rail-lock");
    };
    var unlock = function () {
      if (!locked) return;
      locked = false; root.classList.remove("rail-lock"); body.style.top = "";
      window.scrollTo(x0, y0);
      if (anchor && anchor.isConnected) {
        var r = anchor.getBoundingClientRect(), dy = f0 ? r.top + f0 * r.height - line : r.top - a0;
        if (Math.abs(dy) >= 0.5) window.scrollBy(0, dy);
      }
      anchor = null;
    };
    var isOpen = function () { return rail.classList.contains("open"); };
    var place = function () {   // the bar's bottom edge moves with the safe-area inset when a phone turns
      // on these two only: set on <html>, it would restyle the whole page
      var top = Math.max(0, bar ? bar.getBoundingClientRect().bottom : 0) + "px";
      rail.style.setProperty("--rail-top", top); scrim.style.setProperty("--rail-top", top);
    };
    var open = function () {
      place(); shut++; rail.inert = false;
      rail.classList.add("open"); scrim.classList.add("open"); tg.setAttribute("aria-expanded", "true");
      var cur = rail.querySelector('a[aria-current="page"]') || rail.querySelector("a");
      if (cur) { rail.scrollTop = cur.offsetTop - (rail.clientHeight - cur.offsetHeight) / 2; cur.focus({ preventScroll: true }); }
      later(lock);
    };
    var close = function (refocus) {
      if (!isOpen()) return;
      rail.classList.remove("open"); scrim.classList.remove("open"); tg.setAttribute("aria-expanded", "false");
      if (refocus) tg.focus({ preventScroll: true });
      // out of the tab order while it slides out (it stays visible for the slide), then hidden by book.css
      var k = ++shut; rail.inert = true;
      setTimeout(function () { if (k === shut) rail.inert = false; }, 250);
      later(unlock);
    };
    tg.addEventListener("click", function () { if (isOpen()) close(true); else open(); });
    scrim.addEventListener("click", function () { close(true); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && isOpen()) close(true); });
    rail.addEventListener("click", function (e) {
      var a = e.target.closest && e.target.closest("a");
      if (!a || !isOpen() || e.button !== 0 || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
      if (a.getAttribute("aria-current") === "page") { e.preventDefault(); close(true); }   // reloading would lose the place
      else close(false);
    });
    document.addEventListener("focusin", function (e) {   // Tab past the last entry: back to Contents, where the page is
      if (isOpen() && !rail.contains(e.target) && !(bar && bar.contains(e.target))) close(true);
    });
    window.addEventListener("resize", function () { if (isOpen()) place(); });
    // The page reflowed under the drawer (the phone turned, the charts redrew, a font arrived): fixed again at the place
    // being read, so that it and the top bar stay in view (the old offset can lie past the end of a shorter page)
    if (window.ResizeObserver) new ResizeObserver(function () {
      if (locked) requestAnimationFrame(function () { if (locked) { unlock(); lock(); place(); } });
    }).observe(body);
    // Back or Forward within the page: unlocked at once, so that the browser's restoring of the history entry's scroll
    // position, after this event, moves the page (a locked page cannot scroll, and the later unlock would undo it)
    window.addEventListener("popstate", function () { close(false); unlock(); });
    // Leaving or reloading the page, or hiding it: closed and unlocked first, so that the scroll position the browser
    // keeps for the history entry, and the reading position (trackReading, registered after this), are the page's own
    var release = function () { if (locked || isOpen()) { close(true); unlock(); } };
    window.addEventListener("pagehide", release);
    document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden") release(); });
    var wide = function () {
      rail.style.transition = "none"; void getComputedStyle(rail).transform; rail.style.transition = "";   // no slide across the breakpoint
      if (narrow && !narrow.matches) { close(false); unlock(); rail.inert = false; }   // the lock's CSS has stopped applying
    };
    if (narrow) { if (narrow.addEventListener) narrow.addEventListener("change", wide); else if (narrow.addListener) narrow.addListener(wide); }
  }

  /* The heading being read, for the outline and the reading position: of the outline's targets, the last that has
     reached the reading line, which sits just below the spot where a jump puts a heading (html's scroll-padding-top).
     At the very bottom of the page the last headings may never reach the line, so there it is the last heading whose
     top is inside the window. -1 before the first. */
  function outlineTargets() {
    return Array.prototype.slice.call(document.querySelectorAll(".outline a"))
      .map(function (a) { return document.getElementById(decodeURIComponent(a.getAttribute("href").slice(1))); });
  }
  function readingHead(heads) {
    var line = (parseFloat(getComputedStyle(root).scrollPaddingTop) || 0) + 8, k = -1, i;
    for (i = 0; i < heads.length; i++) if (heads[i] && heads[i].getBoundingClientRect().top <= line) k = i;
    var room = root.scrollHeight - window.innerHeight;   // 0 while the drawer holds the page
    if (room > 1 && window.pageYOffset >= room - 2) {
      for (i = 0; i < heads.length; i++) if (heads[i] && heads[i].getBoundingClientRect().top < window.innerHeight) k = i;
    }
    return k;
  }

  /* Reading position, for the front page's Resume button: on a module page, the module and readingHead(), saved when
     it changes. The page in view owns the record: one opened in the background saves nothing until it is shown, and a
     page hidden or left saves only if no page shown since has saved (Back restores the earlier page from the cache
     before the later one's pagehide, which must not then overwrite it). The front page reads it (build_index.py
     RESUME_JS, the same key) and shows it only for a module it lists, and otherwise keeps its static Start link. */
  var LAST_KEY = "ftck-last-read";
  function trackReading() {
    var n = parseInt(document.body.getAttribute("data-lm"), 10), h1 = document.querySelector(".lm-title");
    if (!(n > 0) || !h1) return;
    var heads = outlineTargets(), page = "lm/lm" + (n < 10 ? "0" : "") + n + ".html", last = null, mine = null, queued = false;
    var save = function (always) {
      queued = false;
      var k = readingHead(heads), id = k < 0 ? "" : heads[k].id;
      if (id === last && !always) return;
      last = id; mine = JSON.stringify({ page: page, id: id, n: n, title: h1.textContent, t: Date.now() });
      store.set(LAST_KEY, mine);
    };
    var shown = function () { if (document.visibilityState !== "hidden") save(true); };
    var left = function () { if (mine !== null && store.get(LAST_KEY) === mine) save(true); };
    shown();
    window.addEventListener("scroll", function () { if (!queued) { queued = true; requestAnimationFrame(function () { save(false); }); } }, { passive: true });
    window.addEventListener("pageshow", function (e) { if (e.persisted) shown(); });
    window.addEventListener("pagehide", left);
    document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden") left(); else shown(); });
  }

  function boot() {
    initTheme(); chrome(); renderCharts(); initWidgets(); layoutTags();
    // charts measure their labels while drawing, and drawing is what starts a web font's download: if a font was
    // still loading then, draw again once it has arrived, so the labels are placed with their real widths
    var fontsLate = !!(document.fonts && document.fonts.status !== "loaded");
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () {
      if (printing()) return;
      if (fontsLate) { renderCharts(); document.querySelectorAll("[data-widget]").forEach(function (h) { if (h.__redraw) h.__redraw(); }); }
      layoutTags();
    });
    var lastW = window.innerWidth, t;
    window.addEventListener("resize", function () {
      clearTimeout(t);
      t = setTimeout(function () {
        if (!printing()) layoutTags();
        if (Math.abs(window.innerWidth - lastW) > 40) { lastW = window.innerWidth; renderCharts(); document.querySelectorAll("[data-widget]").forEach(function (h) { if (h.__redraw) h.__redraw(); }); }
      }, 180);
    });
    // printing: lay the tags out for the A4 text width, then back for the screen; an opened <details> may show a display
    window.addEventListener("beforeprint", function () { layoutTags(A4_TEXT_WIDTH); });
    window.addEventListener("afterprint", function () { layoutTags(); });
    document.addEventListener("toggle", function () { if (!printing()) layoutTags(); }, true);
  }
  Book.boot = boot;
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else setTimeout(boot, 0);
})();
