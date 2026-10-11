#!/usr/bin/env python3
"""Build the From Calculus to Kelly site from Markdown sources.

Markdown dialect (Obsidian-compatible):
  * $inline$ and $$display$$ math (KaTeX, rendered at build time)
  * callouts:  > [!type] Title        (types: definition theorem proposition result example solution
                                        pitfall note case zh deepdive kc answer exhibit python)
               > [!type]- Title       (collapsed <details>)
  * headings:  ## Title {lo=2,3}      numbered section mapped to learning outcomes
               ## Title {-}           unnumbered section (Summary, Practice Problems, ...)
  * [[LM14]] or [[LM14|text]]         cross-references
  * <div data-chart="id"></div>       chart, spec from src/data/<id>.json
  * <div class="widget" data-widget="name"></div>   interactive figure (page JS)
"""
import argparse
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml
from markdown_it import MarkdownIt
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

ROOT = Path(__file__).resolve().parents[1]
SRC, BUILD = ROOT / "src", ROOT / "build"
# Targets: "web" writes a self-contained static site to docs/ (GitHub Pages or any host);
# "artifact" writes the same site to dist/artifact/ with a content-only index for claude.ai artifacts.
TARGET = "web"
OUT = ROOT / "docs"
DOMAIN = "quantmath.fintools.tw"   # GitHub Pages custom domain, written to docs/CNAME (owner, 2026-10-11)
SYL = yaml.safe_load((SRC / "syllabus.yaml").read_text(encoding="utf-8"))
ALL_LMS = [dict(lm, vol=v["id"], vol_title=v["title"]) for v in SYL["volumes"] for lm in v["lms"]]
# A module goes on the site only after review: `status: published` on its entry in syllabus.yaml. Other modules
# with a source file are drafts. Drafts never reach docs/: they build in preview mode, a complete local copy of the
# site in dist/preview/ (git-ignored) where drafts are linked like published modules and carry a draft chip.
WRITTEN = {int(p.stem[2:]) for p in SRC.glob("lm[0-9][0-9].md")}
PUBLISHED = {lm["n"] for lm in ALL_LMS if lm.get("status") == "published" and lm["n"] in WRITTEN}
DRAFTS = WRITTEN - PUBLISHED
AVAILABLE = set(PUBLISHED)          # modules that pages in this build link to (preview adds the drafts)
PREVIEW = False
FONTS_LINK = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
              '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
              '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&display=swap">')
# Theme: set data-theme before the first paint (the reader's saved choice, else the system's), so a light-theme reader
# never sees a dark flash, and run the switch until book.js (at the end of a page of up to 1.5 MB) takes over.
# Night sky = dark theme, day sky = light theme.
THEME_HEAD = ('<script>(function(){var d=document.documentElement,t,m;try{t=localStorage.getItem("ftck-theme")}catch(e){}'
              'if(t!=="light"&&t!=="dark"){m=window.matchMedia&&matchMedia("(prefers-color-scheme: dark)");'
              't=m&&m.matches?"dark":"light"}d.setAttribute("data-theme",t);'
              'document.addEventListener("click",function(e){var b=e.target.closest&&e.target.closest(".theme-toggle");'
              'if(!b||window.__ftckTheme)return;var n=d.getAttribute("data-theme")==="light"?"dark":"light";'
              'try{localStorage.setItem("ftck-theme",n)}catch(x){}window.__ftckEarly=n;d.setAttribute("data-theme",n);'
              'b.setAttribute("aria-checked",n==="light"?"true":"false")})})();</script>')
THEME_TOGGLE = ('<button class="theme-toggle" type="button" role="switch" aria-checked="false" aria-label="Light theme">'
                '<span class="tt-track" aria-hidden="true"><span class="tt-sky tt-night"><i class="tt-star"></i>'
                '<i class="tt-star"></i><i class="tt-star"></i><i class="tt-star"></i></span><span class="tt-sky tt-day">'
                '<i class="tt-cloud tt-cloud-1"></i><i class="tt-cloud tt-cloud-2"></i></span><span class="tt-knob">'
                '<i class="tt-moon"></i><i class="tt-sun"></i></span></span></button>'
                '<script>document.currentScript.previousElementSibling.setAttribute("aria-checked",'
                'document.documentElement.getAttribute("data-theme")==="light"?"true":"false")</script>')

