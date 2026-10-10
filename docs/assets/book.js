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
      default: s = String(Math.round(a * 1e6) / 1e6);
    }
    return (neg ? "−" : "") + s;
  }
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
  function niceStep(span, n) {
    var raw = span / Math.max(1, n), p = Math.pow(10, Math.floor(Math.log10(raw))), r = raw / p;
    return (r <= 1 ? 1 : r <= 2 ? 2 : r <= 2.5 ? 2.5 : r <= 5 ? 5 : 10) * p;
  }
  function linTicks(lo, hi, n) {
    var st = niceStep(hi - lo, n), t = [], v = Math.ceil(lo / st - 1e-9) * st;
    for (; v <= hi + st * 1e-9; v += st) t.push(Math.abs(v) < st * 1e-9 ? 0 : v);
    return t;
  }
  function logTicks(lo, hi) {
    var t = [], base = [1, 2, 5];
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
  // spec: {x:{type:'num'|'date',label,fmt,min,max,ticks,tickLabels}, y:{type:'lin'|'log',label,fmt,min,max,ticks},
  //        series:[{name,color,dash,area,x:[],y:[]}], ann:[{type:'vline'|'hline'|'point'|'band',...}], height}
  Book.lineChart = function (host, spec) {
    host.innerHTML = "";
    host.classList.add("chart");
    var series = spec.series || [];
    if (series.length > 1 || spec.legend) {
      var lg = document.createElement("div"); lg.className = "legend";
      series.forEach(function (s) {
        var k = document.createElement("span"); k.className = "key";
        var sw = document.createElement("i"); sw.className = "sw" + (s.dash ? " dash" : "");
        sw.style.background = color(s.color); sw.style.color = color(s.color);
        k.appendChild(sw); k.appendChild(document.createTextNode(s.name)); lg.appendChild(k);
      });
      host.appendChild(lg);
    }
    var wrap = document.createElement("div"); wrap.style.position = "relative"; host.appendChild(wrap);
    var tip = document.createElement("div"); tip.className = "tip"; tip.hidden = true; wrap.appendChild(tip);
    var W = Math.max(280, Math.round(host.clientWidth || 640)), H = spec.height || Math.round(Math.min(360, Math.max(220, W * 0.52)));
    var narrow = W < 460;
    var m = { l: narrow ? 46 : 58, r: spec.endLabels && !narrow ? (spec.endMargin || 96) : 16, t: 12, b: spec.x.label ? 44 : 30 };
    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, role: "img", "aria-label": spec.alt || "" }, wrap);
    var xs = [], ys = [];
    series.forEach(function (s) { s.x.forEach(function (v, i) { var yv = s.y[i]; if (yv != null && isFinite(yv)) { xs.push(v); ys.push(yv); } }); });
    var x0 = spec.x.min != null ? spec.x.min : Math.min.apply(null, xs), x1 = spec.x.max != null ? spec.x.max : Math.max.apply(null, xs);
    var isLog = spec.y.type === "log";
    var y0 = spec.y.min != null ? spec.y.min : Math.min.apply(null, ys), y1 = spec.y.max != null ? spec.y.max : Math.max.apply(null, ys);
    if (!isLog && spec.y.min == null) { var pad = (y1 - y0) * 0.06 || 1; y0 -= pad; if (spec.y.max == null) y1 += pad; }
    if (isLog) { y0 = y0 * 0.9; y1 = y1 * 1.1; }
    var X = function (v) { return m.l + (v - x0) / (x1 - x0 || 1) * (W - m.l - m.r); };
    var Y = isLog
      ? function (v) { return H - m.b - (Math.log(v) - Math.log(y0)) / (Math.log(y1) - Math.log(y0)) * (H - m.t - m.b); }
      : function (v) { return H - m.b - (v - y0) / (y1 - y0 || 1) * (H - m.t - m.b); };
    // bands
    (spec.ann || []).forEach(function (a) {
      if (a.type === "band") el("rect", { class: "band", x: X(a.x0), y: m.t, width: Math.max(0, X(a.x1) - X(a.x0)), height: H - m.t - m.b }, svg);
    });
    // grid + y ticks
    var g = el("g", { class: "grid" }, svg), ax = el("g", { class: "axis" }, svg);
    var yt = spec.y.ticks || (isLog ? logTicks(y0, y1) : linTicks(y0, y1, narrow ? 4 : 6));
    yt.forEach(function (v) {
      if (v < y0 || v > y1) return;
      el("line", { x1: m.l, x2: W - m.r, y1: Y(v), y2: Y(v) }, g);
      var t = el("text", { x: m.l - 8, y: Y(v) + 3.5, "text-anchor": "end" }, svg); t.textContent = fmt(v, spec.y.tfmt || spec.y.fmt);
    });
    if (!isLog && y0 < 0 && y1 > 0) el("line", { class: "zero", x1: m.l, x2: W - m.r, y1: Y(0), y2: Y(0) }, svg);
    var dt = spec.x.type === "date" ? dateTicks(x0, x1, narrow) : null;
    var xt = dt ? dt.t : (spec.x.ticks || linTicks(x0, x1, narrow ? 4 : 7));
    var xl = !dt && spec.x.ticks && spec.x.tickLabels;   // optional text for each of x.ticks
    el("line", { x1: m.l, x2: W - m.r, y1: H - m.b, y2: H - m.b }, ax);
    xt.forEach(function (v, i) {
      el("line", { x1: X(v), x2: X(v), y1: H - m.b, y2: H - m.b + 4 }, ax);
      var t = el("text", { x: X(v), y: H - m.b + 16, "text-anchor": "middle" }, svg);
      if (dt && dt.mode === "month") t.textContent = fmtDate(v, i === 0 || new Date(v).getUTCMonth() === 0 ? "monthyear" : "month");
      else if (dt) t.textContent = fmtDate(v, dt.mode === "year" ? "year" : null);
      else t.textContent = xl && xl[i] != null ? xl[i] : fmt(v, spec.x.fmt);
    });
    if (spec.x.label) { var tx = el("text", { class: "ttl-y", x: m.l + (W - m.l - m.r) / 2, y: H - 6, "text-anchor": "middle" }, svg); tx.textContent = spec.x.label; }
    if (spec.y.label) { var ty = el("text", { class: "ttl-y", x: m.l, y: m.t - 2 + 0, "text-anchor": "start" }, svg); ty.textContent = ""; host.setAttribute("data-ylabel", spec.y.label); }
    // series
    var sg = el("g", { class: "series" }, svg);
    series.forEach(function (s) {
      var d = "", pen = false;
      for (var i = 0; i < s.x.length; i++) {
        var yv = s.y[i];
        if (yv == null || !isFinite(yv) || (isLog && yv <= 0) || s.x[i] < x0 || s.x[i] > x1) { pen = false; continue; }
        d += (pen ? "L" : "M") + X(s.x[i]).toFixed(1) + "," + Y(Math.min(Math.max(yv, isLog ? y0 : y0 - (y1 - y0)), y1 + (y1 - y0))).toFixed(1);
        pen = true;
      }
      if (s.area && !isLog) {
        var base = Y(Math.max(y0, Math.min(0, y1)));
        el("path", { class: "area", d: d + "L" + X(s.x[s.x.length - 1]).toFixed(1) + "," + base + "L" + X(s.x[0]).toFixed(1) + "," + base + "Z", style: "fill:" + color(s.color) }, sg);
      }
      el("path", { class: "line", d: d, style: "stroke:" + color(s.color) + (s.dash ? ";stroke-dasharray:5 4" : "") + (s.width ? ";stroke-width:" + s.width : "") }, sg);
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
        el("line", { x1: X(a.x), x2: X(a.x), y1: m.t, y2: H - m.b }, ag);
        if (a.label) { var t = el("text", { x: X(a.x) + (a.anchor === "end" ? -5 : 5), y: m.t + 11 + (a.dy || 0), "text-anchor": a.anchor || "start" }, ag); t.textContent = a.label; }
      } else if (a.type === "hline") {
        el("line", { x1: m.l, x2: W - m.r, y1: Y(a.y), y2: Y(a.y) }, ag);
        if (a.label) { var t2 = el("text", { x: W - m.r - 4, y: Y(a.y) - 5, "text-anchor": "end" }, ag); t2.textContent = a.label; }
      } else if (a.type === "point") {
        el("circle", { class: "dot", cx: X(a.x), cy: Y(a.y), r: 4.5, style: "fill:" + color(a.color || "1") }, ag);
        if (a.label) { var t3 = el("text", { x: X(a.x) + (a.dx || 8), y: Y(a.y) + (a.dy || -8), "text-anchor": a.anchor || "start" }, ag); t3.textContent = a.label; }
      }
    });
    // end labels (skip if they would collide)
    if (spec.endLabels && !narrow) {
      var ends = series.map(function (s) {
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
        t.textContent = gp.items.map(function (e) { return e.s.endLabel || e.s.name; }).join(" · ") +
          (spec.endValue ? " " + fmt(gp.items[0].v, spec.y.fmt) : "");
      });
    }
    // crosshair + tooltip
    var cross = el("line", { class: "cross", y1: m.t, y2: H - m.b, x1: -10, x2: -10, visibility: "hidden" }, svg);
    var dots = series.map(function (s) { return el("circle", { class: "dot", r: 4, style: "fill:" + color(s.color), visibility: "hidden" }, svg); });
    var hit = el("rect", { x: m.l, y: m.t, width: W - m.l - m.r, height: H - m.t - m.b, fill: "transparent", style: "cursor:crosshair" }, svg);
    function nearest(arr, v) { var lo = 0, hi = arr.length - 1; while (hi - lo > 1) { var mid = (lo + hi) >> 1; if (arr[mid] < v) lo = mid; else hi = mid; } return Math.abs(arr[lo] - v) <= Math.abs(arr[hi] - v) ? lo : hi; }
    function move(ev) {
      var r = svg.getBoundingClientRect(), sx = (ev.clientX - r.left) * W / r.width;
      var xv = x0 + (sx - m.l) / (W - m.l - m.r) * (x1 - x0);
      var rows = [], px = null;
      series.forEach(function (s, k) {
        var i = nearest(s.x, xv), yv = s.y[i];
        if (yv == null || !isFinite(yv)) { dots[k].setAttribute("visibility", "hidden"); return; }
        px = X(s.x[i]);
        dots[k].setAttribute("cx", px); dots[k].setAttribute("cy", Y(yv)); dots[k].setAttribute("visibility", "visible");
        rows.push({ s: s, v: yv, xv: s.x[i] });
      });
      if (px == null) return;
      cross.setAttribute("x1", px); cross.setAttribute("x2", px); cross.setAttribute("visibility", "visible");
      var head = spec.x.type === "date" ? fmtDate(rows[0].xv) : (spec.x.tipLabel || "") + fmt(rows[0].xv, spec.x.fmt);
      tip.innerHTML = '<div class="hd">' + head + "</div>" + rows.map(function (rw) {
        return '<div class="tk"><i style="background:' + color(rw.s.color) + '"></i><span>' + rw.s.name + "</span><b>" + fmt(rw.v, rw.s.fmt || spec.y.fmt) + "</b></div>";
      }).join("");
      tip.hidden = false;
      var wr = wrap.getBoundingClientRect(), left = px * r.width / W + (r.left - wr.left) + 12;
      if (left + tip.offsetWidth > wr.width) left = px * r.width / W + (r.left - wr.left) - tip.offsetWidth - 12;
      tip.style.left = Math.max(0, left) + "px"; tip.style.top = "8px";
    }
    function leave() { tip.hidden = true; cross.setAttribute("visibility", "hidden"); dots.forEach(function (d) { d.setAttribute("visibility", "hidden"); }); }
    hit.addEventListener("pointermove", move); hit.addEventListener("pointerdown", move); hit.addEventListener("pointerleave", leave);
    if (spec.y.label) {
      var cap = document.createElement("div"); cap.className = "kbd-note"; cap.style.margin = "0 0 0.2rem"; cap.textContent = spec.y.label;
      host.insertBefore(cap, wrap);
    }
    return { X: X, Y: Y, svg: svg };
  };

  /* render every data chart on the page; re-render on width change */
  function renderCharts() {
    document.querySelectorAll("[data-chart]").forEach(function (h) {
      var src = document.getElementById("chart-" + h.getAttribute("data-chart"));
      if (!src) return;
      var spec = JSON.parse(src.textContent);
      if (spec.x.type === "date") {   // dates may be ISO strings or epoch milliseconds, in series and annotations alike
        var toT = function (d) { return typeof d === "number" ? d : Date.parse(d + "T00:00:00Z"); };
        spec.series.forEach(function (s) { s.x = s.x.map(toT); });
        (spec.ann || []).forEach(function (a) { ["x", "x0", "x1"].forEach(function (k) { if (a[k] != null) a[k] = toT(a[k]); }); });
      }
      Book.lineChart(h, spec);
    });
  }
  Book.renderCharts = renderCharts;

  function initWidgets() {
    document.querySelectorAll("[data-widget]").forEach(function (h) {
      var f = Book.widgets[h.getAttribute("data-widget")];
      if (f && !h.__init) { h.__init = true; try { f(h); } catch (e) { h.insertAdjacentHTML("beforeend", '<p class="w-note">This interactive figure could not start in this browser.</p>'); } }
    });
  }

  /* ---------------- page chrome ---------------- */
  function chrome() {
    var tg = document.querySelector(".rail-toggle"), rail = document.getElementById("rail");
    if (tg && rail) tg.addEventListener("click", function () { var o = rail.classList.toggle("open"); tg.setAttribute("aria-expanded", o ? "true" : "false"); });
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
    // outline scroll-spy
    var links = Array.prototype.slice.call(document.querySelectorAll(".outline a"));
    if (links.length && "IntersectionObserver" in window) {
      var map = {}; links.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });
      var io = new IntersectionObserver(function (ents) {
        ents.forEach(function (e) {
          if (e.isIntersecting) { links.forEach(function (a) { a.classList.remove("active"); }); var a = map[e.target.id]; if (a) a.classList.add("active"); }
        });
      }, { rootMargin: "-15% 0px -70% 0px" });
      Object.keys(map).forEach(function (id) { var t = document.getElementById(id); if (t) io.observe(t); });
    }
  }
  function selectPre(pre) { var r = document.createRange(); r.selectNodeContents(pre); var s = window.getSelection(); s.removeAllRanges(); s.addRange(r); }

  function boot() {
    chrome(); renderCharts(); initWidgets();
    var lastW = window.innerWidth, t;
    window.addEventListener("resize", function () {
      clearTimeout(t);
      t = setTimeout(function () { if (Math.abs(window.innerWidth - lastW) > 40) { lastW = window.innerWidth; renderCharts(); document.querySelectorAll("[data-widget]").forEach(function (h) { if (h.__redraw) h.__redraw(); }); } }, 180);
    });
  }
  Book.boot = boot;
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else setTimeout(boot, 0);
})();