def set_target(t):
    global TARGET, OUT
    TARGET = t
    OUT = ROOT / "docs" if t == "web" else ROOT / "dist" / "artifact"

def set_preview():
    """Preview mode: web pages for published and draft modules alike, written to dist/preview/."""
    global PREVIEW, OUT
    set_target("web"); PREVIEW = True; OUT = ROOT / "dist" / "preview"
    AVAILABLE.update(DRAFTS)

def pdf_name(n):
    """File name of a module's PDF, e.g. LM03_Taylor_Series_and_Approximation.pdf."""
    title = next(x for x in ALL_LMS if x["n"] == n)["title"]
    return f"LM{n:02d}_" + re.sub(r"[^A-Za-z0-9]+", "_", title).strip("_") + ".pdf"

# ---------------------------------------------------------------- static assets
NM = BUILD / "node_modules"
VENDOR_FONTS = [
    NM / "@fontsource-variable/source-serif-4/files/source-serif-4-latin-opsz-normal.woff2",
    NM / "@fontsource-variable/source-serif-4/files/source-serif-4-latin-opsz-italic.woff2",
    NM / "@fontsource-variable/source-serif-4/files/source-serif-4-latin-ext-opsz-normal.woff2",
    NM / "@fontsource-variable/source-serif-4/files/source-serif-4-greek-opsz-normal.woff2",
    NM / "@fontsource-variable/archivo/files/archivo-latin-standard-normal.woff2",
    NM / "@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-400-normal.woff2",
    NM / "@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-600-normal.woff2",
]

def copy_assets():
    """Copy hand-written assets from src/assets and vendor fonts/KaTeX from build/node_modules."""
    a = OUT / "assets"
    (a / "fonts").mkdir(parents=True, exist_ok=True); (a / "katex" / "fonts").mkdir(parents=True, exist_ok=True)
    for f in (SRC / "assets").iterdir():
        if f.is_file(): shutil.copy(f, a / f.name)
    for f in VENDOR_FONTS:
        if not f.exists(): raise SystemExit(f"missing {f} — run `npm ci` in build/")
        shutil.copy(f, a / "fonts" / f.name)
    kd = NM / "katex" / "dist"
    css = (kd / "katex.min.css").read_text(encoding="utf-8")
    css = re.sub(r'src:url\((fonts/[^)]+\.woff2)\) format\("woff2"\)[^;}]*', r'src:url(\1) format("woff2")', css)  # woff2 only
    (a / "katex" / "katex.min.css").write_text(css, encoding="utf-8")
    for f in (kd / "fonts").glob("*.woff2"):
        shutil.copy(f, a / "katex" / "fonts" / f.name)
    if TARGET == "web" and not PREVIEW:
        (OUT / ".nojekyll").write_text("")
        (OUT / "CNAME").write_text(DOMAIN + "\n", encoding="utf-8", newline="\n")

# ---------------------------------------------------------------- math
class MathStore:
    def __init__(self): self.items = []
    def add(self, tex, display):
        self.items.append({"tex": tex.strip(), "display": display})
        return f"MATHPH{len(self.items)-1}{'D' if display else 'I'}X"
    def render(self):
        if not self.items: return []
        out = subprocess.run(["node", str(BUILD / "katex_render.js")], input=json.dumps(self.items),
                             capture_output=True, text=True, encoding="utf-8", check=True).stdout
        res = json.loads(out)
        errs = [(self.items[i]["tex"], r["error"]) for i, r in enumerate(res) if isinstance(r, dict)]
        if errs:
            for t, e in errs: print("KaTeX ERROR:", e, "\n   in:", t[:160], file=sys.stderr)
            raise SystemExit(1)
        return res

# punctuation that glue_end keeps on an inline formula's line (tested in Chrome); it does not hold % – - ； ：, which
# are left out. GLUE_NEXT finds the character after the formula, past closing inline tags.
GLUE = set(".,;:!?)]’”\"'，。、」』）】》！？")
GLUE_NEXT = re.compile(r"(?:</(?:em|strong|a)>)*(&quot;|&#39;|.)", re.DOTALL)
def glue_end(h):
    """Wrap the last box of an inline KaTeX formula in .mi-end (white-space: nowrap). Chrome may break a line after
    an inline-block (KaTeX's .base boxes) even before a full stop, word joiner or not; it does not when the box's
    parent is nowrap. The punctuation stays outside the formula, in the body font."""
    i, tail = h.rfind('<span class="base">'), "</span></span>"   # tail closes .katex-html and .katex
    if i < 0 or not h.endswith(tail): return h
    return h[:i] + '<span class="mi-end">' + h[i:-len(tail)] + "</span>" + tail

def protect_code(md):
    """Replace fenced code and inline code with tokens so math extraction skips them."""
    vault = []
    def keep(m): vault.append(m.group(0)); return f"CODEPH{len(vault)-1}X"
    md = re.sub(r"(?ms)^(```|~~~).*?^\1[ \t]*$", keep, md)
    md = re.sub(r"`[^`\n]+`", keep, md)
    return md, vault

def restore_code(md, vault):
    return re.sub(r"CODEPH(\d+)X", lambda m: vault[int(m.group(1))], md)

def extract_math(md, ms):
    md = re.sub(r"(?s)\$\$(.+?)\$\$", lambda m: ms.add(m.group(1), True), md)
    # inline: content may hold escaped characters such as \$ (e.g. \text{NT\$}); an escaped \$ never opens or closes
    md = re.sub(r"(?<![\\$])\$(?!\$)((?:[^\n$\\]|\\.)+?)\$", lambda m: ms.add(m.group(1), False), md)
    return md.replace(r"\$", "&#36;")

# ---------------------------------------------------------------- markdown
def fence_html(code, lang):
    lang = (lang or "text").strip().split()[0]
    try:
        body = highlight(code, get_lexer_by_name(lang), HtmlFormatter(nowrap=True))
    except ClassNotFound:                                  # unknown fence language: plain text
        body = html.escape(code)
    label = {"python": "Python", "bash": "Shell", "sh": "Shell", "text": "Text"}.get(lang, lang)
    return (f'<div class="code"><div class="code-h"><span>{label}</span><button class="copy" type="button">Copy</button></div>'
            f'<pre class="hl"><code>{body}</code></pre></div>')

MD = MarkdownIt("commonmark", {"html": True, "typographer": True}).enable(["table", "strikethrough"])
def _fence(self, tokens, idx, options, env):
    t = tokens[idx]
    return fence_html(t.content, t.info)
MD.add_render_rule("fence", _fence)

def md_to_html(md):
    return MD.render(md)

# ---------------------------------------------------------------- callouts
CO_LABEL = {"definition": "Definition", "theorem": "Theorem", "proposition": "Proposition", "result": "Result",
            "example": "Example", "solution": "Solution", "pitfall": "Pitfall", "note": "Note", "case": "Motivating Case",
            "zh": "導讀", "deepdive": "Deep Dive", "kc": "Knowledge Check", "answer": "Answer", "exhibit": "Exhibit",
            "python": "In Python"}
CO_HEAD = re.compile(r"^\[!(\w+)\]([+-]?)\s*(.*)$")

class Ctx:
    def __init__(self): self.n = {"example": 0, "exhibit": 0, "kc": 0}

def render_blocks(md, ctx):
    """Render markdown that may contain callouts (blockquotes whose first line is [!type])."""
    lines, out, buf, i = md.split("\n"), [], [], 0
    def flush():
        if buf:
            out.append(md_to_html("\n".join(buf))); buf.clear()
    while i < len(lines):
        ln = lines[i]
        m = re.match(r"^>\s?(.*)$", ln)
        if m and CO_HEAD.match(m.group(1).strip()):
            flush()
            block = []
            while i < len(lines) and re.match(r"^>", lines[i]):
                block.append(re.sub(r"^>\s?", "", lines[i], count=1)); i += 1
            out.append(render_callout(block, ctx))
            continue
        buf.append(ln); i += 1
    flush()
    return "\n".join(out)

def render_callout(block, ctx):
    m = CO_HEAD.match(block[0].strip())
    if not m: raise SystemExit(f"bad callout header: {block[0]!r}")
    typ, fold, title = m.groups()
    typ = typ.lower(); inner = "\n".join(block[1:]).strip("\n")
    label = CO_LABEL.get(typ, typ.title())
    if typ in ctx.n:
        ctx.n[typ] += 1; label = f"{label} {ctx.n[typ]}"
    if typ == "exhibit":
        note = ""
        nm = re.search(r"(?ms)^(Note|Source|Sources)s?:\s*(.+)\Z", inner)
        if nm:
            note = f'<div class="ex-note">{md_inline(nm.group(0))}</div>'; inner = inner[:nm.start()].rstrip()
        return (f'<figure class="exhibit" id="ex{ctx.n["exhibit"]}"><figcaption class="ex-bar">{label}: {md_inline(title)}</figcaption>'
                f'<div class="ex-body">{render_blocks(inner, ctx)}</div>{note}</figure>')
    body = render_blocks(inner, ctx)
    t_html = f'<span class="t">{md_inline(title)}</span>' if title else ""
    if fold or typ in ("deepdive", "answer"):
        is_open = " open" if fold == "+" else ""
        hint = '<span class="hint">optional · click to expand</span>' if typ == "deepdive" else ""
        return f'<details class="co {typ}"{is_open}><summary><span class="tag">{label}</span>{t_html}{hint}</summary>{body}</details>'
    if typ == "example":
        anchor = f' id="example{ctx.n["example"]}"'
        return f'<div class="co example"{anchor}><div class="co-h"><span class="tag">{label}</span>{t_html}</div><div class="co-b">{body}</div></div>'
    anchor = f' id="kc{ctx.n["kc"]}"' if typ == "kc" else ""
    return f'<div class="co {typ}"{anchor}><div class="co-h"><span class="tag">{label}</span>{t_html}</div>{body}</div>'

def md_inline(s):
    return MD.renderInline(s)


def label_refs(md):
    """Number exhibits/examples in document order; resolve [[ex:label]] and [[eg:label]]."""
    nums = {"exhibit": 0, "example": 0}; labels = {}
    for m in re.finditer(r"(?m)^(?:>\s?)+\[!(exhibit|example)\][+-]?\s*(.*)$", md):
        typ, title = m.group(1), m.group(2)
        nums[typ] += 1
        lm = re.search(r"\{#([\w-]+)\}\s*$", title)
        if lm: labels[lm.group(1)] = (typ, nums[typ])
    def rep(m):
        kind, lab = m.group(1), m.group(2)
        if lab not in labels: raise SystemExit(f"unknown label {kind}:{lab}")
        typ, n = labels[lab]
        return f'<a href="#ex{n}">Exhibit {n}</a>' if typ == "exhibit" else f'<a href="#example{n}">Example {n}</a>'
    md = re.sub(r"\[\[(ex|eg):([\w-]+)\]\]", rep, md)
    return re.sub(r"(?m)^((?:>\s?)+\[!(?:exhibit|example)\][+-]?\s*.*?)\s*\{#[\w-]+\}\s*$", r"\1", md)

# ---------------------------------------------------------------- cross refs, charts
def xref(md, depth):
    def rep(m):
        n, text = int(m.group(1)), m.group(2) or f"LM{int(m.group(1))}"
        if n in AVAILABLE:
            href = (f"lm{n:02d}.html" if depth == "lm" else f"lm/lm{n:02d}.html")
            return f'<a href="{href}">{text}</a>'
        lm = next((x for x in ALL_LMS if x["n"] == n), None)
        tip = html.escape(f'LM{n} {lm["title"]} — coming in Volume {lm["vol"]}') if lm else "coming"
        return f'<span class="coming" title="{tip}">{text}</span>'
    return re.sub(r"\[\[LM(\d+)(?:\|([^\]]+))?\]\]", rep, md)

def inline_charts(html_s):
    used = re.findall(r'data-chart="([\w-]+)"', html_s)
    blobs = []
    for cid in dict.fromkeys(used):
        spec = json.loads((SRC / "data" / f"{cid}.json").read_text(encoding="utf-8"))
        blobs.append(f'<script type="application/json" id="chart-{cid}">{json.dumps(spec, separators=(",", ":"))}</script>')
    return html_s + "\n".join(blobs)

# ---------------------------------------------------------------- page parts
def rail(current, depth):
    pre = "" if depth == "lm" else "lm/"
    home = "../index.html" if depth == "lm" else "index.html"
    parts = [f'<a class="home" href="{home}">Contents &amp; roadmap</a>']
    for v in SYL["volumes"]:
        parts.append(f'<h2>Vol {v["id"]} · {html.escape(v["title"])}</h2><ol>')
        for lm in v["lms"]:
            n = lm["n"]; t = html.escape(lm["title"])
            if n in AVAILABLE or n == current:
                cur = ' aria-current="page"' if n == current else ""
                parts.append(f'<li><a href="{pre}lm{n:02d}.html"{cur}><span class="k">LM{n}</span><span>{t}</span></a></li>')
            else:
                parts.append(f'<li><span title="Planned"><span class="k">LM{n}</span><span>{t}</span></span></li>')
        parts.append("</ol>")
    return "\n".join(parts)

def chips_for(ns, label):
    if not ns: return ""
    items = []
    for n in ns:
        if n in AVAILABLE: items.append(f'<a href="lm{n:02d}.html">LM{n}</a>')
        else:
            lm = next(x for x in ALL_LMS if x["n"] == n)
            items.append(f'<span class="soon" title="{html.escape(lm["title"])} (planned)">LM{n}</span>')
    return f'<span class="chip"><b>{label}</b> {" · ".join(items)}</span>'

def pager(n):
    avail = sorted(AVAILABLE)
    prev_n = max([a for a in avail if a < n], default=None); next_n = min([a for a in avail if a > n], default=None)
    def cell(k, d, cls):
        if k is None:
            return f'<span class="{cls}"><span class="dir">{d}</span>Contents</span>' if False else f'<a class="{cls}" href="../index.html"><span class="dir">{d}</span><b>Contents &amp; roadmap</b></a>'
        lm = next(x for x in ALL_LMS if x["n"] == k)
        return f'<a class="{cls}" href="lm{k:02d}.html"><span class="dir">{d}</span><b>LM{k} {html.escape(lm["title"])}</b></a>'
    return f'<nav class="pager" aria-label="Module navigation">{cell(prev_n, "Previous", "pv")}{cell(next_n, "Next", "nx")}</nav>'

# ---------------------------------------------------------------- module page
def build_lm(path):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"(?s)^---\n(.*?)\n---\n(.*)$", raw)
    if not m: raise SystemExit(f"{path.name}: no front matter")
    fm_txt, body = m.groups()
    fm = yaml.safe_load(fm_txt)
    n = int(fm["lm"]); meta = next(x for x in ALL_LMS if x["n"] == n)
    ms, ctx = MathStore(), Ctx()
    body, vault = protect_code(body)
    body = extract_math(body, ms)
    body = restore_code(body, vault)
    body = xref(body, "lm")
    body = label_refs(body)
    # outcomes & overview text may contain math too
    los = [extract_math(xref(lo, "lm"), ms) for lo in fm.get("outcomes", [])]
    ovs = [extract_math(xref(o, "lm"), ms) for o in fm.get("overview", [])]
    # split into sections by level-2 headings
    chunks = re.split(r"(?m)^## (.+)$", body)
    intro_md, sections, outline = chunks[0], [], []
    secno = 0
    for k in range(1, len(chunks), 2):
        head, md = chunks[k].strip(), chunks[k + 1]
        attrs = re.search(r"\{([^}]*)\}\s*$", head)
        a = attrs.group(1) if attrs else ""
        title = head[:attrs.start()].strip() if attrs else head
        numbered = a.strip() != "-"
        lo = re.search(r"lo=([\d,]+)", a)
        if "lo=" in a and not lo: raise SystemExit(f"bad lo= in heading: {head!r}")
        lo_ids = [int(x) for x in re.findall(r"\d+", lo.group(1))] if lo else []
        if numbered: secno += 1
        sid = f"s{secno}" if numbered else re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        sub = []
        def h3rep(m, _sid=sid, _sub=sub):
            t = m.group(1).strip(); hid = f"{_sid}-{len(_sub)+1}"; _sub.append((hid, t))
            return f'<h3 id="{hid}">{md_inline(t)}</h3>'
        md = re.sub(r"(?m)^### (.+)$", h3rep, md)
        sec_html = render_blocks(md, ctx)
        lo_html = "".join(f'<div class="sec-lo"><span class="box" aria-hidden="true"></span><span>{md_inline(los[i-1])}</span></div>' for i in lo_ids)
        no = f'<span class="secno">{secno}</span>' if numbered else ""
        cls = "sec" + ("" if numbered else " unnum")
        h2 = f'<h2>{no}<span class="ttl">{md_inline(title)}</span></h2>' if numbered else f'<h2 class="plain"><span class="ttl">{md_inline(title)}</span></h2>'
        if sid == "practice-problems":
            sec_html = sec_html.replace("<ol>", '<ol class="pp">', 1).replace("<ul>", '<ul class="opts">')
            sec_html = re.sub(r"<li>\s*<strong>([A-D])\.</strong>\s*(.*?)</li>", r"<li><b>\1.</b><span>\2</span></li>", sec_html, flags=re.DOTALL)
        elif sid == "solutions":
            sec_html = sec_html.replace("<ol>", '<ol class="sol-list">', 1)
        elif sid == "glossary":
            sec_html = sec_html.replace("<table>", '<table class="gloss">', 1)
        elif sid == "references":
            sec_html = sec_html.replace("<ul>", '<ul class="refs">', 1)
        if "<table" in sec_html:
            sec_html = re.sub(r"(<table(?: class=\"[^\"]*\")?>.*?</table>)", r'<div class="table-wrap">\1</div>', sec_html, flags=re.DOTALL)
        sections.append(f'<section class="{cls}" id="{sid}">{h2}{lo_html}{sec_html}</section>')
        outline.append((sid, (f"{secno}. " if numbered else "") + title, sub))
    # learning outcomes + overview
    lo_rows = "".join(f'<tr><td><input type="checkbox" id="lo{i}" aria-label="Mastered outcome {i}"></td><td><span class="lo-k">{i}</span>{md_inline(t)}</td></tr>'
                      for i, t in enumerate(los, 1))
    lo_box = (f'<section class="lo" aria-label="Learning outcomes"><div class="lo-bar">Learning Outcomes</div>'
              f'<table><thead><tr><th>Mastery</th><th>After this module you should be able to:</th></tr></thead><tbody>{lo_rows}</tbody></table></section>')
    ov_box = ('<aside class="overview"><div class="label">Learning Module Overview</div><ul>' +
              "".join(f"<li>{md_inline(o)}</li>" for o in ovs) + "</ul></aside>") if ovs else ""
    head = (f'<header class="lm-head"><div class="lm-band"><div class="lm-kicker">Learning Module</div>'
            f'<div class="lm-num">{n}</div></div>'
            f'<h1 class="lm-title">{html.escape(fm["title"])}</h1>'
            + (f'<p class="lm-sub">{md_inline(fm["subtitle"])}</p>' if fm.get("subtitle") else "") +
            f'<div class="lm-meta"><span class="chip"><b>Volume</b> {meta["vol"]} · {html.escape(meta["vol_title"])}</span>'
            f'{chips_for(fm.get("prereq", []), "Builds on")}{chips_for(fm.get("leads", []), "Leads to")}'
            + (f'<span class="chip"><b>Time</b> {html.escape(str(fm["time"]))}</span>' if fm.get("time") else "")
            + ('<span class="chip draft-chip"><b>Status</b> draft, under review</span>' if n not in PUBLISHED else "")
            + (f'<a class="chip pdf-chip" href="../pdf/{pdf_name(n)}"><b>PDF</b> A4 print edition</a>' if TARGET == "web" and n in PUBLISHED and not PREVIEW else "")
            + '</div></header>')
    intro_html = render_blocks(intro_md, ctx) if intro_md.strip() else ""
    main = head + lo_box + ov_box + intro_html + "".join(sections) + pager(n)
    # math substitution
    rendered = ms.render()
    def mrep(m):
        i, kind = int(m.group(1)), m.group(2)
        h = rendered[i]
        nxt = GLUE_NEXT.match(m.string, m.end()) if kind == "I" else None
        if nxt and (nxt.group(1) in ("&quot;", "&#39;") or nxt.group(1) in GLUE): h = glue_end(h)
        if kind == "I": return f'<span class="math-inline" role="math" aria-label="{html.escape(ms.items[i]["tex"])}">{h}</span>'
        return f'<div class="math-display" role="math" aria-label="{html.escape(ms.items[i]["tex"])}">{h}</div>'
    main = re.sub(r"<p>\s*MATHPH(\d+)(D)X\s*</p>", mrep, main)
    main = re.sub(r"MATHPH(\d+)([DI])X", mrep, main)
    main = inline_charts(main)
    outline_html = "<h2>On this page</h2><ol>" + "".join(
        f'<li><a href="#{sid}">{md_inline(t)}</a>' + ("<ol class=\"sub\">" + "".join(f'<li class="sub"><a href="#{h}">{md_inline(tt)}</a></li>' for h, tt in sub) + "</ol>" if sub and len(sub) <= 6 else "") + "</li>"
        for sid, t, sub in outline) + "</ol>"
    outline_html = re.sub(r"MATHPH(\d+)([DI])X", lambda m: rendered[int(m.group(1))], outline_html)
    js = "".join(f'<script src="../assets/{j}"></script>' for j in fm.get("js", []))
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{THEME_HEAD}
<title>LM{n} {html.escape(fm["title"])} · From Calculus to Kelly</title>
<meta name="description" content="{html.escape(meta["desc"])}">
<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
{FONTS_LINK}
<link rel="stylesheet" href="../assets/katex/katex.min.css">
<link rel="stylesheet" href="../assets/book.css">
</head>
<body data-lm="{n}">
<a class="skip" href="#main">Skip to content</a>
<header class="topbar"><a class="brand" href="../index.html">From Calculus to Kelly<small>量化數理教科書</small></a>
<span class="crumb">Vol {meta["vol"]} · LM{n} {html.escape(fm["title"])}</span><span class="spacer"></span>
{THEME_TOGGLE}<button class="rail-toggle" type="button" aria-controls="rail" aria-expanded="false">Contents</button></header>
<div class="layout">
<nav class="rail" id="rail" aria-label="Book contents">{rail(n, "lm")}</nav>
<main class="page" id="main">{main}</main>
<aside class="outline" aria-label="On this page">{outline_html}</aside>
</div>
<script src="../assets/book.js"></script>
{js}
</body>
</html>
"""
    out = OUT / "lm" / f"lm{n:02d}.html"
    out.parent.mkdir(parents=True, exist_ok=True); (OUT / "assets").mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    for j in fm.get("js", []):
        shutil.copy(SRC / j, OUT / "assets" / j)
    print(f"built {out.relative_to(ROOT)}  math={len(ms.items)} examples={ctx.n['example']} exhibits={ctx.n['exhibit']} kc={ctx.n['kc']} bytes={len(page):,}")
    return fm

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Build the From Calculus to Kelly site.")
    ap.add_argument("modules", nargs="*", help="e.g. lm03 index (default: every published module plus the index)")
    ap.add_argument("--target", choices=["web", "artifact"], default="web")
    ap.add_argument("--preview", action="store_true",
                    help="build published and draft modules into dist/preview/ (implied when a draft is named)")
    ap.add_argument("--list-pdfs", action="store_true", help="print 'html|pdf|title' for each published module and exit")
    args = ap.parse_args()
    set_target(args.target)
    if args.list_pdfs:
        for n in sorted(PUBLISHED):
            t = next(x for x in ALL_LMS if x["n"] == n)["title"]
            print(f"lm/lm{n:02d}.html|pdf/{pdf_name(n)}|LM{n} {t}")
        raise SystemExit(0)
    named_drafts = [t for t in args.modules if t.startswith("lm") and int(t[2:]) in DRAFTS]
    if args.preview or named_drafts:
        set_preview()
        if named_drafts and not args.preview:
            print(f"preview mode ({', '.join(named_drafts)} not yet published): writing to dist/preview/")
    copy_assets()
    for t in (args.modules or [f"lm{n:02d}" for n in sorted(AVAILABLE)] + ["index"]):
        if t == "index":
            sys.modules.setdefault("build", sys.modules[__name__])   # let build_index see this run's target
            import build_index
            build_index.build()
        else:
            build_lm(SRC / f"{t}.md")
